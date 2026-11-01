# Bond specification: ACP skin to frame (factory bond)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-02 (row in `document-register.csv`) | P01 | DRAFT | 2026-10-31 | Joints Engineer (v2 Milestone 2) |

This is the bond specification the guideline asks for (§8.2, and Milestone 2 item 6), for the one structural bond in the decided build: the 3 mm ACP skin to the 20 × 40 × 1.2 aluminium frame of every wall and ceiling outer panel (ISS-016). With no plywood behind the ACP (D-17), this bond is what holds the skin on. It is made in the factory only; nothing is glued on site (REQ-ASM-05).

**D-131 (PM ruling, 2026-11-01):** the frames are now welded, pre-galvanized steel (joints register J-FRAME-01). SikaTack Panel-50's data sheet and Sika's tables for it list no galvanized steel, so the adhesive changes to **Sikaflex-252**, whose data sheet lists galvanized sheet steel and aluminium, with **Sika Aktivator-205 and Sika Primer-210** on both faces. **Section 8 governs** where it differs from sections 1 to 7, which stay as the record of the aluminium design.

Not covered: the felt on the lining cassette's steel tray (LINING, ISS-015), the gasket and seal tapes (pressure-sensitive, in the joints register), and sealants.

Status words as in the joints register: numbers carry confirmed, source, calculation, assumption or unverified (conventions §9); choices are PROPOSED unless a D-number or a PM ruling is cited. No supplier was contacted.

## Result

1. **Bond system: SikaTack Panel-50**, a one-part, moisture-curing silicone with an ETA for wall cladding (ETA 19/0511), **with SikaTack Panel Fixing Tape** (3 × 12 mm polyethylene foam) to set the joint at 3 mm and hold the skin while it cures. Both faces are pre-treated with **Sika Aktivator-205 and SikaTack Panel Primer**, after a very fine abrasive pad on mill-finish aluminium (Sika's general table). Joint: **12 × 3 mm**, one on every frame member that touches the skin. This is the hardware selection's pick (A9); status source.
2. **B1. The 20 mm tube face is too narrow for Sika's layout.** Sika puts the tape and the bead side by side, with the bead at least 5 mm from the tape and from the rail's edge. That needs about 32 mm of flat face (calculation); the frame's skin-side face is 20 mm wide. **Proposed:** one bead centred on every member, with the 3 mm thickness set by short pieces of the same fixing tape **in line** with the bead, and the panel bonded face down on a flat table. That departs from Sika's "tape along the whole length", so it needs Sika's written OK (HOLD-B2), and the package's T09 coupons test it.
3. **Design check:** the skin's own weight puts about **1.1 kPa** of shear on the bond, and a 2 g bump in shipping about **2.3 kPa** of tension (calculation). Against the ETA's design values, about 12 kPa in long-term shear and 150 kPa in tension (unverified: read from a search engine's extract of the ETA; the PDF itself wouldn't download, HOLD-B1), that's at least 10 times inside them, on top of the ETA's own safety factors. The bond's real strength is shown by coupons on the real skin, frame finish and process (section 6), not by a catalogue figure (guideline §8.2).
4. **Mass: about 4.4 kg for the pod** (calculation: about 79 m of bead at 40 ml/m and 1.4 kg/l), 0.28 kg/m² against the 0.25 kg/m² the layout study assumed: **+0.5 kg** over its estimate.
5. **HOLDs: 6** (section 7): the ETA text, Sika's OK for the in-line tape, the cure time before handling, the ACP's back-face coating and the frame's finish, the coupon results, and Sikaflex-252's data for this use (HOLD-B6).
6. **Steel frames (D-131, section 8):** **Sikaflex-252** on the galvanized frame and the ACP, each face pre-treated with an abrasive pad, Sika Aktivator-205 and Sika Primer-210 (Sika's pre-treatment chart for one-part polyurethanes); the same 12 × 3 joint and in-line tape pieces; frames flat to ±0.5 on the skin side and pressed only onto the tape pieces. The bond's stresses stay under 0.5% of the adhesive's 2.5 MPa lap shear (calculation). About **4.4 kg** a pod with D-135's added studs (calculation).

## 1. Sources

| Key | Document | Status |
|---|---|---|
| TDS | SikaTack® Panel-50 Product Data Sheet, Version 04.01 (12-2023), en_DK, Sika Danmark A/S, [PDF](https://dnk.sika.com/dam/dms/dk01/7/sikatack_panel-50.pdf), read 2026-10-31 | source |
| TAPE | SikaTack® Panel Fixing Tape Product Data Sheet, Version 02.01 (03-2023), en_DK, [PDF](https://industry.sika.com/dam/dms/dk01/m/sikatack-panel-fixingtape.pdf), read 2026-10-31 | source |
| GG | General Guideline SikaTack® Panel System, Version 05, September 2025, Sika Services AG, valid until September 2030, [PDF](https://industry.sika.com/dam/dms/global-industry/m/general-guidelinesikatackpanelsystem.pdf), read 2026-10-31 | source |
| ETA | ETA 19/0511 of 04.04.2024 (ITeC), [PDF link](https://itec.es/certificacio/files/eta_19_0511_04.04.2024_en.pdf). The link returned a web page, not the PDF, on 2026-10-31; the design values below come from a search engine's extract of it | unverified, HOLD-B1 |
| SEL | `v2/05-Engineering/hardware/selection.md` A1 (Alcorest ACP), A9 (adhesive pick), G (emissions) | source |
| LAY | `v2/05-Engineering/layout-study/report.md` §10 inputs: `bond_kgm2` 0.25 kg/m² (assumption); `stud_pitch_acp` 400 (D-16); open item LS-02 | source |
| JR | [`joints-register.md`](joints-register.md): load cases (section 2.6), datum rule (section 4) | — |
| S252 | Sikaflex®-252 Product Data Sheet, Version 04.03 (08-2025), en_VN, Sika Limited (Vietnam), [PDF](https://industry.sika.com/dam/dms/vn01/m/sikaflex-252.pdf), read 2026-11-01. Also en_CA Version 03.01 (04-2023), [PDF](https://can.sika.com/dam/dms/ca01/1/sikaflex-252.pdf), the same values | source |
| SPC | Sika pre-treatment chart for 1-component polyurethanes, Sikaflex-100 and -200 series (2020), [PDF](https://aus.sika.com/dms/getdocument.get/c080b021-d54c-4ad5-821f-0bd2efa46f1e/Pre-treatment_Chart_1C_PU_2020.pdf), read 2026-11-01; its 2015 edition (Version 6) for the Sikaflex-200 and SikaTack series gives galvanized steel the same products | source |
| STP | SikaTack® Panel Product Data Sheet, Version 05.02 (08-2025), en_VN, [PDF](https://industry.sika.com/dam/dms/vn01/t/sikatack-panel.pdf), read 2026-11-01: its substrates, like Panel-50's, are "anodized and coated aluminum, metal composite, high pressure laminate and ceramic materials" | source |

## 2. The specification (guideline §8.2)

| Item | Specification | Status |
|---|---|---|
| Adhesive | SikaTack® Panel-50, product code 012636210019001000, TDS Version 04.01 (12-2023). One-part silicone, moisture curing, grey; density 1.4 kg/l; Shore A 38; tensile strength 2.1 MPa and elongation at break 450% (ISO 527); tear 7 N/mm (ISO 34); service −40 to 150 °C; shelf life 9 months below 25 °C. "Carries ETA 19/0511, Adhesive for wall cladding by ITeC." Suitable substrates include "anodized and coated aluminum … metal composite". | source (TDS) |
| Spacer and initial hold | SikaTack® Panel Fixing Tape, TDS Version 02.01 (03-2023): closed-cell polyethylene, pressure-sensitive adhesive both sides, 3 × 12 mm, 33 m roll; compressive strength 0.12 MPa at 50%; service −40 to 70 °C. "SikaTack® Panel Fixing Tape is not a structural component … never include the mechanical values of the tape in the calculation." | source (TAPE) |
| Surface 1 | Back face of the ACP skin: Alcorest 3 mm, 0.21 mm aluminium skins, plastic (PE-type) core, front colour EV3038 Dark Yellow (D-12, SEL A1). The back face's coating isn't published: bare aluminium, a primer or a service coat (**HOLD-B4**). | source (SEL A1); coating HOLD |
| Surface 2 | The skin-side face of each 20 × 40 × 1.2 frame member (20 mm wide). Alloy, temper and finish are open (ISS-034): anodised or mill finish are in Sika's table; powder coat isn't and would need Sika's lab test (**HOLD-B4**). | confirmed size (D-54); finish HOLD |
| Pre-treatment, ACP back face | Sika's general recommendation for metal composite panel (aluminium surface): **Sika® Aktivator-205 + SikaTack® Panel Primer** (GG §5.4, Table 2). If the back face is coated, Sika's project test decides (GG §5: "Suitable surface pre-treatments based on the results of the related laboratory report are mandatory"). | source (GG); HOLD-B4 |
| Pre-treatment, frame | Anodised: **Aktivator-205 + Panel Primer**. Mill finish: **abrasive pad very fine, clean (e.g. Sika® Cleaner P), Aktivator-205 + Panel Primer** (GG Table 2). | source (GG) |
| Flash-off | Aktivator-205: at least 10 min at 15 °C or more, 30 min below 15 °C, at most 2 h; not wiped dry afterwards (GG §5.1). Primer: one thin, complete coat, never repeated; flash-off "at least 10 minutes at 23 °C" (GG §5.2) and "at least 30 minutes" (GG §7): **30 min is used** (assumption: the stricter of Sika's two figures); adhesive within 2 h of the primer (GG §5.2). | source (GG); 30 min assumption |
| Bond area and geometry | One joint **at least 12 mm wide × 3 mm thick** (GG §3, §6; TDS) along every frame member that touches the skin: the panel's perimeter members and its intermediate members at 400 mm (D-16, D-34). Bead laid from the supplied triangular nozzle, 10 mm wide × 8 mm high (GG §6, §7), centred on the member line. | source (geometry); layout PROPOSED (B1) |
| Joint thickness and initial hold | Fixing-tape pieces 50 mm long (assumption) laid on the same line as the bead, one at each end of a member and at most every 400 mm between (assumption), with the bead stopped 5 mm short of each piece (GG §7: at least 5 mm from the tape). The bead then covers at least 85% of each member's length (calculation: (400 − 50 − 10) / 400). | PROPOSED (B1); needs Sika's OK, **HOLD-B2** |
| Coverage | Bead section 0.5 × 10 × 8 = 40 mm², so **40 ml per metre** (calculation), which presses to 40 / 3 = 13.3 mm wide at 3 mm (calculation, at least the 12 mm Sika asks). About 79 m of bead on the pod's 10 outer panels (calculation from the panel sizes in the joints register, section 2.8, with intermediate members at 400 mm in one direction), so about 3.2 l and **4.4 kg** (calculation). One 300 ml cartridge lays 7.5 m (calculation). | calculation |
| Against a starved or overfilled joint | One continuous bead per member from the gun in a single pass; on the first panel of each shift, lift one bead before it cures to check it pressed to 12 mm or wider and touched both faces; the tape pieces set the 3 mm. Visual check of every panel per GG Table 4: complete joint filling, joint size, primer present, tape applied and sticking. | source (GG); first-panel check PROPOSED |
| Mixing | None: one part. | source (TDS) |
| Assembly time | The skin goes on **within 15 minutes** of the first bead at 23 °C and 50% r.h. (GG Table 3; skin time 25 min, TDS). Sika's rules: within 75% of the skin time measured in the local climate (TDS) and 5 minutes less than the skin time (GG §6); the shorter governs. The skin time is measured on site at each new batch and whenever the temperature or humidity changes much (GG §9.1, Table 4). The factory climate in Vietnam is hot and humid, which shortens it (GG §6). | source (GG, TDS) |
| Climate | Parts and adhesive between 5 and 40 °C, best 15–25 °C; every part at least 3 °C above the dew point; no lower than 5 °C for 5 hours after bonding; no sun or rain on the parts (GG §4; TDS). | source (GG) |
| Pressure | The frame is lowered onto the skin and pressed until it touches every tape piece (GG §7); no clamps: the tape holds it. | source (GG) |
| Cure and handling | Moisture cure; the speed diagram in the TDS isn't readable as text (**HOLD-B3**). The panel stays flat and unloaded until a bead from the same batch, laid on the same day, passes the peel test at 72 h (GG §9.2: "The adhesion must be built-up after 72 hours curing"). **No standing up, stacking or shipping before 72 h** (assumption from GG §9.2, until HOLD-B3 gives the real time). | source (72 h); handling rule assumption |
| Loads | Section 4. | calculation |
| Compatibility | The bond touches only the ACP back face and the frame face. The PET fill lies against the bead's edges but isn't bonded (silicone: no reaction expected, unverified). **Silicone must not reach the frame's joint faces**: the joint gaskets' pressure-sensitive adhesive won't stick to a silicone film, and the seams would leak. Those faces are masked during pre-treatment and bonding (PROPOSED rule). | PROPOSED rule; fill unverified |
| Low emission | TDS: Indoor Air Comfort GOLD, EMICODE EC1 Plus, French VOC A+, M1, CDPH (LEED v4). This meets REQ-MAT-01 for the adhesive once the certificates are on file. The activator's and primer's emission data aren't in these sources; they flash off before bonding (unverified). | source (TDS); certificates on file to do |
| Repair | Factory only. Cut the skin off with a blade or a cutting wire, remove the adhesive and tape, sand the faces with 80 grit, pre-treat again and re-bond as new (GG §8). | source (GG) |
| Traceability | A daily record per GG §10: adhesive batch and expiry, tape used, pre-treatment and flash-off times, temperature and humidity morning and midday, measured skin time, peel-test result, joint size. Each outer panel's label carries its bond date and batch (REQ-ASM-08). | source (GG); label PROPOSED |
| Pass marks | Section 6. | — |

## 3. Finding B1: the 20 mm tube face

**Why it doesn't fit.** Sika's layout puts the 12 mm tape and the bead side by side on each rail, with the bead "at least 5 mm" from the tape and from the rail's edge (GG §7). The bead goes on from a 10 mm wide nozzle (GG §6). So a rail needs at least 5 + 10 + 5 + 12 = **32 mm** of flat face, with the tape at the far edge (calculation). The decided frame tube is 20 × 40 with the 40 through the wall (skeleton: `outer_t` 43 = ACP 3 + frame 40), so its skin-side face is **20 mm**, about 18 mm flat between its corner radii (assumption: typical radii of a 1.2 mm extrusion).

| Option | What | For | Against | Result |
|---|---|---|---|---|
| (a) | Sika's layout on a wider face: a 40 mm wide member, or a flange added to each member | Exactly Sika's system | Turns the frame 90° (only 20 deep, so the fill and the 81 mm stack change, D-16, D-42) or adds an angle to every member (weight) | Rejected |
| (b) | **One bead centred on every member; 3 mm set by short tape pieces in line with the bead** | Fits the 20 mm face (bead 10 wide with 5 mm each side on a full face; about 4 mm with the corner radii); every member bonded; the skin stays supported at 400 mm (LAY LS-02); no weight added | Departs from "tape along the whole length", which Sika writes for panels hung on a vertical façade; here the panel lies flat on a table, and the tape only sets the thickness and stops the frame sliding | **PROPOSED**, with Sika's OK (HOLD-B2) and the package's T09 coupons |
| (c) | Tape on one member, bead on the next | Each fits alone | Only every second member is bonded (the tape is "not a structural component", TAPE), so the skin spans 800 mm between bond lines: waviness risk (LAY `stud_pitch_acp` 400 for flatness) | Rejected |
| (d) | Structural acrylic foam tape alone, no liquid adhesive | Fits 20 mm; no cure wait | Not in the hardware selection; no data checked here; long-term load data for tapes are much lower than for silicone | Fallback only if Sika says no to (b); needs its own data |

## 4. Design check

Bond area per square metre of skin: one 12 mm joint per member at 400 mm gives 0.012 × 2.5 = **0.030 m² per m²** (calculation; the perimeter members add more, ignored here, which is on the safe side).

| Load | Value | Stress in the bond | Against | Margin | Status |
|---|---|---|---|---|---|
| Skin's own weight, long term, in shear (walls) | 3.5 kg/m² × 9.81 = 34.3 N/m² (SEL A1, kg/m² calculation) | 34.3 / 0.030 = **1.14 kPa** | ETA design shear, about 12 kPa (unverified, HOLD-B1) | about 10 | calculation |
| Skin's own weight on the ceiling | 34.3 N/m² | none in tension: the roof skin sits on top of its frame, so its weight presses the bond | — | — | calculation |
| Shipping bump, 2 g, skin side up (joints register LC4) | 2 × 34.3 = 68.6 N/m² | **2.3 kPa** | 150 kPa (unverified) | about 65 | calculation |
| Someone leaning on the wall (LC2) | pushes the skin onto the frame and fill | compression, no tension | — | — | — |
| Temperature indoors | ±10 K (assumption) | The skin's faces are aluminium like the frame, so the two move almost together; the 450% elongation (TDS) takes any rest | — | — | assumption |
| Carrying a panel by its skin edge (peel) | not allowed | — | — | — | rule for the assembly guide: carry outer panels by the frame (PROPOSED) |

Safety factor: the ETA's design values already carry the assessment's own factors. On top of them this spec asks for at least **3** (assumption, for a new use and a new layout); the smallest margin above is about 10. The tensile strength of 2.1 MPa (TDS) is a material property and isn't used as a design value (guideline §8.2: "Không suy sức bền từ một con số lap-shear catalog", don't infer strength from one catalogue number).

Flatness: the panel is bonded face down on a flat table with the skin's face as **datum A**, and two table stops against two skin edges as datums B and C (joints register section 4). The frame and bond-line tolerances then don't move the outside face; a crisp reveal needs that (D-23).

## 5. Process sheet (factory)

1. Condition the skins, frames, adhesive and tape in the bonding room; record temperature and humidity; check every part is at least 3 °C above the dew point (GG §4).
2. Mask the frame's joint faces (the faces that get gaskets and rivnuts), so no activator, primer or silicone reaches them (section 2, compatibility).
3. Frame faces: mill finish: very fine abrasive pad, then clean; anodised: clean only (GG Table 2). Vacuum the dust; wipe with lint-free paper until it comes away clean (GG §7).
4. Sika Aktivator-205 on the frame faces and on the skin's back face along the member lines; wipe in one direction with fresh paper; flash off at least 10 min (30 min below 15 °C), at most 2 h (GG §5.1).
5. SikaTack Panel Primer, one thin complete coat; flash off 30 min; bond within 2 h (GG §5.2, §7).
6. Skin face down on the flat table, against the B and C stops (datum A is the table).
7. Fixing-tape pieces on the skin's back face along the member lines (section 2); liners left on.
8. The bead along each member line from the 10 × 8 triangular nozzle, stopping 5 mm short of each tape piece; then peel the tape liners.
9. Lower the frame onto the skin by its jig stops, within 15 minutes of the first bead (or the shorter time from the measured skin time); press until it touches every tape piece (GG §7, Table 3).
10. Leave flat and unloaded for 72 h; lay the day's peel-test beads on offcuts of the same skin and tube at the same time (GG §9.2).
11. Check every panel per GG Table 4; run the peel test at 72 h; record everything on the daily sheet (GG §10); label the panel with its bond date and batch.
12. Fill and gaskets go in after the bond has passed (the fill isn't bonded).

## 6. Tests

All PLANNED until done (guideline §10). The sample package's numbers take precedence (joints register R-J12): the bond is tested in **T09** and its mass in **T10**, with T09's PM-ruled pass mark (cohesive failure: the bond breaks inside the adhesive, not at a surface). Specimens use the production skin (back face as delivered), the production tube finish and the production pre-treatment (guideline §8.2: "Làm coupon trên đúng stack và quy trình sản xuất dự kiến", coupons on the real stack and process).

| Test | What | Specimens | Pass mark | When | Status |
|---|---|---|---|---|---|
| QC-1 (process check, not a sample test) | Bead peel adhesion by Sika's method (GG §9.2; CQP033-3), on the skin's back face and on the tube face | 3 beads of 150 mm or more per substrate, cured 3–7 days in the factory climate | At least 95% cohesive failure on each substrate (GG §10 record) | Before the first panel; each new adhesive batch; each new skin or tube lot | PLANNED |
| **T09** (package) | Lap-shear coupons on the skin's back face and the tube's real finish, laid out as section 2 (in-line tape, B1): 5 as cured and 5 after 7 days at 40 °C and 95% r.h. (the package's ageing screen); S1's skin flatness before T01; S1's skin cut off after its other tests to compare the bead coverage with the pattern | as the package gives | **The package's PM-ruled mark:** every coupon fails in the adhesive itself, and S1's bead coverage matches the pattern. The strengths are recorded against the ETA's design values (HOLD-B1), as information, not as a pass mark | Before the wall sample; S1 last | PLANNED |
| **T10** (package) | Bond mass: S1 weighed before and after bonding | S1 | Recorded; this spec's figure is at most about 0.49 kg for a side panel (8.7 m of bead, calculation) | During the build | PLANNED |
| Long-term hold (to route) | Shear coupons held at 10 × the skin's own-weight stress, 11.4 kPa (calculation), for the slow creep the guideline asks about (§8.2) | 3 coupons, 500 h at 23 °C (assumption) | Slip 0.1 mm or less (assumption) | Alongside the wall sample, if the PM adds it to the package | PLANNED, for the PM to route |

## 7. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Releases when |
|---|---|---|---|
| HOLD-B1 | ETA 19/0511 design values and scope | Get the ETA PDF (ITeC or Sika) and confirm the design tensile and long-term shear values, the joint size and whether interior wall cladding is in its scope | ETA on file; section 4 re-checked |
| HOLD-B2 | The in-line tape layout (B1) | To Sika: is SikaTack Panel-50 with Fixing Tape pieces in line with the bead, on a 20 mm aluminium face, bonded flat in a factory, acceptable, and on the ceiling's horizontal panels too, since the data sheet scopes Panel-50 to vertically installed sub-structures? The tape's data sheet asks for "written approval of the corresponding project details by the Technical Department of Sika Industry" | Sika's written answer on file and T09 passed |
| HOLD-B3 | Cure time before handling, standing and shipping | To Sika: cure depth against time at 30 °C and 75% r.h. (the TDS diagram isn't readable as text) | Time set from Sika's data and the daily peel test (QC-1) |
| HOLD-B4 | The skin's back-face coating and the frame's finish (ISS-034; D-131) | To the ACP maker (SEL supplier question 1): what is on the back face of Alcorest 3 mm × 0.21 mm? Then, to Sika: a lab adhesion report for Sikaflex-252 with Aktivator-205 and Primer-210 on that face, on the production tube's Z100 zinc as delivered (passivated or oiled?) and on the 2-component zinc-rich touch-up (section 8) | Coating and finish known; Sika's report on file; pre-treatment confirmed |
| HOLD-B5 | Test results | None: QC-1, T09, T10 and the long-term hold | Results recorded with method, date and role |
| HOLD-B6 | Sikaflex-252 for this bond (D-131, section 8) | To Sika: is Sikaflex-252, on Z100 strip-galvanized steel and on the ACP's back face, with the in-line SikaTack Panel Fixing Tape pieces setting a 3 mm joint, acceptable for a factory-bonded interior wall and ceiling skin; what long-term static stress may it carry; Primer-210's data sheet (flash-off, open time); and its emission certificates for REQ-MAT-01? | Sika's written answer and the certificates on file; T09 passed |

## 8. Steel frames (D-131)

D-131 (PM ruling, 2026-11-01) makes every wall and ceiling frame welded, pre-galvanized steel tube, Z100, with the same outside sections (joints register J-FRAME-01). The Lead's design review asked for a primer or adhesive named for galvanized steel. This section governs the bond on the steel frames; where it is silent, sections 2 to 6 stand.

| Item | Specification | Status |
|---|---|---|
| Why the adhesive changes | Neither SikaTack Panel-50 (TDS) nor SikaTack Panel (STP) lists galvanized steel, nor do Sika's tables for them (GG Tables 1 and 2), and the guideline sends galvanized steel to Sika's own technical information "Sikasil® bonding on metal" (GG §5, reference 3). **Sikaflex-252's** data sheet lists "sheet steel (including phosphated, chromated and galvanized components)", aluminium "(including anodized components)" and "metal primers and paint coatings (2-component systems)" (S252). It is Sika's one-part polyurethane for bonding panels to frames in vehicle building, and Sika Vietnam publishes its data sheet. | source (TDS, STP, GG, S252) |
| Adhesive | **Sikaflex-252**: one-part polyurethane, moisture curing; density 1.2 kg/l; skin time 40 min and open time 35 min at 23 °C and 50% r.h.; Shore A 50; tensile strength 3 MPa; elongation at break 400%; tear 7 N/mm; tensile lap-shear strength 2.5 MPa (ISO 4587); service −40 to 90 °C (S252). "Test with actual substrates and conditions have to be performed to ensure adhesion and material compatibility" (S252): T09 and HOLD-B6. | source (S252); use PROPOSED (D-131, the Lead's review) |
| Joint and spacer | As section 2: one joint at least 12 wide × 3 thick along every member that touches the skin, the 3 mm set by SikaTack Panel Fixing Tape pieces in line with the bead (finding B1). The tape is only a spacer and first hold; its use with Sikaflex-252 is part of HOLD-B6. | PROPOSED; HOLD-B6 |
| Pre-treatment, frame | Abrasive pad very fine, then clean (Sika Cleaner P), **Sika Aktivator-205**, then **Sika Primer-210**, one thin complete coat: SPC's route for hot-dip and electrogalvanized steel at level 2 (interior and exterior bonding under normal conditions). Where a bead crosses a ground and touched-up weld (a T joint on a rail), the touch-up is a **2-component zinc-rich epoxy** (J-FRAME-01), a substrate S252 lists; its pre-treatment is SPC's row for 2-component paint primers, and Sika's report confirms it (HOLD-B4). | source (SPC, S252); Sika's report HOLD-B4 |
| Pre-treatment, ACP back face | SPC's aluminium route at level 2: abrasive pad very fine and clean, Sika Aktivator-205, Sika Primer-210. If the back face is coated (HOLD-B4), SPC's coating rows or Sika's lab test decide. | source (SPC); HOLD-B4 |
| Times | Aktivator-205: at least 10 min, at most 2 h before the primer (GG §5.1); primer flash-off and its window from Primer-210's data sheet (HOLD-B6; at least 10 min at 23 °C as GG §5.2 gives for it); the skin goes on within the open time, 35 min at 23 °C and 50% r.h. (S252), less in the factory's heat and humidity, so the skin time is measured each shift (GG §9.1). | source (GG, S252); Primer-210's sheet HOLD-B6 |
| Frame flatness | Skin-side faces within ±0.5 of one plane, the frame lying free; seam faces flat within 0.5 (J-FRAME-01); checked before bonding. The frame is lowered onto the tape pieces and pressed only until it touches every one (GG §7), never clamped flat. | PROPOSED |
| What pressing a bowed frame does | Steel is about three times as stiff as the aluminium was, so a frame pressed onto its tape pieces pushes back. At the ±0.5 limit, L2's two long members (E I about 1.3 × 10¹⁰ N·mm²) need about 300 N to come 1.0 mm flat (calculation: 384 E I δ / 5 L³ over 1495), about 8 kPa on their two bond lines (2 × 1495 × 12 mm). That is a fixed displacement, not a load: the cured adhesive relaxes it rather than creeping under it. While the adhesive cures, the tape pieces hold it, about 30 kPa on their area (calculation, a piece every 400 or less). T09's S1 check records the frame's flatness before bonding and checks after 72 h that no tape piece has let go. | calculation; assumption (relaxation) |
| Design check | The skin's weight on the bond's area, which D-135's members (275 clear or less) raise to about 0.040 m² per m² or more, is about **0.9 kPa** in shear or less; a 2 g bump about **1.7 kPa**; a ±0.5 frame's push at most about **8 kPa**, falling (calculation). Sikaflex-252 has no façade approval with design values (the ETA was Panel-50's), so against its 2.5 MPa lap shear (S252) these are at most about 0.4%: on top of the spec's own factor of 3, a static design value from Sika (HOLD-B6) and the long-term hold coupons (section 6) decide. | calculation; HOLD-B6 |
| Temperature | The skin's aluminium faces (about 23 × 10⁻⁶ /K, assumption) now sit on steel (12 × 10⁻⁶ /K, source EN 1993-1-1). Over half an L1 panel's diagonal (941 mm), ±10 K indoors moves the skin about 0.10 mm against the frame, 3% shear in the 3 mm joint; −10 to 60 °C in storage or shipping against a 25 °C bond (assumption) about 0.40 mm, 13%. Small next to the adhesive's 400% elongation; T09's aged coupons cover the rest. | calculation; assumption |
| Coverage and mass | D-135's added studs (2 more in each side panel, 1 more in each back panel) add about 12.9 m of bead to the pod's 79 m (calculation). At 40 ml/m (section 2) and 1.2 kg/l (S252): 91.9 m, about 3.7 l and **4.4 kg** a pod (calculation), the same as with Panel-50 before the studs. The register's bond-set count follows when WALL's sample is weighed (D-131's mass cap is provisional until then). | calculation |
| Process sheet | As section 5, with steps 3 to 5 as above (pad, clean, Aktivator-205, Primer-210 on both faces) and the open time from S252; the frame's flatness is recorded before step 9. | PROPOSED |
| Tests | **T09** (package): lap-shear coupons on the production galvanized tube and the ACP's back face with this route, half of them across a T joint's ground and touched-up weld; 5 as cured and 5 aged. **QC-1**: peel beads on the galvanized tube, on the touch-up and on the ACP. The long-term hold coupons (section 6) with Sikaflex-252. | PLANNED |
