# Joints register: Spaceship (FocusPod v2), Milestone 2 sample set

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-01 (PROPOSED code; the control pack adds the register row) | P01 | DRAFT | 2026-10-31 | Joints Engineer (v2 Milestone 2) |

This is the joint register the guideline asks for (§8, and Milestone 2 item 6), for the site joints of the sample set: wall to wall, wall to floor (base band), wall to ceiling, back corner, decor to wall, and the lining cassette clips. It also gives the feature-rationale inputs (§7) the Fusion Engineer needs: which holes and slots each joint puts in which part, and why (section 8), and the seam gap the skeleton needs (section 2.8).

- **Status of numbers** (conventions §9): confirmed, source, calculation, assumption, unverified. Every number below carries one.
- **Status of choices:** DECIDED where the PM has ruled, citing the ruling; every other choice in this file is **PROPOSED**: the work goes ahead on it until the PM rules (`AGENTS.md`).
- **PM rulings used here that aren't in the decision log yet** (joints group, 2026-10-31; the control pack adds the rows): **R-J1** captive bolts on seams and corners, replacing D-08's tool-free seam clips, because sealing the gaskets matters more than about 12 minutes of assembly; **R-J2** socket heads to ISO 4762 throughout, so one 5 mm key does the whole pod; **R-J3** 40 × 40 corner edge tubes, accepting the extra 1.3 kg; **R-J4** the back wall's outer frames run up to the ceiling frame at Z 2357 (Fusion Engineer 2 has it).
- **HOLD:** a part or number that waits for data or a test. CAD may reserve a space for it, marked UNVERIFIED, but doesn't use its hole pattern until it's released (guideline §4.3 step 4; D-56). Section 6 lists every HOLD with its question.
- **Not covered here:** the ACP-to-frame bond is in [`bond-spec-acp-aluminium.md`](bond-spec-acp-aluminium.md). Door hinges, the fixed glass and the decor top block's joint to the ceiling (IF-08, IF-09) belong to the FRONT work. The base band's own corner keys and the thin floor belong to the BASE work.
- No supplier was contacted and nothing was ordered. Data comes from the files below and from public pages, each linked with the date read.

## Result

1. **One bolt for every site joint: M6 × 16, ISO 4762 socket head (DECIDED, R-J2), class 8.8, zinc plated, captive in its panel, driven with one 5 mm hex key.** It threads into the Sherex CAH3-610-4.2 rivnut the hardware selection picked for the 1.2 mm tube wall. **76 site bolts** in the six joint families here (section 3.7). The length is a calculation (section 2.2).
2. **Every site bolt lives inside an edge tube of one of the two parts it joins, and is reached from inside the pod** through a small pocket left free of fill, before the lining cassettes go on (they go on last, layout study §5 step 11). Reason: the decided stack leaves only a 4 mm gap between frame and lining, and the cassettes butt at every seam, so there's no room for a bracket, latch or bolt head on the room side of the frame (finding F1).
3. **Seam gap for the skeleton (answer to the Mechanical Checker's F-001): 2.26 mm at every site joint, the compressed gasket thickness.** It is set by a metal stop, not by torque: the rivnut's head, 0.76 mm (Sherex, source), on a 1.5 mm aluminium stop washer clamped under it (PROPOSED part). The 3.18 mm PORON gasket is then squeezed 29% (calculation). Panel sizes that follow are in section 2.8: back panels and ceiling halves (2414 − 3 × 2.26) / 2 = 1203.61 wide.
4. **Findings:**
   - **F1. No room-side hardware.** Frame-to-cassette gap 4 mm (skeleton `lin_gap`, assumption; stack 43 + 4 + 34 = 81, D-16, D-42). An ISO 4762 M6 head alone is 6 mm tall (source). So every fastener sits inside the 40 mm frame depth (section 2.2).
   - **F2. The 90° frame joints overlap only 17 mm**, too narrow for the rivnut and the bolt's access hole (section 2.4). **DECIDED (R-J3):** the edge member of the panel whose skin covers the corner becomes 40 × 40 × 1.2 (side panels' back members, upper side panels' top members, ceiling halves' back members). The overlap grows to 37 mm, for **+1.29 kg** (calculation).
   - **F3. Seams need clamping force, so they get captive bolts.** A gasket only seals when it's squeezed: 0.41 N per mm of seam at 25% for the picked PORON strip, 164 N per 400 mm (calculation, section 2.5). A panel's own weight gives about a sixth of that, and no catalogue latch fits the 4 mm gap. **DECIDED (R-J1):** captive bolts on seams and corners, about 12 minutes more assembly (the layout study's own figure for that change: 125 → about 137 min, calculation).
   - **F4. The ACP bond doesn't fit the 20 mm tube face as the adhesive maker lays it out.** See the bond spec, finding B1.
   - **F5. The skeleton left an 81 × 38 mm void under the ceiling's back edge** (back wall top at Z 2319, ceiling outer panel from Z 2357). **Ruled (R-J4):** the back wall's outer frames run up to Z 2357.
   - **F6. Two head types were in the files** (ISO 4017 in the hardware selection, a 5 mm key in the layout study). **DECIDED (R-J2):** ISO 4762.
5. **HOLDs: 9 open, 2 closed** (section 6). The most important: the rivnut's torque, pull-out and spin-out in the real tube (D-48, ISS-011); the cassette clip and ceiling catch (D-56, ISS-076); the captive retainer part; the base band's section; the decor back plate at the bolts.

## 1. Sources

| Key | File or page | Used for |
|---|---|---|
| GL | `docs/engineering-guideline.md` §6.3, §7, §8, §8.1, §8.2, §10 | Register fields, bolt and bond rules, test status |
| DL | `v2/00-Control/decision-log.md`, D-01 to D-59 | Decided stack, clips, holds |
| PM | PM rulings R-J1 to R-J4 in the joints group, 2026-10-31 | Seams bolted, ISO 4762, 40 × 40 corner tubes, back wall to Z 2357 |
| REQ | `v2/00-Control/requirements.md` | REQ-ASM-02 to -11, REQ-BLD-01, -02 |
| IF | `v2/00-Control/assembly-tree.md` §4 | IF-01, IF-03 to IF-07, IF-10 |
| ISS | `v2/00-Control/issue-register.csv` | ISS-003, -011, -014, -015, -016, -034, -036, -045, -054, -064, -076, -079 |
| SEL | `v2/05-Engineering/hardware/selection.md` | Rivnut A5, bracket A7, clips A8, gaskets and base seal D, sample tests |
| HW | `v2/05-Engineering/acoustics-air/report.md` §1, §8, §10 | Stack layers, gasket in the 3–4 mm gap, cassette mass, clip risk |
| LAY | `v2/05-Engineering/layout-study/report.md` §4, §5 | Assembly order, one 5 mm key, bolt and clip counts, base band and glides |
| SKL | `v2/01-CAD-Native/skeleton/` P03: `100000_P03_POD-SKELETON-PARAMETERS.csv`, `pod_skeleton.py`, `BUILD-RECORD.md` | Envelopes and positions of every panel, cassette and band piece |
| SHX | Sherex [CAH3-610-4.2 product page](https://fasteners.sherex.com/item/nd-rivet-nuts-american-style-rivet-nuts-cah-series/cah-series-aluminum-metric-/cah3-610-4-2-1), read 2026-10-31 | Head Ø12.96 ±0.25, head thickness 0.76 ±0.08, length 14.86 ±0.38, installed length 10.16 max, body Ø9.50 max, open end, aluminium 5056, grip 0.70–4.20, hole 9.53 +0.10. "Grip range can be affected by parent material and hole size": trial installations recommended |
| ISO4762 | ISO 4762 M6 table, via [Engineers Edge](https://engineersedge.com/iso_socket_head_screw.htm) and a [Würth ISO 4762 8.8 listing](https://eshop.wuerth-industrie.com/Hexagon-Socket-Head-Cap-Screw-SCR-CYL-ISO4762-88-IH5-A2K-M6X6/00846%20%206.sku/en/US/EUR/), read 2026-10-31 | Head Ø10 max, head height 6 max, socket 5 |
| ISO898 | ISO 898-1 class 8.8 values via [Engineering ToolBox](https://www.engineeringtoolbox.com/metric-bolts-minimum-ultimate-tensile-proof-loads-d_2026.html), read 2026-10-31 | M6 stress area 20.1 mm², proof load 11.6 kN, minimum ultimate 16.1 kN |

## 2. Rules every site joint follows

### 2.1 Hardware set

| ID | Item | Data | Status |
|---|---|---|---|
| H-01 | **Bolt.** M6 × 16, ISO 4762, class 8.8, zinc plated. Maker and SKU from the master BOM. | Head Ø10, head height 6, 5 mm hex socket (ISO4762). Stress area 20.1 mm², proof load 11.6 kN, minimum ultimate 16.1 kN (ISO898). | DECIDED head type (R-J2); length calculation (2.2); data source |
| H-02 | **Captive retainer.** Holds each bolt in its tube, tip flush with the joint face while the parts are brought together, and lets it run forward into the rivnut. | Part and push-off force not chosen | **HOLD-02** |
| H-03 | **Rivnut.** Sherex CAH3-610-4.2, open end, aluminium 5056 | M6 × 1.0; grip 0.70–4.20; hole Ø9.53 +0.10; head Ø12.96 ±0.25 × 0.76 ±0.08; length 14.86 ±0.38; installed length 10.16 max; body Ø9.50 max (SHX, SEL A5) | source; torque **HOLD-01** (D-48); edge distance in a 20 mm face **HOLD-04** (only the clips might need one) |
| H-04 | **Joint gasket.** Rogers PORON 4701-40 Soft, 3.18 mm, with pressure-sensitive adhesive laminated by a converter, 10 mm wide strips, with a Ø22 hole at each rivnut | 41 kPa at 25% compression; compression set ≤ 5% at 23 °C (ASTM D3574 D) (SEL D) | source; converter and strip **HOLD-05** (SEL) |
| H-05 | **Locating spigot.** Ø8 stainless pin with an M6 thread, screwed into an H-03 rivnut at the factory with threadlocker. A part we make; number from the master BOM. | Ø8, stands 8 proud | PROPOSED (assumption sizes) |
| H-06 | **Base seal.** Closes the gap under the base band to the room floor | Gap 10 nominal (`glide_h`, assumption) ± 5 for the floor (ISS-054, assumption) | **HOLD-06**: none of SEL D's base seals is shown to cover 5–15 mm |
| H-07 | **One tool.** A 5 mm hex key with a ball end, or a 5 mm hex bit in a short driver (LAY §4: one 5 mm key; the base band's glides adjust with the same key) | — | DECIDED (R-J2); meets REQ-ASM-03 |
| H-08 | **Stop washer.** Aluminium, Ø10.5 bore × Ø20 × 1.5, clamped under each site-joint rivnut's head when the rivnut is set, so it can't be lost. A part we make (punched from 1.5 mm 5000- or 6000-series sheet); number from the master BOM. | Grip with it: 1.2 wall + 1.5 = 2.7, inside 0.70–4.20 (SHX). Bore 10.5 clears the Ø9.50 body; the Ø12.96 head clamps it. Needs a 40 mm face (Ø20) | PROPOSED; thickness ±0.05 (assumption) |

The bolt is the only site fastener. Every rivnut, stop washer, spigot, gasket and retainer is fitted in the factory (D-08, REQ-ASM-10). Every site-joint rivnut sits in a 40 mm tube face, so its hole is 15.2 mm from either side of the face (calculation: (40 − 9.53) / 2).

### 2.2 The in-member bolt: how every site bolt is placed

Each joint has a **nut side** (the part with the rivnut) and a **bolt side** (the part whose edge tube holds the captive bolt). The bolt side is the part whose frame bay the person inside the pod can reach; each joint entry says which is which.

1. The nut side has an H-03 rivnut, set through an H-08 stop washer, in the tube wall that faces the joint.
2. The bolt side's edge tube has, on the same axis: a Ø6.6 clearance hole in its joint-side wall, and a Ø11 access hole in the opposite wall, which faces into its own frame bay.
3. The factory pushes the M6 bolt in through the Ø11 hole, tip first, and fits the H-02 retainer. The Ø10 head passes the Ø11 hole. The bolt sits back with its tip flush with the joint face while the parts are brought together.
4. On site, the 5 mm key reaches through the bay (through its fill pocket, section 2.3) and the Ø11 hole into the bolt's socket. The bolt runs into the rivnut, its head seats on the inside of the joint-side wall, and the joint closes onto the stop.

**Why:** F1 (no room on the room side), REQ-ASM-03 (one tool, captive bolts), REQ-ASM-04 (the part is located before the bolt goes in), and access from inside before the cassettes go on (LAY §5).

**Stack check for M6 × 16** (calculation; tube wall 1.2 per D-34 and D-54; rivnut per SHX):

| Step | Value | Status |
|---|---|---|
| Joint-side wall of the bolt-side tube | 1.2 | confirmed (D-54) |
| Stop between the faces: stop washer 1.5 + rivnut head 0.76 | **2.26** (2.13–2.39) | calculation (head source SHX; washer assumption) |
| Bolt beyond the bolt-side wall's outer face: 16 − 1.2 | 14.8 | calculation |
| Rivnut's far end from that face: 0.76 head + 10.16 installed length (max) | 10.92 at most | calculation (SHX) |
| Bolt runs past the rivnut's far end, so every thread is engaged | 3.9 at least; 3.5 with the bolt's length tolerance (js15, ±0.35 at 16; unverified) | calculation |
| Tip beyond the nut-side wall's outer face: 14.8 − 2.26 | 12.5 | calculation |
| Tip clearance in a nut-side tube 20 deep along the bolt (far inner face 18.8 from its outer face) | 6.3 | calculation |
| Tip in a 40-deep tube, a 40 × 40 member, the base band or the decor block | 26 or more | calculation |
| Head inside a bolt-side tube 20 deep: head height 6 in an inner width of 17.6 leaves 11.6 for the key to enter | 11.6 | calculation |
| Bolt and head, 22 long, fit in the 20 mm tube when pulled back: the head stands 2 out of the access hole into the pocket | 2 | calculation |

**Gasket squeeze:** (3.18 − 2.26) / 3.18 = **29%** nominal (calculation). With the stop at 2.13–2.39 and the gasket at 3.18 ±0.32 (assumption: ±10%), the squeeze stays between 17% and 39%. Target 25–50% (assumption; PORON's compression-set figure is quoted at 50%, ASTM D3574 D). The low end (thick gasket, high stop) is the case T-05 watches.

### 2.3 Access pockets

In the wall panels, next to each site bolt, the factory leaves the 40 mm PET fill out of a pocket **60 × 60 mm** (assumption: room for a hand-held key at the 11 mm hole) in the bolt side's bay. The cassette covers it later. The ceiling halves need no pockets: their fill rides on the ceiling cassette (D-24), so their bays are empty until the cassettes go on. 76 pockets of 0.0036 m² at most is 0.27 m², under 2% of the roughly 15.8 m² of wall and ceiling panels (calculation; panel sizes from SKL). The effect on sound isn't modelled; the wall sample is built with pockets (test T-06).

### 2.4 Edge members at the 90° joints

From the skeleton envelopes (SKL P03: `outer_t` 43 = ACP 3 + frame 40; frame tubes 20 × 40 with the 40 through the wall; D-55: the back wall and ceiling frames span between the side frames at X ±1207, and the side skins cover their edges):

| Joint | Edge member of the panel whose skin covers the corner | The other panel's edge tube | Overlap of the faces that touch | Status |
|---|---|---|---|---|
| Back corner (J-WALL-02) | Side panel's back member: Y +830 to +850 (20 wide), X −1247 to −1207 | Back panel's outer member: X −1207 to −1187, Y +807 to +847 (40 deep) | Y +830 to +847 = **17** | calculation |
| Side wall to ceiling (J-CEIL-01) | Upper side panel's top member: Z 2380 to 2400 | Ceiling's side member: Z 2357 to 2397 | Z 2380 to 2397 = **17** | calculation |
| Back wall to ceiling (J-CEIL-01; the back wall reaches Z 2357, R-J4) | Ceiling's back member: Y +830 to +850 | Back panel's top member: Y +807 to +847 | Y +830 to +847 = **17** | calculation |

With 17 mm, the bolt has to sit at the overlap's middle (Y +838.5 at the back corner). The rivnut hole (Ø9.53) is then 3.7 mm from the side of the 20 mm face, the Ø20 stop washer doesn't fit on it at all, and the Ø11 access hole in the other tube comes within 1.8 mm of the inside of that tube's back wall (inner face at Y +845.8). **With a 40 × 40 × 1.2 member (DECIDED, R-J3)**, Y +810 to +850, the overlap is 37 mm and the bolt sits at Y +828: the rivnut hole is 13 mm from the nearest side of the 40 mm face, the stop washer fits (Y +818 to +838), and the access hole is 12 mm from the other tube's back wall (calculation). The member weighs 0.503 kg/m against 0.373 (calculation, aluminium at 2.70 g/cm³ as in SEL A4). Lengths: 4 side back members × 1145, 2 upper side top members × 1495, 2 ceiling back members × 1207: **+1.29 kg** (calculation).

### 2.5 Seals

Every site joint carries one H-04 gasket strip, 10 mm wide, on the nut-side face, with a Ø22 hole around each stop washer (ISS-003 asks every joint to name its seal). Line load at 25% squeeze: 41 kPa × 10 mm = **0.41 N/mm** (calculation from SEL D); at the nominal 29% it's a little more. With one bolt every 400 mm the seam needs about 164 N per bolt; at 452 mm, about 185 N (calculation).

The edge tubes bend between bolts under that load. For a 20 × 40 × 1.2 tube bent across its 20 mm depth, I = 9 584 mm⁴ (calculation); E = 69 000 MPa (assumption: typical of 6000-series aluminium; the alloy is open, ISS-034, HOLD-09). Fixed at the bolts, a tube deflects 0.041 mm between bolts 400 apart and 0.066 mm at 452 (calculation). Two tubes give at most 0.13 mm against the 0.9 mm squeeze, so the seal stays even along the seam. That is why **one bolt per frame bay (400 mm, D-34) is enough for the seal**; strength needs fewer (section 2.6).

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

What they give at the joints (calculation): LC2 on a wall spanning 2.29 m from the base band to the ceiling gives 0.26 kN/m at the base and 0.24 kN/m at the top; at one bolt per 400 mm that's about **105 N per base bolt and 95 N per top bolt**. The door's own weight (LC1) puts a 274 N·m moment on DL, a couple of 152 N between hinges 1.8 m apart (hinge spacing: assumption); LC3 adds 705 N·m, another 391 N. These are small next to the bolt's 11.6 kN proof load. **The weak link is the rivnut in the 1.2 mm tube**, which has no published strength (SHX, SEL A5), so every joint's strength is shown by test T-03 (section 5), not by a catalogue number (guideline §8.1).

The wall works as a plate held on its edges (base, top, corner and decor joints) and across its seam. How the moment from LC2 shares between the seam and the edges needs the panel's own calculation or the wall sample's push test (T-05); it isn't settled here.

### 2.7 Tolerance and adjustment, common to all joints

- **Locating:** two H-05 spigots per horizontal seam, per wall on the base band, and per ceiling half on the back wall's top. The back corners and the vertical seams need none of their own: both panels already stand on base band spigots. One spigot hole is Ø8.5, round; the other a slot 8.5 wide × 14 long along the joint, so frame-length errors can't jam (PROPOSED; sizes assumption until the frame tolerances are set).
- **Bolt clearance holes Ø6.6** (ISO 273 medium series for M6; unverified, from memory) give ±0.3 mm of float at each bolt; the spigots carry the rest.
- **The gap is set by metal stops** (stop washer and rivnut head, 2.26), not by torque, so a joint closes to the same gap however hard it's tightened (2.2, 2.8).
- **Frame flatness at a joint face:** ±0.5 mm over a seam (assumption; set in the frame drawing with the maker's capability, guideline §6.3). The gasket takes up its squeeze range.
- **Room floor:** ±5 mm over the footprint (ISS-054, assumption), taken up by the 8 glides under the base band (LAY B-GLIDE), set from above with the same 5 mm key before any wall goes on.
- **Torque:** HOLD-01 (D-48). These joints only need to be snug: a seal needs at most about 185 N per bolt (2.5), so the torque only has to close the joint onto its stop. It's set from the spin-out test with a margin (T-02).

### 2.8 Seam gaps for the skeleton (answer to F-001)

Every site joint closes onto the same stop, so **the compressed gasket thickness, and the gap between the two frames, is 2.26 mm at every seam** (calculation: stop washer 1.5, assumption, plus rivnut head 0.76 ±0.08, source SHX; range 2.13–2.39). Proposed skeleton parameter: `seam_gap` = 2.26 mm, status calculation, source this section.

| Seam | Interface | Direction of the gap | Compressed gasket = gap |
|---|---|---|---|
| Side wall horizontal seams, L1–L2 and R1–R2 | IF-04 | Z | 2.26 |
| Back wall horizontal seams, B1–B3 and B2–B4 | IF-04 | Z | 2.26 |
| Back wall vertical seams, B1–B2 and B3–B4 | IF-04 | X | 2.26 |
| Back corners, side panels to B1–B4 | IF-03 | X | 2.26 |
| Walls on the base band (L1, R1, B1, B2) | IF-01 | Z | 2.26 |
| Side walls to the ceiling, L2–C1 and R2–C2 | IF-05 | X | 2.26 |
| Back wall to the ceiling, B3–C1 and B4–C2 | IF-05 | Z | 2.26 |
| Ceiling halves, C1–C2 | IF-06 | X | 2.26 |
| Decor blocks to the side walls, DL–L1/L2 and DR–R1/R2 | IF-07 | Y | 2.26 |

What it does to the panel sizes (calculation; the skeleton owner applies them):

| Panel | Was (P03) | With the gaps | How |
|---|---|---|---|
| Back panels B1–B4, width | 1207 | **1203.61** | (2414 − 3 × 2.26) / 2: two corner gaps and the centre seam (F-001's formula) |
| Ceiling halves C1, C2, width | 1207 | **1203.61** | (2414 − 3 × 2.26) / 2: two side gaps and the centre seam |
| Side panels L1, L2, R1, R2, height | 1145 | **1142.74** | (2290 − 2 × 2.26) / 2: the gap on the band and the horizontal seam; L2's top stays at Z 2400 |
| Back panels B1–B4, height | 1104.5 | **1120.11** | (2357 − 110 − 3 × 2.26) / 2: the gap on the band, the horizontal seam and the gap under the ceiling, with the back wall reaching Z 2357 (R-J4) |
| Side panels, length along Y | 1495 | **1492.74** | 1495 − 2.26: the gap at the decor's back plate (Y −645); the outer face stays at Y +850 |
| Walls on the band | Z 110 | **Z 112.26** | 110 + 2.26 |

Two notes for the Fusion Engineer: the outside reveal between two skins is the 2.26 gap plus the skins' setbacks from their frame edges, which the WALL drawing sets for the look (D-23); and the D-49 depth of 1495 now means "1492.74 of panel plus the 2.26 gasket gap at the decor".

## 3. Joint entries

Each entry has the guideline's fields (§8): parts, function and load path, loads, take-down, options compared, choice and reason, parts and process, calculation and tolerance stack, assembly direction, tool and step, what can go wrong, how it's checked, and status.

### 3.1 J-WALL-01: wall to wall, seams inside one wall (IF-04)

| Field | Entry |
|---|---|
| Parts | Horizontal seams: L1–L2, R1–R2 (side panels), B1–B3, B2–B4 (back panels). Vertical seams: B1–B2, B3–B4. Sizes in 2.8. |
| Function and load path | Keeps the outside faces flush so the reveals stay crisp (D-23); carries shear across the seam, in the wall's plane (racking) and out of it (LC2); seals the seam. Horizontal seam: the upper panel's bottom tube sits on the lower panel's top tube. Vertical seam: B2's (or B4's) left tube sits against B1's (or B3's) right tube. Load: bolt → rivnut → the lower or left panel's tube wall. |
| Loads | LC2: about 95 N per bolt across the seam (2.6). Seal: 164–185 N per bolt (2.5). LC1: the upper panel's weight, about 110 N, sits on the lower panel through the stops. |
| Take-down | Yes, 5 cycles (REQ-ASM-09); the bolts back out and stay captive. |
| Options compared | (a) Tool-free hook or wedge connector (the layout study's assumption): no rated part, and the panel's weight gives a sixth of the seal force (2.5). (b) Room-side draw latch: no room in the 4 mm gap (F1). (c) **Captive in-member M6 bolt (chosen).** (d) Glue or rivets on site: not allowed (REQ-ASM-05). |
| Choice and reason | (c): it gives the seal force against a metal stop, uses only parts with data (H-01, H-03), and needs only the one key. **DECIDED (R-J1).** (a) can still go on the wall sample as an experiment (T-07). |
| Nut side and bolt side | Nut side: the lower panel (horizontal seams) or the left panel, B1 or B3 (vertical seams). Rivnuts with stop washers in the top face (40 mm) of the lower panel's top tube, or in the +X face (40 mm) of B1's or B3's right tube; H-04 strip on that face; 2 H-05 spigots per horizontal seam. Bolt side: the upper panel's bottom tube (access hole in its top wall, from the bay above it), or B2's or B4's left tube (access hole in its +X wall, from its bay). All factory-fitted. |
| Bolt count and pitch | One bolt per frame bay, at the bay's middle: side horizontal seams 4 each (1495 / 400, rounded up); back horizontal seams 3 each (1207 / 400); back vertical seams 3 each, at 100 from each end and at mid-height, so about 460 apart (calculation, on the 1120 panel height). **20** for the pod. |
| Calculation and stack | Stack 2.2 (tip clearance 6.3 in a 20-deep nut-side tube). Seal 2.5 (tube deflection at most 0.066 mm per tube at 452, about 0.07 at 460). |
| Assembly direction, tool, step | Horizontal: the upper panel is lowered onto the lower one, spigots into the hole and the slot. Vertical: the second back panel stands on its base band spigots beside the first (LAY step 4). Bolts driven from inside through the bolt side's bay pocket with the 5 mm key, before the cassettes go on (LAY steps 4, 5 and 11). Bolts at 2.2 m need the step stool (LAY). |
| What can go wrong | The rivnut spins or pulls out (T-02, T-03); the key can't reach (pocket missing or fill in the way, T-06); the outside faces step at the seam (spigot fit, T-05); the gasket squeeze drops toward 17% with a thick gasket and a high stop (T-05). |
| Check and pass mark | T-02, T-03, T-05, T-06 (section 5). Pass: no spin at the set torque; faces flush within 0.5 (assumption) after 5 cycles; seam gap 2.26 ±0.15 everywhere (calculation). |
| Status | DECIDED fastener (R-J1, R-J2); details PROPOSED. HOLD-01, -02, -05. |

### 3.2 J-WALL-02: back corner, side wall to back wall (IF-03)

| Field | Entry |
|---|---|
| Parts | BL corner: L1–B1, L2–B3. BR corner: R1–B2, R2–B4. |
| Function and load path | Closes the box at the back corners: racking between side and back walls, the back wall's out-of-plane load into the side walls (LC2), position, seal. The side panels' ACP covers the back panels' edges (D-55, BP-25). Load: the back panel's outer tube → bolt → rivnut in the side panel's back member. |
| Loads | LC2 on the back wall: 0.24–0.26 kN per metre of edge (2.6), about 105 N per bolt with 3 bolts per panel height. Seal: about 185 N per bolt. |
| Take-down | Yes, 5 cycles. |
| Options compared | (a) A bolt in the 17 mm overlap: the rivnut, its washer and the access hole land on tube corners (2.4). (b) A room-side corner angle: no room in the 4 mm gap, and the side panel has no tube face in front of the back panel (F1, 2.4). (c) Tool-free hooks in the overlap: 2.5 mm margins in 17 mm, and no seal force (F3). (d) **A 40 × 40 side back member with an in-member bolt (chosen).** |
| Choice and reason | (d): it makes room for the standard bolt, rivnut and washer, and keeps one fastener type; +0.59 kg for the four corner members (calculation, 2.4). **DECIDED (R-J1, R-J3).** |
| Nut side and bolt side | The back panels go on first, then the sides (LAY step 4). Nut side: the side panel's back member, 40 × 40 × 1.2 (Y +810 to +850), with rivnuts and stop washers in its room-side face (X ∓1207) at Y +828 and the H-04 strip on that face. Bolt side: the back panel's outer tube (B1's left, B2's right), with Ø6.6 in its X ∓1207 wall and Ø11 in its X ∓1187 wall at Y +828. The back panel stands with its bolts pulled back flush; the side panel then goes on, and the bolts are driven from the back panel's bay. |
| Bolt count | 3 per panel height (100 from each end, and the middle): 6 per corner, **12** for the pod. |
| Calculation and stack | Stack 2.2 (nut side 40 deep: tip clearance 26 or more). Overlap 37 (2.4). |
| Assembly direction, tool, step | The side panel is lowered onto its base band spigots against the back panel's edge; the bolts go in along X from inside the back panel's bay pocket, 5 mm key (LAY steps 4 and 5). |
| What can go wrong | The base band spigots hold the side panel 0.5 mm off the back panel's edge: the spigot slot at that end must run along X (2.7). The outside corner shows the side member's back face (Y +850, 43 wide with the ACP edge): it needs the side skin's return or a trim; that's a WALL drawing detail (section 7, item 1). |
| Check and pass mark | T-02, T-03, T-05, T-06; T-09 for the corner. Pass as J-WALL-01. |
| Status | DECIDED fastener and member (R-J1 to R-J3); details PROPOSED. HOLD-01, -02, -05. |

### 3.3 J-BASE-01: wall to base band, the wall-to-floor joint (IF-01)

| Field | Entry |
|---|---|
| Parts | The bottom tubes of L1, R1, B1 and B2 on the base band pieces BAND-L, BAND-R and BAND-BACK (100 × 40, on 10 mm glides, SKL; LAY B-BAND). The thin floor lies loose inside the band (LAY step 3) and isn't part of this joint. |
| Function and load path | Carries the walls' and roof's weight to the band and through the glides to the room floor; locates the walls; takes the base share of LC2 and racking; seals the wall to the band. Weight: the wall's bottom tube → stop washers and gasket → band top → glides. |
| Loads | LC1: about 0.34 kN per metre for a side wall with its cassettes and a third of a ceiling half (calculation from the LC1 masses). LC2: about 105 N per bolt (2.6). |
| Take-down | Yes, 5 cycles. |
| Options compared | (a) A room-side angle from the band to the wall: clashes with the lower cassette, which starts at the wall's bottom (SKL), in the 4 mm gap (F1). (b) Spigots only, no bolt: nothing holds a panel down while the next one goes on, and nothing squeezes the gasket. (c) **In-member bolts down through the wall's bottom tube into rivnuts in the band's top wall (chosen).** |
| Choice and reason | (c), with two spigots per panel so each wall stands on its own before its bolts go in (REQ-ASM-04). The 14 bolts match the layout study's count for this step (LAY §5 step 4). PROPOSED. |
| Nut side and bolt side | Nut side: the band's top wall, with 2 H-05 spigots per panel and rivnuts with stop washers at each bay middle, on the wall tube's centre line (X ±1227 or Y +827, which is 3 mm off the band's own centre line, calculation from SKL). The band's top wall must be inside the grip with the washer: 0.70–4.20 minus 1.5, so **2.7 mm or less** (**HOLD-07**: the band section isn't chosen). H-04 strip on the band top. Bolt side: the wall's bottom tube, with the spigot hole and slot, Ø6.6 in its bottom wall and Ø11 in its top wall for each bolt. H-06 base seal under the band (HOLD-06). |
| Bolt count | L1 and R1: 4 each; B1 and B2: 3 each. **14.** |
| Calculation and stack | Stack 2.2 (the band is open inside, so the tip has well over 20). |
| Tolerance and adjustment | The band is levelled on its 8 glides with the same key before any wall goes on (2.7; LAY step 2). The walls stand 2.26 above the band (2.8). The ACP's outer face stays flush with the band's outer face at X ±1250 and Y +850 (SKL), so the frame overhangs the band by 3 mm on the inside (calculation: band 40, panel 43). |
| Assembly direction, tool, step | The wall is lowered onto the band spigots; the bolts are driven down from inside through the pocket in the wall's bottom bay, 5 mm key (LAY step 4). |
| What can go wrong | The band's top wall too thick for the rivnut and washer (HOLD-07); the band's notch for DR (SKL P03 lists DR 8 mm into BAND-R, a HOLD for the base design); a 10 ± 5 mm gap the base seal can't close (HOLD-06). |
| Check and pass mark | T-02, T-03, T-05, T-06, T-08. Pass as J-WALL-01, plus the base seal touching the floor all the way round on a ±5 mm floor (assumption). |
| Status | DECIDED fastener (R-J2); details PROPOSED. HOLD-01, -02, -05, -06, -07. |

### 3.4 J-CEIL-01: wall to ceiling (IF-05), and J-CEIL-02: ceiling half to ceiling half (IF-06)

| Field | Entry |
|---|---|
| Parts | Side edges: C1 to L2, C2 to R2. Back edges: C1 to B3, C2 to B4. The C1–C2 seam at X 0. |
| Function and load path | Carries the roof (outer panels, cassettes) to the walls; ties the box together at the top (racking); seals. The side panels' ACP covers the ceiling's edges (D-55). Side edges: the ceiling's side tube → bolt → rivnut in the upper side panel's top member (40 × 40), in shear. Back edge: the ceiling's back member sits on the back wall's top tube, which reaches Z 2357 (R-J4), and is bolted to it. |
| Loads | LC1: a ceiling half's outer panel about 9.6 kg plus its cassette about 16 kg hanging from it (calculation, 2.6): about 250 N per half, under 40 N per bolt if shared evenly over its 4 side and 3 back bolts (calculation). LC2 at the top: about 95 N per bolt (2.6). Seal: 164–185 N per bolt. |
| Take-down | Yes, 5 cycles. Overhead work from the step stool (LAY step 6). |
| Options compared | As J-WALL-02: both edges overlap only 17 mm with 20 × 40 tubes (2.4). A ledge under the ceiling's side tube was also looked at: it would sit in the 4 mm gap above the side lining (D-57), which leaves no room. |
| Choice and reason | In-member bolts, with the upper side panels' top members and the ceiling halves' back members at 40 × 40 (R-J3). Two people lift a half into place from inside (LAY step 6): its back edge drops onto 2 spigots on the back wall's top tube (REQ-ASM-04), its side tube lies against the side wall, and they hold its front edge until the first side bolts are in. DECIDED fastener (R-J1 to R-J3); details PROPOSED. |
| Nut side and bolt side | **Side edges:** nut side the wall: rivnuts and stop washers in the upper side panel's top member (room-side face, 40 × 40, at Z 2378); bolt side the ceiling's side tube (access hole in its inner wall, reached from below through the ceiling's open bay). **Back edges:** nut side the ceiling: rivnuts and stop washers in the bottom face of the ceiling's 40 × 40 back member, at Y +828; bolt side the back panel's top tube (Ø6.6 in its top wall, Ø11 in its bottom wall, reached from the pocket in the back panel's top bay). Its bolts are pulled back flush while the ceiling goes on, then driven up. The ceiling's back member can't be the bolt side: its access hole would face the roof skin. **C1–C2:** nut side C1 (rivnuts in its right tube's +X face, 40 mm), bolt side C2's left tube, reached through C2's open bay. |
| Bolt count | Side edges 4 each; back edges 3 each: **14** (the layout study's count for this step, LAY §5 step 6). C1–C2: **4**. |
| Calculation and stack | Stack 2.2. Side and back edges: the nut side is a 40 × 40 member, tip clearance 26 or more. C1–C2: nut side 20 deep, tip clearance 6.3. |
| What can go wrong | The ceiling cassettes and their catches (J-LIN-01) hang on the same ceiling tubes, so those tubes carry both. |
| Check and pass mark | T-02, T-03; the ceiling isn't in the wall sample, so its joints are checked on the corner mock-up (T-09) or the prototype. |
| Status | DECIDED fastener and members (R-J1 to R-J4); details PROPOSED. HOLD-01, -02, -05. |

### 3.5 J-FRONT-01: decor block to wall (IF-07)

| Field | Entry |
|---|---|
| Parts | DL to the left wall's front edge (L1, L2); DR to the right wall's front edge (R1, R2). They meet at Y −645, the decor's back plate against the side walls' front members (D-49), with the 2.26 gasket gap (2.8). |
| Function and load path | Holds DL and DR upright against the side walls, carries the door's moment from DL into the left wall (IF-07, ISS-045), and seals the decor to the wall. Weight goes down through the decor block onto the base band (DL stops at Z 110 on the band, D-57; DR's notch is a base HOLD). Moment: hinges → DL's core frame → back plate → bolts → the left wall's front member. |
| Loads | The door's own weight: a 152 N couple between hinges 1.8 m apart (assumption); misuse (LC3): 391 N more (calculation, 2.6). These go into the wall through 6 bolts per side; the top and bottom bolts take most of it. ISS-045 asks for the full load-path calculation with the decor core frame's size; this entry gives only the joint's share. |
| Take-down | Yes, 5 cycles. DR is also opened from inside for fan service (D-59), which doesn't touch this joint. |
| Options compared | (a) The build plan's V brackets with steel screws (BP-29; SEL A7 picks Simpson ABR7015): a room-side bracket would sit under the side lining, which starts at Y −645 (SKL), in the 4 mm gap (F1); screws aren't the M6 bolt (REQ-ASM-02). (b) Bolts from inside the decor block into the wall: DL has the hinge pocket and no access panel yet. (c) **In-member bolts from the side wall's front bay into rivnuts in the decor's back plate (chosen).** |
| Choice and reason | (c): the same principle as every other joint, reached from inside the pod; the ABR7015 bracket isn't needed for this joint (it may still serve inside the decor block: FRONT's call). DECIDED fastener (R-J2); details PROPOSED. |
| Nut side and bolt side | The walls go up first, then the decor blocks (LAY §5). Nut side: the decor block: rivnuts with stop washers in its back plate. **Requirement for FRONT (HOLD-10):** at each bolt the back plate is aluminium 1.0–2.7 mm thick (2.7 so the grip with the washer stays inside 4.20, SHX; 1.0 as a minimum for strength, assumption), with the core frame close enough behind to carry the load; a local aluminium pad does if the plate is something else. Bolt side: the side panel's front member (20 deep along Y), with Ø6.6 in its front wall and Ø11 in its back wall, reached from the pocket in the side panel's front bay. |
| Bolt count | 3 per side panel (100 from each end, and the middle): 6 per block, **12**. |
| Calculation and stack | Stack 2.2: the tip runs into the hollow decor block. |
| What can go wrong | The back plate isn't aluminium of the right thickness at the bolts (HOLD-10); rivnut pull-out under the door misuse moment (T-03 at the DL load); DL's hinge pocket weakens its frame (ISS-045). |
| Check and pass mark | T-03 at the DL load (about 1.6 kN, assumption: 3 × the top bolt's share of 152 + 391 N); the door sample (SEL sample test 5) with DL bolted to a wall piece. |
| Status | PROPOSED; HOLD-01, -02, -05, -10; ISS-045 open (FRONT). |

### 3.6 J-LIN-01: lining cassette clips (IF-10)

| Field | Entry |
|---|---|
| Parts | Each wall cassette (L1, L2, R1, R2 and B1–B4 cassettes) and ceiling cassette (C1 and C2 cassettes) to its outer panel's frame. |
| Function and load path | Hangs the cassette on the frame without any screw through it, so the inner leaf floats (D-17); holds it under its own weight and knocks; ceiling cassettes can't drop (D-47); hook-and-loop only lines it up. Load: tray → clip → frame tube. The perimeter gasket (PORON 3.2 mm in the 3–4 mm gap, HW §1 layer 5) seals the cassette's edge and carries no load. |
| Loads | Per clip (SEL A8, the Hardware Engineer's calculation, safety factor 3 as an assumption): a wall cassette, 10.3 kg on 4 clips, needs 7.7 kg rated in shear per clip; a ceiling cassette, about 16 kg on 6 clips, needs 8.0 kg rated in pull-out per clip; the ceiling catch needs 48 kg per lanyard, 2 lanyards. |
| Take-down | Yes: cassettes lift off with no tools (HW §8); 5 cycles. |
| Options compared | SEL A8: Häfele KEKU EH (candidate; its rating basis, pull-out rating, captive lock and a fixing to a 0.5 mm tray aren't stated); hook-and-loop alone (no load rating; locating only). |
| Choice and reason | **HOLD (D-56, ISS-076).** This register sets what the clip must meet, so CAD can reserve its space: (1) the rated loads above; (2) captive: it can't unhook without a deliberate lift (D-47); (3) it fits the 4 mm frame-to-tray gap, or sits on the tray's 25 mm returns at the cassette's edge, and clears the site bolts' Ø11 access holes and the pockets; (4) it fixes to the 0.5 mm tray return and to a frame tube's 20 mm face with small rivnuts or blind rivets, never through the ACP; (5) it's soft enough not to bridge the floating leaf (HW §10: clip stiffness unknown); (6) the ceiling catch anchors to a ceiling tube, which is 20 × 40 now, not the 20 × 100 that SEL A8 names (ISS-079). |
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

Not counted here: the base band's corner keys, the door hinges, the fixed glass profiles and DT to the ceiling. The layout study's decided build had 76 bolts and 38 tool-free connectors in all; with R-J1, the 36 seam and corner connectors here become bolts (calculation).

## 4. Tolerance stacks at the joint faces

Worst case, not RSS: there are no process data yet (guideline §6.3). All values in mm; frame tolerances are assumptions until the frame drawing and the maker's capability set them.

| Stack | Contributors | Worst case | Result | Status |
|---|---|---|---|---|
| Bolt in its clearance hole across two parts | Hole position ±0.2 in each part (assumption, CNC); hole Ø6.6 on a Ø6 bolt, 0.3 a side | 0.4 against 0.3 | Can bind by 0.1 at worst. So the **spigots locate, and the bolt holes are positioned from the spigot holes**: at ±0.15 in each part the bolt always enters (calculation) | calculation; the frame drawing sets ±0.15 at the joint holes (PROPOSED) |
| Spigot in its hole and slot | Spigot Ø8 h9, hole Ø8.5 H11 (assumptions); positions ±0.15 in each part | 0.5 clearance against 0.3 | Always enters; leaves up to ±0.25 of float, which the bolts take up | calculation |
| Outside faces flush across a seam | Frame depth 40 ±0.3 a panel (assumption); bond line 3 ±0.5 (bond spec); ACP 3 ±0.2 (assumption) | ±1.0 a panel, up to 2.0 between two | **Too much for a crisp reveal.** So the outer panels are bonded face down on a flat table, with the ACP face as datum A (bond spec §5). The frame and the bond line then don't set the face: ±0.2 (ACP) and ±0.3 (table) a panel, up to 1.0 between two | calculation; PROPOSED rule: the ACP face is datum A of every outer panel |
| Seam gap and gasket squeeze | Head 0.76 ±0.08 (SHX); washer 1.5 ±0.05 (assumption); gasket 3.18 ±0.32 (assumption, ±10%) | gap 2.13–2.39 | Squeeze 17–39%, nominal 29% (2.2) | calculation |
| Panel lengths across the back wall | Two back panels 1203.61 each, three gaps 2.26; frame length ±0.5 each (assumption) | ±1.0 | The gaps don't change: each joint closes onto its rigid stop. The error moves the side walls along X instead, which the X-direction slot at the side panel's band spigot takes: slot 14 on a Ø8 spigot gives ±3 (calculation). A 1 mm shift of a side wall's outer face is not visible (assumption) | calculation |
| The lining floats clear of the frame at the bolts | Gap 4 (SKL, assumption); nothing proud of the frame's room-side face (every head is inside the tubes, 2.2) | 4 | Clear by design; the clip's own height is HOLD-08 | calculation |

## 5. Tests in the wall sample, and two joint samples

Physical tests stay PLANNED until real data exists (guideline §10). The factory's wall-and-door sample is the physical check (D-32). These add to the hardware selection's sample tests 1–5; they don't replace them.

| Test | What | Sample | Pass mark | Status |
|---|---|---|---|---|
| T-01 | Setting the CAH3-610-4.2 through the 1.5 mm stop washer in the real 20 × 40 × 1.2 tube, in a 40 mm face; the bulge clears the inside (Sherex asks for trial installations, SHX) | 10 rivnuts in an offcut | Sets flush on the washer, washer clamped, no cracks, bulge clear | PLANNED |
| T-02 | Spin-out torque (SEL sample test 2, D-48) | 10 rivnuts in an offcut | Sets the tightening torque with a margin; the torque goes in the assembly guide | PLANNED |
| T-03 | Pull-out and shear of a whole joint: M6 × 16 through a bolt-side tube into a rivnut in a nut-side tube, with 20-deep and 40-deep nut-side tubes | 5 of each | Failure at 3 × the joint's highest bolt load or more (assumption: about 0.6 kN for the walls, 1.6 kN for DL), and no loss of fit after 5 assemble-and-strip cycles (REQ-ASM-09) | PLANNED |
| T-04 | Captive retainer: the bolt stays in its tube when the panel is shaken, carried and turned over; it runs forward and backs out 5 times | 5 | Doesn't fall out; push-off force at least 3 × the bolt's weight (assumption) | PLANNED, after HOLD-02 |
| T-05 | Seam gap, flushness and gasket squeeze on the wall sample's seams; push test at 1.2 m with the LC2 load | wall sample | Gap 2.26 ±0.15 at every bolt; faces flush within 0.5 (assumption); no step after the push | PLANNED |
| T-06 | Access: a person drives every bolt of the wall sample with the 5 mm key through the pockets, cassettes off, then clips the real cassettes on; timed | wall sample | Every bolt reached; the time goes in the assembly guide | PLANNED |
| T-07 | Experiment (no gate): a tool-free wedge hook on one vertical seam with a low-force seal, next to a bolted seam | wall sample | Seam squeeze and sound compared with the bolted seam, for later versions (R-J1 stands for v2) | PLANNED, optional |
| T-08 | Base seal on a floor stepped ±5 mm | base band piece | Touches all the way along; checked with a light from inside | PLANNED, after HOLD-06 |
| T-09 | Corner mock-up: one side panel corner, one back panel edge and one ceiling corner, bolted | joint sample | Bolts reached and driven, overhead too; corner faces flush within 0.5 | PLANNED |

## 6. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Owner | Released when |
|---|---|---|---|---|
| HOLD-01 | Rivnut tightening torque (D-48, ISS-011) | None: the spin-out test sets it (T-02) | Hardware Engineer | T-02 recorded and the PM lifts it |
| HOLD-02 | Captive retainer (H-02) | Which push-in retainer holds an M6 bolt in an 11 mm or 6.6 mm hole in 1.2 mm aluminium, with what push-off force, and lets it be driven and backed out 5 times? | Joints Engineer with the Hardware Engineer | Part named with data; T-04 passed |
| HOLD-03 | Rivnut head thickness and installed length | — | — | **Closed**: Sherex's page gives head 0.76 ±0.08 and installed length 10.16 max (SHX) |
| HOLD-04 | Rivnut edge distance in a 20 mm tube face | To Sherex: the minimum distance from the Ø9.53 hole to the edge of a 1.2 mm wall. Every site-joint rivnut is in a 40 mm face (15.2 mm, calculation); only a clip fixing might use a 20 mm face (5.2 mm) | Hardware Engineer | Answer on file, or T-01 shows no cracking |
| HOLD-05 | Gasket converter and strip (SEL D) | PORON 4701-40 with adhesive in 10 mm strips, 3.18 mm thick, with Ø22 holes at the rivnuts | Hardware Engineer | The converter's strip data on file |
| HOLD-06 | Base seal for a 10 ± 5 mm gap (H-06) | Which bulb or brush seal closes 5–15 mm under an aluminium band, with a published compression range? | BASE engineer | Part named; T-08 passed |
| HOLD-07 | Base band section: top wall 2.7 mm or less (rivnut grip with the washer), and room for the spigots | None: BASE design | BASE engineer | Band drawing with its wall thickness |
| HOLD-08 | Cassette clip and ceiling catch (D-56, ISS-076) | SEL question 10 (Häfele: KEKU EH rating basis, pull-out, a captive version, a fixing to a 0.5 mm tray; a rated lanyard), plus points 3–6 of J-LIN-01 | Hardware Engineer; Layout Engineer | Part with its ratings; SEL sample test 4 passed |
| HOLD-09 | Frame tube alloy, temper and E (ISS-034) | None: hardware selection | Hardware Engineer | Alloy named; section 2.5 re-checked with its E |
| HOLD-10 | Decor back plate at the J-FRONT-01 bolts: aluminium 1.0–2.7 mm, with the core frame behind (ISS-045) | None: FRONT design | FRONT engineer | FRONT CAD shows what takes each J-FRONT-01 rivnut |
| HOLD-11 | The back wall's top edge under the ceiling (F5) | — | — | **Closed**: R-J4, the back wall's outer frames run up to Z 2357 (Fusion Engineer 2) |

## 7. Still open for others

1. **The outside corner at the back, for the WALL drawing:** the side panel's back member face (Y +850, 43 wide with the ACP edge) shows from behind. The side skin returns around it or a trim covers it, without changing the look (D-01).
2. **The decision log, for the control pack:** rows for R-J1 to R-J4, and the replaced part of D-08 (tool-free seam clips).
3. **The skeleton, for Fusion Engineer 2:** `seam_gap` = 2.26 and the panel sizes in 2.8; the 40 × 40 edge members (FR-06).

## 8. Feature-rationale inputs for the Fusion Engineer

What each joint puts into each sample part, and why (guideline §7). Sizes are PROPOSED unless marked, with the status shown; positions follow the rules, and the Fusion Engineer places them on the real frame. "Nut side" and "bolt side" are as in section 2.2. Hole tags (H01…) go on the drawings, not here. X and Y are the pod axes (conventions §4); on a part drawing they map to the view's X and Y.

| ID | Part (sample set) | Feature | Size | Where (rule) | Why (function and source) | Status |
|---|---|---|---|---|---|---|
| FR-01 | Nut side: lower panels' top tubes; B1's and B3's right tubes; the base band's top wall; the side panels' 40 × 40 back members; the upper side panels' 40 × 40 top members; the ceilings' 40 × 40 back members (bottom face); C1's right tube; the decor's back plate | Rivnut hole, with the H-08 stop washer under the head | Ø9.53 +0.10 through one wall of 2.7 mm or less; washer Ø20 needs a 40 mm face | One per bolt, at the middle of each frame bay along the joint; on the bolt-side tube's centre line (on the band, 3 mm off the band's own centre line) | H-03 needs that hole (SHX); the washer sets the 2.26 gap (2.8); one per bay for the seal (2.5) and the key's reach (2.3) | source (hole size); position PROPOSED |
| FR-02 | Bolt side: upper panels' bottom tubes; B2's and B4's left tubes; the walls' bottom tubes; the back panels' outer tubes at the corners; the ceilings' side tubes; the back panels' top tubes; C2's left tube; the side panels' front members | Clearance hole in the joint-side wall | Ø6.6 | Coaxial with FR-01 | M6 float ±0.3 (2.7) | PROPOSED (Ø6.6 unverified against ISO 273) |
| FR-03 | The same bolt-side tubes | Access hole in the bay-side wall | Ø11 | Coaxial with FR-02 | Passes the Ø10 head and the 5 mm key (ISO4762, 2.2) | calculation |
| FR-04 | Lower panels' top tubes (horizontal seams); the base band's top wall; the back panels' top tubes (B3, B4) for the ceiling | Spigot rivnut | Ø9.53 +0.10 | 2 per joint, about 100 from each end (assumption), not at a bolt | Holds H-05; the part stands located before any bolt goes in (REQ-ASM-04) | PROPOSED |
| FR-05 | Upper panels' bottom tubes; the walls' bottom tubes; the ceilings' 40 × 40 back members (bottom face) | Spigot hole and slot | Ø8.5 round at one end; slot 8.5 × 14 along the tube at the other | Coaxial with FR-04; where a side panel meets the back corner, the slot at that end runs along X | One fixed point and one slot, so frame-length errors can't jam (2.7, 3.2) | PROPOSED (assumption sizes) |
| FR-06 | Side panels' back members (L1, L2, R1, R2); upper side panels' top members (L2, R2); ceiling halves' back members (C1, C2) | Member size | 40 × 40 × 1.2 instead of 20 × 40 × 1.2 | Whole length of that edge | An overlap of 37 instead of 17, so the rivnut, its washer and the bolt fit (F2, 2.4) | DECIDED (R-J3); +1.29 kg (calculation) |
| FR-07 | Back panels' outer tubes at the corners | FR-02 and FR-03 pair, along X | as FR-02 and FR-03 | Y +828 (the middle of the 37 overlap), 3 per panel height | J-WALL-02 (3.2) | calculation |
| FR-08 | Side panels' front members (L1, L2, R1, R2) | FR-02 and FR-03 pair, along Y | as FR-02 and FR-03 | 3 per panel height, centred on the member's 40 mm face | J-FRONT-01 (3.5) | PROPOSED |
| FR-09 | Every panel, ceiling half and decor block at its site joints | Seam gap | 2.26 (2.13–2.39) | Every face pair in 2.8 | The compressed gasket set by the stop (2.2, 2.8; F-001) | calculation |
| FR-10 | Every wall panel bay next to a bolt (bolt side) | Fill pocket | 60 × 60 × 40 deep, no fill | At each FR-03 | The key's reach (2.3) | PROPOSED (assumption) |
| FR-11 | Every nut-side joint face | Gasket strip | 10 wide × 3.18, Ø22 holes at the rivnuts | Centred on the bolt line | Seal at about 29% squeeze (2.2, 2.5; ISS-003) | PROPOSED |
| FR-12 | Frame tubes behind each cassette's clips and the ceiling catch | Clip and catch fixings | HOLD-08 | Not drawn until the clip is released; reserve an envelope marked UNVERIFIED | D-47, D-56 | HOLD |

Rules for the Fusion check (each can be a scripted check on the CAD):

- R1. Every FR-01 has a coaxial FR-02 and FR-03 in its partner, within 0.15 (2.7, section 4).
- R2. No joint hole's edge closer than 10 mm (assumption) to a tube's inside corner; FR-07 is the tight case at 12 mm (2.4).
- R3. Nothing stands proud of a frame tube's room-side face except the clips (F1, 2.2).
- R4. A bolt's tip clears the far wall of its nut-side tube by at least 3 (2.2: 6.3 nominal).
- R5. Every FR-03 in a wall panel has its FR-10 pocket, with no frame member or cable in it.
- R6. Every part that goes on site stands on a locating pair (FR-04 and FR-05) before its first bolt: walls on the band or the panel below, ceiling halves on the back wall (REQ-ASM-04).
- R7. One bolt in the BOM for every site joint: M6 × 16, ISO 4762, 8.8 (REQ-ASM-02, R-J2).
- R8. No clip (FR-12) over an FR-03 hole or an FR-10 pocket.
- R9. Every site-joint face pair is 2.26 apart (FR-09), and every rivnut with its washer sits on a 40 mm face.
