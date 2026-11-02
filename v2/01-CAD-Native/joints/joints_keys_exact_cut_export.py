"""Export run on the saved corner key family design (version 3): 111212 and 111214 at their exact mitres.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_keys_exact_cut_export.py \\
        --doc 111211_P01_BASE-CORNER-KEY-TABULATED_CAD --folder "Default Project/FocusPod v2/joints" --close

BASE (2026-11-01, relayed by the Lead): cut 111212's face at the mitre's exact 24.1446 deg. The version 3 exports took
corner-keys.csv's 2-decimal angles, so 111212 was cut at -24.14 and the knee 111214 at -7.25; the mitres are
-24.1446 and -7.2546 (corner_keys.py, which now prints them to 4 decimals and checks the build script's KEY_VARIANTS
against them). 111213's +24.02 is already exact, and 111211 and 111215 are square.

The run sets each of the two variants as the build does (cut_angle, fix_y 7, fix_step 0, its own part number),
checks its fixing holes and its long side against the mitre, exports its STEP, and closes the design without saving:
the saved state (111211, square) doesn't change, so the drawing's reference stays current.
"""
import math
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
KEYS = "111211_P01_BASE-CORNER-KEY-TABULATED_CAD"
KEY_LEN, KEY_W = 30.0, 35.0
VARIANTS = [  # part number, name, STEP file, cut angle (deg, signed), the fixing holes it must have (x, y)
    ("111212", "BASE - CORNER KEY - FRONT - LH", "111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step", -24.1446,
     [(10.5, 7.0), (10.5, -7.0)]),
    ("111214", "BASE - CORNER KEY - KNEE - LH", "111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step", -7.2546,
     [(10.5, 7.0), (10.5, -7.0)]),
]


def mm(v):
    return round(v * 10.0, 4)


def health(design):
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    if bad:
        raise RuntimeError("unhealthy features: %s" % bad)


def fixing_hole_centres(body):
    """(x, y) of the bottom's Ø5.0 tap-drill holes (axis along z), sorted."""
    out = []
    for f in body.faces:
        g = f.geometry
        if isinstance(g, adsk.core.Cylinder) and abs(g.axis.z) > 0.9 and abs(g.radius * 20.0 - 5.0) < 0.1:
            out.append((round(g.origin.x * 10.0, 3), round(g.origin.y * 10.0, 3)))
    return sorted(set(out))


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != "111211" or not doc.name.startswith(KEYS):
        raise RuntimeError("open %s with --doc first (active: %s, part %s)" % (KEYS, doc.name, root.partNumber))
    try:
        export_two(design, root)
    finally:
        if doc.isValid:
            doc.close(False)
            print("closed %s without saving (the saved state, 111211, is unchanged)" % KEYS)


def export_two(design, root):
    up = design.userParameters
    em = design.exportManager
    for pn, name, step, ang, want in VARIANTS:
        up.itemByName("cut_angle").expression = "%.4f deg" % ang
        up.itemByName("fix_y").expression = "7 mm"
        up.itemByName("fix_step").expression = "0 mm"
        root.partNumber = pn          # each STEP carries its own part number (C06)
        root.description = "%s | rev P01 | cut %.4f deg (the mitre, exact) | fixing holes %s | joints register " \
                           "J-BASE-02 | PROPOSED" % (name, ang, ", ".join("(%g, %+g)" % h for h in want))
        adsk.doEvents()
        health(design)
        body = root.bRepBodies.item(0)
        got = fixing_hole_centres(body)
        if len(got) != 2 or any(abs(a[0] - b[0]) > 0.01 or abs(a[1] - b[1]) > 0.01 for a, b in zip(got, sorted(want))):
            raise RuntimeError("%s: fixing holes %s, want %s" % (pn, got, sorted(want)))
        b = body.boundingBox
        long_side = KEY_LEN + KEY_W / 2 * math.tan(math.radians(abs(ang)))
        if abs(mm(b.maxPoint.x) - long_side) > 0.002 or abs(mm(b.minPoint.x)) > 0.002:
            raise RuntimeError("%s: X %.4f..%.4f, want 0..%.4f" % (pn, mm(b.minPoint.x), mm(b.maxPoint.x), long_side))
        path = os.path.join(REPO, "v2/03-Manufacturing/joints", step)
        for _attempt in range(10):
            adsk.doEvents()
            if em.execute(em.createSTEPExportOptions(path, root)) and os.path.exists(path) and \
                    os.path.getsize(path) > 2000:
                break
            time.sleep(3)
        else:
            raise RuntimeError("STEP export failed: " + step)
        print("  STEP %s as %s, cut %.4f deg: X %.4f..%.4f (the mitre's long side %.4f), fixing holes %s"
              % (step, pn, ang, mm(b.minPoint.x), mm(b.maxPoint.x), long_side, got))
