# Edit test record: BASE native CAD, samples P01 and P02

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-ET | P02 | DRAFT | 2026-11-01 | BASE Engineer |

`base_edit_test.py` opens the exported `110000_P01_BASE_CAD.f3d` as a copy (the cloud file is never touched), changes skeleton and BASE parameters in three sets, and checks after each that the timeline stays healthy, that every part we make follows its own expressions (box to 0.05 mm), that the side band's J-BASE-01 hole centres follow, and that D-129's back corner holes and slot ends follow. Then it puts every value back and checks that every body returns. The copy is closed without saving.

## Run of 2026-11-01, ended 15:24 UTC (build run G: batch 2, D-144, the welded sill, D-163, the made glide and cap, D-169), in build run G, on its file

Nine parts measured: the side bands LH and RH, the back band, FR1, the sill's two members (111302, 111303), FL1 and FL2; and their holes: the side bands' J-BASE-01 and spigot rivnuts, D-129's back corner holes and slot ends, the sill's 4 channel rivnut holes (tied to FR1's joint and FRONT's glass lines), FR1's keyholes and glide holes.

| Edit set | Changes | Timeline | Boxes | Holes | Back corner (D-129) |
|---|---|---|---|---|---|
| Pod size and wall depth (skeleton), DL's points with the front face | `pod_w` 2700, `pod_d` 1800, `wall_depth` 1595, `dl_y1` 720, `dl_y2` 802, `dl_y3` 894 | healthy | side band LH X −1350…−1310, Y −720…900; back band X ±1310, Y 860…900; RH X 1310…1350; FR1 X 118.46…1015, Y −900…−860; the sill's profile to X 1065 (its right end follows FR1's joint), its plate Y −860…−691.5; FL1 X −1350…−1235.19, Y −802…−702.07; FL2 X −1258…−1064, Y −894…−689: all follow | side band 6, sill 4, FR1's keyholes 2 + 2 and glides 2, RH 6: all follow | follow |
| Band section and glide height (skeleton + BASE) | `band_h` 120, `glide_h` 15, `band_wall` 2.5 | healthy | every part Z 15…135 (the sill's plate to 133): all follow | all follow | follow |
| DL facet, joint and spigot spacing (skeleton + BASE) | `dl_x2` 110, `dl_y1` 700, `jb_e` 260, `sp_e` 120, `jb_n` 5 | healthy | side band LH front end Y −700; FL1 X −1350…−1216.17, Y −802…−682.54; FL2 X −1240…−1064: all follow | side bands 7 each: follow | follow |
| Revert | every value back | healthy | largest difference 0.0000 mm | same | RESTORED |

Result: **PASS**, every part we make follows its parameters and comes back. Every box above is the one the offline check worked out from the same expressions before the run.

## Run of 2026-11-01, ended 12:55 UTC (build run E: batch 2, D-144, the welded sill): stopped in its first set

Nine parts measured since batch 2: the side bands LH and RH, the back band, FR1, the sill's two members, FL1 and FL2. In the first set (`pod_w` 2700, `pod_d` 1800, `wall_depth` 1595) the timeline went unhealthy: FL1's rivnut hole for DL's round spigot found no body to cut ("No target body"). FRONT places DL's spigots from the front face (`decor_d`), while the skeleton gives DL's facet points as Y values from the pod's centre (`dl_y1` to `dl_y3`), so a deeper pod moved the spigot point 50 forward of FL1. Fixed in the test, not the model: the pod-size set now moves DL's points with the front face (`dl_y1` 720, `dl_y2` 802, `dl_y3` 894), and the DL set changes `dl_y1` by −20 as before (700). Checked offline before the next run: in every set both spigot points stayed 13 from their band's nearest edge, and every part's expected box stays a box. (D-169 has since taken DL's base spigots away; the test keeps the pod-size set, as DL's facet still belongs to the front face.)

## Run of 2026-11-01, ended 11:01 UTC (D-150: the sill's closed door end), in build run D, on its file

Five parts measured: the side bands LH and RH, the back band, FR1 and the sill (now with its welded door-end plate).

| Edit set | Changes | Timeline | Boxes | Side band holes | Back corner (D-129) |
|---|---|---|---|---|---|
| Pod size and wall depth (skeleton) | `pod_w` 2700, `pod_d` 1800, `wall_depth` 1595 | healthy | side band LH X −1350…−1310, Y −670…900; back band X ±1310, Y 860…900; side band RH X 1310…1350, Y −672…900; FR1 X 118.46…1015, Y −900…−860; sill X 118.46…965, Y −860…−689.5: all follow | 6, follow | follow |
| Band section and glide height (skeleton + BASE) | `band_h` 120, `glide_h` 15, `band_wall` 2.5 | healthy | every part Z 15…135: all follow | 6, follow | follow |
| DL facet, joint and spigot spacing (skeleton + BASE) | `dl_x2` 110, `dl_y1` 650, `jb_e` 260, `sp_e` 120, `jb_n` 5 | healthy | side band LH front end Y −650; the others as before: all follow | 7, follow | follow |
| Revert | every value back | healthy | largest difference 0.0000 mm | same | RESTORED |

Result: every check passed. The run then stopped on the test's last line, which switched back to the build's document after the build had already closed it. Fixed in `base_edit_test.py`: it now switches back only when that document is open.

In this branch the sill's right end (X 965) and its 4 rivnut positions are numbers taken from FRONT, so with the wider pod the sill still ends at 965 as its parameter says. The next branch ties them to FR1's joint and FRONT's linked glass lines, and its edit test also measures the sill's rivnuts, FR1's keyholes and glide holes and the RH band's holes (Reviewer 8's P3).

## Run of 2026-11-01, ended 07:56 UTC (P02 batch 1, D-129, D-132), on the file from build run C

Five parts measured: the side bands LH and RH, the back band, FR1 and the sill (P02's three parts measured since this run; the build's own run of the test, in the same run as the build, measured the first two and kept the timeline healthy for all).

| Edit set | Changes | Timeline | Boxes | Side band holes | Back corner (D-129) |
|---|---|---|---|---|---|
| Pod size and wall depth (skeleton) | `pod_w` 2700, `pod_d` 1800, `wall_depth` 1595 | healthy | side band LH X −1350…−1310, Y −670…900; back band X ±1310, Y 860…900; side band RH X 1310…1350, Y −672…900; FR1 X 118.46…1015, Y −900…−860; sill X 118.46…965, Y −860…−689.5: all follow | 6, follow | follow |
| Band section and glide height (skeleton + BASE) | `band_h` 120, `glide_h` 15, `band_wall` 2.5 | healthy | every part Z 15…135: all follow | 6, follow | follow |
| DL facet, joint and spigot spacing (skeleton + BASE) | `dl_x2` 110, `dl_y1` 650, `jb_e` 260, `sp_e` 120, `jb_n` 5 | healthy | side band LH front end Y −650; the others as before: all follow | 7, follow | follow |
| Revert | every value back | healthy | largest difference 0.0000 mm | same | RESTORED |

Result: **PASS**, every part we make follows its parameters and comes back.

The hardware copies (rivnuts, spigots, glides, keys, caps) and the lip seal's envelopes are placed by the build from the same expressions as their holes and faces; a parameter edit moves the holes and faces, and a rebuild places the copies again (MANIFEST.md).

## Earlier: sample P01 (2026-10-31)

The same three sets plus the floor's (`fl_gap`, `fl_t`, `lap_w`) on the P01 assembly (side band LH, back band, F1 and its foam): PASS, largest difference after the revert 0.0000 mm. The floor went with D-132.
