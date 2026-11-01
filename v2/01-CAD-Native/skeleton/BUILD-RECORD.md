# Build record: pod skeleton P04 (100000 POD - SPACESHIP)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the Fusion lock: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py --arg close_previous=1 --arg save=1 --arg export=1 --arg close=1`. **DRAFT P04, the only current revision** (see Revisions at the end). Cloud copy: Default Project / FocusPod v2 / `100000_P04_POD-SKELETON_CAD`.

## Result

- envelopes 34 (25 boxes, 4 base band polygons, 5 faceted front bodies), timeline 147 items, unhealthy 0, loose sketches 0, parameters 65, **all favorites**
- clash pairs 0, expected 0, unexpected 0 (P03's one listed pair, DR into the right band, is gone)
- pod box [-1250.03, -850.03, -0.02, 1250.03, 850.03, 2400.03]
- saved: True; closed after the exports
- export `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON_CAD.f3d`: True
- export `v2/03-Manufacturing/skeleton/100000_P04_POD-SKELETON_STEP.step`: True; length unit cm, declared in the file (D-13); `tools/fusion/step_check.py --expect=-1250,-850,0,1250,850,2400` -> MATCH (largest difference 0.0000 mm); author and organization empty in the header
- export `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv`: True, written by the build from the design's own parameter values (65 rows)
- Edit test: `EDIT-TEST-RECORD.md`, PASS (every envelope and all 25 anchors follow pod_w and pod_h, then revert)

## Versions of P04 (updated in place, the same cloud file)

Parts link to `100000_P04_POD-SKELETON_CAD` through Derive, so value changes no longer rebuild the skeleton (a rebuild makes a new file and would cut every link). `skeleton_update.py` opens the cloud file, adds missing parameters and sets every expression, comment and favorite flag from `PARAMS` in `pod_skeleton.py`, checks the timeline, sketches, every envelope and anchor against its expressions and the clash list, saves a new version, and exports the f3d, the STEP and the CSV from it. A failed check rolls everything back. Linked parts take the new values with `Document.updateAllReferences()`.

| Update (2026-10-31) | What changed | Checks |
|---|---|---|
| 1 | `floor_t` 9 (was 15) and `thresh_h` 13 (was 20), a US-accessible threshold; the kick strip keeps its `kick_gap` above it (Z 20 to 105). F-014: `glass_gap` 4.0, and `fix_xbl`, `fix_xtl` are now expressions that put the fixed glass's free edge parallel to the door's slanted edge, 4.0 mm away (was v1's 2.40 to 4.6). Wall-to-band bolt rule: `base_bolt_edge` 220, `n_base_bolt` 4, `base_spigot_inset` 100, pitches `side_base_pitch` 350.91 and `back_base_pitch` 253.54 | 147 items healthy, no loose sketch, all envelopes and anchors on their expressions, 0 clashes |
| 2 | The outer panel split into `skin_t` 3 + `bond_t` 3 + `frame_t` 40 (still 46). Closing seams B1-B2, B3-B4, C1-C2: `close_gap` 5.5 frame gap, frame width `half_fw` **1198.99**, skin width `half_pw` 1200.61 (skins overhang their frames 1.62 at that seam). The 220 mm rule on every bolted edge: `bolt_edge_inset` 220 and `spigot_inset` 100 (the base names now point at them). Wall to ceiling: bolt line `ceil_bolt_z` **2374** on the ceiling frame's centre; counts per update 3 | the same; 83 parameters, all favorites |

Fusion keeps the first description of each part number: the root and the eight assemb
| 3 | PM rulings and Reviewer 5's notes on #58: **back-panel bolt pitches on the frame** (`back_base_pitch`, `ceil_back_pitch` from `half_fw`: **253.00**; "panel end" means the frame end); wall to ceiling `n_ceil_side_bolt` 4 and `n_ceil_back_bolt` **4**; each bolted edge's start point and pitch from the joints register: `ceil_side_y0` Y −645 measured along the ceiling with `ceil_side_pitch` **351.67**, `ceil_back_x0` ±1201.74 on the frame, `base_side_y0` −642.74, `base_back_x0` ±1201.74. **Floor mat (D-72, from BASE):** `mat_t` 3 under the 9 mm ply: F1-MAT and F2-MAT Z 0 to 3 (new bodies, built in place), the ply F1, F2 Z 3 to 12, `floor_top` 12. What reads the floor: the threshold top stays Z 13 (1 above the floor top), the kick strip Z 20 to 105 (7 over the threshold), inside height 2316 − 12 = 2304. The CSV now has a unit column and writes counts as counts (was ×10). A dry run ends with a planned error so Fusion rolls it back; the edit test anchors the fixed glass's free edge too | as above |
| 4 (2026-11-01) | **D-132 (PM ruling, the owner's question): no floor, no threshold.** `mat_t`, `floor_t` and `thresh_h` 0, so `floor_top` is the room floor, Z 0; the envelopes F1, F1-MAT, F2, F2-MAT and THRESHOLD are dropped (`DROPPED` in `pod_skeleton.py`: `skeleton_update.py` now deletes a dropped envelope's component before it sets the values, so the cloud file stays the same file and every Derive link holds; parameters stay, at 0, and `thresh_d` stays in the file though no longer in the table). The kick strip's envelope now starts `kick_gap` 7 over the room floor. Run by the BASE Engineer (the floor values are BASE's since D-132, the Lead): `skeleton_update.py --doc 100000_P04_POD-SKELETON_CAD --close`, first with `dry_run=1` | Dry run: checks passed, all rolled back. Update: timeline 138 items, unhealthy 0, loose sketches 0; every envelope and anchor on its expressions (worst 0 mm); clash pairs 0; pod box [−1250.03, −850.03, 6.98, 1250.03, 850.03, 2400.03]; saved a new version; STEP `step_check.py --expect=-1250,-850,7,1250,850,2400` → MATCH (31 solids, cm declared, D-13); CSV 88 parameters. Edit test on the copy: PASS, 22 envelopes and 26 anchors follow |
| 5 (2026-11-01) | **The kick strip on the band's bottom line (PM ruling on D-132).** The KICK envelope runs from `glide_h` (10, the band's bottom line at the nominal glide setting) to `door_zb` 105, so the door's drop seal works near its rated gap with travel left for uneven floors, as FRONT's model has it; `kick_gap` stays in the table but no longer sets the kick strip. Run by the BASE Engineer: `skeleton_update.py --doc 100000_P04_POD-SKELETON_CAD --close`, first with `dry_run=1` | Dry run: checks passed, all rolled back. Update: the KICK envelope's bottom plane and height changed in place; timeline 138 items, unhealthy 0, loose sketches 0; clash pairs 0; saved a new version over version 5; STEP `step_check.py --expect=-1250,-850,10,1250,850,2400` → MATCH (31 solids, cm declared, D-13); CSV 88 parameters; no account names in the f3d, STEP or CSV. Edit test on the copy: PASS, 22 envelopes and 26 anchors follow |

## Pass D (PM rulings, DECIDED 2026-10-31)

| # | Ruling | In the model |
|---|---|---|
| 1 | DR's bottom moves up to the base band top (Z 110), like DL | `CUT - DR BOTTOM AT THE BASE BAND TOP` removes DR below `wall_z0`; its inner edge keeps the fixed glass line. Anchor: DR zmin = `wall_z0` |
| 2 | The floor runs out to the band, closing the 41 mm trench | F1, F2 now span X ±(`pod_w / 2 - band_t`) = ±1210 and Y −645 to `pod_d / 2 - band_t` = 810: **1210 x 1455 x 15** (was 1169 x 1414). The front edge stays at the walls' start (Y −645) |
| 3 | The front base band follows v1's faceted outline | BAND-FL under DL follows DL's two plan facets and ends at DL's door-side face (X −972); BAND-FR runs v1's straight front from the fixed glass's left edge (X 218) and turns along DR's corner facet. Both are `band_t` (40) thick, their inner faces true offsets of the outline (parameter expressions, no hand numbers). The side bands now start at the facets (Y −670 left, −672 right), mitred to the front pieces. Across the door opening there is no band: the threshold and the kick strip carry the dark line (D-18, D-40) and the step stays 20 mm |
| 4 | Close the 38 mm slot at the back top edge: the back outer frames run up to the ceiling frame; the back linings float 4 mm under it, the same rule as the side walls (PM, F-004) | `back_oh` = `pod_h - outer_t - seam_gap - panel_z0` (2239.48): B3, B4 end one seam under the ceiling frame (Z 2351.74 under 2354). Two equal rows, `back_ph` = 1118.61. The lower back linings match the lower row; the upper ones float 4 mm under the ceiling frame (Z 2350), as the side linings do, closing the inside corner at the back top |
| 5 | One `seam_gap`, **2.26 mm** (the Joints Engineer's metal stop: 1.5 stop washer + 0.76 rivnut head), at all nine site seam types (F-001, F-005) | Walls on the band (walls stand at `panel_z0` = Z 112.26), row to row in each wall, back panels at X 0, side frames to back and ceiling panels, back wall to ceiling, ceiling halves, side walls to the decor (side panels start at Y −642.74: **1492.74** long). `half_pw` = (`pod_w - 2 * outer_t - 3 * seam_gap`) / 2 = **1200.61** (back and ceiling panels, was 1207); `side_h` = (`wall_h - 2 * seam_gap`) / 2 = **1142.74** (was 1145). Linings keep pass C's corner and X 0 joints; their rows follow the frame rows |
| 6 | The outer panel is **46 mm** (ACP 3 + bond line 3 + frame 40) for the walls and the ceiling; re-derive the rest from it | `outer_t` 46; `stack_t` = `outer_t + cav_gap + cass_t` = **84** (was the fixed 81). The inside is 3 mm smaller per wall and in height: 2332 between the side linings, ceiling cassette face at Z 2316, inside height 2301 over the 15 mm floor |

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

Heights (DECIDED on PR #16): v1's front runs from Z 115 to 2417 in the v2 frame; the skeleton lowers it by `fr_dz` = 17 mm so its top meets the 2400 datum (D-21). DL and now DR stand on the base band top (Z 110). The door bottom lands at Z 105; the kick strip is 85 tall (Z 20 to 105) above the 7 mm running gap over the 13 mm threshold.

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

| Code | Assembly | Size X x Y x Z | Z from to | Layout study id |
|---|---|---|---|---|
| L1 | WALL | 46 x 1492.74 x 1142.74 | 112.26 to 1255 | W-SIDE-LO |
| L1-CASS | LINING | 34 x 1445 x 1142.74 | 112.26 to 1255 | L-CASS-SIDE-LO |
| L2 | WALL | 46 x 1492.74 x 1142.74 | 1257.26 to 2400 | W-SIDE-UP |
| L2-CASS | LINING | 34 x 1445 x 1092.74 | 1257.26 to 2350 | L-CASS-SIDE-UP |
| R1 | WALL | 46 x 1492.74 x 1142.74 | 112.26 to 1255 | W-SIDE-LO |
| R1-CASS | LINING | 34 x 1445 x 1142.74 | 112.26 to 1255 | L-CASS-SIDE-LO |
| R2 | WALL | 46 x 1492.74 x 1142.74 | 1257.26 to 2400 | W-SIDE-UP |
| R2-CASS | LINING | 34 x 1445 x 1092.74 | 1257.26 to 2350 | L-CASS-SIDE-UP |
| B1 | WALL | 1200.61 x 46 x 1118.61 | 112.26 to 1230.87 | W-BACK-LO |
| B1-CASS | LINING | 1166 x 34 x 1118.61 | 112.26 to 1230.87 | L-CASS-BACK-LO |
| B2 | WALL | 1200.61 x 46 x 1118.61 | 112.26 to 1230.87 | W-BACK-LO |
| B2-CASS | LINING | 1166 x 34 x 1118.61 | 112.26 to 1230.87 | L-CASS-BACK-LO |
| B3 | WALL | 1200.61 x 46 x 1118.61 | 1233.13 to 2351.74 | W-BACK-UP |
| B3-CASS | LINING | 1166 x 34 x 1116.87 | 1233.13 to 2350 | L-CASS-BACK-UP |
| B4 | WALL | 1200.61 x 46 x 1118.61 | 1233.13 to 2351.74 | W-BACK-UP |
| B4-CASS | LINING | 1166 x 34 x 1116.87 | 1233.13 to 2350 | L-CASS-BACK-UP |
| C1 | CEILING | 1200.61 x 1495 x 46 | 2354 to 2400 | C-HALF |
| C1-CASS | LINING | 1166 x 1411 x 34 | 2316 to 2350 | L-CASS-HALF |
| C2 | CEILING | 1200.61 x 1495 x 46 | 2354 to 2400 | C-HALF |
| C2-CASS | LINING | 1166 x 1411 x 34 | 2316 to 2350 | L-CASS-HALF |
| KICK | GLAZING | 1175 x 20 x 95 | 10 (`glide_h`) to 105 | D-40; its bottom on the band's bottom line (PM ruling on D-132) |

## Decided values that hold

| Value | In the skeleton | Source |
|---|---|---|
| 84 mm wall and ceiling stack | outer 46 + gap 4 + cassette 34 = 84 | D-16, D-42; outer 46 PM ruling (pass D) |
| Wall depth 1495 | 1492.74 of side panel (Y −642.74 to 850) plus the 2.26 seam at the decor | D-49 (v1 1496); joints register 2.8 |
| Decor depth 205 | front face Y -850, back face Y -645 | D-49 |
| Height datum 2400 | roof skin top Z 2400 | D-21 |
| Inside height about 2316 | ceiling cassette face Z 2316 - the room floor Z 0 (no floor, D-132; was 2304 over the 12 mm floor) | D-42; outer 46 (P04 updates); D-132 |
| No floor | People stand on the room floor; no floor, mat or threshold (`floor_top` Z 0); the door's drop seal closes on the room floor (P04 update 4) | D-132 (PM ruling 2026-11-01) |
| Door glass 4+4 laminate 8.76 | DOOR, v1's measured trapezoid | D-46 |

## Not modelled yet

Glides, corner keys, hardware and kits; the base seal lip (BASE's design, D-132). AIR, ELECTRICAL and INTERIOR are empty assembly components until their groups place parts. `v2/00-Control/document-register.csv` still names P03 for the skeleton rows (Control Engineer's file).

## Renders (checked by eye)

`100000_P04_POD-SKELETON-FRONT-ISO_IMG.png` (front, right, above), `...-BACK-ISO_IMG.png` (back, left, above), `...-TOP_IMG.png` (plan), `...-BASE-FRONT_IMG.png` (the front base band, the door's threshold and kick strip, DR on the band), `...-BACK-TOP_IMG.png` (the back top edge: back frames up to the ceiling, 2.26 mm seams). Made with `skeleton_view.py` (camera presets named by pod direction). The look is v1's, as measured.

## Revisions

| Rev | What | Where |
|---|---|---|
| P01 | Stage A: envelopes, box placeholders for the front | PR #15 (c8d094c), removed from the tree |
| P02 | Stage B: the measured faceted front, decor depth 205 | PR #16 (6780e61), removed from the tree |
| P03 | Pass C: wall depth 1495, v1's top joint, floating side linings, closed lining corner | PR #17 (7a5f437), removed from the tree |
| P04 | Pass D: DR on the band, floor out to the band, faceted front band, back frames up to the ceiling, one 2.26 mm seam gap at nine seams, outer panel 46 (stack 84), kick strip gap 7, parameters as favorites | this record |
