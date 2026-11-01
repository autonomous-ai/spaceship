# Build record: BASE native CAD, samples P01 and P02

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-BR | P02 | DRAFT | 2026-11-01 | BASE Engineer |

How the sample's native files were made, and what each build checked (guideline §4.5, §10). Every run goes through `tools/fusion/run_script.py` (the shared Fusion lock) with the late-binding loader `late_base.py`, which reads the scripts only when the lock is granted. Fusion build b43a07003c01.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py --timeout 2700 \
  --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
  --arg save=1 --arg replace=1 --arg export=1 --arg also_parts=<part keys>
python3 v2/03-Manufacturing/base/make_outputs.py --dxf
```

## Run A, 2026-10-31 20:06 to 20:14 UTC: assembly, 4 part designs, edit test

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

The mechanical check (`tools/checks/run_checks.py`) on run A's outputs then asked for three changes: the doubler's ends sat exactly on the 2-diameter line (54 long in run B, ends 27 from the hole), the foam's name must carry FOAM in its function field for D-89 part 3 (`BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM`), and the glide, glide nut and end cap take the joints register's names. The Lead merged run A (PR #55) with the three tracked; run B makes them, on a new branch from main, with the corner keys of joints register #127.

## Run B, 2026-10-31 20:57 to 21:04 UTC: the tracked fixes, the 30 mm keys, subassembly designs

Same checks as run A, all passing: 169 timeline items healthy, 33 sketches fully constrained, own clashes 8 (all expected), skeleton clashes 6 (all expected), STEP re-read 0.000 mm (63 occurrences), edit test PASS (largest difference after the revert 0.0000 mm).

| Change | Result |
|---|---|
| Glide doubler 54 long (ends 27 from the hole) | 111601 part design X ±18, Y ±27, Z 0…3, 0.0147 kg; DXF 36.0 × 54.0, hole Ø13 at the centre |
| Foam renamed `BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM` (D-89 part 3 reads the FOAM function) | DXF `111501_P01_BASE-FLOOR-FOAM-F1-CLOSED-CELL-3-MM_DXF.dxf` |
| Register names: glide 118002, glide nut 838006 (and its finish), end cap 118003 | parts list |
| Corner keys 30 long, fixing holes 10.5 from the key's back face (joints register #127) | back band X ∓1190.5, Y 830 ± 7.0; left band's front end X −1237 and −1223, Y −641.53. Part designs 111101 and 111103 rebuilt with them, STEP MATCH |
| Subassembly designs for the assembly drawings (by rebuilding and trimming, not Save Copy As) | 110101 and 110401 saved. 110103 failed its health check after the trim (its rivnuts and stop washers are pasted copies of the side band's), so a trim now hides that host instead of deleting it; 110103 follows in the next run |

## Run C, 2026-11-01 07:10 to 07:18 UTC: P02 batch 1, D-129's back corners, D-132 (no floor), the 5 mm load blocks; the edit test in the same run

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py --timeout 3600 \
  --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
  --arg save=1 --arg replace=1 --arg export=1 --arg scope=p02 --arg sub_list=band_b --arg also_parts=doubler
python3 v2/03-Manufacturing/base/make_outputs.py --dxf
```

| What | Result |
|---|---|
| Parameters | 88 skeleton P04 parameters (update 5, `pod_skeleton.py`: no floor, D-132) and 78 BASE parameters (P02's added, `base_p02.py`) |
| Timeline | 260 items, all healthy (a STEP import's group is judged by its members) |
| Sketches | 54, all fully constrained |
| Part boxes | side band LH X −1250…−1210, Y −670…850; back band X −1210…1210, Y 810…850; side band RH X 1210…1250, Y −672…850; FR1 X 218.46…915, Y −850…−810; sill X 218.46…965, Y −810…−689.5; all Z 10…110 (the bands on `glide_h`) |
| Holes | side bands: 6 rivnut holes each (spigots at Y −542.74 and 750); the back key's 2 stud bolt holes Ø7.0 in the inner wall and 2 fixing holes Ø7.0 in the bottom wall at each back end; the LH front key's fixing holes at Y −641.53; glides at Y −595 (LH) / −597 (RH) and 700. Back band: 12 rivnut holes on Y 824; glides at X −1060, 0, 1060; end plate slots, head notches and bevels at both ends (D-129). FR1: 2 keyholes in its end plate at X 915, 2 glide nut holes |
| Back corners (D-129) | both: fixing holes, stud bolt holes, key position and the back band's slot end MATCH `corner-keys.csv` |
| Base seal (D-132) | 4 runs of the lip's envelope on the band pieces' inner faces: LH 1462.07, back 2420.00, RH 1464.17, FR1 696.54 mm |
| Own clashes | 8 over 1 mm³, all expected (spigot studs in their rivnuts; key studs and screws in the key's tapped holes) |
| Skeleton clashes | 8, all expected (the spigots enter the walls' bottom tubes L1, R1, B1, B2) |
| Wall stop height | band top Z 110 = `wall_z0`; stop top Z 112.26 = `panel_z0` (D-64) |
| Cloud save | `110000_P01_BASE_CAD` in Default Project / FocusPod v2; the previous copy renamed `110000_P01_BASE_CAD_SUPERSEDED-2026-11-01` (cloud files are never deleted, PM rule); one file of the name after the save |
| STEP | `110000_P01_BASE_STEP.step` (cm, D-13), read back in Fusion: 92 occurrences, box X −1250.01…1250.02, Y −850.02…850.03, Z −0.03…118.03, largest difference 0.000 mm: MATCH |
| Part designs | 111601 (5 mm, 0.0245 kg), 111101 (1.6726 kg, in its part system), 111103 (2.7044 kg), 111102 (1.6749 kg): each saved (the old copy superseded), exported to .f3d and STEP, STEP box MATCH; 110103's own design for its assembly drawing (the rest of BASE hidden) |
| Edit test | PASS in the same run (see EDIT-TEST-RECORD.md) |
| Outputs | parts list 46 rows, P02 scope 10.68 kg; cut list; DXFs of the load block (36 × 54, Ø13) and the sill's flat pattern (746.54 × 250.09) |
| Names in exports | none: the .f3d entries (zstd, decompressed), STEP, CSV, JSON and DXF files scanned for the account's names and e-mail words |

The sill 111301's own design and STEP are made again in a separate run (its kerb now ends on the band's bottom line, D-132), so its STEP matches its copy in the assembly.

## Run D, 2026-11-01 10:54 to 11:01 UTC: Reviewer 8's Hold on #303 (D-150: the sill's closed door end and its lip); the edit test in the same run

A short run at the front of the queue (the PM's approval, once): the assembly, its STEP and data, the sill's own design and the edit test. The band tubes' own designs aren't rebuilt (`with_assembly=0`): this change leaves their holes as run C made them, so their designs and STEPs stay current.

```
python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py --timeout 3600 --lock-front "PM approved: ..." \
  --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
  --arg save=1 --arg replace=1 --arg export=1 --arg scope=p02 --arg also_parts=sill --arg with_assembly=0
python3 v2/03-Manufacturing/base/make_outputs.py --dxf
```

| What | Result |
|---|---|
| Change | The sill 111301's door end closed by a welded 2 mm plate (D-150), one body with the sill; the lip 118001 along the plate's bottom edge (its envelope one L section: the leg on the pod side, the fin under the plate, flush with its outer face); FR1's lip from the plate's pod side; the back band's lip run = its envelope (2.400 m) |
| Timeline | 267 items, all healthy |
| Sketches | 56, all fully constrained |
| Part boxes | as run C; sill X 218.46…965, Y −810…−689.5, Z 10…110 (the plate is inside that box) |
| Back corners (D-129) | stud bolt holes, key position and the back band's slot end MATCH `corner-keys.csv`; the fixing holes are the layout before D-144 (MATCH with the file before #300), as Joints' 111211 STEP still has it: D-144 comes on the next branch |
| Base seal (D-132, D-150) | 5 runs: LH 1462.07, back 2400.00, RH 1464.17, the sill's door end 108.50 (Y −800 to −691.5), FR1 694.54 (from X 220.46) mm |
| Own clashes | 8 over 1 mm³, all expected (as run C); the plate, the two lips and the sill only touch |
| Skeleton clashes | 8, all expected (the spigots enter L1, R1, B1, B2) |
| Cloud save | `110000_P01_BASE_CAD` saved; the previous copy renamed `..._SUPERSEDED-2026-11-01-2` (never deleted) |
| STEP | `110000_P01_BASE_STEP.step` (cm, D-13), read back in Fusion: 93 occurrences (one more lip envelope), box X −1250.01…1250.02, Y −850.02…850.03, Z −0.03…118.03, largest difference 0.000 mm: MATCH |
| Part design | 111301: timeline 13 items, healthy; 4 sketches; 1.0945 kg; saved (the old copy renamed `_SUPERSEDED-2026-11-01-2`), exported, STEP box MATCH. Offline (OCC): one solid, 405 382 mm³ = the profile 513 mm² × 746.54 + the plate 11 282 mm² × 2 − 4 rivnut holes Ø5 × 2 |
| Edit test | every part we make follows all three edit sets, and every one comes back exactly on the revert (EDIT-TEST-RECORD.md). The run then stopped on the test's last line: it switched back to the build's document, which the build had already closed after saving. Fixed in `base_edit_test.py`; the checks themselves had all passed |
| Outputs | parts list 46 rows, P02 scope 10.75 kg; the sill's DXF: the flat pattern 746.54 × 250.09 and the door-end plate's blank 118.5 × 98.0, its 3 corners at inside bends relieved C3; the cut list unchanged |
| Names in exports | none: the two .f3d files (zstd entries decompressed), both STEPs (author and organization empty), the DXF, CSV and data file |

The first try (10:40 UTC, queued at 10:05) stopped in step 6: the lip's fin, extruded as a second body and joined to the leg, stayed a second body. Nothing was saved, and the run closed its own document. The envelope is now one L-section extrude.

## Earlier runs (no files kept)

- 18:02 to 18:43: stopped at the first keyhole sketch (two circles in one sketch over-constrained in Fusion). The keyholes are now two hole features and one slot cut.
- 19:35 to 20:03: the assembly saved and exported, then hung in the new cloud Save Copy As of the subassemblies; Fusion was restarted by Fusion Engineer 2. That step is left out; the subassembly designs for the assembly drawings come with the drawings.
- 2026-11-01 06:17: the first P02 run stopped in step 6: the four lip seal envelopes share one part number, so a component lookup by number put two in one component; components are now kept by key.
- 2026-11-01 06:55: stopped in step 9: reading the index of a STEP import group's members raised an InternalValidationError in Fusion; the health check no longer reads indexes. The run closed its own unsaved document on the way out.
