"""One update run on the saved corner key family design (version 1 to version 2).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_keys_update.py \\
        --doc 111211_P01_BASE-CORNER-KEY-TABULATED_CAD --folder "Default Project/FocusPod v2/joints" --close

The mechanical check on the first build found two things, fixed here in the saved design
(joints_hardware_build.py has the same values for any rebuild):
- C09: the fixing holes sat 10.0 from the free edges, under 2 x the hole (10.06). They move
  to fix_x 10.5 from the back face and fix_y 7.0 from the centre line (10.5 from the sides).
- The carrier's Ø7.0 holes for them must sit 2 x 7 from its mitred end (PM, 2026-11-01): the
  key grows from 25 to 30 on its centre line, so they sit 14.9 or more from every cut end.
- C06: the four STEPs all carried the family's part number 111211. Each STEP now carries
  its own number and name (111212 to 111214 at their cuts).
It saves the design (a new version, never a copy), exports the .f3d and the four STEPs from
that version, and closes the document without keeping the per-STEP part number changes.
"""
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
KEYS = "111211_P01_BASE-CORNER-KEY-TABULATED_CAD"
VARIANTS = [  # part number, name, STEP file, cut angle
    ("111211", "BASE - CORNER KEY - SQUARE - COMMON", "111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step", "0 deg"),
    ("111212", "BASE - CORNER KEY - FRONT - LH", "111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step", "-24.14 deg"),
    ("111213", "BASE - CORNER KEY - FRONT - RH", "111213_P01_BASE-CORNER-KEY-FRONT-RH_STEP.step", "24.02 deg"),
    ("111214", "BASE - CORNER KEY - KNEE - LH", "111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step", "-7.25 deg"),
]


def mm(v):
    return round(v * 10.0, 3)


def health(design):
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    if bad:
        raise RuntimeError("unhealthy features: %s" % bad)


def fixing_hole_centres(body):
    out = []
    for f in body.faces:
        g = f.geometry
        if isinstance(g, adsk.core.Cylinder) and abs(g.axis.z) > 0.9 and abs(g.radius * 20.0 - 5.0) < 0.1:
            out.append((mm(g.origin.x), mm(g.origin.y)))
    return sorted(out)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != "111211" or not doc.name.startswith(KEYS):
        raise RuntimeError("open %s with --doc first (active: %s, part %s)" % (KEYS, doc.name, root.partNumber))
    family = (root.partNumber, root.description)
    up = design.userParameters
    for name, expr, comment in (
            ("key_len", "30 mm", "PROPOSED: length along the carrier on the centre line; 30 keeps the carrier's Ø7.0 fixing holes 2 x 7 from its cut end (J-BASE-02)"),
            ("fix_x", "10.5 mm", "PROPOSED: fixing holes from the key's back face, over 2 x the hole (C09) (FR-16)"),
            ("fix_y", "7 mm", "PROPOSED: fixing holes either side of the centre line, 10.5 from the side faces (C09) (FR-16)")):
        p = up.itemByName(name)
        if p is None:
            raise RuntimeError("no parameter " + name)
        p.expression = expr
        p.comment = comment
    adsk.doEvents()
    health(design)
    body = root.bRepBodies.item(0)
    centres = fixing_hole_centres(body)
    print("fixing holes at %s (want X 10.5, Y -7 and 7)" % centres)
    if [c for c in centres if abs(c[0] - 10.5) > 0.01 or abs(abs(c[1]) - 7.0) > 0.01] or len(centres) != 2:
        raise RuntimeError("the fixing holes didn't move as expected")
    if not doc.save("Key 30 long, fixing holes 10.5 from its edges (C09, band holes 2 x 7 from the cut end); joints_keys_update.py"):
        raise RuntimeError("save failed")
    em = design.exportManager
    f3d = os.path.join(REPO, "v2/01-CAD-Native/joints", KEYS + ".f3d")
    for attempt in range(10):
        adsk.doEvents()
        if em.execute(em.createFusionArchiveExportOptions(f3d, root)):
            break
        time.sleep(3)
    else:
        raise RuntimeError("f3d export failed")
    print("saved (new version) and exported %s" % os.path.basename(f3d))
    for pn, name, step, ang in VARIANTS:
        up.itemByName("cut_angle").expression = ang
        root.partNumber = pn
        root.description = "%s | rev P01 | cut %s | joints register J-BASE-02 | PROPOSED" % (name, ang)
        adsk.doEvents()
        health(design)
        path = os.path.join(REPO, "v2/03-Manufacturing/joints", step)
        for attempt in range(10):
            adsk.doEvents()
            if em.execute(em.createSTEPExportOptions(path, root)) and os.path.getsize(path) > 2000:
                break
            time.sleep(3)
        else:
            raise RuntimeError("STEP export failed: " + step)
        b = root.bRepBodies.item(0).boundingBox
        print("  STEP %s as %s, cut %s: X %.2f..%.2f, holes %s" % (step, pn, ang, mm(b.minPoint.x), mm(b.maxPoint.x),
                                                                fixing_hole_centres(root.bRepBodies.item(0))))
    up.itemByName("cut_angle").expression = "0 deg"
    root.partNumber, root.description = family
    adsk.doEvents()
    if not doc.close(False):
        raise RuntimeError("close failed")
    print("closed %s (the per-STEP part numbers were not kept; the saved version is the family at 0)" % KEYS)
