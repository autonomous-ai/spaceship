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

Four sheet rules from CEILING's first sample (Lead, 2026-11-01), through the shared helpers in
tools/fusion/fusion_drawing.py (#223), which run_script.py gives every script:
- insert_image: every sheet image comes in 58.02 mm wide at scale 1 whatever its pixels, so each is scaled to its
  real width (its pixels over its PNG's px per mm); at scale 1 the 2.5 mm notes printed at about 0.85 mm.
- first_angle_symbol: the outline in a sketch of its own (in one sketch with the circles it printed as a triangle).
- base_view: the style and scale set again on the made view and checked (Fusion ignores the input's style, and
  hidden lines came out on every view, the iso too).
- DimensionSet: the same two points measured the same way are placed once. On top of it, this script skips a
  dimension that measures the same model extent along the same axis as one already placed, from other points or in
  another view (check_drawing_specs.py finds those offline too).
"""

import importlib
import importlib.util
import os
import sys

import adsk.core
import adsk.drawing
import adsk.fusion
from fusion_drawing import DimensionSet, base_view, first_angle_symbol
from fusion_drawing import insert_image as fd_insert_image

ARGS = globals().get("SCRIPT_ARGS", {})
VO = adsk.drawing.ViewOrientationTypes
VISIBLE = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
SNAP = 2.0   # mm on the sheet
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
    """A base view, visible edges only, its style and scale set again on the made view and checked (shared helper)."""
    return base_view(sheet, ORIENT[key], scale, center, VISIBLE)


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
    """The image at its real size (from its PNG's pixels and px per mm), its top left corner at top_left (sheet mm),
    through the shared helper, which places it by its lower left corner and scales it to that width."""
    if not os.path.exists(path):
        raise RuntimeError("missing %s: run render_notes.py first" % path)
    w_px, h_px, px_mm = png_info(path)
    w_mm, h_mm = w_px / px_mm, h_px / px_mm
    scale = fd_insert_image(sheet, path, top_left[0], top_left[1] - h_mm, w_mm)
    print("image %s: %.1f x %.1f mm at scale %.4f, lower left (%.1f, %.1f)" % (
        os.path.basename(path), w_mm, h_mm, scale, top_left[0], top_left[1] - h_mm))


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
    dims = DimensionSet(sheet)
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
        try:
            d = dims.linear(pa, pb, dpt(*place), False, "%s %s to %s" % (vk, a, b))
        except RuntimeError as exc:          # addLinearDimension gave None: reported, the sheet goes on
            skipped.append((vk, a, b, str(exc)))
            continue
        if d is None:
            skipped.append((vk, a, b, "the same two points measured the same way already"))
        else:
            made += 1
            if key2 is not None:
                placed[key2] = vk
    print("dimensions %d made, %d skipped" % (made, len(skipped)))
    for s_ in skipped:
        print("SKIPPED|%s|%s|%s|%s" % s_)
    # 8 mm inside the border (the shared helper refuses less than 6): drawn at X 20 its left edge lay on the border's
    # line and the PDF pulled both left corners onto the border's corner (20, 10), so the outline printed as a
    # triangle (DR frame sample, 2026-11-01)
    first_angle_symbol(sheet, 28.0, 23.0)
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
