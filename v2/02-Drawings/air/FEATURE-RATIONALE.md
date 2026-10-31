# Feature rationale: AIR, the air column and the soffit (AIR P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| 610000-FR | P01 | DRAFT | 2026-11-01 | CEILING Engineer (AIR) |

Why every feature of the air column, the soffit, the cartridges, the fan boxes, the riser and the roof sleeve is where it is (guideline §7). Sizes come from D-60 to D-62, D-87, the air report §7e (sized on skeleton P04) and the PM rulings of 2026-11-01; every value is a named parameter in `v2/01-CAD-Native/air/air_model.py` (the skeleton's and the ceiling's parameters load with it, so the roof slot comes from the ceiling, its owner). Coordinates: the pod system (conventions §4), mm.

## Shipping pieces (D-87: every piece 20 kg or less)

| Piece | What ships together | Mass | Status |
|---|---|---|---|
| 610201 soffit | soffit with the exhaust fan box and its 2 fans fitted at the factory | about 12 kg (CAD); the assembly guide's 13.9 | calculation |
| 610101 column | faces, foot plate, angles, plenum plates, fill, kick grille | about 10 to 12 kg (CAD) | calculation |
| 610301 cartridge × 2 | one slides into the column, one into the soffit, on site | 10.9 kg each | calculation |
| 610401 supply fan box | joined with the intake riser and the transitions (fans counted in FRONT's list) | about 9 kg | calculation |

## Air column 610101 (front-right inside corner)

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-6101-01 | Footprint | X 949…1161, Y −643.5…−285 | The supply path's column; its face flush with the soffit's | D-61 (room face 360 from the side walls' front end); 5 mm off the floating side lining, X up to 1161 (PM ruling 2026-11-01, BASE); its door side on the room-side face of DR's access panel, FRONT's named value dr_acc_face_y, so it doesn't overlap the panel (PM ruling 2026-11-01) | confirmed |
| F-6101-02 | Foot plate, 2 mm aluminium | on the mat at Z 12; Ø8.5 round at (989, −605), 8.5 × 14 slot along Y at (1126, −337) | Closes the base plenum; drops onto BASE's two Ø8 spigots on F2 (no lip to trip on) | Floor top Z 12 (3 mat + 9 ply, PM ruling 2026-11-01); spigots confirmed on F2 by BASE; round plus slot as R-J13 | confirmed |
| F-6101-03 | Faces, ACP 3 + felt 9 | front 212 wide, left 348 deep, Z 124…2120 | The room-side skin, felt-covered (D-60) | D-61, air report 7e | confirmed |
| F-6101-04 | Kick grille, 2 perforated plates | Z 24…124 on the front and the first 312 of the left face | Supply air out at the floor | D-61 (100 high, 10 above the foot) | confirmed; pattern HOLD |
| F-6101-05 | Corner angles | front 9 × 20 × 2 (×2), back-left 20 × 20 × 2 | Carry the faces; the back-left one hooks the column on | The 9 mm front legs keep the 180 hub zone free on the 212 face (PM ruling 2026-11-01) | assumption (sizes) |
| F-6101-06 | Keyholes in the back-left angle | Ø12 big hole 10 below each stud, 6.5 slot up to it, at X 971: studs at Z 1700 and 1850 | The column is pushed back onto DR's two studs and drops 10 mm; it lands on BASE's spigots at the same time | PM ruling 2026-11-01 (tool-free hooks, D-87); studs in DR's access panel (FRONT) | confirmed |
| F-6101-07 | Plenum side plates, 1 mm aluminium | X 1160…1161 at the base plenum (Z 14…134) and the top plenum (Z 1884…2120) | Close the column's right side now that it stands 5 mm off the lining; the cartridge closes the rest | PM ruling 2026-11-01 | assumption (thickness) |
| F-6101-08 | Sensor hub zone | 180 × 180 × 29 at X 971…1151, Z 1110…1290 | The in-house hub (D-70) | D-61; between the front angles' legs | confirmed; module HOLD (ELECTRICAL) |
| F-6101-09 | Supply cartridge | 173 × 314 × 1750 at X 982…1155, Z 134…1884 | Silences the supply path | D-61; 5 clear all round so it slides out | confirmed |

## Soffit 610201 (above the door head)

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-6102-01 | Envelope | X −1161…1161, Y −643.5…−285, underside Z 2120, rails' top Z 2349.24 | Exhaust path over the door head | D-61; 5 mm off both side linings (as the column); the door side on DR's access-panel face (FRONT's dr_acc_face_y), as the column; the top edge is hidden above the ceiling felt (Z 2316) | confirmed |
| F-6102-02 | Underside, 3 pieces, top band's dark tone | left hinged X −1161…−1, right hinged X 1…948, fixed X 949…1161 over the column | Opens for service of the cartridge and the fan box (D-87); the strip over the column can't swing down, so it is fixed | D-60 (dark tone), D-87 (hinged) | confirmed |
| F-6102-03 | Hinges and push latches | 2 hinges per section on the door side (Y −643.5…−638.5), 2 latches on the room side at the quarter points; the fill under the cartridge stops 8 short of the front face, so it clears the latches wherever they fall | The section swings down toward the door | D-87 | HOLD (parts) |
| F-6102-04 | Exhaust grille | 265 × 336 at X −1150…−885, in the left section | Exhaust air in | Air report 7e | confirmed; pattern HOLD |
| F-6102-05 | Front face | Z 2120…2346.24, pockets 13 × 7.5 round the two room-side stud heads | The room-side face; carries the room-side rail; its top is hidden behind the ceiling cassette's edge (felt at Z 2316) | D-61; D-90 | confirmed |
| F-6102-06 | Top rails, 3 aluminium | door side Y −643.5…−621, 22.5 wide (1 clear of the roof sleeve), room side Y −309…−285, 24 wide, Z 2346.24…2349.24 (4.76 under the ceiling frame) | Carry the soffit on the 4 studs' heads | D-90 (HOLD-18): M6 × 16 studs with 9 engaged in the ceiling's rivnuts leave 7 under the rivnut head, so the rails sit there; 6 mm heads with 1.5 clear under each | confirmed; section assumption |
| F-6102-06b | Door-side plate, 2 aluminium | Y −643.5…−641.5, Z 2140…2346.24 | Carries the door-side rail and closes the soffit's door side; stops above the hinges. It is not sealed to DR (open 4.76 under the ceiling frame, open below Z 2140), so DR's riveted back-plate band behind it stays DR's sound wall | D-90 (HOLD-18); PM ruling 2026-11-01 (DR keeps the band) | assumption (thickness) |
| F-6102-07 | Open forks in the rails | 6.5 wide, from each rail's door-side edge to the stud, at X ∓583 | Lift the soffit 24 mm back from its place, hook, slide toward the door; the forks open toward the door, so closed keyholes aren't needed where the door-side studs sit 10 in from the edge | PM ruling 2026-11-01 (forks instead of keyholes, 24 mm slide) | confirmed |
| F-6102-08 | Lock screws | 2 captive M6 × 25 (838002) through Ø6.6 holes in the door-side rail at X −1100 and −950, into C1's rivnuts | So taking out a cassette can never free the soffit; the same 5 mm key | PM ruling 2026-11-01 | confirmed; retainer HOLD |
| F-6102-09 | Exhaust cartridge and fan box | cartridge X −883…867, fan box X 867…1161 (2 fans), Z 2159…2332; the box's 2 mm casing is open on its left face (the cartridge's air comes in) and its top (the fans blow up into the roof sleeve) | Silence and drive the exhaust; the box sits under C2's roof slot | D-61, air report 7e; D-87 (fan box fitted at the factory) | confirmed |
| F-6102-10 | Left end plate, 2 mm | X −1161…−1159 | Closes the inlet plenum's end | D-87 | assumption |

## Supply fan box 610401, riser and roof parts

| Feature ID | Feature | Size, offset | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-6104-01 | Supply fan box | 300 × 155 × 300 at X 645…945, Z 1650…1950 (in DR); the 2 mm casing is open at the bottom (the riser's air comes in) and the top (the fans blow up into the upper transition) | Drives the supply; joined with the riser (D-87) | Air report 7e; all four fans are AIR's (PM ruling 2026-11-01) | confirmed |
| F-6104-02 | Intake riser, 1 mm steel | 139 × 155, Z 105…1445 (in DR) | Draws room air from low in DR | D-61 | confirmed |
| F-6104-03 | Transitions | supply box to the column top; riser to the supply box | Air path | Air report 7e | HOLD (ducts not designed) |
| F-6106-01 | Roof sleeve, 1 mm steel | 285 × 294 from the fan box top to the roof skin | Exhaust through C2's slot | D-61; slot owned by CEILING | confirmed |
| F-6106-02 | Roof grille | 305 × 314 × 2 on the skin | Covers the slot | D-61 | confirmed; pattern HOLD |
