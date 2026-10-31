# Parts list: materials and parts for the sample

| Doc code | Revision | Status | Date |
|---|---|---|---|
| V2-SMP-WD (proposed) | P01 | DRAFT | 2026-10-31 |

One row per material or part. Quantities are what the sample items need (gross, before the factory's cutting waste). The method behind each is in the row. Products are the ones the hardware selection picked (HW-SEL), with no prices and no supplier contact. Where nothing is picked, the row says HOLD and gives no part number. Part numbers for our own parts come from the master BOM in Milestone 2; none is assigned here (D-22, D-28).

The **Status** column gives the status of the numbers in that row (confirmed, source, calculation, assumption or unverified). **HOLD** points to [hold-list.md](hold-list.md).

## Wall panel S1 and cassettes S2, S3

| ID | Part · Vietnamese | For | Qty | Maker · product | Status | Source | HOLD |
|---|---|---|---|---|---|---|---|
| P01 | ACP 3 mm, Dark Yellow EV3038 · tấm ốp alu | S1 skin; S7 bond strips from the offcut | 1 sheet 1500 × 3000 (the skin is about 1495 × 1145 plus any return the skin drawing adds) | Nhôm Việt Dũng · Alcorest outdoor ACP, EV3038, 3 mm × 0.21 mm skins, PE core | source (product, sheet sizes); calculation (fit); confirmed (colour, D-12) | HW-SEL A1 | H16 |
| P02 | Aluminium tube 20 × 40 × 1.2 · khung nhôm | S1 frame 8.7 m; S7 coupons 7.5 m; R2 frame 9.0 m | 25.2 m | Stock tube; alloy, temper and finish recorded by the factory | confirmed (size, D-34); calculation (S1: perimeter 5.28 m plus 3 members of 1.145 m; R2: C1's 1207 × 1495 the same way, 9.03 m; coupons 15 × 0.3 + 20 × 0.15 m); unverified (alloy) | LS frame model; HW-SEL A4; ISS-034 | H11, H15 |
| P03 | PET cavity fill 40 mm, 32 kg/m³ · bông PET | S1 bays 1.71 m²; S3 back 1.65 m²; S5 fill toward the inner face 1.70 m² | 5.07 m² at 40 mm | Pyrotek · Sorberpoly 2D polyester, 32 kg/m³ (40 mm is a custom thickness; 25 and 50 are standard) | confirmed (grade, D-54); source (product); calculation (S1 1495 × 1145; S3 1169 × 1414; S5 2 × 405 × 2100) | HW-SEL B and F2; LS | |
| P03L | PET cavity fill 40 mm, the lighter grade · bông PET loại nhẹ | S1 bays, for T02 | 1.71 m² at 40 mm | Pyrotek · Sorberpoly 2D, 24 kg/m³ (D-54 calls it 25; 24 is the grade Pyrotek lists) | source (grade); calculation (area) | HW-SEL B; D-54 | |
| P04 | Bond, ACP to aluminium · keo dán | S1; S7 bond coupons | per the bead and tape pattern (D10); the factory works the amount out from the maker's coverage data | Sika · SikaTack Panel-50 with SikaTack Panel Fixing Tape | source (product) | HW-SEL A9 | H12 |
| P05 | M6 rivet nut · tán rút (tán rive) | S1 base joint 4; S7 rivnut coupons 15; spares 5 | 24 | Sherex by PEM · CAH3-610-4.2, aluminium 5056, grip 0.70–4.20, hole 9.53 (+0.10), set with the maker's tool for it | source (part and hole); assumption (S1's 4 is the layout study's count estimate for J-BASE-01; coupon and spare counts) | HW-SEL A5; LS joints | H05 |
| P06 | M6 bolt, ISO 4017 class 8.8, zinc · bulong M6 | S1 base joint 4; T06 15; spares 6 | 25 × M6 × 50 | Standard part | source (standard); assumption (length: one 40 mm member into a rivnut needs about M6 × 50 until the joint register sets it) | HW-SEL A5 | H13 |
| P07 | M6 washer, ISO 7089, zinc · long đen M6 | With P06 | 25 | Standard part | assumption (whether a washer is used is the joint register's call) | proof feature rationale; GL §8.1 | |
| P08 | Galvanised steel sheet 0.5 mm · khay thép lót | S2 tray 1.79 m²; S3 tray 1.78 m²; S7 clip strips 0.15 m² | 3.72 m² | EN 10346 DX51D+Z, coating mass to confirm | source (material); calculation (S2: 1448 × 1145 face plus 25 mm returns; S3: 1169 × 1414 the same way; 10 strips of 300 × 50); unverified (supplier) | HW-SEL B; LS | |
| P09 | PET felt 9 mm, Dark Gray · tấm tiêu âm PET (plan VT03-PET) | S2 1.66 m²; S3 1.65 m²; S6 12 m²; R3 inner panel 2.33 m² | 17.6 m² | The factory's 9 mm PET felt (D-31) | unverified (the felt's own data); calculation (faces); assumption (S6 at 12 m²) | HW-SEL A3; D-31; LS | H08 |
| P10 | Felt edge fixing to the tray returns · cố định mép tấm tiêu âm | S2, S3, R3 inner panel | per D05 and D06 | Not designed | assumption (the layout study allows 0.05 kg/m²) | LS felt_fix_kgm2 | H09 |
| P11 | Captive mechanical clip, rated · kẹp treo cassette | S2 4; S3 6; S7 10; spares 4 | 24 | None named. Candidate: Häfele KEKU EH suspension fitting (20 kg vertical, 8 kg horizontal per a distributor page; rating basis not stated) | source (counts per cassette); assumption (coupon and spare counts); unverified (candidate's rating) | HW-SEL A8; D-47; ISS-076 | H03 |
| P12 | Ceiling safety catch: steel wire lanyard with a rated working load, and its two end fixings · dây an toàn trần | S3 2; T08 spares 2 | 4 | None named | source (2 per ceiling cassette) | HW-SEL A8; D-47; ISS-076, ISS-079 | H04 |
| P13 | Hook-and-loop, only to line up · miếng dán Velcro | S2, S3 | per D05 and D06 | VELCRO® Brand PS14 hook 25 mm, or 3M Dual Lock SJ3560 | source (products; locating only, no load rating) | HW-SEL A8 | |
| P14 | Gasket 3.2 mm with PSA, 10–20 mm strip · gioăng | S2 edge 5.19 m; S3 edge 5.17 m; S1 base and corner faces 2.64 m | 13.0 m | Rogers · PORON 4701-40 Soft, laminated with PSA by a converter | source (product); calculation (S2: 2 × (1448 + 1145); S3: 2 × (1169 + 1414); S1: 1495 + 1145) | HW-SEL D | H14 |

## Air sample S5

| ID | Part · Vietnamese | For | Qty | Maker · product | Status | Source | HOLD |
|---|---|---|---|---|---|---|---|
| P15 | 12 V fan · quạt thông gió 12 V | S5, two per cartridge; 1 spare | 5 | Noctua · NF-A14 industrialPPC-3000 PWM, 12 V, 140 × 140 × 25 | source (product, size); assumption (0.3 kg each, weighed in T10) | HW-SEL F1; D-51 | H06 |
| P16 | Cartridge casing, aluminium sheet 2.0 mm · vỏ ống tiêu âm | S5, 2 cartridges | 5.0 m² | Alloy not set | source (2 mm, HW-SEL F2); calculation (per cartridge 2 × (159 + 405) × 2100 + 2 × 159 × 405 mm², from the sound check's cartridge geometry); unverified (alloy) | HW-SEL F2; HW-AA calc.py | H07 |
| P17 | Cartridge linings and fan box linings, 25 mm, 32 kg/m³ · lớp tiêu âm ống | S5, three layers per cartridge plus the fan boxes | 5.05 m² at 25 mm | Pyrotek · Sorberpoly 2D, 25 mm (standard thickness), 32 kg/m³ | source (product, published ISO 354 data at 25 mm); calculation (2 × (3 × 405 × 1800 + 2 × (405 + 155) × 300) mm²) | HW-SEL B and F2; HW-AA calc.py | |
| P18 | Exhaust riser, galvanised steel sheet 1.0 mm · ống thải đứng | S5 riser 150 × 155 × 2000 | 1.22 m² | Galvanised steel, grade as P08 | source (1 mm, HW-SEL F2); calculation (2 × (150 + 155) × 2000 mm²) | HW-SEL F2 | H07 |
| P19 | Fan bulkhead and fan box parts · vách đỡ quạt | S5 | per D08 | Not designed | — | HW-SEL F1 | H07 |
| P20 | ACP 3 mm for R3's inner face · tấm ốp alu mặt trong | R3 removable inner panel, 1016 × 2290 (resized per D-60, HOLD H07) | 1 sheet 1500 × 3000 | As P01 | calculation (fit); source (sheet size) | HW-SEL A1; LS F-DR | |
| P21 | Heater for T05, adjustable, with a power reading · bộ gia nhiệt | R4 | 1, at least 320 W | Test equipment | calculation (314 W lifts 65 l/s by 4 K: 1.2 × 1005 × 0.065 × 4; air density and heat capacity as REQ C4) | T05; D-50; D-52 | |
| P22 | Bench 12 V supply and a PWM speed source for the fans · nguồn 12 V | S5 tests | 1 | Test equipment, set to the fan maker's PWM input | — | HW-SEL F3 (the sensor hub's PWM output is HOLD for the electrical scope) | |

## Door unit S4 (HOLD)

| ID | Part · Vietnamese | For | Qty | Maker · product | Status | Source | HOLD |
|---|---|---|---|---|---|---|---|
| P23 | Door unit parts · cửa kính và phụ kiện | S4 | 1 set | Glass: 4+4 grey laminate of toughened, heat-soaked panes, 8.76 mm, product not named. Hinges and lock: none rated for this door (dormakaba OFFICE 11.233 is listed for toughened 8/10 mm only). Drop seal: athmer Schall-Ex GSA 1-1112 black, cut from 1208 to 1176. Frame stop seal: athmer PS 1515 P Flex. Glass-to-glass seal: Bohle BO5281018, listed for 8–10 mm toughened glass (its fit on the 8.76 laminate is unverified). Pull: one of the HW-SEL C2 options, hole sizes on laminate not confirmed. Kick strip: aluminium, 85 mm tall, in the base band's dark finish. | source (seal products and ratings, HW-SEL C3, C4); confirmed (85 mm, D-57; glass build, D-46); unverified (180° seal on laminate) | HW-SEL C1 to C4; D-46; D-56; D-57 | H01, H02 |

## Rigs

| ID | Part · Vietnamese | For | Qty | Maker · product | Status | Source | HOLD |
|---|---|---|---|---|---|---|---|
| P24 | Base band piece, aluminium 100 × 40 × 2.0 · viền chân nhôm | R1 | 1.66 m (the side band piece's length) | Stock tube | calculation (LS B-BAND-SIDE 1660 = 1700 − 40); assumption (2.0 mm wall, LS t_al_base) | LS | H17 |
