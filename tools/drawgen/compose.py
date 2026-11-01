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
from sheet import AUTHOR, Sheet, W_HID, W_THIN, W_VIS, DASH_HID

GENERATOR = "drawgen"
TOOL_REV = "drawgen 1.0"

ISO_SCALES = [10.0, 5.0, 2.0, 1.0, 1 / 2.0, 1 / 5.0, 1 / 10.0, 1 / 20.0]


def scale_text(s):
    return "%g:1" % s if s >= 1 else "1:%g" % round(1 / s, 3)


def fmt(v, nd=2):
    s = ("%.*f" % (nd, v)).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class _Smaller(Exception):
    """The sheet's row of removed sections and flat pattern ran off the sheet at this scale: draw again smaller (the
    flat pattern first, when it is what runs off and can go smaller)."""

    def __init__(self, scale, flat=None):
        Exception.__init__(self, scale)
        self.scale = scale
        self.flat = flat


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
        # ISO 15786: the depth of the full diameter; a drill point in the model is named with its angle
        return "%s deep%s" % (fmt(f.depth), (", drill point %s°" % fmt(f.point_angle))
                              if getattr(f, "point_angle", None) else "")
    # hollow: past the run's far end the line along the hole meets the member's material again (its far wall), or
    # the run has a partner on its axis in the far wall (a two-wall pair); through a solid the line leaves the part
    # (an angled exit face included)
    far = vadd(f.entry, vmul(f.axis, f.depth + 0.05))
    inter = IntCurvesFace_ShapeIntersector()
    inter.Load(body.shape, 1e-6)
    inter.Perform(gp_Lin(gp_Pnt(*far), gp_Dir(*f.axis)), 0.0, 1e7)
    inside = bool(getattr(f, "partners", None)) or (inter.IsDone() and inter.NbPnt() > 0)
    return "THRU 1 WALL (%s)" % fmt(f.depth) if inside else "THRU (%s)" % fmt(f.depth)


def size_text(feat):
    f = feat.f
    if feat.kind == "hole":
        return "Ø%s" % fmt(f.dia)
    if feat.kind == "keyhole":
        return "KEYHOLE Ø%s + SLOT %s, %s TO END" % (fmt(f.entry_dia), fmt(f.width), fmt(f.neck))
    if feat.kind == "open_slot":
        return "OPEN SLOT %s, R%s END %s FROM THE EDGE%s" % (
            fmt(f.width), fmt(f.r), fmt(f.edge),
            (", MOUTH %s TAPERING OVER %s" % (fmt(f.mouth), fmt(f.taper))) if f.taper > 1e-3 else "")
    return "SLOT %s x %s OVERALL, R%s ENDS" % (fmt(f.width), fmt(f.length), fmt(f.width / 2))


FACE_WORDS = {"-Z": "bottom face", "+Z": "top face", "-Y": "front face", "+Y": "back face", "-X": "left face",
              "+X": "right face"}
VIEW_WORDS = {"principal": "PRINCIPAL VIEW", "above": "VIEW FROM ABOVE", "below": "VIEW FROM BELOW",
              "from_left": "VIEW FROM THE LEFT", "from_right": "VIEW FROM THE RIGHT", "rear": "REAR VIEW"}
POSITION = {"above": (0, -1), "below": (0, 1), "from_left": (1, 0), "from_right": (-1, 0), "rear": (2, 0)}


class Part:
    """Everything one drawing needs, read from the sources."""

    def __init__(self, pn, team, step=None, pod_system=True, row=None, bent=None):
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
            self.step = find_step(pn, team)
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
        self.occurrences = self.unit.get("occurrences", 1)
        self.qty_words = None
        if self.occurrences > 1:
            q = (self.row.get("qty") or self.row.get("qty_per_parent") or "").strip()
            try:
                qn = int(float(q))
            except ValueError:
                qn = None
            if qn is not None and qn != self.occurrences:
                raise NotDrawable("%s: %s holds it %d times, its parts list says %s" % (
                    pn, os.path.basename(self.step), self.occurrences, q))
            par = inputs.parse_name(self.list_file) if self.list_file else None
            self.qty_words = "%s per %s (its parts list); the assembly STEP %s holds %d alike, one is drawn" % (
                q or self.occurrences, ("%s %s" % (par["pn"], par["name"])) if par else "assembly",
                os.path.basename(self.step), self.occurrences)
        self.placement = None
        if pod_system:
            self._to_pod()
        self.shape = geom.compound([b.shape for b in self.bodies])
        self.pod_system = pod_system
        self.features = []
        for b in self.bodies:
            hs, ss = geom.features(b)
            bad = [] if bent else geom.unexplained_curved_faces(b, hs, ss)
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
        self.flat = None
        if bent:
            # bent or folded sheet drawn from its STEP and its team's DXF (the Lead's ruling, 2026-11-01): the folds
            # read from the model, the flat pattern from the DXF, matched bend for bend (sheetmetal)
            self.flat = bent_flat(self, team, bent)
        else:
            why = folded_or_bent(self)
            if why:
                raise NotDrawable("%s is %s: bent and folded parts stay with Fusion (D-113); an entry marked bent draws "
                                  "them from the STEP and the DXF" % (pn, why))
        # flat faces: a straight member's notches, chamfers and welded end plates; any other flat feature (a step, a
        # pocket, an uneven chamfer) would be drawn without a size, so the part is refused
        self.notches, self.chamfers, self.plates = [], [], []
        for b in ([] if self.flat else self.bodies):
            lax = geom.member_axis(b)
            if lax is not None and not plain_section(b, lax):
                raise NotDrawable("%s body %s is a profile whose section isn't a plain rectangle or rectangular tube: its "
                                  "section's sizes aren't drawn yet (D-139: Fusion, or the profile reading)" % (pn, b.name))
            nt, ch, plt, odd = geom.flat_features(b, [ft.f for ft in self.features if ft.body is b and ft.kind != "hole"])
            if odd:
                raise NotDrawable("%s body %s has flat faces this tool can't size yet: %s%s" % (
                    pn, b.name, "; ".join(odd[:3]), " (and %d more)" % (len(odd) - 3) if len(odd) > 3 else ""))
            self.notches += nt
            self.chamfers += ch
            self.plates += plt
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
                if ft.kind == "open_slot":
                    r = inputs.match_open_slot_b(inputs.feature_rows_b(team, pn, sizeless=True), ft.f.width,
                                                 ft.f.mouth)
                else:
                    r = inputs.match_feature_b(rows_b, dia, wall, ft.f.entry, keyhole=(ft.kind == "keyhole"),
                                               along=along)
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


EXTRUDED_WORDS = re.compile(r"\bextru(?:ded|sion|sions)\b", re.I)
BENT_WORDS = re.compile(r"\b(?:bend|bends|bent|fold|folds|folded|brake|v-groove|groove and fold|press brake)\b", re.I)


def profile_section(part, r, v, kept, letters):
    """A bent part's profile: the section across one run of bends, at the largest ISO scale (5:1 down) at which it
    fits 120 mm with its shortest flange 8 or more on paper; a long run (a tray's base) is windowed to its start end,
    up to 20 into its longest flange, and the title says the other end is the same when the run is symmetric. A
    window the same as one already drawn adds nothing (that section reads typical)."""
    ch = r.chain
    P3 = lambda q: vadd(vadd(vmul(ch.u, q[0]), vmul(ch.v, q[1])), vmul(ch.axis, vdot(r.point, ch.axis)))
    marks = [ch.start] + [f.outer_pt for f in ch.folds]
    shortest = min(L for L, _d in ch.flanges)
    longest = max(range(len(ch.flanges)), key=lambda i: ch.flanges[i][0])
    loops = [face_loops(f, v) for f in cut_faces(kept, r.point, r.n)]
    prims = [p for lp in loops for p in lp]
    e = project.extent(prims)
    size = max(e[2] - e[0], e[3] - e[1])
    scales = (5.0, 2.0, 1.0, 0.5, 0.2, 0.1)
    s_full = next((s_ for s_ in scales if size * s_ <= 120.0 and shortest * s_ >= 8.0), None)
    window = None
    shown = list(range(len(ch.flanges)))
    if s_full is None:
        # its start end: the flanges before the longest, and 20 into the longest
        d = ch.flanges[longest][1]
        stop = marks[longest]
        stop = (stop[0] + d[0] * 20.0, stop[1] + d[1] * 20.0)
        pts = [v.to2d(P3(q)) for q in ch.skins["A"][:1] + ch.skins["B"][:1] + marks[1:longest + 1] + [stop]]
        pts += [v.to2d(P3(f.inner_pt)) for f in ch.folds[:longest]]
        window = (min(q[0] for q in pts) - 3.0, max(q[0] for q in pts) + 3.0,
                  min(q[1] for q in pts) - 3.0, max(q[1] for q in pts) + 3.0)
        shown = list(range(longest))
        sym = [round(L, 3) for L, _d in ch.flanges] == [round(L, 3) for L, _d in ch.flanges][::-1] and \
            [round(f.angle, 3) for f in ch.folds] == [round(f.angle, 3) for f in ch.folds][::-1]
        if not sym:
            raise NotDrawable("%s: a long run of bends whose two ends differ isn't drawn yet" % part.pn)
        key = tuple(round(ch.flanges[i][0], 3) for i in shown) + tuple(round(f.angle, 3) for f in ch.folds[:longest])
        prev = getattr(part, "_profile_keys", {})
        if key in prev:
            prev[key].typical = True
            return None
        kept = geom.window_keep(kept, v, *window)
        loops = [face_loops(f, v) for f in cut_faces(kept, r.point, r.n)]
        prims = [p for lp in loops for p in lp]
        for p_ in prims:
            if p_.kind == "line" and all(min(abs(q[0] - window[0]), abs(q[0] - window[1])) < 1e-4 or
                                         min(abs(q[1] - window[2]), abs(q[1] - window[3])) < 1e-4 for q in (p_.p, p_.q)):
                p_.src = "break"            # cut short here: a break line (ISO 128-20, Reviewer 12 on 811101)
        e = project.extent(prims)
        size = max(e[2] - e[0], e[3] - e[1])
        s_full = next((s_ for s_ in scales if size * s_ <= 120.0 and min(ch.flanges[i][0] for i in shown) * s_ >= 8.0),
                      None) or next((s_ for s_ in scales if size * s_ <= 120.0), 1.0)
    for i in shown:
        d = ch.flanges[i][1]
        d2 = v.to2d(vsub(P3((d[0], d[1])), P3((0.0, 0.0))))
        if abs(d2[0]) > 1e-6 and abs(d2[1]) > 1e-6:
            raise NotDrawable("%s: a flange at an angle to the views isn't sized yet" % part.pn)
    vd = VD(v, prims, s_full, "removed")
    vd.hatch = loops
    vd.letter = next(letters)
    vd.name = "removed"
    vd.r = r
    vd.profile = {"chain": ch, "shown": shown, "window": window, "P3": P3, "marks": marks + [None], "typical": False}
    vd.typical = False
    r.vd = vd
    r.letter = vd.letter
    if window:
        part.__dict__.setdefault("_profile_keys", {})[tuple(round(ch.flanges[i][0], 3) for i in shown) +
                                                     tuple(round(f.angle, 3) for f in ch.folds[:longest])] = vd
    return vd


FLAT_W, FLAT_H = 480.0, 300.0       # the most a flat pattern takes on the sheet


def _draw_flat(sh, vd):
    """A flat pattern's lines as the views draw them: the cut outline thick, bend lines thin chain, zone edges thin."""
    for p in vd.prims:
        w, d = W_VIS, None
        if p.src == "bend":
            w, d = W_THIN, (12.0, 1.5, 1.0, 1.5, 1.0, 1.5)
        elif p.src == "zone":
            w, d = W_THIN, None
        if p.kind == "line":
            sh.line(vd.S(p.p), vd.S(p.q), w, d)
        elif p.kind == "arc":
            sh.arc(vd.S(p.c), p.r * vd.scale, p.a0, p.a1, w, d)
        else:
            sh.bezier([vd.S(q) for q in p.pts], w, d)


def flat_view(part, cap=None, box=None):
    """The flat pattern as the team's DXF draws it, in its own x and y: the cut outline thick, the bend lines thin
    chain (ISO 128-20 type 05), the bend zones' edges thin; at the largest ISO scale (1:1 down) at which it fits
    FLAT_W x FLAT_H and the cap (the layout lowers it where the flat's row would run off the sheet; Reviewer 12:
    811201's flat came out at 1:20 with its Ø10 a dot where 1:5 fits)."""
    import sheetmetal
    dx = part.flat.dxf
    prims = []
    for lay, a, b in dx.lines:
        role = dx.role(lay)
        if role in ("cut", "bend", "zone"):
            pr = project.Prim("line", True, p=a, q=b)
            pr.src = {"cut": "sharp", "bend": "bend", "zone": "zone"}[role]
            prims.append(pr)
    for lay, c, rad, a0, a1 in dx.arcs:
        if dx.role(lay) == "cut":
            a0r, a1r = math.radians(a0), math.radians(a1)
            if a1r <= a0r:
                a1r += 2 * math.pi
            pr = project.Prim("arc", True, c=c, r=rad, a0=a0r, a1=a1r)
            pr.src = "sharp"
            prims.append(pr)
    for lay, c, rad in dx.circles:
        if dx.role(lay) == "cut":
            pr = project.Prim("arc", True, c=c, r=rad, a0=0.0, a1=2 * math.pi)
            pr.src = "sharp"
            prims.append(pr)
    for lay, deg, kn, ctrl in dx.splines:
        if dx.role(lay) != "cut":
            continue
        segs = sheetmetal.spline_beziers(deg, kn, ctrl)
        if segs is None:
            raise NotDrawable("%s: its DXF has a spline of degree %d, which isn't drawn yet" % (part.pn, deg))
        for sg in segs:
            pr = project.Prim("bezier", True, pts=list(sg))
            pr.src = "sharp"
            prims.append(pr)
    e = project.extent(prims)
    bw, bh = box or (FLAT_W, FLAT_H)
    fs = next((s_ for s_ in (1.0, 0.5, 0.2, 0.1, 0.05) if (e[2] - e[0]) * s_ <= bw and (e[3] - e[1]) * s_ <= bh
               and (cap is None or s_ <= cap + 1e-9)), 0.05)
    vd = VD(View("flat", (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)), prims, fs, "flat")
    vd.name = "flat"
    return vd


def profile_dims(sh, vd):
    """A bent part's profile: each flange shown whole sized outside (from the free edge or a fold's outside sharp to
    the next), on its outer side, horizontal or vertical as it runs in the view (ISO 129-1)."""
    pr = vd.profile
    ch, P3 = pr["chain"], pr["P3"]
    marks = [ch.start] + [f.outer_pt for f in ch.folds]
    end = ((ch.skins["A"][-1][0] + ch.skins["B"][-1][0]) / 2, (ch.skins["A"][-1][1] + ch.skins["B"][-1][1]) / 2)
    marks.append(end)
    bx = vd.box()
    cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
    used = {}
    for i in pr["shown"]:
        a, b = vd.S(vd.view.to2d(P3(marks[i]))), vd.S(vd.view.to2d(P3(marks[i + 1])))
        d = ch.flanges[i][1]
        d2 = vd.view.to2d(vsub(P3((d[0], d[1])), P3((0.0, 0.0))))
        if abs(d2[0]) > abs(d2[1]):         # the flange runs across the view: sized along x, beside it
            side = "down" if (a[1] + b[1]) / 2 <= cy else "up"
        else:
            side = "left" if (a[0] + b[0]) / 2 <= cx else "right"
        gap = 6.0 + 8.0 * used.get(side, 0)
        used[side] = used.get(side, 0) + 1
        sh.dim_linear(a, b, side, gap, fmt(ch.flanges[i][0]), 2.5)


def flat_dims(sh, part, fv):
    """The flat pattern's overall size, and each bend line's tag by its end (outside the outline where clear)."""
    x0, y0, x1, y1 = fv.box()
    box = part.flat.dxf.cut_box()
    sh.dim_linear((x0, y0), (x1, y0), "down", 8.0, fmt(box[2] - box[0]), 2.5)
    sh.dim_linear((x0, y0), (x0, y1), "left", 8.0, fmt(box[3] - box[1]), 2.5)
    for row in part.flat.rows:
        a, b = row["line"]
        pa, pb = fv.S(a), fv.S(b)
        d = (pb[0] - pa[0], pb[1] - pa[1])
        L = math.hypot(*d) or 1.0
        u = (d[0] / L, d[1] / L)
        cands = []
        for end, sg in ((pb, 1.0), (pa, -1.0)):
            for k in (2.0, 4.0, 7.0):
                q = (end[0] + u[0] * sg * k, end[1] + u[1] * sg * k)
                an = "left" if u[0] * sg > 0.5 else ("right" if u[0] * sg < -0.5 else "center")
                cands.append((q[0], q[1] - 1.25, an))
        # where those are taken (a small flat's bend lines end at the corner reliefs, by the next wall): beside the
        # line, just inside each end, on either side of it
        for end, sg in ((pb, -1.0), (pa, 1.0)):
            for k in (3.0, 8.0, 15.0):
                q = (end[0] + u[0] * sg * k, end[1] + u[1] * sg * k)
                for side in (1.0, -1.0):
                    nx_, ny_ = -u[1] * side, u[0] * side
                    an = "left" if nx_ > 0.5 else ("right" if nx_ < -0.5 else "center")
                    cands.append((q[0] + nx_ * 1.5, q[1] + ny_ * 1.5 - (1.25 if abs(ny_) < 0.5 else (0.0 if ny_ > 0 else 2.5)),
                                  an))
        pick = next((c for c in cands if sh.is_free(sh.text_box(c[0], c[1], row["tag"], 2.5, c[2], bold=True))), None)
        if pick is None:
            raise NotDrawable("%s: no clear place for bend %s's tag in the flat pattern" % (part.pn, row["tag"]))
        sh.text(pick[0], pick[1], row["tag"], 2.5, pick[2], bold=True)
        row["printed_at"] = sh.text_box(pick[0], pick[1], row["tag"], 2.5, pick[2], bold=True)


def flat_data(part, pl):
    """A bent part's flat pattern as the sheet gives it, for the read-back: its DXF, the K-factor and radius, the
    chains' outside flange lengths, fold angles and thickness, each bend's row, how each flange unfolds into the flat
    (the reading the holes pinned, or one of several the DXF's symmetry makes the same part) and where the flat view
    sits."""
    fl = getattr(part, "flat", None)
    if not fl:
        return None
    fv = (getattr(pl, "flats", None) or [None])[0]
    return {"dxf": inputs.rel(fl.path), "sha256_12": inputs.sha12(fl.path), "k": fl.k, "r": fl.radius,
            "chains": [{"t": ch.t, "flanges": [L for L, _d in ch.flanges], "angles": [f.angle for f in ch.folds],
                        "radii": [f.r for f in ch.folds], "dxf_axis": m["dxf_axis"], "reversed": m["reversed"]}
                       for ch, m in zip(fl.chains, fl.matches)],
            "rows": [{"tag": r_["tag"], "axis": r_["axis"], "at": r_["at"], "dir": r_["dir"], "angle": r_["angle"],
                      "r": r_["r"], "printed_at": r_.get("printed_at")} for r_ in fl.rows],
            "map": fl.map.record(), "readings": fl.readings,
            "view": dict({"off": fv.off, "scale": fv.scale, "box": fv.box()}, **({"page": fv.page} if getattr(fv, "page", 0)
                                                                              else {})) if fv else None}


def bent_flat(part, team, bent):
    """A bent part's fold chains matched to its team's DXF (sheetmetal.analyse), or NotDrawable with the reason."""
    import glob as _glob
    import sheetmetal
    if len(part.bodies) != 1:
        raise NotDrawable("%s: a bent part of %d bodies isn't drawn yet" % (part.pn, len(part.bodies)))
    b = part.bodies[0]
    cfg = bent if isinstance(bent, dict) else {}
    # a test's own part gives its DXF; a team's part has it beside its STEP
    dxfs = [cfg["dxf"]] if cfg.get("dxf") else sorted(_glob.glob(os.path.join(inputs.MANUF, team, "%s_*_DXF.dxf" % part.pn)))
    if not dxfs:
        raise NotDrawable("%s: a bent part needs its flat pattern's DXF in v2/03-Manufacturing/%s" % (part.pn, team))
    holes = [ft.f for ft in part.features if ft.body is b and ft.kind == "hole"]
    slots = [ft.f for ft in part.features if ft.body is b and ft.kind != "hole"]
    if slots:
        # the flat's check matches round holes only: a slot's DXF outline would go unchecked
        raise NotDrawable("%s: a bent part's slots aren't matched to its DXF yet (%d in the model)" % (part.pn, len(slots)))
    try:
        fl = sheetmetal.analyse(b, dxfs[0], radius=cfg.get("radius"), radius_from=cfg.get("radius_why"), holes=holes)
    except ValueError as e:
        raise NotDrawable("%s: %s" % (part.pn, e))
    odd = sheetmetal.unexplained_faces(b, fl.chains, holes, slots)
    if odd:
        raise NotDrawable("%s body %s has faces this tool can't dimension: %s" % (part.pn, b.name, ", ".join(odd[:3])))
    fl.path = dxfs[0]
    return fl


def folded_or_bent(part):
    """Why the part is a bent or folded sheet, or None. Its process says so, or its geometry does: a thin-walled
    body whose sheet faces run in two or more directions while its cross-section is one open outline (a tube's
    cross-section closes round its bore, so a tube is not folded). Sharp folds count too (an ACP skin's V-groove
    fold has no bend radius in the model)."""
    proc = (part.row.get("process") or "") + " " + (part.row.get("name") or "")
    m = BENT_WORDS.search(proc)
    if m:
        return "bent or folded (its parts list says '%s')" % m.group(0)
    if EXTRUDED_WORDS.search(proc + " " + (part.row.get("type") or "")):
        return None         # an extrusion's open section is its profile, not a fold (plain_section judges it)
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
        # open or closed cross-section, at three places (one may cut through a hole), across the line both wall
        # directions run along (a tube's axis, a fold's line); with more directions, across the longest side. A tube
        # shorter than its section (FRONT's 15 mm C10 stub) is cut across its own axis, so it closes
        if len(dirs) == 2:
            n = geom.canon_dir(geom.vnorm(geom.vcross(dirs[0], dirs[1])))
        else:
            lk = max(range(3), key=lambda k: b.size[k])
            n = tuple(1.0 if k == lk else 0.0 for k in range(3))
        sv = [vdot(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))), n) for v in geom._vertices_of(b.shape)]
        s0, s1 = min(sv), max(sv)
        from OCP.TopAbs import TopAbs_WIRE
        opens = 0
        for t in (0.31, 0.47, 0.63):
            pt = vadd(b.centroid, vmul(n, s0 + t * (s1 - s0) - vdot(b.centroid, n)))
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


def _rectangle(wire, cuts=False):
    """True when a wire is four straight edges, each parallel or square to the first; with cuts, also short edges at
    45° to them across corners (bevels along a member, legs 5 or less)."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Line
    dirs = []
    e = TopExp_Explorer(wire, TopAbs_EDGE)
    while e.More():
        ed = TopoDS.Edge_s(e.Current())
        if BRepAdaptor_Curve(ed).GetType() != GeomAbs_Line:
            return False
        vs = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))) for v in geom._vertices_of(ed)]
        if len(vs) != 2:
            return False
        dirs.append((geom.vnorm(geom.vsub(vs[1], vs[0])), math.dist(vs[0], vs[1])))
        e.Next()
    ref = max(dirs, key=lambda t: t[1])[0]
    square = [d for d, L in dirs if abs(vdot(d, ref)) < 1e-6 or abs(abs(vdot(d, ref)) - 1) < 1e-6]
    cut = [d for d, L in dirs if cuts and abs(abs(vdot(d, ref)) - 0.7071068) < 1e-4 and L <= 5.0 * math.sqrt(2) + 0.01]
    return len(square) == 4 and len(square) + len(cut) == len(dirs)


def _convex(wire, lax):
    """True when a wire is straight edges round a convex outline (seen along lax)."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepTools import BRepTools_WireExplorer
    from OCP.GeomAbs import GeomAbs_Line
    u = vnorm(vcross(lax, (1.0, 0.0, 0.0) if abs(lax[0]) < 0.9 else (0.0, 1.0, 0.0)))
    v = vcross(lax, u)
    pts = []
    ex = BRepTools_WireExplorer(wire)
    while ex.More():
        if BRepAdaptor_Curve(ex.Current()).GetType() != GeomAbs_Line:
            return False
        p = geom.pnt(BRep_Tool.Pnt_s(ex.CurrentVertex()))
        pts.append((vdot(p, u), vdot(p, v)))
        ex.Next()
    if len(pts) < 3:
        return False
    sgn = 0
    for i in range(len(pts)):
        a, b_, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        cr = (b_[0] - a[0]) * (c[1] - b_[1]) - (b_[1] - a[1]) * (c[0] - b_[0])
        if abs(cr) < 1e-9:
            continue
        if sgn and (cr > 0) != (sgn > 0):
            return False
        sgn = cr
    return True


def plain_section(b, lax):
    """True when a straight member's cross-section, at some station clear of its holes, is a solid convex outline (a
    bar, or a block with an angled side face, as the corner keys) or a rectangle with one rectangular bore (a
    rectangular tube): shapes its views, its section and its material line define. An angle, a channel or a custom
    extrusion (FRONT's kick strip 361002) has a profile to size, which drawgen doesn't do yet (D-139 keeps a
    profile's dimensioned section with Fusion)."""
    from OCP.TopAbs import TopAbs_WIRE
    sv = [vdot(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v))), lax) for v in geom._vertices_of(b.shape)]
    s0, s1 = min(sv), max(sv)
    for t in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8):
        pt = vadd(b.centroid, vmul(lax, s0 + t * (s1 - s0) - vdot(b.centroid, lax)))
        faces = cut_faces(geom.half_space_keep(b.shape, pt, lax), pt, lax)
        if len(faces) != 1:
            continue
        wires = []
        e = TopExp_Explorer(faces[0], TopAbs_WIRE)
        while e.More():
            wires.append(TopoDS.Wire_s(e.Current()))
            e.Next()
        if len(wires) == 1 and _convex(wires[0], lax):
            return True
        if len(wires) == 2:
            # the outer outline may have bevels across its corners (recognised as chamfers along the member); the bore
            # is a plain rectangle
            size = [sum((max(c) - min(c)) for c in zip(*[geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v)))
                                                          for v in geom._vertices_of(w)])) for w in wires]
            outer, inner = (wires[0], wires[1]) if size[0] >= size[1] else (wires[1], wires[0])
            if _rectangle(outer, cuts=True) and _rectangle(inner):
                return True
    return False


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

def find_step(pn, team):
    """The part's own STEP, else the team assembly STEP that holds it."""
    own = inputs.own_step(pn)
    if own:
        return own
    folder = os.path.join(inputs.MANUF, team)
    for f in sorted(os.listdir(folder)):
        nm = inputs.parse_name(os.path.join(folder, f))
        if not nm or nm["doc"] != "STEP":
            continue
        try:
            for name, solids in geom.read_step(os.path.join(folder, f)):
                if geom.part_number_of(name) == pn and solids:
                    return os.path.join(folder, f)
        except RuntimeError:
            continue
    return None


def spigot_origin(part, spec=None):
    """Parts that locate on spigots (joints register R-J13; R-J6 positions every bolt hole from the round spigot
    hole). Datums: A the face the spigot hole enters (the seat), B the round spigot hole's axis, C a face square to
    A and parallel to B, which stops the turn about B. Origin O: datum B's axis on datum A.

    spec: spigot_dia (8.5, the frames' round hole; 9.53 for a band's spigot rivnut), spigot_pick ('-Y': the one
    nearest the front) or spigot_near ({'X': -102.75}: the one nearest that pod coordinate), spigot_slot (True: a
    frame also has the slot), c_face ('-X'...; default the room-side face across the part's thinnest direction),
    a_words / c_words (what the faces are)."""
    spec = spec or {}
    dia = spec.get("spigot_dia", 8.5)
    rounds = [ft for ft in part.features if ft.kind == "hole" and ft.reg and "spigot" in
              (ft.reg["function"] + " " + ft.reg["mating"]).lower() and abs(ft.f.dia - dia) < 0.05]
    slots = [ft for ft in part.features if ft.kind == "slot"]
    if not rounds or (spec.get("spigot_slot", True) and not slots):
        return None
    pick = spec.get("spigot_pick")
    if pick:
        k = "XYZ".index(pick[1])
        rounds.sort(key=lambda ft: ft.f.entry[k] * (1 if pick[0] == "-" else -1))
    near = spec.get("spigot_near")
    if near:
        ((ax, v),) = near.items()
        k = "XYZ".index(ax)
        rounds.sort(key=lambda ft: abs(ft.f.entry[k] - v))
    b = rounds[0]
    if spec.get("c_face"):
        cf = spec["c_face"]
        k = "XYZ".index(cf[1])
        c_normal = tuple((1.0 if cf[0] == "+" else -1.0) if i == k else 0.0 for i in range(3))
        c_plane = part.box[3 + k] if cf[0] == "+" else part.box[k]
        c_words = spec.get("c_words", "the %s face (%s %s)" % (FACE_WORDS.get(cf, "face"), cf[1], fmt(c_plane)))
    else:
        # the frame's room-side face, square to the wall and parallel to B (the slot runs across the rail, R-J17,
        # so it can't stop the turn)
        k = min(range(3), key=lambda i: part.size[i])
        toward_centre = -1.0 if part.box[k] + part.box[3 + k] > 0 else 1.0
        c_normal = tuple(toward_centre if i == k else 0.0 for i in range(3))
        c_plane = part.box[3 + k] if toward_centre > 0 else part.box[k]
        c_words = "the room-side face (%s %s)" % ("XYZ"[k], fmt(c_plane))
    return {"O": b.f.entry, "A_normal": b.f.normal, "B": b, "C": None, "C_plane": (c_normal, c_plane),
            "slot": slots[0] if slots else None,
            "words": {"A": spec.get("a_words", "%s of %s (the seat on the band)" % (
                FACE_WORDS.get(axis_name(b.f.normal), "face"), b.body.name)),
                      "B": "axis of the spigot hole %s" % "{B}",
                      "C": c_words + ", which stops the turn about B"}}


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


def face_origin(part, pl, nm, v):
    """An angled-face view's own origin (the PM's ruling on #296, Reviewer 5): on the face that holds its holes,
    the face's centre line across the view at its bottom edge, so X reads from the face's middle and Y from its
    bottom (as Joints' key sheet: 'on its centre line, 26 and 60 above the bottom')."""
    feats = [ft for g in pl.groups if g.view == nm for ft in g.feats]
    best = None
    for b in {id(ft.body): ft.body for ft in feats}.values():
        for n, off, area, face in geom.planes(b):
            if vdot(n, v.n) < 0.9999:
                continue
            if all(abs(vdot(ft.f.entry, n) - off) < 0.05 for ft in feats if ft.body is b):
                if best is None or area > best[0]:
                    best = (area, face, off)
    if best is None:
        return None, ""
    pts = [v.to2d(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(q)))) for q in _vertices(best[1])]
    xm = (min(p_[0] for p_ in pts) + max(p_[0] for p_ in pts)) / 2
    yb = min(p_[1] for p_ in pts)
    o3 = vadd(vadd(vmul(v.x, xm), vmul(v.y, yb)), vmul(v.n, best[2]))
    return o3, "on the face's centre line, at its bottom edge"


def end_origin(part, pl, nm, v):
    """A long part's end view's own origin: the bottom left corner of the member's outline in that view (a tube's
    end: its bottom face and a side face), on the end's plane, so the table's X and Y read from the member's own
    faces as the view's sizes do (BASE's 111103: the slot's end 63.5 above the bottom face, where the end face's own
    bottom edge sits 1 up, above the bevel)."""
    feats = [ft for g in pl.groups if g.view == nm for ft in g.feats]
    bodies = [b for b in part.bodies if any(ft.body is b for ft in feats)]
    pts = [v.to2d(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(q)))) for b in bodies for q in geom._vertices_of(b.shape)]
    x0, y0 = min(p_[0] for p_ in pts), min(p_[1] for p_ in pts)
    d = max(vdot(ft.f.entry, v.n) for ft in feats)
    return vadd(vadd(vmul(v.x, x0), vmul(v.y, y0)), vmul(v.n, d)), "at the member's bottom left corner"


def aux_view(pl, rel, normal):
    """The view square to an angled face (ISO 128-30: a view in the direction of an arrow, lettered), shared by the
    faces of one normal. It keeps the principal view's up (its Y laid into the face) where it can, else its X, so
    the part reads the same way up as in the principal view."""
    for nm, v in pl.aux.items():
        if vdot(v.n, normal) > 0.9999:
            return nm
    P = pl.principal
    up = vsub(P.y, vmul(normal, vdot(P.y, normal)))
    if math.sqrt(vdot(up, up)) > 0.3:
        x = vcross(vnorm(up), normal)           # with Y = up: n x X = Y
    else:
        x = None
        for cand in (P.x, P.n):
            x = vsub(cand, vmul(normal, vdot(cand, normal)))
            if math.sqrt(vdot(x, x)) > 0.3:
                break
    nm = "aux%d" % (len(pl.aux) + 1)
    v = View(nm, normal, vnorm(x))
    pl.aux[nm] = v
    rel[nm] = v
    return nm


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
    # a straight member lying off the pod's axes (FRONT's 352211, a cross tube on the diagonal): drawn along its own
    # axis, looking square to a side, so its length runs across the sheet and its end cuts read from its axis
    ma = geom.member_axis(part.bodies[0]) if len(part.bodies) == 1 and not spec.get("principal") else None
    turned = False
    if ma is not None:
        sides_ = sorted((t for t in geom.planes(part.bodies[0]) if abs(vdot(t[0], ma)) < 1e-6), key=lambda t: -t[2])
        # its section turned about its axis (FRONT's 352208, 45°: 28.24 high as drawn): its largest side faces off the
        # pod's axes
        turned = bool(sides_) and axis_name(sides_[0][0]) is None
    if ma is not None and (axis_name(ma) is None or turned):
        P0 = pl.principal
        n = P0.n
        if abs(vdot(n, ma)) > 1e-6 or turned:     # look square to the side face nearest the view it had
            sides = [t[0] for t in geom.planes(part.bodies[0]) if abs(vdot(t[0], ma)) < 1e-6]
            n = max(sides, key=lambda v: vdot(v, P0.n)) if sides else n
        sgn = vdot(ma, P0.x) if abs(vdot(ma, P0.x)) > 1e-6 else vdot(ma, P0.y)
        pl.principal = View("principal", n, ma if sgn >= 0 else vmul(ma, -1.0))
        pl.principal.pod_name = "along the member"
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
    pl.aux = {}             # angled faces: a lettered view square to each (its name -> View)
    pl.aux_ends = set()     # the lettered views of a long part's ends
    P1 = pl.principal
    long_x = sum(abs(P1.x[i]) * part.size[i] for i in range(3))
    long_y = sum(abs(P1.y[i]) * part.size[i] for i in range(3))
    for key, feats in sorted(face_groups(part).items(), key=lambda kv: kv[0]):
        normal = feats[0].f.normal
        vname = next((nm for nm, v in rel.items() if vdot(v.n, normal) > 0.9999), None)
        if vname in ("from_left", "from_right") and long_x > 8.0 * long_y:
            # an end of a long part (BASE's back band's end plates): a lettered view by itself, at its own scale,
            # rather than beside the principal view where it would cost the whole sheet a scale step
            vname = aux_view(pl, rel, normal)
            pl.aux_ends.add(vname)
        if vname is None:
            vname = aux_view(pl, rel, normal)
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
    # a chamfer no planned view shows (edge on, or as a band it faces) gets one: the view along its edge first (its
    # true 45°), else one it faces (a bevel along a featureless tube needs the tube's end view)
    def shows(v, ch):
        on = abs(abs(vdot(v.n, ch.edge)) - 1) < 1e-6 and abs(vdot(v.n, ch.n)) < 1e-6
        return on or (abs(vdot(v.n, ch.edge)) < 1e-6 and vdot(v.n, ch.n) > 0.05)
    for ch in getattr(part, "chamfers", []):
        if any(shows(rel[nm], ch) for nm in pl.plain if nm in rel):
            continue
        cand = [nm for nm, v in rel.items() if abs(abs(vdot(v.n, ch.edge)) - 1) < 1e-6 and abs(vdot(v.n, ch.n)) < 1e-6] or \
            [nm for nm, v in rel.items() if shows(v, ch)]
        if cand:
            pl.plain.add(cand[0])
    # every end cut (a mitre, a compound cut's faces) shown in profile by a drawn view: edge on, the member's axis
    # across the view, where its angle from square prints at its end. A view is added where none does (FRONT's #320:
    # 8 tubes whose only view saw their mitres face on, as bands); a cut no plain view shows in profile is refused
    for b in part.bodies:
        lax_ = geom.member_axis(b)
        if lax_ is None:
            continue
        for n_, _off, area_, face_ in geom.planes(b):
            if not (0.02 < abs(vdot(n_, lax_)) < 0.9998):
                continue
            if any(face_.IsSame(cf) for ch in getattr(part, "chamfers", []) for cf in ch.faces):
                continue
            prof = [nm for nm, v in rel.items() if abs(vdot(n_, v.n)) < 1e-6 and abs(vdot(lax_, v.n)) < 1e-6]
            if any(nm in pl.plain for nm in prof):
                continue
            if not prof:
                raise NotDrawable("%s: an end cut of %s (normal %s) that no plain view shows in profile: a compound cut "
                                  "isn't drawn yet" % (part.pn, b.name, tuple(round(c, 3) for c in n_)))
            pl.plain.add(prof[0])
    # a notch is sized in the plain view that looks at its wall from outside (enlarged in a detail when small)
    for nt in getattr(part, "notches", []):
        vname = next((nm for nm, v in rel.items() if vdot(v.n, nt.wall_n) > 0.9999), None)
        if vname is None:
            raise NotDrawable("%s: no plain view looks at the wall the notch at its %s end goes through" % (
                part.pn, axis_name(vmul(nt.lax, nt.sgn)) or "far"))
        pl.plain.add(vname)
    # a face nothing shows: when every hole on it is the far-wall twin of a hole on a face that a plain view
    # shows (same member, same axis), the removed section through the pair shows it (D-113) and its table
    # uses that view's X and Y; any other hidden face gets its own section just in front of it
    by_feat = {id(ft): g for g in pl.groups for ft in g.feats}
    for g in pl.groups:
        if not g.blocked:
            g.view = g.vname
            if g.vname not in pl.aux:
                pl.plain.add(g.vname)
    for g in pl.groups:
        if not g.blocked:
            continue
        if g.vname in pl.aux:
            raise NotDrawable("%s: holes on an angled face (normal %s) that the part itself hides" % (part.pn, g.key[0]))
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
    # (a bent part's holes on one line sit in two of its flanges, each shown in its own face's view: no section, which
    # would cut the whole part; CEILING's tray 513101: its two Ø19.1 bushing holes across the tray)
    for st in ([] if getattr(part, "flat", None) else two_wall_sets(part)):
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
    # a bevel along a member is drawn at its true 45° in a section across that member (Reviewer 6 on #331: C1's seam
    # bevel showed only as a band at 1:5): one is added where no removed section crosses that member
    for ch in getattr(part, "chamfers", []):
        if not ch.long or any(r_.body is ch.body for r_ in pl.removed):
            continue
        P0 = pl.principal
        yv = next((c for c in (P0.y, P0.x, P0.n) if abs(vdot(c, ch.lax)) < 0.99), None)
        yv = vnorm(vsub(yv, vmul(ch.lax, vdot(yv, ch.lax))))
        pts = [geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(q))) for q in geom._vertices_of(ch.body.shape)]
        sv = [vdot(q, ch.lax) for q in pts]
        r = Plan()
        r.feats, r.all, r.body = [], [], ch.body
        r.n, r.y = ch.lax, yv
        r.point = vadd(ch.body.centroid, vmul(ch.lax, (min(sv) + max(sv)) / 2 - vdot(ch.body.centroid, ch.lax)))
        r.bevel = ch
        pl.removed.append(r)
    # a bent part: a section across each run of bends (its profile), seen as the related view along the bend lines
    # sees it, so each flange's outside length is sized where it shows true
    for ch in (part.flat.chains if getattr(part, "flat", None) else []):
        vn = next((v for v in rel.values() if abs(abs(vdot(v.n, ch.axis)) - 1) < 1e-6), None)
        if vn is None:
            raise NotDrawable("%s: no related view looks along its bend lines (%s)" % (part.pn, ch.axis))
        b = part.bodies[0]
        sv = [vdot(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(q))), ch.axis) for q in geom._vertices_of(b.shape)]
        r = Plan()
        r.feats, r.all, r.body, r.chain = [], [], b, ch
        r.n, r.y = vn.n, vn.y
        r.point = vadd(b.centroid, vmul(ch.axis, (min(sv) + max(sv)) / 2 - vdot(b.centroid, ch.axis)))
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
        dat = spigot_origin(part, spec)
        if dat is None:
            raise NotDrawable("%s: no spigot hole and slot found for its datums" % part.pn)
    else:
        dat = spec_origin(part, spec)
    O = dat["O"]

    # ---- tags, in the order the tables list them
    order = ["principal", "below", "above", "from_left", "from_right", "rear"]
    vorder = lambda nm: order.index(nm) if nm in order else len(order) + sorted(pl.aux).index(nm)
    groups = sorted(pl.groups, key=lambda g: (g.view is None, vorder(g.view or g.vname), g.coax_of is not None, g.key))
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
    # the hole tables take the right column; when the views don't fit beside it at a scale, a narrower column (its
    # text wraps more) is tried before a smaller scale, as long as the tables still end above the title block
    tw0 = spec.get("table_w", TABLE_W)
    room = H - 16 - TB_ROOM

    def tables_fit(tw):
        return tw == tw0 or tables_height(sh, part, groups, tw) <= room
    scale, rear_down, table_w = None, False, tw0
    for s in ISO_SCALES:
        if spec.get("scale") and abs(s - spec["scale"]) > 1e-9:
            continue
        if spec.get("_max_scale") and s > spec["_max_scale"] + 1e-9:
            continue
        for tw in (tw0, 230.0, 200.0):
            if tw > tw0 or not tables_fit(tw):
                continue
            avail_w = W - 20 - 10 - spec.get("right_w", tw + 16.0) - 20
            for rd in ((False, True) if "rear" in exts else (False,)):
                bw, bh = block(s, rd)
                if bw <= avail_w and bh <= avail_h:
                    scale, rear_down, table_w = s, rd, tw
                    break
            if scale:
                break
        if scale:
            break
    if scale is None:
        raise NotDrawable("%s doesn't fit on %s at any ISO scale down to 1:20" % (part.pn, size))
    bw, bh = block(scale, rear_down)
    pl.rear_down = rear_down
    pl.table_w = table_w
    # the right column holds the hole tables and the title block, drawn last: no label goes there
    sh.reserved.append((W - 10 - table_w - 4 - 2.0, 10.0, W - 10.0, H - 10.0))

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
    letters = iter("DEFGHJKLMNPRSTUVWXYZ")       # A, B and C name the datums
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
        if getattr(r, "chain", None) is not None:
            vd = profile_section(part, r, v, kept, letters)
            if vd is None:
                continue                # the same as a section already drawn: its title says typical
            removed.append(vd)
            continue
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
    auxs = []
    for nm, v in sorted(pl.aux.items()):
        own = {id(ft.body) for g in pl.groups if g.view == nm for ft in g.feats}
        hid = {i for i, b in enumerate(part.bodies) if id(b) in own} or None
        prims0 = view_prims(part.shape, v, 1.0, bodies=shapes, hidden_from=hid)
        e0 = project.extent(prims0)
        vs = next((c for c in (2.0, 1.0, 0.5, 0.2, 0.1) if c >= scale - 1e-9 and
                   max(e0[2] - e0[0], e0[3] - e0[1]) * c <= 120.0), scale)
        vd = VD(v, view_prims(part.shape, v, vs, bodies=shapes, hidden_from=hid), vs, "aux")
        vd.name = nm
        vd.letter = next(letters)
        if nm in pl.aux_ends:
            vd.origin3d, vd.origin_words = end_origin(part, pl, nm, v)
        else:
            vd.origin3d, vd.origin_words = face_origin(part, pl, nm, v)
        auxs.append(vd)

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
    # detail views (guideline 6.1: details for what is small): where tags crowd at this scale, an enlarged copy of that
    # stretch of the view, cut from the solids (exact edges, the cut drawn thin as the detail's boundary)
    details = []
    pl.notch_views = {}     # view name -> (the notches it sizes, the one drawn, whether a detail enlarges it)
    for nm, vd in list(vds.items()):
        win = crowded_window(vd, [ft for g in pl.groups if g.view == nm for ft in g.feats], part)
        if not win:
            win = open_slot_window(vd, [ft for g in pl.groups if g.view == nm for ft in g.feats])
        nwin, nts, shown = notch_window(vd, part.notches)
        if nts:
            if win and nwin:
                raise NotDrawable("%s: %s needs two details (its holes and a notch): not drawn yet" % (
                    part.pn, VIEW_WORDS.get(nm, nm).lower()))
            pl.notch_views[nm] = (nts, shown, bool(nwin))
            win = win or nwin
        if not win:
            continue
        x0, x1, y0, y1 = win
        ds = next((c for c in (2.0, 1.0, 0.5) if c >= 2 * vd.scale - 1e-9 and (x1 - x0) * c <= 140.0), None)
        if ds is None:
            continue
        kept, hid = [], set()
        own = {id(ft.body) for g in pl.groups if g.view == nm for ft in g.feats}
        for b in part.bodies:
            k_ = geom.window_keep(b.shape, vd.view, x0, x1, y0, y1)
            if geom._solids(k_):
                if id(b) in own:
                    hid.add(len(kept))
                kept.append(k_)
        if not kept:
            continue
        prims = view_prims(None, vd.view, ds, bodies=kept, hidden_from=hid)
        for p_ in prims:        # the cut at the window's edges is the detail's boundary: thin
            if p_.kind == "line" and all(min(abs(q[0] - x0), abs(q[0] - x1)) < 1e-4 or
                                         min(abs(q[1] - y0), abs(q[1] - y1)) < 1e-4 for q in (p_.p, p_.q)):
                p_.src = "boundary"
        dv = VD(vd.view, prims, ds, "detail")
        dv.name = "detail"
        dv.parent = vd
        dv.parent_name = nm
        dv.window = win
        dv.letter = next(letters)
        vd.detail = dv
        details.append(dv)
    for nm, (nts, shown, enlarged) in pl.notch_views.items():
        if enlarged and not getattr(vds[nm], "detail", None):
            raise NotDrawable("%s: no room for the detail that sizes the notch at %s" % (part.pn, nm))
    sized = {id(nt) for nts, _s, _e in pl.notch_views.values() for nt in nts}
    if any(id(nt) not in sized for nt in part.notches):
        raise NotDrawable("%s: a notch no drawn view sizes" % part.pn)
    pl.details = details
    flats = [flat_view(part, spec.get("_flat_cap"))] if getattr(part, "flat", None) and not spec.get("_flat_sheet") \
        else []
    place = removed + auxs + details + flats
    # removed sections and details: a column between the views and the tables when it is wide enough, else a row
    # under the views
    mid_x0 = main_right + GAP + 18
    mid_x1 = W - 10 - pl.table_w - 4 - 10
    need_w = (max(vd.size()[0] for vd in place) + 70) if place else 0
    if place and mid_x1 - mid_x0 >= need_w:
        rx, ry = mid_x0, H - 10 - 30
        for vd in place:
            w, h = vd.size()
            vd.off = (rx - vd.scale * vd.extent[0], ry - h - vd.scale * vd.extent[1])
            ry = ry - h - 58
    elif place:
        # under every view's title too (the principal's title sits 28 under it, its mapping up to three lines), with
        # room over the row for the sections' hole callouts
        under_titles = min([vd_.box()[1] - (28.0 if vd_ is pvd else 10.0) - 4.2 - 3.4 * 2
                            for vd_ in list(vds.values()) + secs])
        rx, ry = 20 + GAP_PL + 14, min(main_bottom - 34, under_titles - 12.0)
        right_limit = W - 10 - pl.table_w - 4 - 10
        for vd in place:
            w, h = vd.size()
            if vd.kind in ("detail", "aux") and (rx + w + 40 > right_limit or ry - h - 40 < 20):
                if vd.kind == "aux":
                    raise NotDrawable("%s: no room on the sheet for view %s (square to an angled face)" % (
                        part.pn, vd.letter))
                vd.dropped = True       # no room: the parent view keeps its tags
                continue
            vd.off = (rx - vd.scale * vd.extent[0], ry - h - vd.scale * vd.extent[1])
            rx += w + 80
    # the removed sections and the flat pattern stay on the sheet: the scale was chosen for the main views alone, so
    # where this row runs off the sheet the views are drawn again at the next smaller scale (make retries)
    right_edge = W - 10 - pl.table_w - 4 - 10
    for vd in place:
        if vd.kind in ("detail", "aux") or getattr(vd, "dropped", False):
            continue
        b_ = vd.box()
        # a flat pattern's title (three lines) goes under it, clear of the sheet's zone numbers
        if b_[1] < (38 if vd.kind == "flat" else 20) or b_[0] < 20 or b_[2] > right_edge:
            raise _Smaller(scale, flat=vd.scale if vd.kind == "flat" and vd.scale > 0.05 + 1e-9 else None)
    for dv in [d_ for d_ in details if getattr(d_, "dropped", False)]:
        if pl.notch_views.get(dv.parent_name, (None, None, False))[2]:
            raise NotDrawable("%s: no room on the sheet for the detail that sizes the notch" % part.pn)
        details.remove(dv)
        del dv.parent.detail
    pl.mid = (main_right + GAP, 0)
    for vd in auxs:             # placed: from here on a view like the others (drawn, tagged, titled, in the data)
        vds[vd.name] = vd
    report = {"pn": part.pn, "rev": part.rev, "scale": scale, "sheet": size, "views": [], "holes": []}

    # ---- draw geometry
    def draw_prims(vd):
        for p in vd.prims:
            w = W_VIS if p.vis else W_HID
            d = None if p.vis else DASH_HID
            if p.src == "boundary":
                w = W_THIN
            elif p.src == "break" and p.kind == "line":
                # a thin zigzag across the cut, 2 past the sheet each side (ISO 128-20 type 01.1 with a zigzag)
                a, b = vd.S(p.p), vd.S(p.q)
                L = math.dist(a, b) or 1.0
                u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
                nrm = (-u[1], u[0])
                a2, b2 = (a[0] - u[0] * 2.0, a[1] - u[1] * 2.0), (b[0] + u[0] * 2.0, b[1] + u[1] * 2.0)
                m = ((a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2)
                z = [a2, (m[0] - u[0] * 0.8, m[1] - u[1] * 0.8), (m[0] - u[0] * 0.4 + nrm[0] * 1.2, m[1] - u[1] * 0.4 + nrm[1] * 1.2),
                     (m[0] + u[0] * 0.4 - nrm[0] * 1.2, m[1] + u[1] * 0.4 - nrm[1] * 1.2), (m[0] + u[0] * 0.8, m[1] + u[1] * 0.8), b2]
                for k_ in range(len(z) - 1):
                    sh.line(z[k_], z[k_ + 1], W_THIN)
                continue
            elif p.src == "bend":       # ISO 128-20 type 05, thin: a bend line in a flat pattern
                w, d = W_THIN, (12.0, 1.5, 1.0, 1.5, 1.0, 1.5)
            elif p.src == "zone":       # a bend zone's edge, thin
                w, d = W_THIN, None
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
    for vd in list(vds.values()) + secs + removed + details + flats:
        draw_prims(vd)
        sh.add_obstacles(outline_segments(vd))
    pl.flats = flats
    sh.flush()

    # ---- marks, tags, origins: placed after the dimensions and titles (annotate calls pl.place_marks), lines
    # before labels, so every label is put where it touches no line and no text

    def mark_features(vd, feats, tags=True, marks=True):
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
            if marks:
                if ft.kind == "hole":
                    sh.centre_mark(c2, r, ext=1.5)
                elif ft.kind == "open_slot":
                    a2 = vd.view.to2d(ft.f.along)
                    sh.centre_mark(c2, ft.f.width / 2 * vd.scale, ext=1.2)
                    e2 = vd.S(vd.view.to2d(vadd(ft.f.entry, vmul(ft.f.along, ft.f.edge + 3.0))))
                    sh.centre_line(c2, e2)
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

    def in_window(vd, ft):
        w = getattr(vd, "detail", None)
        if not w:
            return False
        c = vd.view.to2d(ft.f.entry)
        x0, x1, y0, y1 = w.window
        return x0 <= c[0] <= x1 and y0 <= c[1] <= y1

    # one 3D origin O, its projection named per view (a detail shows its parent's origin, same name); the titles
    # name them, so the names come now and the marks later
    k = 0
    for vd in [vds[n_] for n_ in order if n_ in vds] + secs + auxs:
        k += 1
        vd.origin_name = "O%d" % k
    for dv in details:
        dv.origin_name = dv.parent.origin_name

    def place_marks():
        # 1. centre marks and the detail circles (lines)
        jobs, letters = [], []
        for nm, vd in vds.items():
            feats = [ft for g in pl.groups if g.view == nm for ft in g.feats]
            mark_features(vd, [ft for ft in feats if not in_window(vd, ft)], tags=False)
            mark_features(vd, [ft for ft in feats if in_window(vd, ft)], tags=False)
            jobs.append((vd, [ft for ft in feats if not in_window(vd, ft)]))
            if getattr(vd, "detail", None):
                dv = vd.detail
                mark_features(dv, [ft for ft in feats if in_window(vd, ft)], tags=False)
                jobs.append((dv, [ft for ft in feats if in_window(vd, ft)]))
                # the detail's place on its parent: a thin circle round the window, and its letter (step 3)
                x0, x1, y0, y1 = dv.window
                c = vd.S(((x0 + x1) / 2, (y0 + y1) / 2))
                r = max((x1 - x0), (y1 - y0)) / 2 * vd.scale * 1.08 + 2.0
                sh.circle(c, r, W_THIN)
                letters.append((vd, dv, c, r))
            # the far-wall holes behind (hidden circles) get their centre marks too, untagged
            keys = {(id(ft.body), ft.f.line_key) for ft in feats if ft.kind == "hole"}
            others = [ft for ft in part.features if ft not in feats and _end_on(ft, vd.view) and ft.kind == "hole"
                      and (id(ft.body), ft.f.line_key) in keys]
            mark_features(vd, others, tags=False)
        for vd in secs:
            mark_features(vd, vd.group.feats, tags=False)
            jobs.append((vd, vd.group.feats))
        sh.flush()
        # 2. the origins: arrows, then their names where they are clear
        for vd in [vds[n_] for n_ in order if n_ in vds] + secs + auxs:
            o2 = vd.S(vd.view.to2d(getattr(vd, "origin3d", None) or O))
            if part.features:
                bx = vd.box()
                away = (-1.0 if o2[0] <= (bx[0] + bx[2]) / 2 else 1.0, -1.0 if o2[1] <= (bx[1] + bx[3]) / 2 else 1.0)
                # the label goes outside the outline: when the origin lies inside it (a hole's centre), drop the
                # label below (or above) the outline, clear of the edge
                inside = bx[0] + 0.5 < o2[0] < bx[2] - 0.5 and bx[1] + 0.5 < o2[1] < bx[3] - 0.5
                lab_y = None
                if inside:
                    lab_y = (bx[1] - 4.2) if away[1] < 0 else (bx[3] + 1.8)
                sh.origin_mark(o2, vd.origin_name, away=away, label_y=lab_y)
        for dv in details:
            oc = dv.view.to2d(O)
            x0, x1, y0, y1 = dv.window
            if part.features and x0 <= oc[0] <= x1 and y0 <= oc[1] <= y1:
                o2 = dv.S(oc)
                bx = dv.box()
                away = (-1.0 if o2[0] <= (bx[0] + bx[2]) / 2 else 1.0, -1.0 if o2[1] <= (bx[1] + bx[3]) / 2 else 1.0)
                inside = bx[0] + 0.5 < o2[0] < bx[2] - 0.5 and bx[1] + 0.5 < o2[1] < bx[3] - 0.5
                lab_y = ((bx[1] - 4.2) if away[1] < 0 else (bx[3] + 1.8)) if inside else None
                sh.origin_mark(o2, dv.origin_name, away=away, label_y=lab_y)
        # 3. each detail's letter beside its circle, on the outer side first (away from the view's middle)
        for vd, dv, c, r in letters:
            vb = vd.box()
            sx = 1.0 if c[0] >= (vb[0] + vb[2]) / 2 else -1.0
            cands = []
            for sx_, sy_ in ((sx, 1), (sx, -1), (-sx, 1), (-sx, -1)):
                cands.append((c[0] + sx_ * (r * 0.75 + 1.5), c[1] + sy_ * (r * 0.75 + 1.0) - (3.5 if sy_ < 0 else 0.0),
                              "left" if sx_ > 0 else "right"))
            pick = next((t for t in cands if sh.is_free(sh.text_box(t[0], t[1], dv.letter, 3.5, t[2], bold=True))),
                        cands[0])
            sh.text(pick[0], pick[1], dv.letter, 3.5, pick[2], bold=True)
        # 4. the tags
        for vd, feats in jobs:
            mark_features(vd, feats, marks=False)
        sh.flush()

    pl.place_marks = place_marks
    return sh, pl, vds, secs, removed, dat, scale, report, groups


def outline_segments(vd):
    """The view's visible outline (and a section's cut outline) as sheet segments, for keeping labels off it."""
    segs = []
    prims = [p for p in vd.prims if p.vis and p.src != "boundary"] + [p for lp in vd.hatch for p in lp]
    for p in prims:
        if p.kind == "line":
            segs.append((vd.S(p.p), vd.S(p.q)))
        elif p.kind == "arc":
            n = max(4, int((p.a1 - p.a0) / (math.pi / 8)) + 1)
            pts = [vd.S((p.c[0] + p.r * math.cos(p.a0 + (p.a1 - p.a0) * k / n),
                         p.c[1] + p.r * math.sin(p.a0 + (p.a1 - p.a0) * k / n))) for k in range(n + 1)]
            segs.extend(zip(pts, pts[1:]))
        else:
            pts = [vd.S(q) for q in p.pts]
            segs.extend(zip(pts, pts[1:]))
    return segs


def _side_word(d2):
    if abs(d2[0]) > 0.5:
        return "right" if d2[0] > 0 else "left"
    return "up" if d2[1] > 0 else "down"


def notch_dims(sh, vd, nt):
    """A notch's sizes in the view (or its detail) that looks at its wall (ISO 129-1): its width and its place across
    from the nearer side face (the + side when it is centred), chained beyond the end, and its length from the end
    beside the part, past that side face. Returns the texts as written."""
    v, S = vd.view, vd.S
    plo, phi = nt.prof
    ref = phi if (phi - nt.hi) <= (nt.lo - plo) + 1e-9 else plo
    near = nt.hi if ref == phi else nt.lo
    e = nt.end_s

    def P(s_, a_):
        return S(v.to2d(nt.point(s_, a_)))
    out_end = _side_word(v.to2d(vmul(nt.lax, nt.sgn)))
    out_side = _side_word(v.to2d(vmul(nt.across, 1.0 if ref == phi else -1.0)))
    w_t, p_t, l_t = fmt(nt.width), fmt(abs(ref - near)), fmt(nt.length)
    if "down" in (out_end, out_side):       # the view's title goes under the dimensions
        vd.title_drop = max(getattr(vd, "title_drop", 0.0), 14.0)
    sh.dim_linear(P(e, nt.lo), P(e, nt.hi), out_end, 8.0, w_t, 2.5)
    sh.dim_linear(P(e, near), P(e, ref), out_end, 8.0, p_t, 2.5)
    sh.dim_linear(P(e, ref), P(nt.s_back, near), out_side, 8.0, l_t, 2.5)
    return {"width": w_t, "pos": p_t, "length": l_t, "ref": ref}


def chamfer_text(ch):
    return "%s x 45°" % fmt(ch.leg)


def chamfer_callouts(sh, part, pl, vds, removed=()):
    """Each chamfer (an edge break with equal legs): its size on a leader, in the view that looks along its edge
    and so shows its true angle, at the largest scale (ISO 129-1: '1 x 45°'); the leader goes out from the
    chamfer's middle, turned or longer until the text touches nothing and the leader crosses no text."""
    for ch in part.chamfers:
        edge = ch.edge
        hosts, bands = [], []
        # a removed section across the bevel's own member shows a bevel along it at its true angle (CEILING's seam
        # member, 2:1)
        secs_ = [r_ for r_ in removed if getattr(r_, "r", None) is not None and r_.r.body is ch.body and ch.long]
        for vd in list(vds.values()) + list(getattr(pl, "details", [])) + secs_:
            if abs(abs(vdot(vd.view.n, edge)) - 1) < 1e-6 and abs(vdot(vd.view.n, ch.n)) < 1e-6:
                into = hosts            # looking along its edge: its true 45°
            elif abs(vdot(vd.view.n, edge)) < 1e-6 and vdot(vd.view.n, ch.n) > 0.05:
                into = bands            # facing it, its edge across the view: a band (CEILING's frames)
            else:
                continue
            q2 = [vd.view.to2d(p_) for p_ in ch.pts]
            m2 = (sum(q[0] for q in q2) / len(q2), sum(q[1] for q in q2) / len(q2))
            w = getattr(vd, "window", None)
            if vd.kind == "detail" and not (w[0] <= m2[0] <= w[1] and w[2] <= m2[1] <= w[3]):
                continue
            into.append((vd, m2))
        if not hosts and not bands:
            raise NotDrawable("%s: no view shows the %s chamfer %s" % (
                part.pn, chamfer_text(ch), "along %s" % ch.body.name if ch.long else
                "at its %s end" % (axis_name(vmul(ch.lax, ch.sgn)) or "far")))
        vd, m2 = max(hosts or bands, key=lambda t: t[0].scale)
        m = vd.S(m2)
        n2 = vd.view.to2d(ch.n)
        ln = math.hypot(*n2)
        n2 = (n2[0] / ln, n2[1] / ln)
        txt = chamfer_text(ch)
        pick = None
        for lead in (6.0, 9.0, 13.0, 18.0):
            for rot in (0, 20, -20, 40, -40):
                a = math.radians(rot)
                u = (n2[0] * math.cos(a) - n2[1] * math.sin(a), n2[0] * math.sin(a) + n2[1] * math.cos(a))
                tail = (m[0] + u[0] * lead, m[1] + u[1] * lead)
                an = "left" if u[0] >= 0 else "right"
                tx = tail[0] + (0.8 if an == "left" else -0.8)
                box = sh.text_box(tx, tail[1], txt, 2.5, an, valign="mid")
                if sh.is_free(box) and not any(sh._seg_box(m, tail, b_, 0.3) for b_ in sh.boxes):
                    pick = (u, tail, tx, an)
                    break
            if pick:
                break
        if pick is None:
            raise NotDrawable("%s: no clear place for the %s chamfer's size" % (part.pn, txt))
        u, tail, tx, an = pick
        sh.line(tail, m, 0.25)
        sh.arrow(m, (-u[0], -u[1]), 2.2, 0.9)
        sh.text(tx, tail[1], txt, 2.5, an, valign="mid")
        ch.drawn = {"view": vd, "tip": m, "text": txt, "box": sh.text_box(tx, tail[1], txt, 2.5, an, valign="mid")}


def open_slot_dims(sh, vd, ft):
    """An open slot's sizes from the edge it opens on (the view's axes along and across it): the mouth under the
    edge, the width over the round end, the taper's length and the end's centre from the edge beside the part,
    and the end's radius on a leader."""
    f, v, S = ft.f, vd.view, vd.S
    c, a = v.to2d(f.entry), v.to2d(f.along)
    bx = vd.box()
    if abs(abs(a[1]) - 1) < 1e-6:               # opens down (or up) the view
        sg = 1.0 if a[1] > 0 else -1.0
        ye, yt = c[1] + sg * f.edge, c[1] + sg * (f.edge - f.taper)
        out, inn = ("down", "up") if sg < 0 else ("up", "down")
        sh.dim_linear(S((c[0] - f.mouth / 2, ye)), S((c[0] + f.mouth / 2, ye)), out, 6.0, fmt(f.mouth), 2.5)
        if out == "down":       # the view's title goes under the mouth's dimension
            vd.title_drop = max(getattr(vd, "title_drop", 0.0), 12.0)
        sh.dim_linear(S((c[0] - f.r, c[1])), S((c[0] + f.r, c[1])), inn, f.r * vd.scale + 5.0, fmt(f.width), 2.5)
        right = bx[2]
        if f.taper > 1e-3:
            p1, p2 = S((c[0] + f.mouth / 2, ye)), S((c[0] + f.r, yt))
            sh.dim_linear(p1, p2, "right", right - max(p1[0], p2[0]) + 6.0, fmt(f.taper), 2.5)
        p1, p2 = S((c[0] + f.mouth / 2, ye)), S((c[0] + f.r, c[1]))
        sh.dim_linear(p1, p2, "right", right - max(p1[0], p2[0]) + 14.0, fmt(f.edge), 2.5)
        rt = "R%s" % fmt(f.r)
        pick = None
        for lead in (7.0, 10.0, 14.0, 19.0):
            for deg in (135, 45, 160, 20, 110, 70):
                ux, uy = math.cos(math.radians(deg)), -sg * math.sin(math.radians(deg))   # round the closed end
                arc = S((c[0] + f.r * ux, c[1] + f.r * uy))
                tail = (arc[0] + ux * lead, arc[1] + uy * lead)
                an = "right" if ux < 0 else "left"
                ty = tail[1] - (0.0 if uy > 0 else 2.5)
                box = sh.text_box(tail[0] + (-0.8 if ux < 0 else 0.8), ty, rt, 2.5, an)
                if sh.is_free(box) and not any(sh._seg_box(tail, arc, b_, 0.3) for b_ in sh.boxes):
                    pick = (arc, tail, an, ty)
                    break
            if pick:
                break
        if pick is None:
            raise NotDrawable("%s: no clear place for %s's radius" % (ft.body.name, ft.tag))
        arc, tail, an, ty = pick
        sh.line(tail, arc, 0.25)
        sh.arrow(arc, (arc[0] - tail[0], arc[1] - tail[1]), 2.2, 0.9)
        sh.text(tail[0] + (-0.8 if an == "right" else 0.8), ty, rt, 2.5, an)
        # what the view prints, for the read-back
        ft.dims = {"box": bx, "texts": dict({"width": fmt(f.width), "mouth": fmt(f.mouth), "edge": fmt(f.edge),
                                             "r": rt}, **({"taper": fmt(f.taper)} if f.taper > 1e-3 else {}))}
    else:
        raise NotDrawable("%s: an open slot that opens across the view (%s) isn't dimensioned yet" % (
            ft.body.name, ft.tag))


def notch_window(vd, notches, small=8.0):
    """(window, notches, the one drawn) for the notches this view looks at from outside their wall. Notches at a
    member's two ends that are alike (same width, length, wall and place across) are sized once, on the one at
    the end drawn right (or up), and the drawing says the other end is the same; any other mix isn't drawn yet.
    The window, round the drawn one when it is under `small` mm on paper: from past the end to past its back face,
    across the member's whole profile, so its width, its place across and its length can be sized enlarged."""
    mine = [nt for nt in notches if vdot(vd.view.n, nt.wall_n) > 1 - 1e-6]
    if not mine:
        return None, [], None
    by_body = {}
    for nt in mine:
        by_body.setdefault(id(nt.body), []).append(nt)
    if len(by_body) > 1 or len(mine) > 2:
        raise NotDrawable("%s: more than one notch per end in one view isn't drawn yet" % mine[0].body.name)
    if len(mine) == 2:
        a, b = mine
        if a.sgn == b.sgn or abs(a.width - b.width) > 1e-3 or abs(a.length - b.length) > 1e-3 or \
                abs(a.lo - b.lo) > 1e-3 or abs(a.t - b.t) > 1e-3 or vdot(a.wall_n, b.wall_n) < 1 - 1e-9:
            raise NotDrawable("%s: the notches at its two ends differ: one detail for each isn't drawn yet" % (
                a.body.name))
    v = vd.view

    def where(nt):
        q = v.to2d(vmul(nt.lax, nt.end_s))
        return q[0] + q[1]
    shown = max(mine, key=where)
    if min(shown.width, shown.length) * vd.scale >= small:
        return None, mine, shown
    plo, phi = shown.prof
    g = shown.sgn
    pts = [v.to2d(shown.point(shown.end_s + g * 4.0, plo - 4.0)), v.to2d(shown.point(shown.end_s + g * 4.0, phi + 4.0)),
           v.to2d(shown.point(shown.s_back - g * 10.0, plo - 4.0)), v.to2d(shown.point(shown.s_back - g * 10.0, phi + 4.0))]
    return (min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts)), mine, shown


def open_slot_window(vd, feats, small=5.0):
    """A window round an open slot narrower than `small` mm on paper: the part's width across it, from the edge
    it opens on to past its round end, so its sizes can be dimensioned enlarged."""
    for ft in feats:
        if ft.kind != "open_slot" or not _end_on(ft, vd.view) or ft.f.width * vd.scale >= small:
            continue
        c = vd.view.to2d(ft.f.entry)
        a = vd.view.to2d(ft.f.along)
        e = vd.extent
        if abs(abs(a[1]) - 1) < 1e-6:           # opens up or down the view
            ys = (c[1] - a[1] * (ft.f.r + 8.0), c[1] + a[1] * (ft.f.edge + 2.0))
            return (e[0] - 2.0, e[2] + 2.0, min(ys), max(ys))
        if abs(abs(a[0]) - 1) < 1e-6:           # opens left or right
            xs = (c[0] - a[0] * (ft.f.r + 8.0), c[0] + a[0] * (ft.f.edge + 2.0))
            return (min(xs), max(xs), e[1] - 2.0, e[3] + 2.0)
    return None


def crowded_window(vd, feats, part, near=7.0, reach=25.0):
    """A window (x0, x1, y0, y1 in view mm) round tags that crowd: two tagged features closer than `near` mm on
    paper, with every tagged feature within `reach` mm of them, the part's end when it is that close too, and the
    view's full height. None when nothing crowds."""
    s = vd.scale
    # one item per place: a far-wall twin shares its hole's tag (H05/H10), it doesn't crowd it
    pts = list({(round(p[0], 2), round(p[1], 2)): p for p in
                (vd.view.to2d(ft.f.entry) for ft in feats if _end_on(ft, vd.view))}.values())
    pair = None
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if math.dist(a, b) * s < near and (pair is None or math.dist(a, b) < math.dist(*pair)):
                pair = (a, b)
    if pair is None:
        return None
    cx = (pair[0][0] + pair[1][0]) / 2
    xs = [p[0] for p in pts if abs(p[0] - cx) * s <= reach]
    if len(xs) < 2:
        return None
    e = vd.extent
    x0, x1 = min(xs) - 6.0 / s, max(xs) + 6.0 / s
    if (x0 - e[0]) * s < 15.0:
        x0 = e[0] - 2.0
    if (e[2] - x1) * s < 15.0:
        x1 = e[2] + 2.0
    x0, x1 = max(x0, e[0] - 2.0), min(x1, e[2] + 2.0)
    if (x1 - x0) * s > 60.0 or (e[3] - e[1]) * s > 60.0:
        return None         # not a small region: a detail would only repeat the view
    return (x0, x1, e[1] - 2.0, e[3] + 2.0)


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

def dir_words(d):
    """'+X' for an axis, else the unit vector to 3 decimals."""
    return axis_name(d) or "(%s)" % ", ".join("%.3f" % (0.0 if abs(c) < 5e-4 else c) for c in d)


def mapping_words(view, pod_system):
    sysname = "pod" if pod_system else "part"
    if view.looking:
        look = project.LOOK_WORDS.get(view.looking, view.looking)
    else:
        look = "square to the angled face, along %s" % dir_words(vmul(view.n, -1.0))
    return "X = %s, Y = %s (%s axes); looking %s" % (dir_words(view.x), dir_words(view.y), sysname, look)


def feature_text(ft):
    rivet = getattr(ft, "rivet", None)
    if not ft.reg:
        return ("rivet hole: %s" % rivet) if rivet else ""
    pns = []
    for p in inputs.part_numbers_in(ft.reg["mating"]):
        if p not in pns:
            pns.append(p)
    t = "%s %s" % (ft.reg["id"], inputs.short_function(ft.reg["function"]))
    if pns:
        t += " (%s)" % ", ".join(pns[:3])
    if rivet:
        t += "; rivet hole: %s" % rivet
    return t


def face_title(part, g):
    ft = g.feats[0]
    bodies = sorted({f.body.name for f in g.feats if f.body.name})
    fw = FACE_WORDS.get(axis_name(g.normal), "face" if axis_name(g.normal) else "angled face")
    side = ""
    if part.pod_system and axis_name(g.normal):
        # the side of the pod the face looks to: the room side when it faces the pod's centre line
        c = ft.f.entry
        k = [i for i in range(3) if abs(g.normal[i]) > 0.5][0]
        thin = min(range(3), key=lambda i: part.size[i])
        if k == thin and k < 2 and c[k] * g.normal[k] < 0:
            side = ", room side"
    inner = " (inside the member's bay)" if getattr(g, "blocked", False) else ""
    return "%s, %s%s%s" % (" + ".join(bodies) or part.name, fw, side, inner)


def annotate(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today):
    """Lines first (cutting planes, reference arrows, dimensions), then what can move (hole callouts, view titles,
    centre marks with their tags, origin names, datums), each put where it touches no line and no other text."""
    P = pl.principal
    O = dat["O"]
    pvd = vds["principal"]
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
        if not getattr(vd, "letter", None) or nm in pl.aux:
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
    # ---- removed sections: the hole axis and the profile size (each wall's hole is sized after, clear of these)
    for vd in removed:
        r = vd.r
        if getattr(vd, "profile", None):
            profile_dims(sh, vd)
            continue
        c = vd.S(vd.view.to2d(r.point))
        x0, y0, x1, y1 = vd.box()
        sh.centre_line((c[0], y0 - 4), (c[0], y1 + 4))
        bottom_used = any(vd.S(vd.view.to2d(ft.f.entry))[1] <= c[1] for ft in r.feats)
        w, h = (x1 - x0) / vd.scale, (y1 - y0) / vd.scale
        sh.dim_linear((x0, y0), (x1, y0), "down", 14.0 if bottom_used else 6.0, fmt(w), 2.5)
        sh.dim_linear((x0, y0), (x0, y1), "left", 6.0, fmt(h), 2.5)
    # ---- overall dimensions on the principal (true sizes of the part's box in that view)
    e = pvd.extent
    a, b = pvd.S((e[0], e[1])), pvd.S((e[2], e[3]))
    sh.dim_linear((a[0], a[1]), (b[0], a[1]), "down", 15.0, fmt(e[2] - e[0]), 3.0)
    sh.dim_linear((a[0], a[1]), (a[0], b[1]), "left", 15.0, fmt(e[3] - e[1]), 3.0)
    # an end cut at an angle (a mitre): in the plain view where its face shows edge on, the angle from square and
    # the true lengths along the member's two faces (guideline 6.1: true lengths and angle, not a box)
    angle_texts = []
    # a bent part's cut edges (its corner reliefs' 45° ends) come from its flat pattern, which the DXF defines
    for b in ([] if getattr(part, "flat", None) else part.bodies):
        lk = max(range(3), key=lambda i: b.size[i])
        lax = geom.member_axis(b) or tuple(1.0 if i == lk else 0.0 for i in range(3))
        top_corners = {}        # view -> (view, extent, the mitre corners on its top edge)
        for n, off, area, face in geom.planes(b):
            c = abs(vdot(n, lax))
            if not (0.02 < c < 0.9998):
                continue
            if any(face.IsSame(cf) for ch in part.chamfers for cf in ch.faces):
                continue            # an edge break, called out on its own (below)
            ang = math.degrees(math.acos(c))
            views_m = [(("detail-" + dv.letter), dv) for dv in getattr(pl, "details", [])] + list(vds.items())
            for nm, vd in views_m:
                if abs(vdot(n, vd.view.n)) > 1e-6 or abs(vdot(lax, vd.view.n)) > 1e-6:
                    continue
                # the face's two ends along the line it shows as
                pts = [vd.view.to2d(geom.pnt(BRep_Tool.Pnt_s(TopoDS.Vertex_s(v)))) for v in _vertices(face)]
                if len(pts) < 2:
                    continue
                if getattr(vd, "window", None):
                    wx0, wx1, wy0, wy1 = vd.window
                    if not all(wx0 - 1e-6 <= q[0] <= wx1 + 1e-6 for q in pts):
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
                # the arc 4 past the cut's edge, at most 22 on paper: a long shallow cut (FRONT's 352204, 75.39° over
                # about 80 at 1:1) would swing its arc into the border; a short one keeps its arc past the edge, the edge
                # extended to meet it
                dist = math.dist(S(far), S(near))
                R = min(dist + 4.0, 22.0)
                L = R + 2.0
                towards = 1 if (near[1 - ax_k] - far[1 - ax_k]) > 0 else -1
                ref_end = (S(far)[0] + sq[0] * towards * L, S(far)[1] + sq[1] * towards * L)
                sh.line(S(far), ref_end, W_THIN)
                d_m = (S(near)[0] - S(far)[0], S(near)[1] - S(far)[1])
                lm = math.hypot(*d_m)
                ext_end = (S(far)[0] + d_m[0] / lm * L, S(far)[1] + d_m[1] / lm * L)
                if L > dist + 0.5:
                    sh.line(S(near), ext_end, W_THIN)
                a0 = math.atan2(ref_end[1] - S(far)[1], ref_end[0] - S(far)[0])
                a1 = math.atan2(d_m[1], d_m[0])
                lo, hi = (a0, a1) if ((a1 - a0) % (2 * math.pi)) < math.pi else (a1, a0)
                if hi < lo:
                    hi += 2 * math.pi
                sh.arc(S(far), R, lo, hi, W_THIN)
                am = (lo + hi) / 2
                # the value by the arc's middle, out along it until it touches no line (a narrow angle puts its own
                # lines across a value written right at the arc)
                ang_t = "%s°" % fmt(ang)
                cands = []
                for d_ in (1.5, 3.0, 5.0, 8.0, 12.0):
                    px, py = S(far)[0] + (R + d_) * math.cos(am), S(far)[1] + (R + d_) * math.sin(am)
                    cands += [(px, py, "left" if math.cos(am) >= 0 else "right"), (px, py, "center")]
                # where none of those is clear: along the arc toward either end, farther out, either anchor (FRONT's
                # 352204: its 22.45° at the arc's middle sat on the top length's extension line)
                for d_ in (1.5, 3.0, 5.0, 8.0, 12.0, 17.0):
                    for fr_ in (0.5, 0.3, 0.7, 0.15, 0.85):
                        a_ = lo + fr_ * (hi - lo)
                        px, py = S(far)[0] + (R + d_) * math.cos(a_), S(far)[1] + (R + d_) * math.sin(a_)
                        nat = "left" if math.cos(a_) >= 0 else "right"
                        cands += [(px, py, nat), (px, py, "center"), (px, py, "right" if nat == "left" else "left")]
                # placed after every length dimension of the mitre (below), so their extension lines are known
                # (BASE's D-129 111101: the value sat on the 1502.07 dimension's extension line)
                angle_texts.append((ang_t, cands))
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
                            top_corners.setdefault(id(vd2), (vd2, e2, []))[2].append(q2[0])
                            break
                vd.has_mitre = True
                break
        # the top face's true length: from the square end to its mitre corner, or, mitred at both ends, between
        # its two corners, once (FRONT's 352201: two lengths from each end printed over each other)
        for vd2, e2, xs in top_corners.values():
            xs = sorted(set(round(x_, 4) for x_ in xs))
            if len(xs) == 1:
                oth = e2[0] if abs(xs[0] - e2[0]) > abs(xs[0] - e2[2]) else e2[2]
                a_, b_ = oth, xs[0]
            else:
                a_, b_ = xs[0], xs[-1]
            if abs(abs(b_ - a_) - (e2[2] - e2[0])) < 0.005:
                continue            # the overall length already (FRONT's 352203: 1694.75 printed twice)
            sh.dim_linear(vd2.S((a_, e2[3])), vd2.S((b_, e2[3])), "up", 11.0, fmt(abs(b_ - a_)), 2.5)
            vd2.top_used = 16.0
    pl.angle_marks = []
    for ang_t, cands in angle_texts:
        pick = next((c_ for c_ in cands if sh.is_free(sh.text_box(c_[0], c_[1], ang_t, 2.5, c_[2], valign="mid"))),
                    cands[0])
        sh.text(pick[0], pick[1], ang_t, 2.5, pick[2], valign="mid")
        pl.angle_marks.append({"text": ang_t, "box": sh.text_box(pick[0], pick[1], ang_t, 2.5, pick[2], valign="mid")})
    # angled-face and end views (ISO 128-30): an arrow square to the face, in a drawn view that shows the face edge
    # on, its tip just off the face by the features (else moved along the face, or shorter) where the arrow crosses
    # no line and its letter touches nothing; drawn after every dimension so those are known (BASE's D-129 111103: the
    # end view's letter sat on the 100 height dimension)
    def aux_arrows():
        for nm in sorted(pl.aux):
            avd = vds.get(nm)
            if avd is None:
                continue
            n3 = avd.view.n
            hosts = [vds[h] for h in ("principal", "above", "below", "from_left", "from_right", "rear")
                     if h in vds and abs(vdot(n3, vds[h].view.n)) < 1e-6]
            if not hosts:
                raise NotDrawable("%s: no view shows the angled face edge on, for view %s's arrow" % (
                    part.pn, avd.letter))
            hv = hosts[0]
            feats = [ft for g in pl.groups if g.view == nm for ft in g.feats]
            c3 = tuple(sum(ft.f.entry[i] for ft in feats) / len(feats) for i in range(3))
            c2 = hv.S(hv.view.to2d(c3))
            u = hv.view.to2d(n3)
            L = math.hypot(*u)
            u = (u[0] / L, u[1] / L)
            side = (-u[1], u[0])
            hb = hv.box()
            reach = 0.4 * abs(side[0] * (hb[2] - hb[0]) + side[1] * (hb[3] - hb[1]))
            pick = None
            for sh_ in [0.0] + [k * d_ for d_ in (5.0, 10.0, 15.0) for k in (1, -1)]:
                if abs(sh_) > reach + 1e-9 and sh_:
                    continue
                c_ = (c2[0] + side[0] * sh_, c2[1] + side[1] * sh_)
                for t0, ln in ((3.0, 12.0), (2.0, 8.0)):
                    tip = (c_[0] + u[0] * t0, c_[1] + u[1] * t0)
                    tail = (c_[0] + u[0] * (t0 + ln), c_[1] + u[1] * (t0 + ln))
                    if not sh.seg_free(tail, tip):
                        continue
                    cands = [(tail[0] + u[0] * 2.0 + sd * side[0] * 2.5, tail[1] + u[1] * 2.0 + sd * side[1] * 2.5 - 1.75)
                             for sd in (0, 1, -1, 2, -2)]
                    q = next((q for q in cands
                              if sh.is_free(sh.text_box(q[0], q[1], avd.letter, 3.5, "center", bold=True))), None)
                    if q is not None:
                        pick = (tip, tail, q)
                        break
                if pick:
                    break
            if pick is None:
                tip = (c2[0] + u[0] * 3.0, c2[1] + u[1] * 3.0)
                tail = (c2[0] + u[0] * 15.0, c2[1] + u[1] * 15.0)
                pick = (tip, tail, (tail[0] + u[0] * 2.0, tail[1] + u[1] * 2.0 - 1.75))
            tip, tail, q = pick
            sh.line(tail, tip, 0.35)
            sh.arrow(tip, (-u[0], -u[1]), 3.0, 1.1)
            sh.text(q[0], q[1], avd.letter, 3.5, "center", bold=True)
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
        # values written up their extension lines; one closer than a letter's height to the last is jogged sideways
        # (ISO 129-1 ordinate dimensions)
        items = sorted([(x_front, "0")] + [(x, fmt(v)) for x, v in marks], key=lambda t: t[0])
        if end != e0[0]:
            items = items[::-1]
        last = None
        for x, txt in items:
            lx = x
            if last is not None and abs(lx - last) < 5.0:
                lx = last + (5.0 if end == e0[0] else -5.0)
            sh.line((x, top + 1.0), (x, level - 1.0), W_THIN)
            sh.line((x, level - 1.0), (lx, level + 1.5), W_THIN)
            sh.text(lx + 1.25, level + 2.0, txt, 2.5, "left", rotate=90)
            last = lx
        lab = "STILE CENTRE LINES FROM THE FRONT END"
        ymax = level + 2.0 + max(sh.text_width(fmt(v), 2.5) for _x, v in marks) + 3.0
        if end == e0[0]:
            sh.text(x_front, ymax, lab, 2.5, "left")
        else:
            sh.text(x_front, ymax, lab, 2.5, "right")
    # the spigot hole and slot from the frame's end faces (joints register R-J13: 100 from each end)
    bview = dat["B"].group.view if dat.get("B") else None
    if dat.get("B") and bview in vds:
        vd = vds[bview]
        ve = vd.extent
        for f in [x for x in (dat["B"], dat.get("slot")) if x is not None]:
            c = vd.view.to2d(f.f.entry)
            end_x = ve[0] if abs(c[0] - ve[0]) < abs(c[0] - ve[2]) else ve[2]
            p1 = vd.S((end_x, ve[3]))
            p2 = vd.S((c[0], ve[3]))
            sh.dim_linear(p1, p2, "up", 7.0, fmt(abs(c[0] - end_x)), 2.5)
    # open-ended slots (D-129's hook-in end caps; the PM's ruling): dimensioned from the edge they open on, in the
    # detail that enlarges them (else their view): the mouth, the taper's length, the end's centre from the edge,
    # the width and the end's radius
    for ft in part.features:
        if ft.kind != "open_slot" or ft.group is None or not ft.group.view:
            continue
        vd = vds.get(ft.group.view)
        if vd is None:
            continue
        dv = getattr(vd, "detail", None)
        if dv is not None:
            c0 = vd.view.to2d(ft.f.entry)
            wx0, wx1, wy0, wy1 = dv.window
            if wx0 <= c0[0] <= wx1 and wy0 <= c0[1] <= wy1:
                vd = dv
        open_slot_dims(sh, vd, ft)
    # notches (BASE's FB-15): sized in the detail that enlarges them (else their view)
    for nm, (nts, shown, enlarged) in getattr(pl, "notch_views", {}).items():
        vd = vds[nm].detail if enlarged else vds[nm]
        shown.drawn = {"view": vd, "texts": notch_dims(sh, vd, shown), "alike": [nt for nt in nts if nt is not shown]}
    for fv in getattr(pl, "flats", []):
        flat_dims(sh, part, fv)
    sh.flush()
    aux_arrows()
    chamfer_callouts(sh, part, pl, vds, removed)
    sh.flush()
    # ---- removed sections: each wall's hole sized across its gap, on the outside of that wall (ISO 129-1), with
    # its tag; the words slide out along the line past anything they would touch
    for vd in removed:
        r = vd.r
        c = vd.S(vd.view.to2d(r.point))
        for ft in r.feats:
            wall_out = vd.S(vd.view.to2d(ft.f.entry))[1]
            top_wall = wall_out > c[1]
            pa = (c[0] - ft.f.dia / 2 * vd.scale, wall_out)
            pb = (c[0] + ft.f.dia / 2 * vd.scale, wall_out)
            sh.dim_linear(pa, pb, "up" if top_wall else "down", 5.0,
                          "%s  Ø%s THRU 1 WALL" % (ft.tag, fmt(ft.f.dia)), 2.5, slide=True)
    # ---- view titles
    def title(vd, head, sub, extra=None):
        """The view's name and scale, and under it its X/Y mapping (and any extra line), centred under the view;
        where that would touch a line or a text (or the view is narrower than its title), the first clear of: from
        the view's left edge with the mapping in short lines, the same with the name in two or three lines, the same
        from its right edge, centred in short lines."""
        x0, y0, x1, y1 = vd.box()
        cx = (x0 + x1) / 2
        y = y0 - (28.0 if vd is pvd else 10.0) - getattr(vd, "title_drop", 0.0)
        name, _sp, sc = head.rpartition("  ")
        if not name:
            name, sc = head, ""

        def wrapped(limit):
            lines, cur = [], ""
            for wd in name.split(" "):
                t = (cur + " " + wd).strip()
                if cur and sh.text_width(t, 3.5, True) > limit:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = t
            lines.append(cur)
            if sc:
                if sh.text_width(lines[-1] + "  " + sc, 3.5, True) <= limit:
                    lines[-1] += "  " + sc
                else:
                    lines.append(sc)
            return lines

        def lay(xa, an, heads, parts, gap=3.4):
            out, yy = [], y
            for i, h_ in enumerate(heads):
                if i:
                    yy -= 4.6
                out.append((xa, yy, h_, 3.5, an, True))
            yy -= 4.2
            for p_ in parts:
                out.append((xa, yy, p_, 2.5, an, False))
                yy -= gap
            return out
        whole = [sub] + ([extra] if extra else [])
        short = sub.split("; ") + (extra.split("; ") if extra else [])
        # the name in as few lines as are clear: wider limits first
        heads = []
        for lim in (50.0, 40.0, 30.0):
            w_ = wrapped(lim)
            if len(w_) > 1 and w_ not in heads:
                heads.append(w_)
        lays = []
        if x1 - x0 >= max([sh.text_width(head, 3.5, True)] + [sh.text_width(t, 2.5) for t in whole]) + 4:
            lays.append(lay(cx, "center", [head], whole, 3.7))
        for xa, an in ((x0 - 2.0, "left"), (x1 + 2.0, "right")):
            lays += [lay(xa, an, [head], short)] + [lay(xa, an, h_, short) for h_ in heads]
        lays += [lay(cx, "center", h_, short) for h_ in heads]
        pick = next((L_ for L_ in lays if all(sh.is_free(sh.text_box(xa, yy, t, sz, an, bold=b))
                                              for xa, yy, t, sz, an, b in L_)), lays[0])
        for xa, yy, t, sz, an, b in pick:
            sh.text(xa, yy, t, sz, an, bold=b)
    sname = scale_text(scale)
    osfx = (lambda vd: "; origin %s%s" % (vd.origin_name, (" " + vd.origin_words) if getattr(vd, "origin_words", "")
                                           else "")) if part.features else (lambda vd: "")
    for nm, vd in vds.items():
        head = "%s  %s" % (VIEW_WORDS.get(nm, "VIEW"), sname)
        if getattr(vd, "letter", None):
            head = "VIEW %s  %s" % (vd.letter, scale_text(vd.scale) if nm in pl.aux else sname)
        title(vd, head, mapping_words(vd.view, part.pod_system) + osfx(vd))
    for vd in secs:
        title(vd, "SECTION %s-%s  %s" % (vd.letter, vd.letter, sname),
              mapping_words(vd.view, part.pod_system) + osfx(vd))
    for dv in getattr(pl, "details", []):
        nv = getattr(pl, "notch_views", {}).get(dv.parent_name)
        where = ""
        if nv and nv[2]:
            shown = nv[1]
            where = ", at the %s end" % (axis_name(vmul(shown.lax, shown.sgn)) or "drawn")
            if shown.drawn["alike"]:
                where += " (the notch at the %s end is the same)" % (
                    axis_name(vmul(shown.lax, -shown.sgn)) or "other")
        title(dv, "DETAIL %s  %s" % (dv.letter, scale_text(dv.scale)),
              "of the %s%s; %s; origin %s" % (VIEW_WORDS.get(dv.parent_name, "view").lower(), where,
                                              mapping_words(dv.view, part.pod_system), dv.origin_name))
    for fv in getattr(pl, "flats", []):
        fv.title_drop = 14.0
        title(fv, "FLAT PATTERN  %s" % scale_text(fv.scale),
              "from %s, as its x and y draw it: the side it shows faces you; bend lines thin chain, B1 to B%d" % (
                  os.path.basename(part.flat.path), len(part.flat.rows)),
              extra="UP: the flange folds toward you")
    for vd in removed:
        tags = sorted({f.tag for s_ in vd.r.all for f in s_})
        vd.title_drop = 14.0
        if getattr(vd, "profile", None):
            pr = vd.profile
            words = "across the bends, at the middle" + (
                "; one end, the other end the same" if pr["window"] else "") + (
                "; typical at every side" if getattr(vd, "typical", False) else "")
            title(vd, "SECTION %s-%s  %s" % (vd.letter, vd.letter, scale_text(vd.scale)), words,
                  extra=mapping_words(vd.view, part.pod_system))
            continue
        title(vd, "SECTION %s-%s  %s" % (vd.letter, vd.letter, scale_text(vd.scale)),
              ("through %s (typical: %s)" % ("/".join(sorted(f.tag for f in vd.r.feats)), ", ".join(tags)))
              if vd.r.feats else ("across %s, showing its bevel along it" % (vd.r.body.name or "the member"))
              if getattr(vd.r, "bevel", None) else "across the middle, showing the thickness",
              extra=mapping_words(vd.view, part.pod_system))
    sh.flush()
    # ---- centre marks, origins and tags (draw's place_marks), clear of everything above
    pl.place_marks()
    # ---- datums, each where its symbol touches no text and its frame no line: short leaders first
    def put_datum(cands, letter):
        pick = next((c_ for c_ in cands if sh.datum_free(c_[0], c_[1], leader=c_[2])), cands[0])
        sh.datum(pick[0], pick[1], letter, leader=pick[2])
    if dat.get("B"):
        Bf = dat["B"]
        cn, cp = dat["C_plane"]
        bview = None
        for nm, vd in vds.items():
            if nm == Bf.group.view and _end_on(Bf, vd.view):
                bview = nm
                cb = vd.S(vd.view.to2d(Bf.f.entry))
                rb = Bf.f.dia / 2 * vd.scale
                put_datum([((cb[0] + sx * rb * 0.7, cb[1] + sy * rb * 0.7), (0.6 * sx, 1.0 * sy), lead)
                           for lead in (7.0, 10.0, 13.0) for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1))], "B")

        # C on the face that stops the turn about B, on an edge-on view of it: B's view first, then the others,
        # short leaders before long ones; along the edge where it is farthest from the tagged holes
        def c_cands(nm, vd, leads):
            n2 = vd.view.to2d(cn)
            if abs(vdot(cn, vd.view.n)) > 1e-6 or abs(n2[1]) <= 0.5:
                return []
            yy = vd.view.to2d(tuple(cp if abs(cn[i]) > 0.5 else 0.0 for i in range(3)))[1]
            e = vd.extent
            xs = [vd.view.to2d(ft.f.entry)[0] for g in pl.groups if g.view == nm for ft in g.feats]
            if n2[1] < 0:       # pointing down into the view's title: keep to the ends, past the title
                ts = (0.06, 0.12, 0.88, 0.94)
            else:               # clear of the middle, where a length dimension's text sits
                ts = (0.2, 0.28, 0.36, 0.64, 0.72, 0.8)
            xc = sorted([e[0] + t * (e[2] - e[0]) for t in ts], key=lambda x: -min([abs(x - h) for h in xs] or [1e9]))
            return [(vd.S((x, yy)), (0, n2[1]), lead) for lead in leads for x in xc]
        names = ([bview] if bview else []) + [n_ for n_ in vds if n_ != bview]
        cands = [c_ for leads in ((7.0, 10.0), (14.0, 18.0, 22.0)) for n_ in names for c_ in c_cands(n_, vds[n_], leads)]
        if cands:
            put_datum(cands, "C")
        # A: the seat face, on the principal view's edge
        x0, y0, x1, y1 = pvd.box()
        n2 = P.to2d(dat["A_normal"])
        if abs(n2[1]) > 0.5:
            yA = pvd.S((0, P.to2d(O)[1]))[1]
            put_datum([((x0 + t * (x1 - x0), yA), (0, n2[1]), lead) for lead in (7.0, 10.0, 14.0)
                       for t in (0.18, 0.1, 0.26, 0.34, 0.66, 0.74, 0.82, 0.9)], "A")
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
                    yy = vd.view.to2d(tuple(plane if i == k else 0.0 for i in range(3)))[1]
                    xs = [e[0] + t * (e[2] - e[0]) + 8 * (ord(letter) - 65) for t in (0.30, 0.2, 0.4, 0.6, 0.7, 0.8)]
                    put_datum([(vd.S((x, yy)), (0, n2[1]), lead) for lead in (7.0, 10.0, 14.0) for x in xs], letter)
                else:
                    xx = vd.view.to2d(tuple(plane if i == k else 0.0 for i in range(3)))[0]
                    ys = [e[1] + t * (e[3] - e[1]) for t in (0.25, 0.4, 0.6, 0.75)]
                    put_datum([(vd.S((xx, y_)), (n2[0], 0), lead) for lead in (7.0, 10.0, 14.0) for y_ in ys], letter)
                break
    # ---- keys fitted in the part's ends (Joints' corner-keys.csv): a note at each end saying which way round the
    # key goes, since its bottom holes sit off its middle and meet the part's only one way (the Lead's ask on #228)
    if spec.get("key_notes"):
        key_notes(sh, part, pl, vds)
    sh.flush()
    return


def key_notes(sh, part, pl, vds):
    """For each key in the part's ends: a leader to the key's stud face on the end, in the view (or its detail)
    that shows the part's holes for the key's screws, and a note: which key, which face goes on this end, and
    that only this way round do its bottom holes meet the part's (and how far off they are turned round). When the
    part's STEP has no holes where Joints' file puts the key's screws (the two teams' files between changes, D-129),
    the end gets a HOLD note naming those positions instead, and the read-back checks that the holes really are
    missing; regenerating once the STEP has them gives the full note."""
    for r in inputs.key_rows(part.pn):
        fc = (float(r["face_centre_x"]), float(r["face_centre_y"]))
        bk = (float(r["key_back_centre_x"]), float(r["key_back_centre_y"]))
        hs = [(float(r["fix_hole_1_x"]), float(r["fix_hole_1_y"])), (float(r["fix_hole_2_x"]), float(r["fix_hole_2_y"]))]
        L = math.dist(fc, bk)
        u = ((fc[0] - bk[0]) / L, (fc[1] - bk[1]) / L)
        mid = ((hs[0][0] + hs[1][0]) / 2, (hs[0][1] + hs[1][1]) / 2)
        d_hole = abs((mid[0] - bk[0]) * u[0] + (mid[1] - bk[1]) * u[1])
        fts = sorted([ft for ft in part.features if ft.tag and any(math.dist((ft.f.entry[0], ft.f.entry[1]), h) < 0.5
                                                                    for h in hs)], key=lambda f: f.tag)
        hold = len(fts) != 2
        if hold:
            # the view that looks at the key's bottom (its screws go up through the part's bottom wall)
            vd = next((v_ for v_ in vds.values() if abs(v_.view.n[2]) > 0.99), None)
        else:
            vd = vds.get(fts[0].group.view) if fts[0].group.view else None
        if vd is None:
            continue
        z = (float(r["key_bottom_z"]) + float(r["key_top_z"])) / 2
        c2 = vd.view.to2d((fc[0], fc[1], z))
        dv = getattr(vd, "detail", None)
        if dv is not None:
            x0, x1, y0, y1 = dv.window
            if x0 - 1e-6 <= c2[0] <= x1 + 1e-6 and y0 - 1e-6 <= c2[1] <= y1 + 1e-6:
                vd = dv
        a = vd.S(c2)
        cut = abs(float(r["cut_deg_signed"] or 0))
        if hold:
            text = ("HOLD: Joints' key file puts key %s, %s, in this end, its screws at X %s Y %s and X %s Y %s (pod), "
                    "but this STEP has no holes there yet; the key note follows when the model has them." % (
                        r["part_number"], r["joint"], fmt(hs[0][0]), fmt(hs[0][1]), fmt(hs[1][0]), fmt(hs[1][1])))
        else:
            text = None
        # where the stud face sits: on the part's end (its normal along the part) or against its inner wall (across)
        k = max(range(2), key=lambda i: part.size[i])
        sn = (float(r["stud_normal_x"]), float(r["stud_normal_y"]))
        on_end = abs(sn[k]) / (math.hypot(*sn) or 1.0) > 0.7
        text = text or ("Key %s, %s, fitted at the factory (J-BASE-02): stud face%s %s, back face %s mm "
                "inside. Only this way round do its bottom holes meet %s; turned round they are %s mm off (Joints' "
                "key sheet 111211)." % (r["part_number"], r["joint"], (" (cut %s°)" % fmt(cut)) if cut > 0.01 else "",
                                        "flush with this end" if on_end else "against the inner wall",
                                        fmt(L), " and ".join(f.tag for f in fts), fmt(abs(L - 2 * d_hole))))
        lines = sh.wrap(text, 2.5, 78.0)
        w = max(sh.text_width(t, 2.5) for t in lines)
        h = 2.5 + 3.6 * (len(lines) - 1)
        # the leader leaves the end face square to it, along the part (out of the key's stud face), for 6 mm, then
        # bends to the note: it never runs along the outline
        cd = vd.view.to2d((float(r["carrier_dir_x"]), float(r["carrier_dir_y"]), 0.0))
        n_ = math.hypot(*cd) or 1.0
        cd = (cd[0] / n_, cd[1] / n_)
        elbow = (a[0] + cd[0] * 6.0, a[1] + cd[1] * 6.0)
        base = math.degrees(math.atan2(cd[1], cd[0]))
        angles = [(base + d_) % 360 for d_ in (0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150, 180)]

        def block_at(px, py, ca, sa):
            left = px - w if ca < -1e-6 else (px - w / 2 if abs(ca) <= 1e-6 else px)
            top = py + h if sa > 1e-6 else (py + h / 2 if abs(sa) <= 1e-6 else py)
            return [(left, top - 2.5 - 3.6 * i, t) for i, t in enumerate(lines)]

        def crosses_text(p0, p1):
            return any(sh._seg_box(p0, p1, b_, 0.3) for b_ in sh.boxes)
        pick = None
        if not crosses_text(a, elbow):
            for rad in (4.0, 8.0, 14.0, 22.0, 32.0, 44.0, 58.0):
                for ang in angles:
                    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                    ca, sa = (0.0 if abs(ca) < 1e-6 else ca), (0.0 if abs(sa) < 1e-6 else sa)
                    att = (elbow[0] + rad * ca, elbow[1] + rad * sa)
                    blk = block_at(att[0], att[1], ca, sa)
                    if all(sh.is_free(sh.text_box(x_, y_, t, 2.5)) for x_, y_, t in blk) and not crosses_text(elbow, att):
                        pick = (att, blk)
                        break
                if pick:
                    break
        if pick is None:
            raise NotDrawable("%s: no clear place for the note on key %s (%s)" % (part.pn, r["part_number"], r["joint"]))
        att, blk = pick
        sh.line(att, elbow, W_THIN)
        sh.line(elbow, a, W_THIN)
        sh.arrow(a, (-cd[0], -cd[1]), 2.2, 0.9)
        for x_, y_, t in blk:
            sh.text(x_, y_, t, 2.5)


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
TB_ROOM = 120.0     # the title block's height and the gap over it, which the right column's tables stay above


def table_name(g):
    """A hole table's title start: HOLES H01-H07, or HOLE H19 / SLOT H19 for a table of one."""
    if len(g.feats) == 1:
        return "%s %s" % ("HOLE" if g.feats[0].kind == "hole" else "SLOT", g.feats[0].tag)
    return "HOLES %s-%s" % (g.feats[0].tag, g.feats[-1].tag)


def hole_cols(tw):
    return [("TAG", 14, "c"), ("X (mm)", 24, "r"), ("Y (mm)", 24, "r"), ("SIZE", 40, "l"), ("DEPTH", 42, "l"),
            ("FEATURE (register) AND FITS", tw - 144, "l")]


def tables_height(sh, part, groups, tw):
    """The hole tables' height in the right column at width tw, as tables_and_text draws them (the numbers and the
    second title line at their longest)."""
    total = 0.0
    for g in groups:
        rows = [[ft.tag, "-0000.00", "-0000.00",
                 size_text(ft) + (" along X" if ft.kind == "slot" else " toward +X" if ft.kind == "keyhole" else ""),
                 wall_word(ft.f, ft.body), feature_text(ft)] for ft in g.feats]
        head = ["%s: %s" % (table_name(g), face_title(part, g)),
                "far wall, coaxial with H00-H00: hidden in the view from below, shown in section D-D, E-E; origin O0; "
                "+X right, +Y up; drilled from this face"]
        total += sh.table_height(hole_cols(tw), rows, size=2.5, title=head, title_size=2.5) + 5.0
    fl = getattr(part, "flat", None)
    if fl:      # the bend table under the hole tables
        cols = [("TAG", 14, "c"), ("L", 60, "l"), ("D", 24, "c"), ("A", 20, "r"), ("R", 30, "r"), ("B", tw - 148, "l")]
        rows = [["B00", "x 0000.00 from the lower edge", "DOWN", "180°", "R00.00", "0000.000"] for _r in fl.rows]
        total += sh.table_height(cols, rows, size=2.5, title=["BENDS", "UP: the flange folds toward the viewer of the "
                                                                   "flat pattern as drawn; K-factor 0.000, inside radius from its entry"],
                                 title_size=2.5) + 5.0
    return total


def tables_and_text(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today):
    """Sheet 1: member balloons on the principal view and one hole table per face in the right column."""
    W, H = sh.W, sh.H
    P = pl.principal
    O = dat["O"]
    pvd = vds["principal"]
    tw = getattr(pl, "table_w", spec.get("table_w", TABLE_W))
    right_x0 = W - 10 - tw - 4
    y = H - 10 - 6
    # ---- member balloons (frames): item numbers of the cut list on sheet 2. The usual place first; where its circle
    # would touch a line or a text, or its leader cross a text, the next of: other offsets, the other side, other
    # points along the member
    members = cut_list(part)
    pb = pvd.box()
    for m in members:
        for b in m["bodies"]:
            e = project.extent(project.project(b.shape, P))
            horiz = (e[2] - e[0]) > (e[3] - e[1])
            cands = []      # (anchor on the member, leader end, balloon centre)
            if horiz:
                for t in (0.62, 0.5, 0.75, 0.38, 0.85, 0.25):
                    anchor = pvd.S((e[0] + t * (e[2] - e[0]), (e[1] + e[3]) / 2))
                    sy = -1.0 if anchor[1] > (pb[1] + pb[3]) / 2 else 1.0
                    for dy in (14.0, 18.0, 10.0):
                        for sx in (1.0, -1.0):
                            end = (anchor[0] + sx * 7.0, anchor[1] + sy * dy)
                            cands.append((anchor, end, (end[0] + sx * 4.0, end[1])))
            else:
                for t in (0.55, 0.45, 0.65, 0.35, 0.75, 0.25):
                    anchor = pvd.S(((e[0] + e[2]) / 2, e[1] + t * (e[3] - e[1])))
                    inner = 1.0 if anchor[0] < (pb[0] + pb[2]) / 2 else -1.0
                    for sx in (1.0, -1.0) if inner > 0 else (1.0, -1.0):
                        for dx in (10.0, 14.0, 18.0):
                            for dy in (7.0, -7.0):
                                end = (anchor[0] + sx * dx, anchor[1] + dy)
                                cands.append((anchor, end, (end[0] + sx * 4.0, end[1])))

            def free(c_):
                anchor, end, cc = c_
                circ = (cc[0] - 4.0, cc[1] - 4.0, cc[0] + 4.0, cc[1] + 4.0)
                return sh.is_free(circ) and not any(sh._seg_box(anchor, end, b_, 0.3) for b_ in sh.boxes)
            anchor, end, cc = next((c_ for c_ in cands if free(c_)), cands[0])
            sh.circle(anchor, 0.6, 0.18, fill=(0, 0, 0))
            sh.line(anchor, end, 0.18)
            sh.circle(cc, 4.0, 0.25)
            sh.text(cc[0], cc[1], str(m["item"]), 3.5, "center", valign="mid", bold=True)
    sh.flush()
    # ---- hole tables, one per face
    cols = hole_cols(tw)
    for g in groups:
        vd = vds.get(g.view) if g.view else g.vd
        oname = vd.origin_name
        v = vd.view
        o2 = v.to2d(getattr(vd, "origin3d", None) or O)
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
            x, yv = (0.0 if abs(x) < 0.005 else x), (0.0 if abs(yv) < 0.005 else yv)       # never "-0.00"
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
        head = ["%s: %s" % (table_name(g), face_title(part, g)),
                "%s; origin %s; +X right, +Y up; drilled from this face" % (where, oname)]
        y = sh.table(right_x0, y, cols, rows, size=2.5, title=head, title_size=2.5) - 5.0
    fl = getattr(part, "flat", None)
    if fl:
        bcols = [("TAG", 14, "c"), ("LINE IN THE FLAT (mm)", 60, "l"), ("DIRECTION", 24, "c"), ("ANGLE", 20, "r"),
                 ("INSIDE RADIUS", 30, "r"), ("BEND ALLOWANCE (mm)", tw - 148, "l")]
        brows = []
        for row in fl.rows:
            ch, f = next((c, f) for c, m in zip(fl.chains, fl.matches) for f, ln in zip(c.folds, m["lines"])
                         if ln is row["line"])
            import sheetmetal
            brows.append([row["tag"], "%s %s from the %s edge" % ("x" if row["axis"] == "x" else "y", fmt(row["at"]),
                                                                    "left" if row["axis"] == "x" else "lower"),
                          row["dir"], "%s°" % fmt(row["angle"]), "R%s" % fmt(row["r"]),
                          fmt(sheetmetal.bend_allowance(f, row["r"], ch.t, fl.k), 3)])
        head = ["BENDS B1-B%d: %s; sheet %s thick" % (len(fl.rows), os.path.basename(fl.path), fmt(fl.chains[0].t)),
                "UP: the flange folds toward the viewer of the flat pattern as drawn; K-factor %s, inside radius from %s"
                % (fmt(fl.k, 3), fl.radius_from)]
        y = sh.table(right_x0, y, bcols, brows, size=2.5, title=head, title_size=2.5) - 5.0
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
                    title=["CUT LIST (parts list %s)" % os.path.basename(part.list_file or ""), mat], title_size=2.5)


def notes_list(part, spec, pl, vds, secs, removed, dat, groups):
    P = pl.principal
    notes = []
    notes.append("UNITS: mm. Do not scale the drawing. ISO first-angle projection (ISO 5456-2), symbol in the "
                 "title block. Dimensions to ISO 129-1. Sheet 1: views, sections and hole tables; %s: these "
                 "general notes%s." % ("sheet 2: the flat pattern; sheet 3" if spec.get("_flat_sheet") else "sheet 2",
                                       ", the cut list" if cut_list(part) else "") + "")
    if getattr(part, "qty_words", None):
        notes.append("QUANTITY: %s." % part.qty_words)
    vw = "the room side" if part.pod_system and pl.principal.pod_name in ("right", "front", "top") else "its side"
    notes.append("Views: the principal view looks %s (%s); every view's title gives its own X and Y and how they "
                 "map to the %s axes (conventions section 4). On every view X runs right and Y up." % (
                     project.LOOK_WORDS.get(P.looking, P.looking), mapping_words(P, part.pod_system),
                     "pod" if part.pod_system else "part"))
    if dat.get("B"):
        slot = (" (the spigot slot %s runs across the rail, R-J17, so it locates along the rail only)" %
                dat["slot"].tag) if dat.get("slot") else ""
        notes.append("Datums (ISO 5459): A = %s; B = axis of the spigot hole %s (joints register R-J6, R-J13); "
                     "C = %s%s. Origin O = datum B's axis on datum A; O1, O2... are O seen in each view. Hole "
                     "positions in the tables are theoretically exact from O." % (
                         dat["words"]["A"], dat["B"].tag, dat["words"]["C"], slot))
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
        hollow = any("1 WALL" in wall_word(ft.f, ft.body) for ft in part.features if ft.kind == "hole")
        notes.append("Holes go %s unless the table says otherwise; deburr both sides. %s" % (
            "THRU 1 WALL of the member" if hollow else "THRU the part",
            "Coaxial holes in two walls of one member are shown in section%s %s." % (
                "s" if len(two) > 1 else "", " and ".join("%s-%s" % (l, l) for l in two)) if two else ""))
    fl = getattr(part, "flat", None)
    if fl:
        import sheetmetal
        rad = "R%s from %s" % (fmt(fl.radius), fl.radius_from)
        notes.append("Bent from the flat pattern %s (sha256 %s): its CUT outline, its BEND lines the bend centre lines%s. "
                     "Sheet %s thick (the model). Inside radius %s; K-factor %s (calculation: the DXF's bend lines and "
                     "flat size against the "
                     "model's flanges at that radius, every bend within 0.05). Flange lengths are outside sizes, to "
                     "each fold's outside sharp; the bend table gives each bend's direction, angle and allowance." % (
                         inputs.rel(fl.path), inputs.sha12(fl.path),
                         ", its MARK lines the bend zones' edges" if fl.dxf.zone_lines() else "", fmt(fl.chains[0].t), rad,
                         fmt(fl.k, 3)))
    if spec.get("tolerance"):
        notes.append("TOLERANCES (PROPOSED until the shop confirms; not ISO 2768): " + spec["tolerance"])
    elif (part.row.get("tolerance") or "").strip():     # the entry gives none: its parts list's (Reviewer 12)
        notes.append("TOLERANCES (PROPOSED until the shop confirms; not ISO 2768): %s (its parts list)" %
                     part.row["tolerance"].strip())
    src = "Source: %s (sha256 %s; declared unit %s, read in mm and checked against tools/checks/stepfile.py, " \
          "worst box difference %s mm)" % (inputs.rel(part.step), inputs.sha12(part.step), part.unit["declared"],
                                          fmt(part.unit["box_check_mm"], 3))
    src += "; parts list %s" % inputs.rel(part.list_file) if part.list_file else ""
    regs = sorted({ft.reg["file"] for ft in part.features if ft.reg})
    if regs:
        src += "; feature rationale %s" % ", ".join(regs)
    if spec.get("key_notes") and inputs.key_rows(part.pn):
        src += "; key positions %s" % inputs.rel(inputs.KEYS_CSV)
    # the Lead's ruling (2026-11-01): a note names the source, never an agent, a role or a script as the maker
    src += ". From that STEP: regenerate it, never edit the PDF."
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
    sc += spec.get("_scale_more", "")
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
        [(62, "CREATED BY", AUTHOR, VAL, False), (40, "APPROVED", "not released", VAL, False),
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
    """Generate one drawing; returns a report. step and row: a part outside the repo's lists (tests). A big bent
    part whose flat pattern sheet 1 can't hold legibly (no room for it, or no clear place for its bend tags: CEILING's
    tray 513101, the Lead) gets the flat pattern on a sheet of its own."""
    try:
        return _make(pn, team, spec, out_path, today, step, row)
    except NotDrawable as e:
        msg = str(e)
        if spec.get("bent") and not spec.get("_flat_sheet") and (
                "no clear place for bend" in msg or "no room on the sheet for its sections and flat pattern" in msg):
            return _make(pn, team, dict(spec, _flat_sheet=True), out_path, today, step, row)
        raise


def _make(pn, team, spec, out_path, today=None, step=None, row=None):
    part = Part(pn, team, step=step, pod_system=spec.get("pod_system", True), row=row, bent=spec.get("bent"))
    # rivet holes: an entry lists its rivet hole sizes with the rivet (BASE's D-130 boot: blind rivets in 3.3, 4.2
    # and about 5.0 holes, the tap drills' sizes too; the PM's ruling): those holes are no tap drills, and their
    # table rows name the rivet
    rivets = {float(k): str(v) for k, v in (spec.get("rivet_holes") or {}).items()}
    for ft in part.features:
        ft.rivet = next((v for k, v in rivets.items() if ft.kind == "hole" and abs(ft.f.dia - k) < 0.011), None)
    # tapped holes need thread callouts (item 5): until then such a part isn't drawn (the PM's ruling on #296). A hole
    # is taken as tapped when the part's row says so (rivet holes or not), or when its size is a metric tap drill's
    # (M3 to M8), which no clearance hole in the project uses, and its entry doesn't list it as a rivet hole
    if not spec.get("_test_allow_tapped"):
        words = " ".join((part.row.get(k) or "") for k in ("process", "note", "name", "tolerance")).lower()
        said = re.search(r"\btap(ped|ping)?\b|\bthread|\bm\d+\s*x\s*[\d.]+", words)
        drills = (2.5, 3.3, 4.2, 6.8)
        sized = [ft for ft in part.features if ft.kind == "hole" and not ft.rivet and (
            4.9 <= ft.f.dia <= 5.16 or any(abs(ft.f.dia - d) < 0.06 for d in drills))]
        if said or sized:
            raise NotDrawable("%s has tapped holes (%s): their thread callouts come with item 5; until then the part "
                              "isn't drawn here" % (pn, "its parts list says so" if said else "Ø%s, a tap drill's size" % (
                                  fmt(sized[0].f.dia))))
    # an entry written for a material (D-131's welded steel frames) never draws over a list that still says another
    need = spec.get("material_has")
    if need and need.lower() not in (part.row.get("material") or "").lower():
        raise NotDrawable("%s: its parts list gives the material as '%s', but its drawing entry is for %s (%s): the "
                          "list and the model change first" % (pn, part.row.get("material", ""), need,
                                                               spec.get("material_why", "its notes")))
    with open(part.step, encoding="latin-1") as fh:
        head = fh.read(4000)
    import re as _re
    m = _re.search(r"(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}", head)
    today = today or (m.group(1) if m else datetime.date.today().isoformat())
    while True:
        try:
            sh, pl, vds, secs, removed, dat, scale, report, groups = draw(part, spec, None, today)
            break
        except _Smaller as e:
            if e.flat is not None:          # the flat pattern a step smaller first
                spec = dict(spec, _flat_cap=max(s_ for s_ in (1.0, 0.5, 0.2, 0.1, 0.05) if s_ < e.flat - 1e-9))
                continue
            smaller = [s_ for s_ in ISO_SCALES if s_ < e.scale - 1e-9]
            if not smaller:
                raise NotDrawable("%s: no room on the sheet for its sections and flat pattern at any scale" % pn)
            spec = dict(spec, _max_scale=smaller[0])
    spec = dict(spec)
    spec["_scale"] = scale
    other = [vd for nm, vd in sorted(vds.items()) if nm in pl.aux and abs(vd.scale - scale) > 1e-9]
    if other:
        spec["_scale_more"] = " (view%s %s %s)" % ("s" if len(other) > 1 else "", ", ".join(vd.letter for vd in other),
                                                 scale_text(other[0].scale))
    flats_ = [vd for vd in getattr(pl, "flats", []) if abs(vd.scale - scale) > 1e-9]
    if flats_:
        spec["_scale_more"] = spec.get("_scale_more", "") + " (flat pattern %s)" % scale_text(flats_[0].scale)
    annotate(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today)
    ty, _members = tables_and_text(sh, part, spec, pl, vds, secs, removed, dat, scale, groups, today)
    sheets = 3 if spec.get("_flat_sheet") else 2
    tb_top = title_block(sh, part, spec, scale, removed, today, 1, sheets)
    if ty < tb_top + 4:
        report["warning"] = "the tables run into the title block"
    sh.border()
    sh.flush()
    if spec.get("_flat_sheet"):
        # ---- sheet 2: the flat pattern on its own, at the largest scale the sheet holds with room for its tags
        sh.new_page()
        aw, ah = sh.W - 20 - 10 - 60, sh.H - 20 - TB_ROOM - 50
        fv = flat_view(part, box=(aw, ah))
        w_, h_ = fv.size()
        fv.place_ll(20 + 30 + (aw - w_) / 2, sh.H - 10 - 30 - h_)
        _draw_flat(sh, fv)
        sh.add_obstacles(outline_segments(fv))
        sh.flush()
        flat_dims(sh, part, fv)
        bx = fv.box()
        sh.text((bx[0] + bx[2]) / 2, bx[1] - 22.0, "FLAT PATTERN  %s" % scale_text(fv.scale), 3.5, "center", bold=True)
        sh.text((bx[0] + bx[2]) / 2, bx[1] - 27.0, "from %s, as its x and y draw it: the side it shows faces you; bend "
                "lines thin chain, B1 to B%d (the bend table on sheet 1)" % (os.path.basename(part.flat.path),
                                                                         len(part.flat.rows)), 2.5, "center")
        sh.text((bx[0] + bx[2]) / 2, bx[1] - 31.0, "UP: the flange folds toward you", 2.5, "center")
        fv.page = 1
        pl.flats = [fv]
        title_block(sh, part, spec, scale, removed, today, 2, sheets)
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
    title_block(sh, part, spec, scale, removed, today, sheets, sheets)
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
    if getattr(part, "flat", None):
        srcs.append({"role": "flat pattern", "path": inputs.rel(part.flat.path), "sha256_12": inputs.sha12(part.flat.path)})
    for f in sorted({ft.reg["file"] for ft in part.features if ft.reg}):
        srcs.append({"role": "feature rationale", "path": f, "sha256_12": inputs.sha12(os.path.join(geom.REPO, f))})
    if spec.get("key_notes") and inputs.key_rows(part.pn):
        srcs.append({"role": "key positions", "path": inputs.rel(inputs.KEYS_CSV), "sha256_12": inputs.sha12(inputs.KEYS_CSV)})
    views = []
    for vd in [vds[n_] for n_ in ("principal", "below", "above", "from_left", "from_right", "rear") if n_ in vds] + \
            [vds[n_] for n_ in sorted(pl.aux) if n_ in vds] + secs:
        views.append({"origin": vd.origin_name, "name": vd.name, "n": vd.view.n, "x": vd.view.x, "y": vd.view.y,
                      "scale": vd.scale, "off": vd.off, "origin3d": getattr(vd, "origin3d", None)})
    for vd in removed:
        views.append({"origin": None, "name": "section %s-%s" % (vd.letter, vd.letter), "n": vd.view.n,
                      "x": vd.view.x, "y": vd.view.y, "scale": vd.scale, "off": vd.off})
    for dv in getattr(pl, "details", []):
        views.append({"origin": None, "name": "detail %s" % dv.letter, "n": dv.view.n, "x": dv.view.x,
                      "y": dv.view.y, "scale": dv.scale, "off": dv.off, "box": dv.box()})
    # notches and chamfers: where they are in the model and what the sheet prints for them, for the read-back
    notches = []
    for nt in part.notches:
        shown = next((x for x in part.notches if getattr(x, "drawn", None) and (x is nt or nt in x.drawn["alike"])),
                     None)
        dr = shown.drawn if shown else None
        notches.append({"sgn": nt.sgn, "end_s": nt.end_s, "lax": nt.lax, "across": nt.across, "wall_n": nt.wall_n,
                        "lo": nt.lo, "hi": nt.hi, "s_back": nt.s_back, "t": nt.t, "prof": list(nt.prof),
                        "texts": dict(dr["texts"]) if dr else None, "drawn": nt is shown,
                        "box": dr["view"].box() if dr else None})
    chamfers = [{"sgn": ch.sgn, "end_s": ch.end_s, "lax": ch.lax, "side_n": ch.side_n, "n": ch.n, "leg": ch.leg,
                 "long": ch.long, "leg_dirs": ch.leg_dirs, "pts": ch.pts, "text": ch.drawn["text"],
                 "tip": ch.drawn["tip"], "box": ch.drawn["box"]} for ch in part.chamfers]
    feats = []
    for g in groups:
        vd = vds.get(g.view) if g.view else g.vd
        for ft in g.feats:
            feats.append({"tag": ft.tag, "kind": ft.kind, "dia": ft.f.dia, "entry": ft.f.entry, "axis": ft.f.axis,
                          "depth": ft.f.depth, "body": ft.body.name, "table_origin": vd.origin_name,
                          "drawn_in": vd.origin_name if _end_on(ft, vd.view) else None,
                          "register": ft.reg["id"] if ft.reg else None})
            if ft.kind == "open_slot":
                feats[-1].update({"r": ft.f.r, "edge": ft.f.edge, "mouth": ft.f.mouth, "taper": ft.f.taper,
                                  "along": ft.f.along, "size": size_text(ft),
                                  "dims": getattr(ft, "dims", {}).get("texts"), "dims_box": getattr(ft, "dims", {}).get("box")})
    out = {"generator": TOOL_REV, "pn": part.pn, "rev": part.rev, "dwg": part.dwg_name, "sheet": sh.size,
            "placement": ({"assembly": part.placement["assembly"], "m": part.placement["m"],
                           "t": part.placement["shift"]} if part.placement else None),
            "sheet_h": sh.H, "sources": srcs, "origin": dat["O"], "occurrences": part.occurrences,
            "datums": {"B": dat["B"].tag if dat.get("B") else None,
                       "C": ("plane %s at %s" % (axis_name(dat["C_plane"][0]), fmt(dat["C_plane"][1])))
                       if dat.get("C_plane") else None},
            "views": views, "features": feats, "notches": notches, "chamfers": chamfers,
            "angles": getattr(pl, "angle_marks", []),
            "plates": [{"sgn": p_["sgn"], "t": p_["t"]} for p_ in getattr(part, "plates", [])]}
    if getattr(part, "flat", None):      # only a bent part's record has it: every other sheet keeps its bytes
        out["flat"] = flat_data(part, pl)
    return out
