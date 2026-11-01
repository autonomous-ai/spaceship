# Edit test record: 410000 CEILING P01 (guideline §4.4)

Run 2026-11-01 16:20:13 to 16:20:44 UTC on Mac 1, Fusion 2706.1.17, through the Fusion lock, in two runs of the held session that built version 12, from commit d4aa018:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py --arg edits=0,1,2 --label "CEILING Engineer"`, then the same with `--arg edits=3,4`.

On a copy, on skeleton P04 v4: the script opens `410000_P01_CEILING_CAD.f3d` (the export of the saved cloud version 12, written by the run that saved it: D-131's welded steel frames with D-163's Ø10.00 rivnut holes and DT's four bolt holes, the rib's real folds) as a new document, changes one parameter at a time (the last step two at once), rebuilds, and checks every body in the root context against the box the layout (`ceiling_model.py`) gives for the new values: the 14 frame members, the 8 mitre plates, both skins, and in both cassettes the tray, felt, 2 ribs, 3 fill strips, 6 clip spaces and 2 catch spaces (54 bodies). It also checks the 58 joint hole faces in the frames, DT's bolt holes among them, against the positions the joints register gives for the new values (`ceiling_checks.hole_check`). Then it reverts, checks again and closes the copy without saving. `pod_w`, `wall_depth`, `ceil_side_pitch` and `ceil_back_pitch` are skeleton parameters; `cs_front` is the D-60 soffit depth; `bolt_edge_inset` is the register's first-bolt distance from each panel's edge (DT's pitch follows it too).

| Step | Change | Bodies checked | Joint holes checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|---|
| before | none | 54 | 58 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 54 | 58 | 0.0 | none | 0 |
| revert | pod_w back | 54 | 58 | 0.0 | none | 0 |
| edit | wall_depth 1495 mm -> 1520 mm | 54 | 58 | 0.0 | none | 0 |
| revert | wall_depth back | 54 | 58 | 0.0 | none | 0 |
| edit | cs_front 360 mm -> 330 mm | 54 | 58 | 0.0 | none | 0 |
| revert | cs_front back | 54 | 58 | 0.0 | none | 0 |
| edit | bolt_edge_inset 220 mm -> 250 mm | 54 | 58 | 0.0 | none | 0 |
| revert | bolt_edge_inset back | 54 | 58 | 0.0 | none | 0 |
| edit | ceil_side_pitch ( wall_depth - 2 * bolt_edge_inset ) / ( n_ceil_side_bolt - 1 ) -> 340 mm, ceil_back_pitch ( half_fw - 2 * bolt_edge_inset ) / ( n_ceil_back_bolt - 1 ) -> 240 mm | 54 | 58 | 0.0 | none | 0 |
| revert | ceil_side_pitch, ceil_back_pitch back | 54 | 58 | 0.0 | none | 0 |

**EDIT TEST: PASS** (both runs). The 54 bodies are the 14 frame members, the 8 mitre plates, the 2 skins and both cassettes' parts; the 58 hole faces are the 56 joint holes (DT's 8 among them) and the two spigot slots' end arcs. The frames with all their joint holes, the turned copies, the mitre plates, the skins and both cassettes follow each change, including the sheet-metal tray (base flange, returns, lips and cable holes), the ribs with their folds, the fill strips with their notches, and the clip and catch spaces placed by joints. The tolerance is 0.05 mm.

What the test does not cover:
- Which fill bays get a strip is set when the design is built (a bay mostly over the soffit gets none). A soffit change large enough to open or close a bay needs a rebuild from the script, not an edit.
- The number of bolts on an edge (`n_ceil_side_bolt`, `n_ceil_back_bolt`) is set when the design is built, as each hole is its own sketch and cut; a change of count needs a rebuild.
- The sheet metal rule holds the tray thickness as a value (Fusion's rules don't take user parameters), so changing `tray_t` also needs a rebuild.

## STEP re-read

In the same held session (16:20:48 UTC), `python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/step_reimport_check.py` imported `v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step` (version 12's export) into a new design and closed it unsaved: 54 bodies, box X −1201.76…1201.77, Y −645.03…850.03, Z 2315.98…2400.03 against the layout's −1201.74…1201.74, −645…850, 2316…2400: **MATCH** (largest difference 0.030 mm).
