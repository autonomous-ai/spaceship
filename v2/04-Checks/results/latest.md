# Mechanical check run: de19950 on 2026-11-01

Offline checks (`tools/checks/run_checks.py`) on revision `de19950`. The Fusion checks (exact clash, tool access, thread engagement) are recorded separately when they run.

**Findings in this run: 13** (7 severe, 4 major, 2 minor). Register numbers in brackets.

## What ran

| Check | Ran on this revision | Findings |
|---|---|---|
| C01 clash and minimum gaps (Fusion) | yes | 0 |
| C02 tolerance stack-ups | yes | 0 |
| C03 fastener and tool access | no inputs yet | 0 |
| C04 weight, doorway and pallet fit | yes | 0 |
| C05 drawing completeness | yes | 11 |
| C06 BOM completeness | yes | 2 |
| C07 fastener schedule and thread engagement | yes | 0 |
| C08 hole-to-hole alignment | yes | 0 |
| C09 edge distance, bend radius, hole-to-bend | yes | 0 |
| C10 mixed metals | yes | 0 |
| C11 material grade and finish | yes | 0 |

Inputs: {"bodies_skeleton": 36, "bodies_assembly": 47, "parts_lists": ["v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv", "v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv", "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv"], "part_steps": ["v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step", "v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step", "v2/03-Manufacturing/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_STEP.step", "v2/03-Manufacturing/wall/211301_P01_WALL-SKIN-SIDE-LOWER-LH_STEP.step", "v2/03-Manufacturing/wall/211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_STEP.step", "v2/03-Manufacturing/wall/510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_STEP.step", "v2/03-Manufacturing/wall/511101_P01_LINING-TRAY-SIDE-LOWER-LH_STEP.step"]}

## Findings

| Register | Severity | Check | Subject | Finding | Owner |
|---|---|---|---|---|---|
| F-020 | severe | C05 | 211101 | 211101 WALL - PANEL FRAME - SIDE LOWER - LH has no drawing PDF (211101_REV_NAME_DWG.pdf under v2/02-Drawings) though its CAD is in v2/03-Manufacturing/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_STEP.step. | WALL |
| F-021 | severe | C05 | 211301 | 211301 WALL - SKIN - SIDE LOWER - LH has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: its DXF draws on BEND; only CUT and MARK pass, so it is folded; it isn't a sheet part (46.0 thick across 1142.7); its row's process names fold, groove. | WALL |
| F-030 | severe | C05 | 361001 | 361001 FRONT - DOOR LEAF - 4+4 LAMINATED has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: its row lacks a cut by laser, waterjet or router in its process; thickness; finish; an ISO 2768 general tolerance. | FRONT |
| F-031 | severe | C05 | 361002 | 361002 FRONT - DOOR KICK STRIP has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: its faces lie at 8 levels through the thickness (a pocket, a step or a rebate). | FRONT |
| F-024 | severe | C05 | 511101 | 511101 LINING - TRAY - SIDE LOWER - LH has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: its DXF draws on BEND; only CUT and MARK pass, so it is folded; it is folded (4 bends in its STEP); its row's process names bend, brake. | WALL |
| F-025 | severe | C05 | 831001 | 831001 HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS has no drawing PDF (831001_REV_NAME_DWG.pdf under v2/02-Drawings). | Joints Engineer |
| F-026 | severe | C05 | 831002 | 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL has no drawing PDF (831002_REV_NAME_DWG.pdf under v2/02-Drawings). | Joints Engineer |
| F-019 | major | C05 | 210101 | 210101 WALL - PANEL ASSY - SIDE LOWER - LH has no drawing PDF (210101_REV_NAME_DWG.pdf under v2/02-Drawings) though its CAD is in v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_STEP.step. | WALL |
| F-022 | major | C05 | 211501 | 211501 WALL - CAVITY FILL - SIDE LOWER - LH has no drawing, and D-89's cut-list route doesn't apply: its row names pockets, so it isn't a plain rectangle. | WALL |
| F-029 | major | C05 | 360001 | 360001 FRONT - DOOR UNIT has no drawing PDF (360001_REV_NAME_DWG.pdf under v2/02-Drawings) though its CAD is in v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step. | FRONT |
| F-023 | major | C05 | 510101 | 510101 LINING - CASSETTE - SIDE LOWER - LH has no drawing PDF (510101_REV_NAME_DWG.pdf under v2/02-Drawings) though its CAD is in v2/03-Manufacturing/wall/510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_STEP.step. | WALL |
| F-027 | minor | C06 | 368006 | 368006 is named 'FRONT - 180 MAGNETIC SEAL - DOOR SIDE - HOLD' in the CAD (v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step) but 'FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD' in the parts list (v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv); the guideline wants one name everywhere (section 4.2). | FRONT |
| F-028 | minor | C06 | 368102 | 368102 is named 'FRONT - DOOR CATCH STRIKE - SUGATSUNE HT-MSG62-U10' in the CAD (v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step) but 'FRONT - DOOR STRIKE' in the parts list (v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv); the guideline wants one name everywhere (section 4.2). | FRONT |

## Tolerance stacks (C02)

| Stack | Joint | What | Needs | Nominal | Worst case | RSS (info) | State | Missing |
|---|---|---|---|---|---|---|---|---|
| ST-01 | IF-02 door to threshold | Running gap between the door's kick strip and the threshold | 3.0 to 10.0 | 7.00 | 7.00 to 7.00 | 7.00 to 7.00 | OPEN | Door bottom height (glass bottom); Kick strip height below the glass; Threshold height; Floor height under the threshold |
| ST-03 | IF-01 IF-03 IF-04 IF-05 M6 bolt into a rivnut through a clearance hole | Radial clearance left for an M6 bolt after both hole positions and the rivnut's float (fixed-fastener case; the panel shifts to the bolts within the spigot play) | >= 0.0 | 0.51 | 0.05 to 0.51 | 0.14 to 0.43 | PASS |  |
| ST-02 | IF-03 and IF-04 back wall across its width | Closing seam B1-B2 frame gap: the span less the two corner stops and the B1, B2 frames | 4.0 to 7.0 | 5.50 | 5.24 to 5.76 | 5.32 to 5.68 | OPEN | Space between the side frames; Back panel B1 frame width; Back panel B2 frame width |
| ST-02A | IF-03 and IF-04 back wall across its width: perfect frames | As ST-02 with the frames and the span taken as perfect, so only the two corner stops vary | 4.0 to 7.0 | 5.50 | 5.24 to 5.76 | 5.32 to 5.68 | PASS |  |
| ST-04 | IF-05 and IF-06 ceiling across its width | Closing seam C1-C2 frame gap: the span less the two side stops and the C1, C2 frames | 4.0 to 7.0 | 5.50 | 5.24 to 5.76 | 5.32 to 5.68 | OPEN | Space between the upper side panels' top members; Ceiling half C1 frame width; Ceiling half C2 frame width |
| ST-04A | IF-05 and IF-06 ceiling across its width: perfect frames | As ST-04 with the frames and the span taken as perfect, so only the two side stops vary | 4.0 to 7.0 | 5.50 | 5.24 to 5.76 | 5.32 to 5.68 | PASS |  |

## Shipping pieces (C04), from `v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv`

| Piece | kg | Size mm | Ships as | Status |
|---|---|---|---|---|
| 1-01 BASE - FLOOR PANEL - F1 | 8.708 | 1455 x 1219 x 12 | upright | calculation; confirmed (9 mm, poplar core); calculation |
| 1-02 BASE - FLOOR PANEL - F2 | 8.708 | 1455 x 1219 x 12 | upright | calculation; confirmed (9 mm, poplar core); calculation |
| 1-03 WALL - PANEL ASSY - BACK LOWER - LH | 8.756 | 1200.61 x 1118.61 x 46 | upright | calculation; fill provisional |
| 1-04 WALL - PANEL ASSY - BACK LOWER - RH | 11.556 | 1200.61 x 1118.61 x 84 | upright | calculation (ELECTRICAL); calculation; fill provisional |
| 1-05 WALL - PANEL ASSY - SIDE LOWER - LH | 11.163 | 1492.74 x 1142.74 x 46 | upright | calculation (CAD); fill provisional |
| 1-06 WALL - PANEL ASSY - SIDE LOWER - RH | 11.163 | 1492.74 x 1142.74 x 46 | upright | calculation (CAD); fill provisional |
| 1-07 WALL - PANEL ASSY - BACK UPPER - LH | 8.756 | 1200.61 x 1118.61 x 46 | upright | calculation; fill provisional |
| 1-08 WALL - PANEL ASSY - BACK UPPER - RH | 8.756 | 1200.61 x 1118.61 x 46 | upright | calculation; fill provisional |
| 1-09 WALL - PANEL ASSY - SIDE UPPER - LH | 11.075 | 1492.74 x 1142.74 x 46 | upright | calculation; fill provisional |
| 1-10 WALL - PANEL ASSY - SIDE UPPER - RH | 11.075 | 1492.74 x 1142.74 x 46 | upright | calculation; fill provisional |
| 1-11 CEILING - PANEL ASSY - C1 | 10.035 | 1495 x 1200.61 x 46 | upright | calculation (CAD); bond assumption |
| 1-12 CEILING - PANEL ASSY - C2 | 10.535 | 1495 x 1200.61 x 60 | upright | calculation; calculation (CAD); bond assumption |
| 1-13 LINING - CASSETTE - SIDE LOWER - RH | 10.346 | 1445 x 1142.74 x 34 | upright | calculation (CAD) |
| 1-14 LINING - CASSETTE - SIDE UPPER - RH | 10.047 | 1445 x 1092.74 x 34 | upright | calculation; lips confirmed |
| 1-15 LINING - CASSETTE - SIDE LOWER - LH | 10.346 | 1445 x 1142.74 x 34 | upright | calculation (CAD) |
| 1-16 LINING - CASSETTE - SIDE UPPER - LH | 10.047 | 1445 x 1092.74 x 34 | upright | calculation; lips confirmed |
| 1-17 LINING - CASSETTE - BACK LOWER - LH | 8.411 | 1166 x 1118.61 x 34 | upright | calculation; lips confirmed |
| 1-18 LINING - CASSETTE - BACK LOWER - RH | 8.411 | 1166 x 1118.61 x 34 | upright | calculation; lips confirmed |
| 1-19 LINING - CASSETTE - BACK UPPER - LH | 8.399 | 1166 x 1116.87 x 34 | upright | calculation; lips confirmed |
| 1-20 LINING - CASSETTE - BACK UPPER - RH | 8.399 | 1166 x 1116.87 x 34 | upright | calculation; lips confirmed |
| 2-01 FRONT - FIXED GLASS UNIT | 28.782 | 2033 x 1031 x 12 | glass | calculation (CAD) |
| 2-02 FRONT - DOOR UNIT | 49.076 | 2089 x 1175 x 149 | glass | calculation (CAD); kick strip assumption |
| 2-03 FRONT - DECOR BLOCK - DR | 18.6 | 2290 x 1016 x 205 | long | calculation; calculation (CAD) |
| 2-04 BASE - BAND ASSY - BACK | 3.285 | 2420 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-05 BASE - BAND ASSY - SIDE - LH | 2.242 | 1517 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-06 BASE - BAND ASSY - SIDE - RH | 2.242 | 1517 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-07 BASE - BAND ASSY - FRONT - RH - UNDER THE FIXED GLASS | 1.153 | 729 x 110 x 40 | long | assumption; calculation; calculation (CAD); calculation; confirmed (1.5 mm) |
| 2-08 BASE - DOOR THRESHOLD - 13 MM | 1.2 | 1175 x 60 x 13 | long | assumption |
| 2-09 FRONT - DECOR BLOCK - DL | 9.976 | 2290 x 278 x 205 | long | calculation |
| 2-10 AIR - SOFFIT WITH THE EXHAUST FAN BOX AND 2 FANS | 13.873 | 2332 x 360 x 220 | long | assumption; calculation; calculation; fill provisional |
| 2-11 AIR - AIR COLUMN | 9.735 | 2105 x 360 x 217 | long | calculation; fill provisional |
| 2-12 FRONT - DECOR BLOCK - DT | 7.088 | 1697 x 280 x 205 | long | calculation; calculation (CAD) |
| 2-13 ELECTRICAL - KIT - HARNESS, CORD SET, HUB ZONE, LIGHTS | 2.14 | 600 x 250 x 200 | long | calculation (ELECTRICAL) |
| 2-14 INTERIOR - LIGHT SHELF | 1.954 | 2332 x 80 x 50 | long | assumption |
| 2-15 BASE - SMALL PARTS CARTON | 1.626 | 600 x 400 x 150 | long | assumption; calculation; confirmed (1.5 mm) |
| 2-16 INTERIOR - LEDGE AND SCREEN MOUNT CARTON | 2.4 | 1000 x 250 x 120 | long | assumption |
| 2-17 AIR - INTAKE RISER WITH THE SUPPLY FAN BOX AND 2 FANS | 14.895 | 1845 x 460 x 155 | long | assumption; calculation |
| 2-18 AIR - CARTRIDGE - SUPPLY | 11.155 | 1750 x 314 x 173 | long | calculation |
| 2-19 AIR - CARTRIDGE - EXHAUST | 11.155 | 1750 x 314 x 173 | long | calculation |
| 2-20 LINING - CASSETTE - CEILING - COMMON | 9.476 | 1163 x 1048 x 74 | long | calculation (CAD); fill provisional |
| 2-21 LINING - CASSETTE - CEILING - COMMON | 9.476 | 1163 x 1048 x 74 | long | calculation (CAD); fill provisional |
| 2-22 POD - INSTALLATION KIT (OPEN FIRST) | 0.5 | 300 x 150 x 80 | long | assumption |

## Fastener schedule (C07)

13 fastener lines; full table in `v2/04-Checks/fastener-schedule.csv`.

