"""Regression tests for the layout study. Run from the layout-study folder: python3 scripts/test_layout.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inputs import override, p  # noqa: E402


def test_nested_override_keeps_outer_values():
    """Reviewer 2: an inner override used to drop the outer one's keys on exit (wall thickness fell back to 38 mm)."""
    base = p("wall_t_plan")
    with override(wall_t_plan=81):
        with override(wall_t_plan=81, ceil_t=81):
            assert p("ceil_t") == 81
        assert p("wall_t_plan") == 81, "outer override lost after the inner one exited"
        assert p("ceil_t") == P_DEFAULT_CEIL, "inner-only key must go back to its default"
    assert p("wall_t_plan") == base


def test_decided_build_counts_and_limits():
    from assembly import sequence, timing
    from pallets import pack, summary
    from v2_model import FINAL, parts_for, total
    with override(wall_t_plan=p("final_wall_t"), ceil_t=p("final_ceil_t")):
        parts = parts_for("plan", FINAL)
        s = summary(pack(parts))
        t = timing(sequence("plan", FINAL, parts, False, s["n_std"], s["n_long"]))
    assert t["bolts"] == 72 and t["cams"] == 36, (t["bolts"], t["cams"])
    assert 123 <= t["elapsed_min"] <= 127, t["elapsed_min"]
    heavy = [pt.pid for pt in parts if pt.ship not in ("glass", "none") and pt.kg > 20.0]
    assert not heavy, heavy
    assert total(parts) <= p("cap_kg") + 0.05, total(parts)
    assert s["n_std"] == 1 and s["n_long"] == 1, (s["n_std"], s["n_long"])
    names = [pt.name for pt in parts]
    assert not any("FAN OPENING" in n for n in names), "fans sit in the decor blocks, not in the ceiling"


P_DEFAULT_CEIL = p("ceil_t")

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"{len(tests)} tests passed")
