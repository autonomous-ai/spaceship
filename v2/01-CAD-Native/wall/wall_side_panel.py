"""Spaceship (FocusPod v2) WALL: one side wall panel and its lining cassette.

Native, parameter-driven Fusion design, built by script into the ACTIVE
document (open your own document first, for example with the runner's
--doc-new NAME). One run builds one document:

    part=panel     the outer panel assembly: frame, ACP skin, PET fill
    part=cassette  the lining cassette: steel tray, felt, clip zones (HOLD)

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_side_panel.py \
        --doc-new 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD \
        --arg part=panel --arg side=L --arg row=1 --save "build P01" --close

Options (--arg KEY=VALUE):
    part=panel|cassette   which document to build (default panel)
    side=L|R              left (-X) or right (+X) wall, seen from outside facing the door
    row=1|2               lower (1) or upper (2) panel
    stop_after=N          stop after step N, for step-by-step checks
    rebuild=1             empty the active design first (only a design this script built:
                          its root part number must be the one this run builds)
    skeleton=NAME         skeleton cloud file to derive from (default 100000_P04_POD-SKELETON_CAD)
    link=derive|parse     how the skeleton parameters come in (default derive)

Coordinates: the pod system of conventions.md section 4 (origin on the room
floor at the pod centre, +X right, +Y back, +Z up), the same as skeleton P03,
so every part sits where it goes in the pod and the WALL and GA assemblies
insert these designs without a transform.

Parameters: the skeleton is the single source of the pod sizes. The design
links to the saved skeleton (cloud file `skeleton`, default
100000_P04_POD-SKELETON_CAD) with Fusion's Derive: every skeleton parameter
arrives as <name>_Ref and follows each new skeleton version
(Document.updateAllReferences). The wall then adds one alias per skeleton name
it uses (side_h = side_h_Ref, ...) so its own expressions read plainly, and its
own parameters below. Inside Fusion, change an alias (side_h, wall_depth) and
every body follows (edit test, edit_test_wall.py). link=parse instead copies
the values from pod_skeleton.py's PARAMS (offline tests and emergencies only).

Every sketch is fully constrained (the run fails otherwise), every feature,
body and sketch is named by its function, and each part is its own component
with its part number (conventions.md section 6, DECIDED by the PM).
"""

import ast
import math
import os
import re

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REV = "P01"
PART = ARGS.get("part", "panel")
SIDE = ARGS.get("side", "L").upper()
ROW = int(ARGS.get("row", "1"))
STOP_AFTER = int(ARGS.get("stop_after", "99"))
S = -1 if SIDE == "L" else 1          # sign of X for this side
SKELETON_REL = "v2/01-CAD-Native/skeleton/pod_skeleton.py"
MM = 0.1                               # Fusion API lengths are cm

if SIDE not in ("L", "R") or ROW not in (1, 2) or PART not in ("panel", "cassette"):
    raise ValueError("side must be L or R, row 1 or 2, part panel or cassette")

# ---------------------------------------------------------------- part numbers and names

POS = {("L", 1): 1, ("R", 1): 2, ("L", 2): 3, ("R", 2): 4}[(SIDE, ROW)]
CODE = "%s%d" % (SIDE, ROW)            # position code, conventions.md section 4
HAND = "LH" if SIDE == "L" else "RH"
LEVEL = "LOWER" if ROW == 1 else "UPPER"
VN_SIDE = "Vách trái" if SIDE == "L" else "Vách phải"
VN_LEVEL = "dưới" if ROW == 1 else "trên"

# key: (part number, English name, Vietnamese name). Numbers follow conventions.md
# section 6: WALL 21 (assemblies 0001-0999, made parts 1000-7999), LINING 51.
# Status: confirmed (PM ruling in the WALL group, 2026-10-31: numbers per
# conventions section 6, checked against D-28's reserved list).
PARTS = {
    "assy": ("2101%02d" % POS, "WALL - PANEL ASSY - SIDE %s - %s" % (LEVEL, HAND),
             "%s - cụm tấm %s" % (VN_SIDE, VN_LEVEL)),
    "frame": ("2111%02d" % POS, "WALL - PANEL FRAME - SIDE %s - %s" % (LEVEL, HAND),
              "%s - khung %s" % (VN_SIDE, VN_LEVEL)),
    "skin": ("2113%02d" % POS, "WALL - SKIN - SIDE %s - %s" % (LEVEL, HAND),
             "%s - tấm ốp alu %s" % (VN_SIDE, VN_LEVEL)),
    "fill": ("2115%02d" % POS, "WALL - CAVITY FILL - SIDE %s - %s" % (LEVEL, HAND),
             "%s - bông PET %s" % (VN_SIDE, VN_LEVEL)),
    "cass": ("5101%02d" % POS, "LINING - CASSETTE - SIDE %s - %s" % (LEVEL, HAND),
             "Cassette lót %s %s (khay thép + tấm tiêu âm)" % (VN_SIDE.lower(), VN_LEVEL)),
    "tray": ("5111%02d" % POS, "LINING - TRAY - SIDE %s - %s" % (LEVEL, HAND),
             "Khay thép lót %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "felt": ("5113%02d" % POS, "LINING - FELT - SIDE %s - %s" % (LEVEL, HAND),
             "Tấm tiêu âm %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "clip": ("NO-PN-HOLD-H03", "HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED)",
             "Vùng dành cho kẹp treo cassette (HOLD)"),
}
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005",
            "350011", "830001", "830005"}          # D-28
for _k, (_pn, _n, _v) in PARTS.items():
    if _pn in RESERVED:
        raise RuntimeError("reserved part number %s (D-28)" % _pn)
ROOT_KEY = "assy" if PART == "panel" else "cass"
DOC_NAME = "%s_%s_%s_CAD" % (PARTS[ROOT_KEY][0], REV, re.sub(r"[^A-Z0-9]+", "-", PARTS[ROOT_KEY][1]).strip("-"))

# ---------------------------------------------------------------- wall parameters

# name, expression, unit, status, source. A parameter may use any skeleton
# parameter and the ones above it. Statuses per conventions.md section 9.
WALL_PARAMS = [
    # outer panel
    ("skin_t", "3 mm", "mm", "source", "HW-SEL A1: Alcorest ACP 3 mm x 0.21 mm skins, EV3038 (plan VT01); D-12 colour"),
    ("tube_w", "20 mm", "mm", "confirmed",
     "D-34, D-54: aluminium tube 20 x 40 x 1.2; the 20 mm face carries the skin, so the 40 mm runs through the "
     "wall (outer_t = ACP 3 + frame 40). The joint register may turn it for the bond width (HOLD)"),
    ("bond_t", "3 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (outer panel 46 = ACP 3 + bond 3 + frame 40): SikaTack Panel-50 joint 12 x 3, the fixing tape "
     "sets 3 mm (bond spec, PR #23)"),
    ("tube_d", "outer_t - skin_t - bond_t", "mm", "calculation", "frame depth = outer panel 46 - skin 3 - bond 3 = 40 (D-34)"),
    ("tube_t", "1.2 mm", "mm", "confirmed", "D-34, D-54: wall 1.2 mm (rivnut grip check passed)"),
    ("stile_pitch_max", "400 mm", "mm", "confirmed", "D-16, D-34: members 400 mm apart or less, to keep the ACP flat"),
    ("pnl_len", "wall_depth - seam_gap", "mm", "calculation",
     "D-49 depth 1495 less the 2.26 gap at the decor back plate (PM ruling on F-008): 1492.74"),
    ("pnl_h", "side_h", "mm", "calculation", "skeleton side_h: 2 sheets per side wall (D-23) with the seam gaps"),
    ("skin_ret", "outer_t - skin_t", "mm", "assumption",
     "back return of the side skin: covers the frame's back end at the corner, where the side skin covers the back "
     "panel's edge (D-55; sample drawing D04). V-groove and fold per the ACP maker (HOLD H16)"),
    ("skin_setback", "0 mm", "mm", "assumption",
     "skin edge set back from the frame's top and bottom edges: 0, so the outside reveal equals the 2.26 seam gap "
     "(D-23: crisp, aligned reveals; joints register 2.8 leaves the setback to the WALL drawing)"),
    ("frm_len", "pnl_len - skin_t", "mm", "calculation", "the frame stops at the inside of the skin's back return"),
    ("frm_h", "pnl_h", "mm", "assumption",
     "the frame fills the skeleton envelope height; seam and base gasket gaps are set by the joint register (HOLD)"),
    ("corner_w", "40 mm", "mm", "confirmed",
     "the side panel's back member is 40 x 40 x 1.2 (PM ruling on the joints register, item 3, 2026-10-31; "
     "register F2, FR-06): the back corner joint needs a 37+ mm overlap for the rivnut and the bolt"),
    ("stile_n_mid", "ceil((frm_len - tube_w / 2 - corner_w / 2) / stile_pitch_max) - 1", "", "calculation",
     "intermediate stiles so that no stile pitch (centre to centre) exceeds stile_pitch_max"),
    ("stile_pitch", "(frm_len - tube_w / 2 - corner_w / 2) / (stile_n_mid + 1)", "mm", "calculation",
     "equal stile pitch, centre to centre, from the front stile to the 40 mm back stile"),
    ("stile_len", "frm_h - 2 * tube_w", "mm", "calculation", "stiles fit between the full-length rails (butt joints)"),
    ("fill_t", "tube_d", "mm", "calculation", "40 mm PET fill fills the frame depth (D-34; layout study 40 mm)"),
    # site joints, joints register V2-ENG-JNT-01 P01 (ce1f415): M6 x 20 ISO 4762 captive bolts into Sherex
    # CAH3-610-4.2 rivnuts, bolts and corner members DECIDED by the PM (2026-10-31); positions PROPOSED there
    ("bolt_d", "7 mm", "mm", "confirmed", "PM ruling on F-009: bolt holes 7.0 (0.51 float), position tolerance "
     "0.4 (+-0.2) from the spigot hole, CNC or drill jig (joints register FR-02)"),
    ("access_d", "11 mm", "mm", "calculation", "register FR-03: passes the M6 ISO 4762 head (10 max) and the 5 mm key"),
    ("rivnut_d", "9.53 mm", "mm", "source", "Sherex CAH3-610-4.2 hole 9.53 +0.10 (HW-SEL A5; register H-03)"),
    ("spigot_d", "8.5 mm", "mm", "assumption", "register FR-05: hole for the 8 mm locating spigot H-05"),
    ("spigot_slot", "14 mm", "mm", "assumption", "register FR-05: slot length for the second spigot"),
    ("spigot_edge", "100 mm", "mm", "assumption", "register FR-04: spigots about 100 from each end of the joint"),
    ("jnt_edge", "100 mm", "mm", "assumption", "register J-WALL-02, J-FRONT-01: end bolts 100 from each end"),
    ("n_side_jnt", "3", "", "source", "register J-WALL-02, J-FRONT-01: 3 bolts per panel height"),
    ("side_jnt_pitch", "(pnl_h - 2 * jnt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "equal pitch of the 3 bolts up the corner and decor joints"),
    ("pocket_w", "60 mm", "mm", "assumption", "register FR-10: fill left out 60 x 60 next to each bolt for the key"),
    ("base_bolt_edge", "220 mm", "mm", "source",
     "J-BASE-01 band rivnuts: the end ones 220 in from the panel ends, even pitch (BASE Engineer, 2026-10-31; the PM "
     "ruled the positions stand)"),
    ("n_base_bolt", "4", "", "source", "J-BASE-01: 4 bolts per side panel (BASE Engineer; joints register 3.3)"),
    ("base_bolt_pitch", "(pnl_len - 2 * base_bolt_edge) / (n_base_bolt - 1)", "mm", "calculation",
     "even pitch of the J-BASE-01 bolts"),
    # lining cassette
    ("felt_t", "9 mm", "mm", "source", "plan VT03-PET 9 mm PET felt; HW-SEL A3; D-31 (the factory's felt)"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm"),
    ("tray_h", "cass_t", "mm", "confirmed",
     "PM ruling 2026-10-31 (WALL group, option 1): the wall cassettes use the ceiling's tray, returns the full "
     "cassette depth (34) turned in as lips that hold the felt, no ribs; settles H09 for the walls"),
    ("lip_w", "12 mm", "mm", "confirmed", "PM ruling 2026-10-31 (WALL group, option 1): 12 mm lips hold the felt edge"),
    ("bend_r", "tray_t", "mm", "assumption",
     "inside bend radius 1 x t for 0.5 mm DX51D (the sheet metal rule's bend radius is its Thickness); the factory's "
     "tooling sets it (guideline 9)"),
    ("felt_c", "1 mm", "mm", "assumption", "felt edge clearance inside the returns, as the ceiling cassette"),
    ("gap_h", "tray_h - felt_t - 2 * tray_t", "mm", "calculation",
     "air gap between the tray base and the felt (24): the acoustic gap (D-17) and the cable path (D-26)"),
    ("cass_len", "wall_depth - stack_t + cass_t", "mm", "calculation",
     "= 1448: from the decor back plate to past the back cassette's face, closing the inside corner (D-57)"),
    ("cass_h", "side_h" if ROW == 1 else "side_h - outer_t - lin_gap", "mm", "calculation",
     "lower: the panel height; upper: stops lin_gap under the roof frame so it floats (D-57)"),
    ("clip_zone_h", "60 mm", "mm", "assumption", "height of each reserved clip zone (H03: no clip named)"),
    ("clip_zone_dz", "100 mm", "mm", "assumption", "clip zone centre from the cassette's top and bottom edges (H03)"),
]

# kg/m3, status, source; used for body materials (mass properties)
DENSITY = {
    "frame": (2700.0, "source", "aluminium 2.70 g/cm3 (HW-SEL A4 calculation basis); alloy HOLD (ISS-034, H15)"),
    "skin": (3.5 / 0.003, "calculation", "HW-SEL A1: 3.5 kg/m2 for 3 mm Alcorest / 3 mm; real kg/m2 HOLD (H16)"),
    "fill": (32.0, "confirmed", "D-54: 32 kg/m3 fill until the wall sample tests 25"),
    "tray": (7850.0, "source", "steel 7850 kg/m3 (EN 10346 DX51D+Z)"),
    "felt": (1.8 / 0.009, "source", "Polyx Board 9: 1.8 kg/m2 at 9 mm (HW-SEL A3 opt 2); the factory felt is unverified"),
    "zone": (1.0, "assumption", "reserved zone, not a part: near-zero density so it adds no mass"),
}

# ---------------------------------------------------------------- helpers


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    """Expression value in mm."""
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def skeleton_params(repo_root):
    """PARAMS of pod_skeleton.py, parsed with ast (no code is run)."""
    path = os.path.join(repo_root, SKELETON_REL)
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PARAMS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("no PARAMS in " + path)


def names_in(expr):
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", expr)) - {"mm", "ceil", "floor", "abs", "round"}


def needed_skeleton(skel, wall):
    """The skeleton parameters the wall expressions use, with their own dependencies, in skeleton order."""
    by_name = {p[0]: p for p in skel}
    want, todo = set(), set()
    for _n, expr, _u, _s, _src in wall:
        todo |= names_in(expr)
    for extra in ("pod_w", "pod_d", "pod_h", "wall_z0", "side_h", "stack_t", "outer_t", "cass_t", "lin_gap"):
        todo.add(extra)
    while todo:
        n = todo.pop()
        if n in by_name and n not in want:
            want.add(n)
            todo |= names_in(by_name[n][1])
    return [p for p in skel if p[0] in want]


SKELETON_NAMES = ("pod_w", "pod_d", "pod_h", "wall_depth", "wall_z0", "panel_z0", "side_h", "stack_t", "outer_t",
                  "cass_t", "lin_gap", "seam_gap")       # the skeleton parameters the wall uses (P04)


def derive_skeleton(app, design, name):
    """Link the design to the saved skeleton with Fusion's Derive (favorite parameters only), as
    tools/fusion/README.md 'Linking a part to the skeleton' describes. Returns the version derived."""
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
    files = [f for f in folder.dataFiles if f.name == name]
    if not files:
        raise RuntimeError("skeleton %r not found in Default Project / FocusPod v2" % name)
    part_doc = app.activeDocument
    skel_doc = app.documents.open(files[0], False)          # invisible
    try:
        skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
        part_doc.activate()
        root = design.rootComponent
        di = root.features.deriveFeatures.createInput(skel)
        di.isIncludeFavoriteParameters = True
        di.sourceEntities = [skel.rootComponent.xYConstructionPlane]   # parameters only
        d = root.features.deriveFeatures.add(di)
        d.timelineObject.name = "DERIVE - SKELETON PARAMETERS (%s)" % name
        for pl in root.constructionPlanes:          # the derived plane only carries the link; keep it hidden
            if pl.isLightBulbOn and "PLANE - " not in pl.name:
                pl.isLightBulbOn = False
    finally:
        skel_doc.close(False)
        part_doc.activate()
    return files[0].versionNumber


def add_params(design, repo_root):
    app = adsk.core.Application.get()
    if ARGS.get("link", "derive") == "derive":
        skel_name = ARGS.get("skeleton", "100000_P04_POD-SKELETON_CAD")
        ver = derive_skeleton(app, design, skel_name)
        for n in SKELETON_NAMES:
            ref = design.allParameters.itemByName(n + "_Ref")
            if ref is None:
                raise RuntimeError("the skeleton has no favorite parameter %s (derived as %s_Ref)" % (n, n))
            design.userParameters.add(n, vi(n + "_Ref"), "mm", "LINKED: %s_Ref, derived from %s v%d (skeleton is the "
                                                               "single source)" % (n, skel_name, ver))
        n_skel = len(SKELETON_NAMES)
    else:
        skel = skeleton_params(repo_root)
        used = needed_skeleton(skel, WALL_PARAMS)
        for name, expr, unit, status, src in used:
            design.userParameters.add(name, vi(expr), unit, "%s: %s [copied from pod_skeleton.py PARAMS, link=parse]" % (
                status.upper(), src))
        n_skel = len(used)
    for name, expr, unit, status, src in WALL_PARAMS:
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        if p is None:
            raise RuntimeError("could not add parameter " + name)
    return n_skel, len(WALL_PARAMS)


def new_comp(parent, key, sheet_metal=False):
    pn, name, vn = PARTS[key]
    tr = adsk.core.Matrix3D.create()
    occ = parent.occurrences.addNewSheetMetalComponent(tr) if sheet_metal else parent.occurrences.addNewComponent(tr)
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s | %s" % (name, vn, REV)
    return c


def sx(expr):
    """X coordinate expression on this side: expr is the distance from the pod centre plane."""
    return "-(%s)" % expr if S < 0 else "(%s)" % expr


def span(design, a, b):
    """Order two coordinate expressions by value: (low, high)."""
    return (a, b) if ev(design, a) <= ev(design, b) else (b, a)


def xy_plane(comp, z_expr, design, label):
    if abs(ev(design, z_expr)) < 1e-9:
        return comp.xYConstructionPlane
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, vi(z_expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    return pl


def box(design, comp, label, xr, yr, zr, op="new", body=None, plane=None):
    """Axis-aligned box: a fully constrained rectangle on the XY plane at z0 (corners dimensioned
    from the sketch origin by the parameter expressions), extruded along +Z to z1.
    op: new | cut | join (cut and join act on `body`). Returns the feature."""
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    x0, x1, y0, y1 = (ev(design, e) for e in (xr[0], xr[1], yr[0], yr[1]))
    pl = plane or xy_plane(comp, zr[0], design, label + " BOTTOM")
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
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
    ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
           "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
           "join": adsk.fusion.FeatureOperations.JoinFeatureOperation}
    ext_in = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), ops[op])
    ext_in.setDistanceExtent(False, vi("(%s) - (%s)" % (zr[1], zr[0])))
    if op != "new" and body is not None:
        ext_in.participantBodies = body if isinstance(body, list) else [body]
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "%s - %s" % ({"new": "EXTRUDE", "cut": "CUT", "join": "JOIN"}[op], label)
    return ext


def tube(design, comp, label, xr, yr, zr, along):
    """Hollow 20 x 40 x 1.2 member: outer box, then the bore cut through its length.
    along: 'y' (rail) or 'z' (stile)."""
    ext = box(design, comp, label + " TUBE", xr, yr, zr)
    b = ext.bodies.item(0)
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    t = "tube_t"
    bx = ("(%s) + %s" % (xr[0], t), "(%s) - %s" % (xr[1], t))
    if along == "y":
        box(design, comp, label + " BORE", bx, yr, ("(%s) + %s" % (zr[0], t), "(%s) - %s" % (zr[1], t)), "cut", b)
    else:
        box(design, comp, label + " BORE", bx, ("(%s) + %s" % (yr[0], t), "(%s) - %s" % (yr[1], t)), zr, "cut", b)
    b.name = label
    return b


def pattern_y(comp, bodies, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for b in bodies:
        coll.add(b)
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, comp.yConstructionAxis, vi(count_expr), vi(pitch_expr),
        adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    # Fusion 2706 defaults direction two to 3 instances at 0 mm when it isn't set, which stacks 3
    # identical bodies on every instance (found on the first L1 build, 2026-10-31): set it to 1.
    pin.setDirectionTwo(comp.zConstructionAxis, vi("1"), vi("1 mm"))
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


AXES = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def origin_plane(comp, axis):
    """The origin plane normal to a model axis."""
    return {"x": comp.yZConstructionPlane, "y": comp.xZConstructionPlane, "z": comp.xYConstructionPlane}[axis]


def plane_at(design, comp, axis, expr, label):
    """Construction plane normal to `axis` at coordinate `expr`. An offset runs along the origin plane's
    normal, which need not point along +axis (Fusion's XZ plane), so the sign follows that normal."""
    base = origin_plane(comp, axis)
    if abs(ev(design, expr)) < 1e-9:
        return base
    n = base.geometry.normal
    sign = 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(base, vi(expr if sign > 0 else "-(%s)" % expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    o = pl.geometry.origin
    got = {"x": o.x, "y": o.y, "z": o.z}[axis] * 10.0
    if abs(got - ev(design, expr)) > 0.01:
        raise RuntimeError("plane %s landed at %s = %.2f, not %.2f" % (label, axis, got, ev(design, expr)))
    return pl


def sketch_axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis maps to on this sketch."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*AXES[model_axis]))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def hole(design, comp, body, axis, plane_expr, into, pos, dia, depth, label):
    """A simple hole feature on a plane normal to `axis` at `plane_expr`, drilled `into` (+1 or -1 along
    the axis) for `depth`. pos: {model axis: coordinate expression} for the two in-plane axes. The centre
    point is dimensioned from the sketch origin by those expressions, so the sketch is fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "HOLE CENTRE - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    pt = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(pt, sk.originPoint)
        else:
            g = pt.geometry
            tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, H if sa == "x" else V,
                                                     tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    hin = comp.features.holeFeatures.createSimpleInput(vi(dia))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi(depth))
    n = pl.geometry.normal
    if into * {"x": n.x, "y": n.y, "z": n.z}[axis] > 0:
        hin.isDefaultDirection = False       # a hole runs against the plane normal unless flipped
    hin.participantBodies = [body]
    h = comp.features.holeFeatures.add(hin)
    h.name = "HOLE - %s" % label
    return h


def rect_on_x(design, comp, x_expr, yr, zr, label):
    """Fully constrained rectangle on a plane normal to X at x_expr, spanning model Y yr and Z zr."""
    yr, zr = span(design, *yr), span(design, *zr)
    pl = plane_at(design, comp, "x", x_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    x = ev(design, x_expr)
    y0, y1, z0, z1 = (ev(design, e) for e in (yr[0], yr[1], zr[0], zr[1]))

    def sp(y, z):
        return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, z * MM))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(sp(y0, z0), sp(y1, z1))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(a.y - b.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for q in (ln.startSketchPoint, ln.endSketchPoint):
            if all(q != o for o in pts):
                pts.append(q)

    def near(y, z):
        t = sp(y, z)
        return min(pts, key=lambda q: (q.geometry.x - t.x) ** 2 + (q.geometry.y - t.y) ** 2)
    c00, c10, c01 = near(y0, z0), near(y1, z0), near(y0, z1)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    ay, az = sketch_axis_of(sk, "y"), sketch_axis_of(sk, "z")
    o = {"x": H, "y": V}
    mid = sp((y0 + y1) / 2, (z0 + z1) / 2)
    tp = adsk.core.Point3D.create(mid.x, mid.y, 0)
    sk.sketchDimensions.addDistanceDimension(c00, c10, o[ay], tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    sk.sketchDimensions.addDistanceDimension(c00, c01, o[az], tp).parameter.expression = "(%s) - (%s)" % (zr[1], zr[0])
    for axis, val, e in ((ay, y0, yr[0]), (az, z0, zr[0])):
        if abs(val) < 1e-6:
            (gc.addVerticalPoints if axis == "x" else gc.addHorizontalPoints)(c00, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c00, o[axis], tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk


def pattern_feat(comp, feats, axis, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for f in feats:
        coll.add(f)
    ax = {"x": comp.xConstructionAxis, "y": comp.yConstructionAxis, "z": comp.zConstructionAxis}[axis]
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, ax, vi(count_expr), vi(pitch_expr), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    other = comp.zConstructionAxis if axis != "z" else comp.xConstructionAxis
    pin.setDirectionTwo(other, vi("1"), vi("1 mm"))      # see pattern_y
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


def name_by_y(comp, known, first, prefix):
    """Name the pattern's copies and the original by their order along +Y: PREFIX 1..n.
    Fusion API objects compare with == but are not hashable, so `known` is a list."""
    group = [first] + [b for b in comp.bRepBodies if not any(b == k for k in known) and not b == first]
    group.sort(key=lambda b: b.boundingBox.minPoint.y)
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along Y: %s" % prefix)
    out = {}
    for i, b in enumerate(group):
        b.name = "%s %d" % (prefix, i + 1)
        out[b.name] = b
    return out


def bbox(entity):
    b = entity.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def size(b):
    return "%g x %g x %g" % (round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2))


def set_material(design, bodies, key, label):
    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
    base = lib.materials.itemByName("Aluminum")
    name = "%s %g kg/m3 (%s)" % (label, round(DENSITY[key][0], 1), DENSITY[key][1])
    mat = design.materials.itemByName(name)
    if mat is None:
        mat = design.materials.addByCopy(base, name)
        mat.materialProperties.itemById("structural_Density").value = DENSITY[key][0]
    for b in bodies:
        b.material = mat
    return mat


def clash_check(bodies, allowed=()):
    """Pairwise solid intersections over 1 mm3; fails on any pair not in `allowed`."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            ba, bb = bbox(a), bbox(b)
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(a), tbm.copy(b)
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((a.name, b.name, round(vol)))
    bad = [h for h in hits if frozenset(h[:2]) not in {frozenset(p) for p in allowed}]
    return hits, bad


def clear_design(design):
    """rebuild=1: empty a design this script built before (same root part number)."""
    tl = design.timeline
    if tl.count:
        tl.moveToBeginning()
        tl.deleteAllAfterMarker()
    for i in range(design.userParameters.count - 1, -1, -1):
        design.userParameters.item(i).deleteMe()
    for i in range(design.materials.count - 1, -1, -1):
        m = design.materials.item(i)
        if " kg/m3 (" in m.name:
            try:
                m.deleteMe()
            except Exception:       # still in use by nothing after the timeline is gone; ignore
                pass


# ---------------------------------------------------------------- geometry expressions

X_OUT = sx("pod_w / 2")                          # outer face of the skin
X_SKIN_IN = sx("pod_w / 2 - skin_t")             # inner face of the skin
X_FRAME_OUT = sx("pod_w / 2 - skin_t - bond_t")  # outer face of the frame, behind the 3 mm bond line
X_FRAME_IN = sx("pod_w / 2 - outer_t")           # inner face of the frame (side frames' inner face)
X_IN = sx("pod_w / 2 - stack_t")                 # room-side face of the lining (felt face)
X_TRAY_BACK = sx("pod_w / 2 - stack_t + cass_t")   # back face of the tray base (4 mm from the frame)
X_FELT_FACE = sx("pod_w / 2 - stack_t + tray_t")   # felt's room face, behind the lips
X_FELT_BACK = sx("pod_w / 2 - stack_t + tray_t + felt_t")

# panel envelope: the skeleton's side panel (seam gaps at the decor, on the band and at the row seam)
Y_FRONT = "pod_d / 2 - wall_depth + seam_gap"    # panel front end: 2.26 behind the decor back plate (F-008)
Y_BACK = "pod_d / 2"                             # outer face of the back wall
Y_FRAME_BACK = "pod_d / 2 - skin_t"              # inside of the skin's back return
Y_CASS_FRONT = "pod_d / 2 - wall_depth"          # the lining starts at the decor back plate (skeleton P04)
Y_CASS_BACK = "pod_d / 2 - stack_t + cass_t"     # side lining end, past the back lining (D-57)

# rows as skeleton P04: panel_z0 = the walls' bottom, one seam_gap above the band top (F-008)
Z0 = "panel_z0" if ROW == 1 else "panel_z0 + side_h + seam_gap"
Z1 = "panel_z0 + side_h" if ROW == 1 else "pod_h"
Z_SKIN0 = "(%s) + skin_setback" % Z0
Z_SKIN1 = "(%s) - skin_setback" % Z1 if ROW == 1 else Z1   # the upper skins run to the roof datum
Z_CASS1 = Z1 if ROW == 1 else "pod_h - outer_t - lin_gap"


def build_panel(design, root):
    out = {}
    frame, skin, fill = new_comp(root, "frame"), new_comp(root, "skin"), new_comp(root, "fill")
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin, fill)))
    if STOP_AFTER <= 1:
        return out
    xf = (X_FRAME_OUT, X_FRAME_IN)
    yf = (Y_FRONT, Y_FRAME_BACK)
    # rails run the full frame length; stiles fit between them (butt joints, member joint method HOLD H11)
    out["RAIL - BOTTOM"] = tube(design, frame, "RAIL - BOTTOM", xf, yf, (Z0, "(%s) + tube_w" % Z0), "y")
    out["RAIL - TOP"] = tube(design, frame, "RAIL - TOP", xf, yf, ("(%s) - tube_w" % Z1, Z1), "y")
    print("step 2: rails", [(k, size(bbox(v))) for k, v in out.items()])
    if STOP_AFTER <= 2:
        return out
    zs = ("(%s) + tube_w" % Z0, "(%s) - tube_w" % Z1)
    out["STILE - FRONT"] = tube(design, frame, "STILE - FRONT", xf, (Y_FRONT, "(%s) + tube_w" % Y_FRONT), zs, "z")
    out["STILE - BACK"] = tube(design, frame, "STILE - BACK", xf, ("(%s) - corner_w" % Y_FRAME_BACK, Y_FRAME_BACK),
                               zs, "z")
    mid = tube(design, frame, "STILE - MID 1", xf,
               ("(%s) + stile_pitch" % Y_FRONT, "(%s) + stile_pitch + tube_w" % Y_FRONT), zs, "z")
    out["STILE - MID 1"] = mid
    pattern_y(frame, [mid], "stile_n_mid", "stile_pitch", "STILES - MID")
    out.update(name_by_y(frame, list(out.values()), mid, "STILE - MID"))
    print("step 3: stiles, %d mid at pitch %.2f" % (
        round(design.userParameters.itemByName("stile_n_mid").value),
        design.userParameters.itemByName("stile_pitch").value * 10.0))
    if STOP_AFTER <= 3:
        return out
    yskin = (Y_FRONT, Y_BACK)
    zskin = (Z_SKIN0, Z_SKIN1)
    plate = box(design, skin, "SKIN PLATE", (X_OUT, X_SKIN_IN), yskin, zskin).bodies.item(0)
    box(design, skin, "SKIN BACK RETURN", (X_SKIN_IN, sx("pod_w / 2 - skin_t - skin_ret")),
        (Y_FRAME_BACK, Y_BACK), zskin, "join", plate)
    plate.name = "SKIN - ACP 3 WITH BACK RETURN"
    out[plate.name] = plate
    print("step 4: skin", size(bbox(plate)))
    if STOP_AFTER <= 4:
        return out
    # fill bays: one per bay between the stiles; the last bay (against the 40 mm back stile) is its own box
    bay = box(design, fill, "FILL BAY 1", xf, ("(%s) + tube_w" % Y_FRONT, "(%s) + stile_pitch" % Y_FRONT),
              zs).bodies.item(0)
    bay.name = "FILL - BAY 1"
    out[bay.name] = bay
    pattern_y(fill, [bay], "stile_n_mid", "stile_pitch", "FILL BAYS")
    out.update(name_by_y(fill, list(out.values()), bay, "FILL - BAY"))
    last = box(design, fill, "FILL BAY LAST", xf, ("(%s) + stile_n_mid * stile_pitch + tube_w" % Y_FRONT,
                                                    "(%s) - corner_w" % Y_FRAME_BACK), zs).bodies.item(0)
    last.name = "FILL - BAY %d" % (sum(1 for k in out if k.startswith("FILL")) + 1)
    out[last.name] = last
    # pockets beside every bolt this panel drives (FR-10): one cut per bolt, at the bolt's own rule, each
    # allowed to cut any fill bay (a pattern of a cut can't reach other bodies: PATTERN_FEATURES_NO_PASTE_INT_EDGES)
    bays = [b for k, b in out.items() if k.startswith("FILL")]
    z_rail_top = "(%s) + tube_w" % Z0
    if ROW == 1:
        n_now = int(round(design.userParameters.itemByName("n_base_bolt").value))
        ys = ["(%s) + base_bolt_edge + %d * base_bolt_pitch" % (Y_FRONT, i) for i in range(n_now)]
    else:
        n_now = int(round(design.userParameters.itemByName("stile_n_mid").value)) + 1
        ys = ["(%s) + tube_w / 2 + (%d + 0.5) * stile_pitch" % (Y_FRONT, i) for i in range(n_now)]
    for i, yc in enumerate(ys):
        box(design, fill, "FILL POCKET BOTTOM BOLT %d" % (i + 1), xf,
            ("(%s) - pocket_w / 2" % yc, "(%s) + pocket_w / 2" % yc), (z_rail_top, "(%s) + pocket_w" % z_rail_top),
            "cut", bays)
    z_j1 = "(%s) + jnt_edge" % Z0
    for j in range(3):
        zc = "(%s) + %d * side_jnt_pitch" % (z_j1, j)
        box(design, fill, "FILL POCKET DECOR BOLT %d" % (j + 1), xf,
            ("(%s) + tube_w" % Y_FRONT, "(%s) + tube_w + pocket_w" % Y_FRONT),
            ("(%s) - pocket_w / 2" % zc, "(%s) + pocket_w / 2" % zc), "cut", bays)
    print("step 5: fill, %d bays, pockets at every bolt this panel drives" % sum(1 for k in out if k.startswith("FILL")))
    if STOP_AFTER <= 5:
        return out
    joint_features(design, frame, fill, out)
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "ALUMINIUM TUBE (alloy HOLD)")
    set_material(design, [plate], "skin", "ACP 3 MM EV3038")
    set_material(design, [b for k, b in out.items() if k.startswith("FILL")], "fill", "PET FILL 40 MM")
    return out


def joint_features(design, frame, fill, out):
    """Site joint holes per the joints register (V2-ENG-JNT-01 P01, ce1f415). The fill pockets are in step 5."""
    xc = sx("pod_w / 2 - skin_t - bond_t - tube_d / 2")     # centre line of the frame depth
    y_bay1 = "(%s) + tube_w / 2 + stile_pitch / 2" % Y_FRONT  # first bolt: mid-pitch of the first bay
    n_bays = "stile_n_mid + 1"
    t = "tube_t"
    bot, top = out["RAIL - BOTTOM"], out["RAIL - TOP"]
    front, back = out["STILE - FRONT"], out["STILE - BACK"]
    zb0, zb1 = Z0, "(%s) + tube_w" % Z0                      # bottom rail bottom and top faces
    zt1 = Z1                                                 # top rail top face
    # bottom rail, bolt side of J-BASE-01 (lower) or J-WALL-01 (upper): FR-02 + FR-03 at each bay
    if ROW == 1:      # J-BASE-01: at the band's rivnuts (BASE Engineer's rule, ruled to stand)
        y_b1, n_b, p_b = "(%s) + base_bolt_edge" % Y_FRONT, "n_base_bolt", "base_bolt_pitch"
    else:             # J-WALL-01 bolt side: one per bay, coaxial with the lower panel's rivnuts
        y_b1, n_b, p_b = y_bay1, n_bays, "stile_pitch"
    a = hole(design, frame, bot, "z", zb0, +1, {"x": xc, "y": y_b1}, "bolt_d", t, "BOTTOM RAIL BOLT CLEARANCE 1")
    b = hole(design, frame, bot, "z", zb1, -1, {"x": xc, "y": y_b1}, "access_d", t, "BOTTOM RAIL KEY ACCESS 1")
    pattern_feat(frame, [a, b], "y", n_b, p_b, "BOTTOM RAIL BOLT HOLES")
    # bottom rail locating: round spigot hole at the front end, slot along X at the back-corner end (FR-05)
    hole(design, frame, bot, "z", zb0, +1, {"x": xc, "y": "(%s) + spigot_edge" % Y_FRONT}, "spigot_d", t,
         "BOTTOM RAIL SPIGOT ROUND")
    ys = "(%s) - spigot_edge" % Y_BACK
    half = "(spigot_slot - spigot_d) / 2"
    box(design, frame, "BOTTOM RAIL SPIGOT SLOT", ("(%s) - %s" % (xc, half), "(%s) + %s" % (xc, half)),
        ("(%s) - spigot_d / 2" % ys, "(%s) + spigot_d / 2" % ys), (zb0, "(%s) + %s" % (zb0, t)), "cut", bot)
    for i, sgn in enumerate(("-", "+")):
        hole(design, frame, bot, "z", zb0, +1, {"x": "(%s) %s %s" % (xc, sgn, half), "y": ys}, "spigot_d", t,
             "BOTTOM RAIL SPIGOT SLOT END %d" % (i + 1))
    if ROW == 1:
        # top rail, nut side of J-WALL-01: rivnut at each bay (FR-01) and 2 spigot rivnuts (FR-04)
        r = hole(design, frame, top, "z", zt1, -1, {"x": xc, "y": y_bay1}, "rivnut_d", t, "TOP RAIL RIVNUT 1")
        pattern_feat(frame, [r], "y", n_bays, "stile_pitch", "TOP RAIL RIVNUTS")
        hole(design, frame, top, "z", zt1, -1, {"x": xc, "y": "(%s) + spigot_edge" % Y_FRONT}, "rivnut_d", t,
             "TOP RAIL SPIGOT RIVNUT FRONT")
        hole(design, frame, top, "z", zt1, -1, {"x": xc, "y": "(%s) - spigot_edge" % Y_BACK}, "rivnut_d", t,
             "TOP RAIL SPIGOT RIVNUT BACK")
    z_j1 = "(%s) + jnt_edge" % Z0
    # front stile, bolt side of J-FRONT-01 (decor block): FR-02 in the front wall, FR-03 in the back wall
    a = hole(design, frame, front, "y", Y_FRONT, +1, {"x": xc, "z": z_j1}, "bolt_d", t, "FRONT STILE BOLT CLEARANCE 1")
    b = hole(design, frame, front, "y", "(%s) + tube_w" % Y_FRONT, -1, {"x": xc, "z": z_j1}, "access_d", t,
             "FRONT STILE KEY ACCESS 1")
    pattern_feat(frame, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "FRONT STILE BOLT HOLES")
    # 40 x 40 back stile, nut side of J-WALL-02 (back corner): rivnut in the room-side face (FR-01, FR-06)
    r = hole(design, frame, back, "x", X_FRAME_IN, S, {"y": "(%s) - corner_w / 2" % Y_FRAME_BACK, "z": z_j1},
             "rivnut_d", t, "BACK STILE CORNER RIVNUT 1")
    pattern_feat(frame, [r], "z", "n_side_jnt", "side_jnt_pitch", "BACK STILE CORNER RIVNUTS")
    holes = sum(c.features.holeFeatures.count for c in [frame])
    print("step 6: joint features: %d hole features (before patterns)" % holes)


def build_tray(design, root, tray, yc, zc):
    """Sheet metal tray, the ceiling tray's recipe (v2/01-CAD-Native/ceiling): base flange on the plane of the
    tray back, returns tray_h deep toward the room, 12 mm lips turned in to hold the felt. Edge flanges need the
    sheet metal component active. Bend position and lip direction are tried both ways and kept only when the
    outer faces land on the cassette outline."""
    rule = design.designSheetMetalRules.itemByName("GALV STEEL 0.5 - LINING TRAY")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(tray.activeSheetMetalRule, "GALV STEEL 0.5 - LINING TRAY")
    rule.thickness.expression = "%.4f mm" % ev(design, "tray_t")   # a rule takes values only (Fusion 2706)
    rule.bendRadius.expression = "Thickness"                        # = bend_r (1 x t)
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    tray.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == tray][0]
    occ.activate()
    want_yz = [ev(design, e) for e in (span(design, *yc) + span(design, *zc))]
    xb = ev(design, X_TRAY_BACK)
    try:
        sk = rect_on_x(design, tray, X_TRAY_BACK, yc, zc, "TRAY BASE OUTLINE")
        ff = tray.features.flangeFeatures
        base = None
        for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                       adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
            bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
            bfi.orientation = orient
            f = ff.add(bfi)
            b = bbox(f.bodies.item(0))
            back, room = (b[0], b[3]) if S < 0 else (b[3], b[0])     # the room is toward -S
            if abs(back - xb) < 0.01 and abs(room - (xb - S * ev(design, "tray_t"))) < 0.01:
                base = f
                break
            f.deleteMe()
        if base is None:
            raise RuntimeError("tray: no base flange side lies on the room side of the tray back")
        base.name = "BASE - TRAY"
        body = tray.bRepBodies.item(0)
        body.name = "TRAY - STEEL 0.5 WITH RETURNS AND LIPS"
        xr = xb - S * ev(design, "tray_t")      # room-side face of the base (the room is toward -S)

        def x_edges(x, keep):
            return [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
                    and abs(e.startVertex.geometry.x * 10 - x) < 0.01 and abs(e.endVertex.geometry.x * 10 - x) < 0.01
                    and keep(e)]
        eds = x_edges(xr, lambda e: True)
        if len(eds) != 4:
            raise RuntimeError("tray: expected 4 base edges on the room side, got %d" % len(eds))
        ret = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType,
                    adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            efi = ff.createEdgeFlangeInput([], vi("tray_h - tray_t - bend_r"))
            for e in eds:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            efi.bendPositionType = pos
            f = ff.add(efi)
            b = bbox(tray.bRepBodies.item(0))
            if all(abs(g - w) < 0.05 for g, w in zip([b[1], b[4], b[2], b[5]], want_yz)):
                ret = f
                break
            f.deleteMe()
        if ret is None:
            raise RuntimeError("tray: no bend position keeps the returns' outer faces on the outline")
        ret.name = "FLANGE - TRAY RETURNS"
        body = tray.bRepBodies.item(0)
        b = bbox(body)
        xt = b[3] if S < 0 else b[0]         # the returns' tips, at the room side

        def off_outline(e):
            q = e.startVertex.geometry
            return min(abs(q.y * 10 - b[1]), abs(q.y * 10 - b[4]), abs(q.z * 10 - b[2]), abs(q.z * 10 - b[5])) > 0.05 \
                and e.length * 10 > 100
        inner = x_edges(xt, off_outline)
        if len(inner) != 4:
            raise RuntimeError("tray: expected 4 inner tip edges, got %d" % len(inner))
        lip = None
        x_room = ev(design, X_IN)
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput([], vi("lip_w"))
            for e in inner:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = bbox(tray.bRepBodies.item(0))
            room = b2[3] if S < 0 else b2[0]
            inside = all(abs(g - w) < 0.05 for g, w in zip([b2[1], b2[4], b2[2], b2[5]], want_yz)) and \
                abs(room - x_room) < 0.05
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("tray: no lip direction keeps the lips inside the outline at the room face")
        lip.name = "FLANGE - TRAY LIPS HOLDING THE FELT"
        body = tray.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(fc.geometry.normal.x) > 0.99), key=lambda fc: fc.area)
        fp = tray.flatPattern or tray.createFlatPattern(big)
        print("FLAT|%s|%s" % (tray.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    return tray.bRepBodies.item(0)


def build_cassette(design, root):
    out = {}
    tray, felt, clip = new_comp(root, "tray", sheet_metal=True), new_comp(root, "felt"), new_comp(root, "clip")
    print("step 1: components %s" % ", ".join(c.name for c in (root, tray, felt, clip)))
    if STOP_AFTER <= 1:
        return out
    yc = (Y_CASS_FRONT, Y_CASS_BACK)
    zc = (Z0, Z_CASS1)
    pan = build_tray(design, root, tray, yc, zc)
    out[pan.name] = pan
    print("step 2: tray", size(bbox(pan)))
    if STOP_AFTER <= 2:
        return out
    fb = box(design, felt, "FELT", (X_FELT_FACE, X_FELT_BACK),
             ("(%s) + tray_t + felt_c" % yc[0], "(%s) - tray_t - felt_c" % yc[1]),
             ("(%s) + tray_t + felt_c" % zc[0], "(%s) - tray_t - felt_c" % zc[1])).bodies.item(0)
    fb.name = "FELT - PET 9 HELD BY THE TRAY LIPS"
    out[fb.name] = fb
    print("step 3: felt", size(bbox(fb)))
    if STOP_AFTER <= 3:
        return out
    # reserved zones for the captive clips (H03): in the 4 mm gap between the frame's inner face and the
    # tray back, on the first and last intermediate stiles of the panel frame, near the top and bottom
    ys = [("(%s) + stile_pitch" % Y_FRONT, "(%s) + stile_pitch + tube_w" % Y_FRONT),
          ("(%s) + stile_n_mid * stile_pitch" % Y_FRONT, "(%s) + stile_n_mid * stile_pitch + tube_w" % Y_FRONT)]
    zs = [("(%s) + clip_zone_dz - clip_zone_h / 2" % Z0, "(%s) + clip_zone_dz + clip_zone_h / 2" % Z0),
          ("(%s) - clip_zone_dz - clip_zone_h / 2" % Z_CASS1, "(%s) - clip_zone_dz + clip_zone_h / 2" % Z_CASS1)]
    n = 0
    for zi, zr in enumerate(zs):
        for yi, yr in enumerate(ys):
            n += 1
            b = box(design, clip, "CLIP ZONE %d" % n, (X_FRAME_IN, X_TRAY_BACK), yr, zr).bodies.item(0)
            b.name = "HOLD - CLIP ZONE %d (%s %s)" % (n, "BOTTOM" if zi == 0 else "TOP", "FRONT" if yi == 0 else "BACK")
            out[b.name] = b
    print("step 4: %d clip zones (HOLD H03)" % n)
    set_material(design, [pan], "tray", "GALVANISED STEEL 0.5")
    set_material(design, [fb], "felt", "PET FELT 9 MM")
    set_material(design, [b for k, b in out.items() if k.startswith("HOLD")], "zone", "RESERVED ZONE")
    return out


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("the active document is not a Fusion design")
    root = design.rootComponent
    pn = PARTS[ROOT_KEY][0]
    if design.userParameters.count or root.occurrences.count or root.bRepBodies.count:
        if ARGS.get("rebuild") != "1":
            raise RuntimeError("the active design is not empty; pass rebuild=1 to rebuild it")
        if root.partNumber != pn and not app.activeDocument.name.startswith(pn + "_"):
            # a root part number set while --doc-new's first upload is still running can be
            # overwritten by it (seen on the first cassette build), so the document name counts too
            raise RuntimeError("refusing to rebuild: root part number is %r, not %s" % (root.partNumber, pn))
        clear_design(design)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    n_skel, n_wall = add_params(design, ARGS["repo_root"])
    root.partNumber = pn
    root.description = "%s | %s | %s | position %s" % (PARTS[ROOT_KEY][1], PARTS[ROOT_KEY][2], REV, CODE)
    print("document %s (expected name %s): %d skeleton + %d wall parameters" % (
        app.activeDocument.name, DOC_NAME, n_skel, n_wall))
    bodies = build_panel(design, root) if PART == "panel" else build_cassette(design, root)
    tl = design.timeline
    bad_items = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    print("timeline %d items, unhealthy %d, sketches %d, loose %d" % (
        tl.count, len(bad_items), sum(c.sketches.count for c in design.allComponents), len(loose)))
    for name, b in sorted(bodies.items()):
        print("BODY|%s|%s|%s|%s" % (b.parentComponent.partNumber, name, size(bbox(b)), bbox(b)))
    hits, bad = clash_check(list(bodies.values()))
    print("clash pairs %d, unexpected %d %s" % (len(hits), len(bad), bad))
    for c in design.allComponents:
        if c.bRepBodies.count:
            pp = c.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
            print("MASS|%s|%s|%.3f kg|%d bodies" % (c.partNumber, c.name, pp.mass, c.bRepBodies.count))
    root.partNumber = pn            # again at the end, in case an upload overwrote it (see above)
    allb = list(bodies.values())
    print("root part number %s, bodies box %s" % (root.partNumber, [
        round(min(bbox(b)[i] for b in allb), 2) for i in range(3)] + [round(max(bbox(b)[i + 3] for b in allb), 2)
                                                                    for i in range(3)]))
    if bad_items or loose or bad:
        raise RuntimeError("checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
