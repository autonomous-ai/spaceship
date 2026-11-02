"""Method test for D-117 and D-120 before WALL's frames are rebuilt (D-118: prove a method on a sample first).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/d120_method_test.py --label "WALL Engineer: D-120 method test"

Runs in a NEW, UNSAVED document that it makes and closes without saving (nothing reaches the cloud), then
gives back the document that was active. On a small frame corner it tries the four things the rework needs and
prints what it finds:
  1. members as their own components: a 20 x 40 rail and a 20 x 40 stile, hollow (1.2 wall), each mitred at
     the shared outer corner by one fully constrained triangle cut (the mitre runs outer corner to inner corner);
     a 40 x 40 stile meeting a 20 x 40 rail at the other corner (26.57 / 63.43 degrees off square);
  2. a stud as one component placed n times by a pattern of its occurrence, driven by parameters;
  3. a hardware part as one component, its first copy held in a hole by a rigid joint to the hole's edge,
     the second copy by a joint to the patterned hole;
  4. a parameter edit (length, pitch, hole position): every member, stud copy and hardware copy follows, and
     every feature and joint stays healthy; then the edit is undone and the boxes come back.
"""

import traceback

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
MM = 0.1


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def bbox(entity):
    b = entity.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def plane_x(comp, design, expr, label):
    """A construction plane normal to X at expr (the YZ origin plane's normal is +X)."""
    if abs(ev(design, expr)) < 1e-9:
        return comp.yZConstructionPlane
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, vi(expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - " + label
    return pl


def dim_point(sk, pt, model_axis, expr):
    """Dimension a sketch point from the sketch origin along the sketch axis that a model axis maps to."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*{"y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]))
    horiz = abs(e.x - o.x) > abs(e.y - o.y)
    g = pt.geometry
    if abs(g.x if horiz else g.y) < 1e-9:
        (sk.geometricConstraints.addVerticalPoints if horiz else sk.geometricConstraints.addHorizontalPoints)(
            pt, sk.originPoint)
        return
    ori = (adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation if horiz else
           adsk.fusion.DimensionOrientations.VerticalDimensionOrientation)
    sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, ori, adsk.core.Point3D.create(g.x + 0.3, g.y + 0.3, 0)
                                             ).parameter.expression = "abs(%s)" % expr


def poly_on_x(design, comp, x_expr, pts, label):
    """A fully constrained closed polygon on a plane normal to X: pts = [(y_expr, z_expr), ...]."""
    pl = plane_x(comp, design, x_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - " + label
    x = ev(design, x_expr)
    sp = [sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(
        x * MM, ev(design, y) * MM, ev(design, z) * MM))) for y, z in pts]
    lines = sk.sketchCurves.sketchLines
    for i in range(len(sp)):
        lines.addByTwoPoints(sp[i], sp[(i + 1) % len(sp)])
    for p, (y, z) in zip(sp, pts):
        dim_point(sk, p, "y", y)
        dim_point(sk, p, "z", z)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk


def box(design, comp, label, xr, yr, zr, op="new", body=None):
    """Axis-aligned box: a rectangle on a plane normal to X at xr[0] (corners dimensioned), extruded +X."""
    sk = poly_on_x(design, comp, xr[0], [(yr[0], zr[0]), (yr[1], zr[0]), (yr[1], zr[1]), (yr[0], zr[1])], label)
    ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
           "cut": adsk.fusion.FeatureOperations.CutFeatureOperation}
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), ops[op])
    ei.setDistanceExtent(False, vi("(%s) - (%s)" % (xr[1], xr[0])))
    if body is not None:
        ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = ("CUT - " if op == "cut" else "EXTRUDE - ") + label
    return f


def tube(design, comp, label, yr, zr, along, t="t"):
    """Hollow member, depth X 0..d: outer box, then the bore cut through its length."""
    b = box(design, comp, label, ("0 mm", "d"), yr, zr).bodies.item(0)
    if along == "y":
        box(design, comp, label + " BORE", (t, "d - %s" % t), yr, ("(%s) + %s" % (zr[0], t), "(%s) - %s" % (zr[1], t)),
            "cut", b)
    else:
        box(design, comp, label + " BORE", (t, "d - %s" % t), ("(%s) + %s" % (yr[0], t), "(%s) - %s" % (yr[1], t)), zr,
            "cut", b)
    b.name = label
    return b


def mitre(design, comp, body, tri, label):
    """Cut one mitre: a triangle (three (y, z) corners) cut through the member's depth."""
    sk = poly_on_x(design, comp, "0 mm - 1 mm", tri, label)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                   adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setDistanceExtent(False, vi("d + 2 mm"))
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - MITRE " + label
    return f


def member(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ


def run(_context):
    app = adsk.core.Application.get()
    before = app.activeDocument
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    out = []
    try:
        test(app, doc, out)
    except Exception:                                    # noqa: BLE001
        out.append("TEST|ERROR " + traceback.format_exc()[-1500:])
    finally:
        print("\n".join(out))
        doc.close(False)                                 # never saved
        if before is not None and before.isValid:
            before.activate()


def test(app, doc, out):
    p = out.append
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = design.rootComponent
    up = design.userParameters
    for n, e in (("L", "600 mm"), ("H", "400 mm"), ("w", "20 mm"), ("wb", "40 mm"), ("d", "40 mm"), ("t", "1.2 mm"),
                 ("pitch", "150 mm"), ("n", "2"), ("hole_y", "100 mm"), ("hole_p", "300 mm")):
        up.add(n, vi(e), "mm" if "mm" in e else "", "test")
    # 1. members as components, mitred at the corners (frame in the YZ plane, depth along X)
    rail_o, stf_o, stb_o = member(root, "MEMBER - RAIL BOTTOM"), member(root, "MEMBER - STILE FRONT"), \
        member(root, "MEMBER - STILE BACK 40 X 40")
    rail = tube(design, rail_o.component, "RAIL BOTTOM", ("0 mm", "L"), ("0 mm", "w"), "y")
    stf = tube(design, stf_o.component, "STILE FRONT", ("0 mm", "w"), ("0 mm", "H"), "z")
    stb = tube(design, stb_o.component, "STILE BACK", ("L - wb", "L"), ("0 mm", "H"), "z")
    # front corner, equal sizes, 45 degrees: the mitre runs from the outer corner (0, 0) to the inner (w, w)
    mitre(design, rail_o.component, rail, [("0 mm - 1 mm", "0 mm - 1 mm"), ("0 mm - 1 mm", "w + 1 mm"), ("w", "w + 1 mm"),
                                           ("w", "w")], "RAIL FRONT")
    mitre(design, stf_o.component, stf, [("0 mm - 1 mm", "0 mm - 1 mm"), ("w + 1 mm", "0 mm - 1 mm"), ("w + 1 mm", "w"),
                                         ("w", "w")], "STILE FRONT BOTTOM")
    # back corner, a 40 wide stile on a 20 high rail: outer (L, 0) to inner (L - wb, w)
    # the polygon's closing edge lies on the mitre line itself: its ends are on the line extended past both
    # corners (z = w * (L - y) / wb), so the cut passes exactly through the outer and inner corners
    mitre(design, rail_o.component, rail, [("L + 2 mm", "0 mm - 2 mm * w / wb"), ("L + 2 mm", "w + 1 mm"),
                                           ("L - wb", "w + 1 mm"), ("L - wb", "w")], "RAIL BACK")
    mitre(design, stb_o.component, stb, [("L + 2 mm", "0 mm - 2 mm * w / wb"), ("L + 2 mm", "0 mm - 5 mm"),
                                         ("L - wb - 1 mm", "0 mm - 5 mm"), ("L - wb - 1 mm", "w + 1 mm * w / wb")],
           "STILE BACK BOTTOM")
    # 2. a stud: one component, placed n times by a pattern of its occurrence
    stud_o = member(root, "MEMBER - STUD")
    tube(design, stud_o.component, "STUD", ("pitch", "pitch + w"), ("w", "H"), "z")
    coll = adsk.core.ObjectCollection.create()
    coll.add(stud_o)
    pin = root.features.rectangularPatternFeatures.createInput(coll, root.yConstructionAxis, vi("n"), vi("pitch"),
                                                               adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    pin.setDirectionTwo(root.zConstructionAxis, vi("1"), vi("1 mm"))
    spat = root.features.rectangularPatternFeatures.add(pin)
    spat.name = "PATTERN - STUD COPIES"
    # 3. a hole pattern in the rail's bottom wall and a hardware part held in each hole by a rigid joint
    rc = rail_o.component
    hsk = rc.sketches.add(rc.xYConstructionPlane)
    hsk.name = "HOLE CENTRE - TEST"
    hp = hsk.sketchPoints.add(hsk.modelToSketchSpace(adsk.core.Point3D.create(ev(design, "d / 2") * MM,
                                                                           ev(design, "hole_y") * MM, 0)))
    hsk.sketchDimensions.addDistanceDimension(hsk.originPoint, hp, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                                              adsk.core.Point3D.create(1, 1, 0)).parameter.expression = "d / 2"
    hsk.sketchDimensions.addDistanceDimension(hsk.originPoint, hp, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,
                                              adsk.core.Point3D.create(1, 2, 0)).parameter.expression = "hole_y"
    p("TEST|hole sketch fully constrained: %s" % hsk.isFullyConstrained)
    hin = rc.features.holeFeatures.createSimpleInput(vi("7 mm"))
    hin.setPositionBySketchPoint(hp)
    hin.setDistanceExtent(vi("t + 1 mm"))
    hin.isDefaultDirection = False
    hin.participantBodies = [rail]
    hole = rc.features.holeFeatures.add(hin)
    hole.name = "HOLE - TEST"
    hc = adsk.core.ObjectCollection.create()
    hc.add(hole)
    hpin = rc.features.rectangularPatternFeatures.createInput(hc, rc.yConstructionAxis, vi("2"), vi("hole_p"),
                                                              adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    hpin.setDirectionTwo(rc.zConstructionAxis, vi("1"), vi("1 mm"))
    hpat = rc.features.rectangularPatternFeatures.add(hpin)
    hpat.name = "PATTERN - TEST HOLES"
    hw_o = member(root, "838003 HARDWARE - TEST RIVNUT")
    hwc = hw_o.component
    csk = hwc.sketches.add(hwc.xYConstructionPlane)
    circ = csk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.475)
    csk.sketchDimensions.addDiameterDimension(circ, adsk.core.Point3D.create(1, 1, 0)).parameter.expression = "9.5 mm"
    csk.geometricConstraints.addCoincident(circ.centerSketchPoint, csk.originPoint)
    ei = hwc.features.extrudeFeatures.createInput(csk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setDistanceExtent(False, vi("10 mm"))
    hwb = hwc.features.extrudeFeatures.add(ei).bodies.item(0)
    hwb.name = "RIVNUT"

    def circ_edges(body, dia, z=None):
        found = []
        for e in body.edges:
            g = e.geometry
            if g.objectType == adsk.core.Circle3D.classType() and abs(adsk.core.Circle3D.cast(g).radius * 20 - dia) < 0.01:
                if z is None or abs(adsk.core.Circle3D.cast(g).center.z * 10 - z) < 0.01:
                    found.append(e)
        return found
    rail_now = rail_o.component.bRepBodies.item(0)
    hole_edges = sorted(circ_edges(rail_now, 7.0, z=0.0), key=lambda e: adsk.core.Circle3D.cast(e.geometry).center.y)
    p("TEST|hole edges on the bottom face: %d" % len(hole_edges))
    hw_edge = circ_edges(hwb, 9.5, z=0.0)[0]
    joints = []
    occs = [hw_o]
    second = root.occurrences.addExistingComponent(hwc, adsk.core.Matrix3D.create())
    occs.append(second)
    for i, occ in enumerate(occs):
        g_hw = adsk.fusion.JointGeometry.createByCurve(hw_edge.createForAssemblyContext(occ),
                                                       adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
        g_hole = adsk.fusion.JointGeometry.createByCurve(hole_edges[i].createForAssemblyContext(rail_o),
                                                         adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
        jin = root.joints.createInput(g_hw, g_hole)
        jin.setAsRigidJointMotion()
        if i == 1:
            jin.offset = vi("1.5 mm")             # a washer's thickness under the head, as a joint offset
        j = root.joints.add(jin)
        j.name = "JOINT - RIVNUT %d IN ITS HOLE" % (i + 1)
        joints.append(j)
        p("TEST|joint %d: health %s; rivnut copy box %s (the rail's bottom face is Z 0; the head should hang below it)" % (
            i + 1, j.healthState, bbox(occ.bRepBodies.item(0))))
    # 3b. the plan for the panels: one joint for the first copy, then a pattern of that copy like the holes
    hw3 = root.occurrences.addExistingComponent(hwc, adsk.core.Matrix3D.create())
    g_hw = adsk.fusion.JointGeometry.createByCurve(hw_edge.createForAssemblyContext(hw3),
                                                   adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
    g_hole = adsk.fusion.JointGeometry.createByCurve(hole_edges[0].createForAssemblyContext(rail_o),
                                                     adsk.fusion.JointKeyPointTypes.CenterKeyPoint)
    jin = root.joints.createInput(g_hw, g_hole)
    jin.setAsRigidJointMotion()
    jin.offset = vi("20 mm")                      # lifted clear of the first copy, so the two don't overlap
    j3 = root.joints.add(jin)
    j3.name = "JOINT - RIVNUT 3 (PATTERN SEED)"
    pc = adsk.core.ObjectCollection.create()
    pc.add(hw3)
    ppin = root.features.rectangularPatternFeatures.createInput(pc, root.yConstructionAxis, vi("2"), vi("hole_p"),
                                                                adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    ppin.setDirectionTwo(root.zConstructionAxis, vi("1"), vi("1 mm"))
    ppat = root.features.rectangularPatternFeatures.add(ppin)
    ppat.name = "PATTERN - RIVNUT COPIES FROM THE SEED"
    p("TEST|seed joint %s, copy pattern %s; occurrences of the rivnut part: %d" % (
        j3.healthState, ppat.healthState, root.allOccurrencesByComponent(hwc).count))
    # 4. report, edit, report, undo
    def snap():
        rows = {}
        for occ in root.allOccurrences:
            for b in occ.bRepBodies:
                rows["%s / %s" % (occ.name, b.name)] = bbox(b)
        return rows

    def health():
        tl = design.timeline
        bad = ["%s (%s)" % (tl.item(i).name, tl.item(i).errorOrWarningMessage) for i in range(tl.count)
               if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        jb = [j.name for j in root.joints if j.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
        return bad, jb, loose
    a = snap()
    p("TEST|before: components %d, occurrences %d, joints %d, health %s" % (
        design.allComponents.count, root.allOccurrences.count, root.joints.count, health()))
    for k in sorted(a):
        p("TEST|%s %s" % (k, a[k]))
    for n, e in (("L", "700 mm"), ("pitch", "170 mm"), ("hole_y", "120 mm"), ("hole_p", "350 mm")):
        up.itemByName(n).expression = e
    adsk.doEvents()
    b = snap()
    p("TEST|after the edit (L 700, pitch 170, hole_y 120, hole_p 350): health %s" % (health(),))
    for k in sorted(b):
        p("TEST|%s %s -> %s" % (k, a.get(k), b[k]))
    for n, e in (("L", "600 mm"), ("pitch", "150 mm"), ("hole_y", "100 mm"), ("hole_p", "300 mm")):
        up.itemByName(n).expression = e
    adsk.doEvents()
    c = snap()
    p("TEST|undo: every box back: %s; health %s" % (all(c.get(k) == v for k, v in a.items()), health()))
