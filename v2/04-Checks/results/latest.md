# Mechanical check run: e4cc460 on 2026-10-31

Offline checks (`tools/checks/run_checks.py`) on revision `e4cc460`. The Fusion checks (exact clash, tool access, thread engagement) are recorded separately when they run.

**Findings in this run: 1** (0 severe, 1 major, 0 minor). Register numbers in brackets.

## What ran

| Check | Ran on this revision | Findings |
|---|---|---|
| C01 clash and minimum gaps (Fusion) | yes | 0 |
| C02 tolerance stack-ups | yes | 0 |
| C03 fastener and tool access | no inputs yet | 0 |
| C04 weight, doorway and pallet fit | yes | 1 |
| C05 drawing completeness | no inputs yet | 0 |
| C06 BOM completeness | no inputs yet | 0 |
| C07 fastener schedule and thread engagement | no inputs yet | 0 |
| C08 hole-to-hole alignment | no inputs yet | 0 |
| C09 edge distance, bend radius, hole-to-bend | no inputs yet | 0 |
| C10 mixed metals | no inputs yet | 0 |
| C11 material grade and finish | no inputs yet | 0 |

Inputs: {"bodies_skeleton": 34, "bodies_assembly": 0, "parts_lists": [], "part_steps": []}

## Findings

| Register | Severity | Check | Subject | Finding | Owner |
|---|---|---|---|---|---|
| F-010 | major | C04 | POD total mass | The pod is about 436.3 kg against the 420 kg cap (D-37, D-54): 16.3 kg over. The layout study's list gives 436.3 kg (v2/05-Engineering/layout-study/out/parts-decided-P04.csv). Open against the cap until the wall sample settles it (ISS-080). | PM (Lead) |

## Tolerance stacks (C02)

| Stack | Joint | What | Needs | Nominal | Worst case | RSS (info) | State | Missing |
|---|---|---|---|---|---|---|---|---|
| ST-01 | IF-02 door to threshold | Running gap between the door's kick strip and the threshold | 3.0 to 10.0 | 7.00 | 7.00 to 7.00 | 7.00 to 7.00 | OPEN | Door bottom height (glass bottom); Kick strip height below the glass; Threshold height; Floor height under the threshold |
| ST-03 | IF-01 IF-03 IF-04 IF-05 M6 bolt into a rivnut through a clearance hole | Radial clearance left for an M6 bolt after both hole positions and the rivnut's float (fixed-fastener case; the panel shifts to the bolts within the spigot play) | >= 0.0 | 0.51 | 0.05 to 0.51 | 0.14 to 0.43 | PASS |  |
| ST-02 | IF-03 and IF-04 back wall across its width | Centre seam B1-B2 gap: the span less B1, B2 and the two corner stops; the centre seam takes the chain's tolerance through its slotted holes | 0.76 to 3.76 | 2.26 | 2.00 to 2.52 | 2.08 to 2.44 | OPEN | Space between the side frames; Back panel B1 width; Back panel B2 width |
| ST-02A | IF-03 and IF-04 back wall across its width: perfect panels | As ST-02 with the panels and the span taken as perfect, so only the two corner stops vary | 0.76 to 3.76 | 2.26 | 2.00 to 2.52 | 2.08 to 2.44 | PASS |  |
| ST-04 | IF-05 and IF-06 ceiling across its width | Centre seam C1-C2 gap: the span less C1, C2 and the two side stops; the centre seam takes the chain's tolerance through its slotted holes | 0.76 to 3.76 | 2.26 | 2.00 to 2.52 | 2.08 to 2.44 | OPEN | Space between the upper side panels' top members; Ceiling half C1 width; Ceiling half C2 width |
| ST-04A | IF-05 and IF-06 ceiling across its width: perfect halves | As ST-04 with the halves and the span taken as perfect, so only the two side stops vary | 0.76 to 3.76 | 2.26 | 2.00 to 2.52 | 2.08 to 2.44 | PASS |  |

## Shipping pieces (C04), from `v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv`

| Piece | kg | Size mm | Ships as | Status |
|---|---|---|---|---|
| W-SIDE-LO WALL - SIDE PANEL - LOWER (outer: ACP + frame + fill) | 11.86 | 1495 x 1145 x 43 | upright | calculation |
| L-CASS-SIDE-LO LINING - CASSETTE FOR W-SIDE-LO (steel tray + felt) | 11.08 | 1448 x 1145 x 34 | upright | calculation |
| W-SIDE-UP WALL - SIDE PANEL - UPPER (outer: ACP + frame + fill) | 11.86 | 1495 x 1145 x 43 | upright | calculation |
| L-CASS-SIDE-UP LINING - CASSETTE FOR W-SIDE-UP (steel tray + felt) | 10.64 | 1448 x 1098 x 34 | upright | calculation |
| W-BACK-LO WALL - BACK PANEL - LOWER (outer: ACP + frame + fill) | 9.67 | 1207 x 1104 x 43 | upright | calculation |
| L-CASS-BACK-LO LINING - CASSETTE FOR W-BACK-LO (steel tray + felt) | 8.68 | 1169 x 1104 x 34 | upright | calculation |
| W-BACK-UP WALL - BACK PANEL - UPPER (outer: ACP + frame + fill) | 9.67 | 1207 x 1104 x 43 | upright | calculation |
| L-CASS-BACK-UP LINING - CASSETTE FOR W-BACK-UP (steel tray + felt) | 8.68 | 1169 x 1104 x 34 | upright | calculation |
| C-HALF CEILING - HALF PANEL (outer: ACP + frame) | 10.14 | 1495 x 1207 x 43 | upright | calculation |
| L-CASS-HALF LINING - CASSETTE FOR C-HALF (steel tray + felt + ceiling fill) | 13.16 | 1414 x 1169 x 74 | upright | calculation |
| B-BAND-BACK BASE - BASE BAND PIECE 100x40 - BACK | 3.55 | 2420 x 100 x 40 | long | calculation |
| B-BAND-SIDE BASE - BASE BAND PIECE 100x40 - SIDE | 2.44 | 1660 x 100 x 40 | long | calculation |
| B-BAND-FRONT-L BASE - BASE BAND PIECE 100x40 - FRONT-L | 0.44 | 300 x 100 x 40 | upright | calculation |
| B-BAND-FRONT-R BASE - BASE BAND PIECE 100x40 - FRONT-R | 1.54 | 1050 x 100 x 40 | upright | calculation |
| B-KEY BASE - CORNER KEY | 0.15 | 120 x 80 x 40 | box | assumption |
| B-GLIDE BASE - LEVELLING GLIDE (hex from above) | 0.15 | 50 x 50 x 40 | box | assumption |
| B-THRESH BASE - DOOR THRESHOLD, LOW | 1.2 | 1176 x 60 x 20 | upright | assumption |
| B-FLOOR BASE - THIN FLOOR PANEL 15 mm | 15.37 | 1414 x 1169 x 15 | upright | calculation |
| F-DL FRONT - DECOR BLOCK - LEFT | 9.98 | 2290 x 278 x 205 | long | calculation |
| F-DR FRONT - DECOR BLOCK - RIGHT | 18.06 | 2290 x 1016 x 205 | long | calculation |
| F-DT FRONT - DECOR BLOCK - TOP | 7.02 | 1697 x 280 x 205 | long | calculation |
| F-GLASS-DOOR FRONT - GLASS DOOR UNIT (4+4 laminated glass, frameless, 85 mm kick strip with drop seal, hinges, pull) | 47.48 | 2096 x 1176 x 20 | glass | calculation |
| F-GLASS-FIXED FRONT - FIXED GLASS (4+4 laminated glass, frameless) | 27.97 | 2139 x 724 x 9 | glass | calculation |
| F-HW FRONT - SEALED GLAZING PROFILES FOR THE FIXED GLASS | 2.58 | 2200 x 120 x 60 | box | assumption |
| A-CART-SUPPLY AIR - SUPPLY SPLITTER CARTRIDGE WITH 2 x 12 V FANS (Noctua NF-A14 industrialPPC-3000 PWM) | 17.7 | 2100 x 405 x 159 | long | calculation |
| A-CART-EXHAUST AIR - EXHAUST SPLITTER CARTRIDGE WITH 2 x 12 V FANS (Noctua NF-A14 industrialPPC-3000 PWM) | 17.7 | 2100 x 405 x 159 | long | calculation |
| A-RISER AIR - EXHAUST RISER 150 mm (1 mm galvanised steel duct) | 9.6 | 2000 x 155 x 150 | long | calculation |
| K-SEALS KIT - DOOR EDGE SEALS, BASE SEAL, CABLE GROMMETS | 1.6 | 600 x 300 x 100 | box | source |
| E-KIT ELECTRICAL - SWITCHES, LIGHTS, HARNESS | 3.05 | 600 x 400 x 200 | box | assumption |
| K-FIX KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS | 4.67 | 400 x 300 x 150 | box | calculation |

## Fastener schedule (C07)

0 fastener lines; full table in `v2/04-Checks/fastener-schedule.csv`.

