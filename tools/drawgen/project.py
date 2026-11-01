"""Exact hidden-line projection (OCC HLRBRep_Algo, the exact algorithm, never the polygonal one).

A view is a viewing direction and two in-plane axes, named and mapped to the pod (or part) system as in
conventions section 4. `project` returns 2D primitives in the view's own X/Y (mm, true size): lines, circular
arcs with their true centre and radius, and Bezier pieces for any other curve (exact for B-splines up to
degree 3). Visible and hidden edges come apart, so the sheet draws hidden ones dashed.
"""

import math

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_BSplineCurve, GeomAbs_BezierCurve, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Line
from OCP.GeomConvert import GeomConvert_BSplineCurveToBezierCurve
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from geom import vcross, vdot, vmul, vnorm, axis_name

# The six standard views of the pod system (conventions section 4): toward-viewer direction, X(view), Y(view).
POD_VIEWS = {
    "front": ((0, -1, 0), (1, 0, 0), (0, 0, 1)),     # looking toward +Y
    "top": ((0, 0, 1), (1, 0, 0), (0, 1, 0)),        # looking down
    "left": ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),     # from the left (looking toward +X)
    "right": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),      # from the right (looking toward -X)
    "rear": ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),      # looking toward -Y
    "bottom": ((0, 0, -1), (1, 0, 0), (0, -1, 0)),   # looking up
}

LOOK_WORDS = {"+X": "toward +X", "-X": "toward -X", "+Y": "toward +Y", "-Y": "toward -Y", "+Z": "up (toward +Z)",
              "-Z": "down (toward -Z)"}


class View:
    """A named orthographic view. n: unit vector toward the viewer; x, y: the view's X and Y in 3D."""

    def __init__(self, name, n, x, y=None, title=None, section=None):
        self.name = name
        self.n = vnorm(n)
        self.x = vnorm(x)
        self.y = vnorm(y) if y else vcross(self.n, self.x)
        if vdot(vcross(self.n, self.x), self.y) < 0.999:
            raise ValueError("view %s is not right-handed" % name)
        self.title = title or name.upper()
        self.section = section          # (point, normal) of the cutting plane for a section view
        self.label = None

    def to2d(self, p):
        return (vdot(p, self.x), vdot(p, self.y))

    def depth(self, p):
        """Distance toward the viewer."""
        return vdot(p, self.n)

    @property
    def looking(self):
        return axis_name(vmul(self.n, -1.0))

    def mapping(self, system="pod"):
        """'X(view) = +Y, Y(view) = +Z, looking toward -X' in words, for the sheet (guideline 3.3)."""
        return "X = %s, Y = %s (%s %s), looking %s" % (
            axis_name(self.x) or "%.3f,%.3f,%.3f" % self.x, axis_name(self.y) or "%.3f,%.3f,%.3f" % self.y,
            system, "axes", LOOK_WORDS.get(self.looking, self.looking or "obliquely"))


def related(principal, which):
    """First-angle views around a principal view: the view from above sits below it, from below above it,
    from its left on its right, from its right on its left, and the rear view beside the left one."""
    n0, x0, y0 = principal.n, principal.x, principal.y
    if which == "above":
        return View("above", y0, x0, vmul(n0, -1.0))
    if which == "below":
        return View("below", vmul(y0, -1.0), x0, n0)
    if which == "from_left":
        return View("from_left", vmul(x0, -1.0), n0, y0)
    if which == "from_right":
        return View("from_right", x0, vmul(n0, -1.0), y0)
    if which == "rear":
        return View("rear", vmul(n0, -1.0), vmul(x0, -1.0), y0)
    raise KeyError(which)


class Prim:
    """A 2D primitive in view mm. kind: 'line' (p, q), 'arc' (c, r, a0, a1 radians, counter-clockwise from a0
    to a1; a full circle has a1 - a0 = 2 pi), 'bezier' (list of cubic control points p0, c1, c2, p1)."""

    __slots__ = ("kind", "vis", "p", "q", "c", "r", "a0", "a1", "pts", "src")

    def __init__(self, kind, vis, **kw):
        self.kind = kind
        self.vis = vis
        self.p = kw.get("p")
        self.q = kw.get("q")
        self.c = kw.get("c")
        self.r = kw.get("r")
        self.a0 = kw.get("a0")
        self.a1 = kw.get("a1")
        self.pts = kw.get("pts")
        self.src = kw.get("src", "")

    def bbox(self):
        if self.kind == "line":
            xs, ys = (self.p[0], self.q[0]), (self.p[1], self.q[1])
        elif self.kind == "arc":
            # the arc's end points and any quadrant point it passes
            angs = [self.a0, self.a1]
            k = math.ceil(self.a0 / (math.pi / 2))
            while k * math.pi / 2 < self.a1:
                angs.append(k * math.pi / 2)
                k += 1
            xs = [self.c[0] + self.r * math.cos(a) for a in angs]
            ys = [self.c[1] + self.r * math.sin(a) for a in angs]
        else:
            xs = [p[0] for p in self.pts]
            ys = [p[1] for p in self.pts]
        return min(xs), min(ys), max(xs), max(ys)

    def moved(self, dx, dy):
        k = dict(p=self.p, q=self.q, c=self.c, r=self.r, a0=self.a0, a1=self.a1, pts=self.pts, src=self.src)
        if self.p:
            k["p"] = (self.p[0] + dx, self.p[1] + dy)
            k["q"] = (self.q[0] + dx, self.q[1] + dy)
        if self.c:
            k["c"] = (self.c[0] + dx, self.c[1] + dy)
        if self.pts:
            k["pts"] = [(x + dx, y + dy) for x, y in self.pts]
        return Prim(self.kind, self.vis, **k)


def _edges(comp):
    if comp is None or comp.IsNull():
        return
    e = TopExp_Explorer(comp, TopAbs_EDGE)
    while e.More():
        yield TopoDS.Edge_s(e.Current())
        e.Next()


def _xy(p):
    return (p.X(), p.Y())


def _collinear(pts, tol=1e-6):
    p, q = pts[0], pts[-1]
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return False
    return all(abs((x - p[0]) * dy - (y - p[1]) * dx) / L < tol for x, y in pts)


def _arc_from_curve(a, vis, src):
    circ = a.Circle()
    c = _xy(circ.Location())
    r = circ.Radius()
    f, l = a.FirstParameter(), a.LastParameter()
    p0, pm, p1 = _xy(a.Value(f)), _xy(a.Value(0.5 * (f + l))), _xy(a.Value(l))
    ang = lambda p: math.atan2(p[1] - c[1], p[0] - c[0])
    a0, am, a1 = ang(p0), ang(pm), ang(p1)
    full = abs(l - f) > 2 * math.pi - 1e-9
    if full:
        return Prim("arc", vis, c=c, r=r, a0=0.0, a1=2 * math.pi, src=src)
    # counter-clockwise from a0 to a1 passing am?
    def ccw_span(s, e):
        d = (e - s) % (2 * math.pi)
        return d
    if ccw_span(a0, am) <= ccw_span(a0, a1):
        s, e = a0, a0 + ccw_span(a0, a1)
    else:
        s, e = a1, a1 + ccw_span(a1, a0)
    return Prim("arc", vis, c=c, r=r, a0=s, a1=e, src=src)


def _bezier_pieces(a, vis, src):
    """Exact cubic Bezier pieces of a B-spline or Bezier edge of degree <= 3; finer cubic fits otherwise."""
    out = []
    t = a.GetType()
    if t == GeomAbs_BSplineCurve:
        bs = a.BSpline()
        conv = GeomConvert_BSplineCurveToBezierCurve(bs, a.FirstParameter(), a.LastParameter(), 1e-9)
        arcs = [conv.Arc(i) for i in range(1, conv.NbArcs() + 1)]
    elif t == GeomAbs_BezierCurve:
        arcs = [a.Bezier()]
    else:
        arcs = []
    if arcs and all(b.Degree() <= 3 for b in arcs):
        for b in arcs:
            poles = [_xy(b.Pole(i)) for i in range(1, b.NbPoles() + 1)]
            if b.Degree() == 1:
                p, q = poles
                poles = [p, (p[0] + (q[0] - p[0]) / 3, p[1] + (q[1] - p[1]) / 3),
                         (p[0] + 2 * (q[0] - p[0]) / 3, p[1] + 2 * (q[1] - p[1]) / 3), q]
            elif b.Degree() == 2:
                p, m, q = poles
                poles = [p, (p[0] + 2 / 3 * (m[0] - p[0]), p[1] + 2 / 3 * (m[1] - p[1])),
                         (q[0] + 2 / 3 * (m[0] - q[0]), q[1] + 2 / 3 * (m[1] - q[1])), q]
            out.append(poles)
    else:
        # cubic Hermite pieces through points and tangents of the exact curve (ellipses, high-degree splines)
        f, l = a.FirstParameter(), a.LastParameter()
        n = 16
        from OCP.gp import gp_Pnt as _P, gp_Vec as _V
        prev = None
        for i in range(n + 1):
            u = f + (l - f) * i / n
            p, v = _P(), _V()
            a.D1(u, p, v)
            cur = (_xy(p), (v.X() * (l - f) / n / 3, v.Y() * (l - f) / n / 3))
            if prev:
                (p0, d0), (p1, d1) = prev, cur
                out.append([p0, (p0[0] + d0[0], p0[1] + d0[1]), (p1[0] - d1[0], p1[1] - d1[1]), p1])
            prev = cur
    if out and all(_collinear(seg) for seg in out) and _collinear([out[0][0], out[-1][-1]] + [s[-1] for s in out]):
        return [Prim("line", vis, p=out[0][0], q=out[-1][-1], src=src)]
    pts = [out[0][0]]
    for seg in out:
        pts.extend(seg[1:])
    return [Prim("bezier", vis, pts=pts, src=src)]


def edge_prims(edge, vis, src=""):
    a = BRepAdaptor_Curve(edge)
    t = a.GetType()
    if t == GeomAbs_Line:
        p, q = _xy(a.Value(a.FirstParameter())), _xy(a.Value(a.LastParameter()))
        if math.dist(p, q) < 1e-6:
            return []
        return [Prim("line", vis, p=p, q=q, src=src)]
    if t == GeomAbs_Circle:
        return [_arc_from_curve(a, vis, src)]
    return _bezier_pieces(a, vis, src)


def project(shape, view):
    """Visible and hidden 2D primitives of shape in view (HLRBRep_Algo: exact, edges stay curves)."""
    algo = HLRBRep_Algo()
    algo.Add(shape)
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*view.n), gp_Dir(*view.x))
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    prims = []
    for comp, vis, src in ((h.VCompound(), True, "sharp"), (h.OutLineVCompound(), True, "outline"),
                           (h.Rg1LineVCompound(), True, "smooth"), (h.HCompound(), False, "sharp"),
                           (h.OutLineHCompound(), False, "outline")):
        for e in _edges(comp):
            prims.extend(edge_prims(e, vis, src))
    return clean(prims)


def _seg_on_seg(h, v, tol):
    """True when hidden line h runs parallel to visible line v and lies within tol of it over its whole length."""
    (x1, y1), (x2, y2) = v.p, v.q
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return False
    hx, hy = h.q[0] - h.p[0], h.q[1] - h.p[1]
    hl = math.hypot(hx, hy)
    if hl < 1e-9 or abs(hx * dy - hy * dx) / (hl * math.sqrt(L2)) > 0.0175:     # 1 degree
        return False
    for px, py in (h.p, h.q):
        t = ((px - x1) * dx + (py - y1) * dy) / L2
        if t < -1e-6 or t > 1 + 1e-6:
            return False
        if abs((px - x1) * dy - (py - y1) * dx) / math.sqrt(L2) > tol:
            return False
    return True


def clean(prims, tol=1e-4):
    """Drop duplicate primitives and hidden lines lying on visible ones (they would print as one line)."""
    out, seen = [], set()
    for p in prims:
        if p.kind == "line":
            a, b = sorted([tuple(round(v, 4) for v in p.p), tuple(round(v, 4) for v in p.q)])
            key = ("l", a, b, p.vis)
        elif p.kind == "arc":
            key = ("a", round(p.c[0], 4), round(p.c[1], 4), round(p.r, 4), round(p.a0 % (2 * math.pi), 4),
                   round(p.a1 - p.a0, 4), p.vis)
        else:
            key = ("b", tuple(tuple(round(v, 4) for v in q) for q in p.pts), p.vis)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    vis_lines = [p for p in out if p.vis and p.kind == "line"]
    vis_arcs = [p for p in out if p.vis and p.kind == "arc"]
    res = []
    for p in out:
        if not p.vis and p.kind == "line" and any(_seg_on_seg(p, v, tol) for v in vis_lines):
            continue
        if not p.vis and p.kind == "arc" and any(
                math.dist(p.c, v.c) < tol and abs(p.r - v.r) < tol and v.a1 - v.a0 > 2 * math.pi - 1e-6
                for v in vis_arcs):
            continue        # the far end of a hole behind its visible near end
        res.append(p)
    return res


def _covered(h, others, gap):
    """True when the parallel lines in `others` lying within gap of hidden line h cover its whole length
    (their union, so a visible edge split at vertices still counts)."""
    hx, hy = h.q[0] - h.p[0], h.q[1] - h.p[1]
    L = math.hypot(hx, hy)
    if L < 1e-9:
        return True
    ux, uy = hx / L, hy / L
    iv = []
    for o in others:
        if o is h or o.kind != "line":
            continue
        ox, oy = o.q[0] - o.p[0], o.q[1] - o.p[1]
        lo = math.hypot(ox, oy)
        if lo < 1e-9 or abs(ox * uy - oy * ux) / lo > 0.0175:
            continue
        # distance of o's line from h's line
        if abs((o.p[0] - h.p[0]) * uy - (o.p[1] - h.p[1]) * ux) > gap:
            continue
        t1 = (o.p[0] - h.p[0]) * ux + (o.p[1] - h.p[1]) * uy
        t2 = (o.q[0] - h.p[0]) * ux + (o.q[1] - h.p[1]) * uy
        iv.append((min(t1, t2), max(t1, t2)))
    iv.sort()
    # a hidden line may run past the visible one by up to gap at either end (a wall's inner face meeting an end
    # cut at an angle): on paper that is the same line
    reach = gap
    for a, b in iv:
        if a > reach + 1e-6:
            break
        reach = max(reach, b)
        if reach >= L - gap - 1e-6:
            return True
    return reach >= L - gap - 1e-6


def drop_hidden_near(prims, min_gap):
    """Hidden lines closer than min_gap (mm, true size) to parallel visible lines over their length: on paper they
    print on top of them (a tube's inner wall behind its outer wall), so ISO practice leaves them out."""
    vis = [p for p in prims if p.vis and p.kind == "line"]
    return [p for p in prims if p.vis or p.kind != "line" or not _covered(p, vis, min_gap)]


def merge_close_hidden(prims, gap):
    """Of hidden lines closer than gap to parallel hidden lines that cover them, keep one: on paper they print as
    one line."""
    out, kept = [], []
    for p in prims:
        if not p.vis and p.kind == "line":
            if kept and _covered(p, kept, gap):
                continue
            kept.append(p)
        out.append(p)
    return out


def extent(prims):
    bb = [p.bbox() for p in prims]
    if not bb:
        return (0, 0, 0, 0)
    return (min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb))
