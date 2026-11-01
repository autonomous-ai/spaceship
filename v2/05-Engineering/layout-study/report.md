<!-- report.md is generated from report_template.md by scripts/run_all.py. Edit the template or the scripts, never report.md. -->
# Spaceship layout study: weight, pallets and 2-person assembly

Status words: every number carries one of confirmed, source, calculation, assumption or unverified (guideline section 10). A value the PM decided is confirmed and cites its decision, D-xx in `v2/00-Control/decision-log.md`. Under AGENTS.md the PM decides and the log records it. HOLD marks a part or interface that a supplier or a sample must confirm first. Spaceship is the working name of v2 (folders keep their v2 names).

Every number below comes from the scripts in `scripts/`. `python3 scripts/run_all.py --check` proves that this report and the files in `out/` reproduce exactly. Section 10 lists the inputs, their status and their sources.

## Result

1. **Weight.** v1 weighs 480 kg by its BOM (range 459 to 574 kg). Spaceship as planned weighs 440 kg, and the light build 296 kg (297 kg with the fast-assembly hardware). The decided build comes to **426.7 kg** against the PM's 420 kg cap (**6.7 kg over**, open item LS-01, ISS-080). The sound and air check (PR #11) puts the same build at 417.5 kg in its own model, about 418. The 9.2 kg between the two is almost all in the walls and ceiling: this study carries the lining cassettes' clips and rails (9.0 kg) and the bond lines (3.9 kg), and that check leaves both out; without them this study's walls and ceiling are 3.7 kg lighter than the check's. Both are assumptions. By D-54 the cap stays at 420 kg and 426.7 kg is the current estimate, open against it; two wall-sample tests settle it: weigh a real cassette with its clips, rails and bond lines per m2, and test the 25 kg/m3 fill next to the 32 kg/m3 (section 5.1).
   - In the build: the sound study's final walls and ceiling with the 0.5 mm tray (the 0.4 mm tray would have saved 12.7 kg but cost 1 dB, D-37); 20 x 40 x 1.2 frames (save 7.5 kg against 1.5 mm, D-34); fill at 32 kg/m3 (25 kg/m3 would save 4.3 kg, but that grade has no published absorption, so the wall sample tests it first, D-54); back wall and ceiling frames that span frame to frame, 1,207 mm per half with 1,169 mm linings; four 12 V fans in two cartridges with the exhaust riser, all in the right decor block; and a frameless 4+4 laminated front.
2. **Parts.** Every part is 20 kg or less except the glass. The door ships as one unit 2,096 mm long and 47.5 kg: 4+4 laminated glass (2,011 mm), a kick strip 85 mm tall holding the drop seal, and the hinges and pull fitted in the factory. Its hinges and lock are on HOLD until a set rated for this glass, 47.5 kg and 1176 mm is named (D-46, D-56). Two people carry it with 2 suction lifters (23.7 kg each). The fixed panel weighs 28.0 kg. Each splitter cartridge weighs 17.7 kg with its 2 fans fitted, and the riser 9.6 kg. They slide into the mounted right decor block (18.1 kg) from inside, through its removable inner panel (D-59), so no lift carries the block and its air parts together (63.1 kg).
3. **Shipping (confirmed, D-04).** One 48 x 40 pallet and one 96 x 48 pallet, 526 kg gross, 6.7 lb/ft3. The 48 x 40 weighs 244 kg and stands 1,641 mm high. The 96 x 48 weighs 281 kg and stands 971 mm high, with both lites flat on top in their frame. Walls and ceiling are 81 mm thick.
4. **Assembly (confirmed changes, D-08).** Two people with one 5 mm hex key. The light build takes 166 min before the fast-assembly changes and 104 min after. The decided build takes **126 min** (4.2 person-hours): 78 M6 bolts, 38 tool-free clips and 10 clip-on lining cassettes. The 1-hour target is not reached on these assumptions. Most of what remains is unpacking, levelling, setting the glass and door, and testing, so the timed prototype decides.
5. **Decisions.** Every layout choice is confirmed by a decision; the table below cites it.
6. **The live weight count on skeleton P04** ([weight-rollup.md](weight-rollup.md), ISS-081, F-010): **409.7 kg as shipped, 10.3 kg under the 420 kg cap and 0.3 kg under the PM's 410 kg target.** It takes the adopted savings of D-81 and D-85 (28.1 kg in all; the 24 kg/m3 fill, the 1.5 mm base band and the poplar-core floor are provisional on T02 and BASE's checks), budgets and allowances for the light shelf, the work-wall ledge and the named clips, tonight's CAD masses (CEILING PR #32, FRONT PRs #27, #28 and #105, WALL's L1), D-60's air parts and the P04 sizes. The voice kit's 4.0 kg reserve rides outside the cap (D-11, D-81). Its part list is `out/parts-decided-P04.csv`. The sections below still describe the P03 build.

## Decisions

Decided specs, each citing the decision log (`v2/00-Control/decision-log.md`, D-01 to D-59).

| Decision | Status | Log |
| --- | --- | --- |
| Keep the plan's panel split: 2 frames per side wall (vách hông), 4 back wall frames (vách hậu), 2 ceiling halves (trần), 3 decor blocks (khung trang trí) | confirmed | D-23 |
| Every part 20 kg or less except the glass | confirmed | D-03 |
| Ship on one 48 x 40 and one 96 x 48 pallet. Don't split the decor blocks: a seam across the faceted front breaks the look rule, and a third pallet costs more than it saves | confirmed | D-04 |
| Thin floor inside an aluminium base band (viền chân); the band drops to a 20 mm threshold across the door only. Castors are a possible later accessory, not part of v2 | confirmed | D-05, D-18 |
| Aluminium frames, 20 x 40 x 1.2 mm at 400 mm, in the walls and in the ceiling; walls and ceiling on the same 81 mm stack | confirmed | D-16, D-34, D-42 |
| Back wall (vách hậu) and ceiling (trần) frames span frame to frame between the side frames: 1,207 mm per half, with their lining cassettes at 1,169 mm | confirmed | D-55 |
| Side walls (vách hông) 1,495 mm deep, starting at the decor back plate as in v1. Side lining cassettes 1,448 mm long to close the inside corner; the upper ones 1,098 mm tall, stopping 4 mm under the roof frame so they float | confirmed | D-49, D-57 |
| No plywood behind the ACP; the sound mass sits in the floating lining cassette with a 0.5 mm steel tray (0.4 mm cost 1 dB) | confirmed | D-17, D-37 |
| Cavity fill (bông PET) at 32 kg/m3: the lighter grade has no published absorption, so D-34's 25 kg/m3 doesn't apply yet. The wall sample tests it next to the 32 kg/m3, and the build switches if it matches on sound | confirmed | D-54 |
| Fast-assembly changes: factory subassemblies, captive bolts, tool-free clips on panel seams, felt pre-fitted (section 4) | confirmed | D-08 |
| Front: 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look). The door is left-hinged; it carries an aluminium kick strip 85 mm tall in the base band's dark finish, holding the drop seal, so the door unit is 2,096 mm long. Door and fixed glass are carried by two people with suction lifters. Door hinges and lock on HOLD until a rated set is named | confirmed | D-19, D-27, D-40, D-46, D-56, D-57 |
| Weight: cap 420 kg with the 0.5 mm tray. This study's 426.7 kg is the current estimate, open against it until the wall sample is weighed; the PM rules on trims if the sample still lands over | confirmed | D-37, D-54 |
| Air (thông gió): four 12 V fans (quạt thông gió), two per path, in the lined fan boxes of two splitter cartridges (ống tiêu âm) side by side in the right decor block, supply grille low and exhaust grille high on its inner face. The room-side intake sits low on the block (its underside or the bottom of its outer face) and the exhaust leaves through the top slot, at least 1 m apart; a 150 mm riser carries the exhaust up to the slot. The block's inner face is a removable, felt-covered panel carrying both grilles; the cartridges and riser slide in and out through it, into the pod, for fitting and service (inside only). Lifting them out through the top lid is rejected: it would need about 4.5 m of room height. If a full-length cartridge proves awkward inside the 2.3 m pod, it splits into two sections with a sealed slip joint. Fan sample and the riser's CAD fit on HOLD | confirmed | D-29, D-51, D-52, D-56, D-58, D-59 |
| Lining cassettes ship as separate clip-on inner leaves, one per panel, with the outside seams as planned; captive mechanical clips with a rated load, plus a safety catch on the ceiling ones; the clip and catch on HOLD | confirmed | D-17, D-23, D-47, D-56 |
| Ceiling fill carried on the back of the ceiling cassettes | confirmed | D-24 |
| Decor block (khối trang trí) depth 205 mm, as v1 (measured from its drawings and STEP); not D-39's 230 to 235, nor the plan's 200 | confirmed | D-49 (replaces D-39) |
| Decor cladding in Dark Yellow ACP EV3038 (no weight effect) | confirmed | D-12 |
| Rejected: split decor blocks (B2), 5 bands per wall (C), full-height walls, castors in v2, no floor | confirmed | D-04, D-05, D-18, D-23 |

## 1. Weight

### 1.1 v1 baseline (short)

The v1 BOM (2026-10-29) is the main source; the older STEP (2026-10-14) is a cross-check only. The range comes from wood densities and from the board conflict already on the issue list: the BOM lists 9 mm inner and floor boards, the drawings and the STEP show 15 mm ply. "Tấm nhôm" skins are taken as ACP (the decor skins are routed and folded, which is how ACP is worked). If they were solid aluminium sheet, v1 would gain 79 kg.

| Assembly | Low: BOM, light densities | BOM as written | High: 15 mm boards (drawings, STEP), heavy densities |
| --- | ---: | ---: | ---: |
| BASE | 73 | 74 | 90 |
| WALL | 108 | 116 | 123 |
| FRONT | 151 | 151 | 151 |
| CEILING | 32 | 34 | 37 |
| LINING | 78 | 86 | 155 |
| AIR | 4 | 4 | 4 |
| ELECTRICAL | 2 | 2 | 2 |
| INTERIOR | 11 | 12 | 13 |
| **Total** | **459** | **480** | **574** |

STEP cross-check (same densities). The STEP agrees with the BOM on every big item except board thickness, where it matches the drawings. Glass is lighter in the STEP because the BOM gives the rectangles to cut from, and the STEP gives the finished shape:

| Item | BOM quantity | STEP quantity | kg (BOM, 9 mm boards) | kg (STEP, 15 mm boards) |
| --- | ---: | ---: | ---: | ---: |
| Inner lining and floor boards | 18.60 m2 | 17.19 m2 | 100 | 155 |
| 12 mm back-centre lining | 0.00 m2 | 1.33 m2 | 0 | 10 |
| 6 mm boards behind the skins | 16.26 m2 | 16.10 m2 | 59 | 58 |
| 2 mm ACP skins | 17.60 m2 | 17.42 m2 | 51 | 51 |
| 10 mm glass | 3.91 m2 | 3.42 m2 | 98 | 86 |
| 40x40 timber frame | 0.079 m3 | 0.074 m3 | 44 | 41 |
| Steel floor-frame tube | 0.007 m3 | 0.007 m3 | 53 | 56 |

8 of v1's shipping pieces weigh over 20 kg, not counting the glass: FL 55 kg, LW 47 kg, RW 47 kg, BWL 31 kg, BWC 26 kg, BWR 31 kg, CL 53 kg, DR 27 kg.

### 1.2 Spaceship as planned and the light build

"As planned" follows the build plan: 3 mm ACP glued to 6 mm plywood on 20 x 20 steel tube (1.2 mm wall, assumed), 9 mm PET felt, the raised 50 x 100 steel floor with 30 x 60 joists and 6 feet, a decor core of 20 x 20 steel, 10 mm glass as v1, and the table. The light build is the cumulative result of the steps below. Section 5 adds the sound study's final walls on top of it.

| Assembly | v2 as planned, kg | Light indoor build, kg | Change, kg |
| --- | ---: | ---: | ---: |
| BASE | 82.3 | 46.6 | -35.7 |
| WALL | 133.1 | 76.8 | -56.3 |
| FRONT | 140.1 | 109.3 | -30.8 |
| CEILING | 37.7 | 21.2 | -16.6 |
| LINING | 29.0 | 29.0 | 0.0 |
| AIR | 3.0 | 6.0 | 3.0 |
| ELECTRICAL | 3.0 | 7.1 | 4.1 |
| INTERIOR | 12.0 | 0.0 | -12.0 |
| **Total** | **440.2** | **295.9** | **-144.3** |

How the light build gets there, one change at a time:

| Step | Status | Change, kg | Running total, kg |
| --- | --- | ---: | ---: |
| v2 as planned (steel frames, 6 mm plywood, raised steel floor, 10 mm glass, table) | source + calculation |  | 440.2 |
| Remove the table; the pod ships empty | confirmed (D-06) | -12.0 | 428.2 |
| Thin floor inside an aluminium base band instead of the raised steel frame | confirmed (D-05, D-18) | -36.0 | 392.3 |
| Aluminium 20x20 frames instead of steel (walls, ceiling, decor) | confirmed (D-16) | -47.0 | 345.3 |
| No plywood behind the ACP; frame members at 400 mm to keep the ACP flat | confirmed (D-17) | -53.9 | 291.4 |
| 8 mm tempered glass instead of 10 mm | light build only; the decided build uses 4+4 laminated glass (D-27) | -17.1 | 274.2 |
| Add gaskets on every panel joint, sealed glazing profiles, door drop seal | plan requirement | 5.0 | 279.3 |
| Add 2 silenced vents and an occupancy sensor for automatic fans | plan requirement | 3.1 | 282.4 |
| Add light cavity fill (20 mm PET) in wall and ceiling bays | assumption (sound group sizes it) | 9.6 | 291.9 |
| Hold 4 kg for the later voice cockpit kit | confirmed (D-11) | 4.0 | 295.9 |

Notes:
- Glass weights use the finished shapes from the STEP: door 2.08 m2, fixed panel 1.34 m2. Decor skins use the STEP's finished areas too (6.30 m2, against 7.67 m2 of cutting rectangles in the BOM).
- The ACP is Alcorest EV3038, 3 mm with 0.21 mm skins (the plan's VT01). The maker gives skins, not kg/m2; 3.5 kg/m2 is the sound study's calculation, used here by the PM's ruling. Every 0.1 kg/m2 of ACP changes the pod by 2.2 kg.
- The colour of the decor cladding (yellow ACP in the plan's materials, black in the plan's pictures) is on the issue list. It does not change any weight.

### 1.3 Variants

One change at a time against the light build:

| Variant (one change to the light build) | Change, kg | Total, kg | Note |
| --- | ---: | ---: | --- |
| Front: smoked acrylic 8 mm (door and fixed panel) | -35.9 | 260.0 | Room uses an acrylic booth door; scratches more, needs a stiffer door frame or hinges rated for acrylic; sound check decides. |
| Front: smoked acrylic 10 mm | -27.7 | 268.2 | Stiffer door; same notes. |
| Front: 4+4 laminated acoustic glass | +2.8 | 298.7 | About the weight of 8 mm, quieter (sound group). |
| Front: 10 mm tempered glass (as v1) | +17.1 | 313.0 | Reference. |
| Walls and ceiling: foam-core sandwich (same ACP face, 25 mm foam, 0.5 mm aluminium inner skin) | +29.5 | 325.4 | Stiff and flat without studs; factory-bonded; fire behaviour of the core to check for the later US rules. |
| Walls and ceiling: aluminium honeycomb sandwich (same ACP face on a 10 mm honeycomb panel) | +47.8 | 343.7 | Heaviest of the light options here because the ACP face sits on a full honeycomb panel. |
| No floor at all (base band only) | -32.8 | 263.1 | Weakest for sound (open to the room floor). |
| Raised steel floor kept (plan) | +36.0 | 331.9 | Reference. |

The smoked acrylic front is the biggest single lever, but the decided build uses 4+4 laminated glass: acrylic needed an opaque band down the door, which breaks the look. The sandwich walls are heavier than the frame build here, because the frame build without plywood is already 5.9 kg/m2. Sandwich walls buy flatness and a second skin, not weight.

### 1.4 Every part against 20 kg

Light build: no part is over 20 kg except the glass (door 41.6 kg, fixed panel 26.9 kg at 8 mm). Over 20 kg in the light build: none. Over 20 kg as planned: F-DR 26.5 kg. With the felt pre-fitted, the light build's wall and ceiling panels weigh 10 to 13 kg. For the decided build see section 5.

<details><summary>Part list with weights, light build</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,495 x 1,145 x 38 | 2 | 10.1 | 20.1 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,495 x 1,145 x 38 | 2 | 10.1 | 20.1 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 8.4 | 16.7 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 8.4 | 16.7 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,495 x 1,212 x 38 | 2 | 10.6 | 21.2 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,457 x 1,145 x 9 | 4 | 3.1 | 12.3 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,457 x 1,212 x 9 | 2 | 3.3 | 6.5 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,457 x 1,212 x 15 | 2 | 16.4 | 32.8 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 205 | 1 | 10.0 | 10.0 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 205 | 1 | 18.1 | 18.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 205 | 1 | 7.0 | 7.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 3.2 | 3.2 |  | calculation |
|  | **Total** |  |  | 54 |  | **295.9** |  |  |

</details>

<details><summary>Part list with weights, as planned (option A)</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,495 x 1,145 x 38 | 2 | 17.9 | 35.9 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,495 x 1,145 x 38 | 2 | 17.9 | 35.9 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 14.9 | 29.9 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 14.9 | 29.9 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,495 x 1,212 x 38 | 2 | 18.9 | 37.7 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,457 x 1,145 x 9 | 4 | 3.1 | 12.3 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,457 x 1,212 x 9 | 2 | 3.3 | 6.5 |  | calculation |
| B-RAIL-FL-01 | BASE - FRAME RAIL 50x100 - L2400 / Khung sàn - thép hộp 50x100 | BASE | 2,400 x 100 x 50 | 1 | 11.0 | 11.0 |  | calculation |
| B-RAIL-FL-02 | BASE - FRAME RAIL 50x100 - L2020 / Khung sàn - thép hộp 50x100 | BASE | 2,020 x 100 x 50 | 1 | 9.3 | 9.3 |  | calculation |
| B-RAIL-FL-03 | BASE - FRAME RAIL 50x100 - L1370 / Khung sàn - thép hộp 50x100 | BASE | 1,370 x 100 x 50 | 2 | 6.3 | 12.6 |  | calculation |
| B-RAIL-FL-04 | BASE - FRAME RAIL 50x100 - L269 / Khung sàn - thép hộp 50x100 | BASE | 269 x 100 x 50 | 1 | 1.2 | 1.2 |  | calculation |
| B-RAIL-FL-05 | BASE - FRAME RAIL 50x100 - L212 / Khung sàn - thép hộp 50x100 | BASE | 212 x 100 x 50 | 1 | 1.0 | 1.0 |  | calculation |
| B-RAIL-FL-06 | BASE - FRAME RAIL 50x100 - L150 / Khung sàn - thép hộp 50x100 | BASE | 150 x 100 x 50 | 2 | 0.7 | 1.4 |  | calculation |
| B-RAIL-FL-07 | BASE - FRAME RAIL 50x100 - L123.5 / Khung sàn - thép hộp 50x100 | BASE | 124 x 100 x 50 | 1 | 0.6 | 0.6 |  | calculation |
| B-RAIL-FL-08 | BASE - FRAME RAIL 50x100 - L76 / Khung sàn - thép hộp 50x100 | BASE | 100 x 76 x 50 | 4 | 0.3 | 1.4 |  | calculation |
| B-JOIST | BASE - JOIST 30x60 - L2400 / Nan đỡ ván sàn - thép hộp 30x60 | BASE | 2,400 x 60 x 30 | 2 | 4.6 | 9.2 |  | calculation |
| B-FOOT | BASE - LEVELLING FOOT M10 / Chân tăng đưa M10 | BASE | 80 x 60 x 60 | 6 | 0.2 | 1.5 |  | assumption |
| B-BRACKET | BASE - CORNER BRACKET / Pát góc khung sàn | BASE | 150 x 100 x 60 | 4 | 0.3 | 1.4 |  | assumption |
| B-BOARD | BASE - FLOOR BOARD / Ván sàn | BASE | 1,428 x 1,184 x 15 | 2 | 15.2 | 30.4 |  | calculation |
| B-THRESH | BASE - FRONT EDGE TRIM / Ốp mép sàn trước | BASE | 1,917 x 204 x 3 | 1 | 1.4 | 1.4 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 205 | 1 | 14.7 | 14.7 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 205 | 1 | 26.5 | 26.5 | OVER 20 kg | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 205 | 1 | 10.7 | 10.7 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (10 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 10 | 1 | 52.0 | 52.0 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (10 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 10 | 1 | 33.6 | 33.6 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 2.6 | 2.6 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.0 | 3.0 |  | assumption |
| I-TABLE | INTERIOR - TABLE (v1), FLAT-PACKED / Bàn | INTERIOR | 1,000 x 600 x 120 | 1 | 12.0 | 12.0 |  | calculation |
| K-FIX | KIT - M6 BOLTS, RIVNUTS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 1.6 | 1.6 |  | calculation |
|  | **Total** |  |  | 59 |  | **440.2** |  |  |

</details>

## 2. Panel split options

All options use only standard pallets. On a 48 x 40 in pallet (1219 x 1016 mm), panels stand upright with their length along the 48 in side, at most about 6 ft loaded. On a 96 x 48 in pallet (2438 x 1219 mm), long pieces and glass lie flat. Freight density is gross weight over the pallet footprint times the loaded height. The LTL class depends on the NMFC item and, for density-rated items, on density, so this report gives densities and does not guess a class. B1, B2 and C below use the light build with the confirmed fast-assembly changes (D-08); section 5 repeats B1 with the final walls.

| Option | What it is | Pod kg | Parts | M6 bolts + clips | Cable connectors | Pallets 48x40 + 96x48 | Shipped kg (gross) | Max loaded height mm | Density lb/ft3 | Assembly, min (2 people) | Person-hours |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | Plan as written | 440 | 59 | 134 + 0 | 3 | 1 + 1 | 543 | 1,641 | 7.7 | 191 | 6.4 |
| **B1** | Plan split, light build, fast assembly, 2 pallets (confirmed, D-04) | 297 | 45 | 76 + 38 | 3 | 1 + 1 | 396 | 1,641 | 6.4 | 104 | 3.5 |
| **B2** | As B1, decor and base band split to fit 48x40 (rejected) | 300 | 49 | 92 + 38 | 3 | 2 + 1 | 425 | 1,806 | 4.9 | 113 | 3.8 |
| **C** | Horizontal bands, light build, fast assembly (rejected) | 311 | 57 | 76 + 98 | 6 | 1 + 1 | 410 | 1,641 | 4.7 | 124 | 4.1 |

- **A, plan as written.** Fits 2 pallets only if the raised floor frame ships as knock-down bars; welded as in v1 (2500 x 1703 mm per the v1 BOM, 55 kg), it fits no standard pallet. Heaviest option (440 kg). The right decor block is over 20 kg, and the floor boards need screws and a driver.
- **B1, confirmed (D-04).** Panels, short base band pieces, floor panels and the felt strips go on the 48 x 40 (179 kg, 1,641 mm high). The decor blocks, the long base band pieces, the kit boxes and the glass go on the 96 x 48 (217 kg, 618 mm high). Its longest piece is 2,420 mm (95.3 in), under the 96 in length where most LTL carriers start overlength charges. One long pallet is needed anyway: the glass is 2011 and 2139 mm long.
- **B2, rejected.** Cutting the decor blocks and standing the base band up puts everything except the glass on 48 x 40 pallets. But it needs two of them, and the glass still takes the long pallet alone: 3 pallets, 425 kg gross. The cut also puts seams across the faceted front.
- **C, rejected.** Five stacked bands per wall (like Orangebox Air3) give light 4 to 5 kg parts. But they add 60 fixings, 3 extra visible seams per wall, 3 more cable connectors and more gasket to seal. With the plan's split, parts are already under 20 kg, so bands buy nothing.
- **Fewer, larger panels, rejected where the 20 kg limit bites.** A full-height side wall weighs 19 kg even without felt. A full-height back panel with felt pre-fitted weighs 19.9 kg. Both are over 20 kg.

<details><summary>Option A: part list, joints, pallets, assembly</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,495 x 1,145 x 38 | 2 | 17.9 | 35.9 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,495 x 1,145 x 38 | 2 | 17.9 | 35.9 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 14.9 | 29.9 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 14.9 | 29.9 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,495 x 1,212 x 38 | 2 | 18.9 | 37.7 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,457 x 1,145 x 9 | 4 | 3.1 | 12.3 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,457 x 1,212 x 9 | 2 | 3.3 | 6.5 |  | calculation |
| B-RAIL-FL-01 | BASE - FRAME RAIL 50x100 - L2400 / Khung sàn - thép hộp 50x100 | BASE | 2,400 x 100 x 50 | 1 | 11.0 | 11.0 |  | calculation |
| B-RAIL-FL-02 | BASE - FRAME RAIL 50x100 - L2020 / Khung sàn - thép hộp 50x100 | BASE | 2,020 x 100 x 50 | 1 | 9.3 | 9.3 |  | calculation |
| B-RAIL-FL-03 | BASE - FRAME RAIL 50x100 - L1370 / Khung sàn - thép hộp 50x100 | BASE | 1,370 x 100 x 50 | 2 | 6.3 | 12.6 |  | calculation |
| B-RAIL-FL-04 | BASE - FRAME RAIL 50x100 - L269 / Khung sàn - thép hộp 50x100 | BASE | 269 x 100 x 50 | 1 | 1.2 | 1.2 |  | calculation |
| B-RAIL-FL-05 | BASE - FRAME RAIL 50x100 - L212 / Khung sàn - thép hộp 50x100 | BASE | 212 x 100 x 50 | 1 | 1.0 | 1.0 |  | calculation |
| B-RAIL-FL-06 | BASE - FRAME RAIL 50x100 - L150 / Khung sàn - thép hộp 50x100 | BASE | 150 x 100 x 50 | 2 | 0.7 | 1.4 |  | calculation |
| B-RAIL-FL-07 | BASE - FRAME RAIL 50x100 - L123.5 / Khung sàn - thép hộp 50x100 | BASE | 124 x 100 x 50 | 1 | 0.6 | 0.6 |  | calculation |
| B-RAIL-FL-08 | BASE - FRAME RAIL 50x100 - L76 / Khung sàn - thép hộp 50x100 | BASE | 100 x 76 x 50 | 4 | 0.3 | 1.4 |  | calculation |
| B-JOIST | BASE - JOIST 30x60 - L2400 / Nan đỡ ván sàn - thép hộp 30x60 | BASE | 2,400 x 60 x 30 | 2 | 4.6 | 9.2 |  | calculation |
| B-FOOT | BASE - LEVELLING FOOT M10 / Chân tăng đưa M10 | BASE | 80 x 60 x 60 | 6 | 0.2 | 1.5 |  | assumption |
| B-BRACKET | BASE - CORNER BRACKET / Pát góc khung sàn | BASE | 150 x 100 x 60 | 4 | 0.3 | 1.4 |  | assumption |
| B-BOARD | BASE - FLOOR BOARD / Ván sàn | BASE | 1,428 x 1,184 x 15 | 2 | 15.2 | 30.4 |  | calculation |
| B-THRESH | BASE - FRONT EDGE TRIM / Ốp mép sàn trước | BASE | 1,917 x 204 x 3 | 1 | 1.4 | 1.4 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 205 | 1 | 14.7 | 14.7 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 205 | 1 | 26.5 | 26.5 | OVER 20 kg | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 205 | 1 | 10.7 | 10.7 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (10 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 10 | 1 | 52.0 | 52.0 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (10 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 10 | 1 | 33.6 | 33.6 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 2.6 | 2.6 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.0 | 3.0 |  | assumption |
| I-TABLE | INTERIOR - TABLE (v1), FLAT-PACKED / Bàn | INTERIOR | 1,000 x 600 x 120 | 1 | 12.0 | 12.0 |  | calculation |
| K-FIX | KIT - M6 BOLTS, RIVNUTS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 1.6 | 1.6 |  | calculation |
|  | **Total** |  |  | 59 |  | **440.2** |  |  |

| Joint | What it joins | Edges | M6 bolts |
| --- | --- | ---: | ---: |
| J-WALL-01 | side wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-02 | back wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-03 | back wall: left half to right half, vertical seam | 2 | 6 |
| J-WALL-04 | side wall to back wall, corner | 4 | 12 |
| J-BASE-01 | walls to base band | 4 | 16 |
| J-CEIL-01 | ceiling halves to walls (side and back edges) | 4 | 16 |
| J-CEIL-02 | ceiling half to ceiling half | 1 | 4 |
| J-FRONT-01 | decor blocks to walls, ceiling and base | 3 | 18 |
| J-FRONT-02 | door hinges and fixed-glass profiles | 1 | 10 |
| J-AIR-01 | fans into ceiling halves | 2 | 4 |
| J-BASE-02 | raised frame corners and joists | 8 | 32 |
|  | **Total** |  | **134** |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-A-1-48x40.svg) | 1,219 x 1,016 | 258 | 569 | 1,641 (64.6 in) | 71.8 | 7.9 | B-BOARD, B-RAIL-FL-06, B-RAIL-FL-07, B-RAIL-FL-08, C-HALF, L-FELT-BACK, L-FELT-CEIL, L-FELT-SIDE, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-A-2-96x48.svg) | 2,438 x 1,219 | 285 | 629 | 798 (31.4 in) | 83.8 | 7.5 | B-JOIST, B-RAIL-FL-01, B-RAIL-FL-02, B-RAIL-FL-03, B-RAIL-FL-04, B-RAIL-FL-05, B-THRESH, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, I-TABLE, KIT-CARTON |

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 20.0 | 0.0 | - |
| 2 | Raised frame: bars, corner brackets, joists, 6 feet; level | 15 | 32 | 0 | 24.2 | 24.2 | Corner bolts from above and inside before any wall stands on the frame. |
| 3 | 2 floor boards screwed to the joists (plan: screws, a second fastener and a driver) | 2 | 0 | 0 | 3.0 | 5.3 | From above, open. |
| 4 | Lower walls: back pair on its pins, then the two sides; bolts to the band, bolts at seam and corners | 4 | 25 | 0 | 4.5 | 14.0 | From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays. |
| 5 | Upper walls: back pair, then sides; bolts at horizontal seams, vertical seam and corners | 4 | 25 | 0 | 4.5 | 14.0 | As the lower walls; top fixings at 2.2 m need the step stool. |
| 6 | Ceiling halves lifted onto the walls from inside; fans and silenced vents from below | 2 | 24 | 0 | 5.5 | 12.0 | Upward from inside, ceiling felt (or its joint strips) not yet on; fans mount from below through their opening. |
| 7 | Decor blocks (skins on, factory-made): left door post, right, then top | 3 | 18 | 0 | 4.5 | 9.0 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 8 | Fixed glass into its sealed profiles (2 people, 2 suction lifters) | 1 | 4 | 0 | 12.8 | 2.0 | Profile frame bolted from inside; glass held by clip-in beads. |
| 9 | Door: hinges on the left decor post, pull, drop seal; adjust swing (2 people, 2 suction lifters) | 1 | 6 | 0 | 18.8 | 3.0 | Hinge bolts reachable with the door open 90 degrees. |
| 10 | Electrics: 3 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 1.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 11 | Felt lining: 10 panels pressed onto Velcro | 10 | 0 | 0 | 0.0 | 12.5 | Closes every bay: last. |
| 12 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 43 | 134 | 0 |  |  | **191 min (6.4 person-hours)** |

</details>

<details><summary>Option B1 (confirmed, D-04), light build: part list, joints, pallets</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER WITH FELT / Vách hông - khung dưới | WALL | 1,495 x 1,145 x 47 | 2 | 12.5 | 24.9 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER WITH FELT / Vách hông - khung trên | WALL | 1,495 x 1,145 x 47 | 2 | 12.5 | 24.9 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER WITH FELT / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 47 | 2 | 10.3 | 20.5 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER WITH FELT / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 47 | 2 | 10.3 | 20.5 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,495 x 1,212 x 47 | 2 | 13.2 | 26.3 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 6.5 | 6.5 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,457 x 1,212 x 15 | 2 | 16.4 | 32.8 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 205 | 1 | 10.0 | 10.0 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 205 | 1 | 18.1 | 18.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 205 | 1 | 7.0 | 7.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 4.7 | 4.7 |  | calculation |
|  | **Total** |  |  | 45 |  | **297.4** |  |  |

| Joint | What it joins | Edges | M6 bolts |
| --- | --- | ---: | ---: |
| J-WALL-01 | side wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-02 | back wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-03 | back wall: left half to right half, vertical seam | 2 | 6 |
| J-WALL-04 | side wall to back wall, corner | 4 | 12 |
| J-BASE-01 | walls to base band | 4 | 16 |
| J-CEIL-01 | ceiling halves to walls (side and back edges) | 4 | 16 |
| J-CEIL-02 | ceiling half to ceiling half | 1 | 4 |
| J-FRONT-01 | decor blocks to walls, ceiling and base | 3 | 18 |
| J-FRONT-02 | door hinges and fixed-glass profiles | 1 | 10 |
| J-AIR-01 | fans into ceiling halves | 2 | 4 |
| J-BASE-02 | base band corner keys and front joints | 6 | 12 |
|  | **Total** |  | **114** |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-B1-1-48x40.svg) | 1,219 x 1,016 | 179 | 395 | 1,641 (64.6 in) | 71.8 | 5.5 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, C-HALF, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-B1-2-96x48.svg) | 2,438 x 1,219 | 217 | 479 | 618 (24.3 in) | 64.9 | 7.4 | B-BAND-BACK, B-BAND-SIDE, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-BOX-1, KIT-BOX-2 |

</details>

<details><summary>Option B2: part list, joints, pallets, assembly</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER WITH FELT / Vách hông - khung dưới | WALL | 1,495 x 1,145 x 47 | 2 | 12.5 | 24.9 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER WITH FELT / Vách hông - khung trên | WALL | 1,495 x 1,145 x 47 | 2 | 12.5 | 24.9 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER WITH FELT / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 47 | 2 | 10.3 | 20.5 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER WITH FELT / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 47 | 2 | 10.3 | 20.5 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,495 x 1,212 x 47 | 2 | 13.2 | 26.3 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 6.5 | 6.5 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK (1/2) / Viền chân nhôm | BASE | 1,210 x 100 x 40 | 2 | 1.9 | 3.8 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,457 x 1,212 x 15 | 2 | 16.4 | 32.8 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT (half) / Khung trang trí - khối trái (nửa) | FRONT | 1,145 x 278 x 205 | 2 | 5.3 | 10.6 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT (half) / Khung trang trí - khối phải (nửa) | FRONT | 1,145 x 1,016 x 205 | 2 | 9.3 | 18.7 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP (half) / Khung trang trí - khối trên (nửa) | FRONT | 848 x 280 x 205 | 2 | 3.8 | 7.6 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 4.9 | 4.9 |  | calculation |
|  | **Total** |  |  | 49 |  | **299.6** |  |  |

| Joint | What it joins | Edges | M6 bolts |
| --- | --- | ---: | ---: |
| J-WALL-01 | side wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-02 | back wall: panel to panel, horizontal seam | 2 | 8 |
| J-WALL-03 | back wall: left half to right half, vertical seam | 2 | 6 |
| J-WALL-04 | side wall to back wall, corner | 4 | 12 |
| J-BASE-01 | walls to base band | 4 | 16 |
| J-CEIL-01 | ceiling halves to walls (side and back edges) | 4 | 16 |
| J-CEIL-02 | ceiling half to ceiling half | 1 | 4 |
| J-FRONT-01 | decor blocks to walls, ceiling and base | 3 | 18 |
| J-FRONT-02 | door hinges and fixed-glass profiles | 1 | 10 |
| J-AIR-01 | fans into ceiling halves | 2 | 4 |
| J-BASE-02 | base band corner keys and front joints | 6 | 12 |
| J-BASE-03 | base band splices | 1 | 4 |
| J-FRONT-03 | decor half to decor half | 3 | 12 |
|  | **Total** |  | **130** |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-B2-1-48x40.svg) | 1,219 x 1,016 | 149 | 329 | 1,641 (64.6 in) | 71.8 | 4.6 | C-HALF, F-DL, F-DR, F-DT, W-BACK-LO, W-SIDE-LO, W-SIDE-UP |
| [2: 48x40 in](out/pallets-B2-2-48x40.svg) | 1,219 x 1,016 | 101 | 224 | 1,806 (71.1 in) | 79.0 | 2.8 | B-BAND-BACK, B-BAND-FRONT-L, B-BAND-FRONT-R, B-BAND-SIDE, B-FLOOR, B-THRESH, W-BACK-LO, W-BACK-UP |
| [3: 96x48 in](out/pallets-B2-3-96x48.svg) | 2,438 x 1,219 | 174 | 383 | 398 (15.7 in) | 41.8 | 9.2 | F-GLASS-DOOR, F-GLASS-FIXED, KIT-CARTON |

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 14.0 | 0.0 | - |
| 2 | Base band: 4 pieces and corner keys on 8 glides; level from above | 6 | 16 | 0 | 13.5 | 7.8 | Corner keys from above and inside; closed later by the wall panels, so bolted first. |
| 3 | Seal mat and 2 thin floor panels dropped inside the band (no fixings) | 2 | 0 | 0 | 2.2 | 0.0 | - |
| 4 | Lower walls: back pair on its pins, then the two sides; bolts to the band, cam or clip connectors at seam and corners | 4 | 16 | 9 | 1.3 | 9.3 | From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays. |
| 5 | Upper walls: back pair, then sides; cam or clip connectors at horizontal seams, vertical seam and corners | 4 | 0 | 25 | 1.3 | 7.2 | As the lower walls; top fixings at 2.2 m need the step stool. |
| 6 | Ceiling halves lifted onto the walls from inside; fans and silenced vents from below | 2 | 20 | 4 | 4.0 | 8.2 | Upward from inside, ceiling felt (or its joint strips) not yet on; fans mount from below through their opening. |
| 7 | Decor blocks (skins on, factory-made): left door post, right, then top | 6 | 30 | 0 | 2.0 | 13.5 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 8 | Fixed glass in its factory profile frame: set and fix (2 people, 2 suction lifters) | 1 | 4 | 0 | 5.8 | 1.2 | Profile frame bolted from inside; glass held by clip-in beads. |
| 9 | Door: hinges and pull fitted in the factory; lift onto the hinge pins, fit drop seal, adjust (2 people, 2 suction lifters) | 1 | 6 | 0 | 6.8 | 1.8 | Hinge bolts reachable with the door open 90 degrees. |
| 10 | Electrics: 3 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 1.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 11 | Felt: 15 loose strips over the joints (the rest came pre-fitted) | 0 | 0 | 0 | 0.0 | 5.0 | Closes the joints: last. |
| 12 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 27 | 92 | 38 |  |  | **113 min (3.8 person-hours)** |

</details>

<details><summary>Option C: part list, joints, pallets, assembly</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-BAND | WALL - SIDE BAND WITH FELT / Vách hông - băng | WALL | 1,495 x 458 x 47 | 10 | 5.3 | 53.1 |  | calculation |
| W-BACK-BAND | WALL - BACK BAND WITH FELT / Vách hậu - băng | WALL | 1,212 x 450 x 47 | 10 | 4.4 | 43.7 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,495 x 1,212 x 47 | 2 | 13.2 | 26.3 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 10.5 | 10.5 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,457 x 1,212 x 15 | 2 | 16.4 | 32.8 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 205 | 1 | 10.0 | 10.0 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 205 | 1 | 18.1 | 18.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 205 | 1 | 7.0 | 7.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 8.6 | 8.6 |  | calculation |
|  | **Total** |  |  | 57 |  | **311.1** |  |  |

| Joint | What it joins | Edges | M6 bolts |
| --- | --- | ---: | ---: |
| J-WALL-01 | side wall: panel to panel, horizontal seam | 8 | 32 |
| J-WALL-02 | back wall: panel to panel, horizontal seam | 8 | 32 |
| J-WALL-03 | back wall: left half to right half, vertical seam | 5 | 10 |
| J-WALL-04 | side wall to back wall, corner | 10 | 20 |
| J-BASE-01 | walls to base band | 4 | 16 |
| J-CEIL-01 | ceiling halves to walls (side and back edges) | 4 | 16 |
| J-CEIL-02 | ceiling half to ceiling half | 1 | 4 |
| J-FRONT-01 | decor blocks to walls, ceiling and base | 3 | 18 |
| J-FRONT-02 | door hinges and fixed-glass profiles | 1 | 10 |
| J-AIR-01 | fans into ceiling halves | 2 | 4 |
| J-BASE-02 | base band corner keys and front joints | 6 | 12 |
|  | **Total** |  | **174** |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-C-1-48x40.svg) | 1,219 x 1,016 | 141 | 311 | 1,641 (64.6 in) | 71.8 | 4.3 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, W-BACK-BAND, W-SIDE-BAND |
| [2: 96x48 in](out/pallets-C-2-96x48.svg) | 2,438 x 1,219 | 269 | 593 | 1,147 (45.2 in) | 120.4 | 4.9 | B-BAND-BACK, B-BAND-SIDE, C-HALF, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-CARTON, W-BACK-BAND |

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 10.0 | 0.0 | - |
| 2 | Base band: 4 pieces and corner keys on 8 glides; level from above | 5 | 12 | 0 | 13.9 | 5.1 | Corner keys from above and inside; closed later by the wall panels, so bolted first. |
| 3 | Seal mat and 2 thin floor panels dropped inside the band (no fixings) | 2 | 0 | 0 | 2.2 | 0.0 | - |
| 4 | Walls row by row from the bottom: back pair, then each side, 5 rows | 20 | 16 | 94 | 6.7 | 35.5 | All from inside through open frame bays or the loose felt strips over the joints. |
| 5 | Ceiling halves lifted onto the walls from inside; fans and silenced vents from below | 2 | 20 | 4 | 4.0 | 8.2 | Upward from inside, ceiling felt (or its joint strips) not yet on; fans mount from below through their opening. |
| 6 | Decor blocks (skins on, factory-made): left door post, right, then top | 3 | 18 | 0 | 3.2 | 5.4 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 7 | Fixed glass in its factory profile frame: set and fix (2 people, 2 suction lifters) | 1 | 4 | 0 | 5.8 | 1.2 | Profile frame bolted from inside; glass held by clip-in beads. |
| 8 | Door: hinges and pull fitted in the factory; lift onto the hinge pins, fit drop seal, adjust (2 people, 2 suction lifters) | 1 | 6 | 0 | 6.8 | 1.8 | Hinge bolts reachable with the door open 90 degrees. |
| 9 | Electrics: 6 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 2.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 10 | Felt: 36 loose strips over the joints (the rest came pre-fitted) | 0 | 0 | 0 | 0.0 | 12.0 | Closes the joints: last. |
| 11 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 35 | 76 | 98 |  |  | **124 min (4.1 person-hours)** |

</details>

## 3. Floor options

Weighed as the BASE assembly (khung sàn / sàn) under the light build. Step height is from the room floor to the walking surface at the door. Sound notes are directions for the sound group, not ratings.

| Floor | BASE kg (light build) | vs thin floor, kg | Step at the door, mm | Sound | Square and stiff | Levelling | Cables | Assembly | Look | Status |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Raised steel floor (plan as written) | 82.3 | +35.7 | 125 | Closed box: boards over a 100 mm cavity; seal the board joints and perimeter. | Best: the welded or bolted frame sets square and level; walls bolt to it. | 6 M10 feet under the frame; needs a spanner unless the feet adjust from above. | Under the floor, easy. | Longest: 6 frame bars, 2 joists, 4 bolted corners, 6 feet, then 2 boards screwed to the joists (a second fastener type and tool). | Same as v1. | calculation |
| Thin floor inside an aluminium base band (confirmed, D-05, D-18) | 46.6 | +0.0 | 21 | Closed box: floor panels on a 3 mm seal mat, gasket to the base band; the room slab adds mass under it. | Good: the aluminium base band with corner keys sets square; floor panels float inside it. | 8 glides adjusted from above with the same hex key; floor panels follow the room floor and carry no walls. | Inside the back wall cavity and along the base band channel. | Quick: 4 rails and 6 corner keys, level, drop in 2 floor panels. | Base band unchanged except across the door, where it becomes a low threshold. | calculation |
| No floor (base band only) | 13.7 | -32.8 | 0 | Open box: sound and air leak under the walls into the room floor; floorless pods post the weakest numbers (market study). | As the thin floor (same base band). | As the thin floor. | Base band channel only. | Quickest: 4 rails and 6 corner keys, level. | As the thin floor. | calculation |
| Castor platform (optional, Lead's request) | 67.0 | +20.4 | 93 | Closed box like the raised floor, but the gap under the pod needs a skirt or drop seal when parked. | Needs a stiffer platform: the pod racks while rolling, and the glass door can go out of line. | Castors do not level; 4 parking feet are added. | Under the platform; the power cord must be long and loose enough to move the pod. | Like the raised floor (knock-down platform), plus 6 castors. | Base band hides the castors if the frame stays 100 mm; a ramp is needed at the door. | assumption |

Confirmed (D-05, D-18): the thin floor. It is 36 kg lighter than the raised steel floor, closes the box for sound, and cuts the step from 125 mm to 21 mm. The room inside gets 104 mm taller. No floor saves a further 33 kg, but leaves the box open to the room floor, which the market study says leaks most. Castors would let an assembled pod roll around the office. They would cost about 20 kg over the thin floor, a step of about 93 mm with a ramp, a skirt to close the gap when parked, and a stiffer platform so the door stays in line while rolling. Confirmed (D-05, D-18): a possible later accessory, not part of v2.

## 4. Assembly by 2 people

Tool: one 5 mm T-handle hex key (M6 socket-head bolts into rivnuts; glides adjust from above with the same key). Handling aids, not tools: a small step stool and 2 suction lifters for the glass. A small step stool is needed for the ceiling and the top fixings; it is not a tool. Every bolt and clip is reached from inside the pod, through open frame bays or behind the loose felt strip over each joint. The strips, or in the decided build the lining cassettes, go on last.

Before and after the confirmed fast-assembly changes (D-08), on the light build. Each row adds one change to the rows above it, with the same time model:

| Change (each added to the ones above) | Status | Saves, min | Assembly after it, min | M6 bolts | Cam or clip connectors |
| --- | --- | ---: | ---: | ---: | ---: |
| Option B1 as first studied (light build, everything bolted, felt on site) | - |  | 166 | 114 | 0 |
| Factory subassemblies: decor blocks with skins on (already), door hinges and pull fitted in the factory so the door lifts onto its pins, fixed glass pre-glazed in its profile frame | confirmed (D-08) | 22 | 145 | 114 | 0 |
| Captive M6 bolts, already started in their panels, that can't be dropped | confirmed (D-08) | 13 | 132 | 114 | 0 |
| Tool-free cam or clip connectors on every panel-to-panel seam; panels sit on pins or hooks and hold themselves (bolts stay where loads go to the base, ceiling, decor and hinges) | confirmed (D-08) | 12 | 120 | 76 | 38 |
| Felt pre-fitted on the panels; only a loose strip over each joint goes on site | confirmed (D-08) | 4 | 116 | 76 | 38 |
| Pallets packed in assembly order, parts numbered | packaging, no design change | 12 | 104 | 76 | 38 |

The full-height back wall panel (fewer, larger panels) was also tried. With the felt pre-fitted it weighs 19.9 kg, over the limit, so it is not used.

What remains is mostly work that does not shrink with fewer parts: unpacking, levelling, setting the glass and the door, and testing the electrics. The 1-hour target needs that work timed on the prototype, and possibly more done in the factory. Section 5 gives the step-by-step sequence and access check for the decided build.

Benchmark: Room S needs 4 people for 3 to 5 hours (12 to 20 person-hours), and hushMeet 2 installers for 2.5 to 3 hours (market study). The decided build takes 4.2 person-hours.

## 5. The decided build: final wall stack (re-check)

The sound study's final stack (confirmed, D-16, D-17, D-34, D-37, D-42): ACP 3 mm on a 20 x 40 x 1.2 aluminium frame at 400 mm with 40 mm PET fill at 32 kg/m3, then a floating lining cassette: a 0.5 mm steel tray, 25 mm deep, with 9 mm felt across its face. That makes 81 mm and 12.6 kg/m2 in the sound study. The ceiling uses the same stack. The front is frameless 4+4 laminated glass.

This study builds it on the B1 layout. The outer panel (ACP, frame and fill) and its cassette are separate parts; the cassette is the clip-on inner leaf (D-17). Sizes follow the pod skeleton P03 (S32):
- side walls (vách hông) 1,495 mm deep, starting at the decor back plate as in v1 (D-49); side cassettes 1,448 mm long, running past the back cassettes' face to close the inside corner; the upper ones 1,098 mm tall, stopping 4 mm under the roof frame so they float (D-57);
- back wall (vách hậu) and ceiling (trần) outer panels 1,207 mm per half, frame to frame between the side frames, with the side skins covering their edges; their cassettes 1,169 mm (D-55);
- decor blocks (khối trang trí) 205 mm deep, as v1 (D-49). Their weights already came from v1's real shapes in the STEP, so only the packing changes.

The inside narrows to 2,338 mm. The wall here comes to 13.4 kg/m2 with clips and tray returns (the sound study: 12.6). The door edge seals, base seal and cable grommets are counted too.

Air (thông gió), as the sound and air check picked it (D-51, S30): four 12 V fans (quạt thông gió; Noctua NF-A14 industrialPPC-3000 PWM, 0.3 kg each, an assumption until the sample is weighed), two per path on a bulkhead in each cartridge's lined fan box; two splitter cartridges (ống tiêu âm), 2,100 x 405 x 159 mm, 17.1 kg each with their fill and 17.7 kg with their fans; and the 2,000 x 155 x 150 mm exhaust riser, 9.6 kg. That is 45.0 kg, all in the right decor block. The room-side intake sits low on the block and the exhaust leaves through the top slot, at least 1 m apart, so the pod doesn't breathe its own exhaust (D-58). The top block carries no air parts, and there is no loose decor fill: the 40 mm fill in front of each cartridge replaces the old felt-lined decor cavity (S31).

Result: **426.7 kg** against the 420 kg cap (6.7 kg over), 0 parts over 20 kg except the glass, heaviest F-DR at 18.1 kg, 1 + 1 pallets, 526 kg gross, 1,641 mm at most, assembly 126 min.

### 5.1 Against the sound and air check's 418 kg

Same build, two models. The check (PR #11) multiplies its wall and ceiling mass per m2 by the outside areas, adds its bought parts, and takes the rest of the pod from an older copy of this study. This study adds up its own parts:

| Group | This study, kg | Sound and air check, kg | Difference, kg | Why |
| --- | ---: | ---: | ---: | --- |
| Walls, ceiling and their lining cassettes | 210.9 | 201.6 | +9.3 | this study carries the cassette clips and rails (0.6 kg/m2, 9.0 kg) and the bond lines (0.25 kg/m2, 3.9 kg), both assumptions that the check leaves out; without them this study's walls and ceiling are 3.7 kg lighter than the check's 12.6 kg/m2 over the outside areas |
| Glass: door leaf and fixed panel | 71.2 | 71.9 | -0.7 | finished shapes from the v1 STEP here; 21 kg/m2 over 3.425 m2 there |
| Air: 2 cartridges, riser, 4 fans | 45.0 | 45.0 | +0.0 | the same cartridges, riser and fans |
| Everything else | 99.6 | 99.0 | +0.6 | base, decor blocks, door hardware, kits, electrics and the voice-kit reserve; the check takes them from an older copy of this study |
| **Total** | **426.7** | **417.5** | **+9.2** |  |

The gap is the clip and bond allowances, which neither model can source yet: the clip is still a candidate (Häfele KEKU EH, HOLD) and the bond pattern waits for its coupon test. By D-54 the cap stays at 420 kg and this study carries 426.7 kg as the current estimate, open against it (LS-01, ISS-080). The factory's wall sample (D-32) settles it with two tests: weigh a real cassette with its clips, rails and bond lines per m2, and test the 25 kg/m3 fill next to the 32 kg/m3; if the lighter fill matches on sound, the build switches and saves 4.3 kg. If the sample still lands over 420 kg, the PM rules on trims then. The CAD parts list in Milestone 2 settles the rest.

- **Glass.** The door unit (2,096 mm, 47.5 kg: glass, kick strip with drop seal, hinges, pull) and the fixed panel (28.0 kg) ride flat on top of the long pallet in their timber frame, with nothing on them. On site, each is carried by two people with 2 suction lifters. The door lifts straight onto its hinge pins once a rated hinge set is named (HOLD, D-46, D-56). The fixed glass's profiles sit hidden in the decor and base, so the front stays frameless like v1.
- **Decor blocks and air parts (confirmed, D-59).** Each decor block is mounted empty. The right block's inner face is a removable, felt-covered panel that carries both grilles. With it off, the two cartridges, with their fans fitted, and the riser slide in from inside the pod, and the panel goes back on. They come out the same way for service, into the pod. Lifting them out through the top lid is rejected, because it would need about 4.5 m of room height. If a full-length cartridge (2,100 x 405 x 159 mm) proves awkward to handle inside the pod, about 2.3 m tall, it splits into two sections with a sealed slip joint. That is the only place the fans appear: the ceiling has no fan opening and no fan joint. Every lift stays at 20 kg or less; the right block with its air parts inside would weigh 63.1 kg. The panel is inside only, so the look is untouched. How the cartridges and riser fit inside the 205 mm block is a CAD HOLD (D-56, ISS-078).
- **Ceiling (confirmed, D-24).** The fill still rides on the back of the ceiling cassette. With 40 mm frames, both ceiling parts are well under 20 kg either way.
- **Pallets.** The 48 x 40 carries the wall and ceiling panels, the wall cassettes, the floor panels and the short band pieces (244 kg, 1,641 mm). The long pallet carries the decor blocks, the long band pieces, the two cartridges and the riser, the kit, the ceiling cassettes that don't fit the upright stack, and the glass on top (281 kg, 971 mm). The pallet tables below list every part. Still 1 + 1.

Wall, ceiling, decor, air and glass parts of the decided build:

| Part | Size mm | Qty | kg each | 20 kg check |
| --- | --- | ---: | ---: | --- |
| W-SIDE-LO: WALL - SIDE PANEL - LOWER (outer: ACP + frame + fill) | 1,495 x 1,145 x 43 | 2 | 11.9 |  |
| L-CASS-SIDE-LO: LINING - CASSETTE FOR W-SIDE-LO (steel tray + felt) | 1,448 x 1,145 x 34 | 2 | 11.1 |  |
| W-SIDE-UP: WALL - SIDE PANEL - UPPER (outer: ACP + frame + fill) | 1,495 x 1,145 x 43 | 2 | 11.9 |  |
| L-CASS-SIDE-UP: LINING - CASSETTE FOR W-SIDE-UP (steel tray + felt) | 1,448 x 1,098 x 34 | 2 | 10.6 |  |
| W-BACK-LO: WALL - BACK PANEL - LOWER (outer: ACP + frame + fill) | 1,207 x 1,104 x 43 | 2 | 9.7 |  |
| L-CASS-BACK-LO: LINING - CASSETTE FOR W-BACK-LO (steel tray + felt) | 1,169 x 1,104 x 34 | 2 | 8.7 |  |
| W-BACK-UP: WALL - BACK PANEL - UPPER (outer: ACP + frame + fill) | 1,207 x 1,104 x 43 | 2 | 9.7 |  |
| L-CASS-BACK-UP: LINING - CASSETTE FOR W-BACK-UP (steel tray + felt) | 1,169 x 1,104 x 34 | 2 | 8.7 |  |
| C-HALF: CEILING - HALF PANEL (outer: ACP + frame) | 1,495 x 1,207 x 43 | 2 | 10.1 |  |
| L-CASS-HALF: LINING - CASSETTE FOR C-HALF (steel tray + felt + ceiling fill) | 1,414 x 1,169 x 74 | 2 | 13.2 |  |
| F-DL: FRONT - DECOR BLOCK - LEFT | 2,290 x 278 x 205 | 1 | 10.0 |  |
| F-DR: FRONT - DECOR BLOCK - RIGHT | 2,290 x 1,016 x 205 | 1 | 18.1 |  |
| F-DT: FRONT - DECOR BLOCK - TOP | 1,697 x 280 x 205 | 1 | 7.0 |  |
| F-GLASS-DOOR: FRONT - GLASS DOOR UNIT (4+4 laminated glass, frameless, 85 mm kick strip with drop seal, hinges, pull) | 2,096 x 1,176 x 20 | 1 | 47.5 | glass (exempt) |
| F-GLASS-FIXED: FRONT - FIXED GLASS (4+4 laminated glass, frameless) | 2,139 x 724 x 9 | 1 | 28.0 | glass (exempt) |
| A-CART-SUPPLY: AIR - SUPPLY SPLITTER CARTRIDGE WITH 2 x 12 V FANS (Noctua NF-A14 industrialPPC-3000 PWM) | 2,100 x 405 x 159 | 1 | 17.7 |  |
| A-CART-EXHAUST: AIR - EXHAUST SPLITTER CARTRIDGE WITH 2 x 12 V FANS (Noctua NF-A14 industrialPPC-3000 PWM) | 2,100 x 405 x 159 | 1 | 17.7 |  |
| A-RISER: AIR - EXHAUST RISER 150 mm (1 mm galvanised steel duct) | 2,000 x 155 x 150 | 1 | 9.6 |  |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-B1F-1-48x40.svg) | 1,219 x 1,016 | 244 | 539 | 1,641 (64.6 in) | 71.8 | 7.5 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, C-HALF, L-CASS-BACK-LO, L-CASS-BACK-UP, L-CASS-SIDE-LO, L-CASS-SIDE-UP, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-B1F-2-96x48.svg) | 2,438 x 1,219 | 281 | 620 | 971 (38.2 in) | 101.9 | 6.1 | A-CART-EXHAUST, A-CART-SUPPLY, A-RISER, B-BAND-BACK, B-BAND-SIDE, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-BOX-1, L-CASS-HALF |

Step by step, with the access check. A step fails the check if a part fitted earlier blocks its fixings; none does in this order. The check is at layout level and is repeated on the CAD in Milestone 2.

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 10.0 | 0.0 | - |
| 2 | Base band: 4 pieces and corner keys on 8 glides; level from above | 5 | 12 | 0 | 13.9 | 5.1 | Corner keys from above and inside; closed later by the wall panels, so bolted first. |
| 3 | Seal mat and 2 thin floor panels dropped inside the band (no fixings) | 2 | 0 | 0 | 2.2 | 0.0 | - |
| 4 | Lower walls: back pair on its pins, then the two sides; bolts to the band, cam or clip connectors at seam and corners | 4 | 16 | 9 | 1.3 | 9.3 | From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays. |
| 5 | Upper walls: back pair, then sides; cam or clip connectors at horizontal seams, vertical seam and corners | 4 | 0 | 25 | 1.3 | 7.2 | As the lower walls; top fixings at 2.2 m need the step stool. |
| 6 | Ceiling halves lifted onto the walls from inside | 2 | 16 | 4 | 4.0 | 7.0 | Upward from inside, ceiling felt (or its joint strips) not yet on. |
| 7 | Decor blocks (skins on, factory-made): left door post, right, then top; then 3 air parts slid into the right block from inside, with its removable felt-covered inner panel off: the supply and exhaust cartridges with their 12 V fans fitted, and the exhaust riser between them; the panel, carrying both grilles, goes back on | 6 | 24 | 0 | 9.2 | 7.2 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 8 | Fixed glass in its factory profile frame: set and fix (2 people, 2 suction lifters) | 1 | 4 | 0 | 5.8 | 1.2 | Profile frame bolted from inside; glass held by clip-in beads. |
| 9 | Door: hinges and pull fitted in the factory; lift onto the hinge pins, fit drop seal, adjust (2 people, 2 suction lifters) | 1 | 6 | 0 | 6.8 | 1.8 | Hinge bolts reachable with the door open 90 degrees. |
| 10 | Electrics: 3 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 1.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 11 | 10 lining cassettes (steel tray + felt) clipped on from inside, ceiling ones from below | 10 | 0 | 0 | 6.7 | 17.5 | Close every bay and joint: last. Joints stay reachable until then. |
| 12 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 36 | 78 | 38 |  |  | **126 min (4.2 person-hours)** |

<details><summary>Sensitivity: the same layout at 380 and 400 kg with an even added mass (before the final stack was known)</summary>

It adds an even mass to the walls (with or without the ceiling) until the pod reaches the target, with the frames deeper by 20 or 40 mm. Mass inside the plan's panels breaks the 20 kg limit (side panels 24.9 kg, ceiling halves 25.9 kg at 380 kg); on separate inner leaves every part stays at 20 kg or less up to the 400 kg cap.

| Pod kg | Walls thicker by | Sound mass on | Layout | Added kg/m2 | Heaviest part, kg (not glass) | Parts over 20 kg | Pallets 48x40 + 96x48 | Heaviest 48x40 / 96x48 gross kg | Max height mm | Assembly min |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 380 | +20 mm | walls and ceiling | plan split, sound mass inside the panels | 5.9 | C-HALF 25.9 | 3 | 1 + 1 | 290 / 189 | 1,641 | 108 |
| 380 | +20 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 5.5 | C-HALF 25.2 | 1 | 1 + 1 | 224 / 255 | 1,641 | 113 |
| 380 | +20 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 5.7 | F-DR 18.1 | 0 | 1 + 1 | 296 / 183 | 1,641 | 118 |
| 380 | +20 mm | walls only | plan split, sound mass inside the panels | 7.6 | W-SIDE-LO 27.8 | 4 | 1 + 1 | 290 / 189 | 1,641 | 108 |
| 380 | +20 mm | walls only | 3 rows per wall, sound mass inside the panels | 7.1 | W-SIDE-ROW 18.3 | 0 | 1 + 1 | 242 / 237 | 1,641 | 113 |
| 380 | +20 mm | walls only | plan split, sound mass on separate inner leaves | 7.3 | F-DR 18.1 | 0 | 1 + 1 | 296 / 183 | 1,641 | 120 |
| 380 | +40 mm | walls and ceiling | plan split, sound mass inside the panels | 4.7 | C-HALF 25.8 | 3 | 1 + 1 | 264 / 215 | 1,641 | 108 |
| 380 | +40 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 4.2 | C-HALF 25.0 | 1 | 1 + 1 | 199 / 280 | 1,641 | 113 |
| 380 | +40 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 4.5 | F-DR 18.1 | 0 | 1 + 1 | 266 / 213 | 1,641 | 119 |
| 380 | +40 mm | walls only | plan split, sound mass inside the panels | 6.0 | W-SIDE-LO 27.6 | 4 | 1 + 1 | 272 / 207 | 1,641 | 108 |
| 380 | +40 mm | walls only | 3 rows per wall, sound mass inside the panels | 5.4 | W-SIDE-ROW 18.2 | 0 | 1 + 1 | 211 / 268 | 1,641 | 113 |
| 380 | +40 mm | walls only | plan split, sound mass on separate inner leaves | 5.8 | F-DR 18.1 | 0 | 1 + 1 | 266 / 213 | 1,641 | 119 |
| 400 | +20 mm | walls and ceiling | plan split, sound mass inside the panels | 7.1 | C-HALF 28.1 | 5 | 1 + 1 | 310 / 189 | 1,641 | 108 |
| 400 | +20 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 6.7 | C-HALF 27.5 | 1 | 1 + 1 | 239 / 260 | 1,641 | 113 |
| 400 | +20 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 6.9 | F-DR 18.1 | 0 | 1 + 1 | 316 / 183 | 1,641 | 121 |
| 400 | +20 mm | walls only | plan split, sound mass inside the panels | 9.2 | W-SIDE-LO 30.6 | 4 | 1 + 1 | 310 / 189 | 1,641 | 108 |
| 400 | +20 mm | walls only | 3 rows per wall, sound mass inside the panels | 8.7 | W-SIDE-ROW 20.2 | 1 | 1 + 1 | 261 / 238 | 1,641 | 115 |
| 400 | +20 mm | walls only | plan split, sound mass on separate inner leaves | 9.0 | L-LEAF-SIDE-LO 18.7 | 0 | 1 + 1 | 316 / 183 | 1,641 | 120 |
| 400 | +40 mm | walls and ceiling | plan split, sound mass inside the panels | 6.0 | C-HALF 28.1 | 5 | 1 + 1 | 282 / 217 | 1,641 | 108 |
| 400 | +40 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 5.5 | C-HALF 27.2 | 1 | 1 + 1 | 211 / 288 | 1,641 | 113 |
| 400 | +40 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 5.8 | F-DR 18.1 | 0 | 1 + 1 | 274 / 225 | 1,641 | 119 |
| 400 | +40 mm | walls only | plan split, sound mass inside the panels | 7.7 | W-SIDE-LO 30.4 | 4 | 1 + 1 | 292 / 207 | 1,641 | 108 |
| 400 | +40 mm | walls only | 3 rows per wall, sound mass inside the panels | 7.1 | W-SIDE-ROW 20.1 | 1 | 1 + 1 | 226 / 273 | 1,641 | 115 |
| 400 | +40 mm | walls only | plan split, sound mass on separate inner leaves | 7.5 | F-DR 18.1 | 0 | 1 + 1 | 274 / 225 | 1,641 | 121 |

</details>

## 6. Doorway check

Every part must pass a 914 x 2032 mm (36 x 80 in) doorway. A part is carried on edge, with its longest side along the corridor. It passes if its thickness plus 40 mm of hand room each side fits the width, and its middle dimension fits the height. It is also checked against 813 mm, the minimum clear width of a door under the ADA. Failures: 0.

| Part | Size mm (long x mid x thin) | kg | Width needed on edge, mm | 914 x 2032 doorway | 813 mm clear (ADA) |
| --- | --- | ---: | ---: | --- | --- |
| W-SIDE-LO | 1,495 x 1,145 x 43 | 11.9 | 123 | passes | passes |
| L-CASS-SIDE-LO | 1,448 x 1,145 x 34 | 11.1 | 114 | passes | passes |
| W-SIDE-UP | 1,495 x 1,145 x 43 | 11.9 | 123 | passes | passes |
| L-CASS-SIDE-UP | 1,448 x 1,098 x 34 | 10.6 | 114 | passes | passes |
| W-BACK-LO | 1,207 x 1,104 x 43 | 9.7 | 123 | passes | passes |
| L-CASS-BACK-LO | 1,169 x 1,104 x 34 | 8.7 | 114 | passes | passes |
| W-BACK-UP | 1,207 x 1,104 x 43 | 9.7 | 123 | passes | passes |
| L-CASS-BACK-UP | 1,169 x 1,104 x 34 | 8.7 | 114 | passes | passes |
| C-HALF | 1,495 x 1,207 x 43 | 10.1 | 123 | passes | passes |
| L-CASS-HALF | 1,414 x 1,169 x 74 | 13.2 | 154 | passes | passes |
| B-BAND-BACK | 2,420 x 100 x 40 | 3.6 | 120 | passes | passes |
| B-BAND-SIDE | 1,660 x 100 x 40 | 2.4 | 120 | passes | passes |
| B-BAND-FRONT-L | 300 x 100 x 40 | 0.4 | 120 | passes | passes |
| B-BAND-FRONT-R | 1,050 x 100 x 40 | 1.5 | 120 | passes | passes |
| B-KEY | 120 x 80 x 40 | 0.1 | 120 | passes | passes |
| B-GLIDE | 50 x 50 x 40 | 0.1 | 120 | passes | passes |
| B-THRESH | 1,176 x 60 x 20 | 1.2 | 100 | passes | passes |
| B-FLOOR | 1,414 x 1,169 x 15 | 15.4 | 95 | passes | passes |
| F-DL | 2,290 x 278 x 205 | 10.0 | 285 | passes | passes |
| F-DR | 2,290 x 1,016 x 205 | 18.1 | 285 | passes | passes |
| F-DT | 1,697 x 280 x 205 | 7.0 | 285 | passes | passes |
| F-GLASS-DOOR | 2,096 x 1,176 x 20 | 47.5 | 100 | passes | passes |
| F-GLASS-FIXED | 2,139 x 724 x 9 | 28.0 | 89 | passes | passes |
| F-HW | 2,200 x 120 x 60 | 2.6 | 140 | passes | passes |
| A-CART-SUPPLY | 2,100 x 405 x 159 | 17.7 | 239 | passes | passes |
| A-CART-EXHAUST | 2,100 x 405 x 159 | 17.7 | 239 | passes | passes |
| A-RISER | 2,000 x 155 x 150 | 9.6 | 230 | passes | passes |
| K-SEALS | 600 x 300 x 100 | 1.6 | 180 | passes | passes |
| E-KIT | 600 x 400 x 200 | 3.1 | 280 | passes | passes |
| K-FIX | 400 x 300 x 150 | 4.7 | 230 | passes | passes |

Corridor corners: the longest piece (2,420 mm) must also turn corners carried flat. The longest thin part that turns a 90-degree corner is 3,394 mm between two 1200 mm corridors, and 2,980 mm between a 1200 mm corridor and a 914 mm one, so every part passes.

## 7. Hooks for the voice cockpit kit (later)

Reserve now; don't design the kit (mic array, speakers, screen, status light).

- **Mounting points.** M6 rivnuts in the frame members, placed in the CAD at Milestone 2: a 100 x 100 mm pattern on the back wall centre for a screen at seated eye height; 4 points on a ceiling-half frame for a mic array and speaker plate; 2 behind the top decor block for a status light seen from outside. Each point gets a matching hole in the cassette in front of it.
- **Cable path.** One vertical cable channel with a pull cord in the back wall bay that holds the switches. It runs from the base band (power inlet) to the ceiling. It crosses the same 3 seams as the main harness, so the seam connectors get spare pins instead of new crossings; the bands option would have needed 6 crossings. The channel runs in the outer frame's cavity, behind the cassette; any cable in the cassette gap clips to the cassette only (D-26).
- **Power.** 12 V 5 A (60 W) for the kit on the pod's 12 V bus, which also feeds the fans, lights and sensors (D-10, D-11); the electrical group adds it to the power budget.
- **Weight.** 4 kg is already held in the weight budget.

## 8. Open items and issues found

| ID | Item | State | Who |
| --- | --- | --- | --- |
| LS-01 | 426.7 kg here against the 420 kg cap (6.7 kg over); the sound and air check gives 417.5 kg for the same build (section 5.1). D-54, ISS-080: the cap stays; this estimate stays open until the wall sample weighs a real cassette with its clips, rails and bond lines per m2 and tests the 25 kg/m3 fill next to the 32 kg/m3; then the CAD parts list | open | Wall sample, PM, Milestone 2 |
| LS-02 | 400 mm frame pitch and full-face bond keep the ACP flat without plywood; prove on the early wall sample | PLANNED | Prototype team |
| LS-03 | Tool-free cam or clip connector and captive bolt: real part numbers, loads and pull-out on the aluminium frame | open | Hardware group |
| LS-04 | Cassette clips: captive mechanical clips with a rated load, plus a safety catch on each ceiling cassette (D-47). Candidate Häfele KEKU EH; its rating basis, pull-out rating and fixing to the 0.5 mm tray are HOLD (D-56, ISS-076). Its real weight replaces the 0.6 kg/m2 allowance | HOLD | Hardware group |
| LS-05 | Door hinges and lock rated for the 4+4 laminate of toughened, heat-soaked panes (8.76 mm), 47.5 kg and 1176 mm, fitted in the factory, with the door lifting onto its pins | HOLD (D-46, D-56, ISS-002) | Hardware group |
| LS-06 | The plan uses code VT03 for both the PET felt and the 50 x 100 steel tube | issue | Control pack |
| LS-07 | v1 BOM 9 mm boards vs 15 mm in the drawings and STEP (already listed by the control pack) | issue | Control pack |
| LS-08 | Panasonic FV-15AUL1 weight not published on the pages read; 1.5 kg assumed | unverified | Hardware group |
| LS-09 | Tube wall thicknesses assumed (20 x 20 steel 1.2 mm, aluminium 1.5 mm); the plan gives none | assumption | Hardware group |
| LS-10 | Bolt counts use a 400 mm pitch only for counting; the joint register sets the real pitch from loads | assumption | Milestone 2 |
| LS-11 | Assembly times are assumptions until the timed prototype trial | PLANNED | Prototype team |
| LS-12 | Decor cladding colour: Dark Yellow ACP EV3038 (D-12); no weight effect | confirmed | Control pack |
| LS-13 | Room floor flatness must stay within the glides' adjustment range; check on site before install | assumption | Install guide |
| LS-15 | Removable, felt-covered inner panel of the right decor block, carrying both grilles: the cartridges and riser slide in after the block is mounted and come out into the pod for service; inside only. If a full-length cartridge is awkward to handle inside the 2.3 m pod, it splits in two with a sealed slip joint; the wall sample's handling check shows which | confirmed (D-59) | Decor CAD, wall sample |
| LS-16 | Cartridges and riser inside the 205 mm right block: CAD fit, and the fan sample (flow against pressure, octave sound power at 53 and 70 l/s, any tone at 125 to 250 Hz, and at boost the intake air within 0.5 K of the room, D-58). The fans' 0.3 kg each is an assumption until weighed (D-56, ISS-077, ISS-078) | HOLD | Sound study, Milestone 2 |
| LS-14 | The upright stack on the 48 x 40 does not fill its depth: centre it and strap through the deck, or put the kit boxes beside it | note | Packaging |
| LS-17 | The control pack's PR #19 logged the rulings this study first cited by PR, as D-49 to D-59 (decor and wall depth, 12 V fans, weight, frame-to-frame back wall and ceiling, HOLD list, kick strip and linings, air openings, cartridge service); the numbers cited here match the merged log. This update also settles the layout study's part of ISS-079 (the 230-235 decor and the 1169 back and ceiling panels) | closed | Control pack |

## 9. How to reproduce

From this folder, with Python 3.10+ and openpyxl:

```
python3 scripts/run_all.py           # writes report.md, out/*.csv and out/*.svg
python3 scripts/run_all.py --check   # rebuilds in memory; fails if anything differs
python3 scripts/test_layout.py       # regression tests: overrides, decided-build counts and limits, sizes, air parts, status words
```

The STEP cross-check data (`data/v1_step_solids.csv`) comes from `scripts/step_crosscheck.py`, which reads the v1 STEP with cadquery-ocp in a separate virtualenv (see the script header). Unit note: 1 lb = 0.4536 kg; imperial values are reference data for US freight only.

## 10. Inputs, status and sources

| Name | Value | Unit | Status | Source | Note |
| --- | ---: | --- | --- | --- | --- |
| pod_w | 2500 | mm | confirmed | S04, D-01 | overall width X |
| pod_d | 1700 | mm | confirmed | S04, D-01 | overall depth Y |
| pod_h | 2400 | mm | confirmed | S04, D-21 | overall height Z, room floor to the top of the roof skin |
| decor_depth | 205 | mm | confirmed | D-49 (replaces D-39; S32) | front decor block depth as v1: v1 decor-frame drawing and STEP, Y -850 to -645 (D-39's 230-235 came from the v1 BOM; the plan said 200) |
| wall_depth | 1495 | mm | confirmed | D-49 (S32) | side walls start at the decor back plate (Y -645), as v1 (1496); was 1500 = 1700 - 200 |
| acp_t | 3 | mm | source | S23 | ACP skin thickness (Alcorest 3 mm) |
| wall_t_plan | 38 | mm | source | S04 | 3 ACP + 6 ply + 20 tube + 9 PET (plan joint detail) |
| base_h | 100 | mm | source | S04 | base band: 50x100 tube on edge |
| glide_h | 10 | mm | assumption | S04 | foot/glide height below the base band |
| rho_steel | 7850 | kg/m3 | source | S06 |  |
| rho_al | 2700 | kg/m3 | source | S07 |  |
| rho_glass | 2500 | kg/m3 | source | S08 |  |
| rho_pmma | 1190 | kg/m3 | source | S09 |  |
| rho_ply | 600 | kg/m3 | assumption | S13 | plywood/board; range 540-660 used for the v1 range |
| rho_ply_lo | 540 | kg/m3 | assumption | S13 |  |
| rho_ply_hi | 660 | kg/m3 | assumption | S13 |  |
| rho_timber | 550 | kg/m3 | assumption | S13 | v1 40x40 frame timber, species not stated |
| rho_timber_lo | 500 | kg/m3 | assumption | S13 |  |
| rho_timber_hi | 600 | kg/m3 | assumption | S13 |  |
| pvb_kgm2 | 0.81 | kg/m2 | calculation | S08 | 0.76 mm PVB at 1070 kg/m3 (assumption on PVB density) |
| acp2_kgm2 | 2.9 | kg/m2 | source | S10 | 2 mm ACP |
| acp3_kgm2 | 3.5 | kg/m2 | calculation | S23, S24 | Spaceship: 3 mm Alcorest EV3038 ACP, 0.21 mm skins; the sound study's figure from the skin spec, used by PM ruling (was 3.8); the maker publishes no kg/m2 |
| acp3_v1_kgm2 | 3.8 | kg/m2 | source | S10 | v1's 3 mm decor skins: maker unknown, kept at the 0.3 mm-skin figure |
| pet9_kgm2 | 1.8 | kg/m2 | source | S11 | 9 mm PET felt |
| felt_t | 9 | mm | confirmed | D-17 | PET felt on the lining cassette's face (the factory's felt, tested in the wall sample first, D-31) |
| hc10_kgm2 | 4 | kg/m2 | source | S12 | 10 mm Al honeycomb, 0.5+0.5 skins |
| foam25_kgm2 | 1.5 | kg/m2 | assumption |  | 25 mm closed-cell foam core at about 60 kg/m3; the sound group picks the core |
| al05_kgm2 | 1.35 | kg/m2 | calculation | S07 | 0.5 mm aluminium inner skin |
| bond_kgm2 | 0.25 | kg/m2 | assumption |  | factory bond line or structural tape, per bonded face |
| felt_fix_kgm2 | 0.05 | kg/m2 | assumption |  | Velcro strips on felt panels |
| t_steel_20 | 1.2 | mm | assumption | S04 | VT10 20x20 steel tube; plan gives no wall thickness |
| t_steel_50x100 | 2 | mm | calculation | S02 | v1 STEP: volume/length of the 100x50 rails gives 2.0 mm |
| t_steel_30x60 | 1.4 | mm | assumption | S04 | VT04 30x60 joists |
| t_steel_16 | 1 | mm | assumption | S01 | v1 decor 16x16 tube (STEP models these as solid bars) |
| t_steel_60x20 | 1.2 | mm | assumption | S01 |  |
| t_steel_20_v1 | 1 | mm | assumption | S01 |  |
| t_steel_d100 | 2 | mm | assumption | S01 | v1 table leg tube |
| t_al_20 | 1.5 | mm | assumption | S07 | 20x20 aluminium tube for light frames |
| t_al_base | 2 | mm | assumption | S07 | aluminium 100x40 base rail (the base band) |
| stud_pitch_ply | 600 | mm | assumption |  | max frame member spacing with plywood backing |
| stud_pitch_acp | 400 | mm | confirmed | D-16 | max spacing when ACP is bonded to the frame without plywood, to keep it flat (oil-canning risk) |
| glass_door_w | 1176 | mm | source | S01 |  |
| glass_door_h | 2011 | mm | source | S01 |  |
| glass_fixed_w | 724 | mm | source | S01 | cut rectangle; real shape is bevelled to the decor |
| glass_fixed_h | 2139 | mm | source | S01 |  |
| glass_door_area_step | 2.11 | m2 | calculation | S02 | STEP solid volume / thickness |
| glass_fixed_area_step | 1.37 | m2 | calculation | S02 | STEP solid volume / thickness |
| fan_kg | 1.5 | kg | unverified | S04 | Panasonic FV-15AUL1; weight not published on the pages read |
| fan_v1_kg | 1 | kg | assumption | S01 | v1 200x200x60 fan |
| silencer_kg | 1.5 | kg | assumption | S05 | one silenced vent box per fan (air group designs it) |
| light_kg | 0.5 | kg | assumption | S01 | 170x170 LED ceiling light |
| plate_kg | 0.15 | kg | assumption | S04 | UTEN S300 switch/socket/dimmer/LAN set, each |
| harness_kg | 1.5 | kg | assumption |  | wiring, connectors at panel seams, inlet |
| sensor_kg | 0.1 | kg | assumption | S05 | occupancy sensor for automatic fans |
| foot_kg | 0.25 | kg | assumption | S04 | M10 levelling foot D50 |
| glide_kg | 0.15 | kg | assumption |  | levelling glide adjusted from above |
| hinge_kg | 0.6 | kg | assumption | S01 | glass door hinge, each |
| handle_kg | 0.8 | kg | assumption | S01 | 300 mm glass door pull |
| drop_seal_kg | 0.6 | kg | assumption | S05 | automatic door bottom |
| glazing_profile_kgm | 0.45 | kg/m | assumption | S05 | aluminium U-profile with gasket for fixed glass |
| gasket_kgm | 0.06 | kg/m | assumption | S05 | EPDM/foam gasket on panel joints |
| fill_kgm2 | 0.6 | kg/m2 | assumption | S05 | 20 mm PET cavity fill at 30 kg/m3 (light; sound group sizes it) |
| bolt_kg | 0.012 | kg | assumption |  | M6 bolt + washer + rivnut |
| bolt_pitch | 400 | mm | assumption |  | bolt spacing used only to count bolts; the joint register sets real pitches |
| voice_kit_kg | 4 | kg | assumption | D-11 | reserve for the later voice cockpit kit: mic array, speakers, screen, status light |
| voice_kit_w | 60 | W | confirmed | D-11 | 12 V 5 A for the voice cockpit kit on the 12 V bus (D-10) |
| pal_std_l | 1219 | mm | confirmed | S05 | 48 in |
| pal_std_w | 1016 | mm | confirmed | S05 | 40 in |
| pal_std_h | 121 | mm | source | S14 | 4.75 in |
| pal_std_kg | 20 | kg | source | S14 | 44 lb |
| pal_long_l | 2438 | mm | confirmed | S05 | 96 in |
| pal_long_w | 1219 | mm | confirmed | S05 | 48 in |
| pal_long_h | 121 | mm | assumption | S15 | 3.5 in stringer + 2 x 0.5 in decks = 4.5 in; 4.75 in used |
| pal_long_kg | 48.5 | kg | source | S15 | 107 lb |
| max_load_h | 1829 | mm | confirmed | S05 | about 6 ft loaded height |
| overlength | 2438 | mm | source | S19 | 96 in: pieces longer than this trigger overlength charges at most LTL carriers |
| edge_board | 10 | mm | assumption |  | edge protector at each end of an upright stack |
| glass_pack_h | 50 | mm | assumption |  | two lites flat with foam in a timber edge frame |
| sheet_under_glass | 12 | mm | assumption |  | ply sheet between the decor layer and the glass frame |
| pack_cap_h | 25 | mm | assumption |  | top cap board and corner protection |
| pack_gap | 4 | mm | assumption |  | foam interleaf between upright panels |
| pack_kg_std | 6 | kg | assumption |  | corner boards, foam, straps, film per 48x40 pallet |
| pack_kg_long | 9 | kg | assumption |  | same for a 96x48 pallet |
| glass_frame_kg | 18 | kg | assumption |  | timber A-frame/edge frame holding the glass on the long pallet |
| door_w | 914 | mm | confirmed | S05 | 36 in nominal doorway |
| door_h | 2032 | mm | confirmed | S05 | 80 in nominal doorway |
| door_clear_w | 813 | mm | source | S17 | 32 in minimum clear width |
| hand_clear | 40 | mm | assumption |  | room for fingers each side when carrying a part on edge |
| t_bolt_s | 30 | s | assumption |  | one M6 bolt into a rivnut with a T-handle hex key, panel already on its pins |
| t_carry_s | 45 | s | assumption |  | carry one part from the pallet to its place |
| t_place_s | 45 | s | assumption |  | set one wall/floor part on its locating pins |
| t_place_overhead_s | 120 | s | assumption |  | lift and set one ceiling half, 2 people, step stool |
| t_felt_s | 60 | s | assumption |  | press one felt panel onto its Velcro |
| t_unpack_std_min | 8 | min | assumption |  | open one 48x40 pallet and lay parts out by label |
| t_unpack_long_min | 12 | min | assumption |  | open the long pallet and stand the glass safely |
| t_level_min | 10 | min | assumption |  | level the base with glides and a spirit level |
| t_fixed_glass_min | 12 | min | assumption |  | set fixed glass into its sealed profiles, 2 people |
| t_door_min | 18 | min | assumption |  | hang the glass door, adjust, fit handle and drop seal, 2 people |
| t_elec_min | 10 | min | assumption |  | plug seam connectors and power, test fans and lights |
| t_final_min | 10 | min | assumption |  | check door swing and seals, clean |
| t_connector_s | 20 | s | assumption |  | mate one plug-in cable connector at a panel seam |
| inefficiency | 0.15 | - | assumption |  | added to elapsed time for hand-offs and checking |
| cam_seams | 0 | flag | assumption |  | 1 = panel-to-panel seams use tool-free cam or clip connectors instead of bolts |
| t_cam_s | 10 | s | assumption |  | close one cam or clip connector by hand |
| t_bolt_captive_s | 18 | s | assumption |  | captive M6 bolt already started in its panel: no picking up, no dropping |
| t_place_hung_s | 20 | s | assumption |  | panel hung on hooks or seated on pins holds itself: no second person holding |
| t_door_prehung_min | 6 | min | assumption |  | door arrives hung on the left decor post: set the post, check swing |
| t_fixed_preglazed_min | 5 | min | assumption |  | fixed glass arrives in its profile frame: set and fix the frame |
| t_unpack_std_ordered_min | 4 | min | assumption |  | 48x40 packed in assembly order, parts numbered |
| t_unpack_long_ordered_min | 6 | min | assumption |  | long pallet packed in assembly order |
| t_felt_strip_s | 20 | s | assumption |  | felt pre-fitted on its panel; only the strip over a joint goes on site |
| cam_kg | 0.05 | kg | assumption |  | one cam or clip connector pair |
| kick_strip_kg | 1 | kg | assumption | S29, D-56 | aluminium kick strip at the door bottom, base band finish, houses the drop seal; the PM's 'about 1 kg' |
| kick_strip_h | 85 | mm | confirmed | D-40, D-57 | v1's front drops 17 mm to the 2400 datum, so the door bottom sits at Z 105 and the strip is 85 tall (D-40 said about 90) |
| kick_strip_d | 20 | mm | assumption | S32 | kick strip envelope depth, as the skeleton's kick_d (D-40 gives the height only) |
| strip_w | 150 | mm | assumption |  | loose felt strip over each joint, so the joint stays reachable |
| frame_depth | 20 | mm | source | S04 | wall frame tube depth (20x20); the quiet build deepens it |
| quiet_total | 380 | kg | confirmed | D-02 (replaced by D-27) | history: the PM's target from the Hardware Engineer's sound curve, before the final stack |
| hw_380_total | 377 | kg | source | S20 | Hardware Engineer's best build within a 380 kg budget |
| hw_380_dsa | 22.5 | dB | source | S20 | its central D_S,A estimate |
| quiet_cap | 400 | kg | confirmed | D-02 (replaced by D-37) | history: heavier walls allowed up to 400 kg in total |
| rho_mass_layer | 1600 | kg/m3 | assumption |  | dense sound layer (MLV-like) used only to size the inner leaf thickness |
| leaf_clip_kgm2 | 0.6 | kg/m2 | assumption |  | clip rail and clips of an inner leaf |
| ceil_t | 0 | mm | assumption |  | ceiling thickness; 0 means the same as the walls |
| final_wall_t | 81 | mm | confirmed | D-16, D-42 | final wall: outer panel 3 + 40, cassette 25 + 9, 4 mm gaps |
| final_ceil_t | 81 | mm | confirmed | D-42 | the ceiling uses the wall stack |
| final_wall_depth | 40 | mm | confirmed | D-16, D-34 | 20x40 aluminium wall frame |
| final_ceil_depth | 40 | mm | confirmed | D-42 | 20x40 aluminium ceiling frame (replaces D-16's 20x100 and D-27's 53 mm ceiling) |
| lin_gap | 4 | mm | assumption | D-57 (S32) | gap between the roof frame and the upper side linings, so they float; the same 4 mm as the stack gap |
| final_kgm2_hw | 12.6 | kg/m2 | calculation | S31 | the sound study's wall and ceiling mass with frame, 32 kg/m3 fill, cassette and felt |
| fill_pet_kgm3 | 32 | kg/m3 | confirmed | D-54 (S30, S31) | Pyrotek Sorberpoly 2D; D-34's 25 kg/m3 needs absorption data that isn't published, so its condition moves to the wall sample |
| fill_pet_light_kgm3 | 25 | kg/m3 | source | D-34, D-54 | the lighter fill: the wall sample tests it next to the 32, and the pod switches if it matches on sound |
| t_al_final | 1.2 | mm | confirmed | D-34, D-54 | wall of the 20x40 aluminium frames (was 1.5); the rivnut grip check passed, which settles D-34's frame condition |
| tray_t | 0.5 | mm | confirmed | D-37 | steel lining tray (0.4 mm cost 1 dB, so back to 0.5) |
| tray_t_thin | 0.4 | mm | confirmed | D-35 (replaced by D-37) | the thinner tray tried and dropped |
| tray_depth | 25 | mm | confirmed | D-17 | tray returns and the air gap behind the felt |
| hw_385_total | 385 | kg | source | S21 |  |
| hw_385_dsa | 24.2 | dB | source | S21 |  |
| hw_400_total | 400 | kg | source | S22 | sound study's total with 4+4 laminated glass |
| hw_400_dsa | 23.8 | dB | source | S22 |  |
| cap_kg | 420 | kg | confirmed | D-37, D-54 | weight cap with the 0.5 mm tray; the study's estimate stays open against it until the wall sample |
| hw_total | 417.5 | kg | calculation | S31 | the sound and air check's decided build in its own model ('about 418 kg') |
| hw_shell_kg | 201.6 | kg | calculation | S31 | its walls and ceiling: 12.63 kg/m2 x (12.33 + 3.64) m2 of outside area, cassettes and felt included |
| hw_glass_kg | 71.9 | kg | calculation | S31 | its glass: 21 kg/m2 x 3.425 m2 |
| hw_air_kg | 45 | kg | calculation | S31 | its cartridges 34.2, riser 9.6 and four fans 1.2 |
| hw_rest_kg | 99 | kg | calculation | S31 | its rest of the pod: 102.4 from an older copy of this study, plus 2.6 of fixes, less 6.0 of that copy's fans and boxes |
| fan12_kg | 0.3 | kg | assumption | S30, D-51 | Noctua NF-A14 industrialPPC-3000 PWM, 12 V, 140 x 140 x 25 mm; weight not published: weigh the sample |
| cart_kg | 17.1 | kg | calculation | S30, D-51 | one splitter cartridge with its 40 mm fill toward the pod, without fans |
| cart_d | 159 | mm | calculation | S30 | cartridge depth: three 25 mm layers, two 40 mm passages, 2 mm casing |
| cart_w | 405 | mm | calculation | S30 | cartridge width: two cartridges and the riser side by side in the right block |
| cart_l | 1800 | mm | calculation | S30 | lined passage length |
| fanbox_l | 300 | mm | calculation | S30 | lined fan box at one end of the cartridge, 2 fans on a bulkhead |
| riser_kg | 9.6 | kg | calculation | S30, D-51 | exhaust riser, 1 mm galvanised steel |
| riser_w | 150 | mm | calculation | S30 | the 150 mm exhaust riser |
| riser_d | 155 | mm | calculation | S30 | riser depth, the cartridges' layer stack |
| riser_l | 2000 | mm | calculation | S30 | from the exhaust fans at the foot to the slot on the block's top face |
| door_edge_seal_kg | 1 | kg | source | S20 | door edge seals on 3 sides |
| base_seal_kg | 0.5 | kg | source | S20 | seal under the thin floor and band |
| grommet_kg | 0.1 | kg | source | S20 | sealed cable holes |
| t_leaf_s | 60 | s | assumption |  | clip one inner leaf (sound mass + felt) onto its frame from inside |

Sources:

| ID | What it says | Where |
| --- | --- | --- |
| S01 | v1 materials BOM, v5, 2026-10-29 | `sources/v1/indoor-pod-v3-bom-v5-2026-10-29.xlsx` |
| S02 | v1 STEP assembly, exported 2026-10-14 (older than the BOM; cross-check only) | `sources/v1/indoor-pod-v3-assembly.step` |
| S03 | v1 drawings: wood parts, floor frame, decor frame | `sources/v1/drawings/` |
| S04 | v2 build plan from the indoor pod lead engineer | `v2/00-Control/v2-build-plan.pdf` |
| S05 | v2 plan approved by the product owner, 2026-10-31 (targets, light options, pallet sizes) | `v2/PLAN.md` |
| S06 | EN 1993-1-1 section 3.2.6: steel density 7850 kg/m3 | `EN 1993-1-1:2005` |
| S07 | EN 1999-1-1 section 3.2.3.1: aluminium alloy density 2700 kg/m3 | `EN 1999-1-1:2007` |
| S08 | EN 572-1: soda-lime silicate glass, density 2500 kg/m3 | `EN 572-1:2012+A1:2016` |
| S09 | Evonik PLEXIGLAS GS/XT technical information: PMMA density 1.19 g/cm3 (ISO 1183), E = 3300 MPa | https://www.voskunststoffen.nl/files/166151/datasheet%20plexiglas%20XT%20GS.pdf (read 2026-10-31) |
| S10 | 3A Composites DIBOND product guide: ACP with 0.3 mm aluminium skins, PE core, 2 mm = 2.9 kg/m2, 3 mm = 3.8 kg/m2 | https://www.display.3acomposites.com/files/downloads/products/en/aluminium-composite-sheets/EN_DIBOND_ProductGuide.pdf (read 2026-10-31) |
| S11 | Polyx Board 9 datasheet: 9 mm polyester (PET) acoustic board, 1800 g/m2 | https://aid.co/wp-content/uploads/2024/10/Polyx-Board-9-No-Insulation-No-Air-Gap.pdf (read 2026-10-31) |
| S12 | Compocel AL TDS: 10 mm aluminium honeycomb panel, 0.5 + 0.5 mm skins, about 4.0 kg/m2 | https://www.chemical-concepts.com/wp-content/uploads/2023/09/Compocel-AL-TDS.pdf (read 2026-10-31) |
| S13 | Plywood density: eucalyptus-core plywood 580 +/- 10 kg/m3 (EN 323, distributor datasheet); Vietnamese acacia wood 574-597 kg/m3 (VAFS) | https://vafs.gov.vn/en/wood-properties-of-some-commercial-tree-species-for-the-central-north-region-of-vietnam/ (read 2026-10-31) |
| S14 | PHS S-4840 new wood GMA pallet: 48 x 40 x 4.75 in, 44 lb, 2500 lb dynamic capacity | https://www.phsinc.com/pallet/wood-pallets/s-4840/ (read 2026-10-31) |
| S15 | Uline H-1627 new wood pallet 96 x 48 in: 107 lb, 4-way, 7000 lb fork capacity; 3.5 in stringers, 0.5 in deck boards | https://www.uline.com/Product/Detail/H-1627/Pallets/New-Wood-Pallet-96-x-48 (read 2026-10-31) |
| S16 | NMFTA: ClassIT+ is the official source for NMFC classes; since the 2025 NMFC changes density plays a larger role (density scale widened from 11 to 13 sub-provisions, per carrier summaries) | https://info.nmfta.org/2025-nmfc-changes (read 2026-10-31) |
| S17 | 2010 ADA Standards section 404.2.3: door clear width 32 in (813 mm) minimum | https://www.access-board.gov/ada/#ada-404 (read 2026-10-31) |
| S18 | Market study, 2026-10-31 | `v2/research/market-study.md` |
| S20 | Hardware Engineer's sound and air calc (branch super-tab/09f4617f, commit e22cab1): total-pod kg vs D_S,A curve; at a 380 kg budget with a 10 mm smoked acrylic front: walls DL-ST (ACP 3 / 40 mm fill, shared studs / 0.5 mm steel + felt 9), ceiling DL-2HDF-60-FL (ACP 3 / 60 mm fill / 2 x HDF 3 floating + felt 9), 377 kg, D_S,A 22.5 dB central | `v2/05-Engineering/acoustics-air/calc.py on that branch (read 2026-10-31)` |
| S21 | Hardware Engineer's final wall stack, relayed by the PM in the layout chat, 2026-10-31: ACP 3 / 20x40 aluminium frame at 400 mm with 40 mm PET fill / floating lining cassette (0.5 mm steel tray, 25 mm deep, 9 mm felt across its face); 81 mm and 13.1 kg/m2. Ceiling the same on 20x100, 141 mm. Pod about 385 kg and 24.2 dB with the acrylic front | `layout conversation, PM message of 2026-10-31` |
| S22 | PM ruling relayed in the layout chat, 2026-10-31: front is 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look); the sound study puts the pod at about 400 kg and 23.8 dB with 40 mm ceiling frames and separate silencer boxes; the door is handled by two people with suction lifters | `layout conversation, PM message of 2026-10-31` |
| S23 | Alcorest outdoor ACP, colour EV3038 Dark Yellow (the plan's VT01), 3 mm with 0.21 mm skins: maker's catalogue gives skins, not kg/m2; the sound study calculates 3.5 kg/m2 from the skin spec (selection.md VT01). PM ruling 2026-10-31: use 3.5 | https://vietdung.com.vn/wp-content/uploads/2026/07/CTL-ACP-ALCOREST-07.08.25.pdf (via the sound study's selection table) |
| S24 | PM ruling 2026-10-31: the 400 kg cap stays; carry the total as 400 +/- 10 kg until the CAD parts list settles it; if the CAD BOM lands over 400 kg, trim the inner steel tray or the fans, not the sound | `layout conversation, PM message of 2026-10-31` |
| S28 | Decision log D-01 to D-59, as merged on main (1eec888; PR #19 added D-49 to D-59) | `v2/00-Control/decision-log.md (read 2026-10-31)` |
| S29 | PM ruling after Reviewer 2, 2026-10-31, now logged as D-40: the door gets a ~90 mm aluminium kick strip at the bottom in the base band's dark finish, housing the drop seal, about 1 kg | `layout conversation, PM message of 2026-10-31` |
| S30 | Hardware Engineer's bought-parts selection after the PR #11 fix pass: four Noctua NF-A14 industrialPPC-3000 PWM 12 V fans, two per path on a bulkhead in each cartridge's lined fan box, 140 x 140 x 25 mm, about 0.3 kg each (assumption: weigh the sample); two splitter cartridges side by side in the right decor block, 159 x 405 x 1800 mm plus a 300 mm fan box, 2 mm aluminium casing, three 25 mm Pyrotek layers, 40 mm polyester fill toward the pod, 17.1 kg each with that fill (calculation); exhaust riser between them, 150 x 155 x 2000 mm, 1 mm galvanised steel, 9.6 kg (calculation; CAD fit HOLD); cavity fill Pyrotek Sorberpoly 2D at 32 kg/m3, because the 24 kg/m3 grade has no published absorption | `v2/05-Engineering/hardware/selection.md, summary, B, F1 and F2 (PR #11, merged 39c5c3e; read 2026-10-31)` |
| S31 | Hardware Engineer's sound and air check after the PR #11 fix pass: the decided stack is 81 mm at 12.6 kg/m2 with frame, 32 kg/m3 fill and felt; the decided build is about 418 kg in its own model (417.5 kg: 102.4 kg rest of pod from an older copy of this study, 2.6 kg fixes, 12.63 kg/m2 over 12.33 m2 of walls and 3.64 m2 of ceiling, 71.9 kg glass, 34.2 kg cartridges, 9.6 kg riser, 1.2 kg fans, less 6 kg of the old study's fans and boxes); decor 205 mm deep; the 40 mm fill in front of each cartridge replaces the old felt-lined decor cavity | `v2/05-Engineering/acoustics-air/report.md sections 1, 6 and 7b, and calc.py pod_total_kg (PR #11; read 2026-10-31)` |
| S32 | Pod skeleton P03 build record, PM rulings: PR #15, back wall and ceiling frames span frame to frame between the side frames (X +-1207), so 1207 per half, with their linings staying 1169; PR #16 ruling 3, D-39 means as v1, and the v1 decor-frame drawing and STEP give 205 mm (front face Y -850, back face Y -645); PR #17 pass C, wall depth 1495 (side walls start at the decor back plate, as v1's 1496), side linings 1448 long to close the inside corner, upper side linings stop 4 mm under the roof frame (1098 tall) | `v2/01-CAD-Native/skeleton/BUILD-RECORD.md and 100000_P03_POD-SKELETON-PARAMETERS.csv (read 2026-10-31)` |
| S33 | Pod skeleton P04 (PR #24): 46 mm outer panel (ACP 3 + bond line 3 + frame 40), 84 mm stack, 2.26 mm seams; side panels 1492.74 x 1142.74, back panels 1200.61 x 1118.61, side linings 1445 long, back linings 1166 wide, floor panels 1210 x 1455 | `v2/01-CAD-Native/skeleton/BUILD-RECORD.md and 100000_P04_POD-SKELETON-PARAMETERS.csv; updated in place in PR #58 (floor 9, threshold 13, back and ceiling frames 1198.99 under 1200.61 skins, the 220 mm bolt rule) and PR #94 (bolt pitches on the frame, bolt lines, counts, the floor on its 3 mm mat); the roll-up reads its named values` |
| S34 | WALL P01 parts lists merged on main for all four side panels: 210101 to 210104 the outer panels L1, R1, L2, R2 (frames with their 3 mid stiles at 1.0 mm and the 40 x 40 back stiles, L2 and R2 with 40 x 40 tops; skins; 40 mm fill at 24 kg/m3; bond sets; hardware listed) and 510101 to 510104 their lining cassettes (trays with lips, felts with ELECTRICAL's openings, hook-and-loop, seals; clips HOLD); the roll-up reads them | `PRs #41 (6ccbfac) and #104 (87586c1): v2/03-Manufacturing/wall/21010n_P01_*_BOM.csv` |
| S35 | CEILING P01 parts list, merged on main: panels C1 and C2 (frames with the 40 x 40 back member, skins, bond sets; hardware and the closing-seam bulb seal listed) and the common ceiling cassette 510301 (tray, 2 ribs, felt, three fill bays at 25 kg/m3; clips and catches HOLD); its first list gave 9.586 kg a panel and 9.816 kg a cassette on skeleton P03; the roll-up reads it | `PR #32 (c72ea57): v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv` |
| S36 | FRONT door unit 360001 P01 parts list, merged on main: the 4+4 leaf, the hollow kick strip (D-85), drop seal, U-seal, 3 hinges (HOLD), the strike and one half of the magnetic seal (D-83), the pull pair (HOLD); its first list gave 50.17 kg with a solid 2.094 kg strip; the roll-up reads it | `PR #27 (7963e9c): v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv` |
| S37 | FRONT fixed glass unit 360002 P01 parts list, merged on main: the 4+4 pane, the glazing U-profile and U-seal, and one half of the magnetic seal (D-83, HOLD); its first list gave 29.58 kg with a glass-to-glass seal; the roll-up reads it | `PR #28: v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv` |
| S38 | Air report section 7f (D-60 on skeleton P04, with AIR #91's column and soffit sizes, section 7j): the air parts and the four fans, read from calc.py d60_parts() | `v2/05-Engineering/acoustics-air/report.md and calc.py d60_parts() (PRs #26, #30)` |
| S40 | D-81, the PM's weight ruling on PR #38: clip-only cassette fixing, no rails; the lighter cavity fill as the default, back to 32 kg/m3 if T02 fails (24 kg/m3, the grade Pyrotek lists and the sample tests); the base band with a 1.5 mm wall if BASE's check passes; the voice kit's 4.0 kg reserve outside the 420 kg cap, which is for the pod as shipped (D-11); the fixed glass in 3+3 only after FRONT's calculation; the door leaf in 3+3 rejected (D-46 stands); 410 kg or less as shipped | `v2/00-Control/decision-log.md D-81 (PR #36, fbdfc73; its fill corrected to 24 kg/m3 in PR #48, f03372c); the PM's brief for the live roll-up, 2026-10-31` |
| S53 | D-126: the light shelf's down-light is a bought LED profile, listed in ELECTRICAL's parts list under INTERIOR's shelf 810201 (PR #216): the profile 718101, its clip-in cover 718102 (satin, at least 86 % of the light, D-127, PR #219), 2 end caps 718103 and 3 clips 718104, all HOLD. They replace INTERIOR's down-light channel 811204 and diffuser 811205 and ship with the shelf, so the shelf's line carries them and leaves out the channel and diffuser while INTERIOR's list still lists them | `PR #216 (916b6f7), PR #219 (40871f9): v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv; v2/00-Control/decision-log.md D-126, D-127` |
| S52 | AIR P01 parts list (PR #91): the air column 610101, the soffit 610201 with the exhaust fan box 610402, the splitter cartridge 610301 (two), the supply fan box 610401 with the intake riser 611501 and the two transitions (HOLD, at their sized masses), the roof sleeve and grille, four fans (0.3 kg each, assumption); masses from Fusion (CAD geometry x density). The roll-up takes the changes already ruled that the AIR follow-up builds (D-81 fill at 24, D-116 layers at 32, D-124 fan box casings 3 mm) and the air report's sizes for what the CAD doesn't model yet (D-121's bulkheads and linings, the riser's foot and mesh piece) | `v2/03-Manufacturing/air/610000_P01_AIR-PARTS-LIST_BOM.csv (PR #91); v2/05-Engineering/acoustics-air/calc.py d60_parts()` |
| S50 | WALL P01 parts lists merged on main for the two lower back panels (PR #152): 210201 and 210202, B1 and B2 (frames with their 2 mid stiles at 1.0 mm, skins, 40 mm fill at 24 kg/m3, bond sets; hardware listed) and their lining cassettes 510201 and 510202 (trays with their lips, felts, hook-and-loop and edge seals; clips listed). B3 and B4 aren't in CAD yet | `v2/03-Manufacturing/wall/210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_BOM.csv and 210202 (PR #152)` |
| S51 | FRONT P01 parts lists for the three decor blocks (PR #105): 350001 DL, 350002 DT and 350003 DR, each the block's ACP skin, its welded 6063-T6 tube frame, its aluminium back plate and its stops, seals, panels and felt as built in CAD (ACP at 3.5 kg/m2, selection VT01); DR lists AIR's riser, transitions and supply fan box as reserved air spaces with no mass; the hardware is the joints register's | `v2/03-Manufacturing/front/350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_BOM.csv, 350002 and 350003 (PR #105)` |
| S49 | D-117, confirmed (the owner kept v2's construction): the frames' mitred corners take 14.9 g corner cleats and the T joints 6.7 g plug cleats, about 1.2 kg per pod with their glue; the roll-up carries 1.2 kg (assumption) in place of D-115's 2.4 kg allowance until the cleat models land | `the PM (Lead) in the layout study's group, 2026-11-01` |
| S48 | The joints register's part-number table (H-01 to H-09): the site and factory M6 bolts, the closing-seam pins, rivnuts, washers, retainers, the joint gasket and the closing-seam bulb seal, counted per pod; the roll-up multiplies them by the parts lists' masses (D-116: the old fixings model's cam connectors don't exist) | `v2/05-Engineering/joints/joints-register.md; D-116, the PM in the layout study's group, 2026-11-01` |
| S47 | D-115: internal aluminium cleats in the WALL and CEILING frames, about 120 joints at up to 20 g each; the roll-up carries a 2.4 kg allowance (assumption) until the Joints Engineer's cleat models land | `the PM (Lead) in the layout study's group, 2026-11-01 (the decision log follows)` |
| S46 | INTERIOR P01 parts list, merged on main: the work-wall ledge (its top and 2 brackets on HOLD), the light shelf (back and side shelves, the right-wall down-light channel and diffuser; the LED strips are ELECTRICAL's) and the screen rail on HOLD; the roll-up reads it | `PR #92 (b3cc47e): v2/03-Manufacturing/interior/810000_P01_INTERIOR-PARTS-LIST_BOM.csv` |
| S45 | The joints' made hardware list, merged on main: the corner key family 111211 to 111215 (30 mm thick, 6 per pod; D-144), 30 locating spigots 831001 and 76 stop washers 831002 per pod, each with its CAD mass; BASE's follow-up (PR #138) took the 30 mm keys and a 54 mm glide doubler | `PR #139 (e7eef66): v2/03-Manufacturing/joints/V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv; PR #138 (8c3aca4)` |
| S44 | BASE P01 sample parts list, merged on main: the back-left corner and F1 (band tubes side LH 1517 long and back 2420 long at 1.5 mm, the back corner keys, a glide doubler and a HOLD levelling glide at each glide, floor panel F1 in poplar-core 9 mm ply with a hard face veneer, its 3 mm foam mat, the base seal); the right side and F2 as mirrors; the front bands and front keys follow in P02; the roll-up reads it | `PR #55 (dc61ad9): v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv` |
| S43 | ELECTRICAL P01 parts list, merged on main: 710000 as shipped, the power unit 710001 in B2 (enclosure, front plate, three 60 W Class 2 supplies, the LED controller, RCBO, inlet, sockets), the harnesses and cables, the hub and controls zone, the cord set, the LED strips (Loox5 2168 for the shelf uplight and the down-light, 2165 for the call light) and the call light profile; heat: the supplies' losses and the loads in its load table; the roll-up reads it | `PR #64 (e06fa22): v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv; v2/05-Engineering/electrical/` |
| S42 | D-86: the base band at 1.5 mm with an aluminium load block at each glide (about 0.4 kg per pod); the floor in poplar-core 9 mm ply with a hard face veneer, about 0.6 mm at a panel edge under 1000 N, its castor and edge tests planned. D-87: the intake riser joined to the supply fan box (about 14.9 kg with its fans) and the exhaust fan box fitted in the soffit (about 13.9 kg), both under 20 kg; the band's corner keys hook in (12 fewer bolts); the floor foam bonded under the floor panels | `v2/00-Control/decision-log.md D-86, D-87 (PR #57, e163737)` |
| S41 | D-82: the fixed glass stays 4+4 (a 3+3 pane bends 58 mm). D-83: a magnetic catch in DT and a magnetic seal pair replace the door lock. D-85, the PM's pick toward the 410 kg target: weight budgets for the light shelf (0.4 kg/m) and the ledge (1.5 mm folded aluminium); inner frame studs at 1.0 mm on the walls only, the perimeters at 1.2 for the rivnuts and the ceiling's inner members at 1.2 for the overhead cassette clips and safety catches; 2 inner studs in each back panel at 393 mm; a hollow kick strip with the same outside; poplar-core 9 mm floor plywood if BASE's castor and 1000 N edge tests pass. Rejected: the perimeters at 1.0 mm. Parked: the decor frames, 18 kg/m3 fill and a lighter felt; the 410 kg target stays | `v2/00-Control/decision-log.md D-82, D-83 (PR #48, f03372c); D-85: the PM (Lead) in the layout study's group, 2026-10-31 (the decision log follows)` |
| S39 | Tonight's PM rulings: D-63 (40 x 40 corner edge tubes, +1.3 kg), D-69 (wall trays take 12 mm lips, +0.43 kg each), D-71 (the running estimate and what it leaves out), D-72 (9 mm plywood floor), D-76 (3 mm firm foam mat, about 2.1 kg) | `PR #35 (49e2d94): v2/00-Control/decision-log.md, D-61 to D-78; the Mechanical Checker's F-010 (PR #25)` |
| S19 | LTL overlength rules: most carriers start excessive-length charges for a piece over 96 in (summary; check each carrier's rules tariff) | https://logisticsplus.com/?p=25575 (read 2026-10-31) |
