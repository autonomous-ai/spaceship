"""Every input number of the layout study, with its status and source.

Status words follow the guideline (section 10), and only these five are used: confirmed,
source, calculation, assumption, unverified. A value the PM decided is confirmed (AGENTS.md
makes the PM's decision the requirement); its source cites the decision log entry (D-xx) or,
until the log carries it, the PR ruling. A material property the PM chose to use keeps the
status of its evidence (for example the ACP's kg/m2 stays a calculation). Nothing in the other
scripts may introduce a number that is not either defined here or calculated from what is
defined here, except plain counts that the scripts state next to the code (for example
"2 hinges").
"""
from dataclasses import dataclass

# ---------------------------------------------------------------- sources
SOURCES = {
    "S01": ("v1 materials BOM, v5, 2026-10-29", "sources/v1/indoor-pod-v3-bom-v5-2026-10-29.xlsx"),
    "S02": ("v1 STEP assembly, exported 2026-10-14 (older than the BOM; cross-check only)", "sources/v1/indoor-pod-v3-assembly.step"),
    "S03": ("v1 drawings: wood parts, floor frame, decor frame", "sources/v1/drawings/"),
    "S04": ("v2 build plan from the indoor pod lead engineer", "v2/00-Control/v2-build-plan.pdf"),
    "S05": ("v2 plan approved by the product owner, 2026-10-31 (targets, light options, pallet sizes)", "v2/PLAN.md"),
    "S06": ("EN 1993-1-1 section 3.2.6: steel density 7850 kg/m3", "EN 1993-1-1:2005"),
    "S07": ("EN 1999-1-1 section 3.2.3.1: aluminium alloy density 2700 kg/m3", "EN 1999-1-1:2007"),
    "S08": ("EN 572-1: soda-lime silicate glass, density 2500 kg/m3", "EN 572-1:2012+A1:2016"),
    "S09": ("Evonik PLEXIGLAS GS/XT technical information: PMMA density 1.19 g/cm3 (ISO 1183), E = 3300 MPa", "https://www.voskunststoffen.nl/files/166151/datasheet%20plexiglas%20XT%20GS.pdf (read 2026-10-31)"),
    "S10": ("3A Composites DIBOND product guide: ACP with 0.3 mm aluminium skins, PE core, 2 mm = 2.9 kg/m2, 3 mm = 3.8 kg/m2", "https://www.display.3acomposites.com/files/downloads/products/en/aluminium-composite-sheets/EN_DIBOND_ProductGuide.pdf (read 2026-10-31)"),
    "S11": ("Polyx Board 9 datasheet: 9 mm polyester (PET) acoustic board, 1800 g/m2", "https://aid.co/wp-content/uploads/2024/10/Polyx-Board-9-No-Insulation-No-Air-Gap.pdf (read 2026-10-31)"),
    "S12": ("Compocel AL TDS: 10 mm aluminium honeycomb panel, 0.5 + 0.5 mm skins, about 4.0 kg/m2", "https://www.chemical-concepts.com/wp-content/uploads/2023/09/Compocel-AL-TDS.pdf (read 2026-10-31)"),
    "S13": ("Plywood density: eucalyptus-core plywood 580 +/- 10 kg/m3 (EN 323, distributor datasheet); Vietnamese acacia wood 574-597 kg/m3 (VAFS)", "https://vafs.gov.vn/en/wood-properties-of-some-commercial-tree-species-for-the-central-north-region-of-vietnam/ (read 2026-10-31)"),
    "S14": ("PHS S-4840 new wood GMA pallet: 48 x 40 x 4.75 in, 44 lb, 2500 lb dynamic capacity", "https://www.phsinc.com/pallet/wood-pallets/s-4840/ (read 2026-10-31)"),
    "S15": ("Uline H-1627 new wood pallet 96 x 48 in: 107 lb, 4-way, 7000 lb fork capacity; 3.5 in stringers, 0.5 in deck boards", "https://www.uline.com/Product/Detail/H-1627/Pallets/New-Wood-Pallet-96-x-48 (read 2026-10-31)"),
    "S16": ("NMFTA: ClassIT+ is the official source for NMFC classes; since the 2025 NMFC changes density plays a larger role (density scale widened from 11 to 13 sub-provisions, per carrier summaries)", "https://info.nmfta.org/2025-nmfc-changes (read 2026-10-31)"),
    "S17": ("2010 ADA Standards section 404.2.3: door clear width 32 in (813 mm) minimum", "https://www.access-board.gov/ada/#ada-404 (read 2026-10-31)"),
    "S18": ("Market study, 2026-10-31", "v2/research/market-study.md"),
    "S20": ("Hardware Engineer's sound and air calc (branch super-tab/09f4617f, commit e22cab1): total-pod kg vs D_S,A curve; at a 380 kg budget with a 10 mm smoked acrylic front: walls DL-ST (ACP 3 / 40 mm fill, shared studs / 0.5 mm steel + felt 9), ceiling DL-2HDF-60-FL (ACP 3 / 60 mm fill / 2 x HDF 3 floating + felt 9), 377 kg, D_S,A 22.5 dB central", "v2/05-Engineering/acoustics-air/calc.py on that branch (read 2026-10-31)"),
    "S21": ("Hardware Engineer's final wall stack, relayed by the PM in the layout chat, 2026-10-31: ACP 3 / 20x40 aluminium frame at 400 mm with 40 mm PET fill / floating lining cassette (0.5 mm steel tray, 25 mm deep, 9 mm felt across its face); 81 mm and 13.1 kg/m2. Ceiling the same on 20x100, 141 mm. Pod about 385 kg and 24.2 dB with the acrylic front", "layout conversation, PM message of 2026-10-31"),
    "S22": ("PM ruling relayed in the layout chat, 2026-10-31: front is 4+4 laminated glass, frameless like v1, not acrylic (acrylic needed an opaque 80 mm band down the door, which breaks the look); the sound study puts the pod at about 400 kg and 23.8 dB with 40 mm ceiling frames and separate silencer boxes; the door is handled by two people with suction lifters", "layout conversation, PM message of 2026-10-31"),
    "S23": ("Alcorest outdoor ACP, colour EV3038 Dark Yellow (the plan's VT01), 3 mm with 0.21 mm skins: maker's catalogue gives skins, not kg/m2; the sound study calculates 3.5 kg/m2 from the skin spec (selection.md VT01). PM ruling 2026-10-31: use 3.5", "https://vietdung.com.vn/wp-content/uploads/2026/07/CTL-ACP-ALCOREST-07.08.25.pdf (via the sound study's selection table)"),
    "S24": ("PM ruling 2026-10-31: the 400 kg cap stays; carry the total as 400 +/- 10 kg until the CAD parts list settles it; if the CAD BOM lands over 400 kg, trim the inner steel tray or the fans, not the sound", "layout conversation, PM message of 2026-10-31"),
    "S28": ("Decision log D-01 to D-59, as merged on main (1eec888; PR #19 added D-49 to D-59)", "v2/00-Control/decision-log.md (read 2026-10-31)"),
    "S29": ("PM ruling after Reviewer 2, 2026-10-31, now logged as D-40: the door gets a ~90 mm aluminium kick strip at the bottom in the base band's dark finish, housing the drop seal, about 1 kg", "layout conversation, PM message of 2026-10-31"),
    "S30": ("Hardware Engineer's bought-parts selection after the PR #11 fix pass: four Noctua NF-A14 industrialPPC-3000 PWM 12 V fans, two per path on a bulkhead in each cartridge's lined fan box, 140 x 140 x 25 mm, about 0.3 kg each (assumption: weigh the sample); two splitter cartridges side by side in the right decor block, 159 x 405 x 1800 mm plus a 300 mm fan box, 2 mm aluminium casing, three 25 mm Pyrotek layers, 40 mm polyester fill toward the pod, 17.1 kg each with that fill (calculation); exhaust riser between them, 150 x 155 x 2000 mm, 1 mm galvanised steel, 9.6 kg (calculation; CAD fit HOLD); cavity fill Pyrotek Sorberpoly 2D at 32 kg/m3, because the 24 kg/m3 grade has no published absorption", "v2/05-Engineering/hardware/selection.md, summary, B, F1 and F2 (PR #11, merged 39c5c3e; read 2026-10-31)"),
    "S31": ("Hardware Engineer's sound and air check after the PR #11 fix pass: the decided stack is 81 mm at 12.6 kg/m2 with frame, 32 kg/m3 fill and felt; the decided build is about 418 kg in its own model (417.5 kg: 102.4 kg rest of pod from an older copy of this study, 2.6 kg fixes, 12.63 kg/m2 over 12.33 m2 of walls and 3.64 m2 of ceiling, 71.9 kg glass, 34.2 kg cartridges, 9.6 kg riser, 1.2 kg fans, less 6 kg of the old study's fans and boxes); decor 205 mm deep; the 40 mm fill in front of each cartridge replaces the old felt-lined decor cavity", "v2/05-Engineering/acoustics-air/report.md sections 1, 6 and 7b, and calc.py pod_total_kg (PR #11; read 2026-10-31)"),
    "S32": ("Pod skeleton P03 build record, PM rulings: PR #15, back wall and ceiling frames span frame to frame between the side frames (X +-1207), so 1207 per half, with their linings staying 1169; PR #16 ruling 3, D-39 means as v1, and the v1 decor-frame drawing and STEP give 205 mm (front face Y -850, back face Y -645); PR #17 pass C, wall depth 1495 (side walls start at the decor back plate, as v1's 1496), side linings 1448 long to close the inside corner, upper side linings stop 4 mm under the roof frame (1098 tall)", "v2/01-CAD-Native/skeleton/BUILD-RECORD.md and 100000_P03_POD-SKELETON-PARAMETERS.csv (read 2026-10-31)"),
    "S33": ("Pod skeleton P04 (PR #24): 46 mm outer panel (ACP 3 + bond line 3 + frame 40), 84 mm stack, 2.26 mm seams; side panels 1492.74 x 1142.74, back panels 1200.61 x 1118.61, side linings 1445 long, back linings 1166 wide, floor panels 1210 x 1455", "v2/01-CAD-Native/skeleton/BUILD-RECORD.md and 100000_P04_POD-SKELETON-PARAMETERS.csv; updated in place in PR #58 (floor 9, threshold 13, back and ceiling frames 1198.99 under 1200.61 skins, the 220 mm bolt rule) and PR #94 (bolt pitches on the frame, bolt lines, counts, the floor on its 3 mm mat); the roll-up reads its named values"),
    "S34": ("WALL P01 parts lists merged on main for all four side panels: 210101 to 210104 the outer panels L1, R1, L2, R2 (frames with their 3 mid stiles at 1.0 mm and the 40 x 40 back stiles, L2 and R2 with 40 x 40 tops; skins; 40 mm fill at 24 kg/m3; bond sets; hardware listed) and 510101 to 510104 their lining cassettes (trays with lips, felts with ELECTRICAL's openings, hook-and-loop, seals; clips HOLD); the roll-up reads them", "PRs #41 (6ccbfac) and #104 (87586c1): v2/03-Manufacturing/wall/21010n_P01_*_BOM.csv"),
    "S35": ("CEILING P01 parts list, merged on main: panels C1 and C2 (frames with the 40 x 40 back member, skins, bond sets; hardware and the closing-seam bulb seal listed) and the common ceiling cassette 510301 (tray, 2 ribs, felt, three fill bays at 25 kg/m3; clips and catches HOLD); its first list gave 9.586 kg a panel and 9.816 kg a cassette on skeleton P03; the roll-up reads it", "PR #32 (c72ea57): v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv"),
    "S36": ("FRONT door unit 360001 P01 parts list, merged on main: the 4+4 leaf, the hollow kick strip (D-85), drop seal, U-seal, 3 hinges (HOLD), the strike and one half of the magnetic seal (D-83), the pull pair (HOLD); its first list gave 50.17 kg with a solid 2.094 kg strip; the roll-up reads it", "PR #27 (7963e9c): v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv"),
    "S37": ("FRONT fixed glass unit 360002 P01 parts list, merged on main: the 4+4 pane, the glazing U-profile and U-seal, and one half of the magnetic seal (D-83, HOLD); its first list gave 29.58 kg with a glass-to-glass seal; the roll-up reads it", "PR #28: v2/03-Manufacturing/front/360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv"),
    "S38": ("Air report section 7f (D-60 on skeleton P04, with AIR #91's column and soffit sizes, section 7j): the air parts and the four fans, read from calc.py d60_parts()", "v2/05-Engineering/acoustics-air/report.md and calc.py d60_parts() (PRs #26, #30)"),
    "S40": ("D-81, the PM's weight ruling on PR #38: clip-only cassette fixing, no rails; the lighter cavity fill as the default, back to 32 kg/m3 if T02 fails (24 kg/m3, the grade Pyrotek lists and the sample tests); the base band with a 1.5 mm wall if BASE's check passes; the voice kit's 4.0 kg reserve outside the 420 kg cap, which is for the pod as shipped (D-11); the fixed glass in 3+3 only after FRONT's calculation; the door leaf in 3+3 rejected (D-46 stands); 410 kg or less as shipped", "v2/00-Control/decision-log.md D-81 (PR #36, fbdfc73; its fill corrected to 24 kg/m3 in PR #48, f03372c); the PM's brief for the live roll-up, 2026-10-31"),
    "S47": ("D-115: internal aluminium cleats in the WALL and CEILING frames, about 120 joints at up to 20 g each; the roll-up carries a 2.4 kg allowance (assumption) until the Joints Engineer's cleat models land", "the PM (Lead) in the layout study's group, 2026-11-01 (the decision log follows)"),
    "S46": ("INTERIOR P01 parts list, merged on main: the work-wall ledge (its top and 2 brackets on HOLD), the light shelf (back and side shelves, the right-wall down-light channel and diffuser; the LED strips are ELECTRICAL's) and the screen rail on HOLD; the roll-up reads it", "PR #92 (b3cc47e): v2/03-Manufacturing/interior/810000_P01_INTERIOR-PARTS-LIST_BOM.csv"),
    "S45": ("The joints' made hardware list, merged on main: the corner key family 111211 to 111214 (30 mm thick, 6 per pod), 30 locating spigots 831001 and 76 stop washers 831002 per pod, each with its CAD mass; BASE's follow-up (PR #138) took the 30 mm keys and a 54 mm glide doubler", "PR #139 (e7eef66): v2/03-Manufacturing/joints/V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv; PR #138 (8c3aca4)"),
    "S44": ("BASE P01 sample parts list, merged on main: the back-left corner and F1 (band tubes side LH 1517 long and back 2420 long at 1.5 mm, the back corner keys, a glide doubler and a HOLD levelling glide at each glide, floor panel F1 in poplar-core 9 mm ply with a hard face veneer, its 3 mm foam mat, the base seal); the right side and F2 as mirrors; the front bands and front keys follow in P02; the roll-up reads it", "PR #55 (dc61ad9): v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv"),
    "S43": ("ELECTRICAL P01 parts list, merged on main: 710000 as shipped, the power unit 710001 in B2 (enclosure, front plate, three 60 W Class 2 supplies, the LED controller, RCBO, inlet, sockets), the harnesses and cables, the hub and controls zone, the cord set, the LED strips (Loox5 2168 for the shelf uplight and the down-light, 2165 for the call light) and the call light profile; heat: the supplies' losses and the loads in its load table; the roll-up reads it", "PR #64 (e06fa22): v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv; v2/05-Engineering/electrical/"),
    "S42": ("D-86: the base band at 1.5 mm with an aluminium load block at each glide (about 0.4 kg per pod); the floor in poplar-core 9 mm ply with a hard face veneer, about 0.6 mm at a panel edge under 1000 N, its castor and edge tests planned. D-87: the intake riser joined to the supply fan box (about 14.9 kg with its fans) and the exhaust fan box fitted in the soffit (about 13.9 kg), both under 20 kg; the band's corner keys hook in (12 fewer bolts); the floor foam bonded under the floor panels", "v2/00-Control/decision-log.md D-86, D-87 (PR #57, e163737)"),
    "S41": ("D-82: the fixed glass stays 4+4 (a 3+3 pane bends 58 mm). D-83: a magnetic catch in DT and a magnetic seal pair replace the door lock. D-85, the PM's pick toward the 410 kg target: weight budgets for the light shelf (0.4 kg/m) and the ledge (1.5 mm folded aluminium); inner frame studs at 1.0 mm on the walls only, the perimeters at 1.2 for the rivnuts and the ceiling's inner members at 1.2 for the overhead cassette clips and safety catches; 2 inner studs in each back panel at 393 mm; a hollow kick strip with the same outside; poplar-core 9 mm floor plywood if BASE's castor and 1000 N edge tests pass. Rejected: the perimeters at 1.0 mm. Parked: the decor frames, 18 kg/m3 fill and a lighter felt; the 410 kg target stays", "v2/00-Control/decision-log.md D-82, D-83 (PR #48, f03372c); D-85: the PM (Lead) in the layout study's group, 2026-10-31 (the decision log follows)"),
    "S39": ("Tonight's PM rulings: D-63 (40 x 40 corner edge tubes, +1.3 kg), D-69 (wall trays take 12 mm lips, +0.43 kg each), D-71 (the running estimate and what it leaves out), D-72 (9 mm plywood floor), D-76 (3 mm firm foam mat, about 2.1 kg)", "PR #35 (49e2d94): v2/00-Control/decision-log.md, D-61 to D-78; the Mechanical Checker's F-010 (PR #25)"),
    "S19": ("LTL overlength rules: most carriers start excessive-length charges for a piece over 96 in (summary; check each carrier's rules tariff)", "https://logisticsplus.com/?p=25575 (read 2026-10-31)"),
}

# ---------------------------------------------------------------- values
@dataclass(frozen=True)
class V:
    value: float
    unit: str
    status: str
    source: str
    note: str = ""


P = {
    # ---- pod envelope (look stays the same)
    "pod_w": V(2500, "mm", "confirmed", "S04, D-01", "overall width X"),
    "pod_d": V(1700, "mm", "confirmed", "S04, D-01", "overall depth Y"),
    "pod_h": V(2400, "mm", "confirmed", "S04, D-21", "overall height Z, room floor to the top of the roof skin"),
    "decor_depth": V(205, "mm", "confirmed", "D-49 (replaces D-39; S32)", "front decor block depth as v1: v1 decor-frame drawing and STEP, Y -850 to -645 (D-39's 230-235 came from the v1 BOM; the plan said 200)"),
    "wall_depth": V(1495, "mm", "confirmed", "D-49 (S32)", "side walls start at the decor back plate (Y -645), as v1 (1496); was 1500 = 1700 - 200"),
    "acp_t": V(3, "mm", "source", "S23", "ACP skin thickness (Alcorest 3 mm)"),
    "wall_t_plan": V(38, "mm", "source", "S04", "3 ACP + 6 ply + 20 tube + 9 PET (plan joint detail)"),
    "base_h": V(100, "mm", "source", "S04", "base band: 50x100 tube on edge"),
    "glide_h": V(10, "mm", "assumption", "S04", "foot/glide height below the base band"),
    # ---- material densities
    "rho_steel": V(7850, "kg/m3", "source", "S06"),
    "rho_al": V(2700, "kg/m3", "source", "S07"),
    "rho_glass": V(2500, "kg/m3", "source", "S08"),
    "rho_pmma": V(1190, "kg/m3", "source", "S09"),
    "rho_ply": V(600, "kg/m3", "assumption", "S13", "plywood/board; range 540-660 used for the v1 range"),
    "rho_ply_lo": V(540, "kg/m3", "assumption", "S13"),
    "rho_ply_hi": V(660, "kg/m3", "assumption", "S13"),
    "rho_timber": V(550, "kg/m3", "assumption", "S13", "v1 40x40 frame timber, species not stated"),
    "rho_timber_lo": V(500, "kg/m3", "assumption", "S13"),
    "rho_timber_hi": V(600, "kg/m3", "assumption", "S13"),
    "pvb_kgm2": V(0.81, "kg/m2", "calculation", "S08", "0.76 mm PVB at 1070 kg/m3 (assumption on PVB density)"),
    # ---- sheet products (areal mass)
    "acp2_kgm2": V(2.9, "kg/m2", "source", "S10", "2 mm ACP"),
    "acp3_kgm2": V(3.5, "kg/m2", "calculation", "S23, S24", "Spaceship: 3 mm Alcorest EV3038 ACP, 0.21 mm skins; the sound study's figure from the skin spec, used by PM ruling (was 3.8); the maker publishes no kg/m2"),
    "acp3_v1_kgm2": V(3.8, "kg/m2", "source", "S10", "v1's 3 mm decor skins: maker unknown, kept at the 0.3 mm-skin figure"),
    "pet9_kgm2": V(1.8, "kg/m2", "source", "S11", "9 mm PET felt"),
    "felt_t": V(9, "mm", "confirmed", "D-17", "PET felt on the lining cassette's face (the factory's felt, tested in the wall sample first, D-31)"),
    "hc10_kgm2": V(4.0, "kg/m2", "source", "S12", "10 mm Al honeycomb, 0.5+0.5 skins"),
    "foam25_kgm2": V(1.5, "kg/m2", "assumption", "", "25 mm closed-cell foam core at about 60 kg/m3; the sound group picks the core"),
    "al05_kgm2": V(1.35, "kg/m2", "calculation", "S07", "0.5 mm aluminium inner skin"),
    "bond_kgm2": V(0.25, "kg/m2", "assumption", "", "factory bond line or structural tape, per bonded face"),
    "felt_fix_kgm2": V(0.05, "kg/m2", "assumption", "", "Velcro strips on felt panels"),
    # ---- tube wall thicknesses (not given in the plan)
    "t_steel_20": V(1.2, "mm", "assumption", "S04", "VT10 20x20 steel tube; plan gives no wall thickness"),
    "t_steel_50x100": V(2.0, "mm", "calculation", "S02", "v1 STEP: volume/length of the 100x50 rails gives 2.0 mm"),
    "t_steel_30x60": V(1.4, "mm", "assumption", "S04", "VT04 30x60 joists"),
    "t_steel_16": V(1.0, "mm", "assumption", "S01", "v1 decor 16x16 tube (STEP models these as solid bars)"),
    "t_steel_60x20": V(1.2, "mm", "assumption", "S01"),
    "t_steel_20_v1": V(1.0, "mm", "assumption", "S01"),
    "t_steel_d100": V(2.0, "mm", "assumption", "S01", "v1 table leg tube"),
    "t_al_20": V(1.5, "mm", "assumption", "S07", "20x20 aluminium tube for light frames"),
    "t_al_base": V(2.0, "mm", "assumption", "S07", "aluminium 100x40 base rail (the base band)"),
    # ---- frames
    "stud_pitch_ply": V(600, "mm", "assumption", "", "max frame member spacing with plywood backing"),
    "stud_pitch_acp": V(400, "mm", "confirmed", "D-16", "max spacing when ACP is bonded to the frame without plywood, to keep it flat (oil-canning risk)"),
    # ---- glass and front
    "glass_door_w": V(1176, "mm", "source", "S01"),
    "glass_door_h": V(2011, "mm", "source", "S01"),
    "glass_fixed_w": V(724, "mm", "source", "S01", "cut rectangle; real shape is bevelled to the decor"),
    "glass_fixed_h": V(2139, "mm", "source", "S01"),
    "glass_door_area_step": V(2.110, "m2", "calculation", "S02", "STEP solid volume / thickness"),
    "glass_fixed_area_step": V(1.370, "m2", "calculation", "S02", "STEP solid volume / thickness"),
    # ---- bought parts and allowances (the hardware group pins real SKUs)
    "fan_kg": V(1.5, "kg", "unverified", "S04", "Panasonic FV-15AUL1; weight not published on the pages read"),
    "fan_v1_kg": V(1.0, "kg", "assumption", "S01", "v1 200x200x60 fan"),
    "silencer_kg": V(1.5, "kg", "assumption", "S05", "one silenced vent box per fan (air group designs it)"),
    "light_kg": V(0.5, "kg", "assumption", "S01", "170x170 LED ceiling light"),
    "plate_kg": V(0.15, "kg", "assumption", "S04", "UTEN S300 switch/socket/dimmer/LAN set, each"),
    "harness_kg": V(1.5, "kg", "assumption", "", "wiring, connectors at panel seams, inlet"),
    "sensor_kg": V(0.1, "kg", "assumption", "S05", "occupancy sensor for automatic fans"),
    "foot_kg": V(0.25, "kg", "assumption", "S04", "M10 levelling foot D50"),
    "glide_kg": V(0.15, "kg", "assumption", "", "levelling glide adjusted from above"),
    "hinge_kg": V(0.6, "kg", "assumption", "S01", "glass door hinge, each"),
    "handle_kg": V(0.8, "kg", "assumption", "S01", "300 mm glass door pull"),
    "drop_seal_kg": V(0.6, "kg", "assumption", "S05", "automatic door bottom"),
    "glazing_profile_kgm": V(0.45, "kg/m", "assumption", "S05", "aluminium U-profile with gasket for fixed glass"),
    "gasket_kgm": V(0.06, "kg/m", "assumption", "S05", "EPDM/foam gasket on panel joints"),
    "fill_kgm2": V(0.6, "kg/m2", "assumption", "S05", "20 mm PET cavity fill at 30 kg/m3 (light; sound group sizes it)"),
    "bolt_kg": V(0.012, "kg", "assumption", "", "M6 bolt + washer + rivnut"),
    "bolt_pitch": V(400, "mm", "assumption", "", "bolt spacing used only to count bolts; the joint register sets real pitches"),
    "voice_kit_kg": V(4.0, "kg", "assumption", "D-11", "reserve for the later voice cockpit kit: mic array, speakers, screen, status light"),
    "voice_kit_w": V(60, "W", "confirmed", "D-11", "12 V 5 A for the voice cockpit kit on the 12 V bus (D-10)"),
    "table_v1_kg": V(0, "kg", "calculation", "S01", "computed from the BOM in v1_weights.py"),
    # ---- shipping
    "pal_std_l": V(1219, "mm", "confirmed", "S05", "48 in"),
    "pal_std_w": V(1016, "mm", "confirmed", "S05", "40 in"),
    "pal_std_h": V(121, "mm", "source", "S14", "4.75 in"),
    "pal_std_kg": V(20.0, "kg", "source", "S14", "44 lb"),
    "pal_long_l": V(2438, "mm", "confirmed", "S05", "96 in"),
    "pal_long_w": V(1219, "mm", "confirmed", "S05", "48 in"),
    "pal_long_h": V(121, "mm", "assumption", "S15", "3.5 in stringer + 2 x 0.5 in decks = 4.5 in; 4.75 in used"),
    "pal_long_kg": V(48.5, "kg", "source", "S15", "107 lb"),
    "max_load_h": V(1829, "mm", "confirmed", "S05", "about 6 ft loaded height"),
    "overlength": V(2438, "mm", "source", "S19", "96 in: pieces longer than this trigger overlength charges at most LTL carriers"),
    "edge_board": V(10, "mm", "assumption", "", "edge protector at each end of an upright stack"),
    "glass_pack_h": V(50, "mm", "assumption", "", "two lites flat with foam in a timber edge frame"),
    "sheet_under_glass": V(12, "mm", "assumption", "", "ply sheet between the decor layer and the glass frame"),
    "pack_cap_h": V(25, "mm", "assumption", "", "top cap board and corner protection"),
    "pack_gap": V(4, "mm", "assumption", "", "foam interleaf between upright panels"),
    "pack_kg_std": V(6.0, "kg", "assumption", "", "corner boards, foam, straps, film per 48x40 pallet"),
    "pack_kg_long": V(9.0, "kg", "assumption", "", "same for a 96x48 pallet"),
    "glass_frame_kg": V(18.0, "kg", "assumption", "", "timber A-frame/edge frame holding the glass on the long pallet"),
    # ---- doorway
    "door_w": V(914, "mm", "confirmed", "S05", "36 in nominal doorway"),
    "door_h": V(2032, "mm", "confirmed", "S05", "80 in nominal doorway"),
    "door_clear_w": V(813, "mm", "source", "S17", "32 in minimum clear width"),
    "hand_clear": V(40, "mm", "assumption", "", "room for fingers each side when carrying a part on edge"),
    # ---- assembly time
    "t_bolt_s": V(30, "s", "assumption", "", "one M6 bolt into a rivnut with a T-handle hex key, panel already on its pins"),
    "t_carry_s": V(45, "s", "assumption", "", "carry one part from the pallet to its place"),
    "t_place_s": V(45, "s", "assumption", "", "set one wall/floor part on its locating pins"),
    "t_place_overhead_s": V(120, "s", "assumption", "", "lift and set one ceiling half, 2 people, step stool"),
    "t_felt_s": V(60, "s", "assumption", "", "press one felt panel onto its Velcro"),
    "t_unpack_std_min": V(8, "min", "assumption", "", "open one 48x40 pallet and lay parts out by label"),
    "t_unpack_long_min": V(12, "min", "assumption", "", "open the long pallet and stand the glass safely"),
    "t_level_min": V(10, "min", "assumption", "", "level the base with glides and a spirit level"),
    "t_fixed_glass_min": V(12, "min", "assumption", "", "set fixed glass into its sealed profiles, 2 people"),
    "t_door_min": V(18, "min", "assumption", "", "hang the glass door, adjust, fit handle and drop seal, 2 people"),
    "t_elec_min": V(10, "min", "assumption", "", "plug seam connectors and power, test fans and lights"),
    "t_final_min": V(10, "min", "assumption", "", "check door swing and seals, clean"),
    "t_connector_s": V(20, "s", "assumption", "", "mate one plug-in cable connector at a panel seam"),
    "inefficiency": V(0.15, "-", "assumption", "", "added to elapsed time for hand-offs and checking"),
    # ---- levers towards about 1 hour (each an assumption until timed on the prototype)
    "cam_seams": V(0, "flag", "assumption", "", "1 = panel-to-panel seams use tool-free cam or clip connectors instead of bolts"),
    "t_cam_s": V(10, "s", "assumption", "", "close one cam or clip connector by hand"),
    "t_bolt_captive_s": V(18, "s", "assumption", "", "captive M6 bolt already started in its panel: no picking up, no dropping"),
    "t_place_hung_s": V(20, "s", "assumption", "", "panel hung on hooks or seated on pins holds itself: no second person holding"),
    "t_door_prehung_min": V(6, "min", "assumption", "", "door arrives hung on the left decor post: set the post, check swing"),
    "t_fixed_preglazed_min": V(5, "min", "assumption", "", "fixed glass arrives in its profile frame: set and fix the frame"),
    "t_unpack_std_ordered_min": V(4, "min", "assumption", "", "48x40 packed in assembly order, parts numbered"),
    "t_unpack_long_ordered_min": V(6, "min", "assumption", "", "long pallet packed in assembly order"),
    "t_felt_strip_s": V(20, "s", "assumption", "", "felt pre-fitted on its panel; only the strip over a joint goes on site"),
    "cam_kg": V(0.05, "kg", "assumption", "", "one cam or clip connector pair"),
    "kick_strip_kg": V(1.0, "kg", "assumption", "S29, D-56", "aluminium kick strip at the door bottom, base band finish, houses the drop seal; the PM's 'about 1 kg'"),
    "kick_strip_h": V(85, "mm", "confirmed", "D-40, D-57", "v1's front drops 17 mm to the 2400 datum, so the door bottom sits at Z 105 and the strip is 85 tall (D-40 said about 90)"),
    "kick_strip_d": V(20, "mm", "assumption", "S32", "kick strip envelope depth, as the skeleton's kick_d (D-40 gives the height only)"),
    "strip_w": V(150, "mm", "assumption", "", "loose felt strip over each joint, so the joint stays reachable"),
    # ---- quiet build re-check (Lead's ruling 2026-10-31: about 380 kg, acrylic front, deeper filled cavities)
    "frame_depth": V(20, "mm", "source", "S04", "wall frame tube depth (20x20); the quiet build deepens it"),
    "quiet_total": V(380, "kg", "confirmed", "D-02 (replaced by D-27)", "history: the PM's target from the Hardware Engineer's sound curve, before the final stack"),
    "hw_380_total": V(377, "kg", "source", "S20", "Hardware Engineer's best build within a 380 kg budget"),
    "hw_380_dsa": V(22.5, "dB", "source", "S20", "its central D_S,A estimate"),
    "quiet_cap": V(400, "kg", "confirmed", "D-02 (replaced by D-37)", "history: heavier walls allowed up to 400 kg in total"),
    "rho_mass_layer": V(1600, "kg/m3", "assumption", "", "dense sound layer (MLV-like) used only to size the inner leaf thickness"),
    "leaf_clip_kgm2": V(0.6, "kg/m2", "assumption", "", "clip rail and clips of an inner leaf"),
    "ceil_t": V(0, "mm", "assumption", "", "ceiling thickness; 0 means the same as the walls"),
    "final_wall_t": V(81, "mm", "confirmed", "D-16, D-42", "final wall: outer panel 3 + 40, cassette 25 + 9, 4 mm gaps"),
    "final_ceil_t": V(81, "mm", "confirmed", "D-42", "the ceiling uses the wall stack"),
    "final_wall_depth": V(40, "mm", "confirmed", "D-16, D-34", "20x40 aluminium wall frame"),
    "final_ceil_depth": V(40, "mm", "confirmed", "D-42", "20x40 aluminium ceiling frame (replaces D-16's 20x100 and D-27's 53 mm ceiling)"),
    "lin_gap": V(4, "mm", "assumption", "D-57 (S32)", "gap between the roof frame and the upper side linings, so they float; the same 4 mm as the stack gap"),
    "final_kgm2_hw": V(12.6, "kg/m2", "calculation", "S31", "the sound study's wall and ceiling mass with frame, 32 kg/m3 fill, cassette and felt"),
    "fill_pet_kgm3": V(32, "kg/m3", "confirmed", "D-54 (S30, S31)", "Pyrotek Sorberpoly 2D; D-34's 25 kg/m3 needs absorption data that isn't published, so its condition moves to the wall sample"),
    "fill_pet_light_kgm3": V(25, "kg/m3", "source", "D-34, D-54", "the lighter fill: the wall sample tests it next to the 32, and the pod switches if it matches on sound"),
    "t_al_final": V(1.2, "mm", "confirmed", "D-34, D-54", "wall of the 20x40 aluminium frames (was 1.5); the rivnut grip check passed, which settles D-34's frame condition"),
    "tray_t": V(0.5, "mm", "confirmed", "D-37", "steel lining tray (0.4 mm cost 1 dB, so back to 0.5)"),
    "tray_t_thin": V(0.4, "mm", "confirmed", "D-35 (replaced by D-37)", "the thinner tray tried and dropped"),
    "tray_depth": V(25, "mm", "confirmed", "D-17", "tray returns and the air gap behind the felt"),
    "hw_385_total": V(385, "kg", "source", "S21"),
    "hw_385_dsa": V(24.2, "dB", "source", "S21"),
    "hw_400_total": V(400, "kg", "source", "S22", "sound study's total with 4+4 laminated glass"),
    "hw_400_dsa": V(23.8, "dB", "source", "S22"),
    "cap_kg": V(420, "kg", "confirmed", "D-37, D-54", "weight cap with the 0.5 mm tray; the study's estimate stays open against it until the wall sample"),
    "hw_total": V(417.5, "kg", "calculation", "S31", "the sound and air check's decided build in its own model ('about 418 kg')"),
    "hw_shell_kg": V(201.6, "kg", "calculation", "S31", "its walls and ceiling: 12.63 kg/m2 x (12.33 + 3.64) m2 of outside area, cassettes and felt included"),
    "hw_glass_kg": V(71.9, "kg", "calculation", "S31", "its glass: 21 kg/m2 x 3.425 m2"),
    "hw_air_kg": V(45.0, "kg", "calculation", "S31", "its cartridges 34.2, riser 9.6 and four fans 1.2"),
    "hw_rest_kg": V(99.0, "kg", "calculation", "S31", "its rest of the pod: 102.4 from an older copy of this study, plus 2.6 of fixes, less 6.0 of that copy's fans and boxes"),
    "fan12_kg": V(0.3, "kg", "assumption", "S30, D-51", "Noctua NF-A14 industrialPPC-3000 PWM, 12 V, 140 x 140 x 25 mm; weight not published: weigh the sample"),
    "cart_kg": V(17.1, "kg", "calculation", "S30, D-51", "one splitter cartridge with its 40 mm fill toward the pod, without fans"),
    "cart_d": V(159, "mm", "calculation", "S30", "cartridge depth: three 25 mm layers, two 40 mm passages, 2 mm casing"),
    "cart_w": V(405, "mm", "calculation", "S30", "cartridge width: two cartridges and the riser side by side in the right block"),
    "cart_l": V(1800, "mm", "calculation", "S30", "lined passage length"),
    "fanbox_l": V(300, "mm", "calculation", "S30", "lined fan box at one end of the cartridge, 2 fans on a bulkhead"),
    "riser_kg": V(9.6, "kg", "calculation", "S30, D-51", "exhaust riser, 1 mm galvanised steel"),
    "riser_w": V(150, "mm", "calculation", "S30", "the 150 mm exhaust riser"),
    "riser_d": V(155, "mm", "calculation", "S30", "riser depth, the cartridges' layer stack"),
    "riser_l": V(2000, "mm", "calculation", "S30", "from the exhaust fans at the foot to the slot on the block's top face"),
    "door_edge_seal_kg": V(1.0, "kg", "source", "S20", "door edge seals on 3 sides"),
    "base_seal_kg": V(0.5, "kg", "source", "S20", "seal under the thin floor and band"),
    "grommet_kg": V(0.1, "kg", "source", "S20", "sealed cable holes"),
    "t_leaf_s": V(60, "s", "assumption", "", "clip one inner leaf (sound mass + felt) onto its frame from inside"),
}


_OVERRIDE = {}


def p(name):
    """Value of a parameter (or of a temporary override used for what-if levers)."""
    if name in _OVERRIDE:
        return _OVERRIDE[name]
    return P[name].value


class override:
    """with override(t_door_min=6): ... runs the model with changed assumptions.

    Nests safely: on exit each key goes back to the value it had before (an outer override's value, or none)."""

    _MISSING = object()

    def __init__(self, **kw):
        self.kw = kw
        self.saved = {}

    def __enter__(self):
        self.saved = {k: _OVERRIDE.get(k, self._MISSING) for k in self.kw}
        _OVERRIDE.update(self.kw)

    def __exit__(self, *exc):
        for k, old in self.saved.items():
            if old is self._MISSING:
                _OVERRIDE.pop(k, None)
            else:
                _OVERRIDE[k] = old


SPACESHIP_NOTE = "Spaceship is the working name of v2 (folders keep their v2 names)."
