"""Drawing specs for the fixed glass unit (360002) and its parts, run inside drawing_specs.py's namespace when this file is present (one file per sub-assembly, so each
sub-assembly's branch carries only its own specs)."""

V_FIX, G_FIX = _evaluate("fixed_glass.py")


def gx(expr_pt, env=V_FIX):
    """Evaluate a front_lib.g_* corner (a pair of expression strings) to model mm."""
    f = lambda e: eval(re.sub(r"(\d)\s*mm\b", r"\1", e), {"__builtins__": {}, "sqrt": math.sqrt}, env)
    return f(expr_pt[0]), f(expr_pt[1])


_L = G_FIX["L"]
PB = [gx(p) for p in _L.g_outline("fg_bite")]          # the pane as cut: BL, BR, K, TR, TL
PV = [gx(p) for p in _L.g_outline("0 mm")]             # its visible outline
UP = [gx(p) for p in _L.g_outline("gu_prof_d")]        # the channels' outer line
xs = [p[0] for p in PB]
SPECS["pane"] = {
    "design": doc("361003", "FRONT - FIXED GLASS - 4+4 LAMINATED", "CAD"),
    "drawing": doc("361003", "FRONT - FIXED GLASS - 4+4 LAMINATED", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (190, 225), "iso": (320, 100)},
    "box": {"front": (min(xs), PB[0][1], max(xs), PB[4][1])},
    "dims": [
        ("front", PB[0], PB[1], "below", 12), ("front", PB[1], (PB[1][0], PB[3][1]), "right", 15),
        ("front", PB[4], PB[3], "above", 10), ("front", PB[0], PB[4], "left", 12),
        ("front", PB[1], PB[2], "right", 30), ("front", PB[2], PB[3], "right", 45),
    ],
    "notes": [
        "Glass: 4+4 laminated safety glass, two toughened, heat-soaked panes (EN 12150, EN 14179) with 0.76 mm grey "
        "PVB, 8.76 nominal (D-27, D-46); it stays 4+4 (PM ruling 2026-10-31). Product HOLD until named (ISS-074).",
        "Outline 1:1 in 361003_P01_FRONT-FIXED-GLASS-4-4-LAMINATED_DXF.dxf. The visible outline is the skeleton's "
        "measured v1 pentagon; the four held edges run %.1f past it into hidden channels in the base band, DR and DT; "
        "the free edge runs parallel to the door's latch edge, %.1f off (PM rulings)." % (V_FIX["fg_bite"], V_FIX["fg_gap"]),
        "No holes. Edges ground and arrised before toughening. Tolerances (PROPOSED, the supplier confirms): sizes and "
        "diagonals +/-1; corners at the knee and bottom right to the DXF.",
        "Fit order (PM ruling 2026-11-01): the bottom channel comes factory-fitted on BASE's sill; on site the pane "
        "drops into it, then DR from the side, then DT from above.",
    ],
    "title": title("361003", "FRONT - FIXED GLASS - 4+4 LAMINATED", "Tấm kính cố định 4+4",
                   "4+4 laminated toughened heat-soaked glass, grey PVB", "edges ground and arrised", "1:10", "A2",
                   [("MASS", "28.6 kg (calculation)")]),
}
SPECS["fixed_unit"] = {
    "design": doc("360002", "FRONT - FIXED GLASS UNIT", "CAD"),
    "drawing": doc("360002", "FRONT - FIXED GLASS UNIT", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (170, 240), "top": (170, 105),
                                                                     "left": (300, 240), "iso": (340, 95)},
    "box": {"front": (min(p[0] for p in UP + PV) - V_FIX["fg_gap"] / 2, UP[0][1], max(p[0] for p in UP), UP[4][1])},
    "dims": [
        ("front", PV[0], PV[1], "below", 20), ("front", PV[1], PV[2], "right", 20), ("front", PV[4], PV[3], "above", 15),
    ],
    "notes": [
        "Fixed glass unit: pane 361003 in the Bohle U-profile 368004 (4 pieces, mitred) with the silicone U-seal "
        "368002 on its four held edges; the pane's half 368003 of the 180 deg magnetic seal on its free edge (HOLD).",
        "The channels sit hidden: in the base band (bottom, BASE), inside DR behind a slot in its skin (right edge and "
        "diagonal) and inside DT behind a slot in its underside (top). Their fixings come with those designs.",
        "The pane carries no closing load on its free edge: the door is held by its hinges and the catch in DT, and "
        "the magnetic seal pulls in the glass plane (PM ruling). Edge movement under 16 N spread along it: 2 mm or less.",
        "Mass about 29.6 kg (calculation; parts list).",
    ],
    "title": title("360002", "FRONT - FIXED GLASS UNIT", "Cụm vách kính cố định", "see the parts list",
                   "see the parts list", "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
}
def _ang(a, b, c):
    """Angle at b between b->a and b->c, degrees."""
    u, w = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
    return math.degrees(math.acos((u[0] * w[0] + u[1] * w[1]) / math.hypot(*u) / math.hypot(*w)))


# 368004 cut list: the 4 pieces of the U-profile, base (outer) and mouth (visible line) lengths, mitre at each corner
_PCS = [("bottom", 0, 1), ("right", 1, 2), ("diagonal", 2, 3), ("top", 3, 4)]
_CUT = [(nm, math.dist(UP[i], UP[j]), math.dist(PV[i], PV[j])) for nm, i, j in _PCS]
_MIT = {k: _ang(PV[k - 1], PV[k], PV[k + 1]) / 2 for k in (1, 2, 3)}
_GS = [V_FIX["gs_xl"] + V_FIX["gs_end"] + k * V_FIX["gs_p"] for k in range(4)]
SPECS["uprof"] = {
    "design": doc("368004", "FRONT - GLAZING U-PROFILE - BOHLE BO5201571", "CAD"),
    "drawing": doc("368004", "FRONT - GLAZING U-PROFILE - BOHLE BO5201571", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (170, 240), "top": (170, 105),
                                                                     "iso": (330, 95)},
    "box": {"front": (min(p[0] for p in UP), UP[1][1], max(p[0] for p in UP), UP[4][1]),
            "top": (min(p[0] for p in UP), -V_FIX["glass_y"] - V_FIX["gu_prof_w"] / 2, max(p[0] for p in UP),
                    -V_FIX["glass_y"] + V_FIX["gu_prof_w"] / 2)},
    "dims": [
        ("front", UP[0], UP[1], "below", 15), ("front", UP[4], UP[3], "above", 12),
        ("front", UP[1], UP[2], "right", 20), ("front", UP[2], UP[3], "right", 35), ("front", UP[0], UP[4], "left", 15),
    ],
    "notes": [
        "Bohle BO5201571 aluminium U-profile 15 x 15 x 1.5 (hardware selection C5), bought by length, cut into 4 "
        "pieces mitred at the corners, round the fixed pane's 4 held edges; the silicone U-seal 368002 goes inside.",
        "Cut list, base (outer) / mouth (visible line) length, mm: " + "; ".join(
            "%s %.1f / %.1f" % (nm, a, b) for nm, a, b in _CUT) + ". Mitres: bottom-right %.1f deg, knee %.1f deg, "
        "top-right %.1f deg from each piece's axis; the bottom and top pieces' left ends are cut along the pane's free "
        "edge, %.1f and %.1f deg to the piece." % (_MIT[1], _MIT[2], _MIT[3], _ang(PV[1], PV[0], PV[4]),
                                                    _ang(PV[3], PV[4], PV[0])),
        "HOLE TABLE, bottom piece only: 4 x dia %.1f through the base, countersunk 90 deg to dia %.1f on the inside "
        "(for ISO 10642 M3 x 8 A2 into BASE's sill rivnuts). From the piece's left end, on its underside: %s. Pod X: "
        "%s; Y %.1f (the channel's centre line), Z %.1f (underside). Tolerance +/-0.5 (PROPOSED)." % (
            V_FIX["gs_hole"], V_FIX["gs_csk"], ", ".join("%.1f" % (x - V_FIX["gs_xl"]) for x in _GS),
            ", ".join("%.1f" % x for x in _GS), -V_FIX["glass_y"], V_FIX["fg_vis_zb"] - V_FIX["gu_prof_d"]),
        "The bottom piece is screwed to BASE's sill at the factory and ships on it (PM ruling 2026-11-01); the right "
        "and diagonal pieces sit inside DR's slot, the top piece in DT's underside slot.",
        "Lengths +/-0.5, mitres +/-0.5 deg (PROPOSED). Burr-free cut ends.",
    ],
    "title": title("368004", "FRONT - GLAZING U-PROFILE - BOHLE BO5201571", "Thanh U nhôm kẹp kính",
                   "Bohle BO5201571 aluminium 15 x 15 x 1.5", "as supplied (hidden in the channels)", "1:10", "A2",
                   [("MASS", "0.56 kg (calculation)")]),
}
