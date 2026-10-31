# Compliance note: UL 962 and NEC Class 2 (ELECTRICAL P01)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-02 | P01 | DRAFT | 2026-10-31 | ELECTRICAL Engineer |

The v2 prototype is built and powered in Vietnam on 220 V. US rules come later (D-14, REQ-SCP-02), but they aren't designed out (REQ-US-05). This note says what the US rules will likely ask of the electrical design and how P01 keeps every one of them a change on the mains side only. It is a design note, not a compliance claim. Nothing here is certified or tested, and the standards' clause text still has to be read in full in the US rules phase (ISS-083).

## Result

1. **Every low-voltage circuit is Class 2.** Each of the three 12 V supplies is a 60 W unit, which is the most a Class 2 source may deliver at 12 V. So every cable inside the walls, ceiling and air column carries a power-limited circuit, safe for two non-electricians to plug together.
2. **Mains stays in one place.** The only mains parts are in the earthed power unit in panel B2: the inlet, the RCBO, the user socket and the three supplies' inputs. They're wired and tested in the factory, so no mains connection is made on site.
3. **The US version changes the mains side only:** the cord set, the inlet side of the power unit, the socket (a UL 962A furniture power unit in place of the VN socket) and the protective device. The three supplies take 100 to 240 V, so they stay, and so do the harnesses, connectors, routes, lights, fans and hub.
4. **Open for the US rules phase (HOLD, ISS-083):** read the current UL 962 and UL 962A editions and list their clauses for the pod; confirm every 12 V supply carries a Class 2 marking under UL 1310 or UL 62368-1, or a listed Class 2 LED driver marking under UL 8750; pick a US cord set and the furniture power unit.

## 1. NEC Class 2 at 12 V

NEC Chapter 9, Table 11(B), for an inherently limited DC Class 2 source of 0 to 20 V: maximum nameplate rating **5.0 × Vmax VA** and **5.0 A**. At 12 V that is **60 VA**. Status: source, read from public summaries of NEC Table 11(B) on 2026-10-31; the NFPA 70 text itself is to be checked in the US rules phase.

| Circuit | Supply | Rated | Load, max (load table) | Class 2 at 12 V? |
|---|---|---:|---:|---|
| Voice cockpit hook, 12 V 5 A (D-11) | PS1, 60 W | 5.0 A | 60 W | yes: 60 VA, 5.0 A, exactly the limit |
| Light shelf | PS2, 60 W dimmable | 5.0 A | 24 W | yes |
| Fans, hub, call light | PS3, 60 W | 5.0 A | about 37.5 W | yes |

Why three supplies and not one 150 W unit (DECIDED, PM ruling 2026-10-31 in the ELECTRICAL group): a single 150 W, 12.5 A supply can't be Class 2 at 12 V. Its 12 V wiring would need Chapter 3 wiring methods in the US: power cable, protected routing and listed fittings, not plug-in cables in a felt-lined cassette. Three Class 2 units, 180 W in all for about 125 W of load (REQ-ELE-03), keep every 12 V cable Class 2 in both markets.

What Class 2 lets the design do (NEC Article 725 in the 2020 edition, Article 722/724 in 2023; to check in the US rules phase):
- Class 2 cable (CL2, or a listed equivalent) in the cassettes and the column, with plug-in connectors and no conduit;
- Class 2 conductors kept apart from mains conductors. In P01 they never share a box or a cable path: mains stays inside the power unit's mains section, and its 12 V outputs leave on the other side.

## 2. UL 962 and UL 962A

- **UL 962, Household and Commercial Furnishings.** The go-to-market research flagged that UL 962 now covers booths and pods with electrical parts (REQ-US-05, ISS-083). Edition and scope are unverified until the standard's text is read (HOLD ISS-083).
- **UL 962A, Furniture Power Distribution Units.** A receptacle unit built into furniture is a furniture power distribution unit. The US power unit uses a UL 962A listed unit for the user outlets, with its own protection, in place of the VN socket.
- **What P01 already does that a furnishing listing will look for** (a design checklist, not a claim):
  - only listed or recognised electrical parts, each with its maker and exact SKU in the parts list (HOLD until the US equivalents are named);
  - a strain-relieved, locking inlet (powerCON TRUE1 TOP, rated 16 A at 250 V), so the cord can't be pulled out under load;
  - all mains wiring inside one earthed metal enclosure, factory made, with the frame it is fixed to bonded to earth;
  - no mains wiring in the walls, ceiling or air column (D-10);
  - every cable through a sheet-metal hole runs in a grommet; cables clip to the cassettes only (D-26);
  - power-limited 12 V circuits, so a pinched or damaged cable in a wall can't start a fire from mains energy.

## 3. Earthing and bonding

- The power unit is an aluminium enclosure with a protective earth stud. The inlet's earth, the socket's earth and the enclosure stud meet on one earth terminal block.
- **B2's aluminium frame is bonded** to that terminal by a 2.5 mm² green-yellow lead with ring lugs under one of the unit's mounting bolts, with a serrated washer. B2 is the only panel a mains part can touch: the inlet is fixed through its skin and the unit to its frame.
- No other panel carries a mains part, so no other frame needs bonding. The 12 V side is SELV from double-insulated (Class II) supplies and needs no earth.
- US version: the same bond, with the conductor size checked against UL 962 and the NEC.

## 4. 220 V prototype (Vietnam) and 120 V later

| Item | 220 V prototype (P01) | US version (later) |
|---|---|---|
| Cord set | 3 m, H05VV-F 3G1.5, plug for VN office sockets (HOLD: plug type checked with the factory's sockets), powerCON TRUE1 cord connector | NEMA 5-15P, SJT 3 × 14 AWG, same cord connector (UL listed) |
| Inlet | Neutrik powerCON TRUE1 TOP, 16 A 250 V | same, UL listed (to confirm in the US phase) |
| Protection | RCBO 1P+N, C10, 30 mA, in the power unit | per the UL 962A unit (GFCI and overcurrent inside it) |
| User outlet | UTEN S300 universal socket (plan VT07), 86 × 86 | UL 962A furniture power unit, NEMA 5-15R |
| 12 V supplies | 3 × Mean Well 60 W, 100–240 V input | the same three units |
| Harnesses, connectors, routes, lights, fans, hub | — | unchanged |

## 5. Not covered here

Fire ratings of the materials, sprinklers (ISS-082), the threshold rule (ISS-084) and EMC are outside this note. For the prototype the applicable rules are Vietnamese, with the factory's electrician checking the power unit before first power-up (test plan in `README.md` §11).
