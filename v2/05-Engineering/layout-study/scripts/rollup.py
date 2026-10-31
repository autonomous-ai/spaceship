"""Weight roll-up on skeleton P04 (ISS-081, F-010): the decided build recounted with tonight's rulings and CAD masses.

The base is this study's decided build (option B1 with the final stack, skeleton P03). Each line is replaced where a
newer number exists: the teams' CAD masses (CEILING PR #32, FRONT PRs #27 and #28, the WALL group's L1), the air parts as
sized for D-60 (the air report, section 7f), and this study's own model re-run at skeleton P04's sizes for the parts with
no CAD yet. Every line carries its status and its source (SOURCES in inputs.py). run_all.py writes weight-rollup.md and
out/parts-decided-P04.csv from here, and its --check proves they reproduce.
"""
import os
import sys

from inputs import p
from shapes import al_rhs, plate_kg
from v2_model import FINAL, final_leaf_kg, final_outer_kg, parts_for, total

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "acoustics-air"))
import calc as AA  # noqa: E402  (the air report's own model: D-60's air parts)

CAP_KG = 420.0          # confirmed, D-37 and D-54
D71_KG = 429.3          # the PM's running estimate (D-71, S39), for the cross-check
D71_LEFT_OUT = 1.3 + 0.5 + 2.1   # corner tubes, bond, floor foam: D-71's "not in the sum yet" (S39)

# Skeleton P04 sizes, mm (S33)
P04 = dict(side_w=1492.74, side_h=1142.74, side_up_h=1142.74, back_w=1200.61, back_h=1118.61,
           side_cass_l=1445.0, side_cass_lo_h=1142.74, side_cass_up_h=1092.74, back_cass_w=1166.0,
           back_cass_lo_h=1118.61, back_cass_up_h=1116.87, floor_w=1210.0, floor_d=1455.0, ceil_w=1200.61,
           wall_depth=1495.0, frame_d=40.0)
# The teams' CAD masses, kg (status calculation: CAD geometry x density)
WALL_L1_MADE, WALL_L1_BOND = 11.35, 0.49                      # S34
CEIL_PANEL, CEIL_CASS = 9.586, 9.816                          # S35 (P03 build; the P04 cassette is 1160 x 1045)
CEIL_TRAY = (1163.0, 1048.0)                                  # S35: the cassette tray's outline as built
CEIL_FILL_M2 = 1.11674 * (0.33875 + 0.33875 + 0.27475)        # S35: the three fill strips on each cassette's back
DOOR_UNIT, DOOR_GLASS = 50.17, 43.891                         # S36
FIXED_UNIT, FIXED_GLASS = 29.58, 28.584                       # S37
LIP_KG = 0.43                 # confirmed, D-69: each wall cassette with the 12 mm lips (S39)
CORNER_TUBES_KG = 1.3         # confirmed, D-63 (S39)
BOND_OVER_KG = 0.5            # calculation, PR #23 via D-71: bond over this study's 0.25 kg/m2 (S39)
FLOOR_T, FOAM_KG = 9.0, 2.1   # confirmed, D-72 (9 mm plywood); calculation, D-76 (3 mm foam at about 200 kg/m3) (S39)
# Savings inputs
LAM33_T, LAM44_T = 6.76, 8.76  # mm: 3+3 and 4+4 laminate (glass 3 + 0.76 PVB + 3, as the 4+4 is 4 + 0.76 + 4)
FILL_LIGHT = 25.0             # kg/m3, D-54's lighter grade (S30, S31)
CLIP_KG, CATCH_KG = 0.04, 0.10  # assumption: a clip-only fixing, about 40 g a clip and 100 g a catch lanyard (H03, H04)
BAND_T_LIGHT = 1.5            # mm: the base band's wall, against this study's 2.0 (an assumption, S07)


def base_parts():
    """This study's decided build on skeleton P03 (option B1 with the final stack)."""
    return parts_for("plan", FINAL)


def base_parts_kg(pid):
    """kg each of one part in this study's decided build (P03)."""
    return [pt for pt in base_parts() if pt.pid == pid][0].kg


def stile_delta_kg():
    """A 40 x 40 back stile over the 20 x 40 member it replaces, one side panel high (calculation)."""
    return (al_rhs(40, 40, p("t_al_final")) - al_rhs(20, 40, p("t_al_final"))) * P04["side_h"] * 1e-3


def lines():
    """[(group, item, qty, kg_each, status, source)] for the pod on skeleton P04, tonight's numbers."""
    base = {pt.pid: pt for pt in base_parts()}
    L = []
    side_a = P04["side_w"] * P04["side_h"] * 1e-6
    l1 = WALL_L1_MADE + WALL_L1_BOND
    L.append(("WALL", "L1 and R1, lower side outer panels (R1 is L1's mirror)", 2, l1, "calculation (CAD)",
              "S34: 11.35 kg of made parts + 0.49 kg of bond"))
    L.append(("WALL", "L2 and R2, upper side outer panels, the same size and build", 2,
              final_outer_kg(P04["side_w"], P04["side_up_h"], P04["frame_d"], FINAL), "calculation",
              "this study's model at the P04 size (S33)"))
    L.append(("WALL", "B1 to B4, back outer panels", 4, final_outer_kg(P04["back_w"], P04["back_h"], P04["frame_d"], FINAL),
              "calculation", "this study's model at the P04 size (S33)"))
    L.append(("WALL", "40 x 40 corner edge tubes beyond L1 and R1's back stiles", 1,
              CORNER_TUBES_KG - 2 * stile_delta_kg(), "calculation", "D-63's 1.3 kg less L1 and R1's two stiles (S34, S39)"))
    L.append(("WALL", "Bond over this study's 0.25 kg/m2, beyond L1 and R1", 1,
              BOND_OVER_KG - 2 * (WALL_L1_BOND - p("bond_kgm2") * side_a), "calculation",
              "D-71's 0.5 kg (PR #23) less L1 and R1's share (S34, S39)"))
    for item, w, h in (("side, lower", P04["side_cass_l"], P04["side_cass_lo_h"]),
                       ("side, upper", P04["side_cass_l"], P04["side_cass_up_h"]),
                       ("back, lower", P04["back_cass_w"], P04["back_cass_lo_h"]),
                       ("back, upper", P04["back_cass_w"], P04["back_cass_up_h"])):
        L.append(("LINING", f"Wall cassette, {item}, with 12 mm lips", 2, final_leaf_kg(w, h) + LIP_KG,
                  "calculation; lips confirmed", "this study's model at the P04 size (S33) + 0.43 kg of lips (D-69, S39)"))
    ceil_bond = p("bond_kgm2") * P04["ceil_w"] * P04["wall_depth"] * 1e-6
    L.append(("CEILING", "Ceiling outer panels C1 and C2, with their bond line", 2, CEIL_PANEL + ceil_bond,
              "calculation (CAD); bond assumption", "S35 + this study's 0.25 kg/m2 bond on the P04 46 mm panel"))
    clip_ceil = p("leaf_clip_kgm2") * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6
    L.append(("LINING", "Ceiling cassettes, one part for both halves, with a clip and catch allowance", 2,
              CEIL_CASS + clip_ceil, "calculation (CAD); clips assumption",
              "S35 + this study's 0.6 kg/m2 clip allowance (the clips and catches are HOLD there)"))
    notes = {"B-THRESH": "this study's model (D-72's 13 mm profile isn't modelled yet)",
             "B-KEY": "this study's model", "B-GLIDE": "this study's model"}
    for pid in ("B-BAND-BACK", "B-BAND-SIDE", "B-BAND-FRONT-L", "B-BAND-FRONT-R", "B-KEY", "B-GLIDE", "B-THRESH"):
        pt = base[pid]
        L.append(("BASE", f"{pt.name.split(' - ', 1)[1].capitalize()}", pt.qty, pt.kg, pt.status,
                  notes.get(pid, "this study's model (P03 lengths; P04's faceted front band is about 0.2 m shorter)")))
    fa = P04["floor_w"] * P04["floor_d"] * 1e-6
    L.append(("BASE", "Floor panels, 9 mm plywood with a 0.3 kg/m2 finish", 2, plate_kg(fa, FLOOR_T, p("rho_ply")) + fa * 0.3,
              "confirmed (9 mm); calculation", "D-72 (S39) at the P04 size (S33); plywood 600 kg/m3 (S13)"))
    L.append(("BASE", "Floor mat, 3 mm firm closed-cell foam", 1, FOAM_KG, "calculation", "D-76 (S39), BASE Engineer"))
    for pid in ("F-DL", "F-DR", "F-DT"):
        pt = base[pid]
        L.append(("FRONT", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status,
                  "this study's model from v1's STEP shapes (S02)"))
    L.append(("FRONT", "Door unit 360001: 4+4 leaf, kick strip, drop seal, hinges, lock, pull", 1, DOOR_UNIT,
              "calculation (CAD)", "S36"))
    L.append(("FRONT", "Fixed glass unit 360002: 4+4 pane, U-profiles and seals", 1, FIXED_UNIT, "calculation (CAD)", "S37"))
    for name, size, kg, basis in AA.d60_parts():
        L.append(("AIR", name, 1, kg, "calculation", "S38: " + basis))
    L.append(("AIR", "Four 12 V fans", 1, AA.fans_kg(), "assumption", "S38: 0.3 kg each until the sample is weighed"))
    for pid in ("K-SEALS", "E-KIT", "E-VOICE-RESERVE", "K-FIX"):
        pt = base[pid]
        L.append((pt.assy, pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status, "this study's model"))
    return L


def pod_kg(rows=None):
    return sum(q * kg for _, _, q, kg, _, _ in (rows or lines()))


def savings():
    """The five best savings that keep the look and the sound targets: (kg, what changes, risk, owner), ranked."""
    fill_m2_walls = 4 * P04["side_w"] * P04["side_h"] * 1e-6 + 4 * P04["back_w"] * P04["back_h"] * 1e-6
    w, d, l = (x / 1000 for x in AA.D60["cart"])
    fill_air_m3 = 2 * AA.D60["fill"] / 1000 * (w + d) * l
    fill_kg = (p("fill_pet_kgm3") - FILL_LIGHT) * (P04["frame_d"] * 1e-3 * fill_m2_walls + 2 * CEIL_FILL_M2 * 0.040 + fill_air_m3)
    cass_m2 = 2 * (P04["side_cass_l"] * (P04["side_cass_lo_h"] + P04["side_cass_up_h"])
                   + P04["back_cass_w"] * (P04["back_cass_lo_h"] + P04["back_cass_up_h"])) * 1e-6 + 2 * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6
    clips = 8 * 4 + 2 * 6
    clip_kg = p("leaf_clip_kgm2") * cass_m2 - (clips * CLIP_KG + 4 * CATCH_KG)
    band_m = sum(pt.dims[0] * pt.qty for pt in base_parts() if pt.pid.startswith("B-BAND")) * 1e-3
    band_kg = (al_rhs(100, 40, p("t_al_base")) - al_rhs(100, 40, BAND_T_LIGHT)) * band_m
    lam = 1 - LAM33_T / LAM44_T
    return [
        (FIXED_GLASS * lam, "Fixed glass in 3+3 laminate of toughened, heat-soaked panes (6.76 mm) instead of 4+4; same grey "
         "interlayer, same frameless edge in its U-profiles, so it looks the same. The glass carries about 4% of the speech "
         "that gets out, so the pod loses well under 0.1 dB (mass law on the fixed pane's third of the glass)",
         "medium: the glass supplier checks a 1.06 m2 pentagon up to 2 m tall in 3+3 for strength and deflection; the door "
         "stays 4+4 (D-46)", "FRONT"),
        (clip_kg, f"Clip-only cassette fixing, no rails: {clips} clips and 4 catch lanyards at about 40 g and 100 g "
         f"(assumption) instead of this study's 0.6 kg/m2 clip-and-rail allowance over {cass_m2:.1f} m2 of cassettes. Hidden "
         "behind the felt", "medium: the clip still has to be named with a rated load and a captive lock (H03, ISS-076) and "
         "mustn't bridge the floating lining (wall sample T01, T07)", "WALL and CEILING (linings), with the Hardware Engineer"),
        (fill_kg, f"Cavity fill at {FILL_LIGHT:.0f} kg/m3 instead of {p('fill_pet_kgm3'):.0f} in the wall panels, on the "
         "ceiling cassettes and in the air column and soffit. Hidden", "medium: the lighter grade has no published "
         "absorption data, so the wall sample's T02 decides (D-54)", "WALL and CEILING, with the Hardware Engineer (T02)"),
        (band_kg, f"Base band 100 x 40 aluminium with a {BAND_T_LIGHT} mm wall instead of {p('t_al_base'):.1f} mm, "
         f"{band_m:.1f} m of it. The same outside size and finish", "medium: the band carries the walls, the right block and "
         "the glides; BASE checks it (this study's 2.0 mm is an assumption)", "BASE"),
        (DOOR_GLASS * lam, "Door leaf in 3+3 laminate instead of 4+4. Looks the same; the door carries about 2/3 of the "
         "glass's small share of the speech leak", "high: reopens D-46. A 2 m frameless leaf on hinges needs the 4+4's "
         "stiffness, and the hinge and lock set is rated for this glass (PR #27)", "FRONT and the PM"),
    ]


REJECTED = (
    ("0.4 mm lining tray", "saves about 12.7 kg but costs 1 dB (D-37)"),
    ("Lighter cartridge casings, 1.2 mm aluminium", "about 27.8 dB(A) at 53 l/s against the 26 target (air report section 7d)"),
    ("Intake riser in 0.8 mm steel", "saves about 1.7 kg but gives 30.03 dB(A) at the 65 l/s boost against 30 (air report model)"),
    ("Lighter ACP or felt on the walls and ceiling", "they are the sound leaves; less mass loses dB"),
)


def rollup_csv(rows):
    head = ["group", "item", "qty", "kg_each", "kg_total", "status", "source"]
    out = [",".join(head)]
    for g, item, q, kg, st, src in rows:
        cells = [g, item, str(q), f"{kg:.3f}", f"{q * kg:.2f}", st, src]
        out.append(",".join('"' + c.replace('"', '""') + '"' if ("," in c or '"' in c) else c for c in cells))
    return "\n".join(out) + "\n"


def rollup_md(rows):
    tot = pod_kg(rows)
    base = total(base_parts())
    by = {}
    for g, *_r in rows:
        by.setdefault(g, 0.0)
    for g, _i, q, kg, _s, _src in rows:
        by[g] += q * kg
    sv = savings()
    four = sum(s[0] for s in sv[:4])
    model_l1 = final_outer_kg(P04["side_w"], P04["side_h"], P04["frame_d"], FINAL)
    heavy = max(rows, key=lambda r: r[3] if "glass" not in r[1].lower() and "door unit" not in r[1].lower() else 0)
    md = []
    md.append("<!-- weight-rollup.md is generated by scripts/run_all.py (scripts/rollup.py). Edit the scripts, never this file. -->")
    md.append("# Weight roll-up on skeleton P04")
    md.append("")
    md.append(f"**The pod comes to {tot:.1f} kg against the {CAP_KG:.0f} kg cap: {tot - CAP_KG:.1f} kg over** (calculation). "
              f"The first four savings below take {four:.1f} kg off, to about {tot - four:.1f} kg, without changing the look or "
              "the sound targets.")
    md.append("")
    md.append(f"- **Basis.** This study's decided build ({base:.1f} kg on skeleton P03), recounted with tonight's numbers: the "
              "teams' CAD masses where they exist (CEILING PR #32, FRONT PRs #27 and #28, WALL's L1), D-60's air parts as sized "
              "(the air report), and this study's model at skeleton P04's sizes for the rest. Every line has its status and source "
              "below and in `out/parts-decided-P04.csv`.")
    md.append(f"- **Cross-checks.** This study's model gives L1 {model_l1:.2f} kg at the P04 size; WALL's CAD gives "
              f"{WALL_L1_MADE + WALL_L1_BOND:.2f} kg. The PM's running estimate, D-71, is {D71_KG:.1f} kg plus "
              f"{D71_LEFT_OUT:.1f} kg it leaves out (corner tubes, bond, floor foam), {D71_KG + D71_LEFT_OUT:.1f} kg; this "
              f"recount is {tot - D71_KG - D71_LEFT_OUT:+.1f} kg from that.")
    door_d = DOOR_UNIT - base_parts_kg("F-GLASS-DOOR")
    floor_d = (plate_kg(P04["floor_w"] * P04["floor_d"] * 1e-6, FLOOR_T, p("rho_ply")) + P04["floor_w"] * P04["floor_d"] * 1e-6 * 0.3) * 2 \
        - (base_parts_kg("B-FLOOR") * 2 - 12.6)
    md.append(f"  Most of the difference: the door unit's CAD is {door_d:+.1f} kg over this study's {base_parts_kg('F-GLASS-DOOR'):.1f}, "
              f"and P04's floor panels (1210 x 1455) are larger than the ones D-71's -12.6 kg was worked on ({floor_d:+.1f} kg).")
    md.append(f"- **20 kg rule (D-03).** The heaviest piece apart from the glass is {heavy[1].split(',')[0]} at {heavy[3]:.1f} kg. "
              "The door unit and the fixed glass unit are glass and exempt.")
    md.append("")
    md.append("| Assembly | kg |")
    md.append("|---|---:|")
    for g in ("WALL", "LINING", "CEILING", "BASE", "FRONT", "AIR", "ELECTRICAL"):
        if g in by:
            md.append(f"| {g} | {by[g]:.1f} |")
    md.append(f"| **Pod** | **{tot:.1f}** |")
    md.append(f"| Cap (D-37, D-54) | {CAP_KG:.0f} |")
    md.append(f"| **Over the cap** | **{tot - CAP_KG:.1f}** |")
    md.append("")
    md.append("## Every line")
    md.append("")
    md.append("| Assembly | Item | Qty | kg each | kg | Status | Source |")
    md.append("|---|---|---:|---:|---:|---|---|")
    for g, item, q, kg, st, src in rows:
        md.append(f"| {g} | {item} | {q} | {kg:.2f} | {q * kg:.2f} | {st} | {src} |")
    md.append("")
    md.append("Sources S33 to S39 are in section 10 of the report (`scripts/inputs.py`). Not in the total yet: the light shelf "
              "and the work-wall ledge (D-70), which aren't designed; the clips and catches as named parts (an allowance is "
              "carried); the next skeleton update (9 mm floor, 13 mm threshold, ISS-086).")
    md.append("")
    md.append("## The five best savings")
    md.append("")
    md.append("Each keeps the look exactly and the sound targets (19.3 dB speech reduction; fan noise 26 dB(A) at 53 l/s and "
              "30 at the boost). Ranked by kg, with the high-risk one last.")
    md.append("")
    md.append("| # | Saves kg | What changes | Risk | Owner |")
    md.append("|---:|---:|---|---|---|")
    for i, (kg, what, risk, owner) in enumerate(sv, 1):
        md.append(f"| {i} | {kg:.1f} | {what} | {risk} | {owner} |")
    md.append("")
    md.append(f"Savings 1 to 4 together: {four:.1f} kg, giving about {tot - four:.1f} kg, {CAP_KG - (tot - four):.1f} kg under "
              f"the cap. With saving 5 as well: about {tot - four - sv[4][0]:.1f} kg.")
    md.append("")
    md.append(f"The total includes the {base_parts_kg('E-VOICE-RESERVE'):.1f} kg voice-kit reserve. The kit ships later (D-11), so the "
              "PM may choose to hold it outside the shipping cap; that is a budget rule, not a saving.")
    md.append("")
    md.append("Looked at and rejected, because they lose the sound targets:")
    md.append("")
    for name, why in REJECTED:
        md.append(f"- {name}: {why}.")
    md.append("")
    return "\n".join(md)


def rollup_files():
    rows = lines()
    return {"weight-rollup.md": rollup_md(rows), "out/parts-decided-P04.csv": rollup_csv(rows)}


if __name__ == "__main__":
    rows = lines()
    print(rollup_md(rows))
