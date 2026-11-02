# Edit test record: 610000 AIR P01 (guideline §4.4)

Run 2026-11-01 16:10:42 to 16:11:32 UTC on Mac 1, Fusion 2706.1.17, through the Fusion lock, in the held session right
after the rebuild (`BUILD-RECORD.md`), from commit 3a1b82f:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/edit_test_air.py`

On a copy, on skeleton P04 v4: the script opens `610000_P01_AIR_CAD.f3d` (the export of the saved build, written by the
same run that saved it) as a new document, makes each change of `air_model.EDITS`, rebuilds, and checks the 58 layout
units (each copy, each joined stud and lock screw) against the boxes `air_model.layout()` gives for the new values; then
it reverts, checks again and closes the copy without saving. It names any timeline item that isn't healthy. `pod_d` and
`wall_depth` change together, since the side walls start at DR's back, which places the soffit's and the column's door
side (FRONT's `dr_acc_face_y`); `dr_acc_t` is FRONT's panel thickness; `col_x0` and `hub_z` are AIR's own.
`test_air_offline.py` checks beforehand that every cut and hole lands in its body for each change, the transitions' 24
rivet holes and the riser's chamfer among them.

| Step | Change | Bodies checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|
| before | none | 58 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 58 | 0.0 | none | 0 |
| revert | pod_w back | 58 | 0.0 | none | 0 |
| edit | pod_d 1700 mm -> 1725 mm, wall_depth 1495 mm -> 1520 mm | 58 | 0.0 | none | 0 |
| revert | pod_d, wall_depth back | 58 | 0.0 | none | 0 |
| edit | dt_zb 2137 mm - fr_dz -> 2100 mm | 58 | 0.0 | none | 0 |
| revert | dt_zb back | 58 | 0.0 | none | 0 |
| edit | dr_acc_t 3 mm -> 4 mm | 58 | 0.0 | none | 0 |
| revert | dr_acc_t back | 58 | 0.0 | none | 0 |
| edit | col_x0 949 mm -> 940 mm | 58 | 0.0 | none | 0 |
| revert | col_x0 back | 58 | 0.0 | none | 0 |
| edit | hub_z 1200 mm -> 1250 mm | 58 | 0.0 | none | 0 |
| revert | hub_z back | 58 | 0.0 | none | 0 |

**EDIT TEST: PASS.** Every unit follows each change and no timeline item turns unhealthy: the riser's chamfer, the
transitions' 24 rivet holes in the riser and the supply box casing, and the cuts and holes from before all rebuild with
each change. The tolerance is 0.05 mm.

What the test does not cover:
- The number of hinges and latches per section and the stud and lock positions are set when the design is built.
- The HOLD envelopes (transitions, hinges, latches) follow by position only.
- FRONT's named values (DR's panel face and its opening into the column) are read from FRONT's DR model when the build
  runs, so a change there needs AIR's rebuild, not an edit.
