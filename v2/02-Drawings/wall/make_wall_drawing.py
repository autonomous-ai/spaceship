"""Views, dimensions, hole tables, datums, notes and PDF for a WALL part drawing, in one Fusion run.

    python3 tools/fusion/start_drawing.py 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD \
        211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG --sheet A2
    python3 v2/02-Drawings/wall/make_sheet_images.py frame 211101
    python3 tools/fusion/run_script.py v2/02-Drawings/wall/make_wall_drawing.py \
        --doc 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG --arg kind=frame --arg pn=211101 --save "views, dims, tables"

Options: --arg kind=frame|frame_back|skin|tray|panel|cassette, --arg pn=PN, --arg datum_b=left|right (the
FRONT view edge that is datum B: the side panels' front end, which is on the right for the right wall, and
the back panels' closing-seam face, on the right for B1/B3 and the left for B2/B4). Dimensions and hole
table origins start from datum B's corner.

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

KINDS: "dict[str, dict]" = {
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
    # back panel frame (B1-B4): no hole along Y; tables on the rails' faces and both stiles' end walls
    "frame_back": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
                   "views": [("front", VO.FrontViewOrientationType, "centre"),
                             ("top", VO.TopViewOrientationType, "below"),
                             ("bottom", VO.BottomViewOrientationType, "above"),
                             ("left", VO.LeftViewOrientationType, "right"),
                             ("right", VO.RightViewOrientationType, "left")],
                   "tables": [("top", "HOLE TABLE 1 - TOP VIEW, TOP RAIL TOP FACE"),
                              ("bottom", "HOLE TABLE 2 - BOTTOM VIEW, BOTTOM RAIL BOTTOM FACE"),
                              ("left", "HOLE TABLE 3 - LEFT VIEW, STILE END WALL"),
                              ("right", "HOLE TABLE 4 - RIGHT VIEW, STILE END WALL")],
                   "images": [("data", (410.0, 108.0)), ("notes", (410.0, 155.0))],
                   "symbol_at": (440.0, 95.0)},
    "skin": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
             "views": [("front", VO.FrontViewOrientationType, "centre"),
                       ("top", VO.TopViewOrientationType, "below"),
                       ("left", VO.LeftViewOrientationType, "right"),
                       ("right", VO.RightViewOrientationType, "left")],
             "tables": [], "images": [("data", (410.0, 108.0)), ("notes", (410.0, 150.0)), ("table", (410.0, 200.0))],
             "symbol_at": (440.0, 95.0)},
    "tray": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
             "views": [("front", VO.FrontViewOrientationType, "centre"),
                       ("top", VO.TopViewOrientationType, "below"),
                       ("left", VO.LeftViewOrientationType, "right")],
             "tables": [], "images": [("data", (410.0, 108.0)), ("notes", (410.0, 150.0)), ("table", (410.0, 200.0))],
             "symbol_at": (440.0, 95.0)},
    # cavity fill (D-89: the bays have pockets): overall sizes here, pockets in a table image from the frame
    "fill": {"scale": 0.2, "front_at": (205.0, 235.0), "gap": 14.0,
             "views": [("front", VO.FrontViewOrientationType, "centre"),
                       ("top", VO.TopViewOrientationType, "below")],
             "tables": [], "images": [("data", (410.0, 108.0)), ("notes", (410.0, 150.0)),
                                      ("pockets", (410.0, 200.0)), ("table", (410.0, 235.0))],
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


def overall_dims(sheet, views, right=False):
    """Overall length and height on the FRONT view from its lower corner at datum B (left, or right) and A,
    and the overall depth on the TOP view."""
    v = views["front"]
    e = extent(v)
    xb, xo = (e[2], e[0]) if right else (e[0], e[2])
    o = nearest_end(v, (xb, e[1]))
    dim(sheet, o, nearest_end(v, (xo, e[1])), ((e[0] + e[2]) / 2, e[1] - 18.0))
    dim(sheet, o, nearest_end(v, (xb, e[3])), (xb + (14.0 if right else -14.0), (e[1] + e[3]) / 2))
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
    # the view may still be computing when Views.add returns: reading its scale then raised "failed to read view
    # scale" (the skin sample, 2026-11-01 11:11); let Fusion work and read again, for up to about 30 s
    import time
    for tries in range(60):
        try:
            got = v.scaleValue
            break
        except RuntimeError as exc:
            if tries == 59:
                raise RuntimeError("the %s view's scale still can't be read after 30 s (%s): its model may not "
                                   "have loaded" % (orientation, exc))
            adsk.doEvents()
            time.sleep(0.5)
    if tries:
        print("VIEW|%s view readable after %d tries" % (orientation, tries))
    if abs(got - scale) > 1e-6:
        v.scaleValue = scale            # the input's scale is ignored in this build (tools/fusion/README.md)
    # Fusion ignores the style given at creation and draws hidden lines on every view (CEILING's first sample,
    # PM check 2026-11-01): set it again on the view; the hole tables carry each face's holes
    if v.style != adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType:
        v.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
    if v.style != adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType:
        raise RuntimeError("view %s keeps hidden lines after the style is set" % orientation)
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


def frame_dims(sheet, views, scale, right=False):
    """FRONT view: overall length and height from datums B (left or right edge) and A (bottom edge), and the
    near edge of every stile from B, stacked under the view."""
    v = views["front"]
    e = extent(v)
    xb, xo = (e[2], e[0]) if right else (e[0], e[2])
    o = nearest_end(v, (xb, e[1]))
    n = 0
    dim(sheet, o, nearest_end(v, (xo, e[1])), ((e[0] + e[2]) / 2, e[1] - 22.0))
    dim(sheet, o, nearest_end(v, (xb, e[3])), (xb + (14.0 if right else -14.0), (e[1] + e[3]) / 2))
    n += 2
    # stile left edges: vertical lines spanning most of the height, left edge x values (not the outline)
    lines, _ = curves(v)
    xs = sorted({round(xy(ln.startPoint)[0], 3) for ln in lines
                 if abs(xy(ln.startPoint)[0] - xy(ln.endPoint)[0]) < 0.01
                 and abs(xy(ln.startPoint)[1] - xy(ln.endPoint)[1]) > 0.8 * (e[3] - e[1])})
    near = [x for i, x in enumerate(xs) if i % 2 == (1 if right else 0) and e[0] + 0.5 < x < e[2] - 0.5]
    kept = []                         # never the same dimension twice (PM check 2026-11-01)
    for x in near:
        if all(abs(x - y) > 0.5 for y in kept):
            kept.append(x)
    near = kept
    for k, x in enumerate(near):
        tgt = nearest_end(v, (x, e[1] + 20.0 * scale), tol=20.0 * scale + 0.6)
        dim(sheet, o, tgt, ((xb + x) / 2, e[1] - 8.0 - 4.5 * (k % 3)))
        n += 1
    print("front view: %d dimensions (length, height, %d stile edges from B)" % (n, len(near)))


def hole_table(sheet, view, title, corner):
    e = extent(view)
    origin = nearest_end(view, {"bl": (e[0], e[1]), "tl": (e[0], e[3]), "br": (e[2], e[1])}[corner])
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
    """ISO first-angle symbol: the truncated cone's outline in a sketch of its own (sharing one with the circles
    drew it as a triangle: CEILING's first sample, PM check 2026-11-01), the two circles in another."""
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - OUTLINE")
    pts = [p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
           p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)]
    sk.lines.add(pts)
    sk2 = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - CIRCLES")
    cx = x0 + length + gap + big / 2
    sk2.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk2.circles.addByCenterRadius(p2(cx, y0), d / 2)


MAPPING = os.path.join(HERE, "image_mapping.json")
STACK_X, STACK_Y0, STACK_GAP, STACK_TOP = 410.0, 72.0, 4.0, 405.0   # right column, above the title block (mm)
ORDER = ("data", "parts", "table", "pockets", "notes")             # bottom to top


def stack_at(pn):
    """Where this drawing's note images stack: (x, y0, top) in sheet mm, bottom-up. The default is the right
    column above the title block; --arg images_at="PN=X,Y0[,TOP];..." moves it for a drawing whose hole tables
    took that column (Fusion places hole tables itself, top right; the API can't move them)."""
    for item in (ARGS.get("images_at") or "").split(";"):
        if "=" in item and item.split("=", 1)[0].strip() == pn:
            vals = [float(v) for v in item.split("=", 1)[1].split(",")]
            return vals[0], vals[1], vals[2] if len(vals) > 2 else STACK_TOP
    return STACK_X, STACK_Y0, STACK_TOP


def images(sheet, pn, cfg):
    """The note images, stacked bottom-up (by default in the right column: lower-left corners at x 410, from
    y 72; stack_at), placed with the measured Images.insert mapping (image_mapping.json). Until that mapping is
    measured nothing is placed: an inserted image can't be moved or deleted, so a guess would cost the drawing."""
    with open(os.path.join(ARGS["repo_root"], MAPPING)) as fh:
        mp = json.load(fh)
    if not mp.get("width_at_scale_1_mm") or not mp.get("anchor"):
        print("IMAGES|skipped: the Images.insert mapping for %s isn't measured yet (%s)" % (mp.get("sheet"), MAPPING))
        return 0
    width_mm = sheet.width * 10.0 if sheet.width < 100 else sheet.width     # the API may report cm
    if abs(width_mm - {"A2": 594.0, "A3": 420.0, "A1": 841.0}.get(mp.get("sheet"), -1)) > 1.0:
        print("IMAGES|skipped: the mapping is for %s, this sheet is %.1f mm wide" % (mp.get("sheet"), width_mm))
        return 0
    with open(os.path.join(ARGS["repo_root"], HERE, ".images", "%s_images.json" % pn)) as fh:
        meta = json.load(fh)
    names = [n for n in ORDER if n in meta and n in [c for c, _at in cfg["images"]]]
    sx, y, top = stack_at(pn)
    total = sum(meta[n]["h_mm"] for n in names) + STACK_GAP * max(len(names) - 1, 0)
    if y + total > top:                    # check the whole stack first: never place half of it
        raise RuntimeError("note images don't fit (%.1f mm from y %.1f, top %.1f); nothing placed" % (total, y, top))
    placed = 0
    for name in names:
        m = meta[name]
        # at scale 1 an image comes out width_at_scale_1_mm wide (the sheet sets it), keeping its aspect ratio
        scale = m["w_mm"] / mp["width_at_scale_1_mm"]
        w, h = m["w_mm"], m["h_mm"]
        dx, dy = {"lower-left": (0.0, 0.0), "upper-left": (0.0, h), "center": (w / 2, h / 2)}[mp["anchor"]]
        ii = sheet.images.createInput()
        ii.imageFilePath = m["path"]
        ii.position = p2(sx + dx, y + dy)
        ii.scale = scale
        if not sheet.images.insert(ii):
            raise RuntimeError("image %s not inserted" % name)
        print("IMAGE|%s|lower-left (%.1f, %.1f)|%s x %.1f mm|scale %.5f" % (name, sx, y, w, h, scale))
        y += h + STACK_GAP
        placed += 1
    return placed


def annotate(app, kind, pn, datum_b):
    """Views, dimensions, datums, hole tables, symbol, images and the raw PDF on the active, empty drawing."""
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing")
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views; start a new drawing" % sheet.views.count)
    cfg = KINDS[kind]
    print("sheet %s: %s x %s" % (sheet.name, round(sheet.width, 2), round(sheet.height, 2)))
    step("STEP|views for %s" % pn)
    views = place_views(sheet, cfg)
    right = datum_b == "right"
    side = "right" if right else "left"
    f = views["front"]
    fe = extent(f)
    b_at = (fe[2] + 26.0, fe[1] + 40.0) if right else (fe[0] - 26.0, fe[1] + 40.0)
    if kind in ("skin", "tray", "panel", "cassette", "fill"):
        overall_dims(sheet, views, right)
        datum(sheet, "A", edge_line(f, "bottom"), (fe[0] + 40.0, fe[1] - 26.0))
        datum(sheet, "B", edge_line(f, side), b_at)
    if kind in ("frame", "frame_back"):
        frame_dims(sheet, views, cfg["scale"], right)
        datum(sheet, "A", edge_line(f, "bottom"), (fe[0] + 40.0, fe[1] - 30.0))
        datum(sheet, "B", edge_line(f, side), b_at)
        t = views["top"]
        datum(sheet, "C", edge_line(t, "top"), (extent(t)[0] + 60.0, extent(t)[3] + 10.0))
    for vname, title in cfg["tables"]:
        hole_table(sheet, views[vname], "%s (ORIGIN: VIEW LOWER %s CORNER)" % (title, side.upper())
                   if "ORIGIN" not in title else title, "br" if right else "bl")
    step("STEP|symbol and notes for %s" % pn)
    projection_symbol(sheet, 30.0, 400.0)                 # top left: clear of the views and the note column
    finish(app, dwg, sheet, kind, pn)


def finish(app, dwg, sheet, kind, pn):
    """The note images (once their mapping is measured) and the raw PDF."""
    if ARGS.get("images", "1") != "0":
        images(sheet, pn, KINDS[kind])
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


STEP_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".raw", "annotate-steps.log")


def step(msg):
    """Print a step and append it, timestamped, to .raw/annotate-steps.log at once: the runner only returns a run's
    printed lines when it ends, so after a hang (the 05:00 run, 2026-11-01) this file shows where it stopped."""
    import time
    print(msg)
    try:
        os.makedirs(os.path.dirname(STEP_LOG), exist_ok=True)
        with open(STEP_LOG, "a", encoding="utf-8") as fh:
            fh.write("%s %s\n" % (time.strftime("%H:%M:%S", time.gmtime()), msg))
            fh.flush()
    except OSError:
        pass


def open_drawing(app, name):
    """Open the saved drawing NAME from Default Project / FocusPod v2 (the screen is unlocked: PM rule)."""
    proj = [app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
            if app.data.dataProjects.item(i).name == "Default Project"][0]
    fold = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
    from fusion_folder import read_folder     # the shared reader (#213): one fetch of the folder per pass
    found, _unknown, _others = read_folder(fold, stop_when=lambda f, u, o: name in f)
    files = found.get(name, [])
    if len(files) != 1:
        raise RuntimeError("%d saved drawings are called %r" % (len(files), name))
    app.data.activeProject = proj
    doc = app.documents.open(files[0], True)
    if doc is None:
        raise RuntimeError("could not open %r" % name)
    step("BATCH|opened %s (version %s)" % (name, files[0].versionNumber))
    return doc


def update_refs(doc, name):
    """A drawing keeps the design version it was started from: bring its references to the latest saved
    versions before any view is added (the WALL rework saves new design versions, D-120). Prints each
    reference's version before and after; raises when one is still out of date."""
    def state():
        out = []
        refs = doc.documentReferences
        for i in range(refs.count):
            r = refs.item(i)
            out.append((r.dataFile.name if r.dataFile else "?", r.version, r.isOutOfDate))
        return out
    before = state()
    if any(st for _n, _v, st in before):
        if not doc.updateAllReferences():
            raise RuntimeError("%s: updating its references failed (%s)" % (name, before))
        after = state()
        if any(st for _n, _v, st in after):
            raise RuntimeError("%s: references still out of date after the update: %s" % (name, after))
        step("BATCH|references of %s updated: %s -> %s" % (name, before, after))
    else:
        step("BATCH|references of %s up to date: %s" % (name, before))


def run(_context):
    """One drawing (the active one: --doc DWG with --save and --close on the runner), or, with
    --arg batch="KIND:PN:DWG:DATUM_B;...", every listed drawing start_drawing.py saved: each is opened (or
    activated, if open and unmodified), annotated, saved and closed. A failing one is reported (BATCH|FAIL) and closed unsaved, so it
    stays as start_drawing.py made it; the batch goes on and never raises (PM fair-share ruling 2026-10-31:
    fewer, bigger runs)."""
    import traceback
    app = adsk.core.Application.get()
    if not ARGS.get("batch"):
        annotate(app, ARGS["kind"], ARGS["pn"], ARGS.get("datum_b", "left"))
        return
    done, failed = [], []
    for item in [x.strip() for x in ARGS["batch"].split(";") if x.strip()]:
        doc = None
        try:
            kind, pn, name, datum_b = item.split(":")
            docs = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name == name]
            if len(docs) > 1:
                raise RuntimeError("%d open documents are called %r" % (len(docs), name))
            if docs and docs[0].isModified:
                raise RuntimeError("%r is open with unsaved changes; not reused (PM rule 4)" % name)
            doc = docs[0] if docs else open_drawing(app, name)
            doc.activate()
            update_refs(doc, name)
            if ARGS.get("only_images") == "1":            # notes added later to an annotated drawing
                dwg = adsk.drawing.Drawing.cast(app.activeProduct)
                if dwg is None or not dwg.activeSheet.views.count:
                    raise RuntimeError("%r has no views yet: annotate it first" % name)
                step("BATCH|images %s" % name)
                finish(app, dwg, dwg.activeSheet, kind, pn)
            else:
                step("BATCH|annotate %s" % name)
                annotate(app, kind, pn, datum_b)
            if not doc.save("views, dimensions, hole tables, notes"):
                raise RuntimeError("save failed")
            done.append(name)
            step("BATCH|done %s" % name)
        except Exception as exc:                          # noqa: BLE001  (report, close, go on)
            failed.append(item)
            step("BATCH|FAIL %s: %s" % (item, exc))
            print(traceback.format_exc()[-1200:])
        finally:
            if doc is not None and doc.isValid:
                try:
                    doc.close(False)
                except Exception as exc:                  # noqa: BLE001
                    print("BATCH|could not close %s: %s" % (doc.name, exc))
    print("BATCH|summary: %d done, %d failed%s" % (len(done), len(failed), (": " + ", ".join(failed)) if failed else ""))
