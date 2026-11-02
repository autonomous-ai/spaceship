"""Fourth turned-copy probe, in a throwaway unsaved design (D-118): turning a copy without setting a joint's own flip or
angle, the two ways the second probe's failure leaves.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe4.py --label "CEILING Engineer"

The same 20 x 10 x 10 block off its component's origin (X 100 to 120, Y 0 to 10, Z 50 to 60). Each case its own copy:

  H  a joint origin at the target point (0, 0, 110) made flipped on its own input, then a plain rigid joint from the
     copy's origin to it
  I  as H, the joint origin turned 180 deg on its input instead
  J  an empty locator component placed by a plain rigid joint at the target point; the copy set turned about Y in
     place (its transform), then held to the locator by a rigid as-built joint. Then the target point moves +50 in Z
     (its plane's offset, as an edit test would move it): the copy must follow, still turned

For each it prints the joint health and the copy's rotation, move and box after Design.computeAll(). The turn about
Y sends the block to X -120..-100, Z 50..60 with the origin at (0, 0, 110). Closes without saving.
"""

import adsk.core
import adsk.fusion

MM = 0.1
TURN_Y = ((-1, 0, 0), (0, 1, 0), (0, 0, -1))


def bbox_mm(body):
    b = body.boundingBox
    return tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                            b.minPoint.z, b.maxPoint.z))


def place_of(occ):
    m = occ.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 4) for c in range(3)) for r in range(3))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    return rot, move, bbox_mm(occ.bRepBodies.item(0)) if occ.bRepBodies.count else None


def target(root, z_mm):
    pin = root.constructionPlanes.createInput()
    pin.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_mm * MM))
    plane = root.constructionPlanes.add(pin)
    sk = root.sketches.add(plane)
    return plane, sk.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0))


def report(tag, design, joint, copy, want_box):
    design.computeAll()
    adsk.doEvents()
    rot, move, box = place_of(copy)
    ok = joint is None or joint.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    msg = "" if ok else " (%s)" % (joint.errorOrWarningMessage or "").replace("\n", " ")[:100]
    turned = all(abs(rot[r][c] - TURN_Y[r][c]) < 1e-6 for r in range(3) for c in range(3))
    at = box is not None and max(abs(a - b) for a, b in zip(box, want_box)) < 1e-3
    print("case %s: healthy %s%s; rotation %s move %s box %s -> %s" % (
        tag, ok, msg, rot, move, box, "TURNED AND PLACED" if turned and at else "no"))
    return turned and at


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ.component
        comp.name = "PROBE BLOCK"
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(100 * MM, 0, 0),
                                                         adsk.core.Point3D.create(120 * MM, 10 * MM, 0))
        ext = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(10 * MM)),
                             adsk.fusion.ExtentDirections.PositiveExtentDirection)
        ext.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(50 * MM))
        comp.features.extrudeFeatures.add(ext)
        want = (-120.0, -100.0, 0.0, 10.0, 50.0, 60.0)
        results = {}
        for tag, flip, angle in (("H", True, None), ("I", False, "180 deg")):
            copy = root.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            _plane, pt = target(root, 110)
            joi = root.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(pt))
            joi.isFlipped = flip
            if angle:
                joi.angle = adsk.core.ValueInput.createByString(angle)
            jo = root.jointOrigins.add(joi)
            g_occ = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(copy))
            ji = root.joints.createInput(g_occ, jo)
            ji.setAsRigidJointMotion()
            try:
                j = root.joints.add(ji)
            except RuntimeError as e:
                print("case %s: joints.add raised: %s" % (tag, str(e).splitlines()[0]))
                continue
            results[tag] = report(tag, design, j, copy, want)
        # J: a locator placed by a plain joint, the copy turned in place and held to it by a rigid as-built joint
        lo_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        lo_occ.component.name = "PROBE LOCATOR"
        plane, pt = target(root, 110)
        g_lo = adsk.fusion.JointGeometry.createByPoint(lo_occ.component.originConstructionPoint.createForAssemblyContext(lo_occ))
        ji = root.joints.createInput(g_lo, adsk.fusion.JointGeometry.createByPoint(pt))
        ji.setAsRigidJointMotion()
        jl = root.joints.add(ji)
        design.computeAll()
        print("case J locator: healthy %s, move %s" % (
            jl.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState, place_of(lo_occ)[1]))
        copy = root.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
        m = adsk.core.Matrix3D.create()
        m.setCell(0, 0, -1.0)
        m.setCell(2, 2, -1.0)
        m.setCell(2, 3, 110 * MM)          # turned about Y through Z 55: the origin goes to Z 110
        copy.transform2 = m
        ab = root.asBuiltJoints.createInput(copy, lo_occ, None)
        ab.setAsRigidJointMotion()
        try:
            abj = root.asBuiltJoints.add(ab)
            results["J"] = report("J", design, abj, copy, want)
            # an edit: the target point's plane moves up 50; the locator follows its joint, the copy the locator
            adsk.fusion.ConstructionPlaneOffsetDefinition.cast(plane.definition).offset.value = 160 * MM
            design.computeAll()
            results["J edit"] = report("J after the target moves +50 in Z", design, abj, copy,
                                       (-120.0, -100.0, 0.0, 10.0, 100.0, 110.0))
        except RuntimeError as e:
            print("case J: as-built joint raised: %s" % str(e).splitlines()[0])
        print("TURN PROBE 4: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in results.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
