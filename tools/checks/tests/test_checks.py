"""Offline tests for tools/checks. Run: python3 -m pytest tools/checks/tests -q

Each rule is shown firing on a bad input and staying quiet on a good one.
Real repo files are used where they exist (the Phase 0 proof part and the
skeleton P03 STEP); the rest is built in the test.
"""

import csv
import math
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import stepfile as sf  # noqa: E402
import c_geometry  # noqa: E402
import c_parts  # noqa: E402
import c_stacks  # noqa: E402
import c_drawings  # noqa: E402
import register  # noqa: E402
from common import Finding, pn_class, pn_problems, parse_file_name, owner_for  # noqa: E402

PROOF = os.path.join(ROOT, "v2/03-Manufacturing/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step")
# skeleton P03 as it was on main at c9ae2a4, kept as a fixed test model: it has the seam, kick-strip
# and back-slot faults F-001, F-002 and F-004 that P04 fixed
SKEL = os.path.join(HERE, "fixtures", "skeleton-P03.step")


# ----------------------------------------------------------------- STEP reader

def test_step_units_products_and_holes_match_the_proof_build_record():
    s = sf.StepFile(PROOF)
    assert s.unit_name == "cm" and s.scale == 10.0
    counts, tops = s.usage_counts()
    assert tops == ["V2-SWL-00"]
    by_name = {}
    for inst in s.instances():
        so = s.solid(inst["solid"])
        by_name[so.name] = (so, inst)
    rail, _ = by_name["WALL - FRAME RAIL - TOP - TUBE"]
    # build record: 4 holes per rail at X 60, 510, 960, 1410, through both walls
    xs = sorted({round(h.center[0], 1) for h in rail.holes})
    assert xs == [60.0, 510.0, 960.0, 1410.0]
    assert len(rail.holes) == 8 and all(abs(h.diameter - 6.6) < 1e-6 for h in rail.holes)
    # the hole 40 mm from the rail's end (rail runs X 20 to 1450)
    h = [h for h in rail.holes if round(h.center[0]) == 1410][0]
    d, kind = sf.edge_distance(rail, h)
    assert kind == "free edge" and abs(d - 40.0) < 1e-6
    stile, _ = by_name["WALL - FRAME STILE - REAR - TUBE"]
    h = [h for h in stile.holes if round(h.center[2]) == 1090][0]
    assert abs(sf.edge_distance(stile, h)[0] - 60.0) < 1e-6
    assert rail.thickness == 1.2


def test_step_assembly_transforms_put_skeleton_envelopes_in_pod_coordinates():
    bodies = c_geometry.bodies_of(ROOT, SKEL)
    boxes = {b.label.split(" / ")[-1]: b.box for b in bodies}
    assert boxes["B1 ENVELOPE"] == pytest.approx((-1207.0, 807.0, 110.0, 0.0, 850.0, 1214.5), abs=1e-6)
    assert boxes["KICK ENVELOPE"][2] == pytest.approx(20.0) and boxes["THRESHOLD ENVELOPE"][5] == pytest.approx(20.0)


def test_parse_entities_handles_strings_with_semicolons_and_complex_entities():
    text = "DATA;\n#1=PRODUCT('a;b','it''s',$,(#2));\n#2=(NAMED_UNIT(*) LENGTH_UNIT() SI_UNIT(.MILLI.,.METRE.));\nENDSEC;"
    e = sf.parse_entities(text)
    assert e[1][0][1][0] == "a;b" and e[1][0][1][1] == "it's"
    assert [n for n, _ in e[2]] == ["NAMED_UNIT", "LENGTH_UNIT", "SI_UNIT"]


# ----------------------------------------------------------------- synthetic solids

def _arc(center, axis, xdir, r, a0, a1, forward=True):
    fr = sf.Frame.from_axes(center, axis, xdir)
    p = lambda a: fr.point((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.0))
    return (fr, r, p(a0), p(a1), forward)


def _plate_with_hole(width=100.0, height=50.0, t=2.0, hole_x=10.0, hole_y=25.0, d=6.0):
    """A flat plate in XY (Z 0 to t) with one through hole."""
    s = sf.Solid(1, "plate")
    corners = [(0, 0), (width, 0), (width, height), (0, height)]
    lines_top = [((*corners[i], t), (*corners[(i + 1) % 4], t)) for i in range(4)]
    lines_bot = [((*corners[i], 0.0), (*corners[(i + 1) % 4], 0.0)) for i in range(4)]
    rim_top = _arc((hole_x, hole_y, t), (0, 0, 1), (1, 0, 0), d / 2, 0, 0)
    rim_bot = _arc((hole_x, hole_y, 0.0), (0, 0, 1), (1, 0, 0), d / 2, 0, 0)
    pts_top = [p for ln in lines_top for p in ln] + [rim_top[2]]
    pts_bot = [p for ln in lines_bot for p in ln] + [rim_bot[2]]
    s.faces.append(sf.Face(1, "plane", (0, 0, t), (0, 0, 1), None, True, pts_top, [rim_top], lines_top))
    s.faces.append(sf.Face(2, "plane", (0, 0, 0), (0, 0, -1), None, True, pts_bot, [rim_bot], lines_bot))
    s.faces.append(sf.Face(3, "cylinder", (hole_x, hole_y, 0), (0, 0, 1), d / 2, False,
                           [rim_top[2], rim_bot[2]], [rim_top, rim_bot], []))
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        n = sf.norm(((b[1] - a[1]), -(b[0] - a[0]), 0.0))
        pts = [(*a, 0.0), (*b, 0.0), (*a, t), (*b, t)]
        s.faces.append(sf.Face(10 + i, "plane", (*a, 0.0), n, None, True, pts, [],
                               [((*a, 0.0), (*b, 0.0)), ((*a, t), (*b, t))]))
    s.box = (0, 0, 0, width, height, t)
    s.thickness = sf._sheet_thickness(s)
    s.holes = sf._holes(s)
    return s


def _half_cyl(x, r=3.25, t=1.5, side=1.0):
    """A concave half-cylinder face (a slot's round end) on the X axis at x, t long, 180 degrees of arc."""
    fr = sf.Frame((x, 830.0, 73.5), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (side, 0.0, 0.0))
    a = (fr, r, (x, 830.0 + r, 73.5), (x, 830.0 - r, 73.5), True)
    b = (sf.Frame((x + t, 830.0, 73.5), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (side, 0.0, 0.0)), r,
         (x + t, 830.0 + r, 73.5), (x + t, 830.0 - r, 73.5), True)
    pts = [a[2], a[3], b[2], b[3]]
    return sf.Face(1, "cylinder", (x, 830.0, 73.5), (side, 0.0, 0.0), r, False, pts, [a, b], [])


def test_a_hole_goes_all_the_way_round_in_its_own_place_on_the_axis():
    # BASE's D-129 back band: a half-round slot end in each end plate, 2.4 m apart on one axis, isn't a hole
    import types
    solid = types.SimpleNamespace(id=7, faces=[_half_cyl(-1210.0), _half_cyl(1208.5)])
    assert sf._holes(solid) == []
    # two half faces in one place make one hole
    solid = types.SimpleNamespace(id=7, faces=[_half_cyl(-1210.0), _half_cyl(-1210.0, side=-1.0)])
    hs = sf._holes(solid)
    assert len(hs) == 1 and abs(hs[0].diameter - 6.5) < 1e-9 and abs(hs[0].length - 1.5) < 1e-9


def test_edge_distance_rule_fires_under_two_diameters_and_not_above():
    bad = _plate_with_hole(hole_x=10.0, d=6.0)       # 10 < 12
    assert bad.thickness == 2.0 and len(bad.holes) == 1
    assert sf.edge_distance(bad, bad.holes[0])[0] == pytest.approx(10.0)
    good = _plate_with_hole(hole_x=13.0, d=6.0)      # 13 > 12, and 25 to the long edges
    assert sf.edge_distance(good, good.holes[0])[0] == pytest.approx(13.0)


def test_bend_found_and_hole_to_bend_measured():
    s = sf.Solid(2, "bracket")
    t, r = 1.5, 0.5
    # bend axis along X through (0, 0, 0); inner radius r, outer r + t, a 90 degree arc
    inner = sf.Face(1, "cylinder", (0, 0, 0), (1, 0, 0), r, False, [], [_arc((0, 0, 0), (1, 0, 0), (0, 1, 0), r, 0, 90)], [])
    outer = sf.Face(2, "cylinder", (0, 0, 0), (1, 0, 0), r + t, True, [], [_arc((0, 0, 0), (1, 0, 0), (0, 1, 0), r + t, 0, 90)], [])
    inner.points = [inner.arcs[0][2], inner.arcs[0][3]]
    outer.points = [outer.arcs[0][2], outer.arcs[0][3]]
    s.faces = [inner, outer]
    s.thickness = t
    bends = sf._bends(s)
    assert len(bends) == 1 and bends[0].inner_radius == pytest.approx(r) and bends[0].angle_deg == pytest.approx(90)
    # a hole in the flange that lies in the XY plane, axis along Z, 4 mm from the bend axis
    h = sf.Hole(2, (10.0, -4.0, 0.0), (0.0, 0.0, 1.0), 3.0, t, [])
    assert sf.hole_to_bend(h, bends[0]) == pytest.approx(4.0 - 1.5)


def test_part_feature_check_reports_edge_distance_and_bend_radius(monkeypatch, tmp_path):
    bad = _plate_with_hole(hole_x=8.0, d=6.0)

    class FakeStep:
        def instances(self):
            return [{"solid": 1, "part_number": "211500", "name": "x", "path": ["211500"], "frame": sf.Frame()}]

        def solid(self, sid):
            return bad
    monkeypatch.setitem(c_geometry.load_step.__defaults__[0], str(tmp_path / "x.step"), FakeStep())
    fs = c_geometry.check_part_features(str(tmp_path), str(tmp_path / "x.step"), {}, [])
    assert [f.rule for f in fs] == ["edge-distance"] and fs[0].severity == "severe"   # 8 < 1.5 x 6 = 9


# ----------------------------------------------------------------- shell and gap rules

class _B:
    def __init__(self, label, box, pn="", holes=()):
        self.label, self.box, self.part_number, self.file = label, box, pn, "x.step"
        self.solid = type("S", (), {"holes": list(holes)})()
        self.frame = sf.Frame()


def test_shell_check_finds_the_back_top_slot_in_skeleton_p03():
    bodies = c_geometry.bodies_of(ROOT, SKEL)
    gaps = c_geometry.shell_gaps(bodies, root=ROOT)
    assert len(gaps) == 1
    g = gaps[0]
    assert g["zone"] == "back" and g["a"] == pytest.approx((-1207, 1207)) and g["b"] == pytest.approx((2319, 2357))


def test_shell_check_quiet_when_panels_meet():
    walls = [_B("back", (-1250, 807, 110, 1250, 850, 2400)), _B("left", (-1250, -645, 110, -1207, 850, 2400)),
             _B("right", (1207, -645, 110, 1250, 850, 2400)), _B("roof", (-1250, -645, 2357, 1250, 850, 2400))]
    assert c_geometry.shell_gaps(walls) == []
    # the decided 2.26 mm seam is a seam, not an opening
    seam = [_B("b1", (-1250, 807, 110, -1.13, 850, 2400)), _B("b2", (1.13, 807, 110, 1250, 850, 2400))] + walls[1:]
    assert c_geometry.shell_gaps(seam) == []


def test_gap_rules_reproduce_f001_f002_on_skeleton_and_pass_when_fixed():
    rules = c_geometry.load_gap_rules(ROOT)
    bodies = c_geometry.bodies_of(ROOT, SKEL)
    keys = {f.key for f in c_geometry.check_gap_rules(ROOT, "skeleton", bodies, rules)}
    assert "C02|gap-SEAM-GAPS|skeleton SEAM-GAPS" in keys
    assert not any("KICK" in k for k in keys)    # D-151: the skeleton's thresh_h is no longer the kick strip's datum
    assert not any("LINING-FLOATS" in k for k in keys)          # the linings float in P03


def test_the_kick_strip_runs_on_the_bands_bottom_line_over_the_room_floor():
    # D-151 (D-132: no threshold): the kick strip's bottom at glide_h, Z 10, over the room floor, the plane Z 0
    rules = c_geometry.load_gap_rules(ROOT)
    old = [_B("FRONT - DOOR KICK STRIP", (-961, -709, 7, 214, -689, 105))]          # threshold + 7 with no threshold
    fs = c_geometry.check_gap_rules(ROOT, "assembly", old, rules)
    assert [(f.rule, f.severity) for f in fs] == [("gap-KICK-OVER-FLOOR", "severe")] and "7.0 mm" in fs[0].message
    ok = [_B("FRONT - DOOR KICK STRIP", (-961, -709, 10, 214, -689, 105)),
          _B("AIR - KICK GRILLE", (900, -700, 2, 1100, -690, 100))]                 # not the door's strip
    assert c_geometry.check_gap_rules(ROOT, "assembly", ok, rules) == []


def test_alignment_flags_offset_mating_holes_only():
    h1 = sf.Hole(1, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 6.6, 1.2, [])
    h2 = sf.Hole(2, (2.0, 0.3, 0.0), (1.0, 0.0, 0.0), 6.6, 1.2, [])
    h3 = sf.Hole(3, (2.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 6.6, 1.2, [])
    a, b, c = _B("frame A", None, "211101", [h1]), _B("frame B", None, "211201", [h2]), _B("frame C", None, "211301", [h3])
    fs = c_geometry.check_alignment(ROOT, "assembly", [a, b])
    assert len(fs) == 1 and fs[0].evidence["offset_mm"] == pytest.approx(0.3)
    assert c_geometry.check_alignment(ROOT, "assembly", [a, c]) == []


# ----------------------------------------------------------------- parts lists

def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def test_parts_list_checks(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    good = {"part_number": "211101", "name": "WALL - PANEL FRAME - SIDE LOWER - LH", "name_vi": "Vách trái - khung dưới",
            "material": "EN AW-6063 T6", "finish": "mill finish", "qty": "1", "mass_kg": "2.4", "status": "calculation",
            "source": "CAD", "maker": "", "sku": "", "size": "", "length_mm": "", "torque_nm": ""}
    no_finish = dict(good, part_number="211102", name="WALL - PANEL FRAME - SIDE UPPER - LH", finish="", material="aluminium")
    bolt = dict(good, part_number="838001", name="HARDWARE - BOLT - M6 X 60", material="steel", finish="", maker="",
                sku="", torque_nm="", mass_kg="0.02")
    reserved = dict(good, part_number="211000", name="WALL - BONDED PANEL")
    _write_csv(d / "parts.csv", [good, no_finish, bolt, reserved])
    plists = c_parts.find_parts_lists(str(tmp_path))
    assert len(plists) == 1
    fs = c_parts.check_parts_lists(str(tmp_path), plists)
    rules = {(f.rule, f.subject) for f in fs}
    assert ("material-finish", "211102") in rules           # C11: no finish, no grade
    assert ("material-finish", "211101") not in rules
    assert ("fastener-spec", "838001") in rules             # C07: no finish, torque, maker, SKU
    assert ("bad-part-number", "211000") in rules           # D-28 reserved
    assert any(f.rule == "bad-part-number" and f.severity == "severe" for f in fs)
    mm = c_parts.check_mixed_metals(str(tmp_path), plists, [])
    assert {(f.rule, f.subject) for f in mm} == {("fastener-bare-steel", "838001")}   # C10


def test_metal_classes():
    assert c_parts.metal_class("EN AW-6063 T6") == "aluminium"
    assert c_parts.metal_class("DX51D+Z275 galvanised steel") == "steel-coated"
    assert c_parts.metal_class("steel 8.8") == "steel-bare"
    assert c_parts.metal_class("8.8 zinc plated") == "steel-coated"
    assert c_parts.metal_class("A2-70") == "stainless"


def test_fasteners_are_family_83_but_not_the_frames_welded_mitre_plates():
    from common import is_fastener
    assert is_fastener("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS")
    assert is_fastener("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2")
    assert is_fastener("", "HARDWARE - BOLT - M6 X 16")
    assert not is_fastener("831007", "HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL")
    assert not is_fastener("831008", "HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL")


def test_shipping_rules(tmp_path):
    d = tmp_path / "v2/05-Engineering/layout-study/out"
    d.mkdir(parents=True)
    rows = [
        {"id": "OK", "name": "WALL - PANEL", "assembly": "WALL", "size_mm": "1495 x 1145 x 43", "kg_each": "11.9",
         "ships_as": "upright", "status": "calculation"},
        {"id": "HEAVY", "name": "WALL - PANEL", "assembly": "WALL", "size_mm": "1495 x 1145 x 43", "kg_each": "21",
         "ships_as": "upright", "status": "calculation"},
        {"id": "GLASS", "name": "FRONT - GLASS DOOR", "assembly": "FRONT", "size_mm": "2096 x 1176 x 20",
         "kg_each": "47.5", "ships_as": "glass", "status": "calculation"},
        {"id": "WIDE", "name": "BASE - SLAB", "assembly": "BASE", "size_mm": "2100 x 950 x 950", "kg_each": "5",
         "ships_as": "long", "status": "assumption"},
        {"id": "LONGBOX", "name": "FRONT - PROFILES", "assembly": "FRONT", "size_mm": "2200 x 120 x 60",
         "kg_each": "2.6", "ships_as": "box", "status": "assumption"},
        {"id": "TOOLONGBOX", "name": "FRONT - PROFILES", "assembly": "FRONT", "size_mm": "2500 x 120 x 60",
         "kg_each": "2.6", "ships_as": "box", "status": "assumption"},
    ]
    _write_csv(d / "parts-option-B1-final-stack.csv", rows)
    fs, rep, src = c_parts.check_shipping(str(tmp_path))
    got = {(f.rule, f.subject) for f in fs}
    assert ("mass-over-20kg", "HEAVY") in got and ("mass-over-20kg", "GLASS") not in got
    assert ("doorway", "WIDE") in got                       # 950 and 950: passes 914? no
    # the layout packer puts box pieces in its 2400 mm kit carton on the long pallet (pallets.py)
    assert ("pallet-fit", "LONGBOX") not in got and ("pallet-fit", "TOOLONGBOX") in got
    assert not any(s == "OK" for _r, s in got)


# ----------------------------------------------------------------- stacks

def test_stack_worst_case_and_open_state():
    contribs = [
        {"name": "space", "sign": "1", "nominal_mm": "100", "plus_mm": "0.5", "minus_mm": "0.5"},
        {"name": "part", "sign": "-1", "nominal_mm": "98", "plus_mm": "0.3", "minus_mm": "0.1"},
    ]
    r = c_stacks.evaluate(contribs)
    assert r["nominal"] == pytest.approx(2.0)
    assert r["wc_min"] == pytest.approx(2.0 - 0.5 - 0.3) and r["wc_max"] == pytest.approx(2.0 + 0.5 + 0.1)
    assert r["missing"] == []
    r = c_stacks.evaluate(contribs + [{"name": "gasket", "sign": "-1", "nominal_mm": "", "plus_mm": "", "minus_mm": ""}])
    assert r["missing"] == ["gasket"]


def test_repo_stacks_are_open_until_tolerances_exist():
    fs, rep = c_stacks.check_stacks(ROOT)
    assert {r["stack_id"]: r["state"] for r in rep} == {"ST-01": "OPEN", "ST-02": "OPEN", "ST-02A": "PASS",
                                                        "ST-03": "PASS", "ST-04": "OPEN", "ST-04A": "PASS"}
    # D-65 with the joints register's closing seam (R-J16): frames 1198.99, frame gap 5.5 inside 4.0 to 7.0;
    # with perfect frames the two corner stops move it 5.5 +-0.26
    st2a = [r for r in rep if r["stack_id"] == "ST-02A"][0]
    assert st2a["wc_min"] == pytest.approx(5.24) and st2a["wc_max"] == pytest.approx(5.76)
    assert fs == []
    st3 = [r for r in rep if r["stack_id"] == "ST-03"][0]
    # F-009 ruling: Ø7.0 holes, positions Ø0.4 each: (7.0 - 5.974) / 2 - 0.2 - 0.2 - 0.065 rivnut float
    assert st3["nominal"] == pytest.approx(0.513) and st3["wc_min"] == pytest.approx(0.048)


# ----------------------------------------------------------------- drawings

def test_drawing_check(tmp_path):
    fitz = pytest.importorskip("fitz")
    (tmp_path / "v2/02-Drawings/wall").mkdir(parents=True)
    (tmp_path / "v2/03-Manufacturing/wall").mkdir(parents=True)
    pdf = tmp_path / "v2/02-Drawings/wall/211101_P01_WALL-PANEL-FRAME_DWG.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "UNITS: mm  MATERIAL: EN AW-6063 T6  FINISH: mill  GENERAL TOLERANCES ISO 2768-m")
    page.insert_text((50, 80), "H01  H02")
    doc.save(str(pdf))
    holes = [sf.Hole(1, (0, 0, 0), (1, 0, 0), 6.6, 1.2, []), sf.Hole(1, (0, 0, 100), (1, 0, 0), 6.6, 1.2, []),
             sf.Hole(1, (0, 0, 200), (1, 0, 0), 6.6, 1.2, [])]
    fs = c_drawings.check_drawings(str(tmp_path), {"211101", "211102"}, {"211101": holes})
    got = {(f.rule, f.subject) for f in fs}
    assert ("no-drawing", "211102") in got                 # no PDF at all: severe for a part
    assert ("holes-untagged", "211101") in got             # 3 hole axes, 2 tags
    assert not any(r == "drawing-content" for r, _s in got)


# ----------------------------------------------------------------- register

def test_register_lifecycle(tmp_path):
    reg = {"next": 1, "findings": []}
    f1 = Finding("C04", "mass-over-20kg", "W1", "severe", "too heavy", evidence={}).to_dict()
    f2 = Finding("C02", "gap-X", "skeleton X", "major", "no gap", evidence={"model": "skeleton"}).to_dict()
    new, re_, closed = register.merge(reg, [f1, f2], "aaa", "2026-10-31", ["C04", "C02:skeleton"])
    assert new == ["F-001", "F-002"] and not re_ and not closed
    # next run: f1 fixed, the skeleton model not checked: f2 must stay open
    new, re_, closed = register.merge(reg, [], "bbb", "2026-10-31", ["C04"])
    assert closed == ["F-001"]
    assert [f["status"] for f in reg["findings"]] == ["CLOSED", "OPEN"]
    # it comes back: reopened with the same number
    new, re_, closed = register.merge(reg, [f1], "ccc", "2026-10-31", ["C04"])
    assert re_ == ["F-001"] and new == []
    register.save(reg, str(tmp_path))
    md = open(tmp_path / "v2/04-Checks/findings.md", encoding="utf-8").read()
    assert "F-001" in md and "Open: 2" in md


def test_part_numbers_and_file_names():
    assert pn_class("211101") == "part" and pn_class("210000") == "assembly" and pn_class("838001") == "bought"
    assert "reserved by D-28 (old V5 number)" in pn_problems("350011")
    m = parse_file_name("211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG.pdf")
    assert m["pn"] == "211101" and m["rev"] == "P01" and m["doc"] == "DWG"
    assert owner_for("v2/03-Manufacturing/front/x.step") == "FRONT" and owner_for("", "") == "PM"
    assert owner_for("", "411001") == "CEILING"


def test_pod_mass_against_the_cap(tmp_path):
    # D-131: the cap is 460 kg (provisional until the wall sample's recount), from config/policy.csv
    rows = [{"kg_total": "440.0"}, {"kg_total": "26.7"}]
    fs, info = c_parts.check_pod_mass(str(tmp_path), rows, "list.csv")
    assert info["total_kg"] == pytest.approx(466.7) and info["cap_kg"] == 460.0
    assert [f.rule for f in fs] == ["pod-mass-over-cap"] and "460 kg cap (D-131" in fs[0].message
    fs, info = c_parts.check_pod_mass(str(tmp_path), [{"kg_total": "426.7"}], "list.csv")
    assert fs == []                                                       # over the old 420, under D-131's 460
    assert c_parts.check_pod_mass(ROOT, [{"kg_total": "1"}], "list.csv")[1]["cap_kg"] == 460.0   # the repo's policy


def test_what_decisions_cancelled_is_gone_and_what_they_added_is_there(tmp_path):
    # D-131 cancels the cleats, D-132 the floor parts and the threshold and adds the base seal lip
    import shutil
    cfg = tmp_path / "v2/04-Checks/config"
    cfg.mkdir(parents=True)
    for n in ("cancelled-items.csv", "required-items.csv"):
        shutil.copy(os.path.join(ROOT, "v2/04-Checks/config", n), cfg / n)
    d = tmp_path / "v2/03-Manufacturing/base"
    d.mkdir(parents=True)
    row = {"part_number": "111401", "name": "BASE - FLOOR PANEL - F1", "name_vi": "x", "material": "plywood 9",
           "finish": "HPL", "qty": "1", "mass_kg": "9", "status": "DRAFT", "source": "CAD"}
    rows = [row, dict(row, part_number="111501", name="BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM"),
            dict(row, part_number="111101", name="BASE - BAND TUBE - SIDE - LH")]
    _write_csv(d / "110000_P01_BASE_BOM.csv", rows)
    plists = c_parts.find_parts_lists(str(tmp_path))
    prods = {"118003": {"files": {"v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step"}, "count": 1,
                        "name": "118003 FRONT - THRESHOLD - 13 MM"},
             "212999": {"files": {"v2/03-Manufacturing/skeleton/x.step"}, "count": 1, "name": "212999 CORNER CLEAT"}}
    got = {(f.rule, f.subject): f for f in c_parts.check_decided_items(str(tmp_path), plists, prods)}
    assert {k for k in got if k[0] == "cancelled-by-decision"} == {
        ("cancelled-by-decision", "111401"), ("cancelled-by-decision", "111501"), ("cancelled-by-decision", "118003")}
    assert got[("cancelled-by-decision", "111401")].owner == "BASE" and "D-132" in got[("cancelled-by-decision", "111401")].message
    assert got[("cancelled-by-decision", "118003")].owner == "FRONT"                 # the skeleton's cleat isn't a part
    req = [f for f in got.values() if f.rule == "required-by-decision"]
    assert len(req) == 1 and req[0].owner == "BASE" and "seal lip" in req[0].message
    _write_csv(d / "110000_P01_BASE_BOM.csv", rows[2:] + [dict(row, part_number="118101", name="BASE - SEAL LIP - SOFT")])
    got = c_parts.check_decided_items(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)), {})
    assert got == []                                                       # floor parts gone, the lip there


def test_repo_pod_mass_from_the_newest_list_without_double_counting():
    src, rows = c_parts.load_mass_list(ROOT)
    fs, info = c_parts.check_pod_mass(ROOT, rows, src)
    if src.endswith("parts-decided-P04.csv"):
        # the P04 roll-up already holds the air parts, the tray lips and the 9 mm floor: no adjustments on top
        # no adjustments on top of the live roll-up; any voice cockpit kit line sits outside the cap (D-81)
        assert info["adjustments"] == []
        assert info["total_kg"] == pytest.approx(sum(float(r["kg_total"]) for r in rows) - info["outside_cap_kg"],
                                                 abs=0.01)
    else:
        # the older list: 426.73 + 11.8 air + 3.4 wall trays - 12.6 floor (D-71)
        assert info["total_kg"] == pytest.approx(429.33, abs=0.01)
    # a finding exactly when the total is over the cap
    assert bool(fs) == (info["total_kg"] > info["cap_kg"])
    assert all(f.rule == "pod-mass-over-cap" for f in fs)


def test_skip_rules_use_whole_words_and_their_own_columns(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/base"
    d.mkdir(parents=True)
    base = {"part_number": "", "name": "", "name_vi": "x", "material": "", "finish": "", "qty": "1", "mass_kg": "1",
            "status": "calculation", "source": "CAD", "maker": "", "sku": ""}
    rows = [
        dict(base, part_number="111001", name="BASE - DOOR THRESHOLD", material="EN AW-6063 T6"),        # THRESHOLD
        dict(base, part_number="111002", name="BASE - SEAL HOLDER", material="EN AW-6063 T6"),           # HOLDER
        dict(base, part_number="118001", name="BASE - PROFILE", material="EN AW-6063 T6"),               # 4 digits, bought
        dict(base, part_number="118002", name="BASE - HINGE - HOLD", material="not named", status="HOLD (ISS-002)"),
        dict(base, part_number="118003", name="BASE - SEAL", material="EPDM", finish="black", maker="Acme",
             sku="SEAL-123", status="source"),
    ]
    _write_csv(d / "parts.csv", rows)
    fs = c_parts.check_parts_lists(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)))
    got = {(f.rule, f.subject) for f in fs}
    assert ("material-finish", "111001") in got              # THRESHOLD is not HOLD
    assert ("material-finish", "111002") in got              # HOLDER is not HOLD
    assert ("bought-no-sku", "118001") in got                # EN AW-6063 is not an SKU
    assert ("material-finish", "118001") in got
    assert not any(s == "118002" for _r, s in got)          # HOLD in its status column: skipped
    assert not any(s == "118003" for _r, s in got)          # maker and SKU in their columns


def test_soft_goods_rule_uses_whole_words(tmp_path):
    (tmp_path / "v2/03-Manufacturing/front").mkdir(parents=True)
    with open(tmp_path / "v2/03-Manufacturing/front/cut-list.csv", "w") as fh:
        fh.write("part_number,name,size_mm,thickness_mm,material,tolerance\n" +
                 "".join("%s,x,2000 x 10,3,EPDM 60 Shore A,±0.5\n" % n for n in ("351001", "351002", "351003", "351004")))
    names = {"351001": "FRONT - SEALED GLAZING PROFILE", "351002": "FRONT - TAPERED BLOCK",
             "351003": "FRONT - FILLER PANEL", "351004": "FRONT - DOOR SEAL"}
    plural = {"351005": "FRONT - DOOR SEALS - SET", "351006": "FRONT - GASKETS - KIT"}
    fs = c_drawings.check_drawings(str(tmp_path), set(names), {}, names)
    got = {f.subject: f.severity for f in fs}
    assert got == {"351001": "severe", "351002": "severe", "351003": "severe"}   # real parts need drawings
    # the PM's policy can rate a missing drawing major while the drawing start is being solved
    (tmp_path / "v2/04-Checks/config").mkdir(parents=True)
    (tmp_path / "v2/04-Checks/config/policy.csv").write_text("key,value,status_source\nmissing_drawing_severity,major,x\n")
    fs = c_drawings.check_drawings(str(tmp_path), set(names), {}, names)
    assert {f.subject: f.severity for f in fs} == {"351001": "major", "351002": "major", "351003": "major"}
    # 351004 is a seal: its full cut-list line defines it (D-89 part 3); plurals count too
    with open(tmp_path / "v2/03-Manufacturing/front/cut-list.csv", "a") as fh:
        fh.write("351005,x,2000 x 10,3,EPDM,±0.5\n351006,x,500 x 10,2,PORON,±0.3\n")
    assert c_drawings.check_drawings(str(tmp_path), set(plural), {}, plural) == []


def _pdf(path, text):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    for line in text.split("\n"):
        page.insert_text((40, y), line)
        y += 20
    doc.save(str(path))


def test_units_rule(tmp_path):
    (tmp_path / "v2/02-Drawings/wall").mkdir(parents=True)
    good = "UNITS: mm\nMATERIAL: EN AW-6063 T6  FINISH: anodised 15 um\nGENERAL TOLERANCES ISO 2768-m"
    bad = "MATERIAL: EN AW-6063 T6  FINISH: anodised 15 um  X (mm) Y (mm)\nGENERAL TOLERANCES ISO 2768-m"
    _pdf(tmp_path / "v2/02-Drawings/wall/211101_P01_A_DWG.pdf", good)
    _pdf(tmp_path / "v2/02-Drawings/wall/211102_P01_B_DWG.pdf", bad)
    fs = c_drawings.check_drawings(str(tmp_path), {"211101", "211102"}, {})
    got = {f.subject: f.message for f in fs if f.rule == "drawing-content"}
    assert "211101" not in got
    assert "units (mm)" in got["211102"]          # a column header in mm is not the title block's UNITS: mm


def test_generated_drawings_count_the_same_and_their_findings_go_to_the_generator(tmp_path):
    # D-112: tools/drawgen makes part drawings from STEP; its PDFs name drawgen in the Creator field
    fitz = pytest.importorskip("fitz")
    d = tmp_path / "v2/02-Drawings/wall"
    d.mkdir(parents=True)
    (tmp_path / "v2/03-Manufacturing/wall").mkdir(parents=True)
    def pdf(name, text, creator):
        doc = fitz.open()
        page = doc.new_page()
        for i, line in enumerate(text.split("\n")):
            page.insert_text((40, 50 + 20 * i), line)
        doc.set_metadata({"creator": creator})
        doc.save(str(d / name))
    full = "UNITS: mm\nMATERIAL: EN AW-6063 T6\nFINISH: mill finish\nGENERAL TOLERANCES: see note 1\nH01  X (mm)  Y (mm)"
    pdf("211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG.pdf", full, "drawgen 0.1 (tools/drawgen)")
    pdf("211103_P01_WALL-PANEL-FRAME-SIDE-UPPER-LH_DWG.pdf", full.replace("GENERAL TOLERANCES: see note 1", ""),
        "drawgen 0.1")
    pdf("211104_P01_WALL-PANEL-FRAME-SIDE-UPPER-RH_DWG.pdf", full.replace("GENERAL TOLERANCES: see note 1", ""),
        "Autodesk Fusion")
    holes = {pn: [sf.Hole(1, (0, 0, 0), (1, 0, 0), 6.6, 1.2, [])] for pn in ("211101", "211103", "211104")}
    fs = c_drawings.check_drawings(str(tmp_path), set(holes), holes)
    got = {(f.rule, f.subject): f for f in fs}
    assert not [k for k in got if k[1] == "211101"]                       # a complete generated drawing counts
    f = got[("drawing-content", "211103")]
    assert f.owner == "Drawing Generator" and "tools/drawgen" in f.fix   # the generator fixes its own drawing
    assert got[("drawing-content", "211104")].owner != "Drawing Generator"
    # a generated table drawing (D-89) one revision behind a part's STEP: the generator regenerates it
    pdf("211301_P01_WALL-SKIN-SIDE-LOWER-LH_DWG.pdf", full + "\nTABULATED: 211301 211302", "drawgen 0.1")
    (tmp_path / "v2/03-Manufacturing/wall/211302_P02_WALL-SKIN-SIDE-LOWER-RH_STEP.step").write_text("")
    fs = c_drawings.check_drawings(str(tmp_path), {"211301", "211302"}, {})
    f = {(f.rule, f.subject): f for f in fs}[("rev-mismatch", "211302")]
    assert f.owner == "Drawing Generator"


def test_generated_drawings_follow_d113_sections_and_no_bent_parts(tmp_path):
    fitz = pytest.importorskip("fitz")
    d = tmp_path / "v2/02-Drawings/base"
    d.mkdir(parents=True)
    full = "UNITS: mm\nMATERIAL: EN AW-6063 T6\nFINISH: mill finish\nGENERAL TOLERANCES: note 1\nH01  X (mm)  Y (mm)"
    def pdf(name, text, creator):
        doc = fitz.open()
        page = doc.new_page()
        for i, line in enumerate(text.split("\n")):
            page.insert_text((40, 50 + 20 * i), line)
        doc.set_metadata({"creator": creator})
        doc.save(str(d / name))
    pdf("111101_P01_BASE-BAND-TUBE-SIDE-LH_DWG.pdf", full, "drawgen 0.1")                 # holes through both walls
    pdf("111102_P01_BASE-BAND-TUBE-SIDE-RH_DWG.pdf", full + "\nSECTION A-A", "drawgen 0.1")
    pdf("111103_P01_BASE-BAND-TUBE-BACK_DWG.pdf", full, "Autodesk Fusion")              # D-113 is the generator's rule
    pdf("111601_P01_BASE-BRACKET_DWG.pdf", full, "drawgen 0.1")                         # a bent bracket
    pns = {"111101", "111102", "111103", "111601"}
    holes = {pn: [sf.Hole(1, (0, 0, 0), (0, 0, 1), 6.6, 2.0, [])] for pn in pns}
    fs = c_drawings.check_drawings(str(tmp_path), pns, holes, two_wall_by_pn={"111101": 2, "111102": 2, "111103": 2},
                                   bends_by_pn={"111601": 2})
    got = {(f.rule, f.subject): f for f in fs}
    assert set(got) == {("no-section", "111101"), ("generated-bent-part", "111601")}
    assert got[("no-section", "111101")].owner == got[("generated-bent-part", "111601")].owner == "Drawing Generator"
    # the STEP facts behind them: a hole axis through both walls of one body; copies of a part counted once
    assert c_drawings.two_wall_axes([sf.Hole(1, (0, 0, 0), (0, 0, 1), 6.6, 2, []),
                                     sf.Hole(1, (0, 0, 40), (0, 0, 1), 6.6, 2, []),
                                     sf.Hole(1, (50, 0, 40), (0, 0, 1), 6.6, 2, [])]) == 1
    a = math.radians(30.0)
    turned = sf.Frame.from_axes((100.0, 0.0, 0.0), (0, 0, 1), (math.cos(a), math.sin(a), 0))
    same = [c_drawings.body_shape(_profile(f, holes=((300.0, 9.53),))) for f in (sf.Frame(), turned)]
    assert same[0] == same[1]                                                            # one part, turned
    assert c_drawings.body_shape(_profile(sf.Frame(), length=500.0, holes=((300.0, 9.53),))) != same[0]


def test_every_part_is_its_own_component_not_a_body(tmp_path):
    # D-120 (build plan rule 2, BP-04): a component that holds several bodies is reported, as ruled
    class FakeStep:
        def __init__(self, rows, solids):
            self.rows, self.solids = rows, solids
        def instances(self):
            return [{"pd": pd, "solid": sid, "part_number": pn, "name": name} for pd, sid, pn, name in self.rows]
        def solid(self, sid):
            return self.solids[sid]
    def body(sid, name, d):
        so = sf.Solid(sid, name)
        so.holes = [sf.Hole(sid, (0, 0, 0), (0, 0, 1), d, 2.0, [])]
        return so
    names = ["RAIL - TOP", "STILE - FRONT", "STILE - MID 1", "STOP WASHER", "STOP WASHER - 2", "SPIGOT",
             "HOLD PULL SPACE - OUTSIDE", "HOLD PULL SPACE - POD SIDE", "L1 ROUTE", "G GROMMET PAIR", "RIVNUT",
             "RIVET NUT M6 - ENVELOPE"]
    dias = [6.6, 9.53, 9.53, 10.5, 10.5, 8.0, 1.0, 1.0, 1.0, 2.0, 9.5, 9.5]
    solids = {i + 1: body(i + 1, n, d) for i, (n, d) in enumerate(zip(names, dias))}
    frame, washer = "211101 WALL - PANEL FRAME - SIDE LOWER - LH", "831002 HARDWARE - STOP WASHER"
    rows = [(10, 1, "211101", frame), (10, 2, "211101", frame), (10, 3, "211101", frame),   # a frame: 3 bodies
            (20, 4, "831002", washer), (20, 5, "831002", washer),                           # 2 copies as bodies
            (30, 6, "831001", "831001 SPIGOT"), (30, 6, "831001", "831001 SPIGOT"),       # one component placed twice
            (40, 7, "368103", "368103 FRONT - DOOR PULL PAIR - HOLD"), (40, 8, "368103", "x - HOLD"),   # HOLD space
            (50, 9, "710011", "710011 ELECTRICAL - HARNESS"), (50, 10, "710011", "y"),     # route bodies (D-92)
            (60, 11, "838003", "838003 RIVET NUT"), (60, 12, "838003", "838003 RIVET NUT"),   # a rivnut, its ENVELOPE
            (70, 7, "NO-PN-HOLD-H03", "HOLD - CLIP ZONES"), (70, 8, "NO-PN-HOLD-H03", "HOLD - CLIP ZONES")]
    path = str(tmp_path / "v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step")
    fake = FakeStep(rows, solids)
    got = {f.subject: f for f in c_parts.check_components(str(tmp_path), [path], lambda p: fake)}
    assert set(got) == {"211101", "831002"}
    assert "3 bodies of 2 different shapes" in got["211101"].message and got["211101"].owner == "WALL"
    assert got["211101"].severity == "major" and "assembly" in got["211101"].fix
    assert "copies of one part" in got["831002"].message and "place it 2 times" in got["831002"].fix
    assert got["831002"].owner == "WALL"           # WALL placed the Joints Engineer's washer: WALL fixes its model


def test_a_plain_strip_passes_on_its_full_parts_list_row(tmp_path):
    # D-125, extending D-89: a plain straight-cut strip or sheet with no features needs no drawing when its row gives
    # material and grade, thickness, length, width, finish and tolerance. INTERIOR's diffuser strip 811205 is the first
    strip = _profile(sf.Frame(), length=991.0, w=28.0, h=1.5, t=None)
    sides = c_drawings.cuboid_sides(strip)
    assert sides == pytest.approx((1.5, 28.0, 991.0)) and c_drawings.is_strip(sides)
    assert c_drawings.cuboid_sides(_profile(sf.Frame(), length=991.0, w=28.0, h=1.5, t=None,
                                            holes=((300.0, 5.0),))) is None              # a hole: not plain
    assert c_drawings.cuboid_sides(_profile(sf.Frame(), w=40.0, h=40.0, t=2.0)) is None  # a tube
    assert c_drawings.cuboid_sides(_profile(sf.Frame(), w=30.0, h=3.0, t=None, chamfer=1.0)) is None
    assert not c_drawings.is_strip((20.0, 20.0, 500.0))                                  # a square bar
    d = tmp_path / "v2/03-Manufacturing/interior"
    d.mkdir(parents=True)
    row = {"part_number": "811205", "name": "INTERIOR - LIGHT SHELF - DIFFUSER RH", "kind": "MP",
           "material": "Opal polycarbonate (grade HOLD: picked with ELECTRICAL's down-light strips)",
           "finish": "opal, as supplied", "process": "cut to length",
           "size_mm": "991.0 long, section 28.0 x 1.5, 1.5 sheet", "tolerance": "±0.5 on cut sizes (assumption)"}
    def found(**change):
        _write_csv(d / "810000_P01_INTERIOR-PARTS-LIST_BOM.csv", [dict(row, **change)])
        fs = c_drawings.check_drawings(str(tmp_path), {"811205"}, {}, {"811205": row["name"]},
                                       cuboid_by_pn={"811205": sides})
        return " ".join(f.message for f in fs)
    assert found() == ""                                                   # the full row stands in for a drawing
    assert "D-125" in found(finish="") and "finish" in found(finish="")
    assert "the material's grade" in found(material="polycarbonate")
    assert "1.5 x 28 x 991" in found(size_mm="980.0 long, section 28.0 x 1.5")   # not the STEP's length
    assert "tolerance on the length and the width" in found(tolerance="")
    assert "hole" in found(process="cut to length, one cable hole")
    # the tolerance covers both cut sizes (PM, 2026-11-01); the thickness takes the sheet's own, as its grade names it
    assert "tolerance on the width" in found(tolerance="cut length +/-1 (assumption)")       # 811205's line today
    assert found(tolerance="cut length +/-1, width as supplied (assumption)") == ""          # a bought strip
    assert found(tolerance="cut length +/-1 (assumption)", size_mm="991.0 long, 28.0 wide (width as supplied), 1.5 "
                 "sheet") == ""
    assert found(tolerance="ISO 2768-m") == "" and found(tolerance="length ±1; width ±0.5") == ""
    assert found(tolerance="cut +/-0.5") == ""                                               # no size named: both
    assert "tolerance on the length and the width" in found(tolerance="thickness ±0.1, hole positions ±0.2")
    assert c_drawings.tolerance_cover(["cut length +0/-0.5", "end angle ±0.25°"], []) == {"length"}
    assert c_drawings.tolerance_cover(["bent ±0.5"], ["width as supplied"]) == {"width"}
    assert c_drawings.tolerance_cover(["+0.2/0"], []) == {"length", "width"}            # one-sided, no size named
    # a bar or block isn't a strip: it keeps its drawing whatever its row says
    assert "D-125" not in " ".join(f.message for f in c_drawings.check_drawings(
        str(tmp_path), {"811205"}, {}, {"811205": row["name"]}, cuboid_by_pn={"811205": (20.0, 20.0, 500.0)}))


def test_the_strip_list_keeps_one_plain_thin_shape_per_part():
    # D-125's per-part strip list, shared with the release checklist: one shape per part across every STEP, a plain
    # rectangular block, thin enough to be a strip or sheet
    class FakeStep:
        def __init__(self, rows):
            self.rows = rows
        def instances(self):
            return [{"solid": i, "part_number": pn} for i, (pn, _so) in enumerate(self.rows)]
        def solid(self, sid):
            return self.rows[sid][1]
    a = math.radians(30.0)
    turned = sf.Frame.from_axes((100.0, 50.0, 0.0), (0, 0, 1), (math.cos(a), math.sin(a), 0))
    strip = lambda frame=sf.Frame(), length=991.0: _profile(frame, length=length, w=28.0, h=1.5, t=None)
    files = {
        "a.step": FakeStep([("811205", strip()),                                    # a strip ...
                            ("111999", _profile(sf.Frame(), length=100.0, w=50.0, h=40.0, t=None)),   # a thick block
                            ("211999", strip(length=500.0)),                        # two shapes under one number
                            ("831999", strip(length=60.0)), ("831999", strip(turned, length=60.0)),   # copies, turned
                            ("211998", _profile(sf.Frame(), w=40.0, h=40.0, t=2.0))]),                # a tube
        "b.step": FakeStep([("811205", strip(turned)),                              # ... the same strip in a 2nd file
                            ("211999", strip(length=300.0))]),
    }
    got = c_drawings.strip_sides(list(files), files.get)
    assert got == {"811205": pytest.approx((1.5, 28.0, 991.0)), "831999": pytest.approx((1.5, 28.0, 60.0))}


def test_run_with_ref_leaves_no_export_behind():
    import glob
    import subprocess
    import tempfile
    import run_checks
    sha = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    pattern = os.path.join(tempfile.gettempdir(), "checks-%s-*" % sha)
    before = set(glob.glob(pattern))
    run_checks.main(["--ref", "HEAD", "--json"])
    assert set(glob.glob(pattern)) == before


def test_hole_size_rule_only_for_holes_facing_a_rivnut():
    rules = [{"id": "M6-CLEARANCE-7", "min_dia_mm": "6.3", "max_dia_mm": "6.95", "severity": "major",
              "status_source": "F-009", "message": "m", "fix": "f"}]
    def body(label, pn, holes):
        b = _B(label, None, pn, holes)
        b.file = label + ".step"
        return b
    frame = body("frame", "211101", [sf.Hole(1, (0.0, 0.0, 0.0), (0, 0, 1), 6.6, 1.2, [])])
    band = body("band", "111101", [sf.Hole(2, (0.0, 0.0, -3.4), (0, 0, 1), 9.53, 2.0, [])])
    rivet = body("trim", "211301", [sf.Hole(3, (100.0, 0.0, 0.0), (0, 0, 1), 6.5, 1.0, [])])     # a 6.4 blind rivet's hole
    fs = c_geometry.check_hole_sizes(ROOT, "assembly", [frame, band, rivet], hole_rules=rules)
    assert [f.evidence["dia_mm"] for f in fs] == [6.6]                 # only the hole facing the rivnut
    assert c_geometry.check_hole_sizes(ROOT, "assembly", [frame, rivet], hole_rules=rules) == []

def test_update_refuses_a_revision_label_for_another_tree(capsys):
    import run_checks
    code = run_checks.main(["--update", "--rev", "0000000"])
    assert code == 2 and "refusing --update" in capsys.readouterr().err


def test_cad_and_parts_list_names_must_match(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    row = {"part_number": "211101", "name": "WALL - PANEL FRAME - SIDE LOWER - LH", "name_vi": "x", "material": "EN AW-6063 T6",
           "finish": "mill finish", "qty": "1", "mass_kg": "2", "status": "calculation", "source": "CAD"}
    _write_csv(d / "parts.csv", [row, dict(row, part_number="211102", name="WALL - PANEL FRAME - SIDE UPPER - LH")])
    plists = c_parts.find_parts_lists(str(tmp_path))
    prods = {"211101": {"files": {"a.step"}, "count": 1, "name": "211101 WALL - PANEL FRAME - SIDE LOWER - LH"},
             "211102": {"files": {"a.step"}, "count": 1, "name": "211102 WALL - FRAME - UPPER"}}
    got = {(f.rule, f.subject) for f in c_parts.check_cad_match(str(tmp_path), plists, prods)}
    assert ("name-mismatch", "211102") in got and ("name-mismatch", "211101") not in got


def test_parts_list_rows_are_matched_only_against_their_own_teams_cad(tmp_path):
    # WALL has exported STEP files, BASE hasn't yet; the master BOM lists every team's parts
    row = {"part_number": "211101", "name": "WALL - PANEL FRAME - SIDE LOWER - LH", "name_vi": "x", "material": "EN AW-6063 T6",
           "finish": "mill finish", "qty": "1", "mass_kg": "2", "status": "calculation", "source": "CAD"}
    for folder, rows in (("v2/03-Manufacturing/wall", [row, dict(row, part_number="211301", name="WALL - SKIN - SIDE LOWER - LH")]),
                         ("v2/03-Manufacturing/base", [dict(row, part_number="111401", name="BASE - FLOOR PANEL - F1")])):
        (tmp_path / folder).mkdir(parents=True)
        _write_csv(tmp_path / folder / "parts.csv", rows)
    (tmp_path / "v2/04-BOM").mkdir(parents=True)
    _write_csv(tmp_path / "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv",
               [dict(row, part_number="100000", name="POD - SPACESHIP"), dict(row, part_number="210000", name="WALL")])
    plists = c_parts.find_parts_lists(str(tmp_path))
    prods = {"211101": {"files": {"v2/03-Manufacturing/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_STEP.step"},
                        "count": 1, "name": "211101 WALL - PANEL FRAME - SIDE LOWER - LH"}}
    got = {(f.rule, f.subject) for f in c_parts.check_cad_match(str(tmp_path), plists, prods)}
    assert ("bom-not-in-cad", "211301") in got                       # WALL's own list, WALL has STEP files
    assert not {s for r, s in got if r == "bom-not-in-cad"} & {"111401", "100000", "210000"}


def test_bolt_patterns_across_assemblies_must_match():
    def body(label, file, holes):
        b = _B(label, None, "x", holes)
        b.file = file
        return b
    wall = body("wall rail", "wall.step", [sf.Hole(1, (-1227.0, y, 111.0), (0, 0, 1), 6.6, 1.2, []) for y in (-452.2, 278.8)])
    band = body("band tube", "base.step", [sf.Hole(2, (-1227.0, y, 109.0), (0, 0, 1), 9.53, 2.0, []) for y in (-425.0, 278.3)])
    fs = c_geometry.check_unmatched(ROOT, "assembly", [wall, band])
    offs = sorted(round(f.evidence["offset_mm"], 1) for f in fs)
    assert offs == [27.2, 27.2]                 # the -452.2 / -425 pair, reported on both sides; 278.8 / 278.3 matches
    assert all(f.severity == "severe" for f in fs)


def test_a_bolt_into_its_own_files_rivnut_is_not_paired_with_the_next_files_bolt_line():
    # FRONT #105: DR's access panel (clearance Ø7.0) bolts into DR's own rivnuts on the same axis; WALL's bolt line,
    # 36 mm away, goes into DR's frame. Neither is a bolt pattern that doesn't match.
    def body(label, file, holes):
        b = _B(label, None, "x", holes)
        b.file = file
        return b
    ax, zs = (1.0, 0.0, 0.0), (300.0, 650.0, 1000.0)
    panel = body("DR ACCESS PANEL", "dr.step", [sf.Hole(1, (1188.0, -645.0, z), ax, 7.0, 3.0, []) for z in zs])
    rivnuts = body("DR RIVNUT", "dr.step", [sf.Hole(2, (1192.0, -645.0, z), ax, 9.53, 2.0, []) for z in zs])
    frame = body("DR FRAME", "dr.step", [sf.Hole(3, (1195.0, -609.0, z), ax, 9.53, 2.0, []) for z in zs])
    wall = body("WALL R1", "wall.step", [sf.Hole(4, (1199.0, -609.0, z), ax, 6.6, 1.2, []) for z in zs])
    assert c_geometry.check_unmatched(ROOT, "assembly", [panel, rivnuts, frame, wall]) == []
    # without its own rivnuts the access panel's holes pair with the wall's bolt line and are reported
    fs = c_geometry.check_unmatched(ROOT, "assembly", [panel, frame, wall])
    assert [round(f.evidence["offset_mm"]) for f in fs] == [36, 36, 36]
    assert all("DR ACCESS PANEL" in f.subject for f in fs)
    # a rivnut of its own 10 mm off the hole's axis isn't its partner: still reported
    off = body("DR RIVNUT", "dr.step", [sf.Hole(2, (1192.0, -635.0, z), ax, 9.53, 2.0, []) for z in zs])
    got = {f.subject for f in c_geometry.check_unmatched(ROOT, "assembly", [panel, off, frame, wall])}
    assert {"assembly DR ACCESS PANEL hole Ø7.0 at X 1188 Y -645 Z %d" % z for z in zs} <= got


def test_shell_reports_a_split_slot_and_ignores_the_decided_seam():
    side = [_B("left", (-1250, -645, 110, -1204, 850, 2400)), _B("right", (1204, -645, 110, 1250, 850, 2400)),
            _B("roof", (-1250, -645, 2354, 1250, 850, 2400))]
    # back wall: a 15 mm horizontal slot (Z 1200 to 1215) with a small bracket over part of its lower side
    slot = [_B("lower", (-1250, 804, 110, 1250, 850, 1200)), _B("upper", (-1250, 804, 1215, 1250, 850, 2354)),
            _B("bracket", (-100, 804, 1199, 100, 850, 1208))]
    gaps = c_geometry.shell_gaps(side + slot)
    assert len(gaps) == 1 and gaps[0]["zone"] == "back"
    assert gaps[0]["b"][0] == pytest.approx(1200, abs=0.01) and gaps[0]["b"][1] == pytest.approx(1215, abs=0.01)
    # the same back wall with the decided 2.26 mm seam instead: closed
    seam = [_B("lower", (-1250, 804, 110, 1250, 850, 1200)), _B("upper", (-1250, 804, 1202.26, 1250, 850, 2354))]
    assert c_geometry.shell_gaps(side + seam) == []
    # a 2.6 mm gap is wider than the seam: reported
    wide = [_B("lower", (-1250, 804, 110, 1250, 850, 1200)), _B("upper", (-1250, 804, 1202.6, 1250, 850, 2354))]
    assert len(c_geometry.shell_gaps(side + wide)) == 1


def test_door_swing_steps_leave_no_big_unchecked_gap():
    rows = c_parts.read_csv(os.path.join(ROOT, "v2/04-Checks/config/door-swing.csv"))
    for r in rows:
        travel = math.radians(float(r["step_deg"])) * 1176.0          # the door's free edge (D-46 width)
        assert travel <= 12.0, travel


def test_soft_goods_by_head_noun():
    from common import is_soft, head_noun
    assert head_noun("BASE - SEAL HOLDER - LH") == "HOLDER" and not is_soft("BASE - SEAL HOLDER - LH")
    assert is_soft("LINING - FILL - CEILING - BAY A") and is_soft("FRONT - DOOR SEALS - SET")
    assert is_soft("FRONT - GLAZING U-SEAL - BOHLE BO5201735") and is_soft("FRONT - GLASS-TO-GLASS SEAL 180 - BOHLE")
    assert not is_soft("FRONT - SEALED GLAZING PROFILE") and not is_soft("FRONT - FILLER PANEL")
    assert is_soft("LINING - FELT - CEILING", ("FELT",)) and not is_soft("LINING - FELT - CEILING", ("FILL",))


def test_current_skeleton_on_main_passes_the_shell_and_gap_rules():
    import glob
    cur = sorted(glob.glob(os.path.join(ROOT, "v2/03-Manufacturing/skeleton/*.step")))
    if not cur or cur[-1].endswith("P03_POD-SKELETON_STEP.step"):
        pytest.skip("no later skeleton in this checkout")
    bodies = c_geometry.bodies_of(ROOT, cur[-1])
    assert c_geometry.shell_gaps(bodies, root=ROOT) == []
    assert c_geometry.check_gap_rules(ROOT, "skeleton", bodies, c_geometry.load_gap_rules(ROOT)) == []


def test_missing_drawing_follows_the_screen_lock(monkeypatch, tmp_path):
    (tmp_path / "v2/04-Checks/config").mkdir(parents=True)
    (tmp_path / "v2/04-Checks/config/policy.csv").write_text("key,value,status_source\nmissing_drawing_severity,auto-screen-lock,D-84\n")
    monkeypatch.setattr(c_drawings, "screen_locked", lambda: True)
    assert c_drawings.missing_drawing_severity(str(tmp_path)) == "major"
    monkeypatch.setattr(c_drawings, "screen_locked", lambda: False)
    assert c_drawings.missing_drawing_severity(str(tmp_path)) == "severe"
    monkeypatch.setattr(c_drawings, "screen_locked", lambda: None)
    assert c_drawings.missing_drawing_severity(str(tmp_path)) == "severe"


def test_shipping_reads_the_packing_list_when_there_is_one(tmp_path):
    d = tmp_path / "v2/07-Packaging"
    d.mkdir(parents=True)
    (d / "910001_P01_PALLET-1-48X40_PKG.svg").write_text("<svg/>")
    (d / "910002_P01_PALLET-2-96X48_PKG.svg").write_text("<svg/>")
    rows = [{"label": "1-01", "part_number": "211101", "name": "WALL - PANEL", "pallet": "1", "kg": "11.3",
             "size_mm": "1492.74 x 1142.74 x 46", "glass": "no", "kg_status": "calculation"},
            {"label": "2-01", "part_number": "360002", "name": "FRONT - FIXED GLASS UNIT", "pallet": "2", "kg": "29.6",
             "size_mm": "2033 x 1031 x 12", "glass": "yes", "kg_status": "calculation"},
            {"label": "1-02", "part_number": "350003", "name": "FRONT - DECOR BLOCK - DR", "pallet": "1", "kg": "18.1",
             "size_mm": "2290 x 1016 x 205", "glass": "no", "kg_status": "calculation"}]
    _write_csv(d / "910000_P01_PACKING-LIST_BOM.csv", rows)
    fs, rep, src = c_parts.check_shipping(str(tmp_path))
    assert src.endswith("PACKING-LIST_BOM.csv")
    got = {(f.rule, f.subject) for f in fs}
    assert ("pallet-fit", "1-02") in got                 # a 2290 mm block put on the 48 x 40 pallet
    assert not any(s in ("1-01", "2-01") for _r, s in got)  # the glass unit is exempt from 20 kg; both fit


def test_shared_hardware_drawings_go_to_the_joints_engineer_but_list_rows_stay_with_the_team():
    from common import owner_for
    assert owner_for("", "831001") == "Joints Engineer"                  # the spigot's drawing: no team path
    assert owner_for("v2/03-Manufacturing/wall/210101_P01_X_BOM.csv", "838003") == "WALL"   # WALL's own row
    assert owner_for("", "211101") == "WALL" and owner_for("", "999999") == "PM"


def test_d89_a_tabulated_drawing_covers_the_numbers_it_lists(tmp_path):
    d = tmp_path / "v2/02-Drawings/wall"
    d.mkdir(parents=True)
    (tmp_path / "v2/03-Manufacturing/wall").mkdir(parents=True)
    base = "UNITS: mm\nMATERIAL: EN AW-6063 T6  FINISH: mill finish\nGENERAL TOLERANCES ISO 2768-m\n"
    _pdf(d / "211101_P01_WALL-PANEL-FRAME-SIDE-LOWER_DWG.pdf",
         base + "TABULATED DRAWING\nPART NO | SIDE\n211101 | LH\n211102 | RH\nRIVNUT 838003 IN EVERY H01")
    _pdf(d / "210101_P01_WALL-PANEL-ASSY_DWG.pdf", base + "TABULATED\nPARTS LIST: 211301 SKIN")
    names = {"211101": "WALL - PANEL FRAME - SIDE LOWER - LH", "211102": "WALL - PANEL FRAME - SIDE LOWER - RH",
             "211301": "WALL - SKIN - SIDE LOWER - LH", "210101": "WALL - PANEL ASSY - SIDE LOWER - LH"}
    got = {(f.rule, f.subject) for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert ("no-drawing", "211102") not in got           # listed in 211101's tabulated drawing
    assert ("no-drawing", "211301") in got               # an assembly drawing's parts list doesn't cover a part
    # the covered part's CAD at another revision: the drawing is out of date for it
    (tmp_path / "v2/03-Manufacturing/wall/211102_P02_WALL-PANEL-FRAME-SIDE-LOWER-RH_STEP.step").write_text("x")
    got = {(f.rule, f.subject) for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert ("rev-mismatch", "211102") in got
    # without the word TABULATED, a number in the text is only a reference
    _pdf(d / "211101_P01_WALL-PANEL-FRAME-SIDE-LOWER_DWG.pdf", base + "MIRROR OF 211102")
    got = {(f.rule, f.subject) for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert ("no-drawing", "211102") in got


def test_d89_felt_and_fill_rectangles_pass_on_a_complete_cut_list_row(tmp_path):
    m = tmp_path / "v2/03-Manufacturing/wall"
    m.mkdir(parents=True)
    with open(m / "510000_P01_LINING-CUT-LIST_SPEC.csv", "w") as fh:
        fh.write("part_number,name,size_mm,material,tolerance_mm\n"
                 "511301,felt,1445 x 1142.74 x 9,PET felt 9 mm Dark Gray,±1.0\n"
                 "511401,fill,1100 x 1050 x 40,PET fill 24 kg/m3,\n"
                 "511302,felt,1445 x 1142.74 x 9,PET felt 9 mm Dark Gray,±1.0\n")
    (m / "511303_P01_LINING-FELT-BACK_DXF.dxf").write_text("x")
    names = {"511301": "LINING - FELT - SIDE LOWER - LH", "511401": "LINING - FILL - SIDE LOWER - BAY A",
             "511302": "LINING - FELT - SIDE LOWER - RH", "511303": "LINING - FELT - BACK LOWER - LH"}
    holes = {"511302": [sf.Hole(1, (0, 240.5, 1180.0), (1, 0, 0), 60.0, 9.0, [])]}
    fs = {f.subject: f.message for f in c_drawings.check_drawings(str(tmp_path), set(names), holes, names)}
    assert "511301" not in fs                              # complete row, plain rectangle: no drawing needed
    assert "doesn't give tolerance" in fs["511401"]
    assert "isn't a plain rectangle" in fs["511302"]       # the felt has a hole: it needs a drawing
    assert "no cut list or parts list has a row" in fs["511303"]   # a DXF alone doesn't clear felt
    # a body with pockets (more than a block's 6 faces) isn't a plain rectangle either
    fs = {f.subject: f.message for f in c_drawings.check_drawings(str(tmp_path), {"511301"}, {}, names,
                                                                   {"511301": [6, 22]})}
    assert "22 faces" in fs["511301"]


def test_d89_a_parts_list_row_serves_as_the_cut_list(tmp_path):
    # PM ruling 2026-11-01: a parts-list row that gives part number, size, material and tolerance serves as
    # the cut list; a row that names pockets keeps the drawing; other soft goods need thickness, or a DXF
    m = tmp_path / "v2/03-Manufacturing/wall"
    m.mkdir(parents=True)
    (m / "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv").write_text(
        "part_number,name,material,size_mm,tolerance\n"
        "511301,LINING - FELT - SIDE LOWER - LH,PET felt 9 mm Dark Gray,9 x 1442 x 1139.74,±1 on length and width\n"
        "211501,WALL - CAVITY FILL - SIDE LOWER - LH,PET fill 40 mm,1102.7 x 344.9 x 40 with 60 x 60 pockets,±2\n"
        "513401,LINING - EDGE GASKET - SIDE LOWER,PORON 4701-40,1445 x 10,±0.5\n")
    names = {"511301": "LINING - FELT - SIDE LOWER - LH", "211501": "WALL - CAVITY FILL - SIDE LOWER - LH",
             "513401": "LINING - EDGE GASKET - SIDE LOWER"}
    fs = {f.subject: f.message for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert "511301" not in fs and "names pockets" in fs["211501"]
    assert "doesn't give thickness" in fs["513401"]                 # a gasket's line must give its thickness
    (m / "513401_P01_LINING-EDGE-GASKET-SIDE-LOWER_DXF.dxf").write_text("x")
    fs = {f.subject for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert "513401" not in fs                                       # or a DXF gives its outline (D-89 part 3)


def test_duplicate_number_ignores_hyphens_and_case_but_not_words(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    row = {"part_number": "848011", "name": "SEALS - HOOK-AND-LOOP - 25 MM", "name_vi": "x", "material": "VELCRO PS14",
           "finish": "none", "qty": "1", "mass_kg": "0.01", "status": "HOLD", "source": "register"}
    _write_csv(d / "a.csv", [row, dict(row, part_number="848012", name="SEALS - CASSETTE EDGE GASKET - 10 X 3.18")])
    _write_csv(d / "b.csv", [dict(row, name="SEALS - Hook and loop - 25 MM"),
                             dict(row, part_number="848012", name="SEALS - CASSETTE EDGE SEAL - 10 X 2.0")])
    got = {f.subject for f in c_parts.check_parts_lists(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)))
           if f.rule == "duplicate-number"}
    assert got == {"848012"}


def test_an_accepted_edge_distance_holds_only_as_ruled():
    # glide doubler 111601: 36 wide; ruling: at least 52 long (ends 26 = 2d), hole centred (18 to each long side)
    def plate(length, offset):
        x0, x1, y0, y1 = -length / 2, length / 2, -18.0 - offset, 18.0 - offset
        rim = (sf.Frame(), 6.5, (6.5, 0, 0), (6.5, 0, 0), True)          # the hole's full circle in this face
        face = sf.Face(1, "plane", (0, 0, 0), (0, 0, 1), None, True, [], [rim],
                       [((x0, y0, 0), (x1, y0, 0)), ((x1, y0, 0), (x1, y1, 0)), ((x1, y1, 0), (x0, y1, 0)),
                        ((x0, y1, 0), (x0, y0, 0))])
        so = sf.Solid(1, "GLIDE DOUBLER")
        so.faces = [face]
        return so
    hole = sf.Hole(1, (0, 0, 0), (0, 0, 1), 13.0, 3.0, [])
    rows = [{"part_number": "111601", "hole_dia_mm": "13.0", "min_edge_mm": "18.0", "max_short_edges": "2"}]
    def accepted(length, offset):
        edges = sf.free_edge_distances(plate(length, offset), hole)
        return c_geometry._edge_accepted(rows, hole, edges, 26.0) is not None
    assert accepted(52.0, 0.0)                 # as ruled
    assert not accepted(30.0, 0.0)             # ends 15 mm: the ruling wants 26
    assert not accepted(52.0, 3.0)             # off centre: one side at 15 mm


def _profile(frame, length=600.0, w=40.0, h=40.0, t=2.0, holes=(), chamfer=0.0):
    """A straight rectangular profile along its own X (0 to `length`), placed by `frame`: a tube with walls `t`
    thick, or a solid bar when t is None. Holes (x, d) go down through its top wall, centred across it; `chamfer`
    cuts a 45 degree chamfer that many mm on its outer top-left corner. Returns the solid."""
    P = frame.point
    y0, y1, z0, z1, c = -w / 2, w / 2, -h / 2, h / 2, chamfer
    outer = [(y0, z0), (y1, z0), (y1, z1)] + ([(y0 + c, z1), (y0, z1 - c)] if c else [(y0, z1)])
    inner = [] if t is None else [(y0 + t, z0 + t), (y1 - t, z0 + t), (y1 - t, z1 - t), (y0 + t, z1 - t)]
    lo = z0 if t is None else z1 - t                                    # the bottom of the holes
    rim = lambda x, z, d: _arc(P((x, 0.0, z)), frame.vector((0, 0, 1)), frame.vector((1, 0, 0)), d / 2, 0, 0)
    s = sf.Solid(7, "PROFILE")
    fid = 1
    for poly, sign in ((outer, 1), (inner, -1)):
        for i in range(len(poly)):
            (ya, za), (yb, zb) = poly[i], poly[(i + 1) % len(poly)]
            n = sf.norm((0.0, sign * (zb - za), -sign * (yb - ya)))      # out of the material
            lines = [(P((0, ya, za)), P((0, yb, zb))), (P((length, ya, za)), P((length, yb, zb))),
                     (P((0, ya, za)), P((length, ya, za))), (P((0, yb, zb)), P((length, yb, zb)))]
            arcs = []
            if abs(abs(n[2]) - 1.0) < 1e-9 and min(ya, yb) < 0.0 < max(ya, yb) and za in (z1, lo):
                arcs = [rim(x, za, d) for x, d in holes]               # the faces the holes go through
            pts = [p for ln in lines for p in ln] + [a[2] for a in arcs]
            s.faces.append(sf.Face(fid, "plane", P((0, ya, za)), frame.vector(n), None, True, pts, arcs, lines))
            fid += 1
    for x, nx in ((0.0, -1), (length, 1)):                               # the two end faces
        lines = [(P((x, *poly[k])), P((x, *poly[(k + 1) % len(poly)]))) for poly in (outer, inner)
                 for k in range(len(poly))]
        s.faces.append(sf.Face(fid, "plane", P((x, y0, z0)), frame.vector((nx, 0, 0)), None, True,
                               [p for ln in lines for p in ln], [], lines))
        fid += 1
    for x, d in holes:                                                   # the holes' walls
        top, bottom = rim(x, z1, d), rim(x, lo, d)
        s.faces.append(sf.Face(fid, "cylinder", P((x, 0.0, lo)), frame.vector((0, 0, 1)), d / 2, False,
                               [top[2], bottom[2]], [top, bottom], []))
        fid += 1
    pts = list(s.points())
    s.box = tuple(min(p[k] for p in pts) for k in range(3)) + tuple(max(p[k] for p in pts) for k in range(3))
    s.thickness = sf._sheet_thickness(s)
    s.holes = sf._holes(s)
    return s


def test_a_tube_set_at_an_angle_keeps_its_corners_out_of_the_edge_distance():
    # FRONT #105: DL's spigot hole in a diagonal bottom tube. Its box isn't long in any axis, so a direction read
    # from the box missed that the tube's corners are where the next wall carries on, and called them free edges.
    a = math.radians(30.0)
    for frame in (sf.Frame(), sf.Frame.from_axes((100.0, 200.0, 50.0), (0, 0, 1), (math.cos(a), math.sin(a), 0))):
        along = frame.vector((1.0, 0.0, 0.0))
        tube = _profile(frame, holes=((300.0, 17.0), (25.0, 17.0)))
        assert tube.thickness == pytest.approx(2.0) and len(tube.holes) == 2
        mid, end = sorted(tube.holes, key=lambda h: -abs(sf.dot(sf._sub(h.center, frame.o), along) - 25.0))
        # the middle hole: 20 mm to each corner (under 2 x 17), 300 mm to the tube's ends, which are its free edges
        assert sf.edge_distance(tube, mid) == (pytest.approx(300.0), "free edge")
        assert all(abs(sf.dot(e[1], along)) < 1e-6 for e in sf.free_edge_distances(tube, mid))
        # the hole 25 mm from the end still fires the rule
        assert sf.edge_distance(tube, end)[0] == pytest.approx(25.0)
        # a 1 mm chamfer on the corner next to the hole (CEILING's seam members, 19 mm from a Ø9.53 hole) is no
        # free edge either: the next wall carries on beyond it
        cham = _profile(frame, holes=((300.0, 9.53),), chamfer=1.0)
        assert sf.edge_distance(cham, cham.holes[0]) == (pytest.approx(300.0), "free edge")
        # a flat bar's long edges are free edges, chamfered or not (box-read, a long bar hid them as a profile)
        bar = _profile(frame, w=30.0, h=3.0, t=None, holes=((300.0, 6.6),), chamfer=1.0)
        assert bar.thickness == pytest.approx(3.0)
        assert sf.edge_distance(bar, bar.holes[0]) == (pytest.approx(14.0), "free edge")
    # a block the hole goes 40 mm through: its sides are free edges, though they are wider than a sheet's edge
    block = _plate_with_hole(t=40.0, hole_x=5.0, d=6.6)
    assert block.thickness is None and sf.edge_distance(block, block.holes[0]) == (pytest.approx(5.0), "free edge")


def test_flat_plate_tells_plain_sheet_parts_from_machined_ones():
    s = sf.StepFile(os.path.join(os.path.dirname(__file__), "fixtures", "bolt-joints.step"))
    seen = {}
    for inst in s.instances():
        seen.setdefault(inst["name"], sf.flat_plate(s.solid(inst["solid"])))
    plate = next(v for k, v in seen.items() if "BOLT SIDE A" in k)
    assert plate[0] and abs(plate[1] - 1.2) < 0.01               # a 1.2 mm wall with a through-hole
    block = next(v for k, v in seen.items() if "FILL E" in k)
    assert not block[0] and "isn't a sheet" in block[2]          # a 90 x 120 x 73 block is no sheet
    rivnut = next(v for k, v in seen.items() if "RIVNUT - M6 A" in k)
    assert not rivnut[0] and "across 9.5" in rivnut[2]           # a turned tube, longer than it is wide
    # a 3 mm plate with a 1.5 mm deep pocket: a third level through the thickness
    def face(normal, pts):
        return sf.Face(1, "plane", pts[0], normal, None, True, pts, [], [])
    so = sf.Solid(1, "POCKETED PLATE")
    so.faces = [face((0, 0, -1), [(0, 0, 0), (100, 0, 0), (100, 50, 0), (0, 50, 0)]),
                face((0, 0, 1), [(0, 0, 3), (100, 0, 3), (100, 50, 3), (0, 50, 3)]),
                face((0, 0, 1), [(40, 10, 1.5), (60, 10, 1.5), (60, 30, 1.5), (40, 30, 1.5)]),
                face((1, 0, 0), [(100, 0, 0), (100, 50, 0), (100, 50, 3), (100, 0, 3)]),
                face((0, 1, 0), [(0, 50, 0), (100, 50, 0), (100, 50, 3), (0, 50, 3)])]
    ok, _t, why = sf.flat_plate(so)
    assert not ok and "3 levels" in why


def _dxf(path, layers_circles):
    body = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for layer, kind, r in layers_circles:
        if kind == "CIRCLE":
            body += ["0", "CIRCLE", "8", layer, "10", "50", "20", "50", "40", str(r)]
        else:
            body += ["0", "LWPOLYLINE", "8", layer, "90", "4", "10", "0", "20", "0"]
    body += ["0", "ENDSEC", "0", "EOF"]
    path.write_text("\n".join(body) + "\n")


class TestD89FlatSheetParts:
    """D-89 (4), with the release checklist's own cases (v2/00-Control/test_build_release_checklist.py,
    D89FlatSheetParts) so both tools agree; then what only the files show."""
    LIST = "v2/03-Manufacturing/front/360000_P01_FRONT_BOM.csv"
    HEAD = "part_number,name,material,thickness_mm,finish,process,tolerance,note"
    GOOD = "361101,FRONT - COVER PLATE,aluminium 5754-H22,2,black anodised AA20,laser cut,ISO 2768-m,"

    def plate(self, tmp_path, line=GOOD, head=HEAD, dxf=True, pn="361101", layers=(("CUT", "LWPOLYLINE", 0),),
              holes=None, flat=None):
        d = tmp_path / "v2/03-Manufacturing/front"
        d.mkdir(parents=True, exist_ok=True)
        (tmp_path / self.LIST).write_text(head + "\n" + line + "\n")
        for f in d.glob("*_DXF.dxf"):
            f.unlink()
        for ext in ("CAD.f3d", "STEP.step"):
            (d / ("%s_P01_FRONT-COVER-PLATE_%s" % (pn, ext))).write_text("x")
        if dxf:
            _dxf(d / ("%s_P01_FRONT-COVER-PLATE_DXF.dxf" % pn), list(layers))
        names = {pn: "FRONT - COVER PLATE"}
        fs = c_drawings.check_drawings(str(tmp_path), {pn}, {pn: holes or []}, names,
                                       flat_by_pn={pn: flat} if flat else None)
        return {f.subject: f.message for f in fs if f.rule == "no-drawing"}

    def test_a_laser_cut_plate_with_its_dxf_and_a_full_row_is_drawn(self, tmp_path):
        assert self.plate(tmp_path) == {}

    def test_each_missing_item_keeps_the_drawing(self, tmp_path):
        assert "361101" in self.plate(tmp_path, dxf=False)
        assert "ISO 2768" in self.plate(tmp_path, self.GOOD.replace("ISO 2768-m", "±0.2"))["361101"]
        assert "finish" in self.plate(tmp_path, self.GOOD.replace("black anodised AA20", ""))["361101"]
        assert "thickness" in self.plate(tmp_path, self.GOOD.replace(",2,", ",,"))["361101"]
        assert "laser, waterjet or router" in self.plate(tmp_path, self.GOOD.replace("laser cut", "punch"))["361101"]

    def test_bent_machined_or_bonded_parts_keep_the_drawing(self, tmp_path):
        for process in ("laser cut, brake bend", "laser cut, tap M6", "CNC router: outline and the seam half-lap",
                        "router cut, then bonded to the frame", "waterjet, countersink 4 holes"):
            assert "361101" in self.plate(tmp_path, self.GOOD.replace("laser cut", '"%s"' % process)), process

    def test_a_mill_finish_is_not_milling(self, tmp_path):
        assert self.plate(tmp_path, self.GOOD.replace("black anodised AA20", "mill finish")) == {}

    def test_thickness_may_sit_in_the_material(self, tmp_path):
        head = "part_number,name,material,finish,process,tolerance"
        line = "361101,FRONT - COVER PLATE,aluminium 5754-H22 2 mm,black anodised AA20,waterjet,ISO 2768-m"
        assert self.plate(tmp_path, line, head) == {}

    def test_an_assembly_always_keeps_its_drawing(self, tmp_path):
        assert "360101" in self.plate(tmp_path, self.GOOD.replace("361101", "360101"), pn="360101")

    # what only the files show
    def test_a_line_on_the_bend_layer_keeps_the_drawing_whatever_the_row_says(self, tmp_path):
        msg = self.plate(tmp_path, layers=(("CUT", "LWPOLYLINE", 0), ("BEND", "LINE", 0)))["361101"]
        assert "draws on BEND; only CUT and MARK pass, so it is folded" in msg

    def test_only_the_cut_and_mark_layers_are_allowed(self, tmp_path):
        assert self.plate(tmp_path, layers=(("CUT", "LWPOLYLINE", 0), ("MARK", "TEXT", 0))) == {}
        for layer in ("POCKET-HALF-DEPTH", "ENGRAVE", "HALF-LAP"):
            msg = self.plate(tmp_path, layers=(("CUT", "LWPOLYLINE", 0), (layer, "LINE", 0)))["361101"]
            assert "draws on %s; only CUT and MARK pass" % layer in msg, layer

    # the release checklist's own layer cases (test_build_release_checklist.py, D-89 (4) layers), so both
    # tools read a DXF the same way
    @staticmethod
    def dxf_doc(*entities):
        head = ["0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER"]
        for name in ("CUT", "BEND", "MARK"):
            head += ["0", "LAYER", "2", name, "70", "0"]
        head += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
        body = []
        for typ, layer in entities:
            body += ["0", typ, "8", layer, "10", "0.0", "20", "0.0", "11", "100.0", "21", "0.0"]
        return "\n".join(head + body + ["0", "ENDSEC", "0", "EOF"]) + "\n"

    BLOCKS = ("0\nSECTION\n2\nBLOCKS\n0\nBLOCK\n8\n0\n2\n*Model_Space\n0\nENDBLK\n8\n0\n"
              "0\nBLOCK\n8\n0\n2\n_ARCHTICK\n0\nLWPOLYLINE\n8\n0\n0\nENDBLK\n8\n0\n"
              "0\nBLOCK\n8\n0\n2\nTAB\n0\nLINE\n8\nBEND\n0\nENDBLK\n8\n0\n0\nENDSEC\n")

    def test_reading_the_layers(self):
        o = c_drawings.dxf_other_layers
        assert o(self.dxf_doc(("LINE", "CUT"), ("TEXT", "MARK"))) == set()       # BEND only in the layer table
        assert o(self.dxf_doc(("LINE", "CUT"), ("LINE", "BEND"))) == {"BEND"}
        assert o(self.dxf_doc(("LWPOLYLINE", "cut"), ("LINE", "bend"), ("LWPOLYLINE", "POCKET-HALF-DEPTH"))) == \
            {"BEND", "POCKET-HALF-DEPTH"}
        assert o("") is None and o("AutoCAD Binary DXF\r\n\x1a\x00") is None

    def test_only_drawn_entities_and_inserted_blocks_count(self):
        o = c_drawings.dxf_other_layers
        assert o(self.BLOCKS + self.dxf_doc(("LINE", "CUT"))) == set()           # blocks never inserted
        inserted = self.BLOCKS + self.dxf_doc(("LINE", "CUT")).replace(
            "0\nENDSEC\n0\nEOF", "0\nINSERT\n8\nCUT\n2\nTAB\n0\nENDSEC\n0\nEOF")
        assert o(inserted) == {"BEND"}

    def test_an_unreadable_dxf_keeps_the_drawing(self, tmp_path):
        self.plate(tmp_path)
        (tmp_path / "v2/03-Manufacturing/front/361101_P01_FRONT-COVER-PLATE_DXF.dxf").write_text("")
        fs = {f.subject: f.message for f in c_drawings.check_drawings(str(tmp_path), {"361101"}, {},
                                                                     {"361101": "FRONT - COVER PLATE"})}
        assert "can't be read" in fs["361101"]

    def test_the_dxf_must_hold_every_hole_of_the_step(self, tmp_path):
        holes = [sf.Hole(1, (50, 50, 0), (0, 0, 1), 7.0, 2.0, [])]
        assert "has 0 of the 1 Ø7 holes" in self.plate(tmp_path, holes=holes)["361101"]
        assert self.plate(tmp_path, holes=holes, layers=(("CUT", "LWPOLYLINE", 0), ("CUT", "CIRCLE", 3.5))) == {}

    def test_a_step_that_is_not_flat_keeps_the_drawing(self, tmp_path):
        flat = (False, None, "its faces lie at 3 levels through the thickness (a pocket, a step or a rebate)")
        assert "3 levels" in self.plate(tmp_path, flat=flat)["361101"]

def test_door_swing_moves_everything_in_the_door_unit_but_the_hinges():
    import csv as _csv
    with open(os.path.join(ROOT, "v2/04-Checks/config/door-swing.csv"), newline="") as fh:
        cfg = next(_csv.DictReader(fh))
    mv, ex = re.compile(cfg["moving"], re.I), re.compile(cfg["fixed_exclude"], re.I)
    unit = "360001_P01_FRONT-DOOR-UNIT_CAD:1 / %s:1 / Body1"
    moves = lambda label: bool(mv.search(label)) and not ex.search(label)
    assert moves(unit % "368002 FRONT - GLAZING U-SEAL - BOHLE BO5201735")      # rides on the leaf's edge
    assert moves(unit % "361001 FRONT - DOOR LEAF - 4+4 LAMINATED")
    assert not moves(unit % "368101 FRONT - DOOR HINGE - HOLD - H1 BOTTOM")      # half fixed, half moving: left out
    assert not moves("360002_P01_FRONT-FIXED-GLASS-UNIT_CAD:1 / 361003 FRONT - FIXED GLASS - 4+4 LAMINATED:1 / Body1")


def test_seam_rules_leave_out_electricals_reserved_spaces():
    # ELECTRICAL's 71xxxx bodies are reserved spaces (routes, pockets, grommets), not wall panels, though their
    # names carry position codes such as B2/R1 (PM, 2026-11-01)
    import csv as _csv
    with open(os.path.join(ROOT, "v2/04-Checks/config/gap-rules.csv"), newline="") as fh:
        seams = [r for r in _csv.DictReader(fh) if r["id"].startswith("SEAM-")]
    elec = ("710000_P01_ELECTRICAL_CAD:1 / 710021 ELECTRICAL - HARNESS - TRUNK - B2/R1:1 / "
            "S-PU-X GROMMETED SLOT - CUT-OUT RIGHT RETURN B2 R1 B4 B1 B3 L1 R2 L2")
    for r in seams:
        assert not re.search(r["a"], elec) and not re.search(r["b"], elec), r["id"]
    corner = next(r for r in seams if r["id"] == "SEAM-BACK-CORNER-R")
    assert re.search(corner["b"], "210000 WALL:1 / 210202 WALL - PANEL ASSY - BACK LOWER - B2:1 / FRAME")


def test_a_shared_hardware_drawing_stays_with_the_joints_engineer_when_a_team_models_it(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    (d / "831001_P01_HARDWARE-LOCATING-SPIGOT_STEP.step").write_text("x")
    fs = c_drawings.check_drawings(str(tmp_path), {"831001"}, {}, {"831001": "HARDWARE - LOCATING SPIGOT - M6 X Ø8"})
    assert [f.owner for f in fs if f.rule == "no-drawing"] == ["Joints Engineer"]


def test_d93_to_d99(tmp_path, monkeypatch):
    # D-97: a missing drawing is severe whatever the screen state (the repo's policy file)
    monkeypatch.setattr(c_drawings, "screen_locked", lambda: True)
    assert c_drawings.missing_drawing_severity(ROOT) == "severe"
    # D-95: the base keys are the Joints Engineer's, even from BASE's own list
    assert owner_for("v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv", "111211") == "Joints Engineer"
    assert owner_for("v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv", "111401") == "BASE"
    # D-93: the wiring diagram draws 710000, with no units or tolerance block asked of it
    d = tmp_path / "v2/02-Drawings/electrical"
    d.mkdir(parents=True)
    _pdf(d / "710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf", "SHEET 3 ROUTES AND JOINTS")
    assert c_drawings.check_drawings(str(tmp_path), {"710000"}, {}, {"710000": "ELECTRICAL"}) == []
    # D-99: part 4 is for flat metal sheet; glass keeps its drawing
    m = tmp_path / "v2/03-Manufacturing/front"
    m.mkdir(parents=True)
    (m / "360000_P01_FRONT_BOM.csv").write_text(
        "part_number,name,material,thickness_mm,finish,process,tolerance\n"
        "361001,FRONT - DOOR LEAF - 4+4 LAMINATED,laminated safety glass 4+4,8.76,polished edges,waterjet cut,ISO 2768-m\n")
    _dxf(m / "361001_P01_FRONT-DOOR-LEAF_DXF.dxf", [("CUT", "LWPOLYLINE", 0)])
    fs = {f.subject: f.message for f in c_drawings.check_drawings(str(tmp_path), {"361001"}, {},
                                                                 {"361001": "FRONT - DOOR LEAF - 4+4 LAMINATED"})}
    assert "metal or ACP sheet (D-99, D-100)" in fs["361001"]
    # D-100: a flat ACP skin counts under part 4 like metal sheet
    (m / "360000_P01_FRONT_BOM.csv").write_text(
        "part_number,name,material,thickness_mm,finish,process,tolerance\n"
        "361001,FRONT - DOOR LEAF - 4+4 LAMINATED,ACP 4 mm FR core,4,PVDF RAL 9005,CNC router,ISO 2768-m\n")
    assert c_drawings.check_drawings(str(tmp_path), {"361001"}, {}, {"361001": "FRONT - DOOR LEAF - 4+4 LAMINATED"}) == []
    # D-99: hardware names come from the joints register
    j = tmp_path / "v2/05-Engineering/joints"
    j.mkdir(parents=True)
    (j / "joints-register.md").write_text("| H-22 | **368102** | FRONT - DOOR STRIKE · Đế hít cửa | bought | 1 |\n")
    _write_csv(m / "360001_P01_FRONT-DOOR-UNIT_BOM.csv", [{"part_number": "368102", "name": "FRONT - DOOR STRIKE",
                                                          "qty": "1"}])
    plists = c_parts.find_parts_lists(str(tmp_path))
    prods = {"368102": {"files": {"v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step"}, "count": 1,
                        "name": "368102 FRONT - DOOR CATCH STRIKE - SUGATSUNE HT-MSG62-U10"}}
    fs = [f for f in c_parts.check_cad_match(str(tmp_path), plists, prods) if f.rule == "name-mismatch"]
    assert len(fs) == 1 and "'FRONT - DOOR STRIKE'" in fs[0].message and "the CAD" in fs[0].fix


def test_a_renamed_register_part_lists_every_file_and_team_and_a_new_maker_code_is_major(tmp_path):
    # D-131: the register re-specified 838003 from the aluminium CAH3 to the steel CAH2; every team still names the old
    j = tmp_path / "v2/05-Engineering/joints"
    j.mkdir(parents=True)
    (j / "joints-register.md").write_text(
        "| H-03 | **838003** | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2 · Tán rút | bought |\n"
        "| H-22 | **368102** | FRONT - DOOR STRIKE · Đế hít cửa | bought | 1 |\n")
    old = "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2"
    for team, pn in (("wall", "210101"), ("base", "110000")):
        (tmp_path / "v2/03-Manufacturing" / team).mkdir(parents=True)
        _write_csv(tmp_path / "v2/03-Manufacturing" / team / ("%s_P01_X_BOM.csv" % pn),
                   [{"part_number": "838003", "name": old, "qty": "4"}])
    _write_csv(tmp_path / "v2/03-Manufacturing/wall/210102_P01_Y_BOM.csv",
               [{"part_number": "838003", "name": "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2",
                 "qty": "4"}])
    plists = c_parts.find_parts_lists(str(tmp_path))
    prods = {"838003": {"files": {"v2/03-Manufacturing/wall/210101_P01_X_STEP.step",
                                  "v2/03-Manufacturing/base/110000_P01_X_STEP.step"}, "count": 4,
                        "name": "838003 " + old,
                        "names": {"v2/03-Manufacturing/wall/210101_P01_X_STEP.step": "838003 " + old + " (1)",
                                  "v2/03-Manufacturing/base/110000_P01_X_STEP.step": "838003 " + old}}}
    fs = [f for f in c_parts.check_cad_match(str(tmp_path), plists, prods) if f.rule == "name-mismatch"]
    assert len(fs) == 1
    f = fs[0]
    assert f.severity == "major" and f.owner == "BASE; WALL"
    assert "CAH3-610-4.2 (gone)" in f.message and "CAH2-610-4.2 (new)" in f.message and "STEEL (new)" in f.message
    assert "110000_P01_X_STEP.step" in f.message and "v2/03-Manufacturing/base/110000_P01_X_BOM.csv" in f.message
    assert "210102_P01_Y_BOM.csv" not in f.message and "material and finish" in f.fix and "(2 CAD, 2 parts lists)" in f.fix
    assert f.evidence["files"] == sorted(f.evidence["files"]) and len(f.evidence["files"]) == 4
    # wording only stays minor
    assert c_parts.part_words("FRONT - DOOR STRIKE") == c_parts.part_words("FRONT - DOOR CATCH STRIKE") == set()
    prods = {"368102": {"files": {"v2/03-Manufacturing/wall/210101_P01_X_STEP.step"}, "count": 1,
                        "name": "368102 FRONT - DOOR CATCH STRIKE"}}
    fs = [f for f in c_parts.check_cad_match(str(tmp_path), plists, prods) if f.rule == "name-mismatch"]
    assert [f.subject for f in fs] == ["368102", "838003"]          # 838003's lists are checked without its CAD too
    assert fs[0].severity == "minor" and fs[0].owner == "WALL"
    assert fs[1].severity == "major" and fs[1].owner == "BASE; WALL" and "the CAD" not in fs[1].message


def test_names_compare_by_their_words_and_a_stale_master_bom_owns_its_fix(tmp_path):
    from common import name_words
    assert name_words("BASE - LEVELLING GLIDE - M10 (HOLD)") == name_words("BASE - LEVELLING GLIDE - M10 - HOLD")
    assert name_words("FRONT - DOOR STRIKE") != name_words("FRONT - DOOR LOCK")
    j = tmp_path / "v2/05-Engineering/joints"
    j.mkdir(parents=True)
    (j / "joints-register.md").write_text("| H-06 | **118001** | BASE - BASE SEAL - FLOOR EDGE - FIXED 4 GAP · x | bought |\n")
    row = {"part_number": "118001", "name": "BASE - BASE SEAL - FLOOR EDGE - FIXED 4 GAP", "name_vi": "x",
           "material": "silicone", "finish": "none", "qty": "1", "mass_kg": "0.1", "status": "HOLD", "source": "register"}
    (tmp_path / "v2/03-Manufacturing/base").mkdir(parents=True)
    _write_csv(tmp_path / "v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv", [row])
    (tmp_path / "v2/04-BOM").mkdir(parents=True)
    _write_csv(tmp_path / "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv", [dict(row, name="BASE - BASE SEAL - GAP 10 ±5")])
    plists = c_parts.find_parts_lists(str(tmp_path))
    # a register part's names are the register's to decide (D-99): one name-mismatch, not a duplicate-number too
    assert [f for f in c_parts.check_parts_lists(str(tmp_path), plists) if f.rule == "duplicate-number"] == []
    fs = [f for f in c_parts.check_cad_match(str(tmp_path), plists, {}) if f.rule == "name-mismatch"]
    assert len(fs) == 1 and fs[0].owner == "Control" and "100000_P01_POD-MASTER_BOM.csv" in fs[0].fix
    # an unregistered number with two names stays a duplicate-number
    _write_csv(tmp_path / "v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv",
               [row, dict(row, part_number="111999", name="BASE - A")])
    _write_csv(tmp_path / "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv",
               [dict(row, part_number="111999", name="BASE - B")])
    fs = [f for f in c_parts.check_parts_lists(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)))
          if f.rule == "duplicate-number"]
    assert [f.subject for f in fs] == ["111999"]


def test_a_master_bom_row_copied_from_a_team_list_is_checked_there_whatever_its_source_suffix():
    row = {"_raw": {"row_type": "part", "source_file": "v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv @ working tree"}}
    assert c_parts.is_placeholder(row)
    assert c_parts.is_placeholder({"_raw": {"row_type": "hardware (register only)", "source_file": "x @ main"}})
    assert not c_parts.is_placeholder({"_raw": {"row_type": "part", "source_file": "v2/00-Control/assembly-tree.md"}})


def test_the_master_boms_generated_views_are_not_parts_lists(tmp_path):
    d = tmp_path / "v2/04-BOM"
    d.mkdir(parents=True)
    row = {"part_number": "118002", "name": "BASE - LEVELLING GLIDE - M10 - HOLD", "qty": "7"}
    for name in ("100000_P01_POD-MASTER_BOM.csv", "100000_P01_POD-BOUGHT-PARTS_BOM.csv",
                 "100000_P01_POD-MADE-PARTS-BY-PROCESS_BOM.csv"):
        _write_csv(d / name, [row])
    assert [os.path.basename(p) for p, _r in c_parts.find_parts_lists(str(tmp_path))] == ["100000_P01_POD-MASTER_BOM.csv"]


def test_reserved_air_spaces_are_listed_under_air_not_as_missing_drawings(tmp_path):
    # the Lead's ruling on FRONT's DR air transitions, as D-92's reserved spaces
    (tmp_path / "v2/04-Checks/config").mkdir(parents=True)
    (tmp_path / "v2/04-Checks/config/reserved-spaces.csv").write_text(
        "part_number,owner,ruling,why\n351403,AIR,as D-92,DR's lower air transition\n")
    names = {"351403": "FRONT - AIR TRANSITION - LOWER - DR", "351404": "FRONT - SUPPLY FAN BOX - DR"}
    fs = {f.subject: f for f in c_drawings.check_drawings(str(tmp_path), set(names), {}, names)}
    assert fs["351403"].rule == "reserved-space" and fs["351403"].owner == "AIR"
    assert fs["351404"].rule == "no-drawing"
    from common import reserved_spaces, reserved_label
    res = reserved_spaces(str(tmp_path))
    assert reserved_label("350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD:1 / 351403 FRONT - AIR TRANSITION:1 / Body1", res)
    assert not reserved_label("3514030 X", res)


def test_a_reserved_air_space_row_asks_for_no_mass_material_or_finish(tmp_path):
    (tmp_path / "v2/04-Checks/config").mkdir(parents=True)
    (tmp_path / "v2/04-Checks/config/reserved-spaces.csv").write_text("part_number,owner,ruling,why\n351402,AIR,x,riser space\n")
    d = tmp_path / "v2/03-Manufacturing/front"
    d.mkdir(parents=True)
    _write_csv(d / "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv",
               [{"part_number": "351402", "name": "FRONT - AIR INTAKE RISER - DR", "type": "reserved air space", "qty": "1"},
                {"part_number": "351306", "name": "FRONT - DR - FRAME", "type": "made", "qty": "1"}])
    subjects = {f.subject.split(" ")[0] for f in c_parts.check_parts_lists(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)))}
    assert "351402" not in subjects and "351306" in subjects


def test_d105_a_row_typed_reserved_air_space_is_reserved_without_a_config_line(tmp_path):
    d = tmp_path / "v2/03-Manufacturing/front"
    d.mkdir(parents=True)
    _write_csv(d / "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv",
               [{"part_number": "351406", "name": "FRONT - AIR SPACE - DR", "type": "reserved air space", "qty": "1"}])
    from common import reserved_spaces
    r = reserved_spaces(str(tmp_path))
    assert r["351406"]["owner"] == "AIR" and r["351406"]["ruling"] == "D-105"


def test_a_duplicate_name_goes_to_the_list_that_is_off(tmp_path):
    row = {"name_vi": "x", "material": "6061-T6", "finish": "mill", "qty": "1", "mass_kg": "0.1", "status": "DRAFT",
           "source": "CAD"}
    for folder, name in (("base", "110000_P01_BASE_BOM.csv"), ("joints", "V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv")):
        (tmp_path / "v2/03-Manufacturing" / folder).mkdir(parents=True)
    _write_csv(tmp_path / "v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv",
               [dict(row, part_number="111211", name="BASE - CORNER KEY - BACK - COMMON"),
                dict(row, part_number="111501", name="BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM")])
    _write_csv(tmp_path / "v2/03-Manufacturing/joints/V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv",
               [dict(row, part_number="111211", name="BASE - CORNER KEY - SQUARE - COMMON")])
    (tmp_path / "v2/04-BOM").mkdir(parents=True)
    _write_csv(tmp_path / "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv",
               [dict(row, part_number="111501", name="BASE - FLOOR MAT - F1 - CLOSED-CELL 3 MM FOAM")])
    fs = {f.subject: f for f in c_parts.check_parts_lists(str(tmp_path), c_parts.find_parts_lists(str(tmp_path)))
          if f.rule == "duplicate-number"}
    assert fs["111211"].owner == "BASE" and "SQUARE" in fs["111211"].fix      # the key's name is the Joints Engineer's
    assert fs["111501"].owner == "Control" and "Rebuild the master BOM" in fs["111501"].fix


def test_edge_distance_is_for_rigid_parts_not_felt(monkeypatch, tmp_path):
    # the owner's rule 9 is for sheet parts: a 60 mm access hole near a felt's edge can't tear out
    def plate(name):
        x0, x1, y0, y1 = -31.0, 500.0, -31.0, 500.0         # a 1 mm web round a Ø60 opening (the Lead's web rule)
        rim = (sf.Frame(), 30.0, (30.0, 0, 0), (30.0, 0, 0), True)
        face = sf.Face(1, "plane", (0, 0, 0), (0, 0, 1), None, True, [], [rim],
                       [((x0, y0, 0), (x1, y0, 0)), ((x1, y0, 0), (x1, y1, 0)), ((x1, y1, 0), (x0, y1, 0)),
                        ((x0, y1, 0), (x0, y0, 0))])
        so = sf.Solid(1, name)
        so.faces, so.holes, so.bends = [face], [sf.Hole(1, (0, 0, 0), (0, 0, 1), 60.0, 1.0, [])], []
        return so

    class FakeStep:
        def __init__(self, pn, name):
            self.pn, self.name, self.so = pn, name, plate(name)

        def instances(self):
            return [{"solid": 1, "part_number": self.pn, "name": "%s %s" % (self.pn, self.name), "path": [], "frame": sf.Frame()}]

        def solid(self, _sid):
            return self.so
    for pn, name, flagged in (("511302", "LINING - FELT - SIDE LOWER - RH", False),
                              ("511102", "LINING - TRAY - SIDE LOWER - RH", True)):
        monkeypatch.setattr(c_geometry, "load_step", lambda _p, s=FakeStep(pn, name): s)
        fs = [f for f in c_geometry.check_part_features(str(tmp_path), str(tmp_path / "x.step"), {}, {}, hole_rules=[],
                                                         edge_exceptions={}) if f.rule in ("edge-distance", "opening-web")]
        assert bool(fs) == flagged, name                    # the tray's Ø60 is an opening: its 1 mm web fails


def test_the_assembled_shell_is_checked_face_by_face_once_its_parts_are_on_main():
    lo = _B("210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_CAD:1 / 210102 WALL - PANEL ASSY - SIDE LOWER - RH:1 / SKIN",
            (1204.0, -642.7, 112.3, 1250.0, 850.0, 1255.0), "211302")
    up = _B("210104_P01_WALL-PANEL-ASSY-SIDE-UPPER-RH_CAD:1 / 210104 WALL - PANEL ASSY - SIDE UPPER - RH:1 / SKIN",
            (1204.0, -642.7, 1257.3, 1250.0, 850.0, 2400.0), "211304")
    dr = _B("350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD:1 / 350003 FRONT - DECOR BLOCK ASSY - DR:1 / BODY",
            (950.0, -850.0, 110.0, 1250.0, -645.0, 2400.0), "351301")
    band = _B("110000_P01_BASE_CAD:1 / 110102 BASE - BAND ASSY - SIDE - RH:1 / TUBE",
              (1210.0, -645.0, 10.0, 1250.0, 850.0, 110.0), "111102")
    assert "right" not in c_geometry.shell_faces_ready("assembly", [lo, up])        # DR not on main yet
    assert "right" not in c_geometry.shell_faces_ready("assembly", [lo, up, dr])    # nor the band its seam closes on
    assert "right" in c_geometry.shell_faces_ready("assembly", [lo, up, dr, band])
    assert "back" not in c_geometry.shell_faces_ready("assembly", [lo, up, dr, band])      # no back walls yet
    # the file names' hyphens count as the words' spaces (the real assembly's top components)
    hy = [_B(b.label.split(" / ")[0] + " / X", b.box, b.part_number) for b in (lo, up, dr)] + [band]
    assert "right" in c_geometry.shell_faces_ready("assembly", hy)
    # a seam-wide strip along the face's own edge is the seam to the next face's part: not an opening
    assert [g for g in c_geometry.shell_gaps([lo, up]) if g["zone"] == "right"] == []
    # an L of wider strips (10 mm short of the band and of the decor) reports as its two strips
    lo10 = _B(lo.label, (1204.0, -635.0, 120.0, 1250.0, 850.0, 1255.0), "211302")
    up10 = _B(up.label, (1204.0, -635.0, 1257.3, 1250.0, 850.0, 2400.0), "211304")
    gaps = [g for g in c_geometry.shell_gaps([lo10, up10]) if g["zone"] == "right"]
    assert len(gaps) == 2 and all(min(g["a"][1] - g["a"][0], g["b"][1] - g["b"][0]) < 15 for g in gaps)

def test_a_step_whose_top_carries_another_number_is_reported(tmp_path):
    import shutil, run_checks
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    # the bolt fixture's root part number is CHECK-FIXTURE: named for 210101, it should say so
    shutil.copy(os.path.join(HERE, "fixtures", "bolt-joints.step"), d / "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step")
    out = run_checks.run(str(tmp_path), "test")
    fs = out[0] if isinstance(out, tuple) else out["findings"] if isinstance(out, dict) else out
    keys = {(f.rule, f.subject) if hasattr(f, "rule") else (f["rule"], f["subject"]) for f in fs}
    assert ("top-part-number", "210101") in keys


def test_a_solid_with_a_sealed_void_reads_by_its_outer_shell():
    # BREP_WITH_VOIDS (an inner shell, valid STEP; AIR's closed fan boxes): the outer shell gives the box and the
    # holes, the void is counted, and nothing crashes
    text = open(os.path.join(HERE, "fixtures", "bolt-joints.step"), encoding="utf-8").read()
    path_plain = os.path.join(HERE, "fixtures", "bolt-joints.step")
    hollow = text.replace("#256=MANIFOLD_SOLID_BREP('WALL - TEST WALL BOLT SIDE A',#3379);",
                          "#256=BREP_WITH_VOIDS('WALL - TEST WALL BOLT SIDE A',#3379,(#999901));\n"
                          "#999901=ORIENTED_CLOSED_SHELL('',*,#3380,.F.);")
    assert hollow != text
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "hollow.step")
        open(p, "w", encoding="utf-8").write(hollow)
        a, b = sf.StepFile(path_plain), sf.StepFile(p)
        sa, sb = a.solid(256), b.solid(256)
        assert sb.voids == 1 and sa.voids == 0
        assert sb.box == sa.box and len(sb.holes) == len(sa.holes) == 1
        assert any(i["solid"] == 256 for i in b.instances())        # still found as a solid of its product


def _felt_dxf(path, body, blocks=""):
    """A small ASCII DXF in mm: body is the ENTITIES section's records, blocks its BLOCKS section's."""
    path.write_text("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nBLOCKS\n" + blocks +
                    "0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + body + "0\nENDSEC\n0\nEOF\n")


def _dxf_rect(w, h, layer="CUT"):
    return ("0\nLWPOLYLINE\n8\n%s\n90\n4\n70\n1\n10\n0\n20\n0\n10\n%g\n20\n0\n10\n%g\n20\n%g\n10\n0\n20\n%g\n"
            % (layer, w, w, h, h))


def _dxf_circle(x, y, r, layer="CUT"):
    return "0\nCIRCLE\n8\n%s\n10\n%g\n20\n%g\n40\n%g\n" % (layer, x, y, r)


def test_a_felt_with_openings_passes_on_its_dxf_and_row(tmp_path):
    # D-128, extending D-89 part (3): a felt or fill piece with through-openings or edge notches only needs no drawing
    # when its DXF gives the full outline with every opening and its row gives material, density or grade, thickness,
    # tolerance and part number. A pocket keeps the drawing.
    felt = _profile(sf.Frame(), length=1000.0, w=500.0, h=9.0, t=None, holes=((300.0, 50.0),))
    shape, why = c_drawings.prism_shape(felt)
    assert why == "" and shape == {"thickness": pytest.approx(9.0), "sides": (500.0, 1000.0), "loops": 2}
    assert c_drawings.prism_shape(_profile(sf.Frame(), w=40.0, h=40.0, t=2.0))[0] is None      # a tube's inner face
    assert c_drawings.prism_shape(_profile(sf.Frame(), w=30.0, h=3.0, t=None, chamfer=1.0))[0] is None
    d = tmp_path / "v2/03-Manufacturing/wall"
    d.mkdir(parents=True)
    dxf = d / "511302_P01_LINING-FELT-SIDE-LOWER-RH_DXF.dxf"
    unplaced = "0\nBLOCK\n8\n0\n2\nSPARE\n10\n0\n20\n0\n" + _dxf_circle(100, 100, 10) + "0\nENDBLK\n"
    _felt_dxf(dxf, _dxf_rect(1000, 500) + _dxf_circle(300, 250, 25), unplaced)
    assert c_drawings.dxf_shapes(str(dxf)) == {"loops": 2, "open": 0, "size": (500.0, 1000.0), "units": "4"}
    row = {"part_number": "511302", "name": "LINING - FELT - SIDE LOWER - RH", "kind": "MP",
           "material": "PET felt 9 mm, 1800 g/m2", "size_mm": "9 x 1000 x 500", "tolerance": "±1 on length and width"}
    names = {"511302": row["name"]}
    def found(change=None, shape_why=(shape, "")):
        _write_csv(d / "210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_BOM.csv", [dict(row, **(change or {}))])
        fs = c_drawings.check_drawings(str(tmp_path), {"511302"}, {"511302": felt.holes}, names,
                                       {"511302": [len(felt.faces)]}, prism_by_pn={"511302": shape_why})
        return " ".join(f.message for f in fs)
    assert found() == ""                                                      # the DXF and the row stand in
    _write_csv(d / "210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_BOM.csv", [row])
    assert "D-89's cut-list route doesn't apply" in " ".join(       # without D-128 the opening keeps the drawing
        f.message for f in c_drawings.check_drawings(str(tmp_path), {"511302"}, {"511302": felt.holes}, names,
                                                     {"511302": [len(felt.faces)]}, prism_by_pn={}))
    assert "density or grade" in found({"material": "polyester"})
    assert "thickness (9 mm" in found({"size_mm": "12 x 1000 x 500", "material": "PET felt, 1800 g/m2"})
    assert "through features only" in found({"size_mm": "9 x 1000 x 500, two pockets"})
    assert found({"size_mm": "", "material": "PET felt 9 mm", "note": "its outline is stepped and slanted"}) == ""
    assert "a piece cut straight through (a face sits between" in found(shape_why=(None, "a face sits between the "
                                                                                       "sheet's two faces (a pocket)"))
    _felt_dxf(dxf, _dxf_rect(1000, 500))                                               # the opening left out of the DXF
    assert "every opening in its DXF (the STEP has 2 closed shapes, the DXF 1)" in found()
    _felt_dxf(dxf, _dxf_rect(1000, 500) + "0\nINSERT\n8\nCUT\n2\nHOLE\n10\n300\n20\n250\n",       # placed by an INSERT: counts
         "0\nBLOCK\n8\n0\n2\nHOLE\n10\n0\n20\n0\n" + _dxf_circle(0, 0, 25) + "0\nENDBLK\n")
    assert found() == ""
    _felt_dxf(dxf, _dxf_rect(1000, 500) + _dxf_circle(300, 250, 25) + _dxf_circle(10, 10, 2, layer="POCKET"))
    assert "CUT and MARK layers only" in found()


def test_a_drawgen_part_stays_severe_on_a_locked_screen(tmp_path, monkeypatch):
    # D-113: drawgen doesn't wait for the screen, so under D-84's auto mode its parts keep a missing drawing severe
    cfg = tmp_path / "v2/04-Checks/config"
    cfg.mkdir(parents=True)
    _write_csv(cfg / "policy.csv", [{"key": "missing_drawing_severity", "value": "auto-screen-lock",
                                     "status_source": "test"}])
    (tmp_path / "tools/drawgen").mkdir(parents=True)
    (tmp_path / "tools/drawgen/specs.py").write_text(
        'SPECS = {"111101": ("base", "part", {}), "211501": ("wall", "tabulated", {"covers": ["211501", "211502"]})}\n')
    assert c_drawings.drawgen_parts(str(tmp_path)) == {"111101", "211501", "211502"}
    monkeypatch.setattr(c_drawings, "screen_locked", lambda: True)
    sev = {f.subject: f.severity for f in c_drawings.check_drawings(str(tmp_path), {"111101", "211502", "111999"}, {})
           if f.rule == "no-drawing"}
    assert sev == {"111101": "severe", "211502": "severe", "111999": "major"}


def test_a_parts_holes_come_from_its_own_step_first():
    # BASE's assembly holds corner key 111211 turned 180 degrees in its own frame (the same key; it is symmetric), so its
    # bottom holes sit at other key coordinates than in the key's own STEP: adding both gave six hole axes for four holes
    import run_checks
    files = {"v2/03-Manufacturing/base/110000_P01_BASE_STEP.step": 1,
             "v2/03-Manufacturing/joints/111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step": 2}
    assert run_checks.own_file_first("111211", files).endswith("111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step")
    assert run_checks.own_file_first("111999", files).endswith("110000_P01_BASE_STEP.step")


def test_a_parts_copies_must_be_the_part_its_own_step_holds():
    # a copy of a part in another team's STEP must have its own STEP's hole layout and sizes, however it is turned
    class FakeStep:
        def __init__(self, rows):
            self.rows = rows
        def instances(self):
            return [{"solid": i, "part_number": pn} for i, (pn, _so) in enumerate(self.rows)]
        def solid(self, sid):
            return self.rows[sid][1]
    a = math.radians(90.0)
    turned = sf.Frame.from_axes((500.0, 300.0, 20.0), (0, 0, 1), (math.cos(a), math.sin(a), 0))
    key = lambda frame=sf.Frame(), holes=((20.0, 6.6), (80.0, 6.6)), length=100.0: \
        _profile(frame, length=length, w=30.0, h=10.0, t=None, holes=holes)
    own = os.path.join(ROOT, "v2/03-Manufacturing/joints/831999_P01_HARDWARE-TEST-KEY_STEP.step")
    base = os.path.join(ROOT, "v2/03-Manufacturing/base/110000_P01_BASE_STEP.step")
    wall = os.path.join(ROOT, "v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step")
    front = os.path.join(ROOT, "v2/03-Manufacturing/front/350001_P01_FRONT-DECOR_STEP.step")
    files = {own: FakeStep([("831999", key())]),
             base: FakeStep([("831999", key(turned))]),                        # turned and moved: the same part
             wall: FakeStep([("831999", key(holes=((20.0, 6.6), (70.0, 6.6))))]),   # a hole 10 mm off
             front: FakeStep([("831999", key(length=102.0))])}                 # 2 mm longer
    got = {(f.owner, f.severity): f for f in c_parts.check_copies(ROOT, list(files), files.get)}
    assert set(got) == {("WALL; Joints Engineer", "severe"), ("FRONT; Joints Engineer", "major")}
    assert "hole layout" in got[("WALL; Joints Engineer", "severe")].message
    assert "sizes" in got[("FRONT; Joints Engineer", "major")].message
    # round parts compare the length at each radius both have; a detailed and a plain model aren't compared as boxes
    spigot = ("round", ((2.94, 8.0), (4.0, 6.24)))
    assert not c_parts._sizes_differ(spigot, ("round", ((3.0, 8.0), (4.0, 6.24))))          # BASE's plain copy
    assert c_parts._sizes_differ(spigot, ("round", ((3.0, 10.0), (4.0, 7.24))))              # WALL's longer one
    assert not c_parts._sizes_differ(("box", (4.0, 6.31, 15.24)), spigot)                    # can't compare: skip


def test_the_drawing_traps_are_read_back_into_c05(tmp_path):
    # ELECTRICAL's read-back (pdf_traps.py) folded into C05 (PM, 2026-11-01): small text and a symbol without 4 corners
    # are major, hidden lines and a value printed twice minor; a drawing that keeps hidden lines on purpose is listed
    fitz = pytest.importorskip("fitz")
    MMP = 72.0 / 25.4
    d = tmp_path / "v2/02-Drawings/joints"
    d.mkdir(parents=True)
    def pdf(name, note_cap, hidden):
        doc = fitz.open()
        page = doc.new_page(width=420 * MMP, height=297 * MMP)
        hid = doc.add_ocg("Hidden", on=True)
        for i in range(hidden):                                          # one view's dashes per 100 mm
            page.draw_line(fitz.Point((50 + 100 * i) * MMP, 50 * MMP), fitz.Point((60 + 100 * i) * MMP, 50 * MMP), oc=hid)
        for i, line in enumerate(["UNITS: mm", "MATERIAL: EN AW-6063 T6", "FINISH: mill finish",
                                  "GENERAL TOLERANCES: ISO 2768-m"]):
            page.insert_text(fitz.Point(30 * MMP, (200 + 8 * i) * MMP), line, fontsize=2.5 / 0.718 * MMP)
        page.insert_text(fitz.Point(30 * MMP, 240 * MMP), "NOTE", fontsize=note_cap / 0.718 * MMP)
        doc.save(str(d / name))
    pdf("831998_P01_HARDWARE-TEST-A_DWG.pdf", 1.6, 2)
    pdf("831999_P01_HARDWARE-TEST-B_DWG.pdf", 2.5, 2)
    cfg = tmp_path / "v2/04-Checks/config"
    cfg.mkdir(parents=True)
    _write_csv(cfg / "hidden-lines-allow.csv", [{"drawing": "831999_P01_HARDWARE-TEST-B_DWG.pdf", "views": "2",
                                                 "reason": "test", "ruling": "test"}])
    got = {(f.subject, f.rule, f.severity) for f in c_drawings.check_drawings(str(tmp_path), {"831998", "831999"}, {})}
    assert ("831998", "letter-height", "major") in got and ("831998", "hidden-lines", "minor") in got
    assert not [g for g in got if g[0] == "831999"]                     # 2.5 mm text; its 2 hidden views allowed


def test_the_acp_skins_bays_are_275_clear_or_less():
    # D-135: 2 mm or less under 100 N at a bay's centre; WALL's span table: 274.8 mm clear gives 1.99 mm
    lab = "210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD:1 / 211201 WALL - PANEL FRAME - BACK LOWER - B1:1 / %s"
    def frame(centres):
        bs = [_B(lab % "RAIL - BOTTOM", (0.0, 810.0, 0.0, 1200.0, 850.0, 20.0)),
              _B(lab % "RAIL - TOP", (0.0, 810.0, 1080.0, 1200.0, 850.0, 1100.0))]
        x = 0.0
        while x <= 1180.0 + 1e-6:
            bs.append(_B(lab % "STILE", (x, 810.0, 20.0, x + 20.0, 850.0, 1080.0)))
            x += centres
        for b in bs:
            b.file = "v2/03-Manufacturing/wall/210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_STEP.step"
        return bs
    wide = frame(393.33)                                           # D-85's centres: 373 clear
    assert [x[0] for x in c_geometry.acp_bays(wide)["211201 BACK LOWER - B1"]] == [373.3, 373.3, 373.3]
    fs = c_geometry.check_acp_bays(ROOT, "assembly", wide)
    assert len(fs) == 1 and fs[0].owner == "WALL" and fs[0].severity == "major" and "373.3 mm" in fs[0].message
    assert c_geometry.check_acp_bays(ROOT, "assembly", frame(295.0)) == []            # 275 clear: passes
    other = [_B("410000_P01_CEILING_CAD:1 / 411101 CEILING - PANEL FRAME - C1:1 / X", (0, 0, 0, 1200, 40, 1100))]
    assert c_geometry.acp_bays(other) == {}                          # the rule is for the wall panels' ACP


def test_a_bought_profile_we_mitre_and_drill_is_a_made_part_with_a_drawing(tmp_path):
    # D-143 (3): FRONT's 368004, Bohle's U-profile cut into 4 mitred pieces with holes, needs one table drawing
    row = {"part_number": "368004", "name": "FRONT - GLAZING U-PROFILE - BOHLE BO5201571",
           "_raw": {"kind": "bought by length, 4 pieces mitred", "note": "outer lengths 745 / 1446 mm"}}
    seal = {"part_number": "368002", "name": "FRONT - GLAZING U-SEAL", "_raw": {"kind": "bought by length, 4 pieces"}}
    bolt = {"part_number": "838001", "name": "HARDWARE - BOLT", "_raw": {"kind": "bought, drilled through"}}
    holes = {"368004": ["a hole"], "368002": [], "838001": ["a hole"]}
    why = c_drawings.processed_bought([("x.csv", [row, seal, bolt])], holes)
    assert list(why) == ["368004"] and "D-143" in why["368004"]
    assert c_drawings.processed_bought([("x.csv", [row])], {"368004": []}) == {}       # no holes: a cut length only
    as_front = dict(row, _raw={"type": "bought by length, 4 pieces mitred"})            # FRONT's column name
    assert list(c_drawings.processed_bought([("x.csv", [as_front])], holes)) == ["368004"]
    m = tmp_path / "v2/03-Manufacturing/front"
    m.mkdir(parents=True)
    fs = c_drawings.check_drawings(str(tmp_path), {"368004"}, holes, {"368004": row["name"]}, made_why=why)
    assert [(f.rule, f.severity) for f in fs] == [("no-drawing", "major")] and "D-143" in fs[0].message
    assert c_drawings.check_drawings(str(tmp_path), {"368004"}, holes, {"368004": row["name"]}) == []


def test_the_base_keys_are_joints_parts_from_111211_to_111215():
    # D-144: FR1's key became 111215, a Joints part like 111211 to 111214
    from common import owner_for, JOINTS_KEYS
    assert all(JOINTS_KEYS.match("11121%d" % i) for i in range(1, 6)) and not JOINTS_KEYS.match("111216")
    assert owner_for("v2/03-Manufacturing/base/110000_P01_BASE_STEP.step", "111215") == "Joints Engineer"


def test_a_pre_check_keeps_the_rule_rows_a_pr_adds(tmp_path):
    # FRONT's #313 added D-145's edge exception to the checks' own list: a pre-check must read it, while the
    # current rules still win for everything else
    import subprocess
    from common import export_ref
    repo = tmp_path / "repo"
    cfg = repo / "v2/04-Checks/config"
    cfg.mkdir(parents=True)
    run = lambda *a: subprocess.run(["git", "-C", str(repo)] + list(a), check=True, capture_output=True)
    run("init", "-q")
    (cfg / "edge-exceptions.csv").write_text("part_number,hole_dia_mm\n111601,13.0\n351305,7.0\n")
    run("add", "-A")
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "pr")
    (cfg / "edge-exceptions.csv").write_text("part_number,hole_dia_mm\n111601,13.0\n368004,3.4\n")   # ours now
    dest, _sha = export_ref("HEAD", repo=str(repo), dest=str(tmp_path / "a"), ref_rows=True)
    rows = open(os.path.join(dest, "v2/04-Checks/config/edge-exceptions.csv")).read().splitlines()
    assert rows == ["part_number,hole_dia_mm", "111601,13.0", "368004,3.4", "351305,7.0"]
    dest, _sha = export_ref("HEAD", repo=str(repo), dest=str(tmp_path / "b"))
    assert "351305,7.0" not in open(os.path.join(dest, "v2/04-Checks/config/edge-exceptions.csv")).read()


def test_walls_l1_names_a_wrapped_step_string_and_the_teams_own_finish():
    # the Lead's ruling on WALL's L1 sample (2026-11-01): fix the checks, don't rename parts
    from common import head_noun, is_soft
    # (1) a fill piece is fill, wherever the size sits in the function field
    n = "WALL - CAVITY FILL PIECE F01 240 X 1102.7 - SIDE LOWER - COMMON"
    assert head_noun(n) == "FILL" and is_soft(n)
    assert head_noun("BASE - SEAL HOLDER - LH") == "HOLDER" and not is_soft("BASE - SEAL HOLDER - LH")
    assert head_noun("WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH") == "BACK"
    assert head_noun("LINING - FILL - CEILING - BAY A") == "FILL" and head_noun("FRONT - DROP SEAL - ATHMER") == "SEAL"
    # (2) Fusion wraps a long STEP string across lines; the line break is no part of the name
    assert sf._decode("'WALL - FILL - SIDE LOWER - COMMO\nN'") == "WALL - FILL - SIDE LOWER - COMMON"
    assert sf._decode("'A\r\nB'") == "AB"
    # (3) the team's own row gives the finish; the master BOM's empty row doesn't hide it
    team = {"part_number": "831007", "name": "HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL",
            "material": "steel plate 2.0, galvanized", "grade": "", "finish": "galvanized Z100", "_raw": {}}
    skin = {"part_number": "211301", "name": "WALL - SKIN - SIDE LOWER - LH", "material": "ACP aluminium", "grade": "",
            "finish": "PVDF", "_raw": {}}
    master = dict(team, material="", finish="", _raw={"row_type": "part"})
    plists = [("/r/v2/03-Manufacturing/wall/210101_P01_X_BOM.csv", [team, skin]),
              ("/r/v2/04-BOM/100000_P01_POD-MASTER_BOM.csv", [master])]
    assert c_parts.materials_by_pn("/r", plists)["831007"] == "steel plate 2.0, galvanized galvanized Z100"
    assert c_parts.check_mixed_metals("/r", plists, [("831007", "211301", "x.step")]) == []
    bare = [("/r/v2/03-Manufacturing/wall/210101_P01_X_BOM.csv", [dict(team, material="", finish=""), skin]),
            ("/r/v2/04-BOM/100000_P01_POD-MASTER_BOM.csv", [master])]
    fs = c_parts.check_mixed_metals("/r", bare, [("831007", "211301", "x.step")])
    assert [f.rule for f in fs] == ["bare-steel-on-aluminium"]         # with no material at all, the name still speaks


def test_an_opening_takes_the_web_rule_and_a_fastener_hole_the_two_diameter_rule(monkeypatch, tmp_path):
    # the Lead's ruling on CEILING's fan bulkheads (2026-11-01): a Ø135 fan bore is an opening; its rim needs
    # max(2 x t, 3 mm) of material to an edge or the next hole; the fan's own screw holes keep 2 diameters
    def plate_with(holes, width=300.0, height=150.0, t=1.5):
        s = sf.Solid(1, "bulkhead")
        corners = [(0, 0), (width, 0), (width, height), (0, height)]
        lt = [((*corners[i], t), (*corners[(i + 1) % 4], t)) for i in range(4)]
        lb = [((*corners[i], 0.0), (*corners[(i + 1) % 4], 0.0)) for i in range(4)]
        rt = [_arc((x, y, t), (0, 0, 1), (1, 0, 0), d / 2, 0, 0) for x, y, d in holes]
        rb = [_arc((x, y, 0.0), (0, 0, 1), (1, 0, 0), d / 2, 0, 0) for x, y, d in holes]
        s.faces.append(sf.Face(1, "plane", (0, 0, t), (0, 0, 1), None, True, [p for l in lt for p in l], rt, lt))
        s.faces.append(sf.Face(2, "plane", (0, 0, 0), (0, 0, -1), None, True, [p for l in lb for p in l], rb, lb))
        for k, (x, y, d) in enumerate(holes):
            s.faces.append(sf.Face(3 + k, "cylinder", (x, y, 0), (0, 0, 1), d / 2, False, [rt[k][2], rb[k][2]],
                                   [rt[k], rb[k]], []))
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            n = sf.norm(((b[1] - a[1]), -(b[0] - a[0]), 0.0))
            s.faces.append(sf.Face(20 + i, "plane", (*a, 0.0), n, None, True, [(*a, 0.0), (*b, 0.0), (*a, t), (*b, t)],
                                   [], [((*a, 0.0), (*b, 0.0)), ((*a, t), (*b, t))]))
        s.box = (0, 0, 0, width, height, t)
        s.thickness = sf._sheet_thickness(s)
        s.holes = sf._holes(s)
        return s
    # two Ø135 bores: 7.5 mm rims to the long edges, 9 mm between them; a fan screw hole Ø4.3 4 mm from an edge
    plate = plate_with([(75.0, 75.0, 135.0), (219.0, 75.0, 135.0), (150.0, 146.0, 4.3)])
    assert len(plate.holes) == 3

    class FakeStep:
        def instances(self):
            return [{"solid": 1, "part_number": "611403", "name": "AIR - FAN BULKHEAD - EXHAUST", "path": ["611403"],
                     "frame": sf.Frame()}]

        def solid(self, sid):
            return plate
    monkeypatch.setitem(c_geometry.load_step.__defaults__[0], str(tmp_path / "x.step"), FakeStep())
    fs = c_geometry.check_part_features(str(tmp_path), str(tmp_path / "x.step"), {}, [])
    got = sorted((f.rule, round(f.evidence.get("web_mm", f.evidence.get("edge_mm", 0)), 1)) for f in fs)
    assert ("edge-distance", 4.0) in got                         # the screw hole: 4 < 2 x 4.3 to the top edge
    assert not any(r == "edge-distance" and v > 5 for r, v in got)   # no 2-diameter rule on the bores
    assert not any(r == "hole-spacing" for r, _v in got)
    # 7.5 and 6 mm rims and the 9 mm web pass max(2 x 1.5, 3) = 3; a 2 mm rim doesn't
    assert not any(r == "opening-web" for r, _v in got)
    plate = plate_with([(69.5, 75.0, 135.0), (219.0, 75.0, 135.0), (150.0, 146.0, 4.3)])          # a 2 mm rim
    fs = c_geometry.check_part_features(str(tmp_path), str(tmp_path / "x.step"), {}, [])
    webs = [f for f in fs if f.rule == "opening-web"]
    assert len(webs) == 1 and webs[0].evidence["web_mm"] == 2.0 and "3.0 mm" in webs[0].message
    # a smaller cut its row names as an opening is an opening too
    small = sf.Hole(1, (10.0, 10.0, 0.75), (0.0, 0.0, 1.0), 16.0, 1.5, [])
    assert c_geometry.is_opening(small, "AIR - BULKHEAD; Ø16 cable opening") and not c_geometry.is_opening(small, "")


def _box_body(label, box, file="v2/03-Manufacturing/front/350003_P01_X_STEP.step"):
    """A body whose solid is its box's six flat faces, outward normals."""
    x0, y0, z0, x1, y1, z1 = box
    faces = []
    for k, (lo, hi) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
        for val, sgn in ((lo, -1.0), (hi, 1.0)):
            n = [0.0, 0.0, 0.0]
            n[k] = sgn
            o = [x0, y0, z0]
            o[k] = val
            others = [i for i in range(3) if i != k]
            pts = []
            for a in (box[others[0]], box[others[0] + 3]):
                for b in (box[others[1]], box[others[1] + 3]):
                    q = [0.0, 0.0, 0.0]
                    q[k], q[others[0]], q[others[1]] = val, a, b
                    pts.append(tuple(q))
            faces.append(sf.Face(len(faces) + 1, "plane", tuple(o), tuple(n), None, True, pts, [], []))
    solid = sf.Solid(1, label.split(" / ")[-2])
    solid.faces = faces
    return c_geometry.Body(label, solid, sf.Frame(), box, file, "", None)


def test_every_bonded_skin_sits_bond_t_off_its_frame():
    # D-137 (the Lead, 2026-11-01): FRONT's decor frames were modelled right on their skins, with no glue line
    top = "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD:1"
    skin = _box_body(top + " / 351301 FRONT - DECOR SKIN - DR:1 / Body1", (0, -650, 0, 400, -647, 2000))
    def tube(name, y0):
        return _box_body(top + " / 351306 FRONT - DECOR FRAME - DR:1 / %s:1 / Body1" % name, (0, y0, 0, 20, y0 + 20, 2000))
    on = c_geometry.check_bond_lines(ROOT, "assembly", [skin, tube("TUBE A", -647.0), tube("TUBE B", -647.0)], bt=3.0)
    assert [(f.rule, f.severity) for f in on] == [("bond-line", "severe")] and "2 frame member face(s)" in on[0].message
    ok = c_geometry.check_bond_lines(ROOT, "assembly", [skin, tube("TUBE A", -644.0), tube("TUBE B", -644.0)], bt=3.0)
    assert ok == []
    thick = c_geometry.check_bond_lines(ROOT, "assembly", [skin, tube("TUBE A", -642.0)], bt=3.0)
    assert [(f.rule, f.severity) for f in thick] == [("bond-line", "major")]
    far = c_geometry.check_bond_lines(ROOT, "assembly", [skin, tube("TUBE A", -630.0)], bt=3.0)   # 17 mm behind: not bonded
    assert far == []
    assert c_geometry.bond_t(ROOT) == 3.0              # the skeleton's own parameter
