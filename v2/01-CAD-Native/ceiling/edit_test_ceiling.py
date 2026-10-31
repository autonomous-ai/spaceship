"""Edit test for the ceiling (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py \
        --label "CEILING Engineer"

Opens 410000_P01_CEILING_CAD.f3d as a new document and changes skeleton
parameters (pod_w +100, wall_depth +25) and the soffit depth (cs_front 0 ->
300, D-60). After each change it rebuilds and checks every body against the
box the layout gives for the new values: frame members, both skins, and in
both cassettes the tray, felt, ribs, fill strips, light plates, clips and
catches. Then it reverts, checks again, and closes the copy without saving.
Prints a Markdown record.
"""

import importlib
import os
import sys

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import ceiling_model as M  # noqa: E402
importlib.reload(M)

F3D_REL = "v2/01-CAD-Native/ceiling/410000_%s_CEILING_CAD.f3d" % M.REV
EDITS = [
    [("pod_w", "2600 mm")],
    [("wall_depth", "1520 mm")],
    [("cs_front", "300 mm")],
]
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
        for i, (x, y) in enumerate(M.light_points()):
            cs(("%s - ring_od / 2" % x, "%s + ring_od / 2" % x, "%s - ring_od / 2" % y, "%s + ring_od / 2" % y,
                M.FELT_Z1, "%s + ring_t" % M.FELT_Z1), "LIGHT PLATE %d" % (i + 1))
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
              "513401": "LIGHT PLATE", "518001": "CLIP", "518002": "CATCH"}
    for half in ("C1", "C2"):
        for prefix in ("RIB", "FILL BAY", "LIGHT PLATE", "CLIP", "CATCH"):
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


def run(_context):
    app = adsk.core.Application.get()
    path = os.path.join(ARGS["repo_root"], F3D_REL)
    doc = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(path))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    lines = ["| Step | Change | Bodies checked | Worst deviation (mm) | Off | Unhealthy timeline items |",
             "|---|---|---|---|---|---|"]
    failed = False
    try:
        r = check(design)
        lines.append("| before | none | %d | %s | %s | %d |" % (r["checked"], r["worst"], r["bad"] or "none", len(r["unhealthy"])))
        failed |= bool(r["bad"] or r["unhealthy"])
        params = design.userParameters
        for edit in EDITS:
            old = [(n, params.itemByName(n).expression) for n, _v in edit]
            for n, v in edit:
                params.itemByName(n).expression = v
            adsk.doEvents()
            r = check(design)
            desc = ", ".join("%s %s -> %s" % (n, o, v) for (n, o), (_n, v) in zip(old, edit))
            lines.append("| edit | %s | %d | %s | %s | %d |" % (desc, r["checked"], r["worst"], r["bad"] or "none",
                                                              len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
            if r["unhealthy"]:
                lines.append("|  | unhealthy: %s |  |  |  |  |" % ", ".join(r["unhealthy"][:8]))
            for n, o in old:
                params.itemByName(n).expression = o
            adsk.doEvents()
            r = check(design)
            lines.append("| revert | %s back | %d | %s | %s | %d |" % (", ".join(n for n, _o in old), r["checked"],
                                                                       r["worst"], r["bad"] or "none", len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
    finally:
        doc.close(False)
    print("\n".join(lines))
    print("EDIT TEST:", "FAIL" if failed else "PASS")
    if failed:
        raise RuntimeError("edit test failed")
