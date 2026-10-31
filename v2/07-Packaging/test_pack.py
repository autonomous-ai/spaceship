#!/usr/bin/env python3
"""Regression tests for pack.py. Run: python3 v2/07-Packaging/test_pack.py

Each test that changes the model restores it, so the tests run in any order.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack  # noqa: E402

# The joints register's section 3.9 as it stands in PR #23 at aed1590, so the parser is tested without the file.
REGISTER_39 = """
### 3.9 Bolt count

| Joint | Bolts | Bolt |
|---|---:|---|
| J-WALL-01 horizontal seams | 16 | M6 × 16 |
| J-WALL-02 back corners | 12 | M6 × 16 |
| J-WALL-03 back closing seams | 6 | M6 × 25 pin |
| J-BASE-01 walls on the base band | 16 | M6 × 16 |
| J-CEIL-01 walls to ceiling | 16 | M6 × 16 |
| J-CEIL-02 ceiling closing seam | 4 | M6 × 25 pin |
| J-FRONT-01 decor to walls | 12 | M6 × 16 |
| **Total** | **82** | 72 × M6 × 16, 10 × M6 × 25 |

### 3.10 Joint IDs against the layout study
"""


def failing(m):
    return [c["id"] for c in m.checks if not c["ok"]]


def test_all_checks_pass():
    m = pack.Model()
    assert m.ok(), failing(m)


def test_outputs_current():
    assert pack.main(["--check"]) == 0, "an output is stale: run python3 v2/07-Packaging/pack.py"


def test_register_parser(tmp=Path(__file__).resolve().parent / "_register_test.md"):
    tmp.write_text(REGISTER_39, encoding="utf-8")
    try:
        rows, total = pack.read_register(tmp)
    finally:
        tmp.unlink()
    assert total == 82
    assert rows == pack.REGISTER_PINNED, rows
    assert sum(c for c, s in rows.values() if s == "M6 x 25") == 10


def test_bolt_change_is_caught():
    st = next(s for s in pack.STEPS if s["n"] == 5)
    saved = copy.deepcopy(st["joints"])
    st["joints"]["J-WALL-02"] -= 1
    try:
        m = pack.Model()
        assert "K7" in failing(m)
    finally:
        st["joints"] = saved
    assert "K7" not in failing(pack.Model())


def test_heavy_piece_is_caught():
    p = pack.PIECE["2-03"]
    saved = p.extra_kg
    p.extra_kg = 5.0          # DR with its riser's share would pass 20 kg
    try:
        assert "K2" in failing(pack.Model())
    finally:
        p.extra_kg = saved


def test_rollup_line_lost_is_caught():
    p = pack.PIECE["2-21"]
    saved = list(p.mass)
    p.mass = [("FANBOX_E", 1)]   # drops the exhaust fans' half of the fans line
    try:
        assert "K1" in failing(pack.Model())
    finally:
        p.mass = saved


def test_overhang_is_caught():
    p = pack.PIECE["1-03"]
    saved = p.dims
    p.dims = pack.S(1455, 1225.5, 9)   # the floor panel with BASE P01's 19.5 mm lap
    try:
        assert "K4" in failing(pack.Model())
    finally:
        p.dims = saved


def test_time_within_limit():
    m = pack.Model()
    clock = m.time_total(pack.CLOCK_LAST_STEP) / 60
    assert clock <= pack.MINE["time_limit_min"].value, clock


def test_glass_order_in_crate():
    assert pack.PIECE[pack.CRATE_TAGS[-1]].step < pack.PIECE[pack.CRATE_TAGS[0]].step


def test_door_before_dt():
    door = next(s["n"] for s in pack.STEPS if "2-02" in s["tags"])
    dt = next(s["n"] for s in pack.STEPS if "2-12" in s["tags"])
    assert door < dt


def test_dr_bolts_before_air_column():
    dr = next(s["n"] for s in pack.STEPS if "2-03" in s["tags"])
    col = next(s["n"] for s in pack.STEPS if "2-11" in s["tags"])
    assert dr < col


def test_status_words():
    allowed = {"confirmed", "source", "calculation", "assumption", "unverified"}
    for k, v in {**pack.MINE, **pack.TIME}.items():
        assert v.status in allowed, (k, v.status)


def test_no_reserved_part_numbers():
    reserved = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}
    used = {p.pn for p in pack.PIECES} | {it["pn"] for it in pack.PACKAGING}
    assert not (used & reserved), used & reserved


def test_what_if_prices():
    base = pack.clock_min(pack.STEPS, pack.OTHER_FIXINGS)
    m = pack.Model()
    assert abs(base - m.time_total(pack.CLOCK_LAST_STEP) / 60) < 1e-9
    assert abs(pack.what_if([]) - base) < 1e-9
    for f in pack.FIXES:
        assert pack.what_if([f]) < base, f["id"]
    assert pack.what_if(pack.FIXES) < min(pack.what_if([f]) for f in pack.FIXES)
    # what_if works on copies: the guide's own steps are unchanged
    assert abs(pack.clock_min(pack.STEPS, pack.OTHER_FIXINGS) - base) < 1e-9


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    bad = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL {name}: {e}")
    print(f"{len(tests) - bad} of {len(tests)} passed")
    sys.exit(1 if bad else 0)
