"""Build every number, table, CSV and pallet diagram of the layout study, and render report.md.

    python3 scripts/run_all.py          # rebuild out/ and report.md
    python3 scripts/run_all.py --check  # rebuild in memory and fail if report.md or out/ differ

Needs Python 3.10+ and openpyxl. The STEP cross-check data (data/v1_step_solids.csv) comes from
step_crosscheck.py, which needs cadquery-ocp and is not run here.
"""
import csv
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from assembly import TOOL, corridor_turn_max, doorway, sequence, timing  # noqa: E402
from floors import floor_options  # noqa: E402
from inputs import P, SOURCES, override, p  # noqa: E402
from pallets import IN_PER_MM, LB_PER_KG, pack, summary, svg  # noqa: E402
from v1_weights import biggest_v1_parts, step_crosscheck, v1_weights  # noqa: E402
from quiet import LAYOUTS, quiet_rows  # noqa: E402
from v2_model import (ASSEMBLIES, FAST, FINAL, FRONT_LABEL, LIGHT, PLAN, by_assembly, connectors, decor_skin_area,  # noqa: E402
                      decor_skin_area_bom, fastener_counts, gasket_length_m, glass_area, joints, parts_for, total, variant)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "out")

OPTIONS = {
    "A": dict(split="plan", m=PLAN, split_long=False, title="Plan as written",
              desc="The plan's materials and split, raised steel floor as knock-down bars, decor blocks whole."),
    "B1": dict(split="plan", m=FAST, split_long=False, title="Plan split, light build, fast assembly, 2 pallets (DECIDED)",
               desc="Same panel split as the plan, light build with the fast-assembly changes, thin floor inside an aluminium base band; decor blocks, long base band pieces and glass ride one 96x48 pallet."),
    "B2": dict(split="plan", m=FAST, split_long=True, title="As B1, decor and base band split to fit 48x40 (rejected)",
               desc="As B1, but the decor blocks are cut in half and the base band pieces stand upright, so everything except the glass goes on 48x40 pallets."),
    "C": dict(split="bands", m=FAST, split_long=False, title="Horizontal bands, light build, fast assembly (rejected)",
              desc="Walls in 5 stacked horizontal bands per wall (like Orangebox Air3); long pieces on one long pallet."),
}


def f0(x):
    return f"{x:,.0f}"


def f1(x):
    return f"{x:,.1f}"


def table(head, rows, align=None):
    align = align or ["l"] + ["r"] * (len(head) - 1)
    sep = ["---:" if a == "r" else "---" for a in align]
    lines = ["| " + " | ".join(head) + " |", "| " + " | ".join(sep) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(lines)


def flag(pt):
    if pt.ship == "glass":
        return "glass (exempt)"
    return "OVER 20 kg" if pt.kg > 20.0 else ""


def parts_table(parts):
    rows = []
    for pt in parts:
        dims = " x ".join(f0(d) for d in sorted(pt.dims, reverse=True)) if pt.ship != "none" else "-"
        rows.append([pt.pid, f"{pt.name} / {pt.name_vi}", pt.assy, dims, pt.qty, f1(pt.kg), f1(pt.total), flag(pt), pt.status])
    rows.append(["", "**Total**", "", "", sum(pt.qty for pt in parts if pt.ship != "none"), "", f"**{f1(total(parts))}**", "", ""])
    return table(["ID", "Part (English / Vietnamese)", "Assembly", "Size mm", "Qty", "kg each", "kg", "20 kg check", "Status"], rows,
                 ["l", "l", "l", "l", "r", "r", "r", "l", "l"])


def option_results():
    res = {}
    for key, o in OPTIONS.items():
        parts = parts_for(o["split"], o["m"], o["split_long"])
        pals = pack(parts, rebalance=not o["split_long"])   # B2's point is to keep everything but the glass on 48x40
        s = summary(pals)
        steps = sequence(o["split"], o["m"], parts, o["split_long"], s["n_std"], s["n_long"])
        res[key] = dict(o=o, parts=parts, pallets=pals, sum=s, steps=steps, time=timing(steps),
                        joints=joints(o["split"], o["m"], o["split_long"]), conn=connectors(o["split"]))
    return res


def waterfall():
    steps = [("v2 as planned (steel frames, 6 mm plywood, raised steel floor, 10 mm glass, table)", {}, "source + calculation"),
             ("Remove the table; the pod ships empty", dict(table=False), "confirmed (Dee)"),
             ("Thin floor inside an aluminium base band instead of the raised steel frame", dict(floor="thin"), "PROPOSED"),
             ("Aluminium 20x20 frames instead of steel (walls, ceiling, decor)", dict(frame="al"), "PROPOSED"),
             ("No plywood behind the ACP; frame members at 400 mm to keep the ACP flat", dict(ply=False), "PROPOSED"),
             ("8 mm tempered glass instead of 10 mm", dict(front="glass8"), "PROPOSED"),
             ("Add gaskets on every panel joint, sealed glazing profiles, door drop seal", dict(seals=True), "plan requirement"),
             ("Add 2 silenced vents and an occupancy sensor for automatic fans", dict(vents=True, sensor=True), "plan requirement"),
             ("Add light cavity fill (20 mm PET) in wall and ceiling bays", dict(fill=True), "assumption (sound group sizes it)"),
             ("Hold 4 kg for the later voice cockpit kit", dict(voice=True), "Dee's scope addition")]
    m = dict(PLAN)
    rows, prev = [], None
    for text, change, status in steps:
        m = variant(m, **change)
        t = total(parts_for("plan", m, False))
        rows.append((text, status, None if prev is None else t - prev, t))
        prev = t
    assert all(m[k] == LIGHT[k] for k in LIGHT if k not in ("key", "label")), "waterfall must end at the light build"
    return rows


def alternatives():
    base = total(parts_for("plan", LIGHT, False))
    alts = [("Front: smoked acrylic 8 mm (door and fixed panel)", dict(front="acrylic8"),
             "Room uses an acrylic booth door; scratches more, needs a stiffer door frame or hinges rated for acrylic; sound check decides."),
            ("Front: smoked acrylic 10 mm", dict(front="acrylic10"), "Stiffer door; same notes."),
            ("Front: 4+4 laminated acoustic glass", dict(front="lam44"), "About the weight of 8 mm, quieter (sound group)."),
            ("Front: 10 mm tempered glass (as v1)", dict(front="glass10"), "Reference."),
            ("Walls and ceiling: foam-core sandwich (same ACP face, 25 mm foam, 0.5 mm aluminium inner skin)", dict(core="foam"),
             "Stiff and flat without studs; factory-bonded; fire behaviour of the core to check for the later US rules."),
            ("Walls and ceiling: aluminium honeycomb sandwich (same ACP face on a 10 mm honeycomb panel)", dict(core="honeycomb"),
             "Heaviest of the light options here because the ACP face sits on a full honeycomb panel."),
            ("No floor at all (base band only)", dict(floor="none"), "Weakest for sound (open to the room floor)."),
            ("Raised steel floor kept (plan)", dict(floor="raised"), "Reference.")]
    rows = []
    for text, change, note in alts:
        t = total(parts_for("plan", variant(LIGHT, **change), False))
        rows.append((text, t - base, t, note))
    return base, rows


def acp_sensitivity():
    """kg per 0.1 kg/m2 change of the ACP areal mass (all ACP in the light build)."""
    t0 = total(parts_for("plan", LIGHT, False))
    with override(acp3_kgm2=p("acp3_kgm2") + 0.1):
        t1 = total(parts_for("plan", LIGHT, False))
    return t1 - t0


def levers():
    """Time saved by each DECIDED fast-assembly change, added one at a time to option B1 as first studied (light build)."""
    o = OPTIONS["B1"]
    changes = [("Factory subassemblies: decor blocks with skins on (already), door hinges and pull fitted in the factory so the door lifts onto its pins, fixed glass pre-glazed in its profile frame",
                dict(prehung=True), "DECIDED"),
               ("Captive M6 bolts, already started in their panels, that can't be dropped", dict(captive=True), "DECIDED"),
               ("Tool-free cam or clip connectors on every panel-to-panel seam; panels sit on pins or hooks and hold themselves (bolts stay where loads go to the base, ceiling, decor and hinges)",
                dict(cams=True), "DECIDED"),
               ("Felt pre-fitted on the panels; only a loose strip over each joint goes on site", dict(prefit=True), "DECIDED"),
               ("Pallets packed in assembly order, parts numbered", dict(ordered=True), "packaging, no design change")]

    def run(m):
        parts = parts_for(o["split"], m, o["split_long"])
        s = summary(pack(parts))
        return timing(sequence(o["split"], m, parts, o["split_long"], s["n_std"], s["n_long"]))

    m = dict(LIGHT)
    before = run(m)
    rows, prev = [], before
    for text, change, status in changes:
        m = variant(m, **change)
        t = run(m)
        rows.append((text, status, prev["elapsed_min"] - t["elapsed_min"], t["elapsed_min"], t["bolts"], t["cams"]))
        prev = t
    assert all(m[k] == FAST[k] for k in FAST if k not in ("key", "label")), "levers must end at the fast build"
    return before, rows, prev


def build():
    files = {}
    N = {}
    # ---------------- v1
    v1, v1_lines = v1_weights()
    N["v1_lo"], N["v1_bom"], N["v1_hi"] = (f0(sum(v1[c].values())) for c in ("lo", "bom", "drawing"))
    rows = [[a, f0(v1["lo"][a]), f0(v1["bom"][a]), f0(v1["drawing"][a])] for a in ASSEMBLIES]
    rows.append(["**Total**", f"**{N['v1_lo']}**", f"**{N['v1_bom']}**", f"**{N['v1_hi']}**"])
    N["table_v1"] = table(["Assembly", "Low: BOM, light densities", "BOM as written", "High: 15 mm boards (drawings, STEP), heavy densities"], rows)
    pieces = biggest_v1_parts()
    over = [f"{k} {f0(v)} kg" for k, v in pieces.items() if v > 20 and k not in ("GL", "GW")]
    N["v1_over20"] = ", ".join(over)
    N["v1_over20_n"] = str(len(over))
    xc = step_crosscheck()
    names = {"board_15": ("Inner lining and floor boards", "m2"), "board_12": ("12 mm back-centre lining", "m2"),
             "board_6": ("6 mm boards behind the skins", "m2"), "skin_2": ("2 mm ACP skins", "m2"),
             "glass_10": ("10 mm glass", "m2"), "timber": ("40x40 timber frame", "m3"), "base_tube": ("Steel floor-frame tube", "m3")}
    rows = []
    for k, qb, qs, kb, ks in xc:
        nm, unit = names[k]
        dec = 3 if unit == "m3" else 2
        rows.append([nm, f"{qb:.{dec}f} {unit}", f"{qs:.{dec}f} {unit}", f0(kb), f0(ks)])
    N["table_v1_step"] = table(["Item", "BOM quantity", "STEP quantity", "kg (BOM, 9 mm boards)", "kg (STEP, 15 mm boards)"], rows)
    files["out/v1-bom-lines.csv"] = csv_text(["code", "spec", "kind", "assembly", "kg_bom_case"],
                                             [[c, s, k, a, f"{kg:.2f}"] for c, s, k, a, kg in v1_lines])

    # ---------------- v2 weights
    plan_parts = parts_for("plan", PLAN, False)
    light_parts = parts_for("plan", LIGHT, False)
    N["plan_total"] = f0(total(plan_parts))
    N["light_total"] = f0(total(light_parts))
    bp, bl = by_assembly(plan_parts), by_assembly(light_parts)
    rows = [[a, f1(bp[a]), f1(bl[a]), f1(bl[a] - bp[a])] for a in ASSEMBLIES]
    rows.append(["**Total**", f"**{f1(total(plan_parts))}**", f"**{f1(total(light_parts))}**", f"**{f1(total(light_parts) - total(plan_parts))}**"])
    N["table_assy"] = table(["Assembly", "v2 as planned, kg", "Light indoor build, kg", "Change, kg"], rows)
    wf = waterfall()
    N["table_waterfall"] = table(["Step", "Status", "Change, kg", "Running total, kg"],
                                 [[t, s, "" if d is None else f1(d), f1(tt)] for t, s, d, tt in wf], ["l", "l", "r", "r"])
    base, alts = alternatives()
    N["table_alts"] = table(["Variant (one change to the light build)", "Change, kg", "Total, kg", "Note"],
                            [[t, f"{d:+.1f}", f1(tt), n] for t, d, tt, n in alts], ["l", "r", "r", "l"])
    alt = {t: (d, tt) for t, d, tt, n in alts}
    N["acrylic8_total"] = f0(alt["Front: smoked acrylic 8 mm (door and fixed panel)"][1])
    N["acrylic8_delta"] = f0(-alt["Front: smoked acrylic 8 mm (door and fixed panel)"][0])
    N["acrylic10_total"] = f0(alt["Front: smoked acrylic 10 mm"][1])
    N["lam_total"] = f0(alt["Front: 4+4 laminated acoustic glass"][1])
    N["foam_delta"] = f1(alt["Walls and ceiling: foam-core sandwich (same ACP face, 25 mm foam, 0.5 mm aluminium inner skin)"][0])
    N["acp_sens"] = f1(acp_sensitivity())
    N["margin"] = f1(300 - total(light_parts))
    N["table_parts_light"] = parts_table(light_parts)
    N["table_parts_plan"] = parts_table(plan_parts)
    heavy_plan = [pt for pt in plan_parts if pt.kg > 20 and pt.ship != "glass"]
    N["plan_over20"] = ", ".join(f"{pt.pid} {f1(pt.kg)} kg" for pt in heavy_plan) or "none"
    heavy_light = [pt for pt in light_parts if pt.kg > 20 and pt.ship != "glass"]
    N["light_over20"] = ", ".join(f"{pt.pid} {f1(pt.kg)} kg" for pt in heavy_light) or "none"
    nonglass = [pt for pt in light_parts if pt.ship not in ("glass", "none")]
    hv = max(nonglass, key=lambda pt: pt.kg)
    N["light_heaviest"] = f"{hv.name.split(' - ')[-1].lower()} ({hv.pid}) at {f1(hv.kg)} kg"
    N["dr_kg"] = f1([pt for pt in light_parts if pt.pid == "F-DR"][0].kg)
    N["door_glass8"] = f1([pt for pt in light_parts if pt.pid == "F-GLASS-DOOR"][0].kg)
    N["fixed_glass8"] = f1([pt for pt in light_parts if pt.pid == "F-GLASS-FIXED"][0].kg)
    N["glass_area_door"] = f"{glass_area('door'):.2f}"
    N["glass_area_fixed"] = f"{glass_area('fixed'):.2f}"
    N["decor_area_step"] = f"{sum(decor_skin_area(b) for b in ('DL', 'DR', 'DT')):.2f}"
    N["decor_area_bom"] = f"{sum(decor_skin_area_bom(b) for b in ('DL', 'DR', 'DT')):.2f}"
    N["gasket_m"] = f1(gasket_length_m("plan"))
    for key, prts in (("plan", plan_parts), ("light", light_parts)):
        files[f"out/parts-weights-{key}.csv"] = parts_csv(prts)

    # ---------------- options
    res = option_results()
    rows = []
    for k, r in res.items():
        s, t = r["sum"], r["time"]
        n_parts = sum(pt.qty for pt in r["parts"] if pt.ship != "none")
        nb, nc = fastener_counts(r["o"]["split"], r["o"]["m"], r["o"]["split_long"])
        rows.append([f"**{k}**", r["o"]["title"], f0(total(r["parts"])), n_parts, f"{nb} + {nc}", r["conn"],
                     f"{s['n_std']} + {s['n_long']}", f0(s["kg"]), f0(s["max_h"]), f1(s["pcf"]), f0(t["elapsed_min"]),
                     f1(t["person_h"])])
        files[f"out/parts-option-{k}.csv"] = parts_csv(r["parts"])
        for i, pal in enumerate(r["pallets"], 1):
            files[f"out/pallets-{k}-{i}-{pal['kind']}.svg"] = svg(pal, f"Option {k}, pallet {i} of {len(r['pallets'])}")
    N["table_options"] = table(["Option", "What it is", "Pod kg", "Parts", "M6 bolts + clips", "Cable connectors", "Pallets 48x40 + 96x48",
                                "Shipped kg (gross)", "Max loaded height mm", "Density lb/ft3", "Assembly, min (2 people)", "Person-hours"],
                               rows, ["l", "l", "r", "r", "r", "r", "r", "r", "r", "r", "r", "r"])
    for k, r in res.items():
        N[f"{k}_parts"] = parts_table(r["parts"])
        N[f"{k}_pallets"] = pallets_table(k, r["pallets"])
        N[f"{k}_joints"] = table(["Joint", "What it joins", "Edges", "M6 bolts"], [[j[0], j[1], j[2], j[3]] for j in r["joints"]] +
                                 [["", "**Total**", "", f"**{sum(j[3] for j in r['joints'])}**"]], ["l", "l", "r", "r"])
        N[f"{k}_steps"] = steps_table(r["steps"], r["time"])
        s = r["sum"]
        N[f"{k}_elapsed"] = f0(r["time"]["elapsed_min"])
        N[f"{k}_ph"] = f1(r["time"]["person_h"])
        N[f"{k}_bolts"] = str(r["time"]["bolts"])
        N[f"{k}_gross"] = f0(s["kg"])
        N[f"{k}_npal"] = str(s["n"])
        N[f"{k}_pcf"] = f1(s["pcf"])
        N[f"{k}_maxh"] = f0(s["max_h"])
        N[f"{k}_total"] = f0(total(r["parts"]))
    b1 = res["B1"]["pallets"]
    N["B1_std_kg"] = f0(b1[0]["gross"])
    N["B1_std_h"] = f0(b1[0]["height"])
    N["B1_long_kg"] = f0(b1[-1]["gross"])
    N["B1_long_h"] = f0(b1[-1]["height"])
    N["B1_long_items"] = ", ".join(sorted({i["pid"] for lay in b1[-1]["layers"] for i in lay["items"]}))
    longest = max(max(pt.dims) for pt in res["B1"]["parts"] if pt.ship != "none")
    N["longest_piece"] = f0(longest)
    N["longest_in"] = f1(longest * IN_PER_MM)
    N["bolts_C_extra"] = str(res["C"]["time"]["bolts"] + res["C"]["time"]["cams"] - res["B1"]["time"]["bolts"] - res["B1"]["time"]["cams"])

    # ---------------- floors
    fl = floor_options()
    N["table_floors"] = table(["Floor", "BASE kg (light build)", "vs thin floor, kg", "Step at the door, mm", "Sound", "Square and stiff",
                               "Levelling", "Cables", "Assembly", "Look", "Status"],
                              [[r["name"], f1(r["kg"]), f"{r['delta_thin']:+.1f}", f0(r["step"]), r["sound"], r["square"], r["level"],
                                r["cables"], r["assembly"], r["look"], r["status"]] for r in fl],
                              ["l", "r", "r", "r", "l", "l", "l", "l", "l", "l", "l"])
    fd = {r["key"]: r for r in fl}
    N["raised_vs_thin"] = f0(fd["raised"]["delta_thin"])
    N["castor_vs_thin"] = f0(fd["castors"]["delta_thin"])
    N["castor_step"] = f0(fd["castors"]["step"])
    N["thin_step"] = f0(fd["thin"]["step"])
    N["raised_step"] = f0(fd["raised"]["step"])

    # ---------------- assembly: before and after the fast-assembly changes
    before, lv, after = levers()
    N["table_levers"] = table(["Change (each added to the ones above)", "Status", "Saves, min", "Assembly after it, min", "M6 bolts", "Cam or clip connectors"],
                              [["Option B1 as first studied (light build, everything bolted, felt on site)", "-", "", f0(before["elapsed_min"]), before["bolts"], before["cams"]]] +
                              [[t, st, f0(d), f0(e), b, c] for t, st, d, e, b, c in lv], ["l", "l", "r", "r", "r", "r"])
    N["before_min"], N["after_min"] = f0(before["elapsed_min"]), f0(after["elapsed_min"])
    N["before_ph"], N["after_ph"] = f1(before["person_h"]), f1(after["person_h"])
    N["before_bolts"], N["after_bolts"], N["after_cams"] = str(before["bolts"]), str(after["bolts"]), str(after["cams"])
    N["saved_min"] = f0(before["elapsed_min"] - after["elapsed_min"])
    N["tool"] = TOOL
    with override():
        tb = parts_for("tallback", FAST)
    back_full = [pt for pt in tb if pt.pid == "W-BACK-FULL"][0]
    N["tallback_kg"] = f1(back_full.kg)
    N["fast_total"] = f0(total(parts_for("plan", FAST)))

    # ---------------- quiet build re-check (PM ruling: about 380 kg, cap 400 kg)
    qr = quiet_rows()
    lab = {(sp, lf): t for sp, lf, t in LAYOUTS}
    rows = []
    for r in qr:
        s_ = r["sum"]
        rows.append([f0(r["target"]), f"+{r['dt']} mm", "walls and ceiling" if r["ceiling"] else "walls only", lab[(r["split"], r["leaf"])],
                     f1(r["x"]), f"{r['heaviest'].pid} {f1(r['heaviest'].kg)}", str(len(r["over"])) if r["over"] else "0",
                     f"{s_['n_std']} + {s_['n_long']}", f"{f0(r['std_gross'])} / {f0(r['long_gross'])}", f0(s_["max_h"]), f0(r["time"]["elapsed_min"])])
    N["table_quiet"] = table(["Pod kg", "Walls thicker by", "Sound mass on", "Layout", "Added kg/m2", "Heaviest part, kg (not glass)",
                              "Parts over 20 kg", "Pallets 48x40 + 96x48", "Heaviest 48x40 / 96x48 gross kg", "Max height mm", "Assembly min"],
                             rows, ["r", "r", "l", "l", "r", "l", "r", "r", "r", "r", "r"])
    def pick(target, dt, ceiling, split, leaf):
        return [r for r in qr if r["target"] == target and r["dt"] == dt and r["ceiling"] == ceiling and r["split"] == split and r["leaf"] == leaf][0]
    q_in = pick(p("quiet_total"), 20, True, "plan", False)
    q_leaf = pick(p("quiet_total"), 20, True, "plan", True)
    q_leaf60 = pick(p("quiet_total"), 40, True, "plan", True)
    q_cap = pick(p("quiet_cap"), 40, True, "plan", True)
    side_in = [pt for pt in parts_of(q_in) if pt.pid == "W-SIDE-LO"]
    N["q_side_in"] = f1(max(pt.kg for pt in q_in_parts(q_in, "W-SIDE")))
    N["q_ceil_in"] = f1(max(pt.kg for pt in q_in_parts(q_in, "C-HALF")))
    N["q_leaf_heaviest"] = f"{q_leaf['heaviest'].pid} at {f1(q_leaf['heaviest'].kg)} kg"
    N["q_leaf_max"] = f1(max(pt.kg for pt in q_in_parts(q_leaf, "L-LEAF")))
    N["q_leaf_pallets"] = f"{q_leaf['sum']['n_std']} + {q_leaf['sum']['n_long']}"
    N["q_leaf60_pallets"] = f"{q_leaf60['sum']['n_std']} + {q_leaf60['sum']['n_long']}"
    N["q_leaf_min"] = f0(q_leaf["time"]["elapsed_min"])
    N["q_leaf60_min"] = f0(q_leaf60["time"]["elapsed_min"])
    N["q_leaf_std"] = f0(q_leaf["std_gross"])
    N["q_cap_ok"] = "every part stays at 20 kg or less" if not q_cap["over"] else f"{len(q_cap['over'])} parts go over 20 kg"
    # ---------------- final stack (sound study's DECIDED wall), B1 layout
    with override(wall_t_plan=p("final_wall_t"), ceil_t=p("final_ceil_t")):
        fparts = parts_for("plan", FINAL)
        fpals = pack(fparts)
        fs = summary(fpals)
        ft = timing(sequence("plan", FINAL, fparts, False, fs["n_std"], fs["n_long"]))
        fsteps = sequence("plan", FINAL, fparts, False, fs["n_std"], fs["n_long"])
    files["out/parts-option-B1-final-stack.csv"] = parts_csv(fparts)
    for i, pal in enumerate(fpals, 1):
        files[f"out/pallets-B1F-{i}-{pal['kind']}.svg"] = svg(pal, f"Option B1 with the final wall stack, pallet {i} of {len(fpals)}")
    N["final_total"] = f0(total(fparts))
    fh = sorted((pt for pt in fparts if pt.ship not in ("glass", "none")), key=lambda pt: -pt.kg)
    N["final_heaviest"] = f"{fh[0].pid} at {f1(fh[0].kg)} kg"
    N["final_over20"] = str(sum(1 for pt in fh if pt.kg > 20.0))
    N["final_npal"] = f"{fs['n_std']} + {fs['n_long']}"
    N["final_gross"] = f0(fs["kg"])
    N["final_pcf"] = f1(fs["pcf"])
    N["final_maxh"] = f0(fs["max_h"])
    N["final_min"] = f0(ft["elapsed_min"])
    N["final_ph"] = f1(ft["person_h"])
    N["final_bolts"], N["final_cams"] = str(ft["bolts"]), str(ft["cams"])
    N["final_pallets"] = pallets_table("B1F", fpals)
    N["final_steps"] = steps_table(fsteps, ft)
    shell = [pt for pt in fparts if pt.pid.startswith(("W-", "C-", "L-CASS"))]
    N["final_shell_table"] = table(["Part", "Size mm", "Qty", "kg each", "20 kg check"],
                                   [[f"{pt.pid}: {pt.name}", " x ".join(f0(d) for d in sorted(pt.dims, reverse=True)), pt.qty, f1(pt.kg), flag(pt)]
                                    for pt in shell], ["l", "l", "r", "r", "l"])
    side = [pt for pt in fparts if pt.pid == "W-SIDE-LO"][0]
    cas = [pt for pt in fparts if pt.pid == "L-CASS-SIDE-LO"][0]
    N["final_wall_kgm2"] = f1((side.kg + cas.kg) / (side.dims[0] * side.dims[1] * 1e-6))
    N["final_kgm2_hw"] = f1(p("final_kgm2_hw"))
    N["final_wall_t"], N["final_ceil_t"] = f0(p("final_wall_t")), f0(p("final_ceil_t"))
    N["hw_385_total"], N["hw_385_dsa"] = f0(p("hw_385_total")), f1(p("hw_385_dsa"))
    with override(wall_t_plan=p("final_wall_t"), ceil_t=p("final_ceil_t")):
        cf = parts_for("plan", variant(FINAL, ceil_fill_on_cassette=False))
    N["ceil_outer_with_fill"] = f1([pt for pt in cf if pt.pid == "C-HALF"][0].kg)
    N["inner_w_final"] = f0(p("pod_w") - 2 * p("final_wall_t"))
    N["final_cassettes"] = str(sum(pt.qty for pt in fparts if pt.pid.startswith("L-CASS")))
    N["pitch_count"] = f0(p("bolt_pitch"))
    N["hw_380_total"] = f0(p("hw_380_total"))
    N["hw_380_dsa"] = f1(p("hw_380_dsa"))

    # ---------------- doorway
    d = doorway(res["B1"]["parts"]) + [r for r in doorway(res["A"]["parts"]) if r["pid"].startswith(("B-RAIL", "B-JOIST", "B-BOARD", "I-"))]
    N["table_doorway"] = table(["Part", "Size mm (long x mid x thin)", "kg", "Width needed on edge, mm", "914 x 2032 doorway", "813 mm clear (ADA)"],
                               [[r["pid"], " x ".join(f0(x) for x in r["dims"]), f1(r["kg"]), f0(r["need_w"]),
                                 "passes" if r["ok_nom"] else "FAILS", "passes" if r["ok_clear"] else "FAILS"] for r in d],
                               ["l", "l", "r", "r", "l", "l"])
    N["doorway_fails"] = str(sum(1 for r in d if not r["ok_clear"]))
    N["turn_1200"] = f0(corridor_turn_max(1200, 1200))
    N["turn_914"] = f0(corridor_turn_max(1200, 914))

    # ---------------- inputs
    rows = [[k, f"{v.value:g}", v.unit, v.status, v.source, v.note] for k, v in P.items() if k != "table_v1_kg"]
    N["table_inputs"] = table(["Name", "Value", "Unit", "Status", "Source", "Note"], rows, ["l", "r", "l", "l", "l", "l"])
    N["table_sources"] = table(["ID", "What it says", "Where"], [[k, a, f"`{b}`" if not b.startswith("http") else b] for k, (a, b) in SOURCES.items()],
                               ["l", "l", "l"])
    N["kg_per_lb"] = f"{1 / LB_PER_KG:.4f}"
    # ---------------- derived numbers quoted in the text
    fast_parts = parts_for("plan", FAST)
    fw = [pt for pt in fast_parts if pt.pid.startswith(("W-", "C-"))]
    N["fast_panel_min"], N["fast_panel_max"] = f0(min(pt.kg for pt in fw)), f0(max(pt.kg for pt in fw))
    fhv = max((pt for pt in fast_parts if pt.ship not in ("glass", "none")), key=lambda pt: pt.kg)
    N["fast_heaviest"] = f"{fhv.pid} at {f1(fhv.kg)} kg"
    wall_like = [pt for pt in light_parts if pt.pid.startswith(("W-", "C-"))]
    N["light_panel_min"] = f0(min(pt.kg for pt in wall_like))
    N["light_panel_max"] = f0(max(pt.kg for pt in wall_like))
    side = [pt for pt in light_parts if pt.pid == "W-SIDE-LO"][0]
    N["light_wall_kgm2"] = f1(side.kg / (side.dims[0] * side.dims[1] * 1e-6))
    N["ply_kgm2"] = f1(6e-3 * p("rho_ply"))
    N["height_gain"] = f0(fd["raised"]["step"] - fd["thin"]["step"])
    N["none_vs_thin"] = f0(-fd["none"]["delta_thin"])
    N["B1_hours"] = f1(res["B1"]["time"]["elapsed_min"] / 60)
    N["levers_hours"] = f1(after["elapsed_min"] / 60)
    deficit = total(light_parts) - 300.0
    N["acp_needed"] = f1(p("acp3_kgm2") - max(deficit, 0.0) / acp_sensitivity() * 0.1)
    from v2_model import geom, panel_kg  # noqa: E402
    N["full_wall_kg"] = f0(panel_kg(p("wall_depth"), geom()["wall_h"], LIGHT))
    bands = [pt for pt in res["C"]["parts"] if pt.pid.endswith("BAND")]
    N["band_min"], N["band_max"] = f0(min(pt.kg for pt in bands)), f0(max(pt.kg for pt in bands))
    N["band_extra_seams"] = str(5 - 2)
    N["conn_extra_C"] = str(res["C"]["conn"] - res["B1"]["conn"])
    N["v1_fl_kg"] = f0(pieces["FL"])
    with override(acp2_kgm2=2e-3 * p("rho_al"), acp3_kgm2=3e-3 * p("rho_al")):
        solid = v1_weights()[0]["bom"]
    N["v1_solid_al_delta"] = f0(sum(solid.values()) - sum(v1["bom"].values()))
    N["hand_clear"] = f0(p("hand_clear"))
    N["door_clear_w"] = f0(p("door_clear_w"))
    N["tool_power"] = (f"Hold {p('voice_kit_w'):.0f} W for the kit on its own fused circuit from the power inlet, "
                       "and add it to the electrical group's power budget next to the fans and lights.")
    N["pitch_acp"] = f0(p("stud_pitch_acp"))
    tmpl = open(os.path.join(ROOT, "report_template.md"), encoding="utf-8").read()
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", tmpl)) - set(N))
    if missing:
        raise KeyError(f"template keys without a value: {missing}")
    report = re.sub(r"\{\{(\w+)\}\}", lambda mo: N[mo.group(1)], tmpl)
    files["report.md"] = report
    return files


def q_in_parts(r, prefix):
    return [pt for pt in r["parts"] if pt.pid.startswith(prefix)]


def parts_of(r):
    return r["parts"]


def csv_text(head, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(head)
    w.writerows(rows)
    return buf.getvalue()


def parts_csv(parts):
    return csv_text(["id", "name", "name_vi", "assembly", "size_mm", "qty", "kg_each", "kg_total", "ships_as", "status", "note"],
                    [[pt.pid, pt.name, pt.name_vi, pt.assy, " x ".join(f"{d:.0f}" for d in sorted(pt.dims, reverse=True)),
                      pt.qty, f"{pt.kg:.2f}", f"{pt.total:.2f}", pt.ship, pt.status, pt.note] for pt in parts])


def pallets_table(key, pals):
    rows = []
    for i, pal in enumerate(pals, 1):
        if pal["kind"] == "48x40":
            content = sorted({it["pid"] for s in pal["slots"] for it in s["items"]})
        else:
            content = sorted({it["pid"] for lay in pal["layers"] for it in lay["items"]})
        fn = f"out/pallets-{key}-{i}-{pal['kind']}.svg"
        rows.append([f"[{i}: {pal['kind']} in]({fn})", f0(pal["L"]) + " x " + f0(pal["W"]), f0(pal["gross"]), f0(pal["lb"]),
                     f0(pal["height"]) + f" ({pal['height'] * IN_PER_MM:.1f} in)", f1(pal["cuft"]), f1(pal["pcf"]), ", ".join(content)])
    return table(["Pallet (diagram)", "Deck mm", "Gross kg", "Gross lb", "Loaded height mm", "ft3", "lb/ft3", "Carries"], rows,
                 ["l", "l", "r", "r", "r", "r", "r", "l"])


def steps_table(steps, t):
    rows = []
    for i, s in enumerate(steps, 1):
        rows.append([i, s["name"], s["lifts"], s["bolts"], f1(s["two"] / 60), f1(s["one"] / 60), s["access"]])
    rows.append(["", f"**Elapsed for 2 people, with {p('inefficiency') * 100:.0f} % for hand-offs**", t["lifts"], t["bolts"], "", "",
                 f"**{t['elapsed_min']:.0f} min ({t['person_h']:.1f} person-hours)**"])
    return table(["#", "Step", "Lifts", "M6 bolts", "2-person min", "1-person min (shared)", "Access check"], rows,
                 ["r", "l", "r", "r", "r", "r", "l"])


def main():
    check = "--check" in sys.argv
    files = build()
    bad = []
    for rel, text in sorted(files.items()):
        path = os.path.join(ROOT, rel)
        if check:
            try:
                cur = open(path, encoding="utf-8").read()
            except FileNotFoundError:
                cur = None
            if cur != text:
                bad.append(rel)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
    if check:
        stale = sorted(set(os.listdir(OUT)) - {os.path.basename(k) for k in files if k.startswith("out/")})
        bad += [f"out/{s} (not produced by the scripts)" for s in stale]
        if bad:
            print("NOT REPRODUCED:\n  " + "\n  ".join(bad))
            sys.exit(1)
        print(f"OK: report.md and {len(files) - 1} output files reproduce exactly.")
    else:
        produced = {os.path.basename(k) for k in files if k.startswith("out/")}
        for name in sorted(set(os.listdir(OUT)) - produced):
            os.remove(os.path.join(OUT, name))      # out/ belongs to this script: drop files it no longer makes
        print(f"wrote report.md and {len(files) - 1} output files")


if __name__ == "__main__":
    main()
