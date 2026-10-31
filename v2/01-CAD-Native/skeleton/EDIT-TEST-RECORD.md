Run 2026-10-31 on Mac 1, Fusion 2706.1.17, `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/edit_test_skeleton.py` on the P03 skeleton.

## Skeleton edit test record

Copy of `v2/01-CAD-Native/skeleton/100000_P03_POD-SKELETON_CAD.f3d`, opened as a new unsaved document and closed without saving.

| State | pod size X x Y x Z (mm) | Unhealthy items | Envelopes off their expressions | Worst (mm) |
|---|---|---|---|---|
| Before | 2500 x 1700 x 2400 | 0 | none (all 27 envelopes and 10 faceted anchors follow) | 0 |
| pod_w 2600, pod_h 2450 | 2600 x 1700 x 2450 | 0 | none (all 27 envelopes and 10 faceted anchors follow) | 0 |
| Reverted | 2500 x 1700 x 2400 | 0 | none (all 27 envelopes and 10 faceted anchors follow) | 0 |

**RESULT: PASS (CAD check on a copy)**
