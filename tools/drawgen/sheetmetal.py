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
from dxf import Dxf  # the reader is shared with the read-back
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
    the chain's folds, whose places along that axis the model's flat gives at one K-factor, the chain run forward or
    reversed. Returns {"dxf_axis": 0 or 1 (x or y: the lines' places), "reversed", "k", "lines": [DXF line per fold],
    "worst": mm} or None."""
    box = dxf.cut_box()
    if box is None:
        return None
    best = None
    for ax in (0, 1):
        group = [(a, b) for a, b in dxf.bend_lines() if abs(a[ax] - b[ax]) < 1e-6]
        if len(group) != len(chain.folds):
            continue
        group.sort(key=lambda l: l[0][ax])
        lo, hi = box[ax], box[2 + ax]
        k = solve_k(chain, r, hi - lo)
        if k is None:
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
            if worst <= tol and (best is None or worst < best["worst"]):
                best = {"dxf_axis": ax, "reversed": rev, "k": k, "lines": lines, "worst": worst, "positions": pos}
    return best


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


def _flat_frame(ch, m, ref):
    """For chain ch matched by m: the DXF axis its places run along (m's axis) as a 3D direction in the reference
    flange's plane (the run of flange ref, with the chain's sense, reversed when the DXF runs the other way)."""
    d = ch.flanges[ref][1]
    d3 = vadd(vmul(ch.u, d[0]), vmul(ch.v, d[1]))
    return vmul(d3, -1.0) if m["reversed"] else d3


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


def analyse(body, dxf_path, radius=None, radius_from=None, holes=(), tol=0.05):
    """Read a bent part against its DXF. Raises ValueError with the reason drawgen can't draw it. radius: the
    inside radius for folds the model draws sharp (the team's entry), with where it comes from."""
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
    nb = len(fl.dxf.bend_lines())
    if nb != sum(len(ch.folds) for ch in fl.chains):
        raise ValueError("its DXF has %d bend lines, its model %d folds" % (nb, sum(len(ch.folds) for ch in fl.chains)))
    for ch in fl.chains:
        rs = {round(f.r, 4) for f in ch.folds if f.r is not None}
        if len(rs) > 1:
            raise ValueError("its folds have different inside radii (%s): one bend table radius isn't enough" % rs)
        r = rs.pop() if rs else radius
        if r is None:
            raise ValueError("its model folds sharp: its entry must give the inside radius (bent: {'radius': ...})")
        if any(f.r is None for f in ch.folds) and rs:
            raise ValueError("some folds have a radius in the model and some don't")
        m = match_chain(ch, fl.dxf, r, tol)
        if m is None:
            raise ValueError("its DXF's bend lines don't sit where the model's folds put them at any one K-factor "
                             "(inside radius R%s)" % _f(r))
        m["r"] = r
        fl.matches.append(m)
    ks = [m["k"] for m in fl.matches]
    if max(ks) - min(ks) > 0.005:
        raise ValueError("its chains need different K-factors (%s)" % ", ".join("%.3f" % k for k in ks))
    fl.k = sum(ks) / len(ks)
    fl.radius = fl.matches[0]["r"]
    fl.radius_from = "the model" if any(f.r is not None for f in fl.chains[0].folds) else (radius_from or "its entry")
    # the bend zones the DXF marks (MARK / BEND_EXTENT pairs) must be the bend allowance at that K
    zones = fl.dxf.zone_lines()
    if zones:
        for ch, m in zip(fl.chains, fl.matches):
            ax = m["dxf_axis"]
            for f, line in zip(ch.folds, m["lines"]):
                at = line[0][ax]
                near = sorted(abs(z[0][ax] - at) for z in zones if abs(z[0][ax] - z[1][ax]) < 1e-6)
                ba = bend_allowance(f, m["r"], ch.t, fl.k)
                if len(near) < 2 or abs(near[0] + near[1] - ba) > tol:
                    raise ValueError("a bend zone the DXF marks isn't the bend allowance %.3f at K %.3f" % (ba, fl.k))
    # which skin the DXF shows, and so each fold's direction as drawn: the DXF's x and y as 3D directions in the
    # reference flange (each chain's longest), the second axis's sense fixed by a second chain, or by the holes
    ref = [max(range(len(ch.flanges)), key=lambda i: ch.flanges[i][0]) for ch in fl.chains]
    dirs = {}
    for ch, m, i in zip(fl.chains, fl.matches, ref):
        dirs[m["dxf_axis"]] = _flat_frame(ch, m, i)
    if len(dirs) < 2:
        ch, m = fl.chains[0], fl.matches[0]
        other = 1 - m["dxf_axis"]
        sense = _axis_sense(body, ch, m, fl, holes, tol)
        dirs[other] = vmul(ch.axis, sense)
    z = vcross(dirs[0], dirs[1])
    fl.rows = []
    nb = 0
    for ch, m, i in zip(fl.chains, fl.matches, ref):
        nA = _skin_normal(ch, i)
        if nA is None:
            raise ValueError("drawgen can't tell its two skins apart on flange %d" % (i + 1))
        viewed = "A" if vdot(nA, z) > 0 else "B"
        ax = m["dxf_axis"]
        box = fl.dxf.cut_box()
        for f, line in zip(ch.folds, m["lines"]):
            nb += 1
            at = line[0][ax] - box[ax]
            fl.rows.append({"tag": "B%d" % nb, "axis": "xy"[ax], "at": at, "dir": "UP" if f.inside == viewed else "DOWN",
                            "angle": f.angle, "r": m["r"], "line": line})
    # the table in reading order: lines across x first (their places up the flat), then lines across y
    fl.rows.sort(key=lambda x: (x["axis"] != "y", x["at"]))
    for j, x in enumerate(fl.rows):
        x["tag"] = "B%d" % (j + 1)
    fl.viewed = "from the side the DXF shows"
    return fl


def _f(v):
    t = ("%.2f" % v).rstrip("0").rstrip(".")
    return t or "0"


def flat_coord(ch, m, k, P):
    """A point on the sheet (3D, on one of its flanges): its place along the chain in the flat, from the DXF's lower
    edge on the chain's axis (mm), or None when it isn't on a flange."""
    r = m["r"]
    p2 = (vdot(P, ch.u), vdot(P, ch.v))
    pos, total = flat_positions(ch, r, k)
    marks = [ch.start] + [f.outer_pt for f in ch.folds]
    for i, (L, d) in enumerate(ch.flanges):
        q = (p2[0] - marks[i][0]) * d[0] + (p2[1] - marks[i][1]) * d[1]
        off = abs((p2[0] - marks[i][0]) * d[1] - (p2[1] - marks[i][1]) * d[0])
        if -1e-6 <= q <= L + 1e-6 and off <= ch.t + 1e-3:
            start = 0.0 if i == 0 else pos[i - 1] + bend_allowance(ch.folds[i - 1], r, ch.t, k) / 2
            c = start + q - (ossb(ch.folds[i - 1], r, ch.t) if i else 0.0)
            return (total - c) if m["reversed"] else c
    return None


def _axis_sense(body, ch, m, fl, holes, tol):
    """The sense of the DXF's other axis along the bend lines (+1: it runs with ch.axis), from the holes: each hole
    of the model must have a circle of its size in the DXF at its flat place. Without holes either sense is the same
    part (a mirror of a symmetric flat): +1."""
    if not holes:
        if fl.dxf.circles:
            raise ValueError("its DXF has %d holes, its model none" % len(fl.dxf.circles))
        return 1.0
    box = fl.dxf.cut_box()
    other = 1 - m["dxf_axis"]
    pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(body.shape)]
    w0 = min(vdot(p, ch.axis) for p in pts)
    circles = [(c, r) for lay, c, r in fl.dxf.circles if fl.dxf.role(lay) == "cut"]
    if len(circles) != len(holes):
        raise ValueError("its DXF has %d holes, its model %d" % (len(circles), len(holes)))
    fails = {}
    for sense in (1.0, -1.0):
        bad = []
        for h in holes:
            c = flat_coord(ch, m, fl.k, h.entry)
            if c is None:
                bad.append("a Ø%s hole off its flanges" % _f(h.dia))
                continue
            w = vdot(h.entry, ch.axis) - w0
            want = [0.0, 0.0]
            want[m["dxf_axis"]] = box[m["dxf_axis"]] + c
            want[other] = (box[other] + w) if sense > 0 else (box[2 + other] - w)
            hit = [cc for cc, rr in circles if abs(rr * 2 - h.dia) < 0.011 and _d2(cc, want) <= tol]
            if not hit:
                near = min(circles, key=lambda cr: _d2(cr[0], want))
                bad.append("the model's Ø%s hole belongs at (%s, %s) in the flat; the DXF's nearest is at (%s, %s)" % (
                    _f(h.dia), _f(want[0]), _f(want[1]), _f(near[0][0]), _f(near[0][1])))
        if not bad:
            return sense
        fails[sense] = bad
    raise ValueError("its DXF's holes don't match the model: " + "; ".join(min(fails.values(), key=len)))


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
