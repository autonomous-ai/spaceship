"""Re-read the ceiling STEP in Fusion and check its box and body count (tools/fusion/README).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/step_reimport_check.py \
        --label "CEILING Engineer"

`step_check.py` reads the declared unit and the header, but its box treats every
component as if it sat at the origin; this design places its common parts by
assembly transforms, so the box is checked here, after Fusion composes them.
Opens the STEP as a new document and closes it without saving.
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

STEP_REL = "v2/03-Manufacturing/ceiling/410000_%s_CEILING_STEP.step" % M.REV
TOL = 0.05


def run(_context):
    app = adsk.core.Application.get()
    v = M.evaluate(M.all_params())
    xs = [M.ev(v, e) for half in ("C1", "C2") for _c, _n, _a, b in M.frame_members(half) for e in b[:2]]
    want = [min(xs), M.ev(v, M.YW), M.ev(v, M.CASSETTE_CS["C1"][2]) - v["tray_h"], max(xs), M.ev(v, M.YB), v["pod_h"]]
    path = os.path.join(ARGS["repo_root"], STEP_REL)
    doc = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(path))
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
        print("STEP BOX:", "MATCH" if d <= TOL else "MISMATCH")
        if d > TOL:
            raise RuntimeError("STEP box mismatch")
    finally:
        doc.close(False)
