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
# segment; "pairs" is a face's chains cut into pieces of at most 3 segments (4 points), each
# in its own sketch (2026-11-01 07:55: long chains came out garbled, 4-point chains exact);
# "none" means no form worked, so nothing is drawn. Thin faces have their own form (the
# probe's "thin" answer): their fill lines are only 0.3 mm apart, too close to join.
LINE_MODES = ("plain", "mid", "dup-first", "dup-last", "chain", "pairs", "own-sketch")
PIECE_SEGMENTS = 3

# ISO 128-50: a cut face too thin to hatch is shown solid; at 1:20 a skin, frame or
# cassette layer is 0.15 to 2 mm wide on the sheet. Narrower than THIN_MM on the
# sheet: lines FILL_MM apart (about solid at the 0.35 mm line) that run ALONG the
# strip (Fusion's PDF export merges lines under about 1 mm into wrong paths, live
# probe 2026-11-01, so no short 45 degree strokes there); else HATCH_MM apart at 45.
THIN_MM = 2.0
FILL_MM = 0.3
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
    if mode in ("plain", "own-sketch", "chain", "pairs"):
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


def read_thin_mode(path=None, default="none"):
    """The form for thin faces' fill lines from the probe's JSON file ("own-sketch" or "none");
    a file from before this answer existed gives default."""
    if not path:
        return default
    with open(path, encoding="utf-8") as fh:
        mode = json.load(fh).get("thin", default)
    if mode not in ("own-sketch", "none"):
        raise ValueError("unknown thin-face form %r in %s" % (mode, path))
    return mode


def pieces(chain, max_segments=PIECE_SEGMENTS):
    """A point chain cut into chains of at most max_segments segments; each piece starts where
    the last one ended, so together they draw every segment once."""
    if len(chain) <= max_segments + 1:
        return [list(chain)]
    return [list(chain[i:i + max_segments + 1]) for i in range(0, len(chain) - 1, max_segments)]


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


def long_edge_angle(loops):
    """The angle (degrees) of the longest edge of the face's outer loop: the direction
    a thin strip runs in."""
    if loops and isinstance(loops[0][0], (int, float)):
        loops = [loops]
    outer = max(loops, key=lambda lp: abs(sum(lp[i][0] * lp[(i + 1) % len(lp)][1] -
                                                lp[(i + 1) % len(lp)][0] * lp[i][1] for i in range(len(lp)))))
    best, angle = -1.0, 0.0
    for i in range(len(outer)):
        p, q = outer[i], outer[(i + 1) % len(outer)]
        d = math.dist(p, q)
        if d > best:
            best, angle = d, math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0
    return angle


def fill_lines(loops, index=0, thin=THIN_MM, fill=FILL_MM, hatch=HATCH_MM):
    """The lines for one cut face: a thin face gets lines FILL_MM apart along its
    long edge; a wider one 45 or 135 degree hatch (alternating by index)."""
    if face_width(loops) < thin:
        return hatch_segments(loops, spacing=fill, angle_deg=long_edge_angle(loops), phase=fill / 2.0)
    return hatch_segments(loops, spacing=hatch, angle_deg=45.0 if index % 2 == 0 else 135.0)


def _inside(loops, x, y):
    if loops and isinstance(loops[0][0], (int, float)):
        loops = [loops]
    c = False
    for lp in loops:
        for i in range(len(lp)):
            (x1, y1), (x2, y2) = lp[i], lp[(i + 1) % len(lp)]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c


def _on_outline(loops, x, y, tol=0.02):
    if loops and isinstance(loops[0][0], (int, float)):
        loops = [loops]
    for lp in loops:
        for i in range(len(lp)):
            (x1, y1), (x2, y2) = lp[i], lp[(i + 1) % len(lp)]
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
            if math.dist((x, y), (x1 + t * dx, y1 + t * dy)) <= tol:
                return True
    return False


def chains(segments, loops, max_link=None):
    """The hatch segments of one face joined into as few point chains as possible, back
    and forth (each next line reversed), so one Lines.add call draws many lines: Fusion's
    PDF export keeps one chain per sketch exactly, but garbles a sketch of many lines
    (live probe 2026-11-01). A link between two lines must stay inside the face (or on
    its outline) and be no longer than max_link (default: 3 x the line spacing seen);
    otherwise a new chain starts. Returns [[point, ...], ...]."""
    if not segments:
        return []
    if max_link is None:
        gaps = [math.dist(segments[i][0], segments[i + 1][0]) for i in range(len(segments) - 1)]
        max_link = 3.0 * (min(gaps) if gaps else 1.0) + 0.5
    out, cur = [], [segments[0][0], segments[0][1]]
    for a, b in segments[1:]:
        end = cur[-1]
        first, second = (a, b) if math.dist(end, a) <= math.dist(end, b) else (b, a)
        mid = ((end[0] + first[0]) / 2.0, (end[1] + first[1]) / 2.0)
        if math.dist(end, first) <= max_link and (_inside(loops, *mid) or _on_outline(loops, *mid)):
            cur += [first, second]
        else:
            out.append(cur)
            cur = [first, second]
    out.append(cur)
    return out
