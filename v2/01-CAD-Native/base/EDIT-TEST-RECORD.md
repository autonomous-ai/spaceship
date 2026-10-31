# Edit test record: BASE native CAD, sample P01

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-ET | P01 | DRAFT | 2026-11-01 | BASE Engineer |

`base_edit_test.py` opens the exported `110000_P01_BASE_CAD.f3d` as a copy, changes skeleton and BASE parameters in four sets, and checks after each that the timeline stays healthy, that every part we make follows its own expressions (box to 0.05 mm) and that the side band's J-BASE-01 hole centres follow the skeleton's start point and the 220 mm rule. Then it puts every value back and checks the model returns exactly. The copy is closed without saving. Run A, 2026-11-01 20:14 UTC (see BUILD-RECORD.md).

| Edit set | Changes | Timeline | Boxes (side band LH, back band, F1, its foam) | Side band holes |
|---|---|---|---|---|
| Pod size and wall depth (skeleton) | `pod_w` 2700, `pod_d` 1800, `wall_depth` 1595 | healthy | side band X −1350…−1310, Y −670…897; back band X ±1310, Y 860…900; F1 X −1306…12.5, Y −695…856: all follow | 6, follow |
| Band section and glide height | `band_h` 120, `glide_h` 15, `band_wall` 2.5 | healthy | bands Z 15…135; F1 and foam unchanged: all follow | 6, follow |
| DL facet, joint and spigot spacing | `dl_x2` 110, `dl_y1` 650, `jb_e` 260, and the spigot inset | healthy | side band front end Y −650: follows | 6, follow |
| Floor | `fl_gap` 6, `fl_t` 12, `lap_w` 10 | healthy | F1 X −1304…9.5, Y −695…854, Z 3…15; foam Z 0…3: follow | 6, follow |
| Revert | every value back | healthy | largest difference 0.0000 mm | same: RESTORED |

Result: **PASS**, every part we make follows its parameters and comes back. The hardware copies (rivnuts, spigots, glides, keys) are placed by the build from the same expressions as their holes; a parameter edit moves the holes, and a rebuild re-places the copies (MANIFEST.md).
