"""Regression tests for the layout study. Run from the layout-study folder: python3 scripts/test_layout.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inputs import P, SOURCES, override, p  # noqa: E402

STATUS_WORDS = {"confirmed", "source", "calculation", "assumption", "unverified"}
# The decided build in this study's own parts list, at this revision (LS-01). It is over the 420 kg cap: the clip
# and bond allowances that the sound and air check leaves out settle on the wall sample. D-54: the cap stays and
# this estimate stays open against it (ISS-080), so the total may not grow past this figure.
DECIDED_KG_CEILING = 426.71


def decided_parts():
    from v2_model import FINAL, parts_for
    with override(wall_t_plan=p("final_wall_t"), ceil_t=p("final_ceil_t")):
        return parts_for("plan", FINAL)


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
    # 72 + 36 before the 1207 back and ceiling frames (one more bolt or clip per back and ceiling edge at the 400 mm
    # counting pitch) and the third air part (2 cartridges and the riser, 2 bolts each)
    assert t["bolts"] == 78 and t["cams"] == 38, (t["bolts"], t["cams"])
    assert 123 <= t["elapsed_min"] <= 127, t["elapsed_min"]
    heavy = [pt.pid for pt in parts if pt.ship not in ("glass", "none") and pt.kg > 20.0]
    assert not heavy, heavy
    kg = total(parts)
    assert kg <= DECIDED_KG_CEILING + 0.05, f"decided build grew to {kg:.2f} kg (LS-01)"
    if kg > p("cap_kg") + 0.05:
        from run_all import build
        report = build()["report.md"]
        assert f"{kg - p('cap_kg'):,.1f} kg over" in report, "the report must say the decided build is over the cap"
    assert s["n_std"] == 1 and s["n_long"] == 1, (s["n_std"], s["n_long"])
    names = [pt.name for pt in parts]
    assert not any("FAN OPENING" in n for n in names), "fans sit in the decor blocks, not in the ceiling"


def test_decided_shell_follows_the_skeleton():
    """D-49, D-55, D-57: frame-to-frame back wall and ceiling, 1495 side walls, decor 205, 85 mm kick strip."""
    byid = {pt.pid: pt for pt in decided_parts()}
    for pid in ("W-BACK-LO", "W-BACK-UP", "C-HALF"):
        assert round(byid[pid].dims[1]) == 1207, (pid, byid[pid].dims)
    for pid in ("L-CASS-BACK-LO", "L-CASS-BACK-UP", "L-CASS-HALF"):
        assert round(byid[pid].dims[1]) == 1169, (pid, byid[pid].dims)
    assert round(byid["W-SIDE-LO"].dims[1]) == 1495, byid["W-SIDE-LO"].dims
    assert [round(d) for d in byid["L-CASS-SIDE-LO"].dims[:2]] == [1145, 1448], byid["L-CASS-SIDE-LO"].dims
    assert [round(d) for d in byid["L-CASS-SIDE-UP"].dims[:2]] == [1098, 1448], byid["L-CASS-SIDE-UP"].dims
    for pid in ("F-DL", "F-DR", "F-DT"):
        assert min(byid[pid].dims) == 205, (pid, byid[pid].dims)
    assert round(max(byid["F-GLASS-DOOR"].dims)) == 2096, byid["F-GLASS-DOOR"].dims   # 2011 glass + 85 kick strip


def test_decided_air_is_four_12v_fans_in_two_cartridges():
    """D-51: both paths in the right decor block, a riser for the exhaust; no TD-500, no old silencers."""
    parts = decided_parts()
    air = [pt for pt in parts if pt.assy == "AIR"]
    assert sorted(pt.pid for pt in air) == ["A-CART-EXHAUST", "A-CART-SUPPLY", "A-RISER"], [pt.pid for pt in air]
    for pt in air:
        if pt.pid.startswith("A-CART"):
            assert "2 x 12 V FANS" in pt.name, pt.name
            assert abs(pt.kg - (p("cart_kg") + 2 * p("fan12_kg"))) < 1e-9, pt.kg
    assert not any(pt.pid in ("F-DECOR-FILL", "A-FAN") or pt.pid.startswith("A-SIL") for pt in parts)
    text = " ".join(f"{pt.name} {pt.note}" for pt in parts)
    text += " ".join(f"{v.source} {v.note}" for v in P.values()) + " ".join(a for a, _ in SOURCES.values())
    assert "TD-500" not in text and "TD500" not in text


def test_only_the_five_status_words():
    """Brief: confirmed, source, calculation, assumption or unverified; a decided value is confirmed with its decision."""
    from run_all import OPTIONS
    from v2_model import parts_for
    bad = [(k, v.status) for k, v in P.items() if v.status not in STATUS_WORDS]
    assert not bad, bad
    for o in OPTIONS.values():
        bad = [(pt.pid, pt.status) for pt in parts_for(o["split"], o["m"], o["split_long"]) if pt.status not in STATUS_WORDS]
        assert not bad, bad
    bad = [(pt.pid, pt.status) for pt in decided_parts() if pt.status not in STATUS_WORDS]
    assert not bad, bad
    for k, v in P.items():   # confirmed = a PM decision (D-xx, or a PR ruling not logged yet) or the approved plan (S05)
        if v.status == "confirmed":
            assert any(c in v.source for c in ("D-", "PR #", "S05")), f"{k}: a confirmed value cites its decision ({v.source})"


def test_p04_rollup_lines():
    """ISS-081: every roll-up line has a status word and a source, the total is their sum, every piece but the glass is
    20 kg or less (D-03), the air parts are the air report's 61.8 kg with fans, and the five savings are ranked."""
    import rollup
    rows = rollup.lines()
    for g, item, q, kg, st, src in rows:
        assert any(w in st for w in STATUS_WORDS), (item, st)
        assert src.strip(), item
        assert kg <= 20.0 or "glass" in item.lower() or "door unit" in item.lower(), (item, kg)
    assert abs(rollup.pod_kg(rows) - sum(q * kg for _, _, q, kg, _, _ in rows)) < 1e-9
    air = sum(q * kg for g, _, q, kg, _, _ in rows if g == "AIR")
    assert abs(air - 61.8) < 0.05, air
    sv = rollup.savings()
    assert len(sv) == 5 and all(s[0] > 0 for s in sv)
    assert [s[0] for s in sv[:4]] == sorted((s[0] for s in sv[:4]), reverse=True), "savings 1 to 4 ranked by kg"


P_DEFAULT_CEIL = p("ceil_t")

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"{len(tests)} tests passed")
