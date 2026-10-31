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

import json
import math

# The point list handed to DrawingSketch Lines.add for one straight segment a-b, in
# the form a live probe showed Fusion keeps (ga_pdf_check.py probe; the add is a
# preview API: on 2026-10-31 a closed 5-point chain lost a corner and 2-point lines
# came out as scraps in the PDF). "own-sketch" is the plain form, one sketch per
# segment; "none" means no form worked, so nothing is drawn.
LINE_MODES = ("plain", "mid", "dup-first", "dup-last", "own-sketch")

# ISO 128-50: a cut face too thin to hatch is shown solid; at 1:20 a skin, frame or
# cassette layer is 0.15 to 2 mm wide on the sheet. Narrower than THIN_MM on the
# sheet: lines FILL_MM apart (about solid at the 0.35 mm line); else HATCH_MM apart.
THIN_MM = 2.0
FILL_MM = 0.5
HATCH_MM = 2.0


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


def chain_for(a, b, mode="plain"):
    """Points for one Lines.add call drawing the segment a-b in the given form."""
    if mode in ("plain", "own-sketch"):
        return [a, b]
    if mode == "mid":
        return [a, ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0), b]
    if mode == "dup-first":
        return [a, a, b]
    if mode == "dup-last":
        return [a, b, b]
    raise ValueError("no form of Lines.add draws a straight line (%r), so nothing is drawn" % (mode,))


def read_line_mode(path=None, default="plain"):
    """The form from the probe's JSON file (ga_pdf_check.py probe), or default without one."""
    if not path:
        return default
    with open(path, encoding="utf-8") as fh:
        mode = json.load(fh)["mode"]
    if mode not in LINE_MODES and mode != "none":
        raise ValueError("unknown line mode %r in %s" % (mode, path))
    return mode


def loop_area_perimeter(loops):
    """(area, perimeter) of a face given as loops (outer + holes, even-odd)."""
    if loops and isinstance(loops[0][0], (int, float)):
        loops = [loops]
    areas, per = [], 0.0
    for lp in loops:
        m = len(lp)
        if m < 3:
            continue
        a2 = sum(lp[i][0] * lp[(i + 1) % m][1] - lp[(i + 1) % m][0] * lp[i][1] for i in range(m))
        areas.append(abs(a2) / 2.0)
        per += sum(math.dist(lp[i], lp[(i + 1) % m]) for i in range(m))
    if not areas:
        return 0.0, per
    big = max(areas)
    return max(0.0, big - (sum(areas) - big)), per


def face_width(loops):
    """About how wide a face is: 2 x area / perimeter (a long strip's width; half a
    square's side, so small compact faces count as thin and are filled)."""
    area, per = loop_area_perimeter(loops)
    return 2.0 * area / per if per > 0 else 0.0


def spacing_for(loops, thin=THIN_MM, fill=FILL_MM, hatch=HATCH_MM):
    """FILL_MM for a face thinner than THIN_MM on the sheet, else HATCH_MM."""
    return fill if face_width(loops) < thin else hatch
