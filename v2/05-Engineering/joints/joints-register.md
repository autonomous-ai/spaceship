# Joints register: Spaceship (FocusPod v2), Milestone 2 sample set

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-01 (PROPOSED code; the control pack adds the register row) | P01 | DRAFT | 2026-10-31 | Joints Engineer (v2 Milestone 2) |

This is the joint register the guideline asks for (§8, and Milestone 2 item 6), for the site joints of the sample set: wall to wall, wall to floor (base band), wall to ceiling, back corner, decor to wall, and the lining cassette clips. It also gives the feature-rationale inputs (§7) the Fusion Engineer needs: which holes and slots each joint puts in which part, and why (section 8).

- **Status of numbers** (conventions §9): confirmed, source, calculation, assumption, unverified. Every number below carries one.
- **Status of choices:** DECIDED only where a decision-log row (D-nn) is cited. Every other choice in this file is **PROPOSED**: the work goes ahead on it until the PM rules (`AGENTS.md`). Section 7 lists the choices the PM should rule on.
- **HOLD:** a part or number that waits for data or a test. CAD may reserve a space for it, marked UNVERIFIED, but doesn't use its hole pattern until it's released (guideline §4.3 step 4; D-56). Section 6 lists every HOLD with its question.
- **Not covered here:** the ACP-to-frame bond is in [`bond-spec-acp-aluminium.md`](bond-spec-acp-aluminium.md). Door hinges, the fixed glass and the decor top block's joint to the ceiling (IF-08, IF-09) belong to the FRONT work. The base band's own corner keys and the thin floor belong to the BASE work.
- No supplier was contacted and nothing was ordered. Data comes from the files below and from public pages, each linked with the date read.

## Result

1. **One bolt for every site joint: M6 × 20, ISO 4762 socket head, class 8.8, zinc plated, captive in its panel, driven with one 5 mm hex key.** Only if the decor block's back plate can't take a rivnut does the decor joint need M6 × 25 (section 3.5). Every bolt threads into a Sherex CAH3-610-4.2 rivnut, the rivnut the hardware selection picked for the 1.2 mm tube wall. **76 site bolts** in the six joint families here (section 3.7). Status: PROPOSED; the lengths are calculations (section 2.2).
2. **Every site bolt lives inside an edge tube of one of the two parts it joins, and is reached from inside the pod** through a small pocket left free of fill, before the lining cassettes go on (they go on last, layout study §5 step 11). Reason: the decided stack leaves only a 4 mm gap between frame and lining, and the cassettes butt at every seam, so there's no room for a bracket, latch or bolt head on the room side of the frame (finding F1).
3. **Findings that change the frame or need the PM:**
   - **F1. No room-side hardware.** Frame-to-cassette gap 4 mm (skeleton `lin_gap`, assumption; stack 43 + 4 + 34 = 81, D-16, D-42). An ISO 4762 M6 head alone is 6 mm tall (source). So every fastener sits inside the 40 mm frame depth (section 2.2).
   - **F2. The 90° frame joints overlap only 17 mm.** At the back corners and at the wall-to-ceiling edges, one panel's edge tube meets the side of the other panel's edge tube over 17 mm (calculation from the skeleton envelopes, section 2.4). That is too narrow for the rivnut and the bolt's access hole. **Fix (PROPOSED): the edge member of the panel whose skin covers the corner becomes 40 × 40 × 1.2** (side panels' back members, upper side panels' top members, ceiling halves' back members). The overlap grows to 37 mm. Cost: **+1.29 kg** on the pod (calculation); a 30 × 40 × 1.2 member would do it for +0.65 kg if the extruder lists one.
   - **F3. Seams need clamping force, so they get captive bolts, not tool-free clips.** A gasket only seals when it's squeezed: 0.41 N per mm of seam for the picked PORON strip at 25%, 164 N per 400 mm (calculation, section 2.5). A panel's own weight gives about a sixth of that, and no catalogue latch fits the 4 mm gap. The layout study counted tool-free connectors on the seams and corners (D-08: "tool-free wherever they can hold"); here they become captive bolts. **That costs about 12 minutes of assembly** (the layout study's own figure for that change: 125 → about 137 min, calculation). The PM should rule (section 7, item 1).
   - **F4. The ACP bond doesn't fit the 20 mm tube face as the adhesive maker lays it out.** See the bond spec, finding B1.
   - **F5. The skeleton leaves a gap under the ceiling's back edge.** The back wall stops at Z 2319 (`back_h` = `wall_h` − `stack_t`), while the ceiling's outer panel starts at Z 2357. Over Y +769 to +850 that leaves an 81 × 38 mm void along the whole back-top edge, which the back lining doesn't close either (it also stops at Z 2319). The back wall's outer panels must reach the ceiling frame (Z 2357), or a closer must fill the void. Calculation from `pod_skeleton.py` P03, lines 134–149. For the Fusion Engineer (section 7, item 4).
   - **F6. Two head types are in the files.** The hardware selection names ISO 4017 hex bolts (10 mm across flats); the layout study's assembly time uses one 5 mm hex key, which means socket heads (ISO 4762). This register uses ISO 4762: the Ø10 head fits inside a 20 × 40 tube, and the key enters through an 11 mm hole (section 7, item 2).
4. **HOLDs: 11** (section 6). The most important: the rivnut's torque, pull-out and spin-out in the real tube (D-48, ISS-011); the cassette clip and ceiling catch (D-56, ISS-076); the captive retainer part; the base band's section; the rivnut flange thickness, which sets the gasket squeeze.

## 1. Sources

| Key | File or page | Used for |
|---|---|---|
| GL | `docs/engineering-guideline.md` §6.3, §7, §8, §8.1, §8.2, §10 | Register fields, bolt and bond rules, test status |
| DL | `v2/00-Control/decision-log.md`, D-01 to D-59 | Decided stack, clips, holds |
| REQ | `v2/00-Control/requirements.md` | REQ-ASM-02 to -11, REQ-BLD-01, -02 |
| IF | `v2/00-Control/assembly-tree.md` §4 | IF-01, IF-03 to IF-07, IF-10 |
| ISS | `v2/00-Control/issue-register.csv` | ISS-003, -011, -014, -015, -016, -034, -036, -045, -054, -064, -076, -079 |
| SEL | `v2/05-Engineering/hardware/selection.md` | Rivnut A5, bracket A7, clips A8, gaskets and base seal D, sample tests |
| HW | `v2/05-Engineering/acoustics-air/report.md` §1, §8, §10 | Stack layers, gasket in the 3–4 mm gap, cassette mass, clip risk |
| LAY | `v2/05-Engineering/layout-study/report.md` §4, §5 | Assembly order, one 5 mm key, bolt and clip counts, base band and glides |
| SKL | `v2/01-CAD-Native/skeleton/` P03: `100000_P03_POD-SKELETON-PARAMETERS.csv`, `pod_skeleton.py`, `BUILD-RECORD.md` | Envelopes and positions of every panel, cassette and band piece |
| ISO4762 | ISO 4762 M6 table, via [Engineers Edge](https://engineersedge.com/iso_socket_head_screw.htm) and a [Würth ISO 4762 8.8 listing](https://eshop.wuerth-industrie.com/Hexagon-Socket-Head-Cap-Screw-SCR-CYL-ISO4762-88-IH5-A2K-M6X6/00846%20%206.sku/en/US/EUR/), read 2026-10-31 | Head Ø10 max, head height 6 max, socket 5 |
| ISO898 | ISO 898-1 class 8.8 values via [Engineering ToolBox](https://www.engineeringtoolbox.com/metric-bolts-minimum-ultimate-tensile-proof-loads-d_2026.html), read 2026-10-31 | M6 stress area 20.1 mm², proof load 11.6 kN, minimum ultimate 16.1 kN |

## 2. Rules every site joint follows

### 2.1 Hardware set

| ID | Item | Data | Status |
|---|---|---|---|
| H-01 | **Bolt.** M6 × 20, ISO 4762, class 8.8, zinc plated (M6 × 25 only for J-FRONT-01's fallback). Maker and SKU from the master BOM. | Head Ø10, head height 6, 5 mm hex socket (ISO4762). Stress area 20.1 mm², proof load 11.6 kN, minimum ultimate 16.1 kN (ISO898). | PROPOSED (head type: section 7 item 2); data source |
| H-02 | **Captive retainer.** Holds each bolt in its tube, tip flush with the joint face while the parts are brought together, and lets it run forward into the rivnut. | Part and push-off force not chosen | **HOLD-02** |
| H-03 | **Rivnut.** Sherex CAH3-610-4.2, aluminium 5056, large flange, thin-wall series | M6 × 1.0; grip 0.70–4.20 (covers the 1.2 mm wall); hole Ø9.53 +0.10; length 14.86; flange Ø12.96 (SEL A5) | source; torque **HOLD-01** (D-48); flange thickness and thread position **HOLD-03**; edge distance in a 20 mm face **HOLD-04** |
| H-04 | **Joint gasket.** Rogers PORON 4701-40 Soft, 3.18 mm, with pressure-sensitive adhesive laminated by a converter, 10 mm wide strips | 41 kPa at 25% compression; compression set ≤ 5% at 23 °C (ASTM D3574 D) (SEL D) | source; converter and strip **HOLD-05** (SEL) |
| H-05 | **Locating spigot.** Ø8 stainless pin with an M6 thread, screwed into an H-03 rivnut at the factory with threadlocker. A part we make; number from the master BOM. | Ø8, stands 8 proud | PROPOSED (assumption sizes) |
| H-06 | **Base seal.** Closes the gap under the base band to the room floor | Gap 10 nominal (`glide_h`, assumption) ± 5 for the floor (ISS-054, assumption) | **HOLD-06**: none of SEL D's base seals is shown to cover 5–15 mm |
| H-07 | **One tool.** A 5 mm hex key with a ball end, or a 5 mm hex bit in a short driver (LAY §4: one 5 mm key; the base band's glides adjust with the same key) | — | PROPOSED; meets REQ-ASM-03 |

The bolt is the only site fastener. Every rivnut, spigot, gasket and retainer is fitted in the factory (D-08, REQ-ASM-10).

### 2.2 The in-member bolt: how every site bolt is placed

Each joint has a **nut side** (the part with the rivnut) and a **bolt side** (the part whose edge tube holds the captive bolt). The bolt side is the part whose frame bay the person inside the pod can reach; each joint entry says which is which.

1. The nut side has an H-03 rivnut set in the tube wall that faces the joint.
2. The bolt side's edge tube has, on the same axis: a Ø6.6 clearance hole in its joint-side wall, and a Ø11 access hole in the opposite wall, which faces into its own frame bay.
3. The factory pushes the M6 bolt in through the Ø11 hole, tip first, and fits the H-02 retainer. The Ø10 head passes the Ø11 hole. The bolt sits back with its tip flush with the joint face while the parts are brought together.
4. On site, the 5 mm key reaches through the bay (through its fill pocket, section 2.3) and the Ø11 hole into the bolt's socket. The bolt runs into the rivnut, and its head seats on the inside of the joint-side wall.

**Why:** F1 (no room on the room side), REQ-ASM-03 (one tool, captive bolts), REQ-ASM-04 (the part is located before the bolt goes in), and access from inside before the cassettes go on (LAY §5).

**Stack check for M6 × 20** (calculation; tube wall 1.2 per D-34 and D-54, gasket 3.18 per SEL D):

| Step | Value | Status |
|---|---|---|
| Joint-side wall of the bolt-side tube | 1.2 | confirmed (D-54) |
| Gap at the joint: the rivnut flange is the metal stop, with the gasket around it | t_f (flange thickness, HOLD-03; 1.0–1.6 expected) | unverified range |
| Bolt beyond the bolt-side wall's outer face: 20 − 1.2 | 18.8 | calculation |
| Rivnut far end from that face: t_f + 14.86 | 15.9–16.5 | calculation |
| Bolt runs past the rivnut's far end (full thread engaged) | 2.3–2.9 | calculation |
| Tip inside a nut-side tube that is 20 deep along the bolt (its far inner face is 1.2 + 17.6 = 18.8 from its outer face): clearance 18.8 − (18.8 − t_f) = t_f | 1.0–1.6; at least 0.6 with the bolt's length tolerance (js15, ±0.42 at 20; unverified) | calculation |
| Tip inside a nut-side tube 40 deep, the base band, a decor block or a 40 × 40 member | 20 or more | calculation |
| Head inside a bolt-side tube 20 deep: head height 6 in an inner width of 17.6 leaves 11.6 for the key to enter | 11.6 | calculation |

So M6 × 20 works in every joint here; the 20-deep nut-side tubes are the tight case (at least 0.6 mm at the tip). HOLD-03 asks Sherex for the flange thickness and where the thread starts, which closes this check.

**The rivnut flange sets the gasket squeeze.** When the bolt is tight, the bolt-side tube bears on the rivnut flange, metal to metal, so the gasket's squeeze is (3.18 − t_f) / 3.18: for a flange 1.0–1.6 thick, 50–69%. That's more than the 25% the stiffness figure is quoted at, so the gasket thickness is picked once HOLD-03 gives t_f, with a **target of 25–50% squeeze** (assumption; PORON's compression-set figure is quoted at 50%, ASTM D3574 D). If the flange is thinner than 1.6 mm, the next PORON thickness is used (4.76 mm is in the listed 3.18–12.70 range, SEL D; stock unverified). The gasket strip has a Ø14 hole at each rivnut (assumption: flange Ø12.96 + 1).

### 2.3 Access pockets

In the wall panels, next to each site bolt, the factory leaves the 40 mm PET fill out of a pocket **60 × 60 mm** (assumption: room for a hand-held key at the 11 mm hole) in the bolt side's bay. The cassette covers it later. The ceiling halves need no pockets: their fill rides on the ceiling cassette (D-24), so their bays are empty until the cassettes go on. 76 pockets of 0.0036 m² at most is 0.27 m², under 2% of the roughly 15.8 m² of wall and ceiling panels (calculation; panel sizes from SKL). The effect on sound isn't modelled; the wall sample is built with pockets (test T-06).

### 2.4 Edge members at the 90° joints

From the skeleton envelopes (SKL P03: `outer_t` 43 = ACP 3 + frame 40; frame tubes 20 × 40 with the 40 through the wall; D-55: the back wall and ceiling frames span between the side frames at X ±1207, and the side skins cover their edges):

| Joint | Edge member of the panel whose skin covers the corner | The other panel's edge tube | Overlap of the faces that touch | Status |
|---|---|---|---|---|
| Back corner (J-WALL-02) | Side panel's back member: Y +830 to +850 (20 wide), X −1247 to −1207 | Back panel's outer member: X −1207 to −1187, Y +807 to +847 (40 deep) | Y +830 to +847 = **17** | calculation |
| Side wall to ceiling (J-CEIL-01) | Upper side panel's top member: Z 2380 to 2400 | Ceiling's side member: Z 2357 to 2397 | Z 2380 to 2397 = **17** | calculation |
| Back wall to ceiling (J-CEIL-01, once F5 makes the back wall reach Z 2357) | Ceiling's back member: Y +830 to +850 | Back panel's top member: Y +807 to +847 | Y +830 to +847 = **17** | calculation |

With 17 mm, the bolt has to sit at the overlap's middle (Y +838.5 at the back corner). The rivnut hole (Ø9.53) is then 3.7 mm from the side of the side member's 20 mm face, and the Ø11 access hole in the other tube comes within 1.8 mm of the inside of that tube's back wall (inner face at Y +845.8). Both are tube corners (rule R2 in section 8 asks for 10 mm). **With a 40 × 40 × 1.2 member** (Y +810 to +850) the overlap is 37 mm and the bolt sits at Y +828: the rivnut hole is 13 mm from the nearest side of the 40 mm face, and the access hole 12 mm from the other tube's back wall (calculation). The member weighs 0.503 kg/m against 0.373 (calculation, aluminium at 2.70 g/cm³ as in SEL A4). Lengths: 4 side back members × 1145, 2 upper side top members × 1495, 2 ceiling back members × 1207: **+1.29 kg** (calculation).

### 2.5 Seals

Every site joint carries one H-04 gasket strip, 10 mm wide, on the nut-side face (ISS-003 asks every joint to name its seal). Line load at 25% squeeze: 41 kPa × 10 mm = **0.41 N/mm** (calculation from SEL D). With one bolt every 400 mm the seam needs 164 N per bolt; at 452 mm, 185 N (calculation).

The edge tubes bend between bolts under that load. For a 20 × 40 × 1.2 tube bent across its 20 mm depth, I = 9 584 mm⁴ (calculation); E = 69 000 MPa (assumption: typical of 6000-series aluminium; the alloy is open, ISS-034, HOLD-09). Fixed at the bolts, a tube deflects 0.041 mm between bolts 400 apart and 0.066 mm at 452 (calculation). Two tubes give at most 0.13 mm against the 0.8 mm of a 25% squeeze, so the seal stays even along the seam. That is why **one bolt per frame bay (400 mm, D-34) is enough for the seal**; strength needs fewer (section 2.6).

A panel's own weight doesn't clamp a seam: an upper side panel's outer part weighs about 11.3 kg (calculation: 6.6 kg/m², from HW's 12.6 kg/m² minus the cassette's 6.0 kg/m², SEL A8) and gives about 0.07 N/mm along its 1495 mm seam, a sixth of the 0.41 N/mm needed (calculation). Hence F3.

### 2.6 Load cases

None of these loads is in the requirements yet. They are working values, so each joint has a load to check against, and each is marked.

| LC | What | Value | Status |
|---|---|---|---|
| LC1 | Own weight. Outer panels 6.6 kg/m² for walls, 5.3 kg/m² for the ceiling (its fill rides on the cassette, D-24); wall cassette 10.3 kg (1500 × 1145, SEL A8); ceiling cassette about 16 kg with its fill (SEL A8); door unit 47.5 kg (D-56) | as listed | calculation (from HW, SEL); door confirmed (D-56) |
| LC2 | Someone leaning or pushing on a wall: 0.5 kN per metre of wall, at 1.2 m height | 0.5 kN/m | assumption; to check against EN 1991-1-1 §6.4 for office partitions (unverified: memory of that table) |
| LC3 | Door misuse: a downward force at the free edge of the open door | 600 N | assumption; EN 1192 classes to be checked (unverified) |
| LC4 | Handling and shipping: the panel carried at its edges by two people; a 2 g bump on the pallet | 2 g | assumption |
| LC5 | Repeated assembly | 5 cycles | assumption (REQ-ASM-09) |

What they give at the joints (calculation): LC2 on a wall spanning 2.29 m from the base band to the ceiling gives 0.26 kN/m at the base and 0.24 kN/m at the top; at one bolt per 400 mm that's about **105 N per base bolt and 95 N per top bolt**. The door's own weight (LC1) puts a 274 N·m moment on DL, a couple of 152 N between hinges 1.8 m apart (hinge spacing: assumption); LC3 adds 705 N·m, another 391 N. These are small next to the bolt's 11.6 kN proof load. **The weak link is the rivnut in the 1.2 mm tube**, which has no published rating (SEL A5), so every joint's strength is shown by test T-03 (section 5), not by a catalogue number (guideline §8.1).

The wall works as a plate held on its edges (base, top, corner and decor joints) and across its seam. How the moment from LC2 shares between the seam and the edges needs the panel's own calculation or the wall sample's push test (T-05); it isn't settled here.

### 2.7 Tolerance and adjustment, common to all joints

- **Locating:** two H-05 spigots per horizontal seam, per wall on the base band, and per ceiling half on the back wall's top. The back corners and the vertical seams need none of their own: both panels already stand on base band spigots. One spigot hole is Ø8.5, round; the other a slot 8.5 wide × 14 long along the joint, so frame-length errors can't jam (PROPOSED; sizes assumption until the frame tolerances are set).
- **Bolt clearance holes Ø6.6** (ISO 273 medium series for M6; unverified, from memory) give ±0.3 mm of float at each bolt; the spigots carry the rest.
- **Squeeze is set by metal stops** (the rivnut flanges), not by torque, so a joint closes to the same gap however hard it's tightened (section 2.2).
- **Frame flatness at a joint face:** ±0.5 mm over a seam (assumption; set in the frame drawing with the maker's capability, guideline §6.3). The gasket takes up its squeeze range, about 0.8 mm at 25%.
- **Room floor:** ±5 mm over the footprint (ISS-054, assumption), taken up by the 8 glides under the base band (LAY B-GLIDE), set from above with the same 5 mm key before any wall goes on.
- **Torque:** HOLD-01 (D-48). These joints only need to be snug: a seal needs at most 185 N per bolt (section 2.5), so the torque only has to seat the head on its stop. It's set from the spin-out test with a margin (T-02).

## 3. Joint entries

Each entry has the guideline's fields (§8): parts, function and load path, loads, take-down, options compared, choice and reason, parts and process, calculation and tolerance stack, assembly direction, tool and step, what can go wrong, how it's checked, and status.

### 3.1 J-WALL-01: wall to wall, seams inside one wall (IF-04)

| Field | Entry |
|---|---|
| Parts | Horizontal seams: L1–L2, R1–R2 (1495 long), B1–B3, B2–B4 (1207 long). Vertical seams: B1–B2, B3–B4 (1104.5 long). Lengths from SKL. |
| Function and load path | Keeps the outside faces flush so the reveals stay crisp (D-23); carries shear across the seam, in the wall's plane (racking) and out of it (LC2); seals the seam. Horizontal seam: the upper panel's bottom tube sits on the lower panel's top tube. Vertical seam: B2's (or B4's) left tube sits against B1's (or B3's) right tube. Load: bolt → rivnut → the lower or left panel's tube wall. |
| Loads | LC2: about 95 N per bolt across the seam (2.6). Seal: 164–185 N per bolt (2.5). LC1: the upper panel's weight, about 110 N, sits on the lower panel through the stops and gasket. |
| Take-down | Yes, 5 cycles (REQ-ASM-09); the bolts back out and stay captive. |
| Options compared | (a) Tool-free hook or wedge connector (the layout study's assumption): no rated part, and the panel's weight gives a sixth of the seal force (2.5). (b) Room-side draw latch: no room in the 4 mm gap (F1). (c) **Captive in-member M6 bolt (chosen).** (d) Glue or rivets on site: not allowed (REQ-ASM-05). |
| Choice and reason | (c): it gives the seal force against a metal stop, uses only parts with data (H-01, H-03), and needs only the one key. It costs about 12 minutes against (a) (F3). (a) goes on the wall sample as an experiment (T-07). PROPOSED. |
| Nut side and bolt side | Nut side: the lower panel (horizontal seams) or the left panel, B1 or B3 (vertical seams). Rivnuts in the top face (40 mm) of the lower panel's top tube, or in the +X face (40 mm) of B1's or B3's right tube; H-04 strip on that face; 2 H-05 spigots per horizontal seam. Bolt side: the upper panel's bottom tube (access hole in its top wall, from the bay above it), or B2's or B4's left tube (access hole in its +X wall, from its bay). All factory-fitted. |
| Bolt count and pitch | One bolt per frame bay, at the bay's middle: side horizontal seams 4 each (1495 / 400, rounded up); back horizontal seams 3 each (1207); back vertical seams 3 each, at 100 from each end and at mid-height, so 452 apart (calculation). **20** for the pod. |
| Calculation and stack | Stack 2.2: the nut-side tube is 20 deep along the bolt, so the tip clearance is at least 0.6 (the tight case). Seal 2.5: tube deflection at most 0.066 mm per tube. |
| Assembly direction, tool, step | Horizontal: the upper panel is lowered onto the lower one, spigots into the hole and the slot. Vertical: the second back panel stands on its base band spigots beside the first (LAY step 4). Bolts driven from inside through the bolt side's bay pocket with the 5 mm key, before the cassettes go on (LAY steps 4, 5 and 11). Bolts at 2.2 m need the step stool (LAY). |
| What can go wrong | The rivnut spins or pulls out (T-02, T-03); the gasket is squeezed too far if the flange is thin (HOLD-03, 2.2); the key can't reach (pocket missing or fill in the way, T-06); the tip touches the far wall of a 20-deep tube (2.2: at least 0.6 mm); the outside faces step at the seam (spigot fit, T-05). |
| Check and pass mark | T-02, T-03, T-05, T-06 (section 5). Pass: no spin at the set torque; faces flush within 0.5 (assumption) after 5 cycles; seam gap even within 0.3 (assumption). |
| Status | PROPOSED. HOLD-01, -02, -03, -05. All rivnuts here are in 40 mm faces, so HOLD-04 doesn't apply. |

### 3.2 J-WALL-02: back corner, side wall to back wall (IF-03)

| Field | Entry |
|---|---|
| Parts | BL corner: L1–B1, L2–B3. BR corner: R1–B2, R2–B4. |
| Function and load path | Closes the box at the back corners: racking between side and back walls, the back wall's out-of-plane load into the side walls (LC2), position, seal. The side panels' ACP covers the back panels' edges (D-55, BP-25). Load: the back panel's outer tube → bolt → rivnut in the side panel's back member. |
| Loads | LC2 on the back wall: 0.24–0.26 kN per metre of edge (2.6), about 105 N per bolt with 3 bolts per panel height. Seal: 185 N per bolt. |
| Take-down | Yes, 5 cycles. |
| Options compared | (a) A bolt in the 17 mm overlap: the rivnut and access hole land on tube corners (2.4). (b) A room-side corner angle: no room in the 4 mm gap, and the side panel has no tube face in front of the back panel (F1, 2.4). (c) Tool-free hooks in the overlap: 2.5 mm margins in 17 mm, and no seal force (F3). (d) **A 40 × 40 side back member with an in-member bolt (chosen).** |
| Choice and reason | (d): it makes room for the standard bolt and rivnut, adds 0.59 kg for the four corner members (calculation, 2.4), and keeps one fastener type. PROPOSED. |
| Nut side and bolt side | The back panels go on first, then the sides (LAY step 4). Nut side: the side panel's back member, 40 × 40 × 1.2 (Y +810 to +850), with H-03 rivnuts in its room-side face (X ∓1207) at Y +828 and the H-04 strip on that face. Bolt side: the back panel's outer tube (B1's left, B2's right), with Ø6.6 in its X ∓1207 wall and Ø11 in its X ∓1187 wall at Y +828. The back panel stands with its bolts pulled back flush; the side panel then goes on, and the bolts are driven from the back panel's bay. |
| Bolt count | 3 per panel height (100 from each end, and the middle): 6 per corner, **12** for the pod. |
| Calculation and stack | Stack 2.2: the nut-side member is 40 deep along the bolt, so the tip clears by 20 or more. Overlap 37 (2.4). |
| Assembly direction, tool, step | The side panel is lowered onto its base band spigots against the back panel's edge; the bolts go in along X from inside the back panel's bay pocket, 5 mm key (LAY steps 4 and 5). |
| What can go wrong | The base band spigots hold the side panel 0.5 mm off the back panel's edge: the spigot slot at that end must run along X (2.7). The outside corner shows the side member's back face (Y +850, 43 wide with the ACP edge): it needs the side skin's return or a trim; that's a WALL drawing detail (section 7, item 5). |
| Check and pass mark | T-02, T-03, T-05, T-06; T-09 for the corner. Pass as J-WALL-01. |
| Status | PROPOSED; HOLD-01, -02, -03, -05. |

### 3.3 J-BASE-01: wall to base band, the wall-to-floor joint (IF-01)

| Field | Entry |
|---|---|
| Parts | The bottom tubes of L1, R1, B1 and B2 on the base band pieces BAND-L, BAND-R and BAND-BACK (100 × 40, on 10 mm glides, SKL; LAY B-BAND). The thin floor lies loose inside the band (LAY step 3) and isn't part of this joint. |
| Function and load path | Carries the walls' and roof's weight to the band and through the glides to the room floor; locates the walls; takes the base share of LC2 and racking; seals the wall to the band. Weight: the wall's bottom tube → rivnut flanges and gasket → band top → glides. |
| Loads | LC1: about 0.34 kN per metre for a side wall with its cassettes and a third of a ceiling half (calculation from the LC1 masses). LC2: about 105 N per bolt (2.6). |
| Take-down | Yes, 5 cycles. |
| Options compared | (a) A room-side angle from the band to the wall: clashes with the lower cassette, which starts at Z 110 (SKL), in the 4 mm gap (F1). (b) Spigots only, no bolt: nothing holds a panel down while the next one goes on, and nothing squeezes the gasket. (c) **In-member bolts down through the wall's bottom tube into rivnuts in the band's top wall (chosen).** |
| Choice and reason | (c), with two spigots per panel so each wall stands on its own before its bolts go in (REQ-ASM-04). The 14 bolts match the layout study's count for this step (LAY §5 step 4). PROPOSED. |
| Nut side and bolt side | Nut side: the band's top wall, with 2 H-05 spigots per panel and H-03 rivnuts at each bay middle, coaxial with the wall tube's centre line (X ±1227 or Y +827, which is 3 mm off the band's own centre line, calculation from SKL). The band's wall thickness must be inside the rivnut grip, 0.70–4.20 (**HOLD-07**: the band section isn't chosen). H-04 strip on the band top. Bolt side: the wall's bottom tube, with the spigot hole and slot, Ø6.6 in its bottom wall and Ø11 in its top wall for each bolt. H-06 base seal under the band (HOLD-06). |
| Bolt count | L1 and R1: 4 each; B1 and B2: 3 each. **14.** |
| Calculation and stack | Stack 2.2 (the band is open inside, so the tip has well over 20). |
| Tolerance and adjustment | The band is levelled on its 8 glides with the same key before any wall goes on (2.7; LAY step 2). The ACP's outer face stays flush with the band's outer face at X ±1250 and Y +850 (SKL), so the frame overhangs the band by 3 mm on the inside (calculation: band 40, panel 43). |
| Assembly direction, tool, step | The wall is lowered onto the band spigots; the bolts are driven down from inside through the pocket in the wall's bottom bay, 5 mm key (LAY step 4). |
| What can go wrong | The band's wall too thick for the rivnut (HOLD-07); the band's notch for DR (SKL P03 lists DR 8 mm into BAND-R, a HOLD for the base design); a 10 ± 5 mm gap the base seal can't close (HOLD-06). |
| Check and pass mark | T-02, T-03, T-05, T-06, T-08. Pass as J-WALL-01, plus the base seal touching the floor all the way round on a ±5 mm floor (assumption). |
| Status | PROPOSED; HOLD-01, -02, -03, -05, -06, -07. |

### 3.4 J-CEIL-01: wall to ceiling (IF-05), and J-CEIL-02: ceiling half to ceiling half (IF-06)

| Field | Entry |
|---|---|
| Parts | Side edges: C1 to L2, C2 to R2 (1495 long). Back edges: C1 to B3, C2 to B4 (1207 each). The C1–C2 seam at X 0 (1495). |
| Function and load path | Carries the roof (outer panels, cassettes) to the walls; ties the box together at the top (racking); seals. The side panels' ACP covers the ceiling's edges (D-55). Side edges: the ceiling's side tube → bolt → rivnut in the upper side panel's top member (40 × 40, F2), in shear. Back edge: the ceiling's back member sits on the back wall's top tube (once F5 is fixed) and is bolted to it. |
| Loads | LC1: a ceiling half's outer panel about 9.6 kg plus its cassette about 16 kg hanging from it (calculation, 2.6): about 250 N per half, under 40 N per bolt if shared evenly over its 4 side and 3 back bolts (calculation). LC2 at the top: about 95 N per bolt (2.6). Seal: 164–185 N per bolt. |
| Take-down | Yes, 5 cycles. Overhead work from the step stool (LAY step 6). |
| Options compared | As J-WALL-02: both edges overlap only 17 mm (F2). A ledge under the ceiling's side tube was also looked at: it would sit in the 4 mm gap above the side lining (D-57), which leaves no room. |
| Choice and reason | In-member bolts, with the upper side panels' top members and the ceiling halves' back members at 40 × 40 (F2). Two people lift a half into place from inside (LAY step 6): its back edge drops onto 2 spigots on the back wall's top tube (REQ-ASM-04), its side tube lies against the side wall, and they hold its front edge until the first side bolts are in. PROPOSED. |
| Nut side and bolt side | **Side edges:** nut side the wall: rivnuts in the upper side panel's top member (room-side face, 40 × 40, at Z 2378); bolt side the ceiling's side tube (access hole in its inner wall, reached from below through the ceiling's open bay). **Back edges:** nut side the ceiling: rivnuts in the bottom face of the ceiling's 40 × 40 back member, at Y +828; bolt side the back panel's top tube (Ø6.6 in its top wall, Ø11 in its bottom wall, reached from the pocket in the back panel's top bay); the bolts are pulled back flush while the ceiling goes on, then driven up. The ceiling's back member can't be the bolt side: its access hole would face the roof skin. **C1–C2:** nut side C1 (rivnuts in its right tube's +X face, 40 mm), bolt side C2's left tube, reached through C2's open bay. |
| Bolt count | Side edges 4 each; back edges 3 each: **14** (the layout study's count for this step, LAY §5 step 6). C1–C2: **4**. |
| Calculation and stack | Stack 2.2. Side edges: the nut-side member is 40 deep, so the tip clears by 20 or more. Back edges: the nut side is the 40 × 40 member: 20 or more. C1–C2: the nut-side tube is 20 deep: the tight case (at least 0.6). |
| What can go wrong | F5 not fixed: the back edge has nothing to sit on. The ceiling cassettes and their catches (J-LIN-01) hang on the same ceiling tubes, so those tubes carry both. |
| Check and pass mark | T-02, T-03; the ceiling isn't in the wall sample, so its joints are checked on the corner mock-up (T-09) or the prototype. |
| Status | PROPOSED; HOLD-01, -02, -03, -05, -11. |

### 3.5 J-FRONT-01: decor block to wall (IF-07)

| Field | Entry |
|---|---|
| Parts | DL to the left wall's front edge (L1, L2); DR to the right wall's front edge (R1, R2). They meet face to face at Y −645: the decor's back plate against the side walls' front members (D-49). |
| Function and load path | Holds DL and DR upright against the side walls, carries the door's moment from DL into the left wall (IF-07, ISS-045), and seals the decor to the wall. Weight goes down through the decor block onto the base band (DL stops at Z 110 on the band, D-57; DR's notch is a base HOLD). Moment: hinges → DL's core frame → back plate → bolts → the left wall's front member. |
| Loads | The door's own weight: a 152 N couple between hinges 1.8 m apart (assumption); misuse (LC3): 391 N more (calculation, 2.6). These go into the wall through 6 bolts per side; the top and bottom bolts take most of it. ISS-045 asks for the full load-path calculation with the decor core frame's size; this entry gives only the joint's share. |
| Take-down | Yes, 5 cycles. DR is also opened from inside for fan service (D-59), which doesn't touch this joint. |
| Options compared | (a) The build plan's V brackets with steel screws (BP-29; SEL A7 picks Simpson ABR7015): a room-side bracket would sit under the side lining, which starts at Y −645 (SKL), in the 4 mm gap (F1); screws aren't the M6 bolt (REQ-ASM-02). (b) Bolts from inside the decor block into the wall: DL has the hinge pocket and no access panel yet. (c) **In-member bolts from the side wall's front bay through the decor's back plate (chosen).** |
| Choice and reason | (c): the same principle as every other joint, reached from inside the pod. The ABR7015 bracket isn't needed for this joint (it may still serve inside the decor block: FRONT's call). PROPOSED. |
| Nut side and bolt side | The walls go up first, then the decor blocks (LAY §5). Nut side: the decor block. **Preferred:** H-03 rivnuts in the back plate itself, if FRONT makes it aluminium 2–4 mm thick (inside the rivnut grip); then the stack is the standard one and the bolt is M6 × 20. **Fallback:** if the back plate can't take a rivnut, the rivnuts go in the core frame's rear member behind Ø14 holes in the back plate (FR-09), and the bolt is M6 × 25 (calculation: 1.2 wall + 2.39 gasket + 3 back plate, assumption + 14.86 rivnut + 2 to pass it = 23.5 under the head). In the fallback the flange sits below the plate's face, so it's no longer the squeeze stop and the torque sets the squeeze: the preferred route is better. Bolt side: the side panel's front member (20 deep along Y), with Ø6.6 in its front wall and Ø11 in its back wall, reached from the pocket in the side panel's front bay. |
| Bolt count | 3 per side panel (100 from each end, and the middle): 6 per block, **12**. |
| What can go wrong | The decor's back plate or rear member isn't behind the bolt (FRONT CAD); rivnut pull-out under the door misuse moment (T-03 at the DL load); DL's hinge pocket weakens its frame (ISS-045). |
| Check and pass mark | T-03 at the DL load (about 1.6 kN, assumption: 3 × the top bolt's share of 152 + 391 N); the door sample (SEL sample test 5) with DL bolted to a wall piece. |
| Status | PROPOSED; HOLD-01, -02, -03, -05, -10; ISS-045 open (FRONT). |

### 3.6 J-LIN-01: lining cassette clips (IF-10)

| Field | Entry |
|---|---|
| Parts | Each wall cassette (L1, L2, R1, R2 and B1–B4 cassettes) and ceiling cassette (C1 and C2 cassettes) to its outer panel's frame. |
| Function and load path | Hangs the cassette on the frame without any screw through it, so the inner leaf floats (D-17); holds it under its own weight and knocks; ceiling cassettes can't drop (D-47); hook-and-loop only lines it up. Load: tray → clip → frame tube. The perimeter gasket (PORON 3.2 mm in the 3–4 mm gap, HW §1 layer 5) seals the cassette's edge and carries no load. |
| Loads | Per clip (SEL A8, the Hardware Engineer's calculation, safety factor 3 as an assumption): a wall cassette, 10.3 kg on 4 clips, needs 7.7 kg rated in shear per clip; a ceiling cassette, about 16 kg on 6 clips, needs 8.0 kg rated in pull-out per clip; the ceiling catch needs 48 kg per lanyard, 2 lanyards. |
| Take-down | Yes: cassettes lift off with no tools (HW §8); 5 cycles. |
| Options compared | SEL A8: Häfele KEKU EH (candidate; its rating basis, pull-out rating, captive lock and a fixing to a 0.5 mm tray aren't stated); hook-and-loop alone (no load rating; locating only). |
| Choice and reason | **HOLD (D-56, ISS-076).** This register sets what the clip must meet, so CAD can reserve its space: (1) the rated loads above; (2) captive: it can't unhook without a deliberate lift (D-47); (3) it fits the 4 mm frame-to-tray gap, or sits on the tray's 25 mm returns at the cassette's edge, and clears the site bolts' Ø11 access holes and the pockets; (4) it fixes to the 0.5 mm tray return and to a frame tube's 20 mm face with rivnuts or blind rivets, never through the ACP; (5) it's soft enough not to bridge the floating leaf (HW §10: clip stiffness unknown); (6) the ceiling catch anchors to a ceiling tube, which is 20 × 40 now, not the 20 × 100 that SEL A8 names (ISS-079). |
| Assembly direction, tool, step | Last, after every bolt is in and checked (LAY step 11). Wall cassettes hook on from inside; ceiling ones from below, with the catch clipped first. No tool (REQ-ASM-03). |
| What can go wrong | A clip lands over a bolt's access hole or pocket (rule R8, section 8); the clip bridges the leaf and costs sound (HW §10: about 0.5 dB if the clips act as point bridges); a ceiling cassette drops if the catch isn't clipped first. |
| Check and pass mark | SEL sample test 4 (pull test on a real cassette return, drop test of the catch); T-06 (the wall sample is built with the real clips, HW §10). |
| Status | HOLD (ISS-076, HOLD-08); the requirements above are PROPOSED. |

### 3.7 Bolt count

| Joint | Bolts |
|---|---:|
| J-WALL-01 seams | 20 |
| J-WALL-02 back corners | 12 |
| J-BASE-01 wall to base band | 14 |
| J-CEIL-01 wall to ceiling | 14 |
| J-CEIL-02 ceiling seam | 4 |
| J-FRONT-01 decor to wall | 12 |
| **Total in this register** | **76** |

Not counted here: the base band's corner keys, the door hinges, the fixed glass profiles and DT to the ceiling. The layout study's decided build had 76 bolts and 38 tool-free connectors in all; with F3, the 36 seam and corner connectors here become bolts (calculation).

## 4. Tolerance stacks at the joint faces

Worst case, not RSS: there are no process data yet (guideline §6.3). All values in mm; frame tolerances are assumptions until the frame drawing and the maker's capability set them.

| Stack | Contributors | Worst case | Result | Status |
|---|---|---|---|---|
| Bolt in its clearance hole across two parts | Hole position ±0.2 in each part (assumption, CNC); hole Ø6.6 on a Ø6 bolt, 0.3 a side | 0.4 against 0.3 | Can bind by 0.1 at worst. So the **spigots locate, and the bolt holes are positioned from the spigot holes**: at ±0.15 in each part the bolt always enters (calculation) | calculation; the frame drawing sets ±0.15 at the joint holes (PROPOSED) |
| Spigot in its hole and slot | Spigot Ø8 h9, hole Ø8.5 H11 (assumptions); positions ±0.15 in each part | 0.5 clearance against 0.3 | Always enters; leaves up to ±0.25 of float, which the bolts take up | calculation |
| Outside faces flush across a seam | Frame depth 40 ±0.3 a panel (assumption); bond line 3 ±0.5 (bond spec); ACP 3 ±0.2 (assumption) | ±1.0 a panel, up to 2.0 between two | **Too much for a crisp reveal.** So the outer panels are bonded face down on a flat table, with the ACP face as datum A (bond spec §5). The frame and the bond line then don't set the face: ±0.2 (ACP) and ±0.3 (table) a panel, up to 1.0 between two | calculation; PROPOSED rule: the ACP face is datum A of every outer panel |
| Gasket squeeze | Flange t_f (HOLD-03) ±0.1 (assumption); gasket 3.18 ±0.3 (assumption); tube face flatness ±0.5 over the seam (assumption) | — | Stays inside 25–50% only if the gasket is picked after HOLD-03 and the flatness holds ±0.3 | calculation; closes with HOLD-03 and T-05 |
| The lining floats clear of the frame at the bolts | Gap 4 (SKL, assumption); nothing proud of the frame's room-side face (every head is inside the tubes, 2.2) | 4 | Clear by design; the clip's own height is HOLD-08 | calculation |

## 5. Tests in the wall sample, and two joint samples

Physical tests stay PLANNED until real data exists (guideline §10). The factory's wall-and-door sample is the physical check (D-32). These add to the hardware selection's sample tests 1–5; they don't replace them.

| Test | What | Sample | Pass mark | Status |
|---|---|---|---|---|
| T-01 | Setting the CAH3-610-4.2 in the real 20 × 40 × 1.2 tube, in a 20 mm face and in a 40 mm face; the bulge clears the inside | 10 rivnuts in an offcut | Sets flush, no cracks, bulge clear (SEL A5 HOLD) | PLANNED |
| T-02 | Spin-out torque (SEL sample test 2, D-48) | 10 rivnuts in an offcut | Sets the tightening torque with a margin; the torque goes in the assembly guide | PLANNED |
| T-03 | Pull-out and shear of a whole joint: M6 × 20 through a bolt-side tube into a rivnut in a nut-side tube, with 20-deep and 40-deep nut-side tubes | 5 of each | Failure at 3 × the joint's highest bolt load or more (assumption: about 0.6 kN for the walls, 1.6 kN for DL), and no loss of fit after 5 assemble-and-strip cycles (REQ-ASM-09) | PLANNED |
| T-04 | Captive retainer: the bolt stays in its tube when the panel is shaken, carried and turned over; it runs forward and backs out 5 times | 5 | Doesn't fall out; push-off force at least 3 × the bolt's weight (assumption) | PLANNED, after HOLD-02 |
| T-05 | Flushness and gasket squeeze on the wall sample's seams; push test at 1.2 m with the LC2 load | wall sample | Faces flush within 0.5 (assumption); seam gap even within 0.3 (assumption); squeeze 25–50% at every bolt; no step after the push | PLANNED |
| T-06 | Access: a person drives every bolt of the wall sample with the 5 mm key through the pockets, cassettes off, then clips the real cassettes on; timed | wall sample | Every bolt reached; the time goes in the assembly guide | PLANNED |
| T-07 | Experiment (no gate): a tool-free wedge hook on one vertical seam with a low-force seal, next to a bolted seam | wall sample | Seam squeeze and sound compared with the bolted seam; if they match, the PM can switch seams to tool-free (F3) | PLANNED, optional |
| T-08 | Base seal on a floor stepped ±5 mm | base band piece | Touches all the way along; checked with a light from inside | PLANNED, after HOLD-06 |
| T-09 | Corner mock-up: one side panel corner, one back panel edge and one ceiling corner, bolted | joint sample | Bolts reached and driven, overhead too; corner faces flush within 0.5 | PLANNED |

## 6. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Owner | Released when |
|---|---|---|---|---|
| HOLD-01 | Rivnut tightening torque (D-48, ISS-011) | None: the spin-out test sets it (T-02) | Hardware Engineer | T-02 recorded and the PM lifts it |
| HOLD-02 | Captive retainer (H-02) | Which push-in retainer holds an M6 bolt in an 11 mm or 6.6 mm hole in 1.2 mm aluminium, with what push-off force, and lets it be driven and backed out 5 times? | Joints Engineer with the Hardware Engineer | Part named with data; T-04 passed |
| HOLD-03 | Rivnut flange thickness and thread position (H-03) | To Sherex: the CAH3-610-4.2 drawing: flange thickness, and where the thread starts along the 14.86 length | Hardware Engineer | Drawing on file; stack 2.2 and the gasket thickness re-checked |
| HOLD-04 | Rivnut edge distance in a 20 mm tube face | To Sherex: the minimum distance from the Ø9.53 hole to the edge of a 1.2 mm wall. Is 5.2 mm to the side of a 20 mm tube (calculation: (20 − 9.53) / 2) enough? Only the clip fixings might use a 20 mm face; every site-joint rivnut here is in a 40 mm face | Hardware Engineer | Answer on file, or T-01 shows no cracking |
| HOLD-05 | Gasket converter and strip (SEL D) | PORON 4701-40 with adhesive in 10 mm strips, 3.18 and 4.76 mm thick, with Ø14 holes at the rivnuts | Hardware Engineer | The converter's strip data on file |
| HOLD-06 | Base seal for a 10 ± 5 mm gap (H-06) | Which bulb or brush seal closes 5–15 mm under an aluminium band, with a published compression range? | BASE engineer | Part named; T-08 passed |
| HOLD-07 | Base band section: wall thickness inside the rivnut grip (0.70–4.20), and room for the spigots | None: BASE design | BASE engineer | Band drawing with its wall thickness |
| HOLD-08 | Cassette clip and ceiling catch (D-56, ISS-076) | SEL question 10 (Häfele: KEKU EH rating basis, pull-out, a captive version, a fixing to a 0.5 mm tray; a rated lanyard), plus points 3–6 of J-LIN-01 | Hardware Engineer; Layout Engineer | Part with its ratings; SEL sample test 4 passed |
| HOLD-09 | Frame tube alloy, temper and E (ISS-034) | None: hardware selection | Hardware Engineer | Alloy named; section 2.5 re-checked with its E |
| HOLD-10 | The decor's back plate material and thickness, and its core frame's rear member (ISS-045) | None: FRONT design | FRONT engineer | FRONT CAD shows what takes each J-FRONT-01 rivnut |
| HOLD-11 | The back wall's top edge under the ceiling (F5) | None: skeleton geometry | Fusion Engineer | The back wall reaches Z 2357, or a closer is drawn |

## 7. Decisions for the PM

1. **Seams and corners: captive bolts (recommended) or tool-free connectors?** D-08 says tool-free wherever they can hold. Here they can't make the seal force (F3, section 2.5), and nothing fits the 4 mm gap (F1). Bolts cost about 12 minutes (125 → about 137 min, the layout study's own figure). Recommendation: bolts for the prototype, with the wedge hook as an experiment on the wall sample (T-07). Until the PM rules, this register follows the recommendation, marked PROPOSED.
2. **Bolt head: ISO 4762 socket head (recommended) or ISO 4017 hex head (SEL A5)?** Socket heads fit inside the 20 × 40 tube and take the one 5 mm key the layout study timed (F6).
3. **Edge members at the 90° joints: 40 × 40 × 1.2 (recommended, +1.29 kg), or 30 × 40 × 1.2 (+0.65 kg) if the extruder lists it?** The pod is already estimated at about 427 kg against the 420 kg cap (D-54).
4. **F5, for the Fusion Engineer:** make the back wall's outer panels reach the ceiling frame (Z 2357), so the ceiling's back edge sits on them; the back linings stay where they are.
5. **The outside corner at the back, for the WALL drawing:** the side panel's back member face (Y +850, 43 wide with the ACP edge) shows from behind. The side skin returns around it or a trim covers it, without changing the look (D-01).

## 8. Feature-rationale inputs for the Fusion Engineer

What each joint puts into each sample part, and why (guideline §7). Sizes are PROPOSED, with the status shown; positions follow the rules, and the Fusion Engineer places them on the real frame. "Nut side" and "bolt side" are as in section 2.2. Hole tags (H01…) go on the drawings, not here. X and Y are the pod axes (conventions §4); on a part drawing they map to the view's X and Y.

| ID | Part (sample set) | Feature | Size | Where (rule) | Why (function and source) | Status |
|---|---|---|---|---|---|---|
| FR-01 | Nut side: lower panels' top tubes; B1's and B3's right tubes; the base band's top wall; the side panels' 40 × 40 back members; the upper side panels' 40 × 40 top members; the ceilings' 40 × 40 back members (bottom face); C1's right tube; the decor's back plate (or its rear member, fallback) | Rivnut hole | Ø9.53 +0.10, through one 1.2 wall | One per bolt, at the middle of each frame bay along the joint; centred on the bolt-side tube's centre line (on the band, 3 mm off the band's own centre line) | H-03 needs that hole (SEL A5); one per bay for the seal (2.5) and the key's reach (2.3) | source (hole size); position PROPOSED |
| FR-02 | Bolt side: upper panels' bottom tubes; B2's and B4's left tubes; the walls' bottom tubes; the back panels' outer tubes at the corners; the ceilings' side tubes; the back panels' top tubes; C2's left tube; the side panels' front members | Clearance hole in the joint-side wall | Ø6.6 | Coaxial with FR-01 | M6 float ±0.3 (2.7) | PROPOSED (Ø6.6 unverified against ISO 273) |
| FR-03 | The same bolt-side tubes | Access hole in the bay-side wall | Ø11 | Coaxial with FR-02 | Passes the Ø10 head and the 5 mm key (ISO4762, 2.2) | calculation |
| FR-04 | Lower panels' top tubes (horizontal seams); the base band's top wall; the back panels' top tubes (B3, B4) for the ceiling | Spigot rivnut | Ø9.53 +0.10 | 2 per joint, about 100 from each end (assumption), not at a bolt | Holds H-05; the part stands located before any bolt goes in (REQ-ASM-04) | PROPOSED |
| FR-05 | Upper panels' bottom tubes; the walls' bottom tubes; the ceilings' 40 × 40 back members (bottom face) | Spigot hole and slot | Ø8.5 round at one end; slot 8.5 × 14 along the tube at the other | Coaxial with FR-04; where a side panel meets the back corner, the slot at that end runs along X | One fixed point and one slot, so frame-length errors can't jam (2.7, 3.2) | PROPOSED (assumption sizes) |
| FR-06 | Side panels' back members (L1, L2, R1, R2); upper side panels' top members (L2, R2); ceiling halves' back members (C1, C2) | Member size | 40 × 40 × 1.2 instead of 20 × 40 × 1.2 | Whole length of that edge | An overlap of 37 instead of 17, so the rivnut and the bolt fit (F2, 2.4) | PROPOSED; +1.29 kg (calculation) |
| FR-07 | Back panels' outer tubes at the corners | FR-02 and FR-03 pair, along X | as FR-02 and FR-03 | Y +828 (the middle of the 37 overlap), 3 per panel height | J-WALL-02 (3.2) | calculation |
| FR-08 | Side panels' front members (L1, L2, R1, R2) | FR-02 and FR-03 pair, along Y | as FR-02 and FR-03 | 3 per panel height, centred on the member's 40 mm face | J-FRONT-01 (3.5) | PROPOSED |
| FR-09 | Decor back plate (DL, DR), fallback only | Hole around the rivnut flange | Ø14 | Coaxial with FR-08 | The flange sits in the plate so the wall bears on the plate (3.5) | PROPOSED (assumption: flange Ø12.96 + 1) |
| FR-10 | Every wall panel bay next to a bolt (bolt side) | Fill pocket | 60 × 60 × 40 deep, no fill | At each FR-03 | The key's reach (2.3) | PROPOSED (assumption) |
| FR-11 | Every nut-side joint face | Gasket strip | 10 wide, Ø14 holes at the rivnuts | Centred on the bolt line | Seal at 25–50% squeeze (2.2, 2.5; ISS-003) | PROPOSED |
| FR-12 | Frame tubes behind each cassette's clips and the ceiling catch | Clip and catch fixings | HOLD-08 | Not drawn until the clip is released; reserve an envelope marked UNVERIFIED | D-47, D-56 | HOLD |

Rules for the Fusion check (each can be a scripted check on the CAD):

- R1. Every FR-01 has a coaxial FR-02 and FR-03 in its partner, within 0.15 (2.7, section 4).
- R2. No joint hole's edge closer than 10 mm (assumption) to a tube's inside corner; FR-07 is the tight case at 12 mm (2.4).
- R3. Nothing stands proud of a frame tube's room-side face except the clips (F1, 2.2).
- R4. A bolt's tip clears the far wall of its nut-side tube by at least 0.6 (2.2).
- R5. Every FR-03 in a wall panel has its FR-10 pocket, with no frame member or cable in it.
- R6. Every part that goes on site stands on a locating pair (FR-04 and FR-05) before its first bolt: walls on the band or the panel below, ceiling halves on the back wall (REQ-ASM-04).
- R7. One bolt type in the BOM for every site joint: M6, ISO 4762, 8.8, in one length (20), or two (20, 25) if J-FRONT-01 uses its fallback (REQ-ASM-02).
- R8. No clip (FR-12) over an FR-03 hole or an FR-10 pocket.
