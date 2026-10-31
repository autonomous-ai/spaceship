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
    """Evaluated polygon, axis (unit, in the member's plane), length along it, and end-cut angles."""
    pts = [(ev(u), ev(v)) for u, v in m["pts"]]
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
    """Each member: a fully constrained polygon, extruded, then shelled to a tube with its end faces open.
    Returns {key: body}. A member whose shell fails stays solid and is reported (FRAME SHELL FAILED)."""
    import adsk.core
    import adsk.fusion
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    bodies = {}
    for m in members:
        sk = L.poly(design, comp, L.plane_of(comp, m["axes"]), m["axes"], 0, "TUBE %s - %s" % (m["key"], m["name"]),
                    m["pts"])
        f = L.extrude_span(comp, sk, m["along"], m["a"], m["b"], NEW, None, "EXTRUDE - TUBE %s" % m["key"])
        if f.bodies.count != 1:
            raise RuntimeError("tube %s: extrude made %d bodies" % (m["key"], f.bodies.count))
        b = f.bodies.item(0)
        b.name = "%s %s %s" % (m["key"], m["name"], m["section"])
        ev = lambda e: L.ev(design, e)
        num = member_numbers(m, ev)
        ax = axis3(m["axes"], *num["axis"])
        ends = adsk.core.ObjectCollection.create()
        for fc in b.faces:
            ok, nrm = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
            if abs(nrm.x * ax[0] + nrm.y * ax[1] + nrm.z * ax[2]) > 0.25:
                ends.add(fc)
        try:
            if ends.count < 2:
                raise RuntimeError("%d end faces" % ends.count)
            si = comp.features.shellFeatures.createInput(ends, False)
            si.insideThickness = adsk.core.ValueInput.createByString(t_expr)
            sh = comp.features.shellFeatures.add(si)
            sh.name = "SHELL - TUBE %s (ENDS OPEN)" % m["key"]
        except Exception as exc:
            print("FRAME SHELL FAILED|%s|%r" % (m["key"], exc))
        bodies[m["key"]] = b
    return bodies


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
