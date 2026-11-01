"""GA sheet 1: the whole pod, 100000, as one assembly sheet drawn from the teams' STEPs (D-158; the PM's rulings of
2026-11-01). Run it in drawgen's environment (tools/drawgen/run.sh makes it):

    <venv>/bin/python tools/drawgen/pod_assembly.py generate      # v2/02-Drawings/00-General-Assembly/, read back
    <venv>/bin/python tools/drawgen/pod_assembly.py check v2/02-Drawings/00-General-Assembly/100000_*_DWG.pdf

The pod has no STEP of its own. Its parts are the teams' assembly STEPs, all in pod coordinates: every STEP under
v2/03-Manufacturing, the skeleton's folder left out, whose top part has an assembly number (conventions section 6),
the set the whole-pod mechanical check reads (tools/checks/run_fusion_checks.py, pick_steps). Each file's top part is
drawn as part of its first-level assembly in the master BOM (210101 under 210000 WALL, 350001 under 350000 FRONT -
DECOR), so the items are the pod's first-level assemblies; the parts table is the master BOM's first-level rows that
have a part number, less the entry's leave_out (the packaging 910000 isn't on the pod as it stands). A first-level row
no STEP has yet gets its row with a * and no balloon, as the assembly mode does.

The sheet itself is the assembly mode's (tools/drawgen/assembly.py, the Air Engineer's): its views, sections, balloons,
table, sizes, notes and title block, through make()'s hook for an assembly built elsewhere. This file adds the reading
of the pod and its own read-back, against the same STEPs and the master BOM (assembly.check reads one STEP and one
team list). The entry is POD in tools/drawgen/teams/ga.py. The drawing takes the skeleton's revision (the pod's own
number, 100000, revised as the skeleton is) and the date of its newest STEP.
"""

import csv
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import assembly as A  # noqa: E402
import geom  # noqa: E402
import inputs  # noqa: E402
from compose import NotDrawable  # noqa: E402
from geom import vdot, vsub  # noqa: E402
from sheet import W_THIN  # noqa: E402

POD_PN = "100000"
TEAM = "ga"                               # the GA's folder under v2/02-Drawings is 00-General-Assembly
MASTER_REL = "v2/04-BOM/100000_P01_POD-MASTER_BOM.csv"
OUT_REL = "v2/02-Drawings/00-General-Assembly"
SKELETON_DIR = "skeleton"
ROLLUP_REL = "v2/05-Engineering/layout-study/weight-rollup.md"
ROLLUP_ROW = "Pod as shipped"            # the roll-up's total: every part on the pod, packaging not in it
CODE_RE = re.compile(r"^(L[12]|R[12]|B[1-4]|C[1-3])\s")      # guideline 5.1's position codes (skeleton bodies)
TOL_SIZE = 0.05                          # true mm: a clear size measured again
BEAM_HALF = 0.05                         # true mm: half the side of a thin beam's square section
SIZE_TEXT = 2.5                          # paper mm: the clear sizes' text
TAG_TEXT = 3.5                           # paper mm: the position codes' text


def _checks(name):
    """A module of the repo's own checks (tools/checks): stepfile (the STEP reader without OCC), common."""
    p = os.path.join(inputs.REPO, "tools", "checks")
    if p not in sys.path:
        sys.path.insert(0, p)
    return __import__(name)


def pod_steps(root=None):
    """The whole pod's STEPs, sorted: every STEP under v2/03-Manufacturing, the skeleton's folder left out, whose top
    part has an assembly number (conventions section 6), as the whole-pod check picks them."""
    root = root or inputs.MANUF
    stepfile, common = _checks("stepfile"), _checks("common")
    out = []
    for p in sorted(glob.glob(os.path.join(root, "*", "*.step")) + glob.glob(os.path.join(root, "*", "*.stp"))):
        if os.path.basename(os.path.dirname(p)) == SKELETON_DIR:
            continue
        _c, tops = stepfile.StepFile(p).usage_counts()
        if any(common.pn_class(t) == "assembly" for t in tops):
            out.append(p)
    return out


def master_tree(path):
    """(the pod's row, [first-level rows that have a part number], {part number: the part number of its first-level
    assembly}) from the master BOM, whose rows run in tree order with their level (0 the pod)."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or rows[0].get("level") != "0" or (rows[0].get("part_number") or "").strip() != POD_PN:
        raise NotDrawable("%s: its first row is not the pod %s at level 0" % (inputs.rel(path), POD_PN))
    stack, first, up = [], [], {}
    for r in rows:
        lv = int(r["level"])
        pn = (r.get("part_number") or "").strip()
        stack = stack[:lv] + [pn]
        if lv == 1 and pn:
            first.append(r)
        if lv >= 1 and pn and len(stack) > 1 and stack[1]:
            up.setdefault(pn, stack[1])
    return rows[0], first, up


def skeleton_rev(root=None):
    """The skeleton STEP's revision (PN_REV_NAME_STEP.step under the skeleton's folder), newest when several."""
    root = root or inputs.MANUF
    revs = []
    for p in glob.glob(os.path.join(root, SKELETON_DIR, "*_STEP.step")):
        m = inputs.NAME_RE.match(os.path.basename(p))
        if m and m.group(1) == POD_PN:
            revs.append(m.group(2))
    if not revs:
        raise NotDrawable("no skeleton STEP %s_*_STEP.step under %s" % (POD_PN, inputs.rel(os.path.join(root,
                                                                                                      SKELETON_DIR))))
    return sorted(revs)[-1]


def _step_date(path):
    with open(path, encoding="latin-1") as fh:
        m = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})", fh.read(4000))
    return (m.group(1), m.group(2)) if m else ("", "")


def top_parts(path):
    """[(part number, product name, solids)] for each top part of a team STEP (its free shapes), solids in the
    file's top coordinates (the pod system)."""
    from OCP.TDF import TDF_LabelSequence
    _doc, st = A._xcaf(path)
    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    out = []
    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        name = A._label_name(lab)
        out.append((geom.part_number_of(name), name, A._solids_of(st.GetShape_s(lab))))
    return out


# ------------------------------------------------------------------ what the pod's sheet adds: its sources


def rollup_mass(path=None):
    """(the pod's mass in kg as the weight roll-up writes it, the file): its 'Pod as shipped' row, the sum of every
    part on the pod as it stands in the room, packaging not in it."""
    path = path or os.path.join(inputs.REPO, ROLLUP_REL)
    if not os.path.exists(path):
        raise NotDrawable("no weight roll-up at %s" % inputs.rel(path))
    pat = re.compile(r"^\|\s*\*\*%s\*\*\s*\|\s*\*\*([0-9]+(?:\.[0-9]+)?)\*\*\s*\|" % re.escape(ROLLUP_ROW))
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                return m.group(1), path
    raise NotDrawable("%s has no '%s' row" % (inputs.rel(path), ROLLUP_ROW))


def skeleton_step(root=None):
    """The skeleton's STEP at its newest revision."""
    root = root or inputs.MANUF
    rev = skeleton_rev(root)
    ps = sorted(glob.glob(os.path.join(root, SKELETON_DIR, "%s_%s_*_STEP.step" % (POD_PN, rev))))
    if not ps:
        raise NotDrawable("no skeleton STEP %s_%s_*_STEP.step" % (POD_PN, rev))
    return ps[-1]


_LEAVES = {}


def named_leaves(path):
    """[(part numbers from the top part down to the body, the body's own label, solid)] for every body of a STEP, in
    the file's top coordinates (the pod system). Read once per file and modification time."""
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.TopLoc import TopLoc_Location
    key = (os.path.abspath(path), os.path.getmtime(path))
    if key in _LEAVES:
        return _LEAVES[key]
    _doc, st = A._xcaf(path)
    out = []

    def walk(lab, loc, chain, name):
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = TDF_Label()
                st.GetReferredShape_s(c, ref)
                nm = A._label_name(ref) or A._label_name(c) or ""
                pn = geom.part_number_of(nm)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)), chain + ((pn,) if pn else ()), nm)
            return
        shape = st.GetShape_s(lab)
        if not loc.IsIdentity():
            shape = shape.Moved(loc)
        for s in A._solids_of(shape):
            out.append((chain, name, s))

    tops = TDF_LabelSequence()
    st.GetFreeShapes(tops)
    for i in range(1, tops.Length() + 1):
        lab = tops.Value(i)
        nm = A._label_name(lab) or ""
        pn = geom.part_number_of(nm)
        walk(lab, TopLoc_Location(), (pn,) if pn else (), nm)
    _LEAVES[key] = out
    return out


def skeleton_codes(path=None):
    """{position code: its envelope's box (x0, y0, z0, x1, y1, z1)} from the skeleton STEP's bodies named by code
    (guideline 5.1: L1 to R2 the side panels, B1 to B4 the back, C1 to C3 the ceiling); the cassettes' bodies
    (L1-CASS ...) are not positions."""
    out = {}
    for _chain, name, s in named_leaves(path or skeleton_step()):
        m = CODE_RE.match(name or "")
        if m:
            b = A.box_of([s])
            if m.group(1) in out:
                o = out[m.group(1)]
                b = tuple(min(o[k], b[k]) for k in range(3)) + tuple(max(o[k], b[k]) for k in range(3, 6))
            out[m.group(1)] = tuple(b)
    return out


# ------------------------------------------------------------------ clear sizes: free stretches through the solids


def _obox(shape):
    """A shape's tight box (x0, y0, z0, x1, y1, z1), true mm."""
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    b = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, b, False, False)
    return b.Get()


class Body:
    """One body of the pod for the clear sizes: its first-level assembly, the part numbers from its file's top part
    down to it, the solid and its box."""

    def __init__(self, item, chain, solid):
        self.item, self.chain, self.solid = item, tuple(chain), solid
        self.box = _obox(solid)

    def named(self, pns):
        return any(p in self.chain for p in pns)


def pod_bodies(steps, up):
    """[Body] for every body of the pod's STEPs, under its first-level assembly (up: the master BOM's tree)."""
    out = []
    for p in steps:
        for chain, _name, s in named_leaves(p):
            item = up.get(chain[0]) if chain else None
            if item:
                out.append(Body(item, chain, s))
    return out


def turned_door(bodies, spec):
    """The bodies with the door unit's turned open about its hinge pivot (a vertical axis through spec['pivot'],
    opening outward, toward -Y, by spec['angle'] degrees), the bodies spec['left_out'] names left out (the hinges'
    HOLD spaces are boxes, not hinges). Raises NotDrawable when the open door runs into another body."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(spec["pivot"][0], spec["pivot"][1], 0.0), gp_Dir(0, 0, 1)),
                  math.radians(-float(spec["angle"])))     # +X (the leaf, hinge to latch) turns to -Y: outward
    fixed = [b for b in bodies if b.chain[:1] != (spec["unit"],)]
    turned = [Body(b.item, b.chain, BRepBuilderAPI_Transform(b.solid, t, True).Shape()) for b in bodies
              if b.chain[:1] == (spec["unit"],) and not b.named(spec.get("left_out", ()))]
    if not turned:
        raise NotDrawable("no door unit %s in the pod's STEPs" % spec["unit"])
    for m in turned:
        for f in fixed:
            if any(m.box[k + 3] < f.box[k] or m.box[k] > f.box[k + 3] for k in range(3)):
                continue
            com = BRepAlgoAPI_Common(m.solid, f.solid).Shape()
            if A._has_faces(com):
                g = GProp_GProps()
                BRepGProp.VolumeProperties_s(com, g)
                if g.Mass() > 1.0:
                    raise NotDrawable("the door open %g deg runs into %s (%.0f mm3 of %s)" % (
                        spec["angle"], f.chain[-1], g.Mass(), m.chain[-1]))
    return fixed + turned


AXES = "xyz"


def free_run(bodies, along, start, beam=None):
    """The free stretch along pod axis `along` ('x', 'y' or 'z') through point `start`, for a beam whose section is
    beam ({axis: (lo, hi)} for the other two axes; a square of side 2 x BEAM_HALF round start where not given):
    {"lo": (value, Body, point) or None, "hi": ...}, each end the nearest material of any body in the beam, its point
    the centre of that body's part in the beam moved onto the end. Raises ValueError naming a body that sits across
    start (the beam isn't free there)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    k = AXES.index(along)
    lo = [start[i] - BEAM_HALF for i in range(3)]
    hi = [start[i] + BEAM_HALF for i in range(3)]
    lo[k], hi[k] = start[k] - 6000.0, start[k] + 6000.0
    for a, (u, v) in (beam or {}).items():
        lo[AXES.index(a)], hi[AXES.index(a)] = float(u), float(v)
    box = BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()
    ends = {"lo": None, "hi": None}
    c0 = start[k]
    for b in bodies:
        if any(b.box[i + 3] < lo[i] or b.box[i] > hi[i] for i in range(3)):
            continue
        com = BRepAlgoAPI_Common(b.solid, box).Shape()
        if not A._has_faces(com):
            continue
        cb = _obox(com)
        mid = [(cb[i] + cb[i + 3]) / 2 for i in range(3)]
        if cb[k + 3] <= c0 + 1e-6:
            if ends["lo"] is None or cb[k + 3] > ends["lo"][0]:
                mid[k] = cb[k + 3]
                ends["lo"] = (cb[k + 3], b, _on_body(com, mid))
        elif cb[k] >= c0 - 1e-6:
            if ends["hi"] is None or cb[k] < ends["hi"][0]:
                mid[k] = cb[k]
                ends["hi"] = (cb[k], b, _on_body(com, mid))
        else:
            raise ValueError("%s sits across %s %.1f" % (b.chain[-1] if b.chain else b.item, along, c0))
    return ends


def _on_body(shape, p):
    """The point of shape nearest p: the box's middle moved onto the end can be in air (an L or U profile: DL's
    stop 351103, the glass's seal 368003), so the end's point is taken on the body itself."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.gp import gp_Pnt
    d = BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(), shape)
    if not d.IsDone() or d.NbSolution() < 1:
        return tuple(p)
    q = d.PointOnShape2(1)
    return (q.X(), q.Y(), q.Z())


def floor_z(bodies, base_pn="110000"):
    """The room floor: the base's lowest point (its glides stand on it), Z 0 in the pod's axes."""
    zs = [b.box[2] for b in bodies if b.item == base_pn]
    if not zs:
        raise NotDrawable("no base %s in the pod's STEPs: no room floor" % base_pn)
    return min(zs)


def measure(bodies, spec, start, floor):
    """One clear size by spec at start: (value, lo point, hi point, lo part, hi part), or None when the ends aren't
    the parts the spec names (lo 'floor': nothing between the room floor and start)."""
    try:
        ends = free_run(bodies, spec["along"], start, spec.get("beam"))
    except ValueError:
        return None
    k = AXES.index(spec["along"])
    want_lo, want_hi = spec["ends"]
    if want_lo == ["floor"]:
        if ends["lo"] is not None or ends["hi"] is None:
            return None
        lo_v = floor
        lo_p = list(ends["hi"][2])
        lo_p[k] = floor
        lo = (lo_v, None, tuple(lo_p))
    else:
        lo = ends["lo"]
        if lo is None or not lo[1].named(want_lo):
            return None
    hi = ends["hi"]
    if hi is None or not hi[1].named(want_hi):
        return None

    def name(e, want):
        return "floor" if e[1] is None else next(p for p in want if p in e[1].chain)
    return hi[0] - lo[0], lo[2], hi[2], name(lo, want_lo), name(hi, want_hi)


class PodAssy(A.Assy):
    """The pod as the assembly mode's Assy: its items are the master BOM's first-level assemblies, each with the top
    parts of the team STEPs that fall under it."""

    kind = "pod"

    def __init__(self, pn, team, entry, step=None, master=None, steps=None):     # noqa: D107 (Assy's own fields)
        if pn != POD_PN:
            raise NotDrawable("%s: the pod sheet is %s" % (pn, POD_PN))
        # the entry's notes are a copy: extra() adds the measured ones for this sheet only
        self.pn, self.team, self.entry = pn, team, dict(entry, notes=list(entry.get("notes", ())))
        self.list_file = master or os.path.join(inputs.REPO, MASTER_REL)
        own, first, up = master_tree(self.list_file)
        self.up = up
        leave = set(entry.get("leave_out", ()))
        self.steps = list(steps) if steps is not None else pod_steps()
        if not self.steps:
            raise NotDrawable("%s: no team STEP under v2/03-Manufacturing" % pn)
        # the title block's MASS: the weight roll-up's pod (the master BOM's pod row sums only the listed parts)
        self.mass, self.rollup = rollup_mass()
        self.row = dict(own, mass_each_kg=self.mass)
        self.name = (own.get("name") or "").strip()
        self.name_vi = (own.get("name_vi") or "").strip()
        self.rev = entry.get("rev") or skeleton_rev()
        self.dwg_name = "%s_%s_%s_DWG" % (pn, self.rev, inputs.ascii_name(self.name))
        # the sheet's date is the newest STEP's (make() reads it from self.step's header)
        self.step = max(self.steps, key=lambda p: (_step_date(p), p))
        by_item, self.files = {}, {}
        for p in self.steps:
            for tpn, name, solids in top_parts(p):
                if tpn is None:
                    raise NotDrawable("%s: %s has a top part without a part number (%s)" % (pn, inputs.rel(p), name))
                item = up.get(tpn)
                if item is None:
                    raise NotDrawable("%s: %s's top part %s isn't under a first-level assembly in %s" % (
                        pn, inputs.rel(p), tpn, inputs.rel(self.list_file)))
                if item in leave:
                    raise NotDrawable("%s: %s's top part %s falls under %s, which the entry leaves out" % (
                        pn, inputs.rel(p), tpn, item))
                by_item.setdefault(item, []).append(A.Occ(item, name, solids))
                self.files.setdefault(item, []).append(inputs.rel(p))
        self.items = []
        for r in first:
            ipn = r["part_number"].strip()
            if ipn in leave:
                continue
            row = dict(r)
            row["qty_per_parent"] = row.get("qty_per_pod", "")   # the table's quantity: each per pod
            self.items.append(A.Item(ipn, row, by_item.get(ipn, [])))
        for n, it in enumerate(self.items, 1):
            it.no = n
        self.occs = [o for it in self.items for o in it.occs]
        self.count_notes = []

    def sources(self):
        """The sheet's sources: every STEP drawn, the master BOM, the skeleton STEP (the position codes) and the
        weight roll-up (the mass)."""
        sk = skeleton_step()
        return ([{"role": "STEP", "path": inputs.rel(p), "sha256_12": inputs.sha12(p)} for p in self.steps] +
                [{"role": "parts list", "path": inputs.rel(self.list_file), "sha256_12": inputs.sha12(self.list_file)},
                 {"role": "skeleton STEP", "path": inputs.rel(sk), "sha256_12": inputs.sha12(sk)},
                 {"role": "mass", "path": inputs.rel(self.rollup), "sha256_12": inputs.sha12(self.rollup),
                  "kg": self.mass}])

    # ---------------------------------------------------------------- assembly.make()'s hook: what only the pod has

    def extra(self, sh, views, sides):
        """What only the pod's sheet has, drawn after the interface sizes and before the balloons: the clear sizes
        (inside width, depth and height; the door's clear opening with the door open), each measured on the teams'
        STEPs as a free stretch through the pod's bodies and drawn where it is free; the position codes on their
        panels (from the skeleton STEP's bodies); and the notes giving them with their status and basis. Returns
        what the sheet's data keeps as "extra", which check() measures again."""
        e = self.entry
        bodies = pod_bodies(self.steps, self.up)
        floor = floor_z(bodies)
        door = e.get("door")
        opened = turned_door(bodies, door) if door else bodies
        out = {"floor_z": round(floor, 3), "door": dict(door) if door else None, "sizes": [], "codes": [],
               "floor_lines": [], "mass": {"kg": self.mass, "status": "calculation", "row": ROLLUP_ROW,
                                           "source": inputs.rel(self.rollup)}}
        got = {}
        for spec in e.get("clear", ()):
            rec = None
            for start in _starts(spec):
                m = measure(opened if spec.get("open") else bodies, spec, start, floor)
                if m is None:
                    continue
                rec = self._draw_size(sh, views, sides, spec, start, m, out) if spec.get("view") else \
                    _size_record(spec, start, m)
                if rec:
                    break
            if rec is None:
                raise NotDrawable("%s: no place where %s is measured between %s and %s and drawn clear" % (
                    self.pn, spec["name"], "/".join(spec["ends"][0]), "/".join(spec["ends"][1])))
            out["sizes"].append(rec)
            got[spec["name"]] = rec
        codes = skeleton_codes()
        for vname, names in e.get("codes", {}).items():
            av = views.get(vname)
            if av is None:
                raise NotDrawable("%s: position codes on %s, a view the sheet hasn't" % (self.pn, vname))
            for code in names:
                if code not in codes:
                    raise NotDrawable("%s: the skeleton STEP has no position %s" % (self.pn, code))
                rec = _place_tag(sh, av, code, codes[code])
                if rec is None:
                    raise NotDrawable("%s: no free place for the position code %s on %s" % (self.pn, code, vname))
                out["codes"].append(rec)
        e["notes"] += _extra_notes(e, got, out, self)
        out["notes"] = list(e["notes"])
        sh.flush()
        return out

    def _draw_size(self, sh, views, sides, spec, start, m, out):
        """Draw one clear size on its view; its record, or None when its value finds no free place there."""
        value, lo3, hi3, lo_pn, hi_pn = m
        av = views.get(spec["view"])
        if av is None:
            raise NotDrawable("%s: %s goes on %s, a view the sheet hasn't" % (self.pn, spec["name"], spec["view"]))
        lo3, hi3 = list(lo3), list(hi3)
        for a_, v_ in spec.get("draw_at", {}).items():
            lo3[AXES.index(a_)] = hi3[AXES.index(a_)] = float(v_)
        a, b = av.S(av.view.to2d(tuple(lo3))), av.S(av.view.to2d(tuple(hi3)))
        text = spec["label"] % A.fmt(value, 1)
        rec = _size_record(spec, start, m)
        rec.update({"view": av.name, "lo3d": [round(c, 4) for c in lo3], "hi3d": [round(c, 4) for c in hi3],
                    "text": text, "tips": [list(a), list(b)]})
        side = spec.get("outside") or spec.get("offset")
        if side:
            # a dimension with extension lines (sheet.dim_linear), its line `gap` beyond the farther point: outside
            # the view (beyond what the view's other sizes keep there) or offset inside it, where its text is free
            x0, y0, x1, y1 = av.box()
            k = 1 if side in ("up", "down") else 0
            sgn = -1.0 if side in ("down", "left") else 1.0
            far = min(a[k], b[k]) if sgn < 0 else max(a[k], b[k])
            tw = sh.text_width(text, SIZE_TEXT)
            if tw + 2 > abs(a[1 - k] - b[1 - k]):
                raise NotDrawable("%s: %s: its text doesn't fit between its arrows" % (self.pn, spec["name"]))
            if spec.get("outside"):
                edge = {"down": y0, "up": y1, "left": x0, "right": x1}[side]
                gaps = [abs(far - edge) + g + sides[av.name].dims[side] for g in (8.0, 12.0, 16.0, 20.0)]
            else:
                gaps = [6.0, 9.0, 12.0, 15.0, 20.0, 25.0, 30.0]
            for gap in gaps:
                ln = far + sgn * gap
                if k == 1:
                    tx, ty = (a[0] + b[0]) / 2, (ln - 0.8 - SIZE_TEXT if sgn < 0 else ln + 0.8)
                    tb = sh.text_box(tx, ty, text, SIZE_TEXT, "center")
                else:
                    tx, ty = (ln - 0.8 if sgn < 0 else ln + 0.8 + SIZE_TEXT), (a[1] + b[1]) / 2
                    tb = sh.text_box(tx, ty, text, SIZE_TEXT, "center", rotate=90)
                if sh.is_free(tb):
                    break
            else:
                return None
            for f in spec["ends"]:
                if f == ["floor"] and av.name not in [fl["view"] for fl in out["floor_lines"]]:
                    fl = _floor_line(sh, av, out["floor_z"])
                    if fl is None:
                        return None
                    out["floor_lines"].append(fl)
            sh.dim_linear(a, b, side, gap, text, SIZE_TEXT)
            if spec.get("outside"):
                edge = {"down": y0, "up": y1, "left": x0, "right": x1}[side]
                sides[av.name].dims[side] = abs(ln - edge) + SIZE_TEXT + 2.0
            rec.update({"text_at": [tx, ty], "rotate": 0 if k == 1 else 90, "side": side, "line_at": ln})
            return rec
        horiz = abs(a[1] - b[1]) < 1e-6
        if not horiz and abs(a[0] - b[0]) > 1e-6:
            raise NotDrawable("%s: %s isn't along the view's x or y" % (self.pn, spec["name"]))
        span = abs(b[0] - a[0]) if horiz else abs(b[1] - a[1])
        tw = sh.text_width(text, SIZE_TEXT)
        spot = None
        for t in (0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74, 0.18, 0.82):
            if horiz:
                cx, cy = a[0] + t * (b[0] - a[0]), a[1] + 0.8
                tb = sh.text_box(cx, cy, text, SIZE_TEXT, "center")
                inside = tb[0] >= min(a[0], b[0]) + 4.0 and tb[2] <= max(a[0], b[0]) - 4.0
            else:
                cx, cy = a[0] - 0.8, a[1] + t * (b[1] - a[1])
                tb = sh.text_box(cx, cy, text, SIZE_TEXT, "center", rotate=90)
                inside = tb[1] >= min(a[1], b[1]) + 4.0 and tb[3] <= max(a[1], b[1]) - 4.0
            if inside and span > tw + 10.0 and sh.is_free(tb):
                spot = (cx, cy)
                break
        if spot is None:
            return None
        for f in spec["ends"]:
            if f == ["floor"] and av.name not in [fl["view"] for fl in out["floor_lines"]]:
                fl = _floor_line(sh, av, out["floor_z"])
                if fl is None:
                    return None
                out["floor_lines"].append(fl)
        sh.line(a, b, W_THIN)
        sh.arrow(a, (a[0] - b[0], a[1] - b[1]))
        sh.arrow(b, (b[0] - a[0], b[1] - a[1]))
        sh.text(spot[0], spot[1], text, SIZE_TEXT, "center", rotate=0 if horiz else 90)
        rec.update({"text_at": list(spot), "rotate": 0 if horiz else 90})
        return rec


def _starts(spec):
    """The points a clear size is tried at, in order: its start, moved along the axis its search names."""
    base = [float(c) for c in spec["start"]]
    if not spec.get("search"):
        return [tuple(base)]
    (ax, vals), = spec["search"].items()
    out = []
    for v in vals:
        p = list(base)
        p[AXES.index(ax)] = float(v)
        out.append(tuple(p))
    return out


def _size_record(spec, start, m):
    value, lo3, hi3, lo_pn, hi_pn = m
    return {"name": spec["name"], "along": spec["along"], "start": [round(c, 4) for c in start],
            "beam": spec.get("beam"), "open": bool(spec.get("open")), "value": round(value, 3),
            "lo_pn": lo_pn, "hi_pn": hi_pn, "lo_at": [round(c, 4) for c in lo3], "hi_at": [round(c, 4) for c in hi3]}


def _floor_line(sh, av, floor):
    """The room floor as a thin line across a section at Z floor, with its name beyond the view's right edge."""
    x0, y0, x1, y1 = av.box()
    y = av.S(av.view.to2d((0.0, 0.0, floor)))[1] if abs(av.view.y[2]) > 0.99 else None
    if y is None:
        return None
    label = "ROOM FLOOR"
    for lx in (x1 + 3.0, x0 - 3.0 - sh.text_width(label, SIZE_TEXT)):
        tb = sh.text_box(lx, y + 0.8, label, SIZE_TEXT, "left")
        if sh.is_free(tb):
            break
    else:
        return None
    sh.line((x0 - 2.0, y), (x1 + 2.0, y), W_THIN)
    sh.text(lx, y + 0.8, label, SIZE_TEXT, "left")
    return {"view": av.name, "y": y, "x0": x0 - 2.0, "x1": x1 + 2.0, "label_at": [lx, y + 0.8]}


def _place_tag(sh, av, code, env):
    """A position code in a thin box, on its panel in view av: the free spot nearest the panel's centre, inside
    the panel's outline as the view shows it. Its record, or None when there is no free spot."""
    pts = [av.S(av.view.to2d((env[0] if i & 1 else env[3], env[1] if i & 2 else env[4], env[2] if i & 4 else env[5])))
           for i in range(8)]
    rx0, ry0 = min(p[0] for p in pts), min(p[1] for p in pts)
    rx1, ry1 = max(p[0] for p in pts), max(p[1] for p in pts)
    hw = sh.text_width(code, TAG_TEXT, bold=True) / 2 + 1.2
    hh = TAG_TEXT / 2 + 1.2
    cx0, cy0 = (rx0 + rx1) / 2, (ry0 + ry1) / 2
    cands = []
    for i in range(-60, 61):
        for j in range(-60, 61):
            cx, cy = cx0 + i * 1.0, cy0 + j * 1.0
            if rx0 + hw + 0.5 <= cx <= rx1 - hw - 0.5 and ry0 + hh + 0.5 <= cy <= ry1 - hh - 0.5:
                cands.append((math.hypot(i, j), cx, cy))
    for _d, cx, cy in sorted(cands):
        box = (cx - hw, cy - hh, cx + hw, cy + hh)
        if sh.is_free(box):
            sh.rect(cx - hw, cy - hh, 2 * hw, 2 * hh, lw=W_THIN)
            sh.text(cx, cy, code, TAG_TEXT, "center", bold=True, valign="mid")
            return {"code": code, "view": av.name, "env": [round(c, 3) for c in env], "centre": [cx, cy],
                    "box": list(box)}
    return None


def _extra_notes(e, got, out, assy):
    """The notes that give the measured sizes, the position codes, the sections' planes and the mass, each with its
    status and basis."""
    notes = []
    secs = []
    for s in e.get("sections", ()):
        n = s["normal"]
        k = max(range(3), key=lambda i: abs(n[i]))
        seen = {(0, -1): "the left", (0, 1): "the right", (1, -1): "the front", (1, 1): "behind", (2, 1): "above",
                (2, -1): "below"}[(k, 1 if n[k] > 0 else -1)]
        secs.append("%s-%s at %s %s%s, seen from %s" % (s["letter"], s["letter"], AXES[k].upper(),
                                                       A.fmt(s["point"][k], 1),
                                                       (" (%s)" % s["words"]) if s.get("words") else "", seen))
    if secs:
        notes.append("Sections cut the teams' parts as modelled: %s. Each assembly's own sheets give its build-ups, "
                     "fixings and sizes." % "; ".join(secs))
    f = lambda n: A.fmt(got[n]["value"], 1)     # noqa: E731
    if all(n in got for n in ("inside width", "inside depth", "clear height")):
        d = got["inside depth"]
        notes.append("Inside sizes, measured on the teams' STEPs (calculation): width %s between the side linings at Z "
                     "%s (C-C); depth %s from the closed door's inner face to the back lining at X %s (C-C); clear "
                     "height %s from the room floor to the ceiling cassettes' underside (B-B)." % (
                         f("inside width"), A.fmt(got["inside width"]["start"][2], 1), f("inside depth"),
                         A.fmt(d["start"][0], 1), f("clear height")))
    door = e.get("door")
    dw = [got[n] for n in ("door clear width at the foot", "door clear width", "door clear width at the head")
          if n in got]
    if door and dw and "door clear height" in got:
        notes.append(
            "Door clear opening with the door open %s° outward (calculation on FRONT's STEPs): width %s, from DL's "
            "hinge-side stop %s to the fixed glass's door edge (the opening narrows upward with the door's slanted "
            "edge); height %s under the door catch %s in DT (A-A). The hinge isn't named yet (HOLD H01): the leaf is "
            "turned about a pivot taken at X %s, Y %s (D-154's limit), the hinges' HOLD spaces left out "
            "(assumption); the open leaf stays clear of these sizes." % (
                A.fmt(door["angle"], 1),
                ", ".join("%s at Z %s%s" % (A.fmt(r["value"], 1), A.fmt(r["start"][2], 1),
                                            " (C-C)" if r.get("view") else "") for r in dw),
                dw[0]["lo_pn"], A.fmt(got["door clear height"]["value"], 1), got["door clear height"]["hi_pn"],
                A.fmt(door["pivot"][0], 1), A.fmt(door["pivot"][1], 1)))
    if out["codes"]:
        by = {}
        for c in out["codes"]:
            by.setdefault(c["view"], []).append(c["code"])

        def where(k):
            if k.startswith("section_"):
                return "section %s-%s" % (k[-1], k[-1])
            return {"from_left": "the view from the left", "from_right": "the view from the right",
                    "above": "the view from above", "principal": "the front view"}.get(k, k)
        notes.append("Position codes (guideline 5.1), on the skeleton %s's panels: %s.%s" % (
            skeleton_rev(), "; ".join("%s on %s" % (", ".join(v), where(k)) for k, v in by.items()),
            (" " + e["codes_words"]) if e.get("codes_words") else ""))
    notes.append("MASS %s kg (calculation): the weight roll-up on skeleton %s (%s, its '%s' row): every part on the "
                 "pod as it stands in the room, the parts that ship loose included; packaging not in it, nor the voice "
                 "kit's reserve (D-11)." % (assy.mass, skeleton_rev(), inputs.rel(assy.rollup), ROLLUP_ROW))
    return notes



def entry():
    """The GA's entry, POD in tools/drawgen/teams/ga.py."""
    import importlib.util as _ilu
    path = os.path.join(HERE, "teams", "ga.py")
    sp = _ilu.spec_from_file_location("drawgen_pod_entry", path)
    m = _ilu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.POD


def make(out_path, conf=None, today=None):
    """Draw the pod's sheet into out_path; returns the assembly mode's report."""
    conf = conf if conf is not None else entry()
    return A.make(POD_PN, TEAM, conf, out_path, today=today, assy=PodAssy(POD_PN, TEAM, conf))


def generate(out_dir=None, conf=None):
    """Write the sheet as out_dir/PN_REV_NAME_DWG.pdf, never over a PDF drawgen didn't make (a Fusion drawing)."""
    out_dir = out_dir or os.path.join(inputs.REPO, OUT_REL)
    tmp = os.path.join(out_dir, ".drawgen-%s.pdf" % POD_PN)
    os.makedirs(out_dir, exist_ok=True)
    try:
        rep = make(tmp, conf)
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


# ------------------------------------------------------------------ the read-back


def _item_parts(steps, up):
    """{first-level part number: [the solids of each team STEP top part under it]}: one list per placed part, as
    the sheet measures an interface point on a placed part's whole box (assembly._ref_point)."""
    out = {}
    for p in steps:
        for tpn, _name, solids in top_parts(p):
            item = up.get(tpn)
            if item:
                out.setdefault(item, []).append(solids)
    return out


def check(pdf_path):
    """Read the pod's sheet back against the team STEPs and the master BOM, independently of how it was drawn:
    the STEPs it names are the whole-pod set today and unchanged since (else draw it again); every table row against
    the master BOM's first-level row (item order, number, name, quantity, material, finish, word for word); every
    balloon's number against the table, its tip where its 3D point projects, an arrowhead or dot there and that point
    in or on its item's solids; every item a STEP has carries a balloon, and a * only where none has; the interface
    ordinates measured again; Creator drawgen, CREATED BY and author Autonomous, no maker line, no text touching text
    or a line. Returns (failures, stats)."""
    import fitz
    import readback
    doc = fitz.open(pdf_path)
    page = doc[0]
    data = readback.read_data(doc)
    fails = []
    stats = {"rows": 0, "balloons": 0, "interfaces": 0, "steps": 0}
    if data.get("kind") != "pod":
        return ["not the pod's sheet (no kind 'pod' in its drawing data)"], stats
    steps = [os.path.join(inputs.REPO, s["path"]) for s in data["sources"] if s["role"] == "STEP"]
    lst = os.path.join(inputs.REPO, [s for s in data["sources"] if s["role"] == "parts list"][0]["path"])
    # 0. the sources: today's whole-pod set, each file as it was drawn
    now = [inputs.rel(p) for p in pod_steps()]
    drawn = [inputs.rel(p) for p in steps]
    for p in sorted(set(now) - set(drawn)):
        fails.append("%s is in the pod's STEPs now but not on the sheet: draw it again" % p)
    for p in sorted(set(drawn) - set(now)):
        fails.append("%s is on the sheet but not in the pod's STEPs now" % p)
    for s in data["sources"]:
        stats["steps"] += s["role"] == "STEP"
        p = os.path.join(inputs.REPO, s["path"])
        if not os.path.exists(p):
            fails.append("source %s is gone" % s["path"])
        elif s["role"] == "mass":           # the roll-up changes often; only its total matters here
            try:
                now_kg = rollup_mass(p)[0]
            except NotDrawable as e_:
                now_kg = str(e_)
            if now_kg != s.get("kg"):
                fails.append("the weight roll-up gives the pod %s kg now, the sheet %s: draw it again" % (
                    now_kg, s.get("kg")))
        elif inputs.sha12(p) != s["sha256_12"]:
            fails.append("source %s changed since the sheet was drawn: draw it again" % s["path"])
    _own, first, up = master_tree(lst)
    leave = set(entry().get("leave_out", ()))       # the sheet's data doesn't hold it; the entry does
    rows = [r for r in first if r["part_number"].strip() not in leave]
    # 1. the table against the master BOM's first-level rows
    tab = A.table_text(page, data)
    if sorted(tab) != list(range(1, len(rows) + 1)):
        fails.append("the table's items %s are not 1 to %d (the master BOM's first-level rows)" % (sorted(tab),
                                                                                                   len(rows)))
    for n, r in enumerate(rows, 1):
        if n not in tab:
            continue
        stats["rows"] += 1
        want = [str(n), r["part_number"].strip(), (r.get("name") or "").strip(), A.qty_text(r.get("qty_per_pod")),
                (r.get("material") or "").strip() or "-", (r.get("finish") or "").strip() or "-"]
        for k, (w, g) in enumerate(zip(want, tab[n][1])):
            if k and " ".join(w.split()) != g:
                fails.append("table item %d %s: '%s' where the master BOM has '%s'" % (n, A.COLS[k][0], g[:60],
                                                                                       w[:60]))
    # 2. balloons, on their items' solids from every STEP
    parts = _item_parts(steps, up)
    solids = {k: [x for sol in v for x in sol] for k, v in parts.items()}
    views = {v["name"]: v for v in data["views"]}
    ballooned = set()
    for b in data.get("balloons", []):
        stats["balloons"] += 1
        n, bpn = b["no"], b["pn"]
        if n not in tab:
            fails.append("balloon %d: no table row %d" % (n, n))
        elif tab[n][1][1] != bpn:
            fails.append("balloon %d names %s, its table row %s" % (n, bpn, tab[n][1][1]))
        if bpn not in solids:
            fails.append("balloon %d: no STEP has a part under %s" % (n, bpn))
        v = views.get(b["view"])
        t3 = tuple(b["tip3d"])
        S = (v["off"][0] + v["scale"] * vdot(t3, v["x"]), v["off"][1] + v["scale"] * vdot(t3, v["y"]))
        if math.dist(S, b["tip"]) > A.TOL_TIP:
            fails.append("balloon %d: its tip is %.3f mm from where its point projects" % (n, math.dist(S, b["tip"])))
        if not A._arrow_or_dot_at(page, data["sheet_h"], tuple(b["tip"]), b["end"]):
            fails.append("balloon %d: no %s drawn at its tip" % (n, "arrowhead" if b["end"] == "arrow" else "dot"))
        if not A._in_or_on(solids.get(bpn, []), t3):
            fails.append("balloon %d: its point (%.2f, %.2f, %.2f) is not on %s in the STEPs" % ((n,) + t3 + (bpn,)))
        ballooned.add(bpn)
        txt = [t for t in readback.text_boxes(page, data["sheet_h"]) if t[4] == str(n) and
               math.dist(((t[0] + t[2]) / 2, (t[1] + t[3]) / 2), tuple(b["centre"])) < 1.5]
        if not txt:
            fails.append("balloon %d: its number isn't written in its circle" % n)
    for n, (mark, cells) in tab.items():
        has = cells[1] in solids
        if not mark and not has:
            fails.append("item %d %s has no * but no STEP has a part under it" % (n, cells[1]))
        if mark and has:
            fails.append("item %d %s is marked as not modelled, but a STEP has it" % (n, cells[1]))
        if not mark and cells[1] not in ballooned:
            fails.append("item %d %s is in the STEPs but has no balloon" % (n, cells[1]))
    # 3. interface ordinates, measured again from the STEPs
    for g in data.get("interfaces", []):
        v = views[g["view"]]
        ax = v["x"] if g["axis"] == "x" else v["y"]
        o3 = tuple(g["origin3d"])
        for p_ in g["points"]:
            stats["interfaces"] += 1
            c3 = tuple(p_["at3d"])
            if not any(all(bx[k] - A.TOL_ON <= c3[k] <= bx[k + 3] + A.TOL_ON for k in range(3))
                       for bx in [A.box_of(sol) for sol in parts.get(p_["pn"], [])]):
                fails.append("interface point of %s at (%.2f, %.2f, %.2f) is outside it" % ((p_["pn"],) + c3))
            want = abs(vdot(vsub(c3, o3), ax))
            if abs(abs(float(p_["value"])) - want) > A.TOL_ON:
                fails.append("interface value %s for %s, the STEPs give %.2f" % (p_["value"], p_["pn"], want))
    # 4. what only the pod's sheet has: clear sizes, position codes, mass
    text = "\n".join(pg.get_text() for pg in doc)
    fails += check_extra(page, data, steps, up, text, stats)
    # 5. the sheet as a whole: what every drawgen sheet must hold
    up_text = text.upper()
    for need, pat in (("UNITS: mm", r"UNITS:\s*MM\b"), ("MATERIAL", r"MATERIAL:"), ("FINISH", r"FINISH:"),
                      ("TOLERANCE", r"TOLERANCE")):
        if not re.search(pat, up_text):
            fails.append("text lacks %s" % need)
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


def _sheet_pt(v, p3):
    """A 3D point where the sheet's view v (its data) draws it."""
    return (v["off"][0] + v["scale"] * vdot(p3, v["x"]), v["off"][1] + v["scale"] * vdot(p3, v["y"]))


def _text_near(page, sheet_h, words, at, tol=1.5):
    """True when the page has the text `words` whose box (paper mm) holds the point `at` (where the sheet anchored
    it: a corner, an edge's middle or its centre), give or take tol."""
    import readback
    return any(t[4] == words and t[0] - tol <= at[0] <= t[2] + tol and t[1] - tol <= at[1] <= t[3] + tol
               for t in readback.text_boxes(page, sheet_h))


def check_extra(page, data, steps, up, text, stats):
    """The read-back of what only the pod's sheet has, against today's STEPs, skeleton and roll-up and the GA's
    entry: every clear size the entry asks for measured again at its recorded place, between the parts it names
    (the door turned as the entry says), and drawn there (its arrowheads, its text); every position code on its
    panel as the skeleton has it; the mass as the roll-up gives it, in the title block."""
    fails = []
    e = entry()
    x = data.get("extra")
    if not x:
        return ["no clear sizes, position codes or mass on the sheet (its data has no 'extra')"] \
            if (e.get("clear") or e.get("codes")) else []
    if (x.get("door") or None) != (e.get("door") or None):
        fails.append("the sheet's door (%s) isn't the entry's (%s)" % (x.get("door"), e.get("door")))
    bodies = pod_bodies(steps, up)
    floor = floor_z(bodies)
    opened = turned_door(bodies, e["door"]) if e.get("door") else bodies
    views = {v["name"]: v for v in data["views"]}
    recs = {r["name"]: r for r in x.get("sizes", [])}
    stats["clear sizes"] = 0
    for spec in e.get("clear", ()):
        r = recs.get(spec["name"])
        if r is None:
            fails.append("clear size '%s' is not on the sheet" % spec["name"])
            continue
        stats["clear sizes"] += 1
        start = tuple(r["start"])
        if not any(all(abs(a - b) < 1e-6 for a, b in zip(start, s)) for s in _starts(spec)):
            fails.append("%s: measured at %s, not a place the entry gives" % (spec["name"], list(start)))
            continue
        m = measure(opened if spec.get("open") else bodies, spec, start, floor)
        if m is None:
            fails.append("%s: at %s it is no longer measured between %s and %s" % (
                spec["name"], list(start), "/".join(spec["ends"][0]), "/".join(spec["ends"][1])))
            continue
        if abs(m[0] - r["value"]) > TOL_SIZE:
            fails.append("%s: the sheet has %s, measured again %.3f" % (spec["name"], r["value"], m[0]))
        if (m[3], m[4]) != (r["lo_pn"], r["hi_pn"]):
            fails.append("%s: between %s and %s on the sheet, %s and %s now" % (spec["name"], r["lo_pn"],
                                                                                r["hi_pn"], m[3], m[4]))
        shown = A.fmt(r["value"], 1)
        if spec.get("view"):
            v = views.get(spec["view"])
            if v is None or r.get("view") != spec["view"]:
                fails.append("%s: not on %s" % (spec["name"], spec["view"]))
                continue
            want = spec["label"] % shown
            if r["text"] != want or not _text_near(page, data["sheet_h"], want, tuple(r["text_at"])):
                fails.append("%s: its text '%s' isn't written where the sheet says" % (spec["name"], want))
            lo3, hi3 = list(m[1]), list(m[2])
            for a_, v_ in spec.get("draw_at", {}).items():
                lo3[AXES.index(a_)] = hi3[AXES.index(a_)] = float(v_)
            tips = [_sheet_pt(v, tuple(lo3)), _sheet_pt(v, tuple(hi3))]
            for t_, rt in zip(tips, r["tips"]):
                if math.dist(t_, tuple(rt)) > A.TOL_TIP:
                    fails.append("%s: an end is %.3f mm from where its point projects" % (spec["name"],
                                                                                         math.dist(t_, tuple(rt))))
            if r.get("side"):           # sheet.dim_linear: the arrowheads on the dimension line
                k = 1 if r["side"] in ("up", "down") else 0
                heads = [(t_[0], r["line_at"]) if k == 1 else (r["line_at"], t_[1]) for t_ in tips]
            else:
                heads = tips
            for h in heads:
                if not A._arrow_or_dot_at(page, data["sheet_h"], tuple(h), "arrow"):
                    fails.append("%s: no arrowhead at (%.2f, %.2f)" % ((spec["name"],) + tuple(h)))
            for end_, p3, pn in ((0, m[1], m[3]), (1, m[2], m[4])):
                if pn == "floor":
                    if abs(p3[2] - floor) > TOL_SIZE:
                        fails.append("%s: its floor end isn't on the room floor" % spec["name"])
                elif not A._in_or_on([b.solid for b in (opened if spec.get("open") else bodies) if b.named([pn])],
                                     tuple(p3)):
                    fails.append("%s: its end (%.2f, %.2f, %.2f) is not on %s" % ((spec["name"],) + tuple(p3) +
                                                                                   (pn,)))
        if shown not in " ".join(text.split()):
            fails.append("%s: %s isn't written on the sheet" % (spec["name"], shown))
    codes = skeleton_codes()
    want_codes = [(vn, c) for vn, cl in e.get("codes", {}).items() for c in cl]
    got_codes = {(r["view"], r["code"]): r for r in x.get("codes", [])}
    stats["codes"] = 0
    for vn, c in want_codes:
        r = got_codes.get((vn, c))
        if r is None:
            fails.append("position code %s is not on %s" % (c, vn))
            continue
        stats["codes"] += 1
        env = codes.get(c)
        v = views.get(vn)
        if env is None:
            fails.append("position code %s: the skeleton has no such panel now" % c)
            continue
        pts = [_sheet_pt(v, (env[0] if i & 1 else env[3], env[1] if i & 2 else env[4], env[2] if i & 4 else env[5]))
               for i in range(8)]
        cx, cy = r["centre"]
        if not (min(p[0] for p in pts) <= cx <= max(p[0] for p in pts) and
                min(p[1] for p in pts) <= cy <= max(p[1] for p in pts)):
            fails.append("position code %s sits off its panel on %s" % (c, vn))
        if not _text_near(page, data["sheet_h"], c, (cx, cy)):
            fails.append("position code %s isn't written where the sheet says" % c)
    for fl in x.get("floor_lines", []):
        if not _text_near(page, data["sheet_h"], "ROOM FLOOR", tuple(fl["label_at"])):
            fails.append("the room floor's name is missing on %s" % fl["view"])
    try:
        kg = rollup_mass()[0]
    except NotDrawable as e_:
        kg = str(e_)
    if x.get("mass", {}).get("kg") != kg:
        fails.append("MASS: the sheet has %s kg, the weight roll-up %s" % (x.get("mass", {}).get("kg"), kg))
    if "%s kg (calculation)" % kg not in text:
        fails.append("the title block's MASS isn't %s kg (calculation)" % kg)
    return fails


def main(argv=None):
    """generate [--out DIR]: draw the pod's sheet and read it back; check PDF...: read sheets back."""
    import argparse
    ap = argparse.ArgumentParser(description="drawgen: GA sheet 1, the whole pod")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--out", default=None)
    c = sub.add_parser("check")
    c.add_argument("pdfs", nargs="+")
    a = ap.parse_args(argv)
    bad = 0
    if a.cmd == "generate":
        try:
            final, rep = generate(a.out)
        except NotDrawable as e:
            print("%s: not drawn: %s" % (POD_PN, e))
            return 1
        fails, st = check(final)
        print("%s: %s; read-back %s (%d STEPs, %d table rows, %d balloons, %d interface sizes, %d clear sizes, "
              "%d position codes)" % (
                  POD_PN, inputs.rel(final) if final.startswith(inputs.REPO) else final,
                  "PASS" if not fails else "FAIL", st["steps"], st["rows"], st["balloons"], st["interfaces"],
                  st.get("clear sizes", 0), st.get("codes", 0)))
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
    sys.exit(main())
