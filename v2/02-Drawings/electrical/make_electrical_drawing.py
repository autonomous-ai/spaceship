"""Views and PDF for 710000_P01_ELECTRICAL-ROUTES_DWG, the Fusion drawing of the
route model. Ready for when the Mac's screen is unlocked (PM rule: a drawing
start needs the screen; adding views does not).

    # 1. start the drawing (only when the PM says the screen is unlocked)
    python3 tools/fusion/start_drawing.py 710000_P01_ELECTRICAL_CAD 710000_P01_ELECTRICAL-ROUTES_DWG --sheet A2
    # 2. views and the raw PDF (works on a locked screen)
    python3 tools/fusion/run_script.py v2/02-Drawings/electrical/make_electrical_drawing.py \
        --label "ELECTRICAL Engineer" --doc 710000_P01_ELECTRICAL-ROUTES_DWG --save "views" --close
    # 3. the repo copy, without the account holder's name
    python3 tools/fusion/pdf_clear_field.py v2/02-Drawings/electrical/.raw/710000_P01_ELECTRICAL-ROUTES_DWG.pdf \
        v2/02-Drawings/electrical/710000_P01_ELECTRICAL-ROUTES_DWG.pdf

Views, first-angle, all at 1:20 on A2 (594 x 420; this build places in mm):
- FRONT (Fusion's Front looks along +Y: the back wall's routes as seen from
  inside, the power unit, the light feed, the trunk);
- LEFT (Fusion's Left looks toward +X: the right wall's routes from inside,
  the corner pocket, the kit drop, the column chase and hub zone);
- TOP (looking down: the routes' depth in the cassettes, the column, the
  ceiling route);
- an iso view at 1:30 to recognise the parts.
Only base views exist in the API (tools/fusion/README.md), so the views are
base views placed in the first-angle layout. Text goes on the generated wiring
diagram sheets (custom table text doesn't print in this build).
"""

import os

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
DWG_NAME = "710000_P01_ELECTRICAL-ROUTES_DWG"
RAW = "v2/02-Drawings/electrical/.raw/%s.pdf" % DWG_NAME
VO = adsk.drawing.ViewOrientationTypes
VIEWS = [  # orientation, scale, sheet centre (mm), what it shows
    (VO.FrontViewOrientationType, 0.05, (150.0, 265.0), "front: back wall routes from inside"),
    (VO.LeftViewOrientationType, 0.05, (330.0, 265.0), "left (looking toward +X): right wall routes"),
    (VO.TopViewOrientationType, 0.05, (150.0, 95.0), "top: depths, column, ceiling route"),
    (VO.IsoTopRightViewOrientationType, 1.0 / 30.0, (470.0, 110.0), "iso, to recognise the parts"),
]


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(adsk.core.Point2D.create(x, y))


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc.name != DWG_NAME:
        raise RuntimeError("active document is %r, not %r" % (doc.name, DWG_NAME))
    dwg = adsk.drawing.Drawing.cast(doc.products.itemByProductType("DrawingProductType"))
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; views can't be deleted by the API" % sheet.views.count)
    for orientation, scale, (cx, cy), what in VIEWS:
        inp = sheet.views.createBaseViewInput()
        vp = inp.viewParameters
        vp.orientation = orientation
        vp.scaleValue = scale
        vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
        inp.placementPoint = dpt(cx, cy)
        v = sheet.views.add(inp)
        if v is None:
            raise RuntimeError("Views.add returned None: " + what)
        if abs(v.scaleValue - scale) > 1e-9:      # the input's scale is ignored in this build
            v.scaleValue = scale
        print("view %s at (%.0f, %.0f), scale 1:%.0f" % (what, cx, cy, 1.0 / v.scaleValue))
    raw = os.path.join(ARGS["repo_root"], RAW)
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF (not for the repo): %s" % raw)
