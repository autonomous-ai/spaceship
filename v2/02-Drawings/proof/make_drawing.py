"""Native ISO drawing of the proof frame V2-SWL-10, scripted through Fusion's
drawing API (adsk.drawing, a preview API in Fusion 2706.1.17).

    python3 tools/fusion/run_script.py v2/02-Drawings/proof/make_drawing.py --arg create=1
    python3 tools/fusion/run_script.py v2/02-Drawings/proof/make_drawing.py

create=1 makes the drawing from the saved design in Default Project /
FocusPod v2 and opens it. Without it the script works on the open drawing:
it places the hole tables, the dimensions to hole centres from the datums
and the title block, then exports the PDF.

Coordinate mapping (guideline section 3.3), part system X/Y/Z (see
v2/01-CAD-Native/proof/MANIFEST.md):
  front view (from inside the pod): X-2D = X, Y-2D = Z
  top view:                         X-2D = X, Y-2D = Y
  view from the back (rear stile):  X-2D = -Y, Y-2D = Z
"""

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
DESIGN_NAME = "V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH"
FOLDER = "FocusPod v2"
PDF_REL = "v2/02-Drawings/proof/V2-SWL-10_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG.pdf"


def design_file(app):
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER)
    for df in folder.dataFiles:
        if df.name == DESIGN_NAME and df.fileExtension == "f3d":
            return folder, df
    raise RuntimeError("saved design not found: %s / %s" % (FOLDER, DESIGN_NAME))


def create(app):
    """Automatic creation: one sheet for the frame sub-assembly with its
    orthogonal views, no auto dimensions, skin left out. (Manual creation
    needs a template with view placeholders, which we don't have.)"""
    _folder, src = design_file(app)
    dm = adsk.drawing.DrawingManager.get()
    inp = dm.createDrawingInput(src, adsk.drawing.DrawingCreationModes.AutomaticDrawingCreationMode)
    inp.standard = adsk.drawing.DrawingStandardTypes.ISODrawingStandardType
    inp.units = adsk.drawing.DrawingUnitTypes.MillimeterDrawingUnitType
    inp.sheetSize = adsk.drawing.SheetSizes.A2ISOSheetSize
    inp.orientationType = adsk.drawing.SheetOrientationTypes.LandscapeSheetOrientationType
    g = inp.automationPreferences.globalPreferences
    g.isAutoDimensionEnabled = False
    g.isMainAssemblySheetGenerated = False
    g.isSubAssemblySheetGenerated = True
    g.isComponentSheetGenerated = False
    g.isFlatPatternSheetGenerated = False
    g.isFoldedModelSheetGenerated = False
    g.isAnimationSheetGenerated = False
    g.omitComponentsWithKeywords = "Bolt,Screw,Nut,Washer,SKIN"
    sub = inp.automationPreferences.subAssemblyPreferences
    sub.isoViewSheetPreferences.isSheetCreated = False
    sub.orthogonalViewSheetPreferences.isSheetCreated = True
    sub.orthogonalViewSheetPreferences.isPartsListIncluded = False
    out = dm.createDrawing(inp)
    print("created drawing:", out.name if out else None)
    return out


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("create") == "1":
        create(app)
        return
    raise RuntimeError("annotation step not written yet")
