"""Edit test for a FRONT sub-assembly (engineering guideline section 4.4).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/edit_test_front.py \
        --arg anchors=v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_ANCHORS.json \
        --arg edits="pod_w=2600 mm;fr_dz=12 mm;door_xbr=1474 mm"

Opens the exported .f3d named in the anchors file as a NEW, unsaved copy,
checks every anchor (a component's bounding-box side against its parameter
expression), changes the skeleton parameters given in `edits`, checks again,
puts the values back, checks a third time, and closes the copy without
saving. The saved design is never touched. Prints a markdown table and
RESULT: PASS or FAIL (FAIL raises, so the runner exits 1).
"""

import json
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
TOL = 0.05   # mm


def comp_box(comp):
    b = comp.boundingBox
    return [v * 10.0 for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z, b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def check(design, anchors):
    um = design.unitsManager
    worst, off = 0.0, []
    by_name = {c.name: c for c in design.allComponents}
    for a in anchors:
        comp = by_name.get(a["component"])
        if comp is None:
            raise RuntimeError("component not found: " + a["component"])
        got = comp_box(comp)[a["index"]]
        want = um.evaluateExpression(a["expression"], "mm") * 10.0
        d = abs(got - want)
        worst = max(worst, d)
        if d > TOL:
            off.append("%s[%d] %.2f vs %s = %.2f" % (a["component"], a["index"], got, a["expression"], want))
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    root = comp_box(design.rootComponent)
    return {"box": " x ".join("%.1f" % (root[k + 3] - root[k]) for k in range(3)), "bad": bad, "loose": loose,
            "off": off, "worst": worst}


def run(_context):
    test(adsk.core.Application.get(), ARGS["repo_root"], ARGS["anchors"], ARGS["edits"])


def test(app, root_dir, anchors_rel, edits_text):
    """The edit test on a copy of the f3d named in the anchors file; also called by the build scripts' "post" step."""
    spec = json.load(open(os.path.join(root_dir, anchors_rel), encoding="utf-8"))
    edits = [e.split("=", 1) for e in edits_text.split(";") if e.strip()]
    im = app.importManager
    doc = im.importToNewDocument(im.createFusionArchiveImportOptions(os.path.join(root_dir, spec["f3d"])))
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        ups = design.userParameters
        old = {}
        for name, expr in edits:
            p = ups.itemByName(name.strip())
            if p is None:
                raise RuntimeError("no parameter " + name)
            old[name.strip()] = p.expression
        rows = [("Before", check(design, spec["anchors"]))]
        for name, expr in edits:
            ups.itemByName(name.strip()).expression = expr.strip()
        adsk.doEvents()
        rows.append(("; ".join("%s %s" % (n.strip(), e.strip()) for n, e in edits), check(design, spec["anchors"])))
        for name, expr in old.items():
            ups.itemByName(name).expression = expr
        adsk.doEvents()
        rows.append(("Reverted", check(design, spec["anchors"])))
    finally:
        doc.close(False)
    print("Copy of `%s`, opened as a new unsaved document and closed without saving; %d anchors." % (
        spec["f3d"], len(spec["anchors"])))
    print("")
    print("| State | Box X x Y x Z (mm) | Unhealthy items | Loose sketches | Anchors off their expressions | Worst (mm) |")
    print("|---|---|---|---|---|---|")
    ok = True
    for state, r in rows:
        print("| %s | %s | %d | %d | %s | %.3f |" % (state, r["box"], len(r["bad"]), len(r["loose"]),
                                                    "; ".join(r["off"]) or "none", r["worst"]))
        ok = ok and not (r["bad"] or r["loose"] or r["off"])
    ok = ok and rows[0][1]["box"] == rows[2][1]["box"]
    print("")
    print("RESULT: %s (CAD check on a copy)" % ("PASS" if ok else "FAIL"))
    if not ok:
        raise RuntimeError("edit test failed")
