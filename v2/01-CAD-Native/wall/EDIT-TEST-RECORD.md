# Edit test record: WALL designs

Guideline section 4.4. `edit_test_wall.py` (run by `post_wall_doc.py`) opens each exported .f3d as a new, unsaved copy, changes two skeleton values and one wall rule (wall_depth 1495 -> 1300, side_h -> 1000, stile_pitch_max 400 -> 300), checks that every part follows and every feature stays healthy, then reverts and checks that every body is back to its exact box. The copy is closed without saving.

## Edit test: 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101, 211301, 211501, 831001, 831002, 838003.

1. Reopen: timeline 164 items, 0 not healthy; sketches 47, 47 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm: rebuild 164 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 3 |
| stile_pitch | 364.935 | 316.185 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 / RAIL - BOTTOM | (-1244.0, -642.74, 112.26, -1204.0, 847.0, 132.26) | (-1244.0, -447.74, 112.26, -1204.0, 847.0, 132.26) |
| 211101 / RAIL - TOP | (-1244.0, -642.74, 1235.0, -1204.0, 847.0, 1255.0) | (-1244.0, -447.74, 1092.26, -1204.0, 847.0, 1112.26) |
| 211101 / STILE - BACK | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1235.0) | (-1244.0, 807.0, 132.26, -1204.0, 847.0, 1092.26) |
| 211101 / STILE - FRONT | (-1244.0, -642.74, 132.26, -1204.0, -622.74, 1235.0) | (-1244.0, -447.74, 132.26, -1204.0, -427.74, 1092.26) |
| 211101 / STILE - MID 1 | (-1244.0, -277.81, 132.26, -1204.0, -257.81, 1235.0) | (-1244.0, -131.56, 132.26, -1204.0, -111.56, 1092.26) |
| 211101 / STILE - MID 2 | (-1244.0, 87.13, 132.26, -1204.0, 107.13, 1235.0) | (-1244.0, 184.63, 132.26, -1204.0, 204.63, 1092.26) |
| 211101 / STILE - MID 3 | (-1244.0, 452.06, 132.26, -1204.0, 472.06, 1235.0) | (-1244.0, 500.81, 132.26, -1204.0, 520.81, 1092.26) |
| 211301 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 112.26, -1204.0, 850.0, 1255.0) | (-1250.0, -447.74, 112.26, -1204.0, 850.0, 1112.26) |
| 211501 / FILL - BAY 1 | (-1244.0, -622.74, 132.26, -1204.0, -277.81, 1235.0) | (-1244.0, -427.74, 132.26, -1204.0, -131.56, 1092.26) |
| 211501 / FILL - BAY 2 | (-1244.0, -257.81, 132.26, -1204.0, 87.13, 1235.0) | (-1244.0, -111.56, 132.26, -1204.0, 184.63, 1092.26) |
| 211501 / FILL - BAY 3 | (-1244.0, 107.13, 132.26, -1204.0, 452.06, 1235.0) | (-1244.0, 204.63, 132.26, -1204.0, 500.81, 1092.26) |
| 211501 / FILL - BAY 4 | (-1244.0, 472.06, 132.26, -1204.0, 807.0, 1235.0) | (-1244.0, 520.81, 132.26, -1204.0, 807.0, 1092.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT BACK | (-1228.0, 746.0, 1245.76, -1220.0, 754.0, 1263.0) | (-1228.0, 746.0, 1103.02, -1220.0, 754.0, 1120.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT FRONT | (-1228.0, -546.74, 1245.76, -1220.0, -538.74, 1263.0) | (-1228.0, -351.74, 1103.02, -1220.0, -343.74, 1120.26) |
| 831002 / STOP WASHER - BACK STILE CORNER 1 | (-1204.0, 814.0, 322.26, -1202.5, 834.0, 342.26) | (-1204.0, 814.0, 322.26, -1202.5, 834.0, 342.26) |
| 831002 / STOP WASHER - BACK STILE CORNER 2 | (-1204.0, 814.0, 661.56, -1202.5, 834.0, 681.56) | (-1204.0, 814.0, 661.56, -1202.5, 834.0, 681.56) |
| 831002 / STOP WASHER - BACK STILE CORNER 3 | (-1204.0, 814.0, 1000.87, -1202.5, 834.0, 1020.87) | (-1204.0, 814.0, 1000.87, -1202.5, 834.0, 1020.87) |
| 831002 / STOP WASHER - TOP RAIL 1 | (-1234.0, -432.74, 1255.0, -1214.0, -412.74, 1256.5) | (-1234.0, -237.74, 1112.26, -1214.0, -217.74, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 2 | (-1234.0, -81.83, 1255.0, -1214.0, -61.83, 1256.5) | (-1234.0, 48.17, 1112.26, -1214.0, 68.17, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 3 | (-1234.0, 269.09, 1255.0, -1214.0, 289.09, 1256.5) | (-1234.0, 334.09, 1112.26, -1214.0, 354.09, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 4 | (-1234.0, 620.0, 1255.0, -1214.0, 640.0, 1256.5) | (-1234.0, 620.0, 1112.26, -1214.0, 640.0, 1113.76) |
| 838003 / RIVNUT - BACK STILE CORNER 1 | (-1212.66, 817.52, 325.78, -1201.74, 830.48, 338.74) | (-1212.66, 817.52, 325.78, -1201.74, 830.48, 338.74) |
| 838003 / RIVNUT - BACK STILE CORNER 2 | (-1212.66, 817.52, 665.09, -1201.74, 830.48, 678.05) | (-1212.66, 817.52, 665.09, -1201.74, 830.48, 678.05) |
| 838003 / RIVNUT - BACK STILE CORNER 3 | (-1212.66, 817.52, 1004.39, -1201.74, 830.48, 1017.35) | (-1212.66, 817.52, 1004.39, -1201.74, 830.48, 1017.35) |
| 838003 / RIVNUT - TOP RAIL 1 | (-1230.48, -429.22, 1246.34, -1217.52, -416.26, 1257.26) | (-1230.48, -234.22, 1103.6, -1217.52, -221.26, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 2 | (-1230.48, -78.31, 1246.34, -1217.52, -65.35, 1257.26) | (-1230.48, 51.69, 1103.6, -1217.52, 64.65, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 3 | (-1230.48, 272.61, 1246.34, -1217.52, 285.57, 1257.26) | (-1230.48, 337.61, 1103.6, -1217.52, 350.57, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 4 | (-1230.48, 623.52, 1246.34, -1217.52, 636.48, 1257.26) | (-1230.48, 623.52, 1103.6, -1217.52, 636.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL SPIGOT BACK | (-1230.48, 743.52, 1244.84, -1217.52, 756.48, 1255.76) | (-1230.48, 743.52, 1102.1, -1217.52, 756.48, 1113.02) |
| 838003 / RIVNUT - TOP RAIL SPIGOT FRONT | (-1230.48, -549.22, 1244.84, -1217.52, -536.26, 1255.76) | (-1230.48, -354.22, 1102.1, -1217.52, -341.26, 1113.02) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span side_h - 20 - top_h | PASS |
| mid stile count follows the 400 mm rule (3) | PASS |
| no stile pitch over 400 | PASS |
| fill bays = mid stile count + 1 (4) | PASS |
| skin runs wall_depth - 2.26 and side_h | PASS |
| top rail rivnuts follow the 220 rule [-227.74, 58.17, 344.09, 630.0] | PASS |
| a stop washer under each top rail rivnut | PASS |
| front spigot follows the panel's front end (+100) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 164 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211102, 211302, 211502, 831001, 831002, 838003.

1. Reopen: timeline 164 items, 0 not healthy; sketches 47, 47 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm: rebuild 164 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 3 |
| stile_pitch | 364.935 | 316.185 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211102 / RAIL - BOTTOM | (1204.0, -642.74, 112.26, 1244.0, 847.0, 132.26) | (1204.0, -447.74, 112.26, 1244.0, 847.0, 132.26) |
| 211102 / RAIL - TOP | (1204.0, -642.74, 1235.0, 1244.0, 847.0, 1255.0) | (1204.0, -447.74, 1092.26, 1244.0, 847.0, 1112.26) |
| 211102 / STILE - BACK | (1204.0, 807.0, 132.26, 1244.0, 847.0, 1235.0) | (1204.0, 807.0, 132.26, 1244.0, 847.0, 1092.26) |
| 211102 / STILE - FRONT | (1204.0, -642.74, 132.26, 1244.0, -622.74, 1235.0) | (1204.0, -447.74, 132.26, 1244.0, -427.74, 1092.26) |
| 211102 / STILE - MID 1 | (1204.0, -277.81, 132.26, 1244.0, -257.81, 1235.0) | (1204.0, -131.56, 132.26, 1244.0, -111.56, 1092.26) |
| 211102 / STILE - MID 2 | (1204.0, 87.13, 132.26, 1244.0, 107.13, 1235.0) | (1204.0, 184.63, 132.26, 1244.0, 204.63, 1092.26) |
| 211102 / STILE - MID 3 | (1204.0, 452.06, 132.26, 1244.0, 472.06, 1235.0) | (1204.0, 500.81, 132.26, 1244.0, 520.81, 1092.26) |
| 211302 / SKIN - ACP 3 WITH BACK RETURN | (1204.0, -642.74, 112.26, 1250.0, 850.0, 1255.0) | (1204.0, -447.74, 112.26, 1250.0, 850.0, 1112.26) |
| 211502 / FILL - BAY 1 | (1204.0, -622.74, 132.26, 1244.0, -277.81, 1235.0) | (1204.0, -427.74, 132.26, 1244.0, -131.56, 1092.26) |
| 211502 / FILL - BAY 2 | (1204.0, -257.81, 132.26, 1244.0, 87.13, 1235.0) | (1204.0, -111.56, 132.26, 1244.0, 184.63, 1092.26) |
| 211502 / FILL - BAY 3 | (1204.0, 107.13, 132.26, 1244.0, 452.06, 1235.0) | (1204.0, 204.63, 132.26, 1244.0, 500.81, 1092.26) |
| 211502 / FILL - BAY 4 | (1204.0, 472.06, 132.26, 1244.0, 807.0, 1235.0) | (1204.0, 520.81, 132.26, 1244.0, 807.0, 1092.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT BACK | (1220.0, 746.0, 1245.76, 1228.0, 754.0, 1263.0) | (1220.0, 746.0, 1103.02, 1228.0, 754.0, 1120.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT FRONT | (1220.0, -546.74, 1245.76, 1228.0, -538.74, 1263.0) | (1220.0, -351.74, 1103.02, 1228.0, -343.74, 1120.26) |
| 831002 / STOP WASHER - BACK STILE CORNER 1 | (1202.5, 814.0, 322.26, 1204.0, 834.0, 342.26) | (1202.5, 814.0, 322.26, 1204.0, 834.0, 342.26) |
| 831002 / STOP WASHER - BACK STILE CORNER 2 | (1202.5, 814.0, 661.56, 1204.0, 834.0, 681.56) | (1202.5, 814.0, 661.56, 1204.0, 834.0, 681.56) |
| 831002 / STOP WASHER - BACK STILE CORNER 3 | (1202.5, 814.0, 1000.87, 1204.0, 834.0, 1020.87) | (1202.5, 814.0, 1000.87, 1204.0, 834.0, 1020.87) |
| 831002 / STOP WASHER - TOP RAIL 1 | (1214.0, -432.74, 1255.0, 1234.0, -412.74, 1256.5) | (1214.0, -237.74, 1112.26, 1234.0, -217.74, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 2 | (1214.0, -81.83, 1255.0, 1234.0, -61.83, 1256.5) | (1214.0, 48.17, 1112.26, 1234.0, 68.17, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 3 | (1214.0, 269.09, 1255.0, 1234.0, 289.09, 1256.5) | (1214.0, 334.09, 1112.26, 1234.0, 354.09, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 4 | (1214.0, 620.0, 1255.0, 1234.0, 640.0, 1256.5) | (1214.0, 620.0, 1112.26, 1234.0, 640.0, 1113.76) |
| 838003 / RIVNUT - BACK STILE CORNER 1 | (1201.74, 817.52, 325.78, 1212.66, 830.48, 338.74) | (1201.74, 817.52, 325.78, 1212.66, 830.48, 338.74) |
| 838003 / RIVNUT - BACK STILE CORNER 2 | (1201.74, 817.52, 665.09, 1212.66, 830.48, 678.05) | (1201.74, 817.52, 665.09, 1212.66, 830.48, 678.05) |
| 838003 / RIVNUT - BACK STILE CORNER 3 | (1201.74, 817.52, 1004.39, 1212.66, 830.48, 1017.35) | (1201.74, 817.52, 1004.39, 1212.66, 830.48, 1017.35) |
| 838003 / RIVNUT - TOP RAIL 1 | (1217.52, -429.22, 1246.34, 1230.48, -416.26, 1257.26) | (1217.52, -234.22, 1103.6, 1230.48, -221.26, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 2 | (1217.52, -78.31, 1246.34, 1230.48, -65.35, 1257.26) | (1217.52, 51.69, 1103.6, 1230.48, 64.65, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 3 | (1217.52, 272.61, 1246.34, 1230.48, 285.57, 1257.26) | (1217.52, 337.61, 1103.6, 1230.48, 350.57, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 4 | (1217.52, 623.52, 1246.34, 1230.48, 636.48, 1257.26) | (1217.52, 623.52, 1103.6, 1230.48, 636.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL SPIGOT BACK | (1217.52, 743.52, 1244.84, 1230.48, 756.48, 1255.76) | (1217.52, 743.52, 1102.1, 1230.48, 756.48, 1113.02) |
| 838003 / RIVNUT - TOP RAIL SPIGOT FRONT | (1217.52, -549.22, 1244.84, 1230.48, -536.26, 1255.76) | (1217.52, -354.22, 1102.1, 1230.48, -341.26, 1113.02) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span side_h - 20 - top_h | PASS |
| mid stile count follows the 400 mm rule (3) | PASS |
| no stile pitch over 400 | PASS |
| fill bays = mid stile count + 1 (4) | PASS |
| skin runs wall_depth - 2.26 and side_h | PASS |
| top rail rivnuts follow the 220 rule [-227.74, 58.17, 344.09, 630.0] | PASS |
| a stop washer under each top rail rivnut | PASS |
| front spigot follows the panel's front end (+100) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 164 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 210103_P01_WALL-PANEL-ASSY-SIDE-UPPER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211103, 211303, 211503, 831002, 838003.

1. Reopen: timeline 129 items, 0 not healthy; sketches 37, 37 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 129 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 3 |
| stile_pitch | 364.935 | 316.185 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211103 / RAIL - BOTTOM | (-1244.0, -642.74, 1257.26, -1204.0, 847.0, 1277.26) | (-1244.0, -447.74, 1234.52, -1204.0, 847.0, 1254.52) |
| 211103 / RAIL - TOP | (-1244.0, -642.74, 2360.0, -1204.0, 847.0, 2400.0) | (-1244.0, -447.74, 2360.0, -1204.0, 847.0, 2400.0) |
| 211103 / STILE - BACK | (-1244.0, 807.0, 1277.26, -1204.0, 847.0, 2360.0) | (-1244.0, 807.0, 1254.52, -1204.0, 847.0, 2360.0) |
| 211103 / STILE - FRONT | (-1244.0, -642.74, 1277.26, -1204.0, -622.74, 2360.0) | (-1244.0, -447.74, 1254.52, -1204.0, -427.74, 2360.0) |
| 211103 / STILE - MID 1 | (-1244.0, -277.81, 1277.26, -1204.0, -257.81, 2360.0) | (-1244.0, -131.56, 1254.52, -1204.0, -111.56, 2360.0) |
| 211103 / STILE - MID 2 | (-1244.0, 87.13, 1277.26, -1204.0, 107.13, 2360.0) | (-1244.0, 184.63, 1254.52, -1204.0, 204.63, 2360.0) |
| 211103 / STILE - MID 3 | (-1244.0, 452.06, 1277.26, -1204.0, 472.06, 2360.0) | (-1244.0, 500.81, 1254.52, -1204.0, 520.81, 2360.0) |
| 211303 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 1257.26, -1204.0, 850.0, 2400.0) | (-1250.0, -447.74, 1234.52, -1204.0, 850.0, 2400.0) |
| 211503 / FILL - BAY 1 | (-1244.0, -622.74, 1277.26, -1204.0, -277.81, 2360.0) | (-1244.0, -427.74, 1254.52, -1204.0, -131.56, 2360.0) |
| 211503 / FILL - BAY 2 | (-1244.0, -257.81, 1277.26, -1204.0, 87.13, 2360.0) | (-1244.0, -111.56, 1254.52, -1204.0, 184.63, 2360.0) |
| 211503 / FILL - BAY 3 | (-1244.0, 107.13, 1277.26, -1204.0, 452.06, 2360.0) | (-1244.0, 204.63, 1254.52, -1204.0, 500.81, 2360.0) |
| 211503 / FILL - BAY 4 | (-1244.0, 472.06, 1277.26, -1204.0, 807.0, 2360.0) | (-1244.0, 520.81, 1254.52, -1204.0, 807.0, 2360.0) |
| 831002 / STOP WASHER - BACK STILE CORNER 1 | (-1204.0, 814.0, 1443.13, -1202.5, 834.0, 1463.13) | (-1204.0, 814.0, 1443.13, -1202.5, 834.0, 1463.13) |
| 831002 / STOP WASHER - BACK STILE CORNER 2 | (-1204.0, 814.0, 1782.43, -1202.5, 834.0, 1802.43) | (-1204.0, 814.0, 1782.43, -1202.5, 834.0, 1802.43) |
| 831002 / STOP WASHER - BACK STILE CORNER 3 | (-1204.0, 814.0, 2121.74, -1202.5, 834.0, 2141.74) | (-1204.0, 814.0, 2121.74, -1202.5, 834.0, 2141.74) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 1 | (-1204.0, -435.0, 2364.0, -1202.5, -415.0, 2384.0) | (-1204.0, -240.0, 2364.0, -1202.5, -220.0, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 2 | (-1204.0, -83.33, 2364.0, -1202.5, -63.33, 2384.0) | (-1204.0, 46.67, 2364.0, -1202.5, 66.67, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 3 | (-1204.0, 268.33, 2364.0, -1202.5, 288.33, 2384.0) | (-1204.0, 333.33, 2364.0, -1202.5, 353.33, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 4 | (-1204.0, 620.0, 2364.0, -1202.5, 640.0, 2384.0) | (-1204.0, 620.0, 2364.0, -1202.5, 640.0, 2384.0) |
| 838003 / RIVNUT - BACK STILE CORNER 1 | (-1212.66, 817.52, 1446.65, -1201.74, 830.48, 1459.61) | (-1212.66, 817.52, 1446.65, -1201.74, 830.48, 1459.61) |
| 838003 / RIVNUT - BACK STILE CORNER 2 | (-1212.66, 817.52, 1785.95, -1201.74, 830.48, 1798.91) | (-1212.66, 817.52, 1785.95, -1201.74, 830.48, 1798.91) |
| 838003 / RIVNUT - BACK STILE CORNER 3 | (-1212.66, 817.52, 2125.26, -1201.74, 830.48, 2138.22) | (-1212.66, 817.52, 2125.26, -1201.74, 830.48, 2138.22) |
| 838003 / RIVNUT - TOP MEMBER CEILING 1 | (-1212.66, -431.48, 2367.52, -1201.74, -418.52, 2380.48) | (-1212.66, -236.48, 2367.52, -1201.74, -223.52, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 2 | (-1212.66, -79.81, 2367.52, -1201.74, -66.85, 2380.48) | (-1212.66, 50.19, 2367.52, -1201.74, 63.15, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 3 | (-1212.66, 271.85, 2367.52, -1201.74, 284.81, 2380.48) | (-1212.66, 336.85, 2367.52, -1201.74, 349.81, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 4 | (-1212.66, 623.52, 2367.52, -1201.74, 636.48, 2380.48) | (-1212.66, 623.52, 2367.52, -1201.74, 636.48, 2380.48) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span the panel height - 20 - top_h | PASS |
| mid stile count follows the 400 mm rule (3) | PASS |
| no stile pitch over 400 | PASS |
| fill bays = mid stile count + 1 (4) | PASS |
| skin runs wall_depth - 2.26 and the panel height | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 129 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 210104_P01_WALL-PANEL-ASSY-SIDE-UPPER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211104, 211304, 211504, 831002, 838003.

1. Reopen: timeline 129 items, 0 not healthy; sketches 37, 37 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 129 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 3 |
| stile_pitch | 364.935 | 316.185 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211104 / RAIL - BOTTOM | (1204.0, -642.74, 1257.26, 1244.0, 847.0, 1277.26) | (1204.0, -447.74, 1234.52, 1244.0, 847.0, 1254.52) |
| 211104 / RAIL - TOP | (1204.0, -642.74, 2360.0, 1244.0, 847.0, 2400.0) | (1204.0, -447.74, 2360.0, 1244.0, 847.0, 2400.0) |
| 211104 / STILE - BACK | (1204.0, 807.0, 1277.26, 1244.0, 847.0, 2360.0) | (1204.0, 807.0, 1254.52, 1244.0, 847.0, 2360.0) |
| 211104 / STILE - FRONT | (1204.0, -642.74, 1277.26, 1244.0, -622.74, 2360.0) | (1204.0, -447.74, 1254.52, 1244.0, -427.74, 2360.0) |
| 211104 / STILE - MID 1 | (1204.0, -277.81, 1277.26, 1244.0, -257.81, 2360.0) | (1204.0, -131.56, 1254.52, 1244.0, -111.56, 2360.0) |
| 211104 / STILE - MID 2 | (1204.0, 87.13, 1277.26, 1244.0, 107.13, 2360.0) | (1204.0, 184.63, 1254.52, 1244.0, 204.63, 2360.0) |
| 211104 / STILE - MID 3 | (1204.0, 452.06, 1277.26, 1244.0, 472.06, 2360.0) | (1204.0, 500.81, 1254.52, 1244.0, 520.81, 2360.0) |
| 211304 / SKIN - ACP 3 WITH BACK RETURN | (1204.0, -642.74, 1257.26, 1250.0, 850.0, 2400.0) | (1204.0, -447.74, 1234.52, 1250.0, 850.0, 2400.0) |
| 211504 / FILL - BAY 1 | (1204.0, -622.74, 1277.26, 1244.0, -277.81, 2360.0) | (1204.0, -427.74, 1254.52, 1244.0, -131.56, 2360.0) |
| 211504 / FILL - BAY 2 | (1204.0, -257.81, 1277.26, 1244.0, 87.13, 2360.0) | (1204.0, -111.56, 1254.52, 1244.0, 184.63, 2360.0) |
| 211504 / FILL - BAY 3 | (1204.0, 107.13, 1277.26, 1244.0, 452.06, 2360.0) | (1204.0, 204.63, 1254.52, 1244.0, 500.81, 2360.0) |
| 211504 / FILL - BAY 4 | (1204.0, 472.06, 1277.26, 1244.0, 807.0, 2360.0) | (1204.0, 520.81, 1254.52, 1244.0, 807.0, 2360.0) |
| 831002 / STOP WASHER - BACK STILE CORNER 1 | (1202.5, 814.0, 1443.13, 1204.0, 834.0, 1463.13) | (1202.5, 814.0, 1443.13, 1204.0, 834.0, 1463.13) |
| 831002 / STOP WASHER - BACK STILE CORNER 2 | (1202.5, 814.0, 1782.43, 1204.0, 834.0, 1802.43) | (1202.5, 814.0, 1782.43, 1204.0, 834.0, 1802.43) |
| 831002 / STOP WASHER - BACK STILE CORNER 3 | (1202.5, 814.0, 2121.74, 1204.0, 834.0, 2141.74) | (1202.5, 814.0, 2121.74, 1204.0, 834.0, 2141.74) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 1 | (1202.5, -435.0, 2364.0, 1204.0, -415.0, 2384.0) | (1202.5, -240.0, 2364.0, 1204.0, -220.0, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 2 | (1202.5, -83.33, 2364.0, 1204.0, -63.33, 2384.0) | (1202.5, 46.67, 2364.0, 1204.0, 66.67, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 3 | (1202.5, 268.33, 2364.0, 1204.0, 288.33, 2384.0) | (1202.5, 333.33, 2364.0, 1204.0, 353.33, 2384.0) |
| 831002 / STOP WASHER - TOP MEMBER CEILING 4 | (1202.5, 620.0, 2364.0, 1204.0, 640.0, 2384.0) | (1202.5, 620.0, 2364.0, 1204.0, 640.0, 2384.0) |
| 838003 / RIVNUT - BACK STILE CORNER 1 | (1201.74, 817.52, 1446.65, 1212.66, 830.48, 1459.61) | (1201.74, 817.52, 1446.65, 1212.66, 830.48, 1459.61) |
| 838003 / RIVNUT - BACK STILE CORNER 2 | (1201.74, 817.52, 1785.95, 1212.66, 830.48, 1798.91) | (1201.74, 817.52, 1785.95, 1212.66, 830.48, 1798.91) |
| 838003 / RIVNUT - BACK STILE CORNER 3 | (1201.74, 817.52, 2125.26, 1212.66, 830.48, 2138.22) | (1201.74, 817.52, 2125.26, 1212.66, 830.48, 2138.22) |
| 838003 / RIVNUT - TOP MEMBER CEILING 1 | (1201.74, -431.48, 2367.52, 1212.66, -418.52, 2380.48) | (1201.74, -236.48, 2367.52, 1212.66, -223.52, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 2 | (1201.74, -79.81, 2367.52, 1212.66, -66.85, 2380.48) | (1201.74, 50.19, 2367.52, 1212.66, 63.15, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 3 | (1201.74, 271.85, 2367.52, 1212.66, 284.81, 2380.48) | (1201.74, 336.85, 2367.52, 1212.66, 349.81, 2380.48) |
| 838003 / RIVNUT - TOP MEMBER CEILING 4 | (1201.74, 623.52, 2367.52, 1212.66, 636.48, 2380.48) | (1201.74, 623.52, 2367.52, 1212.66, 636.48, 2380.48) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span the panel height - 20 - top_h | PASS |
| mid stile count follows the 400 mm rule (3) | PASS |
| no stile pitch over 400 | PASS |
| fill bays = mid stile count + 1 (4) | PASS |
| skin runs wall_depth - 2.26 and the panel height | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 129 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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
| top_h | 20 | 20 |

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
| stiles span side_h - 20 - top_h | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 73 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211102_P01_WALL-PANEL-FRAME-SIDE-LOWER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211102.

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
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211102 / RAIL - BOTTOM | (1204.0, -642.74, 112.26, 1244.0, 847.0, 132.26) | (1204.0, -447.74, 112.26, 1244.0, 847.0, 132.26) |
| 211102 / RAIL - TOP | (1204.0, -642.74, 1235.0, 1244.0, 847.0, 1255.0) | (1204.0, -447.74, 1092.26, 1244.0, 847.0, 1112.26) |
| 211102 / STILE - BACK | (1204.0, 807.0, 132.26, 1244.0, 847.0, 1235.0) | (1204.0, 807.0, 132.26, 1244.0, 847.0, 1092.26) |
| 211102 / STILE - FRONT | (1204.0, -642.74, 132.26, 1244.0, -622.74, 1235.0) | (1204.0, -447.74, 132.26, 1244.0, -427.74, 1092.26) |
| 211102 / STILE - MID 1 | (1204.0, -277.81, 132.26, 1244.0, -257.81, 1235.0) | (1204.0, -194.79, 132.26, 1244.0, -174.79, 1092.26) |
| 211102 / STILE - MID 1 (1) | - | (1204.0, 564.05, 132.26, 1244.0, 584.05, 1092.26) |
| 211102 / STILE - MID 2 | (1204.0, 87.13, 132.26, 1244.0, 107.13, 1235.0) | (1204.0, 58.16, 132.26, 1244.0, 78.16, 1092.26) |
| 211102 / STILE - MID 3 | (1204.0, 452.06, 132.26, 1244.0, 472.06, 1235.0) | (1204.0, 311.1, 132.26, 1244.0, 331.1, 1092.26) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span side_h - 20 - top_h | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 73 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211103_P01_WALL-PANEL-FRAME-SIDE-UPPER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211103.

1. Reopen: timeline 67 items, 0 not healthy; sketches 20, 20 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm, stile_pitch_max -> 300 mm: rebuild 67 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211103 / RAIL - BOTTOM | (-1244.0, -642.74, 1257.26, -1204.0, 847.0, 1277.26) | (-1244.0, -447.74, 1234.52, -1204.0, 847.0, 1254.52) |
| 211103 / RAIL - TOP | (-1244.0, -642.74, 2360.0, -1204.0, 847.0, 2400.0) | (-1244.0, -447.74, 2360.0, -1204.0, 847.0, 2400.0) |
| 211103 / STILE - BACK | (-1244.0, 807.0, 1277.26, -1204.0, 847.0, 2360.0) | (-1244.0, 807.0, 1254.52, -1204.0, 847.0, 2360.0) |
| 211103 / STILE - FRONT | (-1244.0, -642.74, 1277.26, -1204.0, -622.74, 2360.0) | (-1244.0, -447.74, 1254.52, -1204.0, -427.74, 2360.0) |
| 211103 / STILE - MID 1 | (-1244.0, -277.81, 1277.26, -1204.0, -257.81, 2360.0) | (-1244.0, -194.79, 1254.52, -1204.0, -174.79, 2360.0) |
| 211103 / STILE - MID 1 (1) | - | (-1244.0, 564.05, 1254.52, -1204.0, 584.05, 2360.0) |
| 211103 / STILE - MID 2 | (-1244.0, 87.13, 1277.26, -1204.0, 107.13, 2360.0) | (-1244.0, 58.16, 1254.52, -1204.0, 78.16, 2360.0) |
| 211103 / STILE - MID 3 | (-1244.0, 452.06, 1277.26, -1204.0, 472.06, 2360.0) | (-1244.0, 311.1, 1254.52, -1204.0, 331.1, 2360.0) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span the panel height - 20 - top_h | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 67 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211104_P01_WALL-PANEL-FRAME-SIDE-UPPER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211104.

1. Reopen: timeline 67 items, 0 not healthy; sketches 20, 20 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm, stile_pitch_max -> 300 mm: rebuild 67 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211104 / RAIL - BOTTOM | (1204.0, -642.74, 1257.26, 1244.0, 847.0, 1277.26) | (1204.0, -447.74, 1234.52, 1244.0, 847.0, 1254.52) |
| 211104 / RAIL - TOP | (1204.0, -642.74, 2360.0, 1244.0, 847.0, 2400.0) | (1204.0, -447.74, 2360.0, 1244.0, 847.0, 2400.0) |
| 211104 / STILE - BACK | (1204.0, 807.0, 1277.26, 1244.0, 847.0, 2360.0) | (1204.0, 807.0, 1254.52, 1244.0, 847.0, 2360.0) |
| 211104 / STILE - FRONT | (1204.0, -642.74, 1277.26, 1244.0, -622.74, 2360.0) | (1204.0, -447.74, 1254.52, 1244.0, -427.74, 2360.0) |
| 211104 / STILE - MID 1 | (1204.0, -277.81, 1277.26, 1244.0, -257.81, 2360.0) | (1204.0, -194.79, 1254.52, 1244.0, -174.79, 2360.0) |
| 211104 / STILE - MID 1 (1) | - | (1204.0, 564.05, 1254.52, 1244.0, 584.05, 2360.0) |
| 211104 / STILE - MID 2 | (1204.0, 87.13, 1277.26, 1244.0, 107.13, 2360.0) | (1204.0, 58.16, 1254.52, 1244.0, 78.16, 2360.0) |
| 211104 / STILE - MID 3 | (1204.0, 452.06, 1277.26, 1244.0, 472.06, 2360.0) | (1204.0, 311.1, 1254.52, 1244.0, 331.1, 2360.0) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 3 | PASS |
| frame starts 2.26 behind the decor back plate | PASS |
| stiles span the panel height - 20 - top_h | PASS |
| mid stile count follows the 300 mm rule (4) | PASS |
| no stile pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 67 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211301_P01_WALL-SKIN-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211301.

1. Reopen: timeline 8 items, 0 not healthy; sketches 2, 2 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 8 items, 0 not healthy, 0 sketches not fully constrained.

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
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211301 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 112.26, -1204.0, 850.0, 1255.0) | (-1250.0, -447.74, 112.26, -1204.0, 850.0, 1112.26) |

| Check | Result |
|---|---|
| skin runs wall_depth - 2.26 and side_h | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 8 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211501.

1. Reopen: timeline 30 items, 0 not healthy; sketches 9, 9 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm: rebuild 30 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1000 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 3 |
| stile_pitch | 364.935 | 316.185 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1000 |
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211501 / FILL - BAY 1 | (-1244.0, -622.74, 132.26, -1204.0, -277.81, 1235.0) | (-1244.0, -427.74, 132.26, -1204.0, -131.56, 1092.26) |
| 211501 / FILL - BAY 2 | (-1244.0, -257.81, 132.26, -1204.0, 87.13, 1235.0) | (-1244.0, -111.56, 132.26, -1204.0, 184.63, 1092.26) |
| 211501 / FILL - BAY 3 | (-1244.0, 107.13, 132.26, -1204.0, 452.06, 1235.0) | (-1244.0, 204.63, 132.26, -1204.0, 500.81, 1092.26) |
| 211501 / FILL - BAY 4 | (-1244.0, 472.06, 132.26, -1204.0, 807.0, 1235.0) | (-1244.0, 520.81, 132.26, -1204.0, 807.0, 1092.26) |

| Check | Result |
|---|---|
| fill bays = mid stile count + 1 (4) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 30 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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
| top_h | 20 | 20 |

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
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray height follows side_h | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 24 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510102_P01_LINING-CASSETTE-SIDE-LOWER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511102, 511302, NO-PN-HOLD-H03.

1. Reopen: timeline 33 items, 0 not healthy; sketches 9, 9 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm, stile_pitch_max -> 300 mm: rebuild 33 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1120 |
| top_h | 20 | 20 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |
| el_y_kit | 240.5 | 338 |
| el_y_cx | -298 | -103 |
| el_trunk_z | 1100 | 1100 |
| el_kit_dz | 80 | 80 |
| el_kit_d | 60 | 60 |
| el_grm_d | 19.1 | 19.1 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511102 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (1166.0, -645.0, 112.26, 1200.0, 800.0, 1255.0) | (1166.0, -450.0, 112.26, 1200.0, 800.0, 1232.26) |
| 511302 / FELT - PET 9 HELD BY THE TRAY LIPS | (1166.5, -643.5, 113.76, 1175.5, 798.5, 1253.5) | (1166.5, -448.5, 113.76, 1175.5, 798.5, 1230.76) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (1200.0, -277.81, 182.26, 1204.0, -257.81, 242.26) | (1200.0, -194.79, 182.26, 1204.0, -174.79, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (1200.0, 452.06, 182.26, 1204.0, 472.06, 242.26) | (1200.0, 564.05, 182.26, 1204.0, 584.05, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP FRONT) | (1200.0, -277.81, 1125.0, 1204.0, -257.81, 1185.0) | (1200.0, -194.79, 1102.26, 1204.0, -174.79, 1162.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP BACK) | (1200.0, 452.06, 1125.0, 1204.0, 472.06, 1185.0) | (1200.0, 564.05, 1102.26, 1204.0, 584.05, 1162.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray height follows the row (cass_h) | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| el_y_kit moves half the wall_depth change (+97.50) | PASS |
| FA-KIT 60 hole at Y el_y_kit, Z trunk + 80 | PASS |
| FX-COL 19.1 hole follows the column's back face (Y -103.00) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 33 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510103_P01_LINING-CASSETTE-SIDE-UPPER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511103, 511303, NO-PN-HOLD-H03.

1. Reopen: timeline 24 items, 0 not healthy; sketches 6, 6 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm, stile_pitch_max -> 300 mm: rebuild 24 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511103 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1200.0, -645.0, 1257.26, -1166.0, 800.0, 2350.0) | (-1200.0, -450.0, 1234.52, -1166.0, 800.0, 2350.0) |
| 511303 / FELT - PET 9 HELD BY THE TRAY LIPS | (-1175.5, -643.5, 1258.76, -1166.5, 798.5, 2348.5) | (-1175.5, -448.5, 1236.02, -1166.5, 798.5, 2348.5) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (-1204.0, -277.81, 1327.26, -1200.0, -257.81, 1387.26) | (-1204.0, -194.79, 1304.52, -1200.0, -174.79, 1364.52) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (-1204.0, 452.06, 1327.26, -1200.0, 472.06, 1387.26) | (-1204.0, 564.05, 1304.52, -1200.0, 584.05, 1364.52) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP FRONT) | (-1204.0, -277.81, 2220.0, -1200.0, -257.81, 2280.0) | (-1204.0, -194.79, 2220.0, -1200.0, -174.79, 2280.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP BACK) | (-1204.0, 452.06, 2220.0, -1200.0, 472.06, 2280.0) | (-1204.0, 564.05, 2220.0, -1200.0, 584.05, 2280.0) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray height follows the row (cass_h) | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 24 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510104_P01_LINING-CASSETTE-SIDE-UPPER-RH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511104, 511304, NO-PN-HOLD-H03.

1. Reopen: timeline 30 items, 0 not healthy; sketches 8, 8 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm, stile_pitch_max -> 300 mm: rebuild 30 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 3 | 4 |
| stile_pitch | 364.935 | 252.948 |
| cass_len | 1445 | 1250 |
| cass_h | 1092.74 | 1115.48 |
| top_h | 40 | 40 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |
| el_call_y | -209.5 | -112 |
| el_call_z | 1450 | 1450 |
| el_shelf_z | 2250 | 2250 |
| el_grm_s | 12 | 12 |
| el_y_kit | 240.5 | 338 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511104 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (1166.0, -645.0, 1257.26, 1200.0, 800.0, 2350.0) | (1166.0, -450.0, 1234.52, 1200.0, 800.0, 2350.0) |
| 511304 / FELT - PET 9 HELD BY THE TRAY LIPS | (1166.5, -643.5, 1258.76, 1175.5, 798.5, 2348.5) | (1166.5, -448.5, 1236.02, 1175.5, 798.5, 2348.5) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (1200.0, -277.81, 1327.26, 1204.0, -257.81, 1387.26) | (1200.0, -194.79, 1304.52, 1204.0, -174.79, 1364.52) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (1200.0, 452.06, 1327.26, 1204.0, 472.06, 1387.26) | (1200.0, 564.05, 1304.52, 1204.0, 584.05, 1364.52) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP FRONT) | (1200.0, -277.81, 2220.0, 1204.0, -257.81, 2280.0) | (1200.0, -194.79, 2220.0, 1204.0, -174.79, 2280.0) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP BACK) | (1200.0, 452.06, 2220.0, 1204.0, 472.06, 2280.0) | (1200.0, 564.05, 2220.0, 1204.0, 584.05, 2280.0) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray height follows the row (cass_h) | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last mid stile | PASS |
| top clip zones follow the top edge | PASS |
| el_y_kit moves half the wall_depth change (+97.50) | PASS |
| FX-CALL0 and FX-CALL2 12 holes follow the call light line (Y -112.00) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 30 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 511101_P01_LINING-TRAY-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511101.

1. Reopen: timeline 7 items, 0 not healthy; sketches 1, 1 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1000 mm, stile_pitch_max -> 300 mm: rebuild 7 items, 0 not healthy, 0 sketches not fully constrained.

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
| top_h | 20 | 20 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511101 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1200.0, -645.0, 112.26, -1166.0, 800.0, 1255.0) | (-1200.0, -450.0, 112.26, -1166.0, 800.0, 1112.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts at the decor back plate | PASS |
| tray height follows side_h | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 7 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

