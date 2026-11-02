"""Which WALL frame members are the same part (PM rule, 2026-11-01): two members share a number only when one
solid matches the other moved or turned, never mirrored, with the same section, length, both end cuts (mitres
and cleat slots included) and holes.

    python3 v2/03-Manufacturing/wall/check_member_identity.py [STEP ...]

With no arguments it reads every panel STEP here (2101xx, 2102xx). Each member is one solid: in a STEP built
as D-120 asks, a product whose number starts 212 (its copies are the same solid, counted once); in an older
STEP, a frame body named RAIL - ... or STILE - .... For each member, in its own box (origin at the box centre,
the pod axes): the two ends of every straight edge of its flat faces (the section, the length, the mitre and
chamfer faces, the straight sides of the cleat slots; a hole's seam line is left out, Fusion puts it anywhere)
and every hole (centre, axis, diameter). Two members are the same part when
one of the 24 turns that take the axes onto the axes (determinant +1: no mirror) maps the first's box, edge ends
and holes onto the second's within 0.05 mm. Prints the groups of same parts with the
turn that matches each, and the numbers a group would free (all but its first).
"""

import glob
import itertools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "checks"))
import stepfile  # noqa: E402

TOL = 0.05
POSITIONS = {"210101": "L1", "210102": "R1", "210103": "L2", "210104": "R2",
             "210201": "B1", "210202": "B2", "210203": "B3", "210204": "B4"}


def turns():
    """The 24 signed permutation matrices with determinant +1 (rotations of a right-handed frame)."""
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0] * 3 for _ in range(3)]
            for r in range(3):
                m[r][perm[r]] = signs[r]
            det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                   + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
            if det == 1:
                out.append(m)
    return out


TURNS = turns()


def apply(m, v):
    return tuple(sum(m[r][c] * v[c] for c in range(3)) for r in range(3))


def turn_name(m):
    if m == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        return "as placed"
    flips = [r for r in range(3) if m[r][r] == -1]
    if all(m[r][r] != 0 for r in range(3)) and len(flips) == 2:
        axis = "xyz"[[r for r in range(3) if m[r][r] == 1][0]]
        return "turned half round about %s" % axis
    return "turned %s" % m


def signature(sf, inst):
    """(box size, edge ends, holes) of one placed solid, in its own box (centre at 0), mm."""
    s = sf.solid(inst["solid"])
    fr = inst["frame"]
    pts = [fr.point(p) for p in s.points()]
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    c = [(lo[k] + hi[k]) / 2.0 for k in range(3)]
    ends = set()
    for f in s.faces:
        if f.kind != "plane":        # a hole's cylinder has a seam line wherever Fusion put it: not geometry
            continue
        for a, b in f.lines:
            for p in (a, b):
                q = fr.point(p)
                ends.add(tuple(q[k] - c[k] for k in range(3)))
    holes = []
    for h in s.holes:
        q = fr.point(h.center)
        a = fr.vector(h.axis)
        ax = max(range(3), key=lambda k: abs(a[k]))
        holes.append((round(h.diameter, 2), ax, tuple(q[k] - c[k] for k in range(3))))
    return tuple(hi[k] - lo[k] for k in range(3)), sorted(ends), holes


def close(p, q):
    return all(abs(a - b) <= TOL for a, b in zip(p, q))


def match_sets(a, b):
    """Every point of a has one within TOL in b and the other way round (equal counts after merging)."""
    if len(a) != len(b):
        return False
    used = [False] * len(b)
    for p in a:
        for j, q in enumerate(b):
            if not used[j] and close(p, q):
                used[j] = True
                break
        else:
            return False
    return True


def same_part(sa, sb):
    """The first turn that maps member a onto member b, or None."""
    (da, ea, ha), (db, eb, hb) = sa, sb
    for m in TURNS:
        if not close([abs(x) for x in apply(m, da)], db):
            continue
        if not match_sets([apply(m, p) for p in ea], eb):
            continue
        ha2 = [(d, [r for r in range(3) if m[r][ax] != 0][0]) + apply(m, cen) for d, ax, cen in ha]
        if match_sets(ha2, [(d, ax) + cen for d, ax, cen in hb]):
            return m
    return None


def members(path):
    """{key: (label, signature)} of one STEP's frame members, one per distinct solid."""
    sf = stepfile.StepFile(path)
    pos = POSITIONS.get(os.path.basename(path)[:6], os.path.basename(path)[:6])
    out = {}
    for inst in sf.instances():
        pn = inst["part_number"] or ""
        s = sf.solid(inst["solid"])
        if pn.startswith("212"):
            key, label = (pos, pn), "%s %s" % (pn, inst["name"])
        elif (s.name or "").upper().startswith(("RAIL - ", "STILE - ")) and "FRAME" in " ".join(inst["path"]).upper():
            key, label = (pos, s.name), s.name
        else:
            continue
        if key not in out:
            out[key] = (label, signature(sf, inst))
    return out


def main(argv):
    paths = argv[1:] or sorted(glob.glob(os.path.join(HERE, "2101[0-9][0-9]_P01_*_STEP.step")) +
                               glob.glob(os.path.join(HERE, "2102[0-9][0-9]_P01_*_STEP.step")))
    allm = {}
    for p in paths:
        allm.update(members(p))
    groups = []                     # [(first key, [(key, turn)])]
    for key in sorted(allm):
        for g in groups:
            m = same_part(allm[g[0]][1], allm[key][1])
            if m is not None:
                g[1].append((key, turn_name(m)))
                break
        else:
            groups.append((key, [(key, "as placed")]))
    freed = 0
    for i, (first, mem) in enumerate(groups, 1):
        d = allm[first][1][0]
        print("part %d: %s, box %.2f x %.2f x %.2f, %d edge ends, %d holes" % (
            i, allm[first][0], d[0], d[1], d[2], len(allm[first][1][1]), len(allm[first][1][2])))
        for key, how in mem:
            print("    %s %s: %s" % (key[0], allm[key][0], how))
        freed += len(mem) - 1
    print("%d members in %d STEP(s): %d distinct parts; sharing would free %d numbers" % (
        len(allm), len(paths), len(groups), freed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
