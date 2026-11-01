"""Assembly and weldment sheets from the team's assembly STEP, outside Fusion (the PM's brief of 2026-11-01; D-139,
D-147 (2)).

One sheet per assembly, drawn from the team's assembly STEP of the same revision:
- first-angle views of the assembly's own parts (a sub-assembly is one item), only as many as it takes to show every
  part and the three overall sizes; visible lines, as an assembly drawing shows them (ISO 128: hidden lines only where
  they help, and the entry names them);
- a balloon for each part number of the assembly (ISO 6433), its leader ending in an arrowhead on a visible edge of
  that part;
- a parts table (ISO 7573) from the team parts list's rows whose parent is this assembly: item, part number, name,
  quantity in this assembly, material and finish, word for word as the list has them;
- the overall sizes, and the interface sizes the entry names;
- for a panel, the layer build-up as a section detail at 1:2 or 1:5 (D-147 (2)).

It reuses drawgen's exact hidden-line projection (project.py), its sheet (sheet.py), its title block and finish (CREATED
BY and the PDF's author Autonomous, no maker line), and its read-back checks; `check` reads every balloon back against
its part in the STEP (the repo's own STEP reader, no OCC) and every table row against the parts list.

A part in the assembly's STEP that the list doesn't put under it (a part that ships on its own and is fitted on site)
is drawn as a reference outline (ISO 128-20 type 05, phantom) with a note, and gets no item number. A list row with
no solid in the STEP (a held or unmodelled part) gets its table row and no balloon; the table says so.

Run it in drawgen's environment (tools/drawgen/run.sh makes it):
    <venv>/bin/python tools/drawgen/assembly.py generate 110101 410101   # into v2/02-Drawings/<team>/, read back
    <venv>/bin/python tools/drawgen/assembly.py check v2/02-Drawings/base/110101_P01_*_DWG.pdf

Each team lists its assembly sheets in its own entries file, tools/drawgen/teams/<team>.py, as ASSEMBLIES = {pn:
entry} (D-139). An entry holds only what the STEP and the list can't give:
- parent_keys: the list's key for this assembly when the list doesn't name parents by number (CEILING: 'assy_c1');
- principal: the pod view to draw first ('front', 'top', 'left', 'right', 'rear', 'bottom'); else the view along the
  assembly's thinnest size that shows the most of its parts;
- views: the related first-angle views ('above', 'below', 'from_left', 'from_right'); else as many as it takes to
  show every part, at least one;
- sections: [{letter, point, normal (toward the viewer), scale, slice (depth kept behind the plane), window (x0, x1,
  y0, y1 in the section's view), stack (the layers' faces as ordinates and a balloon on each layer: a build-up,
  D-147 (2)), on (the view its plane is drawn on)}]; when a part is hidden in every view and no section is given, a
  section across the parts that hide it is added;
- interfaces: [{view, of: [part numbers], along: 'x' or 'y', origin: {pn, pick: '-Y'...}, at: 'centre', 'min' or
  'max', side, words}]: ordinates of those parts from the origin part (guideline 5.1's interface sizes);
- unhatched: part numbers a section leaves whole (ISO 128-50: shafts, pins, studs and the like cut along their
  axis are drawn uncut), such as a spigot or a glide's stem;
- hidden: part numbers whose hidden lines are drawn;
- notes: the fixing method and order, each with its source; tolerance: the sheet's tolerance note;
- sheet, scale: only when the default choice is wrong.
"""

import csv
import math
import os
import re

from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TDataStd import TDataStd_Name
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.gp import gp_Ax2, gp_Dir, gp_Lin, gp_Pnt

import compose
import geom
import inputs
import project
from compose import ISO_SCALES, TOOL_REV, NotDrawable, fmt, mapping_words, scale_text
from geom import vadd, vcross, vdot, vmul, vnorm, vsub
from project import POD_VIEWS, View
from sheet import DASH_HID, SIZES, Sheet, W_HID, W_THIN, W_VIS

PN_RE = re.compile(r"^(\d{6})(?!\d)")


# ------------------------------------------------------------------ small helpers of our own (no core internals)


def _label_name(lab):
    """A STEP product's name as XCAF holds it."""
    n = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), n):
        return n.Get().ToExtString()
    return ""


def _solids_of(shape):
    out = []
    e = TopExp_Explorer(shape, TopAbs_SOLID)
    while e.More():
        out.append(TopoDS.Solid_s(e.Current()))
        e.Next()
    return out


def _latin(s):
    """True when s prints in the built-in Helvetica (Windows-1252), as sheet.text writes it."""
    try:
        s.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def _seg_box(p, q, box, gap=0.4):
    """True when segment p-q comes within gap of the box (Liang-Barsky clip against the grown box)."""
    x0, y0, x1, y1 = box[0] - gap, box[1] - gap, box[2] + gap, box[3] + gap
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            r = qq / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def _plane_trace(view, point, normal, ext):
    """A cutting plane's line on a view that sees it edge on, spanning ext (x0, y0, x1, y1), or None."""
    c = view.to2d(point)
    if abs(abs(vdot(normal, view.x)) - 1) < 1e-6:
        return (c[0], ext[1]), (c[0], ext[3])
    if abs(abs(vdot(normal, view.y)) - 1) < 1e-6:
        return (ext[0], c[1]), (ext[2], c[1])
    return None


def _narrowest(loop):
    """A cut face's narrowest width (true mm): the least distance between two parallel lines of its outline."""
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


def _stepfile():
    """The repo's own STEP reader (tools/checks/stepfile.py, no OCC), for the read-back."""
    import sys as _sys
    p = os.path.join(inputs.REPO, "tools", "checks")
    if p not in _sys.path:
        _sys.path.insert(0, p)
    import stepfile
    return stepfile


# ------------------------------------------------------------------ the assembly in its STEP


class Occ:
    """One placed occurrence of a direct child of the assembly: its part number, product name and solids in the
    file's top coordinates (the pod system for every team file)."""

    def __init__(self, pn, name, solids):
        self.pn = pn
        self.name = name
        self.solids = solids


def _xcaf(path):
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    r = STEPCAFControl_Reader()
    r.SetNameMode(True)
    if int(r.ReadFile(path)) != 1:          # IFSelect_RetDone
        raise RuntimeError("STEP read failed: %s" % path)
    if not r.Transfer(doc):
        raise RuntimeError("STEP transfer failed: %s" % path)
    return doc, XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())


def _pn(name):
    m = PN_RE.match((name or "").strip())
    return m.group(1) if m else None


def read_assembly(path, pn):
    """(the assembly's product name, [Occ]) for the first occurrence of assembly pn in a team STEP. Its direct
    children are its items: a child with a part number is one occurrence of that part (a sub-assembly's solids all
    belong to it); a child without one (a grouping Fusion adds) is looked through. Raises LookupError when the file
    has no assembly pn."""
    _doc, st = _xcaf(path)
    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    found = []

    def solids_under(lab, loc):
        if st.IsAssembly_s(lab):
            out = []
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                out += solids_under(ref, loc.Multiplied(st.GetLocation_s(c)))
            return out
        shape = st.GetShape_s(lab)
        if not loc.IsIdentity():
            shape = shape.Moved(loc)
        return _solids_of(shape)

    def children(lab, loc):
        out = []
        comps = TDF_LabelSequence()
        st.GetComponents_s(lab, comps)
        for i in range(1, comps.Length() + 1):
            c = comps.Value(i)
            ref = TDF_Label()
            st.GetReferredShape_s(c, ref)
            cloc = loc.Multiplied(st.GetLocation_s(c))
            name = _label_name(ref) or _label_name(c)
            cpn = _pn(name)
            if cpn is None and st.IsAssembly_s(ref):
                out += children(ref, cloc)          # a grouping without a part number: look through it
                continue
            out.append(Occ(cpn, name, solids_under(ref, cloc)))
        return out

    def walk(lab, loc, name):
        if found:
            return
        if _pn(name) == pn and st.IsAssembly_s(lab):
            found.append((name, children(lab, loc)))
            return
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)), _label_name(ref) or _label_name(c))

    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        walk(lab, TopLoc_Location(), _label_name(lab))
    if not found:
        raise LookupError("no assembly %s in %s" % (pn, inputs.rel(path)))
    return found[0]


def team_step(team):
    """The team's assembly STEP (PN_REV_TEAM_STEP.step, the team's top number xx0000), newest revision."""
    hits = []
    for p in sorted(os.listdir(os.path.join(inputs.MANUF, team))):
        m = inputs.NAME_RE.match(p)
        if m and m.group(4) == "STEP" and m.group(1).endswith("0000"):
            hits.append((m.group(2), os.path.join(inputs.MANUF, team, p)))
    return sorted(hits)[-1][1] if hits else None


# ------------------------------------------------------------------ the parts list


def _num(s):
    s = (s or "").strip()
    try:
        v = float(s)
    except ValueError:
        return None
    return v


def qty_text(s):
    v = _num(s)
    if v is None:
        return (s or "").strip()
    return ("%d" % v) if abs(v - round(v)) < 1e-9 else ("%g" % v)


def list_rows(pn, team, parent_keys=()):
    """(the assembly's own row, [rows whose parent is the assembly], the list file). A team list names a parent by
    its part number, or (CEILING) by a key such as 'assy_c1': the entry gives those keys. A cell may hold several
    parents ('assy_c1|assy_c2')."""
    keys = {pn} | set(parent_keys)
    own, kids, src = None, [], None
    for p in inputs.team_lists(team):
        with open(p, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        if not rows or "part_number" not in rows[0] or "parent" not in rows[0]:
            continue
        mine = [r for r in rows if keys & {x.strip() for x in (r.get("parent") or "").split("|")}]
        me = [r for r in rows if (r.get("part_number") or "").strip() == pn]
        if me and own is None:
            own, src = me[0], p
        if mine:
            if kids and src != p:
                raise NotDrawable("%s: rows under it in two lists (%s and %s)" % (pn, inputs.rel(src), inputs.rel(p)))
            kids, src = mine, p
    return own, kids, src


def unit_of(row):
    """The row's unit when it isn't a count: its unit cell, else metres for family 84 (the master BOM's 'SEALS AND
    TAPES BY LENGTH (family 84)', counted per metre)."""
    u = (row.get("unit") or "").strip()
    if u and u not in ("pcs", "pc", "ea"):
        return u
    return "m" if (row.get("part_number") or "").strip().startswith("84") else ""


# ------------------------------------------------------------------ the assembly: items, rows, revision


class Item:
    """One part number of the assembly: its list row (None for a reference part), its occurrences in the STEP and
    its item number in the parts table."""

    def __init__(self, pn, row, occs, ref=False):
        self.pn = pn
        self.row = row
        self.occs = occs
        self.ref = ref
        self.no = None
        for o in occs:
            o.item = self

    @property
    def name(self):
        if self.row:
            return (self.row.get("name") or "").strip()
        return re.sub(r"^\d{6}\s*", "", self.occs[0].name).strip() if self.occs else ""


class Assy:
    """Everything one assembly sheet needs, read from the team STEP and the team parts list."""

    def __init__(self, pn, team, entry, step=None):
        self.pn, self.team, self.entry = pn, team, entry
        self.step = step or team_step(team)
        if not self.step:
            raise NotDrawable("%s: %s has no team STEP under v2/03-Manufacturing/%s" % (pn, team, team))
        self.step_name, occs = read_assembly(self.step, pn)
        loose = [o for o in occs if o.pn is None]
        if loose:
            raise NotDrawable("%s: its STEP has parts without a part number (%s): every body belongs to a numbered "
                              "part (guideline 4.1)" % (pn, ", ".join(sorted({o.name or "?" for o in loose}))))
        own, kids, self.list_file = list_rows(pn, team, entry.get("parent_keys", ()))
        if own is None:
            raise NotDrawable("%s: no row in %s's parts lists" % (pn, team))
        if not kids:
            raise NotDrawable("%s: no parts-list row names it as its parent" % pn)
        self.row = own
        self.name = (own.get("name") or "").strip()
        self.name_vi = (own.get("name_vi") or "").strip()
        step_rev = inputs.parse_name(self.step)["rev"]
        own_rev = (own.get("revision") or "").strip()
        if own_rev and own_rev != step_rev:
            raise NotDrawable("%s: its list row says revision %s, its STEP is %s: a drawing takes its STEP's revision"
                              % (pn, own_rev, step_rev))
        self.rev = step_rev
        self.dwg_name = "%s_%s_%s_DWG" % (pn, self.rev, inputs.ascii_name(self.name))
        by_pn = {}
        for o in occs:
            by_pn.setdefault(o.pn, []).append(o)
        self.items, seen = [], set()
        for r in kids:
            p = (r.get("part_number") or "").strip()
            if p in seen:
                raise NotDrawable("%s: %s has two rows under it in %s" % (pn, p, inputs.rel(self.list_file)))
            seen.add(p)
            self.items.append(Item(p, r, by_pn.get(p, [])))
        for p in sorted(set(by_pn) - seen):
            self.items.append(Item(p, None, by_pn[p], ref=True))
        n = 0
        for it in self.items:
            if not it.ref:
                n += 1
                it.no = n
        self.occs = [o for it in self.items for o in it.occs]
        # the STEP's count of each part against the list's quantity (a length or an area isn't counted)
        self.count_notes = []
        for it in self.items:
            if it.ref or not it.occs:
                continue
            q = _num(it.row.get("qty_per_parent"))
            if q is not None and abs(q - round(q)) < 1e-9 and int(round(q)) != len(it.occs):
                raise NotDrawable("%s: the list has %d of %s under it, the STEP %d" % (pn, int(round(q)), it.pn,
                                                                                    len(it.occs)))

    @property
    def table_items(self):
        return [it for it in self.items if not it.ref]

    @property
    def refs(self):
        return [it for it in self.items if it.ref]


# ------------------------------------------------------------------ views



SHOWN_MM = 3.0          # an item counts as shown in a view when this much of its outline (true mm) is visible
VIEW_ORDER = ["principal", "above", "below", "from_left", "from_right"]


def box_of(shapes):
    b = Bnd_Box()
    for s in shapes:
        BRepBndLib.AddOptimal_s(s, b, False, False)
    p, q = b.CornerMin(), b.CornerMax()
    return (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())


def hlr(shapes, view, hidden=()):
    """Exact hidden-line removal of several shapes hiding each other (OCC HLRBRep_Algo, never the polygonal one):
    [prims] per shape, its visible edges, and its hidden ones too for the indices in hidden."""
    algo = HLRBRep_Algo()
    for s in shapes:
        algo.Add(s)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*view.n), gp_Dir(*view.x))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    out = []
    for i, s in enumerate(shapes):
        comps = [(h.VCompound(s), True, "sharp"), (h.OutLineVCompound(s), True, "outline"),
                 (h.Rg1LineVCompound(s), True, "smooth")]
        if i in hidden:
            comps += [(h.HCompound(s), False, "sharp"), (h.OutLineHCompound(s), False, "outline")]
        prims = []
        for comp, vis, src in comps:
            for e in _edges_of(comp):
                prims.extend(project.edge_prims(e, vis, src))
        out.append(project.clean(prims))
    return out


def _edges_of(comp):
    """The edges of an HLR result compound."""
    if comp is None or comp.IsNull():
        return
    e = TopExp_Explorer(comp, TopAbs_EDGE)
    while e.More():
        yield TopoDS.Edge_s(e.Current())
        e.Next()


def prim_len(p):
    if p.kind == "line":
        return math.dist(p.p, p.q)
    if p.kind == "arc":
        return p.r * (p.a1 - p.a0)
    return sum(math.dist(a, b) for a, b in zip(p.pts, p.pts[1:]))


def bez(pts, t):
    """A Bezier curve's point at t, any degree (de Casteljau)."""
    q = [tuple(p) for p in pts]
    while len(q) > 1:
        q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
    return q[0]


def prim_point(p, t):
    """The point at fraction t along a primitive, and the direction along it there."""
    if p.kind == "line":
        return ((p.p[0] + t * (p.q[0] - p.p[0]), p.p[1] + t * (p.q[1] - p.p[1])), (p.q[0] - p.p[0], p.q[1] - p.p[1]))
    if p.kind == "arc":
        a = p.a0 + t * (p.a1 - p.a0)
        return (p.c[0] + p.r * math.cos(a), p.c[1] + p.r * math.sin(a)), (-math.sin(a), math.cos(a))
    q0, q1 = bez(p.pts, max(0.0, t - 0.01)), bez(p.pts, min(1.0, t + 0.01))
    return bez(p.pts, t), (q1[0] - q0[0], q1[1] - q0[1])


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    if L2 < 1e-18:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def prim_dist(pt, p):
    """Distance (view mm) from a point to a primitive."""
    if p.kind == "line":
        return seg_dist(pt, p.p, p.q)
    if p.kind == "arc":
        a = math.atan2(pt[1] - p.c[1], pt[0] - p.c[0])
        while a < p.a0:
            a += 2 * math.pi
        if a <= p.a1:
            return abs(math.dist(pt, p.c) - p.r)
        ends = [(p.c[0] + p.r * math.cos(x), p.c[1] + p.r * math.sin(x)) for x in (p.a0, p.a1)]
        return min(math.dist(pt, e) for e in ends)
    pts = [bez(p.pts, k / 16.0) for k in range(17)]
    return min(seg_dist(pt, a, b) for a, b in zip(pts, pts[1:]))


class AView:
    """A view of the assembly: its projection direction, each occurrence's 2D primitives (view mm, true size), and
    where it sits on the sheet."""

    def __init__(self, name, view, prims, kind="view"):
        self.name = name
        self.view = view
        self.prims = prims          # [[Prim] per occurrence], in Assy.occs order
        self.kind = kind            # view, section
        self.scale = 1.0
        self.off = (0.0, 0.0)
        self.letter = None
        self.hatch = []             # [(occurrence index, [loop prims])] for a section
        self.cut = None             # (point, normal) for a section
        self.kept = None            # a section's cut shapes, per occurrence
        self.spec = {}
        self.own_scale = None       # a section's own scale (else the sheet's)
        self.on = None              # the view a section's cutting plane is drawn on
        allp = [p for ps in prims for p in ps]
        self.extent = project.extent(allp)

    def S(self, p):
        return (self.off[0] + self.scale * p[0], self.off[1] + self.scale * p[1])

    def box(self):
        x0, y0, x1, y1 = self.extent
        a, b = self.S((x0, y0)), self.S((x1, y1))
        return (a[0], a[1], b[0], b[1])

    def size(self, scale=None):
        s = self.scale if scale is None else scale
        x0, y0, x1, y1 = self.extent
        return (x1 - x0) * s, (y1 - y0) * s

    def shown(self, occs):
        """{item: visible outline length (true mm)} of the items with an outline in this view."""
        out = {}
        for o, ps in zip(occs, self.prims):
            L = sum(prim_len(p) for p in ps if p.vis)
            if L > 0:
                out[o.item] = out.get(o.item, 0.0) + L
        return {it: L for it, L in out.items() if L >= SHOWN_MM}


def std_view(name):
    n, x, y = POD_VIEWS[name]
    return View(name, n, x, y)


def plan_views(assy):
    """The views: the principal (the entry's, else the pod's standard view along the assembly's thinnest
    direction, from the side that shows more of its parts), then related first-angle views only while they show a
    part no chosen view shows yet (at least one, for the third overall size); a section when a part is still hidden
    (inside a casing)."""
    entry = assy.entry
    shapes = [geom.compound(o.solids) for o in assy.occs]
    assy.shapes = shapes
    assy.box = box_of(shapes)
    hidden_pns = set(entry.get("hidden", ()))
    hid = {i for i, o in enumerate(assy.occs) if o.item.pn in hidden_pns}

    def make(name, view):
        return AView(name, view, hlr(shapes, view, hid))

    if entry.get("principal"):
        P = make("principal", std_view(entry["principal"]))
        P.std = entry["principal"]
    else:
        ext = [assy.box[3 + k] - assy.box[k] for k in range(3)]
        thin = min(range(3), key=lambda k: ext[k])
        cands = [nm for nm in ("front", "top", "left", "right", "rear", "bottom")
                 if abs(abs(POD_VIEWS[nm][0][thin]) - 1) < 1e-9]
        best = None
        for nm in cands:
            v = make("principal", std_view(nm))
            k = len(v.shown(assy.occs))
            if best is None or k > best[0]:
                best = (k, v, nm)
        P, P.std = best[1], best[2]
    views = {"principal": P}
    shown = set(P.shown(assy.occs))
    want = {it for it in assy.items if it.occs}
    asked = entry.get("views")
    cand = {nm: make(nm, project.related(P.view, nm)) for nm in (asked or ["above", "below", "from_left", "from_right"])}
    if asked:
        views.update(cand)
        for v in cand.values():
            shown |= set(v.shown(assy.occs))
    else:
        while True:
            gains = []
            for nm, v in cand.items():
                if nm in views:
                    continue
                s = set(v.shown(assy.occs))
                gains.append((len((s - shown) & want), len(s), -VIEW_ORDER.index(nm), nm, s))
            if not gains:
                break
            g = max(gains)
            if g[0] == 0 and len(views) >= 2:
                break
            views[g[3]] = cand[g[3]]
            shown |= g[4]
    assy.missing = sorted((want - shown), key=lambda it: it.no or 999)
    letters = iter("ABCDEFGHJKLMNPRSTUVWXYZ")
    for spec in entry.get("sections", ()):
        spec = dict(spec)
        spec.setdefault("letter", next(letters))
        sv = section_view(assy, spec, views)
        views[sv.name] = sv
        shown |= set(sv.shown(assy.occs)) | {assy.occs[i].item for i, _l in sv.hatch}
    if assy.missing and not entry.get("sections"):
        used = {v.letter for v in views.values() if v.letter}
        sv = auto_section(assy, views, next(x for x in letters if x not in used))
        views[sv.name] = sv
        shown |= set(sv.shown(assy.occs)) | {assy.occs[i].item for i, _l in sv.hatch}
    assy.missing = sorted((want - shown), key=lambda it: it.no or 999)
    return views


# ------------------------------------------------------------------ sections (ISO 128-40, 128-50)



def _has_faces(shape):
    return shape is not None and not shape.IsNull() and TopExp_Explorer(shape, TopAbs_FACE).More()


def section_view(assy, spec, views):
    """A section of the whole assembly: the cutting plane through spec's point with its normal toward the viewer
    (the view looks along -normal at what lies behind the plane), each part's cut face hatched. spec may add a
    slice depth (only what lies within it behind the plane), its own scale, and the view the cutting plane is
    drawn on."""
    P = views["principal"]
    letter, point, normal = spec["letter"], tuple(spec["point"]), vnorm(tuple(spec["normal"]))
    base = None
    for v in views.values():
        if v.kind == "view" and all(abs(a - b) < 1e-9 for a, b in zip(v.view.n, normal)):
            base = v.view
            break
    if base is None:
        # keep the principal's up when it lies in the plane (the section reads upright, as the main view), else
        # its X
        if abs(vdot(P.view.y, normal)) < 1e-9:
            y = P.view.y
            base = View("section", normal, vcross(y, normal), y)
        elif abs(vdot(P.view.x, normal)) < 1e-9:
            base = View("section", normal, P.view.x)
        else:
            raise NotDrawable("%s: section %s's plane is square to no axis of the principal view" % (assy.pn, letter))
    view = View("section_" + letter, base.n, base.x, base.y)
    kept = []
    whole = set(assy.entry.get("unhatched", ()))
    off = vdot(point, normal)
    cut_whole = set()
    for i, (o, shp) in enumerate(zip(assy.occs, assy.shapes)):
        b = box_of([shp])
        ds = [vdot((b[0] if j & 1 else b[3], b[1] if j & 2 else b[4], b[2] if j & 4 else b[5]), normal) for j in range(8)]
        if o.item.pn in whole and min(ds) < off < max(ds):
            k = shp                     # ISO 128-50: a shaft or pin the plane cuts along is drawn whole, not hatched
            cut_whole.add(i)
        else:
            k = geom.half_space_keep(shp, point, normal)
            if spec.get("slice"):
                k = geom.half_space_keep(k, vsub(point, vmul(normal, float(spec["slice"]))), vmul(normal, -1.0))
        if spec.get("window"):
            x0, x1, y0, y1 = spec["window"]
            k = geom.window_keep(k, view, x0, x1, y0, y1) if _has_faces(k) else k
        kept.append(k if _has_faces(k) else None)
    live = [i for i, k in enumerate(kept) if k is not None]
    pr = hlr([kept[i] for i in live], view)
    prims = [[] for _ in assy.occs]
    for i, ps in zip(live, pr):
        prims[i] = ps
    av = AView(spec.get("name", "section_" + letter), view, prims, kind="section")
    av.letter = letter
    av.cut = (point, normal)
    av.kept = kept
    av.spec = spec
    av.own_scale = spec.get("scale")
    av.on = spec.get("on")
    for i in live:
        if i in cut_whole:
            continue
        for f in compose.cut_faces(kept[i], point, normal):
            av.hatch.append((i, compose.face_loops(f, view)))
    if not av.hatch:
        raise NotDrawable("%s: section %s cuts no part" % (assy.pn, letter))
    return av


def auto_section(assy, views, letter):
    """For parts no view shows (inside a casing): a section through the middle of those parts on the axis plane
    that cuts the most parts (the most compact on a tie), at its own scale: the largest ISO scale, 1:1 at most, at
    which it fits 180 mm each way."""
    sh = [geom.compound([s for o in it.occs for s in o.solids]) for it in assy.missing]
    b = box_of(sh)
    c = ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)
    best = None
    for n in ((0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
        if not any(v.kind == "view" and abs(vdot(v.view.n, n)) < 1e-9 for v in views.values()):
            continue
        try:
            sv = section_view(assy, {"letter": letter, "point": c, "normal": n}, views)
        except NotDrawable:
            continue
        cut = {assy.occs[i].item for i, _l in sv.hatch if not assy.occs[i].item.ref}
        w, h = sv.size(1.0)
        sv.own_scale = next((k for k in ISO_SCALES if k <= 1.0 and w * k <= 180.0 and h * k <= 180.0), ISO_SCALES[-1])
        key = (set(assy.missing) <= cut, sv.own_scale, len(cut))
        if best is None or key > best[0]:
            best = (key, sv)
    if best is None:
        raise NotDrawable("%s: no section shows %s" % (assy.pn, ", ".join(it.pn for it in assy.missing)))
    return best[1]

# ------------------------------------------------------------------ the sheet: layout



DASH_PHANTOM = (10.0, 1.5, 1.0, 1.5, 1.0, 1.5)     # ISO 128-20 type 05: long dash double-short dash
GAP = 52.0              # between neighbouring views: a dimension and a row of balloons each side
MARGIN = 40.0           # round the views: dimensions, then balloons
EX_MARGIN = (34.0, 52.0, 34.0, 30.0)    # round a section: left, bottom (its title), right, top
COLS = [("ITEM", 13, "c"), ("PART NUMBER", 22, "c"), ("NAME", 74, "l"), ("QTY", 15, "c"), ("MATERIAL", 70, "l"),
        ("FINISH", 58, "l")]
TABLE_W = sum(c[1] for c in COLS)
B_R = 4.6               # balloon radius (ISO 6433: a thin circle round the item number)
B_H = 4.0               # item number letter height
LANE = 16.0             # balloon centres this far out from a view's annotated box


def main_views(views):
    return {nm: v for nm, v in views.items() if v.kind == "view"}


def extra_views(views):
    return [v for v in views.values() if v.kind != "view"]


def placement(views, s):
    """First-angle places (offsets of each view's lower-left relative to the principal's) and the group's box at
    scale s: the view from above below the principal, from below above it, from the left on its right, from the
    right on its left; each aligned with the principal along their shared axis."""
    P = views["principal"]
    wP, hP = P.size(s)
    pos = {"principal": (0.0, 0.0)}
    x_lo, x_hi, y_lo, y_hi = 0.0, wP, 0.0, hP
    for nm, v in main_views(views).items():
        if nm == "principal":
            continue
        w, h = v.size(s)
        pos[nm] = {"above": (0.0, -GAP - h), "below": (0.0, hP + GAP), "from_left": (wP + GAP, 0.0),
                   "from_right": (-GAP - w, 0.0)}[nm]
        x, y = pos[nm]
        x_lo, x_hi, y_lo, y_hi = min(x_lo, x), max(x_hi, x + w), min(y_lo, y), max(y_hi, y + h)
    return pos, (x_lo, y_lo, x_hi, y_hi)


def pack(views, s, area_w, area_h):
    """Where the main group and the sections go in the views' area (sizes in sheet mm): with no section the group
    is centred; else the group takes the top left and the sections fill the column to its right, then the row
    under it. Returns ({name: lower-left of the view's geometry, relative to the area}, ok)."""
    pos, gb = placement(views, s)
    fw, fh = gb[2] - gb[0] + 2 * MARGIN, gb[3] - gb[1] + 2 * MARGIN
    if fw > area_w or fh > area_h:
        return None, False
    ex = extra_views(views)
    out = {}
    if not ex:
        gx, gy = (area_w - fw) / 2 + MARGIN - gb[0], (area_h - fh) / 2 + MARGIN - gb[1]
    else:
        gx, gy = MARGIN - gb[0], area_h - fh + MARGIN - gb[1]
    for nm, (x, y) in pos.items():
        out[nm] = (gx + x, gy + y)
    y_top, x_cur = area_h, 0.0
    for v in ex:
        w, h = v.size(v.own_scale or s)
        ew, eh = w + EX_MARGIN[0] + EX_MARGIN[2], h + EX_MARGIN[1] + EX_MARGIN[3]
        if area_w - fw >= ew and y_top - eh >= 0:
            out[v.name] = (fw + EX_MARGIN[0], y_top - eh + EX_MARGIN[1])
            y_top -= eh
        elif x_cur + ew <= area_w and area_h - fh - eh >= 0:
            out[v.name] = (x_cur + EX_MARGIN[0], area_h - fh - eh + EX_MARGIN[1])
            x_cur += ew
        else:
            return None, False
    return out, True


def area_of(size):
    W, H = SIZES[size]
    return (20.0, 10.0, W - 10 - TABLE_W - 14, H - 10)


def choose_sheet(views, entry):
    """The sheet and the largest ISO scale at which the views and sections fit beside the parts table: A2 first,
    A1 when A2's scale is smaller (guideline 5.1: A2 or A1, legible at the published print size)."""
    best = None
    for size in ([entry["sheet"]] if entry.get("sheet") else ["A2", "A1"]):
        x0, y0, x1, y1 = area_of(size)
        for s in ([entry["scale"]] if entry.get("scale") else ISO_SCALES):
            _out, ok = pack(views, s, x1 - x0, y1 - y0)
            if ok:
                if best is None or s > best[1] + 1e-12:
                    best = (size, s)
                break
    if best is None:
        raise NotDrawable("the views fit no ISO scale on an A1 sheet")
    return best


# ------------------------------------------------------------------ the sheet: drawing


VIEW_WORDS = {"principal": None, "above": "VIEW FROM ABOVE", "below": "VIEW FROM BELOW",
              "from_left": "VIEW FROM THE LEFT", "from_right": "VIEW FROM THE RIGHT"}
STD_WORDS = {"front": "FRONT VIEW", "top": "VIEW FROM ABOVE", "left": "VIEW FROM THE LEFT", "right": "VIEW FROM THE RIGHT",
             "rear": "REAR VIEW", "bottom": "VIEW FROM BELOW"}


HATCH = [(45.0, 1.0), (135.0, 1.0), (45.0, 0.6), (135.0, 0.6), (60.0, 1.0), (120.0, 1.0), (30.0, 1.0), (150.0, 1.0)]


def _sheet_loop(av, loop):
    out = []
    for p in loop:
        if p.kind == "line":
            out.append(("line", av.S(p.p), av.S(p.q)))
        elif p.kind == "arc":
            out.append(("arc", av.S(p.c), p.r * av.scale, p.a0, p.a1))
        else:
            pts = [av.S(bez(p.pts, k / 8.0)) for k in range(9)]
            out += [("line", a, b) for a, b in zip(pts, pts[1:])]
    return out


def draw_prims(sh, av, occs):
    """The view's outlines: visible lines (thick), a reference part's in the phantom line, hidden lines dashed
    where the entry asks; a section's cut faces hatched, each part its own way (ISO 128-50), a thin one solid."""
    for o, ps in zip(occs, av.prims):
        ref = o.item.ref
        for p in ps:
            if p.vis:
                w, dash = (W_THIN, DASH_PHANTOM) if ref else (W_VIS, None)
            else:
                w, dash = W_HID, DASH_HID
            if p.kind == "line":
                sh.line(av.S(p.p), av.S(p.q), w, dash)
            elif p.kind == "arc":
                sh.arc(av.S(p.c), p.r * av.scale, p.a0, p.a1, w, dash)
            else:
                sh.bezier([av.S(q) for q in p.pts], w, dash)
    sh.flush()
    style = {}
    for i, loop in av.hatch:
        it = occs[i].item
        if it.ref:          # a reference part isn't hatched: its cut outline in the phantom line
            for p in loop:
                if p.kind == "line":
                    sh.line(av.S(p.p), av.S(p.q), W_THIN, DASH_PHANTOM)
                elif p.kind == "arc":
                    sh.arc(av.S(p.c), p.r * av.scale, p.a0, p.a1, W_THIN, DASH_PHANTOM)
            continue
        if it not in style:
            style[it] = HATCH[len(style) % len(HATCH)]
        ang, sp = style[it]
        sl = _sheet_loop(av, loop)
        narrow = _narrowest(loop) * av.scale
        if narrow < 1.6:
            sh.fill_loops([sl])
        else:
            sh.hatch([sl], spacing=max(0.8, min(2.5, narrow / 2.5)) * (1.6 if sp > 0.8 else 1.0), angle=ang, w=0.18)
    sh.flush()


def cutting_planes(sh, views):
    """Each section's cutting plane on a view that sees it edge on (the entry's, else the principal, else the
    first that does), with the letter and arrows looking the section's way (ISO 128-40)."""
    out = []
    for sv in extra_views(views):
        point, normal = sv.cut
        cands = ([sv.on] if sv.on else []) + ["principal"] + [nm for nm in VIEW_ORDER if nm in views]
        for nm in cands:
            v = views.get(nm)
            if v is None or v.kind != "view" or abs(vdot(v.view.n, normal)) > 1e-9:
                continue
            x0, y0, x1, y1 = v.extent
            if sv.spec.get("window"):       # a detail section: its plane only over the window's span
                wx0, wx1, wy0, wy1 = sv.spec["window"]
                corners = [vadd(vadd(vmul(sv.view.x, a), vmul(sv.view.y, b)), vmul(sv.view.n, vdot(point, sv.view.n)))
                           for a in (wx0, wx1) for b in (wy0, wy1)]
                xs = [vdot(c, v.view.x) for c in corners]
                ys = [vdot(c, v.view.y) for c in corners]
                x0, x1 = max(x0, min(xs)), min(x1, max(xs))
                y0, y1 = max(y0, min(ys)), min(y1, max(ys))
            tr = _plane_trace(v.view, point, normal, (x0, y0, x1, y1))
            if tr is None:
                continue
            p0, q0 = v.S(tr[0]), v.S(tr[1])
            ux, uy = q0[0] - p0[0], q0[1] - p0[1]
            L = math.hypot(ux, uy)
            ext = 8.0
            while ext < 70.0:       # a plane near another gets longer ends, so their letters don't meet
                p = (p0[0] - ux / L * ext, p0[1] - uy / L * ext)
                q = (q0[0] + ux / L * ext, q0[1] + uy / L * ext)
                if all(math.dist(p, c["p"]) > 14.0 and math.dist(q, c["q"]) > 14.0 for c in out if c["on"] == nm):
                    break
                ext += 12.0
            look = (vdot(vmul(normal, -1.0), v.view.x), vdot(vmul(normal, -1.0), v.view.y))
            if section_line(sh, p, q, sv.letter, look) is None:
                raise NotDrawable("no free place for section %s's letters on view %s" % (sv.letter, nm))
            out.append({"letter": sv.letter, "on": nm, "p": p, "q": q})
            break
        else:
            raise NotDrawable("no view sees section %s's plane edge on" % sv.letter)
    sh.flush()
    return out


class Side:
    """Which sides of a view keep a dimension (so the balloons go further out there)."""

    def __init__(self):
        self.dims = {"left": 0.0, "right": 0.0, "up": 0.0, "down": 0.0}


def overall_dims(sh, views, sides):
    """The three overall sizes (true mm, read from the exact projection): the principal's width and height, and
    the depth on the first related view; each on a side no neighbouring view uses."""
    P = views["principal"]
    out = []

    def put(av, axis, side):
        x0, y0, x1, y1 = av.extent
        if axis == "x":
            val = x1 - x0
            ya = y1 if side == "up" else y0
            p1, p2 = av.S((x0, ya)), av.S((x1, ya))
        else:
            val = y1 - y0
            xa = x0 if side == "left" else x1
            p1, p2 = av.S((xa, y0)), av.S((xa, y1))
        txt = fmt(val, 1)
        sh.dim_linear(p1, p2, side, 10.0, txt, 2.5)
        sides[av.name].dims[side] = max(sides[av.name].dims[side], 14.0)
        out.append({"view": av.name, "axis": axis, "value": round(val, 3), "text": txt})

    put(P, "x", "up" if "below" not in views else ("down" if "above" not in views else "up"))
    put(P, "y", "left" if "from_right" not in views else ("right" if "from_left" not in views else "left"))
    for nm, axis, side in (("above", "y", "left"), ("from_left", "x", "down"), ("below", "y", "left"),
                           ("from_right", "x", "down")):
        if nm in views:
            put(views[nm], axis, side)
            break
    sh.flush()
    return out


def view_title(sh, av, assy):
    """Under the view (beyond its dimension and balloons): what the view is, its scale, and its X/Y mapping to the
    pod axes (guideline 3.3)."""
    if av.kind == "section":
        head = "SECTION %s-%s  %s" % (av.letter, av.letter, scale_text(av.scale))
    else:
        head = "%s  %s" % (STD_WORDS.get(_std_name(av.view)) or VIEW_WORDS.get(av.name) or "VIEW",
                           scale_text(av.scale))
    words = mapping_words(av.view, True)
    x0, y0, x1, y1 = av.box()
    cx = (x0 + x1) / 2
    for dy in [k * 2.0 for k in range(0, 40)]:
        y = y0 - av.title_gap - dy
        b1 = sh.text_box(cx, y, head, 3.5, "center", bold=True)
        b2 = sh.text_box(cx, y - 5.5, words, 2.5, "center")
        if sh.is_free(b1) and sh.is_free(b2):
            sh.text(cx, y, head, 3.5, "center", bold=True)
            sh.text(cx, y - 5.5, words, 2.5, "center")
            av.title_box = (min(b1[0], b2[0]), b2[1], max(b1[2], b2[2]), b1[3])
            return
    raise NotDrawable("%s: no free place for the title of view %s" % (assy.pn, av.name))


def _std_name(view):
    for nm, (n, x, y) in POD_VIEWS.items():
        if all(abs(a - b) < 1e-9 for a, b in zip(n, view.n)) and all(abs(a - b) < 1e-9 for a, b in zip(x, view.x)):
            return nm
    return None


# ------------------------------------------------------------------ balloons (ISO 6433)


FAR = 1e5               # the viewer's distance for a sight line (mm)
CLEAR = 0.8             # an arrow's tip at least this far (paper mm) from every other part's line
DOT_CLEAR = 1.2         # a dot at least this far (paper mm) from every line


def _pt3(av, xy, depth):
    v = av.view
    return vadd(vadd(vmul(v.x, xy[0]), vmul(v.y, xy[1])), vmul(v.n, depth))


def _shape_of(av, i, assy):
    return av.kept[i] if av.kind == "section" else assy.shapes[i]


def edge_tip3d(av, i, assy, xy):
    """The 3D point of part i's edge that projects to xy in this view, nearest the viewer: the sight line through
    xy touches the part there (BRepExtrema); None when it doesn't (within 0.01 mm)."""
    shp = _shape_of(av, i, assy)
    if shp is None:
        return None
    a, b = _pt3(av, xy, FAR), _pt3(av, xy, -FAR)
    e = BRepBuilderAPI_MakeEdge(gp_Pnt(*a), gp_Pnt(*b)).Edge()
    d = BRepExtrema_DistShapeShape(e, shp)
    if not d.IsDone() or d.Value() > 0.01:
        return None
    best = None
    for k in range(1, d.NbSolution() + 1):
        p = d.PointOnShape2(k)
        q = (p.X(), p.Y(), p.Z())
        if best is None or vdot(q, av.view.n) > vdot(best, av.view.n):
            best = q
    return best


class Rays:
    """Sight lines into a view's parts: which part a line through a 2D point meets first, and where."""

    def __init__(self, av, assy):
        self.av = av
        self.inter = []
        for i in range(len(assy.occs)):
            shp = _shape_of(av, i, assy)
            if shp is None:
                self.inter.append(None)
                continue
            it = IntCurvesFace_ShapeIntersector()
            it.Load(shp, 1e-6)
            self.inter.append(it)

    def first(self, xy):
        v = self.av.view
        lin = gp_Lin(gp_Pnt(*_pt3(self.av, xy, FAR)), gp_Dir(*vmul(v.n, -1.0)))
        best = None
        for i, it in enumerate(self.inter):
            if it is None:
                continue
            it.Perform(lin, 0.0, 2 * FAR)
            if not it.IsDone():
                continue
            for k in range(1, it.NbPnt() + 1):
                w = it.WParameter(k)
                if best is None or w < best[0]:
                    p = it.Pnt(k)
                    best = (w, i, (p.X(), p.Y(), p.Z()))
        return best


def _others(av, assy, item):
    return [p for o, ps in zip(assy.occs, av.prims) if o.item is not item for p in ps if p.vis]


def edge_candidates(av, assy, item):
    """Arrow tips: points on the item's visible edges at least CLEAR on paper from every other part's line,
    nearest the view's side first (short leaders)."""
    s = av.scale
    cl = CLEAR / s
    others = _others(av, assy, item)
    bx = av.box()
    out = []
    for i, (o, ps) in enumerate(zip(assy.occs, av.prims)):
        if o.item is not item:
            continue
        for p in ps:
            if not p.vis or prim_len(p) * s < 2.0:
                continue
            for t in (0.5, 0.3, 0.7, 0.15, 0.85):
                pt, d = prim_point(p, t)
                if any(prim_dist(pt, q) < cl for q in others if _bbox_near(q, pt, cl)):
                    continue
                S = av.S(pt)
                edge = min(S[0] - bx[0], bx[2] - S[0], S[1] - bx[1], bx[3] - S[1])
                out.append((edge, "arrow", i, pt, S, d))
    out.sort(key=lambda c: c[0])
    return out


def dot_candidates(av, assy, item, rays):
    """Dot tips (ISO 128-22: a leader ending inside a part's outline ends in a dot): points just inside the item's
    visible region (its edges offset inward), at least DOT_CLEAR on paper from every line, where the sight line
    meets this item first; for a section, inside its cut face."""
    s = av.scale
    allp = [p for ps in av.prims for p in ps if p.vis]
    bx = av.box()
    out = []
    seen = 0
    for i, (o, ps) in enumerate(zip(assy.occs, av.prims)):
        if o.item is not item:
            continue
        loops = [l for j, l in av.hatch if j == i]
        for p in ps + [q for l in loops for q in l]:
            if not p.vis or prim_len(p) * s < 3.0:
                continue
            for t in (0.5, 0.25, 0.75):
                pt, d = prim_point(p, t)
                dl = math.hypot(*d)
                if dl < 1e-12:
                    continue
                nrm = (-d[1] / dl, d[0] / dl)
                for side in (1, -1):
                    for off in (1.6, 3.0, 5.0):
                        q = (pt[0] + side * nrm[0] * off / s, pt[1] + side * nrm[1] * off / s)
                        if any(prim_dist(q, r) < DOT_CLEAR / s for r in allp if _bbox_near(r, q, DOT_CLEAR / s)):
                            continue
                        seen += 1
                        if seen > 400:
                            break
                        hit = rays.first(q)
                        if hit is None or hit[1] != i:
                            continue
                        S = av.S(q)
                        edge = min(S[0] - bx[0], bx[2] - S[0], S[1] - bx[1], bx[3] - S[1])
                        out.append((edge + 2.0, "dot", i, q, S, None, hit[2]))
                        break
    out.sort(key=lambda c: c[0])
    return out


def _cross(a, b, c, d):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return (o1 * o2 < 0) and (o3 * o4 < 0)


def lane_spots(av, side, S):
    """Balloon centres along the lanes round a view, nearest the tip's side first, sliding along the lane."""
    x0, y0, x1, y1 = av.box()
    d = side.dims
    lanes = [("left", (x0 - d["left"] - LANE, None)), ("right", (x1 + d["right"] + LANE, None)),
             ("down", (None, y0 - d["down"] - LANE - getattr(av, "title_room", 0.0))),
             ("up", (None, y1 + d["up"] + LANE))]
    dist = {"left": S[0] - x0, "right": x1 - S[0], "down": S[1] - y0, "up": y1 - S[1]}
    lanes.sort(key=lambda ln: dist[ln[0]])
    for k in range(0, 15):
        for nm, (lx, ly) in lanes[:3]:
            for sgn in ((0,) if k == 0 else (1, -1)):
                off = sgn * k * 11.0
                yield nm, ((lx, S[1] + off) if lx is not None else (S[0] + off, ly))


def place_balloons(sh, assy, views, sides, items=None, only=None, recs=None, leaders=None, centres=None):
    """A balloon for each part number in the table that the STEP has: its leader from the balloon to the part,
    ending in an arrowhead on a visible edge (ISO 128-22: on an outline) or, when every edge of it lies against
    another part, in a dot inside its outline; crossing no text, no other leader and no other balloon."""
    leaders = [] if leaders is None else leaders
    centres = [] if centres is None else centres
    recs = [] if recs is None else recs
    order = ["principal"] + [nm for nm in VIEW_ORDER if nm in views and nm != "principal"] + \
        [nm for nm in views if nm not in VIEW_ORDER]
    if only:
        order = [only]
    rays = {}
    for it in (items if items is not None else assy.table_items):
        if not it.occs:
            continue
        done = None
        for style in ("arrow", "dot"):
            cands = []
            for k, nm in enumerate(order):
                av = views[nm]
                if style == "arrow":
                    cs = edge_candidates(av, assy, it)[:40]
                else:
                    if nm not in rays:
                        rays[nm] = Rays(av, assy)
                    cs = dot_candidates(av, assy, it, rays[nm])[:20]
                cands += [(c[0] + 30.0 * k, nm, c) for c in cs]
            cands.sort(key=lambda c: c[0])
            for _score, nm, c in cands[:80]:
                av = views[nm]
                kind, i, pt, S, d = c[1], c[2], c[3], c[4], c[5]
                for _lane, ctr in lane_spots(av, sides[nm], S):
                    r = B_R
                    if not sh.is_free((ctr[0] - r - 0.6, ctr[1] - r - 0.6, ctr[0] + r + 0.6, ctr[1] + r + 0.6)):
                        continue
                    dx, dy = S[0] - ctr[0], S[1] - ctr[1]
                    L = math.hypot(dx, dy)
                    if L < r + 6.0 or L > 170.0:
                        continue
                    u = (dx / L, dy / L)
                    a = (ctr[0] + u[0] * r, ctr[1] + u[1] * r)
                    if d is not None:
                        dl = math.hypot(*d)
                        if dl > 1e-12 and abs(u[0] * d[0] / dl + u[1] * d[1] / dl) > math.cos(math.radians(25)):
                            continue        # nearly along the edge it lands on: it would read as that edge
                    if any(_seg_box(a, S, b, 0.6) for b in sh.boxes):
                        continue
                    if any(_cross(a, S, p, q) for p, q in leaders):
                        continue
                    if any(seg_dist(cc, a, S) < r + 1.5 for cc in centres):
                        continue
                    t3 = c[6] if kind == "dot" else edge_tip3d(av, i, assy, pt)
                    if t3 is None:
                        break
                    done = (nm, kind, i, pt, S, ctr, a, u, t3)
                    break
                if done:
                    break
            if done:
                break
        if not done:
            raise NotDrawable("%s: no free place for the balloon of item %d (%s)" % (assy.pn, it.no, it.pn))
        nm, kind, i, pt, S, ctr, a, u, t3 = done
        if kind == "arrow":
            sh.line(a, (S[0] - u[0] * 0.5, S[1] - u[1] * 0.5), W_THIN)
            sh.arrow(S, u, 3.0, 1.0)
        else:
            sh.line(a, S, W_THIN)
            sh.circle(S, 0.6, 0.1, fill=(0, 0, 0))
        sh.circle(ctr, B_R, W_THIN)
        sh.text(ctr[0], ctr[1], str(it.no), B_H, "center", valign="mid")
        sh.boxes.append((ctr[0] - B_R, ctr[1] - B_R, ctr[0] + B_R, ctr[1] + B_R))
        leaders.append((a, S))
        centres.append(ctr)
        recs.append({"no": it.no, "pn": it.pn, "view": nm, "end": kind, "tip": S, "tip_view": pt, "tip3d": t3,
                     "centre": ctr, "r": B_R})
        sh.flush()
    return recs


def _bbox_near(p, pt, pad):
    x0, y0, x1, y1 = p.bbox()
    return x0 - pad <= pt[0] <= x1 + pad and y0 - pad <= pt[1] <= y1 + pad




# ------------------------------------------------------------------ table, notes, title block


def table_rows(assy):
    rows = []
    for it in assy.table_items:
        r = it.row
        u = unit_of(r)
        rows.append({"no": it.no, "mark": "" if it.occs else "*", "pn": it.pn, "name": it.name,
                     "qty": qty_text(r.get("qty_per_parent")) + ((" " + u) if u else ""),
                     "material": (r.get("material") or "").strip() or "-",
                     "finish": (r.get("finish") or "").strip() or "-"})
    return rows


def notes_for(assy, views):
    e = assy.entry
    out = ["Parts, quantities, materials and finishes as the parts list %s (its rows under %s), word for word; each "
           "part's own drawing holds its sizes and tolerances." % (os.path.basename(assy.list_file), assy.pn)]
    un = [it for it in assy.table_items if not it.occs]
    if un:
        out.append("Items marked * (%s) are not in the STEP %s %s: they have no balloon; their places are in their "
                   "rows and the joints register." % (", ".join("%d %s" % (it.no, it.pn) for it in un),
                                                      os.path.basename(assy.step), assy.rev))
    for it in assy.refs:
        r, _k, _f = list_rows(it.pn, assy.team)
        par = (r or {}).get("parent", "").strip() if r else ""
        why = (r or {}).get("source", "").strip() if r else ""
        out.append("%s %s is drawn as a reference outline (thin long dash double-dot line, ISO 128-20 type 05) and "
                   "is not an item of this assembly: the parts list puts it under %s%s." % (
                       it.pn, it.name, par or "another assembly", (" (%s)" % why) if why else ""))
    out.append("Views in first angle (ISO 5456-2); each view title gives its X and Y in pod axes (guideline 3.3). "
               "Visible outlines only, as an assembly drawing shows them.")
    for g in e.get("interfaces", ()):
        if g.get("words"):
            out.append("Interface sizes (ordinates, true mm from the STEP): %s." % g["words"])
    out += list(e.get("notes", ()))
    out.append("TOLERANCE: " + e.get("tolerance", "the overall sizes are for reference; each part's drawing holds its "
                                                  "own tolerances. Not ISO 2768."))
    return out


class TitlePart:
    """What compose.title_block reads, for an assembly."""

    def __init__(self, assy):
        self.pn, self.name, self.name_vi, self.rev, self.dwg_name = (assy.pn, assy.name, assy.name_vi, assy.rev,
                                                                     assy.dwg_name)
        mass = (assy.row.get("mass_each_kg") or assy.row.get("unit_mass_kg") or "").strip()
        self.row = {"material": "see the parts list", "finish": "see the parts list", "mass_each_kg": mass}


# ------------------------------------------------------------------ one sheet


def _title_height(size, assy, spec, today):
    """The title block's height, measured on a scratch sheet (it sizes its rows to their wrapped text)."""
    scratch = Sheet(size)
    top = compose.title_block(scratch, TitlePart(assy), spec, spec["_scale"], [], today, 1, 2)
    scratch.doc.close()
    return top


def make(pn, team, entry, out_path, today=None, step=None):
    """Draw assembly pn's sheet into out_path; returns a report (as compose.make does)."""
    assy = Assy(pn, team, entry, step=step)
    views = plan_views(assy)
    size, s = choose_sheet(views, entry)
    with open(assy.step, encoding="latin-1") as fh:
        head = fh.read(4000)
    m = re.search(r"(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}", head)
    today = today or (m.group(1) if m else "2026-01-01")
    sh = Sheet(size, title="%s %s" % (assy.pn, assy.name), subject="%s %s DRAFT" % (assy.dwg_name, assy.rev),
               keywords="drawgen assembly; D-139; source %s sha256:%s" % (inputs.rel(assy.step), inputs.sha12(assy.step)))
    W, H = sh.W, sh.H
    for v in views.values():
        v.scale = v.own_scale or s if v.kind != "view" else s
    ax0, ay0, ax1, ay1 = area_of(size)
    pos, ok = pack(views, s, ax1 - ax0, ay1 - ay0)
    if not ok:
        raise NotDrawable("%s: the views don't fit the %s sheet at %s" % (pn, size, scale_text(s)))
    for nm, v in views.items():
        px, py = pos[nm]
        v.off = (ax0 + px - v.scale * v.extent[0], ay0 + py - v.scale * v.extent[1])
    # the table column is kept clear of every label placed on the views
    sh.reserved.append((W - 10 - TABLE_W - 6, 10, W - 10, H - 10))
    order = [nm for nm in VIEW_ORDER if nm in views] + [v.name for v in extra_views(views)]
    for nm in order:
        draw_prims(sh, views[nm], assy.occs)
    cuts = cutting_planes(sh, views)
    sides = {nm: Side() for nm in views}
    dims = overall_dims(sh, views, sides)
    ifaces = interface_dims(sh, assy, views, sides)
    stacks = stack_dims(sh, assy, views, sides)
    for nm in order:
        av = views[nm]
        av.title_gap = sides[nm].dims["down"] + 9.0
        view_title(sh, av, assy)
        av.title_room = (av.box()[1] - av.title_box[1]) - sides[nm].dims["down"] + 2.0
    sh.flush()
    leaders, centres = [], []
    balloons = place_balloons(sh, assy, views, sides, leaders=leaders, centres=centres)
    for sv in extra_views(views):           # a build-up section names its layers too (D-147 (2))
        if sv.spec.get("stack"):
            cut = []
            for i, _l in sv.hatch:
                it = assy.occs[i].item
                if not it.ref and it not in cut:
                    cut.append(it)
            place_balloons(sh, assy, views, sides, items=sorted(cut, key=lambda it: it.no), only=sv.name,
                           recs=balloons, leaders=leaders, centres=centres)
    # ---- the right column: the parts table at the top, the title block at the bottom, the notes between
    spec = {"_scale": s}
    rows = table_rows(assy)
    cells = [["%d%s" % (r["no"], r["mark"]), r["pn"], r["name"], r["qty"], r["material"], r["finish"]] for r in rows]
    tx, ty = W - 10 - TABLE_W - 2.0, H - 10 - 2.0
    title = "PARTS LIST: %s %s" % (assy.pn, assy.name)
    y_bot, row_spans = draw_table(sh, tx, ty, COLS, cells, 2.5, title=title, title_size=3.5)
    notes = notes_for(assy, views)
    nw = TABLE_W - 9.0
    need = 9.0 + sum(len(wrap2(sh, t, 2.5, nw)) * 2.5 * 1.6 + 2.0 for t in notes)
    tb_top = _title_height(size, assy, spec, today)
    sheets = 1 if y_bot - 6.0 - need >= tb_top + 4.0 else 2
    compose.title_block(sh, TitlePart(assy), spec, s, [], today, 1, sheets)
    if sheets == 1:
        ny = y_bot - 8.0
        sh.text(tx, ny, "NOTES", 3.5, bold=True)
        ny -= 6.0
        for i, t in enumerate(notes, 1):
            sh.text(tx, ny, "%d." % i, 2.5)
            ny = paragraph2(sh, tx + 7.0, ny, t, 2.5, nw) - 2.0
    sh.border()
    sh.flush()
    if sheets == 2:
        sh.new_page()
        nx, ny = 30.0, sh.H - 22.0
        sh.text(nx, ny, "GENERAL NOTES", 3.5, bold=True)
        ny -= 8.0
        for i, t in enumerate(notes, 1):
            sh.text(nx, ny, "%d." % i, 2.5)
            ny = paragraph2(sh, nx + 7, ny, t, 2.5, 360.0) - 2.0
        compose.title_block(sh, TitlePart(assy), spec, s, [], today, 2, 2)
        sh.border()
        sh.flush()
    xs = [tx]
    for c in COLS:
        xs.append(xs[-1] + c[1])
    data = {"kind": "assembly", "generator": TOOL_REV, "pn": assy.pn, "rev": assy.rev, "dwg": assy.dwg_name,
            "sheet": size, "sheet_h": H, "team": team,
            "sources": [{"role": "STEP", "path": inputs.rel(assy.step), "sha256_12": inputs.sha12(assy.step)},
                        {"role": "parts list", "path": inputs.rel(assy.list_file),
                         "sha256_12": inputs.sha12(assy.list_file)}],
            "parent_keys": list(entry.get("parent_keys", ())), "unhatched": list(entry.get("unhatched", ())),
            "views": [{"name": nm, "kind": v.kind, "n": v.view.n, "x": v.view.x, "y": v.view.y, "scale": v.scale,
                       "off": v.off, "box": v.box(), "letter": v.letter,
                       "cut": ({"point": v.cut[0], "normal": v.cut[1], "slice": v.spec.get("slice")} if v.cut else None)}
                      for nm, v in views.items()],
            "cutting_planes": cuts,
            "balloons": balloons, "dims": dims, "interfaces": ifaces, "stacks": stacks,
            "table": {"x": xs, "y_top": ty, "y_bot": y_bot,
                      "rows": [{"no": r["no"], "pn": r["pn"], "top": a, "bottom": b} for r, (a, b) in zip(rows, row_spans)]},
            "refs": [it.pn for it in assy.refs], "unmodelled": [it.pn for it in assy.table_items if not it.occs]}
    sh.meta["creationDate"] = "D:%s000000Z" % today.replace("-", "")
    sh.meta["modDate"] = sh.meta["creationDate"]
    sh.data = data
    sh.save(out_path)
    return {"dwg": assy.dwg_name, "data": data, "sheet": size, "scale": s, "views": list(views),
            "missing": [it.pn for it in assy.missing]}


def generate(pn, team, entry, out_dir):
    """Write the sheet as out_dir/PN_REV_NAME_DWG.pdf; never over a PDF drawgen didn't make (a Fusion drawing)."""
    tmp = os.path.join(out_dir, ".drawgen-%s.pdf" % pn)
    os.makedirs(out_dir, exist_ok=True)
    try:
        rep = make(pn, team, entry, tmp)
        final = os.path.join(out_dir, rep["dwg"] + ".pdf")
        if os.path.exists(final):
            import fitz
            with fitz.open(final) as d:
                if (d.metadata or {}).get("creator") != "drawgen":
                    raise NotDrawable("%s exists and was not made by drawgen (a Fusion drawing): left as it is"
                                      % inputs.rel(final))
        os.replace(tmp, final)
        return final, rep
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ------------------------------------------------------------------ interface sizes


def _ref_point(occ, at, axis3):
    """A part's centre (its box's), or the point of its box at the low or high end along a view axis."""
    b = box_of(occ.solids)
    c = [(b[k] + b[k + 3]) / 2 for k in range(3)]
    if at in ("min", "max"):
        corners = [(b[0] if i & 1 else b[3], b[1] if i & 2 else b[4], b[2] if i & 4 else b[5]) for i in range(8)]
        vals = [vdot(q, axis3) for q in corners]
        target = min(vals) if at == "min" else max(vals)
        cur = vdot(tuple(c), axis3)
        c = [c[k] + axis3[k] * (target - cur) for k in range(3)]
    return tuple(c)


def interface_dims(sh, assy, views, sides):
    """The interface sizes the entry names (guideline 5.1: the sizes where the assembly meets the next one), as
    ordinate dimensions (ISO 129-1 9.3) in a view: each named part's centre (or its face at the low or high end
    along the axis), from an origin the entry picks (a named part's occurrence nearest a pod direction). Values in
    true mm from the STEP; the read-back measures them again."""
    out = []
    for g in assy.entry.get("interfaces", ()):
        av = views[g.get("view", "principal")]
        axis = g.get("along", "x")
        ax3 = av.view.x if axis == "x" else av.view.y
        o_spec = g["origin"]
        cand = [o for o in assy.occs if o.item.pn == o_spec["pn"]]
        if not cand:
            raise NotDrawable("%s: interface origin %s is not in the STEP" % (assy.pn, o_spec["pn"]))
        pick = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1),
                "-Z": (0, 0, -1)}[o_spec.get("pick", "-Y")]
        org3 = max((_ref_point(o, o_spec.get("at", "centre"), ax3) for o in cand), key=lambda c: vdot(c, pick))
        pts3 = []
        for o in assy.occs:
            if o.item.pn in g["of"]:
                pts3.append((o.item.pn, _ref_point(o, g.get("at", "centre"), ax3)))
        if not pts3:
            raise NotDrawable("%s: no part of interface group %s in the STEP" % (assy.pn, g["of"]))
        o2 = av.S(av.view.to2d(org3))
        sp = [av.S(av.view.to2d(c)) for _pn, c in pts3]
        raw = [vdot(vsub(c, org3), ax3) for _pn, c in pts3]
        sgn = 1.0 if sum(1 for r_ in raw if r_ > 1e-6) >= sum(1 for r_ in raw if r_ < -1e-6) else -1.0
        vals = [fmt(sgn * r_, 2) for r_ in raw]
        side = g.get("side", "up" if axis == "x" else "right")
        x0, y0, x1, y1 = av.box()
        d = sides[av.name].dims
        if axis == "x":
            level = (y1 + d["up"] + 12.0) if side == "up" else (y0 - d["down"] - 12.0)
        else:
            level = (x1 + d["right"] + 12.0) if side == "right" else (x0 - d["left"] - 12.0)
        draw_ordinates(sh, o2, sp, axis, level, vals)
        d[side] += 12.0 + 4.0 + max(sh.text_width(v_, 2.5) for v_ in vals + ["0"])
        out.append({"view": av.name, "axis": axis, "origin3d": org3, "words": g.get("words", ""),
                    "points": [{"pn": pn, "at3d": c, "value": v_} for (pn, c), v_ in zip(pts3, vals)]})
    sh.flush()
    return out


def draw_ordinates(sh, origin, pts, axis, level, values):
    """Ordinate dimensions (ISO 129-1 9.3) from an origin marked 0: from each point an extension line to the level,
    its value written along the line beyond it; labels of near points spread apart both ways, joined by a short
    jog; points sharing a position give one value."""
    k = 0 if axis == "x" else 1
    items = {}
    for p, v in zip(pts, values):
        items.setdefault(round(p[k], 3), (p, v))
    rows = [(origin[k], origin, "0")] + sorted((c, p, v) for c, (p, v) in items.items() if abs(c - origin[k]) > 1e-6)
    rows.sort(key=lambda r: r[0])
    lab = [r[0] for r in rows]
    step = 4.2
    for _it in range(50):           # spread to at least step apart, keeping the order, centred on the points
        moved = False
        for i in range(1, len(lab)):
            if lab[i] - lab[i - 1] < step - 1e-9:
                push = (step - (lab[i] - lab[i - 1])) / 2
                lab[i - 1] -= push
                lab[i] += push
                moved = True
        if not moved:
            break
    for (c, p, v), lp in zip(rows, lab):
        if axis == "x":
            sgn = 1 if level > p[1] else -1
            jog = level - sgn * 3.0
            sh.line((c, p[1] + sgn * 1.0), (c, jog), W_THIN)
            sh.line((c, jog), (lp, level), W_THIN)
            sh.text(lp + 0.9, level + sgn * 0.8, v, 2.5, "left" if sgn > 0 else "right", rotate=90)
        else:
            sgn = 1 if level > p[0] else -1
            jog = level - sgn * 3.0
            sh.line((p[0] + sgn * 1.0, c), (jog, c), W_THIN)
            sh.line((jog, c), (level, lp), W_THIN)
            sh.text(level + sgn * 0.8, lp, v, 2.5, "left" if sgn > 0 else "right", valign="mid")
    sh.flush()


def stack_dims(sh, assy, views, sides):
    """A build-up section (spec 'stack': D-147 (2)): the layer faces across it as ordinates from its lowest face,
    on its right, read from the cut faces of the assembly's parts (true mm)."""
    out = []
    for sv in extra_views(views):
        if not sv.spec.get("stack"):
            continue
        axis = sv.spec.get("stack_along", "y")
        k = 1 if axis == "y" else 0
        ext = {}
        for i, loop in sv.hatch:
            it = assy.occs[i].item
            if it.ref:
                continue
            lo = min(p.bbox()[k] for p in loop)
            hi = max(p.bbox()[k + 2] for p in loop)
            a, b = ext.get(it, (lo, hi))
            ext[it] = (min(a, lo), max(b, hi))
        cuts = sorted({round(c, 3) for lo, hi in ext.values() for c in (lo, hi)})
        if len(cuts) < 2:
            continue
        x0, y0, x1, y1 = sv.box()
        if axis == "y":
            pts = [(x1, sv.S((0.0, c))[1]) for c in cuts]
            org = pts[0]
            level = x1 + sides[sv.name].dims["right"] + 12.0
        else:
            pts = [(sv.S((c, 0.0))[0], y1) for c in cuts]
            org = pts[0]
            level = y1 + sides[sv.name].dims["up"] + 12.0
        vals = [fmt(c - cuts[0], 2) for c in cuts]
        draw_ordinates(sh, org, pts[1:], axis, level, vals[1:])
        sides[sv.name].dims["right" if axis == "y" else "up"] += 12.0 + 4.0 + max(sh.text_width(v_, 2.5) for v_ in vals)
        out.append({"view": sv.name, "axis": axis, "faces": cuts, "values": vals})
    return out


# ------------------------------------------------------------------ read-back


TOL_TIP = 0.02          # paper mm: a balloon's tip where its 3D point projects
TOL_ON = 0.05           # true mm: a balloon's 3D point in or on its part's solid


def _join(lines):
    """Wrapped lines back into one string: a word broken after '-', '_' or '/' joins without a space; a line
    that ends in a free-standing ' -' (a separator) joins with one."""
    out = ""
    for ln in lines:
        if not out:
            out = ln
        elif out[-1] in "-_/" and not out.endswith(" -"):
            out += ln
        else:
            out += " " + ln
    return " ".join(out.split())


def table_text(page, data):
    """The parts table as the PDF's text gives it: {item number: (mark, [cell text per column])}, each cell's wrapped
    lines joined (a line broken after '-', '_' or '/' joins without a space)."""
    import readback
    xs = data["table"]["x"]
    yt, yb = data["table"]["y_top"], data["table"]["y_bot"]
    spans = [b for b in readback.text_boxes(page, data["sheet_h"])
             if xs[0] - 0.5 <= (b[0] + b[2]) / 2 <= xs[-1] + 0.5 and yb - 0.5 <= (b[1] + b[3]) / 2 <= yt + 0.5]
    col = lambda b: next((k for k in range(len(xs) - 1) if xs[k] <= (b[0] + b[2]) / 2 <= xs[k + 1]), None)
    out = {}
    for r in data["table"]["rows"]:
        top, bot = r["top"], r["bottom"]
        cells = []
        for c in range(len(xs) - 1):
            ls = sorted([b for b in spans if col(b) == c and bot < (b[1] + b[3]) / 2 < top],
                        key=lambda b: -(b[1] + b[3]) / 2)
            cells.append(_join([b[4] for b in ls]))
        m = re.match(r"^(\d+)(\*?)$", cells[0])
        if not m:
            out[-r["no"]] = (False, cells)
            continue
        out[int(m.group(1))] = (m.group(2) == "*", cells)
    return out


def _solids_by_pn(step_path):
    """{part number: its solids in the file's top coordinates}. A sub-assembly's number owns every solid under it
    (a D-120 welded frame's members, a cassette's parts), as drawing takes a sub-assembly as one item; a part's
    bodies without names of their own belong to it."""
    _doc, st = _xcaf(step_path)
    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    out = {}

    def walk(lab, loc, names):
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)), names + [_label_name(ref) or _label_name(c)])
            return
        shape = st.GetShape_s(lab)
        if not loc.IsIdentity():
            shape = shape.Moved(loc)
        sol = _solids_of(shape)
        for pn in {geom.part_number_of(nm) for nm in names} - {None}:
            out.setdefault(pn, []).extend(sol)

    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        walk(lab, TopLoc_Location(), [_label_name(lab)])
    return out


def _in_or_on(solids, p, tol=TOL_ON):
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    for s in solids:
        c = BRepClass3d_SolidClassifier(s, gp_Pnt(*p), tol)
        if c.State() in (TopAbs_IN, TopAbs_ON):
            return True
    return False


def _arrow_or_dot_at(page, sheet_h, tip, end):
    """True when the PDF has a filled arrowhead with its point at tip, or a filled dot centred there."""
    from sheet import MM as _MM
    for d in page.get_drawings():
        if not d.get("fill"):
            continue
        pts = []
        for it in d["items"]:
            if it[0] == "l":
                pts += [it[1], it[2]]
            elif it[0] == "c":
                pts += [it[1], it[4]]
        pts = [(p.x / _MM, sheet_h - p.y / _MM) for p in pts]
        if not pts:
            continue
        if end == "arrow" and any(math.dist(p, tip) < TOL_TIP for p in pts):
            return True
        if end == "dot":
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            if math.dist((cx, cy), tip) < 0.05:
                return True
    return False


def check(pdf_path):
    """Read an assembly sheet back against its STEP and parts list, independently of how it was drawn: every
    table row against the list's rows under the assembly (item order, number, name, quantity, material, finish,
    word for word); every balloon's number against the table, its part under the assembly in the STEP's tree (the
    repo's own reader), its tip where its 3D point projects through its view, an arrowhead or dot drawn there, and
    that point in or on the part's solid (within 0.05 mm); every item the STEP has carries a balloon; the
    interface ordinates against the STEP; no text touching text or an outline and no line through a text;
    Creator drawgen, CREATED BY and author Autonomous, no maker line, and what the mechanical check reads.
    Returns (failures, stats)."""
    import fitz
    import readback
    doc = fitz.open(pdf_path)
    page = doc[0]
    data = readback.read_data(doc)
    fails = []
    stats = {"rows": 0, "balloons": 0, "interfaces": 0}
    if data.get("kind") != "assembly":
        return ["not an assembly sheet (no kind 'assembly' in its drawing data)"], stats
    step = os.path.join(inputs.REPO, [s_ for s_ in data["sources"] if s_["role"] == "STEP"][0]["path"])
    lst = os.path.join(inputs.REPO, [s_ for s_ in data["sources"] if s_["role"] == "parts list"][0]["path"])
    pn = data["pn"]
    # 1. the table against the list
    keys = {pn} | set(data.get("parent_keys", ()))
    with open(lst, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if keys & {x.strip() for x in (r.get("parent") or "").split("|")}]
    tab = table_text(page, data)
    if sorted(tab) != list(range(1, len(rows) + 1)):
        fails.append("the table's items %s are not 1 to %d (the list's rows under %s)" % (sorted(tab), len(rows), pn))
    for n, r in enumerate(rows, 1):
        if n not in tab:
            continue
        stats["rows"] += 1
        u = unit_of(r)
        want = [str(n), (r.get("part_number") or "").strip(), (r.get("name") or "").strip(),
                qty_text(r.get("qty_per_parent")) + ((" " + u) if u else ""),
                (r.get("material") or "").strip() or "-", (r.get("finish") or "").strip() or "-"]
        got = tab[n][1]
        for k, (w, g) in enumerate(zip(want, got)):
            if k == 0:
                continue
            if " ".join(w.split()) != g:
                fails.append("table item %d %s: '%s' where the list has '%s'" % (n, COLS[k][0], g[:60], w[:60]))
    # 2. balloons
    s_f = _stepfile().StepFile(step)
    prods = {p_["pd"]: p_ for p_ in s_f.products()}
    occ = s_f.occurrences()
    kids = {}
    for o in occ:
        kids.setdefault(o["parent"], []).append(o["child"])
    under = set()
    for pd, p_ in prods.items():
        if p_["part_number"] == pn or geom.part_number_of(p_["name"]) == pn:
            stack = [pd]
            while stack:
                c = stack.pop()
                for ch in kids.get(c, []):
                    q = prods.get(ch, {})
                    under.add(geom.part_number_of(q.get("part_number", "")) or geom.part_number_of(q.get("name", "")))
                    stack.append(ch)
    views = {v["name"]: v for v in data["views"]}
    solids = _solids_by_pn(step)
    ballooned = set()
    for b in data.get("balloons", []):
        stats["balloons"] += 1
        n, bpn = b["no"], b["pn"]
        if n not in tab:
            fails.append("balloon %d: no table row %d" % (n, n))
        elif tab[n][1][1] != bpn:
            fails.append("balloon %d names %s, its table row %s" % (n, bpn, tab[n][1][1]))
        if bpn not in under:
            fails.append("balloon %d: %s is not a part of %s in %s" % (n, bpn, pn, inputs.rel(step)))
        v = views.get(b["view"])
        t3 = tuple(b["tip3d"])
        S = (v["off"][0] + v["scale"] * vdot(t3, v["x"]), v["off"][1] + v["scale"] * vdot(t3, v["y"]))
        if math.dist(S, b["tip"]) > TOL_TIP:
            fails.append("balloon %d: its tip is %.3f mm from where its point projects" % (n, math.dist(S, b["tip"])))
        if not _arrow_or_dot_at(page, data["sheet_h"], tuple(b["tip"]), b["end"]):
            fails.append("balloon %d: no %s drawn at its tip" % (n, "arrowhead" if b["end"] == "arrow" else "dot"))
        if not _in_or_on(solids.get(bpn, []), t3):
            fails.append("balloon %d: its point (%.2f, %.2f, %.2f) is not on %s in the STEP" % ((n,) + t3 + (bpn,)))
        if v["kind"] == "section" and v.get("cut") and bpn not in data.get("unhatched", ()):
            pt, nr = v["cut"]["point"], v["cut"]["normal"]
            if vdot(vsub(t3, pt), nr) > TOL_ON:
                fails.append("balloon %d: its point lies in front of section %s's plane" % (n, v.get("letter")))
        ballooned.add(bpn)
        txt = [t for t in readback.text_boxes(page, data["sheet_h"]) if t[4] == str(n) and
               math.dist(((t[0] + t[2]) / 2, (t[1] + t[3]) / 2), tuple(b["centre"])) < 1.5]
        if not txt:
            fails.append("balloon %d: its number isn't written in its circle" % n)
    for n, (mark, cells) in tab.items():
        if not mark and cells[1] not in ballooned:
            fails.append("item %d %s is in the STEP but has no balloon" % (n, cells[1]))
        if mark and cells[1] in ballooned:
            fails.append("item %d %s is marked as not modelled but has a balloon" % (n, cells[1]))
        if not mark and cells[1] not in under:
            fails.append("item %d %s has no * but the STEP has no %s under %s" % (n, cells[1], cells[1], pn))
        if mark and cells[1] in under:
            fails.append("item %d %s is marked as not in the STEP, but the STEP has it" % (n, cells[1]))
    # 3. interface ordinates, measured again from the STEP
    for g in data.get("interfaces", []):
        v = views[g["view"]]
        ax = v["x"] if g["axis"] == "x" else v["y"]
        o3 = tuple(g["origin3d"])
        for p_ in g["points"]:
            stats["interfaces"] += 1
            c3 = tuple(p_["at3d"])
            sol = solids.get(p_["pn"], [])
            if not any(all(bx[k] - TOL_ON <= c3[k] <= bx[k + 3] + TOL_ON for k in range(3)) for bx in
                       [box_of([s_]) for s_ in sol]):
                fails.append("interface point of %s at (%.2f, %.2f, %.2f) is outside it" % ((p_["pn"],) + c3))
            want = abs(vdot(vsub(c3, o3), ax))
            if abs(abs(float(p_["value"])) - want) > TOL_ON:
                fails.append("interface value %s for %s, the STEP gives %.2f" % (p_["value"], p_["pn"], want))
    text = "\n".join(pg.get_text() for pg in doc)
    up = text.upper()
    for need, pat in (("UNITS: mm", r"UNITS:\s*MM\b"), ("MATERIAL", r"MATERIAL:"), ("FINISH", r"FINISH:"),
                      ("TOLERANCE", r"TOLERANCE")):
        if not re.search(pat, up):
            fails.append("text lacks %s" % need)
    if " " in text or "­" in text:
        fails.append("the text layer has non-breaking spaces or soft hyphens (search breaks)")
    meta = doc.metadata or {}
    if meta.get("creator") != "drawgen":
        fails.append("PDF Creator is not drawgen")
    if meta.get("author") != "Autonomous":
        fails.append("PDF author is not Autonomous")
    if not re.search(r"CREATED BY\s+Autonomous\b", text):
        fails.append("the title block's CREATED BY is not Autonomous")
    for pg, phrase in readback.note_makers(doc):
        fails.append("sheet %d: a note names a maker ('%s')" % (pg, phrase))
    for pg, what in readback.clashes(doc):
        fails.append("sheet %d: %s" % (pg, what))
    return fails, stats


# ------------------------------------------------------------------ text measured as printed


_FONT = {}


def tw(sh, s, size, bold=False):
    """The printed width (sheet mm) of s at letter height size: fitz.Font's measure, which matches the PDF's own
    span boxes (fitz.get_text_length under-measures Ø and µ in the built-in Helvetica)."""
    from sheet import CAP, MM
    if _latin(s) or not sh.fonts["bold" if bold else "reg"]:
        key = "hebo" if bold else "helv"
        import fitz
        f = _FONT.get(key) or _FONT.setdefault(key, fitz.Font(key))
        return f.text_length(s, fontsize=size / CAP * MM) / MM
    return sh.text_width(s, size, bold)


def wrap2(sh, s, size, width, bold=False):
    """Lines of s no wider than width as printed; a word wider than a line breaks after '-', '_' or '/' (else
    between letters), never cut short."""
    words = []
    for wd in s.split(" "):
        if tw(sh, wd, size, bold) <= width:
            words.append(wd)
            continue
        cur = ""
        for ch in wd:
            if cur and tw(sh, cur + ch, size, bold) > width:
                cut = max(cur.rfind("-"), cur.rfind("_"), cur.rfind("/"))
                if cut > 0:
                    words.append(cur[:cut + 1])
                    cur = cur[cut + 1:]
                else:
                    words.append(cur)
                    cur = ""
            cur += ch
        if cur:
            words.append(cur)
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip() if cur else wd
        if cur and tw(sh, t, size, bold) > width:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def paragraph2(sh, x, y, s, size, width, lead=1.6):
    for ln in wrap2(sh, s, size, width):
        sh.text(x, y, ln, size)
        y -= size * lead
    return y


def draw_table(sh, x, y_top, cols, rows, size=2.5, title=None, title_size=3.5):
    """A ruled table from its top-left corner down (ISO 7573 parts list): a title, a header and the rows, each cell
    wrapped to its column as printed (never cut short). Returns (y of its bottom, [(top, bottom) per row])."""
    row_h = size * 2.6
    lead = size * 1.65
    total = sum(c[1] for c in cols)
    y = y_top
    if title:
        tl = wrap2(sh, title, title_size, total - 3.0, bold=True)
        th = len(tl) * title_size * 1.65 + 2.2
        sh.rect(x, y - th, total, th, W_THIN)
        ty = y - 1.2 - title_size
        for ln in tl:
            sh.text(x + 1.5, ty, ln, title_size, bold=True)
            ty -= title_size * 1.65
        y -= th
    top = y
    hl = [wrap2(sh, h, size, w - 2.4, bold=True) for h, w, _al in cols]
    hh = max(row_h, max(len(x_) for x_ in hl) * size * 1.6 + (row_h - size * 1.6))
    sh.rect(x, y - hh, total, hh, W_THIN)
    cx = x
    for (h, w, _al), ls in zip(cols, hl):
        y0 = y - hh / 2 + (len(ls) - 1) * size * 0.8
        for k, ln in enumerate(ls):
            sh.text(cx + w / 2, y0 - k * size * 1.6, ln, size, "center", valign="mid", bold=True)
        cx += w
    y -= hh
    spans = []
    for r in rows:
        cells = [wrap2(sh, str(v), size, w - 2.4) if v not in (None, "") else [""] for (_h, w, _al), v in zip(cols, r)]
        n = max(len(c) for c in cells)
        hgt = row_h + (n - 1) * lead
        sh.rect(x, y - hgt, total, hgt, W_THIN)
        cx = x
        for (_h, w, al), ls in zip(cols, cells):
            for k, ln in enumerate(ls):
                yy = y - row_h / 2 - k * lead
                if al == "c":
                    sh.text(cx + w / 2, yy, ln, size, "center", valign="mid")
                else:
                    sh.text(cx + 1.2, yy, ln, size, "left", valign="mid")
            cx += w
        spans.append((y, y - hgt))
        y -= hgt
    cx = x
    for _h, w, _al in cols[:-1]:
        cx += w
        sh.line((cx, top), (cx, y), W_THIN)
    sh.flush()
    return y, spans


def table_height(sh, cols, rows, size=2.5, title=None, title_size=3.5):
    total = sum(c[1] for c in cols)
    h = 0.0
    if title:
        h += len(wrap2(sh, title, title_size, total - 3.0, bold=True)) * title_size * 1.65 + 2.2
    hl = [wrap2(sh, c[0], size, c[1] - 2.4, bold=True) for c in cols]
    h += max(size * 2.6, max(len(x_) for x_ in hl) * size * 1.6 + size)
    for r in rows:
        n = max(len(wrap2(sh, str(v), size, w - 2.4)) if v not in (None, "") else 1 for (_h, w, _al), v in zip(cols, r))
        h += size * 2.6 + (n - 1) * size * 1.65
    return h


# ------------------------------------------------------------------ cutting planes (ISO 128-40)


def section_line(sh, p, q, letter, look):
    """A cutting plane from p to q: a thin chain line, thick at its ends, an arrow at each end pointing the way
    the section looks, and the letter beside each arrow where it touches no line and no text (it moves out along
    the arrow until it does). Returns the letters' boxes, or None when no free place was found."""
    from sheet import DASH_CTR
    sh.line(p, q, 0.18, DASH_CTR)
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    boxes = []
    for e, sgn in ((p, 1), (q, -1)):
        sh.line(e, (e[0] + sgn * ux * 6, e[1] + sgn * uy * 6), 0.7)
        tip = (e[0] + look[0] * 7, e[1] + look[1] * 7)
        sh.line(e, (tip[0] - look[0] * 2.5, tip[1] - look[1] * 2.5), W_THIN)
        sh.arrow(tip, look, 3.0, 1.1)
        sh.flush()
        placed = None
        for k in range(0, 12):
            for side in (-sgn, sgn):
                cx = tip[0] - side * ux * (3.2 + k * 1.5) + look[0] * 1.0
                cy = tip[1] - side * uy * (3.2 + k * 1.5) + look[1] * 1.0
                b = sh.text_box(cx, cy, letter, 3.5, "center", bold=True, valign="mid")
                if sh.is_free((b[0] - 0.4, b[1] - 0.4, b[2] + 0.4, b[3] + 0.4)):
                    placed = (cx, cy, b)
                    break
            if placed:
                break
        if not placed:
            return None
        sh.text(placed[0], placed[1], letter, 3.5, "center", bold=True, valign="mid")
        boxes.append(placed[2])
    sh.flush()
    return boxes


# ------------------------------------------------------------------ entries and command line


def assemblies():
    """{pn: (team, entry)} from each team's tools/drawgen/teams/<team>.py ASSEMBLIES (D-139: each team keeps its
    own entries); a number listed twice is an error."""
    import glob as _glob
    import importlib.util as _ilu
    out = {}
    for path in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "teams", "*.py"))):
        team = os.path.splitext(os.path.basename(path))[0]
        if team.startswith("_"):
            continue
        sp = _ilu.spec_from_file_location("drawgen_asm_" + team, path)
        m = _ilu.module_from_spec(sp)
        sp.loader.exec_module(m)
        for pn, conf in getattr(m, "ASSEMBLIES", {}).items():
            if pn in out:
                raise ValueError("drawgen: assembly %s is listed twice (%s and %s)" % (pn, team, out[pn][0]))
            out[pn] = (team, conf)
    return out


def main(argv=None):
    """generate PN... [--out DIR]: draw each listed assembly into v2/02-Drawings/<team>/ (or DIR) and read it back;
    check PDF...: read sheets back."""
    import argparse
    ap = argparse.ArgumentParser(description="drawgen assembly sheets")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("pns", nargs="*")
    g.add_argument("--all", action="store_true")
    g.add_argument("--out", default=None)
    c = sub.add_parser("check")
    c.add_argument("pdfs", nargs="+")
    a = ap.parse_args(argv)
    bad = 0
    if a.cmd == "generate":
        reg = assemblies()
        for pn in (list(reg) if a.all else a.pns):
            if pn not in reg:
                print("%s: no assembly entry in tools/drawgen/teams/" % pn)
                bad += 1
                continue
            team, entry = reg[pn]
            try:
                final, rep = generate(pn, team, entry, a.out or os.path.join(inputs.DRAWINGS, team))
            except NotDrawable as e:
                print("%s: not drawn: %s" % (pn, e))
                bad += 1
                continue
            fails, st = check(final)
            print("%s: %s; read-back %s (%d table rows, %d balloons, %d interface sizes)" % (
                pn, inputs.rel(final) if final.startswith(inputs.REPO) else final, "PASS" if not fails else "FAIL",
                st["rows"], st["balloons"], st["interfaces"]))
            for f in fails:
                print("  - " + f)
            bad += bool(fails)
    else:
        for p in a.pdfs:
            fails, _st = check(p)
            print("%s: %s" % (os.path.basename(p), "PASS" if not fails else "FAIL"))
            for f in fails:
                print("  - " + f)
            bad += bool(fails)
    return 1 if bad else 0


if __name__ == "__main__":
    import sys as _sys
    _sys.exit(main())
