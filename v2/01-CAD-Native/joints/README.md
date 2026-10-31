# Joint hardware we make: native models (joints register)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-JNT (folder row in `document-register.csv`) | P01 | PROPOSED | 2026-11-01 | Joints Engineer |

The made parts of the joints register (`v2/05-Engineering/joints/joints-register.md`), as native Fusion designs built by one script on skeleton P04's named values. The register is the source for every size; the models follow it. STEP and DXF are in `v2/03-Manufacturing/joints/`, with the manufacturing rows (`V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv`). Drawings follow on their own branch once the shared drawing start runs again (D-91).

## Files

| File | What |
|---|---|
| `joints_hardware_build.py` | Builds all three designs in one Fusion run, saves them to Default Project / FocusPod v2 / joints, exports the .f3d, STEP and DXF, and edit-tests each one. See its docstring. |
| `111211_P01_BASE-CORNER-KEY-TABULATED_CAD.f3d` | Corner key family 111211 to 111214 (J-BASE-02): one block, `cut_angle` per part number. Saved at 0 (111211); one STEP per part number. |
| `831001_P01_HARDWARE-LOCATING-SPIGOT_CAD.f3d` | Locating spigot 831001 (H-05). |
| `831002_P01_HARDWARE-STOP-WASHER_CAD.f3d` | Stop washer 831002 (H-08). It is flat and cut from sheet, so it has a DXF and no drawing (D-89 part 4). |
| `corner_keys.py`, `corner-keys.csv` | Where each of the 6 keys sits in the pod, from the skeleton's named values and BASE's front points (register J-BASE-02). |
| `BUILD-RECORD.md` | The build run's log, with sizes, masses, STEP checks and edit tests. |

## Placing the parts (for WALL, BASE, FRONT, CEILING and AIR)

Every body is one solid in its design's root component, in mm.

| Part | Its origin and axes | Where it goes |
|---|---|---|
| Spigot 831001 | Origin on the axis, on the face it sits on: the top of its rivnut's head, 0.76 above the tube face. +Z up the pin. The pin's top is at Z 7.24, so 8.00 above the tube face; the M6 stud runs down to Z −8. | At every spigot rivnut (838003 without a stop washer): the band's top, the lower panels' and back panels' tops, DL's and DR's tops, DL and DR's support, and F2 under the air column (register FR-04, FR-17, FR-22). Place it at the rivnut's axis, its origin 0.76 above the tube face. |
| Stop washer 831002 | Origin on the axis, on its bottom face. +Z through its 1.5 thickness. | Under the head of every stopped-joint rivnut (FR-01): on the tube face, under the rivnut's 0.76 head, so the head's top is 2.26 above the face (seam_gap). |
| Corner keys 111211 to 111214 | Origin at the middle of the key's back face, on its bottom. +X along the carrier toward the joint, +Y = Z × X (to the left of +X), +Z up. The stud face is at X 30 on the centre line, cut by `cut_angle`. | One row per key in `corner-keys.csv`: put the origin at `key_back_centre_x, key_back_centre_y, key_bottom_z` and turn +X to `carrier_dir_x, carrier_dir_y`. Use the STEP of that row's part number. |

The keys' STEP files are exported at their own cut, so each one can be placed as it is. A team that copies the parts into its own design keeps these part numbers and names (register R7).

## Rebuild

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_hardware_build.py

It refuses to run if a design of the same name is already in FocusPod v2 / joints, or if any entry of that folder can't be read. To rebuild one design, delete its cloud file first and pass `--arg only=keys` (or `spigot`, `washer`). Then check the STEP files:

    python3 tools/fusion/step_check.py v2/03-Manufacturing/joints/<file>.step --expect=xmin,ymin,zmin,xmax,ymax,zmax
