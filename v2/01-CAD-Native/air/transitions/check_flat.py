"""Develop a folded part's flat from its STEP alone, and check its DXF against it.

Independent of sheetmetal.py (which builds both the STEP and the DXF from one definition): this reads only the
STEP's faces. One skin is the faces reached from the largest plane across tangent edges (planes and the fold
cylinders); the other skin is the rest of the large faces, and the thin faces are the sheet's edges. Each fold
is a pair of coaxial cylinders whose radii differ by the thickness: the smaller is the inside radius r. The skin
is unrolled: each plane rigidly, each fold as a strip as wide as its bend allowance angle x (r + K t), the
neutral fibre at K t from the fold's inside. The developed outline, fold centre lines, zone edges and holes must
match the DXF's CUT, BEND and MARK layers within 0.01 mm after one rigid move (or a mirror, when the DXF shows
the other skin); the K-factor each zone in the DXF implies must be the given K.

Usage: python check_flat.py PART.step PART.dxf [--k 0.44]   (prints PASS or the faults; exit 1 on a fault)
"""

import argparse
import math
import sys

import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Cylinder, GeomAbs_Line, GeomAbs_Plane
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID, TopAbs_WIRE
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS

TOL = 0.01


def read_solid(path):
    r = STEPControl_Reader()
    if r.ReadFile(path) != IFSelect_RetDone:
        raise SystemExit("can't read %s" % path)
    r.TransferRoots()
    sh = r.OneShape()
    solids = []
    e = TopExp_Explorer(sh, TopAbs_SOLID)
    while e.More():
        solids.append(e.Current())
        e.Next()
    if len(solids) != 1:
        raise SystemExit("%s holds %d solids, not one part" % (path, len(solids)))
    return solids[0]


def v3(p):
    return np.array([p.X(), p.Y(), p.Z()])


class Face:
    def __init__(self, idx, f):
        self.idx, self.f = idx, f
        s = BRepAdaptor_Surface(f, True)
        self.kind = {GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cyl"}.get(s.GetType(), "other")
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(f, props)
        self.area = props.Mass()
        rev = f.Orientation() == TopAbs_REVERSED
        if self.kind == "plane":
            pl = s.Plane()
            n = v3(pl.Axis().Direction())
            self.n = -n if rev else n               # outward normal of the solid
            self.p = v3(pl.Location())
        elif self.kind == "cyl":
            c = s.Cylinder()
            self.axis_p, self.axis_d, self.rad = v3(c.Axis().Location()), v3(c.Axis().Direction()), c.Radius()
            self.u0, self.u1 = s.FirstUParameter(), s.LastUParameter()
            self.v0, self.v1 = s.FirstVParameter(), s.LastVParameter()
            self.rev = rev


def faces_and_edges(solid):
    fmap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(solid, TopAbs_FACE, fmap)
    faces = [Face(i, TopoDS.Face_s(fmap.FindKey(i))) for i in range(1, fmap.Extent() + 1)]
    emap = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(solid, TopAbs_EDGE, TopAbs_FACE, emap)
    adj = []
    for i in range(1, emap.Extent() + 1):
        edge = TopoDS.Edge_s(emap.FindKey(i))
        ids = []
        it = emap.FindFromIndex(i)
        for fs in it:
            ids.append(fmap.FindIndex(fs) - 1)
        ids = sorted(set(ids))
        if len(ids) == 2:
            adj.append((ids[0], ids[1], edge))
    return faces, adj


def normal_at(face, pt):
    """The solid's outward normal of a plane or cylinder face at a point on it."""
    if face.kind == "plane":
        return face.n
    d = pt - face.axis_p
    d = d - np.dot(d, face.axis_d) * face.axis_d
    n = d / np.linalg.norm(d)
    # a cylinder face's outward normal points away from the axis unless the face is reversed
    return -n if face.rev else n


def edge_mid(edge):
    c = BRepAdaptor_Curve(edge)
    return v3(c.Value((c.FirstParameter() + c.LastParameter()) / 2))


def skins(faces, adj):
    """Two sets of face indices: the skin with the largest plane, and the other skin (each reached across
    tangent edges); the rest are the sheet's edge faces."""
    tangent = {}
    for a, b, e in adj:
        m = edge_mid(e)
        if abs(abs(float(np.dot(normal_at(faces[a], m), normal_at(faces[b], m)))) - 1) < 1e-6:
            tangent.setdefault(a, set()).add(b)
            tangent.setdefault(b, set()).add(a)

    def grow(start):
        seen, todo = {start}, [start]
        while todo:
            x = todo.pop()
            for y in tangent.get(x, ()):
                if y not in seen and faces[y].kind in ("plane", "cyl"):
                    seen.add(y)
                    todo.append(y)
        return seen
    planes = sorted([f for f in faces if f.kind == "plane"], key=lambda f: -f.area)
    a = grow(planes[0].idx - 1)
    other = [f for f in planes if (f.idx - 1) not in a]
    # the other skin: the plane parallel and opposite to the largest one
    p0 = planes[0]
    cand = [f for f in other if float(np.dot(f.n, p0.n)) < -1 + 1e-9]
    if not cand:
        raise SystemExit("can't find the second skin")
    b = grow(max(cand, key=lambda f: f.area).idx - 1)
    return a, b


def thickness(faces, skin_a, skin_b):
    pa = max((faces[i] for i in skin_a if faces[i].kind == "plane"), key=lambda f: f.area)
    best = None
    for i in skin_b:
        f = faces[i]
        if f.kind == "plane" and float(np.dot(f.n, pa.n)) < -1 + 1e-9:
            d = abs(float(np.dot(f.p - pa.p, pa.n)))
            best = d if best is None else min(best, d)
    return best


def rot_about(pt, d, ang):
    d = d / np.linalg.norm(d)
    K = np.array([[0, -d[2], d[1]], [d[2], 0, -d[0]], [-d[1], d[0], 0]])
    R = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = pt - R @ pt
    return M


def tr(v):
    M = np.eye(4)
    M[:3, 3] = v
    return M


def ap(M, p):
    return M[:3, :3] @ p + M[:3, 3]


def develop(faces, adj, skin, t, k):
    """Unroll one skin: {face index: 4x4 to the flat (z = 0)} for its planes, and its folds as
    [(cylinder face, parent plane, child plane, r, angle_rad, zone in the flat [4 points], centre line)]."""
    edges_of = {}
    for a, b, e in adj:
        edges_of.setdefault(a, []).append((b, e))
        edges_of.setdefault(b, []).append((a, e))
    base = max((faces[i] for i in skin if faces[i].kind == "plane"), key=lambda f: f.area)
    # the flat's frame on the base plane: x along its longest straight edge
    best = None
    for _o, e in edges_of[base.idx - 1]:
        c = BRepAdaptor_Curve(e)
        if c.GetType() == GeomAbs_Line:
            a, b = v3(c.Value(c.FirstParameter())), v3(c.Value(c.LastParameter()))
            if best is None or np.linalg.norm(b - a) > np.linalg.norm(best[1] - best[0]):
                best = (a, b)
    x = (best[1] - best[0]) / np.linalg.norm(best[1] - best[0])
    z = base.n
    y = np.cross(z, x)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = x, y, z
    M[:3, 3] = -M[:3, :3] @ best[0]
    maps = {base.idx - 1: M}
    folds = []
    todo = [base.idx - 1]
    cyl_parent = {}
    while todo:
        pi = todo.pop()
        P = faces[pi]
        for ci, e in edges_of[pi]:
            if ci not in skin or faces[ci].kind != "cyl" or ci in cyl_parent:
                continue
            C = faces[ci]
            # the plane on the cylinder's far side
            far = [(oi, oe) for oi, oe in edges_of[ci] if oi in skin and oi != pi and faces[oi].kind == "plane"]
            if len(far) != 1:
                raise SystemExit("a fold cylinder doesn't join two planes of one skin")
            qi, qe = far[0]
            Q = faces[qi]
            cyl_parent[ci] = pi
            ang = math.acos(max(-1.0, min(1.0, float(np.dot(P.n, Q.n)))))
            # the inside radius: this skin's cylinder radius, or that less the thickness
            partner = [f for f in faces if f.kind == "cyl" and f.idx - 1 != ci and
                       abs(abs(float(np.dot(f.axis_d, C.axis_d))) - 1) < 1e-9 and
                       np.linalg.norm(np.cross(f.axis_p - C.axis_p, C.axis_d)) < 1e-6]
            radii = sorted({round(C.rad, 6)} | {round(f.rad, 6) for f in partner})
            r = radii[0]
            if len(radii) != 2 or abs(radii[1] - radii[0] - t) > 1e-4:
                raise SystemExit("a fold's two cylinders aren't t apart (%s)" % radii)
            # the tangent line on P and the direction from P across the fold, in P's plane
            m = edge_mid(e)
            axis = C.axis_d / np.linalg.norm(C.axis_d)
            foot = C.axis_p + np.dot(m - C.axis_p, axis) * axis
            out = np.cross(axis, P.n)
            # out must point from P's interior toward the fold: away from P's centroid
            props = GProp_GProps()
            BRepGProp.SurfaceProperties_s(P.f, props)
            pc = v3(props.CentreOfMass())
            if np.dot(m - pc, out) < 0:
                out = -out
            # rotate Q back by the fold's angle about the axis, so its plane meets P's again
            Rq = rot_about(foot, axis, ang)
            if np.linalg.norm(Rq[:3, :3] @ Q.n - P.n) > 1e-6:
                Rq = rot_about(foot, axis, -ang)
            if np.linalg.norm(Rq[:3, :3] @ Q.n - P.n) > 1e-6:
                raise SystemExit("can't unroll a fold")
            # after the rotation Q's tangent line sits on P's: open the zone to the bend allowance, along out
            ba = ang * (r + k * t)
            maps[qi] = maps[pi] @ tr(out * ba) @ Rq
            # the zone in the flat: P's tangent line and that line moved by ba along out
            le = BRepAdaptor_Curve(e)
            a, b = v3(le.Value(le.FirstParameter())), v3(le.Value(le.LastParameter()))
            za, zb = ap(maps[pi], a)[:2], ap(maps[pi], b)[:2]
            o2 = (maps[pi][:3, :3] @ out)[:2]
            zone = [za, zb, zb + o2 * ba, za + o2 * ba]
            folds.append(dict(cyl=ci, parent=pi, child=qi, r=r, ang=ang, ba=ba, zone=zone,
                              centre=(za + o2 * ba / 2, zb + o2 * ba / 2), concave_on_skin=None))
            todo.append(qi)
    planes = [i for i in skin if faces[i].kind == "plane"]
    missing = [i for i in planes if i not in maps]
    if missing:
        raise SystemExit("%d planes of the skin weren't reached by unrolling" % len(missing))
    return maps, folds


def face_loops_2d(face, M):
    """A skin plane's wires in the flat: (outer loop points, [inner straight-edged loops], [(circle centre, radius)])."""
    from OCP.BRepTools import BRepTools, BRepTools_WireExplorer
    outer_w = BRepTools.OuterWire_s(face.f)
    outer, inner, circles = None, [], []
    e = TopExp_Explorer(face.f, TopAbs_WIRE)
    while e.More():
        w = TopoDS.Wire_s(e.Current())
        pts, circ_here = [], []
        ex = BRepTools_WireExplorer(w, face.f)
        while ex.More():
            c = BRepAdaptor_Curve(ex.Current())
            if c.GetType() == GeomAbs_Circle and abs(c.LastParameter() - c.FirstParameter() - 2 * math.pi) < 1e-9:
                circ = c.Circle()
                circ_here.append((ap(M, v3(circ.Location()))[:2], circ.Radius()))
            elif c.GetType() == GeomAbs_Line:
                pts.append(ap(M, v3(BRep_Tool.Pnt_s(ex.CurrentVertex())))[:2])
            else:
                raise SystemExit("a skin plane has an edge that is neither a line nor a full circle")
            ex.Next()
        if w.IsSame(outer_w):
            outer = pts
        elif pts:
            inner.append(pts)
        circles += circ_here
        e.Next()
    return outer, inner, circles


def developed(step_path, k):
    solid = read_solid(step_path)
    faces, adj = faces_and_edges(solid)
    if any(f.kind == "other" for f in faces):
        raise SystemExit("the part has faces that are neither planes nor cylinders")
    sa, sb = skins(faces, adj)
    t = thickness(faces, sa, sb)
    maps, folds = develop(faces, adj, sa, t, k)
    regions, holes, cutouts = [], [], []
    for i, M in maps.items():
        outer, inner, circles = face_loops_2d(faces[i], M)
        regions.append(outer)
        cutouts += inner
        holes += [(c, rad * 2) for c, rad in circles]
    for fd in folds:
        regions.append([tuple(p) for p in fd["zone"]])
    return dict(t=t, folds=folds, regions=regions, holes=holes, cutouts=cutouts, faces=faces, skin=sa)


def outline_of(regions):
    """The union of the developed regions as segments (OCC sewing and unify, as the builder's flat)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_Sewing
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.gp import gp_Pnt
    sew = BRepBuilderAPI_Sewing(1e-5)
    for pts in regions:
        uniq = []
        for p in pts:
            if not uniq or np.linalg.norm(np.array(p) - np.array(uniq[-1])) > 1e-9:
                uniq.append(p)
        if len(uniq) > 2 and np.linalg.norm(np.array(uniq[0]) - np.array(uniq[-1])) < 1e-9:
            uniq.pop()
        mp = BRepBuilderAPI_MakePolygon()
        for p in uniq:
            mp.Add(gp_Pnt(float(p[0]), float(p[1]), 0.0))
        mp.Close()
        sew.Add(BRepBuilderAPI_MakeFace(mp.Wire(), True).Face())
    sew.Perform()
    u = ShapeUpgrade_UnifySameDomain(sew.SewedShape(), True, True, True)
    u.Build()
    segs = []
    e = TopExp_Explorer(u.Shape(), TopAbs_EDGE)
    nf = 0
    fe = TopExp_Explorer(u.Shape(), TopAbs_FACE)
    while fe.More():
        nf += 1
        fe.Next()
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge_s(e.Current()))
        if c.GetType() == GeomAbs_Line:
            a, b = v3(c.Value(c.FirstParameter()))[:2], v3(c.Value(c.LastParameter()))[:2]
            segs.append((a, b))
        e.Next()
    return segs, nf


# ---------------------------------------------------------------------- the DXF
def read_dxf(path):
    with open(path, errors="replace") as fh:
        raw = [ln.rstrip("\r\n") for ln in fh]
    pairs = [(raw[i].strip(), raw[i + 1].strip()) for i in range(0, len(raw) - 1, 2)]
    units, sec, cur, ents = None, None, None, []
    for i, (c, v) in enumerate(pairs):
        if c == "9" and v == "$INSUNITS":
            units = int(pairs[i + 1][1])
        if c == "2" and v in ("ENTITIES", "HEADER", "TABLES", "BLOCKS"):
            sec = v
        if sec != "ENTITIES":
            continue
        if c == "0":
            if cur:
                ents.append(cur)
            cur = (v, {}) if v not in ("ENDSEC", "EOF") else None
        elif cur is not None:
            cur[1].setdefault(c, []).append(v)
    out = dict(units=units, lines={}, circles=[], other=[])
    for typ, d in ents:
        lay = d.get("8", ["0"])[0].upper()
        if typ == "LINE":
            out["lines"].setdefault(lay, []).append((np.array([float(d["10"][0]), float(d["20"][0])]),
                                                     np.array([float(d["11"][0]), float(d["21"][0])])))
        elif typ == "CIRCLE":
            out["circles"].append((lay, np.array([float(d["10"][0]), float(d["20"][0])]), 2 * float(d["40"][0])))
        else:
            out["other"].append(typ)
    return out


def seg_dist(p, a, b):
    ab = b - a
    L = float(np.dot(ab, ab))
    s = 0.0 if L == 0 else max(0.0, min(1.0, float(np.dot(p - a, ab)) / L))
    return float(np.linalg.norm(p - (a + s * ab)))


def hausdorff(segs_a, segs_b, step=1.0):
    def samples(segs):
        pts = []
        for a, b in segs:
            n = max(1, int(np.linalg.norm(b - a) / step))
            pts += [a + (b - a) * i / n for i in range(n + 1)]
        return pts
    d1 = max(min(seg_dist(p, a, b) for a, b in segs_b) for p in samples(segs_a))
    d2 = max(min(seg_dist(p, a, b) for a, b in segs_a) for p in samples(segs_b))
    return max(d1, d2)


def candidates(segs_dev, segs_dxf):
    """Rigid moves (2x2 matrix, offset) that may carry the developed flat onto the DXF's: the longest developed
    edge laid on each DXF edge of the same length, both ways, plain or mirrored."""
    a0, b0 = max(segs_dev, key=lambda s: np.linalg.norm(s[1] - s[0]))
    L0 = np.linalg.norm(b0 - a0)
    out = []
    for a1, b1 in segs_dxf:
        if abs(np.linalg.norm(b1 - a1) - L0) > 0.05:
            continue
        for p, q in ((a1, b1), (b1, a1)):
            for mirror in (False, True):
                u0 = (b0 - a0) / L0
                u1 = (q - p) / np.linalg.norm(q - p)
                F = np.array([[1, 0], [0, -1]]) if mirror else np.eye(2)
                u0m = F @ u0
                ang = math.atan2(u1[1], u1[0]) - math.atan2(u0m[1], u0m[0])
                R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]]) @ F
                off = p - R @ a0
                out.append((R, off, mirror))
    return out


def check(step_path, dxf_path, k=0.44, tol=TOL, verbose=True):
    faults = []
    dev = developed(step_path, k)
    dx = read_dxf(dxf_path)
    if dx["units"] != 4:
        faults.append("the DXF's units aren't mm ($INSUNITS %s)" % dx["units"])
    segs_dev, nf = outline_of(dev["regions"])
    if nf != 1:
        faults.append("the developed flat isn't one piece (%d faces)" % nf)
    for poly in dev["cutouts"]:               # straight-edged openings: their edges are cut lines too
        segs_dev += [(np.array(poly[i]), np.array(poly[(i + 1) % len(poly)])) for i in range(len(poly))]
    cut = dx["lines"].get("CUT", [])
    best = None
    for R, off, mirror in candidates(segs_dev, cut):
        moved = [(R @ a + off, R @ b + off) for a, b in segs_dev]
        h = hausdorff(moved, cut, step=2.0)
        if best is None or h < best[0]:
            best = (h, R, off, mirror)
    if best is None:
        faults.append("no DXF outline edge matches the developed flat's longest edge")
        return faults, dev
    h0, R, off, mirror = best
    moved = [(R @ a + off, R @ b + off) for a, b in segs_dev]
    h = hausdorff(moved, cut, step=0.5)
    if h > tol:
        faults.append("the DXF's outline is %.4f mm off the developed flat (allowed %.2f)" % (h, tol))
    # fold centre lines and zone edges
    bends = dx["lines"].get("BEND", [])
    marks = dx["lines"].get("MARK", [])
    if len(bends) != len(dev["folds"]):
        faults.append("the DXF has %d bend lines, the model %d folds" % (len(bends), len(dev["folds"])))
    ks = []
    for fd in dev["folds"]:
        c0, c1 = (R @ fd["centre"][0] + off, R @ fd["centre"][1] + off)
        hit = [bl for bl in bends if (np.linalg.norm(bl[0] - c0) < tol and np.linalg.norm(bl[1] - c1) < tol) or
               (np.linalg.norm(bl[0] - c1) < tol and np.linalg.norm(bl[1] - c0) < tol)]
        if len(hit) != 1:
            near = min((max(min(np.linalg.norm(bl[0] - c0), np.linalg.norm(bl[1] - c0)),
                            min(np.linalg.norm(bl[0] - c1), np.linalg.norm(bl[1] - c1))) for bl in bends),
                       default=float("nan"))
            faults.append("a fold of %.2f deg, r %.2f: no DXF bend line on its centre line (nearest %.4f mm)" % (
                math.degrees(fd["ang"]), fd["r"], near))
            continue
        # the K-factor the DXF's two zone edges imply
        bl = hit[0]
        d = (bl[1] - bl[0]) / np.linalg.norm(bl[1] - bl[0])
        nrm = np.array([-d[1], d[0]])
        # the DXF's coordinates carry 6 decimals: a zone edge is parallel to the bend line within 1e-5 rad and
        # keeps its offset within 1e-4 mm along its length
        offs = []
        for m in marks:
            dm = m[1] - m[0]
            sin = abs(float(dm[0] * d[1] - dm[1] * d[0])) / float(np.linalg.norm(dm))
            o0, o1 = float(np.dot(m[0] - bl[0], nrm)), float(np.dot(m[1] - bl[0], nrm))
            if sin < 1e-5 and abs(o1 - o0) < 1e-4 and abs(o0) < fd["ba"] + 1.0:
                offs.append(o0)
        offs.sort()
        if len(offs) < 2:
            faults.append("a fold's zone edges aren't in the DXF's MARK layer")
            continue
        width = offs[-1] - offs[0]
        kk = (width / fd["ang"] - fd["r"]) / dev["t"]
        ks.append(kk)
        if abs(kk - k) > 0.001:
            faults.append("a fold's zone in the DXF implies K %.4f, not %.2f" % (kk, k))
    # holes
    dh = [(c, d) for lay, c, d in dx["circles"] if lay == "CUT"]
    if len(dh) != len(dev["holes"]):
        faults.append("the DXF has %d holes, the model %d" % (len(dh), len(dev["holes"])))
    for c, d in dev["holes"]:
        cc = R @ c + off
        if not any(np.linalg.norm(cc - c2) < tol and abs(d - d2) < tol for c2, d2 in dh):
            faults.append("the model's hole %.2f at %s has no DXF circle" % (d, np.round(cc, 3)))
    if dx["other"]:
        faults.append("the DXF has entities the flat check doesn't read: %s" % sorted(set(dx["other"])))
    if verbose:
        print("%s: t %.3f, %d folds, outline %.4f mm off%s, K %s -> %s" % (
            step_path.split("/")[-1], dev["t"], len(dev["folds"]), h, " (mirrored: the DXF shows the other skin)"
            if mirror else "", ", ".join("%.4f" % x for x in ks) or "-", "PASS" if not faults else "FAIL"))
        for f in faults:
            print("   " + f)
    return faults, dev


def main(argv):
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("step")
    ap_.add_argument("dxf")
    ap_.add_argument("--k", type=float, default=0.44)
    a = ap_.parse_args(argv)
    faults, _dev = check(a.step, a.dxf, a.k)
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
