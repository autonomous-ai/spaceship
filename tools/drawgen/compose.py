"""Compose one part drawing from the part's STEP: choose the views, cut the sections, tag the holes, write the
hole tables, the notes and the title block, and save the PDF.

The rules (guideline sections 3.2, 3.3, 6; D-112, D-113; conventions sections 3, 4, 7):
- first-angle: the view from above sits below the principal view, from below above it, from the left on its
  right, from the right on its left;
- the principal view looks along the part's thinnest direction, as the pod's standard view for that axis;
- every face with holes gets a view that looks straight at it: a plain projected view when nothing of the part
  stands in front of it, else a section just in front of it;
- holes through two walls of one member (coaxial runs) get a removed section through their axis (D-113),
  hatched per ISO 128-50;
- each view has its own 2D origin O1, O2... with +X right and +Y up and the mapping to 3D in its title;
- hole positions are in one table per face, X (mm) and Y (mm) from that view's origin, with the tags on the
  view; depth, wall and entry face in their own columns (no Z column).
"""

import datetime
import math
import os
import re

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.TopAbs import TopAbs_EDGE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax3, gp_Dir, gp_Lin, gp_Pnt, gp_Trsf

import geom
import inputs
import project
from geom import axis_name, vadd, vcross, vdot, vmul, vnorm, vsub
from project import View
from sheet import Sheet, W_HID, W_THIN, W_VIS, DASH_HID

GENERATOR = "drawgen"
TOOL_REV = "drawgen 1.0"

ISO_SCALES = [10.0, 5.0, 2.0, 1.0, 1 / 2.0, 1 / 5.0, 1 / 10.0, 1 / 20.0]


def scale_text(s):
    return "%g:1" % s if s >= 1 else "1:%g" % round(1 / s, 3)


def fmt(v, nd=2):
    s = ("%.*f" % (nd, v)).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class NotDrawable(Exception):
    """The part has something this tool can't dimension properly: it goes back to Fusion (D-112, D-113)."""


# ------------------------------------------------------------------ geometry helpers

def ray_blocked(shape, p, d, skip=0.02):
    """True when the ray from p along d meets the shape (after a small skip)."""
    inter = IntCurvesFace_ShapeIntersector()
    inter.Load(shape, 1e-6)
    lin = gp_Lin(gp_Pnt(*vadd(p, vmul(d, skip))), gp_Dir(*d))
    inter.Perform(lin, 0.0, 1e7)
    return inter.IsDone() and inter.NbPnt() > 0


def view_trsf(view):
    """Transform taking pod/part coordinates into the view's frame (x, y in the view, z toward the viewer)."""
    ax3 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(*view.n), gp_Dir(*view.x))
    t = gp_Trsf()
    t.SetTransformation(ax3)
    return t


def cut_faces(kept, point, normal):
    """Planar faces of the kept half lying on the cutting plane (outward normal along +normal)."""
    off = vdot(point, normal)
    out = []
    for f in geom._faces(kept):
        s = BRepAdaptor_Surface(f, True)
        if s.GetType() != GeomAbs_Plane:
            continue
        pl = s.Plane()
        n = pl.Axis().Direction()
        n = (n.X(), n.Y(), n.Z())
        if f.Orientation() == TopAbs_REVERSED:
            n = vmul(n, -1.0)
        if vdot(n, normal) > 0.9999 and abs(vdot(geom.pnt(pl.Location()), normal) - off) < 1e-4:
            out.append(f)
    return out


def face_loops(face, view):
    """The face's boundary as 2D prims in the view (exact lines and arcs), one list for the whole face (the
    hatch fills even-odd, so holes in it stay open)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    t = view_trsf(view)
    f2 = BRepBuilderAPI_Transform(face, t, True).Shape()
    prims = []
    e = TopExp_Explorer(f2, TopAbs_EDGE)
    while e.More():
        prims.extend(project.edge_prims(TopoDS.Edge_s(e.Current()), True, "cut"))
        e.Next()
    return prims


# ------------------------------------------------------------------ the drawing model

class VD:
    """A view on the sheet."""

    def __init__(self, view, prims, scale, kind="view"):
        self.view = view
        self.prims = prims
        self.scale = scale
        self.kind = kind              # view, section, removed
        self.hatch = []               # lists of prims (view mm) to hatch
        self.marks = []               # (centre 2D view mm, radius, feature) holes seen end-on
        self.origin = None            # view mm
        self.origin_name = None
        self.origin_words = ""
        self.off = (0.0, 0.0)         # sheet = off + scale * view mm
        self.title = []
        self.ann_margin = [0, 0, 0, 0]   # left, bottom, right, top (sheet mm) for annotations
        self.cut_lines = []           # (p, q view mm, letter, look 2D) cutting planes drawn on this view
        self.dims = []                # callables (sheet) -> None, added after placement
        self.extent = project.extent(prims)

    def S(self, p):
        return (self.off[0] + self.scale * p[0], self.off[1] + self.scale * p[1])

    def size(self):
        x0, y0, x1, y1 = self.extent
        return (x1 - x0) * self.scale, (y1 - y0) * self.scale

    def box(self):
        """Sheet box of the geometry."""
        x0, y0, x1, y1 = self.extent
        a, b = self.S((x0, y0)), self.S((x1, y1))
        return (a[0], a[1], b[0], b[1])

    def place_ll(self, x, y):
        """Put the geometry's lower-left corner at sheet (x, y)."""
        x0, y0 = self.extent[0], self.extent[1]
        self.off = (x - self.scale * x0, y - self.scale * y0)


class Feature:
    """A hole, slot or keyhole as the drawing lists it."""

    def __init__(self, f, kind):
        self.f = f
        self.kind = kind          # hole, slot, keyhole
        self.tag = None
        self.reg = None           # feature rationale row
        self.group = None


def wall_word(f, body):
    """'1 wall' for a hole through one wall of a hollow member, 'thru' through a solid, or the depth."""
    if not f.through:
        return "blind %s deep" % fmt(f.depth)
    # hollow: the far side of the run opens into the member's cavity, not outside the part's box
    far = vadd(f.entry, vmul(f.axis, f.depth + 0.5))
    b = body.box
    inside = all(b[k] + 0.4 < far[k] < b[3 + k] - 0.4 for k in range(3) if abs(f.axis[k]) < 0.5)
    inside = inside and (b[[k for k in range(3) if abs(f.axis[k]) > 0.5][0]] + 0.4 <
                         far[[k for k in range(3) if abs(f.axis[k]) > 0.5][0]] <
                         b[3 + [k for k in range(3) if abs(f.axis[k]) > 0.5][0]] - 0.4)
    return "THRU 1 WALL (%s)" % fmt(f.depth) if inside else "THRU (%s)" % fmt(f.depth)


def size_text(feat):
    f = feat.f
    if feat.kind == "hole":
        return "Ø%s" % fmt(f.dia)
    if feat.kind == "keyhole":
        return "KEYHOLE Ø%s + SLOT %s, %s TO END" % (fmt(f.entry_dia), fmt(f.width), fmt(f.neck))
    return "SLOT %s x %s OVERALL, R%s ENDS" % (fmt(f.width), fmt(f.length), fmt(f.width / 2))


FACE_WORDS = {"-Z": "bottom face", "+Z": "top face", "-Y": "front face", "+Y": "back face", "-X": "left face",
              "+X": "right face"}
VIEW_WORDS = {"principal": "PRINCIPAL VIEW", "above": "VIEW FROM ABOVE", "below": "VIEW FROM BELOW",
              "from_left": "VIEW FROM THE LEFT", "from_right": "VIEW FROM THE RIGHT", "rear": "REAR VIEW"}
POSITION = {"above": (0, -1), "below": (0, 1), "from_left": (1, 0), "from_right": (-1, 0), "rear": (2, 0)}


class Part:
    """Everything one drawing needs, read from the sources."""

    def __init__(self, pn, team, step=None, pod_system=True, row=None):
        self.pn = pn
        self.team = team
        self.step = step or inputs.own_step(pn)
        if row is not None:         # a test's own part: its row given, no parts list file
            self.row, self.cut_rows, self.list_file = row, [], None
        else:
            self.row, self.cut_rows, self.list_file = inputs.parts_row(pn, team)
        if not self.row:
            raise NotDrawable("%s has no parts-list row in v2/03-Manufacturing/%s" % (pn, team))
        if not self.step:
            # a part that lives only in its team's assembly STEP: that file's geometry, and the revision of its
            # parts list (the mechanical check reads it so)
            import tabulated
            self.step = tabulated.find_step(pn, team)
            if not self.step:
                raise NotDrawable("%s has no STEP under v2/03-Manufacturing/%s" % (pn, team))
            self.rev = inputs.parse_name(self.list_file)["rev"]
            self.file_name = inputs.ascii_name(self.row["name"])
        else:
            nm = inputs.parse_name(self.step)
            self.rev = nm["rev"]
            self.file_name = nm["name"]
        self.name = self.row.get("name", "").strip()
        self.name_vi = (self.row.get("name_vi") or "").strip()
        self.bodies, self.unit = geom.load_part(self.step, pn)
        self.placement = None
        if pod_system:
            self._to_pod()
        self.shape = geom.compound([b.shape for b in self.bodies])
        self.pod_system = pod_system
        self.features = []
        for b in self.bodies:
            hs, ss = geom.features(b)
            bad = geom.unexplained_curved_faces(b, hs, ss)
            if bad:
                raise NotDrawable("%s body %s has faces this tool can't dimension: %s" % (
                    pn, b.name, ", ".join(sorted({"%s r%s" % (k, fmt(r)) if r else k for k, r in bad}))))
            for h in hs:
                ft = Feature(h, "hole")
                ft.body = b
                self.features.append(ft)
            for s in ss:
                ft = Feature(s, s.kind)
                ft.body = b
                self.features.append(ft)
        why = folded_or_bent(self)
        if why:
            raise NotDrawable("%s is %s: bent and folded parts stay with Fusion (D-113)" % (pn, why))
        self.reg = inputs.feature_rows(pn, team)
        for ft in self.features:
            ax = axis_name(ft.f.axis)
            if ax and ft.kind == "hole":
                ctr = vadd(ft.f.entry, vmul(ft.f.axis, ft.f.depth / 2))
                ft.reg = inputs.match_feature(self.reg, ft.body.name, ft.f.dia, ax[1], ctr)
            elif ax and ft.kind == "slot":
                # the register lists a slot as the two arcs of its ends
                half = (ft.f.length - ft.f.width) / 2
                for sgn in (1, -1):
                    c = vadd(vadd(ft.f.entry, vmul(ft.f.along, sgn * half)), vmul(ft.f.axis, ft.f.depth / 2))
                    ft.reg = ft.reg or inputs.match_feature(self.reg, ft.body.name, ft.f.width, ax[1], c)
        b = [bb.box for bb in self.bodies]
        self.box = tuple(min(x[k] for x in b) for k in range(3)) + tuple(max(x[3 + k] for x in b) for k in range(3))
        # the second register layout (BASE): matched by size, wall and a named pod coordinate
        if not any(ft.reg for ft in self.features):
            rows_b = inputs.feature_rows_b(team, pn)
            for ft in self.features:
                nrm = ft.f.normal
                k = max(range(3), key=lambda i: abs(nrm[i]))
                if k == 2:
                    wall = "top" if nrm[2] > 0 else "bottom"
                else:
                    wall = "inner" if ft.f.entry[k] * nrm[k] < 0 else "outer"
                dia = ft.f.entry_dia if ft.kind == "keyhole" else ft.f.dia
                along = max(range(3), key=lambda i: ft.body.size[i])
                r = inputs.match_feature_b(rows_b, dia, wall, ft.f.entry, keyhole=(ft.kind == "keyhole"), along=along)
                if r:
                    ft.reg = {"id": r["id"], "function": r["title"], "mating": r["function"], "file": r["file"]}

    def _to_pod(self):
        """A part file in its own system (as BASE exports its tubes) is drawn where it sits in the pod: the
        rotation and shift come from the team's assembly STEP holding the same part, checked hole for hole
        (geom.find_placement); the drawing states the mapping (guideline 3.3)."""
        b = [bb.box for bb in self.bodies]
        lo = [min(x[k] for x in b) for k in range(3)]
        if max(abs(v) for v in lo) > 1.0:
            return          # not at its own origin: already in the pod system
        folder = os.path.dirname(self.step)
        for asm in sorted(os.listdir(folder)):
            nm = inputs.parse_name(os.path.join(folder, asm))
            if not nm or nm["doc"] != "STEP" or nm["pn"] == self.pn or not asm.endswith(".step"):
                continue
            try:
                ab, _u = geom.load_part(os.path.join(folder, asm), self.pn)
            except (LookupError, ValueError, RuntimeError):
                continue
            pl = geom.find_placement(self.bodies, ab)
            if pl is None:
                continue
            m, t = pl
            for bb in self.bodies:
                bb2 = geom.Body(bb.name, geom.placed(bb.shape, m, t))
                bb.shape, bb.box, bb.centroid = bb2.shape, bb2.box, bb2.centroid
            names = "XYZ"
            words = []
            for j in range(3):          # where the part's own X, Y, Z point in the pod
                col = [m[i][j] for i in range(3)]
                i = max(range(3), key=lambda i: abs(col[i]))
                words.append("%s(part) = %s%s(pod)" % (names[j], "+" if col[i] > 0 else "-", names[i]))
            self.placement = {"assembly": inputs.rel(os.path.join(folder, asm)), "words": ", ".join(words),
                              "shift": t, "m": m}
            return

    @property
    def size(self):
        return tuple(self.box[3 + k] - self.box[k] for k in range(3))

    @property
    def dwg_name(self):
        return "%s_%s_%s_DWG" % (self.pn, self.rev, self.file_name)


BENT_WORDS = re.compile(r"\b(?:bend|bends|bent|fold|folds|folded|brake|v-groove|groove and fold|press brake)\b", re.I)


def folded_or_bent(part):
    """Why the part is a bent or folded sheet, or None. Its process says so, or its geometry does: a thin-walled
    body whose sheet faces run in two or more directions while its cross-section is one open outline (a tube's
    cross-section closes round its bore, so a tube is not folded). Sharp folds count too (an ACP skin's V-groove
    fold has no bend radius in the model)."""
    proc = (part.row.get("process") or "") + " " + (part.row.get("name") or "")
    m = BENT_WORDS.search(proc)
    if m:
        return "bent or folded (its parts list says '%s')" % m.group(0)
    for b in part.bodies:
        pls = geom.planes(b)
        if not pls:
            continue
        big = max(a for _n, _o, a, _f in pls)
        dirs = []
        for i, (n1, o1, a1, f1) in enumerate(pls):
            if a1 < 0.05 * big:
                continue
            for n2, o2, a2, f2 in pls[i + 1:]:
                if a2 < 0.05 * big or vdot(n1, n2) > -0.9999:
                    continue
                gap = -(o1 + o2)          # opposite normals: offsets o1 = n.p1, o2 = -n.p2
                if 0.2 < abs(gap) < 6.0:
                    d = geom.canon_dir(n1)
                    if not any(abs(abs(vdot(d, e)) - 1) < 1e-4 for e in dirs):
                        dirs.append(d)
        if len(dirs) < 2:
            continue
        # open or closed cross-section, across the long direction, at three places (one may cut through a hole)
        lk = max(range(3), key=lambda k: b.size[k])
        n = tuple(1.0 if k == lk else 0.0 for k in range(3))
        from OCP.TopAbs import TopAbs_WIRE
        opens = 0
        for t in (0.31, 0.47, 0.63):
            pt = tuple(b.box[k] + t * b.size[k] if k == lk else b.centroid[k] for k in range(3))
            faces = cut_faces(geom.half_space_keep(b.shape, pt, n), pt, n)
            wires = 0
            for f in faces:
                e = TopExp_Explorer(f, TopAbs_WIRE)
                while e.More():
                    wires += 1
                    e.Next()
            opens += bool(faces) and wires == len(faces)
        if opens == 3:
            return "a folded sheet (body %s: sheet faces in %d directions, open cross-section)" % (b.name, len(dirs))
    return None


def principal_view(part):
    """Look along the part's thinnest direction, from the side most of its holes are drilled from; on a tie, from
    the pod's centre (the room side: both hands of a mirrored pair are then drawn from the same side, and the
    RH sheet is the LH sheet's mirror image), else the pod's standard view for that axis."""
    k = min(range(3), key=lambda i: part.size[i])
    axis = tuple(1.0 if i == k else 0.0 for i in range(3))
    count = {+1: 0, -1: 0}
    for ft in part.features:
        d = vdot(ft.f.normal, axis)
        if abs(abs(d) - 1) < 1e-6:
            count[1 if d > 0 else -1] += 1
    if count[1] != count[-1]:
        sign = 1 if count[1] > count[-1] else -1
    elif part.pod_system and abs(part.box[k] + part.box[3 + k]) > 1.0:
        sign = -1 if part.box[k] + part.box[3 + k] > 0 else 1     # toward the pod's centre
    else:
        sign = {0: 1, 1: -1, 2: 1}[k]
    n = vmul(axis, float(sign))
    name = next(nm for nm, (vn, vx, vy) in project.POD_VIEWS.items() if vdot(vn, n) > 0.9999)
    vn, vx, vy = project.POD_VIEWS[name]
    v = View("principal", vn, vx, vy)
    v.pod_name = name
    return v


def face_groups(part):
    groups = {}
    for ft in part.features:
        nrm = ft.f.normal
        key = (axis_name(nrm) or "%.3f,%.3f,%.3f" % nrm, round(vdot(ft.f.entry, nrm), 2))
        groups.setdefault(key, []).append(ft)
    return groups


def two_wall_sets(part):
    """Coaxial hole runs in two walls of one body (D-113): {(body, axis line): [features]}."""
    sets = {}
    for ft in part.features:
        if ft.kind != "hole" or not ft.f.partners:
            continue
        sets.setdefault((id(ft.body), ft.f.line_key), []).append(ft)
    return [v for v in sets.values() if len(v) >= 2]


# ------------------------------------------------------------------ datum scheme

def spigot_origin(part):
    """WALL and CEILING frames sit on two spigots: a round hole and a slot in the bottom rail (joints register
    R-J13; R-J6 positions every bolt hole from the round one). Datums: A the face they enter (the seat), B the
    round hole's axis, C the slot. Origin O: datum B's axis on datum A."""
    rounds = [ft for ft in part.features if ft.kind == "hole" and ft.reg and "spigot" in
              (ft.reg["function"] + ft.reg["mating"]).lower() and "slot" not in ft.reg["function"].lower()[:12]]
    rounds = [ft for ft in rounds if abs(ft.f.dia - 8.5) < 0.05] or rounds
    slots = [ft for ft in part.features if ft.kind == "slot"]
    if not rounds or not slots:
        return None
    b = rounds[0]
    # C must stop the turn about B. The slot runs across the rail (R-J17: the panel closes onto its neighbour across
    # the corner gap), so it can't; the frame's room-side face, square to the wall and parallel to B, does.
    k = min(range(3), key=lambda i: part.size[i])
    toward_centre = -1.0 if part.box[k] + part.box[3 + k] > 0 else 1.0
    c_normal = tuple(toward_centre if i == k else 0.0 for i in range(3))
    c_plane = part.box[3 + k] if toward_centre > 0 else part.box[k]
    return {"O": b.f.entry, "A_normal": b.f.normal, "B": b, "C": None, "C_plane": (c_normal, c_plane),
            "slot": slots[0],
            "words": {"A": "%s of %s (the seat on the band)" % (FACE_WORDS.get(axis_name(b.f.normal), "face"),
                                                              b.body.name),
                      "B": "axis of the spigot hole %s" % "{B}",
                      "C": "the room-side face (%s %s), which stops the turn about B" % ("XYZ"[k], fmt(c_plane))}}


def corner_origin(part, corner):
    """Origin at a corner of the part's faces, e.g. corner='-X-Y-Z' (the faces at min X, min Y, min Z)."""
    c = []
    for k, n in enumerate("XYZ"):
        c.append(part.box[k] if ("-" + n) in corner else part.box[3 + k])
    return {"O": tuple(c), "A_normal": None, "B": None, "C": None, "words": {}}


def spec_origin(part, spec):
    dat = corner_origin(part, spec.get("corner", "-X-Y-Z"))
    dat["words"] = dict(spec.get("datum_words", {}))
    return dat


# ------------------------------------------------------------------ view planning

class Plan:
    pass


def plan_views(part, spec):
    """Decide the views: principal, the plain related views that show a drilled face, sections in front of
    the faces nothing shows, and removed sections through two-wall holes. Returns a Plan."""
    pl = Plan()
    if isinstance(spec.get("principal"), dict):
        # {"look": "+Z", "x": "-X"}: the way the viewer looks and the view's X, as pod axes
        ax = lambda a: tuple((1.0 if a[0] == "+" else -1.0) if i == "XYZ".index(a[1]) else 0.0 for i in range(3))
        pl.principal = View("principal", vmul(ax(spec["principal"]["look"]), -1.0), ax(spec["principal"]["x"]))
        pl.principal.pod_name = "custom"
    elif spec.get("principal"):
        vn, vx, vy = project.POD_VIEWS[spec["principal"]]
        pl.principal = View("principal", vn, vx, vy)
        pl.principal.pod_name = spec["principal"]
    else:
        pl.principal = principal_view(part)
    # a long part seen end up: turn the view so its length runs across the sheet (every view states its mapping)
    P0 = pl.principal
    ext_x = sum(abs(P0.x[i]) * part.size[i] for i in range(3))
    ext_y = sum(abs(P0.y[i]) * part.size[i] for i in range(3))
    if ext_y > 2.0 * ext_x:
        nx = P0.y if (P0.y[0] + P0.y[1] + P0.y[2]) > 0 else vmul(P0.y, -1.0)
        pl.principal = View("principal", P0.n, nx)
        pl.principal.pod_name = getattr(P0, "pod_name", "") + " turned"
    rel = {"principal": pl.principal}
    for nm in ("above", "below", "from_left", "from_right", "rear"):
        rel[nm] = project.related(pl.principal, nm)
    pl.rel = rel
    pl.groups = []
    pl.sections = []
    pl.removed = []
    pl.plain = {"principal"}
    for key, feats in sorted(face_groups(part).items(), key=lambda kv: kv[0]):
        normal = feats[0].f.normal
        vname = next((nm for nm, v in rel.items() if vdot(v.n, normal) > 0.9999), None)
        if vname is None:
            raise NotDrawable("%s has holes on a face at an angle to every principal view (normal %s)" % (
                part.pn, key[0]))
        blocked, free = False, 1e9
        for ft in feats:
            inter = IntCurvesFace_ShapeIntersector()
            inter.Load(part.shape, 1e-6)
            inter.Perform(gp_Lin(gp_Pnt(*vadd(ft.f.entry, vmul(normal, 0.02))), gp_Dir(*normal)), 0.0, 1e7)
            if inter.IsDone() and inter.NbPnt() > 0:
                blocked = True
                free = min(free, min(inter.WParameter(i) for i in range(1, inter.NbPnt() + 1)))
        g = Plan()
        g.key, g.feats, g.normal, g.vname = key, feats, normal, vname
        g.plane = key[1]
        g.coax_of = None
        g.blocked = blocked
        g.free = free
        pl.groups.append(g)
    # a face nothing shows: when every hole on it is the far-wall twin of a hole on a face that a plain view
    # shows (same member, same axis), the removed section through the pair shows it (D-113) and its table
    # uses that view's X and Y; any other hidden face gets its own section just in front of it
    by_feat = {id(ft): g for g in pl.groups for ft in g.feats}
    for g in pl.groups:
        if not g.blocked:
            g.view = g.vname
            pl.plain.add(g.vname)
    for g in pl.groups:
        if not g.blocked:
            continue
        twins = []
        for ft in g.feats:
            outer = [o for o in part.features if o is not ft and o.body is ft.body and o.kind == "hole" and
                     o.f.line_key == ft.f.line_key and not by_feat[id(o)].blocked]
            twins.append(outer[0] if outer else None)
        if all(twins):
            og = by_feat[id(twins[0])]
            g.coax_of = og
            g.view = og.view
            for ft, tw in zip(g.feats, twins):
                ft.twin = tw
            continue
        d = min(1.0, 0.5 * g.free)
        g.section_point = vadd(g.feats[0].f.entry, vmul(g.normal, d))
        g.view = None
        pl.sections.append(g)
    # removed sections through two-wall holes (D-113), one per body and pattern
    seen = set()
    for st in two_wall_sets(part):
        ft = sorted(st, key=lambda f: (f.f.dia))[0]
        body = ft.body
        sz = body.size
        long_k = max(range(3), key=lambda k: sz[k])
        long_dir = tuple(1.0 if k == long_k else 0.0 for k in range(3))
        pattern = (id(body), tuple(sorted(round(f.f.dia, 2) for f in st)), axis_name(geom.canon_dir(ft.f.axis)))
        same = [s for s in two_wall_sets(part) if s[0].body is body and
                tuple(sorted(round(f.f.dia, 2) for f in s)) == pattern[1]]
        if pattern in seen:
            continue
        seen.add(pattern)
        r = Plan()
        r.feats = st
        r.all = same
        r.body = body
        y = geom.canon_dir(ft.f.axis)
        # look along the member, from the principal view's side where possible
        n = long_dir
        if vdot(vcross(n, vcross(y, n)), y) < 0:
            n = vmul(n, -1.0)
        r.point = vadd(ft.f.entry, vmul(ft.f.axis, ft.f.depth / 2))
        r.n = n
        r.y = y
        pl.removed.append(r)
    # a thin plate or strip: a section across its middle shows the thickness the plan view can't (guideline 6.1)
    k = min(range(3), key=lambda i: part.size[i])
    if not pl.removed and part.size[k] < 6.0 and len(part.bodies) == 1:
        b = part.bodies[0]
        lk = max(range(3), key=lambda i: part.size[i])
        r = Plan()
        r.feats, r.all, r.body = [], [], b
        r.n = tuple(1.0 if i == lk else 0.0 for i in range(3))
        r.y = tuple(1.0 if i == k else 0.0 for i in range(3))
        r.point = b.centroid
        r.thin = True
        pl.removed.append(r)
    return pl


def view_prims(shape, view, scale, min_paper=0.6, bodies=None, hidden_from=None):
    if bodies is not None:
        pr = project.project_bodies(bodies, view, hidden_from)
    else:
        pr = project.project(shape, view)
    # ISO 128-20 practice: leave out hidden lines that print on top of a visible one, and hidden scraps too
    # short to read at this scale
    pr = project.drop_hidden_near(pr, 0.5 / scale)
    pr = project.merge_close_hidden(pr, 0.5 / scale)
    out = []
    for p in pr:
        if not p.vis:
            x0, y0, x1, y1 = p.bbox()
            if max(x1 - x0, y1 - y0) * scale < min_paper:
                continue
        out.append(p)
    return out


# ------------------------------------------------------------------ drawing

def _end_on(ft, view):
    return abs(abs(vdot(ft.f.axis, view.n)) - 1.0) < 1e-6


def _trace(view, point, normal, ext):
    """The cutting plane's trace on a view, as a 2D segment spanning ext (x0, y0, x1, y1) plus 6 mm-ish."""
    c = view.to2d(point)
    if abs(abs(vdot(normal, view.x)) - 1) < 1e-6:
        return (c[0], ext[1]), (c[0], ext[3])
    if abs(abs(vdot(normal, view.y)) - 1) < 1e-6:
        return (ext[0], c[1]), (ext[2], c[1])
    return None


def draw(part, spec, out_path, today=None):
    """Write the drawing PDF of part to out_path. spec: per-part options (see specs.py). Returns a report dict."""
    pl = plan_views(part, spec)
    if spec.get("datums") == "spigot":
        dat = spigot_origin(part)
        if dat is None:
            raise NotDrawable("%s: no spigot hole and slot found for its datums" % part.pn)
    else:
        dat = spec_origin(part, spec)
    O = dat["O"]

    # ---- tags, in the order the tables list them
    order = ["principal", "below", "above", "from_left", "from_right", "rear"]
    groups = sorted(pl.groups, key=lambda g: (g.view is None, order.index(g.view or g.vname),
                                              g.coax_of is not None, g.key))
    n = 0
    for g in groups:
        view = pl.rel[g.view or g.vname]
        # by distance from the origin along X, then Y: a mirrored part (RH) gets the same tags as its LH twin
        g.feats.sort(key=lambda ft: (round(abs(view.to2d(ft.f.entry)[0] - view.to2d(O)[0]), 2),
                                     round(abs(view.to2d(ft.f.entry)[1] - view.to2d(O)[1]), 2)))
        for ft in g.feats:
            n += 1
            ft.tag = "H%02d" % n
            ft.group = g

    # ---- scale and sheet
    size = spec.get("sheet", "A1")
    sh = Sheet(size, title="%s %s" % (part.pn, part.name), subject="%s %s %s" % (part.dwg_name, part.rev, "DRAFT"),
               keywords="drawgen; D-112; source %s sha256:%s" % (inputs.rel(part.step), inputs.sha12(part.step)))
    W, H = sh.W, sh.H
    right_w = spec.get("right_w", spec.get("table_w", TABLE_W) + 16.0)
    avail_w = W - 20 - 10 - right_w - 20
    avail_h = H - 20 - 30
    P = pl.principal

    def ext_of(view, shape=None):
        return project.extent(project.project(shape or part.shape, view))

    exts = {nm: ext_of(pl.rel[nm]) for nm in pl.plain}
    sec_ext = {}
    for i, g in enumerate(pl.sections):
        g.kept = geom.half_space_keep(part.shape, g.section_point, g.normal)
        v = pl.rel[g.vname]
        g.sview = View("section", v.n, v.x, v.y)
        sec_ext[i] = ext_of(g.sview, g.kept)
    GAP = 40.0          # between stacked views: the title under a view, then the next view's tags, dimensions
    GAP_PB = 62.0       # under the principal: its overall dimension, its title, then the next view's dimensions
    GAP_PL = 40.0       # left of the principal: its height dimension
    GAP_PT = 52.0       # over the principal: member positions or section letters and datum symbols

    def block(scale, rear_down=False):
        wx = lambda e: (e[2] - e[0]) * scale
        hy = lambda e: (e[3] - e[1]) * scale
        pw, ph = wx(exts["principal"]), hy(exts["principal"])
        up = sum(hy(exts[n_]) + GAP for n_ in ("below",) if n_ in exts) + \
            sum(hy(sec_ext[i]) + GAP for i, g in enumerate(pl.sections) if g.vname == "below") + (GAP_PT - GAP)
        down = sum(hy(exts[n_]) + GAP for n_ in ("above",) if n_ in exts) + \
            sum(hy(sec_ext[i]) + GAP for i, g in enumerate(pl.sections) if g.vname == "above") + (GAP_PB - GAP)
        beside = ("from_left",) if rear_down else ("from_left", "rear")
        right = sum(wx(exts[n_]) + GAP for n_ in beside if n_ in exts) + \
            sum(wx(sec_ext[i]) + GAP for i, g in enumerate(pl.sections) if g.vname in ("from_left", "rear", "principal"))
        if rear_down and "rear" in exts:
            down += hy(exts["rear"]) + GAP
        left = sum(wx(exts[n_]) + GAP for n_ in ("from_right",) if n_ in exts) + \
            sum(wx(sec_ext[i]) + GAP for i, g in enumerate(pl.sections) if g.vname == "from_right") + (GAP_PL - GAP)
        return left + pw + right + 2 * GAP, up + ph + down + 2 * GAP
    scale, rear_down = None, False
    for s in ISO_SCALES:
        if spec.get("scale") and abs(s - spec["scale"]) > 1e-9:
            continue
        for rd in ((False, True) if "rear" in exts else (False,)):
            bw, bh = block(s, rd)
            if bw <= avail_w and bh <= avail_h:
                scale, rear_down = s, rd
                break
        if scale:
            break
    if scale is None:
        raise NotDrawable("%s doesn't fit on %s at any ISO scale down to 1:20" % (part.pn, size))
    bw, bh = block(scale, rear_down)
    pl.rear_down = rear_down

    # ---- the view objects
    vds = {}
    shapes = [b.shape for b in part.bodies]
    for nm in sorted(pl.plain, key=order.index):
        v = pl.rel[nm]
        # hidden detail only of the members whose face this view shows (all of them in the principal view)
        own = {id(ft.body) for g in pl.groups if g.view == nm for ft in g.feats}
        hid = None if nm == "principal" or not own else {i for i, b in enumerate(part.bodies) if id(b) in own}
        vd = VD(v, view_prims(part.shape, v, scale, bodies=shapes, hidden_from=hid), scale)
        vd.name = nm
        vds[nm] = vd
    letters = iter("ABCDEFGHJKLMNPRSTUVWXYZ")
    secs = []
    for g in pl.sections:
        v = g.sview
        own = {id(ft.body) for ft in g.feats}
        kept, hid = [], set()
        for b in part.bodies:
            k_ = geom.half_space_keep(b.shape, g.section_point, g.normal)
            if geom._solids(k_):
                if id(b) in own:
                    hid.add(len(kept))
                kept.append(k_)
        vd = VD(v, view_prims(g.kept, v, scale, bodies=kept, hidden_from=hid), scale, "section")
        for f in cut_faces(g.kept, g.section_point, g.normal):
            vd.hatch.append(face_loops(f, v))
        g.letter = next(letters)
        vd.letter = g.letter
        vd.name = "section"
        vd.group = g
        g.vd = vd
        secs.append(vd)
    removed = []
    for r in pl.removed:
        x = vcross(r.y, r.n)
        v = View("removed", r.n, x, r.y)
        kept = geom.half_space_keep(r.body.shape, r.point, r.n)
        loops = [face_loops(f, v) for f in cut_faces(kept, r.point, r.n)]
        prims = [p for lp in loops for p in lp]
        rs = None
        for s in (10.0, 5.0, 2.0, 1.0, 0.5):
            e = project.extent(prims)
            if max(e[2] - e[0], e[3] - e[1]) * s <= (150 if getattr(r, "thin", False) else 110) and \
                    (s <= 5.0 or getattr(r, "thin", False)):
                rs = s
                break
        vd = VD(v, prims, rs or 1.0, "removed")
        vd.hatch = loops
        vd.letter = next(letters)
        vd.name = "removed"
        vd.r = r
        r.vd = vd
        r.letter = vd.letter
        removed.append(vd)

    # ---- placement: principal, then the first-angle neighbours and the sections stacked beyond them
    x_left = 20 + GAP_PL
    pvd = vds["principal"]
    pw, ph = pvd.size()
    left_w = sum(vds[n_].size()[0] + GAP for n_ in ("from_right",) if n_ in vds) + \
        sum(s.size()[0] + GAP for s in secs if s.group.vname == "from_right")
    up_h = sum(vds[n_].size()[1] + GAP for n_ in ("below",) if n_ in vds) + \
        sum(s.size()[1] + GAP for s in secs if s.group.vname == "below") + (GAP_PT - GAP)
    down_h = bh - 2 * GAP - ph - up_h
    block_h = up_h + ph + down_h
    top = H - 10 - 30           # top-aligned (room above for the top view's dimensions and datum symbols)
    px = x_left + left_w
    py = top - up_h - ph - 4
    pvd.place_ll(px, py)
    # neighbours
    def stack(names, axis, sign):
        cur = None
        for item in names:
            if axis == "y":
                if sign > 0:        # upward from the principal's top
                    y = (pvd.box()[3] + GAP_PT) if cur is None else cur + GAP
                    item.off = (0, 0)
                    item.place_ll(0, 0)
                    x_al = pvd.off[0] + pvd.scale * 0     # align X with the principal
                    item.off = (pvd.off[0] - 0 + (item.scale - pvd.scale) * 0, y - item.scale * item.extent[1])
                    cur = item.box()[3]
                else:
                    y = (pvd.box()[1] - GAP_PB) if cur is None else cur - GAP
                    item.off = (pvd.off[0], y - item.scale * item.extent[3])
                    cur = item.box()[1]
            else:
                if sign > 0:
                    x = (pvd.box()[2] if cur is None else cur) + GAP
                    item.off = (x - item.scale * item.extent[0], pvd.off[1])
                    cur = item.box()[2]
                else:
                    x = (pvd.box()[0] - GAP_PL) if cur is None else cur - GAP
                    item.off = (x - item.scale * item.extent[2], pvd.off[1])
                    cur = item.box()[0]
        return cur
    # projected views share the principal's X (or Y) axis only when their own X (Y) maps to the same 3D axis
    def aligned_items(slot):
        items = ([vds[slot]] if slot in vds else []) + [s for s in secs if s.group.vname == slot]
        return items
    stack(aligned_items("below"), "y", +1)
    stack(aligned_items("above"), "y", -1)
    right_items = aligned_items("from_left") + ([] if rear_down else aligned_items("rear")) + \
        aligned_items("principal")[1:]
    stack(right_items, "x", +1)
    stack(aligned_items("from_right"), "x", -1)
    if rear_down and "rear" in vds:
        # too long to sit beside: under the other views as a lettered view with a reference arrow (ISO 128-30)
        rv = vds["rear"]
        lowest = min([pvd.box()[1] - GAP_PB + GAP] + [it.box()[1] for it in aligned_items("above")])
        y = lowest - GAP
        rv.off = (pvd.box()[0] - rv.scale * rv.extent[0], y - rv.scale * rv.extent[3])
        rv.letter = next(letters)
    # check the X/Y alignment assumption: a view stacked above/below shares the principal's x axis
    for item in aligned_items("below") + aligned_items("above"):
        assert abs(vdot(item.view.x, P.x) - 1) < 1e-9
    for item in right_items + aligned_items("from_right"):
        assert abs(vdot(item.view.y, P.y) - 1) < 1e-9

    main_right = max([v.box()[2] for v in vds.values()] + [s.box()[2] for s in secs])
    main_bottom = min([v.box()[1] for v in vds.values()] + [s.box()[1] for s in secs])
    # removed sections: a column between the views and the tables when it is wide enough, else a row under the views
    mid_x0 = main_right + GAP + 18
    mid_x1 = W - 10 - spec.get("table_w", TABLE_W) - 4 - 10
    need_w = (max(vd.size()[0] for vd in removed) + 70) if removed else 0
    if removed and mid_x1 - mid_x0 >= need_w:
        rx, ry = mid_x0, H - 10 - 30
        for vd in removed:
            w, h = vd.size()
            vd.off = (rx - vd.scale * vd.extent[0], ry - h - vd.scale * vd.extent[1])
            ry = ry - h - 58
    elif removed:
        rx, ry = 20 + GAP_PL + 14, main_bottom - 34
        for vd in removed:
            w, h = vd.size()
            vd.off = (rx - vd.scale * vd.extent[0], ry - h - vd.scale * vd.extent[1])
            rx += w + 80
    pl.mid = (main_right + GAP, 0)
    report = {"pn": part.pn, "rev": part.rev, "scale": scale, "sheet": size, "views": [], "holes": []}

    # ---- draw geometry
    def draw_prims(vd):
        for p in vd.prims:
            w = W_VIS if p.vis else W_HID
            d = None if p.vis else DASH_HID
            if p.kind == "line":
                sh.line(vd.S(p.p), vd.S(p.q), w, d)
            elif p.kind == "arc":
                if not p.vis:       # a small hidden circle gets dashes it can show (8 a turn at most)
                    L = p.r * vd.scale * (p.a1 - p.a0)
                    d = (min(DASH_HID[0], L / 12), min(DASH_HID[1], L / 24))
                sh.arc(vd.S(p.c), p.r * vd.scale, p.a0, p.a1, w, d)
            else:
                sh.bezier([vd.S(q) for q in p.pts], w, d)
        for loop in vd.hatch:
            sl = []
            for p in loop:
                if p.kind == "line":
                    sl.append(("line", vd.S(p.p), vd.S(p.q)))
                elif p.kind == "arc":
                    sl.append(("arc", vd.S(p.c), p.r * vd.scale, p.a0, p.a1))
            # ISO 128-50: hatch at 45 degrees; a thin wall under 2 mm on paper is filled solid
            thin = min((vd.scale * 1.5), 99) < 2.0 and vd.kind == "removed"
            narrow = _narrowest(loop) * vd.scale
            if narrow < 1.6:
                sh.fill_loops([sl])
            else:
                sh.hatch([sl], spacing=max(0.8, min(2.5, narrow / 2.5)), angle=45.0, w=0.18)
            if vd.kind == "removed":
                for p in loop:
                    if p.kind == "line":
                        sh.line(vd.S(p.p), vd.S(p.q), W_VIS)
                    elif p.kind == "arc":
                        sh.arc(vd.S(p.c), p.r * vd.scale, p.a0, p.a1, W_VIS)
    for vd in list(vds.values()) + secs + removed:
        draw_prims(vd)
    sh.flush()

    # ---- marks, tags, origins
    tag_side = {}

    def mark_features(vd, feats, tags=True):
        placed = []
        at = {}
        for ft in feats:
            if not _end_on(ft, vd.view):
                continue
            c2 = vd.S(vd.view.to2d(ft.f.entry))
            at.setdefault((round(c2[0], 2), round(c2[1], 2)), []).append(ft)
        for key, fts in sorted(at.items()):
            fts.sort(key=lambda f: f.tag or "")
            ft = fts[0]
            c2 = vd.S(vd.view.to2d(ft.f.entry))
            r = max((f.f.entry_dia if f.kind == "keyhole" else f.f.dia) / 2 for f in fts) * vd.scale
            r0 = (ft.f.entry_dia if ft.kind == "keyhole" else ft.f.dia) / 2 * vd.scale
            if ft.kind == "hole":
                sh.centre_mark(c2, r, ext=1.5)
            else:
                a2 = vd.view.to2d(ft.f.along)
                L = (ft.f.length - ft.f.width) / 2 if ft.kind == "slot" else ft.f.neck
                if ft.kind == "slot":
                    e1 = vd.S(vd.view.to2d(vadd(ft.f.entry, vmul(ft.f.along, -L))))
                    e2 = vd.S(vd.view.to2d(vadd(ft.f.entry, vmul(ft.f.along, L))))
                else:
                    e1 = c2
                    e2 = vd.S(vd.view.to2d(vadd(ft.f.entry, vmul(ft.f.along, L))))
                if ft.f.length * vd.scale >= 6.0:
                    for e in (e1, e2):
                        sh.centre_mark(e, ft.f.width / 2 * vd.scale, ext=1.2)
                    sh.centre_line((e1[0] - a2[0] * 3, e1[1] - a2[1] * 3), (e2[0] + a2[0] * 3, e2[1] + a2[1] * 3))
                else:
                    sh.centre_mark(vd.S(vd.view.to2d(ft.f.entry)), ft.f.length / 2 * vd.scale, ext=1.5)
            labels = [f.tag for f in fts if f.tag]
            if tags and labels:
                close = [p for p in placed if math.dist(p, c2) < 9.0]
                up = (len(close) % 2 == 0)
                d = (0.55, 1.0) if up else (0.55, -1.0)
                sh.tag(c2, r, "/".join(labels), d, size=2.5, leader=4.5)
                placed.append(c2)

    for nm, vd in vds.items():
        feats = [ft for g in pl.groups if g.view == nm for ft in g.feats]
        mark_features(vd, feats)
        # the far-wall holes behind (hidden circles) get their centre marks too, untagged
        keys = {(id(ft.body), ft.f.line_key) for ft in feats if ft.kind == "hole"}
        others = [ft for ft in part.features if ft not in feats and _end_on(ft, vd.view) and ft.kind == "hole"
                  and (id(ft.body), ft.f.line_key) in keys]
        mark_features(vd, others, tags=False)
    for vd in secs:
        mark_features(vd, vd.group.feats)
    sh.flush()

    # origins: one 3D origin O, its projection named per view
    onames = {}
    k = 0
    for vd in [vds[n_] for n_ in order if n_ in vds] + secs:
        k += 1
        vd.origin_name = "O%d" % k
        o2 = vd.S(vd.view.to2d(O))
        if part.features:
            bx = vd.box()
            away = (-1.0 if o2[0] <= (bx[0] + bx[2]) / 2 else 1.0, -1.0 if o2[1] <= (bx[1] + bx[3]) / 2 else 1.0)
            sh.origin_mark(o2, vd.origin_name, away=away)
        onames[id(vd)] = vd.origin_name
    sh.flush()
    return sh, pl, vds, secs, removed, dat, scale, report, groups


def _vertices(face):
    from OCP.TopAbs import TopAbs_VERTEX
    e = TopExp_Explorer(face, TopAbs_VERTEX)
    while e.More():
        yield e.Current()
        e.Next()


def _narrowest(loop):
    """A rough narrowest width of a cut face (true mm): the smallest distance between parallel opposite lines."""
    lines = [p for p in loop if p.kind == "line"]
    best = 1e9
    for i, a in enumerate(lines):
        ax, ay = a.q[0] - a.p[0], a.q[1] - a.p[1]
        la = math.hypot(ax, ay)
        if la < 1e-9:
            continue
        for b in lines[i + 1:]:
            bx, by = b.q[0] - b.p[0], b.q[1] - b.p[1]
            lb = math.hypot(bx, by)
            if lb < 1e-9 or abs(ax * by - ay * bx) / (la * lb) > 1e-6:
                continue
            d = abs((b.p[0] - a.p[0]) * ay - (b.p[1] - a.p[1]) * ax) / la
            if d > 1e-6:
                best = min(best, d)
    return best if best < 1e9 else 10.0


# ------------------------------------------------------------------ annotation, tables, notes, title block

def mapping_words(view, pod_system):
    sysname = "pod" if pod_system else "part"
    look = project.LOOK_WORDS.get(view.looking, view.looking or "obliquely")
    return "X = %s, Y = %s (%s axes); looking %s" % (axis_name(view.x), axis_name(view.y), sysname, look)


def feature_text(ft):
    if not ft.reg:
        return ""
    pns = []
    for p in inputs.part_numbers_in(ft.reg["mating"]):
        if p not in pns:
            pns.append(p)
    t = "%s %s" % (ft.reg["id"], inputs.short_function(ft.reg["function"]))
    if pns:
        t += " (%s)" % ", ".join(pns[:3])
    return t


def face_title(part, g):
    ft = g.feats[0]
    bodies = sorted({f.body.name for f in g.feats if f.body.name})
    fw = FACE_WORDS.get(axis_name(g.normal), "face")
    side = ""
    if part.pod_system:
        # the side of the pod the face looks to: the room side when it faces the pod's centre line
        c = ft.f.entry
        k = [i for i in range(3) if abs(g.normal[i]) > 0.5][0]
        thin = min(range(3), key=lambda i: part.size[i])
        if k == thin and k < 2 and c[k] * g.normal[k] < 0:
            side = ", room side"
    inner = " (inside the member's bay)" if getattr(g, "blocked", False) else ""
    return "%s, %s%s%s" % (" + ".join(bodies) or part.name, fw, side, inner)


def annotate(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today):
    P = pl.principal
    O = dat["O"]
    pvd = vds["principal"]
    W, H = sh.W, sh.H
    # ---- view titles
    def title(vd, head, sub):
        """The view's name and scale, and under it its X/Y mapping, centred under the view; a view narrower than
        its title gets the title in short lines starting at its left edge (so it never runs into a neighbour)."""
        x0, y0, x1, y1 = vd.box()
        cx = (x0 + x1) / 2
        y = y0 - (28.0 if vd is pvd else 10.0) - getattr(vd, "title_drop", 0.0)
        if x1 - x0 >= max(sh.text_width(head, 3.5, True), sh.text_width(sub, 2.5)) + 4:
            sh.text(cx, y, head, 3.5, "center", bold=True)
            sh.text(cx, y - 4.2, sub, 2.5, "center")
            return
        xl = x0 - 2.0
        sh.text(xl, y, head, 3.5, "left", bold=True)
        yy = y - 4.2
        for part_ in sub.split("; "):
            sh.text(xl, yy, part_, 2.5, "left")
            yy -= 3.4
    sname = scale_text(scale)
    osfx = (lambda vd: "; origin %s" % vd.origin_name) if part.features else (lambda vd: "")
    for nm, vd in vds.items():
        head = "%s  %s" % (VIEW_WORDS[nm], sname)
        if getattr(vd, "letter", None):
            head = "VIEW %s  %s" % (vd.letter, sname)
        title(vd, head, mapping_words(vd.view, part.pod_system) + osfx(vd))
    for vd in secs:
        g = vd.group
        title(vd, "SECTION %s-%s  %s" % (vd.letter, vd.letter, sname),
              mapping_words(vd.view, part.pod_system) + osfx(vd))
    for vd in removed:
        tags = sorted({f.tag for s in vd.r.all for f in s})
        vd.title_drop = 14.0
        title(vd, "SECTION %s-%s  %s" % (vd.letter, vd.letter, scale_text(vd.scale)),
              ("through %s (typical: %s)" % ("/".join(sorted(f.tag for f in vd.r.feats)), ", ".join(tags)))
              if vd.r.feats else "across the middle, showing the thickness")
        sh.text((vd.box()[0] + vd.box()[2]) / 2, vd.box()[1] - 9.5 - 8.4 - vd.title_drop,
                mapping_words(vd.view, part.pod_system), 2.5, "center")
    # ---- cutting planes on the principal view
    ext = pvd.extent
    for vd in secs:
        g = vd.group
        tr = _trace(P, g.section_point, g.normal, ext)
        if not tr:
            continue
        a, b = pvd.S(tr[0]), pvd.S(tr[1])
        # extend 5 mm past the part
        d = (b[0] - a[0], b[1] - a[1])
        L = math.hypot(*d)
        u = (d[0] / L, d[1] / L)
        a, b = (a[0] - u[0] * 5, a[1] - u[1] * 5), (b[0] + u[0] * 5, b[1] + u[1] * 5)
        look = P.to2d(vmul(g.normal, -1.0))
        sh.section_arrows(a, b, vd.letter, look)
    for vd in removed:
        r = vd.r
        body2d = project.extent(project.project(r.body.shape, P))
        tr = _trace(P, r.point, r.n, body2d)
        if not tr:
            continue
        a, b = pvd.S(tr[0]), pvd.S(tr[1])
        d = (b[0] - a[0], b[1] - a[1])
        L = math.hypot(*d) or 1
        u = (d[0] / L, d[1] / L)
        a, b = (a[0] - u[0] * 6, a[1] - u[1] * 6), (b[0] + u[0] * 6, b[1] + u[1] * 6)
        look = P.to2d(vmul(r.n, -1.0))
        sh.section_arrows(a, b, vd.letter, look, size=3.5)
    sh.flush()
    for nm, vd in vds.items():
        if not getattr(vd, "letter", None):
            continue
        look3 = vmul(vd.view.n, -1.0)
        host = next((h for h in ("above", "below", "principal") if h in vds and abs(vdot(look3, vds[h].view.n)) < 1e-6
                     and h != nm), None)
        if host:
            hv = vds[host]
            l2 = hv.view.to2d(look3)
            hb = hv.box()
            cx = hb[0] + 0.40 * (hb[2] - hb[0])
            cx = hb[0] + 0.22 * (hb[2] - hb[0])
            if abs(l2[1]) > 0.5:        # arrow across the strip, on the viewer's side, clear of its dimensions
                y0 = hb[3] + 9 + getattr(hv, "top_used", 0.0) if l2[1] < 0 else hb[1] - 9
                tip = (cx, y0 + l2[1] * 6)
                sh.line((cx, y0), tip, 0.35)
                sh.arrow(tip, (0, l2[1]), 3.0, 1.1)
                sh.text(cx + 3.0, y0 - (1.0 if l2[1] > 0 else -0.5), vd.letter, 3.5, "left", bold=True)
            else:
                x0 = hb[2] + 9 if l2[0] < 0 else hb[0] - 9
                cy = (hb[1] + hb[3]) / 2
                tip = (x0 + l2[0] * 6, cy)
                sh.line((x0, cy), tip, 0.35)
                sh.arrow(tip, (l2[0], 0), 3.0, 1.1)
                sh.text(x0, cy + 3.0, vd.letter, 3.5, "center", bold=True)
    # ---- removed sections: the hole axis and the hole sizes
    for vd in removed:
        r = vd.r
        c = vd.S(vd.view.to2d(r.point))
        x0, y0, x1, y1 = vd.box()
        sh.centre_line((c[0], y0 - 4), (c[0], y1 + 4))
        # each wall's hole sized across its gap, on the outside of that wall (ISO 129-1), with its tag
        bottom_used = False
        for ft in r.feats:
            ent = vd.view.to2d(ft.f.entry)
            ax2 = vd.view.to2d(r.point)
            wall_out = vd.S(ent)[1]
            top_wall = wall_out > c[1]
            if not top_wall:
                bottom_used = True
            pa = (c[0] - ft.f.dia / 2 * vd.scale, wall_out)
            pb = (c[0] + ft.f.dia / 2 * vd.scale, wall_out)
            sh.dim_linear(pa, pb, "up" if top_wall else "down", 5.0,
                          "%s  Ø%s THRU 1 WALL" % (ft.tag, fmt(ft.f.dia)), 2.5)
        # profile size
        w, h = (x1 - x0) / vd.scale, (y1 - y0) / vd.scale
        sh.dim_linear((x0, y0), (x1, y0), "down", 14.0 if bottom_used else 6.0, fmt(w), 2.5)
        sh.dim_linear((x0, y0), (x0, y1), "left", 6.0, fmt(h), 2.5)
    # ---- datums
    if dat.get("B"):
        Bf = dat["B"]
        cn, cp = dat["C_plane"]
        for nm, vd in vds.items():
            if nm == Bf.group.view and _end_on(Bf, vd.view):
                cb = vd.S(vd.view.to2d(Bf.f.entry))
                rb = Bf.f.dia / 2 * vd.scale
                sh.datum((cb[0] - rb * 0.7, cb[1] - rb * 0.7), (-0.6, -1), "B")
                # C on the room-side face, where this view shows it edge on
                n2 = vd.view.to2d(cn)
                if abs(n2[1]) > 0.5:
                    yy = vd.view.to2d(tuple(cp if abs(cn[i]) > 0.5 else 0.0 for i in range(3)))[1]
                    e = vd.extent
                    # where it is farthest from every tagged hole along the edge (clear of the tags)
                    xs = [vd.view.to2d(ft.f.entry)[0] for g in pl.groups if g.view == nm for ft in g.feats]
                    cands = [e[0] + t * (e[2] - e[0]) for t in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)]
                    xc = max(cands, key=lambda x: min([abs(x - h) for h in xs] or [1e9]))
                    sh.datum(vd.S((xc, yy)), (0, n2[1]), "C")
        # A: the seat face, on the principal view's edge
        a_off = vdot(O, dat["A_normal"])
        x0, y0, x1, y1 = pvd.box()
        n2 = P.to2d(dat["A_normal"])
        if abs(n2[1]) > 0.5:
            yA = pvd.S((0, P.to2d(O)[1]))[1]
            sh.datum((x0 + 0.18 * (x1 - x0), yA), (0, n2[1]), "A")
    if not dat.get("B") and spec.get("datum_faces"):
        for letter, face in sorted(spec["datum_faces"].items()):
            k = "XYZ".index(face[1])
            nrm = tuple((1.0 if face[0] == "+" else -1.0) if i == k else 0.0 for i in range(3))
            plane = part.box[3 + k] if face[0] == "+" else part.box[k]
            for nm in ("principal", "above", "below", "from_left", "from_right"):
                if nm not in vds or abs(vdot(nrm, vds[nm].view.n)) > 1e-6:
                    continue
                vd = vds[nm]
                n2 = vd.view.to2d(nrm)
                e = vd.extent
                if abs(n2[1]) > 0.5:
                    yy = plane * n2[1] if False else vd.view.to2d(tuple(plane if i == k else 0.0 for i in range(3)))[1]
                    at = vd.S((e[0] + 0.30 * (e[2] - e[0]) + 8 * (ord(letter) - 65), yy))
                    sh.datum(at, (0, n2[1]), letter)
                else:
                    xx = vd.view.to2d(tuple(plane if i == k else 0.0 for i in range(3)))[0]
                    at = vd.S((xx, e[1] + 0.25 * (e[3] - e[1])))
                    sh.datum(at, (n2[0], 0), letter)
                break
    # ---- overall dimensions on the principal (true sizes of the part's box in that view)
    e = pvd.extent
    a, b = pvd.S((e[0], e[1])), pvd.S((e[2], e[3]))
    sh.dim_linear((a[0], a[1]), (b[0], a[1]), "down", 15.0, fmt(e[2] - e[0]), 3.0)
    sh.dim_linear((a[0], a[1]), (a[0], b[1]), "left", 15.0, fmt(e[3] - e[1]), 3.0)
    # an end cut at an angle (a mitre): in the plain view where its face shows edge on, the angle from square and
    # the true lengths along the member's two faces (guideline 6.1: true lengths and angle, not a box)
    for b in part.bodies:
        lk = max(range(3), key=lambda i: b.size[i])
        lax = tuple(1.0 if i == lk else 0.0 for i in range(3))
        for n, off, area, face in geom.planes(b):
            c = abs(vdot(n, lax))
            if not (0.02 < c < 0.9998):
                continue
            ang = math.degrees(math.acos(c))
            for nm, vd in vds.items():
                if abs(vdot(n, vd.view.n)) > 1e-6 or abs(vdot(lax, vd.view.n)) > 1e-6:
                    continue
                # the face's two ends along the line it shows as
                pts = [vd.view.to2d(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v)))) for v in _vertices(face)]
                if len(pts) < 2:
                    continue
                n2 = vd.view.to2d(n)
                t2 = (-n2[1], n2[0])
                pts.sort(key=lambda q: q[0] * t2[0] + q[1] * t2[1])
                pa, pb = pts[0], pts[-1]
                a2 = vd.view.to2d(lax)
                ax_k = 0 if abs(a2[0]) > 0.5 else 1
                # the long point is the one farther along the member, from the body's middle
                mid = vd.view.to2d(b.centroid)
                far = max((pa, pb), key=lambda q: abs(q[ax_k] - mid[ax_k]))
                near = pb if far is pa else pa
                S = vd.S
                # reference line square to the member through the long point, and the angle arc between
                sq = (0.0, 1.0) if ax_k == 0 else (1.0, 0.0)
                L = math.dist(S(far), S(near)) + 6
                towards = 1 if (near[1 - ax_k] - far[1 - ax_k]) > 0 else -1
                ref_end = (S(far)[0] + sq[0] * towards * L, S(far)[1] + sq[1] * towards * L)
                sh.line(S(far), ref_end, W_THIN)
                d_m = (S(near)[0] - S(far)[0], S(near)[1] - S(far)[1])
                lm = math.hypot(*d_m)
                ext_end = (S(far)[0] + d_m[0] / lm * L, S(far)[1] + d_m[1] / lm * L)
                sh.line(S(near), ext_end, W_THIN)
                a0 = math.atan2(ref_end[1] - S(far)[1], ref_end[0] - S(far)[0])
                a1 = math.atan2(d_m[1], d_m[0])
                lo, hi = (a0, a1) if ((a1 - a0) % (2 * math.pi)) < math.pi else (a1, a0)
                if hi < lo:
                    hi += 2 * math.pi
                R = L - 2
                sh.arc(S(far), R, lo, hi, W_THIN)
                am = (lo + hi) / 2
                sh.text(S(far)[0] + (R + 1.5) * math.cos(am), S(far)[1] + (R + 1.5) * math.sin(am),
                        "%s°" % fmt(ang), 2.5, "left" if math.cos(am) >= 0 else "right", valign="mid")
                # true lengths along the two long faces, from the other (square) end
                ve = vd.extent
                other = ve[0] if abs(far[ax_k] - ve[0]) > abs(far[ax_k] - ve[2]) else ve[2]
                if ax_k == 0:
                    # each face's true length goes over the view where that face is the top edge, measured from
                    # the square end to its own corner of the mitre
                    p3 = {}
                    for v_ in _vertices(face):
                        P3 = geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v_)))
                        key = (round(vd.view.to2d(P3)[0], 3), round(vd.view.to2d(P3)[1], 3))
                        p3[key] = P3
                    corners = [p3.get((round(q[0], 3), round(q[1], 3))) for q in (far, near)]
                    for P3 in corners:
                        if P3 is None:
                            continue
                        for nm2, vd2 in vds.items():
                            if abs(vdot(n, vd2.view.n)) > 1e-6 or abs(vdot(lax, vd2.view.n)) > 1e-6:
                                continue
                            q2 = vd2.view.to2d(P3)
                            e2 = vd2.extent
                            if abs(q2[1] - e2[3]) > 1e-3:
                                continue
                            oth = e2[0] if abs(q2[0] - e2[0]) > abs(q2[0] - e2[2]) else e2[2]
                            sh.dim_linear(vd2.S((oth, e2[3])), vd2.S((q2[0], e2[3])), "up", 11.0,
                                          fmt(abs(q2[0] - oth)), 2.5)
                            vd2.top_used = 16.0
                            break
                vd.has_mitre = True
                break
    # frame members: the stiles' centre lines from the frame's front end (ordinate, ISO 129-1), over the view
    stiles = [b for b in part.bodies if "STILE" in (b.name or "").upper()]
    if stiles:
        e0 = pvd.extent
        top = pvd.box()[3]
        level = top + 13.0
        ox = P.to2d(O)[0]
        end = e0[0] if abs(ox - e0[0]) <= abs(ox - e0[2]) else e0[2]
        x_front = pvd.S((end, 0))[0]
        marks = []
        for b in stiles:
            be = project.extent(project.project(b.shape, P))
            cx = (be[0] + be[2]) / 2
            marks.append((pvd.S((cx, 0))[0], abs(cx - end)))
            # the stile's centre line through the view
            sh.centre_line(pvd.S((cx, be[1] + 4)), pvd.S((cx, be[3] - 4)))
        sh.line((x_front, top + 1.0), (x_front, level + 1.5), W_THIN)
        sh.text(x_front - 0.8, level + 2.0, "0", 2.5, "left", rotate=90)
        for x, v in sorted(marks):
            sh.line((x, top + 1.0), (x, level + 1.5), W_THIN)
            sh.text(x - 0.8, level + 2.0, fmt(v), 2.5, "left", rotate=90)
        lab = "STILE CENTRE LINES FROM THE FRONT END"
        ymax = level + 2.0 + max(sh.text_width(fmt(v), 2.5) for _x, v in marks) + 3.0
        if end == e0[0]:
            sh.text(x_front, ymax, lab, 2.5, "left")
        else:
            sh.text(x_front, ymax, lab, 2.5, "right")
    # the spigot hole and slot from the frame's end faces (joints register R-J13: 100 from each end)
    if dat.get("B") and "below" in vds:
        vd = vds["below"]
        ve = vd.extent
        for f in (dat["B"], dat["slot"]):
            c = vd.view.to2d(f.f.entry)
            end_x = ve[0] if abs(c[0] - ve[0]) < abs(c[0] - ve[2]) else ve[2]
            p1 = vd.S((end_x, ve[3]))
            p2 = vd.S((c[0], ve[3]))
            sh.dim_linear(p1, p2, "up", 7.0, fmt(abs(c[0] - end_x)), 2.5)
    sh.flush()
    return


def member_key(name):
    s = (name or "").upper()
    s = s.replace("(CUT LENGTH)", "").strip()
    import re as _re
    return _re.sub(r"\s+\d+$", "", s).strip()


def cut_list(part):
    """Frame members from the parts list's level-2 cut rows, matched to the bodies by name."""
    rows = []
    for r in part.cut_rows:
        if (r.get("kind") or "").strip().lower() != "cut":
            continue
        key = member_key(r.get("name"))
        bodies = [b for b in part.bodies if member_key(b.name) == key]
        rows.append({"item": len(rows) + 1, "member": key, "profile": (r.get("size_mm") or "").strip(),
                     "material": (r.get("material") or "").strip(), "length": (r.get("cut_length_mm") or "").strip(),
                     "qty": (r.get("qty") or "").strip(), "tol": (r.get("tolerance") or "").strip(),
                     "note": (r.get("note") or "").strip(), "bodies": bodies})
    return rows


TABLE_W = 262.0


def tables_and_text(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today):
    """Sheet 1: member balloons on the principal view and one hole table per face in the right column."""
    W, H = sh.W, sh.H
    P = pl.principal
    O = dat["O"]
    pvd = vds["principal"]
    tw = spec.get("table_w", TABLE_W)
    right_x0 = W - 10 - tw - 4
    y = H - 10 - 6
    # ---- member balloons (frames): item numbers of the cut list on sheet 2
    members = cut_list(part)
    for m in members:
        for b in m["bodies"]:
            e = project.extent(project.project(b.shape, P))
            horiz = (e[2] - e[0]) > (e[3] - e[1])
            if horiz:
                anchor = pvd.S((e[0] + 0.62 * (e[2] - e[0]), (e[1] + e[3]) / 2))
                upper = anchor[1] > (pvd.box()[1] + pvd.box()[3]) / 2
                off = (anchor[0] + 7, anchor[1] - 14 if upper else anchor[1] + 14)
            else:
                anchor = pvd.S(((e[0] + e[2]) / 2, e[1] + 0.55 * (e[3] - e[1])))
                off = (anchor[0] + 10, anchor[1] + 7)
            sh.circle(anchor, 0.6, 0.18, fill=(0, 0, 0))
            sh.line(anchor, off, 0.18)
            sh.circle((off[0] + 4.0, off[1]), 4.0, 0.25)
            sh.text(off[0] + 4.0, off[1], str(m["item"]), 3.5, "center", valign="mid", bold=True)
    sh.flush()
    # ---- hole tables, one per face
    cols = [("TAG", 14, "c"), ("X (mm)", 24, "r"), ("Y (mm)", 24, "r"), ("SIZE", 40, "l"), ("DEPTH", 42, "l"),
            ("FEATURE (register) AND FITS", tw - 144, "l")]
    for g in groups:
        vd = vds.get(g.view) if g.view else g.vd
        oname = vd.origin_name
        v = vd.view
        o2 = v.to2d(O)
        rows = []
        for ft in g.feats:
            c = v.to2d(ft.f.entry)
            x, yv = c[0] - o2[0], c[1] - o2[1]
            size_t = size_text(ft)
            if ft.kind == "slot":
                a2 = v.to2d(ft.f.along)
                size_t += " along %s" % ("X" if abs(a2[0]) > 0.5 else "Y")
            if ft.kind == "keyhole":
                a2 = v.to2d(ft.f.along)
                size_t += " toward %s%s" % ("+" if (a2[0] + a2[1]) > 0 else "-", "X" if abs(a2[0]) > 0.5 else "Y")
            rows.append([ft.tag, "%.2f" % x, "%.2f" % yv, size_t, wall_word(ft.f, ft.body), feature_text(ft)])
        if g.coax_of is not None:
            rm = [r_ for r_ in removed if any(f in st for st in r_.r.all for f in g.feats)]
            twins = sorted(ft.twin.tag for ft in g.feats)
            where = "far wall, coaxial with %s: hidden in the %s, shown in section %s" % (
                twins[0] + ("-" + twins[-1] if len(twins) > 1 else ""), VIEW_WORDS[g.view].lower(),
                ", ".join("%s-%s" % (r_.letter, r_.letter) for r_ in rm) or "-")
        elif g.view:
            where = "seen in the %s" % (("view %s" % vd.letter) if getattr(vd, "letter", None)
                                        else VIEW_WORDS[g.view].lower())
        else:
            where = "seen in section %s-%s" % (vd.letter, vd.letter)
        head = ["HOLES %s-%s: %s" % (g.feats[0].tag, g.feats[-1].tag, face_title(part, g)),
                "%s; origin %s; +X right, +Y up; drilled from this face" % (where, oname)]
        y = sh.table(right_x0, y, cols, rows, size=2.5, title=head, title_size=2.5) - 5.0
    return y, members


def cut_list_table(sh, part, members, x, y, width):
    ccols = [("ITEM", 14, "c"), ("MEMBER", 52, "l"), ("PROFILE (mm)", 40, "l"), ("CUT LENGTH (mm)", 34, "r"),
             ("QTY", 14, "c"), ("ENDS, TOLERANCE", width - 154, "l")]
    crow = []
    for m in members:
        crow.append([str(m["item"]), m["member"], m["profile"], m["length"], m["qty"],
                     ("%s; %s" % ("square-cut ends" if "square" in (m["note"] + m["tol"]).lower() else m["note"],
                                  m["tol"].split(",")[0])).strip("; ")])
    mat = part.row.get("material", "")
    return sh.table(x, y, ccols, crow, size=2.5,
                    title=["CUT LIST (parts list %s)" % os.path.basename(part.list_file or ""),
                           "aluminium 6063-T6 tube: %s" % mat.split(":", 1)[-1].strip()], title_size=2.5)


def notes_list(part, spec, pl, vds, secs, removed, dat, groups):
    P = pl.principal
    notes = []
    notes.append("UNITS: mm. Do not scale the drawing. ISO first-angle projection (ISO 5456-2), symbol in the "
                 "title block. Dimensions to ISO 129-1. Sheet 1: views, sections and hole tables; sheet 2: these "
                 "general notes%s." % (", the cut list" if cut_list(part) else "") + "")
    vw = "the room side" if part.pod_system and pl.principal.pod_name in ("right", "front", "top") else "its side"
    notes.append("Views: the principal view looks %s (%s); every view's title gives its own X and Y and how they "
                 "map to the %s axes (conventions section 4). On every view X runs right and Y up." % (
                     project.LOOK_WORDS.get(P.looking, P.looking), mapping_words(P, part.pod_system),
                     "pod" if part.pod_system else "part"))
    if dat.get("B"):
        notes.append("Datums (ISO 5459): A = %s; B = axis of the spigot hole %s (joints register R-J6, R-J13); C = %s "
                     "(the spigot slot %s runs across the rail, R-J17, so it locates along the rail only). Origin O = "
                     "datum B's axis on datum A; O1, O2... are O seen in each view. Hole positions in the tables are "
                     "theoretically exact from O." % (
                         dat["words"]["A"], dat["B"].tag, dat["words"]["C"], dat["slot"].tag))
    elif not part.features:
        pass        # nothing is located from a datum: the overall sizes define the part
    else:
        w = dat.get("words", {})
        if w.get("A"):
            notes.append("Datums (ISO 5459): A = %s; B = %s; C = %s. Origin O = the corner where A, B and C meet; "
                         "O1, O2... are O seen in each view. Hole positions in the tables are theoretically exact "
                         "from O." % (w["A"], w.get("B", "-"), w.get("C", "-")))
        else:
            notes.append("Origin O = %s; O1, O2... are O seen in each view. Hole positions in the tables are from "
                         "O." % w.get("O", "the part's corner shown"))
    if part.placement:
        notes.append("Drawn where it sits in the pod: its STEP is in its own system CS-%s, placed in the pod by %s; "
                     "%s (checked hole for hole against that assembly)." % (
                         part.pn, part.placement["assembly"], part.placement["words"]))
    for t in spec.get("notes", []):
        notes.append(t)
    two = [vd.letter for vd in removed if vd.r.feats]
    if part.features:
        notes.append("Holes go THRU 1 WALL of the member unless the table says otherwise; deburr both sides. %s" % (
            "Coaxial holes in two walls of one member are shown in section%s %s." % (
                "s" if len(two) > 1 else "", " and ".join("%s-%s" % (l, l) for l in two)) if two else ""))
    if spec.get("tolerance"):
        notes.append("TOLERANCES (PROPOSED until the shop confirms; not ISO 2768): " + spec["tolerance"])
    src = "Source: %s (sha256 %s; declared unit %s, read in mm and checked against tools/checks/stepfile.py, " \
          "worst box difference %s mm)" % (inputs.rel(part.step), inputs.sha12(part.step), part.unit["declared"],
                                          fmt(part.unit["box_check_mm"], 3))
    src += "; parts list %s" % inputs.rel(part.list_file) if part.list_file else ""
    regs = sorted({ft.reg["file"] for ft in part.features if ft.reg})
    if regs:
        src += "; feature rationale %s" % ", ".join(regs)
    src += ". Made by tools/drawgen (D-112) from that STEP: regenerate it, never edit the PDF."
    notes.append(src)
    return notes


TB_W = 180.0      # ISO 7200: the title block is at most 180 mm wide


def title_block(sh, part, spec, scale, removed, today, sheet_no=1, sheets=1):
    """ISO 7200 title block at the sheet's lower right: rows sized to their wrapped text, letter height 2.5 mm
    or more for every value (the field names 2.0). Returns its top y."""
    W = sh.W
    w = TB_W
    x0 = W - 10 - w
    row = part.row
    LAB, VAL = 2.0, 2.5
    mass = (row.get("mass_each_kg") or row.get("unit_mass_kg") or "").strip()
    sc = scale_text(spec["_scale"]) + ("" if not removed else " (sections %s %s)" % (
        " ".join("%s-%s" % (vd.letter, vd.letter) for vd in removed), scale_text(removed[0].scale)))
    # rows of cells: (width share, label, value, value size, bold)
    rows = [
        [(70, "PROJECT", "Spaceship (FocusPod v2)", VAL, True), (36, "STATUS", "DRAFT", 3.0, True),
         (40, "DATE", today, VAL, False), (34, "SHEET", "%d/%d" % (sheet_no, sheets), 3.0, True)],
        [(180, "TITLE", part.name, 3.5, True)] + ([] if not part.name_vi else []),
        [(40, "PART NUMBER", part.pn, 7.0, True), (22, "REV", part.rev, 5.0, True),
         (118, "DRAWING NUMBER (FILE)", part.dwg_name, VAL, True)],
        [(180, "MATERIAL", "MATERIAL: " + (row.get("material") or "").strip(), VAL, False)],
        [(180, "FINISH", "FINISH: " + ((row.get("finish") or "").strip() or "none (as supplied)"), VAL, False)],
        [(62, "SCALE", sc, VAL, False), (18, "SIZE", sh.size, VAL, False), (32, "UNITS", "UNITS: mm", VAL, True),
         (68, "MASS", ("%s kg (calculation)" % mass) if mass else "see parts list", VAL, False)],
        [(62, "MADE BY", "tools/drawgen (D-112)", VAL, False), (40, "APPROVED", "not released", VAL, False),
         (78, "TOLERANCES", "TOLERANCE: see the notes; not ISO 2768", VAL, False)],
    ]
    proj_h = 12.0
    heights = []
    wrapped = []
    for r in rows:
        cells = []
        hmax = 0.0
        for cw, lab, val, vs, bold in r:
            ls = sh.wrap(val, vs, cw - 2.4, bold) if val else []
            if lab == "TITLE" and part.name_vi:
                ls = [(l_, 3.5, True) for l_ in ls] + [(l_, VAL, False) for l_ in sh.wrap(part.name_vi, VAL, cw - 2.4)]
            else:
                ls = [(l_, vs, bold) for l_ in ls]
            hh = 1.2 + LAB + 1.6 + sum(z[1] * 1.45 for z in ls) + 1.0
            hmax = max(hmax, hh)
            cells.append((cw, lab, ls))
        heights.append(hmax)
        wrapped.append(cells)
    total = sum(heights) + proj_h
    y_top = 10.0 + total
    sh.rect(x0, 10.0, w, total, 0.7)
    y = y_top
    for cells, hh in zip(wrapped, heights):
        sh.line((x0, y - hh), (x0 + w, y - hh), W_THIN)
        cx = x0
        for cw, lab, ls in cells:
            if cx > x0 + 0.1:
                sh.line((cx, y), (cx, y - hh), W_THIN)
            sh.text(cx + 1.2, y - 1.2 - LAB, lab, LAB)
            yy = y - 1.2 - LAB - 1.6
            for txt, vs, bold in ls:
                yy -= vs
                sh.text(cx + 1.2, yy, txt, vs, bold=bold)
                yy -= vs * 0.45
            cx += cw
        y -= hh
    # projection row: the first-angle symbol and its name
    sh.text(x0 + 1.2, y - 1.2 - LAB, "PROJECTION", LAB)
    sh.first_angle_symbol(x0 + 40, y - proj_h + 2.5, 6.5)
    sh.text(x0 + 70, y - proj_h / 2 - 1.2, "ISO first angle (ISO 5456-2)", VAL)
    sh.flush()
    return y_top


def make(pn, team, spec, out_path, today=None, step=None, row=None):
    """Generate one drawing; returns a report. step and row: a part outside the repo's lists (tests)."""
    part = Part(pn, team, step=step, pod_system=spec.get("pod_system", True), row=row)
    with open(part.step, encoding="latin-1") as fh:
        head = fh.read(4000)
    import re as _re
    m = _re.search(r"(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}", head)
    today = today or (m.group(1) if m else datetime.date.today().isoformat())
    sh, pl, vds, secs, removed, dat, scale, report, groups = draw(part, spec, None, today)
    spec = dict(spec)
    spec["_scale"] = scale
    annotate(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today)
    ty, _members = tables_and_text(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today)
    tb_top = title_block(sh, part, spec, scale, removed, today, 1, 2)
    if ty < tb_top + 4:
        report["warning"] = "the tables run into the title block"
    sh.border()
    sh.flush()
    # ---- sheet 2: GENERAL NOTES, the cut list and a small isometric (guideline 6.1: general rules on their own
    # sheet, specific notes near their feature on sheet 1)
    sh.new_page()
    nx, ny = 30.0, sh.H - 22.0
    nw = min(sh.W - 10 - TB_W - 30.0 - 24.0, 360.0)        # lines a reader can follow
    sh.text(nx, ny, "GENERAL NOTES", 3.5, bold=True)
    ny -= 8.0
    for i, t in enumerate(notes_list(part, spec, pl, vds, secs, removed, dat, groups), 1):
        sh.text(nx, ny, "%d." % i, 2.5)
        ny = sh.paragraph(nx + 7, ny, t, 2.5, nw - 8, lead=1.6) - 2.0
    members = cut_list(part)
    if members:
        ny = cut_list_table(sh, part, members, nx, ny - 6.0, min(nw, 330.0)) - 6.0
    if spec.get("iso", True):
        P = pl.principal
        n_iso = vnorm(vadd(vadd(P.n, vmul(P.x, -1.0)), P.y))
        x_iso = vnorm(vcross(P.y, n_iso))
        iv = View("iso", n_iso, x_iso)
        prims = [p_ for p_ in project.project(part.shape, iv) if p_.vis]
        e = project.extent(prims)
        box_x0, box_w = nx, nw
        box_h = ny - 30.0 - 20.0
        right_free = sh.W - 10 - (nx + nw) - 20
        if right_free > 200:    # to the right of the notes, over the title block
            box_x0, box_w, box_h = nx + nw + 20, right_free, sh.H - 20 - tb_top - 40
        elif box_h < 80:        # beside the title block instead
            box_x0, box_w, box_h = sh.W - 10 - TB_W - 10, TB_W, sh.H - 20 - tb_top - 40
        si = None
        for cand in ISO_SCALES:
            if (e[2] - e[0]) * cand <= box_w * 0.85 and (e[3] - e[1]) * cand <= box_h * 0.85:
                si = cand
                break
        if si:
            ivd = VD(iv, prims, si, "iso")
            cx = box_x0 + box_w / 2
            cy = (ny - 10.0 + 30.0) / 2 if box_x0 == nx else tb_top + 20 + box_h / 2
            ivd.off = (cx - si * (e[0] + e[2]) / 2, cy - si * (e[1] + e[3]) / 2)
            for p_ in prims:
                if p_.kind == "line":
                    sh.line(ivd.S(p_.p), ivd.S(p_.q), 0.35)
                elif p_.kind == "arc":
                    sh.arc(ivd.S(p_.c), p_.r * si, p_.a0, p_.a1, 0.35)
                else:
                    sh.bezier([ivd.S(q) for q in p_.pts], 0.35)
            sh.flush()
            bx = ivd.box()
            sh.text((bx[0] + bx[2]) / 2, bx[1] - 9.0, "ISOMETRIC VIEW  %s" % scale_text(si), 3.5, "center", bold=True)
            sh.text((bx[0] + bx[2]) / 2, bx[1] - 14.0, "for identification only", 2.5, "center")
    title_block(sh, part, spec, scale, removed, today, 2, 2)
    sh.border()
    report["dwg"] = part.dwg_name
    report["tags"] = {ft.tag: {"x3": ft.f.entry, "dia": ft.f.dia, "kind": ft.kind} for ft in part.features}
    report["origin"] = dat["O"]
    report["views"] = {vd.origin_name: {"n": vd.view.n, "x": vd.view.x, "y": vd.view.y, "scale": vd.scale,
                                        "off": vd.off} for vd in list(vds.values()) + secs}
    report["removed"] = [{"letter": vd.letter, "scale": vd.scale, "off": vd.off, "n": vd.view.n, "x": vd.view.x,
                          "y": vd.view.y} for vd in removed]
    sh.meta["creationDate"] = "D:%s000000Z" % today.replace("-", "")
    sh.meta["modDate"] = sh.meta["creationDate"]
    data = drawing_data(part, spec, pl, vds, secs, removed, dat, groups, sh)
    report["data"] = data
    sh.data = data
    sh.save(out_path)
    return report


def drawing_data(part, spec, pl, vds, secs, removed, dat, groups, sh):
    """What the drawing was made from and where everything sits on it, stored in the PDF (catalog key
    /DrawgenData) so a reader can check it: the sources with their hashes, each view's mapping and place on the
    sheet, the origin, the datums and every tagged feature (guideline 4.5: the drawing names its sources)."""
    srcs = [{"role": "STEP", "path": inputs.rel(part.step), "sha256_12": inputs.sha12(part.step),
             "unit": part.unit}]
    if part.list_file:
        srcs.append({"role": "parts list", "path": inputs.rel(part.list_file), "sha256_12": inputs.sha12(part.list_file)})
    for f in sorted({ft.reg["file"] for ft in part.features if ft.reg}):
        srcs.append({"role": "feature rationale", "path": f, "sha256_12": inputs.sha12(os.path.join(geom.REPO, f))})
    views = []
    for vd in [vds[n_] for n_ in ("principal", "below", "above", "from_left", "from_right", "rear") if n_ in vds] + secs:
        views.append({"origin": vd.origin_name, "name": vd.name, "n": vd.view.n, "x": vd.view.x, "y": vd.view.y,
                      "scale": vd.scale, "off": vd.off})
    for vd in removed:
        views.append({"origin": None, "name": "section %s-%s" % (vd.letter, vd.letter), "n": vd.view.n,
                      "x": vd.view.x, "y": vd.view.y, "scale": vd.scale, "off": vd.off})
    feats = []
    for g in groups:
        vd = vds.get(g.view) if g.view else g.vd
        for ft in g.feats:
            feats.append({"tag": ft.tag, "kind": ft.kind, "dia": ft.f.dia, "entry": ft.f.entry, "axis": ft.f.axis,
                          "depth": ft.f.depth, "body": ft.body.name, "table_origin": vd.origin_name,
                          "drawn_in": vd.origin_name if _end_on(ft, vd.view) else None,
                          "register": ft.reg["id"] if ft.reg else None})
    return {"generator": TOOL_REV, "pn": part.pn, "rev": part.rev, "dwg": part.dwg_name, "sheet": sh.size,
            "placement": ({"assembly": part.placement["assembly"], "m": part.placement["m"],
                           "t": part.placement["shift"]} if part.placement else None),
            "sheet_h": sh.H, "sources": srcs, "origin": dat["O"],
            "datums": {"B": dat["B"].tag if dat.get("B") else None,
                       "C": ("plane %s at %s" % (axis_name(dat["C_plane"][0]), fmt(dat["C_plane"][1])))
                       if dat.get("C_plane") else None},
            "views": views, "features": feats}
