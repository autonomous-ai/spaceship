# ELECTRICAL P01: calculation results

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-03 | P01 | DRAFT, written by `electrical_docs.py` | 2026-10-31 | ELECTRICAL Engineer |

Every number here is a **calculation** from the load table (`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`), the harness list and the route model, unless marked. Inputs carry their own status in those files.

## 1. Supply loading (24 V and 12 V, D-168)

| Supply | Output | Rated W | Load max W | Load typical W | Max load / rating | Feeds |
|---|---|---:|---:|---:|---:|---|
| PS1 | 24 V DC | 96 | 60.0 | 0.0 | 62 % | voice kit feed: one 24 V Class 2 feed, fused 5 A (REQ-VCK-04, D-168) |
| PS2 | 24 V DC | 60 | 40.5 | 22.0 | 68 % | all lights: uplight, down-light and call light, through the light controller |
| PS3 | 12 V DC | 60 | 31.4 | 11.9 | 52 % | four fans and the sensor hub (column fuse block) |
| **All** | | **216** | **131.9** | **33.9** | 61 % | REQ-ELE-03: about 125 W load |

The voice kit takes one 24 V Class 2 feed (D-168): its 60 W peak is 62.5 % of PS1's 96 W, under the 76.8 W cap (80 %), and one source means no two Class 2 sources can share a 0 V.

Typical = one or two people, lights full, fans near the 53 l/s normal flow, no voice kit fitted. Max = every load at its maximum at once, which the control never asks for (the fans reach full speed only above the 65 l/s boost).

## 2. Mains side (US 120 V 60 Hz, D-133)

- Supplies' input at maximum load: 154 W, each at its sheet's efficiency (LPV-60-12 83 %, LPV-60-24 86 %, CLG-100-24 88.5 %, at 230 V and full load) plus 0.5 W no-load each (assumption): about **1.29 A at 120 V** (the LPV-60s have no PFC, so their current is somewhat higher than this; the breaker sizing below has wide margin).
- Inrush (the breaker's C curve): the two LPV-60s draw 60 A for 525 us and the CLG-100 40 A for 1030 us, cold, at 230 V (their sheets), about half at 120 V. Mean Well allows 6 LPV-60 or 5 CLG-100 on one 16 A C-curve breaker at 230 V, so the three supplies switch on together within the 15 A C-curve breaker's instant trip (calculation).
- The breaker is 15 A, 1 pole, UL 489: 15 A x 120 V = 1.80 kW for the user outlets and the supplies together, 1.44 kW continuous at 80 % (NEC 210.19, 210.20). A laptop charger takes about 0.6 A; a 1.5 kW heater, the largest plug-in appliance on a 15 A US circuit, takes 12.5 A and still holds with the supplies (assumption).
- Mains conductors 14 AWG (UL 1015, 105 °C, in the sleeve and inside the unit): rated for 15 A and protected by the 15 A breaker (NEC 240.4(D)); the equipment ground is 14 AWG green too (NEC 250.122).
- The prototype is tested in Vietnam through a 220-to-110 V step-down transformer, part of the test set, not the pod (D-133); it must carry the outlets' load too (2 kVA or more, assumption).

## 3. Voltage drop on the 24 V and 12 V circuits (copper at 60 °C, 0.0206 Ω mm²/m)

Loop resistance = 2 x length x ρ / area, divided by the number of parallel pairs. Each segment carries its own maximum current (the loads beyond it at full power). Limit used: 3 % of the circuit's voltage (24 V for the lights and the kit, 12 V for the air) from the supply to the farthest load (assumption; the fans start at 7 V and run to 13.2 V).

| Segment | Circuit | Length mm | Area mm² x pairs | Max A | Drop V |
|---|---|---:|---:|---:|---:|
| W10a PU | PS2 lights | 170 | 0.823 x 1 | 0.92 | 0.008 |
| W10b B2-CASS | PS2 lights | 400 | 0.823 x 1 | 0.92 | 0.018 |
| W10c B4-CASS | PS2 lights | 1360 | 0.823 x 1 | 0.92 | 0.062 |
| W11a SHELF | PS2 lights | 300 | 0.823 x 1 | 0.92 | 0.014 |
| W11b SHELF | PS2 lights | 1610 | 0.823 x 1 | 0.26 | 0.021 |
| W11c SHELF | PS2 lights | 1220 | 0.823 x 1 | 0.85 | 0.052 |
| W20a PU | PS3 air | 170 | 0.823 x 2 | 2.62 | 0.011 |
| W20b B2-CASS | PS3 air | 1050 | 0.823 x 2 | 2.62 | 0.069 |
| W20c R1-CASS | PS3 air | 1060 | 0.823 x 2 | 2.62 | 0.069 |
| W30a PU | PS1 kit | 170 | 0.823 x 2 | 2.5 | 0.011 |
| W30b B2-CASS | PS1 kit | 1050 | 1.31 x 2 | 2.5 | 0.041 |
| W30c R1-CASS | PS1 kit | 1050 | 1.31 x 2 | 2.5 | 0.041 |
| W24a PU | hub I/O | 170 | 0.823 x 1 | 0.01 | 0 |
| W24b B2-CASS | hub I/O | 1050 | 0.205 x 1 | 0.01 | 0.002 |
| W24c R1-CASS | hub I/O | 1060 | 0.205 x 1 | 0.01 | 0.002 |
| W20d COLUMN | PS3 air | 380 | 0.823 x 2 | 2.62 | 0.025 |
| W24d COLUMN | hub I/O | 380 | 0.205 x 1 | 0.01 | 0.001 |
| W40 COLUMN | PS3 fan S | 1910 | 0.519 x 1 | 1.1 | 0.167 |
| W41 COLUMN | PS3 fan E | 1550 | 0.519 x 1 | 1.1 | 0.135 |
| W43 COLUMN | PS3 hub | 300 | 0.823 x 1 | 0.42 | 0.006 |
| W12 R2-CASS | PS2 lights | 1250 | 0.823 x 1 | 0.11 | 0.007 |

| Path, supply to the farthest load | Drop V | Drop % | 3 % limit |
|---|---:|---:|---|
| PS1 to the voice kit outlet (W30a + W30b + W30c) | 0.09 | 0.4 | within |
| PS2 to the left wall uplight (W10a + W10b + W10c + W11a + W11b) | 0.12 | 0.5 | within |
| PS2 to the call light (W10a + W10b + W10c + W11a + W11c + W12) | 0.16 | 0.7 | within |
| PS3 to the supply fans (W20a + W20b + W20c + W20d + W40) | 0.34 | 2.8 | within |
| PS3 to the exhaust fans (W20a + W20b + W20c + W20d + W41) | 0.31 | 2.6 | within |
| PS3 to the sensor hub (W20a + W20b + W20c + W20d + W43) | 0.18 | 1.5 | within |

Mains conductors are left out: 0.92 m of 14 AWG (2.08 mm², 8.28 Ω/km at 20 °C) at the breaker's full 15 A drops about 0.23 V of 120 V (0.2 %).

## 4. Heat the electrical parts add inside the pod

The supplies sit inside the pod (in the power unit), so their losses heat the pod air; the lights' and the hub's power is heat inside too, and so is the supply fans' power (it ends up in the supply air). The exhaust fans' power leaves with the exhaust.

| Heat source, typical | W |
|---|---:|
| Lights (already in C4's 30 W) | 22.0 |
| Supply losses, 3 units | 7.5 |
| Sensor hub | 3.0 |
| Supply fan pair at 53 l/s | 5.2 |
| **Not yet in C4's 240 W** (losses + hub + supply fans) | **15.7** |

At the 53 l/s normal flow that adds **0.25 K** to C4's 3.8 K (ΔT = P / (1.2 × 1005 × 0.053), calculation). The lights are 22.0 W in the work scene: the down-light at full and the uplight on the rest of the 22 W the hub holds them to (PM ruling 2026-11-01), inside C4's 30 W for lights. With the voice kit at its 40 W average (D-88), the kit adds 40 W and its supply's loss about 5.2 W more (calculation). For the Air Engineer's 4 K check (D-50).

## 5. Mass

| Group | kg | Status |
|---|---:|---|
| 710001 power unit (with its mains wiring and fixings) | 3.84 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 710041 hub and controls zone | 0.36 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 719001 cord set kit (ships loose; counts in the pod as shipped) | 0.59 | calculation (parts list: quantity x mass each, each mass with its own status) |
| lights: shelf strip, call strip and profile | 0.30 | calculation (parts list: quantity x mass each, each mass with its own status) |
| harness parts: cables, plugs, terminals, RJ45 parts, bushings, edge strip, clips, senses | 1.27 | calculation (parts list: quantity x mass each, each mass with its own status) |
| **710000 ELECTRICAL** | **6.35** | calculation; the layout study's roll-up carries 3.05 kg for switches, lights and harness (assumption) |

**B2 with the power unit inside (D-03, at most 20 kg):** B2's outer panel about 9.1 kg (calculation from CEILING's measured frame and skin masses per m², PR #32, scaled to B2's 1.343 m², plus 40 mm fill at 25 kg/m³, D-81) + the power unit 3.84 kg = **12.9 kg**, under 20 kg. WALL's own B2 mass replaces the first figure when B2 is modelled.

## 6. Heat inside the power unit (711001)

The supplies, the breaker, the GFCI receptacle and the light controller share the closed box; its air sets each part's temperature. A steady heat balance (`unit_heat.py`): the supplies sit flat on the shell's back wall; heat leaves through the front plate to the pod, through the vent slots by stack flow, and through the shell into B2's skin and members to the room. The last path carries most of it and is the least certain, so the worst case takes it at half (assumption). Case: room 32 °C (D-173: the room the pod is designed for), the pod 4 K over it (D-50); the voice kit at its 40 W average (D-88), the lights at the hub's 22 W (PM ruling), the fans at the 65 l/s boost with the hub, 19.2 W (calculation).

| Supply | Model | Load W | Efficiency at 115 V | Loss W | Basis |
|---|---|---:|---:|---:|---|
| PS1 | CLG-100-24 | 40.0 | 84.2 % | 7.5 | source: Mean Well CLG-100 sheet, its 115 V curve (48 V model; the 24 V has the same 88.5 %) |
| PS2 | LPV-60-24 | 22.0 | 80.2 % | 5.4 | assumption: LPV-60-24's 86 % (sheet, 230 V) less one point at 115 V, on the CLG-100's curve shape |
| PS3 | LPV-60-12 | 19.2 | 76.7 % | 5.8 | assumption: LPV-60-12's 83 % (sheet, 230 V) less one point at 115 V, on the CLG-100's curve shape |

Other heat in the box: the light controller 2.0 W (assumption), the breaker 2.0 W per pole at 15 A (Eaton), the GFCI receptacle about 1.5 W at 12 A (assumption), the receptacle's mains wiring and the fuses (calculation); with the user outlets at 3 A (laptops, a monitor, chargers: assumption) that is 2.3 W, at their 12 A continuous limit 6.0 W.

| Inside air, °C | the plate before (2 rows of 5 slots) | this plate (8 rows of 3 slots, right side) |
|---|---:|---:|
| outlets at 3 A, shell path as estimated | 56.6 | 50.1 |
| outlets at 3 A, shell path at half | 63.0 | 53.4 |
| **worst:** outlets at 12 A, shell path at half | 68.8 | 56.8 |

**Worst case, each part against its own limit:** the box's air at 56.8 °C, 3 K more for the upper part (no fan inside, assumption): **59.8 °C**.

| Part | Its limit | Margin at 60 °C |
|---|---|---:|
| light controller LTECH LT-995 | 65 °C (LTECH LT-995 sheet: -30 to +65 °C) | 5 K |
| GFCI receptacle P&S 1597TRW | 66 °C (Legrand CS3339: -35 to +66 °C) | 6 K |
| Mean Well supplies, the units themselves | 70 °C (LPV-60 and CLG-100 sheets: -30 to +70 °C, by their derating curves) | 10 K |
| LAN keystone jacks Panduit NK688MWH | 75 °C (Panduit COSP588: -10 to +75 °C) | 15 K |
| Cat6 cable Belden 3612 | 75 °C (Belden 3612 sheet: 75 °C) | 15 K |
| 12 and 24 V and signal leads in the unit: Alpha Wire 3075 single cores (UL 1015) | 105 °C (UL AWM 1015: 105 °C (D-173); they may lie on the supplies' cases, see below) | 45 K |
| lever connectors WAGO 221-415 | 85 °C (WAGO: T85, surrounding air 85 °C at most) | 25 K |
| fuse holders Littelfuse FHAC0001ZXJ | 105 °C (Littelfuse OL-FHAC0001ZXJ: 105 °C) | 45 K |
| bushings Heyco 2836N | 105 °C (Heyco: -18 to +105 °C) | 45 K |
| mains wire Alpha Wire 461419 (UL 1015) | 105 °C (Alpha Wire: UL 1015 AWM 105 °C) | 45 K |
| PS1 CLG-100-24 at its peak load, 60.0 W | 77 W at 60 °C (80 % of 96 W, its maker's derating) | 17 W |
| PS2 LPV-60-24 at its peak load, 40.5 W | 46 W at 60 °C (76 % of 60 W, its maker's derating) | 5 W |
| PS3 LPV-60-12 at its peak load, 31.4 W | 46 W at 60 °C (76 % of 60 W, its maker's derating) | 14 W |

The supplies' cases reach 72.7 °C; a lead lying on one is a 105 °C single core (D-173), 32 K under its rating. No part falls under 3 K.

Room temperature (the case above takes 32 °C, the room the pod is designed for, D-173): with the same worst loads, each room gives these upper-air temperatures and the tightest part's margin:

| Room | Upper air | Tightest part | Its margin |
|---:|---:|---|---:|
| 28 °C | 55.9 °C | light controller LTECH LT-995 (65 °C) | 9 K |
| 30 °C | 57.9 °C | light controller LTECH LT-995 (65 °C) | 7 K |
| 32 °C | 59.8 °C | light controller LTECH LT-995 (65 °C) | 5 K |

The breaker is calibrated at 40 °C and carries 0.5 % less per K above (Eaton): 13.5 A at 60 °C, over the outlets' 12 A continuous limit. These figures are a calculation; the prototype's test measures the box's air with the kit at 40 W (a dummy load) and the outlets loaded.

