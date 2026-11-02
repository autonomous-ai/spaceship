"""Seventh turned-copy probe, in a throwaway unsaved design (D-118).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe7.py --label "CEILING Engineer"

Probe 6 (2026-11-01 08:15), in the build's own structure: every joint on a copy of a block whose first occurrence
was built in place failed ("conflicts with assembly relationships"); a new plate's first occurrence, placed by its
own joint, reported healthy but did not move; a copy of the plate moved, but turned 45 deg for an input of 135.
Probe 5 read isGroundToParent True on new occurrences: Fusion grounds an occurrence to its parent, and a joint
that would move it then conflicts. This probe reads that flag on every new occurrence, turns it off before each
joint, and maps the joint's angle to the turn it gives.

Inside one FRAME component (as build_frame), the block's first occurrence built in place (as C1's side member):
  P  a copy, ground to parent off, a plain rigid joint from its origin to a FRAME sketch point at (0, 0, 110)
  Q  as P, angle 180 deg on the input (a turn about Z)
  T  as P, flipped, angle 180 (the turn about Y that C2's side member needs); T' flipped, angle 0
  R  a new plate component, its first occurrence ground to parent off, a joint with angle 0
  S  copies of the plate, ground to parent off, angles 0, 45, 90, 135 and 180 deg: the turn about Z each gives
Each prints the flag as made, the joint's health and the occurrence's turn and move after Design.computeAll().
Closes without saving.
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1


def block(comp, x0, x1, y0, y1, z0, h):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(x0 * MM, y0 * MM, 0),
                                                     adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
    ext = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(h * MM)),
                         adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z0 * MM))
    comp.features.extrudeFeatures.add(ext)


def point(fc, z_mm):
    pin = fc.constructionPlanes.createInput()
    pin.setByOffset(fc.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_mm * MM))
    sk = fc.sketches.add(fc.constructionPlanes.add(pin))
    return sk.sketchPoints.add(adsk.core.Point3D.create(0, 0, 0))


def unground(occ):
    """The occurrence's ground-to-parent flag as made, then set off; returns 'was X, now Y' (or the error)."""
    try:
        was = occ.isGroundToParent
        occ.isGroundToParent = False
        return "ground to parent was %s, now %s" % (was, occ.isGroundToParent)
    except Exception as e:      # noqa: BLE001  (a probe: report whatever Fusion says)
        return "ground to parent: %s" % str(e).replace("\n", " ")[:80]


def joint(fc, comp, occ, pt, flip=False, angle=None):
    g = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(occ))
    ji = fc.joints.createInput(g, adsk.fusion.JointGeometry.createByPoint(pt))
    ji.setAsRigidJointMotion()
    if flip:
        ji.isFlipped = True
    if angle is not None:
        ji.angle = adsk.core.ValueInput.createByString(angle)
    return fc.joints.add(ji)


def report(tag, design, j, occ, flag):
    design.computeAll()
    adsk.doEvents()
    m = occ.transform2
    rz = math.degrees(math.atan2(m.getCell(1, 0), m.getCell(0, 0)))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    ok = j.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    msg = "" if ok else " (%s)" % (j.errorOrWarningMessage or "").replace("\n", " ")[:80]
    print("case %s: %s; healthy %s%s; turn about Z %.1f deg, Z axis to Z %.3f, X axis to X %.3f; move %s" % (
        tag, flag, ok, msg, rz, m.getCell(2, 2), m.getCell(0, 0), move))
    return ok and abs(move[2] - 110.0) < 1e-3, rz, m.getCell(2, 2)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        frame = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        fc = frame.component
        fc.name = "PROBE FRAME"
        print("case A: the frame's occurrence in root: %s" % unground(frame))
        first = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = first.component
        comp.name = "PROBE MEMBER"
        block(comp, 100, 120, 0, 10, 50, 10)                   # built in place, as C1's side member
        print("case A: the block's first occurrence (left grounded, as built in place): ground to parent %s" %
              first.isGroundToParent)
        res = {}
        for tag, flip, angle in (("P plain", False, None), ("Q angle 180", False, "180 deg"),
                                 ("T flip + angle 180", True, "180 deg"), ("T' flip + angle 0", True, "0 deg")):
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            flag = unground(c)
            res[tag] = report(tag, design, joint(fc, comp, c, point(fc, 110), flip, angle), c, flag)
        plate = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        pcomp = plate.component
        pcomp.name = "PROBE PLATE"
        block(pcomp, 0, 28, -1, 1, -20, 40)
        flag = unground(plate)
        res["R plate, angle 0"] = report("R plate, angle 0", design, joint(fc, pcomp, plate, point(fc, 110), False, "0 deg"),
                                         plate, flag)
        for a in (0, 45, 90, 135, 180):
            c = fc.occurrences.addExistingComponent(pcomp, adsk.core.Matrix3D.create())
            flag = unground(c)
            tag = "S plate copy, angle %d" % a
            res[tag] = report(tag, design, joint(fc, pcomp, c, point(fc, 110), False, "%d deg" % a), c, flag)
        print("TURN PROBE 7: %s" % "; ".join("%s %s (Z turn %.1f, Z axis %.0f)" % (k, "MOVED" if v[0] else "no", v[1], v[2])
                                             for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
