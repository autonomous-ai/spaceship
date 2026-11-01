"""ELECTRICAL's cable-tie holes in a lining tray, checked against the frame members behind it, on the STEPs.

A Heyco 3904 push-mount tie's wings open behind the tray's back sheet, in the 4 mm gap, so no tie hole may sit in front
of a frame member (ELECTRICAL's rule, the Lead's relay of 2026-11-01 11:37 UTC). For each Ø6.4 hole in the tray of a
cassette STEP, this finds the frame members of the panel STEP of the same position (products numbered 212xxx) and the
distance, in the tray's plane, from the hole's edge to the nearest member's face. It must be WING mm or more.

    python3 v2/03-Manufacturing/wall/check_tie_holes.py CASSETTE_STEP PANEL_STEP

Exit 1 if a hole is closer, or if the cassette has none (a tray that should carry ties was rebuilt without them).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "checks"))
import stepfile  # noqa: E402

TIE_D = 6.4
WING = 5.0          # the tie's wings past the hole's edge, behind the sheet (assumption until ELECTRICAL's part sheet)


def tie_holes(path):
    """[(centre in pod axes, axis index)] of the Ø6.4 through holes in the tray's solid."""
    sf = stepfile.StepFile(path)
    out = []
    for inst in sf.instances():
        if "TRAY" not in (inst["name"] or "").upper():
            continue
        s = sf.solid(inst["solid"])
        for h in s.holes:
            if abs(h.diameter - TIE_D) < 0.05:
                c = inst["frame"].point(h.center)
                a = inst["frame"].vector(h.axis)
                out.append((c, max(range(3), key=lambda k: abs(a[k]))))
    return out


def member_boxes(path):
    sf = stepfile.StepFile(path)
    out = []
    for inst in sf.instances():
        if (inst["part_number"] or "").startswith("212"):
            pts = [inst["frame"].point(p) for p in sf.solid(inst["solid"]).points()]
            out.append(("%s %s" % (inst["part_number"], inst["name"]),
                        [min(p[k] for p in pts) for k in range(3)] + [max(p[k] for p in pts) for k in range(3)]))
    return out


def main(argv):
    holes, members = tie_holes(argv[1]), member_boxes(argv[2])
    if not holes:
        print("%s: no Ø%g tie holes in its tray" % (os.path.basename(argv[1]), TIE_D))
        return 1
    if not members:
        print("%s: no frame members (212xxx) found" % os.path.basename(argv[2]))
        return 1
    worst, bad = None, []
    for c, ax in holes:
        plane = [k for k in range(3) if k != ax]
        best = None
        for name, b in members:
            gap = max(max(b[k] - c[k], c[k] - b[k + 3], 0.0) for k in plane)   # centre to the member's face, in the plane
            if best is None or gap < best[0]:
                best = (gap, name)
        edge = best[0] - TIE_D / 2
        print("tie at (%s): edge %.1f from %s" % (", ".join("%.1f" % c[k] for k in plane), edge, best[1][:50]))
        worst = edge if worst is None else min(worst, edge)
        if edge < WING:
            bad.append(c)
    print("%s: %d tie holes, the closest edge %.1f from a member (needs %.1f): %s" % (
        os.path.basename(argv[1]), len(holes), worst, WING, "clear" if not bad else "%d too close" % len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
