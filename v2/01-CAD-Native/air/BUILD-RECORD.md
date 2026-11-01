# Build record: 610000 AIR P01 (air column, soffit, cartridges, fan boxes, riser, transitions, roof sleeve)

The AIR follow-up's rebuild on FRONT's rebuilt DR (#313): run 2026-11-01 15:58 to 16:11 UTC on Mac 1 (Fusion 2706.1.17),
through the Fusion lock (one held session, at the queue's front on the Lead's approval), from commit 3a1b82f:
`python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --arg own_doc=1 --arg save=1 --arg export=1`.
**DRAFT P01.** Cloud copy: Default Project / FocusPod v2 / `610000_P01_AIR_CAD`, rebuilt in place as a new version (the
first build, 2026-11-01 02:00 UTC, made it). Parameters: skeleton P04 v4, the ceiling's (the roof slot and the hanger
and lock rivnuts are CEILING's), FRONT's named values read from FRONT's DR model at load (DR's panel face and its opening
into the column; AIR keeps no copy), and AIR's own (`air_model.py`). The runner is main's with #386 (an open soon after a
save waits for the saved version).

The method was proven first, on unsaved designs (D-118): dry runs at 08:24 and 09:38 UTC and turned-copy probes 6 to 11.
This rebuild's new cuts use proven methods: the riser's chamfer is a polygon cut (poly_prism, as the transitions), and the
rivet holes through the walls normal to X are the ceiling's circle_cut_x (proven in the ceiling's builds).

## Result

- timeline 583 items, unhealthy 0, loose sketches 0, user parameters 297, bodies 68
- clash pairs over 1 mm³: 0
- position check: 58 units (each copy, each joined stud and lock screw) on their layout boxes, worst 0.000 mm
- the column's right front angle is the left one's copy (D-120), turned about Y by its joint (flip, angle 180°), the turn
  read in the design after a full compute
- saved: True; the f3d and STEP exported by the same run that saved, so they are the saved version:
  `610000_P01_AIR_CAD.f3d`, `v2/03-Manufacturing/air/610000_P01_AIR_STEP.step`
- STEP (`tools/fusion/step_check.py`): length unit cm, declared in the file (D-13); 54 products, 47 solids (68 placed,
  OCC); the roof sleeve 611601, the fan box casings and bulkheads and the riser each one solid
- the STEP's holes (OCC): the riser 611501 carries its 10 Ø4.1 rivet holes and the buffer rivnut's Ø10.00, the supply box
  casing 611402 its 14 Ø4.1, the roof sleeve its 4 Ø10.00; all 24 rivet holes lie within 0.033 mm of the AIR Transitions
  Engineer's list (which gives one decimal)
- no personal names in the STEP, the DXF and CSV files or any entry of the `.f3d` (zstd entries decompressed): 22 files,
  144 entries
- the STEP re-read in Fusion (68 bodies, its box within 0.030 mm of the layout's: MATCH) and the edit test (PASS):
  `EDIT-TEST-RECORD.md`
- the commits after 3a1b82f on this branch change names and texts only (838003's register name, a parameter's source);
  the exports read them

## What the follow-up changes (PM rulings 2026-11-01)

- **The supply fan box** at X 680 to 980 (the Lead's ruling, the AIR Transitions Engineer's find), front face at Y −819:
  25 behind DR's skin plus D-137's 3 mm bond line, 5 behind the cross tube F09 over it. Its rest in DR: the lip angle
  611408 across its front wall on two rubber pads 618402 on DR's shelf tube F08; the riser buffer 618501 in one 838003
  rivnut on the riser's front face, against DR's cross tube F07 (it holds the assembly upright with DR's inner panel off;
  the outlet's soft seal carries no load).
- **The riser** at X 959 to 1098, Y −803 to −653, from Z 252 (D-130's boot to come) to Z 1386: cut 60 shorter (the
  Lead's ruling), so the lower transition's turn eases to 52°. Its front-right vertical edge is chamfered 8 × 8 (the
  Lead's ruling): 6.5 from DR's corner facet skin, where the square corner was 1.2 (calculation on #313's DR STEP).
- **The transitions' 24 rivet holes** (the AIR Transitions Engineer's list, 2026-11-01 15:18): Ø4.1 for a Ø4.0 blind
  rivet (HOLD until Joints picks it), made in both parts' flats, none drilled on site (the Lead's ruling). In the riser:
  10 at Z 1373.5, the middle of the lower transition's 25 mm collar. In the supply box casing: 3 in each end wall at
  Z 1660 for the lower transition's webs, 4 in the front wall at Z 1941 and 4 in the back wall at Z 1891.5 for the upper
  transition, between the end walls' linings. Each position is a named parameter measured from its wall's own edges.
- **The transitions** stay HOLD envelopes in this PR, sized from FRONT's reserved spaces: the upper one 618102 over the
  box and the full-depth passage beside it to DR's opening (FRONT's, X 961 to 1146, Z 1895 to 2102); the lower one 618103,
  FRONT's trapezoid from the riser's top to the box's bottom over the riser's depth (from Y −803: from the box's front
  line it cut DR's corner skin). The AIR Transitions Engineer's #395 makes them parts (610403, 610404).
- **The roof sleeve 611601** with its top flange (40 left, 72 back, 15 front and right, J-AIR-03) and the grille's 4
  rivnuts; **the grille 611602** is the flange's outline.
- **DR's panel face and its screws (D-142):** AIR reads FRONT's named value for the face, so it fits either face: the
  door-side plate's pockets round the two door-side stud heads; B08's three screws get Ø14 reliefs in the door plate and
  12 × 12 pockets in the fill (nothing in the undersides); the supply cartridge is lifted 6 (Z 140 to 1890) over B01's.
- **D-163:** every 838003 rivnut hole AIR makes is Ø10.00 (the sleeve's 4, the buffer's), and the hanger and lock
  rivnuts it hangs on are the ceiling's (#348's entry).
- **Names:** 611302 is AIR - CARTRIDGE FILL - LAYER 50 (a knife-cut fill, no drawing, D-89 part 3); 838003 carries the
  register's name, SHEREX CAL2-610-4.2 (Control's ask for #397), applied at the exports.

## Clearances to DR (OCC on this build's STEP and #313's DR STEP at 780aa83; FRONT's reserved air spaces skipped)

| AIR part | Nearest DR solid | Gap (mm) | Rule or note |
|---|---|---:|---|
| supply box casing 611402 | back ring diagonal tube (B06) | 6.325 | the 6 mm rule |
| supply box casing 611402 | front ring fan box shelf (F08), cross tube over the box (F09) | 5.000 | 25 behind the skin |
| intake riser 611501 | DR's corner facet skin, at the chamfer | 6.547 | the Lead's 8 × 8 chamfer (was 1.199) |
| intake riser 611501 | back ring glass-edge tube (B07), at its foot | 5.725 | |
| upper transition 618102 (HOLD) | facet tube C04 | 2.997 | C04 is no bolt-line tube or band: outside the 6 mm rule |
| upper transition 618102 (HOLD) | back ring bolt-line tube (B02) | 18.000 | the 6 mm rule |
| upper transition 618102 (HOLD) | DR's removable inner face panel | 2.360 | |
| lower transition 618103 (HOLD) | DR's corner facet skin, at its foot | 1.199 | FRONT's reserved spaces for the riser and this duct come as close (1.199, measured); #395's duct follows the chamfer |
| lip angle 611408 | DR's skin | 2.000 | its free edge over F08 |
| pads 618402, buffer 618501 | F08, F07 | 0.000 | they bear on them, by design |

## Shipping pieces (D-87: 20 kg or less; masses from Fusion, HOLD items at their parts-list figures)

| Piece | Mass |
|---|---:|
| 610201 soffit with the exhaust fan box and its 2 fans fitted | 14.64 kg |
| 610101 column (without its cartridge) | 8.15 kg |
| 610301 cartridge (each of 2) | 10.55 kg |
| 610401 supply fan box with its 2 fans, the riser, the transitions, the lip, pads and buffer | 11.75 kg |

The weight roll-up takes these CAD masses: AIR 57.9 kg (was 58.4: the riser 60 shorter, the soffit's fill and rail
thinner on DR's rebuilt panel face), the pod 395.4 kg as shipped.

## Exports (`air_exports.py` on this run's log)

- `610000_P01_AIR-PARTS-LIST_BOM.csv`: 56 rows, each with size, tolerance, maker and SKU (the row is the flat parts' cut
  list, D-89); the door-side plate and the grilles laser cut (D-89 part 4)
- DXF cut files of the flat parts: foot plate, plenum plates, top rails (forks, lock holes), end plate, the door-side plate
  (its outline, the two head pockets and B08's three Ø14 reliefs), the ACP faces with their openings, the grilles (the
  kick grilles 611105 and 611111 too), the two fan bulkheads (bores and screw holes)

## Open

- The flat cut files of the bent parts with their real folds: the riser 611501 and the fan box casings 611401 and 611402
  (with the transitions' rivet holes and the casings' own seam rivets, 18 a pod, told to Joints), the cartridge casing
  611301, the roof sleeve 611601 (D-158: the generator's bent sheet mode draws them).
- The soffit supports (straps, mounts, latch brackets, the hinge's space) and ELECTRICAL's harness route: the next AIR PRs.
- HOLD: D-130's intake boot 611502 and the cartridge gaskets 611303 (BASE's frame faces), D-132's column foot locator,
  the lock screws' retainer, grille patterns.
