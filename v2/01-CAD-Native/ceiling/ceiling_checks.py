"""Position checks shared by the ceiling build and its edit test (runs inside Fusion).

check(design) compares every body in the root context with the box the layout
(ceiling_model.py) gives for the design's current parameter values: frame
members, both skins, and in both cassettes the tray, felt, ribs, fill strips,
clips and catches. Repeated parts are paired by nearest fit.
"""

import adsk.core
import adsk.fusion

import ceiling_model as M

TOL = 0.05   # mm
# the frame members' part numbers (D-120): each member its own component; the plain cross member
# (X2, X3 of both halves) is one common part placed as copies
CROSS_PN = M.PARTS["m_cross"][0]
MEMBER_PNS = {v[0] for k, v in M.PARTS.items() if k.startswith("m_")}


def bb_mm(b):
    bb = b.boundingBox
    return [bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.x * 10, bb.maxPoint.y * 10,
            bb.maxPoint.z * 10]


def expected(design):
    """{key: [xmin, ymin, zmin, xmax, ymax, zmax]} from the design's own parameter values."""
    um = design.unitsManager

    def ev(e):
        return um.evaluateExpression(e, "mm") * 10.0
    out = {}
    for half in ("C1", "C2"):
        for code, name, _axis, b in M.frame_members(half):
            x0, x1, y0, y1, z0, z1 = (ev(e) for e in b)
            out["%s %s" % (half, name)] = [x0, y0, z0, x1, y1, z1]
        vals = param_values(design)
        for name, pkey, b in M.plate_boxes(vals, half):          # the mitre plates (D-131, J-FRAME-01)
            out["%s %s %s" % (half, "MITRE", name)] = [b[0], b[2], b[4], b[1], b[3], b[5]]
        sx, sy, sz = (ev(e) for e in M.SKIN_PLACES[half])
        b = [ev(e) for e in M.skin_box()]
        out["SKIN %s" % half] = [b[0] + sx, b[2] + sy, b[4] + sz, b[1] + sx, b[3] + sy, b[5] + sz]
        ox, oy, oz = (ev(e) for e in M.CASSETTE_CS[half])

        def cs(box, key):
            b = [ev(e) for e in box]
            out["%s %s" % (half, key)] = [b[0] + ox, b[2] + oy, b[4] + oz, b[1] + ox, b[3] + oy, b[5] + oz]
        cs((M.CS_X0, M.CS_X1, M.CS_Y0, M.CS_Y1, "-tray_h", "0 mm"), "TRAY")
        cs(("-(cs_w / 2 - tray_t - felt_c)", "(cs_w / 2 - tray_t - felt_c)", "(%s + tray_t + felt_c)" % M.CS_Y0,
            "(%s - tray_t - felt_c)" % M.CS_Y1, M.FELT_Z0, M.FELT_Z1), "FELT 9")
        for n, b in M.rib_boxes():
            cs(b, n)
        for key, bay, b, _n in M.fill_strips():
            cs(b, "FILL BAY %d" % bay)
        for n, b in M.clip_boxes() + M.catch_boxes():
            cs(b, n)
    return out


def actual(design):
    """Same keys, from the bodies in the root context."""
    root = design.rootComponent
    out = {}
    for occ in root.allOccurrences:
        c = occ.component
        path = occ.fullPathName
        for b in occ.bRepBodies:
            box = bb_mm(b)
            pn = c.partNumber
            half = "C1" if (box[0] + box[3]) / 2 < 0 else "C2"
            if pn in MEMBER_PNS and pn != CROSS_PN:
                # "C1 SIDE MEMBER" and so on, keyed by the half the body sits in: the side member and cross member 1
                # are one part each for both frames (M.TURNED), their bodies named without a half ("SIDE MEMBER")
                nm = b.name.split(" ", 1)
                out["%s %s" % (half, nm[1] if nm[0] in ("C1", "C2") and len(nm) > 1 else b.name)] = box
            elif pn == CROSS_PN:
                out.setdefault("%s|%s" % (pn, half), []).append(box)
            elif pn in ("411301", "411302"):
                out["SKIN %s" % ("C1" if pn == "411301" else "C2")] = box
            elif pn == "513101":
                out["%s TRAY" % half] = box
            elif pn == "513201":
                out["%s FELT 9" % half] = box
            else:
                out.setdefault(("%s|%s" % (pn, half)), []).append(box)
    return out


def match_many(exp, act_list, keys):
    """Pair repeated parts (ribs, fills, plates, clips, catches) with expected boxes by nearest fit."""
    worst, bad = 0.0, []
    remaining = list(act_list)
    for k in keys:
        if not remaining:
            bad.append((k, "missing"))
            continue
        best = min(remaining, key=lambda a: max(abs(p - q) for p, q in zip(a, exp[k])))
        d = max(abs(p - q) for p, q in zip(best, exp[k]))
        remaining.remove(best)
        worst = max(worst, d)
        if d > TOL:
            bad.append((k, round(d, 3)))
    return worst, bad


def check(design):
    exp, act = expected(design), actual(design)
    worst, bad = 0.0, []
    shared = {"%s CROSS MEMBER %d" % (h, k) for h in ("C1", "C2") for k in (2, 3)}
    single = [k for k in exp if (" MEMBER" in k and k not in shared) or k.startswith("SKIN") or k.endswith(("TRAY", "FELT 9"))]
    for half in ("C1", "C2"):                       # the common cross member's copies, by nearest fit
        keys = ["%s CROSS MEMBER %d" % (half, k) for k in (2, 3)]
        w, b = match_many(exp, act.get("%s|%s" % (CROSS_PN, half), []), keys)
        worst = max(worst, w)
        bad += b
    for k in single:
        if k not in act:
            bad.append((k, "missing"))
            continue
        d = max(abs(p - q) for p, q in zip(act[k], exp[k]))
        worst = max(worst, d)
        if d > TOL:
            bad.append((k, round(d, 3)))
    groups = {"513102": "RIB", "513301": "FILL BAY", "513302": "FILL BAY", "513303": "FILL BAY",
              "518001": "CLIP", "518002": "CATCH", "831007": "MITRE", "831008": "MITRE"}
    for half in ("C1", "C2"):
        for prefix in ("RIB", "FILL BAY", "CLIP", "CATCH", "MITRE"):
            keys = [k for k in exp if k.startswith("%s %s" % (half, prefix))]
            acts = []
            for pn, pre in groups.items():
                if pre == prefix:
                    acts += act.get("%s|%s" % (pn, half), [])
            w, b = match_many(exp, acts, keys)
            worst = max(worst, w)
            bad += b
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    return {"checked": len(exp), "worst": round(worst, 3), "bad": bad, "unhealthy": unhealthy}


def param_values(design):
    """{name: value} in mm (or plain numbers) from the design's user parameters."""
    out = {}
    for i in range(design.userParameters.count):
        p = design.userParameters.item(i)
        out[p.name] = p.value * 10.0 if p.unit == "mm" else p.value
    return out


def hole_check(design, tol=TOL):
    """Every site-joint hole of both frames where ceiling_model.hole_positions puts it for the
    design's current values (joints register 2.9): a cylindrical face of the right diameter
    whose axis passes through the expected centre, in the right frame. The slot is matched by
    its two end arcs. No other cylindrical faces are allowed on a frame."""
    vals = param_values(design)
    root = design.rootComponent
    cyl = {"C1": [], "C2": []}
    for occ in root.allOccurrences:
        pn = occ.component.partNumber
        if pn not in MEMBER_PNS:
            continue
        for b in occ.bRepBodies:
            half = "C1" if (b.boundingBox.minPoint.x + b.boundingBox.maxPoint.x) < 0 else "C2"
            for f in b.faces:
                g = f.geometry
                if g.objectType != adsk.core.Cylinder.classType():
                    continue
                cyl[half].append((g.radius * 20.0, [g.origin.x * 10, g.origin.y * 10, g.origin.z * 10],
                                  [g.axis.x, g.axis.y, g.axis.z], b.name))
    worst, bad, checked = 0.0, [], 0
    for half in ("C1", "C2"):
        want = []
        for name, d, xyz in M.hole_positions(vals, half):
            if name == "BACK SPIGOT SLOT":
                run = (vals["spig_slot"] - vals["spig_hole"]) / 2
                want += [(name + " END 1", d, (xyz[0] - run, xyz[1], xyz[2])), (name + " END 2", d, (xyz[0] + run, xyz[1], xyz[2]))]
            elif name == "DT PIN SLOT":                 # D-169: its end arcs lie along Z
                run = (vals["dt_slot_l"] - vals["spig_hole"]) / 2
                want += [(name + " END 1", d, (xyz[0], xyz[1], xyz[2] - run)), (name + " END 2", d, (xyz[0], xyz[1], xyz[2] + run))]
            else:
                want.append((name, d, xyz))
        left = list(cyl[half])
        for name, d, xyz in want:
            checked += 1
            best, dist = None, None
            for c in left:
                if abs(c[0] - d) > tol:
                    continue
                o, a = c[1], c[2]
                v = [xyz[i] - o[i] for i in range(3)]
                t = sum(v[i] * a[i] for i in range(3))
                off = sum((v[i] - t * a[i]) ** 2 for i in range(3)) ** 0.5
                if dist is None or off < dist:
                    best, dist = c, off
            if best is None or dist > tol:
                bad.append(("%s %s at %s" % (half, name, tuple(round(c, 2) for c in xyz)), "missing" if best is None else round(dist, 3)))
                continue
            worst = max(worst, dist)
            left.remove(best)
        for c in left:
            bad.append(("%s extra cylinder D%.2f on %s" % (half, c[0], c[3]), "extra"))
    return {"checked": checked, "worst": round(worst, 3), "bad": bad}
