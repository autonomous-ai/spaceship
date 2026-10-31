# Assembly tree: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-002 | P01 | DRAFT | 2026-10-31 | Control pack |

One tree for the whole pod (guideline §4.1). POD splits into BASE, WALL, FRONT, CEILING, LINING, AIR, ELECTRICAL and INTERIOR. PACKAGING is the delivery configuration of the POD, not a branch of it. Family numbers follow the PROPOSED part-number scheme (`conventions.md` §6). Sides and position codes follow `conventions.md` §4.

What this file gives you:
1. the tree;
2. every node, with its contents, part classes, plan items, plan VT codes and v1 counterparts;
3. where every plan VT code and every build-plan item goes;
4. the interfaces between neighbouring assemblies;
5. the v1 BOM codes behind each node;
6. the vocabulary.

Part classes (guideline §4.1): **MP** a part we make, **BS** a bonded subassembly, **HS** a subassembly fitted with hardware, **PI** a bought item, **KIT** the installation kit.

## 1. Tree

```
100000  POD - SPACESHIP (FocusPod v2) ................................. Pod hoàn chỉnh
├── 110000  BASE ............................................................ Đế / sàn
│   ├── FLOOR PANEL F1..Fn            thin floor, DECIDED (D-05) ............. Tấm sàn mỏng
│   ├── BASE RAIL - PERIMETER         locates and fixes the walls ............ Thanh biên đế
│   ├── BASE SEAL + UNDERLAY                                                Gioăng đế, lớp lót sàn
│   ├── THRESHOLD 20 mm (D-18)        door edge of the floor ................. Ngưỡng cửa
│   ├── ALUMINIUM BASE BAND           outside, keeps the v1 look; the thin
│   │                                 floor sits inside it (D-18) ............ Nẹp chân nhôm
│   └── (build plan's raised floor, dropped by D-05, for reference only)
│       FLOOR FRAME 50x100 + 30x60, 6 LEVELING FEET M10, 2 FLOOR BOARDS ..... Khung sàn, chân tăng đưa, ván sàn
├── 210000  WALL ............................................................ Vách
│   ├── LEFT WALL  - PANEL ASSY L1, L2 ....................................... Vách trái
│   ├── RIGHT WALL - PANEL ASSY R1, R2 ....................................... Vách phải
│   └── BACK WALL  - PANEL ASSY B1..B4 ....................................... Vách hậu
│        each panel, 81 mm (D-16, D-17), made at the factory as 2 parts:
│        OUTER PANEL = SKIN ACP 3 + FRAME AL 20x40 at 400 + PET FILL 40 + GASKETS
│                      + captive M6 bolts or tool-free connectors
│        LINING CASSETTE (510000) = steel tray 0.5 + 25 air gap + felt 9, floating
├── 350000  FRONT ........................................................... Mặt trước
│   ├── DECOR BLOCK DL, DR, DT  (AL frame + ACP grooved and folded;
│   │                            hinge pocket in DL, D-19) ................. Khung trang trí trái, phải, trên
│   └── 360000  DOOR AND GLAZING
│       ├── DOOR LEAF + HINGES + HANDLE SET + CATCH + DOOR SEALS .............. Cửa, bản lề, tay nắm, gioăng
│       ├── FIXED PANEL + GLAZING PROFILES + SETTING BLOCKS + SEALS .......... Vách kính cố định
│       └── (both panels smoked acrylic, laminated glass as the fallback, D-07)
├── 410000  CEILING - PANEL ASSY C1, C2  (same stack on AL 20x100, 141 mm;
│                                          silencer and fan openings) ...... Trần
├── 510000  LINING - CASSETTES: steel tray + felt, made at the factory, floating Tấm tiêu âm
├── 610000  AIR - 2 FANS 12 V DC (1 in, 1 out) + SILENCERS + GRILLES / SLOTS .. Thông gió
├── 710000  ELECTRICAL ...................................................... Điện
│   ├── MAINS: inlet, protection, user socket (the only mains point inside)
│   ├── 12 V DC BUS: power supply, fused branches, harness with joint connectors
│   ├── DESK PRO AI SENSOR HUB (in-house: CO2, presence, air quality, sound level)
│   ├── LIGHTS 12 V: 1 dimmable LED ceiling light + front face light (D-20); LAN socket
│   └── VOICE COCKPIT HOOKS: 12 V 5 A outlet, data link, mounts, cable path
│       (kit later, on the in-house Lamp electronics)
├── 810000  INTERIOR - empty (no furniture); inside trims only ................ Nội thất
└── 109000  POD - INSTALLATION KIT  (spare captive M6 bolts, the one tool, packers) Bộ phụ kiện lắp

910000  PACKAGING - delivery configuration of 100000 POD ...................... Đóng gói
        48 x 40 in pallets + one standard long pallet, decor not split (D-04);
        protection, labels, kit box
```

## 2. Nodes

| Node | Name · Vietnamese | v2 contents | Classes | Build plan | Plan VT | v1 counterpart (BOM code) | Status |
|---|---|---|---|---|---|---|---|
| 100000 | POD · Pod hoàn chỉnh | Everything below; overall size 2500 × 1700 × 2400 | — | BP-01…BP-05 | — | the whole v1 (STEP root "Indoor Pod V3 (Assembly)") | DRAFT |
| 110000 | BASE · Đế / sàn | Thin floor panels inside the aluminium base band (D-18), base rail, base seal and underlay, 20 mm threshold (D-18). The thin floor is DECIDED (D-05); its build is PROPOSED (open-questions Q4). The plan's steel floor frame, 6 feet and 2 boards are dropped. | MP, HS, PI | BP-24, BP-30, BP-08 | VT03-ST, VT04, VT12, VT05 (assumption) | FL-01…FL-13, FLR-01, MUA-01 | DECIDED (D-05) |
| 210000 | WALL · Vách | Left L1–L2, right R1–R2, back B1–B4 outer panels: ACP 3 skin, aluminium 20 × 40 frame at 400, 40 mm PET fill, gaskets, captive M6 bolts or tool-free connectors, electrical back boxes. 81 mm with the lining cassette, 13.1 kg/m² (D-16, D-17). Seams: 2 sheets per side wall, 4 at the back, aligned reveals (D-23). No plywood. | MP, BS, HS, PI | BP-06, BP-07, BP-25, BP-26, BP-27 | VT01, VT10, VT11 (VT02 dropped) | LW-01…08, RW-01…08, BWL-01…07, BWC-01…06, BWR-01…07; v1 VT-01…VT-03 (M8 screws and inserts) | DECIDED stack (D-16, D-17) |
| 350000 | FRONT · Mặt trước | Decor blocks DL, DR, DT (aluminium frames, D-16; ACP in Dark Yellow, D-12; not split, D-04; hinge pocket in DL, D-19) with their brackets; door and glazing (360000) | MP, BS, HS, PI | BP-29 | VT01, VT10, VT05 (assumption) | DL-01…17, DR-01…32 (+ CAD "Decor Right (DR2)"), DT-01…24 | DRAFT |
| 360000 | FRONT - DOOR AND GLAZING · Cửa và kính | Door leaf and fixed panel in smoked acrylic, or laminated glass as the fallback (D-07), hinges, handle set, catch, glazing profiles, setting blocks, perimeter and drop seals. Not in the build plan (ISS-001, ISS-002, ISS-003). | PI, HS | — (gap) | — | GL-01, GW-01, MUA-09 (hinges), MUA-10 (handle) | DECIDED material (D-07) and hand (D-19); hardware PROPOSED (Q1) |
| 410000 | CEILING · Trần | Panel assemblies C1 (−X half) and C2 (+X half): the wall stack on a 20 × 100 × 1.5 aluminium frame, 141 mm, 17.4 kg/m² (D-16); fan openings with slot patterns; reserved sprinkler zone; voice cockpit front zone | MP, BS, HS | BP-06, BP-07, BP-28 | VT01, VT10, VT11 (VT02 dropped) | CL-01…05 | DECIDED stack (D-16) |
| 510000 | LINING · Lớp tiêu âm | Lining cassettes for the walls and ceiling: a 0.5 mm galvanised steel tray with 25 mm returns, a 25 mm air gap and 9 mm PET felt on its face, made at the factory (D-08, D-17). Each cassette ships as its own part, hangs on the frame with tool-free clips and never touches it through a screw (floating). The gap is also the spare cable path (ISS-069). | MP (cut felt), PI | BP-07 | VT03-PET | none: v1 had no felt. Its inner layer was plywood LW-04, RW-04, BWL-05, BWC-04, BWR-05, CL-03, plus the yellow inner sheet BWC-07. | DECIDED pre-fitted (D-08) |
| 610000 | AIR · Thông gió | 2 fans in the ceiling (1 in, 1 out) on the 12 V DC bus (D-10), CO2-driven and self-starting through the sensor hub, 70 l/s and 25 dB(A) or less (D-09); silencers, grilles or slot pattern; airflow to REQ-AIR | PI, MP | BP-09, BP-28 | VT06 | MUA-02 (4 fans in 2 units) | DECIDED targets (D-09, D-10); fans OPEN (ISS-039) |
| 710000 | ELECTRICAL · Điện | Per D-10 and D-11. Mains: 220 V inlet (prototype), protection, the user socket (the only mains point inside). 12 V DC bus: power supply, fused branches, harness. In-house Desk Pro AI sensor hub (CO2, presence, air quality, sound level). 12 V LED lights and soft front light, LAN socket. Voice cockpit hooks: fused 12 V 5 A outlet, data link, mounts, cable path. | PI, HS | BP-10 | VT07, VT08, VT09 | MUA-03…MUA-08 | DECIDED architecture (D-10, D-11); design OPEN (ISS-004, ISS-005, ISS-060, ISS-061, ISS-062) |
| 810000 | INTERIOR · Nội thất | Nothing: the pod ships empty. Inside trims only, if any. | MP | — | — | TB-01…03 (table, removed: ISS-006); BWC-07 inner decor sheet (replaced by felt) | DECIDED: no furniture (D-06) |
| 109000 | POD - INSTALLATION KIT · Bộ phụ kiện lắp | Spare captive M6 bolts, the one hand tool, packers, labels. Most connectors arrive fitted to the panels. | KIT | BP-22 | VT11 | none (v1 BOM lists screws but no kit) | DRAFT |
| 910000 | PACKAGING · Đóng gói | Pallets, crates, protection, labels, the kit box; layout from the layout study | MP, PI | BP-02 goal 5 | — | none in the v1 files. The v1 summary lists the largest units: ceiling 2480 × 1486 × 64, side wall 64 × 1496 × 2300. | DECIDED pallets (D-04); layout OPEN |

## 3. Where every plan code and plan item goes

### 3.1 Plan material codes VT01…VT12

| Plan code | Material (build plan) | Node | Where used | v2 status |
|---|---|---|---|---|
| VT01 | Tấm ốp Aluminium Composite Panel 3 mm, Dark Yellow EV3038 · ACP skin | WALL, CEILING, FRONT | Outer skin of every wall and ceiling panel; decor skin, grooved and folded | Kept. Spec gaps ISS-035; decor colour ISS-031. |
| VT02 | Ván plywood 6 mm · plywood backer | WALL, CEILING | Under the ACP, bonded to it and screwed to the frame | Dropped: no plywood behind the ACP (D-17) |
| VT03-PET | Tấm tiêu âm Polyester Fiber 9 mm, Dark Gray · acoustic felt | LINING | On the lining cassette's face, walls and ceiling | Kept, pre-fitted on the cassette (D-08, D-17). Code clash ISS-007. |
| VT03-ST | Thép hộp 50×100 · steel box tube | BASE | Outer frame of the plan's raised floor | Dropped: thin floor (D-05) |
| VT04 | Thép hộp 30×60 · steel box tube | BASE | 2 joists of the plan's raised floor | Dropped: thin floor (D-05) |
| VT05 | Thép tấm 3 mm · steel plate | BASE, FRONT (assumption) | No step in the plan uses it; probably brackets | Open (ISS-037) |
| VT06 | Quạt thông gió Panasonic FV-15AUL1 · fan | AIR | Ceiling, one per half: 1 in, 1 out | A mains fan clashes with the 12 V DC bus; 12 V DC fans to pick (ISS-039) |
| VT07 | Công tắc 1 chiều + ổ cắm 5 chấu UTEN S300 · switch and socket | ELECTRICAL | Back wall, inside | Socket kept: the only mains point inside. Switch role open (ISS-061). |
| VT08 | Bộ triết áp quạt UTEN S300 · fan speed knob | ELECTRICAL (controls AIR) | Back wall, inside | Can't drive 12 V fans; the sensor hub controls them (ISS-038) |
| VT09 | Ổ cắm đơn mạng UTEN S300 · network socket | ELECTRICAL | Back wall, inside | Kept; voice cockpit data path starts here |
| VT10 | Thép hộp 20×20 · box tube | WALL, CEILING, FRONT | Panel frames and decor core frames | Aluminium (D-16): 20 × 40 at 400 for walls, 20 × 100 for the ceiling; alloy and wall thickness ISS-034 |
| VT11 | Bolt M6×60 | POD - INSTALLATION KIT | Site joints IF-01, IF-03 to IF-08 | Kept as the one bolt size (ISS-036, ISS-011) |
| VT12 | Chân tăng đưa M10 · leveling foot | BASE | Under the plan's floor frame | Dropped: thin floor (D-05) |

### 3.2 Build plan items

| Plan item (`requirements.md` §G) | Node | Interfaces |
|---|---|---|
| BP-01 overall size | POD | IF-17 |
| BP-02 goals | POD | — |
| BP-03 sketches, BP-04 components, BP-05 modelling order | POD (CAD method) | — |
| BP-06 wall-to-wall joint section (rule 4) | WALL, CEILING | IF-03, IF-04, IF-05 |
| BP-07 glue, screws, hook-and-loop (rule 5) | WALL, CEILING, LINING | IF-10 |
| BP-08 walls bolted to the floor with M6 (rule 6) | BASE, WALL | IF-01 |
| BP-09 fans in the ceiling, 1 in and 1 out (rule 7) | AIR, CEILING | IF-11, IF-14 |
| BP-10 VT07–VT09 on the back wall (rule 8) | ELECTRICAL, WALL | IF-12 |
| BP-11 … BP-23 materials VT01 … VT12 | see 3.1 | — |
| BP-24 section I, floor frame | BASE | IF-01, IF-02 |
| BP-25 section II, left wall | WALL | IF-01, IF-03, IF-04, IF-05, IF-07 |
| BP-26 section III, right wall | WALL | IF-01, IF-03, IF-04, IF-05, IF-07 |
| BP-27 section IV, back wall | WALL | IF-01, IF-03, IF-04, IF-05, IF-12 |
| BP-28 section V, ceiling | CEILING, AIR | IF-05, IF-06, IF-08, IF-11, IF-13 |
| BP-29 section VI, decor frame | FRONT | IF-02, IF-07, IF-08, IF-09 |
| BP-30 section VII, floor boards | BASE | IF-01, IF-19 |
| Plan gap: door, fixed glass, hinges, handle, seals, lights, wiring, power inlet | FRONT (360000), ELECTRICAL | IF-02, IF-09, IF-12, IF-13 |
| D-11: voice cockpit hooks (12 V 5 A, data, mounts, cable path) | ELECTRICAL, WALL, CEILING, FRONT | IF-15, IF-16 |
| D-09, D-10: 12 V DC bus, mains to outlets only; in-house sensor hub | ELECTRICAL, AIR | IF-12, IF-13, IF-14, IF-20 |

## 4. Interfaces between neighbouring assemblies

Each interface becomes one or more Joint Register entries (J-BASE-01, J-WALL-01 …, guideline §8) when it is designed. "Plan" is what the build plan says. "v2 working answer" is PROPOSED unless marked otherwise.

| IF | Between | What crosses it | Plan | v2 working answer | Issues |
|---|---|---|---|---|---|
| IF-01 | BASE – WALL (L, R, B) | Weight of the walls and roof down to the room floor; racking; base seal; position | Walls bolted to the floor frame with M6 (rule 6) | The thin floor lies inside the aluminium base band (D-18). Wall bottom rails stand on the room floor on the base seal, are located by the floor's perimeter base rail, and fix to it with tool-free connectors or captive M6 bolts (thin floor D-05, fixing D-08; rail PROPOSED, open-questions Q4) | ISS-040, ISS-050, ISS-054, ISS-011 |
| IF-02 | BASE – FRONT | Decor blocks DL and DR stand on the base; threshold under the door; bottom glazing profile; drop seal strike | Not covered | Threshold profile on the floor's front edge; base trim continues under the decor | ISS-053, ISS-022, ISS-003 |
| IF-03 | WALL – WALL at the back corners (BL: L–B, BR: R–B) | Racking, position, seal; the side wall skin covers the back wall edge | M6×60 between frames; side ACP covers the back wall frame (II) | Captive M6 bolts or tool-free connectors (D-08), a corner gasket and a locating feature | ISS-011, ISS-003 |
| IF-04 | WALL – WALL inside one wall (L1–L2, R1–R2, B1…B4) | Panel-to-panel shear, seal, visible seam | M6×60 between frames (II–IV) | Captive M6 bolts or tool-free connectors (D-08) and a seam gasket; the seam layout is a look question | ISS-044, ISS-011 |
| IF-05 | WALL – CEILING | Roof weight onto the walls; position; seal; the side wall skins cover the ceiling edge | Ceiling between the side walls on their frames, 1 mm gap, bolts (rule 4 picture) | Captive M6 bolts or tool-free connectors (D-08), a gasket in the gap; cables for fans and lights cross with a plug | ISS-011, ISS-003, ISS-012 |
| IF-06 | CEILING – CEILING (C1–C2) | Shear, seal, seam at X = 0 | M6×60 (V) | Captive M6 bolts or tool-free connectors (D-08) and a seam gasket | ISS-011 |
| IF-07 | WALL – FRONT (left wall – DL, right wall – DR) | Decor weight; **door load through DL**; position; seal; depth chain | V brackets and steel screws (VI) | Brackets with captive M6 bolts or tool-free hooks (D-08); overlap per the depth chain | ISS-014, ISS-045, ISS-012 |
| IF-08 | CEILING – FRONT (C1, C2 – DT) | Top decor weight; seal; voice cockpit front zone | "3 blocks to 3 walls" (VI); the top block actually meets the ceiling | Brackets with captive M6 bolts or tool-free hooks into the ceiling front edge (D-08) | ISS-045, ISS-051 |
| IF-09 | Inside FRONT: DL–DT, DR–DT; door – DL (hinges); door – fixed panel (slanted joint); fixed panel – DR, DT, BASE (profiles) | Door weight and moment; seals; panel edge clearances | Not covered | Hinges on DL (left, as v1); a seal on the slanted joint; fixed panel in sealed U profiles; panels in smoked acrylic or laminated glass (D-07) | ISS-001, ISS-002, ISS-003, ISS-023, ISS-024, ISS-059 |
| IF-10 | WALL, CEILING – LINING | The lining cassette hangs on the frame; felt and cassette edges at panel joints; cut-outs for boxes and lights; cables in the 25 mm gap | Hook-and-loop last, on site (rule 5) | Floating cassette on tool-free clips, never a screw (D-17); made at the factory (D-08); edges at each joint so the gasket seals and the bolt or connector stays reachable | ISS-015, ISS-064, ISS-069 |
| IF-11 | CEILING – AIR | Fan mounting, openings and slot patterns, silencer depth; the ceiling build is only about 38 mm thick | Fan in each half, slots below (V) | Fan and silencer housing sized by the air design; any housing above the roof keeps the roof look (one grille per half, as BP p1) | ISS-010, ISS-039, ISS-049 |
| IF-12 | WALL (back) – ELECTRICAL | Back boxes for VT07–VT09; mains inlet and the user socket; the 12 V power supply and its heat; cable route inside the back wall band | VT07–VT09 on the back wall (rule 8) | Mains stays in the back wall band (inlet to socket only); 12 V supply in the same band; route up to the ceiling; inlet kept inside the 1700 depth or listed as a protrusion | ISS-005, ISS-025, ISS-062 |
| IF-13 | CEILING – ELECTRICAL | 12 V lights and front light, 12 V cables to the fans, sprinkler or alarm reserve | Not covered | Lights per open-questions Q2; plug connectors at the WALL–CEILING joint so panels come apart | ISS-004, ISS-052, ISS-062 |
| IF-14 | AIR – ELECTRICAL | 12 V fan power, speed, boost, start on presence | VT08 knob only | The sensor hub drives the fans from presence and CO2; wired in; any manual trim is a 12 V input | ISS-038, ISS-039 |
| IF-15 | ELECTRICAL – voice cockpit kit (later, on the Lamp electronics) | Fused 12 V 5 A outlet, data link (Ethernet + spare cable), cable ends | Not covered | REQ-VCK-03, -04, -05; REQ-ELE-03 load budget | ISS-051, ISS-060 |
| IF-16 | WALL (back), CEILING, FRONT (DT) – voice cockpit kit (later) | Hidden M6 mounting points: screen, speakers and computer on the back wall's middle band; mic array and status light at the ceiling front or DT | Not covered | REQ-VCK-01, -02, -06 | ISS-051, ISS-060 |
| IF-17 | POD – room (site) | Room floor flatness, power point, clear space above the roof for the fans, later sprinkler and alarm | Not covered | Install requirements sheet (to write) | ISS-049, ISS-054, ISS-052 |
| IF-18 | POD – PACKAGING | Every shipped item has a pallet place, protection and a label (part number + position code); kit box | Goal 5 only | 48 × 40 in pallets plus one standard long pallet, decor not split (D-04); layout from the layout study | ISS-057, ISS-048 |
| IF-19 | BASE – INTERIOR (customer furniture) | Customer furniture and people stand on the thin floor; no fixings into walls unless reserved | Floor boards on joists (VII) | Thin floor rated for office use; the load value is still to set (assumption, to check against an office floor-load standard) | ISS-040 |
| IF-20 | ELECTRICAL (sensor hub) – pod air and occupants | The hub must see the seated person and sample breathing-height air, away from the supply jet and the exhaust | Not covered | Placement rule REQ-ELE-04, set with the air design | ISS-060 |

## 5. v1 counterparts by BOM code (reference only)

| v1 BOM code | v1 item (Vietnamese) | v1 STEP component | v2 node | Notes |
|---|---|---|---|---|
| FL-01…FL-10 | Khung sàn: hộp thép 100x50, 60x30, 20x20 | Floor Frame (FL) | BASE (dropped) | Replaced by the thin floor (D-05) |
| FL-11 | Ốp mép sàn trước (nẹp ngưỡng cửa) | Floor Frame (FL) Body50 | BASE (threshold, trim) | Material conflict ISS-022 |
| FL-12, FL-13 | Pát | Floor Frame (FL) "Base Pat…" bodies | BASE | Bracket list incomplete, ISS-026 |
| FLR-01 | Sàn: ván gỗ 9 mm (2 tấm) | Floor (2 bodies, 15 mm) | BASE (floor panels) | 9 vs 15 mm, ISS-018 |
| LW-01…LW-08 | Vách trái: khung gỗ 40x40, ốp trong, ván 6 mm, nhôm 2 mm | Left Wall (LW) | WALL L1, L2 | v1 frame is wood; v2 is tube |
| RW-01…RW-08 | Vách phải | Right Wall (RW) | WALL R1, R2 | |
| BWL-01…BWL-07 | Vách sau – trái | Back Wall Left | WALL B1, B3 | |
| BWC-01…BWC-07 | Vách sau – giữa, incl. lỗ đi dây, cụm điện, ốp trang trí mặt trong | Back Wall Center | WALL B-wall; ELECTRICAL zone; BWC-07 to INTERIOR | Labelled 6 mm on the drawing, ISS-028 |
| BWR-01…BWR-07 | Vách sau – phải | Back Wall Right | WALL B2, B4 | |
| CL-01…CL-05 | Trần (ván trong có lưới lỗ thông gió) | Ceiling (CL) | CEILING C1, C2 | |
| DL-01…DL-17 | Decor mặt trước – trái | Tấm Decor Left (DL) | FRONT DL | Colour ISS-031 |
| DR-01…DR-32 | Decor mặt trước – phải | Tấm Decor Right (DR), (DR2) | FRONT DR | DR2 not in the BOM, ISS-029 |
| DT-01…DT-24 | Decor mặt trước – trên | Tấm Decor Top (DT) | FRONT DT | |
| GL-01 | Cửa kính xám khói 10 mm | Door | FRONT 360000 door leaf | Trapezoid, ISS-023; smoked acrylic in v2 (D-07) |
| GW-01 | Vách kính cố định 10 mm | Wall Glass | FRONT 360000 fixed glass | 3 sizes in v1, ISS-023 |
| TB-01…TB-03 | Bàn | Table | INTERIOR (removed) | ISS-006 |
| VT-01, VT-02, VT-03 | Vít M8x60, M8x40, tán cấy M8x20 | — | WALL joints (v2 uses M6) | Not plan VT codes, ISS-033 |
| MUA-01 | Chân tăng chỉnh D50 ren M12 (6) | Adjustable D50xM12 (8 instances, 6 places) | BASE (dropped, D-05) | ISS-017 |
| MUA-02 | Quạt thông gió 200x200x60 (4) | Ventilation Fan (2 units) | AIR | |
| MUA-03 | Đèn ốp trần vuông 170x170 (2) | Ceiling Light (1) | ELECTRICAL | ISS-019 |
| MUA-04…MUA-06 | Công tắc, ổ cắm, ổ LAN (mặt 86x86) | Switch, Outlet, LAN | ELECTRICAL | |
| MUA-07, MUA-08 | Jack LAN, jack nguồn | Jack LAN, Power Jack | ELECTRICAL (inlet) | Protrudes 18 mm at the back, ISS-025 |
| MUA-09 | Bản lề cửa kính (3) | Shower Hinges (3 instances, 2 places) | FRONT 360000 | ISS-024 |
| MUA-10 | Tay nắm cửa kính 300 mm | Handle (outside only) | FRONT 360000 | ISS-056 |

## 6. Vocabulary

| English (v2 documents) | Vietnamese (team) |
|---|---|
| base · thin floor panel · floor frame · floor board | đế · tấm sàn mỏng · khung sàn · ván sàn |
| leveling foot | chân tăng đưa (plan), chân tăng chỉnh (v1) |
| left wall · right wall · back wall | vách trái · vách phải · vách hậu (plan), vách sau (v1) |
| ceiling · roof skin | trần · tấm ốp nóc |
| decor frame · decor block | khung trang trí · khối trang trí |
| skin · backer · frame · box tube | tấm ốp · ván lót · khung · thép hộp |
| acoustic felt · hook-and-loop | tấm tiêu âm · miếng dán Velcro |
| bolt · screw · bracket · V bracket · rivet nut | bulong · vít · pát · pát V · tán rút |
| glue · seal / gasket | keo · gioăng |
| door · fixed glass · hinge · handle · threshold | cửa · vách kính cố định · bản lề · tay nắm · ngưỡng cửa |
| fan · switch · socket · network socket · fan speed knob | quạt thông gió · công tắc · ổ cắm · ổ cắm mạng · chiết áp quạt |
| light · table · packaging | đèn · bàn · đóng gói |
