"""C01 seal line: the pod's floor seal line, traced as closed rings in horizontal cuts (the Lead's ask, 2026-11-01).

Two open paths into the pod were found by eye on 2026-11-01, both from the floor to Z 105: at the fixed glass's door
end (D-150) and on the door's hinge side. This check finds them, and any like them, from the CAD.

- The assembly is cut by horizontal planes from the room floor (Z 0) up to the band's top (the skeleton's glide_h +
  band_h, Z 110): one cut in the middle of every height step between two heights where a part's outline can change
  (a vertex, the top or bottom of a round edge or of a hole lying down), and cuts 1 mm apart where a round face makes
  the outline curve, so each opening's area is summed right.
- Each part's outline in a cut is exact, from its STEP faces: a flat face gives straight lines, an upright round face
  an arc, a round face lying down (a hole through an upright wall) straight lines along its axis.
- The outlines are laid on rows 0.1 mm apart (exact along each row), and on columns the same, to see which parts
  touch. A cut is sealed when the pod's inside (the open middle of the plan) is ringed by parts that touch or come
  within 1 mm of each other. If it isn't, the gaps between parts are added shortest first: the first one that closes
  a ring round the inside is the widest gap of the best ring (the ring whose widest gap is least), and every gap on
  that ring wider than 1 mm is an opening, with its width, its place and the parts on each side.
- An opening found in cut after cut is one opening: its height range, its narrowest and widest width, and its open
  area (width times height, summed over the cuts) are reported, with the total for the Air Engineer.

The door's drop seal is modelled up, flush with the kick strip's bottom; in use it drops to the room floor. A part
named in config/seal-travel.csv is taken down by its travel, to the floor when that is within reach. Space holders
(reserved air spaces, zones and routes) are not parts and are left out.
"""

import bisect
import glob
import math
import os
import re

import numpy as np

from common import CHECKS_DIR, Finding, num, owner_for, read_csv, reserved_label, reserved_spaces

SEAL_GAP = 1.0          # the Lead's ask: every gap wider than 1 mm
ROW_H = 0.25            # the rows' pitch (mm) along X, which say what touches; each row is exact along its length
TRY_H = 0.5             # the pitch of the rows in the other directions, which only offer gaps to try (each measured
                        # exactly afterwards); no part at floor level is thinner, so none falls between two rows
CURVE_STEP = 1.0        # cuts this far apart (mm) in a height step where a round face makes an outline curve
ARC_SAGITTA = 0.01      # an arc in a cut is drawn as lines no further than this from it (mm)
SPACE_HOLDER = re.compile(r"\bRESERVED\b|\bZONE\b|\bROUTE\b")
TWO_PI = 2.0 * math.pi
DIRECTIONS = (0.0, 90.0, 45.0, 135.0)   # the rows' directions (degrees from +X): along X first, which says what touches


# ----------------------------------------------------------------- inputs

def band_top(root):
    """(Z of the band's top, its source): the skeleton's glide_h + band_h, or 110 with a note."""
    vals = {}
    for p in sorted(glob.glob(os.path.join(root, "v2/01-CAD-Native/skeleton/*_POD-SKELETON-PARAMETERS.csv")),
                    reverse=True):
        for row in read_csv(p):
            k = (row.get("name") or row.get("parameter") or "").strip()
            if k in ("glide_h", "band_h") and k not in vals:
                vals[k] = num(row.get("value") or row.get("expression"))
        break
    if vals.get("glide_h") is not None and vals.get("band_h") is not None:
        return vals["glide_h"] + vals["band_h"], "the skeleton's glide_h + band_h"
    return 110.0, "Z 110, the band's top (assumption: no skeleton table read)"


def load_travel(root):
    """[(compiled pattern, travel mm, source)] from config/seal-travel.csv."""
    p = os.path.join(root, CHECKS_DIR, "config", "seal-travel.csv")
    out = []
    if os.path.exists(p):
        for r in read_csv(p):
            pat, t = (r.get("pattern") or "").strip(), num(r.get("travel_mm"))
            if pat and t:
                out.append((re.compile(pat, re.I), t, (r.get("source") or "").strip()))
    return out


# ----------------------------------------------------------------- faces in pod coordinates

class _WFace:
    __slots__ = ("kind", "o", "ax", "r", "half", "edges", "zlo", "zhi")


def _ang(o, ex, ey, p):
    d = (p[0] - o[0], p[1] - o[1], p[2] - o[2])
    return math.atan2(d[0] * ey[0] + d[1] * ey[1] + d[2] * ey[2], d[0] * ex[0] + d[1] * ex[1] + d[2] * ex[2])


def _unit(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / n, v[1] / n, v[2] / n) if n > 0 else v


def world_faces(body, cache={}):
    """The body's faces in pod coordinates: kind (plane, cyl, cone, other), a point o and the normal or axis ax, the
    radius r (and the cone's half angle), edges as ("seg", a, b) or ("arc", centre, ex, ey, r, start, span) with the
    arc running anticlockwise about ex x ey from its start angle, and the face's height range."""
    pre = getattr(body, "wfaces", None)
    if pre is not None:                           # a shape built in pod coordinates (tests, saved model cuts)
        return pre
    key = (id(body.solid), id(body.frame))
    if key in cache:
        return cache[key]
    fr = body.frame
    out = []
    for f in body.solid.faces:
        if not f.points:
            continue
        pts = [fr.point(p) for p in f.points]
        w = _WFace()
        w.zlo, w.zhi = min(p[2] for p in pts), max(p[2] for p in pts)
        w.edges = []
        for kind, v1, v2, data in getattr(f, "edges", ()) or ():
            a, b = fr.point(v1), fr.point(v2)
            if kind == "circle":
                c, r, sense = data
                o = fr.point(c.o)
                ex, ey = _unit(fr.vector(c.x)), _unit(fr.vector(c.y))
                t1, t2 = _ang(o, ex, ey, a), _ang(o, ex, ey, b)
                start, end = (t1, t2) if sense else (t2, t1)
                span = (end - start) % TWO_PI
                if span < 1e-9:
                    span = TWO_PI                       # a whole circle, one edge from a vertex back to it
                w.edges.append(("arc", o, ex, ey, r, start, span))
                # an upright circle's top and bottom are outline changes too
                zr = r * math.hypot(ex[2], ey[2])
                for z in (o[2] - zr, o[2] + zr):
                    w.zlo, w.zhi = min(w.zlo, z), max(w.zhi, z)
            else:
                w.edges.append(("seg", a, b))
        w.o, w.ax, w.r, w.half = None, None, None, None
        if f.kind == "plane":
            w.kind, w.o, w.ax = "plane", fr.point(f.origin), _unit(fr.vector(f.normal))
        elif f.kind == "cylinder":
            w.kind, w.o, w.ax, w.r = "cyl", fr.point(f.origin), _unit(fr.vector(f.normal)), f.radius
        elif getattr(f, "cone", None):
            o, ax, r, half = f.cone
            w.kind, w.o, w.ax, w.r, w.half = "cone", fr.point(o), _unit(fr.vector(ax)), r, half
        else:
            w.kind = "other"
        out.append(w)
    cache[key] = out
    return out


def outline_heights(wfaces):
    """Heights where the outline can change: every vertex, every arc's top and bottom, a lying-down round face's top
    and bottom; and whether a face curves the outline (a round face that isn't upright) between them."""
    zs, curved = set(), []
    for w in wfaces:
        for e in w.edges:
            if e[0] == "seg":
                zs.add(e[1][2])
                zs.add(e[2][2])
        zs.add(w.zlo)
        zs.add(w.zhi)
        if w.kind in ("cyl", "cone") and abs(w.ax[2]) < 1.0 - 1e-6:
            curved.append((w.zlo, w.zhi))
            if w.kind == "cyl" and abs(w.ax[2]) < 1e-6:
                for z in (w.o[2] - w.r, w.o[2] + w.r):
                    if w.zlo - 1e-6 <= z <= w.zhi + 1e-6:
                        zs.add(z)
    return zs, curved


# ----------------------------------------------------------------- one face, one cut

def _edge_cross(e, z0):
    """Where an edge crosses the plane Z = z0: a list of (x, y)."""
    if e[0] == "seg":
        a, b = e[1], e[2]
        da, db = a[2] - z0, b[2] - z0
        if (da < 0) != (db < 0) and da != db:
            t = da / (da - db)
            return [(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))]
        return []
    _k, o, ex, ey, r, start, span = e
    A, B, D = r * ex[2], r * ey[2], z0 - o[2]
    R = math.hypot(A, B)
    if R < 1e-12 or abs(D) >= R:
        return []
    phi, dl = math.atan2(B, A), math.acos(D / R)
    out = []
    for th in (phi + dl, phi - dl):
        if (th - start) % TWO_PI < span:
            c, s = math.cos(th), math.sin(th)
            out.append((o[0] + r * (c * ex[0] + s * ey[0]), o[1] + r * (c * ex[1] + s * ey[1])))
    return out


def _arc_pts(cx, cy, r, a0, a1):
    n = max(2, int(math.ceil((a1 - a0) / (2.0 * math.acos(max(-1.0, 1.0 - ARC_SAGITTA / r))))) + 1) if r > 0 else 2
    ts = np.linspace(a0, a1, n)
    return list(zip(cx + r * np.cos(ts), cy + r * np.sin(ts)))


def _upright_inside(w, cx, cy, rad, alpha, z0):
    """Is the point at angle alpha on an upright round face, at height z0, inside the face? The face's edges are
    counted where they pass over it (an even-odd count up the face)."""
    px, py = cx + rad * math.cos(alpha), cy + rad * math.sin(alpha)
    n = 0
    for e in w.edges:
        if e[0] == "arc":
            _k, o, ex, ey, r, start, span = e
            if abs(ex[2]) > 1e-6 or abs(ey[2]) > 1e-6:
                continue                                # not a level circle of the face
            if o[2] <= z0:
                continue
            p = (px, py, o[2])
            if (_ang(o, ex, ey, p) - start) % TWO_PI < span:
                n += 1
        else:
            a, b = e[1], e[2]
            ta = math.atan2(a[1] - cy, a[0] - cx)
            tb = math.atan2(b[1] - cy, b[0] - cx)
            d = (tb - ta + math.pi) % TWO_PI - math.pi  # the short way round
            if abs(d) < 1e-12:
                continue                                # an upright seam
            u = (alpha - ta + math.pi) % TWO_PI - math.pi
            if (0 <= u < d) if d > 0 else (d < u <= 0):
                z = a[2] + (b[2] - a[2]) * (u / d)
                if z > z0:
                    n += 1
    return n % 2 == 1


def face_cut(w, z0):
    """A face's outline in the cut at z0, as 2D segments ((x1, y1), (x2, y2))."""
    if not (w.zlo < z0 < w.zhi):
        return [], 0
    pts = []
    for e in w.edges:
        pts.extend(_edge_cross(e, z0))
    bad = 0
    if w.kind == "plane":
        n = w.ax
        if abs(n[2]) > 1.0 - 1e-9:
            return [], 0
        d = (n[1], -n[0])
        pts.sort(key=lambda p: p[0] * d[0] + p[1] * d[1])
        if len(pts) % 2:
            return [], 1
        return [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)], 0
    if w.kind in ("cyl", "cone") and abs(w.ax[2]) > 1.0 - 1e-6:
        cx, cy = w.o[0], w.o[1]
        rad = w.r
        if w.kind == "cone":
            rad = w.r + (z0 - w.o[2]) * w.ax[2] * math.tan(w.half)
        if rad <= 1e-9:
            return [], 0
        angs = sorted(math.atan2(p[1] - cy, p[0] - cx) for p in pts)
        segs = []
        if not angs:
            if _upright_inside(w, cx, cy, rad, 0.0, z0):
                ring = _arc_pts(cx, cy, rad, 0.0, TWO_PI)
                segs = list(zip(ring[:-1], ring[1:]))
            return segs, 0
        for i, a0 in enumerate(angs):
            a1 = angs[i + 1] if i + 1 < len(angs) else angs[0] + TWO_PI
            if a1 - a0 < 1e-12:
                continue
            if _upright_inside(w, cx, cy, rad, 0.5 * (a0 + a1), z0):
                arc = _arc_pts(cx, cy, rad, a0, a1)
                segs.extend(zip(arc[:-1], arc[1:]))
        return segs, 0
    if w.kind == "cyl" and abs(w.ax[2]) < 1e-6:
        c = (z0 - w.o[2]) / w.r
        if abs(c) >= 1.0:
            return [], 0
        wv = (w.ax[1], -w.ax[0])
        sides = {}
        for p in pts:
            s = (p[0] - w.o[0]) * wv[0] + (p[1] - w.o[1]) * wv[1]
            sides.setdefault(s > 0, []).append(p)
        segs = []
        for side in sides.values():
            side.sort(key=lambda p: p[0] * w.ax[0] + p[1] * w.ax[1])
            if len(side) % 2:
                bad += 1
                continue
            segs.extend((side[i], side[i + 1]) for i in range(0, len(side), 2))
        return segs, bad
    # any other face (a slanted round face, a cone lying down, a free-form face): its edges' crossings, paired
    # along the line they spread on (its straight chords stand for it)
    if len(pts) < 2:
        return [], 1 if pts else 0
    P = np.array(pts)
    m = P.mean(axis=0)
    u, s, vt = np.linalg.svd(P - m)
    d = vt[0]
    pts.sort(key=lambda p: p[0] * d[0] + p[1] * d[1])
    if len(pts) % 2:
        return [], 1
    return [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)], 0


def body_cut(wfaces, z0):
    """A body's outline in the cut at z0: (array of segments x1, y1, x2, y2; faces whose crossings didn't pair)."""
    segs, bad = [], 0
    for w in wfaces:
        s, b = face_cut(w, z0)
        segs.extend(s)
        bad += b
    if not segs:
        return np.zeros((0, 4)), bad
    return np.array([(a[0], a[1], b[0], b[1]) for a, b in segs], dtype=float), bad


# ----------------------------------------------------------------- outlines on rows

def _crossings(segs, lo, h, n):
    """Each segment's crossings with the rows' centre lines (row j at lo + (j + 0.5) h), the rows running along the
    segments' first coordinate: (row index array, coordinate along the row array), sorted by row then position,
    and a mask of rows whose crossings don't pair (an outline not closed there)."""
    if not len(segs):
        return np.zeros(0, int), np.zeros(0), np.zeros(n, bool)
    x1, y1, x2, y2 = segs[:, 0], segs[:, 1], segs[:, 2], segs[:, 3]
    ya, yb = np.minimum(y1, y2), np.maximum(y1, y2)
    keep = yb - ya > 1e-12
    x1, y1, x2, y2, ya, yb = x1[keep], y1[keep], x2[keep], y2[keep], ya[keep], yb[keep]
    j0 = np.maximum(np.ceil((ya - lo) / h - 0.5).astype(np.int64), 0)
    j1 = np.minimum(np.ceil((yb - lo) / h - 0.5).astype(np.int64) - 1, n - 1)
    cnt = np.maximum(j1 - j0 + 1, 0)
    tot = int(cnt.sum())
    if tot == 0:
        return np.zeros(0, int), np.zeros(0), np.zeros(n, bool)
    si = np.repeat(np.arange(len(cnt)), cnt)
    first = np.repeat(np.cumsum(cnt) - cnt, cnt)
    rows = j0[si] + (np.arange(tot) - first)
    yc = lo + (rows + 0.5) * h
    x = x1[si] + (yc - y1[si]) * (x2[si] - x1[si]) / (y2[si] - y1[si])
    order = np.lexsort((x, rows))
    rows, x = rows[order], x[order]
    odd = np.bincount(rows, minlength=n) % 2 == 1
    return rows, x, odd


class Raster:
    """Every part's outline in one cut, laid on rows: rows run along the direction at angle theta from +X, row j at
    v = lo + (j + 0.5) h across them (u along a row = x cos + y sin, v = -x sin + y cos). Per row its solid spans
    (start, end), exact along the row, each with the parts at its two ends (sb, eb)."""

    def __init__(self, cuts, theta, box, h=ROW_H):
        self.theta, self.h = theta, h
        self.c, self.sn = math.cos(theta), math.sin(theta)
        x0, y0, x1, y1 = box
        vs = [-x * self.sn + y * self.c for x in (x0, x1) for y in (y0, y1)]
        self.lo = min(vs)
        self.n = int(math.ceil((max(vs) - self.lo) / h))
        R, S, E, B = [], [], [], []
        self.open_rows = 0
        for bid, segs in cuts:
            if not len(segs):
                continue
            u1 = segs[:, 0] * self.c + segs[:, 1] * self.sn
            v1 = -segs[:, 0] * self.sn + segs[:, 1] * self.c
            u2 = segs[:, 2] * self.c + segs[:, 3] * self.sn
            v2 = -segs[:, 2] * self.sn + segs[:, 3] * self.c
            rows, x, odd = _crossings(np.stack([u1, v1, u2, v2], axis=1), self.lo, h, self.n)
            if not len(rows):
                continue
            if odd.any():
                self.open_rows += int(odd.sum())
                ok = ~odd[rows]
                rows, x = rows[ok], x[ok]
            R.append(rows[0::2])
            S.append(x[0::2])
            E.append(x[1::2])
            B.append(np.full(len(rows) // 2, bid))
        if R:
            R, S, E, B = np.concatenate(R), np.concatenate(S), np.concatenate(E), np.concatenate(B)
        else:
            R, S, E, B = np.zeros(0, np.int64), np.zeros(0), np.zeros(0), np.zeros(0, np.int64)
        order = np.lexsort((S, R))
        R, S, E, B = R[order], S[order], E[order], B[order]
        # join spans that overlap or touch, row by row
        K = 1e5
        run = np.maximum.accumulate(R * K + E) if len(R) else R * 1.0
        prev = np.concatenate(([-np.inf], run[:-1]))
        new = (R * K + S) > prev + 1e-9
        gid = np.cumsum(new) - 1
        ng = int(gid[-1] + 1) if len(gid) else 0
        self.row = np.zeros(ng, np.int64)
        self.s, self.e = np.full(ng, np.inf), np.full(ng, -np.inf)
        self.sb, self.eb = np.zeros(ng, np.int64), np.zeros(ng, np.int64)
        if ng:
            self.row[gid] = R
            np.minimum.at(self.s, gid, S)
            np.maximum.at(self.e, gid, E)
            self.sb = B[np.flatnonzero(new)]
            o2 = np.lexsort((E, gid))
            self.eb[gid[o2]] = B[o2]                    # the part reaching furthest: written last
        self.start = np.searchsorted(self.row, np.arange(self.n + 1))
        self.K = K

    def centre(self, j):
        return self.lo + (np.asarray(j) + 0.5) * self.h

    def spans(self, j):
        return self.start[j], self.start[j + 1]

    def world(self, u, v):
        return u * self.c - v * self.sn, u * self.sn + v * self.c

    def local(self, x, y):
        return x * self.c + y * self.sn, -x * self.sn + y * self.c

    def find(self, j, x, tol=1e-6):
        """The span of row j holding x, or -1 (scalars)."""
        k = self.find_many(np.array([j]), np.array([x]), tol)[0]
        return int(k)

    def find_many(self, js, xs, tol=1e-6):
        """For each (row, position along it): the span holding it, or -1."""
        out = np.full(len(js), -1, np.int64)
        if not len(self.s) or not len(js):
            return out
        ok = (js >= 0) & (js < self.n)
        key = js * self.K + xs
        k = np.searchsorted(self.row * self.K + self.s, key + tol, side="right") - 1
        kk = np.clip(k, 0, len(self.s) - 1)
        hit = ok & (k >= 0) & (self.row[kk] == js) & (self.e[kk] >= xs - tol)
        out[hit] = kk[hit]
        return out


# ----------------------------------------------------------------- rings round the inside

class _UF:
    """Union-find with each node's offset from its root: the times a path crosses the ray from the inside point
    (upward +1). Joining two nodes already joined with a different offset closes a ring round the inside."""

    def __init__(self, n):
        self.p = list(range(n))
        self.w = [0] * n

    def find(self, a):
        path = []
        while self.p[a] != a:
            path.append(a)
            a = self.p[a]
        root, acc = a, 0
        for x in reversed(path):
            acc += self.w[x]
            self.w[x] = acc
            self.p[x] = root
        return root

    def join(self, a, b, d):
        """pot(b) = pot(a) + d. Returns 'joined', 'same' or 'ring'."""
        ra, rb = self.find(a), self.find(b)
        oa, ob = (self.w[a] if a != ra else 0), (self.w[b] if b != rb else 0)
        if ra == rb:
            return "same" if ob - oa == d else "ring"
        self.p[rb] = ra
        self.w[rb] = oa + d - ob
        return "joined"


def _labels(n, u, v):
    """Connected components of n nodes joined by edges u-v: each node's smallest member (vectorized)."""
    lab = np.arange(n)
    if not len(u):
        return lab
    while True:
        a, b = lab[u], lab[v]
        if (a == b).all():
            return lab
        m = np.minimum(a, b)
        np.minimum.at(lab, a, m)
        np.minimum.at(lab, b, m)
        while True:
            l2 = lab[lab]
            if (l2 == lab).all():
                break
            lab = l2


def _seed(rows, target=(0.0, 0.0), need=200.0):
    """A point in the open middle of the plan: on the row nearest the target (then rows 50 mm apart round it), a
    free stretch at least `need` long, within 900 mm of the target; (row, x)."""
    h = rows.h
    j0 = int((target[1] - rows.lo) / h)
    for k in range(0, 40):
        for j in ((j0 + int(k * 50 / h)), (j0 - int(k * 50 / h))):
            if j < 0 or j >= rows.n - 1:
                continue
            a, b = rows.spans(j)
            ends = [-1e9] + list(rows.e[a:b])
            starts = list(rows.s[a:b]) + [1e9]
            best = None
            for g0, g1 in zip(ends, starts):
                lo_, hi_ = max(g0, -1250.0), min(g1, 1250.0)
                if hi_ - lo_ < need:
                    continue
                x = min(max(target[0], lo_ + need / 2), hi_ - need / 2)
                score = abs(x - target[0])
                if best is None or score < best[0]:
                    best = (score, x)
            if best is not None and best[0] < 900.0:
                return j, best[1]
    return None


def _ray_offset(xa, ya, xb, yb, xs, yr):
    """Signed crossings of the segments a-b with the ray from (xs, yr) along +X (arrays)."""
    up = (ya < yr) & (yb > yr)
    dn = (ya > yr) & (yb < yr)
    t = np.where(up | dn, (yr - ya) / np.where(yb != ya, yb - ya, 1.0), 0.0)
    xc = xa + t * (xb - xa)
    return np.where(up & (xc > xs), 1, 0) - np.where(dn & (xc > xs), 1, 0)


def ring_gaps(rows, others=(), seed=None):
    """The gaps on the narrowest ring of parts round the inside in one cut.

    rows: the cut on rows along X (the main raster, which says what touches); others: the same cut on rows in other
    directions, which only add gaps to try. Returns (state, gaps, info): state 'sealed' (parts touch or come within
    1 mm all round), 'open' (gaps listed: width, the two points, the parts on each side), 'no ring' (no ring of parts
    round the inside even across every gap) or 'no inside' (no open middle found)."""
    if seed is None:
        seed = _seed(rows)
    if seed is None:
        return "no inside", [], {}
    js, xs = seed
    ys = float(rows.centre(js))
    yr = ys + rows.h / 2.0                       # the ray: from the inside point along +X, between rows js and js + 1
    info = {"seed": (xs, ys)}
    ns = len(rows.s)
    if not ns:
        return "no ring", [], info
    # spans of neighbouring rows that overlap (or touch) are one solid
    keyS, keyE = rows.row * rows.K + rows.s, rows.row * rows.K + rows.e
    q = np.flatnonzero(rows.row > 0)
    lo = np.searchsorted(keyE, (rows.row[q] - 1) * rows.K + rows.s[q] - 1e-6, side="left")
    hi = np.searchsorted(keyS, (rows.row[q] - 1) * rows.K + rows.e[q] + 1e-6, side="right")
    cnt = np.maximum(hi - lo, 0)
    qq = np.repeat(q, cnt)
    pp = np.repeat(lo, cnt) + (np.arange(int(cnt.sum())) - np.repeat(np.cumsum(cnt) - cnt, cnt))
    # an overlap between rows js and js + 1 right of the inside point crosses the ray: cut there
    cross = (rows.row[pp] == js) & (np.maximum(rows.s[pp], rows.s[qq]) > xs)
    lab = _labels(ns, pp[~cross], qq[~cross])
    comps, comp_of = np.unique(lab, return_inverse=True)
    uf = _UF(len(comps))
    forest = {}                                  # the joins made, to walk a ring back: solid -> [(solid, gap)]
    ca, cb = comp_of[pp[cross]], comp_of[qq[cross]]
    for a, b in sorted(set(zip(ca.tolist(), cb.tolist()))):
        r = uf.join(a, b, 1)
        if r == "ring":
            return "sealed", [], info
        if r == "joined":                        # the same solid, across the ray: no gap
            forest.setdefault(a, []).append((b, {"width": 0.0}))
            forest.setdefault(b, []).append((a, {"width": 0.0}))
    # gaps to try: between neighbouring spans along every row of every raster
    C = []
    for r in (rows,) + tuple(others):
        k = np.flatnonzero(r.row[:-1] == r.row[1:])
        if not len(k):
            continue
        g = r.s[k + 1] - r.e[k]
        vrow = r.centre(r.row[k])
        da = np.minimum(0.2, 0.5 * (r.e[k] - r.s[k]))
        db = np.minimum(0.2, 0.5 * (r.e[k + 1] - r.s[k + 1]))
        ax, ay = r.world(r.e[k] - da, vrow)
        bx, by = r.world(r.s[k + 1] + db, vrow)
        C.append((g, ax, ay, bx, by, r.eb[k], r.sb[k + 1], r.world(r.e[k], vrow), r.world(r.s[k + 1], vrow)))
    if not C:
        return "no ring", [], info
    g = np.concatenate([c[0] for c in C])
    ax, ay, bx, by = (np.concatenate([c[i] for c in C]) for i in (1, 2, 3, 4))
    pa, pb = np.concatenate([c[5] for c in C]), np.concatenate([c[6] for c in C])
    ex_a = np.concatenate([c[7][0] for c in C]), np.concatenate([c[7][1] for c in C])
    ex_b = np.concatenate([c[8][0] for c in C]), np.concatenate([c[8][1] for c in C])
    # each end into the main rows: the row whose centre is nearest, or the next one either side
    def node_of(x, y):
        j = np.rint((y - rows.lo) / rows.h - 0.5).astype(np.int64)
        k = rows.find_many(j, x)
        for dj in (1, -1, 2, -2):
            miss = k < 0
            if not miss.any():
                break
            k2 = rows.find_many(j[miss] + dj, x[miss])
            k[np.flatnonzero(miss)] = k2
        return k
    na, nb = node_of(ax, ay), node_of(bx, by)
    ok = (na >= 0) & (nb >= 0)
    # not through the inside point itself
    dx, dy = bx - ax, by - ay
    L2 = np.where(dx * dx + dy * dy > 0, dx * dx + dy * dy, 1.0)
    t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
    ok &= np.hypot(ax + t * dx - xs, ay + t * dy - ys) > 1.0
    idx = np.flatnonzero(ok)
    if not len(idx):
        return "no ring", [], info
    na, nb = na[idx], nb[idx]
    ya_s, yb_s = rows.centre(rows.row[na]), rows.centre(rows.row[nb])
    off = _ray_offset(ax[idx], ya_s, bx[idx], yb_s, xs, yr)
    cA, cB = comp_of[na], comp_of[nb]
    # one gap per pair of solids and way round (the shortest): another between the same two, the same way round,
    # closes no ring the first doesn't
    lo_c, hi_c = np.minimum(cA, cB), np.maximum(cA, cB)
    off_n = np.where(cA <= cB, off, -off)
    order = np.lexsort((g[idx], off_n, hi_c, lo_c))
    keyc = np.stack([lo_c[order], hi_c[order], off_n[order]], axis=1)
    first = np.ones(len(order), bool)
    first[1:] = (keyc[1:] != keyc[:-1]).any(axis=1)
    pick = idx[order[first]]
    pick_local = order[first]
    rec = sorted(zip(g[pick].tolist(), pick_local.tolist()), key=lambda t: t[0])
    for width, li in rec:
        a, b, d = int(cA[li]), int(cB[li]), int(off[li])
        res = uf.join(a, b, d)
        gi = idx[li]
        gap = {"width": width, "a": (float(ex_a[0][gi]), float(ex_a[1][gi])), "b": (float(ex_b[0][gi]), float(ex_b[1][gi])),
               "parts": (int(pa[gi]), int(pb[gi]))}
        if res == "joined":
            forest.setdefault(a, []).append((b, gap))
            forest.setdefault(b, []).append((a, gap))
        elif res == "ring":
            if width <= SEAL_GAP:
                return "sealed", [], info
            ring = [gap] + _forest_path(forest, a, b)
            info["widest"] = width
            return "open", [x for x in ring if x["width"] > SEAL_GAP], info
    return "no ring", [], info


def _forest_path(forest, a, b):
    """The gaps on the forest's path between solids a and b."""
    if a == b:
        return []
    prev = {a: None}
    stack = [a]
    while stack:
        u = stack.pop()
        if u == b:
            break
        for v, c in forest.get(u, ()):
            if v not in prev:
                prev[v] = (u, c)
                stack.append(v)
    out = []
    u = b
    while prev.get(u) is not None:
        u, c = prev[u]
        out.append(c)
    return out


# ----------------------------------------------------------------- exact widths

def _seg_dist(P, Q):
    """Least distance between two sets of 2D segments, and the closest points: (d, p, q)."""
    best = (np.inf, None, None)
    if not len(P) or not len(Q):
        return best

    def pt_seg(pts, segs):
        a, b = segs[:, None, 0:2], segs[:, None, 2:4]
        ab = b - a
        L = (ab ** 2).sum(-1)
        t = np.clip(((pts[None, :, :] - a) * ab).sum(-1) / np.where(L > 0, L, 1.0), 0.0, 1.0)
        proj = a + t[..., None] * ab
        d = np.sqrt(((pts[None, :, :] - proj) ** 2).sum(-1))
        return d, proj

    for A, Bs, flip in ((P, Q, False), (Q, P, True)):
        pts = np.concatenate([A[:, 0:2], A[:, 2:4]])
        d, proj = pt_seg(pts, Bs)
        k = np.unravel_index(np.argmin(d), d.shape)
        if d[k] < best[0]:
            p, q = tuple(pts[k[1]]), tuple(proj[k])
            best = (float(d[k]), q, p) if flip else (float(d[k]), p, q)
    return best


def refine(gap, cuts_by_id, window=5.0):
    """The gap's exact width: the least distance between the two parts' outlines near it (the rows and columns
    measure along X and Y only, so a slanted gap reads wider there)."""
    (ax, ay), (bx, by) = gap["a"], gap["b"]
    mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
    rad = gap["width"] / 2.0 + window
    pa, pb = gap["parts"]

    def near(segs):
        if not len(segs):
            return segs
        lo = np.minimum(segs[:, 0:2], segs[:, 2:4])
        hi = np.maximum(segs[:, 0:2], segs[:, 2:4])
        keep = (lo[:, 0] <= mx + rad) & (hi[:, 0] >= mx - rad) & (lo[:, 1] <= my + rad) & (hi[:, 1] >= my - rad)
        return segs[keep]

    P, Q = near(cuts_by_id.get(pa, np.zeros((0, 4)))), near(cuts_by_id.get(pb, np.zeros((0, 4))))
    if pa == pb or not len(P) or not len(Q):
        return gap
    d, p, q = _seg_dist(P, Q)
    if d < gap["width"] - 1e-6:
        g = dict(gap)
        g.update({"width": d, "a": p, "b": q})
        return g
    return gap


# ----------------------------------------------------------------- the whole floor band

def _part_label(body):
    return body.label.split(" / ")[-2] if " / " in body.label else body.label


def cut_heights(wf_by_id, z_lo, z_hi, extra=()):
    """The cuts: the middle of each step between outline-change heights, and 1 mm apart in a step a round face
    curves. Returns [(z, step bottom, step top)], each cut standing for its share of the step."""
    zs, curved = {z_lo, z_hi}, []
    for wfs in wf_by_id.values():
        z, c = outline_heights(wfs)
        zs |= {v for v in z if z_lo < v < z_hi}
        curved.extend(c)
    zs |= {v for v in extra if z_lo < v < z_hi}
    zs = sorted(zs)
    steps = []
    for a in zs:
        if not steps or a - steps[-1] > 1e-3:
            steps.append(a)
    out = []
    for a, b in zip(steps[:-1], steps[1:]):
        bent = any(lo < b - 1e-6 and hi > a + 1e-6 for lo, hi in curved)
        k = max(1, int(math.ceil((b - a) / CURVE_STEP))) if bent else 1
        for i in range(k):
            lo_, hi_ = a + (b - a) * i / k, a + (b - a) * (i + 1) / k
            out.append(((lo_ + hi_) / 2.0, lo_, hi_))
    return out


def seal_line(bodies, z_top, travel=(), reserved=None, xy=(-1260.0, -860.0, 1260.0, 860.0), z_floor=0.0,
              heights=None, log=None):
    """Trace the seal line from the floor to z_top. Returns (openings, cuts): each opening a dict with its width
    range, place, parts, height range and open area (mm^2); cuts the per-cut states."""
    reserved = reserved or {}
    use = []
    for b in bodies:
        if b.box is None or b.box[2] >= z_top or b.box[5] <= z_floor:
            if not any(p.search(b.label) for p, _t, _s in travel):
                continue
        name = b.label.upper()
        if SPACE_HOLDER.search(name.split(" / ")[-1]) or SPACE_HOLDER.search(_part_label(b).upper()) or \
                reserved_label(b.label, reserved):
            continue
        use.append(b)
    wf = {i: world_faces(b) for i, b in enumerate(use)}
    drops = {}
    extra = set()
    for i, b in enumerate(use):
        for p, t, src in travel:
            if p.search(b.label):
                bottom = b.box[2]
                drops[i] = (max(z_floor, bottom - t), bottom, src)
                extra |= {max(z_floor, bottom - t), bottom}
                break
    cuts = cut_heights(wf, z_floor, z_top, extra) if heights is None else [(z, z - 0.5, z + 0.5) for z in heights]
    # an upright part (faces upright or level, round faces upright) cuts the same between two of its own heights
    own, memo = {}, {}
    for i, w in wf.items():
        zs, curved = outline_heights(w)
        upright = not curved and all(f.kind in ("plane", "cyl") and (abs(f.ax[2]) < 1e-9 or abs(f.ax[2]) > 1 - 1e-9)
                                     for f in w)
        own[i] = sorted(zs) if upright else None
    states, found = [], []
    for z, z0, z1 in cuts:
        segs = {}
        open_faces = 0
        for i, b in enumerate(use):
            zz = z
            if i in drops and drops[i][0] <= z < drops[i][1]:
                zz = drops[i][1] + 1e-3                 # its own bottom outline, taken down
            if not (b.box[2] < zz < b.box[5]):
                continue
            key = (i, bisect.bisect(own[i], zz)) if own[i] is not None else None
            if key is not None and key in memo:
                s, bad = memo[key]
            else:
                s, bad = body_cut(wf[i], zz)
                if key is not None:
                    memo[key] = (s, bad)
            open_faces += bad
            if len(s):
                segs[i] = s
        items = list(segs.items())
        rows = Raster(items, 0.0, xy)
        others = [Raster(items, math.radians(a), xy, TRY_H) for a in DIRECTIONS[1:]]
        state, gaps, info = ring_gaps(rows, others)
        gaps = [refine(g, segs) for g in gaps]
        gaps = [g for g in gaps if g["width"] > SEAL_GAP]
        if state == "open" and not gaps:
            state = "sealed"
        states.append({"z": z, "z0": z0, "z1": z1, "state": state, "gaps": gaps,
                       "open_rows": rows.open_rows + sum(o.open_rows for o in others),
                       "unpaired_faces": open_faces, "seed": info.get("seed")})
        if log:
            log("Z %.2f %s %s" % (z, state, ", ".join("%.1f" % g["width"] for g in gaps)))
        for g in gaps:
            found.append((z, z0, z1, g))
    return _openings(found, use), states, use


def _openings(found, use, reach=25.0):
    """Join the gaps cut by cut into openings. A gap continues an opening of the cut just below when their middles
    are within 5 mm, or within 25 mm (or the narrower width) and their widths are alike (within 1 mm or a quarter):
    nearest pairs first, one gap to one opening per cut, so two gaps side by side stay two openings. Each opening: its height range, widths, open area (width x height), the parts on its
    sides with the area each pair bounds, and the place of its widest cut."""
    by_z = {}
    for z, z0, z1, g in found:
        by_z.setdefault((z, z0, z1), []).append(g)
    ops, live = [], []
    for (z, z0, z1) in sorted(by_z):
        gaps = by_z[(z, z0, z1)]
        mids = [((g["a"][0] + g["b"][0]) / 2.0, (g["a"][1] + g["b"][1]) / 2.0) for g in gaps]
        pairs = []
        for oi, o in enumerate(live):
            if abs(o["z1"] - z0) > 1e-3:
                continue
            for gi, (g, m) in enumerate(zip(gaps, mids)):
                d = math.hypot(o["m"][0] - m[0], o["m"][1] - m[1])
                wg, wo = g["width"], o["w_last"]
                alike = abs(wg - wo) <= max(1.0, 0.25 * max(wg, wo))
                if d <= 5.0 or (alike and d <= max(reach, min(wg, wo))):
                    pairs.append((d, oi, gi))
        pairs.sort()
        took_o, took_g, nxt = set(), set(), []
        for d, oi, gi in pairs:
            if oi in took_o or gi in took_g:
                continue
            took_o.add(oi)
            took_g.add(gi)
            o, g = live[oi], gaps[gi]
            _grow(o, z0, z1, g, mids[gi], use)
            nxt.append(o)
        for gi, g in enumerate(gaps):
            if gi in took_g:
                continue
            o = {"z0": z0, "z1": z0, "w_min": g["width"], "w_max": g["width"], "w_last": g["width"], "area": 0.0,
                 "m": mids[gi], "pairs": {}, "cuts": 0, "widest": None}
            _grow(o, z0, z1, g, mids[gi], use)
            ops.append(o)
            nxt.append(o)
        live = nxt
    return ops


def _grow(o, z0, z1, g, m, use):
    w = g["width"]
    o["z1"] = z1
    o["w_min"], o["w_max"], o["w_last"] = min(o["w_min"], w), max(o["w_max"], w), w
    o["area"] += w * (z1 - z0)
    o["m"] = m
    o.setdefault("mids", []).append((round(m[0], 2), round(m[1], 2), round((z0 + z1) / 2.0, 3), round(w, 3)))
    o["cuts"] += 1
    key = tuple(sorted(use[p].label for p in set(g["parts"])))
    o["pairs"][key] = o["pairs"].get(key, 0.0) + w * (z1 - z0)
    if o["widest"] is None or w > o["widest"]["width"]:
        o["widest"] = {"width": w, "a": g["a"], "b": g["b"], "z": (z0 + z1) / 2.0}


# ----------------------------------------------------------------- findings

def _pn(label):
    """A body's part number (the 6 digits its part's label starts with), or its part name."""
    part = label.split(" / ")[-2] if " / " in label else label
    m = re.match(r"\s*(\d{6})", part)
    return m.group(1) if m else re.sub(r":\d+$", "", part).strip()


def _part_name(label):
    part = label.split(" / ")[-2] if " / " in label else label
    return re.sub(r":\d+$", "", part).strip()


def check_seal_line(root, mdl, bodies, log=None):
    """C01 seal-gap findings for the floor seal line of an assembly, and the run's seal-line report (None when there
    is nothing at floor level to check)."""
    z_top, z_src = band_top(root)
    travel = load_travel(root)
    reserved = reserved_spaces(root)
    if not any(b.box is not None and b.box[2] < z_top and b.box[5] > 0.0 for b in bodies):
        return [], None
    ops, states, use = seal_line(bodies, z_top, travel, reserved, log=log)
    total = sum(o["area"] for o in ops)
    files = {b.label: b.file for b in use}
    fs, rows = [], []
    named = {}
    for o in ops:
        pair = max(o["pairs"].items(), key=lambda kv: kv[1])[0]
        a, b = pair[0], pair[-1]
        key = " | ".join(sorted({_pn(a), _pn(b)}))
        named.setdefault(key, []).append(o)
    for key, group in named.items():
        for o in group:
            pair = max(o["pairs"].items(), key=lambda kv: kv[1])[0]
            a, b = pair[0], pair[-1]
            w = o["widest"]
            x, y = (w["a"][0] + w["b"][0]) / 2.0, (w["a"][1] + w["b"][1]) / 2.0
            subject = "floor seal line %s" % key
            if len(group) > 1:                  # two openings between the same parts: their place, then height
                at = lambda g: "X %.0f Y %.0f" % ((g["widest"]["a"][0] + g["widest"]["b"][0]) / 2.0,
                                                   (g["widest"]["a"][1] + g["widest"]["b"][1]) / 2.0)
                same = [g for g in group if at(g) == at(o)]
                subject += " at " + at(o) + (" Z %.0f" % o["z0"] if len(same) > 1 else "")
            teams = sorted({owner_for(files.get(l, "")) for l in pair})
            others = sorted({_part_name(l) for p in o["pairs"] for l in p} - {_part_name(a), _part_name(b)})
            width = ("%.1f mm" % o["w_max"]) if o["w_max"] - o["w_min"] < 0.05 else \
                ("%.1f to %.1f mm" % (o["w_min"], o["w_max"]))
            span = "from the floor" if o["z0"] <= 1e-6 else "from Z %.1f" % o["z0"]
            msg = ("The pod's floor seal line is open between %s and %s: a gap %s wide at X %.1f, Y %.1f, %s to "
                   "Z %.1f, open area %.0f mm² (calculation: width times height, summed over %d cuts of the "
                   "STEPs). Air passes between the room and the pod there%s.%s All openings on this run: %d, "
                   "%.0f mm² in all." % (
                       _part_name(a), _part_name(b), width, x, y, span, o["z1"], o["area"], o["cuts"],
                       (" (other parts on its sides at some heights: %s)" % ", ".join(others)) if others else "",
                       " A gap this wide is a part not modelled yet, or missing." if o["w_max"] > 50.0 else "",
                       len(ops), total))
            fix = ("Close it: make the parts meet, or come within 1 mm, all the way up; or add the part that "
                   "bridges it (a seal, a brush, a plate, a lip), in the CAD as it sits when fitted (pressed, "
                   "compressed). The check takes the door's drop seal down to the floor within its travel "
                   "(config/seal-travel.csv).")
            f0 = files.get(a, "") or files.get(b, "")
            fs.append(Finding("C01", "seal-gap", subject, "severe", msg, fix, f0, "; ".join(teams),
                              {"model": "seal-line", "at": [round(x, 1), round(y, 1)],
                               "z": [round(o["z0"], 2), round(o["z1"], 2)],
                               "width_mm": [round(o["w_min"], 2), round(o["w_max"], 2)],
                               "area_mm2": round(o["area"], 1), "parts": sorted({l for p in o["pairs"] for l in p}),
                               "widest_cut": {"z": round(w["z"], 2), "a": [round(v, 2) for v in w["a"]],
                                              "b": [round(v, 2) for v in w["b"]]}}))
            rows.append({"subject": subject, "between": "%s | %s" % (_part_name(a), _part_name(b)),
                         "at": (round(x, 1), round(y, 1)), "z": (round(o["z0"], 2), round(o["z1"], 2)),
                         "width": (round(o["w_min"], 2), round(o["w_max"], 2)), "area": round(o["area"], 1),
                         "owner": "; ".join(teams)})
    report = {"z_top": z_top, "z_top_source": z_src, "cuts": len(states),
              "sealed_cuts": sum(1 for s in states if s["state"] == "sealed"),
              "no_ring_cuts": [round(s["z"], 2) for s in states if s["state"] in ("no ring", "no inside")],
              "unclosed_outline_rows": sum(s["open_rows"] for s in states),
              "unpaired_faces": sum(s["unpaired_faces"] for s in states),
              "travel": [{"pattern": p.pattern, "mm": t, "source": src} for p, t, src in travel],
              "openings": sorted(rows, key=lambda r: -r["area"]), "total_mm2": round(total, 1)}
    for z in report["no_ring_cuts"]:
        fs.append(Finding("C01", "seal-no-ring", "floor seal line at Z %.1f" % z, "severe",
                          "At Z %.1f no ring of parts can be traced round the pod's inside at all, even across every "
                          "gap: the floor seal line can't be checked at that height." % z,
                          "Model the parts that close the pod at that height.", "", "PM",
                          {"model": "seal-line", "z": z}))
    return fs, report


# ----------------------------------------------------------------- shapes in pod coordinates (tests, saved cuts)

class Shape:
    """A body given by its faces in pod coordinates: label, box, file, part number and world faces."""
    __slots__ = ("label", "box", "file", "part_number", "wfaces", "solid", "frame")

    def __init__(self, label, wfaces, file="", part_number=""):
        self.label, self.wfaces, self.file, self.part_number = label, wfaces, file, part_number
        self.solid = self.frame = None
        pts = [p for w in wfaces for e in w.edges if e[0] == "seg" for p in (e[1], e[2])]
        zs = [z for w in wfaces for z in (w.zlo, w.zhi)]
        self.box = (min(p[0] for p in pts), min(p[1] for p in pts), min(zs),
                    max(p[0] for p in pts), max(p[1] for p in pts), max(zs))


def _plane_face(poly, n):
    w = _WFace()
    w.kind, w.o, w.ax, w.r, w.half = "plane", poly[0], _unit(n), None, None
    w.edges = [("seg", poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
    w.zlo, w.zhi = min(p[2] for p in poly), max(p[2] for p in poly)
    return w


def prism(label, outline, z0, z1, file="", part_number=""):
    """An upright prism: a plan outline (x, y) points, anticlockwise, from z0 to z1."""
    n = len(outline)
    lo = [(x, y, z0) for x, y in outline]
    hi = [(x, y, z1) for x, y in outline]
    faces = [_plane_face(list(reversed(lo)), (0, 0, -1)), _plane_face(hi, (0, 0, 1))]
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        faces.append(_plane_face([lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]], (b[1] - a[1], a[0] - b[0], 0)))
    return Shape(label, faces, file, part_number)


def box(label, x0, y0, z0, x1, y1, z1, file="", part_number=""):
    return prism(label, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, file, part_number)


def load_shapes(path):
    """Shapes saved by save_shapes (a gzip JSON of the floor band's faces)."""
    import gzip
    import json
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        data = json.load(fh)
    out = []
    for b in data["bodies"]:
        faces = []
        for f in b["faces"]:
            w = _WFace()
            w.kind, w.r, w.half = f["k"], f["r"], f["h"]
            w.o = tuple(f["o"]) if f["o"] else None
            w.ax = tuple(f["ax"]) if f["ax"] else None
            w.zlo, w.zhi = f["z"]
            w.edges = [("seg", tuple(e[1]), tuple(e[2])) if e[0] == "s" else
                       ("arc", tuple(e[1]), tuple(e[2]), tuple(e[3]), e[4], e[5], e[6]) for e in f["e"]]
            faces.append(w)
        sh = Shape(b["label"], faces, b.get("file", ""), b.get("pn", ""))
        sh.box = tuple(b["box"])
        out.append(sh)
    return out, data.get("source", "")


def save_shapes(path, bodies, z_top, source=""):
    """Save the faces of the bodies that reach below z_top, in pod coordinates, as a gzip JSON (test fixtures)."""
    import gzip
    import json

    def r(v):
        return round(v, 4)
    out = []
    for b in bodies:
        if b.box is None or b.box[2] >= z_top or b.box[5] <= 0.0:
            continue
        fl = []
        for w in world_faces(b):
            es = []
            for e in w.edges:
                if e[0] == "seg":
                    es.append(["s", [r(x) for x in e[1]], [r(x) for x in e[2]]])
                else:
                    es.append(["a", [r(x) for x in e[1]], [r(x) for x in e[2]], [r(x) for x in e[3]], r(e[4]),
                               r(e[5]), r(e[6])])
            fl.append({"k": w.kind, "o": [r(x) for x in w.o] if w.o else None,
                       "ax": [r(x) for x in w.ax] if w.ax else None, "r": r(w.r) if w.r else None, "h": w.half,
                       "z": [r(w.zlo), r(w.zhi)], "e": es})
        out.append({"label": b.label, "file": b.file, "pn": b.part_number, "box": [r(x) for x in b.box],
                    "faces": fl})
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump({"source": source, "bodies": out}, fh, separators=(",", ":"))
    return len(out)
