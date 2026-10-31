# Joints register: Spaceship (FocusPod v2), Milestone 2 sample set

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-01 (row in `document-register.csv`) | P01 | DRAFT | 2026-10-31 | Joints Engineer (v2 Milestone 2) |

This is the joint register the guideline asks for (§8, and Milestone 2 item 6), for the site joints of the sample set: wall to wall, wall to floor (base band), wall to ceiling, back corner, decor to wall, the closing seams, and the lining cassette clips. It also gives the feature-rationale inputs (§7) the Fusion Engineers need (section 8), the seam gaps and bolt positions the skeleton needs (sections 2.8 and 2.9), and the closed-chain stacks ST-02 and ST-04 (section 2.11).

- **Status of numbers** (conventions §9): confirmed, source, calculation, assumption, unverified. Every number below carries one.
- **Status of choices:** DECIDED where the PM has ruled, citing the ruling; every other choice is **PROPOSED**: the work goes ahead on it until the PM rules (`AGENTS.md`).
- **PM rulings used here** (joints group, 2026-10-31; the control pack logs them in `decision-log.md`):
  - **R-J1** captive bolts on seams and corners, replacing D-08's tool-free seam clips;
  - **R-J2** socket heads to ISO 4762 throughout, one 5 mm key for the whole pod;
  - **R-J3** 40 × 40 corner edge tubes, accepting about 1.3 kg;
  - **R-J4** the back wall's outer frames run up to the ceiling frame;
  - **R-J5** (F-008) one seam gap, 2.26 mm, at every stopped seam, including the walls on the base band (IF-01) and the decor back plate (IF-07); this changes D-49's "face to face";
  - **R-J6** (F-009) bolt clearance holes Ø7.0, positioned to Ø0.4 (±0.2) from the spigot hole, by CNC or a drill jig;
  - **R-J7** (Reviewer 7, P2-1) the gasket runs beside the washer line, about 8 mm wide, so the seal is never cut;
  - **R-J8** (P2-2) the 46 mm outer panel everywhere (ACP 3 + bond line 3 + frame 40; skeleton P04);
  - **R-J9** (P2-3) the ceiling closes by assembly order: the side walls' top corner bolts stay finger-tight until both ceiling halves are in and bolted, then everything is torqued; a 1 mm lead-in at C1–C2;
  - **R-J10** an ISO 7093 6.4 × 18 A2 washer under every M6 socket head that clamps on aluminium;
  - **R-J11** (F-011, F-012) each closed chain gets one closing seam that takes its tolerance: B1–B2, B3–B4 and C1–C2 have no hard stop, take about ±1.5 mm across the seam and carry a thicker gasket; the other seams keep their stops;
  - **R-J12** (P2-4) this PR also fixes the sample package, as a one-time exception, and the joint tests take the package's numbers;
  - **R-J13** wall-to-band bolts follow one skeleton rule: end bolts 220 mm in from each panel end, 4 evenly spaced, spigots 100 mm in from each end (Ø8.5 round at one end, 8.5 × 14 slot at the other), holes Ø7.0;
  - **R-J14** the 220 mm rule is the one bolt rule on every bolted edge, not bay middles: end bolts 220 mm in from the ends, the rest evenly spaced, every bolt at least 30 mm clear of any stile (WALL moves a stile if needed, never a bolt);
  - **R-J15** the register owns the bolt lines: on the bolt-side tube's centre, Z 2374 for wall to ceiling;
  - **R-J16** the pinned closing seam is accepted: frames at B1–B2, B3–B4 and C1–C2 are 1198.99 wide, with a 5.5 mm frame gap (4.0–7.0) and the 9.53 gasket (the seal is replaced by a bulb, R-J17); the look doesn't change: the ACP skins stay 1200.61 wide and overhang their frame by 1.62 mm at the closing seam, so the visible skin seam stays 2.26 nominal (0.76–3.76) like every other seam; the same on the ceiling, one part design.
  - **R-J17** fit-up (Reviewer 7's second hold): the side panels' back-end spigots are slotted along X, so each side panel drops in clear of the corner gasket and the corner bolts pull it shut; the closing seams B1–B2, B3–B4 and C1–C2 take a low-force hollow bulb seal (EPDM or TPE) sized for the 4.0–7.0 mm gap instead of foam, reusable when the pod is moved; J-T5's pass mark includes a fit-up force of 150 N or less per edge by hand, overhead included; the joint gasket sits on the nut side (the band at the base joint), gasket names don't start with HARDWARE, and the base seal belongs to family 11 (BASE).
- **HOLD:** a part or number that waits for data or a test. CAD may reserve a space for it, marked UNVERIFIED, but doesn't use its hole pattern until it's released (guideline §4.3 step 4; D-56). Section 6 lists every HOLD with its question.
- **Not covered here:** the ACP-to-frame bond is in [`bond-spec-acp-aluminium.md`](bond-spec-acp-aluminium.md). Door hinges, the fixed glass and the decor top block's joint to the ceiling (IF-08, IF-09) belong to FRONT; the base band's corner keys and the thin floor to BASE.
- No supplier was contacted and nothing was ordered. Data comes from the files below and from public pages, each linked with the date read.

## Result

1. **Two bolts, one key:** every site joint uses an **M6 ISO 4762 socket head, class 8.8, zinc plated, with an ISO 7093 6.4 × 18 A2 washer under the head**, driven with one 5 mm key (R-J2, R-J10). **M6 × 16** at the 72 stopped joints, threaded into a Sherex CAH3-610-4.2 rivnut; **M6 × 25** as a pin at the 10 closing-seam positions. **82 site bolts** in all (section 3.9). The bolt lives inside an edge tube of the part placed second and is driven from inside the pod before the linings go on (section 2.2).
2. **Seam gaps for the skeleton:** **2.26 mm** at every stopped seam (R-J5), set by a metal stop: rivnut head 0.76 (Sherex) on a 1.5 mm aluminium stop washer. **5.5 mm nominal (4.0–7.0) at the three closing seams** B1–B2, B3–B4 and C1–C2 (R-J11, section 2.10). So the back panels' and ceiling halves' **frames become (2408 − 2 × 2.26 − 5.5) / 2 = 1198.99 wide**, against 1200.61 in skeleton P04 (calculation), while **their skins stay 1200.61 and overhang the frame by 1.62 mm at the closing seam**, so every visible skin seam stays 2.26 nominal (R-J16).
3. **Bolt positions follow one rule on every bolted edge** (R-J13, R-J14): end bolts 220 mm in from each panel end, evenly spaced between, every bolt at least 30 mm clear of any stile; 4 on the horizontal edges and 3 on the vertical edges of about 1.1 m; spigots 100 mm in from each end (section 2.9). The register owns the bolt lines (R-J15).
4. **Seals:** at every stopped joint, PORON 4701-40 foam, 8 mm wide, beside the washer line on the outer (skin) side of the nut-side face, so no seal is cut (R-J7): **3.97 mm thick, squeezed 33–51%** (43% nominal). At the three closing seams, **a low-force hollow bulb seal (EPDM or TPE) whose working gap covers 4.0–7.0 mm** (R-J17), which needs no squeeze at fit-up and can be reused when the pod is moved; the part is HOLD-12. **Fit-up:** every part drops in or slides past a seal with 150 N or less per edge by hand (J-T5, R-J17): the side panels' back-end spigots are slotted along X so they drop clear of the corner gasket, and the side walls' tops lean out for the ceiling (R-J9).
5. **Holes:** clearance Ø7.0 positioned to ±0.2 from the spigot hole (R-J6), leaving 0.05 mm to spare worst case (stack ST-03, section 4); access Ø19, so the Ø18 head washer goes in with the bolt (section 2.2).
6. **Findings carried from the first pass:** F1, no room-side hardware in the 4 mm frame-to-lining gap; F2, the 90° joints overlap only 14 mm with 20 × 40 tubes, 34 mm with the 40 × 40 edge members (R-J3); F3, seams need clamping force (R-J1); F4, the bond doesn't fit the 20 mm face as Sika lays it out (bond spec B1); F5, the back-top gap (closed by R-J4); F6, one head type (R-J2).
7. **Part numbers and per-pod counts** for all 15 hardware items, in 2.1: bolts 838001 (72) and 838002 (10), rivnut 838003 (102), head washer 838004 (82), retainer 838005 (72), spigot 831001 (20), stop washer 831002 (72), joint gasket 848001 (25.2 m), closing-seam bulb seal 848004 (3.73 m), base seal 118001 (7.1 m), key 108001 (1), cassette clip 518001 (44), ceiling safety catch 518002 (4), ACP bond set 108002 (4.4 kg), hook-and-loop 848011 (1.6 m on the walls), cassette edge gasket 848012. 848002 and 848003 are cancelled (never used again, conventions §6).
8. **HOLDs: 10 open, 2 closed** (section 6). **Tests** take the sample package's numbers: rivnut spin-out **T06**, bond **T09**, timed access **T11**; the joint tests the package doesn't have are **J-T1 to J-T5**, for the PM to route (section 5).

## 1. Sources

| Key | File or page | Used for |
|---|---|---|
| GL | `docs/engineering-guideline.md` §6.3, §7, §8, §8.1, §8.2, §10 | Register fields, bolt and bond rules, test status |
| DL | `v2/00-Control/decision-log.md`, D-01 to D-60 | Decided stack, clips, holds, the D-60 air layout |
| PM | PM rulings R-J1 to R-J17 in the joints group, 2026-10-31 | As listed above |
| REQ | `v2/00-Control/requirements.md` | REQ-ASM-02 to -11, REQ-BLD-01, -02 |
| IF | `v2/00-Control/assembly-tree.md` §4 | IF-01, IF-03 to IF-07, IF-10 |
| ISS | `v2/00-Control/issue-register.csv` | ISS-003, -011, -014, -015, -016, -034, -036, -045, -054, -064, -076, -079 |
| SEL | `v2/05-Engineering/hardware/selection.md` | Rivnut A5, bracket A7, clips A8, gaskets and base seal D, sample tests |
| HW | `v2/05-Engineering/acoustics-air/report.md` §1, §8, §10 | Stack layers, cassette mass, clip risk |
| LAY | `v2/05-Engineering/layout-study/report.md` §4, §5 | Assembly order, one 5 mm key, bolt and clip counts, base band and glides |
| SKL | `v2/01-CAD-Native/skeleton/` P04: `100000_P04_POD-SKELETON-PARAMETERS.csv` (`outer_t` 46, `cav_gap` 4, `seam_gap` 2.26, `half_pw` 1200.61, `side_h` 1142.74, `side_l` 1492.74, `back_ph` 1118.61, `panel_z0` 112.26) | Envelopes and positions |
| SMP | `v2/06-Samples/wall-door-sample/` (parts list, test plan, hold list) | Sample package: P05–P07, T06, T09, T11, H13 |
| CHK | Mechanical Checker findings F-001, F-008, F-009, F-011, F-012, F-013 and stacks ST-02, ST-03, ST-04 | Gaps, hole float, closed chains |
| SHX | Sherex [CAH3-610-4.2 product page](https://fasteners.sherex.com/item/nd-rivet-nuts-american-style-rivet-nuts-cah-series/cah-series-aluminum-metric-/cah3-610-4-2-1), read 2026-10-31 | Head Ø12.96 ±0.25 × 0.76 ±0.08; length 14.86 ±0.38; installed length 10.16 max; body Ø9.50 max; open end; aluminium 5056; grip 0.70–4.20; hole 9.53 +0.10; "trial installations" recommended |
| ISO4762 | ISO 4762 M6 via [Engineers Edge](https://engineersedge.com/iso_socket_head_screw.htm) and a [Würth ISO 4762 8.8 listing](https://eshop.wuerth-industrie.com/Hexagon-Socket-Head-Cap-Screw-SCR-CYL-ISO4762-88-IH5-A2K-M6X6/00846%20%206.sku/en/US/EUR/), read 2026-10-31 | Head Ø10 max, height 6 max, socket 5; max major Ø 5.974 (CHK) |
| ISO7093 | ISO 7093-1 M6 via a [Fabory A2 200 HV listing](https://www.fabory.com/en_GB/iso-7093-1-penny-mudguard-flat-washer%2c-stainless-steel-a2%2c-200-hv-m6/p/51531060001), read 2026-10-31 | 6.4 × 18 × 1.6 |
| ISO898 | ISO 898-1 class 8.8 via [Engineering ToolBox](https://www.engineeringtoolbox.com/metric-bolts-minimum-ultimate-tensile-proof-loads-d_2026.html), read 2026-10-31 | M6 stress area 20.1 mm², proof load 11.6 kN, minimum ultimate 16.1 kN |

## 2. Rules every site joint follows

### 2.1 Hardware set

| ID | Item | Data | Status |
|---|---|---|---|
| H-01 | **Bolt, stopped joints.** M6 × 16, ISO 4762, class 8.8, zinc plated | Head Ø10, height 6, 5 mm socket (ISO4762); stress area 20.1 mm², proof load 11.6 kN (ISO898) | DECIDED head (R-J2); length calculation (2.2) |
| H-01P | **Pin bolt, closing seams.** M6 × 25, ISO 4762, class 8.8, zinc plated | as H-01 | DECIDED head; length calculation (2.10) |
| H-02 | **Captive retainer, stopped joints.** An elastomer grommet in the Ø19 access hole that grips the bolt head, so the bolt sits back with its tip flush while the parts come together, and lets it be driven and backed out. The closing-seam pin bolts need none: their own rivnut's thread holds them (2.10). | Part and grip force not chosen | concept PROPOSED; part **HOLD-02** |
| H-03 | **Rivnut.** Sherex CAH3-610-4.2, open end, aluminium 5056 | M6 × 1.0; grip 0.70–4.20; hole Ø9.53 +0.10; head Ø12.96 × 0.76 ±0.08; installed length 10.16 max; body Ø9.50 max (SHX) | source; torque **HOLD-01** (D-48); edge distance **HOLD-04** |
| H-04 | **Joint gasket, stopped joints.** Rogers PORON 4701-40 Soft with pressure-sensitive adhesive, 3.97 mm thick, 8 mm wide, on the nut-side face beside the washer line (R-J7, R-J17) | 41 kPa at 25% compression; compression set ≤ 5% at 23 °C (ASTM D3574 D); 3.18–12.70 mm listed (SEL D) | source; the 3.97 thickness and the converter **HOLD-05** |
| H-04B | **Closing-seam seal.** A low-force hollow bulb (D or P profile) in EPDM or TPE, on the nut-side face beside the pin line, whose published working gap covers 4.0–7.0 mm (R-J17); reusable | Candidate with a published range: tesa tesamoll D-Profile EPDM, gaps 3–7 mm (SEL D; consumer grade). Closure force not published | requirement DECIDED (R-J17); part **HOLD-12** |
| H-05 | **Locating spigot.** Ø8 stainless pin with an M6 thread, screwed into an H-03 rivnut at the factory with threadlocker. A part we make. | Ø8, stands 8 proud | PROPOSED (assumption sizes) |
| H-06 | **Base seal.** Closes the gap under the base band to the room floor | Gap 10 nominal (`glide_h`, assumption) ± 5 for the floor (ISS-054, assumption) | **HOLD-06** |
| H-07 | **One tool.** A 5 mm ball-end hex key, or a 5 mm hex bit in a short driver (LAY §4) | — | DECIDED (R-J2) |
| H-08 | **Stop washer.** Aluminium, Ø10.5 × Ø20 × 1.5, clamped under each stopped-joint rivnut's head when the rivnut is set. A part we make (punched from 1.5 mm 5000- or 6000-series sheet). | Grip with it: 1.2 + 1.5 = 2.7, inside 0.70–4.20 (SHX); needs a 40 mm face | PROPOSED; thickness ±0.05 (assumption) |
| H-09 | **Head washer.** ISO 7093-1 large series, 6.4 × 18 × 1.6, A2 stainless, under every bolt head (R-J10) | (ISO7093) | DECIDED (R-J10); dimensions source |
| H-10 | **Lining cassette clip.** The only fixing between each lining cassette and its outer panel's frame: clip-only, no rails (D-81). It must carry a rated load, have a captive lock, and never bridge the floating lining (D-17, D-47; J-LIN-01) | Rated load at least 8.3 kg in shear per wall clip and 8.0 kg in pull-out per ceiling clip (the sample package's T07 limits, calculation, safety factor 3 as an assumption); about 40 g each (D-81's working figure, assumption) | DECIDED requirement (D-47, D-81); part **HOLD-08** |
| H-11 | **Ceiling cassette safety catch.** A steel wire lanyard with a rated working load and its two end fixings, from the ceiling cassette's return to a 20 × 40 ceiling tube (D-47) | At least 48 kg working load per lanyard (the package's T08 limit: 3 × a 16 kg cassette; the P04 cassette is 9.8 kg, CEILING PR #32, so this covers it) | DECIDED requirement (D-47); part **HOLD-08** |
| H-12 | **ACP bond set.** The bond spec's system as one bought set: SikaTack Panel-50 adhesive, Sika Aktivator-205, SikaTack Panel Primer and SikaTack Panel Fixing Tape 3 × 12 | About 0.49 kg per side panel, 4.4 kg per pod (bond spec section 2, calculation) | source (bond spec); in-line tape layout HOLD-B2 |
| H-13 | **Hook-and-loop, locating only.** Lines a cassette up on its frame before the clips take it; never holds it (D-47) | VELCRO® Brand PS14 hook 25 mm, or 3M Dual Lock SJ3560 (SEL A8; no load rating, locating only) | source (candidates); choice open |
| H-14 | **Cassette edge gasket.** PORON 4701-40 Soft with pressure-sensitive adhesive, 3.18 mm thick, 10 mm wide, on a cassette's edge where it meets the next cassette across the 2.26 mm gap (the sample package's P14) | Squeezed (3.18 − 2.26) / 3.18 = 29% (calculation; SEL D data) | source; converter HOLD-05 |

Every rivnut, stop washer, spigot, gasket, retainer and pre-fitted bolt is fitted in the factory (D-08, REQ-ASM-10); on site only the bolts are turned. Every joint rivnut sits on a 40 mm tube face (or the decor's back plate).

**Part numbers** (conventions §5 and §6: 6 digits, FF NNNN; family 83 HARDWARE, 84 SEALS AND TAPES, 11 BASE, 51 LINING, 10 POD general items and the installation kit; NNNN 1000–7999 for parts we make, 8000–8999 for bought catalogue items). Given here at the PM's request so the master BOM can match every team's hardware to this register (D-63: the register owns the one list); the master BOM adopts them. None is on the reserved list (D-28), and none was in use on main or in the open pull requests on 2026-10-31 except 518001 and 518002, which CEILING already uses for the clip and the catch and which this register adopts. The stopped-joint gasket and the closing-seam bulb are different parts, so each has its own number (one number covers one form, fit and function, conventions §6); a cancelled number stays cancelled. The per-pod counts are calculation from the joint entries (section 3) and the panel sizes (2.8).

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-01 | **838001** | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC · Bulong lục giác chìm M6 × 16 | bought | 72 | PROPOSED number; part DECIDED (R-J2) |
| H-01P | **838002** | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC · Bulong lục giác chìm M6 × 25 (chốt mối nối khép) | bought | 10 | PROPOSED number; part DECIDED (R-J16) |
| H-02 | **838005** | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE · Vòng giữ đầu bulong | bought | 72 (the stopped-joint bolts; the pins need none) | PROPOSED number; part HOLD-02 (number kept for it) |
| H-03 | **838003** | HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2 · Tán rút M6 | bought | 102 (72 stopped joints, 10 closing-seam pins, 20 spigots) | PROPOSED number; part source (SHX) |
| H-04 | **848001** | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA · Gioăng mối nối 3.97 | bought by length | 25.2 m (every stopped joint) | PROPOSED number; strip HOLD-05 |
| H-04B | **848004** | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE · Gioăng ống mối nối khép | bought by length | 3.73 m (the three closing seams) | PROPOSED number; part HOLD-12 |
| H-05 | **831001** | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS · Chốt định vị Ø8 | made | 20 (8 on the band, 8 on the horizontal seams, 4 under the ceiling) | PROPOSED number and part |
| H-06 | **118001** | BASE - BASE SEAL - GAP 10 ±5 · Gioăng chân đế | bought by length, used only in BASE | 7.1 m (the base band's length) | PROPOSED number; part HOLD-06 (number kept for it) |
| H-07 | **108001** | POD - HEX KEY - 5 MM BALL END · Lục giác 5 mm đầu bi | bought, in the installation kit 109000 | 1 | PROPOSED number; part DECIDED (R-J2) |
| H-08 | **831002** | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL · Long đen chặn nhôm | made | 72 (one under each stopped-joint rivnut) | PROPOSED number and part |
| H-09 | **838004** | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 · Long đen to M6 inox | bought | 82 (one under each bolt head) | PROPOSED number; part DECIDED (R-J10) |
| H-10 | **518001** | LINING - CASSETTE CLIP · Kẹp treo cassette | bought, used only in LINING | **44**: 4 on each of the 8 wall cassettes, 6 on each of the 2 ceiling cassettes | number as CEILING uses it (PR #32); part HOLD-08 |
| H-11 | **518002** | LINING - CEILING SAFETY CATCH · Dây an toàn cassette trần | bought, used only in LINING | **4**: 2 on each ceiling cassette | number as CEILING uses it (PR #32); part HOLD-08 |
| H-12 | **108002** | POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE · Bộ keo dán ACP | bought set, used by WALL and CEILING | about 4.4 kg (0.49 kg per side panel, bond spec) | PROPOSED number; system source (bond spec) |
| H-13 | **848011** | SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY · Băng gai dính định vị cassette | bought by length | 1.6 m for the 8 wall cassettes (0.2 m each, WALL's figure); CEILING adds its own if it uses it | PROPOSED number (WALL's placeholder kept) |
| H-14 | **848012** | SEALS - CASSETTE EDGE GASKET - 10 X 3.18 - PORON 4701-40 PSA · Gioăng mép cassette | bought by length | WALL's count; about 5.2 m for the horizontal joints between stacked wall cassettes (calculation: 2 × 1448 + 2 × 1169) | PROPOSED number (WALL's placeholder kept); strip HOLD-05 |

**Cancelled numbers, never to be reused (conventions §6):** 848002, the 9.53 mm foam strip first proposed for the closing seams, replaced by the bulb seal 848004; 848003, the base seal's first number, moved to 118001 in family 11, BASE (R-J17); and 848010, WALL's placeholder for the bond, which is not a seal or tape and takes 108002 in family 10 instead (a bought set used by both WALL and CEILING, so it belongs to neither family alone). WALL's placeholders 848011 and 848012 are kept for the hook-and-loop and the edge gasket, which family 84 covers (gaskets, hook-and-loop, adhesive tapes).

### 2.2 The in-member bolt (stopped joints)

Each joint has a **nut side** (the part with the rivnut) and a **bolt side** (the part whose edge tube holds the captive bolt). The bolt side is the part whose frame bay the person inside the pod can reach; each joint entry says which is which.

1. The nut side has an H-03 rivnut, set through an H-08 stop washer, in the tube face that meets the joint.
2. The bolt side's edge tube has, on the same axis: a **Ø7.0** clearance hole in its joint-side wall, and a **Ø19** access hole in the opposite wall, facing into its own frame bay.
3. The factory puts the H-09 washer on the bolt and pushes both in through the Ø19 hole, tip first, then presses the H-02 grommet into the Ø19 hole around the head. The washer can't come off: its 6.4 bore is smaller than the head.
4. On site, the 5 mm key reaches through the bay's pocket (2.3) into the socket. The bolt runs into the rivnut, the washer seats on the inside of the joint-side wall, and the joint closes onto its stop.

**Stack for M6 × 16** (calculation; tube wall 1.2 per D-54; rivnut SHX; washer ISO7093):

| Step | Value | Status |
|---|---|---|
| Head washer 1.6 + joint-side wall 1.2 under the head | 2.8 | confirmed wall; source washer |
| Stop between the faces: stop washer 1.5 + rivnut head 0.76 | **2.26** (2.13–2.39) | calculation |
| Bolt beyond the joint-side wall's outer face: 16 − 2.8 | 13.2 | calculation |
| Rivnut's far end from that face: 0.76 + 10.16 installed length (max) | 10.92 at most | calculation (SHX) |
| Bolt past the rivnut's far end (every thread engaged) | 2.28; at least 1.9 with the bolt's length tolerance (js15, ±0.35; unverified) | calculation |
| Tip beyond the nut-side wall's outer face: 13.2 − 2.26 | 10.94 | calculation |
| Tip clearance in a nut-side tube 20 deep along the bolt (far inner face at 18.8) | 7.9 | calculation |
| Head and washer inside a bolt-side tube 20 deep: 6 + 1.6 in an inner width of 17.6 leaves 10.0 for the key | 10.0 | calculation |
| Pulled back (tip flush with the joint face), the head stands 2 out of the Ø19 hole, held by the grommet | 2 | calculation |
| Bearing under the head: washer ring π/4 × (18² − 7²) = 216 mm² against 40 mm² for a bare head on a Ø7.0 hole (CHK's caution) | 5.4 × the area | calculation; T06 checks the wall doesn't dish |

**Gasket squeeze at the stops:** 3.97 mm PORON in a 2.26 gap is squeezed (3.97 − 2.26) / 3.97 = **43%**; with the stop at 2.13–2.39 and the gasket ±10% (assumption), 33–51% (calculation). That replaces the 3.18 mm strip of the first pass, whose worst case was 17% (Reviewer 7, P3).

### 2.3 Access pockets

In the wall panels, next to each site bolt, the factory leaves the 40 mm PET fill out of a pocket **60 × 60 mm** (assumption) in the bolt side's bay, in front of the Ø19 hole. The cassette covers it later. The ceiling halves need no pockets: their fill rides on the ceiling cassette (D-24), so their bays are empty until the cassettes go on. 82 pockets of 0.0036 m² at most is 0.30 m², about 2% of the roughly 15.6 m² of wall and ceiling panels (calculation from SKL P04 sizes). The effect on sound isn't modelled; the wall sample is built with pockets. Because the bolts follow the 220 mm rule rather than bay middles, **every bolt stays at least 30 mm clear of any stile** (R-J14): the WALL and CEILING drawings move a stile if needed, never a bolt, so no frame member crosses a pocket (rule R5).

### 2.4 Edge members at the 90° joints

With the 46 mm outer panel (R-J8; SKL P04): side frames X −1244 to −1204 (room-side face at X ∓1204), back frames Y +804 to +844, ceiling frames Z 2354 to 2394.

| Joint | Edge member of the panel whose skin covers the corner | The other panel's edge tube | Overlap with a 20 × 40 member | Overlap with the 40 × 40 member (R-J3) |
|---|---|---|---|---|
| Back corner (J-WALL-02) | Side panel's back member, X −1244 to −1204 | Back panel's outer tube, Y +804 to +844 | Y +830 to +844 = **14** | Y +810 to +844 = **34** |
| Side wall to ceiling (J-CEIL-01) | Upper side panel's top member, X −1244 to −1204 | Ceiling's side tube, Z 2354 to 2394 | Z 2380 to 2394 = **14** | Z 2360 to 2394 = **34** |
| Back wall to ceiling (J-CEIL-01) | Ceiling's back member, Z 2354 to 2394 | Back panel's top tube, Y +804 to +844 | Y +830 to +844 = **14** | Y +810 to +844 = **34** |

All calculation from SKL P04. **The bolt lines sit on the bolt-side tube's centre: Y +824 and Z 2374** (DECIDED, R-J15), not the middle of the overlap (Y +827, Z 2377). The Ø19 access hole needs the tube's whole width: centred, it keeps 9.3 mm to each inner wall; at +827 it would keep 6.3 on one side. At +824 the rivnut's hole edge is 9.2 mm from the edge of the 40 × 40 member's face and the Ø20 stop washer (Y +814 to +834) lies inside both faces (calculation). The 40 × 40 member weighs 0.503 kg/m against 0.373 (calculation, aluminium 2.70 g/cm³): **+1.29 kg** for 4 side back members × 1142.74, 2 upper side top members × 1492.74 and 2 ceiling back members × 1198.99 (calculation).

### 2.5 Seals

Every joint face carries one H-04 strip, **8 mm wide, beside the washer line on the outer (skin) side** (R-J7): at the stops it sits between the Ø20 stop washer's edge and the face's outer edge, 1 mm clear of each (on a 40 mm face the washer leaves 10 mm each side of itself, calculation); at the closing seams the bulb seal (H-04B) runs beside the Ø12.96 rivnut heads the same way. It passes beside the spigots the same way, so **the seal line is unbroken** along every joint (ISS-003).

Line load at 25% squeeze: 41 kPa × 8 mm = **0.33 N/mm** (calculation from SEL D). At 43% the foam is stiffer and no point is published; up to 1.0 N/mm is assumed (3 ×, assumption). The tubes bend between bolts under it: for a 20 × 40 × 1.2 tube bent across its 20 mm depth, I = 9 584 mm⁴ (calculation), E = 69 000 MPa (assumption; alloy open, ISS-034, HOLD-09). Fixed at bolts 352 mm apart (the widest spacing, 2.9), a tube deflects under 0.06 mm at 1.0 N/mm (calculation); beyond the end bolts, 220 mm to the panel corner, a fully free tube end would open 0.44 mm, but the frame corner holds it, so the real figure is smaller and J-T3 measures it. Either way the squeeze stays above 25% (0.44 × 2 = 0.88 against a 1.71 mm squeeze, calculation).

A panel's own weight doesn't clamp a seam: an upper side panel's outer part weighs about 11.3 kg, about 0.07 N/mm along its 1493 mm seam (calculation), a fifth of the 0.33 needed. Hence R-J1.

### 2.6 Load cases

Working values, so each joint has a load to check against. Each is marked.

| LC | What | Value | Status |
|---|---|---|---|
| LC1 | Own weight. Outer panels 6.6 kg/m² for walls, 5.3 for the ceiling (its fill rides on the cassette, D-24); wall cassette 10.3 kg (SEL A8); ceiling cassette about 16 kg with fill (SEL A8); door unit 47.5 kg (D-56) | as listed | calculation (from HW, SEL); door confirmed (D-56) |
| LC2 | Someone leaning or pushing on a wall: 0.5 kN per metre of wall, at 1.2 m height | 0.5 kN/m | assumption; to check against EN 1991-1-1 §6.4 (unverified) |
| LC3 | Door misuse: a downward force at the free edge of the open door | 600 N | assumption; EN 1192 classes to check (unverified) |
| LC4 | Handling and shipping: carried at the edges by two people; a 2 g bump on the pallet | 2 g | assumption |
| LC5 | Repeated assembly | 5 cycles | assumption (REQ-ASM-09) |

At the joints (calculation): LC2 on a wall spanning 2.29 m gives 0.26 kN/m at the base and 0.24 kN/m at the top: with 4 bolts on a 1493 mm edge, about **100 N per base bolt**. The door's weight puts a 274 N·m moment on DL, a 152 N couple between hinges 1.8 m apart (assumption); LC3 adds 391 N. These are small next to the bolt's 11.6 kN proof load: **the weak link is the rivnut in the 1.2 mm tube**, which has no published strength (SHX), so strength is shown by test (J-T1), not a catalogue figure (guideline §8.1). How LC2's moment shares between a wall's edges and its seams needs the panel's own calculation or the push test in J-T3.

### 2.7 Tolerance and adjustment, common to all joints

- **Clearance holes Ø7.0, positioned to Ø0.4 (±0.2) from the spigot hole, by CNC or a drill jig (R-J6).** Stack ST-03 (CHK): (7.0 − 5.974) / 2 − 0.2 − 0.2 − 0.065 rivnut float = **0.05 mm to spare** worst case (calculation). The rivnut's 0.065 is half of (9.63 − 9.50), hole maximum against body maximum (SHX).
- **Locating:** two H-05 spigots 100 mm in from the ends of each horizontal edge that a part is set down on (the base band, the panel below, the back wall's top under the ceiling): a Ø8.5 round hole at one end, an 8.5 × 14 slot along the edge at the other (R-J13). The vertical joints need none of their own: both parts already stand on spigots.
- **Fit-up without scraping a seal (R-J17):** at the back corners the side panels' back-end spigot slot runs **along X** (8.5 × 14, so ±3 mm), not along the edge: each side panel goes down with its back end held clear of the corner gasket on its own back member (the strip stands 1.71 mm proud of the stop, and the panel is held about 2.5 mm out, assumption), then the corner bolts pull it in onto the stops, and only then are the base bolts near its back end driven (their holes line up once it's pulled in). The upper side panels do the same on the lower ones' top tubes. At the ceiling's side edges the side walls' tops lean out instead, with their top corner bolts finger-tight (R-J9): about 4 N moves a wall's top 1.7 mm (calculation: 3 E I δ / L³ for the wall as a 2.29 m cantilever, I of 5 frame tubes ≈ 1.4 × 10⁵ mm⁴, assumption). At the closing seams the bulb seal needs no squeeze at fit-up (H-04B). If FRONT locates the decor blocks by spigots, their slots run along Y for the same reason.
- **Gaps are set by metal stops** (2.26) at the stopped seams, and by the parts' own spigots at the closing seams (2.10), never by torque.
- **Frame flatness at a joint face:** ±0.5 mm over a seam (assumption; set in the frame drawings with the maker's capability, guideline §6.3).
- **Room floor:** ±5 mm over the footprint (ISS-054, assumption), taken up by the 8 glides under the base band, set from above with the same key before any wall goes on (LAY).
- **Torque:** HOLD-01 (D-48), from T06. A seal needs at most about 350 N per bolt (1.0 N/mm × 352 mm), so the torque only has to close the joint onto its stop.
- **Order of tightening** (R-J9, R-J11): each wall's and the ceiling's closing-seam pins first; then the stopped seams; the side walls' top corner bolts and the ceiling's side bolts last, once both ceiling halves are in and bolted. A stop that sits up to ±0.25 off is taken up by the spigot play (Ø8.5 on Ø8) and the bolt-hole float (ST-03); the frame tolerances in 2.11 keep the band-set mismatch inside that. Higher up a wall, a bolt can also pull a stop shut by flexing the frame: a 40 × 40 × 1.2 member 1.14 m long needs about 23 N to move 0.3 mm at mid-length (calculation: 48 E I δ / L³, I ≈ 35 000 mm⁴, assumption), but the bottom bolt, 220 mm above the fixed base, can't.

### 2.8 Seam gaps for the skeleton (F-001, R-J5, R-J11)

| Seam | Interface | Gap direction | Gap (compressed gasket) | Gasket |
|---|---|---|---|---|
| Side wall horizontal seams, L1–L2 and R1–R2 | IF-04 | Z | 2.26 (stop) | 3.97 |
| Back wall horizontal seams, B1–B3 and B2–B4 | IF-04 | Z | 2.26 (stop) | 3.97 |
| **Back wall centre seams, B1–B2 and B3–B4 (closing)** | IF-04 | X | **5.5 nominal, 4.0–7.0** | bulb seal |
| Back corners, side panels to B1–B4 | IF-03 | X | 2.26 (stop) | 3.97 |
| Walls on the base band (L1, R1, B1, B2) | IF-01 | Z | 2.26 (stop) | 3.97 |
| Side walls to the ceiling, L2–C1 and R2–C2 | IF-05 | X | 2.26 (stop) | 3.97 |
| Back wall to the ceiling, B3–C1 and B4–C2 | IF-05 | Z | 2.26 (stop) | 3.97 |
| **Ceiling centre seam, C1–C2 (closing)** | IF-06 | X | **5.5 nominal, 4.0–7.0** | bulb seal |
| Decor blocks to the side walls, DL–L1/L2 and DR–R1/R2 | IF-07 | Y | 2.26 (stop) | 3.97 |

Panel sizes (calculation; the skeleton owner applies them):

| Panel | Skeleton P04 | With the closing seams | How |
|---|---|---|---|
| Back panels B1–B4 and ceiling halves C1, C2: frame width | 1200.61 (`half_pw`) | **1198.99** | (2408 − 2 × 2.26 − 5.5) / 2: two stopped gaps and one closing gap between the side frames (R-J16) |
| The same panels: skin width | 1200.61 | **1200.61** (unchanged) | flush with the frame at the stopped edge, 1.62 past it at the closing seam (R-J16) |
| Side panels, height | 1142.74 | 1142.74 | unchanged |
| Side panels, length | 1492.74 | 1492.74 | unchanged |
| Back panels, height | 1118.61 | 1118.61 | unchanged |
| Walls on the band | Z 112.26 | Z 112.26 | unchanged |

**The visible skin seam is 2.26 nominal everywhere (R-J16).** At the stopped seams the skins are flush with their frame edges, so the skin seam is the 2.26 frame gap. At the closing seams the back and ceiling skins keep their 1200.61 width on the 1198.99 frames and overhang the frame by 1.62 mm on the seam side: the skin seam is 5.5 − 2 × 1.62 = 2.26 nominal, and 0.76–3.76 as the frame gap moves through 4.0–7.0 (calculation). Each back panel and ceiling half is one part design: B1, B3 and C1 overhang on their right edge, B2, B4 and C2 on their left (mirror pairs, conventions §5). For the WALL and CEILING drawings and the skins' DXF.

### 2.9 Bolt and spigot positions (R-J13)

One rule for every bolted edge (DECIDED, R-J13, R-J14): **end bolts 220 mm in from each end of the panel edge, the rest evenly spaced, every bolt at least 30 mm clear of any stile; spigots 100 mm in from each end where the edge has them; holes Ø7.0 (clearance), Ø19 (access), Ø9.53 (rivnut).** The register sets the count on each edge and the bolt lines (R-J15); Fusion Engineer 2 carries the rule in the skeleton; WALL and CEILING move a stile, never a bolt.

| Edge | Length (SKL P04, 2.8) | Bolts | Positions from the edge's start | Spacing | Status |
|---|---|---|---|---|---|
| Side panel on the band; side horizontal seam | 1492.74 | 4 | 220, 570.91, 921.83, 1272.74 | 350.91 | DECIDED |
| Back panel on the band; back horizontal seam; ceiling back edge | 1198.99 | 4 | 220, 473.00, 725.99, 978.99 | 253.00 | DECIDED |
| Back corner; back closing seam (along the back panel's 1118.61 edge) | 1118.61 | 3 | 220, 559.31, 898.61 | 339.31 | DECIDED rule; count this register's |
| Decor to side wall (along each side panel's height) | 1142.74 | 3 | 220, 571.37, 922.74 | 351.37 | DECIDED rule; count this register's |
| Ceiling side edge; ceiling closing seam (along Y) | 1495 (unverified: the ceiling's Y extent in P04) | 4 | 220, 571.67, 923.33, 1275.00 | 351.67 | DECIDED rule; count this register's |

All positions are calculation. Spigots at 100 from each end, Ø8.5 round at one end and 8.5 × 14 along the edge at the other: on the band, on the lower panels' top tubes, and on the back wall's top tubes under the ceiling. Which end is round is set in the skeleton with the rule; it doesn't change any number here.

### 2.10 The closing seams (R-J11)

**Where:** B1–B2 and B3–B4 (back wall, X 0) and C1–C2 (ceiling, X 0). Every other seam keeps its stop.

**How it works.** In this scheme the bolt runs across the seam, so the seam's ±1.5 mm is taken **along the bolt**, and no slot is needed. The closing-seam bolt is a **pin**, not a clamp:

1. The bolt side (B2, B4, C2: the right-hand part) has an H-03 rivnut in its joint-side wall, with no stop washer. The factory screws an M6 × 25 bolt with its H-09 washer into it from inside the tube, until its tip is just inside the rivnut's head: the thread holds it captive.
2. The nut side (B1, B3, C1) has a plain **Ø7.0** hole in its joint-side wall, coaxial within ±0.2 (R-J6). No rivnut.
3. On site, after both parts stand on their own spigots, the key drives the bolt on until its washer meets the rivnut's inner end. Its shank then crosses the gap and passes through the Ø7.0 hole as a pin. It's snugged, not torqued: it locks the bolt in its own rivnut and pulls nothing.
4. The pin holds the two faces flush and level (±0.26: the Ø7.0 float, ST-03) and leaves the gap free along the bolt.

| Check | Value | Status |
|---|---|---|
| Washer seat: the rivnut's inner end, 10.16 (max) from the joint face; washer 1.6; head 6 | head top at 17.76, inside the 18.8 tube, 1.04 clear of the access wall | calculation |
| Pin through the nut-side wall at the widest gap, 7.0 | 5.04 past the wall's inner face | calculation |
| Pin tip at the narrowest gap, 4.0, in a 20-deep tube | 9.56 clear of the far wall | calculation |
| Smallest possible gap: the bolt side's rivnut head | 0.76: a hard limit far below the 4.0 working minimum | calculation (SHX) |
| Seal over 4.0–7.0 | a low-force hollow bulb whose published working gap covers 4.0–7.0 (H-04B, HOLD-12); the candidate's 3–7 mm does (SEL D) | source (range); closure force J-T5 |

**Why 5.5 nominal:** the range must stay well above the 0.76 rivnut head and sit inside the bulb seal's working gap; ±1.5 about 5.5 gives 4.0–7.0, inside the candidate's published 3–7 mm (SEL D), with 1 mm to spare at each end (calculation). 5.5 also clears any thread or spigot play by a wide margin.

**The lead-in (R-J9):** the C1–C2 faces get a 1 × 45° chamfer on their lower edges, so C2 drops in past C1 without catching its gasket; B1–B2 and B3–B4 get the same on their top edges, for the upper panels.

### 2.11 Closed-chain stacks ST-02 and ST-04 (F-011, F-012)

Worst case, all mm, positions along X. Every part stands on its own spigots (round hole plus slot, R-J13), so each chain's tolerance comes from where the spigots are and how far each part's joint face sits from its round spigot hole. The tolerances below are what the chains need. They are PROPOSED for the BASE, WALL and CEILING drawings: **±0.1 for each spigot position and for each panel's spigot-to-joint-face distance (CNC or a drill jig, as R-J6 already asks for the bolt holes)**.

**ST-02, back wall (each row: L side frame, stop, B1, closing seam, B2, stop, R side frame).**

| Contributor | Worst case | Status |
|---|---|---|
| B1's and B2's round spigots on the back band, spacing | ±0.1 | PROPOSED (CNC band) |
| B1: round spigot hole to its right face; B2: round spigot hole to its left face | ±0.1 each | PROPOSED (CNC frame) |
| **Closing gap B1–B2, nominal 5.5** | **±0.3, so 5.2–5.8** | calculation: well inside 4.0–7.0 |
| Corner gap: the side panel's back spigot on BAND-L to the back panel's round spigot on BAND-BACK, across the band's corner key | ±0.1 | PROPOSED (CNC band and key) |
| Side panel: back spigot to its back member's face; back panel: round spigot to its outer face | ±0.1 each | PROPOSED |
| **Corner gap at the stop, nominal 2.26** | **±0.3**, taken up by the ±0.25 spigot play and the ±0.26 bolt-hole float, so the stop seats (2.7) | calculation |

**ST-04, ceiling (L2 top member, stop, C1, closing seam, C2, stop, R2 top member).** C1 and C2 stand on their back spigots on B3 and B4, which stand on B1 and B2:

| Contributor | Worst case | Status |
|---|---|---|
| B1's and B2's round spigots on the back band, spacing | ±0.1 | PROPOSED |
| B1 and B2: round spigot hole to their top spigot rivnuts | ±0.1 each | PROPOSED |
| B3 and B4: bottom spigot hole to their top spigot rivnuts | ±0.1 each | PROPOSED |
| B3 and B4 on B1 and B2: spigot play at the horizontal seam | ±0.25 each | calculation (Ø8.5 on Ø8) |
| C1 and C2: round spigot hole to the closing face | ±0.1 each | PROPOSED |
| **Closing gap C1–C2, nominal 5.5** | **±1.2, so 4.3–6.7** (about ±0.4 as the root of the sum of squares) | calculation: inside 4.0–7.0 |

At looser tolerances, ±0.25 on each panel, the ceiling's worst case would be ±2.0 (3.5–7.5), past the gasket's range, which is why the ±0.1 is asked for. The ceiling's side gaps close onto their stops through the side bolts, with the side walls' top corner bolts finger-tight so the walls' tops can follow (R-J9), and are torqued last.

## 3. Joint entries

Each entry has the guideline's fields (§8). Joint IDs here differ from the layout study's (mapping in 3.10).

### 3.1 J-WALL-01: wall to wall, horizontal seams (IF-04)

| Field | Entry |
|---|---|
| Parts | Side walls: L1–L2, R1–R2. Back wall: B1–B3, B2–B4. |
| Function and load path | Keeps the outside faces flush so the reveals stay crisp (D-23); carries shear across the seam (racking and LC2); seals it. The upper panel's bottom tube sits on the lower panel's top tube through the stops. Load: bolt → rivnut → the lower panel's tube wall. |
| Loads | LC2: about 100 N per bolt (2.6). Seal: up to 350 N per bolt (2.7). LC1: the upper panel's 110 N rests on the stops. |
| Take-down | Yes, 5 cycles; the bolts back out and stay captive. |
| Options compared | (a) tool-free hook or wedge: no rated part and no seal force (2.5); (b) room-side latch: no room (F1); (c) **captive in-member M6 bolt (chosen)**; (d) glue or rivets on site: not allowed (REQ-ASM-05). |
| Choice and reason | (c), DECIDED (R-J1). |
| Nut side and bolt side | Nut side: the lower panel: rivnuts with stop washers in its top tube's top face (40 mm), 2 H-05 spigots, H-04 strip on the outer side. Bolt side: the upper panel's bottom tube: Ø7.0 down through its bottom wall, Ø19 in its top wall, reached from the bay above. |
| Bolts | 4 per seam at the 220 mm rule (2.9): side 4 × 2, back 4 × 2: **16**. |
| Stack | 2.2: nut-side tube 20 deep, tip clear by 7.9. |
| Assembly | The upper panel is lowered onto the lower one, spigots into hole and slot (lead-in chamfers on the closing seam above B1–B2, 2.10); bolts from inside through the pockets, before the cassettes (LAY steps 4, 5, 11); 2.2 m bolts from the step stool. |
| What can go wrong | Rivnut spins or pulls out (T06, J-T1); key can't reach (pocket blocked, T11); faces step at the seam (J-T3). |
| Check and pass mark | T06, T11, J-T1, J-T3 (section 5). |
| Status | DECIDED fastener (R-J1, R-J2, R-J10); positions PROPOSED (R-J13 approach). HOLD-01, -02, -05. |

### 3.2 J-WALL-02: back corner, side wall to back wall (IF-03)

| Field | Entry |
|---|---|
| Parts | BL: L1–B1, L2–B3. BR: R1–B2, R2–B4. |
| Function and load path | Closes the box at the back corners: racking, the back wall's out-of-plane load into the side walls, seal. The side panels' ACP covers the back panels' edges (D-55). Load: the back panel's outer tube → bolt → rivnut in the side panel's 40 × 40 back member. |
| Loads | LC2: about 0.26 kN per metre of edge, about 100 N per bolt. Seal: up to 350 N per bolt. |
| Options compared | 20 × 40 member in a 14 mm overlap: no room (2.4); room-side angle: no room (F1); tool-free hook: no seal force (F3); **40 × 40 member with an in-member bolt (chosen)**. |
| Choice and reason | DECIDED (R-J1, R-J3); bolt line DECIDED (R-J15). |
| Nut side and bolt side | Back panels go on first, then the sides (LAY step 4). Nut side: the side panel's back member, 40 × 40 × 1.2 (Y +810 to +850), with rivnuts and stop washers in its room-side face at **Y +824**. Bolt side: the back panel's outer tube, Ø7.0 in the wall that faces the side panel and Ø19 in its bay-side wall, at Y +824; the bolts stay pulled back while the side panel goes on. |
| Bolts | 3 per back panel edge at the 220 mm rule: 6 per corner, **12**. |
| Stack | 2.2: nut side 40 deep. Overlap 34 (2.4). Corner gaps per ST-02 (2.11): bolted shut, torqued last. |
| Assembly | Side panel lowered onto its band spigots with its back end held about 2.5 mm out (the back-end slot runs along X, R-J17), clear of the gasket on its own back member; the corner bolts, along X from the back panel's bay, pull it in onto the stops; then its base bolts near the back end (2.7). |
| What can go wrong | The outside corner shows the side member's back face (Y +850, 46 wide with the bond line and ACP edge) along its full height, and the ceiling's back member shows the same way along the back top edge: both need the skin's return or a trim, without changing the look (D-01; section 7). |
| Check and pass mark | T06, T11, J-T1, J-T5. |
| Status | DECIDED fastener and member; positions PROPOSED. HOLD-01, -02, -05. |

### 3.3 J-WALL-03: back wall closing seams, B1–B2 and B3–B4 (IF-04, R-J11)

| Field | Entry |
|---|---|
| Parts | B1–B2 (lower row), B3–B4 (upper row), at X 0. |
| Function and load path | Takes the back wall's tolerance (ST-02); holds the two panels' faces flush and level; seals. The pin carries shear across the seam (out of plane and vertical); nothing pulls the seam shut. |
| Loads | LC2 shear across the seam: about 100 N per pin (2.6). No seal force needed from the bolt: the bulb seal works across the whole gap range by itself. |
| Options compared | A stopped seam: zero slack in a closed chain (F-011); slotted holes: in this scheme the bolt crosses the seam, so a slot does nothing; **a pin bolt threaded into the right-hand panel and passing a Ø7.0 hole in the left (chosen, 2.10)**. |
| Choice and reason | DECIDED (R-J11, R-J16). |
| Nut side and bolt side | Nut side B1 or B3: a plain Ø7.0 hole in the right tube's +X wall. Bolt side B2 or B4: an H-03 rivnut (no stop washer) in the left tube's −X wall, the M6 × 25 pin screwed into it from inside, Ø19 access in its +X wall. 1 × 45° lead-in on the top edges of both faces. H-04B bulb seal on B1's or B3's face beside the pin line, outer side (R-J17). |
| Bolts | 3 per seam at the 220 mm rule: **6**. |
| Stack | 2.10 (gap 4.0–7.0; pin engaged 5.04 or more). |
| Assembly | B1 and B2 stand on their band spigots; pins driven any time before the corners are torqued; then B3 and B4 the same. |
| What can go wrong | The pin misses the Ø7.0 hole if the panels are off by more than the float (ST-03: 0.05 to spare); the bulb seal too stiff for a 150 N fit-up, or too soft to seal at 7.0: J-T3 checks the seam for light and air, J-T5 the fit-up force. |
| Check and pass mark | J-T3, J-T5. |
| Status | DECIDED (R-J11, R-J16); HOLD-05. |

### 3.4 J-BASE-01: wall to base band, the wall-to-floor joint (IF-01)

| Field | Entry |
|---|---|
| Parts | The bottom tubes of L1, R1, B1 and B2 on BAND-L, BAND-R and BAND-BACK (100 × 40, on 10 mm glides; SKL; LAY B-BAND). The thin floor lies loose inside the band and isn't part of this joint. |
| Function and load path | Carries the walls and roof to the band and the glides; locates the walls; takes the base share of LC2 and racking; seals. Weight: bottom tube → stops and gasket → band top → glides. |
| Loads | LC1: about 0.34 kN per metre of side wall (calculation). LC2: about 100 N per bolt. |
| Options compared | Room-side angle: clashes with the lower cassette (F1); spigots alone: nothing holds a panel down or squeezes the gasket; **in-member bolts down into rivnuts in the band (chosen)**. |
| Choice and reason | DECIDED positions (R-J13): 4 bolts at the 220 mm rule, spigots 100 in, Ø7.0. |
| Nut side and bolt side | Nut side: the band's top wall, with 2 H-05 spigots and 4 rivnuts with stop washers per panel, on the wall tube's centre line: **X ∓1224** (side walls) or **Y +824** (back wall), 6 mm off the band's own centre line (calculation: band 40, panel 46). The band's top wall must be 2.7 mm or thinner for the rivnut grip with the washer (**HOLD-07**). Bolt side: the wall's bottom tube: spigot hole and slot, Ø7.0 in its bottom wall, Ø19 in its top wall. H-06 base seal under the band (HOLD-06). |
| Bolts | 4 per panel: **16**. |
| Stack | 2.2 (the band is open inside). |
| Tolerance and adjustment | The band is levelled on its 8 glides before any wall goes on; the walls stand at Z 112.26 (2.8); the ACP's outer face is flush with the band's outer face, so the frame overhangs the band by **6 mm** inside (calculation). |
| Assembly | Wall lowered onto the band spigots; bolts down from the pocket in its bottom bay (LAY step 4). |
| What can go wrong | Band top wall too thick (HOLD-07); DR's notch in BAND-R (a BASE HOLD); a 10 ± 5 mm gap the base seal can't close (HOLD-06). |
| Check and pass mark | T06, T11 (its 4 base bolts), J-T1, J-T4. |
| Status | DECIDED (R-J2, R-J10, R-J13); HOLD-01, -02, -05, -06, -07. |

### 3.5 J-CEIL-01: wall to ceiling (IF-05)

| Field | Entry |
|---|---|
| Parts | Side edges: C1 to L2, C2 to R2. Back edges: C1 to B3, C2 to B4. |
| Function and load path | Carries the roof to the walls; ties the box at the top; seals. The side panels' ACP covers the ceiling's edges (D-55). Side edges: the ceiling's side tube → bolt → rivnut in the upper side panel's 40 × 40 top member. Back edges: the ceiling's 40 × 40 back member sits on the back wall's top tube through the stops, bolted from below. |
| Loads | LC1: about 250 N per ceiling half (outer panel 9.6 kg plus cassette 16 kg), under 40 N per bolt. LC2 at the top: about 100 N per bolt. Seal: up to 350 N per bolt. |
| Options compared | As J-WALL-02 (14 mm overlaps, 2.4); a ledge under the side tube: no room in the 4 mm gap above the side lining (D-57). |
| Choice and reason | DECIDED members and fastener (R-J1 to R-J3); closing order R-J9. |
| Nut side and bolt side | **Side edges:** nut side the wall: rivnuts and stop washers in the upper side panel's top member (room-side face) at **Z 2374**; bolt side the ceiling's side tube, Ø19 in its inner wall, reached through the ceiling's open bay. **Back edges:** nut side the ceiling: rivnuts and stop washers in its back member's bottom face at **Y +824**; bolt side the back panel's top tube (Ø7.0 in its top wall, Ø19 in its bottom wall, from the pocket in the top bay), bolts pulled back while the ceiling goes on, then driven up. 2 H-05 spigots per half on the back panel's top tube (2.7, 2.9). |
| Bolts | 4 per edge at the 220 mm rule: **16** (the layout study counts 16 bolts for this step too, LAY §5 step 6). |
| Assembly (R-J9) | The side walls' top corner bolts are finger-tight. C1 is lifted from inside onto its back spigots, its side tube against L2; then C2 the same, dropping past C1's lead-in (2.10); then the C1–C2 pins (J-CEIL-02), the ceiling's back bolts, its side bolts, and last the side walls' top corner bolts, all torqued. |
| What can go wrong | **D-60:** C2's bolts, access holes and pockets must stay clear of the roof exhaust slot just behind DR, and of the soffit's path above the door head; the CEILING drawing checks it. The ceiling cassettes and their catches (J-LIN-01) hang on the same tubes. |
| Check and pass mark | T06, J-T1, J-T5 (the ceiling isn't in the wall sample). |
| Status | DECIDED (R-J1 to R-J4, R-J9, R-J10); positions PROPOSED; HOLD-01, -02, -05. |

### 3.6 J-CEIL-02: ceiling closing seam, C1–C2 (IF-06, R-J11)

| Field | Entry |
|---|---|
| Parts | C1–C2 at X 0. |
| Function and load path | Takes the ceiling's tolerance (ST-04); holds the halves' faces flush and level; seals. Same pin principle as J-WALL-03 (2.10). |
| Nut side and bolt side | Nut side C1: a plain Ø7.0 hole in its right tube's +X wall. Bolt side C2: an H-03 rivnut in its left tube's −X wall with the M6 × 25 pin, Ø19 access from C2's open bay. 1 × 45° lead-in on the lower edges of both faces (R-J9). H-04B bulb seal on C1's face beside the pin line, outer (roof) side (R-J17). |
| Bolts | 4 at the 220 mm rule: **4**. |
| Stack | 2.10 and ST-04 (2.11): with the ±0.1 spigot and panel tolerances the gap stays inside 4.0–7.0. |
| Check and pass mark | J-T3, J-T5. |
| Status | DECIDED (R-J11, R-J16); HOLD-05. |

### 3.7 J-FRONT-01: decor block to wall (IF-07)

| Field | Entry |
|---|---|
| Parts | DL to L1 and L2; DR to R1 and R2, at Y −645 with the 2.26 gap (R-J5). |
| Function and load path | Holds DL and DR upright against the side walls, carries the door's moment from DL into the left wall (ISS-045), seals. Weight goes down through the decor block onto the base band. Moment: hinges → DL's frame → back plate → bolts → the left wall's front member. |
| Loads | Door: a 152 N couple between hinges 1.8 m apart (assumption); misuse 391 N more (2.6), mostly at the top and bottom bolts. ISS-045 holds the full load path; this entry gives the joint's share. |
| Options compared | The build plan's V brackets with steel screws (BP-29; SEL A7, Simpson ABR7015): under the side lining in the 4 mm gap (F1), and screws aren't the M6 bolt; bolts from inside the decor block: DL has no access panel yet; **in-member bolts from the side wall's front bay into rivnuts in the decor's back plate (chosen)**. |
| Choice and reason | DECIDED fastener (R-J2, R-J10); design PROPOSED. |
| Nut side and bolt side | Nut side the decor block: rivnuts with stop washers in its back plate, which must be aluminium 1.0–2.7 mm thick at each bolt (2.7 for the grip with the washer, SHX; 1.0 minimum, assumption), with its frame behind (**HOLD-10**, FRONT). Bolt side: the side panel's front member (20 deep along Y), Ø7.0 in its front wall and Ø19 in its back wall, on its centre line X ∓1224, reached from the pocket in the side panel's front bay. |
| Bolts | 3 per side panel at the 220 mm rule: **12**. |
| Stack | 2.2: the tip runs into the hollow decor block. |
| Assembly | Walls first, then the decor blocks (LAY §5). **D-60:** the right-hand bolts are driven before the front-right air column goes in, and for take-down the column comes out first. |
| What can go wrong | No aluminium plate where a bolt lands (HOLD-10); rivnut pull-out under the door misuse moment (J-T1 at the DL load); the hinge pocket weakens DL's frame (ISS-045). |
| Check and pass mark | J-T1 at about 1.6 kN (assumption: 3 × the top bolt's share); the door sample (T13) with DL bolted to a wall piece. |
| Status | PROPOSED; HOLD-01, -02, -05, -10; ISS-045 open (FRONT). |

### 3.8 J-LIN-01: lining cassette clips (IF-10)

| Field | Entry |
|---|---|
| Parts | Each wall and ceiling cassette to its outer panel's frame: 8 wall cassettes and 2 ceiling cassettes. Clip 518001 (H-10), 44 per pod: 4 on each wall cassette, 6 on each ceiling cassette. Safety catch 518002 (H-11), 4 per pod: 2 on each ceiling cassette. |
| Function and load path | Hangs the cassette with no screw through it, so the inner leaf floats (D-17); holds it under its weight and knocks; ceiling cassettes can't drop (D-47). **Clip-only fixing, no rails (D-81):** the clips are the cassette's only load path; hook-and-loop only lines it up. Load: tray → clip → frame tube. The perimeter gasket in the 4 mm gap seals the cassette edge and carries no load. |
| Loads | Per clip, with a safety factor of 3 (assumption, as SEL A8 and the package's T07): a wall cassette of 11.1 kg (layout study) on 4 clips needs **8.3 kg rated in shear** per clip; a ceiling cassette on 6 clips needs 4.9 kg in pull-out for the P04 cassette of 9.77 kg (CEILING PR #32), and **8.0 kg** for the older 16 kg figure, which the package's T07 keeps. The catch: **48 kg working load per lanyard** (T08; 3 × 9.77 = 29.3 kg would do for the P04 cassette). Clip mass about 40 g, so 1.76 kg per pod (D-81's working figure; calculation). |
| Choice and reason | **HOLD (D-56, ISS-076, HOLD-08).** What the clip must meet, so CAD can reserve its space: (1) those rated loads; (2) captive: no unhooking without a deliberate lift (D-47); (3) fits the 4 mm frame-to-tray gap (`cav_gap`, D-16, D-42), or sits on the tray's 25 mm returns, clear of the Ø19 access holes and the pockets; (4) fixes to the 0.5 mm tray return and to a frame tube's face with small rivnuts or blind rivets, never through the ACP; (5) soft enough not to bridge the floating leaf (HW §10); (6) the ceiling catch anchors to a 20 × 40 ceiling tube, not the 20 × 100 SEL A8 names (ISS-079). |
| Assembly | Last, after every bolt is in and checked (LAY step 11); no tool. |
| Check and pass mark | T07 and T08 in the sample package; the wall sample is built with the real clips (HW §10). |
| Status | Requirements DECIDED (D-47, D-81); parts HOLD (HOLD-08); numbers 518001 and 518002 as CEILING uses them. |

### 3.9 Bolt count

| Joint | Bolts | Bolt |
|---|---:|---|
| J-WALL-01 horizontal seams | 16 | M6 × 16 |
| J-WALL-02 back corners | 12 | M6 × 16 |
| J-WALL-03 back closing seams | 6 | M6 × 25 pin |
| J-BASE-01 walls on the base band | 16 | M6 × 16 |
| J-CEIL-01 walls to ceiling | 16 | M6 × 16 |
| J-CEIL-02 ceiling closing seam | 4 | M6 × 25 pin |
| J-FRONT-01 decor to walls | 12 | M6 × 16 |
| **Total** | **82** | 72 × M6 × 16, 10 × M6 × 25 |

Every bolt carries one H-09 washer. Not counted: the base band's corner keys, the door hinges, the fixed glass profiles and DT to the ceiling. The layout study's decided build counts 78 bolts and 38 tool-free clips (LAY §4); R-J1 turns the seam and corner clips into bolts, which the PM set at about 12 more minutes of assembly.

### 3.10 Joint IDs against the layout study

| Layout study (LAY §2 tables) | This register |
|---|---|
| J-WALL-01 side horizontal seam; J-WALL-02 back horizontal seam | J-WALL-01 |
| J-WALL-03 back vertical seam | J-WALL-03 (now the closing seam) |
| J-WALL-04 side wall to back wall corner | J-WALL-02 |
| J-BASE-01 walls to base band | J-BASE-01 |
| J-CEIL-01 ceiling halves to walls; J-CEIL-02 ceiling half to half | J-CEIL-01; J-CEIL-02 (now the closing seam) |
| J-FRONT-01 decor blocks to walls, ceiling and base | J-FRONT-01 covers the decor to the side walls only; DT to the ceiling and the decor on the band stay with FRONT and BASE |

## 4. Tolerance stacks at the joint faces

Worst case, not the root of the sum of squares, unless marked: there are no process data yet (guideline §6.3).

| Stack | Contributors | Result | Status |
|---|---|---|---|
| ST-03: bolt in its Ø7.0 hole (R-J6) | Float (7.0 − 5.974) / 2 = 0.513; positions ±0.2 in each part from the spigot hole; rivnut float 0.065 | 0.05 to spare | calculation (CHK) |
| Spigot in hole and slot | Spigot Ø8 h9 in Ø8.5 H11 (assumptions); positions ±0.2 | Always enters; leaves up to ±0.25 of float, which the bolts take up | calculation |
| Outside faces flush across a seam | Frame depth 40 ±0.3 a panel (assumption); bond line 3 ±0.5 (bond spec); ACP 3 ±0.2 (assumption) | ±1.0 a panel unless the panels are bonded face down on a flat table with the ACP face as datum A (bond spec §5): then ±0.5 a panel, up to 1.0 between two | calculation; PROPOSED rule: the ACP face is datum A of every outer panel |
| Gap and squeeze at a stopped seam | Head 0.76 ±0.08 (SHX); stop washer 1.5 ±0.05 (assumption); gasket 3.97 ±0.4 (assumption) | Gap 2.13–2.39; squeeze 33–51% | calculation |
| ST-02: back wall closing gap and corner stops | 2.11, with ±0.1 spigot and spigot-to-face tolerances (PROPOSED) | Closing gap 5.2–5.8 inside 4.0–7.0; corner stops seat (±0.3 against ±0.25 play and ±0.26 float) | calculation |
| ST-04: ceiling closing gap | 2.11, same tolerances | 4.3–6.7 inside 4.0–7.0 (±2.0 at ±0.25 tolerances: too wide) | calculation |
| The lining floats clear of the frame at the bolts | Gap 4 (`cav_gap`, decided in SKL P04); every head inside its tube | Clear by design; the clip's own height is HOLD-08 | calculation |

## 5. Tests

Physical tests stay PLANNED until real data exists (guideline §10); the factory's wall-and-door sample is the physical check (D-32). **The sample package's tests take precedence** (R-J12): this register's rivnut, access and bond tests are folded into the package's T06, T11 and T09, which this PR updates to the joint as drawn. The tests the package doesn't have yet are listed as J-T1 to J-T5, for the PM to route into the package or a later sample.

| Test | What | On | Pass mark | Status |
|---|---|---|---|---|
| **T06** (package) | Rivnut spin-out with the joint's own stack: the CAH3-610-4.2 set through the 1.5 mm stop washer in a 40 mm face of the real 20 × 40 × 1.2 tube; torque applied by an M6 × 16 ISO 4762 with its ISO 7093 6.4 × 18 A2 washer, through a 1.2 mm wall coupon with a Ø7.0 hole; 2 cut open to check the bulge clears the far wall | S7 coupons | The package's PM-ruled limit: torque at most half the lowest spin-out torque, and no turning, loosening or stripping in 5 cycles; plus the wall under the head washer doesn't dish at that torque (R-J10) | PLANNED |
| **T09** (package) | The ACP bond (bond spec section 6) | S7 coupons; S1 | The package's PM-ruled pass mark: every coupon fails in the adhesive itself | PLANNED |
| **T11** (package) | Timed assembly: two people, one 5 mm key, carry S1, set it on its spigots, drive its 4 base bolts through the pocket, clip S2 on; 5 cycles | S1, S2 on R1 | The package's pass marks; and every bolt reached through its pocket | PLANNED |
| J-T1 | Pull-out and shear of a whole joint: M6 × 16 through a bolt-side tube into a rivnut and stop washer in a nut-side tube (20- and 40-deep), and a closing-seam pin | 5 of each | Failure at 3 × the joint's highest bolt load or more (assumption: about 0.6 kN for the walls, 1.6 kN for DL), no loss of fit after 5 cycles (REQ-ASM-09) | PLANNED, to route |
| J-T2 | Captive retainer: the bolt stays in its tube when the panel is shaken, carried and turned over; drives and backs out 5 times | 5 | Doesn't fall out; grips at least 3 × the bolt and washer's weight (assumption) | PLANNED, after HOLD-02 |
| J-T3 | Seams: gap at every bolt, flushness, gasket squeeze, light and air through the seam; push test at 1.2 m with LC2; on one stopped seam and one closing seam set at 4.0 and 7.0 | wall sample or a seam mock-up | Stopped gap 2.26 ±0.15; faces flush within 0.5 (assumption); no light through either seam; no step after the push | PLANNED, to route |
| J-T4 | Base seal on a floor stepped ±5 mm | base band piece (R1) | Touches all the way along; checked with a light from inside | PLANNED, after HOLD-06 |
| J-T5 | Corner and ceiling mock-up: a side panel corner, the back closing seam, and both ceiling halves closed in the R-J9 order | joint mock-up | Every bolt reached, overhead too; **every part drops in or slides past its seal with 150 N or less per edge by hand, overhead included** (push-pull gauge; R-J17); C2 drops in past the lead-in; the corner stops close with the bolts; faces flush within 0.5 | PLANNED, to route |

## 6. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Owner | Released when |
|---|---|---|---|---|
| HOLD-01 | Rivnut tightening torque (D-48, ISS-011) | None: T06 sets it | Hardware Engineer | T06 recorded and the PM sets it (package H05) |
| HOLD-02 | Captive retainer (H-02): an elastomer grommet for a Ø19 hole in 1.2 mm aluminium that grips an M6 socket head (Ø10) | Which grommet, with what grip on the head, survives 5 drive-and-back-out cycles? | Joints Engineer with the Hardware Engineer | Part named; J-T2 passed (package H13) |
| HOLD-03 | Rivnut head thickness and installed length | — | — | **Closed** (SHX) |
| HOLD-04 | Rivnut edge distance | To Sherex: minimum distance from a Ø9.53 hole to the edge of a 1.2 mm aluminium face; is 9.2 mm (the corner and ceiling bolt lines, 2.4) enough? | Hardware Engineer | Answer on file, or T06's coupons show no cracking |
| HOLD-05 | Joint gasket thickness and converter | PORON 4701-40 with adhesive in 8 mm strips, 3.97 mm thick | Hardware Engineer | The converter's strip data on file (package H14) |
| HOLD-06 | Base seal for a 10 ± 5 mm gap (H-06) | Which bulb or brush seal closes 5–15 mm under an aluminium band, with a published range? | BASE engineer | Part named; J-T4 passed |
| HOLD-07 | Base band top wall 2.7 mm or thinner (grip with the stop washer) | None: BASE design | BASE engineer | Band drawing with its wall thickness |
| HOLD-08 | Cassette clip 518001 and ceiling catch 518002 (D-56, ISS-076) | SEL question 10, plus points 1–6 of J-LIN-01: a clip rated for 8.3 kg in shear and 8.0 kg in pull-out with a captive lock that doesn't bridge the lining; a lanyard rated for 48 kg | Hardware Engineer; Layout Engineer | Parts with ratings named; T07 and T08 passed |
| HOLD-09 | Frame tube alloy, temper and E (ISS-034) | None: D-79, pending in the control pack, names 6063-T6, mill finish | Hardware Engineer | D-79 merged; 2.5 re-checked with 6063-T6 |
| HOLD-10 | Decor back plate at the J-FRONT-01 bolts: aluminium 1.0–2.7 mm with the frame behind (ISS-045) | None: FRONT design | FRONT engineer | FRONT CAD shows it |
| HOLD-11 | The back wall's top edge under the ceiling | — | — | **Closed** (R-J4) |
| HOLD-12 | Closing-seam bulb seal (H-04B, 848004) | Which EPDM or TPE hollow bulb has a published working gap covering 4.0–7.0 mm and a closure force low enough for a 150 N fit-up per edge, and survives being reused? (The tesamoll D-Profile's 3–7 mm range is published; it is consumer grade, with no force data) | Hardware Engineer | Part named with its range and force; J-T5 and J-T3 passed |

## 7. Open for others

1. **Skeleton (Fusion Engineer 2):** the closing gap 5.5 at X 0 for the back wall and the ceiling, so the frames are 1198.99 wide while the skins stay 1200.61 (2.8, R-J16); the 220 mm bolt rule on every bolted edge (2.9); the bolt lines at the tube centres, Y +824 and Z 2374 (2.4, R-J15).
2. **BASE, WALL and CEILING drawings:** every stile at least 30 mm from a bolt (R-J14); ±0.1 on every spigot position and every panel's spigot-to-joint-face distance (ST-02, ST-04); the skins' 1.62 mm overhang at the closing seams (FR-14); the outside corner and the back top edge, where the side panels' back members and the ceiling's back member show (3.2).
3. **Decision log (control pack):** rows for R-J1 to R-J16, including the parts of D-08 (tool-free seam clips) and D-49 ("face to face") they change.
4. **Sample package:** P05–P07 and the new head washer and retainer rows, T06's stack, T09's bonded face, H13 and H14 are updated in this PR (R-J12); J-T1 to J-T5 wait for the PM to route.

## 8. Feature-rationale inputs for the Fusion Engineers

What each joint puts into each part, and why (guideline §7). "Nut side" and "bolt side" as in 2.2. Hole tags go on the drawings. X and Y are the pod axes (conventions §4).

| ID | Part | Feature | Size | Where (rule) | Why | Status |
|---|---|---|---|---|---|---|
| FR-01 | Nut side of every stopped joint: lower panels' top tubes; the band's top wall; side panels' 40 × 40 back members; upper side panels' 40 × 40 top members; ceilings' 40 × 40 back members (bottom face); the decor's back plate. Bolt side of the closing seams: B2's, B4's and C2's left tubes | Rivnut hole (with the H-08 stop washer, except at the closing seams) | Ø9.53 +0.10 through one wall of 2.7 or less | At the 220 mm rule (2.9), on the bolt-side tube's centre line | H-03 needs it (SHX); the stop sets 2.26 (2.8) | source (hole); positions DECIDED for the band, PROPOSED elsewhere |
| FR-02 | Bolt side of every stopped joint: upper panels' bottom tubes; walls' bottom tubes; back panels' outer tubes at the corners; ceilings' side tubes; back panels' top tubes; side panels' front members. Nut side of the closing seams: B1's, B3's and C1's right tubes | Clearance hole | **Ø7.0, position Ø0.4 (±0.2) from the spigot hole, CNC or drill jig** | Coaxial with FR-01 | ST-03 (R-J6) | DECIDED |
| FR-03 | Every bolt-side tube | Access hole in the bay-side wall | **Ø19** | Coaxial with FR-02, or with FR-01 at the closing seams | Passes the Ø18 head washer, the Ø10 head and the key (2.2) | calculation |
| FR-04 | The band's top wall; lower panels' top tubes; back panels' top tubes under the ceiling | Spigot rivnut | Ø9.53 +0.10 | 100 from each end (R-J13) | Holds H-05; the part stands located before its first bolt (REQ-ASM-04) | DECIDED for the band; PROPOSED elsewhere |
| FR-05 | Walls' bottom tubes; upper panels' bottom tubes; ceilings' back members (bottom face) | Spigot hole and slot | Ø8.5 round at one end, 8.5 × 14 slot at the other: along the edge, except **along X at the side panels' back ends** (R-J17) | Coaxial with FR-04 | One fixed point and one slot (R-J13); the side panels drop clear of the corner gasket (2.7) | DECIDED |
| FR-06 | Side panels' back members (L1, L2, R1, R2); upper side panels' top members (L2, R2); ceiling halves' back members (C1, C2) | Member size | 40 × 40 × 1.2 instead of 20 × 40 × 1.2 | Whole length of that edge | Overlap 34 instead of 14 (2.4) | DECIDED (R-J3); +1.29 kg |
| FR-07 | Back panels' outer tubes at the corners; back panels' top tubes; ceilings' side tubes | Bolt line | Y +824 or Z 2374 | The bolt-side tube's centre | Room for the Ø19 hole (2.4) | DECIDED (R-J15) |
| FR-08 | Side panels' front members | FR-02 and FR-03 pair, along Y | as FR-02, FR-03 | 3 per panel at the 220 mm rule, X ∓1224 | J-FRONT-01 | PROPOSED |
| FR-09 | Every site joint | Frame gap | 2.26 stopped; 5.5 (4.0–7.0) closing | 2.8 | Gasket squeeze set by the stop or the gap | DECIDED (R-J5, R-J16) |
| FR-10 | Wall panel bays at each bolt (bolt side) | Fill pocket | 60 × 60 × 40, no fill; every stile at least 30 mm from the bolt | In front of each FR-03 | The key's reach (2.3); R-J14 | PROPOSED pocket (assumption); 30 mm DECIDED (R-J14) |
| FR-11 | Every joint face (nut side) | Seal | Stopped joints: PORON strip 8 × 3.97 (848001). Closing seams: the bulb seal (848004) | Beside the washer or pin line, outer side, unbroken | R-J7, R-J17, 2.5 | DECIDED (R-J7, R-J17); parts HOLD-05, HOLD-12 |
| FR-12 | Frame tubes behind the cassette clips and the ceiling catch | Clip and catch fixings | HOLD-08 | Reserve an UNVERIFIED envelope only | D-47, D-56 | HOLD |
| FR-13 | The closing seams' faces | Lead-in chamfer | 1 × 45° | C1–C2 lower edges; B1–B2 and B3–B4 top edges | R-J9 (2.10) | DECIDED (R-J9) |
| FR-14 | Back panels' and ceiling halves' skins (B1–B4, C1, C2) | Skin width and overhang | Skin 1200.61 on a 1198.99 frame: flush at the stopped edge, 1.62 past the frame at the closing seam | The closing-seam edge: right edge on B1, B3, C1; left edge on B2, B4, C2 | Visible skin seam 2.26 nominal everywhere, 0.76–3.76 at the closing seams (2.8) | DECIDED (R-J16) |

Rules for the Fusion check (each can be a scripted check):

- R1. Every FR-01 has a coaxial FR-02 (or, at a closing seam, FR-02 on the other part) and FR-03, within Ø0.4 of the spigot datum (R-J6).
- R2. No rivnut or clearance hole's edge closer than 9 mm (assumption) to the edge of its face; no Ø19 access hole's edge closer than 9 mm to the tube's inner walls (2.4).
- R3. Nothing stands proud of a frame tube's room-side face except the clips (F1).
- R4. Every bolt tip clears the far wall of its tube by at least 3 (2.2, 2.10).
- R5. Every FR-03 in a wall panel has its FR-10 pocket, with no fill or cable in it, and every stile at least 30 mm from the bolt (R-J14).
- R6. Every part that goes on site stands on an FR-04/FR-05 pair before its first bolt (REQ-ASM-04).
- R7. Two bolts in the BOM for every site joint: 838001 (M6 × 16) and 838002 (M6 × 25), ISO 4762, 8.8, each with an 838004 washer (REQ-ASM-02, R-J2, R-J10); every hardware item in the CAD and BOM carries its part number from 2.1.
- R8. No clip (FR-12) over an FR-03 hole or an FR-10 pocket.
- R9. Every stopped joint's frames are 2.26 apart and every closing seam's 5.5; every visible skin seam is 2.26 (R-J16); every stopped rivnut with its washer sits on a 40 mm face.
