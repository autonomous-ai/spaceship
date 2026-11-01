#!/usr/bin/env python3
"""Offline test of drawing 711001's scripts (make_body_drawing.py and body_drawing_text.py): no Fusion.

    python3 v2/02-Drawings/electrical/test_body_drawing_offline.py

It fakes the adsk.drawing objects the script uses. Each faked view has the size Fusion should give it
(at the route model's size: FRONT w x h at 1:2, TOP and BOTTOM w x d, the side views d x h) at the centre the script asks
for. The test runs the whole annotate step, then checks:
- every view, dimension, datum and the symbol sits inside the A2 frame, clear of the title block, the text
  block and the other views; dimensions start and end on real vertices of the views' edge lines, though the
  folded body's corner reliefs leave no vertex at a view's corner; no Fusion hole table;
- a view of the wrong size (a FRONT that isn't the room side) stops the run before any dimension;
- the finished PDF (the faked export, then body_drawing_text.py) has no account name and states units,
  material, finish, a tolerance and every hole H01-H08, read with the drawing check's rules;
- the PM's four drawing traps (2026-11-01, CEILING's first sample), with the shared helpers
  (tools/fusion/fusion_drawing.py): (1) every line of the PDF text block is at least 2.5 mm capital height
  (headings 3.5) and stays inside its block; (2) the first-angle symbol's outline is one closed chain alone in
  its sketch, its circles in another; (3) every view, the iso too, ends with visible edges only, though the
  faked Fusion hands each view back with hidden lines, as the real one does; (4) no dimension twice.
  Centre marks and lines go on the 5 orthographic views' holes after every dimension.
It tests the script's logic; Fusion's own view conventions are checked on the real sheet.
"""

import importlib.util
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
TEXT = (410.0, 62.0, 584.0, 240.0)
FAKE_NAME = "Jordan Quill"          # stands in for the account holder's name Fusion prints


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
LOG = []                            # the order things are made in: "dim", "centre"


class Curve:
    def __init__(self, kind, a=None, b=None, c=None):
        self.type = kind
        self.startPoint = DrawingPoint(*a, owner="line") if a else None
        self.endPoint = DrawingPoint(*b, owner="line") if b else None
        self.centerPoint = DrawingPoint(*c, owner="circle") if c else None


class Curves:
    def __init__(self, items):
        self.items, self.count = items, len(items)

    def item(self, i):
        return self.items[i]


class View:
    """Fusion hands a new view back with hidden lines whatever style the input asked for (CEILING's sample)."""
    def __init__(self, orientation, scale, curves):
        self.orientation, self.scaleValue, self.viewCurves = orientation, scale, Curves(curves)
        self.style = STYLE.VisibleAndHiddenEdgesDrawingViewStyleType
        self._marks = types.SimpleNamespace(isAppliedToHoles=False)
        self._lines = types.SimpleNamespace(isAppliedToHoles=False)

    def getCenterMarkOptions(self):
        return types.SimpleNamespace(isAppliedToHoles=self._marks.isAppliedToHoles)

    def getCenterLineOptions(self):
        return types.SimpleNamespace(isAppliedToHoles=self._lines.isAppliedToHoles)

    def setCenterMarkOptions(self, o):
        LOG.append("centre")
        self._marks = types.SimpleNamespace(isAppliedToHoles=o.isAppliedToHoles)
        return True

    def setCenterLineOptions(self, o):
        self._lines = types.SimpleNamespace(isAppliedToHoles=o.isAppliedToHoles)
        return True


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
    """The part as Fusion should show it, at the model's size: sizes per orientation (sheet mm at the view's scale)."""
    W, H, D = model_size()
    LIP = 22.0
    wrong_front = False

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
            for dx, dy in ((30, 11), (cls.W - 30, 11), (30, cls.H - 11), (cls.W - 30, cls.H - 11)):
                cv.append(Curve(VCT.CircleViewCurveType, c=(c[0] - w / 2 + dx * s, c[1] - h / 2 + dy * s)))
        return View(o, s, cv)


class BaseViewInput:
    def __init__(self):
        opts = types.SimpleNamespace(isAppliedToHoles=False)
        self.viewParameters = types.SimpleNamespace(orientation=None, scaleValue=1.0, style=None,
                                                    centerMarkOptions=opts, centerLineOptions=opts)
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


def fake_pdf(path):
    """An A2 page with the stock title block's "Created by" field, as Fusion exports it."""
    import fitz
    doc = fitz.open()
    pt = 72.0 / 25.4
    page = doc.new_page(width=594 * pt, height=420 * pt)
    page.draw_rect(fitz.Rect(20 * pt, 10 * pt, 584 * pt, 410 * pt))
    page.insert_text(fitz.Point(495 * pt, (420 - 52) * pt), "Created by", fontsize=6)
    page.insert_text(fitz.Point(495 * pt, (420 - 47) * pt), FAKE_NAME, fontsize=8)
    page.insert_text(fitz.Point(545 * pt, (420 - 47) * pt), "01/11/26", fontsize=8)
    doc.save(path)


class ExportManager:
    def createPDFExportOptions(self, path):
        return types.SimpleNamespace(path=path, openPDF=True, useLineWeights=False)

    def execute(self, opts):
        fake_pdf(opts.path)
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


def app_with(sheet, dwg_name):
    dwg = types.SimpleNamespace(activeSheet=sheet, exportManager=ExportManager())
    return types.SimpleNamespace(activeProduct=dwg, activeDocument=types.SimpleNamespace(name=dwg_name + " v1"))


# ------------------------------------------------------------------ the test

def box_of(view):
    xs = [c.startPoint.coordinate.x for c in view.viewCurves.items if c.startPoint] + \
         [c.endPoint.coordinate.x for c in view.viewCurves.items if c.endPoint]
    ys = [c.startPoint.coordinate.y for c in view.viewCurves.items if c.startPoint] + \
         [c.endPoint.coordinate.y for c in view.viewCurves.items if c.endPoint]
    return min(xs), min(ys), max(xs), max(ys)


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

    with tempfile.TemporaryDirectory() as tmp:
        md = load("make_body_drawing")
        md.ARGS.update({"repo_root": REPO})
        raw_dir = os.path.join(REPO, md.HERE, ".raw")
        sheet = Sheet()
        del LOG[:]
        md.annotate(app_with(sheet, md.DWG))
        views = sheet.views.items
        boxes = [box_of(v) for v in views]
        check(len(views) == 6, "6 views (front, top, bottom, left, right, iso), got %d" % len(views))
        check(all(inside((b[0], b[1]), FRAME) and inside((b[2], b[3]), FRAME) for b in boxes),
              "every view inside the A2 frame")
        check(not any(overlap(b, TITLE) for b in boxes), "no view on the title block")
        check(not any(overlap(b, TEXT) for b in boxes), "no view on the text block")
        pairs = [(i, j) for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if overlap(boxes[i], boxes[j], 5.0)]
        check(not pairs, "views at least 5 mm apart (%s)" % pairs)
        f, t, bt, lf, rt = boxes[:5]
        check(abs(t[3] - (f[1] - md.GAP)) < 1e-6 and abs(bt[1] - (f[3] + md.GAP)) < 1e-6,
              "first angle: TOP one gap below the FRONT, BOTTOM one gap above it")
        check(abs(lf[0] - (f[2] + md.GAP)) < 1e-6 and abs(rt[2] - (f[0] - md.GAP)) < 1e-6,
              "first angle: view from the LEFT on the right, from the RIGHT on the left")
        check(all(v.style == STYLE.VisibleEdgesDrawingViewStyleType for v in views),
              "(3) every view, the iso too, visible edges only (handed back with hidden lines, as Fusion does)")
        check(all(v.getCenterMarkOptions().isAppliedToHoles and v.getCenterLineOptions().isAppliedToHoles
                  for v in views[:5]) and not views[5].getCenterMarkOptions().isAppliedToHoles,
              "centre marks and lines on the 5 orthographic views' holes, none on the iso")
        check("centre" in LOG and "dim" in LOG and max(i for i, e in enumerate(LOG) if e == "dim") <
              min(i for i, e in enumerate(LOG) if e == "centre"), "centre marks set after every dimension")
        dims = sheet.drawingDimensions.made
        check(len(dims) == 3, "3 dimensions (width, height, depth), got %d" % len(dims))
        keys = {(tuple(sorted([(round(a.coordinate.x, 3), round(a.coordinate.y, 3)), (round(b.coordinate.x, 3), round(b.coordinate.y, 3))])),
                 "x" if abs(p.coordinate.y - (a.coordinate.y + b.coordinate.y) / 2) >= abs(p.coordinate.x - (a.coordinate.x + b.coordinate.x) / 2) else "y")
                for a, b, p in dims}
        check(len(keys) == len(dims), "(4) no dimension placed twice (same two points, same direction)")
        check(all(a.owner == "line" and b.owner == "line" for a, b, _p in dims), "dimensions start and end on view line vertices")
        check(not any(inside((p.coordinate.x, p.coordinate.y), b, 1.0) for _a, _b, p in dims for b in boxes),
              "no dimension placed on a view")
        w = abs(dims[0][1].coordinate.x - dims[0][0].coordinate.x) / md.SCALE
        hgt = abs(dims[1][1].coordinate.y - dims[1][0].coordinate.y) / md.SCALE
        dep = abs(dims[2][1].coordinate.y - dims[2][0].coordinate.y) / md.SCALE
        check((round(w, 3), round(hgt, 3), round(dep, 3)) == (Fake.W, Fake.H, Fake.D),
              "dimensions measure the part's %g x %g x %g (%g, %g, %g)" % (Fake.W, Fake.H, Fake.D, w, hgt, dep))
        syms = sheet.drawingSymbols.made
        check([s.identifier for s in syms] == ["A", "B", "C"], "datums A, B, C")
        check(not any(inside((s.placementPoint.coordinate.x, s.placementPoint.coordinate.y), b, 1.0)
                      for s in syms for b in boxes), "no datum placed on a view")
        check(sheet.holeTables.count == 0, "no Fusion hole table (relieved corners; the hole list is in the PDF)")
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
        raw = os.path.join(raw_dir, md.DWG + ".pdf")
        check(os.path.exists(raw), "raw PDF exported to .raw/")
        # the finished PDF
        bt_mod = load("body_drawing_text")
        out = os.path.join(tmp, md.DWG + ".pdf")
        bt_mod.finish_pdf(raw, out)
        import fitz
        text = "\n".join(p.get_text() for p in fitz.open(out))
        check(not any(part in text for part in FAKE_NAME.split()), "no account name left in the finished PDF")
        check(bt_mod.required_missing(text) == [], "finished PDF states units, material, finish, tolerance, hole tags")
        check(all("H%02d" % i in text for i in range(1, 9)) and len(re.findall(r"[Ø⌀]\s*\d", text)) >= 8,
              "all 8 holes H01-H08 with their diameters")
        pt = 72.0 / 25.4
        page = fitz.open(out)[0]
        spans = [(sp["text"], sp["size"] / pt, sp["bbox"]) for blk in page.get_text("dict")["blocks"]
                 for ln in blk.get("lines", []) for sp in ln["spans"] if sp["text"].strip()]
        block = [(t, sz, bb) for t, sz, bb in spans if inside((bb[0] / pt, 420.0 - bb[3] / pt), TEXT, 1.0)]
        caps = [sz * bt_mod.CAP for _t, sz, _bb in block]
        want = [r for r in bt_mod.wrap(bt_mod.lines(), bt_mod.BLOCK[2] - bt_mod.BLOCK[0] - 4.0,
                                       fitz.Font(fontfile=bt_mod.FONT)) if r[0].strip()]
        check(len(block) == len(want) and min(caps or [0]) >= 2.5 - 1e-6,
              "(1) every text-block line at least 2.5 mm capital height (%d of %d lines, smallest %.2f mm)" % (
                  len(block), len(want), min(caps or [0])))
        check(sum(1 for c in caps if c >= 3.5 - 1e-6) == 3, "(1) the 3 headings 3.5 mm capital height")
        check(all(TEXT[0] - 0.5 <= bb[0] / pt and bb[2] / pt <= TEXT[2] + 0.5 and
                  TEXT[1] - 0.5 <= 420.0 - bb[3] / pt and 420.0 - bb[1] / pt <= TEXT[3] + 0.5 for _t, _s, bb in block),
              "the text block stays inside its space")
        os.remove(raw)
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
        if os.path.isdir(raw_dir) and not os.listdir(raw_dir):
            os.rmdir(raw_dir)
    print("\n%d checks failed" % len(failures) if failures else "\nall checks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
