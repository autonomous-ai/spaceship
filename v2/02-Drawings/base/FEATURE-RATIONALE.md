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
| 111601 | BASE - GLIDE DOUBLER - COMMON | 3 mm plate inside the band at each glide |
| 111401 | BASE - FLOOR PANEL - F1 | 9 mm poplar-core plywood, X −1206…+12.5, Y −645…+806 |
| 111501 | BASE - SEAL MAT - F1 | 3 mm closed-cell foam bonded under F1 (D-87) |
| 110101, 110103, 110401 | the band assemblies and F1's bonded assembly | |

The joint hardware (rivnut 838003, stop washer 831002, spigot 831001) is the joints register's (J-BASE-01, section 3.4); this file covers where BASE puts it.

## Band tubes (111101, 111103)

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FB-01 | Section 100 × 40 × 1.5 | Carries the walls to the glides; the outside dark band of v1's look | 100 tall (Z 10…110), 40 wide | Band top = `wall_z0` 110 (skeleton); the ACP's outer face flush with the band's outer face (joints register 3.4). Wall 1.5: sag 0.38 mm over the 1.33 m glide span at 0.34 kN/m, stress about 7 MPa (calculation) | section source (layout study B-BAND); wall confirmed (PM ruling 2026-10-31) |
| FB-02 | Side band front end, mitre | Meets DL's outer facet band piece face to face, so the band follows v1's faceted outline (D-01, Lead ruling 3) | Outer corner (X −1250, Y −670 = −`dl_y1`), inner corner (X −1210, Y −652.07); 24.14° from square | Bisector of the side and DL's facet direction (`dl_x2`, `dl_y1`, `dl_y2`); the same expression as the skeleton's `_ML` | calculation |
| FB-03 | Side band back end, square | Takes the end cap (118003); the back band butts the side band's inner face, as v1's frame | Y 847 = `pod_d / 2 − cap_t`, so the cap's face is flush with Y 850 | Back band 2420 long fits the 96 × 48 in pallet (layout study B1) | cap_t assumption; cap HOLD |
| FB-04 | J-BASE-01 rivnut holes Ø9.53, top wall | Nut side of the wall-to-band joint: a rivnut 838003 set through a stop washer 831002, so the wall stands on the stop at Z 112.26 (`panel_z0`) | 4 per panel at the 220 mm rule from the panel's **frame** ends (`base_bolt_edge`, `n_base_bolt`). L1: X −1224, Y −422.74, −71.83, 279.09, 630.00 (pitch 350.91). B1: Y 824, X −981.74, −728.74, −475.75, −222.75 (pitch 253.00 on the frame, PM ruling); B2 mirrored | Bolt line on the wall tube's centre: `outer_t − frame_t / 2` = 26 in from the outer face (joints register 3.4). Hole Ø9.53 +0.10/0 for CAH3-610-4.2 (maker). Grip 1.5 + 1.5 washer = 3.0, inside 0.70–4.20 | confirmed rule (D-75); hole source; rivnut torque HOLD-01 |
| FB-05 | Spigot rivnut holes Ø9.53, top wall | Hold the Ø8 locating spigots 831001 that the wall drops onto | 2 per panel, 100 in from the frame ends (`base_spigot_inset`). L1: Y −542.74, 750.00. B1: X −1101.74, −102.75; B2 mirrored | Same line as FB-04; no stop washer, so the spigot's rivnut head (0.76) stays under the wall's 2.26 gap | confirmed rule (D-75) |
| FB-06 | Glide key holes Ø10, top wall | A 5 mm hex key reaches the glide stem from above, to level the band before any wall goes on (layout study; D-87: glides preset at the factory, trimmed on site) | One over each glide: L1 band (X −1227, Y −625 and +700), back band (Y 827, X −1060, 0, +1060) | Kept inboard of the wall's gasket strip (joints register 2.4: strip 8 wide beside the washer line, outer side), hence the glide axis 3 mm inboard of the band centre (`gl_dx`); ≥ 40 mm from any rivnut | assumption (sizes); positions calculation |
| FB-07 | Glide nut holes Ø13, bottom wall | Take the M10 rivnut 838006 that carries the glide 118002 | Same X, Y as FB-06 | Ø13 for an M10 rivnut (assumption until the nut is named, HOLD) | HOLD |
| FB-08 | Glide positions | Support the band: side band glides 45 behind the band's front corner and 150 from the back face; back band at 150 from each end and the middle | Side span 1325, back spans 1060 | Sag under 0.5 mm at 1.5 mm wall (FB-01); the front glide is tied to the band's own end (`-dl_y1 + gl_e_f`), not the wall's edge, so it stays under the band when the skeleton moves | assumption (spacing), calculation (sag) |
| FB-09 | Finish | The visible dark band | Black anodised, matte, 20 µm (AA20, EN ISO 7599) | D-67 | confirmed |

## Glide doubler (111601)

| ID | Feature | Function | Size | Constraint behind it | Status |
|---|---|---|---|---|---|
| FD-01 | 3 mm plate, 36 × 30 | Spreads the glide's load across the band's 1.5 mm bottom face to both side walls | 36 wide = the 37 mm bore less 1 mm, 30 long | A ~500 N glide load on the bare 1.5 mm face bends it to about 123 MPa (Roark, plate fixed on two long edges, load on the Ø16 nut head) against a yield of about 160 for 6063-T6; with the 3 mm doubler about 31 MPa (calculation) | assumption (sizes), calculation |
| FD-02 | Hole Ø13, 3 mm off centre | The glide's M10 rivnut passes through the doubler and the bottom face, clamping both (grip 4.5) | On the glide axis, `gl_dx` toward the pod side | One part for the left, right and back bands (turned) | HOLD with the nut |

## Floor panel F1 (111401) and its mat (111501)

| ID | Feature | Function | Size, position | Constraint behind it | Status |
|---|---|---|---|---|---|
| FF-01 | Outline | The floor inside the band ring, out to the band (Lead ruling 2), so no trench is left | X −1206 (band inner face + 4 gap) to the seam; Y −645 (walls' front edge) to +806 (back band − 4) | The 4 mm gap takes the floor-edge seal 118001 (PM ruling: seal at the floor's edge, so v1's shadow line under the band stays open) | confirmed (rulings), gap assumption |
| FF-02 | 9 mm thickness on a 3 mm mat | Floor top Z 12, so the door threshold is 13 mm (US accessibility) | Z 3…12 | D-72; poplar-core with a hard face veneer, about 450 kg/m³ (D-85); edge deflection about 0.6 mm under 1000 N on the firm foam (calculation, test PLANNED) | confirmed (thickness), assumption (density) |
| FF-03 | Half-lap at the F1/F2 seam | Keeps the seam flush with no glue; F1's lower half runs under F2's upper half | 13 wide, 4.5 deep (`lap_w`, `fl_t / 2`); F1 is 1218.5 wide with it | ≤ 1219 so F1 stands on the 48 × 40 in pallet (packing plan, PM ruling); a tongue in 9 mm ply would leave 2 mm groove walls | confirmed (width), assumption (lap) |
| FF-04 | Foam mat 3 mm, bonded at the factory | Seals the floor to the room floor; one piece to carry and lay (D-87) | F1's outline less the lap zone | Firm closed-cell PE or EPDM, about 200 kg/m³ (D-76); a solid rubber mat would add about 13.6 kg | confirmed (type), product HOLD (ISS-085) |

## What is not here yet

- Back corner joint: the Joints Engineer's hook-in corner key (D-87). The band ends stay square until it is drawn (HOLD).
- Front band pieces (faceted, under DL and DR), the DR intake mesh piece with its support and closing plate (D-62), the right side, F2 and the 13 mm threshold: revision P02.
