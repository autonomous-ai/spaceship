"""A flat pattern's DXF, read without OCC (the read-back uses it too): lines, arcs, circles, polylines (their bulges
as arcs) and splines, each with its layer, and the layers' roles (cut outline, bend centre lines, bend zone edges)."""

import math


class Dxf:
    """The entities of a flat pattern DXF that drawgen draws and checks: lines, arcs, circles, polylines (bulges as
    arcs) and splines, each with its layer."""

    def __init__(self, path):
        self.path = path
        self.units = None
        self.lines, self.arcs, self.circles, self.splines = [], [], [], []
        self._read(path)

    def _read(self, path):
        with open(path, errors="replace") as fh:
            raw = [ln.rstrip("\r\n") for ln in fh]
        pairs = [(raw[i].strip(), raw[i + 1].strip()) for i in range(0, len(raw) - 1, 2)]
        for i, (c, v) in enumerate(pairs):
            if c == "9" and v == "$INSUNITS" and i + 1 < len(pairs):
                self.units = int(pairs[i + 1][1])
        ents, cur, sec = [], None, None
        for c, v in pairs:
            if c == "2" and v in ("ENTITIES", "BLOCKS", "TABLES", "HEADER", "OBJECTS", "CLASSES"):
                sec = v
            if sec != "ENTITIES":
                continue
            if c == "0":
                if cur is not None:
                    ents.append(cur)
                cur = (v, []) if v != "ENDSEC" else None
            elif cur is not None:
                cur[1].append((c, v))
        poly = None
        for typ, codes in ents:
            d = {}
            for c, v in codes:
                d.setdefault(c, []).append(v)
            lay = (d.get("8") or ["0"])[0]
            f = lambda c, j=0: float(d[c][j])
            if typ == "LINE":
                self.lines.append((lay, (f("10"), f("20")), (f("11"), f("21"))))
            elif typ == "CIRCLE":
                self.circles.append((lay, (f("10"), f("20")), f("40")))
            elif typ == "ARC":
                self.arcs.append((lay, (f("10"), f("20")), f("40"), f("50"), f("51")))
            elif typ == "LWPOLYLINE":
                xs, ys = d.get("10", []), d.get("20", [])
                bul = []
                # bulges follow their vertex: walk the codes in order
                vb, cur_b = [], None
                for c, v in codes:
                    if c == "10":
                        vb.append([float(v), None, 0.0])
                    elif c == "20" and vb:
                        vb[-1][1] = float(v)
                    elif c == "42" and vb:
                        vb[-1][2] = float(v)
                closed = int((d.get("70") or ["0"])[0]) & 1
                self._poly(lay, [(x, y, b_) for x, y, b_ in vb], closed)
            elif typ == "POLYLINE":
                poly = (lay, [], int((d.get("70") or ["0"])[0]) & 1)
            elif typ == "VERTEX" and poly is not None:
                poly[1].append((f("10"), f("20"), float((d.get("42") or ["0"])[0])))
            elif typ == "SEQEND" and poly is not None:
                self._poly(*poly)
                poly = None
            elif typ == "SPLINE":
                deg = int((d.get("71") or ["3"])[0])
                knots = [float(x) for x in d.get("40", [])]
                ctrl = [(float(x), float(y)) for x, y in zip(d.get("10", []), d.get("20", []))]
                self.splines.append((lay, deg, knots, ctrl))

    def _poly(self, lay, verts, closed):
        n = len(verts)
        for i in range(n if closed else n - 1):
            x0, y0, bul = verts[i]
            x1, y1, _b = verts[(i + 1) % n]
            if abs(bul) < 1e-12:
                self.lines.append((lay, (x0, y0), (x1, y1)))
                continue
            # a bulge: an arc of included angle 4 atan(bulge), counter-clockwise when positive
            th = 4 * math.atan(bul)
            ch = math.hypot(x1 - x0, y1 - y0)
            rad = ch / (2 * math.sin(abs(th) / 2))
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            h = math.sqrt(max(rad * rad - (ch / 2) ** 2, 0.0)) * (1 if abs(th) < math.pi else -1)
            nx, ny = -(y1 - y0) / ch, (x1 - x0) / ch
            sgn = 1 if bul > 0 else -1
            cx, cy = mx + sgn * h * nx, my + sgn * h * ny
            a0 = math.degrees(math.atan2(y0 - cy, x0 - cx))
            a1 = math.degrees(math.atan2(y1 - cy, x1 - cx))
            if bul < 0:
                a0, a1 = a1, a0
            self.arcs.append((lay, (cx, cy), rad, a0, a1))

    LAYER_ROLE = {"CUT": "cut", "OUTER_PROFILES": "cut", "INTERIOR_PROFILES": "cut", "BEND": "bend",
                  "MARK": "zone", "BEND_EXTENT": "zone"}

    def role(self, layer):
        return self.LAYER_ROLE.get(layer.upper(), "other")

    def bend_lines(self):
        return [(a, b) for lay, a, b in self.lines if self.role(lay) == "bend"]

    def zone_lines(self):
        return [(a, b) for lay, a, b in self.lines if self.role(lay) == "zone"]

    def cut_box(self):
        """The CUT outline's box (x0, y0, x1, y1): lines, arcs (their extremes), circles and spline control points."""
        xs, ys = [], []
        for lay, a, b in self.lines:
            if self.role(lay) == "cut":
                xs += [a[0], b[0]]
                ys += [a[1], b[1]]
        for lay, c, r, a0, a1 in self.arcs:
            if self.role(lay) != "cut":
                continue
            for k in range(0, 361, 5):
                ang = math.radians(k)
                if _in_arc(k, a0, a1):
                    xs.append(c[0] + r * math.cos(ang))
                    ys.append(c[1] + r * math.sin(ang))
            for ang in (a0, a1):
                xs.append(c[0] + r * math.cos(math.radians(ang)))
                ys.append(c[1] + r * math.sin(math.radians(ang)))
        for lay, deg, kn, ctrl in self.splines:
            if self.role(lay) == "cut":
                xs += [p[0] for p in ctrl]
                ys += [p[1] for p in ctrl]
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None

    def _cut_prims(self):
        """The cut geometry (outline and holes) as primitives: ("L", a, b), ("A", c, r, a0, a1), ("C", c, r); a
        spline as short lines along its Bezier pieces, or ("?", degree) when it isn't a clamped cubic."""
        prims = []
        for lay, a, b in self.lines:
            if self.role(lay) == "cut":
                prims.append(("L", a, b))
        for lay, c, r, a0, a1 in self.arcs:
            if self.role(lay) == "cut":
                prims.append(("A", c, r, a0, a1))
        for lay, c, r in self.circles:
            if self.role(lay) == "cut":
                prims.append(("C", c, r))
        for lay, deg, kn, ctrl in self.splines:
            if self.role(lay) != "cut":
                continue
            segs = spline_beziers(deg, kn, ctrl)
            if segs is None:
                prims.append(("?", deg))
                continue
            for seg in segs:
                pts = [_bezier(seg, i / 32.0) for i in range(33)]
                prims += [("L", pts[i], pts[i + 1]) for i in range(32)]
        return prims

    def cut_loops(self, tol=0.01):
        """How many separate shapes the cut lines, arcs and splines make, round holes (circles) aside: 1 for a flat
        that is one outline; each cut-out that isn't a round hole adds one."""
        ends = []
        for lay, a, b in self.lines:
            if self.role(lay) == "cut":
                ends.append((a, b))
        for lay, c, r, a0, a1 in self.arcs:
            if self.role(lay) == "cut":
                ends.append(tuple((c[0] + r * math.cos(math.radians(t)), c[1] + r * math.sin(math.radians(t)))
                                  for t in (a0, a1)))
        for lay, deg, kn, ctrl in self.splines:
            if self.role(lay) == "cut" and ctrl:
                ends.append((ctrl[0], ctrl[-1]))       # a clamped spline starts and ends on its end control points
        parent = list(range(len(ends)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        cells = {}
        cs = 10 * tol
        for i, pair in enumerate(ends):
            for p in pair:
                cx, cy = int(math.floor(p[0] / cs)), int(math.floor(p[1] / cs))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for j, q in cells.get((cx + dx, cy + dy), ()):
                            if math.hypot(p[0] - q[0], p[1] - q[1]) <= tol:
                                parent[root(i)] = root(j)
                cells.setdefault((cx, cy), []).append((i, p))
        return len({root(i) for i in range(len(ends))})

    def off_symmetry(self, T, tol=0.05, step=1.0):
        """None when the cut geometry (outline and holes), the bend lines and the bend zone lines all map onto
        themselves under the plane map T = (M, c), x' = M x + c; else the first place that doesn't, in words."""
        M, c = T

        def f(p):
            return (M[0][0] * p[0] + M[0][1] * p[1] + c[0], M[1][0] * p[0] + M[1][1] * p[1] + c[1])
        prims = self._cut_prims()
        if any(p[0] == "?" for p in prims):
            return "a spline drawgen can't read"
        grid = _Grid(prims, tol)
        for pr in prims:
            for p in _samples(pr, step):
                q = f(p)
                if grid.dist(q) > tol:
                    return "the outline at (%.2f, %.2f) has no twin at (%.2f, %.2f)" % (p + q)
        for role in ("bend", "zone"):
            ls = [(a, b) for lay, a, b in self.lines if self.role(lay) == role]
            for a, b in ls:
                ta, tb = f(a), f(b)
                if not any((_d(ta, a2) <= tol and _d(tb, b2) <= tol) or (_d(ta, b2) <= tol and _d(tb, a2) <= tol)
                           for a2, b2 in ls):
                    return "the %s line (%.2f, %.2f) to (%.2f, %.2f) has no twin" % (
                        "bend" if role == "bend" else "bend zone", a[0], a[1], b[0], b[1])
        return None


def _d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _bezier(seg, t):
    p0, c1, c2, p1 = seg
    u = 1.0 - t
    return tuple(u * u * u * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t * t * t * p1[i] for i in range(2))


def _arc_span(a0, a1):
    s = (a1 - a0) % 360.0
    return s if s > 1e-9 else 360.0


def _samples(pr, step):
    """Points along a primitive, about step apart, its ends included."""
    if pr[0] == "L":
        a, b = pr[1], pr[2]
        n = max(1, int(math.ceil(_d(a, b) / step)))
        return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
    if pr[0] == "A":
        c, r, a0, a1 = pr[1], pr[2], pr[3], pr[4]
        span = _arc_span(a0, a1)
        n = max(2, int(math.ceil(r * math.radians(span) / step)))
        return [(c[0] + r * math.cos(math.radians(a0 + span * i / n)), c[1] + r * math.sin(math.radians(a0 + span * i / n)))
                for i in range(n + 1)]
    c, r = pr[1], pr[2]
    n = max(8, int(math.ceil(2 * math.pi * r / step)))
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _prim_dist(pr, p):
    if pr[0] == "L":
        a, b = pr[1], pr[2]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
    if pr[0] == "A":
        c, r, a0, a1 = pr[1], pr[2], pr[3], pr[4]
        ang = math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))
        if _in_arc(ang, a0, a1):
            return abs(math.hypot(p[0] - c[0], p[1] - c[1]) - r)
        return min(_d(p, (c[0] + r * math.cos(math.radians(t)), c[1] + r * math.sin(math.radians(t)))) for t in (a0, a1))
    c, r = pr[1], pr[2]
    return abs(math.hypot(p[0] - c[0], p[1] - c[1]) - r)


class _Grid:
    """Primitives bucketed by 10 mm cells, for the distance from a point to the nearest one."""

    def __init__(self, prims, tol, cell=10.0):
        self.cell, self.cells = cell, {}
        for pr in prims:
            if pr[0] == "L":
                xs, ys = (pr[1][0], pr[2][0]), (pr[1][1], pr[2][1])
            else:
                xs, ys = (pr[1][0] - pr[2], pr[1][0] + pr[2]), (pr[1][1] - pr[2], pr[1][1] + pr[2])
            for i in range(int(math.floor((min(xs) - tol) / cell)), int(math.floor((max(xs) + tol) / cell)) + 1):
                for j in range(int(math.floor((min(ys) - tol) / cell)), int(math.floor((max(ys) + tol) / cell)) + 1):
                    self.cells.setdefault((i, j), []).append(pr)

    def dist(self, p):
        prs = self.cells.get((int(math.floor(p[0] / self.cell)), int(math.floor(p[1] / self.cell))), ())
        return min((_prim_dist(pr, p) for pr in prs), default=float("inf"))


def _in_arc(k, a0, a1):
    a0, a1, k = a0 % 360, a1 % 360, k % 360
    return (a0 <= k <= a1) if a0 <= a1 else (k >= a0 or k <= a1)


def spline_beziers(deg, knots, ctrl):
    """A clamped cubic B-spline as cubic Bezier segments [(p0, c1, c2, p1)] (knot insertion until every inner knot
    is threefold); None for any other degree."""
    if deg != 3 or len(knots) != len(ctrl) + 4:
        return None
    kn, P = list(knots), [tuple(p) for p in ctrl]

    def insert(kn, P, u):
        k = max(i for i in range(len(kn) - 1) if kn[i] <= u < kn[i + 1]) if u < kn[-1] else len(kn) - 5
        Q = []
        for i in range(len(P) + 1):
            if i <= k - 3:
                Q.append(P[i])
            elif i > k:
                Q.append(P[i - 1])
            else:
                den = kn[i + 3] - kn[i]
                a = (u - kn[i]) / den if den else 0.0
                Q.append(tuple((1 - a) * P[i - 1][j] + a * P[i][j] for j in range(2)))
        return kn[:k + 1] + [u] + kn[k + 1:], Q
    inner = sorted(set(kn[4:-4]))
    for u in inner:
        while kn.count(u) < 3:
            kn, P = insert(kn, P, u)
    segs = []
    for s in range(0, len(P) - 1, 3):
        if s + 3 < len(P):
            segs.append((P[s], P[s + 1], P[s + 2], P[s + 3]))
    return segs
