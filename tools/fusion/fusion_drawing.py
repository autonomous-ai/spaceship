"""Shared drawing helpers: one copy for every team's Fusion drawing scripts (PM ruling
2026-11-01, after CEILING's first drawing hit four traps that sit in every team's code).

In a script run through run_script.py:

    from fusion_drawing import insert_image, first_angle_symbol, base_view, DimensionSet

run_script.py makes this module importable inside Fusion and loads it fresh on every
run, so a fix here reaches every team at once.

1. insert_image(sheet, png, x, y, width_mm): a picture inserted with Images.insert comes
   in 58.02 mm wide at scale 1 on A1, A2 and A3, whatever its pixels (measured
   2026-10-31), so a notes image must be scaled to its real width, or its text prints
   about 1.6 mm high. Scale = width_mm / 58.02; (x, y) is the lower-left corner. A sheet
   size not yet measured is refused (pass width_at_scale_1 after measuring it).
2. first_angle_symbol(sheet, x0, cy): the outline is one closed chain in a sketch of its
   own and the circles go in another, and the whole symbol stays at least 6 mm clear
   of the frame and the title block (with no x0, cy it sits just left of the title
   block). Either fault made Fusion's PDF print the outline as a triangle: sharing a
   sketch with the circles (GA sheet 1, 2026-10-31), and an edge on the border's line,
   whose corners the PDF pulled onto the border's corner (FRONT, CEILING 2026-11-01).
   A symbol closer than that is refused.
3. base_view(sheet, orientation, scale, at, style): Fusion ignores the style given in the
   view input (hidden lines showed on every view, the iso too), so the style and scale
   are set again on the made view and checked.
4. DimensionSet(sheet): adds each linear dimension once. The same two points measured the
   same way again (either order, within 0.01 mm) are skipped. Dimensions placed by an
   earlier run can't be read back (the API gives only their type), so a sheet that
   already has dimensions is refused unless allow_existing=True: give a sheet its
   dimensions in one run, or redo it from an empty version.
"""

try:
    import adsk
    import adsk.core
    import adsk.drawing
except ImportError:                 # offline tests
    adsk = None

IMAGE_WIDTH_AT_SCALE_1_MM = 58.02    # measured on A1, A2 and A3 (2026-10-31)
MEASURED_SHEETS = {"A1": (841.0, 594.0), "A2": (594.0, 420.0), "A3": (420.0, 297.0)}
SYMBOL_NAME = "PROJECTION SYMBOL - FIRST ANGLE"
# Fusion's ISO sheets (measured on A1 and A2 exports, 2026-11-01; assumed on the other A
# sizes): the frame 20 mm in on the left and 10 mm on the other sides (ISO 5457), the
# title block 180 x 47 mm in the frame's bottom-right corner
FRAME_MARGINS = (20.0, 10.0, 10.0, 10.0)        # left, bottom, right, top
TITLE_BLOCK_SIZE = (180.0, 47.0)
SYMBOL_CLEARANCE = 6.0                           # FRONT's sample: 6 mm in from the border


def _point2d(x, y):
    return adsk.core.Point2D.create(x, y)


def _drawing_point(x, y):
    return adsk.drawing.DrawingPoint.create(_point2d(x, y))


def sheet_size_name(sheet: "adsk.drawing.Sheet", tol=1.0):
    """"A1", "A2" or "A3" when the sheet is one of the measured sizes (either way up)."""
    w, h = float(sheet.width), float(sheet.height)
    for name, (a, b) in MEASURED_SHEETS.items():
        if (abs(w - a) <= tol and abs(h - b) <= tol) or (abs(w - b) <= tol and abs(h - a) <= tol):
            return name
    return None


def image_scale(width_mm, width_at_scale_1=IMAGE_WIDTH_AT_SCALE_1_MM):
    if width_mm <= 0 or width_at_scale_1 <= 0:
        raise ValueError("widths must be positive")
    return float(width_mm) / float(width_at_scale_1)


def insert_image(sheet: "adsk.drawing.Sheet", png, x, y, width_mm, width_at_scale_1=None):
    """Insert a picture with its lower-left corner at (x, y) sheet mm, width_mm wide.
    Returns the scale used. Raises on a sheet size not measured or a failed insert."""
    if width_at_scale_1 is None:
        size = sheet_size_name(sheet)
        if size is None:
            raise RuntimeError("sheet %g x %g mm isn't a measured size (%s); measure its picture width "
                               "at scale 1 and pass width_at_scale_1" % (
                                   sheet.width, sheet.height, ", ".join(sorted(MEASURED_SHEETS))))
        width_at_scale_1 = IMAGE_WIDTH_AT_SCALE_1_MM
    scale = image_scale(width_mm, width_at_scale_1)
    ii = sheet.images.createInput()
    ii.imageFilePath = png
    ii.position = _point2d(x, y)
    ii.scale = scale
    if not sheet.images.insert(ii):
        raise RuntimeError("Images.insert returned False for %s" % png)
    return scale


def symbol_outline(x0, cy, small=5.0, big=10.0, length=10.0):
    """The truncated cone seen from the side, as one closed chain of 5 points."""
    return [(x0, cy - small / 2), (x0 + length, cy - big / 2), (x0 + length, cy + big / 2),
            (x0, cy + small / 2), (x0, cy - small / 2)]


def frame_box(sheet):
    """(x0, y0, x1, y1) of the drawing frame, sheet mm."""
    left, bottom, right, top = FRAME_MARGINS
    return (left, bottom, float(sheet.width) - right, float(sheet.height) - top)


def title_block_box(sheet):
    """(x0, y0, x1, y1) of the title block in the frame's bottom-right corner."""
    _l, bottom, right, _t = FRAME_MARGINS
    w, h = TITLE_BLOCK_SIZE
    x1 = float(sheet.width) - right
    return (x1 - w, bottom, x1, bottom + h)


def symbol_box(x0, cy, small=5.0, big=10.0, length=10.0, gap=4.0):
    """(x0, y0, x1, y1) the whole symbol covers: the outline and the circles."""
    return (x0, cy - big / 2, x0 + length + gap + big, cy + big / 2)


def symbol_clear(sheet, box, clearance=SYMBOL_CLEARANCE):
    """Why the symbol at `box` is too close to the frame or the title block, or None."""
    fx0, fy0, fx1, fy1 = frame_box(sheet)
    if box[0] < fx0 + clearance or box[1] < fy0 + clearance or box[2] > fx1 - clearance \
            or box[3] > fy1 - clearance:
        return "it is within %g mm of the sheet's border (frame %s, symbol %s)" % (
            clearance, tuple(round(v, 1) for v in (fx0, fy0, fx1, fy1)), tuple(round(v, 1) for v in box))
    tx0, ty0, tx1, ty1 = title_block_box(sheet)
    if not (box[2] <= tx0 - clearance or box[3] <= ty0 - clearance or box[1] >= ty1 + clearance):
        return "it is within %g mm of the title block (title block %s, symbol %s)" % (
            clearance, tuple(round(v, 1) for v in (tx0, ty0, tx1, ty1)), tuple(round(v, 1) for v in box))
    return None


def default_symbol_place(sheet, small=5.0, big=10.0, length=10.0, gap=4.0, clearance=SYMBOL_CLEARANCE):
    """(x0, cy): just left of the title block, its foot `clearance` above the frame."""
    tx0, ty0, _tx1, _ty1 = title_block_box(sheet)
    return (tx0 - clearance - (length + gap + big), ty0 + clearance + big / 2)


def first_angle_symbol(sheet: "adsk.drawing.Sheet", x0=None, cy=None, small=5.0, big=10.0, length=10.0, gap=4.0,
                       name=SYMBOL_NAME, clearance=SYMBOL_CLEARANCE):
    """ISO first-angle symbol, the outline from (x0, cy - small/2); the end view gap mm
    to its right; at least `clearance` mm from the frame and the title block (with no
    x0, cy: just left of the title block). Returns (outline sketch, circles sketch)."""
    if x0 is None or cy is None:
        x0, cy = default_symbol_place(sheet, small, big, length, gap, clearance)
    why = symbol_clear(sheet, symbol_box(x0, cy, small, big, length, gap), clearance)
    if why:
        raise RuntimeError("first-angle symbol refused: %s; Fusion's PDF pulls an outline touching "
                           "a border line onto it (a triangle)" % why)
    have = [sheet.sketches.item(i).name for i in range(sheet.sketches.count)]
    if any(n == name or n.startswith(name + " ") for n in have):
        raise RuntimeError("the sheet has a %r sketch already" % name)
    outline = sheet.sketches.add(name)
    if outline.lines.add([_point2d(*p) for p in symbol_outline(x0, cy, small, big, length)]) is None:
        raise RuntimeError("the projection symbol's outline wasn't made")
    circles = sheet.sketches.add(name + " CIRCLES")
    cx = x0 + length + gap + big / 2
    for r in (big / 2, small / 2):
        if circles.circles.addByCenterRadius(_point2d(cx, cy), r) is None:
            raise RuntimeError("a circle of the projection symbol wasn't made")
    return outline, circles


# What was seen (2026-11-01): GA sheet 1's isometric view at 0.0375 read back near the scale asked but not within
# 1e-9 of it, so the old 1e-9 check refused a view at the right scale. The error printed 0.0375 at 6 digits, so it
# was 1e-9 to 5e-8 off, up to 1.3e-6 of the value. 1:5 (ELECTRICAL's 711001, two live runs) and 1:20 (the GA
# sections) passed the 1e-9 check. How Fusion keeps a scale isn't known, so a scale counts as set within 1e-5 of the
# value, which still refuses any wrong scale (1:26.67 and 1:26.7 differ by 1.2e-3 of theirs), and each view's
# read-back is printed with all its digits.
SCALE_REL_TOL = 1e-5


def scale_is(got, want):
    """True when a view's read-back scale `got` is the scale `want` (SCALE_REL_TOL of it)."""
    return abs(got - want) <= SCALE_REL_TOL * abs(want)


def base_view(sheet: "adsk.drawing.Sheet", orientation, scale, at, style=None):
    """A base view at `at` (sheet mm, its centre), with the style and scale set again on
    the made view and checked (Fusion ignores the input's style). Default style:
    visible edges only, no hidden lines."""
    if style is None:
        style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
    inp = sheet.views.createBaseViewInput()
    vp = inp.viewParameters
    vp.orientation = orientation
    vp.scaleValue = scale
    vp.style = style
    inp.placementPoint = _drawing_point(*at)
    view = sheet.views.add(inp)
    if view is None:
        raise RuntimeError("Views.add returned None")
    if view.style != style:
        view.style = style
    if not scale_is(view.scaleValue, scale):
        view.scaleValue = scale
    if adsk is not None:
        adsk.doEvents()
    if view.style != style:
        raise RuntimeError("the view's style stays %s after setting %s" % (view.style, style))
    got = view.scaleValue
    print("view scale: asked %r, read back %r" % (scale, got))     # all the digits, for the record
    if not scale_is(got, scale):
        raise RuntimeError("the view's scale stays %r after setting %r" % (got, scale))
    return view


def _xy(p):
    """(x, y) of a DrawingPoint, a Point2D or an (x, y) pair."""
    c = getattr(p, "coordinate", p)
    return (float(c.x), float(c.y)) if hasattr(c, "x") else (float(c[0]), float(c[1]))


def measured_direction(a, b, place, aligned=False):
    """What a linear dimension measures: "aligned", or "x" when its line sits above or
    below the two points (a horizontal size), else "y"."""
    if aligned:
        return "aligned"
    (ax, ay), (bx, by), (px, py) = _xy(a), _xy(b), _xy(place)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    return "x" if abs(py - my) >= abs(px - mx) else "y"


class DimensionSet:
    """Linear dimensions on one sheet, each placed once."""

    def __init__(self, sheet: "adsk.drawing.Sheet", tol=0.01, allow_existing=False, log=print):
        self.sheet, self.tol, self.log = sheet, tol, log
        self.placed = []
        have = sheet.drawingDimensions.count
        if have and not allow_existing:
            raise RuntimeError("the sheet has %d dimension(s) from an earlier run; they can't be read "
                               "back, so more could double one. Give a sheet its dimensions in one run, "
                               "or redo it from an empty version (allow_existing=True to add anyway)" % have)

    def _same(self, p, q):
        return abs(p[0] - q[0]) <= self.tol and abs(p[1] - q[1]) <= self.tol

    def linear(self, a, b, place, aligned=False, label=""):
        """Place the dimension unless the same one is on the sheet already; returns it or None."""
        pa, pb, way = _xy(a), _xy(b), measured_direction(a, b, place, aligned)
        for qa, qb, qway in self.placed:
            if qway == way and ((self._same(pa, qa) and self._same(pb, qb)) or
                                (self._same(pa, qb) and self._same(pb, qa))):
                self.log("fusion_drawing: %s skipped: the same dimension is on the sheet already"
                         % (label or "a dimension"))
                return None
        dim = self.sheet.drawingDimensions.addLinearDimension(a, b, place, aligned)
        if dim is None:
            raise RuntimeError("addLinearDimension returned None%s" % (" for " + label if label else ""))
        self.placed.append((pa, pb, way))
        return dim
