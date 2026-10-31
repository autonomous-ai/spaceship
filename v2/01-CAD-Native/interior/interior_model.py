"""Spaceship (FocusPod v2) INTERIOR (D-70, D-85): parameters and layout, without Fusion.

The light shelf along the tops of the side and back walls (it lights the felt ceiling; on
the right wall it also carries ELECTRICAL's down-light over the ledge), the work wall's
1000 mm ledge, and the screen rail. Every size is a named parameter: the skeleton's own list
(loaded from its CSV, the highest revision in ../skeleton/), the ceiling's (the soffit
depth cs_front sets where the side walls' free length starts), and the INTERIOR parameters
below, each with its status and source.

Coordinates: the pod system (conventions.md section 4), mm. INTERIOR parts sit on the
floating linings (D-17) or stand off them: the light shelf is screwed to the wall cassettes
(light, nothing bridges to the outer frame); the ledge and the screen rail need the outer
frame, so they stand on stand-offs through clearance holes in the lining (WALL interface).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import ceiling_model as CM  # noqa: E402  (skeleton loader and expression tools)

REV = "P01"
D70 = "D-70 (PM ruling 2026-10-31)"
ELEC = "ELECTRICAL's input via the PM, 2026-11-01"

INTERIOR_PARAMS = [
    # ---- light shelf: a folded 1.0 mm aluminium U along the wall tops, the up-light strip in it
    ("sh_d", "60 mm", "mm", "assumption", D70 + ": slim light shelf; 60 out from the lining face"),
    ("sh_hb", "40 mm", "mm", "assumption", "back flange height, screwed to the wall cassette"),
    ("sh_hl", "20 mm", "mm", "assumption", "front lip height: hides the up-light strip from a seated eye"),
    ("sh_t", "1 mm", "mm", "assumption", "D-85 budget 0.4 kg/m: 1.0 mm aluminium, 118 mm2 section (0.32 kg/m) plus the strip"),
    ("sh_z0", "2230 mm", "mm", "assumption", "shelf underside; ELECTRICAL's feed and call-light drop are at Z 2250, in the back flange, and the felt ceiling (Z 2316) is 46 above the flange"),
    ("dc_x0", "15 mm", "mm", "assumption", "down channel (right wall only) from 15 out from the lining"),
    ("dc_w", "30 mm", "mm", "assumption", ELEC + ": a down channel with a diffuser for two 8 mm strips over the ledge"),
    ("dc_h", "12 mm", "mm", "assumption", "down channel depth under the shelf"),
    ("df_t", "1.5 mm", "mm", "assumption", "opal diffuser strip in the down channel"),
    ("cab_d", "10 mm", "mm", "assumption", "cable hole in the back flange for the feed and the call-light drop"),
    ("feed_x", "355 mm", "mm", "confirmed", ELEC + ": the feed point at X 355 on the back wall, Z 2250"),
    ("call_y", "-209.5 mm", "mm", "confirmed", ELEC + ": the call-light drop at Y -209.5 on the right wall, Z 2250"),
    ("cab_z", "2250 mm", "mm", "confirmed", ELEC + ": both at Z 2250"),
    # ---- work wall ledge (right wall beside the air column)
    ("lg_l", "1000 mm", "mm", "confirmed", D70 + ": a 1000 mm ledge on the work wall"),
    ("lg_d", "250 mm", "mm", "assumption", "ledge depth: room for a keyboard, leaning on it standing"),
    ("lg_z", "1067 mm", "mm", "assumption", "ledge top: standing lean height"),
    ("lg_t", "1.5 mm", "mm", "confirmed", "D-85: 1.5 mm folded aluminium"),
    ("lg_lip", "25 mm", "mm", "assumption", "front lip folded down"),
    ("lg_up", "25 mm", "mm", "assumption", "back flange folded down, at the wall"),
    ("lg_gap", "2 mm", "mm", "assumption", "the ledge stands 2 off the felt so it never bridges the floating lining (D-17)"),
    ("br_w", "200 mm", "mm", "assumption", "ledge bracket arm under the ledge, HOLD (a rated concealed shelf bracket)"),
    ("br_h", "150 mm", "mm", "assumption", "ledge bracket height at the wall, HOLD"),
    ("br_t", "30 mm", "mm", "assumption", "ledge bracket width along the wall, HOLD"),
    ("br_y1", "98.63 mm", "mm", "source", "WALL's right lower panel R1: mid stile at Y 98.63 (side panel stile pitch 365.69, mirror of L1)"),
    ("br_y2", "464.32 mm", "mm", "source", "WALL's R1: mid stile at Y 464.32"),
    # ---- screen rail (a screen up to about 900 wide, D-70; the screen itself is an option)
    ("sr_l", "900 mm", "mm", "confirmed", D70 + ": a screen up to about 900 mm wide"),
    ("sr_z", "1300 mm", "mm", "assumption", "rail centre height; the screen hangs on it above the ledge"),
    ("sr_d", "25 mm", "mm", "assumption", "rail depth out from the lining, HOLD (a bought VESA rail)"),
    ("sr_h", "50 mm", "mm", "assumption", "rail height, HOLD"),
]

PARTS = {   # key: part number, name, Vietnamese name, kind, material key
    "interior": ("810000", "INTERIOR", "Nội thất", "HS", None),
    "ledge_assy": ("810101", "INTERIOR - WORK WALL LEDGE ASSY", "Bàn tựa vách làm việc (cụm)", "HS", None),
    "shelf_assy": ("810201", "INTERIOR - LIGHT SHELF ASSY", "Kệ đèn hắt (cụm)", "HS", None),
    "ledge": ("811101", "INTERIOR - LEDGE - TOP", "Mặt bàn tựa nhôm gấp 1.5", "MP", "al"),
    "shelf_back": ("811201", "INTERIOR - LIGHT SHELF - BACK", "Kệ đèn - vách sau", "MP", "al"),
    "shelf_lh": ("811202", "INTERIOR - LIGHT SHELF - SIDE LH", "Kệ đèn - vách trái", "MP", "al"),
    "shelf_rh": ("811203", "INTERIOR - LIGHT SHELF - SIDE RH", "Kệ đèn - vách phải", "MP", "al"),
    "dchan": ("811204", "INTERIOR - LIGHT SHELF - DOWN CHANNEL RH", "Máng đèn rọi xuống - vách phải", "MP", "al"),
    "diffuser": ("811205", "INTERIOR - LIGHT SHELF - DIFFUSER RH", "Tấm khuếch tán - vách phải", "MP", "pc"),
    "bracket": ("818101", "INTERIOR - LEDGE BRACKET - HOLD", "Ke đỡ bàn tựa (chờ)", "HOLD", "hold"),
    "rail": ("818102", "INTERIOR - SCREEN RAIL - HOLD", "Thanh treo màn hình (chờ)", "HOLD", "hold"),
}

MATERIALS = {   # name, density kg/m3, status, source
    "al": ("Aluminium 5052-H32 sheet (alloy HOLD)", 2700.0, "source", "aluminium 2.70 g/cm3"),
    "pc": ("Opal polycarbonate", 1200.0, "source", "polycarbonate 1.20 g/cm3"),
    "hold": ("HOLD envelope - no mass", 1.0, "assumption", "space only"),
}
HOLD_MASS = {"bracket": (0.10, "assumption: an aluminium concealed shelf bracket with its stand-offs, about 0.1 kg (D-85 budget: the ledge with 2 brackets 1.4 kg)"),
             "rail": (0.50, "assumption: a 900 aluminium VESA rail, about 0.5 kg")}
STRIP_KG_M = (0.02, "assumption: an 8 mm LED strip, about 20 g/m (ELECTRICAL's part, counted here only for the 0.4 kg/m budget)")

XIR = "(pod_w / 2 - stack_t)"            # right lining face
XIL = "(-pod_w / 2 + stack_t)"           # left lining face
YBL = "(pod_d / 2 - stack_t)"            # back lining face
YFACE = "(pod_d / 2 - wall_depth + cs_front)"   # soffit's and column's room face (Y -285)


def all_params():
    base = CM.all_params()
    have = {p[0] for p in base}
    clash = [p[0] for p in INTERIOR_PARAMS if p[0] in have]
    if clash:
        raise ValueError("INTERIOR parameter names clash with the skeleton or the ceiling: %s" % clash)
    return base + INTERIOR_PARAMS


def evaluate(params=None, overrides=None):
    return CM.evaluate(params or all_params(), overrides)


ev = CM.ev
overlap = CM.overlap


def shelf_section(u0_expr, sign, plane):
    """The shelf's folded U as (u, z) corner expressions, u measured from the lining face out
    into the room: back flange, bottom, front lip. u0_expr: the lining face's coordinate;
    sign: +1 when out into the room is +u, -1 when it is -u."""
    s = "+" if sign > 0 else "-"
    t, z0 = "sh_t", "sh_z0"

    def u(d):
        return "(%s %s (%s))" % (u0_expr, s, d)
    return [(u("0 mm"), z0), (u("sh_d"), z0), (u("sh_d"), "%s + sh_hl" % z0), (u("sh_d - %s" % t), "%s + sh_hl" % z0),
            (u("sh_d - %s" % t), "%s + %s" % (z0, t)), (u(t), "%s + %s" % (z0, t)), (u(t), "%s + sh_hb" % z0),
            (u("0 mm"), "%s + sh_hb" % z0)]


def down_channel_section():
    """The right wall's down channel: an open-bottomed U under the shelf (x, z) in the XZ plane."""
    def x(d):
        return "(%s - (%s))" % (XIR, d)
    z0 = "sh_z0"
    a, b = "dc_x0", "dc_x0 + dc_w"
    return [(x(a), z0), (x(b), z0), (x(b), "%s - dc_h" % z0), (x("%s - sh_t" % b), "%s - dc_h" % z0),
            (x("%s - sh_t" % b), "%s - sh_t" % z0), (x("%s + sh_t" % a), "%s - sh_t" % z0),
            (x("%s + sh_t" % a), "%s - dc_h" % z0), (x(a), "%s - dc_h" % z0)]


def ledge_section():
    """The ledge's folded inverted U (x, z) in the XZ plane: top, front lip down, back flange
    down at the wall (2 mm off the felt)."""
    xb = "(%s - lg_gap)" % XIR
    xa = "(%s - lg_gap - lg_d)" % XIR
    z1 = "lg_z"
    return [(xa, z1), (xb, z1), (xb, "%s - lg_up" % z1), ("%s - lg_t" % xb, "%s - lg_up" % z1),
            ("%s - lg_t" % xb, "%s - lg_t" % z1), ("%s + lg_t" % xa, "%s - lg_t" % z1),
            ("%s + lg_t" % xa, "%s - lg_lip" % z1), (xa, "%s - lg_lip" % z1)]


def ledge_y():
    """The ledge's Y range: centred in the right wall's free length beside the column."""
    y0 = "(%s + (%s - %s - lg_l) / 2)" % (YFACE, YBL, YFACE)
    return y0, "%s + lg_l" % y0


def layout():
    """[(part key, body name, kind, data)]: kind 'xz' (section in the XZ plane, extruded along
    Y from y0 to y1), 'yz' (section in the YZ plane, extruded along X) or 'box'."""
    out = []
    sy0, sy1 = YFACE, "%s - sh_d" % YBL          # side shelves butt into the back shelf
    out.append(("shelf_back", "LIGHT SHELF BACK", "yz", (shelf_section(YBL, -1, "yz"), XIL, XIR)))
    out.append(("shelf_lh", "LIGHT SHELF LH", "xz", (shelf_section(XIL, 1, "xz"), sy0, sy1)))
    out.append(("shelf_rh", "LIGHT SHELF RH", "xz", (shelf_section(XIR, -1, "xz"), sy0, sy1)))
    out.append(("dchan", "DOWN CHANNEL RH", "xz", (down_channel_section(), sy0, sy1)))
    out.append(("diffuser", "DIFFUSER RH", "box", ("%s - dc_x0 - dc_w + sh_t" % XIR, "%s - dc_x0 - sh_t" % XIR, sy0, sy1,
                                                     "sh_z0 - dc_h", "sh_z0 - dc_h + df_t")))
    y0, y1 = ledge_y()
    out.append(("ledge", "LEDGE TOP", "xz", (ledge_section(), y0, y1)))
    for k, yb in (("1", "br_y1"), ("2", "br_y2")):
        out.append(("bracket", "LEDGE BRACKET %s" % k, "box", ("%s - lg_gap - br_w" % XIR, "%s - lg_gap - lg_t" % XIR,
                                                              "%s - br_t / 2" % yb, "%s + br_t / 2" % yb,
                                                              "lg_z - lg_t - br_h", "lg_z - lg_t")))
    yc = "(%s + %s) / 2" % (y0, y1)
    out.append(("rail", "SCREEN RAIL", "box", ("%s - lg_gap - sr_d" % XIR, "%s - lg_gap" % XIR, "%s - sr_l / 2" % yc, "%s + sr_l / 2" % yc,
                                              "sr_z - sr_h / 2", "sr_z + sr_h / 2")))
    return out


def features():
    """Cable holes in the shelves' back flanges (ELECTRICAL's feed and call-light drop)."""
    return [("LIGHT SHELF BACK", "ycircle", ("feed_x", "cab_z", YBL, "%s - sh_t" % YBL, "cab_d")),
            ("LIGHT SHELF RH", "xcircle", (XIR, "call_y", "cab_z", "-1", "cab_d"))]


def boxes(vals):
    """Bounding boxes in mm of every layout body (for checks)."""
    out = {}
    for key, name, kind, data in layout():
        if kind == "box":
            b = [ev(vals, e) for e in data]
        else:
            sec, a0, a1 = data
            us = [ev(vals, u) for u, _z in sec]
            zs = [ev(vals, z) for _u, z in sec]
            r = (ev(vals, a0), ev(vals, a1))
            if kind == "xz":
                b = [min(us), max(us), min(r), max(r), min(zs), max(zs)]
            else:
                b = [min(r), max(r), min(us), max(us), min(zs), max(zs)]
        out[name] = (key, b)
    return out


def section_area(vals, sec):
    pts = [(ev(vals, u), ev(vals, z)) for u, z in sec]
    a = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


if __name__ == "__main__":
    v = evaluate()
    for name, (key, b) in boxes(v).items():
        print("%-10s %-18s %s" % (key, name, [round(x, 2) for x in b]))
    print("shelf section %.1f mm2, down channel %.1f mm2, ledge %.1f mm2" % (
        section_area(v, shelf_section(XIR, -1, "xz")), section_area(v, down_channel_section()), section_area(v, ledge_section())))
