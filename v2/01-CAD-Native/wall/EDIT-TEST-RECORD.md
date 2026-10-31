# Edit test record: WALL designs

Guideline section 4.4. `edit_test_wall.py` (run by `post_wall_doc.py`) opens each exported .f3d as a new, unsaved copy, changes two skeleton values and one wall rule (wall_depth 1495 -> 1300, side_h -> 1000, stile_pitch_max 400 -> 300), checks that every part follows and every feature stays healthy, then reverts and checks that every body is back to its exact box. The copy is closed without saving.

## Edit test: 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101, 211301, 211501.

1. Reopen: timeline 109 items, 0 not healthy; sketches 33, 33 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 109 items, 1 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 / RAIL - BOTTOM | (-1244.0, -642.74, 112.26, -1204.0, 847.0, 132.26) | (-1244.0, -447.74, 112.26, -1204.0, 847.0, 132.26) |
| 211101 / RAIL - TOP | (-1244.0, -642.74, 1235.0, -1204.0, 847.0, 1255.0) | (-1244.0, -447.74, 1092.26, -1204.0, 847.0, 1112.26) |
| 211101 / STILE - BACK | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1235.0) | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1092.26) |
| 211101 / STILE - FRONT | (-1244.0, -642.74, 132.26, -1204.0, -622.74, 1235.0) | (-1244.0, -447.74, 132.26, -1204.0, -427.74, 1092.26) |
| 211101 / STILE - MID 1 | (-1244.0, -277.81, 132.26, -1204.0, -257.81, 1235.0) | (-1244.0, -194.79, 132.26, -1204.0, -174.79, 1092.26) |
| 211101 / STILE - MID 1 (1) | - | (-1244.0, 564.05, 132.26, -1204.0, 584.05, 1092.26) |
| 211101 / STILE - MID 2 | (-1244.0, 87.13, 132.26, -1204.0, 107.13, 1235.0) | (-1244.0, 58.16, 132.26, -1204.0, 78.16, 1092.26) |
| 211101 / STILE - MID 3 | (-1244.0, 452.06, 132.26, -1204.0, 472.06, 1235.0) | (-1244.0, 311.1, 132.26, -1204.0, 331.1, 1092.26) |
| 211301 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 112.26, -1204.0, 850.0, 1255.0) | (-1250.0, -447.74, 112.26, -1204.0, 850.0, 1112.26) |
| 211501 / FILL - BAY 1 | (-1244.0, -622.74, 132.26, -1204.0, -277.81, 1235.0) | (-1244.0, -427.74, 132.26, -1204.0, -194.79, 1092.26) |
| 211501 / FILL - BAY 1 (1) | - | (-1244.0, 331.1, 132.26, -1204.0, 564.05, 1092.26) |
| 211501 / FILL - BAY 2 | (-1244.0, -257.81, 132.26, -1204.0, 87.13, 1235.0) | (-1244.0, -174.79, 132.26, -1204.0, 58.16, 1092.26) |
| 211501 / FILL - BAY 3 | (-1244.0, 107.13, 132.26, -1204.0, 452.06, 1235.0) | (-1244.0, 78.16, 132.26, -1204.0, 311.1, 1092.26) |
| 211501 / FILL - BAY 4 | (-1244.0, 472.06, 132.26, -1204.0, 807.0, 1235.0) | (-1244.0, 584.05, 132.26, -1204.0, 807.0, 1092.26) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span side_h - 40 | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| fill bays = mid stile count + 1 (5) | PASS |
| skin runs wall_depth - 2.26 and side_h | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 109 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101.

1. Reopen: timeline 73 items, 0 not healthy; sketches 22, 22 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 73 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 / RAIL - BOTTOM | (-1244.0, -642.74, 112.26, -1204.0, 847.0, 132.26) | (-1244.0, -447.74, 112.26, -1204.0, 847.0, 132.26) |
| 211101 / RAIL - TOP | (-1244.0, -642.74, 1235.0, -1204.0, 847.0, 1255.0) | (-1244.0, -447.74, 1092.26, -1204.0, 847.0, 1112.26) |
| 211101 / STILE - BACK | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1235.0) | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1092.26) |
| 211101 / STILE - FRONT | (-1244.0, -642.74, 132.26, -1204.0, -622.74, 1235.0) | (-1244.0, -447.74, 132.26, -1204.0, -427.74, 1092.26) |
| 211101 / STILE - MID 1 | (-1244.0, -277.81, 132.26, -1204.0, -257.81, 1235.0) | (-1244.0, -194.79, 132.26, -1204.0, -174.79, 1092.26) |
| 211101 / STILE - MID 1 (1) | - | (-1244.0, 564.05, 132.26, -1204.0, 584.05, 1092.26) |
| 211101 / STILE - MID 2 | (-1244.0, 87.13, 132.26, -1204.0, 107.13, 1235.0) | (-1244.0, 58.16, 132.26, -1204.0, 78.16, 1092.26) |
| 211101 / STILE - MID 3 | (-1244.0, 452.06, 132.26, -1204.0, 472.06, 1235.0) | (-1244.0, 311.1, 132.26, -1204.0, 331.1, 1092.26) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span side_h - 40 | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 73 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511101, 511301, NO-PN-HOLD-H03.

1. Reopen: timeline 24 items, 0 not healthy; sketches 6, 6 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 24 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511101 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1200.0, -645.0, 112.26, -1166.0, 800.0, 1255.0) | (-1200.0, -450.0, 112.26, -1166.0, 800.0, 1112.26) |
| 511301 / FELT - PET 9 HELD BY THE TRAY LIPS | (-1175.5, -643.5, 113.76, -1166.5, 798.5, 1253.5) | (-1175.5, -448.5, 113.76, -1166.5, 798.5, 1110.76) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (-1204.0, -277.81, 182.26, -1200.0, -257.81, 242.26) | (-1204.0, -194.79, 182.26, -1200.0, -174.79, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (-1204.0, 452.06, 182.26, -1200.0, 472.06, 242.26) | (-1204.0, 564.05, 182.26, -1200.0, 584.05, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP FRONT) | (-1204.0, -277.81, 1125.0, -1200.0, -257.81, 1185.0) | (-1204.0, -194.79, 982.26, -1200.0, -174.79, 1042.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP BACK) | (-1204.0, 452.06, 1125.0, -1200.0, 472.06, 1185.0) | (-1204.0, 564.05, 982.26, -1200.0, 584.05, 1042.26) |

| Check | Result |
|---|---|
| tray runs cass_len | FAIL |
| tray starts at the decor back plate | FAIL |
| tray height follows side_h | FAIL |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 24 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

