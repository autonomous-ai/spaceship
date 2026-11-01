# Edit test record: 810000 INTERIOR P01

Run 2026-11-01 07:35 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock, in the same held session as the
rebuild (`BUILD-RECORD.md`), on the saved design, closed without saving:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/edit_test_interior.py`. Each change is made alone, every
body is checked against the box the layout gives for the new values, then the change is reverted and checked again.
(The first build's edit test, 2026-10-31 20:52 UTC, passed the same way with 9 bodies; the D-126 rebuild's, 2026-11-01
05:52 UTC, with 8; this one checks the ledge and the rail at their new place, 5 mm off the lining.)

| Step | Change | Bodies checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|
| before | none | 8 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 8 | 0.0 | none | 0 |
| revert | pod_w back | 8 | 0.0 | none | 0 |
| edit | wall_depth 1495 mm -> 1520 mm | 8 | 0.0 | none | 0 |
| revert | wall_depth back | 8 | 0.0 | none | 0 |
| edit | cs_front 360 mm -> 330 mm | 8 | 0.0 | none | 0 |
| revert | cs_front back | 8 | 0.0 | none | 0 |
| edit | sh_z0 2230 mm -> 2220 mm | 8 | 0.0 | none | 0 |
| revert | sh_z0 back | 8 | 0.0 | none | 0 |
| edit | lg_z 1067 mm -> 1000 mm | 8 | 0.0 | none | 0 |
| revert | lg_z back | 8 | 0.0 | none | 0 |

**EDIT TEST: PASS.** The shelves and the LED profile follow the lining faces and the soffit depth, the ledge and the
rail follow the right wall, and every body holds its place on revert.
