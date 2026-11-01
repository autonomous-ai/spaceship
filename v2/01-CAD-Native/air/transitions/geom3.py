"""Small 3D helpers for laying out sheet metal walls: planes, line intersections and corner reliefs (mm)."""

import numpy as np


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def plane(p0, p1, p2, outward_hint):
    """(point, unit normal) of the plane through three points, the normal turned toward outward_hint."""
    p0, p1, p2 = (np.asarray(p, float) for p in (p0, p1, p2))
    n = unit(np.cross(p1 - p0, p2 - p0))
    if np.dot(n, outward_hint) < 0:
        n = -n
    return p0, n


def offset(pl, d):
    """The plane moved d along its normal."""
    p, n = pl
    return p + n * d, n


def plane_line(pa, pb):
    """The line where two planes meet: (point, unit direction)."""
    (p1, n1), (p2, n2) = pa, pb
    d = np.cross(n1, n2)
    if np.linalg.norm(d) < 1e-12:
        raise ValueError("parallel planes")
    d = unit(d)
    # a point on both: solve n1.x = n1.p1, n2.x = n2.p2, d.x = 0
    A = np.array([n1, n2, d])
    b = np.array([np.dot(n1, p1), np.dot(n2, p2), 0.0])
    return np.linalg.solve(A, b), d


def line_plane(lp, pl):
    """Where a line meets a plane."""
    (q, d), (p, n) = lp, pl
    den = np.dot(d, n)
    if abs(den) < 1e-12:
        raise ValueError("line parallel to plane")
    s = np.dot(p - q, n) / den
    return q + s * d


def lines_meet(p1, d1, p2, d2):
    """Where two coplanar lines meet (least squares, checked)."""
    A = np.array([d1, -d2]).T
    s, *_ = np.linalg.lstsq(A, p2 - p1, rcond=None)
    x1, x2 = p1 + s[0] * d1, p2 + s[1] * d2
    if np.linalg.norm(x1 - x2) > 1e-6:
        raise ValueError("lines don't meet (%.6f)" % np.linalg.norm(x1 - x2))
    return x1


def relief(K, A, B, a1, a2):
    """A corner relief at polygon corner K between neighbours A (before) and B (after): [P1, Q, P2] to put in
    K's place. P1 is a1 from K toward A, P2 a2 from K toward B; Q is where the line from P1 square to KA meets
    the line from P2 square to KB, both inside the corner, so the outline leaves each edge at a right angle."""
    K, A, B = (np.asarray(x, float) for x in (K, A, B))
    d1, d2 = unit(A - K), unit(B - K)
    P1, P2 = K + a1 * d1, K + a2 * d2
    n1 = unit(d2 - np.dot(d2, d1) * d1)
    n2 = unit(d1 - np.dot(d1, d2) * d2)
    Q = lines_meet(P1, n1, P2, n2)
    return [P1, Q, P2]


def holes_along(p0, p1, inward, inset, end, pitch, dia):
    """Holes on a line inset from p0-p1 (toward inward): the first and last `end` from each end, evenly spaced at
    most `pitch` apart. [(centre, dia)]"""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    d = (p1 - p0) / L
    span = L - 2 * end
    if span < 3 * dia:                   # too short for two holes 3 diameters apart: one in the middle
        return [(p0 + d * (L / 2) + inward * inset, dia)]
    n = max(1, int(np.ceil(span / pitch)))
    return [(p0 + d * (end + span * i / n) + inward * inset, dia) for i in range(n + 1)]


def kite(K, A, B, a1, a2):
    """The relief [P1, Q, P2] for given distances along KA (a1) and KB (a2), and |P1Q|, |P2Q|."""
    K, A, B = (np.asarray(x, float) for x in (K, A, B))
    d1, d2 = unit(A - K), unit(B - K)
    P1, P2 = K + a1 * d1, K + a2 * d2
    n1 = unit(d2 - np.dot(d2, d1) * d1)
    n2 = unit(d1 - np.dot(d1, d2) * d2)
    Q = lines_meet(P1, n1, P2, n2)
    return [P1, Q, P2], float(np.linalg.norm(Q - P1)), float(np.linalg.norm(Q - P2))


def relief_need(K, A, B, h1, h2, amin, a1_fixed=None, a2_fixed=None):
    """The smallest (a1, a2), each at least amin (or as fixed), whose relief leaves the outline square to KA for
    h1 and square to KB for h2 (each fold's tangent distance and a margin)."""
    best = None
    steps = [amin + 0.1 * i for i in range(0, 400)]
    for x in ([a1_fixed] if a1_fixed is not None else steps):
        for y in ([a2_fixed] if a2_fixed is not None else steps):
            try:
                _pts, l1, l2 = kite(K, A, B, x, y)
            except ValueError:
                continue
            if l1 >= h1 - 1e-9 and l2 >= h2 - 1e-9:
                if best is None or x + y < best[0] + best[1]:
                    best = (x, y)
                break
    if best is None:
        raise ValueError("no relief fits at corner %s" % np.round(K, 2))
    return best


def inside_margin(pt, poly, n, margin):
    """True when pt (on the polygon's plane) lies inside the planar polygon and at least `margin` from its edges."""
    pt = np.asarray(pt, float)
    u = unit(poly[1] - poly[0])
    v = np.cross(n, u)
    q = [(float(np.dot(p - poly[0], u)), float(np.dot(p - poly[0], v))) for p in poly]
    x, y = float(np.dot(pt - poly[0], u)), float(np.dot(pt - poly[0], v))
    inside = False
    for i in range(len(q)):
        (x1, y1), (x2, y2) = q[i], q[(i + 1) % len(q)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
        ex, ey = x2 - x1, y2 - y1
        L2 = ex * ex + ey * ey
        s = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x1) * ex + (y - y1) * ey) / L2))
        if np.hypot(x - (x1 + s * ex), y - (y1 + s * ey)) < margin - 1e-9:
            return False
    return inside
