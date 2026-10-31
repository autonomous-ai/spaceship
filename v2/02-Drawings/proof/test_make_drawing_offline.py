#!/usr/bin/env python3
"""Offline test of make_drawing.py: no Fusion needed.

    python3 v2/02-Drawings/proof/test_make_drawing_offline.py

It fakes the few adsk.drawing objects the script uses, lays out the three
views at 1:5 the way Fusion should (front view from inside: X right, Z up;
view from above: X right, Y up; view from the right: Y right, Z up), runs the
annotation step and checks that every dimension and hole table lands on the
intended points. It tests the script's geometry logic only; Fusion's own
view conventions are checked on the real sheet.
"""

import importlib.util
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
S = 0.2           # sheet mm per model mm at 1:5 (this Fusion build uses mm on sheets)


# ------------------------------------------------------------- fake adsk

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


ViewCurveTypes = Enum("LineViewCurveType", "ArcViewCurveType", "CircleViewCurveType")
ViewOrientationTypes = Enum("FrontViewOrientationType", "BackViewOrientationType",
                            "TopViewOrientationType", "BottomViewOrientationType",
                            "RightViewOrientationType", "LeftViewOrientationType")
DrawingViewStyleTypes = Enum("VisibleEdgesDrawingViewStyleType")


class Curve:
    def __init__(self, kind, a=None, b=None, c=None):
        self.type = kind
        self.startPoint = DrawingPoint(*a, owner="line") if a else None
        self.endPoint = DrawingPoint(*b, owner="line") if b else None
        self.centerPoint = DrawingPoint(*c, owner="circle") if c else None


class Curves:
    def __init__(self, items):
        self.items = items
        self.count = len(items)

    def item(self, i):
        return self.items[i]


class View:
    def __init__(self, orientation, curves):
        self.orientation = orientation
        self.type = 0
        self.scaleValue = 0.2
        self.viewCurves = Curves(curves)


def line(p, q):
    return Curve(ViewCurveTypes.LineViewCurveType, a=p, b=q)


def circle(c):
    return Curve(ViewCurveTypes.CircleViewCurveType, c=c)


def front_view(x0, y0):
    m = lambda X, Z: (x0 + X * S, y0 + Z * S)
    c = [line(m(0, 0), m(0, 1150)), line(m(20, 0), m(20, 1150)), line(m(0, 0), m(1500, 0)),
         line(m(0, 1150), m(1500, 1150)), line(m(1450, 0), m(1450, 1150)),
         line(m(1470, 0), m(1470, 1150)), line(m(1500, 0), m(1500, 1150))]
    for z in (20, 565, 585, 1130):
        c.append(line(m(20, z), m(1450, z)))
    return View(ViewOrientationTypes.FrontViewOrientationType, c)


def top_view(x0, ytop):
    m = lambda X, Y: (x0 + X * S, ytop - (3 - Y) * S)
    c = [line(m(0, 3), m(1500, 3)), line(m(0, 0), m(1500, 0)), line(m(0, -20), m(1470, -20)),
         line(m(0, -20), m(0, 3)), line(m(1470, -20), m(1470, 0)), line(m(1500, 0), m(1500, 3))]
    for X in (60, 510, 960, 1410):
        c.append(circle(m(X, -10)))
        c.append(circle(m(X, -10)))   # the coaxial hole in the bottom wall
    return View(ViewOrientationTypes.TopViewOrientationType, c)


def right_view(xright, y0):
    m = lambda Y, Z: (xright - (3 - Y) * S, y0 + Z * S)
    c = [line(m(3, 0), m(3, 1150)), line(m(0, 0), m(0, 1150)), line(m(-20, 0), m(-20, 1150)),
         line(m(-20, 0), m(3, 0)), line(m(-20, 1150), m(3, 1150))]
    for Z in (60, 403.333, 746.667, 1090):
        c.append(circle(m(-10, Z)))
        c.append(circle(m(-10, Z)))   # the coaxial hole in the far wall
    return View(ViewOrientationTypes.RightViewOrientationType, c)


class Dims:
    def __init__(self):
        self.made = []
        self.count = 0

    def addLinearDimension(self, a, b, place, aligned):
        self.made.append((a, b, place, aligned))
        self.count += 1
        return object()


class HoleTables:
    def __init__(self):
        self.made = []
        self.count = 0

    def createInput(self):
        return types.SimpleNamespace(view=None, originPoint=None, title="")

    def add(self, inp):
        self.made.append(inp)
        self.count += 1
        return object()


class Views:
    def __init__(self, views):
        self.views = views
        self.count = len(views)

    def item(self, i):
        return self.views[i]


class Sheet:
    def __init__(self, views):
        self.name = "Sheet1"
        self.width, self.height = 59.4, 42.0
        self.views = Views(views)
        self.drawingDimensions = Dims()
        self.holeTables = HoleTables()
        self.customTables = types.SimpleNamespace(count=0)
        self.titleBlock = None


def load_script():
    adsk = types.ModuleType("adsk")
    core = types.ModuleType("adsk.core")
    core.Point2D = Point2D
    drawing = types.ModuleType("adsk.drawing")
    drawing.DrawingPoint = DrawingPoint
    drawing.ViewCurveTypes = ViewCurveTypes
    drawing.ViewOrientationTypes = ViewOrientationTypes
    drawing.DrawingViewStyleTypes = DrawingViewStyleTypes
    fusion = types.ModuleType("adsk.fusion")
    adsk.core, adsk.drawing, adsk.fusion = core, drawing, fusion
    sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.drawing": drawing,
                        "adsk.fusion": fusion})
    spec = importlib.util.spec_from_file_location("make_drawing", os.path.join(HERE, "make_drawing.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------- the test

def near(p, q, tol=1e-6):
    return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol


def main():
    md = load_script()
    fx0, fy0 = 180.0, 140.0               # front view origin O on the sheet, mm
    gb, gl = md.cm(md.GAP_BELOW), md.cm(md.GAP_LEFT)
    front = front_view(fx0, fy0)
    top = top_view(fx0, fy0 - gb)         # below, X aligned
    right = right_view(fx0 - gl, fy0)     # left, Z aligned
    sheet = Sheet([front, top, right])
    failures = []

    def check(cond, what):
        print(("ok   " if cond else "FAIL ") + what)
        if not cond:
            failures.append(what)

    md.annotate_front(sheet, front)
    o_top = md.annotate_top(sheet, top)
    o_right = md.annotate_right(sheet, right)
    md.hole_table(sheet, top, o_top, "T1")
    md.hole_table(sheet, right, o_right, "T2")

    dims = sheet.drawingDimensions.made
    check(len(dims) == 4 + 5 + 5, "14 dimensions (4 front, 5 above, 5 right), got %d" % len(dims))
    # front: 1470 = O to (1470, 0)
    a, b = dims[0][0].coordinate, dims[0][1].coordinate
    check(near((a.x, a.y), (fx0, fy0)) and near((b.x, b.y), (fx0 + 1470 * S, fy0)),
          "front: overall width runs from datum corner O to X = 1470")
    # above: each hole dim starts on (X=0, Y=0) and ends on a hole centre
    tx0, ty0 = fx0, (fy0 - gb) - 3 * S
    for i, X in enumerate((60, 510, 960, 1410)):
        a, b = dims[4 + i][0], dims[4 + i][1]
        check(near(md.xy(a), (tx0, ty0)) and b.owner == "circle" and
              near(md.xy(b), (tx0 + X * S, ty0 - 10 * S)),
              "above: H%02d centre at X = %d from datum C (start on C x A, end on hole centre)" % (i + 1, X))
    # right: each hole dim starts on (Y=0, Z=0) and ends on a hole centre
    rx0 = (fx0 - gl) - 3 * S
    for i, Z in enumerate((60, 403.333, 746.667, 1090)):
        a, b = dims[9 + i][0], dims[9 + i][1]
        check(near(md.xy(a), (rx0, fy0)) and b.owner == "circle" and
              near(md.xy(b), (rx0 - 10 * S, fy0 + Z * S)),
              "right: H%02d centre at Z = %g from datum B" % (9 + i, Z))
    # every start point of a dimension is a real view vertex, not a free point
    check(all(d[0].owner in ("line", "circle") for d in dims), "all dimensions start on view geometry")
    check(all(d[1].owner in ("line", "circle") for d in dims), "all dimensions end on view geometry")
    t = sheet.holeTables.made
    check(len(t) == 2 and t[0].view is top and t[1].view is right, "2 hole tables on the right views")
    check(near(md.xy(t[0].originPoint), (tx0, ty0)), "hole table 1 origin on datum corner C x A")
    check(near(md.xy(t[1].originPoint), (rx0, fy0)), "hole table 2 origin on datum corner A x B")
    # dimension lines sit outside every view's geometry and clear of the other views
    boxes = [md.extent(v) for v in (front, top, right)]

    def inside(p, b, pad=1.0):
        return b[0] - pad < p.x < b[2] + pad and b[1] - pad < p.y < b[3] + pad
    clash = [d for d in dims if any(inside(d[2].coordinate, b) for b in boxes)]
    check(not clash, "no dimension placed inside a view (%d inside)" % len(clash))
    check(all(d[2].coordinate.x < boxes[2][0] for d in dims[9:13]),
          "right-view hole dimensions sit on the far side, away from the front view")
    check(all(boxes[1][3] < d[2].coordinate.y < boxes[0][1] for d in dims[4:8]),
          "above-view hole dimensions sit between that view and the front view")
    print("\n%d checks failed" % len(failures) if failures else "\nall checks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
