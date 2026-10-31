# Master BOM check: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BOM-002 | P01 | DRAFT, written by `build_master_bom.py` | 2026-10-31 | Control pack |

Read from: this working tree.

**Result: OK.** 0 failure(s) on the five rules; 0 part lines (0 made, 0 bought, 0 on HOLD) and 0 sub-assembly lines from 0 parts list(s); 16 hardware items in the joints register (16 with a part number). Listed parts weigh 0.0 kg per pod (calculation: quantity x mass each; assemblies with no list count 0, so this is not the pod's weight).

## Files read

- `v2/05-Engineering/joints/joints-register.md` @ working tree

## Failures

- none

## Missing or on HOLD, per team

**BASE**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/base/)

**WALL**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/wall/)

**FRONT**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/front/)

**CEILING**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/ceiling/)

**CEILING (builds AIR, D-80)**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/air/)

**CEILING (builds INTERIOR, D-80)**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/interior/)

**ELECTRICAL**
- no parts list yet (expected *_BOM.csv files in v2/03-Manufacturing/electrical/)

**Packing and Assembly**
- no parts list yet (expected *_BOM.csv files in v2/07-Packaging/)

## Rules

Fails: no part number; one number for two different items; no mass; a hardware item (any bought item except AIR 61, ELECTRICAL 71 and PACKAGING 91) with no joints-register row (D-63); a reserved old number (D-28).
Listed as missing, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish (D-79, D-67), a made part with no process, a HOLD item, a register item with no part number.
