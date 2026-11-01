"""Spaceship (FocusPod v2) AIR P01 (D-60, D-61): native, parameter-driven Fusion design.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/air/air_build.py --label "CEILING Engineer" \
        --doc 610000_P01_AIR_CAD --doc-new --arg into_active=1 --arg save=1 --arg export=1 --close --discard

One design, 610000 AIR, in the pod system:
  610101 AIR - AIR COLUMN: front and left faces (ACP + felt), 3 corner angles, fill,
         the kick grille, the sensor hub zone (HOLD) and the supply cartridge
  610201 AIR - SOFFIT: underside (top band's dark tone) and front face, fill, the exhaust
         grille, the exhaust cartridge and the exhaust fan box with its 2 fans
  610401 AIR - SUPPLY FAN BOX with its 2 fans and the transition to the column (HOLD shape)
  611501 AIR - INTAKE RISER and its transition into the fan box (HOLD shape)
  611601 AIR - ROOF SLEEVE and 611602 AIR - ROOF GRILLE through the right outer ceiling panel
The cartridge is one part (610301) for both paths; it lies upright in the column and along X
in the soffit, so it is modelled twice in place, both from the same parameters.

Every size is a user parameter (air_model.py): the skeleton's, read from its CSV, the
ceiling's, and the AIR sizes of D-61 and the air report. Checks fail the run: timeline
health, sketches, clashes over 1 mm3, and every body against its layout box.
"""

import importlib
import os
import sys
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
_CEIL = os.path.normpath(os.path.join(HERE, "..", "ceiling"))
# Fusion keeps modules loaded between runs, and a run from another worktree may have loaded its
# own copy of these (the ceiling's own runs load the ceiling model too): drop any copy from
# another folder and put this worktree's folders first, so the imports below take its files
for _n, _d in (("air_model", HERE), ("air_checks", HERE), ("ceiling_model", _CEIL), ("ceiling_checks", _CEIL),
               ("ceiling_build", _CEIL), ("ceiling_exports", _CEIL)):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != _d:
        del sys.modules[_n]
for _d in (_CEIL, HERE):
    if _d in sys.path:
        sys.path.remove(_d)
    sys.path.insert(0, _d)
import ceiling_model  # noqa: E402
importlib.reload(ceiling_model)
import ceiling_checks  # noqa: E402,F401
importlib.reload(ceiling_checks)
import ceiling_build as CB  # noqa: E402  (tested helpers: sketches, boxes, joints, checks)
importlib.reload(CB)
import air_model as A  # noqa: E402
importlib.reload(A)
import air_checks as K  # noqa: E402
importlib.reload(K)

DOC_NAME = "610000_%s_AIR_CAD" % A.REV
F3D_REL = "v2/01-CAD-Native/air/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/air/610000_%s_AIR_STEP.step" % A.REV
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation


def new_comp(parent, key):
    pn, name, vn, kind, _mat = A.PARTS[key]
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = "%s %s" % (pn, name)
    c.partNumber = pn
    c.description = "%s | %s | %s | %s" % (name, vn, kind, A.REV)
    return occ, c


def set_material(design, comp, key):
    mk = A.PARTS[key][4]
    if mk is None:
        return
    name, density = A.MATERIALS[mk]
    m = design.materials.itemByName(name)
    if m is None:
        lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
        m = design.materials.addByCopy(lib.materials.itemByName("Steel" if mk == "steel" else "Aluminum"), name)
        adsk.core.FloatProperty.cast(m.materialProperties.itemById("structural_Density")).value = density
    for b in comp.bRepBodies:
        b.material = m


def hollow_open(comp, body, opens, thick, name):
    """Shell a box into a casing, open on the faces `opens` ((axis, -1) is the face at the low end
    along that axis, (axis, 1) the high one): a fan box is open where its air comes in and goes out."""
    coll = adsk.core.ObjectCollection.create()
    for axis, side in opens:
        k = {"x": 0, "y": 1, "z": 2}[axis]
        cands = []
        for f in body.faces:
            if f.geometry.objectType != adsk.core.Plane.classType():
                continue
            n = adsk.core.Plane.cast(f.geometry).normal
            if abs((n.x, n.y, n.z)[k]) > 0.99:
                p = f.pointOnFace
                cands.append(((p.x, p.y, p.z)[k], f))
        if len(cands) != 2:
            raise RuntimeError("%s: expected 2 faces across %s, found %d" % (name, axis, len(cands)))
        cands.sort(key=lambda c: c[0])
        coll.add(cands[0][1] if side < 0 else cands[-1][1])
    si = comp.features.shellFeatures.createInput(coll, False)
    si.insideThickness = CB.vi(thick)
    f = comp.features.shellFeatures.add(si)
    f.name = "SHELL - %s (OPEN WHERE THE AIR PASSES)" % name
    return f


def hollow_axis(comp, body, axis, thick, name):
    ends = []
    for f in body.faces:
        if f.geometry.objectType != adsk.core.Plane.classType():
            continue
        n = f.geometry.normal
        if abs({"x": n.x, "y": n.y, "z": n.z}[axis]) > 0.99:
            ends.append(f)
    if len(ends) != 2:
        raise RuntimeError("%s: expected 2 end faces, found %d" % (name, len(ends)))
    coll = adsk.core.ObjectCollection.create()
    for f in ends:
        coll.add(f)
    si = comp.features.shellFeatures.createInput(coll, False)
    si.insideThickness = CB.vi(thick)
    f = comp.features.shellFeatures.add(si)
    f.name = "SHELL - %s" % name
    return f


def poly_xy_extrude(comp, name, pts, z0, z1, ctx):
    """Closed polygon on the XY plane offset to z0 (corners dimensioned from the origin
    by their expressions), extruded to z1 as a new body named `name`."""
    plane = CB.offset_plane(comp, comp.xYConstructionPlane, z0, "PLANE - %s Z0" % name)
    sk = comp.sketches.add(plane)
    sk.name = "PROFILE - " + name
    vals = [(ctx.ev(x), ctx.ev(y)) for x, y in pts]
    lines = sk.sketchCurves.sketchLines
    verts, edges = [], []
    n = len(vals)
    for i in range(n):
        a = verts[-1] if verts else adsk.core.Point3D.create(vals[0][0] * CB.MM, vals[0][1] * CB.MM, 0)
        b = adsk.core.Point3D.create(vals[i + 1][0] * CB.MM, vals[i + 1][1] * CB.MM, 0) if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(a, b)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    gc, dims = sk.geometricConstraints, sk.sketchDimensions
    for ln in edges:
        p, q = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
        (gc.addHorizontal if abs(p.y - q.y) < 1e-9 else gc.addVertical)(ln)
    # one dimension per distinct x and per distinct y, from the origin
    done_x, done_y = {}, {}
    for (ex, ey), (vx, vy), vp in zip(pts, vals, verts):
        kx, ky = round(vx, 6), round(vy, 6)
        if kx not in done_x:
            done_x[kx] = vp
            g = vp.geometry
            d = dims.addDistanceDimension(sk.originPoint, vp, CB.H, adsk.core.Point3D.create(g.x + 0.3, g.y + 0.7, 0))
            d.parameter.expression = "abs(%s)" % ex
        if ky not in done_y:
            done_y[ky] = vp
            g = vp.geometry
            d = dims.addDistanceDimension(sk.originPoint, vp, CB.V, adsk.core.Point3D.create(g.x + 0.7, g.y + 0.3, 0))
            d.parameter.expression = "abs(%s)" % ey
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), NEW)
    ei.setDistanceExtent(False, CB.vi("(%s) - (%s)" % (z1, z0)))
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - " + name
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def _sketch_axis(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis ('x', 'y' or 'z') maps to on this sketch's plane."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def poly_prism(comp, name, plane_axes, pts, along, a, b, ctx, op=None, bodies=None):
    """A closed polygon on one of the component's origin planes, fully constrained, extruded along the third axis from
    a to b (expressions, a < b). Unlike poly_xy_extrude, its edges may slant (the transition's facet side, the lower
    transition's trapezoid, the lip's L): an edge along an axis gets a horizontal or vertical constraint, the corners it
    joins share one dimension, and every corner is dimensioned from a reference point air_sk_ref off the origin on both
    axes, so no dimension flips side in an edit. Adapted from FRONT's front_lib.poly and extrude_span (the skeleton's
    pod_skeleton.py pattern), proven in FRONT's DR builds. Returns the new body, or the feature when op joins or cuts."""
    if op is None:            # not `op or NEW`: JoinFeatureOperation is 0, so `or` would turn a join into a new body
        op = NEW
    plane = {("x", "y"): comp.xYConstructionPlane, ("x", "z"): comp.xZConstructionPlane,
             ("y", "z"): comp.yZConstructionPlane}[tuple(plane_axes)]
    sk = comp.sketches.add(plane)
    sk.name = "SECTION - " + name
    third = ({"x", "y", "z"} - set(plane_axes)).pop()

    def at(ea, eb):
        c = {plane_axes[0]: ctx.ev(ea), plane_axes[1]: ctx.ev(eb), third: 0.0}
        return sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * CB.MM, c["y"] * CB.MM, c["z"] * CB.MM))
    sp = [at(ea, eb) for ea, eb in pts]
    lines = sk.sketchCurves.sketchLines
    verts, edges = [], []
    n = len(sp)
    for i in range(n):
        start = verts[-1] if verts else sp[0]
        end = sp[i + 1] if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(start, end)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    dims, gc = sk.sketchDimensions, sk.geometricConstraints
    expr_on = {_sketch_axis(sk, ax): k for k, ax in enumerate(plane_axes)}
    ref = sk.sketchPoints.add(at("-air_sk_ref", "-air_sk_ref"))
    for sa in ("x", "y"):
        g = ref.geometry
        dims.addDistanceDimension(sk.originPoint, ref, CB.H if sa == "x" else CB.V,
                                  adsk.core.Point3D.create(g.x / 2, g.y / 2, 0)).parameter.expression = "air_sk_ref"
    for sa in ("x", "y"):
        group = list(range(n))

        def root_of(i):
            while group[i] != i:
                i = group[i]
            return i
        for i, ln in enumerate(edges):
            p0, p1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs((p0.x - p1.x) if sa == "x" else (p0.y - p1.y)) < 1e-7:
                (gc.addVertical if sa == "x" else gc.addHorizontal)(ln)
                group[root_of((i + 1) % n)] = root_of(i)
        for i in range(n):
            if root_of(i) != i:
                continue
            g = verts[i].geometry
            d = dims.addDistanceDimension(ref, verts[i], CB.H if sa == "x" else CB.V,
                                          adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0))
            d.parameter.expression = "(%s) + air_sk_ref" % pts[i][expr_on[sa]]
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    nrm = sk.xDirection.crossProduct(sk.yDirection)
    sign = 1 if {"x": nrm.x, "y": nrm.y, "z": nrm.z}[along] > 0 else -1
    if sk.profiles.count != 1:
        raise RuntimeError("%s: the outline made %d profiles" % (sk.name, sk.profiles.count))
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(CB.vi("(%s) * (%d)" % (a, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(CB.vi("(%s) - (%s)" % (b, a))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    if bodies:
        ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei)
    f.name = ("EXTRUDE - " if op == NEW else "JOIN - " if op == JOIN else "CUT - ") + name
    if op == NEW:
        if f.bodies.count != 1:
            raise RuntimeError("%s: the extrude made %d bodies" % (name, f.bodies.count))
        f.bodies.item(0).name = name
        return f.bodies.item(0)
    return f


def circle_cut_y(comp, body, name, cx, cz, y0, y1, dia, ctx):
    """A round hole through a face normal to Y, from y0 to y1: sketch on the XZ plane offset
    to y0, centre dimensioned by expressions for model X and Z."""
    plane = CB.offset_plane(comp, comp.xZConstructionPlane, y0, "PLANE - %s" % name)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE - " + name
    cen = sk.modelToSketchSpace(adsk.core.Point3D.create(ctx.ev(cx) * CB.MM, ctx.ev(y0) * CB.MM, ctx.ev(cz) * CB.MM))
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cen.x, cen.y, 0), ctx.ev(dia) / 2 * CB.MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = dia
    for model_axis, expr in (("x", cx), ("z", cz)):
        sa, _sign = CB.model_to_sketch_axis(sk, model_axis)
        tp = adsk.core.Point3D.create(g.x + 0.6, g.y + 0.6, 0)
        sk.sketchDimensions.addDistanceDimension(sk.originPoint, c.centerSketchPoint, CB.H if sa == "x" else CB.V,
                                                 tp).parameter.expression = "abs(%s)" % expr
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: HOLE - " + name)
    n = sk.xDirection.crossProduct(sk.yDirection)
    want = 1 if ctx.ev(y1) > ctx.ev(y0) else -1
    prof = min(sk.profiles, key=lambda p: p.areaProperties().area)
    ei = comp.features.extrudeFeatures.createInput(prof, CUT)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(CB.vi("abs((%s) - (%s))" % (y1, y0))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if n.y * want > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


def cyl_body(comp, name, bx, ctx):
    """A round envelope (a stud or screw shank) filling the box's XY square, extruded up Z."""
    x0, x1, y0, y1, z0, z1 = bx
    cx, cy, d = "((%s) + (%s)) / 2" % (x0, x1), "((%s) + (%s)) / 2" % (y0, y1), "(%s) - (%s)" % (x1, x0)
    plane = CB.offset_plane(comp, comp.xYConstructionPlane, z0, "PLANE - %s Z0" % name)
    sk = comp.sketches.add(plane)
    sk.name = "OUTLINE - " + name
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(ctx.ev(cx) * CB.MM, ctx.ev(cy) * CB.MM, 0), ctx.ev(d) / 2 * CB.MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = d
    CB.dim_point(sk, c.centerSketchPoint, cx, cy, ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: OUTLINE - " + name)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), NEW)
    ei.setDistanceExtent(False, CB.vi("(%s) - (%s)" % (z1, z0)))
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - " + name
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def cyl_join(comp, body, name, cx, cy, d, z0, z1, ctx):
    """A round piece (a stud's or screw's shank) joined onto body: a circle of diameter d at (cx, cy) on a plane at
    z0, extruded to z1 (expressions in the component's own frame)."""
    plane = CB.offset_plane(comp, comp.xYConstructionPlane, z0, "PLANE - %s Z0" % name)
    sk = comp.sketches.add(plane)
    sk.name = "OUTLINE - " + name
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(ctx.ev(cx) * CB.MM, ctx.ev(cy) * CB.MM, 0), ctx.ev(d) / 2 * CB.MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = d
    CB.dim_point(sk, c.centerSketchPoint, cx, cy, ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: OUTLINE - " + name)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), JOIN)
    ei.setDistanceExtent(False, CB.vi("(%s) - (%s)" % (z1, z0)))
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - " + name
    return f


def _rot(m):
    return tuple(tuple(m.getCell(r, c) for c in range(3)) for r in range(3))


def turn_in_parent(root, parent, occ):
    """occ's turn (3 x 3) relative to its parent component, read in the design: through the parent's one occurrence
    there (its proxy), as turned-copy probes 9 to 11 read it (an occurrence's own transform inside a sub-component misled
    probes 6 and 7, and a native occurrence inside one has no entity token: AIR dry run 3)."""
    ps = root.allOccurrencesByComponent(parent)
    if ps.count == 0:                   # the parent is the root itself
        return _rot(occ.transform2)
    if ps.count != 1:
        raise RuntimeError("%s has %d occurrences; a child's turn can't be read against one" % (parent.name, ps.count))
    pp = ps.item(0)
    rp, ro = _rot(pp.transform2), _rot(occ.createForAssemblyContext(pp).transform2)
    return tuple(tuple(sum(rp[k][r] * ro[k][c] for k in range(3)) for c in range(3)) for r in range(3))


# the joint's (flip, angle) that gives each turn, as turned-copy probe 9 measured it in the design (2026-11-01 08:33):
# a rigid joint from the copy's origin to a sketch point on an XY plane of the parent; flip with angle 0 turns about X
TURN_SETTINGS = {"z": [(False, "180 deg")], "y": [(True, "180 deg")]}


def place_turned(parent, occ, axis, xyz, name, ctx):
    """A copy turned 180 deg about the pod's Y or Z axis (D-120: one part, turned): a rigid joint takes the copy's
    origin to xyz, with the flip and angle turned-copy probe 9 measured for that turn on the joint's input (Fusion
    refuses to edit a made joint without rolling the timeline back). The copy's ground-to-parent flag goes off first:
    Fusion grounds the first occurrence made in a component, and copies of it, and a joint then conflicts (probes 8
    and 9). The turn is read back in the design after a full compute; a copy that doesn't land turned stops the
    build."""
    plane = CB.offset_plane(parent, parent.xYConstructionPlane, xyz[2], "PLANE - PLACE %s" % name)
    sk = parent.sketches.add(plane)
    sk.name = "PLACE - " + name
    pt = sk.sketchPoints.add(adsk.core.Point3D.create(ctx.ev(xyz[0]) * CB.MM, ctx.ev(xyz[1]) * CB.MM, 0))
    CB.dim_point(sk, pt, xyz[0], xyz[1], ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("placement sketch not fully constrained: " + name)
    if occ.isGroundToParent:
        occ.isGroundToParent = False
    want = {"y": ((-1, 0, 0), (0, 1, 0), (0, 0, -1)), "z": ((-1, 0, 0), (0, -1, 0), (0, 0, 1))}[axis]
    root = ctx.design.rootComponent
    tried = []
    for flip, angle in TURN_SETTINGS[axis]:
        g_occ = adsk.fusion.JointGeometry.createByPoint(occ.component.originConstructionPoint.createForAssemblyContext(occ))
        ji = parent.joints.createInput(g_occ, adsk.fusion.JointGeometry.createByPoint(pt))
        ji.setAsRigidJointMotion()
        ji.isFlipped = flip
        ji.angle = adsk.core.ValueInput.createByString(angle)
        j = parent.joints.add(ji)
        j.name = "PLACE - " + name
        ctx.design.computeAll()
        got = turn_in_parent(root, parent, occ)
        healthy = j.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
        tried.append((flip, angle, healthy, tuple(tuple(round(v, 4) for v in row) for row in got)))
        if healthy and all(abs(got[r][c] - want[r][c]) < 1e-6 for r in range(3) for c in range(3)):
            print("%s: turned about %s by the joint's flip %s, angle %s (read in the design)" % (name, axis.upper(), flip, angle))
            return j
        j.deleteMe()
    raise RuntimeError("the joint didn't turn %s about %s: %s" % (name, axis, tried))


def build_cartridge(parent, design, ctx, bx, along, tag):
    """Casing (2 mm tube open at both ends) and three 50 mm layers parallel to the
    front face, with two passages between them. bx: outer box; along: 'z' or 'x'."""
    occ, comp = new_comp(parent, "cart")
    comp.name = comp.name + " (%s)" % tag
    x0, x1, y0, y1, z0, z1 = bx
    _co, cas = new_comp(comp, "casing")
    casing = CB.box_body(cas, "CARTRIDGE %s" % tag, bx, ctx)     # the casing carries the layout name
    hollow_axis(cas, casing, along, "cart_t", "CARTRIDGE %s CASING" % tag)
    set_material(design, cas, "casing")
    # D-120: the three layers are one part (611302), built once in its own frame and placed three times
    lay_comp = None
    for k in range(3):
        ly0 = "%s + cart_t + %d * (lay_t + pass_w)" % (y0, k)
        if along == "z":
            lb = ("%s + cart_t" % x0, "%s - cart_t" % x1, ly0, "%s + lay_t" % ly0, z0, z1)
        else:
            lb = (x0, x1, ly0, "%s + lay_t" % ly0, "%s + cart_t" % z0, "%s - cart_t" % z1)
        if lay_comp is None:
            lo, lay_comp = new_comp(comp, "layer")
            CB.box_body(lay_comp, "LAYER 50 %s" % tag, ("0 mm", "(%s) - (%s)" % (lb[1], lb[0]), "0 mm",
                                                         "(%s) - (%s)" % (lb[3], lb[2]), "0 mm",
                                                         "(%s) - (%s)" % (lb[5], lb[4])), ctx)
            set_material(design, lay_comp, "layer")
        else:
            lo = comp.occurrences.addExistingComponent(lay_comp, adsk.core.Matrix3D.create())
        CB.place(comp, lo, (lb[0], lb[2], lb[4]), "LAYER %d %s" % (k + 1, tag), ctx)
    return occ, comp


FOLDER = "Default Project/FocusPod v2"
# part-only designs for the drawings (D-89 parts 1 to 4: assemblies, folded, machined and bonded
# parts keep drawings); each scope lists layout keys, or a special item in capitals
SCOPE_KEYS = {
    "column": ["col_foot", "col_front", "col_left", "col_side_lo", "col_side_hi", "col_fill", "col_fill_l", "kick",
               "kick_l", "hub", "col_ang", "col_ang_b", "CART:SUPPLY"],
    "soffit": ["sof_under", "sof_under_r", "sof_under_f", "sof_front", "sof_rail_d", "sof_rail_r", "sof_door", "sof_end", "sof_fill",
               "sof_fill_f", "egrille", "stud", "hinge", "latch", "lock", "CART:EXHAUST", "BOX:EXHAUST"],
    "cart": ["CART:SUPPLY"], "sbox": ["BOX:SUPPLY", "trans", "riser", "rtrans"], "ebox": ["BOX:EXHAUST"],
    "col_ang": ["ANGLE:FL"], "col_ang_b": ["col_ang_b"], "casing": ["CASING"], "box": ["BOXCASE:EXHAUST"],
    "box_s": ["BOXCASE:SUPPLY"], "blk_e": ["blk_e"], "blk_s": ["blk_s"],
    "riser": ["riser"], "sleeve": ["sleeve"], "col_front": ["col_front"], "col_left": ["col_left"],
    "sof_under": ["sof_under"], "sof_under_r": ["sof_under_r"], "sof_under_f": ["sof_under_f"], "sof_front": ["sof_front"],
}


def part_doc_name(key):
    import re
    pn, name, _vn, _k, _m = A.PARTS[key]
    return "%s_%s_%s_CAD" % (pn, A.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"))


def open_or_create(app, name):
    """The design called `name` in FOLDER: activate it if open, open it from the cloud, or make
    it there (the same steps as run_script.py --doc NAME --doc-new)."""
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name.split(" v")[0] == name:
            if d.isModified:
                # PM rule 2026-11-01: never reuse an open document with unsaved changes
                d.close(False)
                break
            d.activate()
            return d, "activated"
    parts = [p for p in FOLDER.split("/") if p]
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == parts[0])
    folder = proj.rootFolder
    for n in parts[1:]:
        folder = folder.dataFolders.itemByName(n)
    # the shared folder reader (tools/fusion/fusion_folder.py, given to every script by the runner): one fetch of the
    # folder per pass; reading it entry by entry took about 7 min on 2026-11-01 (the follow-up build ran past 900 s)
    from fusion_folder import read_folder
    files, unknown, _others = read_folder(folder, stop_when=lambda fs, _u, _o: name in fs)
    found, unreadable = list(files.get(name, [])), len(unknown)
    if len(found) > 1:
        raise RuntimeError("%d files called %r in %s; rename the extra ones first (D-141)" % (len(found), name, FOLDER))
    app.data.activeProject = proj
    if found:
        d = app.documents.open(found[0], True)
        d.activate()
        return d, "opened"
    if unreadable and ARGS.get("new_name") != "1":
        # PM ruling 2026-11-01: list the folder first and stop before creating anything if any
        # entry can't be read (that entry could be this very design), unless the name has never
        # been used (new_name=1: the author checked it never existed, so no duplicate can arise)
        raise RuntimeError("%d entries of %s can't be read, so %r isn't made" % (unreadable, FOLDER, name))
    if ARGS.get("create") != "1":
        # PM ruling 2026-11-01: no new designs until the runner's folder fix lands, since an
        # entry Fusion can't read could make a second, empty design with a real one's name
        raise RuntimeError("%r is not in %s; pass create=1 to make it (only once that's allowed)" % (name, FOLDER))
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    if not d.saveAs(name, folder, "new, made by air_build.py parts=", ""):
        raise RuntimeError("saveAs %r failed" % name)
    d.activate()
    return d, "made"


def build_scope(root, design, ctx, scope):
    lay = {name: (key, bx) for key, name, bx in A.layout()}
    cuts = {}
    for target, cb in A.cutouts():
        cuts.setdefault(target, []).append(cb)
    made = {}

    def body(name):
        b = (cyl_body if name.endswith("SHANK") else CB.box_body)(root, name, lay[name][1], ctx)
        for i, cb in enumerate(cuts.get(name, [])):
            CB.box_body(root, "%s OPENING %d" % (name, i + 1), cb, ctx, op=CUT, bodies=[b])
        made[name] = b
        return b

    def casing(bname, key):
        b = body(bname)
        hollow_open(root, b, A.FAN_BOX_OPEN[bname], "fbox_t", bname)
        return b
    for item in SCOPE_KEYS[scope]:
        if item.startswith("CART:"):
            tag = item.split(":")[1]
            build_cartridge(root, design, ctx, lay["CARTRIDGE %s" % tag][1], "z" if tag == "SUPPLY" else "x", tag)
        elif item == "CASING":
            b = CB.box_body(root, "CARTRIDGE CASING", lay["CARTRIDGE SUPPLY"][1], ctx)
            hollow_axis(root, b, "z", "cart_t", "CARTRIDGE CASING")
        elif item.startswith(("BOX:", "BOXCASE:")):
            tag = item.split(":")[1]
            casing("%s FAN BOX" % tag, "box" if tag == "EXHAUST" else "box_s")
            if item.startswith("BOX:"):
                for k, name, _bx in A.fan_box_inner():      # D-121: the bulkhead and the linings
                    if tag in name:
                        body(name)
                fan_comp = None
                for fname, fx, fy, fz in [f for f in A.fan_points() if f[0].startswith(tag)]:
                    if fan_comp is None:
                        fo, fan_comp = new_comp(root, "fan")
                        CB.box_body(fan_comp, "FAN 140 ENVELOPE", ("-fan_s / 2", "fan_s / 2", "-fan_s / 2", "fan_s / 2",
                                                                    "0 mm", "fan_t"), ctx)
                    else:
                        fo = root.occurrences.addExistingComponent(fan_comp, adsk.core.Matrix3D.create())
                    CB.place(root, fo, (fx, fy, fz), fname, ctx)
        elif item in ("col_ang", "col_ang_b") or item.startswith("ANGLE:"):
            # the column's angles: the front pair (col_ang), the back one (col_ang_b), or one angle for its part design
            tags = {"col_ang": ("FL", "FR"), "col_ang_b": ("BL",)}.get(item) or (item.split(":")[1],)
            for tag in tags:
                x0, x1, y0, y1, z0, z1 = lay["COLUMN ANGLE %s" % tag][1]
                made["COLUMN ANGLE %s" % tag] = poly_xy_extrude(root, "COLUMN ANGLE %s" % tag,
                                                                A.angle_pts(tag, x0, x1, y0, y1), z0, z1, ctx)
        else:
            for k, name, _bx in A.layout():
                if k != item:
                    continue
                b = body(name)
                if k == "riser":
                    poly_prism(root, "INTAKE RISER CHAMFER", ("x", "y"), A.riser_chamfer(), "z", "rs_z0 - 1 mm",
                               "rs_z1 + 1 mm", ctx, op=CUT, bodies=[b])
                    hollow_axis(root, b, "z", "rs_t", name)
                if k == "sleeve":
                    hollow_axis(root, b, "z", "slv_t", name)
    for k, (bname, kind, a) in enumerate(A.features()):
        if bname not in made:
            continue
        label = "%s FEATURE %d" % (bname, k + 1)
        if kind == "zcircle":
            CB.circle_cut(root, made[bname], label, a[0], a[1], a[4], a[2], a[3], ctx)
        elif kind == "ycircle":
            circle_cut_y(root, made[bname], label, a[0], a[1], a[2], a[3], a[4], ctx)
        else:
            CB.box_body(root, label, a, ctx, op=CUT, bodies=[made[bname]])
    return made


def run_parts(app, scopes):
    """One run, several part-only designs for the drawings (fair-share queue rule)."""
    for scope in scopes:
        if scope not in SCOPE_KEYS:
            raise RuntimeError("scope must be one of %s" % sorted(SCOPE_KEYS))
        name = part_doc_name(scope)
        t0 = time.time()
        doc, how = open_or_create(app, name)
        design = adsk.fusion.Design.cast(app.activeProduct)
        CB.clear_design(design)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        ctx = CB.Ctx(design)
        params = A.all_params()
        for pname, expr, unit, status, src in params:
            design.userParameters.add(pname, CB.vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = A.evaluate(params)
        try:
            root = design.rootComponent
            pn, pname_, vn, kind, mk = A.PARTS[scope]
            root.partNumber = pn
            root.description = "%s | %s | %s | %s | drawing source, built by air_build.py" % (pname_, vn, kind, A.REV)
            build_scope(root, design, ctx, scope)
            if mk:
                nm, density = A.MATERIALS[mk]
                m = design.materials.itemByName(nm)
                if m is None:
                    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
                    m = design.materials.addByCopy(lib.materials.itemByName("Steel" if mk == "steel" else "Aluminum"), nm)
                    adsk.core.FloatProperty.cast(m.materialProperties.itemById("structural_Density")).value = density
                for b in root.bRepBodies:
                    b.material = m
            adsk.doEvents()
            tl = design.timeline
            bad = [tl.item(i).name for i in range(tl.count)
                   if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
            loose = [c.name + "/" + sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
            print("PART %s %s (%s): timeline %d, unhealthy %d, loose %d, box %s, %.0f s" % (
                pn, pname_, how, tl.count, len(bad), len(loose), CB.body_box(root), time.time() - t0))
            if bad or loose:
                raise RuntimeError("part %s checks failed (unhealthy %s, loose %s)" % (scope, bad, loose))
            print("saved:", doc.save("%s %s drawing source, skeleton %s" % (pn, A.REV, ceiling_model.SKELETON_REV)))
            adsk.doEvents()
        finally:
            doc.close(False)        # each run closes what it opened (PM rule 2026-11-01)


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("parts"):
        run_parts(app, [k for k in ARGS["parts"].split(",") if k])
        return
    into_active = ARGS.get("into_active") == "1"
    own = ARGS.get("own_doc") == "1"          # the script opens or makes DOC_NAME itself
    if own:
        doc, how = open_or_create(app, DOC_NAME)
        print("document %s: %s" % (DOC_NAME, how))
        into_active = True
    elif into_active:
        doc = app.activeDocument
        if doc.name.split(" v")[0] != DOC_NAME:
            raise RuntimeError("active document is %r, not %s" % (doc.name, DOC_NAME))
    else:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    ok = False
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if into_active:
            CB.clear_design(design)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        ctx = CB.Ctx(design)
        params = A.all_params()
        for name, expr, unit, status, src in params:
            design.userParameters.add(name, CB.vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = A.evaluate(params)
        root = design.rootComponent
        root.partNumber = "610000"
        root.description = "AIR | Thông gió | HS | " + A.REV
        lay = {name: (key, bx) for key, name, bx in A.layout()}
        cuts = {}
        for target, cb in A.cutouts():
            cuts.setdefault(target, []).append(cb)

        def body_in(comp, name, key=None):
            b = (cyl_body if name.endswith("SHANK") else CB.box_body)(comp, name, lay[name][1], ctx)
            for i, cb in enumerate(cuts.get(name, [])):
                CB.box_body(comp, "%s OPENING %d" % (name, i + 1), cb, ctx, op=CUT, bodies=[b])
            return b

        made = {}      # body name -> (component, body)

        def put(comp, name):
            made[name] = (comp, body_in(comp, name))
            return made[name][1]

        def comp_with(parent, key, names, material=True):
            _o2, c = new_comp(parent, key)
            for n in names:
                put(c, n)
            if material:
                set_material(design, c, key)
            return c

        def names_of(key):
            return [n for k, n, _b in A.layout() if k == key]
        unit_of = {name: bx for _k, name, bx in A.units()}

        def rel(e, o):
            return "(%s) - (%s)" % (e, o)

        def box_maker(body_name):
            def make(comp, _n, u):
                return CB.box_body(comp, body_name, ("0 mm", rel(u[1], u[0]), "0 mm", rel(u[3], u[2]), "0 mm",
                                                     rel(u[5], u[4])), ctx)
            return make

        def stud_maker(body_name):
            def make(comp, _n, u):        # D-120: the head with its shank joined, one body
                head = CB.box_body(comp, body_name, ("0 mm", "stud_d", "0 mm", "stud_d", "0 mm", "hd_h"), ctx)
                cyl_join(comp, head, body_name + " SHANK", "stud_d / 2", "stud_d / 2", "6 mm", "hd_h", rel(u[5], u[4]), ctx)
                return head
            return make

        def copies(parent, key, unit_names, maker, setup=None):
            """One part placed as copies (D-120): made once in its own frame (the first unit's low corner at the
            origin) and each copy joined to its unit's low corner; the units must all be the part's size."""
            us = [unit_of[n] for n in unit_names]
            dims = [[ctx.ev(rel(u[2 * i + 1], u[2 * i])) for i in range(3)] for u in us]
            if any(max(abs(a - b) for a, b in zip(d, dims[0])) > 1e-6 for d in dims):
                raise RuntimeError("%s: its copies differ in size: %s" % (key, dims))
            comp = None
            for n, u in zip(unit_names, us):
                if comp is None:
                    if setup is None:
                        occ, comp = new_comp(parent, key)
                    else:
                        occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                        comp = occ.component
                        setup(comp)
                    made[n] = (comp, maker(comp, n, u))
                    set_material(design, comp, "riser" if key in ("lock", "stud") else key)
                else:
                    occ = parent.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
                CB.place(parent, occ, (u[0], u[2], u[4]), n, ctx)
            return comp

        def units_of(key):
            return [n for k, n, _b in A.units() if k == key]
        # ---- column: foot plate, faces, kick grille, plenum plates, fill, hub zone, angles, cartridge
        _o, col = new_comp(root, "column")
        for key in ("col_foot", "col_front", "col_left", "col_side_lo", "col_side_hi", "col_fill", "col_fill_l", "kick",
                    "kick_l", "hub"):
            comp_with(col, key, names_of(key))
        # the two front angles: one part (611103), the left built in its own frame, the right its copy turned about Y
        x0, x1, y0, y1, z0, z1 = lay["COLUMN ANGLE FL"][1]
        occ_fl, ang = new_comp(col, "col_ang")
        pts = [(rel(px, x0), rel(py, y0)) for px, py in A.angle_pts("FL", x0, x1, y0, y1)]
        made["COLUMN ANGLE FL"] = (ang, poly_xy_extrude(ang, "COLUMN ANGLE FRONT", pts, "0 mm", rel(z1, z0), ctx))
        set_material(design, ang, "col_ang")
        CB.place(col, occ_fl, (x0, y0, z0), "COLUMN ANGLE FL", ctx)
        fx0, fx1, fy0, fy1, fz0, fz1 = lay["COLUMN ANGLE FR"][1]
        if ARGS.get("no_turn") == "1":
            # a dry run's stand-in while the turned-copy method is being proven (turn probes 2 to 5, 2026-11-01): the
            # right angle built in place as its own body under the same number; never saved
            if ARGS.get("save") == "1":
                raise RuntimeError("no_turn=1 is for unsaved dry runs only")
            _ofr, angr = new_comp(col, "col_ang")
            made["COLUMN ANGLE FR"] = (angr, poly_xy_extrude(angr, "COLUMN ANGLE FRONT", A.angle_pts("FR", fx0, fx1, fy0, fy1),
                                                             fz0, fz1, ctx))
            set_material(design, angr, "col_ang")
        else:
            occ_fr = col.occurrences.addExistingComponent(ang, adsk.core.Matrix3D.create())
            place_turned(col, occ_fr, A.TURNED["col_ang"], (fx1, fy0, fz1), "COLUMN ANGLE FR", ctx)
        # the back-left angle (611109), in place, with its keyholes (features below)
        x0, x1, y0, y1, z0, z1 = lay["COLUMN ANGLE BL"][1]
        _ob, angb = new_comp(col, "col_ang_b")
        made["COLUMN ANGLE BL"] = (angb, poly_xy_extrude(angb, "COLUMN ANGLE BL", A.angle_pts("BL", x0, x1, y0, y1),
                                                         z0, z1, ctx))
        set_material(design, angb, "col_ang_b")
        build_cartridge(col, design, ctx, lay["CARTRIDGE SUPPLY"][1], "z", "SUPPLY")
        print("step column done")
        # ---- soffit (ships with its exhaust fan box fitted, D-87): underside sections, face,
        #      rails, end plate, fill, grille, hanging and service hardware envelopes
        _o, sof = new_comp(root, "soffit")
        for key in ("sof_under", "sof_under_r", "sof_under_f", "sof_front", "sof_rail_d", "sof_rail_r", "sof_door",
                    "sof_end", "sof_fill", "sof_fill_f", "egrille"):
            comp_with(sof, key, names_of(key))
        hs = A.HARDWARE["stud"]

        def stud_setup(sd):
            # the register's M6 x 16 socket head bolt 838001 (D-90, HOLD-18; the Lead's ruling 2026-11-01)
            sd.name, sd.partNumber = "%s %s" % (hs[0], hs[1]), hs[0]
            sd.description = "%s | %s | PI | %s | the soffit's hanger stud (D-90)" % (hs[1], hs[2], A.REV)
        copies(sof, "stud", units_of("stud"), stud_maker("HANGER STUD"), setup=stud_setup)   # steel, as the riser
        copies(sof, "hinge", units_of("hinge"), box_maker("HINGE ENVELOPE"))
        copies(sof, "latch", units_of("latch"), box_maker("LATCH ENVELOPE"))
        hp = A.HARDWARE["lock"]

        def lock_setup(lk):
            lk.name, lk.partNumber = "%s %s" % (hp[0], hp[1]), hp[0]
            lk.description = "%s | %s | PI | %s | captive retainer HOLD (joints register)" % (hp[1], hp[2], A.REV)
        copies(sof, "lock", units_of("lock"), stud_maker("LOCK SCREW"), setup=lock_setup)   # steel, as the riser
        build_cartridge(sof, design, ctx, lay["CARTRIDGE EXHAUST"][1], "x", "EXHAUST")
        print("step soffit done")
        # ---- fan boxes with their fans; the supply box joined with the riser and transitions (D-87)
        fan_comp = None
        fans = A.fan_points()
        boxes = {}
        for key, bname, parent in (("ebox", "EXHAUST FAN BOX", sof), ("sbox", "SUPPLY FAN BOX", root)):
            _o, fb = new_comp(parent, key)
            boxes[key] = fb
            ck = "box" if key == "ebox" else "box_s"
            _o2, casing = new_comp(fb, ck)
            b = put(casing, bname)
            hollow_open(casing, b, A.FAN_BOX_OPEN[bname], "fbox_t", bname)
            set_material(design, casing, ck)
            tag = "EXHAUST" if key == "ebox" else "SUPPLY"
            if tag == "EXHAUST":
                comp_with(fb, "blk_e", names_of("blk_e"))
                copies(fb, "lin_es", units_of("lin_es"), box_maker("FAN BOX LINING EXHAUST SIDE"))
                comp_with(fb, "lin_ee", names_of("lin_ee"))
            else:
                comp_with(fb, "blk_s", names_of("blk_s"))
                copies(fb, "lin_s", units_of("lin_s"), box_maker("FAN BOX LINING SUPPLY END"))
                # how the assembly rests in DR (PM rulings 2026-11-01): the lip angle on the box's front wall, its two
                # pads on F08 (one part placed twice), the riser's buffer against F07
                _ol, lipc = new_comp(fb, "lip")
                made["FAN BOX LIP ANGLE SUPPLY"] = (lipc, poly_prism(lipc, "FAN BOX LIP ANGLE SUPPLY", ("y", "z"),
                                                                     A.lip_section(), "x", "sb_x0", A.LIP_X1, ctx))
                set_material(design, lipc, "lip")
                copies(fb, "pad", units_of("pad"), box_maker("FAN BOX PAD"))
                comp_with(fb, "buffer", names_of("buffer"))
            for fname, fx, fy, fz in [f for f in fans if f[0].startswith(tag)]:
                if fan_comp is None:
                    fo, fan_comp = new_comp(fb, "fan")
                    CB.box_body(fan_comp, "FAN 140 ENVELOPE", ("-fan_s / 2", "fan_s / 2", "-fan_s / 2", "fan_s / 2",
                                                                "0 mm", "fan_t"), ctx)
                    set_material(design, fan_comp, "fan")
                else:
                    fo = fb.occurrences.addExistingComponent(fan_comp, adsk.core.Matrix3D.create())
                CB.place(fb, fo, (fx, fy, fz), fname, ctx)
        # the upper transition over the box and the full-depth passage beside it (PM rulings 2026-11-01), one body
        _ot, tc = new_comp(boxes["sbox"], "trans")
        (top, z0, z1), (side, z2, z3) = A.transition_outlines()
        tb = poly_prism(tc, "SUPPLY TRANSITION", ("x", "y"), top, "z", z0, z1, ctx)
        poly_prism(tc, "SUPPLY TRANSITION BESIDE THE BOX", ("x", "y"), side, "z", z2, z3, ctx, op=JOIN, bodies=[tb])
        made["SUPPLY TRANSITION"] = (tc, tb)
        set_material(design, tc, "trans")
        rc = comp_with(boxes["sbox"], "riser", names_of("riser"))
        # the 8 x 8 chamfer on its front-right edge (the Lead's ruling 2026-11-01), cut before the shell so the tube's
        # wall follows it
        poly_prism(rc, "INTAKE RISER CHAMFER", ("x", "y"), A.riser_chamfer(), "z", "rs_z0 - 1 mm", "rs_z1 + 1 mm", ctx,
                   op=CUT, bodies=[made["INTAKE RISER"][1]])
        hollow_axis(rc, made["INTAKE RISER"][1], "z", "rs_t", "INTAKE RISER")
        # the lower transition: FRONT's trapezoid from the riser's top to the box's bottom, over the riser's depth as
        # FRONT reserves it (Reviewer 7: from the box's front line it cut DR's corner skin)
        _or, rtc = new_comp(boxes["sbox"], "rtrans")
        made["RISER TRANSITION"] = (rtc, poly_prism(rtc, "RISER TRANSITION", ("x", "z"), A.riser_transition_outline(),
                                                    "y", "rs_y0", "rs_y0 + rs_d", ctx))
        set_material(design, rtc, "rtrans")
        # the roof sleeve: its walls through the slot, and its top flange on C2's skin round the slot (J-AIR-03)
        _os, slc = new_comp(root, "sleeve")
        sz0 = lay["ROOF SLEEVE"][1][4]
        sw = CB.box_body(slc, "ROOF SLEEVE", ("slot_x0", "slot_x0 + slot_w", "slot_y0", "slot_y0 + slot_d", sz0, "pod_h"),
                         ctx)
        hollow_axis(slc, sw, "z", "slv_t", "ROOF SLEEVE")
        fx0, fx1, fy0, fy1 = A.sleeve_flange()
        jf = CB.box_body(slc, "ROOF SLEEVE FLANGE", (fx0, fx1, fy0, fy1, "pod_h", "pod_h + slv_t"), ctx, op=JOIN,
                         bodies=[sw])
        jf.name = "JOIN - ROOF SLEEVE FLANGE"
        ox0, ox1, oy0, oy1 = A.sleeve_opening()     # the walls' inside: the flange stays on the wall tops (one solid)
        CB.box_body(slc, "ROOF SLEEVE FLANGE OPENING", (ox0, ox1, oy0, oy1, "pod_h", "pod_h + slv_t"), ctx, op=CUT,
                    bodies=[sw])
        made["ROOF SLEEVE"] = (slc, sw)
        set_material(design, slc, "sleeve")
        comp_with(root, "rgrille", names_of("rgrille"))
        # ---- cut features: keyholes, BASE's spigot hole and slot, the rails' forks, lock holes
        for k, (bname, kind, a) in enumerate(A.features()):
            comp, body = made[bname]
            label = "%s FEATURE %d" % (bname, k + 1)
            if kind == "zcircle":
                CB.circle_cut(comp, body, label, a[0], a[1], a[4], a[2], a[3], ctx)
            elif kind == "ycircle":
                circle_cut_y(comp, body, label, a[0], a[1], a[2], a[3], a[4], ctx)
            else:
                CB.box_body(comp, label, a, ctx, op=CUT, bodies=[body])
        adsk.doEvents()
        print("step boxes, riser, sleeve done")

        # ---- checks
        tl = design.timeline
        bad = [tl.item(i).name for i in range(tl.count)
               if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [c.name + "/" + s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
        bodies = CB.all_bodies(root)
        hits = CB.clash_check(bodies)
        print("timeline %d items, unhealthy %d, loose sketches %d, parameters %d, bodies %d, clashes %d" % (
            tl.count, len(bad), len(loose), design.userParameters.count, len(bodies), len(hits)))
        for h in hits:
            print("CLASH|%s|%s|%s mm3" % h)
        # every layout body where the layout says (fans checked by their centres)
        worst, off = K.place_check(K.bodies_by_number(root), ctx.vals)
        print("position check: %d units (each copy, each joined stud), worst %.3f mm, off %s" % (
            len(A.units()), worst, off or "none"))
        for n, b in bodies:
            print("BODY|%s|%s" % (n, CB.body_box(b)))
        for occ in root.allOccurrences:
            c = occ.component
            if c.bRepBodies.count:
                print("MASS|%s|%s|%.3f kg" % (occ.fullPathName, c.partNumber, c.getPhysicalProperties().mass))
        if bad or loose or hits or off:
            raise RuntimeError("AIR checks failed (unhealthy %s, loose %s, clashes %s, off %s)" % (bad, loose, hits, off))
        if ARGS.get("save") == "1":
            if not into_active:
                raise RuntimeError("save=1 needs into_active=1 with the runner's --doc %s --doc-new" % DOC_NAME)
            print("saved:", doc.save("AIR %s build, skeleton %s" % (A.REV, ceiling_model.SKELETON_REV)))
            adsk.doEvents()
        if ARGS.get("export") == "1":
            em = design.exportManager
            for rel, mk in ((F3D_REL, em.createFusionArchiveExportOptions), (STEP_REL, em.createSTEPExportOptions)):
                path = os.path.join(ARGS["repo_root"], rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                done = False
                for _try in range(10):
                    done = em.execute(mk(path, root))
                    if done and os.path.getsize(path) > 2000:
                        break
                    adsk.doEvents()
                    time.sleep(3)
                print("export %s: %s" % (rel, done))
                if not done:
                    raise RuntimeError("export failed: " + rel)
        ok = True
    finally:
        if own or not (into_active or ARGS.get("keep") == "1"):
            doc.close(False)
    if not ok:
        raise RuntimeError("build did not finish")
