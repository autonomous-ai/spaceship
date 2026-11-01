# ELECTRICAL P01: calculation results

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-03 | P01 | DRAFT, written by `electrical_docs.py` | 2026-10-31 | ELECTRICAL Engineer |

Every number here is a **calculation** from the load table (`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`), the harness list and the route model, unless marked. Inputs carry their own status in those files.

## 1. Supply loading (12 V)

| Supply | Rated W | Load max W | Load typical W | Max load / rating | Feeds |
|---|---:|---:|---:|---:|---|
| PS1 | 60 | 60.0 | 0.0 | 100 % | voice cockpit hook, fused 5 A (REQ-VCK-04) |
| PS2 | 60 | 41.0 | 22.0 | 68 % | all lights: uplight, down-light and call light, through the 3-channel light controller |
| PS3 | 60 | 31.4 | 11.9 | 52 % | four fans and the sensor hub (column fuse block) |
| **All** | **180** | **132.4** | **33.9** | 74 % | REQ-ELE-03: about 125 W load, supply at least 150 W |

Typical = one or two people, lights full, fans near the 53 l/s normal flow, no voice kit fitted. Max = every load at its maximum at once, which the control never asks for (the fans reach full speed only above the 65 l/s boost).

## 2. Mains side (US 120 V 60 Hz, D-133)

- Supplies' input at maximum load: 161 W at 83 % efficiency (assumption from the maker's typical figure, parts list) plus 0.5 W no-load each: about **1.34 A at 120 V**.
- The breaker is 15 A, 1 pole, UL 489: 15 A x 120 V = 1.80 kW for the user outlets and the supplies together, 1.44 kW continuous at 80 % (NEC 210.19, 210.20). A laptop charger takes about 0.6 A; a 1.5 kW heater, the largest plug-in appliance on a 15 A US circuit, takes 12.5 A and still holds with the supplies (assumption).
- Mains conductors 14 AWG (UL 1015, 105 °C, in the sleeve and inside the unit): rated for 15 A and protected by the 15 A breaker (NEC 240.4(D)); the equipment ground is 14 AWG green too (NEC 250.122).
- The prototype is tested in Vietnam through a 220-to-110 V step-down transformer, part of the test set, not the pod (D-133); it must carry the outlets' load too (2 kVA or more, assumption).

## 3. Voltage drop on the 12 V circuits (copper at 60 °C, 0.0206 Ω mm²/m)

Loop resistance = 2 x length x ρ / area, divided by the number of parallel pairs. Each segment carries its own maximum current (the loads beyond it at full power). Limit used: 3 % of 12 V from the supply to the farthest load (assumption; the fans start at 7 V and run to 13.2 V, and the strips are specified at 12 V).

| Segment | Circuit | Length mm | Area mm² x pairs | Max A | Drop V |
|---|---|---:|---:|---:|---:|
| W10a PU | PS2 lights | 300 | 0.823 x 1 | 1.83 | 0.028 |
| W10b B2-CASS | PS2 lights | 270 | 0.823 x 1 | 1.83 | 0.025 |
| W10c B4-CASS | PS2 lights | 1360 | 0.823 x 1 | 1.83 | 0.125 |
| W11a SHELF | PS2 lights | 300 | 0.823 x 1 | 1.83 | 0.028 |
| W11b SHELF | PS2 lights | 1610 | 0.823 x 1 | 0.53 | 0.042 |
| W11c SHELF | PS2 lights | 1220 | 0.823 x 1 | 1.73 | 0.105 |
| W20a PU | PS3 air | 300 | 0.823 x 2 | 2.62 | 0.02 |
| W20b B2-CASS | PS3 air | 920 | 0.823 x 2 | 2.62 | 0.06 |
| W20c R1-CASS | PS3 air | 1260 | 0.823 x 2 | 2.62 | 0.083 |
| W30a PU | PS1 kit | 300 | 0.823 x 2 | 5 | 0.038 |
| W30b B2-CASS | PS1 kit | 920 | 0.823 x 2 | 5 | 0.115 |
| W30c R1-CASS | PS1 kit | 1050 | 0.823 x 2 | 5 | 0.131 |
| W24a PU | hub I/O | 300 | 0.205 x 1 | 0.01 | 0.001 |
| W24b B2-CASS | hub I/O | 920 | 0.205 x 1 | 0.01 | 0.002 |
| W24c R1-CASS | hub I/O | 1260 | 0.205 x 1 | 0.01 | 0.003 |
| W20d COLUMN | PS3 air | 420 | 0.823 x 2 | 2.62 | 0.028 |
| W24d COLUMN | hub I/O | 420 | 0.205 x 1 | 0.01 | 0.001 |
| W40 COLUMN | PS3 fan S | 1550 | 0.519 x 1 | 1.1 | 0.135 |
| W41 COLUMN | PS3 fan E | 1260 | 0.519 x 1 | 1.1 | 0.11 |
| W43 COLUMN | PS3 hub | 300 | 0.823 x 1 | 0.42 | 0.006 |
| W12 R2-CASS | PS2 lights | 1250 | 0.823 x 1 | 0.23 | 0.014 |

| Path, supply to the farthest load | Drop V | Drop % | 3 % limit |
|---|---:|---:|---|
| PS1 to the voice kit outlet (W30a + W30b + W30c) | 0.28 | 2.4 | within |
| PS2 to the left wall uplight (W10a + W10b + W10c + W11a + W11b) | 0.25 | 2.1 | within |
| PS2 to the call light (W10a + W10b + W10c + W11a + W11c + W12) | 0.33 | 2.7 | within |
| PS3 to the supply fans (W20a + W20b + W20c + W20d + W40) | 0.33 | 2.7 | within |
| PS3 to the exhaust fans (W20a + W20b + W20c + W20d + W41) | 0.30 | 2.5 | within |
| PS3 to the sensor hub (W20a + W20b + W20c + W20d + W43) | 0.20 | 1.6 | within |

Mains conductors are left out: 0.92 m of 14 AWG (2.08 mm², 8.28 Ω/km at 20 °C) at the breaker's full 15 A drops about 0.23 V of 120 V (0.2 %).

## 4. Heat the electrical parts add inside the pod

The supplies sit inside the pod (in the power unit), so their losses heat the pod air; the lights' and the hub's power is heat inside too, and so is the supply fans' power (it ends up in the supply air). The exhaust fans' power leaves with the exhaust.

| Heat source, typical | W |
|---|---:|
| Lights (already in C4's 30 W) | 22.0 |
| Supply losses, 3 units | 8.4 |
| Sensor hub | 3.0 |
| Supply fan pair at 53 l/s | 5.2 |
| **Not yet in C4's 240 W** (losses + hub + supply fans) | **16.6** |

At the 53 l/s normal flow that adds **0.26 K** to C4's 3.8 K (ΔT = P / (1.2 × 1005 × 0.053), calculation). The lights are 22.0 W in the work scene: the down-light at full and the uplight on the rest of the 22 W the hub holds them to (PM ruling 2026-11-01), inside C4's 30 W for lights. With the voice kit at its 40 W average (D-88), the kit adds 40 W and its supply's loss about 8.2 W more (calculation). For the Air Engineer's 4 K check (D-50).

## 5. Mass

| Group | kg | Status |
|---|---:|---|
| 710001 power unit (with its mains wiring and fixings) | 2.84 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 710041 hub and controls zone | 0.36 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 719001 cord set kit (ships loose; counts in the pod as shipped) | 0.53 | calculation (parts list: quantity x mass each, each mass with its own status) |
| lights: shelf strip, call strip and profile | 0.30 | calculation (parts list: quantity x mass each, each mass with its own status) |
| harness parts: cables, plugs, terminals, RJ45 parts, bushings, edge strip, clips, senses | 1.23 | calculation (parts list: quantity x mass each, each mass with its own status) |
| **710000 ELECTRICAL** | **5.25** | calculation; the layout study's roll-up carries 3.05 kg for switches, lights and harness (assumption) |

**B2 with the power unit inside (D-03, at most 20 kg):** B2's outer panel about 9.1 kg (calculation from CEILING's measured frame and skin masses per m², PR #32, scaled to B2's 1.343 m², plus 40 mm fill at 25 kg/m³, D-81) + the power unit 2.84 kg = **11.9 kg**, under 20 kg. WALL's own B2 mass replaces the first figure when B2 is modelled.

