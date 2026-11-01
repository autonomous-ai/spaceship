# Release checklist: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-009 | P01 | DRAFT, written by `build_release_checklist.py` | 2026-11-01 | Control pack |

What stands between the design and a manufacturing release, part by part. Nothing here is released (guideline milestone 4, REQ-DOC-02). Re-run it whenever parts merge.

Read from: main (f9d8c11), PR #91 (0cb3135), PR #105 (bc3f023), PR #203 (1b3fa40), PR #202 (803aec9). The Mac's screen at run time: **unlocked**. 452 files in the CAD, drawing and manufacturing folders; the FAI plan's 86 characteristics, 11 functional checks and 19 bought-part test lines.

**Done**: nothing missing from the columns below; a test counts once it is named, and its result belongs in the FAI plan. **Open**: something missing that can be done now. **Blocked**: only the drawing is missing and the screen is locked; the drawing start needs it unlocked (D-84). **HOLD**: a bought part whose product isn't named yet, or a made part with nothing else missing whose material, grade or status says HOLD (PM, 2026-11-01).

## Totals per team

| Team | Made: done | Made: open | Made: blocked by the locked screen | Made: HOLD | Bought: done | Bought: open | Bought: HOLD |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASE | 3 | 3 | 0 | 3 | 3 | 0 | 4 |
| CEILING | 3 | 11 | 0 | 0 | 5 | 0 | 5 |
| CEILING (builds AIR, D-80) | 8 | 17 | 0 | 6 | 1 | 0 | 7 |
| CEILING (builds INTERIOR, D-80) | 0 | 9 | 0 | 0 | 0 | 0 | 2 |
| ELECTRICAL | 8 | 2 | 0 | 2 | 3 | 0 | 65 |
| FRONT | 4 | 18 | 0 | 0 | 4 | 1 | 5 |
| JOINTS | 2 | 4 | 0 | 0 | 0 | 0 | 0 |
| WALL | 8 | 34 | 0 | 0 | 5 | 1 | 5 |
| **All, each number once** | 36 | 98 | 0 | 11 | 10 | 2 | 89 |

98 of the 145 made numbers have no drawing yet; for 80 of them the drawing is the only gap, so their drawings can start now (D-84).

What the open made numbers miss: drawing 98, DXF or cut list 15, BOM row 3, CAD 3.

## Made parts with no FAI line

Every made number has at least one line in the FAI plan (`v2/06-Verification/fai-plan.md`).

## Made parts and assemblies

### BASE

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 110000 | BASE | main | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01, K-B05, K-B06, K-B07 | open: drawing |
| 110101 | BASE - BAND ASSY - SIDE - LH | main | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01 | open: drawing |
| 111101 | BASE - BAND TUBE - SIDE - LH | main | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 111601 | BASE - GLIDE DOUBLER - COMMON | main | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-B09 | done |
| 110103 | BASE - BAND ASSY - BACK | main | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01 | open: drawing |
| 111103 | BASE - BAND TUBE - BACK | main | yes | yes | yes | yes | yes | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01, K-B10 | done |
| 110401 | BASE - FLOOR PANEL ASSY - F1 | main | yes | yes | yes | n/a | yes | yes | n/a | K-J13, K-J14, K-F06, K-B01 | HOLD |
| 111401 | BASE - FLOOR PANEL - F1 | main | yes | yes | yes | yes | yes | yes | n/a | K-B02, K-B03 | HOLD |
| 111501 | BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-B04 | HOLD |

### CEILING

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 410000 | CEILING | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 410101 | CEILING - PANEL ASSY - C1 | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 410102 | CEILING - PANEL ASSY - C2 | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 411101 | CEILING - PANEL FRAME - C1 | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17, K-P07 | open: drawing |
| 411102 | CEILING - PANEL FRAME - C2 | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17, K-P07 | open: drawing |
| 411301 | CEILING - SKIN - C1 | main | yes | yes | yes | yes | row: a plain strip or sheet (D-125) | yes | n/a | K-P03, K-P04 | done |
| 411302 | CEILING - SKIN - C2 | main | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04, K-P06 | done |
| 510301 | LINING - CASSETTE - CEILING - COMMON | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05, K-L10 | open: drawing |
| 513101 | LINING - TRAY - CEILING | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02, K-L06 | open: drawing |
| 513102 | LINING - RIB - CEILING | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02, K-L07 | open: drawing |
| 513201 | LINING - FELT - CEILING | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04, K-L08 | done |
| 513301 | LINING - FILL - CEILING - BAY A | main | yes | yes | yes | yes | no | yes | n/a | K-P05, K-L09 | open: drawing |
| 513302 | LINING - FILL - CEILING - BAY B | main | yes | yes | yes | yes | no | yes | n/a | K-P05, K-L09 | open: drawing |
| 513303 | LINING - FILL - CEILING - BAY C | main | yes | yes | yes | yes | no | yes | n/a | K-P05, K-L09 | open: drawing |

### CEILING (builds AIR, D-80)

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 610000 | AIR | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 610101 | AIR - AIR COLUMN | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611106 | AIR - COLUMN FOOT PLATE | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611101 | AIR - COLUMN FACE - FRONT | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611102 | AIR - COLUMN FACE - LEFT | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611103 | AIR - COLUMN CORNER ANGLE | PR #91 | yes | yes | yes | n/a | no | yes | yes | K-A01, K-A02, K-A03 | open: drawing |
| 611107 | AIR - COLUMN PLENUM SIDE PLATE - LOW | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611108 | AIR - COLUMN PLENUM SIDE PLATE - HIGH | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611104 | AIR - COLUMN FILL | PR #91 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611105 | AIR - KICK GRILLE | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 610301 | AIR - SPLITTER CARTRIDGE - COMMON | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611301 | AIR - CARTRIDGE CASING | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611302 | AIR - CARTRIDGE LAYER 50 | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 610201 | AIR - SOFFIT | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611201 | AIR - SOFFIT UNDERSIDE - LEFT HINGED | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611207 | AIR - SOFFIT UNDERSIDE - RIGHT HINGED | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611208 | AIR - SOFFIT UNDERSIDE - FIXED OVER THE COLUMN | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611202 | AIR - SOFFIT FACE - FRONT | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611205 | AIR - SOFFIT TOP RAIL - DOOR SIDE | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611209 | AIR - SOFFIT TOP RAIL - ROOM SIDE | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611206 | AIR - SOFFIT END PLATE - LEFT | PR #91 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-A01, K-A02, K-A03 | HOLD |
| 611210 | AIR - SOFFIT DOOR-SIDE PLATE | PR #91 | yes | yes | yes | yes | no | yes | yes | K-A01, K-A02, K-A03 | open: drawing |
| 611203 | AIR - SOFFIT FILL | PR #91 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-A01, K-A02, K-A03 | done |
| 611204 | AIR - EXHAUST GRILLE | PR #91 | yes | yes | yes | yes | no | yes | yes | K-A01, K-A02, K-A03 | open: drawing |
| 610402 | AIR - EXHAUST FAN BOX | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03 | open: drawing |
| 611401 | AIR - FAN BOX CASING - EXHAUST | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 610401 | AIR - SUPPLY FAN BOX | PR #91 | yes | yes | yes | n/a | no | yes | n/a | K-A01, K-A02, K-A03, K-A05 | open: drawing |
| 611402 | AIR - FAN BOX CASING - SUPPLY | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611501 | AIR - INTAKE RISER | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03, K-A04 | open: DXF or cut list, drawing |
| 611601 | AIR - ROOF SLEEVE | PR #91 | yes | yes | yes | no | no | yes | yes | K-A01, K-A02, K-A03 | open: DXF or cut list, drawing |
| 611602 | AIR - ROOF GRILLE | PR #91 | yes | yes | yes | yes | no | yes | yes | K-A01, K-A02, K-A03 | open: drawing |

### CEILING (builds INTERIOR, D-80)

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 810000 | INTERIOR | main | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 810101 | INTERIOR - WORK WALL LEDGE ASSY | main | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 811101 | INTERIOR - LEDGE - TOP | main | yes | yes | yes | yes | no | yes | yes | K-A02, K-I01, K-I02 | open: drawing |
| 810201 | INTERIOR - LIGHT SHELF ASSY | main | yes | yes | yes | n/a | no | yes | n/a | K-A02, K-I01 | open: drawing |
| 811201 | INTERIOR - LIGHT SHELF - BACK | main | yes | yes | yes | yes | no | yes | yes | K-A02, K-I01, K-I03 | open: drawing |
| 811202 | INTERIOR - LIGHT SHELF - SIDE LH | main | yes | yes | yes | yes | no | yes | yes | K-A02, K-I01, K-I03 | open: drawing |
| 811203 | INTERIOR - LIGHT SHELF - SIDE RH | main | yes | yes | yes | yes | no | yes | yes | K-A02, K-I01, K-I03 | open: drawing |
| 811204 | INTERIOR - LIGHT SHELF - DOWN CHANNEL RH | main | yes | yes | yes | yes | no | yes | yes | K-A02, K-I01, K-I04 | open: drawing |
| 811205 | INTERIOR - LIGHT SHELF - DIFFUSER RH | main | yes | yes | yes | n/a | no: as a plain strip or sheet (D-125) its row in v2/03-Manufacturing/interior/810000_P01_INTERIOR-PARTS-LIST_BOM.csv doesn't give a tolerance on the width (one general tolerance on the cut sizes, such as ISO 2768-m or '±0.5 on cut sizes', or one for each; 'width as supplied' for a bought strip) | yes | n/a | K-A02, K-I01, K-I05 | open: drawing |

### ELECTRICAL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 710000 | ELECTRICAL | main | yes | yes | yes | n/a | yes: its wiring diagram, routes and joints on sheet 3 (D-93) | yes | n/a | K-E01 | done |
| 710001 | ELECTRICAL - POWER UNIT - B2 | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 711001 | ELECTRICAL - POWER UNIT - ENCLOSURE BODY | main | yes | yes | yes | yes | no | yes | yes | K-E01, K-E02 | open: drawing |
| 711002 | ELECTRICAL - POWER UNIT - FRONT PLATE | main | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-F06, K-E01, K-E03 | HOLD |
| 710011 | ELECTRICAL - HARNESS - LIGHT FEED - B2/B4 | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710021 | ELECTRICAL - HARNESS - TRUNK - B2/R1 | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710023 | ELECTRICAL - HARNESS - AIR COLUMN | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710024 | ELECTRICAL - HARNESS - CALL LIGHT - R2 | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710031 | ELECTRICAL - DRAW WIRE - CEILING ROUTE | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 710041 | ELECTRICAL - HUB AND CONTROLS ZONE | main | yes | yes | yes | n/a | yes | yes | n/a | K-E01 | done |
| 711005 | ELECTRICAL - HUB ZONE COVER PLATE | main | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-F06, K-E01, K-E04 | HOLD |
| 719001 | ELECTRICAL - CORD SET - 220 V VN - 3 M (KIT) | main | yes | yes | yes | n/a | no | yes | n/a | K-E01 | open: drawing |

### FRONT

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 350001 | FRONT - DECOR BLOCK ASSY - DL | PR #105 | yes | yes | yes | n/a | no | yes | n/a | K-D18 | open: drawing |
| 351101 | FRONT - DECOR SKIN - DL | PR #105 | yes | yes | yes | yes | no | yes | n/a | K-D19 | open: drawing |
| 351104 | FRONT - DECOR FRAME - DL | PR #105 | yes | yes | yes | yes | no | yes | yes | K-D20 | open: drawing |
| 351102 | FRONT - DECOR BACK PLATE - DL | PR #105 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D21 | done |
| 351103 | FRONT - DOOR HINGE-SIDE STOP - DL | PR #105 | yes | yes | yes | no | no | yes | yes | K-D22 | open: DXF or cut list, drawing |
| 350002 | FRONT - DECOR BLOCK ASSY - DT | PR #105 | yes | yes | yes | n/a | no | yes | n/a | K-D13 | open: drawing |
| 351201 | FRONT - DECOR SKIN - DT | PR #105 | yes | yes | yes | yes | no | yes | n/a | K-D14 | open: drawing |
| 351204 | FRONT - DECOR FRAME - DT | PR #105 | yes | yes | yes | yes | no | yes | yes | K-D15 | open: drawing |
| 351202 | FRONT - DECOR BACK PLATE - DT | PR #105 | yes | yes | yes | yes | no | yes | n/a | K-D16 | open: drawing |
| 351203 | FRONT - DOOR TOP STOP - DT | PR #105 | yes | yes | yes | no | no | yes | yes | K-D17 | open: DXF or cut list, drawing |
| 350003 | FRONT - DECOR BLOCK ASSY - DR | PR #105 | yes | yes | yes | n/a | no | yes | n/a | K-D01, K-D02 | open: drawing |
| 351301 | FRONT - DECOR SKIN - DR | PR #105 | yes | yes | yes | yes | no | yes | n/a | K-D03 | open: drawing |
| 351306 | FRONT - DECOR FRAME - DR | PR #105 | yes | yes | yes | yes | no | yes | yes | K-D04, K-D05 | open: drawing |
| 351302 | FRONT - DECOR BACK PLATE - DR | PR #105 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D06 | done |
| 351305 | FRONT - DECOR ACCESS PANEL - DR | PR #105 | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-D07 | done |
| 351303 | FRONT - DECOR INNER PANEL - DR | PR #105 | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-D08 | done |
| 351304 | FRONT - DECOR INNER PANEL FELT - DR | PR #105 | yes | yes | yes | yes | no | yes | n/a | K-D09 | open: drawing |
| 360001 | FRONT - DOOR UNIT | main | yes | yes | yes | n/a | no | yes | n/a | K-F07, K-F08 | open: drawing |
| 361001 | FRONT - DOOR LEAF - 4+4 LAMINATED | main | yes | yes | yes | yes | no | yes | n/a | K-F01, K-F02 | open: drawing |
| 361002 | FRONT - DOOR KICK STRIP | main | yes | yes | yes | yes | no | yes | yes | K-F05, K-F06 | open: drawing |
| 360002 | FRONT - FIXED GLASS UNIT | main | yes | yes | yes | n/a | no | yes | n/a | K-F03, K-F04 | open: drawing |
| 361003 | FRONT - FIXED GLASS - 4+4 LAMINATED | main | yes | yes | yes | yes | no | yes | n/a | K-F01, K-F02 | open: drawing |

### JOINTS

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 831001 | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS | main | yes | yes | yes | n/a | yes | yes | yes | K-J07 | done |
| 831002 | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL | main | yes | yes | yes | yes | DXF and row (D-89) | yes | yes | K-J08 | done |
| 111211 | BASE - CORNER KEY - BACK - COMMON | main | yes | yes | yes | no | no | yes | yes | K-B08 | open: DXF or cut list, drawing |
| 111212 | BASE CORNER KEY FRONT LH | main | no | no | yes | — | no | no | — | K-B08 | open: BOM row, CAD, drawing |
| 111213 | BASE CORNER KEY FRONT RH | main | no | no | yes | — | no | no | — | K-B08 | open: BOM row, CAD, drawing |
| 111214 | BASE CORNER KEY KNEE LH | main | no | no | yes | — | no | no | — | K-B08 | open: BOM row, CAD, drawing |

### WALL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 210101 | WALL - PANEL ASSY - SIDE LOWER - LH | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211101 | WALL - PANEL FRAME - SIDE LOWER - LH | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211301 | WALL - SKIN - SIDE LOWER - LH | main | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 211501 | WALL - CAVITY FILL - SIDE LOWER - LH | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510101 | LINING - CASSETTE - SIDE LOWER - LH | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511101 | LINING - TRAY - SIDE LOWER - LH | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511301 | LINING - FELT - SIDE LOWER - LH | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210102 | WALL - PANEL ASSY - SIDE LOWER - RH | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211102 | WALL - PANEL FRAME - SIDE LOWER - RH | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211302 | WALL - SKIN - SIDE LOWER - RH | main | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 211502 | WALL - CAVITY FILL - SIDE LOWER - RH | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510102 | LINING - CASSETTE - SIDE LOWER - RH | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511102 | LINING - TRAY - SIDE LOWER - RH | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511302 | LINING - FELT - SIDE LOWER - RH | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210103 | WALL - PANEL ASSY - SIDE UPPER - LH | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211103 | WALL - PANEL FRAME - SIDE UPPER - LH | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211303 | WALL - SKIN - SIDE UPPER - LH | main | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 211503 | WALL - CAVITY FILL - SIDE UPPER - LH | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510103 | LINING - CASSETTE - SIDE UPPER - LH | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511103 | LINING - TRAY - SIDE UPPER - LH | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511303 | LINING - FELT - SIDE UPPER - LH | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210104 | WALL - PANEL ASSY - SIDE UPPER - RH | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211104 | WALL - PANEL FRAME - SIDE UPPER - RH | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211304 | WALL - SKIN - SIDE UPPER - RH | main | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 211504 | WALL - CAVITY FILL - SIDE UPPER - RH | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510104 | LINING - CASSETTE - SIDE UPPER - RH | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511104 | LINING - TRAY - SIDE UPPER - RH | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511304 | LINING - FELT - SIDE UPPER - RH | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210201 | WALL - PANEL ASSY - BACK LOWER - B1 | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211201 | WALL - PANEL FRAME - BACK LOWER - B1 | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211401 | WALL - SKIN - BACK LOWER - B1 | main | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04 | done |
| 211601 | WALL - CAVITY FILL - BACK LOWER - B1 | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510201 | LINING - CASSETTE - BACK LOWER - B1 | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511201 | LINING - TRAY - BACK LOWER - B1 | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511401 | LINING - FELT - BACK LOWER - B1 | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |
| 210202 | WALL - PANEL ASSY - BACK LOWER - B2 | main | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211202 | WALL - PANEL FRAME - BACK LOWER - B2 | main | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16, K-J17 | open: drawing |
| 211402 | WALL - SKIN - BACK LOWER - B2 | main | yes | yes | yes | yes | DXF and row (D-89) | yes | n/a | K-P03, K-P04 | done |
| 211602 | WALL - CAVITY FILL - BACK LOWER - B2 | main | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 510202 | LINING - CASSETTE - BACK LOWER - B2 | main | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511202 | LINING - TRAY - BACK LOWER - B2 | main | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511402 | LINING - FELT - BACK LOWER - B2 | main | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |

## Bought parts

### BASE

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 118002 | BASE - LEVELLING GLIDE - M10 - HOLD | main | H-25 | HOLD | no | HOLD |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | main | H-03 | yes | J-T1, T06 | done |
| 838006 | HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD | main | H-26 | HOLD | no | HOLD |
| 118003 | BASE - TUBE END CAP - 100 X 40 - BLACK - HOLD | main | H-27 | HOLD | no | HOLD |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | main | H-01 | yes | J-T1, T06 | done |
| 838010 | HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2 | main | H-31 | yes | J-T6 | done |
| 118001 | BASE - BASE SEAL - FLOOR EDGE - FIXED 4 GAP | main | H-06 | HOLD | J-T4 | HOLD |

### CEILING

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 518001 | LINING - CASSETTE CLIP | main | H-10 | HOLD | T07 | HOLD |
| 518002 | LINING - CEILING SAFETY CATCH | main | H-11 | HOLD | T08 | HOLD |
| 108002 | POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE | main | H-12 | yes | T09 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | main | H-01 | yes | J-T1, T06 | done |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | main | H-01P | yes | J-T1 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | main | H-03 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | main | H-09 | yes | T06 | done |
| 838005 | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE | main | H-02 | HOLD | J-T2 | HOLD |
| 848001 | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA | main | H-04 | HOLD | J-T3 | HOLD |
| 848004 | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE | main | H-04B | HOLD | J-T3, J-T5 | HOLD |

### CEILING (builds AIR, D-80)

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 618101 | AIR - SENSOR HUB ZONE - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618104 | AIR - SOFFIT HANGER STUD - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618105 | AIR - SOFFIT UNDERSIDE HINGE - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618106 | AIR - SOFFIT UNDERSIDE LATCH - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618401 | AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618102 | AIR - SUPPLY TRANSITION - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 618103 | AIR - RISER TRANSITION - HOLD | PR #91 | n/a (team-numbered) | HOLD | T04 | HOLD |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | PR #91 | H-01P | yes | J-T1 | done |

### CEILING (builds INTERIOR, D-80)

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 818101 | INTERIOR - LEDGE BRACKET - HOLD | main | H-32 | HOLD | no | HOLD |
| 818102 | INTERIOR - SCREEN RAIL - HOLD | main | H-33 | HOLD | no | HOLD |

### ELECTRICAL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 718001 | ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718002 | ELECTRICAL - LED CONTROLLER - 3 CHANNEL 12 V PWM - RS-485 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718003 | ELECTRICAL - RCBO - 1P+N C10 30 MA TYPE A | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718004 | ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718005 | ELECTRICAL - INLET SEALING CAP | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718006 | ELECTRICAL - LAN FEED-THROUGH - ETHERCON | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718007 | ELECTRICAL - USER SOCKET - UTEN S300 UNIVERSAL | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718008 | ELECTRICAL - LAN SOCKET - UTEN S300 TWO PORT | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718009 | ELECTRICAL - BACK BOX - 86 PLATE | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718010 | ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718011 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718012 | ELECTRICAL - FUSE - ATO 5 A 32 V | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718013 | ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718019 | ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718049 | ELECTRICAL - SPACER - M4 X 2 MM - NYLON, BLACK | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718047 | ELECTRICAL - CLINCH NUT - M4 - FOR 1.0 MM ALUMINIUM | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718014 | ELECTRICAL - EARTH STUD - M5 SELF-CLINCHING | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718015 | ELECTRICAL - BONDING WASHER - SERRATED M6 A2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718016 | ELECTRICAL - RING TERMINAL - INSULATED 1.5-2.5 MM2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718017 | ELECTRICAL - CONDUIT - PVC FLEXIBLE - 20 MM | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | main | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | main | H-09 | yes | T06 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | main | H-03 | yes | J-T1, T06 | done |
| 718020 | ELECTRICAL - WIRE - H07V-K 1.5 MM2 (BROWN, BLUE, GREEN-YELLOW) | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718021 | ELECTRICAL - WIRE - H05V-K 1.0 MM2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718022 | ELECTRICAL - WIRE - H07V-K 2.5 MM2 GREEN-YELLOW | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718073 | ELECTRICAL - CURRENT SENSE MODULE - 12 V 0-5 A | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718026 | ELECTRICAL - CABLE - 4 X 20 AWG | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718027 | ELECTRICAL - CABLE - 4 X 24 AWG SCREENED | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718051 | ELECTRICAL - LED STRIP - LOOX5 2165 - 12 V 3.0 W/M - 3000 K | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718052 | ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718044 | ELECTRICAL - DRAW CORD - NYLON 3 MM | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718048 | ELECTRICAL - SCREW - M4 X 12 - ISO 7045 A2 PAN HEAD, BLACK | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718060 | ELECTRICAL - SENSOR HUB - DESK PRO AI (IN-HOUSE) | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718061 | ELECTRICAL - PUSH BUTTON - MOMENTARY - BOOST | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718062 | ELECTRICAL - PUSH BUTTON - MOMENTARY - CALL | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718063 | ELECTRICAL - LIGHT KNOB - POTENTIOMETER WITH KNOB | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718069 | ELECTRICAL - PUSH BUTTON - MOMENTARY - SELF-TEST | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718064 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - COLUMN | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718065 | ELECTRICAL - INLET TEMPERATURE SENSOR | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718066 | ELECTRICAL - FUSE - ATO 2 A 32 V | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718067 | ELECTRICAL - FUSE - ATO 1 A 32 V | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718068 | ELECTRICAL - FAN Y-CABLE - 4-PIN PWM | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718070 | ELECTRICAL - CORD CONNECTOR - POWERCON TRUE1 TOP | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718071 | ELECTRICAL - CORD - H05VV-F 3G1.5 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718072 | ELECTRICAL - MAINS PLUG - VN OFFICE SOCKET | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718023 | ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718024 | ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718029 | ELECTRICAL - CABLE - 6 X 18 AWG - CLASS 2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718025 | ELECTRICAL - CABLE - 6 X 24 AWG SCREENED - CLASS 2 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718028 | ELECTRICAL - CABLE - CAT6 U/UTP | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718030 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 2 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718031 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 2 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718045 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718046 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718032 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718033 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718034 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718035 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718036 | ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718037 | ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718038 | ELECTRICAL - RJ45 PLUG - CAT6 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718039 | ELECTRICAL - RJ45 INLINE COUPLER - CAT6 | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718040 | ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718041 | ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718042 | ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718043 | ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY | main | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718050 | ELECTRICAL - LED STRIP - LOOX5 2168 - 12 V 6.0 W/M - 3000 K | main | n/a (team-numbered) | HOLD | F-06 | HOLD |

### FRONT

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 368005 | FRONT - FRAME-STOP SEAL | PR #105 | H-20 | no | F-03 | open: maker and SKU |
| 368007 | FRONT - DOOR CATCH - IN DT | PR #105 | H-23 | yes | F-02 | done |
| 368001 | FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112 | main | H-15 | yes | T13 | done |
| 368002 | FRONT - GLAZING U-SEAL - BOHLE BO5201735 | main | H-16 | yes | F-03 | done |
| 368101 | FRONT - DOOR HINGE - HOLD | main | H-21 | HOLD | T13 | HOLD |
| 368102 | FRONT - DOOR STRIKE | main | H-22 | HOLD | F-02 | HOLD |
| 368006 | FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD | main | H-18 | HOLD | T13 | HOLD |
| 368103 | FRONT - DOOR PULL PAIR - HOLD | main | H-24 | HOLD | T13 | HOLD |
| 368004 | FRONT - GLAZING U-PROFILE - BOHLE BO5201571 | main | H-19 | yes | F-03 | done |
| 368003 | FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD | main | H-17 | HOLD | T13 | HOLD |

### WALL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 108002 | POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE | main | H-12 | yes | T09 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | main | H-03 | yes | J-T1, T06 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | main | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | main | H-09 | yes | T06 | done |
| 838005 | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE | main | H-02 | HOLD | J-T2 | HOLD |
| 848001 | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA | main | H-04 | HOLD | J-T3 | HOLD |
| 518001 | LINING - CASSETTE CLIP | main | H-10 | HOLD | T07 | HOLD |
| 848011 | SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY | main | H-13 | no | no | open: maker and SKU, test |
| 848012 | SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN | main | H-14 | HOLD | F-03 | HOLD |
| 838002 | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC | main | H-01P | yes | J-T1 | done |
| 848004 | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE | main | H-04B | HOLD | J-T3, J-T5 | HOLD |

## Joints-register items no parts list uses yet

| Part | Register | Name |
|---|---|---|
| 108001 | H-07 | POD - HEX KEY - 5 MM BALL END |
| 838007 | H-28 | HARDWARE - COUNTERSUNK SCREW - M3 X 8 - ISO 10642 A2 |
| 838008 | H-29 | HARDWARE - RIVET NUT - M3 - COUNTERSUNK HEAD - HOLD |
| 838009 | H-30 | HARDWARE - THREADED INSERT - M6 - FOR 9 MM PLY - HOLD |
| 831003 | H-34 | HARDWARE - FRAME CORNER CLEAT - 20 X 40 - 45 DEG |
| 831004 | H-35 | HARDWARE - FRAME CORNER CLEAT - 40 X 40 - 45 DEG |
| 831005 | H-36 | HARDWARE - FRAME CORNER CLEAT - 40 X 40 TO 20 X 40 |
| 831006 | H-37 | HARDWARE - FRAME T PLUG - 20 X 40 STUD |
| 108003 | H-38 | POD - FRAME CLEAT ADHESIVE - SIKAFAST-5215 NT WITH SIKAFAST-5200 |

## How it's built

`python3 v2/00-Control/build_release_checklist.py --open-prs` reads origin/main and every open PR that changes parts, through the master BOM's reader (a later branch adds only the files it changed), the files named `PARTNO_REV_NAME_DOCTYPE.ext` in `v2/01-CAD-Native`, `v2/02-Drawings` and `v2/03-Manufacturing`, the FAI plan (`v2/06-Verification/fai-plan.md`) and the test plans. Without `--open-prs` it reads this working tree.

- A part's CAD and STEP may sit in its assembly's file; its DXF and drawing carry its own number, except as D-89 allows, read as the mechanical check reads them: a drawing whose text says TABULATED covers the other numbers of its family and kind that it lists; a felt or fill piece needs no drawing or DXF when a cut-list or parts-list row gives its number, size, material and tolerance and names no pockets, notches or holes (the mechanical check also counts the holes and faces in its STEP); another soft good cut from sheet or roll (foam, gasket, seal or tape, by the name's last word in its function field) needs no drawing when its DXF gives the outline, or, as a plain strip or rectangle, when such a row also gives its thickness; a flat part cut from sheet needs no drawing when it has its own DXF and its row's process names laser, waterjet or router cutting and no bend, fold, groove, lap, machining, drilling, tapping, welding or bonding, and the row gives material, thickness, finish and an ISO 2768 general tolerance. The checklist can't tell which holes are critical, so a critical-hole note is left to the drawing review. The DXF may draw only on the CUT and MARK layers (the guideline's layers, section 9; every entity in its ENTITIES section counts except the BLOCK, ENDBLK, VERTEX and SEQEND records, and a stored block only where an INSERT places it, its layer-0 shapes taking the INSERT's layer): a line on any other layer (BEND, a pocket, an engraving, a half-lap) keeps the drawing whatever the process says. Assemblies always keep their drawings. Part (4) is for flat metal sheet and flat ACP (D-99, D-100): glass and other materials keep their drawings, and a routed-and-folded ACP part keeps its own through its groove and fold layers.
- ELECTRICAL's 710000 is drawn by its wiring diagram, whose sheet 3 holds the route and joint views (D-93).
- The base corner and inline keys 111211 to 111214, and any part whose model sits in a joints folder, count under JOINTS: the Joints Engineer makes them and the teams place them by reference (D-95).
- A DXF is asked of sheet, felt, fill, foam, ply and glass parts; a cut list (or the list's cut rows) of tube parts.
- D-125 (a plain strip or sheet on a full parts-list row) is read by the mechanical check's own functions and STEP reader (tools/checks), from the working tree only, as C05 reads it: a strip that exists only on an open branch shows as needing a drawing until it merges. A made part with nothing else missing whose own material, grade or status says HOLD shows HOLD.
- Finish is asked of metal parts: a `finish` column, or a coating named in the material.
- FAI: the plan's characteristics whose patterns match the number. Bought parts: the plan's section H, or a test that names the number or its register ID.
- A register number's product status comes from the joints register: on HOLD, or named (DECIDED or from a source), or left to the parts list; a team number's from its parts list.
