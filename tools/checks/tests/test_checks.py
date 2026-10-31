"""Offline tests for tools/checks. Run: python3 -m pytest tools/checks/tests -q

Each rule is shown firing on a bad input and staying quiet on a good one.
Real repo files are used where they exist (the Phase 0 proof part and the
skeleton P03 STEP); the rest is built in the test.
"""

import csv
import math
import os
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
    assert "C02|gap-KICK-OVER-THRESHOLD|skeleton KICK-OVER-THRESHOLD" in keys
    assert not any("LINING-FLOATS" in k for k in keys)          # the linings float in P03
    fixed = [_B("KICK", (-961, -709, 27, 214, -689, 105)), _B("THRESHOLD", (-961, -729, 0, 214, -669, 20))]
    assert c_geometry.check_gap_rules(ROOT, "skeleton", fixed, rules) == []


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
    rows = [{"kg_total": "400.0"}, {"kg_total": "26.7"}]
    fs, info = c_parts.check_pod_mass(str(tmp_path), rows, "list.csv")
    assert info["total_kg"] == pytest.approx(426.7) and [f.rule for f in fs] == ["pod-mass-over-cap"]
    fs, info = c_parts.check_pod_mass(str(tmp_path), [{"kg_total": "419"}], "list.csv")
    assert fs == []


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
        fh.write("part_number,name\n351001,x\n351002,x\n351003,x\n351004,x\n")
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
    # 351004 is a seal: its cut-list line defines it; plurals count too
    with open(tmp_path / "v2/03-Manufacturing/front/cut-list.csv", "a") as fh:
        fh.write("351005,x\n351006,x\n")
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
    assert "no cut list has a row" in fs["511303"]         # a DXF alone isn't D-89's route
