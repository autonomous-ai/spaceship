"""Spaceship (FocusPod v2) pod skeleton P04: native, parameter-driven.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py
        [--arg close_previous=1] [--arg save=1] [--arg export=1] [--arg close=1]

One Fusion design, components per v2/00-Control/assembly-tree.md (POD with
BASE, WALL, FRONT > DOOR AND GLAZING, CEILING, LINING, AIR, ELECTRICAL,
INTERIOR). Every panel, lining, band and floor is an envelope body in its own
component: a fully constrained rectangle on an XY plane offset by a
parameter, extruded by a parameter. The front decor blocks and the glass are
faceted bodies measured from the v1 STEP (V1-FRONT-FACETS.md). Coordinates
follow conventions.md section 4: origin on the room floor at the pod centre,
+X right (seen from outside facing the door), +Y back, +Z up.

Overlaps made on purpose are listed in EXPECTED with the reason; any other
clash over 1 mm3 fails the run. P01 (stage A, box placeholders), P02
(stage B) and P03 (pass C) are superseded and live only in git history
(BUILD-RECORD.md). Every user parameter is a favorite, so a part design can
derive them from the saved skeleton (they arrive as <name>_Ref) and follow it
(tools/fusion/README.md, "Linking a part to the skeleton").

Parts are linked to the cloud file 100000_P04_POD-SKELETON_CAD. To change a
value, edit PARAMS here and run skeleton_update.py, which saves a new version
of that same file. This build makes a NEW file and would cut every link: use
it only for a new revision of the shape.
"""

import time
import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REV = "P04"     # pass D: DR on the band, floor out to the band, back frames to the roof, faceted front band
DOC_NAME = "100000_%s_POD-SKELETON_CAD" % REV
CLOUD_FOLDER = "FocusPod v2"
F3D_REL = "v2/01-CAD-Native/skeleton/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/skeleton/100000_%s_POD-SKELETON_STEP.step" % REV
CSV_REL = "v2/01-CAD-Native/skeleton/100000_%s_POD-SKELETON-PARAMETERS.csv" % REV

# name, expression, unit, status, source
PARAMS = [
    ("pod_w", "2500 mm", "mm", "decided", "D-01; conventions s4 (X = +-1250)"),
    ("pod_d", "1700 mm", "mm", "decided", "D-01; conventions s4 (Y = +-850)"),
    ("pod_h", "2400 mm", "mm", "decided", "D-21 (room floor to roof skin top)"),
    ("glide_h", "10 mm", "mm", "assumption", "layout study inputs.py glide_h"),
    ("band_h", "100 mm", "mm", "source", "layout study B1 list B-BAND 100x40; inputs.py base_h"),
    ("band_t", "40 mm", "mm", "source", "layout study B1 list B-BAND 100x40"),
    ("skin_t", "3 mm", "mm", "decided", "ACP skin, walls and ceiling (D-16; PM ruling 2026-10-31 on outer_t)"),
    ("bond_t", "3 mm", "mm", "decided", "bond line between the ACP and the frame (PM ruling 2026-10-31 on outer_t)"),
    ("frame_t", "40 mm", "mm", "decided", "aluminium frame tube depth, walls and ceiling (PM ruling 2026-10-31 on outer_t)"),
    ("outer_t", "skin_t + bond_t + frame_t", "mm", "decided", "PM ruling 2026-10-31: ACP 3 + bond line 3 + frame 40, walls and ceiling (was 43)"),
    ("cav_gap", "4 mm", "mm", "decided", "D-16, D-42: the gap between the outer panel and the lining cassette in the wall and ceiling stack"),
    ("cass_t", "34 mm", "mm", "source", "layout study B1 final list L-CASS 34 (tray + 25 gap + felt 9)"),
    ("stack_t", "outer_t + cav_gap + cass_t", "mm", "calculation", "D-16, D-42 stack, walls and ceiling: outer panel + cavity gap + cassette (PM ruling 2026-10-31 on outer_t)"),
    ("wall_depth", "1495 mm", "mm", "decided", "PM ruling pass C: side walls start at the decor back plate (Y -645), as v1 (1496)"),
    ("lin_gap", "4 mm", "mm", "assumption", "PM ruling pass C: gap above the upper side linings so they stay floating (= the 4 mm stack gap)"),
    ("seam_gap", "2.26 mm", "mm", "decided", "PM ruling 2026-10-31 (Mechanical Checker F-001, F-005): the Joints Engineer's 2.26 mm at all nine site seam types, set by a metal stop (1.5 stop washer + 0.76 rivnut head; joints register section 2.8)"),
    ("floor_t", "9 mm", "mm", "decided", "PM ruling 2026-10-31: 9 mm floor panels (was 15, layout study B1 list)"),
    ("thresh_h", "13 mm", "mm", "decided", "PM ruling 2026-10-31: 13 mm, a US-accessible threshold (D-18 had 20); the kick strip keeps its kick_gap above it"),
    ("thresh_d", "60 mm", "mm", "source", "layout study B1 list B-THRESH 1176 x 60 x 20"),
    ("decor_d", "205 mm", "mm", "source", "v1 geometry per the PM ruling on D-39 (as v1; the drawings win): v1 decor-frame drawing frames 191 (left) and 197 (right) deep plus ACP and back plate = the v1 STEP shell, Y -850 to -645 = 205. D-39 and the B1 list say 230-235 (v1 BOM); see BUILD-RECORD-P02"),
    ("dl_w", "278 mm", "mm", "source", "B1 list F-DL 278 (v1 BOM DL)"),
    ("dr_w", "1016 mm", "mm", "source", "B1 list F-DR 1016 (v1 STEP solid 78)"),
    ("dt_w", "1697 mm", "mm", "source", "B1 list F-DT 1697 (v1 BOM DT)"),
    ("dt_h", "280 mm", "mm", "source", "B1 list F-DT 280"),
    ("door_w", "1176 mm", "mm", "decided", "D-46"),
    ("door_h", "2011 mm", "mm", "source", "B1 list F-GLASS-DOOR 2011; v1 STEP solid 238"),
    ("glass_t", "8.76 mm", "mm", "decided", "D-46 (4+4 laminate)"),
    ("glass_y", "699 mm", "mm", "source", "v1 STEP solid 238 centre Y = -699 (layout study data)"),
    ("kick_d", "20 mm", "mm", "assumption", "kick strip envelope depth (D-40 gives the height only)"),
    ("kick_gap", "7 mm", "mm", "source", "FRONT door unit: 7 mm running gap between the threshold and the kick strip for the drop seal (Mechanical Checker F-002 on P03)"),
    # stage B: the faceted front, measured from the v1 STEP (V1-FRONT-FACETS.md), Z shifted
    # -17 mm so v1's top (2417) meets the 2400 datum (D-21); X offsets from the side faces
    ("fr_dz", "17 mm", "mm", "calculation", "v1 front top 2417 (v2 frame) - pod_h 2400"),
    ("door_xl", "289 mm", "mm", "source", "V1-FRONT-FACETS: door left edge X -961 = -1250 + 289"),
    ("door_xbr", "1464 mm", "mm", "source", "V1-FRONT-FACETS: door bottom-right X 214"),
    ("door_xtr", "1182 mm", "mm", "source", "V1-FRONT-FACETS: door top-right X -68"),
    ("door_zb", "122 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: door bottom Z 122"),
    ("door_zt", "2133 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: door top Z 2133"),
    ("glass_gap", "4 mm", "mm", "decided", "PM ruling 2026-10-31 on Mechanical Checker F-014: the fixed glass's free edge runs parallel to the door's slanted edge, 4.0 mm away (FRONT's glass in PR #28 is the reference)"),
    ("fix_xbr", "302 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass bottom-right X 948 = 1250 - 302"),
    ("fix_xk", "501 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass knee X 749 = 1250 - 501"),
    ("fix_zk", "1538 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass knee Z 1538"),
    ("fix_xtr", "1480 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass top-right X 230 = -1250 + 1480"),

    ("fix_zb", "119 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass bottom Z 119"),
    ("fix_zt", "2136 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass top Z 2136"),
    ("dt_zb", "2137 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: DT and DR edge above the glass Z 2137"),
    ("ch_zlo", "2217 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: top chamfer front edge Z 2217 at Y -848"),
    ("ch_yb", "672 mm", "mm", "source", "V1-FRONT-FACETS: top chamfer back edge Y -672"),
    ("dl_x2", "92 mm", "mm", "source", "V1-FRONT-FACETS: DL facet knee X -1158 = -1250 + 92"),
    ("dl_y2", "752 mm", "mm", "source", "V1-FRONT-FACETS: DL facet knee Y -752"),
    ("dl_x3", "271 mm", "mm", "source", "V1-FRONT-FACETS: DL front corner X -979"),
    ("dl_y3", "844 mm", "mm", "source", "V1-FRONT-FACETS: DL front corner Y -844"),
    ("dl_y1", "670 mm", "mm", "source", "V1-FRONT-FACETS: DL outer facet start Y -670"),
    ("dl_zo", "2414 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: DL top at the outer corner Z 2414"),
    ("dt_x2", "281 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet left X -969 = -1250 + 281"),
    ("dt_y2", "767 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet left Y -767"),
    ("dt_y3", "753 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet outer Y -753 at X -1154"),
    ("dr_xc", "198 mm", "mm", "source", "V1-FRONT-FACETS: DR corner facet front X 1052 = 1250 - 198"),
    ("dt_xr", "1699 mm", "mm", "source", "V1-FRONT-FACETS: DT/DR joint at the top, X 449 = -1250 + 1699 (PM ruling pass C)"),
    ("dr_yc", "672 mm", "mm", "source", "V1-FRONT-FACETS: DR corner facet back Y -672"),
    # derived
    ("fix_xbl", "door_xbr + (door_zb - fix_zb) * (door_xbr - door_xtr) / (door_zt - door_zb) + glass_gap * sqrt((door_xbr - door_xtr) * (door_xbr - door_xtr) + (door_zt - door_zb) * (door_zt - door_zb)) / (door_zt - door_zb)", "mm", "calculation", "F-014: fixed glass bottom-left, on the line glass_gap from the door's slanted edge (was v1's 1468)"),
    ("fix_xtl", "door_xbr + (door_zb - fix_zt) * (door_xbr - door_xtr) / (door_zt - door_zb) + glass_gap * sqrt((door_xbr - door_xtr) * (door_xbr - door_xtr) + (door_zt - door_zb) * (door_zt - door_zb)) / (door_zt - door_zb)", "mm", "calculation", "F-014: fixed glass top-left, on the same line (was v1's 1184)"),
    ("wall_z0", "glide_h + band_h", "mm", "calculation", "base band top: glides + band"),
    ("panel_z0", "wall_z0 + seam_gap", "mm", "calculation", "walls stand one seam_gap above the band top (joints register 2.8, IF-01)"),
    ("wall_h", "pod_h - wall_z0", "mm", "calculation", "2290 = layout study v2_model wall_h"),
    ("side_h", "(wall_h - 2 * seam_gap) / 2", "mm", "calculation", "D-23: 2 sheets per side wall; the gap on the band and the horizontal seam (joints register 2.8)"),
    ("side_l", "wall_depth - seam_gap", "mm", "calculation", "side panel length along Y: the seam_gap at the decor's back plate (joints register 2.8, IF-07)"),
    ("back_oh", "pod_h - outer_t - seam_gap - panel_z0", "mm", "calculation", "PM ruling 2026-10-31 (pass D, F-004): the back outer frames run up to the ceiling frame (pod_h - outer_t), less the seam_gap under it, closing the slot at the back top edge"),
    ("back_ph", "(back_oh - seam_gap) / 2", "mm", "calculation", "D-23: 4 sheets on the back, two equal rows with one seam_gap between them (joints register 2.8); the lower back linings match the lower row, as on the side walls"),
    ("half_pw", "(pod_w - 2 * outer_t - 3 * seam_gap) / 2", "mm", "calculation", "SKIN width of each back and ceiling panel: two skins and three seam_gap seams between the side frames (F-001, joints register 2.8)"),
    ("close_gap", "5.5 mm", "mm", "decided", "PM ruling 2026-10-31 (joints register, F-011/F-012): frame gap at the closing seams B1-B2, B3-B4 and C1-C2, which have no hard stop (slotted holes, thicker gasket)"),
    ("half_fw", "(pod_w - 2 * outer_t - 2 * seam_gap - close_gap) / 2", "mm", "calculation", "FRAME width of each back and ceiling panel: the skins overhang their frames by half_pw - half_fw at the closing seam (PM ruling 2026-10-31)"),
    ("inner_w", "pod_w - 2 * stack_t", "mm", "calculation", "inside width between the side linings"),
    # team-to-team bolt rules: one copy, derived by both sides of the joint (PM rulings 2026-10-31)
    ("bolt_edge_inset", "220 mm", "mm", "decided", "PM ruling 2026-10-31: on every bolted edge the end bolts sit this far in from each panel end, the rest evenly spaced"),
    ("spigot_inset", "100 mm", "mm", "decided", "PM ruling 2026-10-31: locating spigots this far in from each panel end (round hole at one end, slot at the other)"),
    ("base_bolt_edge", "bolt_edge_inset", "mm", "decided", "J-BASE-01 wall to band: the edge rule (kept by this name for parts already linked)"),
    ("n_base_bolt", "4", "", "decided", "PM ruling 2026-10-31, J-BASE-01: bolts per panel along the band, evenly spaced"),
    ("base_spigot_inset", "spigot_inset", "mm", "decided", "J-BASE-01: the spigot rule (kept by this name for parts already linked)"),
    ("side_base_pitch", "(side_l - 2 * base_bolt_edge) / (n_base_bolt - 1)", "mm", "calculation", "J-BASE-01 bolt pitch along a side panel"),
    ("back_base_pitch", "(half_pw - 2 * base_bolt_edge) / (n_base_bolt - 1)", "mm", "calculation", "J-BASE-01 bolt pitch along a back panel"),
    ("ceil_bolt_z", "pod_h - outer_t + frame_t / 2", "mm", "decided", "PM ruling 2026-10-31, J-CEIL-01 wall to ceiling: the bolt line on the ceiling frame's centre (Z 2374)"),
    ("n_ceil_side_bolt", "4", "", "assumption", "J-CEIL-01 bolts along each side wall top (WALL's proposal 2026-10-31); count per edge to be confirmed"),
    ("n_ceil_back_bolt", "3", "", "assumption", "J-CEIL-01 bolts along each back panel top (WALL's proposal 2026-10-31); count per edge to be confirmed"),
    ("ceil_side_pitch", "(side_l - 2 * bolt_edge_inset) / (n_ceil_side_bolt - 1)", "mm", "calculation", "J-CEIL-01 bolt pitch along a side wall top"),
    ("ceil_back_pitch", "(half_pw - 2 * bolt_edge_inset) / (n_ceil_back_bolt - 1)", "mm", "calculation", "J-CEIL-01 bolt pitch along a back panel top"),
]

ASSEMBLIES = [  # key, part number, name, Vietnamese name, parent key
    ("BASE", "110000", "BASE", "Đế / sàn", None),
    ("WALL", "210000", "WALL", "Vách", None),
    ("FRONT", "350000", "FRONT", "Mặt trước", None),
    ("GLAZING", "360000", "FRONT - DOOR AND GLAZING", "Cửa và kính", "FRONT"),
    ("CEILING", "410000", "CEILING", "Trần", None),
    ("LINING", "510000", "LINING", "Lớp tiêu âm", None),
    ("AIR", "610000", "AIR", "Thông gió", None),
    ("ELECTRICAL", "710000", "ELECTRICAL", "Điện", None),
    ("INTERIOR", "810000", "INTERIOR", "Nội thất", None),
]

XL, XR = "-pod_w / 2", "pod_w / 2"
YB, YW, YF = "pod_d / 2", "pod_d / 2 - wall_depth", "-pod_d / 2"
XIL, XIR = "-pod_w / 2 + stack_t", "pod_w / 2 - stack_t"    # inner faces: linings span between these
XOL, XOR = "-pod_w / 2 + outer_t", "pod_w / 2 - outer_t"    # side frames' inner faces: back and ceiling
# frames span frame to frame between these, with the side skins over their edges (PM ruling on
# PR #15, build plan rule 4)

# envelope: assembly, code, name, layout-study id, (x0, x1), (y0, y1), (z0, z1)
ENVELOPES = []


def env(asm, code, name, sid, x, y, z):
    ENVELOPES.append((asm, code, name, sid, x, y, z))


YWP = YW + " + seam_gap"       # side panels start one seam_gap behind the decor's back plate (IF-07)
for side, x0, x1, cx0, cx1 in (("L", XL, XL + " + outer_t", XIL + " - cass_t", XIL),
                               ("R", XR + " - outer_t", XR, XIR, XIR + " + cass_t")):
    for row, z0, z1 in ((1, "panel_z0", "panel_z0 + side_h"), (2, "panel_z0 + side_h + seam_gap", "pod_h")):
        cz1 = z1 if row == 1 else "pod_h - outer_t - lin_gap"   # stops under the roof frame, floating
        lo = "LOWER" if row == 1 else "UPPER"
        env("WALL", "%s%d" % (side, row), "WALL - SIDE PANEL - %s - %s" % (lo, "LH" if side == "L" else "RH"),
            "W-SIDE-" + lo[:2], (x0, x1), (YWP, YB), (z0, z1))
        env("LINING", "%s%d-CASS" % (side, row), "LINING - CASSETTE - SIDE %s - %s" % (lo, side),
            "L-CASS-SIDE-" + lo[:2], (cx0, cx1), (YW, YB + " - stack_t + cass_t"), (z0, cz1))   # closes the inside corner
# pass D (PM ruling): the back outer frames run up to the ceiling frame (Z 2357) in two equal
# rows; the back linings stop under the ceiling cassette (Z 2319), the lower ones matching the
# lower row, as on the side walls
# Seams (PM ruling on F-001): one seam_gap between every pair of frames: side frame to back or
# ceiling panel, panel to panel at X 0, row to row, and back wall to ceiling. The linings keep
# pass C's corner and X 0 joints; their rows follow the frame rows.
BL_X = (XOL + " + seam_gap", XOL + " + seam_gap + half_pw")     # B1, B3, C1
BR_X = (XOR + " - seam_gap - half_pw", XOR + " - seam_gap")     # B2, B4, C2
UP0 = "panel_z0 + back_ph + seam_gap"                            # bottom of the upper back row
LTOP = "pod_h - outer_t - lin_gap"     # upper linings float 4 mm under the roof frame (D-57; F-004 ruling)
for code, x0, x1, z0, z1, cz1 in (("B1", -1, "0 mm", "panel_z0", "panel_z0 + back_ph", "panel_z0 + back_ph"),
                                  ("B2", "0 mm", 1, "panel_z0", "panel_z0 + back_ph", "panel_z0 + back_ph"),
                                  ("B3", -1, "0 mm", UP0, "panel_z0 + back_oh", LTOP),
                                  ("B4", "0 mm", 1, UP0, "panel_z0 + back_oh", LTOP)):
    lo = "LOWER" if code in ("B1", "B2") else "UPPER"
    ox0, ox1 = BL_X if x0 == -1 else BR_X
    ix0, ix1 = (XIL if x0 == -1 else x0), (XIR if x1 == 1 else x1)
    env("WALL", code, "WALL - BACK PANEL - %s - %s" % (lo, code), "W-BACK-" + lo[:2],
        (ox0, ox1), (YB + " - outer_t", YB), (z0, z1))
    env("LINING", code + "-CASS", "LINING - CASSETTE - BACK %s - %s" % (lo, code), "L-CASS-BACK-" + lo[:2],
        (ix0, ix1), (YB + " - stack_t", YB + " - stack_t + cass_t"), (z0, cz1))
for code, ox0, ox1, ix0, ix1 in (("C1",) + BL_X + (XIL, "0 mm"), ("C2",) + BR_X + ("0 mm", XIR)):
    env("CEILING", code, "CEILING - HALF PANEL - " + code, "C-HALF",
        (ox0, ox1), (YW, YB), ("pod_h - outer_t", "pod_h"))
    env("LINING", code + "-CASS", "LINING - CASSETTE - CEILING - " + code, "L-CASS-HALF",
        (ix0, ix1), (YW, YB + " - stack_t"), ("pod_h - stack_t", "pod_h - stack_t + cass_t"))
    # pass D (PM ruling): the floor runs out to the base band, closing the 41 mm trench
    # under the wall stack (sides and back); its front edge stays at the walls' start
    fx0, fx1 = (XL + " + band_t", "0 mm") if code == "C1" else ("0 mm", XR + " - band_t")
    env("BASE", "F" + code[1], "BASE - THIN FLOOR PANEL - F" + code[1], "B-FLOOR",
        (fx0, fx1), (YW, YB + " - band_t"), ("0 mm", "floor_t"))
env("BASE", "BAND-BACK", "BASE - BASE BAND - BACK", "B-BAND-BACK",
    (XL + " + band_t", XR + " - band_t"), (YB + " - band_t", YB), ("glide_h", "wall_z0"))
# The side bands and the faceted front band are polygons: see base_bands().
env("BASE", "THRESHOLD", "BASE - DOOR THRESHOLD", "B-THRESH",
    (XL + " + door_xl", XL + " + door_xbr"), ("-glass_y - thresh_d / 2", "-glass_y + thresh_d / 2"),
    ("0 mm", "thresh_h"))
env("GLAZING", "KICK", "FRONT - DOOR KICK STRIP", "D-40",
    (XL + " + door_xl", XL + " + door_xbr"), ("-glass_y - kick_d / 2", "-glass_y + kick_d / 2"),
    ("thresh_h + kick_gap", "door_zb"))

# Stage B bodies have no box expressions; the edit test checks these anchors
# (code, bounding-box index 0..5 = xmin ymin zmin xmax ymax zmax, expression).
FACET_ANCHORS = [
    ("DL", 0, XL), ("DL", 2, "wall_z0"), ("DT", 0, XL), ("DT", 5, "pod_h"),
    ("DR", 3, XR), ("DR", 5, "pod_h"), ("DR", 2, "wall_z0"),
    ("DOOR", 0, XL + " + door_xl"), ("DOOR", 3, XL + " + door_xbr"),
    ("FIXED", 3, XR + " - fix_xbr"), ("FIXED", 5, "fix_zt"),
    ("BAND-L", 0, XL), ("BAND-L", 1, "-dl_y1"), ("BAND-L", 4, YB),
    ("BAND-R", 3, XR), ("BAND-R", 1, "-dr_yc"), ("BAND-R", 4, YB),
    ("BAND-FL", 0, XL), ("BAND-FL", 1, "-dl_y3"), ("BAND-FL", 3, XL + " + dl_w"),
    ("BAND-FL", 2, "glide_h"), ("BAND-FL", 5, "wall_z0"),
    ("BAND-FR", 0, XL + " + fix_xbl"), ("BAND-FR", 1, YF), ("BAND-FR", 3, XR),
]

# Overlaps made on purpose, with the reason. Any other
# clash fails the run.
EXPECTED = [
    # P03's one listed pair (DR 8 mm into BAND-R) is gone: DR now stops at the band top (pass D)
]

MM = 0.1


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def add_params(design):
    for name, expr, unit, status, src in PARAMS:
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        p.isFavorite = True       # so part designs can derive it (it arrives as <name>_Ref)


def new_comp(parent, pn, name, vn):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s" % (name, vn)
    return c


def build_envelope(design, comp, code, name, sid, xr, yr, zr):
    x0, x1, y0, y1, z0, z1 = (ev(design, e) for e in (xr[0], xr[1], yr[0], yr[1], zr[0], zr[1]))
    planes = comp.constructionPlanes
    if abs(z0) < 1e-9:
        plane = comp.xYConstructionPlane
    else:
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, vi(zr[0]))
        plane = planes.add(pin)
        plane.name = "PLANE - %s BOTTOM" % code
    sk = comp.sketches.add(plane)
    sk.name = "OUTLINE - %s" % code
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0 * MM, y0 * MM, 0), adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
    gc = sk.geometricConstraints
    for ln in rect:   # addTwoPointRectangle doesn't always add these
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType())
                   for c in ln.geometricConstraints):
            s0, s1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(s0.y - s1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for p in (ln.startSketchPoint, ln.endSketchPoint):
            if all(p != q for q in pts):
                pts.append(p)

    def near(x, y):
        return min(pts, key=lambda p: (p.geometry.x - x * MM) ** 2 + (p.geometry.y - y * MM) ** 2)
    c00, c10, c01 = near(x0, y0), near(x1, y0), near(x0, y1)
    dims = sk.sketchDimensions
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    tp = adsk.core.Point3D.create((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
    dims.addDistanceDimension(c00, c10, H, tp).parameter.expression = "(%s) - (%s)" % (xr[1], xr[0])
    dims.addDistanceDimension(c00, c01, V, tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    if abs(x0) < 1e-6:
        gc.addVerticalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, H, tp).parameter.expression = "abs(%s)" % xr[0]
    if abs(y0) < 1e-6:
        gc.addHorizontalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, V, tp).parameter.expression = "abs(%s)" % yr[0]
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    ext_in = comp.features.extrudeFeatures.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, vi("(%s) - (%s)" % (zr[1], zr[0])))
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "EXTRUDE - %s ENVELOPE" % code
    body = ext.bodies.item(0)
    body.name = "%s ENVELOPE" % code
    return body


def box(body):
    b = body.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def clash_check(bodies):
    """Pairwise solid intersections; fails on any pair not in EXPECTED."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    allowed = {frozenset(k) for k, _r in EXPECTED}
    codes = list(bodies)
    hits, bad = [], []
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            a, b = codes[i], codes[j]
            ba, bb = box(bodies[a]), box(bodies[b])
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(bodies[a]), tbm.copy(bodies[b])
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((a, b, round(vol)))
                if frozenset((a, b)) not in allowed:
                    bad.append((a, b, round(vol)))
    return hits, bad



# ---------------------------------------------------------------- the faceted front

def _axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis ('x', 'y' or 'z') maps to."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def poly(design, comp, plane, plane_axes, fixed, name, pts):
    """Closed polygon on `plane`, each vertex dimensioned from the sketch origin
    along both plane axes by its parameter expression (fully constrained).
    plane_axes: the two model axes in the plane, e.g. ("x", "z"); fixed: value
    in mm of the third axis on the plane. pts: [(expr_a, expr_b)]."""
    sk = comp.sketches.add(plane)
    sk.name = name
    third = ({"x", "y", "z"} - set(plane_axes)).pop()
    sp = []
    for ea, eb in pts:
        c = {plane_axes[0]: ev(design, ea), plane_axes[1]: ev(design, eb), third: fixed}
        sp.append(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    lines = sk.sketchCurves.sketchLines
    verts, edges = [], []          # the polygon's corners in the order of pts, and its lines
    n = len(sp)
    for i in range(n):
        start = verts[-1] if verts else sp[0]
        end = sp[i + 1] if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(start, end)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    dims, gc = sk.sketchDimensions, sk.geometricConstraints
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    expr_on = {}                   # sketch axis -> index into (ea, eb)
    for k, ax in enumerate(plane_axes):
        expr_on[_axis_of(sk, ax)] = k
    for sa in ("x", "y"):
        # corners joined by an edge parallel to the other axis share this coordinate:
        # constrain that edge and dimension one corner per group (never redundant)
        group = list(range(n))

        def root(i):
            while group[i] != i:
                i = group[i]
            return i
        for i, ln in enumerate(edges):
            a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs((a.x - b.x) if sa == "x" else (a.y - b.y)) < 1e-7:
                (gc.addVertical if sa == "x" else gc.addHorizontal)(ln)
                group[root((i + 1) % n)] = root(i)
        for i in range(n):
            if root(i) != i:
                continue
            ex = pts[i][expr_on[sa]]
            vp = verts[i]
            if abs(ev(design, ex)) < 1e-6:
                (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(vp, sk.originPoint)
            else:
                g = vp.geometry
                tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
                dims.addDistanceDimension(sk.originPoint, vp, H if sa == "x" else V, tp).parameter.expression = \
                    "abs(%s)" % ex
    if not sk.isFullyConstrained:
        info = ["v%d %s%s" % (i, "ok" if vp.isFullyConstrained else "LOOSE",
                              "(%.1f,%.1f)" % (vp.geometry.x * 10, vp.geometry.y * 10)) for i, vp in enumerate(verts)]
        cons = [c.objectType.split("::")[-1] for c in sk.geometricConstraints]
        raise RuntimeError("sketch not fully constrained: %s | dims %d | %s | constraints %s" % (
            name, sk.sketchDimensions.count, " ".join(info), cons))
    return sk


def _normal_sign(sk, axis):
    n = sk.xDirection.crossProduct(sk.yDirection)
    return 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1


def extrude_span(comp, sk, axis, a_expr, b_expr, op, bodies=None, name=""):
    """Extrude the sketch's profiles along a model axis from a to b (a < b)."""
    sign = _normal_sign(sk, axis)
    coll = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        coll.add(pr)
    ei = comp.features.extrudeFeatures.createInput(coll, op)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi("(%s) * (%d)" % (a_expr, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("(%s) - (%s)" % (b_expr, a_expr))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    if bodies:
        ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    return f


def faceted_front(design, asm):
    """DL, DT, DR as measured outlines, extruded and cut by the measured planes;
    door and fixed glass with their true outlines. Returns {code: body}."""
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    out = {}
    back = YF + " + decor_d"
    chamfer = [(YF, "ch_zlo"), ("-ch_yb", "pod_h"), (YF, "pod_h")]

    def comp_for(a, code, name, sid):
        return new_comp(asm[a], "", "%s %s" % (code, name), sid)

    # DL: plan outline (two facets), up to the 45 degree slope shared with DT
    c = comp_for("FRONT", "DL", "FRONT - DECOR BLOCK - LEFT (FACETED, v1 MEASURED)", "F-DL")
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - DL FACETS",
              [(XL, back), (XL, "-dl_y1"), (XL + " + dl_x2", "-dl_y2"), (XL + " + dl_x3", "-dl_y3"),
               (XL + " + dl_w", "-dl_y3"), (XL + " + dl_w", back)])
    f = extrude_span(c, sk, "z", "wall_z0", "pod_h", NEW, name="EXTRUDE - DL PLAN")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "SLOPE - DL TOP",
              [(XL, "dl_zo"), (XL + " + dl_w", "dt_zb"), (XL + " + dl_w", "pod_h"), (XL, "pod_h")])
    extrude_span(c, sk, "y", YF, back, CUT, [b], "CUT - DL TOP SLOPE")
    b.name = "DL FACETED"
    out["DL"] = b

    # DT: plan outline (lower facet), above the slope, front top chamfer
    c = comp_for("FRONT", "DT", "FRONT - DECOR BLOCK - TOP (FACETED, v1 MEASURED)", "F-DT")
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - DT FACETS",
              [(XL, back), (XL, "-dl_y1"), (XL + " + dl_x2 + 4 mm", "-dt_y3"), (XL + " + dt_x2", "-dt_y2"),
               (XL + " + fix_xtr", YF), (XL + " + dt_xr", "-ch_yb"), (XL + " + dt_xr", back)])
    f = extrude_span(c, sk, "z", "dt_zb", "pod_h", NEW, name="EXTRUDE - DT PLAN")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "SLOPE - DT BOTTOM",
              [(XL, "dt_zb"), (XL + " + dl_w", "dt_zb"), (XL, "dl_zo")])
    extrude_span(c, sk, "y", YF, back, CUT, [b], "CUT - DT BOTTOM SLOPE")
    sk = poly(design, c, c.yZConstructionPlane, ("y", "z"), 0, "CHAMFER - DT TOP FRONT", chamfer)
    extrude_span(c, sk, "x", XL, XR, CUT, [b], "CUT - DT TOP CHAMFER")
    b.name = "DT FACETED"
    out["DT"] = b

    # DR: front outline following the fixed glass, corner facet, top chamfer
    c = comp_for("FRONT", "DR", "FRONT - DECOR BLOCK - RIGHT (FACETED, v1 MEASURED)", "F-DR")
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "FRONT - DR OUTLINE",
              [(XR + " - fix_xbr", "fix_zb"), (XR, "fix_zb"), (XR, "pod_h"), (XL + " + fix_xtr", "pod_h"),
               (XL + " + fix_xtr", "dt_zb"), (XR + " - fix_xk", "fix_zk")])
    f = extrude_span(c, sk, "y", YF, back, NEW, name="EXTRUDE - DR OUTLINE")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "CORNER FACET - DR",
              [(XR + " - dr_xc", YF), (XR, "-dr_yc"), (XR, YF)])
    extrude_span(c, sk, "z", "0 mm", "pod_h", CUT, [b], "CUT - DR CORNER FACET")
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "JOINT - DR TO DT (v1 LINE TO X 449)",
              [(XL + " + fix_xtr", YF), (XL + " + dt_xr", "-ch_yb"), (XL + " + dt_xr", back), (XL + " + fix_xtr", back)])
    extrude_span(c, sk, "z", "dt_zb", "pod_h", CUT, [b], "CUT - DR TO DT JOINT")
    sk = poly(design, c, c.yZConstructionPlane, ("y", "z"), 0, "CHAMFER - DR TOP FRONT", chamfer)
    extrude_span(c, sk, "x", XL, XR, CUT, [b], "CUT - DR TOP CHAMFER")
    # pass D (PM ruling): DR stands on the base band like DL; its inner edge keeps the glass line
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - DR BOTTOM ON THE BAND",
              [(XL + " + fix_xtr", YF), (XR, YF), (XR, back), (XL + " + fix_xtr", back)])
    extrude_span(c, sk, "z", "0 mm", "wall_z0", CUT, [b], "CUT - DR BOTTOM AT THE BASE BAND TOP")
    b.name = "DR FACETED"
    out["DR"] = b

    # glass, true outlines
    gy0, gy1 = "-glass_y - glass_t / 2", "-glass_y + glass_t / 2"
    for code, name, sid, pts in (
            ("DOOR", "FRONT - DOOR LEAF GLASS 4+4 (TRAPEZOID, v1 MEASURED)", "F-GLASS-DOOR",
             [(XL + " + door_xl", "door_zb"), (XL + " + door_xbr", "door_zb"),
              (XL + " + door_xtr", "door_zt"), (XL + " + door_xl", "door_zt")]),
            ("FIXED", "FRONT - FIXED GLASS 4+4 (PENTAGON, v1 MEASURED)", "F-GLASS-FIXED",
             [(XL + " + fix_xbl", "fix_zb"), (XR + " - fix_xbr", "fix_zb"), (XR + " - fix_xk", "fix_zk"),
              (XL + " + fix_xtr", "fix_zt"), (XL + " + fix_xtl", "fix_zt")])):
        c = comp_for("GLAZING", code, name, sid)
        sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "OUTLINE - " + code, pts)
        f = extrude_span(c, sk, "y", gy0, gy1, NEW, name="EXTRUDE - %s GLASS" % code)
        f.bodies.item(0).name = code + " GLASS"
        out[code] = f.bodies.item(0)
    return out


# ---------------------------------------------------------------- the base band (pass D)

def _hyp(a, b):
    return "sqrt((%s) * (%s) + (%s) * (%s))" % (a, a, b, b)


# DL's two plan facets (V1-FRONT-FACETS): facet 1 runs a1 in +X and drops b1 in -Y,
# facet 2 runs a2 and drops b2. Their inward unit normals are (b, a) / L. DR's corner
# facet rises dyr in +Y over dxr in +X; its inward normal is (-dyr, dxr) / Lr.
_A1, _B1 = "dl_x2", "(dl_y2 - dl_y1)"
_A2, _B2 = "(dl_x3 - dl_x2)", "(dl_y3 - dl_y2)"
_DXR, _DYR = "dr_xc", "(pod_d / 2 - dr_yc)"
_L1, _L2, _LR = _hyp(_A1, _B1), _hyp(_A2, _B2), _hyp(_DXR, _DYR)
_DOT12 = "((%s) * (%s) + (%s) * (%s)) / ((%s) * (%s))" % (_B1, _B2, _A1, _A2, _L1, _L2)

# Mitre between the left side band and facet 1: the side band's inner face meets
# facet 1's inner face (offset band_t)
_ML = (XL + " + band_t", "-dl_y1 + band_t * (%s - %s) / %s" % (_L1, _B1, _A1))
# Inner corner under DL's facet knee: both facets offset band_t
_IL2 = (XL + " + dl_x2 + band_t * (%s / %s + %s / %s) / (1 + %s)" % (_B1, _L1, _B2, _L2, _DOT12),
        "-dl_y2 + band_t * (%s / %s + %s / %s) / (1 + %s)" % (_A1, _L1, _A2, _L2, _DOT12))
# Facet 2's inner face meets the end at DL's door-side face (X = XL + dl_w). DL's 7 mm
# front edge is shorter than the band is thick, so the band ends on facet 2.
_EL = (XL + " + dl_w", "-dl_y2 + (band_t * %s - %s * (dl_w - dl_x2)) / %s" % (_L2, _B2, _A2))
# Mitre between the right side band and DR's corner facet, and the inner corner
# where the corner facet meets the straight front run
_MR = (XR + " - band_t", "-dr_yc + band_t * (%s - %s) / %s" % (_LR, _DYR, _DXR))
_IR1 = (XR + " - dr_xc - band_t * %s / (%s + %s)" % (_DYR, _LR, _DXR), YF + " + band_t")

# code, name, layout-study id, plan polygon (x, y expressions), why
BANDS = [
    ("BAND-L", "BASE - BASE BAND - SIDE - LH", "B-BAND-SIDE",
     [(XL, "-dl_y1"), (XL, YB), (XL + " + band_t", YB), _ML],
     "side band, from the back corner to DL's outer facet, mitred to the front band"),
    ("BAND-FL", "BASE - BASE BAND - FRONT LEFT (FACETED, UNDER DL)", "B-BAND-FRONT",
     [(XL, "-dl_y1"), (XL + " + dl_x2", "-dl_y2"), (XL + " + dl_x3", "-dl_y3"), (XL + " + dl_w", "-dl_y3"),
      _EL, _IL2, _ML],
     "follows DL's two plan facets (v1's faceted outline), ends at DL's door-side face"),
    ("BAND-FR", "BASE - BASE BAND - FRONT RIGHT (FACETED, UNDER THE FIXED GLASS AND DR)", "B-BAND-FRONT",
     [(XL + " + fix_xbl", YF), (XR + " - dr_xc", YF), (XR, "-dr_yc"), _MR, _IR1, (XL + " + fix_xbl", YF + " + band_t")],
     "v1's straight front run from the fixed glass's left edge, then DR's corner facet"),
    ("BAND-R", "BASE - BASE BAND - SIDE - RH", "B-BAND-SIDE",
     [(XR, "-dr_yc"), (XR, YB), (XR + " - band_t", YB), _MR],
     "side band, from the back corner to DR's corner facet, mitred to the front band"),
]


def base_bands(design, asm):
    """The side and front base bands as plan polygons, extruded from the glides to the
    band top. Across the door opening there is no band: the threshold and the door's
    kick strip carry the dark line (D-18, D-40). Returns {code: body}."""
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    out = {}
    for code, name, sid, pts, _why in BANDS:
        c = new_comp(asm["BASE"], "", "%s %s" % (code, name), sid)
        sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - " + code, pts)
        f = extrude_span(c, sk, "z", "glide_h", "wall_z0", NEW, name="EXTRUDE - %s" % code)
        b = f.bodies.item(0)
        b.name = code + " ENVELOPE"
        out[code] = b
    return out


def export_files(design, root_dir):
    """f3d, STEP (cm, D-13) and the parameter CSV, from the saved version."""
    import csv
    root = design.rootComponent
    em = design.exportManager
    for rel, mk in ((F3D_REL, em.createFusionArchiveExportOptions),
                    (STEP_REL, em.createSTEPExportOptions)):
        ok = False
        for _try in range(10):        # right after a save Fusion may still be uploading
            ok = em.execute(mk("%s/%s" % (root_dir, rel), root))
            if ok:
                break
            adsk.doEvents()
            time.sleep(3)
        print("export %s: %s" % (rel, ok))
        if not ok:
            raise RuntimeError("export failed: " + rel)
    with open("%s/%s" % (root_dir, CSV_REL), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["parameter", "value_mm", "expression", "status", "source"])
        for name, expr, _unit, status, src in PARAMS:
            v = design.userParameters.itemByName(name).value * 10.0
            w.writerow([name, ("%.3f" % v).rstrip("0").rstrip("."), expr, status, src])
    print("export %s: True (%d parameters, all favorites)" % (CSV_REL, len(PARAMS)))


def descriptions():
    """Component descriptions carry no revision: Fusion keeps one description
    per part number across the hub (the STEP still showed P01 under P04), and
    the revision lives in the file name and the title block."""
    out = {"100000": "POD - SPACESHIP (FocusPod v2) skeleton | Pod hoàn chỉnh"}
    for _key, pn, name, vn, _parent in ASSEMBLIES:
        out[pn] = "%s | %s" % (name, vn)
    return out


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("close_previous") == "1":
        for i in range(app.documents.count - 1, -1, -1):
            d = app.documents.item(i)
            if d.objectType != adsk.fusion.FusionDocument.classType():
                continue          # drawings have no design product
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            if dd and not d.isSaved and dd.rootComponent.partNumber == "100000":
                d.close(False)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    add_params(design)
    root = design.rootComponent
    root.partNumber = "100000"
    root.description = descriptions()["100000"]
    asm = {}
    for key, pn, name, vn, parent in ASSEMBLIES:
        asm[key] = new_comp(asm[parent] if parent else root, pn, name, vn)
    bodies = {}
    for a, code, name, sid, x, y, z in ENVELOPES:
        comp = new_comp(asm[a], "", "%s %s" % (code, name), sid)
        bodies[code] = build_envelope(design, comp, code, name, sid, x, y, z)
    bodies.update(faceted_front(design, asm))
    bodies.update(base_bands(design, asm))
    tl = design.timeline
    bad_items = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    print("envelopes %d, timeline %d items, unhealthy %d, loose sketches %d, parameters %d" % (
        len(bodies), tl.count, len(bad_items), len(loose), design.userParameters.count))
    for a, code, name, sid, x, y, z in ENVELOPES:
        b = box(bodies[code])
        print("ENV|%s|%s|%s|%g x %g x %g|%s" % (code, a, sid, round(b[3] - b[0], 2), round(b[4] - b[1], 2),
                                                 round(b[5] - b[2], 2), b))
    for code, _n, sid, _pts, _why in BANDS:
        b = box(bodies[code])
        print("BAND|%s|BASE|%s|%g x %g x %g|%s" % (code, sid, round(b[3] - b[0], 2), round(b[4] - b[1], 2),
                                                round(b[5] - b[2], 2), b))
    hits, bad = clash_check(bodies)
    print("clash pairs %d, expected %d, unexpected %d" % (len(hits), len(hits) - len(bad), len(bad)))
    for a, b, v in hits:
        print("CLASH|%s|%s|%d mm3|%s" % (a, b, v, "UNEXPECTED" if (a, b, v) in bad else "listed"))
    hit_set = {frozenset((a, b)) for a, b, _v in hits}
    print("listed pairs that do not clash:", [k for k, _r in EXPECTED if frozenset(k) not in hit_set])
    rb = box(root)
    print("pod box", rb)
    if bad_items or loose or bad:
        raise RuntimeError("skeleton checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
    if ARGS.get("save") == "1":
        proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
        app.data.activeProject = proj
        folder = proj.rootFolder.dataFolders.itemByName(CLOUD_FOLDER)
        if any(df.name == DOC_NAME for df in folder.dataFiles):
            raise RuntimeError("%s already in %s" % (DOC_NAME, CLOUD_FOLDER))
        print("saved:", doc.saveAs(DOC_NAME, folder, "Spaceship pod skeleton, %s" % REV, ""))
    if ARGS.get("export") == "1":
        export_files(design, ARGS["repo_root"])
    if ARGS.get("close") == "1":          # leave Fusion as we found it (tools/fusion/README.md)
        if not doc.isSaved:
            raise RuntimeError("close=1 needs save=1: the new skeleton would be lost")
        print("closed %s: %s" % (DOC_NAME, doc.close(False)))
