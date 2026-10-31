"""Spaceship (FocusPod v2) CEILING P01: native, parameter-driven Fusion design.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/ceiling_build.py \
        --label "CEILING Engineer" [--arg keep=1] [--arg save=1] [--arg export=1]

Builds one new design, 410000 CEILING (pod coordinates, conventions.md s4):

  410101 CEILING - PANEL ASSY - C1 (-X half)
      411101 CEILING - PANEL FRAME - C1: aluminium 20 x 40 x 1.2 members and a 40 x 40 x 1.2
             back member, half_fw wide, with the site-joint holes (J-CEIL-01, J-CEIL-02)
      411301 CEILING - SKIN - C1: ACP 3 mm, half_pw wide
  410102 CEILING - PANEL ASSY - C2 (+X half): 411102 frame + 411302 skin with the roof slot
  510301 LINING - CASSETTE - CEILING - COMMON, at C1-CASS and at C2-CASS:
      513101 tray (sheet metal, 0.5 mm, returns turned in under the felt as a 12 mm lip)
      2 x 513102 rib, 513201 felt, 513301 + 513302 + 513303 fill strips,
      6 x 518001 clip and 2 x 518002 safety catch (HOLD envelopes)

Every size is a user parameter: the skeleton's own list (P04), loaded from its CSV,
then the ceiling's (ceiling_model.py), each with its status and source. Repeated
parts are one component with several occurrences; each occurrence is placed by a
rigid joint to a sketch point dimensioned by expressions, so placements follow the
parameters. Checks fail the run: timeline health, every sketch fully constrained,
every body where the layout says, no clash, the cassette clear of the frame.

Options (--arg KEY=VALUE): close_previous=1 (close unsaved 410000 designs left by
an earlier run), keep=1 (leave the new design open), save=1 (save into
Default Project / FocusPod v2), export=1 (f3d, STEP and the tray's flat-pattern
DXF into the repo; needs save=1).
"""

import importlib
import os
import re
import sys
import time
import traceback

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import ceiling_model as M  # noqa: E402
importlib.reload(M)      # Fusion keeps modules loaded between runs
import ceiling_checks as C  # noqa: E402
importlib.reload(C)

DOC_NAME = "410000_%s_CEILING_CAD" % M.REV
SCOPES = ("cassette", "tray", "rib", "felt", "fill_a", "fill_b", "fill_c",
          "frame_c1", "frame_c2", "skin_c1", "skin_c2", "assy_c1", "assy_c2")   # part-only designs for drawings


def part_doc_name(key):
    pn, name, _vn, _k, _m = M.PARTS[key]
    return "%s_%s_%s_CAD" % (pn, M.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"))
CLOUD_FOLDER = "FocusPod v2"
F3D_REL = "v2/01-CAD-Native/ceiling/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/ceiling/410000_%s_CEILING_STEP.step" % M.REV
DXF_RAW_REL = "v2/03-Manufacturing/ceiling/.raw/513101_%s_LINING-TRAY-CEILING_flat-fusion.dxf" % M.REV
MM = 0.1
EPS = 1e-6
H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


class Ctx:
    """Build state shared by the helpers."""
    def __init__(self, design):
        self.design = design
        self.vals = None

    def ev(self, expr):
        return self.design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def is_zero(expr):
    return expr.strip() in ("0 mm", "0", "(0 mm)")


# ---------------------------------------------------------------- sketches and bodies

def offset_plane(comp, base, expr, name):
    if is_zero(expr):
        return base
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(base, vi(expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = name
    pl.isLightBulbOn = False
    return pl


def dim_point(sk, pt, x_expr, y_expr, ctx, anchor=None):
    """Fix a sketch point by dimensions from the sketch origin (XY-type planes only)."""
    dims, gc = sk.sketchDimensions, sk.geometricConstraints
    g = pt.geometry
    tp = adsk.core.Point3D.create(g.x + 0.7, g.y + 0.7, 0)
    for expr, horiz in ((x_expr, True), (y_expr, False)):
        if is_zero(expr) or abs(ctx.ev(expr)) < EPS:
            if not is_zero(expr):
                raise RuntimeError("expression %r is zero now but not literally zero" % expr)
            (gc.addVerticalPoints if horiz else gc.addHorizontalPoints)(pt, sk.originPoint)
        else:
            d = dims.addDistanceDimension(sk.originPoint, pt, H if horiz else V, tp)
            d.parameter.expression = "abs(%s)" % expr


def rect_sketch(comp, plane, name, x0, x1, y0, y1, ctx):
    """Fully constrained rectangle on an XY-type plane: size and one corner by expressions."""
    sk = comp.sketches.add(plane)
    sk.name = name
    a = (ctx.ev(x0), ctx.ev(y0))
    b = (ctx.ev(x1), ctx.ev(y1))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(a[0] * MM, a[1] * MM, 0), adsk.core.Point3D.create(b[0] * MM, b[1] * MM, 0))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            s0, s1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(s0.y - s1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for p in (ln.startSketchPoint, ln.endSketchPoint):
            if all(p != q for q in pts):
                pts.append(p)

    def near(x, y):
        return min(pts, key=lambda p: (p.geometry.x - x * MM) ** 2 + (p.geometry.y - y * MM) ** 2)
    c00, c10, c01 = near(a[0], a[1]), near(b[0], a[1]), near(a[0], b[1])
    dims = sk.sketchDimensions
    tp = adsk.core.Point3D.create((a[0] + b[0]) / 2 * MM, (a[1] + b[1]) / 2 * MM, 0)
    dims.addDistanceDimension(c00, c10, H, tp).parameter.expression = "(%s) - (%s)" % (x1, x0)
    dims.addDistanceDimension(c00, c01, V, tp).parameter.expression = "(%s) - (%s)" % (y1, y0)
    dim_point(sk, c00, x0, y0, ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + name)
    return sk


def box_body(comp, name, b, ctx, op=None, bodies=None):
    """A box from six expressions (x0, x1, y0, y1, z0, z1) in the component's frame:
    a rectangle on the XY plane offset by z0, extruded by z1 - z0."""
    x0, x1, y0, y1, z0, z1 = b
    plane = offset_plane(comp, comp.xYConstructionPlane, z0, "PLANE - %s Z0" % name)
    sk = rect_sketch(comp, plane, "OUTLINE - " + name, x0, x1, y0, y1, ctx)
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
    ei.setDistanceExtent(False, vi("(%s) - (%s)" % (z1, z0)))
    if bodies:
        ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei)
    f.name = ("EXTRUDE - " if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation else "CUT - ") + name
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        f.bodies.item(0).name = name
        return f.bodies.item(0)
    return f


def circle_cut(comp, body, name, cx, cy, dia, z0, z1, ctx):
    plane = offset_plane(comp, comp.xYConstructionPlane, z0, "PLANE - %s Z0" % name)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE - " + name
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(ctx.ev(cx) * MM, ctx.ev(cy) * MM, 0), ctx.ev(dia) / 2 * MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = dia
    dim_point(sk, c.centerSketchPoint, cx, cy, ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: HOLE - " + name)
    prof = min(sk.profiles, key=lambda p: p.areaProperties().area)
    ei = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setDistanceExtent(False, vi("(%s) - (%s)" % (z1, z0)))
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


def circle_cut_x(comp, body, name, xf, cy, cz, dia, depth, into, ctx):
    """A round hole through a face normal to X: sketch on the YZ plane offset to X = xf, the
    centre dimensioned by expressions for model Y and Z, cut by depth toward into (+1 or -1
    along model X), into one body only."""
    plane = offset_plane(comp, comp.yZConstructionPlane, xf, "PLANE - %s" % name)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE - " + name
    c3 = adsk.core.Point3D.create(ctx.ev(xf) * MM, ctx.ev(cy) * MM, ctx.ev(cz) * MM)
    cen = sk.modelToSketchSpace(c3)
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cen.x, cen.y, 0), ctx.ev(dia) / 2 * MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = dia
    dims = sk.sketchDimensions
    for model_axis, expr in (("y", cy), ("z", cz)):
        sa, _sign = model_to_sketch_axis(sk, model_axis)
        if abs(ctx.ev(expr)) < EPS:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else sk.geometricConstraints.addHorizontalPoints)(
                c.centerSketchPoint, sk.originPoint)
        else:
            tp = adsk.core.Point3D.create(g.x + 0.6, g.y + 0.6, 0)
            dims.addDistanceDimension(sk.originPoint, c.centerSketchPoint, H if sa == "x" else V, tp).parameter.expression = \
                "abs(%s)" % expr
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: HOLE - " + name)
    n = sk.xDirection.crossProduct(sk.yDirection)
    prof = min(sk.profiles, key=lambda p: p.areaProperties().area)
    ei = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(depth)),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if n.x * into > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


def circles_cut(comp, body, name, plane, coord, centres, dia, depth, into, ctx):
    """A row of round holes in one sketch and one cut: plane 'z' (an XY-type plane at Z =
    coord, centres as (x, y) expressions) or 'x' (a YZ-type plane at X = coord, centres as
    (y, z)); every circle's size and centre dimensioned by expressions; cut by depth toward
    `into` (+1 or -1 along the plane's model axis), into one body only."""
    base = comp.xYConstructionPlane if plane == "z" else comp.yZConstructionPlane
    pl = offset_plane(comp, base, coord, "PLANE - %s" % name)
    sk = comp.sketches.add(pl)
    sk.name = "HOLES - " + name
    dims, gc = sk.sketchDimensions, sk.geometricConstraints
    axes = ("x", "y") if plane == "z" else ("y", "z")
    for u, v in centres:
        mv = {axes[0]: ctx.ev(u), axes[1]: ctx.ev(v), plane: ctx.ev(coord)}
        cen = sk.modelToSketchSpace(adsk.core.Point3D.create(mv["x"] * MM, mv["y"] * MM, mv["z"] * MM))
        c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cen.x, cen.y, 0),
                                                            ctx.ev(dia) / 2 * MM)
        g = c.centerSketchPoint.geometry
        dims.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = dia
        for model_axis, expr in ((axes[0], u), (axes[1], v)):
            sa, _sign = model_to_sketch_axis(sk, model_axis)
            if abs(ctx.ev(expr)) < EPS:
                (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(c.centerSketchPoint, sk.originPoint)
            else:
                tp = adsk.core.Point3D.create(g.x + 0.6, g.y + 0.6, 0)
                dims.addDistanceDimension(sk.originPoint, c.centerSketchPoint, H if sa == "x" else V,
                                          tp).parameter.expression = "abs(%s)" % expr
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: HOLES - " + name)
    coll = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        coll.add(pr)
    n = sk.xDirection.crossProduct(sk.yDirection)
    normal = n.z if plane == "z" else n.x
    ei = comp.features.extrudeFeatures.createInput(coll, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(depth)),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if normal * into > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


def pattern(comp, feature, axis, n, pitch, name):
    """Rectangular pattern of one feature along a component axis: n instances, pitch apart
    (both expressions), toward +axis."""
    coll = adsk.core.ObjectCollection.create()
    coll.add(feature)
    ax = {"x": comp.xConstructionAxis, "y": comp.yConstructionAxis, "z": comp.zConstructionAxis}[axis]
    pi = comp.features.rectangularPatternFeatures.createInput(
        coll, ax, vi(n), vi(pitch), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    try:
        # identical copies: every instance cuts the same flat wall, and it computes much faster
        pi.patternComputeOption = adsk.fusion.PatternComputeOptions.IdenticalPatternCompute
    except Exception:
        pass
    f = comp.features.rectangularPatternFeatures.add(pi)
    f.name = "PATTERN - " + name
    return f


def edge_at(body, along, fixed, ctx_tol=0.005):
    """The straight edge of a body that runs along the model axis `along` with its other two
    coordinates at fixed = {axis: value in mm}."""
    for e in body.edges:
        a, b = e.startVertex.geometry, e.endVertex.geometry
        pa = {"x": a.x * 10, "y": a.y * 10, "z": a.z * 10}
        pb = {"x": b.x * 10, "y": b.y * 10, "z": b.z * 10}
        if all(abs(pa[k] - v) < ctx_tol and abs(pb[k] - v) < ctx_tol for k, v in fixed.items()) \
                and abs(pa[along] - pb[along]) > 1.0:
            return e
    raise RuntimeError("no edge along %s at %s on %s" % (along, fixed, body.name))


def chamfer(comp, edges, dist, name):
    coll = adsk.core.ObjectCollection.create()
    for e in edges:
        coll.add(e)
    cf = comp.features.chamferFeatures
    try:
        ci = cf.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll, vi(dist), False)
    except Exception:
        ci = cf.createInput(coll, False)
        ci.setToEqualDistance(vi(dist))
    f = cf.add(ci)
    f.name = "CHAMFER - " + name
    return f


def hollow(comp, body, axis, name):
    """Shell a box member into a tube: open both ends, wall tube_t inside."""
    ends = []
    for f in body.faces:
        if f.geometry.objectType != adsk.core.Plane.classType():
            continue
        n = f.geometry.normal
        if abs({"x": n.x, "y": n.y}[axis]) > 0.99:
            ends.append(f)
    if len(ends) != 2:
        raise RuntimeError("%s: expected 2 end faces, found %d" % (name, len(ends)))
    coll = adsk.core.ObjectCollection.create()
    for f in ends:
        coll.add(f)
    si = comp.features.shellFeatures.createInput(coll, False)
    si.insideThickness = vi("tube_t")
    f = comp.features.shellFeatures.add(si)
    f.name = "SHELL - %s TUBE" % name
    return f


def model_to_sketch_axis(sk, model_axis):
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return ("x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"), (1 if (e.x - o.x + e.y - o.y) > 0 else -1)


def poly_xz(comp, name, pts, ctx):
    """Closed polygon on the XZ plane, every corner dimensioned from the origin
    (pts = [(x_expr, z_expr)]); returns the sketch (fully constrained)."""
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = name
    sp = [sk.modelToSketchSpace(adsk.core.Point3D.create(ctx.ev(x) * MM, 0, ctx.ev(z) * MM)) for x, z in pts]
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
    ax_x, _sx = model_to_sketch_axis(sk, "x")
    expr_index = {ax_x: 0, ("y" if ax_x == "x" else "x"): 1}
    for sa in ("x", "y"):
        group = list(range(n))

        def root(i):
            while group[i] != i:
                i = group[i]
            return i
        for i, ln in enumerate(edges):
            a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs((a.x - b.x) if sa == "x" else (a.y - b.y)) < 1e-7:
                (gc.addVertical if sa == "x" else gc.addHorizontal)(ln)
                group[root((i + 1) % n)] = root(i)
        for i in range(n):
            if root(i) != i:
                continue
            ex = pts[i][expr_index[sa]]
            vp = verts[i]
            if abs(ctx.ev(ex)) < EPS:
                (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(vp, sk.originPoint)
            else:
                g = vp.geometry
                tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
                dims.addDistanceDimension(sk.originPoint, vp, H if sa == "x" else V, tp).parameter.expression = \
                    "abs(%s)" % ex
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + name)
    return sk


def extrude_y(comp, sk, y0, y1, name):
    """Extrude all profiles of an XZ sketch along +Y from y0 to y1 (new body)."""
    n = sk.xDirection.crossProduct(sk.yDirection)
    sign = 1 if n.y > 0 else -1
    coll = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        coll.add(pr)
    ei = comp.features.extrudeFeatures.createInput(coll, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi("(%s) * (%d)" % (y0, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("(%s) - (%s)" % (y1, y0))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - " + name
    return f


# ---------------------------------------------------------------- components and placement

def new_comp(parent, key, ctx, sheet_metal=False):
    pn, name, vn, kind, _mat = M.PARTS[key]
    tr = adsk.core.Matrix3D.create()
    occ = (parent.occurrences.addNewSheetMetalComponent(tr) if sheet_metal
           else parent.occurrences.addNewComponent(tr))
    c = occ.component
    c.name = "%s %s" % (pn, name)
    c.partNumber = pn
    c.description = "%s | %s | %s | %s" % (name, vn, kind, M.REV)
    return occ, c


def place(parent, occ, xyz, name, ctx):
    """Rigid joint: the occurrence's origin onto a sketch point at xyz (expressions,
    in the parent's frame). Returns the joint."""
    plane = offset_plane(parent, parent.xYConstructionPlane, xyz[2], "PLANE - PLACE %s" % name)
    sk = parent.sketches.add(plane)
    sk.name = "PLACE - " + name
    pt = sk.sketchPoints.add(adsk.core.Point3D.create(ctx.ev(xyz[0]) * MM, ctx.ev(xyz[1]) * MM, 0))
    dim_point(sk, pt, xyz[0], xyz[1], ctx)
    if not sk.isFullyConstrained:
        raise RuntimeError("placement sketch not fully constrained: " + name)
    g_occ = adsk.fusion.JointGeometry.createByPoint(
        occ.component.originConstructionPoint.createForAssemblyContext(occ))
    g_par = adsk.fusion.JointGeometry.createByPoint(pt)
    ji = parent.joints.createInput(g_occ, g_par)
    ji.setAsRigidJointMotion()
    j = parent.joints.add(ji)
    j.name = "PLACE - " + name
    return j


def material(ctx, key):
    name, density, _st, _src = M.MATERIALS[key]
    d = ctx.design
    m = d.materials.itemByName(name)
    if m is None:
        lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
        base = lib.materials.itemByName("Steel" if key in ("steel",) else "Aluminum")
        m = d.materials.addByCopy(base, name)
        m.materialProperties.itemById("structural_Density").value = density
    return m


def set_material(comp, ctx, key):
    m = material(ctx, key)
    for b in comp.bRepBodies:
        b.material = m


# ---------------------------------------------------------------- the parts

def build_frame_bodies(comp, half, ctx):
    """The members (tubes), then the site-joint holes as patterned cuts (J-CEIL-01, J-CEIL-02,
    joints register 2.9), the spigot hole and slot, and the 1 x 45 lead-in on the closing face."""
    s = M.side_sign(half)
    bodies = {}
    for code, name, axis, b in M.frame_members(half):
        body = box_body(comp, "%s %s" % (half, name), b, ctx)
        hollow(comp, body, axis, "%s %s" % (half, name))
        bodies[code] = body
    into = {("SIDE", "out"): -s, ("SIDE", "in"): s, ("SEAM", "out"): s, ("SEAM", "in"): -s}
    for name, member, face, (x, y, z), dia, n, pitch, axis in M.joint_holes(half):
        label = "%s %s" % (half, name)
        # one sketch per row: hole k at the row's first centre + k pitches (the start, pitch and
        # count are the skeleton's named values, so a rebuild follows them; Fusion's identical
        # pattern can't paste onto these hollow tubes, and an adjusted one is too slow)
        count = int(round(M.ev(ctx.vals, n)))
        def at(e, a):
            return e if a != axis else "(%s) + %d * (%s)" % (e, k, pitch)
        cs = []
        for k in range(count):
            cs.append((at(x, "x"), at(y, "y")) if face == "bottom" else (at(y, "y"), at(z, "z")))
        if face == "bottom":
            circles_cut(comp, bodies[member], label, "z", z, cs, dia, "2 * tube_t", 1, ctx)
        else:
            circles_cut(comp, bodies[member], label, "x", x, cs, dia, "2 * tube_t", into[(member, face)], ctx)
    sx, sy, sz, sw, sl = M.spigot_slot(half)
    label = "%s BACK SPIGOT SLOT" % half
    half_run = "(%s - %s) / 2" % (sl, sw)
    box_body(comp, label, ("%s - %s" % (sx, half_run), "%s + %s" % (sx, half_run), "%s - %s / 2" % (sy, sw),
                           "%s + %s / 2" % (sy, sw), sz, "%s + 2 * tube_t" % sz), ctx,
             op=adsk.fusion.FeatureOperations.CutFeatureOperation, bodies=[bodies["BACK"]])
    for end, sign in (("END 1", "-"), ("END 2", "+")):
        circle_cut(comp, bodies["BACK"], "%s %s" % (label, end), "%s %s %s" % (sx, sign, half_run), sy, sw, sz,
                   "%s + 2 * tube_t" % sz, ctx)
    xs, z0 = ctx.ev(M.xr(half, "0 mm", "tube_w")[1 if s < 0 else 0]), ctx.ev(M.ZF0)
    for code in ("SEAM", "BACK"):
        chamfer(comp, [edge_at(bodies[code], "y", {"x": xs, "z": z0})], "lead_in",
                "%s %s LEAD-IN ON THE CLOSING FACE" % (half, code))
    return bodies


def build_frame(assy, half, ctx):
    key = "frame_c1" if half == "C1" else "frame_c2"
    occ, comp = new_comp(assy, key, ctx)
    build_frame_bodies(comp, half, ctx)
    set_material(comp, ctx, "al")
    return occ, comp


def build_skin_bodies(comp, key, ctx):
    body = box_body(comp, "SKIN ACP 3", M.skin_box(), ctx)
    if key == "skin_c2":
        box_body(comp, "ROOF SLOT", M.roof_slot_box(), ctx, op=adsk.fusion.FeatureOperations.CutFeatureOperation,
                 bodies=[body])
    return body


def build_skin(assy, key, ctx):
    occ, comp = new_comp(assy, key, ctx)
    build_skin_bodies(comp, key, ctx)
    set_material(comp, ctx, "acp")
    return occ, comp


def build_tray(cass_occ_root, cass_comp, ctx):
    """Sheet metal tray in CS-510301. The tray occurrence is activated through the
    first cassette occurrence (edge flanges need the active component)."""
    occ, comp = new_comp(cass_comp, "tray", ctx, sheet_metal=True)
    d = ctx.design
    rule = d.designSheetMetalRules.itemByName("GALV STEEL 0.5 - CEILING TRAY")
    if rule is None:
        rule = d.designSheetMetalRules.addByCopy(comp.activeSheetMetalRule, "GALV STEEL 0.5 - CEILING TRAY")
    # A sheet metal rule takes values and its own names (Thickness), not user parameters
    # (Fusion 2706.1: "Invalid expression"), so the build writes tray_t's value into it.
    rule.thickness.expression = "%.4f mm" % ctx.ev("tray_t")
    rule.bendRadius.expression = "Thickness"      # = tray_t (bend_r, 1 x t); rule values only take rule names
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    comp.activeSheetMetalRule = rule
    proxy = occ.createForAssemblyContext(cass_occ_root) if cass_occ_root is not None else occ
    proxy.activate()
    try:
        sk = rect_sketch(comp, comp.xYConstructionPlane, "OUTLINE - TRAY BASE",
                         M.CS_X0, M.CS_X1, M.CS_Y0, M.CS_Y1, ctx)
        ff = comp.features.flangeFeatures
        bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
        bfi.orientation = adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation
        bf = ff.add(bfi)
        bf.name = "BASE - TRAY"
        body = bf.bodies.item(0)
        body.name = "TRAY"
        bot = -ctx.ev("tray_t")
        eds = [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
               and abs(e.startVertex.geometry.z * 10 - bot) < 0.01 and abs(e.endVertex.geometry.z * 10 - bot) < 0.01]
        if len(eds) != 4:
            raise RuntimeError("tray: expected 4 bottom edges, got %d" % len(eds))
        want = [ctx.ev(M.CS_X0), ctx.ev(M.CS_Y0), ctx.ev(M.CS_X1), ctx.ev(M.CS_Y1)]
        ret = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType,
                    adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            # the lip bend adds bend_r + tray_t below the return, so the tray ends at tray_h
            efi = ff.createEdgeFlangeInput([], vi("tray_h - tray_t - bend_r"))
            for e in eds:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            efi.bendPositionType = pos
            ef = ff.add(efi)
            b = body_box(comp.bRepBodies.item(0))
            got = [b[0], b[1], b[3], b[4]]
            print("tray returns, bend position %d: box %s" % (pos, b))
            if all(abs(g - w) < 0.05 for g, w in zip(got, want)):
                ret = ef
                break
            ef.deleteMe()
        if ret is None:
            raise RuntimeError("tray: no bend position keeps the outer faces on the outline")
        ret.name = "FLANGE - TRAY RETURNS"
        body = comp.bRepBodies.item(0)
        b = body_box(body)
        zlo = b[2]
        eds = [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
               and abs(e.startVertex.geometry.z * 10 - zlo) < 0.01 and abs(e.endVertex.geometry.z * 10 - zlo) < 0.01]

        def on_outline(e):
            s = e.startVertex.geometry
            return min(abs(s.x * 10 - b[0]), abs(s.x * 10 - b[3]), abs(s.y * 10 - b[1]), abs(s.y * 10 - b[4])) < 0.05
        inner = [e for e in eds if not on_outline(e) and e.length * 10 > 100]
        if len(inner) != 4:
            raise RuntimeError("tray: expected 4 inner bottom edges, got %d" % len(inner))
        lip = None
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput([], vi("lip_w"))
            for e in inner:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = body_box(comp.bRepBodies.item(0))
            inside = abs(b2[0] - b[0]) < 0.05 and abs(b2[3] - b[3]) < 0.05 and abs(b2[1] - b[1]) < 0.05 \
                and abs(b2[4] - b[4]) < 0.05 and abs(b2[2] - (-ctx.ev("tray_h"))) < 0.05
            print("tray lips, flipped %s: box %s, %s" % (flip, b2, "inside" if inside else "rejected"))
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("tray: no lip direction keeps the lips inside the outline at the tray height")
        lip.name = "FLANGE - TRAY LIPS UNDER THE FELT"
        # cable holes in the front and back returns, on the centre line, mid gap
        body = comp.bRepBodies.item(0)
        for tag, yexpr in (("FRONT", M.CS_Y0), ("BACK", M.CS_Y1)):
            pin = comp.constructionPlanes.createInput()
            pin.setByOffset(comp.xZConstructionPlane, vi(yexpr))
            pl = comp.constructionPlanes.add(pin)
            pl.name = "PLANE - CABLE HOLE %s" % tag
            pl.isLightBulbOn = False
            sk = comp.sketches.add(pl)
            sk.name = "HOLE - CABLE %s RETURN" % tag
            zc = "-(tray_t + gap_h / 2)"
            p3 = sk.modelToSketchSpace(adsk.core.Point3D.create(0, ctx.ev(yexpr) * MM, ctx.ev(zc) * MM))
            c = sk.sketchCurves.sketchCircles.addByCenterRadius(p3, ctx.ev("cable_hole") / 2 * MM)
            g = c.centerSketchPoint.geometry
            sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = "cable_hole"
            sk.geometricConstraints.addVerticalPoints(c.centerSketchPoint, sk.originPoint) \
                if model_to_sketch_axis(sk, "x")[0] == "x" else sk.geometricConstraints.addHorizontalPoints(c.centerSketchPoint, sk.originPoint)
            orient = V if model_to_sketch_axis(sk, "z")[0] == "y" else H
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c.centerSketchPoint, orient,
                                                     adsk.core.Point3D.create(g.x + 1, g.y - 1, 0)).parameter.expression = "tray_t + gap_h / 2"
            if not sk.isFullyConstrained:
                raise RuntimeError("sketch not fully constrained: " + sk.name)
            prof = sk.profiles.item(0)
            ei = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
            ei.setSymmetricExtent(vi("4 * tray_t"), True)
            ei.participantBodies = [body]
            f = comp.features.extrudeFeatures.add(ei)
            f.name = "CUT - CABLE HOLE %s RETURN (D-41)" % tag
    finally:
        ctx.design.activateRootComponent()
    set_material(comp, ctx, "steel")
    return occ, comp


def build_rib(cass_comp, ctx):
    """Hat-section rib in its own frame: centre line X = 0, from Y = 0 to rib_len,
    top flanges at Z = 0 (against the tray base underside), crown at Z = -gap_h."""
    occ, comp = new_comp(cass_comp, "rib", ctx)
    c, f, t, h = "rib_crown / 2", "rib_fl", "tray_t", "gap_h"
    pts = [("-(%s + %s)" % (c, f), "0 mm"), ("-(%s - %s)" % (c, t), "0 mm"), ("-(%s - %s)" % (c, t), "-(%s - %s)" % (h, t)),
           ("(%s - %s)" % (c, t), "-(%s - %s)" % (h, t)), ("(%s - %s)" % (c, t), "0 mm"), ("(%s + %s)" % (c, f), "0 mm"),
           ("(%s + %s)" % (c, f), "-%s" % t), ("(%s)" % c, "-%s" % t), ("(%s)" % c, "-(%s)" % h),
           ("-(%s)" % c, "-(%s)" % h), ("-(%s)" % c, "-%s" % t), ("-(%s + %s)" % (c, f), "-%s" % t)]
    sk = poly_xz(comp, "SECTION - RIB HAT", pts, ctx)
    fe = extrude_y(comp, sk, "0 mm", "cs_d - 2 * tray_t - 2 * rib_end", "RIB")
    fe.bodies.item(0).name = "RIB"
    set_material(comp, ctx, "steel")
    return occ, comp


def build_felt(cass_comp, ctx):
    occ, comp = new_comp(cass_comp, "felt", ctx)
    b = ("-(cs_w / 2 - tray_t - felt_c)", "(cs_w / 2 - tray_t - felt_c)",
         "(%s + tray_t + felt_c)" % M.CS_Y0, "(%s - tray_t - felt_c)" % M.CS_Y1, M.FELT_Z0, M.FELT_Z1)
    body = box_body(comp, "FELT 9", b, ctx)
    # reserved sprinkler zones (REQ-US-01): fully constrained sketches, nothing cut
    for i, (x, y) in enumerate(M.sprinkler_points()):
        pl = offset_plane(comp, comp.xYConstructionPlane, M.FELT_Z0, "PLANE - SPRINKLER ZONE %d" % (i + 1))
        sk = comp.sketches.add(pl)
        sk.name = "RESERVE - SPRINKLER ZONE %d (REQ-US-01)" % (i + 1)
        cc = sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(ctx.ev(x) * MM, ctx.ev(y) * MM, 0), ctx.ev("sprk_d") / 2 * MM)
        cc.isConstruction = True
        g = cc.centerSketchPoint.geometry
        sk.sketchDimensions.addDiameterDimension(cc, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = "sprk_d"
        dim_point(sk, cc.centerSketchPoint, x, y, ctx)
        if not sk.isFullyConstrained:
            raise RuntimeError("sketch not fully constrained: " + sk.name)
    set_material(comp, ctx, "felt")
    return occ, comp


def build_fill(cass_comp, key, bay_box, notches, ctx):
    """A fill strip in its own frame: X centred, Y from its front edge, Z from the tray top."""
    occ, comp = new_comp(cass_comp, key, ctx)
    y0 = bay_box[2]
    length = "(%s) - (%s)" % (bay_box[3], y0)
    body = box_body(comp, "FILL 40", ("-fill_hw", "fill_hw", "0 mm", length, "0 mm", "fill_t"), ctx)
    for name, nb in notches:
        loc = (nb[0], nb[1], "(%s) - (%s)" % (nb[2], y0), "(%s) - (%s)" % (nb[3], y0), "0 mm", "fill_t")
        box_body(comp, "NOTCH %s" % name, loc, ctx, op=adsk.fusion.FeatureOperations.CutFeatureOperation, bodies=[body])
    set_material(comp, ctx, "fill")
    return occ, comp


def build_hold(cass_comp, key, b, ctx):
    occ, comp = new_comp(cass_comp, key, ctx)
    box_body(comp, "HOLD ENVELOPE", b, ctx)
    set_material(comp, ctx, "hold")
    return occ, comp


def build_cassette_contents(cass, cass_occ, ctx):
    """Tray, felt, ribs, fill strips, clip and catch spaces inside the cassette
    component `cass` (CS-510301). cass_occ is its first occurrence in the root,
    or None when `cass` is the root itself (the cassette-only design)."""
    _tray_occ, tray_comp = build_tray(cass_occ, cass, ctx)
    print("step tray done")
    felt_occ, _felt = build_felt(cass, ctx)
    rib_occ, rib = build_rib(cass, ctx)
    rib_y = "%s + tray_t + rib_end" % M.CS_Y0
    place(cass, rib_occ, ("-rib_off", rib_y, "-tray_t"), "RIB L", ctx)
    rib_occ2 = cass.occurrences.addExistingComponent(rib, adsk.core.Matrix3D.create())
    place(cass, rib_occ2, ("rib_off", rib_y, "-tray_t"), "RIB R", ctx)
    # an occurrence without a joint stayed at its world position when the cassette was
    # placed (build run 9), so the felt gets a joint at the cassette origin too
    place(cass, felt_occ, ("0 mm", "0 mm", "0 mm"), "FELT", ctx)
    fill_occ = {}
    for key, bay, bbox, notches in M.fill_strips(ctx.vals):
        vals = ctx.vals
        sb = tuple(M.ev(vals, e) for e in bbox)
        use = [(n, nb) for n, nb in notches if M.overlap(sb, tuple(M.ev(vals, e) for e in nb))]
        if key in fill_occ:
            o = cass.occurrences.addExistingComponent(fill_occ[key], adsk.core.Matrix3D.create())
        else:
            o, c = build_fill(cass, key, bbox, use, ctx)
            fill_occ[key] = c
        place(cass, o, ("0 mm", bbox[2], "0 mm"), "FILL BAY %d" % bay, ctx)
    clip_comp = None
    for name, b in M.clip_boxes():
        if clip_comp is None:
            o, clip_comp = build_hold(cass, "clip", ("-clip_w / 2", "clip_w / 2", "0 mm", "clip_d", "0 mm", "clip_h"), ctx)
        else:
            o = cass.occurrences.addExistingComponent(clip_comp, adsk.core.Matrix3D.create())
        xc = "(%s) + clip_w / 2" % b[0]
        place(cass, o, (xc, b[2], "0 mm"), name, ctx)      # origin on the member's back face
    catch_comp = None
    for name, b in M.catch_boxes():
        if catch_comp is None:
            o, catch_comp = build_hold(cass, "catch", ("-catch_w / 2", "catch_w / 2", "-catch_d", "0 mm", "0 mm", "catch_h"), ctx)
        else:
            o = cass.occurrences.addExistingComponent(catch_comp, adsk.core.Matrix3D.create())
        xc = "(%s) + catch_w / 2" % b[0]
        place(cass, o, (xc, b[3], "0 mm"), name, ctx)      # origin on the member's front face
    return tray_comp


# ---------------------------------------------------------------- checks

def body_box(body):
    b = body.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def all_bodies(root):
    """(path name, body proxy in root context) for every body under every occurrence."""
    out = []
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out.append(("%s/%s" % (occ.fullPathName, b.name), b))
    return out


def clash_check(bodies, allowed=()):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            (na, a), (nb, b) = bodies[i], bodies[j]
            ba, bb = body_box(a), body_box(b)
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(a), tbm.copy(b)
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((na, nb, round(vol, 1)))
    return hits


# ---------------------------------------------------------------- save and export

def clear_design(design):
    """Empty the active design, so a rebuild goes into the same cloud file as a new version.
    The whole timeline goes first (features, sketches, joints, occurrences), then the
    parameters, which nothing references any more."""
    root = design.rootComponent
    tl = design.timeline
    if tl.count:
        tl.moveToBeginning()
        tl.deleteAllAfterMarker()
    for j in list(root.joints):
        j.deleteMe()
    for occ in list(root.occurrences):
        occ.deleteMe()
    params = design.userParameters
    for _round in range(10):
        for i in range(params.count - 1, -1, -1):
            try:
                params.item(i).deleteMe()
            except Exception:
                pass
        if params.count == 0:
            break
    if params.count or root.occurrences.count or tl.count:
        raise RuntimeError("could not clear the design (%d parameters, %d occurrences, %d timeline items left)" % (
            params.count, root.occurrences.count, tl.count))


def export_all(design, tray_comp):
    root_dir = ARGS["repo_root"]
    em = design.exportManager
    out = {}
    for rel, mk in ((F3D_REL, em.createFusionArchiveExportOptions), (STEP_REL, em.createSTEPExportOptions)):
        path = os.path.join(root_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ok = False
        for _try in range(10):
            ok = em.execute(mk(path, design.rootComponent))
            if ok and os.path.getsize(path) > 2000:
                break
            adsk.doEvents()
            time.sleep(3)
        print("export %s: %s" % (rel, ok))
        if not ok:
            raise RuntimeError("export failed: " + rel)
        out[rel] = ok
    fp = tray_comp.flatPattern
    path = os.path.join(root_dir, DXF_RAW_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ok = em.execute(em.createDXFFlatPatternExportOptions(path, fp))
    print("export %s: %s" % (DXF_RAW_REL, ok))
    if not ok:
        raise RuntimeError("flat pattern export failed")
    return out


def make_flat_pattern(tray_comp):
    body = tray_comp.bRepBodies.item(0)
    top = max((f for f in body.faces if f.geometry.objectType == adsk.core.Plane.classType()
               and f.geometry.normal.z > 0.99), key=lambda f: f.area)
    fp = tray_comp.flatPattern or tray_comp.createFlatPattern(top)
    fb = fp.flatBody
    print("FLAT|513101|%s" % body_box(fb))
    return fp


def run_part(app, doc, design, root, scope, ctx):
    """A part-only design for a drawing (a Fusion drawing shows its whole design):
    the same build functions, the part alone in its own frame. Checks: timeline,
    sketches, clashes. The source of record stays 410000_P01_CEILING_CAD."""
    pn, name, vn, kind, _m = M.PARTS[scope]
    root.partNumber = pn
    root.description = "%s | %s | %s | %s | drawing source, built by ceiling_build.py" % (name, vn, kind, M.REV)
    tray_comp = None
    if scope == "cassette":
        tray_comp = build_cassette_contents(root, None, ctx)
    elif scope == "tray":
        _o, tray_comp = build_tray(None, root, ctx)
    elif scope == "rib":
        build_rib(root, ctx)
    elif scope == "felt":
        build_felt(root, ctx)
    elif scope in ("frame_c1", "frame_c2"):
        build_frame_bodies(root, "C1" if scope == "frame_c1" else "C2", ctx)
        set_material(root, ctx, "al")
    elif scope in ("skin_c1", "skin_c2"):
        build_skin_bodies(root, scope, ctx)
        set_material(root, ctx, "acp")
    elif scope in ("assy_c1", "assy_c2"):
        half = "C1" if scope == "assy_c1" else "C2"
        build_frame(root, half, ctx)
        skin_occ, _skin = build_skin(root, "skin_c1" if half == "C1" else "skin_c2", ctx)
        place(root, skin_occ, M.SKIN_PLACES[half], "SKIN " + half, ctx)
    else:
        for key, bay, bbox, notches in M.fill_strips(ctx.vals):
            if key == scope:
                sb = tuple(M.ev(ctx.vals, e) for e in bbox)
                use = [(n, nb) for n, nb in notches if M.overlap(sb, tuple(M.ev(ctx.vals, e) for e in nb))]
                build_fill(root, key, bbox, use, ctx)
                break
        else:
            raise RuntimeError("no fill strip of kind %s in this layout" % scope)
    adsk.doEvents()
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [c.name + "/" + sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
    bodies = all_bodies(root) + [("root/" + b.name, b) for b in root.bRepBodies]
    hits = clash_check(bodies)
    print("PART %s %s: timeline %d items, unhealthy %d, loose sketches %d, bodies %d, clashes %d, box %s" % (
        pn, name, tl.count, len(bad), len(loose), len(bodies), len(hits), body_box(root)))
    if bad or loose or hits:
        raise RuntimeError("part checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, hits))
    if tray_comp is not None:
        make_flat_pattern(tray_comp)
    design.activateRootComponent()
    if ARGS.get("save") == "1":
        print("saved:", doc.save("%s %s drawing source, skeleton %s" % (pn, M.REV, M.SKELETON_REV)))
        adsk.doEvents()


FOLDER = "Default Project/FocusPod v2"


def open_or_create(app, name):
    """The design called `name` in FOLDER: activate it if open, open it from the cloud, or make
    it there (the same steps as run_script.py --doc NAME --doc-new)."""
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name.split(" v")[0] == name:
            d.activate()
            return d, "activated"
    parts = [p for p in FOLDER.split("/") if p]
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == parts[0])
    folder = proj.rootFolder
    for n in parts[1:]:
        folder = folder.dataFolders.itemByName(n)
    found, unreadable = [], 0
    for i in range(folder.dataFiles.count):
        try:
            f = folder.dataFiles.item(i)
            if f.name == name:
                found.append(f)
        except RuntimeError:
            unreadable += 1
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
    if not d.saveAs(name, folder, "new, made by ceiling_build.py parts=", ""):
        raise RuntimeError("saveAs %r failed" % name)
    d.activate()
    return d, "made"


def run_parts(app, scopes):
    """Several part-only designs in one run (fair-share queue rule, PM ruling 2026-11-01)."""
    for scope in scopes:
        if scope not in SCOPES:
            raise RuntimeError("scope must be one of %s" % (SCOPES,))
        t0 = time.time()
        doc, how = open_or_create(app, part_doc_name(scope))
        design = adsk.fusion.Design.cast(app.activeProduct)
        clear_design(design)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        ctx = Ctx(design)
        params = M.all_params()
        for name, expr, unit, status, src in params:
            design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = M.evaluate(params)
        run_part(app, doc, design, design.rootComponent, scope, ctx)       # checks, then saves (save=1)
        print("part %s (%s) in %.0f s" % (scope, how, time.time() - t0))
        doc.close(False)


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("parts"):
        run_parts(app, [k for k in ARGS["parts"].split(",") if k])
        return
    if ARGS.get("close_previous") == "1":
        for i in range(app.documents.count - 1, -1, -1):
            d = app.documents.item(i)
            if d.objectType != adsk.fusion.FusionDocument.classType():
                continue
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            if dd and not d.isSaved and dd.rootComponent.partNumber == "410000":
                d.close(False)
    scope = ARGS.get("scope", "")
    if scope and scope not in SCOPES:
        raise RuntimeError("scope must be one of %s" % (SCOPES,))
    doc_name = part_doc_name(scope) if scope else DOC_NAME
    into_active = ARGS.get("into_active") == "1"
    if into_active:
        doc = app.activeDocument
        if doc.name.split(" v")[0] != doc_name:
            raise RuntimeError("active document is %r, not %s (use the runner's --doc)" % (doc.name, doc_name))
    else:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    keep = ARGS.get("keep") == "1" or into_active
    ok = False
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if into_active:
            clear_design(design)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        ctx = Ctx(design)
        if ARGS.get("skeleton_csv"):
            print("skeleton list from", ARGS["skeleton_csv"], "rev", M.use_skeleton(ARGS["skeleton_csv"]))
        params = M.all_params()
        for name, expr, unit, status, src in params:
            design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = M.evaluate(params)
        root = design.rootComponent
        root.partNumber = "410000"
        root.description = "CEILING | Trần | HS | " + M.REV
        stop = ARGS.get("stop_after", "")
        if scope:
            run_part(app, doc, design, root, scope, ctx)
            ok = True
            return

        t0 = time.time()

        def lap(what):
            print("step %s done at %.0f s" % (what, time.time() - t0))
        # outer panels
        assy = {}
        for half in ("C1", "C2"):
            o, c = new_comp(root, "assy_c1" if half == "C1" else "assy_c2", ctx)
            assy[half] = (o, c)
            build_frame(c, half, ctx)
        for half in ("C1", "C2"):
            skin_occ, _skin = build_skin(assy[half][1], "skin_c1" if half == "C1" else "skin_c2", ctx)
            place(assy[half][1], skin_occ, M.SKIN_PLACES[half], "SKIN " + half, ctx)
        lap("outer panels")
        if stop == "outer":
            raise StopIteration

        # the cassette (one component, two occurrences)
        cass_occ, cass = new_comp(root, "cassette", ctx)
        tray_comp = build_cassette_contents(cass, cass_occ, ctx)
        lap("cassette parts")
        place(root, cass_occ, M.CASSETTE_CS["C1"], "CASSETTE C1-CASS", ctx)
        cass_occ2 = root.occurrences.addExistingComponent(cass, adsk.core.Matrix3D.create())
        place(root, cass_occ2, M.CASSETTE_CS["C2"], "CASSETTE C2-CASS", ctx)
        adsk.doEvents()
        lap("placement")

        # ---- checks
        tl = design.timeline
        bad = [tl.item(i).name for i in range(tl.count)
               if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [c.name + "/" + s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
        bodies = all_bodies(root)
        print("timeline %d items, unhealthy %d, loose sketches %d, parameters %d, bodies %d" % (
            tl.count, len(bad), len(loose), design.userParameters.count, len(bodies)))
        for n, b in bodies:
            print("BODY|%s|%s" % (n, body_box(b)))
        full = ARGS.get("checks", "1") == "1"      # checks=0: ceiling_report.py checks the saved version
        hits = clash_check(bodies) if full else []
        print("clash pairs over 1 mm3: %s" % (len(hits) if full else "not checked (checks=0)"))
        for h in hits:
            print("CLASH|%s|%s|%s mm3" % h)
        for occ in root.allOccurrences:
            c = occ.component
            if c.bRepBodies.count:
                pp = c.getPhysicalProperties()
                print("MASS|%s|%s|%.3f kg" % (occ.fullPathName, c.partNumber, pp.mass))
        pos = C.check(design) if full else {"checked": 0, "worst": 0.0, "bad": []}
        print("position check: %d bodies against the layout, worst %.3f mm, off %s" % (
            pos["checked"], pos["worst"], pos["bad"] or "none"))
        holes = C.hole_check(design) if full else {"checked": 0, "worst": 0.0, "bad": []}
        print("hole check: %d joint holes against the register's positions, worst %.3f mm, off %s" % (
            holes["checked"], holes["worst"], holes["bad"] or "none"))
        lap("checks")
        if bad or loose or hits or pos["bad"] or holes["bad"]:
            raise RuntimeError("ceiling checks failed (unhealthy %s, loose %s, clashes %s, off layout %s, holes %s)" % (
                bad, loose, hits, pos["bad"], holes["bad"]))
        make_flat_pattern(tray_comp)
        design.activateRootComponent()
        if ARGS.get("save") == "1":
            if not into_active:
                raise RuntimeError("save=1 needs into_active=1 with the runner's --doc %s --doc-new" % doc_name)
            print("saved:", doc.save("CEILING %s build, skeleton %s" % (M.REV, M.SKELETON_REV)))
            adsk.doEvents()
            lap("save")
        if ARGS.get("export") == "1":
            if ARGS.get("save") != "1":
                raise RuntimeError("export=1 needs save=1, so the exports come from a saved version")
            export_all(design, tray_comp)
        ok = True
    except StopIteration:
        print("stopped after", ARGS.get("stop_after"))
        ok = True
    finally:
        if not keep:
            doc.close(False)
    if not ok:
        raise RuntimeError("build did not finish")
