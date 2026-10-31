# Build record: 410000 CEILING P01 (ceiling halves and the ceiling cassette)

Run 2026-10-31 on Mac 1, Fusion 2706.1.17, through the Fusion lock:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py --label "CEILING Engineer" --doc 410000_P01_CEILING_CAD --doc-new --arg into_active=1 --arg save=1 --arg export=1 --close --discard`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `410000_P01_CEILING_CAD` (version 3). Parameters: skeleton **P03** (main), loaded from `../skeleton/100000_P03_POD-SKELETON-PARAMETERS.csv`, plus the ceiling's own (`ceiling_model.py`).

## Result

- timeline 168 items, unhealthy 0, loose sketches 0, user parameters 97, bodies 46
- clash pairs over 1 mm³: 0
- position check: all 46 bodies on their layout boxes, worst 0.000 mm
- saved: True; exports from the saved version:
  - `410000_P01_CEILING_CAD.f3d`
  - `v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step`: length unit cm, declared in the file (D-13). Re-read in Fusion (`step_reimport_check.py`): 46 bodies, box X −1204.76…1204.77, Y −645.03…850.03, Z 2318.98…2400.03 against the layout's −1204.74…1204.74, −645…850, 2319…2400: **MATCH** (0.03 mm). `tools/fusion/step_check.py` confirms the unit and the 16 product names; its own box assumes every component at the origin, which this design doesn't use (common parts are placed by assembly transforms), so the box check is the Fusion re-read.
  - the tray's flat pattern from Fusion (`.raw/`, git-ignored), put on the CUT / BEND / MARK layers by `ceiling_exports.py` as `513101_P01_LINING-TRAY-CEILING_DXF.dxf`
- no personal names in the STEP, the DXF files, the CSV files or any of the 64 entries of the `.f3d` (scanned, zstd entries decompressed)

## The parts and where they are (pod system, mm)

| Part | Box or size | Mass each (Fusion) |
|---|---|---:|
| 411101 / 411102 frames C1 / C2 | X −1204.74…−1.13 / 1.13…1204.74, Y −645…850, Z 2357…2397; 7 members each, cross members at 368.75 | 3.288 kg |
| 411301 skin, both halves | 1203.61 × 1495 × 3, Z 2397…2400 | 6.298 kg |
| 410101 / 410102 outer panel C1 / C2 | frame + skin | **9.586 kg** (20 kg or less, D-03) |
| 513101 tray | X ±581.5 about each cassette centre (−584.5 / +584.5), Y −282…766, Z 2319…2353 | 5.548 kg |
| 513102 rib (2 per cassette) | hat 44 × 24, 1037 long, X′ ±193.83 | 0.370 kg |
| 513201 felt | 1160 × 1045 × 9 on the lips, Z 2319.5…2328.5, no holes | 2.182 kg |
| 513301 / 513302 / 513303 fill | 1116.74 × 338.75 / 338.75 / 274.75 × 40, on the tray back | 0.477 / 0.480 / 0.389 kg |
| 518001 clip, 518002 catch | HOLD envelopes, no mass | — |
| 510301 cassette | the above | **9.816 kg** plus clips and catches (20 kg or less) |
| 410000 ceiling | 2 outer panels + 2 cassettes | **38.80 kg** plus clips and catches |

The cassette starts at Y −282: the D-60 soffit takes the front 360 mm under both halves (Y −645…−285) and the cassette keeps a 3 mm gap to it. The layout study's 13.2 kg cassette was the full 1414 length with no soffit.

## Flat pattern

Fusion's flat pattern of the tray: **1251.53 × 1136.52 mm**. The K-factor calculation in `ceiling_model.tray_flat()` (K 0.44, r = t = 0.5, outside setback r + t on each straight, bend allowance π/2 · (r + K·t) = 1.131) gives **1251.52 × 1136.52**: the same to 0.01 mm. K and r are assumptions until a bend coupon on the factory's tooling sets them (guideline §9).

## How the design is built

- One component per part, with part number, name and the Vietnamese name in its description. Repeated parts are one component with several occurrences: the cassette (C1-CASS, C2-CASS), the skin, the ribs, the clip and catch spaces.
- Every sketch is fully constrained on a construction plane offset by a parameter expression; every feature is named by its function.
- Every occurrence that a parameter places is held by a rigid joint to a sketch point dimensioned by expressions, so placements follow the parameters (edit test: `EDIT-TEST-RECORD.md`).
- The tray is a sheet metal component (rule "GALV STEEL 0.5 - CEILING TRAY": 0.5 mm, bend radius = thickness, K 0.44, square corner relief): base flange, four returns (inside bend position, so their outer faces sit on the 1163 × 1048 outline), four lips turned in under the felt with mitred corners, two Ø20 cable holes.
- The skeleton's numbers are read from its CSV, by name; the ceiling's own parameters carry their status and source in the Fusion parameter comment.

## Ready for the next skeleton

Skeleton P04 (PR #24, open) moves the outer panel to 46 mm (3 ACP + 3 bond line + 40 frame), the stack to 84 mm and every frame seam to 2.26 mm. The ceiling already follows it: with P04's list the offline checks pass and give frames 1200.61 wide (the skeleton's `half_pw`), the frame at Z 2354…2394 under a 3 mm bond line, the cassette 1160 × 1045 at Z 2316…2350. When P04 merges, this design is rebuilt from the same script and these records are redone.

## Not in this build yet

- Drawings: D06 (the cassette) and the tray, waiting for the shared no-click drawing start in `tools/fusion` (Fusion Engineer 2); see `../../02-Drawings/ceiling/`.
- HOLD, drawn as space only: the clip (H03), the safety catch (H04), the felt fixing to the lips and ribs (H09), the fill fixing (H10), the frame member joints (H11), the joints to the walls, to the other half and to the top decor block (joints register), the cable grommet.
- Next PRs: the roof slot in the right outer panel (D-60; the two skins then become two parts), the soffit and the air column with their cartridges and the hub zone, the interior parts, and the wall-top light shelf.
