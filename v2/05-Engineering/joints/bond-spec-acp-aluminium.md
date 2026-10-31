# Bond specification: ACP skin to aluminium frame (factory bond)

| Doc code | Revision | Status | Date | Owner |
|---|---|---|---|---|
| V2-ENG-JNT-02 (PROPOSED code; the control pack adds the register row) | P01 | DRAFT | 2026-10-31 | Joints Engineer (v2 Milestone 2) |

This is the bond specification the guideline asks for (§8.2, and Milestone 2 item 6), for the one structural bond in the decided build: the 3 mm ACP skin to the 20 × 40 × 1.2 aluminium frame of every wall and ceiling outer panel (ISS-016). With no plywood behind the ACP (D-17), this bond is what holds the skin on. It is made in the factory only; nothing is glued on site (REQ-ASM-05).

Not covered: the felt on the lining cassette's steel tray (LINING, ISS-015), the gasket and seal tapes (pressure-sensitive, in the joints register), and sealants.

Status words as in the joints register: numbers carry confirmed, source, calculation, assumption or unverified (conventions §9); choices are PROPOSED unless a D-number or a PM ruling is cited. No supplier was contacted.

## Result

1. **Bond system: SikaTack Panel-50**, a one-part, moisture-curing silicone with an ETA for wall cladding (ETA 19/0511), **with SikaTack Panel Fixing Tape** (3 × 12 mm polyethylene foam) to set the joint at 3 mm and hold the skin while it cures. Both faces are pre-treated with **Sika Aktivator-205 and SikaTack Panel Primer**, after a very fine abrasive pad on mill-finish aluminium (Sika's general table). Joint: **12 × 3 mm**, one on every frame member that touches the skin. This is the hardware selection's pick (A9); status source.
2. **B1. The 20 mm tube face is too narrow for Sika's layout.** Sika puts the tape and the bead side by side, with the bead at least 5 mm from the tape and from the rail's edge. That needs about 32 mm of flat face (calculation); the frame's skin-side face is 20 mm wide. **Proposed:** one bead centred on every member, with the 3 mm thickness set by short pieces of the same fixing tape **in line** with the bead, and the panel bonded face down on a flat table. That departs from Sika's "tape along the whole length", so it needs Sika's written OK (HOLD-B2), and the coupons (section 6) test it.
3. **Design check:** the skin's own weight puts about **1.1 kPa** of shear on the bond, and a 2 g bump in shipping about **2.3 kPa** of tension (calculation). Against the ETA's design values, about 12 kPa in long-term shear and 150 kPa in tension (unverified: read from a search engine's extract of the ETA; the PDF itself wouldn't download, HOLD-B1), that's at least 10 times inside them, on top of the ETA's own safety factors. The bond's real strength is shown by coupons on the real skin, frame finish and process (section 6), not by a catalogue figure (guideline §8.2).
4. **Mass: about 4.4 kg for the pod** (calculation: about 79 m of bead at 40 ml/m and 1.4 kg/l), 0.28 kg/m² against the 0.25 kg/m² the layout study assumed: **+0.5 kg** over its estimate.
5. **HOLDs: 5** (section 7): the ETA text, Sika's OK for the in-line tape, the cure time before handling, the ACP's back-face coating and the frame's finish, and the coupon results.

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
| (b) | **One bead centred on every member; 3 mm set by short tape pieces in line with the bead** | Fits the 20 mm face (bead 10 wide with 5 mm each side on a full face; about 4 mm with the corner radii); every member bonded; the skin stays supported at 400 mm (LAY LS-02); no weight added | Departs from "tape along the whole length", which Sika writes for panels hung on a vertical façade; here the panel lies flat on a table, and the tape only sets the thickness and stops the frame sliding | **PROPOSED**, with Sika's OK (HOLD-B2) and coupons C-1 to C-4 |
| (c) | Tape on one member, bead on the next | Each fits alone | Only every second member is bonded (the tape is "not a structural component", TAPE), so the skin spans 800 mm between bond lines: waviness risk (LAY `stud_pitch_acp` 400 for flatness) | Rejected |
| (d) | Structural acrylic foam tape alone, no liquid adhesive | Fits 20 mm; no cure wait | Not in the hardware selection; no data checked here; long-term load data for tapes are much lower than for silicone | Fallback only if Sika says no to (b); needs its own data |

## 4. Design check

Bond area per square metre of skin: one 12 mm joint per member at 400 mm gives 0.012 × 2.5 = **0.030 m² per m²** (calculation; the perimeter members add more, ignored here, which is on the safe side).

| Load | Value | Stress in the bond | Against | Margin | Status |
|---|---|---|---|---|---|
| Skin's own weight, long term, in shear (walls) | 3.5 kg/m² × 9.81 = 34.3 N/m² (SEL A1, kg/m² calculation) | 34.3 / 0.030 = **1.14 kPa** | ETA design shear, about 12 kPa (unverified, HOLD-B1) | about 10 | calculation |
| Skin's own weight on the ceiling, hanging in tension | 34.3 N/m² | **1.14 kPa** | ETA design tensile, about 150 kPa (unverified) | over 100 | calculation |
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

## 6. Coupon and sample tests

All PLANNED until done (guideline §10). Specimens use the production skin (back face as delivered), the production tube finish and the production pre-treatment (guideline §8.2: "Làm coupon trên đúng stack và quy trình sản xuất dự kiến", coupons on the real stack and process).

| Test | What | Specimens | Pass mark | When | Status |
|---|---|---|---|---|---|
| C-1 | Bead peel adhesion by Sika's method (GG §9.2; CQP033-3), on the skin's back face and on the tube face | 3 beads of 150 mm or more per substrate, cured 3–7 days in the factory climate | At least 95% cohesive failure on each substrate (GG §10 record) | Before the first panel; each new adhesive batch; each new skin or tube lot | PLANNED |
| C-2 | Tension and shear coupons: a 12 × 3 × 50 mm joint between a skin strip and a tube offcut, made by the in-line-tape layout (B1) | 5 in tension and 5 in shear at 23 °C after 7 days; the same again after 7 days at 70 °C (assumption: indoor heat ageing) | Mean at least 6 × the ETA design value (assumption, pending HOLD-B1), no result below 4 ×, and at least 95% cohesive failure | Before the wall sample | PLANNED |
| C-3 | Long-term load: shear coupons held at 10 × the skin's own-weight stress, 11.4 kPa (calculation) | 3 coupons, 500 h at 23 °C (assumption) | Slip 0.1 mm or less (assumption) | Alongside the wall sample | PLANNED |
| C-4 | A whole outer panel bonded by the process sheet | 1 side panel, then it goes into the wall sample | Face flat within ±0.3 mm per metre (assumption); every bead 12 mm or wider where seen; tap test finds no unbonded length; bond mass weighed (section 2: at most about 0.49 kg for a side panel, 8.7 m of bead, calculation) | Wall sample | PLANNED |
| C-5 | Cut-out after the wall sample's sound test | 300 mm of one bead | At least 95% cohesive failure | After the sound test | PLANNED |

## 7. HOLD list

| HOLD | What | Question (for the PM to send; we don't contact suppliers) | Releases when |
|---|---|---|---|
| HOLD-B1 | ETA 19/0511 design values and scope | Get the ETA PDF (ITeC or Sika) and confirm the design tensile and long-term shear values, the joint size and whether interior wall cladding is in its scope | ETA on file; section 4 re-checked |
| HOLD-B2 | The in-line tape layout (B1) | To Sika: is SikaTack Panel-50 with Fixing Tape pieces in line with the bead, on a 20 mm aluminium face, bonded flat in a factory, acceptable? The tape's data sheet asks for "written approval of the corresponding project details by the Technical Department of Sika Industry" | Sika's written answer on file and C-2 passed |
| HOLD-B3 | Cure time before handling, standing and shipping | To Sika: cure depth against time at 30 °C and 75% r.h. (the TDS diagram isn't readable as text) | Time set from Sika's data and C-1 |
| HOLD-B4 | The skin's back-face coating and the frame's finish (ISS-034) | To the ACP maker (SEL supplier question 1): what is on the back face of Alcorest 3 mm × 0.21 mm? Then Sika's lab test on that face and on the chosen frame finish if either isn't in Sika's table | Coating and finish known; pre-treatment confirmed |
| HOLD-B5 | Coupon results | None: tests C-1 to C-5 | Results recorded with method, date and role |
