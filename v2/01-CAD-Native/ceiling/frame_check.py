"""Check a ceiling frame's part design (D-117 mitred corners, D-120 member components), read only.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/frame_check.py \\
        --doc 411101_P01_CEILING-PANEL-FRAME-C1_CAD --arg half=C1 --read-only --close \\
        --screenshot <png> --label "CEILING Engineer"

For the sample (C1 first, then C2, D-118): every member is its own component with the number the
master BOM allocated; each member's box is where ceiling_model.frame_members puts it; each mitre's
end faces have the corner design's angles (45 deg at the front, the back member 26.57 deg off square
and the side and seam members 63.43 deg); each joint hole of that half is where the joints register
puts it, and nothing else is round (the frame is welded, D-131: no cleat slots);
the timeline is healthy and every sketch fully constrained. Prints FRAME CHECK: PASS or FAIL.
"""

import math
import os
import sys

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
for _n in ("ceiling_model", "ceiling_checks"):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != HERE:
        del sys.modules[_n]
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)
import ceiling_model as M  # noqa: E402
import ceiling_checks as C  # noqa: E402

TOL = 0.05


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    half = ARGS.get("half", "C1")
    vals = C.param_values(design)
    root = design.rootComponent
    bad = []
    # components and their numbers
    want_pn = {}
    for code, key, bname, _axis, _pts, _z0, _z1 in M.member_shapes(half):
        want_pn[code] = M.PARTS[key][0]
    occs = [o for o in root.allOccurrences if o.component.bRepBodies.count]
    seen = {}
    for o in occs:
        seen.setdefault(o.component.partNumber, []).append(o)
    for code, pn in want_pn.items():
        if pn not in seen:
            bad.append(("no component for", code, pn))
    cross = seen.get(M.PARTS["m_cross"][0], [])
    print("components with bodies: %d (%s); plain cross member copies: %d" % (
        len(occs), ", ".join(sorted(seen)), len(cross)))
    if len(cross) != 2:
        bad.append(("plain cross member copies", len(cross)))
    for o in occs:
        if o.component.bRepBodies.count != 1:
            bad.append(("bodies in", o.component.name, o.component.bRepBodies.count))
    # boxes against the layout
    exp = {code: [M.ev(vals, e) for e in b] for code, _n, _a, b in M.frame_members(half)}
    got = {}
    for o in occs:
        for b in o.bRepBodies:
            bb = C.bb_mm(b)
            got.setdefault(o.component.partNumber, []).append(bb)
    worst = 0.0
    for code, pn in want_pn.items():
        e = exp[code]
        e6 = [e[0], e[2], e[4], e[1], e[3], e[5]]
        cands = got.get(pn, [])
        if not cands:
            continue
        d = min(max(abs(p - q) for p, q in zip(c, e6)) for c in cands)
        worst = max(worst, d)
        if d > TOL:
            bad.append(("box off", code, round(d, 3)))
    print("member boxes against the layout: worst %.3f mm" % worst)
    # mitre angles from the end faces
    for o in occs:
        pn = o.component.partNumber
        code = [c for c, p in want_pn.items() if p == pn]
        if not code or code[0] not in ("SIDE", "SEAM", "FRONT", "BACK"):
            continue
        code = code[0]
        axis = 1 if code in ("SIDE", "SEAM") else 0
        angles = []
        for b in o.bRepBodies:
            for f in b.faces:
                if f.geometry.objectType != adsk.core.Plane.classType():
                    continue
                n = adsk.core.Plane.cast(f.geometry).normal
                c = abs((n.x, n.y, n.z)[axis])
                # the open ends' rims (138 to 310 mm2 on these tubes), not the slots' or the spigot
                # slot's short walls (under 30 mm2) or the long faces (normal across the axis)
                if c > 0.1 and f.area * 100 > 100:
                    angles.append(round(math.degrees(math.acos(min(1.0, c))), 2))
        angles = sorted(set(angles))
        want = {"FRONT": [45.0], "BACK": [26.57], "SIDE": [45.0, 63.43], "SEAM": [45.0, 63.43]}[code]
        ok = all(any(abs(a - w) < 0.05 for a in angles) for w in want)
        print("mitres %s: end faces off square %s (want %s)%s" % (code, angles, want, "" if ok else "  <- WRONG"))
        if not ok:
            bad.append(("mitre", code, angles))
    # holes: only this half's
    h = C.hole_check(design)
    other = "C2" if half == "C1" else "C1"
    hb = [x for x in h["bad"] if not str(x[0]).startswith(other)]
    print("joint holes of %s: %d checked in both halves, worst %.3f mm, off %s" % (half, h["checked"], h["worst"], hb or "none"))
    bad += hb
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [c.name + "/" + sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
    print("timeline %d items, unhealthy %d, loose sketches %d" % (tl.count, len(unhealthy), len(loose)))
    bad += [("unhealthy", u) for u in unhealthy] + [("loose", l) for l in loose]
    for o in occs:
        print("MASS|%s|%s|%.3f kg" % (o.fullPathName, o.component.partNumber, o.component.getPhysicalProperties().mass))
    print("FRAME CHECK:", "FAIL %s" % bad if bad else "PASS")
    if bad:
        raise RuntimeError("frame check failed")
