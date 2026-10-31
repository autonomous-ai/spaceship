# Edit test record: FRONT

Engineering guideline section 4.4. Each test opens the exported .f3d as a new unsaved copy, changes skeleton parameters, checks every anchor in the anchors file (a body side against the parameter expression it must follow), puts the values back, checks again and closes the copy without saving. The saved design is never touched.

## 360001 FRONT - DOOR UNIT, P01

In the same Fusion run as the build (`--arg step=all`, `--arg edits=...`), on a copy of the exported f3d opened as a new unsaved document and closed without saving, skeleton P04 v4:

| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |
|---|---|---|---|---|---|
| Before | 1348.1 x 148.8 x 2095.5 | 0 | 0 | none | 0.020 |
| pod_w 2600 mm; fr_dz 12 mm; door_xbr 1474 mm | 1358.1 x 148.8 x 2100.5 | 0 | 0 | none | 0.020 |
| Reverted | 1348.1 x 148.8 x 2095.5 | 0 | 0 | none | 0.020 |

RESULT: PASS. 31 anchors (leaf, kick strip, seals, hinge, strike and pull spaces against their expressions) follow the three skeleton edits at once and return exactly. An earlier run of this test caught a real fault (a dimension that flipped side across the centre line); every FRONT sketch now measures from a far reference point.
