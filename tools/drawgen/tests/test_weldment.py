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
6. FRONT's cut lists (#313): with the two end angle columns, the model check reads the angles from them (each end's
   steepest cut), an ends text that gives both angles must agree with them, and each member prints its parts-list
   name rather than the tube's place.
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


def _tube(x0, y0, length, along_x, mitre=0.0, flip_b=False):
    """A 20 x 20 x 1.5 box tube, length along X (or Y), from (x0, y0, 0); mitre: both ends cut that many degrees from
    square in plan (the long points on its -Y face), as a frame's corner members are. flip_b: the far end's long
    point on the +Y face instead, so the two cuts are parallel planes (FRONT's lean 'parallel')."""
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
            far = [(x0 + length + 1, y0 + 20), (x0 + length - k, y0 + 20), (x0 + length, y0), (x0 + length + 1, y0)]
            if flip_b:
                far = [(x0 + length + 1, y0), (x0 + length - k, y0), (x0 + length, y0 + 20), (x0 + length + 1, y0 + 20)]
            sh = cut(sh, wedge(far))
    else:
        sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, 0), 20, length, 20).Shape(),
                 BRepPrimAPI_MakeBox(gp_Pnt(x0 + 1.5, y0 - 1, 1.5), 17, length + 2, 17).Shape())
    return sh


def _weldment(path, bought=False, own=False, holes=False, two_cut=False, parallel=False):
    """A test assembly '219970 TEST ASSY' holding the frame '219980 TEST FRAME' (no body of its own) at 0,0,0, as a
    team STEP holds CEILING's 411101: two long members 219981 (300, both ends mitred 45° in plan), two short ones
    219982
    (180, between them), and one plate 219983 (a 2 mm plate on the corner), each a part named by its number. With
    bought, a bought part 219984 sits under the frame too. With two_cut, the long members' right ends have two cuts,
    as FRONT's 352207 has: the 45° mitre and its long point cut square 2 mm back, so they are 298 long. With parallel,
    their right ends' long points are on the +Y face, so each long member's two cuts are parallel. Each placement
    is named as Fusion names them ('NAME:1'), so the repo's own STEP reader sees the tree as it sees Fusion's
    files."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
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
    long_a = _tube(0, 0, 300, True, mitre=45.0, flip_b=parallel)
    if holes:               # two after-weld holes in one long member (the register test: OCC finds them)
        long_a = _holes(long_a, [(100, 10), (200, 10)])
    long_b = _tube(0, 200, 300, True, mitre=45.0, flip_b=parallel)
    if two_cut:             # the long point at the right end cut square 2 mm back: a second cut at that end

        def tip(sh, y0):
            c = BRepAlgoAPI_Cut(sh, BRepPrimAPI_MakeBox(gp_Pnt(298, y0 - 1, -1), 10, 22, 22).Shape())
            c.Build()
            return c.Shape()
        long_a, long_b = tip(long_a, 0), tip(long_b, 200)
    parts = [("219981 TEST MEMBER LONG", long_a),
             ("219981 TEST MEMBER LONG", long_b),
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
    """A team cut list in the columns CEILING, WALL and FRONT share, plus any other column the rows give (FRONT's
    end_a_deg and end_b_deg)."""
    cols = ["frame", "member", "member_part", "name", "section", "length_mm", "qty", "ends", "holes", "status"]
    cols += [k for r in rows for k in r if k not in cols]
    cols = list(dict.fromkeys(cols))
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


def _made(tag, rows=GOOD, bought=False, welded_in=("219983",), two_cut=False, parallel=False):
    d = os.path.join(TMP, tag)
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219970_P01_TEST-ASSY_STEP.step"), bought=bought, two_cut=two_cut,
                     parallel=parallel)
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
    """WALL's 211101 in its own STEP: its top product is the document and every body is a member part, so once its
    entry names a cut list it reads as a frame of members, as from a team STEP; until then it reads as before."""
    d = os.path.join(TMP, "own")
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219980_P01_TEST-FRAME_STEP.step"), own=True)
    bodies, unit = geom.load_part(step, "219980", frame_members=True)
    assert sorted(b.name for b in bodies)[:2] == ["219981 TEST MEMBER LONG"] * 2 and unit.get("members"), unit
    # without a cut list in its entry, the own file reads as it always did (WALL's L1 sheet stays as main draws it
    # until WALL names its cut list: Reviewer 9 on #365)
    bodies, unit = geom.load_part(step, "219980")
    assert not unit.get("members") and all(b.name == "" or not b.name.startswith("2199") for b in bodies), unit
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


def _front_rows():
    """GOOD as FRONT writes its cut lists, for the frame with two cuts at the long members' right ends (two_cut):
    each row names the tube's place, and the end angles are in two columns as well as the text. The long members'
    text has two cuts at one end (its 45° mitre and a square one) and a tolerance note ('to within 0.1 deg'), so it
    gives no pair the text reader can use; one number keeps one text and one pair of angles (D-120)."""
    rows = [dict(r) for r in GOOD]
    two_cuts = ("left end (A) 45.0°; right end (B) two cuts, 45.0° and square (0°) (its own sheet); flat on the "
                "posts (to within 0.1 deg)")
    rows[0].update(name="LONG MEMBER AT THE FRONT", end_a_deg="45.0", end_b_deg="45.0 and 0.0 (two cuts)",
                   ends=two_cuts, length_mm="298")
    rows[1].update(name="LONG MEMBER AT THE BACK", end_a_deg="45.0", end_b_deg="45.0 and 0.0 (two cuts)",
                   ends=two_cuts, length_mm="298")
    rows[2].update(name="SHORT MEMBER", end_a_deg="0.0", end_b_deg="0.0", ends="square both ends, between the rails")
    return rows


LISTED = {"219981": {"part_number": "219981", "kind": "MP", "name": "TEST - FRAME - MEMBER LONG"},
          "219982": {"part_number": "219982", "kind": "MP", "name": "TEST - FRAME - MEMBER SHORT"}}


def test_front_angle_columns_and_parts_list_names():
    """FRONT's cut lists (#313, for its D-131 frames): the model check reads each row's end angles from its two angle
    columns, because a text with two cuts at one end or a tolerance note gives no pair. At a two-cut end both cuts
    are checked (the generator's owner on #404): the steepest against the body's steepest there, and the angles
    against that end's cut faces, both ways. The sheet prints each end from the checked columns, not the text (the
    Lead's ruling on #424), and each member its parts-list name, not the tube's place (the Lead's ruling,
    2026-11-01)."""
    rows = _front_rows()
    d, step, spec = _made("front", rows, two_cut=True)
    p = os.path.join(d, "frame.pdf")
    with _Rows(dict(LISTED, **{"219983": PLATE_ROW})):
        got, _p = inputs.cut_list_rows("none", spec["cut_list"], "219980")
        assert [r.get("angles") for r in got[:2]] == [[45.0, 45.0], [0.0, 0.0]], got
        assert got[0]["cuts"] == [[45.0], [0.0, 45.0]], got[0]
        assert [r["name"] for r in got[:2]] == ["219981 TEST - FRAME - MEMBER LONG",
                                                "219982 TEST - FRAME - MEMBER SHORT"], got
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails
    text = " ".join(" ".join(pg.get_text() for pg in fitz.open(p)).split())
    assert "219981 TEST - FRAME - MEMBER LONG" in text and "219982 TEST - FRAME - MEMBER SHORT" in text, text[:600]
    assert "LONG MEMBER AT THE" not in text and "SHORT MEMBER" not in text
    assert "left end (A) 45.0°; right end (B) two cuts, 45.0° and square" in text    # from the checked columns
    # a member with no parts-list row keeps the cut list's own name
    with _Rows({"219983": PLATE_ROW}):
        got, _p = inputs.cut_list_rows("none", spec["cut_list"], "219980")
    assert got[0]["name"] == "219981 LONG MEMBER AT THE FRONT", got[0]["name"]
    # the columns are checked against the model: an angle a degree off is refused
    body = "its body's end cuts there 45.00° and at its other end 0.00° and 45.00° from square"
    rows = _front_rows()
    for r in rows[:2]:
        r["end_a_deg"] = "44.0"
    _refused("front1", "its cut list gives end A (its left end) 44° and end B 0° and 45°, " + body, rows,
             two_cut=True)
    # a two-cut end's steepest is the body's steepest there: a 30° cut can't stand in for the 45° mitre
    rows = _front_rows()
    for r in rows[:2]:
        r["end_b_deg"] = "30.0 and 0.0 (two cuts)"
    _refused("front2", "its cut list gives end A (its left end) 45° and end B 0° and 30°, " + body, rows,
             two_cut=True)
    # and its other cut is checked too: a 10° second cut the body doesn't have is refused
    rows = _front_rows()
    for r in rows[:2]:
        r["end_b_deg"] = "45.0 and 10.0 (two cuts)"
    _refused("front6", "its cut list gives end A (its left end) 45° and end B 10° and 45°, " + body, rows,
             two_cut=True)
    # both ways: an end the list gives one cut where the body has two is refused
    rows = _front_rows()
    for r in rows[:2]:
        r["end_b_deg"] = "45.0"
    _refused("front7", "its cut list gives end A (its left end) 45° and end B 45°, " + body, rows, two_cut=True)
    # the short members' columns say 45°, their bodies are square: refused, whatever the text says
    rows = _front_rows()
    rows[2]["end_b_deg"] = "45.0"
    _refused("front3", "member 219982: its cut list gives its two ends different cuts, but its ends text doesn't say "
             "which end is A", rows, two_cut=True)
    # a row whose columns give one end only
    rows = _front_rows()
    rows[2]["end_b_deg"] = "square"
    _refused("front4", "member 219982's end angle columns '0.0' and 'square' don't give a number each", rows,
             two_cut=True)
    # one number, two pairs of angles (D-120)
    rows = _front_rows()
    rows[1]["end_a_deg"] = "46.0"
    _refused("front5", "member 219981 has two lengths or two ends texts or two pairs of end angles", rows,
             two_cut=True)


def test_the_sheet_prints_the_ends_from_the_checked_columns():
    """Reviewer 6 on #424, the Lead's ruling: under D-162 the printed ends are the member's drawing, so they come from
    the checked columns, never the list's own text. Here the text contradicts the columns twice (other angles, and
    the lean the other way), and the sheet still prints the columns' values, which the model check passed; the row's
    note, free words the check doesn't read, follows in brackets."""
    rows = _front_rows()
    for r in rows[:2]:
        r.update(lean="opposite", note="mitred to its neighbours",
                 ends="left end (A) 30.0°; right end (B) 60.0°; the cuts lean the same way (parallel)")
    d, step, spec = _made("printed", rows, two_cut=True)
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails
    text = " ".join(" ".join(pg.get_text() for pg in fitz.open(p)).split())
    want = ("left end (A) 45.0°; right end (B) two cuts, 45.0° and square; the cuts lean apart (opposite) "
            "(note: mitred to its neighbours)")
    assert want in text, text
    assert "30.0°" not in text and "60.0°" not in text and "the same way" not in text, text


def _lean_rows(lean):
    """GOOD as FRONT writes it for the frame with one 45° cut at each end of the long members: end A named (the left
    one), the angle columns and the lean column."""
    rows = [dict(r) for r in GOOD]
    for r in rows[:2]:
        r.update(end_a_deg="45.0", end_b_deg="45.0", lean=lean,
                 ends="left end (A) 45.0°; right end (B) 45.0°; the cuts %s" % (
                     "lean apart (opposite)" if lean == "opposite" else "are parallel"))
    rows[2].update(end_a_deg="0.0", end_b_deg="0.0", lean="square", ends="square both ends, between the rails")
    return rows


def test_front_end_a_and_the_lean_are_the_models():
    """Reviewer 6 on #404, the Lead's ruling: under D-162 the cut list row is the member's drawing, so its end A and
    its lean are checked against the model too. End A is the end its ends text names, in pod axes (left -X, right
    +X, front -Y, back +Y, lower -Z, upper +Z: FRONT's cut lists, checked on all 63 of #313's members); its cuts must
    be that end's. A row whose two ends differ must say which end is A. The lean: 'opposite' (the cuts lean apart)
    is two mirror-image cuts, whose tilts point the same way; 'parallel' is two parallel cut planes."""
    # end A and end B swapped: the left end has the plain 45° mitre, the right end the two cuts
    rows = _front_rows()
    for r in rows[:2]:
        r["end_a_deg"], r["end_b_deg"] = "45.0 and 0.0 (two cuts)", "45.0"
    _refused("order1", "its cut list gives end A (its left end) 0° and 45° and end B 45°, its body's end cuts there "
             "45.00° and at its other end 0.00° and 45.00° from square", rows, two_cut=True)
    # two different ends, and a text that doesn't name end A
    rows = _front_rows()
    for r in rows[:2]:
        r["ends"] = "two cuts at one end: 45.0° and square (0°); a 45.0° mitre at the other"
    _refused("order2", "its cut list gives its two ends different cuts, but its ends text doesn't say which end is A",
             rows, two_cut=True)
    # the lean: the long members' cuts are mirror images (long points on one face), so 'opposite' draws and reads
    # back, and 'parallel' is refused
    d, step, spec = _made("lean1", _lean_rows("opposite"))
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails
    _refused("lean2", "its cut list says its end cuts lean parallel ('parallel'), its body's lean apart (mirror "
             "images: 'opposite')", _lean_rows("parallel"))
    # and the other way: parallel cuts (long points on opposite faces) draw as 'parallel', 'opposite' is refused
    d, step, spec = _made("lean3", _lean_rows("parallel"), parallel=True)
    p = os.path.join(d, "frame.pdf")
    with _Rows({"219983": PLATE_ROW}):
        compose.make("219980", "none", spec, p, step=step, row=ROW)
        fails, _st = readback.check(p, step)
    assert not fails, fails
    _refused("lean4", "its cut list says its end cuts lean apart (mirror images: 'opposite'), its body's lean "
             "parallel ('parallel')", _lean_rows("opposite"), parallel=True)
    # one number, two leans (D-120)
    rows = _lean_rows("opposite")
    rows[1]["lean"] = "parallel"
    _refused("lean5", "member 219981 has two lengths or two ends texts or two pairs of end angles or two leans", rows)


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
