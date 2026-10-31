# Spaceship bought parts and hardware selection

Spaceship is the working name for FocusPod v2 ("Indoor Pod"). This is the parts table that the guideline (§4.3) asks for before CAD. Each row gives a real part number, the page it came from, its interface data, Vietnam availability, open questions and status. Lightest options come first, with at least two options where they exist.

- **Checked:** every link on 2026-10-31. Public pages only. No supplier was contacted, nothing was ordered, and no prices were collected.
- **Number status:** source (read on the maker's or a distributor's page), calculation (our arithmetic, method shown), assumption, or unverified (not on any page opened).
- **Decision status:** DECIDED (the PM ruled on it, 2026-10-31; D-xx = entry in `v2/00-Control/decision-log.md`, other rulings are from the project chat), PROPOSED (still needs a call), HOLD (a supplier or a sample must confirm it before CAD uses the geometry).
- **Related:** the sound and air numbers are in [`../acoustics-air/report.md`](../acoustics-air/report.md) and [`calc.py`](../acoustics-air/calc.py). Plan codes VT01–VT12 come from `v2/00-Control/v2-build-plan.pdf`.

## Summary

| Function | Pick | Status |
|---|---|---|
| Lights | Häfele Loox5 12 V: 6 × LED 2094 downlights (CRI > 90) + 2 m LED 2162 strip (CRI 92) as the soft front light, all on the 12 V bus (D-10) | source; VN stock unverified |
| Outer skin (VT01) | Alcorest ACP 3 mm EV3038 Dark Yellow, 0.21 mm skins, PE core | source; kg/m² calculation; DECIDED: no plywood (VT02 dropped) |
| Wall and ceiling frame (VT10) | Aluminium 20 × 40 × 1.2, members at 400 mm, 40 mm deep for walls and ceiling | DECIDED (1.2 mm wall after the rivnut grip check passed) |
| Cavity fill | Pyrotek Sorberpoly 2D polyester, 32 kg/m³, 40 mm | DECIDED; the 24 kg/m³ grade has no published absorption, so it isn't used |
| Inner leaf | Floating lining cassette: 0.5 mm galvanised steel tray, 25 mm deep, with 9 mm felt across its face | DECIDED; 0.4 mm rejected because it costs 1 dB |
| Felt (VT03) | The factory's 9 mm PET felt, tested in the wall sample first; buy Autex Cube 12 mm only if it falls short. Absorption in the calc: Polyx Board 9 published data (same 9 mm and 1.8 kg/m²) | DECIDED (test-first); **emission certificate HOLD** (Target 6, Reviewer 3 P3-8) |
| Front | 4+4 laminated glass of **toughened, heat-soaked panes** (8.76 mm), grey, frameless like v1 (PM ruling 3). Product HOLD: none of the cited acoustic laminates is shown offered with toughened panes, so the supplier names one | DECIDED build; product HOLD; smoked acrylic 10 mm only as an optional experiment on the factory sample (C9) |
| Door hinges and lock | HOLD (PM ruling 3): the glass is 4+4 laminate of toughened, heat-soaked panes (8.76 mm), the door 47.5 kg and 1176 mm wide. dormakaba lists OFFICE 11.233 for toughened glass 8/10 only and offers laminated glass only with its MUNDUS patch fittings; the STUDIO lock 10.200 is for doors up to 1000 mm. Frameless look kept, hinges in the left decor block. Supplier questions below | HOLD until a rated set is named |
| Door seals | Frame stop seal athmer PS 1515 P Flex, drop seal athmer Schall-Ex GSA (rated for VSG 8.76) cut to 1176 mm, 180° glass-to-glass seal on the fixed pane | source |
| Fans (VT06) | 12 V: four Noctua NF-A14 industrialPPC-3000 PWM, two per path: the supply pair in a lined box high in the right decor block, the exhaust pair lying flat in the soffit's right end (D-60). On the 12 V bus, so mains feeds the outlets only. The 5c1003b S&P TD-500 (ØD 221) and TD-350 (ØD 204) don't fit | DECIDED (12 V under ruling 1; placement D-60): 25.1 dB(A) at 53 l/s against the 26 target, 29.6 at the 65 l/s boost (66 l/s at 30 dB(A)); fan-sample test HOLD |
| Silencers | D-60: one splitter cartridge size for both paths, 173 × 314 × 1750 mm, 11.2 kg: two 80 mm passages between three 50 mm Pyrotek Sorberpoly 2D layers in a 2 mm aluminium casing. The supply's stands in a 220 × 360 mm felt-covered air column in the front-right inside corner, with a kick grille at its foot; the exhaust's lies in a 360 × 220 mm felt-covered soffit above the door head. 30 mm polyester fill behind each felt-covered face. A 1 mm steel riser brings the room air up the right block from the intake in its underside; the exhaust leaves through a roof slot | DECIDED (D-60 and the PM's sizing ruling); the 50 mm layer data is published, so nothing is interpolated; CAD by the CEILING Engineer (FRONT: the intake opening) |
| Fan control | In-house Desk Pro AI sensor hub, on the air column's front face at seated eye height, reads and shows CO2 and temperature and drives both 12 V fan pairs with one shared signal (D-09): CO2 leads with a 26 l/s floor for one person (D-44), heat keeps the inside within 4 K, 53 l/s for two at 25.1 dB(A), boost up to 66 l/s inside 30 dB(A), run-on after presence | DECIDED control logic; PWM interface of the hub HOLD (electrical scope) |
| Power inlet | Neutrik powerCON TRUE1 TOP NAC3MPX-TOP + etherCON NE8FDP | source |
| Thread in thin tube (VT11) | M6 rivet nut in the aluminium members: Sherex CAH3-610-4.2 (aluminium 5056, grip 0.70–4.20 mm, so it covers the 1.2 mm wall); M6 ISO 4017 8.8 bolts | source; grip check passed; spin-out and bulge clearance HOLD for a sample in the tube |

## A. Plan materials (VT01–VT12)

### A1. VT01 Aluminium composite panel 3 mm, EV3038 Dark Yellow (tấm ốp alu)

| Opt | Maker · product · variant | Key data | kg/m² | VN | Source (checked 2026-10-31) | Status | Open questions |
|---|---|---|---:|---|---|---|---|
| 1 (pick) | Nhôm Việt Dũng · **Alcorest outdoor ACP**, colour **EV3038 "Vàng đậm"**, 3 mm × 0.21 mm skins | Sheet 3–6 mm, skins 0.21–0.50 mm, widths 1220 / 1500, lengths 2440 / 3000; PVDF/FEVE paint; alloys 1050–3003; for 3.0 × 0.21: bending strength ≥ 45 MPa, modulus ≥ 13 GPa, peel ≥ 4.0 N/mm. Core: plastic (PE-type). Fire class of 3 mm PE: not published | 3.5 | VN maker and distributors | https://vietdung.com.vn/tam-op-nhom-nhua/tam-op-ngoai-troi-alcorest.html ; catalogue https://vietdung.com.vn/wp-content/uploads/2026/07/CTL-ACP-ALCOREST-07.08.25.pdf ; distributor https://tongkhoalu.com/cua-hang/alcorest-vang-dam-ma-mau-ev3038-alu-ngoai-troi | source; kg/m² calculation (skins 1.14 + PE core 2.3–2.4) | Real kg/m²; core type (recycled PE, HDPE or LDPE); V-groove rest thickness for folding 3 mm |
| 2 | Same, **Alcorest FR** (fire-retardant core), EV3038 | Only 4–5 mm, skins 0.3–0.5 mm; "B1 (DIN 4102-1)"; QCVN 06:2022 classes LT1/BC1/SK1/ĐT1 | 5.5–7 (distributor claim) | VN maker | https://vietdung.com.vn/tam-op-loi-chong-chay/tam-op-loi-chong-chay-cao-cap-alcorest-fr.html | source; kg/m² unverified | Needed only if later fire rules require FR; adds about 30 kg |
| 3 | 3A Composites **ALUCOBOND PLUS** 3 mm | 0.5 mm skins, mineral-filled core, EN 13501-1 B-s1,d0; V-groove folding rules published | 5.9 | unverified in VN | https://alucobond.com.sg/products/alucobond-plus/technical-data-plus | source | Colour match to EV3038 |

Reason: option 1 is the plan's material, made in Vietnam, and the lightest. Thicker FR panels add about 2 kg/m² over 17 m² of skin.

### A2. VT02 Plywood 6 mm (ván plywood): DECIDED dropped

The PM ruled "no plywood behind the ACP" on 2026-10-31. For reference: HCPLY 6 mm commercial plywood is 2.99 / 3.49 / 3.90 kg/m² (styrax / acacia / eucalyptus core; calculation from https://vietnam-plywood.com/plywood-weight-table-all-core-types-thickness/), with emissions "E0 or E1 per buyer" and "CARB P2" self-declared without certificate numbers (https://vietnam-plywood.com/vietnam-plywood-technical-datasheet-sample-standards/). An Cường has no 6 mm sheet. If a board comes back, ask for a CARB P2 / TSCA Title VI certificate number.

### A3. VT03 PET felt 9 mm, Dark Gray (tấm tiêu âm polyester)

| Opt | Maker · product | Key data | kg/m² | VN | Source | Status | Open questions |
|---|---|---|---:|---|---|---|---|
| 1 (plan) | Nội Thất DHG · "Tấm Polyester Fiber" 9 mm | 1220 × 2420 × 9; density stated "20–30 kg/m³" (that's loose-wool data, not a 9 mm panel); absorption "< 0.94" with no standard; "chống cháy hạng B" with no standard; no certificate | unverified | VN distributor | https://noithatdhg.com/products/tam-polyester-fiber | source, but the data can't be used | Real kg/m², ISO 354 report, fire test, emission certificate, real maker |
| 2 | Polyx Board 9 (9 mm PET board) | 1800 g/m² | 1.8 | unverified in VN | https://aid.co/wp-content/uploads/2024/10/Polyx-Board-9-No-Insulation-No-Air-Gap.pdf (via the layout study, S11) | source | Absorption per octave; emissions |
| 3 (reference data) | Autex **Cube 12 mm** | ISO 354: direct 0.05/0.10/0.30/0.65/0.90/0.95 (NRC 0.45); with 25 mm gap 0.05/0.30/0.60/0.95/0.95/0.85 (NRC 0.70); EN 13501-1 B-s1,d0; CDPH-compliant, Declare Red List free, HPD, EPD; 1220 × 2440 | not stated on the cited sheet | unverified in VN | https://cdn.mediavalet.com/aunsw/autex/v7u3NcemSkmPcPN5VuEQ9Q/cXKq4VBRsEGhTdPqme4gJA/Original/Cube%20Datasheet.pdf | source | 9 mm or custom thickness; VN reseller |
| 4 | EASYfelt PET felt Panel 9 mm | 120 × 60 / 120 / 240 cm; B-s1,d0; absorption shown only as a graph | unverified | unverified in VN | https://easy-noise-control.files.prepr.io/64s9qhr374wk-easyfelt-product-sheet-panel-9mm.pdf | source (numbers unverified) | Octave numbers; emissions |

DECIDED (PM, 2026-10-31): test the factory's 9 mm PET felt in the wall sample first, and buy Autex Cube only if it falls short. The calc uses Autex Cube 12 mm data as a proxy, which is slightly optimistic for 9 mm. Still ask the factory for the felt's emission certificate.

### A4. Tube: VT10 20 × 20, VT04 30 × 60, VT03 50 × 100 (thép hộp), and the DECIDED aluminium

| Size | Steel, Hòa Phát (kg/m by wall) | Aluminium (kg/m) | Source | Status |
|---|---|---|---|---|
| 20 × 20 | t1.0 0.59 · t1.2 0.70 · t1.4 0.81 · t1.5 0.86 · t1.8 1.01 · t2.0 1.10 | 6060 T66: t1.5 0.30 · t2 0.39 | Hòa Phát catalogue 2025 p. 21 (link dead on 2026-10-31, so these figures are unverified until the catalogue is found again) https://file.hoaphat.com.vn/ongthep/2026/03/catalogue-ong-thep-2025-in-170326.pdf ; Voss https://www.voss-edelstahl.com/online/en/Aluminium/profiles-tubes/Squares/ | source (steel kg/pc ÷ 6 m = calculation) |
| 20 × 40 × 1.2 (DECIDED wall and ceiling frame) | — | t1.2 0.37 (t1.5 0.46) | calculation: (2 × (20 + 40) − 4 × 1.2) × 1.2 × 2.70 g/cm³ | calculation |
| 20 × 100 (ceiling option, not used) | — | t1.5 0.95 | calculation | calculation |
| 30 × 60 | t1.2 1.64 · t1.4 1.91 · t1.5 2.04 · t2.0 2.68 · t3.0 3.90 | 60 × 30 × 2: 0.93 | as above; Voss rectangular https://www.voss-edelstahl.com/online/en/Aluminium/profiles-tubes/Rectangular/3/?lang=1 | source |
| 50 × 100 | t1.5 3.45 · t2.0 4.56 · t3.0 6.73 · t4.0 8.82 | 100 × 50 × 2: 1.57; × 3: 2.33 | as above | source |

The plan's raised steel floor (VT03/VT04) goes with the thin floor (DECIDED, D-05; the layout study owns it). Open question: a Vietnamese extruder table for 6063-T5 tubes with 1.5 mm walls. The aluminium data above is 6060 from a German stockist.

### A5. VT11 M6 × 60 bolts and what they thread into (bulong M6, tán rive)

| Opt | Maker · part number | Key data | Fits | VN | Source | Status | Open questions |
|---|---|---|---|---|---|---|---|
| 1 (pick for aluminium frames) | Sherex by PEM **CAH3-610-4.2**, aluminium 5056, half-hex, large flange, thin-wall series | M6 × 1.0; grip 0.70–4.20; hole 9.53 (+0.10); length 14.86; head Ø12.96 | 1.5 mm aluminium tube wall; no steel–aluminium contact | unverified in VN | https://fasteners.sherex.com/item/nd-rivet-nuts-american-style-rivet-nuts-cah-series/cah-series-aluminum-metric-/cah3-610-4-2-1 | source | Torque limit with an 8.8 bolt; does the bulge clear the 17 mm inside of a 20 mm tube |
| 2 | Avdel **Hexsert 09498-72620**, steel, hex body | M6; grip 0.50–3.00; hex hole 9.00–9.10 A/F; torque-to-turn ≥ 11.9 N·m; pull-out 14.4 kN | steel or aluminium wall (galvanic pairing to check) | SG distributor | https://www.gripwell.com.sg/image/catalog/Gripwell/Fastening%20Solutions/Threaded%20Inserts/Steel%20Threaded%20Inserts/9498%20Hexsert/Gripwell%20-%209498%20Hexsert.pdf | source | Can a hex hole be punched in a tube face |
| 3 | Avdel **FS58 Nutsert 0FS58-70628**, steel, round | M6; grip 0.50–3.00; hole 9.10; max torque 12.4 N·m; pull-out 10.8 kN | thin wall | SG distributor | https://www.gripwell.com.sg/image/catalog/Gripwell/Fastening%20Solutions/Threaded%20Inserts/Steel%20Threaded%20Inserts/FS58%20Thin%20Sheet%20Nutsert/Gripwell%20-%20FS58%20Thin%20Sheet%20Nutsert.pdf | source | Spin-out in a round hole |
| 4 | Sherex **CLM2-610-3.0**, steel, knurled | M6; grip 0.50–3.00; hole 9.00 | thin steel wall | unverified in VN | https://fasteners.sherex.com/viewitems/nd-rivet-nuts-european-style-rivet-nuts-clm-series/clm-series-steel?plpver=30 | source | — |
| Bolt | **M6 ISO 4017 class 8.8, zinc** (example: Ahlsell 300237, M6 × 60) | full thread; head 4.0 mm; 10 mm A/F | — | standard part | https://www.ahlsell.se/en/products/mounting/machine-threaded-screw/hexagon-bolt-zpl/300237/ | source | Length per joint is set by the joint register: through one 40 mm member into a rivnut needs about M6 × 50 |

Rule: one bolt size, M6, throughout (DECIDED in the plan). **Tightening torque: HOLD until a spin-out test in the real 20 × 40 × 1.2 tube (PM ruling 6; listed under Sample tests).** The 12 N·m quoted before is the steel Avdel part's maximum; Reviewer 3 found that the FS58 starts to spin at 3.4 N·m, and the aluminium pick has no published torque (guideline §8.1). HOLD also: the sample must confirm the formed bulge clears the inside.

### A6. VT12 M10 leveling feet (chân tăng chỉnh)

| Opt | Maker · part | Load rating | Size | VN | Source | Status |
|---|---|---|---|---|---|---|
| 1 | Elesa **LV.A-60-14-AS-M10x43** (code 307221), PA base, NBR anti-slip disk | max limit static load 14 000 N (apply a safety factor) | D60, M10, thread 43 | unverified in VN | https://www.elesa.com/siteassets/PDF/PDF_US/LV.A.pdf | source |
| 2 | MiniTec **21.1892/0** foot M10 D80 | "Load capacity max. 1000 kg"; 15° angle compensation | D80, L 82.5 | unverified in VN | https://docs.rs-online.com/0dcc/A700000015733439.pdf | source |
| plan | lkcg.vn "Chân đế cao su chống trơn trượt công nghiệp D50" (PVN4806) | no load rating published; out of stock | D50 | VN shop | https://lkcg.vn/chan-de-cao-su-chong-tron-truot-cong-nghiep-d50 | source (no rating) |

With the thin floor, the base band's levelling glides (layout study) replace these feet.

### A7. V brackets (pát V = L-angle bracket)

| Opt | Maker · part | Data | Source | Status |
|---|---|---|---|---|
| 1 | Simpson Strong-Tie **ABR7015** | 70 × 70 × 55, t 1.5, galvanised S250GD+Z275; holes 8 × Ø5 + 1 × Ø7 + 1 × Ø9 (corrected: Reviewer 3 found the second bolt hole is Ø9) | https://www.sitebox.ltd.uk/docs/sst/SST_ABR.pdf | source |
| 2 | Simpson Strong-Tie **A33** | 75 × 75 × 38, t 2.5, pre-galvanised; 4 × Ø4.0 per flange | https://www.sitebox.ltd.uk/docs/sst/SST_A.pdf | source |

Use ABR7015 with M6 through the Ø7 hole so the one-bolt rule holds. VN stock is unverified.

### A8. Cassette clips (kẹp treo cassette), hook-and-loop only to line up

PM ruling 4: every lining cassette hangs on captive mechanical clips with a rated load, and every ceiling cassette also gets a safety catch. Hook-and-loop stays only to locate a cassette, never to hold it (guideline §8.2 forbids tape-only retention on a ceiling; Velcro PS14 has no load rating, and 3M suggests about 57 cm² of Dual Lock per kg).

Load each clip must carry (calculation, safety factor 3 as an assumption until the guideline's factor is applied):

| Cassette | kg | Clips | Load per clip | Rated load needed per clip |
|---|---:|---:|---:|---:|
| Wall cassette, 1500 × 1145 | 10.3 | 4, hooked in (shear) | 2.6 kg | 7.7 kg in shear |
| Ceiling cassette with its fill | about 16 | 6, captive (pull-out) | 2.7 kg | 8.0 kg in pull-out |
| Ceiling safety catch | about 16 | 2 steel lanyards | 8 kg each if all clips let go | 48 kg each (3 × the whole cassette) |

| Opt | Maker · part | Data | Source | Status |
|---|---|---|---|---|
| 1 (candidate) | Häfele **KEKU EH** suspension fitting, hook-in, polycarbonate | 20 kg vertical, 8 kg horizontal; at least 4 pairs per rectangular panel; per fitting or per pair not stated; made for wood panels in the System 32 grid | distributor page https://www.ostermann.eu/en_GB/product/suspension-fitting-keku-eh-s-area-component | source (distributor, not Häfele); rating basis, pull-out rating, captive lock and fixing to a 0.5 mm steel tray HOLD |
| safety catch | steel wire lanyard with a rated working load, cassette return to the 20 × 100 ceiling member | no product picked yet | none | HOLD: part number and rating; the Layout Engineer's clip study asks for the same |
| locate only | VELCRO® Brand **PS14 hook** 25 mm, or 3M **Dual Lock SJ3560** | no load rating (PS14); about 57 cm² per kg static (3M guidance) | https://www.silmid.com/es/tapes/velcro-brand-tapes/Velcro-Brand-Tapes-Hook-Self-Adhesive-Tape-Black-25mm/ ; https://silmid.com/fr/tapes/velcro-brand-tapes/3m-dual-lock-sj3560-clear-reclosable-fastener-25mm/ | source; locating only |

HOLD: pull test of the picked clip on a real cassette return, and a drop test of the safety catch (Sample tests).

### A9. Adhesive, ACP to frame (keo dán), factory only

With plywood dropped, the bond is ACP to aluminium.

| Opt | Product | Data | Low-emission label | Source | Status |
|---|---|---|---|---|---|
| 1 (pick) | Sika **SikaTack® Panel-50** with SikaTack Panel Fixing Tape | substrates "anodized and coated aluminum, glass, metal composite …"; for ventilated facades and clad interior walls; tensile 2.1 MPa | Indoor Air Comfort GOLD, EMICODE EC1 Plus, French A+, M1, LEED v4 (CDPH) | https://dnk.sika.com/dam/dms/dk01/7/sikatack_panel-50.pdf | source |
| 2 | Bostik **P95 Turbo-Fix** (MS polymer) | wood, metal, aluminium; tensile > 1.6 N/mm² | EMICODE EC1+ | https://source.thenbs.com/en/gb/product/bostik-p95-turbo-fix/vtjCxpnJQTJvXwpTsgcxxL/BaFc1q7woU8FvbJzmGxko | source |
| no | Sika Sikaflex-118 Extreme Grab | "Do not use for structural bonding"; not for full-surface use | EC1 PLUS | https://aus.sika.com/dam/dms/au01/6/sikaflex_-118_extremegrab.pdf | source |

HOLD: coupon test on PVDF-coated Alcorest against the chosen aluminium finish, plus the bead pattern.

## B. Light options that Spaceship leans on

| Function | Opt | Maker · product | Key data | kg/m² | Source | Status |
|---|---|---|---|---:|---|---|
| Sandwich panel, honeycomb (not chosen: R speech 10–13, coincidence in the speech band) | 1 | CEL **Compocel AL** | 0.5 + 0.5 skins: 10 mm 4.0, 15 mm 4.3; 1250 × 2500 | 4.0–4.3 | https://www.chemical-concepts.com/wp-content/uploads/2023/09/Compocel-AL-TDS.pdf | source |
| | 2 | 3A **ALUCORE** | 10 mm 5.0, 15 mm 6.7, 20 mm 7.0; B-s1,d0 | 5.0–7.0 | https://alucobond.com/products/alucore | source (page conflicts) |
| Sandwich panel, foam core (not chosen: behaves like plain mass) | 1 | CEL **Compocel ALF** (PET foam core) | 1 + 1 skins, PET 80: 10 mm 6.8, 15 mm 7.2, 20 mm 7.6 | 6.8–7.6 | https://www.celcomponents.com/img_ins/files/Compocel_Alf_uk_Rev7.pdf | source |
| Cavity fill and silencer lining (bông PET) | 1 (DECIDED) | Pyrotek **Sorberpoly 2D** polyester, 32 kg/m³ | densities 18, 24, 32, 48, 60 kg/m³ (commonly sold as 32/48/60); 25 and 50 mm standard, custom thicknesses available. ISO 354 (University of Canterbury, reports 323 and 324), 32 kg/m³: 25 mm 0.08/0.27/0.48/0.63/0.71/0.75 (NRC 0.50), 50 mm 0.16/0.47/0.82/0.90/0.84/0.83 (NRC 0.75); UL94 HF-1 | 1.3 at 40 mm (calculation) | https://www.pyroteknc.com/dmsdocument/58/SORBERPOLY-2D-TDS-215IP.pdf | source; "Acoustic results are based on 32 kg/m3 density material", so 24 kg/m³ is not used |
| | 2 | CSR **Martini dECO Quiet Panel 50 mm** | thermally bonded polyester, 25–60 kg/m³ | — | https://www.branz.co.nz/design-build/certified-products/csr-martini-deco-quiet-panel-50-mm | source (density range only) |
| Lining cassette sheet | 1 | Galvanised steel sheet 0.5 mm (EN 10346 DX51D+Z or equal; VN coil makers) | 3.93 kg/m² for 0.5 mm steel | 3.93 | standard material; supplier unverified | calculation; supplier HOLD |
| Front, smoked acrylic (optional experiment only) | 1 | Perspex **Neutral 9T56** cast acrylic | 6, 8, 10, 12 mm; 3050 × 2030; 1.19 g/cm³; LT 46%, the same at any thickness (Perspex); Euroclass E, UL 94 HB | 11.9 at 10 mm | https://www.perspex.co.uk/materials/perspex-cast-acrylic/colours-transparent-and-tints/ ; data sheet https://www.perspex.co.uk/Perspex/media/General/technical-library/PDFs/Perspex-Cell-Cast-Acrylic-Technical-Data-Sheet-(Complete)_EN-2019.pdf | source |
| | 2 | Röhm/Polyvantis **PLEXIGLAS GS** grey (7C83 / 7C82) | 1.19 g/cm³; Euroclass E; grey codes seen only in snippets, 3–8 mm | 11.9 | EPD https://www.zenit.cz/public/media/Plasty/Zenit_Bezpecnostni_List_Plasty_Plexiglas_EPD.pdf | source; grey in 10 mm unverified |
| | 3 | VN "mica" (Taiwan FS / Chochen) | 2–50 mm, 1220 × 2440; no grey code shown | — | https://mica.com.vn/san-pham/mica-acrylic-dai-loan-fs-fusheng/ | source (sizes); grey unverified |
| Front, 4+4 acoustic laminate (DECIDED) | 1 | AGC **Stratophone Planibel Coloured 44.2** (Grey or Dark Grey panes) | the cited pages offer it neither with toughened panes nor with "Rw 37 (0;−2), 9 mm, 21 kg/m²" (Reviewer 3), so those figures are removed | 21 (calculation, 2.5 g/cm³) | https://www.agc-yourglass.com/en-UG/brands/stratophone ; https://www.agc-yourglass.com/sites/default/files/2025-04/Showpad_Planibel%20Coloured_EN_LR.pdf | unverified for toughened panes |
| | 2 | Saint-Gobain **SGG STADIP SILENCE 44.2** on PARSOL grey | Rw 37 (0;−3); a toughened, heat-soaked version is not shown | 21 | https://www.saint-gobain.pt/assets/download/media/54856 | source for Rw; toughened version unverified |
| | 3 | Pilkington **Optiphon 8.8** | Rw 37 (0;−2); tint and a toughened version not stated | ~21 | https://www.pilkington.com/en/global/products/product-categories/noise-control/pilkington-optiphon | source; tint unverified |
| Front reference, toughened 8 / 10 mm | — | float glass data (toughening assumed neutral) | 8 mm Rw 32–34; 10 mm Rw 35; 1/3-octave data in the calc | 20 / 25 | Eastman acoustic glazing booklet https://saflex-vanceva.eastman.com/content/dam/saflex/pdf-documents/arch/saflex/brochures/ai-arch-7807_-_acoustic_glazing_performance_data_booklet_low-res.pdf | source |

VN availability: none of the tinted acoustic laminates or grey cast acrylic were found on a VN page. VFG (Vietnam Float Glass) lists no grey tint.

## C. Door and glass hardware (the plan leaves these out)

Door: 1176 × 2011 mm. 4+4 laminate (DECIDED) is 47.5 kg (PM figure). 8 mm glass would be 47 kg, 10 mm glass 59 kg, and the optional acrylic experiment about 32 kg with its hinge stile.

### C1. Hinges

**Main finding:** every published glass-door hinge is rated for doors 711–1000 mm wide, except the two below. Narrowing the door would change the look.

| Opt | Maker · article | Rating | Interface | Weight | VN | Source | Status |
|---|---|---|---|---|---|---|---|
| 1 (HOLD, was DECIDED) | dormakaba **OFFICE 11.233**, hinge for project doors with 160 mm frame portion | 70 kg, door width max 1200 mm | Needs a 160 mm frame pocket ("reception element VN 7608/160 3D or VZK 060-1/3, or equivalent – not included"); Ø20 frame pin; TSG 8/10 mm | Al 0.519 kg | dormakaba SG serves VN; stock unverified | https://dormakaba-res.cloudinary.com/image/upload/v1745406852/dormakaba-prod/1505294593-tb-054432-man-sa-da-door-systems-low-gb-2001.pdf (p. 68) | source; **not rated for the 4+4 laminate** (TSG 8/10 only; laminated only with MUNDUS patch fittings, which recommend heat-soaked panes): HOLD (ruling 3) |
| 2 | dormakaba **UNIVERSAL** pivots: PT 10 03.100 + floor bearing 01.137 (no floor recess, 80 kg) + PT 20 03.110 + PT 24 01.123 | range 130 kg / 1300 mm, but doors ≥ 1100 mm need an EN 4+ closer that the thin floor can't take | glass prep p. 29; pivot 55 or 65 mm from the frame | 0.564 + 0.195 + 0.477 + 0.042 kg | as above | https://dormakaba-res.cloudinary.com/image/upload/v1745424952/dormakaba-prod/1508255179-tbr-054433-universal-gb-170817.pdf | source; not chosen |
| 3 | Simonswerk **BILOBA BL 8910** (Bohle BO5210388), hydraulic, self-closing from 80° | 100 kg per pair, width 500–1000 mm | TSG 8–12, LSG 8.76–13.52; wall plate 59 × 110, 4 holes 40 × 80 | not published | unverified in VN | https://www.bohle.com/uk-EN/Biloba-BL-8910-hydraulic-swing-door-hinge-glass-wall-900/BO5210388 | source; width over |
| 4 | Kinlong **WHY11010**, SS304 | 65 kg per pair, 600–800 mm, glass 8–12 | no drawing | not published | **listed on kinlong.vn** | https://kinlong.vn/ban-le-carbin-tam-why11010/ | source; width over |
| 5 | Häfele **981.09.111** hydraulic, 10–15 mm glass | 65 kg / 2 hinges, 800–1000 mm | auto-close 85°, hold-open 90° | not published | hafele.com.vn blocked | Häfele TH catalogue https://htdocs.kirz.com/HTHMKT/Catalogue/AH/08-bathroom-fittings.pdf (p. AH 8.27) | source; width over |

### C2. Pull handle (tay nắm)

| Opt | Maker · article | Data | VN | Source | Status |
|---|---|---|---|---|---|
| 1 | Häfele UK **903.10.390** pull pair, 300 mm c/c, Ø19, M8, satin SS316 + fixing set **909.00.900** (8–18 mm leaves, Ø13 hole, nylon sheaths) | sleeved fixing suits acrylic | unverified | https://files.hafele.co.uk/CatalogFiles/www/19A1-129.pdf ; https://files.hafele.co.uk/CatalogFiles/www/19A1-130.pdf | source |
| 2 | ASSA ABLOY **AEH-11B-300** D-pull, back-to-back, 300 mm, Ø19, SS304 | brochure lists 10–12 mm glass | brochure on the ASSA ABLOY VN site | https://www.assaabloy.com/vn/market-images/product-assets/assa-abloy/pull-handle/assets/documents/Brochure%20-%20Pull%20Handle.pdf | source |
| 3 | CRL **LP8X8CH** ladder pull, 203 mm c/c, 305 mm long, Ø12 hole | 8–12 mm glass; about 0.70 kg | unverified | https://www.crlaurence.com/p/LP8X8CH | source |
| 4 | dormakaba **21.267** pair, 350 mm, holes 150 c/c, Ø22 hole | 1.254 kg per pair | dormakaba SG | TB PDF as C1 (p. 165) | source |

On acrylic, the holes follow C8: about 2 × the bolt Ø, PE sleeve, EPDM washers.

### C3. Perimeter seals (gioăng cửa)

| Opt | Maker · article | Data | Rating | Source | Status |
|---|---|---|---|---|---|
| 1 (frame stop, hinge side and top) | athmer **PS 1515 P Flex** | 15 × 15 mm, frame gap 2–6 mm, self-adhesive; lengths 2100–3000 mm; **PVC co-extrusion** | 56 dB per joint at 3 mm gap; UL10C | https://athmer.com/asia-en/ps-1515-p-flex/PS-1515-P-Flex | source; on an acrylic door the soft PVC must not touch the leaf (C8), so use an EPDM or silicone equivalent: HOLD |
| 2 | athmer **PS 1010 P Flex** | 10 × 10 mm, gap 2–4 mm | 52 dB per joint | https://athmer.com/asia-en/ps-1010-p-flex/PS-1010-P-Flex | source; same PVC caveat |
| 3 (silicone) | Pemko **S88BL SiliconSeal** bulb | 12.7 × 6.4 mm, silicone, self-adhesive; UL 1784, UL 10C | no dB published | https://doorwaysplus.com/shop/pemko-s88bl-siliconseal-1-4-bulb-perimeter-gasket-black-ul-10c-ul-1784-fire-smoke-rated-2204 | source; gap range unverified |
| 180° (door edge to fixed pane) | Bohle **BO5281018** "shower door seal with 180° front stop", 8–10 mm TSG, clear PVC, 2160 mm | push-on the fixed-pane edge; 4 mm (8 mm glass) or 6 mm (10 mm) between edges | none | https://www.bohle.com/se-EN/Shower-door-seal-with-1800-front-stop/BO5281018 | source; PVC caveat on acrylic; no dB data: weak point, HOLD |
| 180° alt | Häfele **950.06.590** (8–10 mm) / **950.17.851** (10–12 mm) glass door seal 180° | 23 mm lip, 5 mm gap | none | Häfele TH catalogue (p. AH 8.34) | source |

### C4. Drop seal (automatic door bottom, ron chân cửa)

| Opt | Maker · article | Data | Rating | Source | Status |
|---|---|---|---|---|---|
| 1 (pick) | athmer **Schall-Ex GSA** 1-1112 black RAL 9005, side-bonded, glass from 8 mm, ESG and VSG | 11.6 × 40 mm; travel 20 mm; stock 1208 mm cut back up to 125 mm, so **1176 works**; tape-bonded | 51 dB joint at 7 mm floor gap (a 47 dB figure quoted before isn't on the cited pages, so it is removed); "up to 37 dB Rw,P" | https://athmer.com/asia-en/schall-ex-gsa/Schall-Ex-GSA ; https://athmer.com/media/d9/c4/80/1746739483/EN_SchallExGSAnew.pdf | source; bond on acrylic HOLD |
| 2 | athmer **Schall-Ex GSH-10** 1-1132 black, push-on, ESG 10 mm | 13 × 40 mm; same lengths | 49 dB joint | https://athmer.com/asia-en/schall-ex-gsh-10/Schall-Ex-GSH-10 | source |
| 3 | Planet **KG-A10 schmal** 1209 mm (Planet 35121-A10, SFS 2137398) | 12.9 × 38 mm, stroke 16 mm, push-on + VHB, cut back 125 mm | 48 dB at 7 mm floor gap | https://www.assaabloy.com/ch/de/documents/service/downloads/planet/drop-down-seals/broschuere-planet-absenkdichtung-kg.pdf | source |

The actuator strikes the frame on the hinge side, so the strike point on the left decor block is a CAD detail.

### C5. Fixed glass retention (U-profile, nẹp kính)

| Opt | Maker · article | Data | Source | Status |
|---|---|---|---|---|
| 1 | dormakaba **MR 22 / MR 28** frame profile system (frame profile + clamping profile + 2 contact rubbers) | glass 8 or 10 mm; face 22 / 28 mm; "No load transfer by the profiles"; rubbers are PVC | https://www.dormakaba.com/sg-en/offering/products/interior-glass-systems/fittings-for-toughened-glass-assemblies/mr-2228--do_3303 | source; PVC rubbers not for acrylic |
| 2 | Bohle **BO5201571** U-profile 15 × 15 × 1.5 mm + **BO5201735** silicone U-profile seal (TSG 8–12) | ≈ 0.17 kg/m (calculation); silicone dry-glazing seal | https://www.bohle.com/uk-EN/U-profile-15-x-15-mm/BO5201571 ; https://www.bohle.com/uk-EN/U-profile-seal/BO5201735 | source; silicone is acrylic-safe |
| 3 | CRL **DUC38BA** dry-glaze U-channel with vinyl | 10 mm only; ≤ 1.0 kg/m (calculation) | https://www.crlaurence.com/p/DUC38BA | source; vinyl not for acrylic |

Pick: option 2 (silicone seal) for both acrylic and glass. The slanted edge follows the decor block, which is a CAD detail.

### C6. Setting blocks (căn kê kính)

| Opt | Maker · article | Data | Source | Status |
|---|---|---|---|---|
| 1 | CRL **SBEP3 / SBEP4** EPDM, 80 Shore A, 5 or 6 × 29 × 102 mm, cut to width | "used successfully … with Saflex (PVB) interlayer laminated glass" | https://www.crlaurence.com/p/SBEP3 | source |
| 2 | Tremco silicone 80 Shore **0020381SA4** / EPDM 85 Shore **0020381EA4**, 6.4 × 25.4 × 101.6 mm | stocked program | https://www.tremcosealants.com/media/Sealants/Documents/Tremco_Stocked_Setting_Block_Program.pdf | source |
| no | CRL SB572 neoprene | may discolour silicones | https://www.crlaurence.com/p/SB572 | source |

### C7. Holding the door shut (chốt / nam châm)

| Opt | Maker · article | Data | Source | Status |
|---|---|---|---|---|
| 1 (HOLD, was the pick) | dormakaba **STUDIO Rondo lock 10.200**, non-locking latch, DIN EN 12209 | lock 159 × 65 mm; needs a strike in the frame and a lever pair; Al 0.840 kg | dormakaba TB PDF as C1 (pp. 12, 16) | source; **not rated for this door: STUDIO is for doors up to 1000 mm, ours is 1176 mm.** HOLD (ruling 3): the OFFICE Junior lock 11.264 / 11.265 in the same catalogue is the candidate Reviewer 3 found; its rating for 1176 mm and laminated glass goes to dormakaba |
| 2 | Sugatsune **HT-MSG62** magnetic catch + strike HT-MSG62-U10 | 35 N; strike on the upper door | https://www.marek.eu/katalog-obrazku/produkt-36377/85606-ht-msg62.pdf | source; 35 N is likely too weak for the seals alone |
| 3 | Simonswerk **KEEP CLOSED KCM 50 / KCM 50/G** | for 8 and 10 mm glass; force not published | https://selector.simonswerk.com/en/products/detail/kcm-50-g | source; force unverified |

Later US rules want a light pull (about 22 N). The latch keeps the opening force low, while a self-closer would add force.

### C8. Clamping acrylic (HOLD)

No door-size hinge, patch or seal maker covers acrylic. dormakaba, Bohle, CRL and Häfele specify toughened glass only, and dormakaba recommends heat-soaked TSG. Acrylic makers' rules:
- Bolts at the edge must not be the main support "without the use of load spreading devices" (Perspex Design Guide).
- Holes at least 2 × the bolt Ø, or bolt + 5 mm per metre of sheet. Fit a PE sleeve or rubber grommet, use large EPDM or neoprene washers, and keep the edge distance at least 1.5 × the hole Ø (ACRYLITE, PLEXIGLAS).
- Tighten only so the sheet can still slide, with a spacer sleeve to limit clamp pressure. Allow 5 mm per metre: about 6 mm across and 10 mm along the door (PLEXIGLAS).
- "Plasticised PVC sealing strips should not be used under any circumstances" (Perspex). EPDM, polychloroprene, PE and silicone are fine (PLEXIGLAS).
- No maker publishes a torque or pad-pressure limit. Long-term tensile is 7–8.6 MPa (Perspex).

Sources: https://www.perspex.co.uk/Perspex/media/General/technical-library/PDFs/Perspex-Design-Guide.pdf ; https://www.zenit.cz/public/media/Plasty/Zenit_Montaz_Plasty_Plexiglas_EN.pdf ; https://www.acrylite.co/resources/knowledge-base/article/how-far-in-should-I-drill-a-hole-from-the-edge-of-acrylic-sheet

What the acrylic door needs is a continuous aluminium strip along the hinge edge, clamped with sleeved oversize bolts, with the 11.233 hinges fixed to the strip and not to the PMMA. That's our reading of the guides, not a maker design. The PM made it the baseline (C9). These questions go on the factory's list, because we don't contact suppliers:
- dormakaba approves 11.233 on 10 mm acrylic: hole size, sleeve, pads, torque and rating.
- Perspex or Röhm approves the hinge-edge detail.
- Every seal touching the leaf is confirmed acrylic-safe.

These matter only for the optional acrylic experiment; the baseline is 4+4 laminated glass (DECIDED). The stile detail is in C9.


### C9. Acrylic door experiment: hinge-edge stile (only if the factory sample tests acrylic)

The baseline front is 4+4 laminated glass (DECIDED); this detail applies only to the optional acrylic experiment. The hinges never touch the acrylic. They clamp an aluminium stile that has the same thickness as the glass they're rated for. The stile carries the acrylic leaf through a bolted joint that spreads the load and lets the acrylic move. The opaque 80 mm band it adds is why acrylic isn't the baseline (look rule D-01).

| Part | Spec | Why | Status |
|---|---|---|---|
| Hinge stile | Aluminium flat bar 10 × 50 mm, EN AW-6060-T66 or 6063-T6, 2011 mm long, anodised or painted to suit the look; the 11.233 hinge preparation is machined into the bar, not the acrylic | 10 mm is the glass thickness the hinge is rated for, so the hinge clamps metal, not PMMA | calculation; hinge-on-aluminium rating on the factory's list |
| Acrylic leaf | Cast PMMA 10 mm, Perspex Neutral 9T56, 1123 × 2011 mm (1176 door − 50 stile − 3 joint) | same outer door size as v1 | source (sheet); size calculation |
| Joint | 3 mm butt gap with an EPDM strip between stile and acrylic edge | acrylic must never touch plasticised PVC; EPDM is listed as suitable by PLEXIGLAS | source (C8) |
| Cover strips | 2 × aluminium flat 3 × 60 mm, full height, one on each face: 30 mm over the stile, 30 mm over the acrylic, with 2 mm EPDM pads on the acrylic side | spreads the load ("load spreading devices", Perspex) and hides the bolts | calculation |
| Bolts | M6 throughout (one-bolt rule). Stile side: 8 bolts in Ø6.6 holes. Acrylic side: 8 bolts in Ø12 holes (2 × bolt Ø, ACRYLITE; PLEXIGLAS gives bolt + 5 mm/m = 11.6), each with an aluminium spacer sleeve 6.5/9 mm × 13 mm and a PE sleeve, so the bolt clamps the strips onto the spacer and the EPDM is compressed to a set gap. Hole centres 20 mm from the acrylic edge (≥ 1.5 × hole Ø = 18 mm) | PMMA is only clamped through soft pads, with the pressure set by the spacer, as PLEXIGLAS shows | source for the rules; layout calculation |
| Movement | Fixed point: the middle two acrylic-side bolts in round Ø12 holes. All others in vertical slots 12 × 20 mm (±4 mm) | differential movement along the 2011 mm edge: 2.2 mm thermal (20 K, PMMA 77 vs Al 23 × 10⁻⁶/K) + 2–6 mm moisture (0.1–0.3%); fixed at mid-height that's 2.1–4.1 mm at each end | calculation |
| Load check | Acrylic leaf 26.9 kg, so 33 N per acrylic-side bolt. Bearing on PMMA through the 9 mm sleeve is 0.37 MPa against a long-term tensile of 7 MPa (factor about 19). The EPDM friction carries part of it too | — | calculation |
| Mass | Stile 2.71 + covers 1.95 + pads 0.31 + bolts 0.19 kg; door total about 32 kg (the frameless acrylic door is 28 kg; 8 mm glass is 47 kg); +3.9 kg in the pod totals | well inside 11.233's 70 kg | calculation |
| Seals | The hinge-side frame stop seal bears on the aluminium stile. Latch-side and 180° seals that touch the acrylic must be EPDM or silicone | Perspex: no plasticised PVC on acrylic | source (C8) |
| Handle and catch | Through-bolted on the acrylic with the same sleeved-hole rule (2 × bolt Ø, EPDM washers). Catch strike on a small aluminium plate with 2 sleeved bolts | same creep rule | HOLD for the factory's list (Häfele 909.00.900 sleeves are sized for a Ø13 glass hole) |
| **Look** | An opaque band about 80 mm wide down the hinge edge, on both faces (stile 50 + cover 30). v1's frameless door doesn't have one | it is the price of the 24 kg saving; the 4+4 glass fallback has no band | the factory sample shows both fronts; PM's call on the look stays open |

For the factory's list: dormakaba, the 11.233 clamping a 10 mm aluminium bar (rating and gaskets); Perspex or Röhm, the sleeved joint detail and the EPDM pads; athmer, the drop seal bonded to acrylic.

## D. Seals and gaskets for the walls and floor

| Function | Opt | Maker · part | Data | Source | Status |
|---|---|---|---|---|---|
| Gasket on every panel joint and around the lining cassettes | 1 (pick) | Rogers **PORON 4701-40 Soft** (PSA laminated by a converter) | compression set ≤ 5% at 23 °C, ≤ 10% at 70 °C (ASTM D3574 D); 3.18–12.70 mm; 41 kPa at 25%; UL 94 HBF | https://www.stockwell.com/data-sheets/poron-4701-40-soft.pdf | source; converter with PSA in 10–20 mm strips HOLD |
| | 2 | tesa **66709** EPDM closed-cell, 9.5 mm | −40 to 115 °C; 45 kPa at 25%; FMVSS 302; no compression set published | https://www.tesa.com/en/files/download/12214269,2,medium-12214269.pdf | source |
| | 3 | Steinbach & Vollmann EPDM cellular, self-adhesive **V07800880** (15 × 5), **V07800820** (10 × 5) | 30 Shore; −60 to 160 °C | https://stuv.de/api/en-GB/datasheet/V07800880 | source |
| Base seal under the thin floor | 1 | Pemko **S88BL** silicone bulb, 12.7 × 6.4 mm | UL 1784 | as C3 | source; gap range unverified |
| | 2 | tesa **tesamoll D-Profile** EPDM (BNR 05389 / 05393) | gaps 3–7 mm | https://tesa.com/pt-pt/files/download/11243651,1,medium-11243651.pdf | source; consumer grade |
| | 3 | tesa **tesamoll STANDARD Door Brush BNR 05433** | gaps up to 12 mm | https://www.tesa.com/en/files/download/12230504,0,medium-12230504.pdf | source; a brush leaks more than a bulb |
| Cable holes | — | rubber grommets or sealant at every penetration | about 0.1 dB per unsealed 28 mm hole in the DECIDED pod (calculation) | report §4 | calculation |

## E. Lights, front light and power

Lights run on the 12 V DC bus (D-10) and stay low-heat. In v1 the pod had two 170 × 170 mm mains panels.

| Function | Opt | Maker · article | Data | Source (checked 2026-10-31) | Status |
|---|---|---|---|---|---|
| Ceiling light | 1 (pick) | Häfele **Loox5 12V LED 2094** downlight, Ø65 mm; white 3000 K **833.72.539** / 4000 K **833.72.540** (black 833.72.535 / .536); surface bezel 833.72.807 (white) | 12 V, 2.5 W, dimmable, IP20; 150 lm (3000 K), 160 lm (4000 K); CRI Ra > 90, R9 > 50; recess in a Ø58 hole, at least 13.5 mm deep, which fits inside the lining cassette's 25 mm gap; 2 m lead with Loox5 12 V connector | https://files.hafele.co.uk/CatalogFiles/www/20D5-115A.pdf | source; Häfele has a VN company, but stock of these UK article numbers is unverified |
| | plan | six downlights over the ceiling: 15 W, about 900–960 lm in total (calculation) | — | — | calculation; light level to confirm on the prototype |
| Soft front light for video calls | 1 (pick) | Häfele **Loox5 LED 2162** 8 mm strip, 12 V; 3000 K **833.74.056** / 4000 K **833.74.057** (833.74.246 / .247 are 50 m reels, corrected), in an aluminium diffuser profile | 3.0 W/m; 465 lm/m (3000 K), 490 lm/m (4000 K); CRI Ra 92, R9 > 50; Häfele recommends a profile "for appealing design, diffuse" light | https://files.hafele.co.uk/CatalogFiles/www/25L1-18.pdf | source; profile article and VN stock unverified |
| | plan | 2 m of strip on the back wall or the ceiling front edge, facing the user: 6 W, about 950 lm (calculation) | — | — | calculation; position decided with the Control Engineer (open question on lights) |
| Driver | — | Loox5 12 V driver from the same system, or the pod's 12 V bus (D-10) | — | catalogue reference in the 25L1-18 sheet | unverified |

Power inlet (outside, back wall):

| Opt | Maker · part | Data | Source | Status |
|---|---|---|---|---|
| 1 (pick) | Neutrik **NAC3MPX-TOP** powerCON TRUE1 TOP locking inlet + **NAC3F-TRUE1-S** cord connector | 16 A 250 V (EN 60320-1); IP65 only mated or with its **SCNAC-01** cap, so the cap is on the parts list; can be unplugged under load; cutout Ø23.8 + 2 × Ø3.2 at 19 × 24 mm | https://www.neutrik.com/en/product/nac3f-true1-s ; https://www.neutrik.com/en/product/nac3fx-w-top | source; VN stockist unverified |
| 2 | Schurter **6162.0156** IEC C14 V-Lock inlet | 10 A 250 V; IP20; snap-in 27.5 × 20 mm; needs a V-Lock cord | https://www.digikey.at/en/products/detail/schurter-inc/6162-0156/2646983 | source (distributor) |
| LAN | Neutrik **NE8FDP** etherCON feed-through | CAT5e; cutout Ø24 + 2 × Ø3.2; panel ≤ 4 mm | https://www.neutrik.com/en/product/ne8fdp | source |

Plan items VT07 to VT09: UTEN S300 switch and socket (code S300GK12Z12Z13/N on utenmall, but the catalogue's 1-way code is S300K11Z12Z13: confirm), LAN socket S300G-1PC (category not stated), 86 × 86 plates with UBBOX/A 85 × 85 × 50 boxes. Source: https://utenmall.com/san-pham/bo-cong-tac-1-chieu-va-o-cam-5-chau-s300/ ; https://utenmall.com/san-pham/bo-o-cam-don-mang-s300/ ; catalogue https://utenmall.com/wp-content/uploads/2025/08/UTEN_Catalogue-UTEN-2024-nen.pdf (pp. 58–61). VT08, the UTEN fan speed control S300G-1D/S (phase-cut, 25–300 W, for ceiling fans), is replaced by the CO2 controller's 0–10 V output.

**Power budget** (calculation; the electrical design itself belongs to the electrical scope):

| Circuit | Load | W |
|---|---|---:|
| 12 V DC bus (D-10) | Ceiling lights, 6 × Loox5 2094 | 15 |
| 12 V DC bus | Soft front light, 2 m Loox5 2162 | 6 |
| 12 V DC bus | Sensor hub with CO2 display, presence sensor | about 5 (assumption) |
| 12 V DC bus | Voice cockpit kit reserve, 12 V 5 A (D-11) | 60 |
| 12 V DC bus (D-10) | 4 fans, Noctua NF-A14 industrialPPC-3000 PWM, two per path (fix pass; the mains fan exception is no longer needed) | power at our duty unverified (maker figure not found); HOLD for the fan-sample test |
| Mains, outlet circuit | User sockets (laptops) | up to 2 × 100 |

## F. Air: fans, silencer, controls

### F1. Fans (VT06)

| Opt | Maker · SKU | Duty near 70 l/s | Sound | Power | Size, weight | VN | Source | Status |
|---|---|---|---|---|---|---|---|---|
| 1 (DECIDED) | Noctua **NF-A14 industrialPPC-3000 PWM**, 12 V, **two per path** (four in all), side by side on a bulkhead in a lined fan box: the supply pair high in the right decor block, blowing up, the exhaust pair lying flat in the soffit's right end, blowing up into the roof slot (D-60) | maker: 3000 rpm, 269.3 m³/h at 0 Pa, 6.58 mm H₂O (64.5 Pa) maximum. At 53 l/s the supply pair runs at about 72% speed (17 Pa, with the riser) and the exhaust pair at 65% (12 Pa); the supply pair tops out near 73 l/s and the exhaust pair near 82 l/s (straight-line curve, calculation) | 41.3 dB(A) at full speed, condition not stated (taken as sound pressure at 1 m: LwA = LpA + 11, assumption); no octave data. Inside the pod 25.1 dB(A) at 53 l/s, 29.6 at 65 l/s, and 66 l/s at 30 dB(A) (report §7d) | 12 V bus (D-10); power at our duty unverified | 140 × 140 × 25; about 0.3 kg each (assumption: weigh the sample) | unverified in VN | maker page https://www.noctua.at/cn/products/nf-a14-industrialppc-3000-pwm/specifications | source; octave spectrum, tones and flow in the box HOLD for the fan-sample test |
| rejected (DECIDED at 5c1003b) | Soler & Palau **TD-500/150-160 SILENT ECOWATT** (EC, 0–10 V) | 4 V curve: about 70 l/s at 9 Pa | duct side 25/37/49/46/37/29 dB(A) per band at 4 V; the casing radiates 44 dB(A) (25/36/40/41/24/21). With the casing sound the 5c1003b layout gives 35.8 dB(A) at 53 l/s (report §7i) | 10 W at 4 V | ØD 221, length 484, 6.0 kg: **doesn't fit** the 199 mm clear depth of the 205 mm decor | unverified in VN | S&P TD SILENT ECOWATT catalogue https://statics.solerpalau.com/media/import/documentation/EN_TD-SILENT-ECOWATT.pdf (duty points read off the curve figure; casing data as read by Reviewer 3) | source; rejected on fit and noise (report §7i) |
| rejected | Soler & Palau **TD-350/100-125 SILENT ECOWATT** (EC) | 8 V: about 250 m³/h at 30 Pa | 54 dB(A) at 8 V | 15 W at 8 V | ØD 204 (doesn't fit 199 mm), length 462, 5.0 kg | unverified in VN | same catalogue | source; rejected on fit |
| plan, rejected | Panasonic **FV-15AUL1** wall fan | 255 m³/h at 0 Pa; no fan curve published | 36 dB(A) (method not stated) | 12.5 W | 1.2 kg; cutout 200 × 200 | VN | spec sheet https://www.panasonic.com/content/dam/panasonic/vn/vi/pim/dam/FV/FV-15A/FV-15AUL1-PP/ast-2125349.pdf ; manual https://www.panasonic.com/content/dam/panasonic/vn/vi/pim/dam/FV/FV-15A/FV-15AUL1-PP/ast-2353437.pdf ; product page https://www.panasonic.com/vn/air-solutions/products/fan-ventilating-fan/vf/wall-mounted-type/wall-mount-vf-automatic-shutter-luver-series/fv-15aul1.html | source: the manual says "Prohibit to install this fan in the ceiling" |
| 12 V, not picked | San Ace **109E5712M501** (172 × 150 mm); ebm-papst **RG 160-28/14 N** (12–28 V centrifugal) | San Ace 248 m³/h at 0 Pa, 67.6 Pa maximum; RG 160: 209 m³/h at 24 V | San Ace 41.0 dB(A) (condition not stated); RG 160: LwA 66 dB at 24 V | San Ace 5.76 W; RG 160 20 W at 24 V | 172 × 150 (too big for the 155 mm passage stack); 220 × 220 × 56, 1.4 kg | unverified in VN | https://www.digikey.com/en/products/detail/sanyo-denki-america-inc/109E5712M501/6191765 ; https://img.ebmpapst.com/products/datasheets/DC-centrifugal-fan-RG1602814N-ENU.pdf | source; the RG 160 figures are at 24 V, not 12 V (corrected) |

Location (D-60, DECIDED; replaces PR #11's placement): the right decor block isn't the 1016 mm wide box PR #11 assumed. It follows the fixed glass, 145–343 mm wide below Z 1521, so the cartridges moved inside the pod (report §7b–7c).
- Supply: room air enters through a mesh in the right block's underside, in the base band's shadow line, and rises up a 1 mm steel riser behind the air column to the supply fans, high in the block behind its removable inner face. They blow into the top of the air column and down its cartridge to a kick grille at its foot.
- Exhaust: from a grille in the soffit's underside at its far end, along the soffit's cartridge to the exhaust fans in its right end, and up through a roof slot 2.3 m above the intake.
- Service, all from inside (D-59): the supply fans through the right block's inner face beside the column top; the exhaust fans through the soffit's underside.
- Sizes and positions: report §7e.

### F2. Silencer (ống tiêu âm)

D-60 (DECIDED, PM 2026-10-31) moves the cartridges inside the pod, behind felt-covered faces, with one size for both paths. PR #11's 159 × 405 × 1800 cartridges and the 150 mm exhaust riser are replaced: they needed 960 mm of width that the right decor block doesn't have.

| Cartridge or duct | Size mm | Build | kg | Source of the data | Status |
|---|---|---|---:|---|---|
| Supply, standing in the air column (front-right inside corner), air down to the kick grille | 173 × 314 × 1750 (width × stack × length) | two 80 mm passages between three 50 mm Pyrotek Sorberpoly 2D layers (32 kg/m³), 2 mm aluminium casing; 30 mm polyester fill to the column's felt-covered front and left faces | 11.2 | Pyrotek's 50 mm ISO 354 data (B), published | calculation; HOLD for the factory mock-up |
| Exhaust, lying in the soffit above the door head | same part, along the soffit | same; 30 mm fill to the soffit's underside and front face | 11.2 | same | same |
| Intake riser, behind the air column in the right decor block | 139 × 155, widening to 250 where it turns into the supply fan box; 1740 long | 1 mm galvanised steel, with a coarse stainless intake mesh in the block's underside | 9.2 with the mesh | calculation | CAD by the CEILING Engineer; the intake opening by FRONT |

Bought circular silencers with published insertion loss, for comparison only. At 225–270 mm outside diameter they're deeper than the 205 mm decor:

| SKU | D / D1 / L mm | kg | 125 | 250 | 500 | 1k | 2k | 4k dB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SR 125/1200 | 125 / 225 / 1200 | 5.9 | 9 | 16 | 27 | 48 | 27 | 21 |
| SRF 150/2000 | 149 / 270 / 2000 | 6.8 | 10 | 21 | 42 | 50 | 48 | 26 |

Source: Vents SR / SRF datasheet https://ventilation-system.com/download/sr-round-datasheet-20663.pdf (status: source; VN availability unverified).

### F3. Controls

The CO2 sensing and display come from the in-house Desk Pro AI sensor hub (DECIDED, D-09). It drives both 12 V fan pairs with the same signal for supply and exhaust, so the pod stays near room pressure. The fans take PWM, so the hub needs a PWM output or a 0–10 V to PWM converter: HOLD for the electrical scope.
- the hub sits on the air column's front face at seated eye height (Z 1200), with the boost button below it; its cables run in the column's cable chase to both fan pairs (D-60);
- the supply fan inlet sensor (D-50) sits in the supply fan box inlet, reading the intake air from the floor;
- start on presence;
- never below 26 l/s while occupied (D-44); 53 l/s for two;
- ramp to the 65 l/s boost as CO2 rises (800 ppm limit);
- boost on temperature too, because heat sets the flow (report §7a);
- run on for 15–30 min after the last presence;
- no user off switch, only boost.

Third-party CO2 controllers, for reference or as a fallback if the hub isn't ready for the prototype:

| Opt | Maker · SKU | Data | Source (checked 2026-10-31) | Status |
|---|---|---|---|---|
| 1 (VN) | Produal **HDH-N-R** (product no. 1135041010: HDH-N with HD-R relay option) | display; 0–2000 ppm with automatic self-calibration; typically ±40 ppm + 3% of reading; CO2 output 0–10 V, PI-control output 0–10 V; relay 24 V AC 1 A changeover, factory-set on at 1100 ppm; supply 24 V AC/DC; 87 × 86 × 30 mm. NDIR not stated | https://www.produal.com/en/products/hdh ; user guide https://produal-pim.rockon.io//rockon/api/v1/int/extmedia/openFile/01TGWJBKAXY5TMZKSPIZFLSVWYYEMK44CA ; VN seller https://stock.ttech.vn/cam-bien-do-nong-do-khi-co2-o2-voc-hang-produal-p24928.aspx | source; **listed in VN**; needs a 24 V supply |
| 2 | Belimo **P-22RTM-1900D-1** room unit (CO2, T, RH) | ePaper touch display 69 × 62 mm; NDIR dual channel, 0–2000 ppm, ±(50 ppm + 2% of reading), ±20 ppm per year; 3 × 0–10 V outputs; MP-Bus; IP30 | https://www.belimo.com/mam/general-documents/datasheets/en-gb/belimo_P-22RT..-1900D-1_datasheet_en-gb.pdf | source; VN stock unverified |
| 3 | E+E Elektronik **CDS201** (CO2, T, RH) with optional large graphic display (e.g. CDS201-M11 US format) | NDIR dual wavelength, 0–2000 / 5000 ppm, ±(60 ppm + 2%); three analogue outputs or RS485 | https://www.epluse.com/fileadmin/data/product/cds201/datasheet_CDS201.pdf | source; VN stock unverified |

Presence sensor for automatic start and run-on:

| Opt | Maker · SKU | Data | VN | Source | Status |
|---|---|---|---|---|---|
| 1 (pick) | Schneider **CCT551012** ARGUS Presence Dual-Tech, 2 channels | PIR + ultrasonic; output 2 (HVAC) relay 5 A, motor load 100 W, motion only, delay up to 60 min | VN distributors list the 1-channel CCT551011 | se.com product pages, links not kept | unverified; keep it away from vents and glass (maker warning) |
| 2 | Hager **EE805A** | PIR; 10 A AC1 230 V; Ø90 × 61 mm; 5 s–30 min | unverified | no link kept | unverified |
| 3 | Legrand **048803** ceiling PIR | 8.5 A; 360°, about 8 m; 5 s–30 min | VN distributor (knxstore.vn) | https://knxstore.vn/products/cam-bien-gan-tran-8-5a-legrand-048803 | source |

## G. Low-emission certified options

| Use | Product | Certificate or label | Source | Status |
|---|---|---|---|---|
| Felt | Autex Cube / Composition | CDPH Standard, "<0.092 mg/m³ (7 days)", Declare Red List free, HPD, EPD | A3 | source |
| Felt | Woven Image EchoPanel | GreenTag GreenRate Level A, PHD PlatinumHEALTH | https://globalgreentag.com/products/echopanel | source |
| Felt | DHG (plan) | none named | A3 | source (none) |
| Glue | SikaTack Panel-50 | Indoor Air Comfort GOLD, EMICODE EC1 Plus, A+, M1 | A9 | source |
| Glue | Bostik P95 Turbo-Fix | EMICODE EC1+ | A9 | source |
| Boards | none in the DECIDED stack | (if plywood or HDF returns: E0 / CARB P2 / TSCA Title VI with a certificate number; HCPLY self-declares, UPM WISA on request) | A2 | source |
| Steel lining, aluminium frame, ACP | no wood, no formaldehyde | — | — | — |

## H. Reserved hooks for the voice cockpit kit

Mic array, speakers, screen and status light. Reserved here; the kit itself isn't designed.
- **Mounting:** M6 rivnuts (A5) in the 20 × 40 aluminium members at positions the Layout Engineer sets. Screen on the back wall, status light on the front decor top block, mic array and speakers on lining cassettes. Never cut through the ACP outer skin.
- **Cable path:** the 25 mm gap inside each lining cassette; the ceiling cassettes link the back wall to the front decor blocks.
- **Power:** 60 W reserve in the power budget (E) and in the heat figures (report §7a).
- **Data:** the NE8FDP LAN feed-through (E) and the UTEN LAN socket.

## Open questions for suppliers (no contact yet; for the PM to send)

1. Nhôm Việt Dũng (Alcorest): kg/m² and core type of 3 mm × 0.21 EV3038; V-groove rest thickness; whether 3 mm FR exists.
2. dormakaba (PM ruling 3): a frameless side-hung hinge set and a lock rated for a 4+4 (8.76 mm) laminate of toughened, heat-soaked panes, a 47.5 kg door and 1176 mm width, with the hinges clamped in a pocket in the left decor block. Does OFFICE 11.233 accept that laminate, or only the MUNDUS patch fittings? Is the OFFICE Junior lock 11.264 / 11.265 rated for 1176 mm and laminated glass? Hole and step sizes for the 21.267 handle on laminate (Reviewer 3: a stepped Ø28 / 26 hole); the frame reception element; VN stock.
3. athmer: Schall-Ex GSA on the 8.76 mm laminate; PS 1515 in EPDM or silicone; actuator strike detail.
4. Perspex or Röhm (acrylic experiment only): approval of a sleeved hinge-edge strip on 10 mm cast acrylic; a hard-coated grade.
5. AGC, Saint-Gobain or a VN laminator: a grey 4+4 (8.76 mm) laminate of toughened, heat-soaked panes, with an acoustic interlayer if it is offered toughened; its Rw; VN stock.
6. Noctua or its distributor: octave-band sound power of the NF-A14 industrialPPC-3000 PWM at 1500–2500 rpm, and the measurement method behind 41.3 dB(A); VN stock.
7. Felt supplier: ISO 354 data from 100 Hz for the 9 mm felt with a 25 mm air gap behind it, and an emission certificate (HOLD, Target 6); or Autex Cube in VN.
8. Rivnut supplier: sample fit of CAH3-610-4.2 in a 20 × 40 × 1.2 member, and its spin-out torque there.
9. UTEN: switch code K11 vs K12; LAN category.
10. Häfele: KEKU EH load ratings from Häfele (per fitting or per pair; pull-out for a ceiling), a captive or locking version, and a fixing to a 0.5 mm steel tray return; a rated safety lanyard.

## Sample tests (factory, before CAD freezes)

1. **Wall sample:** sound insulation and the felt's absorption on its 25 mm gap, both measured down to 100 Hz (PM ruling 5).
2. **Rivnut spin-out:** M6 rivnuts in the real 20 × 40 × 1.2 tube, torque to spin-out; this sets the tightening torque (PM ruling 6).
3. **Fan sample:** one fan pair in its lined box on a D-60 cartridge: flow against pressure, octave sound power at 53 and 65 l/s, and any tone at 125–250 Hz (report §7d). The same set-up runs the recirculation check: at the 65 l/s boost, the inlet stays within 0.5 K of the room (report §7g, ISS-078).
4. **Cassette clips:** pull test of the picked clip on a real cassette return; drop test of the ceiling safety catch.
5. **Door sample:** the rated hinge set and lock on the 8.76 mm laminate, with the seals.
