"""Each WALL frame member's end cuts, read from its panel STEP, against its parts-list row.

The Lead's ruling of 2026-11-01: a welded frame's drawing carries its members' cut list (number, section, cut
length, both end angles, quantity), and that cut list is the member's drawing. So each row must give each end's
angle by its end and the face the long points lie on, and they must be the STEP's.

    python3 v2/03-Manufacturing/wall/check_member_ends.py [PANEL_STEP ...]

With no arguments it reads every panel STEP here whose members are their own products (212xxx, D-120), with the
parts list of the same panel number. For each member, in the pod's axes:
- its axis is its box's longest side, and its cut length that side's length;
- each end is the plane face that reaches that end of the box; its angle off square is the angle between its
  normal and the axis, and its long point lies on the side face that the normal's sideways part points away from;
- the row's note must name the same: square ends, or each end (front and back along Y, bottom and top along Z,
  outer and centre along X on a back panel, outer at the pod's corner) with its angle within 0.01°, and the long
  points' face (bottom, top, front, back, corner-side or seam-side). The cut length must match within 0.02.
Exit 1 on any mismatch.
"""

import csv
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "checks"))
import stepfile  # noqa: E402

ANGLE_TOL = 0.01
LENGTH_TOL = 0.02
LEFT = {"210101", "210103", "210201", "210203"}       # the panels whose outer side is at -X: L1, L2, B1, B3
BACK = {"210201", "210202", "210203", "210204"}


def end_cuts(path):
    """{pn: {"axis": "Y", "length": mm, "low": (angle, side), "high": (angle, side)}} for each member product
    (212xxx) of a panel STEP. side is the face the long point lies on, as '-Z', or '' for a square end."""
    sf = stepfile.StepFile(path)
    out = {}
    for inst in sf.instances():
        pn = inst["part_number"] or ""
        if not pn.startswith("212") or pn in out:
            continue
        s = sf.solid(inst["solid"])
        fr = inst["frame"]
        pts = [fr.point(p) for p in s.points()]
        box = [min(p[k] for p in pts) for k in range(3)] + [max(p[k] for p in pts) for k in range(3)]
        ax = max(range(3), key=lambda k: box[k + 3] - box[k])
        cut = {"axis": "XYZ"[ax], "length": box[ax + 3] - box[ax]}
        for end, at in (("low", box[ax]), ("high", box[ax + 3])):
            best = None
            for f in s.faces:
                if f.kind != "plane":
                    continue
                n = fr.vector(f.normal)
                if abs(n[ax]) < 0.05:
                    continue
                fp = [fr.point(p) for p in f.points]
                reach = min(abs(p[ax] - at) for p in fp)
                if reach > 0.01:
                    continue                    # not this end's face (a hole's or a slot's flat, say)
                ang = math.degrees(math.acos(min(1.0, abs(n[ax]))))
                side = ""
                if ang > ANGLE_TOL:
                    perp = [n[k] if k != ax else 0.0 for k in range(3)]
                    k = max(range(3), key=lambda i: abs(perp[i]))
                    side = ("-" if perp[k] > 0 else "+") + "XYZ"[k]
                area = len(fp)
                if best is None or area > best[2]:
                    best = (ang, side, area)
            cut[end] = best[:2] if best else None
        out[pn] = cut
    return out


def expected(note, panel):
    """What a row's note says: {"square": True} or {"ends": {end: angle}, "face": side}. Ends and faces become
    the STEP's terms: (axis, 'low'/'high') and '-Z' etc., for the panel's hand."""
    left = panel in LEFT
    where = {"front": ("Y", "low"), "back": ("Y", "high"), "bottom": ("Z", "low"), "top": ("Z", "high"),
             "outer": ("X", "low" if left else "high"), "centre": ("X", "high" if left else "low")}
    faces = {"bottom": "-Z", "top": "+Z", "front": "-Y", "back": "+Y", "corner-side": "-X" if left else "+X",
             "seam-side": "+X" if left else "-X"}
    if re.search(r"\bsquare ends\b", note):
        return {"square": True}
    m = re.search(r"(\w+) end mitred ([\d.]+)° and (\w+) end ([\d.]+)° off square", note)
    if m:
        ends = {m.group(1): float(m.group(2)), m.group(3): float(m.group(4))}
    else:
        m = re.search(r"(\w+) and (\w+) ends both mitred ([\d.]+)° off square", note)
        if not m:
            return None
        ends = {m.group(1): float(m.group(3)), m.group(2): float(m.group(3))}
    f = re.search(r"long points on its ([\w-]+) face", note)
    if not f or any(e not in where for e in ends) or f.group(1) not in faces:
        return None
    return {"ends": {where[e]: a for e, a in ends.items()}, "face": faces[f.group(1)]}


def check(step_path, bom_path):
    """Mismatches between a panel STEP's members and its parts list's member rows (empty: they agree)."""
    panel = os.path.basename(step_path)[:6]
    rows = {r["part_number"]: r for r in csv.DictReader(open(bom_path, encoding="utf-8"))
            if (r.get("part_number") or "").startswith("212")}
    cuts = end_cuts(step_path)
    bad = []
    for pn in sorted(set(rows) | set(cuts)):
        if pn not in rows:
            bad.append("%s: in the STEP, not in the list" % pn)
            continue
        if pn not in cuts:
            bad.append("%s: in the list, not in the STEP" % pn)
            continue
        r, c = rows[pn], cuts[pn]
        if abs(float(r["cut_length_mm"]) - c["length"]) > LENGTH_TOL:
            bad.append("%s: cut length %s in the list, %.3f in the STEP" % (pn, r["cut_length_mm"], c["length"]))
        want = expected(r.get("note") or "", panel)
        if want is None:
            bad.append("%s: the note doesn't name both ends and the long points' face: %r" % (pn, r.get("note")))
            continue
        if c["low"] is None or c["high"] is None:
            bad.append("%s: no end face found at %s" % (pn, "both ends" if c["low"] is None and c["high"] is None
                                                       else ("the low end" if c["low"] is None else "the high end")))
            continue
        if want.get("square"):
            for end in ("low", "high"):
                if c[end][0] > ANGLE_TOL:
                    bad.append("%s: the list says square ends; its %s end is %.3f° off square" % (pn, end, c[end][0]))
            continue
        for (axis, end), ang in sorted(want["ends"].items()):
            if axis != c["axis"]:
                bad.append("%s: the note names an end along %s; the member runs along %s" % (pn, axis, c["axis"]))
                continue
            got, side = c[end]
            if abs(got - ang) > ANGLE_TOL:
                bad.append("%s: %s end %.2f° in the list, %.3f° in the STEP" % (pn, end, ang, got))
            if side != want["face"]:
                bad.append("%s: %s end's long point on %s in the list, %s in the STEP" % (pn, end, want["face"], side))
    return bad


def panel_steps():
    out = []
    for p in sorted(glob.glob(os.path.join(HERE, "210[12]0[1-4]_P01_*_STEP.step"))):
        if end_cuts(p):
            out.append(p)
    return out


def main(argv):
    steps = argv[1:] or panel_steps()
    rc = 0
    for p in steps:
        boms = glob.glob(os.path.join(HERE, "%s_P01_*_BOM.csv" % os.path.basename(p)[:6]))
        if not boms:
            print("%s: no parts list" % os.path.basename(p))
            rc = 1
            continue
        bad = check(p, boms[0])
        n = len(end_cuts(p))
        print("%s: %d members, %s" % (os.path.basename(p)[:6], n, "every end as listed" if not bad else
                                      "%d mismatch(es)" % len(bad)))
        for b in bad:
            print("  " + b)
        rc = rc or (1 if bad else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
