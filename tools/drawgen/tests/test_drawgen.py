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
12. BASE's D-129 back band features on a test band: open slots sized from the edge, the notches in a detail, the
    bevels called out; the read-back checks each against the STEP. A flat feature it can't size is refused.
13. Holes at a tap drill's size are refused as tapped unless the entry lists them as rivet holes (BASE's D-130
    boot); then the table names the rivet. A list row that says tapped is still refused.
"""

import math
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


def _profile(path, kind):
    """Test members along Y: 'stub' a 20 x 20 x 1 tube only 15 long (shorter than its section, as FRONT's C10);
    'angle' a 20 x 20 x 2 extruded angle 600 long; 'bevelled' a 20 x 40 x 1.2 tube 600 long with a 1 x 45° bevel along
    one outer corner (CEILING's seam member)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Pnt, gp_Vec

    def box(x, y, z, dx, dy, dz):
        return BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()
    if kind == "stub":
        sh = cut(box(0, 0, 0, 20, 15, 20), box(1, -1, 1, 18, 17, 18))
    elif kind == "angle":
        sh = cut(box(0, 0, 0, 20, 600, 20), box(2, -1, 2, 19, 602, 19))
    else:
        sh = cut(box(0, 0, 0, 20, 600, 40), box(1.2, -1, 1.2, 17.6, 602, 37.6))
        poly = BRepBuilderAPI_MakePolygon()
        for q in ((20, -1, 0), (19, -1, 0), (20, -1, 1)):
            poly.Add(gp_Pnt(*q))
        poly.Close()
        sh = cut(sh, BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(0, 602, 0)).Shape())
    w = STEPControl_Writer()
    w.Transfer(sh, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def test_profiles_and_short_tubes():
    """A tube shorter than its section (FRONT's 15 mm C10 stub) is cut across its own axis, so it reads as a tube,
    not a folded sheet. A member whose section is an angle (an extrusion: its list says so) or a tube with a bevel
    along a corner is refused as a profile to size, not drawn with only its outer sizes (the sweep found FRONT's
    kick strip 361002 drawn so)."""
    d = os.path.join(TMP, "profiles")
    os.makedirs(d, exist_ok=True)
    stub = _profile(os.path.join(d, "219994_P01_TEST-STUB_STEP.step"), "stub")
    compose.Part("219994", "none", step=stub, row=dict(ROW, part_number="219994"))      # not refused as folded
    for pn, kind, proc in (("219993", "angle", "extruded angle, cut"), ("219992", "bevelled", "cut")):
        step = _profile(os.path.join(d, "%s_P01_TEST-%s_STEP.step" % (pn, kind.upper())), kind)
        try:
            compose.Part(pn, "none", step=step, row=dict(ROW, part_number=pn, process=proc))
            raise AssertionError("drew a %s as a plain member" % kind)
        except compose.NotDrawable as e:
            assert "is a profile" in str(e), (kind, str(e))


def _cut_tube(path, kind, deg=45.0):
    """A 20 x 20 x 1.5 tube along X, 300 long. 'band': its +X end mitred deg from square in the XZ plane, which the view
    drawgen picks first (from below) sees face on; 'top': both ends cut deg in the XZ plane, the top face (+Z) running the full length;
    'turned': square ends, the section turned 45° about the tube's axis (FRONT's 352208)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_Transform
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()

    def prism(pts, v):
        poly = BRepBuilderAPI_MakePolygon()
        for q in pts:
            poly.Add(gp_Pnt(*q))
        poly.Close()
        return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(*v)).Shape()
    sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 300, 20, 20).Shape(),
             BRepPrimAPI_MakeBox(gp_Pnt(-1, 1.5, 1.5), 302, 17, 17).Shape())
    k = 20.0 * math.tan(math.radians(deg))
    if kind == "band":
        sh = cut(sh, prism([(300, -1, 0), (300 - k, -1, 20), (301, -1, 20), (301, -1, 0)], (0, 22, 0)))
    elif kind == "top":
        sh = cut(sh, prism([(300, -1, 20), (300 - k, -1, 0), (301, -1, 0), (301, -1, 20)], (0, 22, 0)))
        sh = cut(sh, prism([(0, -1, 20), (k, -1, 0), (-1, -1, 0), (-1, -1, 20)], (0, 22, 0)))
    elif kind == "turned":
        t = gp_Trsf()
        t.SetRotation(gp_Ax1(gp_Pnt(0, 10, 10), gp_Dir(1, 0, 0)), math.radians(45.0))
        sh = BRepBuilderAPI_Transform(sh, t, True).Shape()
    w = STEPControl_Writer()
    w.Transfer(sh, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def test_end_cuts_print_their_angles():
    """FRONT's #320 (Reviewer 7): a mitre that the only planned view sees face on gets a view that shows it in
    profile, its angle printed at its end; the read-back finds every end cut in the STEP on its own and fails a sheet
    whose angle isn't there (here: the 45° sheet against a model cut at 36.87°). A tube turned about its axis is drawn
    square to its faces (20 high, not 28.28: FRONT's 352208), and a top face as long as the part isn't sized twice
    (FRONT's 352203)."""
    d = os.path.join(TMP, "endcuts")
    os.makedirs(d, exist_ok=True)
    row = dict(ROW, part_number="219991")
    step = _cut_tube(os.path.join(d, "219991_P01_TEST-BAND_STEP.step"), "band")
    p = os.path.join(d, "band.pdf")
    face_on = dict(SPEC, principal={"look": "+Z", "x": "+X"})      # its principal sees the mitre face on
    compose.make("219991", "none", face_on, p, step=step, row=row)
    fails, _st = readback.check(p, step)
    assert not fails, fails
    text = " ".join(fitz.open(p)[0].get_text().split())
    assert "45°" in text, text[:500]
    other = _cut_tube(os.path.join(d, "219991_P01_TEST-OTHER_STEP.step"), "band", deg=36.87)
    f2, _ = readback.check(p, other)
    assert any("36.87° from square" in x for x in f2), f2
    step = _cut_tube(os.path.join(d, "219990_P01_TEST-TURNED_STEP.step"), "turned")
    p = os.path.join(d, "turned.pdf")
    compose.make("219990", "none", SPEC, p, step=step, row=dict(ROW, part_number="219990"))
    words = fitz.open(p)[0].get_text().split()
    assert "20" in words and "28.28" not in words, words[:80]
    step = _cut_tube(os.path.join(d, "219989_P01_TEST-TOP_STEP.step"), "top", deg=30.0)
    p = os.path.join(d, "top.pdf")
    compose.make("219989", "none", SPEC, p, step=step, row=dict(ROW, part_number="219989"))
    fails, _st = readback.check(p, step)
    assert not fails, fails
    words = fitz.open(p)[0].get_text().split()
    assert words.count("300") == 1 and "30°" in words, words[:80]


def test_bent_sheet_from_step_and_dxf():
    """The Lead's ruling (2026-11-01): bent parts come from the generator. WALL's tray 511101 (radiused bends, two runs
    of them) and INTERIOR's ledge 811101 (sharp folds, its inside radius from its entry) draw from main's STEP and DXF:
    a profile section per run of bends, the flat pattern from the DXF, a bend table. The DXF's bend lines sit where the
    model's flanges put them at one K-factor (0.44); the read-back fails the same sheet against a DXF whose bend line
    moved 0.5 mm, and a DXF with a hole the model hasn't is refused."""
    import sheetmetal
    d = os.path.join(TMP, "bent")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "511101.pdf")
    compose.make("511101", "wall", {"tolerance": "test", "bent": True}, p)
    fails, _st = readback.check(p)
    assert not fails, fails
    data = readback.read_data(fitz.open(p))
    assert len(data["flat"]["rows"]) == 8 and abs(data["flat"]["k"] - 0.44) < 0.001, data["flat"]
    assert all(r["dir"] == "UP" for r in data["flat"]["rows"]) and data["flat"]["r"] == 0.5, data["flat"]["rows"]
    p2 = os.path.join(d, "811101.pdf")
    compose.make("811101", "interior", {"tolerance": "test", "bent": {"radius": 1.5, "radius_why": "test"}}, p2)
    doc = fitz.open(p2)
    fails, _st = readback.check(p2)
    assert not fails, fails
    text = " ".join(doc[0].get_text().split())
    assert "FLAT PATTERN" in text and "BENDS B1-B2" in text and "K-factor 0.44" in text, text[:400]
    data2 = readback.read_data(doc)
    src = os.path.join(readback.REPO, data2["flat"]["dxf"])
    moved = os.path.join(d, "811101_moved_DXF.dxf")
    with open(src) as fh:
        dtext = fh.read()
    assert dtext.count("271.0894") == 2
    with open(moved, "w") as fh:
        fh.write(dtext.replace("271.0894", "271.5894"))
    data2["flat"]["dxf"] = moved
    f2 = readback.flat_fails(data2, readback.text_boxes(doc[0], data2["sheet_h"]), doc[0].get_text())
    assert any("on no BEND line" in x for x in f2) and any("put a bend line" in x for x in f2), f2
    holed = os.path.join(d, "811101_holed_DXF.dxf")
    with open(holed, "w") as fh:
        assert dtext.count("ENTITIES\n") == 1
        fh.write(dtext.replace("ENTITIES\n", "ENTITIES\n0\nCIRCLE\n8\nCUT\n10\n500.0\n20\n140.0\n40\n5.0\n", 1))
    import geom
    bodies, _u = geom.load_part(compose.find_step("811101", "interior"), "811101")
    try:
        sheetmetal.analyse(bodies[0], holed, radius=1.5, holes=[])
        raise AssertionError("drew a flat with a hole the model hasn't")
    except ValueError as e:
        assert "its DXF has 1 holes, its model none" in str(e), str(e)


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


def test_notes_name_no_maker():
    """The Lead's rulings (2026-11-01, #302): a note names the source, never an agent, a role, a script or tool, a
    team or a person as its maker; a process may be named ("holes made by drilling after welding", "made by
    bending the flange", as the steel-frame and bond notes say). The title block's CREATED BY Autonomous is the one
    maker field. The read-back fails only the first kind, by the mechanical check's own rule."""
    from sheet import Sheet
    d = os.path.join(TMP, "maker")
    os.makedirs(d, exist_ok=True)
    sh = Sheet("A3")
    sh.text(300, 280, "CREATED BY", 2.0)
    sh.text(300, 276, "Autonomous", 2.5)
    sh.text(30, 100, "Source: the STEP. Made by tools/drawgen (D-112) from that STEP.", 2.5)
    sh.text(30, 90, "From that STEP: regenerate it, never edit the PDF.", 2.5)
    sh.text(30, 80, "Holes made by drilling after welding; deburr both sides.", 2.5)
    sh.text(30, 70, "The flange is made by bending, inside radius 1.", 2.5)
    sh.text(30, 60, "Faces prepared by abrasive pad before bonding.", 2.5)
    sh.text(30, 50, "Drawn by the WALL Engineer.", 2.5)
    sh.save(os.path.join(d, "m.pdf"))
    found = readback.note_makers(fitz.open(os.path.join(d, "m.pdf")))
    assert len(found) == 2 and "tools/drawgen" in found[0][1] and "Engineer" in found[1][1], found


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
    # the key's holes are tapped: the guard (item 5 not in yet) is lifted to test the view itself
    rep = compose.make("111212", "joints", {"pod_system": False, "corner": "-X-Y-Z", "tolerance": "test",
                                            "_test_allow_tapped": True}, p)
    fails, st = readback.check(p)
    assert not fails, fails
    assert st["worst_table"] <= 0.05 and st["worst_drawn"] <= 0.05
    doc = fitz.open(p)
    text = doc[0].get_text()
    assert "looking square to the angled face" in text and "VIEW D" in text, text[:400]
    assert text.count("THRU (34)") == 2 and text.count("18 deep, drill point 118°") == 2, text
    # its own origin: X from the face's centre line, Y from its bottom (Joints' key sheet: 26 and 60 above it)
    import re as _re
    assert sorted(_re.findall(r"H0[34]\s+(-?[\d.]+)\s+(-?[\d.]+)", text)) == [("0.00", "26.00"), ("0.00", "60.00")], text
    assert "Holes go THRU the part" in doc[1].get_text()


def test_tapped_holes_wait_for_their_callouts():
    """A part with tapped holes isn't drawn until thread callouts land (item 5; the PM's ruling on #296): the
    front corner key 111212 (M6 tapped, Ø5.03 at a tap drill's size) is refused and says why."""
    try:
        compose.make("111212", "joints", {"pod_system": False, "tolerance": "test"}, os.path.join(TMP, "tap.pdf"))
    except compose.NotDrawable as e:
        assert "tapped holes" in str(e) and "item 5" in str(e), e
    else:
        raise AssertionError("drew a part with tapped holes")


def _drilled_bar(path, dia):
    """A 300 x 40 x 20 bar with two holes of one size through its thickness."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    sh = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 300, 40, 20).Shape()
    for x in (50.0, 250.0):
        c = BRepAlgoAPI_Cut(sh, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, 20, -1), gp_Dir(0, 0, 1)), dia / 2, 22).Shape())
        c.Build()
        sh = c.Shape()
    w = STEPControl_Writer()
    w.Transfer(sh, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def test_rivet_holes_pass_the_tapped_guard():
    """BASE's D-130 boot takes blind rivets in holes of tap drills' sizes (3.3, 4.2, about 5.0; Reviewer 5): a part
    with Ø4.2 holes is refused as tapped, unless its entry lists 4.2 as a rivet hole; then it is drawn and its table
    names the rivet. A parts-list row that says tapped is still refused."""
    d = os.path.join(TMP, "rivet")
    os.makedirs(d, exist_ok=True)
    step = _drilled_bar(os.path.join(d, "219995_P01_TEST-BAR-RIVETED_STEP.step"), 4.2)
    row = dict(ROW, part_number="219995", name="TEST - BAR - RIVETED")
    try:
        compose.make("219995", "none", SPEC, os.path.join(d, "a.pdf"), step=step, row=row)
        raise AssertionError("drew Ø4.2 holes as plain holes")
    except compose.NotDrawable as e:
        assert "tapped holes" in str(e) and "Ø4.2" in str(e), e
    spec = dict(SPEC, rivet_holes={4.2: "blind rivet, Ø4 (test)"})
    p = os.path.join(d, "b.pdf")
    compose.make("219995", "none", spec, p, step=step, row=row)
    text = " ".join(fitz.open(p)[0].get_text().split())
    assert text.count("rivet hole: blind rivet, Ø4 (test)") == 2, text[:800]
    try:
        compose.make("219995", "none", spec, os.path.join(d, "c.pdf"), step=step,
                     row=dict(row, process="drilled and tapped M5"))
        raise AssertionError("drew a part whose list says tapped")
    except compose.NotDrawable as e:
        assert "its parts list says so" in str(e), e


def test_text_width_matches_the_printed_text():
    """The free-space boxes are as wide as the printed text, Ø and µ included (fitz.get_text_length under-measured
    them: 'Ø9.53' 7.55 against 9.48 printed; the Air Engineer's read-back found it): each width within 0.05 mm of the
    PDF's own span box, regular and bold."""
    from sheet import Sheet
    d = os.path.join(TMP, "widths")
    os.makedirs(d, exist_ok=True)
    sh = Sheet("A3")
    samples = ["Ø9.53", "µm", "45°", "1 x 45°", "H01  Ø13 THRU 1 WALL"]
    for i, t in enumerate(samples):
        sh.text(30, 250 - 10 * i, t, 2.5)
        sh.text(200, 250 - 10 * i, t, 2.5, bold=True)
    sh.save(os.path.join(d, "w.pdf"))
    spans = {}
    for b in fitz.open(os.path.join(d, "w.pdf"))[0].get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                spans[(sp["text"], "Bold" in sp["font"])] = (sp["bbox"][2] - sp["bbox"][0]) / (72 / 25.4)
    for t in samples:
        for bold in (False, True):
            assert abs(spans[(t, bold)] - sh.text_width(t, 2.5, bold)) < 0.05, (t, bold, spans[(t, bold)],
                                                                             sh.text_width(t, 2.5, bold))


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
    """A part an assembly STEP holds several times (BASE's glide doubler 111601 in the band assembly) loads as one
    occurrence, with the count kept for the drawing's quantity note and its check against the list. The count is
    BASE's parts list's per-pod total (5 before BASE's D-129 P02, 9 after), so the test follows BASE's model."""
    import csv
    import geom
    base = os.path.join(drawgen.inputs.REPO, "v2", "03-Manufacturing", "base")
    with open(os.path.join(base, "110000_P01_BASE_BOM.csv"), newline="", encoding="utf-8") as fh:
        want = sum(int(float(r["qty_per_pod"])) for r in csv.DictReader(fh) if r["part_number"] == "111601")
    bodies, unit = geom.load_part(os.path.join(base, "110000_P01_BASE_STEP.step"), "111601")
    assert want > 1 and len(bodies) == 1 and unit["occurrences"] == want, (want, len(bodies), unit)


def _notched_band(path, length=1000.0, notch_w=12.0, window=False):
    """A test back band like BASE's D-129 111103: a 100 x 40 x 1.5 tube closed by 1.5 end plates, each plate with an
    open slot (12 wide at the bottom edge, 6.5 from 6 up, its R3.25 end centred 63.5 up), a notch_w x 9 notch
    through the bottom wall at each end and a 1 x 45° bevel on each end's bottom edge, either side of the notch.
    window: a 20 x 10 cut-out through the top wall's middle too (a flat feature drawgen can't size)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec

    def box(x, y, z, dx, dy, dz):
        return BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()

    def prism(pts, v):
        poly = BRepBuilderAPI_MakePolygon()
        for q in pts:
            poly.Add(gp_Pnt(*q))
        poly.Close()
        return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(*v)).Shape()

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        assert c.IsDone()
        return c.Shape()
    L = length
    sh = cut(box(0, 0, 0, L, 40, 100), box(1.5, 1.5, 1.5, L - 3, 37, 97))
    for x0 in (-1.0, L - 2.5):
        sh = cut(sh, prism([(x0, 14, 0), (x0, 26, 0), (x0, 23.25, 6), (x0, 16.75, 6)], (3.5, 0, 0)))
        sh = cut(sh, box(x0, 16.75, 6, 3.5, 6.5, 57.5))
        # the cylinder's seam down, inside the straight cut: the slot's end stays one half-round face, as Fusion
        # writes it
        sh = cut(sh, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, 20, 63.5), gp_Dir(1, 0, 0), gp_Dir(0, 0, -1)),
                                              3.25, 3.5).Shape())
    a = 20 - notch_w / 2
    sh = cut(sh, box(-1, a, -1, 10, notch_w, 2.5))
    sh = cut(sh, box(L - 9, a, -1, 10, notch_w, 2.5))
    sh = cut(sh, prism([(0, -1, 0), (1, -1, 0), (0, -1, 1)], (0, 42, 0)))
    sh = cut(sh, prism([(L, -1, 0), (L - 1, -1, 0), (L, -1, 1)], (0, 42, 0)))
    if window:
        sh = cut(sh, box(L / 2 - 10, 15, 97, 20, 10, 5))
    w = STEPControl_Writer()
    w.Transfer(sh, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


BAND_ROW = dict(ROW, part_number="219997", name="TEST - BAND - NOTCHED", material="aluminium 6063-T6 tube with end plates")


def test_open_slot_notch_and_bevel_are_sized():
    """BASE's D-129 back band features, on a test band: each open slot sized from the edge in its end's own view
    (mouth, taper, width, radius, the end's centre from the edge); the 12 x 9 notches in the bottom wall sized
    once in a detail from below (width, place across, length from the end), the drawing saying the other end's is
    the same; each end's 1 x 45° bevel called out (not read as a mitre). The read-back passes, and fails the same
    drawing against a model whose notches are 10 wide."""
    d = os.path.join(TMP, "notched")
    os.makedirs(d, exist_ok=True)
    step = _notched_band(os.path.join(d, "219997_P01_TEST-BAND-NOTCHED_STEP.step"))
    p = os.path.join(d, "219997.pdf")
    compose.make("219997", "none", SPEC, p, step=step, row=BAND_ROW)
    fails, st = readback.check(p, step)
    assert not fails, fails
    doc = fitz.open(p)
    text = doc[0].get_text()
    flat = " ".join(text.split())
    assert flat.count("1 x 45°") == 2 and "45° " not in flat.replace("1 x 45°", ""), flat[:600]
    assert "DETAIL" in text and "the notch at the -X end is the same" in flat, flat[:600]
    data = readback.read_data(doc)
    assert len(data["notches"]) == 2 and len(data["chamfers"]) == 2 and len(data["plates"]) == 2, data["notches"]
    shown = [n for n in data["notches"] if n["drawn"]]
    assert len(shown) == 1 and shown[0]["texts"]["width"] == "12" and shown[0]["texts"]["length"] == "9" and \
        shown[0]["texts"]["pos"] == "14", shown
    slots = [f for f in data["features"] if f["kind"] == "open_slot"]
    assert len(slots) == 2 and all(f["dims"] == {"width": "6.5", "mouth": "12", "edge": "63.5", "r": "R3.25",
                                                  "taper": "6"} for f in slots), slots
    narrow = _notched_band(os.path.join(d, "219997_P01_TEST-BAND-NARROW_STEP.step"), notch_w=10.0)
    f2, _ = readback.check(p, narrow)
    assert any("notch" in x for x in f2), f2


def test_an_unsized_flat_feature_is_refused():
    """A flat-faced feature drawgen can't size yet (here a cut-out in the middle of a tube's top wall) is refused
    with the faces named, rather than drawn without sizes."""
    d = os.path.join(TMP, "window")
    os.makedirs(d, exist_ok=True)
    step = _notched_band(os.path.join(d, "219996_P01_TEST-BAND-WINDOW_STEP.step"), window=True)
    try:
        compose.make("219996", "none", SPEC, os.path.join(d, "w.pdf"), step=step,
                     row=dict(BAND_ROW, part_number="219996"))
        raise AssertionError("drew a part with an unsized cut-out")
    except compose.NotDrawable as e:
        assert "flat faces this tool can't size yet" in str(e) and "Z 98.50..100.00" in str(e), str(e)


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
