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
    not a folded sheet. A member whose section is an angle (an extrusion: its list says so) is refused as a profile to
    size, not drawn with only its outer sizes (the sweep found FRONT's kick strip 361002 drawn so). A tube with a
    1 x 45° bevel along an outer corner (CEILING's seam member) is drawn, the bevel called out where a view shows its
    true angle, and read back against the STEP."""
    d = os.path.join(TMP, "profiles")
    os.makedirs(d, exist_ok=True)
    stub = _profile(os.path.join(d, "219994_P01_TEST-STUB_STEP.step"), "stub")
    compose.Part("219994", "none", step=stub, row=dict(ROW, part_number="219994"))      # not refused as folded
    step = _profile(os.path.join(d, "219993_P01_TEST-ANGLE_STEP.step"), "angle")
    try:
        compose.Part("219993", "none", step=step, row=dict(ROW, part_number="219993", process="extruded angle, cut"))
        raise AssertionError("drew an extruded angle as a plain member")
    except compose.NotDrawable as e:
        assert "is a profile" in str(e), str(e)
    step = _profile(os.path.join(d, "219992_P01_TEST-BEVELLED_STEP.step"), "bevelled")
    p = os.path.join(d, "bevelled.pdf")
    compose.make("219992", "none", SPEC, p, step=step, row=dict(ROW, part_number="219992", process="cut"))
    fails, _st = readback.check(p, step)
    assert not fails, fails
    data = readback.read_data(fitz.open(p))
    assert [c["long"] for c in data["chamfers"]] == [True] and data["chamfers"][0]["text"] == "1 x 45°", data["chamfers"]


def test_ceiling_frame_bevels():
    """CEILING's frame C1 (411101, main's STEP): the back member's 1 x 45° end bevel, which no view looks along, is
    called out where it shows as a band; the seam member's bevel along its whole length, in the removed section
    across that member at its true angle. Both read back against the STEP."""
    d = os.path.join(TMP, "ceiling")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "411101.pdf")
    compose.make("411101", "ceiling", {"tolerance": "test"}, p)
    fails, _st = readback.check(p)
    assert not fails, fails
    doc = fitz.open(p)
    data = readback.read_data(doc)
    assert sorted(c["long"] for c in data["chamfers"]) == [False, True], data["chamfers"]
    assert "showing its bevel along it" in " ".join(doc[0].get_text().split())      # its 2:1 section (Reviewer 6)
    # Reviewer 6's plant on #331: the seam bevel's callout moved 50 mm, its record moved with it: the read-back
    # still finds the bevel in the STEP and fails the callout that isn't by it
    step = os.path.join(readback.REPO, [s_ for s_ in data["sources"] if s_["role"] == "STEP"][0]["path"])
    planes = [f for f in readback.step_faces(step, data["pn"], data.get("placement"))
              if f["kind"] == "plane" and "n" in f and f["pts"]]
    texts = readback.text_boxes(doc[0], data["sheet_h"])
    assert not readback.flat_feature_fails(data, planes, texts)
    i = next(j for j, c in enumerate(data["chamfers"]) if c["long"])
    bx, tip = data["chamfers"][i]["box"], data["chamfers"][i]["tip"]
    moved = [(t[0] + 50, t[1], t[2] + 50, t[3], t[4], t[5]) if t[4] == "1 x 45°" and abs(t[0] - bx[0]) < 3 and
             abs(t[1] - bx[1]) < 3 else t for t in texts]
    assert moved != texts
    data["chamfers"][i]["box"] = [bx[0] + 50, bx[1], bx[2] + 50, bx[3]]
    data["chamfers"][i]["tip"] = [tip[0] + 50, tip[1]]
    f2 = readback.flat_feature_fails(data, planes, moved)
    assert any("along the member: its size 1 x 45° is not printed by it" in x for x in f2), f2


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
        assert "its DXF has 1 round holes, its model 0" in str(e) and "Ø10 hole at (500, 140) is on no hole" in str(e), e
    # Reviewer 6 on #335: a Ø10 hole the model hasn't, planted in the DXF of 511101 (bent both ways): refused, and the
    # read-back of 511101's sheet fails against that DXF
    data = readback.read_data(fitz.open(p))
    src = os.path.join(readback.REPO, data["flat"]["dxf"])
    with open(src) as fh:
        wtext = fh.read()
    import dxf as dxfmod
    bx = dxfmod.Dxf(src).cut_box()
    cx, cy = round((bx[0] + bx[2]) / 2, 3), round((bx[1] + bx[3]) / 2, 3)
    planted = os.path.join(d, "511101_planted_DXF.dxf")
    with open(planted, "w") as fh:
        assert wtext.count("ENTITIES\n") == 1
        fh.write(wtext.replace("ENTITIES\n", "ENTITIES\n0\nCIRCLE\n8\nCUT\n10\n%r\n20\n%r\n40\n5.0\n" % (cx, cy), 1))
    b511, _u = geom.load_part(compose.find_step("511101", "wall"), "511101")
    try:
        sheetmetal.analyse(b511[0], planted, holes=[])
        raise AssertionError("drew 511101 with a hole the model hasn't")
    except ValueError as e:
        assert "its DXF has 1 round holes, its model 0" in str(e) and "is on no hole of the model" in str(e), e
    data["flat"]["dxf"] = planted
    doc1 = fitz.open(p)
    faces = readback.step_faces(os.path.join(readback.REPO, [s_ for s_ in data["sources"] if s_["role"] == "STEP"][0]["path"]),
                                data["pn"], data.get("placement"))
    f3 = readback.flat_hole_fails(data, [], faces)
    assert any("has 1 round holes, the STEP 0" in x for x in f3) and any("on no STEP hole" in x for x in f3), f3
    assert doc1 is not None


def test_a_sharp_v_groove_is_refused():
    """D-161 (Reviewer 6 on #341): a V-grooved ACP fold bends its outer skin round a radius (2 mm minimum), so a model
    that leaves the fold sharp would develop as the plain sum of the outside lengths, 0.86 too long. A test skin
    modelled sharp is refused, even against the blank that fits it."""
    d = os.path.join(TMP, "vgroove_sharp")
    os.makedirs(d, exist_ok=True)
    step = _rounded_skin(os.path.join(d, "219992_P01_TEST-SKIN-SHARP_STEP.step"), r=0.0)
    sharp, _w, _x = _skin_dxf(os.path.join(d, "219992_sharp_DXF.dxf"), 0.0)
    row = dict(ROW, part_number="219992", name="TEST - SKIN SHARP", material="ACP 3", process="CNC router, V-groove, fold")
    try:
        compose.make("219992", "none", dict(SPEC, bent={"vgroove": "test", "dxf": sharp}), os.path.join(d, "s.pdf"),
                     step=step, row=row)
        raise AssertionError("drew a V-groove fold the model leaves sharp")
    except compose.NotDrawable as e:
        assert "V-groove fold is sharp in the model" in str(e), e


def _rounded_skin(path, r=2.0):
    """A V-grooved ACP skin as WALL now models it (the Lead's ruling, 2026-11-01): a 3 mm panel, its main face 300 long
    and its return 46 (outside lengths, to the fold's outside sharp), 100 high, sharp inside (the groove closes) and
    rounded outside at R r (the maker's guide: 2 minimum)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.GeomAbs import GeomAbs_Line
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    from OCP.gp import gp_Pnt
    f = BRepAlgoAPI_Fuse(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 300, 3, 100).Shape(),
                         BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 3, 46, 100).Shape())
    f.SetFuzzyValue(1e-6)
    f.Build()
    u = ShapeUpgrade_UnifySameDomain(f.Shape(), True, True, True)
    u.Build()
    shape = u.Shape()
    mk = BRepFilletAPI_MakeFillet(shape)
    e = TopExp_Explorer(shape, TopAbs_EDGE)
    found = []
    if not r:           # left sharp
        e = TopExp_Explorer()
    while e.More():
        ed = TopoDS.Edge_s(e.Current())
        c = BRepAdaptor_Curve(ed)
        p0, p1 = c.Value(c.FirstParameter()), c.Value(c.LastParameter())
        if c.GetType() == GeomAbs_Line and max(abs(p0.X()), abs(p0.Y()), abs(p1.X()), abs(p1.Y())) < 1e-6 and \
                not any(ed.IsSame(f_) for f_ in found):      # each face meets it: one edge seen twice
            found.append(ed)
        e.Next()
    if r:
        assert len(found) == 1, len(found)
        mk.Add(r, found[0])         # the outer fold edge, along Z at X 0, Y 0
        mk.Build()
    w = STEPControl_Writer()
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 0)
    try:
        w.Transfer(mk.Shape() if r else shape, STEPControl_AsIs)
        assert w.Write(path) == IFSelect_RetDone
    finally:
        Interface_Static.SetIVal_s("write.surfacecurve.mode", 1)
    return path


def _skin_dxf(path, r):
    """_rounded_skin's blank by WALL's rule, worked here by hand: each leg to the fold's outside arc plus the arc,
    (46 - r) + (300 - r) + pi/2 r, the BEND line at the arc's middle, (46 - r) + pi/4 r from the return's edge."""
    w = (46.0 - r) + (300.0 - r) + math.pi / 2 * r
    x = (46.0 - r) + math.pi / 4 * r
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    pts = [(0.0, 0.0), (w, 0.0), (w, 100.0), (0.0, 100.0)]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % 4]
        out += ["0", "LINE", "8", "CUT", "10", repr(p[0]), "20", repr(p[1]), "11", repr(q[0]), "21", repr(q[1])]
    out += ["0", "LINE", "8", "BEND", "10", repr(x), "20", "0.0", "11", repr(x), "21", "100.0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    return path, w, x


def test_v_groove_with_its_outside_radius():
    """WALL's skins now model the fold's 2 mm outside radius (the Lead's ruling): the flat develops along the outer
    face, each leg to the arc plus the arc (0.86 less than sharp for a 90° fold at R2), the fold line at the arc's
    middle. A test skin with R2 outside draws against its blank by that rule and reads back, its folds table giving
    R2; the sharp blank (the sum of the outside lengths) is refused for it, and the sheet's read-back fails against
    that blank."""
    d = os.path.join(TMP, "vgroove_r")
    os.makedirs(d, exist_ok=True)
    step = _rounded_skin(os.path.join(d, "219995_P01_TEST-SKIN_STEP.step"))
    good, w, x = _skin_dxf(os.path.join(d, "219995_r2_DXF.dxf"), 2.0)
    sharp, w0, x0 = _skin_dxf(os.path.join(d, "219995_sharp_DXF.dxf"), 0.0)
    assert abs((w0 - w) - (4.0 - math.pi)) < 1e-9 and abs(w - 345.14) < 0.01 and abs(x - 45.57) < 0.01
    row = dict(ROW, part_number="219995", name="TEST - SKIN", material="ACP 3", process="CNC router, V-groove, fold")
    p = os.path.join(d, "219995.pdf")
    vg = "110° V, 2 mm flat root (test)"
    compose.make("219995", "none", dict(SPEC, bent={"vgroove": vg, "dxf": good, "outside_radius": 2}), p, step=step,
                 row=row)
    fails, _st = readback.check(p)
    assert not fails, fails
    doc = fitz.open(p)
    text = " ".join(doc[0].get_text().split())
    assert "FOLDS B1-B1" in text and "R2" in text and "middle of its fold's outside arc" in text, text[:600]
    data = readback.read_data(doc)
    assert data["flat"]["chains"][0]["radii_out"] == [2.0] and abs(data["flat"]["rows"][0]["at"] - x) < 1e-6, data["flat"]
    try:
        compose.make("219995", "none", dict(SPEC, bent={"vgroove": vg, "dxf": sharp}), os.path.join(d, "s.pdf"),
                     step=step, row=row)
        raise AssertionError("drew the R2 skin from a sharp blank")
    except compose.NotDrawable as e:
        assert "outside radius" in str(e), e
    data["flat"]["dxf"] = sharp
    f2 = readback.flat_fails(data, readback.text_boxes(doc[0], data["sheet_h"]), doc[0].get_text())
    assert any("flat is %s long, the DXF's 346" % readback._fmtv(w) in x_ for x_ in f2), f2
    # the fold line moved 0.5 mm in the blank: the read-back fails it
    with open(good) as fh:
        gtext = fh.read()
    assert gtext.count(repr(x)) == 2
    moved = os.path.join(d, "219995_moved_DXF.dxf")
    with open(moved, "w") as fh:
        fh.write(gtext.replace(repr(x), repr(x + 0.5)))
    data["flat"]["dxf"] = moved
    f3 = readback.flat_fails(data, readback.text_boxes(doc[0], data["sheet_h"]), doc[0].get_text())
    assert any("V-groove" in x_ for x_ in f3), f3
    # an entry that states another outside radius is refused; the read-back finds the arc in the STEP itself
    try:
        compose.make("219995", "none", dict(SPEC, bent={"vgroove": vg, "dxf": good, "outside_radius": 3}),
                     os.path.join(d, "r3.pdf"), step=step, row=row)
        raise AssertionError("drew an R2 fold against an entry's R3")
    except compose.NotDrawable as e:
        assert "outside radius R2, its entry says R3" in str(e), e
    data = readback.read_data(doc)
    data["flat"]["chains"][0]["radii_out"] = [2.5]
    f4 = readback.vgroove_radius_fails(data, readback.step_faces(step, "219995"))
    assert any("no outside arc R2.5" in x_ for x_ in f4), f4


def _spigot_rail(path, slot="along", width=20.0, hole_y=10.0, slot_y=10.0):
    """A 600 long rail along X, a 40 high x width x 1.2 tube seated on its bottom face, with a Ø8.5 spigot hole at
    X 100 and an 8.5 x 14 spigot slot at X 500 through its bottom wall; the slot runs along the rail (toward the
    hole when slot_y is hole_y) or across it. Returns the path and the slot's two end centres (X, Y)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()
    sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 600, width, 40).Shape(),
             BRepPrimAPI_MakeBox(gp_Pnt(-1, 1.2, 1.2), 602, width - 2.4, 40 - 2.4).Shape())
    sh = cut(sh, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(100, hole_y, -1), gp_Dir(0, 0, 1)), 4.25, 4).Shape())
    half = (14.0 - 8.5) / 2
    if slot == "along":
        ends = [(500 - half, slot_y), (500 + half, slot_y)]
        tool = BRepPrimAPI_MakeBox(gp_Pnt(500 - half, slot_y - 4.25, -1), 2 * half, 8.5, 4).Shape()
    else:
        ends = [(500, slot_y - half), (500, slot_y + half)]
        tool = BRepPrimAPI_MakeBox(gp_Pnt(500 - 4.25, slot_y - half, -1), 8.5, 2 * half, 4).Shape()
    for x, y in ends:
        f = BRepAlgoAPI_Fuse(tool, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, -1), gp_Dir(0, 0, 1)), 4.25, 4).Shape())
        f.Build()
        tool = f.Shape()
    u = ShapeUpgrade_UnifySameDomain(cut(sh, tool), True, True, True)
    u.Build()
    w = STEPControl_Writer()
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 0)
    try:
        w.Transfer(u.Shape(), STEPControl_AsIs)
        assert w.Write(path) == IFSelect_RetDone
    finally:
        Interface_Static.SetIVal_s("write.surfacecurve.mode", 1)
    return path, ends


def _spigot_sheet(d, pn, slot, spec=None, **kw):
    """_spigot_rail drawn with spigot datums, its hole and slot named as spigots by a test register."""
    step, ends = _spigot_rail(os.path.join(d, "%s_P01_TEST-RAIL-SPIGOT_STEP.step" % pn), slot, **kw)
    reg = os.path.join(d, "FEATURE-RATIONALE-%s.md" % pn)
    with open(reg, "w") as fh:
        fh.write("test register for %s\n" % pn)
    base = {"body": "", "dia": 8.5, "axis": "Z", "rule": "", "tolerance": "", "status": "", "file": reg,
            "mating": "the frame's spigot (test)"}
    rows = [dict(base, id="F-T-01", centres=[(100.0, kw.get("hole_y", 10.0))], function="spigot hole (test)"),
            dict(base, id="F-T-02", centres=ends, function="spigot slot (test)")]
    real = compose.inputs.feature_rows
    compose.inputs.feature_rows = lambda pn_, team: rows if pn_ == pn else real(pn_, team)
    try:
        p = os.path.join(d, "%s.pdf" % pn)
        row = dict(ROW, part_number=pn, name="TEST - RAIL - SPIGOT")
        compose.make(pn, "none", spec or {"datums": "spigot", "tolerance": "test", "iso": False}, p, step=step, row=row)
        return p
    finally:
        compose.inputs.feature_rows = real


def _datum_near(doc, data, tag, letter="C", within=25.0):
    """True when the sheet prints the datum letter within `within` mm of the feature's centre, in the view that shows
    it face on."""
    ft = next(f for f in data["features"] if f["tag"] == tag)
    tb = readback.text_boxes(doc[0], data["sheet_h"])
    for v in data["views"]:
        if abs(abs(sum(a * b for a, b in zip(v["n"], ft["axis"]))) - 1) > 1e-6:
            continue
        q = (sum(a * b for a, b in zip(ft["entry"], v["x"])), sum(a * b for a, b in zip(ft["entry"], v["y"])))
        c = (v["off"][0] + v["scale"] * q[0], v["off"][1] + v["scale"] * q[1])
        if any(t[4] == letter and math.dist(((t[0] + t[2]) / 2, (t[1] + t[3]) / 2), c) < within for t in tb):
            return True
    return False


def test_datum_c_is_the_spigot_slot_where_it_runs_along_the_rail():
    """The Lead's ruling on datum C (2026-11-01): a spigot slot that runs along its rail toward B (R-J13: CEILING's
    frames, WALL's back panels) stops the turn about B, so C is the slot, and the note says so. A test rail with its
    slot along it, in line with B: datum C is the slot, its symbol on the slot, and the note gives R-J13's sentence,
    never R-J17's. A slot along its rail but off B's line is refused, and so is an entry that names a face for C."""
    d = os.path.join(TMP, "datum_c_along")
    os.makedirs(d, exist_ok=True)
    p = _spigot_sheet(d, "219980", "along")
    fails, _st = readback.check(p)
    assert not fails, fails
    doc = fitz.open(p)
    data = readback.read_data(doc)
    slot = next(f for f in data["features"] if f["kind"] == "slot")
    hole = next(f for f in data["features"] if f["tag"] == data["datums"]["B"])
    assert hole["kind"] == "hole" and data["datums"]["C"] == "slot %s" % slot["tag"], data["datums"]
    notes = " ".join(" ".join(pg.get_text().split()) for pg in doc)
    want = ("C = the spigot slot %s, the median plane of its width (it runs along the rail toward B, R-J13, so it "
            "stops the turn about B)" % slot["tag"])
    assert want in notes and "R-J17" not in notes, notes[notes.find("Datums"):][:400]
    assert _datum_near(doc, data, slot["tag"]), "no datum C symbol at the slot"
    try:
        _spigot_sheet(d, "219979", "along", width=40.0, hole_y=10.0, slot_y=30.0)
        raise AssertionError("read datum C from a slot that misses B's line")
    except compose.NotDrawable as e:
        assert "its line passes 20 from B's axis" in str(e), e
    try:
        _spigot_sheet(d, "219978", "along", spec={"datums": "spigot", "c_face": "-Y", "tolerance": "test", "iso": False})
        raise AssertionError("took a face for C with the slot along the rail")
    except compose.NotDrawable as e:
        assert "so C is the slot" in str(e), e


def test_datum_c_is_a_face_where_the_spigot_slot_runs_across_the_rail():
    """The Lead's ruling on datum C (2026-11-01): a spigot slot that runs across its rail (R-J17: WALL's side
    panels' back ends) doesn't stop the turn about B, so C stays the room-side face. A test rail with its slot across
    it: datum C is that face, and the note gives R-J17's sentence, never R-J13's."""
    d = os.path.join(TMP, "datum_c_across")
    os.makedirs(d, exist_ok=True)
    p = _spigot_sheet(d, "219977", "across")
    fails, _st = readback.check(p)
    assert not fails, fails
    doc = fitz.open(p)
    data = readback.read_data(doc)
    slot = next(f for f in data["features"] if f["kind"] == "slot")
    assert data["datums"]["C"] == "plane -Y at 0", data["datums"]
    notes = " ".join(" ".join(pg.get_text().split()) for pg in doc)
    want = ("C = the room-side face (Y 0), which stops the turn about B (the spigot slot %s runs across the rail, "
            "R-J17, so it locates along the rail only)" % slot["tag"])
    assert want in notes and "R-J13, so it stops" not in notes, notes[notes.find("Datums"):][:400]
    assert not _datum_near(doc, data, slot["tag"], within=8.0), "a datum C symbol on the slot"


def test_datums_are_never_dropped():
    """WALL (the Lead's order): a corner datum whose face no plain view shows edge on was dropped without a word. It
    now goes on a section that shows its face edge on, or the sheet is refused. WALL's tray 511101 with its
    cassette's scheme (A the back face, B the end return, C the bottom return) prints all three, A on its profile
    section; a block whose datum face only its principal view sees face on is refused."""
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.gp import gp_Pnt
    d = os.path.join(TMP, "datums")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "511101.pdf")
    compose.make("511101", "wall", {"tolerance": "test", "bent": True, "datums": "faces",
                                    "datum_faces": {"A": "-X", "B": "-Y", "C": "-Z"}}, p)
    fails, _st = readback.check(p)
    assert not fails, fails
    words = [w[4] for w in fitz.open(p)[0].get_text("words")]
    assert all(words.count(L) == 3 for L in "ABC"), [words.count(L) for L in "ABC"]     # the border has two each
    step = os.path.join(d, "219985_P01_TEST-BLOCK_STEP.step")
    w = STEPControl_Writer()
    w.Transfer(BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 100, 60, 40).Shape(), STEPControl_AsIs)
    assert w.Write(step) == IFSelect_RetDone
    row = dict(ROW, part_number="219985", name="TEST - BLOCK")
    try:
        compose.make("219985", "none", dict(SPEC, datum_faces={"A": "-Z"}), os.path.join(d, "b.pdf"), step=step,
                     row=row)
        raise AssertionError("drew the block without its datum A")
    except compose.NotDrawable as e:
        assert "datum A on its -Z face shows edge on in no view or section drawn" in str(e), e


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


def _tray(path):
    """A 200 x 150 x 30 tray of 1 mm sheet folded sharp up all four sides (6 mm open corners), with a Ø8 hole through
    its front wall at X 60, Z 15: two runs of bends, square to each other, and a hole on a folded flange."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    shape = None
    for (x, y, z), (dx, dy, dz) in (((0, 0, 0), (200, 150, 1)), ((6, 0, 0), (188, 1, 30)), ((6, 149, 0), (188, 1, 30)),
                                    ((0, 6, 0), (1, 138, 30)), ((199, 6, 0), (1, 138, 30))):
        b = BRepPrimAPI_MakeBox(gp_Pnt(x, y, z), dx, dy, dz).Shape()
        if shape is None:
            shape = b
            continue
        f = BRepAlgoAPI_Fuse(shape, b)
        f.SetFuzzyValue(1e-6)
        f.Build()
        shape = f.Shape()
    c = BRepAlgoAPI_Cut(shape, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(60, -1, 15), gp_Dir(0, 1, 0)), 4.0, 3.0).Shape())
    c.Build()
    u = ShapeUpgrade_UnifySameDomain(c.Shape(), True, True, True)
    u.Build()
    # edges written as their own curves, no surface-curve wrapper, as Fusion writes them (the repo's STEP reader
    # reads a hole's circles so); the setting is put back after
    from OCP.Interface import Interface_Static
    w = STEPControl_Writer()          # first: making the writer sets the STEP settings to their defaults
    was = Interface_Static.IVal_s("write.surfacecurve.mode")
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 0)
    try:
        w.Transfer(u.Shape(), STEPControl_AsIs)
        assert w.Write(path) == IFSelect_RetDone
    finally:
        Interface_Static.SetIVal_s("write.surfacecurve.mode", was)
    return path


def _tray_dxf(path, hole_dx=0.0):
    """_tray's flat pattern, worked out here by hand (inside radius 1, K 0.44, 90° folds): OSSB (r + t) tan 45° = 2,
    allowance pi/2 (r + K t) = 2.262; x across the left and right folds, y across the front and back ones; the hole
    15 from the front wall's free edge and base0 + 60 along, moved hole_dx along x."""
    t, r, k = 1.0, 1.0, 0.44
    ossb = (r + t) * math.tan(math.radians(45.0))
    ba = math.radians(90.0) * (r + k * t)
    wall = 30.0 - ossb                          # each wall's straight part, from its free edge
    W = 200 + 2 * 30 - 4 * ossb + 2 * ba        # the flat across the left and right folds
    H = 150 + 2 * 30 - 4 * ossb + 2 * ba
    base0 = wall + ba - ossb                    # the base's pod 0 (its outer sharp) in the flat
    a, b, c, e = base0 + 6, base0 + 194, base0 + 6, base0 + 144     # the walls' ends
    x0, x1, y0, y1 = wall, W - wall, wall, H - wall                 # the bend zones' outer edges
    pts = [(a, 0), (b, 0), (b, y0), (x1, y0), (x1, c), (W, c), (W, e), (x1, e), (x1, y1), (b, y1), (b, H), (a, H),
           (a, y1), (x0, y1), (x0, e), (0, e), (0, c), (x0, c), (x0, y0), (a, y0)]
    ents = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        ents.append(("LINE", "CUT", p, q))
    for p, q in (((wall + ba / 2, c), (wall + ba / 2, e)), ((W - wall - ba / 2, c), (W - wall - ba / 2, e)),
                 ((a, wall + ba / 2), (b, wall + ba / 2)), ((a, H - wall - ba / 2), (b, H - wall - ba / 2))):
        ents.append(("LINE", "BEND", p, q))
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for _typ, lay, p, q in ents:
        out += ["0", "LINE", "8", lay, "10", repr(p[0]), "20", repr(p[1]), "11", repr(q[0]), "21", repr(q[1])]
    out += ["0", "CIRCLE", "8", "CUT", "10", repr(base0 + 60 + hole_dx), "20", repr(15.0), "40", "4.0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    return path, base0


def test_bent_holes_counted_both_ways():
    """Reviewer 6 on #335 (P1): a part bent both ways has its holes checked against the DXF too. A test tray with a
    Ø8 hole in its front wall draws and reads back PASS against its hand-worked DXF, every bend UP (the DXF shows the
    inside); with the DXF's hole moved 5 mm the generator refuses it, and the read-back of the good sheet fails
    against the moved DXF, both ways (the STEP's hole on no DXF hole, the DXF's hole on no STEP hole)."""
    import sheetmetal
    d = os.path.join(TMP, "tray")
    os.makedirs(d, exist_ok=True)
    step = _tray(os.path.join(d, "219996_P01_TEST-TRAY_STEP.step"))
    good, base0 = _tray_dxf(os.path.join(d, "219996_good_DXF.dxf"))
    moved, _b = _tray_dxf(os.path.join(d, "219996_moved_DXF.dxf"), hole_dx=5.0)
    row = dict(ROW, part_number="219996", name="TEST - TRAY", process="laser cut, brake bend")
    p = os.path.join(d, "219996.pdf")
    spec = dict(SPEC, bent={"radius": 1.0, "radius_why": "test", "dxf": good})
    compose.make("219996", "none", spec, p, step=step, row=row)
    fails, st = readback.check(p)
    assert not fails, fails
    data = readback.read_data(fitz.open(p))
    fl = data["flat"]
    assert len(fl["rows"]) == 4 and all(r_["dir"] == "UP" for r_ in fl["rows"]) and abs(fl["k"] - 0.44) < 1e-4, fl["rows"]
    assert fl["readings"] == 1, fl["readings"]          # the hole pins one of the four readings the symmetric runs allow
    try:
        compose.make("219996", "none", dict(SPEC, bent={"radius": 1.0, "radius_why": "test", "dxf": moved}),
                     os.path.join(d, "moved.pdf"), step=step, row=row)
        raise AssertionError("drew a tray whose DXF hole is 5 mm off")
    except compose.NotDrawable as e:
        want = "the model's Ø8 hole belongs at (%s, 15) in the flat" % sheetmetal._f(base0 + 60)
        assert want in str(e) and "is on no hole of the model" in str(e), e
    data["flat"]["dxf"] = moved
    faces = readback.step_faces(step, "219996")
    f2 = readback.flat_hole_fails(data, readback.step_holes(step, "219996"), faces)
    assert any("unfolds to (%s, 15)" % readback._fmtv(base0 + 60) in x for x in f2), f2
    assert any("Ø8 hole at (%s, 15) that is on no STEP hole" % readback._fmtv(base0 + 65) in x for x in f2), f2


def test_unpinned_bend_directions_are_refused():
    """Reviewer 6 on #335 (P2): with no hole to tell which way up the DXF is drawn, the readings left must fold the
    same part, so the flat must be symmetric the way they differ. INTERIOR's 811101 (no holes, a symmetric flat)
    draws; its DXF with one corner cut 5 x 5 isn't symmetric, so it is refused. WALL's 511202 is refused for its
    cut-outs that aren't round holes (the flat's check reads round holes only)."""
    import geom
    import sheetmetal
    d = os.path.join(TMP, "unpinned")
    os.makedirs(d, exist_ok=True)
    src = [f for f in os.listdir(os.path.join(readback.REPO, "v2", "03-Manufacturing", "interior"))
           if f.startswith("811101_") and f.endswith("_DXF.dxf")][0]
    with open(os.path.join(readback.REPO, "v2", "03-Manufacturing", "interior", src)) as fh:
        text = fh.read()
    corner = "VERTEX\n8\nCUT\n10\n0.0000\n20\n0.0000\n30\n0.0\n0\n"
    assert text.count(corner) == 1, "811101's outline changed: rework this test"
    cut = (corner.replace("20\n0.0000", "20\n5.0000") +
           corner.replace("10\n0.0000", "10\n5.0000"))
    bad = os.path.join(d, "811101_corner_DXF.dxf")
    with open(bad, "w") as fh:
        fh.write(text.replace(corner, cut))
    bodies, _u = geom.load_part(compose.find_step("811101", "interior"), "811101")
    fl = sheetmetal.analyse(bodies[0], os.path.join(readback.REPO, "v2", "03-Manufacturing", "interior", src), radius=1.5)
    assert fl.readings == 4, fl.readings
    try:
        sheetmetal.analyse(bodies[0], bad, radius=1.5)
        raise AssertionError("drew 811101 from a DXF whose flat isn't symmetric, with nothing to pin it")
    except ValueError as e:
        assert "nothing pins which way up its DXF is drawn" in str(e), e
    b2, _u = geom.load_part(compose.find_step("511202", "wall"), "511202")
    try:
        sheetmetal.analyse(b2[0], [os.path.join(readback.REPO, "v2", "03-Manufacturing", "wall", f)
                                   for f in os.listdir(os.path.join(readback.REPO, "v2", "03-Manufacturing", "wall"))
                                   if f.startswith("511202_") and f.endswith("_DXF.dxf")][0])
        raise AssertionError("drew 511202 with cut-outs the flat's check doesn't read")
    except ValueError as e:
        assert "2 cut-outs that aren't round holes (80 x 11, 304 x 268)" in str(e), e


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


def test_section_letter_keeps_clear_of_lines():
    """WALL's L1 frame (#343, its studs): a removed section's letter at its usual place by the arrow sat on a stud's
    outline. A cutting plane across a rail, with a stud standing where the upper letter would go: the letter takes
    the first clear place by its arrow, and the read-back finds no clash (the usual place had the stud through it)."""
    from sheet import Sheet
    d = os.path.join(TMP, "letter")
    os.makedirs(d, exist_ok=True)
    sh = Sheet("A3")
    sh.line((100, 100), (240, 100), 0.5)                 # the rail
    sh.line((100, 104), (240, 104), 0.5)
    sh.line((190.5, 104), (190.5, 160), 0.5)             # the stud, through the letter's usual place
    sh.line((194.5, 104), (194.5, 160), 0.5)
    usual = sh.text_box(193.0 - 1.5, 116.0 + 1.0, "E", 3.5, "center", bold=True)
    assert not sh.is_free(usual)
    sh.section_arrows((200.0, 96.0), (200.0, 116.0), "E", (-1.0, 0.0), size=3.5)
    sh.save(os.path.join(d, "e.pdf"))
    doc = fitz.open(os.path.join(d, "e.pdf"))
    found = [w for _p, w in readback.clashes(doc)]
    assert not found, found
    es = [w for w in doc[0].get_text("words") if w[4] == "E"]
    assert len(es) == 2, es


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
