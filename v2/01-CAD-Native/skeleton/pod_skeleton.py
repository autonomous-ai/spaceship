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
DOC_NAME = "100000_P01_POD-SKELETON_CAD"
CLOUD_FOLDER = "FocusPod v2"
F3D_REL = "v2/01-CAD-Native/skeleton/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/skeleton/100000_P01_POD-SKELETON_STEP.step"

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
    (XL + " + dl_w", XL + " + dl_w + door_w"), ("-glass_y - thresh_d / 2", "-glass_y + thresh_d / 2"),
    ("0 mm", "thresh_h"))
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
    (XL + " + dl_w", XL + " + dl_w + door_w"), ("-glass_y - kick_d / 2", "-glass_y + kick_d / 2"),
    ("thresh_h", "door_z0"))

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
        print("saved:", doc.saveAs(DOC_NAME, folder, "Spaceship pod skeleton stage A, P01", ""))
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
