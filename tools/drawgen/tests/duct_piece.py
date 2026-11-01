"""A test duct piece: a trapezoid base with three folds on three non-parallel edges (90 deg with a hole, 60 deg
tapering, 30 deg kink), inside radius 1 = t, and its flat worked by hand at K 0.44."""
import math

T, R, K = 1.0, 1.0, 0.44
BASE = [(0.0, 0.0), (300.0, 0.0), (260.0, 200.0), (40.0, 200.0)]
# edge index, angle (deg), s0, s1 (along the edge from its start), the tab's outer edge from its u=0 side to u=W side,
# holes in tab coordinates (u along the edge from s0, v out from the bend), diameter
def tabs():
    L = lambda i: math.dist(BASE[i], BASE[(i + 1) % 4])
    out = []
    w0 = 260.0
    out.append((0, 90.0, 20.0, 280.0, [(0.0, 40.0), (w0, 40.0)], [((60.0, 20.0), 8.0)]))
    l1 = L(1)
    out.append((1, 60.0, 15.0, l1 - 15.0, [(10.0, 30.0), (l1 - 30.0 - 10.0, 30.0)], []))
    l3 = L(3)
    out.append((3, 30.0, 15.0, l3 - 15.0, [(0.0, 25.0), (l3 - 30.0, 25.0)], []))
    return out


def edge_frame(i):
    P, Q = BASE[i], BASE[(i + 1) % 4]
    L = math.dist(P, Q)
    X = ((Q[0] - P[0]) / L, (Q[1] - P[1]) / L)
    W = (X[1], -X[0])          # outward: the base (counter-clockwise) is on the left
    return P, X, W, L


def build_step(path):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec

    def prism(pts, v):
        poly = BRepBuilderAPI_MakePolygon()
        for q in pts:
            poly.Add(gp_Pnt(*q))
        poly.Close()
        return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(*v)).Shape()

    def fuse(a, b):
        f = BRepAlgoAPI_Fuse(a, b)
        f.SetFuzzyValue(1e-6)
        f.Build()
        return f.Shape()

    def cut(a, b):
        c = BRepAlgoAPI_Cut(a, b)
        c.Build()
        return c.Shape()
    shape = prism([(x, y, 0.0) for x, y in BASE], (0, 0, T))
    holes = []
    for i, ang, s0, s1, outer, hs in tabs():
        P, X, W, L = edge_frame(i)
        th = math.radians(ang)
        X3, W3, Z3 = (X[0], X[1], 0.0), (W[0], W[1], 0.0), (0.0, 0.0, 1.0)
        g = lambda x, y, z: (P[0] + x * X[0] + y * W[0], P[1] + x * X[1] + y * W[1], z)
        ax0 = g(s0, 0.0, T + R)                     # the bend's axis at s0 (above the edge, inner radius R up)
        rho = tuple(-math.cos(th) * Z3[k] + math.sin(th) * W3[k] for k in range(3))
        d = tuple(math.cos(th) * W3[k] + math.sin(th) * Z3[k] for k in range(3))
        # the sweep from straight down toward the outside: the cylinder's frame runs back along the edge from s1,
        # so its second axis (main x first) is the outward one
        ax1 = g(s1, 0.0, T + R)
        a2 = gp_Ax2(gp_Pnt(*ax1), gp_Dir(-X3[0], -X3[1], 0.0), gp_Dir(0, 0, -1))
        outer_pie = BRepPrimAPI_MakeCylinder(a2, R + T, s1 - s0, th).Shape()
        inner_pie = BRepPrimAPI_MakeCylinder(a2, R, s1 - s0, th).Shape()
        shape = fuse(shape, cut(outer_pie, inner_pie))
        Wt = s1 - s0
        tab_uv = [(0.0, 0.0)] + outer + [(Wt, 0.0)]
        pts = []
        for u, v in tab_uv:
            pts.append(tuple(ax0[k] + u * X3[k] + R * rho[k] + v * d[k] for k in range(3)))
        shape = fuse(shape, prism(pts, tuple(T * c for c in rho)))
        for (u, v), dia in hs:
            c = tuple(ax0[k] + u * X3[k] + (R - T) * rho[k] + v * d[k] for k in range(3))
            holes.append(BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*c), gp_Dir(*rho)), dia / 2, 3 * T).Shape())
    for h in holes:
        shape = cut(shape, h)
    u = ShapeUpgrade_UnifySameDomain(shape, True, True, True)
    u.Build()
    w = STEPControl_Writer()
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 0)
    w.Transfer(u.Shape(), STEPControl_AsIs)
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 1)
    assert w.Write(path) == IFSelect_RetDone
    return path


def flat():
    """The flat by hand: outline, bend lines, holes (the base's top face's x, y)."""
    outline, bends, holes = [], [], []
    tb = {i: (i, ang, s0, s1, outer, hs) for i, ang, s0, s1, outer, hs in tabs()}
    for i in range(4):
        P, X, W, L = edge_frame(i)
        q = lambda s, o: (P[0] + s * X[0] + o * W[0], P[1] + s * X[1] + o * W[1])
        outline.append(q(0.0, 0.0))
        if i in tb:
            _i, ang, s0, s1, outer, hs = tb[i]
            BA = math.radians(ang) * (R + K * T)
            outline.append(q(s0, 0.0))
            outline.append(q(s0, BA))
            for u, v in outer:
                outline.append(q(s0 + u, BA + v))
            outline.append(q(s1, BA))
            outline.append(q(s1, 0.0))
            bends.append((q(s0, BA / 2), q(s1, BA / 2), ang))
            for (u, v), dia in hs:
                holes.append((q(s0 + u, BA + v), dia))
    return outline, bends, holes


def write_dxf(path, move=None):
    outline, bends, holes = flat()
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for i, p in enumerate(outline):
        q = outline[(i + 1) % len(outline)]
        out += ["0", "LINE", "8", "CUT", "10", repr(p[0]), "20", repr(p[1]), "11", repr(q[0]), "21", repr(q[1])]
    for p, q, _a in bends:
        out += ["0", "LINE", "8", "BEND", "10", repr(p[0]), "20", repr(p[1]), "11", repr(q[0]), "21", repr(q[1])]
    for (c, dia) in holes:
        cx, cy = c
        if move:
            cx += move
        out += ["0", "CIRCLE", "8", "CUT", "10", repr(cx), "20", repr(cy), "40", repr(dia / 2)]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    return path
