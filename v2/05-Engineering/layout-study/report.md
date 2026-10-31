<!-- report.md is generated from report_template.md by scripts/run_all.py. Edit the template or the scripts, never report.md. -->
# Spaceship layout study: weight, pallets and 2-person assembly

Status: DECIDED marks the PM's rulings of 2026-10-31. Under AGENTS.md the PM decides, and the Control Engineer records each decision in `v2/00-Control/decision-log.md`. Spaceship is the working name of v2 (folders keep their v2 names).

Every number below comes from the scripts in `scripts/`. `python3 scripts/run_all.py --check` proves that this report and the files in `out/` reproduce exactly. Section 10 lists the inputs, their status (confirmed, source, calculation, assumption, unverified) and their sources.

## Result

1. **Weight.** v1 weighs 480 kg by its BOM (range 459 to 574 kg). Spaceship as planned weighs 447 kg. The light build is 303 kg, and 304 kg with the fast-assembly hardware. The decided build, with the sound study's final walls and a frameless 4+4 laminated front, is **412 kg** here and about 400 kg in the sound study. Both numbers stand until the master BOM comes out of the CAD (PM ruling). The gap is mostly two items. The inline fans the sound study picked weigh 5 kg each, which adds 7.0 kg here; its own total still carries the plan's 1.5 kg fans. And this study holds 9.0 kg for cassette clips and rails. Against the 400 kg cap that is 12 kg over here. An ACP of 3.4 kg/m2 instead of 3.8 would bring it to 404 kg.
2. **Parts.** In the decided build every part is 20 kg or less except the glass. The glass door weighs 43.3 kg and the fixed panel 28.0 kg; two people carry each with 2 suction lifters (21.6 kg each on the door). The heaviest other part is F-DR at 19.1 kg. The decor's PET fill (4.0 kg) ships loose and goes in on site: inside the right decor block it would make that block 21.2 kg.
3. **Shipping (DECIDED).** One 48 x 40 pallet and one 96 x 48 pallet, 511 kg gross, 6.2 lb/ft3. The 48 x 40 weighs 253 kg and stands 1,646 mm high. The 96 x 48 weighs 258 kg and stands 1,056 mm high, with both lites flat on top in their frame. Walls and ceiling are 81 mm thick.
4. **Assembly (DECIDED changes).** Two people with one 5 mm hex key. The light build takes 166 min before the fast-assembly changes and 104 min after. The decided build takes **121 min** (4.0 person-hours): 76 M6 bolts, 38 tool-free clips and 10 clip-on lining cassettes. The 1-hour target is not reached on these assumptions. Most of what remains is unpacking, levelling, setting the glass and door, and testing, so the timed prototype decides.
5. **Decisions.** Everything in the layout is DECIDED, including carrying the ceiling fill on its cassette. One thing to watch: this study's total is 12 kg over the 400 kg cap until the master BOM settles it (item 1).

## Decisions

| Decision | Status |
| --- | --- |
| Keep the plan's panel split: 2 frames per side wall (vách hông), 4 back wall frames (vách hậu), 2 ceiling halves (trần), 3 decor blocks (khung trang trí) | DECIDED |
| Ship on one 48 x 40 and one 96 x 48 pallet. Don't split the decor blocks: a seam across the faceted front breaks the look rule, and a third pallet costs more than it saves | DECIDED |
| Thin floor inside an aluminium base band (viền chân); the band drops to a 20 mm threshold across the door only. Castors are a possible later accessory, not part of v2 | DECIDED |
| Aluminium frames, with the section depth set by the sound study's wall: 20 x 40 in the walls and in the ceiling | DECIDED |
| No plywood behind the ACP; frame members at 400 mm keep the ACP flat | DECIDED |
| Fast-assembly changes: factory subassemblies, captive bolts, tool-free clips on panel seams, felt pre-fitted (section 4) | DECIDED |
| Front: 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look). Door and fixed glass are carried by two people with suction lifters | DECIDED |
| Quiet build: the sound study's final stack with separate silencer boxes, 400 kg cap, 20 kg part limit and pallet layout kept | DECIDED |
| The inner skin and felt ship as separate clip-on inner leaves (the sound study's lining cassettes), one per panel, 19 kg or less, with the outside seams as planned | DECIDED |
| Ceiling fill carried on the back of the ceiling cassettes, so the ceiling panel stays at 20 kg or less (section 5) | DECIDED |
| Rejected: split decor blocks (B2), 5 bands per wall (C), full-height walls, castors in v2, no floor | DECIDED |

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
| BASE | 82.4 | 46.7 | -35.7 |
| WALL | 137.0 | 80.7 | -56.4 |
| FRONT | 142.0 | 111.2 | -30.8 |
| CEILING | 38.9 | 22.3 | -16.6 |
| LINING | 29.0 | 29.0 | 0.0 |
| AIR | 3.0 | 6.0 | 3.0 |
| ELECTRICAL | 3.0 | 7.1 | 4.1 |
| INTERIOR | 12.0 | 0.0 | -12.0 |
| **Total** | **447.4** | **303.0** | **-144.4** |

How the light build gets there, one change at a time:

| Step | Status | Change, kg | Running total, kg |
| --- | --- | ---: | ---: |
| v2 as planned (steel frames, 6 mm plywood, raised steel floor, 10 mm glass, table) | source + calculation |  | 447.4 |
| Remove the table; the pod ships empty | confirmed (Dee) | -12.0 | 435.4 |
| Thin floor inside an aluminium base band instead of the raised steel frame | DECIDED | -36.0 | 399.4 |
| Aluminium 20x20 frames instead of steel (walls, ceiling, decor) | DECIDED | -47.0 | 352.4 |
| No plywood behind the ACP; frame members at 400 mm to keep the ACP flat | DECIDED | -54.0 | 298.4 |
| 8 mm tempered glass instead of 10 mm | light build only; the decided build uses 10 mm acrylic | -17.1 | 281.3 |
| Add gaskets on every panel joint, sealed glazing profiles, door drop seal | plan requirement | 5.0 | 286.3 |
| Add 2 silenced vents and an occupancy sensor for automatic fans | plan requirement | 3.1 | 289.4 |
| Add light cavity fill (20 mm PET) in wall and ceiling bays | assumption (sound group sizes it) | 9.6 | 299.0 |
| Hold 4 kg for the later voice cockpit kit | Dee's scope addition | 4.0 | 303.0 |

Notes:
- Glass weights use the finished shapes from the STEP: door 2.08 m2, fixed panel 1.34 m2. Decor skins use the STEP's finished areas too (6.30 m2, against 7.67 m2 of cutting rectangles in the BOM).
- The ACP areal mass (3.8 kg/m2) is for a product with 0.3 mm skins, so it is likely conservative. Every 0.1 kg/m2 lighter ACP takes 2.2 kg off the pod.
- The colour of the decor cladding (yellow ACP in the plan's materials, black in the plan's pictures) is on the issue list. It does not change any weight.

### 1.3 Variants

One change at a time against the light build:

| Variant (one change to the light build) | Change, kg | Total, kg | Note |
| --- | ---: | ---: | --- |
| Front: smoked acrylic 8 mm (door and fixed panel) | -35.9 | 267.1 | Room uses an acrylic booth door; scratches more, needs a stiffer door frame or hinges rated for acrylic; sound check decides. |
| Front: smoked acrylic 10 mm | -27.7 | 275.2 | Stiffer door; same notes. |
| Front: 4+4 laminated acoustic glass | +2.8 | 305.7 | About the weight of 8 mm, quieter (sound group). |
| Front: 10 mm tempered glass (as v1) | +17.1 | 320.1 | Reference. |
| Walls and ceiling: foam-core sandwich (same ACP face, 25 mm foam, 0.5 mm aluminium inner skin) | +29.6 | 332.5 | Stiff and flat without studs; factory-bonded; fire behaviour of the core to check for the later US rules. |
| Walls and ceiling: aluminium honeycomb sandwich (same ACP face on a 10 mm honeycomb panel) | +47.9 | 350.9 | Heaviest of the light options here because the ACP face sits on a full honeycomb panel. |
| No floor at all (base band only) | -33.0 | 270.0 | Weakest for sound (open to the room floor). |
| Raised steel floor kept (plan) | +36.0 | 338.9 | Reference. |

The smoked acrylic front is the biggest single lever, but the decided build uses 4+4 laminated glass: acrylic needed an opaque band down the door, which breaks the look. The sandwich walls are heavier than the frame build here, because the frame build without plywood is already 6.2 kg/m2. Sandwich walls buy flatness and a second skin, not weight.

### 1.4 Every part against 20 kg

Light build: no part is over 20 kg except the glass (door 41.6 kg, fixed panel 26.9 kg at 8 mm). Over 20 kg in the light build: none. Over 20 kg as planned: F-DR 27.5 kg. With the felt pre-fitted, the light build's wall and ceiling panels weigh 11 to 14 kg. For the decided build see section 5.

<details><summary>Part list with weights, light build</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,500 x 1,145 x 38 | 2 | 10.6 | 21.2 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,500 x 1,145 x 38 | 2 | 10.6 | 21.2 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 8.8 | 17.5 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 8.8 | 17.5 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,500 x 1,212 x 38 | 2 | 11.2 | 22.3 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,462 x 1,145 x 9 | 4 | 3.1 | 12.4 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,462 x 1,212 x 9 | 2 | 3.3 | 6.6 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,462 x 1,212 x 15 | 2 | 16.5 | 33.0 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 200 | 1 | 10.5 | 10.5 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 200 | 1 | 19.1 | 19.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 200 | 1 | 7.4 | 7.4 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 3.2 | 3.2 |  | calculation |
|  | **Total** |  |  | 54 |  | **303.0** |  |  |

</details>

<details><summary>Part list with weights, as planned (option A)</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,500 x 1,145 x 38 | 2 | 18.5 | 37.0 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,500 x 1,145 x 38 | 2 | 18.5 | 37.0 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 15.3 | 30.7 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 15.3 | 30.7 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,500 x 1,212 x 38 | 2 | 19.5 | 38.9 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,462 x 1,145 x 9 | 4 | 3.1 | 12.4 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,462 x 1,212 x 9 | 2 | 3.3 | 6.6 |  | calculation |
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
| B-THRESH | BASE - FRONT EDGE TRIM / Ốp mép sàn trước | BASE | 1,917 x 204 x 3 | 1 | 1.5 | 1.5 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 200 | 1 | 15.3 | 15.3 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 200 | 1 | 27.5 | 27.5 | OVER 20 kg | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 200 | 1 | 11.0 | 11.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (10 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 10 | 1 | 52.0 | 52.0 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (10 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 10 | 1 | 33.6 | 33.6 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 2.6 | 2.6 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.0 | 3.0 |  | assumption |
| I-TABLE | INTERIOR - TABLE (v1), FLAT-PACKED / Bàn | INTERIOR | 1,000 x 600 x 120 | 1 | 12.0 | 12.0 |  | calculation |
| K-FIX | KIT - M6 BOLTS, RIVNUTS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 1.6 | 1.6 |  | calculation |
|  | **Total** |  |  | 59 |  | **447.4** |  |  |

</details>

## 2. Panel split options

All options use only standard pallets. On a 48 x 40 in pallet (1219 x 1016 mm), panels stand upright with their length along the 48 in side, at most about 6 ft loaded. On a 96 x 48 in pallet (2438 x 1219 mm), long pieces and glass lie flat. Freight density is gross weight over the pallet footprint times the loaded height. The LTL class depends on the NMFC item and, for density-rated items, on density, so this report gives densities and does not guess a class. B1, B2 and C below use the light build with the DECIDED fast-assembly changes; section 5 repeats B1 with the final walls.

| Option | What it is | Pod kg | Parts | M6 bolts + clips | Cable connectors | Pallets 48x40 + 96x48 | Shipped kg (gross) | Max loaded height mm | Density lb/ft3 | Assembly, min (2 people) | Person-hours |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | Plan as written | 447 | 59 | 134 + 0 | 3 | 1 + 1 | 550 | 1,646 | 7.8 | 193 | 6.4 |
| **B1** | Plan split, light build, fast assembly, 2 pallets (DECIDED) | 304 | 45 | 76 + 38 | 3 | 1 + 1 | 403 | 1,646 | 6.5 | 104 | 3.5 |
| **B2** | As B1, decor and base band split to fit 48x40 (rejected) | 307 | 49 | 92 + 38 | 3 | 2 + 1 | 432 | 1,806 | 4.9 | 113 | 3.8 |
| **C** | Horizontal bands, light build, fast assembly (rejected) | 318 | 57 | 76 + 98 | 6 | 1 + 1 | 417 | 1,646 | 4.8 | 124 | 4.1 |

- **A, plan as written.** Fits 2 pallets only if the raised floor frame ships as knock-down bars; welded as in v1 (2500 x 1703 mm per the v1 BOM, 55 kg), it fits no standard pallet. Heaviest option (447 kg). The right decor block is over 20 kg, and the floor boards need screws and a driver.
- **B1, DECIDED.** Panels, short base band pieces, floor panels and the felt strips go on the 48 x 40 (184 kg, 1,646 mm high). The decor blocks, the long base band pieces, the kit boxes and the glass go on the 96 x 48 (219 kg, 608 mm high). Its longest piece is 2,420 mm (95.3 in), under the 96 in length where most LTL carriers start overlength charges. One long pallet is needed anyway: the glass is 2011 and 2139 mm long.
- **B2, rejected.** Cutting the decor blocks and standing the base band up puts everything except the glass on 48 x 40 pallets. But it needs two of them, and the glass still takes the long pallet alone: 3 pallets, 432 kg gross. The cut also puts seams across the faceted front.
- **C, rejected.** Five stacked bands per wall (like Orangebox Air3) give light 5 to 6 kg parts. But they add 60 fixings, 3 extra visible seams per wall, 3 more cable connectors and more gasket to seal. With the plan's split, parts are already under 20 kg, so bands buy nothing.
- **Fewer, larger panels, rejected where the 20 kg limit bites.** A full-height side wall weighs 20 kg even without felt. A full-height back panel with felt pre-fitted weighs 20.7 kg. Both are over 20 kg.

<details><summary>Option A: part list, joints, pallets, assembly</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER / Vách hông - khung dưới | WALL | 1,500 x 1,145 x 38 | 2 | 18.5 | 37.0 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER / Vách hông - khung trên | WALL | 1,500 x 1,145 x 38 | 2 | 18.5 | 37.0 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 38 | 2 | 15.3 | 30.7 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 38 | 2 | 15.3 | 30.7 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING / Trần - nửa khung | CEILING | 1,500 x 1,212 x 38 | 2 | 19.5 | 38.9 |  | calculation |
| L-FELT-SIDE | LINING - PET FELT - SIDE / Tấm tiêu âm PET - vách hông | LINING | 1,462 x 1,145 x 9 | 4 | 3.1 | 12.4 |  | calculation |
| L-FELT-BACK | LINING - PET FELT - BACK / Tấm tiêu âm PET - vách hậu | LINING | 1,212 x 1,126 x 9 | 4 | 2.5 | 10.1 |  | calculation |
| L-FELT-CEIL | LINING - PET FELT - CEILING / Tấm tiêu âm PET - trần | LINING | 1,462 x 1,212 x 9 | 2 | 3.3 | 6.6 |  | calculation |
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
| B-THRESH | BASE - FRONT EDGE TRIM / Ốp mép sàn trước | BASE | 1,917 x 204 x 3 | 1 | 1.5 | 1.5 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 200 | 1 | 15.3 | 15.3 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 200 | 1 | 27.5 | 27.5 | OVER 20 kg | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 200 | 1 | 11.0 | 11.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (10 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 10 | 1 | 52.0 | 52.0 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (10 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 10 | 1 | 33.6 | 33.6 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 2.6 | 2.6 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.0 | 3.0 |  | assumption |
| I-TABLE | INTERIOR - TABLE (v1), FLAT-PACKED / Bàn | INTERIOR | 1,000 x 600 x 120 | 1 | 12.0 | 12.0 |  | calculation |
| K-FIX | KIT - M6 BOLTS, RIVNUTS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 1.6 | 1.6 |  | calculation |
|  | **Total** |  |  | 59 |  | **447.4** |  |  |

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
| [1: 48x40 in](out/pallets-A-1-48x40.svg) | 1,219 x 1,016 | 263 | 580 | 1,646 (64.8 in) | 72.0 | 8.1 | B-BOARD, B-RAIL-FL-06, B-RAIL-FL-07, B-RAIL-FL-08, C-HALF, L-FELT-BACK, L-FELT-CEIL, L-FELT-SIDE, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-A-2-96x48.svg) | 2,438 x 1,219 | 287 | 633 | 788 (31.0 in) | 82.7 | 7.7 | B-JOIST, B-RAIL-FL-01, B-RAIL-FL-02, B-RAIL-FL-03, B-RAIL-FL-04, B-RAIL-FL-05, B-THRESH, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, I-TABLE, KIT-CARTON |

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 20.0 | 0.0 | - |
| 2 | Raised frame: bars, corner brackets, joists, 6 feet; level | 15 | 32 | 0 | 24.2 | 24.2 | Corner bolts from above and inside before any wall stands on the frame. |
| 3 | 2 floor boards screwed to the joists (plan: screws, a second fastener and a driver) | 2 | 0 | 0 | 3.0 | 5.3 | From above, open. |
| 4 | Lower walls: back pair on its pins, then the two sides; bolts to the band, bolts at seam and corners | 4 | 25 | 0 | 6.0 | 12.5 | From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays. |
| 5 | Upper walls: back pair, then sides; bolts at horizontal seams, vertical seam and corners | 4 | 25 | 0 | 6.0 | 12.5 | As the lower walls; top fixings at 2.2 m need the step stool. |
| 6 | Ceiling halves lifted onto the walls from inside; fans and silenced vents from below | 2 | 24 | 0 | 5.5 | 12.0 | Upward from inside, ceiling felt (or its joint strips) not yet on; fans mount from below through their opening. |
| 7 | Decor blocks (skins on, factory-made): left door post, right, then top | 3 | 18 | 0 | 4.5 | 9.0 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 8 | Fixed glass into its sealed profiles (2 people, 2 suction lifters) | 1 | 4 | 0 | 12.8 | 2.0 | Profile frame bolted from inside; glass held by clip-in beads. |
| 9 | Door: hinges on the left decor post, pull, drop seal; adjust swing (2 people, 2 suction lifters) | 1 | 6 | 0 | 18.8 | 3.0 | Hinge bolts reachable with the door open 90 degrees. |
| 10 | Electrics: 3 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 1.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 11 | Felt lining: 10 panels pressed onto Velcro | 10 | 0 | 0 | 0.0 | 12.5 | Closes every bay: last. |
| 12 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 43 | 134 | 0 |  |  | **193 min (6.4 person-hours)** |

</details>

<details><summary>Option B1 (DECIDED), light build: part list, joints, pallets</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER WITH FELT / Vách hông - khung dưới | WALL | 1,500 x 1,145 x 47 | 2 | 13.0 | 26.0 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER WITH FELT / Vách hông - khung trên | WALL | 1,500 x 1,145 x 47 | 2 | 13.0 | 26.0 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER WITH FELT / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 47 | 2 | 10.7 | 21.4 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER WITH FELT / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 47 | 2 | 10.7 | 21.4 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,500 x 1,212 x 47 | 2 | 13.7 | 27.5 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 6.6 | 6.6 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,462 x 1,212 x 15 | 2 | 16.5 | 33.0 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 200 | 1 | 10.5 | 10.5 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 200 | 1 | 19.1 | 19.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 200 | 1 | 7.4 | 7.4 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 4.7 | 4.7 |  | calculation |
|  | **Total** |  |  | 45 |  | **304.4** |  |  |

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
| [1: 48x40 in](out/pallets-B1-1-48x40.svg) | 1,219 x 1,016 | 184 | 407 | 1,646 (64.8 in) | 72.0 | 5.6 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, C-HALF, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-B1-2-96x48.svg) | 2,438 x 1,219 | 219 | 483 | 608 (23.9 in) | 63.8 | 7.6 | B-BAND-BACK, B-BAND-SIDE, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-BOX-1, KIT-BOX-2 |

</details>

<details><summary>Option B2: part list, joints, pallets, assembly</summary>

| ID | Part (English / Vietnamese) | Assembly | Size mm | Qty | kg each | kg | 20 kg check | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| W-SIDE-LO | WALL - SIDE PANEL - LOWER WITH FELT / Vách hông - khung dưới | WALL | 1,500 x 1,145 x 47 | 2 | 13.0 | 26.0 |  | calculation |
| W-SIDE-UP | WALL - SIDE PANEL - UPPER WITH FELT / Vách hông - khung trên | WALL | 1,500 x 1,145 x 47 | 2 | 13.0 | 26.0 |  | calculation |
| W-BACK-LO | WALL - BACK PANEL - LOWER WITH FELT / Vách hậu - khung dưới | WALL | 1,212 x 1,126 x 47 | 2 | 10.7 | 21.4 |  | calculation |
| W-BACK-UP | WALL - BACK PANEL - UPPER WITH FELT / Vách hậu - khung trên | WALL | 1,212 x 1,126 x 47 | 2 | 10.7 | 21.4 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,500 x 1,212 x 47 | 2 | 13.7 | 27.5 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 6.6 | 6.6 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK (1/2) / Viền chân nhôm | BASE | 1,210 x 100 x 40 | 2 | 1.9 | 3.8 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,462 x 1,212 x 15 | 2 | 16.5 | 33.0 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT (half) / Khung trang trí - khối trái (nửa) | FRONT | 1,145 x 278 x 200 | 2 | 5.6 | 11.1 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT (half) / Khung trang trí - khối phải (nửa) | FRONT | 1,145 x 1,016 x 200 | 2 | 9.8 | 19.7 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP (half) / Khung trang trí - khối trên (nửa) | FRONT | 848 x 280 x 200 | 2 | 4.0 | 8.0 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 4.9 | 4.9 |  | calculation |
|  | **Total** |  |  | 49 |  | **306.6** |  |  |

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
| [1: 48x40 in](out/pallets-B2-1-48x40.svg) | 1,219 x 1,016 | 155 | 342 | 1,646 (64.8 in) | 72.0 | 4.7 | C-HALF, F-DL, F-DR, F-DT, W-BACK-LO, W-SIDE-LO, W-SIDE-UP |
| [2: 48x40 in](out/pallets-B2-2-48x40.svg) | 1,219 x 1,016 | 103 | 227 | 1,806 (71.1 in) | 79.0 | 2.9 | B-BAND-BACK, B-BAND-FRONT-L, B-BAND-FRONT-R, B-BAND-SIDE, B-FLOOR, B-THRESH, W-BACK-LO, W-BACK-UP |
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
| W-SIDE-BAND | WALL - SIDE BAND WITH FELT / Vách hông - băng | WALL | 1,500 x 458 x 47 | 10 | 5.5 | 55.3 |  | calculation |
| W-BACK-BAND | WALL - BACK BAND WITH FELT / Vách hậu - băng | WALL | 1,212 x 450 x 47 | 10 | 4.5 | 45.3 |  | calculation |
| C-HALF | CEILING - HALF PANEL WITH FAN OPENING WITH FELT / Trần - nửa khung | CEILING | 1,500 x 1,212 x 47 | 2 | 13.7 | 27.5 |  | calculation |
| L-STRIP | LINING - LOOSE FELT STRIPS OVER JOINTS / Dải tiêu âm che mối nối | LINING | 1,500 x 300 x 60 | 1 | 10.5 | 10.5 |  | calculation |
| B-BAND-BACK | BASE - BASE BAND PIECE 100x40 - BACK / Viền chân nhôm | BASE | 2,420 x 100 x 40 | 1 | 3.6 | 3.6 |  | calculation |
| B-BAND-SIDE | BASE - BASE BAND PIECE 100x40 - SIDE / Viền chân nhôm | BASE | 1,660 x 100 x 40 | 2 | 2.4 | 4.9 |  | calculation |
| B-BAND-FRONT-L | BASE - BASE BAND PIECE 100x40 - FRONT-L / Viền chân nhôm | BASE | 300 x 100 x 40 | 1 | 0.4 | 0.4 |  | calculation |
| B-BAND-FRONT-R | BASE - BASE BAND PIECE 100x40 - FRONT-R / Viền chân nhôm | BASE | 1,050 x 100 x 40 | 1 | 1.5 | 1.5 |  | calculation |
| B-KEY | BASE - CORNER KEY / Ke góc đế | BASE | 120 x 80 x 40 | 6 | 0.1 | 0.9 |  | assumption |
| B-GLIDE | BASE - LEVELLING GLIDE (hex from above) / Chân chỉnh cao | BASE | 50 x 50 x 40 | 8 | 0.1 | 1.2 |  | assumption |
| B-THRESH | BASE - DOOR THRESHOLD, LOW / Ngưỡng cửa thấp | BASE | 1,176 x 60 x 20 | 1 | 1.2 | 1.2 |  | assumption |
| B-FLOOR | BASE - THIN FLOOR PANEL 15 mm / Tấm sàn mỏng | BASE | 1,462 x 1,212 x 15 | 2 | 16.5 | 33.0 |  | calculation |
| F-DL | FRONT - DECOR BLOCK - LEFT / Khung trang trí - khối trái | FRONT | 2,290 x 278 x 200 | 1 | 10.5 | 10.5 |  | calculation |
| F-DR | FRONT - DECOR BLOCK - RIGHT / Khung trang trí - khối phải | FRONT | 2,290 x 1,016 x 200 | 1 | 19.1 | 19.1 |  | calculation |
| F-DT | FRONT - DECOR BLOCK - TOP / Khung trang trí - khối trên | FRONT | 1,697 x 280 x 200 | 1 | 7.4 | 7.4 |  | calculation |
| F-GLASS-DOOR | FRONT - GLASS DOOR (8 mm tempered glass) / Cửa kính | FRONT | 2,011 x 1,176 x 8 | 1 | 41.6 | 41.6 | glass (exempt) | calculation |
| F-GLASS-FIXED | FRONT - FIXED GLASS (8 mm tempered glass) / Vách kính cố định | FRONT | 2,139 x 724 x 8 | 1 | 26.9 | 26.9 | glass (exempt) | calculation |
| F-HW | FRONT - DOOR AND GLAZING HARDWARE KIT / Phụ kiện cửa và kính | FRONT | 600 x 400 x 150 | 1 | 5.8 | 5.8 |  | assumption |
| A-FAN | AIR - CEILING FAN (Panasonic FV-15AUL1 per plan) / Quạt thông gió | AIR | 300 x 300 x 200 | 2 | 1.5 | 3.0 |  | unverified |
| A-SILENCER | AIR - SILENCED VENT BOX / Hộp tiêu âm cửa gió | AIR | 450 x 300 x 120 | 2 | 1.5 | 3.0 |  | assumption |
| E-KIT | ELECTRICAL - SWITCHES, LIGHTS, HARNESS / Bộ điện: công tắc, đèn, dây | ELECTRICAL | 600 x 400 x 200 | 1 | 3.1 | 3.1 |  | assumption |
| E-VOICE-RESERVE | ELECTRICAL - VOICE COCKPIT KIT RESERVE (later) / Dự phòng bộ voice cockpit | ELECTRICAL | - | 1 | 4.0 | 4.0 |  | assumption |
| K-FIX | KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS / Bộ bu lông M6, gioăng | WALL | 400 x 300 x 150 | 1 | 8.6 | 8.6 |  | calculation |
|  | **Total** |  |  | 57 |  | **318.1** |  |  |

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
| [1: 48x40 in](out/pallets-C-1-48x40.svg) | 1,219 x 1,016 | 145 | 319 | 1,646 (64.8 in) | 72.0 | 4.4 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, W-BACK-BAND, W-SIDE-BAND |
| [2: 96x48 in](out/pallets-C-2-96x48.svg) | 2,438 x 1,219 | 273 | 601 | 1,132 (44.6 in) | 118.8 | 5.1 | B-BAND-BACK, B-BAND-SIDE, C-HALF, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-CARTON, W-BACK-BAND |

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
| Raised steel floor (plan as written) | 82.4 | +35.7 | 125 | Closed box: boards over a 100 mm cavity; seal the board joints and perimeter. | Best: the welded or bolted frame sets square and level; walls bolt to it. | 6 M10 feet under the frame; needs a spanner unless the feet adjust from above. | Under the floor, easy. | Longest: 6 frame bars, 2 joists, 4 bolted corners, 6 feet, then 2 boards screwed to the joists (a second fastener type and tool). | Same as v1. | calculation |
| Thin floor inside an aluminium base band (DECIDED) | 46.7 | +0.0 | 21 | Closed box: floor panels on a 3 mm seal mat, gasket to the base band; the room slab adds mass under it. | Good: the aluminium base band with corner keys sets square; floor panels float inside it. | 8 glides adjusted from above with the same hex key; floor panels follow the room floor and carry no walls. | Inside the back wall cavity and along the base band channel. | Quick: 4 rails and 6 corner keys, level, drop in 2 floor panels. | Base band unchanged except across the door, where it becomes a low threshold. | calculation |
| No floor (base band only) | 13.7 | -33.0 | 0 | Open box: sound and air leak under the walls into the room floor; floorless pods post the weakest numbers (market study). | As the thin floor (same base band). | As the thin floor. | Base band channel only. | Quickest: 4 rails and 6 corner keys, level. | As the thin floor. | calculation |
| Castor platform (optional, Lead's request) | 67.1 | +20.4 | 93 | Closed box like the raised floor, but the gap under the pod needs a skirt or drop seal when parked. | Needs a stiffer platform: the pod racks while rolling, and the glass door can go out of line. | Castors do not level; 4 parking feet are added. | Under the platform; the power cord must be long and loose enough to move the pod. | Like the raised floor (knock-down platform), plus 6 castors. | Base band hides the castors if the frame stays 100 mm; a ramp is needed at the door. | assumption |

DECIDED: the thin floor. It is 36 kg lighter than the raised steel floor, closes the box for sound, and cuts the step from 125 mm to 21 mm. The room inside gets 104 mm taller. No floor saves a further 33 kg, but leaves the box open to the room floor, which the market study says leaks most. Castors would let an assembled pod roll around the office. They would cost about 20 kg over the thin floor, a step of about 93 mm with a ramp, a skirt to close the gap when parked, and a stiffer platform so the door stays in line while rolling. DECIDED: a possible later accessory, not part of v2.

## 4. Assembly by 2 people

Tool: one 5 mm T-handle hex key (M6 socket-head bolts into rivnuts; glides adjust from above with the same key). Handling aids, not tools: a small step stool and 2 suction lifters for the glass. A small step stool is needed for the ceiling and the top fixings; it is not a tool. Every bolt and clip is reached from inside the pod, through open frame bays or behind the loose felt strip over each joint. The strips, or in the decided build the lining cassettes, go on last.

Before and after the DECIDED fast-assembly changes, on the light build. Each row adds one change to the rows above it, with the same time model:

| Change (each added to the ones above) | Status | Saves, min | Assembly after it, min | M6 bolts | Cam or clip connectors |
| --- | --- | ---: | ---: | ---: | ---: |
| Option B1 as first studied (light build, everything bolted, felt on site) | - |  | 166 | 114 | 0 |
| Factory subassemblies: decor blocks with skins on (already), door hinges and pull fitted in the factory so the door lifts onto its pins, fixed glass pre-glazed in its profile frame | DECIDED | 22 | 145 | 114 | 0 |
| Captive M6 bolts, already started in their panels, that can't be dropped | DECIDED | 13 | 132 | 114 | 0 |
| Tool-free cam or clip connectors on every panel-to-panel seam; panels sit on pins or hooks and hold themselves (bolts stay where loads go to the base, ceiling, decor and hinges) | DECIDED | 12 | 120 | 76 | 38 |
| Felt pre-fitted on the panels; only a loose strip over each joint goes on site | DECIDED | 4 | 116 | 76 | 38 |
| Pallets packed in assembly order, parts numbered | packaging, no design change | 12 | 104 | 76 | 38 |

The full-height back wall panel (fewer, larger panels) was also tried. With the felt pre-fitted it weighs 20.7 kg, over the limit, so it is not used.

What remains is mostly work that does not shrink with fewer parts: unpacking, levelling, setting the glass and the door, and testing the electrics. The 1-hour target needs that work timed on the prototype, and possibly more done in the factory. Section 5 gives the step-by-step sequence and access check for the decided build.

Benchmark: Room S needs 4 people for 3 to 5 hours (12 to 20 person-hours), and hushMeet 2 installers for 2.5 to 3 hours (market study). The decided build takes 4.0 person-hours.

## 5. The decided build: final wall stack (re-check)

The sound study's final stack (DECIDED): ACP 3 mm on a 20 x 40 aluminium frame at 400 mm with 40 mm PET fill, then a floating lining cassette: a 0.5 mm steel tray, 25 mm deep, with 9 mm felt across its face. That makes 81 mm and 13.1 kg/m2 in the sound study. The ceiling now uses the same 20 x 40 frame (was 20 x 100), and the silencers are separate boxes. The front is frameless 4+4 laminated glass. The sound study puts the pod at about 400 kg and 23.8 dB.

This study builds it on the B1 layout. The outer panel (ACP, frame and fill) and its cassette are separate parts; the cassette is the DECIDED clip-on inner leaf. The outside size stays the same; the inside narrows to 2,338 mm. The wall here comes to 14.0 kg/m2 with clips and tray returns (the sound study: 13.1). The fans and silencer boxes are the sound study's: two 5 kg inline fans and two 3.5 kg silencer boxes. Its door edge seals, base seal and cable grommets are counted too.

Result: **412 kg**, 0 parts over 20 kg except the glass, heaviest F-DR at 19.1 kg, 1 + 1 pallets, 511 kg gross, 1,646 mm at most, assembly 121 min.

- **Glass.** Door 43.3 kg and fixed panel 28.0 kg in 4+4 laminated. They ride flat on top of the long pallet in their timber frame, with nothing on them. On site, each is carried by two people with 2 suction lifters. The door's hinges and pull are fitted in the factory, so it lifts straight onto its hinge pins. The fixed glass's profiles sit hidden in the decor and base, so the front stays frameless like v1.
- **Decor fill.** The sound study fills the decor blocks with PET (4.0 kg). Inside the right decor block it would make that block 21.2 kg, so the fill ships loose in the kit and is pushed into each block's open back just before it is mounted.
- **Ceiling (DECIDED).** The fill still rides on the back of the ceiling cassette. With 40 mm frames, both ceiling parts are well under 20 kg either way.
- **Pallets.** The 48 x 40 carries the wall and ceiling panels, the wall cassettes, the floor panels and the short band pieces (253 kg, 1,646 mm). The long pallet carries the decor blocks, the long band pieces, the silencer boxes, the kit, the ceiling cassettes that don't fit the upright stack, and the glass on top (258 kg, 1,056 mm). Still 1 + 1.

Wall and ceiling parts of the decided build:

| Part | Size mm | Qty | kg each | 20 kg check |
| --- | --- | ---: | ---: | --- |
| W-SIDE-LO: WALL - SIDE PANEL - LOWER (outer: ACP + frame + fill) | 1,500 x 1,145 x 43 | 2 | 13.2 |  |
| L-CASS-SIDE-LO: LINING - CASSETTE FOR W-SIDE-LO (steel tray + felt) | 1,419 x 1,145 x 34 | 2 | 10.9 |  |
| W-SIDE-UP: WALL - SIDE PANEL - UPPER (outer: ACP + frame + fill) | 1,500 x 1,145 x 43 | 2 | 13.2 |  |
| L-CASS-SIDE-UP: LINING - CASSETTE FOR W-SIDE-UP (steel tray + felt) | 1,419 x 1,145 x 34 | 2 | 10.9 |  |
| W-BACK-LO: WALL - BACK PANEL - LOWER (outer: ACP + frame + fill) | 1,169 x 1,104 x 43 | 2 | 10.0 |  |
| L-CASS-BACK-LO: LINING - CASSETTE FOR W-BACK-LO (steel tray + felt) | 1,169 x 1,104 x 34 | 2 | 8.7 |  |
| W-BACK-UP: WALL - BACK PANEL - UPPER (outer: ACP + frame + fill) | 1,169 x 1,104 x 43 | 2 | 10.0 |  |
| L-CASS-BACK-UP: LINING - CASSETTE FOR W-BACK-UP (steel tray + felt) | 1,169 x 1,104 x 34 | 2 | 8.7 |  |
| C-HALF: CEILING - HALF PANEL WITH FAN OPENING (outer: ACP + frame) | 1,500 x 1,169 x 43 | 2 | 11.2 |  |
| L-CASS-HALF: LINING - CASSETTE FOR C-HALF (steel tray + felt + ceiling fill) | 1,419 x 1,169 x 74 | 2 | 13.2 |  |

| Pallet (diagram) | Deck mm | Gross kg | Gross lb | Loaded height mm | ft3 | lb/ft3 | Carries |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1: 48x40 in](out/pallets-B1F-1-48x40.svg) | 1,219 x 1,016 | 253 | 558 | 1,646 (64.8 in) | 72.0 | 7.8 | B-BAND-FRONT-L, B-BAND-FRONT-R, B-FLOOR, B-THRESH, C-HALF, L-CASS-BACK-LO, L-CASS-BACK-UP, L-CASS-SIDE-LO, L-CASS-SIDE-UP, W-BACK-LO, W-BACK-UP, W-SIDE-LO, W-SIDE-UP |
| [2: 96x48 in](out/pallets-B1F-2-96x48.svg) | 2,438 x 1,219 | 258 | 569 | 1,056 (41.6 in) | 110.8 | 5.1 | A-SILENCER, B-BAND-BACK, B-BAND-SIDE, F-DL, F-DR, F-DT, F-GLASS-DOOR, F-GLASS-FIXED, KIT-CARTON, L-CASS-HALF |

Step by step, with the access check. A step fails the check if a part fitted earlier blocks its fixings; none does in this order. The check is at layout level and is repeated on the CAD in Milestone 2.

| # | Step | Lifts | M6 bolts | Clips | 2-person min | 1-person min (shared) | Access check |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Unpack, check parts against the label list, stand the glass safely | 0 | 0 | 0 | 10.0 | 0.0 | - |
| 2 | Base band: 4 pieces and corner keys on 8 glides; level from above | 5 | 12 | 0 | 13.9 | 5.1 | Corner keys from above and inside; closed later by the wall panels, so bolted first. |
| 3 | Seal mat and 2 thin floor panels dropped inside the band (no fixings) | 2 | 0 | 0 | 2.2 | 0.0 | - |
| 4 | Lower walls: back pair on its pins, then the two sides; bolts to the band, cam or clip connectors at seam and corners | 4 | 16 | 9 | 1.3 | 9.3 | From inside through open frame bays, or behind the loose felt strip over each joint; hex key swings in the 1.2 m bays. |
| 5 | Upper walls: back pair, then sides; cam or clip connectors at horizontal seams, vertical seam and corners | 4 | 0 | 25 | 1.3 | 7.2 | As the lower walls; top fixings at 2.2 m need the step stool. |
| 6 | Ceiling halves lifted onto the walls from inside; fans and silenced vents from below | 2 | 20 | 4 | 4.0 | 8.2 | Upward from inside, ceiling felt (or its joint strips) not yet on; fans mount from below through their opening. |
| 7 | Decor blocks (skins on, factory-made): PET fill pushed into each open back, then left door post, right, then top | 4 | 18 | 0 | 3.6 | 7.7 | Through the front frame members of the side walls and ceiling from inside, behind the loose felt strips. |
| 8 | Fixed glass in its factory profile frame: set and fix (2 people, 2 suction lifters) | 1 | 4 | 0 | 5.8 | 1.2 | Profile frame bolted from inside; glass held by clip-in beads. |
| 9 | Door: hinges and pull fitted in the factory; lift onto the hinge pins, fit drop seal, adjust (2 people, 2 suction lifters) | 1 | 6 | 0 | 6.8 | 1.8 | Hinge bolts reachable with the door open 90 degrees. |
| 10 | Electrics: 3 plug-in connectors at panel seams, power in, test fans and lights | 0 | 0 | 0 | 10.0 | 1.0 | Connectors sit in the open bays, or behind the loose strip, next to each seam. |
| 11 | 10 lining cassettes (steel tray + felt) clipped on from inside, ceiling ones from below | 10 | 0 | 0 | 6.7 | 17.5 | Close every bay and joint: last. Joints stay reachable until then. |
| 12 | Threshold, final check of door swing and seals, clean | 1 | 0 | 0 | 10.0 | 0.0 | - |
|  | **Elapsed for 2 people, with 15 % for hand-offs** | 34 | 76 | 38 |  |  | **121 min (4.0 person-hours)** |

<details><summary>Sensitivity: the same layout at 380 and 400 kg with an even added mass (before the final stack was known)</summary>

It adds an even mass to the walls (with or without the ceiling) until the pod reaches the target, with the frames deeper by 20 or 40 mm. Mass inside the plan's panels breaks the 20 kg limit (side panels 24.7 kg, ceiling halves 25.7 kg at 380 kg); on separate inner leaves every part stays at 20 kg or less up to the 400 kg cap.

| Pod kg | Walls thicker by | Sound mass on | Layout | Added kg/m2 | Heaviest part, kg (not glass) | Parts over 20 kg | Pallets 48x40 + 96x48 | Heaviest 48x40 / 96x48 gross kg | Max height mm | Assembly min |
| ---: | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 380 | +20 mm | walls and ceiling | plan split, sound mass inside the panels | 5.4 | C-HALF 25.7 | 3 | 1 + 1 | 288 / 191 | 1,646 | 108 |
| 380 | +20 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 5.0 | C-HALF 25.0 | 1 | 1 + 1 | 223 / 256 | 1,646 | 113 |
| 380 | +20 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 5.2 | F-DR 19.1 | 0 | 1 + 1 | 294 / 185 | 1,646 | 118 |
| 380 | +20 mm | walls only | plan split, sound mass inside the panels | 7.0 | W-SIDE-LO 27.4 | 4 | 1 + 1 | 288 / 191 | 1,646 | 108 |
| 380 | +20 mm | walls only | 3 rows per wall, sound mass inside the panels | 6.5 | F-DR 19.1 | 0 | 1 + 1 | 240 / 239 | 1,646 | 113 |
| 380 | +20 mm | walls only | plan split, sound mass on separate inner leaves | 6.7 | F-DR 19.1 | 0 | 1 + 1 | 294 / 185 | 1,646 | 118 |
| 380 | +40 mm | walls and ceiling | plan split, sound mass inside the panels | 4.2 | C-HALF 25.6 | 3 | 1 + 1 | 262 / 217 | 1,646 | 108 |
| 380 | +40 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 3.7 | C-HALF 24.8 | 1 | 1 + 1 | 198 / 281 | 1,646 | 113 |
| 380 | +40 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 4.0 | F-DR 19.1 | 0 | 1 + 1 | 263 / 216 | 1,646 | 121 |
| 380 | +40 mm | walls only | plan split, sound mass inside the panels | 5.4 | W-SIDE-LO 27.2 | 4 | 1 + 1 | 270 / 209 | 1,646 | 108 |
| 380 | +40 mm | walls only | 3 rows per wall, sound mass inside the panels | 4.8 | F-DR 19.1 | 0 | 1 + 1 | 208 / 271 | 1,646 | 113 |
| 380 | +40 mm | walls only | plan split, sound mass on separate inner leaves | 5.2 | F-DR 19.1 | 0 | 1 + 1 | 263 / 216 | 1,646 | 121 |
| 400 | +20 mm | walls and ceiling | plan split, sound mass inside the panels | 6.7 | C-HALF 27.9 | 5 | 1 + 1 | 308 / 191 | 1,646 | 108 |
| 400 | +20 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 6.3 | C-HALF 27.2 | 1 | 1 + 1 | 237 / 262 | 1,646 | 113 |
| 400 | +20 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 6.5 | F-DR 19.1 | 0 | 1 + 1 | 314 / 185 | 1,646 | 119 |
| 400 | +20 mm | walls only | plan split, sound mass inside the panels | 8.6 | W-SIDE-LO 30.2 | 4 | 1 + 1 | 308 / 191 | 1,646 | 108 |
| 400 | +20 mm | walls only | 3 rows per wall, sound mass inside the panels | 8.1 | W-SIDE-ROW 19.9 | 0 | 1 + 1 | 258 / 241 | 1,646 | 115 |
| 400 | +20 mm | walls only | plan split, sound mass on separate inner leaves | 8.4 | F-DR 19.1 | 0 | 1 + 1 | 314 / 185 | 1,646 | 120 |
| 400 | +40 mm | walls and ceiling | plan split, sound mass inside the panels | 5.5 | C-HALF 27.9 | 5 | 1 + 1 | 280 / 219 | 1,646 | 108 |
| 400 | +40 mm | walls and ceiling | 3 rows per wall, sound mass inside the panels | 5.0 | C-HALF 27.0 | 1 | 1 + 1 | 210 / 289 | 1,646 | 113 |
| 400 | +40 mm | walls and ceiling | plan split, sound mass on separate inner leaves | 5.3 | F-DR 19.1 | 0 | 1 + 1 | 271 / 228 | 1,646 | 121 |
| 400 | +40 mm | walls only | plan split, sound mass inside the panels | 7.1 | W-SIDE-LO 30.0 | 4 | 1 + 1 | 290 / 209 | 1,646 | 108 |
| 400 | +40 mm | walls only | 3 rows per wall, sound mass inside the panels | 6.5 | W-SIDE-ROW 19.8 | 0 | 1 + 1 | 224 / 275 | 1,646 | 115 |
| 400 | +40 mm | walls only | plan split, sound mass on separate inner leaves | 6.9 | F-DR 19.1 | 0 | 1 + 1 | 271 / 228 | 1,646 | 122 |

</details>

## 6. Doorway check

Every part must pass a 914 x 2032 mm (36 x 80 in) doorway. A part is carried on edge, with its longest side along the corridor. It passes if its thickness plus 40 mm of hand room each side fits the width, and its middle dimension fits the height. It is also checked against 813 mm, the minimum clear width of a door under the ADA. Failures: 0.

| Part | Size mm (long x mid x thin) | kg | Width needed on edge, mm | 914 x 2032 doorway | 813 mm clear (ADA) |
| --- | --- | ---: | ---: | --- | --- |
| W-SIDE-LO | 1,500 x 1,145 x 47 | 13.0 | 127 | passes | passes |
| W-SIDE-UP | 1,500 x 1,145 x 47 | 13.0 | 127 | passes | passes |
| W-BACK-LO | 1,212 x 1,126 x 47 | 10.7 | 127 | passes | passes |
| W-BACK-UP | 1,212 x 1,126 x 47 | 10.7 | 127 | passes | passes |
| C-HALF | 1,500 x 1,212 x 47 | 13.7 | 127 | passes | passes |
| L-STRIP | 1,500 x 300 x 60 | 6.6 | 140 | passes | passes |
| B-BAND-BACK | 2,420 x 100 x 40 | 3.6 | 120 | passes | passes |
| B-BAND-SIDE | 1,660 x 100 x 40 | 2.4 | 120 | passes | passes |
| B-BAND-FRONT-L | 300 x 100 x 40 | 0.4 | 120 | passes | passes |
| B-BAND-FRONT-R | 1,050 x 100 x 40 | 1.5 | 120 | passes | passes |
| B-KEY | 120 x 80 x 40 | 0.1 | 120 | passes | passes |
| B-GLIDE | 50 x 50 x 40 | 0.1 | 120 | passes | passes |
| B-THRESH | 1,176 x 60 x 20 | 1.2 | 100 | passes | passes |
| B-FLOOR | 1,462 x 1,212 x 15 | 16.5 | 95 | passes | passes |
| F-DL | 2,290 x 278 x 200 | 10.5 | 280 | passes | passes |
| F-DR | 2,290 x 1,016 x 200 | 19.1 | 280 | passes | passes |
| F-DT | 1,697 x 280 x 200 | 7.4 | 280 | passes | passes |
| F-GLASS-DOOR | 2,011 x 1,176 x 8 | 41.6 | 88 | passes | passes |
| F-GLASS-FIXED | 2,139 x 724 x 8 | 26.9 | 88 | passes | passes |
| F-HW | 600 x 400 x 150 | 5.8 | 230 | passes | passes |
| A-FAN | 300 x 300 x 200 | 1.5 | 280 | passes | passes |
| A-SILENCER | 450 x 300 x 120 | 1.5 | 200 | passes | passes |
| E-KIT | 600 x 400 x 200 | 3.1 | 280 | passes | passes |
| K-FIX | 400 x 300 x 150 | 4.7 | 230 | passes | passes |
| B-RAIL-FL-01 | 2,400 x 100 x 50 | 11.0 | 130 | passes | passes |
| B-RAIL-FL-02 | 2,020 x 100 x 50 | 9.3 | 130 | passes | passes |
| B-RAIL-FL-03 | 1,370 x 100 x 50 | 6.3 | 130 | passes | passes |
| B-RAIL-FL-04 | 269 x 100 x 50 | 1.2 | 130 | passes | passes |
| B-RAIL-FL-05 | 212 x 100 x 50 | 1.0 | 130 | passes | passes |
| B-RAIL-FL-06 | 150 x 100 x 50 | 0.7 | 130 | passes | passes |
| B-RAIL-FL-07 | 124 x 100 x 50 | 0.6 | 130 | passes | passes |
| B-RAIL-FL-08 | 100 x 76 x 50 | 0.3 | 130 | passes | passes |
| B-JOIST | 2,400 x 60 x 30 | 4.6 | 110 | passes | passes |
| B-BOARD | 1,428 x 1,184 x 15 | 15.2 | 95 | passes | passes |
| I-TABLE | 1,000 x 600 x 120 | 12.0 | 200 | passes | passes |

Corridor corners: the longest piece (2,420 mm) must also turn corners carried flat. The longest thin part that turns a 90-degree corner is 3,394 mm between two 1200 mm corridors, and 2,980 mm between a 1200 mm corridor and a 914 mm one, so every part passes.

## 7. Hooks for the voice cockpit kit (later)

Reserve now; don't design the kit (mic array, speakers, screen, status light).

- **Mounting points.** M6 rivnuts in the frame members, placed in the CAD at Milestone 2: a 100 x 100 mm pattern on the back wall centre for a screen at seated eye height; 4 points on a ceiling-half frame for a mic array and speaker plate; 2 behind the top decor block for a status light seen from outside. Each point gets a matching hole in the cassette in front of it.
- **Cable path.** One vertical cable channel with a pull cord in the back wall bay that holds the switches. It runs from the base band (power inlet) to the ceiling. It crosses the same 3 seams as the main harness, so the seam connectors get spare pins instead of new crossings; the bands option would have needed 6 crossings. The channel runs in the outer frame's cavity, behind the cassette.
- **Power.** Hold 60 W for the kit on its own fused circuit from the power inlet, and add it to the electrical group's power budget next to the fans and lights.
- **Weight.** 4 kg is already held in the weight budget.

## 8. Open items and issues found

| ID | Item | Status | Who |
| --- | --- | --- | --- |
| LS-01 | 412 kg here against about 400 kg in the sound study, against a 400 kg cap: settle from the master BOM out of the CAD, with real clip and ACP weights | open | Milestone 2 |
| LS-02 | 400 mm frame pitch and full-face bond keep the ACP flat without plywood; prove on the early wall sample | PLANNED | Prototype team |
| LS-03 | Tool-free cam or clip connector and captive bolt: real part numbers, loads and pull-out on the aluminium frame | open | Hardware group |
| LS-04 | Cassette clips: part numbers, and how the cassette floats (no stud bridge) while it carries a 19 kg leaf | open | Hardware group |
| LS-05 | Hinges for a frameless 4+4 laminated door of about 43 kg, fitted in the factory, with the door lifting onto its pins | open | Hardware group |
| LS-06 | The plan uses code VT03 for both the PET felt and the 50 x 100 steel tube | issue | Control pack |
| LS-07 | v1 BOM 9 mm boards vs 15 mm in the drawings and STEP (already listed by the control pack) | issue | Control pack |
| LS-08 | Panasonic FV-15AUL1 weight not published on the pages read; 1.5 kg assumed | unverified | Hardware group |
| LS-09 | Tube wall thicknesses assumed (20 x 20 steel 1.2 mm, aluminium 1.5 mm); the plan gives none | assumption | Hardware group |
| LS-10 | Bolt counts use a 400 mm pitch only for counting; the joint register sets the real pitch from loads | assumption | Milestone 2 |
| LS-11 | Assembly times are assumptions until the timed prototype trial | PLANNED | Prototype team |
| LS-12 | Decor cladding colour (yellow in the materials list, black in the plan's pictures); no weight effect | issue | Control pack |
| LS-13 | Room floor flatness must stay within the glides' adjustment range; check on site before install | assumption | Install guide |
| LS-14 | The upright stack on the 48 x 40 does not fill its depth: centre it and strap through the deck, or put the kit boxes beside it | note | Packaging |

## 9. How to reproduce

From this folder, with Python 3.10+ and openpyxl:

```
python3 scripts/run_all.py           # writes report.md, out/*.csv and out/*.svg
python3 scripts/run_all.py --check   # rebuilds in memory; fails if anything differs
```

The STEP cross-check data (`data/v1_step_solids.csv`) comes from `scripts/step_crosscheck.py`, which reads the v1 STEP with cadquery-ocp in a separate virtualenv (see the script header). Unit note: 1 lb = 0.4536 kg; imperial values are reference data for US freight only.

## 10. Inputs, status and sources

| Name | Value | Unit | Status | Source | Note |
| --- | ---: | --- | --- | --- | --- |
| pod_w | 2500 | mm | confirmed | S04 | overall width X |
| pod_d | 1700 | mm | confirmed | S04 | overall depth Y |
| pod_h | 2400 | mm | confirmed | S04 | overall height Z |
| decor_depth | 200 | mm | confirmed | S04 | front decor frame depth |
| wall_depth | 1500 | mm | confirmed | S04 | side wall depth = 1700 - 200 |
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
| acp3_kgm2 | 3.8 | kg/m2 | source | S10 | 3 mm ACP; local ACP with thinner skins is lighter (conservative) |
| pet9_kgm2 | 1.8 | kg/m2 | source | S11 | 9 mm PET felt |
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
| stud_pitch_acp | 400 | mm | assumption |  | max spacing when ACP is bonded to the frame without plywood, to keep it flat (oil-canning risk) |
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
| voice_kit_kg | 4 | kg | assumption |  | reserve for the later voice cockpit kit: mic array, speakers, screen, status light |
| voice_kit_w | 60 | W | assumption |  | power reserve for the voice cockpit kit |
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
| strip_w | 150 | mm | assumption |  | loose felt strip over each joint, so the joint stays reachable |
| frame_depth | 20 | mm | source | S04 | wall frame tube depth (20x20); the quiet build deepens it |
| quiet_total | 380 | kg | confirmed | S20 | PM ruling from the Hardware Engineer's sound curve |
| hw_380_total | 377 | kg | source | S20 | Hardware Engineer's best build within a 380 kg budget |
| hw_380_dsa | 22.5 | dB | source | S20 | its central D_S,A estimate |
| quiet_cap | 400 | kg | confirmed |  | Lead's ruling: heavier walls allowed up to 400 kg in total |
| rho_mass_layer | 1600 | kg/m3 | assumption |  | dense sound layer (MLV-like) used only to size the inner leaf thickness |
| leaf_clip_kgm2 | 0.6 | kg/m2 | assumption |  | clip rail and clips of an inner leaf |
| ceil_t | 0 | mm | assumption |  | ceiling thickness; 0 means the same as the walls |
| final_wall_t | 81 | mm | source | S21 | final wall: outer panel 3 + 40, cassette 25 + 9, 4 mm gaps |
| final_ceil_t | 81 | mm | calculation | S22 | 40 mm ceiling frames: the same 81 mm stack as the walls |
| final_wall_depth | 40 | mm | source | S21 | 20x40 aluminium wall frame |
| final_ceil_depth | 40 | mm | source | S22 | 20x40 aluminium ceiling frame (was 20x100) |
| final_kgm2_hw | 13.1 | kg/m2 | source | S21 | the sound study's wall mass with frame, fill and cassette |
| fill_pet_kgm3 | 32 | kg/m3 | source | S20 | PET cavity fill (the sound study's fill row) |
| tray_t | 0.5 | mm | source | S21 | steel lining tray |
| tray_depth | 25 | mm | source | S21 |  |
| hw_385_total | 385 | kg | source | S21 |  |
| hw_385_dsa | 24.2 | dB | source | S21 |  |
| hw_400_total | 400 | kg | source | S22 | sound study's total with 4+4 laminated glass |
| hw_400_dsa | 23.8 | dB | source | S22 |  |
| fan_final_kg | 5 | kg | source | S20 | S&P TD-350/100-125 ECOWATT inline fan, the sound study's pick |
| silencer_final_kg | 3.5 | kg | calculation | S20 | one separate silencer box: 0.6 m2 HDF 3 box + 1.2 m2 lining 25 mm at 1.2 kg/m2 |
| door_edge_seal_kg | 1 | kg | source | S20 | door edge seals on 3 sides |
| base_seal_kg | 0.5 | kg | source | S20 | seal under the thin floor and band |
| grommet_kg | 0.1 | kg | source | S20 | sealed cable holes |
| decor_fill_kg | 4 | kg | calculation | S20 | PET fill in the front decor: 1.65 m2 x 75 mm x 32 kg/m3 |
| t_leaf_s | 60 | s | assumption |  | clip one inner leaf (sound mass + felt) onto its frame from inside |

Sources:

| ID | What it says | Where |
| --- | --- | --- |
| S01 | v1 materials BOM, v5, 2026-10-29 | `sources/v1/indoor-pod-v3-bom-v5-2026-10-29.xlsx` |
| S02 | v1 STEP assembly, exported 2026-10-14 (older than the BOM; cross-check only) | `sources/v1/indoor-pod-v3-assembly.step` |
| S03 | v1 drawings: wood parts, floor frame, decor frame | `sources/v1/drawings/` |
| S04 | v2 build plan from the indoor pod lead engineer | `v2/00-Control/v2-build-plan.pdf` |
| S05 | v2 plan approved by Dee, 2026-10-31 (targets, light options, pallet sizes) | `v2/PLAN.md` |
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
| S19 | LTL overlength rules: most carriers start excessive-length charges for a piece over 96 in (summary; check each carrier's rules tariff) | https://logisticsplus.com/?p=25575 (read 2026-10-31) |
