"""Offline tests for turning the Fusion check's JSON into findings
(tools/checks/run_fusion_checks.py). The Fusion script itself runs only
through the locked runner; its live run is recorded in the PR."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import run_fusion_checks as rf  # noqa: E402


def _bolt(**kw):
    b = {"bolt": "210000 WALL / 838001 HARDWARE - BOLT - M6 X 50:1 / Body1", "length_mm": 54.0, "dia_mm": 6.0,
         "head": [0, 0, 0], "axis": [0, 0, 1], "layers": [], "collisions": [], "tip_clearance": None,
         "tool": "socket", "tool_blocked_by": []}
    b.update(kw)
    return b


def rules_of(fs):
    return sorted(f.rule for f in fs)


def test_unlisted_clash_is_severe_and_listed_one_is_not_reported():
    res = {"clashes": [{"a": "x / 211101 A:1 / B1", "b": "x / 211201 B:1 / B2", "mm3": 12.5, "allowed": None},
                       {"a": "bolt", "b": "rivnut", "mm3": 30.0, "allowed": "BOLT-IN-THREAD"}]}
    fs = rf.findings_from(res, "assembly")
    assert rules_of(fs) == ["clash"] and fs[0].severity == "severe" and fs[0].evidence["mm3"] == 12.5


def test_gap_rule_results():
    res = {"gaps": [{"id": "KICK-OVER-THRESHOLD", "group": "", "gap_mm": 0.0, "a": "k", "b": "t", "min_mm": 7.0,
                     "max_mm": None, "severity": "severe", "method": "box"},
                    {"id": "LINING-FLOATS", "group": "", "gap_mm": 4.0, "a": "c", "b": "f", "min_mm": 4.0,
                     "max_mm": None}]}
    fs = rf.findings_from(res, "skeleton")
    assert [f.subject for f in fs] == ["skeleton KICK-OVER-THRESHOLD"] and fs[0].severity == "severe"


def test_bolt_running_into_a_wall_is_too_long():
    nut = {"body": "w / 838101 HARDWARE - RIVNUT - M6:1 / Body1", "from_head_mm": 42.0, "to_mm": 50.0, "is_nut": True}
    b = _bolt(layers=[nut], collisions=[{"body": "w / 211101 FRAME:1 / tube", "from_head_mm": 52.0, "to_mm": 54.0}])
    fs = rf.findings_from({"fasteners": [b]}, "assembly")
    assert "bolt-collides" in rules_of(fs) and all(f.severity == "severe" for f in fs if f.rule == "bolt-collides")


def test_short_engagement_and_good_engagement():
    nut = {"body": "w / 838101 HARDWARE - RIVNUT - M6:1 / Body1", "from_head_mm": 48.0, "to_mm": 58.0, "is_nut": True}
    short = rf.findings_from({"fasteners": [_bolt(layers=[nut])]}, "assembly")     # ends at 54 of 48..58
    assert rules_of(short) == ["short-engagement"]
    ok = rf.findings_from({"fasteners": [_bolt(length_mm=60.0, layers=[nut])]}, "assembly")
    assert ok == []


def test_nut_needs_a_thread_past_it_and_tip_clearance():
    nut = {"body": "w / 838201 HARDWARE - NUT - M6:1 / Body1", "from_head_mm": 48.0, "to_mm": 53.5, "is_nut": True}
    fs = rf.findings_from({"fasteners": [_bolt(layers=[nut])]}, "assembly")       # 0.5 mm past the nut
    assert rules_of(fs) == ["no-protrusion"]
    nut2 = dict(nut, to_mm=50.0)
    fs = rf.findings_from({"fasteners": [_bolt(layers=[nut2], tip_clearance={"body": "plate", "mm": 0.4})]},
                          "assembly")
    assert rules_of(fs) == ["tip-clearance"]


def test_tool_blocked_and_no_thread_found():
    clamp = {"body": "w / 211101 FRAME:1 / tube", "from_head_mm": 1.0, "to_mm": 40.0, "is_nut": False}
    fs = rf.findings_from({"fasteners": [_bolt(layers=[clamp], tool_blocked_by=[{"body": "lining", "mm3": 900.0}])]},
                          "assembly")
    assert rules_of(fs) == ["no-thread-found", "tool-blocked"]


def test_contacts_carry_part_numbers():
    res = {"touching": [{"a": "x / 211101 FRAME:1 / b", "b": "y / 838001 BOLT:1 / b", "gap_mm": 0.0},
                        {"a": "x / envelope", "b": "y / 211101", "gap_mm": 0.0}]}
    assert rf.contacts_from(res) == [("211101", "838001", "")]


def test_offline_run_cannot_close_a_fusion_clash():
    import register
    reg = {"next": 1, "findings": []}
    res = {"clashes": [{"a": "x / BAND-R:1 / Body1", "b": "x / DR:1 / Body1", "mm3": 14393.5, "allowed": None}]}
    fs = [f.to_dict() for f in rf.findings_from(res, "skeleton")]
    register.merge(reg, fs, "aaa", "2026-10-31", ["C01:skeleton/fusion"])
    _n, _r, closed = register.merge(reg, [], "bbb", "2026-10-31", ["C01:skeleton"])      # offline run
    assert closed == [] and reg["findings"][0]["status"] == "OPEN"
    _n, _r, closed = register.merge(reg, [], "ccc", "2026-10-31", ["C01:skeleton/fusion"])   # Fusion run, fixed
    assert closed == ["F-001"]


def test_live_fusion_result_on_the_bolt_fixture():
    """A recorded live run (tools/checks/tests/fixtures/bolt-joints-result.json,
    made by make_bolt_fixture.py and whole_pod_check.py through the lock):
    A M6 x 16 right, B M6 x 25 into the far wall, C M6 x 8 short in the
    rivnut, D M6 x 16 with a plate over its head."""
    import json
    import pytest
    p = os.path.join(HERE, "fixtures", "bolt-joints-result.json")
    if not os.path.exists(p):
        pytest.skip("no recorded Fusion run")
    res = json.load(open(p, encoding="utf-8"))
    fs = rf.findings_from(res, "fixture")
    by_case = {}
    for f in fs:
        for tag in "ABCD":
            if f.subject.endswith(" %s:1" % tag) or (" %s:1 " % tag) in f.subject or f.subject.split(" at ")[0].endswith(tag):
                by_case.setdefault(tag, set()).add(f.rule)
    rules = [(f.rule, f.subject) for f in fs]
    assert not any("X 16 ISO 4762 A" in s for _r, s in rules), rules          # the right bolt is clean
    assert any(r == "bolt-collides" and "X 25" in s for r, s in rules), rules
    assert any(r == "short-engagement" and "X 8" in s for r, s in rules), rules
    assert any(r == "tool-blocked" and "ISO 4762 D" in s for r, s in rules), rules
    assert any(r == "clash" and "FAR WALL B" in s for r, s in rules), rules   # the long bolt also clashes
    assert not any(r == "clash" and "RIVNUT" in s for r, s in rules), rules   # bolt in thread is allowed
    # the hex key turns 90 degrees toward the room: through the fill pocket it gets in (E), with no pocket not (F)
    assert not any(r == "tool-blocked" and "ISO 4762 E" in s for r, s in rules), rules
    assert any(r == "tool-blocked" and "ISO 4762 F" in s for r, s in rules), rules
    assert not any(x.startswith("/") for x in res["steps"] + [i["file"] for i in res["imports"]])   # no local paths


def test_door_swing_hit_is_severe_and_a_free_swing_is_quiet():
    hit = {"door_swing": [{"rule": "r", "max_deg": 90, "step_deg": 2, "direction": "outward", "moving": ["door"],
                           "first_hit": {"angle_deg": 96, "moving": "x / DOOR LEAF:1 / b",
                                         "hits": "x / DL FRONT - DECOR BLOCK - LEFT:1 / b", "mm3": 12.0}}]}
    fs = rf.findings_from(hit, "skeleton")
    assert [f.rule for f in fs] == ["door-swing"] and fs[0].severity == "severe" and "96" in fs[0].message
    free = {"door_swing": [{"rule": "r", "max_deg": 90, "step_deg": 2, "direction": "outward", "moving": ["door"],
                            "first_hit": None}]}
    assert rf.findings_from(free, "skeleton") == []



def test_exact_only_gap_on_the_skeleton_is_major():
    res = {"gaps": [{"id": "GLASS-TO-GLASS", "group": "", "gap_mm": 2.4, "a": "d", "b": "f", "min_mm": 3.9,
                     "max_mm": 4.1, "severity": "severe", "method": "exact"}]}
    assert [f.severity for f in rf.findings_from(res, "skeleton")] == ["major"]
    assert [f.severity for f in rf.findings_from(res, "assembly")] == ["severe"]


def test_saved_results_have_no_absolute_paths(tmp_path):
    res = {"steps": [os.path.join(rf.REPO_ROOT, "v2/03-Manufacturing/a.step"), "/elsewhere/b.step"],
           "imports": [{"file": os.path.join(rf.REPO_ROOT, "v2/03-Manufacturing/a.step"), "ok": True}]}
    out = rf._relative(res, rf.REPO_ROOT)
    assert out["steps"] == ["v2/03-Manufacturing/a.step", "b.step"]
    assert out["imports"][0]["file"] == "v2/03-Manufacturing/a.step"


def test_door_swing_a_seal_it_only_touches_is_not_a_collision():
    def swing(hits, first=None):
        return {"door_swing": [{"direction": "outward", "max_deg": 90.0, "rule": "x", "hits": hits, "first_hit": first}]}
    seal = {"hits": "360002 / 368003 FRONT - GLASS-TO-GLASS SEAL 180", "moving": "361001 FRONT - DOOR LEAF",
            "first_deg": 0.5, "last_deg": 0.5, "max_mm3": 0.3, "soft": True}
    assert rf.findings_from(swing([seal]), "assembly") == []          # the door wipes its seal: no finding
    crushed = dict(seal, max_mm3=650.0)
    fs = rf.findings_from(swing([crushed]), "assembly")
    assert [f.rule for f in fs] == ["door-swing"] and "650.0 mm3" in fs[0].message
    wall = {"angle_deg": 63.5, "moving": "361001 FRONT - DOOR LEAF", "hits": "350002 FRONT - DECOR BLOCK - DL", "mm3": 12.0}
    fs = rf.findings_from(swing([seal], wall), "assembly")
    assert len(fs) == 1 and "63.5 degrees" in fs[0].message


def test_d104_an_envelope_may_overlap_the_part_it_clamps_in_its_own_file_only():
    import csv
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    with open(os.path.join(root, "v2/04-Checks/config/clash-allow.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    door = "360001_P01_FRONT-DOOR-UNIT_CAD:1 / "
    own = {"a": door + "361001 FRONT - DOOR LEAF - 4+4 LAMINATED:1 / Body1",
           "b": door + "368102 FRONT - DOOR STRIKE - ENVELOPE:1 / Body1", "mm3": 11948.6}
    assert rf._allowed(own, rows) == "ENVELOPE-ON-ITS-PART"
    other = dict(own, a="350004_P01_FRONT-DECOR-BLOCK-DT_CAD:1 / 351401 FRONT - DT - SKIN:1 / Body1")
    assert rf._allowed(other, rows) is None                    # a clash with another file's part still counts
    named = dict(own, b=door + "368102 FRONT - DOOR STRIKE - SUGATSUNE HT-MSG62-U10:1 / Body1")
    assert rf._allowed(named, rows) is None                    # without ENVELOPE in its name it is a clash


def test_d104_a_skeleton_panel_envelope_is_not_a_hardware_stand_in():
    import csv
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    with open(os.path.join(root, "v2/04-Checks/config/clash-allow.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    skel = "100000_P04_POD-SKELETON_CAD:1 / "
    c = {"a": skel + "350000 FRONT:1 / DR ENVELOPE:1 / Body1", "b": skel + "110000 BASE:1 / BAND-R ENVELOPE:1 / Body1",
         "mm3": 14393.5}
    assert rf._allowed(c, rows) is None                        # F-006's kind of clash still counts


def test_a_screw_in_a_base_keys_tapped_hole_is_its_thread_not_a_clash():
    import csv
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    with open(os.path.join(root, "v2/04-Checks/config/clash-allow.csv"), newline="") as fh:
        rows = list(csv.DictReader(fh))
    base = "110000_P01_BASE_CAD:1 / "
    c = {"a": base + "111211 BASE - CORNER KEY - BACK - COMMON:1 / Body1",
         "b": base + "838010 HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2:1 / Body1", "mm3": 90.7}
    assert rf._allowed(c, rows) == "SCREW-IN-TAPPED-KEY"
    assert rf._allowed(dict(c, mm3=900.0), rows) is None       # far more than a thread's overlap
    wall = dict(c, a=base + "111101 BASE - BAND TUBE - SIDE - LH:1 / Body1")
    assert rf._allowed(wall, rows) is None                     # a screw into the band tube isn't a tapped key


def test_fusion_bolts_are_found_by_the_joints_registers_names():
    # D-99: hardware names come from the joints register, with the type first (HARDWARE - SOCKET HEAD BOLT - M6 X 16);
    # the Fusion script's pattern missed them, so no bolt was measured for thread engagement (C07)
    import ast
    import re
    import common
    src = open(os.path.join(rf.REPO_ROOT, "tools/checks/fusion/whole_pod_check.py"), encoding="utf-8").read()
    pats = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("FASTENER_RE", "NUT_RE"):
            pats[node.targets[0].id] = re.compile(node.value.args[0].value, re.I)
    names = common.register_names(rf.REPO_ROOT)
    bolts = {pn: n for pn, n in names.items() if re.search(r"\b(BOLT|SCREW)\b", n) and not re.search(r"\bNUT\b", n)}
    assert bolts, "the joints register lists bolts and screws"
    for pn, n in bolts.items():
        label = "110000_P01_BASE_CAD:1 / %s %s:1 / Body1" % (pn, n)
        assert pats["FASTENER_RE"].search(label) and not pats["NUT_RE"].search(label), n
    for n in ("838003 HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20",
              "831001 HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS"):
        assert not pats["FASTENER_RE"].search(n) or pats["NUT_RE"].search(n), n


def test_route_bodies_have_no_gap_rule_and_a_clash_names_both_teams():
    # D-92: ELECTRICAL's route bodies are reserved spaces for the gap rules; a clash still counts, owned by both teams
    tray = "410000_P01_CEILING_CAD:1 / 510301 LINING - CASSETTE - CEILING - COMMON (1):1 / 513101 LINING - TRAY - CEILING:2 / Body1"
    wire = "710000_P01_ELECTRICAL_CAD:1 / 710031 ELECTRICAL - DRAW WIRE - CEILING ROUTE:1 / Body5"
    res = {"steps": ["v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step",
                     "v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step"],
           "clashes": [{"a": tray, "b": wire, "mm3": 69.74, "allowed": None}],
           "gaps": [{"id": "LINING-FLOATS", "group": "", "gap_mm": 0.0, "a": tray, "b": wire.replace("Body5", "Body7"),
                     "min_mm": 4.0, "max_mm": None, "severity": "major", "method": "box", "owner": "WALL; CEILING"}]}
    fs = rf.findings_from(res, "assembly")
    assert [(f.check, f.severity, f.owner) for f in fs] == [("C01", "severe", "CEILING; ELECTRICAL")]



# ----------------------------------------------------------------- run on main 9e0dcd1 (the checker's own faults)

STEPS = ["/x/v2/03-Manufacturing/air/610000_P01_AIR_STEP.step",
         "/x/v2/03-Manufacturing/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step",
         "/x/v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step",
         "/x/v2/03-Manufacturing/base/110000_P01_BASE_STEP.step"]
RESERVED = {"351404": {"owner": "AIR"}}
ALLOW = [{"id": "BOLT-IN-THREAD", "a": r"\b(BOLT|SCREW)\b", "b": r"\b(RIVNUT|RIVET NUT|NUT|INSERT|CLINCH)\b",
          "max_mm3": "0"},
         {"id": "SCREW-IN-TAPPED-KEY", "a": r"\b(BOLT|SCREW)\b", "b": r"\b(CORNER|INLINE|KNEE) KEY\b",
          "max_mm3": "260"}]


def test_a_reserved_space_takes_its_owners_parts_but_no_one_elses():
    space = "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD:1 / 351404 FRONT - SUPPLY FAN BOX - DR - RESERVED AIR SPACE:1 / B1"
    res = {"steps": STEPS, "clashes": [
        {"a": "610000_P01_AIR_CAD:1 / 611402 AIR - FAN BOX CASING - SUPPLY:1 / Body1", "b": space, "mm3": 326455.5},
        {"a": space, "b": "710000_P01_ELECTRICAL_CAD:1 / 710023 ELECTRICAL - HARNESS - AIR COLUMN:1 / Body3",
         "mm3": 90.6}]}
    fs = rf.findings_from(res, "assembly", reserved=RESERVED)
    assert len(fs) == 1 and "710023" in fs[0].subject and fs[0].owner == "ELECTRICAL; FRONT"


def test_a_clash_reports_its_largest_overlap_once():
    a = "610000_P01_AIR_CAD:1 / 611101 AIR - COLUMN FACE - FRONT:1 / Body1"
    res = {"steps": STEPS, "clashes": [
        {"a": a, "b": "710000_P01_ELECTRICAL_CAD:1 / 710023 ELECTRICAL - HARNESS - AIR COLUMN:1 / Body1", "mm3": 217790.1},
        {"a": a, "b": "710000_P01_ELECTRICAL_CAD:1 / 710023 ELECTRICAL - HARNESS - AIR COLUMN:1 / Body5", "mm3": 247.1}]}
    fs = rf.findings_from(res, "assembly")
    assert len(fs) == 1 and fs[0].evidence["mm3"] == 217790.1 and fs[0].evidence["pairs"] == 2
    assert "largest of 2 body pairs" in fs[0].message and fs[0].owner == "CEILING; ELECTRICAL"


def _corner_bolt(**kw):
    b = _bolt(bolt="110000_P01_BASE_CAD:1 / 110103 BASE - BAND ASSY - BACK:1 / 838001 HARDWARE - SOCKET HEAD BOLT - "
                   "M6 X 16 - ISO 4762 8.8 ZINC:1 / Body1", length_mm=22.0, head=[-1217.8, 830.0, 37.5],
              layers=[{"body": "110000_P01_BASE_CAD:1 / 110101 BASE - BAND ASSY - SIDE - LH:1 / 111101 BASE - BAND TUBE "
                               "- SIDE - LH:1 / Body1", "from_head_mm": 6.5, "to_mm": 7.75, "is_nut": False},
                      {"body": "110000_P01_BASE_CAD:1 / 110103 BASE - BAND ASSY - BACK:1 / 111211 BASE - CORNER KEY - "
                               "BACK - COMMON:1 / Body1", "from_head_mm": 8.0, "to_mm": 37.75, "is_nut": False}],
              tool_blocked_by=[{"body": "110000_P01_BASE_CAD:1 / 110101 BASE - BAND ASSY - SIDE - LH:1 / 111101 BASE - "
                                        "BAND TUBE - SIDE - LH:1 / Body1", "segment": "room", "mm3": 438.3}])
    b.update(kw)
    return b


def test_a_screw_in_a_tapped_key_has_its_thread_and_needs_one_and_a_half_diameters():
    # F-017 / J-BASE-02: the base corner key is tapped; the stud engages 14 mm (22 - 8)
    assert rf.findings_from({"steps": STEPS, "fasteners": [_corner_bolt(tool_blocked_by=[])]}, "assembly",
                            allow_rows=ALLOW) == []
    # without the allow rule the key isn't known as a thread
    assert rules_of(rf.findings_from({"steps": STEPS, "fasteners": [_corner_bolt(tool_blocked_by=[])]},
                                     "assembly")) == ["no-thread-found"]
    # 8 mm of thread in it is under 1.5 x 6 = 9
    short = _corner_bolt(tool_blocked_by=[], layers=[dict(_corner_bolt()["layers"][1], from_head_mm=14.0)])
    fs = rf.findings_from({"steps": STEPS, "fasteners": [short]}, "assembly", allow_rows=ALLOW)
    assert rules_of(fs) == ["short-engagement"] and "9.0 mm" in fs[0].message and fs[0].owner == "BASE"


def test_a_factory_fitted_stud_is_only_blocked_by_its_own_band_piece():
    factory = [{"pattern": r"BAND ASSY[^/]*/ 8380(01|10)\b", "why": "J-BASE-02"}]
    fs = rf.findings_from({"steps": STEPS, "fasteners": [_corner_bolt()]}, "assembly", allow_rows=ALLOW)
    assert rules_of(fs) == ["tool-blocked"]                 # the side band goes on after it, on site
    assert rf.findings_from({"steps": STEPS, "fasteners": [_corner_bolt()]}, "assembly", allow_rows=ALLOW,
                            factory=factory) == []
    own_piece = {"body": "110000_P01_BASE_CAD:1 / 110103 BASE - BAND ASSY - BACK:1 / 111103 BASE - BAND TUBE - BACK:1 "
                         "/ Body1", "segment": "axis", "mm3": 50.0}
    fs = rf.findings_from({"steps": STEPS, "fasteners": [_corner_bolt(tool_blocked_by=[own_piece])]}, "assembly",
                          allow_rows=ALLOW, factory=factory)
    assert rules_of(fs) == ["tool-blocked"]


def test_a_bolt_is_never_blocked_by_its_own_bodies_and_a_stub_model_is_one_finding():
    bolt = "610000_P01_AIR_CAD:1 / 610201 AIR - SOFFIT:1 / 838002 HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC:1"
    whole = _bolt(bolt=bolt + " / Body2", length_mm=31.0,
                  layers=[{"body": "w / 838003 HARDWARE - RIVET NUT - M6:1 / Body1", "from_head_mm": 8.0,
                           "to_mm": 22.0, "is_nut": True}],
                  tool_blocked_by=[{"body": bolt + " / Body1", "segment": "axis", "mm3": 276.5}])
    assert rf.findings_from({"steps": STEPS, "fasteners": [whole]}, "assembly") == []
    stub = dict(whole, length_mm=7.0, layers=[])
    fs = rf.findings_from({"steps": STEPS, "fasteners": [stub]}, "assembly")
    assert rules_of(fs) == ["fastener-model"] and "31.0 mm" in fs[0].message and fs[0].owner == "CEILING"
    assert rf.nominal_length("HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2") == (6.0, 12.0, 15.3)
    assert rf.nominal_length("HARDWARE - BOLT - M6 X 50") is None


def test_a_saved_door_swing_that_moved_a_part_outside_the_door_is_set_aside():
    rows = [{"moving": "DOOR[- ]UNIT|DOOR LEAF|DOOR KICK STRIP", "fixed_exclude": "HINGE", "direction": "outward"}]
    swing = {"direction": "outward", "max_deg": 90.0, "rule": "r",
             "moving": ["360001_P01_FRONT-DOOR-UNIT_CAD:1 / 361001 FRONT - DOOR LEAF:1 / Body1",
                        "610000_P01_AIR_CAD:1 / 611105 AIR - KICK GRILLE:1 / Body1"],
             "first_hit": {"angle_deg": 0.5, "moving": "610000_P01_AIR_CAD:1 / 611105 AIR - KICK GRILLE:1 / Body1",
                           "hits": "x / 611103 AIR - COLUMN CORNER ANGLE:1 / Body1", "mm3": 400.0}, "hits": []}
    notes = []
    assert rf.findings_from({"door_swing": [swing]}, "assembly", door_rows=rows, notes=notes) == []
    assert notes and "611105 AIR - KICK GRILLE" in notes[0]
    good = dict(swing, moving=swing["moving"][:1],
                first_hit=dict(swing["first_hit"], moving=swing["moving"][0]))
    fs = rf.findings_from({"door_swing": [good]}, "assembly", door_rows=rows)
    assert rules_of(fs) == ["door-swing"] and fs[0].evidence["model"] == "assembly/fusion-swing"


def test_todays_allow_list_reads_a_saved_run_both_ways():
    # the run on 9e0dcd1 allowed AIR's HOLD riser transition through the fixed glass under HOLD-ON-GLASS; the rule is
    # now for one file's own HOLD hardware on its own glass, so the saved clash comes back
    hold_on_glass = {"id": "HOLD-ON-GLASS", "a": r"\bHOLD\b", "b": "DOOR LEAF|FIXED GLASS|LAMINATED", "max_mm3": "0",
                     "scope": "same-file"}
    res = {"steps": STEPS, "clashes": [
        {"a": "610000_P01_AIR_CAD:1 / 618103 AIR - RISER TRANSITION - HOLD:1 / Body1",
         "b": "360002_P01_FRONT-FIXED-GLASS-UNIT_CAD:1 / 361003 FRONT - FIXED GLASS - 4+4 LAMINATED:1 / Body1",
         "mm3": 152005.9, "allowed": "HOLD-ON-GLASS"},
        {"a": "360001_P01_FRONT-DOOR-UNIT_CAD:1 / 361001 FRONT - DOOR LEAF - 4+4 LAMINATED:1 / Body1",
         "b": "360001_P01_FRONT-DOOR-UNIT_CAD:1 / 368101 FRONT - DOOR HINGE - HOLD - H1 BOTTOM:1 / Body1",
         "mm3": 105120.0, "allowed": "HOLD-ON-GLASS"}]}
    fs = rf.findings_from(res, "assembly", allow_rows=[hold_on_glass])
    assert len(fs) == 1 and "618103" in fs[0].subject and fs[0].evidence["mm3"] == 152005.9
    assert rf.findings_from(res, "assembly") == []           # no list given: the run's own marks stand
