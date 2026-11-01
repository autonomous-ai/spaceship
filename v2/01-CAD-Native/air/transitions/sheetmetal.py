"""Folded sheet metal parts for AIR's duct transitions (618102, 618103 replacements), built outside Fusion.

A part is a set of planar walls joined by folds. Each wall is given by its outer skin: a planar polygon in pod
coordinates (mm) and its outward normal; the sheet's material lies on the inner side, thickness t. A fold joins
two walls along a segment of the line where their outer skins meet (the virtual sharp). From that one definition
this module builds:

- the folded solid (OCC): each wall's flat part (its outer polygon trimmed back from each fold by the fold's
  tangent distance) extruded by t, and each fold as an exact cylindrical sector of inside radius r and outside
  radius r + t, fused into one solid;
- the developed flat pattern: each wall's flat part placed by unfolding the tree of folds, each fold's zone
  as wide as its bend allowance BA = angle x (r + K t), the neutral fibre at K t from the fold's inside skin.

Rules a wall must keep (checked): at both ends of a fold segment the wall's outline runs square to the fold
for at least the fold's tangent distance (a corner relief where two folds meet), so the flat part and the
fold's zone meet edge to edge.

Lengths in mm, angles in degrees unless named _rad. The flat is seen from the outer skin (the duct's outside):
a fold whose inside is the inner skin goes DOWN (away from the viewer), one whose inside is the outer skin UP.
"""

import math

import numpy as np

TOL = 1e-6


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise ValueError("zero vector")
    return v / n


def rot_about(axis_pt, axis_dir, ang_rad):
    """4x4 matrix rotating points by ang_rad about the line through axis_pt along axis_dir (right hand)."""
    k = unit(axis_dir)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    R = np.eye(3) + math.sin(ang_rad) * K + (1 - math.cos(ang_rad)) * (K @ K)
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = np.asarray(axis_pt, float) - R @ np.asarray(axis_pt, float)
    return M


def translate(v):
    M = np.eye(4)
    M[:3, 3] = np.asarray(v, float)
    return M


def apply(M, p):
    p = np.asarray(p, float)
    return (M[:3, :3] @ p) + M[:3, 3]


class Wall:
    """A planar wall: its outer skin polygon (3D points in order), its outward normal, and its holes (centre on
    the outer skin, diameter)."""

    def __init__(self, name, pts, n_out, holes=(), cutouts=()):
        self.name = name
        self.pts = [np.asarray(p, float) for p in pts]
        self.n = unit(n_out)
        self.holes = [(np.asarray(c, float), float(d)) for c, d in holes]
        self.cutouts = [[np.asarray(p, float) for p in poly] for poly in cutouts]   # straight-edged openings
        o = self.pts[0]
        for p in self.pts:
            if abs(np.dot(p - o, self.n)) > 1e-6:
                raise ValueError("wall %s isn't planar (a point is %.6f off its plane)" % (name, np.dot(p - o, self.n)))
        for c, _d in self.holes:
            if abs(np.dot(c - o, self.n)) > 1e-6:
                raise ValueError("a hole of wall %s isn't on its outer skin" % name)
        for poly in self.cutouts:
            for p in poly:
                if abs(np.dot(p - o, self.n)) > 1e-6:
                    raise ValueError("a cut-out of wall %s isn't on its outer skin" % name)
        if self.signed_area() <= 0:
            self.pts = self.pts[::-1]          # counter-clockwise seen from the outside

    def signed_area(self):
        s = np.zeros(3)
        for i in range(len(self.pts)):
            s += np.cross(self.pts[i], self.pts[(i + 1) % len(self.pts)])
        return 0.5 * float(np.dot(s, self.n))

    def centroid(self):
        return sum(self.pts) / len(self.pts)


class Fold:
    """A fold between walls a and b along the segment p0-p1 of their outer skins' common line."""

    def __init__(self, a, b, p0, p1, tag=None, r=None):
        self.a, self.b = a, b
        self.p0, self.p1 = np.asarray(p0, float), np.asarray(p1, float)
        self.tag = tag
        self.r = r                       # this fold's inside radius, when it isn't the part's (a vane's curve)


class Part:
    """A folded part: walls, folds (a tree), thickness t, inside radius r, K-factor k, the base wall's name."""

    def __init__(self, number, name, walls, folds, t, r, k, base, density, material, reliefs=()):
        self.number, self.name = number, name
        self.walls = {w.name: w for w in walls}
        self.folds = folds
        self.t, self.r, self.k = float(t), float(r), float(k)
        self.base = base
        self.density, self.material = density, material
        self.reliefs = reliefs
        self._analyse()
        self._tree()
        self._develop()

    # ------------------------------------------------------------------ each fold's geometry
    def _analyse(self):
        t, k = self.t, self.k
        for f in self.folds:
            r = f.r if f.r is not None else self.r
            f.rin = r
            A, B = self.walls[f.a], self.walls[f.b]
            L = f.p1 - f.p0
            f.length = float(np.linalg.norm(L))
            f.l = unit(L)
            for W in (A, B):
                for p in (f.p0, f.p1):
                    if abs(np.dot(p - W.pts[0], W.n)) > 1e-6:
                        raise ValueError("fold %s-%s: its segment isn't on wall %s's outer skin" % (f.a, f.b, W.name))
                if abs(np.dot(f.l, W.n)) > 1e-9:
                    raise ValueError("fold %s-%s: its line isn't in wall %s's plane" % (f.a, f.b, W.name))
            f.e = {}
            for W in (A, B):
                # into the wall: the polygon runs counter-clockwise about its normal, so its inside is left of the
                # edge that carries the fold (a centroid can sit outside an L-shaped wall)
                d_edge = self._edge_dir(W, f)
                f.e[W.name] = unit(np.cross(W.n, d_edge))
            eA, eB = f.e[A.name], f.e[B.name]
            f.theta_rad = math.acos(max(-1.0, min(1.0, -float(np.dot(eA, eB)))))
            if f.theta_rad < 1e-4:
                raise ValueError("fold %s-%s has no angle" % (f.a, f.b))
            f.theta = math.degrees(f.theta_rad)
            f.concave = float(np.dot(eB, A.n)) > 0          # the outer skin is the fold's inside
            f.rho_out = r if f.concave else r + t            # the outer skin's arc radius
            f.dt = f.rho_out * math.tan(f.theta_rad / 2)      # tangent distance from the virtual sharp, on each wall
            f.ba = f.theta_rad * (r + k * t)
            tA = f.p0 + eA * f.dt
            f.centre = tA + (A.n if f.concave else -A.n) * f.rho_out
            f.axis_dir = unit(np.cross(A.n, B.n))
            if np.dot(f.axis_dir, f.l) < 0:
                f.axis_dir = f.axis_dir          # direction of rotation is fixed below, the line is what matters
            # the radial direction at A's tangent and the rotation that carries it to B's
            f.rad_a = A.n if not f.concave else -A.n
            f.rad_b = B.n if not f.concave else -B.n
            s = float(np.dot(np.cross(f.rad_a, f.rad_b), f.l))
            f.rot_sign = 1.0 if s >= 0 else -1.0
            # check: the centre is rho_out from both outer planes and B's tangent point is where it should be
            for W in (A, B):
                dpl = abs(float(np.dot(f.centre - W.pts[0], W.n)))
                if abs(dpl - f.rho_out) > 1e-6:
                    raise ValueError("fold %s-%s: centre %.6f off wall %s's plane, not %.6f" % (
                        f.a, f.b, dpl, W.name, f.rho_out))

    @staticmethod
    def _edge_dir(W, f):
        """The direction, in the wall's own (counter-clockwise) order, of the polygon edge holding the fold."""
        n = len(W.pts)
        for i in range(n):
            a, b = W.pts[i], W.pts[(i + 1) % n]
            d = b - a
            L = float(np.linalg.norm(d))
            if L < 1e-9:
                continue
            u = d / L
            if all(np.linalg.norm(np.cross(p - a, u)) < 1e-6 and -1e-6 <= float(np.dot(p - a, u)) <= L + 1e-6
                   for p in (f.p0, f.p1)):
                return u
        raise ValueError("fold %s-%s isn't on an edge of wall %s" % (f.a, f.b, W.name))

    # ------------------------------------------------------------------ the tree from the base wall
    def _tree(self):
        seen = {self.base}
        order, parent = [self.base], {}
        todo = [self.base]
        while todo:
            w = todo.pop(0)
            for f in self.folds:
                for x, y in ((f.a, f.b), (f.b, f.a)):
                    if x == w and y not in seen:
                        seen.add(y)
                        parent[y] = (x, f)
                        order.append(y)
                        todo.append(y)
        if len(seen) != len(self.walls):
            raise ValueError("walls not joined to the base: %s" % sorted(set(self.walls) - seen))
        used = {id(f) for _w, (_p, f) in parent.items()}
        if len(used) != len(self.folds):
            raise ValueError("the folds make a loop; a closed part can't be developed")
        self.order, self.parent = order, parent

    # ------------------------------------------------------------------ trimmed walls and the flat
    def trimmed(self, wname):
        """The wall's flat part: its outer polygon with each fold edge moved in by the fold's tangent distance."""
        W = self.walls[wname]
        pts = [p.copy() for p in W.pts]
        n = len(pts)
        for f in self.folds:
            if wname not in (f.a, f.b):
                continue
            hit = None
            for i in range(n):
                a, b = W.pts[i], W.pts[(i + 1) % n]
                for u, v in ((f.p0, f.p1), (f.p1, f.p0)):
                    if np.linalg.norm(a - u) < 1e-6 and np.linalg.norm(b - v) < 1e-6:
                        hit = i
            if hit is None:
                raise ValueError("fold %s-%s isn't an edge of wall %s" % (f.a, f.b, wname))
            e = f.e[wname]
            for j, nb in ((hit, (hit - 1) % n), ((hit + 1) % n, (hit + 2) % n)):
                d = W.pts[nb] - W.pts[j]
                if abs(float(np.dot(unit(d), f.l))) > 1e-6:
                    raise ValueError("wall %s: the outline at fold %s-%s's end isn't square to the fold (needs a "
                                     "relief)" % (wname, f.a, f.b))
                if float(np.linalg.norm(d)) < f.dt + 1e-6:
                    raise ValueError("wall %s: the edge beside fold %s-%s is shorter than the tangent distance "
                                     "%.3f" % (wname, f.a, f.b, f.dt))
                pts[j] = W.pts[j] + e * f.dt
        return pts

    def _develop(self):
        """Each wall's map from 3D to the flat (a 4x4 whose result's z is 0 on the outer skin)."""
        B = self.walls[self.base]
        o = B.pts[0]
        x = unit(B.pts[1] - B.pts[0])
        y = np.cross(B.n, x)
        M = np.eye(4)
        M[0, :3], M[1, :3], M[2, :3] = x, y, B.n
        M[:3, 3] = -M[:3, :3] @ o
        self.map = {self.base: M}
        for w in self.order[1:]:
            p, f = self.parent[w]
            A, W = self.walls[p], self.walls[w]
            # unfold W about the virtual sharp line so its outer normal meets A's, then open the gap to BA
            ang = math.atan2(float(np.dot(np.cross(W.n, A.n), f.l)), float(np.dot(W.n, A.n)))
            R = rot_about(f.p0, f.l, ang)
            if np.linalg.norm(R[:3, :3] @ W.n - A.n) > 1e-9:
                raise ValueError("unfolding %s failed" % w)
            shift = -f.e[A.name] * (f.ba - 2 * f.dt)
            self.map[w] = self.map[p] @ translate(shift) @ R
        for w in self.order:
            for q in self.walls[w].pts:
                z = apply(self.map[w], q)[2]
                if abs(z) > 1e-6:
                    raise ValueError("wall %s doesn't develop flat (z %.6f)" % (w, z))

    def flat_regions(self):
        """[(kind, name, [(x, y)])]: each wall's flat part and each fold's zone, in the flat."""
        out = []
        for w in self.order:
            pts = [apply(self.map[w], q)[:2] for q in self.trimmed(w)]
            out.append(("wall", w, pts))
        for f in self.folds:
            pa = self._zone_edge(f, f.a)
            pb = self._zone_edge(f, f.b)
            out.append(("zone", f.tag or "%s-%s" % (f.a, f.b), [pa[0], pa[1], pb[1], pb[0]]))
        return out

    def _zone_edge(self, f, wname):
        e = f.e[wname]
        return [apply(self.map[wname], f.p0 + e * f.dt)[:2], apply(self.map[wname], f.p1 + e * f.dt)[:2]]

    def bend_lines(self):
        """[(tag, (x0, y0), (x1, y1), angle, direction, ba, zone edge a, zone edge b)] in the flat."""
        out = []
        for i, f in enumerate(self.folds):
            ea, eb = self._zone_edge(f, f.a), self._zone_edge(f, f.b)
            gap = abs(float(np.cross(np.append(ea[1] - ea[0], 0), np.append(eb[0] - ea[0], 0))[2])) / \
                np.linalg.norm(ea[1] - ea[0])
            if abs(gap - f.ba) > 1e-6:
                raise ValueError("fold %s: its zone is %.6f wide, not BA %.6f" % (f.tag, gap, f.ba))
            c0, c1 = (ea[0] + eb[0]) / 2, (ea[1] + eb[1]) / 2
            out.append((f.tag or "F%d" % (i + 1), c0, c1, f.theta, "UP" if f.concave else "DOWN", f.ba, ea, eb))
        return out

    def flat_cutouts(self):
        """The walls' straight-edged openings in the flat: [[(x, y)]]."""
        out = []
        for w in self.order:
            for poly in self.walls[w].cutouts:
                out.append([apply(self.map[w], p)[:2] for p in poly])
        return out

    def flat_holes(self):
        out = []
        for w in self.order:
            for c, d in self.walls[w].holes:
                out.append((apply(self.map[w], c)[:2], d))
        return out

    # ------------------------------------------------------------------ the folded solid
    def solid(self):
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
        from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
        from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Vec, gp_Circ, gp_Ax2
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCP.TopTools import TopTools_ListOfShape
        from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

        def poly_face(pts, holes=(), normal=None, cutouts=()):
            mp = BRepBuilderAPI_MakePolygon()
            for p in pts:
                mp.Add(gp_Pnt(*map(float, p)))
            mp.Close()
            mf = BRepBuilderAPI_MakeFace(mp.Wire(), True)
            for c, d in holes:
                circ = gp_Circ(gp_Ax2(gp_Pnt(*map(float, c)), gp_Dir(*map(float, normal))), d / 2)
                w = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circ).Edge()).Wire()
                w.Reverse()
                mf.Add(w)
            for poly in cutouts:
                mp2 = BRepBuilderAPI_MakePolygon()
                for p in poly:
                    mp2.Add(gp_Pnt(*map(float, p)))
                mp2.Close()
                w = mp2.Wire()
                # an inner wire runs clockwise seen from the face's normal
                s2 = np.zeros(3)
                for i in range(len(poly)):
                    s2 += np.cross(poly[i], poly[(i + 1) % len(poly)])
                if float(np.dot(s2, normal)) > 0:
                    w.Reverse()
                mf.Add(w)
            return mf.Face()

        pieces = []
        self.piece_volumes = []
        for w in self.order:
            W = self.walls[w]
            face = poly_face(self.trimmed(w), W.holes, W.n, W.cutouts)
            prism = BRepPrimAPI_MakePrism(face, gp_Vec(*map(float, -W.n * self.t))).Shape()
            pieces.append(prism)
        for f in self.folds:
            c0 = f.centre
            # the start face: the radial strip from radius r to r + t at A's tangent, along the fold
            a0 = c0 + f.rad_a * f.rin
            a1 = c0 + f.rad_a * (f.rin + self.t)
            b0 = a0 + (f.p1 - f.p0)
            b1 = a1 + (f.p1 - f.p0)
            face = poly_face([a0, a1, b1, b0])
            ax = gp_Ax1(gp_Pnt(*map(float, c0)), gp_Dir(*map(float, f.l * f.rot_sign)))
            pieces.append(BRepPrimAPI_MakeRevol(face, ax, f.theta_rad).Shape())
        fuse = BRepAlgoAPI_Fuse()
        args, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
        args.Append(pieces[0])
        for p in pieces[1:]:
            tools.Append(p)
        fuse.SetArguments(args)
        fuse.SetTools(tools)
        fuse.SetFuzzyValue(1e-6)
        fuse.Build()
        if not fuse.IsDone():
            raise RuntimeError("fuse failed for %s" % self.name)
        u = ShapeUpgrade_UnifySameDomain(fuse.Shape(), True, True, True)
        u.Build()
        return u.Shape()

    def expected_volume(self):
        """mm3 from the definition: each flat part's area x t, each fold's sector."""
        v = 0.0
        for w in self.order:
            pts = self.trimmed(w)
            s = np.zeros(3)
            for i in range(len(pts)):
                s += np.cross(pts[i], pts[(i + 1) % len(pts)])
            area = 0.5 * abs(float(np.dot(s, self.walls[w].n)))
            area -= sum(math.pi * d * d / 4 for _c, d in self.walls[w].holes)
            for poly in self.walls[w].cutouts:
                s2 = np.zeros(3)
                for i in range(len(poly)):
                    s2 += np.cross(poly[i], poly[(i + 1) % len(poly)])
                area -= 0.5 * abs(float(np.dot(s2, self.walls[w].n)))
            v += area * self.t
        for f in self.folds:
            v += 0.5 * f.theta_rad * ((f.rin + self.t) ** 2 - f.rin ** 2) * f.length
        return v


# ---------------------------------------------------------------------- outputs
def solid_checks(shape):
    """(number of solids, valid, volume mm3, (xmin, ymin, zmin, xmax, ymax, zmax))."""
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    n = 0
    e = TopExp_Explorer(shape, TopAbs_SOLID)
    while e.More():
        n += 1
        e.Next()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    b = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, b, False, False)
    p, q = b.CornerMin(), b.CornerMax()
    return n, BRepCheck_Analyzer(shape).IsValid(), props.Mass(), (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())


def write_step(shapes, path, title):
    """Write [(product name, shape)] as one STEP (mm), each a named product under a root named title; the
    header's author and organisation stay empty (the owner's rule: no names in files)."""
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.STEPControl import STEPControl_AsIs
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString, TCollection_HAsciiString
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from OCP.TDataStd import TDataStd_Name
    from OCP.APIHeaderSection import APIHeaderSection_MakeHeader
    from OCP.Interface import Interface_Static
    from OCP.IFSelect import IFSelect_RetDone
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    if len(shapes) == 1:
        lab = st.AddShape(shapes[0][1], False)
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(shapes[0][0]))
    else:
        from OCP.TopoDS import TopoDS_Compound
        from OCP.BRep import BRep_Builder
        comp = TopoDS_Compound()
        bb = BRep_Builder()
        bb.MakeCompound(comp)
        root = st.NewShape()
        TDataStd_Name.Set_s(root, TCollection_ExtendedString(title))
        from OCP.TopLoc import TopLoc_Location
        for nm, sh in shapes:
            sub = st.AddShape(sh, False)
            TDataStd_Name.Set_s(sub, TCollection_ExtendedString(nm))
            comp_lab = st.AddComponent(root, sub, TopLoc_Location())
            TDataStd_Name.Set_s(comp_lab, TCollection_ExtendedString(nm))
        st.UpdateAssemblies()
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS")
    Interface_Static.SetCVal_s("write.step.product.name", title)
    w = STEPCAFControl_Writer()
    w.SetNameMode(True)
    if not w.Transfer(doc, STEPControl_AsIs):
        raise RuntimeError("STEP transfer failed")
    model = w.ChangeWriter().Model()
    h = APIHeaderSection_MakeHeader(model)
    h.SetName(TCollection_HAsciiString(path.split("/")[-1]))
    h.SetAuthorValue(1, TCollection_HAsciiString(""))
    h.SetOrganizationValue(1, TCollection_HAsciiString(""))
    h.SetOriginatingSystem(TCollection_HAsciiString("Open CASCADE 7.8 (AIR transitions script)"))
    h.SetAuthorisation(TCollection_HAsciiString(""))
    h.SetDescriptionValue(1, TCollection_HAsciiString(title))
    if w.Write(path) != IFSelect_RetDone:
        raise RuntimeError("STEP write failed: %s" % path)


def flat_outline(regions):
    """The flat's outline loops [[(x, y)]] (outer first), from the union of its regions (OCC 2D boolean)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE, TopAbs_WIRE
    from OCP.BRepTools import BRepTools_WireExplorer, BRepTools
    from OCP.BRep import BRep_Tool
    from OCP.TopoDS import TopoDS
    from OCP.gp import gp_Pnt
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    sew = BRepBuilderAPI_Sewing(1e-6)
    for _k, _n, pts in regions:
        mp = BRepBuilderAPI_MakePolygon()
        for p in pts:
            mp.Add(gp_Pnt(float(p[0]), float(p[1]), 0.0))
        mp.Close()
        sew.Add(BRepBuilderAPI_MakeFace(mp.Wire(), True).Face())
    sew.Perform()          # the regions meet edge to edge: sew them, then merge into one face
    u = ShapeUpgrade_UnifySameDomain(sew.SewedShape(), True, True, True)
    u.Build()
    sh = u.Shape()
    loops = []
    e = TopExp_Explorer(sh, TopAbs_FACE)
    nf = 0
    while e.More():
        nf += 1
        face = TopoDS.Face_s(e.Current())
        outer = BRepTools.OuterWire_s(face)
        we = TopExp_Explorer(face, TopAbs_WIRE)
        while we.More():
            wire = TopoDS.Wire_s(we.Current())
            ex = BRepTools_WireExplorer(wire, face)
            pts = []
            while ex.More():
                v = BRep_Tool.Pnt_s(ex.CurrentVertex())
                pts.append((v.X(), v.Y()))
                ex.Next()
            if wire.IsSame(outer):
                loops.insert(0, pts)
            else:
                loops.append(pts)
            we.Next()
        e.Next()
    if nf != 1:
        raise ValueError("the flat isn't one piece (%d faces)" % nf)
    return loops


def write_dxf(path, loops, holes, bends, cutouts=()):
    """An ASCII DXF (R12 entities, $INSUNITS 4 = mm): the outline and holes on CUT, each fold's centre line on
    BEND and its zone's two edges on MARK."""
    out = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4",
           "9", "$MEASUREMENT", "70", "1", "0", "ENDSEC",
           "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "3"]
    for name, col in (("CUT", 7), ("BEND", 1), ("MARK", 3)):
        out += ["0", "LAYER", "2", name, "70", "0", "62", str(col), "6", "CONTINUOUS"]
    out += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]

    def line(layer, a, b):
        return ["0", "LINE", "8", layer, "10", "%.6f" % a[0], "20", "%.6f" % a[1], "30", "0.0",
                "11", "%.6f" % b[0], "21", "%.6f" % b[1], "31", "0.0"]
    for lp in loops:
        for i in range(len(lp)):
            out += line("CUT", lp[i], lp[(i + 1) % len(lp)])
    for poly in cutouts:
        for i in range(len(poly)):
            out += line("CUT", poly[i], poly[(i + 1) % len(poly)])
    for c, d in holes:
        out += ["0", "CIRCLE", "8", "CUT", "10", "%.6f" % c[0], "20", "%.6f" % c[1], "30", "0.0", "40", "%.6f" % (d / 2)]
    for _tag, c0, c1, _ang, _dir, _ba, ea, eb in bends:
        out += line("BEND", c0, c1)
        out += line("MARK", ea[0], ea[1])
        out += line("MARK", eb[0], eb[1])
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(out) + "\n")
