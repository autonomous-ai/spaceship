"""ISO first-angle drawings of the FRONT parts and units, through Fusion's drawing API (adsk.drawing, preview).

    # 1. the design the drawing shows (part drawings use part-only designs; a base view shows its whole design):
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py \
        --doc 361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_CAD --doc-new --arg scope=leaf --save "P01" --close
    # 2. start the drawing (shared command, no clicks; needs the Mac unlocked):
    python3 tools/fusion/start_drawing.py 361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_CAD \
        361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_DWG --sheet A2
    # 3. notes and title data as images (offline), then views, dimensions, symbol, images and the raw PDF:
    python3 v2/02-Drawings/front/render_notes.py
    python3 tools/fusion/run_script.py v2/02-Drawings/front/make_drawing_front.py \
        --doc 361001_P01_FRONT-DOOR-LEAF-4-4-LAMINATED_DWG --arg drawing=leaf --save "P01" --close
    # 4. name strip and render:
    python3 tools/fusion/pdf_clear_field.py v2/02-Drawings/front/.raw/<name>.pdf v2/02-Drawings/front/<name>.pdf

Views: base views at one scale (projected views can't be made by the API), aligned in the first-angle layout of
drawing_specs.py. Dimensions: each spec dimension names two points in the view's own 2D axes (model mm); they are
mapped onto the sheet from the view's extent and the model box, and each end snaps to the nearest view vertex.
Pattern: the CEILING Engineer's v2/02-Drawings/ceiling/make_drawing_ceiling.py.
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
SNAP = 2.0   # mm on the sheet

HERE = os.path.dirname(os.path.abspath(globals().get("__file__") or ARGS.get("script_path", "")))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import drawing_specs as S  # noqa: E402
importlib.reload(S)

ORIENT = {"front": VO.FrontViewOrientationType, "top": VO.TopViewOrientationType,
          "left": VO.LeftViewOrientationType, "iso": VO.IsoTopRightViewOrientationType}


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def xy(dp):
    c = dp.coordinate
    return (c.x, c.y)


def view_points(view):
    pts = []
    vc = view.viewCurves
    for i in range(vc.count):
        c = vc.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            pts += [c.startPoint, c.endPoint]
        elif c.type == adsk.drawing.ViewCurveTypes.CircleViewCurveType:
            pts.append(c.centerPoint)
    return pts


def extent(view):
    pts = [xy(p) for p in view_points(view)]
    if not pts:
        return None
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def snap(view, target):
    best, dist = None, None
    for p in view_points(view):
        x, y = xy(p)
        d = (x - target[0]) ** 2 + (y - target[1]) ** 2
        if dist is None or d < dist:
            best, dist = p, d
    return best, (dist ** 0.5 if dist is not None else None)


def add_view(sheet, key, center, scale):
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = ORIENT[key]
    vp.scaleValue = scale
    vp.style = VISIBLE
    inp.placementPoint = dpt(*center)
    v = sheet.views.add(inp)
    if v is None:
        raise RuntimeError("Views.add returned None for %s" % key)
    if abs(v.scaleValue - scale) > 1e-6:
        v.scaleValue = scale     # the scale set on the input is ignored in this build
    return v


def to_sheet(e, box, u, v):
    bu0, bv0, bu1, bv1 = box
    sx = e[0] + (u - bu0) * (e[2] - e[0]) / (bu1 - bu0) if bu1 != bu0 else e[0]
    sy = e[1] + (v - bv0) * (e[3] - e[1]) / (bv1 - bv0) if bv1 != bv0 else e[1]
    return sx, sy


def projection_symbol(sheet, x0, y0, d=5.0, big=10.0, length=10.0, gap=4.0):
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    sk.lines.add([p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
                  p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)])
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def insert_image(sheet, path, top_left):
    if not os.path.exists(path):
        raise RuntimeError("missing %s: run render_notes.py first" % path)
    h_mm = png_size(path)[1] / 10.0
    inp = sheet.images.createInput()
    inp.imageFilePath = path
    inp.position = p2(top_left[0], top_left[1] - h_mm)
    inp.scale = float(ARGS.get("img_scale", "1.0"))
    ok = sheet.images.insert(inp)
    print("image %s: %s" % (os.path.basename(path), ok))


def run(_context):
    app = adsk.core.Application.get()
    key = ARGS["drawing"]
    sp = S.SPECS[key]
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing")
    if not app.activeDocument.name.startswith(sp["drawing"]):
        raise RuntimeError("active drawing is %r, expected %s" % (app.activeDocument.name, sp["drawing"]))
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; start a new drawing" % sheet.views.count)
    want = S.SHEETS[sp["sheet"]]
    if abs(sheet.width - want[0]) > 1 or abs(sheet.height - want[1]) > 1:
        raise RuntimeError("sheet is %s x %s, the spec wants %s" % (sheet.width, sheet.height, sp["sheet"]))
    views, ext = {}, {}
    for vk, center in sp["views"].items():
        views[vk] = add_view(sheet, vk, center, sp["scales"].get(vk, sp["scale"]))
        ext[vk] = extent(views[vk])
        print("view %-5s scale %g extent %s" % (vk, views[vk].scaleValue,
                                                tuple(round(x, 2) for x in ext[vk]) if ext[vk] else None))
    made, skipped = 0, []
    for vk, a, b, side, gap in sp["dims"]:
        if vk not in views or vk not in sp["box"]:
            skipped.append((vk, a, b, "no view or box"))
            continue
        e, box = ext[vk], sp["box"][vk]
        pa, da = snap(views[vk], to_sheet(e, box, *a))
        pb, db = snap(views[vk], to_sheet(e, box, *b))
        if pa is None or pb is None or da > SNAP or db > SNAP:
            skipped.append((vk, a, b, "no vertex within %.1f mm (%.2f, %.2f)" % (SNAP, da or -1, db or -1)))
            continue
        (xa, ya), (xb, yb) = xy(pa), xy(pb)
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        place = {"below": (mx, min(ya, yb) - gap), "above": (mx, max(ya, yb) + gap),
                 "left": (min(xa, xb) - gap, my), "right": (max(xa, xb) + gap, my)}[side]
        d = sheet.drawingDimensions.addLinearDimension(pa, pb, dpt(*place), False)
        if d is None:
            skipped.append((vk, a, b, "addLinearDimension returned None"))
        else:
            made += 1
    print("dimensions %d made, %d skipped" % (made, len(skipped)))
    for s_ in skipped:
        print("SKIPPED|%s|%s|%s|%s" % s_)
    projection_symbol(sheet, 20.0, 20.0)
    notes_dir = os.path.join(HERE, ".notes")
    insert_image(sheet, os.path.join(notes_dir, sp["drawing"] + "_NOTES.png"), sp["images"]["notes"])
    insert_image(sheet, os.path.join(notes_dir, sp["drawing"] + "_TITLE.png"), sp["images"]["title"])
    raw = os.path.join(HERE, ".raw", "%s.pdf" % sp["drawing"])
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("raw PDF:", raw)
