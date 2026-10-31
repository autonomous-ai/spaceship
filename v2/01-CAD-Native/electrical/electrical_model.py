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
    ("cs_h", "5.5 mm", "mm", "calculation",
     "half the corner slot in B2-CASS's end return, Y 776-787: inside its gap (from 775.5) and clear of R1-CASS's back lip (from 788)"),
    ("grm_c", "2 mm", "mm", "assumption", "grommet envelope: space taken on the pocket side of a return"),
    ("slot_h", "10 mm", "mm", "assumption",
     "half the height of the grommeted slot in the cut-out's right return (20 x 40): the RJ45 and 6-way plugs pass it on site"),
    ("slot_l", "40 mm", "mm", "assumption", "length of that slot along Z"),
    # ---- the power unit (PROPOSED by ELECTRICAL, DECIDED by the PM)
    ("pu_w", "300 mm", "mm", "assumption", "power unit width (X): two 86 x 86 plates side by side, the RCBO window and the vents"),
    ("pu_h", "260 mm", "mm", "assumption", "power unit height (Z): plates over the RCBO window, the three supplies behind"),
    ("pu_d", "72 mm", "mm", "calculation",
     "power unit depth (Y) from the felt face: 78 to the frame's skin side (84 - 3 ACP - 3 bond line) less 6 clear"),
    ("pu_x0", "95 mm", "mm", "assumption",
     "power unit left side: clear of the B1-B2 closing seam member (X 1.13-21.13) and its pin-bolt pocket (to X 81); WALL confirms the bay"),
    ("pu_zc", "1000 mm", "mm", "DECIDED", PM + ": the user socket and LAN at the ledge height, about 1000 mm (D-70); v1's plates were at Z 1066"),
    ("pu_clr", "4 mm", "mm", "assumption", "gap between the frame-mounted unit and the floating B2 cassette's cut-out, so the lining stays floating (= cav_gap)"),
    ("pu_x1", "pu_x0 + pu_w", "mm", "calculation", "power unit right side, X 395"),
    ("pu_z0", "pu_zc - pu_h / 2", "mm", "calculation", "power unit bottom, Z 870"),
    ("pu_z1", "pu_zc + pu_h / 2", "mm", "calculation", "power unit top, Z 1130"),
    ("cut_x1", "pu_x1 + pu_clr", "mm", "calculation", "B2-CASS cut-out: its right return, X 399"),
    ("cut_z1", "pu_z1 + pu_clr", "mm", "calculation", "B2-CASS cut-out: its top return, Z 1134"),
    ("lt_x", "pu_x1 - 40 mm", "mm", "assumption", "light feed leaves the unit's top 40 mm in from its right side, X 355"),
    # ---- the inlet and the LAN feed-through: v1's back-wall position (PM ruling)
    ("inlet_x", "120 mm", "mm", "assumption",
     "v1's inlet sits at X 0, which is now the B1-B2 closing seam (D-65); it moves into B2 just clear of the seam member and its pin-bolt pocket"),
    ("inlet_z", "313 mm", "mm", "source", "v1 STEP 'Power Jack' centre Z(v1) 298.3 + 15 (conventions section 4)"),
    ("lan_z", "375 mm", "mm", "source", "v1 STEP 'Jack LAN' centre Z(v1) 360 + 15"),
    ("inlet_d", "24 mm", "mm", "source", "powerCON TRUE1 TOP cut-out Ø23.8 (selection E); etherCON NE8FDP Ø24"),
    ("inlet_l", "35 mm", "mm", "source",
     "depth behind the skin: powerCON TRUE1 TOP 31.2 mm behind its 4.5 mm flange; etherCON NE8FDP 34.55 mm (Neutrik drawings, read 2026-10-31)"),
    ("sl_x", "inlet_x + 26 mm", "mm", "calculation", "mains and LAN sleeve, beside the inlet column, X 146 (centre)"),
    ("sl_y", "pod_d / 2 - 26 mm", "mm", "calculation", "sleeve centre in the frame bay (frame Y 804-844), Y 824"),
    # ---- the trunk to the right wall and the air column
    ("trunk_z", "1100 mm", "mm", "assumption",
     "trunk height in B2-CASS and R1-CASS: above a ledge at about 1000 mm and its brackets, below the R1/R2 joint at Z 1255; INTERIOR keeps the ledge and screen fixings 15 mm clear"),
    ("y_xc", "y_bf + tray_t + felt_t + 6 mm", "mm", "calculation",
     "corner crossing Y 781.5: inside B2-CASS's gap (from Y 775.5) and clear of R1-CASS's back lip (from Y 788)"),
    ("col_w", "217 mm", "mm", "DECIDED", "D-61: the air column is 217 x 360 on skeleton P04"),
    ("col_d", "360 mm", "mm", "DECIDED", "D-61"),
    ("col_y0", "pod_d / 2 - wall_depth", "mm", "calculation", "air column front face, against the decor back plate, Y -645"),
    ("col_y1", "col_y0 + col_d", "mm", "calculation", "air column back face (into the pod), Y -285"),
    ("col_x0", "x_rf - col_w", "mm", "calculation", "air column left face, X 949"),
    ("col_z1", "2120 mm", "mm", "DECIDED", "D-61: the soffit's underside, the top of the air column (Z 15 to 2120)"),
    ("col_skin", "1 mm", "mm", "assumption", "column casing in front of its 30 mm fill (CEILING models the column)"),
    ("ch_w", "24 mm", "mm", "assumption", "cable chase in the column's fill, 24 x 24, behind its back face and against the right wall"),
    ("ch_off", "2 mm", "mm", "assumption", "chase clear of the right lining's felt face"),
    ("y_cx", "col_y1 - col_skin - ch_w / 2", "mm", "calculation", "where the trunk leaves R1-CASS's felt into the column chase, Y -298"),
    ("hub_w", "180 mm", "mm", "DECIDED", "D-61, D-70: the 180 x 180 zone for the sensor hub and controls"),
    ("hub_rec", "30 mm", "mm", "assumption", "hub zone recessed into the column's 30 mm fill, behind its back face"),
    ("hub_x0", "col_x0 + 8 mm", "mm", "assumption", "hub zone left edge, so it clears the chase"),
    ("hub_zc", "1200 mm", "mm", "source", "selection F3: the hub at seated eye height, Z 1200 (REQ-ELE-04)"),
    ("y_kit", "(col_y1 + y_bf) / 2", "mm", "calculation", "voice kit drop at the middle of the work wall beside the column, Y 240.5 (D-70, REQ-VCK-02)"),
    ("kit_d", "60 mm", "mm", "assumption", "felt access hole for the kit drop, behind the screen, with a felt plug"),
    ("call_z", "1450 mm", "mm", "assumption", "call light feed height, above the screen zone (D-70)"),
    ("call_y", "y_kit - 450 mm", "mm", "calculation", "call light feed at the front end of a 900 mm bar centred on the work wall, Y -209.5"),
    ("shelf_z", "2250 mm", "mm", "assumption", "light shelf feed height on the back wall, behind the shelf (Z 2200-2290 assumed; INTERIOR sets the shelf)"),
    ("ceil_x", "583 mm", "mm", "source", "CEILING P01: the cassette's cable holes sit on its centre, X +583 for the right half (PR #32)"),
    ("ceil_y0", "-282 mm", "mm", "source", "CEILING P01: the ceiling cassette's front return, behind the soffit (Y -282)"),
    ("ceil_y1", "763 mm", "mm", "source", "CEILING P01: the ceiling cassette's back return, 3 mm off the back lining (Y 763)"),
    ("soff_y", "col_y1", "mm", "DECIDED", "D-61: the soffit's back face is flush with the column's face, Y -285"),
]

# Skeleton values offline (from 100000_P04_POD-SKELETON-PARAMETERS.csv); the
# test reads the CSV and checks these match it.
SKELETON_VALUES = {
    "pod_w": 2500.0, "pod_d": 1700.0, "pod_h": 2400.0, "outer_t": 46.0, "cav_gap": 4.0, "cass_t": 34.0,
    "stack_t": 84.0, "seam_gap": 2.26, "lin_gap": 4.0, "wall_depth": 1495.0, "side_h": 1142.74,
    "back_ph": 1118.61, "back_oh": 2239.48, "half_pw": 1200.61, "panel_z0": 112.26,
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
# unit), not a manufactured shape: guideline 4.3 step 4 lets CAD reserve the
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
IN_DR = ("DR", "through the opening from the right decor block into the column top (D-61)")

BODIES = [
    # ---- power unit, inlet, LAN feed-through, mains sleeve (all mains parts: B2 only)
    dict(code="PU", comp="PU", name="POWER UNIT ENVELOPE", kind=B,
         x=("pu_x0", "pu_x1"), y=("y_bf", "y_bf + pu_d"), z=("pu_z0", "pu_z1"),
         allow=[IN_B2, ("B2-CASS", "through the cassette's cut-out, 4 mm clear all round (pu_clr)")]),
    dict(code="INLET", comp="PU", name="MAINS INLET ENVELOPE", kind=C, axis="y",
         c=("inlet_x", "inlet_z"), d="inlet_d", a=("pod_d / 2 - inlet_l", "pod_d / 2"), allow=[IN_B2]),
    dict(code="LAN-FT", comp="PU", name="LAN FEED-THROUGH ENVELOPE", kind=C, axis="y",
         c=("inlet_x", "lan_z"), d="inlet_d", a=("pod_d / 2 - inlet_l", "pod_d / 2"), allow=[IN_B2]),
    dict(code="SLEEVE", comp="PU", name="MAINS AND LAN SLEEVE", kind=B,
         x=("sl_x - 10 mm", "sl_x + 10 mm"), y=("sl_y - 10 mm", "sl_y + 10 mm"), z=("inlet_z - 12 mm", "pu_z0"),
         allow=[IN_B2]),
    # ---- light feed: unit top -> B2-CASS -> B4-CASS -> light shelf (W10)
    dict(code="G-PU-TOP", comp="LIGHT", name="GROMMET - CUT-OUT TOP RETURN", kind=C, axis="z",
         c=("lt_x", "y_bg"), d="grm_d", a=("cut_z1 - grm_c", "cut_z1 + tray_t"), allow=[IN_B2CASS]),
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
    dict(code="FX-SHELF", comp="LIGHT", name="FELT EXIT - LIGHT SHELF", kind=C, axis="y",
         c=("lt_x", "shelf_z"), d="16 mm", a=("y_bf", "y_bf + tray_t + felt_t"), allow=[IN_B4CASS]),
    # ---- trunk: unit side -> B2-CASS -> corner -> R1-CASS -> kit drop and air column (W20, W24, W30, W31)
    dict(code="S-PU-X", comp="TRUNK", name="GROMMETED SLOT - CUT-OUT RIGHT RETURN", kind=B,
         x=("cut_x1 - grm_c", "cut_x1 + tray_t"), y=("y_bg - slot_h", "y_bg + slot_h"),
         z=("trunk_z - slot_l / 2", "trunk_z + slot_l / 2"), allow=[IN_B2CASS]),
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
    dict(code="FA-KIT", comp="TRUNK", name="FELT ACCESS - VOICE KIT DROP", kind=C, axis="x",
         c=("y_kit", "trunk_z + 80 mm"), d="kit_d", a=("x_rf", "x_rf + tray_t + felt_t"), allow=[IN_R1CASS]),
    dict(code="T1-R1B", comp="TRUNK", name="ROUTE - TRUNK - R1-CASS - KIT TO COLUMN", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_cx - grm_d / 2", "y_kit - pk_l / 2"),
         z=("trunk_z - rt_w / 2", "trunk_z + rt_w / 2"), allow=[IN_R1CASS]),
    dict(code="FX-COL", comp="TRUNK", name="FELT EXIT - INTO THE AIR COLUMN", kind=C, axis="x",
         c=("y_cx", "trunk_z"), d="grm_d", a=("x_rf - ch_off", "x_rf + tray_t + felt_t"), allow=[IN_R1CASS]),
    # ---- air column: chase, hub zone, fan leads (W20 to W24, W32)
    dict(code="CHASE", comp="COLUMN", name="ROUTE - CABLE CHASE IN THE AIR COLUMN", kind=B,
         x=("x_rf - ch_off - ch_w", "x_rf - ch_off"), y=("col_y1 - col_skin - ch_w", "col_y1 - col_skin"),
         z=("trunk_z - grm_d", "col_z1"), allow=[]),
    dict(code="TO-DR", comp="COLUMN", name="ROUTE - TO THE SUPPLY FANS AND INLET SENSOR IN DR", kind=B,
         x=("x_rf - ch_off - ch_w", "x_rf - ch_off"), y=("col_y0 - 20 mm", "col_y1 - col_skin - ch_w"),
         z=("col_z1 - 20 mm", "col_z1 - 4 mm"), allow=[IN_DR]),
    dict(code="TO-SOFFIT", comp="COLUMN", name="ROUTE - TO THE EXHAUST FANS IN THE SOFFIT", kind=B,
         x=("x_rf - ch_off - ch_w", "x_rf - ch_off"), y=("col_y1 - col_skin - ch_w", "col_y1 - col_skin"),
         z=("col_z1", "col_z1 + 40 mm"), allow=[]),
    dict(code="HUB", comp="HUB", name="SENSOR HUB AND CONTROLS ZONE", kind=B,
         x=("hub_x0", "hub_x0 + hub_w"), y=("col_y1 - hub_rec", "col_y1"), z=("hub_zc - hub_w / 2", "hub_zc + hub_w / 2"),
         allow=[]),
    # ---- call light: column -> R2-CASS -> the light bar on the work wall (W12)
    dict(code="FX-CALL1", comp="CALL", name="FELT HOLE - R2-CASS BEHIND THE COLUMN", kind=C, axis="x",
         c=("y_cx", "call_z"), d="grm_s", a=("x_rf - ch_off", "x_rf + tray_t + felt_t"), allow=[IN_R2CASS]),
    dict(code="CALL-R2", comp="CALL", name="ROUTE - CALL LIGHT - R2-CASS", kind=B,
         x=("x_rg - rt_h", "x_rg + rt_h"), y=("y_cx - grm_s / 2", "call_y + grm_s / 2"),
         z=("call_z - rt_h", "call_z + rt_h"), allow=[IN_R2CASS]),
    dict(code="FX-CALL2", comp="CALL", name="FELT EXIT - CALL LIGHT", kind=C, axis="x",
         c=("call_y", "call_z"), d="grm_s", a=("x_rf", "x_rf + tray_t + felt_t"), allow=[IN_R2CASS]),
    # ---- ceiling route (D-41): back-wall top -> ceiling cassette gap -> soffit back face (W33)
    dict(code="C1-UP", comp="CEIL", name="DRAW WIRE - B4-CASS UP", kind=B,
         x=("lt_x - dw_h", "lt_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("shelf_z + 40 mm", "z_cf - 4 mm"),
         allow=[IN_B4CASS]),
    dict(code="C1-JOG", comp="CEIL", name="DRAW WIRE - B4-CASS ALONG X", kind=B,
         x=("lt_x - dw_h", "ceil_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("z_cf - 4 mm", "z_cf + 4 mm"),
         allow=[IN_B4CASS]),
    dict(code="C1-RISE", comp="CEIL", name="DRAW WIRE - B4-CASS TO THE CEILING HOLE", kind=B,
         x=("ceil_x - dw_h", "ceil_x + dw_h"), y=("y_bg - dw_h", "y_bg + dw_h"), z=("z_cf + 4 mm", "z_cg + dw_h"),
         allow=[IN_B4CASS]),
    dict(code="FX-CEIL", comp="CEIL", name="BUSHED HOLE - B4-CASS TOP LIP AND FELT", kind=C, axis="y",
         c=("ceil_x", "z_cg"), d="grm_d", a=("y_bf", "y_bf + tray_t + felt_t"), allow=[IN_B4CASS]),
    dict(code="G-CEIL-B", comp="CEIL", name="GROMMET - CEILING CASSETTE BACK RETURN", kind=C, axis="y",
         c=("ceil_x", "z_cg"), d="grm_d", a=("ceil_y1 - tray_t", "y_bf"), allow=[IN_C2CASS]),
    dict(code="C1-CEIL", comp="CEIL", name="DRAW WIRE - CEILING CASSETTE", kind=B,
         x=("ceil_x - dw_h", "ceil_x + dw_h"), y=("ceil_y0 + tray_t", "ceil_y1 - tray_t"), z=("z_cg - dw_h", "z_cg + dw_h"),
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
