"""Bent sheet with folds along any line (AIR's duct transitions, the Lead's queue 2026-11-01): the folds are read one
by one from the model's bend cylinders, not from a section, and the part is unfolded face by face.

The sheet's two skins are found by following each skin across the edges where it runs on smoothly (a flange's face
into its bend's cylinder and on into the next flange); the faces that meet a skin at an edge (the sheet's edges, its
holes) belong to neither. A bend is a cylinder of one skin with its partner on the other, coaxial and t further out
or in; its angle is the cylinder's own sweep. Unfolding starts from the largest flange: each bend between a flange
already in the flat and the next leaves a strip of its bend allowance a (r + K t) between their tangent lines, the
next flange turned about the bend line into the plane. Lengths are mm; the flat's frame is the largest flange's,
its +z the first skin's outside. The DXF is then met by a plane isometry (any angle, either side up) that puts every
unfolded bend line on one of its BEND lines and every hole on one of its circles, both ways."""

import math

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepGProp import BRepGProp
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Line, GeomAbs_Plane
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.TopoDS import TopoDS

import geom
from geom import vadd, vcross, vdot, vmul, vnorm, vsub


def _area(f):
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(f, p)
    return p.Mass()


def _centre(f):
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(f, p)
    c = p.CentreOfMass()
    return (c.X(), c.Y(), c.Z())


def _normal_at(f, P):
    """The face's outward normal (the solid's) at the point of it nearest P."""
    surf = BRep_Tool.Surface_s(f)
    pr = GeomAPI_ProjectPointOnSurf(geom_pnt(P), surf)
    u, v = pr.LowerDistanceParameters()
    props = BRepLProp_SLProps(BRepAdaptor_Surface(f, True), u, v, 1, 1e-7)
    n = props.Normal()
    out = (n.X(), n.Y(), n.Z())
    return vmul(out, -1.0) if f.Orientation() == TopAbs_REVERSED else out


def geom_pnt(P):
    from OCP.gp import gp_Pnt
    return gp_Pnt(*P)


def _edge_mid(e):
    c = BRepAdaptor_Curve(e)
    return geom.pnt(c.Value((c.FirstParameter() + c.LastParameter()) / 2))


def _edge_ends(e):
    c = BRepAdaptor_Curve(e)
    return geom.pnt(c.Value(c.FirstParameter())), geom.pnt(c.Value(c.LastParameter()))


class Face:
    def __init__(self, i, f):
        self.i, self.f = i, f
        s = BRepAdaptor_Surface(f, True)
        self.kind = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder"}.get(s.GetType(), "other")
        self.area = _area(f)
        self.centre = _centre(f)
        if self.kind == "plane":
            self.normal = _normal_at(f, self.centre)
        if self.kind == "cylinder":
            c = s.Cylinder()
            ax = c.Axis()
            self.axis_p = geom.pnt(ax.Location())
            self.axis_d = vnorm((ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()))
            self.radius = c.Radius()
            u0, u1, _v0, _v1 = BRepTools.UVBounds_s(f)
            self.sweep = abs(u1 - u0)


class Bend:
    """One fold: its cylinder on the first skin (`face`, radius R) and on the other (`twin`), its axis, its inside
    radius r and angle (radians), the two flanges it joins and the tangent edges it shares with them on the first
    skin."""

    def __init__(self, face, twin, t):
        self.face, self.twin = face, twin
        self.axis_p, self.axis_d = face.axis_p, face.axis_d
        self.r = min(face.radius, twin.radius)
        self.t = t
        self.angle = face.sweep
        self.inside_first = face.radius < twin.radius   # the first skin is on the fold's inside
        self.flanges = []           # [(flange Face, shared edge)]


class Sheet:
    """A bent part read face by face: its thickness, its first skin's flanges (planes) and bends."""

    def __init__(self):
        self.t = None
        self.faces, self.skin, self.other = [], [], []
        self.flanges, self.bends = [], []


def read(body):
    """The sheet's skins, thickness, flanges and bends; ValueError with the reason when the body isn't one."""
    shape = body.shape
    efm = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, efm)
    faces = []
    e = TopExp_Explorer(shape, TopAbs_FACE)
    while e.More():
        f = TopoDS.Face_s(e.Current())
        if not any(f.IsSame(x.f) for x in faces):
            faces.append(Face(len(faces), f))
        e.Next()
    idx = lambda f: next(x for x in faces if x.f.IsSame(f))
    # each face's edges and the face across each
    nbrs = {x.i: [] for x in faces}
    for k in range(1, efm.Extent() + 1):
        ed = TopoDS.Edge_s(efm.FindKey(k))
        fl = efm.FindFromIndex(k)
        it = [TopoDS.Face_s(s) for s in fl]
        uniq = []
        for f in it:
            if not any(f.IsSame(u) for u in uniq):
                uniq.append(f)
        if len(uniq) != 2:
            continue
        a, b = idx(uniq[0]), idx(uniq[1])
        P = _edge_mid(ed)
        smooth = vdot(_normal_at(a.f, P), _normal_at(b.f, P)) > 1 - 1e-6
        nbrs[a.i].append((b, ed, smooth))
        nbrs[b.i].append((a, ed, smooth))

    def flood(start):
        seen, todo = {start.i}, [start]
        while todo:
            x = todo.pop()
            for y, _e, sm in nbrs[x.i]:
                if sm and y.i not in seen and y.kind in ("plane", "cylinder"):
                    seen.add(y.i)
                    todo.append(y)
        return [x for x in faces if x.i in seen]
    planes = sorted([x for x in faces if x.kind == "plane"], key=lambda x: -x.area)
    if not planes:
        raise ValueError("it has no flat faces")
    skin = flood(planes[0])
    rest = [x for x in planes if x.i not in {s.i for s in skin}]
    if not rest:
        raise ValueError("drawgen can't find its second skin")
    other = flood(rest[0])
    sh = Sheet()
    sh.faces, sh.skin, sh.other = faces, skin, other
    sh.nbrs = nbrs
    # bends: each cylinder of the first skin with a coaxial partner on the other
    cyl_o = [x for x in other if x.kind == "cylinder"]
    ts = []
    for c in [x for x in skin if x.kind == "cylinder"]:
        tw = [o for o in cyl_o if abs(abs(vdot(o.axis_d, c.axis_d)) - 1) < 1e-6 and
              vnorm_len(vsub(vsub(o.axis_p, c.axis_p), vmul(c.axis_d, vdot(vsub(o.axis_p, c.axis_p), c.axis_d)))) < 1e-4]
        if len(tw) != 1:
            raise ValueError("a curved face of its skin isn't a bend (no coaxial partner on the other skin): r%.2f"
                             % c.radius)
        ts.append(abs(tw[0].radius - c.radius))
        sh.bends.append(Bend(c, tw[0], None))
    if not sh.bends:
        raise ValueError("it has no bends")
    t = sum(ts) / len(ts)
    if max(ts) - min(ts) > 1e-3:
        raise ValueError("its bends give different thicknesses (%s)" % ", ".join("%.3f" % x for x in ts))
    sh.t = t
    for b in sh.bends:
        b.t = t
    # flanges: the first skin's planes; each bend's two tangent edges and the flanges across them
    sh.flanges = [x for x in skin if x.kind == "plane"]
    for b in sh.bends:
        for y, ed, sm in nbrs[b.face.i]:
            if sm and y.kind == "plane":
                c = BRepAdaptor_Curve(ed)
                if c.GetType() == GeomAbs_Line:
                    b.flanges.append((y, ed))
        if len(b.flanges) != 2 or b.flanges[0][0].i == b.flanges[1][0].i:
            raise ValueError("a bend (r%.2f) doesn't join two flanges" % b.r)
    if any(x.kind == "other" for x in skin + other):
        raise ValueError("its skins have faces that are neither flat nor a bend's cylinder")
    return sh


def vnorm_len(v):
    return math.sqrt(vdot(v, v))


class Map2D:
    """A flange's place in the flat: P -> c + (R . (P - p0)), R two 3D rows (the flat's x and y in 3D)."""

    def __init__(self, p0, ex, ey, c):
        self.p0, self.ex, self.ey, self.c = p0, ex, ey, c

    def __call__(self, P):
        d = vsub(P, self.p0)
        return (self.c[0] + vdot(d, self.ex), self.c[1] + vdot(d, self.ey))

    def vec(self, v):
        return (vdot(v, self.ex), vdot(v, self.ey))


class Unfolded:
    """The sheet in the flat: each flange's map, each bend's centre line and zone edges (flat 2D, the first skin's
    outside up), and the bend allowance used."""

    def __init__(self):
        self.maps = {}          # flange face index -> Map2D
        self.lines = []         # per bend: (bend, (a, b) centre line, (zone edge F, zone edge G), allowance)


def unfold(sh, k):
    """Unfold from the largest flange at K-factor k: each bend's strip a (r + K t) wide between the tangent lines."""
    base = max(sh.flanges, key=lambda f: f.area)
    N = base.normal
    # the largest flange's frame: x along its longest straight edge, y = N x x
    best = None
    e = TopExp_Explorer(base.f, TopAbs_EDGE)
    while e.More():
        ed = TopoDS.Edge_s(e.Current())
        c = BRepAdaptor_Curve(ed)
        if c.GetType() == GeomAbs_Line:
            a, b = _edge_ends(ed)
            L = vnorm_len(vsub(b, a))
            if best is None or L > best[0]:
                best = (L, a, b)
        e.Next()
    ex = vnorm(vsub(best[2], best[1])) if best else vnorm(vcross(N, (1.0, 0.0, 0.0) if abs(N[0]) < 0.9 else (0, 1, 0)))
    ey = vcross(N, ex)
    uf = Unfolded()
    uf.maps[base.i] = Map2D(best[1] if best else base.centre, ex, ey, (0.0, 0.0))
    done = {base.i}
    todo = [base]
    while todo:
        F = todo.pop(0)
        mF = uf.maps[F.i]
        for b in sh.bends:
            ends = {fl.i: ed for fl, ed in b.flanges}
            if F.i not in ends:
                continue
            G, eG = next((fl, ed) for fl, ed in b.flanges if fl.i != F.i)
            if G.i in done:
                continue
            eF = ends[F.i]
            a = b.axis_d
            pF0, _pF1 = _edge_ends(eF)
            # in each flange's plane, the direction square to the bend line: out of F toward the bend, and out of
            # the bend into G
            def across(face, P):
                d = vsub(P, face.centre)
                d = vsub(d, vmul(a, vdot(d, a)))
                d = vsub(d, vmul(face.normal, vdot(d, face.normal)))
                return vnorm(d)
            nF = across(F, pF0)
            pG0, _pG1 = _edge_ends(eG)
            nG = vmul(across(G, pG0), -1.0)
            BA = b.angle * (b.r + k * sh.t)
            nu = mF.vec(nF)
            al = mF.vec(a)
            # G's point pG0 sits across the strip from the point of F's tangent line at its place along the bend
            pF_star = vadd(pF0, vmul(a, vdot(vsub(pG0, pF0), a)))
            q = mF(pF_star)
            cG = (q[0] + nu[0] * BA, q[1] + nu[1] * BA)
            # G's map: a -> al, nG -> nu (in 3D rows: ex_G = a al_x + nG nu_x, ey_G = a al_y + nG nu_y)
            exG = vadd(vmul(a, al[0]), vmul(nG, nu[0]))
            eyG = vadd(vmul(a, al[1]), vmul(nG, nu[1]))
            uf.maps[G.i] = Map2D(pG0, exG, eyG, cG)
            done.add(G.i)
            todo.append(G)
        for b in sh.bends:
            pass
    if len(done) != len(sh.flanges):
        raise ValueError("%d of its flanges aren't reached through its bends" % (len(sh.flanges) - len(done)))
    # each bend's centre line and zone edges, from the flange its strip starts at (the one nearer the base in the walk
    # does not matter: both give the same line)
    for b in sh.bends:
        (F, eF), (G, eG) = b.flanges
        mF = uf.maps[F.i]
        pa, pb = _edge_ends(eF)
        a2, b2 = mF(pa), mF(pb)
        # the strip lies on the side of F's tangent line away from F's middle
        c2 = mF(F.centre)
        d = (b2[0] - a2[0], b2[1] - a2[1])
        L = math.hypot(*d) or 1.0
        nrm = (-d[1] / L, d[0] / L)
        if (c2[0] - a2[0]) * nrm[0] + (c2[1] - a2[1]) * nrm[1] > 0:
            nrm = (-nrm[0], -nrm[1])
        BA = b.angle * (b.r + k * sh.t)
        mid = lambda p, s: (p[0] + nrm[0] * s, p[1] + nrm[1] * s)
        uf.lines.append((b, (mid(a2, BA / 2), mid(b2, BA / 2)), ((a2, b2), (mid(a2, BA), mid(b2, BA))), BA))
    uf.k = k
    return uf


# ------------------------------------------------------------------ the DXF

def _iso(m):
    """A plane isometry from (mirror, cos, sin, tx, ty): x' = Rot (Mirror x) + t."""
    mirror, c, s, tx, ty = m

    def f(p):
        x, y = p
        if mirror:
            y = -y
        return (c * x - s * y + tx, s * x + c * y + ty)
    return f


def _fit(p0, p1, q0, q1, mirror):
    """The isometry that takes segment p0-p1 to q0-q1 (mirrored first when asked), or None when their lengths
    differ by more than 0.05."""
    if mirror:
        p0, p1 = (p0[0], -p0[1]), (p1[0], -p1[1])
    dp = (p1[0] - p0[0], p1[1] - p0[1])
    dq = (q1[0] - q0[0], q1[1] - q0[1])
    lp, lq = math.hypot(*dp), math.hypot(*dq)
    if abs(lp - lq) > 0.05 or lp < 1e-9:
        return None
    ang = math.atan2(dq[1], dq[0]) - math.atan2(dp[1], dp[0])
    c, s = math.cos(ang), math.sin(ang)
    tx = q0[0] - (c * p0[0] - s * p0[1])
    ty = q0[1] - (s * p0[0] + c * p0[1])
    return (mirror, c, s, tx, ty)


def match(uf, dxf, holes_flat, tol=0.05):
    """Every plane isometry that puts each unfolded bend line on one of the DXF's BEND lines (both ends within tol,
    one to one) and each hole (flat centre, diameter) on one of its CUT circles of that size, both ways."""
    lines = dxf.bend_lines()
    circles = [(c, r) for lay, c, r in dxf.circles if dxf.role(lay) == "cut"]
    if len(lines) != len(uf.lines):
        return [], "its DXF has %d bend lines, its model %d bends" % (len(lines), len(uf.lines))
    if len(circles) != len(holes_flat):
        return [], "its DXF has %d round holes, its model %d" % (len(circles), len(holes_flat))
    m0 = max(uf.lines, key=lambda x: math.dist(*x[1]))
    out, seen = [], []
    for q0, q1 in lines:
        for mirror in (False, True):
            for a_, b_ in ((q0, q1), (q1, q0)):
                T = _fit(m0[1][0], m0[1][1], a_, b_, mirror)
                if T is None:
                    continue
                f = _iso(T)
                used, ok = set(), True
                pairs = []
                for ln in uf.lines:
                    pa, pb = f(ln[1][0]), f(ln[1][1])
                    hit = next((i for i, (u, v) in enumerate(lines) if i not in used and (
                        (math.dist(pa, u) <= tol and math.dist(pb, v) <= tol) or
                        (math.dist(pa, v) <= tol and math.dist(pb, u) <= tol))), None)
                    if hit is None:
                        ok = False
                        break
                    used.add(hit)
                    pairs.append(lines[hit])
                if not ok:
                    continue
                cu = set()
                for c, dia in holes_flat:
                    q = f(c)
                    hit = next((i for i, (cc, rr) in enumerate(circles) if i not in cu and abs(2 * rr - dia) < 0.011
                                and math.dist(q, cc) <= tol), None)
                    if hit is None:
                        ok = False
                        break
                    cu.add(hit)
                if not ok:
                    continue
                key = tuple(round(v, 6) for v in (T[0], T[1], T[2], T[3], T[4]))
                if key not in seen:
                    seen.append(key)
                    out.append((T, pairs))
    return out, None


def _apply(T, p):
    return _iso(T)(p)


def outline(sh, uf):
    """The unfolded outline (model flat): each flange's edges where it meets the sheet's edge (not a bend), sampled,
    and each bend zone's two ends (its strip's width, across)."""
    polys = []
    for f in sh.flanges:
        m = uf.maps[f.i]
        outer = BRepTools.OuterWire_s(f.f)
        oe = []
        e = TopExp_Explorer(outer, TopAbs_EDGE)
        while e.More():
            oe.append(TopoDS.Edge_s(e.Current()))
            e.Next()
        for y, ed, sm in sh.nbrs[f.i]:
            if sm or not any(ed.IsSame(x) for x in oe):
                continue            # a tangent line into a bend, or a hole's edge
            c = BRepAdaptor_Curve(ed)
            n = 1 if c.GetType() == GeomAbs_Line else 24
            u0, u1 = c.FirstParameter(), c.LastParameter()
            polys.append([m(geom.pnt(c.Value(u0 + (u1 - u0) * i / n))) for i in range(n + 1)])
    for b, _line, zone, _ba in uf.lines:
        polys.append([zone[0][0], zone[1][0]])
        polys.append([zone[0][1], zone[1][1]])
    return polys


def outline_fails(polys, T, dxf, tol=0.05):
    """The unfolded outline against the DXF's CUT outline, both ways: every point of each within tol of the other."""
    import dxf as dxfmod
    comps = dxf.cut_components()
    if not comps:
        return ["its DXF has no outline"]
    prims = comps[0]["prims"]
    g = dxfmod._Grid(prims, tol)
    segs = []
    for pl in polys:
        pts = [_apply(T, p) for p in pl]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            n = max(1, int(math.ceil(math.dist(a, b) / 1.0)))
            for j in range(n + 1):
                q = (a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n)
                if g.dist(q) > tol:
                    return ["the model's outline unfolds to (%.2f, %.2f), off the DXF's" % q]
            segs.append(("L", a, b))
    g2 = dxfmod._Grid(segs, tol)
    for pr in prims:
        for q in dxfmod._samples(pr, 1.0):
            if g2.dist(q) > tol:
                return ["the DXF's outline at (%.2f, %.2f) is on no edge of the unfolded model" % q]
    return []


def _relating(T1, T2):
    """The plane map (M, c) with T2(x) = M T1(x) + c, from three points."""
    pts = [(0.0, 0.0), (100.0, 0.0), (0.0, 100.0)]
    a = [_apply(T1, p) for p in pts]
    b = [_apply(T2, p) for p in pts]
    A = ((a[1][0] - a[0][0], a[2][0] - a[0][0]), (a[1][1] - a[0][1], a[2][1] - a[0][1]))
    B = ((b[1][0] - b[0][0], b[2][0] - b[0][0]), (b[1][1] - b[0][1], b[2][1] - b[0][1]))
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    inv = ((A[1][1] / det, -A[0][1] / det), (-A[1][0] / det, A[0][0] / det))
    M = tuple(tuple(sum(B[i][k] * inv[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    c = tuple(b[0][i] - M[i][0] * a[0][0] - M[i][1] * a[0][1] for i in range(2))
    return M, c


class Flat:
    """A bent part unfolded face by face and met with its DXF: what compose and the read-back take from it."""

    def __init__(self):
        self.mode = "unfold"
        self.chains, self.matches, self.cutouts = [], [], []
        self.vgroove = None
        self.rows = []
        self.readings = 0


def where(sh, uf, P):
    """A point of the sheet's place in the model's flat (before the DXF's isometry): from the flange it lies on (within
    the sheet of its plane, inside its outer edge), or None."""
    from OCP.BRepClass import BRepClass_FaceClassifier
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    from OCP.gp import gp_Pnt
    hits = []
    for f in sh.flanges:
        dist = vdot(vsub(P, f.centre), f.normal)
        if abs(dist) > sh.t + 0.01:
            continue
        Q = vsub(P, vmul(f.normal, dist))
        cl = BRepClass_FaceClassifier(_outer_face(f), gp_Pnt(*Q), 1e-6)
        if cl.State() in (TopAbs_IN, TopAbs_ON):
            hits.append(f)
    if len(hits) != 1:
        return None
    return uf.maps[hits[0].i](P)


_OUTER = {}


def _outer_face(f):
    """The flange's face without its holes (a hole's centre lies in its outer edge, not in its material)."""
    if f.i not in _OUTER or not _OUTER[f.i][0].IsSame(f.f):
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        w = BRepTools.OuterWire_s(f.f)
        _OUTER[f.i] = (f.f, BRepBuilderAPI_MakeFace(BRep_Tool.Surface_s(f.f), w, True).Face())
    return _OUTER[f.i][1]


def analyse(body, dxf_path, k, holes=(), radius=None, radius_from=None, tol=0.05):
    """A bent part with folds along any line, read face by face and met with its DXF at K-factor k (its entry's): every
    bend line and hole of the unfolded model on the DXF's, both ways. Raises ValueError with the reason."""
    from dxf import Dxf
    import sheetmetal
    fl = Flat()
    fl.dxf = Dxf(dxf_path)
    if fl.dxf.units not in (None, 4):
        raise ValueError("its DXF isn't in mm ($INSUNITS %s)" % fl.dxf.units)
    sh = read(body)
    cuts, odd = sheetmetal.model_cutouts(body)
    if cuts or odd:
        raise ValueError("its cut-outs that aren't round holes aren't read with folds along any line yet")
    rs = {round(b.r, 4) for b in sh.bends}
    if len(rs) > 1:
        raise ValueError("its bends have different inside radii (%s)" % ", ".join("R%s" % sheetmetal._f(r) for r in rs))
    uf = unfold(sh, k)
    _OUTER.clear()
    holes_flat = []
    for h in holes:
        c = vadd(h.entry, vmul(h.axis, h.depth / 2))
        q = where(sh, uf, c)
        if q is None:
            raise ValueError("the model's Ø%s hole at (%s) isn't on one flange" % (
                sheetmetal._f(h.dia), ", ".join(sheetmetal._f(x) for x in c)))
        holes_flat.append((q, h.dia))
    if fl.dxf.cut_loops() != 1:
        raise ValueError("its DXF cuts shapes inside its outline besides round holes")
    found, why = match(uf, fl.dxf, holes_flat, tol)
    if why:
        raise ValueError(why)
    # the outline too, both ways (it pins K: each flange beyond a bend moves by its allowance)
    polys = outline(sh, uf)
    kept, out_why = [], None
    for T_, pr_ in found:
        of = outline_fails(polys, T_, fl.dxf, tol)
        if of:
            out_why = out_why or of[0]
            continue
        kept.append((T_, pr_))
    if found and not kept:
        raise ValueError("its DXF's outline isn't where the model unfolds to at K %s: %s" % (sheetmetal._f(k), out_why))
    found = kept
    if not found:
        raise ValueError("its DXF's bend lines and holes don't sit where the model unfolds to at K %s (each within %s)"
                         % (sheetmetal._f(k), tol))
    # more than one placement fits: each must give the same part, so the DXF must map onto itself the way they differ
    for T2, _p in found[1:]:
        M, c = _relating(found[0][0], T2)
        if all(abs(M[i][j] - (1.0 if i == j else 0.0)) < 1e-6 for i in range(2) for j in range(2)) and \
                all(abs(x) <= 0.01 for x in c):
            continue
        bad = fl.dxf.off_symmetry((M, c), tol)
        if bad:
            raise ValueError("nothing pins which way up its DXF is drawn: no hole tells, and its flat isn't symmetric "
                             "(%s)" % bad)
    T, pairs = found[0]
    fl.readings = len(found)
    box = fl.dxf.cut_box()
    viewed_first = not T[0]         # a plain turn keeps the first skin's outside up
    rows = []
    for (b, line, zone, BA), dl in zip(uf.lines, pairs):
        p, q = _apply(T, line[0]), _apply(T, line[1])
        if p[1] > q[1] + 1e-9 or (abs(p[1] - q[1]) <= 1e-9 and p[0] > q[0]):
            p, q = q, p
        up = b.inside_first == viewed_first
        rows.append({"p": (p[0] - box[0], p[1] - box[1]), "q": (q[0] - box[0], q[1] - box[1]), "dir": "UP" if up else
                     "DOWN", "angle": math.degrees(b.angle), "r": b.r, "ba": BA, "line": dl,
                     "zone": [[_apply(T, z) for z in zone[0]], [_apply(T, z) for z in zone[1]]], "bend": b})
    rows.sort(key=lambda r_: (round((r_["p"][1] + r_["q"][1]) / 2, 3), round((r_["p"][0] + r_["q"][0]) / 2, 3)))
    for j, r_ in enumerate(rows):
        r_["tag"] = "B%d" % (j + 1)
        r_["axis"] = "any"
        r_["at"] = 0.0
    fl.rows = rows
    fl.k, fl.radius, fl.radius_from = k, sh.bends[0].r, (radius_from or "the model")
    fl.sheet, fl.unfolded, fl.T = sh, uf, T
    fl.viewed = "from the side the DXF shows"
    fl.holes_flat = holes_flat
    return fl


def record(fl):
    """The unfolding as plain numbers, for the read-back: the DXF's isometry, each flange's plane and map, each bend's
    zone edges, line and allowance (DXF coordinates)."""
    r3 = lambda v: [round(x, 9) for x in v]
    sh, uf = fl.sheet, fl.unfolded
    out = {"T": [bool(fl.T[0])] + [round(x, 12) for x in fl.T[1:]], "t": sh.t, "k": fl.k, "flanges": [], "bends": []}
    for f in sh.flanges:
        m = uf.maps[f.i]
        poly = []
        w = BRepTools.OuterWire_s(f.f)
        from OCP.BRepTools import BRepTools_WireExplorer
        ex = BRepTools_WireExplorer(w)
        while ex.More():
            c = BRepAdaptor_Curve(ex.Current())
            n = 1 if c.GetType() == GeomAbs_Line else 16
            for i in range(n):
                poly.append(r3(geom.pnt(c.Value(c.FirstParameter() + (c.LastParameter() - c.FirstParameter()) * i / n))))
            ex.Next()
        out["flanges"].append({"N": r3(f.normal), "o": vdot(f.centre, f.normal), "p0": r3(m.p0), "ex": r3(m.ex),
                               "ey": r3(m.ey), "c": [m.c[0], m.c[1]], "poly": poly})
    for r_ in fl.rows:
        b = r_["bend"]
        out["bends"].append({"tag": r_["tag"], "r": b.r, "angle": math.degrees(b.angle), "ba": r_["ba"],
                             "axis": r3(b.axis_d), "axis_p": r3(b.axis_p),
                             "zone": [[list(p) for p in z] for z in r_["zone"]]})
    return out


def unexplained(sh, holes):
    """Curved faces that are neither a bend's two cylinders nor a round hole's."""
    bendf = {b.face.i for b in sh.bends} | {b.twin.i for b in sh.bends}
    out = []
    for f in sh.faces:
        if f.kind == "plane" or f.i in bendf:
            continue
        if f.kind == "cylinder" and any(abs(h.dia / 2 - f.radius) < 1e-3 for h in holes):
            continue
        out.append("a cylinder r%.2f" % f.radius if f.kind == "cylinder" else "a curved face")
    return out
