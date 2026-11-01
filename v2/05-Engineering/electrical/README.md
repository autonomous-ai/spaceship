# ELECTRICAL design: Spaceship (FocusPod v2), P01

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-ELE-01 | P01 | DRAFT | 2026-10-31 | ELECTRICAL Engineer |

The pod's electrical design: mains, the 24 V and 12 V buses, the sensor hub, lights, fans, the voice cockpit hooks and the harness. It is built so that two people can put it together with no electrician. Every number carries a status (conventions §9). Choices the PM has ruled on are DECIDED; the rest are PROPOSED, and work goes ahead on them (AGENTS.md). Bought parts stay on HOLD: nothing was ordered and no supplier was contacted.

## Result

1. **Mains in one place, made in the factory (DECIDED, PM ruling 2026-10-31).** One earthed aluminium power unit sits in the lower back panel B2, its face flush with the felt at the ledge height (centre Z 1000). It holds the user outlets (a tamper-resistant GFCI duplex NEMA 5-15R) and two LAN keystone jacks on its face, a 15 A breaker behind a window, and the three 12 V supplies. Its mains side is US 120 V 60 Hz with UL-listed parts, on the prototype too (D-133); the prototype is tested in Vietnam through a 220-to-110 V step-down transformer. The inlet and the LAN feed-through use v1's back-wall spot. v1 had them at X 0, which is now the B1–B2 closing seam (D-65), so they move into B2 at X 120, at v1's heights (Z 313 and 375). On site, nothing mains is connected. Only B2's frame is bonded to earth.
2. **Three Class 2 supplies (DECIDED, D-168).** The load is about 132 W at its hardware maximum and about 34 W typical (calc-results §1). PS1, a Mean Well CLG-100-24 (96 W), gives the voice kit hook its one 24 V feed: the kit's 60 W peak is 62.5 % of it, under its 77 W cap (80 %). PS2, an LPV-60-24, feeds all the lights at 24 V through the light controller; PS3, an LPV-60-12, the four fans and the hub at 12 V. A light fault can't stall the fresh air. Each is a Class 2 power unit on its own sheet (UL 1310), so every cable in the walls, ceiling and air column is power-limited, and no two Class 2 sources ever share a 0 V. The mains side is US 120 V 60 Hz with UL-listed parts (D-133, [compliance note](compliance-note.md)).
3. **Cables in the lining cassettes' 24 mm gap, clipped to the cassettes only (D-26, D-41), with a plug pair at every joint (DECIDED).** The trunk runs from the unit along B2's lining to the back-right corner, then along R1's lining at Z 1100, past the voice-kit drop, into a cable chase in the air column. The light feed runs up B2 and B4 to the light shelf. A draw-wire route runs through the ceiling cassette (D-41). Every hole in sheet steel has a grommet. 7 joints carry 13 plug pairs.
4. **The hub runs the air and the lights, and tests them (D-09, D-44, D-50, D-61, D-87).** The fans and the hub sit at the air column, with short cables. Two PWM signals drive the two balanced fan pairs, with tach back. The hub also sets the three light channels (uplight, down-light, call light) over RS-485 and keeps them at about 22 W in all (PM ruling). Its **self-test button (D-87)** checks the three rails (24 V kit and lights, 12 V air), runs both fan pairs and reads their tach, steps each light channel and reads PS2's current change, reads the sensors, and shows PASS or the failing item. If a PWM line opens, the fans run at full speed, so a hub fault never stops the fresh air. Every harness segment is tested in the factory before it ships (D-87).
5. **CAD:** 41 reserved spaces (routes, pockets, bushings, the unit, the inlet, the hub zone) in `710000_P01_ELECTRICAL_CAD`, derived from skeleton P04. Its own clash check runs against the skeleton's real bodies. The three sheet-metal parts we make each have their own design: the folded enclosure body 711001 has a drawing; the flat front plate 711002 and hub zone plate 711005 are defined by their DXF and parts-list row (D-89 part 4). Cut-outs that wait on module data are marked HOLD (PM ruling). See `v2/01-CAD-Native/electrical/MANIFEST.md` and `BUILD-RECORD.md`.
6. **Every 24 V and 12 V path stays under 3 % voltage drop** at full load; the worst is 2.9 %, to the supply fans (calc-results §3). The air feed and the kit feed use two conductors per pole.
7. **Mass:** ELECTRICAL is 4.94 kg against the layout study's 3.05 kg allowance (calc-results §5): the power unit 2.80, the harness parts 1.00, the cord set 0.50, the hub zone 0.38, the lights 0.26. B2 with the unit inside is about 11.9 kg, under the 20 kg limit (D-03).
8. **Open:** the hub's interface (ISS-060), the parts on HOLD (§10), and the interfaces the other teams draw (§12). The route model has no separate Fusion drawing: sheet 3 of the wiring diagram is its drawing (PM ruling 2026-11-01). The folded enclosure body has its Fusion drawing (711001, A2).

## Files

| File | What it is |
|---|---|
| [`calc-results.md`](calc-results.md) | Supply loading, mains current, voltage drop, heat added to the pod, mass (generated) |
| [`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`](710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv) | The load table (generated) |
| [`compliance-note.md`](compliance-note.md) | UL 962 / NEC Class 2 note |
| [`electrical_docs.py`](electrical_docs.py), [`wiring_diagram.py`](wiring_diagram.py), [`assembly_sheets.py`](assembly_sheets.py), [`sheet_kit.py`](sheet_kit.py) | Write the CSV files, the calculations, the wiring diagram and the assembly sheets from the model; `--check` fails if a file is stale. `sheet_kit.py` keeps every letter at 2.5 mm or more (titles 3.5; ISO 3098 capital heights), wraps text and table cells instead of cutting them, and fails a sheet with overlapping text or a line through a text |
| `../../02-Drawings/electrical/710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf` | Wiring diagram, 3 A1 sheets: the schematic; the harness list; two route views at 1:10 with the site order and keep-outs |
| `../../02-Drawings/electrical/7100x1_P01_*_DWG.pdf` | The 7 assembly sheets (A2): power unit, hub zone, 4 harnesses and the draw wire set |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv` | Electrical parts list (generated), for the master BOM |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv` | Harness list: every segment with its conductors, length, plugs, grommets and voltage drop (generated) |
| `../../03-Manufacturing/electrical/710000_P01_ELECTRICAL_STEP.step` | The route model (Fusion writes cm, declared in the file, D-13) |
| `../../01-CAD-Native/electrical/` | The model data, the Fusion builds (route model; sheet-metal parts), the edit test, the offline tests, the manifest and the build record |
| `../../02-Drawings/electrical/711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG.pdf` | Fusion drawing of the folded enclosure body (A2: views, dimensions, datums; notes and the hole list H01-H08 in its text block). The route model's drawing is sheet 3 of the wiring diagram (PM ruling 2026-11-01). The flat front plate 711002 and hub plate 711005 have no drawing: their DXF and parts-list row define them (D-89 part 4). |
| `../../03-Manufacturing/electrical/*_STEP.step`, `*_DXF.dxf` | STEP of each design (cm, declared, D-13); DXF flat pattern of the body and the plates' outlines (mm) |

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
                                     BREAKER 15 A ───┬─ GFCI RECEPTACLE, TR 5-15R (unit face, Z 1050)
                                                     ├─ PS1 96 W 24 V ─ F1 5 A ─ trunk (4 x 16 AWG, 2 per pole) ─ VOICE KIT DROP (one 24 V feed, capped)
                                                     ├─ PS2 60 W 24 V ─ F2 5 A ─ LIGHT CONTROLLER ─ up B2, B4 ─ SHELF: uplight, down-light, call drop
                                                     └─ PS3 60 W 12 V ─ trunk ─ AIR COLUMN fuse block ─ fans S, fans E, hub
LAN ─ etherCON (B2 skin) ─ keystone jack 1 (unit face); keystone jack 2 ─ trunk ─ voice kit drop (Cat6, capped)
```

- **Mains goes only to the outlets and the supplies, inside the unit** (REQ-ELE-01, D-10). No mains conductor enters a cassette, the ceiling or the air column.
- **24 V and 12 V Class 2 everywhere else.** Each output is isolated from mains (SELV): the LPV-60s are double insulated (Class II); the CLG-100's case is earthed through its FG lead to the unit's earth stud.
- **Why the unit is in B2 near the centre:** v1's inlet spot is there, the mains lead from the inlet to the unit stays inside one bay of one panel, and the socket sits at v1's plate height. The trunk to the right wall is 12 V, so its length costs little (calc-results §3).

## 3. The power unit (710001)

| Item | Value | Status |
|---|---|---|
| Box | 296 W × 260 H × 72 D mm (narrowed from 300 so its right side clears B2's first stud at X 395.75 by 4.75 mm, WALL through the PM); front flush with the felt (Y 766), back 6 mm short of the skin side | assumption (sizes); calculation (depth). The body (711001) and front plate (711002) are modelled in their own designs. The body's holes follow the named parts (2026-11-01): PEM CLA-M4-1 clinch nuts in Ø5.94 holes 10 from the top and bottom (H05-H08, 12 from the lip's free edge), a PEM FHA-M5-12 earth stud in a Ø5.0 hole in the bottom near the mains entry (H09; its place an assumption until the inside layout), and H04 Ø22.2 for the NMLT-11 conduit connector; the front plate's screws moved with the nuts. Still HOLD: the fixing to B2's frame (WALL, IF-12). |
| Position | X 95–391, Z 870–1130, in one bay of B2 | DECIDED height (PM: about 1000 mm); assumption (X, clear of the B1–B2 closing seam member and its pin pocket); WALL confirms the bay |
| Face: front plate 320 × 284, 1.5 mm aluminium, black anodised AA20 as the visible aluminium (D-67), covering the cut-out's felt edge 8 mm all round and standing 2 mm off the felt on 4 spacers | the GFCI receptacle in a decorator opening 33.6 × 67 held by two 6-32 plate screws, two LAN keystone jacks in 14.9 × 19.4 openings, the breaker through a 19 × 45 window (D-133); vent slots top and bottom | PROPOSED |
| Inside | the breaker on a DIN rail; PS1 (222 × 68 × 39) and PS2, PS3 (162.5 × 42.5 × 32 each) lying flat on the back wall in one stack (68 + 2 × 42.5 = 153 mm tall, up to 39 deep, clear of the front devices' 30 mm and the breaker; a calculation, the unit's inside layout is the factory's drawing); F1 and F2 in fuse holders; PE terminal; the 24 V and 12 V output leads leave through two Ø19.1 bushed exits in the unit's right side and a Ø19.1 bushed hole in its top, straight into B2-CASS's cable gap (the cut-out is plain: no steel on their path) | PROPOSED |
| Body | 1.0 mm aluminium 5052-H32, folded, mill finish (hidden, D-79), side flanges fixed to B2's vertical members with 4 × 838001 (M6 × 16) and 838004 washers into 838003 rivnuts: the pod's one bolt and one key (D-63) | PROPOSED |
| Cassette | B2-CASS has a plain cut-out through its tray base and felt, 4 mm clear all round the unit (304 × 268), so the lining never touches the frame-mounted unit (D-17, D-26). No returns: WALL found they can't be folded from a flat blank (corner tabs overlap). The front plate covers the cut felt edge. | PROPOSED; WALL draws the cut-out |
| Mass | see calc-results §5 | calculation |

The inlet and the etherCON sit in B2's skin at X 120 (Z 313 and 375), the inlet's rear in a rear box (711003, modelled with the inlet in the next rebuild: Neutrik makes no rear cover), with the 1/2 in conduit from that box up the same bay to the unit's bottom. All of it is fitted in B2 at the factory, so B2 ships with the unit wired and tested.

## 4. 24 V and 12 V circuits and the load table

The load table is in [`710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv`](710000_P01_ELECTRICAL-LOAD-TABLE_CALC.csv), and the supply loading in calc-results §1.

| Supply | Feeds | Protection |
|---|---|---|
| PS1, 96 W, 24 V | The voice kit's one 24 V Class 2 feed: its 60 W peak is 62.5 % of the supply, under the 77 W cap (D-11, D-88, REQ-VCK-04, D-168) | F1 5 A in the unit; the supply's own Class 2 limit |
| PS2, 60 W, 24 V | The light controller: uplight (26.4 W at full), down-light (11.4 W), call light (2.7 W); the hub holds the three at about 22 W | F2 5 A in the unit |
| PS3, 60 W, 12 V | The column fuse block behind the hub zone cover: F3a 2 A supply fans, F3b 2 A exhaust fans, F3c 1 A hub | Branch fuses protect the thinner branch cables; the feed is protected by the supply's own limit |

## 5. Routes, joints and site assembly

Routes are reserved spaces in the cassettes' 24 mm gap: 16 mm deep, which leaves 4 mm each side for the clips, centred in the gap (Y 787.5 on the back wall, X 1187.5 on the right wall). They are modelled in the Fusion design with the pockets and grommets (sheet 2 of the wiring diagram shows them at 1:25).

| Joint | Where | What crosses | How |
|---|---|---|---|
| X1 | The unit to B2-CASS | Air feed and hub link (one 10-way), kit feed, Cat6 (right); light feed (top) | The unit's 150 mm leads leave its right side (H01, H02) and top (H03), each bushed, straight into B2-CASS's cable gap through the plain cut-out. Mated in pockets P1 and P5 inside B2-CASS before it is hung. |
| X2 | Back-right inside corner, B2-CASS to R1-CASS | Same four cables | 4 × Ø12 grommets in B2-CASS's end return (the window between its felt and R1's back lip is only 12.5 mm). Mated in pocket P2 inside R1-CASS through a felt slot that B2-CASS's end hides. |
| X3 | R1-CASS into the air column | Air feed, dimming | A Ø19.1 felt exit behind the column; mated before the column is placed |
| X4 | B2-CASS to B4-CASS (horizontal seam) | Light feed | A Ø19.1 hole pair through both returns, each with a Heyco 2836 bushing; mated, then pushed up into pocket P4 |
| X5 | B4-CASS to the light shelf | Light feed | A Ø16 felt exit behind the shelf (pocket P6) |
| X6 | Light shelf to R2-CASS | Call light drop | A Ø12 felt hole behind the shelf at Y −209.5; mated, pushed into pocket P7, then straight down R2-CASS to a felt exit behind the call bar |
| X7 | Voice kit drop, R1-CASS behind the screen | Kit power (capped 4-way outlet), Cat6 (capped keystone), draw wire | A Ø60 felt plug (FA-KIT) |

**Holes:** every hole through a sheet gets a bushing: the six in the cassettes' 0.5 mm steel returns and lips, the hole through DR's back plate where the supply-fan and sensor run enters DR (G-DR, Y −645, Z 2108), and the hole through the soffit's casing above the column chase (G-SOFFIT, Z 2120). The two slots get an edge strip. The felt holes (FX-SHELF, FA-KIT, FX-COL, FX-CALL1, FX-CALL2, FS-CNR) pass the felt only. In WALL's and CEILING's cassette models the felt sits on 12 mm edge lips with the 24 mm gap behind it, so there is no steel edge at those spots, and a bushing (made for 0.5–1.6 mm panels) has nothing to sit in.

**Slack across the floating gap:** the power unit's leads cross the 4 mm gap to the floating B2-CASS, so they run slack to their first clip, with no clip within 150 mm of the cut-out.

**Site order, two people, one 5 mm key, no electrician:**
1. Hang R1-CASS and R2-CASS. Their corner and column tails stay out.
2. Hold B2-CASS near the wall. Plug its leads into the unit's leads (X1) and into R1's corner tails (X2), push the pairs into P1 and P2, then hang B2-CASS.
3. Hold B4-CASS. Plug X4, push the pair into P4, then hang B4-CASS. Plug the shelf at X5 when the shelf goes up.
4. Before the air column goes in, plug X3 and X6 behind it. Then plug the fans at their boxes: the supply pair through DR's removable inner face, the exhaust pair through the soffit's underside (D-59).
5. Plug the room cord into the inlet, switch the breaker on, press the GFCI's TEST and RESET, and check: fans start on presence, the knob dims the shelf, CALL lights the bar, the kit outlet reads 24 V.

**Plugs:** Molex Mini-Fit Jr, latching, UL94 V-0 housings. The way count tells circuits apart at the joints where several cross: 2-way for the lights, 4-way for the kit, and 10-way for the air feed together with the hub link. Data uses RJ45. The supply side is always the receptacle with female contacts.

## 6. Wire sizes and voltage drop

calc-results §3. Every circuit stays under 3 % from its supply to its load at the maximum current (calculation, copper at 60 °C).

## 7. Sensor hub, controls and the fans

- **Hub placement (REQ-ELE-04, D-70):** in the air column's 180 × 180 zone on its back face (Y −285), X 957–1137, Z 1110–1290. It is centred at Z 1200, seated eye height (SEL F3). It looks across the work-wall seat and sits 1 m above the kick grille, away from the exhaust grille at the soffit's far end. The zone is recessed 30 mm into the column's fill. CEILING models the column and keeps the zone and the chase.
- **Controls, in the same zone, all hub inputs (W44):** BOOST (D-33), TEST (the self-test, D-87), CALL and the LIGHT knob. The hub sets the light controller's three channels over RS-485 on W24.
- **Self-test (D-87), what the wiring gives the hub to check:** all three rails (PS1's and PS2's 24 V sensed in the power unit over W24; PS3's 12 V is the hub's own supply), both fan pairs (PWM out, tach in: each pair at 30 % and 100 %, rpm within the maker's band), each light channel in turn (the current change on PS2's output), the inlet temperature sensor against the hub's own (within 2 K at start), and CO2, presence and sound in plausible ranges. It shows PASS, or the item that failed, on the hub's display in about 2 minutes (assumption). The test logic is the in-house team's (ISS-060); P01 wires every signal it needs.
- **Fans:** two 4-core leads (W40, W41): 12 V through F3a and F3b, a PWM signal each from the hub, and a tach each back to it. Two signals keep the two pairs balanced (D-61). The fans' PWM input is pulled up inside the fan, so an open PWM line means full speed (fail-safe; the fan sample confirms the iPPC's behaviour, H-ELE-07).
- **Inlet temperature sensor (D-50):** in the supply fan box inlet, on W42 to the hub's sensor port. The sensor part is on HOLD until the hub's sensor interface is known (H-ELE-06, ISS-060).
- **Interface the hub must give (for the in-house team; nothing about its insides goes here):** 12 V input (5 W assumed); 2 × PWM out (25 kHz, open drain); 2 × tach in (open collector); 1 × RS-485 out (the light controller); 4 × analog in (light knob, PS2's current, and the PS1 and PS2 rails: 24 V each, so each sense input needs a divider on the hub side, D-168); 3 × button in (BOOST, TEST, CALL); 1 × temperature sensor port; a display for PASS or FAIL. If the hub lacks some of these, a small I/O board in the hub zone adds them and talks to the hub over one link (H-ELE-05).

## 8. Voice cockpit hooks (REQ-VCK-01 to 06)

| Hook | P01 provision | Status |
|---|---|---|
| Power, one 24 V Class 2 feed (VCK-04, D-168) | PS1 → F1 5 A → W30 (4 x 16 AWG, two cores per pole) → a capped Mini-Fit Jr 4-way outlet at the kit drop X7 (two pins per pole), on a 500 mm service loop; 60 W peak, 40 W average (D-88); the kit takes 24 V in (D-168) | DECIDED (D-11, D-168); counted in the load and heat tables |
| Data (VCK-05) | Cat6 from LAN port 2 → W31 → a capped keystone at X7; the building LAN arrives at port 1 through the etherCON at v1's spot | DECIDED link; PROPOSED type |
| Cable path (VCK-03) | W32 draw wire: kit drop → column chase → soffit right end (mic, status light); W33 draw wire: back wall top → ceiling cassette → soffit back face (D-41). Every hole is made in the factory. | PROPOSED |
| Mounts (VCK-01, -06) | Not ELECTRICAL's: the screen and kit mounts are INTERIOR's inserts on the cassettes; the trunk band (Z 1085–1115) is kept clear for them | — |

## 9. Lights

- **Uplight on the light shelf (D-70):** Häfele's 24 V 6.0 W/m strip (LED 3145, the US twin of the 2168: 970 lm/m at 3000 K, 162 lm/W, Ra over 90; D-168) along the tops of the side and back walls, 4.40 m in four runs of whole 50 mm sections (1.15 m each way on the back, 1.05 m on each side). It runs from the soffit's back face to the back lining, fed at X 346 on the back wall, with jumpers in the shelf's channel. It is 26.4 W and about 4,270 lm at full.
- **Down-light (PM rulings 2026-11-01, D-126):** two rows of the same strip, 2 × 0.95 m (it cuts every 50 mm at 24 V), side by side in a bought aluminium LED profile under the right-wall shelf (718101, 23 × 12.5, Tech-Light P13-2 type, 991 mm) behind its clip-in satin cover (718102), aimed at the ledge: 11.4 W and about 1,840 lm. Bare, that gives about 325 lx on the ledge at full; through the satin cover, which passes at least 86 % (D-127), 279 to 292 lx. With the uplight's share in the work scene (10.6 W, about 66 lx) the ledge gets 345 to 358 lx when new, at the same 22 W, with room for about 15 % from aging and dust. No clear cover: the shelves are open underneath, so the LED dots would show from the seat. The cover is HOLD: Tech-Light lists only 98 / 70 / 63 % covers for the P13-2 type, and no satin cover of 86 % is verified for it yet. This is a calculation: a Lambertian strip 1.2 m above a 1000 × 350 mm ledge at Z 1000, with no reflections. One row would give only about half, because most of a strip's light falls beside a 350 mm ledge.
- **Call light (D-70):** a 900 mm bar of Häfele's 24 V 3.0 W/m strip (LED 3142, the 2165's twin: about 155 lm/W, about 420 lm) in a diffuser profile above the screen, 2.7 W. Its feed drops from the shelf straight down R2-CASS.
- **About 22 W in all, balanced by the hub (PM ruling):** in the work scene the down-light is full and the uplight runs at 10.6 W (about 1,710 lm), so the ledge gets about 279 + 66 ≈ 345 lx through the satin cover at 86 % (calculation; measured on the prototype, ISS-004). In the call scene the call light is on and the hub trims the down-light to 9.6 W, about 335 lx. The three channels come from one 24 V supply through the light controller's PWM channels, set by the hub (H-ELE-14). Every strip run is 1.5 m or less, inside the maker's 3.5 m per feed. The strips weigh about 0.02 kg/m, inside D-85's 0.4 kg/m shelf budget.
- **CEILING owns the shelf:** it needs an up-facing channel for one 8 mm strip all round, the down-light's bought LED profile with its opal cover for two 8 mm strips along the right wall (D-126: ELECTRICAL lists 718101 to 718104, CEILING places them), a wiring channel for the jumpers, the feed entry at X 346 on the back wall and the call drop at Y −209.5 on the right wall, both at Z 2250 behind the shelf.
- **Check:** the light level on the ledge, measured on the prototype (ISS-004); the target is about 300 lx (PM ruling).

## 10. HOLD list

| ID | Item | Question or check | Release condition |
|---|---|---|---|
| H-ELE-01 | Bushings and edge strip | Named: Heyco 2836N thin panel bushing (locks in 0.5 to 1.6 mm sheet; the plain 2836 locks only at 1.6 mm), Heyco 12431 grommet channel (0.5 to 3.2 mm). Still open: DR's back plate (G-DR, 1.0-2.7 mm, FRONT HOLD-10) and the soffit's casing (G-SOFFIT) over 1.6 mm need a thicker-panel bushing | Sample fit in a cassette return; FRONT and CEILING give the plate thicknesses |
| H-ELE-02 | The supplies (24 V and 12 V) and the dimmable driver | Data confirmed; Class 2 marking checked for the US phase | Datasheets on file (parts list) |
| H-ELE-03 | Inlet and etherCON fit in the 46 mm outer panel (skin 3 + bond 3 + frame bay) | The inlet NAC3MPX-TOP reaches 31.2 mm behind its flange (38.2 overall; Neutrik ST-NAC3MPX-TOP), about 28 behind the skin's inside face; Neutrik gives no panel-thickness range. It is a UL 498 Recognized component, so its rear goes in the rear box 711003, where the conduit's second NMLT-11 ends. Straight disconnects and the 14 AWG bends need about 60 mm behind the skin, over the 43 mm bay: flag disconnects or a flatter lead dress, settled when 711003 is modelled. The etherCON NE8FDY-C6-B reaches 39.85 mm behind its flange, and its 3 mm panel limit is the skin's thickness | Model 711003 with the inlet; sample in a B2 skin |
| H-ELE-04 | The US outlets' parts (D-133) | Named: Pass & Seymour 1597TRW GFCI (1595TRW is no longer listed; the same decorator body) and Panduit NK688MWH keystone jacks. Their sheets give no panel cut-out: prove the decorator 33.6 x 67 and keystone 14.9 x 19.4 openings in the 1.5 mm plate | A sample of the front plate with both parts fitted |
| H-ELE-05 | The hub's fan outputs | PWM or 0–10 V; current; connector | ISS-060 data |
| H-ELE-06 | Inlet temperature sensor | Type set by the hub's sensor port; accuracy for the 4 K limit | ISS-060 data |
| H-ELE-07 | Fan connectors at the fan boxes; the fans' 0 % PWM behaviour | Y-cable and harness end housing | Fan sample (ISS-077) |
| H-ELE-08 | The hub's supply voltage | 12 V direct, or a 12-to-5 V converter in the hub zone | ISS-060 data |
| H-ELE-09 | LED strips, call light bar, the shelf's profile | Named from Häfele America's 24 V range (D-168; it sells no 12 V lighting from 2026): LED 3145 833.76.226 (the 2168's twin) and LED 3142 833.76.216 (the 2165's twin), 3000 K, the same light per metre, cut every 50 mm; feed lead 833.75.763; call light profile 2191 with a milk lens 833.72.861 and end caps 833.72.853. Still open: the shelf's profile and satin cover (718101-718104): no maker sheet read gives a 23 x 12.5 surface profile with a satin cover of 86 % or more (D-127) | A profile family with its sheet, or the PM's call on a taller one (the look); light-level test on the prototype (ISS-004) |
| H-ELE-10 | Cable clips on 0.5 mm galvanised steel | Named: Heyco 3904 (PMT 150) push-mount tie: it needs a Ø6.4 mm hole at each clip point in the cassette trays | WALL and CEILING add the holes to their trays (an interface); pull test on a cassette tray |
| H-ELE-11 | ATO blade fuse holders (unit and column) | Named: Littelfuse FHAC0001ZXJ, with cover, 16 AWG leads, 20 A at 32 V DC; fuses Littelfuse 0287 ATOF 5, 2 and 1 A | Closed: datasheets on file |
| H-ELE-12 | Cat6 RJ45 plugs, inline couplers, keystone | Named: Panduit SP688E-C plugs, CC688IW couplers (Panduit allows two per channel: X1 and X2), NK688MWH jacks with a PSL-DCJB block-out at X7 (it comes out only with Panduit's tool, one per pack), Belden 3612 cable. The etherCON is now the CAT6 IDC jack NE8FDY-C6-B, so it adds no coupler to the kit's channel (the CAT5e feedthrough NE8FDP did) | The 3612's insulated core size isn't published: a sample must measure 0.91 to 1.07 mm for the plug (Panduit PN649A) |
| H-ELE-13 | Current sense module on PS2's output | Part to name, output to suit the hub's input | ISS-060 data |
| H-ELE-14 | Light controller, 5-channel 12-24 V PWM, DMX512 | Named: LTECH LT-995, 5 channels at 6 A (3 used), 12-24 V, common +V, DMX512 on its screw terminal (no Modbus); rated -30 to 65 °C; cURus E500585. Its sheet doesn't say what it does when the data stops | Bench test with the 24 V strips: on a lost DMX link it holds its level or goes dark, never brighter |
| H-ELE-15 | The body's holes for the named parts | Closed by #353 (merged): H05-H08 Ø5.94 +0.08 for the CLA-M4-1 nuts (10 mm from the lip's fold, 12 from its free edge, over PEM's 7.1), H09 Ø5.0 +0.08 for the FHA-M5-12 earth stud, H04 Ø22.2 for the NMLT-11 | Closed |

## 11. Tests (planned, not run: PLANNED / NOT TESTED)

1. **Power unit, in the factory, before B2 ships:** ground continuity, inlet ground to the enclosure stud and B2's frame (at most 0.1 Ω); dielectric withstand, L+N to ground, 1240 V AC for 1 min (1000 V + 2 × 120 V, D-133); the GFCI's TEST trips it; each supply's output 12 V ± 3 % at no load. The factory's electrician signs it.
2. **Harness segments, every one in the factory before it ships (D-87):** continuity, polarity and no shorts on a test board with mating plugs, latch pull test, and a label with its ID and "tested".
3. **On the prototype:** every circuit at full load (voltage at the far end, within 3 %); fans on presence, boost by CO2, heat and hand; PWM-open fail-safe; the 4 K and 800 ppm control with the hub; the light level at the ledge; and a timed plug-up of all joints by two people.

## 12. Open for others (interfaces, for the PM to route)

| Team | What ELECTRICAL needs | Where |
|---|---|---|
| WALL | B2: one clear bay X 95–391, Z 870–1130 for the unit (4.75 mm clear of the first stud at X 395.75), with 4 × 838003 rivnuts in its vertical members; the sleeve's path X 140–160, Z 301–870; the inlet and etherCON cut-outs in B2's skin at X 120, Z 313 and 375 (Ø23.8 + 2 × Ø3.2 and Ø24 + 2 × Ø3.2). B2-CASS: a plain cut-out through the tray base and felt, no returns (304 × 268 mm, X 91–395, Z 866–1134, 4 mm clear of the unit all round; the unit's leads leave its side at Z 1045 and 1085 and its top at X 346 straight into the gap), 4 × Ø12 in its right end return at Y 781.5, a Ø19.1 in its top return at X 346. B4-CASS: a Ø19.1 in its bottom return at X 346, a Ø16 felt exit at X 346, Z 2250, a Ø12 felt-only hole below its top lip at X 583, Z 2330 (its top 2 mm below the lip: no hole through a lip, D-69). R1-CASS: the felt slot at the corner (Y 768–786, Z 1040–1160), the Ø19.1 felt exit at Y −298, Z 1100, the Ø60 kit plug at Y 240.5, Z 1180. R2-CASS: Ø12 felt holes at Y −298 and Y −209.5, Z 1450. | Wiring diagram sheet 2; model bodies |
| CEILING (AIR, INTERIOR) | The column's 24 × 24 chase against the right wall (X 1140–1164, Y −310 to −286) and its open side at the trunk entry; the hub zone (X 957–1137, Z 1110–1290, 30 deep); the soffit entry above the chase; the ceiling cassette's holes at X 583 (D-41 route), Ø19.1 for the Heyco 2836 bushings (CEILING's model has 20 mm, its assumption): the back-return hole at Z 2330, level with B4-CASS's felt hole below its lip, the front-return hole at Z 2337.5; the light shelf's channel and its feed point at X 346, Z 2250; the call light bar on R2; the ledge and screen fixings kept 15 mm off the trunk band Z 1085–1115 | Model bodies CHASE, HUB, TO-SOFFIT, C1-CEIL |
| FRONT | A Ø19.1 bushed hole in DR's back plate at the column top for W40 and W42: X 1152, Z 2108 (G-DR); the run inside DR to the supply fan box (IN-DR) | Bodies G-DR, IN-DR |
| AIR | The fans' leads and Y-cables at each fan box; the fan sample checks the 0 % PWM behaviour | W40, W41 |
| Control pack | Register rows for the four electrical folders (D-78); ISS-005, ISS-061 and ISS-062 can move to DECIDED on the PM's ruling; ISS-025: the inlet's protrusion (about 20 mm with its cap, assumption) goes on the GA as a listed protrusion | — |
| In-house team (via the PM) | The hub's supply, fan outputs, tach and sensor inputs, size and mounting (ISS-060) | §7 |
