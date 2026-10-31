"""Build 710000 ELECTRICAL P01 in Fusion: the cable routes, connector pockets,
grommets, the power unit and the hub zone as named bodies, linked to skeleton
P04 by Derive.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/electrical_build.py \
        --label "ELECTRICAL Engineer" --doc 710000_P01_ELECTRICAL_CAD --doc-new \
        --arg save=1 --arg export=1 --close --discard

What it does, in one run (an exception rolls every change back):
1. derives the skeleton's favourite parameters (they arrive as <name>_Ref) and
   adds a user parameter of the same plain name for each one it uses, then the
   electrical parameters from electrical_model.PARAMS, each with its status and
   source in the comment;
2. builds one component per harness or zone and one body per reserved space,
   every sketch fully constrained by the parameter expressions;
3. checks: timeline health, loose sketches, every body box against the offline
   model (0.01 mm), no overlap between its own bodies, and no overlap with a
   skeleton P04 body that the model doesn't list as intended (exact Fusion
   intersections, 0.1 mm3);
4. save=1: saves the design (the cloud copy keeps its link to the skeleton);
5. export=1: breaks the derive link in memory only (shared rule for repo
   exports: a linked .f3d won't open on its own), writes the .f3d and the STEP
   (Fusion writes cm, declared in the file, D-13), re-reads the STEP and
   compares its box. run_script's --close --discard then drops the unlinked
   copy, so the cloud design stays linked.
"""

import importlib
import os
import sys
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(ARGS.get("script_path", globals().get("__file__", "."))))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import electrical_model as M  # noqa: E402

importlib.reload(M)            # Fusion keeps modules between runs

MM = 0.1                       # Fusion's internal unit is cm
CLOUD_FOLDER = "FocusPod v2"
F3D_REL = "v2/01-CAD-Native/electrical/%s.f3d" % M.DOC_NAME
STEP_REL = "v2/03-Manufacturing/electrical/%s_STEP.step" % M.DOC_NAME[:-4]
TOL_BOX = 0.01                 # mm, body box against the offline model
TOL_VOL = 0.1                  # mm3, the mechanical check's clash threshold


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design: "adsk.fusion.Design", expr):
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def box(body: "adsk.fusion.BRepBody"):
    b = body.boundingBox
    return [round(v * 10.0, 3) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def _axis_of(sk: "adsk.fusion.Sketch", model_axis):
    """Which sketch axis ('x' or 'y') a model axis maps to."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def _normal_sign(sk: "adsk.fusion.Sketch", axis):
    n = sk.xDirection.crossProduct(sk.yDirection)
    return 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1


def extrude_span(comp: "adsk.fusion.Component", sk: "adsk.fusion.Sketch", axis, a_expr, b_expr, name):
    """New body: the sketch's profile extruded along a model axis from a to b."""
    sign = _normal_sign(sk, axis)
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                   adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi("(%s) * (%d)" % (a_expr, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("(%s) - (%s)" % (b_expr, a_expr))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    return f


BASE_PLANE = {"z": "xYConstructionPlane", "y": "xZConstructionPlane", "x": "yZConstructionPlane"}


def _dim_point(design: "adsk.fusion.Design", sk: "adsk.fusion.Sketch", pt: "adsk.fusion.SketchPoint", axis_expr):
    """Dimension a sketch point from the sketch origin along each model axis in
    axis_expr {model axis: expression}; a zero coordinate gets a coincidence."""
    dims, gc = sk.sketchDimensions, sk.geometricConstraints
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for ax, ex in axis_expr.items():
        sa = _axis_of(sk, ax)
        if abs(ev(design, ex)) < 1e-6:
            (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(pt, sk.originPoint)
        else:
            g = pt.geometry
            tp = adsk.core.Point3D.create(g.x + 0.7, g.y + 0.7, 0)
            dims.addDistanceDimension(sk.originPoint, pt, H if sa == "x" else V, tp).parameter.expression = \
                "abs(%s)" % ex


def build_box(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", b):
    """A box from the XY plane: rectangle dimensioned to the origin, extruded z0 -> z1."""
    (ex0, ex1), (ey0, ey1), (ez0, ez1) = b["x"], b["y"], b["z"]
    x0, x1, y0, y1 = (ev(design, e) for e in (ex0, ex1, ey0, ey1))
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "OUTLINE - %s" % b["code"]
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0 * MM, y0 * MM, 0), adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
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
    c00, c10, c01 = near(x0, y0), near(x1, y0), near(x0, y1)
    dims = sk.sketchDimensions
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    tp = adsk.core.Point3D.create((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
    dims.addDistanceDimension(c00, c10, H, tp).parameter.expression = "(%s) - (%s)" % (ex1, ex0)
    dims.addDistanceDimension(c00, c01, V, tp).parameter.expression = "(%s) - (%s)" % (ey1, ey0)
    _dim_point(design, sk, c00, {"x": ex0, "y": ey0})
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    f = extrude_span(comp, sk, "z", ez0, ez1, "EXTRUDE - %s" % b["code"])
    return f.bodies.item(0)


def build_cyl(design: "adsk.fusion.Design", comp: "adsk.fusion.Component", b):
    """A cylinder: circle on the origin plane normal to its axis, extruded a0 -> a1."""
    axis = b["axis"]
    others = [a for a in ("x", "y", "z") if a != axis]
    sk = comp.sketches.add(getattr(comp, BASE_PLANE[axis]))
    sk.name = "OUTLINE - %s" % b["code"]
    c = {axis: 0.0, others[0]: ev(design, b["c"][0]), others[1]: ev(design, b["c"][1])}
    p = sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM))
    circ = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(p.x, p.y, 0),
                                                           ev(design, b["d"]) / 2 * MM)
    g = circ.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(circ, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)) \
        .parameter.expression = b["d"]
    _dim_point(design, sk, circ.centerSketchPoint, {others[0]: b["c"][0], others[1]: b["c"][1]})
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    f = extrude_span(comp, sk, axis, b["a"][0], b["a"][1], "EXTRUDE - %s" % b["code"])
    return f.bodies.item(0)


def find_file(app: "adsk.core.Application", name):
    """The one DataFile called `name` in Default Project / FocusPod v2. Other
    agents save into the same folder, so its list can change while it is read
    (run of 2026-10-31: 'invalid argument index'): take a snapshot with
    asArray() and retry."""
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    app.data.activeProject = proj
    folder = proj.rootFolder.dataFolders.itemByName(CLOUD_FOLDER)
    last = None
    for _try in range(6):
        try:
            entries = folder.dataFiles.asArray()
        except RuntimeError as e:   # the list changed under us
            last = e
            adsk.doEvents()
            time.sleep(2)
            continue
        hits, unreadable = [], 0
        for f in entries:
            try:                    # one unreadable entry must not stop the rest (as run_script, PR #86)
                if f.name == name:
                    hits.append(f)
            except RuntimeError:
                unreadable += 1
        if unreadable:
            print("find_file: %d entries of %s could not be read; skipped" % (unreadable, CLOUD_FOLDER))
        if len(hits) != 1:
            raise RuntimeError("expected one %r in %s, found %d" % (name, CLOUD_FOLDER, len(hits)))
        return hits[0]
    raise RuntimeError("could not read %s: %s" % (CLOUD_FOLDER, last))


def skeleton_bodies(skel: "adsk.fusion.Design"):
    """{code: body} for every body of the skeleton, by its body name."""
    out = {}
    for comp in skel.allComponents:
        for i in range(comp.bRepBodies.count):
            b = comp.bRepBodies.item(i)
            code = b.name
            for suffix in (" ENVELOPE", " FACETED", " GLASS"):
                if code.endswith(suffix):
                    code = code[:-len(suffix)]
            out[code] = b
    return out


def intersect_mm3(tbm: "adsk.fusion.TemporaryBRepManager", a: "adsk.fusion.BRepBody", b: "adsk.fusion.BRepBody"):
    ba, bb = box(a), box(b)
    if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
        return 0.0
    t1, t2 = tbm.copy(a), tbm.copy(b)
    tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return t1.volume * 1000.0 if t1 else 0.0


def clear_design(design: "adsk.fusion.Design"):
    """Empty the design for a rebuild: the timeline (features, sketches, the derive) and the components.
    User parameters stay and are updated in place, because a parameter that a feature still uses can't
    be deleted (run of 2026-10-31: 'param name is not valid' on re-adding one)."""
    for i in range(design.userParameters.count):      # freeze values, so nothing points at the old derive
        p = design.userParameters.item(i)
        if p.unit == "mm":
            p.expression = "%.6f mm" % (p.value * 10.0)
        elif p.unit == "":
            p.expression = "%.6f" % p.value
    tl = design.timeline
    if tl.count:
        tl.markerPosition = 0
        tl.deleteAllAfterMarker()
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    left = design.timeline.count + root.occurrences.count + root.bRepBodies.count
    if left:
        raise RuntimeError("rebuild: %d timeline items, components or bodies left after clearing" % left)


def set_param(design: "adsk.fusion.Design", name, expr, unit, comment):
    """Add a user parameter, or update it in place when a rebuild finds it."""
    p = design.userParameters.itemByName(name)
    if p is None:
        return design.userParameters.add(name, vi(expr), unit, comment)
    p.expression = expr
    p.comment = comment
    return p


def export_with_retry(em: "adsk.fusion.ExportManager", mk, path, root: "adsk.fusion.Component"):
    for _try in range(10):          # right after a save Fusion may still be uploading
        if em.execute(mk(path, root)) and os.path.getsize(path) > 1000:
            return True
        adsk.doEvents()
        time.sleep(3)
    return False


def skeleton_missing(app: "adsk.core.Application"):
    """Favourites this build needs from skeleton P04 that aren't there. PM heads-up 2026-10-31 (about
    18:53): P04 lost its favourite skin_t for a while, and builds that derive its favourites wait until
    Fusion Engineer 2 restores it. Read-only; closes the skeleton only if this run opened it."""
    was_open = any(app.documents.item(i).name.split(" v")[0] == M.SKELETON_DOC for i in range(app.documents.count))
    d = app.documents.open(find_file(app, M.SKELETON_DOC), False)
    try:
        skel = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
        out = []
        for n in ["skin_t"] + list(M.SKELETON_PARAMS):
            p = skel.userParameters.itemByName(n)
            if p is None or not p.isFavorite:
                out.append(n)
        return out
    finally:
        if not was_open:
            d.close(False)


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc.name != M.DOC_NAME:
        raise RuntimeError("active document is %r, not %r (use --doc)" % (doc.name, M.DOC_NAME))
    missing = skeleton_missing(app)
    if missing:
        raise RuntimeError("held, nothing changed: skeleton P04 lacks the favourite(s) %s; this build derives its "
                           "favourites, so it waits until they are restored (PM heads-up 2026-10-31)" % ", ".join(missing))
    doc.activate()
    print("skeleton P04: skin_t and the %d favourites this build derives are there" % len(M.SKELETON_PARAMS))
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    if root.occurrences.count or design.userParameters.count or design.timeline.count:
        if ARGS.get("rebuild") != "1":
            raise RuntimeError("%s is not empty; pass --arg rebuild=1 to rebuild it" % doc.name)
        clear_design(design)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits

    # 1. derive the skeleton's parameters
    skel_doc = app.documents.open(find_file(app, M.SKELETON_DOC), False)
    try:
        skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
        doc.activate()
        di = root.features.deriveFeatures.createInput(skel)
        di.isIncludeFavoriteParameters = True
        di.sourceEntities = [skel.rootComponent.xYConstructionPlane]
        der = root.features.deriveFeatures.add(di)
        der.name = "DERIVE - SKELETON P04 PARAMETERS"
        for name in M.SKELETON_PARAMS:
            ref = design.allParameters.itemByName(name + "_Ref")
            if ref is None:
                raise RuntimeError("derived parameter %s_Ref not found" % name)
            set_param(design, name, name + "_Ref", "mm", "SOURCE: skeleton P04 %s, derived (%s)" % (name, M.SKELETON_DOC))
        for name, expr, unit, status, src in M.PARAMS:
            set_param(design, name, expr, unit, "%s: %s" % (status.upper(), src))
        root.partNumber = "710000"
        root.description = "ELECTRICAL | Điện | %s | routes, pockets, grommets, power unit, hub zone" % M.REV

        # 2. components and bodies
        comps = {}
        for key, pn, name, vn, kind in M.COMPONENTS:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            c = occ.component
            c.name = "%s %s" % (pn, name)
            c.partNumber = pn
            c.description = "%s | %s | %s | %s" % (name, vn, kind, M.REV)
            comps[key] = c
        bodies = {}
        for b in M.BODIES:
            body = (build_box if b["kind"] == M.B else build_cyl)(design, comps[b["comp"]], b)
            body.name = "%s %s" % (b["code"], b["name"])
            bodies[b["code"]] = body

        # 3. checks
        tl = design.timeline
        unhealthy = [tl.item(i).name for i in range(tl.count)
                     if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
        live = {name: design.userParameters.itemByName(name).value * 10.0 for name in M.SKELETON_PARAMS}
        changed = {k: (round(M.SKELETON_VALUES[k], 3), round(v, 3)) for k, v in live.items()
                   if abs(v - M.SKELETON_VALUES[k]) > 1e-6}
        values = M.values(live)          # the boxes follow the live skeleton
        off = []
        for b in M.BODIES:
            want = M.body_box(b, values)
            got = box(bodies[b["code"]])
            d = max(abs(g - w) for g, w in zip(got, want))
            if d > TOL_BOX:
                off.append((b["code"], round(d, 3), got, [round(w, 3) for w in want]))
        tbm = adsk.fusion.TemporaryBRepManager.get()
        own = []
        codes = [b["code"] for b in M.BODIES]
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                v = intersect_mm3(tbm, bodies[codes[i]], bodies[codes[j]])
                if v > TOL_VOL:
                    own.append((codes[i], codes[j], round(v, 1)))
        sk_bodies = skeleton_bodies(skel)
        hits, bad = [], []
        for b in M.BODIES:
            allowed = {a for a, _why in b["allow"]}
            for code, sb in sk_bodies.items():
                v = intersect_mm3(tbm, bodies[b["code"]], sb)
                if v > TOL_VOL:
                    hits.append((b["code"], code, round(v, 1)))
                    if code not in allowed:
                        bad.append((b["code"], code, round(v, 1)))
        unused = [(b["code"], a) for b in M.BODIES for a, _w in b["allow"]
                  if not any(h[0] == b["code"] and h[1] == a for h in hits)]
    finally:
        skel_doc.close(False)
        doc.activate()

    print("bodies %d, components %d, timeline %d items, unhealthy %d, loose sketches %d, user parameters %d" % (
        len(bodies), len(comps), tl.count, len(unhealthy), len(loose), design.userParameters.count))
    for b in M.BODIES:
        print("BODY|%s|%s|%s|%s" % (b["code"], b["comp"], b["kind"], box(bodies[b["code"]])))
    print("skeleton bodies read: %d; live skeleton values that differ from the repo CSV (csv, live): %s" % (
        len(sk_bodies), changed))
    for h in hits:
        print("OVERLAP|%s|%s|%.1f mm3|%s" % (h[0], h[1], h[2], "UNEXPECTED" if h in bad else "intended"))
    print("own overlaps: %s" % own)
    print("box mismatches: %s" % off)
    print("intended overlaps not found (allow entries that are not needed): %s" % unused)
    rb = box(root)
    print("design box %s" % rb)
    if unhealthy or loose or off or own or bad:
        raise RuntimeError("electrical checks failed: unhealthy %s, loose %s, boxes %s, own %s, clashes %s" % (
            unhealthy, loose, off, own, bad))

    # 4. save (keeps the link)
    if ARGS.get("save") == "1":
        print("saved:", doc.save("ELECTRICAL %s: routes, pockets, grommets, power unit, hub zone (skeleton P04)" % M.REV))

    # 5. repo export from an unlinked copy in memory
    if ARGS.get("export") == "1":
        if ARGS.get("save") != "1":
            raise RuntimeError("export=1 needs save=1: export only what the cloud copy holds")
        for i in range(root.features.deriveFeatures.count):
            print("derive link broken for the export:", root.features.deriveFeatures.item(i).breakLink())
        adsk.doEvents()
        bad_params = [p.name for p in design.userParameters if not p.isValid or p.value is None]
        if bad_params:
            raise RuntimeError("parameters broken after unlinking: %s" % bad_params)
        repo = ARGS["repo_root"]
        em = design.exportManager
        for rel, mk in ((F3D_REL, em.createFusionArchiveExportOptions), (STEP_REL, em.createSTEPExportOptions)):
            path = os.path.join(repo, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            ok = export_with_retry(em, mk, path, root)
            print("export %s: %s" % (rel, ok))
            if not ok:
                raise RuntimeError("export failed: " + rel)
        copy = app.importManager.importToNewDocument(
            app.importManager.createSTEPImportOptions(os.path.join(repo, STEP_REL)))
        try:
            cd = adsk.fusion.Design.cast(copy.products.itemByProductType("DesignProductType"))
            got = box(cd.rootComponent)
            n = sum(c.bRepBodies.count for c in cd.allComponents)
        finally:
            copy.close(False)
            doc.activate()
        diff = max(abs(a - b) for a, b in zip(rb, got))
        print("STEP re-read: %d bodies, box %s, max difference %.3f mm" % (n, got, diff))
        if diff > 0.05 or n != len(bodies):
            raise RuntimeError("STEP re-read does not match the design")
