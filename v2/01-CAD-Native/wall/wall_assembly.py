"""Spaceship (FocusPod v2) WALL assembly 210000: the 8 outer panels and their 8 lining cassettes, inserted.
NOT RUN YET (2026-11-01): it runs once all 16 designs are saved.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_assembly.py --label "WALL Engineer" \
        --doc 210000_P01_WALL_CAD --doc-new --arg post=1 --close --discard

Inserts each saved panel and cassette design (`<pn>_P01_<NAME>_CAD` in Default Project / FocusPod v2) into the
active, empty design as a referenced component at the identity transform: every design is already in pod
coordinates (conventions section 4), so nothing moves. Then it checks what only the whole wall can show:
every pair of bodies across the 16 designs (panel to panel, panel to cassette, cassette to cassette) for an
overlap over 1 mm³, apart from the spigots, which stand in the panel above's spigot holes by design; and the
wall's box against the skeleton (X -1250 to 1250, Y -645 to 850, Z 112.26 to 2400). With post=1 it saves
and exports the STEP (cm, as Fusion writes it, D-13) to v2/03-Manufacturing/wall/, re-reads it and compares
the box. It refuses if a design is missing.
"""

import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
PN, REV, NAME = "210000", "P01", "WALL"
DESIGNS = [
    "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD", "210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_CAD",
    "210103_P01_WALL-PANEL-ASSY-SIDE-UPPER-LH_CAD", "210104_P01_WALL-PANEL-ASSY-SIDE-UPPER-RH_CAD",
    "210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD", "210202_P01_WALL-PANEL-ASSY-BACK-LOWER-B2_CAD",
    "210203_P01_WALL-PANEL-ASSY-BACK-UPPER-B3_CAD", "210204_P01_WALL-PANEL-ASSY-BACK-UPPER-B4_CAD",
    "510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD", "510102_P01_LINING-CASSETTE-SIDE-LOWER-RH_CAD",
    "510103_P01_LINING-CASSETTE-SIDE-UPPER-LH_CAD", "510104_P01_LINING-CASSETTE-SIDE-UPPER-RH_CAD",
    "510201_P01_LINING-CASSETTE-BACK-LOWER-B1_CAD", "510202_P01_LINING-CASSETTE-BACK-LOWER-B2_CAD",
    "510203_P01_LINING-CASSETTE-BACK-UPPER-B3_CAD", "510204_P01_LINING-CASSETTE-BACK-UPPER-B4_CAD",
]
EXPECT_BOX = (-1250.0, -645.0, 112.26, 1250.0, 850.0, 2400.0)     # skeleton P04 (mm)


def bbox_mm(b):
    bb = b.boundingBox
    return [round(v * 10.0, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                         bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]


def all_bodies(root):
    """(occurrence name, body proxy) for every solid body in the assembly, in assembly context."""
    out = []
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            if b.isSolid:
                out.append((occ.component.partNumber, b))
    return out


def clashes(items):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = []
    boxes = [bbox_mm(b) for _o, b in items]
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            ba, bb = boxes[i], boxes[j]
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            (pa, a), (pb, b) = items[i], items[j]
            if pa == pb:
                continue                        # inside one design: that design's own build checked it
            t1, t2 = tbm.copy(a), tbm.copy(b)
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append(("%s / %s" % (pa, a.name), "%s / %s" % (pb, b.name), round(vol, 1)))
    return hits


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.occurrences.count or root.bRepBodies.count:
        raise RuntimeError("the active design is not empty")
    folder = app.data.activeProject.rootFolder.dataFolders.itemByName("FocusPod v2")
    if folder is None:
        raise RuntimeError("folder FocusPod v2 not found in the active project")
    files = {}
    for i in range(folder.dataFiles.count):
        f = folder.dataFiles.item(i)
        files[f.name] = f
    missing = [d for d in DESIGNS if d not in files]
    if missing:
        raise RuntimeError("designs not saved yet: %s" % missing)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    for d in DESIGNS:
        occ = root.occurrences.addByInsert(files[d], adsk.core.Matrix3D.create(), True)
        if occ is None:
            raise RuntimeError("insert failed: " + d)
        print("inserted %s v%s" % (d, files[d].versionNumber))
    root.partNumber = PN
    root.description = "WALL | Vách | %s | the 8 outer panels and their 8 lining cassettes" % REV
    items = all_bodies(root)
    boxes = [bbox_mm(b) for _o, b in items]
    box = [min(b[k] for b in boxes) for k in range(3)] + [max(b[k + 3] for b in boxes) for k in range(3)]
    print("bodies %d; wall box %s (skeleton %s)" % (len(items), box, list(EXPECT_BOX)))
    hits = clashes(items)
    spigots = [h for h in hits if "SPIGOT" in h[0] or "SPIGOT" in h[1]]
    bad = [h for h in hits if h not in spigots]
    print("cross-design overlaps over 1 mm3: %d (spigots in their holes %d, unexpected %d)" % (
        len(hits), len(spigots), len(bad)))
    for h in bad[:40]:
        print("CLASH|%s|%s|%s mm3" % h)
    off = [k for k in range(6) if abs(box[k] - EXPECT_BOX[k]) > 0.05 and not (k == 5 and box[k] <= EXPECT_BOX[k])]
    if bad or off:
        raise RuntimeError("wall check failed: %d unexpected overlaps; box off on %s" % (len(bad), off))
    if ARGS.get("post") != "1":
        return
    doc = app.activeDocument
    if not doc.save("%s assembly of the 16 WALL designs" % REV):
        raise RuntimeError("save failed")
    rel = "v2/03-Manufacturing/wall/%s_%s_%s_STEP.step" % (PN, REV, NAME)
    path = os.path.join(ARGS["repo_root"], rel)
    opts = design.exportManager.createSTEPExportOptions(path, root)
    if not design.exportManager.execute(opts):
        raise RuntimeError("STEP export failed")
    imp = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(path))
    try:
        d2 = adsk.fusion.Design.cast(imp.products.itemByProductType("DesignProductType"))
        b2 = [bbox_mm(b) for c in d2.allComponents for b in c.bRepBodies if b.isSolid]
        box2 = [min(b[k] for b in b2) for k in range(3)] + [max(b[k + 3] for b in b2) for k in range(3)]
        diff = max(abs(p - q) for p, q in zip(box, box2))
        print("export %s: STEP box %s (max difference %.3f mm), %d bodies" % (rel, box2, diff, len(b2)))
        if diff > 0.05:
            raise RuntimeError("STEP box differs by %.3f mm" % diff)
    finally:
        imp.close(False)
