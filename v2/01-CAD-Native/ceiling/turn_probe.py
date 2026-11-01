"""Probe, in a throwaway unsaved design, how a rigid joint turns a copy of a component (D-118: prove the
method on a sample before the ceiling build uses it for C2's common members, ceiling_build.place_turned).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe.py --label "CEILING Engineer"

Makes a new design (never saved), a component with a 20 x 10 x 10 mm block off its origin (X 100 to 120,
Y 0 to 10, Z 50 to 60), and a copy of it joined, as the build joins them, from the copy's origin to a sketch
point: (0, 0, 110), where a turn about Y through the block's mid height sends the origin, and (0, 10, 0) for a
turn about Z through its mid width. For each joint flip and angle it prints the copy's rotation and the block's
box, then which setting gives each turn, so place_turned's read-back is known to find one. Closes the design
without saving whatever happens.

Second probe (2026-11-01): the first fixed run read every copy unmoved (identity, not even the move to the
point), so the copy's place is read three times after each joint: at once, after adsk.doEvents(), and after
Design.computeAll(), with the joint's health; the build reads it the first way that shows the joint's effect.
"""

import adsk.core
import adsk.fusion

MM = 0.1
WANT = {"y": ((-1, 0, 0), (0, 1, 0), (0, 0, -1)), "z": ((-1, 0, 0), (0, -1, 0), (0, 0, 1))}
TARGET = {"y": (0.0, 0.0, 110.0), "z": (0.0, 10.0, 0.0)}
BOX = {"y": (-120.0, -100.0, 0.0, 10.0, 50.0, 60.0), "z": (-120.0, -100.0, 0.0, 10.0, 50.0, 60.0)}


def bbox_mm(body):
    b = body.boundingBox
    return tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                            b.minPoint.z, b.maxPoint.z))


def place_of(occ):
    m = occ.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 6) for c in range(3)) for r in range(3))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    return rot, move, bbox_mm(occ.bRepBodies.item(0))


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
        print("block in its own place:", bbox_mm(occ.bRepBodies.item(0)))
        found, when = {}, {}
        for axis in ("y", "z"):
            copy = root.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            print("copy %s: grounded %s" % (axis.upper(), copy.isGrounded))
            tx, ty, tz = TARGET[axis]
            pin = root.constructionPlanes.createInput()
            pin.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(tz * MM))
            plane = root.constructionPlanes.add(pin)
            psk = root.sketches.add(plane)
            pt = psk.sketchPoints.add(adsk.core.Point3D.create(tx * MM, ty * MM, 0))
            for flip in (False, True):
                for angle in ("0 deg", "90 deg", "180 deg"):
                    # the flip and angle go on the joint's input: a made joint can't be edited without rolling the
                    # timeline back (the first probe, 2026-11-01), so each setting gets a fresh joint
                    g_occ = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(copy))
                    g_par = adsk.fusion.JointGeometry.createByPoint(pt)
                    ji = root.joints.createInput(g_occ, g_par)
                    ji.setAsRigidJointMotion()
                    ji.isFlipped = flip
                    ji.angle = adsk.core.ValueInput.createByString(angle)
                    j = root.joints.add(ji)
                    reads = [("at once", place_of(copy))]
                    adsk.doEvents()
                    reads.append(("after doEvents", place_of(copy)))
                    design.computeAll()
                    reads.append(("after computeAll", place_of(copy)))
                    print("turn about %s: flip %-5s angle %-7s joint health %s %s" % (
                        axis.upper(), flip, angle, j.healthState, j.errorOrWarningMessage or ""))
                    for label, (rot, move, box) in reads:
                        ok = all(abs(rot[r][c] - WANT[axis][r][c]) < 1e-6 for r in range(3) for c in range(3))
                        print("    %-17s rotation %s move %s box %s%s" % (label, rot, move, box,
                                                                       "  <- the turn" if ok else ""))
                        if ok and axis not in found:
                            found[axis], when[axis] = (flip, angle, box), label
                    j.deleteMe()
                    adsk.doEvents()
        for axis in ("y", "z"):
            if axis in found:
                flip, angle, box = found[axis]
                print("TURN %s: flip %s, angle %s, read %s; the block lands at %s (want %s)" % (
                    axis.upper(), flip, angle, when[axis], box, BOX[axis]))
            else:
                print("TURN %s: no flip and angle gives it" % axis.upper())
        print("TURN PROBE:", "PASS" if len(found) == 2 and all(
            max(abs(a - b) for a, b in zip(found[a][2], BOX[a])) < 1e-3 for a in found) else "FAIL")
    finally:
        doc.close(False)
        print("probe design closed without saving")
