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
            if pn in ("411101", "411102"):
                out[b.name] = box
            elif pn == "411301":
                out["SKIN %s" % half] = box
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
    single = [k for k in exp if " MEMBER" in k or k.startswith("SKIN") or k.endswith(("TRAY", "FELT 9"))]
    for k in single:
        if k not in act:
            bad.append((k, "missing"))
            continue
        d = max(abs(p - q) for p, q in zip(act[k], exp[k]))
        worst = max(worst, d)
        if d > TOL:
            bad.append((k, round(d, 3)))
    groups = {"513102": "RIB", "513301": "FILL BAY", "513302": "FILL BAY", "513303": "FILL BAY",
              "518001": "CLIP", "518002": "CATCH"}
    for half in ("C1", "C2"):
        for prefix in ("RIB", "FILL BAY", "CLIP", "CATCH"):
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
