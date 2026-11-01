#!/usr/bin/env python3
"""drawgen's tests. Run in drawgen's own environment:

    DRAWGEN_VENV=... tools/drawgen/run.sh is the CLI; the tests run with that venv's python:
    <venv>/bin/python tools/drawgen/tests/test_drawgen.py          # prints "N of N passed"
    <venv>/bin/python -m pytest -q tools/drawgen/tests              # the same with pytest, if installed

1. The five sample drawings regenerate from their STEPs on this tree and read back: every STEP hole (the repo's own
   reader, no OCC) is in a hole table within 0.05 mm, drawn as a true circle at its place, the text carries what
   the mechanical check reads, and the PDF's Creator is drawgen.
2. Making a drawing twice from the same sources gives the same bytes (so an unchanged model never shows a diff).
3. A model change regenerates the drawing: a test tube written to STEP, drawn, then a
   hole moved 10 mm and drawn again: the table moves by 10 mm, the read-back passes on both, and `stale` reports
   the first drawing out of date.
4. drawgen never overwrites a PDF it didn't make (a Fusion drawing).
5. A part with a feature it can't dimension (here a fillet) is refused, not drawn.
"""

import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import fitz  # noqa: E402

import compose  # noqa: E402
import drawgen  # noqa: E402
import readback  # noqa: E402
import specs  # noqa: E402

TMP = tempfile.mkdtemp(prefix="drawgen-test-")


def _filleted_block(path):
    """A 40 x 300 x 20 block with one rounded edge: a feature drawgen doesn't dimension."""
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.gp import gp_Pnt
    box = BRepPrimAPI_MakeBox(gp_Pnt(-1244, 0, 100), 40, 300, 20).Shape()
    f = BRepFilletAPI_MakeFillet(box)
    f.Add(2.0, TopoDS.Edge_s(TopExp_Explorer(box, TopAbs_EDGE).Current()))
    w = STEPControl_Writer()
    w.Transfer(f.Shape(), STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def _move_hole(src, dst, dia, centre_mm, shift_mm, axis=2):
    """Copy a Fusion STEP and move one hole along one file axis: every CARTESIAN_POINT that the hole's
    faces use (their axis, their edge circles and vertices, which the wall's inner loop shares) shifts by the
    same amount, so the solid stays valid. Returns the shift in mm along the pod axis it moved."""
    sys.path.insert(0, os.path.join(readback.REPO, "tools", "checks"))
    import re
    import stepfile as sf
    st = sf.StepFile(src)
    scale = st.scale
    target = None
    for inst in st.instances():
        so = st.solid(inst["solid"])
        for h in so.holes:
            c = inst["frame"].point(h.center)
            if abs(h.diameter - dia) < 0.01 and all(abs(a - b) < 0.6 for a, b in zip(c, centre_mm)):
                target = h
    assert target is not None, "no such hole"
    seen, todo = set(), list(target.faces)
    while todo:
        eid = todo.pop()
        if eid in seen:
            continue
        seen.add(eid)
        for name, args in st.e.get(eid, []):
            stack = list(args)
            while stack:
                a = stack.pop()
                if isinstance(a, sf.Ref):
                    todo.append(int(a))
                elif isinstance(a, (list, tuple)):
                    stack.extend(a)
    pts = {eid for eid in seen if any(n == "CARTESIAN_POINT" for n, _a in st.e.get(eid, []))}
    with open(src, encoding="latin-1") as fh:
        text = fh.read()

    pat = re.compile(r"#(\d+)=CARTESIAN_POINT\('([^']*)',\(([^)]*)\)\);")

    def sub(m):
        if int(m.group(1)) not in pts:
            return m.group(0)
        v = [float(x) for x in m.group(3).split(",")]
        v[axis] += shift_mm / scale
        return "#%s=CARTESIAN_POINT('%s',(%s));" % (m.group(1), m.group(2), ",".join(repr(x) for x in v))
    text = pat.sub(sub, text)
    with open(dst, "w", encoding="latin-1") as fh:
        fh.write(text)
    return dst


ROW = {"part_number": "219999", "name": "TEST - BLOCK - DRAWGEN", "name_vi": "", "material": "aluminium 6063-T6",
       "finish": "mill", "mass_each_kg": "0.1"}
SPEC = {"datums": "corner", "corner": "-X-Y-Z", "tolerance": "test tolerance", "iso": False}


def test_sample_regenerates_and_reads_back():
    out = os.path.join(TMP, "sample")
    os.makedirs(out, exist_ok=True)
    for pn in specs.SAMPLE:
        final, rep = drawgen.generate(pn, out)
        fails, st = readback.check(final)
        assert not fails, "%s: %s" % (pn, fails)
        if specs.SPECS[pn][1] == "part":
            assert st["worst_table"] <= 0.05 and st["worst_drawn"] <= 0.05


def test_same_sources_same_bytes():
    a, b = os.path.join(TMP, "a"), os.path.join(TMP, "b")
    for d in (a, b):
        os.makedirs(d, exist_ok=True)
    fa, _ = drawgen.generate("111101", a)
    fb, _ = drawgen.generate("111101", b)
    with open(fa, "rb") as x, open(fb, "rb") as y:
        assert x.read() == y.read()


def test_model_change_regenerates():
    """Move one hole of the L1 frame's real STEP 10 mm and draw again: only that hole's row moves, by 10."""
    d = os.path.join(TMP, "model")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(readback.REPO, "v2/03-Manufacturing/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_STEP.step")
    step = os.path.join(d, os.path.basename(src))
    shutil.copy(src, step)
    p1 = os.path.join(d, "v1.pdf")
    compose.make("211101", "wall", specs.WALL_FRAME, p1, step=step)
    f1, _ = readback.check(p1, step)
    assert not f1, f1
    rows1 = readback.table_rows(fitz.open(p1)[0])
    # the back stile's middle rivnut hole (F09, Ø9.53 at Y 824, Z 671.56) moves 10 mm up the stile (Z)
    moved_step = os.path.join(d, "moved.step")
    _move_hole(src, moved_step, 9.53, (-1204.6, 824.0, 671.56), 10.0, axis=2)
    shutil.copy(moved_step, step)
    why = drawgen.stale(p1)
    assert any("changed" in w and w.endswith("STEP.step changed") for w in why), why     # the drawing knows
    p2 = os.path.join(d, "v2.pdf")
    compose.make("211101", "wall", specs.WALL_FRAME, p2, step=step)
    f2, _ = readback.check(p2, step)
    assert not f2, f2
    rows2 = readback.table_rows(fitz.open(p2)[0])
    changed = sorted(t for t in rows1 if rows1[t][:2] != rows2.get(t, (None, None))[:2])
    assert changed, "nothing moved in the table"
    # the moved hole: the back stile's F09 row whose X/Y changed; every other row the same
    assert len(changed) == 1, (changed, [(rows1[t], rows2.get(t)) for t in changed])
    t = changed[0]
    dx, dy = rows2[t][0] - rows1[t][0], rows2[t][1] - rows1[t][1]
    assert abs(abs(dx) + abs(dy) - 10.0) < 0.01, (rows1[t], rows2[t])
    # and the old drawing no longer matches the changed model
    f3, _ = readback.check(p1, step)
    assert f3, "the old drawing must fail against the moved hole"


def test_never_overwrites_a_fusion_drawing():
    d = os.path.join(TMP, "fusion")
    os.makedirs(d, exist_ok=True)
    final, rep = drawgen.generate("111101", d)
    doc = fitz.open()
    doc.new_page()
    doc.set_metadata({"creator": "Autodesk Fusion"})
    doc.save(final)
    try:
        drawgen.generate("111101", d)
        raise AssertionError("overwrote a PDF drawgen did not make")
    except compose.NotDrawable as e:
        assert "not made by drawgen" in str(e)
    assert fitz.open(final).metadata["creator"] == "Autodesk Fusion"


def test_refuses_what_it_cannot_dimension():
    d = os.path.join(TMP, "fillet")
    os.makedirs(d, exist_ok=True)
    step = _filleted_block(os.path.join(d, "219998_P01_TEST-BLOCK-FILLET_STEP.step"))
    try:
        compose.make("219998", "none", SPEC, os.path.join(d, "x.pdf"), step=step, row=dict(ROW, part_number="219998"))
        raise AssertionError("drew a part with a fillet")
    except compose.NotDrawable as e:
        assert "can't dimension" in str(e)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for t in tests:
        try:
            t()
            ok += 1
            print("PASS %s" % t.__name__)
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            print("FAIL %s: %s" % (t.__name__, e))
    print("%d of %d passed" % (ok, len(tests)))
    shutil.rmtree(TMP, ignore_errors=True)
    return 0 if ok == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
