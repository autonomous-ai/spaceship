# Feature rationale: BASE, sample P01 (back-left corner and F1)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-BASE-FR | P01 | DRAFT | 2026-11-01 | BASE Engineer |

Why every hole, cut and feature of the BASE sample parts exists (guideline §7). Positions are in the pod system (`conventions.md` §4), mm, as the build script makes them from skeleton P04 (`v2/01-CAD-Native/skeleton/pod_skeleton.py`) and BASE's own parameters (`v2/01-CAD-Native/base/base_build.py`, `BASE_PARAMS`). Every value carries its status there; this file gives the reason. Identical features are grouped. The drawings tag them with these IDs.

Statuses: **confirmed** (PM decision), **source** (named document), **calculation**, **assumption**, **HOLD** (waits on a named item).

## Parts covered

| Part | Name | What it is |
|---|---|---|
| 111101 | BASE - BAND TUBE - SIDE - LH | 100 × 40 × 1.5 aluminium tube under the left wall, X −1250…−1210, Z 10…110 |
| 111103 | BASE - BAND TUBE - BACK | 100 × 40 × 1.5 tube under the back wall, X ±1210, Y 810…850 |
| 111601 | BASE - GLIDE DOUBLER - COMMON | 3 mm plate inside the band at each glide; no drawing: its DXF and its parts-list row (D-89 part 4) |
| 111211 | BASE - CORNER KEY - SQUARE - COMMON | the hook-in key in each back band end (J-BASE-02, D-87); the Joints Engineer's part (model, STEP, tabulated drawing), placed here by reference |
| 111401 | BASE - FLOOR PANEL - F1 | 9 mm poplar-core plywood, X −1206…+12.5, Y −645…+806 |
| 111501 | BASE - FLOOR FOAM - F1 - CLOSED-CELL 3 MM | 3 mm closed-cell foam bonded under F1 (D-87); no drawing: its DXF and cut-list row (D-89 part 3) |
| 111102 | BASE - BAND TUBE - SIDE - RH | mirror of 111101 under the right wall, X 1210…1250, front end mitred to the intake's facet piece |
| 111106 | BASE - BAND TUBE - FRONT - FIXED GLASS | FR1: 100 × 40 × 1.5 tube under the fixed glass, X 218.5…915, closed at the joint by a welded 1.5 mm end plate with 2 keyholes |
| 111301 | BASE - SILL - FIXED GLASS | bent 2 mm black profile on FR1 that carries FRONT's bottom U-channel, X 218.5…965 |
| 111402 | BASE - FLOOR PANEL - F2 | 9 mm poplar-core plywood, X 0.5…1206, Y −645…+806, with a tab under the sill |
| 111502 | BASE - FLOOR FOAM - F2 - CLOSED-CELL 3 MM | 3 mm closed-cell foam bonded under F2, with 2 cut-outs; no drawing: its DXF (D-89 part 3) |
| 111801 | BASE - LOCATOR SPIGOT - AIR COLUMN - D8 | Ø8 spigot fitted from below through F2 for the air column's foot |
| 111701 | BASE - DOOR THRESHOLD - 13 MM | 13 mm aluminium threshold across the door opening, X −972…218.5 |
| 110101, 110103, 110401 | the band assemblies and F1's bonded assembly | each has its assembly drawing (D-89: every assembly keeps one), made from its own design that the build saves |

The joint hardware (rivnut 838003, stop washer 831002, spigot 831001) is the joints register's (J-BASE-01, section 3.4); this file covers where BASE puts it.

## Band tubes (111101, 111103)

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FB-01 | Section 100 × 40 × 1.5 | Carries the walls to the glides; the outside dark band of v1's look | 100 tall (Z 10…110), 40 wide | Band top = `wall_z0` 110 (skeleton); the ACP's outer face flush with the band's outer face (joints register 3.4). Wall 1.5: sag 0.38 mm over the 1.33 m glide span at 0.34 kN/m, stress about 7 MPa (calculation) | section source (layout study B-BAND); wall confirmed (PM ruling 2026-10-31) |
| FB-02 | Side band front end, mitre | Meets DL's outer facet band piece face to face, so the band follows v1's faceted outline (D-01, Lead ruling 3) | Outer corner (X −1250, Y −670 = −`dl_y1`), inner corner (X −1210, Y −652.07); 24.14° from square | Bisector of the side and DL's facet direction (`dl_x2`, `dl_y1`, `dl_y2`); the same expression as the skeleton's `_ML` | calculation |
| FB-03 | Side band back end, square | Takes the end cap (118003); the back band butts the side band's inner face, as v1's frame | Y 847 = `pod_d / 2 − cap_t`, so the cap's face is flush with Y 850 | Back band 2420 long fits the 96 × 48 in pallet (layout study B1) | cap_t assumption; cap HOLD |
| FB-04 | J-BASE-01 rivnut holes Ø9.53, top wall | Nut side of the wall-to-band joint: a rivnut 838003 set through a stop washer 831002, so the wall stands on the stop at Z 112.26 (`panel_z0`) | 4 per panel at the 220 mm rule from the panel's **frame** ends (`base_bolt_edge`, `n_base_bolt`). L1: X −1224, Y −422.74, −71.83, 279.09, 630.00 (pitch 350.91). B1: Y 824, X −981.74, −728.74, −475.75, −222.75 (pitch 253.00 on the frame, PM ruling); B2 mirrored | Bolt line on the wall tube's centre: `outer_t − frame_t / 2` = 26 in from the outer face (joints register 3.4). Hole Ø9.53 +0.10/0 for CAH3-610-4.2 (maker). Grip 1.5 + 1.5 washer = 3.0, inside 0.70–4.20 | confirmed rule (D-75); hole source; rivnut torque HOLD-01 |
| FB-05 | Spigot rivnut holes Ø9.53, top wall | Hold the Ø8 locating spigots 831001 that the wall drops onto | 2 per panel, 100 in from the frame ends (`base_spigot_inset`). L1: Y −542.74, 750.00. B1: X −1101.74, −102.75; B2 mirrored | Same line as FB-04; no stop washer, so the spigot's rivnut head (0.76) stays under the wall's 2.26 gap | confirmed rule (D-75) |
| FB-06 | Glide key holes Ø8, top wall | A 5 mm hex key (5.77 across corners) reaches the glide stem from above, to level the band before any wall goes on (layout study; D-87: glides preset at the factory, trimmed on site) | One over each glide, on the band's centre line: L1 band (X −1230, Y −625 and +700), back band (Y 830, X −1060, 0, +1060) | The glide stands on the band's centre line because the doubler's hole is centred (PM ruling, FD-02). Ø8 spans 16 to 24 from the outer face, so it stays inboard of the gasket strip, 8 wide beside the washer line on its outer side (8 to 16; joints register FR-11); ≥ 40 mm from any rivnut | assumption (size); positions calculation |
| FB-07 | Glide nut holes Ø13, bottom wall | Take the M10 rivnut 838006 that carries the glide 118002 | Same X, Y as FB-06 | Ø13 for an M10 rivnut (assumption until the nut is named, HOLD) | HOLD |
| FB-08 | Glide positions | Support the band: side band glides 75 behind the band's front corner and 150 from the back face; back band at 150 from each end and the middle | Side span 1295, back spans 1060. The front glide's doubler stays 15 behind the front corner key's back face (Y −636.03), out of the keyed end's last 30 mm (joints register PR #99). Lowest setting 8.5 under the band: the glide's base, fully home against its rivnut's head, is the stop (PM ruling on F-018) | Sag under 0.5 mm at 1.5 mm wall (FB-01); the front glide is tied to the band's own end (`-dl_y1 + gl_e_f`), not the wall's edge, so it stays under the band when the skeleton moves | assumption (spacing), calculation (sag) |
| FB-09 | Finish | The visible dark band | Black anodised, matte, 20 µm (AA20, EN ISO 7599) | D-67 | confirmed |
| FB-10 | Keyholes in the side band's inner wall, at the back | The hook-in corner (J-BASE-02, D-87): the side band goes on 10 mm high with its Ø12 entries over the back key's stud heads, then drops 10 mm onto them; the heads hold the inner wall and the 6.5 slot locates the corner in Y to ±0.25 | 2, at Y 830 (the back band's centre line): Ø12 entries at Z 27.5 and 61.5, each with a 6.5 slot running 10 up to the stud's seat at Z 37.5 and 71.5 | Entry 10 below the seat, slot up to it (the Joints Engineer's fix of 2026-11-01: the moving piece goes down onto the studs). The studs sit at Z 37.5 and 71.5 so the lower entry's edge (Z 21.5) stays 10 above the bottom wall's inner face, clear of the tube's corner | source (Joints Engineer, via the Lead); register update pending |
| FB-11 | Key fixing holes Ø7.0, back band bottom wall | The factory screws (838010, M6 × 12 flanged button heads, no washer) that hold each back key in the band's end | 2 at each end: 10.5 from the key's back face, so 19.5 in from the band's end (X ∓1190.5), Y 830 ± 7.0 (joints register #127: 2 diameters from the cut end) | Joints register J-BASE-02 (PR #99). F-018: the heads hang 3.3 under the band, so the glides never go below 8.5 (FB-08) | source; PROPOSED |
| FB-12 | Front key fixing holes Ø7.0, left band bottom wall | The left band's front end carries the front corner key 111212 (the register's carrier), fitted at the factory like the back keys | 2: X −1237 and −1223, Y −641.53 (10.5 from the key's back face, which is 30 behind the mitre face's centre) | Joints register #127, `corner-keys.csv` (the 30 mm key keeps them 2 diameters from the mitred end, the Lead's ruling of 2026-11-01: no edge exception, the screws carry the joint's pull); the key itself comes with the front pieces (P02) | source; PROPOSED |

## Glide doubler (111601)

| ID | Feature | Function | Size | Constraint behind it | Status |
|---|---|---|---|---|---|
| FD-01 | 3 mm plate, 36 × 54 | Spreads the glide's load across the band's 1.5 mm bottom face to both side walls | 36 wide = the 37 mm bore less 1 mm; 54 long, so each end is 27 from the hole, past the 2 hole diameters (26) of the PM ruling of 2026-10-31 (at least 52) | A ~500 N glide load on the bare 1.5 mm face bends it to about 123 MPa (Roark, plate fixed on two long edges, load on the Ø16 nut head) against a yield of about 160 for 6063-T6; with the 3 mm doubler about 31 MPa (calculation) | confirmed (length), assumption (thickness), calculation |
| FD-02 | Hole Ø13, centred | The glide's M10 rivnut passes through the doubler and the bottom face, clamping both (grip 4.5) | Centred across the 36 width (18 to each long side, 1.38 hole diameters) and along the 54 length (27 to each end) | **Why 18 mm (1.38 diameters) is enough here (PM ruling 2026-10-31, the Checker's edge rule accepted):** the glide's load pushes the plate onto the band's bottom wall, so the plate works in compression and bearing over its face; nothing pulls the hole toward the long edges. The only sideways load is the glide's small share of friction, which the rivnut's clamp carries. The edge rule guards against tear-out of a hole loaded toward an edge, which this hole never sees. One part for the left, right and back bands (turned) | confirmed (position); hole size HOLD with the nut |
| FD-03 | No drawing | A flat part cut from sheet, no bends, no machined features (D-89 part 4) | DXF `111601_P01_BASE-GLIDE-DOUBLER-COMMON_DXF.dxf` (outline and hole); the parts-list row gives EN AW-5754 H22 3 mm, mill finish (hidden, D-79), ISO 2768-m, and the critical hole: Ø13 +0.10/0 centred ±0.2 | D-89 part 4 | confirmed (rule) |

## Back corner key (111211), as BASE places it

The key is the Joints Engineer's part (PM ruling 2026-11-01: model, STEP and the tabulated drawing of 111211 to 111214); these rows say how BASE's band takes it.

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FK-01 | Block 30 × 35 × 75, EN AW-6061 T6 | Sits in the back band's open end on its bottom wall, end face flush with the band's end at X ∓1210; carries the 2 hook studs that the side band hangs its keyholes on (FB-10) | X 0…30 into the band, 35 across (centred), Z 11.5…86.5 in the pod | Joints register #127: 30 long so its fixing holes keep 2 diameters from the carrier's cut end; 75 tall so the studs could move up | source; PROPOSED |
| FK-02 | Hook stud holes, M6 tapped through the end face | Take the studs 838001, set at the factory with their heads 1.8 off the face (1.5 wall + 0.3), threadlocked | 2 on the band's centre line, 26 and 60 above the key's bottom (pod Z 37.5 and 71.5) | Tapped through, so the 14.2 mm the stud reaches is all in thread (PM ruling on F-017) | confirmed (thread), source (positions) |
| FK-03 | Fixing holes, M6 with 15 of full thread, in the bottom | The 2 factory screws from below (FB-11) | 10.5 from the back face and from each side face (7.0 either side of the centre line); tap drill Ø5.0 × 18 | The M6 × 12 button head engages 10.5 (12 − 1.5 wall) in the 15 of thread (PM ruling on F-017; joints register PR #99) | confirmed (thread); positions PROPOSED |

## Floor panel F1 (111401) and its mat (111501)

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FF-01 | Outline | The floor inside the band ring, out to the band (Lead ruling 2), so no trench is left | X −1206 (band inner face + 4 gap) to the seam; Y −645 (walls' front edge) to +806 (back band − 4) | The 4 mm gap takes the floor-edge seal 118001 (PM ruling: seal at the floor's edge, so v1's shadow line under the band stays open) | confirmed (rulings), gap assumption |
| FF-02 | 9 mm thickness on a 3 mm mat | Floor top Z 12, so the door threshold is 13 mm (US accessibility) | Z 3…12 | D-72; poplar-core with a hard face veneer, about 450 kg/m³ (D-85); edge deflection about 0.6 mm under 1000 N on the firm foam (calculation, test PLANNED) | confirmed (thickness), assumption (density) |
| FF-03 | Half-lap at the F1/F2 seam | Keeps the seam flush with no glue; F1's lower half runs under F2's upper half | 13 wide, 4.5 deep (`lap_w`, `fl_t / 2`); F1 is 1218.5 wide with it | ≤ 1219 so F1 stands on the 48 × 40 in pallet (packing plan, PM ruling); a tongue in 9 mm ply would leave 2 mm groove walls | confirmed (width), assumption (lap) |
| FF-04 | Foam mat 3 mm, bonded at the factory | Seals the floor to the room floor and carries F1's lap edge; one piece to carry and lay (D-87) | F1's full outline, the lap zone included, so the lap stands on foam, not on air | Firm closed-cell PE or EPDM, about 200 kg/m³ (D-76), thickness the skeleton's `mat_t` (v4); a solid rubber mat would add about 13.6 kg. No drawing: DXF and cut-list row (D-89 part 3) | confirmed (type), product HOLD (ISS-085) |

## Right band (111102), FR1 (111106) and its sill (111301): P02 batch 1

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FB-21 | 111102 as the mirror of 111101 | The right side band under R1, with the same J-BASE-01 holes (from the skeleton's `base_side_y0`), glides, keyholes for the back key at BR | Front end mitred to the intake's facet piece (DR's facet, `dr_xc`, `dr_yc`): outer corner (1250, −672), inner (1210, −654.17) | The look (Lead ruling 3): the band follows DR's facet; front key 111213's fixing holes at Y −643.59 (joints register #127) | calculation; source |
| FB-22 | FR1's length X 218.5…915 | The band under the fixed glass, from the door opening to the intake | `x_fr_joint` = pod_w/2 − dr_xc − mesh_front − fr_stub, 915 | The joint left of the mesh so the intake's key sits behind no mesh (PM rulings 2026-11-01: X 920, then X 915 for the 30 mm key) | confirmed |
| FB-23 | FR1's end plate with 2 keyholes | FR1 is the keyhole piece of the inline joint: it goes on last, down onto the intake's key studs | The tube closed at X 915 by its 1.5 wall (welded plate in the shop); Ø12 entries 10 below the seats, 6.5 slots up to them, seats at Z 37.5 and 71.5 on Y −830 | Joints register J-BASE-02 (keyhole fix, #127) | source |
| FB-24 | FR1's glides, no key holes on its top | 2 glides with doublers, 75 in from each end | Nut holes Ø13 at X 293.5 and 840 | FR1's top is in view in front of the glass, so its glides turn by their base (spanner flats on the glide, HOLD) | assumption |
| FS-01 | The sill's section: flange, ledge, drop, seat, kerb | Carries FRONT's bottom U-channel at the glass line: the ledge lies flush with the band top (Z 110), the seat sits under the channel (Z 93…95), the kerb stands on F2's tab and takes the glass's load (about 280 N) to the floor | 2 mm, 4 bends 90°; ledge Y −810…−706.5, seat Y −708.5…−689.5, kerb to Z 12 | FRONT's answer (channel 15 × 15 × 1.5, Y −706.5…−691.5, Z 95…110); PM ruling: the channel ships fitted on the sill | source; bend radius assumption |
| FS-02 | 4 holes Ø5 for flush M3 rivnuts in the seat | The channel's 4 countersunk screws (838007 into 838008) fitted in the factory | X 269.4, 484.3, 699.2 and 905 on the glass line | FRONT's channel holes; the last at 905, 2 hole diameters from FR1's end (joints register J-FRONT-04, Lead 2026-11-01) | source |

## F2 (111402), its foam (111502), the locator spigot (111801) and the threshold (111701): P02 batch 1

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FF-11 | F2's outline with its tab | The floor inside the band ring to the right of the seam, and forward under the fixed glass to carry the sill's kerb | X 0.5…1206, Y −645…806; tab X 218.5…947 to Y −691.5 | 4 mm seal gap at the band (as F1); the tab floors the strip between the glass line and Y −645 | calculation |
| FF-12 | F2's seam rebate, lower half, from below | Takes F1's lap so the seam stays flush | X 0.5…13.5, 4.5 deep | F1's lap 13 plus 1 clearance (`lap_clear`) | assumption |
| FF-13 | 2 holes Ø8 and the locator spigots 111801 | Locate the air column's foot (CEILING) | (989, −605) and (1126, −337); the spigot's Ø16 head sits in the foam's Ø17 cut-out, 8 proud of the floor top | CEILING's positions; factory-fitted from below (PM 2026-10-31) | source |
| FT-01 | Threshold section 13 mm | Meets the US accessibility limit: a 6 mm upright, then a 1:2 bevel, a flat land under the door's drop seal, then level with the floor inside | X −972…218.5 (door opening), Y −728…−645, two pockets from below | D-72; the kick strip clears it by 7 (FRONT) | confirmed; fixing HOLD |

## What is not here yet

- The front corner and inline keys (111212 to 111214, HOLD-14) and the back key's final fixing (F-018): the Joints Engineer's register PR.
- The front-left pieces under DL (with DL's spigots, register #150 and its correction), the DR intake (mesh, stub with the inline key, the closing angle carrying DR's spigots, D-62): P02 batches 2 and 3.
