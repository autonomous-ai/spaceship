"""What each FRONT drawing shows: views, scales, dimensions, notes and title data.

Read by `render_notes.py` (offline: notes and title data become PNG images, because the drawing API can't put text
on a sheet) and by `make_drawing_front.py` (inside Fusion: views, dimensions, the projection symbol, the two
images and the PDF). One drawing per design: a Fusion base view always shows its whole design
(tools/fusion/README.md), so the part drawings use the part-only designs (`door_unit.py --arg scope=leaf`).

Model numbers come from the same parameters as the CAD: the skeleton's parameter list plus the build scripts'
own lists, evaluated here without Fusion (`values()`), so a dimension target always matches the model.

Views, first angle (conventions.md section 3): front looks toward +Y (X right, Z up); the view from above sits
BELOW it (X right, Y up); the view from the left (looking toward +X) sits to its RIGHT (2D X = -Y, 2D Y = Z).
Sheet coordinates in mm, origin bottom left.
"""

import csv
import glob
import math
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAD = os.path.join(REPO, "v2", "01-CAD-Native", "front")
REV = "P01"
SHEETS = {"A1": (841.0, 594.0), "A2": (594.0, 420.0), "A3": (420.0, 297.0)}
IMG_W = 170.0


def _evaluate(script):
    """Every parameter of a FRONT build script (skeleton list + library + own), in mm, without Fusion."""
    for m in ("adsk", "adsk.core", "adsk.fusion"):
        sys.modules.setdefault(m, types.ModuleType(m))
    sys.modules["adsk"].core = sys.modules["adsk.core"]
    sys.modules["adsk"].fusion = sys.modules["adsk.fusion"]
    g = {"SCRIPT_ARGS": {"repo_root": REPO}, "__file__": os.path.join(CAD, script), "__name__": "front_spec"}
    exec(compile(open(g["__file__"], encoding="utf-8").read(), g["__file__"], "exec"), g)
    lib = g["L"]
    params, _path, _rev = lib.load_skeleton_params(REPO)
    lists = [params, lib.LIB_PARAMS, lib.GLASS_PARAMS] + ([g["OWN"]] if "OWN" in g else [])
    env = {"abs": abs, "sqrt": math.sqrt}
    for lst in lists:
        for name, expr, *_ in lst:
            env[name] = eval(re.sub(r"(\d)\s*mm\b", r"\1", expr).replace("^", "**"), {"__builtins__": {}}, env)
    return env, g


V_DOOR, G_DOOR = _evaluate("door_unit.py")


def latch_x(z, v=V_DOOR):
    return -v["pod_w"] / 2 + v["door_xbr"] - (v["door_xbr"] - v["door_xtr"]) * (z - v["door_zb"]) / (v["door_zt"] - v["door_zb"])


COMMON_NOTES = [
    "UNITS: mm. Angles in degrees. Mass in kg.",
    "Projection: first angle (ISO 5456-2). The front view looks toward +Y, at the door from outside the pod; the view "
    "from above is below it; the view from the left is to its right. 2D axes: front X(2D)=X, Y(2D)=Z; above "
    "X(2D)=X, Y(2D)=Y; left X(2D)=-Y, Y(2D)=Z (guideline 3.3). Coordinates are the pod's (conventions 4).",
    "No ISO 2768 class on glass, seals or sandwich parts (conventions 3). Tolerances given here are PROPOSED from "
    "function until the maker confirms what it holds.",
    "Status DRAFT P01: for the prototype and the factory's door sample only, not released (conventions 8).",
    "Why each feature is where it is: v2/02-Drawings/front/FEATURE-RATIONALE.md. Parts list: "
    "v2/03-Manufacturing/front/*_BOM.csv.",
]


def title(pn, name, vn, material, finish, scale, sheet, extra=()):
    return [("PART NO.", pn), ("NAME", name), ("TÊN", vn), ("REV / STATUS", "%s / DRAFT" % REV),
            ("MATERIAL", material), ("FINISH", finish), ("SCALE", scale), ("UNITS", "mm"),
            ("PROJECTION", "first angle"), ("SHEET", sheet)] + list(extra)


def image_places(sheet):
    w, h = SHEETS[sheet]
    return {"notes": (w - 20.0 - IMG_W, h - 15.0), "title": (w - 20.0 - IMG_W, 150.0)}


def doc(pn, name, doctype):
    return "%s_%s_%s_%s" % (pn, REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype)


v = V_DOOR
X0, X1 = v["kick_x0"], v["kick_x1"]                       # hinge edge, strip end under the latch edge
ZLB, ZB, ZT = v["door_zb"] - v["door_glass_engage"], v["door_zb"], v["leaf_zt"]
XT = latch_x(ZT)
KZB = v["kick_zb"]
KY0, KY1 = -v["glass_y"] - v["kick_d"] / 2, -v["glass_y"] + v["kick_d"] / 2
UY0, UY1 = -v["glass_y"] - v["gu_w"] / 2, -v["glass_y"] + v["gu_w"] / 2

# dims: (view, (u1, v1), (u2, v2), side, gap). u, v are the view's own 2D axes in model mm; the make script maps them
# onto the sheet from the view's extent and snaps each end to the nearest view vertex.
SPECS = {
    "leaf": {
        "design": doc("361001", "FRONT - DOOR LEAF - 4+4 LAMINATED", "CAD"),
        "drawing": doc("361001", "FRONT - DOOR LEAF - 4+4 LAMINATED", "DWG"),
        "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (190, 225), "iso": (320, 100)},
        "box": {"front": (X0, ZLB, X1, ZT)},
        "dims": [
            ("front", (X0, ZLB), (X1, ZLB), "below", 12), ("front", (X0, ZLB), (X0, ZT), "left", 12),
            ("front", (X0, ZT), (XT, ZT), "above", 10), ("front", (X1, ZLB), (X1, ZB), "right", 8),
            ("front", (X0, ZLB), (XT, ZT), "right", 30),
        ],
        "notes": [
            "Glass: 4+4 laminated safety glass, two toughened, heat-soaked panes (EN 12150, EN 14179) with 0.76 mm "
            "grey PVB, 8.76 nominal (D-27, D-46). Product HOLD until the supplier names one (ISS-074).",
            "Outline 1:1 in 361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_DXF.dxf (origin: the hinge edge at the leaf "
            "bottom; X right, Y up, seen from outside). The leaf's visible outline is the skeleton's measured v1 "
            "trapezoid; the bottom %.0f mm sit inside the kick strip, and its latch side there runs straight down." % v["door_glass_engage"],
            "No holes, notches or cut-outs until the hinges and pull are named (PM ruling). The hinge, pull and "
            "catch positions on the unit drawing are reserved spaces only.",
            "Edges: ground and arrised before toughening. Tolerances (PROPOSED, the glass supplier confirms): sizes "
            "+/-1, diagonals +/-1, thickness to the supplier's standard.",
            "Datums: A = the hinge edge (X %.0f), B = the bottom edge (Z %.0f). The top is %.0f mm below DT's "
            "underside for the magnetic catch (PM ruling)." % (X0, ZLB, v["dt_zb"] - ZT),
        ],
        "title": title("361001", "FRONT - DOOR LEAF - 4+4 LAMINATED", "Tấm kính cửa 4+4",
                       "4+4 laminated toughened heat-soaked glass, grey PVB", "edges ground and arrised", "1:10", "A2",
                       [("MASS", "43.9 kg (calculation)")]),
    },
    "kick": {
        "design": doc("361002", "FRONT - DOOR KICK STRIP", "CAD"),
        "drawing": doc("361002", "FRONT - DOOR KICK STRIP", "DWG"),
        "sheet": "A2", "scale": 0.2, "scales": {"left": 2.0}, "views": {"front": (170, 300), "top": (170, 250),
                                                                         "left": (345, 230), "iso": (170, 120)},
        "box": {"front": (X0, KZB, X1, ZB), "top": (X0, KY0, X1, KY1), "left": (-KY1, KZB, -KY0, ZB)},
        "dims": [
            ("front", (X0, KZB), (X1, KZB), "below", 10), ("front", (X0, KZB), (X0, ZB), "left", 10),
            ("left", (-KY1, KZB), (-KY0, KZB), "below", 10), ("left", (-KY1, KZB), (-KY1, ZB), "left", 12),
            ("left", (-UY1, ZB), (-UY0, ZB), "above", 8),
            ("left", (-UY0, ZB - v["kick_pocket_d"]), (-UY0, ZB), "right", 10),
            ("left", (-UY0, KZB), (-UY0, KZB + v["kick_cav_h"]), "right", 22),
        ],
        "notes": [
            "Aluminium EN AW-6063-T6 hollow extrusion (D-85), custom die; black anodised matte, 20 um (AA20, D-67), "
            "as the base band. Section 1:1 in 361002_P01_FRONT-DOOR-KICK-STRIP_DXF.dxf.",
            "Cut length %.0f (-1/0), square ends. Chamber ends sealed with black sealant flush with the end faces." % (X1 - X0),
            "Top pocket %.0f wide x %.0f deep takes the Bohle BO5201735 silicone U-seal and the leaf's bottom %.0f mm; "
            "bottom cavity %.0f wide x %.0f tall takes the athmer Schall-Ex GSA drop seal, bonded to the pod-side wall "
            "(bond to anodised aluminium HOLD)." % (v["gu_w"], v["kick_pocket_d"], v["door_glass_engage"], v["gu_w"], v["kick_cav_h"]),
            "Floor gap: the strip's bottom stands %.0f over the threshold top (the drop seal's rated gap). How the strip "
            "is held on the glass is HOLD J-FRONT-02 (structural silicone or a clamp)." % v["kick_gap"],
            "Tolerances (PROPOSED): pocket and cavity widths 12 +0.3/0; height %.0f +/-0.2; skins 1.0 +/-0.1." % (ZB - KZB),
        ],
        "title": title("361002", "FRONT - DOOR KICK STRIP", "Thanh chân cửa nhôm", "aluminium EN AW-6063-T6",
                       "black anodised matte 20 um (AA20)", "1:5, section 2:1", "A2", [("MASS", "1.1 kg (calculation)")]),
    },
    "door_unit": {
        "design": doc("360001", "FRONT - DOOR UNIT", "CAD"),
        "drawing": doc("360001", "FRONT - DOOR UNIT", "DWG"),
        "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (150, 250), "top": (150, 120),
                                                                         "left": (290, 250), "iso": (340, 95)},
        "box": {"front": (v["hinge_x0"], KZB, X1, ZT + v["st_top"])},
        "dims": [
            ("front", (X0, KZB), (X1, KZB), "below", 12), ("front", (X0, KZB), (X0, ZT), "left", 30),
            ("front", (X0, ZB), (X0, ZT), "left", 18), ("front", (X1, KZB), (X1, ZB), "right", 10),
        ],
        "notes": [
            "Door unit (D-56): leaf 361001, kick strip 361002 with the drop seal 368001 in its cavity and the U-seal "
            "368002 in its pocket; the strike 368102 of the magnetic catch in DT; the door's half 368006 of the 180 deg "
            "magnetic seal; three hinges 368101 and the pull 368103 as reserved spaces (red), HOLD.",
            "No latch on the glass (PM ruling): the 35 N magnetic door-stop catch (Sugatsune HT-MSG62) in DT's underside "
            "holds the door at its top latch corner; the hinges hold it at its closed position; the 180 deg magnetic "
            "seal pulls edge to edge in the glass plane, so the fixed pane's free edge carries no closing load.",
            "Hinges (HOLD): rated for the 8.76 laminate, at least 60 kg and the 1176 width; two-part lift-off, frame "
            "halves shipped fitted in DL; hung on site with the 5 mm key. No holes in the glass until named.",
            "Mass of the unit as it hangs: about 48.5 kg (calculation; parts list).",
            "Gaps: 6 to DT (the catch), 4 to the fixed glass (the seal), %.0f under the strip to the threshold." % v["kick_gap"],
        ],
        "title": title("360001", "FRONT - DOOR UNIT", "Cụm cửa kính", "see the parts list", "see the parts list",
                       "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
    },
}
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
        "Fit order: the band's channel, the pane, DR from the side, DT from above (PM ruling).",
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
V_DR, G_DR = _evaluate("dr_block.py")
V_DT, G_DT = _evaluate("dt_block.py")
V_DL, G_DL = _evaluate("dl_block.py")
_XL, _XR, _YF = -v["pod_w"] / 2, v["pod_w"] / 2, -v["pod_d"] / 2
_YB = _YF + v["decor_d"]
_drx0 = V_DR["fix_xtr"] + _XL                       # DR's leftmost point, at DT's underside
SPECS["dr"] = {
    "design": doc("350003", "FRONT - DECOR BLOCK ASSY - DR", "CAD"),
    "drawing": doc("350003", "FRONT - DECOR BLOCK ASSY - DR", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (150, 255), "top": (150, 110),
                                                                     "left": (280, 255), "iso": (345, 95)},
    "box": {"front": (_drx0, V_DR["wall_z0"], _XR, V_DR["pod_h"]), "top": (_drx0, _YF, _XR, _YB + V_DR["felt_t"]),
            "left": (-(_YB + V_DR["felt_t"]), V_DR["wall_z0"], -_YF, V_DR["pod_h"])},
    "dims": [
        ("front", (_XR, V_DR["wall_z0"]), (_XR, V_DR["pod_h"]), "right", 12),
        ("top", (_drx0, _YF), (_XR, _YF), "below", 10),
        ("left", (-_YB, V_DR["wall_z0"]), (-_YF, V_DR["wall_z0"]), "below", 10),
    ],
    "notes": [
        "DR stage 1 (the decor detail sample): 3 mm ACP skin 351301 (EV3038 Dark Yellow) shelled from the skeleton's "
        "measured v1 shape, back plate 351302, removable felt-covered inner panel 351303/351304 (D-59), and the air "
        "supply assembly 350004 (D-87): intake riser 351402, transitions 351403/351405 (reserved duct spaces, HOLD), "
        "supply fan box 351404 with two 12 V fans 618401 (HOLD).",
        "Base open inside the skins over the mesh band piece, back to the closing plate: 0.042 m2 gross (PM ruling, at "
        "least 0.028 free). Air goes band, block, riser; the riser's open foot stands 60 above the base.",
        "Slot along the inner edge for the fixed pane's hidden channel: 17 wide at the glass plane (PM ruling).",
        "Opening 203 x 215 in the back plate into the air column's top (D-60 table). The back plate and the inner panel "
        "come off so the air supply assembly (14.9 kg, plug-in connectors) slides in from inside the pod (D-87).",
        "The aluminium frame inside the skin is stage 2; until then no fixing hole is shown.",
    ],
    "title": title("350003", "FRONT - DECOR BLOCK ASSY - DR", "Khối trang trí phải (cụm)", "see the parts list",
                   "see the parts list", "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
}
_dtx1 = V_DT["dt_xr"] + _XL
SPECS["dt"] = {
    "design": doc("350002", "FRONT - DECOR BLOCK ASSY - DT", "CAD"),
    "drawing": doc("350002", "FRONT - DECOR BLOCK ASSY - DT", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (190, 300), "top": (190, 220),
                                                                     "left": (380, 300), "iso": (190, 110)},
    "box": {"front": (_XL, V_DT["dt_zb"] - V_DT["ca_h"], _dtx1, V_DT["pod_h"])},
    "dims": [("front", (_XL, V_DT["pod_h"]), (_dtx1, V_DT["pod_h"]), "above", 10)],
    "notes": [
        "DT stage 1: 3 mm ACP skin 351201 shelled from the skeleton's measured v1 shape, back plate 351202.",
        "Slot in the underside for the fixed pane's top channel (PM ruling). Door's top: the magnetic door-stop catch "
        "368007 (Sugatsune HT-MSG62, 35 N) behind the leaf's top latch corner; the top stop 351203 with the frame-stop "
        "seal 368005 along the leaf's top, 10 short of the catch. Gap leaf to DT: 6 (PM ruling).",
        "DT goes on after the door hangs and the fixed pane is in (PM rulings). Frame and fixings: stage 2.",
    ],
    "title": title("350002", "FRONT - DECOR BLOCK ASSY - DT", "Khối trang trí trên (cụm)", "see the parts list",
                   "see the parts list", "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
}
_dlx1 = V_DL["dl_w"] + _XL
SPECS["dl"] = {
    "design": doc("350001", "FRONT - DECOR BLOCK ASSY - DL", "CAD"),
    "drawing": doc("350001", "FRONT - DECOR BLOCK ASSY - DL", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (120, 255), "top": (120, 110),
                                                                     "left": (230, 255), "iso": (330, 95)},
    "box": {"front": (_XL, V_DL["wall_z0"], _dlx1 + V_DL["stop_reach"], V_DL["dl_zo"])},
    "dims": [("front", (_XL, V_DL["wall_z0"]), (_XL, V_DL["dl_zo"]), "left", 12)],
    "notes": [
        "DL stage 1: 3 mm ACP skin 351101 shelled from the skeleton's measured v1 shape, back plate 351102.",
        "Three hinge pockets in the door-side face, 160 deep (D-30's candidate pocket), at the door unit's hinge heights: "
        "reserved spaces until a rated two-part hinge set of at least 60 kg is named (D-46, PM rulings). The hinges' "
        "frame halves ship fitted here.",
        "Hinge-side stop 351103 with the frame-stop seal 368005 on the leaf's inner face, in 4 lengths between the hinges.",
        "Bolted to the left wall (J-FRONT-01): rivnut plate HOLD-10. Frame (door moment, ISS-045) and fixings: stage 2.",
    ],
    "title": title("350001", "FRONT - DECOR BLOCK ASSY - DL", "Khối trang trí trái (cụm)", "see the parts list",
                   "see the parts list", "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
}
ORDER = ["door_unit", "leaf", "kick", "fixed_unit", "pane", "dr", "dt", "dl"]

for _k, _sp in SPECS.items():
    _sp["images"] = image_places(_sp["sheet"])
    _sp["notes"] = list(_sp["notes"]) + COMMON_NOTES
