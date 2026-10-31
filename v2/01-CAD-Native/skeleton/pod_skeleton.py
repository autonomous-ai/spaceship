"""Spaceship (FocusPod v2) pod skeleton, stage A: native, parameter-driven.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/pod_skeleton.py
        [--arg close_previous=1] [--arg save=1] [--arg export=1]

One Fusion design, components per v2/00-Control/assembly-tree.md (POD with
BASE, WALL, FRONT > DOOR AND GLAZING, CEILING, LINING, AIR, ELECTRICAL,
INTERIOR). Every panel, block and glass pane is an envelope body in its own
component: a fully constrained rectangle on an XY plane offset by a
parameter, extruded by a parameter. Coordinates follow conventions.md
section 4: origin on the room floor at the pod centre, +X right (seen from
outside facing the door), +Y back, +Z up.

Stage A places the front decor blocks and the door as boxes. The faceted
front (true decor facets and the fixed glass outline, measured from the v1
STEP) is stage B; the overlaps that the boxes cause are listed in EXPECTED
with reasons. Any other clash fails the run.
"""

import time
import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REV = "P02" if ARGS.get("stage", "B") == "B" else "P01"     # P02 = stage B, the measured faceted front
DOC_NAME = "100000_%s_POD-SKELETON_CAD" % REV
CLOUD_FOLDER = "FocusPod v2"
F3D_REL = "v2/01-CAD-Native/skeleton/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/skeleton/100000_%s_POD-SKELETON_STEP.step" % REV

# name, expression, unit, status, source
PARAMS = [
    ("pod_w", "2500 mm", "mm", "decided", "D-01; conventions s4 (X = +-1250)"),
    ("pod_d", "1700 mm", "mm", "decided", "D-01; conventions s4 (Y = +-850)"),
    ("pod_h", "2400 mm", "mm", "decided", "D-21 (room floor to roof skin top)"),
    ("glide_h", "10 mm", "mm", "assumption", "layout study inputs.py glide_h"),
    ("band_h", "100 mm", "mm", "source", "layout study B1 list B-BAND 100x40; inputs.py base_h"),
    ("band_t", "40 mm", "mm", "source", "layout study B1 list B-BAND 100x40"),
    ("stack_t", "81 mm", "mm", "decided", "D-16, D-42 (walls and ceiling)"),
    ("outer_t", "43 mm", "mm", "source", "layout study B1 final list W-SIDE 43 (ACP 3 + frame 40)"),
    ("cass_t", "34 mm", "mm", "source", "layout study B1 final list L-CASS 34 (tray + 25 gap + felt 9)"),
    ("wall_depth", "1500 mm", "mm", "source", "build plan II; conventions s4 (wall front edge Y = -650)"),
    ("floor_t", "15 mm", "mm", "source", "layout study B1 list B-FLOOR 15"),
    ("thresh_h", "20 mm", "mm", "decided", "D-18"),
    ("thresh_d", "60 mm", "mm", "source", "layout study B1 list B-THRESH 1176 x 60 x 20"),
    ("decor_d", "235 mm", "mm", "decided", "D-39 (230-235, v1); B1 list 235"),
    ("dl_w", "278 mm", "mm", "source", "B1 list F-DL 278 (v1 BOM DL)"),
    ("dr_w", "1016 mm", "mm", "source", "B1 list F-DR 1016 (v1 STEP solid 78)"),
    ("dt_w", "1697 mm", "mm", "source", "B1 list F-DT 1697 (v1 BOM DT)"),
    ("dt_h", "280 mm", "mm", "source", "B1 list F-DT 280"),
    ("door_w", "1176 mm", "mm", "decided", "D-46"),
    ("door_h", "2011 mm", "mm", "source", "B1 list F-GLASS-DOOR 2011; v1 STEP solid 238"),
    ("glass_t", "8.76 mm", "mm", "decided", "D-46 (4+4 laminate)"),
    ("glass_y", "699 mm", "mm", "source", "v1 STEP solid 238 centre Y = -699 (layout study data)"),
    ("kick_d", "20 mm", "mm", "assumption", "kick strip envelope depth (D-40 gives the height only)"),
    # stage B: the faceted front, measured from the v1 STEP (V1-FRONT-FACETS.md), Z shifted
    # -17 mm so v1's top (2417) meets the 2400 datum (D-21); X offsets from the side faces
    ("fr_dz", "17 mm", "mm", "calculation", "v1 front top 2417 (v2 frame) - pod_h 2400"),
    ("door_xl", "289 mm", "mm", "source", "V1-FRONT-FACETS: door left edge X -961 = -1250 + 289"),
    ("door_xbr", "1464 mm", "mm", "source", "V1-FRONT-FACETS: door bottom-right X 214"),
    ("door_xtr", "1182 mm", "mm", "source", "V1-FRONT-FACETS: door top-right X -68"),
    ("door_zb", "122 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: door bottom Z 122"),
    ("door_zt", "2133 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: door top Z 2133"),
    ("fix_xbl", "1468 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass bottom-left X 218"),
    ("fix_xbr", "302 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass bottom-right X 948 = 1250 - 302"),
    ("fix_xk", "501 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass knee X 749 = 1250 - 501"),
    ("fix_zk", "1538 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass knee Z 1538"),
    ("fix_xtr", "1480 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass top-right X 230 = -1250 + 1480"),
    ("fix_xtl", "1184 mm", "mm", "source", "V1-FRONT-FACETS: fixed glass top-left X -66"),
    ("fix_zb", "119 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass bottom Z 119"),
    ("fix_zt", "2136 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: fixed glass top Z 2136"),
    ("dt_zb", "2137 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: DT and DR edge above the glass Z 2137"),
    ("ch_zlo", "2217 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: top chamfer front edge Z 2217 at Y -848"),
    ("ch_yb", "672 mm", "mm", "source", "V1-FRONT-FACETS: top chamfer back edge Y -672"),
    ("dl_x2", "92 mm", "mm", "source", "V1-FRONT-FACETS: DL facet knee X -1158 = -1250 + 92"),
    ("dl_y2", "752 mm", "mm", "source", "V1-FRONT-FACETS: DL facet knee Y -752"),
    ("dl_x3", "271 mm", "mm", "source", "V1-FRONT-FACETS: DL front corner X -979"),
    ("dl_y3", "844 mm", "mm", "source", "V1-FRONT-FACETS: DL front corner Y -844"),
    ("dl_y1", "670 mm", "mm", "source", "V1-FRONT-FACETS: DL outer facet start Y -670"),
    ("dl_zo", "2414 mm - fr_dz", "mm", "source", "V1-FRONT-FACETS: DL top at the outer corner Z 2414"),
    ("dt_x2", "281 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet left X -969 = -1250 + 281"),
    ("dt_y2", "767 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet left Y -767"),
    ("dt_y3", "753 mm", "mm", "source", "V1-FRONT-FACETS: DT lower facet outer Y -753 at X -1154"),
    ("dr_xc", "198 mm", "mm", "source", "V1-FRONT-FACETS: DR corner facet front X 1052 = 1250 - 198"),
    ("dr_yc", "672 mm", "mm", "source", "V1-FRONT-FACETS: DR corner facet back Y -672"),
    # derived
    ("wall_z0", "glide_h + band_h", "mm", "calculation", "walls stand on the base band"),
    ("wall_h", "pod_h - wall_z0", "mm", "calculation", "2290 = layout study v2_model wall_h"),
    ("side_h", "wall_h / 2", "mm", "calculation", "D-23: 2 sheets per side wall; B1 list 1145"),
    ("back_h", "wall_h - stack_t", "mm", "calculation", "back wall stands under the ceiling (v2_model back_h)"),
    ("back_ph", "back_h / 2", "mm", "calculation", "D-23: 4 sheets on the back; B1 list 1104"),
    ("inner_w", "pod_w - 2 * stack_t", "mm", "calculation", "2338 between the side walls"),
    ("door_z0", "pod_h - dt_h - door_h", "mm", "calculation", "door meets DT; leaves 89 above the threshold (D-40 about 90)"),
]

ASSEMBLIES = [  # key, part number, name, Vietnamese name, parent key
    ("BASE", "110000", "BASE", "Đế / sàn", None),
    ("WALL", "210000", "WALL", "Vách", None),
    ("FRONT", "350000", "FRONT", "Mặt trước", None),
    ("GLAZING", "360000", "FRONT - DOOR AND GLAZING", "Cửa và kính", "FRONT"),
    ("CEILING", "410000", "CEILING", "Trần", None),
    ("LINING", "510000", "LINING", "Lớp tiêu âm", None),
    ("AIR", "610000", "AIR", "Thông gió", None),
    ("ELECTRICAL", "710000", "ELECTRICAL", "Điện", None),
    ("INTERIOR", "810000", "INTERIOR", "Nội thất", None),
]

XL, XR = "-pod_w / 2", "pod_w / 2"
YB, YW, YF = "pod_d / 2", "pod_d / 2 - wall_depth", "-pod_d / 2"
XIL, XIR = "-pod_w / 2 + stack_t", "pod_w / 2 - stack_t"    # inner faces: linings span between these
XOL, XOR = "-pod_w / 2 + outer_t", "pod_w / 2 - outer_t"    # side frames' inner faces: back and ceiling
# frames span frame to frame between these, with the side skins over their edges (PM ruling on
# PR #15, build plan rule 4)

# envelope: assembly, code, name, layout-study id, (x0, x1), (y0, y1), (z0, z1)
ENVELOPES = []


def env(asm, code, name, sid, x, y, z):
    ENVELOPES.append((asm, code, name, sid, x, y, z))


for side, x0, x1, cx0, cx1 in (("L", XL, XL + " + outer_t", XIL + " - cass_t", XIL),
                               ("R", XR + " - outer_t", XR, XIR, XIR + " + cass_t")):
    for row, z0, z1 in ((1, "wall_z0", "wall_z0 + side_h"), (2, "wall_z0 + side_h", "pod_h")):
        cz1 = z1 if row == 1 else "pod_h - outer_t"   # upper lining stops under the ceiling frame
        lo = "LOWER" if row == 1 else "UPPER"
        env("WALL", "%s%d" % (side, row), "WALL - SIDE PANEL - %s - %s" % (lo, "LH" if side == "L" else "RH"),
            "W-SIDE-" + lo[:2], (x0, x1), (YW, YB), (z0, z1))
        env("LINING", "%s%d-CASS" % (side, row), "LINING - CASSETTE - SIDE %s - %s" % (lo, side),
            "L-CASS-SIDE-" + lo[:2], (cx0, cx1), (YW, YB + " - stack_t"), (z0, cz1))
for code, x0, x1, z0, z1 in (("B1", -1, "0 mm", "wall_z0", "wall_z0 + back_ph"),
                             ("B2", "0 mm", 1, "wall_z0", "wall_z0 + back_ph"),
                             ("B3", -1, "0 mm", "wall_z0 + back_ph", "wall_z0 + back_h"),
                             ("B4", "0 mm", 1, "wall_z0 + back_ph", "wall_z0 + back_h")):
    lo = "LOWER" if code in ("B1", "B2") else "UPPER"
    ox0, ox1 = (XOL if x0 == -1 else x0), (XOR if x1 == 1 else x1)
    ix0, ix1 = (XIL if x0 == -1 else x0), (XIR if x1 == 1 else x1)
    env("WALL", code, "WALL - BACK PANEL - %s - %s" % (lo, code), "W-BACK-" + lo[:2],
        (ox0, ox1), (YB + " - outer_t", YB), (z0, z1))
    env("LINING", code + "-CASS", "LINING - CASSETTE - BACK %s - %s" % (lo, code), "L-CASS-BACK-" + lo[:2],
        (ix0, ix1), (YB + " - stack_t", YB + " - stack_t + cass_t"), (z0, z1))
for code, ox0, ox1, ix0, ix1 in (("C1", XOL, "0 mm", XIL, "0 mm"), ("C2", "0 mm", XOR, "0 mm", XIR)):
    env("CEILING", code, "CEILING - HALF PANEL - " + code, "C-HALF",
        (ox0, ox1), (YW, YB), ("pod_h - outer_t", "pod_h"))
    env("LINING", code + "-CASS", "LINING - CASSETTE - CEILING - " + code, "L-CASS-HALF",
        (ix0, ix1), (YW, YB + " - stack_t"), ("pod_h - stack_t", "pod_h - stack_t + cass_t"))
    env("BASE", "F" + code[1], "BASE - THIN FLOOR PANEL - F" + code[1], "B-FLOOR",
        (ix0, ix1), (YW, YB + " - stack_t"), ("0 mm", "floor_t"))
env("BASE", "BAND-BACK", "BASE - BASE BAND - BACK", "B-BAND-BACK",
    (XL + " + band_t", XR + " - band_t"), (YB + " - band_t", YB), ("glide_h", "wall_z0"))
env("BASE", "BAND-L", "BASE - BASE BAND - SIDE - LH", "B-BAND-SIDE",
    (XL, XL + " + band_t"), (YF + " + band_t", YB), ("glide_h", "wall_z0"))
env("BASE", "BAND-R", "BASE - BASE BAND - SIDE - RH", "B-BAND-SIDE",
    (XR + " - band_t", XR), (YF + " + band_t", YB), ("glide_h", "wall_z0"))
env("BASE", "THRESHOLD", "BASE - DOOR THRESHOLD", "B-THRESH",
    (XL + " + door_xl", XL + " + door_xbr"), ("-glass_y - thresh_d / 2", "-glass_y + thresh_d / 2"),
    ("0 mm", "thresh_h"))
STAGE = ARGS.get("stage", "B")
if STAGE == "A":
  env("FRONT", "DL", "FRONT - DECOR BLOCK - LEFT - PLACEHOLDER BOX (STAGE A, NOT THE LOOK)", "F-DL",
    (XL, XL + " + dl_w"), (YF, YF + " + decor_d"), ("wall_z0", "pod_h"))
  env("FRONT", "DR", "FRONT - DECOR BLOCK - RIGHT - PLACEHOLDER BOX (STAGE A, NOT THE LOOK)", "F-DR",
    (XR + " - dr_w", XR), (YF, YF + " + decor_d"), ("wall_z0", "pod_h"))
  env("FRONT", "DT", "FRONT - DECOR BLOCK - TOP - PLACEHOLDER BOX (STAGE A, NOT THE LOOK)", "F-DT",
    (XL + " + dl_w", XL + " + dl_w + dt_w"), (YF, YF + " + decor_d"), ("pod_h - dt_h", "pod_h"))
  env("GLAZING", "DOOR", "FRONT - DOOR LEAF GLASS 4+4", "F-GLASS-DOOR",
    (XL + " + dl_w", XL + " + dl_w + door_w"), ("-glass_y - glass_t / 2", "-glass_y + glass_t / 2"),
    ("door_z0", "door_z0 + door_h"))
env("GLAZING", "KICK", "FRONT - DOOR KICK STRIP", "D-40",
    (XL + " + door_xl", XL + " + door_xbr"), ("-glass_y - kick_d / 2", "-glass_y + kick_d / 2"),
    ("thresh_h", "door_zb" if STAGE == "B" else "door_z0"))

# Stage B bodies have no box expressions; the edit test checks these anchors
# (code, bounding-box index 0..5 = xmin ymin zmin xmax ymax zmax, expression).
FACET_ANCHORS = [
    ("DL", 0, XL), ("DL", 2, "wall_z0"), ("DT", 0, XL), ("DT", 5, "pod_h"),
    ("DR", 3, XR), ("DR", 5, "pod_h"), ("DOOR", 0, XL + " + door_xl"), ("DOOR", 3, XL + " + door_xbr"),
    ("FIXED", 3, XR + " - fix_xbr"), ("FIXED", 5, "fix_zt"),
]

# Overlaps the stage A boxes make on purpose, with the reason. Any other
# clash fails the run.
EXPECTED = [
    (("DL", "L1"), "decor wraps the side wall front edge by 35 mm (D-39, conventions s4)"),
    (("DL", "L2"), "same"), (("DL", "L1-CASS"), "same"), (("DL", "L2-CASS"), "same"),
    (("DR", "R1"), "same"), (("DR", "R2"), "same"), (("DR", "R1-CASS"), "same"), (("DR", "R2-CASS"), "same"),
    (("DT", "DR"), "boxes of faceted blocks overlap; the facets don't (stage B)"),
    (("DT", "C1"), "DT covers the ceiling front edge (v1); boxes only (stage B)"),
    (("DT", "C2"), "same"), (("DT", "C1-CASS"), "same"), (("DT", "C2-CASS"), "same"),
    (("DL", "BAND-L"), "decor stands on the base band corner; boxes only (stage B)"),
    (("DR", "BAND-R"), "same"),
    (("DL", "C1"), "box corner reaches the ceiling front edge (stage B)"),
    (("DR", "C2"), "same"), (("DL", "C1-CASS"), "same"), (("DR", "C2-CASS"), "same"),
    (("DT", "L2"), "DT wraps the left wall's upper front edge (v1 measured, stage B)"),
    (("DT", "L2-CASS"), "same"),
]

MM = 0.1


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def add_params(design):
    for name, expr, unit, status, src in PARAMS:
        design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))


def new_comp(parent, pn, name, vn):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s | P01" % (name, vn)
    return c


def build_envelope(design, comp, code, name, sid, xr, yr, zr):
    x0, x1, y0, y1, z0, z1 = (ev(design, e) for e in (xr[0], xr[1], yr[0], yr[1], zr[0], zr[1]))
    planes = comp.constructionPlanes
    if abs(z0) < 1e-9:
        plane = comp.xYConstructionPlane
    else:
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, vi(zr[0]))
        plane = planes.add(pin)
        plane.name = "PLANE - %s BOTTOM" % code
    sk = comp.sketches.add(plane)
    sk.name = "OUTLINE - %s" % code
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0 * MM, y0 * MM, 0), adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
    gc = sk.geometricConstraints
    for ln in rect:   # addTwoPointRectangle doesn't always add these
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType())
                   for c in ln.geometricConstraints):
            s0, s1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(s0.y - s1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for p in (ln.startSketchPoint, ln.endSketchPoint):
            if all(p != q for q in pts):
                pts.append(p)

    def near(x, y):
        return min(pts, key=lambda p: (p.geometry.x - x * MM) ** 2 + (p.geometry.y - y * MM) ** 2)
    c00, c10, c01 = near(x0, y0), near(x1, y0), near(x0, y1)
    dims = sk.sketchDimensions
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    tp = adsk.core.Point3D.create((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
    dims.addDistanceDimension(c00, c10, H, tp).parameter.expression = "(%s) - (%s)" % (xr[1], xr[0])
    dims.addDistanceDimension(c00, c01, V, tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    if abs(x0) < 1e-6:
        gc.addVerticalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, H, tp).parameter.expression = "abs(%s)" % xr[0]
    if abs(y0) < 1e-6:
        gc.addHorizontalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, V, tp).parameter.expression = "abs(%s)" % yr[0]
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    ext_in = comp.features.extrudeFeatures.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, vi("(%s) - (%s)" % (zr[1], zr[0])))
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "EXTRUDE - %s ENVELOPE" % code
    body = ext.bodies.item(0)
    body.name = "%s ENVELOPE" % code
    return body


def box(body):
    b = body.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def clash_check(bodies):
    """Pairwise solid intersections; fails on any pair not in EXPECTED."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    allowed = {frozenset(k) for k, _r in EXPECTED}
    codes = list(bodies)
    hits, bad = [], []
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            a, b = codes[i], codes[j]
            ba, bb = box(bodies[a]), box(bodies[b])
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(bodies[a]), tbm.copy(bodies[b])
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((a, b, round(vol)))
                if frozenset((a, b)) not in allowed:
                    bad.append((a, b, round(vol)))
    return hits, bad



# ---------------------------------------------------------------- stage B: faceted front

def _axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis ('x', 'y' or 'z') maps to."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def poly(design, comp, plane, plane_axes, fixed, name, pts):
    """Closed polygon on `plane`, each vertex dimensioned from the sketch origin
    along both plane axes by its parameter expression (fully constrained).
    plane_axes: the two model axes in the plane, e.g. ("x", "z"); fixed: value
    in mm of the third axis on the plane. pts: [(expr_a, expr_b)]."""
    sk = comp.sketches.add(plane)
    sk.name = name
    third = ({"x", "y", "z"} - set(plane_axes)).pop()
    sp = []
    for ea, eb in pts:
        c = {plane_axes[0]: ev(design, ea), plane_axes[1]: ev(design, eb), third: fixed}
        sp.append(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    lines = sk.sketchCurves.sketchLines
    verts, edges = [], []          # the polygon's corners in the order of pts, and its lines
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
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    expr_on = {}                   # sketch axis -> index into (ea, eb)
    for k, ax in enumerate(plane_axes):
        expr_on[_axis_of(sk, ax)] = k
    for sa in ("x", "y"):
        # corners joined by an edge parallel to the other axis share this coordinate:
        # constrain that edge and dimension one corner per group (never redundant)
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
            ex = pts[i][expr_on[sa]]
            vp = verts[i]
            if abs(ev(design, ex)) < 1e-6:
                (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(vp, sk.originPoint)
            else:
                g = vp.geometry
                tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
                dims.addDistanceDimension(sk.originPoint, vp, H if sa == "x" else V, tp).parameter.expression = \
                    "abs(%s)" % ex
    if not sk.isFullyConstrained:
        info = ["v%d %s%s" % (i, "ok" if vp.isFullyConstrained else "LOOSE",
                              "(%.1f,%.1f)" % (vp.geometry.x * 10, vp.geometry.y * 10)) for i, vp in enumerate(verts)]
        cons = [c.objectType.split("::")[-1] for c in sk.geometricConstraints]
        raise RuntimeError("sketch not fully constrained: %s | dims %d | %s | constraints %s" % (
            name, sk.sketchDimensions.count, " ".join(info), cons))
    return sk


def _normal_sign(sk, axis):
    n = sk.xDirection.crossProduct(sk.yDirection)
    return 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1


def extrude_span(comp, sk, axis, a_expr, b_expr, op, bodies=None, name=""):
    """Extrude the sketch's profiles along a model axis from a to b (a < b)."""
    sign = _normal_sign(sk, axis)
    coll = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        coll.add(pr)
    ei = comp.features.extrudeFeatures.createInput(coll, op)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi("(%s) * (%d)" % (a_expr, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("(%s) - (%s)" % (b_expr, a_expr))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    if bodies:
        ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    return f


def faceted_front(design, asm):
    """DL, DT, DR as measured outlines, extruded and cut by the measured planes;
    door and fixed glass with their true outlines. Returns {code: body}."""
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    out = {}
    back = YF + " + decor_d"
    chamfer = [(YF, "ch_zlo"), ("-ch_yb", "pod_h"), (YF, "pod_h")]

    def comp_for(a, code, name, sid):
        return new_comp(asm[a], "", "%s %s" % (code, name), sid)

    # DL: plan outline (two facets), up to the 45 degree slope shared with DT
    c = comp_for("FRONT", "DL", "FRONT - DECOR BLOCK - LEFT (FACETED, v1 MEASURED)", "F-DL")
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - DL FACETS",
              [(XL, back), (XL, "-dl_y1"), (XL + " + dl_x2", "-dl_y2"), (XL + " + dl_x3", "-dl_y3"),
               (XL + " + dl_w", "-dl_y3"), (XL + " + dl_w", back)])
    f = extrude_span(c, sk, "z", "wall_z0", "pod_h", NEW, name="EXTRUDE - DL PLAN")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "SLOPE - DL TOP",
              [(XL, "dl_zo"), (XL + " + dl_w", "dt_zb"), (XL + " + dl_w", "pod_h"), (XL, "pod_h")])
    extrude_span(c, sk, "y", YF, back, CUT, [b], "CUT - DL TOP SLOPE")
    b.name = "DL FACETED"
    out["DL"] = b

    # DT: plan outline (lower facet), above the slope, front top chamfer
    c = comp_for("FRONT", "DT", "FRONT - DECOR BLOCK - TOP (FACETED, v1 MEASURED)", "F-DT")
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "PLAN - DT FACETS",
              [(XL, back), (XL, "-dl_y1"), (XL + " + dl_x2 + 4 mm", "-dt_y3"), (XL + " + dt_x2", "-dt_y2"),
               (XL + " + fix_xtr", YF), (XL + " + fix_xtr", back)])
    f = extrude_span(c, sk, "z", "dt_zb", "pod_h", NEW, name="EXTRUDE - DT PLAN")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "SLOPE - DT BOTTOM",
              [(XL, "dt_zb"), (XL + " + dl_w", "dt_zb"), (XL, "dl_zo")])
    extrude_span(c, sk, "y", YF, back, CUT, [b], "CUT - DT BOTTOM SLOPE")
    sk = poly(design, c, c.yZConstructionPlane, ("y", "z"), 0, "CHAMFER - DT TOP FRONT", chamfer)
    extrude_span(c, sk, "x", XL, XR, CUT, [b], "CUT - DT TOP CHAMFER")
    b.name = "DT FACETED"
    out["DT"] = b

    # DR: front outline following the fixed glass, corner facet, top chamfer
    c = comp_for("FRONT", "DR", "FRONT - DECOR BLOCK - RIGHT (FACETED, v1 MEASURED)", "F-DR")
    sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "FRONT - DR OUTLINE",
              [(XR + " - fix_xbr", "fix_zb"), (XR, "fix_zb"), (XR, "pod_h"), (XL + " + fix_xtr", "pod_h"),
               (XL + " + fix_xtr", "dt_zb"), (XR + " - fix_xk", "fix_zk")])
    f = extrude_span(c, sk, "y", YF, back, NEW, name="EXTRUDE - DR OUTLINE")
    b = f.bodies.item(0)
    sk = poly(design, c, c.xYConstructionPlane, ("x", "y"), 0, "CORNER FACET - DR",
              [(XR + " - dr_xc", YF), (XR, "-dr_yc"), (XR, YF)])
    extrude_span(c, sk, "z", "0 mm", "pod_h", CUT, [b], "CUT - DR CORNER FACET")
    sk = poly(design, c, c.yZConstructionPlane, ("y", "z"), 0, "CHAMFER - DR TOP FRONT", chamfer)
    extrude_span(c, sk, "x", XL, XR, CUT, [b], "CUT - DR TOP CHAMFER")
    b.name = "DR FACETED"
    out["DR"] = b

    # glass, true outlines
    gy0, gy1 = "-glass_y - glass_t / 2", "-glass_y + glass_t / 2"
    for code, name, sid, pts in (
            ("DOOR", "FRONT - DOOR LEAF GLASS 4+4 (TRAPEZOID, v1 MEASURED)", "F-GLASS-DOOR",
             [(XL + " + door_xl", "door_zb"), (XL + " + door_xbr", "door_zb"),
              (XL + " + door_xtr", "door_zt"), (XL + " + door_xl", "door_zt")]),
            ("FIXED", "FRONT - FIXED GLASS 4+4 (PENTAGON, v1 MEASURED)", "F-GLASS-FIXED",
             [(XL + " + fix_xbl", "fix_zb"), (XR + " - fix_xbr", "fix_zb"), (XR + " - fix_xk", "fix_zk"),
              (XL + " + fix_xtr", "fix_zt"), (XL + " + fix_xtl", "fix_zt")])):
        c = comp_for("GLAZING", code, name, sid)
        sk = poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, "OUTLINE - " + code, pts)
        f = extrude_span(c, sk, "y", gy0, gy1, NEW, name="EXTRUDE - %s GLASS" % code)
        f.bodies.item(0).name = code + " GLASS"
        out[code] = f.bodies.item(0)
    return out


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("close_previous") == "1":
        for i in range(app.documents.count - 1, -1, -1):
            d = app.documents.item(i)
            if d.objectType != adsk.fusion.FusionDocument.classType():
                continue          # drawings have no design product
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            if dd and not d.isSaved and dd.rootComponent.partNumber == "100000":
                d.close(False)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    add_params(design)
    root = design.rootComponent
    root.partNumber = "100000"
    root.description = "POD - SPACESHIP (FocusPod v2) skeleton | Pod hoàn chỉnh | P01"
    asm = {}
    for key, pn, name, vn, parent in ASSEMBLIES:
        asm[key] = new_comp(asm[parent] if parent else root, pn, name, vn)
    bodies = {}
    for a, code, name, sid, x, y, z in ENVELOPES:
        comp = new_comp(asm[a], "", "%s %s" % (code, name), sid)
        bodies[code] = build_envelope(design, comp, code, name, sid, x, y, z)
    if STAGE == "B":
        bodies.update(faceted_front(design, asm))
    tl = design.timeline
    bad_items = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    print("envelopes %d, timeline %d items, unhealthy %d, loose sketches %d, parameters %d" % (
        len(bodies), tl.count, len(bad_items), len(loose), design.userParameters.count))
    for a, code, name, sid, x, y, z in ENVELOPES:
        b = box(bodies[code])
        print("ENV|%s|%s|%s|%g x %g x %g|%s" % (code, a, sid, round(b[3] - b[0], 2), round(b[4] - b[1], 2),
                                                 round(b[5] - b[2], 2), b))
    hits, bad = clash_check(bodies)
    print("clash pairs %d, expected %d, unexpected %d" % (len(hits), len(hits) - len(bad), len(bad)))
    for a, b, v in bad:
        print("UNEXPECTED CLASH %s x %s: %d mm3" % (a, b, v))
    rb = box(root)
    print("pod box", rb)
    if bad_items or loose or bad:
        raise RuntimeError("skeleton checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
    if ARGS.get("save") == "1":
        proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
        app.data.activeProject = proj
        folder = proj.rootFolder.dataFolders.itemByName(CLOUD_FOLDER)
        if any(df.name == DOC_NAME for df in folder.dataFiles):
            raise RuntimeError("%s already in %s" % (DOC_NAME, CLOUD_FOLDER))
        print("saved:", doc.saveAs(DOC_NAME, folder, "Spaceship pod skeleton, %s" % REV, ""))
    if ARGS.get("export") == "1":
        root_dir = ARGS["repo_root"]
        em = design.exportManager
        for rel, mk in ((F3D_REL, em.createFusionArchiveExportOptions),
                        (STEP_REL, em.createSTEPExportOptions)):
            ok = False
            for _try in range(10):        # right after a save Fusion may still be uploading
                ok = em.execute(mk("%s/%s" % (root_dir, rel), root))
                if ok:
                    break
                adsk.doEvents()
                time.sleep(3)
            print("export %s: %s" % (rel, ok))
            if not ok:
                raise RuntimeError("export failed: " + rel)
