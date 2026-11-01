# Edit test record: BASE native CAD, samples P01 and P02

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-ET | P02 | DRAFT | 2026-11-01 | BASE Engineer |

`base_edit_test.py` opens the exported `110000_P01_BASE_CAD.f3d` as a copy (the cloud file is never touched), changes skeleton and BASE parameters in three sets, and checks after each that the timeline stays healthy, that every part we make follows its own expressions (box to 0.05 mm), that the side band's J-BASE-01 hole centres follow, and that D-129's back corner holes and slot ends follow. Then it puts every value back and checks that every body returns. The copy is closed without saving.

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
