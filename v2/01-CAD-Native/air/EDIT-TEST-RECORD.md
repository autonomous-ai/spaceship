# Edit test record: 610000 AIR P01 (guideline §4.4)

Run 2026-11-01 02:07 UTC on Mac 1, Fusion 2706.1.17, through the Fusion lock, in the held session after the build:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/edit_test_air.py --label "CEILING Engineer"`

On a copy, on skeleton P04 v4: the script opens `610000_P01_AIR_CAD.f3d` (the export of the saved build) as a new document, makes each change of `air_model.EDITS`, rebuilds, and checks the 53 layout bodies against the boxes `air_model.layout()` gives for the new values; then it reverts, checks again and closes the copy without saving. It names any timeline item that isn't healthy. `pod_d` and `wall_depth` change together, since the side walls start at DR's back, which now places the soffit's and the column's door side (FRONT's `dr_acc_face_y`); `dr_acc_t` is FRONT's panel thickness; `col_x0` and `hub_z` are AIR's own. `test_air_offline.py` checks beforehand that every cut and hole lands in its body for each change (the old latch cut that missed the fill at pod_w 2600 is the case it catches).

| Step | Change | Bodies checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|
| before | none | 53 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 53 | 0.0 | none | 0 |
| revert | pod_w back | 53 | 0.0 | none | 0 |
| edit | pod_d 1700 mm -> 1725 mm, wall_depth 1495 mm -> 1520 mm | 53 | 0.0 | none | 0 |
| revert | pod_d, wall_depth back | 53 | 0.0 | none | 0 |
| edit | dt_zb 2137 mm - fr_dz -> 2100 mm | 53 | 0.0 | none | 0 |
| revert | dt_zb back | 53 | 0.0 | none | 0 |
| edit | dr_acc_t 3 mm -> 4 mm | 53 | 0.0 | none | 0 |
| revert | dr_acc_t back | 53 | 0.0 | none | 0 |
| edit | col_x0 949 mm -> 940 mm | 53 | 0.0 | none | 0 |
| revert | col_x0 back | 53 | 0.0 | none | 0 |
| edit | hub_z 1200 mm -> 1250 mm | 53 | 0.0 | none | 0 |
| revert | hub_z back | 53 | 0.0 | none | 0 |

**EDIT TEST: PASS.** Every body follows each change; no timeline item turns unhealthy (the pod_w 2600 failure of the earlier build, a latch's cut in the soffit fill, is gone: the fill stops short of the latch line). The tolerance is 0.05 mm.

What the test does not cover:
- The number of hinges and latches per section and the stud and lock positions are set when the design is built.
- The HOLD envelopes (hub zone, transitions, hinges, latches) follow by position only.
