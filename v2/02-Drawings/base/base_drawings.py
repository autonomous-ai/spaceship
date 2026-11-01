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

# pn: drawing name, kind, views [(name, orientation, scale, (x, y) sheet mm)], and for an
# assembly the views that get its overall sizes [(view, below, which)]: which = "both", "h" (the
# view's width only) or "v" (its height only), so each size is shown once (ISO 129-1).
# No drawing (D-89): the glide doubler 111601 (part 4: its DXF and parts-list row). Every
# assembly keeps one. The floor panels went with D-132 (no floor). The corner keys
# 111211 to 111214 are the Joints Engineer's (their tabulated drawing; PM ruling 2026-11-01).
SPEC = {
    "111101": ("111101_P01_BASE-BAND-TUBE-SIDE-LH_DWG", "tube", [
        ("front", VO.FrontViewOrientationType, 0.2, (215.0, 300.0)),
        ("top", VO.TopViewOrientationType, 0.2, (215.0, 250.0)),
        ("bottom", VO.BottomViewOrientationType, 0.2, (215.0, 350.0)),
        ("left", VO.LeftViewOrientationType, 0.5, (450.0, 150.0)),          # below the hole table
    ]),
    "111103": ("111103_P01_BASE-BAND-TUBE-BACK_DWG", "tube", [
        ("front", VO.FrontViewOrientationType, 0.2, (300.0, 430.0)),
        ("top", VO.TopViewOrientationType, 0.2, (300.0, 370.0)),
        ("bottom", VO.BottomViewOrientationType, 0.2, (300.0, 490.0)),
        ("left", VO.LeftViewOrientationType, 0.5, (640.0, 430.0)),
    ]),
    "110000": ("110000_P01_BASE_DWG", "assembly", [
        ("front", VO.FrontViewOrientationType, 0.1, (200.0, 330.0)),
        ("top", VO.TopViewOrientationType, 0.1, (200.0, 200.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.05, (480.0, 330.0)),
    ], [("top", True, "both"), ("front", False, "v")]),
    # P02 batch 1 parts, in pod coordinates as built
    "111106": ("111106_P01_BASE-BAND-TUBE-FRONT-FIXED-GLASS_DWG", "tube", [      # A3; runs along X
        ("front", VO.FrontViewOrientationType, 0.2, (240.0, 200.0)),
        ("top", VO.TopViewOrientationType, 0.2, (240.0, 160.0)),
        ("bottom", VO.BottomViewOrientationType, 0.2, (240.0, 236.0)),
        # the keyed end plate, seen from the right: first angle puts that view on the LEFT of the front view
        ("right", VO.RightViewOrientationType, 0.5, (85.0, 200.0)),
    ]),
    "111301": ("111301_P01_BASE-SILL-FIXED-GLASS_DWG", "plate", [              # A3; bent profile along X
        ("front", VO.FrontViewOrientationType, 0.2, (130.0, 240.0)),
        ("top", VO.TopViewOrientationType, 0.2, (130.0, 170.0)),
        ("left", VO.LeftViewOrientationType, 1.0, (320.0, 160.0)),           # the section, full size, below the table
    ]),
    # subassemblies, in pod coordinates as built (their own designs, saved by base_build.py)
    "110101": ("110101_P01_BASE-BAND-ASSY-SIDE-LH_DWG", "assembly", [      # A2; runs along Y
        ("left", VO.LeftViewOrientationType, 0.2, (260.0, 300.0)),
        ("top", VO.TopViewOrientationType, 0.2, (520.0, 215.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.1, (260.0, 180.0)),
    ], [("left", True, "both"), ("top", False, "h")]),
    "110103": ("110103_P01_BASE-BAND-ASSY-BACK_DWG", "assembly", [         # A1; runs along X
        ("front", VO.FrontViewOrientationType, 0.2, (420.0, 430.0)),
        ("top", VO.TopViewOrientationType, 0.2, (420.0, 370.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.1, (420.0, 200.0)),
    ], [("front", True, "both"), ("top", False, "v")]),
    # P02's subassemblies (their own designs, saved by base_build.py with --arg sub_list)
    "110102": ("110102_P01_BASE-BAND-ASSY-SIDE-RH_DWG", "assembly", [      # A2; runs along Y; 110101's mirror
        ("right", VO.RightViewOrientationType, 0.2, (300.0, 300.0)),
        ("top", VO.TopViewOrientationType, 0.2, (520.0, 215.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.1, (300.0, 180.0)),
    ], [("right", True, "both"), ("top", False, "h")]),
    "110106": ("110106_P01_BASE-BAND-ASSY-FRONT-FIXED-GLASS_DWG", "assembly", [   # A2; FR1 and its sill, along X
        ("front", VO.FrontViewOrientationType, 0.5, (300.0, 300.0)),
        ("top", VO.TopViewOrientationType, 0.5, (300.0, 210.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.25, (300.0, 110.0)),
    ], [("front", True, "both"), ("top", False, "v")]),
    "110104": ("110104_P01_BASE-BAND-ASSY-FRONT-LH_DWG", "assembly", [     # A3; DL's two facets: the plan shows them
        ("top", VO.TopViewOrientationType, 1.0, (190.0, 150.0)),
        ("front", VO.FrontViewOrientationType, 1.0, (190.0, 250.0)),
        ("iso", VO.IsoTopRightViewOrientationType, 0.5, (330.0, 220.0)),
    ], [("top", True, "both"), ("front", False, "v")]),
    # Fusion sheets the generator can't draw yet (D-139, D-158; the Lead's ruling of 2026-11-01; DRAWING-RECORD.md):
    # FL1 and FL2 in their own axes (all their side faces lie off the pod's axes; FL2 has the full round on its
    # hinge-side plate): CS-111104 / CS-111105, X along the outer face from the corner / knee end, Y inward, Z up from
    # the band's bottom; the glide, a turned part with a hex socket (its axis on Z)
    # A3 with the notes on the right (finish_pdfs NOTES_RIGHT): the views on the left half, first angle, the view from
    # above below the front view, the view from the left on its right, the iso below them; the hole table top right.
    # Kind "facet" (facet_dims): each size once (the Lead's ruling of 2026-11-01: one height printed in two views goes),
    # each end cut's angle to the outer face (a mitre carries its angle), the hole positions in the hole table only.
    # Options: "angles" [(end of the outer edge, the design's angle to the outer face, deg; "out" = placed beyond the
    # corner, in the opposite sector, which shows the same angle, "in" = inside the part; arc radius on the sheet)],
    # "seats": the side of the end view that takes the keyhole seats' heights (clear of the notes and the other views).
    "111104": ("111104_P01_BASE-BAND-TUBE-FRONT-FACET-1-LH_DWG", "facet", [  # A3, 1:1 (CS-111104: from its corner end)
        ("front", VO.FrontViewOrientationType, 1.0, (110.0, 220.0)),
        ("top", VO.TopViewOrientationType, 1.0, (110.0, 128.0)),            # hidden lines: the bottom wall's holes
        ("left", VO.LeftViewOrientationType, 1.0, (212.0, 220.0)),          # the corner end plate's keyholes
        ("iso", VO.IsoTopRightViewOrientationType, 0.5, (110.0, 52.0)),
    ], {"angles": [("start", 65.855, "out", 14.0),                         # the corner end: 24.14 deg off square
                   ("end", 82.745, "out", 14.0)],                          # the knee end: 7.25 deg off square
        "seats": "left"}),
    "111105": ("111105_P01_BASE-BAND-TUBE-FRONT-FACET-2-LH_DWG", "facet", [  # A3, 1:2 (CS-111105: from its knee end)
        ("front", VO.FrontViewOrientationType, 0.5, (90.0, 232.0)),
        ("top", VO.TopViewOrientationType, 0.5, (90.0, 160.0)),             # hidden lines: the bottom wall's hole
        ("left", VO.LeftViewOrientationType, 0.5, (196.0, 240.0)),          # the knee end plate's keyholes; clear of the notes
        ("iso", VO.IsoTopRightViewOrientationType, 0.25, (90.0, 70.0)),
    ], {"angles": [("start", 82.745, "in", 12.0),                          # the knee end: 7.25 deg off square (at 20 its text crossed the inner edge)
                   ("end", 62.798, "out", 14.0)],                          # the door end, square to the pod's X: 27.20 off square
        "seats": "left"}),                                                  # in the 19 mm gap between the front and end views
    "111602": ("111602_P01_BASE-LEVELLING-GLIDE-M10-D40_DWG", "turned", [     # A3, 2:1
        ("front", VO.FrontViewOrientationType, 2.0, (120.0, 200.0)),        # hidden lines: the socket's depth
        ("top", VO.TopViewOrientationType, 2.0, (120.0, 75.0)),             # below it (first angle); notes on the right
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
    if best is None:
        raise RuntimeError("the view has no line ends (%.2f, %.2f)" % target)
    if dist > tol ** 2:
        # a mitred end or a round part has no line end at its extent's corner: use the nearest real
        # corner (the overall size is then measured between line ends, as the shop measures it)
        print("  note: no line end within %.1f of (%.1f, %.1f); using the nearest, %.1f away" % (
            tol, target[0], target[1], dist ** 0.5))
    return best


def holes(view):
    """One circle per hole centre (a hole through two walls can show twice)."""
    _, circles = curves(view)
    seen = {}
    for c in circles:
        x, y = xy(c.centerPoint)
        seen.setdefault((round(x, 3), round(y, 3)), c)
    return sorted(seen.values(), key=lambda c: (xy(c.centerPoint)[0], xy(c.centerPoint)[1]))


def round_centres(view):
    """One arc or circle per centre. A keyhole's Ø12 entry and its slot's round end show as arcs (the
    slot cuts each circle open), so they aren't holes() and only their centres place them."""
    vc = view.viewCurves
    kinds = (adsk.drawing.ViewCurveTypes.ArcViewCurveType, adsk.drawing.ViewCurveTypes.CircleViewCurveType)
    seen = {}
    for i in range(vc.count):
        c = vc.item(i)
        if c.type in kinds:
            x, y = xy(c.centerPoint)
            seen.setdefault((round(x, 3), round(y, 3)), c)
    return sorted(seen.values(), key=lambda c: (xy(c.centerPoint)[0], xy(c.centerPoint)[1]))


def dim(sheet, a, b, place):
    d = sheet.drawingDimensions.addLinearDimension(a, b, dpt(*place), False)
    if d is None:
        raise RuntimeError("addLinearDimension returned None")
    return d


def add_view(sheet, orientation, scale, center, hidden=False):
    """A base view. Visible edges only, unless hidden=True (a tube's view from above, so the hole table
    also finds the bottom wall's holes). Fusion ignores the style given at creation, so it is set again
    on the view (CEILING's first sample)."""
    style = (adsk.drawing.DrawingViewStyleTypes.VisibleAndHiddenEdgesDrawingViewStyleType if hidden
             else adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType)
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
        raise RuntimeError("Views.add returned None")
    if abs(v.scaleValue - scale) > 1e-6:
        v.scaleValue = scale     # the input's scale can be ignored (tools/fusion/README.md)
    try:
        v.style = style          # set again: the style given at creation is ignored
    except Exception as e:      # an older API without a settable style: say so in the log
        print("  note: could not set the view style again (%s)" % e)
    return v


def edge_end(view, x, y):
    """The curve end lying on the view's vertical line at x (its extent's side), nearest to height y."""
    lines, _ = curves(view)
    ends = [p for ln in lines for p in (ln.startPoint, ln.endPoint) if abs(xy(p)[0] - x) < 1e-3]
    if not ends:
        return nearest_end(view, (x, y))
    return min(ends, key=lambda p: abs(xy(p)[1] - y))


def overall(sheet, view, below=True, left=True, gap=8.0, which="both"):
    """The view's overall sizes from its bottom-left corner: "h" its width, "v" its height, or
    "both". A second view of the same part takes only the size the first one doesn't show, so no
    size is dimensioned twice (ISO 129-1). Returns the corner (the hole dimensions' origin)."""
    e = extent(view)
    o = nearest_end(view, (e[0], e[1]))
    n = 0
    if which in ("both", "h") and e[2] - e[0] > 2.0:
        # the true width: points ON the extent's left and right lines (on 110103 the lowest line was the lip
        # seal's envelope, 10 shorter at each end, so the width read 2400 instead of the band's 2420)
        lo, hi = edge_end(view, e[0], e[1]), edge_end(view, e[2], e[1])
        dim(sheet, lo, hi, ((e[0] + e[2]) / 2, e[1] - gap if below else e[3] + gap))
        n += 1
    if which in ("both", "v") and e[3] - e[1] > 2.0:
        dim(sheet, o, nearest_end(view, (e[0], e[3])), (e[0] - gap if left else e[2] + gap, (e[1] + e[3]) / 2))
        n += 1
    return o, n


def hole_dims(sheet, view, origin, side="below", step=6.0, gap=8.0, hs=None):
    """Every hole centre from the datum corner: baseline dimensions along the
    view's x, stacked on one side, plus the hole line's offset along y.
    hs: the curves whose centres to place (default: the view's holes)."""
    e = extent(view)
    hs = holes(view) if hs is None else hs
    done_x = set()
    i = 0
    for c in hs:
        x, y = xy(c.centerPoint)
        if round(x, 2) in done_x:
            continue            # the same dimension again (two holes on one X): once is enough
        done_x.add(round(x, 2))
        ty = e[1] - gap - step * i if side == "below" else e[3] + gap + step * i
        dim(sheet, origin, c.centerPoint, (x, ty))
        i += 1
    if hs:
        y_lines = sorted({round(xy(c.centerPoint)[1], 2) for c in hs})
        for j, yl in enumerate(y_lines):
            c = [h for h in hs if abs(xy(h.centerPoint)[1] - yl) < 0.01][0]
            dim(sheet, origin, c.centerPoint, (e[0] - gap - step * j, (e[1] + yl) / 2))
    return len(hs)


def profile_dims(sheet, view, step=6.0, gap=8.0):
    """A bent part's section (the sill 111301 in the view from the left, where +Y runs to the left):
    its overall height on the left, lowest face to highest (a section's corners need not sit at its
    extent's corners); every vertical face's distance from the flange's outer face (datum B, the
    view's right edge) below the view; and every horizontal face's depth under the ledge's top
    (datum A, its top edge) on its right. Baseline dimensions from that corner, so nothing stacks
    up. The far faces are overall sizes (the depth is on the view from above), so they are left out.
    A dimension that can't be placed is reported in the log, and the rest go on."""
    e = extent(view)
    corner = nearest_end(view, (e[2], e[3]))
    cx, cy = xy(corner)
    lines, _ = curves(view)
    ends = [p for ln in lines for p in (ln.startPoint, ln.endPoint)]
    lo_y, hi_y = min(xy(p)[1] for p in ends), max(xy(p)[1] for p in ends)
    # the leftmost point at each height, so the extension lines to the dimension on the left are short
    low = min((p for p in ends if abs(xy(p)[1] - lo_y) < 1e-3), key=lambda p: xy(p)[0])
    high = min((p for p in ends if abs(xy(p)[1] - hi_y) < 1e-3), key=lambda p: xy(p)[0])
    n = 0
    try:
        dim(sheet, low, high, (e[0] - gap, (e[1] + e[3]) / 2))
        n += 1
    except RuntimeError as exc:
        print("  section height not dimensioned (%s)" % exc)
    xs, ys = {}, {}       # each face's end nearest its dimension line: a vertical face's lower end, a horizontal one's right end
    for ln in lines:
        a, b = ln.startPoint, ln.endPoint
        (x1, y1), (x2, y2) = xy(a), xy(b)
        if abs(x2 - x1) < 1e-3 and abs(y2 - y1) > 0.2:          # a vertical face
            p, k = (a if y1 < y2 else b), round(x1, 2)
            if k not in xs or xy(p)[1] < xy(xs[k])[1]:
                xs[k] = p
        elif abs(y2 - y1) < 1e-3 and abs(x2 - x1) > 0.2:        # a horizontal face
            p, k = (a if x1 > x2 else b), round(y1, 2)
            if k not in ys or xy(p)[0] > xy(ys[k])[0]:
                ys[k] = p
    def distinct(keys):
        # one face position once: Fusion can split a face's edge into collinear pieces whose ends differ in the
        # last digits, so keys that round apart are merged within 0.01 sheet units (0.1 mm at 1:1; the sill's
        # 103.5 and 118.5 were dimensioned twice on 2026-11-01)
        out = []
        for k in sorted(keys, reverse=True):
            if not out or abs(k - out[-1]) > 0.01:
                out.append(k)
        return out
    far_x = [x for x in distinct(xs) if abs(x - cx) > 0.05 and abs(x - e[0]) > 0.05]
    far_y = [y for y in distinct(ys) if abs(y - cy) > 0.05 and abs(y - e[1]) > 0.05]
    for i, x in enumerate(far_x):
        try:
            dim(sheet, corner, xs[x], (x, e[1] - gap - step * i))
            n += 1
        except RuntimeError as exc:
            print("  section face at x %.2f not dimensioned (%s)" % (x, exc))
    for j, y in enumerate(far_y):     # right of the view, 5 apart so the last stays clear of the frame
        try:
            dim(sheet, corner, ys[y], (e[2] + 6.0 + 5.0 * j, (cy + y) / 2))
            n += 1
        except RuntimeError as exc:
            print("  section face at y %.2f not dimensioned (%s)" % (y, exc))
    print("  section: %d dimensions (height and faces from the corner at %.1f, %.1f)" % (n, cx, cy))
    return n


def turned_dims(sheet, front, top, gap=8.0, step=6.0):
    """A turned part on the Z axis (the glide 111602): in the front view (hidden lines on) its overall height, the
    base's height and the socket's depth; in the view from above the base's and the stem's diameters and the hex
    socket's size across flats. Each size once (ISO 129-1). Heights come from the vertical outline lines' ends, as
    Fusion doesn't report a turned part's edges seen edge-on as horizontal lines (the glide's first sheet,
    2026-11-01). A dimension that can't be placed is reported in the log, and the rest go on."""
    n = 0
    e = extent(front)
    lines, _ = curves(front)
    vert = []               # (x, low end, high end) of each vertical line
    for ln in lines:
        a, b = ln.startPoint, ln.endPoint
        (x1, y1), (x2, y2) = xy(a), xy(b)
        if abs(x2 - x1) < 1e-3 and abs(y2 - y1) > 0.05:
            lo, hi = (a, b) if y1 < y2 else (b, a)
            vert.append((x1, lo, hi))
    def put(a, b, place, what):
        try:
            dim(sheet, a, b, place)
            return 1
        except RuntimeError as exc:
            print("  %s not dimensioned (%s)" % (what, exc))
            return 0
    if not vert:
        print("  turned part: no vertical lines in the front view; heights not dimensioned")
    else:
        cx = (e[0] + e[2]) / 2
        top_y = max(xy(hi)[1] for _x, _lo, hi in vert)
        base = min(vert, key=lambda t: t[0])                         # the base's outline, leftmost
        n += put(base[1], base[2], (e[0] - gap, (xy(base[1])[1] + xy(base[2])[1]) / 2), "base height")
        tall = max(vert, key=lambda t: xy(t[2])[1])                  # a line reaching the top
        n += put(base[1], tall[2], (e[0] - gap - step, (xy(base[1])[1] + top_y) / 2), "overall height")
        sock = [t for t in vert if abs(xy(t[2])[1] - top_y) < 1e-3]  # lines reaching the top: the stem's and the socket's
        if len(sock) >= 2:
            inner = min(sock, key=lambda t: abs(t[0] - cx))          # the socket's wall (hidden), nearest the axis
            if abs(inner[0] - cx) < abs(max(sock, key=lambda t: abs(t[0] - cx))[0] - cx) - 1e-3:
                n += put(inner[1], inner[2], (e[2] + gap, (xy(inner[1])[1] + top_y) / 2), "socket depth")
        print("  turned part: %d vertical lines, heights from the base's outline (x %.1f) and the top (y %.1f)" % (
            len(vert), base[0], top_y))
    # from above: the circles (the base and the stem), and the hex socket's two flats parallel to the view's x
    tl, circles = curves(top)
    def radius(c):          # the API gives no circle radius: the distance from its centre to its start point
        (cx, cy), (sx, sy) = xy(c.centerPoint), xy(c.startPoint)
        return ((sx - cx) ** 2 + (sy - cy) ** 2) ** 0.5
    done = set()
    for c in sorted(circles, key=lambda c: -radius(c)):
        r = round(radius(c), 3)
        if r < 1e-3 or r in done:   # each size once (the base's top and bottom edges show as one circle)
            continue
        done.add(r)
        x, y = xy(c.centerPoint)
        try:
            sheet.drawingDimensions.addDiameterDimension(c, dpt(x + r * 0.8 + 8.0, y + r * 0.8 + 8.0 + 6.0 * len(done)))
            n += 1
        except RuntimeError as exc:
            print("  diameter callout skipped (%s)" % exc)
    flats = []
    for ln in tl:
        (x1, y1), (x2, y2) = xy(ln.startPoint), xy(ln.endPoint)
        if abs(y2 - y1) < 1e-3 and abs(x2 - x1) > 0.05:
            flats.append(ln)
    if len(flats) >= 2:
        lo = min(flats, key=lambda l: xy(l.startPoint)[1])
        hi = max(flats, key=lambda l: xy(l.startPoint)[1])
        et = extent(top) or (0.0, 0.0, 0.0, 0.0)
        try:
            dim(sheet, lo.startPoint, hi.startPoint, (et[0] - gap, (xy(lo.startPoint)[1] + xy(hi.startPoint)[1]) / 2))
            n += 1
        except RuntimeError as exc:
            print("  socket across flats not dimensioned (%s)" % exc)
    else:
        print("  the socket's flats not found in the view from above (%d lines)" % len(flats))
    print("  turned part: %d dimensions" % n)
    return n


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


def _outer_edges(view):
    """A facet's outer face in the view from above (Y 0, the view's lowest line): its lines along the bottom of the
    extent, longest first (a hidden line can lie under the visible one)."""
    lines, _ = curves(view)
    e = extent(view)
    flat = [ln for ln in lines if abs(xy(ln.startPoint)[1] - e[1]) < 1e-3 and abs(xy(ln.endPoint)[1] - e[1]) < 1e-3]
    return sorted(flat, key=lambda ln: -abs(xy(ln.endPoint)[0] - xy(ln.startPoint)[0]))


def facet_angles(sheet, view, wanted):
    """Each end cut's angle to the outer face (the Lead's ruling of 2026-11-01: a mitre carries its angle), in the
    view from above: between the outer edge and the line at that end whose angle to it, measured inside the part,
    is the design's (within 0.05 deg; the longest such line, the cut's visible edge, first). Placed "out" (beyond
    the corner, in the opposite sector, which shows the same angle) or "in" (inside the part), at radius rad on
    the sheet. Every try is logged; returns the number made."""
    import math
    lines, _ = curves(view)
    edges = _outer_edges(view)
    if not edges:
        print("  end cut angles: no outer edge found")
        return 0
    (ax, ay), (bx, by) = sorted([xy(edges[0].startPoint), xy(edges[0].endPoint)])
    reach = 0.12 * (bx - ax)            # how far from the edge's end a cut line may meet the edge's line
    n = 0
    for end, want, where, rad in wanted:
        vx = ax if end == "start" else bx
        cands = []
        for ln in lines:
            (x1, y1), (x2, y2) = xy(ln.startPoint), xy(ln.endPoint)
            dx, dy = x2 - x1, y2 - y1
            if abs(dx) < 0.2 or abs(dy) < 0.2:
                continue
            ux, uy = (dx, dy) if dy > 0 else (-dx, -dy)       # along the cut, into the part (Y inward)
            ang = math.degrees(math.atan2(uy, ux))
            inside = ang if end == "start" else 180.0 - ang
            if abs(inside - want) > 0.05:
                continue
            lo = (x1, y1) if y1 < y2 else (x2, y2)
            mx = lo[0] + (ay - lo[1]) * ux / uy                 # where the cut's line meets the edge's line
            if abs(mx - vx) > reach:
                continue
            cands.append((-math.hypot(dx, dy), ln, (mx, ay), (ux, uy)))
        cands.sort(key=lambda c: c[0])
        print("  end cut at the %s: %d line(s) at %.3f deg to the outer face" % (end, len(cands), want))
        done = False
        for _l, ln, V, (ux, uy) in cands:
            L = math.hypot(ux, uy)
            ux, uy = ux / L, uy / L
            ex_ = 1.0 if end == "start" else -1.0                # along the edge, into the part
            bx_, by_ = ex_ + ux, uy                               # the inside angle's bisector
            B = math.hypot(bx_, by_)
            bx_, by_ = bx_ / B, by_ / B
            s = -1.0 if where == "out" else 1.0
            P = (V[0] + s * rad * bx_, V[1] + s * rad * by_)
            for edge in edges:
                try:
                    d = sheet.drawingDimensions.addAngularDimension(edge, ln, dpt(*P))
                except RuntimeError as exc:
                    print("    tried: vertex (%.2f, %.2f), at (%.2f, %.2f): %s" % (V[0], V[1], P[0], P[1], exc))
                    continue
                if d is None:
                    print("    tried: vertex (%.2f, %.2f), at (%.2f, %.2f): no dimension" % (V[0], V[1], P[0], P[1]))
                    continue
                print("    made: vertex (%.2f, %.2f), placed at (%.2f, %.2f) (%s)" % (V[0], V[1], P[0], P[1], where))
                n += 1
                done = True
                break
            if done:
                break
        if not done:
            print("  END CUT ANGLE NOT MADE at the %s (%.3f deg)" % (end, want))
    return n


def seat_heights(sheet, view, side, gap=6.0):
    """The keyhole seats' heights in the end view: each keyhole's slot has straight sides that end at its seat's
    centre (the slot's round end), and they are lines in any view (the keyholes' circles on a plate turned to the
    view come out as ellipses or splines, with no centre). A chain in one column on that side of the view: the
    lowest seat from the bottom corner on that side, then each seat from the one below (Fusion spaces stacked
    dimensions about 10.5 apart, and a stack of two doesn't fit beside these views)."""
    lines, _ = curves(view)
    e = extent(view)
    tops = {}
    for ln in lines:
        (x1, y1), (x2, y2) = xy(ln.startPoint), xy(ln.endPoint)
        if abs(x2 - x1) > 1e-3:
            continue
        if not (1.0 < abs(y2 - y1) < 0.3 * (e[3] - e[1])):     # a slot's side (4.96 at 1:1), not an outline
            continue
        if min(abs(x1 - e[0]), abs(x1 - e[2])) < 1.0 or min(y1, y2) - e[1] < 1.0 or e[3] - max(y1, y2) < 1.0:
            continue
        tops.setdefault(round(max(y1, y2), 2), ln.startPoint if y1 > y2 else ln.endPoint)
    prev, py = edge_end(view, e[0] if side == "left" else e[2], e[1]), e[1]
    x = e[0] - gap if side == "left" else e[2] + gap
    n = 0
    for ty, p in sorted(tops.items()):
        dim(sheet, prev, p, (x, (py + ty) / 2))
        prev, py = p, ty
        n += 1
    sc = getattr(view, "scaleValue", 1.0) or 1.0
    print("  keyhole seats: %d chained height(s) from the slots' sides (seats %s above the bottom face)" % (
        n, ", ".join("%.2f" % ((ty - e[1]) / sc) for ty in sorted(tops))))
    return n


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
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - OUTLINE")
    sk.lines.add([p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
                  p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)])
    sk2 = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE - CIRCLES")
    cx = x0 + length + gap + big / 2
    sk2.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk2.circles.addByCenterRadius(p2(cx, y0), d / 2)


def run(_context):
    app = adsk.core.Application.get()
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document is not a drawing (run with --doc <drawing name>)")
    pn = ARGS["pn"]
    name, kind, views = SPEC[pn][:3]
    dims = SPEC[pn][3] if len(SPEC[pn]) > 3 else [("top", True, "both"), ("front", False, "v")]
    if app.activeDocument.name != name:
        raise RuntimeError("the active drawing is %r, not %r" % (app.activeDocument.name, name))
    sheet = dwg.activeSheet
    print("drawing %s: sheet %.0f x %.0f, %d views before" % (name, sheet.width, sheet.height, sheet.views.count))
    if sheet.views.count:
        raise RuntimeError("the sheet already has views; start a fresh drawing")
    made = {}
    for vname, orient, scale, center in views:
        made[vname] = add_view(sheet, orient, scale, center,
                               hidden=(kind in ("tube", "facet") and vname == "top") or
                               (kind == "turned" and vname == "front"))
        e = extent(made[vname])
        print("  view %-6s scale %g at %s, extent %s" % (vname, scale, center,
                                                        tuple(round(a, 1) for a in e) if e else None))
    n_dims, n_holes, tables = 0, 0, 0
    if kind == "tube":
        o, n = overall(sheet, made["front"], which="h")      # the length; the section's sizes on the end view
        n_dims += n
        top = made["top"]
        e = extent(top)
        o_top = nearest_end(top, (e[0], e[1]))
        n_holes += hole_dims(sheet, top, o_top, side="below")
        n_dims += mitre_angle(sheet, top)      # diameters: in the hole table (callouts cluttered the views)
        tables += hole_table(sheet, top, o_top, "HOLES SEEN FROM ABOVE (THE BOTTOM WALL'S AS HIDDEN LINES), ORIGIN O = DATUMS C, B")
        # the view from below shows the bottom wall's holes; their positions are in the hole table
        # (its dimensions ran into the front view, and a mitred end has no corner at its extent)
        end = made["left"] if "left" in made else made["right"]
        o_l, n = overall(sheet, end, below=True, left=False, gap=6.0)
        n_dims += n
        keys = round_centres(end)   # an end plate's keyhole entries and seats, from the end view's corner
        if keys:
            n_holes += hole_dims(sheet, end, o_l, side="above", hs=keys)
    elif kind == "plate":
        o, n = overall(sheet, made["top"])
        n_dims += n
        if "left" not in made:   # a flat plate: its thickness (its width is on the view from above)
            _o2, n = overall(sheet, made["front"], below=False, which="v")
            n_dims += n
        if holes(made["top"]):
            n_holes += hole_dims(sheet, made["top"], o, side="above")
            made_table = hole_table(sheet, made["top"], o, "HOLES (VIEW FROM ABOVE), ORIGIN O")
            tables += made_table
            if not made_table:   # the diameters are in the hole table; callouts only when it couldn't be made
                n_dims += diameters(sheet, made["top"])
        if "left" in made:       # a bent part's section: its height, and every face from its datum corner
            sec = made["left"]
            n_dims += profile_dims(sheet, sec)
            if holes(sec):
                e3 = extent(sec)
                n_holes += hole_dims(sheet, sec, nearest_end(sec, (e3[0], e3[1])), side="above")
    elif kind == "facet":
        # DL's facets FL1 and FL2 in their own axes: each size once. The front view: the length and the height; the
        # view from above: each end cut's angle, the holes in the hole table (their positions printed once, there);
        # the end view: the width and the keyhole seats' heights
        opts = SPEC[pn][3]
        _o, n = overall(sheet, made["front"], which="both")
        n_dims += n
        top = made["top"]
        e = extent(top)
        o_top = nearest_end(top, (e[0], e[1]))
        n_dims += facet_angles(sheet, top, opts["angles"])
        tables += hole_table(sheet, top, o_top, "HOLES SEEN FROM ABOVE (THE BOTTOM WALL'S AS HIDDEN LINES), ORIGIN O = DATUMS C, B")
        _o, n = overall(sheet, made["left"], below=True, left=False, gap=6.0, which="h")
        n_dims += n
        n_holes += seat_heights(sheet, made["left"], opts["seats"])
    elif kind == "turned":
        n_dims += turned_dims(sheet, made["front"], made["top"])
    else:
        for vname, below, which in dims:
            _o, n = overall(sheet, made[vname], below=below, which=which)
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
