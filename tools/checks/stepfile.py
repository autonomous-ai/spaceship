#!/usr/bin/env python3
"""Read a STEP file (AP203/AP214, as Fusion writes it) without a CAD kernel.

What it gives the checks:
- the declared length unit, as a factor to mm (Fusion writes cm, D-13);
- products (part number = PRODUCT id, name = PRODUCT name) and how often each
  one is used in the assembly tree (NEXT_ASSEMBLY_USAGE_OCCURRENCE);
- every solid with its placement in the file's top assembly (the
  ITEM_DEFINED_TRANSFORMATION chain), so holes and boxes can be compared
  across parts in pod coordinates;
- per solid: planar and cylindrical faces, holes (concave full cylinders),
  sheet-metal bends (a concave and a convex coaxial cylinder one thickness
  apart, less than a full turn) and the axis-aligned box of its vertices.

Limits (say them in any result that uses them): boxes come from vertices, so
a curved face that bulges past its edges is under-counted; only planes and
cylinders are classified; a hole is a cylinder whose faces add up to a full
turn with the material outside it.

Standard library only. Never edits the file.
"""

import math
import re
from collections import defaultdict

# ----------------------------------------------------------------- parsing

_STMT = re.compile(r"'(?:[^']|'')*'|;")
_ENT = re.compile(r"\s*#(\d+)\s*=\s*(.*)\Z", re.S)
_TOK = re.compile(r"""
    (?P<str>'(?:[^']|'')*')
  | (?P<ref>\#\d+)
  | (?P<enum>\.[A-Za-z0-9_]+\.)
  | (?P<num>[-+]?(?:\d+\.?\d*|\.\d+)(?:[Ee][-+]?\d+)?)
  | (?P<kw>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<p>[(),$*])
  | (?P<ws>\s+)
""", re.X)


class Ref(int):
    """A reference to another entity (#123)."""


class Enum(str):
    """A STEP enumeration such as .T. or .MILLI. (stored without dots)."""


class Typed(tuple):
    """A typed parameter such as LENGTH_MEASURE(1.): (keyword, args)."""


def _decode(s):
    s = s[1:-1].replace("''", "'")
    # \X2\hhhh...\X0\ (UTF-16 hex) and \X\hh (ISO 8859-1) as Fusion writes them
    def x2(m):
        h = m.group(1)
        return "".join(chr(int(h[i:i + 4], 16)) for i in range(0, len(h), 4))
    s = re.sub(r"\\X2\\([0-9A-Fa-f]+)\\X0\\", x2, s)
    s = re.sub(r"\\X\\([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), s)
    return s


def _tokens(text):
    for m in _TOK.finditer(text):
        k = m.lastgroup
        if k == "ws":
            continue
        yield k, m.group(k)


def _parse_list(toks, i):
    """toks[i] is '('. Returns (list, index after ')')."""
    out = []
    i += 1
    while True:
        k, v = toks[i]
        if k == "p" and v == ")":
            return out, i + 1
        if k == "p" and v == ",":
            i += 1
            continue
        val, i = _parse_value(toks, i)
        out.append(val)


def _parse_value(toks, i):
    k, v = toks[i]
    if k == "str":
        return _decode(v), i + 1
    if k == "ref":
        return Ref(int(v[1:])), i + 1
    if k == "enum":
        return Enum(v[1:-1]), i + 1
    if k == "num":
        return float(v), i + 1
    if k == "p" and v == "(":
        return _parse_list(toks, i)
    if k == "p" and v in "$*":
        return None, i + 1
    if k == "kw":
        args, j = _parse_list(toks, i + 1)
        return Typed((v.upper(), args)), j
    raise ValueError("unexpected token %r" % (v,))


def parse_entities(text):
    """Return {id: [(TYPE, args), ...]} for the DATA section (complex
    entities give several (TYPE, args) pairs)."""
    start = text.find("DATA;")
    end = text.rfind("ENDSEC;")
    body = text[start + 5:end] if start >= 0 else text
    ents = {}
    last = 0
    for m in _STMT.finditer(body):
        if m.group(0) != ";":
            continue
        stmt = body[last:m.start()]
        last = m.end()
        em = _ENT.match(stmt)
        if not em:
            continue
        eid, rhs = int(em.group(1)), em.group(2).strip()
        toks = list(_tokens(rhs))
        parts = []
        try:
            if toks and toks[0] == ("p", "("):          # complex entity
                i = 1
                while toks[i] != ("p", ")"):
                    name = toks[i][1].upper()
                    args, i = _parse_list(toks, i + 1)
                    parts.append((name, args))
            else:
                name = toks[0][1].upper()
                args, _ = _parse_list(toks, 1)
                parts.append((name, args))
        except (IndexError, ValueError):
            continue
        ents[eid] = parts
    return ents


# ----------------------------------------------------------------- vectors

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-12 else (0.0, 0.0, 1.0)


def line_distance(p, a, d):
    """Distance from point p to the line through a with unit direction d."""
    v = _sub(p, a)
    t = dot(v, d)
    return math.sqrt(max(dot(v, v) - t * t, 0.0))


class Frame:
    """Rigid placement: origin o and unit axes x, y, z (columns)."""

    def __init__(self, o=(0.0, 0.0, 0.0), x=(1.0, 0.0, 0.0), y=(0.0, 1.0, 0.0), z=(0.0, 0.0, 1.0)):
        self.o, self.x, self.y, self.z = o, x, y, z

    @staticmethod
    def from_axes(o, zdir, xdir):
        z = norm(zdir or (0.0, 0.0, 1.0))
        x = xdir or ((1.0, 0.0, 0.0) if abs(z[0]) < 0.9 else (0.0, 1.0, 0.0))
        x = norm(_sub(x, _mul(z, dot(x, z))))
        y = cross(z, x)
        return Frame(o, x, y, z)

    def point(self, p):
        """Local point -> parent."""
        return (self.o[0] + p[0] * self.x[0] + p[1] * self.y[0] + p[2] * self.z[0],
                self.o[1] + p[0] * self.x[1] + p[1] * self.y[1] + p[2] * self.z[1],
                self.o[2] + p[0] * self.x[2] + p[1] * self.y[2] + p[2] * self.z[2])

    def vector(self, v):
        return (v[0] * self.x[0] + v[1] * self.y[0] + v[2] * self.z[0],
                v[0] * self.x[1] + v[1] * self.y[1] + v[2] * self.z[1],
                v[0] * self.x[2] + v[1] * self.y[2] + v[2] * self.z[2])

    def inverse(self):
        # columns x, y, z -> rows
        o = self.o
        return Frame((-dot(o, self.x), -dot(o, self.y), -dot(o, self.z)),
                     (self.x[0], self.y[0], self.z[0]),
                     (self.x[1], self.y[1], self.z[1]),
                     (self.x[2], self.y[2], self.z[2]))

    def compose(self, inner):
        """self o inner: apply inner first, then self."""
        return Frame(self.point(inner.o), self.vector(inner.x), self.vector(inner.y), self.vector(inner.z))


# ----------------------------------------------------------------- model

class Hole:
    __slots__ = ("solid", "center", "axis", "diameter", "length", "faces", "t0", "t1")

    def __init__(self, solid, center, axis, diameter, length, faces, t0=0.0, t1=0.0):
        self.solid, self.center, self.axis = solid, center, axis
        self.diameter, self.length, self.faces = diameter, length, faces
        self.t0, self.t1 = t0, t1

    def moved(self, frame):
        return Hole(self.solid, frame.point(self.center), norm(frame.vector(self.axis)),
                    self.diameter, self.length, self.faces, self.t0, self.t1)


class Bend:
    __slots__ = ("solid", "axis_point", "axis", "inner_radius", "thickness", "angle_deg")

    def __init__(self, solid, axis_point, axis, inner_radius, thickness, angle_deg):
        self.solid, self.axis_point, self.axis = solid, axis_point, axis
        self.inner_radius, self.thickness, self.angle_deg = inner_radius, thickness, angle_deg


class Face:
    __slots__ = ("id", "kind", "origin", "normal", "radius", "same_sense", "points", "arcs", "lines")

    def __init__(self, fid, kind, origin, normal, radius, same_sense, points, arcs, lines=()):
        self.id, self.kind, self.origin, self.normal = fid, kind, origin, normal
        self.radius, self.same_sense, self.points, self.arcs = radius, same_sense, points, arcs
        self.lines = list(lines)


class Solid:
    def __init__(self, sid, name):
        self.id, self.name = sid, name
        self.faces = []
        self.holes = []
        self.bends = []
        self.box = None
        self.thickness = None     # most common distance between parallel opposite planes
        self.voids = 0            # sealed inner shells (BREP_WITH_VOIDS): noted, not used for boxes or features

    def points(self):
        for f in self.faces:
            for p in f.points:
                yield p


class StepFile:
    """A parsed STEP file. All lengths are returned in mm."""

    def __init__(self, path):
        self.path = path
        with open(path, "r", encoding="latin-1") as fh:
            text = fh.read()
        self.header = text[:text.find("DATA;")] if "DATA;" in text else ""
        self.e = parse_entities(text)
        self.unit_name, self.scale = self._unit()
        self._solids = {}

    # --- basic entity access
    def first(self, eid, name=None):
        parts = self.e.get(int(eid)) or []
        for n, a in parts:
            if name is None or n == name:
                return n, a
        return None, None

    def of_type(self, name):
        for eid, parts in self.e.items():
            for n, a in parts:
                if n == name:
                    yield eid, a

    # --- units
    def _unit(self):
        for eid, parts in self.e.items():
            names = {n for n, _ in parts}
            if "LENGTH_UNIT" not in names:
                continue
            for n, a in parts:
                if n == "SI_UNIT":
                    prefix = a[0]
                    pf = {None: 1000.0, "MILLI": 1.0, "CENTI": 10.0, "DECI": 100.0, "KILO": 1e6, "MICRO": 1e-3}
                    if prefix not in pf:
                        return "unknown SI prefix %s" % prefix, 1.0
                    return {None: "m", "MILLI": "mm", "CENTI": "cm", "DECI": "dm", "KILO": "km",
                            "MICRO": "um"}[prefix], pf[prefix]
                if n == "CONVERSION_BASED_UNIT":
                    label = (a[0] or "").lower()
                    if "inch" in label:
                        return "inch", 25.4
                    if "foot" in label or "feet" in label:
                        return "foot", 304.8
                    return "unknown (%s)" % label, 1.0
        return "undeclared", 1.0

    def pt(self, ref):
        _n, a = self.first(ref, "CARTESIAN_POINT")
        c = list(a[1]) + [0.0] * (3 - len(a[1]))
        return (c[0] * self.scale, c[1] * self.scale, c[2] * self.scale)

    def direction(self, ref):
        if ref is None:
            return None
        _n, a = self.first(ref, "DIRECTION")
        c = list(a[1]) + [0.0] * (3 - len(a[1]))
        return norm(tuple(c))

    def placement(self, ref):
        n, a = self.first(ref, "AXIS2_PLACEMENT_3D")
        if n is None:
            return Frame()
        return Frame.from_axes(self.pt(a[1]), self.direction(a[2]), self.direction(a[3]))

    # --- products and assembly
    def products(self):
        """List of dicts: pd (PRODUCT_DEFINITION id), part_number, name, description."""
        prod = {eid: a for eid, a in self.of_type("PRODUCT")}
        pdf = {eid: a for eid, a in self.of_type("PRODUCT_DEFINITION_FORMATION")}
        pdf.update({eid: a for eid, a in self.of_type("PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE")})
        out = []
        for eid, a in self.of_type("PRODUCT_DEFINITION"):
            f = pdf.get(int(a[2])) if a[2] is not None else None
            p = prod.get(int(f[2])) if f else None
            if p is None:
                continue
            out.append({"pd": eid, "part_number": (p[0] or "").strip(), "name": (p[1] or "").strip(),
                        "description": (p[2] or "").strip()})
        return out

    def occurrences(self):
        """NAUO list: dicts with id, name, parent (PD), child (PD), frame
        (child coordinates -> parent coordinates)."""
        nauo = {eid: a for eid, a in self.of_type("NEXT_ASSEMBLY_USAGE_OCCURRENCE")}
        pds_of = {}
        for eid, a in self.of_type("PRODUCT_DEFINITION_SHAPE"):
            if a[2] is not None:
                pds_of[int(a[2])] = eid
        frames = {}
        for eid, a in self.of_type("CONTEXT_DEPENDENT_SHAPE_REPRESENTATION"):
            rel, pds = int(a[0]), int(a[1])
            parts = self.e.get(rel) or []
            reps, tr = None, None
            for n, ra in parts:
                if n in ("REPRESENTATION_RELATIONSHIP", "SHAPE_REPRESENTATION_RELATIONSHIP") and len(ra) >= 4:
                    reps = (ra[2], ra[3])
                if n == "REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION":
                    tr = ra[0]
            if tr is None:
                continue
            tn, ta = self.first(tr, "ITEM_DEFINED_TRANSFORMATION")
            if tn is None:
                continue
            f_from = self.placement(ta[2])
            f_to = self.placement(ta[3])
            # AP214: rep_1 is the child (its frame ta[2]), rep_2 the parent (ta[3]).
            frames[pds] = f_to.compose(f_from.inverse())
        out = []
        for eid, a in nauo.items():
            pds = pds_of.get(eid)
            out.append({"id": eid, "name": (a[1] or "").strip(), "parent": int(a[3]), "child": int(a[4]),
                        "frame": frames.get(pds, Frame())})
        return out

    def usage_counts(self):
        """part_number -> number of instances in the whole tree (top = 1)."""
        prods = {p["pd"]: p for p in self.products()}
        occ = self.occurrences()
        children = defaultdict(list)
        has_parent = set()
        for o in occ:
            children[o["parent"]].append(o["child"])
            has_parent.add(o["child"])
        tops = [pd for pd in prods if pd not in has_parent]
        counts = defaultdict(int)

        def walk(pd, mult, depth=0):
            if depth > 50:
                return
            counts[prods[pd]["part_number"]] += mult
            for c in children.get(pd, []):
                if c in prods:
                    walk(c, mult, depth + 1)
        for t in tops:
            walk(t, 1)
        return dict(counts), [prods[t]["part_number"] for t in tops]

    def _solids_of_pd(self):
        """PD id -> list of solid entity ids directly in that product."""
        pds_to_pd = {}
        for eid, a in self.of_type("PRODUCT_DEFINITION_SHAPE"):
            if a[2] is not None:
                pds_to_pd[eid] = int(a[2])
        rep_of_pd = defaultdict(list)
        for eid, a in self.of_type("SHAPE_DEFINITION_REPRESENTATION"):
            pd = pds_to_pd.get(int(a[0]))
            if pd is not None:
                rep_of_pd[pd].append(int(a[1]))
        # plain shape-representation relationships (no transformation) join a
        # product's shape rep to its b-rep representations
        linked = defaultdict(set)
        for eid, parts in self.e.items():
            names = {n for n, _ in parts}
            if "REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION" in names:
                continue
            for n, a in parts:
                if n in ("SHAPE_REPRESENTATION_RELATIONSHIP", "REPRESENTATION_RELATIONSHIP") and len(a) >= 4 \
                        and a[2] is not None and a[3] is not None:
                    linked[int(a[2])].add(int(a[3]))
                    linked[int(a[3])].add(int(a[2]))
        solid_types = ("MANIFOLD_SOLID_BREP", "BREP_WITH_VOIDS")
        out = {}
        for pd, reps in rep_of_pd.items():
            seen, stack, solids = set(), list(reps), []
            while stack:
                r = stack.pop()
                if r in seen:
                    continue
                seen.add(r)
                for n, a in self.e.get(r, []):
                    if n.endswith("REPRESENTATION") and len(a) >= 2 and isinstance(a[1], list):
                        for it in a[1]:
                            if isinstance(it, Ref):
                                tn, _ = self.first(it)
                                if tn in solid_types:
                                    solids.append(int(it))
                for l in linked.get(r, ()):
                    # follow only to b-rep representations, not to other products
                    ln, _ = self.first(l)
                    if ln in ("ADVANCED_BREP_SHAPE_REPRESENTATION", "MANIFOLD_SURFACE_SHAPE_REPRESENTATION",
                              "FACETED_BREP_SHAPE_REPRESENTATION"):
                        stack.append(l)
            out[pd] = sorted(set(solids))
        return out

    def instances(self):
        """Every solid in the tree: dicts with solid id, product (part
        number, name), path (names from the top), frame (solid coordinates
        -> top coordinates), and pd, the component (product definition) the
        solid is a body of: several solids of one pd are several bodies of
        one component, while one component placed several times gives the
        same solid again."""
        prods = {p["pd"]: p for p in self.products()}
        occ = self.occurrences()
        children = defaultdict(list)
        has_parent = set()
        for o in occ:
            children[o["parent"]].append(o)
            has_parent.add(o["child"])
        solids = self._solids_of_pd()
        tops = [pd for pd in prods if pd not in has_parent]
        out = []

        def walk(pd, frame, path, depth=0):
            if depth > 50 or pd not in prods:
                return
            p = prods[pd]
            for sid in solids.get(pd, []):
                out.append({"solid": sid, "part_number": p["part_number"], "name": p["name"],
                            "path": path, "frame": frame, "pd": pd})
            for o in children.get(pd, []):
                walk(o["child"], frame.compose(o["frame"]), path + [o["name"] or prods.get(o["child"], {}).get("name", "")],
                     depth + 1)
        for t in tops:
            walk(t, Frame(), [prods[t]["name"] or prods[t]["part_number"]])
        return out

    # --- geometry of one solid
    def solid(self, sid):
        if sid in self._solids:
            return self._solids[sid]
        n, a = self.first(sid)
        s = Solid(sid, (a[0] or "") if a else "")
        shells = []
        if n == "MANIFOLD_SOLID_BREP":
            shells = [a[1]]
        elif n == "BREP_WITH_VOIDS":
            # a solid with a sealed void inside (an inner shell, valid STEP): its outer shell gives the box, the
            # faces, the holes and the clashes; the void is only counted (an ORIENTED_CLOSED_SHELL, whose face list
            # is derived, '*')
            shells = [a[1]]
            s.voids = len([v for v in (a[2] if len(a) > 2 and isinstance(a[2], list) else []) if v is not None])
        for sh in shells:
            if not isinstance(sh, Ref):
                continue
            _sn, sa = self.first(sh)
            faces = sa[1] if sa and len(sa) > 1 and isinstance(sa[1], list) else []
            for fref in faces:
                if not isinstance(fref, Ref):
                    continue
                f = self._face(fref)
                if f is not None:
                    s.faces.append(f)
        pts = list(s.points())
        if pts:
            s.box = tuple(min(p[k] for p in pts) for k in range(3)) + tuple(max(p[k] for p in pts) for k in range(3))
        s.thickness = _sheet_thickness(s)
        s.holes = _holes(s)
        s.bends = _bends(s)
        self._solids[sid] = s
        return s

    def _face(self, fref):
        n, a = self.first(fref, "ADVANCED_FACE")
        if n is None:
            n, a = self.first(fref, "FACE_SURFACE")
            if n is None:
                return None
        bounds, surf, same = a[1], a[2], (a[3] == "T")
        sn, sa = self.first(surf)
        points, arcs, lines = [], [], []
        for b in bounds or []:
            _bn, ba = self.first(b)
            if not ba:
                continue
            ln, la = self.first(ba[1])
            if ln == "VERTEX_LOOP":
                vn, va = self.first(la[1])
                if vn == "VERTEX_POINT":
                    points.append(self.pt(va[1]))
                continue
            if ln != "EDGE_LOOP":
                continue
            for oe in la[1]:
                _on, oa = self.first(oe, "ORIENTED_EDGE")
                if not oa:
                    continue
                en, ea = self.first(oa[3], "EDGE_CURVE")
                if not ea:
                    continue
                v1, v2 = self._vertex(ea[1]), self._vertex(ea[2])
                points.append(v1)
                points.append(v2)
                cn, ca = self.first(ea[3])
                if cn == "CIRCLE":
                    c = self.placement(ca[1])
                    r = ca[2] * self.scale
                    arcs.append((c, r, v1, v2, ea[4] != "F"))
                elif cn == "LINE":
                    lines.append((v1, v2))
        if sn == "PLANE":
            f = self.placement(sa[1])
            return Face(fref, "plane", f.o, f.z if same else _mul(f.z, -1.0), None, same, points, arcs, lines)
        if sn == "CYLINDRICAL_SURFACE":
            f = self.placement(sa[1])
            return Face(fref, "cylinder", f.o, f.z, sa[2] * self.scale, same, points, arcs, lines)
        return Face(fref, (sn or "other").lower(), None, None, None, same, points, arcs, lines)

    def _vertex(self, ref):
        _n, a = self.first(ref, "VERTEX_POINT")
        return self.pt(a[1]) if a else (0.0, 0.0, 0.0)


# ----------------------------------------------------------------- features

def _arc_span_deg(arc):
    """Angle swept by a circular edge. The edge runs from v1 to v2 along the
    circle's own direction (counter-clockwise about its axis) when its sense
    flag is true, the other way round when false."""
    frame, r, v1, v2, forward = arc
    if math.dist(v1, v2) < 1e-6:
        return 360.0
    def ang(p):
        q = _sub(p, frame.o)
        return math.atan2(dot(q, frame.y), dot(q, frame.x))
    d = (ang(v2) - ang(v1)) if forward else (ang(v1) - ang(v2))
    return math.degrees(d % (2 * math.pi))


def _axis_extent(face, axis_o, axis_d):
    ts = [dot(_sub(p, axis_o), axis_d) for p in face.points]
    return (min(ts), max(ts)) if ts else (0.0, 0.0)


def _concave(face):
    """A cylinder face whose outward normal points at its axis (material
    outside the cylinder): a hole wall or the inside of a bend."""
    return face.kind == "cylinder" and not face.same_sense


def _group_coaxial(faces, tol=0.02):
    groups = []
    for f in faces:
        for g in groups:
            h = g[0]
            if abs(h.radius - f.radius) < tol and abs(abs(dot(h.normal, f.normal)) - 1.0) < 1e-6 \
                    and line_distance(f.origin, h.origin, h.normal) < tol:
                g.append(f)
                break
        else:
            groups.append([f])
    return groups


def _holes(solid):
    """Concave cylinders that go all the way round. Coaxial faces are split first into runs along their axis (two
    tube walls are two holes), and each run must cover 359 degrees or more on its own: a slot's half-round end or a
    notch is no hole, even when another one sits on the same line further along (BASE's back band, D-129: its two
    end plates' slot ends, 2.4 m apart on one axis, had added up to one 'hole' each)."""
    cyl = [f for f in solid.faces if _concave(f)]
    holes = []
    for g in _group_coaxial(cyl):
        axis_o, axis_d = g[0].origin, g[0].normal
        ext = sorted(((_axis_extent(f, axis_o, axis_d), f) for f in g), key=lambda x: x[0])
        runs = []
        for (t0, t1), f in ext:
            if runs and t0 <= runs[-1][1] + 1e-3:
                runs[-1][1] = max(runs[-1][1], t1)
                runs[-1][2].append(f)
            else:
                runs.append([t0, t1, [f]])
        for t0, t1, fs in runs:
            span = sum(max([_arc_span_deg(a) for a in f.arcs if abs(a[1] - f.radius) < 1e-3] or [0.0]) for f in fs)
            if span < 359.0:
                continue
            c = _add(axis_o, _mul(axis_d, (t0 + t1) / 2.0))
            holes.append(Hole(solid.id, c, axis_d, 2.0 * g[0].radius, t1 - t0, [f.id for f in fs], t0, t1))
    return holes


def _sheet_thickness(solid):
    """Most common distance between opposite parallel planar faces that
    overlap in projection; None when the part has no such pairs."""
    planes = [f for f in solid.faces if f.kind == "plane" and f.points]
    counts = defaultdict(float)
    for i, a in enumerate(planes):
        for b in planes[i + 1:]:
            if dot(a.normal, b.normal) > -0.9999:
                continue
            d = dot(_sub(b.origin, a.origin), a.normal)
            if d >= 0 or -d > 30.0:
                continue
            area = _overlap_weight(a, b)
            if area > 0:
                counts[round(-d, 2)] += area
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _overlap_weight(a, b):
    """Rough overlap of two parallel faces' vertex boxes in their plane."""
    fr = Frame.from_axes(a.origin, a.normal, None)
    def box(f):
        us = [dot(_sub(p, fr.o), fr.x) for p in f.points]
        vs = [dot(_sub(p, fr.o), fr.y) for p in f.points]
        return min(us), max(us), min(vs), max(vs)
    ua0, ua1, va0, va1 = box(a)
    ub0, ub1, vb0, vb1 = box(b)
    du = min(ua1, ub1) - max(ua0, ub0)
    dv = min(va1, vb1) - max(va0, vb0)
    return du * dv if du > 0 and dv > 0 else 0.0


def _bends(solid):
    t = solid.thickness
    if not t:
        return []
    cyl = [f for f in solid.faces if f.kind == "cylinder"]
    inner = [f for f in cyl if _concave(f)]
    outer = [f for f in cyl if not _concave(f)]
    bends = []
    for f in inner:
        spans = [_arc_span_deg(a) for a in f.arcs if abs(a[1] - f.radius) < 1e-3]
        span = max(spans) if spans else 0.0
        if span >= 359.0 or span <= 0.5:
            continue
        for g in outer:
            if abs(abs(dot(f.normal, g.normal)) - 1.0) < 1e-6 and line_distance(g.origin, f.origin, f.normal) < 0.02 \
                    and abs((g.radius - f.radius) - t) < 0.05:
                bends.append(Bend(solid.id, f.origin, f.normal, f.radius, t, span))
                break
    # one bend per axis
    uniq = []
    for b in bends:
        if not any(abs(abs(dot(b.axis, u.axis)) - 1) < 1e-6 and line_distance(b.axis_point, u.axis_point, u.axis) < 0.05
                   for u in uniq):
            uniq.append(b)
    return uniq


def flat_plate(solid):
    """D-89 part 4: is the solid a plain flat plate cut from sheet? Returns (ok, thickness, why). Plain means:
    no bends; the faces parallel to the sheet lie at only its two skins (a third level is a pocket, a step or a
    rebate); every other plane stands square to the sheet (the cut edges); every cylinder runs square to the
    sheet through its full thickness (through-holes and rounded corners; a blind or cross hole is machined);
    and no other surface (a cone is a countersink)."""
    if solid.bends:
        return False, None, "it is folded (%d bends in its STEP)" % len(solid.bends)
    planes = [f for f in solid.faces if f.kind == "plane"]
    pts = list(solid.points())
    if not planes or not pts:
        return False, None, "its STEP has no flat faces"
    # the sheet's normal: of the plane directions, the one the solid is thinnest along
    dirs = []
    for f in planes:
        d = norm(f.normal)
        if not any(abs(abs(dot(d, e)) - 1.0) < 1e-4 for e in dirs):
            dirs.append(d)
    ext = lambda d: max(dot(p, d) for p in pts) - min(dot(p, d) for p in pts)
    n = min(dirs, key=ext)
    t = ext(n)
    across = [ext(d) for d in dirs if abs(dot(d, n)) < 1e-4]
    if not across:          # no side planes (a disc or a tube): the widest cylinder square to the sheet
        across = [max([2.0 * f.radius for f in solid.faces
                       if f.kind == "cylinder" and abs(abs(dot(norm(f.normal), n)) - 1.0) < 1e-4] or [0.0])]
    if t > 25.0 or t > 0.5 * min(across):
        return False, None, "it isn't a sheet part (%.1f thick across %.1f)" % (t, min(across))
    levels = []
    for f in solid.faces:
        if f.kind == "plane":
            c = abs(dot(norm(f.normal), n))
            if c > 0.9999:
                lv = dot(f.origin, n)
                if not any(abs(lv - x) < 0.02 for x in levels):
                    levels.append(lv)
            elif c > 1e-4:
                return False, None, "a face sits at an angle to the sheet (a chamfer or bevel)"
        elif f.kind == "cylinder":
            if abs(abs(dot(norm(f.normal), n)) - 1.0) > 1e-4:
                return False, None, "a cylinder runs across the sheet (a bend, a cross hole or a radius)"
        else:
            return False, None, "a %s face (a countersink or another machined form)" % f.kind
    if len(levels) != 2:
        return False, None, "its faces lie at %d levels through the thickness (a pocket, a step or a rebate)" % len(levels)
    lo, hi = min(levels), max(levels)
    for f in solid.faces:
        if f.kind == "cylinder" and f.points:
            ts = [dot(p, n) for p in f.points]
            if min(ts) > lo + 0.02 or max(ts) < hi - 0.02:
                return False, None, "a hole stops inside the thickness (a blind or tapped hole)"
    return True, round(hi - lo, 3), ""


def _edge_key(a, b):
    return frozenset((tuple(round(x, 3) for x in a), tuple(round(x, 3) for x in b)))


def _material_goes_on(solid, face, a, b, depth=0.0, normal=None, steps=4):
    """Across the straight edge a-b of `face`, does the part carry on (a wall meets it at the edge: a tube's corner,
    a channel's wall) rather than end (the edge face of a sheet or the side of a block, about as wide as the material
    the hole goes through, `depth`)? Read from the faces across the edge, so it holds whichever way the part is turned
    in the pod (a tube set at an angle in plan, like DL's diagonal bottom tube). A narrow face across the edge is
    looked across in turn: it ends the part when the wall's other side lies beyond it (a sheet's edge, a tube's end
    ring), and not when another wall does (a chamfered tube corner, like CEILING's seam members)."""
    normal = normal or face.normal
    d = norm(_sub(b, a))
    key = _edge_key(a, b)
    wide = max(2.5 * max(solid.thickness or 0.0, depth or 0.0), 4.0)
    for g in solid.faces:
        if g is face or not any(_edge_key(p, q) == key for p, q in g.lines):
            continue
        if g.kind == "cylinder":
            return True                           # a bend or a rounded corner starts there
        if g.kind != "plane" or not g.points or dot(g.normal, normal) < -0.9999:
            continue                              # the wall's other side: the part ends here
        # its width right at this edge: the nearest edge of it running alongside (a tube's end ring is the wall
        # thickness wide there, though it spans the whole tube); its full span when no edge runs alongside
        near = [(line_distance(_mul(_add(p, q), 0.5), a, d), (p, q)) for p, q in g.lines
                if _edge_key(p, q) != key and math.dist(p, q) > 1e-6 and abs(dot(norm(_sub(q, p)), d)) > 0.999]
        near = [x for x in near if x[0] > 1e-6]
        if not near:
            if max(line_distance(p, a, d) for p in g.points) > wide:
                return True
            continue
        across, far = min(near, key=lambda x: x[0])
        if across > wide:
            return True                           # a wall carries on
        if steps > 1 and _material_goes_on(solid, g, far[0], far[1], depth, normal, steps - 1):
            return True                           # a chamfer or a step on the way to the next wall
    return False


def _seg_distance(p, a, b):
    ab = _sub(b, a)
    L2 = dot(ab, ab)
    if L2 < 1e-12:
        return math.dist(p, a)
    t = max(0.0, min(1.0, dot(_sub(p, a), ab) / L2))
    return math.dist(p, _add(a, _mul(ab, t)))


def _on_cylinder(p, f, tol=0.05):
    return abs(line_distance(p, f.origin, f.normal) - f.radius) < tol


def free_edge_distances(solid, hole):
    """Every free straight edge of the face a hole is drilled through, as (distance from the hole centre,
    unit direction, foot of the perpendicular on the edge's line). An edge where the part carries on (a tube's
    corner or a channel's wall meeting it, read from the face across the edge) and an edge that starts a bend
    are not free edges; whichever way the part is turned in the pod."""
    bend_faces = [f for f in solid.faces if f.kind == "cylinder"
                  and not any(abs(a[1] - f.radius) < 1e-3 and _arc_span_deg(a) >= 359.0 for a in f.arcs)]
    out = []
    for f in solid.faces:
        if f.kind != "plane" or abs(abs(dot(f.normal, hole.axis)) - 1.0) > 1e-4:
            continue
        # the face must carry this hole's rim
        if not any(abs(a[1] - hole.diameter / 2.0) < 1e-3 and line_distance(a[0].o, hole.center, hole.axis) < 0.02
                   for a in f.arcs):
            continue
        c = _sub(hole.center, _mul(f.normal, dot(_sub(hole.center, f.origin), f.normal)))
        for a, b in f.lines:
            d = norm(_sub(b, a))
            if _material_goes_on(solid, f, a, b, hole.length):
                continue                          # a tube's corner or a channel's wall, not a free edge
            if any(_on_cylinder(a, bf) and _on_cylinder(b, bf) for bf in bend_faces):
                continue
            foot = _add(a, _mul(d, dot(_sub(c, a), d)))
            out.append((_seg_distance(c, a, b), d, foot))
    return out


def edge_distance(solid, hole):
    """Centre-to-edge distance of a hole, measured in the face it is drilled
    through: the nearest free straight boundary edge of that face, from the
    hole centre (see free_edge_distances). Returns (distance, kind) with kind
    'free edge', or (None, None)."""
    es = free_edge_distances(solid, hole)
    return (min(e[0] for e in es), "free edge") if es else (None, None)


def hole_to_bend(hole, bend):
    """Flat distance from a hole's edge to the start of a bend, measured
    in the flange the hole sits in. Only meaningful when the hole axis is
    perpendicular to the bend axis."""
    if abs(dot(hole.axis, bend.axis)) > 0.01:
        return None
    u = norm(cross(hole.axis, bend.axis))
    centre_to_axis = abs(dot(_sub(hole.center, bend.axis_point), u))
    return centre_to_axis - hole.diameter / 2.0


def world_box(solid, frame):
    pts = [frame.point(p) for p in solid.points()]
    if not pts:
        return None
    return tuple(min(p[k] for p in pts) for k in range(3)) + tuple(max(p[k] for p in pts) for k in range(3))


def box_gap(a, b):
    """Signed gap between two boxes: > 0 apart (largest separation on an
    axis), <= 0 overlapping (minus the smallest overlap depth)."""
    seps = [max(a[k] - b[k + 3], b[k] - a[k + 3]) for k in range(3)]
    return max(seps)
