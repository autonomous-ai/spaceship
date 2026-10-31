# Build record: pod skeleton P02 (stage B: the measured faceted front)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py --arg close_previous=1 --arg save=1 --arg export=1` (stage B is the default; `--arg stage=A` rebuilds P01). **DRAFT P02.**

## Result

- envelopes 32, timeline 139 items, unhealthy 0, loose sketches 0, parameters 58
- clash pairs 17, expected 17, unexpected 0
- pod box [-1250.03, -850.03, -0.02, 1250.03, 850.03, 2400.03]
- saved: True
- export v2/01-CAD-Native/skeleton/100000_P02_POD-SKELETON_CAD.f3d: True
- export v2/03-Manufacturing/skeleton/100000_P02_POD-SKELETON_STEP.step: True
- STEP `v2/03-Manufacturing/skeleton/100000_P02_POD-SKELETON_STEP.step`: length unit cm, declared in the file (D-13); `tools/fusion/step_check.py --expect=-1250,-850,0,1250,850,2400` -> MATCH; no names in the header
- Edit test: see `EDIT-TEST-RECORD.md` (envelopes and faceted anchors)

## The faceted front (stage B)

Measured from the v1 STEP (`V1-FRONT-FACETS.md`); nothing from v1 is pasted in. Every corner is a named parameter (status source, with its v1 value in the comment), every sketch fully constrained:

| Body | How it is built | Measured from |
|---|---|---|
| DL left block | plan outline with v1's two front facets, extruded Z 110 to 2400, top cut by the 45 degree slope it shares with DT | v1 body 42 |
| DT top block | plan outline with v1's lower facet (it recedes from Y -850 at X 230 to Y -767 at X -969), extruded from Z 2120, bottom cut by the same slope over DL, top front cut by the chamfer | v1 body 127 |
| DR right block | front outline at Y -850 whose inner edge follows the fixed glass, extruded 235 back, outer corner facet cut in plan, top front chamfer | v1 bodies 76 and 126 |
| DOOR | true trapezoid 1175 at the bottom, 893 at the top, right edge slanted; 4+4 laminate 8.76 (D-46) | v1 body 221 |
| FIXED | true pentagon, left edge parallel to the door's right edge, right edge with v1's knee at Z 1521 | v1 body 222 |

Heights: v1's front runs from Z 115 to 2417 in the v2 frame. Stage B lowers it by `fr_dz` = 17 mm so its top meets the 2400 datum (D-21); the block bottoms stop at the base band top (Z 110), so DL and DR are 12 mm shorter than v1 at the bottom, where the base band hides the joint. The door bottom lands at Z 105: the kick strip is 85 tall (D-40 says about 90). Status: calculation.

Depth: the blocks run from the front face Y -850 back to Y -615 (235, D-39); v1's shells end at Y -645, and the 30 mm beyond is the decided overlap with the walls (conventions section 4).

## Check by eye against v1

`100000_P02_POD-SKELETON-FRONT-VS-V1_IMG.png`: left, the build plan's front elevation of v1; middle, this skeleton's front view; right, its front iso. The top band slopes down to the knee, the right block's inner edge runs from the knee to the bottom right, the door's right edge is slanted, and the corner facets and the top chamfer are in place. Still to add: the decor's top grille slots (D-29), the hinge pocket (D-30) and the ACP returns; they are details inside these envelopes.

## Envelopes (unchanged from P01 except the door kick strip and threshold, which follow the measured door)

| Code | Assembly | Size X x Y x Z | Layout study id |
|---|---|---|---|
| L1 | WALL | 43 x 1500 x 1145 | W-SIDE-LO |
| L1-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-LO |
| L2 | WALL | 43 x 1500 x 1145 | W-SIDE-UP |
| L2-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-UP |
| R1 | WALL | 43 x 1500 x 1145 | W-SIDE-LO |
| R1-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-LO |
| R2 | WALL | 43 x 1500 x 1145 | W-SIDE-UP |
| R2-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-UP |
| B1 | WALL | 1169 x 43 x 1104.5 | W-BACK-LO |
| B1-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO |
| B2 | WALL | 1169 x 43 x 1104.5 | W-BACK-LO |
| B2-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO |
| B3 | WALL | 1169 x 43 x 1104.5 | W-BACK-UP |
| B3-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP |
| B4 | WALL | 1169 x 43 x 1104.5 | W-BACK-UP |
| B4-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP |
| C1 | CEILING | 1169 x 1500 x 43 | C-HALF |
| C1-CASS | LINING | 1169 x 1419 x 34 | L-CASS-HALF |
| F1 | BASE | 1169 x 1419 x 15 | B-FLOOR |
| C2 | CEILING | 1169 x 1500 x 43 | C-HALF |
| C2-CASS | LINING | 1169 x 1419 x 34 | L-CASS-HALF |
| F2 | BASE | 1169 x 1419 x 15 | B-FLOOR |
| BAND-BACK | BASE | 2420 x 40 x 100 | B-BAND-BACK |
| BAND-L | BASE | 40 x 1660 x 100 | B-BAND-SIDE |
| BAND-R | BASE | 40 x 1660 x 100 | B-BAND-SIDE |
| THRESHOLD | BASE | 1175 x 60 x 20 | B-THRESH |
| KICK | GLAZING | 1175 x 20 x 85 | D-40 |

The P01 record (`BUILD-RECORD.md`) has the size check against the layout study and the explained differences; they still hold.

## Clash check

Same rule as P01: any overlap over 1 mm3 not on the script's list fails the run. P02 adds two listed pairs: DT over L2 and L2-CASS (DT wraps the left wall's upper front edge, as in v1).
