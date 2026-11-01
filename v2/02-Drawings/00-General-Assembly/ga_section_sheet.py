"""GA sheets 2 and 3: a section view, in outline, on the drawing of a cut copy of the skeleton.

    python3 tools/fusion/start_drawing.py 100000_P04_POD-SECTION-AA_CAD 100000_P04_POD-SECTION-AA_DWG --sheet A2 --keep-open
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_section_sheet.py \\
        --doc 100000_P04_POD-SECTION-AA_DWG --arg section=AA --arg notes_png=NOTE.png --arg notes_px=25 \\
        --arg notes_py=20 --save "section A-A"

The drawing is of the cut copy made by ga_section_design.py, so its base view from the viewer's side shows the
cut faces. This script places that view at 1:20 and the sections' note (100000_P04_POD-SECTION_NOTES.txt,
rendered by tools/fusion/sheet_notes.py --render-only), its lower-left corner at notes_px, notes_py.

No hatch (PM ruling 2026-11-01): every cut face in these sections is 2.3 mm or less on the sheet at 1:20, and
three live probes on the B-B view showed Fusion's drawing-sketch lines can't carry a hatch there: line ends on a
view edge, or 0.25 mm beside it, were moved to the edge's corner (0 of 21 right), and with the hatch drawn
before the view each line's start jumped about 4 mm onto the line before it (6 of 55 right). So every cut face
is in outline and the note says so; the layer build-ups are on the assembly sheets' section details. Check an
export with ga_pdf_check.py outline. A sheet that has its view already is refused: a redo is a new drawing
under a revision suffix, the old one renamed (D-141), never a delete.
"""

import adsk
import adsk.core
import adsk.drawing
from fusion_drawing import base_view, insert_image   # shared helpers (tools/fusion), given by run_script.py

ARGS = globals().get("SCRIPT_ARGS", {})
SCALE = 1.0 / 20.0
VO = adsk.drawing.ViewOrientationTypes
# section: (design name, orientation, sheet centre in mm)
SECTIONS = {
    # seen from the left (-X): sheet x runs along -Y (the front, -Y, is on the right), sheet y along +Z
    "AA": ("100000_P04_POD-SECTION-AA_CAD", VO.LeftViewOrientationType, (230.0, 230.0)),
    # seen from the front (-Y): sheet x along +X, sheet y along +Z
    "BB": ("100000_P04_POD-SECTION-BB_CAD", VO.FrontViewOrientationType, (230.0, 230.0)),
}
NOTES_WIDTH = 180.0     # mm on the sheet; the note's lower-left corner at --arg notes_px, notes_py


def run(_context):
    app = adsk.core.Application.get()
    sec = ARGS.get("section", "AA")
    _design, orientation, center = SECTIONS[sec]
    doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
    sheet = doc.drawing.sheets.item(0)
    if sheet.views.count:
        raise RuntimeError("the sheet has %d view(s) already; a redo is a new drawing (D-141), nothing changed"
                           % sheet.views.count)
    # the shared helper sets the style (visible edges) and the scale again on the made view and checks them
    v = base_view(sheet, orientation, SCALE, center)
    print("placed the %s view at %s, 1:%g, every cut face in outline (no hatch at 1:20, PM ruling 2026-11-01)"
          % (sec, center, round(1 / v.scaleValue, 3)))
    place_note(sheet)


def place_note(sheet):
    """The sections' note, if --arg notes_png is given: its lower-left corner at notes_px, notes_py,
    NOTES_WIDTH wide."""
    if ARGS.get("notes_png"):
        scale = insert_image(sheet, ARGS["notes_png"], float(ARGS["notes_px"]), float(ARGS["notes_py"]), NOTES_WIDTH)
        print("note placed at (%s, %s) mm, %g mm wide (scale %.4f)" % (ARGS["notes_px"], ARGS["notes_py"],
                                                                     NOTES_WIDTH, scale))
