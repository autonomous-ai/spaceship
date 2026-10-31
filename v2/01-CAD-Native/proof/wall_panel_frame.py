"""FocusPod v2 proof part: WALL - PANEL FRAME - SIDE LOWER - LH (PROPOSED).

A native, parametric Fusion design built from named user parameters, fully
constrained sketches on defined planes and named features. Run it with:

    python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/wall_panel_frame.py

It opens a NEW design document and never touches other documents. Each step
is measured and printed (bounding boxes, hole count and hole centres, sketch
constraint state) so the result can be checked against the intent.

Options (--arg KEY=VALUE):
    stop_after=N      stop after step N (1..9) for step-by-step checks
    close_previous=1  first close an unsaved document left by an earlier run
                      (same root part number, never saved); nothing else
    save=1            save to the Fusion cloud: Default Project / FocusPod v2
                      (refuses if a file of the same name is already there)
    export=1          export .f3d and STEP into the repo, then re-read the STEP
                      in a new document and compare bounding boxes (runs
                      before save=1)
    export_active=1   no build: re-export the open, unmodified proof document

Part coordinate system (right-handed, mm), shown for the left-hand (LH) wall:
origin O = front-bottom corner of the frame's outer face. +X along the wall
toward the back of the pod, +Y outward (toward the skin), +Z up. So Fusion's
"Front" view looks at the frame from inside the pod. Datums: A = frame outer
face (Y = 0, the skin side), B = bottom face (Z = 0), C = front face (X = 0);
all three meet at O. The frame sits in Y -20..0, the skin in Y 0..3. The RH
frame is the mirror image.

Every number in PARAMS carries its status (SOURCE, CALCULATION, ASSUMPTION,
PROPOSED, HOLD) in its comment, which Fusion shows in the parameters dialog.
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
STOP_AFTER = int(ARGS.get("stop_after", "9"))

DOC_NAME = "V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH"
REV = "P01"

# name, expression, units, comment (status + source). Order matters: a
# parameter may only use parameters defined above it.
PARAMS = [
    ("frame_width", "1470 mm", "mm",
     "Frame outer width along X. CALCULATION: side wall depth 1500 (SOURCE: build plan II) "
     "- rear skin overhang 30."),
    ("frame_height", "1150 mm", "mm",
     "Frame outer height along Z. CALCULATION: wall height 2300 (SOURCE: v1 BOM, walls 2300 tall) "
     "/ 2 frames (SOURCE: build plan II). HOLD: a thin floor would make walls about 80 taller."),
    ("tube_size", "20 mm", "mm",
     "Square tube outside size. SOURCE: build plan VT10, box section 20x20."),
    ("tube_wall", "1.2 mm", "mm",
     "Tube wall thickness. ASSUMPTION: plan gives none; 1.2 is a common 20x20 steel wall "
     "(about 1.5 for aluminium). UNVERIFIED with a supplier."),
    ("frame_material", "'Steel'", "Text",
     "Tube material, 'Steel' (SOURCE: build plan VT10) or 'Aluminum' (PROPOSED in v2 plan). "
     "The build script maps it to a Fusion material."),
    ("hole_dia", "6.6 mm", "mm",
     "Joint hole for an M6 bolt. SOURCE: ISO 273 medium clearance for M6 = 6.6. "
     "Bolt M6x60 (SOURCE: build plan VT11)."),
    ("hole_edge_dist", "60 mm", "mm",
     "First and last hole centre from the frame outer edge. ASSUMPTION: stile 20 + weld 3 + "
     "washer radius 6 + wrench swing 25 = 54, rounded up. Check in the joint register."),
    ("rail_hole_pitch_max", "500 mm", "mm",
     "Largest pitch allowed between rail holes. ASSUMPTION until the joint and gasket "
     "calculation (J-WALL-01) sets it."),
    ("rail_hole_count", "ceil((frame_width - 2 * hole_edge_dist) / rail_hole_pitch_max) + 1", "",
     "CALCULATION: holes per rail, equal pitch, first and last at hole_edge_dist."),
    ("rail_hole_pitch", "(frame_width - 2 * hole_edge_dist) / (rail_hole_count - 1)", "mm",
     "CALCULATION: actual pitch of the rail holes."),
    ("stile_hole_pitch_max", "400 mm", "mm",
     "Largest pitch allowed between rear stile holes. ASSUMPTION until J-WALL-02."),
    ("stile_hole_count", "ceil((frame_height - 2 * hole_edge_dist) / stile_hole_pitch_max) + 1", "",
     "CALCULATION: holes in the rear stile, equal pitch."),
    ("stile_hole_pitch", "(frame_height - 2 * hole_edge_dist) / (stile_hole_count - 1)", "mm",
     "CALCULATION: actual pitch of the rear stile holes."),
    ("mid_rail_z", "frame_height / 2", "mm",
     "Height of the mid rail centre line. ASSUMPTION: halves the unsupported skin span."),
    ("skin_thk", "3 mm", "mm",
     "ACP skin thickness. SOURCE: build plan VT01, ACP 3 mm, Dark Yellow EV3038."),
    ("skin_overhang_rear", "30 mm", "mm",
     "Skin runs past the frame rear edge to cover the back wall edge. SOURCE: build plan joint "
     "detail, ACP 3 + ply 6 + frame 20 + gap 1."),
    ("skin_width", "frame_width + skin_overhang_rear", "mm",
     "CALCULATION: equals the side wall depth 1500."),
    ("skin_height", "frame_height", "mm",
     "ASSUMPTION: skin flush with the frame top and bottom. HOLD: seam gap to the upper panel."),
]

# key: (part number, English name, Vietnamese name). All PROPOSED until the
# control pack sets the v2 numbering.
PARTS = {
    "assy": ("V2-SWL-00", "WALL - PANEL ASSY - SIDE LOWER - LH", "Vách bên dưới - trái (cụm)"),
    "frame": ("V2-SWL-10", "WALL - PANEL FRAME - SIDE LOWER - LH", "Khung vách bên dưới - trái"),
    "stile_rear": ("V2-SWL-11", "WALL - FRAME STILE - REAR", "Thanh đứng sau"),
    "stile_front": ("V2-SWL-12", "WALL - FRAME STILE - FRONT", "Thanh đứng trước"),
    "rail_bottom": ("V2-SWL-13", "WALL - FRAME RAIL - BOTTOM", "Thanh ngang dưới"),
    "rail_top": ("V2-SWL-14", "WALL - FRAME RAIL - TOP", "Thanh ngang trên"),
    "rail_mid": ("V2-SWL-15", "WALL - FRAME RAIL - MID", "Thanh ngang giữa"),
    "skin": ("V2-SWL-20", "WALL - SKIN ACP 3 - SIDE LOWER - LH", "Tấm ốp ACP 3 mm (VT01)"),
}

CM = 0.1  # Fusion API lengths are in cm; multiply mm by CM


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def mm(v_cm):
    return round(v_cm * 10.0, 3)


def p3(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(x_mm * CM, y_mm * CM, z_mm * CM)


def pval(design, name):
    """Parameter value in mm (lengths) or as a plain number (unitless)."""
    p = design.userParameters.itemByName(name)
    return p.value * 10.0 if p.unit == "mm" else p.value


def bbox_mm(entity):
    b = entity.boundingBox
    return tuple(mm(v) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                 b.maxPoint.x, b.maxPoint.y, b.maxPoint.z))


def fmt_box(b):
    return "X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f" % (b[0], b[3], b[1], b[4], b[2], b[5])


# ---------------------------------------------------------------- sketches

def sketch_axis(sk, direction):
    """Which sketch axis a model direction maps to: ('x'|'y', sign)."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    d = adsk.core.Point3D.create(direction.x, direction.y, direction.z)
    e = sk.modelToSketchSpace(d)
    dx, dy = e.x - o.x, e.y - o.y
    if abs(dx) > abs(dy):
        return "x", 1 if dx > 0 else -1
    return "y", 1 if dy > 0 else -1


def orient(axis):
    return (adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation if axis == "x"
            else adsk.fusion.DimensionOrientations.VerticalDimensionOrientation)


def nearest_point(points, target):
    best, dist = None, None
    for sp in points:
        g = sp.geometry
        dd = (g.x - target.x) ** 2 + (g.y - target.y) ** 2
        if dist is None or dd < dist:
            best, dist = sp, dd
    return best


def rect_points(lines):
    pts = []
    for ln in lines:
        for sp in (ln.startSketchPoint, ln.endSketchPoint):
            if all(sp != q for q in pts):
                pts.append(sp)
    return pts


def add_dim(sk, a, b, axis, expr, text_offset):
    """Distance dimension between sketch points a and b along a sketch axis,
    driven by a parameter expression."""
    g1, g2 = a.geometry, b.geometry
    tp = adsk.core.Point3D.create((g1.x + g2.x) / 2 + text_offset[0],
                                  (g1.y + g2.y) / 2 + text_offset[1], 0)
    d = sk.sketchDimensions.addDistanceDimension(a, b, orient(axis), tp)
    d.parameter.expression = expr
    return d


def align_to_origin(sk, pt, axis):
    """Constrain pt to share the origin's coordinate across `axis`
    (i.e. pt lies on the origin's line running along the other axis)."""
    gc = sk.geometricConstraints
    if axis == "x":   # same sketch x as origin
        gc.addVerticalPoints(pt, sk.originPoint)
    else:             # same sketch y as origin
        gc.addHorizontalPoints(pt, sk.originPoint)


def place_corner(sk, pt, u, v, pos_u, pos_v):
    """Locate a corner point from the sketch origin along model directions
    u and v; pos_* is an expression, or None when that coordinate is 0."""
    (au, _), (av, _) = sketch_axis(sk, u), sketch_axis(sk, v)
    if pos_u is None and pos_v is None:
        sk.geometricConstraints.addCoincident(pt, sk.originPoint)
        return
    if pos_u is None:
        align_to_origin(sk, pt, au)
    else:
        add_dim(sk, sk.originPoint, pt, au, pos_u, (-1.5, -1.5))
    if pos_v is None:
        align_to_origin(sk, pt, av)
    else:
        add_dim(sk, sk.originPoint, pt, av, pos_v, (-1.5, -1.5))


def tube_section(sk, corner, u, v, size, wall, pos_u, pos_v):
    """Hollow square tube section in sketch sk, fully constrained.

    corner: model point (mm tuple) of the outer corner with the smallest u, v.
    u, v:   model unit vectors (Vector3D) spanning the section plane.
    size, wall: current values in mm (geometry is drawn at the right size so
            the dimensions never have to move it).
    pos_u, pos_v: expressions for the corner position from the origin along
            u and v (None when 0)."""
    def at(du, dv):
        return sk.modelToSketchSpace(adsk.core.Point3D.create(
            (corner[0] + du * u.x + dv * v.x) * CM,
            (corner[1] + du * u.y + dv * v.y) * CM,
            (corner[2] + du * u.z + dv * v.z) * CM))
    lines = sk.sketchCurves.sketchLines
    outer = lines.addTwoPointRectangle(at(0, 0), at(size, size))
    inner = lines.addTwoPointRectangle(at(wall, wall), at(size - wall, size - wall))
    for rect in (outer, inner):
        ensure_hv(sk, rect)
    o_pts, i_pts = rect_points(outer), rect_points(inner)
    o0, o_u, o_v = (nearest_point(o_pts, at(0, 0)), nearest_point(o_pts, at(size, 0)),
                    nearest_point(o_pts, at(0, size)))
    i0, i_u, i_v = (nearest_point(i_pts, at(wall, wall)), nearest_point(i_pts, at(size - wall, wall)),
                    nearest_point(i_pts, at(wall, size - wall)))
    (au, _), (av, _) = sketch_axis(sk, u), sketch_axis(sk, v)
    off = 0.6
    add_dim(sk, o0, o_u, au, "tube_size", (0, -off) if au == "x" else (-off, 0))
    add_dim(sk, o0, o_v, av, "tube_size", (0, -off) if av == "x" else (-off, 0))
    add_dim(sk, o0, i0, au, "tube_wall", (0, -off / 2) if au == "x" else (-off / 2, 0))
    add_dim(sk, o0, i0, av, "tube_wall", (0, -off / 2) if av == "x" else (-off / 2, 0))
    add_dim(sk, i0, i_u, au, "tube_size - 2 * tube_wall", (0, off / 3) if au == "x" else (off / 3, 0))
    add_dim(sk, i0, i_v, av, "tube_size - 2 * tube_wall", (0, off / 3) if av == "x" else (off / 3, 0))
    place_corner(sk, o0, u, v, pos_u, pos_v)
    return outer, inner


def ensure_hv(sk, rect):
    """Make sure the 4 rectangle lines are horizontal/vertical constrained."""
    gc = sk.geometricConstraints
    for ln in rect:
        has = False
        for c in ln.geometricConstraints:
            if c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                adsk.fusion.VerticalConstraint.classType()):
                has = True
        if not has:
            s, e = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs(s.y - e.y) < 1e-9:
                gc.addHorizontal(ln)
            else:
                gc.addVertical(ln)


def ring_profile(sk):
    for prof in sk.profiles:
        if prof.profileLoops.count == 2:
            return prof
    raise RuntimeError("no tube ring profile in " + sk.name)


def check_sketch(sk):
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return "%s: fully constrained (%d curves, %d dims)" % (
        sk.name, sk.sketchCurves.count, sk.sketchDimensions.count)


# ---------------------------------------------------------------- document

def find_component(design, key):
    want = PARTS[key][0]
    for comp in design.allComponents:
        if comp.partNumber == want:
            return comp
    raise RuntimeError("component not found: " + want)


def new_component(parent, key):
    pn, name, vn = PARTS[key]
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "%s %s" % (pn, name)
    comp.partNumber = pn
    comp.description = "%s | %s | rev %s | PROPOSED" % (name, vn, REV)
    return comp


def step1_document(app):
    """New design document, mm units, named user parameters, component tree."""
    if ARGS.get("close_previous") == "1":
        # only an unsaved document whose root part number is this assembly's
        for i in range(app.documents.count - 1, -1, -1):
            d = app.documents.item(i)
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            if dd and not d.isSaved and dd.rootComponent.partNumber == PARTS["assy"][0]:
                d.close(False)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    for name, expr, units, comment in PARAMS:
        p = design.userParameters.add(name, vi(expr), units, comment)
        if p is None:
            raise RuntimeError("could not add parameter " + name)
    root = design.rootComponent
    root.partNumber = PARTS["assy"][0]
    root.description = "%s | %s | rev %s | PROPOSED" % (PARTS["assy"][1], PARTS["assy"][2], REV)
    frame = new_component(root, "frame")
    for key in ("stile_rear", "stile_front", "rail_bottom", "rail_top", "rail_mid"):
        new_component(frame, key)
    new_component(root, "skin")
    print("step 1: document '%s', %d user parameters" % (doc.name, design.userParameters.count))
    for p in design.userParameters:
        v = p.textValue if p.valueType == adsk.fusion.ParameterValueTypes.TextParameterValueType \
            else ("%.3f %s" % (p.value * 10 if p.unit == "mm" else p.value, p.unit))
        print("  %-22s = %-14s [%s]" % (p.name, v, p.expression))
    print("  components:", ", ".join(c.name for c in design.allComponents))
    return doc, design


# ---------------------------------------------------------------- members

X = adsk.core.Vector3D.create(1, 0, 0)
Y = adsk.core.Vector3D.create(0, 1, 0)
Z = adsk.core.Vector3D.create(0, 0, 1)
INWARD = adsk.core.Vector3D.create(0, -1, 0)   # frame depth runs from Y = 0 to -tube_size


def stile(design, key, x_expr, label):
    """Vertical tube: section on the XY plane (outer face on datum A, Y = 0),
    extruded up by frame_height."""
    comp = find_component(design, key)
    T, t = pval(design, "tube_size"), pval(design, "tube_wall")
    x0 = 0.0 if x_expr is None else pval(design, "frame_width") - T
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SECTION - %s TUBE" % label
    tube_section(sk, (x0, 0, 0), X, INWARD, T, t, x_expr, None)
    msg = check_sketch(sk)
    ext_in = comp.features.extrudeFeatures.createInput(
        ring_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, vi("frame_height"))
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "EXTRUDE - %s TUBE" % label
    body = ext.bodies.item(0)
    body.name = "%s - TUBE" % PARTS[key][1]
    return body, msg


def rail(design, key, z_expr, z_mm, label):
    """Horizontal tube between the stiles: section on the YZ plane, extruded
    along +X from X = tube_size by frame_width - 2 * tube_size."""
    comp = find_component(design, key)
    T, t = pval(design, "tube_size"), pval(design, "tube_wall")
    sk = comp.sketches.add(comp.yZConstructionPlane)
    sk.name = "SECTION - %s TUBE" % label
    tube_section(sk, (0, 0, z_mm), INWARD, Z, T, t, None, z_expr)
    msg = check_sketch(sk)
    ext_in = comp.features.extrudeFeatures.createInput(
        ring_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.startExtent = adsk.fusion.OffsetStartDefinition.create(vi("tube_size"))
    ext_in.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("frame_width - 2 * tube_size")),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "EXTRUDE - %s TUBE" % label
    body = ext.bodies.item(0)
    body.name = "%s - TUBE" % PARTS[key][1]
    return body, msg


def report_bodies(design, keys):
    for key in keys:
        comp = find_component(design, key)
        for b in comp.bRepBodies:
            print("  %-34s %s" % (b.name, fmt_box(bbox_mm(b))))


def step2_stile_front(design):
    body, msg = stile(design, "stile_front", None, "STILE FRONT")
    print("step 2: front stile (on datums A, B, C).", msg)
    report_bodies(design, ["stile_front"])


def step3_stile_rear(design):
    body, msg = stile(design, "stile_rear", "frame_width - tube_size", "STILE REAR")
    print("step 3: rear stile.", msg)
    report_bodies(design, ["stile_rear"])


def step4_rails(design):
    H, T = pval(design, "frame_height"), pval(design, "tube_size")
    zmid = pval(design, "mid_rail_z") - T / 2
    out = []
    out.append(rail(design, "rail_bottom", None, 0.0, "RAIL BOTTOM")[1])
    out.append(rail(design, "rail_top", "frame_height - tube_size", H - T, "RAIL TOP")[1])
    out.append(rail(design, "rail_mid", "mid_rail_z - tube_size / 2", zmid, "RAIL MID")[1])
    print("step 4: rails.", "; ".join(out))
    report_bodies(design, ["rail_bottom", "rail_top", "rail_mid"])


# ---------------------------------------------------------------- holes

def hole_faces(body, dia_mm):
    """Cylindrical faces of the given diameter: (axis origin mm, axis dir)."""
    out = []
    for f in body.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and \
                abs(g.radius * 20.0 - dia_mm) < 0.01:
            out.append(((mm(g.origin.x), mm(g.origin.y), mm(g.origin.z)),
                        (round(g.axis.x, 3), round(g.axis.y, 3), round(g.axis.z, 3)), f))
    return out


def hole_centres(body, dia_mm, axis):
    """Unique hole axis positions (mm) on the two coordinates across `axis`."""
    idx = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
    pts = set()
    for org, _d, _f in hole_faces(body, dia_mm):
        pts.add((round(org[idx[0]], 2), round(org[idx[1]], 2)))
    return sorted(pts)


def hole_row(design, key, plane_base, plane_offset, pt_model, dims, count_expr, extent_expr,
             pattern_axis, label, reverse=False):
    """One parametric hole through both tube walls, patterned along an axis.
    The hole starts on the entry plane (the bolt-head side) and runs
    tube_size deep; reverse=True drills along the plane normal instead of
    against it."""
    comp = find_component(design, key)
    body = comp.bRepBodies.item(0)
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(plane_base(comp), vi(plane_offset))
    plane = planes.add(pin)
    plane.name = "PLANE - %s HOLE ENTRY FACE" % label
    sk = comp.sketches.add(plane)
    sk.name = "HOLE POSITION - %s" % label
    pt = sk.sketchPoints.add(sk.modelToSketchSpace(p3(*pt_model)))
    for direction, expr in dims:
        ax, _s = sketch_axis(sk, direction)
        add_dim(sk, sk.originPoint, pt, ax, expr, (1.0, 1.0))
    msg = check_sketch(sk)
    holes = comp.features.holeFeatures
    hin = holes.createSimpleInput(vi("hole_dia"))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi("tube_size"))
    if reverse:
        hin.isDefaultDirection = False
    hin.participantBodies = [body]
    hf = holes.add(hin)
    hf.name = "HOLE - M6 CLEARANCE - %s" % label
    coll = adsk.core.ObjectCollection.create()
    coll.add(hf)
    pats = comp.features.rectangularPatternFeatures
    patin = pats.createInput(coll, pattern_axis(comp), vi(count_expr), vi(extent_expr),
                             adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
    pat = pats.add(patin)
    pat.name = "PATTERN - %s HOLES" % label
    return body, msg


def step5_rail_holes(design):
    T, H, e = pval(design, "tube_size"), pval(design, "frame_height"), pval(design, "hole_edge_dist")
    dia = pval(design, "hole_dia")
    msgs = []
    # top rail: bolts come down from the upper frame; entry face = top face Z = frame_height
    b_top, m = hole_row(design, "rail_top", lambda c: c.xYConstructionPlane, "frame_height",
                        (e, -T / 2, H), [(X, "hole_edge_dist"), (Y, "tube_size / 2")],
                        "rail_hole_count", "frame_width - 2 * hole_edge_dist",
                        lambda c: c.xConstructionAxis, "TOP RAIL TO UPPER FRAME")
    msgs.append(m)
    # bottom rail: bolts go down into the base; entry face = top face Z = tube_size
    b_bot, m = hole_row(design, "rail_bottom", lambda c: c.xYConstructionPlane, "tube_size",
                        (e, -T / 2, T), [(X, "hole_edge_dist"), (Y, "tube_size / 2")],
                        "rail_hole_count", "frame_width - 2 * hole_edge_dist",
                        lambda c: c.xConstructionAxis, "BOTTOM RAIL TO BASE")
    msgs.append(m)
    print("step 5: rail holes.", "; ".join(msgs))
    for b in (b_top, b_bot):
        c = hole_centres(b, dia, "z")
        print("  %-34s %d holes (expect %d), centres X,Y: %s" % (
            b.name, len(c), int(pval(design, "rail_hole_count")), c))
        print("  %-34s cylindrical faces %d (2 walls per hole)" % ("", len(hole_faces(b, dia))))


def step6_stile_holes(design):
    T, e, dia = pval(design, "tube_size"), pval(design, "hole_edge_dist"), pval(design, "hole_dia")
    W = pval(design, "frame_width")
    # rear stile: bolts go from the frame bay through the stile into the back
    # wall frame; entry face = the stile's bay-side face, X = frame_width - tube_size
    b, m = hole_row(design, "stile_rear", lambda c: c.yZConstructionPlane,
                    "frame_width - tube_size",
                    (W - T, -T / 2, e), [(Y, "tube_size / 2"), (Z, "hole_edge_dist")],
                    "stile_hole_count", "frame_height - 2 * hole_edge_dist",
                    lambda c: c.zConstructionAxis, "REAR STILE TO BACK WALL", reverse=True)
    print("step 6: rear stile holes.", m)
    c = hole_centres(b, dia, "x")
    print("  %-34s %d holes (expect %d), centres Y,Z: %s" % (
        b.name, len(c), int(pval(design, "stile_hole_count")), c))
    zmid, half = pval(design, "mid_rail_z"), T / 2
    clash = [z for (_y, z) in c if abs(z - zmid) < half + 12]
    print("  mid rail zone check (no hole within tube/2 + 12 of mid_rail_z): %s" %
          ("OK" if not clash else "CLASH at %s" % clash))


# ---------------------------------------------------------------- skin

def step7_skin(design):
    comp = find_component(design, "skin")
    W, H, ov = pval(design, "frame_width"), pval(design, "frame_height"), pval(design, "skin_overhang_rear")
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = "OUTLINE - ACP SKIN"
    # front-bottom corner on the origin (datums B, C); runs back past the frame
    # by skin_overhang_rear (inside skin_width)
    a, b = sk.modelToSketchSpace(p3(0, 0, 0)), sk.modelToSketchSpace(p3(W + ov, 0, H))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(a, b)
    ensure_hv(sk, rect)
    pts = rect_points(rect)
    c0 = nearest_point(pts, a)
    cx = nearest_point(pts, sk.modelToSketchSpace(p3(W + ov, 0, 0)))
    cz = nearest_point(pts, sk.modelToSketchSpace(p3(0, 0, H)))
    ax, _ = sketch_axis(sk, X)
    az, _ = sketch_axis(sk, Z)
    add_dim(sk, c0, cx, ax, "skin_width", (0, -1.0) if ax == "x" else (-1.0, 0))
    add_dim(sk, c0, cz, az, "skin_height", (0, -1.0) if az == "x" else (-1.0, 0))
    sk.geometricConstraints.addCoincident(c0, sk.originPoint)
    msg = check_sketch(sk)
    prof = sk.profiles.item(0)
    ext_in = comp.features.extrudeFeatures.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # extrude away from the frame, toward +Y (outside)
    nx = sk.xDirection.crossProduct(sk.yDirection)
    direction = (adsk.fusion.ExtentDirections.PositiveExtentDirection if nx.y > 0
                 else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ext_in.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("skin_thk")), direction)
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "EXTRUDE - ACP SKIN"
    body = ext.bodies.item(0)
    body.name = "%s - SHEET" % PARTS["skin"][1]
    print("step 7: ACP skin.", msg)
    print("  %-34s %s" % (body.name, fmt_box(bbox_mm(body))))


# ---------------------------------------------------------------- materials

# frame_material text -> Fusion Material Library name (densities are the
# library's generic values: Steel 7850, Aluminum 2700 kg/m3).
TUBE_MATERIALS = {"Steel": "Steel", "Aluminum": "Aluminum"}
# ACP 3 mm with a PE core: two 0.3 mm aluminium skins (2700 kg/m3) + 2.4 mm
# PE core (950 kg/m3) = 1.62 + 2.28 = 3.9 kg/m2 -> 1300 kg/m3 effective.
# ASSUMPTION (CALCULATION from typical layer build); the chosen ACP's
# datasheet replaces it. A mineral (FR) core weighs about 6 kg/m2.
ACP_MATERIAL = "ACP 3 mm PE core (effective 1300 kg/m3, ASSUMPTION)"
ACP_DENSITY = 1300.0
MEMBERS = ("stile_rear", "stile_front", "rail_bottom", "rail_top", "rail_mid")


def step8_materials(design):
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName("Fusion Material Library")
    mat_text = design.userParameters.itemByName("frame_material").textValue
    if mat_text not in TUBE_MATERIALS:
        raise RuntimeError("frame_material must be one of %s" % list(TUBE_MATERIALS))
    tube_mat = lib.materials.itemByName(TUBE_MATERIALS[mat_text])
    for key in MEMBERS:
        for b in find_component(design, key).bRepBodies:
            b.material = tube_mat
    acp = design.materials.itemByName(ACP_MATERIAL)
    if acp is None:
        acp = design.materials.addByCopy(lib.materials.itemByName("Aluminum"), ACP_MATERIAL)
    acp.materialProperties.itemById("structural_Density").value = ACP_DENSITY
    alib = app.materialLibraries.itemByName("Fusion Appearance Library")
    yellow = design.appearances.itemByName("Paint - Enamel Glossy (Yellow)")
    if yellow is None:
        yellow = design.appearances.addByCopy(
            alib.appearances.itemByName("Paint - Enamel Glossy (Yellow)"),
            "Paint - Enamel Glossy (Yellow)")
    skin = find_component(design, "skin").bRepBodies.item(0)
    skin.material = acp
    skin.appearance = yellow
    print("step 8: materials. tubes = %s (frame_material '%s'); skin = %s, yellow paint look "
          "(stand-in for EV3038 Dark Yellow)" % (tube_mat.name, mat_text, ACP_MATERIAL))
    report_mass(design)


def comp_mass(comp):
    return comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy).mass


def report_mass(design):
    total_frame = 0.0
    for key in MEMBERS:
        comp = find_component(design, key)
        m = comp_mass(comp)
        total_frame += m
        b = comp.bRepBodies.item(0)
        print("  %-34s %6.3f kg  %s, %.1f cm3" % (PARTS[key][1], m, b.material.name, b.volume))
    skin = find_component(design, "skin")
    ms = comp_mass(skin)
    print("  %-34s %6.3f kg  (frame, CALCULATION from CAD)" % ("FRAME TOTAL", total_frame))
    print("  %-34s %6.3f kg  (%.3f m2 x %.1f kg/m2)" % (
        "ACP SKIN", ms, pval(design, "skin_width") * pval(design, "skin_height") / 1e6,
        ACP_DENSITY * pval(design, "skin_thk") / 1000.0))
    print("  %-34s %6.3f kg  (limit 20 kg per part, v2 PLAN target 1)" % (
        "PANEL ASSY", total_frame + ms))


# ---------------------------------------------------------------- checks

def step9_checks(design):
    """Timeline health, sketch constraint state, feature names, parameters."""
    tl = design.timeline
    bad, unnamed = [], []
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    for i in range(tl.count):
        it = tl.item(i)
        if it.healthState != healthy:
            bad.append("%s: %s" % (it.name, it.errorOrWarningMessage))
    sketches, open_sk = 0, []
    for comp in design.allComponents:
        for sk in comp.sketches:
            sketches += 1
            if not sk.isFullyConstrained:
                open_sk.append(sk.name)
        for coll in (comp.features.extrudeFeatures, comp.features.holeFeatures,
                     comp.features.rectangularPatternFeatures):
            for f in coll:
                if not any(f.name.startswith(p) for p in ("EXTRUDE - ", "HOLE - ", "PATTERN - ")):
                    unnamed.append(f.name)
    print("step 9: checks")
    print("  timeline items: %d, not healthy: %d %s" % (tl.count, len(bad), bad if bad else ""))
    print("  sketches: %d, fully constrained: %d %s" % (
        sketches, sketches - len(open_sk), ("NOT: %s" % open_sk) if open_sk else ""))
    print("  features with default names: %d %s" % (len(unnamed), unnamed if unnamed else ""))
    names = []
    for i in range(tl.count):
        it = tl.item(i)
        names.append(it.name)
    print("  timeline: " + " | ".join(names))
    n_params = design.userParameters.count
    no_unit = [p.name for p in design.userParameters if p.unit == "" and not p.name.endswith("_count")]
    print("  user parameters: %d (unitless only the hole counts: %s)" % (
        n_params, "yes" if not no_unit else "NO: %s" % no_unit))
    ok = not bad and not open_sk and not unnamed and not no_unit
    print("  RESULT: %s" % ("all checks pass" if ok else "CHECKS FAILED"))
    if not ok:
        raise RuntimeError("step 9 checks failed")


# ---------------------------------------------------------------- save, export

CLOUD_FOLDER = "FocusPod v2"   # in the hub's "Default Project"
F3D_REL = "v2/01-CAD-Native/proof/%s_CAD.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/proof/%s_STEP.step" % DOC_NAME


def cloud_folder(app):
    proj = None
    for p in app.data.dataProjects:
        if p.name == "Default Project":
            proj = p
    if proj is None:
        raise RuntimeError("no 'Default Project' in the active hub")
    folder = proj.rootFolder.dataFolders.itemByName(CLOUD_FOLDER)
    if folder is None:
        folder = proj.rootFolder.dataFolders.add(CLOUD_FOLDER)
    return folder


def step_save(app, doc):
    folder = cloud_folder(app)
    for df in folder.dataFiles:
        if df.name == DOC_NAME:
            raise RuntimeError("'%s' already exists in %s; delete or rename it first, so the "
                               "folder keeps one copy" % (DOC_NAME, CLOUD_FOLDER))
    ok = doc.saveAs(DOC_NAME, folder, "FocusPod v2 proof part, rev %s, PROPOSED. Built by "
                    "v2/01-CAD-Native/proof/wall_panel_frame.py" % REV, "")
    if not ok:
        raise RuntimeError("saveAs failed")
    print("save: '%s' saved to Default Project / %s" % (doc.name, CLOUD_FOLDER))


def root_box(design):
    return bbox_mm(design.rootComponent)


def step_export(app, design):
    root_dir = ARGS.get("repo_root")
    if not root_dir:
        raise RuntimeError("export needs repo_root (run through tools/fusion/run_script.py)")
    em = design.exportManager
    f3d = "%s/%s" % (root_dir, F3D_REL)
    step = "%s/%s" % (root_dir, STEP_REL)
    if not em.execute(em.createFusionArchiveExportOptions(f3d, design.rootComponent)):
        raise RuntimeError("f3d export failed")
    # Fusion's API writes STEP in cm even with the design in mm and the units
    # set again right before the export (checked 2026-10-31, Fusion 2706.1.17).
    # The file declares cm, so every CAD reads it at true size; keep it as is.
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    if not em.execute(em.createSTEPExportOptions(step, design.rootComponent)):
        raise RuntimeError("STEP export failed")
    with open(step, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read().replace(" ", "")
    declared = "cm" if "SI_UNIT(.CENTI.,.METRE.)" in text else (
        "mm" if "SI_UNIT(.MILLI.,.METRE.)" in text else "other")
    box = root_box(design)
    print("export: %s" % F3D_REL)
    print("export: %s  (STEP length unit: %s, declared in the file)" % (STEP_REL, declared))
    print("  model bounding box (assembly):  %s" % fmt_box(box))
    # re-read the STEP in a new document and compare
    src_doc = app.activeDocument
    imp = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
    d2 = adsk.fusion.Design.cast(imp.products.itemByProductType("DesignProductType"))
    box2 = root_box(d2)
    n_bodies = sum(c.bRepBodies.count for c in d2.allComponents)
    diff = max(abs(a - b) for a, b in zip(box, box2))
    print("  STEP re-read bounding box:      %s  (%d bodies)" % (fmt_box(box2), n_bodies))
    print("  largest difference: %.4f mm -> %s" % (diff, "MATCH" if diff < 0.01 else "MISMATCH"))
    imp.close(False)
    src_doc.activate()
    if diff >= 0.01:
        raise RuntimeError("STEP bounding box does not match the model")


# ---------------------------------------------------------------- main

def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("export_active") == "1":
        # re-export the open, unmodified proof document (no rebuild)
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None or design.rootComponent.partNumber != PARTS["assy"][0] or \
                app.activeDocument.isModified:
            raise RuntimeError("the active document is not the unmodified proof part")
        print("re-export from '%s' (version %s)" % (
            app.activeDocument.name,
            app.activeDocument.dataFile.versionNumber if app.activeDocument.dataFile else "unsaved"))
        step_export(app, design)
        return
    doc, design = step1_document(app)
    steps = [None, None, step2_stile_front, step3_stile_rear, step4_rails, step5_rail_holes,
             step6_stile_holes, step7_skin, step8_materials, step9_checks]
    last = min(STOP_AFTER, len(steps) - 1)
    for n in range(2, last + 1):
        steps[n](design)
    print("done through step %d" % last)
    if last == len(steps) - 1:
        # export before saving: a STEP export started while Fusion is still
        # uploading a fresh save fails (seen 2026-10-31, Fusion 2706.1.17)
        if ARGS.get("export") == "1":
            step_export(app, design)
        if ARGS.get("save") == "1":
            step_save(app, doc)
