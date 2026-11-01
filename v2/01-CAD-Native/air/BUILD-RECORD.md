# Build record: 610000 AIR P01 (air column, soffit, cartridges, fan boxes, riser, transitions, roof sleeve)

The AIR follow-up's build: run 2026-11-01 11:11 to 11:21 UTC on Mac 1 (Fusion 2706.1.17), through the Fusion lock (one
held session), from commit 891c649:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg own_doc=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `610000_P01_AIR_CAD`, rebuilt in place as a new version (the
first build, 2026-11-01 02:00 UTC, made it). Parameters: skeleton P04 v4, the ceiling's (the roof slot and the hanger
rivnuts are CEILING's), FRONT's named values for DR's panel face read from FRONT's DR model at load (AIR keeps no copy),
and AIR's own (`air_model.py`).

The method was proven first, on unsaved designs (D-118): dry runs at 08:24 and 09:38 UTC (every check below, closed
without saving), and turned-copy probes 6 to 11 for the column's turned front angle. A saved build at 10:10 UTC exported,
but its STEP held the roof sleeve as two solids (the flange's opening was cut at the slot's outline); the 10:31 build cut
it at the walls' inside and passed. This build adds the fan bulkheads by the Lead's rule for openings (below).

## Result

- timeline 509 items, unhealthy 0, loose sketches 0, user parameters 281, bodies 68
- clash pairs over 1 mm³: 0
- position check: 58 units (each copy, each joined stud and lock screw) on their layout boxes, worst 0.000 mm
- the column's right front angle is the left one's copy (D-120), turned about Y by its joint (flip, angle 180°), the turn
  read in the design after a full compute
- saved: True; exports from the saved version: `610000_P01_AIR_CAD.f3d`, `v2/03-Manufacturing/air/610000_P01_AIR_STEP.step`
- STEP (`tools/fusion/step_check.py`): length unit cm, declared in the file (D-13); 54 products, 47 solids (68 placed);
  the roof sleeve 611601 and each fan bulkhead one solid (OCC read)
- no personal names in the STEP, the DXF and CSV files or any entry of the `.f3d` (zstd entries decompressed)
- the STEP re-read in Fusion and the edit test: `EDIT-TEST-RECORD.md`

## What the follow-up changes (PM rulings 2026-11-01)

- **The supply fan box moved** to X 673…973, 25 mm back from DR's skin (front Y −822), in FRONT's reserved space, 4 mm off
  DR's diagonal tube and glass slot. Its rest in DR: the lip angle 611408 (3 mm aluminium) across its front wall, its foot
  on two rubber pads 618402 on DR's shelf tube F08; the riser buffer 618501 in one 838003 rivnut on the riser's front face,
  touching DR's cross tube F07 (holds the assembly upright with DR's inner panel off; the outlet's soft seal carries no load).
- **The riser** at X 956, 150 deep (Y −803…−653), its foot at Z 252 (D-130's boot to come).
- **The upper transition 618102** over the box and the full-depth passage beside it (#283), 3 mm off the facet tube C04;
  **the lower transition 618103**, FRONT's trapezoid, 4 mm off DR's diagonal tube B06 (both HOLD envelopes at sized masses).
- **The roof sleeve 611601** gets its top flange (40 left, 72 back, 15 front and right, J-AIR-03) with the grille's 4
  rivnuts; **the grille 611602** is the flange's outline.
- **DR's panel face and its screws (D-142):** AIR reads FRONT's named value for the face, so it moves to Y −641.14 with
  FRONT's DR rebuild, and AIR fits either face: the soffit's door-side plate gets pockets round the two door-side stud
  heads; B08's three panel screws get Ø14 reliefs in the door plate and 12 × 12 pockets in the fill under the exhaust
  cartridge (nothing in the undersides); **the supply cartridge is lifted 6 mm** (Z 140…1890), its foot tied to B01's
  washers (4 clear), so it holds when BASE's D-132 takes the floor out; B07's lowest stays 4 off the column.
- **D-116, D-121, D-124 in the CAD:** the cartridge layers at 32 kg/m³, the fill at 24 (D-81), the fan boxes in 3 mm with
  their bulkheads and 50 mm linings; the exhaust fans hang under their bulkhead at the box's top.
- **The fan bulkheads (the Lead's rule for openings, 2026-11-01):** each pair of Ø135 bores at the quarter points of its own
  2 mm bulkhead, inside the casing's walls, so the rims are equal: 5.25 on the exhaust bulkhead (its left edge is free, the
  box being open there) and 6.0 and 7.0 on the supply one; the webs between bores 10.5 and 12 (at least 2 × the sheet and
  3 mm). The fans' own screw holes, 4 per fan on Noctua's 124.5 mm square, Ø4.5, each at least 10.5 from every edge (the
  2-diameter rule for fasteners: 9). Each bulkhead is laser cut on its own DXF and sealed to the casing (fixing HOLD).
- **D-120:** the corner angles, the column fill and kick grille pieces, the soffit fill pieces, the cartridge's casing and
  layers and the lock screws are their own components, copies placed by joints.
- **The column's foot** follows the skeleton's floor top; with D-132's no floor its support and locator move to BASE's
  bracket on the band (HOLD until its faces are posted).

## Shipping pieces (D-87: 20 kg or less; masses from Fusion, HOLD items at their parts-list figures)

| Piece | Mass |
|---|---:|
| 610201 soffit with the exhaust fan box and its 2 fans fitted | 14.76 kg |
| 610101 column (without its cartridge) | 8.15 kg |
| 610301 cartridge (each of 2) | 10.55 kg |
| 610401 supply fan box with its 2 fans, the riser, the transitions, the lip, pads and buffer | 12.05 kg |

The weight roll-up now takes these CAD masses as they are (the follow-up models what it used to add): AIR 58.4 kg, the pod
409.2 kg as shipped, as before.

## Exports (`air_exports.py` on this run's log)

- `610000_P01_AIR-PARTS-LIST_BOM.csv`: 56 rows, each with size, tolerance, maker and SKU (the row is the flat parts' cut
  list, D-89); the door-side plate and the grilles laser cut (D-89 part 4)
- DXF cut files of the flat parts: foot plate, plenum plates, top rails (forks, lock holes), end plate, the door-side plate
  (its outline, the two head pockets and B08's three Ø14 reliefs), the ACP faces with their openings, the grilles, the two
  fan bulkheads (bores and screw holes)

## Open

- C09 on the two fan bulkheads: the checks on main still read the Ø135 bores as fastener holes. The Mechanical Checker's
  #334 reads them as openings (the Lead's web rule); the bulkheads meet it, and the fans' screw holes meet the 2-diameter
  rule.
- FRONT's #313 (DR's tubes 3 mm off its skins, D-137's glue line): the supply fan box 3 mm back (front face Y −819), the
  riser 3 mm right (X 959 to 1098), FRONT's new panel screw positions and DR's tube faces from its rebuilt STEP: AIR's next
  update, ready to merge right after #313.
- Drawings for the follow-up's new parts (D-139: the generator for flat and tube parts, Fusion for bent ones and the
  assembly sheets).
- HOLD: D-130's intake boot 611502 and cartridge gaskets 611303 (BASE's frame faces), D-132's column foot locator, the
  transitions' own design, hinges, latches, the lock screws' retainer, the hub zone, grille patterns.
