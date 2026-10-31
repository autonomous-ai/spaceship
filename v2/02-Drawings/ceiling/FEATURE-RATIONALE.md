# Feature rationale: ceiling cassette and ceiling frame (CEILING P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| 510301-FR | P01 | DRAFT | 2026-10-31 | CEILING Engineer |

Why every feature, hole, slot, gap and pitch on the ceiling cassette (sample S3, drawing D06 of the wall-and-door sample) and on the ceiling frames it hangs from is where it is (guideline §7). Values are at P01 with the D-60 soffit over the door head (360 deep, so `cs_front` = 360: both cassettes stop 3 mm behind its back face); every one is a named parameter in `v2/01-CAD-Native/ceiling/ceiling_model.py`, and the skeleton's own parameters load from its CSV at build time.

Coordinates: the pod system (conventions §4) for the frames; the cassette's own system **CS-510301** for the cassette: X' along the pod's X with 0 on the cassette's centre line, Y' toward the back with 0 on the soffit's back face (pod Y −285: the decor's back plate Y −645 plus `cs_front` 360), Z' up with 0 on the tray top (Z 2353, 4 mm under the roof frame). At C1 the origin is at pod X −584.5, at C2 at +584.5; the part is the same at both (PM ruling 2026-10-31), because every feature below is symmetric about X' = 0.

Status words follow conventions §9. **HOLD** marks a feature whose geometry waits for a named part (guideline §4.3): only its space is kept, with no holes.

## Ceiling frame 411101 (C1) and 411102 (C2), aluminium 20 × 40 × 1.2

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-4111-01 | Side member (along Y) | X −1204.74…−1184.74 (C1), 1495 long | Edge member against the side wall frame; carries the half's side edge | D-55 (frame to frame, side skins cover the edge); seam gap 2.26 to the side frame (PM ruling 2026-10-31, the Joints Engineer's stop washer) | confirmed |
| F-4111-02 | Seam member (along Y) | X −21.13…−1.13 (C1), 1495 long | Joins C1 to C2 at the centre seam; with its twin forms the 40 × 40 seam beam | Half the 2.26 seam gap each side of X = 0 | confirmed |
| F-4111-03 | Front and back members (along X) | Y −645…−625 and 830…850, 1163.61 long, between the side and seam members | Close the frame; the back one sits over the back wall's top | D-55; back outer frames run up to the ceiling frame (PM ruling 2026-10-31) | confirmed |
| F-4111-04 | Cross members X1, X2, X3 (along X) | centres 368.75 apart from the front member: Y −266.25, 102.5, 471.25 (centre lines) | Support the bonded ACP at 400 or less (D-16); carry the 6 cassette clips (back faces) and the 2 catches (X2's front face) | (1495 − 20) / 4 = 368.75 (calculation); 3 cross members (PM ruling 2026-10-31) | confirmed (count); calculation (pitch) |
| F-4111-05 | Member joints | — | Join the members into one frame | Not decided: H11 (sample hold list) | HOLD |
| F-4111-06 | Joints to the walls, to C2 and to the top decor block | — | IF-05, IF-06, IF-08 | Waiting for the joints register's table (J-CEIL entries) | HOLD |

## Tray 513101, galvanised steel 0.5 mm (sheet metal)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513101-01 | Base | 1163 × 1048 outside, X' ±581.5, Y' 3…1051 | Carries the fill on its back and the clips; the cassette's back skin (sound mass, D-17) | Envelope 1169 wide (skeleton C1-CASS, D-55), from the soffit's back face to the back lining's face (1414 − 360 = 1054), less a 3 mm gap each side (`cs_gap`, assumption: room for the 3.2 mm PORON gasket, selection D) | calculation; gap assumption |
| F-513101-02 | Four returns | outer faces on the base outline, 34 deep overall | Make the 24 mm air gap (D-17, D-41) and stiffen the edges; carry the gasket on their outer faces | `tray_h` = `cass_t` 34 (skeleton); return flange 33 plus the lip bend 1 (r + t) | confirmed (34, D-42 stack) |
| F-513101-03 | Lips, 12 mm inward, mitred corners | felt seat at Z' −33.5 | Hold the felt's edges mechanically, so the felt can't drop on people even if a bond fails (guideline §8.2) | PM ruling 2026-10-31 (12 mm lip) | confirmed |
| F-513101-04 | Bend radius and K-factor | r = 0.5 (= t), K 0.44 | Flat pattern size | Assumption until the factory's tooling and a bend coupon set them (guideline §9) | assumption |
| F-513101-05 | Corner relief | square, from the sheet metal rule | Lets the four returns fold without tearing | Fusion rule (relief = thickness) | assumption |
| F-513101-06 | Cable hole, back return | Ø20 at X' 0, Z' −12.5 (mid gap) | The reserved voice cockpit route comes in at the back-wall top corner and runs in the gap (D-41, D-26, REQ-VCK-03); also the spare path (ISS-069) | Ø20 for a grommet: grommet not named | assumption; grommet HOLD |
| F-513101-07 | Cable hole, front return | Ø20 at X' 0, Z' −12.5 | Opens toward the soffit: the cockpit route on to its front zone (mic array and status light, REQ-VCK-02, REQ-VCK-03) | as F-513101-06 | assumption; grommet HOLD |
| F-513101-08 | Clip fixing zones (6) | 40 × 30 at X' ±193.83, against the back faces of X1, X2, X3: Y' 28.75…58.75, 397.5…427.5, 766.25…796.25 | Hang the cassette from the frame (D-47) | Over the ribs, so the load goes into the stiffened zone; on cross members so both cassettes match; on the back faces so every clip stays over the cassette for any soffit up to about 385 mm | HOLD (H03, ISS-076): no holes until a clip is named with its rating |
| F-513101-09 | Catch anchor zones (2) | 40 × 30 at X' ±193.83, Y' 347.5…377.5 (in front of X2) | Safety catch: a cassette over people can't drop (D-47) | Over the ribs, near the cassette's middle (524) so it hangs level; on X2's front face while the clips use its back face, so catch and clips never share a fixing | HOLD (H04, ISS-076) |

## Rib 513102 (2 per cassette), galvanised steel 0.5 mm

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513102-01 | Hat section | crown 20, height 24, flanges 2 × 12 | Keeps the felt flat between the lips (crown carries the felt), stiffens the 0.5 mm base under the clips | 24 = the air gap (34 − 9 − 2 × 0.5); crown and flanges assumption | calculation; assumption |
| F-513102-02 | Position | X' ±193.83 (`cs_w` / 6) | Three equal felt spans of 387.7 between lip, rib, rib and lip | PM ruling 2026-10-31 (2 ribs); equal spans (calculation) | confirmed (count); calculation |
| F-513102-03 | Length | 1037, 5 clear of each return | Fits inside the returns | 1048 − 2 × 0.5 − 2 × 5 | calculation |
| F-513102-04 | Rib to tray, felt to rib | — | Fix the ribs and keep the felt on the crowns | Not designed: H09 (felt fixing); rib fixing to be set with it | HOLD |

## Felt 513201, PET 9 mm

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-513201-01 | Panel | 1160 × 1045 × 9, on the lips, no holes | The room face; sound absorption on the 24 mm gap (D-17, D-53). No lights in the ceiling: they sit on a light shelf along the tops of the side and back walls (PM ruling 2026-10-31, interior design) | Inside the returns less 1 mm each side (`felt_c`, assumption), so it drops onto the lips | calculation |
| F-513201-02 | Sprinkler reserve (2 candidates) | Ø150 zones at X' ±387.67, Y' 203.13 (mark only, nothing cut) | Keeps a clear path for a later sprinkler drop (REQ-US-01) | One each side so the cassette stays one part: the middle of the outer felt spans and of the first frame bay over the cassette, clear of ribs, clips and members (checked by the tests) | assumption |

## Fill 513301, 513302, 513303, PET 40 mm at 25 kg/m³ (PM ruling: the default; the wall sample's T02 confirms it, else 32)

| Feature ID | Feature | Size, offset, pitch | Function | Constraint source or calculation | Status |
|---|---|---|---|---|---|
| F-5133-01 | Strips in the frame bays over the cassette | 1116.74 long (X' ±558.37); widths 338.75 (bays 1 and 2), 274.75 (bay 3); 40 thick; bay 0 lies over the soffit and gets none | Fill the outer panel's cavity (D-24: the fill rides on the cassette, so each outer panel stays at 20 kg or less) | 5 mm clear of every member (`fill_c`, assumption) so the cassette never touches the frame (D-17); both ends trimmed by the seam member, so the strip and the cassette stay symmetric | calculation |
| F-5133-02 | Notches | 50 × 40 round each clip (front edges of bays 1, 2, 3) and each catch (back edge of bay 1) | Room for the clips and catches | clip or catch space + 5 mm each side | calculation (HOLD sizes) |
| F-5133-03 | Fixing to the tray back | — | Keep the strips in place while the cassette ships upright | Not designed: H10. In service the strips lie on the tray, so gravity holds them; a fixing failure can't drop anything into the room | HOLD |

## What the cassette never has

- No screw or bolt to the frame (D-17): only the clips and the catches touch the frame, and both are HOLD.
- No cable fixed to the frame (D-26): cables clip to the tray inside the gap.
- No hole in the outer skin (REQ-VCK-06).
