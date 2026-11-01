"""Export run on the saved locating spigot design: the 11 mm proud variant 831010 (the Lead's ruling 2026-11-01).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_spigot_variant_export.py \\
        --doc 831001_P01_HARDWARE-LOCATING-SPIGOT_CAD --folder "Default Project/FocusPod v2/joints" --close

J-FRONT-03: DT's two spigots on DR's ledge stand 11 proud instead of 8, so they still engage DT's holes 5 (a
longer pin, a tabulated variant of 831001, rather than a pad welded onto the steel ledge). The saved design already
drives the pin from pin_proud (pin_len = pin_proud - the rivnut's 0.76 head), so the run sets pin_proud 11 and the
part number, checks the body (the pin 10.24 above its shoulder, the stud 8 below, Ø8), exports the STEP, and closes
the design without saving: its saved state (831001, 8 proud) is unchanged, so the spigot sheet's reference stays
current. A fresh build makes both STEPs (joints_hardware_build.py, SPIGOT_VARIANTS).
"""
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
SPIGOT = "831001_P01_HARDWARE-LOCATING-SPIGOT_CAD"
PN, NAME = "831010", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - 11 PROUD - STAINLESS"
STEP = "831010_P01_HARDWARE-LOCATING-SPIGOT-11-PROUD_STEP.step"
PROUD, HEAD, STUD, PIN_D = 11.0, 0.76, 8.0, 8.0


def mm(v):
    return round(v * 10.0, 4)


def health(design):
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    if bad:
        raise RuntimeError("unhealthy features: %s" % bad)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != "831001" or not doc.name.startswith(SPIGOT):
        raise RuntimeError("open %s with --doc first (active: %s, part %s)" % (SPIGOT, doc.name, root.partNumber))
    try:
        export_variant(design, root)
    finally:
        if doc.isValid:
            doc.close(False)
            print("closed %s without saving (the saved state, 831001 at 8 proud, is unchanged)" % SPIGOT)


def export_variant(design, root):
    up = design.userParameters
    saved = up.itemByName("pin_proud").expression
    up.itemByName("pin_proud").expression = "%g mm" % PROUD
    root.partNumber = PN          # its STEP carries its own part number (C06)
    root.description = "%s | rev P01 | pin %g proud | joints register H-45, J-FRONT-03 | PROPOSED" % (NAME, PROUD)
    adsk.doEvents()
    health(design)
    if root.bRepBodies.count != 1:
        raise RuntimeError("%d bodies" % root.bRepBodies.count)
    body = root.bRepBodies.item(0)
    b = body.boundingBox
    got = (mm(b.minPoint.x), mm(b.minPoint.y), mm(b.minPoint.z), mm(b.maxPoint.x), mm(b.maxPoint.y), mm(b.maxPoint.z))
    want = (-PIN_D / 2, -PIN_D / 2, -STUD, PIN_D / 2, PIN_D / 2, PROUD - HEAD)
    if any(abs(g - w) > 0.002 for g, w in zip(got, want)):
        raise RuntimeError("%s: box %s, want %s" % (PN, got, want))
    em = design.exportManager
    path = os.path.join(REPO, "v2/03-Manufacturing/joints", STEP)
    for _attempt in range(10):
        adsk.doEvents()
        if em.execute(em.createSTEPExportOptions(path, root)) and os.path.exists(path) and os.path.getsize(path) > 2000:
            break
        time.sleep(3)
    else:
        raise RuntimeError("STEP export failed: " + STEP)
    print("  STEP %s as %s (pin_proud %s, was %s): box %s, mass %.5f kg" % (
        STEP, PN, up.itemByName("pin_proud").expression, saved, got, body.physicalProperties.mass))
