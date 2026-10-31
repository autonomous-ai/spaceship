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
        "(reserved duct spaces, HOLD), supply fan box 351404 with two 12 V fans 618401 (HOLD).",
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
        "351204 (13 tubes); back plate 351202 (flat, from its DXF, D-89 part 4).",
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
