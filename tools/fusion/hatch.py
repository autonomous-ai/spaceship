"""Hatch lines for a cut face on a drawing sheet (the API has no hatch).

    from hatch import hatch_segments
    segs = hatch_segments([(x0, y0), (x1, y1), ...], spacing=3.0, angle_deg=45.0)

Pure geometry, standard library only, so it is tested offline
(test_hatch.py) and pasted into Fusion scripts by source. Given a closed
polygon in sheet mm (a cut face's outer loop mapped onto the view, holes as
extra loops), it returns the segments of parallel lines at `angle_deg`,
`spacing` mm apart, that lie inside it (even-odd rule, so a loop inside a
loop is a hole). Draw them with DrawingSketch lines. ISO 128-50 hatching:
thin lines at 45 degrees; adjacent parts get different angles or spacings.
"""

import math


def hatch_segments(loops, spacing=3.0, angle_deg=45.0, phase=0.0):
    """loops: one polygon [(x, y), ...] or a list of them (outer + holes).
    Returns [((x1, y1), (x2, y2)), ...] in the same units."""
    if loops and isinstance(loops[0][0], (int, float)):
        loops = [loops]
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))          # along the hatch lines
    n = (-d[1], d[0])                        # across them
    edges = []
    for loop in loops:
        m = len(loop)
        for i in range(m):
            p, q = loop[i], loop[(i + 1) % m]
            if p != q:
                edges.append((p, q))
    if not edges:
        return []
    proj = [p[0] * n[0] + p[1] * n[1] for e in edges for p in e]
    lo, hi = min(proj), max(proj)
    out = []
    k0 = math.floor((lo - phase) / spacing) + 1
    c = phase + k0 * spacing
    while c < hi:
        hits = []
        for p, q in edges:
            sp = p[0] * n[0] + p[1] * n[1] - c
            sq = q[0] * n[0] + q[1] * n[1] - c
            if (sp > 0) == (sq > 0):          # same side (a vertex on the line counts once)
                continue
            t = sp / (sp - sq)
            x, y = p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])
            hits.append((x * d[0] + y * d[1], (x, y)))
        hits.sort()
        for j in range(0, len(hits) - 1, 2):
            (_s1, a1), (_s2, a2) = hits[j], hits[j + 1]
            if math.dist(a1, a2) > 1e-9:
                out.append((a1, a2))
        c += spacing
    return out
