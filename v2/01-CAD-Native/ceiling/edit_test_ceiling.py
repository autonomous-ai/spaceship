"""Edit test for the ceiling (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py \
        --label "CEILING Engineer"

Opens 410000_P01_CEILING_CAD.f3d as a new document and changes skeleton
parameters (pod_w +100, wall_depth +25), the soffit depth (cs_front 360 ->
330, D-60) and the joint rule (bolt_edge_inset 220 -> 250; 5 bolts on the side
and back edges instead of 4). After each change it rebuilds and checks every
body against the box the layout gives for the new values (frame members, both
skins, and in both cassettes the tray, felt, ribs, fill strips, clips and
catches) and every joint hole against the register's rule for the new values.
Then it reverts, checks again, and closes the copy without saving.
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
import ceiling_checks as C  # noqa: E402
importlib.reload(C)

F3D_REL = "v2/01-CAD-Native/ceiling/410000_%s_CEILING_CAD.f3d" % M.REV
EDITS = [
    [("pod_w", "2600 mm")],
    [("wall_depth", "1520 mm")],
    [("cs_front", "330 mm")],
    [("bolt_edge_inset", "250 mm")],
    [("n_ceil_side_bolt", "5"), ("cj_back_n", "5")],
]


def check(design):
    r = C.check(design)
    h = C.hole_check(design)
    r["holes"], r["holes_worst"] = h["checked"], h["worst"]
    r["bad"] = r["bad"] + h["bad"]
    r["worst"] = max(r["worst"], h["worst"])
    return r


def run(_context):
    app = adsk.core.Application.get()
    path = os.path.join(ARGS["repo_root"], F3D_REL)
    doc = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(path))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    lines = ["| Step | Change | Bodies checked | Joint holes checked | Worst deviation (mm) | Off | Unhealthy timeline items |",
             "|---|---|---|---|---|---|---|"]
    failed = False
    try:
        r = check(design)
        lines.append("| before | none | %d | %d | %s | %s | %d |" % (r["checked"], r["holes"], r["worst"], r["bad"] or "none",
                                                            len(r["unhealthy"])))
        failed |= bool(r["bad"] or r["unhealthy"])
        params = design.userParameters
        pick = ARGS.get("edits")         # e.g. "0,1,2": a part of the list, so each run stays short
        todo = [EDITS[int(i)] for i in pick.split(",")] if pick else EDITS
        for edit in todo:
            old = [(n, params.itemByName(n).expression) for n, _v in edit]
            for n, v in edit:
                params.itemByName(n).expression = v
            adsk.doEvents()
            r = check(design)
            desc = ", ".join("%s %s -> %s" % (n, o, v) for (n, o), (_n, v) in zip(old, edit))
            lines.append("| edit | %s | %d | %d | %s | %s | %d |" % (desc, r["checked"], r["holes"], r["worst"],
                                                                   r["bad"] or "none", len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
            if r["unhealthy"]:
                lines.append("|  | unhealthy: %s |  |  |  |  |  |" % ", ".join(r["unhealthy"][:8]))
            for n, o in old:
                params.itemByName(n).expression = o
            adsk.doEvents()
            r = check(design)
            lines.append("| revert | %s back | %d | %d | %s | %s | %d |" % (", ".join(n for n, _o in old), r["checked"],
                                                                            r["holes"], r["worst"], r["bad"] or "none",
                                                                            len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
    finally:
        doc.close(False)
    print("\n".join(lines))
    print("EDIT TEST:", "FAIL" if failed else "PASS")
    if failed:
        raise RuntimeError("edit test failed")
