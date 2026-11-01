# Joint hardware we make: native models (joints register)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CAD-JNT (folder row in `document-register.csv`) | P01 | PROPOSED | 2026-11-01 | Joints Engineer |

The made parts of the joints register (`v2/05-Engineering/joints/joints-register.md`), as native Fusion designs built by one script on skeleton P04's named values. The register is the source for every size; the models follow it. STEP and DXF are in `v2/03-Manufacturing/joints/`, with the manufacturing rows (`V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv`). Drawings follow on their own branch once the shared drawing start runs again (D-91).

## Files

| File | What |
|---|---|
| `joints_hardware_build.py` | Builds all three designs in one Fusion run, saves them to Default Project / FocusPod v2 / joints, exports the .f3d, STEP and DXF, and edit-tests each one. See its docstring. |
| `111211_P01_BASE-CORNER-KEY-TABULATED_CAD.f3d` | Corner key family 111211 to 111215 (J-BASE-02): one block, `cut_angle` per part number. Saved at 0 (111211); one STEP per part number. The model and STEPs still carry the first fixing-hole layout on 111211 and no 111215 yet: the next Fusion update makes 111211's stepped holes and adds 111215 (register J-BASE-02). |
| `831001_P01_HARDWARE-LOCATING-SPIGOT_CAD.f3d` | Locating spigot family (H-05, H-45): `pin_proud` 8 (831001) or 11 (831010, DR's DT ledge, J-FRONT-03). Saved at 831001; one STEP per part number; a TABULATED sheet. |
| `831002_P01_HARDWARE-STOP-WASHER_CAD.f3d` | Stop washer 831002 (H-08). It is flat and cut from sheet, so it has a DXF and no drawing (D-89 part 4). |
| `831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD.f3d` | Mitre plate family 831007 to 831009 (J-FRAME-01, H-40 to H-42): one rectangular blank on the mitre line, its start `plate_x0` and length `plate_len` per number (the mitre `plate_mitre` from `tube_a` and `tube_b`). Version 2 (the blanks shortened so each square end sits 0.5 inside the frame's faces, the Lead's steer 2026-11-01). Saved at 831007; one STEP and one DXF per part number (flat, cut from sheet, so no drawing, D-89 part 4). |
| `corner_keys.py`, `corner-keys.csv` | Where each of the 6 keys sits in the pod, from the skeleton's named values and BASE's front points (register J-BASE-02). |
| `frame_steel_check.py` | The steel frame check for J-FRAME-01 (D-131): gauges, the steel grade, masses, the corner lift with the mitre plates, seam bolts and rivnuts. `--check` checks every rule, including that 0.8 mm perimeters and steel under 280 MPa would fail. The joints register quotes its tables. |
| `BUILD-RECORD.md` | The build run's log, with sizes, masses, STEP checks and edit tests. |

## Placing the parts (for WALL, BASE, FRONT, CEILING and AIR)

Every body is one solid in its design's root component, in mm.

| Part | Its origin and axes | Where it goes |
|---|---|---|
| Spigots 831001 and 831010 | Origin on the axis, on the face it sits on: the top of its rivnut's head, 0.76 above the tube face. +Z up the pin. The pin's top is at Z 7.24 (831001) or 10.24 (831010), so 8.00 or 11.00 above the tube face; the M6 stud runs down to Z −8. | At every spigot rivnut (838003 without a stop washer): the band's top, the lower panels' and back panels' tops, DL's and DR's tops, DL and DR's support, and F2 under the air column (register FR-04, FR-17, FR-22). Place it at the rivnut's axis, its origin 0.76 above the tube face; 831010 goes only in DR's DT ledge, under DT (J-FRONT-03). |
| Stop washer 831002 | Origin on the axis, on its bottom face. +Z through its 1.5 thickness. | Under the head of every stopped-joint rivnut (FR-01): on the tube face, under the rivnut's 0.76 head, so the head's top is 2.26 above the face (seam_gap). |
| Mitre plates 831007, 831008, 831009 (J-FRAME-01, D-131) | A flat rectangular blank, 2.0 thick: 26.5 × 40 (831007), 41.5 × 40 (831008) or 54.8 × 40 (831009). Origin at the frame's outer corner, on the skin-side face, on the plate's mid-plane (the old mitre plane); the blank starts along +X from it, at X 1.75 (831007, 831009) or 3.15 (831008), and ends at the inner corner (within 0.07), so each corner of its square ends sits 0.51 to 0.53 inside the frame's faces. +X along the mitre line, from the frame's outer corner toward its inner corner; +Y across the frame, from the skin-side face toward the room side (the 40); +Z = X × Y, normal to the plate, which spans Z −1.0 to +1.0. | At every frame corner, one plate: put its origin at the corner's outer point on the skin-side face, +X along the line to the corner's inner point, +Y into the frame. 831007 where two 20 × 40 members meet at 45°, 831009 where two 40 × 40 meet, 831008 where a 20 × 40 meets a 40 × 40 (its +X then runs 26.57° from the 20 × 40 member's axis and 63.43° from the 40 × 40's). Cut each member back so the plate fits and the outside sizes stay: 1.41 at a 45° corner; 2.24 off the 20 × 40 and 1.12 off the 40 × 40 at 831008 (register J-FRAME-01). STEP and DXF: one per number in `v2/03-Manufacturing/joints/`, each with its own part number; the STEP keeps this origin (the blank sits from its X start), the DXF is the blank alone from its own corner. |
| Corner keys 111211 to 111214 | Origin at the middle of the key's back face, on its bottom. +X along the carrier toward the joint, +Y = Z × X (to the left of +X), +Z up. The stud face is at X 30 on the centre line, cut by `cut_angle`. | One row per key in `corner-keys.csv`: put the origin at `key_back_centre_x, key_back_centre_y, key_bottom_z` and turn +X to `carrier_dir_x, carrier_dir_y`. Use the STEP of that row's part number. |

The keys' STEP files are exported at their own cut, so each one can be placed as it is. A team that copies the parts into its own design keeps these part numbers and names (register R7).

## Rebuild

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_hardware_build.py

It refuses to run if a design of the same name is already in FocusPod v2 / joints, or if any entry of that folder can't be read. To rebuild one design, rename its cloud file NAME_SUPERSEDED-<date> first (D-141: never delete a cloud file) and pass `--arg only=keys` (or `spigot`, `washer`). Then check the STEP files:

    python3 tools/fusion/step_check.py v2/03-Manufacturing/joints/<file>.step --expect=xmin,ymin,zmin,xmax,ymax,zmax
