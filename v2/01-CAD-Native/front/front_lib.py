"""Shared helpers for the FRONT build scripts (Spaceship / FocusPod v2).

Loaded by each FRONT build script with load_lib() (a fresh module object on
every run, so edits are never hidden by Fusion's module cache). Runs inside
Fusion through tools/fusion/run_script.py.

Rules built in (v2/00-Control/conventions.md, docs/engineering-guideline.md
section 4.4):
- Every size comes from the skeleton's own parameter list, read at build time
  from v2/01-CAD-Native/skeleton/100000_Pnn_POD-SKELETON-PARAMETERS.csv (the
  highest revision present). Nothing is copied by hand; the names stay the
  skeleton's names, so a skeleton change reaches every FRONT part on the next
  build.
- Every sketch is fully constrained by dimensions driven by parameter
  expressions, never by Fix. A loose sketch, an unhealthy timeline item or an
  unexpected clash raises, which fails the run.
- Pod coordinates per conventions section 4: origin on the room floor at the
  pod centre, +X right (seen from outside facing the door), +Y back, +Z up.
"""

import csv
import glob
import os
import re
import time

import adsk.core
import adsk.fusion

MM = 0.1   # Fusion's internal length unit is cm


# ---------------------------------------------------------------- parameters

def skeleton_csv(repo_root):
    """Path and revision of the newest skeleton parameter list."""
    pat = os.path.join(repo_root, "v2", "01-CAD-Native", "skeleton", "100000_P*_POD-SKELETON-PARAMETERS.csv")
    found = sorted(glob.glob(pat), key=lambda p: int(re.search(r"_P(\d+)_", p).group(1)))
    if not found:
        raise RuntimeError("no skeleton parameter list matches " + pat)
    path = found[-1]
    return path, "P%s" % re.search(r"_P(\d+)_", path).group(1)


def load_skeleton_params(repo_root):
    path, rev = skeleton_csv(repo_root)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # the list carries a unit column since skeleton v4 (#94): "-" marks a count, so it goes in without a unit
    params = [(r["parameter"], r["expression"], "" if (r.get("unit") or "mm").strip() in ("-", "") else "mm",
               "skeleton %s %s" % (rev, r["status"]), r["source"]) for r in rows]
    return params, path, rev


# Added by every FRONT build, after the skeleton's list.
LIB_PARAMS = [
    ("sk_ref", "5000 mm", "mm", "assumption",
     "sketch reference point offset: every sketch corner is dimensioned from a point at -sk_ref on both plane "
     "axes, so no dimension changes side when a corner crosses a pod centre line in an edit"),
]


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    """Value of an expression in mm."""
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def add_params(design, params):
    """params: [(name, expression, unit, status, source)]. Text values use unit 'Text'."""
    for name, expr, unit, status, src in params:
        if design.userParameters.itemByName(name):
            raise RuntimeError("parameter defined twice: " + name)
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        if p is None:
            raise RuntimeError("could not add parameter %s = %s" % (name, expr))


# ---------------------------------------------------------------- document

def clear_design(design):
    """Empty the active design for a clean rebuild: timeline, then parameters."""
    tl = design.timeline
    if tl.count:
        tl.moveToBeginning()
        tl.deleteAllAfterMarker()
    root = design.rootComponent
    for coll in (root.occurrences, root.bRepBodies, root.sketches, root.constructionPlanes):
        for i in range(coll.count - 1, -1, -1):
            coll.item(i).deleteMe()
    for _round in range(50):           # parameters that others depend on go last
        left = design.userParameters.count
        if not left:
            break
        for i in range(left - 1, -1, -1):
            p = design.userParameters.item(i)
            if not p.dependentParameters.count:
                p.deleteMe()
    if design.userParameters.count:
        raise RuntimeError("could not clear %d user parameters" % design.userParameters.count)


def start_design(app, part_number, description):
    """Use the active design (opened by the runner's --doc) and empty it."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("the active document is not a Fusion design")
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    clear_design(design)
    root = design.rootComponent
    root.partNumber = part_number
    root.description = description
    return design


def new_comp(parent, pn, name, vn, rev):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s | %s" % (name, vn, rev)
    return c


# ---------------------------------------------------------------- sketches

def _axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis ('x', 'y' or 'z') maps to."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[model_axis]
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*v))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def poly(design, comp, plane, plane_axes, fixed, name, pts):
    """Closed polygon on an origin plane, fully constrained.

    A reference point sits at -sk_ref on both plane axes (dimensioned from the
    sketch origin). Each corner is dimensioned from that point along both
    plane axes by "(its coordinate expression) + sk_ref", a distance that stays
    positive for any pod size, so no dimension flips side when a corner crosses
    one of the pod's centre lines during an edit (the skeleton's abs() from
    the origin does). Edges parallel to an axis get a horizontal or vertical
    constraint and one dimension per group of corners they join (never
    redundant). plane_axes: the two model axes in the plane, e.g. ("x", "z");
    fixed: the third coordinate on the plane, in mm. pts: [(expr_a, expr_b)].
    (Pattern of v2/01-CAD-Native/skeleton/pod_skeleton.py.)"""
    sk = comp.sketches.add(plane)
    sk.name = name
    third = ({"x", "y", "z"} - set(plane_axes)).pop()
    sp = []
    for ea, eb in pts:
        c = {plane_axes[0]: ev(design, ea), plane_axes[1]: ev(design, eb), third: fixed}
        sp.append(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
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
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    expr_on = {}
    for k, ax in enumerate(plane_axes):
        expr_on[_axis_of(sk, ax)] = k
    off = ev(design, "sk_ref")
    c = {plane_axes[0]: -off, plane_axes[1]: -off, third: fixed}
    ref = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    for sa in ("x", "y"):
        g = ref.geometry
        dims.addDistanceDimension(sk.originPoint, ref, H if sa == "x" else V,
                                  adsk.core.Point3D.create(g.x / 2, g.y / 2, 0)).parameter.expression = "sk_ref"
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
            ex = pts[i][expr_on[sa]]
            vp = verts[i]
            g = vp.geometry
            tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
            dims.addDistanceDimension(ref, vp, H if sa == "x" else V, tp).parameter.expression = \
                "(%s) + sk_ref" % ex
    if not sk.isFullyConstrained:
        info = ["v%d %s" % (i, "ok" if vp.isFullyConstrained else "LOOSE") for i, vp in enumerate(verts)]
        raise RuntimeError("sketch not fully constrained: %s | %s" % (name, " ".join(info)))
    return sk


def _normal_sign(sk, axis):
    n = sk.xDirection.crossProduct(sk.yDirection)
    return 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1


def extrude_span(comp, sk, axis, a_expr, b_expr, op, bodies=None, name="", profiles=None):
    """Extrude the sketch's profiles along a model axis from a to b (a < b)."""
    sign = _normal_sign(sk, axis)
    coll = adsk.core.ObjectCollection.create()
    for pr in (profiles if profiles is not None else sk.profiles):
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


def plane_of(comp, axes):
    return {("x", "y"): comp.xYConstructionPlane, ("x", "z"): comp.xZConstructionPlane,
            ("y", "z"): comp.yZConstructionPlane}[axes]


def prism(design, comp, code, axes, pts, along, a_expr, b_expr, body_name, sketch_name=None, feat_name=None):
    """New body: a fully constrained polygon on an origin plane, extruded along the third axis."""
    sk = poly(design, comp, plane_of(comp, axes), axes, 0, sketch_name or "SECTION - " + code, pts)
    f = extrude_span(comp, sk, along, a_expr, b_expr, adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                     name=feat_name or "EXTRUDE - " + code)
    if f.bodies.count != 1:
        raise RuntimeError("%s: extrude made %d bodies" % (code, f.bodies.count))
    b = f.bodies.item(0)
    b.name = body_name
    return b


def box_body(design, comp, code, xr, yr, zr, body_name, sketch_name=None):
    """Axis-aligned box from expression ranges: rectangle in plan, extruded in Z."""
    pts = [(xr[0], yr[0]), (xr[1], yr[0]), (xr[1], yr[1]), (xr[0], yr[1])]
    return prism(design, comp, code, ("x", "y"), pts, "z", zr[0], zr[1], body_name,
                 sketch_name or "PLAN - " + code, "EXTRUDE - " + code)


# ---------------------------------------------------------------- materials

def material(design, name, base, density):
    """A design material copied from the Fusion library with a set density (kg/m3)."""
    app = adsk.core.Application.get()
    m = _by_name(design.materials, name)
    if m is None:
        lib = app.materialLibraries.itemByName("Fusion Material Library")
        src = _by_name(lib.materials, base) or _by_name(lib.materials, "Aluminum")
        m = design.materials.addByCopy(src, name)
    m.materialProperties.itemById("structural_Density").value = density
    return m


def appearance(design, names):
    """First appearance found in the Fusion Appearance Library, copied into the design."""
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    for nm in names:
        a = _by_name(design.appearances, nm)
        if a:
            return a
        src = _by_name(lib.appearances, nm) if lib else None
        if src:
            return design.appearances.addByCopy(src, nm)
    return None


def _by_name(coll, name):
    """itemByName that returns None instead of raising 'invalid name'."""
    try:
        return coll.itemByName(name)
    except RuntimeError:
        return None


# ---------------------------------------------------------------- checks

def box(entity):
    b = entity.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def clash_check(bodies, expected):
    """Pairwise solid intersections over 1 mm3; any pair not in expected is a failure."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    allowed = {frozenset(k) for k, _r in expected}
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
                    bb = t1.boundingBox
                    print("OVERLAP|%s|%s|%d mm3|box %s" % (a, b, round(vol), [round(v * 10, 2) for v in (
                        bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]))
    return hits, bad


def health(design):
    tl = design.timeline
    bad = ["%s: %s" % (tl.item(i).name, tl.item(i).errorOrWarningMessage) for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    return tl.count, bad, loose


def comp_mass(comp):
    return comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy).mass


# ---------------------------------------------------------------- exports

def save_new_version(app, doc, name, folder_name, description):
    """First save into Default Project / folder_name; later runs save a new version."""
    if doc.isSaved and doc.dataFile and doc.name.split(" v")[0] == name:
        return doc.save(description)
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    app.data.activeProject = proj
    folder = proj.rootFolder.dataFolders.itemByName(folder_name)
    if any(df.name == name for df in folder.dataFiles):
        raise RuntimeError("%s already in %s but the active document is not it" % (name, folder_name))
    return doc.saveAs(name, folder, description, "")


def export(design, root_dir, rel, kind):
    """kind 'f3d' or 'step'; retried because right after a save Fusion may still be uploading."""
    em = design.exportManager
    mk = {"f3d": em.createFusionArchiveExportOptions, "step": em.createSTEPExportOptions}[kind]
    path = os.path.join(root_dir, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ok = False
    for _try in range(10):
        ok = em.execute(mk(path, design.rootComponent))
        if ok and os.path.getsize(path) > 2000:
            break
        ok = False
        adsk.doEvents()
        time.sleep(3)
    if not ok:
        raise RuntimeError("export failed: " + rel)
    return path


def write_dxf_polyline(path, loops, layer="CUT"):
    """Minimal DXF (R12 entities, mm, 1:1): each loop is a closed list of (x, y) in mm.

    $INSUNITS = 4 (millimetres). Lines only, so every CAM reader takes it."""
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "9", "$MEASUREMENT", "70", "1",
           "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for loop in loops:
        for i in range(len(loop)):
            (x0, y0), (x1, y1) = loop[i], loop[(i + 1) % len(loop)]
            out += ["0", "LINE", "8", layer, "10", "%.4f" % x0, "20", "%.4f" % y0, "30", "0.0",
                    "11", "%.4f" % x1, "21", "%.4f" % y1, "31", "0.0"]
    out += ["0", "ENDSEC", "0", "EOF"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii") as f:
        f.write("\n".join(out) + "\n")


# ---------------------------------------------------------------- export package (parts list, anchors, STEP re-read)

# FRONT's bought items as the joints register names them (section 2.1, H-15 to H-24), so the master BOM sees one
# name per number, with maker and SKU where the product is named (HOLD items have none yet)
REGISTER_ITEMS = {
    "368001": ("FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112", "Ron chân cửa tự động", "athmer", "Schall-Ex GSA 1-1112"),
    "368002": ("FRONT - GLAZING U-SEAL - BOHLE BO5201735", "Gioăng chữ U silicone", "Bohle", "BO5201735"),
    "368003": ("FRONT - 180 MAGNETIC SEAL - HALF 1 OF 2 - HOLD", "Gioăng từ 180° (nửa 1)", "", ""),
    "368004": ("FRONT - GLAZING U-PROFILE - BOHLE BO5201571", "Thanh U nhôm kẹp kính", "Bohle", "BO5201571"),
    "368005": ("FRONT - FRAME-STOP SEAL", "Gioăng chặn khung cửa", "athmer", "PS 1515 P Flex"),
    "368006": ("FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD", "Gioăng từ 180° (nửa 2)", "", ""),
    "368007": ("FRONT - DOOR CATCH - IN DT", "Nam châm hít cửa (trong khối DT)", "Sugatsune", "HT-MSG62"),
    "368101": ("FRONT - DOOR HINGE - HOLD", "Bản lề cửa kính", "", ""),
    "368102": ("FRONT - DOOR STRIKE", "Đế hít cửa", "Sugatsune", "HT-MSG62-U10"),
    "368103": ("FRONT - DOOR PULL PAIR - HOLD", "Tay nắm cửa (cặp)", "", ""),
    "618401": ("AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V", "Noctua", "NF-A14 industrialPPC-3000 PWM"),
}


def write_parts_list(design, path, rows, root_pn, root_name, root_vn):
    """rows: [(pn, name, vn, qty, type, material, mass, mass_status, status, source, note)];
    mass "cad" = the component's mass from the model; the root row's mass is the sum of the others.
    Every non-root part number must exist in the CAD with that many components, named 'PN NAME…'."""
    by_pn = {}
    for c in design.allComponents:
        if c.partNumber and c != design.rootComponent:
            by_pn.setdefault(c.partNumber, []).append(c)
    out = []
    for pn, name, vn, qty, typ, mat, mass, mstat, status, src, note in rows:
        if pn == root_pn:
            out.append([pn, root_name, root_vn, typ, mat, qty, "", mstat, status, src, note, "", ""])
            continue
        comps = by_pn.get(pn, [])
        if len(comps) != (qty if isinstance(qty, int) else 1):
            raise RuntimeError("%s: %d components in CAD, parts list says %s" % (pn, len(comps), qty))
        if not comps[0].name.startswith("%s %s" % (pn, name)):
            raise RuntimeError("%s: CAD name %r does not start with %r" % (pn, comps[0].name, name))
        if mass == "cad":
            mass = round(comp_mass(comps[0]), 3)
        if mass is None:              # a sub-assembly row: its parts carry the mass
            mass, mstat = "", mstat or "sum of its parts (rows below)"
        maker = sku = ""
        if pn in REGISTER_ITEMS:      # the register's name (the CAD name was checked above), maker and SKU
            name, vn, maker, sku = REGISTER_ITEMS[pn]
        out.append([pn, name, vn, typ, mat, qty, mass, mstat, status, src, note, maker, sku])
    total = sum((r[5] if isinstance(r[5], int) else 1) * r[6] for r in out if r[0] != root_pn and r[6] != "")
    for r in out:
        if r[0] == root_pn:
            r[6] = round(total, 2)
            r[7] = "calculation (sum of the rows below)"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part_number", "name", "name_vi", "type", "material", "qty", "unit_mass_kg", "mass_status",
                    "status", "source", "note", "maker", "sku"])
        w.writerows(out)
    return total


def step_reread(app, doc, design, step_path):
    imp = app.importManager
    before = box(design.rootComponent)
    sdoc = imp.importToNewDocument(imp.createSTEPImportOptions(step_path))
    sdes = adsk.fusion.Design.cast(sdoc.products.itemByProductType("DesignProductType"))
    after = box(sdes.rootComponent)
    sdoc.close(False)
    doc.activate()
    return before, after, max(abs(a - b) for a, b in zip(before, after))


def ensure_saved_part_number(doc, design, pn):
    """Fusion stamps a new document's root part number on its first save (seen 2026-10-31:
    '2026-10-31-21-54-47-400'); set it back and save a new version, so the exports carry the
    real part number."""
    if design.rootComponent.partNumber != pn:
        design.rootComponent.partNumber = pn
        if not doc.save("root part number %s" % pn):
            raise RuntimeError("save after setting the part number failed")
        for _i in range(20):
            adsk.doEvents()
            if design.rootComponent.partNumber == pn and not doc.isModified:
                break
            time.sleep(1)
    if design.rootComponent.partNumber != pn or not doc.isSaved:
        raise RuntimeError("root part number %r, saved %s" % (design.rootComponent.partNumber, doc.isSaved))


# ---------------------------------------------------------------- the glass lines shared by the fixed pane, DR and DT
# The fixed pane's visible lines (PM rulings 2026-10-31): bottom = the base band top (wall_z0); right edge = the
# skeleton line from the bottom-right corner to the knee; diagonal = the skeleton's DR inner edge from the knee to
# (-pod_w/2 + fix_xtr, dt_zb), DT's underside at the top; free edge = the door's latch edge pushed fg_gap toward the
# pane. DR's inner edge is the right edge and the diagonal, so DR, DT and the pane share these parameters.

GLASS_PARAMS = [
    ("fg_vis_zb", "wall_z0", "mm", "calculation",
     "visible bottom of the fixed pane = the base band top (DL and DR stop there too, PM ruling 2026-10-31)"),
    ("fg_vis_zt", "dt_zb", "mm", "calculation", "visible top of the fixed pane = DT's underside"),
    ("fg_gap", "glass_gap", "mm", "calculation",
     "= the skeleton's glass_gap: the pane's free edge runs parallel to the door's latch edge, 4 mm off (PM ruling "
     "2026-10-31; the skeleton's fix_xbl and fix_xtl follow the same rule since its update #58)"),
    ("gu_prof_w", "15 mm", "mm", "source", "Bohle BO5201571 aluminium U-profile 15 x 15 x 1.5 (hardware selection C5)"),
    ("gu_prof_d", "15 mm", "mm", "source", "as gu_prof_w"),
    ("gu_prof_t", "1.5 mm", "mm", "source", "as gu_prof_w"),
    ("gu_w", "gu_prof_w - 2 * gu_prof_t", "mm", "calculation", "inner width of the U-profile = the U-seal's outer width"),
    ("gu_base", "2 mm", "mm", "assumption", "U-seal base under the glass edge; HOLD for Bohle's BO5201735 section drawing"),
    ("gu_in_d", "gu_prof_d - gu_prof_t", "mm", "calculation", "inner depth of the U-profile"),
    ("fg_bite", "gu_in_d - gu_base", "mm", "calculation",
     "glass cover in the hidden channels, 11.5 (PM ruling 2026-10-31); HOLD for the glass supplier's minimum"),
    ("fg_r_len", "sqrt((fix_xbr - fix_xk) * (fix_xbr - fix_xk) + (fix_zk - fix_zb) * (fix_zk - fix_zb))", "mm",
     "calculation", "length of the skeleton's right edge (bottom-right corner to the knee)"),
    ("fg_rnx", "(fix_zk - fix_zb) / fg_r_len", "", "calculation", "right edge outward normal, X"),
    ("fg_rnz", "(fix_xk - fix_xbr) / fg_r_len", "", "calculation", "right edge outward normal, Z"),
    ("fg_rc", "fg_rnx * (pod_w / 2 - fix_xbr) + fg_rnz * fix_zb", "mm", "calculation", "right edge line constant"),
    ("fg_d_len", "sqrt((pod_w - fix_xtr - fix_xk) * (pod_w - fix_xtr - fix_xk) + (dt_zb - fix_zk) * (dt_zb - fix_zk))",
     "mm", "calculation", "length of DR's diagonal inner edge (knee to DT's underside at X -pod_w/2 + fix_xtr)"),
    ("fg_dnx", "(dt_zb - fix_zk) / fg_d_len", "", "calculation", "diagonal outward normal, X"),
    ("fg_dnz", "(pod_w - fix_xtr - fix_xk) / fg_d_len", "", "calculation", "diagonal outward normal, Z"),
    ("fg_dc", "fg_dnx * (pod_w / 2 - fix_xk) + fg_dnz * fix_zk", "mm", "calculation", "diagonal line constant"),
    ("fg_det", "fg_rnx * fg_dnz - fg_rnz * fg_dnx", "", "calculation", "for the knee corner"),
    ("fg_l_len", "sqrt((door_xbr - door_xtr) * (door_xbr - door_xtr) + (door_zt - door_zb) * (door_zt - door_zb))",
     "mm", "calculation", "length of the door's latch edge"),
    ("fg_lnx", "(door_zt - door_zb) / fg_l_len", "", "calculation", "door latch edge normal toward the pane, X"),
    ("fg_lnz", "(door_xbr - door_xtr) / fg_l_len", "", "calculation", "door latch edge normal toward the pane, Z"),
    ("fg_lc", "fg_lnx * (-pod_w / 2 + door_xbr) + fg_lnz * door_zb", "mm", "calculation", "door latch edge line constant"),
]


def door_x(z):
    """X of the door's latch edge line at height z."""
    return "((fg_lc - fg_lnz * (%s)) / fg_lnx)" % z


def free_x(z):
    """X of the fixed pane's free edge at height z (fg_gap from the door's latch edge)."""
    return "((fg_lc + fg_gap - fg_lnz * (%s)) / fg_lnx)" % z


def right_x(z, d="0 mm"):
    """X of the right edge line pushed out by d, at height z."""
    return "((fg_rc + %s - fg_rnz * (%s)) / fg_rnx)" % (d, z)


def diag_x(z, d="0 mm"):
    """X of the diagonal line pushed out by d, at height z."""
    return "((fg_dc + %s - fg_dnz * (%s)) / fg_dnx)" % (d, z)


def g_BL(d):
    z = "(fg_vis_zb - %s)" % d
    return (free_x(z), z)


def g_BR(d):
    z = "(fg_vis_zb - %s)" % d
    return (right_x(z, d), z)


def g_K(d):
    return ("(((fg_rc + %s) * fg_dnz - (fg_dc + %s) * fg_rnz) / fg_det)" % (d, d),
            "((fg_rnx * (fg_dc + %s) - fg_dnx * (fg_rc + %s)) / fg_det)" % (d, d))


def g_TR(d):
    z = "(fg_vis_zt + %s)" % d
    return (diag_x(z, d), z)


def g_TL(d):
    z = "(fg_vis_zt + %s)" % d
    return (free_x(z), z)


def g_outline(d):
    """The fixed pane's visible outline with its four held edges pushed out by d."""
    return [g_BL(d), g_BR(d), g_K(d), g_TR(d), g_TL(d)]


def g_band(d):
    """C-shaped band between the visible outline and offset d, open along the free edge."""
    return g_outline("0 mm") + [g_TL(d), g_TR(d), g_K(d), g_BR(d), g_BL(d)]


def circles(design, comp, plane, plane_axes, fixed, name, centers, dia_expr):
    """Circles on an origin plane, fully constrained: each centre dimensioned from the -sk_ref reference point along
    both plane axes by "(coordinate expression) + sk_ref", each diameter by dia_expr. Returns the sketch."""
    sk = comp.sketches.add(plane)
    sk.name = name
    third = ({"x", "y", "z"} - set(plane_axes)).pop()
    expr_on = {}
    for k, ax in enumerate(plane_axes):
        expr_on[_axis_of(sk, ax)] = k
    dims = sk.sketchDimensions
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    off = ev(design, "sk_ref")
    c = {plane_axes[0]: -off, plane_axes[1]: -off, third: fixed}
    ref = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    for sa in ("x", "y"):
        g = ref.geometry
        dims.addDistanceDimension(sk.originPoint, ref, H if sa == "x" else V,
                                  adsk.core.Point3D.create(g.x / 2, g.y / 2, 0)).parameter.expression = "sk_ref"
    r = ev(design, dia_expr) / 2
    for ea, eb in centers:
        c = {plane_axes[0]: ev(design, ea), plane_axes[1]: ev(design, eb), third: fixed}
        p = sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM))
        circ = sk.sketchCurves.sketchCircles.addByCenterRadius(p, r * MM)
        cp = circ.centerSketchPoint
        for sa in ("x", "y"):
            ex = (ea, eb)[expr_on[sa]]
            g = cp.geometry
            dims.addDistanceDimension(ref, cp, H if sa == "x" else V,
                                      adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)).parameter.expression = \
                "(%s) + sk_ref" % ex
        dims.addDiameterDimension(circ, adsk.core.Point3D.create(p.x + r * MM, p.y + r * MM, 0)).parameter.expression = dia_expr
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + name)
    return sk


# J-FRONT-01 (joints register 3.7): decor block to side wall, 3 bolts per side panel on the panel's front member
# centre line, the end bolts bolt_edge_inset from each panel end; the rivnuts sit in the decor's aluminium back plate
JF_PARAMS = [
    ("jf_x", "pod_w / 2 - skin_t - bond_t - frame_t / 2", "mm", "calculation",
     "joints register J-FRONT-01: the side panel's front member centre line, X -/+1224 (skin, bond line and half the "
     "40 frame in from the outside, skeleton named values)"),
    ("jf_hole", "9.53 mm", "mm", "source", "rivnut 838003 (Sherex CAH3-610-4.2) hole 9.53 +0.10/0 (hardware selection A5; joints register H-03)"),
    ("jf_z1", "panel_z0 + bolt_edge_inset", "mm", "calculation", "lower panel, bottom bolt (220 rule)"),
    ("jf_z2", "panel_z0 + side_h / 2", "mm", "calculation", "lower panel, middle bolt"),
    ("jf_z3", "panel_z0 + side_h - bolt_edge_inset", "mm", "calculation", "lower panel, top bolt"),
    ("jf_z4", "panel_z0 + side_h + seam_gap + bolt_edge_inset", "mm", "calculation", "upper panel, bottom bolt"),
    ("jf_z5", "panel_z0 + side_h + seam_gap + side_h / 2", "mm", "calculation", "upper panel, middle bolt"),
    ("jf_z6", "panel_z0 + 2 * side_h + seam_gap - bolt_edge_inset", "mm", "calculation", "upper panel, top bolt"),
]


# ---------------------------------------------------------------- ACP skin panels laid flat
def skin_panels(body, probe_mm=60.0):
    """The skin's outside faces as flat panels: [(name, area_mm2, [loop, ...])] with each loop a list of (u, v) in mm.

    The skin is a shell, so each planar outside face is one ACP panel, joined to its neighbours with 45 degree mitred
    edges as in v1 ("ghép mí 45°"); the panel's outline is the face's outline on the outside surface. A face is on the
    outside when a short ray along its outward normal does not hit the skin again (an inside face looks across the
    hollow at the opposite wall). u runs along the face's longest outer edge, v square to it, origin at its corner."""
    import math
    root = body.parentComponent
    out = []
    for i, fc in enumerate(body.faces):
        if fc.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            continue
        p = fc.pointOnFace
        _ok, n = fc.evaluator.getNormalAtPoint(p)
        o = adsk.core.Point3D.create(p.x + n.x * 0.01, p.y + n.y * 0.01, p.z + n.z * 0.01)
        hp = adsk.core.ObjectCollection.create()
        hits = root.findBRepUsingRay(o, n, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
        again = []
        for k in range(hits.count if hits else 0):
            h, q = hits.item(k), hp.item(k) if k < hp.count else None
            if h.body == body and h != fc and q is not None and q.distanceTo(o) * 10 < probe_mm:
                again.append(h)
        if again:
            continue
        loops = []
        edge0 = None
        for lp in fc.loops:
            pts = []
            for coedge in lp.coEdges:
                e = coedge.edge
                a, b = (e.startVertex.geometry, e.endVertex.geometry) if not coedge.isOpposedToEdge else \
                       (e.endVertex.geometry, e.startVertex.geometry)
                pts.append(a)
                if lp.isOuter and (edge0 is None or e.length > edge0[2]):
                    edge0 = (a, b, e.length)
            loops.append((lp.isOuter, pts))
        a, b, _l = edge0
        ux = adsk.core.Vector3D.create(b.x - a.x, b.y - a.y, b.z - a.z)
        ux.normalize()
        vy = n.crossProduct(ux)
        vy.normalize()
        flat = []
        for outer, pts in sorted(loops, key=lambda t: not t[0]):
            flat.append([((q.x - a.x) * ux.x + (q.y - a.y) * ux.y + (q.z - a.z) * ux.z,
                          (q.x - a.x) * vy.x + (q.y - a.y) * vy.y + (q.z - a.z) * vy.z) for q in pts])
        flat = [[(u * 10.0, v * 10.0) for u, v in lp] for lp in flat]
        out.append(("F%02d" % (i + 1), fc.area * 100.0, flat, (round(n.x, 3), round(n.y, 3), round(n.z, 3))))
    return out


def write_panels_dxf(path, panels, gap=60.0, row_w=3000.0):
    """All panels side by side on layer CUT, each with a TEXT label on layer MARK (name, size, outward normal)."""
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "9", "$MEASUREMENT", "70", "1",
           "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    x0 = y0 = 0.0
    row_h = 0.0
    placed = []
    for name, area, loops, nrm in panels:
        us = [u for lp in loops for u, _v in lp]
        vs = [v for lp in loops for _u, v in lp]
        w, h = max(us) - min(us), max(vs) - min(vs)
        if x0 > 0 and x0 + w > row_w:
            x0, y0, row_h = 0.0, y0 + row_h + gap * 2, 0.0
        dx, dy = x0 - min(us), y0 - min(vs)
        for lp in loops:
            for i in range(len(lp)):
                (a, b), (c, d) = lp[i], lp[(i + 1) % len(lp)]
                out += ["0", "LINE", "8", "CUT", "10", "%.3f" % (a + dx), "20", "%.3f" % (b + dy), "30", "0.0",
                        "11", "%.3f" % (c + dx), "21", "%.3f" % (d + dy), "31", "0.0"]
        label = "%s %.0f x %.0f n%s" % (name, w, h, nrm)
        out += ["0", "TEXT", "8", "MARK", "10", "%.3f" % x0, "20", "%.3f" % (y0 - 25.0), "30", "0.0", "40", "15.0",
                "1", label]
        placed.append((name, round(w, 1), round(h, 1), round(area / 1e6, 4)))
        x0 += w + gap
        row_h = max(row_h, h)
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(out) + "\n")
    return placed


# ---- one Fusion run per design (PM fair-share rule 2026-11-01): build, save, export, pictures and the edit test
# in the same run, so each team keeps at most 3 runs in the queue

VIEWS = {"front": "FrontViewOrientation", "top": "TopViewOrientation", "left": "LeftViewOrientation",
         "right": "RightViewOrientation", "iso-top-right": "IsoTopRightViewOrientation"}


def save_doc(app, desc):
    """Save the active document as a new version (it was saved once when the runner made it)."""
    doc = app.activeDocument
    if not doc.save(desc):
        raise RuntimeError("could not save %r" % doc.name)
    print("saved %r: %s" % (doc.name, desc))


def take_shots(app, root_dir, doc, shots, size=(1600, 1000)):
    """Pictures of a design: shots = [(repo-relative .png, view name in VIEWS)]."""
    doc.activate()
    adsk.doEvents()
    vp = app.activeViewport
    for rel, view in shots:
        cam = vp.camera
        cam.viewOrientation = getattr(adsk.core.ViewOrientations, VIEWS[view])
        cam.isFitView = True
        cam.isSmoothTransition = False
        vp.camera = cam
        vp.fit()
        vp.refresh()
        adsk.doEvents()
        path = os.path.join(root_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not vp.saveAsImageFile(path, size[0], size[1]):
            raise RuntimeError("picture failed: " + rel)
        print("picture %s (%s)" % (rel, view))


def load_sibling(here, filename, modname):
    """Load another script in this folder as a module (its run() is not called)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(modname, os.path.join(here, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_steps(app, args, here, step, build_fn, export_fn, shots, anchors_rel=None):
    """step build | export | post (export, pictures, edit test) | all (build, save, post).
    The edit test runs when args has "edits" (skeleton edits "name=value;..."), on a copy of the exported f3d."""
    doc = app.activeDocument
    if step in ("build", "all"):
        build_fn(app)
    if step == "all":
        save_doc(app, args.get("desc", "P01 build"))
    if step in ("export", "post", "all"):
        export_fn(app)
    if step in ("post", "all"):
        take_shots(app, args["repo_root"], doc, shots)
        if args.get("edits"):
            et = load_sibling(here, "edit_test_front.py", "edit_test_front_run")
            et.test(app, args["repo_root"], anchors_rel, args["edits"])
            doc.activate()
        if doc.isModified:           # the part number stamp or the view: keep it, so --close needs no --discard
            doc.activate()
            save_doc(app, "P01 after the export")
    if step not in ("build", "export", "post", "all"):
        raise RuntimeError("unknown step " + step)
