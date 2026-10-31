# Mechanical check run: c9ae2a4 on 2026-10-31

Offline checks (`tools/checks/run_checks.py`) on revision `c9ae2a4`. The Fusion checks (exact clash, tool access, thread engagement) are recorded separately when they run.

**Findings in this run: 6** (3 severe, 3 major, 0 minor). Register numbers in brackets.

## What ran

| Check | Ran on this revision | Findings |
|---|---|---|
| C01 clash and minimum gaps (Fusion) | yes | 1 |
| C02 tolerance stack-ups | yes | 3 |
| C03 fastener and tool access | no inputs yet | 0 |
| C04 weight, doorway and pallet fit | yes | 2 |
| C05 drawing completeness | no inputs yet | 0 |
| C06 BOM completeness | no inputs yet | 0 |
| C07 fastener schedule and thread engagement | no inputs yet | 0 |
| C08 hole-to-hole alignment | no inputs yet | 0 |
| C09 edge distance, bend radius, hole-to-bend | no inputs yet | 0 |
| C10 mixed metals | no inputs yet | 0 |
| C11 material grade and finish | no inputs yet | 0 |

Inputs: {"bodies_skeleton": 32, "bodies_assembly": 0, "parts_lists": [], "part_steps": []}

## Findings

| Register | Severity | Check | Subject | Finding | Owner |
|---|---|---|---|---|---|
| F-004 | severe | C01 | skeleton shell back X -1207..1207 Z 2319..2357 | The outer shell is open on the back face of the skeleton: nothing covers X -1207 to 1207, Z 2319 to 2357 (a slot 2414 x 38 mm). Bordered by: B3 ENVELOPE, B4 ENVELOPE, C1 ENVELOPE, C2 ENVELOPE, L2 ENVELOPE, R2 ENVELOPE. Checked 1 mm inside the face on a 5 mm grid, bodies as their boxes. | Fusion Engineer 2 |
| F-001 | severe | C02 | skeleton SEAM-GAPS | SEAM-BACK-CENTRE: B1 ENVELOPE to B2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-CORNER-L: L1 ENVELOPE to B1 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-CORNER-R: R1 ENVELOPE to B2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-CEILING-CENTRE: C1 ENVELOPE to C2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-CEILING-SIDE: C1 ENVELOPE to L2 ENVELOPE is 0.0 mm, needs at least 1 mm. Rule source: assumption: 1.0 mm stands in until the joints register gives the compressed gasket thickness. Why: IF-04 asks for a seam gasket between B1 and B2 (and B3, B4); a gasket needs a gap of at least its compressed thickness, and frames cut to plus tolerance must still fit | Joints Engineer; Fusion Engineer 2 |
| F-002 | severe | C02 | skeleton KICK-OVER-THRESHOLD | KICK-OVER-THRESHOLD: KICK ENVELOPE to THRESHOLD ENVELOPE is 0.0 mm, needs at least 7 mm. Rule source: confirmed: FRONT's 7 mm floor gap for the drop seal, approved by the PM in the FRONT group on 2026-10-31. Why: The door swings over the threshold; with no running gap it rubs, and the drop seal needs the gap to close | FRONT; Fusion Engineer 2 |
| F-005 | major | C02 | skeleton SEAM-GAPS-HORIZONTAL | SEAM-SIDE-HORIZONTAL: L1 ENVELOPE to L2 ENVELOPE is 0.0 mm, needs at least 1 mm; SEAM-BACK-HORIZONTAL: B1 ENVELOPE to B3 ENVELOPE is 0.0 mm, needs at least 1 mm. Rule source: assumption: as SEAM-BACK-CENTRE. Why: IF-04 asks for a seam gasket between the lower and upper side panels; under the upper panel's weight it needs its compressed thickness or a groove | Joints Engineer; Fusion Engineer 2 |
| F-007 | major | C04 | F-HW | F-HW FRONT - SEALED GLAZING PROFILES FOR THE FIXED GLASS (2200 x 120 x 60 mm) doesn't fit the 48x40 pallet it ships on (1219 x 1016, at most 1679 tall loaded above a 150 mm deck); it fits the 48x96 pallet. | Layout Engineer |
| F-010 | major | C04 | POD total mass | The pod is about 438.7 kg against the 420 kg cap (D-37, D-54): 18.7 kg over. The layout study's list gives 426.7 kg (v2/05-Engineering/layout-study/out/parts-option-B1-final-stack.csv); adjustments since: +12.0 kg AIR-D60 (calculation, Air Engineer, passed on by the PM on 2026-10-31). Open against the cap until the wall sample settles it (ISS-080). | PM (Lead) |

## Tolerance stacks (C02)

| Stack | Joint | What | Needs | Nominal | Worst case | RSS (info) | State | Missing |
|---|---|---|---|---|---|---|---|---|
| ST-01 | IF-02 door to threshold | Running gap between the door's kick strip and the threshold | 3.0 to 10.0 | 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | OPEN | Door bottom height (glass bottom); Kick strip height below the glass; Threshold height; Floor height under the threshold |
| ST-02 | IF-03 and IF-04 back wall across its width | Gasket room left across the back wall: the space between the side frames less two back panels and three seams | >= 0.0 | 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | OPEN | Space between the side frames; Back panel B1 width; Back panel B2 width; Three seam gaskets compressed |
| ST-03 | IF-01 IF-03 IF-04 IF-05 M6 bolt into a rivnut through a clearance hole | Radial clearance left for an M6 bolt after both hole positions and the locating feature's play (fixed-fastener case) | >= 0.0 | 0.31 | 0.25 to 0.31 | 0.25 to 0.31 | OPEN | Clearance hole position (radial); Rivnut position (radial) |

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

