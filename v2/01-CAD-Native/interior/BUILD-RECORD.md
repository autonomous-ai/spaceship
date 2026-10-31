# Build record: 810000 INTERIOR P01 (light shelf, work wall ledge, screen rail)

Run 2026-10-31 19:35 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/interior_build.py --arg own_doc=1 --arg create=1 --arg new_name=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `810000_P01_INTERIOR_CAD` (made by this run, a name never used before; PM ruling 2026-11-01). Parameters: skeleton P04 v4 (main, PR #94) and the ceiling's, loaded from their lists, plus INTERIOR's own (`interior_model.py`).

## Result

- timeline 38 items, unhealthy 0, loose sketches 0, user parameters 170, bodies 9
- clash pairs over 1 mm³: 0
- position check: all 9 bodies on their layout boxes, worst 0.000 mm
- saved: True; exports from the saved version: `810000_P01_INTERIOR_CAD.f3d`, `v2/03-Manufacturing/interior/810000_P01_INTERIOR_STEP.step`
- STEP (`tools/fusion/step_check.py`): length unit cm, declared in the file (D-13); 9 solids; box X −1166…1166, Y −285…766, Z 915.5…2270, as the layout (every component sits at the origin, so the box holds)
- no personal names in the STEP, the DXF and CSV files or any of the 41 entries of the `.f3d` (zstd entries decompressed)

## Masses (Fusion, CAD geometry × density)

| Part | Mass |
|---|---:|
| 811101 ledge top, 1.5 folded aluminium | 1.203 kg |
| 818101 ledge bracket × 2 (HOLD; parts list 0.10 each) | — |
| 810101 ledge assembly | **1.40 kg** (D-85: 1.4) |
| 811201 light shelf, back run | 0.743 kg |
| 811202 / 811203 side runs | 0.316 kg each |
| 811204 down channel RH | 0.139 kg |
| 811205 diffuser RH | 0.050 kg |
| 810201 light shelf assembly | **1.56 kg** over 4.31 m: 0.36 kg/m, about 0.39 with ELECTRICAL's strips (D-85: 0.4) |
| 818102 screen rail (HOLD; parts list 0.5) | — |

## Exports (`interior_exports.py` on this run's log)

- `810000_P01_INTERIOR-PARTS-LIST_BOM.csv`: 11 rows with size, tolerance, maker and SKU or HOLD
- DXF flat blanks of the folded parts (K-factor 0.44, r = t; CUT outline, BEND lines, the cable holes): 811101 (294.79 × 1000), 811201 (116.52 × 2332), 811202 and 811203 (116.52 × 991), 811204 (50.52 × 991)

## Not in this build yet

- Edit test: `edit_test_interior.py` (pod_w, wall_depth, cs_front, sh_z0, lg_z), queued.
- Drawings (D-89 parts 1 to 4): GA, ledge and shelf assemblies, ledge top, back run, side runs (tabulated), down channel: specs ready in `../../02-Drawings/interior/`, waiting for drawing starts.
- HOLD: the ledge brackets and their stand-offs, the screen rail, the shelf's fixing to the wall cassettes (WALL interfaces).
