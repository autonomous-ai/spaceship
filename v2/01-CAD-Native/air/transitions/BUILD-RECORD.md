# Build record: AIR's two transitions P01 (610403 riser transition, 610404 supply transition)

Run 2026-11-01 on Mac 1, outside Fusion (the Lead's brief: Fusion's queue is full), with the drawing generator's OCC
venv (OCP 7.8.1): `build.py --out v2/03-Manufacturing/air --dr DR.step --glass GLASS.step --summary FILE.json`, where
DR.step and GLASS.step are FRONT's 350003 and 360002 STEPs on #313 at c65a3fa (FRONT's newest DR; its tubes are as at
541fe7f). **DRAFT P01.** Every number is in `tr_params.py` with its status and source.

## Result

| Part | Per pod | Mass each (calculation) | Flat (DXF extents) | Folds | Holes | Flat check |
|---|---:|---:|---|---:|---:|---|
| 611701 riser transition - left wrapper | 1 | 0.586 kg | 437.8 x 189.0 | 17 | 24 | PASS |
| 611702 riser transition - right wrapper | 1 | 0.477 kg | 343.5 x 200.0 | 8 | 22 | PASS |
| 611703 riser transition - cheek | 2 | 0.491 kg | 252.6 x 506.1 | 2 | 19 | PASS |
| 611801 supply transition - shell | 1 | 1.609 kg | 935.6 x 579.1 | 10 | 32 + the window | PASS |
| 611802 supply transition - floor | 1 | 0.218 kg | 503.6 x 221.0 | 8 | 13 | PASS |
| 611803 supply transition - vane over the box | 3 | 0.046 kg | 97.0 x 201.5 | 3 | 1 | PASS |
| 611804 supply transition - vane beside the box | 2 | 0.051 kg | 82.0 x 257.5 | 3 | 2 | PASS |

610403 is 2.046 kg and 610404 2.067 kg (calculation, the sum of their parts; the HOLD rows they replace had 1.47
and 1.89), plus 80 rivets and the sealant. The riser loses 0.27 kg with its top cut to Z 1386 (calculation: 59 mm of
its 578 mm of 1 mm steel wall).

- Each part is one valid solid whose volume is the one its definition gives.
- Flat check (`check_flat.py`, from the STEP alone): outline, bend lines, zone edges (the K they imply: 0.44), holes
  and the shell's window within 0.01 mm, 7 of 7. Planted faults fail: a bend line 0.5 off, an outline edge 0.1 off,
  a flat developed at K 0.33.
- Rivets (`rivets.py`): 80, every hole paired with its mate; no hole without one. Stacks and the rivet for each
  (the Joints Engineer's pick) in the README; the 5.0 stacks' heads sit on a 1.0 washer, and the checks count it.
- Overlaps over 0.001 mm3, among the placed pieces, the 80 set rivets (heads 12 x 2.5, tails 7 x 8), the fan box
  with its linings and bulkhead, and the riser with its 8 x 8 chamfer: 0.
- Clearance on FRONT's DR and the glass unit: the nearest DR tube is 6.00 mm (the shell's right wall to the bolt-line
  tube 352308, as designed), the nearest set rivet 6.25 (to the facet side tube 352302); the glass and its U-profile
  are 350 mm or more away. B06 (352312) is 9.0 mm from the duct's top-left corner where it enters the box (the box is
  6.3 there) and 25 mm or more along the slant. DR's skin is 5.81 mm or more from every piece and 10.5 from every set
  rivet (the 4 mm rule).
- The collars slip 0.5 inside the riser and the box all round (0.7 at the riser's chamfer); the right wrapper's slant
  passes 0.42 under the box's right wall's bottom edge.
- The lower duct's slant walls are 19.92 degrees apart (the ruling: 20 or less); it never narrows below its 134 mm
  collar.
- STEP headers: author and organisation empty; mm declared (these are not Fusion exports, so D-13's cm doesn't
  apply); no person's name in any STEP, DXF or CSV.
- Unit tests (`test_transitions.py`): 11 of 11. The clearance test reads FRONT's STEPs from the checkout and skips
  until #313 is on main; the build ran the same check on #313's.

## The Lead's rulings this build follows (2026-11-01)

- The shop build: two wrappers and two cheeks for the lower duct, a shell and a floor with turning vanes for the
  upper; we design for the factory, not for the drawing tool.
- The supply fan box at X 680 to 980; the upper duct's right wall to X 1158; folds at R = t, K 0.44.
- DR's panel opening, and the duct's window, X 961 to 1146, Z 1895 to 2102.
- The riser kink rounded (R 100), and the lower duct's loss at 3.1 Pa or less in the Air Engineer's model: the riser
  cut 60 mm shorter (its top at Z 1386), so the turn eases to 52 degrees and the walls widen at 19.9.
- The riser's front-right upright edge chamfered 8 x 8: the right wrapper's corner fold is R 10 inside it.
- No hole drilled on site: the 24 holes through the riser's and the box's walls are in CEILING's flats too. The box,
  the riser and both transitions ship as one piece (Packing's 2-17), so the rivets are set at the factory.

## Not done yet

- The Air Engineer's model of the rebuilt lower duct (the middle figure at 3.1 Pa or less), and the air report's
  update.
- AIR's parts list rows (CEILING owns the list): on top of CEILING's #378 once it merges (`build.py --rows`).
- The register's rows for the rivets (4 x 8, 4 x 9.5, 4 x 11 and the washer), the bond set's AIR line and 848013's
  AIR line (Joints' next register PR).
- CEILING: the riser cut and chamfer, and the 24 holes in 611501's and 611402's flats, in AIR's next rebuild.
- Drawings: the generator's any-line folds mode (#369, ef811f7) doesn't draw these parts yet (README).
