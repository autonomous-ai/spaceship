"""Re-read the AIR STEP in Fusion and check its box and body count: step_check.py's box treats
every component as if it sat at the origin, and the fans are placed by assembly transforms.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/step_reimport_check_air.py --label "CEILING Engineer (AIR)"
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

STEP_REL = "v2/03-Manufacturing/air/610000_%s_AIR_STEP.step" % A.REV


def run(_context):
    app = adsk.core.Application.get()
    want = K.union_box()
    doc = app.importManager.importToNewDocument(
        app.importManager.createSTEPImportOptions(os.path.join(ARGS["repo_root"], STEP_REL)))
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        root = design.rootComponent
        n = sum(o.bRepBodies.count for o in root.allOccurrences) + root.bRepBodies.count
        bb = root.boundingBox
        got = [bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.x * 10, bb.maxPoint.y * 10,
               bb.maxPoint.z * 10]
        d = max(abs(a - b) for a, b in zip(got, want))
        print("STEP re-read in Fusion: %d bodies, box %s, expected %s, largest difference %.3f mm" % (
            n, [round(x, 2) for x in got], [round(x, 2) for x in want], d))
        print("STEP BOX:", "MATCH" if d <= 0.05 else "MISMATCH")
        if d > 0.05:
            raise RuntimeError("STEP box mismatch")
    finally:
        doc.close(False)
