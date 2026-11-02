"""Build the joints register's made hardware as native Fusion designs, in one run.

Revision P01 (PROPOSED). Run through the Fusion lock (tools/fusion/README.md):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_hardware_build.py
    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_hardware_build.py --arg only=keys
    python3 tools/fusion/run_script.py v2/01-CAD-Native/joints/joints_hardware_build.py --arg only=plates

It makes three parametric mm designs in "Default Project/FocusPod v2/joints" (a
folder of its own, so a new design can never take the name of another team's
design), each with named user parameters (status and source in the comment),
the skeleton P04 parameters it uses (read at run time from the skeleton's
parameter CSV under their own names, the team's way to build on the skeleton),
one component, sketches constrained to the parameters, and features named by
function:

    111211_P01_BASE-CORNER-KEY-TABULATED_CAD   corner key family, joints register J-BASE-02:
        cut_angle 0 (111211), -24.1446 (111212 LH), +24.02 (111213 RH), -7.2546 (111214), 0 (111215):
        the mitres exactly, as corner_keys.py computes them (BASE, 2026-11-01)
        saved and drawn at 0 (111211); one STEP per part number
    831001_P01_HARDWARE-LOCATING-SPIGOT_CAD    spigot family, register H-05 and H-45: pin_proud 8 (831001) or 11
                                               (831010, DR's DT ledge, J-FRONT-03); saved at 831001; one STEP per
                                               part number; a TABULATED sheet
    831002_P01_HARDWARE-STOP-WASHER_CAD        stop washer, register H-08, plus its DXF
                                               (D-89 part 4: flat, cut from sheet, no drawing)
    831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD   mitre plate family, register H-40 to H-42 (J-FRAME-01, D-131):
        831007 (two 20 x 40 at 45 deg), 831008 (a 20 x 40 meeting a 40 x 40), 831009 (two 40 x 40 at 45 deg);
        each a rectangular blank on the mitre line, short of the frame's outer corner so its square ends sit 0.5
        inside the frame's faces (the Lead's steer 2026-11-01; PLATE_BLANKS); saved at 831007; one STEP and one
        DXF per part number (flat, cut from sheet, no drawing)

Each design is saved, exported (.f3d to v2/01-CAD-Native/joints/, STEP and DXF to
v2/03-Manufacturing/joints/), edit-tested (guideline 4.4: change a driving
parameter, rebuild, measure, revert, measure) and closed without keeping the test.
An error raises, so Fusion rolls the run back; a design already saved stays, and
--arg only=... reruns the rest. Before making each design it runs the shared safe-to-create
check (tools/fusion/fusion_folder.py): a name already there, or an unreadable entry that could
be the new file, stops it.

Sign of cut_angle: in the key's frame (x along the carrier toward the joint, z up,
y = z cross x) a positive angle makes the key longer on its +y side; the long side
is always on the outside of the turn (v2/01-CAD-Native/joints/corner_keys.py).
"""
import csv
import glob
import math
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

KEYS = "111211_P01_BASE-CORNER-KEY-TABULATED_CAD"
SPIGOT = "831001_P01_HARDWARE-LOCATING-SPIGOT_CAD"
SPIGOT_VARIANTS = [  # part number, name, how far the pin's top stands above the face it sits on, STEP file
    ("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "8 mm", "831001_P01_HARDWARE-LOCATING-SPIGOT_STEP.step"),
    # the Lead's ruling 2026-11-01 (J-FRONT-03): DT's two ledge spigots stand 11 proud, so they engage DT's holes
    # 5 as before
    ("831010", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - 11 PROUD - STAINLESS", "11 mm",
     "831010_P01_HARDWARE-LOCATING-SPIGOT-11-PROUD_STEP.step"),
]
WASHER = "831002_P01_HARDWARE-STOP-WASHER_CAD"
PLATES = "831007_P01_HARDWARE-MITRE-PLATE-TABULATED_CAD"
PLATE_VARIANTS = [  # part number, name, the two members' widths in the frame's plane, file stem (register H-40 to H-42)
    ("831007", "HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL", "20 mm", "20 mm",
     "831007_P01_HARDWARE-MITRE-PLATE-20X40-45DEG"),
    ("831008", "HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL", "20 mm", "40 mm",
     "831008_P01_HARDWARE-MITRE-PLATE-20X40-TO-40X40"),
    ("831009", "HARDWARE - MITRE PLATE - 40 X 40 - 45 DEG - 2.0 STEEL", "40 mm", "40 mm",
     "831009_P01_HARDWARE-MITRE-PLATE-40X40-45DEG"),
]
KEY_VARIANTS = [  # part number, STEP file, cut angle (signed, see the docstring), fix_y, fix_step (D-144)
    ("111211", "111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step", "0 deg", "6 mm", "7.3 mm"),
    ("111212", "111212_P01_BASE-CORNER-KEY-FRONT-LH_STEP.step", "-24.1446 deg", "7 mm", "0 mm"),
    ("111213", "111213_P01_BASE-CORNER-KEY-FRONT-RH_STEP.step", "24.02 deg", "7 mm", "0 mm"),
    ("111214", "111214_P01_BASE-CORNER-KEY-KNEE-LH_STEP.step", "-7.2546 deg", "7 mm", "0 mm"),
    ("111215", "111215_P01_BASE-CORNER-KEY-SQUARE-INLINE_STEP.step", "0 deg", "7 mm", "0 mm"),
]
DRAWN = "0 deg"        # saved state: 111211 (square, true circles in every view), drawn on the tabulated sheet
CM = 0.1               # the API's lengths are cm


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


def skeleton_rows():
    """{name: (expression, unit, status, source)} from the highest skeleton parameter CSV, and its revision."""
    found = glob.glob(os.path.join(REPO, "v2/01-CAD-Native/skeleton/100000_P[0-9][0-9]_POD-SKELETON-PARAMETERS.csv"))
    if not found:
        raise RuntimeError("no skeleton parameter CSV")
    path = max(found, key=lambda f: os.path.basename(f)[7:10])
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            expr = (r.get("expression") or "").strip()
            if "unit" in r:
                unit = (r.get("unit") or "").strip()
            else:
                unit = "mm" if expr.endswith("mm") else ("deg" if expr.endswith("deg") else "")
            out[r["parameter"].strip()] = (expr, unit, (r.get("status") or "").strip(), (r.get("source") or "").strip())
    return out, os.path.basename(path)[7:10]


def add_skeleton(design, names):
    rows, rev = skeleton_rows()
    for n in names:
        if n not in rows:
            raise RuntimeError("skeleton has no parameter " + n)
        expr, unit, status, src = rows[n]
        try:                                   # a plain quantity: keep the skeleton's own expression
            float(expr.replace("mm", "").replace("deg", "").strip())
        except ValueError:
            raise RuntimeError("skeleton %s is an expression (%s): add what it depends on" % (n, expr))
        if design.userParameters.add(n, vi(expr), unit, "SKELETON %s %s: %s" % (rev, status.upper(), src)[:250]) is None:
            raise RuntimeError("could not add skeleton parameter " + n)
    return rev


def add_params(design, params):
    for name, expr, unit, comment in params:
        if design.userParameters.add(name, vi(expr), unit, comment) is None:
            raise RuntimeError("could not add parameter " + name)


def folder(app):
    """FocusPod v2/joints, made if missing."""
    proj = next((p for p in app.data.dataProjects if p.name == PROJECT), None)
    if proj is None:
        raise RuntimeError("no %r in the active hub" % PROJECT)
    parent = proj.rootFolder.dataFolders.itemByName(PARENT)
    if parent is None:
        raise RuntimeError("no %r folder" % PARENT)
    return parent.dataFolders.itemByName(FOLDER) or parent.dataFolders.add(FOLDER)


def _safe_to_create():
    """The shared check, always loaded from this checkout by full path and printed: Fusion keeps
    modules loaded between runs, so an import by name could pick up another team's copy."""
    import importlib.util
    path = os.path.join(REPO, "tools/fusion/fusion_folder.py")
    spec = importlib.util.spec_from_file_location("joints_fusion_folder", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  safe-to-create check from %s" % mod.__file__)
    if os.path.abspath(mod.__file__) != os.path.abspath(path):
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


def set_root(design, pn, name, name_vi, note):
    root = design.rootComponent
    root.partNumber = pn
    root.description = "%s | %s | rev %s | %s" % (name, name_vi, REV, note)
    return root


def material(comp, names, words):
    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
    if lib is None:
        print("  WARNING: no Fusion Material Library; material not set")
        return None
    pick = None
    for n in names:
        pick = lib.materials.itemByName(n)
        if pick:
            break
    if pick is None:
        for i in range(lib.materials.count):
            m = lib.materials.item(i)
            if all(w.lower() in m.name.lower() for w in words):
                pick = m
                break
    if pick is None:
        print("  WARNING: no material like %s; material not set" % names)
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


def cyl_faces(body, dia_mm):
    return [f for f in body.faces if isinstance(f.geometry, adsk.core.Cylinder)
            and abs(f.geometry.radius * 20.0 - dia_mm) < 0.01]


def cosmetic_thread(comp, faces, internal, size, cls, length=None, label=""):
    """M-thread callout on cylindrical faces (not modelled); optional, so a refusal only warns."""
    tf = comp.features.threadFeatures
    n = 0
    for f in faces:
        try:
            faces_in = adsk.core.ObjectCollection.create()
            faces_in.add(f)
            ti = tf.createInput(faces_in, tf.createThreadInfo(internal, "ISO Metric profile", size, cls))
            ti.isModeled = False
            if length:
                ti.isFullLength = False
                ti.threadLength = vi(length)
            else:
                ti.isFullLength = True
            t = tf.add(ti)
            n += 1
            t.name = "THREAD - %s %s %d" % (size, label, n)
        except Exception as ex:
            print("  WARNING: cosmetic thread %s on %s not added: %s" % (size, label, ex))
            return n
    return n


def cut(comp, body, profiles, extent, name):
    """Extrude-cut the profiles into body, trying both directions; raise if nothing is removed."""
    if not profiles:
        raise RuntimeError("cut %s: no profiles" % name)
    coll = adsk.core.ObjectCollection.create()
    for p in profiles:
        coll.add(p)
    v0 = body.volume
    for direction in (adsk.fusion.ExtentDirections.PositiveExtentDirection,
                      adsk.fusion.ExtentDirections.NegativeExtentDirection):
        ei = comp.features.extrudeFeatures.createInput(coll, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ei.setOneSideExtent(extent(), direction)
        ei.participantBodies = [body]
        try:
            feat = comp.features.extrudeFeatures.add(ei)
        except Exception as ex:
            print("  (cut %s one way failed: %s)" % (name, ex))
            continue
        if body.volume < v0 - 1e-6:
            feat.name = name
            return feat
        feat.deleteMe()
    raise RuntimeError("cut %s removed nothing either way" % name)


def small_profiles(sk, max_cm2=0.6):
    return [sk.profiles.item(i) for i in range(sk.profiles.count)
            if sk.profiles.item(i).areaProperties().area < max_cm2]


def save_export(app, doc, design, f, name, desc, steps):
    """Save to the cloud folder, export the .f3d, then each STEP (with its state change first)."""
    if not doc.saveAs(name, f, desc, ""):
        raise RuntimeError("saveAs failed for " + name)
    em = design.exportManager
    f3d = os.path.join(REPO, CAD_DIR, name + ".f3d")
    if not em.execute(em.createFusionArchiveExportOptions(f3d, design.rootComponent)):
        raise RuntimeError("f3d export failed for " + name)
    print("  saved to %s/%s and exported %s" % (PARENT, FOLDER, os.path.relpath(f3d, REPO)))
    for step_name, before in steps:
        if before:
            before()
        path = os.path.join(REPO, MFG_DIR, step_name)
        for attempt in range(10):
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


# ------------------------------------------------------------------ corner keys 111211 to 111214
def face_where(body, test):
    """The planar face whose outward normal passes test(normal)."""
    for fc in body.faces:
        if isinstance(fc.geometry, adsk.core.Plane):
            ok, n = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
            if ok and test(n):
                return fc
    raise RuntimeError("face not found")


def line_edge(face, test):
    """The straight edge of face whose two ends both pass test((x, y, z) in mm)."""
    for i in range(face.edges.count):
        e = face.edges.item(i)
        if not isinstance(e.geometry, adsk.core.Line3D):
            continue
        a, b = e.startVertex.geometry, e.endVertex.geometry
        if test((a.x * 10, a.y * 10, a.z * 10)) and test((b.x * 10, b.y * 10, b.z * 10)):
            return e
    raise RuntimeError("edge not found on the face")


def hole(comp, body, face, at_mm, edge1, off1, edge2, off2, depth, name):
    """A Ø tap_d hole in face at at_mm, placed by offsets (expressions) from two of the face's
    edges; depth an expression, or None for through. Tries the other direction if nothing is cut."""
    v0 = body.volume
    for flip in (False, True):
        hi = comp.features.holeFeatures.createSimpleInput(vi("tap_d"))
        hi.setPositionByPlaneAndOffsets(face, p3(*at_mm), edge1, vi(off1), edge2, vi(off2))
        if depth is None:
            hi.setAllExtent(adsk.fusion.ExtentDirections.NegativeExtentDirection if flip
                            else adsk.fusion.ExtentDirections.PositiveExtentDirection)
        else:
            hi.setDistanceExtent(vi(depth))
            hi.isDefaultDirection = not flip
        hi.participantBodies = [body]
        try:
            h = comp.features.holeFeatures.add(hi)
        except Exception as ex:
            print("  (%s one way failed: %s)" % (name, ex))
            continue
        if body.volume < v0 - 1e-6:
            h.name = name
            return h
        h.deleteMe()
    raise RuntimeError("%s cut nothing either way" % name)


def stud_face(body):
    """The planar face whose outward normal points most along +X: the stud face (the cut is under 45 deg)."""
    best, bx = None, -2.0
    for fc in body.faces:
        if not isinstance(fc.geometry, adsk.core.Plane):
            continue
        ok, n = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
        if ok and n.x > bx:
            best, bx = fc, n.x
    if best is None or bx < 0.7:
        raise RuntimeError("stud face not found")
    return best


def build_keys(app):
    doc, design, f = new_design(app, KEYS)
    rev = add_skeleton(design, ["band_t", "band_h", "glide_h"])
    add_params(design, [
        ("band_wall", "1.5 mm", "mm", "DECIDED: base band wall 1.5 (D-86)"),
        ("key_clear", "1 mm", "mm", "ASSUMPTION: clearance each side in the band's bore"),
        ("key_w", "band_t - 2 * band_wall - 2 * key_clear", "mm",
         "CALCULATION: across the band, 40 - 3 - 2 = 35 (skeleton band_t)"),
        ("key_h", "75 mm", "mm", "PROPOSED: height, in the band's 97 bore (joints register J-BASE-02)"),
        ("key_len", "30 mm", "mm", "PROPOSED: length along the carrier on the centre line; 30 keeps the carrier's Ø7.0 fixing holes 2 x 7 from its cut end (J-BASE-02)"),
        ("cut_angle", DRAWN, "deg",
         "SOURCE: stud face cut from square, signed: 0 (111211), -24.1446 (111212), +24.02 (111213), -7.2546 (111214), "
         "0 (111215); "
         "BASE's front geometry (corner-keys.csv)"),
        ("fix_x", "10.5 mm", "mm", "PROPOSED: fixing holes from the key's back face, over 2 x the hole (C09) (FR-16)"),
        ("fix_y", "6 mm", "mm", "PROPOSED: fixing holes either side of the centre line: 6 on 111211 (D-144), 7 on the others (C09) (FR-16)"),
        ("fix_step", "7.3 mm", "mm", "PROPOSED (D-144): the -y fixing hole's step along x from fix_x; 7.3 on 111211 (the back corners), 0 on the others"),
        ("stud_z1", "26 mm", "mm", "PROPOSED: lower hook stud above the key's bottom; Z 37.5 in the pod (FR-15)"),
        ("stud_z2", "60 mm", "mm", "PROPOSED: upper hook stud above the key's bottom; Z 71.5 in the pod (FR-15)"),
        ("tap_d", "5 mm", "mm", "SOURCE: M6 x 1 tap drill 5.0 (ISO 2306, unverified)"),
        ("fix_drill", "18 mm", "mm", "CALCULATION: fixing hole drill depth, thread 15 + 3 for the drill point"),
        ("fix_thread", "15 mm", "mm", "DECIDED: at least 15 of thread (PM ruling on F-017); an 838010 M6 x 12 button head through the 1.5 wall engages 10.5"),
    ])
    root = set_root(design, "111211", "BASE - CORNER KEY - TABULATED 111211, 111212, 111213, 111214, 111215",
                    "Ke góc đế (bảng 111211 đến 111215)",
                    "UNITS MM; MATERIAL EN AW-6061-T6; FINISH MILL FINISH, DEBURRED; ISO 2768-m; CUT 111211 0 DEG (SHOWN), "
                    "111212 -24.1446 DEG, 111213 +24.02 DEG, 111214 -7.2546 DEG, 111215 0 DEG; FIXING HOLES 111211 AT "
                    "(10.5, +6) AND (17.8, -6), THE OTHERS AT (10.5, +-7) (D-144); joints register J-BASE-02; PROPOSED")
    comp = root
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - KEY PLAN"
    lines, gc, dims = sk.sketchCurves.sketchLines, sk.geometricConstraints, sk.sketchDimensions
    w, L, t = 17.5, 30.0, math.tan(math.radians(float(DRAWN.split()[0])))
    lab = lines.addByTwoPoints(p3(0, -w), p3(0, w))
    lbc = lines.addByTwoPoints(lab.endSketchPoint, p3(L + w * t, w))
    lcd = lines.addByTwoPoints(lbc.endSketchPoint, p3(L - w * t, -w))
    lda = lines.addByTwoPoints(lcd.endSketchPoint, lab.startSketchPoint)
    gc.addVertical(lab)
    gc.addHorizontal(lbc)
    gc.addHorizontal(lda)
    gc.addMidPoint(sk.originPoint, lab)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    A = adsk.fusion.DimensionOrientations.AlignedDimensionOrientation
    dims.addDistanceDimension(lab.startSketchPoint, lab.endSketchPoint, V, p3(-8, 0)).parameter.expression = "key_w"
    dims.addDistanceDimension(lbc.startSketchPoint, lbc.endSketchPoint, H, p3(8, w + 8)).parameter.expression = \
        "key_len + key_w / 2 * tan(cut_angle)"
    dims.addDistanceDimension(lda.endSketchPoint, lda.startSketchPoint, H, p3(8, -w - 8)).parameter.expression = \
        "key_len - key_w / 2 * tan(cut_angle)"
    cl = lines.addByTwoPoints(p3(0, 0), p3(L, 0))      # the key's centre line, to the stud face's centre
    cl.isConstruction = True
    gc.addCoincident(cl.startSketchPoint, sk.originPoint)
    gc.addHorizontal(cl)
    dims.addDistanceDimension(cl.startSketchPoint, cl.endSketchPoint, H, p3(L / 2, 4)).parameter.expression = "key_len"
    must_constrain(sk)
    prof = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
    ext = comp.features.extrudeFeatures.addSimple(prof, vi("key_h"), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.name = "EXTRUDE - KEY BLOCK"
    body = ext.bodies.item(0)
    body.name = "CORNER KEY"

    # fixing holes from the bottom (2 x M6, drill 18, thread 15) and hook stud holes in the stud
    # face (2 x M6 through, square to it): hole features placed by offsets from the block's own
    # edges, so they follow every parameter (cut_angle included) with no hole sketch
    for name, side in (("FIXING HOLE +Y", 1), ("FIXING HOLE -Y", -1)):
        bottom = face_where(body, lambda n: n.z < -0.99)
        back = line_edge(bottom, lambda q: abs(q[0]) < 0.01)
        edge_y = line_edge(bottom, lambda q: abs(q[1] - side * 17.5) < 0.01)
        hole(comp, body, bottom, (10.5 + (7.3 if side < 0 else 0.0), side * 6.0, 0), back,
             "fix_x" if side > 0 else "fix_x + fix_step", edge_y, "key_w / 2 - fix_y", "fix_drill",
             "HOLE - %s M6 (DRILL 5.0 X 18)" % name)
    for name, zp, z in (("HOOK STUD LOW", "stud_z1", 26.0), ("HOOK STUD HIGH", "stud_z2", 60.0)):
        face = stud_face(body)
        foot = line_edge(face, lambda q: abs(q[2]) < 0.01)
        d_side = line_edge(face, lambda q: abs(q[1] + 17.5) < 0.01)
        hole(comp, body, face, (L, 0, z), foot, zp, d_side, "key_w / 2 / cos(cut_angle)", None,
             "HOLE - %s M6 (DRILL 5.0 THROUGH)" % name)
    holes = cyl_faces(body, 5.0)
    if len(holes) != 4:
        raise RuntimeError("expected 4 tap-drill faces, found %d" % len(holes))
    fix = [h for h in holes if abs(h.geometry.axis.z) > 0.9]
    stud = [h for h in holes if abs(h.geometry.axis.z) < 0.1]
    cosmetic_thread(comp, fix, True, "M6x1", "6H", "fix_thread", "FIXING")
    cosmetic_thread(comp, stud, True, "M6x1", "6H", None, "HOOK STUD")
    mat = material(comp, ["Aluminum 6061", "Aluminum 6061-T6"], ["6061"]) or \
        material(comp, ["Aluminum"], ["aluminum"])
    health(design)
    print("KEYS (skeleton %s): drawn 111211 %s, material %s, mass %.4f kg" % (
        rev, fmt(box(body)), mat, body.physicalProperties.mass))

    names = {"111211": "BASE - CORNER KEY - SQUARE - COMMON", "111212": "BASE - CORNER KEY - FRONT - LH",
             "111213": "BASE - CORNER KEY - FRONT - RH", "111214": "BASE - CORNER KEY - KNEE - LH",
             "111215": "BASE - CORNER KEY - SQUARE - INLINE"}
    holes_of = {pn: (fy, fs) for pn, _step, _ang, fy, fs in KEY_VARIANTS}
    family = (root.partNumber, root.description)

    def state(expr, pn):
        def go():
            design.userParameters.itemByName("cut_angle").expression = expr
            num = pn.split()[0]
            if num in holes_of:         # D-144: each number's fixing holes
                design.userParameters.itemByName("fix_y").expression = holes_of[num][0]
                design.userParameters.itemByName("fix_step").expression = holes_of[num][1]
            if num in names:            # each STEP carries its own part number (C06)
                root.partNumber = num
                root.description = "%s | rev %s | cut %s | joints register J-BASE-02 | PROPOSED" % (names[num], REV, expr)
            adsk.doEvents()
            health(design)
            b = comp.bRepBodies.item(0)
            print("    %s cut %s: %s, %.4f kg, %d faces" % (pn, expr, fmt(box(b)), b.physicalProperties.mass,
                                                        b.faces.count))
        return go

    save_export(app, doc, design, f, KEYS,
                "Corner key family 111211-111215, rev P01, PROPOSED (joints register J-BASE-02, D-144); saved at "
                "cut_angle 0 (111211). Built by joints_hardware_build.py",
                [(step, state(ang, pn)) for pn, step, ang, _fy, _fs in KEY_VARIANTS])
    state(DRAWN, "111211 (back to the drawn state)")()
    root.partNumber, root.description = family
    edit_test(design, lambda: box(comp.bRepBodies.item(0)), [("key_h", "80 mm")],
              lambda b, a: abs((a[5] - a[2]) - 80.0) < 0.01)
    doc.close(False)


# ------------------------------------------------------------------ spigot 831001
def hex_socket(comp, body, sketch_face, depth_param):
    """A 4 mm hex socket in the pin's top face, its sketch constrained to a construction circle on the axis."""
    sk = comp.sketches.add(sketch_face)
    sk.name = "SKETCH - HEX SOCKET"
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, sketch_face.pointOnFace.z))
    r = (4.0 / math.sqrt(3.0)) * CM            # corner radius for 4 across flats
    pts = [adsk.core.Point3D.create(o.x + r * math.cos(math.radians(60 * k)),
                                    o.y + r * math.sin(math.radians(60 * k)), 0) for k in range(6)]
    ls = sk.sketchCurves.sketchLines
    edges = [ls.addByTwoPoints(pts[0], pts[1])]
    for k in range(2, 6):
        edges.append(ls.addByTwoPoints(edges[-1].endSketchPoint, pts[k]))
    edges.append(ls.addByTwoPoints(edges[-1].endSketchPoint, edges[0].startSketchPoint))
    try:
        axis = sk.project(comp.zConstructionAxis).item(0)
        circ = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(o.x, o.y, 0), r)
        circ.isConstruction = True
        g, d = sk.geometricConstraints, sk.sketchDimensions
        g.addCoincident(circ.centerSketchPoint, axis)
        d.addDiameterDimension(circ, adsk.core.Point3D.create(o.x + 0.5, o.y + 0.5, 0)).parameter.expression = \
            "hex_af / cos(30 deg)"
        for e in edges:
            g.addCoincident(e.startSketchPoint, circ)
        for e in edges[1:]:
            g.addEqual(edges[0], e)
        g.addHorizontal(edges[1])         # 60 to 120 deg: the top flat
    except Exception as ex:
        print("  WARNING: hex socket constraints incomplete: %s" % ex)
    print("  hex socket sketch fully constrained: %s" % sk.isFullyConstrained)
    one_loop = [sk.profiles.item(i) for i in range(sk.profiles.count) if sk.profiles.item(i).profileLoops.count == 1]
    prof = min(one_loop, key=lambda p: p.areaProperties().area)
    cut(comp, body, [prof], lambda: adsk.fusion.DistanceExtentDefinition.create(vi(depth_param)), "CUT - HEX SOCKET 4")


def build_spigot(app):
    doc, design, f = new_design(app, SPIGOT)
    add_params(design, [
        ("pin_d", "8 mm", "mm", "PROPOSED: pin diameter, h9 (joints register H-05); Ø8.5 hole or 8.5 slot in the mating part"),
        ("pin_proud", "8 mm", "mm", "PROPOSED: the pin's top stands this far above the joint face: 8 (831001, "
         "H-05) or 11 (831010, H-45: DR's DT ledge, J-FRONT-03)"),
        ("rivnut_head", "0.76 mm", "mm", "SOURCE: Sherex CAH3-610-4.2 head 0.76 +-0.08 (joints register SHX)"),
        ("pin_len", "pin_proud - rivnut_head", "mm", "CALCULATION: the pin sits on its rivnut's head, so 7.24 long"),
        ("thread_d", "6 mm", "mm", "SOURCE: M6 x 1 into the rivnut 838003 (H-03)"),
        ("thread_len", "8 mm", "mm", "ASSUMPTION: inside the rivnut's 10.16 installed length (SHX); as BASE's copies"),
        ("tip_ch", "1 mm", "mm", "ASSUMPTION: lead-in chamfer on the pin's top, as BASE's copies"),
        ("hex_af", "4 mm", "mm", "ASSUMPTION: hex socket across flats, to set it with threadlocker at the factory"),
        ("hex_depth", "3.5 mm", "mm", "ASSUMPTION: hex socket depth"),
    ])
    root = set_root(design, "831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8",
                    "UNITS MM; MATERIAL STAINLESS A2 (1.4301 OR 1.4305); FINISH PASSIVATED, DEBURRED; ISO 2768-m; "
                    "PIN Ø8 h9; joints register H-05; PROPOSED; origin on the face it sits on (its rivnut's head)")
    comp = root
    xy = comp.xYConstructionPlane
    sk = comp.sketches.add(xy)
    sk.name = "SKETCH - PIN AND STUD"
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(p3(0, 0), 0.4)
    c2 = sk.sketchCurves.sketchCircles.addByCenterRadius(p3(0, 0), 0.3)
    sk.geometricConstraints.addCoincident(c.centerSketchPoint, sk.originPoint)
    sk.geometricConstraints.addCoincident(c2.centerSketchPoint, sk.originPoint)
    sk.sketchDimensions.addDiameterDimension(c, p3(6, 6)).parameter.expression = "pin_d"
    sk.sketchDimensions.addDiameterDimension(c2, p3(4, -6)).parameter.expression = "thread_d"
    must_constrain(sk)
    profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
    disc = next(pr for pr in profs if pr.profileLoops.count == 1)
    both = adsk.core.ObjectCollection.create()
    for pr in profs:
        both.add(pr)
    ext = comp.features.extrudeFeatures.addSimple(both, vi("pin_len"), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.name = "EXTRUDE - PIN D8"
    body = ext.bodies.item(0)
    body.name = "LOCATING SPIGOT"
    ei = comp.features.extrudeFeatures.createInput(disc, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("thread_len")),
                        adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ei.participantBodies = [body]
    e2 = comp.features.extrudeFeatures.add(ei)
    e2.name = "EXTRUDE - M6 STUD"
    if comp.bRepBodies.count != 1:
        raise RuntimeError("the pin came out as %d bodies" % comp.bRepBodies.count)
    body = comp.bRepBodies.item(0)
    b = box(body)
    if abs(b[2] + 8.0) > 0.01:
        raise RuntimeError("stud went the wrong way: %s" % fmt(b))
    top = max((fc for fc in body.faces if isinstance(fc.geometry, adsk.core.Plane)), key=lambda fc: fc.pointOnFace.z)
    edges = adsk.core.ObjectCollection.create()
    for e in top.edges:
        edges.add(e)
    chi = comp.features.chamferFeatures.createInput2()
    chi.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, vi("tip_ch"), False)
    comp.features.chamferFeatures.add(chi).name = "CHAMFER - PIN LEAD-IN"
    top = max((fc for fc in body.faces if isinstance(fc.geometry, adsk.core.Plane)), key=lambda fc: fc.pointOnFace.z)
    try:
        hex_socket(comp, body, top, "hex_depth")
    except Exception as ex:
        print("  WARNING: no hex socket: %s" % ex)
    cosmetic_thread(comp, cyl_faces(body, 6.0), False, "M6x1", "6g", None, "STUD")
    mat = material(comp, ["Stainless Steel", "Stainless Steel 304", "Steel, Stainless"], ["stainless"]) or \
        material(comp, ["Steel"], ["steel"])
    health(design)
    print("SPIGOT 831001: %s, material %s, mass %.5f kg" % (fmt(box(body)), mat, body.physicalProperties.mass))
    family = (root.partNumber, root.description)

    def spigot_state(variant):
        def go():
            num, name, proud, _step = variant
            design.userParameters.itemByName("pin_proud").expression = proud
            root.partNumber = num            # each STEP carries its own part number (C06)
            root.description = "%s | rev %s | pin %s proud | joints register H-05, H-45 | PROPOSED" % (name, REV, proud)
            adsk.doEvents()
            health(design)
            print("  %s: %s" % (num, fmt(box(comp.bRepBodies.item(0)))))
        return go

    save_export(app, doc, design, f, SPIGOT,
                "Locating spigot family 831001 (8 proud) and 831010 (11 proud), rev P01, PROPOSED (joints register "
                "H-05, H-45). Built by joints_hardware_build.py",
                [(v[3], spigot_state(v)) for v in SPIGOT_VARIANTS])
    spigot_state(SPIGOT_VARIANTS[0])()        # back to the saved state, 831001
    root.partNumber, root.description = family
    edit_test(design, lambda: box(comp.bRepBodies.item(0)), [("pin_proud", "10 mm")],
              lambda bb, a: abs((a[5] - bb[5]) - 2.0) < 0.01)
    doc.close(False)


# ------------------------------------------------------------------ stop washer 831002
def write_dxf(path, circles):
    """ASCII DXF (R12), mm, the outline and holes on layer CUT (guideline section 9, D-89 part 4)."""
    out = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4",
           "0", "ENDSEC", "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "1",
           "0", "LAYER", "2", "CUT", "70", "0", "62", "7", "6", "CONTINUOUS", "0", "ENDTAB", "0", "ENDSEC",
           "0", "SECTION", "2", "ENTITIES"]
    for x, y, d in circles:
        out += ["0", "CIRCLE", "8", "CUT", "10", "%.4f" % x, "20", "%.4f" % y, "30", "0.0", "40", "%.4f" % (d / 2.0)]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(out) + "\n")


def build_washer(app):
    doc, design, f = new_design(app, WASHER)
    rev = add_skeleton(design, ["seam_gap"])
    add_params(design, [
        ("rivnut_head", "0.76 mm", "mm", "SOURCE: Sherex CAH3-610-4.2 head 0.76 +-0.08 (joints register SHX)"),
        ("wash_t", "seam_gap - rivnut_head", "mm",
         "CALCULATION: the stop is the rivnut's head on this washer, so 2.26 - 0.76 = 1.5 (joints register 2.8)"),
        ("wash_id", "10.5 mm", "mm", "PROPOSED: bore over the rivnut's body (9.50 max, SHX) (H-08)"),
        ("wash_od", "20 mm", "mm", "PROPOSED: outside, on a 40 mm tube face (H-08)"),
    ])
    root = set_root(design, "831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm",
                    "UNITS MM; MATERIAL EN AW-5052-H32 SHEET 1.5; FINISH MILL, DEBURRED; ISO 2768-m; THICKNESS 1.50 +-0.05; "
                    "laser cut, no drawing (D-89 part 4); joints register H-08; PROPOSED")
    comp = root
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SKETCH - WASHER"
    co = sk.sketchCurves.sketchCircles.addByCenterRadius(p3(0, 0), 1.0)
    ci = sk.sketchCurves.sketchCircles.addByCenterRadius(p3(0, 0), 0.525)
    sk.geometricConstraints.addCoincident(co.centerSketchPoint, sk.originPoint)
    sk.geometricConstraints.addCoincident(ci.centerSketchPoint, sk.originPoint)
    sk.sketchDimensions.addDiameterDimension(co, p3(12, 12)).parameter.expression = "wash_od"
    sk.sketchDimensions.addDiameterDimension(ci, p3(4, 4)).parameter.expression = "wash_id"
    must_constrain(sk)
    ring = next(sk.profiles.item(i) for i in range(sk.profiles.count) if sk.profiles.item(i).profileLoops.count == 2)
    ext = comp.features.extrudeFeatures.addSimple(ring, vi("wash_t"), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.name = "EXTRUDE - WASHER"
    body = ext.bodies.item(0)
    body.name = "STOP WASHER"
    mat = material(comp, ["Aluminum 5052", "Aluminum 5052-H32"], ["5052"]) or material(comp, ["Aluminum"], ["aluminum"])
    health(design)
    b = box(body)
    print("WASHER 831002 (skeleton %s): %s, material %s, mass %.6f kg" % (rev, fmt(b), mat, body.physicalProperties.mass))
    save_export(app, doc, design, f, WASHER,
                "Stop washer 831002, rev P01, PROPOSED (joints register H-08). Built by joints_hardware_build.py",
                [("831002_P01_HARDWARE-STOP-WASHER_STEP.step", None)])
    dias = sorted(round(fc.geometry.radius * 20.0, 3) for fc in body.faces if isinstance(fc.geometry, adsk.core.Cylinder))
    dxf = os.path.join(REPO, MFG_DIR, "831002_P01_HARDWARE-STOP-WASHER_DXF.dxf")
    write_dxf(dxf, [(0.0, 0.0, d) for d in dias])
    print("  DXF %s: circles %s on layer CUT" % (os.path.basename(dxf), dias))
    edit_test(design, lambda: box(comp.bRepBodies.item(0)), [("wash_od", "24 mm")],
              lambda bb, a: abs((a[3] - a[0]) - 24.0) < 0.01)
    doc.close(False)


# ------------------------------------------------------------------ mitre plates 831007 to 831009
def write_dxf_rect(path, w, h):
    """ASCII DXF (R12), mm: a w x h rectangle from the origin, four lines on layer CUT (D-89 part 4)."""
    out = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4",
           "0", "ENDSEC", "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "1",
           "0", "LAYER", "2", "CUT", "70", "0", "62", "7", "6", "CONTINUOUS", "0", "ENDTAB", "0", "ENDSEC",
           "0", "SECTION", "2", "ENTITIES"]
    pts = [(0.0, 0.0), (w, 0.0), (w, h), (0.0, h)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        out += ["0", "LINE", "8", "CUT", "10", "%.4f" % x0, "20", "%.4f" % y0, "30", "0.0",
                "11", "%.4f" % x1, "21", "%.4f" % y1, "31", "0.0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(out) + "\n")


def close_leftover_plates(app):
    """A plate run that failed before saving left its new design open and unsaved: close it, and only it (never saved,
    root part number 831007, a plate_len parameter), so this run doesn't leave two."""
    for i in reversed(range(app.documents.count)):
        d = app.documents.item(i)
        try:
            if d.dataFile is not None:
                continue
            des = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
            if des and des.rootComponent.partNumber == "831007" and des.userParameters.itemByName("plate_len"):
                d.close(False)
                print("  closed a leftover unsaved plate design from an earlier failed run")
        except Exception as e:  # a document this check can't read is left as it is
            print("  (document %d left: %s)" % (i, e))


def build_plates(app):
    """The plate family in one design; on an error, its unsaved design is closed before the error goes on."""
    close_leftover_plates(app)
    doc, design, f = new_design(app, PLATES)
    try:
        _build_plates(app, doc, design, f)
    except Exception:
        try:
            doc.close(False)
            print("  closed the plate design after the error")
        except Exception as e:
            print("  could not close the plate design: %s" % e)
        raise


# the blank of each plate (J-FRAME-01; the Lead's steer 2026-11-01): where it starts along the mitre line from the
# frame's outer corner, and its length, so each corner of both square ends sits at least 0.5 inside the frame's faces
# on both plate faces. A plate the mitre's full size pokes out at the outer corner by its half thickness x the cut's
# cosine (0.71 at 45 deg; 0.45 and 0.89 where a 20 x 40 meets a 40 x 40); the all-round weld fills the step and is
# ground flush. Calculation: frame_steel_check.py's PLATE_BLANKS, which checks every corner (--check).
PLATE_BLANKS = {"831007": ("1.75 mm", "26.5 mm"), "831008": ("3.15 mm", "41.5 mm"), "831009": ("1.75 mm", "54.8 mm")}
PLATE_PARAMS = [
    ("tube_a", "20 mm", "mm", "CONFIRMED: the narrower member's width in the frame's plane, 20 or 40 (D-16, R-J3)"),
    ("tube_b", "20 mm", "mm", "CONFIRMED: the other member's width in the frame's plane, 20 or 40 (D-16, R-J3)"),
    ("plate_mitre", "sqrt(tube_a * tube_a + tube_b * tube_b)", "mm",
     "CALCULATION: the mitre line from the frame's outer corner to its inner corner; the blank lies on it"),
    ("plate_x0", "1.75 mm", "mm",
     "CALCULATION: where the blank starts along the mitre line from the frame's outer corner, so its square ends "
     "sit 0.5 inside the frame's faces on both plate faces (the Lead's steer 2026-11-01): 1.75 at 45 deg (831007, "
     "831009), 3.15 at 831008 (frame_steel_check.py PLATE_BLANKS)"),
    ("plate_len", "26.5 mm", "mm",
     "CALCULATION: the laser-cut blank's length along the mitre line, to 0.1: 26.5 (831007), 41.5 (831008), "
     "54.8 (831009) (frame_steel_check.py PLATE_BLANKS)"),
    ("plate_d", "40 mm", "mm", "CONFIRMED: the frame's depth across the wall, 40 (D-16, D-42)"),
    ("plate_t", "2.0 mm", "mm", "PROPOSED: at least 1.5 x the 1.2 mm rails, a stiffened knee (J-FRAME-01)"),
]
PLATE_SKETCH = "SKETCH - PLATE OUTLINE"
PLATE_EXTRUDE = "EXTRUDE - PLATE, SYMMETRIC ON THE MITRE PLANE"


def plate_geometry(design, comp):
    """The plate's sketch and body from the parameters (PLATE_PARAMS): a plate_len x plate_d rectangle whose corner
    sits plate_x0 along +X from the origin (the frame's outer corner, on the skin-side face), held there by a
    construction line from the origin, extruded plate_t symmetric on the mitre plane. Used by the build and by
    joints_plates_trim_update.py, so both make the same plate."""
    up = design.userParameters
    x0, ln = mm(up.itemByName("plate_x0").value), mm(up.itemByName("plate_len").value)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = PLATE_SKETCH
    lines = sk.sketchCurves.sketchLines.addTwoPointRectangle(p3(x0, 0), p3(x0 + ln, 40.0))
    corner = next(lines.item(i).startSketchPoint for i in range(lines.count)
                  if abs(lines.item(i).startSketchPoint.geometry.x - x0 * CM) < 1e-6
                  and abs(lines.item(i).startSketchPoint.geometry.y) < 1e-6)
    gc = sk.geometricConstraints
    lead = sk.sketchCurves.sketchLines.addByTwoPoints(sk.originPoint, corner)    # origin -> the blank's corner
    lead.isConstruction = True
    try:
        gc.addHorizontal(lead)
    except Exception as e:                       # Fusion often gives a line between two level points its own
        print("  (lead line already horizontal: %s)" % e)
    dims = sk.sketchDimensions
    dims.addDistanceDimension(lead.startSketchPoint, lead.endSketchPoint,
                              adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                              p3(x0 / 2, -10.0)).parameter.expression = "plate_x0"
    horiz = next(lines.item(i) for i in range(lines.count)
                 if abs(lines.item(i).startSketchPoint.geometry.y - lines.item(i).endSketchPoint.geometry.y) < 1e-6)
    vert = next(lines.item(i) for i in range(lines.count)
                if abs(lines.item(i).startSketchPoint.geometry.x - lines.item(i).endSketchPoint.geometry.x) < 1e-6)
    dims.addDistanceDimension(horiz.startSketchPoint, horiz.endSketchPoint,
                              adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                              p3(x0 + ln / 2, -6.0)).parameter.expression = "plate_len"
    dims.addDistanceDimension(vert.startSketchPoint, vert.endSketchPoint,
                              adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,
                              p3(x0 - 6.0, 20.0)).parameter.expression = "plate_d"
    added = []
    # the API's rectangle joins its corners and nothing more (run of 2026-11-01): each edge gets its own horizontal or
    # vertical constraint, and one already held is skipped as redundant
    for i in range(lines.count):
        if sk.isFullyConstrained:
            break
        edge = lines.item(i)
        a, b = edge.startSketchPoint.geometry, edge.endSketchPoint.geometry
        kind = "horizontal" if abs(a.y - b.y) < 1e-6 else "vertical" if abs(a.x - b.x) < 1e-6 else None
        if kind is None:
            continue
        try:
            (gc.addHorizontal if kind == "horizontal" else gc.addVertical)(edge)
            added.append(kind)
        except Exception as e:                                       # already held: redundant, skip it
            print("  (%s constraint skipped: %s)" % (kind, e))
    kinds = sorted(set(gc.item(i).objectType.split("::")[-1] for i in range(gc.count)))
    print("  plate sketch: added %s; fully constrained %s; constraints %s" % (added or "none", sk.isFullyConstrained, kinds))
    must_constrain(sk)
    prof = sk.profiles.item(0)
    ei = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setSymmetricExtent(vi("plate_t"), True)
    ext = comp.features.extrudeFeatures.add(ei)
    ext.name = PLATE_EXTRUDE
    body = ext.bodies.item(0)
    body.name = "MITRE PLATE"
    return body


def plate_state(design, root, variant):
    """Set one variant (members, blank, part number), rebuild, and check its box against the blank; returns the box."""
    num, name, a, b, _stem = variant
    x0, ln = PLATE_BLANKS[num]
    up = design.userParameters
    for pname, expr in (("tube_a", a), ("tube_b", b), ("plate_x0", x0), ("plate_len", ln)):
        up.itemByName(pname).expression = expr
    root.partNumber = num            # each STEP carries its own part number (C06)
    root.description = "%s | rev %s | members %s and %s; blank %s long from %s along the mitre | joints register " \
                       "J-FRAME-01 | PROPOSED" % (name, REV, a, b, ln, x0)
    adsk.doEvents()
    health(design)
    body = root.bRepBodies.item(0)
    bb = box(body)
    sx, sl = float(x0.split()[0]), float(ln.split()[0])
    want = (sx, 0.0, -1.0, sx + sl, 40.0, 1.0)
    if any(abs(g - w) > 0.005 for g, w in zip(bb, want)):
        raise RuntimeError("%s: the plate is %s, want %s" % (num, fmt(bb), fmt(want)))
    mitre = mm(up.itemByName("plate_mitre").value)
    if bb[3] > mitre + 1e-6:
        raise RuntimeError("%s: the blank runs past the mitre's inner corner (%.3f > %.3f)" % (num, bb[3], mitre))
    print("    %s (%s, %s): %s, %.5f kg; the mitre line %.3f" % (num, a, b, fmt(bb), body.physicalProperties.mass, mitre))
    return bb


def plate_edit_test(design, root):
    """Guideline 4.4: the blank's start moves the plate along the mitre, its length stays; then back."""
    edit_test(design, lambda: box(root.bRepBodies.item(0)), [("plate_x0", "3.15 mm")],
              lambda b0, a1: abs(a1[0] - 3.15) < 0.01 and abs((a1[3] - a1[0]) - (b0[3] - b0[0])) < 0.01)


def write_plate_dxfs(design, root):
    for v in PLATE_VARIANTS:
        bb = plate_state(design, root, v)
        dxf = os.path.join(REPO, MFG_DIR, v[4] + "_DXF.dxf")
        write_dxf_rect(dxf, bb[3] - bb[0], bb[4] - bb[1])
        print("  DXF %s: %.3f x %.3f on layer CUT" % (os.path.basename(dxf), bb[3] - bb[0], bb[4] - bb[1]))


def _build_plates(app, doc, design, f):
    """The frames' mitre plates (joints register H-40 to H-42, J-FRAME-01): a flat 2.0 blank on the mitre line.
    Origin at the frame's outer corner, on the skin-side face, on the plate's mid-plane; +X along the mitre toward the
    frame's inner corner (the blank starts plate_x0 along it); +Y across the frame toward the room side; Z through the
    plate, -1.0 to +1.0 (the joints CAD README)."""
    add_params(design, PLATE_PARAMS)
    num, name, _a, _b, _stem = PLATE_VARIANTS[0]
    root = set_root(design, num, name, "Tấm đệm góc vát - thép 2.0",
                    "UNITS MM; MATERIAL S280GD+Z (EN 10346) OR SGC400, Z100, 2.0 SHEET; ISO 2768-m; THICKNESS 2.0 "
                    "+-0.1; laser cut, no drawing (D-89 part 4); joints register H-40 to H-42; PROPOSED")
    plate_geometry(design, root)
    mat = material(root, ["Steel, Galvanized", "Steel"], ["steel"])
    health(design)
    family = (root.partNumber, root.description)
    print("PLATES: material %s" % mat)
    save_export(app, doc, design, f, PLATES,
                "Mitre plates 831007-831009, rev P01, PROPOSED (joints register H-40 to H-42, J-FRAME-01); saved at "
                "831007. Built by joints_hardware_build.py",
                [(v[4] + "_STEP.step", (lambda v=v: plate_state(design, root, v))) for v in PLATE_VARIANTS])
    write_plate_dxfs(design, root)
    plate_state(design, root, PLATE_VARIANTS[0])        # back to the saved state, 831007
    root.partNumber, root.description = family
    plate_edit_test(design, root)
    doc.close(False)


def run(_context):
    app = adsk.core.Application.get()
    for d in (CAD_DIR, MFG_DIR):
        os.makedirs(os.path.join(REPO, d), exist_ok=True)
    which = [w.strip() for w in ARGS.get("only", "keys,spigot,washer,plates").split(",") if w.strip()]
    for w in which:
        {"keys": build_keys, "spigot": build_spigot, "washer": build_washer, "plates": build_plates}[w](app)
    print("done: %s" % ", ".join(which))
