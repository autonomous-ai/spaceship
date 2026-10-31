"""Edit test for AIR (guideline section 4.4), on a COPY of the exported .f3d.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/edit_test_air.py --label "CEILING Engineer (AIR)"

Opens 610000_P01_AIR_CAD.f3d as a new document and changes skeleton parameters (pod_w +100,
pod_d and wall_depth +25 together, dt_zb 2120 -> 2100: the soffit underside), FRONT's named input (DR's access
panel dr_acc_t 3 -> 4: the column and the soffit start at its face) and AIR's own (the column's
left face col_x0 949 -> 940, the hub height hub_z 1200 -> 1250). After each change it checks
every layout body against the box the layout gives for the new values, then reverts, checks
again and closes the copy without saving. Prints a Markdown record, naming any timeline item
that isn't healthy.
"""

import importlib
import os
import sys

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
_CEIL = os.path.normpath(os.path.join(HERE, "..", "ceiling"))
# Fusion keeps modules loaded between runs, and a run from another worktree may have loaded its
# own copy of these (the ceiling's own runs load the ceiling model too): drop any copy from
# another folder and put this worktree's folders first, so the imports below take its files
for _n, _d in (("air_model", HERE), ("air_checks", HERE), ("ceiling_model", _CEIL), ("ceiling_checks", _CEIL),
               ("ceiling_build", _CEIL), ("ceiling_exports", _CEIL)):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != _d:
        del sys.modules[_n]
for _d in (_CEIL, HERE):
    if _d in sys.path:
        sys.path.remove(_d)
    sys.path.insert(0, _d)
import air_model as A  # noqa: E402
importlib.reload(A)
import air_checks as K  # noqa: E402
importlib.reload(K)

F3D_REL = "v2/01-CAD-Native/air/610000_%s_AIR_CAD.f3d" % A.REV
EDITS = A.EDITS        # one list with the offline check that every cut lands in its body for each


def sick(r):
    """The unhealthy timeline items, by name (up to 4), or 0."""
    u = r["unhealthy"]
    return "0" if not u else "%d: %s" % (len(u), "; ".join(u[:4]))


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
        lines.append("| before | none | %d | %s | %s | %s |" % (r["checked"], r["worst"], r["bad"] or "none", sick(r)))
        failed |= bool(r["bad"] or r["unhealthy"])
        params = design.userParameters
        for edit in EDITS:
            old = [(n, params.itemByName(n).expression) for n, _v in edit]
            for n, v in edit:
                params.itemByName(n).expression = v
            adsk.doEvents()
            r = K.check(design, adsk.fusion)
            desc = ", ".join("%s %s -> %s" % (n, o, v) for (n, o), (_n, v) in zip(old, edit))
            lines.append("| edit | %s | %d | %s | %s | %s |" % (desc, r["checked"], r["worst"], r["bad"] or "none",
                                                              sick(r)))
            failed |= bool(r["bad"] or r["unhealthy"])
            for n, o in old:
                params.itemByName(n).expression = o
            adsk.doEvents()
            r = K.check(design, adsk.fusion)
            lines.append("| revert | %s back | %d | %s | %s | %s |" % (", ".join(n for n, _o in old), r["checked"],
                                                                       r["worst"], r["bad"] or "none", sick(r)))
            failed |= bool(r["bad"] or r["unhealthy"])
    finally:
        doc.close(False)
    print("\n".join(lines))
    print("EDIT TEST:", "FAIL" if failed else "PASS")
    if failed:
        raise RuntimeError("edit test failed")
