"""Every input number of the layout study, with its status and source.

Status words follow the guideline (section 10): confirmed, source, calculation,
assumption, unverified. Nothing in the other scripts may introduce a number that
is not either defined here or calculated from what is defined here, except plain
counts that the scripts state next to the code (for example "2 hinges").
"""
from dataclasses import dataclass

# ---------------------------------------------------------------- sources
SOURCES = {
    "S01": ("v1 materials BOM, v5, 2026-10-29", "sources/v1/indoor-pod-v3-bom-v5-2026-10-29.xlsx"),
    "S02": ("v1 STEP assembly, exported 2026-10-14 (older than the BOM; cross-check only)", "sources/v1/indoor-pod-v3-assembly.step"),
    "S03": ("v1 drawings: wood parts, floor frame, decor frame", "sources/v1/drawings/"),
    "S04": ("v2 build plan from the indoor pod lead engineer", "v2/00-Control/v2-build-plan.pdf"),
    "S05": ("v2 plan approved by Dee, 2026-10-31 (targets, light options, pallet sizes)", "v2/PLAN.md"),
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
    "S25": ("Sound study update relayed by the PM, 2026-10-31: silencers move inside the decor blocks as splitter silencers with 2 mm aluminium casings, 18 kg in the right block and 9 kg in the top block, next to the S&P TD-500 fans; weight win-backs: 20x40x1.2 aluminium frames and 25 kg/m3 fill; expected total about 398 kg", "layout conversation, PM message of 2026-10-31"),
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
    "pod_w": V(2500, "mm", "confirmed", "S04", "overall width X"),
    "pod_d": V(1700, "mm", "confirmed", "S04", "overall depth Y"),
    "pod_h": V(2400, "mm", "confirmed", "S04", "overall height Z"),
    "decor_depth": V(200, "mm", "confirmed", "S04", "front decor frame depth"),
    "wall_depth": V(1500, "mm", "confirmed", "S04", "side wall depth = 1700 - 200"),
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
    "acp3_kgm2": V(3.5, "kg/m2", "calculation", "S23", "Spaceship: 3 mm Alcorest EV3038 ACP, 0.21 mm skins (PM ruling; was 3.8)"),
    "acp3_v1_kgm2": V(3.8, "kg/m2", "source", "S10", "v1's 3 mm decor skins: maker unknown, kept at the 0.3 mm-skin figure"),
    "pet9_kgm2": V(1.8, "kg/m2", "source", "S11", "9 mm PET felt"),
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
    "stud_pitch_acp": V(400, "mm", "assumption", "", "max spacing when ACP is bonded to the frame without plywood, to keep it flat (oil-canning risk)"),
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
    "voice_kit_kg": V(4.0, "kg", "assumption", "", "reserve for the later voice cockpit kit: mic array, speakers, screen, status light"),
    "voice_kit_w": V(60, "W", "assumption", "", "power reserve for the voice cockpit kit"),
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
    "strip_w": V(150, "mm", "assumption", "", "loose felt strip over each joint, so the joint stays reachable"),
    # ---- quiet build re-check (Lead's ruling 2026-10-31: about 380 kg, acrylic front, deeper filled cavities)
    "frame_depth": V(20, "mm", "source", "S04", "wall frame tube depth (20x20); the quiet build deepens it"),
    "quiet_total": V(380, "kg", "confirmed", "S20", "PM ruling from the Hardware Engineer's sound curve"),
    "hw_380_total": V(377, "kg", "source", "S20", "Hardware Engineer's best build within a 380 kg budget"),
    "hw_380_dsa": V(22.5, "dB", "source", "S20", "its central D_S,A estimate"),
    "quiet_cap": V(400, "kg", "confirmed", "", "Lead's ruling: heavier walls allowed up to 400 kg in total"),
    "rho_mass_layer": V(1600, "kg/m3", "assumption", "", "dense sound layer (MLV-like) used only to size the inner leaf thickness"),
    "leaf_clip_kgm2": V(0.6, "kg/m2", "assumption", "", "clip rail and clips of an inner leaf"),
    "ceil_t": V(0, "mm", "assumption", "", "ceiling thickness; 0 means the same as the walls"),
    "final_wall_t": V(81, "mm", "source", "S21", "final wall: outer panel 3 + 40, cassette 25 + 9, 4 mm gaps"),
    "final_ceil_t": V(81, "mm", "calculation", "S22", "40 mm ceiling frames: the same 81 mm stack as the walls"),
    "final_wall_depth": V(40, "mm", "source", "S21", "20x40 aluminium wall frame"),
    "final_ceil_depth": V(40, "mm", "source", "S22", "20x40 aluminium ceiling frame (was 20x100)"),
    "final_kgm2_hw": V(13.1, "kg/m2", "source", "S21", "the sound study's wall mass with frame, fill and cassette"),
    "fill_pet_kgm3": V(25, "kg/m3", "source", "S25", "PET cavity fill (was 32)"),
    "t_al_final": V(1.2, "mm", "source", "S25", "wall of the 20x40 aluminium frames in the final stack (was 1.5)"),
    "tray_t": V(0.5, "mm", "source", "S21", "steel lining tray"),
    "tray_depth": V(25, "mm", "source", "S21"),
    "hw_385_total": V(385, "kg", "source", "S21"),
    "hw_385_dsa": V(24.2, "dB", "source", "S21"),
    "hw_400_total": V(400, "kg", "source", "S22", "sound study's total with 4+4 laminated glass"),
    "hw_400_dsa": V(23.8, "dB", "source", "S22"),
    "carry_total": V(400, "kg", "confirmed", "S24", "total to carry until the CAD parts list"),
    "carry_tol": V(10, "kg", "confirmed", "S24"),
    "fan_final_kg": V(6.0, "kg", "source", "S20", "S&P TD-500/150-160 ECOWATT inline fan (sound study's fan table)"),
    "sil_right_kg": V(18.0, "kg", "source", "S25", "splitter silencer in the right decor block, 2 mm aluminium casing"),
    "sil_top_kg": V(9.0, "kg", "source", "S25", "splitter silencer in the top decor block"),
    "decor_fill_m2": V(1.65, "m2", "calculation", "S20", "decor faces lined with 75 mm PET fill"),
    "door_edge_seal_kg": V(1.0, "kg", "source", "S20", "door edge seals on 3 sides"),
    "base_seal_kg": V(0.5, "kg", "source", "S20", "seal under the thin floor and band"),
    "grommet_kg": V(0.1, "kg", "source", "S20", "sealed cable holes"),
    "hw_398_total": V(398, "kg", "source", "S25", "sound study's expected total after the update"),
    "t_leaf_s": V(60, "s", "assumption", "", "clip one inner leaf (sound mass + felt) onto its frame from inside"),
}


_OVERRIDE = {}


def p(name):
    """Value of a parameter (or of a temporary override used for what-if levers)."""
    if name in _OVERRIDE:
        return _OVERRIDE[name]
    return P[name].value


class override:
    """with override(t_door_min=6): ... runs the model with changed assumptions."""

    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        _OVERRIDE.update(self.kw)

    def __exit__(self, *exc):
        for k in self.kw:
            _OVERRIDE.pop(k, None)


SPACESHIP_NOTE = "Spaceship is the working name of v2 (folders keep their v2 names)."
