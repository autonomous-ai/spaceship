# Build record: pod skeleton, stage A (100000 POD - SPACESHIP)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py --arg close_previous=1 --arg save=1 --arg export=1`. **DRAFT P01.** The front decor blocks are PLACEHOLDER boxes (stage A); the faceted front is stage B, the next PR. Nothing here is the look of the front.

## Result

- envelopes 31, timeline 130 items, unhealthy 0, loose sketches 0, parameters 30
- clash pairs 17, expected 17, unexpected 0
- pod box [-1250.03, -850.03, -0.02, 1250.03, 850.03, 2400.03]
- saved: True
- export v2/01-CAD-Native/skeleton/100000_P01_POD-SKELETON_CAD.f3d: True
- export v2/03-Manufacturing/skeleton/100000_P01_POD-SKELETON_STEP.step: True
- Edit test: PASS (`EDIT-TEST-RECORD.md`)
- STEP `v2/03-Manufacturing/skeleton/100000_P01_POD-SKELETON_STEP.step`: length unit cm, declared in the file (D-13); `tools/fusion/step_check.py --expect=-1250,-850,0,1250,850,2400` -> MATCH, 31 solids; no names in the header

## Components and envelopes

Coordinates: conventions.md section 4 (origin on the room floor at the pod centre, +X right seen from outside facing the door, +Y back, +Z up). Sizes are the envelope's X x Y x Z in mm. Each envelope is a fully constrained rectangle on an XY plane offset by a parameter, extruded by a parameter, in its own component under its assembly.

| Code | Assembly | Size X x Y x Z | Layout study id / source | Check against the B1 final list |
|---|---|---|---|---|
| L1 | WALL | 43 x 1500 x 1145 | W-SIDE-LO | OK (within 1 mm) |
| L1-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-LO | OK (within 1 mm) |
| L2 | WALL | 43 x 1500 x 1145 | W-SIDE-UP | OK (within 1 mm) |
| L2-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-UP | OK (within 1 mm) |
| R1 | WALL | 43 x 1500 x 1145 | W-SIDE-LO | OK (within 1 mm) |
| R1-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-LO | OK (within 1 mm) |
| R2 | WALL | 43 x 1500 x 1145 | W-SIDE-UP | OK (within 1 mm) |
| R2-CASS | LINING | 34 x 1419 x 1145 | L-CASS-SIDE-UP | OK (within 1 mm) |
| B1 | WALL | 1169 x 43 x 1104.5 | W-BACK-LO | OK (within 1 mm) |
| B1-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO | OK (within 1 mm) |
| B2 | WALL | 1169 x 43 x 1104.5 | W-BACK-LO | OK (within 1 mm) |
| B2-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO | OK (within 1 mm) |
| B3 | WALL | 1169 x 43 x 1104.5 | W-BACK-UP | OK (within 1 mm) |
| B3-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP | OK (within 1 mm) |
| B4 | WALL | 1169 x 43 x 1104.5 | W-BACK-UP | OK (within 1 mm) |
| B4-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP | OK (within 1 mm) |
| C1 | CEILING | 1169 x 1500 x 43 | C-HALF | OK (within 1 mm) |
| C1-CASS | LINING | 1169 x 1419 x 34 | L-CASS-HALF | 1419 x 1169 x 74     DIFF 40.0 |
| F1 | BASE | 1169 x 1419 x 15 | B-FLOOR | OK (within 1 mm) |
| C2 | CEILING | 1169 x 1500 x 43 | C-HALF | OK (within 1 mm) |
| C2-CASS | LINING | 1169 x 1419 x 34 | L-CASS-HALF | 1419 x 1169 x 74     DIFF 40.0 |
| F2 | BASE | 1169 x 1419 x 15 | B-FLOOR | OK (within 1 mm) |
| BAND-BACK | BASE | 2420 x 40 x 100 | B-BAND-BACK | OK (within 1 mm) |
| BAND-L | BASE | 40 x 1660 x 100 | B-BAND-SIDE | OK (within 1 mm) |
| BAND-R | BASE | 40 x 1660 x 100 | B-BAND-SIDE | OK (within 1 mm) |
| THRESHOLD | BASE | 1176 x 60 x 20 | B-THRESH | OK (within 1 mm) |
| DL | FRONT | 278 x 235 x 2290 | F-DL | OK (within 1 mm) |
| DR | FRONT | 1016 x 235 x 2290 | F-DR | OK (within 1 mm) |
| DT | FRONT | 1697 x 235 x 280 | F-DT | OK (within 1 mm) |
| DOOR | GLAZING | 1176 x 8.76 x 2011 | F-GLASS-DOOR | OK (within 1 mm) |
| KICK | GLAZING | 1176 x 20 x 89 | D-40 | not in the list: D-40 |

## Differences from the layout study, explained

- **Ceiling cassettes C1-CASS, C2-CASS: 34 mm, list 74 mm.** The list's 74 includes the 40 mm ceiling fill that rides on the cassette (D-24). In the assembled ceiling that fill sits inside the outer panel's 40 mm frame cavity, so the cassette envelope is the tray, gap and felt only (34). Status: calculation.
- **Back panels: 1104.5 mm, list 1104.** The list rounds back_h / 2 = 2209 / 2. Within 1 mm.
- **KICK (door kick strip): 89 mm tall.** D-40 says about 90; 89 makes the door meet DT exactly (door_z0 = 2400 - 280 - 2011 = 109, threshold 20). Depth 20 is an assumption.
- **Not modelled in stage A:** base band front pieces (the list's 300 and 1050 don't add up with the 1176 door opening, and they sit under the faceted front: stage B), the fixed glass (its true outline is faceted: stage B; the list gives 2139 x 724, v1's box is 2017 x 1014), glides, corner keys, hardware and kits. AIR, ELECTRICAL and INTERIOR are empty assembly components; their parts go in when designed.

## Decided values that hold

| Value | In the skeleton | Source |
|---|---|---|
| 81 mm wall and ceiling stack | outer 43 + gap 4 + cassette 34 = 81 | D-16, D-42 |
| Decor depth 230-235 | 235 (decor front Y = -850, back face Y = -615, 35 mm over the wall front edge) | D-39 |
| Height datum 2400 | roof skin top Z = 2400 | D-21 |
| Inside height about 2301 | ceiling cassette face Z 2319 - floor top Z 15 = 2304; about 2301 with a 3 mm underlay (not modelled) | D-42 |
| Thin floor (DECIDED) | F1, F2 15 mm on the room floor; threshold 20 | D-05, D-18 |
| Door 1176 wide, 4+4 laminate 8.76 | DOOR 1176 x 8.76 x 2011 | D-46 |

## Clash check

Every pair of envelopes is intersected; any overlap over 1 mm3 that is not listed below fails the run. This run: 17 overlaps, all listed, 0 unexpected.

| Pair | Why it is allowed |
|---|---|
| DL x L1 | decor wraps the side wall front edge by 35 mm (D-39, conventions s4) |
| DL x L2 | same |
| DL x L1-CASS | same |
| DL x L2-CASS | same |
| DR x R1 | same |
| DR x R2 | same |
| DR x R1-CASS | same |
| DR x R2-CASS | same |
| DT x DR | boxes of faceted blocks overlap; the facets don't (stage B) |
| DT x C1 | DT covers the ceiling front edge (v1); boxes only (stage B) |
| DT x C2 | same |
| DT x C1-CASS | same |
| DT x C2-CASS | same |
| DL x BAND-L | decor stands on the base band corner; boxes only (stage B) |
| DR x BAND-R | same |
| DL x C1 | box corner reaches the ceiling front edge (stage B) |
| DR x C2 | same |
| DL x C1-CASS | same |
| DR x C2-CASS | same |

## Renders (checked by eye)

`100000_P01_POD-SKELETON-FRONT-ISO_IMG.png` (from the front, right and above), `...-BACK-ISO_IMG.png` (from the back, left and above), `...-TOP_IMG.png` (looking down, front at the bottom). They show the overall form, 2 sheets per side wall and 4 on the back with aligned seams (D-23), and the ceiling halves split at X = 0. **The front in these renders is placeholder boxes, not the look.** Small open corners at the top back edges are envelope gaps (the 4 mm stack gap), not design.

