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

Coordinates: the pod system of conventions.md section 4 (origin on the room
floor at the pod centre, +X right, +Y back, +Z up), the same as skeleton P03,
so every part sits where it goes in the pod and the WALL and GA assemblies
insert these designs without a transform.

Parameters: the skeleton's own parameter list is the single source of the pod
sizes. This script reads PARAMS from v2/01-CAD-Native/skeleton/pod_skeleton.py
(parsed, never copied) and adds every skeleton parameter the wall needs, with
the skeleton's status and source, then adds the wall's own parameters below,
each as an expression on the skeleton ones where it can be. Change a skeleton
value, rebuild, and the wall follows; inside Fusion, change side_h or
wall_depth and every body follows (edit test, edit_test_wall.py).

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
    ("tube_d", "outer_t - skin_t", "mm", "calculation", "frame depth = outer panel 43 - skin 3 = 40 (D-34's 40)"),
    ("tube_t", "1.2 mm", "mm", "confirmed", "D-34, D-54: wall 1.2 mm (rivnut grip check passed)"),
    ("stile_pitch_max", "400 mm", "mm", "confirmed", "D-16, D-34: members 400 mm apart or less, to keep the ACP flat"),
    ("pnl_len", "wall_depth", "mm", "confirmed", "D-49: side walls 1495 deep, Y -645 to +850 (skeleton wall_depth)"),
    ("pnl_h", "side_h", "mm", "calculation", "skeleton side_h = wall_h / 2 (D-23: 2 sheets per side wall)"),
    ("skin_ret", "tube_d", "mm", "assumption",
     "back return of the side skin: covers the frame's back end at the corner, where the side skin covers the back "
     "panel's edge (D-55; sample drawing D04). V-groove and fold per the ACP maker (HOLD H16)"),
    ("reveal", "4 mm", "mm", "assumption",
     "reveal between stacked skins and above the base band: D-23 asks for crisp, aligned reveals and sets no width; "
     "the joint register's seam detail sets it"),
    ("frm_len", "pnl_len - skin_t", "mm", "calculation", "the frame stops at the inside of the skin's back return"),
    ("frm_h", "pnl_h", "mm", "assumption",
     "the frame fills the skeleton envelope height; seam and base gasket gaps are set by the joint register (HOLD)"),
    ("stile_n_mid", "ceil((frm_len - tube_w) / stile_pitch_max) - 1", "", "calculation",
     "intermediate stiles so that no bay pitch exceeds stile_pitch_max"),
    ("stile_pitch", "(frm_len - tube_w) / (stile_n_mid + 1)", "mm", "calculation", "equal stile pitch, centre to centre"),
    ("stile_len", "frm_h - 2 * tube_w", "mm", "calculation", "stiles fit between the full-length rails (butt joints)"),
    ("fill_t", "tube_d", "mm", "calculation", "40 mm PET fill fills the frame depth (D-34; layout study 40 mm)"),
    # lining cassette
    ("felt_t", "9 mm", "mm", "source", "plan VT03-PET 9 mm PET felt; HW-SEL A3; D-31 (the factory's felt)"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm"),
    ("tray_ret", "cass_t - felt_t", "mm", "calculation", "= 25: D-17's 25 mm returns (the air gap behind the felt)"),
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


def add_params(design, repo_root):
    skel = skeleton_params(repo_root)
    used = needed_skeleton(skel, WALL_PARAMS)
    for name, expr, unit, status, src in used:
        design.userParameters.add(name, vi(expr), unit, "%s: %s [skeleton P03, pod_skeleton.py PARAMS]" % (
            status.upper(), src))
    for name, expr, unit, status, src in WALL_PARAMS:
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        if p is None:
            raise RuntimeError("could not add parameter " + name)
    return len(used), len(WALL_PARAMS)


def new_comp(parent, key):
    pn, name, vn = PARTS[key]
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
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
    if op != "new":
        ext_in.participantBodies = [body]
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
X_SKIN_IN = sx("pod_w / 2 - skin_t")             # inner face of the skin = outer face of the frame
X_FRAME_IN = sx("pod_w / 2 - outer_t")           # inner face of the frame (side frames' inner face)
X_IN = sx("pod_w / 2 - stack_t")                 # room-side face of the lining (felt face)
X_TRAY_FRONT = sx("pod_w / 2 - stack_t + felt_t")  # felt back = return edges of the tray
X_TRAY_BACK = sx("pod_w / 2 - stack_t + cass_t")   # back face of the tray (4 mm from the frame)
X_TRAY_BACK_IN = sx("pod_w / 2 - stack_t + cass_t - tray_t")

Y_FRONT = "pod_d / 2 - wall_depth"               # decor back plate, Y -645 (D-49)
Y_BACK = "pod_d / 2"                             # outer face of the back wall
Y_FRAME_BACK = "pod_d / 2 - skin_t"              # inside of the skin's back return
Y_CASS_BACK = "pod_d / 2 - stack_t + cass_t"     # side lining end, past the back lining (D-57)

Z0 = "wall_z0" if ROW == 1 else "wall_z0 + side_h"
Z1 = "wall_z0 + side_h" if ROW == 1 else "pod_h"
Z_SKIN0 = "(%s) + reveal / 2" % Z0
Z_SKIN1 = "(%s) - reveal / 2" % Z1 if ROW == 1 else Z1   # the upper skins run to the roof datum
Z_CASS1 = Z1 if ROW == 1 else "pod_h - outer_t - lin_gap"


def build_panel(design, root):
    out = {}
    frame, skin, fill = new_comp(root, "frame"), new_comp(root, "skin"), new_comp(root, "fill")
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin, fill)))
    if STOP_AFTER <= 1:
        return out
    xf = (X_SKIN_IN, X_FRAME_IN)
    yf = (Y_FRONT, Y_FRAME_BACK)
    # rails run the full frame length; stiles fit between them (butt joints, member joint method HOLD H11)
    out["RAIL - BOTTOM"] = tube(design, frame, "RAIL - BOTTOM", xf, yf, (Z0, "(%s) + tube_w" % Z0), "y")
    out["RAIL - TOP"] = tube(design, frame, "RAIL - TOP", xf, yf, ("(%s) - tube_w" % Z1, Z1), "y")
    print("step 2: rails", [(k, size(bbox(v))) for k, v in out.items()])
    if STOP_AFTER <= 2:
        return out
    zs = ("(%s) + tube_w" % Z0, "(%s) - tube_w" % Z1)
    out["STILE - FRONT"] = tube(design, frame, "STILE - FRONT", xf, (Y_FRONT, "(%s) + tube_w" % Y_FRONT), zs, "z")
    out["STILE - BACK"] = tube(design, frame, "STILE - BACK", xf, ("(%s) - tube_w" % Y_FRAME_BACK, Y_FRAME_BACK),
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
    bay = box(design, fill, "FILL BAY 1", xf, ("(%s) + tube_w" % Y_FRONT, "(%s) + stile_pitch" % Y_FRONT),
              zs).bodies.item(0)
    bay.name = "FILL - BAY 1"
    out[bay.name] = bay
    pattern_y(fill, [bay], "stile_n_mid + 1", "stile_pitch", "FILL BAYS")
    out.update(name_by_y(fill, list(out.values()), bay, "FILL - BAY"))
    print("step 5: fill, %d bays" % sum(1 for k in out if k.startswith("FILL")))
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "ALUMINIUM TUBE (alloy HOLD)")
    set_material(design, [plate], "skin", "ACP 3 MM EV3038")
    set_material(design, [b for k, b in out.items() if k.startswith("FILL")], "fill", "PET FILL 40 MM")
    return out


def build_cassette(design, root):
    out = {}
    tray, felt, clip = new_comp(root, "tray"), new_comp(root, "felt"), new_comp(root, "clip")
    print("step 1: components %s" % ", ".join(c.name for c in (root, tray, felt, clip)))
    if STOP_AFTER <= 1:
        return out
    yc = (Y_FRONT, Y_CASS_BACK)
    zc = (Z0, Z_CASS1)
    # solid pan: outer box, open toward the room; returns tray_ret deep, walls tray_t (D-17, D-37)
    pan = box(design, tray, "TRAY OUTER", (X_TRAY_BACK, X_TRAY_FRONT), yc, zc).bodies.item(0)
    box(design, tray, "TRAY POCKET", (X_TRAY_BACK_IN, X_TRAY_FRONT),
        ("(%s) + tray_t" % Y_FRONT, "(%s) - tray_t" % Y_CASS_BACK),
        ("(%s) + tray_t" % Z0, "(%s) - tray_t" % Z_CASS1), "cut", pan)
    pan.name = "TRAY - STEEL 0.5 WITH 25 RETURNS"
    out[pan.name] = pan
    print("step 2: tray", size(bbox(pan)))
    if STOP_AFTER <= 2:
        return out
    fb = box(design, felt, "FELT", (X_TRAY_FRONT, X_IN), yc, zc).bodies.item(0)
    fb.name = "FELT - PET 9 ACROSS THE TRAY FACE"
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
        if root.partNumber != pn:
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
    print("root box", bbox(root))
    if bad_items or loose or bad:
        raise RuntimeError("checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
