#!/usr/bin/env python3
"""Read back the lines a GA drawing's PDF really holds, per layer, offline.

    python3 ga_pdf_check.py symbol DRAWING.pdf            # GA sheet 1: the first-angle symbol, side by side
    python3 ga_pdf_check.py outline DRAWING.pdf [--min 30]  # a section sheet: its view, and no hatch or probe layer

Why: a drawing sketch's lines in Fusion's PDF can differ from what was asked (2026-10-31: GA sheet 1's
closed first-angle symbol came out as a triangle while the script saw every add succeed). Fusion's export
puts each drawing sketch on its own layer (an optional content group named after the sketch) and the view's
edges on "Visible", so both can be read back and checked before a drawing is saved. Standard library only.
"""

import math
import re
import sys
import zlib

PT_MM = 25.4 / 72.0
TOL = 0.15                   # mm: the PDF holds coordinates to about 0.02 mm


def _objects(data):
    return {int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+) 0 obj(.*?)endobj", data, re.S)}


def _streams(data):
    """Each stream's bytes, inflated: cut by its /Length when that is a number (the
    data can end in a CR or LF byte of its own), else up to "endstream"."""
    for m in re.finditer(rb"stream\r?\n", data):
        if data[max(0, m.start() - 3):m.start()] == b"end":
            continue
        head = data[max(0, m.start() - 300):m.start()]
        n = re.findall(rb"/Length\s+(\d+)(?!\s+\d+\s+R)", head)
        if n and m.end() + int(n[-1]) <= len(data):
            raw = data[m.end():m.end() + int(n[-1])]
        else:
            e = data.find(b"endstream", m.end())
            raw = data[m.end():e if e >= 0 else len(data)].rstrip(b"\r\n")
        try:
            yield zlib.decompressobj().decompress(raw)
        except zlib.error:
            yield raw


TOKEN = re.compile(rb"/[^\s/<>\[\]()%]+|<[0-9A-Fa-f\s]*>|\((?:\\.|[^\\)])*\)|[-+]?(?:\d+\.?\d*|\.\d+)|[A-Za-z*'\"]+|\[|\]")
PAINT = {b"S", b"s", b"f", b"F", b"f*", b"B", b"B*", b"b", b"b*"}


def layers(data):
    """{layer name: [path, ...]}, each path a list of (op, (x, y)) in sheet mm, op m, l or c
    (for c, the curve's end point): every PAINTED path (stroked or filled; clip-only paths
    are left out) inside a layer's marked content. A page's content streams run as one,
    so the scale (cm) set in one stream holds in the next (Fusion sets 0.06 once)."""
    objs = _objects(data)
    names = {}
    for num, body in objs.items():
        if b"/OCG" in body:
            n = re.search(rb"/Name\s*\((.*?)\)\s*[/>]", body, re.S)
            if n:
                names[num] = n.group(1).decode("latin-1")
    res = {}
    for m in re.finditer(rb"/Properties\s*<<(.*?)>>", data, re.S):
        for key, num in re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", m.group(1)):
            if int(num) in names:
                res[key.decode()] = names[int(num)]
    out = {}
    k = PT_MM                                     # pt to mm until a cm says otherwise
    for s in _streams(data):
        stack, ks, ops, path = [], [], [], None
        for tok in TOKEN.findall(s):
            if tok[:1].isdigit() or tok[:1] in b"-+." or tok[:1] in b"/<([":
                ops.append(tok)
                continue
            if tok == b"]":
                continue
            nums = []
            for o in ops:
                try:
                    nums.append(float(o))
                except ValueError:
                    pass
            if tok == b"q":
                ks.append(k)
            elif tok == b"Q":
                k = ks.pop() if ks else k
            elif tok == b"cm" and len(nums) >= 6:
                k = k * nums[-6] if abs(nums[-6] - nums[-3]) < 1e-9 else k
            elif tok == b"BDC":
                tag = ops[-2] if len(ops) >= 2 else b""
                stack.append(res.get(ops[-1][1:].decode(), ops[-1][1:].decode()) if tag == b"/OC" and ops else None)
            elif tok == b"BMC":
                stack.append(None)
            elif tok == b"EMC":
                if stack:
                    stack.pop()
            elif tok == b"m" and len(nums) >= 2:
                path = (path or []) + [("m", (nums[-2] * k, nums[-1] * k))]
            elif tok == b"l" and len(nums) >= 2 and path is not None:
                path.append(("l", (nums[-2] * k, nums[-1] * k)))
            elif tok == b"c" and len(nums) >= 6 and path is not None:
                path.append(("c", (nums[-2] * k, nums[-1] * k)))
            elif tok == b"re" and len(nums) >= 4:
                x, y, w, h = (v * k for v in nums[-4:])
                path = (path or []) + [("m", (x, y)), ("l", (x + w, y)), ("l", (x + w, y + h)),
                                       ("l", (x, y + h)), ("l", (x, y))]
            elif tok == b"h" and path:
                firsts = [p for op, p in path if op == "m"]
                if firsts:
                    path.append(("l", firsts[-1]))
            elif tok in PAINT:
                if path and stack and stack[-1] is not None:
                    if tok in (b"s", b"b", b"b*"):
                        firsts = [p for op, p in path if op == "m"]
                        if firsts:
                            path.append(("l", firsts[-1]))
                    # a path with several m's is several sub-paths
                    cur = None
                    for op, p in path:
                        if op == "m":
                            cur = [("m", p)]
                            out.setdefault(stack[-1], []).append(cur)
                        elif cur is not None:
                            cur.append((op, p))
                path = None
            elif tok == b"n":
                path = None                       # a clip path, never painted
            ops = []
    return out


def segments(paths, min_len=0.02):
    """The straight pieces (l after m or l) of the paths, zero-length ones left out."""
    segs = []
    for path in paths:
        prev = None
        for op, p in path:
            if op == "l" and prev is not None and math.dist(prev, p) >= min_len:
                segs.append((prev, p))
            prev = p
    return segs


def curves(paths):
    return sum(1 for path in paths for op, _p in path if op == "c")


def merge_collinear(segs, tol=TOL):
    """Join pieces that meet end to end in a straight line (a chain [a, mid, b] is one)."""
    segs = [tuple(s) for s in segs]
    changed = True
    while changed:
        changed = False
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                a, b = segs[i]
                c, d = segs[j]
                for (p, q), (r, s) in (((a, b), (c, d)), ((b, a), (c, d)), ((a, b), (d, c)), ((b, a), (d, c))):
                    if math.dist(q, r) > tol:
                        continue
                    u, v = (q[0] - p[0], q[1] - p[1]), (s[0] - r[0], s[1] - r[1])
                    w = (s[0] - p[0], s[1] - p[1])
                    lw = math.hypot(*w)
                    if math.hypot(*u) < 1e-9 or math.hypot(*v) < 1e-9 or lw < 1e-9:
                        continue
                    # one straight line when the joint lies on p-s (0.05 mm: the PDF
                    # rounds to 0.02 mm, so short pieces can't be held to an angle)
                    off = abs(w[0] * (q[1] - p[1]) - w[1] * (q[0] - p[0])) / lw
                    if off < 0.05 and u[0] * v[0] + u[1] * v[1] > 0:
                        segs[i] = (p, s)
                        del segs[j]
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return segs


def dedupe(segs, tol=TOL):
    """Each segment once: Fusion's PDF export draws a 2-point line back and forth over
    itself (m B l A l B l A), the same line on paper."""
    out = []
    for a, b in segs:
        if not any((math.dist(a, c) <= tol and math.dist(b, d) <= tol) or
                   (math.dist(a, d) <= tol and math.dist(b, c) <= tol) for c, d in out):
            out.append((a, b))
    return out


def drawn_lines(paths):
    """The straight lines a layer really shows: pieces deduplicated, then joined."""
    return merge_collinear(dedupe(segments(paths)))


def same_segments(got, want, tol=TOL):
    """True when the two lists hold the same straight segments (either direction)."""
    if len(got) != len(want):
        return False
    left = list(got)
    for a, b in want:
        for k, (c, d) in enumerate(left):
            if (math.dist(a, c) <= tol and math.dist(b, d) <= tol) or \
                    (math.dist(a, d) <= tol and math.dist(b, c) <= tol):
                del left[k]
                break
        else:
            return False
    return True


SYMBOL = [((560.0, 37.5), (570.0, 35.0)), ((570.0, 35.0), (570.0, 45.0)),
          ((570.0, 45.0), (560.0, 42.5)), ((560.0, 42.5), (560.0, 37.5))]


def check_outline(pdf_path, min_view_segments=1):
    """A section sheet drawn in outline only (PM ruling 2026-11-01): no hatch or probe layer is left in the
    PDF, and the view's visible edges are there."""
    with open(pdf_path, "rb") as fh:
        lay = layers(fh.read())
    problems = []
    stray = sorted(n for n in lay if n.startswith(("HATCH", "PROBE")))
    if stray:
        problems.append("%d hatch or probe layer(s) in an outline-only sheet: %s" % (len(stray), ", ".join(stray[:5])))
    seen = len(drawn_lines(lay.get("Visible", [])))
    if seen < min_view_segments:
        problems.append("the view's Visible layer holds %d line(s), fewer than %d" % (seen, min_view_segments))
    print("outline: %d view line(s), %d hatch or probe layer(s)" % (seen, len(stray)))
    return problems


def check_symbol(pdf_path, prefix="PROJECTION SYMBOL - FIRST ANGLE"):
    with open(pdf_path, "rb") as fh:
        lay = layers(fh.read())
    paths = [p for name, ps in lay.items() if name.startswith(prefix) for p in ps]
    got = merge_collinear(segments(paths))
    problems = []
    if not same_segments(got, SYMBOL):
        problems.append("the first-angle symbol's outline is %s, not the 4 sides asked" %
                        [[[round(v, 1) for v in a], [round(v, 1) for v in b]] for a, b in got])
    if curves(paths) < 8:
        problems.append("the symbol has %d curve pieces, fewer than its two circles need" % curves(paths))
    print("symbol: %d straight sides, %d curve pieces" % (len(got), curves(paths)))
    return problems


def main(argv):
    if len(argv) >= 2 and argv[0] == "outline":
        n = int(argv[argv.index("--min") + 1]) if "--min" in argv else 1
        problems = check_outline(argv[1], n)
    elif len(argv) >= 2 and argv[0] == "symbol":
        problems = check_symbol(argv[1])
    else:
        print(__doc__)
        return 2
    for p in problems:
        print("PROBLEM: " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
