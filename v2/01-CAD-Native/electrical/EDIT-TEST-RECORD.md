# Edit test record: 710000 ELECTRICAL P01 (route model)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-ELE-02 | P01 | DRAFT | 2026-11-01 | ELECTRICAL Engineer |

Guideline section 4.4: the native file must follow its parameters. `edit_test_electrical.py` opens the repo's exported `710000_P01_ELECTRICAL_CAD.f3d` as a new, unsaved copy, makes each edit, checks that the timeline stays healthy and that every one of the 41 bodies sits where the offline model (`electrical_model.py`, with the same edit) puts it (0.01 mm), reverts the edit and checks again, then closes the copy without saving. The edits are `EDIT_TEST_EDITS` in `electrical_model.py`; the offline test checks first that each edit leaves every reserved space with a positive size.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/edit_test_electrical.py --label "ELECTRICAL Engineer"
```

## Run 2026-10-31 about 20:56 UTC (export of the 20:55 rebuild, same Fusion run): PASS

| Edit | Timeline | Bodies against the model | Reverted |
|---|---|---|---|
| as exported | 0 unhealthy | 0.0000 mm | - |
| power unit down 50 mm (`pu_zc` 950) | 0 unhealthy | 0.0000 mm | 0.0000 mm |
| trunk up 50 mm (`trunk_z` 1150) | 0 unhealthy | 0.0000 mm | 0.0000 mm |
| pod 20 mm deeper (skeleton `pod_d` 1720) | 0 unhealthy | 0.0000 mm | 0.0000 mm |
| bigger pockets and grommets (`pk_l` 180, `grm_d` 22) | 0 unhealthy | 0.0000 mm | 0.0000 mm |

All 41 bodies follow every edit to 0.0000 mm and come back to the exported state on every revert. The copy was closed without saving.

## Run 2026-10-31 about 20:2x UTC (export of the 19:17 rebuild on skeleton P04 version 4): FAIL, two edits

| Edit | Timeline | Bodies against the model | Reverted |
|---|---|---|---|
| as exported | 0 unhealthy | 0.0000 mm | - |
| power unit up 100 mm (`pu_zc` 1100) | 0 unhealthy | L1-B2 off by 84.13 mm | 0.0000 mm |
| trunk up 50 mm (`trunk_z` 1150) | 0 unhealthy | 0.0000 mm | 0.0000 mm |
| pod 20 mm deeper (skeleton `pod_d` 1720) | 0 unhealthy | G-CEIL-F off by 6.5 mm | 0.0000 mm |
| bigger pockets and grommets (`pk_l` 180, `grm_d` 22) | 0 unhealthy | 0.0000 mm | 0.0000 mm |

Why, and what changed:
- **L1-B2**: the light-feed run from the pocket P5 above the power unit to the top of B2-CASS has about 16 mm of room. With the unit 100 mm higher its start passes its end; Fusion turns the extrude the right way round, the model doesn't, so they differ. The edit was wrong, not the model: the unit can't move up that far in B2. The edit now moves the unit down 50 mm, and the offline test checks every edit first (`test_edit_test_edits_keep_every_body_a_box`).
- **G-CEIL-F**: three numbers copied from CEILING's design didn't follow the skeleton: the ceiling cassette's front return (Y −282), its back return (Y 763) and its cable holes' X (+583). They are now linked: `ceil_y0 = col_y1 + 3 mm` (3 mm behind the soffit's back face), `ceil_y1 = y_bf - 3 mm` (3 mm off the back lining) and `ceil_x = inner_w / 4` (the right ceiling cassette's centre, from the skeleton's named value `inner_w`, now derived too). The values at P04 are the same.
- The first attempt (19:17 run, second step) stopped before any edit: it looked for part number 710000 on the copy's root, which an imported copy doesn't keep. It now checks for the 7 ELECTRICAL components.

