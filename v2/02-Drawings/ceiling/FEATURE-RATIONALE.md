# Feature rationale: ceiling panels, frames, skins and cassette (CEILING P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| 410000-FR | P01 | DRAFT | 2026-11-01 | CEILING Engineer |

Why every feature, hole, slot, gap and pitch on the ceiling is where it is (guideline §7). Values are at P01 on skeleton P04 as updated in place by PR #58 (frames 1198.99, skins 1200.61, the bolt line at Z 2374), with the D-60 soffit over the door head (360 deep: `cs_front` = 360). Every value is a named parameter in `v2/01-CAD-Native/ceiling/ceiling_model.py`; the skeleton's own parameters load from its CSV at build time.

Coordinates: the pod system (conventions §4) for the frames and skins; the cassette's own system **CS-510301** for the cassette: X' along the pod's X with 0 on the cassette's centre line, Y' toward the back with 0 on the soffit's back face (pod Y −285), Z' up with 0 on the tray top (Z 2350, 4 mm under the roof frame). At C1 the origin is at pod X −583, at C2 at +583; the cassette is the same part at both (PM ruling 2026-10-31).

Status words follow conventions §9. **HOLD** marks a feature whose geometry waits for a named part (guideline §4.3).

## Ceiling frames 411101 (C1) and 411102 (C2): welded galvanized steel (D-131), 20 × 40 and one 40 × 40, 1.0 and 0.8 walls

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-01 | Frame width | 1198.99 (skeleton `half_fw`), from the closing face at X ∓2.75 to the side stop at X ∓1201.74 | Leaves the 5.5 mm frame gap at the C1–C2 closing seam, which takes the ceiling's tolerance (ST-04) | `half_fw` = (pod_w − 2 outer_t − 2 seam_gap − close_gap) / 2 (skeleton P04, PM ruling 2026-10-31) | calculation |
| F-4111-02 | Side member 412101 (one part for both frames: C2's is C1's turned upside down) | X −1201.74…−1181.74 (C1), Y −645…850, the frame's full depth; mitred from the outer to the inner corner, 45° at the front, 63.43° at the back (D-117) | Bolt side of J-CEIL-01 against the upper side panel's 40 × 40 top member; every feature centred across its 40 face, so one part serves both sides | D-55, D-117, D-120; Control's allocation 2026-11-01 (412201 cancelled) | confirmed |
| F-4111-03 | Seam member 412102 (C1) / 412202 (C2) | X −22.75…−2.75 (C1), Y −645…850; mitred 45° at the front, 63.43° at the back (D-117) | The closing face of J-CEIL-02; C1's carries the pins' Ø7.0 holes and C2's the rivnuts, so the two differ | close_gap / 2 each side of X 0; D-117, D-120 | confirmed |
| F-4111-04 | Back member 40 × 40, 412104 (C1) / 412204 (C2) | the frame's full width, Y 810…850; cut 26.57° off square at both corners (D-117) | Nut side of J-CEIL-01's back edge: sits on the back panel's top tube (Y 804…844); its spigot hole and slot make it handed | R-J3; D-117, D-120 | confirmed |
| F-4111-05 | Front member 412103 (C1) / 412203 (C2) | the frame's full width, Y −645…−625; 45° mitres (D-117) | Closes the frame; carries the soffit's door-side hanger rivnuts, and C1's the two lock rivnuts, so the two differ | D-55; D-87; D-117, D-120 | confirmed |
| F-4111-06 | Cross member X1, 412105 (one part for both frames: C2's is C1's turned end for end) | Y −301…−281, square cut between the side and seam members | Sits 16 mm over the soffit's back edge so the soffit's back studs have a member above them; its one hanger rivnut sits at the same distance from the seam end in both frames | D-87; D-120; Control's allocation 2026-11-01 (412205 cancelled) | confirmed |
| F-4111-07 | Cross members X2, X3: 412001, one plain part (4 per pod) | Y 92.5…112.5 and 461.25…481.25 (368.75 pitch from the front member), square cut | Support the bonded ACP at 400 or less (D-16, X1 to X3) | D-16; D-120 | confirmed |
| F-4111-15 | Clearances | every bolt 30 or more from any member meeting its own (side bolts: 148 or more) | Stiles move, never bolts | R-J14 (checked by the offline tests) | calculation |
| F-4111-16 | Roof slot clearance (C2) | C2's side access holes 24.7 from the slot's edge | The roof sleeve and the soffit come out before any ceiling bolt is turned, and go in after | Joints register 3.5 (D-60 note); assembly order R-J9 | calculation |
| F-4111-17 | Member joints | welded in a jig: each corner with a 2.0 mitre plate (831007 at the front, 831008 at the back: square-ended blanks, 26.5 from 1.75 and 41.5 from 3.15 along the mitre, so both ends sit 0.5 inside the frame's faces, #308), the T joints direct; beads ground on the skin and closing faces; burnt zones wire-brushed and coated with 2-component zinc-rich epoxy; no vent or drain holes; joint holes made after welding | One stiff frame without glued cleats; the plate carries the corner (the register's corner check) | D-131 (the cleats of D-115 and D-117 cancelled); joints register J-FRAME-01 | confirmed (method); the weld notes follow WALL's L1 sample review |
| F-4111-18 | Plate cut-backs and gauges | each mitred end cut back square to its mitre by half the plate: 1.41 along the member at 45°, 2.24 off the side and seam members and 1.12 off the back member at the back corners; walls 1.0 (side, seam, front, back, X1) and 0.8 (X2, X3); S280GD+Z or SGC400, Z100 | The plates fit and the outside sizes stay; the gauges carry the site joints (1.0 under every rivnut, bolt, spigot and hanger stud) and the lining's clips (0.8) | J-FRAME-01 (D-131): the joints register's gauge and steel rows | confirmed |

Each member's holes, under the member that carries them (D-120: each member its own part). Under D-162 a member has
no sheet of its own: its drawing is its row in the frame's cut list on the frame's weldment sheet, and these holes go on
that sheet, since every joint hole is made after welding (J-FRAME-01), located from the frame's joint faces and its
spigot hole. So is the seam's lead-in (F-4111-12), ground with the closing face's beads. No member has a before-weld
feature: its length and end cuts, the plates' cut-backs too, are its cut list row.

### Side member 412101 (both frames; C2's is C1's turned upside down)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-08 | Side bolt holes, J-CEIL-01 | Ø7.0 in the outer wall and Ø19 in the inner wall, 4 at Y −425, −73.33, 278.33, 630 (from Y −645: 220, then 351.67), Z 2374 | Bolt side: captive M6 × 16 into the wall's rivnuts; the 5 mm key reaches in through the Ø19 from the frame's open bay | Joints register 2.9 owns the bolt lines (PM ruling 2026-10-31): 220 rule along the ceiling's 1495, bolt line on the tube's centre (R-J15) | confirmed |

### Seam members 412102 (C1) and 412202 (C2)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-11 | Closing seam pins, J-CEIL-02 | C1: Ø7.0 in the closing face; C2: Ø10.00 (D-163) rivnut in the closing face and Ø19 access in the face toward the frame's bay; 4 at Y −425, −73.33, 278.33, 630 (the side bolts' Y), Z 2374 | The M6 × 25 pin from C2's rivnut crosses the 5.5 gap into C1's hole: holds the faces flush, pulls nothing | Joints register 2.10, 3.6 | confirmed |
| F-4111-12 | Lead-in | 1 × 45° on the closing face's lower edge (seam member and back member end) | C2 drops past C1 without catching the bulb seal | R-J9 | confirmed |

### Back members 40 × 40, 412104 (C1) and 412204 (C2)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-09 | Back rivnut holes, J-CEIL-01 | Ø10.00 (D-163), 4 in the back member's underside at Y 824, X ∓222.75, ∓475.75, ∓728.74, ∓981.74 (from the closing face: 220, then 253.00) | Nut side: rivnuts on Ø20 stop washers set the 2.26 gap to the back panel | Joints register 2.9 (220 rule on the 1198.99 frame; 4 per back panel, PM correction 2026-10-31); Y on the back tube's centre (R-J15) | confirmed |
| F-4111-10 | Spigot hole and slot | Ø8.5 round at X ∓102.75; 8.5 × 14 slot along X at X ∓1101.74; Y 824 | Each half drops onto the back panel's two spigots | R-J13 (100 from each end). Round at the seam end because ST-04 runs from the round hole to the closing face (±0.1); the slot lets the side bolts pull the half onto its stops | confirmed |

### Front members 412103 (C1) and 412203 (C2)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-13 | Soffit hanger rivnuts, front member | Ø10.00 (D-163) in the front member's underside, Y −635, at X ∓583 | The soffit's 4 keyhole studs (AIR) | PM ruling 2026-11-01 (D-87). On 20 mm faces: edge distance 5.0 with D-163's Ø10.00 (5.2 with the Ø9.53; HOLD-04, as the register) | confirmed; edge distance HOLD-04 |
| F-4111-19 | DT's bolt holes, J-FRONT-03 | Ø7.0 in the front wall (Y −645) and Ø19 in the back wall, on DT's bolt line Z 2374: C1's at X −981.74, −578.16, −174.58, C2's at X +229.00 (from C1's frame end at X −1201.74: 220, then 403.58) | DT's back plate bolts to the front tubes: an M6 × 16 from inside the tube into DT's rivnut, its head and Ø18 washer reached through the Ø19 from the open bay before the soffit goes up | Joints register 3.13 (J-FRONT-03, IF-08, FR-19) and 2.9's 220 rule along DT's 1650.74 edge with the ceiling. C1's middle bolt sits 4.84 from the soffit's front hanger rivnut (X −583, on the underside) inside the same tube: its washer and head stay 2.4 and 4.3 clear of the rivnut's body (calculation, offline test) | PROPOSED (J-FRONT-03) |

### Cross member 1, 412105 (both frames; C2's is C1's turned end for end)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-13A | Soffit hanger rivnuts, cross member 1 | Ø10.00 (D-163) in X1's underside, Y −291, at X ∓583 | The soffit's 4 keyhole studs (AIR) | PM ruling 2026-11-01 (D-87). On 20 mm faces: edge distance 5.0 with D-163's Ø10.00 (5.2 with the Ø9.53; HOLD-04, as the register) | confirmed; edge distance HOLD-04 |
| F-4111-14 | Soffit lock rivnuts | Ø10.00 (D-163) in cross member 1's underside at X ∓1100 and ∓950, Y −291, in both frames; only C1's take the two captive M6 screws | Two captive M6 screws lock the soffit, so taking a cassette out can never free it. They moved off C1's front member when DR's new removable panel brought the soffit's door side to about Y −639.6: the front member's rivnuts can't leave its middle (5 mm of flat to the tube's side, HOLD-04), and the door-side rail would have left 4.6 mm to its edge. On the room-side rail the loaded edge is 18 mm away. C2's cross member carries the mirrored rivnuts unused (they sit over the column's fixed underside), so the member stays one part (412105) | PM rulings 2026-11-01 (D-87 hooks; option b for DR's panel face, the Lead). Over the soffit's left inlet plenum, where no cartridge is: the key reaches them through the left hinged underside | confirmed |

The plain cross member 412001 (X2, X3, 4 per pod) has no holes.

## Skins 411301 (C1) and 411302 (C2): ACP 3, EV3038 Dark Yellow

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4113-01 | Skin | 1200.61 × 1495 × 3, from X ∓1.13 to ∓1201.74 | The roof; overhangs its frame by 1.62 at the closing seam, so the outside seam is one 2.26 gap | Skeleton `half_pw` (PM ruling 2026-10-31) | calculation |
| F-4113-02 | Bond | 3 bond line (skeleton `bond_t`), bond set 108002 | Bonds skin to frame | Bond spec V2-ENG-BND | source |
| F-4113-03 | Roof exhaust slot (C2 only) | 285 × 294 at X 872…1157, Y −620…−326 | The exhaust leaves through the roof over the soffit's fan box; AIR's roof sleeve, 1.0 smaller a side (D-177), drops through it | D-61 (5 mm clear of the front member); the two skins are two parts (PM ruling 2026-10-31) | confirmed |
| F-4113-04 | Clearance holes under the roof sleeve's rivnuts (C2 only) | 4 × Ø17 (`hole_slv`): 2 at X 852, Y −600 and −346 (20 left of the slot); 2 at Y −273, X 892 and 1137 (behind cross member 1) | Each passes a rivnut 838003 that the factory sets in the sleeve's flange (its body 9.91, and the bulge about 14 across that forms right under the flange, in the skin's hole) wherever the sleeve lands in its slot. They are new holes in the outer leaf, so the flange closes them: its butyl ring, outside the four holes, seals them and the sleeve's gap in the slot (REQ-VCK-06; J-AIR-03, AIR's list) | D-177 (PM ruling 2026-11-01): 14 (`slv_bulge`, assumption; Sherex gives no size) + 2 × (1.0 play in the slot + 0.5 for the two holes' positions, ±0.2 each). At full play the back pair's bodies clear cross member 1 by 1.5, and the flange covers each hole with 10.0 outside it: room for the 8-wide ring placed to ±0.5, with 1.5 to spare (tests) | calculation |

## Tray 513101, galvanised steel DX51D+Z 0.5 (sheet metal)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513101-01 | Base | 1160 × 1045 outside, X' ±580, Y' 3…1048 | Carries the fill and the clips; the cassette's back skin (D-17) | Half the 2332 inside width, from the soffit's back face to the back lining (1414 − 360 = 1054), less a 3 mm gap each side (`cs_gap`, assumption) | calculation; gap assumption |
| F-513101-02 | Four returns | 34 deep overall | Make the 24 mm air gap (D-17, D-41), stiffen the edges | `tray_h` = `cass_t` 34 (skeleton) | confirmed |
| F-513101-03 | Lips, 12 inward | felt seat at Z' −33.5 | Hold the felt mechanically (guideline §8.2) | PM ruling 2026-10-31 | confirmed |
| F-513101-04 | Bend radius, K-factor | r = 0.5, K 0.44 | Flat pattern | Until the factory's tooling sets them (guideline §9) | assumption |
| F-513101-05 | Cable holes, front and back returns | Ø19.1 at X' 0, Z' −12.5 | Voice cockpit route and spare path (D-41, REQ-VCK-03, ISS-069) | ELECTRICAL's cable bushing needs a 19.1 panel hole (PM ruling 2026-11-01) | confirmed |
| F-513101-06 | Clip zones (6) | 40 × 30 at X' ±193.33 on the back faces of X1, X2, X3: Y' 4…34, 397.5…427.5, 766.25…796.25 | Hang the cassette (D-47, D-81: clips only); the clip latches when pushed home, so the cassette holds itself overhead before its catches go on (Packing's assembly review, PM ruling 2026-11-01) | Over the ribs; on the back faces so every clip stays over the cassette | HOLD (HOLD-08) |
| F-513101-07 | Catch zones (2) | 40 × 30 at X' ±193.33, Y' 347.5…377.5 (X2's front face) | A cassette over people can't drop (D-47) | Near the middle so it hangs level; never shares a fixing with a clip | HOLD (HOLD-08) |

## Rib 513102 (2 per cassette), DX51D+Z 0.5

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513102-01 | Hat section | crown 20, height 24, flanges 2 × 12 | Keeps the felt flat; stiffens the base under the clips | 24 = the air gap | calculation; assumption |
| F-513102-02 | Position | X' ±193.33 (`cs_w` / 6) | Three equal felt spans | PM ruling 2026-10-31 (2 ribs) | confirmed |
| F-513102-03 | Length | 1034, 5 clear of each return | Fits inside the returns | 1045 − 2 × 0.5 − 2 × 5 | calculation |
| F-513102-04 | Fixings | — | Rib to tray, felt to rib | H09 | HOLD |

## Felt 513201, PET 9, Dark Gray (no drawing: a plain knife-cut rectangle, D-89; its parts-list row is the cut list)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513201-01 | Panel | 1157 × 1042 × 9 on the lips, no holes | The room face (D-17, D-53); the lights are on the wall-top light shelf (D-70) | 1 mm clear of the returns (`felt_c`) | calculation |
| F-513201-02 | Sprinkler reserve | Ø150 zones at X' ±386.67, Y' 190.75 in each cassette (pod X ±196.3 and ±969.7, Y −94.2), marked on the felt, nothing cut | A sprinkler head can be fitted later without cutting a member (REQ-US-01). Clear through every layer: no frame member, rib, clip, catch or cable in a zone, the draw wire 387 away on the cassette's centre line, the roof slot 25 or more away (tests); the skin, tray, felt and fill are cut only when a head is fitted. D-131's steel frames keep the same geometry, so the zones stay clear | The middle of the outer felt spans and of the bay between X1 and X2; the PM's provision 2026-11-01 (zero cost, no holes now) | assumption (the zone size), calculation (the clearances) |

## Fill 513301, 513302, 513303, PET 40 at 24 kg/m³ (D-81; one tabulated drawing, D-89)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-5133-01 | Strips in the bays over the cassette | 1110.5 long (X' ±555.25); 363.5 (bay X1–X2), 338.75 (X2–X3), 271.75 (X3–back) | Fill the cavity (D-24) | 5 clear of every member (`fill_c`), trimmed by the seam member at its new place (close_gap) | calculation |
| F-5133-02 | Notches | 50 × 30 round each clip and catch | Room for the clips and catches | + 5 each side | calculation (HOLD sizes) |
| F-5133-03 | Fixing to the tray | — | Keep the strips in place in transport | H10; gravity in service | HOLD |

## What the cassette never has

- No screw or bolt to the frame (D-17): only the clips and the catches touch it.
- No cable fixed to the frame (D-26).
- No hole in the outer skin except C2's roof slot (D-61) and the four clearance holes under the roof sleeve's flange (F-4113-04, D-177), which the flange and its butyl ring close (REQ-VCK-06).
