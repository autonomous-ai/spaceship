"""Weight roll-up on skeleton P04 (ISS-081, F-010): the decided build recounted with tonight's rulings and CAD masses.

The base is this study's decided build (option B1 with the final stack, skeleton P03). Each line is replaced where a
newer number exists: the teams' CAD masses (CEILING PR #32, FRONT PRs #27 and #28, the WALL group's L1), the air parts as
sized for D-60 (the air report, section 7f), and this study's own model re-run at skeleton P04's sizes for the parts with
no CAD yet. On top: the PM's adopted savings (ruling after PR #38) and allowances for parts not designed yet. Every line
carries its status and its source (SOURCES in inputs.py). run_all.py writes weight-rollup.md and out/parts-decided-P04.csv
from here, and its --check proves they reproduce. The mechanical check sums the CSV for F-010 and leaves out the voice kit's
line, which is outside the cap (PR #40).
"""
import os
import sys

from inputs import override, p
from shapes import al_rhs, plate_kg
from v2_model import FINAL, final_leaf_kg, final_outer_kg, parts_for, total

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "acoustics-air"))
import calc as AA  # noqa: E402  (the air report's own model: D-60's air parts)

CAP_KG = 420.0          # confirmed, D-37 and D-54
TARGET_KG = 410.0       # confirmed: D-81's target for the pod as shipped (S40)
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
SKEL_STACK = 84.0             # mm: outer panel 46 + the floating lining, wall face to lining face (S33)
# D-81, the PM's weight ruling on PR #38 (S40): adopted now, two of them provisional on a test or a check
FILL_LIGHT = 24.0             # kg/m3: the default now, provisional on T02 (D-54, D-81); the grade Pyrotek lists and the
                              # sample tests
CLIP_KG, CATCH_KG = 0.04, 0.10  # assumption: clip-only fixing, no rails (adopted), about 40 g a clip and 100 g a catch
                                # lanyard until H03 and H04 name them
BAND_T_LIGHT = 1.5            # mm: the base band's wall (adopted, provisional on BASE's check; this study's 2.0 is S07's)
# Budgets and allowances for parts that aren't designed yet (assumption)
SHELF_KGM_ALLOW, SHELF_KGM = 0.6, 0.4  # kg/m: the light shelf with its LED strip (D-70): the first allowance, and D-85's
                                       # budget as a 1.2 mm aluminium angle
SHELF_BRACKETS_KG = 0.4       # kg: its brackets at about 400 mm
LEDGE_KG_ALLOW, LEDGE_KG = 2.3, 1.4    # kg: the work wall's 1000 mm ledge (D-70): 12 mm ply at 650 kg/m3 with 2 brackets,
                                       # and D-85's budget in 1.5 mm folded aluminium (1000 x 240 developed) with 2 brackets
# D-85, the PM's pick toward the 410 kg target (S41)
T_STUD_LIGHT = 1.0            # mm: inner studs of the 20 x 40 frames; the perimeters keep D-34's 1.2 for the rivnuts
BACK_STUDS = 2                # inner studs in each back outer panel: 393 mm centres, inside D-16's 400 (this study counted 3)
CEIL_STUDS = 2                # inner studs in each ceiling outer panel, along its 1495 mm (assumption, from PR #32's frame)
KICK_KG, KICK_KG_HOLLOW = 2.094, 1.0  # kg: the kick strip (S36) and a hollow profile, same outside, 2 mm walls (assumption)
FLOOR_RHO_LIGHT = 450.0       # kg/m3: poplar-core 9 mm plywood (assumption) against this study's 600 (S13); provisional on
                              # BASE's castor and 1000 N edge tests (D-76, D-85)
# Parked by D-85, and the rejected glass options
LAM33_T, LAM44_T = 6.76, 8.76  # mm: 3+3 and 4+4 laminate (glass 3 + 0.76 PVB + 3, as the 4+4 is 4 + 0.76 + 4)
FELT_KGM2_LIGHT = 1.4         # kg/m2: a lighter 9 mm PET felt, against Polyx Board 9's 1.8 (S11)
FILL_LIGHTER = 18.0           # kg/m3: Pyrotek's lightest listed grade (hardware selection, fill row: 18, 24, 32, 48, 60)
DECOR_TUBE_CUT = 0.25         # share of the decor blocks' frame tube a FRONT design could leave out (assumption)

def base_parts():
    """This study's decided build on skeleton P03 (option B1 with the final stack)."""
    return parts_for("plan", FINAL)


def base_parts_kg(pid):
    """kg each of one part in this study's decided build (P03)."""
    return [pt for pt in base_parts() if pt.pid == pid][0].kg


def stile_delta_kg():
    """A 40 x 40 back stile over the 20 x 40 member it replaces, one side panel high (calculation)."""
    return (al_rhs(40, 40, p("t_al_final")) - al_rhs(20, 40, p("t_al_final"))) * P04["side_h"] * 1e-3


def cassette_faces_m2():
    """Faces of the 8 wall cassettes (P04) and the 2 ceiling cassettes (PR #32's tray outline), m2."""
    walls = 2 * (P04["side_cass_l"] * (P04["side_cass_lo_h"] + P04["side_cass_up_h"])
                 + P04["back_cass_w"] * (P04["back_cass_lo_h"] + P04["back_cass_up_h"])) * 1e-6
    return walls, 2 * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6


def named_clips_kg():
    """Clip-only fixing (adopted): 4 clips on each wall cassette, 6 on each ceiling cassette, 2 catches each (D-47)."""
    return (8 * 4 + 2 * 6) * CLIP_KG + 2 * 2 * CATCH_KG


def air_fill_delta_kg(fill=FILL_LIGHT):
    """The air column's and soffit's cavity fill (air report D60: 27 mm on each cartridge's two faces toward the pod)
    from 32 kg/m3 to `fill`. The cartridges' 50 mm layers stay at 32, the density their published absorption is for."""
    w, d, l = (x / 1000 for x in AA.D60["cart"])
    return (AA.FILL_KG_M3 - fill) * AA.D60["fill"] / 1000 * (w + d) * l


def shelf_m():
    """The light shelf along the tops of the side and back walls (D-70): the inside width, and each side wall's inside run
    from the back lining to the soffit (air report D60), m."""
    (x0, x1), (y0, y1), _z = AA.D60["soffit"]
    side = P04["wall_depth"] - SKEL_STACK - (y1 - y0)
    return (2 * side + (x1 - x0)) / 1000


ADOPTED = dict(fill=FILL_LIGHT, clip_only=True, band_t=BAND_T_LIGHT, kit_outside=True,     # D-81
               budgets=True, back2=True, studs10=True, kick=True, floor=True)               # D-85
OFF = dict(fill=p("fill_pet_kgm3"), clip_only=False, band_t=p("t_al_base"), kit_outside=False,
           budgets=False, back2=False, studs10=False, kick=False, floor=False)


def lines(**adopt):
    """[(group, item, qty, kg_each, status, source)] for the pod on skeleton P04: tonight's numbers with the PM's adopted
    savings (D-81, D-85). Group LATER is outside the 420 kg cap (the voice kit, D-11). A keyword switches an adopted
    saving back off (its value in OFF); applied() prices each saving that way."""
    a = dict(ADOPTED, **adopt)
    fill, rails, band_t = a["fill"], not a["clip_only"], a["band_t"]
    kgm12 = al_rhs(20, P04["frame_d"], p("t_al_final"))
    kgm_s = al_rhs(20, P04["frame_d"], T_STUD_LIGHT) if a["studs10"] else kgm12
    stud_d = kgm12 - kgm_s                                   # kg/m less on each inner stud (D-85)
    n_back = BACK_STUDS if a["back2"] else 3
    studs_txt = f"; inner studs at {T_STUD_LIGHT:.1f} mm (D-85)" if a["studs10"] else ""
    lighter = fill != p("fill_pet_kgm3")
    prov = "; fill provisional" if lighter else ""
    base = {pt.pid: pt for pt in base_parts()}
    L = []
    side_a = P04["side_w"] * P04["side_h"] * 1e-6
    fill_d = (p("fill_pet_kgm3") - fill) * P04["frame_d"] * 1e-3      # kg/m2 less with the lighter fill
    with override(fill_pet_kgm3=fill):
        up = final_outer_kg(P04["side_w"], P04["side_up_h"], P04["frame_d"], FINAL)
        back = final_outer_kg(P04["back_w"], P04["back_h"], P04["frame_d"], FINAL)
    L.append(("WALL", "L1 and R1, lower side outer panels (R1 is L1's mirror)", 2,
              WALL_L1_MADE + WALL_L1_BOND - fill_d * side_a - 3 * P04["side_h"] * 1e-3 * stud_d,
              "calculation (CAD)" + prov, "S34: 11.35 kg of made parts + 0.49 kg of bond"
              + (f", less the fill from 32 to {fill:g} kg/m3" if lighter else "") + studs_txt))
    L.append(("WALL", "L2 and R2, upper side outer panels, the same size and build", 2,
              up - 3 * P04["side_up_h"] * 1e-3 * stud_d, "calculation" + prov,
              f"this study's model at the P04 size (S33), fill {fill:g} kg/m3" + studs_txt))
    L.append(("WALL", f"B1 to B4, back outer panels, {n_back} inner studs", 4,
              back - 3 * P04["back_h"] * 1e-3 * kgm12 + n_back * P04["back_h"] * 1e-3 * kgm_s, "calculation" + prov,
              f"this study's model at the P04 size (S33), fill {fill:g} kg/m3"
              + ("; 2 inner studs at 393 mm centres, inside D-16 (D-85)" if a["back2"] else "") + studs_txt))
    L.append(("WALL", "40 x 40 corner edge tubes beyond L1 and R1's back stiles", 1,
              CORNER_TUBES_KG - 2 * stile_delta_kg(), "calculation", "D-63's 1.3 kg less L1 and R1's two stiles (S34, S39)"))
    L.append(("WALL", "Bond over this study's 0.25 kg/m2, beyond L1 and R1", 1,
              BOND_OVER_KG - 2 * (WALL_L1_BOND - p("bond_kgm2") * side_a), "calculation",
              "D-71's 0.5 kg (PR #23) less L1 and R1's share (S34, S39)"))
    for item, w, h in (("side, lower", P04["side_cass_l"], P04["side_cass_lo_h"]),
                       ("side, upper", P04["side_cass_l"], P04["side_cass_up_h"]),
                       ("back, lower", P04["back_cass_w"], P04["back_cass_lo_h"]),
                       ("back, upper", P04["back_cass_w"], P04["back_cass_up_h"])):
        L.append(("LINING", f"Wall cassette, {item}, with 12 mm lips" + ("" if rails else ", no clip rails"), 2,
                  final_leaf_kg(w, h) - (0.0 if rails else p("leaf_clip_kgm2") * w * h * 1e-6) + LIP_KG,
                  "calculation; lips confirmed", "this study's model at the P04 size (S33)"
                  + ("" if rails else " without its 0.6 kg/m2 clip-and-rail allowance (clip-only, D-81)")
                  + ", + 0.43 kg of lips (D-69)"))
    ceil_bond = p("bond_kgm2") * P04["ceil_w"] * P04["wall_depth"] * 1e-6
    L.append(("CEILING", "Ceiling outer panels C1 and C2, with their bond line", 2,
              CEIL_PANEL + ceil_bond - CEIL_STUDS * P04["wall_depth"] * 1e-3 * stud_d, "calculation (CAD); bond assumption",
              "S35 + this study's 0.25 kg/m2 bond on the P04 46 mm panel"
              + (f"; its {CEIL_STUDS} inner studs (assumption) at {T_STUD_LIGHT:.1f} mm (D-85)" if a["studs10"] else "")))
    rails_kg = p("leaf_clip_kgm2") * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6 if rails else 0.0
    L.append(("LINING", "Ceiling cassettes, one part for both halves", 2, CEIL_CASS - CEIL_FILL_M2 * fill_d + rails_kg,
              "calculation (CAD)" + prov, "S35" + (f", its fill strips from 32 to {fill:g} kg/m3" if lighter else "")
              + (", + this study's 0.6 kg/m2 clip-and-rail allowance" if rails else "")))
    if not rails:
        L.append(("LINING", "Named clips and catches: 44 clips and 4 catch lanyards", 1, named_clips_kg(), "assumption",
                  "allowance: about 40 g a clip and 100 g a lanyard until H03 and H04 name them (clip-only, D-81)"))
    kgm_band = al_rhs(100, 40, band_t)
    thin = band_t != p("t_al_base")
    for pid in ("B-BAND-BACK", "B-BAND-SIDE", "B-BAND-FRONT-L", "B-BAND-FRONT-R"):
        pt = base[pid]
        L.append(("BASE", f"{pt.name.split(' - ', 1)[1].capitalize()}, {band_t:g} mm wall", pt.qty, pt.dims[0] * 1e-3 * kgm_band,
                  "calculation" + ("; provisional" if thin else ""),
                  "this study's model" + (f", {band_t:g} mm wall (D-81, if BASE's check passes)" if thin else "")
                  + "; P03 lengths, P04's faceted front band is about 0.2 m shorter"))
    for pid, note in (("B-KEY", "this study's model"), ("B-GLIDE", "this study's model"),
                      ("B-THRESH", "this study's model (D-72's 13 mm profile isn't modelled yet)")):
        pt = base[pid]
        L.append(("BASE", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status, note))
    fa = P04["floor_w"] * P04["floor_d"] * 1e-6
    if a["floor"]:
        L.append(("BASE", "Floor panels, 9 mm poplar-core plywood with a 0.3 kg/m2 finish", 2,
                  plate_kg(fa, FLOOR_T, FLOOR_RHO_LIGHT) + fa * 0.3, "confirmed (9 mm); calculation; provisional",
                  "D-72 (S39) at the P04 size (S33); poplar-core plywood about 450 kg/m3 (assumption), if BASE's castor and "
                  "1000 N edge tests pass (D-76, D-85)"))
    else:
        L.append(("BASE", "Floor panels, 9 mm plywood with a 0.3 kg/m2 finish", 2, plate_kg(fa, FLOOR_T, p("rho_ply")) + fa * 0.3,
                  "confirmed (9 mm); calculation", "D-72 (S39) at the P04 size (S33); plywood 600 kg/m3 (S13)"))
    L.append(("BASE", "Floor mat, 3 mm firm closed-cell foam", 1, FOAM_KG, "calculation", "D-76 (S39), BASE Engineer"))
    for pid in ("F-DL", "F-DR", "F-DT"):
        pt = base[pid]
        L.append(("FRONT", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status,
                  "this study's model from v1's STEP shapes (S02)"))
    if a["kick"]:
        L.append(("FRONT", "Door unit 360001: 4+4 leaf, hollow kick strip, drop seal, hinges, lock, pull", 1,
                  DOOR_UNIT - (KICK_KG - KICK_KG_HOLLOW), "calculation (CAD); kick strip assumption",
                  f"S36, with the kick strip as a hollow profile, about {KICK_KG_HOLLOW:.1f} kg against {KICK_KG} (D-85)"))
    else:
        L.append(("FRONT", "Door unit 360001: 4+4 leaf, kick strip, drop seal, hinges, lock, pull", 1, DOOR_UNIT,
                  "calculation (CAD)", "S36"))
    L.append(("FRONT", "Fixed glass unit 360002: 4+4 pane, U-profiles and seals", 1, FIXED_UNIT, "calculation (CAD)", "S37"))
    for name, size, kg, basis in AA.d60_parts():
        filled = lighter and (name.startswith("Air column") or name.startswith("Soffit"))
        loose = name.startswith("Intake riser") or name.startswith("Supply fan box")
        L.append(("AIR", name + ("; ships loose, fitted on site" if loose else ""), 1,
                  kg - (air_fill_delta_kg(fill) if filled else 0.0), "calculation" + ("; fill provisional" if filled else ""),
                  "S38: " + basis + (f"; fill {fill:g} kg/m3" if filled else "")
                  + ("; goes into the right block through its removable inner face (D-59), so the block ships at 20 kg "
                     "or less (D-03)" if loose else "")))
    L.append(("AIR", "Four 12 V fans", 1, AA.fans_kg(), "assumption", "S38: 0.3 kg each until the sample is weighed"))
    pt = base["K-SEALS"]
    L.append(("BASE", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status, "this study's model"))
    pt = base["E-KIT"]
    L.append(("ELECTRICAL", "Switches and harness (the two ceiling lights go, D-70)", 1, pt.kg - 2 * p("light_kg"), pt.status,
              "this study's model less 2 x 0.5 kg ceiling lights"))
    shelf_kgm = SHELF_KGM if a["budgets"] else SHELF_KGM_ALLOW
    L.append(("INTERIOR", "Light shelf along the side and back wall tops, with its LED strip", 1,
              shelf_kgm * shelf_m() + SHELF_BRACKETS_KG, "assumption",
              ("budget (D-85)" if a["budgets"] else "allowance") + f" until it's designed: {shelf_m():.2f} m (the back wall "
              f"and the side walls back of the soffit) at {shelf_kgm:g} kg/m plus 0.4 kg of brackets (D-70)"))
    L.append(("INTERIOR", "Work-wall ledge, 1000 mm", 1, LEDGE_KG if a["budgets"] else LEDGE_KG_ALLOW, "assumption",
              "budget (D-85) until it's designed: 1.5 mm folded aluminium, 1000 x 240 developed, plus 2 brackets (D-70)"
              if a["budgets"] else "allowance until it's designed: 1000 x 200 x 12 mm ply at 650 kg/m3 plus 2 brackets (D-70)"))
    pt = base["K-FIX"]
    L.append(("WALL", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, pt.kg, pt.status, "this study's model"))
    pt = base["E-VOICE-RESERVE"]
    if a["kit_outside"]:
        L.append(("LATER", "Voice cockpit kit reserve, outside the 420 kg cap", 1, pt.kg, pt.status,
                  "the kit ships later as an add-on (D-11); the cap is for the pod as shipped (D-81)"))
    else:
        L.append(("ELECTRICAL", "Voice cockpit kit reserve", 1, pt.kg, pt.status, "this study's model (D-11)"))
    return L


def pod_kg(rows=None):
    """The pod as shipped: every line but the voice kit (group LATER)."""
    return sum(q * kg for g, _, q, kg, _, _ in (rows or lines()) if g != "LATER")


def applied():
    """The adopted savings, D-81 then D-85 (S40, S41): (kg, what, status, owner). Each is priced by switching it on in
    lines(), in this order, from the build with none of them, so the table adds up to the part list exactly."""
    walls_m2, ceil_m2 = cassette_faces_m2()
    band_m = sum(pt.dims[0] * pt.qty for pt in base_parts() if pt.pid.startswith("B-BAND")) * 1e-3
    items = [
        ("clip_only", f"Clip-only cassette fixing, no rails: 44 named clips and 4 catch lanyards ({named_clips_kg():.1f} kg "
         f"allowance) replace this study's 0.6 kg/m2 clip-and-rail allowance over {walls_m2 + ceil_m2:.1f} m2 of cassettes",
         "adopted (D-81); the clip gets named with a rated load and a captive lock (H03), T01 and T07 confirm",
         "WALL and CEILING"),
        ("fill", f"Cavity fill at {FILL_LIGHT:g} kg/m3 instead of {p('fill_pet_kgm3'):g}: the wall panels, the ceiling "
         "cassettes, the air column and the soffit. The cartridges' 50 mm layers stay at 32, the density their published "
         "absorption is for", "provisional (D-81): back to 32 kg/m3 if T02 fails (D-54)", "WALL, CEILING, AIR"),
        ("band_t", f"Base band with a {BAND_T_LIGHT:g} mm wall instead of {p('t_al_base'):.1f} mm, {band_m:.1f} m of it; the "
         "same outside size and finish", "provisional on BASE's check (D-81)", "BASE"),
        ("kit_outside", "The voice kit's reserve moves outside the cap: the kit ships later as an add-on (D-11)",
         "adopted (D-81); the cap is for the pod as shipped", "PM"),
        ("budgets", f"Weight budgets for the parts not designed yet: the light shelf at {SHELF_KGM:g} kg/m, the ledge in "
         "1.5 mm folded aluminium", "adopted (D-85): the designs keep to them", "INTERIOR, WALL"),
        ("back2", f"Back outer panels with {BACK_STUDS} inner studs, not 3: 393 mm centres, inside D-16's 400 mm (this study "
         "counted from the outer width)", "adopted (D-85)", "WALL"),
        ("studs10", f"Inner studs at {T_STUD_LIGHT:.1f} mm wall; the perimeter members keep 1.2 mm for the rivnuts (D-34)",
         "adopted (D-85)", "WALL, CEILING"),
        ("kick", "Door kick strip as a hollow profile with 2 mm walls; the same outside and finish", "adopted (D-85)",
         "FRONT"),
        ("floor", f"Floor panels in poplar-core 9 mm plywood, about {FLOOR_RHO_LIGHT:.0f} kg/m3 against "
         f"{p('rho_ply'):.0f}; the same finish on top", "provisional (D-85): BASE's castor and 1000 N edge tests (D-76) "
         "decide", "BASE"),
    ]
    state = dict(OFF)
    prev = pod_kg(lines(**state))
    out = []
    for key, what, status, owner in items:
        state[key] = ADOPTED[key]
        now = pod_kg(lines(**state))
        out.append((prev - now, what, status, owner))
        prev = now
    return out


def col_soffit_faces_m2():
    """The air column's two felt-covered faces and the soffit's underside and front face (air report D60), m2."""
    (cx0, cx1), (cy0, cy1), (cz0, cz1) = AA.D60["col"]
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = AA.D60["soffit"]
    return ((cx1 - cx0 + cy1 - cy0) * (cz1 - cz0) + (sy1 - sy0 + sz1 - sz0) * (sx1 - sx0)) * 1e-6


def decor_tube_kg():
    """The three decor blocks' frame tube in this study's model (v1's steel layout in the final aluminium section)."""
    from v2_model import decor_kg, decor_skin_area
    return sum(decor_kg(b, FINAL) - decor_skin_area(b) * p("acp3_kgm2") - 4 * 0.05 for b in ("DL", "DR", "DT"))


def perimeter_saving_kg():
    """The 20 x 40 perimeter members of the wall and ceiling outer panels at T_STUD_LIGHT instead of 1.2 mm (rejected)."""
    P = P04
    perim_m = 4 * 2 * (P["side_w"] + P["side_h"]) + 4 * 2 * (P["back_w"] + P["back_h"]) + 2 * 2 * (P["ceil_w"] + P["wall_depth"])
    return (al_rhs(20, 40, p("t_al_final")) - al_rhs(20, 40, T_STUD_LIGHT)) * perim_m * 1e-3


def parked():
    """The candidates D-85 parks: (kg, what, what settles it, owner)."""
    felt_m2 = sum(cassette_faces_m2()) + col_soffit_faces_m2()
    return [
        (DECOR_TUBE_CUT * decor_tube_kg(), f"Decor block frames lighter than v1's steel layout ({decor_tube_kg():.1f} kg of "
         "tube in this study's model; a quarter of it, assumption)", "FRONT's CAD; the right block carries the riser and the "
         "fan box", "FRONT"),
        (pod_kg(lines()) - pod_kg(lines(fill=FILL_LIGHTER)), f"Cavity fill at {FILL_LIGHTER:g} kg/m3 instead of "
         f"{FILL_LIGHT:g}", "the wall sample: no published absorption, and it may slump in the upright panels",
         "WALL, CEILING"),
        ((p("pet9_kgm2") - FELT_KGM2_LIGHT) * felt_m2, f"A lighter 9 mm felt, {FELT_KGM2_LIGHT:g} kg/m2 against "
         f"{p('pet9_kgm2'):g}, the same Dark Gray, on {felt_m2:.1f} m2", "the wall sample: the inside absorption uses Polyx "
         "Board 9's 1.8 kg/m2 data, and the face is the look", "Hardware, LINING"),
    ]


REJECTED = (
    ("Fixed glass in 3+3 laminate", f"saves about {FIXED_GLASS * (1 - LAM33_T / LAM44_T):.1f} kg, but a 3+3 pane bends "
     "58 mm at its free edge under a person leaning on it; it stays 4+4 (D-82)"),
    ("The frame perimeters at 1.0 mm", f"saves about {perimeter_saving_kg():.1f} kg, but the 1.2 mm perimeters carry every "
     "rivnut joint (D-85)"),
    ("Door leaf in 3+3 laminate", f"saves about {DOOR_GLASS * (1 - LAM33_T / LAM44_T):.1f} kg; rejected in D-81, D-46 "
     "stands"),
    ("Lighter faces on the air column and soffit", "2 mm ACP gives 26.1 dB(A) at 53 l/s and 30.5 at the boost, against "
     "26 and 30 (air report model)"),
    ("Side outer panels at a 500 mm stud pitch", "saves about 1.7 kg but reopens D-16: the visible ACP may oil-can"),
    ("0.4 mm lining tray", "saves about 12.7 kg but costs 1 dB (D-37)"),
    ("Lighter cartridge casings, 1.2 mm aluminium", "about 27.8 dB(A) at 53 l/s against the 26 target (air report section 7d)"),
    ("Intake riser in 0.8 mm steel", "saves about 1.7 kg but gives 30.03 dB(A) at the 65 l/s boost against 30 (air report model)"),
    ("Lighter ACP on the walls and ceiling", "it is the outer sound leaf; less mass loses dB"),
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
    later = sum(q * kg for g, _, q, kg, _, _ in rows if g == "LATER")
    by = {}
    for g, _i, q, kg, _s, _src in rows:
        by[g] = by.get(g, 0.0) + q * kg
    ap, op = applied(), parked()
    model_l1 = final_outer_kg(P04["side_w"], P04["side_h"], P04["frame_d"], FINAL)
    shipped = [r for r in rows if r[0] != "LATER" and "glass" not in r[1].lower() and "door unit" not in r[1].lower()]
    heavy = max(shipped, key=lambda r: r[3])
    loose = sum(r[3] for r in rows if r[0] == "AIR" and (r[1].startswith("Intake riser") or r[1].startswith("Supply fan box")))
    gap = lambda x: f"{abs(x):.1f} kg {'over' if x > 0 else 'under'}"
    md = []
    md.append("<!-- weight-rollup.md is generated by scripts/run_all.py (scripts/rollup.py). Edit the scripts, never this file. -->")
    md.append("# Weight roll-up on skeleton P04")
    md.append("")
    md.append(f"**As shipped, the pod comes to {tot:.1f} kg: {gap(tot - CAP_KG)} the {CAP_KG:.0f} kg cap and {gap(tot - TARGET_KG)} "
              f"the {TARGET_KG:.0f} kg target** (calculation). The voice kit's {later:.1f} kg reserve rides outside the cap, "
              f"{tot + later:.1f} kg with it. This is the live count: it is re-run whenever a part's CAD merges or the skeleton "
              "moves (see the end).")
    md.append("")
    md.append("- **Basis.** This study's decided build on skeleton P03, recounted on P04 with tonight's numbers: the teams' CAD "
              "masses where they exist (CEILING PR #32, FRONT PRs #27 and #28, WALL's L1), D-60's air parts as sized (the air "
              "report), the PM's adopted savings (D-81, D-85), budgets and allowances for parts not designed yet, and this "
              "study's model at P04's sizes "
              "for the rest. Every line has its status and source below and in `out/parts-decided-P04.csv`.")
    md.append(f"- **Cross-check.** This study's model gives L1 {model_l1:.2f} kg at the P04 size with 32 kg/m3 fill; WALL's CAD "
              f"gives {WALL_L1_MADE + WALL_L1_BOND:.2f} kg.")
    nm = heavy[1].split(",")[0]
    nm = nm.split(" - ")[1] + " decor block" if nm.startswith("Decor block - ") else nm.lower()
    dr = base_parts_kg("F-DR")
    md.append(f"- **20 kg rule (D-03).** The intake riser and the supply fan box ({loose:.1f} kg together) ship loose and go "
              f"into the right decor block on site through its removable inner face (D-59), so the block ships at {dr:.1f} kg; "
              f"fitted in the factory it would be about {dr + loose:.0f} kg, over the rule. The heaviest piece apart from the "
              f"glass is the {nm} at {heavy[3]:.1f} kg; the door unit and the fixed glass unit are glass and exempt.")
    allow = {r[1].split(",")[0].split(" along")[0]: r[2] * r[3] for r in rows if r[4] == "assumption"
             and ("Light shelf" in r[1] or "ledge" in r[1] or "Named clips" in r[1])}
    md.append(f"- **Budgets and allowances (assumption)** for parts not designed yet: the light shelf "
              f"{allow['Light shelf']:.1f} kg and the work-wall ledge {allow['Work-wall ledge']:.1f} kg (D-70; budgets from "
              f"D-85), and the named clips "
              f"{allow['Named clips and catches: 44 clips and 4 catch lanyards']:.1f} kg; the two ceiling lights go (D-70), "
              f"{2 * p('light_kg'):.1f} kg less.")
    md.append("")
    md.append("| Assembly | kg |")
    md.append("|---|---:|")
    for g in ("WALL", "LINING", "CEILING", "BASE", "FRONT", "AIR", "ELECTRICAL", "INTERIOR"):
        if g in by:
            md.append(f"| {g} | {by[g]:.1f} |")
    md.append(f"| **Pod as shipped** | **{tot:.1f}** |")
    md.append(f"| Cap (D-37, D-54) | {CAP_KG:.0f} ({gap(tot - CAP_KG)}) |")
    md.append(f"| Target (PM) | {TARGET_KG:.0f} ({gap(tot - TARGET_KG)}) |")
    md.append(f"| Voice cockpit kit reserve, later (D-11) | {later:.1f}, outside the cap |")
    md.append("")
    md.append("## Every line")
    md.append("")
    md.append("| Assembly | Item | Qty | kg each | kg | Status | Source |")
    md.append("|---|---|---:|---:|---:|---|---|")
    for g, item, q, kg, st, src in rows:
        md.append(f"| {g} | {item} | {q} | {kg:.2f} | {q * kg:.2f} | {st} | {src} |")
    md.append("")
    md.append("Sources S33 to S39 are in section 10 of the report (`scripts/inputs.py`).")
    md.append("")
    md.append("## Savings applied (D-81, D-85)")
    md.append("")
    md.append("| Saves kg | What changes | Status | Owner |")
    md.append("|---:|---|---|---|")
    for kg, what, st, owner in ap:
        md.append(f"| {kg:.1f} | {what} | {st} | {owner} |")
    md.append(f"| **{sum(a[0] for a in ap):.1f}** | **in all** | | |")
    md.append("")
    md.append("## Parked (D-85)")
    md.append("")
    md.append(f"{gap(tot - TARGET_KG).capitalize()} the {TARGET_KG:.0f} kg target, which stays (D-85). The wall sample "
              "settles the fill and the felt; FRONT's CAD settles the decor frames. Each keeps the look and the sound targets.")
    md.append("")
    md.append("| Saves kg | What changes | What settles it | Owner |")
    md.append("|---:|---|---|---|")
    for kg, what, risk, owner in op:
        md.append(f"| {kg:.1f} | {what} | {risk} | {owner} |")
    md.append("")
    md.append("Looked at and rejected:")
    md.append("")
    for name, why in REJECTED:
        md.append(f"- {name}: {why}.")
    md.append("")
    md.append("## When this is re-run")
    md.append("")
    md.append("- **The next skeleton update** (ISS-086): the 9 mm floor and 13 mm threshold (D-72), and the back and ceiling "
              "frames at 1198.99 mm at the closing seams.")
    md.append("- **Each part PR that merges:** its CAD masses replace this study's model masses line by line (today the walls "
              "other than L1, the base, the decor blocks and the kits are still model masses). The fixings kit is this study's 78 "
              "bolts and 38 cam connectors; the joints register (PR #23) has 82 bolts, 102 rivnuts and no cams, so the kit "
              "is recounted once the register gives masses.")
    md.append(f"- **BASE's support behind the intake mesh:** if it leaves less than {AA.D60_FREE['intake']:.3f} m2 free, the air "
              "report re-runs the fan noise (25.3 / 29.7 dB(A) now).")
    md.append("- **D-83:** a 35 N magnetic catch in DT and a magnetic seal pair on the glass edges replace the door lock "
              "(0.84 kg in FRONT's door unit); the door line follows FRONT's CAD.")
    md.append("- **The tests:** T02 (fill), T07 (clips), T10 (weights) and BASE's castor and 1000 N edge tests (the floor, "
              "D-85) replace the provisional and assumed lines.")
    md.append("")
    return "\n".join(md)


def rollup_files():
    rows = lines()
    return {"weight-rollup.md": rollup_md(rows), "out/parts-decided-P04.csv": rollup_csv(rows)}


if __name__ == "__main__":
    rows = lines()
    print(rollup_md(rows))
