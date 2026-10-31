"""Edit test for the ceiling (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/edit_test_ceiling.py \
        --label "CEILING Engineer"

Opens 410000_P01_CEILING_CAD.f3d as a new document and changes skeleton
parameters (pod_w +100, wall_depth +25) and the soffit depth (cs_front 360 ->
330, D-60). After each change it rebuilds and checks every body against the
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
import ceiling_checks as C  # noqa: E402
importlib.reload(C)
check = C.check

F3D_REL = "v2/01-CAD-Native/ceiling/410000_%s_CEILING_CAD.f3d" % M.REV
EDITS = [
    [("pod_w", "2600 mm")],
    [("wall_depth", "1520 mm")],
    [("cs_front", "330 mm")],
]

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
