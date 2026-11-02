# Release checklist: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-009 | P01 | DRAFT, written by `build_release_checklist.py` | 2026-11-01 | Control pack |

What stands between the design and a manufacturing release, part by part. Nothing here is released (guideline milestone 4, REQ-DOC-02). Re-run it whenever parts merge.

Read from: main (ae83f273), PR #348 (3d7c6ae6), PR #366 (09b48f53), PR #356 (073a0ba7), PR #313 (780aa830), PR #310 (b10bfb2d), PR #364 (db237676), PR #320 (2a4b6263), PR #319 (7d90ef4d), PR #337 (51832426), PR #382 (35640feb), PR #378 (3a1b82f4), PR #343 (dc817309), PR #395 (c440a148), PR #398 (c48b78fd), PR #392 (39f6bbea), PR #377 (96b0db16), PR #399 (d11f2f2e), PR #401 (47acac25), PR #339 (b18b3da6), PR #396 (09c10ffc). The Mac's screen at run time: **unlocked**. 633 files in the CAD, drawing and manufacturing folders; the FAI plan's 96 characteristics, 11 functional checks and 22 bought-part test lines.

Read from main although an open PR changed them, because main changed them later (the PR's edit counts once it rebases): `v2/02-Drawings/air/610101_P01_AIR-AIR-COLUMN_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/ceiling/510301_P01_LINING-CASSETTE-CEILING-COMMON_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510102_P01_LINING-CASSETTE-SIDE-LOWER-RH_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510103_P01_LINING-CASSETTE-SIDE-UPPER-LH_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510104_P01_LINING-CASSETTE-SIDE-UPPER-RH_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510201_P01_LINING-CASSETTE-BACK-LOWER-B1_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/02-Drawings/wall/510202_P01_LINING-CASSETTE-BACK-LOWER-B2_DWG.pdf`: PR #377 changed it, but main changed it later; `v2/05-Engineering/joints/joints-register.md`: PR #382 changed it, but main changed it later; `v2/05-Engineering/joints/joints-register.md`: origin/super-tab/116a11a6d19f4479fa615216-lining changed it, but main changed it later; `v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv`: PR #348 changed it, but main changed it later.

**Done**: nothing missing from the columns below; a test counts once it is named, and its result belongs in the FAI plan. **Open**: something missing that can be done now. **Blocked**: only the drawing is missing and the screen is locked; the drawing start needs it unlocked (D-84), unless tools/drawgen draws it (D-113). **HOLD**: a bought part whose product isn't named yet, or a made part with nothing else missing whose material, grade or status says HOLD (PM, 2026-11-01).

## Totals per team

| Team | Made: done | Made: open | Made: blocked by the locked screen | Made: HOLD | Bought: done | Bought: open | Bought: HOLD |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASE | 12 | 6 | 0 | 0 | 3 | 1 | 3 |
| CEILING | 17 | 6 | 0 | 0 | 5 | 0 | 5 |
| CEILING (builds AIR, D-80) | 15 | 26 | 0 | 9 | 4 | 0 | 9 |
| CEILING (builds INTERIOR, D-80) | 0 | 3 | 0 | 4 | 0 | 0 | 2 |
| ELECTRICAL | 8 | 1 | 0 | 3 | 70 | 1 | 12 |
| FRONT | 55 | 15 | 0 | 3 | 6 | 0 | 7 |
| JOINTS | 5 | 6 | 0 | 0 | 0 | 0 | 0 |
| WALL | 22 | 40 | 0 | 0 | 5 | 5 | 4 |
| **All, each number once** | 134 | 103 | 0 | 19 | 79 | 7 | 39 |

97 of the 256 made numbers have no drawing yet; for 52 of them the drawing is the only gap, so their drawings can start now (D-84).

What the open made numbers miss: drawing 97, BOM row 25, CAD 24, DXF or cut list 20, FAI 12, STEP 11.

## Made parts with no FAI line

12 made numbers have no line in the FAI plan (`v2/06-Verification/fai-plan.md`) yet:

| Team | Part | Name | From |
|---|---|---|---|
| BASE | 111602 | BASE - LEVELLING GLIDE - M10 - D40 | PR #396 |
| BASE | 111301 | BASE - SILL - FIXED GLASS | PR #396 |
| BASE | 111302 | BASE - SILL - FIXED GLASS - BENT PROFILE | PR #396 |
| BASE | 111303 | BASE - SILL - FIXED GLASS - DOOR-END PLATE | PR #396 |
| JOINTS | 831007 | HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL | PR #348, PR #401 |
| JOINTS | 831008 | HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL | PR #348, PR #401 |
| FRONT | 351105 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 1 | PR #378 |
| FRONT | 351106 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 2 AND 3 | PR #378 |
| FRONT | 351107 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 4 | PR #378 |
| FRONT | 361004 | FRONT - DOOR STRIKE SHIM - 1.2 STAINLESS | PR #339 |
| JOINTS | 831009 | HARDWARE MITRE PLATE 40X40 45DEG | main |
| JOINTS | 831010 | HARDWARE LOCATING SPIGOT 11 PROUD | main |

## Made parts and assemblies

### BASE

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 110000 | BASE | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01, K-B05, K-B06, K-B07 | done |
| 110101 | BASE - BAND ASSY - SIDE - LH | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | done |
| 111101 | BASE - BAND TUBE - SIDE - LH | PR #396 | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 111111 | BASE - TUBE END CAP - 97 X 37 X 2 - AL BLACK | PR #396 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 111601 | BASE - GLIDE DOUBLER - COMMON | PR #396 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-B09 | done |
| 111602 | BASE - LEVELLING GLIDE - M10 - D40 | PR #396 | yes | yes | yes | n/a | no | yes | yes | no | open: drawing, FAI |
| 110102 | BASE - BAND ASSY - SIDE - RH | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | done |
| 111102 | BASE - BAND TUBE - SIDE - RH | PR #396 | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 110103 | BASE - BAND ASSY - BACK | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | done |
| 111103 | BASE - BAND TUBE - BACK | PR #396 | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10, K-B11 | done |
| 110104 | BASE - BAND ASSY - FRONT - LH | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | done |
| 111104 | BASE - BAND TUBE - FRONT - FACET 1 - LH | PR #396 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | open: drawing |
| 111105 | BASE - BAND TUBE - FRONT - FACET 2 - LH | PR #396 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | open: drawing |
| 110106 | BASE - BAND ASSY - FRONT - FIXED GLASS | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | done |
| 111106 | BASE - BAND TUBE - FRONT - FIXED GLASS | PR #396 | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 111301 | BASE - SILL - FIXED GLASS | PR #396 | yes | yes | yes | n/a | yes | yes | n/a | no | open: FAI |
| 111302 | BASE - SILL - FIXED GLASS - BENT PROFILE | PR #396 | yes | yes | yes | no | no | yes | yes | no | open: DXF or cut list, drawing, FAI |
| 111303 | BASE - SILL - FIXED GLASS - DOOR-END PLATE | PR #396 | yes | yes | yes | yes | no | yes | yes | no | open: drawing, FAI |

### CEILING

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 410000 | CEILING | PR #348 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 410101 | CEILING - PANEL ASSY - C1 | PR #348 | yes | yes | yes | n/a | yes | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | done |
| 410102 | CEILING - PANEL ASSY - C2 | PR #348 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 411101 | CEILING - PANEL FRAME - C1 | PR #348 | yes | yes | yes | n/a | no | yes | n/a | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17, K-P07 | open: drawing |
| 411102 | CEILING - PANEL FRAME - C2 | PR #348 | yes | yes | yes | n/a | no | yes | n/a | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17, K-P07 | open: drawing |
| 412101 | CEILING - FRAME SIDE MEMBER - COMMON | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 412102 | CEILING - FRAME SEAM MEMBER - C1 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 412103 | CEILING - FRAME FRONT MEMBER - C1 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 412104 | CEILING - FRAME BACK MEMBER 40 X 40 - C1 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 412105 | CEILING - FRAME CROSS MEMBER 1 - COMMON | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 412202 | CEILING - FRAME SEAM MEMBER - C2 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411102 (D-162) | yes | yes | K-J18 | done |
| 412203 | CEILING - FRAME FRONT MEMBER - C2 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411102 (D-162) | yes | yes | K-J18 | done |
| 412204 | CEILING - FRAME BACK MEMBER 40 X 40 - C2 | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411102 (D-162) | yes | yes | K-J18 | done |
| 412001 | CEILING - FRAME CROSS MEMBER - PLAIN - COMMON | PR #348 | yes | yes | yes | yes | its frame's cut list row, 411101 (D-162) | yes | yes | K-J18 | done |
| 411301 | CEILING - SKIN - C1 | PR #348 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | n/a | K-P03, K-P04 | done |
| 411302 | CEILING - SKIN - C2 | PR #348 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04, K-P06 | done |
| 510301 | LINING - CASSETTE - CEILING - COMMON | PR #348 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05, K-L10, K-L11 | done |
| 513101 | LINING - TRAY - CEILING | PR #348 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02, K-L06 | open: drawing |
| 513102 | LINING - RIB - CEILING | PR #348 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02, K-L07 | open: drawing |
| 513201 | LINING - FELT - CEILING | PR #348 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04, K-L08 | done |
| 513301 | LINING - FILL - CEILING - BAY A | PR #348 | yes | yes | yes | yes | DXF and row (D-128) | yes | n/a | K-P05, K-L09 | done |
| 513302 | LINING - FILL - CEILING - BAY B | PR #348 | yes | yes | yes | yes | DXF and row (D-128) | yes | n/a | K-P05, K-L09 | done |
| 513303 | LINING - FILL - CEILING - BAY C | PR #348 | yes | yes | yes | yes | DXF and row (D-128) | yes | n/a | K-P05, K-L09 | done |

### CEILING (builds AIR, D-80)

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 610000 | AIR | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 610101 | AIR - AIR COLUMN | PR #378 | yes | yes | yes | n/a | yes | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611106 | AIR - COLUMN FOOT PLATE | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611101 | AIR - COLUMN FACE - FRONT | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611102 | AIR - COLUMN FACE - LEFT | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611103 | AIR - COLUMN CORNER ANGLE - FRONT | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611109 | AIR - COLUMN CORNER ANGLE - BACK | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611107 | AIR - COLUMN PLENUM SIDE PLATE - LOW | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611108 | AIR - COLUMN PLENUM SIDE PLATE - HIGH | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611104 | AIR - COLUMN FILL - FRONT | PR #378 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611110 | AIR - COLUMN FILL - LEFT | PR #378 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611105 | AIR - KICK GRILLE - FRONT | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611111 | AIR - KICK GRILLE - LEFT | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 610301 | AIR - SPLITTER CARTRIDGE - COMMON | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611301 | AIR - CARTRIDGE CASING | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611302 | AIR - CARTRIDGE LAYER 50 | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 610201 | AIR - SOFFIT | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611201 | AIR - SOFFIT UNDERSIDE - LEFT HINGED | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611207 | AIR - SOFFIT UNDERSIDE - RIGHT HINGED | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611208 | AIR - SOFFIT UNDERSIDE - FIXED OVER THE COLUMN | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611202 | AIR - SOFFIT FACE - FRONT | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611205 | AIR - SOFFIT TOP RAIL - DOOR SIDE | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611209 | AIR - SOFFIT TOP RAIL - ROOM SIDE | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611206 | AIR - SOFFIT END PLATE - LEFT | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611210 | AIR - SOFFIT DOOR-SIDE PLATE | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611203 | AIR - SOFFIT FILL | PR #378 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611211 | AIR - SOFFIT FILL - FRONT | PR #378 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611204 | AIR - EXHAUST GRILLE | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | done |
| 610402 | AIR - EXHAUST FAN BOX | PR #378 | yes | yes | yes | n/a | yes | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611401 | AIR - FAN BOX CASING - EXHAUST | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611403 | AIR - FAN BOX BULKHEAD - EXHAUST | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611405 | AIR - FAN BOX LINING - EXHAUST SIDE | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611406 | AIR - FAN BOX LINING - EXHAUST FAR END | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 610401 | AIR - SUPPLY FAN BOX | PR #378 | yes | yes | yes | n/a | yes | yes | n/a | K-A01, K-A02, K-A03, K-A05 | done |
| 611402 | AIR - FAN BOX CASING - SUPPLY | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611404 | AIR - FAN BOX BULKHEAD - SUPPLY | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611407 | AIR - FAN BOX LINING - SUPPLY END | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611501 | AIR - INTAKE RISER | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03, K-A04 | open: DXF or cut list, drawing |
| 611408 | AIR - FAN BOX LIP ANGLE - SUPPLY | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611601 | AIR - ROOF SLEEVE | PR #378 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611602 | AIR - ROOF GRILLE | PR #378 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | K-A01, K-A02, K-A03 | done |
| 610403 | AIR RISER TRANSITION | PR #395 | no | no | yes | — | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 610404 | AIR SUPPLY TRANSITION | PR #395 | no | no | yes | — | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611701 | AIR RISER TRANSITION LEFT WRAPPER | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611702 | AIR RISER TRANSITION RIGHT WRAPPER | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611703 | AIR RISER TRANSITION CHEEK | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611801 | AIR SUPPLY TRANSITION SHELL | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611802 | AIR SUPPLY TRANSITION FLOOR | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611803 | AIR SUPPLY TRANSITION VANE OVER THE BOX | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |
| 611804 | AIR SUPPLY TRANSITION VANE BESIDE THE BOX | PR #395 | no | no | yes | yes | no | no | — | K-A01, K-A02, K-A03 | open: BOM row, CAD, drawing |

### CEILING (builds INTERIOR, D-80)

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 810000 | INTERIOR | PR #356 | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 810101 | INTERIOR - WORK WALL LEDGE ASSY | PR #356 | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 811101 | INTERIOR - LEDGE - TOP | PR #356 | yes | yes | yes | yes | yes | yes | yes | K-A02, K-I01, K-I02 | HOLD |
| 810201 | INTERIOR - LIGHT SHELF ASSY | PR #356 | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 811201 | INTERIOR - LIGHT SHELF - BACK | PR #356 | yes | yes | yes | yes | yes | yes | yes | K-A02, K-I01, K-I03 | HOLD |
| 811202 | INTERIOR - LIGHT SHELF - SIDE LH | PR #356 | yes | yes | yes | yes | yes | yes | yes | K-A02, K-I01, K-I03 | HOLD |
| 811203 | INTERIOR - LIGHT SHELF - SIDE RH | PR #356 | yes | yes | yes | yes | yes | yes | yes | K-A02, K-I01, K-I03 | HOLD |

### ELECTRICAL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 710000 | ELECTRICAL | PR #337 | yes | yes | yes | n/a | yes: its wiring diagram, routes and joints on sheet 3 (D-93) | yes | n/a | K-E01 | done |
| 710001 | ELECTRICAL - POWER UNIT - B2 | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 711001 | ELECTRICAL - POWER UNIT - ENCLOSURE BODY | PR #337 | yes | yes | yes | yes | yes | yes | yes | K-E01, K-E02 | HOLD |
| 711002 | ELECTRICAL - POWER UNIT - FRONT PLATE | PR #337 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-F06, K-E01, K-E03 | HOLD |
| 710011 | ELECTRICAL - HARNESS - LIGHT FEED - B2/B4 | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710021 | ELECTRICAL - HARNESS - TRUNK - B2/R1 | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710023 | ELECTRICAL - HARNESS - AIR COLUMN | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710024 | ELECTRICAL - HARNESS - CALL LIGHT - R2 | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710031 | ELECTRICAL - DRAW WIRE - CEILING ROUTE | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710041 | ELECTRICAL - HUB AND CONTROLS ZONE | PR #337 | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 711005 | ELECTRICAL - HUB ZONE COVER PLATE | PR #337 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-F06, K-E01, K-E04 | HOLD |
| 719001 | ELECTRICAL - CORD SET - 120 V US - 3 M (KIT) | PR #337 | yes | yes | yes | n/a | no | yes | n/a | K-E01 | open: drawing |

### FRONT

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 350001 | FRONT - DECOR BLOCK ASSY - DL | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D18 | open: drawing |
| 351101 | FRONT - DECOR SKIN - DL | PR #378 | yes | yes | yes | yes | no | yes | n/a | K-D19 | open: drawing |
| 351104 | FRONT - DECOR FRAME - DL | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D20 | open: drawing |
| 351102 | FRONT - DECOR BACK PLATE - DL | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D21 | done |
| 351105 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 1 | PR #378 | yes | yes | yes | no | no | yes | yes | no | open: DXF or cut list, drawing, FAI |
| 351106 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 2 AND 3 | PR #378 | yes | yes | yes | no | no | yes | yes | no | open: DXF or cut list, drawing, FAI |
| 351107 | FRONT - DOOR HINGE-SIDE STOP - DL - PIECE 4 | PR #378 | yes | yes | yes | no | no | yes | yes | no | open: DXF or cut list, drawing, FAI |
| 350002 | FRONT - DECOR BLOCK ASSY - DT | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D13 | open: drawing |
| 351201 | FRONT - DECOR SKIN - DT | PR #378 | yes | yes | yes | yes | no | yes | n/a | K-D14 | open: drawing |
| 351204 | FRONT - DECOR FRAME - DT | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D15 | open: drawing |
| 351202 | FRONT - DECOR BACK PLATE - DT | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D16 | done |
| 351203 | FRONT - DOOR TOP STOP - DT | PR #378 | yes | yes | yes | no | no | yes | yes | K-D17 | open: DXF or cut list, drawing |
| 350003 | FRONT - DECOR BLOCK ASSY - DR | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D01, K-D02 | open: drawing |
| 351301 | FRONT - DECOR SKIN - DR | PR #378 | yes | yes | yes | yes | no | yes | n/a | K-D03 | open: drawing |
| 351306 | FRONT - DECOR FRAME - DR | PR #378 | yes | yes | yes | n/a | no | yes | n/a | K-D04, K-D05 | open: drawing |
| 351302 | FRONT - DECOR BACK PLATE - DR | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D06 | done |
| 351305 | FRONT - DECOR INNER FACE PANEL - DR - REMOVABLE | PR #378 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D07 | done |
| 351304 | FRONT - DECOR INNER PANEL FELT - DR | PR #378 | yes | yes | yes | yes | DXF and row (D-128) | yes | n/a | K-D09 | HOLD |
| 352101 | FRONT - DECOR FRAME DL - BACK RING BOTTOM | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352102 | FRONT - DECOR FRAME DL - BACK RING DOOR SIDE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352103 | FRONT - DECOR FRAME DL - BACK RING SLOPE UNDER DT | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352104 | FRONT - DECOR FRAME DL - BACK RING BOLT LINE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352105 | FRONT - DECOR FRAME DL - RING DOOR SIDE - RINGS 1 TO 4 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352106 | FRONT - DECOR FRAME DL - RING BACK - RINGS 1 TO 4 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352107 | FRONT - DECOR FRAME DL - RING BOTTOM - OUTER FACET | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352108 | FRONT - DECOR FRAME DL - RING BOTTOM - FRONT FACET | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352109 | FRONT - DECOR FRAME DL - RING OUTER FACET - RINGS 2 TO 4 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352110 | FRONT - DECOR FRAME DL - RING FRONT FACET - RINGS 2 TO 4 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352111 | FRONT - DECOR FRAME DL - HINGE POST 1 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352112 | FRONT - DECOR FRAME DL - DOOR-SIDE FRONT POST 1 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352113 | FRONT - DECOR FRAME DL - HINGE POST 2 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352114 | FRONT - DECOR FRAME DL - DOOR-SIDE FRONT POST 2 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352115 | FRONT - DECOR FRAME DL - HINGE POST 3 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352116 | FRONT - DECOR FRAME DL - DOOR-SIDE FRONT POST 3 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351104 (D-162) | yes | yes | K-J18 | done |
| 352201 | FRONT - DECOR FRAME DT - BACK RING BOTTOM | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352202 | FRONT - DECOR FRAME DT - BACK RING DR JOINT | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352203 | FRONT - DECOR FRAME DT - BACK RING TOP | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352204 | FRONT - DECOR FRAME DT - BACK RING SLOPE OVER DL | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352205 | FRONT - DECOR FRAME DT - BACK RING POST | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352206 | FRONT - DECOR FRAME DT - FRONT FACET TUBE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352207 | FRONT - DECOR FRAME DT - CATCH AND STOP RAIL | PR #378 | yes | yes | yes | yes | yes | yes | yes | K-J18 | done |
| 352208 | FRONT - DECOR FRAME DT - CHAMFER TUBE ALONG X | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352209 | FRONT - DECOR FRAME DT - UNDERSIDE CROSS TUBE LEFT | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352210 | FRONT - DECOR FRAME DT - UNDERSIDE CROSS TUBE OVER THE CATCH | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352211 | FRONT - DECOR FRAME DT - CHAMFER CROSS TUBE - 3 OFF | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351204 (D-162) | yes | yes | K-J18 | done |
| 352301 | FRONT - DECOR FRAME DR - FRONT RING BOTTOM | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352302 | FRONT - DECOR FRAME DR - FRONT RING FACET SIDE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352303 | FRONT - DECOR FRAME DR - FRONT RING TOP | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352304 | FRONT - DECOR FRAME DR - FRONT RING DT JOINT | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352305 | FRONT - DECOR FRAME DR - FRONT RING DIAGONAL | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352306 | FRONT - DECOR FRAME DR - FRONT RING GLASS EDGE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352307 | FRONT - DECOR FRAME DR - BACK RING BOTTOM | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352308 | FRONT - DECOR FRAME DR - BACK RING BOLT LINE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352309 | FRONT - DECOR FRAME DR - BACK RING TOP | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352310 | FRONT - DECOR FRAME DR - BACK RING DT JOINT | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352311 | FRONT - DECOR FRAME DR - BACK RING DT LEDGE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352312 | FRONT - DECOR FRAME DR - BACK RING DIAGONAL | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352313 | FRONT - DECOR FRAME DR - BACK RING GLASS EDGE | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352314 | FRONT - DECOR FRAME DR - FRONT RING CROSS 724 | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352315 | FRONT - DECOR FRAME DR - FRONT RING FAN BOX SHELF | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352322 | FRONT - DECOR FRAME DR - FRONT RING CROSS OVER THE FAN BOX | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352316 | FRONT - DECOR FRAME DR - BACK RING BAND | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 352317 | FRONT - DECOR FRAME DR - FACET TUBE - 3 OFF | PR #378 | yes | yes | yes | yes | yes | yes | yes | K-J18 | done |
| 352318 | FRONT - DECOR FRAME DR - FACET TUBE FAN BOX SHELF | PR #378 | yes | yes | yes | yes | yes | yes | yes | K-J18 | done |
| 352319 | FRONT - DECOR FRAME DR - CHAMFER TUBE - 2 OFF | PR #378 | yes | yes | yes | yes | yes | yes | yes | K-J18 | done |
| 352320 | FRONT - DECOR FRAME DR - DT JOINT TUBE SLANTED | PR #378 | yes | yes | yes | yes | its frame's cut list row, 351306 (D-162) | yes | yes | K-J18 | done |
| 360001 | FRONT - DOOR UNIT | PR #339 | yes | yes | yes | n/a | yes | yes | n/a | K-F07, K-F08 | done |
| 361001 | FRONT - DOOR LEAF - 4+4 LAMINATED | PR #339 | yes | yes | yes | yes | yes | yes | n/a | K-F01, K-F02 | HOLD |
| 361002 | FRONT - DOOR KICK STRIP | PR #339 | yes | yes | yes | yes | yes | yes | yes | K-F05, K-F06 | done |
| 361004 | FRONT - DOOR STRIKE SHIM - 1.2 STAINLESS | PR #339 | yes | yes | yes | yes | no | yes | yes | no | open: drawing, FAI |
| 360002 | FRONT - FIXED GLASS UNIT | PR #339 | yes | yes | yes | n/a | yes | yes | n/a | K-F03, K-F04 | done |
| 361003 | FRONT - FIXED GLASS - 4+4 LAMINATED | PR #339 | yes | yes | yes | yes | yes | yes | n/a | K-F01, K-F02 | HOLD |
| 351303 | FRONT DECOR INNER PANEL DR | main | no | no | no | yes | no | no | — | K-D08 | open: BOM row, CAD, STEP, drawing |

### JOINTS

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 111211 | BASE - CORNER KEY - SQUARE - COMMON | PR #396 | yes | yes | yes | yes | yes | yes | yes | K-B08 | done |
| 111212 | BASE - CORNER KEY - FRONT - LH | PR #396 | yes | yes | yes | n/a | on 111211, tabulated (D-89) | yes | yes | K-B08 | done |
| 831001 | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS | PR #396, PR #401 | yes | yes | yes | n/a | yes | yes | yes | K-J07 | done |
| 831002 | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL | PR #348, PR #396, PR #401 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-J08 | done |
| 111214 | BASE - CORNER KEY - KNEE - LH | PR #396 | yes | yes | yes | n/a | on 111211, tabulated (D-89) | yes | yes | K-B08 | done |
| 831007 | HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL | PR #348, PR #401 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | no | open: FAI |
| 831008 | HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL | PR #348, PR #401 | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | yes | no | open: FAI |
| 111213 | BASE CORNER KEY FRONT RH | main | no | no | yes | — | on 111211, tabulated (D-89) | no | — | K-B08 | open: BOM row, CAD |
| 111215 | BASE CORNER KEY SQUARE INLINE | main | no | no | yes | — | on 111211, tabulated (D-89) | no | — | K-B08 | open: BOM row, CAD |
| 831009 | HARDWARE MITRE PLATE 40X40 45DEG | main | no | no | yes | yes | no | no | — | no | open: BOM row, CAD, drawing, FAI |
| 831010 | HARDWARE LOCATING SPIGOT 11 PROUD | main | no | no | yes | — | on 831001, tabulated (D-89) | no | — | no | open: BOM row, CAD, FAI |

### WALL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 210101 | WALL - PANEL ASSY - SIDE LOWER - LH | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211101 | WALL - PANEL FRAME - SIDE LOWER - LH | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 212101 | WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | its frame's cut list row, 211101 (D-162) | yes | yes | K-J18 | done |
| 212102 | WALL - FRAME RAIL TOP - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | its frame's cut list row, 211101 (D-162) | yes | yes | K-J18 | done |
| 212103 | WALL - FRAME STILE FRONT - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | its frame's cut list row, 211101 (D-162) | yes | yes | K-J18 | done |
| 212104 | WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | its frame's cut list row, 211101 (D-162) | yes | yes | K-J18 | done |
| 212105 | WALL - FRAME STILE MID - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | its frame's cut list row, 211101 (D-162) | yes | yes | K-J18 | done |
| 211301 | WALL - SKIN - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04, K-P08 | open: drawing |
| 211515 | WALL - CAVITY FILL PIECE F01 240 X 1102.7 - SIDE LOWER - COMMON | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 211516 | WALL - CAVITY FILL PIECE F02 230.9 X 1102.7 - SIDE LOWER - COMMON | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 211517 | WALL - CAVITY FILL PIECE F03 205.5 X 1102.7 - SIDE LOWER - COMMON | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 211518 | WALL - CAVITY FILL PIECE F04 214 X 1102.7 - SIDE LOWER - COMMON | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 211701 | WALL - CASSETTE LEDGE - SIDE LOWER - COMMON | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J20 | open: drawing |
| 510101 | LINING - CASSETTE - SIDE LOWER - LH | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511101 | LINING - TRAY - SIDE LOWER - LH | PR #401 | yes | yes | yes | yes | yes | yes | yes | K-L01, K-L02 | done |
| 511301 | LINING - FELT - SIDE LOWER - LH | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210102 | WALL - PANEL ASSY - SIDE LOWER - RH | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211102 | WALL - PANEL FRAME - SIDE LOWER - RH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211302 | WALL - SKIN - SIDE LOWER - RH | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04, K-P08 | open: drawing |
| 211502 | WALL - CAVITY FILL - SIDE LOWER - RH | PR #401 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510102 | LINING - CASSETTE - SIDE LOWER - RH | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511102 | LINING - TRAY - SIDE LOWER - RH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511302 | LINING - FELT - SIDE LOWER - RH | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210103 | WALL - PANEL ASSY - SIDE UPPER - LH | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211103 | WALL - PANEL FRAME - SIDE UPPER - LH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211303 | WALL - SKIN - SIDE UPPER - LH | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04, K-P08 | open: drawing |
| 211503 | WALL - CAVITY FILL - SIDE UPPER - LH | PR #401 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510103 | LINING - CASSETTE - SIDE UPPER - LH | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511103 | LINING - TRAY - SIDE UPPER - LH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511303 | LINING - FELT - SIDE UPPER - LH | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210104 | WALL - PANEL ASSY - SIDE UPPER - RH | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211104 | WALL - PANEL FRAME - SIDE UPPER - RH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211304 | WALL - SKIN - SIDE UPPER - RH | PR #401 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04, K-P08 | open: drawing |
| 211504 | WALL - CAVITY FILL - SIDE UPPER - RH | PR #401 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510104 | LINING - CASSETTE - SIDE UPPER - RH | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511104 | LINING - TRAY - SIDE UPPER - RH | PR #401 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511304 | LINING - FELT - SIDE UPPER - RH | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210201 | WALL - PANEL ASSY - BACK LOWER - B1 | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211201 | WALL - PANEL FRAME - BACK LOWER - B1 | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211401 | WALL - SKIN - BACK LOWER - B1 | PR #401 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04, K-P08 | done |
| 211601 | WALL - CAVITY FILL - BACK LOWER - B1 | PR #401 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510201 | LINING - CASSETTE - BACK LOWER - B1 | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511201 | LINING - TRAY - BACK LOWER - B1 | PR #401 | yes | yes | yes | yes | yes | yes | yes | K-L01, K-L02 | done |
| 511401 | LINING - FELT - BACK LOWER - B1 | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210202 | WALL - PANEL ASSY - BACK LOWER - B2 | PR #401 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211202 | WALL - PANEL FRAME - BACK LOWER - B2 | PR #401 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211402 | WALL - SKIN - BACK LOWER - B2 | PR #401 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04, K-P08 | done |
| 211602 | WALL - CAVITY FILL - BACK LOWER - B2 | PR #401 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510202 | LINING - CASSETTE - BACK LOWER - B2 | PR #401 | yes | yes | yes | n/a | yes | yes | n/a | K-L03, K-L05 | done |
| 511202 | LINING - TRAY - BACK LOWER - B2 | PR #401 | yes | yes | yes | yes | yes | yes | yes | K-L01, K-L02 | done |
| 511402 | LINING - FELT - BACK LOWER - B2 | PR #401 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 211501 | WALL CAVITY FILL SIDE LOWER LH | main | no | yes | yes | — | no | no | — | K-P05 | open: BOM row, drawing |
| 211535 | WALL CAVITY FILL PIECE F05 240 X 1082 7 SIDE UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211536 | WALL CAVITY FILL PIECE F06 230 9 X 1082 7 SIDE UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211537 | WALL CAVITY FILL PIECE F07 205 5 X 1082 7 SIDE UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211538 | WALL CAVITY FILL PIECE F08 214 X 1082 7 SIDE UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211614 | WALL CAVITY FILL PIECE F09 274 7 X 1078 6 BACK LOWER B1 | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211615 | WALL CAVITY FILL PIECE F10 274 7 X 1078 6 BACK LOWER B1 | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211616 | WALL CAVITY FILL PIECE F11 274 7 X 1078 6 BACK LOWER B1 | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211634 | WALL CAVITY FILL PIECE F12 274 7 X 1078 6 BACK UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211635 | WALL CAVITY FILL PIECE F13 274 7 X 1078 6 BACK UPPER COMMON | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |
| 211636 | WALL CAVITY FILL PIECE F14 274 7 X 1078 6 BACK UPPER B3 | PR #401 | no | no | no | yes | no | no | — | K-P05 | open: BOM row, CAD, STEP, drawing |

## Bought parts

### BASE

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #396 | H-01 | yes | J-T1, T06 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2 | PR #396 | H-03 | yes | J-T1, K-J19, T06 | done |
| 838010 | HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2 | PR #396 | H-31 | yes | J-T6 | done |
| 838006 | HARDWARE - RIVET NUT - M10 - STEEL ZINC - SHEREX CAL2-1015-7.9 | PR #396 | H-26 | HOLD | no | HOLD |
| 118001 | BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD | PR #396 | H-06 | HOLD | J-T4 | HOLD |
| 838007 | HARDWARE - COUNTERSUNK SCREW - M3 X 8 - ISO 10642 A2 | PR #396 | H-28 | yes | no | open: test |
| 838008 | HARDWARE - RIVET NUT - M3 - COUNTERSUNK HEAD - HOLD | PR #396 | H-29 | HOLD | no | HOLD |

### CEILING

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 518001 | LINING - CASSETTE CLIP | PR #348 | H-10 | HOLD | K-L11, T07 | HOLD |
| 518002 | LINING - CEILING SAFETY CATCH | PR #348 | H-11 | HOLD | T08 | HOLD |
| 108002 | POD - ACP BOND SET - SIKAFLEX-252 WITH AKTIVATOR-205, PRIMER-210, FIXING TAPE | PR #348 | H-12 | yes | T09 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #348 | H-01 | yes | J-T1, T06 | done |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | PR #348 | H-01P | yes | J-T1 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2 | PR #348 | H-03 | yes | J-T1, K-J19, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #348 | H-09 | yes | T06 | done |
| 838005 | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE | PR #348 | H-02 | HOLD | J-T2 | HOLD |
| 848001 | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA | PR #348 | H-04 | HOLD | J-T3 | HOLD |
| 848004 | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE | PR #348 | H-04B | HOLD | J-T3, J-T5 | HOLD |

### CEILING (builds AIR, D-80)

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 618101 | AIR - SENSOR HUB ZONE - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618104 | AIR - SOFFIT HANGER STUD - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618105 | AIR - SOFFIT UNDERSIDE HINGE - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618106 | AIR - SOFFIT UNDERSIDE LATCH - HOLD | PR #378 | n/a (team-numbered) | HOLD | K-A07 | HOLD |
| 618401 | AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM | PR #378 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618102 | AIR - SUPPLY TRANSITION - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618103 | AIR - RISER TRANSITION - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618402 | AIR - FAN BOX PAD - SUPPLY - RUBBER 40 X 15 X 5 - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 618501 | AIR - RISER BUFFER - RUBBER - M6 - HOLD | PR #378 | n/a (team-numbered) | HOLD | no | HOLD |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | PR #378 | H-01P | yes | J-T1 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #378 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #378 | H-09 | yes | T06 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2 | PR #378 | H-03 | yes | J-T1, K-J19, T06 | done |

### CEILING (builds INTERIOR, D-80)

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 818101 | INTERIOR - LEDGE BRACKET - HOLD | PR #356 | H-32 | HOLD | no | HOLD |
| 818102 | INTERIOR - SCREEN RAIL - HOLD | PR #356 | H-33 | HOLD | no | HOLD |

### ELECTRICAL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 718001 | ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2 - MEAN WELL LPV-60-12 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718081 | ELECTRICAL - 24 V SUPPLY - 60 W CLASS 2 - MEAN WELL LPV-60-24 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718082 | ELECTRICAL - 24 V SUPPLY - 96 W CLASS 2 - VOICE KIT - MEAN WELL CLG-100-24 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718002 | ELECTRICAL - LED CONTROLLER - 5 CHANNEL 12-24 V PWM - DMX512 - LTECH LT-995 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718003 | ELECTRICAL - CIRCUIT BREAKER - 1P 15 A C - UL 489 - EATON FAZ-C15/1-NA-L | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718004 | ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP - NEUTRIK NAC3MPX-TOP | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718005 | ELECTRICAL - INLET SEALING CAP - NEUTRIK SCNAC-01 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718006 | ELECTRICAL - LAN JACK - ETHERCON CAT6 - IDC - NEUTRIK NE8FDY-C6-B | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718007 | ELECTRICAL - RECEPTACLE - GFCI TR DUPLEX 15 A - NEMA 5-15R - P&S 1597TRW | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718010 | ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM - PHOENIX CONTACT NS 35/7,5 PERF 2000MM | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718011 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - LITTELFUSE FHAC0001ZXJ | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718012 | ELECTRICAL - FUSE - ATO 5 A 32 V - LITTELFUSE 0287005.PXCN | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718013 | ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS - LITTELFUSE 0287005.PXCN | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718019 | ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD - FABORY 51340.040.008 DIN 7985-H | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718049 | ELECTRICAL - SPACER - M4 X 2 MM - NYLON, BLACK | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718054 | ELECTRICAL - SCREW - 6-32 X 1/2 - OVAL HEAD, BLACK | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718047 | ELECTRICAL - CLINCH NUT - M4 - FOR 1.0 MM ALUMINIUM - PEM CLA-M4-1 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718014 | ELECTRICAL - EARTH STUD - M5 SELF-CLINCHING - PEM FHA-M5-12 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718079 | ELECTRICAL - NUT - M5 - SERRATED FLANGE - A2 - FABORY 51119.050.001 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718080 | ELECTRICAL - LEVER CONNECTOR - 5 CONDUCTOR - UL 486C - WAGO 221-415 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718015 | ELECTRICAL - BONDING WASHER - SERRATED M6 A2 - FABORY 51460.060.001 DIN 6798 A | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718016 | ELECTRICAL - RING TERMINAL - INSULATED 16-14 AWG - PANDUIT PV14-10R-C/PV14-14R-C | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718017 | ELECTRICAL - CONDUIT - FLEXIBLE NONMETALLIC 1/2 IN - ELECTRI-FLEX LIQUATITE NM-11 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #337 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #337 | H-09 | yes | T06 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2 | PR #337 | H-03 | yes | J-T1, K-J19, T06 | done |
| 718020 | ELECTRICAL - WIRE - UL 1015 14 AWG (BLACK, WHITE, GREEN) - ALPHA WIRE 461419 BK005/WH005/GR005 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718021 | ELECTRICAL - WIRE - UL 1015 14 AWG (BLACK, WHITE) - ALPHA WIRE 461419 BK005/WH005 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718022 | ELECTRICAL - WIRE - UL 1015 14 AWG GREEN - ALPHA WIRE 461419 GR005 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718073 | ELECTRICAL - CURRENT SENSE MODULE - 24 V 0-5 A | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718074 | ELECTRICAL - FEMALE DISCONNECT - 0.250 IN - 16-14 AWG - INSULATED - PANDUIT DNF14-250FIB-C | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718075 | ELECTRICAL - CONDUIT CONNECTOR - LFNC 1/2 IN - STRAIGHT - ELECTRI-FLEX NMLT-11 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718026 | ELECTRICAL - CABLE - 4 X 20 AWG SCREENED - PLENUM - BELDEN 6402FE | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718051 | ELECTRICAL - LED STRIP - 24 V 3.0 W/M - 3000 K - 8 MM - HÄFELE 833.76.216 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718052 | ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M - HÄFELE 833.72.861 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718076 | ELECTRICAL - CALL LIGHT PROFILE END CAP (PAIR) - HÄFELE 833.72.853 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718044 | ELECTRICAL - DRAW CORD - NYLON 3 MM - ERIN ROPE SBN041000 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718048 | ELECTRICAL - SCREW - M4 X 12 - ISO 7045 A2 PAN HEAD, BLACK | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718060 | ELECTRICAL - SENSOR HUB - DESK PRO AI (IN-HOUSE) | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718061 | ELECTRICAL - PUSH BUTTON - MOMENTARY - BOOST - E-SWITCH PV16F2B0SS | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718062 | ELECTRICAL - PUSH BUTTON - MOMENTARY - CALL - E-SWITCH PV16F2B0SS | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718063 | ELECTRICAL - LIGHT KNOB - POTENTIOMETER WITH KNOB | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718069 | ELECTRICAL - PUSH BUTTON - MOMENTARY - SELF-TEST - E-SWITCH PV16F2B0SS | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718064 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - COLUMN - LITTELFUSE FHAC0001ZXJ | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718065 | ELECTRICAL - INLET TEMPERATURE SENSOR | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718066 | ELECTRICAL - FUSE - ATO 2 A 32 V - LITTELFUSE 0287002.PXCN | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718067 | ELECTRICAL - FUSE - ATO 1 A 32 V - LITTELFUSE 0287001.PXCN | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718068 | ELECTRICAL - FAN Y-CABLE - 4-PIN PWM | PR #337 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718070 | ELECTRICAL - CORD CONNECTOR - POWERCON TRUE1 TOP - NEUTRIK NAC3F-TRUE1-S | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718071 | ELECTRICAL - CORD - SJOOW 14/3 - CAROL 01360 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718072 | ELECTRICAL - MAINS PLUG - NEMA 5-15P - LEVITON 5266-C | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718023 | ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2 - SOUTHWIRE R40018-1 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718024 | ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2 - SOUTHWIRE R40049-1 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718055 | ELECTRICAL - CABLE - 4 X 16 AWG - CLASS 2 - SOUTHWIRE 94664 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718029 | ELECTRICAL - CABLE - 6 X 18 AWG - CLASS 2 - SOUTHWIRE R40015-1 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718025 | ELECTRICAL - CABLE - 6 X 24 AWG SCREENED - CLASS 2 - BELDEN 9536 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718028 | ELECTRICAL - CABLE - CAT6 U/UTP - BELDEN 3612 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718030 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 2 WAY V-0 - MOLEX 39-01-2025 (5557-02R) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718031 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 2 WAY V-0 - MOLEX 39-01-3029 (5559-02P1) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718045 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0 - MOLEX 39-01-2065 (5557-06R) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718046 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0 - MOLEX 39-01-3069 (5559-06P1) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718032 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0 - MOLEX 39-01-2045 (5557-04R) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718033 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0 - MOLEX 39-01-3049 (5559-04P1) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718034 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0 - MOLEX 39-01-2105 (5557-10R) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718035 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0 - MOLEX 39-01-3109 (5559-10P1) | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718036 | ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN - MOLEX 39-00-0039 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718037 | ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN - MOLEX 39-00-0041 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718038 | ELECTRICAL - RJ45 PLUG - CAT6 - PANDUIT SP688E-C | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718039 | ELECTRICAL - RJ45 INLINE COUPLER - CAT6 - PANDUIT CC688IW | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718040 | ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP - PANDUIT NK688MWH | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718056 | ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 16 AWG TIN - MOLEX 39-00-0078 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718057 | ELECTRICAL - TERMINAL - MINI-FIT JR MALE 16 AWG TIN - MOLEX 39-00-0082 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718077 | ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 22-28 AWG TIN - MOLEX 39-00-0047 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718078 | ELECTRICAL - TERMINAL - MINI-FIT JR MALE 22-28 AWG TIN - MOLEX 39-00-0049 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718041 | ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON - HEYCO 2836N | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718042 | ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET - HEYCO 12431 DS-125 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718043 | ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY - HEYCO 3904 PMT 150 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718050 | ELECTRICAL - LED STRIP - 24 V 6.0 W/M - 3000 K - 8 MM - HÄFELE 833.76.226 | PR #337 | n/a (team-numbered) | yes | F-06 | done |
| 718053 | ELECTRICAL - LED STRIP FEED LEAD - 24 V - 8 MM - HÄFELE 833.75.763 | PR #337 | n/a (team-numbered) | no | F-06 | open: maker and SKU |
| 718101 | ELECTRICAL - LED PROFILE - LIGHT SHELF - SURFACE 23 X 12.5 | PR #337 | n/a (team-numbered) | HOLD | F-06, F-07 | HOLD |
| 718102 | ELECTRICAL - LED PROFILE COVER - SATIN - CLIP-IN | PR #337 | n/a (team-numbered) | HOLD | F-06, F-07 | HOLD |
| 718103 | ELECTRICAL - LED PROFILE END CAP | PR #337 | n/a (team-numbered) | HOLD | F-06, F-07 | HOLD |
| 718104 | ELECTRICAL - LED PROFILE MOUNTING CLIP | PR #337 | n/a (team-numbered) | HOLD | F-06, F-07 | HOLD |

### FRONT

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 368005 | FRONT - FRAME-STOP SEAL | PR #378 | H-20 | yes | F-03 | done |
| 368007 | FRONT - DOOR CATCH - IN DT | PR #378 | H-23 | yes | F-02 | done |
| 848013 | SEALS - ACCESS PANEL SEAL - 4.0 THICK - VERY SOFT FOAM PSA | PR #378 | H-34 | HOLD | T06 | HOLD |
| 368001 | FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112 | PR #339 | H-15 | yes | T13 | done |
| 368002 | FRONT - GLAZING U-SEAL - BOHLE BO5201735 | PR #339 | H-16 | yes | F-03 | done |
| 368101 | FRONT - DOOR HINGE - HOLD | PR #339 | H-21 | HOLD | T13 | HOLD |
| 368102 | FRONT - DOOR STRIKE | PR #339 | H-22 | yes | F-02 | done |
| 368006 | FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD | PR #339 | H-18 | HOLD | T13 | HOLD |
| 368103 | FRONT - DOOR PULL PAIR - HOLD | PR #339 | H-24 | HOLD | T13 | HOLD |
| 368008 | FRONT - DOOR KICK STRIP END SEAL - BRUSH - HOLD | PR #339 | H-43 | HOLD | no | HOLD |
| 368009 | FRONT - DOOR KICK STRIP HINGE END SEAL - BRUSH - HOLD | PR #339 | H-46 | HOLD | no | HOLD |
| 368004 | FRONT - GLAZING U-PROFILE - BOHLE BO5201571 | PR #339 | H-19 | yes | F-03 | done |
| 368003 | FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD | PR #339 | H-17 | HOLD | T13 | HOLD |

### WALL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 108002 | POD - ACP BOND SET - SIKAFLEX-252 WITH AKTIVATOR-205, PRIMER-210, FIXING TAPE | PR #401 | H-12 | yes | T09 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAL2-610-4.2 | PR #401 | H-03 | yes | J-T1, K-J19, T06 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #401 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #401 | H-09 | yes | T06 | done |
| 838005 | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE | PR #401 | H-02 | HOLD | J-T2 | HOLD |
| 848001 | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA | PR #401 | H-04 | HOLD | J-T3 | HOLD |
| 848015 | SEALS - CASSETTE LEDGE PAD - 18 X 2.36 - PORON 4701-40 320 PSA | PR #401 | no | no | no | open: register row, maker and SKU, test |
| 838012 | HARDWARE - BLIND RIVET - CLOSED END - COUNTERSUNK - ISO 15974 - AL/ST - 3.2 X 8 | PR #401 | no | yes | K-J20 | open: register row |
| 518003 | LINING - CASSETTE CLIP - WALL - FASTMOUNT MC-F10 + MC-SM5 | PR #401 | no | yes | no | open: register row, test |
| 848011 | SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY | PR #401 | H-13 | no | no | open: maker and SKU, test |
| 848016 | SEALS - CASSETTE JOINT STRIP - 10 X 2.36 - PORON 4701-40 320 PSA | PR #401 | no | yes | no | open: register row, test |
| 848012 | SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN | PR #401 | H-14 | HOLD | F-03 | HOLD |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | PR #401 | H-01P | yes | J-T1 | done |
| 848004 | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE | PR #401 | H-04B | HOLD | J-T3, J-T5 | HOLD |

## Joints-register items no parts list uses yet

| Part | Register | Name |
|---|---|---|
| 108001 | H-07 | POD - HEX KEY - 5 MM BALL END |
| 118002 | H-25 | BASE - LEVELLING GLIDE - M10 - HOLD |
| 118003 | H-27 | BASE - TUBE END CAP - 100 X 40 - BLACK - HOLD |
| 838011 | H-44 | HARDWARE - WASHER - M6 PLAIN - ISO 7089 6.4 X 12 200HV ZINC |

## How it's built

`python3 v2/00-Control/build_release_checklist.py --open-prs` reads origin/main and every open PR that changes parts, through the master BOM's reader (a later branch adds only the files it changed), the files named `PARTNO_REV_NAME_DOCTYPE.ext` in `v2/01-CAD-Native`, `v2/02-Drawings` and `v2/03-Manufacturing`, the FAI plan (`v2/06-Verification/fai-plan.md`) and the test plans. Without `--open-prs` it reads this working tree.

- A part's CAD and STEP may sit in its assembly's file; its DXF and drawing carry its own number, except as D-89 allows, read as the mechanical check reads them: a drawing whose text says TABULATED covers the other numbers of its family and kind that it lists; a felt or fill piece needs no drawing or DXF when a cut-list or parts-list row gives its number, size, material and tolerance and names no pockets, notches or holes (the mechanical check also counts the holes and faces in its STEP); another soft good cut from sheet or roll (foam, gasket, seal or tape, by the name's last word in its function field) needs no drawing when its DXF gives the outline, or, as a plain strip or rectangle, when such a row also gives its thickness; a flat part cut from sheet needs no drawing when it has its own DXF and its row's process names laser, waterjet or router cutting and no bend, fold, groove, lap, machining, drilling, tapping, welding or bonding, and the row gives material, thickness, finish and an ISO 2768 general tolerance. The checklist can't tell which holes are critical, so a critical-hole note is left to the drawing review. The DXF may draw only on the CUT and MARK layers (the guideline's layers, section 9; every entity in its ENTITIES section counts except the BLOCK, ENDBLK, VERTEX and SEQEND records, and a stored block only where an INSERT places it, its layer-0 shapes taking the INSERT's layer): a line on any other layer (BEND, a pocket, an engraving, a half-lap) keeps the drawing whatever the process says. Assemblies always keep their drawings. Part (4) is for flat metal sheet and flat ACP (D-99, D-100): glass and other materials keep their drawings, and a routed-and-folded ACP part keeps its own through its groove and fold layers.
- ELECTRICAL's 710000 is drawn by its wiring diagram, whose sheet 3 holds the route and joint views (D-93).
- The base corner and inline keys 111211 to 111214, and any part whose model sits in a joints folder, count under JOINTS: the Joints Engineer makes them and the teams place them by reference (D-95).
- A DXF is asked of sheet, felt, fill, foam, ply and glass parts; a cut list (or the list's cut rows) of tube parts.
- D-125 (a plain strip or sheet on a full parts-list row) is read by the mechanical check's own functions and STEP reader (tools/checks), from the working tree only, as C05 reads it: a strip that exists only on an open branch shows as needing a drawing until it merges. A made part with nothing else missing whose own material, grade or status says HOLD shows HOLD. HOLD counts only as a whole word, here and in the joints register: "on hold" does; "holds", "holder" and "threshold" don't.
- D-113: the parts tools/drawgen draws (its specs.py: 111101, 111102, 111103, 111106, 211101, 211102) are never blocked by a locked screen, because drawgen doesn't run in Fusion.
- D-128 (a felt or fill piece with through-openings or edge notches on its DXF and a full parts-list row) is read by the mechanical check's own functions (prism_shapes, felt_dxf_lacks), from the working tree only, as C05 reads it; a plain rectangle on a full cut-list row passes on D-89 first.
- Finish is asked of metal parts: a `finish` column, or a coating named in the material.
- FAI: the plan's characteristics whose patterns match the number. Bought parts: the plan's section H, or a test that names the number or its register ID.
- A register number's product status comes from the joints register: on HOLD, or named (DECIDED or from a source), or left to the parts list; a team number's from its parts list.
