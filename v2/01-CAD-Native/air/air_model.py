"""Spaceship (FocusPod v2) AIR (D-60, D-61): parameters and layout, without Fusion.

The air column in the front-right inside corner, the soffit above the door head,
the splitter cartridge in each, the two fan boxes, the intake riser, the grilles
and the roof sleeve. Every size is a named parameter: the skeleton's own list
(loaded from its CSV, the highest revision in ../skeleton/), the ceiling's
cassette front edge (the soffit depth), and the AIR parameters below, each with
its status and source. Sizes come from the PM's rulings D-60 to D-62 and the
air report section 7e (v2/05-Engineering/acoustics-air/report.md, sized on
skeleton P04); where the report gives a position it is tied to the skeleton
here, so the parts follow it.

Coordinates: the pod system (conventions.md section 4), mm.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get("FRONT_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import ceiling_model as CM  # noqa: E402  (skeleton loader and expression tools)

REV = "P01"
R7E = "air report 7e (sized on skeleton P04)"

AIR_PARAMS = [
    # ---- floor and linings (PM rulings 2026-11-01 from BASE)
    ("col_gap", "5 mm", "mm", "confirmed", "PM ruling 2026-11-01 (BASE): the column keeps 5 mm off the floating side lining (D-17), X up to 1161; the soffit's ends the same"),
    # ---- FRONT's named values (350003 DR model; PM rulings 2026-11-01): the column and the whole soffit
    #      start at the room-side face of DR's access panel, so neither overlaps it. AIR keeps no copy:
    #      FRONT_ENTRIES() reads them, and any input they use, from FRONT's DR model at load (the Lead,
    #      2026-11-01: DR's panel face moved to Y -641.14 on its stops; read FRONT's named value)
    ("@FRONT", "", "", "", ""),
    # ---- faces of the column and the soffit
    ("face_acp", "3 mm", "mm", "source", R7E + ": faces 3 mm ACP + 9 mm felt"),
    ("face_felt", "9 mm", "mm", "source", R7E + ": faces 3 mm ACP + 9 mm felt"),
    ("face_t", "face_acp + face_felt", "mm", "calculation", "12 mm felt-covered face"),
    ("clr", "5 mm", "mm", "source", R7E + ": 5 mm round each cartridge and fan box, to slide it out"),
    # ---- column (front-right inside corner)
    ("col_x0", "949 mm", "mm", "source", R7E + ": the column's left face, X 949 (220 wide on P03, 217 on P04)"),
    ("col_d", "360 mm", "mm", "confirmed", "D-61: the room face 360 from the side walls' front end (Y -285), flush with the soffit's face; the column itself starts at DR's access-panel face, so it is 358.5 deep"),
    ("plen_lo", "120 mm", "mm", "source", R7E + ": the base plenum under the cartridge, 120 tall; now the least it may be, since the cartridge's foot follows FRONT's B01 screws (cart_b01_clr)"),
    ("grille_h", "100 mm", "mm", "confirmed", "D-61: a 100 mm kick grille at the column's foot"),
    ("grille_z", "10 mm", "mm", "source", R7E + ": kick grille Z 25 to 125, 10 mm above the column's foot"),
    ("grille_l", "312 mm", "mm", "source", R7E + ": 529 along the front and left faces, 217 of it on the front"),
    ("grille_t", "2 mm", "mm", "assumption", "perforated aluminium grille plates, flush with the room-side face; free area per the report, pattern HOLD"),
    ("hub_w", "180 mm", "mm", "confirmed", "D-61, D-70: a 180 x 180 zone for the sensor hub and controls"),
    ("hub_t", "29 mm", "mm", "source", R7E + ": up to 29 deep, no fill behind it"),
    ("hub_z", "1200 mm", "mm", "source", R7E + ": zone centred at Z 1200; across, it is centred between the front corner angles (X 1063.5 on P04, the report's 1058 is the column's centre)"),
    # ---- ELECTRICAL's hub and harness through the column and soffit (agreed by ELECTRICAL and CEILING 2026-11-01, the
    #      Lead's ask; the grommets are ELECTRICAL's parts): the hub takes the zone above, the harness enters through the FR
    #      angle, rises in a channel in the front fill and on the FR angle, and reaches the exhaust fans through the soffit
    ("hn_entry_d", "11.1 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): the harness's two entries through the FR angle's side leg, one per "
     "cable (5.3 and 4.2), each a Heyco SB 437-5 snap bushing's Ø11.1 hole (7.9 bore, panels to 3.2): 4.45 rims on "
     "the 20 mm leg of 2 mm, over the opening rule's 2 x the sheet"),
    ("hn_entry_dz", "40 mm", "mm", "confirmed", "ELECTRICAL and CEILING 2026-11-01: the entry 40 above the hub zone's "
     "bottom (Z 1150 at hub_z 1200), straight into the zone"),
    ("hn_entry_p", "25 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): the second entry 25 above the first (Z 1175)"),
    ("hn_tie_p", "15 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): each tie point is a pair of holes 15 apart in Z, so a plain tie loops "
     "out and back and only its 1.3 mm strap sits in the 5 mm gap to the lining (a push-mount tie's arrow would cross it)"),
    ("hn_tie_d", "6.4 mm", "mm", "confirmed", "ELECTRICAL and CEILING 2026-11-01: tie holes for the air-path leads "
     "(flame-rated, tied about every 150 mm: the Lead's rule)"),
    ("hn_tie_z1", "1960 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01: the FR angle's first tie hole, between the fill's top and the soffit"),
    ("hn_tie_z2", "dt_zb - 30 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01: the FR angle's second tie point, 30 under the "
     "soffit's underside (Z 2090), so its pair follows the column's top"),
    ("hn_ch_w", "24 mm", "mm", "confirmed", "ELECTRICAL and CEILING 2026-11-01: the 24 x 24 cable channels cut in the fills"),
    ("hn_sof_d", "12 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): the exhaust fan leads' hole through the soffit's fixed underside over the "
     "column (it crosses from the supply plenum into the soffit), sealed by a Heyco RLTCG M12 cordgrip (Ø12.0 hole, "
     "1.7 to 5.3 cable, IP68; no maker sheet shows a membrane grommet for Ø19.1 in 3 mm)"),
    ("hn_sof_felt", "30 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): the felt cut back to Ø30 round that hole, so the cordgrip grips only the "
     "3 mm ACP (hidden: the hole opens into the column)"),
    ("hn_sof_dy", "19 mm", "mm", "calculation", "that hole's centre 19 behind the fixed underside's room edge (Y -316): "
     "a 13 rim, over the opening rule's 6 on 3 mm ACP (2 x the sheet); over the front fill's channel"),
    ("hn_box_d", "12 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts): the hole in the exhaust fan box's bottom, a second M12 cordgrip"),
    ("hn_box_dy", "17.5 mm", "mm", "calculation", "that hole 17.5 inside the far-end lining's room-side edge (Y -392.6), "
     "so the lining's path round it keeps 5 mm of lining to that edge"),
    ("hn_lin_d", "25 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01 15:47 (sized to the real parts), CEILING's pick of the two ways: a Ø25 path for the leads up through the "
     "exhaust box's far-end lining over that hole, which sits under the lining (X 1108 to 1158); moving the hole to X 1095 "
     "would take the cable under the fan box's room-side mount angle"),
    ("hn_ty0", "43.5 mm", "mm", "confirmed", "ELECTRICAL 2026-11-01: the column's high plenum plate's first tie hole "
     "43.5 from the door side (Y -600), the others 100 apart (-500, -400)"),
    ("hn_tz", "15 mm", "mm", "calculation", "the plenum plate's tie holes 15 above its bottom edge (Z 1905): ELECTRICAL "
     "asked Z 1880, which is inside the cartridge since the follow-up lifted it 6"),
    ("chase_w", "30 mm", "mm", "source", R7E + ": a 30 x 30 cable chase in the column's front-left corner"),
    ("foot_t", "2 mm", "mm", "assumption", "column foot plate, aluminium; it closes the base plenum and takes BASE's two spigots"),
    ("spg1_x", "989 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S1 on F2 (X 989, Y -605), into a round hole"),
    ("spg1_y", "-605 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S1 on F2"),
    ("spg2_x", "1126 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S2 on F2 (X 1126, Y -337), into a slot"),
    ("spg2_y", "-337 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S2 on F2"),
    ("spg_hole", "8.5 mm", "mm", "confirmed", "R-J13 rule for spigots: 8.5 round at one, 8.5 x 14 slot at the other (along Y here)"),
    ("spg_slot", "14 mm", "mm", "confirmed", "R-J13: slot length"),
    ("plate_t", "1 mm", "mm", "assumption", "aluminium plates closing the column's right side at the two plenums, now that the column stands 5 mm off the lining"),
    ("hook_x", "971 mm", "mm", "confirmed", "PM ruling 2026-11-01: the column's two hook studs in DR's access panel at X 971 (FRONT's parts)"),
    ("hook_z1", "1700 mm", "mm", "confirmed", "PM ruling 2026-11-01: lower hook stud Z 1700"),
    ("hook_z2", "1850 mm", "mm", "confirmed", "PM ruling 2026-11-01: upper hook stud Z 1850"),
    ("key_d", "12 mm", "mm", "assumption", "keyhole's big hole, for a 10 mm stud head"),
    ("key_w", "6.5 mm", "mm", "assumption", "keyhole's slot and the rails' forks, for a 6 mm stud shank"),
    ("key_drop", "10 mm", "mm", "confirmed", "PM ruling 2026-11-01: the column drops 10 mm onto its studs and BASE's spigots"),
    ("ang_w", "20 mm", "mm", "assumption", "corner angle leg along the side faces; the report says 4 corner angles, size not given"),
    ("ang_f", "9 mm", "mm", "assumption", "corner angle leg along the front face: short, so the 180 hub zone fits between the two front corners (212 - 12 - 2 x 9 = 182)"),
    ("ang_t", "2 mm", "mm", "assumption", "corner angle thickness, aluminium"),
    # ---- cartridge (one part for both paths, D-61)
    ("cart_w", "173 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_d", "314 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_l", "1750 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_t", "2 mm", "mm", "confirmed", "D-61: 2 mm aluminium casing; D-121 withdrew D-116's 1.8 mm, since the noise margin is gone"),
    ("lay_t", "50 mm", "mm", "confirmed", "D-61: three 50 mm absorbent layers (Pyrotek Sorberpoly 2D at 32 kg/m3, report 7e; D-116)"),
    ("pass_w", "(cart_d - 2 * cart_t - 3 * lay_t) / 2", "mm", "calculation", "D-61: two 80 mm passages"),
    # ---- soffit (above the door head)
    ("sof_h", "220 mm", "mm", "confirmed", "D-61: soffit 220 tall, Z 2120 to 2340"),
    ("eg_x0", "16 mm", "mm", "source", R7E + ": exhaust grille from X -1150, 16 in from the soffit's left end"),
    ("eg_l", "265 mm", "mm", "source", R7E + ": exhaust grille 265 x 336"),
    ("eg_w", "336 mm", "mm", "source", R7E + ": exhaust grille 265 x 336"),
    ("fb_w", "294 mm", "mm", "source", R7E + ": exhaust fans and box 294 x 314 x 173"),
    ("sof_fill_t", "27 mm", "mm", "source", R7E + ": the exhaust cartridge sits on 27 mm of fill over the underside (Z 2159), as in the column"),
    ("lin_t", "50 mm", "mm", "source", R7E + ": fan boxes lined with 50 mm"),
    ("box_t", "2 mm", "mm", "source", R7E + ": 2 mm aluminium sheet, used for the soffit's left end plate"),
    ("fbox_t", "3 mm", "mm", "confirmed", "D-124: both fan box casings in 3 mm aluminium (boost about 29.5 dB(A) at 65 l/s, 66.6 l/s reach, +1.4 kg; the fan sample decides)"),
    # ---- soffit hanging (D-87; PM ruling 2026-11-01): open forks in two top rails on 4 studs in
    #      the ceiling frame, lift and slide toward the door, 2 captive lock screws; the underside
    #      in two hinged sections and a fixed strip over the column
    ("rail_t", "3 mm", "mm", "assumption", "soffit top rails, aluminium flat bar, riveted to the door-side plate and the front face"),
    ("dp_t", "2 mm", "mm", "assumption", "soffit door-side plate: carries the door-side rail, closes the soffit against DT's back plate and DR's back (DR's riveted band stays: PM ruling 2026-11-01)"),
    ("rail_w", "24 mm", "mm", "assumption", "soffit top rail width (room side); the door-side rail runs from the soffit's door side to 24 from the side walls' front end (22.5 wide), so it stays 1 mm clear of the roof sleeve"),
    ("stud_l", "16 mm", "mm", "confirmed", "D-90 (HOLD-18, joints register #99): the hanger studs are M6 x 16 socket head bolts"),
    ("stud_eng", "9 mm", "mm", "assumption", "thread engaged in the ceiling's rivnut (10.16 installed length less the lead-in)"),
    ("rvn_head", "0.76 mm", "mm", "source", "H-03 rivnut head under the frame face (Sherex CAH2-610-4.2, 0.76, SHX2)"),
    ("hd_h", "6 mm", "mm", "source", "ISO 4762 M6 head height 6 (the studs and the lock screws)"),
    ("hd_c", "1.5 mm", "mm", "confirmed", "D-90 (HOLD-18): 1.5 clear under each head"),
    ("stud_d", "10 mm", "mm", "source", "ISO 4762 M6 head diameter 10"),
    ("slide", "24 mm", "mm", "calculation", "the soffit is lifted this far behind its place and slid toward the door: the studs start clear of both rails' edges"),
    ("us_gap", "2 mm", "mm", "assumption", "gap between the underside sections"),
    ("hinge_l", "60 mm", "mm", "assumption", "hinge envelope along the door-side edge, HOLD"),
    ("latch_l", "30 mm", "mm", "assumption", "push latch envelope at the room-side edge, HOLD"),
    ("hl_h", "8 mm", "mm", "assumption", "hinge and latch envelope height above the underside"),
    # ---- the soffit's supports and service parts (the Lead's rulings 2026-11-01, Control's numbers): the cartridge on
    #      two straps, the fan box on four isolating mounts, the fill bonded to the sections from the hinge line, the
    #      push latches in brackets, the hinges' space (611212, designed by the AIR Transitions Engineer)
    ("us_jg", "2 mm", "mm", "confirmed", "the Lead 2026-11-01 (the soffit hinge): a 2 mm joint along the underside's door "
     "edge, as between the sections; fitting needs one too"),
    ("hg_res_y", "28 mm", "mm", "calculation", "the hinge 611212's reserved space from the section's door edge: its pin "
     "about 20 in, at the ACP (CEILING's swing check, the Lead's ruling), its knuckle and leaves behind it"),
    ("hg_res_h", "24 mm", "mm", "calculation", "the hinge's reserved space above the ACP, 3 under the straps' pads"),
    ("st_w", "30 mm", "mm", "assumption", "the cartridge strap 611213: a 6063-T6 aluminium angle 30 x 20 x 2, its 30 leg "
     "flat under the cartridge (5:1 at 52 N a strap: about 40 MPa over its 340 span, calculation)"),
    ("st_h", "20 mm", "mm", "assumption", "the strap's 20 leg, down"),
    ("st_t", "2 mm", "mm", "assumption", "the strap's wall"),
    ("st_pad_t", "3 mm", "mm", "assumption", "the strap pad 618107 (HOLD: Sourcing Engineer 2 picks it): 3 thick"),
    ("st_pad_l", "300 mm", "mm", "assumption", "the strap pad's length under the cartridge's 314 depth"),
    ("sa_l", "40 mm", "mm", "assumption", "the strap's support angles 611214 (4: one at each end of each strap, on the "
     "door-side plate and on the front face): 6063-T6 30 x 30 x 2, 40 long"),
    ("sa_w", "30 mm", "mm", "assumption", "the support angle's legs"),
    ("mt_d", "19.05 mm", "mm", "source", "Sorbothane 0510111-50-10 isolation hemisphere: Ø19.05 (the Sourcing Engineer's "
     "pick, the Lead's ruling 2026-11-01)"),
    ("mt_h", "9.5 mm", "mm", "source", "Sorbothane 0510111-50-10: 9.5 tall"),
    ("ma_t", "2 mm", "mm", "assumption", "the fan box mount angles 611409: 2 mm aluminium"),
    ("ma_w", "53 mm", "mm", "calculation", "the mount angle's flat leg: from its plate to 28 under the box's wall, the "
     "same part on both sides (turned 180 deg)"),
    ("ma_h", "30 mm", "mm", "assumption", "the mount angle's upright leg, riveted to its plate"),
    ("mt_in", "14 mm", "mm", "assumption", "each mount 14 in from the box's door or room wall"),
    ("mt_x1", "33 mm", "mm", "assumption", "the mounts 33 in from the box's left end"),
    ("mt_x2", "51 mm", "mm", "calculation", "and 51 in from its right end (X 1110: 8.5 clear of the harness channel)"),
    ("lt_bw", "20.5 mm", "mm", "source", "Southco E4-10-201-10 (the latch 618106, the Lead's pick 2026-11-01): body 20.5 x 13, "
     "29 long"),
    ("lt_bd", "13 mm", "mm", "source", "Southco E4-10-201-10: body 13"),
    ("lt_bl", "29 mm", "mm", "source", "Southco E4-10-201-10: latch 29 long"),
    ("lt_in", "17 mm", "mm", "confirmed", "the latch's axis 17 in from the section's room edge: its keeper 10 to 20 in "
     "(CEILING's need, the Sourcing pick)"),
    ("lt_z0", "3 mm", "mm", "assumption", "the latch's mouth 3 over the ACP: the keeper's 2 base and its hook's lead-in"),
    ("lb_t", "1.5 mm", "mm", "source", "the latch bracket 611215: 1.5 mm aluminium, inside E4's 1-3 mm mounting plate"),
    ("lb_w", "25 mm", "mm", "assumption", "the latch bracket's width along X"),
    ("lb_h", "30 mm", "mm", "assumption", "the latch bracket's upright leg, riveted to the front face before the felt"),
    ("lb_z", "14 mm", "mm", "assumption", "the latch bracket's tab 14 over the latch's mouth, holding the body by its middle"),
    ("sf_y1_gap", "30 mm", "mm", "calculation", "the bonded fill stops 30 short of the front face, where the latches and "
     "the straps' room ends sit"),
    ("sf_ff_dz", "24 mm", "mm", "calculation", "the front fill's foot 24 over the cartridge's bottom: clear of the room-side "
     "angles' upright legs (to 23) and the latches' brackets (to 20)"),
    ("lt_cx", "19 mm", "mm", "source", "Southco E4-10-201-10: snaps into a 19 x 11.5 cut-out (the latch bracket's tab)"),
    ("lt_cy", "11.5 mm", "mm", "source", "Southco E4-10-201-10: the cut-out's 11.5"),
    # ---- fans (selection F1, D-51)
    ("fan_s", "140 mm", "mm", "source", "Noctua NF-A14 industrialPPC-3000 PWM: 140 x 140 x 25 (selection F1)"),
    ("fan_t", "25 mm", "mm", "source", "Noctua NF-A14 industrialPPC-3000 PWM: 140 x 140 x 25 (selection F1)"),
    ("lock_hole", "7.0 mm", "mm", "source", "the joints register's R-J6: M6 bolt clearance holes 7.0 (the mechanical checks' C08 found 6.6 here, 0.31 mm of float over a rivnut)"),
    # ---- FRONT's panel screws that stand into AIR's space (D-130's one panel on its stops; the Lead's rulings
    #      2026-11-01: heads stay 7.6 proud; the supply cartridge lifted 6 over B01's two; B08's three relieved in
    #      the soffit's door plate and fill, nothing showing from below; B07's lowest moved clear by FRONT)
    ("fr_hd_d", "10 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): M6 x 16 socket heads, ISO 4762, 10 across"),
    ("fr_hd_h", "6 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): M6 socket heads 6 high"),
    ("fr_wsh_d", "12 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): plain washers ISO 7089 M6, 12 across"),
    ("fr_wsh_t", "1.6 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): plain washers ISO 7089 M6, 1.6 thick (head and washer 7.6 proud)"),
    ("fr_scr_clr", "1 mm", "mm", "assumption", "AIR's clearance round FRONT's screw heads and washers, and in each relief"),
    ("b08_x1", "499.0 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B08's first screw"),
    ("b08_x2", "821.7 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): B08's second screw"),
    ("b08_x3", "1144.4 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): B08's third screw"),
    ("b08_z", "2140.1 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B08's three screws' height"),
    ("b01_x1", "1000.2 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): B01's first screw, under the supply cartridge"),
    ("b01_x2", "1145.1 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): B01's second screw, under the supply cartridge"),
    ("b01_z", "130.0 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B01's two screws' height (washers to Z 136; the cartridge from Z 140)"),
    ("cart_b01_clr", "4 mm", "mm", "confirmed", "the Lead's ruling 2026-11-01: the supply cartridge, lifted 6 (the Air Engineer's fix), stands 4 over the washers of B01's two screws; tied to them, so it holds when BASE's D-132 takes the floor out (floor top Z 12 to 0)"),
    ("b07_x", "939.0 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B07's lowest screw, moved 4 clear of the column's left face"),
    ("b07_z", "281.4 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): B07's lowest screw's height (was 259.8)"),
    ("blk_t", "2 mm", "mm", "source", "the air report's sizing (calc.py, D-121): each fan box's 2 mm aluminium bulkhead, the fans mounted on it"),
    ("fan_bore", "135 mm", "mm", "source", "the air report's fan bore (calc.py FAN_BORE 0.135 m): the bulkhead's opening at each fan"),
    ("fan_hp", "124.5 mm", "mm", "source", "Noctua NF-A14 (140 mm frame): its 4 mounting holes on a 124.5 mm square (the maker's data sheet, selection F1)"),
    ("fan_hole", "4.5 mm", "mm", "assumption", "clearance in the bulkhead for each fan screw into the fan's corner hole (the screw HOLD with the fan's mounting)"),
    ("s_lin_gap", "70 mm", "mm", "source", "D-121, the Air Engineer: the supply box's end-wall linings start about 70 mm above the fans, so the air reaches them"),
    ("e_lin_gap", "50 mm", "mm", "source", "D-121, the Air Engineer: the exhaust box's far-end lining stops 50 mm under the fans"),
    # ---- supply fan box and intake riser, inside the right decor block (D-61, D-62)
    ("sb_x0", "680 mm", "mm", "source", "PM ruling 2026-11-01 (the AIR Transitions Engineer's find, the Lead's ruling): the "
     "supply fan box X 680 to 980, 6.3 mm off DR's back ring diagonal tube B06 on FRONT's #313 STEP (at X 673, with the glue "
     "line and the box 3 mm back, it was 1.0) and 8.1 off the front ring's diagonal (FRONT's fan box points had X 673; "
     "report 7e X 645)"),
    ("sb_w", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_d", "155 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_h", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_yf", "31 mm", "mm", "source", "PM ruling 2026-11-01 and FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): the supply fan box's front face at Y -819, 5 mm "
     "behind the cross tube F09 over it (Z 1904 to 1924), now 3 off the skin (was 28: Y -822)"),
    ("sb_z0", "1650 mm", "mm", "source", R7E + ": supply fan box Z 1650 to 1950"),
    ("rs_x0", "959 mm", "mm", "source", "FRONT's DR rebuild with D-137's 3 mm glue line (#313 at 541fe7f, FRONT Engineer, 2026-11-01 10:47): the riser's space X 959 to 1098, 5.9 off the glass-edge tube B07 (was 956; "
     "report 7e had 955)"),
    ("rs_w", "139 mm", "mm", "source", R7E + ": intake riser 139 wide, 155 deep"),
    ("rs_d", "150 mm", "mm", "source", "the air report's D-130 table (riser_y, riser_lo): the riser Y -803 to -653, 6.5 off "
     "DR's frame face (was 155; FRONT's ri_d follows with D-130). Its front-right edge runs 1.2 from DR's corner facet "
     "skin over its height, measured on #313's DR (the air report's 4.8 predates the 3 mm move right)"),
    ("rs_y0", "-803 mm", "mm", "source", R7E + ": intake riser Y -803 to -648"),
    ("rs_z0", "252 mm", "mm", "source", "FRONT's reserved space for the riser (DR model on main: its open foot 140 over DR's "
     "base, Z 252); D-130's sealed intake boot (611502, to come) takes the air from the mesh up to this foot (was Z 105)"),
    ("rs_z1", "1386 mm", "mm", "confirmed", "the Lead's ruling 2026-11-01 in the transitions group: the riser cut 60 "
     "shorter (was 1445, the air report's), so the lower duct's turn eases to 52 deg; the AIR Transitions Engineer's shape"),
    ("rs_t", "1 mm", "mm", "confirmed", "D-61: 1 mm steel intake riser"),
    ("rs_ch", "8 mm", "mm", "confirmed", "the Lead's ruling 2026-11-01: an 8 x 8 chamfer on the riser's front-right vertical "
     "edge, so it stands 6.5 from DR's corner facet skin instead of 1.2 (calculation on #313's DR STEP; the ruling said "
     "6.8), for 0.15% of its area; the lower duct's bottom flange follows it (the AIR Transitions Engineer)"),
    # ---- the transitions' 24 rivet holes in the riser and the supply box casing (the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes)): Ø4.1, made in both parts'
    #      flats so they match without drilling (the Lead's ruling 2026-11-01: no hole is drilled on site); the box, the
    #      riser and both transitions ship as one piece, so the rivets are set at the factory
    ("tr_rv_d", "4.1 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): Ø4.1 for a Ø4.0 blind rivet until Joints picks the rivet (HOLD)"),
    ("tr_col_in", "25 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the lower transition's collar slips 25 into the riser's top; its 10 "
     "rivets at the overlap's middle (Z 1373.5)"),
    ("tr_rs_py", "50.5 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): 3 rivets in each of the riser's side walls, 50.5 apart about its middle"),
    ("tr_rs_x1", "33.5 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the riser's front and back walls, the first rivet 33.5 from its left face "
     "(X 992.5)"),
    ("tr_rs_x2", "92.5 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the riser's front and back walls, the second rivet 92.5 from its left face "
     "(X 1051.5, clear of the chamfer)"),
    ("tr_be_dz", "10 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): 3 rivets in each of the box's end walls 10 above its bottom (Z 1660), "
     "through the lower transition's webs"),
    ("tr_be_py", "50.5 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the box's end-wall rivets 50.5 apart about its middle"),
    ("tr_bf_dz", "9 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): 4 rivets in the box's front wall 9 below its top (Z 1941), into the upper "
     "transition's front"),
    ("tr_bf_px", "164 mm / 3", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the box's front-wall rivets X 748 to 912, even about its middle"),
    ("tr_bb_dz", "58.5 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): 4 rivets in the box's back wall 58.5 below its top (Z 1891.5), into the "
     "upper transition's back flange"),
    ("tr_bb_x0", "70.9 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the box's first back-wall rivet 70.9 from its left face (X 750.9)"),
    ("tr_bb_px", "54.4 mm", "mm", "source", "the AIR Transitions Engineer's hole list 2026-11-01 (the transitions' flats carry the same holes): the box's back-wall rivets 54.4 apart"),
    # ---- how the supply fan box assembly rests in DR (PM rulings 2026-11-01, after the box moved back): a lip angle on
    #      the box's front wall on two rubber pads on DR's shelf tube F08, and a rubber buffer on the riser's front face
    #      against DR's cross tube F07; the outlet's soft lip seal carries no load. DR's frame values are FRONT's (its DR
    #      STEP on main, 350003 P01): F08 Y -847 to -827, top Z 1650 (fb_z0), right end X 1030.85 at the facet side tube
    #      F02; F07 Z 834 to 854, the same right end
    ("dr_skin_t", "3 mm", "mm", "source", "FRONT's DR skin, ACP 3 (DR model's dr_skin_t): DR's front ring tubes start behind it"),
    ("dr_fr_w", "20 mm", "mm", "source", "FRONT's DR frame tube 20 x 20 (DR model's fr_w): F07 and F08"),
    ("dr_f08_x1", "1029.7 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): F08's and F07's right end, at the facet side tube F02's inner face"),
    ("dr_f07_zc", "844 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): F07, the front ring's cross tube, Z 834 to 854"),
    ("lip_t", "3 mm", "mm", "source", "Control's allocation of 611408 (#279): a 3 mm aluminium lip angle, as the casing"),
    ("lip_h", "40 mm", "mm", "assumption", "the lip's upright leg on the box's front wall, room for its 3 rivets 20 above the "
     "foot leg and below the bulkhead (Z 1698)"),
    ("lip_tip", "2 mm", "mm", "calculation", "the lip's tip stays this far off DR's skin (the PM's 25 mm reach less 2)"),
    ("lip_end", "5 mm", "mm", "calculation", "the lip's right end this far short of F02 (X 1025.85)"),
    ("pad_l", "40 mm", "mm", "source", "Control's allocation of 618402 (#279): rubber pad 40 x 15 x 5"),
    ("pad_w", "15 mm", "mm", "source", "Control's allocation of 618402 (#279): rubber pad 40 x 15 x 5"),
    ("pad_t", "5 mm", "mm", "source", "Control's allocation of 618402 (#279): rubber pad 40 x 15 x 5"),
    ("pad_in", "5 mm", "mm", "calculation", "each pad this far in from the lip's ends: the left at X 678, the right at X 980.85, "
     "on F08's free end past the box, since the riser puts the weight centre near the box's right end (about X 940)"),
    ("buf_d", "20 mm", "mm", "assumption", "the riser buffer's rubber body, about 20 across (product HOLD)"),
    ("buf_gap", "0 mm", "mm", "calculation", "the buffer is set to touch F07: about 15 N of the assembly's lean (CEILING, "
     "2026-11-01) holds the riser's foot back with DR's inner panel off"),
    # ---- the upper transition (618102) over the box and in the passage beside it, full depth (PM rulings 2026-11-01,
    #      the Air Engineer's report #283): from the box's front line to DR's frame face, Z 1895 to 2110, kept ut_clr off
    #      the corner facet's shelf tube C04 (Z 1930 to 1950), whose inner face runs between these two plan points
    #      (FRONT's DR STEP on main, 350003 P01)
    ("dr_fac_xa", "1049.7 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): C04's inner face, front end, X"),
    ("dr_fac_ya", "-817.11 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): C04's inner face, front end, Y"),
    ("dr_fac_xb", "1217.23 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): C04's inner face, back end, X"),
    ("dr_fac_yb", "-666.5 mm", "mm", "source", "FRONT's DR STEP on #313 (541fe7f, 350003 P01, every tube 3 off its skin): C04's inner face, back end, Y"),
    ("ut_clr", "3 mm", "mm", "assumption", "the transition keeps this far off C04, so no metal touches DR's frame"),
    ("air_sk_ref", "4000 mm", "mm", "assumption", "the polygon sketches' reference point sits this far off the origin on "
     "both axes, so each corner's dimension stays positive whatever the pod's size (FRONT's sk_ref pattern)"),
    ("fac_len", "sqrt((dr_fac_xb - dr_fac_xa) * (dr_fac_xb - dr_fac_xa) + (dr_fac_yb - dr_fac_ya) * (dr_fac_yb - dr_fac_ya))",
     "mm", "calculation", "C04's inner face, its length in plan"),
    ("ut_ax", "dr_fac_xa - ut_clr * (dr_fac_yb - dr_fac_ya) / fac_len", "mm", "calculation",
     "the transition's facet side: C04's inner face moved ut_clr into DR, a point on it, X"),
    ("ut_ay", "dr_fac_ya + ut_clr * (dr_fac_xb - dr_fac_xa) / fac_len", "mm", "calculation", "the same point, Y"),
    ("ut_xf", "ut_ax + (-pod_d / 2 + sb_yf - ut_ay) * (dr_fac_xb - dr_fac_xa) / (dr_fac_yb - dr_fac_ya)", "mm",
     "calculation", "the transition's facet side meets its front (the box's front line), X (about 1044)"),
    ("ut_yr", "ut_ay + (op_x0 + op_w - ut_ax) * (dr_fac_yb - dr_fac_ya) / (dr_fac_xb - dr_fac_xa)", "mm",
     "calculation", "the transition's facet side meets its right end (the opening's, X 1161), Y (about -717)"),
    # ---- roof slot, sleeve and grille (D-61: Y -620 to -326, in the right outer ceiling panel)
    ("slv_t", "1 mm", "mm", "assumption", "roof sleeve wall, galvanised steel"),
    ("rg_t", "2 mm", "mm", "assumption", "roof grille plate; 50 % free or more (report 7e), pattern HOLD"),
    # the sleeve's top flange on C2's skin, with the grille's 4 rivnuts 838003 (J-AIR-03, HOLD-04's edge rule: each
    # rivnut 2 hole diameters from every free edge, the skin's slot edge too; CEILING's layout, 2026-11-01): 2 on the
    # left side; 2 on the back side BEHIND cross member 1, whose front face is too near the slot for a set rivnut's
    # bulge; none on the front (the front member under the skin) or the right (19.0 to the side member)
    ("slv_rn_e", "20.0 mm", "mm", "calculation", "rivnut centre to any free edge: 2 x the Ø10.00 hole (D-163; HOLD-04's rule; "
     "was 19.2 for the Ø9.53), as the ceiling's"),
    ("slv_rn_in", "20 mm", "mm", "assumption", "the rivnuts this far in from the slot's corners along their sides"),
    ("slv_bulge", "14 mm", "mm", "assumption", "a set rivnut's blind-side bulge, about 14 across (the hole FRONT clears for body and "
     "bulge, DR model fr_hole_jf; Sherex gives no size)"),
    ("slv_rn_clr", "1 mm", "mm", "assumption", "the bulge's clearance to cross member 1's back face"),
    ("slv_fl_l", "40 mm", "mm", "calculation", "the flange on the slot's left side: its rivnuts slv_rn_e in, slv_rn_e to its edge, rounded up"),
    ("slv_fl_f", "15 mm", "mm", "assumption", "the flange on the front and right sides: no rivnuts there"),
    ("slv_rn_yb", "%s + tube_w + slv_bulge / 2 + slv_rn_clr" % CM.cross_y0(1), "mm", "calculation",
     "the back side's rivnuts behind cross member 1: its back face plus half the bulge plus the clearance (Y -273)"),
    ("slv_fl_b", "slv_rn_yb + slv_rn_e - (slot_y0 + slot_d)", "mm", "calculation",
     "the flange on the slot's back side, out to slv_rn_e behind those rivnuts (about 72)"),
]

PARTS = {   # key: part number, name, Vietnamese name, kind, material key
    "air": ("610000", "AIR", "Thông gió", "HS", None),
    "column": ("610101", "AIR - AIR COLUMN", "Cột gió (cụm)", "HS", None),
    "soffit": ("610201", "AIR - SOFFIT", "Hộp gió trần trên cửa (cụm)", "HS", None),
    "cart": ("610301", "AIR - SPLITTER CARTRIDGE - COMMON", "Ống tiêu âm (dùng chung cấp/thải)", "HS", None),
    "sbox": ("610401", "AIR - SUPPLY FAN BOX", "Hộp quạt cấp (cụm)", "HS", None),
    "ebox": ("610402", "AIR - EXHAUST FAN BOX", "Hộp quạt thải (cụm)", "HS", None),
    "col_front": ("611101", "AIR - COLUMN FACE - FRONT", "Cột gió - mặt trước (ACP + nỉ)", "MP", "face"),
    "col_left": ("611102", "AIR - COLUMN FACE - LEFT", "Cột gió - mặt trái (ACP + nỉ)", "MP", "face"),
    "col_ang": ("611103", "AIR - COLUMN CORNER ANGLE - FRONT", "Cột gió - thanh góc nhôm phía trước", "MP", "alx"),
    "col_ang_b": ("611109", "AIR - COLUMN CORNER ANGLE - BACK", "Cột gió - thanh góc nhôm phía sau", "MP", "alx"),
    "col_fill": ("611104", "AIR - COLUMN FILL - FRONT", "Cột gió - bông - tấm trước", "MP", "pfill"),
    "col_fill_l": ("611110", "AIR - COLUMN FILL - LEFT", "Cột gió - bông - tấm trái", "MP", "pfill"),
    "kick": ("611105", "AIR - KICK GRILLE - FRONT", "Lưới gió chân cột - tấm trước", "MP", "perf60"),
    "kick_l": ("611111", "AIR - KICK GRILLE - LEFT", "Lưới gió chân cột - tấm trái", "MP", "perf60"),
    "col_foot": ("611106", "AIR - COLUMN FOOT PLATE", "Cột gió - tấm chân", "MP", "al"),
    "col_side_lo": ("611107", "AIR - COLUMN PLENUM SIDE PLATE - LOW", "Cột gió - tấm hông buồng dưới", "MP", "al"),
    "col_side_hi": ("611108", "AIR - COLUMN PLENUM SIDE PLATE - HIGH", "Cột gió - tấm hông buồng trên", "MP", "al"),
    "sof_under": ("611201", "AIR - SOFFIT UNDERSIDE - LEFT HINGED", "Hộp gió - mặt dưới trái (bản lề, màu tối)", "MP", "face"),
    "sof_under_r": ("611207", "AIR - SOFFIT UNDERSIDE - RIGHT HINGED", "Hộp gió - mặt dưới phải (bản lề, màu tối)", "MP", "face"),
    "sof_under_f": ("611208", "AIR - SOFFIT UNDERSIDE - FIXED OVER THE COLUMN", "Hộp gió - mặt dưới cố định trên cột", "MP", "face"),
    "sof_rail_d": ("611205", "AIR - SOFFIT TOP RAIL - DOOR SIDE", "Hộp gió - thanh treo phía cửa", "MP", "al"),
    "sof_rail_r": ("611209", "AIR - SOFFIT TOP RAIL - ROOM SIDE", "Hộp gió - thanh treo phía trong", "MP", "al"),
    "sof_end": ("611206", "AIR - SOFFIT END PLATE - LEFT", "Hộp gió - tấm đầu trái", "MP", "al"),
    "sof_door": ("611210", "AIR - SOFFIT DOOR-SIDE PLATE", "Hộp gió - tấm phía cửa", "MP", "al"),
    "sof_front": ("611202", "AIR - SOFFIT FACE - FRONT", "Hộp gió - mặt trước", "MP", "face"),
    "sof_fill": ("611203", "AIR - SOFFIT FILL - LEFT", "Hộp gió - bông - tấm trái", "MP", "pfill"),
    "sof_fill_r": ("611216", "AIR - SOFFIT FILL - RIGHT", "Hộp gió - bông - tấm phải", "MP", "pfill"),
    "sof_fill_c": ("611217", "AIR - SOFFIT FILL - OVER THE COLUMN", "Hộp gió - bông - tấm trên cột", "MP", "pfill"),
    "sof_fill_f": ("611211", "AIR - SOFFIT FILL - FRONT", "Hộp gió - bông - tấm trước", "MP", "pfill"),
    "egrille": ("611204", "AIR - EXHAUST GRILLE", "Lưới gió thải", "MP", "perf40"),
    "casing": ("611301", "AIR - CARTRIDGE CASING", "Vỏ ống tiêu âm nhôm 2 mm", "MP", "al"),
    "layer": ("611302", "AIR - CARTRIDGE FILL - LAYER 50", "Bông tiêu âm - lớp 50 mm", "MP", "pyro"),   # a fill (D-89 part 3)
    "box": ("611401", "AIR - FAN BOX CASING - EXHAUST", "Vỏ hộp quạt thải nhôm 3 mm", "MP", "al"),
    "box_s": ("611402", "AIR - FAN BOX CASING - SUPPLY", "Vỏ hộp quạt cấp nhôm 3 mm", "MP", "al"),
    "blk_e": ("611403", "AIR - FAN BOX BULKHEAD - EXHAUST", "Hộp quạt thải - vách ngăn nhôm 2 mm", "MP", "al"),
    "blk_s": ("611404", "AIR - FAN BOX BULKHEAD - SUPPLY", "Hộp quạt cấp - vách ngăn", "MP", "al"),
    "lin_es": ("611405", "AIR - FAN BOX LINING - EXHAUST SIDE", "Hộp quạt thải - lớp lót bên", "MP", "pyro"),
    "lin_ee": ("611406", "AIR - FAN BOX LINING - EXHAUST FAR END", "Hộp quạt thải - lớp lót đầu xa", "MP", "pyro"),
    "lin_s": ("611407", "AIR - FAN BOX LINING - SUPPLY END", "Hộp quạt cấp - lớp lót đầu", "MP", "pyro"),
    "riser": ("611501", "AIR - INTAKE RISER", "Ống hút gió đứng", "MP", "steel"),
    "sleeve": ("611601", "AIR - ROOF SLEEVE", "Ống thải qua mái", "MP", "steel"),
    "rgrille": ("611602", "AIR - ROOF GRILLE", "Lưới thải mái", "MP", "perf50"),
    "fan": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V 140 mm", "PI", "fan"),
    # the hinge 611212 replaces 618105 (made; the AIR Transitions Engineer designs it in the reserved space)
    "hinge": ("611212", "AIR - SOFFIT UNDERSIDE HINGE - RIVETED PIN - HOLD", "Hộp gió - bản lề mặt dưới - chốt tán (chờ)", "MP",
              "hold"),
    "latch": ("618106", "AIR - SOFFIT UNDERSIDE LATCH - PUSH TO CLOSE", "Chốt bấm mặt dưới hộp gió", "PI", "hold"),
    "lt_br": ("611215", "AIR - SOFFIT LATCH BRACKET", "Hộp gió - giá chốt bấm", "MP", "al"),
    "strap": ("611213", "AIR - SOFFIT CARTRIDGE STRAP", "Hộp gió - đai đỡ ống tiêu âm", "MP", "alx"),
    "st_ang": ("611214", "AIR - SOFFIT CARTRIDGE STRAP ANGLE", "Hộp gió - thanh góc đỡ đai", "MP", "alx"),
    "st_pad": ("618107", "AIR - SOFFIT CARTRIDGE STRAP PAD - HOLD", "Hộp gió - đệm xốp đai đỡ ống tiêu âm (chờ)", "HOLD",
               "hold"),
    "m_ang": ("611409", "AIR - FAN BOX MOUNT ANGLE", "Hộp quạt thải - thanh góc đỡ chân cách rung", "MP", "al"),
    "mount": ("618403", "AIR - FAN BOX MOUNT - EXHAUST - HOLD", "Hộp quạt thải - chân cách rung (chờ)", "PI", "hold"),
    "trans": ("618102", "AIR - SUPPLY TRANSITION - HOLD", "Ống chuyển cấp (chờ)", "HOLD", "hold"),
    "rtrans": ("618103", "AIR - RISER TRANSITION - HOLD", "Ống chuyển hút (chờ)", "HOLD", "hold"),
    # how the supply fan box assembly rests in DR (PM rulings 2026-11-01; Control's numbers and names, #279)
    "lip": ("611408", "AIR - FAN BOX LIP ANGLE - SUPPLY", "Hộp quạt cấp - thanh góc mép nhôm 3 mm", "MP", "al"),
    "pad": ("618402", "AIR - FAN BOX PAD - SUPPLY - RUBBER 40 X 15 X 5 - HOLD", "Hộp quạt cấp - đệm cao su 40 x 15 x 5 (chờ)",
            "PI", "hold"),
    "buffer": ("618501", "AIR - RISER BUFFER - RUBBER - M6 - HOLD", "Ống hút gió đứng - đệm cao su ren M6 (chờ)", "PI", "hold"),
}

# joint hardware from the joints register used in AIR (D-63): the soffit's two captive lock
# screws (PM ruling 2026-11-01), into the ceiling's rivnuts; their captive retainer is HOLD
HARDWARE = {
    # the soffit's four hanger studs are the register's M6 x 16 socket head bolt 838001 (D-90, HOLD-18; the Sourcing
    # Engineer's find, the Lead's ruling 2026-11-01: 618104 cancelled), into the ceiling's rivnuts
    "stud": ("838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16", 4,
             0.0062),
    "lock": ("838002", "HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC",
             "Bulong lục giác chìm M6 × 25 (chốt mối nối khép)", 2, 0.0079),
    # the roof grille's fixings (the Air Engineer, 2026-11-01, Packing's open item from #265): the grille goes on from
    # the roof after the soffit hangs, over the roof sleeve's top flange, with the pod's one 5 mm key (R-J2): 4 M6 x 16
    # socket head bolts and washers into 4 M6 rivnuts the factory sets in the sleeve's flange, one near each corner
    "grille_bolt": ("838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC",
                    "Bulong lục giác chìm M6 × 16", 4, 0.0062),
    "grille_washer": ("838004", "HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2",
                      "Long đen to M6 inox", 4, 0.0028),
    "grille_rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2", "Tán rút M6 thép mạ kẽm", 4, 0.0067),
    # the riser buffer 618501 screws into one rivnut set at the factory in the riser's front wall (PM ruling 2026-11-01)
    "buffer_rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2", "Tán rút M6 thép mạ kẽm", 1,
                      0.0067),
}

MATERIALS = {
    "al": ("Aluminium 5052-H32 sheet (alloy HOLD)", 2700.0),         # C11: a named alloy and temper; the factory confirms
    "alx": ("Aluminium 6063-T6 extrusion (alloy HOLD)", 2700.0),     # the column's corner angles
    "perf60": ("Perforated aluminium, 60 % free", 2700.0 * 0.4),
    "perf40": ("Perforated aluminium, 40 % free", 2700.0 * 0.6),
    "perf50": ("Perforated aluminium, 50 % free", 2700.0 * 0.5),
    "steel": ("Galvanised steel DX51D+Z", 7850.0),
    "face": ("ACP 3 + felt 9 face (5.3 kg/m2)", 5.3 / 0.012),
    "pfill": ("Polyester fill 24 kg/m3", 24.0),     # D-81: the lighter cavity fill (provisional on T02); the layers stay at 32
    "pyro": ("Pyrotek Sorberpoly 2D 32 kg/m3", 32.0),      # D-116: the density Pyrotek's published absorption is for (selection.md)
    "fan": ("Fan envelope 0.3 kg (assumption)", 0.3 / (0.14 * 0.14 * 0.025)),
    "hold": ("HOLD envelope - no mass", 1.0),
}

# skeleton planes (expressions)
XIR = "(pod_w / 2 - stack_t)"
XIL = "(-pod_w / 2 + stack_t)"
YW = "(pod_d / 2 - wall_depth)"      # the side walls' front end, the ceiling's front edge (Y -645)
YD = "dr_acc_face_y"                 # the column's and the soffit's door side: DR's access-panel face (FRONT)
YF = "(-pod_d / 2)"
ZS0 = "dt_zb"                        # soffit underside, flush with the top block's underside (D-61)
ZS1 = "(dt_zb + sof_h)"
ZC0 = "floor_top"                    # floor top Z 12 (skeleton v4: mat 3 + ply 9)
ZCB = "(%s + foot_t)" % ZC0          # top of the column's foot plate
XR = "(pod_w / 2 - stack_t - col_gap)"    # the column's and the soffit's right limit, 5 mm off the lining
XL = "(-pod_w / 2 + stack_t + col_gap)"   # the soffit's left limit
ZRB = "(pod_h - outer_t - rvn_head - (stud_l - stud_eng))"   # rails' underside: on the M6 x 16 studs' heads (HOLD-18)
ZBT = "(%s - hd_h - hd_c)" % ZRB                           # top of what sits under a stud head
YFACE = "(%s + col_d)" % YW          # the column's and the soffit's room face (Y -285), the ceiling cassette's front edge
YB_FRAME = "(%s + decor_d - dr_back_t)" % YF   # DR's frame face toward the pod (Y -646.5): the passage and the riser stop short of it


# AIR parameters another owner may take over: if the skeleton or the ceiling ever carries FRONT's
# named values, theirs win and AIR's copies drop out
AIR_MAY_DEFINE = {"dr_back_t", "dr_acc_t", "dr_acc_face_y",
                  # the roof sleeve flange's rivnut layout, which the ceiling's model carries too (C2's skin holes):
                  # once the ceiling's frames PR lands, its copies win and these drop out
                  "slv_rn_e", "slv_rn_in", "slv_bulge", "slv_rn_clr", "slv_rn_yb"}
FRONT_NAMED = ("dr_back_t", "dr_acc_t", "dr_acc_face_y", "op_x0", "op_w", "op_z0", "op_h")   # DR's opening is FRONT's too
FRONT_FILE = "v2/01-CAD-Native/front/dr_block.py"     # FRONT's DR model, which publishes them


def front_table(repo_root):
    """FRONT's DR model's parameter table, read without Fusion: {name: (expression, unit, status, source)}
    in the file's order (FRONT builds its parameters in that order), or None when the file isn't here.
    Its entries are (name, expression, unit, status, source) tuples of strings."""
    import ast
    path = os.path.join(repo_root, FRONT_FILE)
    if not os.path.isfile(path):
        return None
    found = []
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple) and len(node.elts) == 5 and all(
                isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts[:4]):
            name = node.elts[0].value
            if re.fullmatch(r"[a-z][a-z0-9_]*", name):
                src = node.elts[4].value if isinstance(node.elts[4], ast.Constant) else ""
                found.append(((node.lineno, node.col_offset), name, tuple(e.value for e in node.elts[:4]) + (src,)))
    out = {}
    for _at, name, entry in sorted(found):          # the file's order (ast.walk goes breadth first)
        out.setdefault(name, entry)
    return out


def front_named(repo_root):
    """FRONT's own (expression, unit) for each of FRONT_NAMED, or None when its DR model isn't here."""
    t = front_table(repo_root)
    return None if t is None else {n: t[n][1:3] for n in FRONT_NAMED if n in t}


def front_entries(repo_root=REPO_ROOT, have=()):
    """AIR's parameter entries for FRONT's named values, taken from FRONT's DR model, plus every input their
    expressions use that neither the skeleton, the ceiling nor AIR defines (in FRONT's order, so each comes
    after what it uses). Raises when FRONT's model or one of the names is missing: AIR keeps no copy."""
    t = front_table(repo_root)
    if t is None:
        raise RuntimeError("FRONT's DR model %s is not in this checkout; AIR reads DR's panel face from it" % FRONT_FILE)
    missing = [n for n in FRONT_NAMED if n not in t]
    if missing:
        raise RuntimeError("FRONT's DR model no longer publishes %s" % missing)
    own = {p[0] for p in AIR_PARAMS} | set(have)
    take, todo = set(), list(FRONT_NAMED)
    while todo:
        n = todo.pop()
        if n in take:
            continue
        take.add(n)
        for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t[n][1]):
            if ident in t and ident not in own and ident not in take:
                todo.append(ident)
    return [(n, t[n][1], t[n][2], t[n][3], "FRONT's DR model (%s), read at load: %s" % (FRONT_FILE.split("/")[-1], t[n][4]))
            for n in t if n in take]


def all_params():
    base = CM.all_params()
    have = {p[0] for p in base}
    mine = [p for p in AIR_PARAMS if p[0] != "@FRONT"]
    clash = [p[0] for p in mine if p[0] in have and p[0] not in AIR_MAY_DEFINE]
    if clash:
        raise ValueError("AIR parameter names clash with the skeleton or the ceiling: %s" % clash)
    front = [p for p in front_entries(have=have) if p[0] not in have]
    at = [p[0] for p in AIR_PARAMS].index("@FRONT")
    out = [p for p in AIR_PARAMS[:at] if p[0] not in have] + front + [p for p in AIR_PARAMS[at + 1:] if p[0] not in have]
    return base + out


def evaluate(params=None, overrides=None):
    return CM.evaluate(params or all_params(), overrides)


ev = CM.ev
overlap = CM.overlap


# the faces each fan box leaves open, where the air passes (axis, -1 for the low face, +1 for the
# high one): the exhaust box takes the cartridge's air through its left face and blows it up into the
# roof sleeve; the supply box takes the riser's air from below and blows it up into the upper
# transition. A closed box would block the air (and its STEP solid would hold a sealed void)
FAN_BOX_OPEN = {"EXHAUST FAN BOX": (("x", -1), ("z", 1)), "SUPPLY FAN BOX": (("z", -1), ("z", 1))}

# the edit test's changes (edit_test_air.py, guideline 4.4), one list for it and the offline check
# that every cut lands in its body for each: pod_d and wall_depth change together, since the side
# walls start at DR's back (the skeleton keeps the two, and decor_d, as separate values)
EDITS = [[("pod_w", "2600 mm")], [("pod_d", "1725 mm"), ("wall_depth", "1520 mm")], [("dt_zb", "2100 mm")],
         [("dr_acc_t", "4 mm")], [("col_x0", "940 mm")], [("hub_z", "1250 mm")]]


def box(x0, x1, y0, y1, z0, z1):
    return (x0, x1, y0, y1, z0, z1)


def hub_zone():
    """ELECTRICAL's hub 710041 sits here (agreed 2026-11-01; AIR's placeholder 618101 is gone): 180 x 180, 29 deep
    behind the column's front face, centred between the front angles' legs. AIR keeps only the cut through its front face
    and fill."""
    hx = "(col_x0 + face_t + ang_f + %s - ang_f) / 2" % XR
    return box("%s - hub_w / 2" % hx, "%s + hub_w / 2" % hx, "%s - hub_t" % YFACE, YFACE, "hub_z - hub_w / 2",
               "hub_z + hub_w / 2")


def harness_points():
    """ELECTRICAL's harness points (agreed 2026-11-01), as expressions: entry and ties in the FR angle (where the turned
    copy shows them), the soffit hole, the fan box hole, the plenum plate ties."""
    yleg = "%s - face_t - ang_w / 2" % YFACE                     # the FR angle's side leg's middle (Y -307)
    xch = "%s - ang_f - hn_ch_w / 2" % XR                          # the channel's middle (X 1140)
    return {"leg_y": yleg, "entry_z": "hub_z - hub_w / 2 + hn_entry_dz", "tie_z": ("hn_tie_z1", "hn_tie_z2"),
            "ch_x": xch, "sof_y": "%s - face_t - hn_sof_dy" % YFACE,
            "box_y": "%s + clr + cart_d - fbox_t - lin_t - hn_box_dy" % YD,
            "plate_y": tuple("%s + hn_ty0 + %d mm" % (YD, 100 * k) for k in range(3))}


def strap_x():
    """The two cartridge straps' middles in X: the exhaust cartridge's quarter points."""
    x0 = "(%s - fb_w - cart_l)" % XR
    return ("%s + cart_l / 4" % x0, "%s + 3 * cart_l / 4" % x0)


def soffit_supports():
    """The exhaust cartridge's two straps 611213 with their pads 618107 and support angles 611214, and the exhaust fan
    box's four isolating mounts 618403 on two angles 611409 (the Lead's rulings 2026-11-01): [(key, name, box)]."""
    out = []
    ez0 = "%s + face_t + sof_fill_t" % ZS0                    # the cartridge's and the fan box's bottom
    yd1, yff = "%s + dp_t" % YD, "%s - face_t" % YFACE        # the door-side plate's and the front face's insides
    cy0, cy1 = "%s + clr" % YD, "%s + clr + cart_d" % YD
    zs1 = "%s - st_pad_t" % ez0                                # the strap's top
    for k, xm in enumerate(strap_x(), 1):
        # the strap stops 1 short of each support angle's upright leg
        out.append(("strap", "CARTRIDGE STRAP %d" % k, box("%s - st_w / 2" % xm, "%s + st_w / 2" % xm,
                                                           "%s + st_t + 1 mm" % yd1, "%s - st_t - 1 mm" % yff,
                                                           "%s - st_h" % zs1, zs1)))
        out.append(("st_pad", "CARTRIDGE STRAP PAD %d" % k, box("%s - st_w / 2" % xm, "%s + st_w / 2" % xm,
                                                                "%s + (cart_d - st_pad_l) / 2" % cy0,
                                                                "%s + (cart_d + st_pad_l) / 2" % cy0, zs1, ez0)))
        zt = "%s - st_t" % zs1                                 # the support angles' flat legs carry the strap's ends
        out.append(("st_ang", "STRAP ANGLE %d DOOR" % k, box("%s - sa_l / 2" % xm, "%s + sa_l / 2" % xm, yd1,
                                                             "%s + sa_w" % yd1, "%s - st_t" % zt, "%s - st_t + sa_w" % zt)))
        out.append(("st_ang", "STRAP ANGLE %d ROOM" % k, box("%s - sa_l / 2" % xm, "%s + sa_l / 2" % xm,
                                                             "%s - sa_w" % yff, yff, "%s - st_t" % zt,
                                                             "%s - st_t + sa_w" % zt)))
    bx0, bx1 = "%s - fb_w" % XR, XR
    ma_x1 = "%s - ang_f - hn_ch_w - 4 mm" % XR                 # 4 short of ELECTRICAL's channel under the box
    zm = "%s - mt_h" % ez0                                     # the mounts' feet on the angles' flat legs
    for tag, y0, y1 in (("DOOR", yd1, "%s + ma_w" % yd1), ("ROOM", "%s - ma_w" % yff, yff)):
        out.append(("m_ang", "FAN BOX MOUNT ANGLE %s" % tag, box(bx0, ma_x1, y0, y1, "%s - ma_t" % zm,
                                                                 "%s - ma_t + ma_h" % zm)))
    for tag, ym in (("DOOR", "%s + mt_in" % cy0), ("ROOM", "%s - mt_in" % cy1)):
        for k, xm in ((1, "%s + mt_x1" % bx0), (2, "%s - mt_x2" % bx1)):
            out.append(("mount", "FAN BOX MOUNT %s %d" % (tag, k), box("%s - mt_d / 2" % xm, "%s + mt_d / 2" % xm,
                                                                       "%s - mt_d / 2" % ym, "%s + mt_d / 2" % ym,
                                                                       zm, ez0)))
    return out


def strap_section():
    """The strap 611213's L section [(x, z)] in its own frame (run along Y): the flat leg on top under the cartridge,
    the upright leg down at its +X edge."""
    return [("0 mm", "st_h"), ("st_w", "st_h"), ("st_w", "0 mm"), ("st_w - st_t", "0 mm"), ("st_w - st_t", "st_h - st_t"),
            ("0 mm", "st_h - st_t")]


def angle_section(w, h, t):
    """An angle's L section [(y, z)] in its own frame (run along X): its upright leg against the plate at y 0, its flat
    leg out to y w at the bottom. The room-side copy is the same part turned 180 deg about Z."""
    return [("0 mm", "0 mm"), (w, "0 mm"), (w, t), (t, t), (t, h), ("0 mm", h)]


def latch_bracket_section():
    """The latch bracket 611215's L section [(y, z)] in its own frame (run along X): the tab at the bottom from its free
    end (y 0) to the front face, the upright leg up the front face."""
    d = "lt_in + lt_bd / 2 + 4 mm"
    return [("0 mm", "0 mm"), (d, "0 mm"), (d, "lb_h"), ("%s - lb_t" % d, "lb_h"), ("%s - lb_t" % d, "lb_t"),
            ("0 mm", "lb_t")]


def leg_boxes(name, bx, ev):
    """The boxes a shaped soffit part is made of (each an L or the latch's snap groove), from its layout box bx (numbers)
    and its name; None for a plain box part. ev evaluates a parameter expression."""
    x0, x1, y0, y1, z0, z1 = bx
    if name.startswith("CARTRIDGE STRAP ") and "PAD" not in name:
        # the flat leg runs the full length onto both support angles; the upright leg stops 1 short of their flat legs
        t, ua, ub = ev("st_t"), ev("%s + dp_t + sa_w + 1 mm" % YD), ev("%s - face_t - sa_w - 1 mm" % YFACE)
        return [(x0, x1, y0, y1, z1 - t, z1), (x1 - t, x1, ua, ub, z0, z1 - t)]
    if name.startswith("STRAP ANGLE ") or name.startswith("FAN BOX MOUNT ANGLE "):
        t = ev("st_t") if name.startswith("STRAP") else ev("ma_t")
        if name.endswith("DOOR"):
            return [(x0, x1, y0, y0 + t, z0, z1), (x0, x1, y0 + t, y1, z0, z0 + t)]
        return [(x0, x1, y1 - t, y1, z0, z1), (x0, x1, y0, y1 - t, z0, z0 + t)]
    if " LATCH BRACKET " in name:
        t, cx, cy = ev("lb_t"), ev("lt_cx"), ev("lt_cy")
        xm, ym = (x0 + x1) / 2, ev("%s - face_t - lt_in" % YFACE)
        tab = [(x0, xm - cx / 2, y0, y1 - t, z0, z0 + t), (xm + cx / 2, x1, y0, y1 - t, z0, z0 + t),
               (xm - cx / 2, xm + cx / 2, y0, ym - cy / 2, z0, z0 + t), (xm - cx / 2, xm + cx / 2, ym + cy / 2, y1 - t, z0, z0 + t)]
        return [(x0, x1, y1 - t, y1, z0, z1)] + tab
    if " LATCH " in name:
        zt, t, cx, cy = z0 + ev("lb_z"), ev("lb_t"), ev("lt_cx"), ev("lt_cy")
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        return [(x0, x1, y0, y1, z0, zt), (xm - cx / 2, xm + cx / 2, ym - cy / 2, ym + cy / 2, zt, zt + t),
                (x0, x1, y0, y1, zt + t, z1)]
    return None


def soffit_sections():
    """The soffit underside: two hinged sections and a fixed strip over the column (D-87)."""
    return [("sof_under", "SOFFIT UNDERSIDE LEFT", XL, "-us_gap / 2"),
            ("sof_under_r", "SOFFIT UNDERSIDE RIGHT", "us_gap / 2", "col_x0 - us_gap / 2"),
            ("sof_under_f", "SOFFIT UNDERSIDE FIXED", "col_x0", XR)]


def stud_points():
    """(name, x, y) of the soffit's four hanger studs, at the ceiling's hanger rivnuts."""
    yd = "%s + tube_w / 2" % YW
    yr = "%s + cs_front - x1_ov + tube_w / 2" % YW
    return [("STUD %s %s" % (side, edge), "%shang_x" % ("-" if side == "L" else ""), y)
            for side in ("L", "R") for edge, y in (("DOOR", yd), ("ROOM", yr))]


FRONT_SCREWS = [("B08 1", "b08_x1", "b08_z"), ("B08 2", "b08_x2", "b08_z"), ("B08 3", "b08_x3", "b08_z"),
                ("B01 1", "b01_x1", "b01_z"), ("B01 2", "b01_x2", "b01_z"), ("B07 LOW", "b07_x", "b07_z")]


def front_screw_boxes():
    """[(name, washer box, head box)]: FRONT's panel screws that stand into AIR's space, from DR's panel face (FRONT's
    named value, YD) into the pod: a plain washer then a socket head, 7.6 proud in all (not AIR's parts: what AIR
    keeps clear of, or relieves)."""
    out = []
    for name, x, z in FRONT_SCREWS:
        w, h = "fr_wsh_d / 2", "fr_hd_d / 2"
        out.append((name, ("%s - %s" % (x, w), "%s + %s" % (x, w), YD, "%s + fr_wsh_t" % YD, "%s - %s" % (z, w), "%s + %s" % (z, w)),
                    ("%s - %s" % (x, h), "%s + %s" % (x, h), "%s + fr_wsh_t" % YD, "%s + fr_wsh_t + fr_hd_h" % YD,
                     "%s - %s" % (z, h), "%s + %s" % (z, h))))
    return out


def door_stud_pockets():
    """(stud name, pocket box) in the soffit's door-side plate round each door-side stud's head: the head plus hd_c
    all round, from the head room's floor to the rail. With DR's panel face at Y -641.14 the plate reaches 0.86 into
    the heads (FRONT's DR rebuild); the pockets clear them whichever face is built."""
    return [(name, ("%s - stud_d / 2 - hd_c" % x, "%s + stud_d / 2 + hd_c" % x, YD, "%s + dp_t" % YD, ZBT, ZRB))
            for name, x, _y in stud_points() if name.endswith("DOOR")]


def b08_fill_pockets():
    """(screw name, pocket box) in the fill under the exhaust cartridge round each of B08's heads (the fill starts
    clr off DR's panel face, the heads stand 7.6 proud): the head plus fr_scr_clr all round and behind."""
    return [(name, ("%s - fr_hd_d / 2 - fr_scr_clr" % x, "%s + fr_hd_d / 2 + fr_scr_clr" % x, "%s + clr" % YD,
                    "%s + fr_wsh_t + fr_hd_h + fr_scr_clr" % YD, "%s - fr_hd_d / 2 - fr_scr_clr" % z,
                    "%s + fr_hd_d / 2 + fr_scr_clr" % z))
            for name, x, z in FRONT_SCREWS if name.startswith("B08")]


def lock_points():
    """(name, x, y) of the soffit's two captive lock screws: in the room-side rail, into cross member 1's lock rivnuts
    (PM ruling 2026-11-01, option b for DR's new panel face: off the door-side rail, whose edge came too close), at the
    room-side studs' Y, over the left inlet plenum where the key reaches them through the left hinged underside."""
    yr = "%s + cs_front - x1_ov + tube_w / 2" % YW
    return [("LOCK SCREW %d" % (k + 1), x, yr) for k, x in enumerate(("-lock_x", "-lock_x + lock_dx"))]


def layout():
    """[(part key, body name, box expressions)] for every body, pod system."""
    b = []
    # column: foot plate on the floor's mat, faces above the kick grille up to the soffit
    b.append(("col_foot", "COLUMN FOOT PLATE", box("col_x0", XR, YD, YFACE, ZC0, ZCB)))
    zg1 = "%s + grille_z + grille_h" % ZCB
    b.append(("col_front", "COLUMN FACE FRONT", box("col_x0", XR, "%s - face_t" % YFACE, YFACE, zg1, ZS0)))
    b.append(("col_left", "COLUMN FACE LEFT", box("col_x0", "col_x0 + face_t", YD, "%s - face_t" % YFACE, zg1, ZS0)))
    zg0 = "%s + grille_z" % ZCB
    b.append(("kick", "KICK GRILLE FRONT", box("col_x0", XR, "%s - grille_t" % YFACE, YFACE, zg0, zg1)))
    b.append(("kick_l", "KICK GRILLE LEFT", box("col_x0", "col_x0 + grille_t", "%s - grille_t - grille_l" % YFACE,
                                                  "%s - grille_t" % YFACE, zg0, zg1)))
    # corner angles, full height inside the faces (the back-right corner: the plenum plates)
    for name, x0, xw, y0 in (("FL", "col_x0 + face_t", "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("FR", "%s - ang_f" % XR, "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("BL", "col_x0 + face_t", "ang_w", YD)):
        b.append(("col_ang_b" if name == "BL" else "col_ang", "COLUMN ANGLE %s" % name,
                  box(x0, "%s + %s" % (x0, xw), y0, "%s + ang_w" % y0, ZCB, ZS0)))
    # supply cartridge: its right side on the column's limit, 5 off the floating lining; the plenum
    # plates sit only above and below it (air report #110: 27 of fill at the left face, D-61)
    cx1 = XR
    cx0 = "%s - cart_w" % cx1
    cy0, cy1 = "%s + clr" % YD, "%s + clr + cart_d" % YD
    cz0 = "b01_z + fr_wsh_d / 2 + cart_b01_clr"      # 4 over B01's washers (the Lead's ruling): Z 140
    cz1 = "%s + cart_l" % cz0
    b.append(("cart", "CARTRIDGE SUPPLY", box(cx0, cx1, cy0, cy1, cz0, cz1)))
    # the column's right side at the two plenums (the cartridge closes the rest)
    py1 = "%s - face_t - ang_w" % YFACE
    b.append(("col_side_lo", "COLUMN PLENUM PLATE LOW", box("%s - plate_t" % XR, XR, YD, py1, ZCB, cz0)))
    b.append(("col_side_hi", "COLUMN PLENUM PLATE HIGH", box("%s - plate_t" % XR, XR, YD, py1, cz1, ZS0)))
    b.append(("col_fill", "COLUMN FILL FRONT", box("col_x0 + face_t + ang_f", "%s - ang_f" % XR, cy1,
                                                     "%s - face_t" % YFACE, cz0, cz1)))
    b.append(("col_fill_l", "COLUMN FILL LEFT", box("col_x0 + face_t", cx0, "%s + ang_w" % YD, cy1, cz0, cz1)))
    # the hub zone is ELECTRICAL's hub 710041 now (agreed 2026-11-01): no body here, only its cut (hub_zone())
    # soffit: underside sections (dark tone), front face, top rails, left end plate
    zf1 = ZRB                                      # front face up to the rail (riveted); pockets round the studs
    for key, name, x0, x1 in soffit_sections():
        b.append((key, name, box(x0, x1, "%s + us_jg" % YD, "%s - face_t" % YFACE, ZS0, "%s + face_t" % ZS0)))
    b.append(("sof_front", "SOFFIT FACE FRONT", box(XL, XR, "%s - face_t" % YFACE, YFACE, ZS0, zf1)))
    zr0, zr1 = ZRB, "%s + rail_t" % ZRB
    b.append(("sof_rail_d", "SOFFIT RAIL DOOR", box(XL, XR, YD, "%s + rail_w" % YW, zr0, zr1)))
    b.append(("sof_rail_r", "SOFFIT RAIL ROOM", box(XL, XR, "%s - rail_w" % YFACE, YFACE, zr0, zr1)))
    b.append(("sof_door", "SOFFIT DOOR PLATE", box(XL, XR, YD, "%s + dp_t" % YD, "%s + face_t + hl_h" % ZS0, zr0)))
    b.append(("sof_end", "SOFFIT END PLATE LEFT", box(XL, "%s + box_t" % XL, "%s + dp_t" % YD, "%s - face_t" % YFACE,
                                                      "%s + face_t" % ZS0, ZBT)))
    ex1 = "%s - fb_w" % XR
    ez0 = "%s + face_t + sof_fill_t" % ZS0
    b.append(("cart", "CARTRIDGE EXHAUST", box("%s - cart_l" % ex1, ex1, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b.append(("box", "EXHAUST FAN BOX", box(ex1, XR, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b += soffit_supports()
    # the fill under the cartridge: three pieces bonded to the sections (the Lead's ruling 2026-11-01: the cartridge
    # and the fan box carry themselves), from behind the hinges to short of the latches and the straps' room ends
    fy0, fy1 = "%s + dp_t + sa_w" % YD, "%s - face_t - sf_y1_gap" % YFACE   # behind the hinges and the strap angles
    for key, name, x0, x1 in (("sof_fill", "SOFFIT FILL UNDER LEFT", "%s - cart_l" % ex1, "-us_gap / 2"),
                              ("sof_fill_r", "SOFFIT FILL UNDER RIGHT", "us_gap / 2", "col_x0 - us_gap / 2"),
                              ("sof_fill_c", "SOFFIT FILL UNDER OVER THE COLUMN", "col_x0", XR)):
        b.append((key, name, box(x0, x1, fy0, fy1, "%s + face_t" % ZS0, ez0)))
    # the front fill starts above the latches, their brackets and the room-side angles (sf_ff_dz over the cartridge's
    # bottom), so nothing there cuts it, whatever the pod's size
    b.append(("sof_fill_f", "SOFFIT FILL FRONT", box("%s - cart_l" % ex1, XR, cy1, "%s - face_t" % YFACE,
                                                      "%s + sf_ff_dz" % ez0, ZBT)))
    b.append(("egrille", "EXHAUST GRILLE", box("%s + eg_x0" % XIL, "%s + eg_x0 + eg_l" % XIL, "%s + face_t" % YW,
                                                "%s + face_t + eg_w" % YW, ZS0, "%s + grille_t" % ZS0)))
    # hanging: 4 studs (head under the rail, shank up through the fork to the ceiling frame),
    # 2 captive lock screws in the door-side rail (838002, retainer HOLD), hinges and latches
    zf = "(pod_h - outer_t - rvn_head)"
    for name, x, y in stud_points():
        b.append(("stud", name + " HEAD", box("%s - stud_d / 2" % x, "%s + stud_d / 2" % x, "%s - stud_d / 2" % y,
                                              "%s + stud_d / 2" % y, "%s - hd_h" % zr0, zr0)))
        b.append(("stud", name + " SHANK", box("%s - 3 mm" % x, "%s + 3 mm" % x, "%s - 3 mm" % y, "%s + 3 mm" % y, zr0, zf)))
    for name, x, y in lock_points():
        b.append(("lock", name + " HEAD", box("%s - stud_d / 2" % x, "%s + stud_d / 2" % x,
                                              "%s - stud_d / 2" % y, "%s + stud_d / 2" % y, "%s - hd_h" % zr0, zr0)))
        b.append(("lock", name + " SHANK", box("%s - 3 mm" % x, "%s + 3 mm" % x, "%s - 3 mm" % y, "%s + 3 mm" % y, zr0, zf)))
    za = "%s + face_t" % ZS0                                  # the sections' ACP top
    yff = "%s - face_t" % YFACE                               # the front face's inside
    for key, name, x0, x1 in soffit_sections()[:2]:
        for q in (1, 3):
            xc = "(%s) + ((%s) - (%s)) * %d / 4" % (x0, x1, x0, q)
            # the hinge 611212's reserved space (the AIR Transitions Engineer designs the riveted pin hinge inside it)
            b.append(("hinge", "%s HINGE %d" % (name, q), box("%s - hinge_l / 2" % xc, "%s + hinge_l / 2" % xc,
                                                             "%s + us_jg" % YD, "%s + us_jg + hg_res_y" % YD, za,
                                                             "%s + hg_res_h" % za)))
            # the Southco E4 push latch, its axis lt_in from the room edge, held by its bracket's tab
            yl = "%s - lt_in" % yff
            zl = "%s + lt_z0" % za
            b.append(("latch", "%s LATCH %d" % (name, q), box("%s - lt_bw / 2" % xc, "%s + lt_bw / 2" % xc,
                                                             "%s - lt_bd / 2" % yl, "%s + lt_bd / 2" % yl, zl,
                                                             "%s + lt_bl" % zl)))
            zt = "%s + lb_z" % zl
            b.append(("lt_br", "%s LATCH BRACKET %d" % (name, q), box("%s - lb_w / 2" % xc, "%s + lb_w / 2" % xc,
                                                                     "%s - lt_in - lt_bd / 2 - 4 mm" % yff, yff, zt,
                                                                     "%s + lb_h" % zt)))
    # supply fan box joined with the intake riser (D-87), the transitions, the roof sleeve and grille
    sy0 = "%s + sb_yf" % YF
    b.append(("box_s", "SUPPLY FAN BOX", box("sb_x0", "sb_x0 + sb_w", sy0, "%s + sb_d" % sy0, "sb_z0", "sb_z0 + sb_h")))
    b += fan_box_inner()
    # the upper transition: over the box and in the passage beside it, full depth (its shape: transition_outlines())
    b.append(("trans", "SUPPLY TRANSITION", box("sb_x0", "op_x0 + op_w", sy0, YB_FRAME, "op_z0", "op_z0 + op_h")))
    b.append(("riser", "INTAKE RISER", box("rs_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z0", "rs_z1")))
    # the lower transition: FRONT's trapezoid from the riser's top to the box's bottom (riser_transition_outline()), across
    # the box's and the riser's depths
    b.append(("rtrans", "RISER TRANSITION", box("sb_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z1", "sb_z0")))
    # how the assembly rests in DR: the lip angle on two pads on F08, the riser's buffer against F07 (PM rulings 2026-11-01)
    b.append(("lip", "FAN BOX LIP ANGLE SUPPLY", box("sb_x0", LIP_X1, LIP_Y0, sy0, "sb_z0 + pad_t", "sb_z0 + pad_t + lip_h")))
    for side, x0 in (("LEFT", "sb_x0 + pad_in"), ("RIGHT", "%s - pad_in - pad_l" % LIP_X1)):
        b.append(("pad", "FAN BOX PAD %s" % side, box(x0, "%s + pad_l" % x0, "%s - pad_w / 2" % F08_YC,
                                                      "%s + pad_w / 2" % F08_YC, "sb_z0", "sb_z0 + pad_t")))
    b.append(("buffer", "RISER BUFFER", box("%s - buf_d / 2" % BUF_X, "%s + buf_d / 2" % BUF_X,
                                            "%s + dr_skin_t + bond_t + dr_fr_w + buf_gap" % YF, "rs_y0 - rvn_head",
                                            "dr_f07_zc - buf_d / 2", "dr_f07_zc + buf_d / 2")))
    # the roof sleeve with its top flange on C2's skin, and the grille on the flange (J-AIR-03)
    fx0, fx1, fy0, fy1 = sleeve_flange()
    b.append(("sleeve", "ROOF SLEEVE", box(fx0, fx1, fy0, fy1, "%s + cart_w" % ez0, "pod_h + slv_t")))
    b.append(("rgrille", "ROOF GRILLE", box(fx0, fx1, fy0, fy1, "pod_h + slv_t", "pod_h + slv_t + rg_t")))
    return b


# the lip's ends and tip, the pads' line on F08 and the buffer's place over F07 (PM rulings 2026-11-01)
LIP_X1 = "(dr_f08_x1 - lip_end)"
LIP_Y0 = "(%s + dr_skin_t + lip_tip)" % YF
F08_YC = "(%s + dr_skin_t + bond_t + dr_fr_w / 2)" % YF     # D-137: DR's front ring stands the skeleton's bond_t off the skin
BUF_X = "((rs_x0 + dr_f08_x1) / 2)"


def layout_box(name):
    """The layout box (expressions) of one named body."""
    return next(bx for _k, n, bx in layout() if n == name)


def lip_section():
    """The lip angle's section in (Y, Z): the foot leg from its tip under the box's front line, the upright leg up the
    box's front wall, outside it. Extruded along X from the box's left end to LIP_X1."""
    y0, y1 = LIP_Y0, "(%s + sb_yf)" % YF
    z0 = "(sb_z0 + pad_t)"
    return [(y0, z0), (y1, z0), (y1, "%s + lip_h" % z0), ("%s - lip_t" % y1, "%s + lip_h" % z0),
            ("%s - lip_t" % y1, "%s + lip_t" % z0), (y0, "%s + lip_t" % z0)]


def transition_outlines():
    """The upper transition's two plan outlines [(x, y)], each (outline, z0, z1): over the box and the passage from the
    box's top to the opening's top, and the passage beside the box down to the opening's foot; both run from the box's
    front line to DR's frame face, their facet side ut_clr off C04 (PM rulings 2026-11-01, report #283)."""
    y0, xr = "(%s + sb_yf)" % YF, "(op_x0 + op_w)"       # the opening's right edge (FRONT's, X 1146; Reviewer 7)
    top = [("sb_x0", y0), ("ut_xf", y0), (xr, "ut_yr"), (xr, YB_FRAME), ("sb_x0", YB_FRAME)]
    side = [("sb_x0 + sb_w", y0), ("ut_xf", y0), (xr, "ut_yr"), (xr, YB_FRAME), ("sb_x0 + sb_w", YB_FRAME)]
    return [(top, "sb_z0 + sb_h", "op_z0 + op_h"), (side, "op_z0", "sb_z0 + sb_h")]


def riser_chamfer():
    """The riser's front-right vertical edge cut off 8 x 8 (rs_ch; the Lead's ruling 2026-11-01): the triangle [(x, y)]
    removed from its plan, run over its height."""
    xr, yf = "rs_x0 + rs_w", "rs_y0"
    return [("%s - rs_ch" % xr, yf), (xr, yf), (xr, "%s + rs_ch" % yf)]


def riser_transition_outline():
    """The lower transition's side outline [(x, z)]: FRONT's trapezoid from the riser's top to the box's bottom, run in
    Y over the riser's depth, as FRONT reserves it (Y -803 on; Reviewer 7: from the box's front line, -819, it cut DR's
    corner skin)."""
    return [("rs_x0", "rs_z1"), ("rs_x0 + rs_w", "rs_z1"), ("sb_x0 + sb_w", "sb_z0"), ("sb_x0", "sb_z0")]


def sleeve_flange():
    """(x0, x1, y0, y1) of the roof sleeve's top flange, which the grille covers exactly (CEILING's layout 2026-11-01)."""
    return ("slot_x0 - slv_fl_l", "slot_x0 + slot_w + slv_fl_f", "slot_y0 - slv_fl_f", "slot_y0 + slot_d + slv_fl_b")


def sleeve_opening():
    """(x0, x1, y0, y1) of the opening through the sleeve's top flange: the walls' inside (slv_t in from the slot's
    outline), so the flange sits on the walls' top edges and the sleeve is one solid. Cut at the slot's outline, the
    opening took the flange off the wall tops and left it touching them on an edge only: two solids in the STEP (the
    mechanical checks' C06 on the follow-up's first saved build, 2026-11-01)."""
    return ("slot_x0 + slv_t", "slot_x0 + slot_w - slv_t", "slot_y0 + slv_t", "slot_y0 + slot_d - slv_t")


def sleeve_rivnuts():
    """[(name, x, y)] of the grille's 4 rivnuts in the sleeve's flange: 2 on the left side, 2 on the back side behind
    cross member 1 (J-AIR-03)."""
    return [("SLEEVE RIVNUT LEFT FRONT", "slot_x0 - slv_rn_e", "slot_y0 + slv_rn_in"),
            ("SLEEVE RIVNUT LEFT BACK", "slot_x0 - slv_rn_e", "slot_y0 + slot_d - slv_rn_in"),
            ("SLEEVE RIVNUT BACK LEFT", "slot_x0 + slv_rn_in", "slv_rn_yb"),
            ("SLEEVE RIVNUT BACK RIGHT", "slot_x0 + slot_w - slv_rn_in", "slv_rn_yb")]


def features():
    """Cut features inside bodies (no change to their boxes): the column's keyholes in the
    back-left angle, BASE's spigot hole and slot in the foot plate, the rails' forks and the
    lock screws' holes, ELECTRICAL's harness holes, the transitions' rivet holes. [(body name, kind, args)]:
    kind 'zcircle' (x, y, z0, z1, d), 'ycircle' (x, z, y0, y1, d), 'xcircle' (y, z, x0, x1, d) or 'box' (x0, x1, y0,
    y1, z0, z1)."""
    out = []
    # keyholes: the column drops key_drop onto each stud, so the big hole is key_drop below it
    for k, zs in (("1", "hook_z1"), ("2", "hook_z2")):
        out.append(("COLUMN ANGLE BL", "ycircle", ("hook_x", "%s - key_drop" % zs, YD, "%s + ang_t" % YD, "key_d")))
        out.append(("COLUMN ANGLE BL", "box", ("hook_x - key_w / 2", "hook_x + key_w / 2", YD, "%s + ang_t" % YD,
                                               "%s - key_drop" % zs, zs)))
        out.append(("COLUMN ANGLE BL", "ycircle", ("hook_x", zs, YD, "%s + ang_t" % YD, "key_w")))
    # foot plate: S1 round, S2 slot along Y
    out.append(("COLUMN FOOT PLATE", "zcircle", ("spg1_x", "spg1_y", ZC0, ZCB, "spg_hole")))
    run = "(spg_slot - spg_hole) / 2"
    out.append(("COLUMN FOOT PLATE", "box", ("spg2_x - spg_hole / 2", "spg2_x + spg_hole / 2", "spg2_y - %s" % run,
                                             "spg2_y + %s" % run, ZC0, ZCB)))
    for sign in ("-", "+"):
        out.append(("COLUMN FOOT PLATE", "zcircle", ("spg2_x", "spg2_y %s %s" % (sign, run), ZC0, ZCB, "spg_hole")))
    # rails: an open fork from the rail's door-side edge to each stud's place
    zr0, zr1 = ZRB, "%s + rail_t" % ZRB
    for name, x, y in stud_points():
        rail = "SOFFIT RAIL DOOR" if name.endswith("DOOR") else "SOFFIT RAIL ROOM"
        edge = YD if rail.endswith("DOOR") else "%s - rail_w" % YFACE
        out.append((rail, "box", ("%s - key_w / 2" % x, "%s + key_w / 2" % x, edge, y, zr0, zr1)))
        out.append((rail, "zcircle", (x, y, zr0, zr1, "key_w")))
    for _n, x, y in lock_points():
        out.append(("SOFFIT RAIL ROOM", "zcircle", (x, y, zr0, zr1, "lock_hole")))
    # B08's three panel screws through the soffit's door-side plate: the washer plus fr_scr_clr round (the Lead's
    # ruling 2026-11-01: reliefs in the door plate, pockets in the fill, nothing showing from below)
    for name, x, z in FRONT_SCREWS:
        if name.startswith("B08"):
            out.append(("SOFFIT DOOR PLATE", "ycircle", (x, z, YD, "%s + dp_t" % YD, "fr_wsh_d + 2 * fr_scr_clr")))
    # D-121: a fan bore in each bulkhead over each fan (the exhaust fans hang under theirs, the supply fans stand on theirs)
    for name, x, y, z in fan_points():
        tag = "EXHAUST" if name.startswith("EXHAUST") else "SUPPLY"
        z0, z1 = ("%s + fan_t" % z, "%s + fan_t + blk_t" % z) if tag == "EXHAUST" else ("%s - blk_t" % z, z)
        out.append(("FAN BOX BULKHEAD %s" % tag, "zcircle", (x, y, z0, z1, "fan_bore")))
        for sx in ("-", "+"):           # the fan's 4 screws (fasteners: the 2-diameter rule holds for them)
            for sy in ("-", "+"):
                out.append(("FAN BOX BULKHEAD %s" % tag, "zcircle", ("%s %s fan_hp / 2" % (x, sx), "%s %s fan_hp / 2" % (y, sy),
                                                                    z0, z1, "fan_hole")))
    # the riser buffer's rivnut hole in the riser's front wall, over F07 (PM ruling 2026-11-01)
    out.append(("INTAKE RISER", "ycircle", (BUF_X, "dr_f07_zc", "rs_y0", "rs_y0 + rs_t", "hole_rvn")))
    # ELECTRICAL's harness (agreed 2026-11-01). The FR angle is the FL angle turned 180 deg about Y (D-120, TURNED), so
    # its holes are cut in FL's side leg where the turn takes them to FR's points (Z mirrored about the angle's middle):
    # FL shows them hidden behind the column's left face and the left kick grille
    hp, fl = harness_points(), layout_box("COLUMN ANGLE FL")
    ent = [hp["entry_z"], "%s + hn_entry_p" % hp["entry_z"]]
    for z, d in [(e, "hn_entry_d") for e in ent] + [(p, "hn_tie_d") for t in hp["tie_z"] for p in (t, "%s + hn_tie_p" % t)]:
        out.append(("COLUMN ANGLE FL", "xcircle", (hp["leg_y"], "(%s) + (%s) - (%s)" % (fl[4], fl[5], z), fl[0],
                                                   "%s + ang_t" % fl[0], d)))
    pz = "%s + hn_tz" % layout_box("COLUMN PLENUM PLATE HIGH")[4]
    for y in hp["plate_y"]:
        for z in (pz, "%s + hn_tie_p" % pz):
            out.append(("COLUMN PLENUM PLATE HIGH", "xcircle", (y, z, "%s - plate_t" % XR, XR, "hn_tie_d")))
    # the fixed underside: the cordgrip's Ø12 through the ACP, and the felt under it cut back to Ø30
    out.append(("SOFFIT UNDERSIDE FIXED", "zcircle", (hp["ch_x"], hp["sof_y"], ZS0, "%s + face_t" % ZS0, "hn_sof_d")))
    out.append(("SOFFIT UNDERSIDE FIXED", "zcircle", (hp["ch_x"], hp["sof_y"], ZS0, "%s + face_felt" % ZS0, "hn_sof_felt")))
    ez = "%s + face_t + sof_fill_t" % ZS0
    out.append(("EXHAUST FAN BOX", "zcircle", (hp["ch_x"], hp["box_y"], ez, "%s + fbox_t" % ez, "hn_box_d")))
    lee = layout_box("FAN BOX LINING EXHAUST FAR END")
    out.append(("FAN BOX LINING EXHAUST FAR END", "zcircle", (hp["ch_x"], hp["box_y"], lee[4], lee[5], "hn_lin_d")))
    # the grille's rivnuts in the sleeve's flange, and the grille's bolt holes over them (J-AIR-03, R-J6's 7.0)
    for _n, x, y in sleeve_rivnuts():
        out.append(("ROOF SLEEVE", "zcircle", (x, y, "pod_h", "pod_h + slv_t", "hole_rvn")))
        out.append(("ROOF GRILLE", "zcircle", (x, y, "pod_h + slv_t", "pod_h + slv_t + rg_t", "lock_hole")))
    # the transitions' 24 rivet holes in the riser and the supply box casing (the Lead's ruling: made, not drilled)
    out += transition_rivets()
    return out


def cutouts():
    """(body name to cut, cutter box): the hub zone through the front face and the fill
    behind it, the exhaust grille's opening in the soffit underside, the room-side stud heads'
    pockets in the soffit's front face, the door-side stud heads' pockets in the door-side plate,
    and B08's head pockets in the fill under the exhaust cartridge."""
    lay = {name: bx for _k, name, bx in layout()}
    hub = hub_zone()
    eg = lay["EXHAUST GRILLE"]
    hub_cut = (hub[0], hub[1], "%s - face_t - 40 mm" % YFACE, hub[3], hub[4], hub[5])
    eg_cut = (eg[0], eg[1], eg[2], eg[3], ZS0, "%s + face_t" % ZS0)    # the grille's opening through the face
    # in the fill the hub's cut runs on to the FR angle, so no 1 mm of fill stays between the entries and the hub
    # (ELECTRICAL 2026-11-01 15:47)
    hub_fill = (hub[0], "%s - ang_f" % XR) + hub_cut[2:]
    out = [("COLUMN FACE FRONT", hub_cut), ("COLUMN FILL FRONT", hub_fill), ("SOFFIT UNDERSIDE LEFT", eg_cut)]
    for name, x, y in [p for p in stud_points() if p[0].endswith("ROOM")] + lock_points():
        # a head pocket: the head plus 1.5 all round (the room-side studs' and the lock screws')
        out.append(("SOFFIT FACE FRONT", ("%s - stud_d / 2 - hd_c" % x, "%s + stud_d / 2 + hd_c" % x,
                                          "%s - face_t" % YFACE, YFACE, ZBT, ZRB)))
    out += [("SOFFIT DOOR PLATE", bx) for _n, bx in door_stud_pockets()]
    # the bonded fill: notched round each strap and over each mount angle's flat leg (it swings down past them)
    for _k, name, bx in soffit_supports():
        if name.startswith("CARTRIDGE STRAP ") and "PAD" not in name:
            piece = "SOFFIT FILL UNDER LEFT" if name.endswith("1") else "SOFFIT FILL UNDER RIGHT"
            out.append((piece, ("%s - 1 mm" % bx[0], "%s + 1 mm" % bx[1], bx[2], bx[3], "%s - 1 mm" % bx[4],
                                "%s + face_t + sof_fill_t" % ZS0)))           # up to the fill's top: the pad sits there too
        if name.startswith("FAN BOX MOUNT ANGLE "):
            for piece in ("SOFFIT FILL UNDER RIGHT", "SOFFIT FILL UNDER OVER THE COLUMN"):
                out.append((piece, (bx[0], bx[1], bx[2], bx[3], bx[4], "%s + face_t + sof_fill_t" % ZS0)))

    # ELECTRICAL's harness (agreed 2026-11-01): a 24 x 24 channel in the column's front fill from the hub up to the
    # fill's top, beside the FR angle; and one in the soffit's fill from the fixed underside's hole to the fan box's
    hp, col = harness_points(), lay["COLUMN FILL FRONT"]
    x0, x1 = "%s - ang_f - hn_ch_w" % XR, "%s - ang_f" % XR
    out.append(("COLUMN FILL FRONT", (x0, x1, "%s - face_t - hn_ch_w" % YFACE, "%s - face_t" % YFACE,
                                      "hub_z + hub_w / 2", col[5])))
    sf = lay["SOFFIT FILL UNDER OVER THE COLUMN"]
    out.append(("SOFFIT FILL UNDER OVER THE COLUMN", (x0, x1, "%s - hn_ch_w / 2" % hp["box_y"],
                                                      "%s + hn_ch_w / 2" % hp["sof_y"], sf[4], sf[5])))
    return out


# D-120: parts placed as copies of one component, and the parts whose layout boxes are one body together (a stud's or a
# screw's head and shank, joined): {key: how the layout's names group into one copy}
JOINED = {"stud": (" HEAD", " SHANK"), "lock": (" HEAD", " SHANK")}
COPIES = {"stud", "lock", "hinge", "latch", "lin_es", "lin_s", "layer", "pad", "lt_br", "strap", "st_pad", "st_ang",
          "mount", "m_ang"}
TURNED = {"col_ang": "y"}       # the right front angle is the left one turned about Y (the angle runs the full height)
BODY_KEY = {"cart": "casing"}   # a layout box whose body belongs to another part: the cartridge's is its casing's


def angle_pts(tag, x0, x1, y0, y1):
    """A column corner angle's L outline in plan: the front ones (FL, FR) with their short leg along X at the face's
    back (Y y1) and the long leg along Y at the column's outer side; BL with its legs on the door side and the left."""
    if tag == "FL":
        return [(x0, y1), (x1, y1), (x1, "%s - ang_t" % y1), ("%s + ang_t" % x0, "%s - ang_t" % y1),
                ("%s + ang_t" % x0, y0), (x0, y0)]
    if tag == "FR":
        return [(x0, y1), (x1, y1), (x1, y0), ("%s - ang_t" % x1, y0), ("%s - ang_t" % x1, "%s - ang_t" % y1),
                (x0, "%s - ang_t" % y1)]
    return [(x0, y0), (x1, y0), (x1, "%s + ang_t" % y0), ("%s + ang_t" % x0, "%s + ang_t" % y0),
            ("%s + ang_t" % x0, y1), (x0, y1)]


def units():
    """[(key, unit name, box expressions)]: each copy of each part as one box, for the position checks; a joined
    part's head and shank make one unit (the head is wider than the shank, so the unit is the head's plan and runs
    from the head's underside to the shank's top)."""
    out, held = [], {}
    for key, name, bx in layout():
        if key in JOINED:
            head, shank = JOINED[key]
            unit = name[:-len(head)] if name.endswith(head) else name[:-len(shank)]
            held.setdefault((key, unit), {})["head" if name.endswith(head) else "shank"] = bx
            continue
        out.append((key, name, bx))
    for (key, unit), parts in held.items():
        h, sh = parts["head"], parts["shank"]
        out.append((key, unit, (h[0], h[1], h[2], h[3], h[4], sh[5])))
    return out


def fan_box_inner():
    """D-121 (the Air Engineer's layout, PM ruling): each fan box's 2 mm bulkhead and its 50 mm linings, inside the
    3 mm casing. Exhaust: the bulkhead closes the box's open top and the fans hang under it, blowing straight into
    the roof sleeve; the two long walls (Y) are lined full height under the fans, in line with the cartridge's outer
    layers, so the passages stay open and the fans keep about 35 mm clear; the far end (X) is lined up to e_lin_gap
    under the fans. Supply: the fans stand on the bulkhead, and only the two end walls (X) are lined, from s_lin_gap
    above the fans to the box's open top. [(key, name, box)]"""
    ex0, ex1 = "%s - fb_w" % XR, "%s - fbox_t" % XR
    ey0, ey1 = "%s + clr + fbox_t" % YD, "%s + clr + cart_d - fbox_t" % YD
    ez0 = "%s + face_t + sof_fill_t + fbox_t" % ZS0
    etop = "%s + face_t + sof_fill_t + cart_w" % ZS0
    efan = "%s - blk_t - fan_t" % etop
    sx0, sx1 = "sb_x0 + fbox_t", "sb_x0 + sb_w - fbox_t"
    sy0, sy1 = "%s + sb_yf + fbox_t" % YF, "%s + sb_yf + sb_d - fbox_t" % YF
    sfan = "sb_z0 + lin_t"
    stop = "sb_z0 + sb_h"
    return [
        ("blk_e", "FAN BOX BULKHEAD EXHAUST", box(ex0, ex1, ey0, ey1, "%s - blk_t" % etop, etop)),
        ("lin_es", "FAN BOX LINING EXHAUST SIDE 1", box(ex0, ex1, ey0, "%s + lin_t" % ey0, ez0, efan)),
        ("lin_es", "FAN BOX LINING EXHAUST SIDE 2", box(ex0, ex1, "%s - lin_t" % ey1, ey1, ez0, efan)),
        ("lin_ee", "FAN BOX LINING EXHAUST FAR END", box("%s - lin_t" % ex1, ex1, "%s + lin_t" % ey0, "%s - lin_t" % ey1,
                                                        ez0, "%s - e_lin_gap" % efan)),
        ("blk_s", "FAN BOX BULKHEAD SUPPLY", box(sx0, sx1, sy0, sy1, "%s - blk_t" % sfan, sfan)),
        ("lin_s", "FAN BOX LINING SUPPLY END 1", box(sx0, "%s + lin_t" % sx0, sy0, sy1, "%s + fan_t + s_lin_gap" % sfan, stop)),
        ("lin_s", "FAN BOX LINING SUPPLY END 2", box("%s - lin_t" % sx1, sx1, sy0, sy1, "%s + fan_t + s_lin_gap" % sfan, stop)),
    ]


def transition_rivets():
    """The transitions' 24 rivet holes (the AIR Transitions Engineer's list, 2026-11-01), each through its wall from
    face to face: 10 in the riser's top for the lower transition's collar, 6 in the supply box casing's end walls for its
    webs, 4 in the front wall and 4 in the back wall for the upper transition. [(body name, kind, args)]: xcircle (y, z,
    x0, x1, d), ycircle (x, z, y0, y1, d)."""
    out = []
    zr = "rs_z1 - tr_col_in / 2"
    for k in (-1, 0, 1):
        y = "rs_y0 + rs_d / 2 + (%d) * tr_rs_py" % k
        out.append(("INTAKE RISER", "xcircle", (y, zr, "rs_x0", "rs_x0 + rs_t", "tr_rv_d")))
        out.append(("INTAKE RISER", "xcircle", (y, zr, "rs_x0 + rs_w - rs_t", "rs_x0 + rs_w", "tr_rv_d")))
    for xo in ("tr_rs_x1", "tr_rs_x2"):
        out.append(("INTAKE RISER", "ycircle", ("rs_x0 + %s" % xo, zr, "rs_y0", "rs_y0 + rs_t", "tr_rv_d")))
        out.append(("INTAKE RISER", "ycircle", ("rs_x0 + %s" % xo, zr, "rs_y0 + rs_d - rs_t", "rs_y0 + rs_d", "tr_rv_d")))
    sy0, sy1, top = "%s + sb_yf" % YF, "%s + sb_yf + sb_d" % YF, "sb_z0 + sb_h"
    for k in (-1, 0, 1):
        y = "%s + sb_d / 2 + (%d) * tr_be_py" % (sy0, k)
        out.append(("SUPPLY FAN BOX", "xcircle", (y, "sb_z0 + tr_be_dz", "sb_x0", "sb_x0 + fbox_t", "tr_rv_d")))
        out.append(("SUPPLY FAN BOX", "xcircle", (y, "sb_z0 + tr_be_dz", "sb_x0 + sb_w - fbox_t", "sb_x0 + sb_w", "tr_rv_d")))
    for m in ("-1.5", "-0.5", "0.5", "1.5"):
        out.append(("SUPPLY FAN BOX", "ycircle", ("sb_x0 + sb_w / 2 + (%s) * tr_bf_px" % m, "%s - tr_bf_dz" % top, sy0,
                                                  "%s + fbox_t" % sy0, "tr_rv_d")))
    for k in range(4):
        out.append(("SUPPLY FAN BOX", "ycircle", ("sb_x0 + tr_bb_x0 + %d * tr_bb_px" % k, "%s - tr_bb_dz" % top,
                                                  "%s - fbox_t" % sy1, sy1, "tr_rv_d")))
    return out


def fan_points():
    """Fan centres (x, y, z of the fan's underside): two in each fan box, lying flat. The supply fans stand on their
    bulkhead 50 above the box's floor; the exhaust fans hang under a sealed bulkhead at the box's top and blow
    straight into the roof sleeve (D-121: low fans let the cartridge's upper passages short-circuit)."""
    pts = []
    # each pair at the quarter points of its bulkhead's own span (inside the casing's walls), so the two bores keep equal
    # rims to the bulkhead's edges (the Lead's web rule for openings, 2026-11-01: at least 2 x the sheet and 3 mm)
    for tag, x0, w, y0, d, z0 in (("SUPPLY", "(sb_x0 + fbox_t)", "(sb_w - 2 * fbox_t)", "%s + sb_yf" % YF, "sb_d", "sb_z0 + lin_t"),
                                  ("EXHAUST", "(%s - fb_w)" % XR, "(fb_w - fbox_t)", "%s + clr" % YD, "cart_d",
                                   "%s + face_t + sof_fill_t + cart_w - blk_t - fan_t" % ZS0)):
        for k in (1, 3):
            pts.append(("%s FAN %d" % (tag, (k + 1) // 2), "%s + %s * %d / 4" % (x0, w, k), "%s + %s / 2" % (y0, d), z0))
    return pts


if __name__ == "__main__":
    v = evaluate()
    for key, name, bx in layout():
        print("%-10s %-22s %s" % (key, name, [round(ev(v, e), 2) for e in bx]))
    print("pass_w", v["pass_w"], "col width", round(ev(v, XIR) - v["col_x0"], 2))
