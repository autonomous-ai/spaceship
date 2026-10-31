"""Edit test for INTERIOR (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/edit_test_interior.py \\
        --label "CEILING Engineer (INTERIOR)" --timeout 1200

Opens 810000_P01_INTERIOR_CAD.f3d as a new document and changes skeleton parameters (pod_w
+100, wall_depth +25), the soffit depth (cs_front 360 -> 330: where the side runs start) and
INTERIOR's own (the shelf height sh_z0 2230 -> 2220, the ledge height lg_z 1067 -> 1000).
After each change it checks every body against the box the layout gives for the new values,
then reverts, checks again, and closes the copy without saving. Prints a Markdown record.
"""

import importlib
import os
import sys

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
for d in (HERE, os.path.join(HERE, "..", "ceiling")):
    if d not in sys.path:
        sys.path.insert(0, d)
import interior_model as I  # noqa: E402
importlib.reload(I)

F3D_REL = "v2/01-CAD-Native/interior/810000_%s_INTERIOR_CAD.f3d" % I.REV
EDITS = [[("pod_w", "2600 mm")], [("wall_depth", "1520 mm")], [("cs_front", "330 mm")],
         [("sh_z0", "2220 mm")], [("lg_z", "1000 mm")]]
TOL = 0.05


def values(design):
    out = {}
    for i in range(design.userParameters.count):
        p = design.userParameters.item(i)
        out[p.name] = p.value * 10.0 if p.unit == "mm" else p.value
    return out


def check(design):
    want = I.boxes(values(design))
    got = {}
    for occ in design.rootComponent.allOccurrences:
        for b in occ.bRepBodies:
            bb = b.boundingBox
            got[b.name] = [bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.y * 10,
                           bb.minPoint.z * 10, bb.maxPoint.z * 10]
    worst, bad = 0.0, []
    for name, (_k, b) in want.items():
        if name not in got:
            bad.append((name, "missing"))
            continue
        d = max(abs(p - q) for p, q in zip(got[name], b))
        worst = max(worst, d)
        if d > TOL:
            bad.append((name, round(d, 3)))
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    return {"checked": len(want), "worst": round(worst, 3), "bad": bad, "unhealthy": unhealthy}


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
