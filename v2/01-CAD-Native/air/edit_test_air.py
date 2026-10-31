"""Edit test for AIR (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/edit_test_air.py --label "CEILING Engineer (AIR)"

Opens 610000_P01_AIR_CAD.f3d as a new document and changes skeleton parameters (pod_w +100,
wall_depth +25, dt_zb 2120 -> 2100: the soffit underside) and AIR's own (the column's left
face col_x0 949 -> 940, the hub height hub_z 1200 -> 1250). After each change it checks every
layout body against the box the layout gives for the new values, then reverts, checks again
and closes the copy without saving. Prints a Markdown record.
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
import air_model as A  # noqa: E402
importlib.reload(A)
import air_checks as K  # noqa: E402
importlib.reload(K)

F3D_REL = "v2/01-CAD-Native/air/610000_%s_AIR_CAD.f3d" % A.REV
EDITS = [[("pod_w", "2600 mm")], [("wall_depth", "1520 mm")], [("dt_zb", "2100 mm")],
         [("col_x0", "940 mm")], [("hub_z", "1250 mm")]]


def run(_context):
    app = adsk.core.Application.get()
    doc = app.importManager.importToNewDocument(
        app.importManager.createFusionArchiveImportOptions(os.path.join(ARGS["repo_root"], F3D_REL)))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    lines = ["| Step | Change | Bodies checked | Worst deviation (mm) | Off | Unhealthy timeline items |",
             "|---|---|---|---|---|---|"]
    failed = False
    try:
        r = K.check(design, adsk.fusion)
        lines.append("| before | none | %d | %s | %s | %d |" % (r["checked"], r["worst"], r["bad"] or "none", len(r["unhealthy"])))
        failed |= bool(r["bad"] or r["unhealthy"])
        params = design.userParameters
        for edit in EDITS:
            old = [(n, params.itemByName(n).expression) for n, _v in edit]
            for n, v in edit:
                params.itemByName(n).expression = v
            adsk.doEvents()
            r = K.check(design, adsk.fusion)
            desc = ", ".join("%s %s -> %s" % (n, o, v) for (n, o), (_n, v) in zip(old, edit))
            lines.append("| edit | %s | %d | %s | %s | %d |" % (desc, r["checked"], r["worst"], r["bad"] or "none",
                                                              len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
            for n, o in old:
                params.itemByName(n).expression = o
            adsk.doEvents()
            r = K.check(design, adsk.fusion)
            lines.append("| revert | %s back | %d | %s | %s | %d |" % (", ".join(n for n, _o in old), r["checked"],
                                                                       r["worst"], r["bad"] or "none", len(r["unhealthy"])))
            failed |= bool(r["bad"] or r["unhealthy"])
    finally:
        doc.close(False)
    print("\n".join(lines))
    print("EDIT TEST:", "FAIL" if failed else "PASS")
    if failed:
        raise RuntimeError("edit test failed")
