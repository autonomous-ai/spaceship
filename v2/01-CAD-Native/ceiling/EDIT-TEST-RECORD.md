# Edit test record: 410000 CEILING P01 (guideline §4.4)

Run 2026-11-01 on Mac 1, Fusion 2706.1.17, through the Fusion lock, in two runs of one held session:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py --arg edits=0,1,2 --label "CEILING Engineer"`, then the same with `--arg edits=3,4`.

On a copy, on skeleton P04 v4: the script opens `410000_P01_CEILING_CAD.f3d` (the export of the saved cloud version 8, with the 19.1 mm cable holes) as a new document, changes one parameter at a time (the last step two at once), rebuilds, and checks every body in the root context against the box the layout (`ceiling_model.py`) gives for the new values: the 14 frame members, both skins, and in both cassettes the tray, felt, 2 ribs, 3 fill strips, 6 clip spaces and 2 catch spaces (46 bodies). It also checks the 48 joint holes in the frames against the positions the joints register gives for the new values (`ceiling_checks.hole_check`). Then it reverts, checks again and closes the copy without saving. `pod_w`, `wall_depth`, `ceil_side_pitch` and `ceil_back_pitch` are skeleton parameters; `cs_front` is the D-60 soffit depth; `bolt_edge_inset` is the register's first-bolt distance from each panel's edge.

| Step | Change | Bodies checked | Joint holes checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|---|
| before | none | 46 | 48 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 46 | 48 | 0.0 | none | 0 |
| revert | pod_w back | 46 | 48 | 0.0 | none | 0 |
| edit | wall_depth 1495 mm -> 1520 mm | 46 | 48 | 0.0 | none | 0 |
| revert | wall_depth back | 46 | 48 | 0.0 | none | 0 |
| edit | cs_front 360 mm -> 330 mm | 46 | 48 | 0.0 | none | 0 |
| revert | cs_front back | 46 | 48 | 0.0 | none | 0 |
| before | none | 46 | 48 | 0.0 | none | 0 |
| edit | bolt_edge_inset 220 mm -> 250 mm | 46 | 48 | 0.0 | none | 0 |
| revert | bolt_edge_inset back | 46 | 48 | 0.0 | none | 0 |
| edit | ceil_side_pitch (from the register's rule) -> 340 mm, ceil_back_pitch (from the rule) -> 240 mm | 46 | 48 | 0.0 | none | 0 |
| revert | ceil_side_pitch, ceil_back_pitch back | 46 | 48 | 0.0 | none | 0 |

**EDIT TEST: PASS** (both runs). The frames with all their joint holes, the skins and both cassettes follow each change, including the sheet-metal tray (base flange, returns, lips and cable holes), the ribs, the fill strips with their notches, and the clip and catch spaces placed by joints. The tolerance is 0.05 mm.

What the test does not cover:
- Which fill bays get a strip is set when the design is built (a bay mostly over the soffit gets none). A soffit change large enough to open or close a bay needs a rebuild from the script, not an edit.
- The number of bolts on an edge (`n_ceil_side_bolt`, `n_ceil_back_bolt`) is set when the design is built, as each hole is its own sketch and cut; a change of count needs a rebuild.
- The sheet metal rule holds the tray thickness as a value (Fusion's rules don't take user parameters), so changing `tray_t` also needs a rebuild.
