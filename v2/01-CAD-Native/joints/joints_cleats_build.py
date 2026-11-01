"""Build the frame cleats of joints register J-FRAME-01 (D-115, D-117) as native Fusion designs.

Revision P01 (PROPOSED). Run through the Fusion lock (tools/fusion/README.md), sample first (D-118):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_cleats_build.py --arg only=831003,831006
    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_cleats_build.py --arg only=831005,831004

Each cleat is its own parametric mm design in "Default Project/FocusPod v2/joints", so WALL and CEILING can
insert it by reference as its own component (D-120). Sizes come from cleat_check.py (the calculation the
register quotes); each design's user parameters carry their status and source. Every cleat is a profile in
the frame's plane extruded across the frame (an extrusion cut to depth), symmetric about the members'
mid-depth.

    831003_P01_HARDWARE-FRAME-CORNER-CLEAT-20X40_CAD            corner, 20 x 40 to 20 x 40 (45°)
    831004_P01_HARDWARE-FRAME-CORNER-CLEAT-40X40_CAD            corner, 40 x 40 to 40 x 40 (45°)
    831005_P01_HARDWARE-FRAME-CORNER-CLEAT-40X40-TO-20X40_CAD   corner, 40 x 40 to 20 x 40 (26.57° and 63.43°)
    831006_P01_HARDWARE-FRAME-T-PLUG_CAD                        T plug in a stud's end, tongue into the rail

Corner cleats: origin at the frame's outer corner (where the two members' outer faces meet), on the members'
mid-depth plane; +X along member A, +Y along member B, Z across the frame. Leg A (width wa, in member A) runs
La past the corner; leg B (width wb) runs Lb. On 831005, member A is the 40 x 40. The cleat sits wall_gap
(the tube's 1.2 wall plus the 1.0 glue line) in from both outer faces. Hollow (walls cl_t), one web on the
corner's diagonal, two 0.6 spacer ribs on each glue face, and a crimp notch at the middle of each leg's
inner face.

T plug: origin at the stud's end, on its centre line and mid-depth; +X into the stud, Y across it in the
frame's plane, Z across the frame. A hollow box (two chambers) goes into the stud; a solid tongue stands
plug_tl out of its end into the rail's slot.

Each design is saved (a new design, never a copy), exported (.f3d to v2/01-CAD-Native/joints/, STEP to
v2/03-Manufacturing/joints/), checked (one healthy body; box and mass against the same calculation as
cleat_check.py, to 1%), edit-tested (guideline 4.4: change a driving parameter, rebuild, measure, revert,
measure) and closed without keeping the test. Before making each design it runs the shared safe-to-create
check (tools/fusion/fusion_folder.py, loaded by full path from this checkout).
"""
import os
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REPO = ARGS.get("repo_root", "")
PROJECT, PARENT, FOLDER = "Default Project", "FocusPod v2", "joints"
REV = "P01"
CAD_DIR = "v2/01-CAD-Native/joints"
MFG_DIR = "v2/03-Manufacturing/joints"
CM = 0.1               # the API's lengths are cm
RHO = 2.70e-3          # g/mm3, 6005A and 6061 (source)

NOTE = ("UNITS MM; MATERIAL EN AW-6005A-T6 OR EN AW-6061-T6 EXTRUSION (Rp0.2 >= 215 MPa); FINISH MILL, DEBURRED; "
        "ISO 2768-m; WALLS 1.0 (HOLD-21); glue faces clean and grease-free; joints register J-FRAME-01; PROPOSED")

COMMON = [  # name, expression, comment (status and source)
    ("wall_gap", "2.2 mm", "CALCULATION: the tube's 1.2 wall plus the 1.0 nominal glue line; the cleat's faces sit this far in from the members' outer faces (J-FRAME-01)"),
    ("cl_t", "1 mm", "ASSUMPTION: cleat walls; the extruder confirms its minimum (HOLD-21)"),
    ("rib_h", "0.6 mm", "ASSUMPTION: spacer ribs on each glue face set the smallest glue line, inside SikaFast's 0.5 to 3 mm (PDS, source)"),
    ("rib_w", "1 mm", "ASSUMPTION: rib width"),
    ("rib_in", "0.5 mm", "ASSUMPTION: each rib's edge from its leg's root or tip"),
    ("notch_l", "6 mm", "ASSUMPTION: crimp boss length along the leg, as high as the ribs"),
    ("notch_w", "2 mm", "ASSUMPTION: crimp notch width; the crimp dent goes into it (T14, T15)"),
    ("notch_d", "1 mm", "ASSUMPTION: crimp notch depth from the boss's top (0.4 into the wall)"),
]

CORNERS = {  # part number: (design, name, Vietnamese, member note); sizes from cleat_check.py
    "831003": ("831003_P01_HARDWARE-FRAME-CORNER-CLEAT-20X40_CAD",
               "HARDWARE - FRAME CORNER CLEAT - 20 X 40 - 45 DEG", "Ke góc khung 20 × 40",
               "both members 20 x 40, 45 deg mitre"),
    "831004": ("831004_P01_HARDWARE-FRAME-CORNER-CLEAT-40X40_CAD",
               "HARDWARE - FRAME CORNER CLEAT - 40 X 40 - 45 DEG", "Ke góc khung 40 × 40",
               "both members 40 x 40, 45 deg mitre"),
    "831005": ("831005_P01_HARDWARE-FRAME-CORNER-CLEAT-40X40-TO-20X40_CAD",
               "HARDWARE - FRAME CORNER CLEAT - 40 X 40 TO 20 X 40", "Ke góc khung 40 × 40 với 20 × 40",
               "member A 40 x 40 (cut 26.57 deg off square), member B 20 x 40 (cut 63.43 deg off square)"),
}
PLUG = ("831006", "831006_P01_HARDWARE-FRAME-T-PLUG_CAD", "HARDWARE - FRAME T PLUG - 20 X 40 STUD",
        "Ke nối chữ T khung")


# ------------------------------------------------------------------ helpers
def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def mm(v_cm):
    return round(v_cm * 10.0, 3)


def p3(x, y, z=0.0):
    return adsk.core.Point3D.create(x * CM, y * CM, z * CM)


def box(body):
    b = body.boundingBox
    return tuple(mm(v) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                 b.maxPoint.x, b.maxPoint.y, b.maxPoint.z))


def fmt(b):
    return "X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f" % (b[0], b[3], b[1], b[4], b[2], b[5])


def calc():
    """cleat_check.py, the calculation the register quotes, loaded from this checkout by full path and printed
    (Fusion keeps modules loaded between runs): the one source for every size and mass here."""
    import importlib.util
    path = os.path.join(REPO, "v2/01-CAD-Native/joints/cleat_check.py")
    spec = importlib.util.spec_from_file_location("joints_cleat_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("can't load " + path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  sizes from %s" % mod.__file__)
    if os.path.abspath(str(mod.__file__)) != os.path.abspath(path):
        raise RuntimeError("loaded %s, not this checkout's %s" % (mod.__file__, path))
    return mod


def folder(app):
    proj = next((p for p in app.data.dataProjects if p.name == PROJECT), None)
    if proj is None:
        raise RuntimeError("no %r in the active hub" % PROJECT)
    parent = proj.rootFolder.dataFolders.itemByName(PARENT)
    if parent is None:
        raise RuntimeError("no %r folder" % PARENT)
    return parent.dataFolders.itemByName(FOLDER) or parent.dataFolders.add(FOLDER)


def _safe_to_create():
    """The shared check, loaded from this checkout by full path and printed: Fusion keeps modules loaded
    between runs, so an import by name could pick up another team's copy."""
    import importlib.util
    path = os.path.join(REPO, "tools/fusion/fusion_folder.py")
    spec = importlib.util.spec_from_file_location("joints_cleats_fusion_folder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("can't load " + path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  safe-to-create check from %s" % mod.__file__)
    if os.path.abspath(str(mod.__file__)) != os.path.abspath(path):
        raise RuntimeError("loaded %s, not this checkout's %s" % (mod.__file__, path))
    return mod.safe_to_create


def new_design(app, name):
    f = folder(app)
    for w in _safe_to_create()(f, name, "f3d"):        # raises if a new NAME.f3d isn't safe to make
        print("  warning: %s" % w)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    return doc, design, f


def add_params(design, params):
    for name, expr, comment in params:
        if design.userParameters.add(name, vi(expr), "mm", comment[:250]) is None:
            raise RuntimeError("could not add parameter " + name)


def material(comp):
    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
    if lib is None:
        print("  WARNING: no Fusion Material Library; material not set")
        return None
    pick = None
    for n in ("Aluminum 6061", "Aluminum 6061-T6", "Aluminum"):
        pick = lib.materials.itemByName(n)
        if pick:
            break
    if pick is None:
        print("  WARNING: no aluminium in the library; material not set")
        return None
    for b in comp.bRepBodies:
        b.material = pick
    return pick.name


def health(design):
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    if bad:
        raise RuntimeError("unhealthy features: %s" % bad)


def must_constrain(sk):
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch %r is not fully constrained" % sk.name)


SKIPPED = []


def constrain(what, fn):
    """Add a constraint or a dimension. Fusion makes a straight line drawn level or plumb horizontal or vertical
    by itself, so a dimension that the line already implies is refused as over-constraining (the first sample
    run, 2026-11-01): that one is skipped and named. Each sketch is then checked to be fully constrained with
    every point where it was drawn (at_points), so nothing skipped can leave a point loose or moved."""
    try:
        return fn()
    except RuntimeError as ex:
        if "OVER_CONSTRAINT" in str(ex):
            SKIPPED.append(what)
            return None
        raise


def dim_point(sk, pt, ex, ey, yaxis=None):
    """Fix a sketch point by its distances from the origin, as parameter expressions (positive distances; the
    point stays on the side it was drawn). A point on X = 0 goes onto the projected Y axis instead."""
    d, g = sk.sketchDimensions, sk.geometricConstraints
    x, y = pt.geometry.x, pt.geometry.y
    hor = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    ver = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    if ex is None:
        constrain("%s: on the Y axis" % sk.name, lambda: g.addCoincident(pt, yaxis))
    else:
        dim = constrain("%s: x %s" % (sk.name, ex), lambda: d.addDistanceDimension(
            sk.originPoint, pt, hor, adsk.core.Point3D.create(x / 2, y + 0.3, 0)))
        if dim is not None:
            dim.parameter.expression = ex
    dim = constrain("%s: y %s" % (sk.name, ey), lambda: d.addDistanceDimension(
        sk.originPoint, pt, ver, adsk.core.Point3D.create(x + 0.3, y / 2, 0)))
    if dim is not None:
        dim.parameter.expression = ey


def at_points(sk, want_mm):
    """Raise unless every point (mm) of want_mm is a point of the sketch, to 0.001 mm."""
    have = [(p.geometry.x * 10.0, p.geometry.y * 10.0) for p in sk.sketchPoints]
    for w in want_mm:
        if not any(abs(h[0] - w[0]) < 0.001 and abs(h[1] - w[1]) < 0.001 for h in have):
            raise RuntimeError("sketch %r: no point at %s after its constraints" % (sk.name, w))


def polygon(sk, pts, exprs, yaxis=None):
    """A closed polygon through pts (mm), each vertex fixed by exprs[i] = (x expression or None, y expression)."""
    ls = sk.sketchCurves.sketchLines
    lines = [ls.addByTwoPoints(p3(*pts[0]), p3(*pts[1]))]
    for k in range(2, len(pts)):
        lines.append(ls.addByTwoPoints(lines[-1].endSketchPoint, p3(*pts[k])))
    lines.append(ls.addByTwoPoints(lines[-1].endSketchPoint, lines[0].startSketchPoint))
    corners = [lines[0].startSketchPoint] + [ln.endSketchPoint for ln in lines[:-1]]
    for pt, (ex, ey) in zip(corners, exprs):
        dim_point(sk, pt, ex, ey, yaxis)
    at_points(sk, pts)
    return lines


def rect(sk, x0, y0, x1, y1, ex0, ey0, ex1, ey1):
    """An axis-aligned rectangle (mm) fixed by its lower-left (ex0, ey0) and upper-right (ex1, ey1) corners."""
    lines = sk.sketchCurves.sketchLines.addTwoPointRectangle(p3(x0, y0), p3(x1, y1))
    pts = {}
    for i in range(lines.count):
        for p in (lines.item(i).startSketchPoint, lines.item(i).endSketchPoint):
            pts.setdefault((round(p.geometry.x, 6), round(p.geometry.y, 6)), p)
    if len(pts) != 4:
        raise RuntimeError("rectangle with %d corners" % len(pts))
    lo = pts[min(pts, key=lambda k: k[0] + k[1])]
    hi = pts[max(pts, key=lambda k: k[0] + k[1])]
    dim_point(sk, lo, ex0, ey0)
    dim_point(sk, hi, ex1, ey1)
    at_points(sk, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def extrude(comp, sk, op, depth, body=None, name=""):
    coll = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        coll.add(sk.profiles.item(i))
    if coll.count == 0:
        raise RuntimeError("%s: no profiles" % name)
    ei = comp.features.extrudeFeatures.createInput(coll, op)
    ei.setSymmetricExtent(vi(depth), True)
    if body is not None:                   # the part's one body, fetched fresh after the features before
        if comp.bRepBodies.count != 1:
            raise RuntimeError("%s: %d bodies before it" % (name, comp.bRepBodies.count))
        ei.participantBodies = [comp.bRepBodies.item(0)]
    feat = comp.features.extrudeFeatures.add(ei)
    feat.name = name
    return feat


def save_export(app, doc, design, f, name, desc, step_name):
    if not doc.saveAs(name, f, desc, ""):
        raise RuntimeError("saveAs failed for " + name)
    em = design.exportManager
    f3d = os.path.join(REPO, CAD_DIR, name + ".f3d")
    if not em.execute(em.createFusionArchiveExportOptions(f3d, design.rootComponent)):
        raise RuntimeError("f3d export failed for " + name)
    print("  saved to %s/%s and exported %s" % (PARENT, FOLDER, os.path.relpath(f3d, REPO)))
    path = os.path.join(REPO, MFG_DIR, step_name)
    for _attempt in range(10):
        adsk.doEvents()
        if em.execute(em.createSTEPExportOptions(path, design.rootComponent)) and \
                os.path.exists(path) and os.path.getsize(path) > 2000:
            break
        time.sleep(3)
    else:
        raise RuntimeError("STEP export failed: " + step_name)
    print("  STEP %s" % step_name)


def edit_test(design, measure, changes, expect):
    before = measure()
    olds = []
    for name, expr in changes:
        p = design.userParameters.itemByName(name)
        olds.append((p, p.expression))
        p.expression = expr
    adsk.doEvents()
    health(design)
    after = measure()
    for p, old in olds:
        p.expression = old
    adsk.doEvents()
    health(design)
    back = measure()
    ok = expect(before, after) and all(abs(a - b) < 0.01 for a, b in zip(before, back))
    print("  EDIT TEST %s: %s | changed %s | reverted %s -> %s" % (
        ", ".join("%s=%s" % c for c in changes), fmt(before), fmt(after), fmt(back), "PASS" if ok else "FAIL"))
    if not ok:
        raise RuntimeError("edit test failed")


def check_body(comp, want_box, want_mass_g, label):
    if comp.bRepBodies.count != 1:
        raise RuntimeError("%s came out as %d bodies" % (label, comp.bRepBodies.count))
    body = comp.bRepBodies.item(0)
    b = box(body)
    if any(abs(a - w) > 0.01 for a, w in zip(b, want_box)):
        raise RuntimeError("%s box %s, want %s" % (label, fmt(b), fmt(want_box)))
    vol_g = body.volume * 1000.0 * RHO          # cm3 to mm3, at the register's density
    if abs(vol_g - want_mass_g) > 0.01 * want_mass_g:
        raise RuntimeError("%s mass %.2f g at 2.70 g/cm3, want %.2f g (cleat_check.py)" % (label, vol_g, want_mass_g))
    print("  %s: %s; %.2f g at 2.70 g/cm3 (calculation %.2f g)" % (label, fmt(b), vol_g, want_mass_g))
    return body


# ------------------------------------------------------------------ the corner cleats
def build_corner(app, pn):
    name = CORNERS[pn][0]
    doc, design, f = new_design(app, name)
    try:
        _corner(app, doc, design, f, pn)
    finally:                               # every run closes what it opened, saved or not
        if doc.isValid:
            doc.close(False)


def _corner(app, doc, design, f, pn):
    name, title, title_vi, note = CORNERS[pn]
    c = next(x for x in calc().CORNERS if x.pn == pn)
    wa, wb, La, Lb, d = c.wa, c.wb, float(c.La), float(c.Lb), float(c.d)
    print("CLEAT %s: legs %.1f x %g and %.1f x %g, %g deep (cleat_check.py)" % (pn, wa, La, wb, Lb, d))
    add_params(design, COMMON + [
        ("cl_wa", "%g mm" % wa, "CALCULATION: leg A's width, its bore less 2 x the 1.0 glue line (%s) (cleat_check.py)" % note),
        ("cl_wb", "%g mm" % wb, "CALCULATION: leg B's width, its bore less 2 x the 1.0 glue line (cleat_check.py)"),
        ("cl_La", "%g mm" % La, "CALCULATION: leg A past the corner, for the glue at 71%% of 10 MPa at 75.0 N m (cleat_check.py)"),
        ("cl_Lb", "%g mm" % Lb, "CALCULATION: leg B past the corner, as cl_La (cleat_check.py)"),
        ("cl_d", "%g mm" % d, "CALCULATION: depth across the frame, symmetric about the mid-depth (cleat_check.py)"),
    ])
    root = design.rootComponent
    root.partNumber = pn
    root.description = "%s | %s | rev %s | %s; %s; origin at the frame's outer corner, mid-depth" % (
        title, title_vi, REV, NOTE, note)
    comp = root
    g = 2.2

    # the L outline
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - L OUTLINE"
    pts = [(g, g), (g + wb + La, g), (g + wb + La, g + wa), (g + wb, g + wa), (g + wb, g + wa + Lb), (g, g + wa + Lb)]
    exprs = [("wall_gap", "wall_gap"), ("wall_gap + cl_wb + cl_La", "wall_gap"),
             ("wall_gap + cl_wb + cl_La", "wall_gap + cl_wa"), ("wall_gap + cl_wb", "wall_gap + cl_wa"),
             ("wall_gap + cl_wb", "wall_gap + cl_wa + cl_Lb"), ("wall_gap", "wall_gap + cl_wa + cl_Lb")]
    polygon(sk, pts, exprs)
    must_constrain(sk)
    ext = extrude(comp, sk, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, "cl_d", name="EXTRUDE - L")
    body = ext.bodies.item(0)
    body.name = "FRAME CORNER CLEAT %s" % pn

    # hollow: shell with both cut faces open
    caps = adsk.core.ObjectCollection.create()
    for fc in body.faces:
        if isinstance(fc.geometry, adsk.core.Plane):
            ok, n = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
            if ok and abs(n.z) > 0.99:
                caps.add(fc)
    if caps.count != 2:
        raise RuntimeError("expected 2 cut faces, found %d" % caps.count)
    si = comp.features.shellFeatures.createInput(caps, False)
    si.insideThickness = vi("cl_t")
    comp.features.shellFeatures.add(si).name = "SHELL - WALLS"

    # the web on the corner's diagonal, from the outer corner's inside to the inner corner's inside: a strip
    # cl_t wide whose ends stay inside the walls
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - DIAGONAL WEB"
    ax, ay = g + 0.5, g + 0.5
    bx, by = g + wb - 0.5, g + wa - 0.5
    L = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    nx, ny = -(by - ay) / L * 0.5, (bx - ax) / L * 0.5
    n_ex = "cl_t / 2 * (cl_wa - cl_t) / sqrt((cl_wa - cl_t) * (cl_wa - cl_t) + (cl_wb - cl_t) * (cl_wb - cl_t))"
    n_ey = "cl_t / 2 * (cl_wb - cl_t) / sqrt((cl_wa - cl_t) * (cl_wa - cl_t) + (cl_wb - cl_t) * (cl_wb - cl_t))"
    a_x, a_y = "(wall_gap + cl_t / 2)", "(wall_gap + cl_t / 2)"
    b_x, b_y = "(wall_gap + cl_wb - cl_t / 2)", "(wall_gap + cl_wa - cl_t / 2)"
    polygon(sk, [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)],
            [("%s - %s" % (a_x, n_ex), "%s + %s" % (a_y, n_ey)), ("%s - %s" % (b_x, n_ex), "%s + %s" % (b_y, n_ey)),
             ("%s + %s" % (b_x, n_ex), "%s - %s" % (b_y, n_ey)), ("%s + %s" % (a_x, n_ex), "%s - %s" % (a_y, n_ey))])
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.JoinFeatureOperation, "cl_d", body, "EXTRUDE - DIAGONAL WEB")

    # spacer ribs: two on each glue face, rib_in from the leg's root and tip
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - SPACER RIBS"
    r, rw, ri = 0.6, 1.0, 0.5
    for x0e, x0 in (("wall_gap + cl_wb + rib_in", g + wb + ri), ("wall_gap + cl_wb + cl_La - rib_in - rib_w", g + wb + La - ri - rw)):
        rect(sk, x0, g - r, x0 + rw, g, x0e, "wall_gap - rib_h", "%s + rib_w" % x0e, "wall_gap")       # leg A outer
        rect(sk, x0, g + wa, x0 + rw, g + wa + r, x0e, "wall_gap + cl_wa", "%s + rib_w" % x0e, "wall_gap + cl_wa + rib_h")
    for y0e, y0 in (("wall_gap + cl_wa + rib_in", g + wa + ri), ("wall_gap + cl_wa + cl_Lb - rib_in - rib_w", g + wa + Lb - ri - rw)):
        rect(sk, g - r, y0, g, y0 + rw, "wall_gap - rib_h", y0e, "wall_gap", "%s + rib_w" % y0e)       # leg B outer
        rect(sk, g + wb, y0, g + wb + r, y0 + rw, "wall_gap + cl_wb", y0e, "wall_gap + cl_wb + rib_h", "%s + rib_w" % y0e)
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.JoinFeatureOperation, "cl_d", body, "EXTRUDE - SPACER RIBS")

    # crimp bosses at the middle of each leg's inner face, then their notches
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - CRIMP BOSSES"
    mxa, mya = g + wb + La / 2, g + wa + Lb / 2
    xa, ya = "(wall_gap + cl_wb + cl_La / 2)", "(wall_gap + cl_wa + cl_Lb / 2)"
    rect(sk, mxa - 3, g + wa, mxa + 3, g + wa + r, "%s - notch_l / 2" % xa, "wall_gap + cl_wa", "%s + notch_l / 2" % xa,
         "wall_gap + cl_wa + rib_h")
    rect(sk, g + wb, mya - 3, g + wb + r, mya + 3, "wall_gap + cl_wb", "%s - notch_l / 2" % ya, "wall_gap + cl_wb + rib_h",
         "%s + notch_l / 2" % ya)
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.JoinFeatureOperation, "cl_d", body, "EXTRUDE - CRIMP BOSSES")
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - CRIMP NOTCHES"
    rect(sk, mxa - 1, g + wa - 0.4, mxa + 1, g + wa + 1.1, "%s - notch_w / 2" % xa, "wall_gap + cl_wa + rib_h - notch_d",
         "%s + notch_w / 2" % xa, "wall_gap + cl_wa + rib_h + 0.5 mm")
    rect(sk, g + wb - 0.4, mya - 1, g + wb + 1.1, mya + 1, "wall_gap + cl_wb + rib_h - notch_d", "%s - notch_w / 2" % ya,
         "wall_gap + cl_wb + rib_h + 0.5 mm", "%s + notch_w / 2" % ya)
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.CutFeatureOperation, "cl_d + 2 mm", body, "CUT - CRIMP NOTCHES")

    mat = material(comp)
    health(design)
    print("  dimensions Fusion already implied (skipped): %d" % len(SKIPPED))
    del SKIPPED[:]
    want = (g - r, g - r, -d / 2, g + wb + La, g + wa + Lb, d / 2)
    body = check_body(comp, want, c.mass(), "CLEAT %s" % pn)
    print("CLEAT %s: material %s, Fusion mass %.2f g" % (pn, mat, body.physicalProperties.mass * 1000))
    save_export(app, doc, design, f, name,
                "%s %s, rev P01, PROPOSED (joints register J-FRAME-01). Built by joints_cleats_build.py" % (pn, title),
                name.replace("_CAD", "_STEP") + ".step")
    edit_test(design, lambda: box(comp.bRepBodies.item(0)), [("cl_La", "%g mm" % (La + 4))],
              lambda b0, a: abs((a[3] - b0[3]) - 4.0) < 0.01)


# ------------------------------------------------------------------ the T plug
def build_plug(app):
    doc, design, f = new_design(app, PLUG[1])
    try:
        _plug(app, doc, design, f)
    finally:                               # every run closes what it opened, saved or not
        if doc.isValid:
            doc.close(False)


def _plug(app, doc, design, f):
    pn, name, title, title_vi = PLUG
    k0 = calc()
    add_params(design, COMMON + [
        ("plug_w", "%g mm" % k0.W_NARROW, "CALCULATION: across the stud's bore (17.6, or 18.0 in the 1.0 studs) less 2 x the 1.0 glue line (cleat_check.py)"),
        ("plug_ls", "%g mm" % k0.PLUG.Ls, "PROPOSED: the box's length in the stud (cleat_check.py)"),
        ("plug_tw", "%g mm" % k0.PLUG.tw, "PROPOSED: tongue thickness along the rail; the rail's slot is plug_tw + 2 x 1.0 (FR-25)"),
        ("plug_tl", "%g mm" % k0.PLUG.tl, "CALCULATION: tongue length: the rail's 1.2 wall plus 4.8 into its bore"),
        ("plug_d", "%g mm" % k0.PLUG.d, "PROPOSED: depth across the frame; the rail's slot is plug_d + 2 x 1.0 (FR-25)"),
        ("plug_web", "1 mm", "ASSUMPTION: the middle web, on the tongue's line"),
    ])
    root = design.rootComponent
    root.partNumber = pn
    root.description = "%s | %s | rev %s | %s; origin at the stud's end, centre line, mid-depth" % (title, title_vi, REV, NOTE)
    comp = root
    k = calc()
    w, Ls, tw, tl, d = k.W_NARROW, k.PLUG.Ls, k.PLUG.tw, k.PLUG.tl, k.PLUG.d
    print("T PLUG %s: box %.1f x %g, tongue %g x %g, %g deep (cleat_check.py)" % (pn, w, Ls, tw, tl, d))

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - BOX AND TONGUE"
    yaxis = adsk.fusion.SketchLine.cast(sk.project(comp.yConstructionAxis).item(0))
    if yaxis is None:
        raise RuntimeError("the projected Y axis isn't a sketch line")
    yaxis.isConstruction = True
    pts = [(0, -w / 2), (Ls, -w / 2), (Ls, w / 2), (0, w / 2), (0, tw / 2), (-tl, tw / 2), (-tl, -tw / 2), (0, -tw / 2)]
    exprs = [(None, "plug_w / 2"), ("plug_ls", "plug_w / 2"), ("plug_ls", "plug_w / 2"), (None, "plug_w / 2"),
             (None, "plug_tw / 2"), ("plug_tl", "plug_tw / 2"), ("plug_tl", "plug_tw / 2"), (None, "plug_tw / 2")]
    polygon(sk, pts, exprs, yaxis)
    must_constrain(sk)
    ext = extrude(comp, sk, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, "plug_d", name="EXTRUDE - BOX AND TONGUE")
    body = ext.bodies.item(0)
    body.name = "FRAME T PLUG"

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - CHAMBERS"
    rect(sk, 1.0, -w / 2 + 1.0, Ls - 1.0, -0.5, "cl_t", "plug_w / 2 - cl_t", "plug_ls - cl_t", "plug_web / 2")
    rect(sk, 1.0, 0.5, Ls - 1.0, w / 2 - 1.0, "cl_t", "plug_web / 2", "plug_ls - cl_t", "plug_w / 2 - cl_t")
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.CutFeatureOperation, "plug_d + 2 mm", body, "CUT - CHAMBERS")

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - SPACER RIBS"
    r = 0.6
    for x0e, x0 in (("rib_in", 0.5), ("plug_ls - rib_in - rib_w", Ls - 1.5)):
        rect(sk, x0, w / 2, x0 + 1.0, w / 2 + r, x0e, "plug_w / 2", "%s + rib_w" % x0e, "plug_w / 2 + rib_h")
        rect(sk, x0, -w / 2 - r, x0 + 1.0, -w / 2, x0e, "plug_w / 2 + rib_h", "%s + rib_w" % x0e, "plug_w / 2")
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.JoinFeatureOperation, "plug_d", body, "EXTRUDE - SPACER RIBS")

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - CRIMP BOSSES"
    rect(sk, 7, w / 2, 13, w / 2 + r, "plug_ls / 2 - notch_l / 2", "plug_w / 2", "plug_ls / 2 + notch_l / 2", "plug_w / 2 + rib_h")
    rect(sk, 7, -w / 2 - r, 13, -w / 2, "plug_ls / 2 - notch_l / 2", "plug_w / 2 + rib_h", "plug_ls / 2 + notch_l / 2", "plug_w / 2")
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.JoinFeatureOperation, "plug_d", body, "EXTRUDE - CRIMP BOSSES")
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - CRIMP NOTCHES"
    rect(sk, 9, w / 2 - 0.4, 11, w / 2 + 1.1, "plug_ls / 2 - notch_w / 2", "plug_w / 2 + rib_h - notch_d",
         "plug_ls / 2 + notch_w / 2", "plug_w / 2 + rib_h + 0.5 mm")
    rect(sk, 9, -w / 2 - 1.1, 11, -w / 2 + 0.4, "plug_ls / 2 - notch_w / 2", "plug_w / 2 + rib_h + 0.5 mm",
         "plug_ls / 2 + notch_w / 2", "plug_w / 2 + rib_h - notch_d")
    must_constrain(sk)
    extrude(comp, sk, adsk.fusion.FeatureOperations.CutFeatureOperation, "plug_d + 2 mm", body, "CUT - CRIMP NOTCHES")

    mat = material(comp)
    health(design)
    print("  dimensions Fusion already implied (skipped): %d" % len(SKIPPED))
    del SKIPPED[:]
    want = (-tl, -w / 2 - r, -d / 2, Ls, w / 2 + r, d / 2)
    body = check_body(comp, want, k.PLUG.mass(), "T PLUG %s" % pn)
    print("T PLUG %s: material %s, Fusion mass %.2f g" % (pn, mat, body.physicalProperties.mass * 1000))
    save_export(app, doc, design, f, name,
                "%s %s, rev P01, PROPOSED (joints register J-FRAME-01). Built by joints_cleats_build.py" % (pn, title),
                name.replace("_CAD", "_STEP") + ".step")
    edit_test(design, lambda: box(comp.bRepBodies.item(0)), [("plug_ls", "%g mm" % (Ls + 4))],
              lambda b0, a: abs((a[3] - b0[3]) - 4.0) < 0.01)


def run(_context):
    app = adsk.core.Application.get()
    for dd in (CAD_DIR, MFG_DIR):
        os.makedirs(os.path.join(REPO, dd), exist_ok=True)
    which = [w.strip() for w in ARGS.get("only", "831003,831006").split(",") if w.strip()]
    for pn in which:
        if pn == PLUG[0]:
            build_plug(app)
        elif pn in CORNERS:
            build_corner(app, pn)
        else:
            raise RuntimeError("unknown part %s" % pn)
    print("done: %s" % ", ".join(which))
