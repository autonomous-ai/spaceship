# Build list: what the factory builds

| Doc code | Revision | Status | Date |
|---|---|---|---|
| V2-SMP-WD (proposed) | P01 | DRAFT | 2026-10-31 |

The factory builds three items exactly as the pod will get them (S1 to S4, with the door on HOLD), plus the items and rigs the tests need (S5 to S7, R1 to R4). Build each one to its Milestone 2 drawing ([drawings-needed.md](drawings-needed.md)). Where a drawing or a part isn't ready, that item waits; [hold-list.md](hold-list.md) says what blocks it. Part IDs P01… are in [parts-list.md](parts-list.md); tests T01… are in [test-plan.md](test-plan.md).

Positions follow `conventions.md` §4: left and right are as seen from outside, facing the door. Sizes are in mm, given as X × Y × Z in the pod system where the skeleton gives them. Masses come from the layout study (LS, PR #20) and are calculations until T10 weighs the real parts.

## Pod items

### S1 · Lower side wall panel L1, outer panel · Vách trái - cụm tấm dưới

| | |
|---|---|
| Position | L1: the left wall's lower panel (−X side). R1 is its mirror (RH) and isn't built. |
| Size | 43 × 1495 × 1145 (skeleton L1). Depth 1495 confirmed by D-49, 43 = 3 ACP + 40 frame (D-16, D-42). |
| Mass | 11.9 kg (calculation, LS): ACP 6.0, frame 3.3, fill 2.2 at 32 kg/m³, bond lines 0.4 (assumption at 0.25 kg/m²) |
| Build, outside to inside | ACP 3 mm EV3038 (P01), bonded (P04) to an aluminium 20 × 40 × 1.2 frame (P02) with members 400 mm apart or less (D-16, D-34). 40 mm PET fill (P03) in the frame's bays. Gasket (P14J) on its joint faces, beside the washer line. For the base joint: 4 captive M6 × 16 bolts (P06 with P25, held by P26) in its bottom tube, with 7.0 mm clearance and 19 mm access holes, and a spigot hole and slot; the joint's rivnuts are in the band (R1). Its back member is 40 × 40 × 1.2 (P02C), for the corner joint (joints register J-BASE-01, J-WALL-02). |
| Not in it | The lining cassette (S2 is a separate part, D-17). No plywood (D-17). No screw goes through to the cassette. |
| Tests | T01, T02, T10, T11; T09's cut-open bond check comes last, because it destroys the skin bond |

### S2 · Lining cassette for L1 (L1-CASS) · Cassette lót vách trái dưới (khay thép + tấm tiêu âm)

| | |
|---|---|
| Size | 34 × 1448 × 1145 (skeleton L1-CASS). 1448 runs past the back cassette's face to close the inside corner (D-57). |
| Mass | 11.1 kg (calculation, LS): tray 7.0, felt 3.0, clip and rail allowance 1.0 (assumption at 0.6 kg/m²), felt fixing 0.1 (assumption) |
| Build | Galvanised steel tray 0.5 mm (P08) with 25 mm returns (D-17, D-37). The factory's 9 mm PET felt (P09) across its face, its edges fixed to the returns (H09). 4 captive mechanical clips with a rated load (P11, H03) on the returns. Hook-and-loop only to line it up (P13, D-47). PORON gasket round its outer edge (P14). |
| How it fits | It clips onto S1 from inside with a 4 mm gap and never screws to the frame (D-17). Any cable in the 25 mm gap clips to the cassette only (D-26). |
| Tests | T01, T02, T10, T11; T07's clip coupons are cut from the same return |

### S3 · Ceiling cassette (510301, one part for both halves) with its safety catches · Cassette trần (dùng chung trái/phải) + dây an toàn

| | |
|---|---|
| Size | The real ceiling cassette from the CEILING Engineer's PR #32: one part serves both halves, and it stops behind the D-60 soffit. Tray outline 1163 × 1048 × 34 in PR #32's current build, made on skeleton P03's parameters; PR #32's model gives 1160 × 1045 × 34 on skeleton P04, and S3 is built to that rebuild. Flat blank 1251.53 × 1136.52 × 0.5 (PR #32's build). 40 mm fill strips on its back (D-24): 74 thick as shipped (source: PR #32) |
| Mass | About 9.8 kg with its fill: 9.816 kg in PR #32 (tray 5.548, 2 ribs at 0.370, felt 2.182, fill strips 1.346; calculation from its CAD), plus clips and catches (HOLD). The layout study's 13.2 kg was the full 1414 length with no soffit. The hardware selection's older figure is about 16 kg (HW-SEL A8); T07 and T08 keep ISS-076's 16 kg, the larger, until T10 weighs S3. |
| Build | PR #32's parts: the 0.5 mm galvanised tray (P08), its returns the full 34 mm deep and turned in as 12 mm lips that hold the felt's edges; 2 hat ribs, 0.5 mm (P08), so the felt spans three equal widths; the 9 mm felt on the lips (P09); the gasket on the returns' outer faces (P14); 40 mm PET fill strips on the tray's back (P03, fixing H10); 6 captive clips (P11, H03) and 2 steel lanyards with a rated working load (P12, H04). Each lanyard is fixed to the cassette and to a 20 × 40 ceiling member (D-42). |
| Tests | T07, T08, T10 |

### S4 · Door unit (HOLD) · Cửa kính + thanh nhôm chân cửa

| | |
|---|---|
| Size | 2096 × 1176 × 20 envelope (LS): 2011 of glass plus the 85 mm kick strip (D-57) |
| Mass | 47.5 kg as it hangs (D-46, D-56): about 43.3 kg of glass plus 4.2 kg of kick strip, drop seal, three hinges and pull |
| Build | 4+4 laminate of toughened, heat-soaked grey panes, 8.76 mm, cut to v1's trapezoid, 1175.6 at the bottom, 892.9 at the top, 2011.1 tall (REQ-LOOK-04, D-46). Glass product on HOLD (H02). An aluminium kick strip 85 mm tall in the base band's dark finish, holding the drop seal (D-40, D-57). Hinges, lock and pull rated for this glass, 47.5 kg and 1176 mm (H01). Seals (P23). |
| Tests | T13 (HOLD) |
| HOLD | Don't build it until H01 and H02 are released. |

## Test items

### S5 · Air sample in the D-60 air column and soffit mock-ups · Mẫu thông gió (ống tiêu âm + quạt thông gió)

| | |
|---|---|
| What | Both splitter cartridges (one part, used twice), the supply fan box with 2 × 12 V fans on a level bulkhead and its transition into the column top, the exhaust fan box with 2 × 12 V fans and the roof sleeve (P15 to P17, P19), and the intake riser (P18), built as the pod gets them (D-60) |
| Sizes and masses | Each cartridge 173 × 314 × 1750: two 80 mm passages between three 50 mm Pyrotek layers in a 2 mm aluminium casing, 11.2 kg. Supply fan box 300 × 155 × 300 with its transition, 5.1 kg with fans 5.7 kg; exhaust fan box 294 × 314 × 173 with the roof sleeve, 3.5 kg, with fans 4.1 kg. Intake riser 139 × 155, widening to 250 where it turns into the fan box, 1740 long, 9.2 kg with its mesh (calculation, HW-AA sections 7e and 7f, PR #26). |
| Test box (rig R3) | The D-60 air parts as the pod gets them (sizes: HW-AA section 7e). (a) The air column, 217 × 360 × 2105 outside (skeleton P04): front and left faces 3 mm ACP (P20) with 9 mm felt (P09), so the fan sound breaks out through the same skin; the front face lifts off; a 100 mm kick grille at its foot; 30 mm of fill between the cartridge and both faces (P03). It stands against a backboard in place of the right decor block's inner face, with the 203 × 215 opening at the top. Behind the backboard, a box of the block's column shape (skeleton DR, below Z 2120) holds the riser and the supply fans, behind a removable panel. (b) The soffit, 2332 × 360 × 220 outside: underside and front face as the column, the exhaust grille (265 × 336) in the underside at one end and the exhaust fan box at the other, blowing up through a sleeve in place of the roof slot. Any rigid build will do for the backboard and the column-shape box. The intake comes in as in the pod: through a flush black mesh band piece along the box's foot, 371 mm long (front and corner facet) × 100 mm, 80% free (PM, on skeleton P04), into the space under the column-shape box, closed from the pod side by a plate. The intake and the roof sleeve open to the room, at least 1 m apart (D-58). |
| Tests | T04, T05, T10 (weigh the cartridges, fan boxes, riser and fans), T12 |
| HOLD | The CAD of the column, soffit, riser and intake isn't done yet (H07: CEILING and FRONT). If the CAD moves a grille, the opening or the intake, R3 follows the CAD. |

### S6 · Felt absorption specimen · Mẫu tấm tiêu âm

| | |
|---|---|
| What | The factory's 9 mm PET felt (P09) over a 25 mm air space, as on the cassette face; about 12 m² (unverified: ISO 354's specimen area is about 10 to 12 m², and the lab confirms it) |
| Tests | T03 |

### S7 · Coupons · Mẫu thử

| Coupon | What | Count | Test |
|---|---|---:|---|
| Rivnut | A 300 mm piece of the 20 × 40 × 1.2 tube from the frame's own batch, with one rivnut (P05) set through a stop washer (P07) in a 40 mm face, as in the joint (joints register 2.2) | 15 (assumption: 10 for spin-out, 5 for the cycle check) | T06 |
| Bond | A lap-shear pair: an ACP strip (P01) on a 150 mm tube piece, bonded the way S1 is bonded | 10 (assumption: 5 as cured, 5 aged) | T09 |
| Clip | A strip of the cassette's 0.5 mm return (P08) with one clip (P11), and its mate on a 150 mm tube piece | 10 (assumption: 5 in shear for the wall, 5 in pull-out for the ceiling) | T07 |

## Rigs (not product)

| Rig | What | Test |
|---|---|---|
| R1 | Base band rig: a base band piece, aluminium 100 × 40 × 2.0 (P24; LS), with 2 spigots 100 mm in from its ends and 4 rivnuts (P05) with stop washers (P07) at the 220 mm rule, matching S1's base holes (joints register J-BASE-01), per the BASE drawing (H17) | T11 |
| R2 | Ceiling hanging frame: 20 × 40 × 1.2 members (P02) at the cassette's clip and catch positions (PR #32: 6 clips on the back faces of the three cross members, over the ribs, and 2 catches on the middle member's front face), on a stand at the pod's ceiling height, about 2.3 m inside (D-42) | T07, T08 |
| R3 | The D-60 air mock-up for S5 (above): the air column with its backboard, riser box and supply fans, and the soffit with its exhaust fans and roof sleeve | T04, T05, T12 |
| R4 | Heated chamber on R3's inner side: a closed box over the column's kick grille and the soffit's exhaust grille that takes the supply air and feeds the exhaust, as the pod's inside would, with an adjustable heater (P21) | T05 |
