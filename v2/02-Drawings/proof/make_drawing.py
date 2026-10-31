"""Native ISO drawing of the proof panel V2-SWL-00 (frame V2-SWL-10 + skin
V2-SWL-20), scripted through Fusion's drawing API (adsk.drawing, a preview
API in Fusion 2706.1.17).

    python3 tools/fusion/run_script.py v2/02-Drawings/proof/make_drawing.py
    python3 tools/fusion/run_script.py v2/02-Drawings/proof/make_drawing.py --arg inspect=1

Fusion cannot start a drawing from a script on this install (see
tools/fusion/README.md): manual creation needs a template with view
placeholders, none exists, and automatic creation hangs. So a person makes
the first sheet once (File > New Drawing > From Design on the saved design,
ISO, mm, A2; the Front base view at 1:5 is optional). With that drawing
active, this script does the rest:

  1. views, first-angle (ISO): front view = the frame seen from inside the
     pod; the view from above goes below it; the view from the right (the
     back of the pod, +X) goes on its left. Projected views can't be created
     by the API, so they are base views at the same scale, aligned to the
     front view.
  2. hole tables for the rail holes (view from above) and the rear stile
     holes (view from the right), origin on the datum corner of each view
  3. dimensions to hole centres from the datums, and the overall sizes
  4. notes and parts list as custom tables
  5. PDF export to v2/02-Drawings/proof/

Coordinate mapping (guideline section 3.3), part system X/Y/Z in
v2/01-CAD-Native/proof/MANIFEST.md:
  front view (from inside):      X-2D = X,  Y-2D = Z, origin O
  view from above:               X-2D = X,  Y-2D = Y, origin O
  view from the right (+X side): X-2D = Y,  Y-2D = Z, origin at X = 1470
"""

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
DESIGN_NAME = "V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH"
PDF_REL = "v2/02-Drawings/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG.pdf"

SCALE = 0.2                     # 1:5
FRAME_W, FRAME_H, SKIN_W = 1470.0, 1150.0, 1500.0   # mm, model values at P01
FRONT_CENTER = (31.0, 26.0)     # sheet cm (A2 landscape is 59.4 x 42.0)
GAP_BELOW = 6.0                 # sheet cm, front view edge to the view from above
GAP_LEFT = 7.0                  # sheet cm, front view edge to the view from the right
TOL = 0.02                      # sheet cm when matching points

VO = adsk.drawing.ViewOrientationTypes


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp):
    c = dp.coordinate
    return (c.x, c.y)


# ------------------------------------------------------------------ inspect

def view_curves(view):
    lines, circles = [], []
    vc = view.viewCurves
    for i in range(vc.count):
        c = vc.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.CircleViewCurveType:
            circles.append(c)
        elif c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            lines.append(c)
    return lines, circles


def extent(view):
    xs, ys = [], []
    lines, circles = view_curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            xs.append(x)
            ys.append(y)
    for c in circles:
        x, y = xy(c.centerPoint)
        xs.append(x)
        ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def describe(sheet):
    print("sheet '%s' %s x %s cm, %d views, %d dims, %d hole tables, %d tables" % (
        sheet.name, round(sheet.width, 2), round(sheet.height, 2), sheet.views.count,
        sheet.drawingDimensions.count, sheet.holeTables.count, sheet.customTables.count))
    for i in range(sheet.views.count):
        v = sheet.views.item(i)
        lines, circles = view_curves(v)
        e = extent(v)
        print("  view %d type %s orient %s scale %s: %d lines, %d circles, extent %s" % (
            i, v.type, v.orientation, v.scaleValue, len(lines), len(circles),
            tuple(round(a, 3) for a in e) if e else None))
    tb = sheet.titleBlock
    if tb:
        attrs = tb.getAttributes() or []
        print("  title block '%s': %s" % (tb.name, ", ".join(a.attributeName for a in attrs)))


# ------------------------------------------------------------------ views

def find_view(sheet, orientation):
    for i in range(sheet.views.count):
        v = sheet.views.item(i)
        if v.orientation == orientation:
            return v
    return None


def add_view(sheet, orientation, center):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = SCALE
    vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
    vp.centerMarkOptions.isAppliedToHoles = True
    vp.centerLineOptions.isAppliedToHoles = True
    inp.placementPoint = p2(*center)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None for orientation %s" % orientation)
    return v


def ensure_views(sheet):
    front = find_view(sheet, VO.FrontViewOrientationType)
    if front is None:
        front = add_view(sheet, VO.FrontViewOrientationType, FRONT_CENTER)
        print("added front view (base) at %s" % (FRONT_CENTER,))
    if abs(front.scaleValue - SCALE) > 1e-6:
        front.scaleValue = SCALE
    e = extent(front)
    cx, cy = (e[0] + e[2]) / 2, (e[1] + e[3]) / 2
    top = find_view(sheet, VO.TopViewOrientationType)
    if top is None:
        top = add_view(sheet, VO.TopViewOrientationType, (cx, e[1] - GAP_BELOW))
        print("added view from above (base view aligned below the front view)")
    right = find_view(sheet, VO.RightViewOrientationType)
    if right is None:
        right = add_view(sheet, VO.RightViewOrientationType, (e[0] - GAP_LEFT, cy))
        print("added view from the right (base view aligned left of the front view)")
    return front, top, right


# ------------------------------------------------------------------ geometry

def nearest_end(view, target):
    """Nearest line end point (DrawingPoint) to a sheet coordinate."""
    best, dist = None, None
    lines, _ = view_curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            d = (x - target[0]) ** 2 + (y - target[1]) ** 2
            if dist is None or d < dist:
                best, dist = p, d
    if best is None or dist > TOL ** 2:
        raise RuntimeError("no view vertex near %s (closest %.4f cm)" % (
            target, dist ** 0.5 if dist is not None else -1))
    return best


def mm_to_sheet(v_mm):
    return v_mm * SCALE / 10.0


def front_map(view):
    """Front view: X -> sheet x, Z -> sheet y; origin O at the min corner."""
    e = extent(view)
    return lambda X, Z: (e[0] + mm_to_sheet(X), e[1] + mm_to_sheet(Z))


def top_map(view):
    """View from above: X -> sheet x, Y -> sheet y; the skin's outer face
    (Y = 3) is the top edge."""
    e = extent(view)
    return lambda X, Y: (e[0] + mm_to_sheet(X), e[3] - mm_to_sheet(3.0 - Y))


def right_map(view):
    """View from the right (+X): Y -> sheet x, Z -> sheet y; the skin's outer
    face (Y = 3) is the right edge."""
    e = extent(view)
    return lambda Y, Z: (e[2] - mm_to_sheet(3.0 - Y), e[1] + mm_to_sheet(Z))


def circles_sorted(view, key):
    """Hole circles sorted along a sheet axis, one per centre: a hole through
    both tube walls can show as two coincident circles."""
    _, circles = view_curves(view)
    unique = {}
    for c in circles:
        x, y = xy(c.centerPoint)
        unique.setdefault((round(x, 4), round(y, 4)), c)
    return sorted(unique.values(), key=lambda c: xy(c.centerPoint)[key])


# ------------------------------------------------------------------ annotate

def dim(sheet, a, b, place):
    d = sheet.drawingDimensions.addLinearDimension(a, b, dpt(*place), False)
    if d is None:
        raise RuntimeError("addLinearDimension returned None")
    return d


def annotate_front(sheet, view):
    m = front_map(view)
    o = nearest_end(view, m(0, 0))
    e = extent(view)
    dim(sheet, o, nearest_end(view, m(FRAME_W, 0)), (m(FRAME_W / 2, 0)[0], e[1] - 1.2))
    dim(sheet, nearest_end(view, m(FRAME_W, 0)), nearest_end(view, m(SKIN_W, 0)),
        (m(SKIN_W, 0)[0] + 1.0, e[1] - 1.2))
    dim(sheet, o, nearest_end(view, m(0, FRAME_H)), (e[0] - 1.6, m(0, FRAME_H / 2)[1]))
    dim(sheet, o, nearest_end(view, m(20, 565)), (e[0] - 0.8, m(0, 282)[1]))
    print("front view: 4 dimensions (1470 frame, 30 skin overhang, 1150 height, 565 mid rail)")


def annotate_top(sheet, view):
    m = top_map(view)
    o = nearest_end(view, m(0, 0))          # datum C x datum A
    holes = circles_sorted(view, 0)
    e = extent(view)
    for i, c in enumerate(holes):
        dim(sheet, o, c.centerPoint, (xy(c.centerPoint)[0] - 0.3, e[3] + 0.8 + 0.7 * i))
    if holes:
        dim(sheet, o, holes[0].centerPoint, (e[0] - 1.0, xy(holes[0].centerPoint)[1]))
    print("view from above: %d hole-centre dimensions from datum C, 1 from datum A" % len(holes))
    return o


def annotate_right(sheet, view):
    m = right_map(view)
    o = nearest_end(view, m(0, 0))          # datum A x datum B, at X = 1470
    holes = circles_sorted(view, 1)
    e = extent(view)
    # baseline dimensions on the far (left) side, away from the front view
    for i, c in enumerate(holes):
        dim(sheet, o, c.centerPoint, (e[0] - 0.8 - 0.7 * i, xy(c.centerPoint)[1] - 0.3))
    if holes:
        dim(sheet, o, holes[0].centerPoint, (xy(holes[0].centerPoint)[0], e[1] - 1.0))
    print("view from the right: %d hole-centre dimensions from datum B, 1 from datum A" % len(holes))
    return o


NOTES = [
    "GENERAL NOTES (DRAFT P01, proof only, not for manufacture)",
    "1. Units mm. ISO first-angle projection (ISO 5456-2). Do not scale the drawing.",
    "2. Part system: origin O = front-bottom corner of the frame outer face. Datums: A = frame "
    "outer face (Y = 0), B = bottom face (Z = 0), C = front face (X = 0). +X toward the back of "
    "the pod, +Y outward, +Z up. Left-hand (LH) wall; RH is the mirror image.",
    "3. Views and 2D axes: front view from inside the pod, X-2D = X, Y-2D = Z. View from above "
    "(below the front view), X-2D = X, Y-2D = Y. View from the right (left of the front view), "
    "X-2D = Y, Y-2D = Z, origin at the rear face X = 1470.",
    "4. Holes H01-H12: dia 6.6 through both tube walls (M6 clearance, ISO 273 medium). H01-H04 top "
    "rail to the upper frame; H05-H08 bottom rail to the base, under H01-H04; H09-H12 rear stile "
    "to the back wall. Reasons: FEATURE-RATIONALE.md.",
    "5. General tolerances, PROPOSED and to be confirmed by the shop: single tubes (cut length, "
    "hole position) ISO 2768-1 m; welded frame ISO 13920 class B. Hole position for H01-H12 "
    "proposed dia 0.6 to A|B|C (floating fastener: 6.6 - 6.0). Not for the ACP skin.",
    "6. Frame V2-SWL-10: steel tube 20x20x1.2 (VT10), welded. Skin V2-SWL-20: ACP 3 mm, Dark "
    "Yellow EV3038 (VT01), bonded to datum A (bond spec HOLD).",
    "7. For a person in Fusion (no API): section A-A through H01 and section B-B through H09, "
    "both 2:1, showing the hole through both tube walls.",
]

PARTS_ORDER = [("1", "V2-SWL-10"), ("1.1", "V2-SWL-11"), ("1.2", "V2-SWL-12"),
               ("1.3", "V2-SWL-13"), ("1.4", "V2-SWL-14"), ("1.5", "V2-SWL-15"),
               ("2", "V2-SWL-20")]


def parts_rows(app):
    """Parts list built from the open design (the CAD is the source):
    part number, English and Vietnamese names from the component, material,
    cut length of each tube and mass (CALCULATION from CAD)."""
    design = None
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name == DESIGN_NAME:
            design = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
    if design is None:
        # open the saved design without showing it; the drawing stays active
        active = app.activeDocument
        proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
        folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
        src = [df for df in folder.dataFiles if df.name == DESIGN_NAME and df.fileExtension == "f3d"][0]
        d = app.documents.open(src, False)
        design = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
        if active and active.isValid:
            active.activate()
    if design is None:
        raise RuntimeError("could not open the design %s (parts list source)" % DESIGN_NAME)
    comps = {c.partNumber: c for c in design.allComponents}
    acc = adsk.fusion.CalculationAccuracy.HighCalculationAccuracy
    rows = [("Item", "Part no.", "Name", "Tên (VN)", "Material", "Length mm", "Qty", "Mass kg")]
    frame_mass = 0.0
    for item, pn in PARTS_ORDER[1:6]:
        frame_mass += comps[pn].getPhysicalProperties(acc).mass
    for item, pn in PARTS_ORDER:
        c = comps[pn]
        name, vn = (c.description.split(" | ") + ["", ""])[:2]
        bodies = [c.bRepBodies.item(k) for k in range(c.bRepBodies.count)]
        if pn == "V2-SWL-10":
            mat, length, mass = "welded, see 1.1-1.5", "", frame_mass
        else:
            b = bodies[0]
            mat = b.material.name
            bb = b.boundingBox
            ext = sorted((bb.maxPoint.x - bb.minPoint.x, bb.maxPoint.y - bb.minPoint.y,
                          bb.maxPoint.z - bb.minPoint.z))
            length = "%g" % round(ext[2] * 10.0, 1) if pn != "V2-SWL-20" else \
                "%g x %g" % (round(ext[2] * 10.0, 1), round(ext[1] * 10.0, 1))
            mass = c.getPhysicalProperties(acc).mass
        rows.append((item, pn, name, vn, mat, length, "1", "%.2f" % mass))
    return rows


def text_table(sheet, rows):
    inp = sheet.customTables.createInput()
    inp.rowCount = len(rows)
    inp.columnCount = max(len(r) for r in rows)
    t = sheet.customTables.add(inp)
    if t is None:
        raise RuntimeError("CustomTables.add returned None")
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            t.setCellData(r, c, text)
    return t


def hole_table(sheet, view, origin, title):
    inp = sheet.holeTables.createInput()
    inp.view = view
    inp.originPoint = origin
    inp.title = title
    t = sheet.holeTables.add(inp)
    if t is None:
        raise RuntimeError("HoleTables.add returned None for " + title)
    return t


def run(_context):
    app = adsk.core.Application.get()
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("make the drawing active first (File > New Drawing > From Design)")
    sheet = dwg.activeSheet
    describe(sheet)
    if ARGS.get("inspect") == "1":
        return
    if sheet.sheetSize != adsk.drawing.SheetSizes.A2ISOSheetSize:
        sheet.sheetSize = adsk.drawing.SheetSizes.A2ISOSheetSize
        print("sheet size set to A2")
    front, top, right = ensure_views(sheet)
    describe(sheet)
    annotate_front(sheet, front)
    o_top = annotate_top(sheet, top)
    o_right = annotate_right(sheet, right)
    hole_table(sheet, top, o_top, "HOLE TABLE 1 - VIEW FROM ABOVE (X-2D = X, Y-2D = Y, ORIGIN O)")
    hole_table(sheet, right, o_right, "HOLE TABLE 2 - VIEW FROM THE RIGHT (X-2D = Y, Y-2D = Z)")
    parts = parts_rows(app)
    text_table(sheet, [(n,) for n in NOTES])
    text_table(sheet, parts)
    print("notes table (%d rows) and parts list from the CAD (%d rows) added" % (len(NOTES), len(parts)))
    for r in parts:
        print("  " + " | ".join(r))
    describe(sheet)
    path = "%s/%s" % (ARGS["repo_root"], PDF_REL)
    opts = dwg.exportManager.createPDFExportOptions(path)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("PDF: %s" % PDF_REL)
    doc = app.activeDocument
    if ARGS.get("save") == "1":
        if doc.isSaved:
            print("saved new version:", doc.save("Annotated by v2/02-Drawings/proof/make_drawing.py"))
        else:
            proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
            folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
            print("saved as:", doc.saveAs(DESIGN_NAME + "_DWG", folder,
                                          "FocusPod v2 proof drawing, rev P01, DRAFT", ""))
