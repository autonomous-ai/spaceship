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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "03-Manufacturing", "wall", "out")
REG = "joints register V2-ENG-JNT-01 P01 (PR #23)"
RIVNUT_KEY = 9.53             # the tables' key for a rivnut hole, whatever its size in the CAD (D-163: 10.00)

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
        "Sherex CAH2-610-4.2 (838003, steel zinc since D-131), stop washer H-08 (831002) under the bolt ones; spigots H-05 (831001)",
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
        "the gap is set by the spigots", "Sherex CAH2-610-4.2 (838003, steel zinc since D-131); M6 x 25 ISO 4762 (838002) with its washer",
        "3 at F28's positions", "%s 2.10" % REG, "15.2 to each side wall", "±0.2 to F28 (R-J6)",
        "CNC or jig; T-01, T-02", "DECIDED (register)"),
    ("STILE - CENTRE", 19.0, "x"): (
        "F30", "Key access for the pin bolt F29 (B2, B4), in the centre stile's bay-side wall",
        "5 mm key; the bolt's head Ø10 and washer Ø18 stay inside the tube (head top 17.76 of 18.8, register 2.10)",
        "coaxial with F29", "%s 2.10" % REG, "pocket F13 beside it", "coaxial within the Ø0.4 zone",
        "drilled with F29", "calculation"),
}

OTHER_BACK = [
    ("F10", "{frame}", "Three studs at 294.75 between centres (0.8 wall, D-131 start); perimeter 1.0",
     "the skin flexes 2 mm or less under a 100 N push at a bay's centre (PM 2026-11-01; make_acp_spans.py: 1.99); "
     "every bolt 30 or more from every stud (R-J14: 75 or more)", "stile_pitch_max 300 (confirmed); pitch = "
     "(half_fw - 20) / 4 (calculation)", "follows half_fw (edit test)", "cut list ±0.5 (assumption)",
     "DECIDED (PM 2026-11-01)"),
    ("F12", "{frame}", "Rails run the full frame width; stiles fit between them (square butt ends)",
     "a continuous bottom rail sits on its gasket in one line", "member joints: internal cleats per D-115 (corner and T "
     "cleats, crimped, structural adhesive; no welds; the cleats come from the Joints Engineer)", "", "",
     "DECIDED (D-115); cleats to come"),
    ("F13", "{fill}", "Fill notches 60 x 60, right through the 40 mm batt, beside every bolt this panel drives "
     "(bottom rail, corner, and the ceiling bolts on B3/B4, the pins on B2/B4); each piece cut from its DXF (D-128)",
     "the key reaches the access holes from inside before the cassette goes on", "%s FR-10, 2.3" % REG, "", "",
     "PROPOSED (assumption size)"),
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
        "F39", "Bushing holes for the light feed across the B2/B4 lining joint: G-B2-B4 in B2-CASS's top return and "
        "B4-CASS's bottom return", "Heyco 2836 SB 750-625 bushing (ELECTRICAL)",
        "X 346, the light feed (PM 2026-10-31 20:38 UTC); Y 787.5, the middle of the 24 cable gap",
        ELS + ": grm_d 19.1 (the bushing's hole, PM: 19.1), y_bg", "in the return's flat, clear of its bends",
        "±0.2 (assumption)", "punched in the flat blank (DXF)", "source (ELECTRICAL)"),
    (FELT, 12.0, "y"): (
        "F40", "FX-CEIL: the ceiling route's crossing into B4-CASS, felt only",
        "ELECTRICAL draw wire, ceiling route 710031",
        "X el_ceil_x = (pod_w - 2 stack_t) / 4, under the ceiling cassette's cable holes; Z 2330, its top edge 2 under "
        "the 12 lip", "ELECTRICAL via the PM 2026-10-31 21:10 UTC; PM rule: no cable hole through a lip",
        "felt only: 2 clear of the lip, no steel, no bushing", "±1 (assumption)", "knife", "source (ELECTRICAL)"),
    (FELT, 16.0, "y"): (
        "F42", "FX-SHELF: the light shelf feed's way out of B4-CASS", "ELECTRICAL light feed harness 710011",
        "X 346 (the light feed), Z 2250 (the shelf; CEILING sets it)", ELS + ": shelf_z, FX-SHELF 16", "felt only",
        "±1 (assumption)", "knife", "assumption (ELECTRICAL)"),
}
OTHER_EL = {
    "R1": [("F43", "{felt}", "FS-CNR: felt slot 18 x 120 at the back-right corner (Y 768 to 786, Z 1040 to 1160), "
            "hidden behind B2-CASS's end", "the trunk turns the corner from B2-CASS's gap into R1-CASS's gap",
            ELS + ": FS-CNR", "stays on the back lining's plane", "±1 (knife, assumption)", "assumption (ELECTRICAL)")],
    "B2": [("F44", "{tray}", "Power unit cut-out 304 x 268 (X 91 to 395, Z 866 to 1134) through the base, plain "
            "edges, no returns", "the frame-mounted unit (296 x 260 x 72) passes 4 clear all round, so the lining stays "
            "floating; its leads go straight into the cable gap with no steel on their path. Folded returns round a "
            "rectangular hole can't come from a flat blank (their tabs overlap at the corners)",
            ELS + " and its final size; plain cut-out PM ruling 2026-10-31 21:12 UTC", "fixed at ELECTRICAL's place",
            "±0.5 (assumption)", "source (ELECTRICAL); DECIDED (plain)"),
           ("F45", "{tray}", "Corner slot S-CNR 11 x 80 in the end return (Y 776 to 787, Z 1060 to 1140)",
            "the trunk's turn into R1-CASS; ELECTRICAL fits the edge grommet", ELS + ": cs_h, y_xc, trunk_z",
            "follows the side lining's face (pod_w)", "±0.5 (assumption)", "assumption (ELECTRICAL)"),
           ("F46", "{felt}", "Felt cut flush with the tray's cut-out, 4 clear of the unit; the lining face kept clear "
            "of other features in the 8 band round it", "the felt edge there has no lip: the unit's front plate 320 x 284 "
            "covers it by 8 all round, 2 off the felt on four nylon spacers (ELECTRICAL)",
            "ELECTRICAL via the PM 2026-10-31 21:20 UTC", "", "±1", "source (ELECTRICAL)"),
           ("F47", "{fill}", "Fill left out in the first bay: the unit (the cut-out's size, run on to the first stud so "
            "no sliver stays), the sleeve 20 wide down to Z 301, the inlet and LAN connectors (X 108 to 160, Z 301 to "
            "387)", "room for ELECTRICAL's factory-fitted parts; knife cut through the 40 fill", ELS,
            "the unit's cut-out runs to the first stud as it moves", "±2 (knife, assumption)",
            "source (ELECTRICAL); the unit's fixing HOLD (IF-12)"),
           ("F48", "NO-PN-HOLD-H03", "The top clip zone on the first stud starts 0.75 from the cut-out's edge (X 395)",
            "the clip (H03) needs its edge distance on the tray base there", "HOLD H03", "", "", "HOLD")],
}
POSITIONS = {"2101": ("L1", "R1", "L2", "R2"), "2102": ("B1", "B2", "B3", "B4")}
# D-117 and D-120: the frame's corners and parts once it is rebuilt that way (the reports show member parts)
D117_ROW = ("F12", "{frame}", "The 4 perimeter members run to the frame's outer corners, mitred there (the mitre from the "
            "outer to the inner corner: 45 degrees where the two are the same size, 26.57 on a 40 x 40 meeting a 20 x 40 and "
            "63.43 on the 20 x 40); the studs fit square between the rails", "welded in the factory: the 4 corners and every "
            "stud's T joints (D-131, galvanized steel box tube in the same sections; D-117's cleats cancelled)",
            "D-117 (the corner geometry), D-131 (welds); J-FRAME-01 (joints register): a 2 mm mitre plate welded "
            "into each mitre (831007 to 831009, each member cut back for it), the zinc-rich touch-up, every joint hole "
            "made after welding", "follows the frame (edit test)", "mitre angle per the frame drawing",
            "DECIDED (D-117, D-131)")
# D-131: the closing seam's lead-in lies in the corner weld (the members stop 1.41 short of the corner for the plate)
D131_LEAD_IN = ("F32", "{frame}", "1 x 45 lead-in on the top edge of the closing-seam face, ground into the corner "
                "weld after welding", "the next panel drops in past it without catching the bulb seal (R-J9); with "
                "D-131's mitre plate the top rail and the centre stile stop 1.41 short of that corner, so the lead-in "
                "lies wholly in the weld and is not a cut in the members", "%s 2.10, FR-13; D-131, J-FRAME-01" % REG,
                "", "1 x 45, as ground", "DECIDED")
D120_ROW = ("F49", "{frame}", "Every member is its own part with its own number, the studs copies of one; the frame is "
            "their assembly and keeps its number; the fill pieces, each numbered, go straight into the panel (D-123 cancels "
            "the panel's own fill number) and are cut from their DXFs (D-128); the hardware copies of one part each", "the build plan's rule 2: every part a component, never a body", "D-120, D-123; numbers from the "
            "master BOM's allocation; D-128 for the fill pieces", "copies follow their pattern and their holes", "",
            "DECIDED (D-120)")
FAMILIES_D117 = {}                 # D-131 cancels the cleats, so the rails have no cleat slots

# (body name, hole diameter, axis) -> id, function, mating part, rule (where and why there), source,
# clearances, tolerance, make and check, status
FAMILIES = {
    ("RAIL - BOTTOM", 7.0, "z"): (
        "F01", "J-BASE-01 bolt clearance, bolt side: the panel's captive bolt goes down through the rail's bottom wall "
        "into the base band's rivnut (lower panel) or the lower panel's rivnut (upper panel)",
        "M6 x 16 ISO 4762 8.8 (838001) with its ISO 7093-1 head washer (838004), into Sherex CAH2-610-4.2 (838003, steel zinc) "
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
        "these, and its spigots stand in the 2 end ones", "Sherex CAH2-610-4.2 (steel zinc) with the 1.5 mm stop washer H-08 "
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
        "into these", "Sherex CAH2-610-4.2 (steel zinc) with the stop washer H-08 in the room-side wall of the 40 x 40 top member",
        "4 on the ceiling's bolt line Z 2374 (R-J15), at the ceiling's rule: from Y -645 (its front edge), 220 in, "
        "pitch 351.67, so CEILING drills the same (PM ruling 2026-10-31 16:55)",
        "%s 3.4, 2.9; PM rulings R-J3, R-J15" % REG, "hole edge 15.2 from each side wall; Ø20 washer on the 40 face",
        "Ø0.4 from F03, matched by the ceiling's holes", "CNC or jig; T-01, T-02", "source (hole); DECIDED (positions)"),
    ("STILE - BACK", 9.53, "x"): (
        "F09", "J-WALL-02 corner rivnuts, nut side: the back panel's edge tube bolts across the corner gap into these",
        "Sherex CAH2-610-4.2 (steel zinc) with the stop washer H-08 in the room-side wall of the 40 x 40 back stile",
        "3 per panel height at F07's heights, on the back panel's bolt line Y 824 (its tube centre, R-J15)",
        "%s 3.2, FR-01, FR-06, FR-07; PM rulings R-J3 (40 x 40), R-J15" % REG,
        "hole edge 15.2 from each side face of the 40 mm wall; the Ø20 stop washer (Y 814 to 834) lies on it",
        "Ø0.4 from F03, matched by the back panel's FR-07 holes", "CNC or jig; T-01, T-02", "source (hole); PROPOSED (positions)"),
    # the cassette ledge (the Lead's ruling of 2026-11-01: a wall cassette's weight sits on a ledge, not on clip shear)
    ("RAIL - BOTTOM", 3.3, "x"): (
        "F50", "Cassette ledge rivet holes: the ledge's blind rivets through the bottom rail's room-side wall, plain",
        "838012, closed-end countersunk blind rivets ISO 15974 Ø3.2 x 8 (D-166; joints register H-47), through the "
        "ledge's countersunk F51 holes",
        "6 on a line 9 above the frame's bottom, the end ones 40 in from the ledge's ends and the rest evenly between, so the "
        "pattern is symmetric and L1's and R1's ledges are one part", "the Lead's ruling of 2026-11-01 (WALL group)",
        "inside the tube clear of the J-BASE-01 bolt heads and washers (centre line, Ø18) by 4 or more",
        "±0.2 (assumption); drilled with the ledge held in place as the jig", "drilled after welding and the "
        "touch-up (J-FRAME-01)", "assumption (positions); DECIDED (the ledge)"),
}
for _ax in ("x", "y"):                      # side trays' backs face X, back trays' face Y
    FAMILIES_EL[(TRAY, 6.4, _ax)] = (
        "F53", "Cable-tie holes: ELECTRICAL's Heyco 3904 push-mount ties hold its cables in the 24 cable gap (R1 and B2 "
        "along the trunk, R2 along the call light feed, B4 along the light feed)", "Heyco 3904 push-mount cable tie "
        "(ELECTRICAL)", "a tie every 300 or closer along each cable, one 20 inside each connector pocket's end, none "
        "within 150 of the power unit's cut-out (ELECTRICAL's rule); never in front of a frame member, since the tie's "
        "wings sit behind the sheet (check_tie_holes.py)", ELS + ": positions as ELECTRICAL gave them (the Lead's "
        "relay, 2026-11-01 11:37 UTC)", "each 5 or more inside the tray's back; its edge 20 or more from a member's "
        "face (checked on the STEPs)", "±0.5 (assumption)", "punched or laser cut in the flat blank (DXF)",
        "source (ELECTRICAL)")
FAMILIES[("STILE - FRONT", 8.5, "y")] = (
    "F52", "D-169 pin slots: the decor block locates on two pins along its pull, in two Z slots in the front wall "
    "(L1 only, for DL: as amended the same day, DR and DT keep their base locators)", "the block's two 831001 "
    "spigots in its back plate's rivnuts, 5.7 into the "
    "member", "8.5 wide in X by 12 long in Z, on the bolt line, 100 from each end of the seam edge (the register's "
    "spigot rule)", "D-169 (ruled in the Joints group, 2026-11-01; Joints' places)",
    "120 clear of the nearest J-FRONT-01 bolt holes (F07)", "±0.2 to the bolt holes (Joints)",
    "drilled and slotted after welding (J-FRAME-01)", "DECIDED (D-169)")
LEDGE_BODY = "LEDGE - STEEL ANGLE UNDER THE CASSETTE"
# INTERIOR's fixings on R1's and R2's studs (the Lead's rulings of 2026-11-01 on CEILING's load check)
INT = "the Lead's rulings of 2026-11-01 on INTERIOR's fixings (CEILING Engineer's load check, WALL group)"
FAMILIES[("STILE - MID INTERIOR", RIVNUT_KEY, "x")] = (
    "F54", "INTERIOR's fixing rivnuts: R1's work wall ledge brackets (818101, 4) and R2's screen rail (818102), each "
    "an M6 into a rivnut on the stud's room face", "Sherex CAH2-610-4.2 (838003), no stop washer: its head takes "
    "INTERIOR's Ø12 steel stand-off, which runs to 5 proud of the felt",
    "2 per stud on the stud's centre line: R1 studs Y -240, 103.6, 329.1 and 700 at Z 815 and 1045; R2 studs "
    "Y -121.8 and 580 at Z 1320 and 1380 (the studs that carry them are their own part, 212206 and 212406, D-120)",
    INT + "; D-172", "15.2 to each side wall of the stud's 40 face; clear of the clip zones and ELECTRICAL's tie holes "
    "(test_wall_offline.py)", "Ø9.53 +0.10 (Sherex); position ±0.5 (assumption: INTERIOR's bracket slots take it)",
    "drilled after welding and the touch-up (J-FRAME-01); rivnuts set after", "DECIDED (the Lead's rulings)")
FAMILIES_EL[(TRAY, 16.0, "x")] = (
    "F55", "Stand-off clearance holes in the tray: INTERIOR's Ø12 stand-offs pass through the lining to the studs",
    "INTERIOR's stand-offs (to its ledge brackets on R1, its screen rail on R2)", "one at each INTERIOR rivnut (F54)",
    INT, "2 round the Ø12 stand-off, so the floating lining never touches it (D-17)", "±0.5 (assumption)",
    "punched or laser cut in the flat blank (DXF)", "DECIDED (the Lead's rulings)")
FAMILIES_EL[(FELT, 16.0, "x")] = (
    "F56", "Stand-off clearance holes in the felt, in line with F55", "INTERIOR's stand-offs",
    "one at each INTERIOR rivnut (F54)", INT, "as F55: 2 round the stand-off", "±1 (knife, assumption)", "knife",
    "DECIDED (the Lead's rulings)")
# B2 under D-131 (the Lead's approval of WALL's B2 frame, 2026-11-01): the power unit on two cross members
B2F = "the Lead's approval of WALL's B2 frame (2026-11-01); ELECTRICAL's B2 inputs (WALL group, 2026-11-01)"
FAMILIES_BACK[("CROSS - LOWER", RIVNUT_KEY, "z")] = (
    "F57", "The power unit's fixing rivnuts: the unit sits on the lower cross member's 2 rivnut heads and fixes into "
    "them and the upper member's 2", "Sherex CAH2-610-4.2 (838003), no stop washer; ELECTRICAL's M6 x 16 (838001) "
    "with washers 838004, driven from inside the empty unit", "on the tubes' centre line Y 824: the lower member's top "
    "at X 160 and 376, the upper member's underside at X 110 and 376", B2F,
    "15.2 to each side wall; 32 or more from the cable passages (F58)", "Ø9.53 +0.10 (Sherex); position ±0.5",
    "drilled after welding (J-FRAME-01); rivnuts set after", "source (ELECTRICAL); DECIDED (the frame)")
FAMILIES_BACK[("CROSS - UPPER", RIVNUT_KEY, "z")] = FAMILIES_BACK[("CROSS - LOWER", RIVNUT_KEY, "z")]
for _d, _what in ((15.9, "the mains passage's bottom wall, for the Heyco SB 625-7 bushing snapped in from below"),
                  (20.0, "the mains passage's top wall, lined by the unit's own bushing from above"),
                  (11.1, "the LAN passage's bottom wall, for the Heyco SB 437-5 bushing"),
                  (14.0, "the LAN passage's top wall, lined by the unit's own bushing")):
    FAMILIES_BACK[("CROSS - LOWER", _d, "z")] = (
        "F58", "Cable passages through the lower cross member: the mains cord (SJOOW 14/3) and the LAN cable rise from "
        "the inlet and the jack into the unit, apart (%s)" % _what, "ELECTRICAL's bushings and the unit's",
        "the mains at X 113, the LAN at X 207, on the tube's centre line Y 824", B2F,
        "32 or more from the unit's rivnuts; left of the first stud's T joint below", "±0.5 (assumption)",
        "drilled after welding (J-FRAME-01)", "source (ELECTRICAL)")
FAMILIES_BACK[("SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM", 3.2, "y")] = (
    "F59", "The connectors' screw holes: two per connector on the diagonal, +9.5/+12 and -9.5/-12 (X/Z) from its "
    "centre", "M3 screws with nuts (ELECTRICAL), holding the inlet and the LAN jack (Neutrik's drawings)",
    "beside F38's Ø24 holes", B2F + "; D-133", "the ACP's 3 thickness, the jack's panel limit", "±0.2 (CNC router, "
    "assumption)", "routed with the skin blank (DXF)", "source (ELECTRICAL)")
FAMILIES[(LEDGE_BODY, 3.3, "x")] = (
    "F51", "The ledge's own rivet holes, matching F50, countersunk on the upright's room face so the heads sit flush",
    "838012, closed-end countersunk blind rivets ISO 15974 Ø3.2 x 8, heads flush in Ø6.7 x 120 countersinks (D-166)",
    "as F50: 6, symmetric about the ledge's middle", "the Lead's rulings of 2026-11-01 (WALL group): the ledge, its "
    "1.5 upright and flush heads (0.40 clear of the tray at J-FRAME-01's worst case)",
    "centre 9.0 from the upright's top edge (2.8 x d); the countersink's edge 5.4 from the top edge and 6.2 from the "
    "bend (calculation)", "±0.2 (assumption); countersink Ø per its rivet", "laser cut in the flat blank (DXF), "
    "countersunk by machining", "assumption")
FAMILIES[(LEDGE_BODY, 3.3, "y")] = FAMILIES[(LEDGE_BODY, 3.3, "x")]       # the back ledge's (211801), facing -Y
FAMILIES_BACK[("RAIL - BOTTOM", 3.3, "y")] = FAMILIES[("RAIL - BOTTOM", 3.3, "x")]   # the back rail's rivet holes

OTHER = [
    ("F10", "{frame}", "Five studs (0.8 wall, D-131 start; perimeter 1.0), set from the bolts: 50 past the 1st, "
     "50 before the 2nd, midway between the 2nd and 3rd, 50 past the 3rd, 50 before the 4th",
     "the skin flexes 2 mm or less under a 100 N push at a bay's centre (PM 2026-11-01; worst bay 240 clear, 1.52) "
     "and every bolt stays 30 or more clear of every stud (R-J14: 40); 4 even studs would stand 14 and 24 mm from two "
     "bolts", "stud_c1 to stud_c5 (calculation; test_wall_offline.py)", "follows wall_depth (edit test)",
     "cut list ±0.5 (assumption)", "DECIDED (PM 2026-11-01)"),
    ("F11", "{frame}", "Back stile 40 x 40 x 1.2", "room for the corner rivnut, its Ø20 stop washer and the bolt "
     "(37+ mm overlap instead of 17)", "PM ruling R-J3; %s 2.4, FR-06" % REG, "", "", "confirmed"),
    ("F12", "{frame}", "Rails run the full frame length; stiles fit between them (square butt ends)",
     "a continuous bottom rail sits on the band and its gasket in one line", "member joints: internal cleats per D-115 "
     "(corner and T cleats, crimped, structural adhesive; no welds; the cleats come from the Joints Engineer)", "", "",
     "DECIDED (D-115); cleats to come"),
    ("F13", "{fill}", "Fill notches 60 x 60, right through the 40 mm batt, beside every bolt this panel drives (4 "
     "above F01, 3 beside F07); each piece cut from its DXF (D-128)",
     "the 5 mm key reaches F02 and F08 from inside the pod before the cassette goes on", "%s FR-10, 2.3" % REG, "", "", "PROPOSED (assumption size)"),
    ("F14", "{skin}", "Skin back return: the side skin folds 43 mm round the frame's back end at an outside radius of "
     "2 (skin_fold_r; the maker's guide 01/2021/HDTC-VD 4.5), bonded to it through a 3 mm line (the frame stops bond_t "
     "short of the return)",
     "the back corner shows ACP, not the frame end (D-55; register section 7 item 5); every skin face that meets a frame "
     "is bonded at bond_t, no zero fits (the Lead's ruling, 2026-11-01)", "skin_ret = outer_t - skin_t (assumption); "
     "frm_len = pnl_len - skin_t - bond_t",
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




def _subs(text, pairs):
    for a, b in pairs:
        text = text.replace(a, b)
    return text


def holes(rep):
    rows = {}
    prm = {p["name"]: p["value"] for p in rep.get("parameters", [])}
    fold_d = 2.0 * prm.get("skin_fold_r", 0.0)
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
                # not holes: a convex face (a report since the fold radius flags it), and the skin fold's outside
                # radius in a report before that (a quarter cylinder at skin_fold_r; it is F14's)
                if h.get("convex") or (b["name"].startswith("SKIN") and fold_d and not h["full_circle"]
                                       and abs(h["d"] - fold_d) < 0.01):
                    continue
                # the cassette ledge's fold: its inside bend (radius ledge_r) is a part cylinder along the ledge
                if b["name"] == LEDGE_BODY and not h["full_circle"] and abs(h["d"] - 2 * prm.get("ledge_r", -1)) < 0.01:
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
    assy = panel["document"].split("_")[0]
    body_part = {}                       # D-120: a member's holes belong to the member's own number
    for rep in (panel, cass):
        for c in rep["components"]:
            for key, pre in (("frame", ("2111", "2112")), ("skin", ("2113", "2114")), ("fill", ("2115", "2116")),
                             ("tray", ("5111", "5112")), ("felt", ("5113", "5114"))):
                if c["part_number"].startswith(pre):
                    # D-120: the fill is several numbered pieces straight in the panel (D-123), all of them named
                    pns[key] = (pns[key] + " " + c["part_number"]) if key == "fill" and key in pns else c["part_number"]
            if c["part_number"].startswith("212"):
                for b in c["bodies"]:
                    body_part[b["name"]] = c["part_number"]
            if any(b["name"] == LEDGE_BODY for b in c["bodies"]):
                pns["ledge"] = c["part_number"]
    pns["assy"] = assy
    d117 = bool(body_part)
    back = pns["frame"].startswith("2112")
    families = {**FAMILIES, **FAMILIES_BACK, **FAMILIES_EL} if back else {**FAMILIES, **FAMILIES_EL}
    families.update(FAMILIES_D117)
    code = POSITIONS[pns["assy"][:4]][int(pns["assy"][4:6]) - 1]
    found = holes(panel)
    found.update(holes(cass))
    unexplained = []
    # D-163: the rivnut's hole and part follow the panel's own CAD (Ø10.00 and CAL2-610-4.2 from its D-163 rebuild,
    # Ø9.53 before it); the tables key a rivnut hole as RIVNUT_KEY and their text names the size and part read here
    prm = {p["name"]: p["value"] for p in panel.get("parameters", [])}
    rv_d = prm.get("rivnut_d", RIVNUT_KEY)
    rv_sku = next((m.group(1) for c in panel["components"] if c["part_number"] == "838003"
                   for m in [re.search(r"SHEREX (\S+)", c["name"])] if m), "CAH2-610-4.2")
    rv_text = [("Sherex CAH2-610-4.2", "Sherex %s" % rv_sku)]
    rv_hole = [("Ø9.53 +0.10 (Sherex)", "Ø%g +0.10 (%s)" % (rv_d, "D-163; Sherex %s" % rv_sku if rv_d > RIVNUT_KEY
                                                             else "Sherex")),
               ("15.2 ", "%.1f " % ((40.0 - rv_d) / 2))]           # its edge to each side face of a 40 mm wall
    for key, hs in sorted(found.items()):
        body, d, ax = key
        full = [h for h in hs if h["full_circle"]]
        rivnut = abs(d - rv_d) < 0.005
        fam = families.get((body, RIVNUT_KEY, ax) if rivnut else key)
        if fam is not None:
            fam = [_subs(f, rv_text + (rv_hole if rivnut else [])) for f in fam]
        if fam is None:
            if d == 8.5 and body == "RAIL - BOTTOM":
                fam = families[("RAIL - BOTTOM", 8.5, "z")]
            else:
                unexplained.append(key)
                continue
        cs = "; ".join("(%s)" % ", ".join("%g" % v for v in h["centre"] if v is not None) for h in hs)
        # a frame member's holes are the welded frame's: J-FRAME-01 makes every joint hole after welding, in the frame
        # (the drawing generator reads them under the frame's number, 211101 and so on)
        part = pns["felt"] if body == FELT else pns["tray"] if body == TRAY else pns["skin"] if body.startswith("SKIN") \
            else pns.get("ledge", "") if body == LEDGE_BODY else pns["frame"]
        lines.append("| %s | %s %s | Ø%g along %s, %d: %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            fam[0], part, body, d, ax, len(hs), cs, fam[1], fam[2], fam[3], fam[4], fam[5], fam[6], fam[7],
            fam[8]))
    if unexplained:
        raise SystemExit("holes with no rationale: %s" % unexplained)
    lines += ["", "Other features:", "", "| ID | Part | Feature | Why | Source or calculation | Edit behaviour | Tolerance | Status |",
              "|---|---|---|---|---|---|---|---|"]
    other = (OTHER_BACK if back else OTHER) + OTHER_EL.get(code, [])
    if d117:                             # the frame rebuilt as D-117 and D-120 ask: mitred, every member a part
        other = [D117_ROW if r[0] == "F12" else D131_LEAD_IN if r[0] == "F32" else r for r in other] + [D120_ROW]
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
