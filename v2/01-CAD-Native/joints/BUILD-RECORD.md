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

## Mitre plate blanks update (version 2 of the plate design, 2026-11-01)

Run 2026-11-01, 09:25 to 09:26 UTC, on Mac 1 in one held Fusion session: `joints_plates_trim_update.py` by the late loader on the saved design (opened with `--doc`), after `check_api.py` (0 name errors). **PROPOSED P01.** Why: the Lead's steer after WALL's L1 model (WALL group, 07:40 UTC): each plate stays a laser-cut rectangle with square ends, shortened so its ends sit 0.5 inside the frame's faces on both plate faces; a full-size plate poked out at the outer corner by its half thickness × the cut's cosine (0.71 at 45°; 0.45 and 0.89 at 831008), 0.45 of it into L1's skin back return.

- **In the saved design:** the old outline's extrude and sketch deleted (features in the design; no cloud file touched, D-141); parameters added: `plate_mitre` = sqrt(tube_a² + tube_b²) (the old `plate_len` formula), `plate_x0` (where the blank starts along the mitre); `plate_len` became the blank's length. The new outline is the build script's own `plate_geometry()` (so a fresh build makes the same plate): the rectangle's corner held `plate_x0` from the origin by a construction line ("added horizontal, vertical, horizontal, vertical; fully constrained True"), extruded `plate_t` symmetric. Material Steel, Galvanized. Saved as a new version (never a copy) and the `.f3d` exported.

| Variant | `tube_a`, `tube_b` | `plate_x0`, `plate_len` | Body box in its own frame (mm), version 2 | Mass (calculation, Fusion "Steel, Galvanized") | STEP check (`tools/fusion/step_check.py --expect`) |
|---|---|---|---|---|---|
| 831007 (saved state) | 20, 20 | 1.75, 26.5 | X 1.75..28.25, Y 0..40, Z −1..1 | 0.01664 kg | **MATCH** (0.0000 mm) |
| 831008 | 20, 40 | 3.15, 41.5 | X 3.15..44.65, Y 0..40, Z −1..1 | 0.02606 kg | **MATCH** (0.0000 mm) |
| 831009 | 40, 40 | 1.75, 54.8 | X 1.75..56.55, Y 0..40, Z −1..1 | 0.03441 kg | **MATCH** (0.0000 mm) |

- The mitre lines are 28.284, 44.721 and 56.569, so each blank's inner end sits at the inner corner within 0.07; every corner of both square ends is 0.51 to 0.53 inside the frame's faces (`frame_steel_check.py`, `plate_corners()`).
- **Each STEP carries its own part number** (C06), set before each export; the origin stays at the frame's outer corner, so WALL's placement doesn't move. **DXFs** (R12, mm, the blank alone on layer CUT, from its own corner): 26.500 × 40.000, 41.500 × 40.000 and 54.800 × 40.000.
- **Edit test:** `plate_x0` 1.75 → 3.15: X 1.75..28.25 → 3.15..29.65 (the length kept), then back to 1.75..28.25: **PASS**. Closed without keeping it or the per-STEP changes.
- **Checked against the exports:** `frame_steel_check.py --check` now reads each plate's STEP box and DXF extents and fails unless they are its blank (Reviewer 6 on #308); on main's full-size files it fails all six, on these it passes.

## D-144 update run (version 3 of the key design)

Run 2026-11-01, 07:51 to 08:19 UTC queued and run, on Mac 1 through the Fusion lock: `joints_keys_d144_update.py` by the late loader with `--doc 111211_P01_BASE-CORNER-KEY-TABULATED_CAD --close`, after `check_api.py` (0 name errors). It opened version 2 and saved **version 3** in place (never a copy).
- **D-144** (PM ruling 2026-11-01): a new parameter `fix_step` (the −y fixing hole's step along x), `fix_y` per number, and the −y hole's offset from the back edge changed from `fix_x` to `fix_x + fix_step` (its own model parameter). Saved state 111211: `fix_y` 6, `fix_step` 7.3, so its fixing holes are at **(10.5, +6.0) and (17.8, −6.0)**.
- **Five STEPs, each with its own part number** (C06), each checked by the run against its layout before export: 111211 (cut 0, holes as above), 111212 (−24.14°), 111213 (+24.02°), 111214 (−7.25°) and **111215** (cut 0, the FR1 key: holes at (10.5, ±7.0)). `step_check --expect`: all five MATCH (0.004 mm or less). The holes read straight from the STEP files: 111211 (10.5, 6.0) and (17.8, −6.0), 111215 (10.5, ±7.0), the stud axes at y 0, Z 26 and 60 on both.
- Edit test: `fix_step` 7.3 → 8 → 7.3 moved the −y hole from x 17.8 to 18.5 and back: **PASS**. Closed without keeping the per-STEP changes or the test.
- `joints_hardware_build.py` builds the same from scratch (`fix_step`, the stepped −y hole, five variants).

## Exact mitres for 111212 and 111214 (export run, 2026-11-01, 10:08 UTC)

BASE's ask, relayed by the Lead: cut 111212's face at the mitre's exact 24.1446°. Version 3's exports took corner-keys.csv's 2-decimal angles, so 111212 was cut at −24.14 and the knee 111214 at −7.25; the mitres are −24.1446 and −7.2546 (`corner_keys.py`, which now writes the cut to 4 decimals and, with `--check`, fails if the build script's `KEY_VARIANTS` drift from the mitres). 111213's +24.02 is already exact; 111211 and 111215 are square.

`joints_keys_exact_cut_export.py` by the late loader on the saved design (version 3, opened with `--doc`), after `check_api.py` (0 name errors), in the same held Fusion session as the key sheet's redraw. For each of the two it set `cut_angle`, `fix_y` 7 and `fix_step` 0 and the part number, checked the fixing holes and the long side, exported the STEP, and the design closed **without saving** (its saved state, 111211 square, is unchanged, so the drawing's reference stays current).

| Part | `cut_angle` | Body box (mm) | Long side, the mitre's | Fixing holes | STEP check (`step_check.py --expect`) |
|---|---|---|---|---|---|
| 111212 (LH) | −24.1446° | X 0..37.8445, Y ±17.5, Z 0..75 | 37.8445 | (10.5, ±7) | **MATCH** (0.0000 mm); the cut face reads 24.1446° from square (`tools/checks/stepfile.py`) |
| 111214 (knee) | −7.2546° | X 0..32.2277, Y ±17.5, Z 0..75 | 32.2277 | (10.5, ±7) | **MATCH** (0.0000 mm); the cut face reads 7.2546° |

The drawing gives these angles to 0.01° (24.14°, 7.25°) with ±0.25°, and its long and short sides (37.84 / 22.16, 32.23 / 27.77) don't change at 0.01.

## The 11 mm spigot 831010 (export run, 2026-11-01, 11:49 UTC)

The Lead's ruling on J-FRONT-03: DT's two spigots on DR's ledge stand 11 proud, so they still engage DT's bottom back tube 5 now that its bottom face is at Z 2126, 6 above the ledge's top (FRONT's model). The saved spigot design already drives the pin from `pin_proud` (`pin_len` = `pin_proud` − the rivnut's 0.76 head), so `joints_spigot_variant_export.py` (late loader, the design opened with `--doc`, `check_api.py` 0 name errors) set `pin_proud` 11 and the part number 831010, checked the body against the expected box (X and Y ±4, Z −8 to 10.24), exported the STEP and closed the design **without saving**: its saved state, 831001 at 8 proud, doesn't change, so the spigot sheet's reference stays current. A fresh build makes both STEPs (`joints_hardware_build.py`, `SPIGOT_VARIANTS`).

| Part | `pin_proud` | Body (mm) | Mass (Fusion, Stainless Steel) | STEP |
|---|---|---|---|---|
| 831001 (saved state) | 8 | Ø8 pin to Z 7.24, M6 stud to Z −8 | 0.00417 kg | unchanged |
| 831010 | 11 | Ø8 pin to Z 10.24, M6 stud to Z −8 | 0.00538 kg | `831010_P01_HARDWARE-LOCATING-SPIGOT-11-PROUD_STEP.step`, its own part number |

- **Checked from the STEP** (the mechanical check's own reader): the product is 831010; the cylinders are Ø8 and Ø5.884 (the stud at 6g's mean major, as 831001); the levels run −8, 0, 6.74, 9.24, 10.24, each of the pin's 3 above 831001's (3.74, 6.24, 7.24). `step_check.py`'s vertex box reads short in X and Y on any round part, 831001's included; its Z range is exact.
- The run started a few seconds after Fusion's 11:48 server warning was cancelled; it opened, exported and closed normally, and the checks above are on its file.
- The sheet: 831001's drawing becomes TABULATED for both numbers from its finish step only (the drawing record).

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
