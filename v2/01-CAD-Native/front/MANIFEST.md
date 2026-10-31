# FRONT: source manifest

Engineering guideline sections 4.4 and 4.5. **DRAFT P01, not for manufacture.** FRONT is assembly 350000 with the decor blocks DL, DT, DR, and 360000 FRONT - DOOR AND GLAZING (`v2/00-Control/assembly-tree.md`). One native Fusion design per sub-assembly, built by script; the script is the source of the geometry, and the .f3d is exported from the saved cloud version.

Every size comes from the skeleton's own parameter list, loaded at build time from `v2/01-CAD-Native/skeleton/100000_Pnn_POD-SKELETON-PARAMETERS.csv` (the highest revision present; P03 for these files). The skeleton's names are kept, so a skeleton change reaches every FRONT part on the next build. FRONT's own parameters follow them in the same design, each with its status and source in its comment.

Coordinates: the pod system (`conventions.md` section 4): origin on the room floor at the pod centre, +X right as seen from outside facing the door, +Y toward the back, +Z up. Every FRONT design is built in place in that system, so its parts drop into the pod with no transform.

Part numbers: FRONT's own bands, `conventions.md` section 6 (DECIDED, D-22, D-28): 35xxxx decor, 36xxxx door and glazing; 8xxx inside a band is a bought catalog item. None is on the reserved list.

## Sub-assemblies

| Sub-assembly | Native design (cloud: Default Project / FocusPod v2) | Script | Status |
|---|---|---|---|
| 360001 FRONT - DOOR UNIT · Cụm cửa kính | `360001_P01_FRONT-DOOR-UNIT_CAD`, exported as `360001_P01_FRONT-DOOR-UNIT_CAD.f3d` | `door_unit.py` | Built, exported, edit test PASS; drawings pending |
| 360002 FRONT - FIXED GLASS UNIT · Cụm vách kính cố định | `360002_P01_FRONT-FIXED-GLASS-UNIT_CAD`, exported as `360002_P01_FRONT-FIXED-GLASS-UNIT_CAD.f3d` | `fixed_glass.py` | Built, exported, edit test PASS; drawings pending |
| DL, DT, DR decor shells | — | — | After the fixed glass |

Shared code: `front_lib.py` (skeleton parameter loader, fully constrained polygons, clash and health checks, exports), `edit_test_front.py` (edit test of any FRONT design from its anchors file).

## 360001 FRONT - DOOR UNIT

| File | What |
|---|---|
| `v2/01-CAD-Native/front/door_unit.py` | Build script: `step=build`, then `step=export` |
| `v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_CAD.f3d` | Native design, exported from cloud version 3 |
| `v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_STEP.step` | STEP AP214 from the same version. Length unit cm, declared in the file (D-13) |
| `v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv` | Parts list for the master BOM, written from the model |
| `v2/03-Manufacturing/front/361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_DXF.dxf` | Leaf outline 1:1 in mm for the glass cutter |
| `v2/03-Manufacturing/front/361002_P01_FRONT-DOOR-KICK-STRIP_DXF.dxf` | Kick strip section 1:1 in mm |
| `v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_ANCHORS.json` | Edit-test anchors: each body side and the expression it must follow |
| `v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT-FRONT_IMG.png`, `...-ISO_IMG.png` | Renders, front from outside and iso, checked by eye |
| `BUILD-RECORD.md`, `EDIT-TEST-RECORD.md` (this folder) | Checks and results |
| `v2/02-Drawings/front/FEATURE-RATIONALE.md` | Why each feature exists |

### Part to sketch, feature and parameter map

Every body is made by the named sketch and feature in its own component. Every sketch is fully constrained (checked by script): each corner is dimensioned from a reference point at -`sk_ref` on both plane axes by its parameter expression plus `sk_ref`, so no dimension can flip side in an edit. No imported or base-feature bodies.

| Part no. | Component · Vietnamese | Body | Sketch (plane) | Feature | Driving parameters |
|---|---|---|---|---|---|
| 360001 | FRONT - DOOR UNIT (root) · Cụm cửa kính | none | none | none | all |
| 361001 | FRONT - DOOR LEAF - 4+4 LAMINATED · Tấm kính cửa 4+4 | DOOR LEAF GLASS 4+4 | OUTLINE - DOOR LEAF (SKELETON TRAPEZOID + 25 MM INTO THE KICK STRIP) (XZ) | EXTRUDE - DOOR LEAF 8.76 | skeleton: pod_w, door_xl, door_xbr, door_xtr, door_zb, door_zt, glass_y, glass_t; own: door_glass_engage |
| 361002 | FRONT - DOOR KICK STRIP · Thanh chân cửa nhôm | KICK STRIP | SECTION - KICK STRIP (H: GLAZING POCKET OVER DROP-SEAL CAVITY) (YZ) | EXTRUDE - KICK STRIP LENGTH | skeleton: thresh_h, door_zb, glass_y, kick_d, pod_w, door_xl, door_xbr; own: kick_floor_gap, kick_zb, kick_h, gu_w, gu_base, kick_pocket_d, kick_wall, kick_web, kick_cav_h, kick_x0, kick_x1 |
| 368002 | FRONT - GLAZING U-SEAL - BOHLE BO5201735 · Gioăng chữ U silicone | GLAZING U-SEAL | SECTION - GLAZING U-SEAL (YZ) | EXTRUDE - GLAZING U-SEAL LENGTH | gu_w, gu_base, glass_t, door_glass_engage, kick_x0, kick_x1 |
| 368001 | FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112 · Ron chân cửa tự động | DROP SEAL ENVELOPE (CATALOGUE SECTION) | SECTION - DROP SEAL GSA 11.6 X 40 (YZ) | EXTRUDE - DROP SEAL CUT LENGTH | gsa_t, gsa_h, gu_w, kick_zb, kick_x0, kick_x1 |
| 368101 (×3) | FRONT - DOOR HINGE - HOLD - H1 BOTTOM, H2 MIDDLE, H3 TOP · Bản lề cửa (chờ chọn) | HOLD HINGE SPACE H1…H3 | PLAN - HOLD HINGE SPACE Hn (XY) | EXTRUDE - Hn | hinge_clamp_h, hinge_clamp_w, hinge_clamp_t, hinge_pocket_d, hinge_x0, hinge_z1, hinge_z2, hinge_z3 |
| 368102 | FRONT - DOOR LOCK - HOLD · Khóa cửa (chờ chọn) | HOLD LOCK SPACE | PLAN - LOCK (XY) | EXTRUDE - LOCK | lock_zc, lock_h, lock_w, lock_t, lock_x1 |
| 368103 | FRONT - DOOR PULL PAIR - HOLD · Tay nắm cửa (chờ chọn) | HOLD PULL SPACE - OUTSIDE, - POD SIDE | PLAN - PULL-OUT, PLAN - PULL-IN (XY) | EXTRUDE - PULL-OUT, EXTRUDE - PULL-IN | pull_cc, pull_len, pull_w, pull_stand, pull_back, pull_zc, pull_x |

The HOLD bodies are reserved spaces, not part geometry (guideline §4.3 step 4): they carry no holes into the glass and use a 1 kg/m³ "envelope" material, so their mass is carried in the parts list instead.

### Parameters

The design holds the 60 skeleton P03 parameters (comment "SKELETON P03 …"), `sk_ref`, and the door unit's own 35. Values below are on skeleton P03.

| Parameter | Value | Status · source |
|---|---|---|
| door_glass_engage | 25 | decided: PM ruling on the FRONT plan, 2026-10-31 |
| kick_floor_gap | 7 | decided: PM ruling on the FRONT plan; athmer GSA rated at a 7 mm floor gap (selection C4) |
| kick_zb = thresh_h + kick_floor_gap | 27 | calculation |
| kick_h = door_zb - kick_zb | 78 | calculation |
| kick_x0, kick_x1, kick_len | -961, 214, 1175 | calculation from the skeleton door corners |
| gu_w | 12 | source: Bohle BO5201571 U-profile inner width (selection C5) |
| gu_base | 2 | assumption: HOLD for Bohle's BO5201735 section |
| kick_pocket_d = door_glass_engage + gu_base | 27 | calculation |
| kick_wall = (kick_d - gu_w) / 2 | 4 | calculation (kick_d 20 is the skeleton's assumption) |
| kick_web | 3 | assumption |
| kick_cav_h = kick_h - kick_pocket_d - kick_web | 48 | calculation; the build fails if it is below gsa_h |
| gsa_t, gsa_h | 11.6, 40 | source: athmer Schall-Ex GSA 1-1112 (selection C4) |
| hinge_clamp_h, hinge_clamp_w, hinge_clamp_t | 120, 100, 40 | assumption, HOLD H01 |
| hinge_pocket_d | 160 | source: the HOLD candidate's 160 mm frame pocket (D-30, D-46) |
| hinge_x0 = -pod_w/2 + dl_w - hinge_pocket_d | -1132 | calculation |
| hinge_z1, hinge_z2, hinge_z3 | 355, 1110.5, 1866 | assumption, HOLD H01 |
| lock_zc = floor_t + 1050 | 1065 | assumption, HOLD H02 |
| lock_h, lock_w | 159, 65 | source: HOLD candidate STUDIO 10.200 body (selection C7), reserved space only |
| lock_t | 40 | assumption |
| lock_x1 | 68.23 | calculation: the latch edge's X at the lock space's top |
| pull_cc | 300 | source: HOLD candidate Häfele 903.10.390 (selection C2) |
| pull_len, pull_w, pull_stand, pull_back | 360, 40, 70, 100 | assumption |
| pull_zc = lock_zc, pull_x | 1065, -45.86 | assumption, calculation |
| sk_ref | 5000 | assumption: sketch reference point offset |

### Editability check (§4.4)

Edit test PASS on a copy (`EDIT-TEST-RECORD.md`): pod_w 2600, fr_dz 12 and door_xbr 1474 at once; all 29 anchors follow, no unhealthy item, no loose sketch, and the copy reverts to the same size.

## 360002 FRONT - FIXED GLASS UNIT

| File | What |
|---|---|
| `v2/01-CAD-Native/front/fixed_glass.py` | Build script: `step=all` builds, saves, exports, takes the pictures and runs the edit test in one Fusion run; `scope=pane` and `scope=uprof` make the part-only designs for the part drawings |
| `v2/01-CAD-Native/front/360002_P01_FRONT-FIXED-GLASS-UNIT_CAD.f3d` | Native design, exported from the saved cloud version |
| `v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_STEP.step` | STEP AP214, length unit cm, declared in the file (D-13) |
| `v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv` | Parts list, written from the model, with the U-profile cut lengths |
| `v2/03-Manufacturing/front/361003_P01_FRONT-FIXED-GLASS-4-4-LAMINATED_DXF.dxf` | Pane outline 1:1 in mm for the glass cutter |
| `v2/01-CAD-Native/front/360002_P01_FRONT-FIXED-GLASS-UNIT_ANCHORS.json` | Edit-test anchors |
| `v2/01-CAD-Native/front/360002_P01_FRONT-FIXED-GLASS-UNIT-FRONT_IMG.png`, `...-ISO_IMG.png` | Renders, checked by eye |

The visible outline is the skeleton's pentagon with two rulings applied (PM, 2026-10-31): the free edge runs parallel to the door's latch edge at the 4 mm the 180° seal needs (`fg_gap`), and on the four held edges the pane runs `fg_bite` (11.5 mm) into hidden U-channels in DR, DT and the base band. The held edges' visible lines are the base band top (`wall_z0`), the skeleton's right and diagonal edge lines (DR's inner edge) and DT's underside (`dt_zb`). Each corner is the crossing of two of those lines pushed out by the same distance, written as parameter expressions (`fg_rnx`… normals and `fg_rc`… line constants), so the corners mitre and follow every skeleton edit.

| Part no. | Component · Vietnamese | Body | Sketch (plane) | Features | Driving parameters |
|---|---|---|---|---|---|
| 360002 | FRONT - FIXED GLASS UNIT (root) · Cụm vách kính cố định | none | none | none | all |
| 361003 | FRONT - FIXED GLASS - 4+4 LAMINATED · Tấm kính cố định 4+4 | FIXED GLASS 4+4 | OUTLINE - FIXED GLASS (SKELETON PENTAGON + BITE ON 4 EDGES) (XZ) | EXTRUDE - FIXED GLASS 8.76 | skeleton: pod_w, fix_xbr, fix_xk, fix_zk, fix_xtr, fix_zb, fix_zt, door_xbr, door_xtr, door_zb, door_zt, wall_z0, dt_zb, glass_y, glass_t; own: fg_gap, fg_bite and the line parameters |
| 368004 | FRONT - GLAZING U-PROFILE - BOHLE BO5201571 · Thanh U nhôm kẹp kính | GLAZING U-PROFILE (4 PIECES, MITRED) | BAND - U-PROFILE OUTER (4 EDGES, MITRED), BAND - U-PROFILE CHANNEL (XZ) | EXTRUDE - U-PROFILE BAR, CUT - U-PROFILE CHANNEL 12 X 13.5 | gu_prof_w, gu_prof_d, gu_prof_t, gu_w, gu_in_d |
| 368002 | FRONT - GLAZING U-SEAL - BOHLE BO5201735 · Gioăng chữ U silicone | GLAZING U-SEAL (4 PIECES) | BAND - U-SEAL OUTER, BAND - U-SEAL GLASS SLOT (XZ) | EXTRUDE - U-SEAL, CUT - U-SEAL GLASS SLOT | gu_w, gu_in_d, fg_bite, glass_t |
| 368003 | FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD · Gioăng từ 180° (nửa 1) | 180 MAGNETIC SEAL - FIXED PANE HALF (HOLD PRODUCT) | OUTLINE - 180 SEAL SPACE ON THE FREE EDGE (XZ), half the 4 mm gap | EXTRUDE - 180 SEAL SPACE | fg_gap and the door edge line |

| Parameter | Value | Status · source |
|---|---|---|
| fg_gap | 4 | decided: PM ruling 2026-10-31; the seal's 4 mm between edges (selection C3) |
| fg_vis_zb = wall_z0 | 110 | calculation: the band top, where DL and DR stop too |
| fg_vis_zt = dt_zb | 2120 | calculation: DT's underside |
| gu_prof_w, gu_prof_d, gu_prof_t | 15, 15, 1.5 | source: Bohle BO5201571 (selection C5) |
| gu_w, gu_in_d | 12, 13.5 | calculation |
| gu_base | 2 | assumption: HOLD for Bohle's BO5201735 section |
| fg_bite = gu_in_d - gu_base | 11.5 | calculation, decided as the hidden depth (PM ruling); HOLD for the glass supplier's minimum cover |

The bottom U-profile piece has 4 screw holes to BASE's sill (`gs_end`, `gs_hole`, `gs_csk`, `gs_xl`, `gs_xr`, `gs_p`: PM ruling 2026-11-01, 50 from each end, 300 or less apart; ISO 10642 M3 × 8 A2). Parts-list names follow the joints register (H-15 to H-24), with maker and SKU.

Edit test PASS on a copy (`EDIT-TEST-RECORD.md`), in the same run as the build, skeleton P04 v4.
