#!/usr/bin/env python3
"""Tests of drawgen's two weldment hooks (D-120, D-162), agreed with the generator's owner. Run in drawgen's own
environment:

    <venv>/bin/python tools/drawgen/tests/test_weldment.py          # prints "N of N passed"
    <venv>/bin/python -m pytest -q tools/drawgen/tests/test_weldment.py

1. A frame with no body of its own (its members are parts under it, D-120) takes every solid under its first
   placement, each body named by its member's number and name; its quantity is its own placements' count. Its STEP
   is found through its members, and the read-back's holes and faces come from the same set.
2. An entry can name a cut list file in its team's folder (D-162): its rows for the frame, one per member number
   with the quantity summed. Balloons match bodies by member number, and each number's bodies must equal its
   quantity, both ways. A number with two lengths or two ends texts is refused, and so is a bought part under the
   frame. Welded-in made parts the entry names (mitre plates) come from their parts-list rows, as having their own
   drawing.
3. The cut list prints each row's ends as written, and shortens them to 'square-cut ends' only when the text says
   square and gives no angle: 'mitred 63.43 deg off square' keeps its angle.
4. On CEILING's own frames C1 and C2 (411101, 411102: D-131 welded steel, #348), once their members and their tube
   cut list are on this tree: both draw and read back, with the members and the mitre plates in the cut list.
"""

import csv
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


def _tube(x0, y0, length, along_x, holes=()):
    """A 20 x 20 x 1.5 box tube, length along X (or Y), from (x0, y0, 0); holes: Ø8.5 through its top wall at these
    distances from its start."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()
    if along_x:
        sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, 0), length, 20, 20).Shape(),
                 BRepPrimAPI_MakeBox(gp_Pnt(x0 - 1, y0 + 1.5, 1.5), length + 2, 17, 17).Shape())
    else:
        sh = cut(BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, 0), 20, length, 20).Shape(),
                 BRepPrimAPI_MakeBox(gp_Pnt(x0 + 1.5, y0 - 1, 1.5), 17, length + 2, 17).Shape())
    for d in holes:
        c = (x0 + d, y0 + 10) if along_x else (x0 + 10, y0 + d)
        sh = cut(sh, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(c[0], c[1], 15.0), gp_Dir(0, 0, 1)), 4.25, 10).Shape())
    return sh


def _weldment(path, bought=False):
    """A test assembly '219970 TEST ASSY' holding the frame '219980 TEST FRAME' (no body of its own) at 0,0,0, as a
    team STEP holds CEILING's 411101: two long members 219981 (300), two short ones 219982
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

    top = st.NewShape()
    name(top, "219970 TEST ASSY")
    frame = st.NewShape()
    name(frame, "219980 TEST FRAME")
    # no holes here: the repo's STEP reader reads Fusion's hole faces, not the ones OCC writes; the after-weld holes
    # are read back on CEILING's own frames below
    parts = [("219981 TEST MEMBER LONG", _tube(0, 0, 300, True)),
             ("219981 TEST MEMBER LONG", _tube(0, 200, 300, True)),
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
     "ends": "front end mitred 45.00° and back end 63.43° off square"},
    {"frame": "219980", "member": "LONG B", "member_part": "219981", "name": "TEST MEMBER LONG",
     "section": "steel tube 20 x 20 x 1.5", "length_mm": "300", "qty": "1",
     "ends": "front end mitred 45.00° and back end 63.43° off square"},
    {"frame": "219980", "member": "SHORT", "member_part": "219982", "name": "TEST MEMBER SHORT",
     "section": "steel tube 20 x 20 x 1.5", "length_mm": "180", "qty": "2", "ends": "square ends"},
    {"frame": "219980", "member": "PLATE", "member_part": "219983", "name": "TEST PLATE",
     "section": "steel plate 2", "length_mm": "24", "qty": "1", "ends": "both ends mitred 26.57 deg off square"},
    {"frame": "219999", "member": "OTHER", "member_part": "219999", "name": "ANOTHER FRAME'S ROW",
     "section": "-", "length_mm": "1", "qty": "1", "ends": "square cut"},
]


def _made(tag, rows=GOOD, bought=False):
    d = os.path.join(TMP, tag)
    os.makedirs(d, exist_ok=True)
    step = _weldment(os.path.join(d, "219970_P01_TEST-ASSY_STEP.step"), bought=bought)
    spec = dict(SPEC, cut_list={"file": _cut_list(os.path.join(d, "cut.csv"), rows)})
    return d, step, spec


def test_a_frame_takes_its_members_bodies():
    d, step, _spec = _made("load")
    bodies, unit = geom.load_part(step, "219980")
    names = sorted(b.name for b in bodies)
    assert names == ["219981 TEST MEMBER LONG"] * 2 + ["219982 TEST MEMBER SHORT"] * 2 + ["219983 TEST PLATE"], names
    assert unit["occurrences"] == 1 and unit.get("members") is True, unit
    # an ordinary part keeps its data as it was: no members flag
    _b, u2 = geom.load_part(step, "219981")
    assert "members" not in u2, u2


def test_a_frame_draws_and_reads_back_with_its_cut_list():
    d, step, spec = _made("draw")
    p = os.path.join(d, "frame.pdf")
    compose.make("219980", "none", spec, p, step=step, row=ROW)
    fails, st = readback.check(p, step)
    assert not fails, fails
    text = " ".join(" ".join(pg.get_text() for pg in fitz.open(p)).split())
    assert "CUT LIST (cut list cut.csv)" in text, text[:400]
    assert "219981 TEST MEMBER LONG" in text and "219982 TEST MEMBER SHORT" in text and "219983 TEST PLATE" in text
    # the ends as written where they give an angle; 'square-cut ends' for the plain square ends only
    assert "63.43° off square" in text and "26.57 deg off square" in text, text
    assert text.count("square-cut ends") == 1, text.count("square-cut ends")
    assert "ANOTHER FRAME" not in text


def test_counts_both_ways_and_one_number_one_member():
    _d, step, _s = _made("counts")
    rows = [dict(r) for r in GOOD]
    rows[2]["qty"] = "1"                        # the cut list says 1 short member, the frame holds 2
    d, step, spec = _made("count1", rows)
    try:
        compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
        raise AssertionError("a member count off by one was drawn")
    except NotDrawable as e:
        assert "219982 has 2 bodies under the frame, its cut list 1" in str(e), e
    rows = [dict(r) for r in GOOD]
    rows[1]["length_mm"] = "301"                # one number, two lengths (D-120)
    d, step, spec = _made("count2", rows)
    try:
        compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
        raise AssertionError("one number with two lengths was drawn")
    except NotDrawable as e:
        assert "219981 has two lengths or two ends texts" in str(e), e
    rows = [r for r in GOOD if r["member_part"] != "219983"]      # a body whose number the cut list lacks
    d, step, spec = _made("count3", rows)
    try:
        compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
        raise AssertionError("a body missing from the cut list was drawn")
    except NotDrawable as e:
        assert "219983 has 1 bodies under the frame, its cut list 0" in str(e), e


def test_a_bought_part_under_the_frame_is_refused():
    d, step, spec = _made("bought", bought=True)
    real = inputs.parts_row
    inputs.parts_row = lambda pn, team: (({"part_number": pn, "kind": "PI", "name": "TEST RIVNUT"}, [], None)
                                         if pn == "219984" else real(pn, team))
    try:
        compose.make("219980", "none", spec, os.path.join(d, "x.pdf"), step=step, row=ROW)
        raise AssertionError("a bought part under the frame was drawn as frame material")
    except NotDrawable as e:
        assert "219984" in str(e) and "bought part" in str(e), e
    finally:
        inputs.parts_row = real


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
