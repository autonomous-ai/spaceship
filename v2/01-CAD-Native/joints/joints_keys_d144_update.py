"""D-144 update run on the saved corner key family design (version 2 to version 3).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_keys_d144_update.py \\
        --doc 111211_P01_BASE-CORNER-KEY-TABULATED_CAD --folder "Default Project/FocusPod v2/joints" --close

D-144 (PM ruling 2026-11-01, joints register J-BASE-02): the square key at the back corners, 111211, takes its two
fixing holes 6.0 either side of its centre line, the +y one 10.5 from its back face and the -y one 17.8 (stepped 7.3),
so the side band's 7.0 holes stay 14 from its back end and the screws 14 apart. FR1's square key keeps the first
layout (10.5 from the back, 7.0 either side) as its own number, 111215. The front keys don't change.

In the saved design: a new parameter fix_step (the -y hole's step along x), fix_y per variant, and the -y fixing
hole's offset from the back edge becomes fix_x + fix_step. The design is saved as 111211 (a new version, never a
copy); the .f3d and five STEPs (each with its own part number) are exported from it; an edit test moves the step and
back; the document closes without keeping the per-STEP changes.
"""
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
KEYS = "111211_P01_BASE-CORNER-KEY-TABULATED_CAD"
VARIANTS = [  # part number, name, STEP file, cut angle, fix_y, fix_step, the holes it must have (x, y)
    ("111211", "BASE - CORNER KEY - SQUARE - COMMON", "111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step",
     "0 deg", "6 mm", "7.3 mm", [(10.5, 6.0), (17.8, -6.0)]),
    ("111212", "BASE - CORNER KEY - FRONT - LH", "111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step",
     "-24.14 deg", "7 mm", "0 mm", [(10.5, 7.0), (10.5, -7.0)]),
    ("111213", "BASE - CORNER KEY - FRONT - RH", "111213_P01_BASE-CORNER-KEY-FRONT-RH_STEP.step",
     "24.02 deg", "7 mm", "0 mm", [(10.5, 7.0), (10.5, -7.0)]),
    ("111214", "BASE - CORNER KEY - KNEE - LH", "111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step",
     "-7.25 deg", "7 mm", "0 mm", [(10.5, 7.0), (10.5, -7.0)]),
    ("111215", "BASE - CORNER KEY - SQUARE - INLINE", "111215_P01_BASE-CORNER-KEY-SQUARE-INLINE_STEP.step",
     "0 deg", "7 mm", "0 mm", [(10.5, 7.0), (10.5, -7.0)]),
]
FAMILY_DESC = ("BASE - CORNER KEY - TABULATED 111211, 111212, 111213, 111214, 111215 | Ke góc đế (bảng 111211 đến 111215) "
               "| rev P01 | UNITS MM; MATERIAL EN AW-6061-T6; FINISH MILL FINISH, DEBURRED; ISO 2768-m; CUT 111211 0 DEG "
               "(SHOWN), 111212 -24.14 DEG, 111213 +24.02 DEG, 111214 -7.25 DEG, 111215 0 DEG; FIXING HOLES 111211 AT "
               "(10.5, +6) AND (17.8, -6), THE OTHERS AT (10.5, +-7) (D-144); joints register J-BASE-02; PROPOSED")


def mm(v):
    return round(v * 10.0, 3)


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
            out.append((mm(g.origin.x), mm(g.origin.y)))
    return sorted(set(out))


def same(got, want):
    return len(got) == len(want) and all(abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01
                                         for a, b in zip(sorted(got), sorted(want)))


def set_variant(design, root, var):
    pn, name, _step, ang, fy, fs, want = var
    up = design.userParameters
    up.itemByName("cut_angle").expression = ang
    up.itemByName("fix_y").expression = fy
    up.itemByName("fix_step").expression = fs
    root.partNumber = pn
    root.description = "%s | rev P01 | cut %s | fixing holes %s | joints register J-BASE-02 | PROPOSED" % (
        name, ang, ", ".join("(%g, %+g)" % h for h in want))
    adsk.doEvents()
    health(design)
    got = fixing_hole_centres(root.bRepBodies.item(0))
    if not same(got, want):
        raise RuntimeError("%s: fixing holes %s, want %s" % (pn, got, want))
    return got


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.partNumber != "111211" or not doc.name.startswith(KEYS):
        raise RuntimeError("open %s with --doc first (active: %s, part %s)" % (KEYS, doc.name, root.partNumber))
    up = design.userParameters
    if up.itemByName("fix_step") is None:
        if up.add("fix_step", adsk.core.ValueInput.createByString("7.3 mm"), "mm",
                  "PROPOSED (D-144): the -y fixing hole's step along x from fix_x; 7.3 on 111211 (the back "
                  "corners), 0 on the others") is None:
            raise RuntimeError("could not add fix_step")
    # the -y fixing hole's offset from the back edge: fix_x -> fix_x + fix_step (its model parameter)
    hole = next((root.features.holeFeatures.item(i) for i in range(root.features.holeFeatures.count)
                 if "FIXING HOLE -Y" in root.features.holeFeatures.item(i).name), None)
    if hole is None:
        raise RuntimeError("no FIXING HOLE -Y feature")
    moved = 0
    for i in range(root.modelParameters.count):
        p = root.modelParameters.item(i)
        try:
            by = adsk.fusion.HoleFeature.cast(p.createdBy)
        except Exception:
            continue
        if by and by.name == hole.name and p.expression.replace(" ", "") == "fix_x":
            p.expression = "fix_x + fix_step"
            moved += 1
    if moved != 1:
        raise RuntimeError("expected one fix_x offset on the -y hole, changed %d" % moved)
    fy = up.itemByName("fix_y")
    fy.comment = "PROPOSED: fixing holes either side of the centre line: 6 on 111211 (D-144), 7 on the others (C09)"
    first = set_variant(design, root, VARIANTS[0])
    print("111211 (saved state): fixing holes %s" % (first,))
    root.description = FAMILY_DESC
    if not doc.save("D-144: 111211's fixing holes at (10.5, +6) and (17.8, -6); 111215 added (FR1, the first holes); "
                    "joints_keys_d144_update.py"):
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
    print("saved (a new version) and exported %s" % os.path.basename(f3d))
    for var in VARIANTS:
        got = set_variant(design, root, var)
        path = os.path.join(REPO, "v2/03-Manufacturing/joints", var[2])
        for attempt in range(10):
            adsk.doEvents()
            if em.execute(em.createSTEPExportOptions(path, root)) and os.path.exists(path) and os.path.getsize(path) > 2000:
                break
            time.sleep(3)
        else:
            raise RuntimeError("STEP export failed: " + var[2])
        b = root.bRepBodies.item(0).boundingBox
        print("  STEP %s as %s, cut %s: X %.2f..%.2f, fixing holes %s" % (
            var[2], var[0], var[3], mm(b.minPoint.x), mm(b.maxPoint.x), got))
    set_variant(design, root, VARIANTS[0])
    # edit test: the step moves the -y hole along x, and back
    up.itemByName("fix_step").expression = "8 mm"
    adsk.doEvents()
    health(design)
    moved_to = fixing_hole_centres(root.bRepBodies.item(0))
    up.itemByName("fix_step").expression = "7.3 mm"
    adsk.doEvents()
    health(design)
    back = fixing_hole_centres(root.bRepBodies.item(0))
    ok = same(moved_to, [(10.5, 6.0), (18.5, -6.0)]) and same(back, VARIANTS[0][6])
    print("  EDIT TEST fix_step 7.3 -> 8 -> 7.3: %s -> %s -> %s: %s" % (VARIANTS[0][6], moved_to, back, "PASS" if ok else "FAIL"))
    if not ok:
        raise RuntimeError("edit test failed")
    if not doc.close(False):
        raise RuntimeError("close failed")
    print("closed %s (the per-STEP changes and the edit test were not kept; the saved version is 111211)" % KEYS)
