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


def repeated_keys(path, name):
    """Keys written more than once in the dict literal assigned to `name` in a file: Python keeps only the last,
    so the earlier entry vanishes without a word (S51 was both D-126's profile and FRONT's decor blocks)."""
    import ast
    from collections import Counter
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            if isinstance(node.value, ast.Dict):
                keys = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
                return sorted(k for k, c in Counter(keys).items() if c > 1)
    raise AssertionError("no dict literal %s in %s" % (name, path))


def test_every_source_label_and_input_name_written_once():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs.py")
    assert repeated_keys(here, "SOURCES") == []
    assert repeated_keys(here, "P") == []


def test_a_repeated_label_is_found():
    """No pytest fixture: the README runs this file as a script, which calls each test with no arguments."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "x.py")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write('SOURCES = {\n    "S51": ("a", "b"),\n    "S50": ("c", "d"),\n    "S51": ("e", "f"),\n}\n')
        assert repeated_keys(f, "SOURCES") == ["S51"]


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
    """ISS-081, F-010: every roll-up line has a status word and a source and every piece but the glass is 20 kg or less
    (D-03); the pod as shipped is the CSV's sum less the voice kit's line, which the mechanical check leaves out by its
    name (PR #40); at 32 kg/m3 the air parts are the air report's own figure with fans; the allowances are assumptions; each
    applied saving is priced from the list itself (D-81, D-85)."""
    import re
    import csv
    import rollup
    rows = rollup.lines()
    for g, item, q, kg, st, src in rows:
        assert any(w in st for w in STATUS_WORDS), (item, st)
        assert src.strip(), item
        assert kg <= 20.0 or "glass" in item.lower() or "door unit" in item.lower(), (item, kg)
    later = [r for r in rows if r[0] == "LATER"]
    assert len(later) == 1 and "voice" in later[0][1].lower() and abs(later[0][3] - 4.0) < 1e-9, later
    shipped = sum(q * kg for g, _, q, kg, _, _ in rows if g != "LATER")
    assert abs(rollup.pod_kg(rows) - shipped) < 1e-9
    body = rollup.rollup_files()["out/parts-decided-P04.csv"].splitlines()
    assert body[0].split(",")[4] == "kg_total", body[0]
    kit = re.compile(r"outside the cap|voice cockpit kit reserve", re.I)      # tools/checks/c_parts.py, PR #40
    csv_rows = list(csv.reader(body[1:]))
    assert [r[1] for r in csv_rows if kit.search(r[1] + " " + r[5])] == [later[0][1]], "only the kit is outside the cap"
    csv_kg = sum(float(r[4]) for r in csv_rows if not kit.search(r[1] + " " + r[5]))
    assert abs(csv_kg - shipped) < 0.05, (csv_kg, shipped)
    # AIR from its CAD (PR #91): the lines add up to the parts list's 610000 plus the ruled changes its follow-up builds
    # (D-116 layers at 32, D-124 casings at 3 mm) and what the CAD doesn't model yet (D-121, the riser's foot, D-130's boot), nothing
    # twice; the fill moves only the column's and the soffit's fill, from the CAD's 32 kg/m3 (D-81)
    air = lambda f: sum(q * kg for g, _, q, kg, _, _ in rollup.lines(fill=f) if g == "AIR")
    k, A = rollup.AIR["kg"], rollup.AIR
    layers = 2 * A["n_layers"] * k["611302"] * (rollup.AA.CART_LAYER_KG_M3 / A["layer_rho"] - 1)
    casings = (k["611401"] + k["611402"]) * (rollup.AA.CASINGS[rollup.AA.FANBOX_CASING][2] / rollup.AIR_FBOX_T_CAD - 1)
    want = (k["610000"] - sum(A["register_hw"].values()) + layers + casings + sum(rollup.air_unmodelled().values())
            + rollup.AIR_RISER_FOOT_KG + rollup.AA.BOOT_KG)      # AIR's register hardware is in the fixings kit's line
    assert abs(air(32.0) - want) < 0.01, (air(32.0), want)
    assert abs(air(32.0) - air(rollup.FILL_LIGHT) - (k["611104"] + k["611203"]) * (1 - rollup.FILL_LIGHT / 32.0)) < 1e-9
    for name in ("Named clips",):                                  # the light shelf and ledge are INTERIOR's CAD now
        hit = [r for r in rows if r[1].startswith(name)]
        assert len(hit) == 1 and hit[0][4] == "assumption", (name, hit)
    assert len([r for r in rows if "ships loose" in r[1]]) == 2
    ap = rollup.applied()
    assert len(ap) == 8 and all(a[0] > 0 for a in ap), ap                    # D-81's four and D-85's four (its floor item went with D-132)
    off = rollup.lines(**rollup.OFF)
    assert abs(rollup.pod_kg(off) - rollup.pod_kg(rows) - sum(a[0] for a in ap)) < 1e-6, "the table adds up exactly"
    assert set(rollup.OFF) == set(rollup.ADOPTED)
    op = rollup.parked()
    assert len(op) == 2 and all(o[0] > 0 and o[2] and o[3] for o in op), op      # FRONT's CAD settled the decor frames
    names = [name for name, _ in rollup.REJECTED]
    assert any(n.startswith("Fixed glass") for n in names) and any("perimeters" in n for n in names), names   # D-82, D-85


def test_cad_masses_from_main():
    """The roll-up reads the merged parts lists (WALL L1, PR #41; FRONT's door unit, PR #27): those lines are the CAD's
    sums, marked as CAD on main, and every line has a basis; the swap table lists each one."""
    import rollup
    rows = {r[1]: r for r in rollup.lines()}
    ws = rollup.WALL_SIDE
    for item, a_, b_ in (("L1 and R1, lower side outer panels", 1, 2), ("L2 and R2, upper side outer panels", 3, 4)):
        line = rows[item]
        want = sum(ws[n]["frame"] + ws[n]["skin"] + ws[n]["fill"] + ws[n]["bond"] for n in (a_, b_)) / 2
        assert abs(line[3] - want) < 1e-9 and rollup.basis(line) == "CAD, main", line
    l1 = rows["L1 and R1, lower side outer panels"]
    cs = next(r for k, r in rows.items() if k.startswith("Wall cassette, side, lower"))
    assert abs(cs[3] - sum(ws[n]["tray"] + ws[n]["felt"] + ws[n]["cass_seals"] for n in (1, 2)) / 2) < 1e-9, cs
    assert rollup.basis(l1) == rollup.basis(cs) == "CAD, main"
    assert all(rollup.basis(r) in ("CAD, main", "CAD, main (part)", "CAD, open PR", "estimate") for r in rows.values())
    door = next(r for k, r in rows.items() if k.startswith("Door unit 360001"))
    d = {r["pn"]: r["kg"] for r in rollup.read_parts_list(rollup.FRONT_DOOR_LIST) if r["pn"]}
    assert abs(door[3] - d["360001"]) < 1e-9 and rollup.basis(door) == "CAD, main", door
    assert not [k for k in rows if k.startswith(("Floor panels", "Floor mat", "Door threshold"))]   # D-132: no floor
    key = rows["Corner key"]
    assert rollup.basis(key) == "CAD, main", key
    assert abs(key[2] * key[3] - sum(q * kg for q, kg in (rollup.JOINTS[pn] for pn in rollup.KEY_PNS))) < 1e-9, key
    hw = next(r for k, r in rows.items() if k.startswith("M6 bolts, rivnuts"))
    assert rollup.basis(hw) == "CAD, main (part)", hw
    assert "D-117" in hw[5] and "cleats assumption" in hw[4], hw                 # the cleat allowance rides on this line
    assert "cam" not in hw[1].lower(), hw                                          # D-116: no cam connectors
    rc, uk = rollup.register_counts(), rollup.fixings_unit_kg()
    assert set(rc) == set(uk) == set(rollup.FIXING_PNS), (rc, uk)
    (ns, ks), (nw, kw) = rollup.JOINTS["831001"], rollup.JOINTS["831002"]
    nt, kt = rollup.JOINTS["831010"]                  # DT's two 11 mm spigots on DR's ledge (D-157), on the same line
    assert nt == 2 and kt > 0, (nt, kt)
    want = sum(rc[pn] * uk[pn] for pn in rollup.FIXING_PNS) + ns * ks + nt * kt + nw * kw + rollup.CLEATS_KG
    assert abs(hw[3] - want) < 1e-9, (hw[3], want)
    fx = next(r for k, r in rows.items() if k.startswith("Fixed glass unit 360002"))
    f = {r["pn"]: r["kg"] for r in rollup.read_parts_list(rollup.FRONT_FIXED_LIST) if r["pn"]}
    assert abs(fx[3] - f["360002"]) < 1e-9 and rollup.basis(fx) == "CAD, main", fx
    cg = rollup.CEILING
    cp = rows["Ceiling outer panels C1 and C2, with their bond line"]
    assert abs(cp[3] - (cg["c1"] + cg["c2"]) / 2) < 1e-9 and rollup.basis(cp) == "CAD, main", cp
    cc = rows["Ceiling cassettes, one part for both halves"]
    assert rollup.basis(cc) == "CAD, main", cc
    el = next(r for k, r in rows.items() if k.startswith("Switches and harness"))
    assert abs(el[3] - rollup.ELEC["total"]) < 1e-9 and rollup.basis(el) == "CAD, main", el
    sh = next(r for k, r in rows.items() if k.startswith("Light shelf"))
    ld = next(r for k, r in rows.items() if k.startswith("Work-wall ledge"))
    assert abs(sh[3] - rollup.INTERIOR["shelf"]) < 1e-9 and rollup.basis(sh) == "CAD, main", sh
    it, el = rollup.INTERIOR, rollup.ELEC                     # S53: the shelf holds ELECTRICAL's profile parts, not D-126's old ones
    assert [pn for pn, _q, _m in el["hosted"].get("810201", [])] == it["shelf_elec"] and it["shelf_elec_kg"] > 0, it
    assert set(it["shelf_gone"]) <= set(rollup.SHELF_REPLACED), it
    assert abs(it["shelf"] - (it["shelf_listed"] - it["shelf_gone_kg"] + it["shelf_elec_added"])) < 1e-12, it
    assert all(pn not in el["hosted"] for pn in ("710000",)) and set(el["hosted"]) <= {"810201"}, el["hosted"]
    assert abs(ld[3] - rollup.INTERIOR["ledge"] - rollup.INTERIOR["rail"]) < 1e-9 and rollup.basis(ld) == "CAD, main", ld
    bb = rows["B1 to B4, back outer panels"]                                      # B1 and B2 from CAD (PR #152)
    k10, k12 = rollup.al_rhs(20, rollup.P04["frame_d"], rollup.T_STUD_LIGHT), rollup.al_rhs(20, rollup.P04["frame_d"], 1.2)
    want = (sum(rollup.back_cad_kg(n, rollup.FILL_LIGHT, k10, rollup.BACK_STUDS) for n in (1, 2))
            + 2 * rollup.back_est_kg(rollup.FILL_LIGHT, k12, k10, rollup.BACK_STUDS)) / 4
    assert abs(bb[3] - want) < 1e-9 and rollup.basis(bb) == "CAD, main (part)", bb
    for n in (1, 2):
        w = rollup.WALL_BACK[n]
        assert w["mid_n"] == rollup.BACK_STUDS and w["mid_t"] == rollup.T_STUD_LIGHT, w     # D-85's 2 studs at 1.0 mm
    cbl = next(r for k, r in rows.items() if k.startswith("Wall cassette, back, lower"))
    cad = sum(rollup.WALL_BACK[n]["tray"] + rollup.WALL_BACK[n]["felt"] + rollup.WALL_BACK[n]["cass_seals"] for n in (1, 2))
    assert abs(cbl[3] - cad / 2) < 1e-9 and rollup.basis(cbl) == "CAD, main", cbl
    for item, b in (("Decor block - left", "DL"), ("Decor block - right", "DR"), ("Decor block - top", "DT")):  # PR #105
        dl = rows[item]
        d = {r["pn"]: r["kg"] for r in rollup.read_parts_list(os.path.join(rollup.MANUF, "front",
                                                                           rollup.FRONT_DECOR[b]["path"])) if r["pn"]}
        assert abs(dl[3] - d[rollup.FRONT_DECOR_PN[b]]) < 1e-9 and rollup.basis(dl) == "CAD, main", dl
    assert rollup.FRONT_DECOR["DR"]["reserved"] == ["350004", "351402", "351403", "351404", "351405"]
    assert 0.5 < rollup.dr_channels_kg() < 0.6                                   # the right and diagonal channels
    bc = rollup.BASE_CAD          # D-132: BASE's soft lip by its length at the PM's kg/m; the door edge seals are FRONT's
    lip, gr = rows["Base seal: BASE's soft lip along the band pieces' inner faces"], rows["Cable grommets: the sealed cable holes"]
    assert abs(lip[2] - sum(bc["lip_m"].values())) < 1e-9 and lip[3] == p("lip_seal_kgm") == bc["lip_kgm"], lip
    assert gr[2] * gr[3] == p("grommet_kg"), gr
    assert len(rollup.cad_swaps()) == 27


def test_base_batch1_counts_once():
    """BASE's P02 batch 1 (S54): the list's own total is the sum of its rows, and every one of its parts is in exactly one
    roll-up line: the band pieces' own lines, the glide, load block and lip lines, the corner key line (the joints' 6 keys)
    or the fixings kit's line (the joints register's counts); nothing twice, nothing left out."""
    import rollup
    bc = rollup.BASE_CAD
    assert abs(bc["total"] - bc["top"]) < 1e-3, (bc["total"], bc["top"])          # 10.748 kg at e1ba6ef (10.68 at 8ff8f08)
    rows = {r[1]: r for r in rollup.lines()}
    band = [r for k, r in rows.items() if k.startswith(("Base band piece 100x40 - back", "Base band piece 100x40 - side",
                                                       "Base band piece FR1"))]
    assert len(band) == 4, [r[1] for r in band]
    glides = rows["Levelling glide (hex from above)"]
    blocks = next(r for k, r in rows.items() if k.startswith("Glide load blocks"))
    lip = rows["Base seal: BASE's soft lip along the band pieces' inner faces"]
    own = sum(r[2] * r[3] for r in band + [glides, blocks, lip])
    assert abs(own + bc["held_kg"] - bc["total"]) < 1e-9, (own, bc["held_kg"], bc["total"])
    held = set(rollup.KEY_PNS) | set(rollup.FIXING_PNS) | {"831001", "831002"}
    assert set(bc["held"]) <= held, bc["held"]
    rc, (ns, _), (nw, _) = rollup.register_counts(), rollup.JOINTS["831001"], rollup.JOINTS["831002"]
    count = {**{pn: rc[pn] for pn in rollup.FIXING_PNS}, "831001": ns, "831002": nw,
             **{pn: rollup.JOINTS[pn][0] for pn in rollup.KEY_PNS}}
    assert all(q <= count[pn] for pn, q in bc["held"].items()), (bc["held"], count)   # inside the other lines' counts
    assert glides[2] == sum(bc["glides"].values()) == sum(bc["blocks"].values()) == 9, (glides, bc["blocks"])
    assert blocks[2] == 1 and abs(blocks[3] - 9 * bc["doubler"]) < 1e-12, blocks   # one line, shared out by glide
    assert all(not a["own"] or all(pn not in held for pn, *_ in a["own"]) for a in bc["asm"].values())


def test_rollup_items_the_packing_plan_reads():
    """The packing plan (v2/07-Packaging/pack.py) takes, for each of its handles, the one roll-up line whose item text
    starts with it (PR #59), so each handle must match exactly one line here: keep the starts of the item texts fixed and
    put changes in the status or the source column (PR #50 renamed three and broke it)."""
    import ast
    import rollup
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "07-Packaging", "pack.py")
    if not os.path.exists(path):
        return
    tree = ast.parse(open(path, encoding="utf-8").read())
    handles = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "R" for t in n.targets))
    items = [r[1] for r in rollup.lines()]
    bad = {v: n for v in handles.values() for n in [sum(1 for i in items if i.startswith(v))] if n != 1}
    assert not bad, f"handles matching no line or several: {bad}"


P_DEFAULT_CEIL = p("ceil_t")

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"{len(tests)} tests passed")


def test_light_shelf_counts_electricals_rows_once():
    """INTERIOR's 810201 row holds ELECTRICAL's four down-light rows since #437 (its mass status names them), so the
    roll-up must not add them again (Reviewer 21 on #437): the shelf's mass equals its child rows totalled on their own,
    INTERIOR's three runs plus ELECTRICAL's rows under 810201."""
    import csv
    import rollup as R
    base = os.path.join(os.path.dirname(os.path.abspath(R.__file__)), "..", "..", "..", "03-Manufacturing")
    kids = 0.0
    for team, name in (("interior", "810000_P01_INTERIOR-PARTS-LIST_BOM.csv"), ("electrical", "710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv")):
        with open(os.path.join(base, team, name), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["parent"] == "810201":
                    kids += float(r["qty_per_parent"]) * float(r["mass_each_kg"])
    assert abs(R.INTERIOR["shelf"] - kids) < 0.002, (R.INTERIOR["shelf"], kids)
