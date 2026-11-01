"""Spaceship (FocusPod v2) WALL: one side wall panel and its lining cassette.

Native, parameter-driven Fusion design, built by script into the ACTIVE
document (open your own document first, for example with the runner's
--doc-new NAME). One run builds one document:

    part=panel     the outer panel assembly: frame, ACP skin, PET fill pieces (straight in the panel, D-123)
    part=cassette  the lining cassette: steel tray, felt, clip zones (HOLD)

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_side_panel.py \
        --doc-new 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD \
        --arg part=panel --arg side=L --arg row=1 --save "build P01" --close

Options (--arg KEY=VALUE):
    part=panel|cassette   which document to build (default panel): the outer panel assembly, or the cassette
    part=frame|skin|tray|felt   one manufactured part alone in its own design, for its part drawing (the fill
                   pieces have no design of their own: they are built in the panel and cut from their DXFs, D-128)
                          (a Fusion drawing view always shows the whole design); same code, same parameters
    side=L|R              left (-X) or right (+X) wall, seen from outside facing the door
    row=1|2               lower (1) or upper (2) panel
    stop_after=N          stop after step N, for step-by-step checks
    rebuild=1             empty the active design first (only a design this script built:
                          its root part number must be the one this run builds)
    skeleton=NAME         skeleton cloud file to derive from (default 100000_P04_POD-SKELETON_CAD)
    post=1                after a clean build, save the document here and run post_wall_doc.py's steps in the
                          same run (export, report, flat DXF, edit test); close with --close --discard
    link=derive|parse     how the skeleton parameters come in (default derive)

Coordinates: the pod system of conventions.md section 4 (origin on the room
floor at the pod centre, +X right, +Y back, +Z up), the same as skeleton P03,
so every part sits where it goes in the pod and the WALL and GA assemblies
insert these designs without a transform.

Parameters: the skeleton is the single source of the pod sizes. The design
links to the saved skeleton (cloud file `skeleton`, default
100000_P04_POD-SKELETON_CAD) with Fusion's Derive: every skeleton parameter
arrives as <name>_Ref and follows each new skeleton version
(Document.updateAllReferences). The wall then adds one alias per skeleton name
it uses (side_h = side_h_Ref, ...) so its own expressions read plainly, and its
own parameters below. Inside Fusion, change an alias (side_h, wall_depth) and
every body follows (edit test, edit_test_wall.py). link=parse instead copies
the values from pod_skeleton.py's PARAMS (offline tests and emergencies only).

Every sketch is fully constrained (the run fails otherwise), every feature,
body and sketch is named by its function, and each part is its own component
with its part number (conventions.md section 6, DECIDED by the PM).
"""

import ast
import math
import glob
import os
import re

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REV = "P01"
PART = ARGS.get("part", "panel")
SIDE = ARGS.get("side", "L").upper()
ROW = int(ARGS.get("row", "1"))
STOP_AFTER = int(ARGS.get("stop_after", "99"))
S = -1 if SIDE == "L" else 1          # sign of X for this side
INSIDE = "+x" if SIDE == "L" else "-x"   # the room side, for the drawings' Front (set_front.py)
SKELETON_REL = "v2/01-CAD-Native/skeleton/pod_skeleton.py"
MM = 0.1                               # Fusion API lengths are cm

WANT = {"panel": ("frame", "skin", "fill"), "frame": ("frame",), "skin": ("skin",),
        "cassette": ("tray", "felt", "clip"), "tray": ("tray",), "felt": ("felt",)}
if PART == "fill":
    raise ValueError("part=fill is gone: D-123 cancels the panels' fill numbers; the fill pieces go straight into "
                     "the panel assembly (part=panel) and are cut from their DXFs (D-128)")
if SIDE not in ("L", "R") or ROW not in (1, 2) or PART not in WANT:
    raise ValueError("side must be L or R, row 1 or 2, part one of %s" % sorted(WANT))
PANEL_SIDE = PART in ("panel", "frame", "skin")

# ---------------------------------------------------------------- part numbers and names

POS = {("L", 1): 1, ("R", 1): 2, ("L", 2): 3, ("R", 2): 4}[(SIDE, ROW)]
CODE = "%s%d" % (SIDE, ROW)            # position code, conventions.md section 4
HAND = "LH" if SIDE == "L" else "RH"
LEVEL = "LOWER" if ROW == 1 else "UPPER"
VN_SIDE = "Vách trái" if SIDE == "L" else "Vách phải"
VN_LEVEL = "dưới" if ROW == 1 else "trên"

# key: (part number, English name, Vietnamese name). Numbers follow conventions.md
# section 6: WALL 21 (assemblies 0001-0999, made parts 1000-7999), LINING 51.
# Status: confirmed (PM ruling in the WALL group, 2026-10-31: numbers per
# conventions section 6, checked against D-28's reserved list).
PARTS = {
    "assy": ("2101%02d" % POS, "WALL - PANEL ASSY - SIDE %s - %s" % (LEVEL, HAND),
             "%s - cụm tấm %s" % (VN_SIDE, VN_LEVEL)),
    "frame": ("2111%02d" % POS, "WALL - PANEL FRAME - SIDE %s - %s" % (LEVEL, HAND),
              "%s - khung %s" % (VN_SIDE, VN_LEVEL)),
    "skin": ("2113%02d" % POS, "WALL - SKIN - SIDE %s - %s" % (LEVEL, HAND),
             "%s - tấm ốp alu %s" % (VN_SIDE, VN_LEVEL)),
    "cass": ("5101%02d" % POS, "LINING - CASSETTE - SIDE %s - %s" % (LEVEL, HAND),
             "Cassette lót %s %s (khay thép + tấm tiêu âm)" % (VN_SIDE.lower(), VN_LEVEL)),
    "tray": ("5111%02d" % POS, "LINING - TRAY - SIDE %s - %s" % (LEVEL, HAND),
             "Khay thép lót %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "felt": ("5113%02d" % POS, "LINING - FELT - SIDE %s - %s" % (LEVEL, HAND),
             "Tấm tiêu âm %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "clip": ("NO-PN-HOLD-H03", "HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED)",
             "Vùng dành cho kẹp treo cassette (HOLD)"),
}
# joint hardware the panel carries from the factory, numbered by the joints register (V2-ENG-JNT-01, table 2.1;
# PROPOSED numbers, D-63): one component each in the panel assembly
HW_PARTS = {
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2", "Tán rút M6 thép mạ kẽm"),
    "stopw": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm"),
    "spigot": ("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8"),
    # the mitre plates (D-131; joints register H-40 to H-42, made hardware numbered by the Joints Engineer)
    "plate28": ("831007", "HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL",
                "Tấm đệm góc vát 20 × 40 - 45° - thép 2.0"),
    "plate45": ("831008", "HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL",
                "Tấm đệm góc vát 20 × 40 với 40 × 40 - thép 2.0"),
    "plate57": ("831009", "HARDWARE - MITRE PLATE - 40 X 40 - 45 DEG - 2.0 STEEL",
                "Tấm đệm góc vát 40 × 40 - 45° - thép 2.0"),
}
# the cassette ledge (the Lead's ruling of 2026-11-01: a wall cassette's weight sits on a ledge, not on clip shear,
# since no clip maker publishes shear; the clips only hold): a galvanized steel angle riveted to the lower frame's
# bottom rail, a pad on its leg under the tray's bottom return; the upper cassette stands on the lower one through a
# strip in the 2.26 joint (on the cassette's list). Numbers from Control, the pad, strip and rivet picked by Joints;
# until a number is posted the build stops, except a dry run, which labels the part DRY.
LEDGE_PN = {"ledge": None, "pad": None, "rivet": None}
LEDGE_NAMES = {
    "ledge": ("WALL - CASSETTE LEDGE - SIDE LOWER - COMMON", "Vách - gờ đỡ cassette dưới (dùng chung)"),
    "pad": ("SEALS - CASSETTE LEDGE PAD - 18 X 2.26 - HOLD", "Đệm gờ đỡ cassette (chờ)"),
    "rivet": ("HARDWARE - BLIND RIVET - Ø4 - STEEL ZINC - HOLD", "Đinh tán rút Ø4 thép mạ kẽm (chờ)"),
}
if ROW == 1:
    for _k, (_n, _v) in LEDGE_NAMES.items():
        _pn = LEDGE_PN[_k] or ("DRY-LEDGE-%s" % _k.upper() if ARGS.get("dry") == "1" else "NO-PN-LEDGE-%s" % _k.upper())
        if not LEDGE_PN[_k]:                  # unnumbered: marked HOLD, and build_ledge builds it only in a dry run
            _n = "HOLD - %s (NO NUMBER YET)" % _n
        (PARTS if _k == "ledge" else HW_PARTS)[_k] = (_pn, _n, _v)
PARTS.update(HW_PARTS)
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005",
            "350011", "830001", "830005"}          # D-28
for _k, (_pn, _n, _v) in PARTS.items():
    if _pn in RESERVED:
        raise RuntimeError("reserved part number %s (D-28)" % _pn)
ROOT_KEY = {"panel": "assy", "cassette": "cass"}.get(PART, PART)
DOC_NAME = "%s_%s_%s_CAD" % (PARTS[ROOT_KEY][0], REV, re.sub(r"[^A-Z0-9]+", "-", PARTS[ROOT_KEY][1]).strip("-"))

# ---------------------------------------------------------------- wall parameters

# name, expression, unit, status, source. A parameter may use any skeleton
# parameter and the ones above it. Statuses per conventions.md section 9.
WALL_PARAMS = [
    # outer panel
    ("tube_w", "20 mm", "mm", "confirmed",
     "D-34, D-54, kept by D-131 (the same outside sections in welded, galvanized steel box tube): 20 x 40; the 20 mm "
     "face carries the skin, so the 40 mm runs through the wall (outer_t = ACP 3 + frame 40)"),
    ("tube_d", "outer_t - skin_t - bond_t", "mm", "calculation", "frame depth = outer panel 46 - skin 3 - bond 3 = 40 (D-34)"),
    ("tube_t", "1.2 mm", "mm", "source",
     "the Joints Engineer's gauges for D-131 (PM ruling, 2026-11-01 05:29): 1.2 for a side panel's rails and front "
     "stile, for margin against thin tube and weak welds (corner lift 74% on L1 and L2)"),
    ("corner_t", "1.0 mm", "mm", "source",
     "the same: the 40 x 40 members (the back stile, and the upper panel's top member) stay 1.0"),
    ("stud_t", "0.8 mm", "mm", "source", "the same: the studs at 0.8 (no rivnut, only the skin's bond line)"),
    ("plate_t", "2 mm", "mm", "source",
     "the Joints Engineer's corner detail (2026-11-01 05:05): a 2 mm steel plate welded into each mitre, the members "
     "cut back so it fits, centred on the old mitre line"),
    ("stile_pitch_max", "300 mm", "mm", "confirmed",
     "PM ruling 2026-11-01 (D-131 sample): the ACP flexes 2 mm or less under a 100 N push at a bay's centre, edges "
     "simply supported (make_acp_spans.py), so members about 300 apart; it was 400 (D-16, D-34)"),
    ("pnl_len", "wall_depth - seam_gap", "mm", "calculation",
     "D-49 depth 1495 less the 2.26 gap at the decor back plate (PM ruling on F-008): 1492.74"),
    ("pnl_h", "side_h" if ROW == 1 else "pod_h - (panel_z0 + side_h + seam_gap)", "mm", "calculation",
     "lower: skeleton side_h (2 sheets per side wall, D-23); upper: from one seam gap above the lower row to the roof "
     "datum pod_h, as the skeleton's envelope (equal to side_h at P04 values)"),
    ("skin_ret", "outer_t - skin_t", "mm", "assumption",
     "back return of the side skin: covers the frame's back end at the corner, where the side skin covers the back "
     "panel's edge (D-55; sample drawing D04). V-groove and fold per the ACP maker (HOLD H16)"),
    ("skin_fold_r", "2 mm", "mm", "source",
     "outside radius of the back return's V-grooved fold: over 2 at the fold (the panel maker's guide 01/2021/HDTC-VD "
     "4.5 and figure 4.5: under 2 cracks the face and voids the warranty); modelled (the Lead's ruling, 2026-11-01)"),
    ("skin_setback", "0 mm", "mm", "assumption",
     "skin edge set back from the frame's top and bottom edges: 0, so the outside reveal equals the 2.26 seam gap "
     "(D-23: crisp, aligned reveals; joints register 2.8 leaves the setback to the WALL drawing)"),
    ("frm_len", "pnl_len - skin_t - bond_t", "mm", "calculation",
     "the frame stops one bond line (bond_t) inside the skin's back return, which is bonded to it as the main face is "
     "(the Lead's ruling, 2026-11-01: every skin face that meets a frame is bonded at bond_t, no zero fits)"),
    ("frm_h", "pnl_h", "mm", "assumption",
     "the frame fills the skeleton envelope height; seam and base gasket gaps are set by the joint register (HOLD)"),
    ("corner_w", "40 mm", "mm", "confirmed",
     "the side panel's back member is 40 x 40 x 1.2 (PM ruling on the joints register, item 3, 2026-10-31; "
     "register F2, FR-06): the back corner joint needs a 37+ mm overlap for the rivnut and the bolt"),
    ("stile_n_mid", "5", "", "calculation",
     "D-131 sample (PM 2026-11-01): 5 studs, placed clear of the bolts (stud_c1 to stud_c5): 4 even studs about 300 "
     "apart pass the skin's 2 mm limit but stand 14 and 24 mm from two bolts, under R-J14's 30"),
    ("top_h", "tube_w" if ROW == 1 else "corner_w", "mm", "confirmed" if ROW == 2 else "calculation",
     "top member height: 20 on a lower panel; 40 x 40 on an upper panel, where the ceiling bolts in (PM ruling "
     "R-J3, joints register FR-06)"),
    ("stile_len", "frm_h - tube_w - top_h", "mm", "calculation", "stiles fit between the full-length rails (butt joints)"),
    ("ceil_bolt_dz", "pod_h - ceil_bolt_z", "mm", "calculation",
     "J-CEIL-01 side bolts on the ceiling frame tube's centre: the skeleton's ceil_bolt_z, Z 2374 on P04 (joints "
     "register R-J15, FR-07)"),
    ("fill_t", "tube_d", "mm", "calculation", "40 mm PET fill fills the frame depth (D-34; layout study 40 mm)"),
    # site joints, joints register V2-ENG-JNT-01 P01 (ce1f415): M6 x 20 ISO 4762 captive bolts into Sherex
    # CAL2-610-4.2 rivnuts (D-163: the knurled round body in a round Ø10.00 hole; steel since D-131; the CAH2 and
    # CAH3 before), bolts and corner members DECIDED by the PM
    # (2026-10-31); positions PROPOSED there
    ("bolt_d", "7 mm", "mm", "confirmed", "PM ruling on F-009: bolt holes 7.0 (0.51 float), position tolerance "
     "0.4 (+-0.2) from the spigot hole, CNC or drill jig (joints register FR-02)"),
    ("access_d", "19 mm", "mm", "calculation",
     "register FR-03: passes the 18 mm head washer (ISO 7093-1, R-J10), the M6 head and the 5 mm key; holds the "
     "grommet retainer (H-02)"),
    ("bolt_line_y", "pod_d / 2 - skin_t - bond_t - tube_d / 2", "mm", "confirmed",
     "J-WALL-02 bolt line on the back panel's tube centre, Y 824 (joints register R-J15, FR-07)"),
    ("rivnut_d", "10 mm", "mm", "confirmed",
     "D-163 (the Lead's ruling, 2026-11-01): Sherex CAL2-610-4.2 in a round drilled hole Ø10.00 +0.10/0, inside the maker's 10.00 +0.15/-0.0 (Sherex drawing CAL2-610-4.2 rev B, note 2) so the bolt-hole stack ST-03 stays positive; T06's spin-out test confirms it"),
    ("spigot_d", "8.5 mm", "mm", "assumption", "register FR-05: hole for the 8 mm locating spigot H-05"),
    ("spigot_slot", "16 mm", "mm", "confirmed",
     "D-167 (the Lead's ruling, 2026-11-01): the seam gasket is 4.78 (PORON 4701-40's standard), so the side panels' "
     "back-end slot for the second spigot grows from 8.5 x 14 to 8.5 x 16, ±4 of travel, the panel held 3.4 out"),
    ("spigot_edge", "spigot_inset", "mm", "calculation",
     "the skeleton's spigot_inset: spigots 100 from each end of the edge (PM ruling 2026-10-31, R-J13)"),
    ("bolt_edge", "bolt_edge_inset", "mm", "calculation",
     "the skeleton's bolt_edge_inset: end bolts 220 in from the panel's ends, evenly spaced, every bolt 30 or more "
     "from any stile (PM ruling 2026-10-31, R-J14)"),
    ("n_side_jnt", "3", "", "source", "register J-WALL-02, J-FRONT-01: 3 bolts up each side panel"),
    ("side_jnt_pitch", "(pnl_h - 2 * bolt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "equal pitch of the 3 bolts up the corner and decor joints"),
    ("pocket_w", "60 mm", "mm", "assumption", "register FR-10: fill left out 60 x 60 next to each bolt for the key"),
    ("corner_z0", "panel_z0" if ROW == 1 else "panel_z0 + back_ph + seam_gap", "mm", "calculation",
     "bottom of the back panel row this side panel meets at the corner (B1/B2 or B3/B4, skeleton P04)"),
    ("corner_bolt_pitch", "(back_ph - 2 * bolt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "J-WALL-02 bolts run along the back panel's edge: 220, 559.31, 898.61 on its 1118.61 (joints register 2.9)"),
    ("n_len_bolt", "n_base_bolt", "", "calculation",
     "the skeleton's n_base_bolt (4): the same count on J-WALL-01 and the J-CEIL-01 side edges (register 2.9)"),
    ("ceil_bolt_pitch", "(wall_depth - 2 * bolt_edge) / (n_len_bolt - 1)", "mm", "calculation",
     "J-CEIL-01 side edge: 4 bolts along the ceiling's 1495 from Y -645 (its front edge), 220 rule, pitch 351.67 on "
     "P04; CEILING drills the same (PM ruling 2026-10-31 16:55; joints register 2.9)"),
    ("len_bolt_pitch", "(pnl_len - 2 * bolt_edge) / (n_len_bolt - 1)", "mm", "calculation",
     "even pitch of the bolts along the panel"),
    # the studs' centres from the frame's front end, each set from the bolts it stands between, so every bolt stays 30
    # or more clear of every stud (R-J14: WALL moves a stile, never a bolt) and no bay is over the skin's 2 mm
    # limit (stile_pitch_max); the rule holds while the bolts move with the panel length (edit test)
    ("stud_c1", "bolt_edge + 50 mm", "mm", "calculation", "50 past the 1st bolt: its face 40 clear of it (R-J14)"),
    ("stud_c2", "bolt_edge + len_bolt_pitch - 50 mm", "mm", "calculation", "50 before the 2nd bolt (R-J14)"),
    ("stud_c3", "bolt_edge + 1.5 * len_bolt_pitch", "mm", "calculation", "midway between the 2nd and 3rd bolts"),
    ("stud_c4", "bolt_edge + 2 * len_bolt_pitch + 50 mm", "mm", "calculation", "50 past the 3rd bolt (R-J14)"),
    ("stud_c5", "bolt_edge + 3 * len_bolt_pitch - 50 mm", "mm", "calculation", "50 before the 4th bolt (R-J14)"),
    # lining cassette
    ("felt_t", "9 mm", "mm", "source", "plan VT03-PET 9 mm PET felt; HW-SEL A3; D-31 (the factory's felt)"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm"),
    ("tray_h", "cass_t", "mm", "confirmed",
     "PM ruling 2026-10-31 (WALL group, option 1): the wall cassettes use the ceiling's tray, returns the full "
     "cassette depth (34) turned in as lips that hold the felt, no ribs; settles H09 for the walls"),
    ("lip_w", "12 mm", "mm", "confirmed", "PM ruling 2026-10-31 (WALL group, option 1): 12 mm lips hold the felt edge"),
    ("bend_r", "tray_t", "mm", "assumption",
     "inside bend radius 1 x t for 0.5 mm DX51D (the sheet metal rule's bend radius is its Thickness); the factory's "
     "tooling sets it (guideline 9)"),
    ("felt_c", "1 mm", "mm", "assumption", "felt edge clearance inside the returns, as the ceiling cassette"),
    ("gap_h", "tray_h - felt_t - 2 * tray_t", "mm", "calculation",
     "air gap between the tray base and the felt (24): the acoustic gap (D-17) and the cable path (D-26)"),
    ("lin_front_dy", "5 mm" if SIDE == "R" else "0 mm", "mm", "confirmed",
     "Lead ruling 2026-11-01 (F-308, F-309): the right-hand cassettes start at Y -640, 1 mm off DR's inner panel "
     "(its room face at Y -641.14, FRONT's measurement; the panel stays), and the service steps unclip R1's and "
     "R2's cassettes before that panel comes off; the left-hand ones start at the decor back plate (Y -645)"
     if SIDE == "R" else "the left-hand cassettes start at the decor back plate (D-57); the right-hand ones 5 mm "
     "behind it, clear of DR's inner panel (Lead ruling 2026-11-01)"),
    ("cass_len", "wall_depth - stack_t + cass_t - lin_front_dy", "mm", "calculation",
     "from the cassette's front end (lin_front_dy behind the decor back plate) to past the back cassette's face, "
     "closing the inside corner (D-57): 1445 on the left, 1440 on the right"),
    ("cass_h", "side_h" if ROW == 1 else "pod_h - outer_t - lin_gap - (panel_z0 + side_h + seam_gap)", "mm",
     "calculation",
     "lower: the panel height; upper: stops lin_gap under the roof frame so it floats (D-57)"),
    ("clip_zone_h", "60 mm", "mm", "assumption", "height of each reserved clip zone (H03: no clip named)"),
    ("clip_zone_dz", "100 mm", "mm", "assumption", "clip zone centre from the cassette's top and bottom edges (H03)"),
    # joint hardware bodies (register 2.1 sizes): the rivnut as its installed envelope, threads at 6 mm
    ("stopw_od", "20 mm", "mm", "source", "joints register H-08: stop washer Ø10.5 x Ø20 x 1.5 (PROPOSED part)"),
    ("stopw_id", "10.5 mm", "mm", "source", "joints register H-08"),
    ("stopw_t", "1.5 mm", "mm", "source", "joints register H-08: rivnut head 0.76 + washer 1.5 = the 2.26 stop (R-J5)"),
    ("rivnut_head_d", "12.95 mm", "mm", "source", "Sherex CAL2-610-4.2 rev B: flange Ø12.45 to 12.95, the largest "
                                                 "modelled (D-163)"),
    ("rivnut_head_t", "0.76 mm", "mm", "source", "Sherex CAL2-610-4.2 rev B: flange 0.68 to 0.84, its middle; with "
                                                "the 1.5 stop washer the 2.26 stop (R-J5), as before (D-163)"),
    ("rivnut_body_d", "9.91 mm", "mm", "source", "Sherex CAL2-610-4.2 rev B: knurled body Ø9.91 max (D-163)"),
    ("rivnut_len", "9.65 mm", "mm", "source",
     "Sherex CAL2-610-4.2 rev B, note 3: installed length 9.65 max under the flange (14.35 to 15.11 before "
     "setting); the bulge inside the tube is not modelled (D-163)"),
    ("m6_d", "6 mm", "mm", "calculation", "M6 threads shown at their 6 mm major diameter (no modelled thread)"),
    ("spigot_pin_d", "8 mm", "mm", "source", "joints register H-05: Ø8 stainless pin; the part itself is Joints' "
                                             "831001 STEP, placed as it is (F-189)"),
    ("spigot_proud", "8 mm", "mm", "source", "joints register H-05 and Joints' README: the pin's top 8.00 above the "
                                             "tube face (Z 7.24 above its origin on the rivnut head)"),
]

# ELECTRICAL's interface features in WALL parts (ELECTRICAL P01, electrical_model.py, PR #64, and the PM's
# messages of 2026-10-31 20:30-20:45 UTC): the power unit's cut-out in B2-CASS, cable slots and bushing holes in
# the cassette returns, felt-only holes, and the inlet holes and fill cut-outs in panel B2. Same names as
# ELECTRICAL's model with an el_ prefix, same expressions, so a skeleton edit moves them as it moves ELECTRICAL's.
_EL = "ELECTRICAL P01 (electrical_model.py, PR #64)"
EL_PARAMS = [
    ("el_trunk_z", "1100 mm", "mm", "assumption", _EL + " trunk_z: the cable trunk height in B2-CASS and R1-CASS, "
                                                         "above the ledge (about Z 1000), below the R1/R2 joint"),
    ("el_col_d", "360 mm", "mm", "confirmed", _EL + " col_d; D-61: the air column is 217 x 360"),
    ("el_col_skin", "1 mm", "mm", "assumption", _EL + " col_skin: the column casing in front of its fill"),
    ("el_ch_w", "24 mm", "mm", "assumption", _EL + " ch_w: the 24 x 24 cable chase in the column's fill"),
    ("el_y_kit", "((pod_d / 2 - wall_depth + el_col_d) + (pod_d / 2 - stack_t)) / 2", "mm", "calculation",
     _EL + " y_kit: the voice kit drop, halfway between the column's back face and the back lining (Y 240.5, D-70)"),
    ("el_y_cx", "pod_d / 2 - wall_depth + el_col_d - el_col_skin - el_ch_w / 2", "mm", "calculation",
     _EL + " y_cx: where the trunk leaves R1-CASS's felt into the column chase (Y -298)"),
    ("el_grm_d", "19.1 mm", "mm", "source", _EL + " grm_d: the hole for the Heyco 2836 SB 750-625 bushing (maker "
                                                  "page); PM 2026-10-31: 19.1, not 20"),
    ("el_grm_s", "12 mm", "mm", "assumption", _EL + " grm_s: felt-only hole for a single cable"),
    ("el_fs_y0", "2 mm", "mm", "assumption", _EL + " FS-CNR: the corner felt slot starts 2 mm behind the back "
                                                   "lining's face plane"),
    ("el_fs_y1", "20 mm", "mm", "assumption", _EL + " FS-CNR: and ends 20 mm behind it, clear of R1-CASS's back lip"),
    ("el_fs_dz", "60 mm", "mm", "assumption", _EL + " FS-CNR: half the corner felt slot's height (trunk_z +- 60)"),
    ("el_kit_d", "60 mm", "mm", "assumption", _EL + " kit_d: felt access hole for the kit drop, with a felt plug"),
    ("el_kit_dz", "80 mm", "mm", "assumption", _EL + " FA-KIT: the access hole's centre 80 above the trunk"),
    ("el_call_dy", "450 mm", "mm", "assumption", _EL + " call_y = y_kit - 450: the front end of a 900 mm bar"),
    ("el_call_y", "el_y_kit - el_call_dy", "mm", "calculation", _EL + " call_y: the call light feed (Y -209.5)"),
    ("el_call_z", "1450 mm", "mm", "assumption", _EL + " call_z: call light feed height, above the screen zone"),
    ("el_shelf_z", "2250 mm", "mm", "assumption", _EL + " shelf_z: the light shelf height (CEILING sets the shelf)"),
    ("el_shelf_d", "16 mm", "mm", "assumption", _EL + " FX-SHELF: felt hole for the light shelf feed"),
    ("el_pu_x0", "95 mm", "mm", "assumption", _EL + " pu_x0: the power unit's left side, clear of the closing seam "
                                                    "member and its pin-bolt pocket"),
    ("el_pu_w", "296 mm", "mm", "source", "ELECTRICAL's final unit size 296 x 260 x 72 (PM 2026-10-31 20:38 UTC): "
                                          "X 95 to 391, 4.75 clear of B2's first stud"),
    ("el_pu_h", "260 mm", "mm", "source", "ELECTRICAL's final unit size (PM 2026-10-31 20:38 UTC): Z 870 to 1130"),
    ("el_pu_zc", "1000 mm", "mm", "confirmed", _EL + " pu_zc: the socket and LAN at the ledge height (D-70)"),
    ("el_pu_clr", "4 mm", "mm", "assumption", _EL + " pu_clr: the gap round the frame-mounted unit, so the cassette "
                                                    "stays floating (= cav_gap)"),
    ("el_cut_x0", "el_pu_x0 - el_pu_clr", "mm", "calculation", "B2-CASS cut-out: its left return's inner face (X 91)"),
    ("el_cut_x1", "el_pu_x0 + el_pu_w + el_pu_clr", "mm", "calculation",
     _EL + " cut_x1: B2-CASS cut-out: its right return's inner face (X 395)"),
    ("el_cut_z0", "el_pu_zc - el_pu_h / 2 - el_pu_clr", "mm", "calculation",
     "B2-CASS cut-out: its bottom return's inner face (Z 866)"),
    ("el_cut_z1", "el_pu_zc + el_pu_h / 2 + el_pu_clr", "mm", "calculation",
     _EL + " cut_z1: B2-CASS cut-out: its top return's inner face (Z 1134)"),
    ("el_lt_x", "346 mm", "mm", "source", "ELECTRICAL via the PM 2026-10-31 20:38 UTC: the light feed moves from "
                                          "X 355 to X 346"),
    ("el_y_bg", "pod_d / 2 - stack_t + tray_t + felt_t + gap_h / 2", "mm", "calculation",
     _EL + " y_bg: the middle of the back lining's cable gap (Y 787.5)"),
    ("el_slot_h", "10 mm", "mm", "assumption", _EL + " slot_h: half the 20 x 70 slot in the cut-out's right return"),
    ("el_slot_l", "70 mm", "mm", "assumption", _EL + " slot_l: the slot's length along Z, past both lead exits"),
    ("el_lx_z2", "el_trunk_z - 15 mm", "mm", "calculation", _EL + " lx_z2: the unit's upper lead exit (Z 1085)"),
    ("el_lx_z1", "el_lx_z2 - 40 mm", "mm", "calculation", _EL + " lx_z1: the unit's lower lead exit (Z 1045)"),
    ("el_cs_h", "5.5 mm", "mm", "calculation", _EL + " cs_h: half the corner slot in B2-CASS's end return (Y 776-787)"),
    ("el_cs_dz", "40 mm", "mm", "assumption", _EL + " S-CNR: half the corner slot's length (trunk_z +- 40)"),
    ("el_y_xc", "pod_d / 2 - stack_t + tray_t + felt_t + 6 mm", "mm", "calculation",
     _EL + " y_xc: the corner crossing (Y 781.5), clear of R1-CASS's back lip"),
    ("el_ceil_x", "(pod_w - 2 * stack_t) / 4", "mm", "calculation",
     _EL + " ceil_x = inner_w / 4: the ceiling cassette's cable holes (X 583, CEILING P01)"),
    ("el_z_cg", "pod_h - stack_t + tray_t + felt_t + gap_h / 2", "mm", "calculation",
     _EL + " z_cg: the middle of the ceiling lining's cable gap (Z 2337.5)"),
    ("el_ceil_z", "pod_h - outer_t - lin_gap - lip_w - 2 mm - el_grm_s / 2", "mm", "source",
     "ELECTRICAL via the PM 2026-10-31 21:10 UTC: the ceiling route's crossing into B4-CASS is a felt-only 12 hole at "
     "Z 2330, its top edge 2 below the 12 lip (no cable hole through a lip, PM rule)"),
    ("el_inlet_x", "120 mm", "mm", "assumption", _EL + " inlet_x: the inlet column, just clear of the closing seam"),
    ("el_inlet_z", "313 mm", "mm", "source", _EL + " inlet_z: v1's 'Power Jack' centre Z 298.3 + 15"),
    ("el_lan_z", "375 mm", "mm", "source", _EL + " lan_z: v1's 'Jack LAN' centre Z 360 + 15"),
    ("el_inlet_d", "24 mm", "mm", "source", _EL + " inlet_d: powerCON TRUE1 TOP cut-out 23.8, etherCON NE8FDP 24"),
    ("el_sl_x", "el_inlet_x + 30 mm", "mm", "calculation", _EL + " sl_x: the mains and LAN sleeve's centre (X 150)"),
    ("el_sl_w", "20 mm", "mm", "assumption", _EL + " SLEEVE: the sleeve's 20 x 20 envelope"),
]
# what each design needs, by position and kind (the el_ names these refer to come with them)
EL_USE = {
    ("R1", "cass"): ("el_fs_y0", "el_fs_y1", "el_fs_dz", "el_trunk_z", "el_kit_d", "el_kit_dz", "el_y_kit",
                     "el_grm_d", "el_y_cx"),
    ("R2", "cass"): ("el_grm_s", "el_call_y", "el_call_z", "el_shelf_z"),
    # a plain cut-out (no returns, so no slot or bushing in them): PROPOSED by WALL 2026-10-31 21:08 UTC
    ("B2", "cass"): ("el_cut_x0", "el_cut_x1", "el_cut_z0", "el_cut_z1", "el_lt_x", "el_grm_d", "el_y_bg",
                     "el_cs_h", "el_cs_dz", "el_y_xc", "el_trunk_z"),
    ("B2", "panel"): ("el_cut_x0", "el_cut_z0", "el_cut_z1", "el_inlet_x", "el_inlet_z", "el_lan_z", "el_inlet_d",
                      "el_sl_x", "el_sl_w"),
    ("B4", "cass"): ("el_lt_x", "el_grm_d", "el_y_bg", "el_shelf_z", "el_shelf_d", "el_ceil_x", "el_ceil_z", "el_grm_s"),
}


def el_params(code, kind):
    """The ELECTRICAL parameters one design needs, with every el_ name they refer to, in table order."""
    table = {p[0]: p for p in EL_PARAMS}
    want = set(EL_USE.get((code, kind), ()))
    todo = list(want)
    while todo:
        for ref in re.findall(r"\bel_\w+", table[todo.pop()][1]):
            if ref not in want:
                want.add(ref)
                todo.append(ref)
    return [p for p in EL_PARAMS if p[0] in want]


EL_KIND = "frame" if PART == "frame" else ("panel" if PANEL_SIDE else "cass")    # a frame has none of them
WALL_PARAMS = WALL_PARAMS + el_params(CODE, EL_KIND)
# the cassette ledge (the Lead's ruling of 2026-11-01, WALL's sizes accepted the same day): lower panels only
_LG = "the Lead's ledge ruling, 2026-11-01 (WALL's sizes, accepted)"
LEDGE_PARAMS = [
    ("ledge_t", "1 mm", "mm", "assumption", _LG + ": galvanized steel sheet 1.0, DX51D+Z (EN 10346), Z100"),
    ("ledge_r", "ledge_t", "mm", "assumption", "inside bend radius 1 x t, as the trays (the sheet metal rule's)"),
    ("ledge_out", "28 mm", "mm", "assumption", _LG + ": the leg from the rail's room face, under the tray's 34 deep "
                                                    "bottom return; its tip 10 short of the lining's room face, out of sight"),
    ("ledge_up", "tube_w - 2 mm", "mm", "assumption", _LG + ": the upright reaches 2 under the bottom rail's top face"),
    ("ledge_pad_t", "2.31 mm", "mm", "calculation",
     "Joints' pick (WALL group, 2026-11-01): Rogers PORON 4701-40, the 320 kg/m3 grade, 2.36 thick (a standard "
     "size), PSA one side, slit 18 wide; the ledge's 7.7 kPa squeezes it about 2%, to about 2.31, so the leg sits "
     "2.31 under the frame's bottom and the cassette's bottom stays level with it (the foam is ±10% thick)"),
    ("ledge_pad_w", "18 mm", "mm", "source", "Joints' pick: the pad slit 18 wide, on the leg's flat past its bend"),
    ("ledge_front_dy", "5 mm", "mm", "confirmed",
     "both sides' ledges start where the right-hand cassettes do (lin_front_dy on R: the Lead's ruling on F-308 and "
     "F-309), so L1's and R1's are one part"),
    ("ledge_end", "5 mm", "mm", "assumption", _LG + ": the ledge's ends 5 inside the right-hand cassette's"),
    ("ledge_len", "wall_depth - stack_t + cass_t - ledge_front_dy - 2 * ledge_end", "mm", "calculation",
     "1430: the right-hand cassette's length less 5 at each end"),
    ("ledge_rivet_d", "4.1 mm", "mm", "source", "Joints' pick: the hole for the ISO 15979 Ø4.0 blind rivet"),
    ("ledge_rivet_n", "6", "", "assumption", _LG + ": 6 rivets for the two cassettes' 20.2 kg, about 33 N each"),
    ("ledge_rivet_e", "40 mm", "mm", "assumption", "the end rivets 40 in from the ledge's ends"),
    ("ledge_rivet_z", "tube_w / 2 - 1 mm", "mm", "calculation",
     "the rivet line 9 above the frame's bottom: 9.0 from the upright's top edge (2.2 x the Ø4 rivet) and the hole's "
     "edge 8.2 from the bend"),
    ("ledge_rivet_pitch", "(ledge_len - 2 * ledge_rivet_e) / (ledge_rivet_n - 1)", "mm", "calculation",
     "even, so the pattern is symmetric and the turned copy (RH) matches: one part"),
    ("rivet_d", "4 mm", "mm", "source", "Joints' pick: blind rivet ISO 15979, open end, steel/steel, zinc plated, "
                                         "Ø4.0 x 6, grip 1.0 to 3.0 (the stack 1.0 + 1.2 = 2.2); tensile 2200 N, "
                                         "shear 1700 N (Keller & Kalmbach 580000130040060)"),
    ("rivet_head_d", "8 mm", "mm", "source", "Joints' pick: the dome head Ø8"),
    ("rivet_head_t", "1 mm", "mm", "source", "Joints' pick: the dome head 1.0 high"),
    ("rivet_len", "6 mm", "mm", "source", "Joints' pick: the body 6 long as supplied (its envelope; set, it is "
                                           "shorter and bulged inside the tube)"),
]
if ROW == 1:
    WALL_PARAMS = WALL_PARAMS + LEDGE_PARAMS
LEDGE_Y0 = "(pod_d / 2 - wall_depth + ledge_front_dy + ledge_end)"     # the ledge's front end

# kg/m3, status, source; used for body materials (mass properties)
DENSITY = {
    "frame": (7850.0, "source", "D-131: galvanized steel box tube, 7.85 g/cm3 (the zinc coat's mass not counted)"),
    "skin": (3.5 / 0.003, "calculation", "HW-SEL A1: 3.5 kg/m2 for 3 mm Alcorest / 3 mm; real kg/m2 HOLD (H16)"),
    "fill": (24.0, "confirmed", "PM ruling 2026-10-31: 24 kg/m3 by default, the grade Pyrotek lists (the wall sample's "
                                "T02 confirms it, else 32)"),
    "tray": (7850.0, "source", "steel 7850 kg/m3 (EN 10346 DX51D+Z)"),
    "felt": (1.8 / 0.009, "source", "Polyx Board 9: 1.8 kg/m2 at 9 mm (HW-SEL A3 opt 2); the factory felt is unverified"),
    "zone": (1.0, "assumption", "reserved zone, not a part: near-zero density so it adds no mass"),
    "rivnut": (7850.0, "source", "steel C1010/C1008, zinc plated with a yellow trivalent chromate (Sherex "
                                 "CAL2-610-4.2 rev B; D-163, steel since D-131): 7.85 g/cm3"),
    "stopw": (2700.0, "calculation", "5000- or 6000-series aluminium sheet (H-08): 2.70 g/cm3 (5052 2.68, 6061 2.70)"),
    "spigot": (7900.0, "source", "stainless steel (H-05): 7.9 g/cm3"),
    "plate": (7850.0, "source", "joints register H-40 to H-42: 2.0 steel plate, galvanized (17.8 / 28.1 / 35.5 g)"),
    "ledge": (7850.0, "source", "galvanized steel sheet DX51D+Z (EN 10346), 7.85 g/cm3 (the zinc not counted)"),
    "rivet": (7850.0, "source", "ISO 15979 steel blind rivet, zinc plated: 7.85 g/cm3 on its solid envelope"),
    "pad": (320.0, "source", "Rogers PORON 4701-40, the 320 kg/m3 grade (Joints' pick, 2026-11-01)"),
}

# ---------------------------------------------------------------- helpers


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    """Expression value in mm."""
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def skeleton_params(repo_root):
    """PARAMS of pod_skeleton.py, parsed with ast (no code is run)."""
    path = os.path.join(repo_root, SKELETON_REL)
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PARAMS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("no PARAMS in " + path)


def names_in(expr):
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", expr)) - {"mm", "ceil", "floor", "abs", "round"}


def needed_skeleton(skel, wall):
    """The skeleton parameters the wall expressions use, with their own dependencies, in skeleton order."""
    by_name = {p[0]: p for p in skel}
    want, todo = set(), set()
    for _n, expr, _u, _s, _src in wall:
        todo |= names_in(expr)
    for extra in ("pod_w", "pod_d", "pod_h", "wall_z0", "side_h", "stack_t", "outer_t", "cass_t", "lin_gap"):
        todo.add(extra)
    while todo:
        n = todo.pop()
        if n in by_name and n not in want:
            want.add(n)
            todo |= names_in(by_name[n][1])
    return [p for p in skel if p[0] in want]


SKELETON_NAMES = ("pod_w", "pod_d", "pod_h", "wall_depth", "wall_z0", "panel_z0", "side_h", "back_ph", "stack_t",
                  "outer_t", "cass_t", "lin_gap", "seam_gap", "skin_t", "bond_t", "bolt_edge_inset", "spigot_inset",
                  "n_base_bolt", "ceil_bolt_z")       # the skeleton parameters the wall uses (P04, as updated in #58)


def folder_files(folder, name=None):
    """The data files in a cloud folder (all, or those called `name`), through the shared folder reader
    (tools/fusion/fusion_folder.py, #213: one fetch of the folder per pass, about 2.5 s; it reads again while an
    entry can't be read, and stops early once `name` is found)."""
    from fusion_folder import read_folder     # run_script.py makes it importable and loads it fresh every run
    files, _unknown, _others = read_folder(folder, stop_when=(lambda f, u, o: name in f) if name else None)
    if name:
        return files.get(name, [])
    return [f for group in files.values() for f in group]


def derive_skeleton(app, design, name):
    """Link the design to the saved skeleton with Fusion's Derive (favorite parameters only), as
    tools/fusion/README.md 'Linking a part to the skeleton' describes. Returns the version derived."""
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
    files = folder_files(folder, name)
    if not files:
        raise RuntimeError("skeleton %r not found in Default Project / FocusPod v2" % name)
    part_doc = app.activeDocument
    # if the skeleton is already open (its owner may be working in it), use that and never close it
    already = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name == name]
    if already and (already[0].isModified or not already[0].dataFile
                    or already[0].dataFile.versionNumber != files[0].versionNumber):
        # an open copy can be changed, or an older version loaded through another document (the GA drawing
        # kept an old P04 loaded, 2026-10-31 18:53): derive only from the latest saved version
        raise RuntimeError("the skeleton is open in Fusion but not as its latest saved version (v%s; open: v%s, %s): "
                           "try again when it is closed" % (files[0].versionNumber,
                           already[0].dataFile.versionNumber if already[0].dataFile else "?",
                           "modified" if already[0].isModified else "unmodified"))
    skel_doc = already[0] if already else app.documents.open(files[0], False)          # invisible
    try:
        skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
        part_doc.activate()
        root = design.rootComponent
        di = root.features.deriveFeatures.createInput(skel)
        di.isIncludeFavoriteParameters = True
        di.sourceEntities = [skel.rootComponent.xYConstructionPlane]   # parameters only
        d = root.features.deriveFeatures.add(di)
        d.timelineObject.name = "DERIVE - SKELETON PARAMETERS (%s)" % name
        for pl in root.constructionPlanes:          # the derived plane only carries the link; keep it hidden
            if pl.isLightBulbOn and "PLANE - " not in pl.name:
                pl.isLightBulbOn = False
    finally:
        if not already:
            skel_doc.close(False)
        part_doc.activate()
    return files[0].versionNumber


def add_params(design, repo_root):
    app = adsk.core.Application.get()
    if ARGS.get("link", "derive") == "derive":
        skel_name = ARGS.get("skeleton", "100000_P04_POD-SKELETON_CAD")
        ver = derive_skeleton(app, design, skel_name)
        for n in SKELETON_NAMES:
            ref = design.allParameters.itemByName(n + "_Ref")
            if ref is None:
                raise RuntimeError("the skeleton has no favorite parameter %s (derived as %s_Ref)" % (n, n))
            design.userParameters.add(n, vi(n + "_Ref"), ref.unit, "LINKED: %s_Ref, derived from %s v%d (skeleton is "
                                                                 "the single source)" % (n, skel_name, ver))
        n_skel = len(SKELETON_NAMES)
    else:
        skel = skeleton_params(repo_root)
        used = needed_skeleton(skel, WALL_PARAMS)
        for name, expr, unit, status, src in used:
            design.userParameters.add(name, vi(expr), unit, "%s: %s [copied from pod_skeleton.py PARAMS, link=parse]" % (
                status.upper(), src))
        n_skel = len(used)
    for name, expr, unit, status, src in WALL_PARAMS:
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        if p is None:
            raise RuntimeError("could not add parameter " + name)
    return n_skel, len(WALL_PARAMS)


def new_comp(parent, key, sheet_metal=False):
    pn, name, vn = PARTS[key]
    tr = adsk.core.Matrix3D.create()
    occ = parent.occurrences.addNewSheetMetalComponent(tr) if sheet_metal else parent.occurrences.addNewComponent(tr)
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s | %s" % (name, vn, REV)
    return c


def sx(expr):
    """X coordinate expression on this side: expr is the distance from the pod centre plane."""
    return "-(%s)" % expr if S < 0 else "(%s)" % expr


def span(design, a, b):
    """Order two coordinate expressions by value: (low, high)."""
    return (a, b) if ev(design, a) <= ev(design, b) else (b, a)


def xy_plane(comp, z_expr, design, label):
    if abs(ev(design, z_expr)) < 1e-9:
        return comp.xYConstructionPlane
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, vi(z_expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    return pl


def box(design, comp, label, xr, yr, zr, op="new", body=None, plane=None):
    """Axis-aligned box: a fully constrained rectangle on the XY plane at z0 (corners dimensioned
    from the sketch origin by the parameter expressions), extruded along +Z to z1.
    op: new | cut | join (cut and join act on `body`). Returns the feature."""
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    x0, x1, y0, y1 = (ev(design, e) for e in (xr[0], xr[1], yr[0], yr[1]))
    pl = plane or xy_plane(comp, zr[0], design, label + " BOTTOM")
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0 * MM, y0 * MM, 0), adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
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
    ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
           "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
           "join": adsk.fusion.FeatureOperations.JoinFeatureOperation}
    ext_in = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), ops[op])
    ext_in.setDistanceExtent(False, vi("(%s) - (%s)" % (zr[1], zr[0])))
    if op != "new" and body is not None:
        ext_in.participantBodies = body if isinstance(body, list) else [body]
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "%s - %s" % ({"new": "EXTRUDE", "cut": "CUT", "join": "JOIN"}[op], label)
    return ext


def tube(design, comp, label, xr, yr, zr, along, t="tube_t"):
    """Hollow member (20 x 40 or 40 x 40, wall t): outer box, then the bore cut through its length.
    along: 'y' (rail) or 'z' (stile); t: 'tube_t' (perimeter, 1.2) or 'stud_t' (intermediate studs, 1.0, D-85)."""
    ext = box(design, comp, label + " TUBE", xr, yr, zr)
    b = ext.bodies.item(0)
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    bx = ("(%s) + %s" % (xr[0], t), "(%s) - %s" % (xr[1], t))
    if along == "y":
        box(design, comp, label + " BORE", bx, yr, ("(%s) + %s" % (zr[0], t), "(%s) - %s" % (zr[1], t)), "cut", b)
    else:
        box(design, comp, label + " BORE", bx, ("(%s) + %s" % (yr[0], t), "(%s) - %s" % (yr[1], t)), zr, "cut", b)
    b.name = label
    return b


def pattern_y(comp, bodies, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for b in bodies:
        coll.add(b)
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, comp.yConstructionAxis, vi(count_expr), vi(pitch_expr),
        adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    # Fusion 2706 defaults direction two to 3 instances at 0 mm when it isn't set, which stacks 3
    # identical bodies on every instance (found on the first L1 build, 2026-10-31): set it to 1.
    pin.setDirectionTwo(comp.zConstructionAxis, vi("1"), vi("1 mm"))
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


AXES = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def origin_plane(comp, axis):
    """The origin plane normal to a model axis."""
    return {"x": comp.yZConstructionPlane, "y": comp.xZConstructionPlane, "z": comp.xYConstructionPlane}[axis]


def plane_at(design, comp, axis, expr, label):
    """Construction plane normal to `axis` at coordinate `expr`. An offset runs along the origin plane's
    normal, which need not point along +axis (Fusion's XZ plane), so the sign follows that normal."""
    base = origin_plane(comp, axis)
    if abs(ev(design, expr)) < 1e-9:
        return base
    n = base.geometry.normal
    sign = 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(base, vi(expr if sign > 0 else "-(%s)" % expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    o = pl.geometry.origin
    got = {"x": o.x, "y": o.y, "z": o.z}[axis] * 10.0
    if abs(got - ev(design, expr)) > 0.01:
        raise RuntimeError("plane %s landed at %s = %.2f, not %.2f" % (label, axis, got, ev(design, expr)))
    return pl


def sketch_axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis maps to on this sketch."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*AXES[model_axis]))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def hole(design, comp, body, axis, plane_expr, into, pos, dia, depth, label):
    """A simple hole feature on a plane normal to `axis` at `plane_expr`, drilled `into` (+1 or -1 along
    the axis) for `depth`. pos: {model axis: coordinate expression} for the two in-plane axes. The centre
    point is dimensioned from the sketch origin by those expressions, so the sketch is fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "HOLE CENTRE - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    pt = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(pt, sk.originPoint)
        else:
            g = pt.geometry
            tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, H if sa == "x" else V,
                                                     tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    hin = comp.features.holeFeatures.createSimpleInput(vi(dia))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi(depth))
    n = pl.geometry.normal
    if into * {"x": n.x, "y": n.y, "z": n.z}[axis] > 0:
        hin.isDefaultDirection = False       # a hole runs against the plane normal unless flipped
    hin.participantBodies = [body]
    h = comp.features.holeFeatures.add(hin)
    h.name = "HOLE - %s" % label
    return h


def rect_on_x(design, comp, x_expr, yr, zr, label):
    """Fully constrained rectangle on a plane normal to X at x_expr, spanning model Y yr and Z zr."""
    yr, zr = span(design, *yr), span(design, *zr)
    pl = plane_at(design, comp, "x", x_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    x = ev(design, x_expr)
    y0, y1, z0, z1 = (ev(design, e) for e in (yr[0], yr[1], zr[0], zr[1]))

    def sp(y, z):
        return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, z * MM))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(sp(y0, z0), sp(y1, z1))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(a.y - b.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for q in (ln.startSketchPoint, ln.endSketchPoint):
            if all(q != o for o in pts):
                pts.append(q)

    def near(y, z):
        t = sp(y, z)
        return min(pts, key=lambda q: (q.geometry.x - t.x) ** 2 + (q.geometry.y - t.y) ** 2)
    c00, c10, c01 = near(y0, z0), near(y1, z0), near(y0, z1)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    ay, az = sketch_axis_of(sk, "y"), sketch_axis_of(sk, "z")
    o = {"x": H, "y": V}
    mid = sp((y0 + y1) / 2, (z0 + z1) / 2)
    tp = adsk.core.Point3D.create(mid.x, mid.y, 0)
    sk.sketchDimensions.addDistanceDimension(c00, c10, o[ay], tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    sk.sketchDimensions.addDistanceDimension(c00, c01, o[az], tp).parameter.expression = "(%s) - (%s)" % (zr[1], zr[0])
    for axis, val, e in ((ay, y0, yr[0]), (az, z0, zr[0])):
        if abs(val) < 1e-6:
            (gc.addVerticalPoints if axis == "x" else gc.addHorizontalPoints)(c00, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c00, o[axis], tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk


def pattern_feat(comp, feats, axis, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for f in feats:
        coll.add(f)
    ax = {"x": comp.xConstructionAxis, "y": comp.yConstructionAxis, "z": comp.zConstructionAxis}[axis]
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, ax, vi(count_expr), vi(pitch_expr), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    other = comp.zConstructionAxis if axis != "z" else comp.xConstructionAxis
    pin.setDirectionTwo(other, vi("1"), vi("1 mm"))      # see pattern_y
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


HW_SITES = []          # rivnut sites recorded by the joint features, given their hardware by place_hardware
ALLOWED_CLASH = []     # body name pairs that overlap by design (a spigot's thread in its rivnut's bore)


def hw_site(label, axis, face, into, pos, pat=None, washer=True, spigot=False, member=None, kind="rivnut"):
    """Record a rivnut hole for the hardware: the same plane, centre and pattern as the hole, and the frame
    member it is in (D-120: the hardware's copies are jointed to that member's hole).
    into: the hole's direction into the tube; the head and any washer stand the other way, in the joint gap.
    kind "rivet": a ledge rivet's hole, its head on the ledge (ledge_t out from the member's face)."""
    HW_SITES.append({"label": label, "axis": axis, "face": face, "out": -into, "pos": pos, "pat": pat,
                     "washer": washer, "spigot": spigot, "member": member, "kind": kind})


def cyl(design, comp, label, axis, plane_expr, out, pos, od, length, bore=None):
    """New body: a cylinder (or a tube, with `bore`) on a plane normal to `axis` at `plane_expr`, extruded `out`
    (+1 or -1 along the axis) by `length`. The circle's centre is dimensioned from the sketch origin by the `pos`
    expressions and its diameters by `od` and `bore`, so the sketch is fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM))
    circles = sk.sketchCurves.sketchCircles
    outer = circles.addByCenterRadius(ctr, ev(design, od) / 2.0 * MM)
    cp = outer.centerSketchPoint
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    g = cp.geometry
    tp = adsk.core.Point3D.create(g.x + 0.7, g.y + 0.7, 0)
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(cp, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, cp, H if sa == "x" else V,
                                                     tp).parameter.expression = "abs(%s)" % e
    sk.sketchDimensions.addDiameterDimension(outer, tp).parameter.expression = od
    if bore:
        inner = circles.addByCenterRadius(cp, ev(design, bore) / 2.0 * MM)
        sk.sketchDimensions.addDiameterDimension(inner, tp).parameter.expression = bore
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    v, k = ev(design, plane_expr), "xyz".index(axis)
    for dirn in (adsk.fusion.ExtentDirections.PositiveExtentDirection,
                 adsk.fusion.ExtentDirections.NegativeExtentDirection):
        profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
        prof = max(profs, key=lambda q: q.profileLoops.count) if bore else profs[0]
        ein = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ein.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(length)), dirn)
        f = comp.features.extrudeFeatures.add(ein)
        b = bbox(f.bodies.item(0))
        if abs((b[k] if out > 0 else b[k + 3]) - v) < 0.01:
            f.name = "EXTRUDE - %s" % label
            return f.bodies.item(0)
        f.deleteMe()
    raise RuntimeError("cylinder %s: neither direction starts on its plane" % label)


def join_bodies(comp, target, tools, label):
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    cin = comp.features.combineFeatures.createInput(target, coll)
    cin.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    f = comp.features.combineFeatures.add(cin)
    f.name = "COMBINE - %s" % label
    return f.bodies.item(0) if f.bodies.count else target


def name_along(comp, axis, known, first, prefix):
    """Name a pattern's bodies and its original by their order along +axis: PREFIX 1..n."""
    k = "xyz".index(axis)
    group = [first] + [b for b in comp.bRepBodies if not any(b == q for q in known) and not b == first]
    group.sort(key=lambda b: (b.boundingBox.minPoint.x, b.boundingBox.minPoint.y, b.boundingBox.minPoint.z)[k])
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along %s: %s" % (axis, prefix))
    out = {}
    for i, b in enumerate(group):
        b.name = "%s %d" % (prefix, i + 1)
        out[b.name] = b
    return out


def settle_props(app, root, pn, desc, seconds=30.0):
    """The cloud can overwrite the root component's part number and description: --doc-new's first upload
    finishing after a short build (the skin, 2026-10-31) put the document's timestamp name in the part
    number, and new documents came out of their save with an empty description (B1, R1). Wait until the
    document has its data file and both have held for a second, setting them again when they change."""
    import time
    t0, held = time.time(), 0
    while time.time() - t0 < seconds:
        adsk.doEvents()
        if root.partNumber != pn or root.description != desc:
            root.partNumber = pn
            root.description = desc
            held = 0
        elif app.activeDocument.dataFile is not None:
            held += 1
            if held >= 5:
                return True
        time.sleep(0.2)
    return root.partNumber == pn and root.description == desc


def save_holding_props(app, doc, root, pn, desc, note, tries=3):
    """Save, wait for the upload to finish (the data file's version moves on), and check the part number and
    description came through; if the upload reset them, set them again and save again."""
    import time
    for attempt in range(1, tries + 1):
        if not settle_props(app, root, pn, desc):
            raise RuntimeError("root part number / description would not hold before the save (%r, %r)" % (
                root.partNumber, root.description))
        before = doc.dataFile.versionNumber if doc.dataFile else 0
        if not doc.save(note if attempt == 1 else "%s (part number and description set again)" % note):
            raise RuntimeError("save failed")
        t0 = time.time()
        while time.time() - t0 < 90.0 and not (doc.dataFile and doc.dataFile.versionNumber > before):
            adsk.doEvents()
            time.sleep(0.25)
        for _i in range(12):                    # 3 s more for the cloud to send any property back
            adsk.doEvents()
            time.sleep(0.25)
        if root.partNumber == pn and root.description == desc:
            return doc.dataFile.versionNumber if doc.dataFile else None
        print("the save reset the root properties (%r, %r); setting them again" % (root.partNumber, root.description))
    raise RuntimeError("root part number / description did not survive %d saves" % tries)


def name_by_y(comp, known, first, prefix):
    """Name the pattern's copies and the original by their order along +Y: PREFIX 1..n.
    Fusion API objects compare with == but are not hashable, so `known` is a list."""
    group = [first] + [b for b in comp.bRepBodies if not any(b == k for k in known) and not b == first]
    group.sort(key=lambda b: b.boundingBox.minPoint.y)
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along Y: %s" % prefix)
    out = {}
    for i, b in enumerate(group):
        b.name = "%s %d" % (prefix, i + 1)
        out[b.name] = b
    return out


def bbox(entity):
    b = entity.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def size(b):
    return "%g x %g x %g" % (round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2))


def set_material(design, bodies, key, label):
    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
    base = lib.materials.itemByName("Aluminum")
    name = "%s %g kg/m3 (%s)" % (label, round(DENSITY[key][0], 1), DENSITY[key][1])
    mat = design.materials.itemByName(name)
    if mat is None:
        mat = design.materials.addByCopy(base, name)
        mat.materialProperties.itemById("structural_Density").value = DENSITY[key][0]
    for b in bodies:
        b.material = mat
    return mat


def clash_check(bodies, allowed=()):
    """Pairwise solid intersections over 1 mm3; fails on any pair not in `allowed`."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            ba, bb = bbox(a), bbox(b)
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(a), tbm.copy(b)
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((a.name, b.name, round(vol)))
    bad = [h for h in hits if frozenset(h[:2]) not in {frozenset(p) for p in allowed}]
    return hits, bad


def clear_design(design):
    """rebuild=1: empty a design this script built before (same root part number)."""
    tl = design.timeline
    if tl.count:
        tl.moveToBeginning()
        tl.deleteAllAfterMarker()
    for i in range(design.userParameters.count - 1, -1, -1):
        design.userParameters.item(i).deleteMe()
    for i in range(design.materials.count - 1, -1, -1):
        m = design.materials.item(i)
        if " kg/m3 (" in m.name:
            try:
                m.deleteMe()
            except Exception:       # still in use by nothing after the timeline is gone; ignore
                pass


# ---------------------------------------------------------------- geometry expressions

X_OUT = sx("pod_w / 2")                          # outer face of the skin
X_SKIN_IN = sx("pod_w / 2 - skin_t")             # inner face of the skin
X_FRAME_OUT = sx("pod_w / 2 - skin_t - bond_t")  # outer face of the frame, behind the 3 mm bond line
X_FRAME_IN = sx("pod_w / 2 - outer_t")           # inner face of the frame (side frames' inner face)
X_IN = sx("pod_w / 2 - stack_t")                 # room-side face of the lining (felt face)
X_TRAY_BACK = sx("pod_w / 2 - stack_t + cass_t")   # back face of the tray base (4 mm from the frame)
X_FELT_FACE = sx("pod_w / 2 - stack_t + tray_t")   # felt's room face, behind the lips
X_FELT_BACK = sx("pod_w / 2 - stack_t + tray_t + felt_t")

# panel envelope: the skeleton's side panel (seam gaps at the decor, on the band and at the row seam)
Y_FRONT = "pod_d / 2 - wall_depth + seam_gap"    # panel front end: 2.26 behind the decor back plate (F-008)
Y_BACK = "pod_d / 2"                             # outer face of the back wall
Y_RETURN_IN = "pod_d / 2 - skin_t"               # inside of the skin's back return
# the frame's back face, behind the return's own 3 mm bond line (the Lead's ruling, 2026-11-01: every skin face that
# meets a frame is bonded at bond_t, no zero fits; the return gets the D-137 joint like the main face). The 40 x 40
# back stile then spans Y 804 to 844, in line with the back frames and centred on the corner bolt line (bolt_line_y)
Y_FRAME_BACK = "pod_d / 2 - skin_t - bond_t"
Y_CASS_FRONT = "pod_d / 2 - wall_depth"          # the decor back plate (skeleton P04): the ceiling's front edge too
Y_LIN_FRONT = "pod_d / 2 - wall_depth + lin_front_dy"   # the cassette's front end (R side 5 behind, clear of DR)
Y_CASS_BACK = "pod_d / 2 - stack_t + cass_t"     # side lining end, past the back lining (D-57)

# rows as skeleton P04: panel_z0 = the walls' bottom, one seam_gap above the band top (F-008)
Z0 = "panel_z0" if ROW == 1 else "panel_z0 + side_h + seam_gap"
Z1 = "panel_z0 + side_h" if ROW == 1 else "pod_h"
Z_SKIN0 = "(%s) + skin_setback" % Z0
Z_SKIN1 = "(%s) - skin_setback" % Z1 if ROW == 1 else Z1   # the upper skins run to the roof datum
Z_CASS1 = Z1 if ROW == 1 else "pod_h - outer_t - lin_gap"


# ---------------------------------------------------------------- D-120: every part its own component (D-117 corner
# geometry; D-131 welds the corners and T joints in steel)

_ALLOC = []
MEMBER_WORDS = {"RAIL - BOTTOM": "RAIL BOTTOM", "RAIL - TOP": "RAIL TOP", "STILE - FRONT": "STILE FRONT",
                "STILE - BACK": "STILE BACK", "STILE - MID": "STILE MID", "STILE - OUTER": "STILE OUTER",
                "STILE - CENTRE": "STILE CENTRE"}


def allocation(repo_root):
    """The master BOM's number allocation (v2/04-BOM/number-allocation.csv): frame members and fill pieces. Rows
    marked CANCELLED are left out (never reused, D-123), so a number moved to another row can't be picked twice."""
    if not _ALLOC:
        import csv
        with open(os.path.join(repo_root, "v2/04-BOM/number-allocation.csv"), encoding="utf-8") as fh:
            _ALLOC.extend(r for r in csv.DictReader(fh) if (r.get("status") or "").strip().upper() != "CANCELLED")
    return _ALLOC


def member_numbers(repo_root, frame_pn):
    """{member key: (part number, name, Vietnamese name)} of one frame (D-120; the frame keeps its number and
    parents its members, D-123)."""
    out = {}
    for r in allocation(repo_root):
        if frame_pn in r["parent"].split() and r["part_number"].startswith("212"):
            for key, word in MEMBER_WORDS.items():
                if " FRAME %s" % word in r["name"]:
                    out[key] = (r["part_number"], r["name"], r["name_vi"])
    return out


def fill_numbers(repo_root, code):
    """{bay: (part number, name, Vietnamese name)} of one position: the form of each bay from WALL's
    FILL-PIECES.csv, the form's number from the allocation (D-123)."""
    import csv
    forms = {}
    with open(os.path.join(repo_root, "v2/03-Manufacturing/wall/FILL-PIECES.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["position"] == code:
                forms[int(r["bay"])] = r["form"]
    sizes = {}
    with open(os.path.join(repo_root, "v2/03-Manufacturing/wall/FILL-PIECES.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            # as the allocation names them: "240 X 1102.7", not the list's "240.0" (dry run 8 found F01 and F04
            # unnumbered for that)
            sizes[r["form"]] = "%g X %g" % (float(r["w_mm"]), float(r["h_mm"]))
    byform = {}
    for r in allocation(repo_root):
        m = re.search(r"FILL PIECE (F\d\d) ", r["name"])
        if m and m.group(1) in sizes and "%s %s" % (m.group(1), sizes[m.group(1)]) in r["name"]:
            if m.group(1) in byform:
                raise RuntimeError("two live numbers for fill form %s %s" % (m.group(1), sizes[m.group(1)]))
            byform[m.group(1)] = (r["part_number"], r["name"], r["name_vi"])
    out = {bay: byform[f] for bay, f in forms.items() if f in byform}
    if ARGS.get("dry") == "1":            # a dry run (never saved) labels a form whose number isn't allocated yet
        for bay, f in forms.items():
            out.setdefault(bay, ("DRY-%s" % f, "WALL - CAVITY FILL PIECE %s (DRY RUN, NO NUMBER YET)" % f, ""))
    return out


def child(parent, pn, name, vn):
    """A new component in `parent` for one part, named PARTNO NAME; returns (component, its occurrence in the
    parent's context)."""
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = "%s %s" % (pn, name)
    c.partNumber = pn
    c.description = "%s | %s | %s" % (name, vn, REV)
    return c, occ


def root_occ(design, comp):
    """The first occurrence of a component, in the root's context (for joints and proxies)."""
    occs = design.rootComponent.allOccurrencesByComponent(comp)
    return occs.item(0) if occs.count else None


def poly_plan(sxy, exprs):
    """How to constrain a closed polygon (pure, tested offline): sxy = the corners' sketch coordinates, exprs =
    each corner's (sketch-x expression, sketch-y expression). A side that runs along a sketch axis gets its
    vertical or horizontal constraint, which ties its two corners along that axis; each group of tied corners is
    then dimensioned once from the sketch origin, so no dimension repeats a constraint (the L1 run of 2026-11-01
    failed on exactly that: Fusion constrains such sides itself). Returns (sides: [(i, 'V' or 'H')], dims: [(i,
    sketch axis 'x' or 'y', expression)]). Raises when tied corners carry different expressions (the tie would
    override one of them on an edit)."""
    n = len(sxy)
    parent = {"x": list(range(n)), "y": list(range(n))}

    def find(ax, i):
        while parent[ax][i] != i:
            parent[ax][i] = parent[ax][parent[ax][i]]
            i = parent[ax][i]
        return i
    sides = []
    for i in range(n):
        j = (i + 1) % n
        if abs(sxy[i][0] - sxy[j][0]) < 1e-9:
            sides.append((i, "V"))
            parent["x"][find("x", i)] = find("x", j)
        elif abs(sxy[i][1] - sxy[j][1]) < 1e-9:
            sides.append((i, "H"))
            parent["y"][find("y", i)] = find("y", j)
    dims, seen = [], {}
    for i in range(n):
        for k, ax in enumerate(("x", "y")):
            root = find(ax, i)
            if root in seen.setdefault(ax, {}):
                if seen[ax][root] != exprs[i][k]:
                    raise ValueError("corners tied along sketch %s carry %r and %r" % (ax, seen[ax][root], exprs[i][k]))
                continue
            seen[ax][root] = exprs[i][k]
            dims.append((i, ax, exprs[i][k]))
    return sides, dims


def poly_on(design, comp, axis, plane_expr, pts, label):
    """A fully constrained closed polygon on a plane normal to `axis` at plane_expr: pts = [(a, b), ...], the
    corners' expressions in the plane's other two axes in xyz order (axis x: (y, z); y: (x, z)). Constrained as
    poly_plan says: straight sides vertical or horizontal, each tied group of corners dimensioned once from the
    sketch origin by its expressions."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    other = [a for a in "xyz" if a != axis]
    v = ev(design, plane_expr)
    sp = []
    for a, b in pts:
        c = {axis: v, other[0]: ev(design, a), other[1]: ev(design, b)}
        sp.append(sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM,
                                                                                    c["z"] * MM))))
    lines = [sk.sketchCurves.sketchLines.addByTwoPoints(sp[i], sp[(i + 1) % len(sp)]) for i in range(len(sp))]
    # each corner's expressions along the sketch's own x and y
    sa = {m: sketch_axis_of(sk, m) for m in other}
    exprs = [tuple(e for m, e in sorted(((sa[other[0]], a), (sa[other[1]], b)))) for a, b in pts]
    sides, dims = poly_plan([(q.geometry.x, q.geometry.y) for q in sp], exprs)
    gc = sk.geometricConstraints
    kinds = {"V": adsk.fusion.VerticalConstraint.classType(), "H": adsk.fusion.HorizontalConstraint.classType()}
    for i, kind in sides:
        if not any(c.objectType == kinds[kind] for c in lines[i].geometricConstraints):
            (gc.addVertical if kind == "V" else gc.addHorizontal)(lines[i])
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for i, ax, e in dims:
        q = sp[i]
        if abs(ev(design, e)) < 1e-6:
            (gc.addVerticalPoints if ax == "x" else gc.addHorizontalPoints)(q, sk.originPoint)
        else:
            g = q.geometry
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, q, H if ax == "x" else V,
                                                     adsk.core.Point3D.create(g.x + 0.3, g.y + 0.3, 0)
                                                     ).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk, pl


def sketch_points(design, comp, axis, plane_expr, pts, label):
    """Points on a plane normal to `axis` at plane_expr: pts = [(a, b), ...], their expressions in the plane's other
    two axes in xyz order; each dimensioned from the sketch origin (points only, so nothing is tied twice). Returns
    the sketch points, the sketch fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    other = [a for a in "xyz" if a != axis]
    v = ev(design, plane_expr)
    sa = {m: sketch_axis_of(sk, m) for m in other}
    gc = sk.geometricConstraints
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    out = []
    for a, b in pts:
        c = {axis: v, other[0]: ev(design, a), other[1]: ev(design, b)}
        q = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
        for m, e in ((other[0], a), (other[1], b)):
            if abs(ev(design, e)) < 1e-6:
                (gc.addVerticalPoints if sa[m] == "x" else gc.addHorizontalPoints)(q, sk.originPoint)
            else:
                g = q.geometry
                sk.sketchDimensions.addDistanceDimension(sk.originPoint, q, H if sa[m] == "x" else V,
                                                         adsk.core.Point3D.create(g.x + 0.3, g.y + 0.3, 0)
                                                         ).parameter.expression = "abs(%s)" % e
        out.append(q)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return out


def offset_origin(comp, dx, dy, dz, angle=None, name=None):
    """A joint origin on comp's origin moved by (dx, dy, dz) along comp's own axes (expressions, so it follows the
    parameters) and turned `angle` about comp's Z; no sketch to constrain."""
    jin = comp.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint))
    for attr, e in (("offsetX", dx), ("offsetY", dy), ("offsetZ", dz)):
        if e not in (None, "", "0", "0 mm"):
            setattr(jin, attr, vi(e))
    if angle:
        jin.angle = vi(angle)
    jo = comp.jointOrigins.add(jin)
    if name:
        jo.name = name
    return jo


def joint_copy(design, parent, comp, ref, tgt, want, label, angle=None):
    """A copy of comp in `parent` (D-120: copies of one part), held by a rigid joint IN THE ROOT from comp's joint
    origin `ref` to parent's joint origin `tgt` (the dry run of 06:45 showed a joint made inside a sub-component
    stays where it is, while the root's joints place the part), checked against its box `want` (mm, pod
    coordinates), flipped if needed. Returns the copy's occurrence in parent."""
    root = design.rootComponent
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    p_occ = root_occ(design, parent) if parent != root else None
    occ = parent.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
    occ_r = occ.createForAssemblyContext(p_occ) if p_occ else occ
    g1 = ref.createForAssemblyContext(occ_r)
    g2 = tgt.createForAssemblyContext(p_occ) if p_occ else tgt
    for flip in (False, True):
        jin = root.joints.createInput(g1, g2)
        jin.setAsRigidJointMotion()
        jin.isFlipped = flip
        if angle:                          # turned about the joint's Z at the joint origin (a joint origin's own
            jin.angle = vi(angle)          # angle would turn its offsets too: the dry run of 07:20)
        j = root.joints.add(jin)
        got = bbox(occ_r.bRepBodies.item(0))
        if j.healthState == healthy and all(abs(x - y) < 0.05 for x, y in zip(got, want)):
            j.name = "JOINT - %s" % label
            return occ
        print("COPY|%s: flip %s gave %s, want %s" % (label, flip, [round(x, 2) for x in got],
                                                      [round(x, 2) for x in want]))
        j.deleteMe()
    raise RuntimeError("%s: no joint puts the copy at %s" % (label, [round(x, 2) for x in want]))


def poly_on_x(design, comp, x_expr, pts, label):
    """poly_on on a plane normal to X (a side wall's frame plane): pts = [(y_expr, z_expr), ...]."""
    return poly_on(design, comp, "x", x_expr, pts, label)


def mitre(design, comp, body, tri, label, x_lo):
    """One mitre (D-117's corner, welded under D-131): a triangle in the frame's plane, cut through the member's
    depth from x_lo."""
    sk, pl = poly_on_x(design, comp, x_lo, tri, "MITRE " + label)
    depth = "tube_d + 2 mm" if pl.geometry.normal.x > 0 else "-(tube_d + 2 mm)"
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                   adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setDistanceExtent(False, vi(depth))
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - MITRE %s" % label
    return f


def mitre_triangles(o, i, ext=0.1):
    """A corner's two cut triangles: the mitre line from the outer corner o to the inner corner i, extended by `ext`
    of its length past both, closed toward the rail's end (rail) and toward the stile's end (stile)."""
    def at(a, b, k):
        return "(%s) + %s * ((%s) - (%s))" % (a, k, b, a)
    o2 = (at(o[0], i[0], "-%g" % ext), at(o[1], i[1], "-%g" % ext))
    i2 = (at(o[0], i[0], "%g" % (1 + ext)), at(o[1], i[1], "%g" % (1 + ext)))
    return [o2, (o2[0], i2[1]), i2], [o2, (i2[0], o2[1]), i2]


def plated_mitre_triangles(design, o, i, w_rail, w_stile):
    """D-131's corner (the Joints Engineer's detail, 2026-11-01): the two mitre triangles, each moved back along its
    own member so the cut lines stand plate_t apart, centred on the old mitre line, for the 2 mm plate welded in
    between: c = (plate_t / 2) x the mitre's length in the frame plane / the member's own width (1.41 for 20 to 20
    and 40 to 40; 2.24 off a 20 rail and 1.12 off a 40 x 40 stile where they meet). o: the outer corner, i: the
    inner corner, (along-rail, along-stile) expressions; w_rail, w_stile: the members' widths in the frame plane."""
    rt, st = mitre_triangles(o, i, 0.3)
    su = 1 if ev(design, i[0]) > ev(design, o[0]) else -1      # into the rail, along it
    sv = 1 if ev(design, i[1]) > ev(design, o[1]) else -1      # into the stile, along it
    hyp = "sqrt((%s) * (%s) + (%s) * (%s))" % (w_rail, w_rail, w_stile, w_stile)
    cr = "(plate_t / 2) * %s / (%s)" % (hyp, w_rail)
    cs = "(plate_t / 2) * %s / (%s)" % (hyp, w_stile)
    return ([("(%s) %s %s" % (u, "+" if su > 0 else "-", cr), v) for u, v in rt],
            [(u, "(%s) %s %s" % (v, "+" if sv > 0 else "-", cs)) for u, v in st])


def side_corners():
    """The side frame's 4 corners (D-117): (label, rail, stile, outer corner, inner corner). The mitre runs from
    the outer corner to the inner corner, so both members run to the outer corner: 45 degrees where the two are
    the same size; where a 40 x 40 meets a 20 x 40, 26.57 off square on the 40 x 40 and 63.43 on the 20 x 40."""
    yf, yb = Y_FRONT, Y_FRAME_BACK
    return [("BOTTOM FRONT", "RAIL - BOTTOM", "STILE - FRONT", (yf, Z0), ("(%s) + tube_w" % yf, "(%s) + tube_w" % Z0),
             "tube_w", "tube_w"),
            ("BOTTOM BACK", "RAIL - BOTTOM", "STILE - BACK", (yb, Z0), ("(%s) - corner_w" % yb, "(%s) + tube_w" % Z0),
             "tube_w", "corner_w"),
            ("TOP FRONT", "RAIL - TOP", "STILE - FRONT", (yf, Z1), ("(%s) + tube_w" % yf, "(%s) - top_h" % Z1),
             "top_h", "tube_w"),
            ("TOP BACK", "RAIL - TOP", "STILE - BACK", (yb, Z1), ("(%s) - corner_w" % yb, "(%s) - top_h" % Z1),
             "top_h", "corner_w")]


def build_panel(design, root):
    out = {}
    want = WANT[PART]
    frame, skin = (new_comp(root, k) if k in want else None for k in ("frame", "skin"))
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin) if c))
    if STOP_AFTER <= 1:
        return out
    xf = (X_FRAME_OUT, X_FRAME_IN)
    yf = (Y_FRONT, Y_FRAME_BACK)
    zs = ("(%s) + tube_w" % Z0, "(%s) - top_h" % Z1)
    members = {}
    if frame:
        members = build_frame(design, frame, out, xf, yf, zs)
    if skin:
        build_skin(design, skin, out)
    if "fill" in want:
        build_fill(design, root, out, xf, zs)
    if frame:
        joint_features(design, members, out)
    if PART == "panel" and ROW == 1:
        build_ledge(design, root, out)
    if PART == "panel":
        place_hardware(design, root, members, out)
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "STEEL BOX TUBE GALVANIZED")
    set_material(design, [b for k, b in out.items() if k.startswith("SKIN")], "skin", "ACP 3 MM EV3038")
    set_material(design, [b for k, b in out.items() if k.startswith("FILL")], "fill", "PET FILL 40 MM")
    return out


def build_frame(design, frame, out, xf, yf, zs):
    """D-120 and D-131: each member its own component with its master BOM number; the frame an assembly of
    them (it keeps its number, D-123), welded in the factory: the 4 perimeter members run to the frame's outer
    corners, mitred there (D-117's geometry) and welded; the studs fit square between the rails and are welded
    there (T joints), one component placed by a pattern of copies. D-131 cancels D-117's cleats, so the rails have
    no cleat slots. Returns {member key: (component, body)}."""
    nums = member_numbers(ARGS["repo_root"], frame.partNumber)
    need = ["RAIL - BOTTOM", "RAIL - TOP", "STILE - FRONT", "STILE - BACK", "STILE - MID"]
    if [k for k in need if k not in nums]:
        raise RuntimeError("no master BOM numbers for %s of frame %s (number-allocation.csv)" % (
            [k for k in need if k not in nums], frame.partNumber))
    members, occs = {}, {}

    def make(key, yr, zr, along, t="tube_t"):
        c, occ = child(frame, *nums[key])
        b = tube(design, c, key, xf, yr, zr, along, t)
        members[key], occs[key] = (c, b), occ
        return b
    make("RAIL - BOTTOM", (Y_FRONT, Y_FRAME_BACK), (Z0, "(%s) + tube_w" % Z0), "y")
    make("RAIL - TOP", (Y_FRONT, Y_FRAME_BACK), ("(%s) - top_h" % Z1, Z1), "y", "corner_t" if ROW == 2 else "tube_t")
    if STOP_AFTER <= 2:
        return members
    make("STILE - FRONT", (Y_FRONT, "(%s) + tube_w" % Y_FRONT), (Z0, Z1), "z")
    make("STILE - BACK", ("(%s) - corner_w" % Y_FRAME_BACK, Y_FRAME_BACK), (Z0, Z1), "z", "corner_t")
    x_lo = "(%s) - 1 mm" % min(xf, key=lambda e: ev(design, e))
    for label, rail, stile, o, i, w_rail, w_stile in side_corners():
        rt, st = plated_mitre_triangles(design, o, i, w_rail, w_stile)
        mitre(design, members[rail][0], members[rail][0].bRepBodies.item(0), rt, "%s (%s)" % (label, rail), x_lo)
        mitre(design, members[stile][0], members[stile][0].bRepBodies.item(0), st, "%s (%s)" % (label, stile), x_lo)
    mitre_plates(design, frame, [(c[0], c[3], c[4], c[5], c[6]) for c in side_corners()], "x", X_FRAME_OUT,
                 1 if ev(design, X_FRAME_IN) > ev(design, X_FRAME_OUT) else -1)
    studs = ["stud_c%d" % k for k in range(1, int(round(design.userParameters.itemByName("stile_n_mid").value)) + 1)]
    yr = lambda c: ("(%s) + %s - tube_w / 2" % (Y_FRONT, c), "(%s) + %s + tube_w / 2" % (Y_FRONT, c))  # noqa: E731
    make("STILE - MID", yr(studs[0]), zs, "z", "stud_t")
    sc = members["STILE - MID"][0]
    ref = offset_origin(sc, None, None, None, name="JOINT ORIGIN - STUD")
    xs = sorted(ev(design, e) for e in xf)
    for k, c in enumerate(studs[1:], 2):
        tgt = offset_origin(frame, None, "(%s) - (%s)" % (c, studs[0]), None, name="JOINT ORIGIN - STUD %d" % k)
        joint_copy(design, frame, sc, ref, tgt, (xs[0], ev(design, yr(c)[0]), ev(design, zs[0]), xs[1],
                                                 ev(design, yr(c)[1]), ev(design, zs[1])), "STUD %d" % k)
    for key, (c, _b) in members.items():
        members[key] = (c, c.bRepBodies.item(0))
        out[key] = c.bRepBodies.item(0)
        out[key].name = key
    print("step 2-3: frame of %d member parts, %d studs (one part, copies held by joints) at Y %s from the front, "
          "4 mitred corners" % (len(members), len(studs), ", ".join("%.1f" % ev(design, c) for c in studs)))
    return members


PLATES_BUILT = {}


def plate_part(design, frame, key, length):
    """One component per mitre plate (D-120), in the frame (welded into it): Joints' STEP when it is in the repo,
    else a plain 2.0 box over the full mitre (a stand-in only), built about the joints README's origin and axes: the
    origin at the frame's outer corner, on the skin-side face, on the plate's mid-plane; +X along the mitre toward
    the inner corner, +Y across the frame (tube_d), Z the thickness (+-plate_t/2). Joints' blanks are a little
    shorter than the mitre so their square edges sit about 0.5 inside the frame's faces (the Lead, 2026-11-01): each
    starts along +X from the origin (1.75, 3.15 for 831008) and ends at the inner corner; mitre_plates reads each
    blank's own extents. Returns (component, body, the joint origin at the README origin)."""
    if key in PLATES_BUILT:
        return PLATES_BUILT[key]
    pn = PARTS[key][0]
    steps = glob.glob(os.path.join(ARGS["repo_root"], "v2/03-Manufacturing/joints/%s_P01_*_STEP.step" % pn))
    if steps:
        JOINTS_STEP[key] = os.path.relpath(steps[0], ARGS["repo_root"])
        JOINTS_BODY[key] = "MITRE PLATE"
        c, b = import_joints_part(design, frame, key)
    else:
        c = new_comp(frame, key)
        b = box(design, c, "MITRE PLATE", ("0 mm", length), ("0 mm", "tube_d"),
                ("-plate_t / 2", "plate_t / 2")).bodies.item(0)
        b.name = "MITRE PLATE"
        set_material(design, [b], "plate", "STEEL PLATE 2.0 GALVANIZED")
    jin = c.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(c.originConstructionPoint))
    jin.zAxisEntity = c.yConstructionAxis          # into the frame, toward the room (joints README)
    jin.xAxisEntity = c.xConstructionAxis          # along the mitre, toward the inner corner
    ref = c.jointOrigins.add(jin)
    ref.name = "JOINT ORIGIN - PLATE (README AXES)"
    PLATES_BUILT[key] = (c, b, ref)
    return PLATES_BUILT[key]


def mitre_plates(design, frame, corners, axis, face, toward_room):
    """The 2 mm plate welded into each mitre (the Joints Engineer's corner detail, D-131; register H-40 to H-42):
    831007 where two 20 x 40 members meet, 831008 where a 20 x 40 meets a 40 x 40, 831009 where two 40 x 40 meet.
    Each placed as the joints README says: its origin on the corner's outer point on the skin-side face, +X along the
    mitre to the inner corner, +Y into the frame toward the room. One component per plate, every copy held by a rigid
    joint to a sketch point at its corner (it follows an edit), turned until its box matches the corner's.
    corners: [(label, outer corner, inner corner, w_rail, w_stile)] in the frame plane's (along, up) expressions;
    axis: the frame plane's normal ('x' side walls, 'y' back walls); face: the skin-side face's coordinate;
    toward_room: +1 or -1 along that axis."""
    import math
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    t, depth, f = ev(design, "plate_t"), ev(design, "tube_d"), ev(design, face)
    placed = []
    for label, o, i, w_r, w_s in corners:
        widths = (round(ev(design, w_r)), round(ev(design, w_s)))
        key = {(20, 20): "plate28", (20, 40): "plate45", (40, 20): "plate45", (40, 40): "plate57"}[widths]
        length = "sqrt((%s) * (%s) + (%s) * (%s))" % (w_r, w_r, w_s, w_s)
        c, _b, ref = plate_part(design, frame, key, length)
        # the part's first copy anywhere under the frame (a STEP import can wrap it one level down), else a new one
        mine = list(frame.allOccurrencesByComponent(c))
        if not mine:
            raise RuntimeError("mitre plate %s has no copy under the frame" % key)
        occ = mine[0] if not any(p[1] == key for p in placed) else frame.occurrences.addExistingComponent(
            c, adsk.core.Matrix3D.create())
        ou, ov, iu, iv = (ev(design, e) for e in (o[0], o[1], i[0], i[1]))
        ln = math.hypot(iu - ou, iv - ov)
        du, dv = (iu - ou) / ln, (iv - ov) / ln
        # the plate's own extents about its README origin (its STEP may stand back from the outer faces, Lead
        # 2026-11-01: a shorter blank whose square edges sit inside the frame's faces), read from its body
        lb = c.bRepBodies.item(0).boundingBox
        ext = [(lb.minPoint.x * 10.0, lb.maxPoint.x * 10.0), (lb.minPoint.y * 10.0, lb.maxPoint.y * 10.0),
               (lb.minPoint.z * 10.0, lb.maxPoint.z * 10.0)]
        pts = []
        for a in ext[0]:
            for b in ext[1]:
                for k in ext[2]:
                    u, v, w = ou + a * du - k * dv, ov + a * dv + k * du, f + toward_room * b
                    pts.append((w, u, v) if axis == "x" else (u, w, v))
        want = [min(q[j] for q in pts) for j in range(3)] + [max(q[j] for q in pts) for j in range(3)]
        # the corner's joint origin: on its outer point on the skin-side face, Z along the frame's depth axis, X
        # along a sketch line from the outer corner to the inner one (the mitre)
        p_o, p_i = sketch_points(design, frame, axis, face, [(o[0], o[1]), (i[0], i[1])], "PLATE PLACE %s" % label)
        mitre_line = p_o.parentSketch.sketchCurves.sketchLines.addByTwoPoints(p_o, p_i)
        if not p_o.parentSketch.isFullyConstrained:
            raise RuntimeError("the mitre line's sketch at %s isn't fully constrained" % label)
        cin = frame.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(p_o))
        cin.zAxisEntity = frame.xConstructionAxis if axis == "x" else frame.yConstructionAxis
        cin.xAxisEntity = mitre_line
        tgt = frame.jointOrigins.add(cin)
        tgt.name = "JOINT ORIGIN - MITRE %s" % label
        def vec(v):
            return "(%.3f, %.3f, %.3f)" % (v.x, v.y, v.z) if v else "?"
        rp = ref.createForAssemblyContext(occ)
        print("PLATE|%s %s: want %s; plate origin axes Z %s X %s; corner axes Z %s X %s" % (
            label, key, [round(x, 2) for x in want], vec(getattr(rp, "primaryAxisVector", None)),
            vec(getattr(rp, "secondaryAxisVector", None)), vec(getattr(tgt, "primaryAxisVector", None)),
            vec(getattr(tgt, "secondaryAxisVector", None))))
        done = False
        # the joint in the root, with the frame's copy as the context: a joint made inside the frame stays where it
        # is (the dry run of 06:45 tried both; only the root's joints placed the plates)
        frame_occ = root_occ(design, frame) if frame != design.rootComponent else None
        for where in ("root",) if frame_occ is not None else ("frame",):
            owner = frame if where == "frame" else design.rootComponent
            g1 = rp if where == "frame" else ref.createForAssemblyContext(occ.createForAssemblyContext(frame_occ))
            g2 = tgt if where == "frame" else tgt.createForAssemblyContext(frame_occ)
            for flip in (False, True):
                for ang in (0.0, 180.0):
                    jin = owner.joints.createInput(g1, g2)
                    jin.setAsRigidJointMotion()
                    jin.angle = vi("%g deg" % ang)
                    jin.isFlipped = flip
                    j = owner.joints.add(jin)
                    got = bbox(occ.bRepBodies.item(0) if where == "frame" else
                               occ.createForAssemblyContext(frame_occ).bRepBodies.item(0))
                    msg = ""
                    try:
                        msg = (j.timelineObject.errorOrWarningMessage or "")[:160] if j.timelineObject else ""
                    except Exception:            # noqa: BLE001  (diagnostics only)
                        msg = "?"
                    ok = j.healthState == healthy and all(abs(x - y) < 0.05 for x, y in zip(got, want))
                    print("PLATE|  %s joint, angle %g, flip %s: health %s %s; box %s%s" % (
                        where, ang, flip, j.healthState, msg, [round(x, 2) for x in got], " FITS" if ok else ""))
                    if ok:
                        j.name = "JOINT - MITRE PLATE %s %s" % (PARTS[key][0], label)
                        done = True
                        break
                    j.deleteMe()
                if done:
                    break
            if done:
                break
        if not done:
            if ARGS.get("dry") == "1":      # a dry run goes on, so the studs, fill copies and hardware get tried too
                print("PLATE|no fit for %s at %s; this dry run goes on without it (the copy stays at the pod "
                      "centre, clear of every part)" % (key, label))
                continue
            raise RuntimeError("mitre plate %s at %s: no joint turn puts it in the mitre %s" % (key, label, want))
        placed.append((label, key))
    print("step 3b: %d mitre plates (%s), each held in its mitre by a joint" % (
        len(placed), ", ".join("%s %s" % (PARTS[k][0], lb) for lb, k in placed)))
    return placed


def side_bays(design):
    """The side frame's bays, (low Y, high Y) expressions: from the front stile to the first stud, between the studs,
    and from the last stud to the 40 x 40 back stile."""
    n = int(round(design.userParameters.itemByName("stile_n_mid").value))
    edges = ["(%s) + tube_w" % Y_FRONT]
    for k in range(1, n + 1):
        edges += ["(%s) + stud_c%d - tube_w / 2" % (Y_FRONT, k), "(%s) + stud_c%d + tube_w / 2" % (Y_FRONT, k)]
    edges.append("(%s) - corner_w" % Y_FRAME_BACK)
    return [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]


def fill_fits(repo_root, code):
    """{bay: how it takes its form's piece} of one position, from WALL's FILL-PIECES.csv (as cut, turned over left
    to right, turned over top to bottom, end for end)."""
    import csv
    with open(os.path.join(repo_root, "v2/03-Manufacturing/wall/FILL-PIECES.csv"), encoding="utf-8") as fh:
        return {int(r["bay"]): r["fit"] for r in csv.DictReader(fh) if r["position"] == code}


def place_piece_copies(design, parent, built, copies, label):
    """Copies of fill pieces whose form an earlier bay of this panel already has (D-120: identical pieces are copies
    of one part). built: {part number: (component, None, (thickness, along, z) expressions of the piece's low
    corner, the wall's along axis 'x' or 'y')}; copies: [(part number, this bay's box (mm), its corners' expressions
    {"low": (thickness, along, z), "high_turned": (...)}, fit, the notch points that must stay open (mm))]. Each copy
    is held by a rigid joint in the root from a joint origin on its part's low corner to one on the matching corner
    of its bay, turned half round about Z when the fit says "turned over left to right" (the piece is the same right
    through its thickness), so it follows an edit. Checked: the copy fills its bay's box and its notches are open."""
    inside = adsk.fusion.PointContainment.PointInsidePointContainment
    refs = {}

    def xyz(corner, along):                # (thickness, along, z) -> pod (x, y, z) expressions
        return (corner[0], corner[1], corner[2]) if along == "y" else (corner[1], corner[0], corner[2])
    for pn, want, corners, fit, open_pts in copies:
        if fit not in ("as cut", "turned over left to right"):
            raise RuntimeError("%s goes in %s: only as cut or turned over left to right are placed so far" % (pn, fit))
        comp, _first_box, low, along = built[pn]
        if pn not in refs:
            refs[pn] = offset_origin(comp, *xyz(low, along), name="JOINT ORIGIN - PIECE %s" % pn)
        tgt_corner = corners["low"] if fit == "as cut" else corners["high_turned"]
        tgt = offset_origin(parent, *xyz(tgt_corner, along), name="JOINT ORIGIN - PIECE %s %s" % (pn, fit.upper()))
        occ = joint_copy(design, parent, comp, refs[pn], tgt, want, "%s %s %s" % (label, pn, fit.upper()),
                         angle="180 deg" if fit != "as cut" else None)
        body = occ.bRepBodies.item(0)
        shut = [pt for pt in open_pts
                if body.pointContainment(adsk.core.Point3D.create(pt[0] / 10.0, pt[1] / 10.0, pt[2] / 10.0)) == inside]
        if shut:
            raise RuntimeError("%s's copy (%s) fills its bay but its notches at %s are closed" % (pn, fit, shut))


def build_fill(design, parent, out, xf, zs):
    """D-120: each bay's piece a numbered part straight in the panel assembly (D-123 cancels the panel's fill number;
    WALL's FILL-PIECES list gives each bay's form and how it goes in): the box of its bay with the notches beside
    every bolt this panel drives that fall in it (FR-10), each cut right through the piece (D-128). A bay whose form
    an earlier bay has takes a copy of that part, as cut or turned round (place_piece_copies)."""
    nums = fill_numbers(ARGS["repo_root"], CODE)
    fits = fill_fits(ARGS["repo_root"], CODE)
    bays = side_bays(design)
    if sorted(nums) != list(range(1, len(bays) + 1)):
        raise RuntimeError("fill numbers for %s cover bays %s; the frame has %d bays" % (CODE, sorted(nums), len(bays)))
    xs = sorted(xf, key=lambda e: ev(design, e))
    pieces, built = [], {}
    for k, yr in enumerate(bays):
        pn = nums[k + 1][0]
        if pn in built:
            pieces.append((None, yr, pn))
            continue
        c = child(parent, *nums[k + 1])[0]
        b = box(design, c, "FILL PIECE BAY %d" % (k + 1), xf, yr, zs).bodies.item(0)
        b.name = "FILL - BAY %d" % (k + 1)
        built[pn] = (c, None, (xs[0], yr[0], zs[0]), "y")
        pieces.append((c, yr, pn))
    pw, z_top = "pocket_w", "(%s) + tube_w" % Z0
    pockets = []
    for i in range(int(round(design.userParameters.itemByName("n_len_bolt").value))):
        yc = "(%s) + bolt_edge + %d * len_bolt_pitch" % (Y_FRONT, i)
        pockets.append(("BOTTOM BOLT %d" % (i + 1), ("(%s) - %s / 2" % (yc, pw), "(%s) + %s / 2" % (yc, pw)),
                        (z_top, "(%s) + %s" % (z_top, pw))))
    for j in range(3):
        zc = "(%s) + bolt_edge + %d * side_jnt_pitch" % (Z0, j)
        pockets.append(("DECOR BOLT %d" % (j + 1), ("(%s) + tube_w" % Y_FRONT, "(%s) + tube_w + %s" % (Y_FRONT, pw)),
                        ("(%s) - %s / 2" % (zc, pw), "(%s) + %s / 2" % (zc, pw))))
    xm = (ev(design, xf[0]) + ev(design, xf[1])) / 2.0
    copy_open = {}
    for label, yr, zr in pockets:
        ym = (ev(design, yr[0]) + ev(design, yr[1])) / 2.0
        hit = [i for i, (_c, (y0, y1), _pn) in enumerate(pieces) if ev(design, y0) < ym < ev(design, y1)]
        if len(hit) != 1:
            raise RuntimeError("fill notch %s falls in %d pieces" % (label, len(hit)))
        c = pieces[hit[0]][0]
        if c is None:              # a copy: its part carries this notch already, as cut or turned
            copy_open.setdefault(hit[0], []).append((xm, ym, (ev(design, zr[0]) + ev(design, zr[1])) / 2.0))
            continue
        box(design, c, "FILL POCKET " + label, xf, yr, zr, "cut", c.bRepBodies.item(0))
    copies = []
    for i, (c, yr, pn) in enumerate(pieces):
        if c is None:
            want = (ev(design, xs[0]), ev(design, yr[0]), ev(design, zs[0]),
                    ev(design, xs[1]), ev(design, yr[1]), ev(design, zs[1]))
            corners = {"low": (xs[0], yr[0], zs[0]), "high_turned": (xs[1], yr[1], zs[0])}
            copies.append((pn, want, corners, fits.get(i + 1, "as cut"), copy_open.get(i, [])))
    place_piece_copies(design, parent, built, copies, "FILL PIECE")
    for c, _yr, _pn in pieces:
        if c is not None:
            b = c.bRepBodies.item(0)
            out[b.name] = b
    print("step 5: fill, %d piece parts in %d bays (%d copies), notches at every bolt this panel drives" % (
        len(built), len(pieces), len(copies)))


def joint_features(design, members, out):
    """Site joint holes per the joints register (V2-ENG-JNT-01 P01), each in its member's own component."""
    xc = sx("pod_w / 2 - skin_t - bond_t - tube_d / 2")     # centre line of the frame depth
    y_b1 = "(%s) + bolt_edge" % Y_FRONT                     # 220 rule on every edge (R-J14)
    n_b, p_b = "n_len_bolt", "len_bolt_pitch"
    t = "tube_t"
    (bc, bot), (tc, top) = members["RAIL - BOTTOM"], members["RAIL - TOP"]
    (fc, front), (kc, back) = members["STILE - FRONT"], members["STILE - BACK"]
    zb0, zb1 = Z0, "(%s) + tube_w" % Z0                      # bottom rail bottom and top faces
    zt1 = Z1                                                 # top rail top face
    # bottom rail: J-BASE-01 (lower) or J-WALL-01 bolt side (upper), both at the 220 rule (FR-02 + FR-03)
    a = hole(design, bc, bot, "z", zb0, +1, {"x": xc, "y": y_b1}, "bolt_d", t, "BOTTOM RAIL BOLT CLEARANCE 1")
    b = hole(design, bc, bc.bRepBodies.item(0), "z", zb1, -1, {"x": xc, "y": y_b1}, "access_d", t,
             "BOTTOM RAIL KEY ACCESS 1")
    pattern_feat(bc, [a, b], "y", n_b, p_b, "BOTTOM RAIL BOLT HOLES")
    # bottom rail locating: round spigot hole at the front end, slot along X at the back-corner end (FR-05)
    hole(design, bc, bc.bRepBodies.item(0), "z", zb0, +1, {"x": xc, "y": "(%s) + spigot_edge" % Y_FRONT}, "spigot_d",
         t, "BOTTOM RAIL SPIGOT ROUND")
    ys = "(%s) - spigot_edge" % Y_BACK
    half = "(spigot_slot - spigot_d) / 2"
    box(design, bc, "BOTTOM RAIL SPIGOT SLOT", ("(%s) - %s" % (xc, half), "(%s) + %s" % (xc, half)),
        ("(%s) - spigot_d / 2" % ys, "(%s) + spigot_d / 2" % ys), (zb0, "(%s) + %s" % (zb0, t)), "cut",
        bc.bRepBodies.item(0))
    for i, sgn in enumerate(("-", "+")):
        hole(design, bc, bc.bRepBodies.item(0), "z", zb0, +1, {"x": "(%s) %s %s" % (xc, sgn, half), "y": ys},
             "spigot_d", t, "BOTTOM RAIL SPIGOT SLOT END %d" % (i + 1))
    if ROW == 1:
        # the cassette ledge's rivet holes (the Lead's ruling of 2026-11-01): through the bottom rail's room-side
        # wall at its mid-height, made after welding (J-FRAME-01); the ledge's own holes match them (build_ledge)
        pl = {"y": "%s + ledge_rivet_e" % LEDGE_Y0, "z": "(%s) + ledge_rivet_z" % Z0}
        r = hole(design, bc, bc.bRepBodies.item(0), "x", X_FRAME_IN, S, pl, "ledge_rivet_d", t,
                 "BOTTOM RAIL LEDGE RIVET 1")
        pattern_feat(bc, [r], "y", "ledge_rivet_n", "ledge_rivet_pitch", "BOTTOM RAIL LEDGE RIVETS")
        hw_site("BOTTOM RAIL LEDGE RIVET", "x", X_FRAME_IN, S, pl, ("y", "ledge_rivet_n", "ledge_rivet_pitch"),
                washer=False, member="RAIL - BOTTOM", kind="rivet")
        # top rail, nut side of J-WALL-01: rivnut at each bay (FR-01) and 2 spigot rivnuts (FR-04)
        r = hole(design, tc, top, "z", zt1, -1, {"x": xc, "y": y_b1}, "rivnut_d", t, "TOP RAIL RIVNUT 1")
        pattern_feat(tc, [r], "y", n_b, p_b, "TOP RAIL RIVNUTS")
        hw_site("TOP RAIL", "z", zt1, -1, {"x": xc, "y": y_b1}, ("y", n_b, p_b), member="RAIL - TOP")
        for k, ys_ in (("FRONT", "(%s) + spigot_edge" % Y_FRONT), ("BACK", "(%s) - spigot_edge" % Y_BACK)):
            hole(design, tc, tc.bRepBodies.item(0), "z", zt1, -1, {"x": xc, "y": ys_}, "rivnut_d", t,
                 "TOP RAIL SPIGOT RIVNUT %s" % k)
            hw_site("TOP RAIL SPIGOT %s" % k, "z", zt1, -1, {"x": xc, "y": ys_}, washer=False, spigot=True,
                    member="RAIL - TOP")
    if ROW == 2:
        # 40 x 40 top member, nut side of J-CEIL-01 side edges: a rivnut in its room-side face at each bay middle;
        # positions follow the ceiling's edge, not this panel's: from Y -645 at pitch 351.67 (PM ruling 16:55)
        y_c1 = "(%s) + bolt_edge" % Y_CASS_FRONT
        r = hole(design, tc, top, "x", X_FRAME_IN, S, {"y": y_c1, "z": "pod_h - ceil_bolt_dz"}, "rivnut_d", t,
                 "TOP MEMBER CEILING RIVNUT 1")
        pattern_feat(tc, [r], "y", n_b, "ceil_bolt_pitch", "TOP MEMBER CEILING RIVNUTS")
        hw_site("TOP MEMBER CEILING", "x", X_FRAME_IN, S, {"y": y_c1, "z": "pod_h - ceil_bolt_dz"},
                ("y", n_b, "ceil_bolt_pitch"), member="RAIL - TOP")
    z_j1 = "(%s) + bolt_edge" % Z0
    # front stile, bolt side of J-FRONT-01 (decor block): FR-02 in the front wall, FR-03 in the back wall
    a = hole(design, fc, front, "y", Y_FRONT, +1, {"x": xc, "z": z_j1}, "bolt_d", t, "FRONT STILE BOLT CLEARANCE 1")
    b = hole(design, fc, fc.bRepBodies.item(0), "y", "(%s) + tube_w" % Y_FRONT, -1, {"x": xc, "z": z_j1}, "access_d",
             t, "FRONT STILE KEY ACCESS 1")
    pattern_feat(fc, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "FRONT STILE BOLT HOLES")
    # 40 x 40 back stile, nut side of J-WALL-02 (back corner): rivnut in the room-side face (FR-01, FR-06)
    r = hole(design, kc, back, "x", X_FRAME_IN, S, {"y": "bolt_line_y", "z": "corner_z0 + bolt_edge"},
             "rivnut_d", t, "BACK STILE CORNER RIVNUT 1")
    pattern_feat(kc, [r], "z", "n_side_jnt", "corner_bolt_pitch", "BACK STILE CORNER RIVNUTS")
    hw_site("BACK STILE CORNER", "x", X_FRAME_IN, S, {"y": "bolt_line_y", "z": "corner_z0 + bolt_edge"},
            ("z", "n_side_jnt", "corner_bolt_pitch"), member="STILE - BACK")
    for key, (c, _b) in list(members.items()):
        members[key] = (c, c.bRepBodies.item(0))
        out[key] = c.bRepBodies.item(0)
    print("step 6: joint features: %d hole features (before patterns)" % sum(
        c.features.holeFeatures.count for c, _b in members.values()))


# ---------------------------------------------------------------- hardware as copies of one component per part

HW_PARTS_BUILT = {}


# Joints' own STEPs of the shared parts (one source, as D-95 for the keys; F-189), placed as they are. Their
# origins (v2/01-CAD-Native/joints/README.md): the spigot's on its axis at the top of its rivnut's head, +Z up the
# pin; the washer's on its axis at its bottom face, +Z through its 1.5.
JOINTS_STEP = {"spigot": "v2/03-Manufacturing/joints/831001_P01_HARDWARE-LOCATING-SPIGOT_STEP.step",
               "stopw": "v2/03-Manufacturing/joints/831002_P01_HARDWARE-STOP-WASHER_STEP.step"}
JOINTS_BODY = {"spigot": "SPIGOT", "stopw": "STOP WASHER"}


def import_joints_part(design, root, key):
    """Joints' STEP of a shared part imported once into the root as its own component, renamed with the
    register's number and name; its one body keeps Joints' shape, origin and axes. Returns (component, body)."""
    app = adsk.core.Application.get()
    path = os.path.join(ARGS["repo_root"], JOINTS_STEP[key])
    if not os.path.isfile(path):
        raise RuntimeError("Joints' STEP %s is missing" % JOINTS_STEP[key])
    n0 = root.occurrences.count
    opts = app.importManager.createSTEPImportOptions(path)
    opts.isViewFit = False
    if not app.importManager.importToTarget(opts, root):
        raise RuntimeError("could not import %s" % JOINTS_STEP[key])
    new = [root.occurrences.item(i) for i in range(n0, root.occurrences.count)]
    if len(new) != 1:
        raise RuntimeError("importing %s added %d occurrences, not 1" % (JOINTS_STEP[key], len(new)))
    occ = new[0]
    c = occ.component
    while c.bRepBodies.count == 0 and c.occurrences.count == 1:      # a STEP product wrapped in an assembly
        c = c.occurrences.item(0).component
    if c.bRepBodies.count != 1:
        raise RuntimeError("%s holds %d bodies, not 1" % (JOINTS_STEP[key], c.bRepBodies.count))
    m = occ.transform2
    if any(abs(m.getCell(r, k) - (1.0 if r == k else 0.0)) > 1e-9 for r in range(4) for k in range(4)):
        raise RuntimeError("%s came in moved; Joints' origin is the joint datum" % JOINTS_STEP[key])
    pn, name, vn = PARTS[key]
    c.name = "%s %s" % (pn, name)
    c.partNumber = pn
    c.description = "%s | %s | %s | Joints' STEP %s" % (name, vn, REV, os.path.basename(JOINTS_STEP[key]))
    b = c.bRepBodies.item(0)
    b.name = JOINTS_BODY[key]
    # a STEP brings no material, so Fusion gives the body its default steel: the part's own material, for its mass
    # (the L1 sample of 10:0x weighed the aluminium stop washer as steel, 2.7 g, not 0.92)
    dk, label = {"stopw": ("stopw", "ALUMINIUM STOP WASHER"), "spigot": ("spigot", "STAINLESS SPIGOT")}.get(
        key, ("plate", "STEEL PLATE 2.0 GALVANIZED"))
    set_material(design, [b], dk, label)
    return c, b


def hw_part(design, root, key):
    """One component per hardware part (D-120), placed by joints. The spigot 831001 and the stop washer 831002
    are Joints' own STEPs (one source, F-189); the rivnut 838003 is WALL's envelope of the Sherex part (no maker
    model in the repo): its head from Z 0 up, its body down (Z 0 = the underside of the head). Every copy is
    placed by a rigid joint (or a pattern of jointed copies), so it follows its hole on an edit. Returns
    (component, body, the joint circle's diameter expression)."""
    if key in HW_PARTS_BUILT:
        return HW_PARTS_BUILT[key]
    if key in JOINTS_STEP:
        c, b = import_joints_part(design, root, key)
        ring = {"stopw": "stopw_od", "spigot": "spigot_pin_d"}[key]
    elif key == "rivet":
        # the ledge's blind rivet as its set envelope (HOLD until Joints picks it): the head from Z 0 up, the body
        # down through the ledge and the rail's wall (Z 0 = the underside of the head, on the ledge)
        c = new_comp(root, key)
        o = {"x": "0 mm", "y": "0 mm"}
        head = cyl(design, c, "RIVET HEAD", "z", "0 mm", +1, o, "rivet_head_d", "rivet_head_t")
        shank = cyl(design, c, "RIVET BODY", "z", "0 mm", -1, o, "rivet_d", "rivet_len")
        b = join_bodies(c, head, [shank], "RIVET")
        b.name, ring = "BLIND RIVET", "rivet_head_d"
        set_material(design, [b], key, "STEEL ZINC BLIND RIVET (HOLD)")
    else:
        c = new_comp(root, key)
        o = {"x": "0 mm", "y": "0 mm"}
        head = cyl(design, c, "RIVNUT HEAD", "z", "0 mm", +1, o, "rivnut_head_d", "rivnut_head_t", "m6_d")
        shank = cyl(design, c, "RIVNUT BODY", "z", "0 mm", -1, o, "rivnut_body_d", "rivnut_len", "m6_d")
        b = join_bodies(c, head, [shank], "RIVNUT")
        b.name, ring = "RIVNUT", "rivnut_head_d"
        set_material(design, [b], key, "STEEL ZINC RIVNUT")
    HW_PARTS_BUILT[key] = (c, b, ring)
    return HW_PARTS_BUILT[key]


def circle_edge(body, dia_mm, centre=None, axis=None):
    """A circular edge of `body` (any context) of diameter dia_mm; with `centre` ({axis: mm, ...}), the one whose
    centre matches it within 0.05 mm."""
    found = []
    for e in body.edges:
        g = e.geometry
        if g.objectType == adsk.core.Circle3D.classType():
            cg = adsk.core.Circle3D.cast(g)
        elif g.objectType == adsk.core.Arc3D.classType():       # an imported circle split in two arcs
            cg = adsk.core.Arc3D.cast(g)
        else:
            continue
        if abs(cg.radius * 20.0 - dia_mm) > 0.02:
            continue
        p = {"x": cg.center.x * 10.0, "y": cg.center.y * 10.0, "z": cg.center.z * 10.0}
        if centre is None or all(abs(p[a] - v) < 0.05 for a, v in centre.items()):
            found.append(e)
    return found


OUTWARD = {"stopw": "stopw_t", "rivnut": "rivnut_head_t", "spigot": "spigot_proud - rivnut_head_t",
           "rivet": "rivet_head_t"}


def place_one(design, root, key, site, offset_expr, member_body_proxy, hole_d):
    """A copy of hardware part `key` held in its hole by a rigid joint: the part's joint circle (its Z 0) centred
    on the hole's edge on the joint face, `offset_expr` out along the hole's axis, the part's +Z pointing out of
    the tube. Tries the joint's flip and the offset's sign, and keeps the one that lands so (checked by where the
    copy's outward end sits)."""
    c, b, ring = hw_part(design, root, key)
    ax, face, out_dir = site["axis"], ev(design, site["face"]), site["out"]
    centre = {a: ev(design, e) for a, e in site["pos"].items()}
    centre[ax] = face
    holes = circle_edge(member_body_proxy, hole_d, centre)
    if len(holes) != 1:
        raise RuntimeError("%s: %d hole edges of %.2f at %s" % (site["label"], len(holes), hole_d, centre))
    if key not in PLACED_KEYS:                 # the copy hw_part made first, at the origin, is the first placed
        occ = root_occ(design, c)
        PLACED_KEYS.add(key)
    else:
        occ = root.occurrences.addExistingComponent(c, adsk.core.Matrix3D.create())
    ring_edges = circle_edge(b, ev(design, ring), {"x": 0.0, "y": 0.0, "z": 0.0})
    if not ring_edges:
        raise RuntimeError("%s: no joint circle on the part" % key)
    k = "xyz".index(ax)
    off = ev(design, offset_expr)
    z0 = face + off * out_dir                  # where the part's Z 0 must land along the hole's axis
    reach = ev(design, OUTWARD[key])           # how far the part stands out past its Z 0
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    for flip in (False, True):
        for sign in ((1, -1) if off > 1e-9 else (1,)):
            g1 = adsk.fusion.JointGeometry.createByCurve(ring_edges[0].createForAssemblyContext(occ),
                                                         adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
            g2 = adsk.fusion.JointGeometry.createByCurve(holes[0], adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
            jin = root.joints.createInput(g1, g2)
            jin.setAsRigidJointMotion()
            jin.isFlipped = flip
            if off > 1e-9:
                jin.offset = vi(offset_expr if sign > 0 else "-(%s)" % offset_expr)
            j = root.joints.add(jin)
            bb = bbox(occ.bRepBodies.item(0))
            outer = bb[k + 3] if out_dir > 0 else bb[k]
            if j.healthState == healthy and abs((outer - z0) * out_dir - reach) < 0.05:
                j.name = "JOINT - %s - %s" % (key.upper(), site["label"])
                return occ
            j.deleteMe()
    raise RuntimeError("%s %s: no joint flip or offset sign puts the part in its hole the right way" % (
        key, site["label"]))


PLACED_KEYS = set()


def place_hardware(design, root, members, out):
    """The joint hardware the panel carries from the factory (joints register 2.1; sizes H-03, H-05, H-08), as
    copies of one component per part (D-120): at every rivnut hole an H-03 rivnut, with an H-08 stop washer under
    its head at a stopped joint, and an H-05 spigot in each spigot rivnut. The first copy of each site is held in
    its hole by a rigid joint; a patterned site's other copies are a pattern of those, like its holes, so an edit
    moves them with the holes. The bolts stay in the parts list (bought, ISO)."""
    if not HW_SITES:
        return
    n_occ = 0
    for s in HW_SITES:
        mc, _mb = members[s["member"]]
        mo = root_occ(design, mc)
        proxy = mc.bRepBodies.item(0).createForAssemblyContext(mo)
        hd = ev(design, "rivnut_d")
        seeds = []
        if s.get("kind") == "rivet":
            seeds.append(place_one(design, root, "rivet", s, "ledge_t", proxy, ev(design, "ledge_rivet_d")))
        elif s["washer"]:
            seeds.append(place_one(design, root, "stopw", s, "0 mm", proxy, hd))
        if s.get("kind") != "rivet":
            seeds.append(place_one(design, root, "rivnut", s, "stopw_t" if s["washer"] else "0 mm", proxy, hd))
        if s["spigot"]:
            seeds.append(place_one(design, root, "spigot", s,
                                   "stopw_t + rivnut_head_t" if s["washer"] else "rivnut_head_t", proxy, hd))
        n_occ += len(seeds)
        if s["pat"]:
            pax, cnt, pitch = s["pat"]
            coll = adsk.core.ObjectCollection.create()
            for o in seeds:
                coll.add(o)
            axis = {"x": root.xConstructionAxis, "y": root.yConstructionAxis, "z": root.zConstructionAxis}[pax]
            pin = root.features.rectangularPatternFeatures.createInput(
                coll, axis, vi(cnt), vi(pitch), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
            other = root.zConstructionAxis if pax != "z" else root.yConstructionAxis
            pin.setDirectionTwo(other, vi("1"), vi("1 mm"))
            p = root.features.rectangularPatternFeatures.add(pin)
            p.name = "PATTERN - HARDWARE COPIES - %s" % s["label"]
            n = int(cnt) if cnt.isdigit() else int(round(design.userParameters.itemByName(cnt).value))
            n_occ += len(seeds) * (n - 1)
    for key, (c, b, _r) in HW_PARTS_BUILT.items():
        out["%s - %s" % (c.partNumber, b.name)] = b
    print("step 7: joint hardware, %d copies of %d parts (%s), each held in its hole by a joint or a pattern" % (
        n_occ, len(HW_PARTS_BUILT), ", ".join(c.partNumber for c, _b, _r in HW_PARTS_BUILT.values())))


def assembly_bodies(design):
    """Every solid body in the assembly as placed, one entry per copy: {path / body name: (body, occurrence)}
    (the occurrence is None for a body of the root itself)."""
    out = {}
    root = design.rootComponent
    for b in root.bRepBodies:
        out["%s / %s" % (root.partNumber, b.name)] = (b, None)
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out["%s / %s" % (occ.fullPathName, b.name)] = (b, occ)
    return out


def state_name(state):
    """Fusion's name for a timeline item's health state."""
    h = adsk.fusion.FeatureHealthStates
    return {h.HealthyFeatureHealthState: "healthy", h.WarningFeatureHealthState: "warning",
            h.ErrorFeatureHealthState: "error", h.SuppressedFeatureHealthState: "suppressed",
            h.RolledBackFeatureHealthState: "rolled back", h.UnknownFeatureHealthState: "unknown"}.get(state, str(state))


def placed_clashes(placed):
    """Pairwise solid overlaps over 1 mm3 between every placed copy (each copy moved by its occurrence's
    transform); the overlaps allowed_overlap() names are by design. Returns (hits, unexpected)."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    items = list(placed.items())
    boxes = [bbox(b) for _n, (b, _o) in items]
    hits, bad = [], []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            ba, bb_ = boxes[i], boxes[j]
            if not all(ba[k] < bb_[k + 3] - 1e-6 and bb_[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            tmp = []
            for _n, (b, o) in (items[i], items[j]):
                t = tbm.copy(b.nativeObject if b.nativeObject else b)
                if o is not None:
                    tbm.transform(t, o.transform2)
                tmp.append(t)
            tbm.booleanOperation(tmp[0], tmp[1], adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = tmp[0].volume * 1000.0 if tmp[0] else 0.0
            if vol > 1.0:
                hits.append((items[i][0], items[j][0], round(vol)))
                if not allowed_overlap(items[i][0], items[j][0]):
                    bad.append(hits[-1])
    return hits, bad


def allowed_overlap(na, nb):
    """Overlaps by design: a spigot's thread in its rivnut's bore (838003 with 831001), and any pair listed in
    ALLOWED_CLASH (the back builder's hardware bodies)."""
    def part(n):             # the part number of the copy: the first word of the last occurrence on its path
        return n.split(" / ")[0].split("+")[-1].split(" ")[0]
    if {part(na), part(nb)} == {"838003", "831001"}:
        return True
    names = {frozenset(p) for p in ALLOWED_CLASH}
    return frozenset((na.split(" / ")[-1], nb.split(" / ")[-1])) in names


def build_skin(design, skin, out):
    yskin = (Y_FRONT, Y_BACK)
    zskin = (Z_SKIN0, Z_SKIN1)
    plate = box(design, skin, "SKIN PLATE", (X_OUT, X_SKIN_IN), yskin, zskin).bodies.item(0)
    box(design, skin, "SKIN BACK RETURN", (X_SKIN_IN, sx("pod_w / 2 - skin_t - skin_ret")),
        (Y_RETURN_IN, Y_BACK), zskin, "join", plate)
    # the fold's outside radius (skin_fold_r, the maker's guide 4.5): a constant-radius fillet on the outer corner
    # edge, where the main face meets the return's outer face; the inside of the fold is the closed V-groove
    xo, yb = ev(design, X_OUT) / 10.0, ev(design, Y_BACK) / 10.0          # the API's cm
    edges = [e for e in plate.edges if e.geometry.objectType == adsk.core.Line3D.classType() and all(
        abs(v.geometry.x - xo) < 1e-5 and abs(v.geometry.y - yb) < 1e-5 for v in (e.startVertex, e.endVertex))]
    if len(edges) != 1:
        raise RuntimeError("the skin's outer fold edge: %d found at X %.2f, Y %.2f, not 1" % (
            len(edges), xo * 10.0, yb * 10.0))
    oc = adsk.core.ObjectCollection.create()
    oc.add(edges[0])
    fin = skin.features.filletFeatures.createInput()
    fin.edgeSetInputs.addConstantRadiusEdgeSet(oc, adsk.core.ValueInput.createByString("skin_fold_r"), False)
    fil = skin.features.filletFeatures.add(fin)
    fil.name = "FILLET - FOLD OUTSIDE RADIUS (MAKER'S GUIDE 4.5)"
    plate.name = "SKIN - ACP 3 WITH BACK RETURN"
    out[plate.name] = plate
    print("step 4: skin", size(bbox(plate)), "with its fold's outside radius %.1f" % ev(design, "skin_fold_r"))


def build_tray(design, root, tray, yc, zc):
    """Sheet metal tray, the ceiling tray's recipe (v2/01-CAD-Native/ceiling): base flange on the plane of the
    tray back, returns tray_h deep toward the room, 12 mm lips turned in to hold the felt. Edge flanges need the
    sheet metal component active. Bend position and lip direction are tried both ways and kept only when the
    outer faces land on the cassette outline."""
    rule = design.designSheetMetalRules.itemByName("GALV STEEL 0.5 - LINING TRAY")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(tray.activeSheetMetalRule, "GALV STEEL 0.5 - LINING TRAY")
    rule.thickness.expression = "%.4f mm" % ev(design, "tray_t")   # a rule takes values only (Fusion 2706)
    rule.bendRadius.expression = "Thickness"                        # = bend_r (1 x t)
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    tray.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == tray][0]
    occ.activate()
    want_yz = [ev(design, e) for e in (span(design, *yc) + span(design, *zc))]
    xb = ev(design, X_TRAY_BACK)
    try:
        sk = rect_on_x(design, tray, X_TRAY_BACK, yc, zc, "TRAY BASE OUTLINE")
        ff = tray.features.flangeFeatures
        base = None
        for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                       adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
            bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
            bfi.orientation = orient
            f = ff.add(bfi)
            b = bbox(f.bodies.item(0))
            back, room = (b[0], b[3]) if S < 0 else (b[3], b[0])     # the room is toward -S
            if abs(back - xb) < 0.01 and abs(room - (xb - S * ev(design, "tray_t"))) < 0.01:
                base = f
                break
            f.deleteMe()
        if base is None:
            raise RuntimeError("tray: no base flange side lies on the room side of the tray back")
        base.name = "BASE - TRAY"
        body = tray.bRepBodies.item(0)
        body.name = "TRAY - STEEL 0.5 WITH RETURNS AND LIPS"
        xr = xb - S * ev(design, "tray_t")      # room-side face of the base (the room is toward -S)

        def x_edges(x, keep):
            return [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
                    and abs(e.startVertex.geometry.x * 10 - x) < 0.01 and abs(e.endVertex.geometry.x * 10 - x) < 0.01
                    and keep(e)]
        eds = x_edges(xr, lambda e: True)
        if len(eds) != 4:
            raise RuntimeError("tray: expected 4 base edges on the room side, got %d" % len(eds))
        ret = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType,
                    adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            efi = ff.createEdgeFlangeInput([], vi("tray_h - tray_t - bend_r"))
            for e in eds:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            efi.bendPositionType = pos
            f = ff.add(efi)
            b = bbox(tray.bRepBodies.item(0))
            if all(abs(g - w) < 0.05 for g, w in zip([b[1], b[4], b[2], b[5]], want_yz)):
                ret = f
                break
            f.deleteMe()
        if ret is None:
            raise RuntimeError("tray: no bend position keeps the returns' outer faces on the outline")
        ret.name = "FLANGE - TRAY RETURNS"
        body = tray.bRepBodies.item(0)
        b = bbox(body)
        xt = b[3] if S < 0 else b[0]         # the returns' tips, at the room side

        def off_outline(e):
            q = e.startVertex.geometry
            return min(abs(q.y * 10 - b[1]), abs(q.y * 10 - b[4]), abs(q.z * 10 - b[2]), abs(q.z * 10 - b[5])) > 0.05 \
                and e.length * 10 > 100
        inner = x_edges(xt, off_outline)
        if len(inner) != 4:
            raise RuntimeError("tray: expected 4 inner tip edges, got %d" % len(inner))
        lip = None
        x_room = ev(design, X_IN)
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput([], vi("lip_w"))
            for e in inner:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = bbox(tray.bRepBodies.item(0))
            room = b2[3] if S < 0 else b2[0]
            inside = all(abs(g - w) < 0.05 for g, w in zip([b2[1], b2[4], b2[2], b2[5]], want_yz)) and \
                abs(room - x_room) < 0.05
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("tray: no lip direction keeps the lips inside the outline at the room face")
        lip.name = "FLANGE - TRAY LIPS HOLDING THE FELT"
        body = tray.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(adsk.core.Plane.cast(fc.geometry).normal.x) > 0.99), key=lambda fc: fc.area)
        fp = tray.flatPattern or tray.createFlatPattern(big)
        print("FLAT|%s|%s" % (tray.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    return tray.bRepBodies.item(0)


def build_ledge(design, root, out):
    """The cassette ledge (the Lead's ruling of 2026-11-01: a wall cassette's weight sits on a ledge, not on clip
    shear): a 1.0 galvanized steel angle in sheet metal, its upright on the bottom rail's room face (riveted through
    the rail's LEDGE RIVET holes, after welding), its leg ledge_pad_t under the frame's bottom and reaching ledge_out
    toward the room, under the tray's bottom return; the pad on the leg fills the 2.26 to the cassette, so the lining
    doesn't move. One part for L1 and R1 (ledge_front_dy, a symmetric rivet pattern). The bend and the leg's side are
    tried both ways and kept only when the outer faces land on the ledge's outline."""
    unnumbered = [k for k in ("ledge", "pad", "rivet") if not LEDGE_PN[k] and ARGS.get("dry") != "1"]
    if unnumbered:
        raise RuntimeError("the cassette ledge's %s has no number yet (Control posts it in WALL's group): only a "
                           "dry run builds it" % ", ".join(unnumbered))
    ledge = new_comp(root, "ledge", sheet_metal=True)
    rule = design.designSheetMetalRules.itemByName("GALV STEEL 1.0 - CASSETTE LEDGE")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(ledge.activeSheetMetalRule, "GALV STEEL 1.0 - CASSETTE LEDGE")
    rule.thickness.expression = "%.4f mm" % ev(design, "ledge_t")   # a rule takes values only (Fusion 2706)
    rule.bendRadius.expression = "Thickness"                         # = ledge_r (1 x t)
    rule.kFactor = 0.44
    ledge.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == ledge][0]
    occ.activate()
    yr = (LEDGE_Y0, "%s + ledge_len" % LEDGE_Y0)
    zr = ("(%s) - ledge_pad_t - ledge_t" % Z0, "(%s) + ledge_up" % Z0)
    want_y = sorted(ev(design, e) for e in yr)
    want_z = sorted(ev(design, e) for e in zr)
    xf, t = ev(design, X_FRAME_IN), ev(design, "ledge_t")
    want_x = sorted((xf, ev(design, sx("pod_w / 2 - outer_t - ledge_out"))))
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    try:
        sk = rect_on_x(design, ledge, X_FRAME_IN, yr, zr, "LEDGE UPRIGHT OUTLINE")
        ff = ledge.features.flangeFeatures
        base = None
        for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                       adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
            bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
            bfi.orientation = orient
            f = ff.add(bfi)
            b = bbox(f.bodies.item(0))
            back, room = (b[0], b[3]) if S < 0 else (b[3], b[0])     # the room is toward -S
            if abs(back - xf) < 0.01 and abs(room - (xf - S * t)) < 0.01:
                base = f
                break
            f.deleteMe()
        if base is None:
            raise RuntimeError("ledge: no base flange side lies on the room side of the rail's face")
        base.name = "BASE - LEDGE UPRIGHT ON THE BOTTOM RAIL"
        body = ledge.bRepBodies.item(0)
        xr = xf - S * t                       # the upright's room-side face
        eds = [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
               and all(abs(v.geometry.x * 10 - xr) < 0.01 and abs(v.geometry.z * 10 - want_z[0]) < 0.01
                       for v in (e.startVertex, e.endVertex))]
        if len(eds) != 1:
            raise RuntimeError("ledge: expected 1 bottom edge on the upright's room face, got %d" % len(eds))
        leg = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType,
                    adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            for flip in (False, True):
                # outer-faces datum: the height runs from the upright's outer (frame-side) face to the leg's tip,
                # so it is the leg's whole reach (probe of 2026-11-01: 26 gave the tip at 26; Inside keeps the bottom)
                efi = ff.createEdgeFlangeInput([], vi("ledge_out"))
                efi.edgeDefinitions.addFullLengthEdge(eds[0])
                efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
                efi.bendPositionType = pos
                efi.isFlipped = flip
                f = ff.add(efi)
                b = bbox(ledge.bRepBodies.item(0))
                fits = all(abs(g - w) < 0.05 for g, w in zip((b[0], b[3], b[1], b[4], b[2], b[5]),
                                                             want_x + want_y + want_z))
                if fits and f.healthState == healthy:
                    leg = f
                    break
                f.deleteMe()
            if leg:
                break
        if leg is None:
            raise RuntimeError("ledge: no bend position or side keeps the leg's outer faces on the outline")
        leg.name = "FLANGE - LEDGE LEG UNDER THE CASSETTE"
        body = ledge.bRepBodies.item(0)
        body.name = "LEDGE - STEEL 1.0 ANGLE UNDER THE CASSETTE"
        pl = {"y": "%s + ledge_rivet_e" % LEDGE_Y0, "z": "(%s) + ledge_rivet_z" % Z0}
        h = hole(design, ledge, body, "x", X_FRAME_IN, -S, pl, "ledge_rivet_d", "ledge_t", "LEDGE RIVET HOLE 1")
        pattern_feat(ledge, [h], "y", "ledge_rivet_n", "ledge_rivet_pitch", "LEDGE RIVET HOLES")
        body = ledge.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(adsk.core.Plane.cast(fc.geometry).normal.x) > 0.99), key=lambda fc: fc.area)
        fp = ledge.flatPattern or ledge.createFlatPattern(big)
        print("FLAT|%s|%s" % (ledge.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    body = ledge.bRepBodies.item(0)
    set_material(design, [body], "ledge", "GALVANIZED STEEL 1.0")
    out[body.name] = body
    # the pad on the leg's flat, from 0.5 past the bend to ledge_pad_w, the cassette's bottom on its top (Z0)
    pad = new_comp(root, "pad")
    px = (sx("pod_w / 2 - outer_t - ledge_t - ledge_r - 0.5 mm"),
          sx("pod_w / 2 - outer_t - ledge_t - ledge_r - 0.5 mm - ledge_pad_w"))
    pb = box(design, pad, "LEDGE PAD", px, yr, ("(%s) - ledge_pad_t" % Z0, Z0)).bodies.item(0)
    pb.name = "PAD - ON THE LEDGE UNDER THE CASSETTE (HOLD)"
    set_material(design, [pb], "pad", "SOFT PAD (HOLD)")
    out[pb.name] = pb
    print("step 6b: cassette ledge %s, %s long, its leg at Z %.2f, with the pad (%s) and %d rivet holes" % (
        ledge.partNumber, "%.2f" % (want_y[1] - want_y[0]), want_z[0] + t, pad.partNumber,
        int(round(design.userParameters.itemByName("ledge_rivet_n").value))))


def el_inside(design, label, lo_hi, keep):
    """Refuse an ELECTRICAL feature that would not lie wholly inside its part (a skeleton or ELECTRICAL change
    moved one of them): [(feature low, feature high, part low, part high), ...] per axis, `keep` mm of part
    left round it."""
    for f0, f1, p0, p1 in lo_hi:
        a, b, c, d = (ev(design, e) for e in (f0, f1, p0, p1))
        if min(a, b) < min(c, d) + keep - 1e-6 or max(a, b) > max(c, d) - keep + 1e-6:
            raise RuntimeError("%s (%.2f to %.2f) does not lie inside its part (%.2f to %.2f) with %g mm round it" % (
                label, min(a, b), max(a, b), min(c, d), max(c, d), keep))


def el_felt_cuts(design, felt, fb, yc, zc):
    """ELECTRICAL's felt-only openings in the right linings (R1-CASS, R2-CASS; EL_PARAMS): through the 9 mm felt
    from its room face. No steel is there: the tray's lips are only at its edges, so no bushing; the felt hole
    is the whole feature (ELECTRICAL's model, note on felt holes)."""
    if CODE not in ("R1", "R2"):
        return fb
    fy = ("(%s) + tray_t + felt_c" % yc[0], "(%s) - tray_t - felt_c" % yc[1])
    fz = ("(%s) + tray_t + felt_c" % zc[0], "(%s) - tray_t - felt_c" % zc[1])
    holes = []
    if CODE == "R1":
        sy = ("pod_d / 2 - stack_t + el_fs_y0", "pod_d / 2 - stack_t + el_fs_y1")
        sz = ("el_trunk_z - el_fs_dz", "el_trunk_z + el_fs_dz")
        el_inside(design, "FS-CNR", [(sy[0], sy[1], fy[0], fy[1]), (sz[0], sz[1], fz[0], fz[1])], 1.0)
        box(design, felt, "FELT SLOT FS-CNR", (sx("pod_w / 2 - stack_t"), sx("pod_w / 2 - stack_t + tray_t + felt_t + 1 mm")),
            sy, sz, "cut", fb)
        fb = felt.bRepBodies.item(0)
        holes = [("FA-KIT VOICE KIT ACCESS", "el_y_kit", "el_trunk_z + el_kit_dz", "el_kit_d"),
                 ("FX-COL EXIT INTO THE AIR COLUMN", "el_y_cx", "el_trunk_z", "el_grm_d")]
    else:
        holes = [("FX-CALL0 CALL LIGHT FEED BEHIND THE SHELF", "el_call_y", "el_shelf_z", "el_grm_s"),
                 ("FX-CALL2 CALL LIGHT EXIT", "el_call_y", "el_call_z", "el_grm_s")]
    for label, y, z, d in holes:
        el_inside(design, label.split()[0], [("(%s) - (%s) / 2" % (y, d), "(%s) + (%s) / 2" % (y, d), fy[0], fy[1]),
                                             ("(%s) - (%s) / 2" % (z, d), "(%s) + (%s) / 2" % (z, d), fz[0], fz[1])], 1.0)
        hole(design, felt, fb, "x", X_FELT_FACE, S, {"y": y, "z": z}, d, "felt_t + 1 mm", "FELT " + label)
        fb = felt.bRepBodies.item(0)
    if felt.bRepBodies.count != 1:
        raise RuntimeError("the felt split into %d bodies at ELECTRICAL's openings" % felt.bRepBodies.count)
    print("step 3b: ELECTRICAL felt openings in %s: %s" % (CODE, ", ".join(h[0].split()[0] for h in holes) +
                                                           (", FS-CNR" if CODE == "R1" else "")))
    return fb


def build_cassette(design, root):
    out = {}
    want = WANT[PART]
    tray = new_comp(root, "tray", sheet_metal=True) if "tray" in want else None
    felt = new_comp(root, "felt") if "felt" in want else None
    clip = new_comp(root, "clip") if "clip" in want else None
    print("step 1: components %s" % ", ".join(c.name for c in (root, tray, felt, clip) if c))
    if STOP_AFTER <= 1:
        return out
    yc = (Y_LIN_FRONT, Y_CASS_BACK)
    zc = (Z0, Z_CASS1)
    if tray:
        pan = build_tray(design, root, tray, yc, zc)
        out[pan.name] = pan
        print("step 2: tray", size(bbox(pan)))
        set_material(design, [pan], "tray", "GALVANISED STEEL 0.5")
    if felt:
        fb = box(design, felt, "FELT", (X_FELT_FACE, X_FELT_BACK),
                 ("(%s) + tray_t + felt_c" % yc[0], "(%s) - tray_t - felt_c" % yc[1]),
                 ("(%s) + tray_t + felt_c" % zc[0], "(%s) - tray_t - felt_c" % zc[1])).bodies.item(0)
        fb.name = "FELT - PET 9 HELD BY THE TRAY LIPS"
        out[fb.name] = fb
        print("step 3: felt", size(bbox(fb)))
        set_material(design, [fb], "felt", "PET FELT 9 MM DARK GRAY")
        out[fb.name] = el_felt_cuts(design, felt, fb, yc, zc)
    if not clip:
        return out
    # reserved zones for the captive clips (H03): in the 4 mm gap between the frame's inner face and the
    # tray back, on the first and last intermediate stiles of the panel frame, near the top and bottom
    last = "stud_c%d" % int(round(design.userParameters.itemByName("stile_n_mid").value))
    ys = [("(%s) + stud_c1 - tube_w / 2" % Y_FRONT, "(%s) + stud_c1 + tube_w / 2" % Y_FRONT),
          ("(%s) + %s - tube_w / 2" % (Y_FRONT, last), "(%s) + %s + tube_w / 2" % (Y_FRONT, last))]
    zs = [("(%s) + clip_zone_dz - clip_zone_h / 2" % Z0, "(%s) + clip_zone_dz + clip_zone_h / 2" % Z0),
          ("(%s) - clip_zone_dz - clip_zone_h / 2" % Z_CASS1, "(%s) - clip_zone_dz + clip_zone_h / 2" % Z_CASS1)]
    n = 0
    for zi, zr in enumerate(zs):
        for yi, yr in enumerate(ys):
            n += 1
            b = box(design, clip, "CLIP ZONE %d" % n, (X_FRAME_IN, X_TRAY_BACK), yr, zr).bodies.item(0)
            b.name = "HOLD - CLIP ZONE %d (%s %s)" % (n, "BOTTOM" if zi == 0 else "TOP", "FRONT" if yi == 0 else "BACK")
            out[b.name] = b
    print("step 4: %d clip zones (HOLD H03)" % n)
    set_material(design, [b for k, b in out.items() if k.startswith("HOLD")], "zone", "RESERVED ZONE")
    return out


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("the active document is not a Fusion design")
    root = design.rootComponent
    pn = PARTS[ROOT_KEY][0]
    if design.userParameters.count or root.occurrences.count or root.bRepBodies.count:
        if ARGS.get("rebuild") != "1":
            raise RuntimeError("the active design is not empty; pass rebuild=1 to rebuild it")
        if root.partNumber != pn and not app.activeDocument.name.startswith(pn + "_"):
            # a root part number set while --doc-new's first upload is still running can be
            # overwritten by it (seen on the first cassette build), so the document name counts too
            raise RuntimeError("refusing to rebuild: root part number is %r, not %s" % (root.partNumber, pn))
        clear_design(design)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    n_skel, n_wall = add_params(design, ARGS["repo_root"])
    root.partNumber = pn
    desc = "%s | %s | %s | position %s" % (PARTS[ROOT_KEY][1], PARTS[ROOT_KEY][2], REV, CODE)
    root.description = desc
    print("document %s (expected name %s): %d skeleton + %d wall parameters" % (
        app.activeDocument.name, DOC_NAME, n_skel, n_wall))
    bodies = build_panel(design, root) if PANEL_SIDE else build_cassette(design, root)
    tl = design.timeline
    # every item not healthy is printed with Fusion's own message; errors fail the build, and so does a warning
    # on any feature this script made. A warning on a STEP import's timeline group (Joints' shared parts, F-189)
    # is printed for review and doesn't stop the build (the L1 run of 05:32 met two, with no message read then).
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    warning = adsk.fusion.FeatureHealthStates.WarningFeatureHealthState
    bad_items = []
    for i in range(tl.count):
        it = tl.item(i)
        if it.healthState == healthy:
            continue
        msg = (it.errorOrWarningMessage or "").replace("\n", " ")[:300]
        print("HEALTH|%s|%s|%s" % (it.name, state_name(it.healthState), msg))
        if it.isGroup:
            # a group is only a container: it is judged by its own items, each printed with Fusion's message (a STEP
            # import's group reports "unknown", its occurrence and base feature healthy: dry run 7's probe)
            g = adsk.fusion.TimelineGroup.cast(it)
            kids = [g.item(j) for j in range(g.count)]
            sick = [k for k in kids if k.healthState != healthy]
            for k in kids:
                print("HEALTH|  in %s: %s|%s|%s" % (it.name, k.name, state_name(k.healthState),
                                                    (k.errorOrWarningMessage or "").replace("\n", " ")[:200]))
            for k in sick:
                if not (k.healthState == warning and re.match(r"Group\d+$", it.name)):
                    bad_items.append("%s / %s" % (it.name, k.name))
            if not sick:
                print("HEALTH|  %s: all %d of its items are healthy, so it counts as healthy" % (it.name, len(kids)))
            continue
        bad_items.append(it.name)
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    print("timeline %d items, unhealthy %d, sketches %d, loose %d" % (
        tl.count, len(bad_items), sum(c.sketches.count for c in design.allComponents), len(loose)))
    for name, b in sorted(bodies.items()):
        print("BODY|%s|%s|%s|%s" % (b.parentComponent.partNumber, name, size(bbox(b)), bbox(b)))
    placed = assembly_bodies(design)          # every copy as placed (D-120: copies of one component)
    hits, bad = placed_clashes(placed)
    print("clash pairs %d over %d placed bodies, unexpected %d %s" % (len(hits), len(placed), len(bad), bad))
    for c in design.allComponents:
        if c.bRepBodies.count:
            pp = c.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
            n_occ = 1 if c == root else root.allOccurrencesByComponent(c).count
            print("MASS|%s|%s|%.3f kg each|%d bodies|%d copies" % (c.partNumber, c.name, pp.mass,
                                                                    c.bRepBodies.count, n_occ))
    root.partNumber = pn            # again at the end, in case an upload overwrote them (see settle_props)
    root.description = desc
    allb = [b for b, _o in placed.values()]
    print("root part number %s, bodies box %s" % (root.partNumber, [
        round(min(bbox(b)[i] for b in allb), 2) for i in range(3)] + [round(max(bbox(b)[i + 3] for b in allb), 2)
                                                                    for i in range(3)]))
    if bad_items or loose or bad:
        raise RuntimeError("checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
    if ARGS.get("post") == "1":
        doc = app.activeDocument
        # the drawings' Front = the panel seen from inside the pod, saved with the build (set_front.py)
        sf = os.path.join(ARGS["repo_root"], "v2/02-Drawings/wall/set_front.py")
        sf_ns = {"__name__": "__fusion_set_front__", "__file__": sf, "SCRIPT_ARGS": {"inside": INSIDE}}
        with open(sf, "r", encoding="utf-8") as fh:
            exec(compile(fh.read(), sf, "exec"), sf_ns)
        print("helper file %s" % os.path.realpath(sf))
        sf_ns["run"](None)
        ver = save_holding_props(app, doc, root, pn, desc, "%s build: %s" % (REV, ARGS.get("note", "wall_side_panel.py")))
        print("saved %s (version %s), part number %s, description %r" % (doc.name, ver, root.partNumber,
                                                                         root.description[:60]))
        path = os.path.join(ARGS["repo_root"], "v2/01-CAD-Native/wall/post_wall_doc.py")
        ns = {"__name__": "__fusion_post__", "__file__": path, "SCRIPT_ARGS": dict(ARGS, pn=pn)}
        with open(path, "r", encoding="utf-8") as fh:
            exec(compile(fh.read(), path, "exec"), ns)
        print("helper file %s" % os.path.realpath(path))
        ns["run"](None)
