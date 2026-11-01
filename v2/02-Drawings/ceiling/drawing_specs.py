"""What each ceiling drawing shows: views, scale, dimensions, notes and title data.

Read by `render_notes.py` (offline: the notes and title data become PNG images,
because the drawing API can't put text on a sheet) and by `make_drawing_ceiling.py`
(inside Fusion: views, dimensions, hole tables, the projection symbol, the two
images, and the PDF). One drawing per design, because a Fusion base view always
shows its own design (tools/fusion/README.md).

Sheet coordinates in mm, origin bottom left. Fusion's ISO A2 sheet is 594 x 420
with its title block in the bottom right corner; the title data image sits just
above it, the notes image top right.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
import ceiling_model as M  # noqa: E402

SHEETS = {"A1": (841.0, 594.0), "A2": (594.0, 420.0)}
# Fusion's ISO title block sits in the bottom right corner, about 200 x 52 mm inside the
# 10 mm border (measured on the Phase 0 proof PDF); the title data image goes above it
IMG_W = 170.0                   # both images are this wide on the sheet, mm
PX_MM = 10.0                    # the images are drawn at 10 px per mm (render_notes.py)
# Sheet.images.insert puts any PNG in at this width at scale 1, whatever its pixels or DPI tag
# (a 1000 px image and the 1700 px notes of the first rib sample both came out 58.0 mm wide,
# 2026-10-31 and 2026-11-01), so each image is inserted at scale = its width / this
FUSION_IMG_W = 58.02
LABEL_GAP = 3.0                 # a view's scale label sits this far below the view, mm
# views drawn with hidden lines (the rest show visible edges only); make_drawing_ceiling.py sets
# the style again after making the view, as Fusion ignores the one given on the input
STYLES = {"tray": {"front": "hidden", "top": "hidden", "left": "hidden"}, "cassette": {"top": "hidden"}}
# the part axis each view's 2D X and Y run along (guideline 3.3; the left view's X is -Y)
AXES = {"front": ("X", "Z"), "top": ("X", "Y"), "left": ("Y", "Z")}


HOLE_TABLE_ROOM = 55.0          # mm at the sheet's top right: Fusion puts a hole table there and the API can't move
                                # it (the tray's first drawing, 2026-11-01: 30 mm tall with one row), so the notes start lower


def image_places(sheet, holes=False):
    w, h = SHEETS[sheet]
    return {"notes": (w - 20.0 - IMG_W, h - 15.0 - (HOLE_TABLE_ROOM if holes else 0.0)), "title": (w - 20.0 - IMG_W, 150.0)}


SYMBOL_PX_MARGIN = 1.0          # mm of white round the symbol in its picture


def symbol_place(sheet):
    """Where the first-angle symbol's outline starts (its narrow end's middle, sheet mm): the shared helper's place
    (tools/fusion/fusion_drawing.py default_symbol_place), just left of the 180 x 47 title block and 6 clear of it
    and of the frame. The symbol goes on the sheet as a picture: Fusion's PDF export of a sketch chain lost a corner
    on A1 even in a sketch of its own and clear of every border (the tray and cassette, 2026-11-01)."""
    w, _h = SHEETS[sheet]
    return (w - 10.0 - 180.0 - 6.0 - 24.0, 10.0 + 6.0 + 5.0)


def scale_text(scale):
    """1:5, 2:1, 1:10 ..."""
    return ("%g:1" % round(scale, 3)) if scale >= 1 else ("1:%g" % round(1 / scale, 3))


def labels(sp):
    """{view: text} for each view drawn at another scale than the sheet's (ISO 5455: that
    scale goes next to the view; the sheet's own is in the title data)."""
    return {k: "SCALE " + scale_text(x) for k, x in sorted(sp["scales"].items()) if abs(x - sp["scale"]) > 1e-9}


def new_size(done, axis, value, tol=0.05):
    """True, and recorded in done, when no dimension along this part axis has this size yet:
    each size is dimensioned once on a drawing (ISO 129-1). done is a list of (axis, mm)."""
    if any(a == axis and abs(v - value) <= tol for a, v in done):
        return False
    done.append((axis, value))
    return True

COMMON_NOTES = [
    "UNITS: mm. Angles in degrees. Mass in kg.",
    "Projection: first angle (ISO 5456-2). Views: front looks toward +Y; "
    "the view from above is below it; the view from the left is to its right.",
    "2D axes: front view X(2D)=X, Y(2D)=Z; view from above X(2D)=X, Y(2D)=Y; "
    "view from the left X(2D)=-Y, Y(2D)=Z (guideline 3.3).",
    "Dimensions run from the datum faces named in these notes (overall sizes where none is named), and to hole centres. "
    "No ISO 2768 class is applied (conventions 3); the tolerances in note 1 are assumptions "
    "until the factory confirms what it holds.",
    "Status DRAFT P01: for the prototype and the factory's sample only, not released.",
    "Why each feature is where it is: v2/02-Drawings/ceiling/FEATURE-RATIONALE.md.",
]


def doc_name(key, doctype):
    pn, name, _vn, _k, _m = M.PARTS[key]
    return "%s_%s_%s_%s" % (pn, M.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype)


def spec(key, scale, notes, views=None, holes=None, title_extra=(), sheet="A1", scales=None, faces=None, sizes=None):
    """A1 layout: the front view top left, the view from above below it, the view from the
    left to its right (first angle), the isometric view below that; notes top right, title
    data above the title block. faces: {view: ["bottom"]} adds the width of that face of the view where it is a
    size of its own (the rib's crown; the overall width is measured face to face, so a crown narrower than the
    flanges needs its own). sizes: every dimension value the drawing must print, once each (check_drawing_pdf.py
    reads them back), taken from the model's values and the notes."""
    pn, name, vn, kind, mat = M.PARTS[key]
    mname = M.MATERIALS[mat][0] if mat else "see the parts list"
    v = dict(front=(200, 480), top=(200, 290), left=(480, 480), iso=(500, 260)) if sheet == "A1" else \
        dict(front=(150, 330), top=(150, 200), left=(330, 330), iso=(320, 160))
    v.update(views or {})
    return {
        "key": key, "design": doc_name(key, "CAD"), "drawing": doc_name(key, "DWG"),
        "scale": scale, "scales": scales or {}, "views": v, "holes": holes, "sheet": sheet,
        "faces": faces or {}, "sizes": list(sizes or []),
        "styles": STYLES.get(key, {}),
        "images": image_places(sheet, bool(holes)),
        "title": [("PART NO.", pn), ("NAME", name), ("TÊN", vn), ("REV / STATUS", "%s / DRAFT" % M.REV),
                  ("MATERIAL", mname), ("FINISH", M.FINISH.get(key, "-")),
                  ("SCALE", scale_text(scale) + "".join(", %s view %s" % (k, scale_text(x))
                                                         for k, x in sorted((scales or {}).items()))),
                   ("UNITS", "mm"), ("PROJECTION", "first angle"), ("SHEET", sheet)]
        + list(title_extra),
        "notes": list(notes) + COMMON_NOTES,
    }


SPECS = {
    "tray": spec("tray", 0.2, [
        "Tolerances (assumption): laser-cut outline and holes +/-0.2; bent sizes +/-0.5; hole position +/-0.3 from datums.",
        "Galvanised steel DX51D+Z, 0.5 thick (D-37). Inside bend radius = thickness; K 0.44 "
        "(assumptions until a bend coupon on the factory's tooling sets them).",
        "Flat pattern: 513101_P01_LINING-TRAY-CEILING_DXF.dxf (layers CUT, BEND, MARK).",
        "Datums: A = top face of the base; B = outer face of the front return; C = centre plane (X' = 0).",
        "Returns run the full 34 depth and turn in as 12 lips under the felt (PM ruling; guideline 8.2).",
        "Two holes for ELECTRICAL's cable bushings, one in each of the front and back returns, on datum C (PM ruling "
        "2026-11-01): size and height dimensioned in the front view, where the back one lies hidden behind the front one. "
        "No hole table: Fusion's table printed empty on this view twice (2026-11-01).",
        "Clip and catch fixing zones on the base: no holes until a clip and a catch are named (HOLD-08).",
        "Symmetric about datum C: one part for both ceiling halves.",
    ], holes=None, sizes=["1160", "1045", "34", "580", "12.5", "Ø19.1"]),
    "rib": spec("rib", 0.2, [
        "Tolerances (assumption): cut length +/-1; bent sizes +/-0.5.",
        "Galvanised steel DX51D+Z, 0.5 thick, hat section: crown 20, height 24, flanges 2 x 12 (assumptions).",
        "Blank and bend lines: 513102_P01_LINING-RIB-CEILING_DXF.dxf.",
        "Fixing to the tray and to the felt: HOLD (H09), drawn as touching only.",
        "Two per cassette, at X' = +/- cs_w/6 (three equal felt spans).",
        "The front view (the hat section) is drawn at 2:1 so the bends read; the other views at 1:5.",
    ], sheet="A2", scales={"front": 2.0}, views={"front": (110, 360), "top": (110, 200), "left": (260, 360), "iso": (300, 180)},
        faces={"front": ["bottom"]}, sizes=["44", "1034", "20", "24"]),
    "felt": spec("felt", 0.2, [
        "Tolerances (assumption): knife-cut outline +/-1.",
        "PET felt 9, Dark Gray (D-79); the factory's felt (D-31), its emission certificate on HOLD.",
        "Cut file: 513201_P01_LINING-FELT-CEILING_DXF.dxf. No holes: the lights are on the wall-top light shelf (D-70).",
        "Marked zones (MARK layer): two reserved sprinkler drop zones D150 (REQ-US-01); nothing cut.",
        "Sits on the tray's 12 lips; fixing to the ribs HOLD (H09).",
    ]),
    "fill_a": spec("fill_a", 0.2, [
        "Tolerances (assumption): cut sizes +/-2; thickness as supplied.",
        "PET fill 40, 25 kg/m3 by default (D-81; the wall sample's T02 confirms it, else 32).",
        "Cut file: 513301_P01_LINING-FILL-CEILING-BAY-A_DXF.dxf. Notches clear the clips and catches by 5.",
        "Fixing to the tray's back: HOLD (H10); gravity holds it in service.",
    ]),
    "fill_b": spec("fill_b", 0.2, [
        "Tolerances (assumption): cut sizes +/-2; thickness as supplied.",
        "PET fill 40, 25 kg/m3 by default (D-81; the wall sample's T02 confirms it, else 32).",
        "Cut file: 513302_P01_LINING-FILL-CEILING-BAY-B_DXF.dxf. Notches clear the clips by 5.",
        "Fixing to the tray's back: HOLD (H10).",
    ]),
    "fill_c": spec("fill_c", 0.2, [
        "Tolerances (assumption): cut sizes +/-2; thickness as supplied.",
        "PET fill 40, 25 kg/m3 by default (D-81; the wall sample's T02 confirms it, else 32).",
        "Cut file: 513303_P01_LINING-FILL-CEILING-BAY-C_DXF.dxf. Notches clear the clips by 5.",
        "Fixing to the tray's back: HOLD (H10).",
    ]),
    "cassette": spec("cassette", 0.2, [
        "Tolerances: see the part drawings; the assembled outline 1160 x 1045 x 74 +/-1: the tray 34 deep and the "
        "fill 40 on its back (assumption).",
        "Ceiling lining cassette, one part for both halves (C1-CASS, C2-CASS). Drawing D06 of the wall-and-door sample.",
        "Parts: 513101 tray 1, 513102 rib 2, 513201 felt 1, 513301 / 513302 / 513303 fill 1 each, "
        "518001 clip 6 (HOLD), 518002 safety catch 2 (HOLD).",
        "Clips on the back faces of ceiling cross members X1, X2, X3, over the ribs; catches on X2's front face (D-47).",
        "Hangs 4 below the ceiling frame and never touches it except through the clips and catches (D-17).",
        "Cables run in the 24 gap and clip to the tray only (D-26, D-41).",
        "The two cable bushing holes are the tray's, sized and placed on its drawing 513101.",
    ], sizes=["1160", "1045", "74"]),
}



def _vals():
    return M.evaluate(M.all_params())


def frame_hole_notes(half):
    """The frame's joint holes as text lines, from datums A (the closing face), B (the front
    member's front face) and C (the frame's underside), from ceiling_model.hole_positions."""
    v = _vals()
    a, b, c = v["close_gap"] / 2, M.ev(v, M.YW), M.ev(v, M.ZF0)
    rows = {}
    for name, d, (x, y, z) in M.hole_positions(v, half):
        rows.setdefault((name, d), []).append((abs(x) - a, y - b, z - c))
    where = {"SIDE BOLT CLEARANCE": "side member, outer wall", "SIDE BOLT ACCESS": "side member, inner wall",
             "SEAM PIN CLEARANCE": "seam member, closing face", "SEAM PIN RIVNUT": "seam member, closing face (rivnut 838003)",
             "SEAM PIN ACCESS": "seam member, inner wall", "BACK RIVNUT": "back member, underside (rivnut 838003 on stop washer 831002)",
             "BACK SPIGOT ROUND": "back member, underside", "BACK SPIGOT SLOT": "back member, underside, slot 14 long along X",
             "SOFFIT HANGER FRONT": "front member, underside (rivnut 838003 for the AIR soffit's hanger stud, D-87)",
             "SOFFIT HANGER X1": "cross member X1, underside (rivnut 838003 for the AIR soffit's hanger stud, D-87)",
             "SOFFIT LOCK": "front member, underside (rivnuts 838003 for the soffit's two captive lock screws, D-87)"}
    out = []
    for (name, d), pts in rows.items():
        if name.startswith(("BACK", "SOFFIT")):
            pos = "from A: %s; from B: %s" % (", ".join("%.2f" % p[0] for p in pts), ", ".join(sorted({"%.2f" % p[1] for p in pts})))
        else:
            pos = "from B: %s; from C: %.2f" % (", ".join("%.2f" % p[1] for p in pts), pts[0][2])
        out.append("%s: Ø%.2f x %d, %s; %s." % (name, d, len(pts), where[name], pos))
    return out


FRAME_VIEWS = {"front": (170, 520), "top": (170, 300), "left": (470, 520), "iso": (470, 250)}


def frame_spec(key, half):
    v = _vals()
    side = "C1 (-X half)" if half == "C1" else "C2 (+X half)"
    fit = ("4 rivnuts 838003 on stop washers 831002 in the back member; 4 captive M6 x 16 bolts 838001 with "
           "washers 838004 and retainers 838005 in the side member; joint gasket 848001 on the back member's "
           "underside; bulb seal 848004 on the closing face") if half == "C1" else \
          ("8 rivnuts 838003 (4 on stop washers 831002 in the back member, 4 for the pins in the seam member); "
           "4 captive M6 x 16 bolts 838001 with washers 838004 and retainers 838005 in the side member; "
           "4 M6 x 25 pins 838002 with washers 838004 in the seam member's rivnuts; joint gasket 848001 on "
           "the back member's underside")
    return spec(key, 0.2, [
        "Tolerances (assumption until the factory confirms): tube cut length +/-0.5; holes +/-0.2 from the round "
        "spigot hole (R-J6); spigot positions and round spigot hole to the closing face +/-0.1 (ST-04).",
        "Aluminium 6063-T6 tube (alloy ISS-034): 20 x 40 x 1.2, back member 40 x 40 x 1.2 (R-J3). Mill finish "
        "with the bond prep (D-79). Frame %s, %.2f wide (skeleton half_fw), %.2f deep." % (side, v["half_fw"], v["wall_depth"]),
        "Datums: A = the closing face (the seam member's outer face, %.2f from X 0); B = the front member's front "
        "face (Y %.2f); C = the frame's underside (Z %.2f)." % (v["close_gap"] / 2, M.ev(v, M.YW), M.ev(v, M.ZF0)),
        "Members (cut list 410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv): side and seam %.2f, front and cross members "
        "X1-X3 %.2f, back %.2f; cross members at %.2f pitch from B. Frame joints HOLD (H11)." % (
            v["wall_depth"] - v["back_w"], v["half_fw"] - 2 * v["tube_w"], v["half_fw"], v["fr_pitch"]),
        "Joint holes (joints register 2.9; the register owns the bolt lines, PM ruling 2026-10-31):",
    ] + frame_hole_notes(half) + [
        "1 x 45 deg lead-in on the closing face's lower edge, seam member and back member end (R-J9).",
        "Every bolt is 30 or more from any member that meets its own (R-J14); none sits under the roof slot (D-60).",
        "Fitted in the factory: " + fit + ".",
    ], holes="left", views=FRAME_VIEWS, scales={"iso": 0.1})


def skin_spec(key, half):
    v = _vals()
    notes = [
        "Tolerances (assumption until the factory confirms): routed outline and cut-outs +/-0.5.",
        "ACP 3, EV3038 Dark Yellow (D-12; build plan VT01), %.2f x %.2f (skeleton half_pw x wall_depth)." % (
            v["half_pw"], v["wall_depth"]),
        "Datums: A = the closing-seam edge (X %s%.2f); B = the front edge (Y %.2f)." % (
            "-" if half == "C1" else "", v["seam_gap"] / 2, M.ev(v, M.YW)),
        "Bonded to frame %s with the bond set 108002 (bond line %.0f, skeleton bond_t); it overhangs its frame by "
        "%.2f at the closing seam (half_pw - half_fw) and is flush with it at the side." % (
            "411101" if half == "C1" else "411102", v["bond_t"], v["half_pw"] - v["half_fw"]),
        "Cut file: %s_P01_CEILING-SKIN-%s_DXF.dxf (seen from above, origin at A on B)." % (M.PARTS[key][0], half),
    ]
    if half == "C2":
        x0 = v["slot_x0"] - v["seam_gap"] / 2
        y0 = v["slot_y0"] - M.ev(v, M.YW)
        notes.append("Roof exhaust slot %.0f x %.0f (D-61), through: from A %.2f to %.2f, from B %.2f to %.2f; "
                     "the roof grille and sleeve belong to AIR (610000)." % (
                         v["slot_w"], v["slot_d"], x0, x0 + v["slot_w"], y0, y0 + v["slot_d"]))
    return spec(key, 0.2, notes, views=FRAME_VIEWS, scales={"iso": 0.1})


def fill_table():
    """D-89 tabulated drawing: the three fill strips (one drawing, drawn from 513301)."""
    v = _vals()
    rows, seen = [], set()
    for key, bay, box, notches in M.fill_strips(v):
        if key in seen:
            continue
        seen.add(key)
        b = [M.ev(v, e) for e in box]
        ns = []
        for _n, nb in notches:
            n = [M.ev(v, e) for e in nb]
            if M.overlap(tuple(b), tuple(n)):
                ns.append("%.1f x %.1f at X' %.1f, %s edge" % (min(n[1], b[1]) - max(n[0], b[0]), min(n[3], b[3]) - max(n[2], b[2]),
                                                             (max(n[0], b[0]) + min(n[1], b[1])) / 2,
                                                             "front" if abs(max(n[2], b[2]) - b[2]) < 1e-6 else "back"))
        rows.append("%s %s: %.1f x %.1f x %.0f, notches %s." % (
            M.PARTS[key][0], M.PARTS[key][1].split(" - ")[-1], b[1] - b[0], b[3] - b[2], v["fill_t"], "; ".join(ns) or "none"))
    return rows


def tabulated(sp, drawing, covers, extra_notes):
    sp = dict(sp)
    sp["drawing"] = drawing
    sp["title"] = [(k, ("%s (this sheet also covers %s)" % (val, ", ".join(covers)) if k == "PART NO." else val))
                   for k, val in sp["title"]]
    sp["notes"] = list(extra_notes) + sp["notes"]
    return sp


SPECS.update({
    "frame_c1": frame_spec("frame_c1", "C1"), "frame_c2": frame_spec("frame_c2", "C2"),
})
# D-89 (PM ruling 2026-11-01): identical or mirrored parts share one tabulated drawing; a plain
# knife-cut felt or fill rectangle needs none when the cut list gives its size, material,
# tolerance and part number (the felt 513201: its row in 410000_P01_CEILING-PARTS-LIST_BOM.csv)
SPECS["skins"] = tabulated(skin_spec("skin_c2", "C2"), "411302_P01_CEILING-SKIN-C1-C2_DWG", ["411301"], [
    "TABULATED (D-89): drawn as 411302 C2. 411301 C1 is the same outline mirrored about X 0, with no roof slot.",
])
SPECS["fills"] = tabulated(SPECS["fill_a"], "513301_P01_LINING-FILL-CEILING-BAYS-A-B-C_DWG", ["513302", "513303"], [
    "TABULATED (D-89): drawn as 513301. Sizes X' x Y' x thickness and notches (X' from the strip's centre):",
] + fill_table())

# D-89 part 4 (PM ruling 2026-11-01): flat parts cut from sheet with no bends or machined
# features (the two skins) need no drawing: their DXF and parts-list rows define them
del SPECS["skins"]
_assy = spec("assy_c2", 0.2, [
    "TABULATED (D-89): drawn as 410102 C2. 410101 C1 is its mirror about X 0: frame 411101 with the plain "
    "closing-face holes and the two soffit lock rivnuts, skin 411301 with no roof slot.",
    "Bonded panel: skin on the frame with the bond set 108002 (bond line 3, bond spec V2-ENG-BND); the ACP face is "
    "datum A (joints register 4: bonded face down on a flat table).",
    "Flatness and squareness of the bonded panel: +/-0.5 on the ACP face (assumption, joints register 4).",
    "Parts: frame (drawing 411101 / 411102), skin (DXF 411301 / 411302), bond set 108002, the factory-fitted joint "
    "hardware listed in 410000_P01_CEILING-PARTS-LIST_BOM.csv.",
], views=FRAME_VIEWS, scales={"iso": 0.1})
_assy["drawing"] = "410101_P01_CEILING-PANEL-ASSY-C1-C2_DWG"
_assy["title"] = [(k, ("%s (this sheet also covers 410101)" % val if k == "PART NO." else val)) for k, val in _assy["title"]]
SPECS["assy"] = _assy
_ga = spec("ceiling", 0.1, [
    "General arrangement of the ceiling as it ships: two bonded outer panels C1 and C2 and two lining cassettes.",
    "Joints: J-CEIL-01 to the walls (side bolts Z 2374, back rivnuts Y 824), J-CEIL-02 C1 to C2 (4 pins); see the "
    "frame drawings and the joints register V2-ENG-JNT-01.",
    "The soffit (AIR 610201) hangs on the four studs under the front members and X1, locked by two captive screws.",
    "Parts and quantities: 410000_P01_CEILING-PARTS-LIST_BOM.csv.",
], views={"front": (300, 470), "top": (300, 250), "left": (620, 470), "iso": (620, 240)}, scales={"iso": 0.05})
_ga["design"] = "410000_P01_CEILING_CAD"
SPECS["ga"] = _ga
ORDER = ["ga", "assy", "frame_c1", "frame_c2", "cassette", "tray", "rib", "fills"]
