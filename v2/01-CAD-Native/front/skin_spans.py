"""D-131 skin span check for the decor blocks DL, DT and DR: every free span of their 3 mm ACP skins, against the
PM's limit (2026-11-01): 2 mm or less under a 100 N push at a bay's centre, edges taken as simply supported.

    python3 v2/01-CAD-Native/front/skin_spans.py [--grid 2] [--no-selftest]

Reads each block's STEP as built (v2/03-Manufacturing/front), so the bays are the real ones: the skin's inner faces,
the frame tubes' faces bonded to them (coplanar, facing), the folds between faces and the skin's cut edges (pockets,
slots, open joints). Writes SKIN-SPANS.md here. numpy only (the repo's checks python).

A bay is a connected part of a skin face that no tube touches. Its edges are:
- a tube's bonded strip: simply supported (the PM's rule), and in a second reading held flat by the bond (clamped);
- a fold to the next face: an edge when the faces turn FOLD_MIN or more (a folded skin holds its fold line: the
  folded-plate check below shows it on DL's 15 deg fold); shallower folds are laid flat, so both faces form one bay;
- a cut edge: free.
Bays with no free edge are solved by skin_plates.ss_fd (exact for straight-edged convex bays, about 1 % high on a
2 mm grid); bays with a free edge by skin_plates.bfs (plate elements), with each tube strip simply supported where it
runs along the grid and, in the second reading, clamped. A bay held on one edge only hinges under simple supports,
so for those the bonded reading is the one that means something; both are listed.
The load goes at the bay's centroid and at its deepest point (farthest from its edges); the larger counts.
The tubes are taken as rigid, as WALL's check takes them (make_acp_spans.py).
"""
import argparse
import collections
import glob
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "checks"))
sys.path.insert(0, HERE)
import stepfile  # noqa: E402
import skin_plates as SP  # noqa: E402
import frame_members_pn as FPN  # noqa: E402

LIMIT = 2.0                  # mm under 100 N at a bay's centre (PM ruling 2026-11-01, D-131)
BOND_OK = "the PM's reading for strips held on fewer sides (2026-11-01), confirmed by the sample's push test"
P = 100.0
FOLD_MIN = 10.0              # deg between two faces' normals for their fold to count as a bay edge
SLIVER = 10.0                # mm: a strip narrower than this along a support is no span
MIN_AREA = 1000.0            # mm2: a corner pocket smaller than this (10 cm2) is no span
MFG = os.path.join(REPO, "v2", "03-Manufacturing", "front")
BLOCKS = [
    ("DL", "350001", "351101", [FPN.DL_FRAME] + sorted(set(FPN.DL_MEMBERS.values()))),
    ("DT", "350002", "351201", [FPN.DT_FRAME] + sorted(set(FPN.DT_MEMBERS.values()))),
    ("DR", "350003", "351301", [FPN.DR_FRAME] + sorted(set(FPN.DR_MEMBERS.values()))),
]


# ---------------------------------------------------------------- geometry from the STEP

def _unit(a):
    a = np.asarray(a, float)
    return a / np.linalg.norm(a)


def frame2d(n):
    """in-plane axes (e_u, e_v) of a face: e_v up the face (or along +Y on a level face)."""
    z = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(n, z)) < 0.95:
        e_v = _unit(z - np.dot(z, n) * n)
    else:
        y = np.array([0.0, 1.0, 0.0])
        e_v = _unit(y - np.dot(y, n) * n)
    return _unit(np.cross(e_v, n)), e_v


class Face:
    def __init__(self, o, n, segs):
        self.o, self.n, self.segs = np.asarray(o, float), _unit(n), segs
        self.pts = np.array([p for s in segs for p in s])


def _arc(c, r, v1, v2, n=24):
    o, z = np.asarray(c.o), _unit(c.z)
    x = _unit(np.asarray(v1) - o)
    y = np.cross(z, x)
    p2 = np.asarray(v2) - o
    a2 = math.atan2(np.dot(p2, y), np.dot(p2, x))
    a2 = 2 * math.pi if np.linalg.norm(np.asarray(v1) - np.asarray(v2)) < 1e-6 else (a2 + 2 * math.pi if a2 < 0 else a2)
    return [tuple(o + r * (math.cos(t) * x + math.sin(t) * y)) for t in np.linspace(0, a2, n)]


def planar_faces(sf, inst):
    s, fr = sf.solid(inst["solid"]), inst["frame"]
    out = []
    for f in s.faces:
        if f.kind != "plane":
            continue
        segs = [(fr.point(a), fr.point(b)) for a, b in f.lines]
        for c, r, v1, v2, _sense in f.arcs:
            cw = stepfile.Frame(fr.point(c.o), fr.vector(c.x), fr.vector(c.y), fr.vector(c.z))
            pts = _arc(cw, r, fr.point(v1), fr.point(v2))
            segs += list(zip(pts[:-1], pts[1:]))
        out.append(Face(fr.point(f.origin), fr.vector(f.normal), segs))
    return out


def seg_key(a, b):
    ka, kb = tuple(np.round(a, 1)), tuple(np.round(b, 1))
    return (ka, kb) if ka <= kb else (kb, ka)


def rot_about(p, a, axis, ang):
    p = np.asarray(p, float) - a
    return a + p * math.cos(ang) + np.cross(axis, p) * math.sin(ang) + axis * np.dot(axis, p) * (1 - math.cos(ang))


# ---------------------------------------------------------------- raster tools

def fill(segs2, u0, v0, nu, nv, h):
    """even-odd fill of 2D segments on the cell centres of an nv x nu grid of h mm cells from (u0, v0)."""
    vc, uc = v0 + (np.arange(nv) + 0.5) * h, u0 + (np.arange(nu) + 0.5) * h
    inside = np.zeros((nv, nu), bool)
    for (pu, pv), (qu, qv) in segs2:
        if abs(qv - pv) < 1e-12:
            continue
        rows = np.where((vc >= min(pv, qv)) & (vc < max(pv, qv)))[0]
        for r, x in zip(rows, pu + (vc[rows] - pv) / (qv - pv) * (qu - pu)):
            inside[r, uc > x] ^= True
    return inside


def thick_line(p, q, u0, v0, nu, nv, h, w=2.0):
    m = np.zeros((nv, nu), bool)
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    for t in np.linspace(0, 1, max(2, int(L / (h / 2)) + 1)):
        u, v = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
        i0, i1 = int((u - w - u0) / h), int((u + w - u0) / h) + 1
        j0, j1 = int((v - w - v0) / h), int((v + w - v0) / h) + 1
        m[max(0, j0):max(0, j1), max(0, i0):max(0, i1)] = True
    return m


def _shift(m, du, dv):
    out = np.zeros_like(m)
    nv, nu = m.shape
    out[max(0, dv):nv + min(0, dv), max(0, du):nu + min(0, du)] = m[max(0, -dv):nv + min(0, -dv), max(0, -du):nu + min(0, -du)]
    return out


def dilate(m, k):
    o = m.copy()
    for d in range(1, k + 1):
        o = o | _shift(m, d, 0) | _shift(m, -d, 0)
    p = o.copy()
    for d in range(1, k + 1):
        p = p | _shift(o, 0, d) | _shift(o, 0, -d)
    return p


def erode(m, k):
    return ~dilate(~m, k)


def label(mask):
    lab, n = np.zeros(mask.shape, int), 0
    nv, nu = mask.shape
    for j0, i0 in zip(*np.nonzero(mask)):
        if lab[j0, i0]:
            continue
        n += 1
        stack = [(j0, i0)]
        lab[j0, i0] = n
        while stack:
            j, i = stack.pop()
            for a, b in ((j + 1, i), (j - 1, i), (j, i + 1), (j, i - 1)):
                if 0 <= a < nv and 0 <= b < nu and mask[a, b] and not lab[a, b]:
                    lab[a, b] = n
                    stack.append((a, b))
    return lab, n


def _aligned(p, q, tol=0.5):
    a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 90.0
    return min(a, 90.0 - a) < tol


# ---------------------------------------------------------------- the bays of one block

def block_bays(path, skin_pn, frame_pns, h=2.0, extra=None):
    """bays of a block's skin as dicts; extra: {face normal (rounded 3): [world boxes ((x0,x1),(y0,y1),(z0,z1))]}
    added as supports (proposed tubes)."""
    sf = stepfile.StepFile(path)
    skin, frame = [], []
    for i in sf.instances():
        if i["part_number"] == skin_pn:
            skin.append(i)
        elif i["part_number"] in frame_pns:
            frame.append(i)
    sk = [f for i in skin for f in planar_faces(sf, i)]
    fr = [f for i in frame for f in planar_faces(sf, i)]
    cen = np.mean([f.pts.mean(0) for f in fr], axis=0)
    inner = []
    for f in sk:
        e_u, e_v = frame2d(f.n)
        uv = np.array([[np.dot(p - f.o, e_u), np.dot(p - f.o, e_v)] for p in f.pts])
        w, hh = uv.max(0) - uv.min(0)
        if w * hh < 3000.0 or min(w, hh) < 8.0:
            continue
        cont = [m for m in fr if np.dot(m.n, f.n) < -0.9999 and abs(np.dot(m.o - f.o, f.n)) < 0.05]
        if cont or np.dot(cen - f.o, f.n) > 0:
            inner.append((f, cont))
    ids = {id(f): k for k, (f, _c) in enumerate(inner)}
    segf = collections.defaultdict(list)
    for f in sk:
        for a, b in f.segs:
            segf[seg_key(a, b)].append(f)
    folds = {}
    for i, (f, _c) in enumerate(inner):
        for a, b in f.segs:
            for g in segf[seg_key(a, b)]:
                j = ids.get(id(g))
                if j is not None and j != i:
                    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(f.n, g.n))))))
                    folds[(i, j)] = (ang, np.asarray(a, float), np.asarray(b, float))
    parent = list(range(len(inner)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for (i, j), (ang, _a, _b) in folds.items():
        if ang < FOLD_MIN:
            parent[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i in range(len(inner)):
        groups[find(i)].append(i)
    bays = []
    for members in groups.values():
        base = members[0]
        f0 = inner[base][0]
        xf = {base: (lambda p: np.asarray(p, float))}
        todo = [base]
        while todo:
            i = todo.pop()
            for j in members:
                if j in xf or (i, j) not in folds:
                    continue
                ang, a, b = folds[(i, j)]
                axis = _unit(b - a)
                fi, fj = inner[i][0], inner[j][0]
                th = math.atan2(float(np.dot(np.cross(fj.n, fi.n), axis)), float(np.dot(fj.n, fi.n)))
                xf[j] = (lambda prev, a, axis, th: (lambda p: prev(rot_about(p, a, axis, th))))(xf[i], a, axis, th)
                todo.append(j)
        e_u, e_v = frame2d(f0.n)

        def P2(p, t):
            q = t(p)
            return (float(np.dot(q - f0.o, e_u)), float(np.dot(q - f0.o, e_v)))
        segs, conts, free_l, fold_l = [], [], [], []
        for i in members:
            f, cont = inner[i]
            t = xf[i]
            for a, b in f.segs:
                pa, pb = P2(a, t), P2(b, t)
                nb = [ids.get(id(o)) for o in segf[seg_key(a, b)] if o is not f]
                nb = [j for j in nb if j is not None]
                if nb:
                    ang = folds.get((i, nb[0]), (0.0,))[0]
                    if not (nb[0] in members and ang < FOLD_MIN):
                        fold_l.append((pa, pb, ang))
                else:
                    free_l.append((pa, pb))
                segs.append((i, pa, pb))
            conts += [[(P2(a, t), P2(b, t)) for a, b in m.segs] for m in cont]
        us = [p[0] for _i, a, b in segs for p in (a, b)]
        vs = [p[1] for _i, a, b in segs for p in (a, b)]
        u0, v0 = min(us) - 4, min(vs) - 4
        nu, nv = int((max(us) - u0) / h) + 6, int((max(vs) - v0) / h) + 6
        face = np.zeros((nv, nu), bool)
        for i in members:
            face |= fill([(a, b) for k, a, b in segs if k == i], u0, v0, nu, nv, h)
        con, slant = np.zeros_like(face), np.zeros_like(face)
        for poly in conts:
            mp = fill(poly, u0, v0, nu, nv, h)
            con |= mp
            longest = max(poly, key=lambda s: math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
            if not _aligned(*longest):
                slant |= mp
        key = tuple(np.round(f0.n, 3))
        if extra and key in extra:
            U = u0 + (np.arange(nu) + 0.5) * h
            V = v0 + (np.arange(nv) + 0.5) * h
            UU, VV = np.meshgrid(U, V)
            W = f0.o[None, None, :] + UU[..., None] * e_u + VV[..., None] * e_v
            for (x0, x1), (y0, y1), (z0, z1) in extra[key]:
                con |= ((W[..., 0] >= x0) & (W[..., 0] <= x1) & (W[..., 1] >= y0) & (W[..., 1] <= y1) &
                        (W[..., 2] >= z0) & (W[..., 2] <= z1))
        sup = con.copy()
        for pa, pb, _ang in fold_l:
            tl = thick_line(pa, pb, u0, v0, nu, nv, h)
            sup |= tl
            if not _aligned(pa, pb):
                slant |= tl
        k = max(1, int(round(3.0 / h)))
        sup = erode(dilate(sup, k), k) & face
        con = erode(dilate(con, k), k) & face
        slant = dilate(slant, k) & sup
        free_m = np.zeros_like(face)
        for pa, pb in free_l:
            free_m |= thick_line(pa, pb, u0, v0, nu, nv, h)
        lab, n = label(face & ~sup)
        for b in range(1, n + 1):
            m = lab == b
            depth, e = 0, m.copy()
            last = e
            while e.any():
                depth += 1
                last = e
                e = erode(e, 1)
            if depth * h < SLIVER / 2 or m.sum() * h * h < MIN_AREA:
                continue
            jj, ii = np.nonzero(m)
            cj, ci = int(round(jj.mean())), int(round(ii.mean()))
            if not m[cj, ci]:
                q = int(np.argmin((jj - cj) ** 2 + (ii - ci) ** 2))
                cj, ci = int(jj[q]), int(ii[q])
            lj, li = np.nonzero(last)
            dj, di = int(lj[len(lj) // 2]), int(li[len(li) // 2])
            UV = lambda j, i: (u0 + (i + 0.5) * h, v0 + (j + 0.5) * h)
            world = lambda j, i: f0.o + UV(j, i)[0] * e_u + UV(j, i)[1] * e_v
            free_edge = bool((dilate(m, 2) & free_m & ~sup).any())
            pts = np.array([world(j, i) for j, i in zip(jj[::50], ii[::50])])
            bays.append({"faces": len(members), "normal": key, "mask": m, "sup": sup, "con": con, "slant": slant,
                         "free_edge": free_edge, "slanted": bool((dilate(m, 2) & slant).any()), "h": h,
                         "centre": (cj, ci), "deep": (dj, di), "area": m.sum() * h * h,
                         "size": ((ii.max() - ii.min() + 1) * h, (jj.max() - jj.min() + 1) * h),
                         "fill": len(jj) / ((ii.max() - ii.min() + 1) * (jj.max() - jj.min() + 1)),
                         "xyz_min": pts.min(0), "xyz_max": pts.max(0), "centre_xyz": world(cj, ci),
                         "folds": sorted({round(a) for _p, _q, a in fold_l})})
    return bays


# ---------------------------------------------------------------- solving a bay

def _crop(a, j0, j1, i0, i1):
    out = np.zeros((j1 - j0, i1 - i0), bool)
    blk = a[max(0, j0):j1, max(0, i0):i1]
    out[max(0, -j0):max(0, -j0) + blk.shape[0], max(0, -i0):max(0, -i0) + blk.shape[1]] = blk
    return out


def solve_bay(b, coarse=2):
    """deflections at the bay's centre and deepest point: 'ss' (simple supports; None where it can't be read
    on the grid: slanted strips round a free-edged bay) and 'bond' (strips clamped); method name."""
    m, h = b["mask"], b["h"]
    jj, ii = np.nonzero(m)
    if not b["free_edge"]:
        sub = m[jj.min() - 1:jj.max() + 2, ii.min() - 1:ii.max() + 2]
        o = (jj.min() - 1, ii.min() - 1)
        ws = [SP.ss_fd(sub, h, (p[0] - o[0], p[1] - o[1])) for p in {b["centre"], b["deep"]}]
        return {"ss": max(ws), "bond": None, "method": "ss_fd"}
    j0, i0 = jj.min() - 2, ii.min() - 2
    j0 -= j0 % coarse
    i0 -= i0 % coarse
    j1, i1 = jj.max() + 3 + coarse, ii.max() + 3 + coarse
    M, SUP, CON = (_crop(a, j0, j1, i0, i1) for a in (m, b["sup"], b["con"]))
    nv, nu = M.shape[0] // coarse, M.shape[1] // coarse
    down = lambda a: a[:nv * coarse, :nu * coarse].reshape(nv, coarse, nu, coarse)
    cells = down(M).mean(axis=(1, 3)) >= 0.5
    supc = down(SUP).any(axis=(1, 3)) & ~cells
    conc = down(CON).any(axis=(1, 3)) & ~cells
    act = np.zeros((nv + 1, nu + 1), bool)
    for dj in (0, 1):
        for di in (0, 1):
            act[dj:dj + nv, di:di + nu] |= cells

    def touching(c):
        pad = np.zeros((nv + 2, nu + 2), bool)
        pad[1:-1, 1:-1] = c
        return act & (pad[:-1, :-1] | pad[1:, :-1] | pad[:-1, 1:] | pad[1:, 1:])
    held, clamp = touching(supc), touching(conc)
    loads = {((p[0] - j0) // coarse, (p[1] - i0) // coarse) for p in (b["centre"], b["deep"])}
    out = {"method": "bfs"}
    for name, cl in (("ss", None), ("bond", clamp)):
        if name == "ss" and b["slanted"]:
            out[name] = None              # a simple support along a staircase would act as a clamp
            continue
        try:
            out[name] = max(SP.bfs(cells, held, ld, h * coarse, P=P, clamped=cl) for ld in loads)
        except np.linalg.LinAlgError:
            out[name] = float("inf")      # held on one edge only: it hinges
    return out


# ---------------------------------------------------------------- DL's shallow fold, as a folded plate

def dl_fold_check():
    """DL's outer and front facets meet at a 15 deg fold with no tube behind it: folded-plate strips between the
    rings, against the same two faces laid flat (one 303 mm bay) and the front facet alone."""
    L0, K, Dp = (-1247.0, -667.84), (-1156.29, -749.51), (-995.0, -832.4)      # left fold, the 15 deg fold, P posts
    pts, idx = SP.polyline([L0, K, Dp], per_mm=5.0)
    b1, b2 = (math.hypot(K[0] - L0[0], K[1] - L0[1]), math.hypot(Dp[0] - K[0], Dp[1] - K[1]))
    cum = np.concatenate([[0.0], np.cumsum([math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:])])])
    node = lambda s: int(np.argmin(np.abs(cum - s)))
    L = 734.5                                  # the tallest ring bay (fr_z3 - fr_z2 - fr_w)
    w = {nm: abs(SP.fsm(pts, [0, len(pts) - 1], node(s), L)) for nm, s in
         (("outer facet centre", b1 / 2), ("both faces' centre", (b1 + b2) / 2), ("front facet centre", b1 + b2 / 2))}
    return {"b1": b1, "b2": b2, "L": L, "fsm": w, "flat": SP.navier_rect(b1 + b2, L), "front_alone": SP.navier_rect(b2, L)}


# ---------------------------------------------------------------- report

FACES = {   # readable names by inner-face normal (rounded 3)
    "DL": {(0.665, 0.747, 0.0): "outer facet", (0.457, 0.889, 0.0): "front facet", (-1.0, -0.0, -0.0): "door-side face",
           (1.0, 0.0, 0.0): "wall-side face"},
    "DT": {(0.0, 0.747, -0.665): "chamfer", (0.075, 0.997, 0.0): "front facets", (0.069, 0.998, 0.0): "front facets",
           (0.0, 0.0, 1.0): "underside", (-0.0, -0.0, -1.0): "top"},
    "DR": {(0.0, 1.0, 0.0): "front face", (-0.669, 0.744, 0.0): "corner facet", (0.0, 0.747, -0.665): "chamfer",
           (0.99, 0.0, 0.139): "glass-edge strip (right edge)", (0.756, 0.0, 0.655): "glass-edge strip (diagonal)",
           (-1.0, -0.0, -0.0): "wall-side face"},
}

# proposed supports for DR's front face top bay (world boxes; the tube's 20 mm face on the skin)
DR_FRONT = (0.0, 1.0, 0.0)
INF = (-1e9, 1e9)
FAN_BOX = ((645.0, 945.0), INF, (1650.0, 1950.0))      # AIR's supply fan box 611402 front, on the skin (AIR CAD, main)
DR_OPTIONS = [
    ("as built", []),
    ("**one tube across at Z 1904-1924, the fan box 25 back from the skin (PM ruling 2026-11-01: F09)**",
     [(INF, INF, (1904.4, 1924.4))]),
    ("the fan box's front as a backing (no tube)", [FAN_BOX]),
    ("one tube at Z 2000-2020 and the fan box's front as a backing", [(INF, INF, (2000.0, 2020.0)), FAN_BOX]),
    ("three tubes round the fan box (Z 1950-1970, X 625-645, X 950-970)",
     [(INF, INF, (1950.0, 1970.0)), ((625.0, 645.0), INF, (1650.0, 1950.0)), ((950.0, 970.0), INF, (1650.0, 1950.0))]),
]


def dr_options(h):
    path = glob.glob(os.path.join(MFG, "350003_*_STEP.step"))[0]
    out = []
    for name, boxes in DR_OPTIONS:
        worst = None
        for b in block_bays(path, "351301", set(BLOCKS[2][3]), h, extra={DR_FRONT: boxes} if boxes else None):
            if b["normal"] != DR_FRONT or b["free_edge"]:
                continue
            w = solve_bay(b)["ss"]
            if worst is None or w > worst[0]:
                worst = (w, b)
        out.append((name, worst[0], worst[1]))
    return out


def _where(b):
    lo, hi = b["xyz_min"], b["xyz_max"]
    return "X %.0f to %.0f, Z %.0f to %.0f" % (lo[0], hi[0], lo[2], hi[2])


def _fmt(w):
    return "-" if w is None else ("hinges" if not math.isfinite(w) or w > 50 else "%.2f" % w)


def write_md(rows, fold, st, opts, h):
    md = ["# FRONT decor blocks: the ACP skin's free spans (D-131)", "",
          "Generated by `skin_spans.py` (plate solvers in `skin_plates.py`) from the blocks' STEPs as built "
          "(v2/03-Manufacturing/front). D-130 changed only the wall of DR's frame tubes, not where they sit (checked "
          "against the code), so DR's bays stand. The limit (PM ruling 2026-11-01, D-131): **2 mm or less under a "
          "100 N push at a bay's centre, edges simply supported**. The skin: 3 mm ACP with 0.21 mm aluminium skins, "
          "D = %.0f N·mm, as WALL's check. The tubes are taken as rigid, as WALL's check takes them. Grid %.0f mm." % (SP.D_ACP, h), "",
          "A bay is a part of a skin face that no tube touches. Its edges: a tube's bonded strip (simply supported; "
          "the second figure takes the bond as holding the edge flat, clamped), a fold to the next face (an edge when "
          "the faces turn %.0f° or more; see the fold check), or a cut edge (free: pockets, slots, open joints). The "
          "load goes at the bay's centroid and at its deepest point, the larger counting." % FOLD_MIN, ""]
    def verdict(b):
        ss, bond = b["ss"], b["bond"]
        if ss is not None and ss <= LIMIT:
            return "pass"
        if bond is not None and bond <= LIMIT:
            return "pass with the bond held flat (%s)" % ("it hinges if simply supported" if ss is not None and ss > 50 else
                                                        "%.2f if simply supported" % ss if ss is not None else
                                                        "strips at an angle to the grid")
        return "**FAIL**"
    md += ["## Result", ""]
    for tag in ("DL", "DT", "DR"):
        allround = [b["ss"] for b in rows[tag] if not b["free_edge"]]
        freeb = [b for b in rows[tag] if b["free_edge"]]
        fails = [b for b in rows[tag] if verdict(b) == "**FAIL**"]
        bonded = [b for b in rows[tag] if verdict(b).startswith("pass with the bond")]
        line = "- **%s**: bays held all round %.2f mm at most%s" % (
            tag, max(allround) if allround else 0.0, " as built" if any(b["ss"] > LIMIT for b in rows[tag]
                                                                        if not b["free_edge"]) else "")
        ssfree = [b["ss"] for b in freeb if b["ss"] is not None and b["ss"] <= LIMIT]
        if ssfree:
            line += "; bays with a free edge %.2f at most" % max(ssfree)
        if bonded:
            line += ("; %d bay(s) with a free edge that the simple-support figure can't settle (held on one edge, or "
                     "by strips at an angle to the grid) pass with the bond held flat, %.2f at most (%s)") % (
                len(bonded), max(b["bond"] for b in bonded), BOND_OK)
        if fails:
            line += "; **%d bay(s) over 2 mm as built**: %s" % (len(fails), "; ".join(
                "%s, %s, %.2f mm" % (FACES[tag].get(b["normal"], ""), _where(b), b["ss"]) for b in fails))
        md.append(line + ".")
    chosen = [o for o in opts if o[0].startswith("**")]
    if chosen:
        md.append("- DR's front face top bay with the cross tube F09 the PM chose (the fan box 25 back from the skin): "
                  "%.2f mm (below). The bays table reads DR's STEP as built, before F09; rerun this script on the "
                  "rebuilt STEP to list F09's bays." % chosen[0][1])
    md += ["", "## Every bay", "",
           "| Block | Face | Where | Size (mm) | Edges | Method | Simply supported (mm) | Bond held flat (mm) | Result |",
           "|---|---|---|---|---|---|---|---|---|"]
    for tag in ("DL", "DT", "DR"):
        for b in sorted(rows[tag], key=lambda b: (FACES[tag].get(b["normal"], str(b["normal"])), b["xyz_min"][2])):
            edges = []
            if b["free_edge"]:
                edges.append("a free edge")
            if b["folds"]:
                edges.append("folds " + ", ".join("%d°" % a for a in b["folds"]))
            md.append("| %s | %s | %s | %.0f × %.0f | %s | %s | %s | %s | %s |" % (
                tag, FACES[tag].get(b["normal"], str(b["normal"])), _where(b), b["size"][0], b["size"][1],
                "; ".join(edges) or "tubes", b["method"], _fmt(b["ss"]), _fmt(b["bond"]), verdict(b)))
    md += ["", "## DL's 15° fold, as a folded plate", "",
           "DL's outer facet (%.0f wide) and front facet (%.0f free) meet at a 15° fold with no tube behind it. Strips "
           "between two rings (%.1f apart, the tallest bay), held at the wall-side fold and at the door-side front post, "
           "bending and membrane action in each face (`skin_plates.fsm`):" % (fold["b1"], fold["b2"], fold["L"]), ""]
    md += ["- %s: %.2f mm" % (k, v) for k, v in fold["fsm"].items()]
    md += ["- the two faces laid flat as one bay: %.2f mm; the front facet alone, simply supported: %.2f mm" % (
        fold["flat"], fold["front_alone"]), "",
           "The fold holds its line better than a simple support, so a fold counts as a bay edge from %.0f°." % FOLD_MIN, ""]
    md += ["## DR's front face: the top bay and ways to close it", "",
           "The front face's top bay, above the fan box shelf and under the chamfer, is the one over the limit. AIR's "
           "supply fan box (611402, AIR's CAD on main) stands with its front on the skin's inside, X 645 to 945, "
           "Z 1650 to 1950; nothing else in AIR stands within 20 mm of the skin there. PM ruling 2026-11-01: the option "
           "in bold, the cross tube F09 in DR's frame at the bay's mid-height and the fan box 25 back from the skin "
           "(which also keeps the fans' vibration off it); CEILING and the Air Engineer settle the box's X start.", "",
           "| Option | Largest flex on the front face (mm) | Where |", "|---|---|---|"]
    md += ["| %s | %.2f | %s |" % (n, w, _where(b)) for n, w, b in opts]
    if st:
        md += ["", "## The solvers against known answers", "", "| Case | Method | Result (mm) | Reference (mm) | Difference |",
               "|---|---|---|---|---|"]
        md += ["| %s | %s | %.4f | %.4f | %+.2f %% |" % (c, m, v, r, 100 * (v / r - 1)) for c, m, v, r in st]
        md += ["", "References: the Navier double series (simply supported rectangles); beam theory for the free-edged "
               "strip (the plate sits between beam and cylindrical bending, 70.1 mm)."]
    with open(os.path.join(HERE, "SKIN-SPANS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def run(h, selftest=True):
    rows, t0 = {}, time.time()
    for tag, assy, skin_pn, frame_pns in BLOCKS:
        path = glob.glob(os.path.join(MFG, assy + "_*_STEP.step"))[0]
        rows[tag] = []
        for b in block_bays(path, skin_pn, set(frame_pns), h):
            b.update(solve_bay(b))
            rows[tag].append(b)
            print("%s %-28s %4.0f x %4.0f  ss %s bond %s" % (tag, FACES[tag].get(b["normal"], b["normal"]), b["size"][0],
                                                           b["size"][1], _fmt(b["ss"]), _fmt(b["bond"])), flush=True)
    fold = dl_fold_check()
    opts = dr_options(h)
    st = SP.selftest() if selftest else []
    write_md(rows, fold, st, opts, h)
    return rows, fold, st, opts, time.time() - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", type=float, default=2.0)
    ap.add_argument("--no-selftest", action="store_true")
    a = ap.parse_args()
    _rows, fold, _st, opts, dt = run(a.grid, not a.no_selftest)
    print("fold check", {k: round(v, 3) for k, v in fold["fsm"].items()}, "flat %.2f" % fold["flat"])
    for n, w, _b in opts:
        print("DR option: %-70s %.2f mm" % (n, w))
    print("wrote SKIN-SPANS.md (%.0f s)" % dt)
