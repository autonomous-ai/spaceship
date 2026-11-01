# Edit test record: FRONT

Engineering guideline section 4.4. Each test opens the exported .f3d as a new unsaved copy, changes skeleton parameters, checks every anchor in the anchors file (a body side against the parameter expression it must follow), puts the values back, checks again and closes the copy without saving. The saved design is never touched.

## 360001 FRONT - DOOR UNIT, P01

Rerun 2026-11-01 10:27 UTC after the D-150 rebuild (the brush seal 368008 on the kick strip's end, from the floor to Z 105), same method:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1350.5 x 148.8 x 2115.5 | 0 | 0 | none | 0.020 |
| pod_w 2600 mm; fr_dz 12 mm; door_xbr 1474 mm | 1360.5 x 148.8 x 2120.5 | 0 | 0 | none | 0.020 |
| Reverted | 1350.5 x 148.8 x 2115.5 | 0 | 0 | none | 0.020 |

RESULT: PASS, 37 anchors (the brush's six among them).

Rerun 2026-11-01 05:59 UTC after the D-132 rebuild (the kick strip on the band's bottom line, its 60° push-side taper, the pull in the US band), same method:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1348.1 x 148.8 x 2105.5 | 0 | 0 | none | 0.020 |
| pod_w 2600 mm; fr_dz 12 mm; door_xbr 1474 mm | 1358.1 x 148.8 x 2110.5 | 0 | 0 | none | 0.020 |
| Reverted | 1348.1 x 148.8 x 2105.5 | 0 | 0 | none | 0.020 |

RESULT: PASS, 31 anchors.

Earlier run (before D-132):

In the same Fusion run as the build (`--arg step=all`, `--arg edits=...`), on a copy of the exported f3d opened as a new unsaved document and closed without saving, skeleton P04 v4:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1348.1 x 148.8 x 2095.5 | 0 | 0 | none | 0.020 |
| pod_w 2600 mm; fr_dz 12 mm; door_xbr 1474 mm | 1358.1 x 148.8 x 2100.5 | 0 | 0 | none | 0.020 |
| Reverted | 1348.1 x 148.8 x 2095.5 | 0 | 0 | none | 0.020 |

RESULT: PASS. 31 anchors (leaf, kick strip, seals, hinge, strike and pull spaces against their expressions) follow the three skeleton edits at once and return exactly. An earlier run of this test caught a real fault (a dimension that flipped side across the centre line); every FRONT sketch now measures from a far reference point.

## 360002 FRONT - FIXED GLASS UNIT, P01

In the same Fusion run as the build (`--arg step=all`, `--arg edits=...`), on a copy of the exported f3d opened as a new unsaved document and closed without saving, skeleton P04 v4:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1030.8 x 15.0 x 2040.0 | 0 | 0 | none | 0.010 |
| pod_w 2600 mm; fr_dz 12 mm; fix_xk 511 mm; door_xtr 1192 mm | 1121.5 x 15.0 x 2045.0 | 0 | 0 | none | 0.010 |
| Reverted | 1030.8 x 15.0 x 2040.0 | 0 | 0 | none | 0.010 |

RESULT: PASS. 16 anchors (pane, U-profile, U-seal and seal half sides against their expressions) follow the four skeleton edits at once, with the bottom channel's screw holes in the model, and return exactly.

## 350003 FRONT - DECOR BLOCK ASSY - DR, P01 stage 2

In the same Fusion run as the build, on a copy of the exported f3d opened as a new unsaved document and closed without saving, skeleton P04 v4:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1020.0 x 215.0 x 2290.1 | 0 | 0 | none | 0.020 |
| decor_d 215 mm; fix_xk 511 mm; fix_zk 1531 mm | 1020.0 x 225.0 x 2290.1 | 0 | 0 | none | 0.020 |
| Reverted | 1020.0 x 215.0 x 2290.1 | 0 | 0 | none | 0.020 |

RESULT: PASS. 28 anchors (skin, frame tubes, plates, panels and air parts against their expressions) follow the three skeleton edits at once, with the tube frame in the model, and return exactly.

## 350002 FRONT - DECOR BLOCK ASSY - DT, P01 stage 2

Same method and run as its build:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1699.0 x 205.0 x 306.0 | 0 | 0 | none | 0.020 |
| decor_d 215 mm; dt_xr 1690 mm; dl_w 283 mm | 1690.0 x 215.0 x 306.0 | 0 | 0 | none | 0.020 |
| Reverted | 1699.0 x 205.0 x 306.0 | 0 | 0 | none | 0.020 |

RESULT: PASS. 15 anchors follow the three skeleton edits at once and return exactly.

## 350001 FRONT - DECOR BLOCK ASSY - DL, P01 stage 2

Same method and run as its build:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 304.0 x 199.0 x 2292.0 | 0 | 0 | none | 0.020 |
| decor_d 215 mm; dl_w 283 mm; dl_y3 848 mm | 304.0 x 213.0 x 2292.0 | 0 | 0 | none | 0.020 |
| Reverted | 304.0 x 199.0 x 2292.0 | 0 | 0 | none | 0.020 |

RESULT: PASS. 15 anchors follow the three skeleton edits at once and return exactly.

## 350001 DL, 350002 DT, 350003 DR: final builds for #105 (2026-11-01)

Same method, in the same run as each build:

| Block | Edits | Before (box mm) | After the edits | Reverted | Anchors off | Result |
|---|---|---|---|---|---|---|
| DR | decor_d 215; fix_xk 511; fix_zk 1531 | 1020.0 x 215.5 x 2290.1 | 1020.0 x 225.5 x 2290.1 | 1020.0 x 215.5 x 2290.1 | none (worst 0.020) | PASS, 28 anchors |
| DT | decor_d 215; dt_xr 1690; dl_w 283 | 1699.0 x 202.8 x 306.0 | 1690.0 x 212.8 x 306.0 | 1699.0 x 202.8 x 306.0 | none (worst 0.020) | PASS, 17 anchors |
| DL | decor_d 215; dl_w 283; dl_y3 848 | 308.0 x 199.0 x 2292.0 | 313.0 x 213.0 x 2292.0 | 308.0 x 199.0 x 2292.0 | none (worst 0.020) | PASS, 15 anchors |

0 unhealthy items and 0 loose sketches in every state.
