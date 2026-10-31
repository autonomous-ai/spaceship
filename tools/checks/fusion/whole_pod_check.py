"""Whole-pod mechanical check inside Fusion. Run it ONLY through the locked
runner (PM rule), via tools/checks/run_fusion_checks.py:

  python3 tools/fusion/run_script.py tools/checks/fusion/whole_pod_check.py \
      --arg steps=/abs/a.step,/abs/b.step --arg out=/abs/result.json \
      --arg rules=/abs/gap-rules.csv --arg allow=/abs/clash-allow.csv --arg tools=/abs/tools.csv

What it does, in its own new document (never saved, closed at the end):
1. Imports the STEP files (assembly STEPs in pod coordinates).
2. C01: every pair of bodies whose boxes overlap is intersected; an overlap
   over `min_mm3` (default 0.1 mm3) that isn't on the allow-list is a clash.
3. C02: the gap rules (min and max gaps between named bodies), measured as
   true minimum distances.
4. C07: for every bolt or screw, the materials along its axis (sampled on a
   ring just outside the shank): grip, engagement in the nut, rivnut or
   tapped part, and whether the tip hits anything beyond it (too long).
5. C03: a tool envelope (cylinder along the bolt axis, out from the head)
   must miss every body that is in place when the bolt is tightened (all
   bodies except those the tools file marks as fitted later).
6. C10: pairs of bodies that touch (minimum distance 0), for the mixed-metal
   check.
The results are written as JSON to `out`; nothing in the repo is changed.
"""

import csv
import json
import math
import re
import time
import traceback

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
CM = 10.0          # Fusion internal cm -> mm

FASTENER_RE = re.compile(r"\b(BOLT|SCREW)\b|\b83\d{4}\b", re.I)
NUT_RE = re.compile(r"\b(NUT|RIVNUT|RIVET NUT|INSERT|CLINCH)\b", re.I)


def _csv(path):
    if not path:
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _f(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def bbox_mm(b):
    bb = b.boundingBox
    return (bb.minPoint.x * CM, bb.minPoint.y * CM, bb.minPoint.z * CM,
            bb.maxPoint.x * CM, bb.maxPoint.y * CM, bb.maxPoint.z * CM)


def box_gap(a, b):
    return max(max(a[k] - b[k + 3], b[k] - a[k + 3]) for k in range(3))


def label_of(occ, body):
    path = occ.fullPathName if occ else ""
    return (path.replace("+", " / ") + " / " if path else "") + body.name


def collect_bodies(root):
    out = []
    for b in root.bRepBodies:
        out.append((label_of(None, b), b))
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out.append((label_of(occ, b), b))
    return out


def import_steps(app, root, paths):
    im = app.importManager
    done = []
    for p in paths:
        opts = im.createSTEPImportOptions(p)
        ok = im.importToTarget(opts, root)
        done.append({"file": p, "ok": bool(ok)})
        adsk.doEvents()
    return done


def clash_pairs(bodies, allow, min_mm3):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    boxes = [bbox_mm(b) for _l, b in bodies]
    rules = [(re.compile(r["a"], re.I), re.compile(r["b"], re.I), _f(r.get("max_mm3"), 0.0), r) for r in allow]
    out = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            if box_gap(boxes[i], boxes[j]) >= 0:
                continue
            la, ba = bodies[i]
            lb, bb = bodies[j]
            t1 = tbm.copy(ba)
            t2 = tbm.copy(bb)
            if not tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType):
                continue
            vol = (t1.volume if t1 else 0.0) * 1000.0
            if vol <= min_mm3:
                continue
            allowed = None
            for ra, rb, vmax, r in rules:
                if ((ra.search(la) and rb.search(lb)) or (ra.search(lb) and rb.search(la))) and (vmax <= 0 or vol <= vmax):
                    allowed = r.get("id")
                    break
            out.append({"a": la, "b": lb, "mm3": round(vol, 2), "allowed": allowed})
    return out


def gap_rules(app, bodies, rules):
    mm = app.measureManager
    boxes = {id(b): bbox_mm(b) for _l, b in bodies}
    out = []
    for r in rules:
        ra, rb = re.compile(r["a"], re.I), re.compile(r["b"], re.I)
        A = [(l, b) for l, b in bodies if ra.search(l)]
        B = [(l, b) for l, b in bodies if rb.search(l)]
        worst = None
        for la, ba in A:
            for lb, bb in B:
                if ba is bb or box_gap(boxes[id(ba)], boxes[id(bb)]) > 50.0:
                    continue
                d = mm.measureMinimumDistance(ba, bb).value * CM
                if worst is None or d < worst[0]:
                    worst = (d, la, lb)
        if worst:
            out.append({"id": r["id"], "group": r.get("group", ""), "gap_mm": round(worst[0], 3), "a": worst[1],
                        "b": worst[2], "min_mm": _f(r.get("min_gap_mm")), "max_mm": _f(r.get("max_gap_mm"))})
    return out


def bolt_axis(body):
    """Shank axis of a bolt: the longest cylindrical face; head end is where
    the largest-radius cylinder (or the far extent) sits."""
    best, rmax = None, None
    for f in body.faces:
        g = f.geometry
        if g.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
            continue
        bb = f.boundingBox
        length = bb.minPoint.distanceTo(bb.maxPoint)
        if best is None or length > best[0]:
            best = (length, g)
        if rmax is None or g.radius > rmax.radius:
            rmax = g
    if best is None:
        return None
    g = best[1]
    o = g.origin
    ax = g.axis.copy()
    ax.normalize()
    # extent of the body along the axis
    bb = body.boundingBox
    corners = [adsk.core.Point3D.create(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x)
               for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z)]
    ts = [(c.x - o.x) * ax.x + (c.y - o.y) * ax.y + (c.z - o.z) * ax.z for c in corners]
    t0, t1 = min(ts), max(ts)
    # head: the end nearer the largest-radius cylinder's origin
    if rmax is not None and rmax is not g:
        th = (rmax.origin.x - o.x) * ax.x + (rmax.origin.y - o.y) * ax.y + (rmax.origin.z - o.z) * ax.z
        head_at_t1 = abs(th - t1) < abs(th - t0)
    else:
        head_at_t1 = False
    return {"origin": o, "axis": ax, "t0": t0, "t1": t1, "radius": g.radius, "head_at_t1": head_at_t1}


def _pt(o, ax, t, u=None, r=0.0):
    p = adsk.core.Point3D.create(o.x + ax.x * t, o.y + ax.y * t, o.z + ax.z * t)
    if u is not None:
        p = adsk.core.Point3D.create(p.x + u.x * r, p.y + u.y * r, p.z + u.z * r)
    return p


def _perp(ax):
    ref = adsk.core.Vector3D.create(1, 0, 0) if abs(ax.x) < 0.9 else adsk.core.Vector3D.create(0, 1, 0)
    u = ax.crossProduct(ref)
    u.normalize()
    v = ax.crossProduct(u)
    v.normalize()
    return u, v


def fasteners(app, bodies, tools, later_re, step_mm=0.25, ring_extra_mm=0.6, past_tip_mm=30.0):
    """For each bolt or screw body, walk its axis from the head end to
    past_tip_mm beyond the tip and record:
    - layers: bodies whose material surrounds the shank (sampled on a ring
      just outside it): the clamped parts and the nut, rivnut or insert;
    - on_axis: bodies whose material sits ON the axis, i.e. with no hole for
      the bolt. Inside the bolt's length that is a collision; past the tip it
      is what the tip would hit (its distance is the tip clearance);
    - the tool envelope check (C03)."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    inside = adsk.fusion.PointContainment.PointInsidePointContainment
    boxes = {id(b): bbox_mm(b) for _l, b in bodies}
    tool = tools[0] if tools else {"name": "10 mm hex socket", "diameter_mm": "18", "length_mm": "80"}
    tdia, tlen = _f(tool.get("diameter_mm"), 18.0), _f(tool.get("length_mm"), 80.0)
    out = []
    for lb, bb in bodies:
        if not FASTENER_RE.search(lb) or NUT_RE.search(lb):
            continue
        ax = bolt_axis(bb)
        if ax is None:
            out.append({"bolt": lb, "error": "no cylindrical face"})
            continue
        o, a = ax["origin"], ax["axis"]
        r = ax["radius"] + ring_extra_mm / CM
        u, v = _perp(a)
        nu, nv = u.copy(), v.copy()
        nu.scaleBy(-1)
        nv.scaleBy(-1)
        dirs = [u, v, nu, nv]
        head_t, tip_t = (ax["t1"], ax["t0"]) if ax["head_at_t1"] else (ax["t0"], ax["t1"])
        sgn = 1.0 if tip_t > head_t else -1.0
        length_mm = abs(tip_t - head_t) * CM
        reach = (length_mm + past_tip_mm) / CM
        near = [(l, b) for l, b in bodies if b is not bb and box_gap(boxes[id(b)], boxes[id(bb)]) < past_tip_mm]
        n = int((length_mm + past_tip_mm) / step_mm)
        ring, axis_hits = {}, {}
        for k in range(n + 1):
            t = head_t + sgn * k * step_mm / CM
            pos = round(k * step_mm, 3)
            for l, b in near:
                if b.pointContainment(_pt(o, a, t)) == inside:
                    axis_hits.setdefault(l, []).append(pos)
                if pos <= length_mm + step_mm:
                    cnt = sum(1 for d in dirs if b.pointContainment(_pt(o, a, t, d, r)) == inside)
                    if cnt >= 3:
                        ring.setdefault(l, []).append(pos)
        layers = sorted(({"body": l, "from_head_mm": min(ks), "to_mm": max(ks), "is_nut": bool(NUT_RE.search(l))}
                         for l, ks in ring.items()), key=lambda x: x["from_head_mm"])
        collisions = sorted(({"body": l, "from_head_mm": min(ks), "to_mm": max(ks)}
                             for l, ks in axis_hits.items() if min(ks) <= length_mm), key=lambda x: x["from_head_mm"])
        ahead = sorted((min(ks) - length_mm, l) for l, ks in axis_hits.items() if min(ks) > length_mm)
        tip_clear = {"body": ahead[0][1], "mm": round(ahead[0][0], 2)} if ahead else None
        # tool envelope: from the head outward
        out_dir = a.copy()
        out_dir.scaleBy(-sgn)
        p0 = _pt(o, a, head_t)
        p0s = adsk.core.Point3D.create(p0.x + out_dir.x * 0.05, p0.y + out_dir.y * 0.05, p0.z + out_dir.z * 0.05)
        p1 = adsk.core.Point3D.create(p0.x + out_dir.x * tlen / CM, p0.y + out_dir.y * tlen / CM,
                                      p0.z + out_dir.z * tlen / CM)
        cyl = tbm.createCylinderOrCone(p0s, tdia / 2.0 / CM, p1, tdia / 2.0 / CM)
        blocked = []
        cb = bbox_mm(cyl)
        for l, b in bodies:
            if b is bb or (later_re and later_re.search(l)) or box_gap(boxes[id(b)], cb) >= 0:
                continue
            t1 = tbm.copy(cyl)
            t2 = tbm.copy(b)
            if tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType) and t1 \
                    and t1.volume * 1000.0 > 1.0:
                blocked.append({"body": l, "mm3": round(t1.volume * 1000.0, 1)})
        out.append({"bolt": lb, "length_mm": round(length_mm, 2), "dia_mm": round(ax["radius"] * 2 * CM, 2),
                    "head": [round(p0.x * CM, 1), round(p0.y * CM, 1), round(p0.z * CM, 1)],
                    "axis": [round(a.x, 4), round(a.y, 4), round(a.z, 4)], "layers": layers,
                    "collisions": collisions, "tip_clearance": tip_clear, "tool": tool.get("name"),
                    "tool_blocked_by": blocked})
    return out


def touching(app, bodies, tol_mm=0.05):
    mm = app.measureManager
    boxes = [bbox_mm(b) for _l, b in bodies]
    out = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            if box_gap(boxes[i], boxes[j]) > tol_mm:
                continue
            d = mm.measureMinimumDistance(bodies[i][1], bodies[j][1]).value * CM
            if d <= tol_mm:
                out.append({"a": bodies[i][0], "b": bodies[j][0], "gap_mm": round(d, 3)})
    return out


def run(_context):
    app = adsk.core.Application.get()
    t_start = time.time()
    steps = [p for p in (ARGS.get("steps") or "").split(",") if p]
    result = {"steps": steps, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "errors": []}
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        root.partNumber = "CHECK-WHOLE-POD"
        result["imports"] = import_steps(app, root, steps)
        bodies = collect_bodies(root)
        result["bodies"] = [{"label": l, "box_mm": [round(v, 2) for v in bbox_mm(b)]} for l, b in bodies]
        print("bodies %d from %d STEP files" % (len(bodies), len(steps)))
        min_mm3 = _f(ARGS.get("min_mm3"), 0.1)
        result["clashes"] = clash_pairs(bodies, _csv(ARGS.get("allow")), min_mm3)
        print("clash pairs %d (unlisted %d)" % (len(result["clashes"]),
                                                sum(1 for c in result["clashes"] if not c["allowed"])))
        result["gaps"] = gap_rules(app, bodies, _csv(ARGS.get("rules")))
        tools = _csv(ARGS.get("tools"))
        later = ARGS.get("fitted_later") or r"LINING|CASS"
        result["fasteners"] = fasteners(app, bodies, tools, re.compile(later, re.I) if later else None)
        print("fasteners %d" % len(result["fasteners"]))
        result["touching"] = touching(app, bodies)
    except Exception:            # record, then re-raise so the runner reports a failure
        result["errors"].append(traceback.format_exc())
        raise
    finally:
        result["seconds"] = round(time.time() - t_start, 1)
        if ARGS.get("out"):
            with open(ARGS["out"], "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=1)
        doc.close(False)          # our own document, never saved
