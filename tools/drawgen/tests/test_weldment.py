#!/usr/bin/env python3
"""Tests of drawgen's two weldment hooks (D-120, D-162), agreed with the generator's owner. Run in drawgen's own
environment:

    <venv>/bin/python tools/drawgen/tests/test_weldment.py          # prints "N of N passed"
    <venv>/bin/python -m pytest -q tools/drawgen/tests/test_weldment.py

1. A frame with no body of its own (its members are parts under it, D-120) takes every solid under its first
   placement, each body named by its member's number and name; its quantity is its own placements' count. Its STEP
   is found through its members, and the read-back's holes and faces come from the same set. A frame in its own file
   whose every body is a member part (WALL's 211101) reads the same way. Each hole takes its own member's register
   row first, then the frame's own, never another member's.
2. An entry can name a cut list file in its team's folder (D-162): its rows for the frame, one per member number
   with the quantity summed. Balloons match bodies by member number, and each number's bodies must equal its
   quantity, both ways. A number with two lengths or two ends texts is refused, and so is a bought part under the
   frame. Welded-in made parts the entry names (mitre plates) come from their parts-list rows, as having their own
   drawing.
3. The cut list prints each row's ends as written, and shortens them to 'square-cut ends' only when the text says
   square and gives no angle: 'mitred 63.43 deg off square' keeps its angle.
4. The cut list is the members' drawing, so it must be the model's: a member whose cut length (0.05 mm) or end
   angles (0.05°) differ from its body is refused, and the read-back reads the printed cut list against the file,
   so a length edited into the sheet fails it (Reviewer 9 on #365).
5. On CEILING's own frames C1 and C2 (411101, 411102: D-131 welded steel, #348), once their members and their tube
   cut list are on this tree: both draw and read back, with the members and the mitre plates in the cut list.
"""

import csv
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import fitz  # noqa: E402

import compose  # noqa: E402
import geom  # noqa: E402
import inputs  # noqa: E402
import readback  # noqa: E402
from compose import NotDrawable  # noqa: E402

TMP = tempfile.mkdtemp(prefix="drawgen-weld-test-")
ROW = {"part_number": "219980", "name": "TEST - WELDED FRAME", "name_vi": "", "material": "steel tube, welded",
       "finish": "zinc", "process": "cut, welded in a jig", "size_mm": "300 x 220 x 20", "tolerance": "+-0.5",
       "qty": "1", "mass_each_kg": "1.0"}
SPEC = {"tolerance": "test", "notes": ["FRAME: test weldment."]}


def _holes(sh, centres):
    """Ø8.5 holes through the top wall (Z 18.5 to 20) at these (x, y)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    for x, y in centres:
        c = BRepAlgoAPI_Cut(sh, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, 15.0), gp_Dir(0, 0, 1)), 4.25, 10).Shape())
        c.Build()
        sh = c.Shape()
    return sh


def _tube(x0, y0, length, along_x, mitre=0.0):
    """A 20 x 20 x 1.5 box tube, length along X (or Y), from (x0, y0, 0); mitre: both ends cut that many degrees from
    square in plan (the long points on its -Y face), as a frame's corner members are."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
    from OCP.gp import gp_Pnt, gp_Vec

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()

    def wedge(pts):
        poly = BRepBuilderAPI_MakePolygon()
        for q in pts:
            poly.Add(gp_Pnt(q[0], q[1], -1))
        poly.Close()
        return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(0, 0, 22)).Shape()
    if along_x:
        sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, 0), length, 20, 20).Shape(),
                 BRepPrimAPI_MakeBox(gp_Pnt(x0 - 1, y0 + 1.5, 1.5), length + 2, 17, 17).Shape())
        if mitre:
            k = 20.0 * math.tan(math.radians(mitre))
            sh = cut(sh, wedge([(x0 - 1, y0 + 20), (x0 + k, y0 + 20), (x0, y0), (x0 - 1, y0)]))
            sh = cut(sh, wedge([(x0 + length + 1, y0 + 20), (x0 + length - k, y0 + 20), (x0 + length, y0),
                                (x0 + length + 1, y0)]))
    else:
        sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, 0), 20, length, 20).Shape(),
                 BRepPrimAPI_MakeBox(gp_Pnt(x0 + 1.5, y0 - 1, 1.5), 17, length + 2, 17).Shape())
    return sh


def _weldment(path, bought=False, own=False, holes=False):
    """A test assembly '219970 TEST ASSY' holding the frame '219980 TEST FRAME' (no body of its own) at 0,0,0, as a
    team STEP holds CEILING's 411101: two long members 219981 (300, both ends mitred 45° in plan), two short ones
    219982
    (180, between them), and one plate 219983 (a 2 mm plate on the corner), each a part named by its number. With
    bought, a bought part 219984 sits under the frame too. Each placement is named as Fusion names them ('NAME:1'), so
    the repo's own STEP reader sees the tree as it sees Fusion's files."""
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.STEPControl import STEPControl_AsIs
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from OCP.gp import gp_Pnt

    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    def name(lab, s):
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(s))

    if own:                 # the frame in its own file, its top product the document (as Fusion writes WALL's 211101)
        frame = st.NewShape()
        name(frame, "219980_P01_TEST-FRAME_CAD")
    else:
        top = st.NewShape()
        name(top, "219970 TEST ASSY")
        frame = st.NewShape()
        name(frame, "219980 TEST FRAME")
    # no holes here: the repo's STEP reader reads Fusion's hole faces, not the ones OCC writes; the after-weld holes
    # are read back on CEILING's own frames below
    long_a = _tube(0, 0, 300, True, mitre=45.0)
    if holes:               # two after-weld holes in one long member (the register test: OCC finds them)
        long_a = _holes(long_a, [(100, 10), (200, 10)])
    parts = [("219981 TEST MEMBER LONG", long_a),
             ("219981 TEST MEMBER LONG", _tube(0, 200, 300, True, mitre=45.0)),
             ("219982 TEST MEMBER SHORT", _tube(0, 20, 180, False)),
             ("219982 TEST MEMBER SHORT", _tube(280, 20, 180, False)),
             ("219983 TEST PLATE", BRepPrimAPI_MakeBox(gp_Pnt(-2, -2, 0), 2, 24, 20).Shape())]
    if bought:
        parts.append(("219984 TEST RIVNUT", BRepPrimAPI_MakeBox(gp_Pnt(146, 6, 20), 8, 8, 2).Shape()))
    count = {}
    for nm, sh in parts:
        lab = st.AddShape(sh, False)
        name(lab, nm)
        count[nm] = count.get(nm, 0) + 1
        name(st.AddComponent(frame, lab, TopLoc_Location()), "%s:%d" % (nm, count[nm]))   # as Fusion names them
    if not own:
        name(st.AddComponent(top, frame, TopLoc_Location()), "219980 TEST FRAME:1")
    st.UpdateAssemblies()
    w = STEPCAFControl_Writer()
    w.SetNameMode(True)
    w.Transfer(doc, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone
    return path


def _cut_list(path, rows):
    """A team cut list in the columns CEILING, WALL and FRONT share."""
    cols = ["frame", "member", "member_part", "name", "section", "length_mm", "qty", "ends", "holes", "status"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        for r in rows:
            w.writerow(dict({c: "" for c in cols}, **r))
    return path


GOOD = [
    {"frame": "219980", "member": "LONG A", "member_part": "219981", "name": "TEST MEMBER LONG",
     "section": "steel tube 20 x 20 x 1.5", "length_mm": "300", "qty": "1",
     "ends": "both ends mitred 45 deg off square, long points on its outer face"},
    {"frame": "219980", "member": "LONG B", "member_part": "219981", "name": "TEST MEMBER LONG",
     "section": "steel tube 20 x 20 x 1.5", "length_mm": "300", "qty": "1",
     "ends": "both ends mitred 45 deg off square, long points on its outer face"},
    {"frame": "219980", "member": "SHORT", "member_part": "219982", "name": "TEST MEMBER SHORT",
     "section": "steel tube 20 x 20 x 1.5", "length_mm": "180", "qty": "2", "ends": "square ends"},
    {"frame": "219980", "member": "OTHER", "member_part": "219999", "name": "ANOTHER FRAME'S ROW",
     "section": "-", "length_mm": "1", "qty": "1", "ends": "square cut"},
]
for _r in GOOD[-1:]:
    _r["frame"] = "219999"
PLATE_ROW = {"part_number": "219983", "name": "TEST PLATE", "kind": "MP", "material": "steel plate 2",
             "qty_per_parent": "1"}


class _Rows:
    """Parts-list rows the test's own parts need (the plate welded in, a bought part), the team's lists otherwise."""

    def __init__(self, more):
        self.more, self.real = more, inputs.parts_row

    def __enter__(self):
        inputs.parts_row = lambda pn, team: ((self.more[pn], [], None) if pn in self.more else self.real(pn, team))

    def __exit__(self, *a):
        inputs.parts_row = self.real


def _made(tag, rows=GOOD, bought=False, welded_in=("219983",)):
    d = os.path.join(TMP, tag)
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219970_P01_TEST-ASSY_STEP.step"), bought=bought)
    spec = dict(SPEC, cut_list={"file": _cut_list(os.path.join(d, "cut.csv"), rows), "welded_in": list(welded_in)})
    return d, step, spec


def _refused(tag, want, rows=GOOD, **kw):
    d, step, spec = _made(tag, rows, **kw)
    with _Rows({"219983": PLATE_ROW}):
        try:
            compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
        except NotDrawable as e:
            assert want in str(e), (want, str(e))
            return
    raise AssertionError("drawn, though: %s" % want)


def test_a_frame_takes_its_members_bodies():
    d, step, _spec = _made("load")
    bodies, unit = geom.load_part(step, "219980")
    names = sorted(b.name for b in bodies)
    assert names == ["219981 TEST MEMBER LONG"] * 2 + ["219982 TEST MEMBER SHORT"] * 2 + ["219983 TEST PLATE"], names
    assert unit["occurrences"] == 1 and unit.get("members") is True, unit
    # an ordinary part keeps its data as it was: no members flag
    _b, u2 = geom.load_part(step, "219981")
    assert "members" not in u2, u2


def test_a_frame_in_its_own_file_takes_its_members_bodies():
    """WALL's 211101 in its own STEP: its top product is the document and every body is a member part, so it reads
    as a frame of members, as from a team STEP; an ordinary part in its own file keeps its bodies as before."""
    d = os.path.join(TMP, "own")
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219980_P01_TEST-FRAME_STEP.step"), own=True)
    bodies, unit = geom.load_part(step, "219980")
    assert sorted(b.name for b in bodies)[:2] == ["219981 TEST MEMBER LONG"] * 2 and unit.get("members"), unit
    spec = dict(SPEC, cut_list={"file": _cut_list(os.path.join(d, "cut.csv"), GOOD), "welded_in": ["219983"]})
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails


def test_a_hole_takes_its_own_members_row_then_the_frames():
    """A frame of members' hole is matched in its own member's register rows first (CEILING lists them so), then in
    the frame's own rows (WALL lists its after-weld holes there), never in another member's rows (the Lead's rule on
    #365): a row of another member that fits the hole exactly is never taken."""
    d = os.path.join(TMP, "reg")
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219970_P01_TEST-ASSY_STEP.step"), holes=True)
    row = lambda i, body: {"id": i, "body": body, "dia": 8.5, "axis": "Z", "function": i, "mating": "", "tolerance": "",
                           "status": "", "file": "test"}
    regs = {"219982": [dict(row("F-OTHER", "TEST MEMBER SHORT"), centres=[(100.0, 10.0), (200.0, 10.0)])],
            "219981": [dict(row("F-MEMBER", "TEST MEMBER LONG"), centres=[(100.0, 10.0)])],
            "219980": [dict(row("F-FRAME", "RAIL"), centres=[(200.0, 10.0)])]}
    real = inputs.feature_rows
    inputs.feature_rows = lambda pn, team: regs.get(pn, [])
    try:
        part = compose.Part("219980", "none", step=step, row=ROW)
    finally:
        inputs.feature_rows = real
    got = sorted((round(ft.f.entry[0]), (ft.reg or {}).get("id")) for ft in part.features if ft.kind == "hole")
    assert got == [(100, "F-MEMBER"), (200, "F-FRAME")], got


def test_a_frame_draws_and_reads_back_with_its_cut_list():
    d, step, spec = _made("draw")
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails
    text = " ".join(" ".join(pg.get_text() for pg in fitz.open(p)).split())
    assert "CUT LIST (cut list cut.csv)" in text, text[:400]
    assert "219981 TEST MEMBER LONG" in text and "219982 TEST MEMBER SHORT" in text and "219983 TEST PLATE" in text
    # the ends as written where they give an angle; 'square-cut ends' for the plain square ends only; the plate is
    # defined by its parts-list row (D-125)
    assert "both ends mitred 45 deg off square" in text, text
    assert text.count("square-cut ends") == 1, text.count("square-cut ends")
    assert "no drawing of its own, its parts-list row defines it (D-125)" in text
    assert "ANOTHER FRAME" not in text


def test_counts_both_ways_and_one_number_one_member():
    rows = [dict(r) for r in GOOD]
    rows[2]["qty"] = "1"                        # the cut list says 1 short member, the frame holds 2
    _refused("count1", "219982 has 2 bodies under the frame, its cut list 1", rows)
    rows = [dict(r) for r in GOOD]
    rows[1]["length_mm"] = "301"                # one number, two lengths (D-120)
    _refused("count2", "219981 has two lengths or two ends texts", rows)
    _refused("count3", "219983 has 1 bodies under the frame, its cut list 0", welded_in=())   # the plate not named


def test_the_cut_list_is_checked_against_the_model():
    """Reviewer 9 on #365: the cut list is the members' drawing (D-162), so a length or an end angle that differs
    from the member's body is refused, and a length edited into the sheet fails the read-back."""
    rows = [dict(r) for r in GOOD]
    for r in rows[:2]:
        r["length_mm"] = "303"
    _refused("model1", "member 219981: its cut list says 303 long, its body is 300.00", rows)
    rows = [dict(r) for r in GOOD]
    for r in rows[:2]:
        r["ends"] = "both ends mitred 30 deg off square"
    _refused("model2", "its cut list's ends give 30°, 30°, its body's end cuts 45.00°, 45.00° from square", rows)
    rows = [dict(r) for r in GOOD]
    rows[2]["ends"] = "both ends mitred 45 deg"
    _refused("model3", "its cut list's ends give 45°, 45°, its body's end cuts 0.00°, 0.00° from square", rows)
    # a length edited into a copy of the sheet
    d, step, spec = _made("edit")
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        data = readback.read_data(fitz.open(p))
        doc = fitz.open(p)
        page = doc[data["cut_list"]["page"]]
        hit = [w for w in page.get_text("words") if w[4] == "180"]
        assert hit, "no 180 in the cut list"
        r = fitz.Rect(hit[0][:4])
        page.add_redact_annot(r)
        page.apply_redactions()
        page.insert_text((r.x0, r.y1 - 1), "181", fontsize=r.height * 0.8)
        bad = os.path.join(d, "edited.pdf")
        doc.save(bad)
        fails, _st = readback.check(bad, step)
    assert any("CUT LENGTH: '181' where cut.csv gives '180'" in f for f in fails), fails


def test_a_bought_part_under_the_frame_is_refused():
    d, step, spec = _made("bought", bought=True)
    with _Rows({"219983": PLATE_ROW, "219984": {"part_number": "219984", "kind": "PI", "name": "TEST RIVNUT"}}):
        try:
            compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
            raise AssertionError("a bought part under the frame was drawn as frame material")
        except NotDrawable as e:
            assert "219984" in str(e) and "bought part" in str(e), e


def test_ceilings_frames_when_they_are_on_this_tree():
    """CEILING's C1 and C2 frames (#348) with their tube cut list and the mitre plates welded in: they draw and read
    back. Until #348's members and cut list are on this tree, this says so and passes."""
    cl = os.path.join(inputs.MANUF, "ceiling", "410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv")
    with open(cl, newline="", encoding="utf-8") as fh:
        head = next(csv.reader(fh))
    if "member_part" not in head:
        print("  (CEILING's steel frames aren't on this tree yet: skipped)")
        return
    spec = {"corner": "-X-Y-Z", "tolerance": "test",
            "cut_list": {"file": "410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv", "welded_in": ["831007", "831008"]},
            "notes": ["FRAME: welded, galvanized steel tube (D-131, J-FRAME-01)."]}
    for pn, n in (("411101", 21), ("411102", 25)):
        p = os.path.join(TMP, pn + ".pdf")
        compose.make(pn, "ceiling", spec, p)
        step = compose.find_step(pn, "ceiling")
        fails, st = readback.check(p, step)
        assert not fails, (pn, fails)
        text = " ".join(" ".join(pg.get_text() for pg in fitz.open(p)).split())
        assert "831007" in text and "831008" in text and "412101" in text, pn
        assert "its parts-list row defines it (D-125)" in text, pn


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
