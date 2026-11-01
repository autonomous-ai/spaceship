# Master BOM check: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BOM-002 | P01 | DRAFT, written by `build_master_bom.py` | 2026-10-31 | Control pack |

Read from: this working tree.

**Result: OK.** 0 failure(s) on the five rules; 237 part lines (75 made, 162 bought, 128 on HOLD) and 34 sub-assembly lines from 13 parts list(s); 35 hardware items in the joints register (35 with a part number). Listed parts weigh 261.5 kg per pod (calculation: quantity x mass each; assemblies with no list count 0, so this is not the pod's weight).

## Files read

- `v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv` @ working tree
- `v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv` @ working tree
- `v2/03-Manufacturing/ceiling/410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv` @ working tree (skipped: a cut list (its rows are cut pieces of the parts in the parts lists))
- `v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv` @ working tree
- `v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv` @ working tree
- `v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv` @ working tree
- `v2/03-Manufacturing/interior/810000_P01_INTERIOR-PARTS-LIST_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210103_P01_WALL-PANEL-ASSY-SIDE-UPPER-LH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210104_P01_WALL-PANEL-ASSY-SIDE-UPPER-RH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210202_P01_WALL-PANEL-ASSY-BACK-LOWER-B2_BOM.csv` @ working tree
- `v2/04-BOM/number-allocation.csv` @ working tree
- `v2/05-Engineering/joints/joints-register.md` @ working tree
- `v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv` @ working tree

## Failures

- none

## Missing or on HOLD, per team

**BASE**
- 118002 BASE - LEVELLING GLIDE - M10 - HOLD: HOLD (HOLD)
- 838006 HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD: HOLD (HOLD)
- 118003 BASE - TUBE END CAP - 100 X 40 - BLACK - HOLD: HOLD (HOLD)
- 118002 BASE - LEVELLING GLIDE - M10 - HOLD: HOLD (HOLD)
- 838006 HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD: HOLD (HOLD)
- 111501 BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM: HOLD (HOLD)
- 118001 BASE - BASE SEAL - FLOOR EDGE - FIXED 4 GAP: HOLD (HOLD)

**WALL**
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 848012 SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN: HOLD (HOLD)
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 848012 SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN: HOLD (HOLD)
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 848012 SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN: HOLD (HOLD)
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838002 HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC: HOLD (HOLD)
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 848004 SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE: HOLD (HOLD)
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 848012 SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN: HOLD (HOLD)

**FRONT**
- 361001 FRONT - DOOR LEAF - 4+4 LAMINATED: HOLD (DRAFT; product HOLD (ISS-074))
- 368001 FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112: HOLD (source (product); bond to aluminium HOLD)
- 368101 FRONT - DOOR HINGE - HOLD: HOLD (HOLD (D-46, ISS-002))
- 368102 FRONT - DOOR STRIKE: HOLD (source (product); on the 8.76 laminate with a 1.2 mm shim: HOLD)
- 368006 FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD: HOLD (HOLD: product for the 8.76 laminate and a 4 mm gap)
- 368103 FRONT - DOOR PULL PAIR - HOLD: HOLD (HOLD)
- 361003 FRONT - FIXED GLASS - 4+4 LAMINATED: HOLD (DRAFT; product HOLD (ISS-074))
- 368003 FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD: HOLD (HOLD: product for the 8.76 laminate and a 4 mm gap)
- no 350000 FRONT - DECOR parts listed yet

**CEILING**
- 518001 LINING - CASSETTE CLIP: HOLD (HOLD)
- 518002 LINING - CEILING SAFETY CATCH: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 838005 HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE: HOLD (HOLD)
- 848004 SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE: HOLD (HOLD)

**CEILING (builds AIR, D-80)**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/air/)

**CEILING (builds INTERIOR, D-80)**
- 818101 INTERIOR - LEDGE BRACKET - HOLD: HOLD (HOLD)
- 811205 INTERIOR - LIGHT SHELF - DIFFUSER RH: HOLD (HOLD)
- 818102 INTERIOR - SCREEN RAIL - HOLD: HOLD (HOLD)

**ELECTRICAL**
- 711001 ELECTRICAL - POWER UNIT - ENCLOSURE BODY: HOLD (DRAFT; HOLD features: the fixing to B2's frame (WALL, IF-12) and the earth stud hole (PEM data))
- 711002 ELECTRICAL - POWER UNIT - FRONT PLATE: HOLD (DRAFT; HOLD features: the two 86-plate openings (UTEN codes, H-ELE-04))
- 718001 ELECTRICAL - 12 V SUPPLY - 60 W CLASS 2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718002 ELECTRICAL - LED CONTROLLER - 3 CHANNEL 12 V PWM - RS-485: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718003 ELECTRICAL - RCBO - 1P+N C10 30 MA TYPE A: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718004 ELECTRICAL - APPLIANCE INLET - POWERCON TRUE1 TOP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718005 ELECTRICAL - INLET SEALING CAP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718006 ELECTRICAL - LAN FEED-THROUGH - ETHERCON: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718007 ELECTRICAL - USER SOCKET - UTEN S300 UNIVERSAL: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718008 ELECTRICAL - LAN SOCKET - UTEN S300 TWO PORT: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718009 ELECTRICAL - BACK BOX - 86 PLATE: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718010 ELECTRICAL - DIN RAIL - TS35 X 7.5 - 100 MM: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718011 ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718012 ELECTRICAL - FUSE - ATO 5 A 32 V: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718013 ELECTRICAL - FUSE - ATO 5 A 32 V - LIGHTS: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718019 ELECTRICAL - SCREW - M4 X 8 - ISO 7045 A2 PAN HEAD: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718049 ELECTRICAL - SPACER - M4 X 2 MM - NYLON, BLACK: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718047 ELECTRICAL - CLINCH NUT - M4 - FOR 1.0 MM ALUMINIUM: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718014 ELECTRICAL - EARTH STUD - M5 SELF-CLINCHING: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718015 ELECTRICAL - BONDING WASHER - SERRATED M6 A2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718016 ELECTRICAL - RING TERMINAL - INSULATED 1.5-2.5 MM2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718017 ELECTRICAL - CONDUIT - PVC FLEXIBLE - 20 MM: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 838001 HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 838004 HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 838003 HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718020 ELECTRICAL - WIRE - H07V-K 1.5 MM2 (BROWN, BLUE, GREEN-YELLOW): HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718021 ELECTRICAL - WIRE - H05V-K 1.0 MM2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718022 ELECTRICAL - WIRE - H07V-K 2.5 MM2 GREEN-YELLOW: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718073 ELECTRICAL - CURRENT SENSE MODULE - 12 V 0-5 A: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718026 ELECTRICAL - CABLE - 4 X 20 AWG: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718027 ELECTRICAL - CABLE - 4 X 24 AWG SCREENED: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718051 ELECTRICAL - LED STRIP - LOOX5 2165 - 12 V 3.0 W/M - 3000 K: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718052 ELECTRICAL - CALL LIGHT PROFILE AND DIFFUSER - 0.9 M: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718044 ELECTRICAL - DRAW CORD - NYLON 3 MM: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718048 ELECTRICAL - SCREW - M4 X 12 - ISO 7045 A2 PAN HEAD, BLACK: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718060 ELECTRICAL - SENSOR HUB - DESK PRO AI (IN-HOUSE): HOLD (HOLD (in-house module: interface data ISS-060))
- 711005 ELECTRICAL - HUB ZONE COVER PLATE: HOLD (DRAFT; HOLD features: the hub window, button and knob holes (ISS-060) and the fixing holes (CEILING's column))
- 718061 ELECTRICAL - PUSH BUTTON - MOMENTARY - BOOST: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718062 ELECTRICAL - PUSH BUTTON - MOMENTARY - CALL: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718063 ELECTRICAL - LIGHT KNOB - POTENTIOMETER WITH KNOB: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718069 ELECTRICAL - PUSH BUTTON - MOMENTARY - SELF-TEST: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718064 ELECTRICAL - FUSE HOLDER - ATO BLADE - INLINE - COLUMN: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718065 ELECTRICAL - INLET TEMPERATURE SENSOR: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718066 ELECTRICAL - FUSE - ATO 2 A 32 V: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718067 ELECTRICAL - FUSE - ATO 1 A 32 V: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718068 ELECTRICAL - FAN Y-CABLE - 4-PIN PWM: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718070 ELECTRICAL - CORD CONNECTOR - POWERCON TRUE1 TOP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718071 ELECTRICAL - CORD - H05VV-F 3G1.5: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718072 ELECTRICAL - MAINS PLUG - VN OFFICE SOCKET: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718023 ELECTRICAL - CABLE - 2 X 18 AWG - CLASS 2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718024 ELECTRICAL - CABLE - 4 X 18 AWG - CLASS 2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718029 ELECTRICAL - CABLE - 6 X 18 AWG - CLASS 2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718025 ELECTRICAL - CABLE - 6 X 24 AWG SCREENED - CLASS 2: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718028 ELECTRICAL - CABLE - CAT6 U/UTP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718030 ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 2 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718031 ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 2 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718045 ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 6 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718046 ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 6 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718032 ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 4 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718033 ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 4 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718034 ELECTRICAL - CONNECTOR - MINI-FIT JR RECEPTACLE 10 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718035 ELECTRICAL - CONNECTOR - MINI-FIT JR PLUG 10 WAY V-0: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718036 ELECTRICAL - TERMINAL - MINI-FIT JR FEMALE 18-24 AWG TIN: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718037 ELECTRICAL - TERMINAL - MINI-FIT JR MALE 18-24 AWG TIN: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718038 ELECTRICAL - RJ45 PLUG - CAT6: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718039 ELECTRICAL - RJ45 INLINE COUPLER - CAT6: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718040 ELECTRICAL - RJ45 KEYSTONE JACK - CAT6 - WITH DUST CAP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718041 ELECTRICAL - BUSHING - SHORTY 19.1 HOLE - NYLON: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718042 ELECTRICAL - EDGE PROTECTION STRIP - 0.5 MM SHEET: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718043 ELECTRICAL - CABLE CLIP - FOR 0.5 MM STEEL TRAY: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718050 ELECTRICAL - LED STRIP - LOOX5 2168 - 12 V 6.0 W/M - 3000 K: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718101 ELECTRICAL - LED PROFILE - LIGHT SHELF - SURFACE 23 X 12.5: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718102 ELECTRICAL - LED PROFILE COVER - SATIN - CLIP-IN: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718103 ELECTRICAL - LED PROFILE END CAP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))
- 718104 ELECTRICAL - LED PROFILE MOUNTING CLIP: HOLD (HOLD (bought part: no order, no supplier contact; guideline 4.3))

**Packing and Assembly**
- no packaging items (family 91) listed yet; v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv names other teams' parts, which their own lists carry

## Numbers given out by the master BOM (D-120)

From `v2/04-BOM/number-allocation.csv`: 64 numbers, 54 not in a team's list yet, 4 in use, 6 cancelled. Each is for one part in its team's list; a team that finds two of them identical in form, fit and function uses the lower number for both and asks for the other to be cancelled. A cancelled number is never reused.

| Number | Name | Part of | Qty per pod | Status |
|---|---|---|---:|---|
| 412101 | CEILING - FRAME SIDE MEMBER - COMMON | 411101 411102 | 2 | ALLOCATED |
| 412102 | CEILING - FRAME SEAM MEMBER - C1 | 411101 | 1 | ALLOCATED |
| 412103 | CEILING - FRAME FRONT MEMBER - C1 | 411101 | 1 | ALLOCATED |
| 412104 | CEILING - FRAME BACK MEMBER 40 X 40 - C1 | 411101 | 1 | ALLOCATED |
| 412105 | CEILING - FRAME CROSS MEMBER 1 - COMMON | 411101 411102 | 2 | ALLOCATED |
| 412001 | CEILING - FRAME CROSS MEMBER - PLAIN - COMMON | 411101 411102 | 4 | ALLOCATED |
| 412201 | CEILING - FRAME SIDE MEMBER - C2 | 411102 | 1 | CANCELLED |
| 412202 | CEILING - FRAME SEAM MEMBER - C2 | 411102 | 1 | ALLOCATED |
| 412203 | CEILING - FRAME FRONT MEMBER - C2 | 411102 | 1 | ALLOCATED |
| 412204 | CEILING - FRAME BACK MEMBER 40 X 40 - C2 | 411102 | 1 | ALLOCATED |
| 412205 | CEILING - FRAME CROSS MEMBER 1 - C2 | 411102 | 1 | CANCELLED |
| 212101 | WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH | 211101 | 1 | ALLOCATED |
| 212102 | WALL - FRAME RAIL TOP - SIDE LOWER - LH | 211101 | 1 | ALLOCATED |
| 212103 | WALL - FRAME STILE FRONT - SIDE LOWER - LH | 211101 | 1 | ALLOCATED |
| 212104 | WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH | 211101 | 1 | ALLOCATED |
| 212105 | WALL - FRAME STILE MID - SIDE LOWER - LH | 211101 | 3 | ALLOCATED |
| 211511 | WALL - CAVITY FILL PIECE F01 344.9 X 1102.7 - SIDE LOWER - COMMON | 210101 210102 | 2 | ALLOCATED |
| 211512 | WALL - CAVITY FILL PIECE F04 334.9 X 1102.7 - SIDE LOWER - COMMON | 210101 210102 | 2 | ALLOCATED |
| 212201 | WALL - FRAME RAIL BOTTOM - SIDE LOWER - RH | 211102 | 1 | ALLOCATED |
| 212202 | WALL - FRAME RAIL TOP - SIDE LOWER - RH | 211102 | 1 | ALLOCATED |
| 212203 | WALL - FRAME STILE FRONT - SIDE LOWER - RH | 211102 | 1 | ALLOCATED |
| 212204 | WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - RH | 211102 | 1 | ALLOCATED |
| 212205 | WALL - FRAME STILE MID - SIDE LOWER - RH | 211102 | 3 | ALLOCATED |
| 211521 | WALL - CAVITY FILL PIECE 1102.7 X 344.9 - SIDE LOWER - RH | 210102 | 3 | CANCELLED |
| 211522 | WALL - CAVITY FILL PIECE 1102.7 X 334.9 - SIDE LOWER - RH | 210102 | 1 | CANCELLED |
| 212301 | WALL - FRAME RAIL BOTTOM - SIDE UPPER - LH | 211103 | 1 | ALLOCATED |
| 212302 | WALL - FRAME RAIL TOP 40 X 40 - SIDE UPPER - LH | 211103 | 1 | ALLOCATED |
| 212303 | WALL - FRAME STILE FRONT - SIDE UPPER - LH | 211103 | 1 | ALLOCATED |
| 212304 | WALL - FRAME STILE BACK 40 X 40 - SIDE UPPER - LH | 211103 | 1 | ALLOCATED |
| 212305 | WALL - FRAME STILE MID - SIDE UPPER - LH | 211103 | 3 | ALLOCATED |
| 211531 | WALL - CAVITY FILL PIECE F05 344.9 X 1082.7 - SIDE UPPER - COMMON | 210103 210104 | 2 | ALLOCATED |
| 211532 | WALL - CAVITY FILL PIECE F08 334.9 X 1082.7 - SIDE UPPER - COMMON | 210103 210104 | 2 | ALLOCATED |
| 212401 | WALL - FRAME RAIL BOTTOM - SIDE UPPER - RH | 211104 | 1 | ALLOCATED |
| 212402 | WALL - FRAME RAIL TOP 40 X 40 - SIDE UPPER - RH | 211104 | 1 | ALLOCATED |
| 212403 | WALL - FRAME STILE FRONT - SIDE UPPER - RH | 211104 | 1 | ALLOCATED |
| 212404 | WALL - FRAME STILE BACK 40 X 40 - SIDE UPPER - RH | 211104 | 1 | ALLOCATED |
| 212405 | WALL - FRAME STILE MID - SIDE UPPER - RH | 211104 | 3 | ALLOCATED |
| 211541 | WALL - CAVITY FILL PIECE 1082.7 X 344.9 - SIDE UPPER - RH | 210104 | 3 | CANCELLED |
| 211542 | WALL - CAVITY FILL PIECE 1082.7 X 334.9 - SIDE UPPER - RH | 210104 | 1 | CANCELLED |
| 212501 | WALL - FRAME RAIL BOTTOM - BACK LOWER - B1 | 211201 | 1 | ALLOCATED |
| 212502 | WALL - FRAME RAIL TOP - BACK LOWER - B1 | 211201 | 1 | ALLOCATED |
| 212503 | WALL - FRAME STILE OUTER - BACK LOWER - B1 | 211201 | 1 | ALLOCATED |
| 212504 | WALL - FRAME STILE CENTRE - BACK LOWER - B1 | 211201 | 1 | ALLOCATED |
| 212505 | WALL - FRAME STILE MID - BACK LOWER - B1 | 211201 | 2 | ALLOCATED |
| 211611 | WALL - CAVITY FILL PIECE F09 373 X 1078.6 - BACK LOWER - COMMON | 210201 210202 | 2 | ALLOCATED |
| 212601 | WALL - FRAME RAIL BOTTOM - BACK LOWER - B2 | 211202 | 1 | ALLOCATED |
| 212602 | WALL - FRAME RAIL TOP - BACK LOWER - B2 | 211202 | 1 | ALLOCATED |
| 212603 | WALL - FRAME STILE OUTER - BACK LOWER - B2 | 211202 | 1 | ALLOCATED |
| 212604 | WALL - FRAME STILE CENTRE - BACK LOWER - B2 | 211202 | 1 | ALLOCATED |
| 212605 | WALL - FRAME STILE MID - BACK LOWER - B2 | 211202 | 2 | ALLOCATED |
| 211621 | WALL - CAVITY FILL PIECE F12 373 X 1078.6 - BACK LOWER - B2 | 210202 | 1 | ALLOCATED |
| 211513 | WALL - CAVITY FILL PIECE F02 344.9 X 1102.7 - SIDE LOWER - COMMON | 210101 210102 | 2 | ALLOCATED |
| 211514 | WALL - CAVITY FILL PIECE F03 344.9 X 1102.7 - SIDE LOWER - COMMON | 210101 210102 | 2 | ALLOCATED |
| 211533 | WALL - CAVITY FILL PIECE F06 344.9 X 1082.7 - SIDE UPPER - COMMON | 210103 210104 | 2 | ALLOCATED |
| 211534 | WALL - CAVITY FILL PIECE F07 344.9 X 1082.7 - SIDE UPPER - COMMON | 210103 210104 | 2 | ALLOCATED |
| 211612 | WALL - CAVITY FILL PIECE F10 373 X 1078.6 - BACK LOWER - COMMON | 210201 210202 | 2 | ALLOCATED |
| 211613 | WALL - CAVITY FILL PIECE F11 373 X 1078.6 - BACK LOWER - B1 | 210201 | 1 | ALLOCATED |
| 211631 | WALL - CAVITY FILL PIECE F13 373 X 1078.6 - BACK UPPER - COMMON | 210203 210204 | 3 | ALLOCATED |
| 211632 | WALL - CAVITY FILL PIECE F14 373 X 1078.6 - BACK UPPER - COMMON | 210203 210204 | 2 | ALLOCATED |
| 211633 | WALL - CAVITY FILL PIECE F15 373 X 1078.6 - BACK UPPER - B3 | 210203 | 1 | ALLOCATED |
| 718101 | ELECTRICAL - LED PROFILE - LIGHT SHELF - SURFACE 23 X 12.5 | 810201 | 1 | in use |
| 718102 | ELECTRICAL - LED PROFILE COVER - SATIN - CLIP-IN | 810201 | 1 | in use |
| 718103 | ELECTRICAL - LED PROFILE END CAP | 810201 | 2 | in use |
| 718104 | ELECTRICAL - LED PROFILE MOUNTING CLIP | 810201 |  | in use |

## Rules

Fails: no part number; one number for two different items; no mass; a hardware item (any bought item except AIR 61, ELECTRICAL 71 and PACKAGING 91) with no joints-register row (D-63); a reserved old number (D-28); an allocated number that is badly formed, outside its band, allocated twice, used for a different item, or used after it was cancelled (D-120).
Listed as missing, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish (D-79, D-67), a made part with no process, a HOLD item, a register item with no part number.
