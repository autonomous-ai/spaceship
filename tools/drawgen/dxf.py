"""A flat pattern's DXF, read without OCC (the read-back uses it too): lines, arcs, circles, polylines (their bulges
as arcs) and splines, each with its layer, and the layers' roles (cut outline, bend centre lines, bend zone edges)."""

import math


class Dxf:
    """The entities of a flat pattern DXF that drawgen draws and checks: lines, arcs, circles, polylines (bulges as
    arcs) and splines, each with its layer."""

    def __init__(self, path):
        self.path = path
        self.units = None
        self.lines, self.arcs, self.circles, self.splines = [], [], [], []
        self._read(path)

    def _read(self, path):
        with open(path, errors="replace") as fh:
            raw = [ln.rstrip("\r\n") for ln in fh]
        pairs = [(raw[i].strip(), raw[i + 1].strip()) for i in range(0, len(raw) - 1, 2)]
        for i, (c, v) in enumerate(pairs):
            if c == "9" and v == "$INSUNITS" and i + 1 < len(pairs):
                self.units = int(pairs[i + 1][1])
        ents, cur, sec = [], None, None
        for c, v in pairs:
            if c == "2" and v in ("ENTITIES", "BLOCKS", "TABLES", "HEADER", "OBJECTS", "CLASSES"):
                sec = v
            if sec != "ENTITIES":
                continue
            if c == "0":
                if cur is not None:
                    ents.append(cur)
                cur = (v, []) if v != "ENDSEC" else None
            elif cur is not None:
                cur[1].append((c, v))
        poly = None
        for typ, codes in ents:
            d = {}
            for c, v in codes:
                d.setdefault(c, []).append(v)
            lay = (d.get("8") or ["0"])[0]
            f = lambda c, j=0: float(d[c][j])
            if typ == "LINE":
                self.lines.append((lay, (f("10"), f("20")), (f("11"), f("21"))))
            elif typ == "CIRCLE":
                self.circles.append((lay, (f("10"), f("20")), f("40")))
            elif typ == "ARC":
                self.arcs.append((lay, (f("10"), f("20")), f("40"), f("50"), f("51")))
            elif typ == "LWPOLYLINE":
                xs, ys = d.get("10", []), d.get("20", [])
                bul = []
                # bulges follow their vertex: walk the codes in order
                vb, cur_b = [], None
                for c, v in codes:
                    if c == "10":
                        vb.append([float(v), None, 0.0])
                    elif c == "20" and vb:
                        vb[-1][1] = float(v)
                    elif c == "42" and vb:
                        vb[-1][2] = float(v)
                closed = int((d.get("70") or ["0"])[0]) & 1
                self._poly(lay, [(x, y, b_) for x, y, b_ in vb], closed)
            elif typ == "POLYLINE":
                poly = (lay, [], int((d.get("70") or ["0"])[0]) & 1)
            elif typ == "VERTEX" and poly is not None:
                poly[1].append((f("10"), f("20"), float((d.get("42") or ["0"])[0])))
            elif typ == "SEQEND" and poly is not None:
                self._poly(*poly)
                poly = None
            elif typ == "SPLINE":
                deg = int((d.get("71") or ["3"])[0])
                knots = [float(x) for x in d.get("40", [])]
                ctrl = [(float(x), float(y)) for x, y in zip(d.get("10", []), d.get("20", []))]
                self.splines.append((lay, deg, knots, ctrl))

    def _poly(self, lay, verts, closed):
        n = len(verts)
        for i in range(n if closed else n - 1):
            x0, y0, bul = verts[i]
            x1, y1, _b = verts[(i + 1) % n]
            if abs(bul) < 1e-12:
                self.lines.append((lay, (x0, y0), (x1, y1)))
                continue
            # a bulge: an arc of included angle 4 atan(bulge), counter-clockwise when positive
            th = 4 * math.atan(bul)
            ch = math.hypot(x1 - x0, y1 - y0)
            rad = ch / (2 * math.sin(abs(th) / 2))
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            h = math.sqrt(max(rad * rad - (ch / 2) ** 2, 0.0)) * (1 if abs(th) < math.pi else -1)
            nx, ny = -(y1 - y0) / ch, (x1 - x0) / ch
            sgn = 1 if bul > 0 else -1
            cx, cy = mx + sgn * h * nx, my + sgn * h * ny
            a0 = math.degrees(math.atan2(y0 - cy, x0 - cx))
            a1 = math.degrees(math.atan2(y1 - cy, x1 - cx))
            if bul < 0:
                a0, a1 = a1, a0
            self.arcs.append((lay, (cx, cy), rad, a0, a1))

    LAYER_ROLE = {"CUT": "cut", "OUTER_PROFILES": "cut", "INTERIOR_PROFILES": "cut", "BEND": "bend",
                  "MARK": "zone", "BEND_EXTENT": "zone"}

    def role(self, layer):
        return self.LAYER_ROLE.get(layer.upper(), "other")

    def bend_lines(self):
        return [(a, b) for lay, a, b in self.lines if self.role(lay) == "bend"]

    def zone_lines(self):
        return [(a, b) for lay, a, b in self.lines if self.role(lay) == "zone"]

    def cut_box(self):
        """The CUT outline's box (x0, y0, x1, y1): lines, arcs (their extremes), circles and spline control points."""
        xs, ys = [], []
        for lay, a, b in self.lines:
            if self.role(lay) == "cut":
                xs += [a[0], b[0]]
                ys += [a[1], b[1]]
        for lay, c, r, a0, a1 in self.arcs:
            if self.role(lay) != "cut":
                continue
            for k in range(0, 361, 5):
                ang = math.radians(k)
                if _in_arc(k, a0, a1):
                    xs.append(c[0] + r * math.cos(ang))
                    ys.append(c[1] + r * math.sin(ang))
            for ang in (a0, a1):
                xs.append(c[0] + r * math.cos(math.radians(ang)))
                ys.append(c[1] + r * math.sin(math.radians(ang)))
        for lay, deg, kn, ctrl in self.splines:
            if self.role(lay) == "cut":
                xs += [p[0] for p in ctrl]
                ys += [p[1] for p in ctrl]
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _in_arc(k, a0, a1):
    a0, a1, k = a0 % 360, a1 % 360, k % 360
    return (a0 <= k <= a1) if a0 <= a1 else (k >= a0 or k <= a1)


