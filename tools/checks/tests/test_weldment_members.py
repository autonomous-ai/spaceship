"""The Lead's ruling (2026-11-01) for D-131's welded frames: a member's drawing is its row in its frame's cut list, on
the weldment drawing (D-120 members). A member needs a sheet of its own only for work done before welding, or an end
cut a cut list can't state. C05 takes the cut-list row for such a member; no exception rows."""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_drawings  # noqa: E402
import stepfile as sf  # noqa: E402

CUT_LIST = "v2/03-Manufacturing/front/351204_P01_FRONT-DECOR-FRAME-DT-TUBE-CUT-LIST.csv"
HEAD = "frame,member,member_part,name,section,length_mm,qty,ends,status\n"
ROW = "%s,%s,%s,%s,6063-T6 aluminium tube 20 x 20 x 1.5,%s,1,%s,calculation (from the parameters)\n"


def _pdf(path, text):
    fitz = pytest.importorskip("fitz")
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    for line in text.split("\n"):
        page.insert_text((40, y), line)
        y += 20
    doc.save(str(path))


def _repo(tmp_path, rows, frame_sheet=None):
    p = tmp_path / CUT_LIST
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(HEAD + "".join(ROW % r for r in rows), encoding="utf-8")
    if frame_sheet is not None:
        _pdf(tmp_path / "v2/02-Drawings/front/351204_P01_FRONT-DECOR-FRAME-DT_DWG.pdf", frame_sheet)
    return str(tmp_path)


def _missing(fs):
    return {f.subject: f.message for f in fs if f.rule == "no-drawing"}


MITRED = "45.0° at the bottom end; 30.0° at the top end"           # both end angles, as D-162 asks
DEFERRED = "mitred to its neighbours (angles on the frame drawing)"   # not stated in the row (D-162)
SHEET = ("CUT LIST\nMEMBER  PART    NAME                 LENGTH\nB01     352201  BACK RING BOTTOM     1422.8\n"
         "B02     352202  BACK RING DR JOINT   268.0\nB03     352203  BACK RING TOP        1691.7")


def test_a_member_on_its_frames_drawing_needs_no_sheet_of_its_own(tmp_path):
    root = _repo(tmp_path, [("351204", "B01", "352201", "BACK RING BOTTOM", "1422.8", MITRED)], SHEET)
    assert c_drawings.weldment_members(root)["352201"][0][0] == "351204"
    fs = c_drawings.check_drawings(root, {"352201"}, {}, {"352201": "FRONT - DECOR FRAME DT - BACK RING BOTTOM"},
                                   ends_by_pn={"352201": [(1, 1)]})
    assert "352201" not in _missing(fs)
    # square ends said in words count as both angles; 'angles on the frame drawing' doesn't state them
    assert c_drawings.member_row_lacks({"section": "20 x 20", "length_mm": "300", "ends": "square both ends",
                                        "qty": "1"}) == []
    assert c_drawings.member_row_lacks({"section": "20 x 20", "length_mm": "300", "ends": DEFERRED, "qty": ""}) == \
        ["both end angles", "its quantity"]
    # angles in 'deg' or 'degrees' count as well as in '°' (Reviewer 6 on the checklist; CEILING's rows, #348)
    for ends in ("front end mitred 45 deg, back end mitred 63.43 deg off square", "45 degrees and 30 Degrees",
                 # one angle for both ends states both (the Lead's ruling; CEILING's rows 412103, 412104 in #348)
                 "both ends mitred 45 deg; welded into the frame (D-131, J-FRAME-01)",
                 "both ends mitred 26.57 deg off square; welded into the frame", "mitred 30° at both ends",
                 # WALL's rows in #343 (212103 to 212105)
                 "bottom and top ends both mitred 45.00° off square, in the frame's plane",
                 "square ends (fits between the rails, welded T joints, D-131)"):
        assert c_drawings.member_row_lacks({"section": "20 x 40 x 1.0", "length_mm": "1491.35", "ends": ends,
                                            "qty": "1"}) == [], ends
    # but one angle for one end isn't both, and 'both ends' with no angle isn't either
    for ends in ("front end mitred 45 deg; back end to suit", "both ends mitred to suit; 45 deg plate"):
        assert c_drawings.member_row_lacks({"section": "s", "length_mm": "1", "ends": ends, "qty": "1"}) == \
            ["both end angles"], ends


def test_d162_the_row_gives_section_length_both_end_angles_and_quantity(tmp_path):
    root = _repo(tmp_path, [("351204", "B01", "352201", "BACK RING BOTTOM", "1422.8", DEFERRED)], SHEET)
    fs = c_drawings.check_drawings(root, {"352201"}, {}, {}, ends_by_pn={"352201": [(1, 1)]})
    assert "its cut-list row doesn't give both end angles (D-162)" in _missing(fs)["352201"]


def test_a_member_keeps_its_own_sheet_for_work_before_welding_or_an_end_a_list_cant_state(tmp_path):
    rows = [("351204", "B01", "352201", "BACK RING BOTTOM", "1422.8", "square; holes drilled before welding"),
            ("351204", "B02", "352202", "BACK RING DR JOINT", "268.0", "coped to the post"),
            ("351204", "B03", "352203", "BACK RING TOP", "1691.7", MITRED)]
    root = _repo(tmp_path, rows, SHEET)
    fs = c_drawings.check_drawings(root, {"352201", "352202", "352203"}, {}, {},
                                   ends_by_pn={"352203": [(2, 1)]})      # one end cut by two planes in its STEP
    got = _missing(fs)
    assert "work done before welding" in got["352201"]
    assert "an end cut a cut list can't state ('coped')" in got["352202"]
    assert "an end cut by 2 planes" in got["352203"]
    assert all(f.severity == "severe" for f in fs if f.rule == "no-drawing")
    assert all("in its row of the frame's cut list, on the frame's drawing" in f.fix for f in fs
               if f.rule == "no-drawing")


def test_the_row_must_be_on_the_frames_drawing(tmp_path):
    rows = [("351204", "B04", "352204", "BACK RING SLOPE OVER DL", "379.7", MITRED),
            ("351204", "B05", "352204", "BACK RING SLOPE OVER DL (2nd)", "379.7", MITRED)]
    # no frame drawing yet: the frame's own finding carries it, naming its members once, not one finding per member
    fs = c_drawings.check_drawings(_repo(tmp_path, rows), {"352204", "351204"}, {}, {}, ends_by_pn={"352204": [(1, 1)]})
    got = _missing(fs)
    assert "352204" not in got
    assert "carries their cut list (D-162), 1 member (352204)" in got["351204"]
    assert [f.fix for f in fs if f.subject == "351204"][0].endswith("with its members' cut list on it (D-162).")
    # a frame drawing whose cut list doesn't carry the member's number
    fs = c_drawings.check_drawings(_repo(tmp_path, rows, SHEET), {"352204"}, {}, {}, ends_by_pn={"352204": [(1, 1)]})
    assert "drawing 351204_P01_FRONT-DECOR-FRAME-DT_DWG.pdf doesn't show its cut-list row" in _missing(fs)["352204"]
    # a part that isn't in any frame's cut list is untouched by the rule
    fs = c_drawings.check_drawings(_repo(tmp_path, rows, SHEET), {"352299"}, {}, {})
    assert "welded frame" not in _missing(fs)["352299"]


def _face(pts, normal):
    return sf.Face(None, "plane", pts[0], normal, None, True, list(pts), [],
                   [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))])


def _bar(notch=False):
    """A 20 x 20 bar along X, square at X 0 and mitred at 45 degrees at the far end (the plane X + Y = 300); with
    notch, the X 0 end has a 15 deep notch over Y 0 to 10 (two planes at that end)."""
    s = sf.Solid(1, "BAR")
    far = [(300, 0, 0), (280, 20, 0), (280, 20, 20), (300, 0, 20)]
    s.faces = [_face(far, (0.70710678, 0.70710678, 0.0)),
               _face([(0, 0, 0), (300, 0, 0), (280, 20, 0), (0, 20, 0)], (0, 0, -1)),
               _face([(0, 0, 20), (300, 0, 20), (280, 20, 20), (0, 20, 20)], (0, 0, 1)),
               _face([(0, 0, 0), (300, 0, 0), (300, 0, 20), (0, 0, 20)], (0, -1, 0)),
               _face([(0, 20, 0), (280, 20, 0), (280, 20, 20), (0, 20, 20)], (0, 1, 0))]
    if notch:
        s.faces += [_face([(0, 10, 0), (0, 20, 0), (0, 20, 20), (0, 10, 20)], (-1, 0, 0)),
                    _face([(15, 0, 0), (15, 10, 0), (15, 10, 20), (15, 0, 20)], (-1, 0, 0)),
                    _face([(0, 10, 0), (15, 10, 0), (15, 10, 20), (0, 10, 20)], (0, -1, 0))]
    else:
        s.faces.append(_face([(0, 0, 0), (0, 20, 0), (0, 20, 20), (0, 0, 20)], (-1, 0, 0)))
    return s


def test_member_ends_reads_one_plane_per_end_and_sees_a_notch():
    assert c_drawings.member_ends(_bar()) == (1, 1)
    assert c_drawings.member_ends(_bar(notch=True)) == (2, 1)
    # a slot's end far along the member is a feature along it, not an end cut
    s = _bar()
    s.faces.append(_face([(150, 0, 5), (150, 0, 15), (150, 6, 15), (150, 6, 5)], (-1, 0, 0)))
    assert c_drawings.member_ends(s) == (1, 1)
    # a block no longer than 1.5 times its section isn't a member tube: no verdict from its ends
    short = sf.Solid(2, "BLOCK")
    short.faces = [_face([(0, 0, 0), (25, 0, 0), (25, 20, 0), (0, 20, 0)], (0, 0, -1)),
                   _face([(0, 0, 20), (25, 0, 20), (25, 20, 20), (0, 20, 20)], (0, 0, 1)),
                   _face([(0, 0, 0), (0, 20, 0), (0, 20, 20), (0, 0, 20)], (-1, 0, 0)),
                   _face([(25, 0, 0), (25, 20, 0), (25, 20, 20), (25, 0, 20)], (1, 0, 0))]
    assert c_drawings.member_ends(short) is None
