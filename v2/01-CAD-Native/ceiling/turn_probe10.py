"""Tenth turned-copy probe, in a throwaway unsaved design (D-118).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe10.py --label "CEILING Engineer"

Probe 9 (2026-11-01 08:33) placed every copy right with an empty ANCHOR as the frame's first child: Fusion grounds
only the first occurrence made in a component, and a joint on a grounded occurrence (or on a copy of its component,
which comes out grounded too) conflicts. Plain, angle 180 (a turn about Z) and flip + angle 180 (a turn about Y) all
landed; flip + angle 0 is a turn about X. An empty component would show in the STEP and the parts lists, so this
probe instead turns the member's first occurrence's ground to parent off as soon as it is made (no anchor), then
repeats probe 9's cases F, P, Q and T, read in the design through the frame's occurrence.
"""

import adsk.core
import adsk.fusion

MM = 0.1
WANT = {   # tag: (rotation rows, box in the design: x0, x1, y0, y1, z0, z1)
    "F": (((1, 0, 0), (0, 1, 0), (0, 0, 1)), (100, 120, 0, 10, 160, 170)),
    "P": (((1, 0, 0), (0, 1, 0), (0, 0, 1)), (100, 120, 0, 10, 260, 270)),
    "Q": (((-1, 0, 0), (0, -1, 0), (0, 0, 1)), (-120, -100, -10, 0, 360, 370)),
    "T": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 350, 360)),
    "U": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 450, 460)),
    "N": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 550, 560)),
    "N after +50": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 600, 610)),
}


def block(comp):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(100 * MM, 0, 0),
                                                     adsk.core.Point3D.create(120 * MM, 10 * MM, 0))
    ext = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(10 * MM)),
                         adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(50 * MM))
    comp.features.extrudeFeatures.add(ext)


def target(fc, expr):
    pin = fc.constructionPlanes.createInput()
    pin.setByOffset(fc.xYConstructionPlane, adsk.core.ValueInput.createByString(expr))
    plane = fc.constructionPlanes.add(pin)
    sk = fc.sketches.add(plane)
    return plane, sk.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0))


def joint(fc, comp, occ, pt, flip=False, angle=None):
    g = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(occ))
    ji = fc.joints.createInput(g, adsk.fusion.JointGeometry.createByPoint(pt))
    ji.setAsRigidJointMotion()
    if flip:
        ji.isFlipped = True
    if angle is not None:
        ji.angle = adsk.core.ValueInput.createByString(angle)
    return fc.joints.add(ji)


def world(frame, occ):
    """(rotation rows, box mm) of occ's body in the design, read through the frame's occurrence in root."""
    px = occ.createForAssemblyContext(frame)
    m = px.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 4) for c in range(3)) for r in range(3))
    b = px.bRepBodies.item(0).boundingBox
    box = tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                           b.minPoint.z, b.maxPoint.z))
    return rot, box


def report(tag, design, frame, occ, j):
    design.computeAll()
    adsk.doEvents()
    rot, box = world(frame, occ)
    hs = getattr(j, "healthState", None)
    ok = hs is None or hs == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    msg = "" if ok else " (%s)" % (getattr(j, "errorOrWarningMessage", "") or "").replace("\n", " ")[:80]
    want_rot, want_box = WANT[tag]
    good = ok and all(abs(rot[r][c] - want_rot[r][c]) < 1e-4 for r in range(3) for c in range(3)) and \
        max(abs(a - b) for a, b in zip(box, want_box)) < 1e-3
    print("case %s: healthy %s%s; rotation %s box %s -> %s" % (
        tag, "n/a" if hs is None else ok, msg, rot, box, "RIGHT" if good else "no (want %s %s)" % (want_rot, want_box)))
    return good


def flag(occ):
    try:
        return "ground to parent %s" % occ.isGroundToParent
    except Exception as e:      # noqa: BLE001  (a probe: report whatever Fusion says)
        return "ground to parent: %s" % str(e).replace("\n", " ")[:60]


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.userParameters.add("tz_n", adsk.core.ValueInput.createByString("610 mm"), "mm", "probe target")
        root = design.rootComponent
        frame = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        fc = frame.component
        fc.name = "PROBE FRAME"
        first = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = first.component
        comp.name = "PROBE MEMBER"
        made = flag(first)
        first.isGroundToParent = False
        block(comp)
        print("made: frame %s; the member's first occurrence (the frame's first child) %s, set off: %s" % (
            flag(frame), made, flag(first)))
        res = {}
        _p, pt = target(fc, "110 mm")
        res["F"] = report("F", design, frame, first, joint(fc, comp, first, pt))
        for tag, z, flip, angle in (("P", 210, False, None), ("Q", 310, False, "180 deg"),
                                    ("T", 410, True, "180 deg")):
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            print("made: copy %s %s" % (tag, flag(c)))
            _p, pt = target(fc, "%d mm" % z)
            res[tag] = report(tag, design, frame, c, joint(fc, comp, c, pt, flip, angle))
        print("TURN PROBE 10: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
