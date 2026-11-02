# Build record: 810000 INTERIOR P01 (light shelf, work wall ledge, screen rail)

Run 2026-11-01 12:41 to 12:43 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock (one held session), from commit
4736349: first a dry run in a new unsaved design (D-118: the fold fillets are new here; every check below, closed
without saving), then the build in place:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/interior_build.py --arg own_doc=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `810000_P01_INTERIOR_CAD`, rebuilt in place as a new
version (the first build, 2026-10-31 19:35 UTC, made it; the D-126 rebuild ran 2026-11-01 05:45 to 05:52 UTC, the
Checker's 07:28 to 07:35).
Parameters: skeleton P04 v4 and the ceiling's, loaded from their lists, plus INTERIOR's own (`interior_model.py`).

What changed in this rebuild (the Lead's request 2026-11-01, for the drawing generator's bent sheet mode #335): each
fold of the ledge top 811101 and the light shelf 811201 to 811203 is a real fold, its inside corner filleted to the
sheet (`lg_r`, `sh_r`) and its outside corner to twice the sheet (the Lead's ruling: inside radius = the sheet); the
ledge brackets' envelopes 818101 have a 45° relief of 2 × `lg_t` on their top back edge, clear of the ledge's inside
fold; the DXFs of 811201 and 811203 put the Ø10 cable hole 20 from the back flange's free edge (y 20), where the model
has it (it was at y 96.52, in the second fold's zone); the parts list says 2 bends. The flats keep their sizes.

What the Checker's 07:28 rebuild changed (its notes on #285): the ledge top, its two brackets and the screen rail stand
5 mm off the lining's face (calculation: D-17 and D-57's 4 mm, plus 1 mm for the felt's tolerance; the mechanical
check LINING-FLOATS had found the ledge 2.0 mm from the lower side cassette's tray). The ledge now runs X 911 to 1161
and the rail X 1136 to 1161, with the lining's face at X 1166; the ledge keeps its size. The LED profile carries
ELECTRICAL's exact name, 718101 ELECTRICAL - LED PROFILE - LIGHT SHELF - SURFACE 23 X 12.5.

What the D-126 rebuild changed: the down-light is D-126's bought LED profile, modelled under ELECTRICAL's
718101 (23 x 12.5, two 8 mm strips inside) under the right side run for that run's 991, with D-127's satin cover; the
folded down channel 811204 and the cut diffuser 811205 are gone (cancelled by Control); the root component carries
810000 as its part number, so the STEP's root product is 810000 (F-159).

## Result

- timeline 41 items, unhealthy 0, loose sketches 0, user parameters 173, bodies 8 (the dry run the same)
- clash pairs over 1 mm³: 0
- position check: all 8 bodies on their layout boxes, worst 0.000 mm; ledge top X 911…1161, screen rail X 1136…1161,
  ledge brackets X 961…1159.5
- fold check: the 16 fold faces of the four bent parts (two folds each, inside and outside) at their radii: 1.0 and
  2.0 on the shelf, 1.5 and 3.0 on the ledge
- saved: True; exports from the saved version: `810000_P01_INTERIOR_CAD.f3d`, `v2/03-Manufacturing/interior/810000_P01_INTERIOR_STEP.step`
- STEP (`tools/fusion/step_check.py`): length unit cm, declared in the file (D-13); 10 products, the root 810000 and
  718101, 810101, 810201, 811101, 811201, 811202, 811203, 818101, 818102; 8 solids; box X −1166…1166, Y −285…766,
  Z 915.5…2270, as the layout (every component sits at the origin, so the box holds)
- no personal names in the STEP, the DXF and CSV files or any of the 39 entries of the `.f3d` (zstd entries decompressed)

## Masses (Fusion, CAD geometry × density)

| Part | Mass |
|---|---:|
| 811101 ledge top, 1.5 folded aluminium | 1.195 kg |
| 818101 ledge bracket × 2 (HOLD; parts list 0.10 each) | — |
| 810101 ledge assembly | **1.395 kg** (D-85: 1.4) |
| 811201 light shelf, back run | 0.735 kg |
| 811202 / 811203 side runs | 0.312 kg each |
| 718101 LED profile (ELECTRICAL's line and mass; modelled for its place only) | — |
| 810201 light shelf assembly | **1.359 kg** over 4.31 m: 0.32 kg/m; about 0.40 kg/m with ELECTRICAL's profile set (718101 to 718104) and its 6.38 m of strip 718050 at their parts list's assumed masses (calculation), inside D-126's 0.41 kg/m |
| 818102 screen rail (HOLD; parts list 0.5) | — |
| 810000 INTERIOR | **3.254 kg** (parts list, sum of its parts) |

## Exports (`interior_exports.py` on this run's log)

- `810000_P01_INTERIOR-PARTS-LIST_BOM.csv`: 9 rows with size, tolerance, maker and SKU or HOLD (the profile set is ELECTRICAL's lines)
- DXF flat blanks of the folded parts (K-factor 0.44, r = t; CUT outline, BEND lines, the cable holes): 811101 (294.79 × 1000), 811201 (116.52 × 2332), 811202 and 811203 (116.52 × 991)
- The DXFs of 811101 and 811202 come out the same; 811201's and 811203's move their cable hole to y 20. Drawn in the
  generator's bent sheet mode (#335, a scratch merge with main), all four read back PASS from the model's own folds.

## Not in this build yet

- (done) Edit test: `EDIT-TEST-RECORD.md`, PASS on this build (12:42 UTC): pod_w, wall_depth, cs_front, sh_z0, lg_z,
  sh_t and lg_t, every body to 0.0 mm and every fold face at its radius.
- Drawings: the four folded parts (811101, 811201, 811202, 811203) come from the drawing generator's bent sheet mode
  (D-139, D-158; #335), in `../../02-Drawings/interior/`. The GA and the two assembly sheets (810000, 810101, 810201)
  wait for the generator's assembly mode; Fusion draws none of these.
- HOLD: the ledge brackets and their stand-offs, the screen rail, the shelf's fixing to the wall cassettes (WALL interfaces).
