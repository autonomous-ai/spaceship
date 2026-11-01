"""Bent and folded sheet (the Lead's ruling, 2026-11-01: bent parts come from the generator, Fusion the fallback).

The fold chain comes from the part's own STEP: a section square to the bend lines through the part's middle is
the sheet's outline, two skins joined by an end cap at each free end; its corners are the folds. The flat pattern
comes from the team's DXF (its CUT outline, BEND centre lines and MARK bend-zone edges). The two are matched bend
for bend: the flat positions the model's flanges give with the inside radius and a K-factor must land on the DXF's
bend lines, and the K-factor is solved from the DXF's flat size. The read-back repeats that check, so a DXF that
doesn't fit its model fails the drawing.

Lengths are mm. A flange's length is measured outside (to the virtual sharp of the outside of each fold), as a
brake shop sets its back gauge. For a fold of angle a (degrees, 90 for a right-angle bend), inside radius r,
thickness t and K-factor K: the outside setback OSSB = (r + t) tan(a/2), the bend allowance BA = a_rad (r + K t)."""

import math

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
from OCP.TopAbs import TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

import geom
from dxf import Dxf, spline_beziers  # noqa: F401 (the reader and its splines are shared with the read-back)
from geom import vadd, vcross, vdot, vmul, vnorm, vsub


class Fold:
    """One fold of a chain: its angle (degrees, the change of direction), the inside radius when the model has one,
    and on which skin its inside (concave side) lies."""

    def __init__(self, i, angle, r, inside, outer_pt, inner_pt):
        self.i = i
        self.angle = angle
        self.r = r                  # the model's inside radius; None where the model folds sharp
        self.inside = inside        # "A" or "B": the skin on the fold's concave side
        self.outer_pt = outer_pt    # 2D, the virtual sharp of the outside
        self.inner_pt = inner_pt
        self.flat = None            # its centre line's place in the flat, from the chain's start


class Chain:
    """The folds met across one bend direction: the bend lines run along `axis`; the section's 2D frame is (u, v)."""

    def __init__(self, axis, u, v, t, start, flanges, folds, skins, holes_2d=None):
        self.axis = axis
        self.u, self.v = u, v
        self.t = t
        self.start = start          # 2D, the chain's first free end (the middle of its end cap)
        self.flanges = flanges      # [(length outside, direction 2D)], from the start
        self.folds = folds
        self.skins = skins          # {"A": [2D points], "B": [...]} the two skins from the start end


def _section_loops(b, n, frac=0.5):
    """The outline loops of the body's section by the plane square to n at frac of its extent: [[(kind, p2, r)]]."""
    import compose
    pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(b.shape)]
    s = [vdot(p, n) for p in pts]
    pt = vadd(b.centroid, vmul(n, min(s) + frac * (max(s) - min(s)) - vdot(b.centroid, n)))
    faces = compose.cut_faces(geom.half_space_keep(b.shape, pt, n), pt, n)
    u = vnorm(vcross(n, (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)))
    v = vcross(n, u)
    loops = []
    for f in faces:
        e = TopExp_Explorer(f, TopAbs_WIRE)
        while e.More():
            ex = BRepTools_WireExplorer(TopoDS.Wire_s(e.Current()))
            loop = []
            while ex.More():
                c = BRepAdaptor_Curve(ex.Current())
                p = geom.pnt(BRep_Tool.Pnt_s(ex.CurrentVertex()))
                kind = {GeomAbs_Line: "L", GeomAbs_Circle: "C"}.get(c.GetType(), "?")
                loop.append((kind, (vdot(p, u), vdot(p, v)), c.Circle().Radius() if kind == "C" else None))
                ex.Next()
            loops.append(loop)
            e.Next()
    return loops, u, v, pt


def _d2(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _line_x(p1, d1, p2, d2):
    """Where the lines p1 + s d1 and p2 + s d2 meet (None when parallel)."""
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-12:
        return None
    s = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return (p1[0] + s * d1[0], p1[1] + s * d1[1])


def chain_of(b, axis):
    """The fold chain across bend lines along `axis`, or None when the section there isn't one thin open strip
    (one loop: two skins joined by two end caps of the thickness) with at least one fold."""
    loops, u, v, _pt = _section_loops(b, axis)
    if len(loops) != 1:
        return None
    loop = loops[0]
    n = len(loop)
    if any(k == "?" for k, _p, _r in loop):
        return None
    pts = [p for _k, p, _r in loop]
    edges = [(loop[i][0], pts[i], pts[(i + 1) % n], loop[i][2]) for i in range(n)]
    lines = [e for e in edges if e[0] == "L"]
    # the thickness: the shortest line edge whose two neighbours run square to it (the end caps)
    caps = []
    for i, (k, a, c, _r) in enumerate(edges):
        if k != "L":
            continue
        d = vnorm2(c[0] - a[0], c[1] - a[1])
        prv, nxt = edges[i - 1], edges[(i + 1) % n]
        if prv[0] != "L" or nxt[0] != "L":
            continue
        dp = vnorm2(prv[2][0] - prv[1][0], prv[2][1] - prv[1][1])
        dn = vnorm2(nxt[2][0] - nxt[1][0], nxt[2][1] - nxt[1][1])
        if abs(dp[0] * d[0] + dp[1] * d[1]) < 1e-6 and abs(dn[0] * d[0] + dn[1] * d[1]) < 1e-6 and \
                dp[0] * dn[0] + dp[1] * dn[1] < -0.999999:
            caps.append((_d2(a, c), i))
    if len(caps) < 2:
        return None
    caps.sort()
    t = caps[0][0]
    ends = [i for L, i in caps if abs(L - t) < 1e-3]
    if len(ends) != 2 or t > 6.0:
        return None
    i0, i1 = sorted(ends)
    # the two skins between the caps: A from cap i0's end to cap i1's start, B the rest (reversed to run the same way)
    skin_a = [edges[j] for j in range(i0 + 1, i1)]
    skin_b = [edges[j] for j in list(range(i1 + 1, n)) + list(range(0, i0))]
    skin_b = [(k, c, a, r) for k, a, c, r in reversed(skin_b)]
    if not skin_a or not skin_b:
        return None
    # flanges: the straight runs of each skin (a fold is a sharp corner or an arc between two runs)
    runs = {}
    for name, skin in (("A", skin_a), ("B", skin_b)):
        rr = []
        for k, a, c, r in skin:
            if k == "L":
                rr.append((a, c))
        runs[name] = rr
    if len(runs["A"]) != len(runs["B"]) or len(runs["A"]) < 2:
        return None
    nf = len(runs["A"]) - 1
    folds = []
    start = ((skin_a[0][1][0] + skin_b[0][1][0]) / 2, (skin_a[0][1][1] + skin_b[0][1][1]) / 2)
    for i in range(nf):
        out = {}
        for name in ("A", "B"):
            (a1, c1), (a2, c2) = runs[name][i], runs[name][i + 1]
            d1 = vnorm2(c1[0] - a1[0], c1[1] - a1[1])
            d2 = vnorm2(c2[0] - a2[0], c2[1] - a2[1])
            out[name] = (_line_x(a1, d1, a2, d2), d1, d2)
        (xa, d1, d2), (xb, _e1, _e2) = out["A"], out["B"]
        if xa is None or xb is None:
            return None
        ang = math.degrees(math.acos(max(-1.0, min(1.0, d1[0] * d2[0] + d1[1] * d2[1]))))
        turn = d1[0] * d2[1] - d1[1] * d2[0]            # > 0: turns left, going along the chain
        # skin A lies on the left of the chain or the right: the fold's inside is the skin on the turn's side
        a_left = _side(start, runs, d1, i)
        inside = ("A" if a_left else "B") if turn > 0 else ("B" if a_left else "A")
        outer, inner = (xb, xa) if inside == "A" else (xa, xb)
        arcs = [r for (k, a, c, r) in (skin_a if inside == "A" else skin_b) if k == "C"]
        r_in = None
        if arcs:
            # the inside arc of this fold: the arc on the inside skin nearest its virtual sharp
            best = None
            for k, a, c, r in (skin_a if inside == "A" else skin_b):
                if k == "C":
                    dd = min(_d2(a, inner), _d2(c, inner))
                    if best is None or dd < best[0]:
                        best = (dd, r)
            r_in = best[1] if best else None
        folds.append(Fold(i, ang, r_in, inside, outer, inner))
    # outside lengths: from the start's end cap to the first fold's outside sharp, between outside sharps, to the end
    end = ((skin_a[-1][2][0] + skin_b[-1][2][0]) / 2, (skin_a[-1][2][1] + skin_b[-1][2][1]) / 2)
    flanges = []
    marks = [start] + [f.outer_pt for f in folds] + [end]
    for i in range(nf + 1):
        a1, c1 = runs["A"][i]
        d = vnorm2(c1[0] - a1[0], c1[1] - a1[1])
        L = abs((marks[i + 1][0] - marks[i][0]) * d[0] + (marks[i + 1][1] - marks[i][1]) * d[1])
        flanges.append((L, d))
    skins = {"A": [skin_a[0][1]] + [c for _k, _a, c, _r in skin_a], "B": [skin_b[0][1]] + [c for _k, _a, c, _r in skin_b]}
    ch = Chain(axis, u, v, t, start, flanges, folds, skins)
    ch.runs = runs              # each skin's straight runs, one per flange
    return ch


def vnorm2(x, y):
    L = math.hypot(x, y) or 1.0
    return (x / L, y / L)


def _side(start, runs, d1, i):
    """True when skin A lies on the left of the chain's direction along flange i."""
    (a1, c1), (b1, e1) = runs["A"][i], runs["B"][i]
    mid_a = ((a1[0] + c1[0]) / 2, (a1[1] + c1[1]) / 2)
    mid_b = ((b1[0] + e1[0]) / 2, (b1[1] + e1[1]) / 2)
    off = (mid_a[0] - mid_b[0], mid_a[1] - mid_b[1])
    return d1[0] * off[1] - d1[1] * off[0] > 0


def flat_positions(chain, r, k):
    """The chain's flat: each fold's centre line from the start and the total length, with inside radius r (the
    model's where it has one) and K-factor k."""
    pos, x = [], 0.0
    folds = chain.folds
    for i, (L, _d) in enumerate(chain.flanges):
        straight = L
        if i > 0:
            straight -= ossb(folds[i - 1], r, chain.t)
        if i < len(folds):
            straight -= ossb(folds[i], r, chain.t)
        x += straight
        if i < len(folds):
            ba = bend_allowance(folds[i], r, chain.t, k)
            pos.append(x + ba / 2)
            x += ba
    return pos, x


def radius(fold, r):
    return fold.r if fold.r is not None else r


def ossb(fold, r, t):
    return (radius(fold, r) + t) * math.tan(math.radians(fold.angle) / 2)


def bend_allowance(fold, r, t, k):
    return math.radians(fold.angle) * (radius(fold, r) + k * t)


def solve_k(chain, r, flat_total):
    """The K-factor that makes the chain's flat as long as flat_total (linear in K)."""
    _p0, l0 = flat_positions(chain, r, 0.0)
    _p1, l1 = flat_positions(chain, r, 1.0)
    return (flat_total - l0) / (l1 - l0) if abs(l1 - l0) > 1e-12 else None


def match_chain(chain, dxf, r, tol=0.05):
    """The chain's folds against the DXF's bend lines: the group of bend lines square to one DXF axis, as many as
    the chain's folds, whose places along that axis the model's flat gives at one K-factor (between 0 and 1), the
    chain run forward or reversed. Every reading that fits, best first (a symmetric chain fits both ways; which one
    is right is the holes' and the outline's to say, in analyse): [{"dxf_axis": 0 or 1 (x or y: the lines' places),
    "reversed", "k", "lines": [DXF line per fold], "worst": mm}]."""
    box = dxf.cut_box()
    if box is None:
        return []
    out = []
    for ax in (0, 1):
        group = [(a, b) for a, b in dxf.bend_lines() if abs(a[ax] - b[ax]) < 1e-6]
        if len(group) != len(chain.folds):
            continue
        group.sort(key=lambda l: l[0][ax])
        lo, hi = box[ax], box[2 + ax]
        k = solve_k(chain, r, hi - lo)
        if k is None or not 0.0 <= k <= 1.0:
            continue
        pos, total = flat_positions(chain, r, k)
        for rev in (False, True):
            got = [(hi - l[0][ax]) if rev else (l[0][ax] - lo) for l in group]
            if rev:
                got = got[::-1]
                lines = group[::-1]
            else:
                lines = group
            worst = max(abs(p - g) for p, g in zip(pos, got))
            if worst <= tol:
                out.append({"dxf_axis": ax, "reversed": rev, "k": k, "lines": lines, "worst": worst, "positions": pos})
    # best first; readings within 0.0001 of each other keep a fixed order (x before y, forward before reversed)
    out.sort(key=lambda m: (round(m["worst"], 4), m["dxf_axis"], m["reversed"]))
    return out


# ------------------------------------------------------------------ the whole part

class Flat:
    """A bent part read and matched: its chains, the DXF, the K-factor and inside radius, which skin the DXF shows,
    and the bend table's rows (in the DXF's own coordinates)."""

    def __init__(self):
        self.chains, self.matches, self.rows, self.notes = [], [], [], []
        self.k = None
        self.radius = None
        self.radius_from = None
        self.dxf = None
        self.viewed = None


def bend_axes(body):
    """Where bend lines can run: the body's box axes and every cylinder's axis (a radiused bend's)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder
    axes = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    for f in geom._faces(body.shape):
        if BRepAdaptor_Surface(f, True).GetType() == GeomAbs_Cylinder:
            d = geom._cyl_info(f)["dir"]
            if not any(abs(abs(vdot(d, a)) - 1) < 1e-6 for a in axes):
                axes.append(d)
    return axes


def unexplained_faces(body, chains, holes, slots):
    """Curved faces of a bent part that are neither a hole nor a slot, nor a fold's inside or outside cylinder (its
    axis along the chain's bend lines, its radius the fold's inside radius or that plus the thickness), nor the small
    cut end of a bend zone where the outline meets it (a corner relief's spline, no wider than twice r + t)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
    out = []
    radii = []
    for ch in chains:
        for f in ch.folds:
            if f.r is not None:
                radii.append((ch.axis, f.r, ch.t))
    span = max([r + t for _a, r, t in radii] or [0.0])
    for f in geom._faces(body.shape):
        s = BRepAdaptor_Surface(f, True)
        typ = s.GetType()
        if typ == GeomAbs_Plane:
            continue
        if typ == GeomAbs_Cylinder:
            info = geom._cyl_info(f)
            if info["concave"] and (any(abs(h.dia / 2 - info["r"]) < 1e-3 for h in holes) or
                                    any(abs(sl.width / 2 - info["r"]) < 1e-3 for sl in slots)):
                continue
            if any(abs(abs(vdot(info["dir"], a)) - 1) < 1e-6 and (abs(info["r"] - r) < 1e-3 or abs(info["r"] - r - t) < 1e-3)
                   for a, r, t in radii):
                continue
            out.append("a cylinder r%.2f" % info["r"])
            continue
        pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(f)]
        if pts and span and all(max(p[k] for p in pts) - min(p[k] for p in pts) <= 2 * span + 0.1 for k in range(3)):
            continue
        out.append("a surface of type %d" % int(typ))
    return out


def _skin_normal(ch, i):
    """Skin A's outward direction on flange i (3D): from skin B's run across the sheet to skin A's."""
    (a0, a1), (b0, b1) = ch.runs["A"][i], ch.runs["B"][i]
    ma = ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2)
    mb = ((b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2)
    d = ch.flanges[i][1]
    off = (ma[0] - mb[0], ma[1] - mb[1])
    across = off[0] * -d[1] + off[1] * d[0]            # the offset square to the flange: + on its left
    n2 = (-d[1], d[0]) if across > 0 else (d[1], -d[0])
    return vadd(vmul(ch.u, n2[0]), vmul(ch.v, n2[1]))


class FlatMap:
    """One reading of the flat: which DXF axis each chain's bend places run along and which way, and (one chain)
    which way the DXF runs along its bend lines. where(P) gives a point of the sheet its place in the DXF: across a
    chain's bends from the flange it lies on (that flange's straight part, clear of the bend zones); along them from
    the other chain's base flange (two chains, square to each other: the flange both share), or from the part's own
    extent along the bend lines (one chain: folding doesn't change it)."""

    def __init__(self, body, chains, matches, sense, box, k):
        self.chains, self.matches, self.sense, self.box, self.k = chains, matches, sense, box, k
        self.fl = []
        for ch, m in zip(chains, matches):
            r = m["r"]
            pos, _total = flat_positions(ch, r, k)
            marks = [ch.start] + [f.outer_pt for f in ch.folds]
            nf = len(ch.folds)
            recs = []
            for j, (L, d) in enumerate(ch.flanges):
                n2 = (-d[1], d[0])
                start = 0.0 if j == 0 else pos[j - 1] + bend_allowance(ch.folds[j - 1], r, ch.t, k) / 2
                lo = ossb(ch.folds[j - 1], r, ch.t) if j else 0.0
                # the flange's line in the chain's section (through its start mark, along d), as 3D directions: D
                # along the flange, N across it; base: the flat place of the mark; lo..hi: the straight part
                recs.append({"D": vadd(vmul(ch.u, d[0]), vmul(ch.v, d[1])), "N": vadd(vmul(ch.u, n2[0]), vmul(ch.v, n2[1])),
                             "m0": marks[j][0] * d[0] + marks[j][1] * d[1], "o0": marks[j][0] * n2[0] + marks[j][1] * n2[1],
                             "base": start - lo, "lo": lo, "hi": L - (ossb(ch.folds[j], r, ch.t) if j < nf else 0.0)})
            self.fl.append(recs)
        self.base, self.along = None, None
        if len(chains) == 2:
            # the flange both runs share (a tray's base): the one where the two sections cross, on both chains'
            # straight parts there (a tray's lips can lie in one plane, but not where the sections cross)
            pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(body.shape)]
            mids = []
            for ch in chains:
                s = [vdot(p, ch.axis) for p in pts]
                mids.append((min(s) + max(s)) / 2)
            pairs = []
            for i, a in enumerate(self.fl[0]):
                for j, b in enumerate(self.fl[1]):
                    if abs(abs(vdot(a["N"], b["N"])) - 1) > 1e-6:
                        continue
                    P = _solve3((chains[0].axis, chains[1].axis, a["N"]), (mids[0], mids[1], a["o0"]))
                    if P is not None and self._on(0, i, P) and self._on(1, j, P):
                        pairs.append((i, j))
            if len(pairs) != 1:
                raise ValueError("its two runs of bends share %d flanges where they cross; drawgen reads parts whose "
                                 "two runs share one (a tray's base)" % len(pairs))
            self.base = pairs[0]
        else:
            ch = chains[0]
            ws = [vdot(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))), ch.axis) for v in geom._vertices_of(body.shape)]
            self.along = {"ax": 1 - matches[0]["dxf_axis"], "a": ch.axis, "w0": min(ws), "width": max(ws) - min(ws)}
        self.w_mid = vdot(body.centroid, chains[0].axis)

    def ref_flange(self):
        """Chain 0's reference flange: the base both chains share, or one chain's longest flange."""
        if self.base:
            return self.base[0]
        fls = self.chains[0].flanges
        return max(range(len(fls)), key=lambda i: fls[i][0])

    def _on(self, ci, j, P):
        f = self.fl[ci][j]
        q = vdot(P, f["D"]) - f["m0"]
        return abs(vdot(P, f["N"]) - f["o0"]) <= self.chains[ci].t + 0.01 and f["lo"] - 0.01 <= q <= f["hi"] + 0.01

    def _value(self, ci, j, P):
        """P's place in the DXF across chain ci's bends, from flange j's line (extended past its ends)."""
        f, m = self.fl[ci][j], self.matches[ci]
        across = f["base"] + vdot(P, f["D"]) - f["m0"]
        ax = m["dxf_axis"]
        return (self.box[2 + ax] - across) if m["reversed"] else (self.box[ax] + across)

    def where(self, P):
        """(x, y) in the DXF for a point of the sheet; None in a bend zone, off the sheet, or where it could be on
        either run's flanges (a corner)."""
        hits = {(ci, j) for ci in range(len(self.fl)) for j in range(len(self.fl[ci])) if self._on(ci, j, P)}
        xy = [None, None]
        if self.along is not None:
            if len(hits) != 1:
                return None
            (_ci, j), = hits
            xy[self.matches[0]["dxf_axis"]] = self._value(0, j, P)
            a = self.along
            w = vdot(P, a["a"]) - a["w0"]
            xy[a["ax"]] = (self.box[a["ax"]] + w) if self.sense > 0 else (self.box[2 + a["ax"]] - w)
            return tuple(xy)
        jA, jB = self.base
        if hits == {(0, jA), (1, jB)}:
            ja, jb = jA, jB
        elif len(hits) == 1 and not hits & {(0, jA), (1, jB)}:
            (ci, j), = hits
            ja, jb = (j, jB) if ci == 0 else (jA, j)
        else:
            return None
        xy[self.matches[0]["dxf_axis"]] = self._value(0, ja, P)
        xy[self.matches[1]["dxf_axis"]] = self._value(1, jb, P)
        return tuple(xy)

    def dirs(self):
        """The 3D directions (on the reference flange) that the DXF's +x and +y run along."""
        d = [None, None]
        f0, m0 = self.fl[0][self.ref_flange()], self.matches[0]
        d[m0["dxf_axis"]] = vmul(f0["D"], -1.0) if m0["reversed"] else f0["D"]
        if self.along is not None:
            d[self.along["ax"]] = vmul(self.along["a"], self.sense)
        else:
            f1, m1 = self.fl[1][self.base[1]], self.matches[1]
            d[m1["dxf_axis"]] = vmul(f1["D"], -1.0) if m1["reversed"] else f1["D"]
        return d

    def ref_points(self):
        """Three points of the sheet, not in a line, on the reference flange's straight part."""
        f = self.fl[0][self.ref_flange()]
        ax = self.chains[0].axis
        q = (f["lo"] + f["hi"]) / 2
        p0 = vadd(vadd(vmul(f["D"], f["m0"] + q), vmul(f["N"], f["o0"])), vmul(ax, self.w_mid))
        return [p0, vadd(p0, vmul(f["D"], 10.0)), vadd(p0, vmul(ax, 10.0))]

    def relating(self, other):
        """The plane map T, as (M, c) with x' = M x + c, that carries this reading's flat onto the other's:
        other.where(P) = T(self.where(P)) for every point P of the sheet."""
        a = [self.where(p) for p in self.ref_points()]
        b = [other.where(p) for p in self.ref_points()]
        if None in a or None in b:
            raise ValueError("drawgen can't place its reference flange in the flat")
        A = ((a[1][0] - a[0][0], a[2][0] - a[0][0]), (a[1][1] - a[0][1], a[2][1] - a[0][1]))
        B = ((b[1][0] - b[0][0], b[2][0] - b[0][0]), (b[1][1] - b[0][1], b[2][1] - b[0][1]))
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
        inv = ((A[1][1] / det, -A[0][1] / det), (-A[1][0] / det, A[0][0] / det))
        M = tuple(tuple(sum(B[i][k] * inv[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        c = tuple(b[0][i] - M[i][0] * a[0][0] - M[i][1] * a[0][1] for i in range(2))
        return M, c

    def record(self):
        """The reading as plain numbers, for the read-back: each chain's flanges (3D lines, flat places, straight
        parts), the DXF axis and direction each chain runs, the shared base or the run along the bend lines."""
        r3 = lambda v: [round(x, 9) for x in v]
        return {"box": [round(x, 6) for x in self.box],
                "chains": [{"ax": m["dxf_axis"], "rev": m["reversed"], "t": ch.t, "axis": r3(ch.axis),
                            "flanges": [{"D": r3(f["D"]), "N": r3(f["N"]), "m0": f["m0"], "o0": f["o0"],
                                         "base": f["base"], "lo": f["lo"], "hi": f["hi"]} for f in recs]}
                           for ch, m, recs in zip(self.chains, self.matches, self.fl)],
                "base": list(self.base) if self.base else None,
                "along": None if self.along is None else {"ax": self.along["ax"], "a": r3(self.along["a"]),
                                                          "w0": self.along["w0"], "sense": self.sense}}


def _solve3(rows, rhs):
    """The point P with rows[i] . P = rhs[i] (Cramer's rule), or None when the rows are dependent."""
    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    d = det(rows)
    if abs(d) < 1e-9:
        return None
    out = []
    for k in range(3):
        m = [list(r) for r in rows]
        for i in range(3):
            m[i][k] = rhs[i]
        out.append(det(m) / d)
    return tuple(out)


def cutouts(body):
    """The model's cut-outs that aren't round holes: inner boundaries of its flat faces made of anything but one
    circle (a rectangle, a slot). The flat's check matches round holes only, so these would go unchecked."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepTools import BRepTools
    from OCP.GeomAbs import GeomAbs_Plane
    from OCP.TopAbs import TopAbs_EDGE
    out = []
    for f in geom._faces(body.shape):
        if BRepAdaptor_Surface(f, True).GetType() != GeomAbs_Plane:
            continue
        outer = BRepTools.OuterWire_s(f)
        e = TopExp_Explorer(f, TopAbs_WIRE)
        while e.More():
            w = TopoDS.Wire_s(e.Current())
            e.Next()
            if w.IsSame(outer):
                continue
            circ, other = set(), 0
            ee = TopExp_Explorer(w, TopAbs_EDGE)
            while ee.More():
                c = BRepAdaptor_Curve(TopoDS.Edge_s(ee.Current()))
                if c.GetType() == GeomAbs_Circle:
                    ci = c.Circle()
                    p = ci.Location()
                    circ.add((round(p.X(), 3), round(p.Y(), 3), round(p.Z(), 3), round(ci.Radius(), 3)))
                else:
                    other += 1
                ee.Next()
            if other or len(circ) != 1:
                pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(w)]
                ext = sorted((max(p[k] for p in pts) - min(p[k] for p in pts) for k in range(3)), reverse=True)
                mid = tuple((max(p[k] for p in pts) + min(p[k] for p in pts)) / 2 for k in range(3))
                size = "%s x %s" % (_f(ext[0]), _f(ext[1]))
                # a cut-out through the sheet bounds both skins: count it once
                if not any(sz == size and max(abs(a - b) for a, b in zip(mid, m)) < 10.0 for sz, m in out):
                    out.append((size, mid))
    return [sz for sz, _m in out]


def is_identity(T, tol=0.01):
    (M, c) = T
    return all(abs(M[i][j] - (1.0 if i == j else 0.0)) < 1e-6 for i in range(2) for j in range(2)) and \
        all(abs(x) <= tol for x in c)


def hole_fails(fm, holes, circles, tol=0.05):
    """The model's holes against the DXF's round holes under one reading, counted both ways: each model hole on a
    DXF circle of its size at its flat place (both axes), each DXF circle on a model hole."""
    fails, used = [], set()
    if len(holes) != len(circles):
        fails.append("its DXF has %d round holes, its model %d" % (len(circles), len(holes)))
    for h in holes:
        c = vadd(h.entry, vmul(h.axis, h.depth / 2))
        xy = fm.where(c)
        if xy is None:
            fails.append("the model's Ø%s hole at (%s, %s, %s) isn't on the straight part of one flange" % (
                (_f(h.dia),) + tuple(_f(x) for x in c)))
            continue
        cand = sorted((_d2(cc, xy), i) for i, (cc, rr) in enumerate(circles)
                      if i not in used and abs(2 * rr - h.dia) < 0.011)
        if cand and cand[0][0] <= tol:
            used.add(cand[0][1])
            continue
        near = min(circles, key=lambda cr: _d2(cr[0], xy)) if circles else None
        fails.append("the model's Ø%s hole belongs at (%s, %s) in the flat; %s" % (
            _f(h.dia), _f(xy[0]), _f(xy[1]), ("the DXF's nearest is Ø%s at (%s, %s)" % (
                _f(2 * near[1]), _f(near[0][0]), _f(near[0][1]))) if near else "the DXF has no hole"))
    for i, (cc, rr) in enumerate(circles):
        if i not in used:
            fails.append("the DXF's Ø%s hole at (%s, %s) is on no hole of the model" % (_f(2 * rr), _f(cc[0]), _f(cc[1])))
    return fails


def _hole_miss(fm, holes, circles):
    """How far the model's holes land from the DXF's under one reading (each to the nearest circle of its size)."""
    total = 0.0
    for h in holes:
        xy = fm.where(vadd(h.entry, vmul(h.axis, h.depth / 2)))
        ds = [_d2(cc, xy) for cc, rr in circles if xy is not None and abs(2 * rr - h.dia) < 0.011]
        total += min(ds) if ds else 1e6
    return total


def _zone_fails(chains, matches, zones, k, tol):
    """The bend zones the DXF marks (MARK / BEND_EXTENT pairs) must be the bend allowance at K round each line."""
    for ch, m in zip(chains, matches):
        ax = m["dxf_axis"]
        for f, line in zip(ch.folds, m["lines"]):
            at = line[0][ax]
            near = sorted(abs(z[0][ax] - at) for z in zones if abs(z[0][ax] - z[1][ax]) < 1e-6)
            ba = bend_allowance(f, m["r"], ch.t, k)
            if len(near) < 2 or abs(near[0] + near[1] - ba) > tol:
                return ["a bend zone the DXF marks isn't the bend allowance %.3f at K %.3f" % (ba, k)]
    return []


def analyse(body, dxf_path, radius=None, radius_from=None, holes=(), tol=0.05):
    """Read a bent part against its DXF. Raises ValueError with the reason drawgen can't draw it. radius: the
    inside radius for folds the model draws sharp (the team's entry), with where it comes from.

    Every reading of the DXF that fits the bend lines (a symmetric run fits forward and reversed; one run says
    nothing about which way the DXF runs along its bend lines) is tried against the holes, counted both ways. When
    more than one reading is left and they differ, the DXF (outline, holes, bend lines) must be symmetric the way
    they differ, so each folds the same part; otherwise the part is refused, since nothing pins which way up the DXF
    is drawn and the bend directions could be read either way (Reviewer 6 on #335)."""
    import itertools
    fl = Flat()
    fl.dxf = Dxf(dxf_path)
    if fl.dxf.units not in (None, 4):
        raise ValueError("its DXF isn't in mm ($INSUNITS %s)" % fl.dxf.units)
    seen = []
    for ax in bend_axes(body):
        ch = chain_of(body, ax)
        if ch is None or any(abs(abs(vdot(ax, a)) - 1) < 1e-6 for a in seen):
            continue
        seen.append(ax)
        fl.chains.append(ch)
    if not fl.chains:
        raise ValueError("drawgen can't read its folds (no section across them is one strip of sheet)")
    cuts = cutouts(body)
    if cuts:
        raise ValueError("its model has %d cut-out%s that %s round holes (%s): drawgen sizes and checks round holes "
                         "only so far" % (len(cuts), "s" if len(cuts) > 1 else "", "aren't" if len(cuts) > 1 else "isn't a",
                                          ", ".join(cuts)))
    if len(fl.chains) > 2:
        raise ValueError("its bend lines run in %d directions; drawgen reads one or two" % len(fl.chains))
    if len(fl.chains) == 2 and abs(vdot(fl.chains[0].axis, fl.chains[1].axis)) > 1e-6:
        raise ValueError("its two runs of bend lines aren't square to each other")
    nb = len(fl.dxf.bend_lines())
    if nb != sum(len(ch.folds) for ch in fl.chains):
        raise ValueError("its DXF has %d bend lines, its model %d folds" % (nb, sum(len(ch.folds) for ch in fl.chains)))
    loops = fl.dxf.cut_loops()
    if loops != 1:
        raise ValueError("its DXF's cut lines make %d closed shapes besides its round holes; drawgen reads one outline "
                         "and round holes" % loops)
    options = []
    for ch in fl.chains:
        rs = {round(f.r, 4) for f in ch.folds if f.r is not None}
        if len(rs) > 1:
            raise ValueError("its folds have different inside radii (%s): one bend table radius isn't enough" % rs)
        r = rs.pop() if rs else radius
        if r is None:
            raise ValueError("its model folds sharp: its entry must give the inside radius (bent: {'radius': ...})")
        if any(f.r is None for f in ch.folds) and rs:
            raise ValueError("some folds have a radius in the model and some don't")
        opts = match_chain(ch, fl.dxf, r, tol)
        if not opts:
            raise ValueError("its DXF's bend lines don't sit where the model's folds put them at any one K-factor "
                             "(inside radius R%s)" % _f(r))
        for m in opts:
            m["r"] = r
        options.append(opts)
    box = fl.dxf.cut_box()
    circles = [(c, r) for lay, c, r in fl.dxf.circles if fl.dxf.role(lay) == "cut"]
    zones = fl.dxf.zone_lines()
    readings, why, kfail = [], [], None
    for pick in itertools.product(*options):
        if len({m["dxf_axis"] for m in pick}) != len(pick):
            continue
        ks = [m["k"] for m in pick]
        if max(ks) - min(ks) > 0.005:
            kfail = ks
            continue
        k = sum(ks) / len(ks)
        zf = _zone_fails(fl.chains, pick, zones, k, tol) if zones else []
        if zf:
            why.append((len(zf), float("inf"), zf))
            continue
        for sense in ((1.0, -1.0) if len(pick) == 1 else (None,)):
            fm = FlatMap(body, fl.chains, list(pick), sense, box, k)
            if fm.along is not None:
                w = box[2 + fm.along["ax"]] - box[fm.along["ax"]]
                if abs(w - fm.along["width"]) > tol:
                    raise ValueError("its DXF's flat is %s along the bend lines, the model %s" % (_f(w), _f(fm.along["width"])))
            hf = hole_fails(fm, holes, circles, tol)
            if hf:
                why.append((len(hf), _hole_miss(fm, holes, circles), hf))
                continue
            readings.append(fm)
    if not readings:
        if not why and kfail:
            raise ValueError("its chains need different K-factors (%s)" % ", ".join("%.3f" % k for k in kfail))
        # the reading that comes nearest: fewest misses, then the holes nearest the DXF's
        raise ValueError("its DXF doesn't match the model: " + "; ".join(min(why, key=lambda w: w[:2])[2]))
    # more than one reading left (no hole tells them apart): each must fold the same part, so the DXF must map onto
    # itself the way they differ
    for other in readings[1:]:
        T = readings[0].relating(other)
        if is_identity(T):
            continue
        bad = fl.dxf.off_symmetry(T, tol)
        if bad:
            raise ValueError("nothing pins which way up its DXF is drawn: no hole tells, and its flat isn't symmetric "
                             "(%s), so its bends' directions could be read two ways that fold different parts" % bad)
    fl.readings = len(readings)
    best = None
    for fm in readings:
        rows = _rows(fl.chains, fm)
        ups = sum(r_["dir"] == "UP" for r_ in rows)
        if best is None or ups > best[0]:           # among readings that fold the same part: most bends UP
            best = (ups, fm, rows)
    _ups, fm, fl.rows = best
    fl.map = fm
    fl.matches = fm.matches
    fl.k = fm.k
    fl.radius = fl.matches[0]["r"]
    fl.radius_from = "the model" if any(f.r is not None for f in fl.chains[0].folds) else (radius_from or "its entry")
    fl.viewed = "from the side the DXF shows"
    return fl


def _rows(chains, fm):
    """The bend table's rows under one reading: each bend line's place, and UP when the fold closes toward the
    viewer of the DXF (its inside on the skin the DXF shows)."""
    dirs = fm.dirs()
    z = vcross(dirs[0], dirs[1])
    rows = []
    for ci, (ch, m) in enumerate(zip(chains, fm.matches)):
        nA = _skin_normal(ch, fm.ref_flange() if ci == 0 else fm.base[1])
        viewed = "A" if vdot(nA, z) > 0 else "B"
        ax = m["dxf_axis"]
        for f, line in zip(ch.folds, m["lines"]):
            rows.append({"axis": "xy"[ax], "at": line[0][ax] - fm.box[ax], "dir": "UP" if f.inside == viewed else "DOWN",
                         "angle": f.angle, "r": m["r"], "line": line})
    # the table in reading order: lines across x first (their places up the flat), then lines across y
    rows.sort(key=lambda x: (x["axis"] != "y", x["at"]))
    for j, x in enumerate(rows):
        x["tag"] = "B%d" % (j + 1)
    return rows


def _f(v):
    t = ("%.2f" % v).rstrip("0").rstrip(".")
    return t or "0"
