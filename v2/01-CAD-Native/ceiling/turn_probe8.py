"""Eighth turned-copy probe, in a throwaway unsaved design (D-118).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe8.py --label "CEILING Engineer"

Probes 6 and 7 read each occurrence's own transform2 inside the frame component, and every target sat at the same
point (0, 0, 110), so a joint acting on the wrong copy could not be told from a joint acting on its own one: the
plate copies all showed the turn of the FIRST plate's joint (45 in probe 6, 0 in probe 7), whatever their own angle.
This probe gives every joint its own target and reads where each body ends up in the design (through the frame's
occurrence, as the build's position checks read it), with the occurrences placed as the build places them (every
occurrence of a member by a joint, the first one too):

  F  the member's first occurrence, a plain joint to (0, 0, 110)
  P  a copy, plain joint to (0, 0, 210)
  Q  a copy, angle 180 deg on the input, to (0, 0, 310)          (C2's cross member 1: end for end, about Z)
  T  a copy, flipped and angle 180, to (0, 0, 410)                (C2's side member: upside down, about Y)
  U  a copy, flipped and angle 0, to (0, 0, 510)
  N  a locator (an empty component) by a plain joint to (0, 0, 610); a copy set turned about Y in place there and
     held to the locator by a rigid as-built joint; then the locator's target moves +50 in Z (a user parameter), and
     the copy must follow, still turned

The block runs X 100..120, Y 0..10, Z 50..60 in its own frame. Closes without saving.
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
        block(comp)
        res = {}
        _p, pt = target(fc, "110 mm")
        res["F"] = report("F", design, frame, first, joint(fc, comp, first, pt))
        for tag, z, flip, angle in (("P", 210, False, None), ("Q", 310, False, "180 deg"),
                                    ("T", 410, True, "180 deg"), ("U", 510, True, "0 deg")):
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            _p, pt = target(fc, "%d mm" % z)
            res[tag] = report(tag, design, frame, c, joint(fc, comp, c, pt, flip, angle))
        # N: the locator by a plain joint, the copy turned in place and held to it by an as-built joint
        lo = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        lo.component.name = "PROBE LOCATOR"
        plane, pt = target(fc, "tz_n")
        jl = joint(fc, lo.component, lo, pt)
        design.computeAll()
        lm = lo.createForAssemblyContext(frame).transform2
        print("case N locator: healthy %s, its origin in the design at %s" % (
            jl.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState,
            tuple(round(lm.getCell(r, 3) / MM, 3) for r in range(3))))
        c3 = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
        m = adsk.core.Matrix3D.create()
        m.setCell(0, 0, -1.0)
        m.setCell(2, 2, -1.0)
        m.setCell(2, 3, 610 * MM)
        c3.transform2 = m
        ab = fc.asBuiltJoints.createInput(c3, lo, None)
        ab.setAsRigidJointMotion()
        abj = fc.asBuiltJoints.add(ab)
        res["N"] = report("N", design, frame, c3, abj)
        design.userParameters.itemByName("tz_n").expression = "660 mm"
        res["N after +50"] = report("N after +50", design, frame, c3, abj)
        print("TURN PROBE 8: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
