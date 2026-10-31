# ELECTRICAL design: Spaceship (FocusPod v2), P01

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-01 | P01 | DRAFT | 2026-10-31 | ELECTRICAL Engineer |

The pod's electrical design: mains, the 12 V bus, the sensor hub, lights, fans, the voice cockpit hooks and the harness. It is built so that two people can put it together with no electrician. Every number carries a status (conventions §9). Choices the PM has ruled on are DECIDED; the rest are PROPOSED, and work goes ahead on them (AGENTS.md). Bought parts stay on HOLD: nothing was ordered and no supplier was contacted.

## Result

1. **Mains in one place, made in the factory (DECIDED, PM ruling 2026-10-31).** One earthed aluminium power unit sits in the lower back panel B2, its face flush with the felt at the ledge height (centre Z 1000). It holds the user socket and the LAN socket on its face, a 30 mA RCBO behind a window, and the three 12 V supplies. The inlet and the LAN feed-through use v1's back-wall spot. v1 had them at X 0, which is now the B1–B2 closing seam (D-65), so they move into B2 at X 120, at v1's heights (Z 313 and 375). On site, nothing mains is connected. Only B2's frame is bonded to earth.
2. **Three 60 W Class 2 supplies, 180 W in all (DECIDED).** The load is 120.8 W at its maximum and about 41 W typical (calc-results §1): PS1 (Mean Well LPV-60-12) for the voice kit hook (12 V 5 A), PS2 (Mean Well PWM-60-12, dims to off) for the light shelf, PS3 (LPV-60-12) for the four fans, the hub and the call light. 60 W is the Class 2 limit at 12 V, so every cable in the walls, ceiling and air column is power-limited. A later 120 V US version changes only the mains side ([compliance note](compliance-note.md)).
3. **Cables in the lining cassettes' 24 mm gap, clipped to the cassettes only (D-26, D-41), with a plug pair at every joint (DECIDED).** The trunk runs from the unit along B2's lining to the back-right corner, then along R1's lining at Z 1100, past the voice-kit drop, into a cable chase in the air column. The light feed runs up B2 and B4 to the light shelf. A draw-wire route runs through the ceiling cassette (D-41). Every hole in sheet steel has a grommet. 7 joints carry 13 plug pairs.
4. **The hub runs the air and the lights, and tests them (D-09, D-44, D-50, D-61, D-87).** The fans and the hub sit at the air column, with short cables. Two PWM signals drive the two balanced fan pairs, with tach back. The hub also sets the shelf's 0–10 V dimming and switches the call light. Its **self-test button (D-87)** checks the three 12 V rails, runs both fan pairs and reads their tach, cycles both lights and reads their current, reads the sensors, and shows PASS or the failing item. If a PWM line opens, the fans run at full speed, so a hub fault never stops the fresh air. Every harness segment is tested in the factory before it ships (D-87).
5. **CAD: 40 reserved spaces** (routes, pockets, grommets, the unit, the inlet, the hub zone) in `710000_P01_ELECTRICAL_CAD`, derived from skeleton P04. Its own clash check runs against the skeleton's real bodies. See `v2/01-CAD-Native/electrical/BUILD-RECORD.md`.
6. **Every 12 V path stays under 3 % voltage drop** at full load; the worst is 2.9 %, to the supply fans (calc-results §3). The air feed and the kit feed use two conductors per pole.
7. **Mass:** ELECTRICAL is 4.94 kg against the layout study's 3.05 kg allowance (calc-results §5): the power unit 2.80, the harness parts 1.00, the cord set 0.50, the hub zone 0.38, the lights 0.26. B2 with the unit inside is about 11.9 kg, under the 20 kg limit (D-03).
8. **Open:** the hub's interface (ISS-060), the parts on HOLD (§10), and the interfaces the other teams draw (§12). The Fusion drawing of the route model waits for the Mac's screen to be unlocked; its script is ready (BUILD-RECORD).

## Files

| File | What it is |
|---|---|
| [`calc-results.md`](calc-results.md) | Supply loading, mains current, voltage drop, heat added to the pod, mass (generated) |
| [`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`](710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv) | The load table (generated) |
| [`compliance-note.md`](compliance-note.md) | UL 962 / NEC Class 2 note |
| [`electrical_docs.py`](electrical_docs.py), [`wiring_diagram.py`](wiring_diagram.py) | Write the CSV files, the calculations and the wiring diagram from the model; `--check` fails if a file is stale |
| `../../02-Drawings/electrical/710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf` | Wiring diagram, 2 A3 sheets: the schematic; the harness list and two route views at 1:25 |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv` | Electrical parts list (generated), for the master BOM |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv` | Harness list: every segment with its conductors, length, plugs, grommets and voltage drop (generated) |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step` | The route model (Fusion writes cm, declared in the file, D-13) |
| `../../01-CAD-Native/electrical/` | The model data, the Fusion build, the edit test, the offline tests, the build record |

## 1. Sources

| Key | Source | Used for |
|---|---|---|
| BRIEF | ELECTRICAL group brief, 2026-10-31 | Scope and deliverables |
| PM | PM rulings in the ELECTRICAL group, 2026-10-31 | The plan as DECIDED; socket and LAN at about 1000 mm; inlet at v1's position; B2 at most 20 kg |
| DL | `v2/00-Control/decision-log.md` D-09 to D-11, D-26, D-41, D-44, D-50, D-51, D-58 to D-62, D-63, D-65, D-70, D-79 to D-81 | Decided design |
| REQ | `v2/00-Control/requirements.md` REQ-ELE-01 to 05, REQ-AIR-03, -04, -06, REQ-VCK-01 to 06 | Requirements |
| SEL | `v2/05-Engineering/hardware/selection.md` | Inlet, LAN feed-through, fans, lights, sockets (plan VT07–VT09) |
| AIR | `v2/05-Engineering/acoustics-air/report.md` | Fan duty and speeds; the air column and soffit |
| JNT | `v2/05-Engineering/joints/joints-register.md` | Seams, the B1–B2 closing seam, hardware numbers 838001, 838003, 838004 |
| SKL | Skeleton P04: `v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv` | Every size and position (derived in Fusion) |
| CEIL | CEILING P01 (PR #32): cassette gap 24 mm, cable holes at X ±583 | Ceiling route |
| V1 | `sources/v1/indoor-pod-v3-assembly.step`: 'Power Jack' X ±17.5, Z(v1) 279–317.5; 'Jack LAN' Z(v1) 349–371; inside plates Z(v1) 1008.5–1094.5 | The inlet's position |
| LKP | Public maker pages and datasheets, read 2026-10-31 (linked in the parts list) | Part data |

## 2. Architecture

```
ROOM SOCKET ─ cord set ─ INLET (B2 skin, v1 spot) ─┐
                                                  │  POWER UNIT 710001 in B2 (earthed, factory wired)
                                     RCBO C10 30 mA ─┬─ USER SOCKET (unit face, Z 1000)
                                                     ├─ PS1 60 W ─ F1 5 A ─ trunk ─ VOICE KIT DROP (12 V 5 A, capped)
                                                     ├─ PS2 60 W dimmable ─ F2 3 A ─ up B2, B4 ─ LIGHT SHELF
                                                     └─ PS3 60 W ─ trunk ─ AIR COLUMN fuse block ─ fans S, fans E, hub, call light
LAN ─ etherCON (B2 skin) ─ LAN socket port 1 (unit face); port 2 ─ trunk ─ voice kit drop (Cat6, capped)
```

- **Mains goes only to the outlets and the supplies, inside the unit** (REQ-ELE-01, D-10). No mains conductor enters a cassette, the ceiling or the air column.
- **12 V Class 2 everywhere else.** The supplies are double insulated (Class II), so the 12 V side is SELV and needs no earth.
- **Why the unit is in B2 near the centre:** v1's inlet spot is there, the mains lead from the inlet to the unit stays inside one bay of one panel, and the socket sits at v1's plate height. The trunk to the right wall is 12 V, so its length costs little (calc-results §3).

## 3. The power unit (710001)

| Item | Value | Status |
|---|---|---|
| Box | 300 W × 260 H × 72 D mm; front flush with the felt (Y 766), back 6 mm short of the skin side | assumption (sizes); calculation (depth) |
| Position | X 95–395, Z 870–1130, in one bay of B2 | DECIDED height (PM: about 1000 mm); assumption (X, clear of the B1–B2 closing seam member and its pin pocket); WALL confirms the bay |
| Face (1.5 mm aluminium, black anodised AA20 as the visible aluminium, D-67) | user socket (UTEN S300, plan VT07) and LAN socket (plan VT09), 86 × 86 each; the RCBO toggle behind a clear flap; vent slots top and bottom | PROPOSED |
| Inside | RCBO on a DIN rail; PS1, PS2, PS3; F1 and F2 in a fuse holder; PE terminal; the 12 V output leads leave through a grommeted slot in B2-CASS's cut-out (right) and a Ø20 grommet (top) | PROPOSED |
| Body | 1.0 mm aluminium 5052-H32, folded, mill finish (hidden, D-79), side flanges fixed to B2's vertical members with 4 × 838001 (M6 × 16) and 838004 washers into 838003 rivnuts: the pod's one bolt and one key (D-63) | PROPOSED |
| Cassette | B2-CASS has a cut-out 4 mm clear all round the unit, with returns, so the lining never touches the frame-mounted unit (D-17, D-26) | PROPOSED; WALL draws the cut-out |
| Mass | see calc-results §5 | calculation |

The inlet and the etherCON sit in B2's skin at X 120 (Z 313 and 375), with a 20 × 20 mm sleeve up the same bay to the unit's bottom. All of it is fitted in B2 at the factory, so B2 ships with the unit wired and tested.

## 4. 12 V circuits and the load table

The load table is in [`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`](710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv), and the supply loading in calc-results §1.

| Supply | Feeds | Protection |
|---|---|---|
| PS1, 60 W | The voice kit's reserved 12 V 5 A outlet (D-11, REQ-VCK-04) | F1 5 A in the unit; the supply's own Class 2 limit |
| PS2, 60 W dimmable | Light shelf, 24 W | F2 3 A in the unit |
| PS3, 60 W | The column fuse block behind the hub zone cover: F3a 2 A supply fans, F3b 2 A exhaust fans, F3c 1 A hub, F3d 1 A call light | Branch fuses protect the thinner branch cables; the 18 AWG feed is protected by the supply's own limit |

## 5. Routes, joints and site assembly

Routes are reserved spaces in the cassettes' 24 mm gap: 16 mm deep, which leaves 4 mm each side for the clips, centred in the gap (Y 787.5 on the back wall, X 1187.5 on the right wall). They are modelled in the Fusion design with the pockets and grommets (sheet 2 of the wiring diagram shows them at 1:25).

| Joint | Where | What crosses | How |
|---|---|---|---|
| X1 | The unit to B2-CASS | Air feed and hub link (one 10-way), kit feed, Cat6 (right); light feed (top) | The unit's 150 mm leads pass a 20 × 40 grommeted slot (right) or a Ø20 grommet (top) in the cut-out's returns. Mated in pockets P1 and P5 inside B2-CASS before it is hung. |
| X2 | Back-right inside corner, B2-CASS to R1-CASS | Same four cables | 4 × Ø12 grommets in B2-CASS's end return (the window between its felt and R1's back lip is only 12.5 mm). Mated in pocket P2 inside R1-CASS through a felt slot that B2-CASS's end hides. |
| X3 | R1-CASS into the air column | Air feed, dimming | A Ø20 felt exit behind the column; mated before the column is placed |
| X4 | B2-CASS to B4-CASS (horizontal seam) | Light feed | A Ø20 grommet pair through both returns; mated, then pushed up into pocket P4 |
| X5 | B4-CASS to the light shelf | Light feed | A Ø16 felt exit behind the shelf (pocket P6) |
| X6 | Air column to R2-CASS | Call light | A Ø12 felt hole behind the column, then a felt exit behind the call light bar |
| X7 | Voice kit drop, R1-CASS behind the screen | Kit power (capped 4-way outlet), Cat6 (capped keystone), draw wire | A Ø60 felt plug (FA-KIT) |

**Site order, two people, one 5 mm key, no electrician:**
1. Hang R1-CASS and R2-CASS. Their corner and column tails stay out.
2. Hold B2-CASS near the wall. Plug its leads into the unit's leads (X1) and into R1's corner tails (X2), push the pairs into P1 and P2, then hang B2-CASS.
3. Hold B4-CASS. Plug X4, push the pair into P4, then hang B4-CASS. Plug the shelf at X5 when the shelf goes up.
4. Before the air column goes in, plug X3 and X6 behind it. Then plug the fans at their boxes: the supply pair through DR's removable inner face, the exhaust pair through the soffit's underside (D-59).
5. Plug the room cord into the inlet, switch the RCBO on and check: fans start on presence, the knob dims the shelf, CALL lights the bar, the kit outlet reads 12 V.

**Plugs:** Molex Mini-Fit Jr, latching, UL94 V-0 housings. The way count tells circuits apart at the joints where several cross: 2-way for the lights, 4-way for the kit, and 10-way for the air feed together with the hub link. Data uses RJ45. The supply side is always the receptacle with female contacts.

## 6. Wire sizes and voltage drop

calc-results §3. Every circuit stays under 3 % from its supply to its load at the maximum current (calculation, copper at 60 °C).

## 7. Sensor hub, controls and the fans

- **Hub placement (REQ-ELE-04, D-70):** in the air column's 180 × 180 zone on its back face (Y −285), X 957–1137, Z 1110–1290. It is centred at Z 1200, seated eye height (SEL F3). It looks across the work-wall seat and sits 1 m above the kick grille, away from the exhaust grille at the soffit's far end. The zone is recessed 30 mm into the column's fill. CEILING models the column and keeps the zone and the chase.
- **Controls, in the same zone, all hub inputs (W44):** BOOST (D-33), TEST (the self-test, D-87), CALL and the LIGHT knob. The hub sets PS2's 0–10 V dimming over W24 (dim to off) and switches the call light through a current sense.
- **Self-test (D-87), what the wiring gives the hub to check:** the three 12 V rails (PS1 and PS2 sensed in the power unit over W24; PS3 is the hub's own supply), both fan pairs (PWM out, tach in: each pair at 30 % and 100 %, rpm within the maker's band), the shelf light (current sense on PS2's output, ramped 0 to 100 %), the call light (current sense on its branch), the inlet temperature sensor against the hub's own (within 2 K at start), and CO2, presence and sound in plausible ranges. It shows PASS, or the item that failed, on the hub's display in about 2 minutes (assumption). The test logic is the in-house team's (ISS-060); P01 wires every signal it needs.
- **Fans:** two 4-core leads (W40, W41): 12 V through F3a and F3b, a PWM signal each from the hub, and a tach each back to it. Two signals keep the two pairs balanced (D-61). The fans' PWM input is pulled up inside the fan, so an open PWM line means full speed (fail-safe; the fan sample confirms the iPPC's behaviour, H-ELE-07).
- **Inlet temperature sensor (D-50):** in the supply fan box inlet, on W42 to the hub's sensor port. The sensor part is on HOLD until the hub's sensor interface is known (H-ELE-06, ISS-060).
- **Interface the hub must give (for the in-house team; nothing about its insides goes here):** 12 V input (5 W assumed); 2 × PWM out (25 kHz, open drain); 2 × tach in (open collector); 1 × 0–10 V out (PS2's dimming); 1 × switched 12 V out, 0.5 A (call light); 5 × analog in (light knob, two light currents, PS1 and PS2 rails); 3 × button in (BOOST, TEST, CALL); 1 × temperature sensor port; a display for PASS or FAIL. If the hub lacks some of these, a small I/O board in the hub zone adds them and talks to the hub over one link (H-ELE-05).

## 8. Voice cockpit hooks (REQ-VCK-01 to 06)

| Hook | P01 provision | Status |
|---|---|---|
| Power, 12 V 5 A fused (VCK-04) | PS1 → F1 5 A → W30 → a capped Mini-Fit Jr 4-way outlet at the kit drop X7, on a 500 mm service loop | DECIDED (D-11); counted in the load and heat tables |
| Data (VCK-05) | Cat6 from LAN port 2 → W31 → a capped keystone at X7; the building LAN arrives at port 1 through the etherCON at v1's spot | DECIDED link; PROPOSED type |
| Cable path (VCK-03) | W32 draw wire: kit drop → column chase → soffit right end (mic, status light); W33 draw wire: back wall top → ceiling cassette → soffit back face (D-41). Every hole is made in the factory. | PROPOSED |
| Mounts (VCK-01, -06) | Not ELECTRICAL's: the screen and kit mounts are INTERIOR's inserts on the cassettes; the trunk band (Z 1085–1115) is kept clear for them | — |

## 9. Lights

- **Light shelf (D-70):** Häfele Loox5 2168 strip (6.0 W/m, 970 lm/m at 3000 K, Ra over 90) along the tops of the side and back walls. It is 4.434 m long: the back 2332 mm, and each side 1051 mm, from the soffit's back face to the back lining. It draws 26.6 W and gives about 4300 lm, uplighting the felt ceiling. It is fed at X 355 on the back wall: the back strip runs both ways from there, with jumpers in the shelf's channel to each side wall. Every run is 1.5 m or less, inside the maker's 3.5 m per feed. The strip weighs about 0.02 kg/m, inside D-85's 0.4 kg/m shelf budget.
- **Call scene (D-70):** a 900 mm bar of Loox5 2165 strip (3.0 W/m, about 440 lm) in a diffuser profile above the screen on the work wall, 2.7 W. The hub switches it from the CALL button. It lights the face from the screen side.
- **Total 29.3 W, inside REQ-AIR-06's 30 W budget.**
- **Risk, for the PM:** uplight onto dark grey felt gives little light on the ledge. The lumen method (assumption: the ceiling and walls reflect about 15 %, utilisation about 0.15) gives roughly 190 lx from the shelf alone, against the 300–500 lx usual for desk work. The call bar and the office light through the glass add to it. The 30 W budget can't fix that with indirect light alone. A down-lighting strip on the shelf's underside on the same channel, or a lighter ceiling felt, would. Measure on the prototype (ISS-004).

## 10. HOLD list

| ID | Item | Question or check | Release condition |
|---|---|---|---|
| H-ELE-01 | Grommets (Ø20 and Ø12 in 0.5 mm steel; the 20 × 40 slot edge) | Part with its panel range and its hole | Sample fit in a cassette return |
| H-ELE-02 | 12 V supplies and the dimmable driver | Data confirmed; Class 2 marking checked for the US phase | Datasheets on file (parts list) |
| H-ELE-03 | Inlet and etherCON fit in the 46 mm outer panel (skin 3 + bond 3 + frame bay) | Panel-thickness range and depth behind the panel | Datasheet check; sample in a B2 skin |
| H-ELE-04 | UTEN S300 socket-only code and the plate in the unit's face | Exact code (the plan's VT07 set includes a switch P01 doesn't use) | Code from the UTEN catalogue pp. 58–61 |
| H-ELE-05 | The hub's fan outputs | PWM or 0–10 V; current; connector | ISS-060 data |
| H-ELE-06 | Inlet temperature sensor | Type set by the hub's sensor port; accuracy for the 4 K limit | ISS-060 data |
| H-ELE-07 | Fan connectors at the fan boxes; the fans' 0 % PWM behaviour | Y-cable and harness end housing | Fan sample (ISS-077) |
| H-ELE-08 | The hub's supply voltage | 12 V direct, or a 12-to-5 V converter in the hub zone | ISS-060 data |
| H-ELE-09 | LED strips, call light bar, the shelf channel | Final strip by lumen check; the shelf's profile is INTERIOR's | Light-level test on the prototype (ISS-004) |
| H-ELE-10 | Cable clips on 0.5 mm galvanised steel | Adhesive mount or clip, with its hold on the tray | Pull test on a cassette tray |
| H-ELE-11 | ATO blade fuse holders (unit and column) | Part to name | Datasheet on file |
| H-ELE-12 | Cat6 RJ45 plugs, inline couplers, keystone | Part to name | Datasheet on file |
| H-ELE-13 | Current sense modules for the two lights | Part to name, output to suit the hub's input | ISS-060 data |

## 11. Tests (planned, not run: PLANNED / NOT TESTED)

1. **Power unit, in the factory, before B2 ships:** earth continuity inlet PE to the enclosure stud and B2's frame (at most 0.1 Ω); insulation resistance L+N to PE at 500 V DC (at least 1 MΩ); RCBO trip test; each supply's output 12 V ± 3 % at no load. The factory's electrician signs it.
2. **Harness segments, every one in the factory before it ships (D-87):** continuity, polarity and no shorts on a test board with mating plugs, latch pull test, and a label with its ID and "tested".
3. **On the prototype:** every circuit at full load (voltage at the far end, within 3 %); fans on presence, boost by CO2, heat and hand; PWM-open fail-safe; the 4 K and 800 ppm control with the hub; the light level at the ledge; and a timed plug-up of all joints by two people.

## 12. Open for others (interfaces, for the PM to route)

| Team | What ELECTRICAL needs | Where |
|---|---|---|
| WALL | B2: one clear bay X 95–395, Z 870–1130 for the unit, with 4 × 838003 rivnuts in its vertical members; the sleeve's path X 136–156, Z 301–870; the inlet and etherCON cut-outs in B2's skin at X 120, Z 313 and 375 (Ø23.8 + 2 × Ø3.2 and Ø24 + 2 × Ø3.2). B2-CASS: the cut-out with returns (304 × 264 mm), the 20 × 40 slot and the Ø20 hole in its returns, 4 × Ø12 in its right end return at Y 781.5, a Ø20 in its top return at X 355. B4-CASS: a Ø20 in its bottom return at X 355, a Ø16 felt exit at X 355, Z 2250, a Ø12 hole through its top lip at X 583, Z 2337.5. R1-CASS: the felt slot at the corner (Y 768–786, Z 1040–1160), the Ø20 felt exit at Y −298, Z 1100, the Ø60 kit plug at Y 240.5, Z 1180. R2-CASS: Ø12 felt holes at Y −298 and Y −209.5, Z 1450. | Wiring diagram sheet 2; model bodies |
| CEILING (AIR, INTERIOR) | The column's 24 × 24 chase against the right wall (X 1140–1164, Y −310 to −286) and its open side at the trunk entry; the hub zone (X 957–1137, Z 1110–1290, 30 deep); the soffit entry above the chase; the ceiling cassette's existing Ø20 holes at X 583 (D-41 route); the light shelf's channel and its feed point at X 355, Z 2250; the call light bar on R2; the ledge and screen fixings kept 15 mm off the trunk band Z 1085–1115 | Model bodies CHASE, HUB, TO-SOFFIT, C1-CEIL |
| FRONT | An opening in DR's back plate at the column top for W40 and W42: Y −665 to −645, Z 2100–2116, X 1140–1164 | Body TO-DR |
| AIR | The fans' leads and Y-cables at each fan box; the fan sample checks the 0 % PWM behaviour | W40, W41 |
| Control pack | Register rows for the four electrical folders (D-78); ISS-005, ISS-061 and ISS-062 can move to DECIDED on the PM's ruling; ISS-025: the inlet's protrusion (about 20 mm with its cap, assumption) goes on the GA as a listed protrusion | — |
| In-house team (via the PM) | The hub's supply, fan outputs, tach and sensor inputs, size and mounting (ISS-060) | §7 |
