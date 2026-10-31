<!-- report.md is generated from report_template.md by scripts/run_all.py. Edit the template or the scripts, never report.md. -->
# Spaceship layout study: weight, pallets and 2-person assembly

Status: DECIDED marks the PM's rulings of 2026-10-31. Under AGENTS.md the PM decides, and the Control Engineer records each decision in `v2/00-Control/decision-log.md`. Spaceship is the working name of v2 (folders keep their v2 names).

Every number below comes from the scripts in `scripts/`. `python3 scripts/run_all.py --check` proves that this report and the files in `out/` reproduce exactly. Section 10 lists the inputs, their status (confirmed, source, calculation, assumption, unverified) and their sources.

## Result

1. **Weight.** v1 weighs {{v1_bom}} kg by its BOM (range {{v1_lo}} to {{v1_hi}} kg). Spaceship as planned weighs {{plan_total}} kg, and the light build {{light_total}} kg ({{fast_total}} kg with the fast-assembly hardware). The decided build comes to **{{final_total}} kg**, {{cap_margin}} kg {{final_vs_cap}} the PM's {{cap_kg}} kg cap; the sound study expects {{hw_expect_lo}} to {{hw_expect_hi}} kg. That build has the sound study's final walls with the 0.5 mm inner tray, splitter silencers in the decor blocks with the thicker linings (+{{sil_extra}} kg), and a frameless 4+4 laminated front. The 0.4 mm tray would have saved {{tray_thin_saving}} kg but cost 1 dB, so it was dropped. Against the sound study's earlier total, this study also counts the TD-500 fans at {{fan_final_kg}} kg each (+{{gap_fans}} kg against the plan's 1.5 kg fans) and the clips and rails of the lining cassettes (+{{gap_clips}} kg). The win-backs are confirmed: 20 x 40 x 1.2 frames save {{winback_frames}} kg and 25 kg/m3 fill saves {{winback_fill}} kg.
2. **Parts.** Every part is 20 kg or less except the glass and, by {{sil_right_over}} kg, the right splitter silencer ({{sil_right}} kg). That figure assumes the extra lining splits between the two silencers in proportion to their mass. PROPOSED: its splitter baffles ship separately from the casing and slide in after it, which keeps every piece well under 20 kg. The glass door weighs {{final_door_kg}} kg and the fixed panel {{final_fixed_kg}} kg; two people carry each with 2 suction lifters ({{final_door_each}} kg each on the door). The right decor block ({{final_dr}} kg) and its silencer ship apart; together they would weigh {{dr_plus_sil}} kg. The top block ({{final_dt}} kg) and its silencer ({{sil_top}} kg) also ship apart. The decor's PET fill ({{decor_fill_kg}} kg) ships loose: inside the right decor block it would make that block {{dr_with_fill}} kg, too close to the limit for the assumptions behind it.
3. **Shipping (DECIDED).** One 48 x 40 pallet and one 96 x 48 pallet, {{final_gross}} kg gross, {{final_pcf}} lb/ft3. The 48 x 40 weighs {{final_std_kg}} kg and stands {{final_std_h}} mm high. The 96 x 48 weighs {{final_long_kg}} kg and stands {{final_long_h}} mm high, with both lites flat on top in their frame. Walls and ceiling are {{final_wall_t}} mm thick.
4. **Assembly (DECIDED changes).** Two people with one 5 mm hex key. The light build takes {{before_min}} min before the fast-assembly changes and {{after_min}} min after. The decided build takes **{{final_min}} min** ({{final_ph}} person-hours): {{final_bolts}} M6 bolts, {{final_cams}} tool-free clips and {{final_cassettes}} clip-on lining cassettes. The 1-hour target is not reached on these assumptions. Most of what remains is unpacking, levelling, setting the glass and door, and testing, so the timed prototype decides.
5. **Decisions.** Everything in the layout is DECIDED except shipping the right silencer's baffles separately (item 2).

## Decisions

| Decision | Status |
| --- | --- |
| Keep the plan's panel split: 2 frames per side wall (vách hông), 4 back wall frames (vách hậu), 2 ceiling halves (trần), 3 decor blocks (khung trang trí) | DECIDED |
| Ship on one 48 x 40 and one 96 x 48 pallet. Don't split the decor blocks: a seam across the faceted front breaks the look rule, and a third pallet costs more than it saves | DECIDED |
| Thin floor inside an aluminium base band (viền chân); the band drops to a 20 mm threshold across the door only. Castors are a possible later accessory, not part of v2 | DECIDED |
| Aluminium frames, with the section depth set by the sound study's wall: 20 x 40 in the walls and in the ceiling | DECIDED |
| No plywood behind the ACP; frame members at {{pitch_acp}} mm keep the ACP flat | DECIDED |
| Fast-assembly changes: factory subassemblies, captive bolts, tool-free clips on panel seams, felt pre-fitted (section 4) | DECIDED |
| Front: 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look). Door and fixed glass are carried by two people with suction lifters | DECIDED |
| Quiet build: the sound study's final stack with the 0.5 mm inner steel tray (0.4 mm cost 1 dB); splitter silencers with thicker linings inside the right and top decor blocks, shipped as separate parts and slid in through felt-covered access panels (inside only); {{cap_kg}} kg cap, 20 kg part limit and pallet layout kept | DECIDED |
| Decor block depth follows v1's real geometry, 230 to 235 mm, not the plan's 200 | DECIDED |
| The right splitter silencer ships with its baffles separate from the casing, so no piece is over 20 kg | PROPOSED |
| The inner skin and felt ship as separate clip-on inner leaves (the sound study's lining cassettes), one per panel, 19 kg or less, with the outside seams as planned | DECIDED |
| Ceiling fill carried on the back of the ceiling cassettes, so the ceiling panel stays at 20 kg or less (section 5) | DECIDED |
| Rejected: split decor blocks (B2), 5 bands per wall (C), full-height walls, castors in v2, no floor | DECIDED |

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

All options use only standard pallets. On a 48 x 40 in pallet (1219 x 1016 mm), panels stand upright with their length along the 48 in side, at most about 6 ft loaded. On a 96 x 48 in pallet (2438 x 1219 mm), long pieces and glass lie flat. Freight density is gross weight over the pallet footprint times the loaded height. The LTL class depends on the NMFC item and, for density-rated items, on density, so this report gives densities and does not guess a class. B1, B2 and C below use the light build with the DECIDED fast-assembly changes; section 5 repeats B1 with the final walls.

{{table_options}}

- **A, plan as written.** Fits 2 pallets only if the raised floor frame ships as knock-down bars; welded as in v1 (2500 x 1703 mm per the v1 BOM, {{v1_fl_kg}} kg), it fits no standard pallet. Heaviest option ({{A_total}} kg). The right decor block is over 20 kg, and the floor boards need screws and a driver.
- **B1, DECIDED.** Panels, short base band pieces, floor panels and the felt strips go on the 48 x 40 ({{B1_std_kg}} kg, {{B1_std_h}} mm high). The decor blocks, the long base band pieces, the kit boxes and the glass go on the 96 x 48 ({{B1_long_kg}} kg, {{B1_long_h}} mm high). Its longest piece is {{longest_piece}} mm ({{longest_in}} in), under the 96 in length where most LTL carriers start overlength charges. One long pallet is needed anyway: the glass is 2011 and 2139 mm long.
- **B2, rejected.** Cutting the decor blocks and standing the base band up puts everything except the glass on 48 x 40 pallets. But it needs two of them, and the glass still takes the long pallet alone: {{B2_npal}} pallets, {{B2_gross}} kg gross. The cut also puts seams across the faceted front.
- **C, rejected.** Five stacked bands per wall (like Orangebox Air3) give light {{band_min}} to {{band_max}} kg parts. But they add {{bolts_C_extra}} fixings, {{band_extra_seams}} extra visible seams per wall, {{conn_extra_C}} more cable connectors and more gasket to seal. With the plan's split, parts are already under 20 kg, so bands buy nothing.
- **Fewer, larger panels, rejected where the 20 kg limit bites.** A full-height side wall weighs {{full_wall_kg}} kg even without felt. A full-height back panel with felt pre-fitted weighs {{tallback_kg}} kg. Both are over 20 kg.

<details><summary>Option A: part list, joints, pallets, assembly</summary>

{{A_parts}}

{{A_joints}}

{{A_pallets}}

{{A_steps}}

</details>

<details><summary>Option B1 (DECIDED), light build: part list, joints, pallets</summary>

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

DECIDED: the thin floor. It is {{raised_vs_thin}} kg lighter than the raised steel floor, closes the box for sound, and cuts the step from {{raised_step}} mm to {{thin_step}} mm. The room inside gets {{height_gain}} mm taller. No floor saves a further {{none_vs_thin}} kg, but leaves the box open to the room floor, which the market study says leaks most. Castors would let an assembled pod roll around the office. They would cost about {{castor_vs_thin}} kg over the thin floor, a step of about {{castor_step}} mm with a ramp, a skirt to close the gap when parked, and a stiffer platform so the door stays in line while rolling. DECIDED: a possible later accessory, not part of v2.

## 4. Assembly by 2 people

Tool: {{tool}}. A small step stool is needed for the ceiling and the top fixings; it is not a tool. Every bolt and clip is reached from inside the pod, through open frame bays or behind the loose felt strip over each joint. The strips, or in the decided build the lining cassettes, go on last.

Before and after the DECIDED fast-assembly changes, on the light build. Each row adds one change to the rows above it, with the same time model:

{{table_levers}}

The full-height back wall panel (fewer, larger panels) was also tried. With the felt pre-fitted it weighs {{tallback_kg}} kg, over the limit, so it is not used.

What remains is mostly work that does not shrink with fewer parts: unpacking, levelling, setting the glass and the door, and testing the electrics. The 1-hour target needs that work timed on the prototype, and possibly more done in the factory. Section 5 gives the step-by-step sequence and access check for the decided build.

Benchmark: Room S needs 4 people for 3 to 5 hours (12 to 20 person-hours), and hushMeet 2 installers for 2.5 to 3 hours (market study). The decided build takes {{final_ph}} person-hours.

## 5. The decided build: final wall stack (re-check)

The sound study's final stack (DECIDED): ACP 3 mm on a 20 x 40 aluminium frame at {{pitch_acp}} mm with 40 mm PET fill, then a floating lining cassette: a 0.5 mm steel tray, 25 mm deep, with 9 mm felt across its face. That makes {{final_wall_t}} mm and {{final_kgm2_hw}} kg/m2 in the sound study. The ceiling now uses the same 20 x 40 frame (was 20 x 100). Frames are 20 x 40 x 1.2 mm and the fill is 25 kg/m3 (win-backs). The silencers are splitter silencers with 2 mm aluminium casings inside the right and top decor blocks, next to the TD-500 fans. The front is frameless 4+4 laminated glass. The sound study expects {{hw_expect_lo}} to {{hw_expect_hi}} kg after its thicker splitter linings.

This study builds it on the B1 layout. The outer panel (ACP, frame and fill) and its cassette are separate parts; the cassette is the DECIDED clip-on inner leaf. The outside size stays the same; the inside narrows to {{inner_w_final}} mm. The wall here comes to {{final_wall_kgm2}} kg/m2 with clips and tray returns (the sound study: {{final_kgm2_hw}}). The fans and silencers are the sound study's: two TD-500 inline fans at {{fan_final_kg}} kg and splitter silencers of {{sil_right}} kg (right block) and {{sil_top}} kg (top block), including the thicker linings. The decor blocks are {{decor_depth}} mm deep, as in v1. Their weights already came from v1's real shapes in the STEP, so only the packing changes. Its door edge seals, base seal and cable grommets are counted too.

Result: **{{final_total}} kg**, {{final_over20}} parts over 20 kg except the glass, heaviest {{final_heaviest}}, {{final_npal}} pallets, {{final_gross}} kg gross, {{final_maxh}} mm at most, assembly {{final_min}} min.

- **Glass.** Door {{final_door_kg}} kg and fixed panel {{final_fixed_kg}} kg in 4+4 laminated. They ride flat on top of the long pallet in their timber frame, with nothing on them. On site, each is carried by two people with 2 suction lifters. The door's hinges and pull are fitted in the factory, so it lifts straight onto its hinge pins. The fixed glass's profiles sit hidden in the decor and base, so the front stays frameless like v1.
- **Decor blocks and silencers (DECIDED).** Each decor block is mounted empty. Then its splitter silencer slides in from inside the pod through a felt-covered access panel in the right and top blocks, and the fan connects to it. Every lift stays at 20 kg or less, and the same panel gives fan service access later. The right block with its silencer inside would weigh {{dr_plus_sil}} kg. The panels are inside only, so the look is untouched.
- **Decor fill.** The sound study fills the decor blocks with PET ({{decor_fill_kg}} kg). Inside the right decor block it would make that block {{dr_with_fill}} kg, too close to the limit for the assumptions behind it, so the fill ships loose in the kit and is pushed into each block's open back just before it is mounted.
- **Ceiling (DECIDED).** The fill still rides on the back of the ceiling cassette. With 40 mm frames, both ceiling parts are well under 20 kg either way.
- **Pallets.** The 48 x 40 carries the wall and ceiling panels, the wall cassettes, the floor panels and the short band pieces ({{final_std_kg}} kg, {{final_std_h}} mm). The long pallet carries the decor blocks, the long band pieces, the kit, the ceiling cassettes that don't fit the upright stack, and the glass on top ({{final_long_kg}} kg, {{final_long_h}} mm). The two silencers go wherever the packer finds room; the pallet tables below list them. Still 1 + 1.

Wall, ceiling, decor, silencer and glass parts of the decided build:

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
- **Cable path.** One vertical cable channel with a pull cord in the back wall bay that holds the switches. It runs from the base band (power inlet) to the ceiling. It crosses the same 3 seams as the main harness, so the seam connectors get spare pins instead of new crossings; the bands option would have needed 6 crossings. The channel runs in the outer frame's cavity, behind the cassette.
- **Power.** {{tool_power}}
- **Weight.** 4 kg is already held in the weight budget.

## 8. Open items and issues found

| ID | Item | Status | Who |
| --- | --- | --- | --- |
| LS-01 | {{final_total}} kg here against a {{cap_kg}} kg cap ({{hw_expect_lo}} to {{hw_expect_hi}} kg expected by the sound study); settle from the CAD parts list | open | Milestone 2 |
| LS-02 | {{pitch_acp}} mm frame pitch and full-face bond keep the ACP flat without plywood; prove on the early wall sample | PLANNED | Prototype team |
| LS-03 | Tool-free cam or clip connector and captive bolt: real part numbers, loads and pull-out on the aluminium frame | open | Hardware group |
| LS-04 | Cassette clips: part numbers, and how the cassette floats (no stud bridge) while it carries a 19 kg leaf | open | Hardware group |
| LS-05 | Hinges for a frameless 4+4 laminated door of about 43 kg, fitted in the factory, with the door lifting onto its pins | open | Hardware group |
| LS-06 | The plan uses code VT03 for both the PET felt and the 50 x 100 steel tube | issue | Control pack |
| LS-07 | v1 BOM 9 mm boards vs 15 mm in the drawings and STEP (already listed by the control pack) | issue | Control pack |
| LS-08 | Panasonic FV-15AUL1 weight not published on the pages read; 1.5 kg assumed | unverified | Hardware group |
| LS-09 | Tube wall thicknesses assumed (20 x 20 steel 1.2 mm, aluminium 1.5 mm); the plan gives none | assumption | Hardware group |
| LS-10 | Bolt counts use a {{pitch_count}} mm pitch only for counting; the joint register sets the real pitch from loads | assumption | Milestone 2 |
| LS-11 | Assembly times are assumptions until the timed prototype trial | PLANNED | Prototype team |
| LS-12 | Decor cladding colour (yellow in the materials list, black in the plan's pictures); no weight effect | issue | Control pack |
| LS-13 | Room floor flatness must stay within the glides' adjustment range; check on site before install | assumption | Install guide |
| LS-15 | Felt-covered access panel on the pod side of the right and top decor blocks: silencers slide in after the blocks are mounted, and it gives fan service access; inside only | DECIDED | Decor CAD |
| LS-16 | Right splitter silencer at {{sil_right}} kg: ship its baffles separately from the casing, or confirm how the thicker lining splits between the two silencers | PROPOSED | PM, sound study |
| LS-14 | The upright stack on the 48 x 40 does not fill its depth: centre it and strap through the deck, or put the kit boxes beside it | note | Packaging |

## 9. How to reproduce

From this folder, with Python 3.10+ and openpyxl:

```
python3 scripts/run_all.py           # writes report.md, out/*.csv and out/*.svg
python3 scripts/run_all.py --check   # rebuilds in memory; fails if anything differs
```

The STEP cross-check data (`data/v1_step_solids.csv`) comes from `scripts/step_crosscheck.py`, which reads the v1 STEP with cadquery-ocp in a separate virtualenv (see the script header). Unit note: 1 lb = {{kg_per_lb}} kg; imperial values are reference data for US freight only.

## 10. Inputs, status and sources

{{table_inputs}}

Sources:

{{table_sources}}
