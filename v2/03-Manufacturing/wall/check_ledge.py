"""The cassette ledge measured against the real shapes round it (the Lead's ruling of 2026-11-01: a wall cassette's
weight sits on a ledge; WALL's sizes, accepted the same day), from the STEPs, not from the parameters.

    python3 v2/03-Manufacturing/wall/check_ledge.py PANEL_STEP CASSETTE_STEP [BASE_STEP]

With no BASE STEP it reads v2/03-Manufacturing/base/110000_P01_BASE_STEP.step. In the pod's axes, for a side panel
(its frame's room face normal to X; the room toward the pod's centre) or a back panel (normal to Y; B1, B2: the ledge
runs along X), the wall's normal read from the ledge's own box (its long side runs along the wall):
1. the pad's top meets the tray's bottom (within 0.05) under at least 10 of the tray's flat, so the cassette rests
   on it and the lining stays where it was;
2. the ledge's upright and the rivet heads stay off the tray's back: at least 2.0 and 1.0 clear, so the cassette
   still floats (D-17) in the 4 mm gap;
3. the ledge stays clear of BASE: at least 5 from the base band (it drops below the frame inboard of the band's
   inner face) and 50 above the lip seal;
4. the ledge lies inside the cassette's length, at least 4.9 in from each end.
Prints each measurement; exit 1 if one fails.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "checks"))
import stepfile  # noqa: E402


def solids(path, words, exclude=()):
    """[(product name, [points in the pod's axes])] of every placed solid whose product name has all `words`."""
    sf = stepfile.StepFile(path)
    out = []
    for inst in sf.instances():
        name = (inst["name"] or "").upper()
        if all(w in name for w in words) and not any(x in name for x in exclude):
            s = sf.solid(inst["solid"])
            out.append((inst["name"], [inst["frame"].point(p) for p in s.points()]))
    return out


def box(pts):
    return [min(p[k] for p in pts) for k in range(3)] + [max(p[k] for p in pts) for k in range(3)]


def gap(a, b):
    """The largest axis gap between two boxes (0 if they overlap on every axis)."""
    return max(max(a[k] - b[k + 3], b[k] - a[k + 3]) for k in range(3))


def main(argv):
    panel, cass = argv[1], argv[2]
    base = argv[3] if len(argv) > 3 else os.path.join(ROOT, "v2/03-Manufacturing/base/110000_P01_BASE_STEP.step")
    ledge = solids(panel, ("CASSETTE LEDGE",), ("PAD",))
    pad = solids(panel, ("LEDGE PAD",))
    rivets = solids(panel, ("BLIND RIVET",))
    tray = solids(cass, ("LINING - TRAY",))
    if not (ledge and pad and tray):
        print("missing: %s" % ", ".join(k for k, v in (("ledge", ledge), ("pad", pad), ("tray", tray)) if not v))
        return 1
    lp, pp, tp = ledge[0][1], pad[0][1], tray[0][1]
    lb, pb, tb = box(lp), box(pp), box(tp)
    # the ledge's long side runs along the wall: Y on a side panel (normal X), X on a back panel (normal Y)
    a = 1 if lb[4] - lb[1] > lb[3] - lb[0] else 0
    n = 1 - a
    room = 1.0 if (tb[n] + tb[n + 3]) / 2 > (lb[n] + lb[n + 3]) / 2 else -1.0     # +1: the room toward +normal
    tray_back = tb[n] if room > 0 else tb[n + 3]
    fails = []

    def check(ok, text):
        print(("ok    " if ok else "FAIL  ") + text)
        if not ok:
            fails.append(text)

    # 1. the pad's top on the tray's bottom, over the tray's flat (past its bend, 1.0 from its back)
    z_tray = tb[2]
    check(abs(pb[5] - z_tray) < 0.05, "pad top Z %.2f, the tray's bottom Z %.2f" % (pb[5], z_tray))
    tray_room = tb[n + 3] if room > 0 else tb[n]
    flat = sorted((tray_back + room * 1.0, tray_room - room * 1.0))       # the bottom's flat, between its bends
    under = min(pb[n + 3], flat[1]) - max(pb[n], flat[0])
    check(under >= 10.0, "the pad under the tray's flat bottom for %.1f across" % under)
    # 2. the upright and the rivet heads off the tray's back
    upright = [p for p in lp if p[2] > z_tray + 1.0]
    up_face = max(p[n] for p in upright) if room > 0 else min(p[n] for p in upright)
    check((tray_back - up_face) * room >= 2.0, "the upright's room face %.2f from the tray's back" % (
        (tray_back - up_face) * room))
    if rivets:
        heads = [max(p[n] for p in r[1]) if room > 0 else min(p[n] for p in r[1]) for r in rivets]
        worst = min((tray_back - h) * room for h in heads)
        check(worst >= 1.0, "%d rivet heads, the nearest %.2f from the tray's back" % (len(rivets), worst))
    else:
        check(False, "no rivets in the panel STEP")
    # 3. clear of BASE: the band and the lip seal
    bands = [b for b in solids(base, ("BAND TUBE",)) if box(b[1])[a] < lb[a + 3] and box(b[1])[a + 3] > lb[a]
             and min(abs(box(b[1])[n] - lb[n]), abs(box(b[1])[n + 3] - lb[n + 3])) < 200]
    near = min((gap(lb, box(b[1])), b[0]) for b in bands) if bands else (None, "")
    check(near[0] is not None and near[0] >= 5.0, "%.2f from the nearest base band (%s)" % (
        near[0] if near[0] is not None else -1, near[1]))
    seals = [s for s in solids(base, ("LIP",)) if gap(lb, box(s[1])) < 200]
    if seals:
        sz = min(lb[2] - box(s[1])[5] for s in seals)
        check(sz >= 50.0, "%.1f above the lip seal" % sz)
    # 4. inside the cassette's length
    ends = (lb[a] - tb[a], tb[a + 3] - lb[a + 3])
    check(min(ends) >= 4.9, "the ledge %.2f long, %.2f and %.2f in from the cassette's ends" % (
        lb[a + 3] - lb[a], ends[0], ends[1]))
    print("%s: %s" % (os.path.basename(panel), "the ledge checks pass" if not fails else "%d fail" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
