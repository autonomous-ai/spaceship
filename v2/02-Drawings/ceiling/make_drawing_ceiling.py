"""ISO first-angle drawings of the ceiling cassette and its parts, through Fusion's
drawing API (adsk.drawing, preview in Fusion 2706.1.17).

    # 1. a part-only design (a Fusion drawing always shows its whole design):
    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py \
        --doc 513101_P01_LINING-TRAY-CEILING_CAD --doc-new --arg into_active=1 \
        --arg scope=tray --arg save=1 --close --discard
    # 2. start the drawing (shared command, no clicks):
    python3 tools/fusion/start_drawing.py 513101_P01_LINING-TRAY-CEILING_CAD \
        513101_P01_LINING-TRAY-CEILING_DWG --sheet A2
    # 3. views, dimensions, hole table, projection symbol, PDF:
    python3 tools/fusion/run_script.py v2/02-Drawings/ceiling/make_drawing_ceiling.py \
        --doc 513101_P01_LINING-TRAY-CEILING_DWG --arg part=tray --save --close
    # 4. name strip and render:
    python3 tools/fusion/pdf_clear_field.py <raw pdf> <repo pdf>

Views (first-angle, conventions.md section 3): the front view looks toward +Y
(the pod's front view, X right, Z up); the view from above goes BELOW it (X
right, Y up, front at the bottom); the view from the left (looking toward +X)
goes to the RIGHT of it (Y to the left, Z up); an isometric view for
recognition. Projected views can't be made by the API, so all are base views
at one scale, aligned. Dimensions sit on view vertices and on hole centres.
Free text can't be put on a sheet by this API (custom table cells come out
blank) and title block fields can't be set: the part's notes are in
FEATURE-RATIONALE.md and DRAWING-RECORD.md.

The 2D mapping (guideline 3.3), each view in its own X/Y:
  front view:      X(2D) = X(part), Y(2D) = Z(part)
  view from above: X(2D) = X(part), Y(2D) = Y(part)
  view from left:  X(2D) = -Y(part), Y(2D) = Z(part)
"""

import importlib
import os
import sys

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
VISIBLE = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
HIDDEN = adsk.drawing.DrawingViewStyleTypes.VisibleAndHiddenEdgesDrawingViewStyleType
TOL = 0.05   # mm on the sheet, when matching points

HERE = os.path.dirname(os.path.abspath(__file__))
# Fusion keeps modules loaded between runs, and a run from another worktree may have loaded its
# own copy of these: drop any copy from another folder, so the imports below take this
# worktree's files (the drawing scripts here, the ceiling model next to them)
_CAD = os.path.normpath(os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
for _n, _d in (("drawing_specs", HERE), ("make_drawing_ceiling", HERE), ("render_notes", HERE),
               ("ceiling_model", _CAD), ("ceiling_checks", _CAD), ("ceiling_build", _CAD)):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != _d:
        del sys.modules[_n]
for _d in (_CAD, HERE):
    if _d in sys.path:
        sys.path.remove(_d)
    sys.path.insert(0, _d)
import drawing_specs as S  # noqa: E402
importlib.reload(S)
STYLES = {"tray": {"front": HIDDEN, "top": HIDDEN, "left": HIDDEN}, "cassette": {"top": HIDDEN}}


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp):
    c = dp.coordinate
    return (c.x, c.y)


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


def nearest_end(view, target, tol=None):
    best, dist = None, None
    lines, _ = view_curves(view)
    for ln in lines:
        for p in (ln.startPoint, ln.endPoint):
            x, y = xy(p)
            d = (x - target[0]) ** 2 + (y - target[1]) ** 2
            if dist is None or d < dist:
                best, dist = p, d
    if best is None or (tol is not None and dist > tol ** 2):
        raise RuntimeError("no view vertex near %s" % (target,))
    return best


def add_view(sheet, orientation, center, scale, style):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = scale
    vp.style = style
    vp.centerMarkOptions.isAppliedToHoles = True
    vp.centerLineOptions.isAppliedToHoles = True
    inp.placementPoint = dpt(*center)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None for orientation %s" % orientation)
    if abs(v.scaleValue - scale) > 1e-6:
        v.scaleValue = scale     # the scale set on the input is ignored in this build
    return v


def dim(sheet, a, b, place):
    d = sheet.drawingDimensions.addLinearDimension(a, b, dpt(*place), False)
    if d is None:
        raise RuntimeError("addLinearDimension returned None")
    return d


def overall_dims(sheet, view, below=True, left=True, gap=10.0):
    """Width below (or above) and height left (or right) of a view, between the
    vertices at its extent corners."""
    e = extent(view)
    x0, y0, x1, y1 = e
    a = nearest_end(view, (x0, y0))
    b = nearest_end(view, (x1, y0))
    c = nearest_end(view, (x0, y1))
    out = []
    if x1 - x0 > 1.0:
        y = y0 - gap if below else y1 + gap
        out.append(dim(sheet, a, b, ((x0 + x1) / 2, y)))
    if y1 - y0 > 1.0:
        x = x0 - gap if left else x1 + gap
        out.append(dim(sheet, a, c, (x, (y0 + y1) / 2)))
    return out


def hole_dims(sheet, view, gap=8.0):
    """Each hole: its diameter, and its centre from the view's left and top edges."""
    e = extent(view)
    _, circles = view_curves(view)
    unique = {}
    for c in circles:
        x, y = xy(c.centerPoint)
        unique.setdefault((round(x, 3), round(y, 3)), c)
    done = []
    for (cx, cy), c in sorted(unique.items()):
        sheet.drawingDimensions.addDiameterDimension(c, dpt(cx + 12, cy + 12))
        left = nearest_end(view, (e[0], e[3]))
        dim(sheet, left, c.centerPoint, ((e[0] + cx) / 2, e[3] + gap + 6))
        dim(sheet, left, c.centerPoint, (e[0] - gap - 6, (e[3] + cy) / 2))
        done.append((cx, cy))
    return done


def hole_table(sheet, view, title):
    e = extent(view)
    inp = sheet.holeTables.createInput()
    inp.view = view
    inp.originPoint = nearest_end(view, (e[0], e[1]))
    inp.title = title
    t = sheet.holeTables.add(inp)
    if t is None:
        raise RuntimeError("HoleTables.add returned None")
    return t


def projection_symbol(sheet, x0, y0, d=5.0, big=10.0, length=10.0, gap=4.0):
    """ISO first-angle symbol: the truncated cone's side view, narrow end left,
    and its end view (two concentric circles) to the right."""
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    pts = [p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
           p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)]
    sk.lines.add(pts)
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)
    return sk


def insert_image(sheet, path, top_left):
    """Insert a PNG made by render_notes.py with its top left corner at top_left (sheet mm).
    The images are drawn at 10 px per mm; Fusion places an image by its bottom left
    corner, at its own size per pixel, so the first unlocked run checks the size by eye."""
    if not os.path.exists(path):
        raise RuntimeError("missing %s: run render_notes.py first" % path)
    from_png = _png_size(path)
    h_mm = from_png[1] / 10.0
    inp = sheet.images.createInput()
    inp.imageFilePath = path
    inp.position = p2(top_left[0], top_left[1] - h_mm)
    inp.scale = float(ARGS.get("img_scale", "1.0"))
    ok = sheet.images.insert(inp)
    print("image %s at %s: %s" % (os.path.basename(path), (top_left[0], round(top_left[1] - h_mm, 1)), ok))
    return ok


def _png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def run(_context):
    annotate(ARGS["part"])


def annotate(part):
    app = adsk.core.Application.get()
    sp = S.SPECS[part]
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing")
    doc = app.activeDocument
    if not doc.name.startswith(sp["drawing"]):
        raise RuntimeError("active drawing is %r, expected %s" % (doc.name, sp["drawing"]))
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; start a new drawing" % sheet.views.count)
    print("sheet %s x %s (spec %s)" % (round(sheet.width, 1), round(sheet.height, 1), sp["sheet"]))
    want = S.SHEETS[sp["sheet"]]
    if abs(sheet.width - want[0]) > 1 or abs(sheet.height - want[1]) > 1:
        raise RuntimeError("sheet is %s x %s, the spec wants %s" % (sheet.width, sheet.height, sp["sheet"]))
    sc = sp["scale"]
    st = STYLES.get(part, {})
    views = {}
    for key, orient in (("front", VO.FrontViewOrientationType), ("top", VO.TopViewOrientationType),
                        ("left", VO.LeftViewOrientationType), ("iso", VO.IsoTopRightViewOrientationType)):
        views[key] = add_view(sheet, orient, sp["views"][key], sp["scales"].get(key, sc), st.get(key, VISIBLE))
        e = extent(views[key])
        print("view %-5s extent %s" % (key, tuple(round(v, 2) for v in e) if e else None))
    ef, et, el = extent(views["front"]), extent(views["top"]), extent(views["left"])
    print("alignment: front/top x %.2f %.2f, front/left y %.2f %.2f" % (
        ef[0] - et[0], ef[2] - et[2], ef[1] - el[1], ef[3] - el[3]))
    overall_dims(sheet, views["top"], below=True, left=True)
    overall_dims(sheet, views["front"], below=False, left=True)
    overall_dims(sheet, views["left"], below=False, left=False)
    holes = []
    if sp["holes"]:
        holes = hole_dims(sheet, views[sp["holes"]])
    notes_dir = os.path.join(HERE, ".notes")
    # extras: a failure here must not lose the views and dimensions above (the drawing is
    # saved only when the run ends without an error), so each is tried on its own
    extras = [("projection symbol", lambda: projection_symbol(sheet, 20.0, 20.0)),
              ("notes image", lambda: insert_image(sheet, os.path.join(notes_dir, sp["drawing"] + "_NOTES.png"),
                                                   sp["images"]["notes"])),
              ("title image", lambda: insert_image(sheet, os.path.join(notes_dir, sp["drawing"] + "_TITLE.png"),
                                                   sp["images"]["title"]))]
    if sp["holes"]:
        extras.insert(0, ("hole table", lambda: hole_table(sheet, views[sp["holes"]], "HOLES - %s VIEW" % sp["holes"].upper())))
    for what, fn in extras:
        try:
            fn()
        except Exception as e:      # noqa: BLE001 (report and go on)
            print("WARNING: %s not added: %s" % (what, e))
    print("dimensions %d, holes dimensioned %d, hole tables %d" % (
        sheet.drawingDimensions.count, len(holes), sheet.holeTables.count))
    raw = os.path.join(HERE, ".raw", "%s.pdf" % sp["drawing"])
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF:", raw)
