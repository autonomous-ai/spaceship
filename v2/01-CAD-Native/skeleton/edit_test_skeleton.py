"""Edit test for the pod skeleton (guideline section 4.4), on a COPY.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/edit_test_skeleton.py

Opens the exported .f3d as a new document, sets pod_w +100 mm and pod_h
+50 mm, rebuilds, and checks that every envelope matches the box its own
parameter expressions give (so every envelope follows), with a healthy
timeline. Then reverts, checks again, and closes the copy without saving.
Prints a Markdown record.
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
F3D_REL = "v2/01-CAD-Native/skeleton/100000_P03_POD-SKELETON_CAD.f3d"
EDITS = [("pod_w", "2600 mm", "2500 mm"), ("pod_h", "2450 mm", "2400 mm")]
TOL = 0.05   # mm


def skeleton_envelopes():
    ns = {"SCRIPT_ARGS": {}, "__name__": "skeleton"}
    path = "%s/v2/01-CAD-Native/skeleton/pod_skeleton.py" % ARGS["repo_root"]
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), ns)
    return ns["ENVELOPES"], ns.get("FACET_ANCHORS", [])


def bodies(design):
    out = {}
    for c in design.allComponents:
        for b in c.bRepBodies:
            out[b.name.replace(" ENVELOPE", "")] = b
    return out


def check(design, envs, anchors=()):
    um = design.unitsManager
    got = bodies(design)
    worst, bad = 0.0, []
    for _a, code, _n, _s, x, y, z in envs:
        want = [um.evaluateExpression(e, "mm") * 10.0 for e in (x[0], y[0], z[0], x[1], y[1], z[1])]
        bb = got[code].boundingBox
        have = [v * 10.0 for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                   bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]
        d = max(abs(a - b) for a, b in zip(want, have))
        worst = max(worst, d)
        if d > TOL:
            bad.append((code, round(d, 3)))
    for code, k, expr in anchors:            # faceted bodies: their anchors follow
        body = got.get(code) or got.get(code + " FACETED") or got.get(code + " GLASS")
        bb = body.boundingBox
        have = [v * 10.0 for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                   bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)][k]
        d = abs(have - um.evaluateExpression(expr, "mm") * 10.0)
        worst = max(worst, d)
        if d > TOL:
            bad.append((code, round(d, 3)))
    tl = design.timeline
    unhealthy = sum(1 for i in range(tl.count)
                    if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState)
    box = design.rootComponent.boundingBox
    size = [round((box.maxPoint.x - box.minPoint.x) * 10), round((box.maxPoint.y - box.minPoint.y) * 10),
            round((box.maxPoint.z - box.minPoint.z) * 10)]
    return {"worst": round(worst, 3), "bad": bad, "unhealthy": unhealthy, "size": size}


def run(_context):
    app = adsk.core.Application.get()
    envs, anchors = skeleton_envelopes()
    src = app.activeDocument
    doc = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(
        "%s/%s" % (ARGS["repo_root"], F3D_REL)))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    try:
        before = check(design, envs, anchors)
        for name, new, _old in EDITS:
            design.userParameters.itemByName(name).expression = new
        adsk.doEvents()
        after = check(design, envs, anchors)
        for name, _new, old in EDITS:
            design.userParameters.itemByName(name).expression = old
        adsk.doEvents()
        back = check(design, envs, anchors)
    finally:
        doc.close(False)
        if src and src.isValid:
            src.activate()
    ok = all(not r["bad"] and not r["unhealthy"] for r in (before, after, back)) and \
        back["size"] == before["size"]
    print("## Skeleton edit test record\n")
    print("Copy of `%s`, opened as a new unsaved document and closed without saving.\n" % F3D_REL)
    print("| State | pod size X x Y x Z (mm) | Unhealthy items | Envelopes off their expressions | Worst (mm) |")
    print("|---|---|---|---|---|")
    for label, r in (("Before", before), ("pod_w 2600, pod_h 2450", after), ("Reverted", back)):
        print("| %s | %s | %d | %s | %g |" % (label, " x ".join(map(str, r["size"])), r["unhealthy"],
                                              r["bad"] or "none (all %d envelopes and %d faceted anchors follow)" % (len(envs), len(anchors)), r["worst"]))
    print("\n**RESULT: %s**" % ("PASS (CAD check on a copy)" if ok else "FAIL"))
    if not ok:
        raise RuntimeError("edit test failed")
