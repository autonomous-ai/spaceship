#!/usr/bin/env python3
"""Read back the lines a drawing's PDF really holds, per sketch layer, offline.

    python3 ga_pdf_check.py probe PROBE.pdf OUT.json   # which point form Lines.add keeps
    python3 ga_pdf_check.py hatch DRAWING.pdf "HATCH - SECTION BB" [--min 200]
    python3 ga_pdf_check.py symbol DRAWING.pdf

Why: the drawing sketch Lines.add is a preview API, and what it keeps differs
from what was asked. Live 2026-10-31: GA sheet 1's closed 5-point first-angle
symbol came out as a triangle, and the B-B hatch (2-point lines) as short
vertical scraps, while the script saw every add succeed. Fusion's PDF export
puts each drawing sketch on its own layer (an optional content group named
after the sketch), so the lines can be read back from the PDF and checked.

probe: reads the export of the probe cases (img/probe_lines.py in the session
scratchpad; the cases come with the PDF as PDF.json) and picks the first form
whose cases come out exactly as asked:
  plain      [a, b]
  mid        [a, middle, b]
  dup-first  [a, a, b]
  dup-last   [a, b, b]
  own-sketch [a, b], each segment in a sketch of its own
or "none". The drawing scripts read that choice (--arg line_mode_file).
Standard library only.
"""

import json
import math
import os
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


def layers(data):
    """{layer name: [path, ...]}, each path a list of (op, (x, y)) in sheet mm, op m, l or c
    (for c, the curve's end point), from every drawn path inside the layer's marked content."""
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
    for s in _streams(data):
        cm = re.search(rb"([-\d.]+) 0 0 ([-\d.]+) 0 0 cm", s)
        k = float(cm.group(1)) * PT_MM if cm else PT_MM
        for key, body in re.findall(rb"/OC\s*/(\w+)\s+BDC(.*?)EMC", s, re.S):
            name = res.get(key.decode(), key.decode())
            paths, cur = out.setdefault(name, []), None
            for tok in re.finditer(rb"((?:[-\d.]+\s+){2,6})([mlc])\b", body):
                nums = [float(v) for v in tok.group(1).split()]
                op = tok.group(2).decode()
                need = {"m": 2, "l": 2, "c": 6}[op]
                if len(nums) < need:
                    continue
                p = (nums[-2] * k, nums[-1] * k)
                if op == "m":
                    cur = [("m", p)]
                    paths.append(cur)
                elif cur is not None:
                    cur.append((op, p))
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
                    lu, lv = math.hypot(*u), math.hypot(*v)
                    if lu < 1e-9 or lv < 1e-9:
                        continue
                    if abs(u[0] * v[1] - u[1] * v[0]) / (lu * lv) < 1e-3 and u[0] * v[0] + u[1] * v[1] > 0:
                        segs[i] = (p, s)
                        del segs[j]
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return segs


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


def chain_segments(chains):
    return [(tuple(ch[i]), tuple(ch[i + 1])) for ch in chains for i in range(len(ch) - 1)
            if math.dist(ch[i], ch[i + 1]) >= 0.02]


MODES = [("plain", ("01 2pt", "02 2pt x5")), ("mid", ("06 mid x5",)), ("dup-first", ("07 dup first x5",)),
         ("dup-last", ("08 dup last x5",)), ("own-sketch", ("09 2pt own sketch x5",))]


def probe(pdf_path, out_path):
    if not os.path.exists(pdf_path) or not os.path.exists(pdf_path + ".json"):
        # the probe didn't run (a locked screen skips it): draw no lines this session
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump({"mode": "none", "why": "no probe export at %s" % pdf_path}, fh)
        print("line mode: none (no probe export at %s)" % pdf_path)
        return "none"
    with open(pdf_path, "rb") as fh:
        lay = layers(fh.read())
    with open(pdf_path + ".json", encoding="utf-8") as fh:
        spec = json.load(fh)
    ok, drawn = {}, {}
    for label, chains, _own in spec["cases"]:
        paths = [p for name, ps in lay.items() if name == "PROBE " + label or
                 name.startswith("PROBE " + label + " ") for p in ps]
        got = merge_collinear(segments(paths))
        want = merge_collinear(chain_segments(chains))
        ok[label] = same_segments(got, want)
        drawn[label] = [[[round(v, 2) for v in a], [round(v, 2) for v in b]] for a, b in got]
        print("probe %-22s %s: %d segment(s) drawn, %d asked" % (label, "OK  " if ok[label] else "DIFF",
                                                                    len(got), len(want)))
    mode = next((m for m, need in MODES if all(ok.get(n) for n in need)), "none")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"mode": mode, "ok": ok, "drawn": drawn, "made": spec.get("report")}, fh, indent=1)
    print("line mode: %s (written to %s)" % (mode, out_path))
    return mode


def check_hatch(pdf_path, layer, min_segments=1, angles=(45.0, 135.0)):
    """Problems with the hatch layer: too few lines, or lines not at the hatch angles."""
    with open(pdf_path, "rb") as fh:
        lay = layers(fh.read())
    paths = lay.get(layer, [])
    segs = merge_collinear(segments(paths)) if len(paths) < 400 else segments(paths)
    bad = [s for s in segs if min(abs(((math.degrees(math.atan2(s[1][1] - s[0][1], s[1][0] - s[0][0])) % 180)
                                       - a)) for a in angles) > 1.0 and math.dist(*s) > 0.3]
    problems = []
    if len(segs) < min_segments:
        problems.append("%d hatch lines in %r, fewer than %d" % (len(segs), layer, min_segments))
    if bad:
        problems.append("%d of %d lines are not at %s degrees" % (len(bad), len(segs), angles))
    print("hatch %r: %d lines, %d off-angle; layers: %s" % (layer, len(segs), len(bad), sorted(lay)))
    return problems


SYMBOL = [((560.0, 37.5), (570.0, 35.0)), ((570.0, 35.0), (570.0, 45.0)),
          ((570.0, 45.0), (560.0, 42.5)), ((560.0, 42.5), (560.0, 37.5))]


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
    if len(argv) >= 3 and argv[0] == "probe":
        probe(argv[1], argv[2])
        return 0
    if len(argv) >= 3 and argv[0] == "hatch":
        n = int(argv[argv.index("--min") + 1]) if "--min" in argv else 1
        problems = check_hatch(argv[1], argv[2], n)
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
