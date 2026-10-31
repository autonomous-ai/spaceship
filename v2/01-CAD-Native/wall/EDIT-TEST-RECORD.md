# Edit test record: WALL sample (L1 panel and its cassette)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the locked runner (PR #22):

```sh
python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/edit_test_wall.py --arg f3d=v2/01-CAD-Native/wall/<file>.f3d
```

Guideline section 4.4: each copy is opened from the exported .f3d, two skeleton parameters and one wall rule are changed, every body is measured, then the values are reverted and every body must return to its exact box. Result: PASS on both files.

## Edit test: 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101, 211301, 211501.

1. Reopen: timeline 44 items, 0 not healthy; sketches 13, 13 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 44 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1145 | 1000 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1492 | 1297 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 368 | 255.4 |
| cass_len | 1448 | 1253 |
| cass_h | 1145 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 / RAIL - BOTTOM | (-1247.0, -645.0, 110.0, -1207.0, 847.0, 130.0) | (-1247.0, -450.0, 110.0, -1207.0, 847.0, 130.0) |
| 211101 / RAIL - TOP | (-1247.0, -645.0, 1235.0, -1207.0, 847.0, 1255.0) | (-1247.0, -450.0, 1090.0, -1207.0, 847.0, 1110.0) |
| 211101 / STILE - BACK | (-1247.0, 827.0, 130.0, -1207.0, 847.0, 1235.0) | (-1247.0, 827.0, 130.0, -1207.0, 847.0, 1090.0) |
| 211101 / STILE - FRONT | (-1247.0, -645.0, 130.0, -1207.0, -625.0, 1235.0) | (-1247.0, -450.0, 130.0, -1207.0, -430.0, 1090.0) |
| 211101 / STILE - MID 1 | (-1247.0, -277.0, 130.0, -1207.0, -257.0, 1235.0) | (-1247.0, -194.6, 130.0, -1207.0, -174.6, 1090.0) |
| 211101 / STILE - MID 1 (1) | - | (-1247.0, 571.6, 130.0, -1207.0, 591.6, 1090.0) |
| 211101 / STILE - MID 2 | (-1247.0, 91.0, 130.0, -1207.0, 111.0, 1235.0) | (-1247.0, 60.8, 130.0, -1207.0, 80.8, 1090.0) |
| 211101 / STILE - MID 3 | (-1247.0, 459.0, 130.0, -1207.0, 479.0, 1235.0) | (-1247.0, 316.2, 130.0, -1207.0, 336.2, 1090.0) |
| 211301 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -645.0, 112.0, -1207.0, 850.0, 1253.0) | (-1250.0, -450.0, 112.0, -1207.0, 850.0, 1108.0) |
| 211501 / FILL - BAY 1 | (-1247.0, -625.0, 130.0, -1207.0, -277.0, 1235.0) | (-1247.0, -430.0, 130.0, -1207.0, -194.6, 1090.0) |
| 211501 / FILL - BAY 1 (1) | - | (-1247.0, 591.6, 130.0, -1207.0, 827.0, 1090.0) |
| 211501 / FILL - BAY 2 | (-1247.0, -257.0, 130.0, -1207.0, 91.0, 1235.0) | (-1247.0, -174.6, 130.0, -1207.0, 60.8, 1090.0) |
| 211501 / FILL - BAY 3 | (-1247.0, 111.0, 130.0, -1207.0, 459.0, 1235.0) | (-1247.0, 80.8, 130.0, -1207.0, 316.2, 1090.0) |
| 211501 / FILL - BAY 4 | (-1247.0, 479.0, 130.0, -1207.0, 827.0, 1235.0) | (-1247.0, 336.2, 130.0, -1207.0, 571.6, 1090.0) |

| Check | Result |
|---|---|
| rails run wall_depth - 3 | PASS |
| frame starts at the decor back plate (Y = 850 - wall_depth) | PASS |
| stiles span side_h - 40 | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| fill bays = mid stiles + 1 | PASS |
| no stile pitch over 300 | PASS |
| skin runs wall_depth and side_h - reveal | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 44 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511101, 511301, NO-PN-HOLD-H03.

1. Reopen: timeline 24 items, 0 not healthy; sketches 7, 7 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 24 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1145 | 1000 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1492 | 1297 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 368 | 255.4 |
| cass_len | 1448 | 1253 |
| cass_h | 1145 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511101 / TRAY - STEEL 0.5 WITH 25 RETURNS | (-1203.0, -645.0, 110.0, -1178.0, 803.0, 1255.0) | (-1203.0, -450.0, 110.0, -1178.0, 803.0, 1110.0) |
| 511301 / FELT - PET 9 ACROSS THE TRAY FACE | (-1178.0, -645.0, 110.0, -1169.0, 803.0, 1255.0) | (-1178.0, -450.0, 110.0, -1169.0, 803.0, 1110.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (-1207.0, -277.0, 180.0, -1203.0, -257.0, 240.0) | (-1207.0, -194.6, 180.0, -1203.0, -174.6, 240.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (-1207.0, 459.0, 180.0, -1203.0, 479.0, 240.0) | (-1207.0, 571.6, 180.0, -1203.0, 591.6, 240.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP FRONT) | (-1207.0, -277.0, 1125.0, -1203.0, -257.0, 1185.0) | (-1207.0, -194.6, 980.0, -1203.0, -174.6, 1040.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP BACK) | (-1207.0, 459.0, 1125.0, -1203.0, 479.0, 1185.0) | (-1207.0, 571.6, 980.0, -1203.0, 591.6, 1040.0) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray and felt height follow side_h | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 24 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

