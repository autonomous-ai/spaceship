"""What each INTERIOR drawing shows (D-89 parts 1 to 4: the GA, the two assemblies and the
folded parts; D-126's down-light profile set is bought, listed by ELECTRICAL). Read by the ceiling's
drawing machinery through make_drawing_interior.py and render_notes_interior.py. Views are laid
out from each part's size as the AIR specs do.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "interior"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
import interior_model as I  # noqa: E402

SHEETS = {"A1": (841.0, 594.0), "A2": (594.0, 420.0)}
IMG_W = 170.0
SCALES = (1.0, 0.5, 0.2, 0.1, 0.05)
GAP = 30.0
V = I.evaluate()
BOXES = I.boxes(V)


def image_places(sheet):
    w, h = SHEETS[sheet]
    return {"notes": (w - 20.0 - IMG_W, h - 15.0), "title": (w - 20.0 - IMG_W, 150.0)}


def doc_name(key, doctype):
    pn, name, _vn, _k, _m = I.PARTS[key]
    return "%s_%s_%s_%s" % (pn, I.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype)


def bbox(keys):
    pts = [b for _n, (k, b) in BOXES.items() if k in keys]
    return (min(b[0] for b in pts), max(b[1] for b in pts), min(b[2] for b in pts), max(b[3] for b in pts),
            min(b[4] for b in pts), max(b[5] for b in pts))


def layout(box, sheet):
    w, h = SHEETS[sheet]
    dx, dy, dz = box[1] - box[0], box[3] - box[2], box[5] - box[4]
    iso_w, iso_h = (dx + dy) * 0.87, dz + (dx + dy) * 0.5
    aw, ah = w - 20 - 30 - IMG_W - 30, h - 40
    for s in SCALES:
        cw = dx * s + GAP + max(dy, iso_w) * s
        if cw <= aw and max((dz + dy) * s + GAP, (dz + iso_h) * s + GAP) <= ah:
            x0, ytop = 40.0, h - 30.0
            front = (x0 + dx * s / 2, ytop - dz * s / 2)
            return s, {"front": front, "top": (front[0], ytop - dz * s - GAP - dy * s / 2),
                       "left": (x0 + dx * s + GAP + dy * s / 2, front[1]),
                       "iso": (x0 + dx * s + GAP + iso_w * s / 2, ytop - dz * s - GAP - iso_h * s / 2)}
    raise ValueError("box %s doesn't fit an %s sheet" % (box, sheet))


COMMON = [
    "UNITS: mm. Mass in kg. Projection: first angle (ISO 5456-2); views as conventions 3 (front looks toward +Y).",
    "General tolerance ISO 2768-m unless a note says more. Folds: inside radius = thickness, K 0.44 (assumptions until the factory's bend table).",
    "Status DRAFT P01: for the prototype and the factory's sample, not released.",
    "Why each feature is where it is: v2/02-Drawings/interior/FEATURE-RATIONALE.md.",
]


def spec(key, notes, keys, sheet="A1", design=None, drawing=None, covers=None):
    pn, name, vn, kind, mat = I.PARTS[key]
    s, views = layout(bbox(keys), sheet)
    mname = I.MATERIALS[mat][0] if mat else "see the parts list"
    return {
        "key": key, "design": design or doc_name(key, "CAD"), "drawing": drawing or doc_name(key, "DWG"),
        "scale": s, "scales": {}, "views": views, "holes": None, "sheet": sheet, "images": image_places(sheet),
        "title": [("PART NO.", pn + (" (this sheet also covers %s)" % covers if covers else "")), ("NAME", name), ("TÊN", vn),
                  ("REV / STATUS", "%s / DRAFT" % I.REV), ("MATERIAL", mname),
                  ("SCALE", "1:%d" % round(1 / s) if s < 1 else "1:1"), ("UNITS", "mm"), ("PROJECTION", "first angle"),
                  ("SHEET", sheet)],
        "notes": list(notes) + COMMON,
    }


ALL = [k for k in I.PARTS if I.PARTS[k][3] != "HS"]
SPECS = {
    "interior": spec("interior", [
        "INTERIOR general arrangement (D-70): the light shelf along the side and back wall tops (Z 2230 to 2270), the 1000 mm ledge on the work wall (top Z 1067), the screen rail (centre Z 1300).",
        "The ledge and the rail stand 5 mm off the felt on stand-offs to WALL's stiles (R1, R2 at Y 98.63 and 464.32); the shelf screws to the wall cassettes.",
        "Parts and quantities: 810000_P01_INTERIOR-PARTS-LIST_BOM.csv.",
    ], ALL, design="810000_P01_INTERIOR_CAD"),
    "ledge_assy": spec("ledge_assy", [
        "Work wall ledge: top 811101 on two brackets 818101 (HOLD: rated for a 225 N lean at the front edge x 3), at WALL's R1 stiles Y 98.63 and 464.32.",
        "Fixing: stand-offs through clearance holes in R1-CASS into rivnuts in the stiles (WALL interface); the ledge stands 5 off the felt (D-17, D-57).",
    ], ("ledge", "bracket")),
    "shelf_assy": spec("shelf_assy", [
        "Light shelf: back run 811201 (X -1166 to 1166) and side runs 811202 LH, 811203 RH (Y -285 to 706, butting the back run). Under the RH run, 15 off the lining: the down-light's LED profile 718101 (23 x 12.5, 991 long, Y -285 to 706: the side run's length, so it ends at the corner joint) with its clip-in satin cover 718102 (D-127), end caps 718103 and mounting clips 718104 (D-126; bought, product HOLD, listed by ELECTRICAL).",
        "Up-light strip (one 8 mm) all round; two 8 mm down-light strips on the right (ELECTRICAL's parts). Cable holes: feed at X 355 (back), call-light drop at Y -209.5 (right), both Z 2250.",
        "Back flanges screw to the wall cassettes (fixing HOLD, WALL); the profile's clips screw to the RH run's and the back run's undersides.",
    ], ("shelf_back", "shelf_lh", "shelf_rh", "lprofile")),
    "ledge": spec("ledge", [
        "Ledge top: 1.5 aluminium folded: top 250 deep, front lip 25 down, back flange 25 down; 1000 long; powder coat charcoal (RAL HOLD).",
        "Blank 294.8 x 1000 (DXF 811101), two bends.",
    ], ("ledge",)),
    "shelf_back": spec("shelf_back", [
        "Light shelf, back run: 1.0 aluminium folded U: back flange 40, bottom 60, front lip 20; 2332 long; powder coat charcoal (RAL HOLD).",
        "Cable hole 10 in the back flange at X 355, Z 2250 (ELECTRICAL's feed). Blank 116.5 x 2332 (DXF 811201).",
    ], ("shelf_back",)),
    "shelf_rh": spec("shelf_rh", [
        "TABULATED (D-89): drawn as 811203 RH; 811202 LH is its mirror about X 0 with no cable hole.",
        "Light shelf, side run: 1.0 aluminium folded U as the back run; 991 long (Y -285 to 706).",
        "RH only: cable hole 10 in the back flange at Y -209.5, Z 2250 (ELECTRICAL's call-light drop); the LED profile 718101 under it (D-126).",
    ], ("shelf_rh",), drawing="811202_P01_INTERIOR-LIGHT-SHELF-SIDE-LH-RH_DWG", covers="811202"),
}
ORDER = list(SPECS)
