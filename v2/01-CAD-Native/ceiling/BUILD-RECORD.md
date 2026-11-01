# Build record: 410000 CEILING P01 (ceiling halves and the ceiling cassette)

Built 2026-11-01 on Mac 1, Fusion 2706.1.17, through the Fusion lock, in two runs so each stays well under the runner's call limit:

1. the build: `python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py --label "CEILING Engineer" --doc 410000_P01_CEILING_CAD --arg into_active=1 --arg save=1 --arg checks=0 --close --discard` (123 s for the geometry);
2. the checks and exports of the saved version: `python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_report.py --doc 410000_P01_CEILING_CAD --arg export=1 --label "CEILING Engineer" --close --discard`. It first brings the design's parameters up to `ceiling_model.py` (a reference update: this run set `cable_hole` to 19.1 mm, PM ruling 2026-11-01, and saved that as a new version before checking and exporting).

**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `410000_P01_CEILING_CAD` (version 8). Parameters: skeleton **P04 v4** (main, #94), loaded by name from `../skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv` with its `unit` column, plus the ceiling's own in `ceiling_model.py`. The joint lines are the skeleton's named values (`ceil_side_y0`, `ceil_side_pitch`, `n_ceil_side_bolt`, `ceil_back_x0`, `ceil_back_pitch`, `n_ceil_back_bolt`), which follow the joints register.

## Result

- timeline 326 items, unhealthy 0, loose sketches 0, user parameters 141, bodies 46
- clash pairs over 1 mm³: 0
- position check: all 46 bodies on their layout boxes, worst 0.000 mm
- hole check: 48 joint holes on the joints register's positions (from the skeleton's named values), worst 0.000 mm
- saved, then exported from the saved version:
  - `410000_P01_CEILING_CAD.f3d`
  - `v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step`: length unit cm, declared in the file (D-13). Re-read in Fusion (`step_reimport_check.py`): 46 bodies, box X −1201.76…1201.77, Y −645.03…850.03, Z 2315.98…2400.03 against the layout's −1201.74…1201.74, −645…850, 2316…2400: **MATCH** (0.03 mm).
  - the tray's flat pattern from Fusion (`.raw/`, git-ignored), put on the CUT / BEND / MARK layers by `ceiling_exports.py` as `513101_P01_LINING-TRAY-CEILING_DXF.dxf`
- no personal names in the STEP, the DXF files, the CSV files or any entry of the `.f3d` (scanned, zstd entries decompressed)

## The parts and where they are (pod system, mm)

| Part | Box or size | Mass each (Fusion) |
|---|---|---:|
| 411101 / 411102 frames C1 / C2 | X −1201.74…−2.75 / 2.75…1201.74, Y −645…850, Z 2354…2394 (the 3 mm bond line and the skin above); side and seam members 40 × 20 to Y 810, the back member 40 × 40 across, the front member, cross members X1 (Y −301…−281, 16 over the soffit's edge, so the soffit's room-side hanger studs land in it), X2 and X3; every joint hole of the register drilled in the members | 3.410 / 3.407 kg |
| 411301 / 411302 skins C1 / C2 | 1200.61 × 1495 × 3 ACP, Z 2397…2400; C2 with the 285 × 294 roof slot (D-61, X 872…1157, Y −620…−326) | 6.282 / 5.989 kg |
| 410101 / 410102 outer panels C1 / C2 | frame + skin + its share of the ACP bond set 108002 (0.503 kg, bond spec 0.28 kg/m², not modelled as a body) + its joint hardware and seals from the parts list (0.176 / 0.119 kg) | **10.371 / 10.018 kg** (20 kg or less, D-03) |
| 513101 tray | X ±580 about each cassette centre (−583 / +583), Y −282…763, Z 2316…2350; two Ø19.1 cable holes (ELECTRICAL's bushings, PM ruling 2026-11-01) | 5.520 kg |
| 513102 rib (2 per cassette) | hat 44 × 24, 1034 long, X′ ±193.33 | 0.369 kg |
| 513201 felt | 1157 × 1042 × 9 on the lips, Z 2316.5…2325.5, no holes | 2.170 kg |
| 513301 / 513302 / 513303 fill | 1110.5 × 363.5 / 338.75 / 271.75 × 40 at 25 kg/m³ (D-81), on the tray back, notched round the clips and catches | 0.398 / 0.373 / 0.299 kg |
| 518001 clip × 6, 518002 catch × 2 per cassette | HOLD envelopes in the CAD (no mass); the parts list carries the register's 0.040 and 0.100 kg each (assumption) | 0.040 / 0.100 kg |
| 510301 cassette | the above, with clips and catches | **9.938 kg** (20 kg or less) |
| 410000 ceiling | 2 outer panels + 2 cassettes | **40.26 kg** |

The cassette starts at Y −282: the D-60 soffit takes the front 360 mm under both halves (Y −645…−285) and the cassette keeps a 3 mm gap to it, so it is 1045 long (1160 wide).

## Joint holes (joints register, skeleton P04 v4)

| Edge | Holes per half | Where |
|---|---|---|
| side wall | 4 Ø7 bolt clearance holes in the side member's outer face (X ∓1201.74), 4 Ø19 key access holes in its inner face | horizontal, Z 2374 (the tube's centre, R-J15); Y −425, −73.33, 278.33, 630: from `ceil_side_y0` plus the 220 edge inset, pitch `ceil_side_pitch` 351.67 |
| closing seam | C1: 4 Ø7 pin clearance holes in the seam member's outer face; C2: 4 Ø9.53 rivnut holes in its seam member's outer face and 4 Ø19 access holes in the inner face | the same Y and Z as the side bolts (`cj_pin_n` at `cj_pin_pitch`) |
| back wall | 4 Ø9.53 rivnut holes in the back member's bottom face (Z 2354, Y 824, R-J15), a Ø8.5 spigot hole and an 8.5 × 14 spigot slot | C2: X 222.75, 475.75, 728.74, 981.74 on the back frame's pitch 253.00 (`ceil_back_x0`, `ceil_back_pitch`, `n_ceil_back_bolt`), spigots at X 102.75 (round) and 1101.74 (slot); C1 mirrored |
| soffit hangers (AIR) | 1 Ø9.53 rivnut hole in the front member's bottom face (Y −635) and 1 in X1's (Y −291), at X ∓583 (`hang_x`) | the soffit's four M6 × 16 studs (D-90) |
| soffit lock (AIR) | C1 only: 2 Ø9.53 rivnut holes in the front member's bottom face at X −1100 and −950, Y −635 | the soffit's two captive M6 × 25 lock screws |

Each hole is its own fully constrained sketch and cut (a pattern of identical holes failed to compute on these members, and a sketch with several circles on one plane over-constrained), with a 1 mm lead-in chamfer where a bolt enters.

## Flat pattern

Fusion's flat pattern of the tray: **1248.53 × 1133.52 mm**. The K-factor calculation in `ceiling_model.tray_flat()` (K 0.44, r = t = 0.5, outside setback r + t on each straight, bend allowance π/2 · (r + K·t) = 1.131) gives **1248.52 × 1133.52**: the same to 0.01 mm. K and r are assumptions until a bend coupon on the factory's tooling sets them (guideline §9).

## How the design is built

- One component per part, with part number, name and the Vietnamese name in its description. Repeated parts are one component with several occurrences: the cassette (C1-CASS, C2-CASS), the ribs, the clip and catch spaces.
- Every sketch is fully constrained on a construction plane offset by a parameter expression; every feature is named by its function.
- Every occurrence that a parameter places is held by a rigid joint to a sketch point dimensioned by expressions, so placements follow the parameters (edit test: `EDIT-TEST-RECORD.md`).
- The tray is a sheet metal component (rule "GALV STEEL 0.5 - CEILING TRAY": 0.5 mm, bend radius = thickness, K 0.44, square corner relief): base flange, four returns (inside bend position, so their outer faces sit on the 1160 × 1045 outline), four lips turned in under the felt with mitred corners, two Ø19.1 cable holes.
- The skeleton's numbers are read from its CSV, by name and with their units; the ceiling's own parameters carry their status and source in the Fusion parameter comment.

## Master BOM check

`python3 v2/04-BOM/build_master_bom.py --no-write` on this branch: **OK** (no part without a number or a mass, no duplicate number, no unregistered hardware). The parts list carries size, tolerance, maker and SKU on each row, so the row is the cut list for the flat parts (D-89 part 4); the tube cut list is the frames' own.

## Not in this build yet

- Frame member joints: internal cleats per D-115 (corner and T cleats, crimped, with structural adhesive; no welds): the cleats are the Joints Engineer's register entries and models, placed by reference when they land (until then the frames' notes say so).
- Drawings (D-91: they follow this PR): made from part-only designs built by the same script (`parts=`), because a Fusion drawing always shows its whole design; specs in `../../02-Drawings/ceiling/drawing_specs.py`. The skins and the plain felt get no drawing (D-89 part 4: their DXF and parts-list row are enough); the three fill strips share one tabulated drawing (D-89).
- HOLD, drawn as space only: the clip (H03), the safety catch (H04), the felt fixing to the lips and ribs (H09), the fill fixing (H10), the cable grommet.
- The soffit, the air column and their parts are AIR's (`../air/`, PR #91); the light shelf, ledge and screen rail are INTERIOR's (`../interior/`, PR #92).
