# Build record: BASE native CAD, sample P01

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-BR | P01 | DRAFT | 2026-11-01 | BASE Engineer |

How the sample's native files were made, and what each build checked (guideline §4.5, §10). Every run goes through `tools/fusion/run_script.py` (the shared Fusion lock) with the late-binding loader `late_base.py`, which reads the scripts only when the lock is granted. Fusion build b43a07003c01.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py --timeout 2700 \
  --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
  --arg save=1 --arg replace=1 --arg export=1 --arg also_parts=<part keys>
python3 v2/03-Manufacturing/base/make_outputs.py --dxf
```

## Run A, 2026-11-01 20:06 to 20:14 UTC: assembly, 4 part designs, edit test

| What | Result |
|---|---|
| Parameters | 89 skeleton P04 parameters (v4, `pod_skeleton.py`) and 52 BASE parameters; BASE skips none (the skeleton's `mat_t` replaced BASE's own) |
| Timeline | 169 items, all healthy |
| Sketches | 33, all fully constrained (the build stops on any that isn't) |
| Part boxes | side band LH X −1250…−1210, Y −670…847, Z 10…110; back band X −1210…1210, Y 810…850, Z 10…110; F1 X −1206…12.5, Y −645…806, Z 3…12; its foam Z 0…3: each matches its expressions |
| Holes | side band: 6 rivnut holes on X −1224 (Y −542.74, −422.74, −71.83, 279.09, 630.00, 750.00); glides at Y −595 and 700 on X −1230. Back band: 12 rivnut holes on Y 824 (220 / 100 rule on the frame, pitch 253.00); glides at X −1060, 0, 1060 on Y 830 |
| Hardware | back band: 2 corner keys 111211 (by reference), 4 hook studs 838001, 4 button head screws 838010, 3 glides and doublers, 12 rivnuts, 8 stop washers, 4 spigots; side band: 2 glides and doublers, 6 rivnuts, 4 stop washers, 2 spigots |
| Own clashes | 8 over 1 mm³, all expected (spigot studs in their rivnuts; key studs and screws in the key's tapped holes, tap drill modelled) |
| Skeleton clashes | 6, all expected (the spigots enter the walls' bottom tubes L1, B1, B2) |
| Wall stop height | stops at `panel_z0` 112.26 (D-64) |
| Cloud save | `110000_P01_BASE_CAD` in Default Project / FocusPod v2, one file of that name |
| STEP | `110000_P01_BASE_STEP.step` (cm, D-13), read back in Fusion: 63 occurrences, box X −1250.01…1217.83, Y −670.01…850.02, Z −0.03…118.03, largest difference 0.000 mm: MATCH |
| Part designs | 111101 (33 timeline items, 10 sketches, 1.669 kg, turned into its part system), 111103 (30, 10, 2.679 kg), 111601 (2, 1), 111401 (5, 2, 7.122 kg): each saved, exported to .f3d and STEP, STEP box MATCH |
| Edit test | PASS (see EDIT-TEST-RECORD.md) |
| Names in exports | none: the .f3d and STEP files, DXFs, CSVs and the data file scanned for account names and e-mail strings, 0 hits |

The mechanical check (`tools/checks/run_checks.py`) on run A's outputs then asked for three changes: the doubler's ends sat exactly on the 2-diameter line (next: 54 long, ends 27 from the hole), the foam's name must carry FOAM in its function field for D-89 part 3 (`BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM`), and the glide, glide nut and end cap take the joints register's names. The Lead merges this run with the three tracked; they follow on a new branch from main, with the front key's fixing holes moved by the Joints Engineer (3.4 mm toward the key's back face, so 2 diameters from the mitred end; no exception, Lead 2026-11-01).

## Earlier runs (no files kept)

- 18:02 to 18:43: stopped at the first keyhole sketch (two circles in one sketch over-constrained in Fusion). The keyholes are now two hole features and one slot cut.
- 19:35 to 20:03: the assembly saved and exported, then hung in the new cloud Save Copy As of the subassemblies; Fusion was restarted by Fusion Engineer 2. That step is left out; the subassembly designs for the assembly drawings come with the drawings.
