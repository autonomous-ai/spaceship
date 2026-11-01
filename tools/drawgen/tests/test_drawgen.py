#!/usr/bin/env python3
"""drawgen's tests. Run in drawgen's own environment:

    DRAWGEN_VENV=... tools/drawgen/run.sh is the CLI; the tests run with that venv's python:
    <venv>/bin/python tools/drawgen/tests/test_drawgen.py          # prints "N of N passed"
    <venv>/bin/python -m pytest -q tools/drawgen/tests              # the same with pytest, if installed

1. The sample drawings (the band tubes; WALL's frames with their D-131 material guard lifted) regenerate from
   their STEPs on this tree and read back: every STEP hole (the repo's own
   reader, no OCC) is in a hole table within 0.05 mm, drawn as a true circle at its place, the text carries what
   the mechanical check reads, and the PDF's Creator is drawgen.
2. Making a drawing twice from the same sources gives the same bytes (so an unchanged model never shows a diff).
3. A model change regenerates the drawing: a test tube written to STEP, drawn, then a
   hole moved 10 mm and drawn again: the table moves by 10 mm, the read-back passes on both, and `stale` reports
   the first drawing out of date.
4. drawgen never overwrites a PDF it didn't make (a Fusion drawing).
5. A part with a feature it can't dimension (here a fillet) is refused, not drawn; so is a folded sheet, even
   with a sharp fold (D-113).
6. The read-back fails a sheet where two texts touch, a text touches a part outline, or a line runs through a text.
7. A long tube keeps a legible scale: 111103 (2420 mm) fits A1 at 1:5 with a narrower table column instead of
   dropping to 1:10, with datum B on B1's round-spigot rivnut (joints register 2.11).
8. Keys fitted in a part's ends: each key in Joints' corner-keys.csv gets its orientation note, and the read-back
   fails a missing note or one that names holes away from the key's screw positions.
9. Only holes on one line through two walls count as a two-wall pair (which needs a section).
10. Holes square to an angled face get a lettered view square to that face (ISO 128-30); blind holes with a drill
    point read as blind.
11. An entry written for one material (welded steel, D-131) refuses a parts list that gives another.
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


def test_frames_draw_and_read_back():
    """WALL's frames (#202's sample) draw and read back from their STEPs, with J-FRAME-01's weld notes; their entry
    refuses the parts list until WALL's D-131 steel list lands, so the material guard is lifted here: the geometry
    D-131 keeps (every hole, rivnut and joint position) is what this tests."""
    out = os.path.join(TMP, "frames")
    os.makedirs(out, exist_ok=True)
    for pn in specs.FRAMES:
        p = os.path.join(out, pn + ".pdf")
        compose.make(pn, specs.SPECS[pn][0], dict(specs.SPECS[pn][2], material_has=None), p)
        fails, st = readback.check(p)
        assert not fails, "%s: %s" % (pn, fails)
        assert st["worst_table"] <= 0.05 and st["worst_drawn"] <= 0.05
        assert "J-FRAME-01" in " ".join(page.get_text() for page in fitz.open(p))


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
    compose.make("211101", "wall", dict(specs.SPECS["211101"][2], material_has=None), p1, step=step)
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
    compose.make("211101", "wall", dict(specs.SPECS["211101"][2], material_has=None), p2, step=step)
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


def _folded_sheet(path):
    """An L-shaped 3 mm sheet with a sharp fold (no bend radius, as an ACP V-groove fold is modelled)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Pnt
    a = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 300, 3, 100).Shape()
    b = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 3, 40, 100).Shape()
    f = BRepAlgoAPI_Fuse(a, b)
    f.SetFuzzyValue(1e-6)
    f.Build()
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    u = ShapeUpgrade_UnifySameDomain(f.Shape(), True, True, True)
    u.Build()
    w = STEPControl_Writer()
    w.Transfer(u.Shape(), STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def test_refuses_a_folded_sheet():
    """D-113: a bent or folded part stays with Fusion, even when its fold has no radius in the model."""
    d = os.path.join(TMP, "folded")
    os.makedirs(d, exist_ok=True)
    step = _folded_sheet(os.path.join(d, "219997_P01_TEST-FOLDED-SHEET_STEP.step"))
    row = dict(ROW, part_number="219997", name="TEST - FOLDED SHEET", process="laser cut")
    try:
        compose.make("219997", "none", SPEC, os.path.join(d, "x.pdf"), step=step, row=row)
        raise AssertionError("drew a folded sheet")
    except compose.NotDrawable as e:
        assert "folded" in str(e), e


def test_clash_check_catches_touching_text():
    """The read-back fails a sheet where two texts touch, or a text touches a part outline (PM, 2026-11-01)."""
    from sheet import Sheet
    d = os.path.join(TMP, "clash")
    os.makedirs(d, exist_ok=True)
    sh = Sheet("A3")
    sh.text(100, 100, "H03", 2.5, bold=True)
    sh.text(104, 100.5, "O2", 2.5, bold=True)            # runs into H03
    sh.line((150, 90), (150, 110), 0.5)                  # an outline...
    sh.text(149, 100, "H07", 2.5)                        # ...with a tag on it
    sh.text(200, 100, "H09", 2.5)                        # clear of everything
    sh.save(os.path.join(d, "c.pdf"))
    found = [w for _p, w in readback.clashes(fitz.open(os.path.join(d, "c.pdf")))]
    assert any("'H03'" in w and "'O2'" in w for w in found), found
    assert any("'H07' touches an outline" in w for w in found), found
    assert not any("H09" in w for w in found), found


def test_clash_check_catches_a_line_through_text():
    """The read-back fails a line that runs through a text's letters (a dimension line through a datum letter, an
    arrow through an origin name), and passes a leader that stops at its text."""
    from sheet import Sheet
    d = os.path.join(TMP, "clash")
    os.makedirs(d, exist_ok=True)
    sh = Sheet("A3")
    sh.text(100, 100, "O2", 2.5, bold=True)
    sh.line((101.5, 95), (101.5, 106), 0.25)             # an arrow up through O2
    sh.line((180, 101), (197, 101), 0.25)                # a leader that stops short of its tag
    sh.text(197.5, 100.4, "H09", 2.5, bold=True)
    sh.save(os.path.join(d, "l.pdf"))
    found = [w for _p, w in readback.clashes(fitz.open(os.path.join(d, "l.pdf")))]
    assert any("through text 'O2'" in w for w in found), found
    assert not any("H09" in w for w in found), found


def test_long_tube_keeps_its_scale():
    """111103 is 2420 long: beside the default table column only 1:10 fits (the 40 mm tube 4 mm on paper); a
    narrower column keeps 1:5, the tables still end above the title block, and it reads back with B where the
    joints register puts it (the spigot rivnut under B1's round spigot hole, X -102.75)."""
    out = os.path.join(TMP, "long")
    os.makedirs(out, exist_ok=True)
    final, rep = drawgen.generate("111103", out)
    assert abs(rep["scale"] - 0.2) < 1e-9, rep["scale"]
    fails, st = readback.check(final)
    assert not fails, fails
    with fitz.open(final) as d:
        data = readback.read_data(d)
    b = [f for f in data["features"] if f["tag"] == data["datums"]["B"]]
    assert len(b) == 1 and abs(b[0]["entry"][0] - (-102.75)) < 0.01, b


def test_key_notes_name_the_screw_holes():
    """The band tubes carry a note for each key Joints' file puts in their ends (both read back clean: the sample
    test and the long tube test), and the read-back's key check fails a missing note or a wrong hole."""
    import inputs
    rows = inputs.key_rows("111103") + inputs.key_rows("111101")
    assert rows, "no keys in the band tubes' ends in corner-keys.csv"
    row = dict(rows[0])
    row.update({"fix_hole_1_x": "0", "fix_hole_1_y": "0", "fix_hole_2_x": "0", "fix_hole_2_y": "14"})
    good = {"H03": (0.0, 0.0, 10.0), "H04": (0.0, 14.0, 10.0), "H09": (50.0, 0.0, 10.0)}
    note = "Key %s, %s, fitted at the factory: stud face flush with this end. Only this way round do its bottom " \
           "holes meet %s and %s; turned round they are 9 mm off."
    assert readback.key_note_fails(note % (row["part_number"], row["joint"], "H03", "H04"), good, [row]) == []
    bad = readback.key_note_fails(note % (row["part_number"], row["joint"], "H03", "H09"), good, [row])
    assert bad and "H09" in bad[0], bad
    assert readback.key_note_fails("no notes here", good, [row])[0].startswith("no orientation note")
    # a HOLD note stands in only while the STEP has no hole at the key's screw positions
    held = "HOLD: Joints' key file puts key %s, %s, in this end, its screws at ... yet." % (row["part_number"], row["joint"])
    assert readback.key_note_fails(held, good, [row], holes=[{"c": (50.0, 0.0, 10.0)}]) == []
    late = readback.key_note_fails(held, good, [row], holes=[{"c": (0.0, 14.0, 10.0)}])
    assert late and "draw the key note" in late[0], late


def test_two_wall_pairs_are_on_one_line():
    """Two parallel holes side by side in one wall are not a two-wall pair (BASE's FR1: two Ø13 glide nut holes
    546.5 apart in its bottom wall); two holes on one line through both walls are."""
    side = [{"tag": "H01", "kind": "hole", "body": "FR1", "axis": (0, 0, 1), "entry": (0.0, 0.0, 0.0)},
            {"tag": "H02", "kind": "hole", "body": "FR1", "axis": (0, 0, 1), "entry": (546.5, 0.0, 0.0)}]
    assert readback.two_wall_pairs(side) == []
    through = side[:1] + [{"tag": "H03", "kind": "hole", "body": "FR1", "axis": (0, 0, -1), "entry": (0.0, 0.0, 100.0)}]
    assert readback.two_wall_pairs(through) == [("H01", "H03")]
    other = side[:1] + [{"tag": "H04", "kind": "hole", "body": "STILE", "axis": (0, 0, 1), "entry": (0.0, 0.0, 100.0)}]
    assert readback.two_wall_pairs(other) == []


def test_an_entry_for_another_material_is_refused():
    """An entry written for one material (D-131's welded steel frames) never draws over a parts list that gives
    another: the list and the model change first."""
    spec = dict(specs.SPECS["211101"][2], material_has="unobtainium", material_why="a test")
    try:
        compose.make("211101", "wall", spec, os.path.join(TMP, "material.pdf"))
    except compose.NotDrawable as e:
        assert "unobtainium" in str(e) and "a test" in str(e), e
    else:
        raise AssertionError("drew a frame whose entry is for another material")


def test_angled_face_gets_its_own_view():
    """Holes square to a face no principal view looks at straight (Joints' front corner key 111212: two tapped
    holes square to its 24.14° stud face) get a lettered view square to that face, with its own origin and hole
    table, and an arrow in the view that shows the face edge on; the key's blind tapped holes read as blind, with
    their drill point, and the angled through holes as THRU (a solid, not a tube wall). It reads back."""
    out = os.path.join(TMP, "aux")
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "111212.pdf")
    rep = compose.make("111212", "joints", {"pod_system": False, "corner": "-X-Y-Z", "tolerance": "test"}, p)
    fails, st = readback.check(p)
    assert not fails, fails
    assert st["worst_table"] <= 0.05 and st["worst_drawn"] <= 0.05
    text = fitz.open(p)[0].get_text()
    assert "looking square to the angled face" in text and "VIEW D" in text, text[:400]
    assert text.count("THRU (34)") == 2 and text.count("18 deep, drill point 118°") == 2, text


def test_long_words_break_at_separators():
    """A word wider than its cell (a long drawing number in the title block, FRONT's 352211) breaks after its '_'
    or '-', each line inside the cell, and nothing is lost."""
    from sheet import Sheet
    sh = Sheet("A3")
    word = "352211_P01_FRONT-DECOR-FRAME-DT-CHAMFER-CROSS-TUBE-3-OFF_DWG"
    lines = sh.wrap(word, 2.5, 115.6, True)
    assert len(lines) > 1 and "".join(lines) == word, lines
    assert all(sh.text_width(l_, 2.5, True) <= 115.6 for l_ in lines), lines
    sentence = "a normal sentence wraps at spaces"
    ls = sh.wrap(sentence, 2.5, 40)
    assert " ".join(ls) == sentence and all(sh.text_width(l_, 2.5) <= 40 for l_ in ls), ls


def test_a_repeated_part_is_drawn_once():
    """A part an assembly STEP holds several times (BASE's glide doubler 111601, 5 in the band assembly) loads
    as one occurrence, with the count kept for the drawing's quantity note and its check against the list."""
    import geom
    bodies, unit = geom.load_part(os.path.join(drawgen.inputs.REPO, "v2", "03-Manufacturing", "base",
                                               "110000_P01_BASE_STEP.step"), "111601")
    assert len(bodies) == 1 and unit["occurrences"] == 5, (len(bodies), unit)


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
