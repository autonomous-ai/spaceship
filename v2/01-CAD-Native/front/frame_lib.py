"""Tube frames inside the FRONT decor blocks (Spaceship / FocusPod v2).

The blocks' ACP skins are bonded to welded frames of 6063-T6 tube (D-79), as v1's 16 mm steel frames were
(sources/v1 decor frame drawing): a ring of mitred tubes just inside the front skin, a ring just in front of the
back plates, and members between the two rings. Every corner is an expression of the skeleton and the block's own
parameters, so the sketches stay fully constrained and the frame follows an edit.

A line in a plane is (a, b, c): a*u + b*v = c, where (a, b) is the unit normal pointing INTO the block and c is in
mm. push(line, e) moves it e into the block. A ring is a list of (line, offset, tube width): the tube along each
line lies between the line pushed by `offset` and by `offset + width`, and neighbouring tubes meet on the mitre
through their outer and inner corners, so each tube is a quadrilateral.

Members are prisms (a polygon on an origin plane, extruded along the third axis), then shelled to tubes with their
end faces open: real walls, real mass.
"""

import math
import re


# ---- expressions, simplified where a coefficient is a plain number (keeps the sketch dimensions readable)

def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _fmt(x):
    return ("%.10g" % x) if x != 0 else "0"


def _par(s):
    return s if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*|-?[0-9.]+", s) else "(%s)" % s


def mul(x, y):
    nx, ny = _num(x), _num(y)
    if nx is not None and ny is not None:
        return _fmt(nx * ny)
    if nx == 0 or ny == 0:
        return "0"
    if nx == 1:
        return y
    if ny == 1:
        return x
    if nx == -1:
        return "-%s" % _par(y)
    if ny == -1:
        return "-%s" % _par(x)
    return "%s * %s" % (_par(x), _par(y))


def add(x, y):
    nx, ny = _num(x), _num(y)
    if nx is not None and ny is not None:
        return _fmt(nx + ny)
    if nx == 0:
        return y
    if ny == 0:
        return x
    return "%s + %s" % (x, _par(y))


def sub(x, y):
    nx, ny = _num(x), _num(y)
    if nx is not None and ny is not None:
        return _fmt(nx - ny)
    if ny == 0:
        return x
    if nx == 0:
        return "-%s" % _par(y)
    return "%s - %s" % (x, _par(y))


def div(x, y):
    ny = _num(y)
    if ny == 1:
        return x
    if ny == -1:
        return "-%s" % _par(x)
    return "%s / %s" % (_par(x), _par(y))


def line(a, b, c):
    return (str(a), str(b), str(c))


def push(l, e):
    return l if str(e) in ("0", "0 mm") else (l[0], l[1], "(%s + %s)" % (l[2], e))


def meet(l1, l2):
    """Where two lines cross: (u, v) as expressions."""
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = sub(mul(a1, b2), mul(a2, b1))
    u = div(sub(mul(c1, b2), mul(c2, b1)), det)
    v = div(sub(mul(a1, c2), mul(a2, c1)), det)
    return ("(%s)" % u, "(%s)" % v)


def ring(lines):
    """lines = [(line, offset, width)] in order round the ring. Returns one quadrilateral per line, running from
    its corner with the line before to its corner with the line after: [outer start, outer end, inner end, inner
    start]."""
    n = len(lines)
    outer, inner = [], []
    for i in range(n):
        lp, op, wp = lines[i - 1]
        lc, oc, wc = lines[i]
        outer.append(meet(push(lp, op), push(lc, oc)))
        inner.append(meet(push(lp, "%s + %s" % (op, wp)), push(lc, "%s + %s" % (oc, wc))))
    return [[outer[i], outer[(i + 1) % n], inner[(i + 1) % n], inner[i]] for i in range(n)]


# ---- numbers (offline checks and the cut list)

def evaluator(env):
    """ev(expr) -> mm, for expressions in the parameter names of env (a dict of mm values)."""
    def ev(e):
        e2 = re.sub(r"(\d)\s*mm\b", r"\1", str(e)).replace("^", "**")
        return eval(e2, {"__builtins__": {}, "sqrt": math.sqrt, "abs": abs}, env)
    return ev


def member_numbers(m, ev):
    """Evaluated polygon, axis (unit, in the member's plane), length along it, and end-cut angles. A member whose
    polygon is its cross-section ("lengthwise": True) runs along its extrusion: its length is b - a."""
    pts = [(ev(u), ev(v)) for u, v in m["pts"]]
    if m.get("lengthwise"):
        return {"pts": pts, "axis": None, "length": abs(ev(m["b"]) - ev(m["a"]))}
    i, j = m.get("axis", (0, 1))
    d = (pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
    n = math.hypot(*d)
    ax = (d[0] / n, d[1] / n)
    proj = [p[0] * ax[0] + p[1] * ax[1] for p in pts]
    return {"pts": pts, "axis": ax, "length": max(proj) - min(proj)}


def axis3(axes, u, v):
    """A vector given in a plane's (u, v) as a model (x, y, z) vector."""
    out = {"x": 0.0, "y": 0.0, "z": 0.0}
    out[axes[0]], out[axes[1]] = u, v
    return out["x"], out["y"], out["z"]


# ---- Fusion

def build_members(design, comp, L, members, t_expr):
    """Each member: a fully constrained polygon, extruded, then shelled to a tube with its end faces open, to its own
    wall m["t"] when it has one (a parameter name or expression), else t_expr.
    Returns {key: body}. A member whose shell fails stays solid and is reported (FRAME SHELL FAILED).
    (Before D-120: every member a body of comp. build_member_components makes each its own component.)"""
    return {m["key"]: build_one(design, comp, L, m, t_expr) for m in members}


def build_one(design, comp, L, m, t_expr, shell=True):
    """One member in comp: its polygon extruded, then (a tube) shelled with both ends open. Returns the body."""
    import adsk.core
    import adsk.fusion
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    sk = L.poly(design, comp, L.plane_of(comp, m["axes"]), m["axes"], 0, "TUBE %s - %s" % (m["key"], m["name"]),
                m["pts"])
    f = L.extrude_span(comp, sk, m["along"], m["a"], m["b"], NEW, None, "EXTRUDE - TUBE %s" % m["key"])
    if f.bodies.count != 1:
        raise RuntimeError("tube %s: extrude made %d bodies" % (m["key"], f.bodies.count))
    b = f.bodies.item(0)
    b.name = "%s %s %s" % (m["key"], m["name"], m["section"])
    if not shell:
        return b
    ev = lambda e: L.ev(design, e)
    num = member_numbers(m, ev)
    if num["axis"] is None:
        ax = tuple(1.0 if k == m["along"] else 0.0 for k in ("x", "y", "z"))
    else:
        ax = axis3(m["axes"], *num["axis"])
    ends = adsk.core.ObjectCollection.create()
    for fc in b.faces:
        ok, nrm = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
        # an end face leans on the tube's axis; where a wide tube meets a narrow one the mitre is long and
        # oblique (about 14 degrees off the axis for 80 against 20), so the test is small but not zero
        if abs(nrm.x * ax[0] + nrm.y * ax[1] + nrm.z * ax[2]) > 0.1:
            ends.add(fc)
    try:
        if ends.count < 2:
            raise RuntimeError("%d end faces" % ends.count)
        si = comp.features.shellFeatures.createInput(ends, False)
        si.insideThickness = adsk.core.ValueInput.createByString(m.get("t", t_expr))
        sh = comp.features.shellFeatures.add(si)
        sh.name = "SHELL - TUBE %s (ENDS OPEN)" % m["key"]
    except Exception as exc:
        print("FRAME SHELL FAILED|%s|%r" % (m["key"], exc))
    return b


# ---- D-120: every member its own component; a repeated part is copies of one component

def shift_of(first, m):
    """The shift from member `first` to its copy `m`, (dx, dy, dz) as expressions in model axes: the difference of
    their first corners and of their extrusion starts. A component whose two expressions are the same text is 0."""
    ax = {"x": 0, "y": 1, "z": 2}
    out = ["0 mm", "0 mm", "0 mm"]
    for k in (0, 1):
        a, b = str(m["pts"][0][k]), str(first["pts"][0][k])
        out[ax[m["axes"][k]]] = "0 mm" if a == b else "(%s) - (%s)" % (a, b)
    a, b = str(m["a"]), str(first["a"])
    out[ax[m["along"]]] = "0 mm" if a == b else "(%s) - (%s)" % (a, b)
    return tuple(out)


def solid_corners(m, ev):
    """The member's outline corners in model mm, both ends: [(x, y, z)]."""
    ax = {"x": 0, "y": 1, "z": 2}
    out = []
    for w in (ev(m["a"]), ev(m["b"])):
        for u, v in m["pts"]:
            p = [0.0, 0.0, 0.0]
            p[ax[m["axes"][0]]], p[ax[m["axes"][1]]], p[ax[m["along"]]] = ev(u), ev(v), w
            out.append(tuple(p))
    return out


def check_copies(members, parts, ev, tol=0.01):
    """Each member that shares a part number with an earlier one must be that member moved by shift_of(), corner for
    corner (same plane, extrusion axis, section and wall too). Returns [(key, first key, shift in mm)]; raises on any
    that isn't."""
    first, out = {}, []
    for m in members:
        pn = parts[m["key"]][:2]
        if pn not in first:
            first[pn] = m
            continue
        f = first[pn]
        if (m["axes"], m["along"], m["section"], m.get("t")) != (f["axes"], f["along"], f["section"], f.get("t")):
            raise RuntimeError("%s isn't a copy of %s (part %s): plane, axis, section or wall differ" % (m["key"], f["key"], pn))
        d = [ev(e) for e in shift_of(f, m)]
        cf, cm = solid_corners(f, ev), solid_corners(m, ev)
        worst = max(abs(p[i] + d[i] - q[i]) for p, q in zip(cf, cm) for i in range(3))
        if worst > tol:
            raise RuntimeError("%s isn't %s moved by %s: corners off by %.3f mm" % (m["key"], f["key"], d, worst))
        out.append((m["key"], f["key"], tuple(round(x, 3) for x in d)))
    return out


def place_by_shift(parent, occ, shift, name):
    """Rigid joint: occ's origin onto a construction point at `shift` (expressions, in parent's space), where three
    planes meet: each the parent's origin plane, or that plane offset by the shift's expression, so an edit moves it."""
    import adsk.core
    import adsk.fusion
    planes = []
    for base, e, tag in ((parent.yZConstructionPlane, shift[0], "X"), (parent.xZConstructionPlane, shift[1], "Y"),
                         (parent.xYConstructionPlane, shift[2], "Z")):
        if e in ("0", "0 mm"):
            planes.append(base)
            continue
        pi = parent.constructionPlanes.createInput()
        pi.setByOffset(base, adsk.core.ValueInput.createByString(e))
        pl = parent.constructionPlanes.add(pi)
        pl.name = "PLANE %s - %s" % (tag, name)
        pl.isLightBulbOn = False
        planes.append(pl)
    ci = parent.constructionPoints.createInput()
    ci.setByThreePlanes(planes[0], planes[1], planes[2])
    pt = parent.constructionPoints.add(ci)
    pt.name = "POINT - " + name
    pt.isLightBulbOn = False
    g_occ = adsk.fusion.JointGeometry.createByPoint(occ.component.originConstructionPoint.createForAssemblyContext(occ))
    g_par = adsk.fusion.JointGeometry.createByPoint(pt)
    ji = parent.joints.createInput(g_occ, g_par)
    ji.setAsRigidJointMotion()
    j = parent.joints.add(ji)
    j.name = "PLACE - " + name
    return j


def build_member_components(design, frame_comp, L, members, t_expr, parts, rev, shell=True):
    """D-120: each frame member its own component under frame_comp, named 'PN NAME', with its part number.
    parts: {member key: (pn, name, vn)}. The first member of a part (number and name) is built in place (an
    identity occurrence, so its sketches keep the block's expressions and stay fully constrained) and, for a tube,
    shelled; each later member of that part is a copy of its component, placed by place_by_shift() at its shift.
    Returns (native, comps, occs): the body in its own component, the component, and the occurrence in frame_comp's
    context, each by member key (a copy shares the first's body and component)."""
    import adsk.core
    first, native, comps, occs = {}, {}, {}, {}
    for m in members:
        key = m["key"]
        pn, name, vn = parts[key]
        if (pn, name) in first:
            f = first[(pn, name)]
            occ = frame_comp.occurrences.addExistingComponent(comps[f["key"]], adsk.core.Matrix3D.create())
            place_by_shift(frame_comp, occ, shift_of(f, m), "%s %s AS A COPY OF %s" % (pn, key, f["key"]))
            native[key], comps[key], occs[key] = native[f["key"]], comps[f["key"]], occ
            continue
        occ = frame_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        mc = occ.component
        mc.name = ("%s %s" % (pn, name)).strip()
        mc.partNumber = pn
        mc.description = "%s | %s | %s" % (name, vn, rev)
        native[key] = build_one(design, mc, L, m, t_expr, shell)
        first[(pn, name)] = m
        comps[key], occs[key] = mc, occ
    return native, comps, occs


def root_bodies(frame_occ, native, occs):
    """Each member's body in the root's context (through the frame's occurrence and its own; frame_occ None when the
    members sit in the root itself), for the clash check and the box report: a copy's body sits where its joint put it."""
    return {k: native[k].createForAssemblyContext(occs[k] if frame_occ is None else occs[k].createForAssemblyContext(frame_occ))
            for k in native}


def frame_mass(frame_occ, occs):
    """The welded frame's mass: every member occurrence's, copies counted once each (kg)."""
    return sum(occs[k].createForAssemblyContext(frame_occ).physicalProperties.mass for k in occs)


def cut_list_rows(members, ev, frame_pn):
    """Rows for the tube cut list CSV: frame, member, name, section, length, qty, ends, status."""
    rows = []
    for m in members:
        num = member_numbers(m, ev)
        rows.append((frame_pn, m["key"], m["name"], "6063-T6 aluminium tube " + m["section"], "%.1f" % num["length"],
                     1, m.get("ends", "mitred to its neighbours (see the frame drawing)"),
                     "calculation (from the parameters)"))
    return rows


def write_plate_dxf(path, body, along="y"):
    """A flat plate or panel laid flat 1:1 (D-89 part 4: its DXF gives the full outline and every hole): the largest
    face square to `along`, its loops as LINE and CIRCLE entities in mm, in the plate's own corner (the lowest-left
    point of the face at 0,0). Returns (width, height, holes, origin in pod coordinates)."""
    import adsk.core
    ax = {"x": 0, "y": 1, "z": 2}[along]
    keep = [i for i in range(3) if i != ax]

    def uv(p):
        q = (p.x * 10.0, p.y * 10.0, p.z * 10.0)
        return q[keep[0]], q[keep[1]]
    best = None
    for fc in body.faces:
        ok, n = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
        if abs((n.x, n.y, n.z)[ax]) > 0.999 and (best is None or fc.area > best.area):
            best = fc
    if best is None:
        raise RuntimeError("no face square to " + along)
    ents, pts = [], []
    holes = 0
    for loop in best.loops:
        for e in loop.edges:
            g = e.geometry
            if isinstance(g, adsk.core.Circle3D):
                c = uv(g.center)
                ents.append(("CIRCLE", c, g.radius * 10.0))
                pts.append(c)
                holes += 1
            elif isinstance(g, adsk.core.Line3D):
                a, b = uv(e.startVertex.geometry), uv(e.endVertex.geometry)
                ents.append(("LINE", a, b))
                pts += [a, b]
            else:
                ok, mn, mx = e.evaluator.getParameterExtents()
                ok, strokes = e.evaluator.getStrokes(mn, mx, 0.001)
                s = [uv(p) for p in strokes]
                for a, b in zip(s, s[1:]):
                    ents.append(("LINE", a, b))
                pts += s
    u0, v0 = min(p[0] for p in pts), min(p[1] for p in pts)
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for ent in ents:
        if ent[0] == "LINE":
            (a, b) = ent[1], ent[2]
            out += ["0", "LINE", "8", "CUT", "10", "%.4f" % (a[0] - u0), "20", "%.4f" % (a[1] - v0), "30", "0",
                    "11", "%.4f" % (b[0] - u0), "21", "%.4f" % (b[1] - v0), "31", "0"]
        else:
            c, r = ent[1], ent[2]
            out += ["0", "CIRCLE", "8", "CUT", "10", "%.4f" % (c[0] - u0), "20", "%.4f" % (c[1] - v0), "30", "0",
                    "40", "%.4f" % r]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", encoding="ascii") as fh:
        fh.write("\n".join(out) + "\n")
    w = max(p[0] for p in pts) - u0
    h = max(p[1] for p in pts) - v0
    return round(w, 2), round(h, 2), holes, (round(u0, 2), round(v0, 2))


ALLOCATION_REL = "v2/04-BOM/number-allocation.csv"


def member_parts(repo_root, frame_pn, member_pn):
    """{member key: (pn, name, name_vi)} from the master BOM's allocation list (D-120, #232). Each number must be
    allocated to this frame and not cancelled, its quantity must be how many members use it, and a number used once
    must be named after its member. Raises on any mismatch, so the model can't drift from Control's list."""
    import collections
    import csv
    import os
    with open(os.path.join(repo_root, ALLOCATION_REL), encoding="utf-8") as f:
        rows = {r["part_number"]: r for r in csv.DictReader(f)}
    count = collections.Counter(member_pn.values())
    out = {}
    for key, pn in member_pn.items():
        r = rows.get(pn)
        if r is None:
            raise RuntimeError("member %s: %s isn't in %s" % (key, pn, ALLOCATION_REL))
        if r["parent"].strip() != frame_pn or "CANCEL" in r["status"].upper():
            raise RuntimeError("member %s: %s belongs to %r (%s), not to the frame %s" % (key, pn, r["parent"], r["status"], frame_pn))
        if int(round(float(r["qty_per_parent"] or 0))) != count[pn]:
            raise RuntimeError("%s: the allocation list says %s per frame, the frame has %d (%s)" % (
                pn, r["qty_per_parent"], count[pn], ", ".join(k for k, v in member_pn.items() if v == pn)))
        out[key] = (pn, r["name"].strip(), r["name_vi"].strip())
    return out


def write_weldment_lists(L, design, root_dir, rows, frame_pn, member_rows, weld_rel, block_rel, block):
    """D-120 parts lists: the weldment's own list (the frame's row on top, then its tube parts, the frame row the sum
    of them) and the block's list, where the frame is one row carrying that sum, so no tube is counted twice (the
    master BOM reads the frame row as an assembly, the roll-up reads the block's rows). rows: the block's rows with
    the frame row and member_rows among them (front_lib.write_parts_list's tuples); block: (pn, name, name_vi).
    Returns (block total, weldment total)."""
    import os
    frow = [r for r in rows if r[0] == frame_pn][0]
    weld = L.write_parts_list(design, os.path.join(root_dir, weld_rel), [frow] + list(member_rows), frame_pn,
                              frow[1], frow[2])
    members = {id(r) for r in member_rows}
    block_rows = []
    for r in rows:
        if id(r) in members:
            continue
        if r[0] == frame_pn:
            r = tuple(r[:6]) + (round(weld, 3), "calculation (sum of its parts list %s)" % weld_rel.split("/")[-1]) + \
                tuple(r[8:])
        block_rows.append(r)
    total = L.write_parts_list(design, os.path.join(root_dir, block_rel), block_rows, *block)
    return total, weld

