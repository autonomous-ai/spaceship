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
    ("plen_lo", "126 mm", "mm", "confirmed", "PM ruling 2026-11-01 (the Air Engineer's fix): the base plenum under the supply cartridge, 120 in the air report (7e) plus 6, so the cartridge clears the two socket heads of DR's panel on FRONT's B01 (7.6 proud); the cartridge is Z 140 to 1890, 5 under the column's opening (Z 1895)"),
    ("grille_h", "100 mm", "mm", "confirmed", "D-61: a 100 mm kick grille at the column's foot"),
    ("grille_z", "10 mm", "mm", "source", R7E + ": kick grille Z 25 to 125, 10 mm above the column's foot"),
    ("grille_l", "312 mm", "mm", "source", R7E + ": 529 along the front and left faces, 217 of it on the front"),
    ("grille_t", "2 mm", "mm", "assumption", "perforated aluminium grille plates, flush with the room-side face; free area per the report, pattern HOLD"),
    ("hub_w", "180 mm", "mm", "confirmed", "D-61, D-70: a 180 x 180 zone for the sensor hub and controls"),
    ("hub_t", "29 mm", "mm", "source", R7E + ": up to 29 deep, no fill behind it"),
    ("hub_z", "1200 mm", "mm", "source", R7E + ": zone centred at Z 1200; across, it is centred between the front corner angles (X 1063.5 on P04, the report's 1058 is the column's centre)"),
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
    ("b08_x2", "823.5 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B08's second screw"),
    ("b08_x3", "1148.1 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B08's third screw"),
    ("b08_z", "2140.1 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B08's three screws' height"),
    ("b01_x1", "997.2 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B01's first screw, under the supply cartridge"),
    ("b01_x2", "1148.1 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B01's second screw, under the supply cartridge"),
    ("b01_z", "130.0 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B01's two screws' height (washers to Z 136; the cartridge from Z 140)"),
    ("b07_x", "939.0 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B07's lowest screw, moved 4 clear of the column's left face"),
    ("b07_z", "259.8 mm", "mm", "source", "FRONT's DR rebuild (FRONT Engineer, 2026-11-01 07:57, with the Lead's correction: plain washers): B07's lowest screw's height"),
    ("blk_t", "2 mm", "mm", "source", "the air report's sizing (calc.py, D-121): each fan box's 2 mm aluminium bulkhead, the fans mounted on it"),
    ("fan_bore", "135 mm", "mm", "source", "the air report's fan bore (calc.py FAN_BORE 0.135 m): the bulkhead's opening at each fan"),
    ("s_lin_gap", "70 mm", "mm", "source", "D-121, the Air Engineer: the supply box's end-wall linings start about 70 mm above the fans, so the air reaches them"),
    ("e_lin_gap", "50 mm", "mm", "source", "D-121, the Air Engineer: the exhaust box's far-end lining stops 50 mm under the fans"),
    # ---- supply fan box and intake riser, inside the right decor block (D-61, D-62)
    ("sb_x0", "673 mm", "mm", "source", "PM ruling 2026-11-01 (FRONT's fan box points): the supply fan box X 673 to 973, "
     "FRONT's reserved space, 4 mm clear of DR's diagonal tube and its glass slot (was X 645 in report 7e)"),
    ("sb_w", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_d", "155 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_h", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_yf", "28 mm", "mm", "source", "PM ruling 2026-11-01: the supply fan box stands 25 mm further back from DR's front "
     "skin (front face Y -822), so FRONT's tube across the skin at Z 1905 to 1925 fits in front of it with 5 mm (was 3)"),
    ("sb_z0", "1650 mm", "mm", "source", R7E + ": supply fan box Z 1650 to 1950"),
    ("op_x0", "961 mm", "mm", "source", R7E + ": opening from the block into the column top X 961 to 1161, Z 1895 to 2110"),
    ("op_z0", "1895 mm", "mm", "source", R7E + ": opening Z 1895 to 2110"),
    ("op_h", "215 mm", "mm", "source", R7E + ": opening 200 x 215"),
    ("rs_x0", "956 mm", "mm", "source", "FRONT's reserved space for the riser (ri_x0, DR model; the air report's D-60 table): "
     "X 956 to 1095 (report 7e had 955)"),
    ("rs_w", "139 mm", "mm", "source", R7E + ": intake riser 139 wide, 155 deep"),
    ("rs_d", "150 mm", "mm", "source", "the air report's D-130 table (riser_y, riser_lo): the riser Y -803 to -653, 4.8 mm off "
     "DR's corner facet at its front-right corner and 6.5 off DR's frame face (was 155; FRONT's ri_d follows with D-130)"),
    ("rs_y0", "-803 mm", "mm", "source", R7E + ": intake riser Y -803 to -648"),
    ("rs_z0", "252 mm", "mm", "source", "FRONT's reserved space for the riser (DR model on main: its open foot 140 over DR's "
     "base, Z 252); D-130's sealed intake boot (611502, to come) takes the air from the mesh up to this foot (was Z 105)"),
    ("rs_z1", "1445 mm", "mm", "source", R7E + ": intake riser Z 105 to 1445, then it widens into the fan box below Z 1650"),
    ("rs_t", "1 mm", "mm", "confirmed", "D-61: 1 mm steel intake riser"),
    # ---- how the supply fan box assembly rests in DR (PM rulings 2026-11-01, after the box moved back): a lip angle on
    #      the box's front wall on two rubber pads on DR's shelf tube F08, and a rubber buffer on the riser's front face
    #      against DR's cross tube F07; the outlet's soft lip seal carries no load. DR's frame values are FRONT's (its DR
    #      STEP on main, 350003 P01): F08 Y -847 to -827, top Z 1650 (fb_z0), right end X 1030.85 at the facet side tube
    #      F02; F07 Z 834 to 854, the same right end
    ("dr_skin_t", "3 mm", "mm", "source", "FRONT's DR skin, ACP 3 (DR model's dr_skin_t): DR's front ring tubes start behind it"),
    ("dr_fr_w", "20 mm", "mm", "source", "FRONT's DR frame tube 20 x 20 (DR model's fr_w): F07 and F08"),
    ("dr_f08_x1", "1030.85 mm", "mm", "source", "FRONT's DR STEP on main (350003 P01): F08's and F07's right end, at the facet "
     "side tube F02's inner face"),
    ("dr_f07_zc", "844 mm", "mm", "source", "FRONT's DR STEP on main (350003 P01): F07, the front ring's cross tube, Z 834 to 854"),
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
    ("dr_fac_xa", "1050.85 mm", "mm", "source", "FRONT's DR STEP on main: C04's inner face, front end, X"),
    ("dr_fac_ya", "-820.11 mm", "mm", "source", "FRONT's DR STEP on main: C04's inner face, front end, Y"),
    ("dr_fac_xb", "1221.72 mm", "mm", "source", "FRONT's DR STEP on main: C04's inner face, back end, X"),
    ("dr_fac_yb", "-666.5 mm", "mm", "source", "FRONT's DR STEP on main: C04's inner face, back end, Y"),
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
    ("ut_yr", "ut_ay + (pod_w / 2 - stack_t - col_gap - ut_ax) * (dr_fac_yb - dr_fac_ya) / (dr_fac_xb - dr_fac_xa)", "mm",
     "calculation", "the transition's facet side meets its right end (the opening's, X 1161), Y (about -717)"),
    # ---- roof slot, sleeve and grille (D-61: Y -620 to -326, in the right outer ceiling panel)
    ("slv_t", "1 mm", "mm", "assumption", "roof sleeve wall, galvanised steel"),
    ("rg_t", "2 mm", "mm", "assumption", "roof grille plate; 50 % free or more (report 7e), pattern HOLD"),
    # the sleeve's top flange on C2's skin, with the grille's 4 rivnuts 838003 (J-AIR-03, HOLD-04's edge rule: each
    # rivnut 2 hole diameters from every free edge, the skin's slot edge too; CEILING's layout, 2026-11-01): 2 on the
    # left side; 2 on the back side BEHIND cross member 1, whose front face is too near the slot for a set rivnut's
    # bulge; none on the front (the front member under the skin) or the right (19.0 to the side member)
    ("slv_rn_e", "19.2 mm", "mm", "calculation", "rivnut centre to any free edge: 2 x the 9.53 hole (19.06), rounded up (HOLD-04)"),
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
    "sof_fill": ("611203", "AIR - SOFFIT FILL", "Hộp gió - bông", "MP", "pfill"),
    "sof_fill_f": ("611211", "AIR - SOFFIT FILL - FRONT", "Hộp gió - bông - tấm trước", "MP", "pfill"),
    "egrille": ("611204", "AIR - EXHAUST GRILLE", "Lưới gió thải", "MP", "perf40"),
    "casing": ("611301", "AIR - CARTRIDGE CASING", "Vỏ ống tiêu âm nhôm 2 mm", "MP", "al"),
    "layer": ("611302", "AIR - CARTRIDGE LAYER 50", "Lớp tiêu âm 50 mm", "MP", "pyro"),
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
    "stud": ("618104", "AIR - SOFFIT HANGER STUD - HOLD", "Vít treo hộp gió (chờ)", "HOLD", "hold"),
    "hinge": ("618105", "AIR - SOFFIT UNDERSIDE HINGE - HOLD", "Bản lề mặt dưới hộp gió (chờ)", "HOLD", "hold"),
    "latch": ("618106", "AIR - SOFFIT UNDERSIDE LATCH - HOLD", "Chốt bấm mặt dưới hộp gió (chờ)", "HOLD", "hold"),
    "hub": ("618101", "AIR - SENSOR HUB ZONE - HOLD", "Vùng bộ cảm biến (chờ)", "HOLD", "hold"),
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
FRONT_NAMED = ("dr_back_t", "dr_acc_t", "dr_acc_face_y")
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
    cz0 = "%s + plen_lo" % ZCB
    cz1 = "%s + cart_l" % cz0
    b.append(("cart", "CARTRIDGE SUPPLY", box(cx0, cx1, cy0, cy1, cz0, cz1)))
    # the column's right side at the two plenums (the cartridge closes the rest)
    py1 = "%s - face_t - ang_w" % YFACE
    b.append(("col_side_lo", "COLUMN PLENUM PLATE LOW", box("%s - plate_t" % XR, XR, YD, py1, ZCB, cz0)))
    b.append(("col_side_hi", "COLUMN PLENUM PLATE HIGH", box("%s - plate_t" % XR, XR, YD, py1, cz1, ZS0)))
    b.append(("col_fill", "COLUMN FILL FRONT", box("col_x0 + face_t + ang_f", "%s - ang_f" % XR, cy1,
                                                     "%s - face_t" % YFACE, cz0, cz1)))
    b.append(("col_fill_l", "COLUMN FILL LEFT", box("col_x0 + face_t", cx0, "%s + ang_w" % YD, cy1, cz0, cz1)))
    hx = "(col_x0 + face_t + ang_f + %s - ang_f) / 2" % XR     # centred between the front angles' legs
    b.append(("hub", "SENSOR HUB ZONE", box("%s - hub_w / 2" % hx, "%s + hub_w / 2" % hx, "%s - hub_t" % YFACE,
                                             YFACE, "hub_z - hub_w / 2", "hub_z + hub_w / 2")))
    # soffit: underside sections (dark tone), front face, top rails, left end plate
    zf1 = ZRB                                      # front face up to the rail (riveted); pockets round the studs
    for key, name, x0, x1 in soffit_sections():
        b.append((key, name, box(x0, x1, YD, "%s - face_t" % YFACE, ZS0, "%s + face_t" % ZS0)))
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
    # the fill under the cartridge stops short of the latch line, so no latch cuts it, wherever the
    # sections' quarter points fall (a latch cut that missed the fill failed at pod_w 2600)
    b.append(("sof_fill", "SOFFIT FILL UNDER", box("%s - cart_l" % ex1, XR, cy0, "%s - face_t - hl_h" % YFACE,
                                                    "%s + face_t" % ZS0, ez0)))
    b.append(("sof_fill_f", "SOFFIT FILL FRONT", box("%s - cart_l" % ex1, XR, cy1, "%s - face_t" % YFACE, ez0, ZBT)))
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
    zh0, zh1 = "%s + face_t" % ZS0, "%s + face_t + hl_h" % ZS0
    for key, name, x0, x1 in soffit_sections()[:2]:
        for q in (1, 3):
            xc = "(%s) + ((%s) - (%s)) * %d / 4" % (x0, x1, x0, q)
            b.append(("hinge", "%s HINGE %d" % (name, q), box("%s - hinge_l / 2" % xc, "%s + hinge_l / 2" % xc,
                                                             YD, "%s + clr" % YD, zh0, zh1)))
            b.append(("latch", "%s LATCH %d" % (name, q), box("%s - latch_l / 2" % xc, "%s + latch_l / 2" % xc,
                                                             "%s - face_t - hl_h" % YFACE, "%s - face_t" % YFACE, zh0, zh1)))
    # supply fan box joined with the intake riser (D-87), the transitions, the roof sleeve and grille
    sy0 = "%s + sb_yf" % YF
    b.append(("box_s", "SUPPLY FAN BOX", box("sb_x0", "sb_x0 + sb_w", sy0, "%s + sb_d" % sy0, "sb_z0", "sb_z0 + sb_h")))
    b += fan_box_inner()
    # the upper transition: over the box and in the passage beside it, full depth (its shape: transition_outlines())
    b.append(("trans", "SUPPLY TRANSITION", box("sb_x0", XR, sy0, YB_FRAME, "op_z0", "op_z0 + op_h")))
    b.append(("riser", "INTAKE RISER", box("rs_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z0", "rs_z1")))
    # the lower transition: FRONT's trapezoid from the riser's top to the box's bottom (riser_transition_outline()), across
    # the box's and the riser's depths
    b.append(("rtrans", "RISER TRANSITION", box("sb_x0", "rs_x0 + rs_w", sy0, "rs_y0 + rs_d", "rs_z1", "sb_z0")))
    # how the assembly rests in DR: the lip angle on two pads on F08, the riser's buffer against F07 (PM rulings 2026-11-01)
    b.append(("lip", "FAN BOX LIP ANGLE SUPPLY", box("sb_x0", LIP_X1, LIP_Y0, sy0, "sb_z0 + pad_t", "sb_z0 + pad_t + lip_h")))
    for side, x0 in (("LEFT", "sb_x0 + pad_in"), ("RIGHT", "%s - pad_in - pad_l" % LIP_X1)):
        b.append(("pad", "FAN BOX PAD %s" % side, box(x0, "%s + pad_l" % x0, "%s - pad_w / 2" % F08_YC,
                                                      "%s + pad_w / 2" % F08_YC, "sb_z0", "sb_z0 + pad_t")))
    b.append(("buffer", "RISER BUFFER", box("%s - buf_d / 2" % BUF_X, "%s + buf_d / 2" % BUF_X,
                                            "%s + dr_skin_t + dr_fr_w + buf_gap" % YF, "rs_y0 - rvn_head",
                                            "dr_f07_zc - buf_d / 2", "dr_f07_zc + buf_d / 2")))
    # the roof sleeve with its top flange on C2's skin, and the grille on the flange (J-AIR-03)
    fx0, fx1, fy0, fy1 = sleeve_flange()
    b.append(("sleeve", "ROOF SLEEVE", box(fx0, fx1, fy0, fy1, "%s + cart_w" % ez0, "pod_h + slv_t")))
    b.append(("rgrille", "ROOF GRILLE", box(fx0, fx1, fy0, fy1, "pod_h + slv_t", "pod_h + slv_t + rg_t")))
    return b


# the lip's ends and tip, the pads' line on F08 and the buffer's place over F07 (PM rulings 2026-11-01)
LIP_X1 = "(dr_f08_x1 - lip_end)"
LIP_Y0 = "(%s + dr_skin_t + lip_tip)" % YF
F08_YC = "(%s + dr_skin_t + dr_fr_w / 2)" % YF
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
    y0, xr = "(%s + sb_yf)" % YF, XR
    top = [("sb_x0", y0), ("ut_xf", y0), (xr, "ut_yr"), (xr, YB_FRAME), ("sb_x0", YB_FRAME)]
    side = [("sb_x0 + sb_w", y0), ("ut_xf", y0), (xr, "ut_yr"), (xr, YB_FRAME), ("sb_x0 + sb_w", YB_FRAME)]
    return [(top, "sb_z0 + sb_h", "op_z0 + op_h"), (side, "op_z0", "sb_z0 + sb_h")]


def riser_transition_outline():
    """The lower transition's side outline [(x, z)]: FRONT's trapezoid from the riser's top to the box's bottom, run in
    Y across both depths (the box's front line to the riser's back)."""
    return [("rs_x0", "rs_z1"), ("rs_x0 + rs_w", "rs_z1"), ("sb_x0 + sb_w", "sb_z0"), ("sb_x0", "sb_z0")]


def sleeve_flange():
    """(x0, x1, y0, y1) of the roof sleeve's top flange, which the grille covers exactly (CEILING's layout 2026-11-01)."""
    return ("slot_x0 - slv_fl_l", "slot_x0 + slot_w + slv_fl_f", "slot_y0 - slv_fl_f", "slot_y0 + slot_d + slv_fl_b")


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
    lock screws' holes. [(body name, kind, args)]: kind 'zcircle' (x, y, z0, z1, d), 'ycircle'
    (x, z, y0, y1, d) or 'box' (x0, x1, y0, y1, z0, z1)."""
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
    # the riser buffer's rivnut hole in the riser's front wall, over F07 (PM ruling 2026-11-01)
    out.append(("INTAKE RISER", "ycircle", (BUF_X, "dr_f07_zc", "rs_y0", "rs_y0 + rs_t", "hole_rvn")))
    # the grille's rivnuts in the sleeve's flange, and the grille's bolt holes over them (J-AIR-03, R-J6's 7.0)
    for _n, x, y in sleeve_rivnuts():
        out.append(("ROOF SLEEVE", "zcircle", (x, y, "pod_h", "pod_h + slv_t", "hole_rvn")))
        out.append(("ROOF GRILLE", "zcircle", (x, y, "pod_h + slv_t", "pod_h + slv_t + rg_t", "lock_hole")))
    return out


def cutouts():
    """(body name to cut, cutter box): the hub zone through the front face and the fill
    behind it, the exhaust grille's opening in the soffit underside, the room-side stud heads'
    pockets in the soffit's front face, the door-side stud heads' pockets in the door-side plate,
    and B08's head pockets in the fill under the exhaust cartridge."""
    lay = {name: bx for _k, name, bx in layout()}
    hub = lay["SENSOR HUB ZONE"]
    eg = lay["EXHAUST GRILLE"]
    hub_cut = (hub[0], hub[1], "%s - face_t - 40 mm" % YFACE, hub[3], hub[4], hub[5])
    eg_cut = (eg[0], eg[1], eg[2], eg[3], ZS0, "%s + face_t" % ZS0)    # the grille's opening through the face
    out = [("COLUMN FACE FRONT", hub_cut), ("COLUMN FILL FRONT", hub_cut), ("SOFFIT UNDERSIDE LEFT", eg_cut)]
    for name, x, y in [p for p in stud_points() if p[0].endswith("ROOM")] + lock_points():
        # a head pocket: the head plus 1.5 all round (the room-side studs' and the lock screws')
        out.append(("SOFFIT FACE FRONT", ("%s - stud_d / 2 - hd_c" % x, "%s + stud_d / 2 + hd_c" % x,
                                          "%s - face_t" % YFACE, YFACE, ZBT, ZRB)))
    out += [("SOFFIT DOOR PLATE", bx) for _n, bx in door_stud_pockets()]
    out += [("SOFFIT FILL UNDER", bx) for _n, bx in b08_fill_pockets()]
    return out


# D-120: parts placed as copies of one component, and the parts whose layout boxes are one body together (a stud's or a
# screw's head and shank, joined): {key: how the layout's names group into one copy}
JOINED = {"stud": (" HEAD", " SHANK"), "lock": (" HEAD", " SHANK")}
COPIES = {"stud", "lock", "hinge", "latch", "lin_es", "lin_s", "layer", "pad"}
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


def fan_points():
    """Fan centres (x, y, z of the fan's underside): two in each fan box, lying flat. The supply fans stand on their
    bulkhead 50 above the box's floor; the exhaust fans hang under a sealed bulkhead at the box's top and blow
    straight into the roof sleeve (D-121: low fans let the cartridge's upper passages short-circuit)."""
    pts = []
    for tag, x0, w, y0, d, z0 in (("SUPPLY", "sb_x0", "sb_w", "%s + sb_yf" % YF, "sb_d", "sb_z0 + lin_t"),
                                  ("EXHAUST", "%s - fb_w" % XR, "fb_w", "%s + clr" % YD, "cart_d",
                                   "%s + face_t + sof_fill_t + cart_w - blk_t - fan_t" % ZS0)):
        for k in (1, 3):
            pts.append(("%s FAN %d" % (tag, (k + 1) // 2), "%s + %s * %d / 4" % (x0, w, k), "%s + %s / 2" % (y0, d), z0))
    return pts


if __name__ == "__main__":
    v = evaluate()
    for key, name, bx in layout():
        print("%-10s %-22s %s" % (key, name, [round(ev(v, e), 2) for e in bx]))
    print("pass_w", v["pass_w"], "col width", round(ev(v, XIR) - v["col_x0"], 2))
