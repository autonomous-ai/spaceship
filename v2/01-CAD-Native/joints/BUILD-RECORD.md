# Build record: joint hardware we make (P01)

Run 2026-11-01 (about 20:19 UTC) on Mac 1, Fusion 2706.1.17 (API b43a07003c01), through the Fusion lock: `python3 tools/fusion/run_script.py <late loader> --arg target=v2/01-CAD-Native/joints/joints_hardware_build.py`, one run for all three designs. **PROPOSED P01.** The script was checked first with `tools/fusion/check_api.py` (0 name errors). The first run (about 19:16 UTC) stopped at the key's fixing-hole sketch ("over constrained"). Fusion rolled it back, so nothing was saved, and the holes are now hole features placed from the block's edges.

## Result

| Design (Default Project / FocusPod v2 / joints) | Body box in its own frame (mm) | Mass (calculation, Fusion material) | Edit test |
|---|---|---|---|
| `111211_P01_BASE-CORNER-KEY-TABULATED_CAD`, saved at `cut_angle` 0 (111211); **version 2** after the update run below | X 0..30, Y −17.5..17.5, Z 0..75 (version 1: X 0..25); 12 faces (block, 4 tap-drill holes, 2 drill points) | 0.2075 kg (calculation from the version 2 geometry at Fusion's 2.70 g/cm³; version 1 measured 0.1725 kg at 25 long) | `key_h` 75 → 80: Z 0..80, then back to 0..75: **PASS** (version 1) |
| `831001_P01_HARDWARE-LOCATING-SPIGOT_CAD` | X −4..4, Y −4..4, Z −8..7.24 (origin on its rivnut's head); hex socket sketch fully constrained | 0.00417 kg (Stainless Steel) | `pin_proud` 8 → 10: top Z 7.24 → 9.24, then back: **PASS** |
| `831002_P01_HARDWARE-STOP-WASHER_CAD` | X −10..10, Y −10..10, Z 0..1.5 (`wash_t` = skeleton `seam_gap` − 0.76) | 0.000915 kg (Aluminum 5052) | `wash_od` 20 → 24: X −12..12, then back: **PASS** |

The key family, one STEP per part number (`cut_angle` set, then exported):

| Part | `cut_angle` | Body box (mm), version 2 | Mass | STEP check (`tools/fusion/step_check.py --expect`) | Part number in the STEP |
|---|---|---|---|---|---|
| 111211 | 0 | X 0..30.00 | 0.2075 kg | X 0..30, Y ±17.5, Z 0..75: **MATCH** (0.0000) | 111211 |
| 111212 (LH) | −24.14° | X 0..37.84 | 0.2072 kg | X 0..37.84: **MATCH** (0.0028) | 111212 |
| 111213 (RH) | +24.02° | X 0..37.80 | 0.2072 kg | X 0..37.80: **MATCH** (0.0012) | 111213 |
| 111214 (knee) | −7.25° | X 0..32.23 | 0.2075 kg | X 0..32.23: **MATCH** (0.0037) | 111214 |

Every STEP file says its length unit is cm, as Fusion writes it (D-13). step_check takes its box from vertices, so it is exact only for the straight-edged keys. The spigot's and washer's round outlines are checked against the boxes Fusion measured above.

## Update run (version 2 of the key design)

Run about 20:55 UTC through the lock: `joints_keys_update.py` with `--doc 111211_P01_BASE-CORNER-KEY-TABULATED_CAD --close`. The API checker was clean. It changed the saved design in place (a new version, no copy):
- `key_len` 25 → **30**: the carrier's Ø7.0 fixing holes then sit at least 2 × 7 from its cut end on every key: 14.9 on the front corners, 18.5 at the knee, 19.5 on the square keys (PM note, 2026-11-01; register J-BASE-02, merged in #127).
- `fix_x` 10 → **10.5** and `fix_y` 7.5 → **7.0**: the key's own holes sit 10.5 from its back and side faces, over 2 × the Ø5.03 hole (the mechanical check's C09). Log: "fixing holes at [(10.5, -7.0), (10.5, 7.0)]".
- **Each STEP carries its own part number and name** (C06): the four STEPs were exported with the root part number set to 111211, 111212, 111213 and 111214 in turn, then the saved family state (111211 at 0) was restored. The document was closed without keeping those per-STEP changes.

## Mitre plates run (831007 to 831009, J-FRAME-01, D-131)

Run 2026-11-01, ended 07:05 UTC, on Mac 1 through the Fusion lock: `joints_hardware_build.py --arg only=plates` by the late loader, after `check_api.py` (0 name errors). **PROPOSED P01.** Two earlier runs (06:13 and 06:32 UTC) stopped at the outline sketch, "not fully constrained": the API's `addTwoPointRectangle` joins the corners and adds no horizontal or vertical constraints, so one corner stayed free. Neither saved anything; the second closed the first's leftover unsaved design, and the build now closes its own design on any error. The fix gives each of the four edges its horizontal or vertical constraint ("added horizontal, vertical, horizontal, vertical; fully constrained True").

| Design (Default Project / FocusPod v2 / joints) | Variant | Body box in its own frame (mm) | Mass (calculation, Fusion "Steel, Galvanized") |
|---|---|---|---|
| `831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD`, saved at 831007 | 831007 (`tube_a` 20, `tube_b` 20) | X 0..28.28, Y 0..40, Z −1..1 | 0.01776 kg |
| | 831008 (20, 40) | X 0..44.72, Y 0..40, Z −1..1 | 0.02809 kg |
| | 831009 (40, 40) | X 0..56.57, Y 0..40, Z −1..1 | 0.03553 kg |

- Parameters: `tube_a`, `tube_b` (the two members' widths in the frame's plane), `plate_len` = sqrt(tube_a² + tube_b²) (the mitre line), `plate_d` 40 (the frame's depth), `plate_t` 2.0 (at least 1.5 × the 1.2 mm rails). One outline sketch on XY from the origin, fully constrained, extruded `plate_t` symmetric about it, so the mid-plane is Z 0 and the origin is the plate's corner at the frame's outer corner on the skin-side face (README).
- **Each STEP carries its own part number** (C06): the root part number was set to 831007, 831008 and 831009 in turn before each export, then back to the saved state.
- Edit test: `tube_b` 20 → 40: X 0..28.28 → 0..44.72, then back to 0..28.28: **PASS**. Closed without keeping it.
- STEP check (`tools/fusion/step_check.py --expect`): 831007 X 0..28.284, Y 0..40, Z −1..1, largest difference 0.0003 mm, MATCH; 831008 X 0..44.721, 0.0004, MATCH; 831009 X 0..56.569, 0.0005, MATCH. Each file says cm, as Fusion writes it (D-13).
- Exports: `.f3d` `v2/01-CAD-Native/joints/831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD.f3d`; STEP and DXF (R12, mm, the rectangle on layer CUT; D-89 part 4, so no drawing) in `v2/03-Manufacturing/joints/`, `831007_P01_HARDWARE-MITRE-PLATE-20X40-45DEG_*`, `831008_P01_HARDWARE-MITRE-PLATE-20X40-TO-40X40_*`, `831009_P01_HARDWARE-MITRE-PLATE-40X40-45DEG_*`; rows in `V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv`.

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
