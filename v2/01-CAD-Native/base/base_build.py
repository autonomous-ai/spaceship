"""Build 110000 BASE (Spaceship, FocusPod v2) as a native, parametric Fusion design.

Run it through the Fusion runner (tools/fusion/run_script.py):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/base/base_build.py \
        --arg stop_after=9 --arg keep=1

Scope of revision P01 (the sample, built first because the factory's wall
sample stands on it): the back-left corner of the base. The left side band
(also the factory's base band rig R1, sample hold H17), the back band, the
back-left corner bracket, the levelling glides under those two bands, and
floor panel F1 with its seal mat. The front band pieces, the right side, F2
and the threshold follow in the next revision.

Every size comes from parameters. The pod's own sizes are not copied here:
the script reads the skeleton P03 parameter list (PARAMS in
v2/01-CAD-Native/skeleton/pod_skeleton.py) at run time and adds it to this
design under the same names, so a skeleton change reaches the base on the
next build. BASE's own parameters follow, each with its status and source.

Coordinates are the pod system of v2/00-Control/conventions.md section 4:
origin on the room floor at the pod centre, +X to the right wall, +Y to the
back wall, +Z up; left and right as seen from outside facing the door. Each
part is its own component, built in place in pod coordinates.

Steps (--arg stop_after=N stops after step N):
  1 document, parameters, components     6 floor panel F1 and its seal mat
  2 left side band                       7 hardware: rivet nuts, pins, glides
  3 back band                            8 materials and masses
  4 band holes (joints, pins, glides)    9 checks: sketches, timeline, boxes,
  5 corner bracket BL                      holes, clashes (own parts and skeleton)
Optional after step 9: --arg export=1 (f3d, STEP), --arg save=1 (cloud).
"""

import ast
import math
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
STOP_AFTER = int(ARGS.get("stop_after", "9"))
REV = "P01"
DOC_NAME = "110000_%s_BASE_CAD" % REV
HERE = os.path.dirname(os.path.abspath(globals().get("__file__", ARGS.get("script_path", "."))))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SKELETON = os.path.join(REPO, "v2", "01-CAD-Native", "skeleton", "pod_skeleton.py")

CM = 0.1  # Fusion API lengths are in cm; multiply mm by CM

# ---------------------------------------------------------------- parameters
# BASE's own parameters: name, expression, unit, status, source.
# Statuses follow conventions.md section 9. HOLD marks a value that waits on
# a named item (joints register, WALL frame bays, a bought part's data sheet).
BASE_PARAMS = [
    # base band section (100 x 40 is the skeleton's band_h x band_t)
    ("band_wall", "2 mm", "mm", "assumption",
     "layout study inputs.py t_al_base 2.0 mm (aluminium 100x40 base band); alloy, temper and dark finish HOLD (ISS-034, sample hold H15)"),
    ("band_finish", "'Black anodised, matte, 20 um (class AA20, EN ISO 7599)'", "Text", "confirmed",
     "PM ruling 2026-10-31 (BASE group): every base band piece and the door's kick strip"),
    ("cap_t", "3 mm", "mm", "assumption",
     "head of the plastic end cap closing the side band's back end, so the cap face is flush with the back face Y = pod_d/2; cap product HOLD"),
    # the wall above (WALL owns it; these say where its bottom member sits)
    ("frame_d", "40 mm", "mm", "source", "wall frame member depth (D-34: 20 x 40 x 1.2); the outer panel is ACP 3 + bond 3 + frame 40 = outer_t (D-66)"),
    ("jb_x", "outer_t - frame_d / 2", "mm", "calculation",
     "J-BASE-01 bolt line: centre of the wall's bottom tube, 26 in from the pod's outer face (joints register 3.4: X -1224, Y +824)"),
    # J-BASE-01, wall to base band
    ("rn_hole", "9.53 mm", "mm", "source", "Sherex CAH3-610-4.2 M6 rivet nut: hole 9.53 +0.10/0 (hardware selection A5)"),
    ("rn_flange", "12.96 mm", "mm", "source", "CAH3-610-4.2 head diameter 12.96 (hardware selection A5)"),
    ("rn_inst", "10.16 mm", "mm", "source", "CAH3-610-4.2 installed length, at most 10.16 (joints register H-03, maker data)"),
    ("rn_head_t", "0.76 mm", "mm", "source", "CAH3-610-4.2 head height 0.76 +-0.08 (joints register H-03, maker data)"),
    ("sw_hole", "10.5 mm", "mm", "source", "stop washer bore (joints register H-08, PROPOSED)"),
    ("sw_d", "20 mm", "mm", "source", "stop washer outside diameter (joints register H-08, PROPOSED)"),
    ("sw_t", "1.5 mm", "mm", "source",
     "stop washer, under each bolt rivnut's head: washer 1.5 + head 0.76 = seam_gap 2.26, so the walls stand at panel_z0 (D-64)"),
    ("jb_n", "4", "", "confirmed", "D-75 and joints register R-J13: 4 bolts per wall panel on the band"),
    ("jb_e", "220 mm", "mm", "confirmed", "D-75 and joints register R-J13: end bolts 220 in from each panel end, evenly spaced"),
    ("sp_e", "100 mm", "mm", "confirmed", "D-75 and joints register R-J13: spigots 100 in from each panel end"),
    ("sp_dia", "8 mm", "mm", "source", "locating spigot, stainless, M6 thread (joints register H-05, PROPOSED sizes)"),
    ("sp_proud", "8 mm", "mm", "source", "spigot stands 8 proud of the band top (joints register H-05, PROPOSED)"),
    ("sp_ch", "1 mm", "mm", "assumption", "lead-in chamfer on the spigot top"),
    ("sp_stud", "8 mm", "mm", "assumption", "spigot's M6 stud into its rivnut, with threadlocker"),
    # levelling glides (bought, HOLD: no product named yet)
    ("gl_n_side", "2", "", "calculation", "glides per side band: span about 1.3 m, sag under 0.5 mm (see feature rationale)"),
    ("gl_n_back", "3", "", "calculation", "glides on the back band: 2 spans of 1060 (see feature rationale)"),
    ("gl_e_f", "45 mm", "mm", "assumption", "front glide of a side band, behind the band's outer front corner (Y = -dl_y1), so it stays under the band's front end"),
    ("gl_e_b", "150 mm", "mm", "assumption", "back glide of a side band from the back face"),
    ("gl_e_bb", "150 mm", "mm", "assumption", "end glides of the back band from its ends"),
    ("gl_key_hole", "10 mm", "mm", "assumption", "hole in the band top for the 5 mm hex key that turns the glide (levelled before the walls go on); stays inboard of the wall gasket line"),
    ("gl_dx", "3 mm", "mm", "assumption", "glide axis 3 mm inboard of the band's centre line, so its key hole clears the wall gasket strip (joints register 2.4)"),
    ("gl_nut_hole", "13 mm", "mm", "assumption", "hole in the band bottom for an M10 rivet nut that carries the glide; nut product HOLD"),
    ("gl_pad", "36 mm", "mm", "assumption", "glide pad diameter (envelope, HOLD); stays inside the band's 40 mm width"),
    ("gl_stem", "10 mm", "mm", "assumption", "glide stem M10 (envelope, HOLD)"),
    ("gl_nut_t", "2 mm", "mm", "assumption", "M10 rivet nut head under the band, between the band and the glide pad (HOLD)"),
    # back corner bracket (aluminium angle 60 x 60 x 5, inside the corner, pod side)
    ("br_leg", "60 mm", "mm", "assumption", "angle leg, standard extruded aluminium angle 60 x 60 x 5"),
    ("br_t", "5 mm", "mm", "assumption", "angle thickness"),
    ("br_len", "70 mm", "mm", "assumption", "bracket height, Z 25 to 95: above the floor top, below the walls"),
    ("br_z0", "25 mm", "mm", "assumption", "bracket bottom: 13 mm above the floor top (mat_t + fl_t)"),
    ("br_e", "35 mm", "mm", "assumption", "bolt holes from the bracket's heel: clears the other leg and the bolt head"),
    ("br_zh", "15 mm", "mm", "assumption", "bolt holes from the bracket's top and bottom ends"),
    ("br_hole", "6.6 mm", "mm", "source", "ISO 273 medium clearance hole for M6"),
    # thin floor
    ("fl_t", "9 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (BASE group): 9 mm plywood floor panels, as v1 (FLR-01 9 mm), so the floor top is 12 and the threshold 13 (US accessibility). Replaces the skeleton's floor_t 15 until its next update; then fl_t = floor_t"),
    ("mat_t", "3 mm", "mm", "confirmed",
     "PM ruling 2026-10-31: a firm closed-cell foam mat (cross-linked PE or EPDM), 3 mm, about 200 kg/m3, under the floor panels; product HOLD"),
    ("fl_gap", "4 mm", "mm", "assumption", "gap from the floor edge to the band's inner face, closed by the edge seal (hardware selection D, Pemko S88BL pick)"),
    ("fl_seam", "1 mm", "mm", "assumption", "gap at the F1 / F2 seam on X = 0"),
    ("lap_w", "13 mm", "mm", "confirmed",
     "half-lap at the F1 / F2 seam: F1's lower half runs 13 mm under F2's upper half, so the seam stays flush with no glue (a tongue in 9 mm ply leaves 2 mm groove walls). 13 keeps F1 at 1218.5 including its lap, inside the 1219 of the 48 in pallet (PM ruling 2026-10-31, packing plan)"),
]

ASSEMBLY = ("110000", "BASE", "Đế / sàn")
# key: (part number, name, Vietnamese name, class, parent key)
PARTS = {
    "band_l": ("110101", "BASE - BAND ASSY - SIDE - LH", "Viền chân nhôm - cạnh trái (cụm)", "HS", None),
    "band_l_tube": ("111101", "BASE - BAND TUBE - SIDE - LH", "Viền chân nhôm 100x40 - cạnh trái", "MP", "band_l"),
    "band_b": ("110103", "BASE - BAND ASSY - BACK", "Viền chân nhôm - cạnh sau (cụm)", "HS", None),
    "band_b_tube": ("111103", "BASE - BAND TUBE - BACK", "Viền chân nhôm 100x40 - cạnh sau", "MP", "band_b"),
    "bracket": ("111201", "BASE - CORNER BRACKET - BACK - COMMON", "Ke góc đế - góc sau", "MP", None),
    "pin": ("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8", "MP", None),
    "washer": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm", "MP", None),
    "floor_f1": ("111401", "BASE - FLOOR PANEL - F1", "Tấm sàn mỏng - F1", "MP", None),
    "mat_f1": ("111501", "BASE - SEAL MAT - F1", "Tấm lót kín sàn - F1", "MP", None),
    "glide": ("118001", "BASE - LEVELLING GLIDE - M10 (HOLD)", "Chân chỉnh cao", "PI", None),
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "Tán rút M6", "PI", None),
}
CLASS_NAME = {"HS": "hardware-fitted subassembly", "MP": "part we make", "PI": "bought item"}

XL, XR = "-pod_w / 2", "pod_w / 2"
YB, YW = "pod_d / 2", "pod_d / 2 - wall_depth"     # back face; side walls' front edge
XOL = "-pod_w / 2 + outer_t"                        # back panels span frame to frame (D-55)
# P04 panel ranges on the band (skeleton BL_X, BR_X; D-64, D-66): one seam_gap at each stop
B1_X0 = "(-pod_w / 2 + outer_t + seam_gap)"         # B1 from here, half_pw wide
B2_X0 = "(pod_w / 2 - outer_t - seam_gap - half_pw)"  # B2 from here, half_pw wide
# inner point of the mitre between the left side band and DL's outer facet band
# piece (both band_t wide): Y = -dl_y1 + band_t * (L - dy) / dl_x2 with
# L = facet length, dy = dl_y2 - dl_y1 (the bisector of the two outer lines)
Y_MITRE_IN = "(-dl_y1 + band_t * (sqrt(dl_x2 ^ 2 + (dl_y2 - dl_y1) ^ 2) - (dl_y2 - dl_y1)) / dl_x2)"

X = adsk.core.Vector3D.create(1, 0, 0)
Y = adsk.core.Vector3D.create(0, 1, 0)
Z = adsk.core.Vector3D.create(0, 0, 1)


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def mm(v_cm):
    return round(v_cm * 10.0, 3)


def p3(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(x_mm * CM, y_mm * CM, z_mm * CM)


def ev(design, expr):
    """Value of a length expression in mm (plain number for unitless)."""
    um = design.unitsManager
    if any(ch.isalpha() for ch in expr):
        try:
            return um.evaluateExpression(expr, "mm") * 10.0
        except RuntimeError:
            return um.evaluateExpression(expr, "")
    return float(expr)


def bbox_mm(entity):
    b = entity.boundingBox
    return tuple(mm(v) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                 b.maxPoint.x, b.maxPoint.y, b.maxPoint.z))


def fmt_box(b):
    return "X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f" % (b[0], b[3], b[1], b[4], b[2], b[5])


def skeleton_params():
    with open(SKELETON, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), SKELETON)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "PARAMS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("no PARAMS list in " + SKELETON)


# ---------------------------------------------------------------- sketch helpers

def sketch_axis(sk, direction):
    """Which sketch axis a model direction maps to: ('x'|'y', sign)."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(direction.x, direction.y, direction.z))
    dx, dy = e.x - o.x, e.y - o.y
    if abs(dx) > abs(dy):
        return "x", 1 if dx > 0 else -1
    return "y", 1 if dy > 0 else -1


def on_plane(sk, xyz):
    """Sketch-space point for a model point, dropped onto the sketch plane
    (a point off the plane keeps a free coordinate and the sketch is never
    fully constrained)."""
    q = sk.modelToSketchSpace(p3(*xyz))
    return adsk.core.Point3D.create(q.x, q.y, 0)


def orient(axis):
    return (adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation if axis == "x"
            else adsk.fusion.DimensionOrientations.VerticalDimensionOrientation)


def dim_coord(sk, pt, direction, expr, value):
    """Fix pt's model coordinate along `direction` (a model axis lying in the
    sketch plane) to the expression: a distance dimension from the sketch
    origin driven by abs(expr), or an alignment with the origin when it is 0."""
    ax, _sign = sketch_axis(sk, direction)
    if abs(value) < 1e-6:
        if ax == "x":
            sk.geometricConstraints.addVerticalPoints(pt, sk.originPoint)
        else:
            sk.geometricConstraints.addHorizontalPoints(pt, sk.originPoint)
        return
    g = pt.geometry
    tp = adsk.core.Point3D.create(g.x / 2 + 0.7, g.y / 2 + 0.7, 0)
    d = sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, orient(ax), tp)
    d.parameter.expression = "abs(%s)" % expr


def polygon(design, sk, pts, u, v):
    """Closed polygon through pts = [(expr_u, expr_v, (x, y, z) mm), ...] in
    order, fully constrained: an edge parallel to a sketch axis gets a
    horizontal or vertical constraint, and each group of corners that such
    edges tie together gets one dimension from the sketch origin along that
    axis (Fusion over-constrains if both ends of an axis-parallel line are
    dimensioned; the skeleton's poly() does the same)."""
    lines = sk.sketchCurves.sketchLines
    q = [on_plane(sk, xyz) for (_a, _b, xyz) in pts]
    n = len(q)
    verts, edges = [], []
    for i in range(n):
        start = verts[-1] if verts else q[0]
        end = q[i + 1] if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(start, end)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    au, _s = sketch_axis(sk, u)
    av, _s = sketch_axis(sk, v)
    on = {au: (0, u), av: (1, v)}
    gc = sk.geometricConstraints
    for sa in ("x", "y"):
        group = list(range(n))

        def root(i):
            while group[i] != i:
                i = group[i]
            return i
        for i, ln in enumerate(edges):
            ga, gb = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs((ga.x - gb.x) if sa == "x" else (ga.y - gb.y)) < 1e-7:
                (gc.addVertical if sa == "x" else gc.addHorizontal)(ln)
                group[root((i + 1) % n)] = root(i)
        k, direction = on[sa]
        for i in range(n):
            if root(i) != i:
                continue
            xyz = pts[i][2]
            val = xyz[0] * direction.x + xyz[1] * direction.y + xyz[2] * direction.z
            dim_coord(sk, verts[i], direction, pts[i][k], val)
    return verts


def circle_at(sk, xyz, dia_expr, dia_mm, u, v, eu, ev_):
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(on_plane(sk, xyz), dia_mm / 2 * CM)
    g = c.centerSketchPoint.geometry
    d = sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0))
    d.parameter.expression = dia_expr
    uu = xyz[0] * u.x + xyz[1] * u.y + xyz[2] * u.z
    vv = xyz[0] * v.x + xyz[1] * v.y + xyz[2] * v.z
    dim_coord(sk, c.centerSketchPoint, u, eu, uu)
    dim_coord(sk, c.centerSketchPoint, v, ev_, vv)
    return c


def check_sketch(sk):
    if not sk.isFullyConstrained:
        free = []
        for sp in sk.sketchPoints:
            if not sp.isFullyConstrained:
                g = sp.geometry
                free.append("(%.2f, %.2f)" % (g.x * 10, g.y * 10))
        dims = ["%s=%s" % (d.parameter.name, d.parameter.expression) for d in sk.sketchDimensions]
        raise RuntimeError("sketch not fully constrained: %s; free points (sketch mm) %s; dims %s" % (
            sk.name, free, dims))
    return sk.name


def offset_plane(comp, which, expr, value, name):
    """Construction plane parallel to an origin plane ('xy', 'yz' or 'xz') at
    the model coordinate `value` (mm) given by `expr`. Checks the side: an
    origin plane's normal may point along -axis, and then the offset is negated."""
    base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane,
            "xz": comp.xZConstructionPlane}[which]
    if abs(value) < 1e-6:
        return base
    axis = {"xy": 2, "yz": 0, "xz": 1}[which]
    for e in (expr, "-(%s)" % expr):
        pin = comp.constructionPlanes.createInput()
        pin.setByOffset(base, vi(e))
        pl = comp.constructionPlanes.add(pin)
        o = pl.geometry.origin
        got = (o.x, o.y, o.z)[axis] * 10.0
        if abs(got - value) < 0.01:
            pl.name = name
            return pl
        pl.deleteMe()
    raise RuntimeError("could not place plane %s at %.3f" % (name, value))


def extrude(comp, prof, dist_expr, name, op=None, start_expr=None, body=None):
    """Extrude a profile along its plane normal. A join is made as a new body
    and then combined into `body`: an extrude join that only touches the body
    along a face makes a second body instead of joining."""
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    join = op == adsk.fusion.FeatureOperations.JoinFeatureOperation
    ei = comp.features.extrudeFeatures.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation if join else op)
    if start_expr:
        ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi(start_expr))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(dist_expr)),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    if body is not None and not join:
        ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    if join:
        tools = adsk.core.ObjectCollection.create()
        tools.add(f.bodies.item(0))
        ci = comp.features.combineFeatures.createInput(body, tools)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        ci.isKeepToolBodies = False
        cf = comp.features.combineFeatures.add(ci)
        cf.name = name.replace("EXTRUDE", "COMBINE", 1)
    return f


def single_body(comp, name=None):
    """The one body of a part component (a join leaves stale handles)."""
    if comp.bRepBodies.count != 1:
        raise RuntimeError("%s: expected 1 body, found %d" % (comp.name, comp.bRepBodies.count))
    b = comp.bRepBodies.item(0)
    if name:
        b.name = name
    return b


def one_profile(sk):
    if sk.profiles.count != 1:
        raise RuntimeError("%s: expected 1 profile, found %d" % (sk.name, sk.profiles.count))
    return sk.profiles.item(0)


# ---------------------------------------------------------------- document

def find_comp(design, key):
    want = PARTS[key][0]
    for c in design.allComponents:
        if c.partNumber == want:
            return c
    raise RuntimeError("component not found: " + want)


def find_occ(design, key):
    want = PARTS[key][0]
    for occ in design.rootComponent.allOccurrences:
        if occ.component.partNumber == want:
            return occ
    raise RuntimeError("occurrence not found: " + want)


def describe(comp, pn, name, vn, cls):
    comp.name = "%s %s" % (pn, name)
    comp.partNumber = pn
    comp.description = "%s | %s | %s | rev %s | DRAFT" % (name, vn, CLASS_NAME.get(cls, cls), REV)


def close_unsaved_builds(app, keep=None):
    """Close earlier unsaved build documents of this assembly (found by the
    root part number); never a saved document or anyone else's."""
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        try:   # drawings and other documents have no design product
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
        except RuntimeError:
            dd = None
        if dd and not d.isSaved and dd.rootComponent.partNumber == ASSEMBLY[0] and d != keep:
            d.close(False)


def wipe(design):
    """Empty the open design (timeline and user parameters), so the same
    cloud file gets the new build as its next version and drawings linked to
    it stay linked."""
    tl = design.timeline
    if tl.count:
        tl.markerPosition = 0
        tl.deleteAllAfterMarker()
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    up = design.userParameters
    for i in range(up.count - 1, -1, -1):
        up.item(i).deleteMe()


def step1_document(app):
    if ARGS.get("in_place") == "1":
        # the runner's --doc opened our saved document; rebuild it in place
        doc = app.activeDocument
        close_unsaved_builds(app, keep=doc)
        if doc.name != DOC_NAME:
            raise RuntimeError("in_place: the active document is %r, not %r (run with --doc %s)" % (
                doc.name, DOC_NAME, DOC_NAME))
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        wipe(design)
        return build_tree(doc, design)
    if ARGS.get("close_previous", "1") == "1":
        close_unsaved_builds(app)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    return build_tree(doc, design)


def build_tree(doc, design):
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    up = design.userParameters
    n_skel = 0
    for name, expr, unit, status, src in skeleton_params():
        if up.add(name, vi(expr), unit, "SKELETON P03 %s: %s" % (status.upper(), src)) is None:
            raise RuntimeError("could not add skeleton parameter " + name)
        n_skel += 1
    for name, expr, unit, status, src in BASE_PARAMS:
        if up.add(name, vi(expr), unit, "BASE %s: %s" % (status.upper(), src)) is None:
            raise RuntimeError("could not add parameter " + name)
    root = design.rootComponent
    root.partNumber = ASSEMBLY[0]
    # the root component takes the document name; it can't be renamed by script
    root.description = "%s | %s | assembly | rev %s | DRAFT" % (ASSEMBLY[1], ASSEMBLY[2], REV)
    made = {}
    for key, (pn, name, vn, cls, parent) in PARTS.items():
        host = root if parent is None else made[parent]
        occ = host.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        describe(occ.component, pn, name, vn, cls)
        made[key] = occ.component
        # pin, glide and rivnut: this first copy only holds the component; step 7
        # places the real copies at their holes and then deletes it
    print("step 1: document, %d skeleton parameters (read from %s) + %d BASE parameters" % (
        n_skel, os.path.relpath(SKELETON, REPO), len(BASE_PARAMS)))
    for k in ("pod_w", "pod_d", "glide_h", "band_h", "band_t", "wall_z0", "wall_depth", "outer_t",
              "floor_t", "dl_x2", "dl_y1", "dl_y2"):
        print("  %-12s = %9.3f mm   [%s]" % (k, ev(design, k), up.itemByName(k).expression))
    print("  components: " + ", ".join(c.name for c in design.allComponents))
    return doc, design


# ---------------------------------------------------------------- band tubes

def band_tube(design, key, label, outline, bore, axis_note):
    """Hollow 100 x 40 band tube: plan outline extruded band_h up from the
    band bottom (Z glide_h), then the bore cut leaving band_wall all round.
    outline / bore: polygons as for polygon(); the bore runs past both ends."""
    comp = find_comp(design, key)
    plane = offset_plane(comp, "xy", "glide_h", ev(design, "glide_h"),
                         "PLANE - BAND BOTTOM Z = glide_h")
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - %s - OUTLINE" % label
    polygon(design, sk, outline, X, Y)
    check_sketch(sk)
    f = extrude(comp, one_profile(sk), "band_h", "EXTRUDE - %s - TUBE OUTSIDE" % label)
    body = f.bodies.item(0)
    body.name = "%s - TUBE" % PARTS[key][1]
    sk2 = comp.sketches.add(plane)
    sk2.name = "PLAN - %s - BORE" % label
    polygon(design, sk2, bore, X, Y)
    check_sketch(sk2)
    extrude(comp, one_profile(sk2), "band_h - 2 * band_wall", "CUT - %s - BORE, WALL band_wall" % label,
            op=adsk.fusion.FeatureOperations.CutFeatureOperation, start_expr="band_wall", body=body)
    print("  %-30s %s  (%s)" % (PARTS[key][1], fmt_box(bbox_mm(body)), axis_note))
    return body


def P(design, ex, ey, ez="0 mm"):
    """(expr_x, expr_y, (x, y, z) mm) for polygon()."""
    return (ex, ey, (ev(design, ex), ev(design, ey), ev(design, ez)))


def step2_band_side_lh(design):
    outline = [
        P(design, XL, "%s - cap_t" % YB),
        P(design, "%s + band_t" % XL, "%s - cap_t" % YB),
        P(design, "%s + band_t" % XL, Y_MITRE_IN),
        P(design, XL, "-dl_y1"),
    ]
    bore = [
        P(design, "%s + band_wall" % XL, "%s + 20 mm" % YB),
        P(design, "%s + band_t - band_wall" % XL, "%s + 20 mm" % YB),
        P(design, "%s + band_t - band_wall" % XL, "-dl_y1 - 20 mm"),
        P(design, "%s + band_wall" % XL, "-dl_y1 - 20 mm"),
    ]
    print("step 2: left side band (front end mitred to DL's outer facet, back end cut for the cap)")
    band_tube(design, "band_l_tube", "SIDE LH", outline, bore, "length along Y")


def step3_band_back(design):
    outline = [
        P(design, "%s + band_t" % XL, "%s - band_t" % YB),
        P(design, "%s - band_t" % XR, "%s - band_t" % YB),
        P(design, "%s - band_t" % XR, YB),
        P(design, "%s + band_t" % XL, YB),
    ]
    bore = [
        P(design, "%s + band_t - 20 mm" % XL, "%s - band_t + band_wall" % YB),
        P(design, "%s - band_t + 20 mm" % XR, "%s - band_t + band_wall" % YB),
        P(design, "%s - band_t + 20 mm" % XR, "%s - band_wall" % YB),
        P(design, "%s + band_t - 20 mm" % XL, "%s - band_wall" % YB),
    ]
    print("step 3: back band (butts the side bands' inner faces, as v1's frame)")
    band_tube(design, "band_b_tube", "BACK", outline, bore, "length along X")


# ---------------------------------------------------------------- holes

def hole(design, key, plane, label, xyz, dims, dia_expr, depth_expr, want_dir,
         pattern=None):
    """A simple hole (Hole feature) at a sketch point on `plane`, drilled along
    want_dir (model vector) to depth_expr, optionally patterned:
    pattern = (axis attribute name, count expr, extent expr)."""
    comp = find_comp(design, key)
    body = comp.bRepBodies.item(0)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE POSITION - %s" % label
    pt = sk.sketchPoints.add(on_plane(sk, xyz))
    for direction, expr in dims:
        val = xyz[0] * direction.x + xyz[1] * direction.y + xyz[2] * direction.z
        dim_coord(sk, pt, direction, expr, val)
    check_sketch(sk)
    holes = comp.features.holeFeatures
    hin = holes.createSimpleInput(vi(dia_expr))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi(depth_expr))
    n = plane.geometry.normal
    # a hole runs against the sketch plane's normal unless flipped
    if -(n.x * want_dir.x + n.y * want_dir.y + n.z * want_dir.z) < 0:
        hin.isDefaultDirection = False
    hin.participantBodies = [body]
    hf = holes.add(hin)
    hf.name = "HOLE - %s" % label
    if pattern:
        axis_name, count_expr, extent_expr = pattern
        coll = adsk.core.ObjectCollection.create()
        coll.add(hf)
        pats = comp.features.rectangularPatternFeatures
        pin = pats.createInput(coll, getattr(comp, axis_name), vi(count_expr), vi(extent_expr),
                               adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
        # direction two defaults to 3 copies 0 mm apart (found by the WALL
        # Engineer): set it to a single instance
        other = "xConstructionAxis" if axis_name != "xConstructionAxis" else "yConstructionAxis"
        pin.setDirectionTwo(getattr(comp, other), vi("1"), vi("1 mm"))
        pat = pats.add(pin)
        pat.name = "PATTERN - %s" % label
    return hf


def holes_of(body, dia_mm):
    """Hole centres from the cylindrical faces of one diameter: list of
    (axis origin mm, axis direction)."""
    out = []
    for f in body.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and \
                abs(g.radius * 20.0 - dia_mm) < 0.01:
            out.append(((mm(g.origin.x), mm(g.origin.y), mm(g.origin.z)),
                        (round(g.axis.x, 3), round(g.axis.y, 3), round(g.axis.z, 3))))
    return out


def centres(body, dia_mm, along):
    """Unique centres of the holes of one diameter whose axis runs along
    `along`, as the two coordinates across that axis."""
    k = {"x": 0, "y": 1, "z": 2}[along]
    idx = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[along]
    pts = set()
    for org, d in holes_of(body, dia_mm):
        if abs(abs(d[k]) - 1.0) < 1e-3:
            pts.add((round(org[idx[0]], 2), round(org[idx[1]], 2)))
    return sorted(pts)


def step4_band_holes(design):
    v = lambda e: ev(design, e)  # noqa: E731
    # -- left side band
    c = find_comp(design, "band_l_tube")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    inner = offset_plane(c, "yz", "%s + band_t" % XL, v("%s + band_t" % XL),
                         "PLANE - BAND INNER FACE X = -pod_w/2 + band_t")
    down, up, out_x = Z.copy(), Z.copy(), X.copy()
    down.scaleBy(-1)
    out_x.scaleBy(-1)
    xb = "%s + jb_x" % XL
    y1b = "%s + seam_gap + jb_e" % YW                       # L1 starts one seam_gap behind Y -645 (P04)
    hole(design, "band_l_tube", top, "J-BASE-01 RIVNUT - L1", (v(xb), v(y1b), v("wall_z0")),
         [(X, xb), (Y, y1b)], "rn_hole", "band_wall", down, ("yConstructionAxis", "jb_n", "side_l - 2 * jb_e"))
    y1s = "%s + seam_gap + sp_e" % YW
    hole(design, "band_l_tube", top, "SPIGOT RIVNUT - L1", (v(xb), v(y1s), v("wall_z0")),
         [(X, xb), (Y, y1s)], "rn_hole", "band_wall", down, ("yConstructionAxis", "2", "side_l - 2 * sp_e"))
    xg = "%s + band_t / 2 + gl_dx" % XL
    yg0, gext = "-dl_y1 + gl_e_f", "pod_d / 2 - gl_e_b + dl_y1 - gl_e_f"
    hole(design, "band_l_tube", top, "GLIDE KEY ACCESS - SIDE LH", (v(xg), v(yg0), v("wall_z0")),
         [(X, xg), (Y, yg0)], "gl_key_hole", "band_wall", down, ("yConstructionAxis", "gl_n_side", gext))
    hole(design, "band_l_tube", bot, "GLIDE NUT - SIDE LH", (v(xg), v(yg0), v("glide_h")),
         [(X, xg), (Y, yg0)], "gl_nut_hole", "band_wall", up, ("yConstructionAxis", "gl_n_side", gext))
    yb = "%s - band_t - br_e" % YB
    hole(design, "band_l_tube", inner, "BRACKET RIVNUT - BL - SIDE LH",
         (v("%s + band_t" % XL), v(yb), v("br_z0 + br_zh")),
         [(Y, yb), (Z, "br_z0 + br_zh")], "rn_hole", "band_wall", out_x,
         ("zConstructionAxis", "2", "br_len - 2 * br_zh"))
    # -- back band
    c = find_comp(design, "band_b_tube")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    inner = offset_plane(c, "xz", "%s - band_t" % YB, v("%s - band_t" % YB),
                         "PLANE - BAND INNER FACE Y = pod_d/2 - band_t")
    yb_line = "%s - jb_x" % YB
    for panel, x0 in (("B1", B1_X0), ("B2", B2_X0)):
        hole(design, "band_b_tube", top, "J-BASE-01 RIVNUT - %s" % panel, (v("%s + jb_e" % x0), v(yb_line), v("wall_z0")),
             [(X, "%s + jb_e" % x0), (Y, yb_line)], "rn_hole", "band_wall", down,
             ("xConstructionAxis", "jb_n", "half_pw - 2 * jb_e"))
        hole(design, "band_b_tube", top, "SPIGOT RIVNUT - %s" % panel, (v("%s + sp_e" % x0), v(yb_line), v("wall_z0")),
             [(X, "%s + sp_e" % x0), (Y, yb_line)], "rn_hole", "band_wall", down,
             ("xConstructionAxis", "2", "half_pw - 2 * sp_e"))
    xg0, yg = "%s + band_t + gl_e_bb" % XL, "%s - band_t / 2 - gl_dx" % YB
    hole(design, "band_b_tube", top, "GLIDE KEY ACCESS - BACK", (v(xg0), v(yg), v("wall_z0")),
         [(X, xg0), (Y, yg)], "gl_key_hole", "band_wall", down,
         ("xConstructionAxis", "gl_n_back", "pod_w - 2 * band_t - 2 * gl_e_bb"))
    hole(design, "band_b_tube", bot, "GLIDE NUT - BACK", (v(xg0), v(yg), v("glide_h")),
         [(X, xg0), (Y, yg)], "gl_nut_hole", "band_wall", up,
         ("xConstructionAxis", "gl_n_back", "pod_w - 2 * band_t - 2 * gl_e_bb"))
    into_back = Y.copy()
    for corner, xb_ in (("BL", "%s + band_t + br_e" % XL), ("BR", "%s - band_t - br_e" % XR)):
        hole(design, "band_b_tube", inner, "BRACKET RIVNUT - %s - BACK" % corner,
             (v(xb_), v("%s - band_t" % YB), v("br_z0 + br_zh")),
             [(X, xb_), (Z, "br_z0 + br_zh")], "rn_hole", "band_wall", into_back,
             ("zConstructionAxis", "2", "br_len - 2 * br_zh"))
    print("step 4: band holes")
    report_holes(design)


def report_holes(design):
    rn, gk, gn = ev(design, "rn_hole"), ev(design, "gl_key_hole"), ev(design, "gl_nut_hole")
    for key in ("band_l_tube", "band_b_tube"):
        body = find_comp(design, key).bRepBodies.item(0)
        top = [p for p in centres(body, rn, "z")]
        side = [p for p in centres(body, rn, "x")] if key == "band_l_tube" else centres(body, rn, "y")
        print("  %s" % PARTS[key][1])
        print("    rivnut holes in the top wall (X, Y): %d  %s" % (len(top), top))
        print("    rivnut holes in the inner wall:      %d  %s" % (len(side), side))
        print("    glide key holes (top): %s   glide nut holes (bottom): %s" % (
            centres(body, gk, "z"), centres(body, gn, "z")))


# ---------------------------------------------------------------- bracket

def step5_bracket(design):
    v = lambda e: ev(design, e)  # noqa: E731
    comp = find_comp(design, "bracket")
    plane = offset_plane(comp, "xy", "br_z0", v("br_z0"), "PLANE - BRACKET BOTTOM Z = br_z0")
    # heel: the bands' inside corner, standing off by the rivnut heads it bears on
    xh, yh = "%s + band_t + rn_head_t" % XL, "%s - band_t - rn_head_t" % YB
    pts = [
        P(design, xh, yh),
        P(design, "%s + br_leg" % xh, yh),
        P(design, "%s + br_leg" % xh, "%s - br_t" % yh),
        P(design, "%s + br_t" % xh, "%s - br_t" % yh),
        P(design, "%s + br_t" % xh, "%s - br_leg" % yh),
        P(design, xh, "%s - br_leg" % yh),
    ]
    sk = comp.sketches.add(plane)
    sk.name = "SECTION - CORNER BRACKET - ANGLE br_leg x br_leg x br_t"
    polygon(design, sk, pts, X, Y)
    check_sketch(sk)
    f = extrude(comp, one_profile(sk), "br_len", "EXTRUDE - CORNER BRACKET - ANGLE")
    body = f.bodies.item(0)
    body.name = "%s - ANGLE" % PARTS["bracket"][1]
    # leg on the side band: holes along X through br_t, from the pod side
    pl1 = offset_plane(comp, "yz", "%s + br_t" % xh, v("%s + br_t" % xh),
                       "PLANE - BRACKET LEG 1 POD-SIDE FACE")
    to_mx = X.copy()
    to_mx.scaleBy(-1)
    # hole positions use the same expressions as the bands' rivnut holes
    y1 = "%s - band_t - br_e" % YB
    hole(design, "bracket", pl1, "BRACKET - LEG 1 - M6 CLEARANCE",
         (v("%s + br_t" % xh), v(y1), v("br_z0 + br_zh")), [(Y, y1), (Z, "br_z0 + br_zh")],
         "br_hole", "br_t", to_mx, ("zConstructionAxis", "2", "br_len - 2 * br_zh"))
    pl2 = offset_plane(comp, "xz", "%s - br_t" % yh, v("%s - br_t" % yh),
                       "PLANE - BRACKET LEG 2 POD-SIDE FACE")
    x2 = "%s + band_t + br_e" % XL
    hole(design, "bracket", pl2, "BRACKET - LEG 2 - M6 CLEARANCE",
         (v(x2), v("%s - br_t" % yh), v("br_z0 + br_zh")), [(X, x2), (Z, "br_z0 + br_zh")],
         "br_hole", "br_t", Y, ("zConstructionAxis", "2", "br_len - 2 * br_zh"))
    print("step 5: corner bracket BL  %s" % fmt_box(bbox_mm(body)))
    d = ev(design, "br_hole")
    print("  holes leg 1 (Y, Z): %s   leg 2 (X, Z): %s" % (centres(body, d, "x"), centres(body, d, "y")))


# ---------------------------------------------------------------- floor

def step6_floor(design):
    v = lambda e: ev(design, e)  # noqa: E731
    x0, x1 = "%s + band_t + fl_gap" % XL, "-fl_seam / 2"
    xl = "-fl_seam / 2 + lap_w"                        # end of F1's lower lap, under F2
    y0, y1 = YW, "%s - band_t - fl_gap" % YB
    comp = find_comp(design, "floor_f1")
    plane = offset_plane(comp, "xy", "mat_t", v("mat_t"), "PLANE - FLOOR UNDERSIDE Z = mat_t")
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - FLOOR PANEL F1 (WITH THE SEAM LAP)"
    polygon(design, sk, [P(design, x0, y0), P(design, xl, y0), P(design, xl, y1), P(design, x0, y1)], X, Y)
    check_sketch(sk)
    f = extrude(comp, one_profile(sk), "fl_t", "EXTRUDE - FLOOR PANEL F1 - PLYWOOD fl_t")
    f.bodies.item(0).name = "%s - PANEL" % PARTS["floor_f1"][1]
    # the half-lap: cut the upper half along the seam edge; F2's upper half lies on it
    sk2 = comp.sketches.add(plane)
    sk2.name = "PLAN - F1 SEAM LAP ZONE"
    polygon(design, sk2, [P(design, x1, y0), P(design, xl, y0), P(design, xl, y1), P(design, x1, y1)], X, Y)
    check_sketch(sk2)
    body = single_body(comp)
    extrude(comp, one_profile(sk2), "fl_t / 2", "CUT - F1 SEAM HALF-LAP - UPPER HALF",
            op=adsk.fusion.FeatureOperations.CutFeatureOperation, start_expr="fl_t / 2", body=body)
    body = single_body(comp, "%s - PANEL" % PARTS["floor_f1"][1])
    print("step 6: floor panel F1  %s" % fmt_box(bbox_mm(body)))
    comp = find_comp(design, "mat_f1")
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "PLAN - SEAL MAT F1"
    polygon(design, sk, [P(design, x0, y0), P(design, x1, y0), P(design, x1, y1), P(design, x0, y1)], X, Y)
    check_sketch(sk)
    extrude(comp, one_profile(sk), "mat_t", "EXTRUDE - SEAL MAT F1")
    mat = single_body(comp, "%s - SHEET" % PARTS["mat_f1"][1])
    print("  seal mat F1           %s" % fmt_box(bbox_mm(mat)))


# ---------------------------------------------------------------- hardware

def revolve_section(design, comp, name, pts):
    """A round part as one revolve: the half section in the XZ plane (X =
    radius, Z = height, pts as for polygon() with u = X, v = Z) turned 360
    degrees about the Z axis."""
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = "HALF SECTION - %s" % name
    polygon(design, sk, pts, X, Z)
    check_sketch(sk)
    ri = comp.features.revolveFeatures.createInput(
        one_profile(sk), comp.zConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ri.setAngleExtent(False, vi("360 deg"))
    rf = comp.features.revolveFeatures.add(ri)
    rf.name = "REVOLVE - %s" % name
    return single_body(comp, name)


def PZ(design, er, ez):
    """(expr_r, expr_z, (r, 0, z) mm) for a half section in the XZ plane."""
    return (er, ez, (ev(design, er), 0.0, ev(design, ez)))


def build_rivnut(design):
    comp = find_comp(design, "rivnut")
    revolve_section(design, comp, "RIVET NUT M6 CAH3-610-4.2 - ENVELOPE", [
        PZ(design, "3 mm", "-(rn_inst - rn_head_t)"),           # thread bore, M6 (envelope)
        PZ(design, "rn_hole / 2 - 0.065 mm", "-(rn_inst - rn_head_t)"),
        PZ(design, "rn_hole / 2 - 0.065 mm", "0 mm"),
        PZ(design, "rn_flange / 2", "0 mm"),
        PZ(design, "rn_flange / 2", "rn_head_t"),
        PZ(design, "3 mm", "rn_head_t"),
    ])


def build_pin(design):
    """Locating spigot (joints register H-05): Ø8 stainless, sits on its rivnut's
    head and stands sp_proud above the band top; M6 stud into the rivnut."""
    comp = find_comp(design, "pin")
    h = "sp_proud - rn_head_t"
    revolve_section(design, comp, "LOCATING SPIGOT D8", [
        PZ(design, "0 mm", "-sp_stud"),
        PZ(design, "3 mm", "-sp_stud"),                         # M6 stud
        PZ(design, "3 mm", "0 mm"),
        PZ(design, "sp_dia / 2", "0 mm"),
        PZ(design, "sp_dia / 2", "%s - sp_ch" % h),              # lead-in chamfer
        PZ(design, "sp_dia / 2 - sp_ch", h),
        PZ(design, "0 mm", h),
    ])


def build_washer(design):
    """Stop washer (joints register H-08): under each bolt rivnut's head."""
    comp = find_comp(design, "washer")
    revolve_section(design, comp, "STOP WASHER 10.5 X 20 X 1.5", [
        PZ(design, "sw_hole / 2", "0 mm"),
        PZ(design, "sw_d / 2", "0 mm"),
        PZ(design, "sw_d / 2", "sw_t"),
        PZ(design, "sw_hole / 2", "sw_t"),
    ])


def build_glide(design):
    comp = find_comp(design, "glide")
    revolve_section(design, comp, "LEVELLING GLIDE - ENVELOPE (HOLD)", [
        PZ(design, "0 mm", "0 mm"),
        PZ(design, "gl_pad / 2", "0 mm"),
        PZ(design, "gl_pad / 2", "glide_h - gl_nut_t"),
        PZ(design, "gl_stem / 2", "glide_h - gl_nut_t"),
        PZ(design, "gl_stem / 2", "glide_h + band_h / 2"),
        PZ(design, "0 mm", "glide_h + band_h / 2"),
    ])


def place(design, host_key, key, xyz, rot=None):
    """A copy of a hardware component inside a host assembly (or the root when
    host_key is None) at a point; rot = 'x+' turns its +Z to +X, 'y-' to -Y.
    Positions come from the same expressions as the holes and are set when
    the script runs (see the manifest)."""
    m = adsk.core.Matrix3D.create()
    if rot == "x+":
        m.setToRotation(math.pi / 2, Y, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "y-":
        m.setToRotation(math.pi / 2, X, adsk.core.Point3D.create(0, 0, 0))
    m.translation = adsk.core.Vector3D.create(xyz[0] * CM, xyz[1] * CM, xyz[2] * CM)
    host = design.rootComponent if host_key is None else find_comp(design, host_key)
    occ = host.occurrences.addExistingComponent(find_comp(design, key), m)
    occ.isLightBulbOn = True
    return occ


def hardware_points(design):
    """(host assembly, item, (x, y, z) mm, rotation) for every hardware copy,
    from the same parameters as the holes. Bolt rivnuts sit on a stop washer;
    spigot rivnuts sit on the band and carry the spigot (joints register 2.1)."""
    v = lambda e: ev(design, e)  # noqa: E731
    out = []
    z_top, sw, head = v("wall_z0"), v("sw_t"), v("rn_head_t")
    n = int(round(v("jb_n")))
    jb_e, sp_e = v("jb_e"), v("sp_e")

    def edge(host, along, start, length, fixed):
        """J-BASE-01 on one panel edge: 4 bolts at the 220 mm rule, 2 spigots."""
        def pt(t, z):
            return (fixed, start + t, z) if along == "y" else (start + t, fixed, z)
        for i in range(n):
            t = jb_e + i * (length - 2 * jb_e) / (n - 1)
            out.append((host, "washer", pt(t, z_top), None))
            out.append((host, "rivnut", pt(t, z_top + sw), None))
        for t in (sp_e, length - sp_e):
            out.append((host, "rivnut", pt(t, z_top), None))
            out.append((host, "pin", pt(t, z_top + head), None))
    edge("band_l", "y", v("%s + seam_gap" % YW), v("side_l"), v("%s + jb_x" % XL))            # L1
    for x0 in (B1_X0, B2_X0):                                                                 # B1, B2
        edge("band_b", "x", v(x0), v("half_pw"), v("%s - jb_x" % YB))
    # corner bracket rivnuts in the bands' inner walls (BL on both bands, BR on the back band)
    zb, dz = v("br_z0 + br_zh"), v("br_len - 2 * br_zh")
    for k in range(2):
        out.append(("band_l", "rivnut", (v("%s + band_t" % XL), v("%s - band_t - br_e" % YB), zb + k * dz), "x+"))
        for xb_ in (v("%s + band_t + br_e" % XL), v("%s - band_t - br_e" % XR)):
            out.append(("band_b", "rivnut", (xb_, v("%s - band_t" % YB), zb + k * dz), "y-"))
    # glides, screwed into the bands at the factory
    xg = v("%s + band_t / 2 + gl_dx" % XL)
    ng = int(round(v("gl_n_side")))
    yg0, gext = v("-dl_y1 + gl_e_f"), v("pod_d / 2 - gl_e_b + dl_y1 - gl_e_f")
    for i in range(ng):
        out.append(("band_l", "glide", (xg, yg0 + i * gext / (ng - 1), 0.0), None))
    nb = int(round(v("gl_n_back")))
    x0, ext = v("%s + band_t + gl_e_bb" % XL), v("pod_w - 2 * band_t - 2 * gl_e_bb")
    for i in range(nb):
        out.append(("band_b", "glide", (x0 + i * ext / (nb - 1), v("%s - band_t / 2 - gl_dx" % YB), 0.0), None))
    return out


def step7_hardware(design):
    build_rivnut(design)
    build_pin(design)
    build_washer(design)
    build_glide(design)
    counts = {}
    for host, key, xyz, rot in hardware_points(design):
        place(design, host, key, xyz, rot)
        counts[(host, key)] = counts.get((host, key), 0) + 1
    # remove the holding copies from step 1, so the CAD count equals the BOM count
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        occ = root.occurrences.item(i)
        if occ.component.partNumber in (PARTS["pin"][0], PARTS["glide"][0], PARTS["rivnut"][0],
                                        PARTS["washer"][0]):
            occ.deleteMe()
    print("step 7: hardware placed")
    for (host, key), n in sorted(counts.items()):
        print("  %-30s %-44s x %d" % (PARTS[host][1], PARTS[key][1], n))


# ---------------------------------------------------------------- materials

MATERIALS = {
    # key: (library material, design material name or None, density kg/m3 or None)
    "band_l_tube": ("Aluminum", None, None),
    "band_b_tube": ("Aluminum", None, None),
    "bracket": ("Aluminum", None, None),
    "pin": ("Steel", None, None),
    "washer": ("Aluminum", None, None),
    "rivnut": ("Aluminum", None, None),
    "floor_f1": ("Aluminum", "Plywood 600 kg/m3 (ASSUMPTION)", 600.0),
    "mat_f1": ("Aluminum", "Closed-cell foam 200 kg/m3 (ASSUMPTION)", 200.0),
    "glide": ("Aluminum", "Glide envelope 0.15 kg (ASSUMPTION)", None),
}


def step8_materials(design):
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName("Fusion Material Library")
    for key, (libname, dname, rho) in MATERIALS.items():
        base = lib.materials.itemByName(libname)
        mat = base
        if dname:
            mat = design.materials.itemByName(dname)
            if mat is None:
                mat = design.materials.addByCopy(base, dname)
            if rho is None:
                comp = find_comp(design, key)
                vol_cm3 = sum(b.volume for b in comp.bRepBodies)
                rho = 0.15 / (vol_cm3 * 1e-6)
            mat.materialProperties.itemById("structural_Density").value = rho
        for b in find_comp(design, key).bRepBodies:
            b.material = mat
    alib = app.materialLibraries.itemByName("Fusion Appearance Library")
    dark = None
    for nm in ("Aluminum - Anodized Rough (Black)", "Aluminum - Anodized Matte (Black)",
               "Aluminum - Anodized Glossy (Black)", "Paint - Enamel Glossy (Black)", "Plastic - Matte (Black)"):
        try:   # an unknown name raises instead of returning None
            a = alib.appearances.itemByName(nm)
        except RuntimeError:
            a = None
        if a is not None:
            dark = design.appearances.itemByName(nm) or design.appearances.addByCopy(a, nm)
            break
    if dark is not None:
        for key in ("band_l_tube", "band_b_tube"):
            for b in find_comp(design, key).bRepBodies:
                b.appearance = dark
    print("step 8: materials (band look: %s)" % (dark.name if dark else "library default"))
    report_mass(design)


def comp_mass(comp):
    return comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy).mass


def report_mass(design):
    for key in PARTS:
        comp = find_comp(design, key)
        if comp.bRepBodies.count == 0:
            continue
        m = comp_mass(comp)
        flag = "" if m <= 20.0 else "  OVER 20 kg"
        print("  %-44s %7.3f kg  %s%s" % (comp.name, m, comp.bRepBodies.item(0).material.name, flag))


# ---------------------------------------------------------------- checks

def body_boxes(design):
    """(label, proxy body, occurrence) for every visible body in the assembly."""
    out = []
    for occ in design.rootComponent.allOccurrences:
        if not occ.isLightBulbOn:
            continue
        for b in occ.bRepBodies:
            out.append(("%s @%s" % (occ.component.partNumber, occ.name.split(":")[-1]), b, occ))
    return out


def temp_copy(tbm, body, occ):
    """Temporary copy of a body where it sits in the assembly. A proxy's copy
    can come back in its component's own space; then the occurrence's
    transform is applied (checked against the proxy's bounding box)."""
    t = tbm.copy(body)
    if occ is not None:
        a, b = t.boundingBox, body.boundingBox
        if max(abs(a.minPoint.x - b.minPoint.x), abs(a.minPoint.y - b.minPoint.y),
               abs(a.minPoint.z - b.minPoint.z)) > 1e-4:
            tbm.transform(t, occ.transform2)
    return t


def intersect_volume(tbm, a, b, occ_a=None, occ_b=None):
    ba, bb = a.boundingBox, b.boundingBox
    if not ba.intersects(bb):
        return 0.0
    ta, tb = temp_copy(tbm, a, occ_a), temp_copy(tbm, b, occ_b)
    tbm.booleanOperation(ta, tb, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return ta.volume * 1000.0  # cm3 -> mm3


def skeleton_boxes(design):
    """Skeleton P04 envelopes next to the base, from the same parameters
    (pod_skeleton.py: side panels from YW + seam_gap, back panels BL_X / BR_X,
    all standing at panel_z0)."""
    v = lambda e: ev(design, e)  # noqa: E731
    xl, yb, yw, z0 = v(XL), v(YB), v(YW), v("panel_z0")
    ot, st, ct = v("outer_t"), v("stack_t"), v("cass_t")
    sh, bh, hp = v("side_h"), v("back_ph"), v("half_pw")
    b1, b2 = v(B1_X0), v(B2_X0)
    return [
        ("skeleton L1", (xl, yw + v("seam_gap"), z0, xl + ot, yb, z0 + sh)),
        ("skeleton L1-CASS", (xl + st - ct, yw, z0, xl + st, yb - st + ct, z0 + sh)),
        ("skeleton B1", (b1, yb - ot, z0, b1 + hp, yb, z0 + bh)),
        ("skeleton B2", (b2, yb - ot, z0, b2 + hp, yb, z0 + bh)),
        ("skeleton B1-CASS", (xl + st, yb - st, z0, 0.0, yb - st + ct, z0 + bh)),
    ]


# overlaps made on purpose: (part number prefix, skeleton label, reason)
EXPECTED_WITH_SKELETON = [
    ("838003", "skeleton L1", "rivnut heads sit in clearance holes in the wall's bottom member (WALL)"),
    ("838003", "skeleton B1", "same, back wall"),
    ("838003", "skeleton B2", "same, back wall"),
    ("831001", "skeleton L1", "locating spigots enter the wall's bottom tube (WALL: Ø8.5 hole and 8.5 x 14 slot)"),
    ("831001", "skeleton B1", "same, back wall"),
    ("831001", "skeleton B2", "same, back wall"),
]
EXPECTED_OWN = [
    ("838003", "831001", "spigot stud in the rivnut thread (both modelled as envelopes)"),
]


def step9_checks(design):
    tl = design.timeline
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    bad = ["%s: %s" % (tl.item(i).name, tl.item(i).errorOrWarningMessage)
           for i in range(tl.count) if tl.item(i).healthState != healthy]
    n_sk, open_sk = 0, []
    for comp in design.allComponents:
        for sk in comp.sketches:
            n_sk += 1
            if not sk.isFullyConstrained:
                open_sk.append("%s / %s" % (comp.partNumber, sk.name))
    print("step 9: checks")
    print("  timeline items %d, not healthy %d %s" % (tl.count, len(bad), bad or ""))
    print("  sketches %d, fully constrained %d %s" % (n_sk, n_sk - len(open_sk), open_sk or ""))
    v = lambda e: ev(design, e)  # noqa: E731
    expect = {
        "band_l_tube": (v(XL), v(Y_MITRE_IN) if v(Y_MITRE_IN) < v("-dl_y1") else v("-dl_y1"), v("glide_h"),
                        v("%s + band_t" % XL), v("%s - cap_t" % YB), v("wall_z0")),
        "band_b_tube": (v("%s + band_t" % XL), v("%s - band_t" % YB), v("glide_h"),
                        v("%s - band_t" % XR), v(YB), v("wall_z0")),
        "floor_f1": (v("%s + band_t + fl_gap" % XL), v(YW), v("mat_t"),
                     v("-fl_seam / 2 + lap_w"), v("%s - band_t - fl_gap" % YB), v("mat_t + fl_t")),
    }
    box_bad = []
    for key, want in expect.items():
        got = bbox_mm(find_comp(design, key).bRepBodies.item(0))
        diff = max(abs(a - b) for a, b in zip(got, want))
        print("  box %-34s %s  %s" % (PARTS[key][1], fmt_box(got), "OK" if diff < 0.05 else "OFF by %.3f" % diff))
        if diff >= 0.05:
            box_bad.append(key)
    # clashes between the base's own parts
    tbm = adsk.fusion.TemporaryBRepManager.get()
    bodies = body_boxes(design)
    own = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            vol = intersect_volume(tbm, bodies[i][1], bodies[j][1], bodies[i][2], bodies[j][2])
            if vol > 1.0:
                a, b = bodies[i][0].split()[0], bodies[j][0].split()[0]
                ok = any({a, b} == {e[0], e[1]} for e in EXPECTED_OWN)
                own.append((bodies[i][0], bodies[j][0], vol, ok))
    unexpected = [c for c in own if not c[3]]
    print("  own clashes over 1 mm3: %d, expected %d, unexpected %d %s" % (
        len(own), len(own) - len(unexpected), len(unexpected),
        ["%s x %s %.1f mm3" % c[:3] for c in unexpected] or ""))
    # clashes with the skeleton's walls and linings
    sk_hits, sk_bad = {}, []
    for label, bx in skeleton_boxes(design):
        ob = adsk.core.OrientedBoundingBox3D.create(
            p3((bx[0] + bx[3]) / 2, (bx[1] + bx[4]) / 2, (bx[2] + bx[5]) / 2),
            X, Y, (bx[3] - bx[0]) * CM, (bx[4] - bx[1]) * CM, (bx[5] - bx[2]) * CM)
        box = tbm.createBox(ob)
        for name, b, occ in bodies:
            vol = intersect_volume(tbm, b, box, occ, None)
            if vol > 1.0:
                pn = name.split()[0]
                ok = any(pn == e[0] and label == e[1] for e in EXPECTED_WITH_SKELETON)
                sk_hits[(pn, label)] = sk_hits.get((pn, label), 0) + 1
                if not ok:
                    sk_bad.append("%s x %s %.1f mm3" % (name, label, vol))
    print("  clashes with skeleton walls and linings: %s; unexpected %d %s" % (
        ", ".join("%s x %s: %d" % (k[0], k[1], n) for k, n in sorted(sk_hits.items())) or "none",
        len(sk_bad), sk_bad or ""))
    # the walls stand on the stops: band top + stop washer + rivnut head = skeleton panel_z0
    top = bbox_mm(find_comp(design, "band_l_tube").bRepBodies.item(0))[5]
    stop = top + v("sw_t") + v("rn_head_t")
    print("  band top Z %.2f = wall_z0 %.2f; stop top Z %.2f vs skeleton panel_z0 %.2f -> %s" % (
        top, v("wall_z0"), stop, v("panel_z0"), "OK" if abs(stop - v("panel_z0")) < 0.01 else "OFF"))
    if abs(stop - v("panel_z0")) >= 0.01:
        box_bad.append("stop height")
    ok = not bad and not open_sk and not box_bad and not unexpected and not sk_bad
    print("  RESULT: %s" % ("all checks pass" if ok else "CHECKS FAILED"))
    if not ok:
        raise RuntimeError("step 9 checks failed")


# ---------------------------------------------------------------- save, export

CLOUD = ("Default Project", "FocusPod v2")
F3D_REL = "v2/01-CAD-Native/base/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/base/110000_%s_BASE_STEP.step" % REV


def cloud_folder(app):
    for p in app.data.dataProjects:
        if p.name == CLOUD[0]:
            folder = p.rootFolder.dataFolders.itemByName(CLOUD[1])
            if folder is None:
                raise RuntimeError("no folder %s in %s" % (CLOUD[1], CLOUD[0]))
            return p, folder
    raise RuntimeError("no project " + CLOUD[0])


def step_save(app, doc):
    proj, folder = cloud_folder(app)
    for df in folder.dataFiles:
        if df.name == DOC_NAME:
            if ARGS.get("replace") != "1":
                raise RuntimeError("'%s' is already in %s/%s; pass --arg replace=1 to replace it" % (DOC_NAME, *CLOUD))
            for i in range(app.documents.count - 1, -1, -1):   # our own copy, if it is open
                d = app.documents.item(i)
                if d.name == DOC_NAME and d.isSaved:
                    d.close(False)
            df.deleteMe()
            print("save: deleted the previous cloud file %s (our own; no drawing links it yet)" % DOC_NAME)
    app.data.activeProject = proj
    if not doc.saveAs(DOC_NAME, folder, "Spaceship BASE rev %s, DRAFT, built by "
                      "v2/01-CAD-Native/base/base_build.py" % REV, ""):
        raise RuntimeError("saveAs failed")
    print("save: %s saved to %s / %s" % (DOC_NAME, *CLOUD))


def step_export(app, design):
    em = design.exportManager
    f3d, step = os.path.join(REPO, F3D_REL), os.path.join(REPO, STEP_REL)
    for path in (f3d, step):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    if not em.execute(em.createFusionArchiveExportOptions(f3d, design.rootComponent)):
        raise RuntimeError("f3d export failed")
    ok = False
    for _ in range(10):
        if em.execute(em.createSTEPExportOptions(step, design.rootComponent)) and os.path.exists(step) \
                and os.path.getsize(step) > 2000:
            ok = True
            break
        adsk.doEvents()
        import time
        time.sleep(3)
    if not ok:
        raise RuntimeError("STEP export failed")
    with open(step, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read().replace(" ", "")
    unit = "cm" if "SI_UNIT(.CENTI.,.METRE.)" in text else ("mm" if "SI_UNIT(.MILLI.,.METRE.)" in text else "?")
    print("export: %s" % F3D_REL)
    print("export: %s (STEP length unit %s, declared in the file; D-13)" % (STEP_REL, unit))
    if "PRODUCT('%s'," % ASSEMBLY[0] not in text:
        raise RuntimeError("STEP: no root product with part number %s" % ASSEMBLY[0])
    if "/*author*/('')" not in text or "/*organization*/('')" not in text:
        raise RuntimeError("STEP header carries an author or organisation; it must stay empty (public repo)")
    box = bbox_mm(design.rootComponent)
    print("  assembly box   %s" % fmt_box(box))
    # read the STEP back in Fusion (it applies the declared unit and the assembly transforms)
    src = app.activeDocument
    imp = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
    d2 = adsk.fusion.Design.cast(imp.products.itemByProductType("DesignProductType"))
    box2 = bbox_mm(d2.rootComponent)
    n_occ = d2.rootComponent.allOccurrences.count
    imp.close(False)
    src.activate()
    diff = max(abs(a - b) for a, b in zip(box, box2))
    print("  STEP re-read   %s  (%d occurrences); largest difference %.3f mm -> %s" % (
        fmt_box(box2), n_occ, diff, "MATCH" if diff < 0.05 else "MISMATCH"))
    if diff >= 0.05:
        raise RuntimeError("STEP box does not match the model")


DATA_REL = "v2/03-Manufacturing/base/110000_%s_BASE_DATA.json" % REV


def export_data(design):
    """Facts read from the CAD for the parts list, cut list and DXF (made
    offline by v2/03-Manufacturing/base/make_outputs.py): parameters, parts
    with mass and box, copies per parent, hole centres, tube cuts, F1 outline."""
    import json
    v = lambda e: ev(design, e)  # noqa: E731
    up = design.userParameters
    params = []
    for p in up:
        text = p.valueType == adsk.fusion.ParameterValueTypes.TextParameterValueType if hasattr(
            adsk.fusion, "ParameterValueTypes") else False
        val = p.textValue if text else (round(p.value * 10.0, 4) if p.unit == "mm" else round(p.value, 4))
        params.append({"name": p.name, "expression": p.expression, "unit": p.unit, "value": val,
                       "comment": p.comment})
    parts = {}
    for key, (pn, name, vn, cls, parent) in PARTS.items():
        comp = find_comp(design, key)
        rec = {"key": key, "pn": pn, "name": name, "name_vi": vn, "class": cls,
               "parent": PARTS[parent][0] if parent else ASSEMBLY[0]}
        if comp.bRepBodies.count:
            b = comp.bRepBodies.item(0)
            rec.update({"mass_kg": round(comp_mass(comp), 4), "box_mm": bbox_mm(b),
                        "volume_mm3": round(b.volume * 1000.0, 1), "material": b.material.name})
        parts[pn] = rec
    copies = {}
    for occ in design.rootComponent.allOccurrences:
        parent = occ.assemblyContext.component.partNumber if occ.assemblyContext else ASSEMBLY[0]
        k = "%s>%s" % (parent, occ.component.partNumber)
        copies[k] = copies.get(k, 0) + 1
    holes = {}
    for key in ("band_l_tube", "band_b_tube", "bracket"):
        body = find_comp(design, key).bRepBodies.item(0)
        rows = set()
        for org, d in holes_of_all(body):
            rows.add((d[0], d[1], d[2], org[0], org[1], org[2], org[3]))
        holes[PARTS[key][0]] = [{"dia": r[6], "axis": [r[0], r[1], r[2]], "at": [r[3], r[4], r[5]]}
                                for r in sorted(rows, key=lambda r: tuple(-1e9 if x is None else x for x in r))]
    yi, yo = v(Y_MITRE_IN), v("-dl_y1")
    tubes = {
        PARTS["band_l_tube"][0]: {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "Y",
            "outer_face_length": round(v("%s - cap_t" % YB) - yo, 2),
            "inner_face_length": round(v("%s - cap_t" % YB) - yi, 2),
            "front_end": "mitre to DL's outer facet band piece: %.2f deg from square, long point on the outer face"
                         % math.degrees(math.atan2(yi - yo, v("band_t"))),
            "back_end": "square, for the end cap"},
        PARTS["band_b_tube"][0]: {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "X",
            "outer_face_length": round(v("pod_w - 2 * band_t"), 2), "inner_face_length": round(v("pod_w - 2 * band_t"), 2),
            "front_end": "square", "back_end": "square"},
        PARTS["bracket"][0]: {
            "section": "angle %.0f x %.0f x %.0f" % (v("br_leg"), v("br_leg"), v("br_t")), "axis": "Z",
            "outer_face_length": round(v("br_len"), 2), "inner_face_length": round(v("br_len"), 2),
            "front_end": "square", "back_end": "square"},
    }
    floor = {"x0": v("%s + band_t + fl_gap" % XL), "x_seam": v("-fl_seam / 2"), "x_lap": v("-fl_seam / 2 + lap_w"),
             "y0": v(YW), "y1": v("%s - band_t - fl_gap" % YB), "t": v("fl_t"), "lap_depth": v("fl_t / 2")}
    out = {"doc": DOC_NAME, "rev": REV, "params": params, "parts": parts, "copies": copies, "holes": holes,
           "tubes": tubes, "floor_f1": floor, "band_finish": up.itemByName("band_finish").textValue}
    path = os.path.join(REPO, DATA_REL)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print("export: %s (%d parameters, %d parts, %d copy rows)" % (DATA_REL, len(params), len(parts), len(copies)))


def holes_of_all(body):
    """Every hole axis in a body: (centre mm, axis), diameter rounded to 0.01."""
    out = []
    for f in body.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
            d = round(g.radius * 20.0, 2)
            a = (round(abs(g.axis.x), 3), round(abs(g.axis.y), 3), round(abs(g.axis.z), 3))
            o = [round(c * 10.0, 2) for c in (g.origin.x, g.origin.y, g.origin.z)]
            # keep the two coordinates across the axis; drop the one along it
            for k in range(3):
                if a[k] > 0.99:
                    o[k] = None
            out.append(((o[0], o[1], o[2], d), a))
    return out


# ---------------------------------------------------------------- main

def run(_context):
    app = adsk.core.Application.get()
    doc, design = step1_document(app)
    steps = [None, None, step2_band_side_lh, step3_band_back, step4_band_holes, step5_bracket,
             step6_floor, step7_hardware, step8_materials, step9_checks]
    last = min(STOP_AFTER, len(steps) - 1)
    for n in range(2, last + 1):
        steps[n](design)
    print("done through step %d" % last)
    if last == len(steps) - 1:
        if ARGS.get("in_place") == "1":
            # save first, so the exports come from a saved version (PR #6 review)
            if not doc.save("rev %s build by v2/01-CAD-Native/base/base_build.py" % REV):
                raise RuntimeError("save failed")
            print("saved: %s, version %s" % (doc.name, doc.dataFile.versionNumber if doc.dataFile else "?"))
        elif ARGS.get("save") == "1":
            step_save(app, doc)
        if ARGS.get("export") == "1":
            step_export(app, design)
            export_data(design)
    if ARGS.get("in_place") != "1" and ARGS.get("keep") != "1" and ARGS.get("save") != "1":
        doc.close(False)
        print("closed the unsaved build document (pass --arg keep=1 to keep it open)")
