# Build record: pod skeleton P04 (100000 POD - SPACESHIP)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the Fusion lock: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py --arg close_previous=1 --arg save=1 --arg export=1 --arg close=1`. **DRAFT P04, the only current revision** (see Revisions at the end). Cloud copy: Default Project / FocusPod v2 / `100000_P04_POD-SKELETON_CAD`.

## Result

- envelopes 34 (25 boxes, 4 base band polygons, 5 faceted front bodies), timeline 147 items, unhealthy 0, loose sketches 0, parameters 63, **all favorites**
- clash pairs 0, expected 0, unexpected 0 (P03's one listed pair, DR into the right band, is gone)
- pod box [-1250.03, -850.03, -0.02, 1250.03, 850.03, 2400.03]
- saved: True; closed after the exports
- export `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON_CAD.f3d`: True
- export `v2/03-Manufacturing/skeleton/100000_P04_POD-SKELETON_STEP.step`: True; length unit cm, declared in the file (D-13); `tools/fusion/step_check.py --expect=-1250,-850,0,1250,850,2400` -> MATCH (largest difference 0.0000 mm, 34 solids); author and organization empty in the header
- export `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv`: True, written by the build from the design's own parameter values (63 rows)
- Edit test: `EDIT-TEST-RECORD.md`, PASS (every envelope and all 25 anchors follow pod_w and pod_h, then revert)

## Pass D (PM rulings, DECIDED 2026-10-31)

| # | Ruling | In the model |
|---|---|---|
| 1 | DR's bottom moves up to the base band top (Z 110), like DL | `CUT - DR BOTTOM AT THE BASE BAND TOP` removes DR below `wall_z0`; its inner edge keeps the fixed glass line. Anchor: DR zmin = `wall_z0` |
| 2 | The floor runs out to the band, closing the 41 mm trench | F1, F2 now span X ±(`pod_w / 2 - band_t`) = ±1210 and Y −645 to `pod_d / 2 - band_t` = 810: **1210 x 1455 x 15** (was 1169 x 1414). The front edge stays at the walls' start (Y −645) |
| 3 | The front base band follows v1's faceted outline | BAND-FL under DL follows DL's two plan facets and ends at DL's door-side face (X −972); BAND-FR runs v1's straight front from the fixed glass's left edge (X 218) and turns along DR's corner facet. Both are `band_t` (40) thick, their inner faces true offsets of the outline (parameter expressions, no hand numbers). The side bands now start at the facets (Y −670 left, −672 right), mitred to the front pieces. Across the door opening there is no band: the threshold and the kick strip carry the dark line (D-18, D-40) and the step stays 20 mm |
| 4 | Close the 38 mm slot at the back top edge: the back outer frames run up to the ceiling frame, the back linings stop under the ceiling cassette (Z 2319), the same rule as the side walls | `back_oh` = `pod_h - outer_t - seam_gap - wall_z0` (2245): B3, B4 now end at Z 2355, one seam under the ceiling frame (2357). Two equal rows, `back_ph` = 1121.5. The lower back linings match the lower row (as on the side walls); the upper ones end at Z 2319 (1085.5 tall) |
| 5 | Mechanical Checker F-001: one `seam_gap`, 2 mm (an assumption until the Joints Engineer's gasket table and the wall sample confirm it), on every frame-to-frame seam | IF-03 to IF-06: side frame to back and ceiling panels, panel to panel at X 0, row to row in each wall, back wall to ceiling. `half_pw` = (`pod_w - 2 * outer_t - 3 * seam_gap`) / 2 = **1204** (back and ceiling panels, was 1207); `side_h` = (`wall_h - seam_gap`) / 2 = **1144** (was 1145). Linings keep pass C's corner and X 0 joints; their rows follow the frame rows |

Also from the Mechanical Checker on P03: **F-002** the kick strip starts `kick_gap` (7 mm, the FRONT door unit's running gap for the drop seal) above the threshold, Z 27 to 105; **F-003** the unused `door_z0` (109, disagreeing with `door_zb` 105) is removed.

## Linking a part to the skeleton

Every user parameter is a **favorite**, so a part design can derive them from the cloud file `100000_P04_POD-SKELETON_CAD` with Fusion's Derive (`DeriveFeatures.createInput(skeletonDesign)`, `isIncludeFavoriteParameters = True`). They arrive as `<name>_Ref` (for example `wall_depth_Ref`) and can be used in the part's own expressions. Tested on 2026-10-31 with throwaway designs: after the source saved a new value, `Document.updateAllReferences()` brought it in and the part's expressions followed (300 -> 400 mm). How-to: `tools/fusion/README.md`, "Linking a part to the skeleton".

## The faceted front

Measured from the v1 STEP (`V1-FRONT-FACETS.md`); nothing from v1 is pasted in. Every corner is a named parameter (status source), every sketch fully constrained.

| Body | How it is built | Measured from |
|---|---|---|
| DL left block | plan outline with v1's two front facets, extruded Z 110 to 2400, top cut by the 45 degree slope it shares with DT | v1 body 42 |
| DT top block | plan outline with v1's lower facet and v1's joint to DR (to X 449), extruded from Z 2120, bottom cut by the slope over DL, top front cut by the chamfer | v1 body 127 |
| DR right block | front outline at Y -850 whose inner edge follows the fixed glass, extruded 205 back, outer corner facet cut in plan, joint to DT cut in plan, top front chamfer, **bottom cut at the band top (pass D)** | v1 bodies 76 and 126 |
| DOOR | true trapezoid 1175 at the bottom, 893 at the top, right edge slanted; 4+4 laminate 8.76 (D-46) | v1 body 221 |
| FIXED | true pentagon, left edge parallel to the door's right edge, right edge with v1's knee at Z 1521 | v1 body 222 |

Heights (DECIDED on PR #16): v1's front runs from Z 115 to 2417 in the v2 frame; the skeleton lowers it by `fr_dz` = 17 mm so its top meets the 2400 datum (D-21). DL and now DR stand on the base band top (Z 110). The door bottom lands at Z 105; the kick strip is 78 tall above the 7 mm running gap.

Depth (DECIDED on PR #16, ruling 3; D-49): the decor blocks are **205 mm** deep (`decor_d`), front face Y -850, back face Y -645.

## Base band (pass D)

| Code | Plan outline (mm, pod system) | Size X x Y x Z | Layout study id |
|---|---|---|---|
| BAND-L | (−1250, −670) (−1250, 850) (−1210, 850) (−1210, −652.1) | 40 x 1520 x 100 | B-BAND-SIDE |
| BAND-FL | (−1250, −670) (−1158, −752) (−979, −844) (−972, −844) (−972, −802.6) (−1135.2, −718.8) (−1210, −652.1) | 278 x 191.9 x 100 | B-BAND-FRONT |
| BAND-FR | (218, −850) (1052, −850) (1250, −672) (1210, −654.2) (1036.7, −810) (218, −810) | 1032 x 195.8 x 100 | B-BAND-FRONT |
| BAND-R | (1250, −672) (1250, 850) (1210, 850) (1210, −654.2) | 40 x 1522 x 100 | B-BAND-SIDE |
| BAND-BACK | box | 2420 x 40 x 100 | B-BAND-BACK |

The inner points are computed by Fusion from parameter expressions (offset lines of the facets by `band_t`), so they follow any change to the facet parameters or `band_t`. DL's 7 mm front edge is shorter than the band is thick, so BAND-FL ends on facet 2's inner line at DL's door-side face. Joints between the pieces are the BASE design's (HOLD for the corner keys).

## Envelopes

| Code | Assembly | Size X x Y x Z | Layout study id |
|---|---|---|---|
| L1, R1 | WALL | 43 x 1495 x 1144 (Z 110 to 1254) | W-SIDE-LO |
| L2, R2 | WALL | 43 x 1495 x 1144 (Z 1256 to 2400) | W-SIDE-UP |
| L1-CASS, R1-CASS | LINING | 34 x 1448 x 1144 | L-CASS-SIDE-LO |
| L2-CASS, R2-CASS | LINING | 34 x 1448 x 1097 (to Z 2353) | L-CASS-SIDE-UP |
| B1, B2 | WALL | 1204 x 43 x 1121.5 (Z 110 to 1231.5) | W-BACK-LO |
| B3, B4 | WALL | 1204 x 43 x 1121.5 (Z 1233.5 to 2355) | W-BACK-UP |
| B1-CASS, B2-CASS | LINING | 1169 x 34 x 1121.5 | L-CASS-BACK-LO |
| B3-CASS, B4-CASS | LINING | 1169 x 34 x 1085.5 (to Z 2319) | L-CASS-BACK-UP |
| C1, C2 | CEILING | 1204 x 1495 x 43 (X ±1 to ±1205) | C-HALF |
| C1-CASS, C2-CASS | LINING | 1169 x 1414 x 34 | L-CASS-HALF |
| F1, F2 | BASE | 1210 x 1455 x 15 | B-FLOOR |
| THRESHOLD | BASE | 1175 x 60 x 20 | B-THRESH |
| KICK | GLAZING | 1175 x 20 x 78 (Z 27 to 105) | D-40 |

## Decided values that hold

| Value | In the skeleton | Source |
|---|---|---|
| 81 mm wall and ceiling stack | outer 43 + gap 4 + cassette 34 = 81 | D-16, D-42 |
| Wall depth 1495 | side walls Y -645 to 850 | D-49 (v1 1496) |
| Decor depth 205 | front face Y -850, back face Y -645 | D-49 |
| Height datum 2400 | roof skin top Z 2400 | D-21 |
| Inside height about 2301 | ceiling cassette face Z 2319 - floor top Z 15 = 2304; about 2301 with a 3 mm underlay (not modelled) | D-42 |
| Thin floor | F1, F2 15 mm on the room floor, out to the band (pass D); threshold 20 | D-05, D-18 |
| Door glass 4+4 laminate 8.76 | DOOR, v1's measured trapezoid | D-46 |

## Not modelled yet

Glides, corner keys, hardware and kits; the floor's front edge between the threshold and Y −645 (24 mm) and behind the fixed glass (49 mm) is left for the BASE design. AIR, ELECTRICAL and INTERIOR are empty assembly components until their groups place parts. `v2/00-Control/document-register.csv` still names P03 for the skeleton rows (Control Engineer's file).

## Renders (checked by eye)

`100000_P04_POD-SKELETON-FRONT-ISO_IMG.png` (front, right, above), `...-BACK-ISO_IMG.png` (back, left, above), `...-TOP_IMG.png` (plan), `...-BASE-FRONT_IMG.png` (the front base band, the door's threshold and kick strip, DR on the band), `...-BACK-TOP_IMG.png` (the back top edge: back frames up to the ceiling, 2 mm seams). Made with `skeleton_view.py` (camera presets named by pod direction). The look is v1's, as measured.

## Revisions

| Rev | What | Where |
|---|---|---|
| P01 | Stage A: envelopes, box placeholders for the front | PR #15 (c8d094c), removed from the tree |
| P02 | Stage B: the measured faceted front, decor depth 205 | PR #16 (6780e61), removed from the tree |
| P03 | Pass C: wall depth 1495, v1's top joint, floating side linings, closed lining corner | PR #17 (7a5f437), removed from the tree |
| P04 | Pass D: DR on the band, floor out to the band, faceted front band, back frames up to the ceiling, one 2 mm seam gap, kick strip gap 7, parameters as favorites | this record |
