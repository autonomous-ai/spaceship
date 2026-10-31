# Mechanical check run: 40ccd24 on 2026-11-01

Offline checks (`tools/checks/run_checks.py`) on revision `40ccd24`. The Fusion checks (exact clash, tool access, thread engagement) are recorded separately when they run.

**Findings in this run: 0** (0 severe, 0 major, 0 minor). Register numbers in brackets.

## What ran

| Check | Ran on this revision | Findings |
|---|---|---|
| C01 clash and minimum gaps (Fusion) | yes | 0 |
| C02 tolerance stack-ups | yes | 0 |
| C03 fastener and tool access | no inputs yet | 0 |
| C04 weight, doorway and pallet fit | yes | 0 |
| C05 drawing completeness | no inputs yet | 0 |
| C06 BOM completeness | yes | 0 |
| C07 fastener schedule and thread engagement | yes | 0 |
| C08 hole-to-hole alignment | no inputs yet | 0 |
| C09 edge distance, bend radius, hole-to-bend | no inputs yet | 0 |
| C10 mixed metals | yes | 0 |
| C11 material grade and finish | yes | 0 |

Inputs: {"bodies_skeleton": 34, "bodies_assembly": 0, "parts_lists": ["v2/04-BOM/100000_P01_POD-MASTER_BOM.csv"], "part_steps": []}

## Findings

| Register | Severity | Check | Subject | Finding | Owner |
|---|---|---|---|---|---|

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
| 1-05 WALL - PANEL ASSY - SIDE LOWER - LH | 11.088 | 1492.74 x 1142.74 x 46 | upright | calculation (CAD); fill provisional |
| 1-06 WALL - PANEL ASSY - SIDE LOWER - RH | 11.088 | 1492.74 x 1142.74 x 46 | upright | calculation (CAD); fill provisional |
| 1-07 WALL - PANEL ASSY - BACK UPPER - LH | 8.756 | 1200.61 x 1118.61 x 46 | upright | calculation; fill provisional |
| 1-08 WALL - PANEL ASSY - BACK UPPER - RH | 8.756 | 1200.61 x 1118.61 x 46 | upright | calculation; fill provisional |
| 1-09 WALL - PANEL ASSY - SIDE UPPER - LH | 11.075 | 1492.74 x 1142.74 x 46 | upright | calculation; fill provisional |
| 1-10 WALL - PANEL ASSY - SIDE UPPER - RH | 11.075 | 1492.74 x 1142.74 x 46 | upright | calculation; fill provisional |
| 1-11 CEILING - PANEL ASSY - C1 | 10.035 | 1495 x 1203.61 x 46 | upright | calculation (CAD); bond assumption |
| 1-12 CEILING - PANEL ASSY - C2 | 10.535 | 1495 x 1203.61 x 60 | upright | calculation; calculation (CAD); bond assumption |
| 1-13 LINING - CASSETTE - SIDE LOWER - RH | 10.474 | 1445 x 1142.74 x 34 | upright | calculation; lips confirmed |
| 1-14 LINING - CASSETTE - SIDE UPPER - RH | 10.047 | 1445 x 1092.74 x 34 | upright | calculation; lips confirmed |
| 1-15 LINING - CASSETTE - SIDE LOWER - LH | 10.474 | 1445 x 1142.74 x 34 | upright | calculation; lips confirmed |
| 1-16 LINING - CASSETTE - SIDE UPPER - LH | 10.047 | 1445 x 1092.74 x 34 | upright | calculation; lips confirmed |
| 1-17 LINING - CASSETTE - BACK LOWER - LH | 8.411 | 1166 x 1118.61 x 34 | upright | calculation; lips confirmed |
| 1-18 LINING - CASSETTE - BACK LOWER - RH | 8.411 | 1166 x 1118.61 x 34 | upright | calculation; lips confirmed |
| 1-19 LINING - CASSETTE - BACK UPPER - LH | 8.399 | 1166 x 1116.87 x 34 | upright | calculation; lips confirmed |
| 1-20 LINING - CASSETTE - BACK UPPER - RH | 8.399 | 1166 x 1116.87 x 34 | upright | calculation; lips confirmed |
| 2-01 FRONT - FIXED GLASS UNIT | 29.58 | 2033 x 1031 x 12 | glass | calculation (CAD) |
| 2-02 FRONT - DOOR UNIT | 49.076 | 2089 x 1175 x 149 | glass | calculation (CAD); kick strip assumption |
| 2-03 FRONT - DECOR BLOCK - DR | 18.056 | 2290 x 1016 x 205 | long | calculation |
| 2-04 BASE - BAND ASSY - BACK | 3.285 | 2420 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-05 BASE - BAND ASSY - SIDE - LH | 2.242 | 1517 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-06 BASE - BAND ASSY - SIDE - RH | 2.242 | 1517 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-07 BASE - BAND ASSY - FRONT - RH - UNDER THE FIXED GLASS | 0.972 | 729 x 110 x 40 | long | assumption; calculation; calculation; confirmed (1.5 mm) |
| 2-08 BASE - DOOR THRESHOLD - 13 MM | 1.2 | 1175 x 60 x 13 | long | assumption |
| 2-09 FRONT - DECOR BLOCK - DL | 9.976 | 2290 x 278 x 205 | long | calculation |
| 2-10 AIR - SOFFIT WITH THE EXHAUST FAN BOX AND 2 FANS | 13.908 | 2332 x 360 x 220 | long | assumption; calculation; calculation; fill provisional |
| 2-11 AIR - AIR COLUMN | 9.779 | 2105 x 360 x 217 | long | calculation; fill provisional |
| 2-12 FRONT - DECOR BLOCK - DT | 7.015 | 1697 x 280 x 205 | long | calculation |
| 2-13 ELECTRICAL - KIT - HARNESS, CORD SET, HUB ZONE, LIGHTS | 2.14 | 600 x 250 x 200 | long | calculation (ELECTRICAL) |
| 2-14 INTERIOR - LIGHT SHELF | 1.957 | 2332 x 80 x 50 | long | assumption |
| 2-15 BASE - SMALL PARTS CARTON | 1.626 | 600 x 400 x 150 | long | assumption; calculation; confirmed (1.5 mm) |
| 2-16 INTERIOR - LEDGE AND SCREEN MOUNT CARTON | 2.4 | 1000 x 250 x 120 | long | assumption |
| 2-17 AIR - INTAKE RISER WITH THE SUPPLY FAN BOX AND 2 FANS | 14.895 | 1845 x 460 x 155 | long | assumption; calculation |
| 2-18 AIR - CARTRIDGE - SUPPLY | 11.155 | 1750 x 314 x 173 | long | calculation |
| 2-19 AIR - CARTRIDGE - EXHAUST | 11.155 | 1750 x 314 x 173 | long | calculation |
| 2-20 LINING - CASSETTE - CEILING - COMMON | 9.476 | 1163 x 1048 x 74 | long | calculation (CAD); fill provisional |
| 2-21 LINING - CASSETTE - CEILING - COMMON | 9.476 | 1163 x 1048 x 74 | long | calculation (CAD); fill provisional |
| 2-22 POD - INSTALLATION KIT (OPEN FIRST) | 0.5 | 300 x 150 x 80 | long | assumption |

## Fastener schedule (C07)

7 fastener lines; full table in `v2/04-Checks/fastener-schedule.csv`.

