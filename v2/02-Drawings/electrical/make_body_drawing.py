"""Views, dimensions, datums, projection symbol and raw PDF for drawing 711001, the power unit's
folded enclosure body (a folded part keeps its drawing, D-89), in one Fusion run.

    python3 tools/fusion/start_drawing.py 711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD \\
        711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG --sheet A2
    python3 tools/fusion/run_script.py v2/02-Drawings/electrical/make_body_drawing.py --label "ELECTRICAL Engineer" \\
        --doc 711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG --save "views, dimensions, datums" --close
    python3 v2/02-Drawings/electrical/body_drawing_text.py --pdf \\
        v2/02-Drawings/electrical/.raw/711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG.pdf \\
        v2/02-Drawings/electrical/711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG.pdf

The body's build set its design's Front (ViewCube) to the room side, +Y up (electrical_parts_cad.py, WALL's
set_front method), so Fusion's standard views line up in ISO first-angle: TOP below the FRONT, BOTTOM above
it, the view from the LEFT on its right, the view from the RIGHT on its left; an iso at 1:5. The drawing API
makes base views only and can't move them, so each centre is worked out from the part's size before the
view is placed, and every view is measured against the size it should have: a view that doesn't match stops
the run before any dimension is added (nothing wrong gets drawn). Dimensions attach to view geometry
(WALL's helpers, copied); the hole list goes into the PDF. Text can't go on a sheet through the API, so the data block, notes and hole list are written into
the exported PDF by body_drawing_text.py, which also removes the account name (the repo is public).

The shared drawing helpers (tools/fusion/fusion_drawing.py, PM 2026-11-01, after CEILING's first sample) make
the views, the symbol and the dimensions: Fusion ignores the view style given at creation, so each view's style
(visible edges only, no hidden lines, the iso too) is set again on the made view and checked; the symbol's
outline is alone in its own sketch, its circles in another (one sketch printed a triangle); each dimension is
placed once. Centre marks and centre lines go on the views' holes after the dimensions, so they can't change
the edge lines the dimensions attach to; every view's style is checked again before the export.
"""

import os
import sys

import adsk.core
import adsk.drawing
import adsk.fusion
from fusion_drawing import DimensionSet, base_view, first_angle_symbol   # given by run_script.py

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
HERE = "v2/02-Drawings/electrical"
DWG = "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG"
SCALE = 0.5                    # 1:2 on A2
GAP = 24.0                     # sheet mm between a view and its neighbour: room for a dimension and a datum
FRONT_AT = (205.0, 250.0)      # sheet mm, origin at the sheet's lower left corner
ISO_AT, ISO_SCALE = (205.0, 70.0), 0.2
SYMBOL_AT = (350.0, 25.0)      # left of the title block, under the iso
TOL = 1.0                      # sheet mm: a placed view must be this close to its expected size
# name, orientation, where (first-angle position against the FRONT)
VIEWS = [("front", "FrontViewOrientationType", "centre"),
         ("top", "TopViewOrientationType", "below"),
         ("bottom", "BottomViewOrientationType", "above"),
         ("left", "LeftViewOrientationType", "right"),
         ("right", "RightViewOrientationType", "left")]


def part_size():
    """w, h, d of the body (mm) from the route model, the numbers its build used."""
    # by full path, under a name no other team uses: Fusion keeps modules between runs, so a plain import
    # could return another team's module of the same name (PM heads-up 2026-10-31); print the file and check it
    import importlib.util
    path = os.path.join(ARGS.get("repo_root", "."), "v2", "01-CAD-Native", "electrical", "electrical_model.py")
    spec = importlib.util.spec_from_file_location("ele_electrical_model", path)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    if os.path.abspath(M.__file__) != os.path.abspath(path):
        raise RuntimeError("helper loaded from %s, not %s" % (M.__file__, path))
    print("helper electrical_model: %s" % M.__file__)
    v = M.values()
    return v["pu_w"], v["pu_h"], v["pu_d"]


def expected(w, h, d):
    """Each view's centre and size on the sheet (mm), from the part's size and the first-angle layout."""
    fx, fy = FRONT_AT
    W, H, D = w * SCALE, h * SCALE, d * SCALE
    return {"front": ((fx, fy), (W, H)),
            "top": ((fx, fy - H / 2 - GAP - D / 2), (W, D)),
            "bottom": ((fx, fy + H / 2 + GAP + D / 2), (W, D)),
            "left": ((fx + W / 2 + GAP + D / 2, fy), (D, H)),
            "right": ((fx - W / 2 - GAP - D / 2, fy), (D, H))}


# ---------------------------------------------------------------- WALL's helpers (make_wall_drawing.py)

def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp: "adsk.drawing.DrawingPoint"):
    c = dp.coordinate
    return c.x, c.y


def curves(view: "adsk.drawing.View"):
    lines, circles = [], []
    for i in range(view.viewCurves.count):
        c = view.viewCurves.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            lines.append(c)
        elif c.type == adsk.drawing.ViewCurveTypes.CircleViewCurveType:
            circles.append(c)
    return lines, circles


def extent(view: "adsk.drawing.View"):
    lines, _circles = curves(view)
    xs, ys = [], []
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            xs.append(x)
            ys.append(y)
    if not xs:
        raise RuntimeError("view has no line curves")
    return min(xs), min(ys), max(xs), max(ys)


def nearest_end(view: "adsk.drawing.View", target, tol=0.6):
    best, dist = None, None
    lines, _ = curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            dd = (x - target[0]) ** 2 + (y - target[1]) ** 2
            if dist is None or dd < dist:
                best, dist = p, dd
    if best is None or dist > tol ** 2:
        raise RuntimeError("no view vertex near %s (closest %.3f)" % (target, (dist or 0) ** 0.5))
    return best


def edge_line(view: "adsk.drawing.View", side):
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


def end_on(view: "adsk.drawing.View", side, near):
    """The end of the view's edge line on `side` nearest to `near`: a real vertex even where the folded
    body's corner reliefs leave no vertex at the extent's corner (live run 2026-10-31: 0.85 mm off)."""
    ln = edge_line(view, side)
    a, b = ln.startPoint, ln.endPoint
    return min((a, b), key=lambda p: (xy(p)[0] - near[0]) ** 2 + (xy(p)[1] - near[1]) ** 2)


VISIBLE = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType


def add_view(sheet: "adsk.drawing.Sheet", orientation, centre, scale):
    """A base view at `centre` (sheet mm): the shared helper sets its style (visible edges only) and scale again
    on the made view and checks both, since Fusion ignores the input's style."""
    return base_view(sheet, orientation, scale, centre, VISIBLE)


def centre_marks(view: "adsk.drawing.View", name):
    """Centre marks and centre lines on the view's holes, set on the made view and read back."""
    marks = view.getCenterMarkOptions()
    marks.isAppliedToHoles = True
    lines = view.getCenterLineOptions()
    lines.isAppliedToHoles = True
    if not view.setCenterMarkOptions(marks) or not view.setCenterLineOptions(lines):
        raise RuntimeError("centre marks or lines not applied to the %s view" % name)
    if not (view.getCenterMarkOptions().isAppliedToHoles and view.getCenterLineOptions().isAppliedToHoles):
        raise RuntimeError("the %s view's holes have no centre marks or lines after setting them" % name)


def dim(dims: "DimensionSet", a: "adsk.drawing.DrawingPoint", b: "adsk.drawing.DrawingPoint", place, label):
    """Every size on this sheet is needed once: one the shared helper skips as a double is a mistake here."""
    if dims.linear(a, b, dpt(*place), False, label) is None:
        raise RuntimeError("the %s dimension doubles one already placed" % label)


def datum(sheet: "adsk.drawing.Sheet", letter, line: "adsk.drawing.ViewCurve", place):
    syms = sheet.drawingSymbols
    inp = syms.createDatumIdentifierInput()
    inp.identifier = letter
    inp.viewCurve = line
    # this build needs at least two leader points; the same point as the box gives no separate bend (API help)
    inp.leaderPoints = [dpt(*place), dpt(*place)]
    inp.placementPoint = dpt(*place)
    if syms.addDatumIdentifier(inp) is None:
        raise RuntimeError("datum %s not added" % letter)


# ---------------------------------------------------------------- this drawing

def place_views(sheet: "adsk.drawing.Sheet", w, h, d):
    """Every view at its worked-out centre; then each is measured: wrong size or place -> stop."""
    exp = expected(w, h, d)
    views, bad = {}, []
    for name, orient, _where in VIEWS:
        views[name] = add_view(sheet, getattr(VO, orient), exp[name][0], SCALE)
    for name, v in views.items():
        e = extent(v)
        (cx, cy), (sw, sh) = exp[name]
        got = (e[2] - e[0], e[3] - e[1])
        centre = ((e[0] + e[2]) / 2, (e[1] + e[3]) / 2)
        print("VIEW|%s|extent %s|size %.2f x %.2f (expected %.2f x %.2f)" % (
            name, [round(a, 2) for a in e], got[0], got[1], sw, sh))
        if abs(got[0] - sw) > TOL or abs(got[1] - sh) > TOL or abs(centre[0] - cx) > TOL or abs(centre[1] - cy) > TOL:
            bad.append(name)
    iso = add_view(sheet, VO.IsoTopRightViewOrientationType, ISO_AT, ISO_SCALE)
    views["iso"] = iso
    print("VIEW|iso|extent %s" % [round(a, 2) for a in extent(iso)])
    if bad:
        raise RuntimeError("views not as expected (the design's Front may not be the room side): %s" % ", ".join(bad))
    return views


def annotate(app: "adsk.core.Application"):
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing")
    if not app.activeDocument.name.startswith(DWG):
        raise RuntimeError("the active drawing is %r, not %s" % (app.activeDocument.name, DWG))
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; start a new drawing" % sheet.views.count)
    print("sheet %s: %s x %s" % (sheet.name, round(sheet.width, 2), round(sheet.height, 2)))
    w, h, d = part_size()
    views = place_views(sheet, w, h, d)
    f, t, r = views["front"], views["top"], views["right"]
    fe, te, re_ = extent(f), extent(t), extent(r)
    # overall sizes, each in the gap beside its view (nothing crosses another view): width under the front
    # view (datum A), height beside the view from the right (outer side), depth beside the top view
    # each from the edge lines on the two opposite sides, so a corner relief can't move it
    dims = DimensionSet(sheet)
    dim(dims, end_on(f, "left", (fe[0], fe[1])), end_on(f, "right", (fe[2], fe[1])), ((fe[0] + fe[2]) / 2, fe[1] - 9.0), "width")
    dim(dims, end_on(r, "bottom", (re_[0], re_[1])), end_on(r, "top", (re_[0], re_[3])), (re_[0] - 9.0, (re_[1] + re_[3]) / 2), "height")
    dim(dims, end_on(t, "bottom", (te[2], te[1])), end_on(t, "top", (te[2], te[3])), (te[2] + 9.0, (te[1] + te[3]) / 2), "depth")
    print("dimensions: width (front view), height (view from the right), depth (top view)")
    datum(sheet, "A", edge_line(f, "bottom"), (fe[0] + 30.0, fe[1] - 17.0))
    datum(sheet, "B", edge_line(f, "left"), (fe[0] - 14.0, fe[1] + 30.0))
    datum(sheet, "C", edge_line(t, "top"), (te[2] - 20.0, te[3] + 8.0))
    # no Fusion hole tables: on this folded body the view corners are relieved, so a table's origin can't sit on
    # the datum corner; the hole list H01-H08 from the datums goes into the PDF (body_drawing_text.py)
    for name, _o, _w in VIEWS:              # after the dimensions: centre lines can't move an edge line now
        centre_marks(views[name], name)
    first_angle_symbol(sheet, *SYMBOL_AT)
    hidden = [n for n, v in views.items() if v.style != VISIBLE]
    if hidden:
        raise RuntimeError("views showing hidden lines before the export: %s" % ", ".join(hidden))
    print("views: visible edges only (%s); centre marks on the holes of the 5 orthographic views" % ", ".join(views))
    raw = os.path.join(ARGS["repo_root"], HERE, ".raw", DWG + ".pdf")
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF (not for the repo): %s" % os.path.relpath(raw, ARGS["repo_root"]))
    print("sheet now: %d views, %d dimensions, %d hole tables" % (
        sheet.views.count, sheet.drawingDimensions.count, sheet.holeTables.count))


def run(_context):
    """PM rule (drawings restart, 2026-10-31): every run closes what it opened. The runner leaves a failed
    run's document open, so a failure closes this drawing unsaved here, then raises for the runner."""
    app = adsk.core.Application.get()
    try:
        annotate(app)
    except Exception:
        docs = [app.documents.item(i) for i in range(app.documents.count)]     # a snapshot: closing one can close others
        for d in docs:
            try:
                if d.isValid and d.name.split(" v")[0] == DWG:
                    print("closing %s unsaved after the failure (its saved version is kept)" % d.name)
                    d.close(False)
            except Exception as e:                       # never hide the first error behind a cleanup error
                print("cleanup: %s" % e)
        raise
