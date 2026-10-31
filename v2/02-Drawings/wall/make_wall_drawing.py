"""Views, dimensions, hole tables, datums, notes and PDF for a WALL part drawing, in one Fusion run.

    python3 tools/fusion/start_drawing.py 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD \
        211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG --sheet A2
    python3 v2/02-Drawings/wall/make_sheet_images.py frame 211101
    python3 tools/fusion/run_script.py v2/02-Drawings/wall/make_wall_drawing.py \
        --doc 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG --arg kind=frame --arg pn=211101 --save "views, dims, tables"

Runs on the open, empty drawing that start_drawing.py made from the design (whose Front was set to "seen
from inside the pod" by set_front.py). The drawing API makes base views only, so the projected views are
base views at the same scale, placed in the ISO first-angle layout: TOP below the FRONT, BOTTOM above it,
LEFT (the front end) on its right, RIGHT (the back end) on its left. Dimensions attach to view geometry;
each drilled face gets a hole table with its origin on that view's datum corner. Notes and the data block
are images made by make_sheet_images.py (the API can't put text on a sheet). The raw PDF goes to .raw/
(git-ignored): Fusion prints the account holder's name in the title block, so the repo copy is made with
tools/fusion/pdf_clear_field.py.
"""

import json
import os

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
HERE = "v2/02-Drawings/wall"

KINDS = {
    # views: (orientation, where): where = centre | below | above | right | left (first-angle positions)
    "frame": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
              "views": [("front", VO.FrontViewOrientationType, "centre"),
                        ("top", VO.TopViewOrientationType, "below"),
                        ("bottom", VO.BottomViewOrientationType, "above"),
                        ("left", VO.LeftViewOrientationType, "right"),
                        ("right", VO.RightViewOrientationType, "left")],
              "tables": [("front", "HOLE TABLE 1 - FRONT VIEW, BACK STILE ROOM FACE (ORIGIN: VIEW CORNER B-A)"),
                         ("top", "HOLE TABLE 2 - TOP VIEW, TOP RAIL TOP FACE (ORIGIN: VIEW LOWER LEFT CORNER)"),
                         ("bottom", "HOLE TABLE 3 - BOTTOM VIEW, BOTTOM RAIL BOTTOM FACE (ORIGIN: VIEW LOWER LEFT CORNER)"),
                         ("left", "HOLE TABLE 4 - LEFT VIEW, FRONT STILE FRONT FACE (ORIGIN: VIEW LOWER LEFT CORNER)")],
              "images": [("data", (410.0, 108.0)), ("notes", (410.0, 155.0))],
              "symbol_at": (440.0, 95.0)},
    "skin": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
             "views": [("front", VO.FrontViewOrientationType, "centre"),
                       ("top", VO.TopViewOrientationType, "below"),
                       ("left", VO.LeftViewOrientationType, "right"),
                       ("right", VO.RightViewOrientationType, "left")],
             "tables": [], "images": [("data", (410.0, 108.0)), ("notes", (410.0, 150.0))],
             "symbol_at": (440.0, 95.0)},
    "tray": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
             "views": [("front", VO.FrontViewOrientationType, "centre"),
                       ("top", VO.TopViewOrientationType, "below"),
                       ("left", VO.LeftViewOrientationType, "right")],
             "tables": [], "images": [("data", (410.0, 108.0)), ("notes", (410.0, 150.0))],
             "symbol_at": (440.0, 95.0)},
    "panel": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
              "views": [("front", VO.FrontViewOrientationType, "centre"),
                        ("top", VO.TopViewOrientationType, "below"),
                        ("left", VO.LeftViewOrientationType, "right"),
                        ("right", VO.RightViewOrientationType, "left")],
              "tables": [], "images": [("data", (410.0, 100.0)), ("parts", (410.0, 140.0)), ("notes", (410.0, 195.0))],
              "symbol_at": (440.0, 90.0)},
    "cassette": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
                 "views": [("front", VO.FrontViewOrientationType, "centre"),
                           ("top", VO.TopViewOrientationType, "below"),
                           ("left", VO.LeftViewOrientationType, "right")],
                 "tables": [], "images": [("data", (410.0, 100.0)), ("parts", (410.0, 130.0)), ("notes", (410.0, 170.0))],
                 "symbol_at": (440.0, 90.0)},
}


def overall_dims(sheet, views):
    """Overall length and height on the FRONT view from its lower left corner (datums B and A), and the
    overall depth on the TOP view."""
    v = views["front"]
    e = extent(v)
    o = nearest_end(v, (e[0], e[1]))
    dim(sheet, o, nearest_end(v, (e[2], e[1])), ((e[0] + e[2]) / 2, e[1] - 18.0))
    dim(sheet, o, nearest_end(v, (e[0], e[3])), (e[0] - 14.0, (e[1] + e[3]) / 2))
    t = views["top"]
    et = extent(t)
    dim(sheet, nearest_end(t, (et[2], et[1])), nearest_end(t, (et[2], et[3])), (et[2] + 12.0, (et[1] + et[3]) / 2))
    print("overall dimensions: length, height (front view), depth (top view)")


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp):
    c = dp.coordinate
    return c.x, c.y


def curves(view):
    lines, circles = [], []
    for i in range(view.viewCurves.count):
        c = view.viewCurves.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            lines.append(c)
        elif c.type == adsk.drawing.ViewCurveTypes.CircleViewCurveType:
            circles.append(c)
    return lines, circles


def extent(view):
    lines, circles = curves(view)
    xs, ys = [], []
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            xs.append(x)
            ys.append(y)
    if not xs:
        raise RuntimeError("view has no line curves")
    return min(xs), min(ys), max(xs), max(ys)


def nearest_end(view, target, tol=0.6):
    best, dist = None, None
    lines, _ = curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            d = (x - target[0]) ** 2 + (y - target[1]) ** 2
            if dist is None or d < dist:
                best, dist = p, d
    if best is None or dist > tol ** 2:
        raise RuntimeError("no view vertex near %s (closest %.3f)" % (target, (dist or 0) ** 0.5))
    return best


def edge_line(view, side):
    """The longest line lying on one side of the view's extent: left | right | bottom | top."""
    e = extent(view)
    lines, _ = curves(view)
    best, blen = None, 0.0
    for ln in lines:
        (x1, y1), (x2, y2) = xy(ln.startPoint), xy(ln.endPoint)
        on = {"left": abs(x1 - e[0]) < 0.05 and abs(x2 - e[0]) < 0.05,
              "right": abs(x1 - e[2]) < 0.05 and abs(x2 - e[2]) < 0.05,
              "bottom": abs(y1 - e[1]) < 0.05 and abs(y2 - e[1]) < 0.05,
              "top": abs(y1 - e[3]) < 0.05 and abs(y2 - e[3]) < 0.05}[side]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if on and length > blen:
            best, blen = ln, length
    if best is None:
        raise RuntimeError("no edge line on the %s of the view" % side)
    return best


def add_view(sheet, orientation, centre, scale):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = scale
    vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
    vp.centerMarkOptions.isAppliedToHoles = True
    vp.centerLineOptions.isAppliedToHoles = True
    inp.placementPoint = dpt(*centre)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None for %s" % orientation)
    if abs(v.scaleValue - scale) > 1e-6:
        v.scaleValue = scale            # the input's scale is ignored in this build (tools/fusion/README.md)
    return v


def place_views(sheet, cfg):
    views = {}
    scale, gap = cfg["scale"], cfg["gap"]
    for name, orient, where in cfg["views"]:
        if where == "centre":
            views[name] = add_view(sheet, orient, cfg["front_at"], scale)
            continue
        f = extent(views["front"])
        cx, cy = (f[0] + f[2]) / 2, (f[1] + f[3]) / 2
        # place roughly, then measure the view and move nothing (views can't be moved): aim the centre so the
        # near edge lands one gap from the front view, using the view's own size from a first placement guess
        guess = {"below": (cx, f[1] - gap - 5), "above": (cx, f[3] + gap + 5),
                 "right": (f[2] + gap + 5, cy), "left": (f[0] - gap - 5, cy)}[where]
        views[name] = add_view(sheet, orient, guess, scale)
    for name, v in views.items():
        e = extent(v)
        print("VIEW|%s|extent %s|size %.2f x %.2f" % (name, [round(a, 2) for a in e], e[2] - e[0], e[3] - e[1]))
    return views


def dim(sheet, a, b, place):
    d = sheet.drawingDimensions.addLinearDimension(a, b, dpt(*place), False)
    if d is None:
        raise RuntimeError("addLinearDimension returned None")
    return d


def frame_dims(sheet, views, scale):
    """FRONT view: overall length and height from datums B (left edge) and A (bottom edge), and the left
    edge of every stile from B, stacked under the view."""
    v = views["front"]
    e = extent(v)
    o = nearest_end(v, (e[0], e[1]))
    n = 0
    dim(sheet, o, nearest_end(v, (e[2], e[1])), ((e[0] + e[2]) / 2, e[1] - 22.0))
    dim(sheet, o, nearest_end(v, (e[0], e[3])), (e[0] - 14.0, (e[1] + e[3]) / 2))
    n += 2
    # stile left edges: vertical lines spanning most of the height, left edge x values (not the outline)
    lines, _ = curves(v)
    xs = sorted({round(xy(ln.startPoint)[0], 3) for ln in lines
                 if abs(xy(ln.startPoint)[0] - xy(ln.endPoint)[0]) < 0.01
                 and abs(xy(ln.startPoint)[1] - xy(ln.endPoint)[1]) > 0.8 * (e[3] - e[1])})
    lefts = [x for i, x in enumerate(xs) if i % 2 == 0 and e[0] + 0.5 < x < e[2] - 0.5]
    for k, x in enumerate(lefts):
        tgt = nearest_end(v, (x, e[1] + 20.0 * scale), tol=20.0 * scale + 0.6)
        dim(sheet, o, tgt, ((e[0] + x) / 2, e[1] - 8.0 - 4.5 * (k % 3)))
        n += 1
    print("front view: %d dimensions (length, height, %d stile edges from B)" % (n, len(lefts)))


def hole_table(sheet, view, title, corner):
    e = extent(view)
    origin = nearest_end(view, {"bl": (e[0], e[1]), "tl": (e[0], e[3])}[corner])
    inp = sheet.holeTables.createInput()
    inp.view = view
    inp.originPoint = origin
    inp.title = title
    t = sheet.holeTables.add(inp)
    if t is None:
        raise RuntimeError("HoleTables.add returned None for " + title)
    return t


def datum(sheet, letter, line, place):
    syms = sheet.drawingSymbols
    inp = syms.createDatumIdentifierInput()
    inp.identifier = letter
    inp.viewCurve = line
    inp.placementPoint = dpt(*place)
    s = syms.addDatumIdentifier(inp)
    if s is None:
        raise RuntimeError("datum %s not added" % letter)


def projection_symbol(sheet, x0, y0, d=5.0, big=10.0, length=10.0, gap=4.0):
    """ISO first-angle symbol (as the Phase 0 proof drew it)."""
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    pts = [p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
           p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)]
    sk.lines.add(pts)
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)


def images(sheet, pn, cfg):
    path = os.path.join(ARGS["repo_root"], HERE, ".images", "%s_images.json" % pn)
    with open(path) as fh:
        meta = json.load(fh)
    for name, at in cfg["images"]:
        m = meta[name]
        ii = sheet.images.createInput()
        ii.imageFilePath = m["path"]
        ii.position = p2(*at)
        px_w = m["w_mm"] / 25.4 * 300.0
        ii.scale = m["w_mm"] / px_w * float(ARGS.get("img_scale_fudge", "1"))
        if not sheet.images.insert(ii):
            raise RuntimeError("image %s not inserted" % name)
        print("IMAGE|%s|at %s|%s x %s mm|scale %.5f" % (name, at, m["w_mm"], m["h_mm"], ii.scale))


def run(_context):
    app = adsk.core.Application.get()
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing")
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; start a new drawing" % sheet.views.count)
    cfg = KINDS[ARGS["kind"]]
    print("sheet %s: %s x %s" % (sheet.name, round(sheet.width, 2), round(sheet.height, 2)))
    views = place_views(sheet, cfg)
    if ARGS["kind"] in ("skin", "tray", "panel", "cassette"):
        overall_dims(sheet, views)
        f = views["front"]
        datum(sheet, "A", edge_line(f, "bottom"), (extent(f)[0] + 40.0, extent(f)[1] - 26.0))
        datum(sheet, "B", edge_line(f, "left"), (extent(f)[0] - 26.0, extent(f)[1] + 40.0))
    if ARGS["kind"] == "frame":
        frame_dims(sheet, views, cfg["scale"])
        f = views["front"]
        datum(sheet, "A", edge_line(f, "bottom"), (extent(f)[0] + 40.0, extent(f)[1] - 30.0))
        datum(sheet, "B", edge_line(f, "left"), (extent(f)[0] - 26.0, extent(f)[1] + 40.0))
        t = views["top"]
        datum(sheet, "C", edge_line(t, "top"), (extent(t)[0] + 60.0, extent(t)[3] + 10.0))
    for vname, title in cfg["tables"]:
        hole_table(sheet, views[vname], title, "bl")
    projection_symbol(sheet, *cfg["symbol_at"])
    images(sheet, ARGS["pn"], cfg)
    raw = os.path.join(ARGS["repo_root"], HERE, ".raw", app.activeDocument.name + ".pdf")
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF: %s" % os.path.relpath(raw, ARGS["repo_root"]))
    print("sheet now: %d views, %d dimensions, %d hole tables" % (
        sheet.views.count, sheet.drawingDimensions.count, sheet.holeTables.count))
