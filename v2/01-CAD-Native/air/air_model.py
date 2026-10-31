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
    ("ang_w", "20 mm", "mm", "assumption", "corner angle leg along the side faces; the report says 4 corner angles, size not given"),
    ("ang_f", "12 mm", "mm", "assumption", "corner angle leg along the front face: short, so the 180 hub zone fits between the two front corners (217 - 12 - 2 x 12 = 181)"),
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
    ("slot_x0", "872 mm", "mm", "source", R7E + ": roof slot X 872 to 1157"),
    ("slot_w", "285 mm", "mm", "source", R7E + ": roof slot 285 x 294"),
    ("slot_d", "294 mm", "mm", "source", R7E + ": roof slot 285 x 294"),
    ("slot_y0", "-620 mm", "mm", "confirmed", "D-61: roof slot Y -620 to -326 (5 mm clear of the ceiling frame's front member)"),
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
    "sof_under": ("611201", "AIR - SOFFIT UNDERSIDE", "Hộp gió - mặt dưới (màu tối)", "MP", "face"),
    "sof_front": ("611202", "AIR - SOFFIT FACE - FRONT", "Hộp gió - mặt trước", "MP", "face"),
    "sof_fill": ("611203", "AIR - SOFFIT FILL", "Hộp gió - bông", "MP", "pfill"),
    "egrille": ("611204", "AIR - EXHAUST GRILLE", "Lưới gió thải", "MP", "perf40"),
    "casing": ("611301", "AIR - CARTRIDGE CASING", "Vỏ ống tiêu âm nhôm 2 mm", "MP", "al"),
    "layer": ("611302", "AIR - CARTRIDGE LAYER 50", "Lớp tiêu âm 50 mm", "MP", "pyro"),
    "box": ("611401", "AIR - FAN BOX CASING", "Vỏ hộp quạt nhôm 2 mm", "MP", "al"),
    "riser": ("611501", "AIR - INTAKE RISER", "Ống hút gió đứng", "MP", "steel"),
    "sleeve": ("611601", "AIR - ROOF SLEEVE", "Ống thải qua mái", "MP", "steel"),
    "rgrille": ("611602", "AIR - ROOF GRILLE", "Lưới thải mái", "MP", "perf50"),
    "fan": ("618001", "AIR - FAN 12 V 140 - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V 140", "PI", "fan"),
    "hub": ("618101", "AIR - SENSOR HUB ZONE - HOLD", "Vùng bộ cảm biến (chờ)", "HOLD", "hold"),
    "trans": ("618102", "AIR - SUPPLY TRANSITION - HOLD", "Ống chuyển cấp (chờ)", "HOLD", "hold"),
    "rtrans": ("618103", "AIR - RISER TRANSITION - HOLD", "Ống chuyển hút (chờ)", "HOLD", "hold"),
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
ZC0 = "floor_t"                      # column foot on the floor
YFACE = "(%s + col_d)" % YW          # the column's and the soffit's front face (Y -285)


def all_params():
    return CM.all_params() + AIR_PARAMS


def evaluate(params=None, overrides=None):
    return CM.evaluate(params or all_params(), overrides)


ev = CM.ev
overlap = CM.overlap


def box(x0, x1, y0, y1, z0, z1):
    return (x0, x1, y0, y1, z0, z1)


def layout():
    """[(part key, body name, box expressions)] for every body, pod system."""
    b = []
    # column faces: front (Y face) and left (X face), above the kick grille, up to the soffit
    zg1 = "%s + grille_z + grille_h" % ZC0
    b.append(("col_front", "COLUMN FACE FRONT", box("col_x0", XIR, "%s - face_t" % YFACE, YFACE, zg1, ZS0)))
    b.append(("col_left", "COLUMN FACE LEFT", box("col_x0", "col_x0 + face_t", YW, "%s - face_t" % YFACE, zg1, ZS0)))
    # kick grille: front and left pieces, flush with the faces
    zg0 = "%s + grille_z" % ZC0
    b.append(("kick", "KICK GRILLE FRONT", box("col_x0", XIR, "%s - grille_t" % YFACE, YFACE, zg0, zg1)))
    b.append(("kick", "KICK GRILLE LEFT", box("col_x0", "col_x0 + grille_t", "%s - grille_t - grille_l" % YFACE,
                                                  "%s - grille_t" % YFACE, zg0, zg1)))
    # corner angles, full height inside the faces. The report counts 4; the back-right corner
    # has only the 5 mm cartridge clearance, and the side lining and the block's back plate
    # close it, so it gets none (to confirm with the Air Engineer)
    for name, x0, xw, y0 in (("FL", "col_x0 + face_t", "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("FR", "%s - ang_f" % XIR, "ang_f", "%s - face_t - ang_w" % YFACE),
                             ("BL", "col_x0 + face_t", "ang_w", YW)):
        b.append(("col_ang", "COLUMN ANGLE %s" % name, box(x0, "%s + %s" % (x0, xw), y0, "%s + ang_w" % y0, ZC0, ZS0)))
    # supply cartridge: against the side lining and the block, 5 mm clear
    cx0, cx1 = "%s - clr - cart_w" % XIR, "%s - clr" % XIR
    cy0, cy1 = "%s + clr" % YW, "%s + clr + cart_d" % YW
    cz0 = "%s + plen_lo" % ZC0
    b.append(("cart", "CARTRIDGE SUPPLY", box(cx0, cx1, cy0, cy1, cz0, "%s + cart_l" % cz0)))
    # column fill between the cartridge and the faces, over the cartridge's height
    b.append(("col_fill", "COLUMN FILL FRONT", box("col_x0 + face_t + ang_f", "%s - ang_f" % XIR, cy1,
                                                     "%s - face_t" % YFACE, cz0, "%s + cart_l" % cz0)))
    b.append(("col_fill", "COLUMN FILL LEFT", box("col_x0 + face_t", cx0, "%s + ang_w" % YW, cy1, cz0,
                                                    "%s + cart_l" % cz0)))
    # sensor hub zone on the front face (HOLD: in-house module)
    hx = "(col_x0 + face_t + ang_f + %s - ang_f) / 2" % XIR     # centred between the front angles' legs
    b.append(("hub", "SENSOR HUB ZONE", box("%s - hub_w / 2" % hx, "%s + hub_w / 2" % hx, "%s - hub_t" % YFACE,
                                             YFACE, "hub_z - hub_w / 2", "hub_z + hub_w / 2")))
    # soffit: underside (dark tone) and front face; the cartridge along X and the exhaust fan box
    b.append(("sof_under", "SOFFIT UNDERSIDE", box(XIL, XIR, YW, "%s - face_t" % YFACE, ZS0, "%s + face_t" % ZS0)))
    b.append(("sof_front", "SOFFIT FACE FRONT", box(XIL, XIR, "%s - face_t" % YFACE, YFACE, ZS0, ZS1)))
    ex1 = "%s - clr - fb_w" % XIR
    ez0 = "%s + face_t + sof_fill_t" % ZS0
    b.append(("cart", "CARTRIDGE EXHAUST", box("%s - cart_l" % ex1, ex1, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b.append(("box", "EXHAUST FAN BOX", box(ex1, "%s - clr" % XIR, cy0, cy1, ez0, "%s + cart_w" % ez0)))
    b.append(("sof_fill", "SOFFIT FILL UNDER", box("%s - cart_l" % ex1, "%s - clr" % XIR, cy0, "%s - face_t" % YFACE,
                                                    "%s + face_t" % ZS0, ez0)))
    b.append(("sof_fill", "SOFFIT FILL FRONT", box("%s - cart_l" % ex1, "%s - clr" % XIR, cy1, "%s - face_t" % YFACE,
                                                    ez0, ZS1)))
    b.append(("egrille", "EXHAUST GRILLE", box("%s + eg_x0" % XIL, "%s + eg_x0 + eg_l" % XIL, "%s + face_t" % YW,
                                                "%s + face_t + eg_w" % YW, ZS0, "%s + grille_t" % ZS0)))
    # supply fan box and transition, intake riser and its transition (inside the right block)
    sy0 = "%s + sb_yf" % YF
    b.append(("box", "SUPPLY FAN BOX", box("sb_x0", "sb_x0 + sb_w", sy0, "%s + sb_d" % sy0, "sb_z0", "sb_z0 + sb_h")))
    b.append(("trans", "SUPPLY TRANSITION", box("sb_x0", "op_x0 + (%s - clr - op_x0)" % XIR, "%s + sb_d" % sy0, YW,
                                                 "op_z0", "op_z0 + op_h")))
    b.append(("riser", "INTAKE RISER", box("rs_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z0", "rs_z1")))
    b.append(("rtrans", "RISER TRANSITION", box("sb_x0", "rs_x0 + rs_w", "rs_y0", "rs_y0 + rs_d", "rs_z1", "sb_z0")))
    # roof sleeve from the soffit top through the gap and the roof panel; grille on the skin
    b.append(("sleeve", "ROOF SLEEVE", box("slot_x0", "slot_x0 + slot_w", "slot_y0", "slot_y0 + slot_d",
                                            "%s + cart_w" % ez0, "pod_h")))
    b.append(("rgrille", "ROOF GRILLE", box("slot_x0 - 10 mm", "slot_x0 + slot_w + 10 mm", "slot_y0 - 10 mm",
                                             "slot_y0 + slot_d + 10 mm", "pod_h", "pod_h + rg_t")))
    return b


def cutouts():
    """(body name to cut, cutter box): the hub zone through the front face and the fill
    behind it, the exhaust grille's opening in the soffit underside."""
    lay = {name: bx for _k, name, bx in layout()}
    hub = lay["SENSOR HUB ZONE"]
    eg = lay["EXHAUST GRILLE"]
    hub_cut = (hub[0], hub[1], "%s - face_t - 40 mm" % YFACE, hub[3], hub[4], hub[5])
    eg_cut = (eg[0], eg[1], eg[2], eg[3], ZS0, "%s + face_t" % ZS0)    # the grille's opening through the face
    return [("COLUMN FACE FRONT", hub_cut), ("COLUMN FILL FRONT", hub_cut), ("SOFFIT UNDERSIDE", eg_cut)]


def fan_points():
    """Fan centres (x, y, z of the fan's underside): two in each fan box, lying flat."""
    pts = []
    for tag, x0, w, y0, d, z0 in (("SUPPLY", "sb_x0", "sb_w", "%s + sb_yf" % YF, "sb_d", "sb_z0 + lin_t"),
                                  ("EXHAUST", "%s - clr - fb_w" % XIR, "fb_w", "%s + clr" % YW, "cart_d",
                                   "%s + face_t + sof_fill_t + lin_t" % ZS0)):
        for k in (1, 3):
            pts.append(("%s FAN %d" % (tag, (k + 1) // 2), "%s + %s * %d / 4" % (x0, w, k), "%s + %s / 2" % (y0, d), z0))
    return pts


if __name__ == "__main__":
    v = evaluate()
    for key, name, bx in layout():
        print("%-10s %-22s %s" % (key, name, [round(ev(v, e), 2) for e in bx]))
    print("pass_w", v["pass_w"], "col width", round(ev(v, XIR) - v["col_x0"], 2))
