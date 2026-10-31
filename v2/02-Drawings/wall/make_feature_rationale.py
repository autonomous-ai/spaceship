"""Feature rationale register (guideline section 7) for a WALL side panel and its cassette, from the CAD.

    python3 v2/02-Drawings/wall/make_feature_rationale.py 210101 510101

Reads the CAD reports v2/03-Manufacturing/wall/out/<pn>.json (written in Fusion by
v2/01-CAD-Native/wall/report_wall_doc.py) and writes FEATURE-RATIONALE-<panel pn>.md here. Every
hole's size and centre comes from the CAD; the reason, mating part, rule, tolerance, method and status
come from the table FAMILIES below, each with its source. A hole the table doesn't explain fails the
run, so no feature can reach a drawing without a reason.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "03-Manufacturing", "wall", "out")
REG = "joints register V2-ENG-JNT-01 P01 (PR #23)"

# back panels B1-B4 (wall_back_panel.py): the families that differ from the side panels'
FAMILIES_BACK = {
    ("RAIL - BOTTOM", 8.5, "z"): (
        "F03", "Locating: the round spigot hole 100 from the closing-seam end, and the two arcs of the slot F04 100 "
        "from the corner end", "Ø8 spigot H-05 standing 8 proud of the band top (B1, B2) or of the lower panel (B3, B4)",
        "round by the closing seam, so the closing gap is set by the round spigots and their distance to the seam face "
        "(5.2 to 5.8, ST-02); the slot runs along the edge (8.5 x 14)", "%s 2.11 ST-02, R-J13" % REG,
        "16.5 to each side wall", "±0.1 spigot position and spigot-to-seam-face (PROPOSED in ST-02); Ø8.5 on Ø8",
        "CNC or jig; the drill jig's locating point", "PROPOSED (register)"),
    ("RAIL - TOP", 9.53, "z"): (
        "F05", "Top rail rivnuts, nut side: J-WALL-01 to the upper panel (B1, B2: 4 at the 220 rule, with stop washers) "
        "and 2 spigot rivnuts 100 from the ends (B1, B2 for the upper panel; B3, B4 for the ceiling's back spigots)",
        "Sherex CAH3-610-4.2 (838003), stop washer H-08 (831002) under the bolt ones; spigots H-05 (831001)",
        "on the frame's centre line Y 824; bolts 220, 473.00, 725.99, 978.99 from the frame's ends (register 2.9)",
        "%s 2.9, 3.1, 3.4" % REG, "15.2 to each side wall of the 40 face", "Ø0.4 from F03", "CNC or jig; T-01, T-02",
        "source (hole); DECIDED (positions)"),
    ("RAIL - TOP", 7.0, "z"): (
        "F24", "J-CEIL-01 back edge bolt clearance, bolt side (B3, B4): the captive bolt goes up through the top wall "
        "into the ceiling's 40 x 40 back member's rivnut", "M6 x 16 ISO 4762 (838001), washer 838004, into the "
        "ceiling's rivnut over its stop washer",
        "4 at 220, 473.00, 725.99, 978.99 from the frame's ends (register 2.9; 4 per back panel, PM ruling 16:50)",
        "%s 2.4, 2.9, 3.4" % REG, "16.5 to each side wall; 30 or more to every stile (R-J14)", "Ø0.4 from F03",
        "CNC or jig", "DECIDED (register)"),
    ("RAIL - TOP", 19.0, "z"): (
        "F25", "Key access for F24, in the top rail's bottom wall facing the bay; holds the grommet retainer",
        "ISO 7093-1 washer Ø18, ISO 4762 head, 5 mm key", "coaxial with F24", "%s FR-03" % REG,
        "pocket F13 below it", "coaxial within the Ø0.4 zone", "drilled with F24", "calculation"),
    ("STILE - OUTER", 7.0, "x"): (
        "F26", "J-WALL-02 corner bolt clearance, bolt side: the captive bolt goes out through the outer stile's end wall "
        "across the 2.26 corner gap into the side panel's back-stile rivnut", "M6 x 16 ISO 4762 (838001), washer "
        "838004, into the side panel's rivnut (F09) over its stop washer",
        "3 on the bolt line Y 824 (R-J15) at 220, 559.31, 898.61 up the 1118.61 edge (register 2.9)",
        "%s 2.4, 2.9, 3.2" % REG, "16.5 to each side wall", "Ø0.4 from F03, matched by the side panel's F09",
        "CNC or jig", "DECIDED (register)"),
    ("STILE - OUTER", 19.0, "x"): (
        "F27", "Key access for F26, in the outer stile's bay-side wall; holds the grommet retainer",
        "ISO 7093-1 washer Ø18, ISO 4762 head, 5 mm key", "coaxial with F26", "%s FR-03" % REG, "pocket F13 beside it",
        "coaxial within the Ø0.4 zone", "drilled with F26", "calculation"),
    ("STILE - CENTRE", 7.0, "x"): (
        "F28", "Closing-seam pin hole, nut side (B1, B3): a plain hole the right-hand panel's pin bolt passes through; "
        "no rivnut", "the M6 x 25 pin bolt (838002) of B2 or B4", "3 on the frame's centre line at the corner bolts' "
        "heights (220, 559.31, 898.61)", "%s 2.10, R-J11, R-J16" % REG, "16.5 to each side wall",
        "coaxial with the pin rivnut within ±0.2 (R-J6)", "CNC or jig", "DECIDED (register)"),
    ("STILE - CENTRE", 9.53, "x"): (
        "F29", "Closing-seam pin rivnut, bolt side (B2, B4): holds the factory-fitted M6 x 25 pin bolt; no stop washer, "
        "the gap is set by the spigots", "Sherex CAH3-610-4.2 (838003); M6 x 25 ISO 4762 (838002) with its washer",
        "3 at F28's positions", "%s 2.10" % REG, "15.2 to each side wall", "±0.2 to F28 (R-J6)",
        "CNC or jig; T-01, T-02", "DECIDED (register)"),
    ("STILE - CENTRE", 19.0, "x"): (
        "F30", "Key access for the pin bolt F29 (B2, B4), in the centre stile's bay-side wall",
        "5 mm key; the bolt's head Ø10 and washer Ø18 stay inside the tube (head top 17.76 of 18.8, register 2.10)",
        "coaxial with F29", "%s 2.10" % REG, "pocket F13 beside it", "coaxial within the Ø0.4 zone",
        "drilled with F29", "calculation"),
}

OTHER_BACK = [
    ("F10", "{frame}", "Two studs at 393 between centres, 1.0 wall (D-85); perimeter 1.2",
     "keeps the ACP flat (members 400 apart or less, D-16, D-34); every bolt 30 or more from every stud (R-J14)",
     "stile_pitch_max 400; pitch = (half_fw - 20) / 3 (calculation)", "follows half_fw (edit test)",
     "cut list ±0.5 (assumption)", "DECIDED (D-85)"),
    ("F12", "{frame}", "Rails run the full frame width; stiles fit between them (square butt ends)",
     "a continuous bottom rail sits on its gasket in one line", "member joint method HOLD (H11)", "", "", "HOLD"),
    ("F13", "{fill}", "Fill pockets 60 x 60 x 40 beside every bolt this panel drives (bottom rail, corner, and the "
     "ceiling bolts on B3/B4, the pins on B2/B4)", "the key reaches the access holes from inside before the cassette "
     "goes on", "%s FR-10, 2.3" % REG, "", "", "PROPOSED (assumption size)"),
    ("F31", "{frame}", "Frame width half_fw 1198.99, stopping close_gap / 2 (2.75) from X 0",
     "the closing seam takes the back wall's tolerance as a 5.5 gap (4.0 to 7.0), set by the spigots (R-J11, R-J16)",
     "skeleton P04 half_fw, close_gap", "follows half_fw (edit test)", "5.2 to 5.8 (ST-02)", "DECIDED"),
    ("F32", "{frame}", "1 x 45 lead-in on the top edge of the closing-seam face",
     "the next panel drops in past it without catching the bulb seal (R-J9)", "%s 2.10" % REG, "", "", "DECIDED"),
    ("F33", "{skin}", "Skin width half_pw 1200.61: flush with the frame at the corner, 1.62 past it at the closing seam",
     "every visible skin seam stays 2.26 (R-J16); the look is unchanged", "skeleton P04 half_pw", "follows half_pw",
     "0.76 to 3.76 as the closing gap moves (register 2.8)", "DECIDED"),
    ("F16", "{assy}", "Seam gaps 2.26 at the corner (stops) and under the panel (band or seam)",
     "the gasket's compressed thickness, set by the metal stop (stop washer 1.5 + rivnut head 0.76)",
     "skeleton P04 seam_gap", "", "2.13 to 2.39 (register 2.8)", "confirmed"),
    ("F20", "{tray}", "Tray returns run the full 34 mm and turn in as 12 mm lips", "the lips hold the felt with no glue",
     "PM ruling 2026-10-31, option 1", "", "", "confirmed"),
    ("F21", "{tray}", "Bend radius 0.5 (1 x t), K-factor 0.44, square corner relief", "flat pattern for the 0.5 tray",
     "assumption, as the side and ceiling trays", "", "", "assumption"),
    ("F22", "{felt}", "Felt 1 mm clear inside the returns, behind the lips", "held by the lips; 24 mm air gap behind it",
     "felt_c 1 (assumption)", "", "", "assumption"),
    ("F34", "{tray}", "Back cassettes stop seam_gap / 2 (1.13) short of X 0: a 2.26 gap to the next back cassette, "
     "with the soft edge seal H-14", "each cassette hangs on its own frame and the closing seam moves, so touching "
     "edges would clash", "PM ruling 2026-10-31 16:58 (DECIDED)", "follows pod_w", "", "DECIDED"),
    ("F23", "NO-PN-HOLD-H03", "Clip zones on the panel frame's two studs, 100 from the cassette's top and bottom",
     "reserved for the captive clip (D-47); clear of every key access hole and pocket", "HOLD H03, HOLD-08", "", "",
     "HOLD"),
]

# ELECTRICAL's interface features (ELECTRICAL P01, electrical_model.py, PR #64; the PM's final sizes 2026-10-31
# 20:38 UTC), in the parts of the positions that carry them (R1, R2, B2, B4); the build's el_ parameters
ELS = "ELECTRICAL P01 (electrical_model.py, PR #64)"
FELT = "FELT - PET 9 HELD BY THE TRAY LIPS"
TRAY = "TRAY - STEEL 0.5 WITH RETURNS AND LIPS"
FAMILIES_EL = {
    (FELT, 60.0, "x"): (
        "F35", "FA-KIT: felt access hole to the voice kit drop (R1-CASS), closed with a felt plug",
        "ELECTRICAL's kit pocket P3-KIT behind it; the felt plug (ELECTRICAL)",
        "halfway between the air column's back face and the back lining (Y el_y_kit), 80 above the trunk (Z 1180)",
        ELS + ": kit_d, y_kit, trunk_z", "felt only: no steel there (the lips are at the tray's edges)",
        "±1 (knife cut, assumption)", "knife or CNC knife", "assumption (ELECTRICAL)"),
    (FELT, 19.1, "x"): (
        "F36", "FX-COL: the trunk's way out of R1-CASS into the air column's cable chase",
        "ELECTRICAL trunk harness 710021", "Y el_y_cx (13 behind the column's back face), at the trunk (Z 1100)",
        ELS + ": y_cx, trunk_z, grm_d", "felt only", "±1 (assumption)", "knife", "assumption (ELECTRICAL)"),
    (FELT, 12.0, "x"): (
        "F37", "FX-CALL0 and FX-CALL2: the call light feed into R2-CASS behind the shelf and out above the screen",
        "ELECTRICAL call light harness 710024", "Y el_call_y (the front end of a 900 bar), Z 2250 and 1450",
        ELS + ": call_y, shelf_z, call_z, grm_s", "felt only", "±1 (assumption)", "knife", "assumption (ELECTRICAL)"),
    ("SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM", 24.0, "y"): (
        "F38", "Mains inlet and LAN feed-through holes in B2's skin",
        "powerCON TRUE1 TOP (cut-out 23.8) and etherCON NE8FDP (24), ELECTRICAL's selection E",
        "X 120, clear of the closing seam member and its pin pocket; Z 313 and 375 (v1's positions + 15)",
        ELS + ": inlet_x, inlet_z, lan_z, inlet_d", "fill cut-out F47 behind them", "±0.2 (CNC router, assumption)",
        "routed with the skin blank (DXF)", "source (ELECTRICAL)"),
    (TRAY, 19.1, "z"): (
        "F39", "Bushing holes for the light feed: G-PU-TOP in the cut-out's top return, G-B2-B4 in B2-CASS's top return "
        "and B4-CASS's bottom return", "Heyco 2836 SB 750-625 bushing (ELECTRICAL)",
        "X 346, the light feed (PM 2026-10-31 20:38 UTC); Y 787.5, the middle of the 24 cable gap",
        ELS + ": grm_d 19.1 (the bushing's hole, PM: 19.1), y_bg", "in the return's flat, clear of its bends",
        "±0.2 (assumption)", "punched in the flat blank (DXF)", "source (ELECTRICAL)"),
    (FELT, 16.0, "y"): (
        "F42", "FX-SHELF: the light shelf feed's way out of B4-CASS", "ELECTRICAL light feed harness 710011",
        "X 346 (the light feed), Z 2250 (the shelf; CEILING sets it)", ELS + ": shelf_z, FX-SHELF 16", "felt only",
        "±1 (assumption)", "knife", "assumption (ELECTRICAL)"),
}
OTHER_EL = {
    "R1": [("F43", "{felt}", "FS-CNR: felt slot 18 x 120 at the back-right corner (Y 768 to 786, Z 1040 to 1160), "
            "hidden behind B2-CASS's end", "the trunk turns the corner from B2-CASS's gap into R1-CASS's gap",
            ELS + ": FS-CNR", "stays on the back lining's plane", "±1 (knife, assumption)", "assumption (ELECTRICAL)")],
    "B2": [("F44", "{tray}", "Power unit cut-out 304 x 268 (X 91 to 395, Z 866 to 1134) through the base, its edges "
            "turned toward the room as returns the full 34, no lips",
            "the frame-mounted unit (296 x 260 x 72) passes 4 clear all round, so the lining stays floating; the returns "
            "close the cable gap and carry the slot F45 and a bushing hole F39",
            ELS + " and its final size (PM 2026-10-31 20:38 UTC)", "fixed at ELECTRICAL's place",
            "±0.5 (assumption)", "source (ELECTRICAL)"),
           ("F45", "{tray}", "Slots: S-PU-X 20 x 70 in the cut-out's right return (Y 777.5 to 797.5, Z 1030 to 1100); "
            "S-CNR 11 x 80 in the end return (Y 776 to 787, Z 1060 to 1140)",
            "the unit's two lead exits, and the trunk's turn into R1-CASS; ELECTRICAL fits the edge grommets",
            ELS + ": slot_h, slot_l, lx_z1, lx_z2, cs_h, y_xc, trunk_z", "S-CNR follows the side lining's face (pod_w)",
            "±0.5 (assumption)", "assumption (ELECTRICAL)"),
           ("F46", "{felt}", "Felt cut 1 clear round the cut-out's returns", "the felt edge there has no lip; the unit's "
            "face covers it", "felt_c 1 (assumption)", "", "±1", "assumption"),
           ("F47", "{fill}", "Fill left out in the first bay: the unit (the cut-out's size, run on to the first stud so "
            "no sliver stays), the sleeve 20 wide down to Z 301, the inlet and LAN connectors (X 108 to 160, Z 301 to "
            "387)", "room for ELECTRICAL's factory-fitted parts; knife cut through the 40 fill", ELS,
            "the unit's cut-out runs to the first stud as it moves", "±2 (knife, assumption)",
            "source (ELECTRICAL); the unit's fixing HOLD (IF-12)"),
           ("F48", "NO-PN-HOLD-H03", "The top clip zone on the first stud sits beside the cut-out's right return",
            "the clip (H03) must clear the return's bend (X 395 to 396)", "HOLD H03", "", "", "HOLD")],
    "B4": [("F40", "{felt}", "FX-CEIL: the ceiling route's crossing into B4-CASS, under the ceiling cassette's cable "
            "holes (X (pod_w - 2 stack_t) / 4 = 583): not modelled yet", "ELECTRICAL's model put a 19.1 bushed hole "
            "through the top lip, wider than the 12 lip; PM rule 2026-10-31 21:01 UTC: no cable hole through a lip, "
            "felt only or a full steel face with its bushing, never a notch", ELS + ": ceil_x, z_cg",
            "ELECTRICAL sets a felt-only height under the lip", "", "HOLD")],
}
POSITIONS = {"2101": ("L1", "R1", "L2", "R2"), "2102": ("B1", "B2", "B3", "B4")}

# (body name, hole diameter, axis) -> id, function, mating part, rule (where and why there), source,
# clearances, tolerance, make and check, status
FAMILIES = {
    ("RAIL - BOTTOM", 7.0, "z"): (
        "F01", "J-BASE-01 bolt clearance, bolt side: the panel's captive bolt goes down through the rail's bottom wall "
        "into the base band's rivnut (lower panel) or the lower panel's rivnut (upper panel)",
        "M6 x 16 ISO 4762 8.8 (838001) with its ISO 7093-1 head washer (838004), into Sherex CAH3-610-4.2 (838003) "
        "over the 1.5 mm stop washer (831002)",
        "4 holes on the frame's centre line: end bolts 220 in from the panel's ends, evenly spaced (R-J14)",
        "%s 3.1, 3.3, FR-02; PM rulings F-009 (Ø7.0) and R-J14 (220 rule)" % REG,
        "16.5 to each side wall of the 40 mm face; 30 or more to every stile face (R-J14; pocket F13)",
        "Ø7.0 gives 0.51 float on M6; position Ø0.4 (±0.2) from the spigot hole F03 (PM ruling F-009)",
        "CNC or drill jig located on F03; check with a Ø6.6 pin through both parts on the jig", "PROPOSED (register); positions source; Ø confirmed"),
    ("RAIL - BOTTOM", 19.0, "z"): (
        "F02", "Key access for F01: the bolt and its washer go in head first at the factory, a grommet (838005, "
        "HOLD-02) in this hole holds the head, and the 5 mm key reaches the socket on site",
        "ISO 7093-1 washer Ø18; ISO 4762 head Ø10; 5 mm hex key (108001)",
        "coaxial with F01, in the rail's top wall, which faces the bay", "%s 2.2, FR-03" % REG,
        "Ø19 leaves 10.5 to each side wall of the 40 mm face", "coaxial with F01 within the Ø0.4 zone",
        "drilled with F01 in the same set-up", "calculation"),
    ("RAIL - BOTTOM", 8.5, "z"): (
        "F03", "Locating: the fixed spigot hole (round) at the front end, and the two arcs of the slot F04 at the back end",
        "Ø8 spigot H-05 standing 8 proud of the band top", "round hole 100 from the front end; slot 100 from the back "
        "face, its length along X so the panel can close onto the back panel across the corner gap",
        "%s FR-04, FR-05, 3.2; PM ruling (register sizes)" % REG, "16.5 to each side wall",
        "Ø8.5 on Ø8 h9 (assumption): 0.5 clearance; the datum for F01's position",
        "CNC or jig; this hole is the drill jig's locating point", "PROPOSED (register); sizes assumption"),
    ("RAIL - TOP", 9.53, "z"): (
        "F05", "J-WALL-01 rivnuts, nut side (4, one per bay) and 2 spigot rivnuts: the upper panel bolts down into "
        "these, and its spigots stand in the 2 end ones", "Sherex CAH3-610-4.2 with the 1.5 mm stop washer H-08 "
        "(sets the 2.26 seam gap); spigots H-05 in the 2 end ones",
        "bolt rivnuts at the 220 rule, coaxial with the upper panel's F01 holes (R-J14); spigot rivnuts 100 from each "
        "end (R-J13), not at a bolt", "%s 3.1, FR-01, FR-04" % REG,
        "15.2 to each side wall of the 40 mm face (Ø20 stop washer fits a 40 mm face only)",
        "Ø9.53 +0.10 (Sherex); position Ø0.4 from the lower panel's spigot rivnut (PM ruling F-009)",
        "CNC or jig; set with the maker's tool; check flush set and spin with T-01/T-02", "source (hole); PROPOSED (positions)"),
    ("STILE - FRONT", 7.0, "y"): (
        "F07", "J-FRONT-01 bolt clearance, bolt side: the captive bolt goes forward through the front wall into the "
        "decor block's rivnut", "M6 x 16 ISO 4762 into the decor back plate's rivnut (H-03, H-08; FRONT design)",
        "3 per panel height at the 220 rule (220 in from the panel's bottom and top, and the middle); on the frame's "
        "centre line", "%s 3.5, FR-08; PM rulings F-009, R-J14" % REG, "16.5 to each side wall; the Ø19 F08 behind it",
        "Ø0.4 position from F03", "CNC or jig", "PROPOSED (register)"),
    ("STILE - FRONT", 19.0, "y"): (
        "F08", "Key access for F07, in the stile's back wall facing the first bay; holds F07's grommet retainer",
        "ISO 7093-1 washer Ø18, ISO 4762 head, 5 mm key",
        "coaxial with F07", "%s FR-03" % REG, "pocket F13 in the first bay", "coaxial within the Ø0.4 zone",
        "drilled with F07", "calculation"),
    ("RAIL - TOP", 9.53, "x"): (
        "F06", "J-CEIL-01 rivnuts, nut side (upper side panels): the ceiling's side tube bolts across the 2.26 gap "
        "into these", "Sherex CAH3-610-4.2 with the stop washer H-08 in the room-side wall of the 40 x 40 top member",
        "4 on the ceiling's bolt line Z 2374 (R-J15), at the ceiling's rule: from Y -645 (its front edge), 220 in, "
        "pitch 351.67, so CEILING drills the same (PM ruling 2026-10-31 16:55)",
        "%s 3.4, 2.9; PM rulings R-J3, R-J15" % REG, "hole edge 15.2 from each side wall; Ø20 washer on the 40 face",
        "Ø0.4 from F03, matched by the ceiling's holes", "CNC or jig; T-01, T-02", "source (hole); DECIDED (positions)"),
    ("STILE - BACK", 9.53, "x"): (
        "F09", "J-WALL-02 corner rivnuts, nut side: the back panel's edge tube bolts across the corner gap into these",
        "Sherex CAH3-610-4.2 with the stop washer H-08 in the room-side wall of the 40 x 40 back stile",
        "3 per panel height at F07's heights, on the back panel's bolt line Y 824 (its tube centre, R-J15)",
        "%s 3.2, FR-01, FR-06, FR-07; PM rulings R-J3 (40 x 40), R-J15" % REG,
        "hole edge 11 from the inner wall; the Ø20 stop washer (Y 814 to 834) lies on the 40 mm face",
        "Ø0.4 from F03, matched by the back panel's FR-07 holes", "CNC or jig; T-01, T-02", "source (hole); PROPOSED (positions)"),
}

OTHER = [
    ("F10", "{frame}", "Stile pitch 364.93 between centres, 3 intermediate studs at a 1.0 wall (D-85); perimeter 1.2",
     "keeps the ACP flat between bond lines (D-16, D-34: members 400 apart or less); every bolt lands 30 or more from "
     "every stile (R-J14; checked by test_wall_offline.py)", "stile_pitch_max 400 (confirmed); "
     "pitch = (frame length - 10 - 20) / 4 (calculation)", "follows wall_depth (edit test)", "cut list ±0.5 (assumption)", "confirmed rule"),
    ("F11", "{frame}", "Back stile 40 x 40 x 1.2", "room for the corner rivnut, its Ø20 stop washer and the bolt "
     "(37+ mm overlap instead of 17)", "PM ruling R-J3; %s 2.4, FR-06" % REG, "", "", "confirmed"),
    ("F12", "{frame}", "Rails run the full frame length; stiles fit between them (square butt ends)",
     "a continuous bottom rail sits on the band and its gasket in one line", "member joint method HOLD (H11)", "", "", "HOLD (joint method)"),
    ("F13", "{fill}", "Fill pockets 60 x 60 x 40, beside every bolt this panel drives (4 above F01, 3 beside F07)",
     "the 5 mm key reaches F02 and F08 from inside the pod before the cassette goes on", "%s FR-10, 2.3" % REG, "", "", "PROPOSED (assumption size)"),
    ("F14", "{skin}", "Skin back return: the side skin folds 43 mm round the frame's back end",
     "the back corner shows ACP, not the frame end (D-55; register section 7 item 5)", "skin_ret = outer_t - skin_t (assumption)",
     "V-groove and fold per the ACP maker (HOLD H16)", "", "assumption"),
    ("F15", "{skin}", "Skin flush with the frame's top and bottom (setback 0)", "the outside reveal equals the 2.26 seam gap, "
     "crisp and aligned (D-23)", "skin_setback 0 (assumption); seam_gap 2.26 (P04, confirmed)", "", "", "assumption"),
    ("F16", "{assy}", "Seam gaps 2.26: at the decor back plate (front end) and under the panel (band or seam)",
     "the gasket's compressed thickness, set by the metal stop (stop washer 1.5 + rivnut head 0.76)", "skeleton P04 seam_gap and "
     "panel_z0, derived (PM ruling F-008)", "", "2.13 to 2.39 (register 2.8)", "confirmed"),
    ("F20", "{tray}", "Tray returns run the full 34 mm and turn in as 12 mm lips", "the lips hold the felt with no glue "
     "(settles H09) and match the ceiling cassette", "PM ruling 2026-10-31, option 1", "", "", "confirmed"),
    ("F21", "{tray}", "Bend radius 0.5 (1 x t), K-factor 0.44, square corner relief", "flat pattern for the 0.5 mm DX51D tray",
     "assumption, same rule as the ceiling tray; the factory's tooling sets the real values (guideline 9)", "", "", "assumption"),
    ("F22", "{felt}", "Felt 1 mm clear inside the returns, behind the lips", "drops in and is held by the lips; 24 mm air gap "
     "behind it (D-17)", "felt_c 1 (assumption, as the ceiling)", "", "", "assumption"),
    ("F23", "NO-PN-HOLD-H03", "Clip zones on the first and last intermediate stiles, 100 from the cassette's top and bottom",
     "reserved for the captive clip (D-47); clear of every key access hole and pocket (register rule R8)", "HOLD H03, HOLD-08",
     "", "", "HOLD"),
]


def load(pn):
    with open(os.path.join(OUT, "%s.json" % pn), encoding="utf-8") as fh:
        return json.load(fh)


def holes(rep):
    rows = {}
    for c in rep["components"]:
        # panel parts (21xxxx) and the cassette's tray and felt (511x, 512x... 5114); joint hardware (83xxxx) has
        # the maker's bores; a tray's bends are cylinders too (Ø1 and Ø2), so only holes over 3 count there
        lining = c["part_number"].startswith(("5111", "5112", "5113", "5114"))
        if not (c["part_number"].startswith("21") or lining):
            continue
        for b in c["bodies"]:
            for h in b["holes"]:
                if lining and h["d"] <= 3.0:
                    continue
                key = (b["name"], h["d"], h["axis"])
                rows.setdefault(key, []).append(h)
    return rows


def main(argv):
    panel, cass = load(argv[1]), load(argv[2])
    lines = ["# Feature rationale: %s and %s" % (panel["document"], cass["document"]), "",
             "Guideline section 7: why every hole, slot and gap is where it is. Generated by `make_feature_rationale.py` "
             "from the CAD reports (document versions %s and %s); sizes and centres are read from the CAD, X/Y/Z in the "
             "pod system (conventions section 4). On the part drawings the hole tags map to these IDs." % (
                 panel["version"], cass["version"]), "",
             "| ID | Part | Holes from the CAD (Ø, axis, centres) | Function | Mating part | Rule: where and why | Source | "
             "Clearances | Tolerance | Make and check | Status |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    pns = {}
    for rep in (panel, cass):
        for c in rep["components"]:
            for key, pre in (("frame", ("2111", "2112")), ("skin", ("2113", "2114")), ("fill", ("2115", "2116")),
                             ("tray", ("5111", "5112")), ("felt", ("5113", "5114"))):
                if c["part_number"].startswith(pre):
                    pns[key] = c["part_number"]
    pns["assy"] = panel["document"].split("_")[0]
    back = pns["frame"].startswith("2112")
    families = {**FAMILIES, **FAMILIES_BACK, **FAMILIES_EL} if back else {**FAMILIES, **FAMILIES_EL}
    code = POSITIONS[pns["assy"][:4]][int(pns["assy"][4:6]) - 1]
    found = holes(panel)
    found.update(holes(cass))
    unexplained = []
    for key, hs in sorted(found.items()):
        body, d, ax = key
        full = [h for h in hs if h["full_circle"]]
        fam = families.get(key)
        if fam is None:
            if d == 8.5 and body == "RAIL - BOTTOM":
                fam = families[("RAIL - BOTTOM", 8.5, "z")]
            else:
                unexplained.append(key)
                continue
        cs = "; ".join("(%s)" % ", ".join("%g" % v for v in h["centre"] if v is not None) for h in hs)
        part = pns["felt"] if body == FELT else pns["tray"] if body == TRAY else pns["skin"] if body.startswith("SKIN") \
            else pns["frame"]
        lines.append("| %s | %s %s | Ø%g along %s, %d: %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            fam[0], part, body, d, ax, len(hs), cs, fam[1], fam[2], fam[3], fam[4], fam[5], fam[6], fam[7],
            fam[8]))
    if unexplained:
        raise SystemExit("holes with no rationale: %s" % unexplained)
    lines += ["", "Other features:", "", "| ID | Part | Feature | Why | Source or calculation | Edit behaviour | Tolerance | Status |",
              "|---|---|---|---|---|---|---|---|"]
    other = (OTHER_BACK if back else OTHER) + OTHER_EL.get(code, [])
    for row in other:
        lines.append("| %s |" % " | ".join(f.format(**pns) for f in row))
    lines += ["", "Joint hardware modelled in the panel (bodies at every rivnut hole, joints register 2.1): rivnut "
              "838003 as its installed envelope, stop washer 831002 under each stopped-joint rivnut, spigot 831001 in "
              "each spigot rivnut. Their own bores are not features of ours and are not listed."]
    lines += ["", "Masses from the CAD (kg): " + "; ".join(
        "%s %s %.3f" % (c["part_number"], c["name"].split(" ", 1)[-1][:40], sum(b["mass_kg"] for b in c["bodies"]))
        for rep in (panel, cass) for c in rep["components"] if c["bodies"] and not c["part_number"].startswith("NO-PN")), ""]
    out = os.path.join(HERE, "FEATURE-RATIONALE-%s.md" % argv[1])
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s: %d hole families, %d other features" % (os.path.basename(out), len(found), len(other)))


if __name__ == "__main__":
    main(sys.argv)
