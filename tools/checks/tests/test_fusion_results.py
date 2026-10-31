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
                     "max_mm": None},
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
