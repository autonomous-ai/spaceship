# Joints register: Spaceship (FocusPod v2), Milestone 2 sample set

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-01 (row in `document-register.csv`) | P01 | DRAFT | 2026-11-01 | Joints Engineer (v2 Milestone 2) |

This is the joint register the guideline asks for (§8, and Milestone 2 item 6), for the site joints of the sample set: wall to wall, wall to floor (base band), wall to ceiling, back corner, decor to wall, the closing seams, the lining cassette clips, the base band's hook-in corner keys, the decor blocks on the band, on DR's support and under the ceiling, the air parts' hooks (the soffit and the air column) the fixed glass channel's screws, the roof grille's screws (J-AIR-03), and the frames' own welded joints (J-FRAME-01, D-131). It also gives the feature-rationale inputs (§7) the Fusion Engineers need (section 8), the seam gaps and bolt positions the skeleton needs (sections 2.8 and 2.9), and the closed-chain stacks ST-02 and ST-04 (section 2.11).

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
  - **R-J18** (Reviewer 7) the cassette edge seal H-14 seals at near-zero squeeze in the 2.26 mm gap, carrying no load (J-LIN-01): a very soft strip about 2.0–2.2 mm thick, or a fin, that only touches; a 3.18 mm strip at 29% would push about 0.6 kN along a 1.45 m edge and lift the upper cassette off its clips.
- **HOLD:** a part or number that waits for data or a test. CAD may reserve a space for it, marked UNVERIFIED, but doesn't use its hole pattern until it's released (guideline §4.3 step 4; D-56). Section 6 lists every HOLD with its question.
- **Not covered here:** the ACP-to-frame bond is in [`bond-spec-acp-aluminium.md`](bond-spec-acp-aluminium.md). Door hinges, the fixed glass and the decor top block's joint to the ceiling (IF-08, IF-09) belong to FRONT; the thin floor and the band's end caps, which carry the corner keys' keyholes, to BASE.
- No supplier was contacted and nothing was ordered. Data comes from the files below and from public pages, each linked with the date read.

## Result

1. **Two bolts, one key:** every site joint uses an **M6 ISO 4762 socket head, class 8.8, zinc plated, with an ISO 7093 6.4 × 18 A2 washer under the head**, driven with one 5 mm key (R-J2, R-J10). **M6 × 16** at the 72 stopped joints, threaded into a Sherex CAH2-610-4.2 rivnut (zinc-plated steel since D-131; it replaced the aluminium CAH3-610-4.2, with the same head and grip); **M6 × 25** as a pin at the 10 closing-seam positions and as the soffit's 2 lock screws. **92 site bolts** in all: the 82 of the walls and ceiling, 4 for DT, the soffit's 2 lock screws and the roof grille's 4 (section 3.9). The bolt lives inside an edge tube of the part placed second and is driven from inside the pod before the linings go on (section 2.2).
2. **Seam gaps for the skeleton:** **2.26 mm** at every stopped seam (R-J5), set by a metal stop: rivnut head 0.76 (Sherex) on a 1.5 mm aluminium stop washer. **5.5 mm nominal (4.0–7.0) at the three closing seams** B1–B2, B3–B4 and C1–C2 (R-J11, section 2.10). So the back panels' and ceiling halves' **frames become (2408 − 2 × 2.26 − 5.5) / 2 = 1198.99 wide**, against 1200.61 in skeleton P04 (calculation), while **their skins stay 1200.61 and overhang the frame by 1.62 mm at the closing seam**, so every visible skin seam stays 2.26 nominal (R-J16).
3. **Bolt positions follow one rule on every bolted edge** (R-J13, R-J14): end bolts 220 mm in from each panel end, evenly spaced between, every bolt at least 30 mm clear of any stile; 4 on the horizontal edges and 3 on the vertical edges of about 1.1 m; spigots 100 mm in from each end (section 2.9). The register owns the bolt lines (R-J15).
   - **Every outside fixing is now in the register** (D-87; the assembly guide's assumptions): the base band's **6 corner keys hook in** with no site bolt (J-BASE-02: one machined block in four cuts and two fixing-hole layouts: 111211 square at the two back corners, 111215 square at the FR1 inline joint, 111212 and 111213 at the front corners, 111214 at the left knee; positions in [`corner-keys.csv`](../../01-CAD-Native/joints/corner-keys.csv)); **DL stands on 2 spigots on the band and DR on 2 spigots on its support**, held by their J-FRONT-01 bolts, so they need no bolt of their own (J-FRONT-02); **DT sits on 2 spigots on DR's ledge (none under DL) and takes 4 bolts from the ceiling's front tubes** at the 220 mm rule, which also hold its DL end (J-FRONT-03). That turns the guide's 8 assumed fixings into 4 bolts.
   - **Wall-to-ceiling bolt lines confirmed:** side edges from Y −645 along the ceiling (1495 long), pitch 351.67, at Y −425.00, −73.33, +278.33 and +630.00; back edges on the frame (1198.99), pitch 253.00, 4 per back panel (2.9). Skeleton P04 still carries 3 bolts on the back edges on the skin width and the side pitch on the side panel's 1492.74; it follows this register.
   - **The air parts and the fixed glass channel are fixed with registered hardware too** (D-87 and the PM rulings of 2026-11-01): the soffit hangs on 4 factory-set hanger studs and is locked by 2 captive M6 × 25 screws turned with the 5 mm key (J-AIR-01); the air column hooks onto 2 studs in DR's access panel and drops onto 2 spigots on the floor panel F2 (J-AIR-02); the fixed glass's bottom U-channel is screwed to BASE's sill at the factory with 4 M3 countersunk screws in M3 countersunk rivnuts (J-FRONT-04); the roof grille is screwed down over the roof sleeve's flange on site with 4 M6 × 16 into rivnuts in that flange (J-AIR-03). The soffit's lock screws and the grille's screws add 6 site bolts: **92 in all**.
4. **Seals:** at every stopped joint, PORON 4701-40 foam, 8 mm wide, beside the washer line on the outer (skin) side of the nut-side face, so no seal is cut (R-J7): **3.97 mm thick, squeezed 33–51%** (43% nominal). At the three closing seams, **a low-force hollow bulb seal (EPDM or TPE) whose working gap covers 4.0–7.0 mm** (R-J17), which needs no squeeze at fit-up and can be reused when the pod is moved; the part is HOLD-12. **Fit-up:** every part drops in or slides past a seal with 150 N or less per edge by hand (J-T5, R-J17): the side panels' back-end spigots are slotted along X so they drop clear of the corner gasket, and the side walls' tops lean out for the ceiling (R-J9).
5. **Holes:** clearance Ø7.0 positioned to ±0.2 from the spigot hole (R-J6), leaving 0.05 mm to spare worst case (stack ST-03, section 4); access Ø19, so the Ø18 head washer goes in with the bolt (section 2.2).
6. **Findings carried from the first pass:** F1, no room-side hardware in the 4 mm frame-to-lining gap; F2, the 90° joints overlap only 14 mm with 20 × 40 tubes, 34 mm with the 40 × 40 edge members (R-J3); F3, seams need clamping force (R-J1); F4, the bond doesn't fit the 20 mm face as Sika lays it out (bond spec B1); F5, the back-top gap (closed by R-J4); F6, one head type (R-J2).
7. **Part numbers and per-pod counts** for every hardware item, in 2.1: bolts 838001 (80 on site, 18 in the factory) and 838002 (12), rivnut 838003 (126), head washer 838004 (92), the corner keys' button head screw 838010 (12), retainer 838005 (76), spigot 831001 (30), stop washer 831002 (76), M3 countersunk screw 838007 (4), M3 countersunk rivnut 838008 (4), M6 insert for the floor ply 838009 (2), joint gasket 848001 (26.9 m), closing-seam bulb seal 848004 (3.73 m), base seal 118001 (BASE's length), key 108001 (1), cassette clip 518001 (44), ceiling safety catch 518002 (4), ACP bond set 108002 (4.4 kg), hook-and-loop 848011 (1.6 m on the walls), cassette edge gasket 848012, the access-panel seal 848013 (DR's inner face panel), the kick strip's two end seals, 368008 (D-150) and the hinge end's (its number from Control), both FRONT's and fitted on site, the plain M6 washer 838011 under DR's inner panel screws (21, D-142), and the corner keys 111211 (2), 111215, 111212, 111213 and 111214 (1 each, J-BASE-02). 848002, 848003 and 848010 are cancelled (never used again, conventions §6). FRONT's 10 bought items, 368001 to 368007 and 368101 to 368103, and BASE's three, 118002, 838006 and 118003, are adopted as their teams numbered them (2.1).
8. **HOLDs: 16 open, 4 closed** (section 6). **Tests** take the sample package's numbers: rivnut spin-out **T06**, bond **T09**, timed access **T11**; the joint tests the package doesn't have are **J-T1 to J-T7**, for the PM to route (section 5).
9. **Frames (D-131, J-FRAME-01): welded, galvanized steel** with the same outside sections. **1.2 mm** for the side panels' rails and front stiles (PM ruling, for margin); **1.0 mm** for every other perimeter member, every 40 × 40 member and every member with a site joint; **0.8 mm** for the studs (5 in each side panel and 3 in each back panel, D-135) and the ceiling's cross members 2 and 3; every frame at 90% or less at the thinnest wall. Steel with a yield of **280 MPa or more**, **Z100** zinc, walls at least 95% of nominal. **Mitred corners with a 2 mm plate in each mitre**; corners and T joints welded all round in a jig (MIG brazing preferred); no hot-dip after welding, so no vent holes; every joint hole and rivnut after welding; **seam faces flat to 0.5**. Rivnut 838003 is now the **zinc-plated steel CAH2-610-4.2 with the same head**, so the seams stay 2.26. The bond moves to **Sikaflex-252**, whose data sheet lists galvanized steel, with Aktivator-205 and Primer-210 (bond spec section 8). The 10 frames weigh 81.3 kg against 29.0 in aluminium (**+52.3 kg**, calculation); every panel is 12.8 to 18.0 kg.

## 1. Sources

| Key | File or page | Used for |
|---|---|---|
| GL | `docs/engineering-guideline.md` §6.3, §7, §8, §8.1, §8.2, §10 | Register fields, bolt and bond rules, test status |
| DL | `v2/00-Control/decision-log.md`, D-01 to D-60 | Decided stack, clips, holds, the D-60 air layout |
| PM | PM rulings R-J1 to R-J18 in the joints group, 2026-10-31 | As listed above |
| REQ | `v2/00-Control/requirements.md` | REQ-ASM-02 to -11, REQ-BLD-01, -02 |
| IF | `v2/00-Control/assembly-tree.md` §4 | IF-01, IF-03 to IF-07, IF-10 |
| ISS | `v2/00-Control/issue-register.csv` | ISS-003, -011, -014, -015, -016, -034, -036, -045, -054, -064, -076, -079 |
| SEL | `v2/05-Engineering/hardware/selection.md` | Rivnut A5, bracket A7, clips A8, gaskets and base seal D, sample tests |
| HW | `v2/05-Engineering/acoustics-air/report.md` §1, §8, §10 | Stack layers, cassette mass, clip risk |
| LAY | `v2/05-Engineering/layout-study/report.md` §4, §5 | Assembly order, one 5 mm key, bolt and clip counts, base band and glides |
| SKL | `v2/01-CAD-Native/skeleton/` P04: `100000_P04_POD-SKELETON-PARAMETERS.csv` (`outer_t` 46, `cav_gap` 4, `seam_gap` 2.26, `half_pw` 1200.61, `side_h` 1142.74, `side_l` 1492.74, `back_ph` 1118.61, `panel_z0` 112.26) | Envelopes and positions |
| GUIDE | `v2/02-Drawings/30-Assembly-Instructions/100000_P04_POD-ASSEMBLY-GUIDE_INS.md`, its section 5 table of fixings the register didn't count | DL on the band, DR on its support, DT, the corner keys |
| BASE | BASE's draft PR #55 (P01: the back-left corner and F1): `110000_P01_BASE_BOM.csv` and the tube cut list | Band tubes 100 × 40, glides 2 per side band and 3 in the back band, M10 glide nuts, tube end caps, the bolted corner bracket 111201 that the keys replace |
| FRONT-GEO | BASE's front band geometry, relayed by the PM in the joints group on 2026-10-31: every front piece 100 × 40 × 1.5, Z 10 to 110, outer-face points in pod X, Y | The front corner and knee keys' cuts and positions (J-BASE-02, `corner-keys.csv`) |
| CEIL | CEILING's PR #32 (`ceiling_model.py`, `FEATURE-RATIONALE.md` F-4111-13) and its air branch (`v2/01-CAD-Native/air/air_model.py`), read 2026-11-01; PM rulings of 2026-11-01 (D-87 hooks) | The soffit's hanger and lock rivnuts, rails and slide; the air column's hook studs, keyholes and floor spigots (J-AIR-01, J-AIR-02) |
| PKG | Packing list on main (PR #84): the fixed glass's bottom U-channel ships fitted on BASE's sill (PM ruling) | J-FRONT-04 is a factory fixing |
| SMP | `v2/06-Samples/wall-door-sample/` (parts list, test plan, hold list) | Sample package: P05–P07, T06, T09, T11, H13 |
| CHK | Mechanical Checker findings F-001, F-008, F-009, F-011, F-012, F-013 and stacks ST-02, ST-03, ST-04 | Gaps, hole float, closed chains |
| SHX | Sherex [CAH3-610-4.2 product page](https://fasteners.sherex.com/item/nd-rivet-nuts-american-style-rivet-nuts-cah-series/cah-series-aluminum-metric-/cah3-610-4-2-1), read 2026-10-31 | Head Ø12.96 ±0.25 × 0.76 ±0.08; length 14.86 ±0.38; installed length 10.16 max; body Ø9.50 max; open end; aluminium 5056; grip 0.70–4.20; hole 9.53 +0.10; "trial installations" recommended |
| SPC | Sika [pre-treatment chart for 1-component polyurethanes, Sikaflex-100 and -200 series](https://aus.sika.com/dms/getdocument.get/c080b021-d54c-4ad5-821f-0bd2efa46f1e/Pre-treatment_Chart_1C_PU_2020.pdf) (2020) and its [2015 edition for the Sikaflex-200 and SikaTack series](https://dnk.sika.com/dms/getdocument.get/11c7e2c7-7206-32f1-a734-8f8df9a1e7c8/Pre-treatment_Chart_1C_PU_2015_V6%2006%2015.pdf), read 2026-11-01 | Steel, hot-dip galvanized and electrogalvanized, level 2 (interior and exterior bonding under normal conditions): abrasive pad and clean, Sika Aktivator-205, Sika Primer-210 (or Aktivator-100 with Primer-206 G+P); "must be verified by tests on original substrates" |
| SHX2 | Sherex [CAH2-610-4.2 product page](https://fasteners.sherex.com/item/nd-rivet-nuts-american-style-rivet-nuts-cah-series/cah-series-metric-thread-unit-mm-/cah2-610-4-2), CAH Series, Steel (Metric), read 2026-11-01 | Steel 1008/1010; M6 × 1.0; grip 0.70–4.20; head Ø12.96 ±0.64 × 0.76 ±0.08 (the CAH2-610-4.2 item page's own figures; T06 measures the head on its coupons too, since every 2.26 seam rests on it); length 14.86 ±0.38; installed length 10.16 max; body Ø9.50 max; open end. Finish: the series page gives zinc plated with a yellow trivalent chromate (SFS-01-001, SC2), the item page zinc plated with a yellow dichromate (ASTM B633 Fe/Zn8, Type II); no hole size on the item page. "Trial installations" recommended |
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
| H-03 | **Rivnut.** Sherex **CAH2-610-4.2**, open end, **steel 1008/1010, zinc plated** with a trivalent passivation (D-131 and the Lead's design review, 2026-11-01: steel in the steel frames, and in the aluminium parts too, so the pod keeps one rivnut; it replaced the aluminium CAH3-610-4.2 before any was bought, with the same form and fit) | M6 × 1.0; grip 0.70–4.20; head Ø12.96 × 0.76 ±0.08, so the stopped seams stay 2.26 (D-64); installed length 10.16 max; body Ø9.50 max (SHX2); hole Ø9.53 +0.10 as the aluminium part's (SHX; unverified for the steel part, HOLD-04) | source; torque **HOLD-01** (D-48); edge distance **HOLD-04** |
| H-04 | **Joint gasket, stopped joints.** Rogers PORON 4701-40 Soft with pressure-sensitive adhesive, 3.97 mm thick, 8 mm wide, on the nut-side face beside the washer line (R-J7, R-J17) | 41 kPa at 25% compression; compression set ≤ 5% at 23 °C (ASTM D3574 D); 3.18–12.70 mm listed (SEL D) | source; the 3.97 thickness and the converter **HOLD-05** |
| H-04B | **Closing-seam seal.** A low-force hollow bulb (D or P profile) in EPDM or TPE, on the nut-side face beside the pin line, whose published working gap covers 4.0–7.0 mm (R-J17); reusable | Candidate with a published range: tesa tesamoll D-Profile EPDM, gaps 3–7 mm (SEL D; consumer grade). Closure force not published | requirement DECIDED (R-J17); part **HOLD-12** |
| H-05 | **Locating spigot.** Ø8 stainless pin with an M6 thread, screwed into an H-03 rivnut at the factory with threadlocker. A part we make. | Ø8, stands 8 proud | PROPOSED (assumption sizes) |
| H-06 | **Base seal (D-132: no floor).** A soft lip bonded along each band piece's inner face at the factory, pressing on the room floor, so v1's open shadow line under the band stays and DR's intake under the block stays clear. It doesn't run across the door opening, where the door's drop seal closes on the room floor (D-132). Under DR it runs along BASE's closing plate, not behind the mesh piece (AIR's check) | Reaches 21.5 below the band's bottom, so it touches the room floor at any glide setting from 8.5 to 18.5 (BASE, calculation; the glide's travel is an assumption until it is named) | DECIDED place (D-132); part **HOLD-06** |
| H-07 | **One tool.** A 5 mm ball-end hex key, or a 5 mm hex bit in a short driver (LAY §4) | — | DECIDED (R-J2) |
| H-08 | **Stop washer.** Aluminium, Ø10.5 × Ø20 × 1.5, clamped under each stopped-joint rivnut's head when the rivnut is set. A part we make (punched from 1.5 mm 5000- or 6000-series sheet). | Grip with it: 1.0 + 1.5 = 2.5 in the 1.0 mm steel frames (D-131), inside 0.70–4.20 (SHX2); needs a 40 mm face | PROPOSED; thickness ±0.05 (assumption) |
| H-09 | **Head washer.** ISO 7093-1 large series, 6.4 × 18 × 1.6, A2 stainless, under every bolt head (R-J10) | (ISO7093) | DECIDED (R-J10); dimensions source |
| H-10 | **Lining cassette clip.** The only fixing between each lining cassette and its outer panel's frame: clip-only, no rails (D-81). It must carry a rated load, have a captive lock, and never bridge the floating lining (D-17, D-47; J-LIN-01) | Rated load at least 8.3 kg in shear per wall clip and 8.0 kg in pull-out per ceiling clip (the sample package's T07 limits, calculation, safety factor 3 as an assumption); about 40 g each (D-81's working figure, assumption) | DECIDED requirement (D-47, D-81); part **HOLD-08** |
| H-11 | **Ceiling cassette safety catch.** A steel wire lanyard with a rated working load and its two end fixings, from the ceiling cassette's return to a 20 × 40 ceiling tube (D-47) | At least 48 kg working load per lanyard (the package's T08 limit: 3 × a 16 kg cassette; the P04 cassette is 9.8 kg, CEILING PR #32, so this covers it) | DECIDED requirement (D-47); part **HOLD-08** |
| H-12 | **ACP bond set.** The bond spec's system as one bought set (D-137, for D-131's galvanized steel frames): **Sikaflex-252** adhesive, **Sika Aktivator-205** and **Sika Primer-210** on both faces, and SikaTack Panel Fixing Tape 3 × 12 as the 3 mm spacer (bond spec section 8; it was SikaTack Panel-50 with SikaTack Panel Primer, whose data sheets list no galvanized steel) | About 0.49 kg per side panel, 4.4 kg per pod (bond spec section 8, calculation) | source (bond spec section 8, D-137); in-line tape layout HOLD-B2; Sikaflex-252 with the tape and on our tube HOLD-B4, HOLD-B6 |
| H-13 | **Hook-and-loop, locating only.** Lines a cassette up on its frame before the clips take it; never holds it (D-47) | VELCRO® Brand PS14 hook 25 mm, or 3M Dual Lock SJ3560 (SEL A8; no load rating, locating only) | source (candidates); choice open |
| H-14 | **Cassette edge seal.** Seals the 2.26 mm gap where a cassette meets the next one, **at near-zero squeeze and with no load** (R-J18): a very soft foam strip with pressure-sensitive adhesive, 2.0–2.2 mm thick and 10 mm wide, that only touches, or a flexible fin that wipes the other edge | Its push at the smallest gap must stay under a quarter of the upper cassette's weight per length: about 0.02 N per mm of edge (assumption; the cassette is about 11 kg on a 1.45 m edge, 0.075 N/mm, calculation), so about 2 kPa at 20% compression for a 10 mm strip. PORON 4701-40 is about 20 times too stiff (41 kPa at 25%, SEL D). Not for DR's access and inner panels, which sit on 2.36 stops: see H-34 | requirement DECIDED (R-J18); part **HOLD-13** |

Every rivnut, stop washer, spigot, gasket, retainer and pre-fitted bolt is fitted in the factory (D-08, REQ-ASM-10); on site only the bolts are turned. Every joint rivnut sits on a 40 mm tube face (or the decor's back plate).

**Part numbers** (conventions §5 and §6: 6 digits, FF NNNN; family 83 HARDWARE, 84 SEALS AND TAPES, 11 BASE, 51 LINING, 10 POD general items and the installation kit; NNNN 1000–7999 for parts we make, 8000–8999 for bought catalogue items). Given here at the PM's request so the master BOM can match every team's hardware to this register (D-63: the register owns the one list); the master BOM adopts them. None is on the reserved list (D-28), and none was in use on main or in the open pull requests on 2026-10-31 except 518001 and 518002, which CEILING already uses for the clip and the catch and which this register adopts. The stopped-joint gasket and the closing-seam bulb are different parts, so each has its own number (one number covers one form, fit and function, conventions §6); a cancelled number stays cancelled. The per-pod counts are calculation from the joint entries (section 3) and the panel sizes (2.8).

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-01 | **838001** | HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC · Bulong lục giác chìm M6 × 16 | bought | 80 on site (72 at the walls and ceiling, 4 for DT, 4 for the roof grille, J-AIR-03) and 18 in the factory (the 6 corner keys' 12 hook studs, J-BASE-02; the soffit's 4 hanger studs, J-AIR-01; the air column's 2 hook studs, J-AIR-02) | PROPOSED number; part DECIDED (R-J2) |
| H-01P | **838002** | HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC · Bulong lục giác chìm M6 × 25 (chốt mối nối khép) | bought | 12: 10 closing-seam pins and the soffit's 2 lock screws (J-AIR-01) | PROPOSED number; part DECIDED (R-J16) |
| H-02 | **838005** | HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE · Vòng giữ đầu bulong | bought | 76 (the stopped-joint bolts on site; the pins and the factory bolts need none; the soffit's 2 lock screws are held captive in the soffit's rail by AIR's retainer, as HOLD-02) | PROPOSED number; part HOLD-02 (number kept for it) |
| H-03 | **838003** | HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2 · Tán rút M6 thép mạ kẽm | bought | 126 (76 stopped joints, 10 closing-seam pins, 28 spigots, the soffit's 4 hanger studs and 2 lock screws, the air column's 2 hook studs, the roof grille's 4 in the sleeve's flange) | PROPOSED number; part source (SHX2), re-specified to steel before any was bought (D-131; the Lead's review); Control updates the master BOM's name |
| H-04 | **848001** | SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA · Gioăng mối nối 3.97 | bought by length | 26.9 m (every stopped joint, DT's 1.65 m included) | PROPOSED number; strip HOLD-05 |
| H-04B | **848004** | SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE · Gioăng ống mối nối khép | bought by length | 3.73 m (the three closing seams) | PROPOSED number; part HOLD-12 |
| H-05 | **831001** | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS · Chốt định vị Ø8 | made | 30 (8 on the band, 8 on the horizontal seams, 4 under the ceiling, 2 under DL, 2 under DR, 2 under DT, and 2 on the floor panel F2 under the air column, J-AIR-02) | PROPOSED number and part |
| H-06 | **118001** | BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD · Gioăng chân đế - môi mềm trên sàn | bought by length, used only in BASE | BASE's length along the band pieces' inner faces, none across the door: about 6.0 m for the side bands, the back band and FR1 so far; the front-left pieces and the intake piece add theirs (BASE) | PROPOSED number, renamed for D-132 to BASE's name; part HOLD-06 |
| H-07 | **108001** | POD - HEX KEY - 5 MM BALL END · Lục giác 5 mm đầu bi | bought, in the installation kit 109000 | 1 | PROPOSED number; part DECIDED (R-J2) |
| H-08 | **831002** | HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL · Long đen chặn nhôm | made | 76 (one under each stopped-joint rivnut) | PROPOSED number and part |
| H-09 | **838004** | HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2 · Long đen to M6 inox | bought | 92: one under each site bolt's head (the corner keys' fixing screws have flanged heads and need none) | PROPOSED number; part DECIDED (R-J10) |
| H-10 | **518001** | LINING - CASSETTE CLIP · Kẹp treo cassette | bought, used only in LINING | **44**: 4 on each of the 8 wall cassettes, 6 on each of the 2 ceiling cassettes | number as CEILING uses it (PR #32); part HOLD-08 |
| H-11 | **518002** | LINING - CEILING SAFETY CATCH · Dây an toàn cassette trần | bought, used only in LINING | **4**: 2 on each ceiling cassette | number as CEILING uses it (PR #32); part HOLD-08 |
| H-12 | **108002** | POD - ACP BOND SET - SIKAFLEX-252 WITH AKTIVATOR-205, PRIMER-210, FIXING TAPE · Bộ keo dán ACP | bought set, used by WALL and CEILING | about 4.4 kg (0.49 kg per side panel, bond spec) | PROPOSED number; system source (bond spec section 8, D-137: renamed from SikaTack Panel-50 for the steel frames) |
| H-13 | **848011** | SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY · Băng gai dính định vị cassette | bought by length | 1.6 m for the 8 wall cassettes (0.2 m each, WALL's figure); CEILING adds its own if it uses it | PROPOSED number (WALL's placeholder kept) |
| H-14 | **848012** | SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN · Gioăng mép cassette (rất mềm) | bought by length | WALL's count; about 5.2 m for the horizontal joints between stacked wall cassettes (calculation: 2 × 1448 + 2 × 1169) | PROPOSED number (kept: same function, nothing made yet); part HOLD-13 |

**Cancelled numbers, never to be reused (conventions §6):** 848002, the 9.53 mm foam strip first proposed for the closing seams, replaced by the bulb seal 848004; 848003, the base seal's first number, moved to 118001 in family 11, BASE (R-J17); and 848010, WALL's placeholder for the bond, which is not a seal or tape and takes 108002 in family 10 instead (a bought set used by both WALL and CEILING, so it belongs to neither family alone). WALL's placeholders 848011 and 848012 are kept for the hook-and-loop and the edge gasket, which family 84 covers (gaskets, hook-and-loop, adhesive tapes).

**FRONT's bought items** (family 36, FRONT - DOOR AND GLAZING, which conventions §6 gives the door seals, glazing profiles, hinges, handle and catch; NNNN 8000–8999, bought items used only in FRONT). FRONT proposed these numbers in its parts lists (PRs #27 and #28 and its next ones) and the register adopts them unchanged (D-63): they fit the band, none is on the reserved list (D-28), and none is used by another team. Counts and masses are FRONT's; products are FRONT's picks from the hardware selection where named.

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-15 | **368001** | FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112 · Ron chân cửa tự động | bought | 1 (about 0.6 kg) | adopted; product source (SEL C4); mass assumption (D-56) |
| H-16 | **368002** | FRONT - GLAZING U-SEAL - BOHLE BO5201735 · Gioăng chữ U silicone | bought by length | 4.5 m (about 0.39 kg) | adopted; product source (SEL C5) |
| H-17 | **368003** | FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD · Gioăng từ 180° (nửa 1) | bought | 1 (FRONT's count) | adopted; product HOLD (FRONT; it replaces the push-on BO5281018 in FRONT's first list) |
| H-18 | **368006** | FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD · Gioăng từ 180° (nửa 2) | bought | 1 (FRONT's count) | adopted; product HOLD (FRONT); which half sits on which pane is in FRONT's parts list |
| H-19 | **368004** | FRONT - GLAZING U-PROFILE - BOHLE BO5201571 · Thanh U nhôm kẹp kính | bought by length; aluminium as supplied, hidden | 3.3 m (about 0.56 kg) | adopted; product source (SEL C5; 0.17 kg/m, calculation) |
| H-20 | **368005** | FRONT - FRAME-STOP SEAL · Gioăng chặn khung cửa | bought by length | 2.9 m | adopted; product per FRONT's parts list (SEL C3 lists athmer PS 1515 P Flex) |
| H-21 | **368101** | FRONT - DOOR HINGE - HOLD · Bản lề cửa kính | bought | 3 (about 0.6 kg each) | adopted; product HOLD (D-46, ISS-002) |
| H-22 | **368102** | FRONT - DOOR STRIKE · Đế hít cửa | bought | 1 (about 0.023 kg) | adopted; product per FRONT's parts list |
| H-23 | **368007** | FRONT - DOOR CATCH - IN DT · Nam châm hít cửa (trong khối DT) | bought | 1 (about 0.052 kg) | adopted; product per FRONT's parts list |
| H-24 | **368103** | FRONT - DOOR PULL PAIR - HOLD · Tay nắm cửa (cặp) | bought | 1 pair (about 0.8 kg) | adopted; product HOLD (hole sizes on the laminate, SEL C2) |

**BASE's bought items** (from BASE's draft PR #55; family 11 BASE for its own items, 83 for the nut; NNNN 8000–8999). All three are on hold until BASE names the products; the numbers are BASE's proposals, adopted (D-63). Counts: PR #55 has 2 glides on each side band and 3 on the back band; the front pieces come in BASE's P02 (the layout study counts 8 glides in all).

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-25 | **118002** | BASE - LEVELLING GLIDE - M10 - HOLD · Chân chỉnh cao | bought, used only in BASE | 7 in the side and back bands, plus the front pieces' (BASE P02; about 8 in all) | adopted; product HOLD (BASE): an M10 stem with a 5 mm hex socket on top, about a 36 mm pad, preset at the factory (D-87), the same 5 mm key as every bolt (REQ-ASM-03) |
| H-26 | **838006** | HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD · Tán rút M10 cho chân chỉnh | bought | one per glide: 7, plus the front pieces' | adopted; product HOLD (BASE): in the band's 1.5 mm bottom wall with an aluminium load block above it (D-86) |
| H-27 | **118003** | BASE - TUBE END CAP - 100 X 40 - BLACK - HOLD · Nút bịt đầu ống 100x40 | bought, used only in BASE | 2 at the side bands' back ends, plus any open front end (BASE P02) | adopted; product HOLD (BASE): PE or PP insert cap, black |

**More fixings from the PM rulings of 2026-11-01** (bought; family 83 HARDWARE, NNNN 8000–8999; none in use on main or in the open pull requests on 2026-11-01). The fixed glass's bottom U-channel ships fitted on BASE's sill (PM ruling; packing list, PR #84), so its M3 screws are a factory fixing and the 5 mm key stays the only site tool (REQ-ASM-03).

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-28 | **838007** | HARDWARE - COUNTERSUNK SCREW - M3 X 8 - ISO 10642 A2 · Vít đầu côn lục giác chìm M3 × 8 inox | bought | 4 | PROPOSED number; part as the PM named it (ISO 10642, A2 stainless); fitted in the factory (J-FRONT-04) |
| H-29 | **838008** | HARDWARE - RIVET NUT - M3 - COUNTERSUNK HEAD - HOLD · Tán rút M3 đầu côn | bought | 4 | PROPOSED number; product HOLD-16 (grip and countersink to suit BASE's sill wall) |
| H-30 | **838009** | HARDWARE - THREADED INSERT - M6 - FOR 9 MM PLY - HOLD · Ốc cấy M6 cho ván ép 9 mm | bought | 2 | PROPOSED number; product HOLD-17 (BASE: how F2's spigots fix into the ply) |
| H-31 | **838010** | HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2 · Vít đầu tròn có vành M6 × 12 inox | bought | 12 | PROPOSED number; part per the PM ruling on F-018 (a low head for the factory-fitted corner keys, 3.3 tall); fitted in the factory with a 4 mm key (J-BASE-02) |

**INTERIOR's bought items** (family 81 INTERIOR, NNNN 8000–8999, bought items used only in INTERIOR; INTERIOR's parts list in PR #92, which the CEILING Engineer builds, D-80). The register adopts INTERIOR's numbers and names unchanged (D-63, D-99), so its parts list matches; both are product HOLD until INTERIOR names them.

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-32 | **818101** | INTERIOR - LEDGE BRACKET - HOLD · Ke đỡ bàn tựa (chờ) | bought, used only in INTERIOR | 2 | adopted; product HOLD (INTERIOR): a concealed shelf bracket rated for a 225 N lean at the ledge's front edge × 3 (INTERIOR's requirement); about 0.1 kg each (assumption) |
| H-33 | **818102** | INTERIOR - SCREEN RAIL - HOLD · Thanh treo màn hình (chờ) | bought, used only in INTERIOR | 1 | adopted; product HOLD (INTERIOR): a VESA rail for a screen up to 900 wide, about 10 kg (D-70); about 0.5 kg (assumption) |

**A seal from the PM rulings of 2026-11-01** (D-130's notes; family 84 SEALS AND TAPES, NNNN 8000–8999; the number from Control). DR's removable inner face panel (351305, 3 mm aluminium; since D-130's PM ruling one panel takes the place of the access panel and the inner panel 351303) seals on DR's frame with **848013, a very soft foam strip 4.0 thick with PSA, about 8 wide (FRONT's flange decides), pushing about 5 kPa or less at 40%** (PM ruling 2026-11-01: re-specified from the first 1.0 strip before anything used it). It sits on stops, **an 838004 washer (6.4 × 18 × 1.6) on each rivnut head, so the panel is 2.36 off the frame**, its face 1.60 further out than on the bare rivnut heads (for AIR). The seal is squeezed 41% at the screws and keeps at least 10% up to a 1.24 bow between them: at a 400 screw pitch its push bows the panel 0.13 to 0.66 (calculation, continuous to simply supported, over half the panel's width) and the sheet's own flatness adds about 0.5 over 400 (assumption; FRONT notes it on the panel). So the panel takes M6 × 16 screws (838001) at about 400 on every edge, each with a plain Ø12 ISO 7089 washer, 838011, under its head (H-44; D-142: it was an 838004, whose Ø18 broke the felt's holes through their edge), into 838003 rivnuts in DR's frame. **Where the tube under the panel edge is only 20 wide** (the glass edge, the diagonal and the top over DT's ledge), the 18 mm washer and the 8 mm seal don't fit side by side: **the seal is cut round each washer, its foam ends cut a little long so they press against it, and the washer seals its spot metal to metal** (PM ruling 2026-11-01); on the wider tubes the seal runs beside the washers. **D-131 makes DR's frame steel, and its four panel-screw tubes** (the ledge, the diagonal, the glass edge and the band) **may be 0.8 mm** (PM ruling 2026-11-01): the rivnut grips 0.76 at the thinnest wall J-FRAME-01 accepts (0.70–4.20), its Ø9.53 hole leaves about 3.6 mm of flat each side in a 20 mm face (HOLD-04), and T06's 5 DR coupons in that tube set the screws' torque. These screws, rivnuts and washers are FRONT's count, outside this register's joint counts. The cassette edge seal 848012 (2.0–2.2, near-zero squeeze, R-J18) isn't used there: on the bare 0.76 rivnut heads it would have been crushed about 62%.

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-34 | **848013** | SEALS - ACCESS PANEL SEAL - 4.0 THICK - VERY SOFT FOAM PSA · Gioăng tấm thăm - xốp rất mềm dày 4.0, keo dán sẵn | bought by length, used only in FRONT | the outline of DR's one inner face panel 351305, FRONT's length (it was up to about 10.4 m for the two panels before D-130's one-panel ruling) | number from Control (2026-11-01), re-specified to 4.0 (PM ruling 2026-11-01); product HOLD-19 |

**A front seal and a washer from the PM rulings of 2026-11-01** (D-150, D-142; the numbers from Control, the rows this register's, D-63, as for 848013).
- **368008, the kick strip's end seal (D-150).** BASE closes the fixed glass's sill at its door end with a 2 mm end plate from X 218.5 to 220.5, with the lip 118001 along its bottom edge; the kick strip ends at X 214, so a 4.5 mm slot runs between them from the floor to Z 105, past both FR1's lip and the door's drop seal (about 75 cm² open before, Reviewer 8 on #303). A self-adhesive brush strip on the kick strip's end face closes it against sound and air (REQ-SND-02). **It is fitted on site, not at the factory** (the Lead's ruling 2026-11-01): after the glides are set and the door hangs, pressed down onto the real floor, so it meets the floor wherever the glides leave the pod; it ships in the door's kit bag. The Air Engineer confirms the open area once it is modelled. Its product is on HOLD-23.
- **The kick strip's hinge-end seal (the Lead's ruling 2026-11-01).** On the door's hinge side BASE welds a 2 mm plate into FL2's door end, flush with DL's door face at X −972 and running inward to Y −689, which leaves an 11 mm slot to the kick strip's hinge end, from the floor to Z 105. A second self-adhesive brush strip, with a longer pile (FRONT posts its length), closes it from the kick strip's hinge end, fitted on site the same way and shipped in the door's kit bag. Its number is to come from Control; its product is on HOLD-25.
- **The plain washer under DR's inner panel screws (D-142).** The panel keeps its ISO 4762 M6 × 16 screws (838001) into 838003 rivnuts on 838004 stops, but under each screw's head a plain ISO 7089 washer, 6.4 × 12 × 1.6, **200 HV steel, zinc plated** (the Lead's ruling 2026-11-01: it matches the 8.8 zinc screws above it, and zinc sits close to the 5754 aluminium panel, kinder to it than stainless; R-J10's A2 stays for the site bolts' head washers), so the felt takes closed Ø14 holes with a 3 mm web. 21 a pod (D-142, calculation: FRONT's screws round the panel). Like the panel's screws and rivnuts, FRONT's count, outside this register's joint counts.

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-43 | **368008** | FRONT - DOOR KICK STRIP END SEAL - BRUSH - HOLD · Chổi chặn khe đầu thanh chắn chân cửa (chờ) | bought, used only in FRONT; fitted on site, in the door's kit bag | 1: about 105 long, on the kick strip's end face from the floor to Z 105 | number from Control (D-150); fitted on site (the Lead's ruling 2026-11-01); product HOLD-23 |
| H-46 | to be allocated by Control | FRONT - DOOR KICK STRIP HINGE END SEAL - BRUSH - HOLD · Chổi chặn khe đầu bản lề thanh chắn chân cửa (chờ) | bought, used only in FRONT; fitted on site, in the door's kit bag | 1: about 105 long, on the kick strip's hinge end from the floor to Z 105, closing the 11 mm slot to BASE's plate in FL2 | the Lead's ruling 2026-11-01; its number from Control and its pile length from FRONT; product HOLD-25 |
| H-44 | **838011** | HARDWARE - WASHER - M6 PLAIN - ISO 7089 6.4 X 12 200HV ZINC · Long đen phẳng M6 mạ kẽm | bought, used only in FRONT | 21: one under each screw head of DR's inner face panel 351305 | number from Control (2026-11-01); part DECIDED (D-142; zinc-plated steel, the Lead's ruling) |

**The frames' mitre plates** (D-131, J-FRAME-01; the Lead's ruling 2026-11-01: shared parts numbered once, as made hardware like the spigot, the allocation through Control; family 83 HARDWARE, NNNN 1000–7999 for parts we make; none in use on main or in the open pull requests on 2026-11-01). Each is a flat 2.0 mm rectangular blank cut from the frames' own galvanized steel (yield 280 MPa or more, Z100), a little shorter than its mitre so its square ends sit 0.5 inside the frame's faces (the Lead's steer, 2026-11-01; J-FRAME-01), welded between the two members of a frame corner. WALL and CEILING list them by these numbers. H-35 to H-39 were the cleats' rows in draft #203 and aren't reused.

| Item | Part number | Name · Vietnamese | Class | Per pod | Status |
|---|---|---|---|---|---|
| H-40 | **831007** | HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL · Tấm đệm góc vát 20 × 40 - 45° - thép 2.0 | made | 26: 26.5 × 40 × 2.0, 16.6 g, starting 1.75 along the mitre from the frame's outer corner; the 45° corners of two 20 × 40 members (the front corners of L1, R1, C1 and C2, the bottom front ones of L2 and R2, all four of B1 to B4) | PROPOSED number and part; model, STEP and DXF built 2026-11-01, the blank shortened the same day (joints CAD BUILD-RECORD) |
| H-41 | **831008** | HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL · Tấm đệm góc vát 20 × 40 với 40 × 40 - thép 2.0 | made | 12: 41.5 × 40 × 2.0, 26.1 g, starting 3.15 along the mitre; where a 20 × 40 member meets a 40 × 40 one (the back corners of L1, R1, C1 and C2; the bottom back and top front ones of L2 and R2) | PROPOSED number and part; model, STEP and DXF built 2026-11-01, the blank shortened the same day (joints CAD BUILD-RECORD) |
| H-42 | **831009** | HARDWARE - MITRE PLATE - 40 X 40 - 45 DEG - 2.0 STEEL · Tấm đệm góc vát 40 × 40 - 45° - thép 2.0 | made | 2: 54.8 × 40 × 2.0, 34.4 g, starting 1.75 along the mitre; the top back corners of L2 and R2, where two 40 × 40 members meet | PROPOSED number and part; model, STEP and DXF built 2026-11-01, the blank shortened the same day (joints CAD BUILD-RECORD) |

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

All calculation from SKL P04. **The bolt lines sit on the bolt-side tube's centre: Y +824 and Z 2374** (DECIDED, R-J15), not the middle of the overlap (Y +827, Z 2377). The Ø19 access hole needs the tube's whole width: centred, it keeps 9.3 mm to each inner wall; at +827 it would keep 6.3 on one side. At +824 the rivnut's hole edge is 9.2 mm from the edge of the 40 × 40 member's face and the Ø20 stop washer (Y +814 to +834) lies inside both faces (calculation). In steel (D-131, 1.0 mm) the 40 × 40 member weighs 1.204 kg/m against 0.890 (calculation, frame_steel_check.py): **+3.13 kg** for 4 side back members × 1142.74, 2 upper side top members × 1492.74 and 2 ceiling back members × 1198.99 (calculation; +1.29 kg in aluminium).

### 2.5 Seals

Every joint face carries one H-04 strip, **8 mm wide, beside the washer line on the outer (skin) side** (R-J7): at the stops it sits between the Ø20 stop washer's edge and the face's outer edge, 1 mm clear of each (on a 40 mm face the washer leaves 10 mm each side of itself, calculation); at the closing seams the bulb seal (H-04B) runs beside the Ø12.96 rivnut heads the same way. It passes beside the spigots the same way, so **the seal line is unbroken** along every joint (ISS-003).

Line load at 25% squeeze: 41 kPa × 8 mm = **0.33 N/mm** (calculation from SEL D). At 43% the foam is stiffer and no point is published; up to 1.0 N/mm is assumed (3 ×, assumption). The tubes bend between bolts under it: for the 20 × 40 × 1.0 steel tube (D-131) bent across its 20 mm depth, I = 7 950 mm⁴ (calculation, corner radii 2t), E = 210 000 MPa (source: EN 1993-1-1). Fixed at bolts 352 mm apart (the widest spacing, 2.9), a tube deflects 0.02 mm at 1.0 N/mm (calculation); beyond the end bolts, 220 mm to the panel corner, a fully free tube end would open 0.18 mm, but the welded corner holds it, so the real figure is smaller and J-T3 measures it. Either way the squeeze stays above 25% (0.18 × 2 = 0.35 against a 1.71 mm squeeze, calculation; the aluminium tube's figures were 0.06 and 0.44).

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

At the joints (calculation): LC2 on a wall spanning 2.29 m gives 0.26 kN/m at the base and 0.24 kN/m at the top: with 4 bolts on a 1493 mm edge, about **100 N per base bolt**. The door's weight puts a 274 N·m moment on DL, a 152 N couple between hinges 1.8 m apart (assumption); LC3 adds 391 N. These are small next to the bolt's 11.6 kN proof load: **the weak link is the rivnut in the 1.0 mm steel tube** (D-131), which has no published strength (SHX2), so strength is shown by test (J-T1), not a catalogue figure (guideline §8.1). How LC2's moment shares between a wall's edges and its seams needs the panel's own calculation or the push test in J-T3.

### 2.7 Tolerance and adjustment, common to all joints

- **Clearance holes Ø7.0, positioned to Ø0.4 (±0.2) from the spigot hole, by CNC or a drill jig (R-J6).** Stack ST-03 (CHK): (7.0 − 5.974) / 2 − 0.2 − 0.2 − 0.065 rivnut float = **0.05 mm to spare** worst case (calculation). The rivnut's 0.065 is half of (9.63 − 9.50), hole maximum against body maximum (SHX).
- **Locating:** two H-05 spigots 100 mm in from the ends of each horizontal edge that a part is set down on (the base band, the panel below, the back wall's top under the ceiling): a Ø8.5 round hole at one end, an 8.5 × 14 slot along the edge at the other (R-J13). The vertical joints need none of their own: both parts already stand on spigots.
- **Fit-up without scraping a seal (R-J17):** at the back corners the side panels' back-end spigot slot runs **along X** (8.5 × 14, so ±3 mm), not along the edge: each side panel goes down with its back end held clear of the corner gasket on its own back member (the strip stands 1.71 mm proud of the stop, and the panel is held about 2.5 mm out, assumption), then the corner bolts pull it in onto the stops, and only then are the base bolts near its back end driven (their holes line up once it's pulled in). The upper side panels do the same on the lower ones' top tubes. At the ceiling's side edges the side walls' tops lean out instead, with their top corner bolts finger-tight (R-J9): about 12 N moves a wall's top 1.7 mm (calculation: 3 E I δ / L³ for the wall as a 2.29 m cantilever, E 210 000 for the steel frames, I of a side wall's 6 upright members ≈ 1.39 × 10⁵ mm⁴, D-131; about 4 N in aluminium). At the closing seams the bulb seal needs no squeeze at fit-up (H-04B). If FRONT locates the decor blocks by spigots, their slots run along Y for the same reason.
- **Gaps are set by metal stops** (2.26) at the stopped seams, and by the parts' own spigots at the closing seams (2.10), never by torque.
- **Frame flatness at a joint face:** **flat within 0.5 over each seam face** (a 0.5 flatness zone; the Lead's design review for D-131, with an FAI line), on the first article of each frame number (FAI K-J05) and on every frame by the factory; skin-side faces within ±0.5 of one plane (J-FRAME-01).
- **Room floor:** ±5 mm over the footprint (ISS-054, assumption), taken up by the 8 glides under the base band, set from above with the same key before any wall goes on (LAY).
- **Torque:** HOLD-01 (D-48), from T06. A seal needs at most about 350 N per bolt (1.0 N/mm × 352 mm), so the torque only has to close the joint onto its stop.
- **Order of tightening** (R-J9, R-J11): each wall's and the ceiling's closing-seam pins first; then the stopped seams; the side walls' top corner bolts and the ceiling's side bolts last, once both ceiling halves are in and bolted. A stop that sits up to ±0.25 off is taken up by the spigot play (Ø8.5 on Ø8) and the bolt-hole float (ST-03); the frame tolerances in 2.11 keep the band-set mismatch inside that. Higher up a wall, a bolt can also pull a stop shut by flexing the frame: a 40 × 40 × 1.0 steel member 1.14 m long needs about 79 N to move 0.3 mm at mid-length (calculation: 48 E I δ / L³, E 210 000, I ≈ 38 600 mm⁴, D-131; about 23 N in aluminium), but the bottom bolt, 220 mm above the fixed base, can't.

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
| Back panel on the band; back horizontal seam; ceiling back edge | 1198.99 | 4 | 220, 473.00, 725.99, 978.99 | 253.00 | DECIDED (the ceiling's back edges on the frame confirmed by the PM: C1 at X −981.74, −728.74, −475.75, −222.75; C2 mirrored) |
| Back corner; back closing seam (along the back panel's 1118.61 edge) | 1118.61 | 3 | 220, 559.31, 898.61 | 339.31 | DECIDED rule; count this register's |
| Decor to side wall (along each side panel's height) | 1142.74 | 3 | 220, 571.37, 922.74 | 351.37 | DECIDED rule; count this register's |
| Ceiling side edge; ceiling closing seam (along Y), from Y −645 along the ceiling | 1495 | 4 | 220, 571.67, 923.33, 1275.00, so Y −425.00, −73.33, +278.33, +630.00 | 351.67 | DECIDED (confirmed by the PM) |
| DT's edge with the ceiling's front tubes (J-FRONT-03), from X −1201.74 (C1's frame end) to X +449 (DT's right end) | 1650.74 | 4 | 220, 623.58, 1027.16, 1430.74, so X −981.74, −578.16, −174.58, +228.99 | 403.58 | DECIDED rule; count this register's |

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
| Band-to-panel mismatch at the corner: the side panel's back spigot on BAND-L to the back panel's round spigot on BAND-BACK, and each panel's spigot to its joint face | up to ±0.3 | PROPOSED (±0.1 each, CNC) |
| **Corner gap: set by the corner bolts, not the band (R-J17).** The side panel's back-end spigot slot runs along X (±3), so it drops in about 2.5 mm out and the corner bolts pull its back member onto the stops; the slot covers the 2.5 mm offset plus the ±0.3 mismatch with 0.2 to spare | **2.26 ±0.13**, the stop's own tolerance (stop washer and rivnut head) | calculation |

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
| Nut side and bolt side | Back panels go on first, then the sides (LAY step 4). Nut side: the side panel's back member, 40 × 40 × 1.0 steel (D-131; Y +810 to +850), with rivnuts and stop washers in its room-side face at **Y +824**. Bolt side: the back panel's outer tube, Ø7.0 in the wall that faces the side panel and Ø19 in its bay-side wall, at Y +824; the bolts stay pulled back while the side panel goes on. |
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
| Nut side and bolt side | Nut side: the band's top wall, with 2 H-05 spigots and 4 rivnuts with stop washers per panel, on the wall tube's centre line: **X ∓1224** (side walls) or **Y +824** (back wall), 6 mm off the band's own centre line (calculation: band 40, panel 46). The band's top wall must be 2.7 mm or thinner for the rivnut grip with the washer (**HOLD-07**). Bolt side: the wall's bottom tube: spigot hole and slot, Ø7.0 in its bottom wall, Ø19 in its top wall. H-06 base seal: a soft lip on the band's inner face that presses on the room floor (D-132, HOLD-06). |
| Bolts | 4 per panel: **16**. |
| Stack | 2.2 (the band is open inside). |
| Tolerance and adjustment | The band is levelled on its 8 glides before any wall goes on; the walls stand at Z 112.26 (2.8); the ACP's outer face is flush with the band's outer face, so the frame overhangs the band by **6 mm** inside (calculation). |
| Assembly | Wall lowered onto the band spigots; bolts down from the pocket in its bottom bay (LAY step 4). |
| What can go wrong | Band top wall too thick (HOLD-07); DR's notch in BAND-R (a BASE HOLD); the base lip lifting off the room floor at some glide setting (HOLD-06, D-132). |
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
| Function and load path | Hangs the cassette with no screw through it, so the inner leaf floats (D-17); holds it under its weight and knocks; ceiling cassettes can't drop (D-47). **Clip-only fixing, no rails (D-81):** the clips are the cassette's only load path; hook-and-loop only lines it up. Load: tray → clip → frame tube. The perimeter gasket in the 4 mm gap seals the cassette edge and carries no load. Where two cassettes meet, the edge seal H-14 (848012) only touches across the 2.26 mm gap (R-J18), so it can't push a cassette off its clips. |
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
| J-FRONT-03 DT to the ceiling | 4 | M6 × 16 |
| J-BASE-02 base band corner keys | 0 on site (24 in the factory) | M6 × 12 button heads as fixing screws, M6 × 16 as hook studs |
| J-FRONT-02 DL on the band, DR on its support | 0 (spigots) | — |
| J-AIR-01 soffit on the ceiling frame | 2 (the lock screws; its 4 hanger studs are set in the factory) | M6 × 25 lock screws; M6 × 16 hanger studs |
| J-AIR-02 air column on DR and the floor | 0 on site (2 hook studs in the factory; 2 spigots) | M6 × 16 hook studs |
| J-FRONT-04 fixed glass channel on BASE's sill | 0 on site (4 in the factory) | M3 × 8 countersunk |
| J-AIR-03 roof grille on the roof sleeve | 4 | M6 × 16 |
| **Total on site** | **92** | 80 × M6 × 16, 12 × M6 × 25 |

Every site bolt carries one H-09 washer. Not counted: the door hinges and the fixed glass's side and top profiles (FRONT, on hold). The layout study's decided build counts 78 bolts and 38 tool-free clips (LAY §4); R-J1 turns the seam and corner clips into bolts, which the PM set at about 12 more minutes of assembly.

### 3.10 Joint IDs against the layout study

| Layout study (LAY §2 tables) | This register |
|---|---|
| J-WALL-01 side horizontal seam; J-WALL-02 back horizontal seam | J-WALL-01 |
| J-WALL-03 back vertical seam | J-WALL-03 (now the closing seam) |
| J-WALL-04 side wall to back wall corner | J-WALL-02 |
| J-BASE-01 walls to base band | J-BASE-01 |
| J-BASE-02 base band corner keys and front joints | J-BASE-02 (now hook-in keys, no site bolts, D-87) |
| J-CEIL-01 ceiling halves to walls; J-CEIL-02 ceiling half to half | J-CEIL-01; J-CEIL-02 (now the closing seam) |
| J-FRONT-01 decor blocks to walls, ceiling and base | J-FRONT-01 covers the decor to the side walls only; DT to the ceiling and the decor on the band stay with FRONT and BASE |

### 3.11 J-BASE-02: base band corner keys, hook-in (D-87)

| Field | Entry |
|---|---|
| Parts | The base band's pieces at its 6 joints: the 2 back corners (each side band to the back band); the 2 front corners (each side band's mitred front end to its front piece: FL1 on the left, the intake support rail behind the mesh piece on the right); the left knee (FL1 to FL2); and the inline joint at X 915 (the intake support rail to FR1, square; BASE moved it from X 947 to X 915 so the intake mesh stays fully open, then to X 915, a 32 mm stub, for the 30 mm key; rulings 2026-11-01). Band: 100 × 40 aluminium tube, 1.5 mm wall (D-86), on preset glides (D-87); the front pieces' outer-face points are BASE's (relayed by the PM, 2026-10-31). |
| Function and load path | Ties the band into one ring so the corners can't open, and locates each piece on its neighbour so the band sets itself out. The walls' weight goes through the band and the glides to the floor (J-BASE-01); the keys carry only the tie and the racking share, at most a few hundred newtons (assumption: of the order of LC2's 0.26 kN/m on a wall). |
| Take-down | Yes: lift a piece 10 mm and pull it off; 5 cycles. |
| Options compared | (a) BASE's bolted angle, 2 bolts a leg, site-fitted (111201 in PR #55; the layout study's 12 bolts): about 12 minutes on site (D-87). (b) A cleat glued or riveted on site: not allowed (REQ-ASM-05). (c) **A key fitted in one piece at the factory, with headed studs that hook into keyholes in the other piece as it is set down (chosen)**: no tool, no loose part, and it locates. |
| Choice and reason | (c), DECIDED (D-87). The design here is PROPOSED. |
| The key family, 111211 to 111215 | **One machined block for all six joints**: 6061-T6 aluminium, mill finish, hidden; 35 across the band (the 37 bore less 1 each side, from the skeleton's band_t), 75 tall, 30 long on its centre line; about 0.21 kg (calculation: 35 × 30 × 75 mm³ at 2.70 g/cm³, less the holes). 30 keeps the carrier's Ø7.0 fixing holes at least 2 × 7 from its cut end on every key: 14.9 on 111212 and 111213, 18.5 on 111214, 19.5 on 111215 at FR1; at the back corners the carrier's cut end is the side band's back end at Y 850, 14.0 from 111211's nearer hole (calculation; PM note and ruling 2026-11-01). Its stud face is cut to its carrier's mitre and its fixing holes follow its carrier's end (Holes, below), so the five numbers differ in that cut or those holes: **111211 BASE - CORNER KEY - SQUARE - COMMON**, square, with the back corners' holes, 2 per pod (both back corners); **111215 BASE - CORNER KEY - SQUARE - INLINE**, square, with the first holes, 1 per pod (the FR1 inline joint; number proposed here, the allocation through Control); **111212 BASE - CORNER KEY - FRONT - LH**, 24.14° (the FL corner); **111213 BASE - CORNER KEY - FRONT - RH**, 24.02° (the FR corner); **111214 BASE - CORNER KEY - KNEE - LH**, 7.25° (the left knee); 1 each. The long side is always on the outside of the turn. One TABULATED drawing covers the five (D-89). **The joints register and its models are the one source for 111211 to 111215** (native model, one STEP per part number, the tabulated drawing, in `v2/01-CAD-Native/joints/` and `v2/03-Manufacturing/joints/` with the made-hardware PR): BASE places them in its assemblies (BASE ruling 2026-11-01). |
| Holes in the key | **Fixing:** 2 in its bottom, M6, thread 15 deep, Ø5.0 drill 18 deep. **111212 to 111215:** 10.5 from its back face and 7.0 either side of its centre line (10.5 from its side faces: over 2 × the hole, the mechanical check's C09). **111211, the back corners** (PM ruling 2026-11-01: no edge exception; the key can't move, its studs line up with the back band's slots): 6.0 either side of its centre line, the +y one 10.5 from its back face and the −y one 17.8 (stepped 7.3). Each Ø7.0 hole in the side band's bottom wall then stays 14.0 from the band's back end at Y 850 with the key turned either way; the screws are 14.05 apart, so 838010's flanges (Ø13.6 at most) clear by 0.45; the key's walls are 10.5, 11.5 and 12.2 from the holes (C09: 10.06); and the holes end about 19.5 above the key's bottom with their drill points, 4.0 below the lower stud hole (measured straight up; corner_keys.py checks at least 2.0). The right back corner's key is the same 111211 turned 180°, so **the two side bands' fixing holes are not mirror images**: the left band's at X −1231, Y 836 and X −1223.7, Y 824, the right band's at X 1231, Y 824 and X 1223.7, Y 836. BASE drills each band from its own rows in corner-keys.csv, never by mirroring the other. FR1 can't take that layout: its stepped hole would be 12.2 from the rail's end at X 915, and the rail's 32 mm stub leaves no room for a longer key, so FR1 keeps the first layout as 111215 (calculation; corner_keys.py checks every rule). Each takes an **838010** (M6 × 12, ISO 7380-2 flanged button head, A2, no washer) from below, through a Ø7.0 hole in the carrier's bottom wall: engagement 12 − 1.5 = 10.5 in the 15 mm thread (calculation; PM ruling on F-017: at least 15 mm of thread; F-018: a low head). **Hook studs:** 2 in its stud face, M6 tapped through (PM ruling on F-017), square to the face on its centre line, 26 and 60 above its bottom (Z 37.5 and 71.5 in the pod). Each takes an 838001 set at the factory with its head's underside 1.8 off the face (a 1.8 gauge: the 1.5 wall or plate and 0.3 clearance), threadlocked; engagement 14.2 (calculation). **At the two back corners (D-129)** the key sits in the side band against its inner wall from inside, and each stud bolt goes through a Ø7.0 hole in that 1.5 wall into the key: its head's underside is set 1.8 off the wall's outside face, engagement 16 − 1.5 − 1.8 = 12.7 (calculation, over 2 × the diameter). |
| Keyholes and slots in the other piece | **Keyholes, at the front joints:** the moving piece goes on along the studs and then down onto them, so each keyhole's Ø12 entry is centred 10 mm below the stud's final position, and a 6.5 mm wide slot runs 10 mm up from it to the stud's seat. Entries at Z 27.5 and 61.5, so the lower entry's edge stays 10 mm above the band's bottom wall. In BASE's 1.5 mm end cap at each front joint (FL1's at the corner, FL2's at the knee, the intake support rail's at the corner, FR1's at X 915). **Open slots, at the two back corners (D-129):** the back band is lowered straight down between both side bands' studs; it can't slide sideways onto studs at both ends, as its length is the gap between the side bands, so a keyhole's Ø12 entry can't be used. Going down, a cap meets the studs with its bottom edge, so each of its two 1.5 mm end caps has **one 6.5 mm slot open at the cap's bottom edge**, widening to 12 over its bottom 6 mm, on the band's centre line (Y +830), running up past both studs to **2 mm above the upper stud** (its closed end's centre at Z 73.5): the cap slides down in the 1.8 gap between the heads and the side band's face, both shanks in the one slot, and the band comes to rest on its own glides, never on the studs. Each cap's bottom edge has a 1 × 45° bevel on its side-band side, to slip under the heads. **The heads end up inside the band's tube, so they come up into it through a notch in its bottom wall at each end:** 12 wide (the Ø10 head and 1 each side) and 9 deep from the end (the head's far face is 1.8 + 6 = 7.8 from the side band's face), on the band's centre line. BASE's fit check (2026-11-01) set the slot's direction and the notch; the first note here had the slot open at the top, which only works if the band is lifted onto the studs. |
| Where each key goes | Key in the carrier's end → keyholes or slots in the next piece: the side bands' back ends, against their inner walls → the back band's end caps (111211 × 2, open slots, D-129); the left side band's front end → FL1 (111212); FL1's knee end → FL2 (111214); the right side band's front end → the intake support rail (111213); the rail's end at X 915 → FR1 (111215). Every front piece hooks at one end only, so it can be pushed straight along its studs; the back band drops in from above. Each key's face centre, stud axis, fixing holes and keyhole heights in pod coordinates: [`corner-keys.csv`](../../01-CAD-Native/joints/corner-keys.csv), made by [`corner_keys.py`](../../01-CAD-Native/joints/corner_keys.py) from the skeleton's named values (pod_w, pod_d, band_t, glide_h) and BASE's front points. |
| How it goes together | **Both side bands stand on their preset glides first**, their keys and stud bolts fitted at the factory (D-129; the guide's step 2 changes to this order). **Two people, one at each end, lower the back band straight down between them**: each end cap's slot mouth takes the upper stud's shank and then the lower one, the heads come up into the tube through its bottom wall's notches, the cap slides down in the 1.8 gap under both heads, and the band comes to rest on its own preset glides with the upper shank about 2 below the slot's closed end; going down, the caps draw the side bands to the band's 2420. **Until the lower back wall panels B1 and B2 bolt through its top wall (J-BASE-01, the guide's step 4), nothing but its weight holds the back band down**: the studs hold it across and along, nothing in steps 2 and 3 pulls it up, and nobody lifts it or stands on its top wall before then (the guide says so). Take-down is the reverse: with B1 and B2 off, the back band lifts straight out. Then, at the front: each piece is offered 10 mm high, pushed along the studs so the heads pass through the Ø12 entries, then lowered 10 mm onto its preset glides: the shanks ride to the top of the slots and the heads hold the plate behind them. FL1 onto the left side band, FL2 onto FL1, the intake support rail onto the right side band, and **FR1 last, onto the rail**: the guide lists FR1 before the intake piece and should follow this order. The slot width locates each joint across the band to ±0.25 (Ø5.97 shank in 6.5); at the front the slot's top end sets the height, at the back the glides do; the heads hold each joint along the stud axis. |
| Hardware (factory) | Each key: 2 × 838010 fixing screws and 2 × 838001 hook studs; no washers. For the 6 keys: 12 × 838010 and 12 × 838001 (calculation); none on site. |
| Calculation | Stud shank bearing on the 1.5 mm wall at 300 N (assumption): 300 / (5.97 × 1.5) = 34 MPa, against about 160 MPa yield for 6063-T6 (D-86's figure for the band, source); the head on the 6.5 slot's lips takes pull-out of the same order. Block threads: 10.5 mm of M6 for the fixing screws (1.75 × the diameter) and 14.2 mm for the hook studs, in 6061-T6 (calculation). The angled keys keep 11.9 mm of metal between a fixing hole's thread and the stud face (calculation at 24.14°). At the back corners (D-129) the ring's pull bears the key's stud face on the side band's inner wall, so the fixing screws only hold it in place; each head bears on the cap's 1.75 mm slot lips at 150 N (half of 300 N, assumption), a few MPa. |
| What can go wrong | A piece can't be held 10 mm high while it's pushed in: two people, one at each end; the glides' preset height decides where the heads land (J-T6). A fixing hole or keyhole lands on a glide's load block or nut: BASE keeps those clear of the last 30 mm of each keyed end (assumption). The fixing screws' flanged button heads hang 3.3 below the band (ISO 7380-2, unverified), 6.7 off the floor with the glides at 10; **no glide may be set lower than 8.5** (the band's bottom at Z 8.5 or higher), which keeps them at least 5.2 off the floor (PM ruling on F-018: nothing under the band within 5 mm of the floor at the lowest glide setting; BASE's glide range confirms it). The intake support rail's section isn't posted yet (HOLD-15): at its ends it needs the band's 37 × 97 bore. **At the back corners (D-129):** a cap jams under the heads if a head's gap is off, so the 1.8 gauge holds ±0.1 and each cap has its bevel; the key fills each side band's last 37.5 mm at the back (Y 812.5 to 847.5), so its back-end cap (118003) may go no deeper than 2 mm into the tube, and no glide sits within the side band's last 70 mm (assumption); the back band's head notches leave its end's bottom wall open over 12 × 9, so no glide or load block sits within its last 25 mm (assumption). |
| Check and pass mark | J-T6 (section 5): each joint hooks home by hand with no tool; the back band drops between both side bands' studs at 150 N or less per end (as J-T5); it stays closed under a 300 N pull across the joint (assumption). |
| Status | DECIDED principle (D-87); the back corners' keys on the side bands, keyholes in the back band, DECIDED (D-129, PM ruling 2026-11-01: the back band ships at 2420 on the 2438 deck); key family, holes, slots and positions PROPOSED (HOLD-14 closed by BASE's front geometry); the intake support rail HOLD-15. Replaces BASE's bolted bracket 111201, which BASE retires. |

### 3.12 J-FRONT-02: DL on the band and DR on its support

| Field | Entry |
|---|---|
| Parts | DL's bottom on the base band's front-left pieces FL1 and FL2 (DL stops at Z 110, D-57); DR's bottom on the top flange of BASE's closing angle (2 mm aluminium, along Y −645) behind the mesh intake piece, not on the band (D-62: the mesh carries no load). |
| Function and load path | Locates the block where it stands and takes its weight and sideways shear into the band or the support. The door's moment from DL's hinges and DR's own weight are held by the 6 J-FRONT-01 bolts into the side wall; the base only needs to stop sliding. |
| Options compared | (a) The guide's assumed 2 bolts each (M6 × 16): no access to DL's or DR's underside from inside the pod, and nothing for them to do that J-FRONT-01 doesn't. (b) **2 spigots each (chosen)**. |
| Choice and reason | (b): no site fixing, one less step for each block, and it locates the block for its J-FRONT-01 bolts (REQ-ASM-04). PROPOSED. |
| Parts and process | Each block stands on 2 H-05 spigots (831001 in 838003 rivnuts, no stop washer; each stands 8 above its top wall), with a Ø8.5 round hole at the door side and an 8.5 × 14 slot at the wall side in the block's bottom (FRONT's update, PM-approved 2026-11-01). **DL**: on DL's bottom ring tube's centre line, 13 mm in from the outer faces, so BASE's spigots sit 13 mm in from the band's outer face to match: the round hole's spigot on FL1 at **(−1176.7, −718.0)** and the slot's on FL2 at **(−1073.9, −780.6)** (FRONT's exact positions, PM 2026-11-01; they replace #150's centre-line points). Each rivnut hole is then 13 from the band's outer face, 8.2 hole edge to face, the edge distance HOLD-04 asks about. **DR**: in 838003 rivnuts in the top flange of BASE's closing angle (2 mm aluminium, along Y −645; inside the rivnut's 0.70–4.20 grip, SHX), at **(1050, −656.5)** for the round hole and **(1147, −656.5)** for the slot (FRONT's exact positions, PM 2026-11-01). BASE keeps each Ø9.53 rivnut hole 2 × its diameter from the flange's edges. The FL1 spigot sits over the knee key 111214: the rivnut hangs to about Z 99.8 and the key's top is Z 86.5, so they clear by 13 (calculation). |
| Assembly | The block is set down onto its spigots, then bolted to the side wall (J-FRONT-01, the guide's steps 9 and 10). |
| Check and pass mark | J-T5: the block stands on its spigots without being held, then bolts up flush. |
| Status | PROPOSED; positions from FRONT's approved update and BASE's points (PM 2026-11-01). |

### 3.13 J-FRONT-03: DT on DR's ledge, and to the ceiling

| Field | Entry |
|---|---|
| Parts | DT (7.84 kg, FRONT's model) on DR's DT ledge and, at its DL end, on DL's 45° slope skin to skin (D-152), and its back plate to the ceiling halves' front tubes (IF-08). |
| Function and load path | DT's weight goes down about half onto DR's ledge through 2 spigots and half onto DL's 45° slope, its skin on DL's skin (D-152, PM ruling with Packing and FRONT: overhead lifts are hands-free, D-148; FRONT measured the two skins touching along the whole slope, 0.000 apart, so no strip and no new seam: the Lead's ruling 2026-11-01). At DL that is about 38 N down (FRONT's figures), so 54 N square to the slope and 38 N along it toward DR, which the round spigot hole on DR's ledge takes (friction on the slope only helps; calculation). The slope joint is on the decor's outside, not an acoustic boundary, and static once DT is bolted. DT then stands on its own while the 4 bolts go in; they hold it against the ceiling's front edge, so it can't tip or be pulled forward, and close the shell's top front edge (a stopped seam, sealed). The door's 35 N magnetic catch in DT's underside (D-83) is a small pull on DT: at most about 50 N more square to the slope, for a moment. |
| Options compared | (a) The guide's assumed 4 fixings to DL, DR and the ceiling: DT's insides can't be reached once it sits on DL and DR. (b) **In-member bolts from the ceiling's front tubes into DT's back plate, reached from below through the ceiling's open bays before the soffit goes up (D-60), with both spigots on DR's ledge (chosen; FRONT's update, PM-approved 2026-11-01)**: the same joint as J-FRONT-01 and J-CEIL-01. |
| Choice and reason | (b). PROPOSED. |
| Nut side and bolt side | Nut side DT: **4 rivnuts with stop washers on the bolt line Z 2374** in its back plate, **aluminium 2 mm** (FRONT's update; inside HOLD-10's 1.0–2.7). Bolt side: the ceiling's front tubes (C1 and C2), Ø7.0 in their front walls and Ø19 in their back walls, reached from the open bays. H-04 strip beside the washer line on DT's back plate. |
| Stop gap | The ceiling's front face is at Y −645 (the side-edge bolts are measured from it, 2.9). So the 2.26 stop gap comes from DT: **its back plate sits at Y −647.26**, 2.26 in front of the ceiling's face. DT's front and top faces don't move, so the look doesn't change (D-01); for FRONT's DT drawing and the skeleton. |
| Bolts and spigots | 4 bolts at the 220 mm rule along DT's 1650.74 mm edge with the ceiling: X −981.74, −578.16, −174.58 on C1 and +228.99 on C2 (2.9), clear of the C1–C2 closing seam and of the roof slot behind DR (D-60). 2 H-05 spigots in DR's DT ledge, 140 apart, at **(270, −657.9)** and **(410, −657.9)** (FRONT's exact positions, PM 2026-11-01): a round hole and an 8.5 × 14 slot in DT's underside, as FRONT draws them; none in DL's top. |
| Assembly | After the door (the guide's step 12): a protective slip sheet laid on DL's slope; DT lowered from above onto the two spigots on DR's ledge and onto the slope, where it stands without being held (D-148, D-152); the 4 bolts driven from below through the ceiling's front bays, before the soffit; the slip sheet pulled out after the bolts (the Lead's ruling 2026-11-01, Packing's guide step). |
| What can go wrong | The ceiling's front bays get closed before DT's bolts are in (the soffit and the ceiling cassettes go up after this step). DT would tip forward before its bolts are in if its centre of mass sat in front of the line from DR's two spigots to the front end of its bearing on DL's slope: FRONT's model puts it 45 to 65 mm behind that line (HOLD-24, closed). DL's slope marked as DT goes on (the slip sheet). |
| Check and pass mark | J-T5; and the first DT, set down alone on DR's spigots and DL's slope, stands without being held until its 4 bolts are in (D-148, D-152). |
| Status | PROPOSED; the load path confirmed for D-152, skin to skin (this register and the Lead's ruling, 2026-11-01); HOLD-01, -02, -05; HOLD-10 met by the 2 mm back plate; HOLD-24 closed. |

### 3.14 J-AIR-01: the soffit on the ceiling frame (D-60, D-87)

| Field | Entry |
|---|---|
| Parts | AIR's soffit (D-60) under the ceiling frame's front members and cross member X1 (CEILING PR #32; AIR's model on CEILING's air branch; PM ruling 2026-11-01). |
| Function and load path | The soffit hangs on 4 studs in the ceiling frame; 2 lock screws stop it sliding back off them, so taking a ceiling cassette out can never free it (PM ruling 2026-11-01). |
| Parts and process | **4 hanger studs:** 838001 (M6 × 16, head Ø10 × 6) in 838003 rivnuts in the members' undersides: 2 in the front members at Y −635 and 2 in X1 at Y −291, at X ∓583 (CEILING F-4111-13), set at the factory with their heads' undersides 0.3 more than the soffit rail's thickness off the member (3.3 for AIR's 3 mm rails, assumption), threadlocked. **2 lock screws:** 838002 (M6 × 25) with 838004 washers, captive in the soffit's door-side rail, into 838003 rivnuts in C1's front member at X −1100 and −950 (CEILING), driven with the 5 mm key through the soffit's left hinged underside. |
| Assembly | Lift the soffit to the studs 24 mm behind its place, so the studs stand clear in front of its rails; slide it 24 mm toward the door, so the rails' open forks take the shanks above the heads; drive the 2 lock screws (AIR's model). |
| What can go wrong | The heads need 6 mm under the rails (the lock screws 6 + 1.6 with their washers): AIR's head room becomes at least 7.5 mm with the soffit's underside kept at Z 2120 (PM ruling 2026-11-01, HOLD-18 closed). |
| Check and pass mark | J-T5's overhead fit-up: hung and locked by hand with the 5 mm key, at 150 N or less. |
| Status | PROPOSED; HOLD-04 (rivnut edge distance on the members' 20 mm faces). |

### 3.15 J-AIR-02: the air column on DR and on the floor (D-60, D-87)

| Field | Entry |
|---|---|
| Parts | AIR's air column, against DR's access panel (FRONT), standing on the floor panel F2 (BASE). |
| Function and load path | The column's weight goes to the floor through its 2 mm foot plate; 2 hook studs in DR's access panel hold its top against DR, and 2 spigots in F2 locate its foot (PM ruling 2026-11-01). |
| Parts and process | **2 hook studs:** 838001 in 838003 rivnuts in DR's access panel at X 971, Z 1700 and 1850 (AIR's model, PM ruling 2026-11-01), set at the factory with the head's underside 0.3 more than the column's keyhole plate off the panel (1.8 for a 1.5 plate, as AIR's model gives it), threadlocked. The column's keyholes: a Ø12 entry 10 below each stud's seat and a 6.5 slot up to it, as J-BASE-02 (AIR's model has them). **2 spigots:** 831001 on F2 at S1 (X 989, Y −605, into an Ø8.5 hole in the foot plate) and S2 (X 1126, Y −337, into an 8.5 × 14 slot along Y), as R-J13; each in an M6 insert 838009 in the 9 mm ply (HOLD-17). |
| Assembly | The column is offered 10 mm high against DR, pushed onto the studs and lowered 10 mm: the keyholes drop onto the studs and the foot plate onto the spigots. |
| Fit | The spigots stand 8 above the ply's top, the floor top at Z 12 (skeleton floor_top, the ply on its 3 mm mat); held 10 mm high for the hooks, the foot plate clears their tips by 2 (calculation), then drops 8 onto them. |
| Check and pass mark | J-T5: hooked and standing by hand with no tool. |
| Status | PROPOSED; HOLD-17. DR's access panel must suit the rivnut's grip, 0.70–4.20 (SHX; FRONT). |

### 3.16 J-FRONT-04: the fixed glass's bottom channel on BASE's sill

| Field | Entry |
|---|---|
| Parts | The fixed glass's bottom U-channel (368004, the 745 mm bottom piece) on BASE's sill seat on FR1. It ships fitted on BASE's sill (PM ruling; packing list, PR #84). |
| Parts and process | 4 × 838007 (M3 × 8, ISO 10642, A2) through the channel's base into 4 × 838008 (M3 countersunk-head rivnuts) set flush in the sill seat's wall, at the factory. Positions along the channel: FRONT's and BASE's drawings. Since the inline joint moved to X 915, the channel (to X 965) overhangs FR1's end by 50 mm onto the intake stub (PM notes 2026-11-01; BASE confirms the fit in its rebuild): **all 4 screws stay on FR1's sill seat**, and the overhang carries none: the channel's holes are at **X 269.4, 484.3, 699.2 and 905**, the last 10 mm short of FR1's joint at X 915 in plain sill, and BASE's last sill rivnut matches it (**D-111**, built in FRONT's PR #169; it settles the hole that was at X 914.1). |
| Why countersunk | The glass's setting blocks and the U-seal sit in the channel, so nothing may stand up in it. The ISO 10642 M3 head is 1.86 tall (unverified), more than the channel's 1.5 base (368004 is 15 × 15 × 1.5, FRONT), so it stands about 0.4 proud: FRONT checks the setting blocks clear it (HOLD-16). |
| Tool | A 2 mm hex key, in the factory only, so the 5 mm key stays the only site tool (REQ-ASM-03). |
| Status | PROPOSED; HOLD-16. |

### 3.17 J-FRAME-01: the wall and ceiling frames, welded galvanized steel (D-131)

| Field | Entry |
|---|---|
| Ruling | **D-131** (PM ruling, 2026-11-01): the wall, ceiling and decor-core frames change from 6063-T6 aluminium with glued cleats to **welded, galvanized steel box tube with the same outside sections** (20 × 40, 40 × 40; the decor tubes as they are), so the 84 mm stack, the 40 mm fill, every hole, rivnut and joint position, and the look stay. Corners and T joints are welded in the factory; every piece stays at 20 kg or less; D-117's cleats are cancelled. **D-135** the same day: every wall bay under the ACP 275 mm clear or less, so **5 studs in each side panel and 3 in each back panel** (WALL's layout; B2's first bay keeps welded cross members round it); the ceiling keeps its spacing. PM rulings the same day: **Z100 zinc on every frame**; a rivnut may go in 0.8 mm steel on DR's four panel-screw tubes; and, for margin against under-gauge tube and weak welds, **1.2 mm for the side panels' rails and front stiles, with every frame at 90% or less** of its corner's strength at the thinnest accepted wall. The Lead's design review the same day set the steel rivnut, the process notes, a primer or adhesive named for galvanized steel and the tests on galvanized coupons, and left the corner detail to this register. This entry covers the 10 wall and ceiling frames; the decor cores and DR's frame are FRONT's and follow the same rules with their own masses and lift case. |
| Parts | WALL's 211101 to 211104 (L1, R1, L2, R2) and 211201 to 211204 (B1 to B4); CEILING's 411101 and 411102 (C1, C2): their members as on main, in steel, plus D-135's studs and a plate in each mitre. No cleats, no glue, no cleat slots. |
| Gauges | **1.2 mm**: the side panels' rails and front stiles (L1, L2 and their mirrors R1, R2; PM ruling). **1.0 mm**: every other perimeter member, every 40 × 40 member, and any member with a site bolt, a spigot, a stopped-joint rivnut or a hanger stud (CEILING's cross member 1, J-AIR-01). **0.8 mm**: the wall studs, the added ones too, and CEILING's cross members 2 and 3; they may carry the lining's small fixings (blind rivets or small rivnuts for the clips and catches, J-LIN-01) but no site joint. Why: the check below. With every member at 0.8, L2's corner fails; D-131 puts every rivnut member at 1.0; and at 1.0 the side panels' corners, carrying D-135's 5 studs, sat at 98% of the thinnest tube, which left nothing for an under-gauge tube or a weak weld (the PM's reason for 1.2). |
| Steel | Strip-galvanized structural steel formed and welded into tube, with a **certified yield of 280 MPa or more**: S280GD+Z (EN 10346) or SGC400 (JIS G3302), or any grade whose mill certificate, or 3 tensile tests from the lot's flat walls (ISO 6892-1), shows 280 MPa or more; a grade with no stated yield (DX51D, SGCC) only with those tests. **Zinc Z100** (EN 10346: 100 g/m² over both faces). **Walls at least 95% of nominal**, measured through the zinc: 0.95 for 1.0, 0.76 for 0.8 (micrometer, 3 tubes a lot, every wall). Each tube **straight within 0.5 over its length** before it is cut (assumption, so the seam faces can hold 0.5; the tube standards allow more, so tubes are picked or straightened). Outside corner radius about 2t. Why 280 MPa: with the zinc taken off the wall (EN 1993-1-3) and a 95% wall, a 235 or 245 MPa tube puts C1's corner at 94 or 91%, over the PM's 90%; S250GD would sit at 89%, right at it; 280 MPa keeps every frame at 83% or less (table below). If no 280 MPa tube can be had, 1.2 mm on C1's and C2's 20 × 40 perimeter members too keeps every frame at 88% or less with a 235 MPa tube, for about 1.4 kg a pod (calculation). |
| Load path and check | Each frame is one welded piece. Its design case is D-117's (PM-accepted): the bare frame handled before its skin is bonded, its weight on half its long side, × 2 for handling and × 1.5 margin, at one corner, in plane; and held flat by one short member, the rest carried by the two corners at its ends, out of plane (bending in one member, torsion in the other). The joints' own loads (2.6) are small next to these. Calculation: [`frame_steel_check.py`](../../01-CAD-Native/joints/frame_steel_check.py), by EN 1993-1-1's section classes on the core wall (EN 1993-1-3: the wall less its zinc), with EN 1993-1-5's effective width for class 4; its tables are below. |
| Corners and T joints | **Corners mitred, with a 2.0 mm plate welded into each mitre** (this register's call, which the Lead left to it; the plates are made hardware 831007, 831008 and 831009, H-40 to H-42, placed as the joints CAD README gives). The plate is a rectangular blank in the same galvanized steel, centred through its thickness on the old mitre line and a little shorter than the mitre: **26.5 × 40** at a 45° corner of two 20 × 40 members, **41.5 × 40** where a rail meets a 40 × 40 member, **54.8 × 40** where two 40 × 40 members meet, starting 1.75, 3.15 and 1.75 along the mitre from the frame's outer corner, its inner end at the inner corner (within 0.07). Why shorter (the Lead's steer, 2026-11-01, after WALL's L1 model): a square-ended plate the mitre's full size pokes out at the outer corner, each plate face's edge by its half thickness × the cut's cosine: 0.71 at a 45° corner, and 0.45 past the 40 × 40's outer face and 0.89 past the rail's at a mixed one, into the skin's back return and the seams. Trimmed, every corner of both square ends sits 0.51 to 0.53 inside the frame's faces, on both plate faces, so the DXF stays the shape that is cut; the all-round weld fills the small step at the outer corner and is ground flush (Welding, below). `frame_steel_check.py --check` checks every corner, and that a full-size plate would poke out (calculation). Each member is cut back so the outside sizes stay: **1.41 mm off each member at a 45° corner; 2.24 mm off the rail and 1.12 mm off the 40 × 40 member at a mixed corner** (calculation). Why: a plain mitre is a knee whose walls bend at the corner and carry only part of the tube's moment, about 0.66 of a 20 × 40's by EN 1993-1-8's knee rule (written for walls of 2.5 mm and up, so only an indication here), which would put the worst corner lift at about 127%; a plate at least 1.5 t thick (2.0 against the 1.2 mm rails' 1.8) makes it a stiffened knee that carries the tube's moment, the table's figures. Square butt corners were the other choice: cheaper to cut, but the through member's open end would sit in the next seam face (a cap on each), and the butting member crushes the other's side wall at a lower moment still. With the plates: 40 a pod (26, 12 and 2 of the three blanks), 0.81 kg, in the masses below (calculation). **T joints:** each stud or cross member butts square against its rail and is welded all round; a T joint carries 0.3 kN of shear at most (D-117's figure), and a full-perimeter fillet with a throat of 0.7 × the wall carries 12.3 kN in a 0.8 stud (calculation). |
| Welding | Every corner and T joint welded **all round**, continuously, so each tube stays sealed (no open end, no gap). Process: **MIG brazing with CuSi3 wire (ISO 24373 S Cu 6560) under argon, preferred**: less heat than fusion welding, so less warp in 0.8 and 1.0 walls and less zinc burnt off; **or short-arc MAG with G3Si1 wire (ISO 14341-A)** if the factory's procedure passes the same tests (the designations are assumption, for the factory's welding procedure to confirm). The factory writes its welding procedure and proves it on J-T7's coupons before S1's frame is welded (HOLD-22). **Welded in a jig** that holds every member flat and square on its skin side; order: diagonally opposite corners in turn, then the T joints from the middle out, alternating sides; the frame cools in the jig before it is released. Beads on the skin-side faces, the seam faces and any face a skin return covers are ground flush (0 to 0.2 proud, never more than 0.3 below the face), and so is the weld that fills the step over each plate's trimmed end at an outer corner; elsewhere they stay as welded. Zinc fumes are extracted at the torch (factory safety). |
| Finish | **Pre-galvanized tube; no hot-dip galvanizing after welding**: at about 450 °C it warps 0.8 and 1.0 mm frames, and it needs vent holes in every closed cell, so the frames have **no vent or drain holes**. After welding and grinding, each burnt zone is wire-brushed and coated with a **2-component zinc-rich epoxy** (zinc-rich as ISO 12944-5 defines it, about 40 µm dry; assumption), covering every weld and every spot where the zinc is gone; a 2-component paint is a substrate Sikaflex-252's data sheet lists (bond spec section 8). Drilled holes and cut ends in the 0.8 and 1.0 mm galvanized wall stay as they are: indoors the zinc round them protects them (assumption). The bond doesn't land on the touch-up at the corners (the tape pieces sit at the member ends, bond spec section 2); where a rail's bead crosses a T joint it may, so T09's coupons include it (bond spec section 8). |
| Holes and rivnuts | **Every joint hole is made after welding** (spigot Ø8.5 and slot, Ø7.0 clearance, Ø19 access, Ø9.53 rivnut), by CNC or a drill jig that locates on the frame's joint faces and spigot hole, so welding can't move them off R-J6's ±0.2 or 2.11's ±0.1. **Rivnuts are set after the touch-up**, before the bond: **838003 is now Sherex CAH2-610-4.2, zinc-plated steel** (H-03; the Lead's review), with the same Ø12.96 × 0.76 head and 0.70–4.20 grip as the aluminium CAH3 it replaced, so every stopped seam stays 2.26 (rivnut head 0.76 on the 1.5 stop washer, D-64). Grip: 0.95 bare at the thinnest 1.0 wall, 2.5 with the stop washer; 0.76 bare at the thinnest 0.8 wall (calculation). No site joint's rivnut, bolt or spigot goes in a 0.8 member; DR's panel screws may (PM ruling 2026-11-01), with T06's DR coupons in that tube. |
| Flatness and size | **Seam faces flat within 0.5** (a 0.5 flatness zone over each seam face; the Lead's review), **skin-side faces within ±0.5 of one plane** with the frame lying free, and **diagonals equal within 1.5**, measured on a flat table after welding and before the holes; spigot holes and joint faces as 2.7 and 2.11. A frame outside these is straightened cold or rejected, never pulled flat by clamps on the bonding table. FAI: K-J05 for the seam faces (the first article of each frame number); the factory checks every frame the same way. On the bonding table the frame is pressed only until it touches every tape piece (bond spec section 8), so the bond line stays 3 ±0.5 (section 4). |
| Bond on galvanized steel | SikaTack Panel-50 and SikaTack Panel list no galvanized steel (their data sheets name anodized and coated aluminium, metal composite, laminate and ceramic), and the system's guideline sends galvanized steel to Sika's own technical information. **Sikaflex-252**, Sika's one-part polyurethane for bonding panels to frames in vehicle building, lists "sheet steel (including phosphated, chromated and galvanized components)", aluminium and 2-component paints on its data sheet (Sika Vietnam, 2025), and Sika's pre-treatment chart for its one-part polyurethanes (SPC) gives galvanized steel and aluminium the same route: abrasive pad and clean, **Sika Aktivator-205, Sika Primer-210**. So the bond moves to Sikaflex-252 with that route on both faces, with the joint and tape as before. Sika's lab report on the production tube and skin is HOLD-B4, and T09 tests it on galvanized coupons. Bond spec section 8. |
| Isolation, steel to aluminium | **Base band** (anodised aluminium, visible): the wall's steel bottom tube sits on the band's aluminium stop washers, held by the zinc-plated bolt in the band's zinc-plated steel rivnut, with the joint gasket between the faces. Zinc and aluminium sit close in the galvanic series, zinc is the side that would corrode, and indoors nothing stays wet, so there is no isolating washer, which would also change the 2.26 stop (ST-02); the zinc on the bottom tube's band face stays whole (touched up before assembly where it isn't). **DR's inner panel** (3 mm aluminium) sits on 838004 A2 washers on the rivnut heads with its 848013 foam, 2.36 off DR's frame, so it never touches the steel; stainless on aluminium is R-J10's washer, accepted indoors. **ACP skins:** held 3 mm off the steel by the bond line and its tape, both non-conductive; no screw or rivnut goes through them (J-LIN-01). The aluminium stop washers under steel rivnut heads on a steel frame are the same zinc and aluminium pair as at the band. |
| Order of work | Check the tube lot (grade, zinc, wall, straightness) → cut and mitre the members, cut the plates → weld in the jig (the corners with their plates, then the T joints) → cool, release, check flatness and diagonals → grind the beads on the skin-side and seam faces → wire-brush and paint every burnt zone with zinc-rich paint → drill or CNC every joint hole from the joint faces → set the rivnuts with their stop washers → bond the skin (bond spec) → fill and gaskets. |
| What can go wrong | A thin or weak tube (the lot check, HOLD-09); a corner welded without its plate (J-T7; FAI K-J17); warp (the jig, the order, MIG brazing; the flatness check); burnt zinc left bare (the touch-up); a cracked weld (J-T7); the bond on zinc (HOLD-B4, T09); a rivnut spinning in the steel hole (T06 in the steel tube). |
| Check and pass mark | **J-T7** (section 5): corner and T coupons in the production tube, process and plates, each corner past the highest factored corner lift of the frames that use it, at the thinnest wall: 167 N·m for the 1.0 mm corners (C1) and 206 N·m for the 1.2 mm ones and the 40 × 40 pair (L1, L2), without cracking. T06 and J-T1 in the galvanized tube; T09 on it; the lot check above; the FAI lines K-J05, K-J06, K-J16 and K-J17 (Control's). |
| Cancelled | **831003, 831004, 831005, 831006** (the frame cleats) and **108003** (their glue), proposed for D-117 in draft PR #203, which is closed: cancelled by D-131 and never used again (conventions §6). The draft's **HOLD-20 and HOLD-21** and its hardware rows **H-35 to H-39** went with it and aren't reused. |
| Status | Gauges DECIDED (D-131's rule, set by this check); the steel rivnut DECIDED (the Lead's review); the steel grade, the corner plates, the welding, finish, holes, flatness, bond route and isolation PROPOSED; HOLD-09, HOLD-22, HOLD-B4. |

**The check** (calculation, `frame_steel_check.py --check`, which also fails if 0.8 mm perimeters would pass, or if every grade under 280 MPa kept every frame at 90% or less, so neither rule stays without a reason). Section strength at the thinnest wall the spec accepts (95% of nominal, less the zinc), the lower of the two accepted grades:

| Tube, core wall at the thinnest accepted | kg/m (nominal) | In plane M_Rd (N·m), class | Across M_Rd (N·m) | Torsion T_Rd (N·m) |
|---|---:|---:|---:|---:|
| 20x40x0.8 (0.746) | 0.721 | 147, class 4 | 311 | 182 |
| 20x40x1.0 (0.936) | 0.890 | 200, class 4 | 383 | 225 |
| 20x40x1.2 (1.126) | 1.056 | 279, class 2 | 451 | 267 |
| 40x40x0.8 (0.746) | 0.972 | 362, class 4 | 362 | 372 |
| 40x40x1.0 (0.936) | 1.204 | 488, class 4 | 488 | 462 |

Frames: the corner lift at the thinnest wall with the plated corners; the steel frame's mass includes its corner plates; each panel keeps its other parts as its list on main gives them.

| Frame | Per pod | Aluminium frame (kg) | Steel frame (kg) | Panel (kg) | Corner lift need / have (N·m), thinnest wall | Use | Out of plane need / have (N·m) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 211101 L1 (R1 its mirror) | 2 | 3.10 | 9.80 | 18.0 | 205 / 279 | 74% | 93 / 225 |
| 211103 L2 (R2 its mirror) | 2 | 3.26 | 9.82 | 18.0 | 206 / 279 | 74% | 93 / 225 |
| 211201 B1 (B2, B3, B4 alike) | 4 | 2.37 | 6.52 | 12.8 | 110 / 200 | 55% | 49 / 225 |
| 411101 C1 (C2 alike) | 2 | 3.41 | 7.96 | 14.9 | 167 / 200 | 83% | 72 / 225 |
| the pod's 10 wall and ceiling frames | 10 | 29.0 | 81.3 | | | | |

Steel adds 52.3 kg to the 10 frames: 42.9 for the steel, the 1.2 mm side rails and the plates, 9.3 for D-135's added studs (calculation; the decor cores and DR are FRONT's count; B2's extra cross members are in WALL's list). The members' 1 to 2 mm cut-backs at the plates are left out of the masses.

| Corner lift, worst frame | Nominal wall | Wall at 95% |
|---|---:|---:|
| accepted grades (yield 280 or more) | 80% (C1, class 3) | 83% (class 4) |
| S250GD+Z, EN 10346 | 89% (C1, class 3) | 89% (class 3) |
| STKR400, JIS G3466 | 91% (C1, class 3) | 91% (class 3) |
| S235JRH, EN 10219-1 | 88% (L2, class 1) | 94% (class 3) |

The 280 MPa rule against the PM's 90%: the table shows C1 over it with a 235 or 245 MPa tube. The fallback without 280 MPa tube is in the Steel row above.

| Seam bolts and rivnuts, thinnest accepted wall | 0.8 mm | 1.0 mm |
|---|---:|---:|
| Rivnut 838003 grip, bare wall / with the 1.5 stop washer (range 0.70 to 4.20) | 0.76 / 2.30 | 0.95 / 2.50 |
| Pull-through round the rivnut's bulge (kN) | 6.6 | 8.3 |
| Pull-through round the bolt head's 18 mm washer (kN) | 9.1 | 11.4 |
| M6 bearing in the Ø7.0 hole (kN) | 3.2 | 4.0 |

The highest bolt loads are about 0.20 kN on the walls and 0.53 kN at DL (J-T1's pass loads are 3 × these); the rivnut's own strength is shown by T06 and J-T1 in the steel tube, not by a figure.

### 3.18 J-AIR-03: the roof grille on the roof sleeve (D-61)

| Field | Entry |
|---|---|
| Parts | AIR's roof grille 611602 (perforated aluminium, 50% free, 314 × 305 × 2.0, powder coated) over AIR's roof sleeve 611601 (galvanized steel, 294 × 285 × 68), whose top flange rests on C2's roof skin round the roof slot (D-61; AIR's parts list, #267). |
| Function and load path | Covers the roof slot and holds the sleeve's flange down on the roof. It carries its own weight (0.26 kg) and a knock: the sleeve's foot sits on the soft gasket on the exhaust fan box's top (#263), so nothing pulls on the screws. |
| Parts and process | **4 × 838001** (M6 × 16, ISO 4762 8.8 zinc) with **4 × 838004** washers (R-J10), through Ø7.0 holes near the grille's corners, into **4 × 838003** rivnuts that the factory sets in the sleeve's top flange: 2 near the corners of its left side and 2 of its back side (CEILING's layout; AIR's list, #267). Fitted on site from the roof at the guide's step 18, after the soffit hangs, with the 5 mm key (R-J2); snug, not torqued (HOLD-01 for the rivnut). |
| Fit | **CEILING sizes the flange to the 2-diameter rule** (19.1 from the hole's centre to any free edge, the skin's slot edge included; BASE's rule at J-FRONT-02, Reviewer 6's point): the rivnuts go only on the left side (an open bay) and the back side (19.2 before cross member 1), each about 19.2 from the slot edge, with the flange 40 wide on those two sides and 15 on the front and right, where C2's front member (5 from the slot's front edge) and side member (19.0, 0.06 short) leave no room; the grille follows the flange's outline. The flange must suit the rivnut's grip, 0.70–4.20 (SHX2). The rivnut bodies hang about 10 below the flange (installed length 10.16 max, SHX2), through clearance holes in C2's skin, clear of C2's frame (CEILING). The grille keeps a solid border at its screws, wide enough for the Ø18 washer (assumption; AIR's pattern is HOLD). |
| Mass | 45 g for the 4 bolts, 4 washers and 4 rivnuts (calculation: 4 × (6.2 + 2.8 + 2.3) g, AIR's list), counted in the roll-up's fixings line through this register's counts (2.1). |
| Check and pass mark | Driven from the roof with the 5 mm key (J-T5's reach check); the grille flat on the flange and no light through the slot with the pod lit (the guide's step 18 check). |
| Status | PROPOSED; the parts are AIR's (#267); the flange width and C2's clearance for the rivnut bodies are CEILING's. |

## 4. Tolerance stacks at the joint faces

Worst case, not the root of the sum of squares, unless marked: there are no process data yet (guideline §6.3).

| Stack | Contributors | Result | Status |
|---|---|---|---|
| ST-03: bolt in its Ø7.0 hole (R-J6) | Float (7.0 − 5.974) / 2 = 0.513; positions ±0.2 in each part from the spigot hole; rivnut float 0.065 | 0.05 to spare | calculation (CHK) |
| Spigot in hole and slot | Spigot Ø8 h9 in Ø8.5 H11 (assumptions); positions ±0.2 | Always enters; leaves up to ±0.25 of float, which the bolts take up | calculation |
| Outside faces flush across a seam | Frame depth 40 ±0.3 a panel (assumption; D-131: the steel tube's own size tolerance must meet it, HOLD-09); bond line 3 ±0.5 (bond spec); ACP 3 ±0.2 (assumption) | ±1.0 a panel unless the panels are bonded face down on a flat table with the ACP face as datum A (bond spec §5): then ±0.5 a panel, up to 1.0 between two | calculation; PROPOSED rule: the ACP face is datum A of every outer panel |
| Gap and squeeze at a stopped seam | Head 0.76 ±0.08 (SHX); stop washer 1.5 ±0.05 (assumption); gasket 3.97 ±0.4 (assumption) | Gap 2.13–2.39; squeeze 33–51% | calculation |
| ST-02: back wall closing gap and corner stops | 2.11, with ±0.1 spigot and spigot-to-face tolerances (PROPOSED) | Closing gap 5.2–5.8 inside 4.0–7.0; corner stops seat (±0.3 against ±0.25 play and ±0.26 float) | calculation |
| ST-04: ceiling closing gap | 2.11, same tolerances | 4.3–6.7 inside 4.0–7.0 (±2.0 at ±0.25 tolerances: too wide) | calculation |
| The lining floats clear of the frame at the bolts | Gap 4 (`cav_gap`, decided in SKL P04); every head inside its tube | Clear by design; the clip's own height is HOLD-08 | calculation |

## 5. Tests

Physical tests stay PLANNED until real data exists (guideline §10); the factory's wall-and-door sample is the physical check (D-32). **The sample package's tests take precedence** (R-J12): this register's rivnut, access and bond tests are folded into the package's T06, T11 and T09, which this PR updates to the joint as drawn. The tests the package doesn't have yet are listed as J-T1 to J-T7, for the PM to route into the package or a later sample.

| Test | What | On | Pass mark | Status |
|---|---|---|---|---|
| **T06** (package) | Rivnut spin-out with the joint's own stack: the CAH2-610-4.2 (steel, D-131) set through the 1.5 mm stop washer in a 40 mm face of the real 20 × 40 × 1.0 galvanized steel tube; torque applied by an M6 × 16 ISO 4762 with its ISO 7093 6.4 × 18 A2 washer, through a 1.0 mm galvanized steel wall coupon with a Ø7.0 hole; 2 cut open to check the bulge clears the far wall; plus 5 in DR's 0.8 mm galvanized panel-screw tube (PM ruling 2026-11-01) with an 838004 on the rivnut head as the panel's stop (H-34) | S7 coupons | The package's PM-ruled limit: torque at most half the lowest spin-out torque, and no turning, loosening or stripping in 5 cycles; plus the wall under the head washer doesn't dish at that torque (R-J10); DR's panel screws' torque is set the same way from their 5 coupons | PLANNED |
| **T09** (package) | The ACP bond (bond spec sections 6 and 8): Sikaflex-252 on the galvanized tube with Aktivator-205 and Primer-210 (D-131), half the coupons across a T joint's touched-up weld | S7 coupons; S1 | The package's PM-ruled pass mark: every coupon fails in the adhesive itself | PLANNED |
| **T11** (package) | Timed assembly: two people, one 5 mm key, carry S1, set it on its spigots, drive its 4 base bolts through the pocket, clip S2 on; 5 cycles | S1, S2 on R1 | The package's pass marks; and every bolt reached through its pocket | PLANNED |
| J-T1 | Pull-out and shear of a whole joint: M6 × 16 through a bolt-side tube into a rivnut and stop washer in a nut-side tube (20- and 40-deep), all in the production galvanized steel tube (D-131), and a closing-seam pin | 5 of each | Failure at 3 × the joint's highest bolt load or more (assumption: about 0.6 kN for the walls, 1.6 kN for DL), no loss of fit after 5 cycles (REQ-ASM-09) | PLANNED, to route |
| J-T2 | Captive retainer: the bolt stays in its tube when the panel is shaken, carried and turned over; drives and backs out 5 times | 5 | Doesn't fall out; grips at least 3 × the bolt and washer's weight (assumption) | PLANNED, after HOLD-02 |
| J-T3 | Seams: gap at every bolt, flushness, gasket squeeze, light and air through the seam; push test at 1.2 m with LC2; on one stopped seam and one closing seam set at 4.0 and 7.0 | wall sample or a seam mock-up | Stopped gap 2.26 ±0.15; faces flush within 0.5 (assumption); no light through either seam; no step after the push | PLANNED, to route |
| J-T4 | Base seal (D-132): **taken by the package's T15** (R-J12): R1's base lip across the glides' range, on a hard floor and on carpet tile | R1 fitted with the lip | T15's pass mark: no light past the lip on either floor | PLANNED (package T15), after HOLD-06 |
| J-T5 | Corner and ceiling mock-up: a side panel corner, the back closing seam, and both ceiling halves closed in the R-J9 order | joint mock-up | Every bolt reached, overhead too; **every part drops in or slides past its seal with 150 N or less per edge by hand, overhead included** (push-pull gauge; R-J17); C2 drops in past the lead-in; the corner stops close with the bolts; faces flush within 0.5 | PLANNED, to route |
| J-T6 | Hook-in corner keys: the back band lowered by two people between both side bands' studs (111211, D-129), and the FL corner (111212): set FL1 10 mm high, push it along the studs, lower it onto its preset glides | joint mock-up with 3 band pieces, the back band at full length | Hooks home by hand with no tool, the back band at 150 N or less per end, its heads up through its bottom wall's notches, and resting on its glides with both upper shanks clear of their slots' closed ends; under a 300 N pull across the joint (assumption) the corner stays closed and level within the glide's setting; 5 cycles; with the glides at 8.5, the keys' screw heads stand at least 5 off the floor (F-018) | PLANNED, to route |
| J-T7 | Welded joints in the production tube, process and plates (J-FRAME-01, D-131): 5 corner coupons of each kind the frames use, each with its 2 mm plate (two 20 × 40 at 45° in 1.0 and in 1.2; a rail on a 40 × 40, in 1.0 and in 1.2; two 40 × 40), legs 400 long, bent in plane to failure; 5 T coupons (a 0.8 stud on a 1.0 and on a 1.2 rail) bent and pulled to failure; 2 of each sawn through the weld | 25 corner and 10 T coupons, plus the sawn ones | Corners: no crack up to the highest factored corner lift of the frames that use that kind, at the thinnest wall (167 N·m for the 1.0 mm kinds, C1; 206 N·m for the 1.2 mm kinds and the 40 × 40 pair, L1 and L2; calculation), and failure in the tube, not at the weld or the plate; T joints: failure in the tube; sawn welds all round with no lack of fusion or bonding over more than 10% of the length (assumption) | PLANNED, to route; before S1's frame is welded (HOLD-22) |

## 6. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Owner | Released when |
|---|---|---|---|---|
| HOLD-01 | Rivnut tightening torque (D-48, ISS-011) | None: T06 sets it | Hardware Engineer | T06 recorded and the PM sets it (package H05) |
| HOLD-02 | Captive retainer (H-02): an elastomer grommet for a Ø19 hole in a 1.0 mm galvanized steel wall (D-131; it was 1.2 mm aluminium) that grips an M6 socket head (Ø10) | Which grommet, with what grip on the head, survives 5 drive-and-back-out cycles? | Joints Engineer with the Hardware Engineer | Part named; J-T2 passed (package H13) |
| HOLD-03 | Rivnut head thickness and installed length | — | — | **Closed** (SHX) |
| HOLD-04 | Rivnut edge distance | To Sherex, for the steel CAH2-610-4.2 (D-131): its hole size (Ø9.53 +0.10 as the aluminium part's?); a trivalent zinc finish (its item page shows a yellow dichromate); the minimum distance from the hole to the edge of a 1.0 mm steel face, and of DR's 0.8 mm one: is 9.2 mm (the corner and ceiling bolt lines, 2.4) enough, and about 3.6 mm of flat each side of the hole in a 20 mm face? | Hardware Engineer | Answer on file, or T06's coupons show no cracking |
| HOLD-05 | Joint gasket thickness and converter | PORON 4701-40 with adhesive in 8 mm strips, 3.97 mm thick | Hardware Engineer | The converter's strip data on file (package H14) |
| HOLD-06 | Base seal: a soft lip on the band's inner face that presses on the room floor (H-06, 118001; D-132) | Which soft lip, sold by the metre and bonded to the anodised band, reaches 21.5 below the band and stays on the room floor over the glides' range (8.5 to 18.5), on a hard floor and on carpet tile, with a published force low enough not to lift the band? | BASE engineer | Part named with its range and force; T15 passed |
| HOLD-07 | Base band top wall 2.7 mm or thinner (grip with the stop washer) | None: BASE design | BASE engineer | Band drawing with its wall thickness |
| HOLD-08 | Cassette clip 518001 and ceiling catch 518002 (D-56, ISS-076) | SEL question 10, plus points 1–6 of J-LIN-01: a clip rated for 8.3 kg in shear and 8.0 kg in pull-out with a captive lock that doesn't bridge the lining; a lanyard rated for 48 kg | Hardware Engineer; Layout Engineer | Parts with ratings named; T07 and T08 passed |
| HOLD-09 | Frame tube steel (D-131; it was 6063-T6, D-79, ISS-034) | The tube maker's certificate and the lot check for S1's tube: yield 280 MPa or more (S280GD+Z, SGC400, or 3 tensile tests), Z100, walls 95% of nominal or more, straight within 0.5 over a length, outside corner radius and size tolerance (J-FRAME-01) | Hardware Engineer, with the factory | Certificates and the lot check on file; J-T7 passed |
| HOLD-10 | Decor back plate at the J-FRONT-01 bolts: aluminium 1.0–2.7 mm with the frame behind (ISS-045) | None: FRONT design | FRONT engineer | FRONT CAD shows it |
| HOLD-11 | The back wall's top edge under the ceiling | — | — | **Closed** (R-J4) |
| HOLD-12 | Closing-seam bulb seal (H-04B, 848004) | Which EPDM or TPE hollow bulb has a published working gap covering 4.0–7.0 mm and a closure force low enough for a 150 N fit-up per edge, and survives being reused? (The tesamoll D-Profile's 3–7 mm range is published; it is consumer grade, with no force data) | Hardware Engineer | Part named with its range and force; J-T5 and J-T3 passed |
| HOLD-13 | Cassette edge seal (H-14, 848012) | Which PSA foam strip 2.0–2.2 mm thick pushes no more than about 2 kPa at 20% compression (or which fin seal) and still closes a 2.26 mm gap against light? | Hardware Engineer | Part named with its force data; the wall sample's cassettes stay seated on their clips with it fitted (T07, J-T3) |
| HOLD-14 | Front corner keys (111212, 111213, 111214) | — | — | **Closed**: BASE's front geometry gives the cuts and positions (J-BASE-02, corner-keys.csv) |
| HOLD-15 | The intake support rail behind the mesh piece (J-BASE-02) | None: BASE posts the rail's section and line; at its ends it needs the band's 37 × 97 bore, for 111215 at X 915 and the end cap that takes 111213 | BASE engineer | The rail drawn with its key seat and end cap |
| HOLD-16 | M3 countersunk rivnut 838008 in BASE's sill (J-FRONT-04) | Which M3 countersunk-head rivnut has a grip range for the sill seat's wall and sits flush; do the M3 heads (1.86 tall) clear the glass's setting blocks in the 1.5 mm channel? | Hardware Engineer; BASE and FRONT engineers | Part named with its grip and hole data; FRONT's channel drawing shows the heads clear |
| HOLD-17 | How the 2 spigots fix into the floor panel F2's 9 mm ply (J-AIR-02) | None: BASE design; an M6 insert (838009) is proposed: which one holds a spigot in 9 mm ply? | BASE engineer | F2 drawn with the spigots and their insert |
| HOLD-18 | Head room for the air parts' studs (J-AIR-01, J-AIR-02) | — | — | **Closed** (PM ruling 2026-11-01): the model follows the register: the hanger studs stay M6 × 16 socket heads (838001, 6 mm heads), and AIR deepens its head room to at least 7.5 mm without moving the soffit's underside (Z 2120). Each stud's gauge follows AIR's rail and plate thickness as its model gives them |
| HOLD-19 | The access-panel seal 848013 (H-34): DR's inner face panel | Which very soft foam strip with PSA, 4.0 mm thick and about 8 wide, pushes about 5 kPa or less at 40% squeeze, has published compression-set data at 40–45%, recovers after the panel is taken off and refitted several times, and closes the 2.36 gap against light and air? | Hardware Engineer | Product named with its force and compression-set data; FRONT's DR panel refitted 5 times with no light through the seal |
| HOLD-20, HOLD-21 | — | — | — | **Not used**: they were the cleats' HOLDs in draft PR #203, closed when D-131 cancelled the cleats |
| HOLD-22 | Welding procedure for the steel frames (J-FRAME-01) | None: the factory's own. MIG brazing (CuSi3) or short-arc MAG (G3Si1), its settings, the jig and the order, the mitre plates, written down and proved on J-T7's coupons | The factory, with the Joints Engineer | The procedure on file and J-T7 passed |
| HOLD-23 | The kick strip's end seal 368008 (H-43, D-150) | Which adhesive-backed pile or brush strip, fitted on site on the kick strip's end face and pressed down onto the floor: about 105 long (the floor to Z 105), a dense pile long enough to bridge the 4.5 mm slot to BASE's end plate with some overlap, **whose own data sheet names its adhesive and its lowest fitting temperature**, with published air or sound data for a gap that size? | Hardware Engineer, with FRONT | Product named with its data sheet, adhesive and lowest fitting temperature on it; the Air Engineer's open area for the slot confirms it (D-150) |
| HOLD-24 | DT stands on its own (J-FRONT-03, D-152) | — | — | **Closed** (2026-11-01, FRONT's model): DT's centre of mass is at X −343, Y −697.5, Z 2243 (7.84 kg, each part at its parts-list mass), 45 to 65 mm behind the line from DR's spigot at X 410 to the front end of DT's bearing on DL's slope, so it stands on DR's two spigots and the slope with nothing added; the door catch's pull acts at about the same Y |
| HOLD-25 | The kick strip's hinge-end seal (H-46) | Which adhesive-backed pile or brush strip, as HOLD-23's but with a longer pile for the 11 mm slot to BASE's plate in FL2's door end (FRONT posts the pile length): about 105 long, fitted on site and pressed down onto the floor, whose own data sheet names its adhesive and its lowest fitting temperature, with published air or sound data for a gap that size? | Hardware Engineer, with FRONT | Product named with its data sheet; FRONT's pile length; the Air Engineer's open area for the slot |

## 7. Open for others

1. **Skeleton (Fusion Engineer 2):** the closing gap 5.5 at X 0 for the back wall and the ceiling, so the frames are 1198.99 wide while the skins stay 1200.61 (2.8, R-J16); the 220 mm bolt rule on every bolted edge (2.9); the bolt lines at the tube centres, Y +824 and Z 2374 (2.4, R-J15). Also: n_ceil_back_bolt 4 on the frame width (1198.99, pitch 253.00) and the side pitch 351.67 from Y −645 along the ceiling, replacing P04's 3 bolts on the skin width and 350.91 on the side panel; DT's back plate at Y −647.26 (J-FRONT-03).
2. **BASE, WALL and CEILING drawings:** every stile at least 30 mm from a bolt (R-J14); ±0.1 on every spigot position and every panel's spigot-to-joint-face distance (ST-02, ST-04); the skins' 1.62 mm overhang at the closing seams (FR-14); the outside corner and the back top edge, where the side panels' back members and the ceiling's back member show (3.2). BASE: the corner keys' seats, fixing holes and keyholes (J-BASE-02, [`corner-keys.csv`](../../01-CAD-Native/joints/corner-keys.csv)): keyhole entries below the studs; end caps with keyholes on FL1, FL2, the intake support rail and FR1; at the back corners (D-129) the keys in the side bands' back ends against their inner walls, 2 × Ø7.0 in each inner wall for the stud bolts, the back band's end caps with their slots open at the bottom and its bottom wall's head notches, the side bands' back-end caps no deeper than 2 mm and no glide in their last 70 mm; the rail's section (HOLD-15); glides clear of the keyed ends; the spigots for DL and DR's support (J-FRONT-02) and on F2 for the air column (J-AIR-02, HOLD-17); the sill's M3 countersunk rivnuts (J-FRONT-04, HOLD-16); the base seal at the floor's edge (D-86). FRONT: Ø8.5 holes and slots under DL, DR and DT, 2 spigots in DR's DT ledge 140 apart, DT's 2 mm back plate at Y −647.26 with its 4 rivnuts at Z 2374 (J-FRONT-03); the fixed glass channel's last M3 hole at X 905 (D-111, done in #169), with BASE's last sill rivnut under it (J-FRONT-04); DR's access panel's 2 rivnuts for the air column's hook studs at X 971, Z 1700 and 1850 (J-AIR-02); the glass channel's 4 M3 countersunk holes (J-FRONT-04). CEILING: the front tubes' Ø7.0 and Ø19 holes for DT (J-FRONT-03); the soffit's hanger and lock rivnuts are in PR #32 (J-AIR-01).
3. **Decision log (control pack):** rows for R-J1 to R-J16, including the parts of D-08 (tool-free seam clips) and D-49 ("face to face") they change.
4. **Sample package:** P05–P07 and the new head washer and retainer rows, T06's stack, T09's bonded face, H13 and H14 are updated in this PR (R-J12); J-T1 to J-T5 wait for the PM to route.
5. **AIR and the assembly guide:** AIR deepens its head room under the soffit rails to at least 7.5 mm, keeping the soffit's underside at Z 2120, and gives the studs' gauges from its rail and plate thicknesses (PM ruling, HOLD-18 closed); the guide sets FR1 after the intake support rail, as the keys need (J-BASE-02), and, for D-129, sets both side bands before the back band in step 2, the back band lowered between them by two people, and nobody lifting it or standing on it until B1 and B2 are bolted in step 4, and counts the soffit's 2 lock screws and the roof grille's 4 (92 site bolts).
6. **D-131, the steel frames (J-FRAME-01; the mitre plates 831007 to 831009, H-40 to H-42):** **WALL** builds L1 as the sample in steel: the gauges (1.2 mm rails and front stiles on the side panels), D-135's studs, the mitre plates and their cut-backs, no cleat slots; the material, weld, finish and hole notes on its drawing; its list with masses; then the other walls. **CEILING** does the same in its steel switch (cross member 1 at 1.0, 2 and 3 at 0.8). **FRONT** builds the decor cores and DR by the same rules, with their own masses and lift case; DR's panel-screw rivnuts may go in 0.8 (PM ruling). **Control** (sent in the joints group): D-131's rows and the cancelled numbers 831003 to 831006 and 108003 in the decision log; the mitre plates 831007 to 831009 in the allocation list and the master BOM; 838003's new name in the master BOM; the FAI lines K-J05, K-J06, K-J16, K-J17 and K-P03; and the sample package's T06, T07, T08 and T09 on galvanized steel coupons, with S1, R2 and their parts rows (the Lead's review).

## 8. Feature-rationale inputs for the Fusion Engineers

What each joint puts into each part, and why (guideline §7). "Nut side" and "bolt side" as in 2.2. Hole tags go on the drawings. X and Y are the pod axes (conventions §4).

| ID | Part | Feature | Size | Where (rule) | Why | Status |
|---|---|---|---|---|---|---|
| FR-01 | Nut side of every stopped joint: lower panels' top tubes; the band's top wall; side panels' 40 × 40 back members; upper side panels' 40 × 40 top members; ceilings' 40 × 40 back members (bottom face); the decor's back plate. Bolt side of the closing seams: B2's, B4's and C2's left tubes | Rivnut hole (with the H-08 stop washer, except at the closing seams) | Ø9.53 +0.10 through one wall of 2.7 or less | At the 220 mm rule (2.9), on the bolt-side tube's centre line | H-03 needs it (SHX); the stop sets 2.26 (2.8) | source (hole); positions DECIDED for the band, PROPOSED elsewhere |
| FR-02 | Bolt side of every stopped joint: upper panels' bottom tubes; walls' bottom tubes; back panels' outer tubes at the corners; ceilings' side tubes; back panels' top tubes; side panels' front members. Nut side of the closing seams: B1's, B3's and C1's right tubes | Clearance hole | **Ø7.0, position Ø0.4 (±0.2) from the spigot hole, CNC or drill jig** | Coaxial with FR-01 | ST-03 (R-J6) | DECIDED |
| FR-03 | Every bolt-side tube | Access hole in the bay-side wall | **Ø19** | Coaxial with FR-02, or with FR-01 at the closing seams | Passes the Ø18 head washer, the Ø10 head and the key (2.2) | calculation |
| FR-04 | The band's top wall; lower panels' top tubes; back panels' top tubes under the ceiling | Spigot rivnut | Ø9.53 +0.10 | 100 from each end (R-J13) | Holds H-05; the part stands located before its first bolt (REQ-ASM-04) | DECIDED for the band; PROPOSED elsewhere |
| FR-05 | Walls' bottom tubes; upper panels' bottom tubes; ceilings' back members (bottom face) | Spigot hole and slot | Ø8.5 round at one end, 8.5 × 14 slot at the other: along the edge, except **along X at the side panels' back ends** (R-J17) | Coaxial with FR-04 | One fixed point and one slot (R-J13); the side panels drop clear of the corner gasket (2.7) | DECIDED |
| FR-06 | Side panels' back members (L1, L2, R1, R2); upper side panels' top members (L2, R2); ceiling halves' back members (C1, C2) | Member size | 40 × 40 instead of 20 × 40 (1.0 mm steel since D-131; it was 1.2 mm aluminium) | Whole length of that edge | Overlap 34 instead of 14 (2.4) | DECIDED (R-J3); +3.13 kg in steel (2.4) |
| FR-07 | Back panels' outer tubes at the corners; back panels' top tubes; ceilings' side tubes | Bolt line | Y +824 or Z 2374 | The bolt-side tube's centre | Room for the Ø19 hole (2.4) | DECIDED (R-J15) |
| FR-08 | Side panels' front members | FR-02 and FR-03 pair, along Y | as FR-02, FR-03 | 3 per panel at the 220 mm rule, X ∓1224 | J-FRONT-01 | PROPOSED |
| FR-09 | Every site joint | Frame gap | 2.26 stopped; 5.5 (4.0–7.0) closing | 2.8 | Gasket squeeze set by the stop or the gap | DECIDED (R-J5, R-J16) |
| FR-10 | Wall panel bays at each bolt (bolt side) | Fill pocket | 60 × 60 × 40, no fill; every stile at least 30 mm from the bolt | In front of each FR-03 | The key's reach (2.3); R-J14 | PROPOSED pocket (assumption); 30 mm DECIDED (R-J14) |
| FR-11 | Every joint face (nut side) | Seal | Stopped joints: PORON strip 8 × 3.97 (848001). Closing seams: the bulb seal (848004) | Beside the washer or pin line, outer side, unbroken | R-J7, R-J17, 2.5 | DECIDED (R-J7, R-J17); parts HOLD-05, HOLD-12 |
| FR-12 | Frame tubes behind the cassette clips and the ceiling catch | Clip and catch fixings | HOLD-08 | Reserve an UNVERIFIED envelope only | D-47, D-56 | HOLD |
| FR-13 | The closing seams' faces | Lead-in chamfer | 1 × 45° | C1–C2 lower edges; B1–B2 and B3–B4 top edges | R-J9 (2.10) | DECIDED (R-J9) |
| FR-14 | Back panels' and ceiling halves' skins (B1–B4, C1, C2) | Skin width and overhang | Skin 1200.61 on a 1198.99 frame: flush at the stopped edge, 1.62 past the frame at the closing seam | The closing-seam edge: right edge on B1, B3, C1; left edge on B2, B4, C2 | Visible skin seam 2.26 nominal everywhere, 0.76–3.76 at the closing seams (2.8) | DECIDED (R-J16) |
| FR-15 | End caps at the front joints: FL1 (corner), FL2 (knee), the intake support rail (corner), FR1 (X 915). The back band's two end caps (D-129). The side bands' inner walls at the back corners (D-129) | Keyholes and slots in a 1.5 wall or plate | Front: per joint, 2 keyholes, a Ø12 entry centred 10 below the stud's seat and a 6.5 slot running 10 up to it. Back band: per end cap, one 6.5 slot open at the bottom edge, 12 wide at its mouth over its bottom 6, up to Z 73.5 (its closed end's centre), and a 1 × 45° bevel on the cap's bottom edge, side-band side; at each end, a notch in the bottom wall 12 wide and 9 deep from the end, on Y +830, for the heads. Side bands: 2 × Ø7.0 through the inner wall, for the stud bolts | Front: seats at Z 37.5 and 71.5 on the joint's centre line, entries at Z 27.5 and 61.5. Back: the slot and the Ø7.0 holes on Y +830, the holes at Z 37.5 and 71.5 (corner-keys.csv) | J-BASE-02 (D-87, D-129): front pieces go on along their studs and down 10; the back band drops straight in between the side bands | PROPOSED |
| FR-16 | Carrier ends (the side bands' back ends, the key against the inner wall (D-129); the side bands' front ends, FL1's knee end, the rail's end at X 915); keys 111211 to 111215 | Key seat and fixings | Ø7.0 × 2 in the carrier's bottom wall; in the key, M6 thread 15 deep (Ø5.0 drill 18) × 2 from its bottom and M6 tapped through × 2 square to its stud face | Fixing holes 10.5 from the key's back face and 7.0 either side of its centre line (111212 to 111215); on 111211, 6.0 either side, at 10.5 and 17.8 from its back face; studs 26 and 60 above its bottom (corner-keys.csv) | J-BASE-02 | PROPOSED |
| FR-17 | The band's FL1 and FL2 tops (DL); the top flange of BASE's closing angle, 2 mm, along Y −645 (DR); DR's DT ledge (DT) | Spigot rivnut (831001 in 838003) | Ø9.53 +0.10 | DL, 13 in from the band's outer face: (−1176.7, −718.0) round, (−1073.9, −780.6) slot; DR: (1050, −656.5) round, (1147, −656.5) slot; DT on DR's ledge: (270, −657.9) and (410, −657.9) | J-FRONT-02, J-FRONT-03 | PROPOSED (FRONT's update, PM 2026-11-01) |
| FR-18 | DL's and DR's bottoms; DT's underside | Spigot hole and slot | Ø8.5 round and 8.5 × 14 slot at the FR-17 points (DL's round at its back, DR's round at X 1050; DT's as FRONT draws it) | Coaxial with FR-17 | J-FRONT-02, J-FRONT-03 | PROPOSED |
| FR-19 | DT's back plate; the ceiling's front tubes | Joint holes and plate position | FR-01, FR-02 and FR-03 at X −981.74, −578.16, −174.58, +228.99; DT's back plate at Y −647.26 | 2.9, J-FRONT-03 | J-FRONT-03 | PROPOSED |
| FR-20 | The ceiling frame's front members and X1 (undersides) | Soffit hanger and lock rivnuts (838003) | Ø9.53 +0.10 | Hangers at X ∓583, Y −635 and Y −291; locks in C1's front member at X −1100 and −950 (CEILING PR #32) | J-AIR-01 | PROPOSED (positions CEILING's, PM ruling 2026-11-01) |
| FR-21 | DR's access panel | Hook stud rivnuts (838003) | Ø9.53 +0.10 | X 971, Z 1700 and 1850 (AIR) | J-AIR-02 | PROPOSED |
| FR-22 | Floor panel F2 | Spigots for the air column's foot | 831001 in an M6 insert (HOLD-17) | S1 X 989, Y −605; S2 X 1126, Y −337 | J-AIR-02 | PROPOSED |
| FR-23 | BASE's sill seat on FR1; the fixed glass's bottom channel | M3 countersunk rivnut holes; countersunk clearance holes | Rivnut hole per HOLD-16; Ø3.4 with a 90° countersink in the channel (assumption) | 4 along the 745 mm channel (FRONT and BASE) | J-FRONT-04 | PROPOSED |

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
