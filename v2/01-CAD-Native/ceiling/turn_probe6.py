"""Sixth turned-copy probe, in a throwaway unsaved design (D-118): the ceiling build's own structure. Probes 2 to 5 put
the block's first occurrence in the design's root, where Fusion grounds an occurrence to its parent, and every joint on
a copy failed ("conflicts with assembly relationships"); the build keeps a part's first occurrence inside a frame
component, where its plain placement joints on copies computed in every frame sample.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe6.py --label "CEILING Engineer"

Inside one FRAME component (as build_frame), the block's first occurrence built in place (as C1's side member):
  P  a copy, a plain rigid joint from its origin to a FRAME sketch point at (0, 0, 110)
  Q  a copy, the joint's angle 180 deg on its input (a turn about Z)
  T  a copy, flipped and angle 180 on the input (the turn about Y that C2's side member needs)
  R  a new plate-like component (its first occurrence) placed by a joint with angle 45 deg
  S  a copy of R's component, angle 135 deg
Each prints the joint's health and the copy's rotation and box after Design.computeAll(). Closes without saving.
"""

import math

import adsk.core
import adsk.fusion

MM = 0.1


def bbox_mm(body):
    b = body.boundingBox
    return tuple(round(v / MM, 3) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y,
                                            b.minPoint.z, b.maxPoint.z))


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


def joint(fc, comp, occ, pt, flip=False, angle=None):
    g = adsk.fusion.JointGeometry.createByPoint(comp.originConstructionPoint.createForAssemblyContext(occ))
    ji = fc.joints.createInput(g, adsk.fusion.JointGeometry.createByPoint(pt))
    ji.setAsRigidJointMotion()
    if flip:
        ji.isFlipped = True
    if angle:
        ji.angle = adsk.core.ValueInput.createByString(angle)
    return fc.joints.add(ji)


def report(tag, design, j, occ, want_rot):
    design.computeAll()
    adsk.doEvents()
    m = occ.transform2
    rot = tuple(tuple(round(m.getCell(r, c), 4) for c in range(3)) for r in range(3))
    move = tuple(round(m.getCell(r, 3) / MM, 3) for r in range(3))
    ok = j.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    msg = "" if ok else " (%s)" % (j.errorOrWarningMessage or "").replace("\n", " ")[:80]
    good = ok and all(abs(rot[r][c] - want_rot[r][c]) < 1e-4 for r in range(3) for c in range(3)) and \
        abs(move[2] - 110.0) < 1e-3
    print("case %s: healthy %s%s; rotation %s move %s box %s -> %s" % (
        tag, ok, msg, rot, move, bbox_mm(occ.bRepBodies.item(0)), "RIGHT" if good else "no"))
    return good


def rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        fc = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        fc.name = "PROBE FRAME"
        first = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = first.component
        comp.name = "PROBE MEMBER"
        block(comp, 100, 120, 0, 10, 50, 10)                   # built in place, as C1's side member
        res = {}
        for tag, flip, angle, want in (("P plain", False, None, rz(0)), ("Q angle 180", False, "180 deg", rz(180)),
                                       ("T flip + angle 180", True, "180 deg", ((-1, 0, 0), (0, 1, 0), (0, 0, -1)))):
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            res[tag] = report(tag, design, joint(fc, comp, c, point(fc, 110), flip, angle), c, want)
        if not res["T flip + angle 180"]:          # the flip may turn about the joint's X instead: try angle 0
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            res["T' flip + angle 0"] = report("T' flip + angle 0", design, joint(fc, comp, c, point(fc, 110), True, "0 deg"),
                                              c, ((-1, 0, 0), (0, 1, 0), (0, 0, -1)))
        plate = fc.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        pcomp = plate.component
        pcomp.name = "PROBE PLATE"
        block(pcomp, 0, 28, -1, 1, -20, 40)
        res["R plate, angle 45"] = report("R plate, angle 45", design, joint(fc, pcomp, plate, point(fc, 110), False, "45 deg"),
                                          plate, rz(45))
        p2 = fc.occurrences.addExistingComponent(pcomp, adsk.core.Matrix3D.create())
        res["S plate copy, angle 135"] = report("S plate copy, angle 135", design,
                                                joint(fc, pcomp, p2, point(fc, 110), False, "135 deg"), p2, rz(135))
        print("TURN PROBE 6: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
