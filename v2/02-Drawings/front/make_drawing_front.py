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

Four sheet rules from CEILING's first sample (Lead, 2026-11-01):
- Fusion inserts every sheet image 58.02 mm wide at scale 1, whatever its pixel width (a 1000 px PNG and CEILING's
  1700 px PNGs all came out 58.02 mm wide, aspect kept), so each image is scaled to its real width (its pixels over
  its PNG's px per mm); at scale 1 the 2.5 mm notes printed at about 0.85 mm.
- The first-angle symbol's outline in its own sketch: drawn in one sketch with the circles it printed as a triangle.
- Each view's style set again after the view is made: Fusion ignores the style given on the input, and hidden lines
  came out on every view, the iso too.
- No dimension placed twice: a dimension that measures the same model extent along the same axis as one already
  placed, in this view or another, is skipped and reported.
"""

import importlib
import importlib.util
import os
import sys

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
VISIBLE = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
SNAP = 2.0   # mm on the sheet
IMG_W_AT_SCALE_1 = 58.0178   # mm: every image's width at scale 1 (measured in CEILING's 513102 PDF, 1700 px images)
# the model axis each view's 2D axis shows (the notes' projection line): (horizontal, vertical), sign of the 2D axis
VIEW_AXES = {"front": (("X", 1), ("Z", 1)), "top": (("X", 1), ("Y", 1)), "left": (("Y", -1), ("Z", 1))}

HERE = os.path.dirname(os.path.abspath(globals().get("__file__") or ARGS.get("script_path", "")))
# drawing_specs by its full path under a FRONT-only name, fresh each run: Fusion keeps modules loaded between runs,
# so an import by name could return another team's drawing_specs (Lead, 2026-11-01)
_spec = importlib.util.spec_from_file_location("front_drawing_specs_run", os.path.join(HERE, "drawing_specs.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
print("helper module %s: %s" % (S.__name__, S.__file__))

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
    # the style on the input is ignored too (hidden lines came out on every view): set it again on the view
    v.style = VISIBLE
    if v.style != VISIBLE:
        print("STYLE NOT SET|%s|%s" % (key, v.style))
    return v


def to_sheet(e, box, u, v):
    bu0, bv0, bu1, bv1 = box
    sx = e[0] + (u - bu0) * (e[2] - e[0]) / (bu1 - bu0) if bu1 != bu0 else e[0]
    sy = e[1] + (v - bv0) * (e[3] - e[1]) / (bv1 - bv0) if bv1 != bv0 else e[1]
    return sx, sy


def to_model(e, box, sx, sy):
    """A sheet point back in the view's 2D axes (model mm): to_sheet's inverse."""
    bu0, bv0, bu1, bv1 = box
    u = bu0 + (sx - e[0]) * (bu1 - bu0) / (e[2] - e[0]) if e[2] != e[0] else bu0
    v = bv0 + (sy - e[1]) * (bv1 - bv0) / (e[3] - e[1]) if e[3] != e[1] else bv0
    return u, v


def measure_key(vk, side, ua, ub):
    """What a dimension measures, as (model axis, low, high) in model mm to 0.1, so the same extent dimensioned
    twice (in one view or two) has the same key. side below/above is a horizontal dimension, left/right vertical."""
    if vk not in VIEW_AXES:
        return None
    k = 0 if side in ("below", "above") else 1
    axis, sign = VIEW_AXES[vk][k]
    a, b = sign * ua[k], sign * ub[k]
    return axis, round(min(a, b), 1), round(max(a, b), 1)


def projection_symbol(sheet, x0, y0, d=5.0, big=10.0, length=10.0, gap=4.0):
    """ISO 5456-2 first-angle symbol: the cone's side view (narrow end away from the circles), then its end view.
    The outline has its own sketch: in one sketch with the circles it printed as a triangle (CEILING's sample)."""
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - OUTLINE")
    sk.lines.add([p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
                  p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)])
    sc = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - CIRCLES")
    cx = x0 + length + gap + big / 2
    sc.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sc.circles.addByCenterRadius(p2(cx, y0), d / 2)


def png_info(path):
    """(width px, height px, px per mm) of a PNG, the px per mm from its pHYs chunk (render_notes.py writes it)."""
    with open(path, "rb") as fh:
        data = fh.read()
    w, h = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    i = data.find(b"pHYs")
    if i < 0 or data[i + 12] != 1:
        raise RuntimeError("%s has no pHYs size in metres: run render_notes.py" % path)
    return w, h, int.from_bytes(data[i + 4:i + 8], "big") / 1000.0


def insert_image(sheet, path, top_left):
    """The image at its real size, its top left corner at top_left (sheet mm). Fusion places it by its lower left
    corner and makes it IMG_W_AT_SCALE_1 wide at scale 1, so the scale is its real width over that."""
    if not os.path.exists(path):
        raise RuntimeError("missing %s: run render_notes.py first" % path)
    w_px, h_px, px_mm = png_info(path)
    w_mm, h_mm = w_px / px_mm, h_px / px_mm
    inp = sheet.images.createInput()
    inp.imageFilePath = path
    inp.position = p2(top_left[0], top_left[1] - h_mm)
    inp.scale = w_mm / IMG_W_AT_SCALE_1
    ok = sheet.images.insert(inp)
    print("image %s: %s, %.1f x %.1f mm at scale %.4f, lower left (%.1f, %.1f)" % (
        os.path.basename(path), ok, w_mm, h_mm, inp.scale, top_left[0], top_left[1] - h_mm))


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
    made, skipped, placed = 0, [], {}
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
        key2 = measure_key(vk, side, to_model(e, box, xa, ya), to_model(e, box, xb, yb))
        if key2 is not None and key2 in placed:
            skipped.append((vk, a, b, "the same %s extent %.1f to %.1f as a dimension already placed in %s" % (
                key2 + (placed[key2],))))
            continue
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        place = {"below": (mx, min(ya, yb) - gap), "above": (mx, max(ya, yb) + gap),
                 "left": (min(xa, xb) - gap, my), "right": (max(xa, xb) + gap, my)}[side]
        d = sheet.drawingDimensions.addLinearDimension(pa, pb, dpt(*place), False)
        if d is None:
            skipped.append((vk, a, b, "addLinearDimension returned None"))
        else:
            made += 1
            if key2 is not None:
                placed[key2] = vk
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
