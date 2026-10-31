"""Spaceship (FocusPod v2) INTERIOR P01: native, parameter-driven Fusion design (D-70, D-85).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/interior/interior_build.py \\
        --doc 810000_P01_INTERIOR_CAD --doc-new --arg into_active=1 --arg save=1 --arg export=1 \\
        --label "CEILING Engineer" --close --discard

Builds 810000 INTERIOR in pod coordinates (conventions.md section 4):

  810101 INTERIOR - WORK WALL LEDGE ASSY: 811101 ledge top (1.5 mm folded aluminium, its
         section a sketch extruded along the wall) and 2 x 818101 bracket envelopes (HOLD)
  810201 INTERIOR - LIGHT SHELF ASSY: 811201 back, 811202 LH, 811203 RH (1.0 mm folded
         aluminium U), 811204 down channel RH, 811205 diffuser RH; cable holes at ELECTRICAL's
         feed (X 355) and call-light drop (Y -209.5)
  818102 INTERIOR - SCREEN RAIL (HOLD envelope)

Every size is a user parameter (the skeleton's list, the ceiling's and INTERIOR's, each with
its status and source). Checks fail the run: timeline health, every sketch fully constrained,
every body where the layout says, no clash.
"""

import importlib
import os
import sys
import time

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
for d in (HERE, os.path.join(HERE, "..", "ceiling")):
    if d not in sys.path:
        sys.path.insert(0, d)
import ceiling_model  # noqa: E402
importlib.reload(ceiling_model)
import ceiling_checks  # noqa: E402,F401
importlib.reload(ceiling_checks)
import ceiling_build as CB  # noqa: E402  (tested helpers: sketches, boxes, holes, clash check)
importlib.reload(CB)
import interior_model as I  # noqa: E402
importlib.reload(I)

DOC_NAME = "810000_%s_INTERIOR_CAD" % I.REV
F3D_REL = "v2/01-CAD-Native/interior/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/interior/810000_%s_INTERIOR_STEP.step" % I.REV
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation


def new_comp(parent, key):
    pn, name, vn, kind, _mat = I.PARTS[key]
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = "%s %s" % (pn, name)
    c.partNumber = pn
    c.description = "%s | %s | %s | %s" % (name, vn, kind, I.REV)
    return occ, c


def set_material(design, comp, key):
    mk = I.PARTS[key][4]
    name, density, _st, _src = I.MATERIALS[mk]
    m = design.materials.itemByName(name)
    if m is None:
        lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
        m = design.materials.addByCopy(lib.materials.itemByName("Aluminum"), name)
        m.materialProperties.itemById("structural_Density").value = density
    for b in comp.bRepBodies:
        b.material = m


def poly(comp, name, pts, plane_key, ctx):
    """Closed polygon on the XZ or YZ construction plane, each corner dimensioned from the
    origin by its expressions (pts = [(u_expr, z_expr)], u = model X for 'xz', model Y for
    'yz'). Returns the fully constrained sketch."""
    plane = comp.xZConstructionPlane if plane_key == "xz" else comp.yZConstructionPlane
    ua = "x" if plane_key == "xz" else "y"
    sk = comp.sketches.add(plane)
    sk.name = name

    def p3(u, z):
        return adsk.core.Point3D.create(u * CB.MM if ua == "x" else 0, u * CB.MM if ua == "y" else 0, z * CB.MM)
    sp = [sk.modelToSketchSpace(p3(ctx.ev(u), ctx.ev(z))) for u, z in pts]
    lines = sk.sketchCurves.sketchLines
    verts, edges = [], []
    n = len(sp)
    for i in range(n):
        start = verts[-1] if verts else adsk.core.Point3D.create(sp[0].x, sp[0].y, 0)
        end = adsk.core.Point3D.create(sp[i + 1].x, sp[i + 1].y, 0) if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(start, end)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    gc, dims = sk.geometricConstraints, sk.sketchDimensions
    s_u, _ = CB.model_to_sketch_axis(sk, ua)
    expr_of = {s_u: 0, ("y" if s_u == "x" else "x"): 1}
    for sa in ("x", "y"):
        # vertices joined by an edge along the other axis share this coordinate: one dimension
        # per joined group (as ceiling_build.poly_xz does), not one per value
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
            ex = pts[i][expr_of[sa]]
            vp = verts[i]
            if abs(ctx.ev(ex)) < CB.EPS:
                (gc.addVerticalPoints if sa == "x" else gc.addHorizontalPoints)(vp, sk.originPoint)
            else:
                g = vp.geometry
                tp = adsk.core.Point3D.create(g.x + 0.4, g.y + 0.4, 0)
                dims.addDistanceDimension(sk.originPoint, vp, CB.H if sa == "x" else CB.V, tp).parameter.expression = \
                    "abs(%s)" % ex
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + name)
    return sk


def extrude_along(comp, sk, axis, a0, a1, name):
    """Extrude every profile of a sketch on the XZ (axis 'y') or YZ (axis 'x') plane from a0 to
    a1 along the model axis, as one new body named `name`."""
    n = sk.xDirection.crossProduct(sk.yDirection)
    comp_n = n.y if axis == "y" else n.x
    sign = 1 if comp_n > 0 else -1
    coll = adsk.core.ObjectCollection.create()
    for pr in sk.profiles:
        coll.add(pr)
    ei = comp.features.extrudeFeatures.createInput(coll, NEW)
    ei.startExtent = adsk.fusion.OffsetStartDefinition.create(CB.vi("(%s) * (%d)" % (a0, sign)))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(CB.vi("(%s) - (%s)" % (a1, a0))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if sign > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - " + name
    if f.bodies.count != 1:
        raise RuntimeError("%s: expected one body, got %d" % (name, f.bodies.count))
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def circle_cut_y(comp, body, name, cx, cz, y0, y1, dia, ctx):
    plane = CB.offset_plane(comp, comp.xZConstructionPlane, y0, "PLANE - %s" % name)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE - " + name
    cen = sk.modelToSketchSpace(adsk.core.Point3D.create(ctx.ev(cx) * CB.MM, ctx.ev(y0) * CB.MM, ctx.ev(cz) * CB.MM))
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(cen.x, cen.y, 0), ctx.ev(dia) / 2 * CB.MM)
    g = c.centerSketchPoint.geometry
    sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0)).parameter.expression = dia
    for model_axis, expr in (("x", cx), ("z", cz)):
        sa, _s = CB.model_to_sketch_axis(sk, model_axis)
        sk.sketchDimensions.addDistanceDimension(sk.originPoint, c.centerSketchPoint, CB.H if sa == "x" else CB.V,
                                                 adsk.core.Point3D.create(g.x + 0.6, g.y + 0.6, 0)).parameter.expression = \
            "abs(%s)" % expr
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: HOLE - " + name)
    n = sk.xDirection.crossProduct(sk.yDirection)
    want = 1 if ctx.ev(y1) > ctx.ev(y0) else -1
    prof = min(sk.profiles, key=lambda p: p.areaProperties().area)
    ei = comp.features.extrudeFeatures.createInput(prof, CUT)
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(CB.vi("abs((%s) - (%s)) + 1 mm" % (y1, y0))),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection if n.y * want > 0
                        else adsk.fusion.ExtentDirections.NegativeExtentDirection)
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - " + name
    return f


FOLDER = "Default Project/FocusPod v2"
PART_SCOPES = ("ledge", "shelf_back", "shelf_rh", "dchan")      # part-only designs for drawings (D-89 plan)


def part_doc_name(key):
    import re
    pn, name, _vn, _k, _m = I.PARTS[key]
    return "%s_%s_%s_CAD" % (pn, I.REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"))


def open_or_create(app, name):
    """The design called `name` in FOLDER: activate it if open, open it from the cloud, or
    make it there (the same steps as run_script.py --doc NAME --doc-new)."""
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
    files = [folder.dataFiles.item(i) for i in range(folder.dataFiles.count)]
    files = [f for f in files if f.name == name]
    app.data.activeProject = proj
    if files:
        d = app.documents.open(files[0], True)
        d.activate()
        return d, "opened"
    if ARGS.get("create") != "1":
        # PM ruling 2026-11-01: no new designs until the runner's folder fix lands, since an
        # entry Fusion can't read could make a second, empty design with a real one's name
        raise RuntimeError("%r is not in %s; pass create=1 to make it (only once that's allowed)" % (name, FOLDER))
    d = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    if not d.saveAs(name, folder, "new, made by interior_build.py parts=", ""):
        raise RuntimeError("saveAs %r failed" % name)
    d.activate()
    return d, "made"


def build_bodies(root, design, ctx, keys):
    """Build the layout bodies of the given part keys straight into `root` (part-only design)."""
    made = {}
    for key, name, kind, data in I.layout():
        if key not in keys:
            continue
        if kind == "box":
            made[name] = (root, CB.box_body(root, name, data, ctx))
        else:
            sec, a0, a1 = data
            sk = poly(root, "SECTION - " + name, sec, kind, ctx)
            made[name] = (root, extrude_along(root, sk, "y" if kind == "xz" else "x", a0, a1, name))
    for k, (bname, kind, a) in enumerate(I.features()):
        if bname not in made:
            continue
        c, body = made[bname]
        label = "%s CABLE HOLE %d" % (bname, k + 1)
        if kind == "ycircle":
            circle_cut_y(c, body, label, a[0], a[1], a[2], a[3], a[4], ctx)
        else:
            CB.circle_cut_x(c, body, label, a[0], a[1], a[2], a[4], "2 * sh_t", int(a[3]), ctx)
    return made


def run_parts(app, keys):
    """One run, several part-only designs (fair-share queue rule, PM ruling 2026-11-01)."""
    for key in keys:
        if key not in PART_SCOPES:
            raise RuntimeError("part scope must be one of %s" % (PART_SCOPES,))
        name = part_doc_name(key)
        doc, how = open_or_create(app, name)
        design = adsk.fusion.Design.cast(app.activeProduct)
        CB.clear_design(design)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        ctx = CB.Ctx(design)
        params = I.all_params()
        for pname, expr, unit, status, src in params:
            design.userParameters.add(pname, CB.vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = I.evaluate(params)
        root = design.rootComponent
        pn, pname_, vn, kind, _m = I.PARTS[key]
        root.partNumber = pn
        root.description = "%s | %s | %s | %s | drawing source, built by interior_build.py" % (pname_, vn, kind, I.REV)
        build_bodies(root, design, ctx, (key,))
        set_material(design, root, key)
        adsk.doEvents()
        tl = design.timeline
        bad = [tl.item(i).name for i in range(tl.count)
               if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
        loose = [sk.name for sk in root.sketches if not sk.isFullyConstrained]
        print("PART %s %s (%s): timeline %d, unhealthy %d, loose %d, bodies %d, box %s" % (
            pn, pname_, how, tl.count, len(bad), len(loose), root.bRepBodies.count, CB.body_box(root)))
        if bad or loose:
            raise RuntimeError("part %s checks failed (unhealthy %s, loose %s)" % (key, bad, loose))
        print("saved:", doc.save("%s %s drawing source, skeleton %s" % (pn, I.REV, ceiling_model.SKELETON_REV)))
        adsk.doEvents()
        doc.close(False)


def run(_context):
    app = adsk.core.Application.get()
    if ARGS.get("parts"):
        run_parts(app, [k for k in ARGS["parts"].split(",") if k])
        return
    into_active = ARGS.get("into_active") == "1"
    if into_active:
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
        params = I.all_params()
        for name, expr, unit, status, src in params:
            design.userParameters.add(name, CB.vi(expr), unit, "%s: %s" % (status.upper(), src))
        ctx.vals = I.evaluate(params)
        root = design.rootComponent
        root.partNumber = "810000"
        root.description = "INTERIOR | Nội thất | HS | " + I.REV
        made = {}
        _o, ledge_assy = new_comp(root, "ledge_assy")
        _o, shelf_assy = new_comp(root, "shelf_assy")
        parents = {"ledge": ledge_assy, "bracket": ledge_assy, "shelf_back": shelf_assy, "shelf_lh": shelf_assy,
                   "shelf_rh": shelf_assy, "dchan": shelf_assy, "diffuser": shelf_assy, "rail": root}
        comps = {}
        for key, name, kind, data in I.layout():
            if key not in comps:
                _o2, comps[key] = new_comp(parents[key], key)
            c = comps[key]
            if kind == "box":
                made[name] = (c, CB.box_body(c, name, data, ctx))
            else:
                sec, a0, a1 = data
                sk = poly(c, "SECTION - " + name, sec, kind, ctx)
                made[name] = (c, extrude_along(c, sk, "y" if kind == "xz" else "x", a0, a1, name))
        for key, c in comps.items():
            set_material(design, c, key)
        for k, (bname, kind, a) in enumerate(I.features()):
            c, body = made[bname]
            label = "%s CABLE HOLE %d" % (bname, k + 1)
            if kind == "ycircle":
                circle_cut_y(c, body, label, a[0], a[1], a[2], a[3], a[4], ctx)
            else:
                CB.circle_cut_x(c, body, label, a[0], a[1], a[2], a[4], "2 * sh_t", int(a[3]), ctx)
        adsk.doEvents()
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
        want = I.boxes(ctx.vals)
        got = {n.split("/")[-1]: CB.body_box(b) for n, b in bodies}
        off, worst = [], 0.0
        for name, (_k, b) in want.items():
            w = [b[0], b[2], b[4], b[1], b[3], b[5]]
            h = got.get(name)
            if h is None:
                off.append((name, "missing"))
                continue
            d = max(abs(p - q) for p, q in zip(h, w))
            worst = max(worst, d)
            if d > 0.05:
                off.append((name, round(d, 3)))
        print("position check: %d layout bodies, worst %.3f mm, off %s" % (len(want), worst, off or "none"))
        for n, b in bodies:
            print("BODY|%s|%s" % (n, CB.body_box(b)))
        for occ in root.allOccurrences:
            c = occ.component
            if c.bRepBodies.count:
                print("MASS|%s|%s|%.3f kg" % (occ.fullPathName, c.partNumber, c.getPhysicalProperties().mass))
        if bad or loose or hits or off:
            raise RuntimeError("INTERIOR checks failed (unhealthy %s, loose %s, clashes %s, off %s)" % (bad, loose, hits, off))
        design.activateRootComponent()
        if ARGS.get("save") == "1":
            if not into_active:
                raise RuntimeError("save=1 needs into_active=1 with the runner's --doc %s --doc-new" % DOC_NAME)
            print("saved:", doc.save("INTERIOR %s build, skeleton %s" % (I.REV, ceiling_model.SKELETON_REV)))
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
        if not (into_active or ARGS.get("keep") == "1"):
            doc.close(False)
    if not ok:
        raise RuntimeError("build did not finish")
