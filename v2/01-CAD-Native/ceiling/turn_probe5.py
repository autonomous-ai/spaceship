"""Fifth turned-copy probe, in a throwaway unsaved design (D-118). Probes 2 to 4 found every joint on a COPY of the probe
block failing ("conflicts with assembly relationships"), even a plain one, while a joint on a new, unique component (the
locator) computed. The block's first occurrence is the design's first component, which Fusion may ground; the ceiling
build's working copies (the plain cross members) have their first occurrence inside a frame component, jointed too.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe5.py --label "CEILING Engineer"

  K  the block's first occurrence in root: is it grounded? Unground it, then a plain joint on a copy
  L  a second block built inside a sub-component (as the build does), its copy in root: a plain joint
  M  as L, the joint's angle 180 deg on its input (the turn the build needs)
  N  as L, the copy turned in place and held by a rigid as-built joint to a locator placed by a plain joint; then
     the target moves +50 in Z and the copy must follow, still turned

The turn about Y sends the block to X -120..-100, Z 50..60 with the origin at (0, 0, 110). Closes without saving.
"""

import adsk.core
import adsk.fusion

MM = 0.1
TURN_Y = ((-1, 0, 0), (0, 1, 0), (0, 0, -1))
IDENT = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def bbox_mm(body):
    b = body.boundingBox
    return tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                            b.minPoint.z, b.maxPoint.z))


def place_of(occ):
    m = occ.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 4) for c in range(3)) for r in range(3))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    return rot, move, bbox_mm(occ.bRepBodies.item(0)) if occ.bRepBodies.count else None


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


def target(root, z_mm):
    pin = root.constructionPlanes.createInput()
    pin.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_mm * MM))
    plane = root.constructionPlanes.add(pin)
    sk = root.sketches.add(plane)
    return plane, sk.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0))


def plain_joint(root, comp, copy, pt, angle=None):
    g_occ = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(copy))
    ji = root.joints.createInput(g_occ, adsk.fusion.JointGeometry.createByPoint(pt))
    ji.setAsRigidJointMotion()
    if angle:
        ji.angle = adsk.core.ValueInput.createByString(angle)
    return root.joints.add(ji)


def report(tag, design, joint, copy, want_rot, want_box):
    design.computeAll()
    adsk.doEvents()
    rot, move, box = place_of(copy)
    hs = getattr(joint, "healthState", None)
    ok = hs is None or hs == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    msg = "" if ok else " (%s)" % (getattr(joint, "errorOrWarningMessage", "") or "").replace("\n", " ")[:90]
    good = all(abs(rot[r][c] - want_rot[r][c]) < 1e-6 for r in range(3) for c in range(3)) and \
        box is not None and max(abs(a - b) for a, b in zip(box, want_box)) < 1e-3
    print("case %s: healthy %s%s; rotation %s move %s box %s -> %s" % (
        tag, "n/a" if hs is None else ok, msg, rot, move, box, "RIGHT" if good else "no"))
    return good


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        res = {}
        # K: the first component in root
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = "PROBE BLOCK ROOT"
        block(comp)
        print("case K: the first occurrence grounded %s, grounded to parent %s" % (
            occ.isGrounded, getattr(occ, "isGroundToParent", "n/a")))
        occ.isGrounded = False
        copy = root.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
        _p, pt = target(root, 110)
        res["K"] = report("K (original ungrounded, plain joint on a copy)", design, plain_joint(root, comp, copy, pt),
                          copy, IDENT, (100.0, 120.0, 0.0, 10.0, 160.0, 170.0))
        # L and M: the block built inside a sub-component, its copies in root
        sub = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        sub.name = "PROBE FRAME"
        bocc = sub.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        bcomp = bocc.component
        bcomp.name = "PROBE BLOCK IN FRAME"
        block(bcomp)
        print("case L: the block's first occurrence (in the sub-component) grounded %s" % bocc.isGrounded)
        for tag, angle, want_rot, want_box in (("L (plain joint on a copy)", None, IDENT, (100.0, 120.0, 0.0, 10.0, 160.0, 170.0)),
                                               ("M (angle 180 on the input)", "180 deg", None, None)):
            c2 = root.occurrences.addExistingComponent(bcomp, adsk.core.Matrix3D.create())
            _p, pt = target(root, 110)
            j = plain_joint(root, bcomp, c2, pt, angle)
            if want_rot is None:        # the angle turns about the joint's Z (the sketch's normal): about Z, 180
                want_rot, want_box = ((-1, 0, 0), (0, -1, 0), (0, 0, 1)), (-120.0, -100.0, -10.0, 0.0, 160.0, 170.0)
            res[tag[0]] = report(tag, design, j, c2, want_rot, want_box)
        # N: a locator placed by a plain joint, the copy turned in place and held to it by a rigid as-built joint
        lo = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        lo.component.name = "PROBE LOCATOR"
        plane, pt = target(root, 110)
        jl = plain_joint(root, lo.component, lo, pt)
        design.computeAll()
        print("case N locator: healthy %s, move %s" % (
            jl.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState, place_of(lo)[1]))
        c3 = root.occurrences.addExistingComponent(bcomp, adsk.core.Matrix3D.create())
        m = adsk.core.Matrix3D.create()
        m.setCell(0, 0, -1.0)
        m.setCell(2, 2, -1.0)
        m.setCell(2, 3, 110 * MM)
        c3.transform2 = m
        ab = root.asBuiltJoints.createInput(c3, lo, None)
        ab.setAsRigidJointMotion()
        abj = root.asBuiltJoints.add(ab)
        res["N"] = report("N (turned in place, as-built to the locator)", design, abj, c3, TURN_Y,
                          (-120.0, -100.0, 0.0, 10.0, 50.0, 60.0))
        adsk.fusion.ConstructionPlaneOffsetDefinition.cast(plane.definition).offset.value = 160 * MM
        res["N edit"] = report("N after the target moves +50 in Z", design, abj, c3, TURN_Y,
                               (-120.0, -100.0, 0.0, 10.0, 100.0, 110.0))
        print("TURN PROBE 5: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
