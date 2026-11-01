# AIR transitions: the riser transition and the supply transition, as made sheet metal parts

The two ducts of AIR's supply path inside DR, built by script outside Fusion (the Lead's brief, 2026-11-01: Fusion's queue
is full). They replace the HOLD placeholders 618103 (riser transition) and 618102 (supply transition) in AIR's parts list.
Every number is in `tr_params.py` with its status and source. Pod coordinates, mm.

| Part (working key) | What | Material | Per pod |
|---|---|---|---|
| **610403 riser transition** | from the intake riser's top (Z 1386: the riser cut 60 mm shorter, the Lead's ruling) to the supply fan box's bottom (Z 1650) | | 1 |
| 611701 left wrapper | the duct's left wall: a collar into the riser, a throat turning 52° on R 100 (air side) in four bends (3 × 14.4° and a last 9°), the slant, a collar into the box; flanges on the cheeks, notched at each bend | galvanised steel DX51D+Z, 1.0 | 1 |
| 611702 right wrapper | the duct's right wall: collar and upright web, kink level with the throat's last bend, slant (19.9° from the left wall's), kink, collar, flanged the same way; the upright web's front fold is R 10, inside the riser's 8 x 8 chamfer (the Lead's ruling) | galvanised steel DX51D+Z, 1.0 | 1 |
| 611703 cheek | the front and back walls: a plate with two 4° kinks (the box sits 13.5 mm forward of the riser); beside that R 10 fold its right edge stops 11 mm in, on the fold's tangent | galvanised steel DX51D+Z, 1.0 | 2 |
| **610404 supply transition** | from the fan box's open top (Z 1950) to the opening into the air column (X 961 to 1146, Z 1895 to 2102) | | 1 |
| 611801 shell | an upturned tray: the roof and five walls (front, facet, right, back, left) folded down, corner tabs inside the next wall; front and left skirts over the box's walls; the outlet window in the back wall, the gasket 848013 round it | aluminium 5052-H32, 2.0 (alloy HOLD) | 1 |
| 611802 floor | an L beside and behind the box, a ramp beside the box up to the front wall, flanges up the shell's walls and the box's back wall | aluminium 5052-H32, 2.0 (alloy HOLD) | 1 |
| 611803 vane over the box | turning vane, R 32, the turn from up to across; its front tab riveted to the shell's front wall, its back tab bonded to the back wall | aluminium 5052-H32, 1.0 (alloy HOLD) | 3 |
| 611804 vane beside the box | turning vane, R 32, the turn from across into the window; tabs riveted to the floor and the roof | aluminium 5052-H32, 1.0 (alloy HOLD) | 2 |

Folds: inside radius = thickness, K 0.44 (the Lead's ruling), the vanes' curves R 32 and the right wrapper's corner
fold R 10. Joints: closed-end blind rivets (D-166: every tail ends inside the duct or the fan box), one family picked
by the Joints Engineer (2026-11-01): ISO 15973, aluminium body, steel mandrel, Ø4.0 in Ø4.1 holes with 8.5 to every
edge, head 12 x 2.5; the register's rows to come. Every lap and corner is sealed, and the three bonded vane tabs
bonded, with the pod's bond set 108002 (the Joints Engineer). 80 rivets a pod (`rivets.py` pairs every hole with its
mate):

| Duct | Stack (grip) | Rivet | Per pod |
|---|---|---|---:|
| riser transition | steel 1.0 + steel 1.0: the wrappers' flanges on the cheeks (2.0) | 4 x 8 (grip 0.5 to 3.5) | 34 |
| riser transition | steel 1.0 + the riser's steel 1.0: the collars into the riser (2.0) | 4 x 8 | 10 |
| riser transition | steel 1.0 + the fan box's 3.0 end walls (4.0) | 4 x 9.5 (grip 3.5 to 5.0) | 6 |
| supply transition | aluminium 2.0 + 2.0: the shell's corner tabs, the floor's flanges (4.0) | 4 x 9.5 | 15 |
| supply transition | aluminium 2.0 + the fan box's 3.0 front and back walls (5.0) | 4 x 11 (grip 5.0 to 6.5) on a 1.0 aluminium washer | 8 |
| supply transition | the vanes' 1.0 tabs on the 2.0 shell or floor (3.0) | 4 x 8 | 7 |

No rivet goes through the shell's back wall (DR's removable panel is 2.36 mm behind it) or within reach of DR's
bolt-line tube: the back-right corner's tab (behind the gasket's strip right of the window) bears and is sealed, and
the over-the-box vanes' back tabs are bonded. No hole is drilled on site (the Lead's ruling 2026-11-01): the 24 holes
through the riser's and the fan box's walls are in CEILING's flats of 611501 and 611402 as well as in these parts'
(`build.py` lists them); the box, the riser and both transitions ship as one piece (Packing's 2-17), so every rivet is
set at the factory. The box back flange's four rivets are set from inside the duct before the shell goes on. The left
skirt and the floor's edges by the box's right wall sit on the box's lined end walls and are sealed only, and so are
the collars' flanges inside the riser and the box.

## Files

| File | What |
|---|---|
| `tr_params.py` | every number with its status and source; the part numbers once Control allocates them |
| `sheetmetal.py` | the folded sheet kernel: walls (outer skins) and folds give the exact folded solid (OCC) and its developed flat (each fold's zone its bend allowance at K), STEP and DXF |
| `geom3.py` | planes, corner reliefs, rivet rows |
| `lower.py`, `upper.py` | the two transitions' parts |
| `check_flat.py` | develops a part's flat from its STEP alone (skins across tangent edges, folds as coaxial cylinder pairs) and checks its DXF: outline, bend lines, zone edges (the K they imply), holes, cut-outs, within 0.01 mm |
| `rivets.py` | every rivet hole's mate and the stack it closes, and each set rivet's head (up to 12 x 2.5) and tail (7 x 8) as solids for the clearance and overlap checks |
| `clearance.py` | each piece's (and each set rivet's) distance to every DR tube, the glass and its U-profile (the 6 mm rule) and to DR's skin (the 4 mm rule) |
| `build.py` | writes each part's STEP, DXF and fold table and the two assembly STEPs, runs the checks, and prints AIR's parts list rows (`--rows`) |
| `test_transitions.py` | the checks as tests |

Run with the drawing generator's OCC venv:

    ~/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python build.py --out v2/03-Manufacturing/air \
        --dr v2/03-Manufacturing/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step \
        --glass v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_STEP.step
    ~/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python -m unittest test_transitions -v

## Interfaces taken from other teams

- the supply fan box at X 680 to 980 (the Lead's ruling 2026-11-01), Y -819 to -664 (FRONT's DR STEP after the 3 mm glue
  line), Z 1650 to 1950; its 3 mm walls, its 50 mm end linings from Z 1795 up, its bulkhead at Z 1698 (CEILING);
- the riser X 959 to 1098, Y -803 to -653 (FRONT's DR STEP, CEILING), its top cut to Z 1386 and its front-right
  upright edge chamfered 8 x 8 (the Lead's rulings 2026-11-01; CEILING makes both in AIR's next rebuild);
- DR's frame, skin and the glass from FRONT's DR STEP on #313 (c65a3fa: the opening into the column X 961 to 1146,
  Z 1895 to 2102, the Lead's ruling; its tubes as at 541fe7f).

## Not done here

- Drawings: the drawing generator's bent sheet mode (#335) draws parts whose folds run in one or two square sets on a
  constant section; these parts fold along several directions and taper. Its folds-along-any-line mode (#369, open)
  doesn't draw them yet: tried at ef811f7 on all seven, it refuses the shell's window (cut-outs), the vanes' and the
  right wrapper's two radii, two parts' angled views ("no room on the sheet"), reads the floor's flat differently, and
  stops on the left wrapper. The fold tables (`*_FOLDS.csv`) carry each fold's line in the flat, angle, radius and
  direction meanwhile.
- AIR's parts list rows (CEILING owns the list): `build.py --out DIR --rows` prints them from the build's summary.
