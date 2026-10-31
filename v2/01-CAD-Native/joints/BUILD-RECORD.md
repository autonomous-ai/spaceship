# Build record: joint hardware we make (P01)

Run 2026-11-01 (about 20:19 UTC) on Mac 1, Fusion 2706.1.17 (API b43a07003c01), through the Fusion lock: `python3 tools/fusion/run_script.py <late loader> --arg target=v2/01-CAD-Native/joints/joints_hardware_build.py`, one run for all three designs. **PROPOSED P01.** The script was checked first with `tools/fusion/check_api.py` (0 name errors). The first run (about 19:16 UTC) stopped at the key's fixing-hole sketch ("over constrained"). Fusion rolled it back, so nothing was saved, and the holes are now hole features placed from the block's edges.

## Result

| Design (Default Project / FocusPod v2 / joints) | Body box in its own frame (mm) | Mass (calculation, Fusion material) | Edit test |
|---|---|---|---|
| `111211_P01_BASE-CORNER-KEY-TABULATED_CAD`, saved at `cut_angle` 0 (111211) | X 0..25, Y −17.5..17.5, Z 0..75; 12 faces (block, 4 tap-drill holes, 2 drill points) | 0.1725 kg (Aluminum 6061) | `key_h` 75 → 80: Z 0..80, then back to 0..75: **PASS** |
| `831001_P01_HARDWARE-LOCATING-SPIGOT_CAD` | X −4..4, Y −4..4, Z −8..7.24 (origin on its rivnut's head); hex socket sketch fully constrained | 0.00417 kg (Stainless Steel) | `pin_proud` 8 → 10: top Z 7.24 → 9.24, then back: **PASS** |
| `831002_P01_HARDWARE-STOP-WASHER_CAD` | X −10..10, Y −10..10, Z 0..1.5 (`wash_t` = skeleton `seam_gap` − 0.76) | 0.000915 kg (Aluminum 5052) | `wash_od` 20 → 24: X −12..12, then back: **PASS** |

The key family, one STEP per part number (`cut_angle` set, then exported):

| Part | `cut_angle` | Body box (mm) | Mass | STEP check (`tools/fusion/step_check.py --expect`) |
|---|---|---|---|---|
| 111211 | 0 | X 0..25.00 | 0.1725 kg | X 0..25.000, Y ±17.5, Z 0..75: **MATCH** (0.0000) |
| 111212 (LH) | −24.14° | X 0..32.84 | 0.1723 kg | X 0..32.843: **MATCH** (0.0028) |
| 111213 (RH) | +24.02° | X 0..32.80 | 0.1723 kg | X 0..32.799: **MATCH** (0.0012) |
| 111214 (knee) | −7.25° | X 0..27.23 | 0.1725 kg | X 0..27.226: **MATCH** (0.0037) |

Every STEP file says its length unit is cm, as Fusion writes it (D-13). step_check takes its box from vertices, so it is exact only for the straight-edged keys. The spigot's and washer's round outlines are checked against the boxes Fusion measured above.

## Exports

- `.f3d`: `v2/01-CAD-Native/joints/111211_P01_BASE-CORNER-KEY-TABULATED_CAD.f3d`, `831001_P01_HARDWARE-LOCATING-SPIGOT_CAD.f3d`, `831002_P01_HARDWARE-STOP-WASHER_CAD.f3d`, each exported right after its save.
- STEP: `v2/03-Manufacturing/joints/111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step`, `111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step`, `111213_P01_BASE-CORNER-KEY-FRONT-RH_STEP.step`, `111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step`, `831001_P01_HARDWARE-LOCATING-SPIGOT_STEP.step`, `831002_P01_HARDWARE-STOP-WASHER_STEP.step`.
- DXF (D-89 part 4, so no drawing): `v2/03-Manufacturing/joints/831002_P01_HARDWARE-STOP-WASHER_DXF.dxf`: R12, $INSUNITS 4 (mm), circles Ø20.0 and Ø10.5 on layer CUT only, written by the build from the body's own faces.
- Rows: `v2/03-Manufacturing/joints/V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv` (process, material, thickness, finish, ISO 2768-m, critical notes, CAD masses).

## How it is built

- Skeleton values come from `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv` (P04 v4), under their own names: `band_t`, `band_h` and `glide_h` for the keys, `seam_gap` for the washer. The key's width is `band_t − 2 × 1.5 − 2 × 1` = 35.
- Key: a plan sketch (constrained: width, both side lengths from `key_len ± key_w / 2 × tan(cut_angle)`, and the centre line), extruded `key_h`. Two fixing holes (Ø5.0 × 18 with a drill point, M6 thread 15) and two hook-stud holes (Ø5.0 through, M6), as hole features placed from the block's own edges. The stud holes sit `key_w / 2 / cos(cut_angle)` from the stud face's edge, so every cut keeps them on the centre line. M6 cosmetic threads. No hole sketch.
- Spigot: one sketch with both circles (Ø8, Ø6), the pin extruded up `pin_len` = 8 − 0.76, the M6 stud down 8, a 1 × 45° lead-in, and a 4 mm hex socket 3.5 deep (its sketch fully constrained). M6 cosmetic thread.
- Washer: one ring sketch, extruded `seam_gap − rivnut_head`.
- Each design passed the shared safe-to-create check (`tools/fusion/fusion_folder.py`) before it was made. Each was saved once (no copies) and closed without keeping its edit test.
- Positions in the pod: `corner-keys.csv` (from `corner_keys.py`); placement notes in `README.md`.
