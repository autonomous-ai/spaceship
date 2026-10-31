# Build record: 410000 CEILING P01 (ceiling halves and the ceiling cassette)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the Fusion lock:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py --label "CEILING Engineer" --doc 410000_P01_CEILING_CAD --doc-new --arg into_active=1 --arg save=1 --arg export=1 --close --discard`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `410000_P01_CEILING_CAD` (version 5). Parameters: skeleton **P04** (main, 0cb764f), loaded from `../skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv`, plus the ceiling's own (`ceiling_model.py`). P04 brings the 46 mm outer panel (3 ACP + 3 bond line + 40 frame), the 84 mm stack and the 2.26 mm seam gap; the ceiling takes them from the skeleton's list (`half_pw`, `seam_gap`, `outer_t`, `stack_t`).

## Result

- timeline 168 items, unhealthy 0, loose sketches 0, user parameters 101, bodies 46
- clash pairs over 1 mm³: 0
- position check: all 46 bodies on their layout boxes, worst 0.000 mm
- saved: True; exports from the saved version:
  - `410000_P01_CEILING_CAD.f3d`
  - `v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step`: length unit cm, declared in the file (D-13). Re-read in Fusion (`step_reimport_check.py`): 46 bodies, box X −1201.76…1201.77, Y −645.03…850.03, Z 2315.98…2400.03 against the layout's −1201.74…1201.74, −645…850, 2316…2400: **MATCH** (0.03 mm). `tools/fusion/step_check.py` confirms the unit and the 16 product names; its own box assumes every component at the origin, which this design doesn't use (common parts are placed by assembly transforms), so the box check is the Fusion re-read.
  - the tray's flat pattern from Fusion (`.raw/`, git-ignored), put on the CUT / BEND / MARK layers by `ceiling_exports.py` as `513101_P01_LINING-TRAY-CEILING_DXF.dxf`
- no personal names in the STEP, the DXF files, the CSV files or any of the 64 entries of the `.f3d` (scanned, zstd entries decompressed)

## The parts and where they are (pod system, mm)

| Part | Box or size | Mass each (Fusion) |
|---|---|---:|
| 411101 / 411102 frames C1 / C2 | X −1201.74…−1.13 / 1.13…1201.74, Y −645…850, Z 2354…2394 (the 3 mm bond line and the skin above); 7 members each, cross members at 368.75 | 3.282 kg |
| 411301 skin, both halves | 1200.61 × 1495 × 3, Z 2397…2400 | 6.282 kg |
| 410101 / 410102 outer panel C1 / C2 | frame + skin + its share of the ACP bond set 108002 (0.503 kg, bond spec 0.28 kg/m², not modelled as a body) | **10.067 kg** (20 kg or less, D-03) |
| 513101 tray | X ±580 about each cassette centre (−583 / +583), Y −282…763, Z 2316…2350 | 5.520 kg |
| 513102 rib (2 per cassette) | hat 44 × 24, 1034 long, X′ ±193.33 | 0.369 kg |
| 513201 felt | 1157 × 1042 × 9 on the lips, Z 2316.5…2325.5, no holes | 2.170 kg |
| 513301 / 513302 / 513303 fill | 1113.74 × 338.75 / 338.75 / 271.75 × 40 at 25 kg/m³ (D-81), on the tray back | 0.371 / 0.374 / 0.300 kg |
| 518001 clip × 6, 518002 catch × 2 per cassette | HOLD envelopes in the CAD (no mass); the parts list carries the register's 0.040 and 0.100 kg each (assumption) | 0.040 / 0.100 kg |
| 510301 cassette | the above, with clips and catches | **9.913 kg** (20 kg or less) |
| 410000 ceiling | 2 outer panels + 2 cassettes | **39.96 kg** |

The cassette starts at Y −282: the D-60 soffit takes the front 360 mm under both halves (Y −645…−285) and the cassette keeps a 3 mm gap to it, so it is 1045 long (1160 wide). The layout study's 13.2 kg cassette was the full length with no soffit.

## Flat pattern

Fusion's flat pattern of the tray: **1248.53 × 1133.52 mm**. The K-factor calculation in `ceiling_model.tray_flat()` (K 0.44, r = t = 0.5, outside setback r + t on each straight, bend allowance π/2 · (r + K·t) = 1.131) gives **1248.52 × 1133.52**: the same to 0.01 mm. K and r are assumptions until a bend coupon on the factory's tooling sets them (guideline §9).

## How the design is built

- One component per part, with part number, name and the Vietnamese name in its description. Repeated parts are one component with several occurrences: the cassette (C1-CASS, C2-CASS), the skin, the ribs, the clip and catch spaces.
- Every sketch is fully constrained on a construction plane offset by a parameter expression; every feature is named by its function.
- Every occurrence that a parameter places is held by a rigid joint to a sketch point dimensioned by expressions, so placements follow the parameters (edit test: `EDIT-TEST-RECORD.md`).
- The tray is a sheet metal component (rule "GALV STEEL 0.5 - CEILING TRAY": 0.5 mm, bend radius = thickness, K 0.44, square corner relief): base flange, four returns (inside bend position, so their outer faces sit on the 1160 × 1045 outline), four lips turned in under the felt with mitred corners, two Ø20 cable holes.
- The skeleton's numbers are read from its CSV, by name; the ceiling's own parameters carry their status and source in the Fusion parameter comment.

## Master BOM check

`python3 v2/04-BOM/build_master_bom.py --ref origin/main --ref HEAD` reads `410000_P01_CEILING-PARTS-LIST_BOM.csv` with no failure of its own: the CEILING section lists only the two HOLD items, the clip 518001 and the catch 518002 (joints register H-10, H-11). The tube cut list has no part number column and is skipped, as the check intends. The check's failures on that run all come from the packing list (`v2/07-Packaging/`), whose rows carry no masses yet.

## Not in this build yet

- Drawings: made from part-only designs built by the same script, because a Fusion drawing always shows its whole design (`tools/fusion/README.md`); see `../../02-Drawings/ceiling/`.
- HOLD, drawn as space only: the clip (H03), the safety catch (H04), the felt fixing to the lips and ribs (H09), the fill fixing (H10), the frame member joints (H11), the joints to the walls, to the other half and to the top decor block (joints register), the cable grommet.
- Next PRs: the roof slot in the right outer panel (D-60; the two skins then become two parts), the soffit and the air column with their cartridges and the hub zone, the interior parts, and the wall-top light shelf.
