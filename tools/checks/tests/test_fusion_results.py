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
