"""Third turned-copy probe, in a throwaway unsaved design (D-118): which rigid joint set-up moves and turns a copy.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe3.py --label "CEILING Engineer"

The second probe's joints all failed to compute ("conflicts with assembly relationships"), every one made with both
isFlipped and angle set on the input, while the ceiling build's plain placement joints (no flip, no angle, in a
sub-component) computed in every frame sample. Each case here gets its own fresh copy of a 20 x 10 x 10 block that
sits off its component's origin (X 100 to 120, Y 0 to 10, Z 50 to 60), and nothing is deleted:

  A  plain joint, copy origin -> root sketch point at (0, 0, 110), no flip, no angle set
  B  as A, angle 180 deg only
  C  as A, isFlipped only
  D  as A, isFlipped and angle 0 deg (the second probe's first case)
  E  as B, but the point's sketch on an XZ plane (offset 10 in Y): the joint's axis is then Y
  F  as A, inside a sub-component, with the point's sketch in that sub-component (the build's set-up)
  G  as B, inside the sub-component

For each it prints the joint's health and message and the copy's rotation, move and box after Design.computeAll().
A turn about Y sends the block to X -120..-100, Z 50..60 for an origin at (0, 0, 110) (case B, D) or with E's point
at (0, 10, 0), Y -10..0 for a turn about Y... the rotation matrix printed is what matters. Closes without saving.
"""

import adsk.core
import adsk.fusion

MM = 0.1


def bbox_mm(body):
    b = body.boundingBox
    return tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                            b.minPoint.z, b.maxPoint.z))


def place_of(occ):
    m = occ.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 4) for c in range(3)) for r in range(3))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    return rot, move, bbox_mm(occ.bRepBodies.item(0))


def point_on(parent, plane_kind, offset_mm, x_mm, y_mm):
    """A sketch point in `parent`, on its XY plane offset in Z, or its XZ plane offset in Y; sketch coords x, y."""
    base = parent.xYConstructionPlane if plane_kind == "xy" else parent.xZConstructionPlane
    pin = parent.constructionPlanes.createInput()
    pin.setByOffset(base, adsk.core.ValueInput.createByReal(offset_mm * MM))
    plane = parent.constructionPlanes.add(pin)
    sk = parent.sketches.add(plane)
    return sk.sketchPoints.add(adsk.core.Point3D.create(x_mm * MM, y_mm * MM, 0))


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
        sub_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        sub = sub_occ.component
        sub.name = "PROBE FRAME"
        cases = [("A", root, "xy", 110, None, None), ("B", root, "xy", 110, None, "180 deg"),
                 ("C", root, "xy", 110, True, None), ("D", root, "xy", 110, True, "0 deg"),
                 ("E", root, "xz", 10, None, "180 deg"), ("F", sub, "xy", 110, None, None),
                 ("G", sub, "xy", 110, None, "180 deg")]
        moved = []
        for tag, parent, kind, off, flip, angle in cases:
            copy = parent.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            pt = point_on(parent, kind, off, 0, 0)
            g_occ = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(copy))
            g_par = adsk.fusion.JointGeometry.createByPoint(pt)
            ji = parent.joints.createInput(g_occ, g_par)
            ji.setAsRigidJointMotion()
            if flip is not None:
                ji.isFlipped = flip
            if angle is not None:
                ji.angle = adsk.core.ValueInput.createByString(angle)
            try:
                j = parent.joints.add(ji)
            except RuntimeError as e:
                print("case %s: joints.add raised: %s" % (tag, str(e).splitlines()[0]))
                continue
            design.computeAll()
            adsk.doEvents()
            rot, move, box = place_of(copy)
            ok = j.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
            msg = (j.errorOrWarningMessage or "").replace("\n", " ")[:110]
            print("case %s (%s, %s plane +%g, flip %s, angle %s): healthy %s%s" % (
                tag, "sub-component" if parent is sub else "root", kind.upper(), off, flip, angle, ok,
                "" if ok else " (%s)" % msg))
            print("    rotation %s move %s box %s" % (rot, move, box))
            if ok and move != (0.0, 0.0, 0.0):
                moved.append(tag)
        print("TURN PROBE 3: cases whose joint computed and moved the copy: %s" % (", ".join(moved) or "none"))
    finally:
        doc.close(False)
        print("probe design closed without saving")
