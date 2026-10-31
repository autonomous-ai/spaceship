# Master BOM check: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BOM-002 | P01 | DRAFT, written by `build_master_bom.py` | 2026-10-31 | Control pack |

Read from: this working tree.

**Result: OK.** 0 failure(s) on the five rules; 93 part lines (40 made, 53 bought, 33 on HOLD) and 14 sub-assembly lines from 8 parts list(s); 35 hardware items in the joints register (35 with a part number). Listed parts weigh 178.7 kg per pod (calculation: quantity x mass each; assemblies with no list count 0, so this is not the pod's weight).

## Files read

- `v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv` @ working tree
- `v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv` @ working tree
- `v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210103_P01_WALL-PANEL-ASSY-SIDE-UPPER-LH_BOM.csv` @ working tree
- `v2/03-Manufacturing/wall/210104_P01_WALL-PANEL-ASSY-SIDE-UPPER-RH_BOM.csv` @ working tree
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
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/ceiling/)

**CEILING (builds AIR, D-80)**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/air/)

**CEILING (builds INTERIOR, D-80)**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/interior/)

**ELECTRICAL**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/electrical/)

**Packing and Assembly**
- no packaging items (family 91) listed yet; v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv names other teams' parts, which their own lists carry

## Rules

Fails: no part number; one number for two different items; no mass; a hardware item (any bought item except AIR 61, ELECTRICAL 71 and PACKAGING 91) with no joints-register row (D-63); a reserved old number (D-28).
Listed as missing, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish (D-79, D-67), a made part with no process, a HOLD item, a register item with no part number.
