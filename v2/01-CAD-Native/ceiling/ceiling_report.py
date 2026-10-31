"""Checks and exports of the saved ceiling design, without rebuilding it.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_report.py \\
        --doc 410000_P01_CEILING_CAD --label "CEILING Engineer" [--arg save=1] [--arg export=1] --close --discard

The build (ceiling_build.py) and its checks can run past the runner's call limit on a busy
day, so they can be split: the build saves, and this run reports on the saved version with
the same checks and the same log lines (BODY, MASS, FLAT, CLASH) that ceiling_exports.py
reads: timeline health, sketches fully constrained, no clash over 1 mm3, every body where the
layout says, every joint hole where the register says. export=1 also writes the f3d, the
STEP and the tray's flat-pattern DXF.
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
import ceiling_build as CB  # noqa: E402
importlib.reload(CB)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc.name.split(" v")[0] != CB.DOC_NAME:
        raise RuntimeError("active document is %r, not %s (use the runner's --doc)" % (doc.name, CB.DOC_NAME))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    root = design.rootComponent
    print("document %s, version %s" % (doc.name, doc.dataFile.versionNumber if doc.dataFile else "unsaved"))
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [c.name + "/" + s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    bodies = CB.all_bodies(root)
    print("timeline %d items, unhealthy %d, loose sketches %d, parameters %d, bodies %d" % (
        tl.count, len(bad), len(loose), design.userParameters.count, len(bodies)))
    for n, b in bodies:
        print("BODY|%s|%s" % (n, CB.body_box(b)))
    hits = CB.clash_check(bodies)
    print("clash pairs over 1 mm3: %d" % len(hits))
    for h in hits:
        print("CLASH|%s|%s|%s mm3" % h)
    tray = None
    for occ in root.allOccurrences:
        c = occ.component
        if c.bRepBodies.count:
            print("MASS|%s|%s|%.3f kg" % (occ.fullPathName, c.partNumber, c.getPhysicalProperties().mass))
        if c.partNumber == "513101":
            tray = c
    pos = C.check(design)
    print("position check: %d bodies against the layout, worst %.3f mm, off %s" % (
        pos["checked"], pos["worst"], pos["bad"] or "none"))
    holes = C.hole_check(design)
    print("hole check: %d joint holes against the register's positions, worst %.3f mm, off %s" % (
        holes["checked"], holes["worst"], holes["bad"] or "none"))
    if tray is not None:
        CB.make_flat_pattern(tray)
    if bad or loose or hits or pos["bad"] or holes["bad"]:
        raise RuntimeError("ceiling checks failed (unhealthy %s, loose %s, clashes %s, off layout %s, holes %s)" % (
            bad, loose, hits, pos["bad"], holes["bad"]))
    design.activateRootComponent()
    if ARGS.get("save") == "1":
        print("saved:", doc.save("CEILING %s build (checked by ceiling_report.py), skeleton %s" % (M.REV, M.SKELETON_REV)))
        adsk.doEvents()
    if ARGS.get("export") == "1":
        CB.ARGS = ARGS
        CB.export_all(design, tray)
    print("CEILING REPORT: PASS")
