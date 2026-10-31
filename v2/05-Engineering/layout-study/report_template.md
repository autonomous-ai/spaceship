<!-- report.md is generated from report_template.md by scripts/run_all.py. Edit the template or the scripts, never report.md. -->
# Spaceship layout study: weight, pallets and 2-person assembly

Status words: every number carries one of confirmed, source, calculation, assumption or unverified (guideline section 10). A value the PM decided is confirmed and cites its decision, D-xx in `v2/00-Control/decision-log.md`. Under AGENTS.md the PM decides and the log records it. HOLD marks a part or interface that a supplier or a sample must confirm first. Spaceship is the working name of v2 (folders keep their v2 names).

Every number below comes from the scripts in `scripts/`. `python3 scripts/run_all.py --check` proves that this report and the files in `out/` reproduce exactly. Section 10 lists the inputs, their status and their sources.

## Result

1. **Weight.** v1 weighs {{v1_bom}} kg by its BOM (range {{v1_lo}} to {{v1_hi}} kg). Spaceship as planned weighs {{plan_total}} kg, and the light build {{light_total}} kg ({{fast_total}} kg with the fast-assembly hardware). The decided build comes to **{{final_total}} kg** against the PM's {{cap_kg}} kg cap (**{{cap_note}}**, open item LS-01, ISS-080). The sound and air check (PR #11) puts the same build at {{hw_total}} kg in its own model, about 418. The {{reconcile_diff}} kg between the two is almost all in the walls and ceiling: this study carries the lining cassettes' clips and rails ({{gap_clips}} kg) and the bond lines ({{gap_bond}} kg), and that check leaves both out; without them this study's walls and ceiling are {{shell_core_diff}} than the check's. Both are assumptions. By D-54 the cap stays at {{cap_kg}} kg and {{final_total}} kg is the current estimate, open against it; two wall-sample tests settle it: weigh a real cassette with its clips, rails and bond lines per m2, and test the {{fill_light}} kg/m3 fill next to the {{fill_final}} kg/m3 (section 5.1).
   - In the build: the sound study's final walls and ceiling with the 0.5 mm tray (the 0.4 mm tray would have saved {{tray_thin_saving}} kg but cost 1 dB, D-37); 20 x 40 x 1.2 frames (save {{winback_frames}} kg against 1.5 mm, D-34); fill at {{fill_final}} kg/m3 ({{fill_light}} kg/m3 would save {{light_fill_saving}} kg, but that grade has no published absorption, so the wall sample tests it first, D-54); back wall and ceiling frames that span frame to frame, {{back_w_final}} mm per half with {{lin_back_w}} mm linings; four 12 V fans in two cartridges with the exhaust riser, all in the right decor block; and a frameless 4+4 laminated front.
2. **Parts.** Every part is 20 kg or less except the glass. The door ships as one unit {{door_unit_l}} mm long and {{final_door_kg}} kg: 4+4 laminated glass ({{door_glass_h}} mm), a kick strip {{kick_strip_h}} mm tall holding the drop seal, and the hinges and pull fitted in the factory. Its hinges and lock are on HOLD until a set rated for this glass, 47.5 kg and 1176 mm is named (D-46, D-56). Two people carry it with 2 suction lifters ({{final_door_each}} kg each). The fixed panel weighs {{final_fixed_kg}} kg. Each splitter cartridge weighs {{cart_each}} kg with its 2 fans fitted, and the riser {{riser_kg}} kg. They slide into the mounted right decor block ({{final_dr}} kg) from inside, through its removable inner panel (D-59), so no lift carries the block and its air parts together ({{dr_plus_carts}} kg).
3. **Shipping (confirmed, D-04).** One 48 x 40 pallet and one 96 x 48 pallet, {{final_gross}} kg gross, {{final_pcf}} lb/ft3. The 48 x 40 weighs {{final_std_kg}} kg and stands {{final_std_h}} mm high. The 96 x 48 weighs {{final_long_kg}} kg and stands {{final_long_h}} mm high, with both lites flat on top in their frame. Walls and ceiling are {{final_wall_t}} mm thick.
4. **Assembly (confirmed changes, D-08).** Two people with one 5 mm hex key. The light build takes {{before_min}} min before the fast-assembly changes and {{after_min}} min after. The decided build takes **{{final_min}} min** ({{final_ph}} person-hours): {{final_bolts}} M6 bolts, {{final_cams}} tool-free clips and {{final_cassettes}} clip-on lining cassettes. The 1-hour target is not reached on these assumptions. Most of what remains is unpacking, levelling, setting the glass and door, and testing, so the timed prototype decides.
5. **Decisions.** Every layout choice is confirmed by a decision; the table below cites it.
6. **The live weight count on skeleton P04** ([weight-rollup.md](weight-rollup.md), ISS-081, F-010): **{{rollup_total}} kg as shipped, {{rollup_cap_gap}} the 420 kg cap and {{rollup_target_gap}} the PM's 410 kg target.** It takes the adopted savings of D-81 and D-85 ({{rollup_applied}} kg in all; the 24 kg/m3 fill, the 1.5 mm base band and the poplar-core floor are provisional on T02 and BASE's checks), budgets and allowances for the light shelf, the work-wall ledge and the named clips, tonight's CAD masses (CEILING PR #32, FRONT PRs #27 and #28, WALL's L1), D-60's air parts and the P04 sizes. The voice kit's 4.0 kg reserve rides outside the cap (D-11, D-81). Its part list is `out/parts-decided-P04.csv`. The sections below still describe the P03 build.

## Decisions

Decided specs, each citing the decision log (`v2/00-Control/decision-log.md`, D-01 to D-59).

| Decision | Status | Log |
| --- | --- | --- |
| Keep the plan's panel split: 2 frames per side wall (vách hông), 4 back wall frames (vách hậu), 2 ceiling halves (trần), 3 decor blocks (khung trang trí) | confirmed | D-23 |
| Every part 20 kg or less except the glass | confirmed | D-03 |
| Ship on one 48 x 40 and one 96 x 48 pallet. Don't split the decor blocks: a seam across the faceted front breaks the look rule, and a third pallet costs more than it saves | confirmed | D-04 |
| Thin floor inside an aluminium base band (viền chân); the band drops to a 20 mm threshold across the door only. Castors are a possible later accessory, not part of v2 | confirmed | D-05, D-18 |
| Aluminium frames, 20 x 40 x 1.2 mm at {{pitch_acp}} mm, in the walls and in the ceiling; walls and ceiling on the same {{final_wall_t}} mm stack | confirmed | D-16, D-34, D-42 |
| Back wall (vách hậu) and ceiling (trần) frames span frame to frame between the side frames: {{back_w_final}} mm per half, with their lining cassettes at {{lin_back_w}} mm | confirmed | D-55 |
| Side walls (vách hông) {{wall_depth}} mm deep, starting at the decor back plate as in v1. Side lining cassettes {{side_cass_l}} mm long to close the inside corner; the upper ones {{side_cass_up_h}} mm tall, stopping 4 mm under the roof frame so they float | confirmed | D-49, D-57 |
| No plywood behind the ACP; the sound mass sits in the floating lining cassette with a 0.5 mm steel tray (0.4 mm cost 1 dB) | confirmed | D-17, D-37 |
| Cavity fill (bông PET) at {{fill_final}} kg/m3: the lighter grade has no published absorption, so D-34's {{fill_light}} kg/m3 doesn't apply yet. The wall sample tests it next to the {{fill_final}} kg/m3, and the build switches if it matches on sound | confirmed | D-54 |
| Fast-assembly changes: factory subassemblies, captive bolts, tool-free clips on panel seams, felt pre-fitted (section 4) | confirmed | D-08 |
| Front: 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look). The door is left-hinged; it carries an aluminium kick strip {{kick_strip_h}} mm tall in the base band's dark finish, holding the drop seal, so the door unit is {{door_unit_l}} mm long. Door and fixed glass are carried by two people with suction lifters. Door hinges and lock on HOLD until a rated set is named | confirmed | D-19, D-27, D-40, D-46, D-56, D-57 |
| Weight: cap {{cap_kg}} kg with the 0.5 mm tray. This study's {{final_total}} kg is the current estimate, open against it until the wall sample is weighed; the PM rules on trims if the sample still lands over | confirmed | D-37, D-54 |
| Air (thông gió): four 12 V fans (quạt thông gió), two per path, in the lined fan boxes of two splitter cartridges (ống tiêu âm) side by side in the right decor block, supply grille low and exhaust grille high on its inner face. The room-side intake sits low on the block (its underside or the bottom of its outer face) and the exhaust leaves through the top slot, at least 1 m apart; a 150 mm riser carries the exhaust up to the slot. The block's inner face is a removable, felt-covered panel carrying both grilles; the cartridges and riser slide in and out through it, into the pod, for fitting and service (inside only). Lifting them out through the top lid is rejected: it would need about 4.5 m of room height. If a full-length cartridge proves awkward inside the 2.3 m pod, it splits into two sections with a sealed slip joint. Fan sample and the riser's CAD fit on HOLD | confirmed | D-29, D-51, D-52, D-56, D-58, D-59 |
| Lining cassettes ship as separate clip-on inner leaves, one per panel, with the outside seams as planned; captive mechanical clips with a rated load, plus a safety catch on the ceiling ones; the clip and catch on HOLD | confirmed | D-17, D-23, D-47, D-56 |
| Ceiling fill carried on the back of the ceiling cassettes | confirmed | D-24 |
| Decor block (khối trang trí) depth {{decor_depth}} mm, as v1 (measured from its drawings and STEP); not D-39's 230 to 235, nor the plan's 200 | confirmed | D-49 (replaces D-39) |
| Decor cladding in Dark Yellow ACP EV3038 (no weight effect) | confirmed | D-12 |
| Rejected: split decor blocks (B2), 5 bands per wall (C), full-height walls, castors in v2, no floor | confirmed | D-04, D-05, D-18, D-23 |

## 1. Weight

### 1.1 v1 baseline (short)

The v1 BOM (2026-10-29) is the main source; the older STEP (2026-10-14) is a cross-check only. The range comes from wood densities and from the board conflict already on the issue list: the BOM lists 9 mm inner and floor boards, the drawings and the STEP show 15 mm ply. "Tấm nhôm" skins are taken as ACP (the decor skins are routed and folded, which is how ACP is worked). If they were solid aluminium sheet, v1 would gain {{v1_solid_al_delta}} kg.

{{table_v1}}

STEP cross-check (same densities). The STEP agrees with the BOM on every big item except board thickness, where it matches the drawings. Glass is lighter in the STEP because the BOM gives the rectangles to cut from, and the STEP gives the finished shape:

{{table_v1_step}}

{{v1_over20_n}} of v1's shipping pieces weigh over 20 kg, not counting the glass: {{v1_over20}}.

### 1.2 Spaceship as planned and the light build

"As planned" follows the build plan: 3 mm ACP glued to 6 mm plywood on 20 x 20 steel tube (1.2 mm wall, assumed), 9 mm PET felt, the raised 50 x 100 steel floor with 30 x 60 joists and 6 feet, a decor core of 20 x 20 steel, 10 mm glass as v1, and the table. The light build is the cumulative result of the steps below. Section 5 adds the sound study's final walls on top of it.

{{table_assy}}

How the light build gets there, one change at a time:

{{table_waterfall}}

Notes:
- Glass weights use the finished shapes from the STEP: door {{glass_area_door}} m2, fixed panel {{glass_area_fixed}} m2. Decor skins use the STEP's finished areas too ({{decor_area_step}} m2, against {{decor_area_bom}} m2 of cutting rectangles in the BOM).
- The ACP is Alcorest EV3038, 3 mm with 0.21 mm skins (the plan's VT01). The maker gives skins, not kg/m2; 3.5 kg/m2 is the sound study's calculation, used here by the PM's ruling. Every 0.1 kg/m2 of ACP changes the pod by {{acp_sens}} kg.
- The colour of the decor cladding (yellow ACP in the plan's materials, black in the plan's pictures) is on the issue list. It does not change any weight.

### 1.3 Variants

One change at a time against the light build:

{{table_alts}}

The smoked acrylic front is the biggest single lever, but the decided build uses 4+4 laminated glass: acrylic needed an opaque band down the door, which breaks the look. The sandwich walls are heavier than the frame build here, because the frame build without plywood is already {{light_wall_kgm2}} kg/m2. Sandwich walls buy flatness and a second skin, not weight.

### 1.4 Every part against 20 kg

Light build: no part is over 20 kg except the glass (door {{door_glass8}} kg, fixed panel {{fixed_glass8}} kg at 8 mm). Over 20 kg in the light build: {{light_over20}}. Over 20 kg as planned: {{plan_over20}}. With the felt pre-fitted, the light build's wall and ceiling panels weigh {{fast_panel_min}} to {{fast_panel_max}} kg. For the decided build see section 5.

<details><summary>Part list with weights, light build</summary>

{{table_parts_light}}

</details>

<details><summary>Part list with weights, as planned (option A)</summary>

{{table_parts_plan}}

</details>

## 2. Panel split options

All options use only standard pallets. On a 48 x 40 in pallet (1219 x 1016 mm), panels stand upright with their length along the 48 in side, at most about 6 ft loaded. On a 96 x 48 in pallet (2438 x 1219 mm), long pieces and glass lie flat. Freight density is gross weight over the pallet footprint times the loaded height. The LTL class depends on the NMFC item and, for density-rated items, on density, so this report gives densities and does not guess a class. B1, B2 and C below use the light build with the confirmed fast-assembly changes (D-08); section 5 repeats B1 with the final walls.

{{table_options}}

- **A, plan as written.** Fits 2 pallets only if the raised floor frame ships as knock-down bars; welded as in v1 (2500 x 1703 mm per the v1 BOM, {{v1_fl_kg}} kg), it fits no standard pallet. Heaviest option ({{A_total}} kg). The right decor block is over 20 kg, and the floor boards need screws and a driver.
- **B1, confirmed (D-04).** Panels, short base band pieces, floor panels and the felt strips go on the 48 x 40 ({{B1_std_kg}} kg, {{B1_std_h}} mm high). The decor blocks, the long base band pieces, the kit boxes and the glass go on the 96 x 48 ({{B1_long_kg}} kg, {{B1_long_h}} mm high). Its longest piece is {{longest_piece}} mm ({{longest_in}} in), under the 96 in length where most LTL carriers start overlength charges. One long pallet is needed anyway: the glass is 2011 and 2139 mm long.
- **B2, rejected.** Cutting the decor blocks and standing the base band up puts everything except the glass on 48 x 40 pallets. But it needs two of them, and the glass still takes the long pallet alone: {{B2_npal}} pallets, {{B2_gross}} kg gross. The cut also puts seams across the faceted front.
- **C, rejected.** Five stacked bands per wall (like Orangebox Air3) give light {{band_min}} to {{band_max}} kg parts. But they add {{bolts_C_extra}} fixings, {{band_extra_seams}} extra visible seams per wall, {{conn_extra_C}} more cable connectors and more gasket to seal. With the plan's split, parts are already under 20 kg, so bands buy nothing.
- **Fewer, larger panels, rejected where the 20 kg limit bites.** A full-height side wall weighs {{full_wall_kg}} kg even without felt. A full-height back panel with felt pre-fitted weighs {{tallback_kg}} kg. Both are over 20 kg.

<details><summary>Option A: part list, joints, pallets, assembly</summary>

{{A_parts}}

{{A_joints}}

{{A_pallets}}

{{A_steps}}

</details>

<details><summary>Option B1 (confirmed, D-04), light build: part list, joints, pallets</summary>

{{B1_parts}}

{{B1_joints}}

{{B1_pallets}}

</details>

<details><summary>Option B2: part list, joints, pallets, assembly</summary>

{{B2_parts}}

{{B2_joints}}

{{B2_pallets}}

{{B2_steps}}

</details>

<details><summary>Option C: part list, joints, pallets, assembly</summary>

{{C_parts}}

{{C_joints}}

{{C_pallets}}

{{C_steps}}

</details>

## 3. Floor options

Weighed as the BASE assembly (khung sàn / sàn) under the light build. Step height is from the room floor to the walking surface at the door. Sound notes are directions for the sound group, not ratings.

{{table_floors}}

Confirmed (D-05, D-18): the thin floor. It is {{raised_vs_thin}} kg lighter than the raised steel floor, closes the box for sound, and cuts the step from {{raised_step}} mm to {{thin_step}} mm. The room inside gets {{height_gain}} mm taller. No floor saves a further {{none_vs_thin}} kg, but leaves the box open to the room floor, which the market study says leaks most. Castors would let an assembled pod roll around the office. They would cost about {{castor_vs_thin}} kg over the thin floor, a step of about {{castor_step}} mm with a ramp, a skirt to close the gap when parked, and a stiffer platform so the door stays in line while rolling. Confirmed (D-05, D-18): a possible later accessory, not part of v2.

## 4. Assembly by 2 people

Tool: {{tool}}. A small step stool is needed for the ceiling and the top fixings; it is not a tool. Every bolt and clip is reached from inside the pod, through open frame bays or behind the loose felt strip over each joint. The strips, or in the decided build the lining cassettes, go on last.

Before and after the confirmed fast-assembly changes (D-08), on the light build. Each row adds one change to the rows above it, with the same time model:

{{table_levers}}

The full-height back wall panel (fewer, larger panels) was also tried. With the felt pre-fitted it weighs {{tallback_kg}} kg, over the limit, so it is not used.

What remains is mostly work that does not shrink with fewer parts: unpacking, levelling, setting the glass and the door, and testing the electrics. The 1-hour target needs that work timed on the prototype, and possibly more done in the factory. Section 5 gives the step-by-step sequence and access check for the decided build.

Benchmark: Room S needs 4 people for 3 to 5 hours (12 to 20 person-hours), and hushMeet 2 installers for 2.5 to 3 hours (market study). The decided build takes {{final_ph}} person-hours.

## 5. The decided build: final wall stack (re-check)

The sound study's final stack (confirmed, D-16, D-17, D-34, D-37, D-42): ACP 3 mm on a 20 x 40 x 1.2 aluminium frame at {{pitch_acp}} mm with 40 mm PET fill at {{fill_final}} kg/m3, then a floating lining cassette: a 0.5 mm steel tray, 25 mm deep, with 9 mm felt across its face. That makes {{final_wall_t}} mm and {{final_kgm2_hw}} kg/m2 in the sound study. The ceiling uses the same stack. The front is frameless 4+4 laminated glass.

This study builds it on the B1 layout. The outer panel (ACP, frame and fill) and its cassette are separate parts; the cassette is the clip-on inner leaf (D-17). Sizes follow the pod skeleton P03 (S32):
- side walls (vách hông) {{wall_depth}} mm deep, starting at the decor back plate as in v1 (D-49); side cassettes {{side_cass_l}} mm long, running past the back cassettes' face to close the inside corner; the upper ones {{side_cass_up_h}} mm tall, stopping 4 mm under the roof frame so they float (D-57);
- back wall (vách hậu) and ceiling (trần) outer panels {{back_w_final}} mm per half, frame to frame between the side frames, with the side skins covering their edges; their cassettes {{lin_back_w}} mm (D-55);
- decor blocks (khối trang trí) {{decor_depth}} mm deep, as v1 (D-49). Their weights already came from v1's real shapes in the STEP, so only the packing changes.

The inside narrows to {{inner_w_final}} mm. The wall here comes to {{final_wall_kgm2}} kg/m2 with clips and tray returns (the sound study: {{final_kgm2_hw}}). The door edge seals, base seal and cable grommets are counted too.

Air (thông gió), as the sound and air check picked it (D-51, S30): {{n_fans}} 12 V fans (quạt thông gió; Noctua NF-A14 industrialPPC-3000 PWM, {{fan12_kg}} kg each, an assumption until the sample is weighed), two per path on a bulkhead in each cartridge's lined fan box; two splitter cartridges (ống tiêu âm), {{cart_size}} mm, {{cart_kg}} kg each with their fill and {{cart_each}} kg with their fans; and the {{riser_size}} mm exhaust riser, {{riser_kg}} kg. That is {{air_total}} kg, all in the right decor block. The room-side intake sits low on the block and the exhaust leaves through the top slot, at least 1 m apart, so the pod doesn't breathe its own exhaust (D-58). The top block carries no air parts, and there is no loose decor fill: the 40 mm fill in front of each cartridge replaces the old felt-lined decor cavity (S31).

Result: **{{final_total}} kg** against the {{cap_kg}} kg cap ({{cap_note}}), {{final_over20}} parts over 20 kg except the glass, heaviest {{final_heaviest}}, {{final_npal}} pallets, {{final_gross}} kg gross, {{final_maxh}} mm at most, assembly {{final_min}} min.

### 5.1 Against the sound and air check's 418 kg

Same build, two models. The check (PR #11) multiplies its wall and ceiling mass per m2 by the outside areas, adds its bought parts, and takes the rest of the pod from an older copy of this study. This study adds up its own parts:

{{table_reconcile}}

The gap is the clip and bond allowances, which neither model can source yet: the clip is still a candidate (Häfele KEKU EH, HOLD) and the bond pattern waits for its coupon test. By D-54 the cap stays at {{cap_kg}} kg and this study carries {{final_total}} kg as the current estimate, open against it (LS-01, ISS-080). The factory's wall sample (D-32) settles it with two tests: weigh a real cassette with its clips, rails and bond lines per m2, and test the {{fill_light}} kg/m3 fill next to the {{fill_final}} kg/m3; if the lighter fill matches on sound, the build switches and saves {{light_fill_saving}} kg. If the sample still lands over {{cap_kg}} kg, the PM rules on trims then. The CAD parts list in Milestone 2 settles the rest.

- **Glass.** The door unit ({{door_unit_l}} mm, {{final_door_kg}} kg: glass, kick strip with drop seal, hinges, pull) and the fixed panel ({{final_fixed_kg}} kg) ride flat on top of the long pallet in their timber frame, with nothing on them. On site, each is carried by two people with 2 suction lifters. The door lifts straight onto its hinge pins once a rated hinge set is named (HOLD, D-46, D-56). The fixed glass's profiles sit hidden in the decor and base, so the front stays frameless like v1.
- **Decor blocks and air parts (confirmed, D-59).** Each decor block is mounted empty. The right block's inner face is a removable, felt-covered panel that carries both grilles. With it off, the two cartridges, with their fans fitted, and the riser slide in from inside the pod, and the panel goes back on. They come out the same way for service, into the pod. Lifting them out through the top lid is rejected, because it would need about 4.5 m of room height. If a full-length cartridge ({{cart_size}} mm) proves awkward to handle inside the pod, about 2.3 m tall, it splits into two sections with a sealed slip joint. That is the only place the fans appear: the ceiling has no fan opening and no fan joint. Every lift stays at 20 kg or less; the right block with its air parts inside would weigh {{dr_plus_carts}} kg. The panel is inside only, so the look is untouched. How the cartridges and riser fit inside the {{decor_depth}} mm block is a CAD HOLD (D-56, ISS-078).
- **Ceiling (confirmed, D-24).** The fill still rides on the back of the ceiling cassette. With 40 mm frames, both ceiling parts are well under 20 kg either way.
- **Pallets.** The 48 x 40 carries the wall and ceiling panels, the wall cassettes, the floor panels and the short band pieces ({{final_std_kg}} kg, {{final_std_h}} mm). The long pallet carries the decor blocks, the long band pieces, the two cartridges and the riser, the kit, the ceiling cassettes that don't fit the upright stack, and the glass on top ({{final_long_kg}} kg, {{final_long_h}} mm). The pallet tables below list every part. Still 1 + 1.

Wall, ceiling, decor, air and glass parts of the decided build:

{{final_shell_table}}

{{final_pallets}}

Step by step, with the access check. A step fails the check if a part fitted earlier blocks its fixings; none does in this order. The check is at layout level and is repeated on the CAD in Milestone 2.

{{final_steps}}

<details><summary>Sensitivity: the same layout at 380 and 400 kg with an even added mass (before the final stack was known)</summary>

It adds an even mass to the walls (with or without the ceiling) until the pod reaches the target, with the frames deeper by 20 or 40 mm. Mass inside the plan's panels breaks the 20 kg limit (side panels {{q_side_in}} kg, ceiling halves {{q_ceil_in}} kg at 380 kg); on separate inner leaves every part stays at 20 kg or less up to the 400 kg cap.

{{table_quiet}}

</details>

## 6. Doorway check

Every part must pass a 914 x 2032 mm (36 x 80 in) doorway. A part is carried on edge, with its longest side along the corridor. It passes if its thickness plus {{hand_clear}} mm of hand room each side fits the width, and its middle dimension fits the height. It is also checked against {{door_clear_w}} mm, the minimum clear width of a door under the ADA. Failures: {{doorway_fails}}.

{{table_doorway}}

Corridor corners: the longest piece ({{longest_piece}} mm) must also turn corners carried flat. The longest thin part that turns a 90-degree corner is {{turn_1200}} mm between two 1200 mm corridors, and {{turn_914}} mm between a 1200 mm corridor and a 914 mm one, so every part passes.

## 7. Hooks for the voice cockpit kit (later)

Reserve now; don't design the kit (mic array, speakers, screen, status light).

- **Mounting points.** M6 rivnuts in the frame members, placed in the CAD at Milestone 2: a 100 x 100 mm pattern on the back wall centre for a screen at seated eye height; 4 points on a ceiling-half frame for a mic array and speaker plate; 2 behind the top decor block for a status light seen from outside. Each point gets a matching hole in the cassette in front of it.
- **Cable path.** One vertical cable channel with a pull cord in the back wall bay that holds the switches. It runs from the base band (power inlet) to the ceiling. It crosses the same 3 seams as the main harness, so the seam connectors get spare pins instead of new crossings; the bands option would have needed 6 crossings. The channel runs in the outer frame's cavity, behind the cassette; any cable in the cassette gap clips to the cassette only (D-26).
- **Power.** {{tool_power}}
- **Weight.** 4 kg is already held in the weight budget.

## 8. Open items and issues found

| ID | Item | State | Who |
| --- | --- | --- | --- |
| LS-01 | {{final_total}} kg here against the {{cap_kg}} kg cap ({{cap_note}}); the sound and air check gives {{hw_total}} kg for the same build (section 5.1). D-54, ISS-080: the cap stays; this estimate stays open until the wall sample weighs a real cassette with its clips, rails and bond lines per m2 and tests the {{fill_light}} kg/m3 fill next to the {{fill_final}} kg/m3; then the CAD parts list | open | Wall sample, PM, Milestone 2 |
| LS-02 | {{pitch_acp}} mm frame pitch and full-face bond keep the ACP flat without plywood; prove on the early wall sample | PLANNED | Prototype team |
| LS-03 | Tool-free cam or clip connector and captive bolt: real part numbers, loads and pull-out on the aluminium frame | open | Hardware group |
| LS-04 | Cassette clips: captive mechanical clips with a rated load, plus a safety catch on each ceiling cassette (D-47). Candidate Häfele KEKU EH; its rating basis, pull-out rating and fixing to the 0.5 mm tray are HOLD (D-56, ISS-076). Its real weight replaces the {{leaf_clip_kgm2}} kg/m2 allowance | HOLD | Hardware group |
| LS-05 | Door hinges and lock rated for the 4+4 laminate of toughened, heat-soaked panes (8.76 mm), 47.5 kg and 1176 mm, fitted in the factory, with the door lifting onto its pins | HOLD (D-46, D-56, ISS-002) | Hardware group |
| LS-06 | The plan uses code VT03 for both the PET felt and the 50 x 100 steel tube | issue | Control pack |
| LS-07 | v1 BOM 9 mm boards vs 15 mm in the drawings and STEP (already listed by the control pack) | issue | Control pack |
| LS-08 | Panasonic FV-15AUL1 weight not published on the pages read; 1.5 kg assumed | unverified | Hardware group |
| LS-09 | Tube wall thicknesses assumed (20 x 20 steel 1.2 mm, aluminium 1.5 mm); the plan gives none | assumption | Hardware group |
| LS-10 | Bolt counts use a {{pitch_count}} mm pitch only for counting; the joint register sets the real pitch from loads | assumption | Milestone 2 |
| LS-11 | Assembly times are assumptions until the timed prototype trial | PLANNED | Prototype team |
| LS-12 | Decor cladding colour: Dark Yellow ACP EV3038 (D-12); no weight effect | confirmed | Control pack |
| LS-13 | Room floor flatness must stay within the glides' adjustment range; check on site before install | assumption | Install guide |
| LS-15 | Removable, felt-covered inner panel of the right decor block, carrying both grilles: the cartridges and riser slide in after the block is mounted and come out into the pod for service; inside only. If a full-length cartridge is awkward to handle inside the 2.3 m pod, it splits in two with a sealed slip joint; the wall sample's handling check shows which | confirmed (D-59) | Decor CAD, wall sample |
| LS-16 | Cartridges and riser inside the {{decor_depth}} mm right block: CAD fit, and the fan sample (flow against pressure, octave sound power at 53 and 70 l/s, any tone at 125 to 250 Hz, and at boost the intake air within 0.5 K of the room, D-58). The fans' {{fan12_kg}} kg each is an assumption until weighed (D-56, ISS-077, ISS-078) | HOLD | Sound study, Milestone 2 |
| LS-14 | The upright stack on the 48 x 40 does not fill its depth: centre it and strap through the deck, or put the kit boxes beside it | note | Packaging |
| LS-17 | The control pack's PR #19 logged the rulings this study first cited by PR, as D-49 to D-59 (decor and wall depth, 12 V fans, weight, frame-to-frame back wall and ceiling, HOLD list, kick strip and linings, air openings, cartridge service); the numbers cited here match the merged log. This update also settles the layout study's part of ISS-079 (the 230-235 decor and the 1169 back and ceiling panels) | closed | Control pack |

## 9. How to reproduce

From this folder, with Python 3.10+ and openpyxl:

```
python3 scripts/run_all.py           # writes report.md, out/*.csv and out/*.svg
python3 scripts/run_all.py --check   # rebuilds in memory; fails if anything differs
python3 scripts/test_layout.py       # regression tests: overrides, decided-build counts and limits, sizes, air parts, status words
```

The STEP cross-check data (`data/v1_step_solids.csv`) comes from `scripts/step_crosscheck.py`, which reads the v1 STEP with cadquery-ocp in a separate virtualenv (see the script header). Unit note: 1 lb = {{kg_per_lb}} kg; imperial values are reference data for US freight only.

## 10. Inputs, status and sources

{{table_inputs}}

Sources:

{{table_sources}}
