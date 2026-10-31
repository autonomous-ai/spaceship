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
# Fusion keeps modules loaded between runs, and a run from another worktree may have loaded its
# own copy of these (an AIR run loads the ceiling model too): drop any copy from another folder
# and put this folder first, so the imports below take this folder's files
for _n in ("ceiling_model", "ceiling_checks", "ceiling_build"):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != HERE:
        del sys.modules[_n]
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)
import ceiling_model as M  # noqa: E402
importlib.reload(M)
import ceiling_checks as C  # noqa: E402
importlib.reload(C)
import ceiling_build as CB  # noqa: E402
importlib.reload(CB)


def sync_params(design):
    """Reference update from ceiling_model.py: set every user parameter whose expression or
    status and source changed since the build (a parameter-only change needs no rebuild; the
    timeline recomputes). Returns the names changed."""
    changed = []
    ups = design.userParameters
    for name, expr, unit, status, src in M.all_params():
        comment = "%s: %s" % (status.upper(), src)
        p = ups.itemByName(name)
        if p is None:
            ups.add(name, adsk.core.ValueInput.createByString(expr), unit, comment)
            changed.append(name)
            continue
        if "".join(p.expression.split()) != "".join(expr.split()):     # Fusion writes "( a - b )" for "(a - b)"
            p.expression = expr
            changed.append(name)
        if p.comment != comment:
            try:
                p.comment = comment
            except Exception:       # noqa: BLE001 (a comment Fusion won't take is not a geometry change)
                pass
    adsk.doEvents()
    return changed


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc.name.split(" v")[0] != CB.DOC_NAME:
        raise RuntimeError("active document is %r, not %s (use the runner's --doc)" % (doc.name, CB.DOC_NAME))
    if doc.isModified:
        raise RuntimeError("%s has unsaved changes: the report reads saved versions only (PM rule 2026-11-01)" % doc.name)
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    root = design.rootComponent
    print("document %s, version %s" % (doc.name, doc.dataFile.versionNumber if doc.dataFile else "unsaved"))
    changed = sync_params(design)
    print("parameter sync from ceiling_model.py: %s" % (", ".join(changed) or "no change"))
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
    if ARGS.get("save") == "1" or changed:
        # a parameter sync is a design change: save it before exporting (PM ruling 2026-11-01,
        # 19.1 mm cable holes), so the exports and the cloud version agree
        print("saved:", doc.save("CEILING %s build (checked by ceiling_report.py), skeleton %s" % (M.REV, M.SKELETON_REV)))
        adsk.doEvents()
    if ARGS.get("export") == "1":
        CB.ARGS = ARGS
        CB.export_all(design, tray)
    print("CEILING REPORT: PASS")
