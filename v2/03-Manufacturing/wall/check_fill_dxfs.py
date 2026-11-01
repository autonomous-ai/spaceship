"""Check the fill pieces' DXFs (D-128) against the CAD: every fill body in the panel STEPs here, one per bay, has
the outline its form's DXF gives, placed the way FILL-PIECES.csv says (as cut, turned over or end for end).

    python3 v2/03-Manufacturing/wall/check_fill_dxfs.py

For each panel STEP (210101-210104, 210201-210204, those that exist) it reads the bodies of the fill with the
repo's own STEP reader (tools/checks/stepfile.py: mm, every placed copy), and for each body:
- its box: 40 thick, and the bay's w x h;
- its face on one side of the 40 (every coplanar face there, their shared edges dropped), as loops in the bay's
  u, v (u along the wall from the bay's low corner, v up from its bottom), against the DXF's loops moved the way
  the bay takes its piece: each corner of the DXF is a vertex of the face, each vertex of the face lies on the
  DXF's outline, and the enclosed areas agree within 1 mm2.
The DXF is read back from its file (POLYLINE vertices on CUT), not from the script that wrote it. A bay with no
body (B3, B4 until they are built), a position whose forms have no number yet (no DXF), and one the list
leaves out (B2 until its layout is built) are listed, not failed. Exit 1 on any mismatch.
"""

import csv
import glob
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "checks"))
import stepfile  # noqa: E402

PANELS = {"L1": "210101", "R1": "210102", "L2": "210103", "R2": "210104",
          "B1": "210201", "B2": "210202", "B3": "210203", "B4": "210204"}
TOL = 0.05


def dxf_loops(path):
    """The closed POLYLINE loops on the CUT layer, as lists of (x, y)."""
    with open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh.read().splitlines()]
    pairs = list(zip(lines[0::2], lines[1::2]))
    loops, cur, layer, ent, x = [], None, None, None, None
    for c, v in pairs:
        if c == "0":
            ent = v
            if v == "POLYLINE":
                cur, layer = [], None
            elif v == "SEQEND" and cur is not None:
                loops.append(cur)
                cur = None
        elif c == "8":
            layer = v
            if ent == "POLYLINE" and v != "CUT":
                raise ValueError("%s: a polyline on layer %s" % (os.path.basename(path), v))
        elif c == "10" and ent == "VERTEX":
            x = float(v)
        elif c == "20" and ent == "VERTEX" and cur is not None:
            cur.append((x, float(v)))
    return loops


def shoelace(loop):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(loop, loop[1:] + loop[:1])) / 2.0


def on_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    if abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) > TOL * max(1.0, math.dist(a, b)):
        return False
    return min(ax, bx) - TOL <= px <= max(ax, bx) + TOL and min(ay, by) - TOL <= py <= max(ay, by) + TOL


def chain(edges):
    """Undirected edges (p, q) into closed loops of points (shared edges between coplanar faces dropped)."""
    key = lambda p: (round(p[0] / TOL), round(p[1] / TOL))  # noqa: E731
    count = {}
    for p, q in edges:
        k = tuple(sorted((key(p), key(q))))
        if k[0] == k[1]:
            continue
        count.setdefault(k, [0, p, q])[0] += 1
    left = {k: (p, q) for k, (n, p, q) in count.items() if n % 2 == 1}
    adj = {}
    for k, (p, q) in left.items():
        adj.setdefault(k[0], []).append((k[1], q if key(q) == k[1] else p))
        adj.setdefault(k[1], []).append((k[0], p if key(p) == k[0] else q))
    if any(len(v) != 2 for v in adj.values()):
        raise ValueError("the face's edges don't close into simple loops")
    loops, seen = [], set()
    for start in sorted(adj):
        if start in seen:
            continue
        loop, prev, cur = [], None, start
        while True:
            seen.add(cur)
            nbrs = adj[cur]
            nk, npt = nbrs[0] if nbrs[0][0] != prev else nbrs[1]
            loop.append(npt)
            prev, cur = cur, nk
            if cur == start:
                break
        loops.append(loop)
    return loops


def moved(loops, w, h, fit):
    fu, fv = {"as cut": (False, False), "turned over left to right": (True, False),
              "turned over top to bottom": (False, True)}.get(fit, (True, True))
    return [[((w - x) if fu else x, (h - y) if fv else y) for x, y in lp] for lp in loops]


def main():
    bays = {}
    with open(os.path.join(HERE, "FILL-PIECES.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            bays.setdefault(r["position"], []).append(r)
    bad, checked, missing = [], 0, []
    for pos, pn in PANELS.items():
        steps = glob.glob(os.path.join(HERE, "%s_P01_*_STEP.step" % pn))
        rows = sorted(bays.get(pos, []), key=lambda r: int(r["bay"]))
        if not rows:
            missing.append("%s (%s): not in FILL-PIECES.csv (its layout waits)" % (pos, pn))
            continue
        if any(not r["dxf"] for r in rows):
            missing.append("%s (%s): forms %s have no number yet (to allocate), so no DXF to check" % (
                pos, pn, ", ".join(sorted({r["form"] for r in rows if not r["dxf"]}))))
            continue
        if not steps:
            missing.append("%s (%s): no panel STEP yet, %d bays not checked" % (pos, pn, len(rows)))
            continue
        sf = stepfile.StepFile(steps[0])
        back = pos.startswith("B")
        thick_ax, u_ax = (1, 0) if back else (0, 1)
        bodies = []
        for inst in sf.instances():
            if "FILL" not in " ".join([inst["name"] or ""] + list(inst["path"])).upper():
                continue
            s = sf.solid(inst["solid"])
            pts = [inst["frame"].point(p) for p in s.points()]
            lo = [min(p[k] for p in pts) for k in range(3)]
            hi = [max(p[k] for p in pts) for k in range(3)]
            bodies.append((lo, hi, s, inst))
        bodies.sort(key=lambda b: b[0][u_ax])
        if len(bodies) != len(rows):
            bad.append("%s: %d fill bodies in %s, %d bays in FILL-PIECES.csv" % (
                pos, len(bodies), os.path.basename(steps[0]), len(rows)))
            continue
        for (lo, hi, s, inst), r in zip(bodies, rows):
            label = "%s bay %s (%s %s, %s)" % (pos, r["bay"], r["form"], r["number"], r["fit"])
            w, h, t = float(r["w_mm"]), float(r["h_mm"]), float(r["t_mm"])
            size = (hi[u_ax] - lo[u_ax], hi[2] - lo[2], hi[thick_ax] - lo[thick_ax])
            if any(abs(a - b) > TOL for a, b in zip(size, (w, h, t))):
                bad.append("%s: body %.2f x %.2f x %.2f, bay %g x %g x %g" % ((label,) + size + (w, h, t)))
                continue
            top = hi[thick_ax]
            edges = []
            for f in s.faces:
                if f.kind != "plane":
                    continue
                wp = [inst["frame"].point(p) for p in f.points]
                if wp and all(abs(p[thick_ax] - top) < TOL for p in wp):
                    edges += [((inst["frame"].point(a)[u_ax] - lo[u_ax], inst["frame"].point(a)[2] - lo[2]),
                               (inst["frame"].point(b)[u_ax] - lo[u_ax], inst["frame"].point(b)[2] - lo[2]))
                              for a, b in f.lines]
            cad = chain(edges)
            want = moved(dxf_loops(os.path.join(HERE, r["dxf"])), w, h, r["fit"])
            cad_pts = [p for lp in cad for p in lp]
            segs = [(lp[k], lp[(k + 1) % len(lp)]) for lp in want for k in range(len(lp))]
            no_vertex = [c for lp in want for c in lp if not any(math.dist(c, p) < TOL for p in cad_pts)]
            off_line = [p for p in cad_pts if not any(on_segment(p, a, b) for a, b in segs)]
            a_cad = abs(max((shoelace(lp) for lp in cad), key=abs)) - sum(
                abs(shoelace(lp)) for lp in cad if abs(shoelace(lp)) < abs(max((shoelace(q) for q in cad), key=abs)))
            a_dxf = sum(shoelace(lp) for lp in want) * (1 if r["fit"] in ("as cut", "end for end (turned round in its plane)") else -1)
            checked += 1
            if no_vertex or off_line or abs(a_cad - a_dxf) > 1.0:
                bad.append("%s: DXF corners not in the CAD %s; CAD vertices off the DXF outline %s; area CAD %.1f, "
                           "DXF %.1f" % (label, no_vertex[:4], off_line[:4], a_cad, a_dxf))
            else:
                print("ok  %s: %d corners, %d loop(s), %.0f mm2" % (label, sum(len(lp) for lp in want), len(cad), a_cad))
    for m in missing:
        print("--  " + m)
    for b in bad:
        print("BAD " + b)
    print("%d bays checked against the CAD, %d mismatches" % (checked, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
