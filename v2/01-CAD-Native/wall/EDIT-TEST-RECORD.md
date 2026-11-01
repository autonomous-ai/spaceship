# Edit test record: WALL designs

Guideline section 4.4. `edit_test_wall.py` (run by `post_wall_doc.py`) opens each exported .f3d as a new, unsaved copy, changes two skeleton values and one wall rule (wall_depth 1495 -> 1300, side_h -> 1000, stile_pitch_max 400 -> 300), checks that every part follows and every feature stays healthy, then reverts and checks that every body is back to its exact box. The copy is closed without saving.

## Edit test: 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101, 211301, 211515, 211516, 211517, 211518, 212101, 212102, 212103, 212104, 212105, 831001, 831002, 831007, 831008, 838003.

1. Reopen: timeline 209 items, 0 not healthy; sketches 48, 48 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 209 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 300 | 300 |
| frm_len | 1486.74 | 1291.74 |
| stile_n_mid | 5 | 5 |
| stud_c1 | 270 | 270 |
| stud_c2 | 520.913 | 455.913 |
| stud_c3 | 746.37 | 648.87 |
| stud_c4 | 971.827 | 841.827 |
| stud_c5 | 1222.74 | 1027.74 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1120 |
| lin_front_dy | 0 | 0 |
| top_h | 20 | 20 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212101 WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH:1 / RAIL - BOTTOM | (-1244.0, -641.33, 112.26, -1204.0, 841.76, 132.26) | (-1244.0, -446.33, 112.26, -1204.0, 841.76, 132.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212102 WALL - FRAME RAIL TOP - SIDE LOWER - LH:1 / RAIL - TOP | (-1244.0, -641.33, 1235.0, -1204.0, 841.76, 1255.0) | (-1244.0, -446.33, 1212.26, -1204.0, 841.76, 1232.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212103 WALL - FRAME STILE FRONT - SIDE LOWER - LH:1 / STILE - FRONT | (-1244.0, -642.74, 113.67, -1204.0, -622.74, 1253.59) | (-1244.0, -447.74, 113.67, -1204.0, -427.74, 1230.85) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212104 WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH:1 / STILE - BACK | (-1244.0, 804.0, 113.38, -1204.0, 844.0, 1253.88) | (-1244.0, 804.0, 113.38, -1204.0, 844.0, 1231.14) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:1 / STILE - MID | (-1244.0, -382.74, 132.26, -1204.0, -362.74, 1235.0) | (-1244.0, -187.74, 132.26, -1204.0, -167.74, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:2 / STILE - MID | (-1244.0, -131.83, 132.26, -1204.0, -111.83, 1235.0) | (-1244.0, -1.83, 132.26, -1204.0, 18.17, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:3 / STILE - MID | (-1244.0, 93.63, 132.26, -1204.0, 113.63, 1235.0) | (-1244.0, 191.13, 132.26, -1204.0, 211.13, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:4 / STILE - MID | (-1244.0, 319.09, 132.26, -1204.0, 339.09, 1235.0) | (-1244.0, 384.09, 132.26, -1204.0, 404.09, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:5 / STILE - MID | (-1244.0, 570.0, 132.26, -1204.0, 590.0, 1235.0) | (-1244.0, 570.0, 132.26, -1204.0, 590.0, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831007 HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL:1 / MITRE PLATE | (-1244.0, -642.21, 112.79, -1204.0, -622.06, 132.94) | (-1244.0, -447.21, 112.79, -1204.0, -427.06, 132.94) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831007 HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL:2 / MITRE PLATE | (-1244.0, -642.21, 1234.32, -1204.0, -622.06, 1254.47) | (-1244.0, -447.21, 1211.58, -1204.0, -427.06, 1231.73) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831008 HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL:1 / MITRE PLATE | (-1244.0, 803.62, 112.77, -1204.0, 841.63, 133.12) | (-1244.0, 803.62, 112.77, -1204.0, 841.63, 133.12) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831008 HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL:2 / MITRE PLATE | (-1244.0, 803.62, 1234.14, -1204.0, 841.63, 1254.49) | (-1244.0, 803.62, 1211.4, -1204.0, 841.63, 1231.75) |
| 211301 WALL - SKIN - SIDE LOWER - LH:1 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 112.26, -1204.0, 850.0, 1255.0) | (-1250.0, -447.74, 112.26, -1204.0, 850.0, 1232.26) |
| 211515 WALL - CAVITY FILL PIECE F01 240 X 1102.7 - SIDE LOWER - COMMON:1 / FILL - BAY 1 | (-1244.0, -622.74, 132.26, -1204.0, -382.74, 1235.0) | (-1244.0, -427.74, 132.26, -1204.0, -187.74, 1212.26) |
| 211516 WALL - CAVITY FILL PIECE F02 230.9 X 1102.7 - SIDE LOWER - COMMON:1 / FILL - BAY 2 | (-1244.0, -362.74, 132.26, -1204.0, -131.83, 1235.0) | (-1244.0, -167.74, 132.26, -1204.0, -1.83, 1212.26) |
| 211516 WALL - CAVITY FILL PIECE F02 230.9 X 1102.7 - SIDE LOWER - COMMON:2 / FILL - BAY 2 | (-1244.0, 339.09, 132.26, -1204.0, 570.0, 1235.0) | (-1244.0, 404.09, 132.26, -1204.0, 570.0, 1212.26) |
| 211517 WALL - CAVITY FILL PIECE F03 205.5 X 1102.7 - SIDE LOWER - COMMON:1 / FILL - BAY 3 | (-1244.0, -111.83, 132.26, -1204.0, 93.63, 1235.0) | (-1244.0, -18.17, 132.26, -1204.0, 154.78, 1212.26) |
| 211517 WALL - CAVITY FILL PIECE F03 205.5 X 1102.7 - SIDE LOWER - COMMON:2 / FILL - BAY 3 | (-1244.0, 113.63, 132.26, -1204.0, 319.09, 1235.0) | (-1244.0, 247.48, 132.26, -1204.0, 420.43, 1212.26) |
| 211518 WALL - CAVITY FILL PIECE F04 214 X 1102.7 - SIDE LOWER - COMMON:1 / FILL - BAY 6 | (-1244.0, 590.0, 132.26, -1204.0, 804.0, 1235.0) | (-1244.0, 590.0, 132.26, -1204.0, 804.0, 1212.26) |
| 831001 HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS:1 / SPIGOT | (-1228.0, -546.74, 1247.76, -1220.0, -538.74, 1263.0) | (-1228.0, -351.74, 1225.02, -1220.0, -343.74, 1240.26) |
| 831001 HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS:2 / SPIGOT | (-1228.0, 746.0, 1247.76, -1220.0, 754.0, 1263.0) | (-1228.0, 746.0, 1225.02, -1220.0, 754.0, 1240.26) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:1 / STOP WASHER | (-1234.0, -432.74, 1255.0, -1214.0, -412.74, 1256.5) | (-1234.0, -237.74, 1232.26, -1214.0, -217.74, 1233.76) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:2 / STOP WASHER | (-1234.0, -81.83, 1255.0, -1214.0, -61.83, 1256.5) | (-1234.0, 48.17, 1232.26, -1214.0, 68.17, 1233.76) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:3 / STOP WASHER | (-1234.0, 269.09, 1255.0, -1214.0, 289.09, 1256.5) | (-1234.0, 334.09, 1232.26, -1214.0, 354.09, 1233.76) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:4 / STOP WASHER | (-1234.0, 620.0, 1255.0, -1214.0, 640.0, 1256.5) | (-1234.0, 620.0, 1232.26, -1214.0, 640.0, 1233.76) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:5 / STOP WASHER | (-1204.0, 814.0, 322.26, -1202.5, 834.0, 342.26) | (-1204.0, 814.0, 322.26, -1202.5, 834.0, 342.26) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:6 / STOP WASHER | (-1204.0, 814.0, 661.56, -1202.5, 834.0, 681.56) | (-1204.0, 814.0, 661.56, -1202.5, 834.0, 681.56) |
| 831002 HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL:7 / STOP WASHER | (-1204.0, 814.0, 1000.87, -1202.5, 834.0, 1020.87) | (-1204.0, 814.0, 1000.87, -1202.5, 834.0, 1020.87) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:1 / RIVNUT | (-1230.48, -429.22, 1246.34, -1217.52, -416.26, 1257.26) | (-1230.48, -234.22, 1223.6, -1217.52, -221.26, 1234.52) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:2 / RIVNUT | (-1230.48, -78.31, 1246.34, -1217.52, -65.35, 1257.26) | (-1230.48, 51.69, 1223.6, -1217.52, 64.65, 1234.52) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:3 / RIVNUT | (-1230.48, 272.61, 1246.34, -1217.52, 285.57, 1257.26) | (-1230.48, 337.61, 1223.6, -1217.52, 350.57, 1234.52) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:4 / RIVNUT | (-1230.48, 623.52, 1246.34, -1217.52, 636.48, 1257.26) | (-1230.48, 623.52, 1223.6, -1217.52, 636.48, 1234.52) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:5 / RIVNUT | (-1230.48, -549.22, 1244.84, -1217.52, -536.26, 1255.76) | (-1230.48, -354.22, 1222.1, -1217.52, -341.26, 1233.02) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:6 / RIVNUT | (-1230.48, 743.52, 1244.84, -1217.52, 756.48, 1255.76) | (-1230.48, 743.52, 1222.1, -1217.52, 756.48, 1233.02) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:7 / RIVNUT | (-1212.66, 817.52, 325.78, -1201.74, 830.48, 338.74) | (-1212.66, 817.52, 325.78, -1201.74, 830.48, 338.74) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:8 / RIVNUT | (-1212.66, 817.52, 665.09, -1201.74, 830.48, 678.04) | (-1212.66, 817.52, 665.09, -1201.74, 830.48, 678.04) |
| 838003 HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2:9 / RIVNUT | (-1212.66, 817.52, 1004.39, -1201.74, 830.48, 1017.35) | (-1212.66, 817.52, 1004.39, -1201.74, 830.48, 1017.35) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 6 (the back return and its bond line) less their plate cut-backs | PASS |
| rails start one cut-back behind the frame's front end (2.26 behind the decor back plate) | PASS |
| perimeter stiles span the panel height less their plate cut-backs | PASS |
| studs span the panel height - 20 - top_h | PASS |
| 5 studs, set from the bolts | PASS |
| every clear bay 275 or less (the skin's 2 mm limit) [240.0, 165.9, 173.0, 173.0, 165.9, 214.0] | PASS |
| every bolt 30 or more clear of every stud (R-J14) | PASS |
| fill bays = stud count + 1 (6) | PASS |
| skin runs wall_depth - 2.26 and the panel height | PASS |
| top rail rivnuts follow the 220 rule [-227.74, 58.17, 344.09, 630.0] | PASS |
| a stop washer under each top rail rivnut | PASS |
| front spigot follows the panel's front end (+100) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 209 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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

## Edit test: 210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211201, 211401, 211601, 831001, 831002, 838003.

1. Reopen: timeline 147 items, 0 not healthy; sketches 42, 42 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1000 mm: rebuild 147 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1000 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 2 |
| stile_pitch | 392.997 | 359.663 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1000 |
| pnl_h | 1118.61 | 1000 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211201 / RAIL - BOTTOM | (-1201.74, 804.0, 112.26, -2.75, 844.0, 132.26) | (-1101.74, 804.0, 112.26, -2.75, 844.0, 132.26) |
| 211201 / RAIL - TOP | (-1201.74, 804.0, 1210.87, -2.75, 844.0, 1230.87) | (-1101.74, 804.0, 1092.26, -2.75, 844.0, 1112.26) |
| 211201 / STILE - CENTRE | (-22.75, 804.0, 132.26, -2.75, 844.0, 1210.87) | (-22.75, 804.0, 132.26, -2.75, 844.0, 1092.26) |
| 211201 / STILE - MID 1 | (-808.74, 804.0, 132.26, -788.74, 844.0, 1210.87) | (-742.08, 804.0, 132.26, -722.08, 844.0, 1092.26) |
| 211201 / STILE - MID 2 | (-415.75, 804.0, 132.26, -395.75, 844.0, 1210.87) | (-382.41, 804.0, 132.26, -362.41, 844.0, 1092.26) |
| 211201 / STILE - OUTER | (-1201.74, 804.0, 132.26, -1181.74, 844.0, 1210.87) | (-1101.74, 804.0, 132.26, -1081.74, 844.0, 1092.26) |
| 211401 / SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM | (-1201.74, 847.0, 112.26, -1.13, 850.0, 1230.87) | (-1101.74, 847.0, 112.26, -1.13, 850.0, 1112.26) |
| 211601 / FILL - BAY 1 | (-1181.74, 804.0, 132.26, -808.74, 844.0, 1210.87) | (-1081.74, 804.0, 132.26, -742.08, 844.0, 1092.26) |
| 211601 / FILL - BAY 2 | (-788.74, 804.0, 132.26, -415.75, 844.0, 1210.87) | (-722.08, 804.0, 132.26, -382.41, 844.0, 1092.26) |
| 211601 / FILL - BAY 3 | (-395.75, 804.0, 132.26, -22.75, 844.0, 1210.87) | (-362.41, 804.0, 132.26, -22.75, 844.0, 1092.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT HIGH X | (-106.75, 820.0, 1221.63, -98.75, 828.0, 1238.87) | (-106.75, 820.0, 1103.02, -98.75, 828.0, 1120.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT LOW X | (-1105.74, 820.0, 1221.63, -1097.74, 828.0, 1238.87) | (-1005.74, 820.0, 1103.02, -997.74, 828.0, 1120.26) |
| 831002 / STOP WASHER - TOP RAIL 1 | (-991.74, 814.0, 1230.87, -971.74, 834.0, 1232.37) | (-891.74, 814.0, 1112.26, -871.74, 834.0, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 2 | (-738.74, 814.0, 1230.87, -718.74, 834.0, 1232.37) | (-672.08, 814.0, 1112.26, -652.08, 834.0, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 3 | (-485.75, 814.0, 1230.87, -465.75, 834.0, 1232.37) | (-452.41, 814.0, 1112.26, -432.41, 834.0, 1113.76) |
| 831002 / STOP WASHER - TOP RAIL 4 | (-232.75, 814.0, 1230.87, -212.75, 834.0, 1232.37) | (-232.75, 814.0, 1112.26, -212.75, 834.0, 1113.76) |
| 838003 / RIVNUT - TOP RAIL 1 | (-988.22, 817.52, 1222.21, -975.26, 830.48, 1233.13) | (-888.22, 817.52, 1103.6, -875.26, 830.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 2 | (-735.22, 817.52, 1222.21, -722.26, 830.48, 1233.13) | (-668.56, 817.52, 1103.6, -655.6, 830.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 3 | (-482.23, 817.52, 1222.21, -469.27, 830.48, 1233.13) | (-448.89, 817.52, 1103.6, -435.93, 830.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL 4 | (-229.23, 817.52, 1222.21, -216.27, 830.48, 1233.13) | (-229.23, 817.52, 1103.6, -216.27, 830.48, 1114.52) |
| 838003 / RIVNUT - TOP RAIL SPIGOT HIGH X | (-109.23, 817.52, 1220.71, -96.27, 830.48, 1231.63) | (-109.23, 817.52, 1102.1, -96.27, 830.48, 1113.02) |
| 838003 / RIVNUT - TOP RAIL SPIGOT LOW X | (-1108.22, 817.52, 1220.71, -1095.26, 830.48, 1231.63) | (-1008.22, 817.52, 1102.1, -995.26, 830.48, 1113.02) |

| Check | Result |
|---|---|
| frame width follows half_fw (1098.99) | PASS |
| frame stays close_gap / 2 from X 0 at the closing seam | PASS |
| frame's outer end stays one seam gap off the side frame (pod_w / 2 - 46 - 2.26) | PASS |
| stiles span the row height - 40 | PASS |
| stud count follows the 400 mm rule (2) | PASS |
| no stud pitch over 400 | PASS |
| fill bays = stud count + 1 (3) | PASS |
| skin is half_pw wide and the row high | PASS |
| top rail rivnuts follow the 220 rule [-881.74, -662.08, -442.41, -222.75] | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 147 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 210202_P01_WALL-PANEL-ASSY-BACK-LOWER-B2_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211202, 211402, 211602, 831001, 831002, 838003.

1. Reopen: timeline 182 items, 0 not healthy; sketches 53, 53 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm: rebuild 182 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 2 |
| stile_pitch | 392.997 | 359.663 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |
| close_gap | 5.5 | 5.5 |
| tube_w | 20 | 20 |
| el_inlet_x | 120 | 120 |
| el_inlet_z | 313 | 313 |
| el_lan_z | 375 | 375 |
| el_inlet_d | 24 | 24 |
| el_cut_z0 | 866 | 866 |
| el_cut_z1 | 1134 | 1134 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211202 / RAIL - BOTTOM | (2.75, 804.0, 112.26, 1201.74, 844.0, 132.26) | (2.75, 804.0, 112.26, 1101.74, 844.0, 132.26) |
| 211202 / RAIL - TOP | (2.75, 804.0, 1210.87, 1201.74, 844.0, 1230.87) | (2.75, 804.0, 1172.26, 1101.74, 844.0, 1192.26) |
| 211202 / STILE - CENTRE | (2.75, 804.0, 132.26, 22.75, 844.0, 1210.87) | (2.75, 804.0, 132.26, 22.75, 844.0, 1172.26) |
| 211202 / STILE - MID 1 | (395.75, 804.0, 132.26, 415.75, 844.0, 1210.87) | (362.41, 804.0, 132.26, 382.41, 844.0, 1172.26) |
| 211202 / STILE - MID 2 | (788.74, 804.0, 132.26, 808.74, 844.0, 1210.87) | (722.08, 804.0, 132.26, 742.08, 844.0, 1172.26) |
| 211202 / STILE - OUTER | (1181.74, 804.0, 132.26, 1201.74, 844.0, 1210.87) | (1081.74, 804.0, 132.26, 1101.74, 844.0, 1172.26) |
| 211402 / SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM | (1.13, 847.0, 112.26, 1201.74, 850.0, 1230.87) | (1.13, 847.0, 112.26, 1101.74, 850.0, 1192.26) |
| 211602 / FILL - BAY 1 | (22.75, 804.0, 132.26, 395.75, 844.0, 1210.87) | (22.75, 804.0, 132.26, 362.41, 844.0, 1172.26) |
| 211602 / FILL - BAY 2 | (415.75, 804.0, 132.26, 788.74, 844.0, 1210.87) | (382.41, 804.0, 132.26, 722.08, 844.0, 1172.26) |
| 211602 / FILL - BAY 3 | (808.74, 804.0, 132.26, 1181.74, 844.0, 1210.87) | (742.08, 804.0, 132.26, 1081.74, 844.0, 1172.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT HIGH X | (1097.74, 820.0, 1221.63, 1105.74, 828.0, 1238.87) | (997.74, 820.0, 1183.02, 1005.74, 828.0, 1200.26) |
| 831001 / SPIGOT - TOP RAIL SPIGOT LOW X | (98.75, 820.0, 1221.63, 106.75, 828.0, 1238.87) | (98.75, 820.0, 1183.02, 106.75, 828.0, 1200.26) |
| 831002 / STOP WASHER - TOP RAIL 1 | (212.75, 814.0, 1230.87, 232.75, 834.0, 1232.37) | (212.75, 814.0, 1192.26, 232.75, 834.0, 1193.76) |
| 831002 / STOP WASHER - TOP RAIL 2 | (465.75, 814.0, 1230.87, 485.75, 834.0, 1232.37) | (432.41, 814.0, 1192.26, 452.41, 834.0, 1193.76) |
| 831002 / STOP WASHER - TOP RAIL 3 | (718.74, 814.0, 1230.87, 738.74, 834.0, 1232.37) | (652.08, 814.0, 1192.26, 672.08, 834.0, 1193.76) |
| 831002 / STOP WASHER - TOP RAIL 4 | (971.74, 814.0, 1230.87, 991.74, 834.0, 1232.37) | (871.74, 814.0, 1192.26, 891.74, 834.0, 1193.76) |
| 838003 / RIVNUT - CENTRE STILE PIN 1 | (1.99, 817.52, 325.78, 12.91, 830.48, 338.74) | (1.99, 817.52, 325.78, 12.91, 830.48, 338.74) |
| 838003 / RIVNUT - CENTRE STILE PIN 2 | (1.99, 817.52, 665.09, 12.91, 830.48, 678.05) | (1.99, 817.52, 645.78, 12.91, 830.48, 658.74) |
| 838003 / RIVNUT - CENTRE STILE PIN 3 | (1.99, 817.52, 1004.39, 12.91, 830.48, 1017.35) | (1.99, 817.52, 965.78, 12.91, 830.48, 978.74) |
| 838003 / RIVNUT - TOP RAIL 1 | (216.27, 817.52, 1222.21, 229.23, 830.48, 1233.13) | (216.27, 817.52, 1183.6, 229.23, 830.48, 1194.52) |
| 838003 / RIVNUT - TOP RAIL 2 | (469.27, 817.52, 1222.21, 482.23, 830.48, 1233.13) | (435.93, 817.52, 1183.6, 448.89, 830.48, 1194.52) |
| 838003 / RIVNUT - TOP RAIL 3 | (722.26, 817.52, 1222.21, 735.22, 830.48, 1233.13) | (655.6, 817.52, 1183.6, 668.56, 830.48, 1194.52) |
| 838003 / RIVNUT - TOP RAIL 4 | (975.26, 817.52, 1222.21, 988.22, 830.48, 1233.13) | (875.26, 817.52, 1183.6, 888.22, 830.48, 1194.52) |
| 838003 / RIVNUT - TOP RAIL SPIGOT HIGH X | (1095.26, 817.52, 1220.71, 1108.22, 830.48, 1231.63) | (995.26, 817.52, 1182.1, 1008.22, 830.48, 1193.02) |
| 838003 / RIVNUT - TOP RAIL SPIGOT LOW X | (96.27, 817.52, 1220.71, 109.23, 830.48, 1231.63) | (96.27, 817.52, 1182.1, 109.23, 830.48, 1193.02) |

| Check | Result |
|---|---|
| frame width follows half_fw (1098.99) | PASS |
| frame stays close_gap / 2 from X 0 at the closing seam | PASS |
| frame's outer end stays one seam gap off the side frame (pod_w / 2 - 46 - 2.26) | PASS |
| stiles span the row height - 40 | PASS |
| stud count follows the 400 mm rule (2) | PASS |
| no stud pitch over 400 | PASS |
| fill bays = stud count + 1 (3) | PASS |
| skin is half_pw wide and the row high | PASS |
| top rail rivnuts follow the 220 rule [222.75, 442.41, 662.08, 881.74] | PASS |
| inlet and LAN 24 holes in the skin at X 120 | PASS |
| the unit's fill cut-out runs to the first stud (X 362.41), fill below it | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 182 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211101, 212101, 212102, 212103, 212104, 212105, 831007, 831008.

1. Reopen: timeline 136 items, 0 not healthy; sketches 34, 34 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 136 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 300 | 300 |
| frm_len | 1486.74 | 1291.74 |
| stile_n_mid | 5 | 5 |
| stud_c1 | 270 | 270 |
| stud_c2 | 520.913 | 455.913 |
| stud_c3 | 746.37 | 648.87 |
| stud_c4 | 971.827 | 841.827 |
| stud_c5 | 1222.74 | 1027.74 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1120 |
| lin_front_dy | 0 | 0 |
| top_h | 20 | 20 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212101 WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH:1 / RAIL - BOTTOM | (-1244.0, -641.33, 112.26, -1204.0, 841.76, 132.26) | (-1244.0, -446.33, 112.26, -1204.0, 841.76, 132.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212102 WALL - FRAME RAIL TOP - SIDE LOWER - LH:1 / RAIL - TOP | (-1244.0, -641.33, 1235.0, -1204.0, 841.76, 1255.0) | (-1244.0, -446.33, 1212.26, -1204.0, 841.76, 1232.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212103 WALL - FRAME STILE FRONT - SIDE LOWER - LH:1 / STILE - FRONT | (-1244.0, -642.74, 113.67, -1204.0, -622.74, 1253.59) | (-1244.0, -447.74, 113.67, -1204.0, -427.74, 1230.85) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212104 WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH:1 / STILE - BACK | (-1244.0, 804.0, 113.38, -1204.0, 844.0, 1253.88) | (-1244.0, 804.0, 113.38, -1204.0, 844.0, 1231.14) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:1 / STILE - MID | (-1244.0, -382.74, 132.26, -1204.0, -362.74, 1235.0) | (-1244.0, -187.74, 132.26, -1204.0, -167.74, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:2 / STILE - MID | (-1244.0, -131.83, 132.26, -1204.0, -111.83, 1235.0) | (-1244.0, -1.83, 132.26, -1204.0, 18.17, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:3 / STILE - MID | (-1244.0, 93.63, 132.26, -1204.0, 113.63, 1235.0) | (-1244.0, 191.13, 132.26, -1204.0, 211.13, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:4 / STILE - MID | (-1244.0, 319.09, 132.26, -1204.0, 339.09, 1235.0) | (-1244.0, 384.09, 132.26, -1204.0, 404.09, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+212105 WALL - FRAME STILE MID - SIDE LOWER - LH:5 / STILE - MID | (-1244.0, 570.0, 132.26, -1204.0, 590.0, 1235.0) | (-1244.0, 570.0, 132.26, -1204.0, 590.0, 1212.26) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831007 HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL:1 / MITRE PLATE | (-1244.0, -642.21, 112.79, -1204.0, -622.06, 132.94) | (-1244.0, -447.21, 112.79, -1204.0, -427.06, 132.94) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831007 HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL:2 / MITRE PLATE | (-1244.0, -642.21, 1234.32, -1204.0, -622.06, 1254.47) | (-1244.0, -447.21, 1211.58, -1204.0, -427.06, 1231.73) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831008 HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL:1 / MITRE PLATE | (-1244.0, 803.62, 112.77, -1204.0, 841.63, 133.12) | (-1244.0, 803.62, 112.77, -1204.0, 841.63, 133.12) |
| 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1+831008 HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL:2 / MITRE PLATE | (-1244.0, 803.62, 1234.14, -1204.0, 841.63, 1254.49) | (-1244.0, 803.62, 1211.4, -1204.0, 841.63, 1231.75) |

| Check | Result |
|---|---|
| rails run wall_depth - 2.26 - 6 (the back return and its bond line) less their plate cut-backs | PASS |
| rails start one cut-back behind the frame's front end (2.26 behind the decor back plate) | PASS |
| perimeter stiles span the panel height less their plate cut-backs | PASS |
| studs span the panel height - 20 - top_h | PASS |
| 5 studs, set from the bolts | PASS |
| every clear bay 275 or less (the skin's 2 mm limit) [240.0, 165.9, 173.0, 173.0, 165.9, 214.0] | PASS |
| every bolt 30 or more clear of every stud (R-J14) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 136 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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

## Edit test: 211201_P01_WALL-PANEL-FRAME-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211201.

1. Reopen: timeline 74 items, 0 not healthy; sketches 22, 22 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm, stile_pitch_max -> 300 mm: rebuild 74 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 3 |
| stile_pitch | 392.997 | 269.748 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211201 / RAIL - BOTTOM | (-1201.74, 804.0, 112.26, -2.75, 844.0, 132.26) | (-1101.74, 804.0, 112.26, -2.75, 844.0, 132.26) |
| 211201 / RAIL - TOP | (-1201.74, 804.0, 1210.87, -2.75, 844.0, 1230.87) | (-1101.74, 804.0, 1172.26, -2.75, 844.0, 1192.26) |
| 211201 / STILE - CENTRE | (-22.75, 804.0, 132.26, -2.75, 844.0, 1210.87) | (-22.75, 804.0, 132.26, -2.75, 844.0, 1172.26) |
| 211201 / STILE - MID 1 | (-808.74, 804.0, 132.26, -788.74, 844.0, 1210.87) | (-831.99, 804.0, 132.26, -811.99, 844.0, 1172.26) |
| 211201 / STILE - MID 1 (1) | - | (-292.5, 804.0, 132.26, -272.5, 844.0, 1172.26) |
| 211201 / STILE - MID 2 | (-415.75, 804.0, 132.26, -395.75, 844.0, 1210.87) | (-562.25, 804.0, 132.26, -542.25, 844.0, 1172.26) |
| 211201 / STILE - OUTER | (-1201.74, 804.0, 132.26, -1181.74, 844.0, 1210.87) | (-1101.74, 804.0, 132.26, -1081.74, 844.0, 1172.26) |

| Check | Result |
|---|---|
| frame width follows half_fw (1098.99) | PASS |
| frame stays close_gap / 2 from X 0 at the closing seam | PASS |
| frame's outer end stays one seam gap off the side frame (pod_w / 2 - 46 - 2.26) | PASS |
| stiles span the row height - 40 | PASS |
| stud count follows the 300 mm rule (3) | PASS |
| no stud pitch over 300 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 74 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211301_P01_WALL-SKIN-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211301.

1. Reopen: timeline 9 items, 0 not healthy; sketches 2, 2 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 9 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 300 | 300 |
| frm_len | 1486.74 | 1291.74 |
| stile_n_mid | 5 | 5 |
| stud_c1 | 270 | 270 |
| stud_c2 | 520.913 | 455.913 |
| stud_c3 | 746.37 | 648.87 |
| stud_c4 | 971.827 | 841.827 |
| stud_c5 | 1222.74 | 1027.74 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1120 |
| lin_front_dy | 0 | 0 |
| top_h | 20 | 20 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211301 WALL - SKIN - SIDE LOWER - LH:1 / SKIN - ACP 3 WITH BACK RETURN | (-1250.0, -642.74, 112.26, -1204.0, 850.0, 1255.0) | (-1250.0, -447.74, 112.26, -1204.0, 850.0, 1232.26) |

| Check | Result |
|---|---|
| skin runs wall_depth - 2.26 and the panel height | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 9 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 211401_P01_WALL-SKIN-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211401.

1. Reopen: timeline 5 items, 0 not healthy; sketches 1, 1 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm, stile_pitch_max -> 300 mm: rebuild 5 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 3 |
| stile_pitch | 392.997 | 269.748 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211401 / SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM | (-1201.74, 847.0, 112.26, -1.13, 850.0, 1230.87) | (-1101.74, 847.0, 112.26, -1.13, 850.0, 1192.26) |

| Check | Result |
|---|---|
| skin is half_pw wide and the row high | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 5 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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

## Edit test: 211601_P01_WALL-CAVITY-FILL-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 211601.

1. Reopen: timeline 27 items, 0 not healthy; sketches 8, 8 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm: rebuild 27 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 400 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 2 |
| stile_pitch | 392.997 | 359.663 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 211601 / FILL - BAY 1 | (-1181.74, 804.0, 132.26, -808.74, 844.0, 1210.87) | (-1081.74, 804.0, 132.26, -742.08, 844.0, 1172.26) |
| 211601 / FILL - BAY 2 | (-788.74, 804.0, 132.26, -415.75, 844.0, 1210.87) | (-722.08, 804.0, 132.26, -382.41, 844.0, 1172.26) |
| 211601 / FILL - BAY 3 | (-395.75, 804.0, 132.26, -22.75, 844.0, 1210.87) | (-362.41, 804.0, 132.26, -22.75, 844.0, 1172.26) |

| Check | Result |
|---|---|
| fill bays = stud count + 1 (3) | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 27 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511101, 511301, NO-PN-HOLD-H03.

1. Reopen: timeline 24 items, 0 not healthy; sketches 6, 6 fully constrained; parametric.
2. Edit wall_depth -> 1300 mm, side_h -> 1120 mm: rebuild 24 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| wall_depth | 1495 | 1300 |
| side_h | 1142.74 | 1120 |
| stile_pitch_max | 300 | 300 |
| frm_len | 1489.74 | 1294.74 |
| stile_n_mid | 5 | 5 |
| stud_c1 | 270 | 270 |
| stud_c2 | 520.913 | 455.913 |
| stud_c3 | 746.37 | 648.87 |
| stud_c4 | 971.827 | 841.827 |
| stud_c5 | 1222.74 | 1027.74 |
| cass_len | 1445 | 1250 |
| cass_h | 1142.74 | 1120 |
| lin_front_dy | 0 | 0 |
| top_h | 20 | 20 |
| pod_h | 2400 | 2400 |
| panel_z0 | 112.26 | 112.26 |
| seam_gap | 2.26 | 2.26 |
| outer_t | 46 | 46 |
| lin_gap | 4 | 4 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511101 LINING - TRAY - SIDE LOWER - LH:1 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1200.0, -645.0, 112.26, -1166.0, 800.0, 1255.0) | (-1200.0, -450.0, 112.26, -1166.0, 800.0, 1232.26) |
| 511301 LINING - FELT - SIDE LOWER - LH:1 / FELT - PET 9 HELD BY THE TRAY LIPS | (-1175.5, -643.5, 113.76, -1166.5, 798.5, 1253.5) | (-1175.5, -448.5, 113.76, -1166.5, 798.5, 1230.76) |
| NO-PN-HOLD-H03 HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED):1 / HOLD - CLIP ZONE 1 (BOTTOM FRONT) | (-1204.0, -382.74, 182.26, -1200.0, -362.74, 242.26) | (-1204.0, -187.74, 182.26, -1200.0, -167.74, 242.26) |
| NO-PN-HOLD-H03 HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED):1 / HOLD - CLIP ZONE 2 (BOTTOM BACK) | (-1204.0, 570.0, 182.26, -1200.0, 590.0, 242.26) | (-1204.0, 570.0, 182.26, -1200.0, 590.0, 242.26) |
| NO-PN-HOLD-H03 HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED):1 / HOLD - CLIP ZONE 3 (TOP FRONT) | (-1204.0, -382.74, 1125.0, -1200.0, -362.74, 1185.0) | (-1204.0, -187.74, 1102.26, -1200.0, -167.74, 1162.26) |
| NO-PN-HOLD-H03 HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED):1 / HOLD - CLIP ZONE 4 (TOP BACK) | (-1204.0, 570.0, 1125.0, -1200.0, 590.0, 1185.0) | (-1204.0, 570.0, 1102.26, -1200.0, 590.0, 1162.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray starts lin_front_dy behind the decor back plate (R: 5, clear of DR's panel) | PASS |
| tray height follows the row (cass_h) | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| clip zones sit on the first and last stud | PASS |
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

## Edit test: 510201_P01_LINING-CASSETTE-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511201, 511401, NO-PN-HOLD-H03.

1. Reopen: timeline 24 items, 0 not healthy; sketches 6, 6 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm, stile_pitch_max -> 300 mm: rebuild 24 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 3 |
| stile_pitch | 392.997 | 269.748 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511201 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1166.0, 766.0, 112.26, -1.13, 800.0, 1230.87) | (-1066.0, 766.0, 112.26, -1.13, 800.0, 1192.26) |
| 511401 / FELT - PET 9 HELD BY THE TRAY LIPS | (-1164.5, 766.5, 113.76, -2.63, 775.5, 1229.37) | (-1064.5, 766.5, 113.76, -2.63, 775.5, 1190.76) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM LOW X) | (-808.74, 800.0, 182.26, -788.74, 804.0, 242.26) | (-831.99, 800.0, 182.26, -811.99, 804.0, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM HIGH X) | (-415.75, 800.0, 182.26, -395.75, 804.0, 242.26) | (-562.25, 800.0, 182.26, -542.25, 804.0, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP LOW X) | (-808.74, 800.0, 1100.87, -788.74, 804.0, 1160.87) | (-831.99, 800.0, 1062.26, -811.99, 804.0, 1122.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP HIGH X) | (-415.75, 800.0, 1100.87, -395.75, 804.0, 1160.87) | (-562.25, 800.0, 1062.26, -542.25, 804.0, 1122.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray height follows cass_h | PASS |
| tray stops seam_gap / 2 short of X 0 | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 24 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

## Edit test: 510202_P01_LINING-CASSETTE-BACK-LOWER-B2_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511202, 511402, NO-PN-HOLD-H03.

1. Reopen: timeline 36 items, 0 not healthy; sketches 10, 10 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm, stile_pitch_max -> 300 mm: rebuild 36 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 3 |
| stile_pitch | 392.997 | 269.748 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |
| panel_z0 | 112.26 | 112.26 |
| tray_t | 0.5 | 0.5 |
| el_lt_x | 346 | 346 |
| el_y_bg | 787.5 | 787.5 |
| el_grm_d | 19.1 | 19.1 |
| el_cut_x0 | 91 | 91 |
| el_cut_x1 | 395 | 395 |
| el_cut_z0 | 866 | 866 |
| el_cut_z1 | 1134 | 1134 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511202 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (1.13, 766.0, 112.26, 1166.0, 800.0, 1230.87) | (1.13, 766.0, 112.26, 1066.0, 800.0, 1192.26) |
| 511402 / FELT - PET 9 HELD BY THE TRAY LIPS | (2.63, 766.5, 113.76, 1164.5, 775.5, 1229.37) | (2.63, 766.5, 113.76, 1064.5, 775.5, 1190.76) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 1 (BOTTOM LOW X) | (395.75, 800.0, 182.26, 415.75, 804.0, 242.26) | (272.5, 800.0, 182.26, 292.5, 804.0, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 2 (BOTTOM HIGH X) | (788.74, 800.0, 182.26, 808.74, 804.0, 242.26) | (542.25, 800.0, 182.26, 562.25, 804.0, 242.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 3 (TOP LOW X) | (395.75, 800.0, 1100.87, 415.75, 804.0, 1160.87) | (272.5, 800.0, 1062.26, 292.5, 804.0, 1122.26) |
| NO-PN-HOLD-H03 / HOLD - CLIP ZONE 4 (TOP HIGH X) | (788.74, 800.0, 1100.87, 808.74, 804.0, 1160.87) | (542.25, 800.0, 1062.26, 562.25, 804.0, 1122.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray height follows cass_h | PASS |
| tray stops seam_gap / 2 short of X 0 | PASS |
| felt follows the tray, 1 mm clear inside the 0.5 returns | PASS |
| G-B2-B4 19.1 hole in the top return follows the row top (Z 1192.26) | PASS |
| plain power unit cut-out at X 91 to 395 through the tray base and the felt | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 36 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

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

## Edit test: 511201_P01_LINING-TRAY-BACK-LOWER-B1_CAD.f3d

Copy opened as a new, unsaved document and closed without saving. Components: 511201.

1. Reopen: timeline 7 items, 0 not healthy; sketches 1, 1 fully constrained; parametric.
2. Edit pod_w -> 2300 mm, half_pw -> 1100.61 mm, half_fw -> 1098.99 mm, back_ph -> 1080 mm, stile_pitch_max -> 300 mm: rebuild 7 items, 0 not healthy, 0 sketches not fully constrained.

| Parameter | Before | After |
|---|---|---|
| pod_w | 2500 | 2300 |
| half_pw | 1200.61 | 1100.61 |
| half_fw | 1198.99 | 1098.99 |
| back_ph | 1118.61 | 1080 |
| stile_pitch_max | 400 | 300 |
| frm_len | 1198.99 | 1098.99 |
| stile_n_mid | 2 | 3 |
| stile_pitch | 392.997 | 269.748 |
| cass_len | 1164.87 | 1064.87 |
| cass_h | 1118.61 | 1080 |
| pnl_h | 1118.61 | 1080 |

3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):

| Body | Before | After |
|---|---|---|
| 511201 / TRAY - STEEL 0.5 WITH RETURNS AND LIPS | (-1166.0, 766.0, 112.26, -1.13, 800.0, 1230.87) | (-1066.0, 766.0, 112.26, -1.13, 800.0, 1192.26) |

| Check | Result |
|---|---|
| tray runs cass_len | PASS |
| tray height follows cass_h | PASS |
| tray stops seam_gap / 2 short of X 0 | PASS |
| revert: every body back to its before box, healthy | PASS |

4. Revert: 7 items, 0 not healthy, 0 sketches not fully constrained; bodies back to before: True.

