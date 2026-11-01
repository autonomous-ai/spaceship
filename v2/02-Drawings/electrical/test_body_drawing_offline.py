#!/usr/bin/env python3
"""Offline test of drawing 711001's scripts (make_body_drawing.py, body_views.py, body_drawing_text.py): no Fusion.

    python3 v2/02-Drawings/electrical/test_body_drawing_offline.py

It fakes the adsk.drawing objects the script uses. Each faked view has the size Fusion should give it (at the route
model's size: FRONT w x h at 1:2, the views from above and below w x d, the side views d x h) at the centre the
script asks for, and its holes where Fusion draws them, entered here by hand from the build's numbers (not from
body_views.py): Fusion's standard Bottom turned 180 degrees from the first-angle view from below, as on the sheet of
2026-11-01 (Reviewer 7's P1), which the drawing keeps as view D, marked as turned. Like Fusion's API (probe of
2026-11-01), a view also lists the circles of holes hidden behind a wall; its PDF export prints only the seen ones:
lines and circles on Fusion's "Visible" layer, a centre mark on each hole on the "Smart Centers" layer only when the
view's options cover round cuts (this body's holes are cut extrudes), the dimensions' values and the "Created by"
field. Then it checks:
- every view, dimension, datum and the symbol sits inside the A2 frame, clear of the title block, the text block
  and the other views; datum boxes 1.5 mm clear of views, dimension lines and each other; no Fusion hole table;
- each view's holes where the STEP puts them, hidden ones allowed in Fusion's list: a Bottom that comes back the
  other way round (not turned) stops the run before any dimension, as does a wrong-size FRONT; view D stands apart;
- the H05-H08 pitch (236 x 240 since the PEM nuts) joins the holes' centres; the overall sizes join view line vertices;
- the finished PDF: no account name; Autonomous in Created by, author and creator; units, material, finish,
  tolerance; the hole table; a tag beside each hole crossing no line; the pitch printed in brackets; centre
  marks; "D (turned 180°)" over view D and arrow D under the FRONT; the fonts subset (well under 1 MB); and the
  drawing check's own reading (no maker line, the traps); a raw PDF whose view D isn't turned stops the finish;
- the PM's four drawing traps (shared helpers, tools/fusion/fusion_drawing.py): letters 2.5 mm or more (headings
  3.5), the symbol's outline alone in its sketch, visible edges only on every view (the fake hands each view back
  with hidden lines, as Fusion does), no dimension twice. Centre marks go on after every dimension.
It tests the scripts' logic; Fusion's own view conventions are checked on the real sheet.
"""

import importlib.util
import json
import os
import re
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("SPACESHIP_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "fusion"))         # fusion_drawing, as run_script.py gives it
FRAME = (20.0, 10.0, 584.0, 410.0)
TITLE = (404.0, 10.0, 584.0, 57.0)
TEXT = (410.0, 62.0, 584.0, 315.0)
FAKE_NAME = "Jordan Quill"          # stands in for the account holder's name Fusion prints
PT = 72.0 / 25.4


# ------------------------------------------------------------------ fake adsk

class Point2D:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @staticmethod
    def create(x, y):
        return Point2D(x, y)


class DrawingPoint:
    def __init__(self, x, y, owner=None):
        self.coordinate = Point2D(x, y)
        self.owner = owner

    @staticmethod
    def create(p):
        return DrawingPoint(p.x, p.y, "free")


class Enum:
    def __init__(self, *names):
        for i, n in enumerate(names):
            setattr(self, n, i)


VCT = Enum("LineViewCurveType", "ArcViewCurveType", "CircleViewCurveType")
VOT = Enum("FrontViewOrientationType", "BackViewOrientationType", "TopViewOrientationType",
           "BottomViewOrientationType", "RightViewOrientationType", "LeftViewOrientationType",
           "IsoTopRightViewOrientationType")
STYLE = Enum("VisibleEdgesDrawingViewStyleType", "VisibleAndHiddenEdgesDrawingViewStyleType")
LOG = []                            # the order things are made in: "view", "dim", "centre"


class Curve:
    def __init__(self, kind, a=None, b=None, c=None, r=None, hidden=False):
        self.type, self.hidden = kind, hidden
        if kind == VCT.CircleViewCurveType:           # Fusion: a closed curve's start point lies on it
            self.centerPoint = DrawingPoint(*c, owner="circle")
            self.startPoint = DrawingPoint(c[0] + r, c[1], owner="circle")
            self.endPoint = self.startPoint
            self.r = r
        else:
            self.startPoint = DrawingPoint(*a, owner="line")
            self.endPoint = DrawingPoint(*b, owner="line")
            self.centerPoint = None


class Curves:
    def __init__(self, items):
        self.items, self.count = items, len(items)

    def item(self, i):
        return self.items[i]


def _opts():
    return types.SimpleNamespace(isAppliedToHoles=False, isAppliedToRoundCuts=False)


class View:
    """Fusion hands a new view back with hidden lines whatever style the input asked for (CEILING's sample)."""
    def __init__(self, orientation, scale, curves):
        self.orientation, self.scaleValue, self.viewCurves = orientation, scale, Curves(curves)
        self.style = STYLE.VisibleAndHiddenEdgesDrawingViewStyleType
        self._marks, self._lines = _opts(), _opts()

    def getCenterMarkOptions(self):
        return types.SimpleNamespace(**vars(self._marks))

    def getCenterLineOptions(self):
        return types.SimpleNamespace(**vars(self._lines))

    def setCenterMarkOptions(self, o):
        LOG.append("centre")
        self._marks = types.SimpleNamespace(isAppliedToHoles=o.isAppliedToHoles,
                                            isAppliedToRoundCuts=getattr(o, "isAppliedToRoundCuts", False))
        return True

    def setCenterLineOptions(self, o):
        self._lines = types.SimpleNamespace(isAppliedToHoles=o.isAppliedToHoles,
                                            isAppliedToRoundCuts=getattr(o, "isAppliedToRoundCuts", False))
        return True

    def marked(self):
        """Fusion marks this body's holes only for round cuts: they are cut extrudes, not hole features."""
        return self._marks.isAppliedToRoundCuts


RELIEF = 0.85      # sheet mm: the folded body's corner reliefs leave no vertex at the view's corner (live run)


def rect(cx, cy, w, h, relief=RELIEF):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    r = relief
    return [Curve(VCT.LineViewCurveType, (x0 + r, y0), (x1 - r, y0)), Curve(VCT.LineViewCurveType, (x1, y0 + r), (x1, y1 - r)),
            Curve(VCT.LineViewCurveType, (x1 - r, y1), (x0 + r, y1)), Curve(VCT.LineViewCurveType, (x0, y1 - r), (x0, y0 + r))]


def model_size():
    sys.path.insert(0, os.path.join(REPO, "v2", "01-CAD-Native", "electrical"))
    import electrical_model as M
    v = M.values()
    return v["pu_w"], v["pu_h"], v["pu_d"]


class Fake:
    """The part as Fusion shows it, at the model's size: sizes per orientation (sheet mm at the view's scale), and
    each view's holes from its lower left corner in part mm (hand-entered from the build: H01/H02 Ø19.1 in the
    right side at Y 175 and 215, 50.5 from the back; H03 Ø19.1 in the top at X 251, 50.5 from the back; H04 Ø22.2 in
    the bottom at X 55, 18 from the back; H05-H08 Ø5.94 in the lips (PEM CLA-M4-1), 30 from the sides and 10 from top
    and bottom; H09 Ø5.0 in the bottom at X 110, 36 from the back (PEM FHA-M5-12 earth stud))."""
    W, H, D = model_size()
    LIP = 22.0
    wrong_front = False
    bottom_unturned = False      # a Fusion whose Bottom came back the first-angle way: the run must stop

    @classmethod
    def holes(cls, o):
        """[(x, y, diameter, hidden)] from the view's lower left corner, part mm."""
        W, H, D = cls.W, cls.H, cls.D
        if o == VOT.FrontViewOrientationType:
            return [(30, 10, 5.94, False), (W - 30, 10, 5.94, False), (30, H - 10, 5.94, False),
                    (W - 30, H - 10, 5.94, False)]
        if o == VOT.BottomViewOrientationType and cls.bottom_unturned:
            return [(55, 18, 22.2, False), (110, 36, 5.0, False), (251, 50.5, 19.1, True)]
        if o == VOT.BottomViewOrientationType:          # Fusion's Bottom: turned 180; H03 behind the bottom wall
            return [(W - 55, D - 18, 22.2, False), (W - 110, D - 36, 5.0, False), (W - 251, D - 50.5, 19.1, True)]
        if o == VOT.TopViewOrientationType:             # the open side at the bottom, the back (C) at the top
            return [(251, D - 50.5, 19.1, False), (55, D - 18, 22.2, True), (110, D - 36, 5.0, True)]
        if o == VOT.RightViewOrientationType:           # the open side on the left, the back on the right
            return [(D - 50.5, 175, 19.1, False), (D - 50.5, 215, 19.1, False)]
        if o == VOT.LeftViewOrientationType:            # the back on the left: the right side's holes behind a wall
            return [(50.5, 175, 19.1, True), (50.5, 215, 19.1, True)]
        return []

    @classmethod
    def size(cls, o, s):
        if o == VOT.FrontViewOrientationType:
            return (cls.W * s, (cls.D if cls.wrong_front else cls.H) * s)
        if o in (VOT.TopViewOrientationType, VOT.BottomViewOrientationType):
            return (cls.W * s, cls.D * s)
        if o in (VOT.LeftViewOrientationType, VOT.RightViewOrientationType):
            return (cls.D * s, cls.H * s)
        return ((cls.W + cls.D) * 0.866 * s, (cls.H + (cls.W + cls.D) * 0.5) * s)   # iso

    @classmethod
    def view(cls, o, s, c):
        w, h = cls.size(o, s)
        cv = rect(c[0], c[1], w, h)
        if o == VOT.FrontViewOrientationType and not cls.wrong_front:
            cv += rect(c[0], c[1], w - 2 * cls.LIP * s, h - 2 * cls.LIP * s, relief=0.0)      # the lips' inner edges
        if not (o == VOT.FrontViewOrientationType and cls.wrong_front):
            for dx, dy, dia, hid in cls.holes(o):
                cv.append(Curve(VCT.CircleViewCurveType, c=(c[0] - w / 2 + dx * s, c[1] - h / 2 + dy * s), r=dia / 2 * s,
                                hidden=hid))
        return View(o, s, cv)


class BaseViewInput:
    def __init__(self):
        self.viewParameters = types.SimpleNamespace(orientation=None, scaleValue=1.0, style=None,
                                                    centerMarkOptions=_opts(), centerLineOptions=_opts())
        self.placementPoint = None


class Views:
    def __init__(self):
        self.items = []

    @property
    def count(self):
        return len(self.items)

    def item(self, i):
        return self.items[i]

    def createBaseViewInput(self):
        return BaseViewInput()

    def add(self, inp):
        LOG.append("view")
        vp, c = inp.viewParameters, inp.placementPoint.coordinate
        v = Fake.view(vp.orientation, vp.scaleValue, (c.x, c.y))
        self.items.append(v)
        return v


class Dims:
    def __init__(self):
        self.made = []

    @property
    def count(self):
        return len(self.made)

    def addLinearDimension(self, a, b, place, aligned):
        LOG.append("dim")
        self.made.append((a, b, place))
        return object()


class HoleTables:
    def __init__(self):
        self.made = []

    @property
    def count(self):
        return len(self.made)

    def createInput(self):
        return types.SimpleNamespace(view=None, originPoint=None, title="")

    def add(self, inp):
        self.made.append(inp)
        return object()


class Symbols:
    def __init__(self):
        self.made = []

    def createDatumIdentifierInput(self):
        return types.SimpleNamespace(identifier="", viewCurve=None, placementPoint=None, leaderPoints=[])

    def addDatumIdentifier(self, inp):
        if len(inp.leaderPoints) < 2:          # as Fusion 2706 does (live run 2026-10-31)
            raise RuntimeError("leaderPoints must contain at least two DrawingPoint objects.")
        self.made.append(inp)
        return object()


class Sketch:
    def __init__(self, name):
        self.name, self.chains, self.circles_made = name, [], []
        self.lines = types.SimpleNamespace(add=lambda pts: self.chains.append([(p.x, p.y) for p in pts]) or object())
        self.circles = types.SimpleNamespace(addByCenterRadius=lambda c, r: self.circles_made.append((c.x, c.y, r)) or object())

    def points(self):
        return [p for ch in self.chains for p in ch] + \
            [q for (x, y, r) in self.circles_made for q in ((x - r, y - r), (x + r, y + r))]


class Sketches:
    def __init__(self):
        self.made = []

    @property
    def count(self):
        return len(self.made)

    def item(self, i):
        return self.made[i]

    def add(self, name):
        self.made.append(Sketch(name))
        return self.made[-1]

    @property
    def points(self):
        return [p for sk in self.made for p in sk.points()]


class Sheet:
    def __init__(self):
        self.name, self.width, self.height = "Sheet1", 594.0, 420.0
        self.views, self.drawingDimensions = Views(), Dims()
        self.holeTables, self.drawingSymbols, self.sketches = HoleTables(), Symbols(), Sketches()


def fake_pdf(path, sheet, scale):
    """The sheet as Fusion's PDF prints it: view lines and circles on the "Visible" layer, a centre mark on each
    circle of a view marked for round cuts, each dimension's value at its place (a vertical one turned a quarter),
    the symbol's sketches on their own layers, and the stock title block's "Created by" field with a name."""
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=594 * PT, height=420 * PT)
    P = lambda x, y: fitz.Point(x * PT, (420 - y) * PT)            # noqa: E731
    vis, cm, dl = doc.add_ocg("Visible"), doc.add_ocg("Smart Centers"), doc.add_ocg("FD_Dimensions")
    page.draw_rect(fitz.Rect(20 * PT, 10 * PT, 584 * PT, 410 * PT))
    for v in sheet.views.items:
        for c in v.viewCurves.items:
            if c.type == VCT.CircleViewCurveType:
                if c.hidden:                            # the PDF prints visible edges only
                    continue
                x, y = c.centerPoint.coordinate.x, c.centerPoint.coordinate.y
                page.draw_circle(P(x, y), c.r * PT, oc=vis, width=0.35 * PT)
                if v.marked():                          # Fusion's: a cross at the centre, dashes past the circle
                    for a0, a1 in ((-0.9, 0.9), (c.r + 0.6, c.r + 2.1), (-c.r - 2.1, -c.r - 0.6)):
                        page.draw_line(P(x + a0, y), P(x + a1, y), oc=cm, width=0.18 * PT)
                        page.draw_line(P(x, y + a0), P(x, y + a1), oc=cm, width=0.18 * PT)
            else:
                a, b = c.startPoint.coordinate, c.endPoint.coordinate
                page.draw_line(P(a.x, a.y), P(b.x, b.y), oc=vis, width=0.35 * PT)
    for a, b, p in sheet.drawingDimensions.made:
        ax, ay, bx, by = a.coordinate.x, a.coordinate.y, b.coordinate.x, b.coordinate.y
        px, py = p.coordinate.x, p.coordinate.y
        horizontal = abs(py - (ay + by) / 2) >= abs(px - (ax + bx) / 2)
        value = "%g" % round((abs(bx - ax) if horizontal else abs(by - ay)) / scale, 3)
        if horizontal:
            page.draw_line(P(min(ax, bx), py), P(max(ax, bx), py), oc=dl, width=0.18 * PT)
            for x, y in ((ax, ay), (bx, by)):
                page.draw_line(P(x, y + (1 if py > y else -1)), P(x, py + (1.5 if py > y else -1.5)), oc=dl, width=0.18 * PT)
            page.insert_text(P(px - 3.0, py + 1.0), value, fontsize=3.5 * PT, oc=dl)
        else:
            page.draw_line(P(px, min(ay, by)), P(px, max(ay, by)), oc=dl, width=0.18 * PT)
            for x, y in ((ax, ay), (bx, by)):
                page.draw_line(P(x + (1 if px > x else -1), y), P(px + (1.5 if px > x else -1.5), y), oc=dl, width=0.18 * PT)
            page.insert_text(P(px - 2.0, py - 3.0), value, fontsize=3.5 * PT, rotate=90, oc=dl)   # left of its line
    for sk in sheet.sketches.made:
        layer = doc.add_ocg(sk.name)
        for ch in sk.chains:
            page.draw_polyline([P(x, y) for x, y in ch], oc=layer, width=0.25 * PT)
        for x, y, r in sk.circles_made:
            page.draw_circle(P(x, y), r * PT, oc=layer, width=0.25 * PT)
    page.insert_text(P(495, 52), "Created by", fontsize=2.6 * PT)
    page.insert_text(P(495, 47), FAKE_NAME, fontsize=3.6 * PT)
    page.insert_text(P(545, 47), "01/11/26", fontsize=3.6 * PT)
    doc.set_metadata({"creator": "Fusion Drawings", "producer": "pdfplot18.bundle"})
    doc.save(path)


class ExportManager:
    def __init__(self, sheet, scale):
        self.sheet, self.scale = sheet, scale

    def createPDFExportOptions(self, path):
        return types.SimpleNamespace(path=path, openPDF=True, useLineWeights=False)

    def execute(self, opts):
        fake_pdf(opts.path, self.sheet, self.scale)
        return True


def load(name):
    adsk = types.ModuleType("adsk")
    core, drawing, fusion = (types.ModuleType("adsk." + n) for n in ("core", "drawing", "fusion"))
    core.Point2D = Point2D
    drawing.DrawingPoint, drawing.ViewCurveTypes = DrawingPoint, VCT
    drawing.ViewOrientationTypes, drawing.DrawingViewStyleTypes = VOT, STYLE
    drawing.Drawing = types.SimpleNamespace(cast=lambda x: x)
    fusion.DimensionOrientations = types.SimpleNamespace(HorizontalDimensionOrientation=0,
                                                         VerticalDimensionOrientation=1)
    adsk.core, adsk.drawing, adsk.fusion = core, drawing, fusion
    adsk.doEvents = lambda: None
    sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.drawing": drawing, "adsk.fusion": fusion})
    sys.modules.pop("fusion_drawing", None)           # bind the shared helpers to these fakes
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Ref:
    def __init__(self, name, stale):
        self.dataFile, self.version, self.isOutOfDate = types.SimpleNamespace(name=name), 1, stale


class Refs:
    def __init__(self, items):
        self.items, self.count = items, len(items)

    def item(self, i):
        return self.items[i]


class Doc:
    """The drawing document: one reference to the body's design, out of date when the design has a newer version."""
    def __init__(self, name, stale=True, body="711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD"):
        self.name = name
        self.documentReferences = Refs([Ref(body, stale)])
        self.updated = False

    def updateAllReferences(self):
        LOG.append("update")
        for r in self.documentReferences.items:
            r.isOutOfDate = False
        self.updated = True
        return True


def app_with(sheet, dwg_name, doc=None, scale=0.5):
    dwg = types.SimpleNamespace(activeSheet=sheet, exportManager=ExportManager(sheet, scale))
    return types.SimpleNamespace(activeProduct=dwg, activeDocument=doc or Doc(dwg_name + " v1"))


# ------------------------------------------------------------------ the test

def box_of(view):
    pts = [(c.startPoint.coordinate.x, c.startPoint.coordinate.y) for c in view.viewCurves.items
           if c.type == VCT.LineViewCurveType] + \
          [(c.endPoint.coordinate.x, c.endPoint.coordinate.y) for c in view.viewCurves.items if c.type == VCT.LineViewCurveType]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def inside(p, b, pad=0.0):
    return b[0] - pad < p[0] < b[2] + pad and b[1] - pad < p[1] < b[3] + pad


def overlap(a, b, gap=0.0):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def main():
    failures = []

    def check(cond, what):
        print(("ok   " if cond else "FAIL ") + what)
        if not cond:
            failures.append(what)

    # a real run's raw files in .raw/ stay as they were, however the checks end (a finish step that stops raises)
    raw_dir = os.path.join(REPO, "v2", "02-Drawings", "electrical", ".raw")
    existed = os.path.isdir(raw_dir)
    kept = {os.path.join(raw_dir, n): open(os.path.join(raw_dir, n), "rb").read()
            for n in (os.listdir(raw_dir) if existed else [])}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            md = load("make_body_drawing")
            md.ARGS.clear()
            md.ARGS.update({"repo_root": REPO})
            raw_dir = os.path.join(REPO, md.HERE, ".raw")
            raw = os.path.join(raw_dir, md.DWG + ".pdf")
            raw_views = raw[:-4] + ".views.json"
            # a Bottom that comes back the first-angle way (not as view D says) stops the run before any dimension
            Fake.bottom_unturned = True
            sheet0 = Sheet()
            try:
                md.annotate(app_with(sheet0, md.DWG))
                turned = ""
            except RuntimeError as e:
                turned = str(e)
            Fake.bottom_unturned = False
            check("holes not where the STEP puts them" in turned and "d view" in turned and
                  sheet0.drawingDimensions.count == 0 and not sheet0.drawingSymbols.made,
                  "a Bottom that isn't turned stops the run before any dimension or datum (H04 against the STEP)")
            # the real sequence, with the named view from below
            sheet = Sheet()
            del LOG[:]
            doc = Doc(md.DWG + " v1", stale=True)
            md.annotate(app_with(sheet, md.DWG, doc))
            check(doc.updated and LOG.index("update") < LOG.index("view"),
                  "an out-of-date reference to the body's design is updated before any view (run of 2026-11-01)")
            views = sheet.views.items
            boxes = [box_of(v) for v in views]
            check(len(views) == 6, "6 views (front, top, D, left, right, iso), got %d" % len(views))
            check(views[2].orientation == VOT.BottomViewOrientationType, "view D is Fusion's Bottom")
            check(all(inside((b[0], b[1]), FRAME) and inside((b[2], b[3]), FRAME) for b in boxes),
                  "every view inside the A2 frame")
            check(not any(overlap(b, TITLE) for b in boxes), "no view on the title block")
            check(not any(overlap(b, TEXT) for b in boxes), "no view on the text block")
            pairs = [(i, j) for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if overlap(boxes[i], boxes[j], 5.0)]
            check(not pairs, "views at least 5 mm apart (%s)" % pairs)
            f, t, bt, lf, rt = boxes[:5]
            check(abs(t[3] - (f[1] - md.GAP)) < 1e-6, "first angle: TOP one gap below the FRONT")
            check(not (abs((bt[0] + bt[2]) / 2 - (f[0] + f[2]) / 2) < 1.0 and bt[1] > f[3]) and
                  abs((bt[0] + bt[2]) / 2 - md.D_AT[0]) < 1e-6 and abs((bt[1] + bt[3]) / 2 - md.D_AT[1]) < 1e-6,
                  "view D stands apart (top right), not where the first-angle view from below would go")
            check(abs(lf[0] - (f[2] + md.GAP)) < 1e-6 and abs(rt[2] - (f[0] - md.GAP)) < 1e-6,
                  "first angle: view from the LEFT on the right, from the RIGHT on the left")
            check(all(v.style == STYLE.VisibleEdgesDrawingViewStyleType for v in views),
                  "(3) every view, the iso too, visible edges only (handed back with hidden lines, as Fusion does)")
            check(all(v.getCenterMarkOptions().isAppliedToRoundCuts and v.getCenterLineOptions().isAppliedToRoundCuts
                      and v.getCenterMarkOptions().isAppliedToHoles for v in views[:5]) and
                  not views[5].getCenterMarkOptions().isAppliedToRoundCuts,
                  "centre marks and lines for holes and round cuts on the 5 orthographic views, none on the iso")
            check("centre" in LOG and "dim" in LOG and max(i for i, e in enumerate(LOG) if e == "dim") <
                  min(i for i, e in enumerate(LOG) if e == "centre"), "centre marks set after every dimension")
            dims = sheet.drawingDimensions.made
            check(len(dims) == 5, "5 dimensions (the pitch across and up, width, height, depth), got %d" % len(dims))
            keys = {(tuple(sorted([(round(a.coordinate.x, 3), round(a.coordinate.y, 3)), (round(b.coordinate.x, 3), round(b.coordinate.y, 3))])),
                     "x" if abs(p.coordinate.y - (a.coordinate.y + b.coordinate.y) / 2) >= abs(p.coordinate.x - (a.coordinate.x + b.coordinate.x) / 2) else "y")
                    for a, b, p in dims}
            check(len(keys) == len(dims), "(4) no dimension placed twice (same two points, same direction)")
            check(all(a.owner == "circle" and b.owner == "circle" for a, b, _p in dims[:2]) and
                  all(a.owner == "line" and b.owner == "line" for a, b, _p in dims[2:]),
                  "the pitch joins circle centres; the overall sizes join view line vertices")
            check(not any(inside((p.coordinate.x, p.coordinate.y), b, 1.0) for _a, _b, p in dims for b in boxes),
                  "no dimension placed on a view")
            p236 = abs(dims[0][1].coordinate.x - dims[0][0].coordinate.x) / md.SCALE
            p238 = abs(dims[1][1].coordinate.y - dims[1][0].coordinate.y) / md.SCALE
            w = abs(dims[2][1].coordinate.x - dims[2][0].coordinate.x) / md.SCALE
            hgt = abs(dims[3][1].coordinate.y - dims[3][0].coordinate.y) / md.SCALE
            dep = abs(dims[4][1].coordinate.y - dims[4][0].coordinate.y) / md.SCALE
            check((round(p236, 3), round(p238, 3)) == (236.0, 240.0), "the H05-H08 pitch measures 236 x 240 (%g x %g)" % (p236, p238))
            check((round(w, 3), round(hgt, 3), round(dep, 3)) == (Fake.W, Fake.H, Fake.D),
                  "dimensions measure the part's %g x %g x %g (%g, %g, %g)" % (Fake.W, Fake.H, Fake.D, w, hgt, dep))
            check(dims[0][2].coordinate.y < dims[2][2].coordinate.y and f[3] < dims[0][2].coordinate.y,
                  "above the FRONT the pitch 236 sits inside the width, so their lines don't cross")
            syms = sheet.drawingSymbols.made
            check([s.identifier for s in syms] == ["A", "B", "C"], "datums A, B, C")
            # Fusion's datum box: about 7.2 mm, beyond the placement point, away from its edge (measured on the
            # 2026-11-01 sheet: A's box from its point down, C's up, B's to the left). Each box keeps 1.5 mm from every
            # view, every dimension line and every other box (that run had A's box on the top view's edge).
            boxes7 = []
            for sy in syms:
                (x1, y1), (x2, y2) = [(q.coordinate.x, q.coordinate.y) for q in (sy.viewCurve.startPoint, sy.viewCurve.endPoint)]
                px, py = sy.placementPoint.coordinate.x, sy.placementPoint.coordinate.y
                if abs(y1 - y2) < 1e-6:                       # a horizontal edge: the box above or below the point
                    boxes7.append((px - 3.6, py - 7.2, px + 3.6, py) if py < y1 else (px - 3.6, py, px + 3.6, py + 7.2))
                else:                                         # a vertical edge: the box left or right of the point
                    boxes7.append((px - 7.2, py - 3.6, px, py + 3.6) if px < x1 else (px, py - 3.6, px + 7.2, py + 3.6))
            dim_lines = []
            for da, db, dp in dims:
                ax, ay, bx, by = da.coordinate.x, da.coordinate.y, db.coordinate.x, db.coordinate.y
                px, py = dp.coordinate.x, dp.coordinate.y
                if abs(py - (ay + by) / 2) >= abs(px - (ax + bx) / 2):
                    dim_lines.append((min(ax, bx), py - 0.01, max(ax, bx), py + 0.01))
                else:
                    dim_lines.append((px - 0.01, min(ay, by), px + 0.01, max(ay, by)))
            crowded = [(sy.identifier, what) for sy, bx_ in zip(syms, boxes7)
                       for what, other in ([("view %d" % i, vb) for i, vb in enumerate(boxes)] +
                                           [("dimension %d" % i, dl) for i, dl in enumerate(dim_lines)] +
                                           [("datum %s" % o.identifier, ob) for o, ob in zip(syms, boxes7) if o is not sy])
                       if overlap(bx_, other, 1.5)]
            check(not crowded, "datum boxes 1.5 mm clear of views, dimension lines and each other %s" % crowded)
            b_box = boxes7[1]
            check(b_box[0] - rt[2] >= 10.0, "datum B's box %.1f mm clear of the side view (P3: was 3)" % (b_box[0] - rt[2]))
            check(not any(inside((s.placementPoint.coordinate.x, s.placementPoint.coordinate.y), b, 1.0)
                          for s in syms for b in boxes), "no datum placed on a view")
            check(sheet.holeTables.count == 0, "no Fusion hole table (relieved corners; the hole table is in the PDF)")
            pts = sheet.sketches.points
            check(pts and all(inside(p, FRAME) and not inside(p, TITLE) for p in pts) and
                  not any(inside(p, b) for p in pts for b in boxes), "projection symbol inside the frame, clear of views")
            sks = sheet.sketches.made
            outline = [k for k in sks if k.chains]
            circles = [k for k in sks if k.circles_made]
            check(len(sks) == 2 and len(outline) == 1 and len(circles) == 1 and outline[0] is not circles[0] and
                  len(outline[0].chains) == 1 and len(outline[0].chains[0]) == 5 and
                  outline[0].chains[0][0] == outline[0].chains[0][-1] and not outline[0].circles_made and
                  len(circles[0].circles_made) == 2 and not circles[0].chains,
                  "(2) symbol: the outline one closed chain alone in its sketch, the 2 circles in another")
            check(os.path.exists(raw) and os.path.exists(raw_views), "raw PDF and the views' outlines written to .raw/")
            vj = json.load(open(raw_views))
            check(sorted(vj["views"]) == ["d", "front", "iso", "left", "right", "top"] and vj["scale"] == md.SCALE,
                  "the views file names every view and the scale")
            # the finished PDF
            bt_mod = load("body_drawing_text")
            out = os.path.join(tmp, md.DWG + ".pdf")
            bt_mod.finish_pdf(raw, out)
            import fitz
            page = fitz.open(out)[0]
            text = page.get_text()
            check(not any(part in text for part in FAKE_NAME.split()), "no account name left in the finished PDF")
            meta = fitz.open(out).metadata
            check(meta["author"] == "Autonomous" and meta["creator"] == "Autonomous", "PDF author and creator Autonomous")
            sys.path.insert(0, os.path.join(REPO, "tools", "checks"))
            import c_drawings
            check(c_drawings.drawing_people(out, [FAKE_NAME]) == ([], []),
                  "the drawing check reads Autonomous in Created by, the author, no maker line and no name")
            check(bt_mod.required_missing(text) == [], "finished PDF states units, material, finish, tolerance, hole tags")
            check("Made by" not in text and "make_body_drawing" not in text and "SOURCE: the 711001 P01 STEP" in text,
                  "no maker line; the notes name their source")
            check(text.count("D (turned 180°)") == 1 and "View D: the bottom, seen in the direction of arrow D" in text,
                  "view D marked 'D (turned 180°)', with its note")
            segs, _circles, texts = bt_mod.geometry(page)
            outside = [t[4] for t in texts if not overlap(t[:4], TEXT)]
            check(outside.count("(236)") == 1 and outside.count("(240)") == 1 and "236" not in outside and
                  "240" not in outside, "the pitch is printed once each as (236) and (240), for reference")
            tags = [t for t in texts if re.fullmatch(r"H0[1-9]", t[4]) and not overlap(t[:4], TEXT)]
            check(sorted(t[4] for t in tags) == ["H%02d" % i for i in range(1, 10)], "a tag H01-H09 beside each hole on the views")
            crossing = [t[4] for t in tags if any(bt_mod._seg_hits_box(s, t[:4]) for s in segs)]
            check(not crossing, "no tag crosses a line %s" % crossing)
            heads = [t[4] for t in texts if overlap(t[:4], TEXT)]
            check(all(h in heads for h in ("TAG", "FACE", "FROM B", "FROM A", "FROM C", "Ø THRU", "NOTE")) and
                  all(("H%02d" % i) in heads for i in range(1, 10)), "the hole table: its heading row and a row per hole")
            check(os.path.getsize(out) < 300_000, "fonts subset: the PDF is %.0f kB (was 15.3 MB)" % (os.path.getsize(out) / 1e3))
            sp = [(s["text"], s["size"] / PT, s["bbox"]) for blk in page.get_text("dict")["blocks"]
                  for ln in blk.get("lines", []) for s in ln["spans"] if s["text"].strip()]
            block = [(t, sz, bb) for t, sz, bb in sp if inside((bb[0] / PT, 420.0 - bb[3] / PT), TEXT, 1.0)]
            caps = [sz * bt_mod.CAP for _t, sz, _bb in block]
            check(min(caps or [0]) >= 2.5 - 1e-6, "(1) every text-block line at least 2.5 mm capital height (smallest %.2f)"
                  % min(caps or [0]))
            check(sum(1 for c in caps if c >= 3.5 - 1e-6) == 3, "(1) the 3 headings 3.5 mm capital height")
            check(all(TEXT[0] - 0.5 <= bb[0] / PT and bb[2] / PT <= TEXT[2] + 0.5 and
                      TEXT[1] - 0.5 <= 420.0 - bb[3] / PT and 420.0 - bb[1] / PT <= TEXT[3] + 0.5 for _t, _s, bb in block),
                  "the text block and the hole table stay inside their space")
            # a raw PDF whose view D isn't turned (H04 55 from its left, 18 from its bottom) stops the finish step
            ex = vj["views"]["d"]["extent"]
            fz = fitz.open(raw)
            pg = fz[0]
            pg.add_redact_annot(fitz.Rect((ex[0] - 2) * PT, (420 - ex[3] - 2) * PT, (ex[2] + 2) * PT, (420 - ex[1] + 2) * PT))
            pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED)
            pg.draw_circle(fitz.Point((ex[0] + 55 * md.SCALE) * PT, (420 - (ex[1] + 18 * md.SCALE)) * PT), 11.1 * md.SCALE * PT,
                           oc=[x for x, o in fz.get_ocgs().items() if o["name"] == "Visible"][0])
            turned_raw = os.path.join(tmp, "turned.pdf")
            fz.save(turned_raw)
            try:
                bt_mod.finish_pdf(turned_raw, os.path.join(tmp, "turned-out.pdf"), raw_views)
                stopped = ""
            except SystemExit as e:
                stopped = str(e)
            check("d view" in stopped and not os.path.exists(os.path.join(tmp, "turned-out.pdf")),
                  "a view D that isn't turned in the raw PDF stops the finish step")
            check(bt_mod.centre_mark_problems([(100.0, 100.0, 2.0)], []) != [], "a hole without a centre mark is reported")
            for p in (raw, raw_views):
                os.remove(p)
            # a drawing that doesn't reference the body stops before any view
            try:
                md.annotate(app_with(Sheet(), md.DWG, Doc(md.DWG + " v1", body="SOMETHING_ELSE_CAD")))
                wrong_ref = False
            except RuntimeError as e:
                wrong_ref = "doesn't reference" in str(e)
            check(wrong_ref, "a drawing that doesn't reference the body's design stops before any view")
            # a FRONT that isn't the room side stops the run before any dimension
            Fake.wrong_front = True
            sheet2 = Sheet()
            try:
                md.annotate(app_with(sheet2, md.DWG))
                stopped = False
            except RuntimeError as e:
                stopped = "not as expected" in str(e)
            Fake.wrong_front = False
            check(stopped and sheet2.drawingDimensions.count == 0 and sheet2.holeTables.count == 0,
                  "a wrong-size FRONT view stops the run before dimensions and tables")
    finally:
        for n in (os.listdir(raw_dir) if os.path.isdir(raw_dir) else []):
            if os.path.join(raw_dir, n) not in kept:
                os.remove(os.path.join(raw_dir, n))
        for path, data in kept.items():
            open(path, "wb").write(data)
        if os.path.isdir(raw_dir) and not existed and not os.listdir(raw_dir):
            os.rmdir(raw_dir)
    print("\n%d checks failed" % len(failures) if failures else "\nall checks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
