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


def read_step(path, paths=False):
    """[(product name, [solids in top coordinates])] for every leaf product occurrence in the file; with paths, each
    also with its ancestors from the top, [(placement key, product name)] (a welded frame's members, D-120)."""
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

    def walk(lab, loc, name, key, anc):
        if st.IsAssembly_s(lab):
            here = anc + ((key, name or _name(lab)),)
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)), _name(ref) or _name(c), key + (i,), here)
            return
        shape = st.GetShape_s(lab)
        if not loc.IsIdentity():
            shape = shape.Moved(loc)
        out.append((name or _name(lab), _solids(shape)) + ((anc,) if paths else ()))

    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        walk(lab, TopLoc_Location(), _name(lab), (i,), ())
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
    occurrences = 0
    for name, solids in read_step(path):
        if part_number_of(name) != pn:
            continue
        occurrences += 1
        if occurrences > 1:     # the same part used again in the assembly: one is drawn (FRONT's 352211, 3 off)
            continue
        for s in solids:
            bodies.append(Body("", s))
    members = False
    if not bodies:
        # a part's own file: the product may carry the document name (PN_REV_NAME_CAD) or PN_1
        own = os.path.basename(path).startswith(pn + "_")
        if own:
            leaves = [(name, solids) for name, solids in read_step(path) if solids]
            others = [name for name, _s in leaves if part_number_of(name) not in (None, pn)]
            if leaves and len(others) == len(leaves):
                # a welded frame in its own file whose every body is a member part (WALL's 211101, D-120): each body
                # named by its member's number and name, as from a team STEP
                bodies += [Body(name, s) for name, solids in leaves for s in solids]
                members = True
                occurrences = 1
            else:
                for name, solids in leaves:
                    for s in solids:
                        bodies.append(Body("", s))
    if not bodies:
        # a welded frame with no body of its own (D-120: its members are parts under it): every solid under its first
        # placement, each body named by its member's number and name; its quantity is its own placements' count
        first, keys = None, set()
        for name, solids, anc in read_step(path, paths=True):
            key = next((k for k, nm in anc if part_number_of(nm) == pn), None)
            if key is None:
                continue
            keys.add(key)
            if first is None:
                first = key
            if key == first:
                bodies += [Body(name, s) for s in solids]
        members = bool(bodies)
        occurrences = len(keys)
    if not bodies:
        raise LookupError("no solid of %s in %s" % (pn, path))
    names, sf = body_names(path, pn)
    if members:                 # the unit check reads the members' instances
        for mpn in sorted({part_number_of(b.name) for b in bodies} - {None}):
            more, sf = body_names(path, mpn)
            names.update(more)
    for b in bodies:
        if members:             # a member's body keeps its member's name
            continue
        key = tuple(round(v, 1) for v in b.box)
        b.name = names.get(key, "")
        if not b.name:          # boxes from vertices vs. optimal boxes can differ by a rounding step
            best = min(names.items(), key=lambda kv: sum(abs(x - y) for x, y in zip(kv[0], key)), default=None)
            if best and sum(abs(x - y) for x, y in zip(best[0], key)) < 0.6:
                b.name = best[1]
    unit = {"declared": sf.unit_name, "scale_to_mm": sf.scale, "occurrences": max(occurrences, 1)}
    if members:                 # only a frame of members says so (other parts' drawing data stays as it was)
        unit["members"] = True
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
    # open-ended slots (D-129's hook-in end caps): one half cylinder whose open side runs to the part's edge,
    # straight at its width, often widening in a taper to a mouth at the edge
    for i, a in enumerate(partial):
        if i in used or not (math.pi - 0.05 < a["span"] < math.pi + 0.05):
            continue
        o = open_slot(body, a)
        if o is not None:
            used.add(i)
            slots.append(o)
    return holes, slots


def open_slot(body, a):
    """An open-ended slot from its half cylinder a (_cyl_info), or None: its sizes from the part's own vertices in
    the wall the slot goes through, so they are exact. along: from the end's centre toward the opening."""
    d, a0, r = a["dir"], a["a0"], a["r"]
    o = vmul(a["mid"], -1.0)                    # the opening side
    lat = vnorm(vcross(d, o))
    c = vadd(a0, vmul(d, 0.5 * (a["t0"] + a["t1"])))      # the end's centre, mid-wall
    pts = []
    for v in _vertices_of(body.shape):
        p = pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v)))
        t = vdot(vsub(p, a0), d)
        if a["t0"] - 1e-3 <= t <= a["t1"] + 1e-3:
            q = vsub(p, c)
            pts.append((vdot(q, o), vdot(q, lat)))
    # the edge it opens on: the wall's farthest vertices along the opening within a few widths of the slot
    near = [q for q in pts if abs(q[1]) < 6 * r]
    if not near:
        return None
    s_edge = max(q[0] for q in near)
    if s_edge < r:
        return None
    # open: empty all the way from the end's centre to the edge
    if any(_inside(body.shape, vadd(c, vmul(o, s_))) for s_ in (0.5 * s_edge, 0.9 * s_edge, s_edge - 0.05)):
        return None
    # the mouth at the edge: the nearest vertices either side of the centre line
    at_edge = [q[1] for q in near if abs(q[0] - s_edge) < 1e-3 and abs(q[1]) > r - 1e-3]
    left = [w for w in at_edge if w > 0]
    right = [-w for w in at_edge if w < 0]
    if not left or not right:
        return None
    mouth = min(left) + min(right)
    # the taper's start: where the sides leave the slot's width (the last vertices at width before the edge)
    sides = [q[0] for q in near if abs(abs(q[1]) - r) < 1e-3 and -1e-3 < q[0] < s_edge - 1e-3]
    s_taper = max(sides) if sides and mouth > 2 * r + 1e-3 else s_edge
    p0, p1 = vadd(a0, vmul(d, a["t0"])), vadd(a0, vmul(d, a["t1"]))
    cen = body.centroid
    if vdot(vsub(p1, cen), d) >= -vdot(vsub(p0, cen), d):       # entered from the outer face (the part's end)
        entry, axis = p1, vmul(d, -1.0)
    else:
        entry, axis = p0, d
    sl = Slot(body, entry, axis, o, 2 * r, s_edge + r, a["t1"] - a["t0"], True)
    sl.kind = "open_slot"
    sl.r = r
    sl.edge = s_edge            # the end's centre to the edge
    sl.mouth = mouth            # width at the edge
    sl.taper = s_edge - s_taper  # the taper's length, from the edge (0: straight to the edge)
    return sl


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


def _vertices_of(shape):
    from OCP.TopAbs import TopAbs_VERTEX
    e = TopExp_Explorer(shape, TopAbs_VERTEX)
    while e.More():
        yield e.Current()
        e.Next()


def member_axis(body):
    """The axis of a straight member (a tube or bar): square to its two largest side faces that aren't parallel
    (their normals' cross product). None when the body isn't a long prism (no such pair, or the body isn't
    longest along that axis)."""
    fs = sorted(planes(body), key=lambda t: -t[2])
    if not fs:
        return None
    n1 = fs[0][0]
    n2 = next((t[0] for t in fs[1:] if abs(vdot(t[0], n1)) < 0.5), None)
    if n2 is None:
        return None
    a = vnorm(vcross(n1, n2))
    a = canon_dir(a)
    # long along it: the body's extent along the axis beats its extent along both normals
    pts = [pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in _vertices_of(body.shape)]
    if not pts:
        return None
    ext = lambda d: max(vdot(q, d) for q in pts) - min(vdot(q, d) for q in pts)
    if ext(a) < 1.5 * max(ext(n1), ext(n2)):
        return None
    return a


class Notch:
    """A rectangular cut-out through one wall at a member's end, open at that end (BASE's back band: the stud-head
    notches in its bottom wall, FB-15). Sizes from the model's own faces."""
    kind = "notch"

    def __init__(self, body, sgn, end_s, lax, across, wall_n, lo, hi, s_back, t, outer, faces):
        self.body = body
        self.sgn = sgn                  # +1: at the member's end along +axis; -1: at its other end
        self.end_s = end_s              # that end, along the axis
        self.lax = lax                  # the member's axis
        self.across = across            # across the notch (its width), a profile direction
        self.wall_n = wall_n            # the outward normal of the wall it goes through
        self.lo, self.hi = lo, hi       # its sides, along `across`
        self.s_back = s_back            # its back face, along the axis
        self.t = t                      # the wall's thickness (the notch goes through it)
        self.outer = outer              # the wall's outer face, along wall_n
        self.faces = faces
        self.tag = None

    @property
    def width(self):
        return self.hi - self.lo

    @property
    def length(self):
        return abs(self.end_s - self.s_back)

    def point(self, s, a, w=None):
        """The 3D point at axial position s, across position a, on the wall's outer face (or at w along wall_n)."""
        w = self.outer if w is None else w
        base = vadd(vmul(self.lax, s), vmul(self.across, a))
        return vadd(base, vmul(self.wall_n, w))


class Chamfer:
    """An edge break with equal legs (45°) between a member's square end face and one of its side faces, made of one
    or more coplanar faces (BASE's back band: the 1 x 45° bevel, FB-16, cut in two by the notch)."""
    kind = "chamfer"

    def __init__(self, body, sgn, end_s, lax, side_n, n, leg, faces, pts):
        self.body = body
        self.sgn = sgn
        self.end_s = end_s
        self.lax = lax
        self.side_n = side_n            # the side face's outward normal
        self.n = n                      # the chamfer face's outward normal
        self.leg = leg                  # both legs (mm)
        self.faces = faces
        self.pts = pts                  # every vertex of its faces
        self.tag = None
        self.long = False               # True: a bevel along the member's corner (its edge is the member's axis)
        self.edge = vnorm(vcross(lax, side_n))
        self.leg_dirs = (lax, side_n)   # its legs run along these (from the end face, from the side face)


def _in_feature(sl, pts, tol=0.02):
    """True when every point lies in the space a slot, keyhole or open slot cuts: its flats and tapers are its own."""
    lat = vnorm(vcross(sl.axis, sl.along))
    if sl.kind == "open_slot":
        lo_a, hi_a, half = -sl.r, sl.edge, sl.mouth / 2
    elif sl.kind == "keyhole":
        lo_a, hi_a, half = -sl.entry_dia / 2, sl.neck + sl.width / 2, sl.entry_dia / 2
    else:
        lo_a, hi_a, half = -sl.length / 2, sl.length / 2, sl.width / 2
    for p in pts:
        q = vsub(p, sl.entry)
        a, l, d = vdot(q, sl.along), vdot(q, lat), vdot(q, sl.axis)
        if not (lo_a - tol <= a <= hi_a + tol and abs(l) <= half + tol and -tol <= d <= sl.depth + tol):
            return False
    return True


def _face_desc(x, lax):
    """A face for a refusal: where it is and which way it faces."""
    lo = [min(p[k] for p in x["pts"]) for k in range(3)]
    hi = [max(p[k] for p in x["pts"]) for k in range(3)]
    k = max(range(3), key=lambda i: abs(x["n"][i]))
    return "a %.1f mm2 face facing %s%s at X %.2f..%.2f, Y %.2f..%.2f, Z %.2f..%.2f" % (
        x["area"], "+" if x["n"][k] > 0 else "-", "XYZ"[k], lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def flat_features(body, slots):
    """A straight member's flat faces sorted out: (notches, chamfers, end plates, unexplained). A flat face is the
    member's own when it lies on a plane of its profile (a face that runs at least half the length), is a square end
    face, is cut by one of its slots, keyholes or open slots (their flats and tapers), or belongs to an end cut (the
    oblique faces of a mitre or a compound cut, inside the end's cut length). Of the rest: a square face just inside
    an end, facing inward and inside the profile, is a welded end plate's inner face (its thickness 6 or less); a
    notch is a back face facing its end with two side faces from it to the end, through one wall; a chamfer is a small
    oblique face between a square end face and one side face, with equal legs. What is left, the caller refuses: a
    feature this tool can't size yet (a step, a pocket, an uneven chamfer...). Bodies that aren't straight members
    return nothing here."""
    lax = member_axis(body)
    if lax is None:
        return [], [], [], []
    verts = [pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in _vertices_of(body.shape)]
    ss = [vdot(p, lax) for p in verts]
    smin, smax = min(ss), max(ss)
    length = smax - smin
    faces = []
    for n, off, area, f in planes(body):
        pts = [pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in _vertices_of(f)]
        s_ = [vdot(p, lax) for p in pts]
        faces.append({"n": n, "off": off, "area": area, "f": f, "pts": pts, "s0": min(s_), "s1": max(s_),
                      "c": vdot(n, lax)})
    longs = [x for x in faces if abs(x["c"]) < 1e-6 and x["s1"] - x["s0"] >= 0.5 * length]
    # the profile's two directions: the normals of its largest long faces, square to each other
    area = {}
    for y in longs:
        d = canon_dir(y["n"])
        k = next((k for k in area if abs(abs(vdot(k, d)) - 1) < 1e-6), d)
        area[k] = area.get(k, 0.0) + y["area"]
    order = sorted(area, key=lambda k: -area[k])
    main = order[:1] + [k for k in order[1:] if abs(vdot(k, order[0])) < 1e-6][:1]
    # a bevel along the member (CEILING's seam member, 1 x 45°): a narrow long face at 45° to both directions, at an
    # outer corner of the profile, its legs equal and 5 or less
    long_chamfers = []
    if len(main) == 2:
        for y in list(longs):
            a, b = vdot(y["n"], main[0]), vdot(y["n"], main[1])
            if abs(abs(a) - 0.7071068) > 1e-4 or abs(abs(b) - 0.7071068) > 1e-4:
                continue
            d1, d2 = vmul(main[0], 1.0 if a > 0 else -1.0), vmul(main[1], 1.0 if b > 0 else -1.0)
            l1 = max(vdot(p, d1) for p in verts) - min(vdot(p, d1) for p in y["pts"])
            l2 = max(vdot(p, d2) for p in verts) - min(vdot(p, d2) for p in y["pts"])
            r1 = max(vdot(p, d1) for p in y["pts"]) - max(vdot(p, d1) for p in verts)
            r2 = max(vdot(p, d2) for p in y["pts"]) - max(vdot(p, d2) for p in verts)
            if abs(l1 - l2) > 0.01 or l1 > 5.0 or abs(r1) > 1e-3 or abs(r2) > 1e-3:
                continue
            ch = Chamfer(body, 0, None, lax, d2, y["n"], l1, [y["f"]], list(y["pts"]))
            ch.long = True
            ch.edge = lax
            ch.leg_dirs = (d1, d2)
            long_chamfers.append(ch)
            longs.remove(y)
    dirs = []
    for y in longs:
        if not any(abs(abs(vdot(y["n"], d)) - 1) < 1e-6 for d in dirs):
            dirs.append(canon_dir(y["n"]))

    def rng(pts, d):
        v = [vdot(p, d) for p in pts]
        return min(v), max(v)
    bounds = [(d, rng(verts, d)) for d in dirs]

    def on_long(x):
        return any(vdot(x["n"], y["n"]) > 1 - 1e-9 and abs(x["off"] - y["off"]) < 1e-3 for y in longs)

    def at_end(x, e):
        return abs(x["s0"] - e) < 1e-3 and abs(x["s1"] - e) < 1e-3

    ends = {+1: smax, -1: smin}
    square_end = {g: [x for x in faces if abs(abs(x["c"]) - 1) < 1e-6 and x["c"] * g > 0 and at_end(x, e)]
                  for g, e in ends.items()}
    rest = []
    for x in faces:
        if any(x["f"].IsSame(f) for lc in long_chamfers for f in lc.faces):
            continue                # a bevel along the member: called out on its own
        if abs(x["c"]) < 1e-6 and on_long(x):
            continue
        if any(abs(abs(x["c"]) - 1) < 1e-6 and at_end(x, e) for e in ends.values()):
            continue
        if any(_in_feature(sl, x["pts"]) for sl in slots):
            continue
        rest.append(x)
    # chamfers: oblique, at a square end, between that end face and one side face, legs equal and 5 or less
    chamfers, used = [], set()
    for i, x in enumerate(rest):
        if abs(x["c"]) < 1e-6 or abs(abs(x["c"]) - 1) < 1e-6:
            continue
        g = 1 if x["c"] > 0 else -1
        e = ends[g]
        if not square_end[g] or abs((x["s1"] if g > 0 else x["s0"]) - e) > 1e-3:
            continue
        side = vnorm(vsub(x["n"], vmul(lax, x["c"])))       # the side face's outward normal
        if not any(abs(abs(vdot(side, d)) - 1) < 1e-6 for d in dirs):
            continue
        a = x["s1"] - x["s0"]                                 # the leg along the member
        w0, w1 = rng(x["pts"], side)
        outer = max(rng(verts, side))
        b = w1 - w0                                           # the leg across, up from the side face
        if abs(w1 - outer) > 1e-3 or a > 5.0 or b > 5.0 or abs(a - b) > 0.01:
            continue
        for ch in chamfers:
            if ch.sgn == g and vdot(ch.n, x["n"]) > 1 - 1e-9 and abs(vdot(vsub(ch.pts[0], x["pts"][0]), x["n"])) < 1e-3:
                ch.faces.append(x["f"])
                ch.pts += x["pts"]
                break
        else:
            chamfers.append(Chamfer(body, g, e, lax, side, x["n"], a, [x["f"]], list(x["pts"])))
        used.add(i)
    # end cuts: the oblique faces within an end's cut length (a mitre, the facets of a compound cut)
    for g, e in ends.items():
        obl = [x for i, x in enumerate(rest) if i not in used and abs(x["c"]) > 1e-6 and abs(abs(x["c"]) - 1) > 1e-6
               and abs((x["s1"] if g > 0 else x["s0"]) - e) < 1e-3]
        if not obl:
            continue
        reach = max(x["s1"] - x["s0"] for x in obl) + 1e-3
        for i, x in enumerate(rest):
            if i in used or abs(x["c"]) < 1e-6 or abs(abs(x["c"]) - 1) < 1e-6:
                continue
            if (g > 0 and x["s0"] >= e - reach) or (g < 0 and x["s1"] <= e + reach):
                used.add(i)
    # end plates: a square face 6 or less inside an end, facing away from it, inside the profile
    plates = []
    for i, x in enumerate(rest):
        if i in used or abs(abs(x["c"]) - 1) > 1e-6:
            continue
        g = -1 if x["c"] > 0 else 1                           # it faces away from this end
        t = abs(ends[g] - x["s0"])
        inside = all(lo + 0.5 < rng(x["pts"], d)[0] and rng(x["pts"], d)[1] < hi - 0.5 for d, (lo, hi) in bounds)
        if 0 < t <= 6.0 and inside and abs(x["s1"] - x["s0"]) < 1e-3:
            plates.append({"sgn": g, "t": t, "face": x["f"]})
            used.add(i)
    # notches: a back face facing its end, two sides from it to the end, all through one wall
    notches = []
    for i, x in enumerate(rest):
        if i in used or abs(abs(x["c"]) - 1) > 1e-6 or abs(x["s1"] - x["s0"]) > 1e-3:
            continue
        g = 1 if x["c"] > 0 else -1
        e = ends[g]
        sb = x["s0"]
        if abs(sb - e) < 1e-3:
            continue
        for d, (blo, bhi) in bounds:
            w0, w1 = rng(x["pts"], d)
            if abs(w0 - blo) < 1e-3:
                wall_n, outer = vmul(d, -1.0), -blo
            elif abs(w1 - bhi) < 1e-3:
                wall_n, outer = d, bhi
            else:
                continue
            t = w1 - w0
            if t > 6.0:
                continue
            others = [(d2, r2) for d2, r2 in bounds if abs(vdot(d2, d)) < 1e-6]
            if len(others) != 1:
                continue
            ac, prof = others[0]
            lo, hi = rng(x["pts"], ac)
            sides = []
            for j, y in enumerate(rest):
                if j in used or j == i or abs(y["c"]) > 1e-6 or abs(abs(vdot(y["n"], ac)) - 1) > 1e-6:
                    continue
                pos = rng(y["pts"], ac)[0]
                want = 1.0 if abs(pos - lo) < 1e-3 else (-1.0 if abs(pos - hi) < 1e-3 else 0.0)
                if not want or vdot(y["n"], ac) * want < 0.5:
                    continue                                  # a side faces into the notch
                if abs(min(y["s0"], y["s1"]) - min(sb, e)) > 1e-3 or abs(max(y["s0"], y["s1"]) - max(sb, e)) > 1e-3:
                    continue
                if rng(y["pts"], d) != (w0, w1) and (abs(rng(y["pts"], d)[0] - w0) > 1e-3 or
                                                    abs(rng(y["pts"], d)[1] - w1) > 1e-3):
                    continue
                sides.append(j)
            if len(sides) != 2:
                continue
            notches.append(Notch(body, g, e, lax, ac, wall_n, lo, hi, sb, t, outer,
                                 [x["f"]] + [rest[j]["f"] for j in sides]))
            notches[-1].prof = prof         # the member's profile along `across` (its two side faces)
            used.update([i] + sides)
            break
    odd = [_face_desc(x, lax) for i, x in enumerate(rest) if i not in used]
    return notches, chamfers + long_chamfers, plates, odd


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
