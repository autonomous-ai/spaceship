# Build record: 410000 CEILING P01 (ceiling halves and the ceiling cassette)

Built 2026-11-01 17:59:13 to 18:08:11 UTC on Mac 1, Fusion 2706.1.17, through the Fusion lock (one held session), from commit f3072f6 (#348's fix for Reviewer 17's Hold) with main's runner (#386, #402, #410) in the checkout, in one run that builds, checks the design before it saves, saves, and exports from the design it saved:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py --label "CEILING Engineer" --doc 410000_P01_CEILING_CAD --arg into_active=1 --arg save=1 --arg checks=1 --arg export=1 --close --discard`.
It opened version 12 and saved version 13. Version 11 (14:52) checked a reopened copy that turned out to be version 10 (Fusion reopened the cloud file four seconds after the save), so its outputs weren't used; checking before the save and exporting from the same run keeps every number here on the saved design.

The method was proven first, on unsaved designs (D-118): turned-copy probes 2 to 11, then a dry run of the whole build at 09:58 UTC; versions 9 to 12 passed the same checks. Version 13 changes one parameter of a proven cut (the skin holes' size). What version 12 added uses proven methods: the rib's folds are fillets on its fully constrained section (as INTERIOR's ledge and shelf, #356), the D-163 holes change one parameter, and DT's bolt holes are the ceiling's own `circle_cut_y` holes, one sketch and one cut each, as every joint hole.

**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `410000_P01_CEILING_CAD` (version 13; version 12 had Ø10.00 holes under the roof sleeve's rivnuts, version 10 the 9.53 holes, square rib corners and no DT bolts). Parameters: skeleton **P04 v4** (main, #94), loaded by name from `../skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv` with its `unit` column, plus the ceiling's own in `ceiling_model.py`. The joint lines are the skeleton's named values (`ceil_side_y0`, `ceil_side_pitch`, `n_ceil_side_bolt`, `ceil_back_x0`, `ceil_back_pitch`, `n_ceil_back_bolt`), which follow the joints register; DT's bolt line is J-FRONT-03's (`dt_x1`, `dt_bolt_n`, `dt_pitch`).

## What version 13 changes

- **D-177 (PM ruling 2026-11-02, Reviewer 17's P1 on #348):** C2's four holes under the roof sleeve's factory-set rivnuts are Ø17 clearance holes (`hole_slv`), not the rivnut's own Ø10.00. Each passes a set rivnut, its 9.91 body and the bulge (about 14, an assumption) that forms right under the 1 mm flange in the skin's hole, wherever the sleeve lands in its slot: 14 + 2 × (1.0, the sleeve's play a side, which AIR's walls take, + 0.5 for the two holes' positions). At full play the back pair's bodies clear cross member 1 by 1.5, and the flange covers each hole with 10.0 outside it, room for AIR's 8-wide butyl ring (J-AIR-03), which closes the holes and the sleeve's gap (REQ-VCK-06). Rationale F-4113-04. Nothing else in the model moves; the four new parameters make 161.

## What version 12 changed

- **D-163:** every 838003 rivnut hole is Ø10.00 +0.10 (Sherex CAL2-610-4.2, the knurled round body; it was the half-hex CAH2's Ø9.53): the back members' 8, C2's seam rivnuts 4, the soffit's hanger and lock rivnuts 8, C2's skin under the roof sleeve's 4.
- **DT's bolts (J-FRONT-03):** 4 Ø7.0 holes in the front members' front wall (Y −645) into DT's rivnuts, each with a Ø19 access hole in the back wall reached from the open bay: X −981.74, −578.16, −174.58 in C1 and +229.00 in C2 (the 220 rule along DT's 1650.74 edge, pitch 403.58), Z 2374; the middle bolt's washer clears the soffit hanger's rivnut by 2.4 (F-4111-19). No pin slot (D-169 as amended).
- **The rib 513102 has its real folds** (the Lead's ruling on #335: inside radius = the sheet, 0.5): each fold a fillet on its inside corner (R 0.5) and its outside one (R 1.0); the flat uses K 0.44, as the tray's.
- **D-162:** the frames' members have no sheets of their own; their drawings are their rows in the frames' cut list. The frame rows cite J-FRAME-01's tolerance (diagonals equal within 1.5; skin-side faces within ±0.5 of one plane).
- **Names** (Control's ask for #397, the exports): 838003 is SHEREX CAL2-610-4.2; 108002 is the bond spec section 8's set for the steel frames, POD - ACP BOND SET - SIKAFLEX-252 WITH AKTIVATOR-205, PRIMER-210, FIXING TAPE (the same 12 × 3 joint, so its 0.28 kg/m² stands).

## Result

- timeline 379 items, unhealthy 0, loose sketches 0, user parameters 161, bodies 54
- clash pairs over 1 mm³: 0
- position check: all 54 bodies on their layout boxes (the 14 members, 8 mitre plates, 2 skins and both cassettes), worst 0.000 mm
- hole check: 58 hole faces on the joints register's positions (from the skeleton's and J-FRONT-03's named values), worst 0.000 mm: the 56 joint holes with DT's 8, and the two spigot slots by their end arcs; no other cylinder on any member
- turned copies (D-120): C2's side member 412101 is C1's turned about Y, C2's cross member 1 412105 is C1's turned end for end about Z, each mitre plate its part turned about Z to its corner's mitre; every turn read in the design after a full compute
- checked, saved, then exported by the same run:
  - `410000_P01_CEILING_CAD.f3d`
  - `v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step`: length unit cm, declared in the file (D-13); 28 products (`tools/fusion/step_check.py`). Read back with OCC: C2's skin has 4 cylinders of radius 8.5 (Ø17) centred at X 852, Y −600 and −346, and X 892 and 1137, Y −273, the sleeve's rivnuts; the members' holes by radius 3.5 (16), 4.25 (6), 5.0 (20, D-163's Ø10.00), 9.5 (16); the ribs' fold faces at R 0.5 (16) and R 1.0 (16), as version 12. The re-read in Fusion (MATCH, 0.030 mm) and the edit test (PASS): `EDIT-TEST-RECORD.md`. The header stamps Mac 1's local time (2026-11-02 01:08, UTC+7), which the generated sheets print as their date.
  - the tray's flat pattern from Fusion (`.raw/`, git-ignored), put on the CUT / BEND / MARK layers by `ceiling_exports.py` as `513101_P01_LINING-TRAY-CEILING_DXF.dxf`. This run's flat holds the same 70 entities as version 12's, compared one by one to 0.001 mm (only their order differs), so the committed file stands
  - `ceiling_exports.py` on this run's log: the parts list (C2's skin row names its 4 Ø17 holes; its mass 5.986 kg) and the skin's DXF with the holes; the tube cut list comes out unchanged
- no personal names in the STEP, the DXF files, the CSV files or any entry of the `.f3d` (scanned, zstd entries decompressed): 12 files, 134 entries
- the C1 panel's assembly sheet 410101 regenerated from this STEP (read-back PASS; only its date and its sources' record move); the generator's stale check shows 0 out of date

## The parts and where they are (pod system, mm)

| Part | Box or size | Mass each (Fusion) |
|---|---|---:|
| 411101 / 411102 frames C1 / C2 | X −1201.74…−2.75 / 2.75…1201.74, Y −645…850, Z 2354…2394 (the 3 mm bond line and the skin above); galvanized steel welded in a jig (D-131, J-FRAME-01): side and seam members 20 × 40 × 1.0 to Y 810, the back member 40 × 40 × 1.0 across, the front member, cross member X1 (Y −301…−281, 16 over the soffit's edge, so the soffit's room-side hanger studs land in it) in 1.0, X2 and X3 in 0.8; a 2.0 mitre plate in each corner; every joint hole of the register drilled in the members | 7.984 / 7.978 kg |
| 412101 side ×2, 412102 / 412202 seam, 412103 / 412203 front, 412104 / 412204 back, 412105 cross member 1 ×2, 412001 plain cross member ×4 | the frames' members (D-120 numbers; tube cut list `410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv`) | 1.321, 1.324 / 1.313, 1.063 / 1.068, 1.437, 1.054, 0.850 kg |
| 831007 / 831008 mitre plates, 2 of each per frame | the Joints Engineer's blanks (#294, shortened in #308): 831007 26.5 long from 1.75 along the mitre (front corners, 45°), 831008 41.5 from 3.15 (back corners); every end 0.51 to 0.53 inside the frame's faces | 0.017 / 0.026 kg |
| 411301 / 411302 skins C1 / C2 | 1200.61 × 1495 × 3 ACP, Z 2397…2400; C2 with the 285 × 294 roof slot (D-61, X 872…1157, Y −620…−326) and a Ø17 clearance hole under each of the roof sleeve flange's 4 rivnuts (J-AIR-03, D-177) | 6.282 / 5.986 kg |
| 410101 / 410102 outer panels C1 / C2 | frame + skin + its share of the ACP bond set 108002 (0.503 kg, bond spec 0.28 kg/m², not modelled as a body) + its joint hardware and seals from the parts list | **14.980 / 14.630 kg** (20 kg or less, D-03) |
| 513101 tray | X ±580 about each cassette centre (−583 / +583), Y −282…763, Z 2316…2350; two Ø19.1 cable holes (ELECTRICAL's bushings, PM ruling 2026-11-01) | 5.520 kg |
| 513102 rib (2 per cassette) | hat 44 × 24, 1034 long, X′ ±193.33; its folds at R 0.5 inside | 0.364 kg |
| 513201 felt | 1157 × 1042 × 9 on the lips, Z 2316.5…2325.5, no holes | 2.170 kg |
| 513301 / 513302 / 513303 fill | 1110.5 × 363.5 / 338.75 / 271.75 × 40 at 24 kg/m³ (D-81, ISS-088), on the tray back, notched round the clips and catches | 0.382 / 0.358 / 0.287 kg |
| 518001 clip × 6, 518002 catch × 2 per cassette | HOLD envelopes in the CAD (no mass); the parts list carries the register's 0.040 and 0.100 kg each (assumption) | 0.040 / 0.100 kg |
| 510301 cassette | the above, with clips and catches | **9.885 kg** (20 kg or less) |
| 410000 ceiling | 2 outer panels + 2 cassettes | **49.38 kg** |

The cassette starts at Y −282: the D-60 soffit takes the front 360 mm under both halves (Y −645…−285) and the cassette keeps a 3 mm gap to it, so it is 1045 long (1160 wide).

## Joint holes (joints register, skeleton P04 v4)

| Edge | Holes per half | Where |
|---|---|---|
| side wall | 4 Ø7 bolt clearance holes in the side member's outer face (X ∓1201.74), 4 Ø19 key access holes in its inner face | horizontal, Z 2374 (the tube's centre, R-J15); Y −425, −73.33, 278.33, 630: from `ceil_side_y0` plus the 220 edge inset, pitch `ceil_side_pitch` 351.67 |
| closing seam | C1: 4 Ø7 pin clearance holes in the seam member's outer face; C2: 4 Ø10.00 rivnut holes in its seam member's outer face and 4 Ø19 access holes in the inner face | the same Y and Z as the side bolts (`cj_pin_n` at `cj_pin_pitch`) |
| back wall | 4 Ø10.00 rivnut holes in the back member's bottom face (Z 2354, Y 824, R-J15), a Ø8.5 spigot hole and an 8.5 × 14 spigot slot | C2: X 222.75, 475.75, 728.74, 981.74 on the back frame's pitch 253.00 (`ceil_back_x0`, `ceil_back_pitch`, `n_ceil_back_bolt`), spigots at X 102.75 (round) and 1101.74 (slot); C1 mirrored |
| soffit hangers (AIR) | 1 Ø10.00 rivnut hole in the front member's bottom face (Y −635) and 1 in X1's (Y −291), at X ∓583 (`hang_x`) | the soffit's four M6 × 16 studs (D-90) |
| soffit lock (AIR) | 2 Ø10.00 rivnut holes in cross member 1's bottom face, Y −291, at X −1100 and −950 (C2 mirrored, X 950 and 1100, so 412105 stays one part; only C1's take screws) | the soffit's two captive M6 × 25 lock screws (PM ruling 2026-11-01, DR's new panel face: off C1's front member) |
| DT's bolts (J-FRONT-03) | C1: 3 Ø7.0 holes in the front member's front wall (Y −645) and 3 Ø19 access holes in its back wall; C2: 1 of each | Z 2374, X −981.74, −578.16, −174.58 (C1) and 229.00 (C2): from C1's frame end at the 220 rule, pitch 403.58 along DT's 1650.74 edge (`dt_pitch`); M6 × 16 into DT's rivnuts |
| roof sleeve flange (AIR) | C2's skin: 4 Ø10.00 holes under the flange's rivnuts, X 852.8 at Y −600 and −346 (the slot's left side), Y −273 at X 892 and 1137 (behind X1) | the roof grille's 4 rivnuts 838003 (J-AIR-03) |

Each hole is its own fully constrained sketch and cut (a pattern of identical holes failed to compute on these members, and a sketch with several circles on one plane over-constrained), with a 1 mm lead-in chamfer where a bolt enters.

## Flat pattern

Fusion's flat pattern of the tray: **1248.53 × 1133.52 mm**. The K-factor calculation in `ceiling_model.tray_flat()` (K 0.44, r = t = 0.5, outside setback r + t on each straight, bend allowance π/2 · (r + K·t) = 1.131) gives **1248.52 × 1133.52**: the same to 0.01 mm. K and r are assumptions until a bend coupon on the factory's tooling sets them (guideline §9).

## How the design is built

- One component per part, with part number, name and the Vietnamese name in its description. Repeated parts are one component with several occurrences: the cassette (C1-CASS, C2-CASS), the ribs, the clip and catch spaces.
- Every sketch is fully constrained on a construction plane offset by a parameter expression; every feature is named by its function.
- Every occurrence that a parameter places is held by a rigid joint to a sketch point dimensioned by expressions, so placements follow the parameters (edit test: `EDIT-TEST-RECORD.md`). A copy's ground-to-parent flag goes off before its joint (Fusion grounds a component's first-made occurrence and copies of it, and a joint on a grounded one conflicts), and a copy that doesn't land turned as asked stops the build.
- The tray is a sheet metal component (rule "GALV STEEL 0.5 - CEILING TRAY": 0.5 mm, bend radius = thickness, K 0.44, square corner relief): base flange, four returns (inside bend position, so their outer faces sit on the 1160 × 1045 outline), four lips turned in under the felt with mitred corners, two Ø19.1 cable holes.
- The skeleton's numbers are read from its CSV, by name and with their units; the ceiling's own parameters carry their status and source in the Fusion parameter comment.

## Master BOM check

`python3 v2/04-BOM/build_master_bom.py --no-write` on this branch: **OK** (no part without a number or a mass, no duplicate number, no unregistered hardware). The parts list carries size, tolerance, maker and SKU on each row, so the row is the cut list for the flat parts (D-89 part 4); the tube cut list is the frames' own.

## Not in this build yet

- The welds (D-131, J-FRAME-01): the beads aren't modelled. The mitre plates are square-ended blanks that stop 0.5 inside the frame's faces at both ends (#308); the weld fills the steps and is ground flush (a drawing note). Nothing stands proud of the frame, so the packing boxes read its outline as modelled.
- Drawings: the members and plates from the drawing generator (D-139), the bent parts and the assembly sheets in Fusion; specs in `../../02-Drawings/ceiling/drawing_specs.py`. The skins, the plain felt and the fill strips get no drawing (D-89 part 4, D-128: their DXF and parts-list row are enough).
- HOLD, drawn as space only: the clip (H03), the safety catch (H04), the felt fixing to the lips and ribs (H09), the fill fixing (H10), the cable grommet.
- The soffit, the air column and their parts are AIR's (`../air/`, PR #91); the light shelf, ledge and screen rail are INTERIOR's (`../interior/`, PR #92).
