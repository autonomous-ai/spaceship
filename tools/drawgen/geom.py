"""Exact B-rep geometry for the drawing generator (OCC 7.8 through cadquery-ocp).

Reads a STEP file with its product structure (XCAF), picks the solids of one part number and finds what a
part drawing has to define: holes (full concave cylinders, one run per wall they pass), slots (two half
cylinders and two flats), and the planar faces. Every length is in mm: OCC converts the file's declared unit
(Fusion writes cm, D-13) and `check_units` measures the same solid with the repo's own STEP reader
(tools/checks/stepfile.py), which scales by the declared unit on its own.

Nothing here tessellates: holes, slots and faces come from the B-rep surfaces themselves.
"""

import math
import os
import sys

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepGProp import BRepGProp
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepTools import BRepTools
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Cone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE, TopAbs_IN, TopAbs_REVERSED, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# ------------------------------------------------------------------ small vector helpers


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vmul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def vnorm(a):
    n = math.sqrt(vdot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > 0 else a


def canon_dir(d):
    """The direction with its largest component positive, so a line has one key whatever way it was given."""
    d = vnorm(d)
    k = max(range(3), key=lambda i: abs(d[i]))
    return d if d[k] > 0 else vmul(d, -1.0)


def axis_name(d, tol=1e-6):
    """'+X', '-Z'... for a pod axis direction; None for any other direction."""
    for i, n in enumerate("XYZ"):
        if abs(abs(d[i]) - 1.0) < tol:
            return ("+" if d[i] > 0 else "-") + n
    return None


def pnt(p):
    return (p.X(), p.Y(), p.Z())


# ------------------------------------------------------------------ reading


class Body:
    """One solid of a part, in the STEP file's top coordinates (the pod system for every team file)."""

    def __init__(self, name, shape):
        self.name = name
        self.shape = shape
        b = Bnd_Box()
        BRepBndLib.AddOptimal_s(shape, b, False, False)
        p, q = b.CornerMin(), b.CornerMax()
        self.box = (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())
        props = GProp_GProps()
        BRepGProp.VolumeProperties_s(shape, props)
        self.volume = props.Mass()
        c = props.CentreOfMass()
        self.centroid = (c.X(), c.Y(), c.Z())

    @property
    def size(self):
        return tuple(self.box[3 + k] - self.box[k] for k in range(3))


def _name(lab):
    n = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), n):
        return n.Get().ToExtString()
    return ""


def _solids(shape):
    out = []
    e = TopExp_Explorer(shape, TopAbs_SOLID)
    while e.More():
        out.append(TopoDS.Solid_s(e.Current()))
        e.Next()
    return out


def read_step(path):
    """[(product name, [solids in top coordinates])] for every leaf product occurrence in the file."""
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    r = STEPCAFControl_Reader()
    r.SetNameMode(True)
    if int(r.ReadFile(path)) != 1:          # IFSelect_RetDone
        raise RuntimeError("STEP read failed: %s" % path)
    if not r.Transfer(doc):
        raise RuntimeError("STEP transfer failed: %s" % path)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    out = []

    def walk(lab, loc, name):
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)), _name(ref) or _name(c))
            return
        shape = st.GetShape_s(lab)
        if not loc.IsIdentity():
            shape = shape.Moved(loc)
        out.append((name or _name(lab), _solids(shape)))

    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        walk(lab, TopLoc_Location(), _name(lab))
    return out


def part_number_of(name):
    s = (name or "").strip()
    return s[:6] if len(s) >= 6 and s[:6].isdigit() else None


def _stepfile():
    p = os.path.join(REPO, "tools", "checks")
    if p not in sys.path:
        sys.path.insert(0, p)
    import stepfile
    return stepfile


def body_names(path, pn):
    """{rounded box: solid name} for the part's solids, from the repo's STEP reader (Fusion writes each body's
    name on its MANIFOLD_SOLID_BREP; OCC's XCAF reader drops it). Also returns the reader for the unit check."""
    sf = _stepfile().StepFile(path)
    names = {}
    for inst in sf.instances():
        if part_number_of(inst["part_number"]) != pn and part_number_of(inst["name"]) != pn:
            continue
        s = sf.solid(inst["solid"])
        if not s.box:
            continue
        pts = [inst["frame"].point(p) for p in s.points()]
        box = tuple(round(min(p[k] for p in pts), 1) for k in range(3)) + tuple(
            round(max(p[k] for p in pts), 1) for k in range(3))
        names[box] = s.name
    return names, sf


def load_part(path, pn):
    """The bodies of part pn in a STEP file (its own file, or a team assembly holding it), with their names and
    a unit check against the repo's reader. Raises when the file holds no solid of that part."""
    bodies = []
    for name, solids in read_step(path):
        if part_number_of(name) != pn:
            continue
        for s in solids:
            bodies.append(Body("", s))
    if not bodies:
        # a part's own file: the product may carry the document name (PN_REV_NAME_CAD) or PN_1
        own = os.path.basename(path).startswith(pn + "_")
        if own:
            for name, solids in read_step(path):
                for s in solids:
                    bodies.append(Body("", s))
    if not bodies:
        raise LookupError("no solid of %s in %s" % (pn, path))
    names, sf = body_names(path, pn)
    for b in bodies:
        key = tuple(round(v, 1) for v in b.box)
        b.name = names.get(key, "")
        if not b.name:          # boxes from vertices vs. optimal boxes can differ by a rounding step
            best = min(names.items(), key=lambda kv: sum(abs(x - y) for x, y in zip(kv[0], key)), default=None)
            if best and sum(abs(x - y) for x, y in zip(best[0], key)) < 0.6:
                b.name = best[1]
    unit = {"declared": sf.unit_name, "scale_to_mm": sf.scale}
    # unit check (D-13): the repo reader scales by the declared unit; OCC converts on its own. They must agree.
    worst = 0.0
    for b in bodies:
        key = tuple(round(v, 1) for v in b.box)
        if names:
            best = min(names, key=lambda k: sum(abs(x - y) for x, y in zip(k, key)))
            worst = max(worst, max(abs(x - y) for x, y in zip(best, key)))
    unit["box_check_mm"] = round(worst, 3)
    if names and worst > 0.6:
        raise ValueError("unit check failed for %s: OCC and the STEP reader disagree by %.3f mm" % (pn, worst))
    bodies.sort(key=lambda b: (b.name, b.box))
    return bodies, unit


def compound(shapes):
    c = TopoDS_Compound()
    bld = BRep_Builder()
    bld.MakeCompound(c)
    for s in shapes:
        bld.Add(c, s)
    return c


def transformed(shape, trsf):
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def mirror_x(shape):
    t = gp_Trsf()
    from OCP.gp import gp_Ax2, gp_Dir
    t.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    return transformed(shape, t)


# ------------------------------------------------------------------ features


class Hole:
    """One run of a round hole through one wall (or blind into material).

    entry: centre of the hole where the drill enters (the end away from the body's centre), in pod mm;
    axis: unit vector from the entry into the material; depth: run length; through: open at both ends."""

    def __init__(self, body, entry, axis, dia, depth, through, line_key, t0, t1):
        self.body = body
        self.entry = entry
        self.axis = axis
        self.dia = dia
        self.depth = depth
        self.through = through
        self.line_key = line_key
        self.t0, self.t1 = t0, t1
        self.partners = []       # other runs on the same axis (a hole through two tube walls)
        self.tag = None
        self.point_angle = None  # a blind hole's drill point (degrees), when its cone is in the model

    @property
    def normal(self):
        """Outward normal of the entry face."""
        return vmul(self.axis, -1.0)


class Slot:
    def __init__(self, body, entry, axis, along, width, length, depth, through):
        self.body = body
        self.entry = entry          # centre of the slot on the entry face
        self.axis = axis            # into the material
        self.along = along          # unit vector along the slot's length
        self.width = width
        self.length = length        # overall, ends included
        self.depth = depth
        self.through = through
        self.tag = None
        self.kind = "slot"
        self.entry_dia = None
        self.neck = None

    @property
    def dia(self):
        return self.width

    @property
    def normal(self):
        return vmul(self.axis, -1.0)


def _faces(shape):
    e = TopExp_Explorer(shape, TopAbs_FACE)
    while e.More():
        yield TopoDS.Face_s(e.Current())
        e.Next()


def _cyl_info(face):
    s = BRepAdaptor_Surface(face, True)
    if s.GetType() != GeomAbs_Cylinder:
        return None
    cyl = s.Cylinder()
    ax = cyl.Axis()
    loc, d = pnt(ax.Location()), (ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z())
    r = cyl.Radius()
    umin, umax, vmin, vmax = BRepTools.UVBounds_s(face)
    um, vm = 0.5 * (umin + umax), 0.5 * (vmin + vmax)
    props = BRepLProp_SLProps(s, um, vm, 1, 1e-7)
    if not props.IsNormalDefined():
        return None
    n = props.Normal()
    n = (n.X(), n.Y(), n.Z())
    if face.Orientation() == TopAbs_REVERSED:
        n = vmul(n, -1.0)
    p = pnt(s.Value(um, vm))
    t = vdot(vsub(p, loc), d)
    radial = vsub(p, vadd(loc, vmul(d, t)))
    concave = vdot(n, radial) < 0
    # where the face sits round the axis: the direction from the axis to the face's middle
    mid_dir = vnorm(radial)
    span = umax - umin
    # axial extent along the canonical axis line
    cd = canon_dir(d)
    a0 = vsub(loc, vmul(cd, vdot(loc, cd)))      # the axis point closest to the origin
    ends = [vdot(vsub(vadd(loc, vmul(d, v)), a0), cd) for v in (vmin, vmax)]
    return {"r": r, "dir": cd, "a0": a0, "t0": min(ends), "t1": max(ends), "span": span, "concave": concave,
            "mid": mid_dir}


def _inside(solid, p):
    c = BRepClass3d_SolidClassifier(solid, gp_Pnt(*p), 1e-6)
    return c.State() == TopAbs_IN


def _square_end(shape, p, out, r, gap=0.6, eps=0.05):
    """True when the hole's end at p sits in a face square to the hole: just round the hole, material just behind
    the end plane and none just in front of it, all the way round (out: the axis pointing out of the material)."""
    a = (1.0, 0.0, 0.0) if abs(out[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = vnorm(vcross(out, a))
    v = vcross(out, u)
    for k in range(8):
        t = k * math.pi / 4
        q = vadd(p, vadd(vmul(u, (r + gap) * math.cos(t)), vmul(v, (r + gap) * math.sin(t))))
        if not _inside(shape, vadd(q, vmul(out, -eps))) or _inside(shape, vadd(q, vmul(out, eps))):
            return False
    return True


def features(body):
    """(holes, slots) of one body, from its cylindrical faces."""
    cyls = []
    for f in _faces(body.shape):
        info = _cyl_info(f)
        if info and info["concave"]:
            cyls.append(info)
    # group faces on one axis line with one radius
    groups = []
    for c in cyls:
        for g in groups:
            h = g[0]
            if abs(h["r"] - c["r"]) < 1e-4 and abs(abs(vdot(h["dir"], c["dir"])) - 1) < 1e-7 and \
                    math.dist(h["a0"], c["a0"]) < 1e-3:
                g.append(c)
                break
        else:
            groups.append([c])
    # cones: a drill point closes a blind hole's bottom (the probe past the cylinder's end lands in the point's
    # cavity, so the end would read as open)
    cones = []
    for f in _faces(body.shape):
        sf = BRepAdaptor_Surface(f, True)
        if sf.GetType() == GeomAbs_Cone:
            cn = sf.Cone()
            dd = cn.Axis().Direction()
            cones.append({"apex": pnt(cn.Apex()), "dir": canon_dir((dd.X(), dd.Y(), dd.Z())), "semi": abs(cn.SemiAngle())})

    def point_at(d, a0, r, t_end, beyond):
        """A cone that is the drill point at this end of a run (beyond: +1 past t1, -1 before t0): its angle."""
        for cn in cones:
            if abs(abs(vdot(cn["dir"], d)) - 1) > 1e-6:
                continue
            off = vsub(cn["apex"], a0)
            t = vdot(off, d)
            if math.sqrt(max(0.0, vdot(off, off) - t * t)) > 0.02:
                continue
            want = r / math.tan(cn["semi"]) if cn["semi"] > 1e-6 else 1e9
            if abs((t - t_end) * beyond - want) < max(0.02, 0.01 * r):
                return 2 * math.degrees(cn["semi"])
        return None
    holes, partial = [], []
    for g in groups:
        g.sort(key=lambda c: c["t0"])
        runs = []
        for c in g:
            if runs and c["t0"] <= runs[-1]["t1"] + 1e-3:
                runs[-1]["t1"] = max(runs[-1]["t1"], c["t1"])
                runs[-1]["faces"].append(c)
            else:
                runs.append({"t0": c["t0"], "t1": c["t1"], "faces": [c]})
        for run in runs:
            span = sum(c["span"] for c in run["faces"])
            if span < 2 * math.pi - 1e-3:
                partial.extend(run["faces"])
                continue
            h0 = g[0]
            d, a0 = h0["dir"], h0["a0"]
            p0 = vadd(a0, vmul(d, run["t0"]))
            p1 = vadd(a0, vmul(d, run["t1"]))
            pt0 = point_at(d, a0, h0["r"], run["t0"], -1)
            pt1 = point_at(d, a0, h0["r"], run["t1"], +1)
            closed0 = pt0 is not None or _inside(body.shape, vadd(a0, vmul(d, run["t0"] - 0.05)))
            closed1 = pt1 is not None or _inside(body.shape, vadd(a0, vmul(d, run["t1"] + 0.05)))
            through = not closed0 and not closed1
            sq0 = sq1 = False
            if through:     # a through hole drilled square to one face and leaving another at an angle: from the square one
                sq0, sq1 = _square_end(body.shape, p0, vmul(d, -1.0), h0["r"]), _square_end(body.shape, p1, d, h0["r"])
            if closed0 and not closed1:
                entry, axis = p1, vmul(d, -1.0)
            elif closed1 and not closed0:
                entry, axis = p0, d
            elif sq0 != sq1:
                entry, axis = (p0, d) if sq0 else (p1, vmul(d, -1.0))
            else:           # the end farther from the body's centre is the outer face
                c = body.centroid
                if vdot(vsub(p1, c), d) >= -vdot(vsub(p0, c), d):
                    entry, axis = p1, vmul(d, -1.0)
                else:
                    entry, axis = p0, d
            key = (tuple(round(x, 6) for x in d), tuple(round(x, 2) for x in a0))     # the axis line only
            holes.append(Hole(body, entry, axis, 2 * h0["r"], run["t1"] - run["t0"], through, key,
                              run["t0"], run["t1"]))
            holes[-1].point_angle = pt1 if entry is p0 else pt0
    # partners: runs on one axis line (both walls of a tube)
    for h in holes:
        h.partners = [o for o in holes if o is not h and o.line_key == h.line_key]
    # slots: two half cylinders of one radius, parallel, facing away from each other, same axial extent
    slots, used = [], set()
    for i, a in enumerate(partial):
        if i in used or not (math.pi - 0.05 < a["span"] < math.pi + 0.05):
            continue
        for j in range(i + 1, len(partial)):
            b = partial[j]
            if j in used or abs(a["r"] - b["r"]) > 1e-4 or abs(abs(vdot(a["dir"], b["dir"])) - 1) > 1e-7:
                continue
            if abs(a["t0"] - b["t0"]) > 1e-3 or abs(a["t1"] - b["t1"]) > 1e-3:
                continue
            ab = vsub(b["a0"], a["a0"])
            dist = math.sqrt(vdot(ab, ab))
            if dist < 1e-3:
                continue
            u = vmul(ab, 1.0 / dist)
            if vdot(a["mid"], u) > -0.5 or vdot(b["mid"], u) < 0.5:
                continue
            used.update((i, j))
            d = a["dir"]
            mid = vmul(vadd(a["a0"], b["a0"]), 0.5)
            p0, p1 = vadd(mid, vmul(d, a["t0"])), vadd(mid, vmul(d, a["t1"]))
            closed0 = _inside(body.shape, vadd(mid, vmul(d, a["t0"] - 0.05)))
            closed1 = _inside(body.shape, vadd(mid, vmul(d, a["t1"] + 0.05)))
            c = body.centroid
            if closed0 and not closed1:
                entry, axis = p1, vmul(d, -1.0)
            elif closed1 and not closed0:
                entry, axis = p0, d
            elif vdot(vsub(p1, c), d) >= -vdot(vsub(p0, c), d):
                entry, axis = p1, vmul(d, -1.0)
            else:
                entry, axis = p0, d
            slots.append(Slot(body, entry, axis, u, 2 * a["r"], dist + 2 * a["r"], a["t1"] - a["t0"],
                              not closed0 and not closed1))
            break
    # keyholes: a round entry (a concave cylinder over half a turn, cut open by the neck) and a narrower half
    # cylinder (the neck's end) on a parallel axis, same wall, the neck's end facing away from the entry
    for i, a in enumerate(partial):
        if i in used or not (math.pi + 0.05 < a["span"] < 2 * math.pi - 1e-3):
            continue
        for j, b in enumerate(partial):
            if j == i or j in used or not (math.pi - 0.05 < b["span"] < math.pi + 0.05) or b["r"] >= a["r"]:
                continue
            if abs(abs(vdot(a["dir"], b["dir"])) - 1) > 1e-7 or abs(a["t0"] - b["t0"]) > 1e-3 or \
                    abs(a["t1"] - b["t1"]) > 1e-3:
                continue
            ab = vsub(b["a0"], a["a0"])
            dist = math.sqrt(vdot(ab, ab))
            if dist < 1e-3:
                continue
            u = vmul(ab, 1.0 / dist)
            if vdot(b["mid"], u) < 0.5:
                continue
            used.update((i, j))
            d = a["dir"]
            c0 = a["a0"]
            p0, p1 = vadd(c0, vmul(d, a["t0"])), vadd(c0, vmul(d, a["t1"]))
            c = body.centroid
            if vdot(vsub(p1, c), d) >= -vdot(vsub(p0, c), d):
                entry, axis = p1, vmul(d, -1.0)
            else:
                entry, axis = p0, d
            k = Slot(body, entry, axis, u, 2 * b["r"], dist + b["r"], a["t1"] - a["t0"], True)
            k.kind = "keyhole"
            k.entry_dia = 2 * a["r"]
            k.neck = dist          # entry centre to the neck end's centre
            slots.append(k)
            break
    return holes, slots


def unexplained_curved_faces(body, holes, slots):
    """Cylindrical faces that are neither a hole nor a slot, cones and other non-planar faces: features this
    tool can't dimension (bends, fillets, countersinks...). The caller sends such a part back to Fusion."""
    out = []
    for f in _faces(body.shape):
        s = BRepAdaptor_Surface(f, True)
        t = s.GetType()
        if t == GeomAbs_Plane:
            continue
        if t == GeomAbs_Cylinder:
            info = _cyl_info(f)
            if info and info["concave"]:
                ok = any(abs(h.dia / 2 - info["r"]) < 1e-3 for h in holes) or \
                    any(abs(s_.width / 2 - info["r"]) < 1e-3 or abs((s_.entry_dia or 0) / 2 - info["r"]) < 1e-3
                        for s_ in slots)
                if ok:
                    continue
            out.append(("convex cylinder" if info and not info["concave"] else "cylinder", info["r"] if info else None))
            continue
        if t == GeomAbs_Cone and drill_point_of(s, holes) is not None:
            continue
        out.append(({GeomAbs_Cone: "cone"}.get(t, "surface type %s" % int(t)), None))
    return out


def drill_point_of(surface, holes, tol=0.02):
    """The blind hole a cone is the drill point of (the cone on the hole's axis, pointing into the material, its
    base the hole's diameter at the hole's closed end), or None. Sets that hole's point_angle (degrees)."""
    cone = surface.Cone()
    ax = cone.Axis()
    apex_dir = (ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z())
    apex = pnt(cone.Apex())
    for h in holes:
        if h.through:
            continue
        # the apex on the hole's axis line, beyond its closed end, and the cone's axis along the hole's
        bottom = vadd(h.entry, vmul(h.axis, h.depth))
        off = vsub(apex, h.entry)
        along = vdot(off, h.axis)
        if math.sqrt(max(0.0, vdot(off, off) - along * along)) > tol or along < h.depth - tol:
            continue
        if abs(abs(vdot(apex_dir, h.axis)) - 1) > 1e-6:
            continue
        half = cone.SemiAngle()
        # the cone's base is the hole's circle: the apex sits r / tan(half) past the bottom
        if abs(math.dist(apex, bottom) - (h.dia / 2) / math.tan(abs(half))) > max(tol, 0.01 * h.dia):
            continue
        h.point_angle = 2 * math.degrees(abs(half))
        return h
    return None


def planes(body):
    """Planar faces: (outward normal, offset along it, area, face)."""
    out = []
    for f in _faces(body.shape):
        s = BRepAdaptor_Surface(f, True)
        if s.GetType() != GeomAbs_Plane:
            continue
        pl = s.Plane()
        n = pl.Axis().Direction()
        n = (n.X(), n.Y(), n.Z())
        if f.Orientation() == TopAbs_REVERSED:
            n = vmul(n, -1.0)
        o = pnt(pl.Location())
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(f, props)
        out.append((n, vdot(o, n), props.Mass(), f))
    return out


def half_space_keep(shape, point, normal, big=1e5):
    """The part of shape on the -normal side of the plane through point (what a section view keeps)."""
    n = vnorm(normal)
    # a big box whose +normal face sits on the plane
    from OCP.gp import gp_Ax2, gp_Dir
    # build an orthonormal frame with z = -n so the box extends away from the viewer
    z = vmul(n, -1.0)
    x = vnorm(vcross(z, (0, 0, 1) if abs(z[2]) < 0.9 else (1, 0, 0)))
    origin = vadd(vsub(point, vmul(x, big / 2)), vmul(vcross(z, x), -big / 2))
    ax = gp_Ax2(gp_Pnt(*origin), gp_Dir(*z), gp_Dir(*x))
    box = BRepPrimAPI_MakeBox(ax, big, big, big).Shape()
    op = BRepAlgoAPI_Common(shape, box)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("section cut failed")
    return op.Shape()


def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


# ------------------------------------------------------------------ placement of a part file in the pod

def _rotations():
    """The 24 proper rotations that map the axes onto the axes."""
    import itertools
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0.0] * 3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = float(signs[i])
            det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                   + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
            if det > 0:
                out.append(m)
    return out


def _apply(m, p):
    return tuple(sum(m[i][j] * p[j] for j in range(3)) for i in range(3))


def find_placement(own_bodies, asm_bodies, tol=0.02):
    """The rotation (axis to axis) and translation taking a part file's bodies onto the same part in an assembly
    file, checked on every hole entry and the box. Returns (matrix, translation) or None."""
    def holes_of(bodies):
        pts = []
        for b in bodies:
            hs, ss = features(b)
            pts += [h.entry for h in hs] + [s.entry for s in ss]
        return pts
    own_pts, asm_pts = holes_of(own_bodies), holes_of(asm_bodies)
    if len(own_pts) != len(asm_pts):
        return None
    ob = [min(b.box[k] for b in own_bodies) for k in range(3)] + [max(b.box[3 + k] for b in own_bodies) for k in range(3)]
    ab = [min(b.box[k] for b in asm_bodies) for k in range(3)] + [max(b.box[3 + k] for b in asm_bodies) for k in range(3)]
    for m in _rotations():
        c1, c2 = _apply(m, ob[:3]), _apply(m, ob[3:])
        rmin = [min(c1[k], c2[k]) for k in range(3)]
        rmax = [max(c1[k], c2[k]) for k in range(3)]
        if any(abs((rmax[k] - rmin[k]) - (ab[3 + k] - ab[k])) > tol for k in range(3)):
            continue
        t = [ab[k] - rmin[k] for k in range(3)]
        moved = [tuple(v + t[k] for k, v in enumerate(_apply(m, p))) for p in own_pts]
        if all(min(math.dist(p, q) for q in asm_pts) < tol for p in moved):
            return m, tuple(t)
    return None


def placed(shape, m, t):
    tr = gp_Trsf()
    tr.SetValues(m[0][0], m[0][1], m[0][2], t[0], m[1][0], m[1][1], m[1][2], t[1], m[2][0], m[2][1], m[2][2], t[2])
    return transformed(shape, tr)


def window_keep(shape, view, x0, x1, y0, y1, big=1e5):
    """The part of shape inside a window of a view: x0..x1 along the view's X, y0..y1 along its Y, all depths (what
    a detail view shows)."""
    from OCP.gp import gp_Ax2, gp_Dir
    o = vadd(vadd(vmul(view.x, x0), vmul(view.y, y0)), vmul(view.n, -big / 2))
    ax = gp_Ax2(gp_Pnt(*o), gp_Dir(*view.n), gp_Dir(*view.x))
    box = BRepPrimAPI_MakeBox(ax, x1 - x0, y1 - y0, big).Shape()
    op = BRepAlgoAPI_Common(shape, box)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("detail cut failed")
    return op.Shape()
