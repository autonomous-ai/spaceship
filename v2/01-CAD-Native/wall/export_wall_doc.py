"""Export the active WALL design: native .f3d and STEP, then re-read the STEP.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/export_wall_doc.py \
        --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --arg pn=210101 --close --discard

Refuses to run unless the active design is saved, unmodified and has the
root part number given by `pn` (so it never exports someone else's document).
Writes, from the document name PARTNO_REV_NAME_CAD:
    v2/01-CAD-Native/wall/PARTNO_REV_NAME_CAD.f3d     (timeline, sketches, parameters)
    v2/03-Manufacturing/wall/PARTNO_REV_NAME_STEP.step (Fusion writes cm, declared in the file; D-13)
Then imports the STEP into a new document, compares its bounding box with the
design's (0.05 mm), and closes that copy without saving.
"""

import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def box(c):
    """Box of the solid bodies only: a derived construction plane (the skeleton link) would stretch the
    component's own box to Z 0, and a STEP carries no planes."""
    bodies = [b for comp in adsk.fusion.Design.cast(c.parentDesign).allComponents for b in comp.bRepBodies] \
        if isinstance(c, adsk.fusion.Component) else []
    if not bodies:
        b = c.boundingBox
        return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                             b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]
    lo = [min(getattr(b.boundingBox.minPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    hi = [max(getattr(b.boundingBox.maxPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    return [round(v, 2) for v in lo + hi]


def export(em, mk, path, root):
    for _try in range(10):          # right after a save Fusion may still be uploading
        if em.execute(mk(path, root)) and os.path.getsize(path) > 1000:
            return True
        adsk.doEvents()
        time.sleep(3)
    return False


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != ARGS.get("pn"):
        raise RuntimeError("active design %r has root part number %r, not %r" % (doc.name, root.partNumber,
                                                                                 ARGS.get("pn")))
    if not doc.isSaved or doc.isModified:
        raise RuntimeError("save the design before exporting (saved=%s, modified=%s)" % (doc.isSaved, doc.isModified))
    # The cloud design keeps its live Derive link to the skeleton. A local .f3d that still holds it can't be
    # opened on its own ("New design cannot be created from a local file containing external references",
    # Fusion 2706.1), so the link is broken in memory for the export only: the .f3d carries the skeleton's
    # values of this saved version. Close the document without saving afterwards (runner --close --discard).
    broken = []
    for c in design.allComponents:
        for d in c.features.deriveFeatures:
            ref = d.documentReference
            src = "%s v%s" % (ref.dataFile.name, ref.version) if ref and ref.dataFile else "?"
            if not d.breakLink():
                raise RuntimeError("could not break the derive link to %s for the export" % src)
            broken.append(src)
    print("derive links broken for the export only (close without saving): %s" % (broken or "none"))
    name = doc.name
    if not name.endswith("_CAD"):
        raise RuntimeError("document name %r does not end in _CAD" % name)
    repo = ARGS["repo_root"]
    f3d = os.path.join(repo, "v2/01-CAD-Native/wall", name + ".f3d")
    step = os.path.join(repo, "v2/03-Manufacturing/wall", name[:-4] + "_STEP.step")
    os.makedirs(os.path.dirname(step), exist_ok=True)
    em = design.exportManager
    ok_f3d = export(em, em.createFusionArchiveExportOptions, f3d, root)
    ok_step = export(em, em.createSTEPExportOptions, step, root)
    print("export %s: %s" % (os.path.relpath(f3d, repo), ok_f3d))
    print("export %s: %s" % (os.path.relpath(step, repo), ok_step))
    if not (ok_f3d and ok_step):
        raise RuntimeError("export failed")
    want = box(root)
    copy = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
    try:
        got = box(adsk.fusion.Design.cast(copy.products.itemByProductType("DesignProductType")).rootComponent)
    finally:
        copy.close(False)
        doc.activate()
    diff = max(abs(a - b) for a, b in zip(want, got))
    print("design box %s" % want)
    print("STEP box   %s (max difference %.3f mm)" % (got, diff))
    if diff > 0.05:
        raise RuntimeError("STEP re-read does not match the design")
