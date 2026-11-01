"""What each AIR drawing shows (D-89 parts 1 to 4: assemblies and the folded, machined or bonded
parts; flat sheet parts go by their DXF and parts-list row). Read by the ceiling's drawing
machinery through make_drawing_air.py and render_notes_air.py.

Views are laid out from each part's size: first angle, the front view top left, the view from
above under it, the view from the left to its right, the isometric view under that; the
largest standard scale that fits beside the notes column wins.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "air"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
import air_model as A  # noqa: E402

SHEETS = {"A1": (841.0, 594.0), "A2": (594.0, 420.0)}
IMG_W = 170.0
SCALES = (1.0, 0.5, 0.2, 0.1, 0.05)
GAP = 30.0


def image_places(sheet):
    w, h = SHEETS[sheet]
    return {"notes": (w - 20.0 - IMG_W, h - 15.0), "title": (w - 20.0 - IMG_W, 150.0)}


def doc_name(key, doctype):
    pn, name, _vn, _k, _m = A.PARTS[key]
    return "%s_%s_%s_%s" % (pn, A.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype)


V = A.evaluate()
BOXES = {name: (key, [A.ev(V, e) for e in bx]) for key, name, bx in A.layout()}


def bbox(keys=None, names=None):
    pts = [b for n, (k, b) in BOXES.items() if (keys and k in keys) or (names and n in names)]
    return (min(b[0] for b in pts), max(b[1] for b in pts), min(b[2] for b in pts), max(b[3] for b in pts),
            min(b[4] for b in pts), max(b[5] for b in pts))


def layout(box, sheet):
    """(scale, views) for a box (x0, x1, y0, y1, z0, z1) on the sheet."""
    w, h = SHEETS[sheet]
    dx, dy, dz = box[1] - box[0], box[3] - box[2], box[5] - box[4]
    iso_w, iso_h = (dx + dy) * 0.87, dz + (dx + dy) * 0.5
    aw, ah = w - 20 - 30 - IMG_W - 30, h - 40
    for s in SCALES:
        cw = max(dx, dx) * s + GAP + max(dy, iso_w) * s
        chl, chr_ = (dz + dy) * s + GAP, (dz + iso_h) * s + GAP
        if cw <= aw and max(chl, chr_) <= ah:
            x0, ytop = 40.0, h - 30.0
            front = (x0 + dx * s / 2, ytop - dz * s / 2)
            top = (front[0], ytop - dz * s - GAP - dy * s / 2)
            left = (x0 + dx * s + GAP + dy * s / 2, front[1])
            iso = (x0 + dx * s + GAP + iso_w * s / 2, ytop - dz * s - GAP - iso_h * s / 2)
            return s, {"front": front, "top": top, "left": left, "iso": iso}
    raise ValueError("box %s doesn't fit an %s sheet" % (box, sheet))


COMMON = [
    "UNITS: mm. Mass in kg. Projection: first angle (ISO 5456-2); views as conventions 3 (front looks toward +Y).",
    "General tolerance ISO 2768-m unless a note says more (D-89 part 4 for the flat parts' DXF).",
    "Status DRAFT P01: for the prototype and the factory's sample, not released.",
    "Why each feature is where it is: v2/02-Drawings/air/FEATURE-RATIONALE.md.",
]


def spec(key, notes, box, sheet="A1", design=None, holes=None):
    pn, name, vn, kind, mat = A.PARTS[key]
    s, views = layout(box, sheet)
    mname = A.MATERIALS[mat][0] if mat else "see the parts list"
    return {
        "key": key, "design": design or doc_name(key, "CAD"), "drawing": doc_name(key, "DWG"),
        "scale": s, "scales": {}, "views": views, "holes": holes, "sheet": sheet, "images": image_places(sheet),
        "title": [("PART NO.", pn), ("NAME", name), ("TÊN", vn), ("REV / STATUS", "%s / DRAFT" % A.REV),
                  ("MATERIAL", mname), ("SCALE", "1:%d" % round(1 / s) if s < 1 else "1:1"), ("UNITS", "mm"),
                  ("PROJECTION", "first angle"), ("SHEET", sheet)],
        "notes": list(notes) + COMMON,
    }


COL = ["col_foot", "col_front", "col_left", "col_side_lo", "col_side_hi", "col_fill", "kick", "hub", "col_ang"]
SPECS = {
    "air": spec("air", [
        "AIR general arrangement (D-60 to D-62, D-87): the air column in the front-right inside corner, the soffit over the door head, the supply fan box and intake riser inside DR, the roof sleeve and grille through C2's slot.",
        "Shipping pieces, each 20 kg or less (D-87): the soffit with its exhaust fan box fitted; the column; two cartridges; the supply fan box joined with the riser.",
        "Hooks (PM ruling 2026-11-01): the soffit on 4 studs in the ceiling frame, slid 24 mm toward the door, locked by 2 captive M6 screws; the column on 2 studs in DR's access panel (X 971, Z 1700 and 1850), dropped 10 mm onto BASE's 2 spigots.",
        "Parts and quantities: 610000_P01_AIR-PARTS-LIST_BOM.csv.",
    ], bbox(keys=None, names=list(BOXES)), design="610000_P01_AIR_CAD"),
    "column": spec("column", [
        "Air column: X 949 to 1161 (5 mm off the side lining), Y -643.5 (DR's access-panel face, FRONT's named value) to -285, foot on the mat at Z 12, top Z 2120.",
        "Foot plate: 8.5 round hole at (989, -605) and 8.5 x 14 slot along Y at (1126, -337) for BASE's spigots.",
        "Back-left angle: keyholes at X 971 (12 big hole 10 below each stud, 6.5 slot) for DR's studs at Z 1700 and 1850.",
        "Faces ACP 3 + felt 9 bonded (drawings 611101, 611102); kick grille 100 high on the front and left; hub zone 180 x 180 at Z 1200 (HOLD).",
        "The supply cartridge (610301) slides in on site with 5 clear all round.",
    ], bbox(names=[n for n, (k, _b) in BOXES.items() if k in COL] + ["CARTRIDGE SUPPLY"])),
    "soffit": spec("soffit", [
        "Soffit: X -1161 to 1161, Y -643.5 (DR's access-panel face) to -285, underside Z 2120, rails' top Z 2349.24; ships with the exhaust fan box fitted (D-87).",
        "Underside in three pieces: left and right hinged (2 hinges on the door side, 2 push latches each, HOLD), a fixed strip over the column; the top band's dark tone (D-60).",
        "Top rails 3 thick (door side 22.5 wide, room side 24) at Z 2346.24 on the heads of four M6 x 16 studs (HOLD-18: 6 mm heads, 1.5 clear under each), open forks at X -583 and 583: lift 24 mm behind its place, hook, slide toward the door; two captive M6 x 25 lock screws at X -1100 and -950 (5 mm key through the left section). A door-side plate and the front face carry the rails.",
        "Exhaust grille 265 x 336 at X -1150 in the left section; the exhaust cartridge (610301) slides in; the fan box under C2's roof slot.",
    ], bbox(names=[n for n, (k, _b) in BOXES.items() if k in ("sof_under", "sof_under_r", "sof_under_f", "sof_front",
                                                                "sof_rail_d", "sof_rail_r", "sof_end", "sof_fill",
                                                                "egrille", "stud", "hinge", "latch", "lock")]
            + ["EXHAUST FAN BOX", "CARTRIDGE EXHAUST"])),
    "cart": spec("cart", [
        "Splitter cartridge, one part for both paths (D-61): 173 x 314 x 1750, 2 mm aluminium casing open at both ends (D-61; D-121), three 50 mm Sorberpoly 2D layers at 32 kg/m3 (D-116) with two 80 mm passages.",
        "Layers: Pyrotek Sorberpoly 2D, knife cut (parts-list row, no drawing, D-89).",
    ], bbox(names=["CARTRIDGE SUPPLY"])),
    "sbox": spec("sbox", [
        "Supply fan box joined with the intake riser and the transitions (D-87), inside DR; its two fans are in FRONT's list (PM ruling 2026-11-01).",
        "Riser 1 mm steel 139 x 155, Z 105 to 1445; box 300 x 155 x 300 at Z 1650 to 1950.",
    ], bbox(names=["SUPPLY FAN BOX", "INTAKE RISER", "RISER TRANSITION", "SUPPLY TRANSITION"])),
    "ebox": spec("ebox", [
        "Exhaust fan box: 294 x 314 x 173, 3 mm aluminium (D-124), lined 50 (air report 7e); two NF-A14 fans 618401 lying flat.",
        "Fitted in the soffit at the factory (D-87); under C2's roof sleeve.",
    ], bbox(names=["EXHAUST FAN BOX"]), sheet="A2"),
    "col_ang": spec("col_ang", [
        "Set of three corner angles, 2 thick aluminium: two front 9 x 20, the back-left 20 x 20; 2108 long (Z 14 to 2120).",
        "Back-left angle: two keyholes at X 971: 12 big hole at Z 1690 and 1840, 6.5 slot up to Z 1700 and 1850 (PM ruling 2026-11-01).",
        "Keyhole position +/-0.3 from the angle's foot (assumption: the studs in DR are located the same way).",
    ], bbox(keys=["col_ang"])),
    "casing": spec("casing", [
        "Cartridge casing: 173 x 314 x 1750, 2 aluminium, folded into a tube and closed with a riveted seam (HOLD), open at both ends.",
        "Inside 169 x 310 holds the three layers; bend radius and seam: the factory's bend table (HOLD).",
    ], bbox(names=["CARTRIDGE SUPPLY"])),
    "box": spec("box", [
        "Exhaust fan box casing: 294 x 314 x 173, 2 aluminium, folded and riveted (HOLD); openings for the cartridge and the roof sleeve to suit the fans (HOLD until the fan mounts are drawn).",
    ], bbox(names=["EXHAUST FAN BOX"]), sheet="A2"),
    "box_s": spec("box_s", [
        "Supply fan box casing: 300 x 155 x 300, 2 aluminium, folded and riveted (HOLD); openings to the riser and the transition HOLD.",
    ], bbox(names=["SUPPLY FAN BOX"]), sheet="A2"),
    "riser": spec("riser", [
        "Intake riser: 1 galvanised steel tube 139 x 155 x 1340, folded with a lock seam (HOLD), inside DR at X 955 to 1094, Y -803 to -648.",
    ], bbox(names=["INTAKE RISER"])),
    "sleeve": spec("sleeve", [
        "Roof sleeve: 1 galvanised steel tube 285 x 294, from the fan box top (Z 2332) to the roof skin (Z 2400), through C2's slot (D-61).",
        "It goes in with the soffit and comes out first, so C2's front side bolt can be reached (joints register 3.5).",
    ], bbox(names=["ROOF SLEEVE"]), sheet="A2"),
    "col_front": spec("col_front", [
        "Column front face: ACP 3 (EV3038 face) bonded to felt 9 Dark Gray; 212 x 1996; hub opening 180 x 180 at Z 1110 to 1290 (X 971 to 1151).",
        "Bond: the felt maker's PSA or a contact adhesive (HOLD); edges routed after bonding, +/-0.5.",
    ], bbox(names=["COLUMN FACE FRONT"])),
    "col_left": spec("col_left", [
        "Column left face: ACP 3 bonded to felt 9; 348 x 1996.",
        "Bond as the front face (HOLD); edges routed after bonding, +/-0.5.",
    ], bbox(names=["COLUMN FACE LEFT"])),
    "sof_under": spec("sof_under", [
        "Soffit underside, left hinged section: ACP 3 bonded to felt 9, the top band's dark tone (D-60); 1160 x 348.",
        "Exhaust grille opening 265 x 336 at X -1150 to -885 (the grille sits in it).",
        "Hinges on the door-side edge at X -871 and -291, push latches on the room-side edge (HOLD).",
    ], bbox(names=["SOFFIT UNDERSIDE LEFT"])),
    "sof_under_r": spec("sof_under_r", [
        "Soffit underside, right hinged section: ACP 3 bonded to felt 9, dark tone; 947 x 348; hinges at X 238 and 711 (HOLD).",
    ], bbox(names=["SOFFIT UNDERSIDE RIGHT"])),
    "sof_under_f": spec("sof_under_f", [
        "Soffit underside, fixed strip over the column: ACP 3 bonded to felt 9, dark tone; 212 x 348.",
    ], bbox(names=["SOFFIT UNDERSIDE FIXED"]), sheet="A2"),
    "sof_front": spec("sof_front", [
        "Soffit front face: ACP 3 bonded to felt 9 Dark Gray; 2322 x 212, its top hidden behind the ceiling cassette's edge.",
    ], bbox(names=["SOFFIT FACE FRONT"])),
}
ORDER = list(SPECS)
