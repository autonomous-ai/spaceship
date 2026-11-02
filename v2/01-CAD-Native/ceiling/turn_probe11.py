"""Eleventh turned-copy probe, in a throwaway unsaved design (D-118).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/turn_probe11.py --label "CEILING Engineer"

Probe 9 (2026-11-01 08:33) placed copies right, read in the design, with the frame's first child out of the way of
Fusion's auto-grounding: plain, angle 180 (about Z) and flip + angle 180 (about Y). The ceiling frames' mitre plates
turn by other angles about Z (45, 135, -63.43 and -116.57 deg at the corners). This probe, built as probe 10 (the
first occurrence's ground to parent turned off), places plate-like copies with those angles on the joint's input and
reads each one's turn and box in the design.
"""

import adsk.core
import adsk.fusion

MM = 0.1
import math


def rz(deg):
    c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return ((c, -s_, 0.0), (s_, c, 0.0), (0.0, 0.0, 1.0))


def turned_box(deg, z):
    """The block (X 100..120, Y 0..10, Z 50..60) turned deg about Z, then up z: its box."""
    r = rz(deg)
    pts = [(x, y) for x in (100, 120) for y in (0, 10)]
    xs = [r[0][0] * x + r[0][1] * y for x, y in pts]
    ys = [r[1][0] * x + r[1][1] * y for x, y in pts]
    return (round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3), 50 + z, 60 + z)


WANT = {   # tag: (rotation rows, box in the design: x0, x1, y0, y1, z0, z1)
    "F": (((1, 0, 0), (0, 1, 0), (0, 0, 1)), (100, 120, 0, 10, 160, 170)),
    "P": (((1, 0, 0), (0, 1, 0), (0, 0, 1)), (100, 120, 0, 10, 260, 270)),
    "Q": (((-1, 0, 0), (0, -1, 0), (0, 0, 1)), (-120, -100, -10, 0, 360, 370)),
    "T": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 350, 360)),
    "U": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 450, 460)),
    "N": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 550, 560)),
    "N after +50": (((-1, 0, 0), (0, 1, 0), (0, 0, -1)), (-120, -100, 0, 10, 600, 610)),
}
ANGLES = [("A45", 45.0, 610), ("A135", 135.0, 710), ("A-63.43", -63.43, 810), ("A-116.57", -116.57, 910)]
for _t, _a, _z in ANGLES:
    WANT[_t] = (rz(_a), turned_box(_a, _z))


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
        max(abs(a - b) for a, b in zip(box, want_box)) < 0.01
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
                                    ("T", 410, True, "180 deg")) + tuple((t, z, False, "%g deg" % a) for t, a, z in ANGLES):
            c = fc.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
            print("made: copy %s %s" % (tag, flag(c)))
            _p, pt = target(fc, "%d mm" % z)
            res[tag] = report(tag, design, frame, c, joint(fc, comp, c, pt, flip, angle))
        print("TURN PROBE 11: %s" % ", ".join("%s %s" % (k, "PASS" if v else "no") for k, v in res.items()))
    finally:
        doc.close(False)
        print("probe design closed without saving")
