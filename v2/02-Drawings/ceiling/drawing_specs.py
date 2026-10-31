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


def image_places(sheet):
    w, h = SHEETS[sheet]
    return {"notes": (w - 20.0 - IMG_W, h - 15.0), "title": (w - 20.0 - IMG_W, 150.0)}

COMMON_NOTES = [
    "UNITS: mm. Angles in degrees. Mass in kg.",
    "Projection: first angle (ISO 5456-2). Views: front looks toward +Y; "
    "the view from above is below it; the view from the left is to its right.",
    "2D axes: front view X(2D)=X, Y(2D)=Z; view from above X(2D)=X, Y(2D)=Y; "
    "view from the left X(2D)=-Y, Y(2D)=Z (guideline 3.3).",
    "Dimensions run from the datum faces named in these notes, and to hole centres. "
    "No ISO 2768 class is applied (conventions 3); the tolerances in note 1 are assumptions "
    "until the factory confirms what it holds.",
    "Status DRAFT P01: for the prototype and the factory's sample only, not released.",
    "Why each feature is where it is: v2/02-Drawings/ceiling/FEATURE-RATIONALE.md.",
]


def doc_name(key, doctype):
    pn, name, _vn, _k, _m = M.PARTS[key]
    return "%s_%s_%s_%s" % (pn, M.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype)


def spec(key, scale, notes, views=None, holes=None, title_extra=(), sheet="A1", scales=None):
    """A1 layout: the front view top left, the view from above below it, the view from the
    left to its right (first angle), the isometric view below that; notes top right, title
    data above the title block."""
    pn, name, vn, kind, mat = M.PARTS[key]
    mname = M.MATERIALS[mat][0] if mat else "see the parts list"
    v = dict(front=(200, 480), top=(200, 290), left=(480, 480), iso=(500, 260)) if sheet == "A1" else \
        dict(front=(150, 330), top=(150, 200), left=(330, 330), iso=(320, 160))
    v.update(views or {})
    return {
        "key": key, "design": doc_name(key, "CAD"), "drawing": doc_name(key, "DWG"),
        "scale": scale, "scales": scales or {}, "views": v, "holes": holes, "sheet": sheet,
        "images": image_places(sheet),
        "title": [("PART NO.", pn), ("NAME", name), ("TÊN", vn), ("REV / STATUS", "%s / DRAFT" % M.REV),
                  ("MATERIAL", mname), ("FINISH", M.FINISH.get(key, "-")),
                  ("SCALE", "1:%d" % round(1 / scale) + ("".join(", %s view %s" % (k, ("%d:1" % round(x)) if x >= 1 else ("1:%d" % round(1 / x)))
                                                                    for k, x in sorted((scales or {}).items())))),
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
        "Two holes D20 for grommets in the front and back returns, centre 12.5 below datum A (grommet HOLD).",
        "Clip and catch fixing zones on the base: no holes until a clip and a catch are named (HOLD-08).",
        "Symmetric about datum C: one part for both ceiling halves.",
    ], holes="front"),
    "rib": spec("rib", 0.2, [
        "Tolerances (assumption): cut length +/-1; bent sizes +/-0.5.",
        "Galvanised steel DX51D+Z, 0.5 thick, hat section: crown 20, height 24, flanges 2 x 12 (assumptions).",
        "Blank and bend lines: 513102_P01_LINING-RIB-CEILING_DXF.dxf.",
        "Fixing to the tray and to the felt: HOLD (H09), drawn as touching only.",
        "Two per cassette, at X' = +/- cs_w/6 (three equal felt spans).",
        "The front view (the hat section) is drawn at 2:1 so the bends read; the other views at 1:5.",
    ], sheet="A2", scales={"front": 2.0}, views={"front": (110, 360), "top": (110, 200), "left": (260, 360), "iso": (300, 180)}),
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
        "Tolerances: see the part drawings; the assembled outline 1160 x 1045 x 34 +/-1 (assumption).",
        "Ceiling lining cassette, one part for both halves (C1-CASS, C2-CASS). Drawing D06 of the wall-and-door sample.",
        "Parts: 513101 tray 1, 513102 rib 2, 513201 felt 1, 513301 / 513302 / 513303 fill 1 each, "
        "518001 clip 6 (HOLD), 518002 safety catch 2 (HOLD).",
        "Clips on the back faces of ceiling cross members X1, X2, X3, over the ribs; catches on X2's front face (D-47).",
        "Hangs 4 below the ceiling frame and never touches it except through the clips and catches (D-17).",
        "Cables run in the 24 gap and clip to the tray only (D-26, D-41).",
    ], holes="front"),
}

ORDER = ["cassette", "tray", "rib", "felt", "fill_a", "fill_b", "fill_c"]
