"""Views and raw PDF for an ELECTRICAL part drawing (711001, 711002, 711005).

    python3 tools/fusion/start_drawing.py 711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD \
        711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG --sheet A3
    python3 tools/fusion/run_script.py v2/02-Drawings/electrical/make_part_drawing.py --label "ELECTRICAL Engineer" \
        --doc 711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG --save "views" --close
    python3 tools/fusion/pdf_clear_field.py v2/02-Drawings/electrical/.raw/<name>.pdf v2/02-Drawings/electrical/<name>.pdf

Base views only (the API makes no projected or section views): the part's
front (Fusion's Front), top and right in first-angle positions, and an iso,
all at the part's scale on A3 (420 x 297; this build places in mm). The part
number picks the scale and the view spacing.
"""

import os

import adsk.core
import adsk.drawing

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
# part number: scale, front view centre, gap to the next view (sheet mm)
LAYOUT = {
    "711001": (0.5, (120.0, 185.0), 40.0),     # 300 x 260 x 72 at 1:2
    "711002": (0.5, (120.0, 185.0), 30.0),     # 300 x 260 x 1.5 at 1:2
    "711005": (1.0, (120.0, 185.0), 30.0),     # 180 x 180 x 1.5 at 1:1
}
SIZE = {"711001": (300.0, 260.0, 72.0), "711002": (300.0, 260.0, 1.5), "711005": (180.0, 180.0, 1.5)}


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(adsk.core.Point2D.create(x, y))


def add(sheet, orientation, scale, x, y, what):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = scale
    vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleAndHiddenEdgesDrawingViewStyleType
    vp.centerMarkOptions.isAppliedToHoles = True
    vp.centerLineOptions.isAppliedToHoles = True
    inp.placementPoint = dpt(x, y)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None: " + what)
    if abs(v.scaleValue - scale) > 1e-9:
        v.scaleValue = scale
    print("view %s at (%.0f, %.0f), 1:%g" % (what, x, y, 1.0 / v.scaleValue))
    return v


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    name = doc.name
    pn = name[:6]
    if pn not in LAYOUT or not name.endswith("_DWG"):
        raise RuntimeError("active document %r is not one of the ELECTRICAL part drawings" % name)
    dwg = adsk.drawing.Drawing.cast(doc.products.itemByProductType("DrawingProductType"))
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; the API can't delete views" % sheet.views.count)
    scale, (fx, fy), gap = LAYOUT[pn]
    w, h, d = (s * scale for s in SIZE[pn])
    add(sheet, VO.FrontViewOrientationType, scale, fx, fy, "front")
    add(sheet, VO.TopViewOrientationType, scale, fx, fy - h / 2 - gap - d / 2, "top (first angle: below the front)")
    add(sheet, VO.LeftViewOrientationType, scale, fx + w / 2 + gap + d / 2, fy, "left side (first angle: right of the front)")
    add(sheet, VO.IsoTopRightViewOrientationType, scale * 0.6, 330.0, 90.0, "iso")
    raw = os.path.join(ARGS["repo_root"], "v2/02-Drawings/electrical/.raw/%s.pdf" % name)
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF (not for the repo): %s" % raw)
