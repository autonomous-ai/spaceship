# Compliance note: UL 962 and NEC Class 2 (ELECTRICAL P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-02 | P01 | DRAFT | 2026-11-01 | ELECTRICAL Engineer |

The pod is sold in the US, so its mains side is US 120 V, 60 Hz, on the prototype too (D-133, PM ruling 2026-11-01, on the owner's question "why 220 V?"). The prototype is tested in Vietnam through a 220-to-110 V step-down transformer. This note says what the US rules will likely ask of the electrical design and how P01 meets it. It is a design note, not a compliance claim. Nothing here is certified or tested, and the standards' clause text still has to be read in full in the US rules phase (ISS-083).

## Result

1. **Every low-voltage circuit is Class 2.** Each supply's own sheet says "Class 2 power unit" (UL 1310): the kit's Mean Well CLG-100-24 (96 W at 24 V), the lights' LPV-60-24 and the air's LPV-60-12 (60 W each), each within the Class 2 limit at its voltage (D-168). So every cable inside the walls, ceiling and air column carries a power-limited circuit, safe for two non-electricians to plug together, and no two Class 2 sources share a 0 V.
2. **Mains stays in one place.** The only mains parts are in the earthed power unit in panel B2: the inlet, the breaker, the GFCI receptacle and the three supplies' inputs. They're wired and tested in the factory, so no mains connection is made on site.
3. **US 120 V by design, with UL-listed parts on the mains side (D-133):** the powerCON TRUE1 TOP inlet (UL 498), a 15 A one-pole UL 489 breaker, a tamper-resistant GFCI duplex NEMA 5-15R receptacle (UL 943 Class A, UL 498) as the user outlets, UL 1015 14 AWG wiring sized for 15 A, and a NEMA 5-15P SJOOW 14/3 cord set. The three supplies take 100 to 240 V and carry a UL Class 2 listing, so the 12 V side doesn't change: harnesses, connectors, routes, lights, fans and hub.
4. **Open for the US rules phase (HOLD, ISS-083):** read the current UL 962 and UL 962A editions and list their clauses for the pod; settle whether the power unit is evaluated to UL 962A on its own or within the pod's UL 962 evaluation; confirm each mains part's UL file (each is named from its own datasheet in the parts list, 2026-11-01; the breaker's own sheet is still to read, and its interrupting rating at 120 V with it) and each 12 V supply's Class 2 marking under UL 1310 or UL 62368-1, or a listed Class 2 LED driver marking under UL 8750.

## 1. NEC Class 2 at 24 V and 12 V

NEC Chapter 9, Table 11(B), for a DC Class 2 source: 0 to 20 V, maximum nameplate rating **5.0 × Vmax VA** and **5.0 A** (an 8.0 A current limit for an inherently limited source), so **60 VA** at 12 V; over 20 to 30 V, **100 VA**. Status: source, from a 2018 trade article that reprints the table (block.eu, read 2026-10-31); the NFPA 70 text itself is to be checked in the US rules phase.

| Circuit | Supply | Rated | Load, max (load table) | Class 2? |
|---|---|---:|---:|---|
| Voice cockpit hook, one 24 V feed (D-11, D-88, D-168) | PS1, CLG-100-24, 96 W | 4.0 A | 60 W peak (62.5 %) | yes: a Class 2 power unit, within 100 VA at 24 V |
| Lights: uplight, down-light, call light, through the light controller | PS2, LPV-60-24, 60 W | 2.5 A | 40.5 W at full; the hub holds them at about 22 W | yes |
| Fans and hub | PS3, LPV-60-12, 60 W | 5.0 A | 31.4 W | yes |

One feed for the kit, from one 24 V Class 2 source (D-168), replaces the two 12 V feeds of D-136: two Class 2 sources must never be joined, and a kit built later could have tied two feeds' 0 V together inside it. At 24 V the kit's 60 W peak runs its 96 W source at 62.5 %. Why separate supplies and not one large unit (DECIDED, PM ruling 2026-10-31 in the ELECTRICAL group): a single 150 W supply can't be Class 2 at 12 or 24 V. Its wiring would need Chapter 3 wiring methods in the US: power cable, protected routing and listed fittings, not plug-in cables in a felt-lined cassette. Three Class 2 units, 216 W in all for about 132 W of load at the hardware maximum (REQ-ELE-03), keep every low-voltage cable Class 2.

What Class 2 lets the design do (NEC Article 725 in the 2020 edition, Article 722/724 in 2023; to check in the US rules phase):
- Class 2 cable (CL2, or a listed equivalent) in the cassettes and the column, with plug-in connectors and no conduit;
- Class 2 conductors kept apart from mains conductors. In P01 they never share a box or a cable path: mains stays inside the power unit's mains section, and its 24 V and 12 V outputs leave on the other side.

## 2. UL 962 and UL 962A

- **UL 962, Household and Commercial Furnishings, Edition 5** (published 2022-10-21, last revised 2025-06-18; source: the ULSE standards shop page, read 2026-10-31). Its scope item 1.1(k) now names "enclosed rooms, also known as pods, booths, or rooms with ceilings (these are not considered furnishings)", up to 600 V AC. UL 2999 section 1.6 says pods are evaluated to UL 962. So a US Spaceship is evaluated to UL 962. Its clause text is still to read (HOLD, ISS-083).
- **UL 962A, Furniture Power Distribution Units, Edition 6** (published 2023-07-13, last revised 2025-11-18; same source). It covers indoor, cord-and-plug furniture power distribution units up to 250 V AC and 20 A, fixed to the furniture and not used as building wiring. The power unit is one: built from listed parts (inlet, breaker, GFCI receptacle, cord set, wire), it is evaluated to UL 962A on its own or within the pod's UL 962 evaluation (HOLD, ISS-083). If the evaluation asks for a listed unit, a UL 962A listed furniture power unit takes the GFCI receptacle's place on the same plate opening family (the fallback, D-133).
- **What P01 already does that a furnishing listing will look for** (a design checklist, not a claim):
  - only listed or recognised electrical parts, each with its maker and exact SKU in the parts list (US parts named, D-133; all HOLD, no order);
  - a strain-relieved, locking inlet (powerCON TRUE1 TOP, UL 498, 20 A in the US), so the cord can't be pulled out under load;
  - all mains wiring inside one earthed metal enclosure, factory made, with the frame it is fixed to bonded to earth;
  - tamper-resistant receptacles (NEC 406.12) with GFCI protection for people (UL 943 Class A, 4 to 6 mA) and a 15 A breaker for the wiring (NEC 240.4(D));
  - no mains wiring in the walls, ceiling or air column (D-10);
  - every cable through a sheet-metal hole runs in a grommet; cables clip to the cassettes only (D-26);
  - power-limited 24 V and 12 V circuits, so a pinched or damaged cable in a wall can't start a fire from mains energy.

## 3. Earthing and bonding

- The power unit is an aluminium enclosure with a protective earth stud. The inlet's ground, the receptacle's ground and the enclosure stud meet on one ground terminal block.
- **B2's aluminium frame is bonded** to that terminal by a 14 AWG green lead (the equipment ground for a 15 A circuit, NEC 250.122) with ring lugs under one of the unit's mounting bolts, with a serrated washer. B2 is the only panel a mains part can touch: the inlet is fixed through its skin and the unit to its frame.
- No other panel carries a mains part, so no other frame needs bonding. The low-voltage side is SELV: the LPV-60s are double insulated (Class II); the CLG-100's case is earthed through its FG lead to the unit's earth stud.

## 4. US 120 V parts (P01, D-133)

| Item | P01 (US 120 V 60 Hz) | Was (220 V, before D-133) |
|---|---|---|
| Cord set | 3 m: Leviton 5266-C NEMA 5-15P (UL 498, E13399), Carol 01360 SJOOW 14/3 (UL 62), Neutrik NAC3F-TRUE1-S cord connector (UL 498 20 A, E343813; Neutrik certifies it with SJOOW 14/3, not SJT); UL 817 as a set (HOLD) | H05VV-F 3G1.5, VN plug |
| Inlet | Neutrik NAC3MPX-TOP (powerCON TRUE1 TOP), UL 498 20 A 250 V, Recognized, E343813; three Panduit DNF14-250FIB-C disconnects (UL 310) on its 1/4 in tabs | the same part |
| Protection | breaker 1P 15 A, C curve, UL 489 (Eaton FAZ-C15/1-NA-L: its own sheet still to read, HOLD), on the DIN rail; GFCI Class A at the outlets | RCBO 1P+N, C10, 30 mA |
| User outlets | Pass & Seymour 1597TRW: tamper-resistant self-test GFCI duplex NEMA 5-15R, 15 A 125 V, cULus E42190, on the unit face behind a decorator opening | UTEN S300 universal socket, 86 × 86 |
| LAN outlet | two Panduit NK688MWH Cat6 keystone jacks (UL 1863) snapped into the front plate | UTEN S300 two-port LAN socket |
| Mains wiring | Alpha Wire 461419, UL 1015 14 AWG, 600 V, 105 °C (black, white, green); the bond 14 AWG green; Panduit PV14 insulated rings (cULus) | H07V-K 1.5 mm², bond 2.5 mm² |
| Low-voltage supplies | Mean Well CLG-100-24 (kit, 24 V) and LPV-60-24 (lights, 24 V), LPV-60-12 (air and hub, 12 V): Class 2 power units (UL 1310) on their own sheets (D-168) | three units |
| Harnesses, connectors, routes, lights, fans, hub | unchanged | — |

**Tests in Vietnam:** the cord set plugs into a 220-to-110 V step-down transformer (isolating, 2 kVA or more so it carries the outlets' load too; part of the test set, not the pod). The GFCI and the breaker then work as they will in the US.

## 5. Not covered here

Fire ratings of the materials, sprinklers (ISS-082), the threshold rule (ISS-084) and EMC are outside this note. The prototype is built to the US design; for its tests in Vietnam the factory's electrician checks the power unit and the step-down transformer before first power-up (test plan in `README.md` §11).
