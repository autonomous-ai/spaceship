# Build record: pod skeleton P03 (100000 POD - SPACESHIP)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py --arg close_previous=1 --arg save=1 --arg export=1`. **DRAFT P03, the only current revision** (see Revisions at the end). Cloud copy: Default Project / FocusPod v2 / `100000_P03_POD-SKELETON_CAD`.

## Result

- envelopes 32, timeline 141 items, unhealthy 0, loose sketches 0, parameters 60
- clash pairs 1, expected 1, unexpected 0
- pod box [-1250.03, -850.03, -0.02, 1250.03, 850.03, 2400.03]
- saved: True
- export v2/01-CAD-Native/skeleton/100000_P03_POD-SKELETON_CAD.f3d: True
- export v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step: True
- STEP `v2/03-Manufacturing/skeleton/100000_P03_POD-SKELETON_STEP.step`: length unit cm, declared in the file (D-13); `tools/fusion/step_check.py --expect=-1250,-850,0,1250,850,2400` -> MATCH; no names in the header
- Edit test: `EDIT-TEST-RECORD.md` (every envelope and faceted anchor follows pod_w and pod_h)

## Pass C (PM rulings, DECIDED 2026-10-31)

| # | Ruling | In the model |
|---|---|---|
| 1 | Wall depth 1495, so the side walls start at the decor back plate and keep v1's side seam | `wall_depth` 1495 (was 1500). Side panels, side linings and floors start at Y -645, the decor's back face (v1's side wall is 1496, Y -646 to 850). Walls and decor now meet face to face; P02's 5 mm overlap is gone |
| 2 | The top block's joint line matches v1 (to X 449 along the top chamfer), unless the v1 drawings show otherwise | DT's plan ends on v1's line: X 230 on the front face, diagonal to X 449 at the chamfer's back edge (Y -672), then straight to the back face (`dt_xr` 1699, source: v1 body 127). DR is cut on the same line (`CUT - DR TO DT JOINT`), so the blocks meet face to face. v1's top-frame drawing (`sources/v1/drawings/decor-frame-assembly.pdf`, page 10) shows the same diagonal end: 216 mm between its front and back corners on the 16 mm frame, 219 on the skin here. Close-up: `...-TOP-JOINT_IMG.png` |
| 3 | A gap between the roof frame and the side lining tops, so the linings stay floating | Upper side linings stop 4 mm under the roof frame: top Z 2353, 1098 tall (was 2357 and 1102). `lin_gap` 4, assumption: the same 4 mm as the wall stack gap |
| 4 | Close the 34 x 34 inside lining corner | Side linings run 34 mm past the back linings' face to Y 803, so they close the corner: 1448 long (was 1419). Back linings unchanged (1169 per half), butting the side linings' face |
| 5 | Keep only the current files | P01 and P02 files (CAD, STEP, renders, parameter registers, records) are removed; this record replaces both records. Both stay in git history (c8d094c, 6780e61) and as cloud copies, not current |

## The faceted front

Measured from the v1 STEP (`V1-FRONT-FACETS.md`); nothing from v1 is pasted in. Every corner is a named parameter (status source), every sketch fully constrained.

| Body | How it is built | Measured from |
|---|---|---|
| DL left block | plan outline with v1's two front facets, extruded Z 110 to 2400, top cut by the 45 degree slope it shares with DT | v1 body 42 |
| DT top block | plan outline with v1's lower facet and v1's joint to DR (to X 449), extruded from Z 2120, bottom cut by the slope over DL, top front cut by the chamfer | v1 body 127 |
| DR right block | front outline at Y -850 whose inner edge follows the fixed glass, extruded 205 back, outer corner facet cut in plan, joint to DT cut in plan, top front chamfer | v1 bodies 76 and 126 |
| DOOR | true trapezoid 1175 at the bottom, 893 at the top, right edge slanted; 4+4 laminate 8.76 (D-46) | v1 body 221 |
| FIXED | true pentagon, left edge parallel to the door's right edge, right edge with v1's knee at Z 1521 | v1 body 222 |

Heights (DECIDED on PR #16): v1's front runs from Z 115 to 2417 in the v2 frame; the skeleton lowers it by `fr_dz` = 17 mm so its top meets the 2400 datum (D-21). DL stops at the base band top (Z 110), 12 mm shorter than v1; DR's bottom follows the fixed glass bottom (Z 102). The door bottom lands at Z 105, so the kick strip is 85 tall.

Depth (DECIDED on PR #16, ruling 3): D-39 means "as v1", and where the v1 drawings and the STEP disagree the drawings win. v1's decor-frame drawing has core frames 191 deep (left) and 197 (right); with the ACP skin and back plate they give the v1 STEP's shell, front face Y -850, back face Y -645: **205 mm** (`decor_d`). The 230-235 in D-39 and the layout study's B1 list came from the v1 BOM and don't match v1's geometry; the Control Engineer corrects D-39, the Layout Engineer the B1 list.

## Differences from the layout study, explained

- **Back panels B1-B4 and ceiling halves C1, C2: 1207 wide, list 1169.** DECIDED on PR #15: back wall and ceiling frames span frame to frame, between the side frames (X +-1207), with the side skins covering their edges (build plan rule 4). Their linings stay 1169.
- **Upper side linings L2-CASS, R2-CASS: 1098 tall, list 1145.** They stop under the ceiling frame (PR #15) with a 4 mm gap (pass C), so they float and the roof frame never sits on them.
- **Side linings: 1448 long.** They close the inside corner with the back linings (pass C).
- **Ceiling cassettes C1-CASS, C2-CASS: 34 mm, list 74 mm.** The list's 74 includes the 40 mm ceiling fill (D-24), which sits inside the outer panel's 40 mm frame cavity, so the cassette envelope is tray, gap and felt only (34). Status: calculation.
- **Back panels: 1104.5 mm, list 1104.** The list rounds back_h / 2 = 2209 / 2.
- **Not modelled yet:** base band front pieces, glides, corner keys, hardware and kits. AIR, ELECTRICAL and INTERIOR are empty assembly components until their groups place parts.

## Decided values that hold

| Value | In the skeleton | Source |
|---|---|---|
| 81 mm wall and ceiling stack | outer 43 + gap 4 + cassette 34 = 81 | D-16, D-42 |
| Wall depth 1495 | side walls Y -645 to 850 | PM ruling, pass C (v1 1496) |
| Decor depth 205 | front face Y -850, back face Y -645 | PM ruling 3 on PR #16 (v1 drawings and STEP) |
| Height datum 2400 | roof skin top Z 2400 | D-21 |
| Inside height about 2301 | ceiling cassette face Z 2319 - floor top Z 15 = 2304; about 2301 with a 3 mm underlay (not modelled) | D-42 |
| Thin floor | F1, F2 15 mm on the room floor; threshold 20 | D-05, D-18 |
| Door glass 4+4 laminate 8.76 | DOOR, v1's measured trapezoid | D-46 |

## Envelopes

Faceted bodies (DL, DT, DR, DOOR, FIXED) are described above.

| Code | Assembly | Size X x Y x Z | Layout study id |
|---|---|---|---|
| L1 | WALL | 43 x 1495 x 1145 | W-SIDE-LO |
| L1-CASS | LINING | 34 x 1448 x 1145 | L-CASS-SIDE-LO |
| L2 | WALL | 43 x 1495 x 1145 | W-SIDE-UP |
| L2-CASS | LINING | 34 x 1448 x 1098 | L-CASS-SIDE-UP |
| R1 | WALL | 43 x 1495 x 1145 | W-SIDE-LO |
| R1-CASS | LINING | 34 x 1448 x 1145 | L-CASS-SIDE-LO |
| R2 | WALL | 43 x 1495 x 1145 | W-SIDE-UP |
| R2-CASS | LINING | 34 x 1448 x 1098 | L-CASS-SIDE-UP |
| B1 | WALL | 1207 x 43 x 1104.5 | W-BACK-LO |
| B1-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO |
| B2 | WALL | 1207 x 43 x 1104.5 | W-BACK-LO |
| B2-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-LO |
| B3 | WALL | 1207 x 43 x 1104.5 | W-BACK-UP |
| B3-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP |
| B4 | WALL | 1207 x 43 x 1104.5 | W-BACK-UP |
| B4-CASS | LINING | 1169 x 34 x 1104.5 | L-CASS-BACK-UP |
| C1 | CEILING | 1207 x 1495 x 43 | C-HALF |
| C1-CASS | LINING | 1169 x 1414 x 34 | L-CASS-HALF |
| F1 | BASE | 1169 x 1414 x 15 | B-FLOOR |
| C2 | CEILING | 1207 x 1495 x 43 | C-HALF |
| C2-CASS | LINING | 1169 x 1414 x 34 | L-CASS-HALF |
| F2 | BASE | 1169 x 1414 x 15 | B-FLOOR |
| BAND-BACK | BASE | 2420 x 40 x 100 | B-BAND-BACK |
| BAND-L | BASE | 40 x 1660 x 100 | B-BAND-SIDE |
| BAND-R | BASE | 40 x 1660 x 100 | B-BAND-SIDE |
| THRESHOLD | BASE | 1175 x 60 x 20 | B-THRESH |
| KICK | GLAZING | 1175 x 20 x 85 | D-40 |

## Clash check

Any overlap over 1 mm3 that is not on the script's list fails the run. With pass C the walls and the top block meet the decor face to face, so 20 of P02's 21 listed pairs no longer overlap and came off the list. Overlaps found:

- BAND-R x DR: 14394 mm3 (listed)

The one listed pair: DR's bottom follows the fixed glass bottom (Z 102), 8 mm into the right base band's front end (Z 10 to 110). HOLD for the base design: the band gets a notch or stops short.

## Renders (checked by eye)

`100000_P03_POD-SKELETON-FRONT-ISO_IMG.png` (front, right, above), `...-BACK-ISO_IMG.png` (back, left, above), `...-TOP_IMG.png` (plan), `...-TOP-JOINT_IMG.png` (close-up of the DT to DR joint along the chamfer). The look is v1's, as measured.

## Revisions

| Rev | What | Where |
|---|---|---|
| P01 | Stage A: envelopes, box placeholders for the front | PR #15 (c8d094c), removed from the tree |
| P02 | Stage B: the measured faceted front, decor depth 205 | PR #16 (6780e61), removed from the tree |
| P03 | Pass C: wall depth 1495, v1's top joint, floating side linings, closed lining corner | this record |

The superseded stage A code path (box placeholders) was removed from the script with P01.
