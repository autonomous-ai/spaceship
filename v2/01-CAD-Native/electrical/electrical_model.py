"""ELECTRICAL (710000) P01: one source for the route model, the parts list,
the harness list, the load table and the wiring diagram.

No Fusion import here: `electrical_build.py` builds the Fusion design from
these tables, `../../05-Engineering/electrical/electrical_docs.py` writes the
CSV files, the calculations and the wiring diagram, and
`test_electrical_offline.py` checks them without Fusion.

Coordinates are the pod system (conventions section 4): origin on the room
floor at the pod centre, +X right (seen from outside, facing the door), +Y
toward the back wall, +Z up. All lengths in mm.

Every number carries a status (conventions section 9): confirmed, source,
calculation, assumption, unverified; DECIDED / PROPOSED for choices.
"""

import math
import re

REV = "P01"
DOC_NAME = "710000_%s_ELECTRICAL_CAD" % REV
SKELETON_DOC = "100000_P04_POD-SKELETON_CAD"

# ------------------------------------------------------------------ parameters
# Skeleton P04 parameters used here. In Fusion they arrive by Derive as
# <name>_Ref (every skeleton parameter is a favourite) and this design adds a
# user parameter of the same plain name equal to it, so every expression below
# reads the same in Fusion and offline. Offline values: the skeleton's CSV.
SKELETON_PARAMS = [
    "pod_w", "pod_d", "pod_h", "outer_t", "cav_gap", "cass_t", "stack_t", "seam_gap",
    "lin_gap", "wall_depth", "side_h", "back_ph", "back_oh", "half_pw", "panel_z0",
    "dt_zb", "inner_w",
]

PM = "PM ruling 2026-10-31 in the ELECTRICAL group"

# name, expression, unit, status, source
PARAMS = [
    # ---- the lining cassette (the cable path, D-26, D-41)
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: the cassette tray is 0.5 mm galvanised steel"),
    ("felt_t", "9 mm", "mm", "confirmed", "D-17, REQ-BLD-01: 9 mm PET felt on the cassette face"),
    ("gap_in", "cass_t - felt_t - 2 * tray_t", "mm", "calculation",
     "the cassette's air gap between the felt (on its 0.5 mm lips) and the tray base: 34 - 9 - 1 = 24 (as CEILING's gap_h)"),
    ("lip_w", "12 mm", "mm", "confirmed", "D-69: 12 mm lips hold the felt at the cassette edges; no cable hole goes through a lip except where named"),
    ("y_bf", "pod_d / 2 - stack_t", "mm", "calculation", "back wall lining: felt face plane Y 766"),
    ("y_bg", "y_bf + tray_t + felt_t + gap_in / 2", "mm", "calculation", "back wall lining: middle of the cable gap, Y 787.5"),
    ("x_rf", "pod_w / 2 - stack_t", "mm", "calculation", "right wall lining: felt face plane X 1166"),
    ("x_rg", "x_rf + tray_t + felt_t + gap_in / 2", "mm", "calculation", "right wall lining: middle of the cable gap, X 1187.5"),
    ("z_cf", "pod_h - stack_t", "mm", "calculation", "ceiling lining: felt face plane Z 2316"),
    ("z_cg", "z_cf + tray_t + felt_t + gap_in / 2", "mm", "calculation", "ceiling lining: middle of the cable gap, Z 2337.5 (CEILING's cable holes sit here)"),
    ("z_b2t", "panel_z0 + back_ph", "mm", "calculation", "top of the lower back lining B2-CASS, Z 1230.87"),
    ("z_b4b", "panel_z0 + back_ph + seam_gap", "mm", "calculation", "bottom of the upper back lining B4-CASS, Z 1233.13"),
    ("z_r1t", "panel_z0 + side_h", "mm", "calculation", "top of the lower side lining R1-CASS, Z 1255"),
    ("rt_h", "8 mm", "mm", "assumption", "half the depth of a cable bundle in the 24 mm gap (16 deep), leaving 4 mm each side for the clips"),
    ("rt_w", "30 mm", "mm", "assumption", "width of the trunk bundle laid flat: air feed, cockpit feed, signal cable, Cat6"),
    ("dw_h", "4 mm", "mm", "assumption", "half the size of a draw-wire reserve (8 x 8)"),
    ("pk_l", "150 mm", "mm", "assumption", "length of a connector pocket: a mated plug pair and 100 mm of slack loop"),
    ("pk_h", "40 mm", "mm", "assumption", "half the width of a connector pocket (80)"),
    ("grm_d", "19.1 mm", "mm", "source",
     "Heyco 2836 Shorty Bushing SB 750-625: 19.1 mm hole, panels to 1.6 mm, passes 15.9 mm (maker page, read 2026-10-31); 0.5 mm fit HOLD H-ELE-01"),
    ("grm_s", "12 mm", "mm", "assumption", "felt-only hole for a single cable (no steel, so no bushing)"),
    # F-188 (2026-11-01): CEILING's tray 513101 back hole reads this same expression from the skeleton's values;
    # test_ceiling_crossing_heights_drift fails if the skeleton's numbers move it
    ("z_xc", "z_cf + cass_t - lip_w - grm_s / 2 - 2 mm", "mm", "calculation",
     "the ceiling route's crossing out of B4-CASS, Z 2330: its felt-only Ø12 hole 2 mm below the cassette's 12 mm top lip (no hole through a lip, D-69; WALL's fit check) and level with the hole in the ceiling cassette's back return"),
    ("cs_h", "5.5 mm", "mm", "calculation",
     "half the corner slot in B2-CASS's end return, Y 776-787: inside its gap (from 775.5) and clear of R1-CASS's back lip (from 788)"),
    ("grm_c", "2 mm", "mm", "assumption", "grommet envelope: space taken on the pocket side of a return"),
    # ---- the power unit (PROPOSED by ELECTRICAL, DECIDED by the PM)
    ("pu_w", "296 mm", "mm", "assumption", "power unit width (X): the GFCI receptacle, the two LAN keystone jacks, the breaker window and the vents (D-133; sized first for two 86 x 86 plates); narrowed by 4 mm so its right side (X 391) clears B2's first stud (X 395.75) by 4.75 mm (WALL, through the PM, 2026-10-31)"),
    ("pu_h", "260 mm", "mm", "assumption", "power unit height (Z): the devices above the vents, the three supplies behind (D-133)"),
    ("pu_d", "72 mm", "mm", "calculation",
     "power unit depth (Y) from the felt face: 78 to the frame's skin side (84 - 3 ACP - 3 bond line) less 6 clear"),
    ("pu_x0", "95 mm", "mm", "assumption",
     "power unit left side: clear of the B1-B2 closing seam member (X 1.13-21.13) and its pin-bolt pocket (to X 81); WALL confirms the bay"),
    ("pu_zc", "1000 mm", "mm", "DECIDED", PM + ": the user socket and LAN at the ledge height, about 1000 mm (D-70); v1's plates were at Z 1066"),
    ("pu_clr", "4 mm", "mm", "assumption", "gap between the frame-mounted unit and the floating B2 cassette's cut-out, so the lining stays floating (= cav_gap)"),
    ("plate_ov", "8 mm", "mm", "assumption", "the front plate covers the felt's cut edge: 8 mm past the plain cut-out all round (WALL: the cut-out has no returns)"),
    ("plate_gap", "2 mm", "mm", "assumption", "the front plate stands 2 mm off the felt face on four 2 mm spacers, so the floating lining never touches the unit (D-17)"),
    ("fp_t", "1.5 mm", "mm", "PROPOSED", "front plate 711002: 5052-H32 aluminium 1.5 mm, black anodised AA20 (D-67)"),
    ("pu_x1", "pu_x0 + pu_w", "mm", "calculation", "power unit right side, X 391"),
    ("pu_z0", "pu_zc - pu_h / 2", "mm", "calculation", "power unit bottom, Z 870"),
    ("pu_z1", "pu_zc + pu_h / 2", "mm", "calculation", "power unit top, Z 1130"),
    ("cut_x1", "pu_x1 + pu_clr", "mm", "calculation", "B2-CASS cut-out: its right return, X 395"),
    ("cut_z1", "pu_z1 + pu_clr", "mm", "calculation", "B2-CASS cut-out: its top return, Z 1134"),
    ("lt_x", "pu_x1 - 45 mm", "mm", "assumption", "light feed leaves the unit's top 45 mm in from its right side, X 346: its Ø19.1 exit more than 2 diameters from the top's corner relief (C09)"),
    # ---- the inlet and the LAN feed-through: v1's back-wall position (PM ruling)
    ("inlet_x", "120 mm", "mm", "assumption",
     "v1's inlet sits at X 0, which is now the B1-B2 closing seam (D-65); it moves into B2 just clear of the seam member and its pin-bolt pocket"),
    ("inlet_z", "313 mm", "mm", "source", "v1 STEP 'Power Jack' centre Z(v1) 298.3 + 15 (conventions section 4)"),
    ("lan_z", "375 mm", "mm", "source", "v1 STEP 'Jack LAN' centre Z(v1) 360 + 15"),
    ("inlet_d", "24 mm", "mm", "source", "powerCON TRUE1 TOP cut-out Ø23.8 (selection E); etherCON NE8FDP Ø24"),
    ("inlet_l", "35 mm", "mm", "source",
     "depth behind the skin: powerCON TRUE1 TOP 31.2 mm behind its 4.5 mm flange; etherCON NE8FDP 34.55 mm (Neutrik drawings, read 2026-10-31)"),
    ("sl_x", "inlet_x + 30 mm", "mm", "calculation", "mains and LAN sleeve, beside the inlet column, X 150 (centre): its entry hole in the unit's bottom 2 diameters from the corner relief (C09)"),
    ("sl_y", "pod_d / 2 - 30 mm", "mm", "calculation",
     "sleeve centre in the frame bay (frame Y 804-844), Y 820: its entry hole in the unit's bottom stays clear of the back bend"),
    # ---- the trunk to the right wall and the air column
    ("trunk_z", "1100 mm", "mm", "assumption",
     "trunk height in B2-CASS and R1-CASS: above a ledge at about 1000 mm and its brackets, below the R1/R2 joint at Z 1255; INTERIOR keeps the ledge and screen fixings 15 mm clear"),
    ("lx_z2", "trunk_z - 15 mm", "mm", "calculation",
     "upper lead exit in the unit's right side, Z 1085: more than 2 diameters (38.2) below the side's top corner relief (mechanical check C09)"),
    ("lx_z1", "lx_z2 - 40 mm", "mm", "calculation", "lower lead exit, Z 1045: 40 mm below the upper one (2 diameters apart)"),
    ("y_xc", "y_bf + tray_t + felt_t + 6 mm", "mm", "calculation",
     "corner crossing Y 781.5: inside B2-CASS's gap (from Y 775.5) and clear of R1-CASS's back lip (from Y 788)"),
    ("col_w", "217 mm", "mm", "DECIDED", "D-61: the air column is 217 x 360 on skeleton P04"),
    ("col_d", "360 mm", "mm", "DECIDED", "D-61"),
    ("col_y0", "pod_d / 2 - wall_depth", "mm", "calculation", "air column front face, against the decor back plate, Y -645"),
    ("col_y1", "col_y0 + col_d", "mm", "calculation", "air column back face (into the pod), Y -285"),
    ("col_x0", "x_rf - col_w", "mm", "calculation", "air column left face, X 949"),
    ("col_z1", "dt_zb", "mm", "DECIDED", "D-61: the soffit's underside, the top of the air column (Z 15 to 2120) = skeleton dt_zb, the top decor's bottom edge (named value, skeleton v4)"),
    # ---- the column as AIR models it, and the harness route through it (agreed by ELECTRICAL and CEILING 2026-11-01,
    #      the Lead's ask on the 16 clashes; AIR cuts the holes and channels, ELECTRICAL lists the bushings, cordgrips and ties)
    ("col_gap", "5 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the column keeps 5 mm off the floating side lining (PM ruling 2026-11-01)"),
    ("col_xr", "x_rf - col_gap", "mm", "calculation", "the column's right side, X 1161 (AIR's XR)"),
    ("face_t", "12 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the column's and the soffit's faces are 3 mm ACP and 9 mm felt"),
    ("ang_f", "9 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the front corner angles' leg along the face"),
    ("ang_w", "20 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the front corner angles' side leg, 20 deep"),
    ("ang_t", "2 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the corner angles' thickness, aluminium"),
    ("hub_w", "180 mm", "mm", "DECIDED", "D-61, D-70: the 180 x 180 zone for the sensor hub and controls"),
    ("hub_t", "29 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the hub zone up to 29 deep from the column's room face (air report 7e)"),
    ("hub_zc", "1200 mm", "mm", "source", "selection F3: the hub at seated eye height, Z 1200 (REQ-ELE-04)"),
    ("hub_xc", "(col_x0 + face_t + ang_f + col_xr - ang_f) / 2", "mm", "calculation",
     "the hub zone centred between the front angles' legs, X 1061: 710041 takes AIR's zone (618101 is gone)"),
    ("y_ent", "col_y1 - face_t - ang_w / 2", "mm", "calculation", "the trunk's entries in the FR angle's side leg, at its middle, Y -307"),
    ("ent_d", "11.1 mm", "mm", "source",
     "Heyco SB 437-5 snap bushing: mounting hole 0.437 in (11.1), bore 7.9, panels to 3.2 mm (Heyco Snap Bushings sheet, read 2026-11-01)"),
    ("ent_z1", "hub_zc - hub_w / 2 + 40 mm", "mm", "confirmed", "agreed with CEILING: the first entry 40 above the hub zone's bottom, Z 1150"),
    ("ent_dz", "25 mm", "mm", "assumption", "the second entry 25 above the first (Z 1175): one cable in each bushing (5.31 and 4.22 mm)"),
    ("fx_d", "32 mm", "mm", "assumption",
     "felt hole FX-COL: it passes the mated 10-way Mini-Fit pair (about 24.4 x 12.6) when the column is fitted, and is hidden behind it"),
    ("y_fx", "y_ent - 5 mm", "mm", "calculation", "FX-COL's centre 5 behind the entries: its front edge 11 behind the column's room face (Y -312)"),
    ("z_fx", "ent_z1 + ent_dz / 2", "mm", "calculation", "FX-COL's centre between the two entries, Z 1162.5"),
    ("pk_col", "220 mm", "mm", "assumption",
     "pocket P8 for the trunk's joint behind the column: the mated 10-way pair and 150 of slack; its first tie 20 inside its end stays 150 clear of FX-COL, as at the power unit (the cables cross the 5 mm gap to the fixed column with slack)"),
    ("ch_w", "24 mm", "mm", "confirmed", "agreed with CEILING: the 24 x 24 channels AIR cuts in the column's front fill and the soffit's fill"),
    ("ch_x", "col_xr - ang_f - ch_w / 2", "mm", "calculation", "the channels' middle, X 1140, beside the FR angle"),
    ("fill_z1", "1890 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the top of the column's fill (the follow-up lifted the cartridge and its fill by 6)"),
    ("pl_t", "1 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the high plenum side plate 611108, 1 mm aluminium, inside the column's right side"),
    ("dr_face_y", "-641.14 mm", "mm", "source", "FRONT's DR (#313): its access panel's room face, the column's door side as AIR reads it"),
    ("op_x1", "1146 mm", "mm", "source", "FRONT's DR (#313): the right edge of DR's opening from the column's plenum into AIR's upper transition (X 961 to 1146, Z 1895 to 2102)"),
    ("tie_pp", "15 mm", "mm", "assumption",
     "a tie point in AIR's plates is a pair of 6.4 holes 15 apart: a plain tie loops out one and back in the other, so only its strap sits in the 5 mm gap to the floating felt (a push-mount's arrow would reach it)"),
    ("tie_pz", "fill_z1 + 15 mm", "mm", "confirmed", "agreed with CEILING: 611108's lower tie holes 15 above its bottom, Z 1905"),
    ("tie_ay", "dr_face_y + 43.5 mm", "mm", "confirmed", "agreed with CEILING: 611108's first tie point 43.5 from DR's panel face (Y -597.64), the others 100 apart"),
    ("tie_az1", "1960 mm", "mm", "confirmed", "agreed with CEILING: the FR angle's first tie pair (1960 and 1975)"),
    ("tie_az2", "2040 mm", "mm", "confirmed", "ELECTRICAL to CEILING 2026-11-01: the FR angle's second tie pair (2040 and 2055), so the exhaust lead bends into the soffit's cordgrip above it"),
    ("cg_d", "12 mm", "mm", "source",
     "Heyco RLTCG M12 cordgrip (M4330, nut included): clearance hole 12.0, cable 1.7 to 5.3, IP68, UL listed E51579 (Heyco metric cordgrips sheet, read 2026-11-01)"),
    ("cg_l", "21.4 mm", "mm", "calculation", "the cordgrip's body past its panel: 29.5 overall less its 8.1 thread"),
    ("cg_w", "18.5 mm", "mm", "calculation", "the cordgrip's hex across corners: 16.0 across flats / cos 30"),
    ("cg_n", "5 mm", "mm", "assumption", "the cordgrip's locknut on the panel's far side"),
    ("sof_y", "col_y1 - face_t - 19 mm", "mm", "confirmed", "agreed with CEILING: the soffit hole 19 behind the fixed underside's room edge, Y -316"),
    ("sof_fill_t", "27 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the soffit's fill under the cartridge"),
    ("fbox_t", "3 mm", "mm", "source", "AIR's model as CEILING built it for the agreed route (2026-11-01): the fan box casings, 3 mm aluminium (D-124)"),
    ("fb_y", "dr_face_y + 5 mm + 314 mm - fbox_t - 50 mm - 12.5 mm", "mm", "calculation",
     "AIR: the exhaust fan box's bottom hole 12.5 clear of its room-side lining (Y -387.64): box from DR's face + 5, 314 deep, 50 lining"),
    ("fb_x", "1095 mm", "mm", "PROPOSED",
     "ELECTRICAL to CEILING 2026-11-01: the fan box hole moved left of the box's far-end lining (X 1108 to 1158) so the cordgrip's body stands in the open box; CEILING picks this or a path cut through that lining"),
    ("y_kit", "(col_y1 + y_bf) / 2", "mm", "calculation", "voice kit drop at the middle of the work wall beside the column, Y 240.5 (D-70, REQ-VCK-02)"),
    ("kit_d", "60 mm", "mm", "assumption", "felt access hole for the kit drop, behind the screen, with a felt plug"),
    ("call_z", "1450 mm", "mm", "assumption", "call light feed height, above the screen zone (D-70)"),
    ("call_y", "y_kit - 450 mm", "mm", "calculation",
     "call light feed at the front end of a 900 mm bar centred on the work wall, Y -209.5; its drop from the shelf runs straight down here"),
    ("shelf_z", "2250 mm", "mm", "assumption",
     "light shelf height: its feed on the back wall and the call light's drop on the right wall sit behind it (Z 2200-2290 assumed; CEILING sets the shelf)"),
    ("ceil_x", "inner_w / 4", "mm", "calculation", "CEILING P01: the cassette's cable holes sit on the right ceiling cassette's centre, a quarter of the skeleton's inner width (X +583, PR #32)"),
    ("ceil_y0", "col_y1 + 3 mm", "mm", "calculation", "CEILING P01: the ceiling cassette's front return, 3 mm behind the soffit's back face (Y -282)"),
    ("ceil_y1", "y_bf - 3 mm", "mm", "calculation", "CEILING P01: the ceiling cassette's back return, 3 mm off the back lining's felt face (Y 763)"),
    ("soff_y", "col_y1", "mm", "DECIDED", "D-61: the soffit's back face is flush with the column's face, Y -285"),
]

# Skeleton values offline (from 100000_P04_POD-SKELETON-PARAMETERS.csv); the
# test reads the CSV and checks these match it.
SKELETON_VALUES = {
    "pod_w": 2500.0, "pod_d": 1700.0, "pod_h": 2400.0, "outer_t": 46.0, "cav_gap": 4.0, "cass_t": 34.0,
    "stack_t": 84.0, "seam_gap": 2.26, "lin_gap": 4.0, "wall_depth": 1495.0, "side_h": 1142.74,
    "back_ph": 1118.61, "back_oh": 2239.48, "half_pw": 1200.61, "panel_z0": 112.26,
    "dt_zb": 2120.0, "inner_w": 2332.0,
}

_MM = re.compile(r"(\d)\s*mm\b")


def evaluate(expr, values):
    """Evaluate a Fusion-style length expression offline (mm)."""
    e = _MM.sub(r"\1", expr)
    return float(eval(e, {"__builtins__": {}, "abs": abs, "sqrt": math.sqrt}, values))


def values(skeleton=None):
    """All parameter values in mm. `skeleton` overrides the skeleton values
    (the Fusion build passes the live derived values)."""
    v = dict(SKELETON_VALUES)
    if skeleton:
        v.update(skeleton)
    for name, expr, _u, _s, _src in PARAMS:
        v[name] = evaluate(expr, v)
    return v


# ------------------------------------------------------------------ components
# key: part number, name, Vietnamese name, kind (HS assembly, MP made, PI bought)
COMPONENTS = [
    ("PU", "710001", "ELECTRICAL - POWER UNIT - B2", "Điện - hộp nguồn - vách sau B2", "HS"),
    ("LIGHT", "710011", "ELECTRICAL - HARNESS - LIGHT FEED - B2/B4", "Điện - bó dây cấp đèn - vách sau", "HS"),
    ("TRUNK", "710021", "ELECTRICAL - HARNESS - TRUNK - B2/R1", "Điện - bó dây chính - vách sau và vách phải", "HS"),
    ("COLUMN", "710023", "ELECTRICAL - HARNESS - AIR COLUMN", "Điện - bó dây cột gió", "HS"),
    ("CALL", "710024", "ELECTRICAL - HARNESS - CALL LIGHT - R2", "Điện - bó dây đèn gọi video - vách phải trên", "HS"),
    ("CEIL", "710031", "ELECTRICAL - DRAW WIRE - CEILING ROUTE", "Điện - dây mồi - đường trần", "HS"),
    ("HUB", "710041", "ELECTRICAL - HUB AND CONTROLS ZONE", "Điện - vùng cảm biến và nút bấm", "HS"),
]

# ------------------------------------------------------------------ bodies
# Each body is a reserved space (a route, a connector pocket, a grommet, a
# unit), not a manufactured shape. Felt holes (FX-*, FS-CNR, FA-KIT) pass the
# felt only: the felt sits on the tray's 12 mm edge lips with the 24 mm gap
# behind it (WALL and CEILING cassette models), so no steel edge is there and
# a bushing (which needs a 0.5-1.6 mm panel) has nothing to sit in. Their span
# starts at the cassette face plane, 0.5 mm in front of the felt (the lip
# plane), which is air at these spots: guideline 4.3 step 4 lets CAD reserve the
# space of a part on HOLD. Boxes: x, y, z as (low, high) expressions.
# Cylinders: axis, centre (the two other coordinates in x, y, z order),
# diameter and span along the axis. `allow` names the skeleton P04 envelopes
# the body is meant to sit inside, with the reason (the clash check fails on
# any other overlap).
B, C = "box", "cyl"
IN_B2CASS = ("B2-CASS", "in the 24 mm cable gap of the lower back lining (D-26)")
IN_B4CASS = ("B4-CASS", "in the cable gap of the upper back lining (D-26)")
IN_R1CASS = ("R1-CASS", "in the cable gap of the lower right lining (D-26)")
IN_R2CASS = ("R2-CASS", "in the cable gap of the upper right lining (D-26)")
IN_C2CASS = ("C2-CASS", "in the ceiling lining's cable gap (D-41)")
IN_B2 = ("B2", "inside the outer panel B2's frame bay, factory-fitted (IF-12)")

BODIES = [
    # ---- power unit, inlet, LAN feed-through, mains sleeve (all mains parts: B2 only)
    dict(code="PU", comp="PU", name="POWER UNIT ENVELOPE", kind=B,
         x=("pu_x0", "pu_x1"), y=("y_bf", "y_bf + pu_d"), z=("pu_z0", "pu_z1"),
         allow=[IN_B2, ("B2-CASS", "through the cassette's cut-out, 4 mm clear all round (pu_clr)")]),
    dict(code="PU-PLATE", comp="PU", name="FRONT PLATE - OVER THE FELT EDGE, 2 MM OFF THE FELT", kind=B,
         x=("pu_x0 - pu_clr - plate_ov", "pu_x1 + pu_clr + plate_ov"), y=("y_bf - plate_gap - fp_t", "y_bf - plate_gap"),
         z=("pu_z0 - pu_clr - plate_ov", "pu_z1 + pu_clr + plate_ov"), allow=[]),
    dict(code="INLET", comp="PU", name="MAINS INLET ENVELOPE", kind=C, axis="y",
         c=("inlet_x", "inlet_z"), d="inlet_d", a=("pod_d / 2 - inlet_l", "pod_d / 2"), allow=[IN_B2]),
    dict(code="LAN-FT", comp="PU", name="LAN FEED-THROUGH ENVELOPE", kind=C, axis="y",
         c=("inlet_x", "lan_z"), d="inlet_d", a=("pod_d / 2 - inlet_l", "pod_d / 2"), allow=[IN_B2]),
    dict(code="SLEEVE", comp="PU", name="MAINS AND LAN SLEEVE", kind=B,
         x=("sl_x - 10 mm", "sl_x + 10 mm"), y=("sl_y - 10 mm", "sl_y + 10 mm"), z=("inlet_z - 12 mm", "pu_z0"),
         allow=[IN_B2]),
    # ---- light feed: unit top -> B2-CASS -> B4-CASS -> light shelf (W10)
    dict(code="P5", comp="LIGHT", name="POCKET - LIGHT FEED AT THE UNIT", kind=B,
         x=("lt_x - pk_h", "lt_x + pk_h"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("cut_z1 + tray_t", "cut_z1 + tray_t + 80 mm"),
         allow=[IN_B2CASS]),
    dict(code="L1-B2", comp="LIGHT", name="ROUTE - LIGHT FEED - B2-CASS", kind=B,
         x=("lt_x - rt_h", "lt_x + rt_h"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("cut_z1 + tray_t + 80 mm", "z_b2t - tray_t"),
         allow=[IN_B2CASS]),
    dict(code="G-B2-B4", comp="LIGHT", name="GROMMET PAIR - B2/B4 LINING JOINT", kind=C, axis="z",
         c=("lt_x", "y_bg"), d="grm_d", a=("z_b2t - tray_t", "z_b4b + tray_t"),
         allow=[IN_B2CASS, IN_B4CASS]),
    dict(code="P4", comp="LIGHT", name="POCKET - LIGHT FEED AT THE B2/B4 JOINT - B4-CASS", kind=B,
         x=("lt_x - pk_h", "lt_x + pk_h"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("z_b4b + tray_t", "z_b4b + tray_t + pk_l"),
         allow=[IN_B4CASS]),
    dict(code="L1-B4", comp="LIGHT", name="ROUTE - LIGHT FEED - B4-CASS", kind=B,
         x=("lt_x - rt_h", "lt_x + rt_h"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("z_b4b + tray_t + pk_l", "shelf_z - 60 mm"),
         allow=[IN_B4CASS]),
    dict(code="P6", comp="LIGHT", name="POCKET - LIGHT SHELF FEED", kind=B,
         x=("lt_x - pk_h", "lt_x + pk_h"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("shelf_z - 60 mm", "shelf_z + 40 mm"),
         allow=[IN_B4CASS]),
    dict(code="FX-SHELF", comp="LIGHT", name="FELT HOLE - LIGHT SHELF EXIT (FELT ONLY, NO STEEL)", kind=C, axis="y",
         c=("lt_x", "shelf_z"), d="16 mm", a=("y_bf", "y_bf + tray_t + felt_t"), allow=[IN_B4CASS]),
    # ---- trunk: unit side -> B2-CASS -> corner -> R1-CASS -> kit drop and air column (W20, W24, W30, W31)
    dict(code="P1", comp="TRUNK", name="POCKET - TRUNK AT THE UNIT", kind=B,
         x=("cut_x1 + tray_t", "cut_x1 + tray_t + pk_l"), y=("y_bg - rt_h", "y_bg + rt_h"), z=("trunk_z - pk_h", "trunk_z + pk_h"),
         allow=[IN_B2CASS]),
    dict(code="T1-B2", comp="TRUNK", name="ROUTE - TRUNK - B2-CASS", kind=B,
         x=("cut_x1 + tray_t + pk_l", "x_rf - tray_t - grm_c"), y=("y_bg - rt_h", "y_bg + rt_h"),
         z=("trunk_z - rt_w / 2", "trunk_z + rt_w / 2"), allow=[IN_B2CASS]),
    dict(code="FS-CNR", comp="TRUNK", name="FELT SLOT - CORNER - R1-CASS (HIDDEN BEHIND B2-CASS)", kind=B,
         x=("x_rf", "x_rf + tray_t + felt_t"), y=("y_bf + 2 mm", "y_bf + 20 mm"),
         z=("trunk_z - 60 mm", "trunk_z + 60 mm"), allow=[IN_R1CASS]),
    dict(code="P2", comp="TRUNK", name="POCKET - TRUNK AT THE BACK-RIGHT CORNER - R1-CASS", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_xc + cs_h - pk_l", "y_xc + cs_h"),
         z=("trunk_z - pk_h", "trunk_z + pk_h"), allow=[IN_R1CASS]),
]
BODIES.append(dict(code="S-CNR", comp="TRUNK", name="GROMMETED SLOT - CORNER - B2-CASS END RETURN", kind=B,
                   x=("x_rf - tray_t - grm_c", "x_rf"), y=("y_xc - cs_h", "y_xc + cs_h"),
                   z=("trunk_z - 40 mm", "trunk_z + 40 mm"), allow=[IN_B2CASS]))
BODIES += [
    dict(code="T1-R1A", comp="TRUNK", name="ROUTE - TRUNK - R1-CASS - CORNER TO KIT", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_kit + pk_l / 2", "y_xc + cs_h - pk_l"),
         z=("trunk_z - rt_w / 2", "trunk_z + rt_w / 2"), allow=[IN_R1CASS]),
    dict(code="P3-KIT", comp="TRUNK", name="POCKET - VOICE KIT DROP", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_kit - pk_l / 2", "y_kit + pk_l / 2"),
         z=("trunk_z - rt_w / 2", "trunk_z + rt_w / 2 + 120 mm"), allow=[IN_R1CASS]),
    dict(code="FA-KIT", comp="TRUNK", name="FELT HOLE - VOICE KIT ACCESS (FELT ONLY, NO STEEL)", kind=C, axis="x",
         c=("y_kit", "trunk_z + 80 mm"), d="kit_d", a=("x_rf", "x_rf + tray_t + felt_t"), allow=[IN_R1CASS]),
    dict(code="T1-R1B", comp="TRUNK", name="ROUTE - TRUNK - R1-CASS - KIT TO THE COLUMN JOINT", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_fx - fx_d / 2 - 10 mm + pk_col", "y_kit - pk_l / 2"),
         z=("trunk_z - rt_w / 2", "trunk_z + rt_w / 2"), allow=[IN_R1CASS]),
    dict(code="P8", comp="TRUNK", name="POCKET - TRUNK JOINT BEHIND THE AIR COLUMN - R1-CASS", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_fx - fx_d / 2 - 10 mm", "y_fx - fx_d / 2 - 10 mm + pk_col"),
         z=("trunk_z - rt_w / 2", "z_fx + fx_d / 2 + 10 mm"), allow=[IN_R1CASS]),
    dict(code="FX-COL", comp="TRUNK", name="FELT HOLE - THE COLUMN JOINT, HIDDEN BEHIND THE COLUMN (FELT ONLY, NO STEEL)", kind=C, axis="x",
         c=("y_fx", "z_fx"), d="fx_d", a=("col_xr + grm_c", "x_rf + tray_t + felt_t"), allow=[IN_R1CASS]),
    # ---- air column: the trunk's two entries through the FR angle into the hub zone, then up AIR's channel in the fill
    #      (agreed with CEILING 2026-11-01). Supply fans and sensor: along the high plenum plate to DR's opening, where AIR's
    #      upper transition takes them on its own tie points (its reserved space, D-105). Exhaust fans: up the FR angle,
    #      a cordgrip through the soffit's fixed underside, the soffit fill's channel, a cordgrip into the fan box
    dict(code="G-COL1", comp="COLUMN", name="BUSHED HOLE - FR ANGLE - AIR FEED W20D", kind=C, axis="x",
         c=("y_ent", "ent_z1"), d="ent_d", a=("col_xr - ang_t - grm_c", "col_xr + grm_c"), allow=[]),
    dict(code="G-COL2", comp="COLUMN", name="BUSHED HOLE - FR ANGLE - HUB LINK W24D", kind=C, axis="x",
         c=("y_ent", "ent_z1 + ent_dz"), d="ent_d", a=("col_xr - ang_t - grm_c", "col_xr + grm_c"), allow=[]),
    dict(code="IN-HUB", comp="COLUMN", name="ROUTE - FR ANGLE INTO THE HUB ZONE", kind=B,
         x=("hub_xc + hub_w / 2", "col_xr - ang_t - grm_c"), y=("y_ent - ent_d / 2", "y_ent + ent_d / 2"),
         z=("ent_z1 - ent_d / 2", "ent_z1 + ent_dz + ent_d / 2"), allow=[]),
    dict(code="HUB", comp="HUB", name="SENSOR HUB AND CONTROLS ZONE", kind=B,
         x=("hub_xc - hub_w / 2", "hub_xc + hub_w / 2"), y=("col_y1 - hub_t", "col_y1"), z=("hub_zc - hub_w / 2", "hub_zc + hub_w / 2"),
         allow=[]),
    dict(code="CH-FILL", comp="COLUMN", name="ROUTE - CHANNEL IN THE COLUMN FILL", kind=B,
         x=("ch_x - ch_w / 2 + 0.5 mm", "ch_x + ch_w / 2 - 0.5 mm"), y=("col_y1 - face_t - ch_w + 0.5 mm", "col_y1 - face_t - 0.5 mm"),
         z=("hub_zc + hub_w / 2", "fill_z1"), allow=[]),
    dict(code="PL-UP", comp="COLUMN", name="ROUTE - OVER THE FILL INTO THE PLENUM", kind=B,
         x=("ch_x - ch_w / 2 + 0.5 mm", "ch_x + ch_w / 2 - 0.5 mm"), y=("col_y1 - face_t - ch_w + 0.5 mm", "col_y1 - face_t - 0.5 mm"),
         z=("fill_z1", "tie_pz + tie_pp / 2 + rt_h"), allow=[]),
    dict(code="PL-RUN", comp="COLUMN", name="ROUTE - ALONG THE HIGH PLENUM PLATE - SUPPLY FANS AND SENSOR", kind=B,
         x=("col_xr - pl_t - 2 * rt_h - 0.5 mm", "col_xr - pl_t - 0.5 mm"), y=("tie_ay - 20 mm", "col_y1 - face_t - ch_w + 0.5 mm"),
         z=("tie_pz + tie_pp / 2 - rt_h", "tie_pz + tie_pp / 2 + rt_h"), allow=[]),
    dict(code="PL-JOG", comp="COLUMN", name="ROUTE - TO DR'S OPENING - SUPPLY FANS AND SENSOR", kind=B,
         x=("op_x1 - 4 mm - 2 * rt_h", "col_xr - pl_t - 0.5 mm"), y=("dr_face_y + 0.5 mm", "tie_ay - 20 mm"),
         z=("tie_pz + tie_pp / 2 - rt_h", "tie_pz + tie_pp / 2 + rt_h"), allow=[]),
    dict(code="UP-ANG", comp="COLUMN", name="ROUTE - UP THE FR ANGLE IN THE PLENUM - EXHAUST FANS", kind=B,
         x=("col_xr - ang_f + 0.5 mm", "col_xr - ang_t - 0.5 mm"), y=("col_y1 - face_t - ang_w + 0.5 mm", "col_y1 - face_t - ang_t - 0.5 mm"),
         z=("fill_z1", "col_z1 - cg_l - 40 mm"), allow=[]),
    dict(code="TO-SOF", comp="COLUMN", name="ROUTE - FR ANGLE TO THE SOFFIT CORDGRIP - EXHAUST FANS", kind=B,
         x=("ch_x - cg_w / 2", "col_xr - ang_t - 0.5 mm"), y=("sof_y - cg_w / 2", "col_y1 - face_t - ang_t - 0.5 mm"),
         z=("col_z1 - cg_l - 40 mm", "col_z1 - cg_l"), allow=[]),
    dict(code="G-SOF-B", comp="COLUMN", name="CORDGRIP BODY - SOFFIT UNDERSIDE, PLENUM SIDE", kind=C, axis="z",
         c=("ch_x", "sof_y"), d="cg_w", a=("col_z1 - cg_l", "col_z1"), allow=[]),
    dict(code="G-SOFFIT", comp="COLUMN", name="CORDGRIP - THROUGH THE SOFFIT'S FIXED UNDERSIDE", kind=C, axis="z",
         c=("ch_x", "sof_y"), d="cg_d", a=("col_z1", "col_z1 + face_t"), allow=[]),
    dict(code="G-SOF-N", comp="COLUMN", name="CORDGRIP NUT - SOFFIT FILL SIDE", kind=C, axis="z",
         c=("ch_x", "sof_y"), d="cg_w", a=("col_z1 + face_t", "col_z1 + face_t + cg_n"), allow=[]),
    dict(code="SOF-CH", comp="COLUMN", name="ROUTE - CHANNEL IN THE SOFFIT FILL - EXHAUST FANS", kind=B,
         x=("fb_x - cg_w / 2", "ch_x + ch_w / 2 - 0.5 mm"), y=("fb_y - cg_w / 2", "sof_y + cg_w / 2"),
         z=("col_z1 + face_t + cg_n", "col_z1 + face_t + sof_fill_t - cg_n"), allow=[]),
    dict(code="G-FB-N", comp="COLUMN", name="CORDGRIP NUT - UNDER THE EXHAUST FAN BOX", kind=C, axis="z",
         c=("fb_x", "fb_y"), d="cg_w", a=("col_z1 + face_t + sof_fill_t - cg_n", "col_z1 + face_t + sof_fill_t"), allow=[]),
    dict(code="G-FBOX", comp="COLUMN", name="CORDGRIP - THROUGH THE EXHAUST FAN BOX'S BOTTOM", kind=C, axis="z",
         c=("fb_x", "fb_y"), d="cg_d", a=("col_z1 + face_t + sof_fill_t", "col_z1 + face_t + sof_fill_t + fbox_t"), allow=[]),
    dict(code="G-FB-B", comp="COLUMN", name="CORDGRIP BODY - INSIDE THE EXHAUST FAN BOX", kind=C, axis="z",
         c=("fb_x", "fb_y"), d="cg_w", a=("col_z1 + face_t + sof_fill_t + fbox_t", "col_z1 + face_t + sof_fill_t + fbox_t + cg_l"),
         allow=[]),
    # ---- call light: fed down from the light shelf through R2-CASS to the bar on the work wall (W12)
    dict(code="FX-CALL0", comp="CALL", name="FELT HOLE - R2-CASS BEHIND THE SHELF (FELT ONLY, NO STEEL)", kind=C, axis="x",
         c=("call_y", "shelf_z"), d="grm_s", a=("x_rf", "x_rf + tray_t + felt_t"), allow=[IN_R2CASS]),
    dict(code="P7", comp="CALL", name="POCKET - CALL LIGHT DROP AT THE SHELF - R2-CASS", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("call_y - pk_h", "call_y + pk_h"),
         z=("shelf_z - grm_s / 2 - pk_l", "shelf_z - grm_s / 2"), allow=[IN_R2CASS]),
    dict(code="CALL-R2", comp="CALL", name="ROUTE - CALL LIGHT DROP - R2-CASS", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("call_y - rt_h", "call_y + rt_h"),
         z=("call_z + grm_s / 2", "shelf_z - grm_s / 2 - pk_l"), allow=[IN_R2CASS]),
    dict(code="FX-CALL2", comp="CALL", name="FELT HOLE - CALL LIGHT EXIT (FELT ONLY, NO STEEL)", kind=C, axis="x",
         c=("call_y", "call_z"), d="grm_s", a=("x_rf", "x_rf + tray_t + felt_t"), allow=[IN_R2CASS]),
    # ---- ceiling route (D-41): back-wall top -> ceiling cassette gap -> soffit back face (W33)
    dict(code="C1-UP", comp="CEIL", name="DRAW WIRE - B4-CASS UP", kind=B,
         x=("lt_x - dw_h", "lt_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("shelf_z + 40 mm", "z_cf - 4 mm"),
         allow=[IN_B4CASS]),
    dict(code="C1-JOG", comp="CEIL", name="DRAW WIRE - B4-CASS ALONG X", kind=B,
         x=("lt_x - dw_h", "ceil_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("z_cf - 4 mm", "z_cf + 4 mm"),
         allow=[IN_B4CASS]),
    dict(code="C1-RISE", comp="CEIL", name="DRAW WIRE - B4-CASS TO THE CEILING HOLE", kind=B,
         x=("ceil_x - dw_h", "ceil_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("z_cf + 4 mm", "z_xc + dw_h"),
         allow=[IN_B4CASS]),
    dict(code="FX-CEIL", comp="CEIL", name="FELT HOLE - B4-CASS BELOW ITS TOP LIP (FELT ONLY, NO STEEL)", kind=C, axis="y",
         c=("ceil_x", "z_xc"), d="grm_s", a=("y_bf", "y_bf + tray_t + felt_t"), allow=[IN_B4CASS]),
    dict(code="G-CEIL-B", comp="CEIL", name="GROMMET - CEILING CASSETTE BACK RETURN", kind=C, axis="y",
         c=("ceil_x", "z_xc"), d="grm_d", a=("ceil_y1 - tray_t", "y_bf"), allow=[IN_C2CASS]),
    dict(code="C1-CEIL", comp="CEIL", name="DRAW WIRE - CEILING CASSETTE", kind=B,
         x=("ceil_x - dw_h", "ceil_x + dw_h"), y=("ceil_y0 + tray_t", "ceil_y1 - tray_t"), z=("z_xc - dw_h", "z_cg + dw_h"),
         allow=[IN_C2CASS]),
    dict(code="G-CEIL-F", comp="CEIL", name="GROMMET - CEILING CASSETTE FRONT RETURN", kind=C, axis="y",
         c=("ceil_x", "z_cg"), d="grm_d", a=("soff_y", "ceil_y0 + tray_t"), allow=[IN_C2CASS]),
]


def body_box(b, v):
    """Axis-aligned box (x0, y0, z0, x1, y1, z1) of a body, offline."""
    if b["kind"] == B:
        x0, x1 = (evaluate(e, v) for e in b["x"])
        y0, y1 = (evaluate(e, v) for e in b["y"])
        z0, z1 = (evaluate(e, v) for e in b["z"])
        return (x0, y0, z0, x1, y1, z1)
    r = evaluate(b["d"], v) / 2
    c1, c2 = (evaluate(e, v) for e in b["c"])
    a0, a1 = (evaluate(e, v) for e in b["a"])
    if b["axis"] == "x":
        return (a0, c1 - r, c2 - r, a1, c1 + r, c2 + r)
    if b["axis"] == "y":
        return (c1 - r, a0, c2 - r, c1 + r, a1, c2 + r)
    return (c1 - r, c2 - r, a0, c1 + r, c2 + r, a1)


def body_volume(b, v):
    x0, y0, z0, x1, y1, z1 = body_box(b, v)
    if b["kind"] == B:
        return (x1 - x0) * (y1 - y0) * (z1 - z0)
    r = evaluate(b["d"], v) / 2
    span = {"x": x1 - x0, "y": y1 - y0, "z": z1 - z0}[b["axis"]]
    return math.pi * r * r * span


# ------------------------------------------------------------------ skeleton P04 envelopes (offline copy)
# The boxes of the skeleton envelopes these bodies sit in or near, from
# pod_skeleton.py's expressions (P04). The Fusion build checks against the
# real skeleton bodies; this copy lets the offline test check the same rule.
def skeleton_boxes(v):
    XL, XR = -v["pod_w"] / 2, v["pod_w"] / 2
    YB, YW = v["pod_d"] / 2, v["pod_d"] / 2 - v["wall_depth"]
    XIL, XIR = XL + v["stack_t"], XR - v["stack_t"]
    XOL, XOR = XL + v["outer_t"], XR - v["outer_t"]
    s, p0, ph, oh = v["seam_gap"], v["panel_z0"], v["back_ph"], v["back_oh"]
    ltop = v["pod_h"] - v["outer_t"] - v["lin_gap"]
    up0 = p0 + ph + s
    out = {
        "B1": (XOL + s, YB - v["outer_t"], p0, XOL + s + v["half_pw"], YB, p0 + ph),
        "B2": (XOR - s - v["half_pw"], YB - v["outer_t"], p0, XOR - s, YB, p0 + ph),
        "B3": (XOL + s, YB - v["outer_t"], up0, XOL + s + v["half_pw"], YB, p0 + oh),
        "B4": (XOR - s - v["half_pw"], YB - v["outer_t"], up0, XOR - s, YB, p0 + oh),
        "B1-CASS": (XIL, YB - v["stack_t"], p0, 0.0, YB - v["stack_t"] + v["cass_t"], p0 + ph),
        "B2-CASS": (0.0, YB - v["stack_t"], p0, XIR, YB - v["stack_t"] + v["cass_t"], p0 + ph),
        "B3-CASS": (XIL, YB - v["stack_t"], up0, 0.0, YB - v["stack_t"] + v["cass_t"], ltop),
        "B4-CASS": (0.0, YB - v["stack_t"], up0, XIR, YB - v["stack_t"] + v["cass_t"], ltop),
        "R1": (XR - v["outer_t"], YW + s, p0, XR, YB, p0 + v["side_h"]),
        "R2": (XR - v["outer_t"], YW + s, p0 + v["side_h"] + s, XR, YB, v["pod_h"]),
        "R1-CASS": (XIR, YW, p0, XIR + v["cass_t"], YB - v["stack_t"] + v["cass_t"], p0 + v["side_h"]),
        "R2-CASS": (XIR, YW, p0 + v["side_h"] + s, XIR + v["cass_t"], YB - v["stack_t"] + v["cass_t"], ltop),
        "C2": (XOR - s - v["half_pw"], YW, v["pod_h"] - v["outer_t"], XOR - s, YB, v["pod_h"]),
        "C2-CASS": (0.0, YW, v["pod_h"] - v["stack_t"], XIR, YB - v["stack_t"], v["pod_h"] - v["stack_t"] + v["cass_t"]),
        # DR as its bounding box only (it is faceted); the Fusion check is exact
        "DR": (XR - 1016.0, -v["pod_d"] / 2, 110.0, XR, YW, v["pod_h"]),
    }
    return out


def overlap(a, b):
    dx = min(a[3], b[3]) - max(a[0], b[0])
    dy = min(a[4], b[4]) - max(a[1], b[1])
    dz = min(a[5], b[5]) - max(a[2], b[2])
    return max(dx, 0.0) * max(dy, 0.0) * max(dz, 0.0)


# The edit test's edits (edit_test_electrical.py runs them on the exported .f3d; the offline test checks
# first that each keeps every reserved space a real box). One moves the power unit (the socket height the PM
# set; there is about 16 mm of room above its light-feed pocket, so it moves down), one the trunk, one a
# skeleton size the routes follow, and one a pocket and grommet size.
EDIT_TEST_EDITS = [
    ("power unit down 50 mm", {"pu_zc": "950 mm"}),
    ("trunk up 50 mm", {"trunk_z": "1150 mm"}),
    ("pod 20 mm deeper (skeleton pod_d)", {"pod_d": "1720 mm"}),
    ("bigger pockets and grommets", {"pk_l": "180 mm", "grm_d": "22 mm"}),
]


def values_with(overrides):
    """All values with an edit applied the way the edit test applies it in Fusion: a skeleton parameter
    replaces the derived value, any other parameter its expression; every dependant is evaluated again."""
    sk = dict(SKELETON_VALUES)
    for name, expr in overrides.items():
        if name in SKELETON_PARAMS:
            sk[name] = evaluate(expr, sk)
    v = dict(sk)
    for name, expr, _u, _s, _src in PARAMS:
        v[name] = evaluate(overrides[name], v) if name in overrides and name not in SKELETON_PARAMS else evaluate(expr, v)
    return v
