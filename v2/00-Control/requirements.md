# Requirements: Spaceship (FocusPod v2)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-CTL-001 | P01 | DRAFT | 2026-10-31 | Control pack |

Everything the v2 prototype design must meet, each item with a number where one exists, a status and a source. Status values are defined in `conventions.md` §9. **DECIDED** means the PM has ruled; the ruling is in `decision-log.md` (D-nn). **PROPOSED** means our working answer until the PM rules on it. Open points link to `issue-register.csv` (ISS-nnn).

**Sources**

| Key | Document |
|---|---|
| PLAN | `v2/PLAN.md`, approved by the product owner on 2026-10-31 |
| BP | `v2/00-Control/v2-build-plan.pdf`, the v2 build plan from the indoor pod lead engineer (page or section given) |
| GL | `docs/engineering-guideline.md` (hardware engineering lead) |
| MS | `v2/research/market-study.md` |
| V1 | `sources/v1/` (STEP, BOM, drawings) |
| PO-1031 | Product owner's updates passed on by the Lead in the Swarm chat on 2026-10-31: the working name Spaceship; hooks for a later voice cockpit kit; reuse of Autonomous's in-house modules (the Desk Pro AI sensor hub, and Lamp electronics); a 12 V DC bus; cockpit hooks of 12 V 5 A; the default decor colour |
| DL | `v2/00-Control/decision-log.md`: the PM's decisions D-01…D-15 of 2026-10-31. They take in the Lead's earlier rulings that day on quiet, weight, front material, assembly method and decor colour. |
| HW | `v2/05-Engineering/acoustics-air/report.md` on the Hardware Engineer's branch (commit ae219f6, not yet in main): the final wall and ceiling stack, its weight and its calculated sound |
| CALC | Calculations in section H of this file |

## A. Scope and the hard rule

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-SCP-01 | Indoor only: an air-conditioned room with a flat, level floor. No weather, UV, snow, wind or uneven ground. Size the structure for indoor loads: people leaning on it, shipping, and assembling it more than once. | indoor use only | confirmed | PLAN "Same look, lighter bones" | Load cases in the joint register |
| REQ-SCP-02 | US rules (UL, fire, sprinklers) and US 120 V are out of scope for the prototype. The plan's Vietnamese 220 V parts are fine. | 220 V parts for the prototype | DECIDED (D-14) | PLAN "Later, not in the v2 prototype"; DL D-14 | — |
| REQ-SCP-03 | The pod ships empty: no table, no furniture (ISS-006). | 0 furniture items | DECIDED (D-06) | PLAN "Removed"; DL D-06 | BOM |
| REQ-SCP-04 | The one-cable dock, room mic and agent status light are not built in. Hooks for a later voice cockpit kit are reserved (section F). | — | confirmed; DECIDED (hooks, D-11) | PLAN "Left out of v2"; PO-1031; DL D-11 | — |
| REQ-LOOK-01 | **The look stays exactly the same**: the faceted front, overall size, proportions, colours and glass layout. Every saving is invisible from outside. | same as v1 and the BP pictures | DECIDED (D-01) | PLAN Goal; BP p1; AGENTS.md; DL D-01 | v2 GA elevations laid over the v1 STEP outlines (X and Y match, `conventions.md` §4); renders compared with v1 and the result logged by the PM |
| REQ-LOOK-02 | Overall size W × D × H. H is measured from the room floor to the top of the roof skin (D-21). | 2500 × 1700 × 2400 mm | DECIDED (size D-01, datum D-21) | BP p1; PLAN Goal; DL D-01, D-21 | GA-001 |
| REQ-LOOK-03 | Colours: walls, roof **and decor blocks** in ACP Dark Yellow EV3038 (plan VT01); felt dark gray (plan VT03-PET); smoked gray glass or acrylic. Decor in Dark Yellow is decided (D-12). It matches the plan's material list and v1's product photos, while the v1 CAD renders and the plan's pictures draw the decor black (ISS-031). | as stated | source (walls, felt); DECIDED (decor, D-12) | BP material list and section VI; V1 BOM DL/DR/DT; DL D-12 | Colour codes on the drawings, physical samples |
| REQ-LOOK-04 | Front layout as in v1: one hinged door plus one fixed panel in the same plane. The door is a trapezoid, 1175.6 wide at the bottom and 892.9 at the top, 2011.1 tall, with a slanted leading edge. The fixed panel has 5 sides (box 1014.3 × 2017.1). Material: **smoked acrylic, with laminated glass as the fallback** (D-07), chosen by the most dB per kg; the factory sample decides (ISS-043). | v1 outline | source (outline); DECIDED (material, D-07) | V1 STEP "Door", "Wall Glass"; DL D-07 | FRONT drawing checked against the v1 STEP; factory sample |
| REQ-LOOK-05 | Seams follow the build plan's intent: 2 sheets per side wall and 4 on the back, with crisp, aligned reveals. The faceted front and the overall form are what can't change (ISS-044). | 2 per side wall, 4 at the back | DECIDED (D-23) | DL D-23; BP II–IV | GA elevations |

## B. Priority 1: light

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-LGT-01 | Mass of the installed pod: everything that ships, without the packaging. The working target is about 380 kg, set with the quiet target (REQ-SND-01), and 400 kg is a hard cap. The final stack calculates at about 385 kg (HW). PLAN.md's 300 kg is the light build without the sound package (ISS-063). | ≈ 380 kg target; ≤ 400 kg cap; 300 kg goal | DECIDED (D-02) | DL D-02; PLAN Target 1; HW | CAD and BOM weights, then the prototype on a scale |
| REQ-LGT-02 | Every part weighs 20 kg or less, except the glass, that is, the two front panels (D-07). A "part" is each piece handled on its own during delivery and assembly (definition PROPOSED, ISS-047). | ≤ 20 kg each | DECIDED (number, D-03); PROPOSED (definition) | PLAN Target 1; DL D-03 | Weight per part in the master BOM |
| REQ-LGT-03 | Each front panel (smoked acrylic, or laminated glass as the fallback) has a 2-person handling method in the assembly guide. As an upper bound for planning, 8 mm glass would make the door about 41.6 kg and the fixed panel about 26.9 kg (ISS-023). | method defined | assumption (method); calculation (mass, C5) | PLAN Target 1; V1 STEP; DL D-07 | Assembly guide, timed trial |
| REQ-LGT-04 | Mass per m² of floor: 300 kg over 4.25 m². v1 is about 129, rated pods this size 99–136. | about 70.6 kg/m² | calculation (C6) | PLAN; MS | — |
| REQ-LGT-05 | v1 baseline, for comparison only: PLAN.md now gives about 480 kg from v1's BOM; the product page says 431 kg; the first market study said about 550 kg (ISS-030). | to confirm | source (conflict) | PLAN Target 1; MS | Reconciled v1 weight model, or a v1 on a scale |

## C. Priority 2: easy to assemble

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-ASM-01 | Two people assemble the pod in about 1 hour, never more than 4 hours; the stretch is 1 person-hour (PLAN scorecard). The clock starts with the pallets unwrapped on site and stops with the pod closed, powered and the fans running (start and stop PROPOSED). | about 1 h (2 person-hours), ≤ 4 h; stretch 1 person-hour | confirmed (time); PROPOSED (start and stop) | PLAN Target 2 | Step list with fastener count, then a timed trial on the prototype |
| REQ-ASM-02 | One bolt size on site. | M6 only | confirmed | PLAN Target 2; BP rule 6 | Fastener list from the assembly sequence |
| REQ-ASM-03 | Tool-free connectors wherever they can hold the joint. Where a bolt is needed it is a captive M6 bolt (it stays in its part and can't get lost), and one hand tool fits every one of them. Handling aids (suction lifters, spirit level, knife) don't count as tools (ISS-047, ISS-064). | at most 1 tool | DECIDED (tool-free connectors and captive bolts, D-08); PROPOSED (definition) | PLAN Target 2; DL D-08 | Tool list in the assembly guide |
| REQ-ASM-04 | Joints find their own place: every site joint has a locating feature (hook, pin, rebate or slot) that holds the part before the bolt goes in. No measuring on site. | 100 % of site joints | confirmed | PLAN Target 2 | Joint register, timed trial |
| REQ-ASM-05 | No glue, no welding, no wet work and nothing to stick on site. The felt arrives pre-fitted (REQ-ASM-11). | none on site | confirmed (PLAN); DECIDED (pre-fitted felt, D-08) | PLAN Target 2; DL D-08 | Assembly guide |
| REQ-ASM-06 | Every part fits through a doorway and into a normal lift. PLAN.md Target 2 says a 914 × 2032 mm (36 × 80 in) doorway; its scorecard says an 81 cm door. The check rule uses the narrower door (PROPOSED, ISS-048): sort the part's sizes a ≤ b ≤ c; it passes if a ≤ 810 and b ≤ 2032. | 810 × 2032 mm check | confirmed (PLAN); calculation (C1); PROPOSED (rule) | PLAN Target 2 and scorecard | Check against the part list |
| REQ-ASM-07 | No heavy lifting overhead: every roof part is light enough for two people to place from inside the pod. | ≤ 20 kg per roof part | source | MS "What we learned"; PLAN Target 1 | Assembly sequence |
| REQ-ASM-08 | Every part is labelled with its part number and position code. | 100 % of parts | source | MS "What we learned"; GL §4.2 | Labels in the packing plan |
| REQ-ASM-09 | Assembling it more than once doesn't wear out the joints: no lost fit after repeated take-down and rebuild. | ≥ 5 cycles | assumption (count) | PLAN "Same look, lighter bones" | Joint sample test |
| REQ-ASM-10 | Factory-made subassemblies: each wall and ceiling panel arrives as a complete outer panel (skin, frame, fill, gaskets, captive bolts or connectors, cable pass-throughs) plus its lining cassette (steel tray with the felt on it) as a separate part. The cassette lifts on with no tools. On site the parts are only joined (HW). | 100 % of panels | DECIDED (D-08); source (cassette as a separate part, HW) | DL D-08; HW | Packing list, timed trial |
| REQ-ASM-11 | Pre-fitted felt: the PET felt (plan VT03-PET) is fitted on the lining cassette's face at the factory, not stuck on after assembly as the build plan says (BP-07). Felt and cassette edges at panel joints are detailed so the joint still seals (ISS-064). | 0 felt work on site | DECIDED (D-08) | DL D-08, D-17; BP rule 5 | Panel drawings |
| REQ-MOV-01 | Moving it inside the office: castors, or a quick unbolt of the light panels. | under study | source | PLAN scorecard "Moving it inside the office" | Layout study |

## D. Priority 3: easy to ship

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-SHP-01 | Ships on standard 48 × 40 in LTL pallets, loaded height (pallet included) about 6 ft or less. | 1219 × 1016 mm, ≤ 1829 mm | DECIDED (D-04); calculation (conversion, C1) | PLAN Target 3; DL D-04 | Pallet layout from the CAD |
| REQ-SHP-02 | Long parts (door, fixed panel, side decor blocks) go on **one** standard long pallet, such as 48 × 96 in. The decor blocks are not split. Never a custom size. | 1 long pallet, 1219 × 2438 mm | DECIDED (D-04); calculation (C1) | PLAN Target 3; DL D-04 | Pallet layout |
| REQ-SHP-03 | A panel standing upright on a 48 × 40 pallet can be about 1200 wide and 1700 tall: 1829 minus a pallet deck of about 150 mm leaves about 1680. | ≈ 1200 × 1680 mm | source (PLAN); assumption (deck 150 mm) | PLAN "Design for the pallet" | Measure the real pallet |
| REQ-SHP-04 | Every pallet has a layout with loaded height, weight and freight density in lb/ft³. The LTL class follows from density; state the density, don't guess the class. | per pallet | source | PLAN Milestone 1 | Layout study output |

## E. Guardrails and other requirements

### Fresh air (a full requirement)

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-AIR-01 | CO2 inside, 2 people, all day, door closed, at steady state. | ≤ 800 ppm | confirmed | PLAN Target 4 | Calculation (C2), then a CO2 log on the prototype |
| REQ-AIR-02 | Fresh-air flow at the lowest setting allowed while someone is inside, and the design flow. The design flow gives a full air change about every 2 minutes and CO2 near 550 ppm. | ≥ 26 l/s minimum; 70 l/s design | DECIDED (70 l/s, D-09); calculation (C2, C3) | PLAN Target 4; DL D-09 | Fan curve against system pressure, then a flow check |
| REQ-AIR-03 | Fans start by themselves when someone is inside, and CO2 drives their speed, with boost. The CO2 reading is shown inside. Control and readings come from Autonomous's in-house **Desk Pro AI sensor hub** (CO2, presence, air quality, sound level), see REQ-ELE-02. | self-starting, CO2-driven, reading shown | DECIDED (D-09) | PLAN Target 4; DL D-09; PO-1031 | Control scheme, prototype check |
| REQ-AIR-04 | Fans run on the 12 V DC bus (REQ-ELE-01) and are wired in: no plug, and no user control drops the flow below the REQ-AIR-02 minimum while someone is inside (reading PROPOSED, ISS-038). | wired in | DECIDED (12 V, D-10); PROPOSED (reading) | PLAN Target 4; DL D-10 | Wiring diagram |
| REQ-AIR-05 | Fan noise inside **at full flow**, through silenced vents, published. Measured at seated ear height in the middle of the pod with the door closed (point PROPOSED). | ≤ 25 dB(A) at full flow | DECIDED (D-09); assumption (method) | PLAN Target 4 (on main); DL D-09 | Noise estimate, then a measurement on the prototype |
| REQ-AIR-06 | Low-heat lights: one dimmable LED ceiling light plus a soft front face light for video calls, all on 12 V (D-20). Total lighting power budget so the pod stays within about 3 K of the room at the design flow (C4). | ≤ 30 W | DECIDED (lights, D-20); PROPOSED (30 W budget, assumption) | DL D-20; PLAN Target 4; MS | Fitting data |
| REQ-AIR-07 | The air path is in the roof: one fan blows in, one blows out (BP-09), with a free-area slot pattern below each (ISS-010) and clear space above the roof (ISS-049). | 1 in, 1 out | source | BP rule 7, section V | Air design |

### Electrical and in-house modules

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-ELE-01 | A **12 V DC bus** feeds the fans, lights, sensors and the voice kit. Mains (220 V for the prototype) goes **only to the user outlets** (the socket in plan VT07). One power supply turns mains into 12 V. With every load on 12 V, a later 120 V US version only changes the mains side: inlet, outlets and the supply's input. | 12 V DC; mains to outlets only | DECIDED (D-10) | DL D-10; PO-1031 | Wiring diagram, load table |
| REQ-ELE-02 | Reuse Autonomous's in-house modules. The **Desk Pro AI sensor hub** (CO2, presence, air quality, sound level) runs the air control and gives the readings. The **Lamp electronics** (mic array, speakers, computer) are the base of the later voice cockpit. Their supply, size, mounting and data details come from internal documents, still to collect (ISS-060). | 2 modules | DECIDED (reuse, D-09, D-11); unverified (module data) | DL D-09, D-11; PO-1031 | Module datasheets on file |
| REQ-ELE-03 | DC load budget, to size the 12 V supply: voice cockpit 60 W (12 V × 5 A, REQ-VCK-04) + lights ≤ 30 W (REQ-AIR-06) + 2 fans about 15 W each + sensor hub about 5 W, giving about 125 W. A supply of at least 150 W keeps a margin. | ≈ 125 W load; ≥ 150 W supply | calculation (C8); assumption (fan and hub watts) | DL D-10, D-11; PO-1031 | Load table with real fan and hub data |
| REQ-ELE-04 | The sensor hub reads the occupied zone: CO2 at breathing height, presence with a view of the seat, sound level inside. Keep it out of the supply-air jet and away from the exhaust grille. | placement rule | PROPOSED (assumption) | PO-1031 | Placement on the ELECTRICAL drawing, prototype readings |

### Build of the walls, ceiling, floor and door

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-BLD-01 | Wall build, from outside: ACP 3 mm; aluminium 20 × 40 frame at 400 mm centres with 40 mm PET fill; a floating lining cassette made of a 0.5 mm galvanised steel tray with 25 mm returns, a 25 mm air gap and 9 mm PET felt on its face. The outer panel and the cassette ship as separate parts. | 81 mm; 13.1 kg/m² | DECIDED (D-16, D-17); calculation (HW) | DL D-16, D-17; HW | Wall section on the WALL drawing; part weights |
| REQ-BLD-02 | Ceiling build: the same stack on a 20 × 100 × 1.5 aluminium frame with 100 mm of fill. Part of each half holds the lined U-channel silencer. | 141 mm; 17.4 kg/m² | DECIDED (D-16); calculation (HW) | DL D-16; HW | Ceiling section |
| REQ-BLD-03 | No plywood behind the ACP anywhere; plan VT02 is dropped. | no plywood | DECIDED (D-17) | DL D-17 | BOM |
| REQ-BLD-04 | Thin floor inside the aluminium base band, with a 20 mm threshold at the door (build in open-questions Q4). | 20 mm threshold | DECIDED (D-18) | DL D-18 | BASE drawing |
| REQ-BLD-05 | Door left-hinged, as in v1, with the hinge pocket in the left decor block DL. | left-hinged | DECIDED (D-19) | DL D-19 | FRONT drawing |
| REQ-BLD-06 | Inside size with the final stack: about 3 cm narrower and shallower than v1 (2372 × 1480) and 2 cm taller (2223). | ≈ 2338 × 1460 × 2241 mm | calculation (HW) | HW; V1 BOM summary | GA-001 |

### Quiet (guardrail)

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-SND-01 | Speech level reduction D_S,A to ISO 23351-1 of **about 24 dB (Class C)**, with the lightest wall that reaches it. The final stack with a 10 mm smoked acrylic front calculates at 24.2 dB (range 21.7–26.7, HW). The factory sample decides the real figure. For comparison, the calculation gives v1 about 15 dB as built, against its 30 dB claim (ISS-065). | ≈ 24 dB (Class C) | DECIDED (D-02); calculation (HW) | DL D-02; HW; PLAN Target 5; MS | Calculation, factory sample, then the lab test with v1 in the same lab |
| REQ-SND-02 | Seals before mass: a gasket on every panel joint, a drop seal on the door, fill in the cavities, glass seated in sealed profiles, and a seal under the thin floor. | all 5 present | confirmed | PLAN "Quiet without the weight" | Joint register, sound check |
| REQ-SND-03 | If the quiet target needs more mass, add only what it needs, show the kg per dB, and never pass the 400 kg cap. | ≤ 400 kg | DECIDED (D-02) | DL D-02; PLAN Risk 3 | Sound check report |

### Materials, later US rules, and doing it right

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-MAT-01 | Low-emission certified felt, boards and glue from the prototype on. The certificate type is chosen in the hardware selection; examples to check are CARB Phase 2 or TSCA Title VI for wood panels and GREENGUARD Gold for felt and adhesives. | certificate for each | confirmed (need); unverified (certificate names) | PLAN Target 6; MS | Supplier certificates |
| REQ-US-01 | Keep it possible: the roof can take a sprinkler head or open on an alarm (ISS-052). | zone reserved | confirmed | PLAN "Later" | Ceiling drawing |
| REQ-US-02 | Keep it possible: a low threshold. The threshold is 20 mm (D-18); US rules (later) allow about 13 mm (ISS-053). | 20 mm | DECIDED (20 mm, D-18); unverified (13 mm) | DL D-18; PLAN "Later" | Threshold detail |
| REQ-US-03 | Keep it possible: a wide door. The v1 door leaf is 1175.6 wide at the bottom; the clear width with the door open at 90° goes on the GA. | ≥ v1 | confirmed | PLAN "Later"; V1 STEP | GA-001 |
| REQ-US-04 | Keep it possible: a light door pull. The limit is set by the hardware selection; US rules (later) use about 22 N (5 lbf) for interior doors. | ≤ 22 N (to confirm) | confirmed (intent); unverified (number) | PLAN "Later" | Pull test on the prototype |
| REQ-DOC-01 | Built to the guideline: native Fusion CAD with editable sketches and parameters; drawings in the order GA, then assemblies, then parts; one master BOM; joint and feature registers; a status on every number; a Reviewer runs the §13 checklist on every pull request. | all | confirmed | PLAN Target 7; GL | Reviewer checklist |
| REQ-DOC-02 | Agents never order parts, contact suppliers or release anything for production. | — | confirmed | PLAN "How we build it"; AGENTS.md | — |
| REQ-DOC-03 | The repo is public: no supplier quotes, margins or personal data. | — | confirmed | AGENTS.md | Review |
| REQ-DOC-04 | Units in files: drawings and DXF in mm; STEP files may stay in cm when the file declares it. Check the unit and a known size after every import or export (ISS-066). | mm (drawings, DXF) | DECIDED (D-13) | DL D-13; GL §3.1 | Round-trip check in the CAD reports |

## F. Hooks for a later voice cockpit kit

The kit is **not** designed in v2. It will be built on the in-house Lamp electronics (mic array, speakers, computer), plus a screen and a status light. We only reserve what it needs, so it can be added later without cutting or rebuilding panels (ISS-051).

| ID | Requirement | Target | Status | Source | How we prove it |
|---|---|---|---|---|---|
| REQ-VCK-01 | Reserve hidden mounting points for the Lamp electronics (mic array, speakers, computer), a screen and a status light. They stay invisible from outside when no kit is fitted. | mounts for 5 items | DECIDED (D-11) | DL D-11; PO-1031 | WALL, CEILING and ELECTRICAL drawings |
| REQ-VCK-02 | Zones: screen and speakers on the inside of the back wall's middle band, at seated eye height (about 1000–1400 mm above the floor); the computer behind a cover in the same band; mic array and status light at the inside front edge of the ceiling or the top decor block (DT), facing the user. | as stated | PROPOSED (assumption: heights and places) | PO-1031 | Interfaces IF-15, IF-16 |
| REQ-VCK-03 | Cable path: a reserved route with a draw wire from the electrical zone in the back wall to each zone. It runs in the 25 mm gap inside the lining cassettes and through the ceiling's 100 mm zone, so nothing is cut on site later (HW). | 1 route per zone | DECIDED (path, D-11); PROPOSED (route) | DL D-11; HW; PO-1031 | Route drawing |
| REQ-VCK-04 | Power: a reserved, fused 12 V DC outlet from the DC bus for the kit. It is counted in the load budget (REQ-ELE-03) and the heat budget (about +0.7 K at 70 l/s, C4). | 12 V, 5 A (60 W) | DECIDED (D-11) | DL D-11; PO-1031 | ELECTRICAL drawing, load and heat check |
| REQ-VCK-05 | Data: a reserved data link to the kit zone: Ethernet from the network socket (plan VT09), plus a spare data cable in the cable path. The cable type is set with the Lamp electronics. | 1 data link | DECIDED (link, D-11); PROPOSED (type) | DL D-11; PO-1031; BP VT09 | Route drawing |
| REQ-VCK-06 | The kit fixes with M6 into factory-fitted inserts on the lining cassette, never through the ACP skin: a hole through the outer leaf is a new sound leak (HW). | M6 | PROPOSED | PO-1031; PLAN Target 2; HW | Joint register |

## G. Every constraint in the v2 build plan

All lines come from `v2/00-Control/v2-build-plan.pdf`, translated. The last column says what v2 does with each. Changes are either DECIDED (`decision-log.md`) or PROPOSED, and every one is logged as an issue.

| ID | Build plan constraint | Value | Status | Source | v2 disposition |
|---|---|---|---|---|---|
| BP-01 | Overall size | 2500 W × 1700 D × 2400 H mm | source | BP p1 "Overral" | Kept (REQ-LOOK-02). The plan's own picture shows 2405 (ISS-013). |
| BP-02 | Goals: 1 light pod; 2 easy assembly by 2 people; 3 "cách ấm tốt", read as good sound insulation (ISS-008); 4 good ventilation; 5 easy to pack and ship | — | source | BP p1 "Goal" | Kept. Numbers come from PLAN (ISS-009). |
| BP-03 | Rule 1: build each part from 2D sketches | — | source | BP p1 Rule 1 | Kept (GL §4.4) |
| BP-04 | Rule 2: model parts as components, never as bare bodies | — | source | BP p1 Rule 2 | Kept |
| BP-05 | Rule 3: modelling order: floor frame, left wall, right wall, back wall, ceiling, decor frame (black), floor boards | — | source | BP p1 Rule 3 | Kept. With the thin floor (D-05) the first step is BASE. |
| BP-06 | Rule 4: wall-to-wall joint, per the p2 section. Layers from outside: VT01 3, VT02 6, VT10 20, VT03 9 mm. The ceiling or back wall sits between the side walls with a 1 mm gap; the side walls' outer layers cover its edge; bolts join the frames. | 3 / 6 / 20 / 9 mm; 1 mm gap | source (picture dimensions) | BP p2 Rule 4 | Replaced by the final stack (REQ-BLD-01; D-16, D-17): ACP 3, 20 × 40 aluminium with 40 mm PET, floating steel-and-felt cassette, 81 mm. Seals added (ISS-003); bolt anchor open (ISS-011). |
| BP-07 | Rule 5: VT01 glued to VT02; VT02 screwed to the VT10 frame with steel screws; VT03 fixed with hook-and-loop last, after the pod is built | — | source | BP p2 Rule 5 | Changed: no plywood (D-17); the felt is pre-fitted on the lining cassette at the factory (D-08). ISS-015, ISS-016. |
| BP-08 | Rule 6: walls bolted to the floor frame with M6 | M6 | source | BP p2 Rule 6 | Changed: walls fix with captive M6 bolts or tool-free connectors to the thin floor's base rail (thin floor DECIDED D-05; rail PROPOSED, open-questions Q4) |
| BP-09 | Rule 7: ventilation fans in the ceiling, one blowing in and one blowing out | 2 fans | source | BP p2 Rule 7 | Kept (REQ-AIR-07) |
| BP-10 | Rule 8: VT07, VT08 and VT09 mounted on the back wall | — | source | BP p2 Rule 8 | Kept. VT08's role changes (ISS-038). |
| BP-11 | VT01: aluminium composite panel, Dark Yellow (EV3038) | 3 mm | source | BP p2 | Kept; spec gaps (ISS-035) |
| BP-12 | VT02: plywood | 6 mm | source | BP p2 | Dropped: no plywood behind the ACP (D-17) |
| BP-13 | VT03: polyester fibre acoustic panel, dark gray (seller link in the plan) | 9 mm | source | BP p2 | Kept: 9 mm felt on the lining cassette's face (D-17); spec gaps (ISS-035) |
| BP-14 | VT03 (second use of the code): steel box tube | 50 × 100 mm | source | BP p3 | Dropped: thin floor (D-05). Code clash ISS-007. |
| BP-15 | VT04: steel box tube | 30 × 60 mm | source | BP p3 | Dropped: thin floor (D-05) |
| BP-16 | VT05: steel plate | 3 mm | source | BP p3 | Use unknown (ISS-037) |
| BP-17 | VT06: ventilation fan Panasonic FV-15AUL1 (seller link in the plan) | — | source | BP p3 | A mains fan clashes with the 12 V DC bus (REQ-ELE-01); a 12 V DC fan is needed, checked against REQ-AIR (ISS-039) |
| BP-18 | VT07: UTEN S300 one-way switch and 5-pin socket | — | source | BP p3 | Socket kept for the 220 V prototype, and it is the only mains point inside (REQ-ELE-01). What the switch switches is open (ISS-061). |
| BP-19 | VT08: UTEN S300 fan speed controller ("triết áp") | — | source | BP p3 | A mains knob can't drive 12 V DC fans; the sensor hub controls the fans and any manual trim is a 12 V input (ISS-038) |
| BP-20 | VT09: UTEN S300 single network socket | — | source | BP p3 | Kept; also feeds the voice cockpit data path (REQ-VCK-05) |
| BP-21 | VT10: steel box tube | 20 × 20 mm | source | BP p3 | Aluminium: 20 × 40 at 400 mm for the walls, 20 × 100 for the ceiling (D-16); alloy and wall thickness open (ISS-034) |
| BP-22 | VT11: bolt | M6 × 60 | source | BP p3 | Kept as the one bolt size; spec open (ISS-036) |
| BP-23 | VT12: leveling foot (seller link in the plan) | M10 | source | BP p3 | Dropped: thin floor (D-05) |
| BP-24 | Section I, floor frame: outer frame of 50×100 tube (VT03), 2 joists of 30×60 tube (VT04), outline per the top view, 6 M10 leveling feet (VT12) spaced evenly along the middle of the 50×100 tubes | 6 feet | source | BP p3 section I | Replaced by the thin floor (DECIDED, D-05) |
| BP-25 | Section II, left wall: build from outside VT01, VT02, VT10, VT03; split into 2 frames joined with M6×60; depth 1500, with the other 200 for the decor; its ACP covers the edges of the ceiling and back wall frames; only 2 ACP sheets show outside | 1500 + 200 | source | BP p4 section II | Kept: 2 sheets per side wall with aligned reveals (D-23). Depth chain open (ISS-012); panel height (ISS-050). |
| BP-26 | Section III, right wall: same as the left wall; only 2 ACP sheets show outside | — | source | BP p4 section III | Kept, as BP-25 (D-23) |
| BP-27 | Section IV, back wall: same build; 4 frames joined with M6×60; 4 ACP sheets show outside | 4 frames | source | BP p4 section IV | Kept: 4 sheets on the back with aligned reveals (D-23) |
| BP-28 | Section V, ceiling: same build (the text says "back wall", ISS-032); 2 frames joined with M6×60; a fan on each half with a slot pattern below it | 2 frames | source | BP p4 section V | Kept, on a 20 × 100 aluminium frame (D-16), 141 mm thick; slot pattern open (ISS-010) |
| BP-29 | Section VI, decor frame: VT10 core frame inside, VT01 skin outside, the ACP grooved and folded to the faceted shape; 3 blocks (left, right, top), 200 deep, joined to the walls with V brackets and steel screws | 200 deep | source | BP p4–p5 section VI | Kept. ISS-014, ISS-031, ISS-045, ISS-059. |
| BP-30 | Section VII, floor boards: 2 boards laid on the floor frame, screwed to its 2 joists | 2 boards | source | BP p5 section VII | Replaced by the thin floor panels (DECIDED, D-05) |

## H. Calculations

Each line names its inputs and their status. The layout study (`v2/05-Engineering/layout-study/`) and the sound and air check (`v2/05-Engineering/acoustics-air/`) replace these first estimates with their own scripts.

- **C1 Conversions (calculation).** 1 in = 25.4 mm exactly. 48 × 40 in = 1219.2 × 1016.0 mm. 48 × 96 in = 1219.2 × 2438.4 mm. 6 ft = 1828.8 mm. 36 × 80 in = 914.4 × 2032.0 mm. Rounded to whole mm in the tables.
- **C2 CO2 at steady state (calculation).** Rise above the supply air: ΔC = n·G / Q. Inputs: n = 2 people; G = 0.0052 l/s of CO2 per seated adult (assumption, a typical value); supply air at 400 ppm (assumption: the room is near outdoor level). For CO2 ≤ 800 ppm, ΔC ≤ 400 ppm, so Q ≥ 2 × 0.0052 / 0.000400 = **26 l/s**. At Q = 70 l/s, ΔC = 0.0104 / 70 = 149 ppm, so CO2 ≈ **549 ppm**. Office air is often above 400 ppm; the pod then sits higher by the same amount.
- **C3 Air change (calculation).** Inside with the final stack about 2338 × 1460 × 2241 mm (HW) = 7.65 m³; v1 was 2372 × 1480 × 2223 mm = 7.80 m³ (V1 BOM summary). At 70 l/s: 7.65 / 0.070 = 109 s, so **about 2 minutes**.
- **C4 Heat (calculation).** Temperature rise ΔT = P / (ρ · c_p · Q), with ρ = 1.2 kg/m³ and c_p = 1005 J/(kg·K) (air at about 20 °C, source: standard values). Heat inputs, all assumptions: 2 seated people at 75 W sensible each, 2 laptops at 30 W each, lights 30 W, so P = 240 W. At 70 l/s: ΔT = 240 / (1.2 × 1005 × 0.070) = **2.8 K**. At 26 l/s: **7.7 K**. The voice cockpit reserve (60 W) adds 0.7 K at 70 l/s. So the 70 l/s aim, more than the CO2 minimum, is what keeps the pod cool, which matters because heat is the users' top complaint (MS).
- **C5 Glass mass (calculation).** Door area 2.080 m² and fixed glass area 1.344 m², from the v1 STEP outlines (polygon area). Glass density 2500 kg/m³ (assumption: typical soda-lime glass), so 25 kg/m² at 10 mm and 20 kg/m² at 8 mm. Door: 52.0 kg at 10 mm, **41.6 kg at 8 mm**. Fixed glass: 33.6 kg at 10 mm, **26.9 kg at 8 mm**. Both: 85.6 kg at 10 mm, 68.5 kg at 8 mm, so 8 mm saves 17.1 kg. The v1 BOM's rectangles (3.91 m²) overstate the area by 14 % (ISS-023). By decision D-07 the front is smoked acrylic, or laminated glass as the fallback; their masses follow from the thickness the sound check picks.
- **C6 Mass per floor area (calculation).** Footprint 2.5 × 1.7 = 4.25 m². 300 / 4.25 = **70.6 kg/m²**. v1: 550 / 4.25 = 129 kg/m² (MS).
- **C7 Step into the pod (calculation).** v1 floor top at Z(v1) = 115 mm (V1 STEP), plus 15 mm of feet, gives about 130 mm above the room floor. Thin floor (D-05; build PROPOSED in open-questions Q4): about 20 mm.
- **C8 12 V DC load (calculation).** Voice cockpit 12 V × 5 A = 60 W (DECIDED, D-11). Lights ≤ 30 W (REQ-AIR-06, assumption). 2 fans at about 15 W each = 30 W (assumption until the air design picks the fans). Sensor hub about 5 W (assumption until its datasheet arrives, ISS-060). Total about 125 W, which is about 10.4 A at 12 V. A supply rated at 150 W or more (12.5 A) leaves about 20 % margin. Every load is also heat inside the pod (C4).
