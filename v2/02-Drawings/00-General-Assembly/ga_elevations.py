"""GA sheet 1, elevations: the whole pod (skeleton P04) in first-angle views.

    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_elevations.py \\
        --doc 100000_P04_POD-GENERAL-ASSEMBLY_DWG --arg step=views --save "GA views" --close
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_elevations.py \\
        --doc 100000_P04_POD-GENERAL-ASSEMBLY_DWG --arg step=dims --save "GA dims" --close
    python3 tools/fusion/export_drawing.py 100000_P04_POD-GENERAL-ASSEMBLY_DWG \\
        v2/02-Drawings/00-General-Assembly

    or in one run: --arg step=all [--arg notes_png=... --arg notes_px=... --arg notes_py=...
    --arg notes_scale=...], the notes PNG rendered from
    100000_P04_POD-GENERAL-ASSEMBLY_NOTES.txt by tools/fusion/sheet_notes.py.

The drawing was started from the skeleton design with start_drawing.py's
sequence, so every base view shows the whole pod. ISO, first-angle
projection (guideline 3.2): the view from the left sits right of the front
view, the view from the right sits left of it, the view from above sits below
it, the view from the back at the far right. Views are named by pod direction
(conventions.md section 4: front = the door side, -Y; right = +X seen from
outside facing the door); Fusion's Front, Left, Right, Top and Back views of
this Z-up design are exactly those.

API limits (tools/fusion/README.md): base views only, so the sections are
separate drawings of cut copies (GA sheets 2 and 3); views can't be moved or
deleted, so "views" refuses to run on a sheet that already has views; title
block fields can't be set by script (a person fills them: DWG No.
100000-GA, Rev. P04, DRAFT, scale 1:20, units mm).
"""

import time

import adsk
import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
SCALE = 1.0 / 20.0
SHEET_NAME = "GA-1 ELEVATIONS"
VO = adsk.drawing.ViewOrientationTypes

# A1 landscape, 841 x 594 mm. Centres in sheet mm; at 1:20 the front and back
# views are 125 x 120, the side views 85 x 120 and the view from above 125 x 85.
ROW_Y = 410.0
LAYOUT = [
    ("right", VO.RightViewOrientationType, (115.0, ROW_Y)),     # view from +X: left of front
    ("front", VO.FrontViewOrientationType, (265.0, ROW_Y)),
    ("left", VO.LeftViewOrientationType, (415.0, ROW_Y)),       # view from -X: right of front
    ("back", VO.BackViewOrientationType, (565.0, ROW_Y)),
    ("top", VO.TopViewOrientationType, (265.0, ROW_Y - 175.0)), # view from above: below front
    ("iso", VO.IsoTopRightViewOrientationType, (720.0, ROW_Y + 20.0)),
]


# General notes (sheet_notes.py, PR #67): the text file next to this script,
# rendered at 3.5 mm capitals (ISO 3098 for A1) and 280 mm wide; its lower-left
# corner here, in sheet mm. 102.6 mm tall as rendered on 2026-10-31.
NOTES_AT = (340.0, 90.0)
NOTES_WIDTH = 280.0
NOTES_TEXT_MM = 3.5
NOTES_MAX_HEIGHT = 110.0     # assumption: room kept for the text to grow a little


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp: "adsk.drawing.DrawingPoint"):
    c = dp.coordinate
    return (c.x, c.y)


def line_ends(view: "adsk.drawing.View"):
    pts = []
    vc = view.viewCurves
    for i in range(vc.count):
        c = vc.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            pts.extend([c.startPoint, c.endPoint])
    return pts


def extent(view: "adsk.drawing.View"):
    pts = [xy(p) for p in line_ends(view)]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def corner(view: "adsk.drawing.View", fx, fy):
    """The view-curve end point nearest a corner of the view's extent
    (fx, fy = 0 for min, 1 for max)."""
    e = extent(view)
    tx = e[2] if fx else e[0]
    ty = e[3] if fy else e[1]
    return min(line_ends(view), key=lambda p: (xy(p)[0] - tx) ** 2 + (xy(p)[1] - ty) ** 2)


def sheet_and_drawing():
    app = adsk.core.Application.get()
    doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
    if doc is None:
        raise RuntimeError("open the GA drawing first (--doc 100000_P04_POD-GENERAL-ASSEMBLY_DWG)")
    dwg = doc.drawing
    return dwg, dwg.sheets.item(0)


def refresh_references(doc: "adsk.core.Document"):
    """A drawing shows the version of the design it was made from (the GA was
    started from an older skeleton), so take the newest before placing views."""
    def listed():
        refs = doc.documentReferences
        return ["%s v%s%s" % (r.dataFile.name if r.dataFile else "?", r.version,
                              " (out of date)" if r.isOutOfDate else "")
                for r in [refs.item(i) for i in range(refs.count)]]
    before = listed()
    print("references: %s" % before)
    if any("(out of date)" in r for r in before):
        print("updated all references: %s" % doc.updateAllReferences())
        adsk.doEvents()
        after = listed()
        print("references now: %s" % after)
        if any("(out of date)" in r for r in after):
            raise RuntimeError("references still out of date after updating: %s" % after)


def describe(sheet: "adsk.drawing.Sheet"):
    print("sheet '%s' %g x %g mm, %d views, %d dimensions" % (
        sheet.name, sheet.width, sheet.height, sheet.views.count, sheet.drawingDimensions.count))
    for i in range(sheet.views.count):
        v = sheet.views.item(i)
        e = extent(v)
        name = LAYOUT[i][0] if i < len(LAYOUT) else "?"
        print("  view %d (%s) scale 1:%g, extent %s" % (
            i, name, round(1 / v.scaleValue, 3),
            tuple(round(a, 1) for a in e) if e else None))


def step_views(sheet: "adsk.drawing.Sheet"):
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; views can't be moved or deleted by "
                           "script, so make a new sheet instead" % sheet.views.count)
    want = adsk.drawing.SheetSizes.A1ISOSheetSize
    sheet.sheetSize = want
    # Fusion applies a new size in steps (2026-10-31: an A2 sheet read 420 x 420
    # just after it was set), so let it finish and look again before judging
    for _ in range(10):
        adsk.doEvents()
        if sheet.sheetSize == want and abs(sheet.width - 841) <= 1 and abs(sheet.height - 594) <= 1:
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("sheet is %g x %g (size value %s), not A1 841 x 594, after 10 looks"
                           % (sheet.width, sheet.height, sheet.sheetSize))
    try:
        sheet.name = SHEET_NAME
    except Exception as e:  # noqa: BLE001 - a name is nice to have, not worth losing the views
        print("sheet name not set: %s" % e)
    for name, orientation, center in LAYOUT:
        inp = sheet.views.createBaseViewInput()
        vp = inp.viewParameters
        vp.orientation = orientation
        vp.scaleValue = SCALE if name != "iso" else SCALE * 0.75
        vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
        inp.placementPoint = dpt(*center)
        v = sheet.views.add(inp)
        if v is None:
            raise RuntimeError("Views.add returned None for the %s view" % name)
        want = SCALE if name != "iso" else SCALE * 0.75
        if abs(v.scaleValue - want) > 1e-9:
            v.scaleValue = want     # the input's scale was ignored in Phase 0
        print("added %s view at %s" % (name, center))
    describe(sheet)


def extremes(view: "adsk.drawing.View"):
    """The view-curve end points furthest left, right, down and up: the overall size is
    measured between these (2026-10-31: the end point nearest a corner of the extent
    missed the faceted front, giving 2390 for 2400 and 1602 for 1700)."""
    pts = line_ends(view)
    return (min(pts, key=lambda p: xy(p)[0]), max(pts, key=lambda p: xy(p)[0]),
            min(pts, key=lambda p: xy(p)[1]), max(pts, key=lambda p: xy(p)[1]))


def pod_size():
    """pod_w, pod_d, pod_h (mm) from the skeleton this drawing shows (its reference)."""
    doc = adsk.core.Application.get().activeDocument
    refs = doc.documentReferences
    for i in range(refs.count):
        ref = refs.item(i).referencedDocument
        if ref is not None and ref.name.startswith("100000_P04_POD-SKELETON"):
            design = adsk.fusion.Design.cast(ref.products.itemByProductType("DesignProductType"))
            return tuple(design.userParameters.itemByName(n).value * 10.0 for n in ("pod_w", "pod_d", "pod_h"))
    raise RuntimeError("the drawing doesn't reference the skeleton, so its size can't be checked")


def step_dims(sheet: "adsk.drawing.Sheet"):
    if sheet.views.count < 5:
        raise RuntimeError("run step=views first")
    if sheet.drawingDimensions.count:
        raise RuntimeError("the sheet already has dimensions")
    right, front, left, back, top = (sheet.views.item(i) for i in range(5))
    dims = sheet.drawingDimensions
    pod_w, pod_d, pod_h = pod_size()
    fe, le, te = extent(front), extent(left), extent(top)

    def dim(a, b, place, axis, want, label):
        # the API can't read a dimension's value back, so check the points first
        got = abs(xy(b)[axis] - xy(a)[axis]) / SCALE
        if abs(got - want) > 0.5:
            raise RuntimeError("%s would read %.1f mm, not %.1f; nothing kept" % (label, got, want))
        dims.addLinearDimension(a, b, place, False)
        print("  dimension %s: %.1f mm (skeleton %.1f)" % (label, got, want))

    lx, hx, ly, hy = extremes(front)
    dim(lx, hx, dpt((fe[0] + fe[2]) / 2, fe[1] - 12.0), 0, pod_w, "overall width, front view")
    dim(ly, hy, dpt(fe[0] - 14.0, (fe[1] + fe[3]) / 2), 1, pod_h, "overall height, front view")
    lx, hx, _ly, _hy = extremes(left)
    dim(lx, hx, dpt((le[0] + le[2]) / 2, le[1] - 12.0), 0, pod_d, "overall depth, view from the left")
    _lx, _hx, ly, hy = extremes(top)
    dim(ly, hy, dpt(te[0] - 14.0, (te[1] + te[3]) / 2), 1, pod_d, "overall depth, view from above")
    # ISO first-angle symbol, left of the title block
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    x0, cy, d, big, length, gap = 560.0, 40.0, 5.0, 10.0, 10.0, 4.0
    sk.lines.add([p2(x0, cy - d / 2), p2(x0 + length, cy - big / 2), p2(x0 + length, cy + big / 2),
                  p2(x0, cy + d / 2), p2(x0, cy - d / 2)])
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, cy), big / 2)
    sk.circles.addByCenterRadius(p2(cx, cy), d / 2)
    describe(sheet)


def step_redo(dwg: "adsk.drawing.Drawing", old: "adsk.drawing.Sheet"):
    """Sheet 1 again: views and dimensions can't be moved, read or deleted by script, so a
    new sheet gets the views and the checked dimensions, then the old sheet is deleted and
    the new one becomes sheet 1 (its notes go on after, with sheet_notes.py)."""
    inp = dwg.sheets.createInput()
    inp.name = SHEET_NAME + " (NEW)"
    new = dwg.sheets.add(inp)
    step_views(new)
    step_dims(new)
    old_name = old.name
    if not old.deleteMe():
        raise RuntimeError("couldn't delete the old sheet %s" % old_name)
    try:
        new.name = SHEET_NAME
    except Exception as e:  # noqa: BLE001 - a name is nice to have
        print("sheet name not set: %s" % e)
    print("sheet 1 made again; old sheet %r deleted; %d sheet(s) now" % (old_name, dwg.sheets.count))


def step_notes(sheet: "adsk.drawing.Sheet"):
    """The general notes, rendered outside Fusion from the text file next to this
    drawing (tools/fusion/sheet_notes.py --render-only) and placed as an image."""
    ii = sheet.images.createInput()
    ii.imageFilePath = ARGS["notes_png"]
    ii.position = p2(float(ARGS["notes_px"]), float(ARGS["notes_py"]))
    ii.scale = float(ARGS["notes_scale"])
    if not sheet.images.insert(ii):
        raise RuntimeError("Images.insert returned False for the notes")
    print("notes placed at (%s, %s), scale %s" % (ARGS["notes_px"], ARGS["notes_py"], ARGS["notes_scale"]))


def run(_context):
    dwg, sheet = sheet_and_drawing()
    step = ARGS.get("step", "inspect")
    if step in ("views", "all"):
        refresh_references(adsk.core.Application.get().activeDocument)
    if step == "views":
        step_views(sheet)
    elif step == "dims":
        step_dims(sheet)
    elif step == "redo":
        refresh_references(adsk.core.Application.get().activeDocument)
        step_redo(dwg, sheet)
    elif step == "all":          # one run: views, dimensions, notes (keeps the Fusion queue lean)
        step_views(sheet)
        step_dims(sheet)
        if ARGS.get("notes_png"):
            step_notes(sheet)
    else:
        describe(sheet)
