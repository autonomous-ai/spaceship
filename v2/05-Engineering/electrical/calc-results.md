# ELECTRICAL P01: calculation results

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-03 | P01 | DRAFT, written by `electrical_docs.py` | 2026-10-31 | ELECTRICAL Engineer |

Every number here is a **calculation** from the load table (`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`), the harness list and the route model, unless marked. Inputs carry their own status in those files.

## 1. Supply loading (12 V)

| Supply | Rated W | Load max W | Load typical W | Max load / rating | Feeds |
|---|---:|---:|---:|---:|---|
| PS1 | 60 | 60.0 | 0.0 | 100 % | voice cockpit hook, fused 5 A (REQ-VCK-04) |
| PS2 | 60 | 26.6 | 26.6 | 44 % | light shelf (the hub sets its 0-10 V dimming) |
| PS3 | 60 | 34.1 | 14.6 | 57 % | four fans, the sensor hub and the call light (column fuse block) |
| **All** | **180** | **120.8** | **41.2** | 67 % | REQ-ELE-03: about 125 W load, supply at least 150 W |

Typical = one or two people, lights full, fans near the 53 l/s normal flow, no voice kit fitted. Max = every load at its maximum at once, which the control never asks for (the fans reach full speed only above the 65 l/s boost).

## 2. Mains side

- Supplies' input at maximum load: 147 W at 83 % efficiency (assumption from the maker's typical figure, parts list) plus 0.5 W no-load each: about **0.67 A at 220 V**.
- The RCBO is C10, 30 mA: 10 A x 220 V = 2.2 kW for the user socket and the supplies together. A laptop charger takes about 0.3 A; a 2 kW heater would still hold (9.1 A), which is the worst case a user might plug in (assumption).
- Mains conductors 1.5 mm² (H07V-K in the sleeve, 0.82 m): rated well above 10 A in free air (IEC 60364-5-52, to confirm by the factory's electrician); the RCBO protects them.

## 3. Voltage drop on the 12 V circuits (copper at 60 °C, 0.0206 Ω mm²/m)

Loop resistance = 2 x length x ρ / area, divided by the number of parallel pairs. Each segment carries its own maximum current (the loads beyond it at full power). Limit used: 3 % of 12 V from the supply to the farthest load (assumption; the fans start at 7 V and run to 13.2 V, and the strips are specified at 12 V).

| Segment | Circuit | Length mm | Area mm² x pairs | Max A | Drop V |
|---|---|---:|---:|---:|---:|
| W10a PU | PS2 lights | 300 | 0.823 x 1 | 2.22 | 0.033 |
| W10b B2-CASS | PS2 lights | 270 | 0.823 x 1 | 2.22 | 0.03 |
| W10c B4-CASS | PS2 lights | 1360 | 0.823 x 1 | 2.22 | 0.151 |
| W11a SHELF | PS2 lights | 300 | 0.823 x 1 | 2.22 | 0.033 |
| W11b SHELF | PS2 lights | 1620 | 0.823 x 1 | 0.53 | 0.043 |
| W11c SHELF | PS2 lights | 910 | 0.823 x 1 | 0.53 | 0.024 |
| W20a PU | PS3 air | 300 | 0.823 x 2 | 2.84 | 0.021 |
| W20b B2-CASS | PS3 air | 910 | 0.823 x 2 | 2.84 | 0.065 |
| W20c R1-CASS | PS3 air | 1260 | 0.823 x 2 | 2.84 | 0.09 |
| W30a PU | PS1 kit | 300 | 0.823 x 2 | 5 | 0.038 |
| W30b B2-CASS | PS1 kit | 910 | 0.823 x 2 | 5 | 0.114 |
| W30c R1-CASS | PS1 kit | 1050 | 0.823 x 2 | 5 | 0.131 |
| W24a PU | hub I/O | 300 | 0.205 x 1 | 0.01 | 0.001 |
| W24b B2-CASS | hub I/O | 910 | 0.205 x 1 | 0.01 | 0.002 |
| W24c R1-CASS | hub I/O | 1260 | 0.205 x 1 | 0.01 | 0.003 |
| W20d COLUMN | PS3 air | 420 | 0.823 x 2 | 2.84 | 0.03 |
| W24d COLUMN | hub I/O | 420 | 0.205 x 1 | 0.01 | 0.001 |
| W40 COLUMN | PS3 fan S | 1580 | 0.519 x 1 | 1.1 | 0.138 |
| W41 COLUMN | PS3 fan E | 1260 | 0.519 x 1 | 1.1 | 0.11 |
| W43 COLUMN | PS3 hub | 300 | 0.326 x 1 | 0.42 | 0.016 |
| W12a COLUMN | PS3 call | 550 | 0.519 x 1 | 0.5 | 0.022 |
| W12b R2-CASS | PS3 call | 570 | 0.519 x 1 | 0.5 | 0.023 |

| Path, supply to the farthest load | Drop V | Drop % | 3 % limit |
|---|---:|---:|---|
| PS1 to the voice kit outlet (W30a + W30b + W30c) | 0.28 | 2.4 | within |
| PS2 to the left wall strip (the longest light path) (W10a + W10b + W10c + W11a + W11b) | 0.29 | 2.4 | within |
| PS3 to the supply fans (W20a + W20b + W20c + W20d + W40) | 0.34 | 2.9 | within |
| PS3 to the exhaust fans (W20a + W20b + W20c + W20d + W41) | 0.32 | 2.6 | within |
| PS3 to the sensor hub (W20a + W20b + W20c + W20d + W43) | 0.22 | 1.8 | within |
| PS3 to the call light (W20a + W20b + W20c + W20d + W12a + W12b) | 0.25 | 2.1 | within |

Mains conductors are left out: 0.92 m of 1.5 mm² at the RCBO's full 10 A drops about 0.25 V of 220 V (0.1 %).

## 4. Heat the electrical parts add inside the pod

The supplies sit inside the pod (in the power unit), so their losses heat the pod air; the lights' and the hub's power is heat inside too, and so is the supply fans' power (it ends up in the supply air). The exhaust fans' power leaves with the exhaust.

| Heat source, typical | W |
|---|---:|
| Lights (already in C4's 30 W) | 29.3 |
| Supply losses, 3 units | 9.9 |
| Sensor hub | 3.0 |
| Supply fan pair at 53 l/s | 5.2 |
| **Not yet in C4's 240 W** (losses + hub + supply fans) | **18.1** |

At the 53 l/s normal flow that adds **0.28 K** to C4's 3.8 K (ΔT = P / (1.2 × 1005 × 0.053), calculation). With the voice kit at 60 W, its own supply's loss adds about 12.3 W more (calculation). For the Air Engineer's 4 K check (D-50).

## 5. Mass

| Group | kg | Status |
|---|---:|---|
| 710001 power unit (with its mains wiring and fixings) | 2.80 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 710041 hub and controls zone | 0.38 | calculation (parts list: quantity x mass each, each mass with its own status) |
| 710051 cord set (ships loose; counts in the pod as shipped) | 0.50 | calculation (parts list: quantity x mass each, each mass with its own status) |
| lights: shelf strip, call strip and profile | 0.26 | calculation (parts list: quantity x mass each, each mass with its own status) |
| harness parts: cables, plugs, terminals, RJ45 parts, bushings, edge strip, clips, senses | 1.00 | calculation (parts list: quantity x mass each, each mass with its own status) |
| **710000 ELECTRICAL** | **4.94** | calculation; the layout study's roll-up carries 3.05 kg for switches, lights and harness (assumption) |

**B2 with the power unit inside (D-03, at most 20 kg):** B2's outer panel about 9.1 kg (calculation from CEILING's measured frame and skin masses per m², PR #32, scaled to B2's 1.343 m², plus 40 mm fill at 25 kg/m³, D-81) + the power unit 2.80 kg = **11.9 kg**, under 20 kg. WALL's own B2 mass replaces the first figure when B2 is modelled.

