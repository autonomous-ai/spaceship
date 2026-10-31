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
for d in (HERE, os.path.join(HERE, "..", "ceiling")):
    if d not in sys.path:
        sys.path.insert(0, d)
import ceiling_model  # noqa: E402
importlib.reload(ceiling_model)
import ceiling_checks  # noqa: E402,F401
importlib.reload(ceiling_checks)
import ceiling_build as CB  # noqa: E402  (tested helpers: sketches, boxes, joints, checks)
importlib.reload(CB)
import air_model as A  # noqa: E402
importlib.reload(A)

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
        m.materialProperties.itemById("structural_Density").value = density
    for b in comp.bRepBodies:
        b.material = m


def hollow_closed(comp, body, name):
    coll = adsk.core.ObjectCollection.create()
    coll.add(body)
    si = comp.features.shellFeatures.createInput(coll, False)
    si.insideThickness = CB.vi("box_t")
    f = comp.features.shellFeatures.add(si)
    f.name = "SHELL - %s" % name
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


def build_cartridge(parent, design, ctx, bx, along, tag):
    """Casing (2 mm tube open at both ends) and three 50 mm layers parallel to the
    front face, with two passages between them. bx: outer box; along: 'z' or 'x'."""
    occ, comp = new_comp(parent, "cart")
    comp.name = comp.name + " (%s)" % tag
    x0, x1, y0, y1, z0, z1 = bx
    casing = CB.box_body(comp, "CARTRIDGE %s" % tag, bx, ctx)     # the casing carries the layout name
    hollow_axis(comp, casing, along, "cart_t", "CARTRIDGE %s CASING" % tag)
    for k in range(3):
        ly0 = "%s + cart_t + %d * (lay_t + pass_w)" % (y0, k)
        if along == "z":
            lb = ("%s + cart_t" % x0, "%s - cart_t" % x1, ly0, "%s + lay_t" % ly0, z0, z1)
        else:
            lb = (x0, x1, ly0, "%s + lay_t" % ly0, "%s + cart_t" % z0, "%s - cart_t" % z1)
        CB.box_body(comp, "LAYER %d %s" % (k + 1, tag), lb, ctx)
    # materials: casing aluminium, layers absorbent
    al = A.MATERIALS["al"]
    py = A.MATERIALS["pyro"]
    for mk, (name, density) in (("al", al), ("pyro", py)):
        if design.materials.itemByName(name) is None:
            lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
            m = design.materials.addByCopy(lib.materials.itemByName("Aluminum"), name)
            m.materialProperties.itemById("structural_Density").value = density
    for b in comp.bRepBodies:
        b.material = design.materials.itemByName(al[0] if b.name.startswith("CARTRIDGE") else py[0])
    return occ, comp


def run(_context):
    app = adsk.core.Application.get()
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
            b = CB.box_body(comp, name, lay[name][1], ctx)
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
        # ---- column: foot plate, faces, kick grille, plenum plates, fill, hub zone, angles, cartridge
        _o, col = new_comp(root, "column")
        for key in ("col_foot", "col_front", "col_left", "col_side_lo", "col_side_hi", "col_fill", "kick", "hub"):
            comp_with(col, key, names_of(key))
        _o2, ang = new_comp(col, "col_ang")
        for tag in ("FL", "FR", "BL"):
            x0, x1, y0, y1, z0, z1 = lay["COLUMN ANGLE %s" % tag][1]
            if tag == "FL":
                pts = [(x0, y1), (x1, y1), (x1, "%s - ang_t" % y1), ("%s + ang_t" % x0, "%s - ang_t" % y1),
                       ("%s + ang_t" % x0, y0), (x0, y0)]
            elif tag == "FR":
                pts = [(x0, y1), (x1, y1), (x1, y0), ("%s - ang_t" % x1, y0), ("%s - ang_t" % x1, "%s - ang_t" % y1),
                       (x0, "%s - ang_t" % y1)]
            else:
                pts = [(x0, y0), (x1, y0), (x1, "%s + ang_t" % y0), ("%s + ang_t" % x0, "%s + ang_t" % y0),
                       ("%s + ang_t" % x0, y1), (x0, y1)]
            made["COLUMN ANGLE %s" % tag] = (ang, poly_xy_extrude(ang, "COLUMN ANGLE %s" % tag, pts, z0, z1, ctx))
        set_material(design, ang, "col_ang")
        build_cartridge(col, design, ctx, lay["CARTRIDGE SUPPLY"][1], "z", "SUPPLY")
        print("step column done")
        # ---- soffit (ships with its exhaust fan box fitted, D-87): underside sections, face,
        #      rails, end plate, fill, grille, hanging and service hardware envelopes
        _o, sof = new_comp(root, "soffit")
        for key in ("sof_under", "sof_under_r", "sof_under_f", "sof_front", "sof_rail_d", "sof_rail_r", "sof_end",
                    "sof_fill", "egrille", "stud", "hinge", "latch"):
            comp_with(sof, key, names_of(key))
        lo = sof.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        lk = lo.component
        hp = A.HARDWARE["lock"]
        lk.name, lk.partNumber = "%s %s" % (hp[0], hp[1]), hp[0]
        lk.description = "%s | %s | PI | %s | captive retainer HOLD (joints register)" % (hp[1], hp[2], A.REV)
        for n in names_of("lock"):
            put(lk, n)
        set_material(design, lk, "riser")      # steel, as the riser
        build_cartridge(sof, design, ctx, lay["CARTRIDGE EXHAUST"][1], "x", "EXHAUST")
        print("step soffit done")
        # ---- fan boxes with their fans; the supply box joined with the riser and transitions (D-87)
        fan_comp = None
        fans = A.fan_points()
        boxes = {}
        for key, bname, parent in (("ebox", "EXHAUST FAN BOX", sof), ("sbox", "SUPPLY FAN BOX", root)):
            _o, fb = new_comp(parent, key)
            boxes[key] = fb
            _o2, casing = new_comp(fb, "box")
            b = put(casing, bname)
            hollow_closed(casing, b, bname)
            set_material(design, casing, "box")
            tag = "EXHAUST" if key == "ebox" else "SUPPLY"
            for fname, fx, fy, fz in [f for f in fans if f[0].startswith(tag)]:
                if fan_comp is None:
                    fo, fan_comp = new_comp(fb, "fan")
                    CB.box_body(fan_comp, "FAN 140 ENVELOPE", ("-fan_s / 2", "fan_s / 2", "-fan_s / 2", "fan_s / 2",
                                                                "0 mm", "fan_t"), ctx)
                    set_material(design, fan_comp, "fan")
                else:
                    fo = fb.occurrences.addExistingComponent(fan_comp, adsk.core.Matrix3D.create())
                CB.place(fb, fo, (fx, fy, fz), fname, ctx)
        for key, parent in (("trans", boxes["sbox"]), ("riser", boxes["sbox"]), ("rtrans", boxes["sbox"]),
                            ("sleeve", root), ("rgrille", root)):
            c = comp_with(parent, key, names_of(key))
            for n in names_of(key):
                if key == "riser":
                    hollow_axis(c, made[n][1], "z", "rs_t", n)
                if key == "sleeve":
                    hollow_axis(c, made[n][1], "z", "slv_t", n)
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
        off, worst = [], 0.0
        got = {}
        for n, b in bodies:
            got.setdefault(n.split("/")[-1], []).append(CB.body_box(b))
        for key, name, bx in A.layout():
            want = [A.ev(ctx.vals, e) for e in bx]
            want = [want[0], want[2], want[4], want[1], want[3], want[5]]
            have = got.get(name)
            if not have:
                off.append((name, "missing"))
                continue
            d = min(max(abs(p - q) for p, q in zip(h, want)) for h in have)
            worst = max(worst, d)
            if d > 0.05:
                off.append((name, round(d, 3)))
        print("position check: %d layout bodies, worst %.3f mm, off %s" % (len(A.layout()), worst, off or "none"))
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
        if not (into_active or ARGS.get("keep") == "1"):
            doc.close(False)
    if not ok:
        raise RuntimeError("build did not finish")
