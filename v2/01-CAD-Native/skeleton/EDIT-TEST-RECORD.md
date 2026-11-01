Run 2026-11-01 06:42 UTC on Mac 1, Fusion build b43a07003c01, through the Fusion lock: `python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/edit_test_skeleton.py` on the P04 skeleton after in-place update 5 (the kick strip on the band's bottom line, `glide_h`; update 4 took the floor, its mats and the threshold out, D-132). The edit changes `pod_w`, `pod_h`, `seam_gap` (2.26 to 4) and `outer_t` (46 to 50), so every seam and stack rule is shown to follow (Reviewer 5, P3-4 on PR #24). The pod is now 2390 tall in the file: its lowest envelopes, the base bands and the kick strip, start on `glide_h` (Z 10), since there is no floor under them.

## Skeleton edit test record

Copy of `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON_CAD.f3d`, opened as a new unsaved document and closed without saving.

| State | pod size X x Y x Z (mm) | Unhealthy items | Envelopes off their expressions | Worst (mm) |
|---|---|---|---|---|
| Before | 2500 x 1700 x 2390 | 0 | none (all 22 envelopes and 26 faceted anchors follow) | 0 |
| pod_w 2600, pod_h 2450, seam_gap 4, outer_t 50 | 2600 x 1700 x 2440 | 0 | none (all 22 envelopes and 26 faceted anchors follow) | 0 |
| Reverted | 2500 x 1700 x 2390 | 0 | none (all 22 envelopes and 26 faceted anchors follow) | 0 |

**RESULT: PASS (CAD check on a copy)**
