"""Drawing specs for the decor blocks DR, DT, DL (350001 to 350003), run inside drawing_specs.py's namespace when this file is present (one file per sub-assembly, so each
sub-assembly's branch carries only its own specs)."""

V_DR, G_DR = _evaluate("dr_block.py")
V_DT, G_DT = _evaluate("dt_block.py")
V_DL, G_DL = _evaluate("dl_block.py")
_XL, _XR, _YF = -v["pod_w"] / 2, v["pod_w"] / 2, -v["pod_d"] / 2
_YB = _YF + v["decor_d"]
_drx0 = V_DR["fix_xtr"] + _XL                       # DR's leftmost point, at DT's underside
_drfelt = _YB - V_DR["dr_back_t"] + V_DR["dr_skin_t"] + V_DR["felt_t"]   # the felt's back face, DR's rearmost point
SPECS["dr"] = {
    "design": doc("350003", "FRONT - DECOR BLOCK ASSY - DR", "CAD"),
    "drawing": doc("350003", "FRONT - DECOR BLOCK ASSY - DR", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": {"front": (150, 255), "top": (150, 110),
                                                                     "left": (280, 255), "iso": (345, 95)},
    "box": {"front": (_drx0, V_DR["wall_z0"], _XR, V_DR["pod_h"]), "top": (_drx0, _YF, _XR, _drfelt),
            "left": (-_drfelt, V_DR["wall_z0"], -_YF, V_DR["pod_h"])},
    "dims": [
        ("front", (_XR, V_DR["wall_z0"]), (_XR, V_DR["pod_h"]), "right", 12),
        ("top", (_drx0, _YF), (_XR, _YF), "below", 10),
        ("left", (-_YB, V_DR["wall_z0"]), (-_YF, V_DR["wall_z0"]), "below", 10),
    ],
    "notes": [
        "DR (the decor detail sample): 3 mm ACP skin 351301 (EV3038 Dark Yellow) from the skeleton's measured v1 "
        "shape, bonded to the welded 6063-T6 tube frame 351306 (26 tubes, cut list in the parts list's folder); fixed "
        "back plate 351302 on the right wall's bolt line; removable access panel 351305 and felt-covered inner panel "
        "351303/351304 (D-59); the air supply assembly 350004 (D-87): intake riser 351402, transitions 351403/351405 "
        "(reserved air spaces, detail by AIR), supply fan box 351404 with two 12 V fans 618401 (HOLD).",
        "Base open inside the skins over the mesh band piece, back to the closing plate: 0.042 m2 gross less the "
        "frame's bottom tubes (PM ruling: at least 0.028 free). Air goes band, block, riser; the riser's open foot "
        "stands 140 above the base.",
        "Slot along the inner edge for the fixed pane's hidden channel: 17 wide at the glass plane (PM ruling).",
        "Opening 203 x 215 in the access panel into the air column's top (D-60 table). After the column, the inner "
        "panel and the access panel come off so the air supply assembly (14.9 kg, plug-in connectors) slides in from "
        "inside the pod (D-87); no frame tube crosses that opening.",
        "Access panel: 3 mm, 10 bolts M6 x 16 into rivnuts in the frame; the air column hangs on 2 hook studs at X 971, "
        "Z 1700 and 1850 (PM ruling 2026-11-01). Flat sheet parts (back plate, access panel, inner panel, felt) are "
        "cut from their DXFs (D-89 part 4).",
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
        "DT: 3 mm ACP skin 351201 from the skeleton's measured v1 shape, bonded to the welded 6063-T6 tube frame "
        "351204 (13 tubes); back plate 351202 bonded to the frame's back ring (its own drawing: bond area, surface prep).",
        "Slot in the underside for the fixed pane's top channel (PM ruling). Door's top: the magnetic door-stop catch "
        "368007 (Sugatsune HT-MSG62, 35 N) behind the leaf's top latch corner; the top stop 351203 with the frame-stop "
        "seal 368005 along the leaf's top, 10 short of the catch. Gap leaf to DT: 6 (PM ruling).",
        "The catch and the top stop screw into the frame's rail behind the glass's top channel. DT goes on after the "
        "door hangs and the fixed pane is in (PM rulings). DT to DR, DL and the ceiling: joints HOLD.",
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
        "DL: 3 mm ACP skin 351101 from the skeleton's measured v1 shape, bonded to the welded 6063-T6 tube frame "
        "351104 (26 tubes); back plate 351102 (flat, from its DXF, D-89 part 4).",
        "Three hinge pockets in the door-side face, 160 deep (D-30's candidate pocket), at the door unit's hinge heights: "
        "reserved spaces until a rated two-part hinge set of at least 60 kg is named (D-46, PM rulings). The hinges' "
        "frame halves ship fitted here.",
        "Hinge-side stop 351103 with the frame-stop seal 368005 on the leaf's inner face, in 4 lengths between the hinges.",
        "The door's load: hinges, the 60 x 20 hinge post behind the pockets, the frame's rings, the 60 x 20 bolt-line "
        "post, the back plate and the J-FRONT-01 bolts into the left wall (ISS-045; hinge fixing holes HOLD H01).",
    ],
    "title": title("350001", "FRONT - DECOR BLOCK ASSY - DL", "Khối trang trí trái (cụm)", "see the parts list",
                   "see the parts list", "1:10", "A2", [("DOC TYPE", "ASSEMBLY DRAWING")]),
}


def _cut_notes(G, V):
    """The frame's cut list as note lines, from the build script's own tube data."""
    import math as _m
    FLx = G["FL"]
    ev = lambda e: eval(re.sub(r"(\d)\s*mm\b", r"\1", str(e)).replace("^", "**"),
                        {"__builtins__": {}, "sqrt": _m.sqrt, "abs": abs}, V)
    rows = FLx.cut_list_rows(G["frame_members"](), ev, "")
    total = sum(float(r[4]) for r in rows) / 1000.0
    lines = ["CUT LIST (6063-T6 tube, mill finish, D-79), %d tubes, %.1f m: " % (len(rows), total) +
             "; ".join("%s %s %s L %s" % (r[1], re.sub(r"\b(Dt|Dr|Dl)\b", lambda m_: m_.group(0).upper(),
                                                        r[2].capitalize().replace("dt ", "Dt ")),
                                         r[3].replace("6063-T6 aluminium tube ", ""), r[4]) for r in rows) + "."]
    return lines


def _frame_spec(key, pn, name, vn, G, V, views, box, notes):
    return {
        "design": doc(pn, name, "CAD"), "drawing": doc(pn, name, "DWG"),
        "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05}, "views": views, "box": box, "dims": [],
        "notes": notes + _cut_notes(G, V) + [
            "Weld all round at every tube joint (TIG, 6063-T6 filler 4043); grind flush where a skin or plate bonds. "
            "Tube lengths +/-0.5, angles +/-0.5 deg, frame +/-1 overall (PROPOSED). Ends open (no caps) unless noted.",
            "Tube positions and every end cut come from the build script's parameters (frame_members); the 3D model "
            "and STEP are the reference for the joints between tubes.",
        ],
        "title": title(pn, name, vn, "aluminium EN AW-6063-T6 tube", "mill (hidden, D-79)", "1:10", "A2",
                       [("DOC TYPE", "WELDMENT DRAWING")]),
    }


SPECS["dr_frame"] = _frame_spec(
    "dr_frame", "351306", "FRONT - DECOR FRAME - DR", "Khung trang trí phải (hàn)", G_DR, V_DR,
    {"front": (150, 255), "top": (150, 110), "left": (280, 255), "iso": (345, 95)},
    {"front": (_drx0, V_DR["wall_z0"], _XR, V_DR["pod_h"])},
    ["DR's welded frame: a ring 20 inside the front skin, a ring in front of the back plates with the 80 x 20 "
     "bolt-line tube (6 holes 14 in its back wall round the J-FRONT-01 rivnut tails) and the 60 x 20 band tube, "
     "facet, chamfer and DT-joint tubes between the rings. No back-ring tube crosses the opening the air unit slides "
     "through (D-87). Rivnuts 838003 set at the factory: 10 for the access panel's bolts (6 on X 1188, 2 at "
     "Z 130, 2 at Z 2140)."])
SPECS["dr_skin"] = {
    "design": doc("351301", "FRONT - DECOR SKIN - DR", "CAD"), "drawing": doc("351301", "FRONT - DECOR SKIN - DR", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05},
    "views": {"front": (150, 255), "top": (150, 110), "left": (280, 255), "iso": (345, 95)},
    "box": {"front": (_drx0, V_DR["wall_z0"], _XR, V_DR["pod_h"])}, "dims": [
        ("front", (_XR, V_DR["wall_z0"]), (_XR, V_DR["pod_h"]), "right", 12)],
    "notes": [
        "DR's skin: 3 mm ACP (EV3038 Dark Yellow, PE core, D-12), one flat panel per outside face, edges mitred at 45 "
        "deg and joined as v1. Flat patterns 1:1 in 351301_P01_FRONT-DECOR-SKIN-DR_DXF.dxf (layers CUT and MARK).",
        "Open at the back (plates) and where DT sits on DR. Slot 17 wide along the inner edge at the glass plane for "
        "the fixed pane's hidden channel; base open over the mesh band piece (PM rulings).",
        "Bonded to the frame 351306 per the joints register's ACP bond spec. Outline +/-1 (PROPOSED).",
    ],
    "title": title("351301", "FRONT - DECOR SKIN - DR", "Tấm ốp alu khối phải", "ACP 3 mm EV3038 Dark Yellow",
                   "factory coil coating (D-12)", "1:10", "A2"),
}

SPECS["dt_frame"] = _frame_spec(
    "dt_frame", "351204", "FRONT - DECOR FRAME - DT", "Khung trang trí trên (hàn)", G_DT, V_DT,
    {"front": (190, 300), "top": (190, 220), "left": (380, 300), "iso": (190, 110)},
    {"front": (_XL, V_DT["dt_zb"], _dtx1, V_DT["pod_h"])},
    ["DT's welded frame: a back ring in front of the back plate (its slope tube 3 above DL's slope for the joint's "
     "seal, HOLD), a tube along the lower front facet, a tube laid under the top chamfer, the rail just behind the "
     "glass's top channel that the catch 368007 and the top stop 351203 screw into, and cross tubes (one over the "
     "catch)."])
SPECS["dt_skin"] = {
    "design": doc("351201", "FRONT - DECOR SKIN - DT", "CAD"), "drawing": doc("351201", "FRONT - DECOR SKIN - DT", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05},
    "views": {"front": (190, 300), "top": (190, 220), "left": (380, 300), "iso": (190, 110)},
    "box": {"front": (_XL, V_DT["dt_zb"], _dtx1, V_DT["pod_h"])},
    "dims": [("front", (_XL, V_DT["pod_h"]), (_dtx1, V_DT["pod_h"]), "above", 10)],
    "notes": [
        "DT's skin: 3 mm ACP (EV3038 Dark Yellow, PE core, D-12), one flat panel per outside face, edges mitred at 45 "
        "deg and joined as v1. Flat patterns 1:1 in 351201_P01_FRONT-DECOR-SKIN-DT_DXF.dxf (layers CUT and MARK).",
        "Open at the back, at DR and over DL's slope. Slot 17 wide in the underside at the glass plane for the fixed "
        "pane's top channel (PM ruling).",
        "Bonded to the frame 351204 per the joints register's ACP bond spec. Outline +/-1 (PROPOSED).",
    ],
    "title": title("351201", "FRONT - DECOR SKIN - DT", "Tấm ốp alu khối trên", "ACP 3 mm EV3038 Dark Yellow",
                   "factory coil coating (D-12)", "1:10", "A2"),
}
SPECS["dl_frame"] = _frame_spec(
    "dl_frame", "351104", "FRONT - DECOR FRAME - DL", "Khung trang trí trái (hàn)", G_DL, V_DL,
    {"front": (120, 255), "top": (120, 110), "left": (230, 255), "iso": (330, 95)},
    {"front": (_XL, V_DL["wall_z0"], _dlx1, V_DL["dl_zo"])},
    ["DL's welded frame carries the door (ISS-045): the hinges' frame halves screw into the 60 x 20 hinge post "
     "behind the three pockets (holes when the hinge is named, HOLD H01); the four plan rings tie it to the back "
     "ring's 60 x 20 bolt-line post (6 holes 14 round the J-FRONT-01 rivnut tails), the back plate and the bolts "
     "into the left wall."])
SPECS["dl_skin"] = {
    "design": doc("351101", "FRONT - DECOR SKIN - DL", "CAD"), "drawing": doc("351101", "FRONT - DECOR SKIN - DL", "DWG"),
    "sheet": "A2", "scale": 0.1, "scales": {"iso": 0.05},
    "views": {"front": (120, 255), "top": (120, 110), "left": (230, 255), "iso": (330, 95)},
    "box": {"front": (_XL, V_DL["wall_z0"], _dlx1, V_DL["dl_zo"])},
    "dims": [("front", (_XL, V_DL["wall_z0"]), (_XL, V_DL["dl_zo"]), "left", 12)],
    "notes": [
        "DL's skin: 3 mm ACP (EV3038 Dark Yellow, PE core, D-12), one flat panel per outside face, edges mitred at 45 "
        "deg and joined as v1. Flat patterns 1:1 in 351101_P01_FRONT-DECOR-SKIN-DL_DXF.dxf (layers CUT and MARK).",
        "Three hinge pockets in the door-side face, 164 x 44 x 124, 160 deep, at the door unit's hinge heights "
        "(reserved spaces until a rated hinge is named, D-46). Open at the back and under DT.",
        "Bonded to the frame 351104 per the joints register's ACP bond spec. Outline +/-1 (PROPOSED).",
    ],
    "title": title("351101", "FRONT - DECOR SKIN - DL", "Tấm ốp alu khối trái", "ACP 3 mm EV3038 Dark Yellow",
                   "factory coil coating (D-12)", "1:10", "A2"),
}
