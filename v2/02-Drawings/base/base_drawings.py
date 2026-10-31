"""BASE drawings: views, dimensions to hole centres, hole tables, raw PDF.

One drawing per part design (a base view shows its whole design). For each:

    python3 tools/fusion/start_drawing.py <PN>_P01_<NAME>_CAD <PN>_P01_<NAME>_DWG --sheet A2
    python3 tools/fusion/run_script.py v2/02-Drawings/base/base_drawings.py \
        --doc <PN>_P01_<NAME>_DWG --arg pn=<PN> --save "views, dimensions, holes" --close
    python3 v2/02-Drawings/base/finish_pdfs.py <PN>      # name strip, notes, PNG

This script runs on the open drawing (the runner's --doc makes it active):
1. adds the base views of SPEC[pn], first-angle (ISO 5456-2): the view from
   above below the front view, the view from below above it, the view from
   the left on its right. Base views only (the API makes no projected views),
   each at the scale given, aligned by placement;
2. dimensions: overall sizes, and every hole centre from the datum corner
   (baseline, so no tolerance stack), plus the hole line's offset;
3. a hole table on the hole view, origin on the datum corner;
4. the ISO first-angle projection symbol (sheet sketch lines and circles);
5. exports the raw PDF to v2/02-Drawings/base/.raw/ (git-ignored: Fusion
   prints the account holder's name under "Created by").

The notes, title data and parts list go onto the PDF as text in
finish_pdfs.py: the drawing API can't place text on a sheet in this build
(tools/fusion/README.md).
"""

import os

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(globals().get("__file__", ARGS.get("script_path", "."))))
VO = adsk.drawing.ViewOrientationTypes

# pn: drawing name, kind, views [(name, orientation, scale, (x, y) sheet mm)]
SPEC = {
    "111101": ("111101_P01_BASE-BAND-TUBE-SIDE-LH_DWG", "tube", [
        ("front", VO.FrontViewOrientationType, 0.2, (215.0, 300.0)),
        ("top", VO.TopViewOrientationType, 0.2, (215.0, 250.0)),
        ("bottom", VO.BottomViewOrientationType, 0.2, (215.0, 350.0)),
        ("left", VO.LeftViewOrientationType, 0.5, (450.0, 300.0)),
    ]),
    "111103": ("111103_P01_BASE-BAND-TUBE-BACK_DWG", "tube", [
        ("front", VO.FrontViewOrientationType, 0.2, (300.0, 430.0)),
        ("top", VO.TopViewOrientationType, 0.2, (300.0, 370.0)),
        ("bottom", VO.BottomViewOrientationType, 0.2, (300.0, 490.0)),
        ("left", VO.LeftViewOrientationType, 0.5, (640.0, 430.0)),
    ]),
    "111601": ("111601_P01_BASE-GLIDE-DOUBLER-COMMON_DWG", "plate", [
        ("front", VO.FrontViewOrientationType, 2.0, (110.0, 160.0)),
        ("top", VO.TopViewOrientationType, 2.0, (110.0, 100.0)),
    ]),
    "111401": ("111401_P01_BASE-FLOOR-PANEL-F1_DWG", "plate", [
        ("front", VO.FrontViewOrientationType, 0.1, (170.0, 250.0)),
        ("top", VO.TopViewOrientationType, 0.1, (170.0, 150.0)),
    ]),
    "111501": ("111501_P01_BASE-SEAL-MAT-F1_DWG", "plate", [
        ("front", VO.FrontViewOrientationType, 0.1, (170.0, 250.0)),
        ("top", VO.TopViewOrientationType, 0.1, (170.0, 150.0)),
    ]),
    "110000": ("110000_P01_BASE_DWG", "assembly", [
        ("front", VO.FrontViewOrientationType, 0.1, (200.0, 330.0)),
        ("top", VO.TopViewOrientationType, 0.1, (200.0, 200.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.05, (480.0, 330.0)),
    ]),
}


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp):
    c = dp.coordinate
    return (c.x, c.y)


def curves(view):
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
    lines, circles = curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            xs.append(x)
            ys.append(y)
    for c in circles:
        x, y = xy(c.centerPoint)
        xs.append(x)
        ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def nearest_end(view, target, tol=1.0):
    best, dist = None, None
    lines, _ = curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            d = (x - target[0]) ** 2 + (y - target[1]) ** 2
            if dist is None or d < dist:
                best, dist = p, d
    if best is None or dist > tol ** 2:
        raise RuntimeError("no view corner near (%.2f, %.2f)" % target)
    return best


def holes(view):
    """One circle per hole centre (a hole through two walls can show twice)."""
    _, circles = curves(view)
    seen = {}
    for c in circles:
        x, y = xy(c.centerPoint)
        seen.setdefault((round(x, 3), round(y, 3)), c)
    return sorted(seen.values(), key=lambda c: (xy(c.centerPoint)[0], xy(c.centerPoint)[1]))


def dim(sheet, a, b, place):
    d = sheet.drawingDimensions.addLinearDimension(a, b, dpt(*place), False)
    if d is None:
        raise RuntimeError("addLinearDimension returned None")
    return d


def add_view(sheet, orientation, scale, center):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = scale
    vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
    vp.centerMarkOptions.isAppliedToHoles = True
    vp.centerLineOptions.isAppliedToHoles = True
    inp.placementPoint = dpt(*center)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None")
    if abs(v.scaleValue - scale) > 1e-6:
        v.scaleValue = scale     # the input's scale can be ignored (tools/fusion/README.md)
    return v


def overall(sheet, view, below=True, left=True, gap=8.0):
    e = extent(view)
    o = nearest_end(view, (e[0], e[1]))
    n = 0
    if e[2] - e[0] > 2.0:
        dim(sheet, o, nearest_end(view, (e[2], e[1])), ((e[0] + e[2]) / 2, e[1] - gap if below else e[3] + gap))
        n += 1
    if e[3] - e[1] > 2.0:
        dim(sheet, o, nearest_end(view, (e[0], e[3])), (e[0] - gap if left else e[2] + gap, (e[1] + e[3]) / 2))
        n += 1
    return o, n


def hole_dims(sheet, view, origin, side="below", step=6.0, gap=8.0):
    """Every hole centre from the datum corner: baseline dimensions along the
    view's x, stacked on one side, plus the hole line's offset along y."""
    e = extent(view)
    hs = holes(view)
    for i, c in enumerate(hs):
        x, y = xy(c.centerPoint)
        ty = e[1] - gap - step * i if side == "below" else e[3] + gap + step * i
        dim(sheet, origin, c.centerPoint, (x, ty))
    if hs:
        y_lines = sorted({round(xy(c.centerPoint)[1], 2) for c in hs})
        for j, yl in enumerate(y_lines):
            c = [h for h in hs if abs(xy(h.centerPoint)[1] - yl) < 0.01][0]
            dim(sheet, origin, c.centerPoint, (e[0] - gap - step * j, (e[1] + yl) / 2))
    return len(hs)


def diameters(sheet, view):
    """One diameter callout per hole size, beside the first hole of that size."""
    done = set()
    n = 0
    for c in holes(view):
        r = round(c.geometry.radius if hasattr(c, "geometry") and c.geometry else 0.0, 3)
        key = r if r else len(done)
        if key in done:
            continue
        x, y = xy(c.centerPoint)
        try:
            sheet.drawingDimensions.addDiameterDimension(c, dpt(x + 6.0, y + 6.0 + 4.0 * n))
            n += 1
        except RuntimeError as exc:
            print("  diameter callout skipped (%s)" % exc)
        done.add(key)
    return n


def mitre_angle(sheet, view):
    """Angle between the band's long edge and its mitred end, where there is one."""
    lines, _ = curves(view)
    slanted, straight = None, None
    for ln in lines:
        (x1, y1), (x2, y2) = xy(ln.startPoint), xy(ln.endPoint)
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        if dx > 0.2 and dy > 0.2:
            slanted = ln
        elif dy < 1e-3 and dx > 50.0 and (straight is None or min(y1, y2) < min(xy(straight.startPoint)[1],
                                                                                  xy(straight.endPoint)[1])):
            straight = ln
    if slanted is None or straight is None:
        return 0
    (x1, y1), (x2, y2) = xy(slanted.startPoint), xy(slanted.endPoint)
    try:
        sheet.drawingDimensions.addAngularDimension(straight, slanted, dpt(max(x1, x2) - 12.0, min(y1, y2) - 6.0))
        return 1
    except RuntimeError as exc:
        print("  mitre angle not dimensioned (%s)" % exc)
        return 0


def hole_table(sheet, view, origin, title):
    try:
        inp = sheet.holeTables.createInput()
        inp.view = view
        inp.originPoint = origin
        inp.title = title
        t = sheet.holeTables.add(inp)
        return t is not None
    except RuntimeError as exc:
        print("  hole table not made (%s); the dimensions carry the positions" % exc)
        return False


def projection_symbol(sheet, x0, y0, d=5.0, big=10.0, length=10.0, gap=4.0):
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    sk.lines.add([p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
                  p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)])
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)


def run(_context):
    app = adsk.core.Application.get()
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing (run with --doc <drawing name>)")
    pn = ARGS["pn"]
    name, kind, views = SPEC[pn]
    if app.activeDocument.name != name:
        raise RuntimeError("the active drawing is %r, not %r" % (app.activeDocument.name, name))
    sheet = dwg.activeSheet
    print("drawing %s: sheet %.0f x %.0f, %d views before" % (name, sheet.width, sheet.height, sheet.views.count))
    if sheet.views.count:
        raise RuntimeError("the sheet already has views; start a fresh drawing")
    made = {}
    for vname, orient, scale, center in views:
        made[vname] = add_view(sheet, orient, scale, center)
        e = extent(made[vname])
        print("  view %-6s scale %g at %s, extent %s" % (vname, scale, center,
                                                        tuple(round(a, 1) for a in e) if e else None))
    n_dims, n_holes, tables = 0, 0, 0
    if kind == "tube":
        o, n = overall(sheet, made["front"])
        n_dims += n
        top = made["top"]
        e = extent(top)
        o_top = nearest_end(top, (e[0], e[1]))
        n_holes += hole_dims(sheet, top, o_top, side="below")
        n_dims += diameters(sheet, top) + mitre_angle(sheet, top)
        tables += hole_table(sheet, top, o_top, "HOLES IN THE TOP WALL (VIEW FROM ABOVE), ORIGIN O = DATUMS C, B")
        bot = made["bottom"]
        e = extent(bot)
        o_bot = nearest_end(bot, (e[0], e[3]))
        n_holes += hole_dims(sheet, bot, o_bot, side="below")
        n_dims += diameters(sheet, bot)
        o_l, n = overall(sheet, made["left"], below=True, left=False, gap=6.0)
        n_dims += n
    elif kind == "plate":
        o, n = overall(sheet, made["top"])
        n_dims += n
        o2, n = overall(sheet, made["front"], below=False)
        n_dims += n
        if holes(made["top"]):
            n_holes += hole_dims(sheet, made["top"], o, side="above")
            n_dims += diameters(sheet, made["top"])
            tables += hole_table(sheet, made["top"], o, "HOLES (VIEW FROM ABOVE), ORIGIN O")
        if "detail" in made:
            o3, n = overall(sheet, made["detail"], below=True, left=False, gap=5.0)
            n_dims += n
    else:
        o, n = overall(sheet, made["top"])
        n_dims += n
        o2, n = overall(sheet, made["front"], below=False)
        n_dims += n
    projection_symbol(sheet, sheet.width - 60.0, 70.0)
    print("  %d overall dimensions, %d hole-centre dimensions, %d hole table(s), projection symbol" % (
        n_dims, n_holes, tables))
    raw = os.path.join(HERE, ".raw", name + ".pdf")
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("  raw PDF: %s (next: finish_pdfs.py %s)" % (os.path.relpath(raw, HERE), pn))
