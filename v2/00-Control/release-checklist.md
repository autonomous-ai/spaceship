# Release checklist: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-009 | P01 | DRAFT, written by `build_release_checklist.py` | 2026-11-01 | Control pack |

What stands between the design and a manufacturing release, part by part. Nothing here is released (guideline milestone 4, REQ-DOC-02). Re-run it whenever parts merge.

Read from: main (a722824), PR #27 (4696390), PR #28 (04ac4dd), PR #55 (9028182), PR #41 (9e318c5), PR #64 (d459495), PR #32 (a785016). The Mac's screen at run time: **unlocked**. 174 files in the CAD, drawing and manufacturing folders; the FAI plan's 47 characteristics, 11 functional checks and 18 bought-part test lines.

**Done**: nothing missing from the columns below; a test counts once it is named, and its result belongs in the FAI plan. **Open**: something missing that can be done now. **Blocked**: only the drawing is missing and the screen is locked; the drawing start needs it unlocked (D-84). **HOLD**: the product isn't named yet.

## Totals per team

| Team | Made: done | Made: open | Made: blocked by the locked screen | Bought: done | Bought: open | Bought: HOLD |
|---|---:|---:|---:|---:|---:|---:|
| BASE | 0 | 10 | 0 | 3 | 0 | 4 |
| CEILING | 0 | 13 | 0 | 1 | 0 | 2 |
| CEILING (builds AIR, D-80) | — | — | — | — | — | — |
| CEILING (builds INTERIOR, D-80) | — | — | — | — | — | — |
| ELECTRICAL | 0 | 12 | 0 | 3 | 0 | 64 |
| FRONT | 0 | 5 | 0 | 3 | 0 | 4 |
| WALL | 1 | 8 | 0 | 4 | 1 | 4 |
| **All, each number once** | 1 | 46 | 0 | 7 | 1 | 77 |

No parts list yet: CEILING (builds AIR, D-80), CEILING (builds INTERIOR, D-80).

45 of the 47 made numbers have no drawing yet; for 31 of them the drawing is the only gap, so their drawings can start now (D-84).

What the open made numbers miss: drawing 45, CAD 12, STEP 12, DXF or cut list 6.

## Made parts and assemblies

### BASE

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 110000 | BASE | PR #55 | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01, K-B05, K-B06, K-B07 | open: drawing |
| 110101 | BASE - BAND ASSY - SIDE - LH | PR #55 | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01 | open: drawing |
| 111101 | BASE - BAND TUBE - SIDE - LH | PR #55 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01 | open: drawing |
| 831001 | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS | PR #55 | yes | yes | yes | n/a | no | yes | yes | K-J07 | open: drawing |
| 831002 | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL | PR #55 | yes | yes | yes | no | no | yes | yes | K-J08 | open: DXF or cut list, drawing |
| 110103 | BASE - BAND ASSY - BACK | PR #55 | yes | yes | yes | n/a | no | yes | n/a | K-J13, K-J14, K-F06, K-B01 | open: drawing |
| 111103 | BASE - BAND TUBE - BACK | PR #55 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J04, K-J05, K-F06, K-B01 | open: drawing |
| 111201 | BASE - CORNER BRACKET - BACK - COMMON | PR #55 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02 | open: drawing |
| 111401 | BASE - FLOOR PANEL - F1 | PR #55 | yes | yes | yes | yes | no | yes | n/a | K-B02, K-B03 | open: drawing |
| 111501 | BASE - SEAL MAT - F1 | PR #55 | yes | yes | yes | no | no | yes | n/a | K-B04 | open: DXF or cut list, drawing |

### CEILING

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 410000 | CEILING | PR #32 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 410101 | CEILING - PANEL ASSY - C1 | PR #32 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 410102 | CEILING - PANEL ASSY - C2 | PR #32 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P02 | open: drawing |
| 411101 | CEILING - PANEL FRAME - C1 | PR #32 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16 | open: drawing |
| 411102 | CEILING - PANEL FRAME - C2 | PR #32 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16 | open: drawing |
| 411301 | CEILING - SKIN - COMMON | PR #32 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 510301 | LINING - CASSETTE - CEILING - COMMON | PR #32 | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 513101 | LINING - TRAY - CEILING | PR #32 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 513102 | LINING - RIB - CEILING | PR #32 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 513201 | LINING - FELT - CEILING | PR #32 | yes | yes | yes | yes | no | yes | n/a | K-L04 | open: drawing |
| 513301 | LINING - FILL - CEILING - BAY A | PR #32 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 513302 | LINING - FILL - CEILING - BAY B | PR #32 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |
| 513303 | LINING - FILL - CEILING - BAY C | PR #32 | yes | yes | yes | yes | no | yes | n/a | K-P05 | open: drawing |

### ELECTRICAL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 710000 | ELECTRICAL | PR #64 | yes | no | no | n/a | yes | yes | n/a | K-E01 | open: CAD, STEP |
| 710001 | ELECTRICAL - POWER UNIT - B2 | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 711001 | ELECTRICAL - POWER UNIT - ENCLOSURE BODY | PR #64 | yes | no | no | no | no | yes | yes | K-E01 | open: CAD, STEP, DXF or cut list, drawing |
| 711002 | ELECTRICAL - POWER UNIT - FRONT PLATE | PR #64 | yes | no | no | no | no | yes | yes | K-E01 | open: CAD, STEP, DXF or cut list, drawing |
| 710011 | ELECTRICAL - HARNESS - LIGHT FEED - B2/B4 | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 710021 | ELECTRICAL - HARNESS - TRUNK - B2/R1 | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 710023 | ELECTRICAL - HARNESS - AIR COLUMN | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 710024 | ELECTRICAL - HARNESS - CALL LIGHT - R2 | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 710031 | ELECTRICAL - DRAW WIRE SET | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 710041 | ELECTRICAL - HUB AND CONTROLS ZONE | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |
| 711005 | ELECTRICAL - HUB ZONE COVER PLATE | PR #64 | yes | no | no | no | no | yes | yes | K-E01 | open: CAD, STEP, DXF or cut list, drawing |
| 710051 | ELECTRICAL - CORD SET - 220 V VN - 3 M | PR #64 | yes | no | no | n/a | no | yes | n/a | K-E01 | open: CAD, STEP, drawing |

### FRONT

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 360001 | FRONT - DOOR UNIT | PR #28 | yes | yes | yes | n/a | no | yes | n/a | K-F07, K-F08 | open: drawing |
| 361001 | FRONT - DOOR LEAF - 4+4 LAMINATED | PR #28 | yes | yes | yes | yes | no | yes | n/a | K-F01, K-F02 | open: drawing |
| 361002 | FRONT - DOOR KICK STRIP | PR #28 | yes | yes | yes | yes | no | yes | yes | K-F05, K-F06 | open: drawing |
| 360002 | FRONT - FIXED GLASS UNIT | PR #28 | yes | yes | yes | n/a | no | yes | n/a | K-F03, K-F04 | open: drawing |
| 361003 | FRONT - FIXED GLASS - 4+4 LAMINATED | PR #28 | yes | yes | yes | yes | no | yes | n/a | K-F01, K-F02 | open: drawing |

### WALL

| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 210101 | WALL - PANEL ASSY - SIDE LOWER - LH | PR #41 | yes | yes | yes | n/a | no | yes | n/a | K-J09, K-J10, K-J11, K-J12, K-J13, K-J14, K-J15, K-P01 | open: drawing |
| 211101 | WALL - PANEL FRAME - SIDE LOWER - LH | PR #41 | yes | yes | yes | yes | no | yes | yes | K-J01, K-J02, K-J03, K-J04, K-J05, K-J06, K-J16 | open: drawing |
| 211301 | WALL - SKIN - SIDE LOWER - LH | PR #41 | yes | yes | yes | yes | no | yes | n/a | K-P03, K-P04 | open: drawing |
| 211501 | WALL - CAVITY FILL - SIDE LOWER - LH | PR #41 | yes | yes | yes | no | no | yes | n/a | K-P05 | open: DXF or cut list, drawing |
| 831002 | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL | PR #41 | yes | yes | yes | no | no | yes | yes | K-J08 | open: DXF or cut list, drawing |
| 831001 | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS | PR #41 | yes | yes | yes | n/a | no | yes | yes | K-J07 | open: drawing |
| 510101 | LINING - CASSETTE - SIDE LOWER - LH | PR #41 | yes | yes | yes | n/a | no | yes | n/a | K-L03, K-L05 | open: drawing |
| 511101 | LINING - TRAY - SIDE LOWER - LH | PR #41 | yes | yes | yes | yes | no | yes | yes | K-L01, K-L02 | open: drawing |
| 511301 | LINING - FELT - SIDE LOWER - LH | PR #41 | yes | yes | yes | cut list | cut list (D-89) | yes | n/a | K-L04 | done |

## Bought parts

### BASE

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 118002 | BASE - LEVELLING GLIDE - M10 (HOLD) | PR #55 | H-25 | HOLD | no | HOLD |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | PR #55 | H-03 | yes | J-T1, T06 | done |
| 838006 | HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE (HOLD) | PR #55 | H-26 | HOLD | no | HOLD |
| 118003 | BASE - TUBE END CAP - 100 X 40 - BLACK (HOLD) | PR #55 | H-27 | HOLD | no | HOLD |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #55 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - HEAD WASHER - 6.4 X 18 X 1.6 - ISO 7093-1 A2 | PR #55 | H-09 | yes | T06 | done |
| 118001 | BASE - BASE SEAL - FLOOR EDGE - PEMKO S88BL (HOLD) | PR #55 | H-06 | HOLD | J-T4 | HOLD |

### CEILING

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 518001 | LINING - CASSETTE CLIP | PR #32 | H-10 | HOLD | T07 | HOLD |
| 518002 | LINING - CEILING SAFETY CATCH | PR #32 | H-11 | HOLD | T08 | HOLD |
| 108002 | POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE | PR #32 | H-12 | yes | T09 | done |

### ELECTRICAL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 718001 | ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718002 | ELECTRICAL - LED CONTROLLER - 3 CHANNEL 12 V PWM - RS-485 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718003 | ELECTRICAL - RCBO - 1P+N C10 30 MA TYPE A | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718004 | ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718005 | ELECTRICAL - INLET SEALING CAP | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718006 | ELECTRICAL - LAN FEED-THROUGH - ETHERCON | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718007 | ELECTRICAL - USER SOCKET - UTEN S300 UNIVERSAL | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718008 | ELECTRICAL - LAN SOCKET - UTEN S300 TWO PORT | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718009 | ELECTRICAL - BACK BOX - 86 PLATE | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718010 | ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718011 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718012 | ELECTRICAL - FUSE - ATO 5 A 32 V | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718013 | ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718019 | ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718047 | ELECTRICAL - CLINCH NUT - M4 - FOR 1.0 MM ALUMINIUM | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718014 | ELECTRICAL - EARTH STUD - M5 SELF-CLINCHING | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718015 | ELECTRICAL - BONDING WASHER - SERRATED M6 A2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718016 | ELECTRICAL - RING TERMINAL - INSULATED 1.5-2.5 MM2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718017 | ELECTRICAL - CONDUIT - PVC FLEXIBLE - 20 MM | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #64 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #64 | H-09 | yes | T06 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | PR #64 | H-03 | yes | J-T1, T06 | done |
| 718020 | ELECTRICAL - WIRE - H07V-K 1.5 MM2 (BROWN, BLUE, GREEN-YELLOW) | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718021 | ELECTRICAL - WIRE - H05V-K 1.0 MM2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718022 | ELECTRICAL - WIRE - H07V-K 2.5 MM2 GREEN-YELLOW | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718073 | ELECTRICAL - CURRENT SENSE MODULE - 12 V 0-5 A | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718026 | ELECTRICAL - CABLE - 4 X 20 AWG | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718027 | ELECTRICAL - CABLE - 4 X 24 AWG SCREENED | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718051 | ELECTRICAL - LED STRIP - LOOX5 2165 - 12 V 3.0 W/M - 3000 K | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718052 | ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718044 | ELECTRICAL - DRAW CORD - NYLON 3 MM | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718048 | ELECTRICAL - SCREW - M4 X 12 - ISO 7045 A2 PAN HEAD, BLACK | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718060 | ELECTRICAL - SENSOR HUB - DESK PRO AI (IN-HOUSE) | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718061 | ELECTRICAL - PUSH BUTTON - MOMENTARY - BOOST | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718062 | ELECTRICAL - PUSH BUTTON - MOMENTARY - CALL | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718063 | ELECTRICAL - LIGHT KNOB - POTENTIOMETER WITH KNOB | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718069 | ELECTRICAL - PUSH BUTTON - MOMENTARY - SELF-TEST | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718064 | ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - COLUMN | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718065 | ELECTRICAL - INLET TEMPERATURE SENSOR | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718066 | ELECTRICAL - FUSE - ATO 2 A 32 V | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718067 | ELECTRICAL - FUSE - ATO 1 A 32 V | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718068 | ELECTRICAL - FAN Y-CABLE - 4-PIN PWM | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718070 | ELECTRICAL - CORD CONNECTOR - POWERCON TRUE1 TOP | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718071 | ELECTRICAL - CORD - H05VV-F 3G1.5 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718072 | ELECTRICAL - MAINS PLUG - VN OFFICE SOCKET | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718023 | ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718024 | ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718029 | ELECTRICAL - CABLE - 6 X 18 AWG - CLASS 2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718025 | ELECTRICAL - CABLE - 6 X 24 AWG SCREENED - CLASS 2 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718028 | ELECTRICAL - CABLE - CAT6 U/UTP | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718030 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 2 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718031 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 2 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718045 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718046 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718032 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718033 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718034 | ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718035 | ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718036 | ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718037 | ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718038 | ELECTRICAL - RJ45 PLUG - CAT6 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718039 | ELECTRICAL - RJ45 INLINE COUPLER - CAT6 | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718040 | ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718041 | ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718042 | ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718043 | ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |
| 718050 | ELECTRICAL - LED STRIP - LOOX5 2168 - 12 V 6.0 W/M - 3000 K | PR #64 | n/a (team-numbered) | HOLD | F-06 | HOLD |

### FRONT

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 368001 | FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112 | PR #28 | H-15 | yes | T13 | done |
| 368002 | FRONT - GLAZING U-SEAL - BOHLE BO5201735 | PR #28 | H-16 | yes | F-03 | done |
| 368101 | FRONT - DOOR HINGE - HOLD | PR #28 | H-21 | HOLD | T13 | HOLD |
| 368102 | FRONT - DOOR LOCK - HOLD | PR #28 | H-22 | HOLD | F-02 | HOLD |
| 368103 | FRONT - DOOR PULL PAIR - HOLD | PR #28 | H-24 | HOLD | T13 | HOLD |
| 368004 | FRONT - GLAZING U-PROFILE - BOHLE BO5201571 | PR #28 | H-19 | yes | F-03 | done |
| 368003 | FRONT - GLASS-TO-GLASS SEAL 180 - BOHLE BO5281018 | PR #28 | H-17 | HOLD | T13 | HOLD |

### WALL

| Part | Name | From | Register | Maker and SKU | Test | State |
|---|---|---|---|---|---|---|
| 108002 | POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE | PR #41 | H-12 | yes | T09 | done |
| 838003 | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 | PR #41 | H-03 | yes | J-T1, T06 | done |
| 838001 | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC | PR #41 | H-01 | yes | J-T1, T06 | done |
| 838004 | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 | PR #41 | H-09 | yes | T06 | done |
| 838005 | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE | PR #41 | H-02 | HOLD | J-T2 | HOLD |
| 848001 | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA | PR #41 | H-04 | HOLD | J-T3 | HOLD |
| 518001 | LINING - CASSETTE CLIP | PR #41 | H-10 | HOLD | T07 | HOLD |
| 848011 | SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY | PR #41 | H-13 | no | no | open: maker and SKU, test |
| 848012 | SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN | PR #41 | H-14 | HOLD | F-03 | HOLD |

## Joints-register items no parts list uses yet

| Part | Register | Name |
|---|---|---|
| 838002 | H-01P | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC |
| 848004 | H-04B | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE |
| 108001 | H-07 | POD - HEX KEY - 5 MM BALL END |
| 368006 | H-18 | FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD |
| 368005 | H-20 | FRONT - FRAME-STOP SEAL |
| 368007 | H-23 | FRONT - DOOR CATCH - IN DT |

## How it's built

`python3 v2/00-Control/build_release_checklist.py --open-prs` reads origin/main and every open PR that changes parts, through the master BOM's reader (a later branch adds only the files it changed), the files named `PARTNO_REV_NAME_DOCTYPE.ext` in `v2/01-CAD-Native`, `v2/02-Drawings` and `v2/03-Manufacturing`, the FAI plan (`v2/06-Verification/fai-plan.md`) and the test plans. Without `--open-prs` it reads this working tree.

- A part's CAD and STEP may sit in its assembly's file; its DXF and drawing carry its own number, except as D-89 allows, read as the mechanical check reads them: a drawing whose text says TABULATED covers the other numbers of its family and kind that it lists; a felt or fill piece needs no drawing or DXF when a cut-list or parts-list row gives its number, size, material and tolerance and names no pockets, notches or holes (the mechanical check also counts the holes and faces in its STEP); another soft good cut from sheet or roll (foam, gasket, seal or tape, by the name's last word in its function field) needs no drawing when its DXF gives the outline, or, as a plain strip or rectangle, when such a row also gives its thickness; a flat part cut from sheet needs no drawing when it has its own DXF and its row's process names laser, waterjet or router cutting and no bend, fold, groove, lap, machining, drilling, tapping, welding or bonding, and the row gives material, thickness, finish and an ISO 2768 general tolerance. The checklist can't tell which holes are critical, so a critical-hole note is left to the drawing review. A DXF with any line on the BEND layer (the guideline's CUT, BEND and MARK layers, section 9) keeps the drawing whatever the process says. Assemblies always keep their drawings.
- A DXF is asked of sheet, felt, fill, foam, ply and glass parts; a cut list (or the list's cut rows) of tube parts.
- Finish is asked of metal parts: a `finish` column, or a coating named in the material.
- FAI: the plan's characteristics whose patterns match the number. Bought parts: the plan's section H, or a test that names the number or its register ID.
- A register number's product status comes from the joints register: on HOLD, or named (DECIDED or from a source), or left to the parts list; a team number's from its parts list.
