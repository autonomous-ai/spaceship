"""Edit test (guideline 4.4) on a copy of the exported 710000_P01_ELECTRICAL_CAD.f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/edit_test_electrical.py \
        --label "ELECTRICAL Engineer"

Opens the repo's .f3d as a new, unsaved document, then for each edit below:
changes the parameters, rebuilds, checks the timeline is healthy and every
body sits where the offline model (electrical_model.py, with the same edit)
says, to 0.01 mm; then puts the values back and checks every body returned
to its design position. Closes the copy without saving. Writes nothing.
"""

import importlib
import os
import sys

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(ARGS.get("script_path", globals().get("__file__", "."))))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import electrical_model as M  # noqa: E402

importlib.reload(M)

F3D_REL = "v2/01-CAD-Native/electrical/%s.f3d" % M.DOC_NAME
TOL = 0.01

# Each edit: a name and {parameter: new expression}. One moves the power unit
# (the socket height the PM set), one the trunk, one a skeleton size the
# routes follow, and one a pocket and grommet size.
EDITS = [
    ("power unit up 100 mm", {"pu_zc": "1100 mm"}),
    ("trunk up 50 mm", {"trunk_z": "1150 mm"}),
    ("pod 20 mm deeper (skeleton pod_d)", {"pod_d": "1720 mm"}),
    ("bigger pockets and grommets", {"pk_l": "180 mm", "grm_d": "22 mm"}),
]


def box(body: "adsk.fusion.BRepBody"):
    b = body.boundingBox
    return [v * 10.0 for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z, b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def bodies_by_code(design: "adsk.fusion.Design"):
    out = {}
    for comp in design.allComponents:
        for i in range(comp.bRepBodies.count):
            b = comp.bRepBodies.item(i)
            out[b.name.split(" ")[0]] = b
    return out


def check(design: "adsk.fusion.Design", overrides, label):
    adsk.doEvents()
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    live = {}
    for name in M.SKELETON_PARAMS:
        live[name] = design.userParameters.itemByName(name).value * 10.0
    v = M.values(live)
    for name, expr in overrides.items():   # the model's own parameters follow the edit too
        if name not in M.SKELETON_PARAMS:
            v[name] = M.evaluate(expr, v)
    for name, expr, _u, _s, _src in M.PARAMS:   # re-evaluate the dependants in order
        if name not in overrides:
            v[name] = M.evaluate(expr, v)
    got = bodies_by_code(design)
    worst, off = 0.0, []
    for b in M.BODIES:
        want = M.body_box(b, v)
        have = box(got[b["code"]])
        d = max(abs(a - w) for a, w in zip(have, want))
        worst = max(worst, d)
        if d > TOL:
            off.append((b["code"], round(d, 3)))
    print("%s: timeline unhealthy %d, worst body offset %.4f mm, off %s" % (label, len(bad), worst, off))
    return not bad and not off


def run(_context):
    app = adsk.core.Application.get()
    path = os.path.join(ARGS["repo_root"], F3D_REL)
    copy = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(path))
    ok = True
    try:
        design = adsk.fusion.Design.cast(copy.products.itemByProductType("DesignProductType"))
        # an imported copy's root takes the new document's number, so check the components instead
        pns = {c.partNumber for c in design.allComponents}
        want = {pn for _k, pn, _n, _vn, _kind in M.COMPONENTS}
        if not want <= pns:
            raise RuntimeError("the copy is not 710000 ELECTRICAL: components %s missing" % sorted(want - pns))
        print("copy: root %r, the %d ELECTRICAL components found" % (design.rootComponent.partNumber, len(want)))
        ok &= check(design, {}, "as exported")
        for label, edits in EDITS:
            before = {n: design.userParameters.itemByName(n).expression for n in edits}
            for n, e in edits.items():
                design.userParameters.itemByName(n).expression = e
            ok &= check(design, edits, "edit '%s' %s" % (label, edits))
            for n, e in before.items():
                design.userParameters.itemByName(n).expression = e
            ok &= check(design, {}, "reverted '%s'" % label)
    finally:
        copy.close(False)
    print("EDIT TEST:", "PASS" if ok else "FAIL")
    if not ok:
        raise RuntimeError("edit test failed")
