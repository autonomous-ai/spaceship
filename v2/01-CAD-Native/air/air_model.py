"""Spaceship (FocusPod v2) AIR (D-60, D-61): parameters and layout, without Fusion.

The air column in the front-right inside corner, the soffit above the door head,
the splitter cartridge in each, the two fan boxes, the intake riser, the grilles
and the roof sleeve. Every size is a named parameter: the skeleton's own list
(loaded from its CSV, the highest revision in ../skeleton/), the ceiling's
cassette front edge (the soffit depth), and the AIR parameters below, each with
its status and source. Sizes come from the PM's rulings D-60 to D-62 and the
air report section 7e (v2/05-Engineering/acoustics-air/report.md, sized on
skeleton P04); where the report gives a position it is tied to the skeleton
here, so the parts follow it.

Coordinates: the pod system (conventions.md section 4), mm.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import ceiling_model as CM  # noqa: E402  (skeleton loader and expression tools)

REV = "P01"
R7E = "air report 7e (sized on skeleton P04)"

AIR_PARAMS = [
    # ---- floor and linings (PM rulings 2026-11-01 from BASE)
    ("mat_t", "3 mm", "mm", "confirmed", "PM ruling 2026-11-01 (BASE): a 3 mm mat over the 9 mm ply, so the floor top is Z 12; the skeleton's own value replaces this one once it carries it"),
    ("col_gap", "5 mm", "mm", "confirmed", "PM ruling 2026-11-01 (BASE): the column keeps 5 mm off the floating side lining (D-17), X up to 1161; the soffit's ends the same"),
    # ---- faces of the column and the soffit
    ("face_acp", "3 mm", "mm", "source", R7E + ": faces 3 mm ACP + 9 mm felt"),
    ("face_felt", "9 mm", "mm", "source", R7E + ": faces 3 mm ACP + 9 mm felt"),
    ("face_t", "face_acp + face_felt", "mm", "calculation", "12 mm felt-covered face"),
    ("clr", "5 mm", "mm", "source", R7E + ": 5 mm round each cartridge and fan box, to slide it out"),
    # ---- column (front-right inside corner)
    ("col_x0", "949 mm", "mm", "source", R7E + ": the column's left face, X 949 (220 wide on P03, 217 on P04)"),
    ("col_d", "360 mm", "mm", "confirmed", "D-61: 360 deep, flush with the soffit's face"),
    ("plen_lo", "120 mm", "mm", "source", R7E + ": base plenum Z 15 to 135 under the cartridge"),
    ("grille_h", "100 mm", "mm", "confirmed", "D-61: a 100 mm kick grille at the column's foot"),
    ("grille_z", "10 mm", "mm", "source", R7E + ": kick grille Z 25 to 125, 10 mm above the column's foot"),
    ("grille_l", "312 mm", "mm", "source", R7E + ": 529 along the front and left faces, 217 of it on the front"),
    ("grille_t", "2 mm", "mm", "assumption", "perforated aluminium grille plates, flush with the room-side face; free area per the report, pattern HOLD"),
    ("hub_w", "180 mm", "mm", "confirmed", "D-61, D-70: a 180 x 180 zone for the sensor hub and controls"),
    ("hub_t", "29 mm", "mm", "source", R7E + ": up to 29 deep, no fill behind it"),
    ("hub_z", "1200 mm", "mm", "source", R7E + ": zone centred at Z 1200; across, it is centred between the front corner angles (X 1063.5 on P04, the report's 1058 is the column's centre)"),
    ("chase_w", "30 mm", "mm", "source", R7E + ": a 30 x 30 cable chase in the column's front-left corner"),
    ("foot_t", "2 mm", "mm", "assumption", "column foot plate, aluminium; it closes the base plenum and takes BASE's two spigots"),
    ("spg1_x", "989 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S1 on F2 (X 989, Y -605), into a round hole"),
    ("spg1_y", "-605 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S1 on F2"),
    ("spg2_x", "1126 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S2 on F2 (X 1126, Y -337), into a slot"),
    ("spg2_y", "-337 mm", "mm", "confirmed", "PM ruling 2026-11-01: BASE's spigot S2 on F2"),
    ("spg_hole", "8.5 mm", "mm", "confirmed", "R-J13 rule for spigots: 8.5 round at one, 8.5 x 14 slot at the other (along Y here)"),
    ("spg_slot", "14 mm", "mm", "confirmed", "R-J13: slot length"),
    ("plate_t", "1 mm", "mm", "assumption", "aluminium plates closing the column's right side at the two plenums, now that the column stands 5 mm off the lining"),
    ("hook_x", "971 mm", "mm", "confirmed", "PM ruling 2026-11-01: the column's two hook studs in DR's access panel at X 971 (FRONT's parts)"),
    ("hook_z1", "1700 mm", "mm", "confirmed", "PM ruling 2026-11-01: lower hook stud Z 1700"),
    ("hook_z2", "1850 mm", "mm", "confirmed", "PM ruling 2026-11-01: upper hook stud Z 1850"),
    ("key_d", "12 mm", "mm", "assumption", "keyhole's big hole, for a 10 mm stud head"),
    ("key_w", "6.5 mm", "mm", "assumption", "keyhole's slot and the rails' forks, for a 6 mm stud shank"),
    ("key_drop", "10 mm", "mm", "confirmed", "PM ruling 2026-11-01: the column drops 10 mm onto its studs and BASE's spigots"),
    ("ang_w", "20 mm", "mm", "assumption", "corner angle leg along the side faces; the report says 4 corner angles, size not given"),
    ("ang_f", "9 mm", "mm", "assumption", "corner angle leg along the front face: short, so the 180 hub zone fits between the two front corners (212 - 12 - 2 x 9 = 182)"),
    ("ang_t", "2 mm", "mm", "assumption", "corner angle thickness, aluminium"),
    # ---- cartridge (one part for both paths, D-61)
    ("cart_w", "173 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_d", "314 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_l", "1750 mm", "mm", "confirmed", "D-61: one cartridge 173 x 314 x 1750"),
    ("cart_t", "2 mm", "mm", "confirmed", "D-61: 2 mm aluminium casing"),
    ("lay_t", "50 mm", "mm", "confirmed", "D-61: three 50 mm absorbent layers (Pyrotek Sorberpoly 2D, report 7e)"),
    ("pass_w", "(cart_d - 2 * cart_t - 3 * lay_t) / 2", "mm", "calculation", "D-61: two 80 mm passages"),
    # ---- soffit (above the door head)
    ("sof_h", "220 mm", "mm", "confirmed", "D-61: soffit 220 tall, Z 2120 to 2340"),
    ("eg_x0", "16 mm", "mm", "source", R7E + ": exhaust grille from X -1150, 16 in from the soffit's left end"),
    ("eg_l", "265 mm", "mm", "source", R7E + ": exhaust grille 265 x 336"),
    ("eg_w", "336 mm", "mm", "source", R7E + ": exhaust grille 265 x 336"),
    ("fb_w", "294 mm", "mm", "source", R7E + ": exhaust fans and box 294 x 314 x 173"),
    ("sof_fill_t", "27 mm", "mm", "source", R7E + ": the exhaust cartridge sits on 27 mm of fill over the underside (Z 2159), as in the column"),
    ("lin_t", "50 mm", "mm", "source", R7E + ": fan boxes lined with 50 mm"),
    ("box_t", "2 mm", "mm", "source", R7E + ": fan boxes in 2 mm aluminium"),
    # ---- soffit hanging (D-87; PM ruling 2026-11-01): open forks in two top rails on 4 studs in
    #      the ceiling frame, lift and slide toward the door, 2 captive lock screws; the underside
    #      in two hinged sections and a fixed strip over the column
    ("rail_t", "3 mm", "mm", "assumption", "soffit top rails, aluminium flat bar"),
    ("rail_w", "24 mm", "mm", "assumption", "soffit top rail width: holds the 6.5 fork with 8 each side, and the door-side rail stays 1 mm clear of the roof sleeve"),
    ("hd_h", "4 mm", "mm", "assumption", "hanger stud and lock screw head space under the rails"),
    ("stud_d", "10 mm", "mm", "assumption", "hanger stud head, HOLD (joints register to number it, D-63)"),
    ("slide", "24 mm", "mm", "calculation", "the soffit is lifted this far behind its place and slid toward the door: the studs start clear of both rails' edges"),
    ("us_gap", "2 mm", "mm", "assumption", "gap between the underside sections"),
    ("hinge_l", "60 mm", "mm", "assumption", "hinge envelope along the door-side edge, HOLD"),
    ("latch_l", "30 mm", "mm", "assumption", "push latch envelope at the room-side edge, HOLD"),
    ("hl_h", "8 mm", "mm", "assumption", "hinge and latch envelope height above the underside"),
    # ---- fans (selection F1, D-51)
    ("fan_s", "140 mm", "mm", "source", "Noctua NF-A14 industrialPPC-3000 PWM: 140 x 140 x 25 (selection F1)"),
    ("fan_t", "25 mm", "mm", "source", "Noctua NF-A14 industrialPPC-3000 PWM: 140 x 140 x 25 (selection F1)"),
    # ---- supply fan box and intake riser, inside the right decor block (D-61, D-62)
    ("sb_x0", "645 mm", "mm", "source", R7E + ": supply fan box X 645 to 945"),
    ("sb_w", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_d", "155 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_h", "300 mm", "mm", "source", R7E + ": supply fan box 300 x 155 x 300"),
    ("sb_yf", "3 mm", "mm", "source", R7E + ": supply fan box from Y -847, 3 behind the decor's front face"),
    ("sb_z0", "1650 mm", "mm", "source", R7E + ": supply fan box Z 1650 to 1950"),
    ("op_x0", "961 mm", "mm", "source", R7E + ": opening from the block into the column top X 961 to 1161, Z 1895 to 2110"),
    ("op_z0", "1895 mm", "mm", "source", R7E + ": opening Z 1895 to 2110"),
    ("op_h", "215 mm", "mm", "source", R7E + ": opening 200 x 215"),
    ("rs_x0", "955 mm", "mm", "source", R7E + ": intake riser X 955 to 1094"),
    ("rs_w", "139 mm", "mm", "source", R7E + ": intake riser 139 wide, 155 deep"),
    ("rs_d", "155 mm", "mm", "source", R7E + ": intake riser 139 wide, 155 deep"),
    ("rs_y0", "-803 mm", "mm", "source", R7E + ": intake riser Y -803 to -648"),
    ("rs_z0", "105 mm", "mm", "source", R7E + ": intake riser Z 105 to 1445"),
    ("rs_z1", "1445 mm", "mm", "source", R7E + ": intake riser Z 105 to 1445, then it widens into the fan box below Z 1650"),
    ("rs_t", "1 mm", "mm", "confirmed", "D-61: 1 mm steel intake riser"),
    # ---- roof slot, sleeve and grille (D-61: Y -620 to -326, in the right outer ceiling panel)
    ("slv_t", "1 mm", "mm", "assumption", "roof sleeve wall, galvanised steel"),
    ("rg_t", "2 mm", "mm", "assumption", "roof grille plate; 50 % free or more (report 7e), pattern HOLD"),
]

PARTS = {   # key: part number, name, Vietnamese name, kind, material key
    "air": ("610000", "AIR", "Thông gió", "HS", None),
    "column": ("610101", "AIR - AIR COLUMN", "Cột gió (cụm)", "HS", None),
    "soffit": ("610201", "AIR - SOFFIT", "Hộp gió trần trên cửa (cụm)", "HS", None),
    "cart": ("610301", "AIR - SPLITTER CARTRIDGE - COMMON", "Ống tiêu âm (dùng chung cấp/thải)", "HS", None),
    "sbox": ("610401", "AIR - SUPPLY FAN BOX", "Hộp quạt cấp (cụm)", "HS", None),
    "ebox": ("610402", "AIR - EXHAUST FAN BOX", "Hộp quạt thải (cụm)", "HS", None),
    "col_front": ("611101", "AIR - COLUMN FACE - FRONT", "Cột gió - mặt trước (ACP + nỉ)", "MP", "face"),
    "col_left": ("611102", "AIR - COLUMN FACE - LEFT", "Cột gió - mặt trái (ACP + nỉ)", "MP", "face"),
    "col_ang": ("611103", "AIR - COLUMN CORNER ANGLE", "Cột gió - thanh góc nhôm", "MP", "al"),
    "col_fill": ("611104", "AIR - COLUMN FILL", "Cột gió - bông", "MP", "pfill"),
    "kick": ("611105", "AIR - KICK GRILLE", "Lưới gió chân cột", "MP", "perf60"),
    "col_foot": ("611106", "AIR - COLUMN FOOT PLATE", "Cột gió - tấm chân", "MP", "al"),
    "col_side_lo": ("611107", "AIR - COLUMN PLENUM SIDE PLATE - LOW", "Cột gió - tấm hông buồng dưới", "MP", "al"),
    "col_side_hi": ("611108", "AIR - COLUMN PLENUM SIDE PLATE - HIGH", "Cột gió - tấm hông buồng trên", "MP", "al"),
    "sof_under": ("611201", "AIR - SOFFIT UNDERSIDE - LEFT HINGED", "Hộp gió - mặt dưới trái (bản lề, màu tối)", "MP", "face"),
    "sof_under_r": ("611207", "AIR - SOFFIT UNDERSIDE - RIGHT HINGED", "Hộp gió - mặt dưới phải (bản lề, màu tối)", "MP", "face"),
    "sof_under_f": ("611208", "AIR - SOFFIT UNDERSIDE - FIXED OVER THE COLUMN", "Hộp gió - mặt dưới cố định trên cột", "MP", "face"),
    "sof_rail_d": ("611205", "AIR - SOFFIT TOP RAIL - DOOR SIDE", "Hộp gió - thanh treo phía cửa", "MP", "al"),
    "sof_rail_r": ("611209", "AIR - SOFFIT TOP RAIL - ROOM SIDE", "Hộp gió - thanh treo phía trong", "MP", "al"),
    "sof_end": ("611206", "AIR - SOFFIT END PLATE - LEFT", "Hộp gió - tấm đầu trái", "MP", "al"),
    "sof_front": ("611202", "AIR - SOFFIT FACE - FRONT", "Hộp gió - mặt trước", "MP", "face"),
    "sof_fill": ("611203", "AIR - SOFFIT FILL", "Hộp gió - bông", "MP", "pfill"),
    "egrille": ("611204", "AIR - EXHAUST GRILLE", "Lưới gió thải", "MP", "perf40"),
    "casing": ("611301", "AIR - CARTRIDGE CASING", "Vỏ ống tiêu âm nhôm 2 mm", "MP", "al"),
    "layer": ("611302", "AIR - CARTRIDGE LAYER 50", "Lớp tiêu âm 50 mm", "MP", "pyro"),
    "box": ("611401", "AIR - FAN BOX CASING - EXHAUST", "Vỏ hộp quạt thải nhôm 2 mm", "MP", "al"),
    "box_s": ("611402", "AIR - FAN BOX CASING - SUPPLY", "Vỏ hộp quạt cấp nhôm 2 mm", "MP", "al"),
    "riser": ("611501", "AIR - INTAKE RISER", "Ống hút gió đứng", "MP", "steel"),
    "sleeve": ("611601", "AIR - ROOF SLEEVE", "Ống thải qua mái", "MP", "steel"),
    "rgrille": ("611602", "AIR - ROOF GRILLE", "Lưới thải mái", "MP", "perf50"),
    "fan": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V 140 mm", "PI", "fan"),
    "stud": ("618104", "AIR - SOFFIT HANGER STUD - HOLD", "Vít treo hộp gió (chờ)", "HOLD", "hold"),
    "hinge": ("618105", "AIR - SOFFIT UNDERSIDE HINGE - HOLD", "Bản lề mặt dưới hộp gió (chờ)", "HOLD", "hold"),
    "latch": ("618106", "AIR - SOFFIT UNDERSIDE LATCH - HOLD", "Chốt bấm mặt dưới hộp gió (chờ)", "HOLD", "hold"),
    "hub": ("618101", "AIR - SENSOR HUB ZONE - HOLD", "Vùng bộ cảm biến (chờ)", "HOLD", "hold"),
    "trans": ("618102", "AIR - SUPPLY TRANSITION - HOLD", "Ống chuyển cấp (chờ)", "HOLD", "hold"),
    "rtrans": ("618103", "AIR - RISER TRANSITION - HOLD", "Ống chuyển hút (chờ)", "HOLD", "hold"),
}

# joint hardware from the joints register used in AIR (D-63): the soffit's two captive lock
# screws (PM ruling 2026-11-01), into the ceiling's rivnuts; their captive retainer is HOLD
HARDWARE = {
    "lock": ("838002", "HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC",
             "Bulong lục giác chìm M6 × 25 (chốt mối nối khép)", 2, 0.0079),
}

MATERIALS = {
    "al": ("Aluminium (alloy HOLD)", 2700.0),
    "perf60": ("Perforated aluminium, 60 % free", 2700.0 * 0.4),
    "perf40": ("Perforated aluminium, 40 % free", 2700.0 * 0.6),
    "perf50": ("Perforated aluminium, 50 % free", 2700.0 * 0.5),
    "steel": ("Galvanised steel DX51D+Z", 7850.0),
    "face": ("ACP 3 + felt 9 face (5.3 kg/m2)", 5.3 / 0.012),
    "pfill": ("Polyester fill 32 kg/m3", 32.0),
    "pyro": ("Pyrotek Sorberpoly 2D 40 kg/m3", 40.0),
    "fan": ("Fan envelope 0.3 kg (assumption)", 0.3 / (0.14 * 0.14 * 0.025)),
    "hold": ("HOLD envelope - no mass", 1.0),
}

# skeleton planes (expressions)
XIR = "(pod_w / 2 - stack_t)"
XIL = "(-pod_w / 2 + stack_t)"
YW = "(pod_d / 2 - wall_depth)"
YF = "(-pod_d / 2)"
ZS0 = "dt_zb"                        # soffit underside, flush with the top block's underside (D-61)
ZS1 = "(dt_zb + sof_h)"
ZC0 = "(floor_t + mat_t)"            # floor top (the mat's top), PM ruling 2026-11-01
ZCB = "(%s + foot_t)" % ZC0          # top of the column's foot plate
XR = "(pod_w / 2 - stack_t - col_gap)"    # the column's and the soffit's right limit, 5 mm off the lining
XL = "(-pod_w / 2 + stack_t + col_gap)"   # the soffit's left limit
YFACE = "(%s + col_d)" % YW          # the column's and the soffit's front face (Y -285)


AIR_MAY_DEFINE = {"mat_t"}    # the skeleton's own value wins once it carries it


def all_params():
    base = CM.all_params()
    have = {p[0] for p in base}
    clash = [p[0] for p in AIR_PARAMS if p[0] in have and p[0] not in AIR_MAY_DEFINE]
    if clash:
        raise ValueError("AIR parameter names clash with the skeleton or the ceiling: %s" % clash)
    return base + [p for p in AIR_PARAMS if p[0] not in have]


def evaluate(params=None, overrides=None):
    return CM.evaluate(params or all_params(), overrides)


ev = CM.ev
overlap = CM.overlap


def box(x0, x1, y0, y1, z0, z1):
    return (x0, x1, y0, y1, z0, z1)


def soffit_sections():
    """The soffit underside: two hinged sections and a fixed strip over the column (D-87)."""
    return [("sof_under", "SOFFIT UNDERSIDE LEFT", XL, "-us_gap / 2"),
            ("sof_under_r", "SOFFIT UNDERSIDE RIGHT", "us_gap / 2", "col_x0 - us_gap / 2"),
            ("sof_under_f", "SOFFIT UNDERSIDE FIXED", "col_x0", XR)]


def stud_points():
    """(name, x, y) of the soffit's four hanger studs, at the ceiling's hanger rivnuts."""
    yd = "%s + tube_w / 2" % YW
    yr = "%s + cs_front - x1_ov + tube_w / 2" % YW
    return [("STUD %s %s" % (side, edge), "%shang_x" % ("-" if side == "L" else ""), y)
            for side in ("L", "R") for edge, y in (("DOOR", yd), ("ROOM", yr))]


def layout():
    """[(part key, body name, box expressions)] for every body, pod system."""
    b = []
    # column: foot plate on the floor's mat, faces above the kick grille up to the soffit
    b.append(("col_foot", "COLUMN FOOT PLATE", box("col_x0", XR, YW, YFACE, ZC0, ZCB)))
    zg1 = "%s + grille_z + grille_h" % ZCB
    b.append(("col_front", "COLUMN FACE FRONT", box("col_x0", XR, "%s - face_t" % YFACE, YFACE, zg1, ZS0)))
    b.append(("col_left", "COLUMN FACE LEFT", box("col_x0", "col_x0 + face_t", YW, "%s - face_t" % YFACE, zg1, ZS0)))
    zg0 = "%s + grille_z" % ZCB
    b.append(("kick", "KICK GRILLE FRONT", box("col_x0", XR, "%s - grille_t" % YFACE, YFACE, zg0, zg1)))
    b.append(("kick", "KICK GRILLE LEFT", box("col_x0", "col_x0 + grille_t", "%s - grille_t - grille_l" % YFACE,
                                                  "%s - grille_t" % YFACE, zg0, zg1)))
    # corner angles, full height inside the faces (the back-right corner: the plenum plates)
    for name, x0, xw, y0 in (("FL", "col_x0 + face_t", "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("FR", "%s - ang_f" % XR, "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("BL", "col_x0 + face_t", "ang_w", YW)):
        b.append(("col_ang", "COLUMN ANGLE %s" % name, box(x0, "%s + %s" % (x0, xw), y0, "%s + ang_w" % y0, ZCB, ZS0)))
    # supply cartridge: 5 mm clear of the plenum plates and the block
    cx1 = "%s - plate_t - clr" % XR
    cx0 = "%s - cart_w" % cx1
    cy0, cy1 = "%s + clr" % YW, "%s + clr + cart_d" % YW
    cz0 = "%s + plen_lo" % ZCB
    cz1 = "%s + cart_l" % cz0
    b.append(("cart", "CARTRIDGE SUPPLY", box(cx0, cx1, cy0, cy1, cz0, cz1)))
    # the column's right side at the two plenums (the cartridge closes the rest)
    py1 = "%s - face_t - ang_w" % YFACE
    b.append(("col_side_lo", "COLUMN PLENUM PLATE LOW", box("%s - plate_t" % XR, XR, YW, py1, ZCB, cz0)))
    b.append(("col_side_hi", "COLUMN PLENUM PLATE HIGH", box("%s - plate_t" % XR, XR, YW, py1, cz1, ZS0)))
    b.append(("col_fill", "COLUMN FILL FRONT", box("col_x0 + face_t + ang_f", "%s - ang_f" % XR, cy1,
                                                     "%s - face_t" % YFACE, cz0, cz1)))
    b.append(("col_fill", "COLUMN FILL LEFT", box("col_x0 + face_t", cx0, "%s + ang_w" % YW, cy1, cz0, cz1)))
    hx = "(col_x0 + face_t + ang_f + %s - ang_f) / 2" % XR     # centred between the front angles' legs
    b.append(("hub", "SENSOR HUB ZONE", box("%s - hub_w / 2" % hx, "%s + hub_w / 2" % hx, "%s - hub_t" % YFACE,
                                             YFACE, "hub_z - hub_w / 2", "hub_z + hub_w / 2")))
    # soffit: underside sections (dark tone), front face, top rails, left end plate
    zf1 = "%s - rail_t - hd_h - 1 mm" % ZS1        # front face top: hidden above the ceiling felt (Z 2316)
    for key, name, x0, x1 in soffit_sections():
        b.append((key, name, box(x0, x1, YW, "%s - face_t" % YFACE, ZS0, "%s + face_t" % ZS0)))
    b.append(("sof_front", "SOFFIT FACE FRONT", box(XL, XR, "%s - face_t" % YFACE, YFACE, ZS0, zf1)))
    zr0 = "%s - rail_t" % ZS1
    b.append(("sof_rail_d", "SOFFIT RAIL DOOR", box(XL, XR, YW, "%s + rail_w" % YW, zr0, ZS1)))
    b.append(("sof_rail_r", "SOFFIT RAIL ROOM", box(XL, XR, "%s - rail_w" % YFACE, YFACE, zr0, ZS1)))
    b.append(("sof_end", "SOFFIT END PLATE LEFT", box(XL, "%s + box_t" % XL, YW, "%s - face_t" % YFACE,
                                                      "%s + face_t" % ZS0, zr0)))
    ex1 = "%s - fb_w" % XR
    ez0 = "%s + face_t + sof_fill_t" % ZS0
    b.append(("cart", "CARTRIDGE EXHAUST", box("%s - cart_l" % ex1, ex1, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b.append(("box", "EXHAUST FAN BOX", box(ex1, XR, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b.append(("sof_fill", "SOFFIT FILL UNDER", box("%s - cart_l" % ex1, XR, cy0, "%s - face_t" % YFACE,
                                                    "%s + face_t" % ZS0, ez0)))
    b.append(("sof_fill", "SOFFIT FILL FRONT", box("%s - cart_l" % ex1, XR, cy1, "%s - face_t" % YFACE, ez0, zr0)))
    b.append(("egrille", "EXHAUST GRILLE", box("%s + eg_x0" % XIL, "%s + eg_x0 + eg_l" % XIL, "%s + face_t" % YW,
                                                "%s + face_t + eg_w" % YW, ZS0, "%s + grille_t" % ZS0)))
    # hanging: 4 studs (head under the rail, shank up through the fork to the ceiling frame),
    # 2 captive lock screws in the door-side rail (838002, retainer HOLD), hinges and latches
    zf = "(pod_h - outer_t)"
    for name, x, y in stud_points():
        b.append(("stud", name + " HEAD", box("%s - stud_d / 2" % x, "%s + stud_d / 2" % x, "%s - stud_d / 2" % y,
                                              "%s + stud_d / 2" % y, "%s - hd_h" % zr0, zr0)))
        b.append(("stud", name + " SHANK", box("%s - 3 mm" % x, "%s + 3 mm" % x, "%s - 3 mm" % y, "%s + 3 mm" % y, zr0, zf)))
    for k, x in enumerate(("-lock_x", "-lock_x + lock_dx")):
        y = "%s + tube_w / 2" % YW
        b.append(("lock", "LOCK SCREW %d HEAD" % (k + 1), box("%s - stud_d / 2" % x, "%s + stud_d / 2" % x,
                                                              "%s - stud_d / 2" % y, "%s + stud_d / 2" % y,
                                                              "%s - hd_h - 2 mm" % zr0, zr0)))
        b.append(("lock", "LOCK SCREW %d SHANK" % (k + 1), box("%s - 3 mm" % x, "%s + 3 mm" % x, "%s - 3 mm" % y,
                                                               "%s + 3 mm" % y, zr0, zf)))
    zh0, zh1 = "%s + face_t" % ZS0, "%s + face_t + hl_h" % ZS0
    for key, name, x0, x1 in soffit_sections()[:2]:
        for q in (1, 3):
            xc = "(%s) + ((%s) - (%s)) * %d / 4" % (x0, x1, x0, q)
            b.append(("hinge", "%s HINGE %d" % (name, q), box("%s - hinge_l / 2" % xc, "%s + hinge_l / 2" % xc,
                                                             YW, "%s + clr" % YW, zh0, zh1)))
            b.append(("latch", "%s LATCH %d" % (name, q), box("%s - latch_l / 2" % xc, "%s + latch_l / 2" % xc,
                                                             "%s - face_t - hl_h" % YFACE, "%s - face_t" % YFACE, zh0, zh1)))
    # supply fan box joined with the intake riser (D-87), the transitions, the roof sleeve and grille
    sy0 = "%s + sb_yf" % YF
    b.append(("box_s", "SUPPLY FAN BOX", box("sb_x0", "sb_x0 + sb_w", sy0, "%s + sb_d" % sy0, "sb_z0", "sb_z0 + sb_h")))
    b.append(("trans", "SUPPLY TRANSITION", box("sb_x0", "op_x0 + (%s - op_x0)" % XR, "%s + sb_d" % sy0, YW,
                                                 "op_z0", "op_z0 + op_h")))
    b.append(("riser", "INTAKE RISER", box("rs_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z0", "rs_z1")))
    b.append(("rtrans", "RISER TRANSITION", box("sb_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z1", "sb_z0")))
    b.append(("sleeve", "ROOF SLEEVE", box("slot_x0", "slot_x0 + slot_w", "slot_y0", "slot_y0 + slot_d",
                                            "%s + cart_w" % ez0, "pod_h")))
    b.append(("rgrille", "ROOF GRILLE", box("slot_x0 - 10 mm", "slot_x0 + slot_w + 10 mm", "slot_y0 - 10 mm",
                                             "slot_y0 + slot_d + 10 mm", "pod_h", "pod_h + rg_t")))
    return b


def features():
    """Cut features inside bodies (no change to their boxes): the column's keyholes in the
    back-left angle, BASE's spigot hole and slot in the foot plate, the rails' forks and the
    lock screws' holes. [(body name, kind, args)]: kind 'zcircle' (x, y, z0, z1, d), 'ycircle'
    (x, z, y0, y1, d) or 'box' (x0, x1, y0, y1, z0, z1)."""
    out = []
    # keyholes: the column drops key_drop onto each stud, so the big hole is key_drop below it
    for k, zs in (("1", "hook_z1"), ("2", "hook_z2")):
        out.append(("COLUMN ANGLE BL", "ycircle", ("hook_x", "%s - key_drop" % zs, YW, "%s + ang_t" % YW, "key_d")))
        out.append(("COLUMN ANGLE BL", "box", ("hook_x - key_w / 2", "hook_x + key_w / 2", YW, "%s + ang_t" % YW,
                                               "%s - key_drop" % zs, zs)))
        out.append(("COLUMN ANGLE BL", "ycircle", ("hook_x", zs, YW, "%s + ang_t" % YW, "key_w")))
    # foot plate: S1 round, S2 slot along Y
    out.append(("COLUMN FOOT PLATE", "zcircle", ("spg1_x", "spg1_y", ZC0, ZCB, "spg_hole")))
    run = "(spg_slot - spg_hole) / 2"
    out.append(("COLUMN FOOT PLATE", "box", ("spg2_x - spg_hole / 2", "spg2_x + spg_hole / 2", "spg2_y - %s" % run,
                                             "spg2_y + %s" % run, ZC0, ZCB)))
    for sign in ("-", "+"):
        out.append(("COLUMN FOOT PLATE", "zcircle", ("spg2_x", "spg2_y %s %s" % (sign, run), ZC0, ZCB, "spg_hole")))
    # rails: an open fork from the rail's door-side edge to each stud's place
    zr0 = "%s - rail_t" % ZS1
    for name, x, y in stud_points():
        rail = "SOFFIT RAIL DOOR" if name.endswith("DOOR") else "SOFFIT RAIL ROOM"
        edge = YW if rail.endswith("DOOR") else "%s - rail_w" % YFACE
        out.append((rail, "box", ("%s - key_w / 2" % x, "%s + key_w / 2" % x, edge, y, zr0, ZS1)))
        out.append((rail, "zcircle", (x, y, zr0, ZS1, "key_w")))
    for x in ("-lock_x", "-lock_x + lock_dx"):
        out.append(("SOFFIT RAIL DOOR", "zcircle", (x, "%s + tube_w / 2" % YW, zr0, ZS1, "6.6 mm")))
    return out


def cutouts():
    """(body name to cut, cutter box): the hub zone through the front face and the fill
    behind it, the exhaust grille's opening in the soffit underside."""
    lay = {name: bx for _k, name, bx in layout()}
    hub = lay["SENSOR HUB ZONE"]
    eg = lay["EXHAUST GRILLE"]
    hub_cut = (hub[0], hub[1], "%s - face_t - 40 mm" % YFACE, hub[3], hub[4], hub[5])
    eg_cut = (eg[0], eg[1], eg[2], eg[3], ZS0, "%s + face_t" % ZS0)    # the grille's opening through the face
    out = [("COLUMN FACE FRONT", hub_cut), ("COLUMN FILL FRONT", hub_cut), ("SOFFIT UNDERSIDE LEFT", eg_cut)]
    for _k, name, bx in layout():
        if " LATCH " in name:
            out.append(("SOFFIT FILL UNDER", bx))       # the fill clears each latch
    return out


def fan_points():
    """Fan centres (x, y, z of the fan's underside): two in each fan box, lying flat."""
    pts = []
    for tag, x0, w, y0, d, z0 in (("SUPPLY", "sb_x0", "sb_w", "%s + sb_yf" % YF, "sb_d", "sb_z0 + lin_t"),
                                  ("EXHAUST", "%s - fb_w" % XR, "fb_w", "%s + clr" % YW, "cart_d",
                                   "%s + face_t + sof_fill_t + lin_t" % ZS0)):
        for k in (1, 3):
            pts.append(("%s FAN %d" % (tag, (k + 1) // 2), "%s + %s * %d / 4" % (x0, w, k), "%s + %s / 2" % (y0, d), z0))
    return pts


if __name__ == "__main__":
    v = evaluate()
    for key, name, bx in layout():
        print("%-10s %-22s %s" % (key, name, [round(ev(v, e), 2) for e in bx]))
    print("pass_w", v["pass_w"], "col width", round(ev(v, XIR) - v["col_x0"], 2))
