# Edit test record: 810000 INTERIOR P01

Run 2026-11-01 12:42 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock, in the same held session as the
rebuild (`BUILD-RECORD.md`), on a copy of the exported design, closed without saving:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/edit_test_interior.py`. Each change is made alone, every
body is checked against the box the layout gives for the new values and every fold face of the bent parts against its
radius (inside the sheet, outside twice), then the change is reverted and checked again. (Earlier builds' edit tests
passed the same way: 2026-10-31 20:52 UTC with 9 bodies, 2026-11-01 05:52 with 8, 07:35 with the ledge and the rail 5 mm
off the lining; this one adds the folds and the two sheet thicknesses.)

| Step | Change | Bodies checked | Fold faces checked | Worst deviation (mm) | Off | Unhealthy timeline items |
|---|---|---|---|---|---|---|
| before | none | 8 | 16 | 0.0 | none | 0 |
| edit | pod_w 2500 mm -> 2600 mm | 8 | 16 | 0.0 | none | 0 |
| revert | pod_w back | 8 | 16 | 0.0 | none | 0 |
| edit | wall_depth 1495 mm -> 1520 mm | 8 | 16 | 0.0 | none | 0 |
| revert | wall_depth back | 8 | 16 | 0.0 | none | 0 |
| edit | cs_front 360 mm -> 330 mm | 8 | 16 | 0.0 | none | 0 |
| revert | cs_front back | 8 | 16 | 0.0 | none | 0 |
| edit | sh_z0 2230 mm -> 2220 mm | 8 | 16 | 0.0 | none | 0 |
| revert | sh_z0 back | 8 | 16 | 0.0 | none | 0 |
| edit | lg_z 1067 mm -> 1000 mm | 8 | 16 | 0.0 | none | 0 |
| revert | lg_z back | 8 | 16 | 0.0 | none | 0 |
| edit | sh_t 1 mm -> 1.2 mm | 8 | 16 | 0.0 | none | 0 |
| revert | sh_t back | 8 | 16 | 0.0 | none | 0 |
| edit | lg_t 1.5 mm -> 2 mm | 8 | 16 | 0.0 | none | 0 |
| revert | lg_t back | 8 | 16 | 0.0 | none | 0 |

**EDIT TEST: PASS.** The shelves and the LED profile follow the lining faces and the soffit depth, the ledge and the
rail follow the right wall, the folds follow each sheet's thickness (sh_t, lg_t: every fold face at the inside radius
the sheet and the outside twice it), and every body holds its place on revert.
