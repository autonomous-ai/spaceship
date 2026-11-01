"""Build 110000 BASE (Spaceship, FocusPod v2) as a native, parametric Fusion design.

Run it through the Fusion runner (tools/fusion/run_script.py):

    python3 tools/fusion/run_script.py v2/01-CAD-Native/base/base_build.py \
        --arg stop_after=9 --arg keep=1

Scope of revision P01 (the sample, built first because the factory's wall
sample stands on it): the back-left corner of the base. The left side band
(also the factory's base band rig R1, sample hold H17), the back band with
its J-BASE-01 hardware, the levelling glides and their doublers under those
two bands. The back corners join on the Joints Engineer's hook-in corner
keys (D-87, D-129). The pod has no floor (D-132): people stand on the room
floor, and the base seal is a soft lip on the bands' inner faces that presses
on it (a bought item by the metre, listed with each band, not modelled). The
rest of BASE comes from base_p02.py (--arg scope=p02).

Every size comes from parameters. The pod's own sizes are not copied here:
the script reads the skeleton P03 parameter list (PARAMS in
v2/01-CAD-Native/skeleton/pod_skeleton.py) at run time and adds it to this
design under the same names, so a skeleton change reaches the base on the
next build. BASE's own parameters follow, each with its status and source.

Coordinates are the pod system of v2/00-Control/conventions.md section 4:
origin on the room floor at the pod centre, +X to the right wall, +Y to the
back wall, +Z up; left and right as seen from outside facing the door. Each
part is its own component, built in place in pod coordinates.

Steps (--arg stop_after=N stops after step N):
  1 document, parameters, components     6 the P02 parts (with scope=p02)
  2 left side band                       7 hardware: rivet nuts, pins, glides
  3 back band                            8 materials and masses
  4 band holes (joints, spigots, glides)  9 checks: sketches, timeline, boxes,
  5 corner key (HOLD, Joints Engineer)     holes, clashes (own parts and skeleton)
Optional after step 9: --arg export=1 (f3d, STEP), --arg save=1 (cloud).
"""

import ast
import csv
import math
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
STOP_AFTER = int(ARGS.get("stop_after", "9"))
REV = "P01"
DOC_NAME = "110000_%s_BASE_CAD" % REV
HERE = os.path.dirname(os.path.abspath(globals().get("__file__", ARGS.get("script_path", "."))))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SKELETON = os.path.join(REPO, "v2", "01-CAD-Native", "skeleton", "pod_skeleton.py")

CM = 0.1  # Fusion API lengths are in cm; multiply mm by CM

# ---------------------------------------------------------------- parameters
# BASE's own parameters: name, expression, unit, status, source.
# Statuses follow conventions.md section 9. HOLD marks a value that waits on
# a named item (joints register, WALL frame bays, a bought part's data sheet).
BASE_PARAMS = [
    # base band section (100 x 40 is the skeleton's band_h x band_t)
    ("band_wall", "1.5 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (BASE group): 100 x 40 x 1.5 base band (was 2.0), with a doubler at each glide; rivnut coupon in 1.5 mm added to the rivnut test"),
    ("band_finish", "'Black anodised, matte, 20 um (class AA20, EN ISO 7599)'", "Text", "confirmed",
     "PM ruling 2026-10-31 (BASE group): every base band piece and the door's kick strip"),
    ("cap_t", "2 mm", "mm", "source",
     "the side band's back-end cap 118003: flat, inside the tube's end and flush with the back face Y = pod_d/2, no deeper "
     "than 2, as the back corner key sits 2.5 from the end (D-129, joints register J-BASE-02); product HOLD"),
    # the wall above (WALL owns it; these say where its bottom member sits)
    ("jb_x", "outer_t - frame_t / 2", "mm", "calculation",
     "J-BASE-01 bolt line: centre of the wall's bottom tube, 26 in from the pod's outer face (joints register 3.4: X -1224, Y +824)"),
    # J-BASE-01, wall to base band
    ("rn_hole", "9.53 mm", "mm", "source",
     "Sherex CAH2-610-4.2 M6 rivet nut, steel, zinc plated (joints register H-03, D-131): hole 9.53 +0.10/0, as the aluminium "
     "part's it replaced (unverified for the steel part, HOLD-04)"),
    ("rn_flange", "12.96 mm", "mm", "source", "CAH2-610-4.2 head diameter 12.96 (joints register H-03)"),
    ("rn_inst", "10.16 mm", "mm", "source", "CAH2-610-4.2 installed length, at most 10.16 (joints register H-03, maker data)"),
    ("rn_head_t", "0.76 mm", "mm", "source", "CAH2-610-4.2 head height 0.76 +-0.08 (joints register H-03, maker data)"),
    ("sw_hole", "10.5 mm", "mm", "source", "stop washer bore (joints register H-08, PROPOSED)"),
    ("sw_d", "20 mm", "mm", "source", "stop washer outside diameter (joints register H-08, PROPOSED)"),
    ("sw_t", "1.5 mm", "mm", "source",
     "stop washer, under each bolt rivnut's head: washer 1.5 + head 0.76 = seam_gap 2.26, so the walls stand at panel_z0 (D-64)"),
    ("jb_n", "n_base_bolt", "", "confirmed", "skeleton n_base_bolt (D-75, joints register R-J13): 4 bolts per wall panel on the band"),
    ("jb_e", "base_bolt_edge", "mm", "confirmed",
     "skeleton base_bolt_edge (D-75, R-J13): end bolts 220 in from each panel FRAME end, evenly spaced (PM ruling: measured on the frame, not the skin)"),
    ("sp_e", "base_spigot_inset", "mm", "confirmed", "skeleton base_spigot_inset (D-75, R-J13): spigots 100 in from each panel frame end"),
    ("sp_dia", "8 mm", "mm", "source", "locating spigot, stainless, M6 thread (joints register H-05, PROPOSED sizes)"),
    ("sp_proud", "8 mm", "mm", "source", "spigot stands 8 proud of the band top (joints register H-05, PROPOSED)"),
    ("sp_ch", "1 mm", "mm", "assumption", "lead-in chamfer on the spigot top"),
    ("sp_stud", "8 mm", "mm", "assumption", "spigot's M6 stud into its rivnut, with threadlocker"),
    # levelling glides (bought, HOLD: no product named yet)
    ("gl_n_side", "2", "", "calculation", "glides per side band: span about 1.3 m, sag under 0.5 mm (see feature rationale)"),
    ("gl_n_back", "3", "", "calculation", "glides on the back band: 2 spans of 1060 (see feature rationale)"),
    ("gl_e_f", "75 mm", "mm", "calculation",
     "front glide of a side band, behind the band's outer front corner (Y = -dl_y1): its doubler (26 each way) stays 15 behind the front corner key's back face "
     "(Y -636.03) and out of the keyed end's last 30 mm, which the joints register asks BASE to keep clear (PR #99, J-BASE-02)"),
    ("gl_e_b", "150 mm", "mm", "assumption", "back glide of a side band from the back face"),
    ("gl_e_bb", "150 mm", "mm", "assumption", "end glides of the back band from its ends"),
    ("gl_key_hole", "8 mm", "mm", "assumption",
     "hole in the band top for the 5 mm hex key that turns the glide (5.77 across corners, so 1.1 clear each side; levelled before the walls go on). "
     "On the band's centre line it spans 16 to 24 from the outer face, inboard of the PORON strip that runs beside the washer line on its outer side (8 to 16, joints register FR-11)"),
    ("gl_dx", "0 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (BASE group): the doubler's hole centred across its 36 mm width, so the glide stands on the band's centre line"),
    ("gl_nut_hole", "13 mm", "mm", "assumption", "hole in the band bottom for an M10 rivet nut that carries the glide; nut product HOLD"),
    ("gl_pad", "36 mm", "mm", "assumption", "glide pad diameter (envelope, HOLD); stays inside the band's 40 mm width"),
    ("gl_stem", "10 mm", "mm", "assumption", "glide stem M10 (envelope, HOLD)"),
    ("gl_nut_t", "2 mm", "mm", "assumption", "M10 rivet nut head under the band, between the band and the glide pad (HOLD)"),
    ("gl_min", "8.5 mm", "mm", "source",
     "lowest glide setting: the corner keys' button heads hang 3.3 under the band and nothing may come within 5 of the floor (PM ruling on F-018; "
     "joints register PR #99 via the Lead, 2026-11-01)"),
    ("gl_base_min", "gl_min - gl_nut_t", "mm", "calculation",
     "the glide's base must stand this tall (6.5), so that screwed fully home against the M10 rivnut's head it holds the band at gl_min: a hard stop (glide spec, HOLD)"),
    ("gd_l", "54 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (BASE group, the Checker's edge rule): glide doubler at least 52 long, so its ends are 2 hole diameters (26) from the hole; "
     "54 gives 27, clear of that line"),
    ("gd_w", "band_t - 2 * band_wall - 1 mm", "mm", "calculation",
     "glide doubler width: the band's bore less 1 mm, so it bears on the bottom face right next to both side walls"),
    ("gd_t", "5 mm", "mm", "confirmed",
     "load block (glide doubler) 5 mm EN AW-6082 T6 (PM ruling 2026-11-01 on the D-132 PR): about 43 MPa at the worst glide's 0.75 kN "
     "and 97 at 1.7 kN, against about 250 (plate spanning the bore, edges free to turn; feature rationale); clamped with the 1.5 mm "
     "bottom face by the glide's M10 rivnut (grip 6.5)"),
    # back corners: hook-in corner key 111211 (joints register J-BASE-02, D-87; PROPOSED geometry)
    ("ck_x", "30 mm", "mm", "source",
     "corner key length into its carrier: 30, so the carrier's Ø7.0 fixing holes keep 2 diameters from its cut end (joints register #127)"),
    ("ck_y", "35 mm", "mm", "source", "back corner key width across the band (J-BASE-02)"),
    ("ck_z", "75 mm", "mm", "source",
     "back corner key height, standing on the band's bottom wall: 75 (the Joints Engineer, via the Lead 2026-11-01)"),
    ("ck_e", "10.5 mm", "mm", "source",
     "key fixing holes 10.5 from its back face (inside the band) and 7.0 either side of its centre line, so 10.5 from its side faces (joints register #127, J-BASE-02)"),
    ("ck_fy", "6 mm", "mm", "source",
     "back key 111211's fixing holes 6.0 either side of its centre line, so each 7.0 hole stays 14.0 from the side band's cut "
     "end at Y 850 with the key turned either way (D-144: no edge exception; the Joints Engineer's layout, corner-keys.csv)"),
    ("ck_e2", "17.8 mm", "mm", "source",
     "back key 111211's second fixing hole 17.8 from its back face (stepped 7.3 from the first), so the two 838010 flanges "
     "(up to Ø13.6) stand 14.05 apart (D-144, corner-keys.csv)"),
    ("ck_fix_hole", "7 mm", "mm", "source",
     "the keys' fixing screw holes in the carrier's bottom wall, Ø7.0 (J-BASE-02); the side bands carry the back keys since D-129"),
    ("ck_tap", "5 mm", "mm", "source", "M6 tap drill in the key (J-BASE-02)"),
    ("ck_thr_b", "15 mm", "mm", "confirmed",
     "M6 thread in the key's bottom at least 15 deep: the M6 x 16 fixing bolt reaches 12.9 (PM ruling 2026-11-01 on F-017, joints group)"),
    ("ck_tap_d", "18 mm", "mm", "source", "tap drill Ø5.0, 18 deep, under the 15 of full thread (joints register PR #99, J-BASE-02)"),
    ("st_z1", "26 mm", "mm", "source",
     "lower hook stud above the key's bottom: pod Z 37.5 with glide_h 10 and band_wall 1.5, so the keyhole's entry below it clears the tube's bottom corner "
     "(the Joints Engineer, via the Lead 2026-11-01)"),
    ("st_z2", "60 mm", "mm", "source", "upper hook stud above the key's bottom: pod Z 71.5 (the Joints Engineer, via the Lead 2026-11-01)"),
    ("st_gap", "1.8 mm", "mm", "source",
     "hook stud head's underside off the face the next piece hooks onto: its 1.5 wall or plate + 0.3 clearance (J-BASE-02)"),
    ("kh_entry", "12 mm", "mm", "source", "keyhole entry in the front joints' 1.5 end caps, Ø12 (J-BASE-02)"),
    ("kh_slot", "6.5 mm", "mm", "source",
     "keyhole and slot width, 6.5, locates each joint across the band to ±0.25 (Ø5.97 shank, J-BASE-02)"),
    ("kh_drop", "10 mm", "mm", "source",
     "entry centre 10 BELOW the stud's final spot, the slot running 10 up to it: a front piece goes on 10 high, then drops onto the studs "
     "(the Joints Engineer's fix, via the Lead 2026-11-01)"),
    # D-129 (pallet 2): the back corners' keys sit in the side bands' back ends, against their inner walls, and
    # the back band drops in between the side bands (joints register J-BASE-02 and FR-15, corner-keys.csv)
    ("st_hole", "7 mm", "mm", "source",
     "the hook stud bolts' holes through the side band's inner wall at the back corners, Ø7.0 (D-129, J-BASE-02, FR-15)"),
    ("bs_mouth_w", "12 mm", "mm", "source",
     "each back band end cap's slot: 12 wide at the cap's bottom edge, its mouth (D-129, J-BASE-02, FR-15)"),
    ("bs_mouth_h", "6 mm", "mm", "source", "the mouth narrows to the 6.5 slot over the cap's bottom 6 (D-129, FR-15)"),
    ("bs_end", "2 mm", "mm", "source",
     "the slot's closed end centred 2 above the upper stud (Z 73.5): the band rests on its glides, never on the studs (D-129, FR-15)"),
    ("hn_w", "12 mm", "mm", "source",
     "head notch in the back band's bottom wall at each end, 12 wide: the Ø10 head and 1 each side (D-129, FR-15)"),
    ("hn_d", "9 mm", "mm", "source",
     "head notch 9 deep from the band's end: the head's far face is 1.8 + 6 = 7.8 from the side band's face (D-129, FR-15)"),
    ("cap_bevel", "1 mm", "mm", "source",
     "1 x 45 deg bevel on each back band end cap's bottom edge, side-band side, so it slips under the heads (D-129, FR-15)"),
    # D-132 (PM ruling, the owner's question): no floor. The base seal 118001 is a soft lip on the bands' inner
    # faces that presses on the room floor across the glides' range; v1's shadow line under the band stays open
    ("gl_max", "18.5 mm", "mm", "assumption",
     "the band's bottom at the glides' highest setting: 10 mm of travel above the lowest, gl_min (HOLD with the glide product)"),
    ("seal_press", "3 mm", "mm", "assumption", "the lip's least press on the room floor, at the glides' highest setting"),
    ("seal_reach", "gl_max + seal_press", "mm", "calculation",
     "the lip reaches this far below the band's bottom (21.5), so it touches the room floor across the glides' range (D-132)"),
    ("seal_leg", "15 mm", "mm", "assumption", "the lip's leg, bonded to the band's inner face from its bottom edge up (adhesive HOLD)"),
    ("seal_t", "10 mm", "mm", "assumption",
     "the lip's room into the pod from the band's inner face, modelled as an envelope from the room floor to seal_leg above the band's bottom"),
]

ASSEMBLY = ("110000", "BASE", "Đế / sàn")
# key: (part number, name, Vietnamese name, class, parent key)
PARTS = {
    "band_l": ("110101", "BASE - BAND ASSY - SIDE - LH", "Viền chân nhôm - cạnh trái (cụm)", "HS", None),
    "band_l_tube": ("111101", "BASE - BAND TUBE - SIDE - LH", "Viền chân nhôm 100x40 - cạnh trái", "MP", "band_l"),
    "band_b": ("110103", "BASE - BAND ASSY - BACK", "Viền chân nhôm - cạnh sau (cụm)", "HS", None),
    "band_b_tube": ("111103", "BASE - BAND TUBE - BACK", "Viền chân nhôm 100x40 - cạnh sau", "MP", "band_b"),
    "pin": ("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8", "MP", None),
    "washer": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm", "MP", None),
    "glide": ("118002", "BASE - LEVELLING GLIDE - M10 - HOLD", "Chân chỉnh cao", "PI", None),
    "doubler": ("111601", "BASE - GLIDE DOUBLER - COMMON", "Tấm tăng cứng chân chỉnh", "MP", None),
    "key": ("111211", "BASE - CORNER KEY - SQUARE - COMMON", "Ke góc đế - cắt vuông", "MP", None),
    "bolt": ("838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16", "PI", None),
    "bscrew": ("838010", "HARDWARE - FLANGED BUTTON HEAD SCREW - M6 X 12 - ISO 7380-2 A2", "Vít đầu tròn có vành M6 × 12 inox",
               "PI", None),
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2", "Tán rút M6 thép mạ kẽm", "PI", None),
    "cap": ("118003", "BASE - TUBE END CAP - 100 X 40 - BLACK - HOLD", "Nút bịt đầu ống 100x40", "PI", None),
    # the base seal's envelopes (D-132), one per band piece; the parts list counts the seal in metres (its runs)
    "seal_l": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "band_l"),
    "seal_b": ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "band_b"),
}
CLASS_NAME = {"HS": "hardware-fitted subassembly", "BS": "bonded subassembly", "MP": "part we make", "PI": "bought item"}

XL, XR = "-pod_w / 2", "pod_w / 2"
YB, YW = "pod_d / 2", "pod_d / 2 - wall_depth"     # back face; side walls' front edge
XOL = "-pod_w / 2 + outer_t"                        # back panels span frame to frame (D-55)
# P04 panel ranges on the band, linked to the skeleton's named start points (skeleton v4, #94):
# the back bolt lines start at each back FRAME's outer end, X -/+ base_back_x0; the side bolt
# line starts at the side panel's front end, Y base_side_y0 (one seam_gap behind Y -645)
B1_X0 = "(-base_back_x0)"                           # B1's FRAME from here, half_fw wide (to the closing seam)
B2_X0 = "(base_back_x0 - half_fw)"                  # B2's FRAME from here, half_fw wide
# inner point of the mitre between the left side band and DL's outer facet band
# piece (both band_t wide): Y = -dl_y1 + band_t * (L - dy) / dl_x2 with
# L = facet length, dy = dl_y2 - dl_y1 (the bisector of the two outer lines)
Y_MITRE_IN = "(-dl_y1 + band_t * (sqrt(dl_x2 ^ 2 + (dl_y2 - dl_y1) ^ 2) - (dl_y2 - dl_y1)) / dl_x2)"

X = adsk.core.Vector3D.create(1, 0, 0)
Y = adsk.core.Vector3D.create(0, 1, 0)
Z = adsk.core.Vector3D.create(0, 0, 1)


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def mm(v_cm):
    return round(v_cm * 10.0, 3)


def p3(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(x_mm * CM, y_mm * CM, z_mm * CM)


def ev(design, expr):
    """Value of a length expression in mm (plain number for unitless)."""
    um = design.unitsManager
    if any(ch.isalpha() for ch in expr):
        try:
            return um.evaluateExpression(expr, "mm") * 10.0
        except RuntimeError:
            return um.evaluateExpression(expr, "")
    return float(expr)


def bbox_mm(entity):
    b = entity.boundingBox
    return tuple(mm(v) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                 b.maxPoint.x, b.maxPoint.y, b.maxPoint.z))


def fmt_box(b):
    return "X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f" % (b[0], b[3], b[1], b[4], b[2], b[5])


def add_base_params(up):
    """BASE's own parameters. A name the skeleton already defines is skipped:
    the skeleton is the single source, so its value wins (printed)."""
    for name, expr, unit, status, src in BASE_PARAMS:
        if up.itemByName(name) is not None:
            print("  BASE parameter %s skipped: the skeleton defines it (%s)" % (name, up.itemByName(name).expression))
            continue
        if up.add(name, vi(expr), unit, "BASE %s: %s" % (status.upper(), src)) is None:
            raise RuntimeError("could not add parameter " + name)


def skeleton_params():
    with open(SKELETON, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), SKELETON)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "PARAMS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("no PARAMS list in " + SKELETON)


# ---------------------------------------------------------------- sketch helpers

def sketch_axis(sk, direction):
    """Which sketch axis a model direction maps to: ('x'|'y', sign)."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(direction.x, direction.y, direction.z))
    dx, dy = e.x - o.x, e.y - o.y
    if abs(dx) > abs(dy):
        return "x", 1 if dx > 0 else -1
    return "y", 1 if dy > 0 else -1


def on_plane(sk, xyz):
    """Sketch-space point for a model point, dropped onto the sketch plane
    (a point off the plane keeps a free coordinate and the sketch is never
    fully constrained)."""
    q = sk.modelToSketchSpace(p3(*xyz))
    return adsk.core.Point3D.create(q.x, q.y, 0)


def orient(axis):
    return (adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation if axis == "x"
            else adsk.fusion.DimensionOrientations.VerticalDimensionOrientation)


def dim_coord(sk, pt, direction, expr, value):
    """Fix pt's model coordinate along `direction` (a model axis lying in the
    sketch plane) to the expression: a distance dimension from the sketch
    origin driven by abs(expr), or an alignment with the origin when it is 0."""
    ax, _sign = sketch_axis(sk, direction)
    if abs(value) < 1e-6:
        if ax == "x":
            sk.geometricConstraints.addVerticalPoints(pt, sk.originPoint)
        else:
            sk.geometricConstraints.addHorizontalPoints(pt, sk.originPoint)
        return
    g = pt.geometry
    tp = adsk.core.Point3D.create(g.x / 2 + 0.7, g.y / 2 + 0.7, 0)
    d = sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, orient(ax), tp)
    d.parameter.expression = "abs(%s)" % expr


def polygon(design, sk, pts, u, v):
    """Closed polygon through pts = [(expr_u, expr_v, (x, y, z) mm), ...] in
    order, fully constrained: an edge parallel to a sketch axis gets a
    horizontal or vertical constraint, and each group of corners that such
    edges tie together gets one dimension from the sketch origin along that
    axis (Fusion over-constrains if both ends of an axis-parallel line are
    dimensioned; the skeleton's poly() does the same)."""
    lines = sk.sketchCurves.sketchLines
    q = [on_plane(sk, xyz) for (_a, _b, xyz) in pts]
    n = len(q)
    verts, edges = [], []
    for i in range(n):
        start = verts[-1] if verts else q[0]
        end = q[i + 1] if i < n - 1 else verts[0]
        ln = lines.addByTwoPoints(start, end)
        edges.append(ln)
        if i == 0:
            verts.append(ln.startSketchPoint)
        if i < n - 1:
            verts.append(ln.endSketchPoint)
    au, _s = sketch_axis(sk, u)
    av, _s = sketch_axis(sk, v)
    on = {au: (0, u), av: (1, v)}
    gc = sk.geometricConstraints
    for sa in ("x", "y"):
        group = list(range(n))

        def root(i):
            while group[i] != i:
                i = group[i]
            return i
        for i, ln in enumerate(edges):
            ga, gb = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs((ga.x - gb.x) if sa == "x" else (ga.y - gb.y)) < 1e-7:
                (gc.addVertical if sa == "x" else gc.addHorizontal)(ln)
                group[root((i + 1) % n)] = root(i)
        k, direction = on[sa]
        for i in range(n):
            if root(i) != i:
                continue
            xyz = pts[i][2]
            val = xyz[0] * direction.x + xyz[1] * direction.y + xyz[2] * direction.z
            dim_coord(sk, verts[i], direction, pts[i][k], val)
    return verts


def circle_at(sk, xyz, dia_expr, dia_mm, u, v, eu, ev_):
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(on_plane(sk, xyz), dia_mm / 2 * CM)
    g = c.centerSketchPoint.geometry
    d = sk.sketchDimensions.addDiameterDimension(c, adsk.core.Point3D.create(g.x + 1, g.y + 1, 0))
    d.parameter.expression = dia_expr
    uu = xyz[0] * u.x + xyz[1] * u.y + xyz[2] * u.z
    vv = xyz[0] * v.x + xyz[1] * v.y + xyz[2] * v.z
    dim_coord(sk, c.centerSketchPoint, u, eu, uu)
    dim_coord(sk, c.centerSketchPoint, v, ev_, vv)
    return c


def check_sketch(sk):
    if not sk.isFullyConstrained:
        free = []
        for sp in sk.sketchPoints:
            if not sp.isFullyConstrained:
                g = sp.geometry
                free.append("(%.2f, %.2f)" % (g.x * 10, g.y * 10))
        dims = ["%s=%s" % (d.parameter.name, d.parameter.expression) for d in sk.sketchDimensions]
        raise RuntimeError("sketch not fully constrained: %s; free points (sketch mm) %s; dims %s" % (
            sk.name, free, dims))
    return sk.name


def offset_plane(comp, which, expr, value, name):
    """Construction plane parallel to an origin plane ('xy', 'yz' or 'xz') at
    the model coordinate `value` (mm) given by `expr`. Checks the side: an
    origin plane's normal may point along -axis, and then the offset is negated."""
    base = {"xy": comp.xYConstructionPlane, "yz": comp.yZConstructionPlane,
            "xz": comp.xZConstructionPlane}[which]
    if abs(value) < 1e-6:
        return base
    axis = {"xy": 2, "yz": 0, "xz": 1}[which]
    for e in (expr, "-(%s)" % expr):
        pin = comp.constructionPlanes.createInput()
        pin.setByOffset(base, vi(e))
        pl = comp.constructionPlanes.add(pin)
        o = pl.geometry.origin
        got = (o.x, o.y, o.z)[axis] * 10.0
        if abs(got - value) < 0.01:
            pl.name = name
            return pl
        pl.deleteMe()
    raise RuntimeError("could not place plane %s at %.3f" % (name, value))


def extrude(comp, prof, dist_expr, name, op=None, start_expr=None, body=None):
    """Extrude a profile along its plane normal. A join is made as a new body
    and then combined into `body`: an extrude join that only touches the body
    along a face makes a second body instead of joining."""
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    join = op == adsk.fusion.FeatureOperations.JoinFeatureOperation
    ei = comp.features.extrudeFeatures.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation if join else op)
    if start_expr:
        ei.startExtent = adsk.fusion.OffsetStartDefinition.create(vi(start_expr))
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(dist_expr)),
                        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    if body is not None and not join:
        ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    if join:
        tools = adsk.core.ObjectCollection.create()
        tools.add(f.bodies.item(0))
        ci = comp.features.combineFeatures.createInput(body, tools)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        ci.isKeepToolBodies = False
        cf = comp.features.combineFeatures.add(ci)
        cf.name = name.replace("EXTRUDE", "COMBINE", 1)
    return f


def single_body(comp, name=None):
    """The one body of a part component (a join leaves stale handles)."""
    if comp.bRepBodies.count != 1:
        raise RuntimeError("%s: expected 1 body, found %d" % (comp.name, comp.bRepBodies.count))
    b = comp.bRepBodies.item(0)
    if name:
        b.name = name
    return b


def one_profile(sk):
    if sk.profiles.count != 1:
        raise RuntimeError("%s: expected 1 profile, found %d" % (sk.name, sk.profiles.count))
    return sk.profiles.item(0)


# ---------------------------------------------------------------- document

# key -> its own component, filled when the tree is built: several keys can share a part number (the lip seal's
# envelopes, one per band piece, are all 118001), so a lookup by part number alone would find the first one
COMPONENTS = {}


def find_comp(design, key):
    c = COMPONENTS.get(key)
    if c is not None and c.isValid and c.parentDesign == design:
        return c
    want = PARTS[key][0]
    for c in design.allComponents:
        if c.partNumber == want:
            return c
    raise RuntimeError("component not found: " + want)


def find_occ(design, key):
    want = PARTS[key][0]
    for occ in design.rootComponent.allOccurrences:
        if occ.component.partNumber == want:
            return occ
    raise RuntimeError("occurrence not found: " + want)


def describe(comp, pn, name, vn, cls):
    comp.name = "%s %s" % (pn, name)
    comp.partNumber = pn
    comp.description = "%s | %s | %s | rev %s | DRAFT" % (name, vn, CLASS_NAME.get(cls, cls), REV)


def close_own_documents(app):
    """Close BASE's own documents that earlier runs left open (part designs a drawing start opened, drawings),
    without saving: each is saved in the cloud already, and its open copy has no change of ours to keep. Only
    names of BASE's part numbers (11xxxx_P01_...) are touched; with in_place=1 the active document (our assembly,
    opened by the runner's --doc) stays."""
    keep = app.activeDocument if ARGS.get("in_place") == "1" else None
    closed = []
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        n = d.name
        if n[:2] == "11" and n[:6].isdigit() and n[6:11] == "_P01_" and d != keep:
            closed.append(n + (" (had unsaved changes, dropped)" if d.isModified else ""))
            d.close(False)
    print("own documents left open by earlier runs, closed: %s" % (", ".join(closed) or "none"))


def close_unsaved_builds(app, keep=None):
    """Close earlier unsaved build documents of BASE: the assembly's or a part design's (found by the root part
    number, 110000 or 11xxxx); never a saved document or anyone else's (an unsaved document with no BASE part
    number stays)."""
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        try:   # drawings and other documents have no design product
            dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
        except RuntimeError:
            dd = None
        pn = dd.rootComponent.partNumber if dd else ""
        if dd and not d.isSaved and len(pn) == 6 and pn[:2] == "11" and pn.isdigit() and d != keep:
            print("closed an unsaved BASE build document left open (root %s)" % pn)
            d.close(False)


def wipe(design):
    """Empty the open design (timeline and user parameters), so the same
    cloud file gets the new build as its next version and drawings linked to
    it stay linked."""
    tl = design.timeline
    if tl.count:
        tl.markerPosition = 0
        tl.deleteAllAfterMarker()
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        root.occurrences.item(i).deleteMe()
    up = design.userParameters
    for i in range(up.count - 1, -1, -1):
        up.item(i).deleteMe()


def step1_document(app):
    if ARGS.get("in_place") == "1":
        # the runner's --doc opened our saved document; rebuild it in place
        doc = app.activeDocument
        close_unsaved_builds(app, keep=doc)
        if doc.name != DOC_NAME:
            raise RuntimeError("in_place: the active document is %r, not %r (run with --doc %s)" % (
                doc.name, DOC_NAME, DOC_NAME))
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        wipe(design)
        return build_tree(doc, design)
    if ARGS.get("close_previous", "1") == "1":
        close_unsaved_builds(app)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    return build_tree(doc, design)


def build_tree(doc, design):
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    up = design.userParameters
    n_skel = 0
    for name, expr, unit, status, src in skeleton_params():
        if up.add(name, vi(expr), unit, "SKELETON %s: %s" % (status.upper(), src)) is None:
            raise RuntimeError("could not add skeleton parameter " + name)
        n_skel += 1
    add_base_params(up)
    root = design.rootComponent
    root.partNumber = ASSEMBLY[0]
    # the root component takes the document name; it can't be renamed by script
    root.description = "%s | %s | assembly | rev %s | DRAFT" % (ASSEMBLY[1], ASSEMBLY[2], REV)
    made = {}
    for key, (pn, name, vn, cls, parent) in PARTS.items():
        if key in OWNER_STEP:
            continue                    # imported from its owner's STEP in step 7 (D-95)
        host = root if parent is None else made[parent]
        occ = host.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        describe(occ.component, pn, name, vn, cls)
        made[key] = occ.component
        COMPONENTS[key] = occ.component
        # pin, glide and rivnut: this first copy only holds the component; step 7
        # places the real copies at their holes and then deletes it
    print("step 1: document, %d skeleton parameters (read from %s) + %d BASE parameters" % (
        n_skel, os.path.relpath(SKELETON, REPO), len(BASE_PARAMS)))
    for k in ("pod_w", "pod_d", "glide_h", "band_h", "band_t", "wall_z0", "wall_depth", "outer_t",
              "dl_x2", "dl_y1", "dl_y2"):
        print("  %-12s = %9.3f mm   [%s]" % (k, ev(design, k), up.itemByName(k).expression))
    print("  components: " + ", ".join(c.name for c in design.allComponents))
    return doc, design


# ---------------------------------------------------------------- band tubes

def band_tube(design, key, label, outline, bore, axis_note):
    """Hollow 100 x 40 band tube: plan outline extruded band_h up from the
    band bottom (Z glide_h), then the bore cut leaving band_wall all round.
    outline / bore: polygons as for polygon(); the bore runs past both ends."""
    comp = find_comp(design, key)
    plane = offset_plane(comp, "xy", "glide_h", ev(design, "glide_h"),
                         "PLANE - BAND BOTTOM Z = glide_h")
    sk = comp.sketches.add(plane)
    sk.name = "PLAN - %s - OUTLINE" % label
    polygon(design, sk, outline, X, Y)
    check_sketch(sk)
    f = extrude(comp, one_profile(sk), "band_h", "EXTRUDE - %s - TUBE OUTSIDE" % label)
    body = f.bodies.item(0)
    body.name = "%s - TUBE" % PARTS[key][1]
    sk2 = comp.sketches.add(plane)
    sk2.name = "PLAN - %s - BORE" % label
    polygon(design, sk2, bore, X, Y)
    check_sketch(sk2)
    extrude(comp, one_profile(sk2), "band_h - 2 * band_wall", "CUT - %s - BORE, WALL band_wall" % label,
            op=adsk.fusion.FeatureOperations.CutFeatureOperation, start_expr="band_wall", body=body)
    print("  %-30s %s  (%s)" % (PARTS[key][1], fmt_box(bbox_mm(body)), axis_note))
    return body


def P3(design, ex, ey, ez):
    """(expr along the plane's first axis, expr along its second, xyz mm) for a
    polygon on a YZ plane: the dimensioned pair is (Y, Z)."""
    return (ey, ez, (ev(design, ex), ev(design, ey), ev(design, ez)))


def P(design, ex, ey, ez="0 mm"):
    """(expr_x, expr_y, (x, y, z) mm) for polygon()."""
    return (ex, ey, (ev(design, ex), ev(design, ey), ev(design, ez)))


def step2_band_side_lh(design):
    outline = [
        P(design, XL, YB),
        P(design, "%s + band_t" % XL, YB),
        P(design, "%s + band_t" % XL, Y_MITRE_IN),
        P(design, XL, "-dl_y1"),
    ]
    bore = [
        P(design, "%s + band_wall" % XL, "%s + 20 mm" % YB),
        P(design, "%s + band_t - band_wall" % XL, "%s + 20 mm" % YB),
        P(design, "%s + band_t - band_wall" % XL, "-dl_y1 - 20 mm"),
        P(design, "%s + band_wall" % XL, "-dl_y1 - 20 mm"),
    ]
    print("step 2: left side band (front end mitred to DL's outer facet, back end square to the back face, "
          "for its key and flat cap, D-129)")
    band_tube(design, "band_l_tube", "SIDE LH", outline, bore, "length along Y")


def step3_band_back(design):
    outline = [
        P(design, "%s + band_t" % XL, "%s - band_t" % YB),
        P(design, "%s - band_t" % XR, "%s - band_t" % YB),
        P(design, "%s - band_t" % XR, YB),
        P(design, "%s + band_t" % XL, YB),
    ]
    # the bore stops band_wall short of each end: the welded 1.5 end plates that take the side bands' key
    # studs in their slots (D-129); made as one body, as FR1's keyed end (P02)
    bore = [
        P(design, "%s + band_t + band_wall" % XL, "%s - band_t + band_wall" % YB),
        P(design, "%s - band_t - band_wall" % XR, "%s - band_t + band_wall" % YB),
        P(design, "%s - band_t - band_wall" % XR, "%s - band_wall" % YB),
        P(design, "%s + band_t + band_wall" % XL, "%s - band_wall" % YB),
    ]
    print("step 3: back band (between the side bands' inner faces, both ends closed by welded end plates, D-129)")
    band_tube(design, "band_b_tube", "BACK", outline, bore, "length along X")


# ---------------------------------------------------------------- holes

def hole(design, key, plane, label, xyz, dims, dia_expr, depth_expr, want_dir,
         pattern=None):
    """A simple hole (Hole feature) at a sketch point on `plane`, drilled along
    want_dir (model vector) to depth_expr, optionally patterned:
    pattern = (axis attribute name, count expr, extent expr)."""
    comp = find_comp(design, key)
    body = comp.bRepBodies.item(0)
    sk = comp.sketches.add(plane)
    sk.name = "HOLE POSITION - %s" % label
    pt = sk.sketchPoints.add(on_plane(sk, xyz))
    for direction, expr in dims:
        val = xyz[0] * direction.x + xyz[1] * direction.y + xyz[2] * direction.z
        dim_coord(sk, pt, direction, expr, val)
    check_sketch(sk)
    holes = comp.features.holeFeatures
    hin = holes.createSimpleInput(vi(dia_expr))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi(depth_expr))
    n = plane.geometry.normal
    # a hole runs against the sketch plane's normal unless flipped
    if -(n.x * want_dir.x + n.y * want_dir.y + n.z * want_dir.z) < 0:
        hin.isDefaultDirection = False
    hin.participantBodies = [body]
    hf = holes.add(hin)
    hf.name = "HOLE - %s" % label
    if pattern:
        axis_name, count_expr, extent_expr = pattern
        coll = adsk.core.ObjectCollection.create()
        coll.add(hf)
        pats = comp.features.rectangularPatternFeatures
        pin = pats.createInput(coll, getattr(comp, axis_name), vi(count_expr), vi(extent_expr),
                               adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
        # direction two defaults to 3 copies 0 mm apart (found by the WALL
        # Engineer): set it to a single instance
        other = "xConstructionAxis" if axis_name != "xConstructionAxis" else "yConstructionAxis"
        pin.setDirectionTwo(getattr(comp, other), vi("1"), vi("1 mm"))
        pat = pats.add(pin)
        pat.name = "PATTERN - %s" % label
    return hf


def holes_of(body, dia_mm):
    """Hole centres from the cylindrical faces of one diameter: list of
    (axis origin mm, axis direction)."""
    out = []
    for f in body.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
            continue
        g = adsk.core.Cylinder.cast(f.geometry)
        if abs(g.radius * 20.0 - dia_mm) < 0.01:
            out.append(((mm(g.origin.x), mm(g.origin.y), mm(g.origin.z)),
                        (round(g.axis.x, 3), round(g.axis.y, 3), round(g.axis.z, 3))))
    return out


def centres(body, dia_mm, along):
    """Unique centres of the holes of one diameter whose axis runs along
    `along`, as the two coordinates across that axis."""
    k = {"x": 0, "y": 1, "z": 2}[along]
    idx = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[along]
    pts = set()
    for org, d in holes_of(body, dia_mm):
        if abs(abs(d[k]) - 1.0) < 1e-3:
            pts.add((round(org[idx[0]], 2), round(org[idx[1]], 2)))
    return sorted(pts)


def step4_band_holes(design):
    holes_side_lh(design)
    holes_back(design)
    print("step 4: band holes")
    report_holes(design)


def holes_side_lh(design):
    back_key_holes(design, "band_l_tube", -1, "BL")
    v = lambda e: ev(design, e)  # noqa: E731
    c = find_comp(design, "band_l_tube")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    down, up, out_x = Z.copy(), Z.copy(), X.copy()
    down.scaleBy(-1)
    out_x.scaleBy(-1)
    xb = "%s + jb_x" % XL
    y1b = "base_side_y0 + jb_e"                             # L1 starts at the skeleton's base_side_y0
    hole(design, "band_l_tube", top, "J-BASE-01 RIVNUT - L1", (v(xb), v(y1b), v("wall_z0")),
         [(X, xb), (Y, y1b)], "rn_hole", "band_wall", down, ("yConstructionAxis", "jb_n", "side_l - 2 * jb_e"))
    y1s = "base_side_y0 + sp_e"
    hole(design, "band_l_tube", top, "SPIGOT RIVNUT - L1", (v(xb), v(y1s), v("wall_z0")),
         [(X, xb), (Y, y1s)], "rn_hole", "band_wall", down, ("yConstructionAxis", "2", "side_l - 2 * sp_e"))
    # J-BASE-02: the front corner key 111212 sits in this band's front end (its carrier, joints
    # register PR #99): 2 x Ø7.0 in the bottom wall, 10 from the key's back face, which is ck_x
    # behind the mitre face's centre, 7.5 either side of the band's centre line
    yk = "(-dl_y1 + %s) / 2 + ck_x - ck_e" % Y_MITRE_IN
    xk = "%s + band_t / 2 - (ck_y / 2 - ck_e)" % XL
    hole(design, "band_l_tube", bot, "CORNER KEY FIXING - FL (111212)", (v(xk), v(yk), v("glide_h")),
         [(X, xk), (Y, yk)], "ck_fix_hole", "band_wall", up, ("xConstructionAxis", "2", "ck_y - 2 * ck_e"))
    xg = "%s + band_t / 2 + gl_dx" % XL
    yg0, gext = "-dl_y1 + gl_e_f", "pod_d / 2 - gl_e_b + dl_y1 - gl_e_f"
    hole(design, "band_l_tube", top, "GLIDE KEY ACCESS - SIDE LH", (v(xg), v(yg0), v("wall_z0")),
         [(X, xg), (Y, yg0)], "gl_key_hole", "band_wall", down, ("yConstructionAxis", "gl_n_side", gext))
    hole(design, "band_l_tube", bot, "GLIDE NUT - SIDE LH", (v(xg), v(yg0), v("glide_h")),
         [(X, xg), (Y, yg0)], "gl_nut_hole", "band_wall", up, ("yConstructionAxis", "gl_n_side", gext))


def back_key_holes(design, key, sign, label):
    """D-129 (joints register J-BASE-02, FR-15, corner-keys.csv): the back corner key 111211 sits in this
    side band's back end, its stud face against the inner wall from inside. 2 x Ø7.0 through the inner
    wall for its hook stud bolts, on the back band's centre line at the studs' heights, and 2 x Ø7.0 in
    the bottom wall for its fixing screws, 6.0 either side of its centre line, ck_e and ck_e2 from its back face (D-144)
    of the centre line. One-point hole sketches, patterned (two circles in one YZ sketch
    over-constrained, 2026-11-01). sign: -1 for the left side band, +1 for the right."""
    v = lambda e: ev(design, e)  # noqa: E731
    c = find_comp(design, key)
    s = "-" if sign < 0 else ""
    x_in = "%s(pod_w / 2 - band_t)" % s                     # the inner wall's outside face
    yk = "%s - band_t / 2" % YB                             # the back band's centre line
    pl = offset_plane(c, "yz", x_in, v(x_in), "PLANE - BAND INNER FACE (BACK KEY STUDS) - %s" % label)
    into = X.copy()
    if sign < 0:
        into.scaleBy(-1)                                    # into the side band: -X on the left, +X on the right
    z1 = "glide_h + band_wall + st_z1"
    hole(design, key, pl, "BACK KEY HOOK STUD BOLTS - %s (111211, D-129)" % label, (v(x_in), v(yk), v(z1)),
         [(Y, yk), (Z, z1)], "st_hole", "band_wall", into, ("zConstructionAxis", "2", "st_z2 - st_z1"))
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    # D-144: two holes, 6.0 either side of the key's centre line, one ck_e and one ck_e2 from its back face; the key
    # is turned 180 deg at the right corner, so the stepped hole goes to the other side there
    up_y = "+" if sign < 0 else "-"                         # the key's +y side, as seen in the pod
    for lab, e, side in (("1", "ck_e", up_y), ("2", "ck_e2", "-" if up_y == "+" else "+")):
        xf = "%s(pod_w / 2 - band_t + band_wall + ck_x - %s)" % (s, e)
        yf = "%s - band_t / 2 %s ck_fy" % (YB, side)
        hole(design, key, bot, "BACK KEY FIXING %s - %s (111211, D-129, D-144)" % (lab, label), (v(xf), v(yf), v("glide_h")),
             [(X, xf), (Y, yf)], "ck_fix_hole", "band_wall", Z)


def cut_prism(comp, body, plane, sk, depth_expr, want_dir, name):
    """Cut the sketch's one profile from body, depth_expr along want_dir (a model vector square to the
    plane), whichever way the plane's normal points."""
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.CutFeatureOperation)
    n = plane.geometry.normal
    along = n.x * want_dir.x + n.y * want_dir.y + n.z * want_dir.z
    direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if along > 0 else \
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(depth_expr)), direc)
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = name
    return f


def PXZ(design, ex, ey, ez):
    """(expr_x, expr_z, (x, y, z) mm) for polygon() on a plane parallel to XZ."""
    return (ex, ez, (ev(design, ex), ev(design, ey), ev(design, ez)))


def back_band_slots(design):
    """D-129 (joints register J-BASE-02, FR-15): the back band is lowered straight down between the side
    bands, so each of its 1.5 end plates has one slot open at its bottom edge, on the band's centre line:
    bs_mouth_w wide at the edge, narrowing to kh_slot over bs_mouth_h, then kh_slot wide up to its round
    closed end bs_end above the upper stud. At each end the bottom wall has a head notch, hn_w wide and
    hn_d deep from the end, for the stud heads to come up into the tube, and each plate's bottom edge a
    cap_bevel x 45 deg bevel on its side-band side. One-polygon sketches and one-point hole sketches."""
    v = lambda e: ev(design, e)  # noqa: E731
    c = find_comp(design, "band_b_tube")
    body = c.bRepBodies.item(0)
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    yc, yf = "%s - band_t / 2" % YB, "%s - band_t" % YB
    z0, zm = "glide_h", "glide_h + bs_mouth_h"
    z_end = "glide_h + band_wall + st_z2 + bs_end"
    front = offset_plane(c, "xz", yf, v(yf), "PLANE - BACK BAND FRONT FACE (END PLATE BEVELS)")
    for sign, label in ((-1, "LEFT"), (1, "RIGHT")):
        s = "-" if sign < 0 else ""
        xe = "%s(pod_w / 2 - band_t)" % s                   # the band's end: the plate's outer face
        into = X.copy()
        if sign > 0:
            into.scaleBy(-1)                                # into the band: +X at its left end, -X at its right
        pl = offset_plane(c, "yz", xe, v(xe), "PLANE - BACK BAND END - %s" % label)
        sk = c.sketches.add(pl)
        sk.name = "END PLATE SLOT - %s - MOUTH AND SLOT (D-129)" % label
        polygon(design, sk, [P3(design, xe, "%s - bs_mouth_w / 2" % yc, z0), P3(design, xe, "%s + bs_mouth_w / 2" % yc, z0),
                             P3(design, xe, "%s + kh_slot / 2" % yc, zm), P3(design, xe, "%s + kh_slot / 2" % yc, z_end),
                             P3(design, xe, "%s - kh_slot / 2" % yc, z_end), P3(design, xe, "%s - kh_slot / 2" % yc, zm)], Y, Z)
        check_sketch(sk)
        cut_prism(c, body, pl, sk, "band_wall", into, "CUT - END PLATE SLOT - %s (D-129)" % label)
        hole(design, "band_b_tube", pl, "END PLATE SLOT END - %s (D-129)" % label, (v(xe), v(yc), v(z_end)),
             [(Y, yc), (Z, z_end)], "kh_slot", "band_wall", into)
        xn = "%s(pod_w / 2 - band_t - hn_d)" % s
        sk2 = c.sketches.add(bot)
        sk2.name = "HEAD NOTCH - %s (D-129)" % label
        polygon(design, sk2, [P(design, xe, "%s - hn_w / 2" % yc), P(design, xn, "%s - hn_w / 2" % yc),
                              P(design, xn, "%s + hn_w / 2" % yc), P(design, xe, "%s + hn_w / 2" % yc)], X, Y)
        check_sketch(sk2)
        cut_prism(c, body, bot, sk2, "band_wall", Z, "CUT - HEAD NOTCH IN THE BOTTOM WALL - %s (D-129)" % label)
        xb = "%s(pod_w / 2 - band_t - cap_bevel)" % s
        sk3 = c.sketches.add(front)
        sk3.name = "END PLATE BEVEL - %s - BOTTOM EDGE, SIDE-BAND SIDE (D-129)" % label
        polygon(design, sk3, [PXZ(design, xe, yf, z0), PXZ(design, xb, yf, z0), PXZ(design, xe, yf, "glide_h + cap_bevel")],
                X, Z)
        check_sketch(sk3)
        cut_prism(c, body, front, sk3, "band_t", Y, "CUT - END PLATE BEVEL - %s (D-129)" % label)


def holes_back(design):
    v = lambda e: ev(design, e)  # noqa: E731
    down, up = Z.copy(), Z.copy()
    down.scaleBy(-1)
    c = find_comp(design, "band_b_tube")
    top = offset_plane(c, "xy", "wall_z0", v("wall_z0"), "PLANE - BAND TOP Z = wall_z0")
    bot = [p for p in c.constructionPlanes if p.name == "PLANE - BAND BOTTOM Z = glide_h"][0]
    yb_line = "%s - jb_x" % YB
    for panel, x0 in (("B1", B1_X0), ("B2", B2_X0)):
        hole(design, "band_b_tube", top, "J-BASE-01 RIVNUT - %s" % panel, (v("%s + jb_e" % x0), v(yb_line), v("wall_z0")),
             [(X, "%s + jb_e" % x0), (Y, yb_line)], "rn_hole", "band_wall", down,
             ("xConstructionAxis", "jb_n", "half_fw - 2 * jb_e"))
        hole(design, "band_b_tube", top, "SPIGOT RIVNUT - %s" % panel, (v("%s + sp_e" % x0), v(yb_line), v("wall_z0")),
             [(X, "%s + sp_e" % x0), (Y, yb_line)], "rn_hole", "band_wall", down,
             ("xConstructionAxis", "2", "half_fw - 2 * sp_e"))
    xg0, yg = "%s + band_t + gl_e_bb" % XL, "%s - band_t / 2 - gl_dx" % YB
    hole(design, "band_b_tube", top, "GLIDE KEY ACCESS - BACK", (v(xg0), v(yg), v("wall_z0")),
         [(X, xg0), (Y, yg)], "gl_key_hole", "band_wall", down,
         ("xConstructionAxis", "gl_n_back", "pod_w - 2 * band_t - 2 * gl_e_bb"))
    hole(design, "band_b_tube", bot, "GLIDE NUT - BACK", (v(xg0), v(yg), v("glide_h")),
         [(X, xg0), (Y, yg)], "gl_nut_hole", "band_wall", up,
         ("xConstructionAxis", "gl_n_back", "pod_w - 2 * band_t - 2 * gl_e_bb"))
    # D-129: no key in this band; its end plates take the side bands' key studs in open slots
    back_band_slots(design)


def report_holes(design):
    rn, gk, gn = ev(design, "rn_hole"), ev(design, "gl_key_hole"), ev(design, "gl_nut_hole")
    for key in ("band_l_tube", "band_b_tube"):
        body = find_comp(design, key).bRepBodies.item(0)
        top = [p for p in centres(body, rn, "z")]
        side = [p for p in centres(body, rn, "x")] if key == "band_l_tube" else centres(body, rn, "y")
        print("  %s" % PARTS[key][1])
        print("    rivnut holes in the top wall (X, Y): %d  %s" % (len(top), top))
        print("    rivnut holes in the inner wall:      %d  %s" % (len(side), side))
        print("    glide key holes (top): %s   glide nut holes (bottom): %s" % (
            centres(body, gk, "z"), centres(body, gn, "z")))


# ---------------------------------------------------------------- corner key

def step5_corner_key(design):
    """The back corners join on hook-in corner keys that the Joints Engineer
    designs (D-87, 12 fewer bolts than a bolted bracket). Since D-129 the key
    111211 sits in each side band's back end: imported from its owner's STEP
    and placed with the hardware in step 7; the side bands' stud and fixing
    holes and the back band's slotted end plates are made in step 4."""
    print("step 5: back corner joint: hook-in key 111211 in the side bands' back ends (J-BASE-02, D-129), placed in step 7")


# ---------------------------------------------------------------- base seal (D-132)

def seal_runs(design):
    """The base seal 118001's runs (D-132): a soft lip along each band piece's inner face at its bottom edge, pressing
    on the room floor, fitted to the band assembly at the factory. Each run: (envelope key, host key, line, from, to,
    length mm, plan rectangle of its envelope as 4 (x expr, y expr) points, seal_t into the pod). At a back corner the
    side band's inner face is covered by the back band's end plate from Y = pod_d/2 - band_t on, so the side band's
    run stops there; the back band's envelope starts seal_t in, past the side band's. P02 adds its pieces' runs."""
    v = lambda e: ev(design, e)  # noqa: E731
    xi, yb = "%s + band_t" % XL, "%s - band_t" % YB
    runs = [("seal_l", "band_l", "X = %.2f (side band LH, inner face)" % v(xi), Y_MITRE_IN, yb,
             [(xi, Y_MITRE_IN), ("%s + seal_t" % xi, Y_MITRE_IN), ("%s + seal_t" % xi, yb), (xi, yb)]),
            # the back band's lip runs between the side bands' lips, which already fill the corners' seal_t squares:
            # its run is its envelope (it counted 2 x seal_t too much before, 2026-11-01)
            ("seal_b", "band_b", "Y = %.2f (back band, inner face)" % v(yb), "%s + seal_t" % xi, "%s - band_t - seal_t" % XR,
             [("%s + seal_t" % xi, "%s - seal_t" % yb), ("%s - band_t - seal_t" % XR, "%s - seal_t" % yb),
              ("%s - band_t - seal_t" % XR, yb), ("%s + seal_t" % xi, yb)])]
    if P02_ON:
        runs += globals()["p02_seal_runs"](design)
    return [(k, h, line, v(a), v(b), round(abs(v(b) - v(a)), 2), pts) for k, h, line, a, b, pts in runs]


def build_seal_envelopes(design):
    """The base seal's envelopes (D-132): per run, its plan rectangle on the room floor (Z 0), seal_t deep into the pod,
    extruded up to seal_leg above the band's bottom: the room its leg and its fin, bent on the room floor, take. The
    real lip is bought by the metre; the parts list counts it from the runs, not from these bodies."""
    n = 0
    sections = globals()["p02_seal_sections"](design) if P02_ON else {}
    cuts = globals()["p02_seal_cuts"](design) if P02_ON else {}
    for key, _host, _line, _a, _b, _ln, pts in seal_runs(design):
        comp = find_comp(design, key)
        if key in sections:
            # a section across the run (p02_seal_sections), one extrude along +Y from its start to its end
            y0, y1, sec = sections[key]
            yv = ev(design, y0)
            pl = offset_plane(comp, "xz", y0, yv, "PLANE - BASE SEAL LIP - SECTION AT THE RUN'S START")
            sk = comp.sketches.add(pl)
            sk.name = "SECTION - BASE SEAL LIP - LEG AND FIN"
            polygon(design, sk, [(ex, ez, (ev(design, ex), yv, ev(design, ez))) for ex, ez in sec], X, Z)
            check_sketch(sk)
            ei = comp.features.extrudeFeatures.createInput(one_profile(sk),
                                                           adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            direc = adsk.fusion.ExtentDirections.PositiveExtentDirection if pl.geometry.normal.y > 0 else \
                adsk.fusion.ExtentDirections.NegativeExtentDirection
            ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi("%s - %s" % (y1, y0))), direc)
            comp.features.extrudeFeatures.add(ei).name = "EXTRUDE - BASE SEAL LIP - SECTION ALONG THE RUN"
        else:
            sk = comp.sketches.add(comp.xYConstructionPlane)
            sk.name = "PLAN - BASE SEAL LIP - ENVELOPE ON THE ROOM FLOOR"
            polygon(design, sk, [P(design, ex, ey) for ex, ey in pts], X, Y)
            check_sketch(sk)
            extrude(comp, one_profile(sk), "glide_h + seal_leg", "EXTRUDE - BASE SEAL LIP - ENVELOPE, UP TO seal_leg ABOVE THE BAND'S BOTTOM")
            if key in cuts:
                # where a plate stands on the lip's fin (p02_seal_cuts): the envelope is cut from z_from up through its
                # top; the fin under the plate stays joined to the leg below it, so the body stays one
                pts_c, z_from = cuts[key]
                skc = comp.sketches.add(comp.xYConstructionPlane)
                skc.name = "PLAN - BASE SEAL LIP - WHERE THE PLATE STANDS ON THE FIN"
                polygon(design, skc, [P(design, ex, ey) for ex, ey in pts_c], X, Y)
                check_sketch(skc)
                ci = comp.features.extrudeFeatures.createInput(one_profile(skc),
                                                               adsk.fusion.FeatureOperations.CutFeatureOperation)
                ci.startExtent = adsk.fusion.OffsetStartDefinition.create(vi(z_from))
                ci.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                    vi("glide_h + seal_leg - (%s) + 1 mm" % z_from)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
                ci.participantBodies = [single_body(comp)]
                comp.features.extrudeFeatures.add(ci).name = "CUT - BASE SEAL LIP - ABOVE THE FIN, WHERE THE PLATE STANDS"
        body = single_body(comp, "%s - ENVELOPE" % PARTS[key][1])
        if key in sections:
            got = bbox_mm(body)
            want_y = (ev(design, sections[key][0]), ev(design, sections[key][1]))
            if abs(got[1] - want_y[0]) > 0.01 or abs(got[4] - want_y[1]) > 0.01:
                raise RuntimeError("%s: section envelope runs Y %.2f..%.2f, not %.2f..%.2f" % (
                    key, got[1], got[4], want_y[0], want_y[1]))
        n += 1
    print("step 6: base seal envelopes: %d runs (D-132)" % n)


# ---------------------------------------------------------------- hardware

def revolve_section(design, comp, name, pts):
    """A round part as one revolve: the half section in the XZ plane (X =
    radius, Z = height, pts as for polygon() with u = X, v = Z) turned 360
    degrees about the Z axis."""
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = "HALF SECTION - %s" % name
    polygon(design, sk, pts, X, Z)
    check_sketch(sk)
    ri = comp.features.revolveFeatures.createInput(
        one_profile(sk), comp.zConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ri.setAngleExtent(False, vi("360 deg"))
    rf = comp.features.revolveFeatures.add(ri)
    rf.name = "REVOLVE - %s" % name
    return single_body(comp, name)


def PZ(design, er, ez):
    """(expr_r, expr_z, (r, 0, z) mm) for a half section in the XZ plane."""
    return (er, ez, (ev(design, er), 0.0, ev(design, ez)))


def build_rivnut(design):
    comp = find_comp(design, "rivnut")
    revolve_section(design, comp, "RIVET NUT M6 CAH2-610-4.2 - ENVELOPE", [
        PZ(design, "3 mm", "-(rn_inst - rn_head_t)"),           # thread bore, M6 (envelope)
        PZ(design, "rn_hole / 2 - 0.065 mm", "-(rn_inst - rn_head_t)"),
        PZ(design, "rn_hole / 2 - 0.065 mm", "0 mm"),
        PZ(design, "rn_flange / 2", "0 mm"),
        PZ(design, "rn_flange / 2", "rn_head_t"),
        PZ(design, "3 mm", "rn_head_t"),
    ])


def build_pin(design):
    """Locating spigot (joints register H-05): Ø8 stainless, sits on its rivnut's
    head and stands sp_proud above the band top; M6 stud into the rivnut."""
    comp = find_comp(design, "pin")
    h = "sp_proud - rn_head_t"
    revolve_section(design, comp, "LOCATING SPIGOT D8", [
        PZ(design, "0 mm", "-sp_stud"),
        PZ(design, "3 mm", "-sp_stud"),                         # M6 stud
        PZ(design, "3 mm", "0 mm"),
        PZ(design, "sp_dia / 2", "0 mm"),
        PZ(design, "sp_dia / 2", "%s - sp_ch" % h),              # lead-in chamfer
        PZ(design, "sp_dia / 2 - sp_ch", h),
        PZ(design, "0 mm", h),
    ])


def build_washer(design):
    """Stop washer (joints register H-08): under each bolt rivnut's head."""
    comp = find_comp(design, "washer")
    revolve_section(design, comp, "STOP WASHER 10.5 X 20 X 1.5", [
        PZ(design, "sw_hole / 2", "0 mm"),
        PZ(design, "sw_d / 2", "0 mm"),
        PZ(design, "sw_d / 2", "sw_t"),
        PZ(design, "sw_hole / 2", "sw_t"),
    ])


def build_doubler(design):
    """Glide doubler: a 3 mm plate inside the band on its bottom face, under the
    glide's M10 rivnut, so the glide load reaches the side walls without bending
    the 1.5 mm face. Width across the band along local X, length along local Y;
    the hole is centred (gl_dx = 0, PM ruling 2026-10-31: 18 mm to each long
    side, 26 to each end)."""
    comp = find_comp(design, "doubler")
    v = lambda e: ev(design, e)  # noqa: E731
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "PLAN - GLIDE DOUBLER"
    polygon(design, sk, [P(design, "-gd_w / 2", "-gd_l / 2"), P(design, "gd_w / 2", "-gd_l / 2"),
                         P(design, "gd_w / 2", "gd_l / 2"), P(design, "-gd_w / 2", "gd_l / 2")], X, Y)
    circle_at(sk, (v("gl_dx"), 0.0, 0.0), "gl_nut_hole", v("gl_nut_hole"), X, Y, "gl_dx", "0 mm")
    check_sketch(sk)
    ring = [pr for pr in sk.profiles if pr.profileLoops.count == 2][0]
    extrude(comp, ring, "gd_t", "EXTRUDE - GLIDE DOUBLER - PLATE gd_t")
    single_body(comp, "GLIDE DOUBLER")


def build_back_key(design):
    """Back corner key 111211, placed by reference (the Joints Engineer owns its model,
    STEP and drawing; PM ruling 2026-11-01): joints register J-BASE-02, sizes of 2026-11-01: a
    6061-T6 block in the back band's open end. Local system: end face at X 0, the
    block running +X into the band, Y across it (centred), Z up from its bottom.
    Threads (PM ruling on F-017): the end-face stud holes tapped M6 through the
    block; the bottom fixing holes M6 with ck_thr_b of full thread."""
    comp = find_comp(design, "key")
    v = lambda e: ev(design, e)  # noqa: E731
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "PLAN - CORNER KEY - SQUARE"
    polygon(design, sk, [P(design, "0 mm", "-ck_y / 2"), P(design, "ck_x", "-ck_y / 2"),
                         P(design, "ck_x", "ck_y / 2"), P(design, "0 mm", "ck_y / 2")], X, Y)
    check_sketch(sk)
    extrude(comp, one_profile(sk), "ck_z", "EXTRUDE - CORNER KEY - BLOCK ck_z")
    single_body(comp, "CORNER KEY - SQUARE")
    up, intox = Z.copy(), X.copy()
    hole(design, "key", comp.xYConstructionPlane, "KEY FIXING - M6 TAP DRILL FROM BELOW",
         (v("ck_x - ck_e"), -v("ck_y / 2 - ck_e"), 0.0), [(X, "ck_x - ck_e"), (Y, "-(ck_y / 2 - ck_e)")], "ck_tap", "ck_tap_d", up,
         ("yConstructionAxis", "2", "ck_y - 2 * ck_e"))
    hole(design, "key", comp.yZConstructionPlane, "HOOK STUD - M6 TAP DRILL THROUGH THE END FACE",
         (0.0, 0.0, v("st_z1")), [(Y, "0 mm"), (Z, "st_z1")], "ck_tap", "ck_x", intox,
         ("zConstructionAxis", "2", "st_z2 - st_z1"))


def build_bolt(design):
    """M6 x 16 ISO 4762 envelope: head bearing face at Z 0, head up, shank down."""
    comp = find_comp(design, "bolt")
    revolve_section(design, comp, "SOCKET HEAD BOLT M6 X 16 - ENVELOPE", [
        PZ(design, "0 mm", "-16 mm"), PZ(design, "3 mm", "-16 mm"), PZ(design, "3 mm", "0 mm"),
        PZ(design, "5 mm", "0 mm"), PZ(design, "5 mm", "6 mm"), PZ(design, "0 mm", "6 mm")])


def build_bscrew(design):
    """M6 x 12 ISO 7380-2 flanged button head envelope (joints register H-31): head bearing face
    at Z 0, head up (flange Ø13.6 x 1, button Ø10.5 to 3.3 tall; sizes unverified), shank down."""
    comp = find_comp(design, "bscrew")
    revolve_section(design, comp, "FLANGED BUTTON HEAD SCREW M6 X 12 - ENVELOPE", [
        PZ(design, "0 mm", "-12 mm"), PZ(design, "3 mm", "-12 mm"), PZ(design, "3 mm", "0 mm"),
        PZ(design, "6.8 mm", "0 mm"), PZ(design, "6.8 mm", "1 mm"), PZ(design, "5.25 mm", "1 mm"),
        PZ(design, "5.25 mm", "3.3 mm"), PZ(design, "0 mm", "3.3 mm")])


def build_glide(design):
    comp = find_comp(design, "glide")
    revolve_section(design, comp, "LEVELLING GLIDE - ENVELOPE (HOLD)", [
        PZ(design, "0 mm", "0 mm"),
        PZ(design, "gl_pad / 2", "0 mm"),
        PZ(design, "gl_pad / 2", "glide_h - gl_nut_t"),
        PZ(design, "gl_stem / 2", "glide_h - gl_nut_t"),
        PZ(design, "gl_stem / 2", "glide_h + band_h / 2"),
        PZ(design, "0 mm", "glide_h + band_h / 2"),
    ])


def build_cap(design):
    """The side band's back-end cap 118003 (D-129): flat, cap_t thick, the size of the band's bore,
    centred on its own origin in Y, so it is placed with its outer face flush with Y = pod_d / 2.
    Product HOLD: this is its envelope."""
    comp = find_comp(design, "cap")
    sk = comp.sketches.add(comp.xZConstructionPlane)
    sk.name = "OUTLINE - TUBE END CAP - THE BAND'S BORE"
    hw = "(band_t / 2 - band_wall)"
    polygon(design, sk, [PZ(design, "-%s" % hw, "band_wall"), PZ(design, hw, "band_wall"),
                         PZ(design, hw, "band_h - band_wall"), PZ(design, "-%s" % hw, "band_h - band_wall")], X, Z)
    check_sketch(sk)
    ei = comp.features.extrudeFeatures.createInput(one_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ei.setSymmetricExtent(vi("cap_t"), True)
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "EXTRUDE - TUBE END CAP - cap_t THICK, SYMMETRIC"
    single_body(comp, PARTS["cap"][1])


def place(design, host_key, key, xyz, rot=None):
    """A copy of a hardware component inside a host assembly (or the root when
    host_key is None) at a point; rot = 'x+' turns its +Z to +X, 'y-' to -Y.
    Positions come from the same expressions as the holes and are set when
    the script runs (see the manifest)."""
    m = adsk.core.Matrix3D.create()
    if isinstance(rot, tuple) and rot[0] == "z":
        # ("z", deg): turned deg about Z (a front key, its +X along its carrier at any angle)
        m.setToRotation(math.radians(rot[1]), Z, adsk.core.Point3D.create(0, 0, 0))
    elif isinstance(rot, tuple) and rot[0] == "hz":
        # ("hz", deg): its +Z laid level, pointing deg in plan (a hook stud out of a mitred stud face)
        m.setToRotation(math.pi / 2, Y, adsk.core.Point3D.create(0, 0, 0))
        r2 = adsk.core.Matrix3D.create()
        r2.setToRotation(math.radians(rot[1]), Z, adsk.core.Point3D.create(0, 0, 0))
        m.transformBy(r2)
    elif rot == "x+":
        m.setToRotation(math.pi / 2, Y, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "y-":
        m.setToRotation(math.pi / 2, X, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "z-90":
        m.setToRotation(-math.pi / 2, Z, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "x-":
        m.setToRotation(-math.pi / 2, Y, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "z-":
        m.setToRotation(math.pi, X, adsk.core.Point3D.create(0, 0, 0))
    elif rot == "z180":
        m.setToRotation(math.pi, Z, adsk.core.Point3D.create(0, 0, 0))
    m.translation = adsk.core.Vector3D.create(xyz[0] * CM, xyz[1] * CM, xyz[2] * CM)
    host = design.rootComponent if host_key is None else find_comp(design, host_key)
    occ = host.occurrences.addExistingComponent(find_comp(design, key), m)
    occ.isLightBulbOn = True
    return occ


def hardware_points(design):
    """(host assembly, item, (x, y, z) mm, rotation) for every hardware copy,
    from the same parameters as the holes. Bolt rivnuts sit on a stop washer;
    spigot rivnuts sit on the band and carry the spigot (joints register 2.1)."""
    v = lambda e: ev(design, e)  # noqa: E731
    out = []
    z_top, sw, head = v("wall_z0"), v("sw_t"), v("rn_head_t")
    n = int(round(v("jb_n")))
    jb_e, sp_e = v("jb_e"), v("sp_e")

    def edge(host, along, start, length, fixed):
        """J-BASE-01 on one panel edge: 4 bolts at the 220 mm rule, 2 spigots."""
        def pt(t, z):
            return (fixed, start + t, z) if along == "y" else (start + t, fixed, z)
        for i in range(n):
            t = jb_e + i * (length - 2 * jb_e) / (n - 1)
            out.append((host, "washer", pt(t, z_top), None))
            out.append((host, "rivnut", pt(t, z_top + sw), None))
        for t in (sp_e, length - sp_e):
            out.append((host, "rivnut", pt(t, z_top), None))
            out.append((host, "pin", pt(t, z_top + head), None))
    edge("band_l", "y", v("base_side_y0"), v("side_l"), v("%s + jb_x" % XL))                  # L1
    for x0 in (B1_X0, B2_X0):                                                                 # B1, B2
        edge("band_b", "x", v(x0), v("half_fw"), v("%s - jb_x" % YB))
    # J-BASE-02 back corner keys (D-129), fitted to the side bands' back ends at the factory: the block
    # against the inner wall from inside, its 2 flanged button head fixing screws from below (no washer),
    # its 2 hook stud bolts through the inner wall with their heads st_gap off its outside face, and the
    # band's flat end cap. The right side band is P02's; without it the right corner's copies stay at the root.
    zk, yk = v("glide_h + band_wall"), v("%s - band_t / 2" % YB)
    for sign, host, krot, srot in ((-1, "band_l", None, "x+"), (1, "band_r" if P02_ON else None, "z180", "x-")):
        xw = sign * v("pod_w / 2 - band_t")                       # the side band's inner wall, outside face
        # the Joints Engineer's key: origin at its back face's centre on its bottom, +X toward the joint
        # (joints README; corner-keys.csv key_back_centre and carrier_dir)
        xk = sign * v("pod_w / 2 - band_t + band_wall + ck_x")    # its back face
        out.append((host, "key", (xk, yk, zk), krot))
        for zz in ("st_z1", "st_z2"):
            out.append((host, "bolt", (xw - sign * v("st_gap"), yk, zk + v(zz)), srot))
        for e, dy in (("ck_e", -sign), ("ck_e2", sign)):           # D-144: the key's (10.5, +6) and (17.8, -6)
            out.append((host, "bscrew", (xk - sign * v(e), yk + dy * v("ck_fy"), v("glide_h")), "z-"))
        out.append((host, "cap", (sign * v("pod_w / 2 - band_t / 2"), v("%s - cap_t / 2" % YB), v("glide_h")), None))
    # glides, screwed into the bands at the factory
    xg = v("%s + band_t / 2 + gl_dx" % XL)
    ng = int(round(v("gl_n_side")))
    yg0, gext = v("-dl_y1 + gl_e_f"), v("pod_d / 2 - gl_e_b + dl_y1 - gl_e_f")
    xd = v("%s + band_t / 2" % XL)                  # the doubler sits centred in the bore
    zd = v("glide_h + band_wall")
    for i in range(ng):
        out.append(("band_l", "glide", (xg, yg0 + i * gext / (ng - 1), 0.0), None))
        out.append(("band_l", "doubler", (xd, yg0 + i * gext / (ng - 1), zd), None))
    nb = int(round(v("gl_n_back")))
    x0, ext = v("%s + band_t + gl_e_bb" % XL), v("pod_w - 2 * band_t - 2 * gl_e_bb")
    for i in range(nb):
        out.append(("band_b", "glide", (x0 + i * ext / (nb - 1), v("%s - band_t / 2 - gl_dx" % YB), 0.0), None))
        out.append(("band_b", "doubler", (x0 + i * ext / (nb - 1), v("%s - band_t / 2" % YB), zd), "z-90"))
    if P02_ON:
        out += globals()["p02_hardware"](design)
    return out


# hardware whose first copy (made in step 1 at the root, only to hold the component) step 7 deletes
HOLDING_KEYS = ("pin", "glide", "rivnut", "washer", "doubler", "key", "bolt", "bscrew", "cap")


# parts BASE places from their owner's STEP (D-95: one source): imported once in step 7, placed like hardware
OWNER_STEP = {
    "key": "v2/03-Manufacturing/joints/111211_P01_BASE-CORNER-KEY-SQUARE-COMMON_STEP.step",
}


def import_owner_part(design, key):
    """Import the owner's STEP of a part into the root (its holding copy, deleted after the placing, as for
    the hardware), keeping its part number and name (register R7). Its geometry is the owner's, not a copy."""
    app = adsk.core.Application.get()
    path = os.path.join(REPO, OWNER_STEP[key])
    if not os.path.exists(path):
        raise RuntimeError("no owner STEP for %s: %s" % (key, path))
    root = design.rootComponent
    before = root.occurrences.count
    if not app.importManager.importToTarget(app.importManager.createSTEPImportOptions(path), root):
        raise RuntimeError("STEP import failed: %s" % path)
    if root.occurrences.count != before + 1:
        raise RuntimeError("the STEP of %s gave %d occurrences, not 1" % (key, root.occurrences.count - before))
    comp = root.occurrences.item(root.occurrences.count - 1).component
    pn, name, vn, cls, _parent = PARTS[key]
    describe(comp, pn, name, vn, cls)
    print("  %s imported from %s: %d body(ies), %s" % (pn, OWNER_STEP[key], comp.bRepBodies.count,
                                                      fmt_box(bbox_mm(comp.bRepBodies.item(0)))))


def step7_hardware(design):
    build_rivnut(design)
    build_pin(design)
    build_washer(design)
    build_doubler(design)
    for k in OWNER_STEP:                     # the Joints Engineer's keys (D-95), not copies: 111211, and P02's
        if k in PARTS:
            import_owner_part(design, k)
    build_bolt(design)
    build_bscrew(design)
    build_glide(design)
    build_cap(design)
    counts = {}
    for host, key, xyz, rot in hardware_points(design):
        place(design, host, key, xyz, rot)
        counts[(host, key)] = counts.get((host, key), 0) + 1
    # remove the holding copies from step 1, so the CAD count equals the BOM count
    root = design.rootComponent
    holding = {PARTS[k][0] for k in HOLDING_KEYS}
    for i in range(root.occurrences.count - 1, -1, -1):
        occ = root.occurrences.item(i)
        if occ.component.partNumber in holding:
            occ.deleteMe()
    print("step 7: hardware placed")
    for (host, key), n in sorted(counts.items()):
        print("  %-30s %-44s x %d" % (PARTS[host][1], PARTS[key][1], n))


# ---------------------------------------------------------------- materials

MATERIALS = {
    # key: (library material, design material name or None, density kg/m3 or None)
    "band_l_tube": ("Aluminum", None, None),
    "band_b_tube": ("Aluminum", None, None),
    "pin": ("Steel", None, None),
    "washer": ("Aluminum", None, None),
    "rivnut": ("Steel", None, None),
    "doubler": ("Aluminum", None, None),
    "key": ("Aluminum", None, None),
    "bolt": ("Steel", None, None),
    "bscrew": ("Steel", None, None),
    "glide": ("Aluminum", "Glide envelope 0.15 kg (ASSUMPTION)", None),
    "cap": ("Aluminum", "Flat PE end cap 950 kg/m3 (ASSUMPTION)", 950.0),
    # the envelope (10 x 25 per metre) at 320 kg/m3 weighs the lip's 0.08 kg/m (assumption)
    "seal_l": ("Aluminum", "Lip seal envelope 320 kg/m3 (ASSUMPTION)", 320.0),
    "seal_b": ("Aluminum", "Lip seal envelope 320 kg/m3 (ASSUMPTION)", 320.0),
}


def step8_materials(design):
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName("Fusion Material Library")
    for key, (libname, dname, rho) in MATERIALS.items():
        base = lib.materials.itemByName(libname)
        mat = base
        if dname:
            mat = design.materials.itemByName(dname)
            if mat is None:
                mat = design.materials.addByCopy(base, dname)
            if rho is None:
                comp = find_comp(design, key)
                vol_cm3 = sum(b.volume for b in comp.bRepBodies)
                rho = 0.15 / (vol_cm3 * 1e-6)
            adsk.core.FloatProperty.cast(mat.materialProperties.itemById("structural_Density")).value = rho
        for b in find_comp(design, key).bRepBodies:
            b.material = mat
    alib = app.materialLibraries.itemByName("Fusion Appearance Library")
    dark = None
    for nm in ("Aluminum - Anodized Rough (Black)", "Aluminum - Anodized Matte (Black)",
               "Aluminum - Anodized Glossy (Black)", "Paint - Enamel Glossy (Black)", "Plastic - Matte (Black)"):
        try:   # an unknown name raises instead of returning None
            a = alib.appearances.itemByName(nm)
        except RuntimeError:
            a = None
        if a is not None:
            dark = design.appearances.itemByName(nm) or design.appearances.addByCopy(a, nm)
            break
    if dark is not None:
        for key in ("band_l_tube", "band_b_tube"):
            for b in find_comp(design, key).bRepBodies:
                b.appearance = dark
    print("step 8: materials (band look: %s)" % (dark.name if dark else "library default"))
    report_mass(design)


def comp_mass(comp):
    return comp.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy).mass


def report_mass(design):
    for key in PARTS:
        comp = find_comp(design, key)
        if comp.bRepBodies.count == 0:
            continue
        m = comp_mass(comp)
        flag = "" if m <= 20.0 else "  OVER 20 kg"
        print("  %-44s %7.3f kg  %s%s" % (comp.name, m, comp.bRepBodies.item(0).material.name, flag))


# ---------------------------------------------------------------- checks

def body_boxes(design):
    """(label, proxy body, occurrence) for every visible body in the assembly."""
    out = []
    for occ in design.rootComponent.allOccurrences:
        if not occ.isLightBulbOn:
            continue
        for b in occ.bRepBodies:
            out.append(("%s @%s" % (occ.component.partNumber, occ.name.split(":")[-1]), b, occ))
    return out


def temp_copy(tbm, body, occ):
    """Temporary copy of a body where it sits in the assembly. A proxy's copy
    can come back in its component's own space; then the occurrence's
    transform is applied (checked against the proxy's bounding box)."""
    t = tbm.copy(body)
    if occ is not None:
        a, b = t.boundingBox, body.boundingBox
        if max(abs(a.minPoint.x - b.minPoint.x), abs(a.minPoint.y - b.minPoint.y),
               abs(a.minPoint.z - b.minPoint.z)) > 1e-4:
            tbm.transform(t, occ.transform2)
    return t


def intersect_volume(tbm, a, b, occ_a=None, occ_b=None):
    ba, bb = a.boundingBox, b.boundingBox
    if not ba.intersects(bb):
        return 0.0
    ta, tb = temp_copy(tbm, a, occ_a), temp_copy(tbm, b, occ_b)
    tbm.booleanOperation(ta, tb, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return ta.volume * 1000.0  # cm3 -> mm3


def skeleton_boxes(design):
    """Skeleton P04 envelopes next to the base, from the same parameters
    (pod_skeleton.py: side panels from YW + seam_gap, back panels BL_X / BR_X,
    all standing at panel_z0)."""
    v = lambda e: ev(design, e)  # noqa: E731
    xl, yb, yw, z0 = v(XL), v(YB), v(YW), v("panel_z0")
    ot, st, ct = v("outer_t"), v("stack_t"), v("cass_t")
    sh, bh, hp = v("side_h"), v("back_ph"), v("half_pw")
    b1, b2 = v(B1_X0), v("pod_w / 2 - outer_t - seam_gap - half_pw")   # the skeleton's skin envelopes
    return [
        ("skeleton L1", (xl, yw + v("seam_gap"), z0, xl + ot, yb, z0 + sh)),
        ("skeleton L1-CASS", (xl + st - ct, yw, z0, xl + st, yb - st + ct, z0 + sh)),
        ("skeleton B1", (b1, yb - ot, z0, b1 + hp, yb, z0 + bh)),
        ("skeleton B2", (b2, yb - ot, z0, b2 + hp, yb, z0 + bh)),
        ("skeleton B1-CASS", (xl + st, yb - st, z0, 0.0, yb - st + ct, z0 + bh)),
    ]


# overlaps made on purpose: (part number prefix, skeleton label, reason)
EXPECTED_WITH_SKELETON = [
    ("838003", "skeleton L1", "rivnut heads sit in clearance holes in the wall's bottom member (WALL)"),
    ("838003", "skeleton B1", "same, back wall"),
    ("838003", "skeleton B2", "same, back wall"),
    ("831001", "skeleton L1", "locating spigots enter the wall's bottom tube (WALL: Ø8.5 hole and 8.5 x 14 slot)"),
    ("831001", "skeleton B1", "same, back wall"),
    ("831001", "skeleton B2", "same, back wall"),
]
EXPECTED_OWN = [
    ("838003", "831001", "spigot stud in the rivnut thread (both modelled as envelopes)"),
    ("838001", "111211", "hook stud threads in the corner key's tapped holes (tap drill modelled, J-BASE-02)"),
    ("838010", "111211", "fixing screw threads in the corner key's tapped holes (tap drill modelled, J-BASE-02)"),
]


def timeline_problems(design):
    """The timeline items that are not healthy, with their messages. A group (such as the one a STEP import makes,
    "Group1" on 2026-11-01) has no health of its own: each of its members is checked instead. A member's index
    can't be read (Fusion raised InternalValidationError on it, 2026-11-01), so nothing here reads one; a line
    that comes twice is listed once. A member whose health can't be read counts as a problem."""
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    out = []

    def note(line):
        if line not in out:
            out.append(line)

    def walk(item):
        if item.isGroup:
            g = adsk.fusion.TimelineGroup.cast(item)
            for j in range(g.count):
                walk(g.item(j))
            return
        try:
            state, msg = item.healthState, item.errorOrWarningMessage
        except RuntimeError as e:
            note("%s: its health can't be read (%s)" % (item.name, e))
            return
        if state != healthy:
            note("%s: %s" % (item.name, msg))
    tl = design.timeline
    for i in range(tl.count):
        walk(tl.item(i))
    return out


def step9_checks(design):
    tl = design.timeline
    bad = timeline_problems(design)
    n_sk, open_sk = 0, []
    for comp in design.allComponents:
        for sk in comp.sketches:
            n_sk += 1
            if not sk.isFullyConstrained:
                open_sk.append("%s / %s" % (comp.partNumber, sk.name))
    print("step 9: checks")
    print("  timeline items %d, not healthy %d %s" % (tl.count, len(bad), bad or ""))
    print("  sketches %d, fully constrained %d %s" % (n_sk, n_sk - len(open_sk), open_sk or ""))
    v = lambda e: ev(design, e)  # noqa: E731
    expect = {
        "band_l_tube": (v(XL), v(Y_MITRE_IN) if v(Y_MITRE_IN) < v("-dl_y1") else v("-dl_y1"), v("glide_h"),
                        v("%s + band_t" % XL), v(YB), v("wall_z0")),
        "band_b_tube": (v("%s + band_t" % XL), v("%s - band_t" % YB), v("glide_h"),
                        v("%s - band_t" % XR), v(YB), v("wall_z0")),
    }
    box_bad = []
    for key, want in expect.items():
        got = bbox_mm(find_comp(design, key).bRepBodies.item(0))
        diff = max(abs(a - b) for a, b in zip(got, want))
        print("  box %-34s %s  %s" % (PARTS[key][1], fmt_box(got), "OK" if diff < 0.05 else "OFF by %.3f" % diff))
        if diff >= 0.05:
            box_bad.append(key)
    # clashes between the base's own parts
    tbm = adsk.fusion.TemporaryBRepManager.get()
    bodies = body_boxes(design)
    own = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            vol = intersect_volume(tbm, bodies[i][1], bodies[j][1], bodies[i][2], bodies[j][2])
            if vol > 1.0:
                a, b = bodies[i][0].split()[0], bodies[j][0].split()[0]
                ok = any({a, b} == {e[0], e[1]} for e in EXPECTED_OWN)
                own.append((bodies[i][0], bodies[j][0], vol, ok))
    unexpected = [c for c in own if not c[3]]
    print("  own clashes over 1 mm3: %d, expected %d, unexpected %d %s" % (
        len(own), len(own) - len(unexpected), len(unexpected),
        ["%s x %s %.1f mm3" % c[:3] for c in unexpected] or ""))
    # clashes with the skeleton's walls and linings
    sk_hits, sk_bad = {}, []
    for label, bx in skeleton_boxes(design):
        ob = adsk.core.OrientedBoundingBox3D.create(
            p3((bx[0] + bx[3]) / 2, (bx[1] + bx[4]) / 2, (bx[2] + bx[5]) / 2),
            X, Y, (bx[3] - bx[0]) * CM, (bx[4] - bx[1]) * CM, (bx[5] - bx[2]) * CM)
        box = tbm.createBox(ob)
        for name, b, occ in bodies:
            vol = intersect_volume(tbm, b, box, occ, None)
            if vol > 1.0:
                pn = name.split()[0]
                ok = any(pn == e[0] and label == e[1] for e in EXPECTED_WITH_SKELETON)
                sk_hits[(pn, label)] = sk_hits.get((pn, label), 0) + 1
                if not ok:
                    sk_bad.append("%s x %s %.1f mm3" % (name, label, vol))
    print("  clashes with skeleton walls and linings: %s; unexpected %d %s" % (
        ", ".join("%s x %s: %d" % (k[0], k[1], n) for k, n in sorted(sk_hits.items())) or "none",
        len(sk_bad), sk_bad or ""))
    # the walls stand on the stops: band top + stop washer + rivnut head = skeleton panel_z0
    top = bbox_mm(find_comp(design, "band_l_tube").bRepBodies.item(0))[5]
    stop = top + v("sw_t") + v("rn_head_t")
    print("  band top Z %.2f = wall_z0 %.2f; stop top Z %.2f vs skeleton panel_z0 %.2f -> %s" % (
        top, v("wall_z0"), stop, v("panel_z0"), "OK" if abs(stop - v("panel_z0")) < 0.01 else "OFF"))
    if abs(stop - v("panel_z0")) >= 0.01:
        box_bad.append("stop height")
    box_bad += back_corner_check(design)
    ok = not bad and not open_sk and not box_bad and not unexpected and not sk_bad
    print("  RESULT: %s" % ("all checks pass" if ok else "CHECKS FAILED"))
    if not ok:
        raise RuntimeError("step 9 checks failed")


def back_corner_check(design):
    """D-129: the back corners as built against the Joints Engineer's corner-keys.csv (one source, D-95):
    each key's back face centre and bottom, the side band's fixing and stud bolt holes, and the back band's
    slot ends. Returns the names of what is off by 0.05 mm or more."""
    path = os.path.join(REPO, "v2/01-CAD-Native/joints/corner-keys.csv")
    with open(path, encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["joint"] in ("back left corner", "back right corner")]
    off = []
    near = lambda got, want: any(abs(g[0] - want[0]) < 0.05 and abs(g[1] - want[1]) < 0.05 for g in got)  # noqa: E731
    keys = [o for o in design.rootComponent.allOccurrences if o.component.partNumber == PARTS["key"][0]]
    back = find_comp(design, "band_b_tube").bRepBodies.item(0)
    slot_ends = centres(back, ev(design, "kh_slot"), "x")
    for r in rows:
        tube = "band_l_tube" if "left" in r["joint"] else "band_r_tube"
        if tube not in PARTS:
            print("  %s: not in this build (P01 scope)" % r["joint"])
            continue
        body = find_comp(design, tube).bRepBodies.item(0)
        fix = centres(body, ev(design, "ck_fix_hole"), "z")
        studs = centres(body, ev(design, "st_hole"), "x")
        want_fix = [(float(r["fix_hole_1_x"]), float(r["fix_hole_1_y"])), (float(r["fix_hole_2_x"]), float(r["fix_hole_2_y"]))]
        want_studs = [(float(r["face_centre_y"]), float(r["stud_z_low"])), (float(r["face_centre_y"]), float(r["stud_z_high"]))]
        want_key = (float(r["key_back_centre_x"]), float(r["key_back_centre_y"]), float(r["key_bottom_z"]))
        got_keys = [tuple(mm(c) for c in (o.transform2.translation.x, o.transform2.translation.y,
                                          o.transform2.translation.z)) for o in keys]
        checks = [
            ("fixing holes", all(near(fix, w) for w in want_fix)),
            ("stud bolt holes", all(near(studs, w) for w in want_studs)),
            ("key position", any(max(abs(a - b) for a, b in zip(g, want_key)) < 0.05 for g in got_keys)),
            ("back band slot end", near(slot_ends, (float(r["face_centre_y"]), float(r["slot_end_z"])))),
        ]
        print("  %s against corner-keys.csv: %s" % (r["joint"], ", ".join(
            "%s %s" % (name, "MATCH" if good else "OFF") for name, good in checks)))
        off += ["%s %s" % (r["joint"], name) for name, good in checks if not good]
    return off


# ---------------------------------------------------------------- save, export

CLOUD = ("Default Project", "FocusPod v2")
F3D_REL = "v2/01-CAD-Native/base/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/base/110000_%s_BASE_STEP.step" % REV


def cloud_folder(app):
    for p in app.data.dataProjects:
        if p.name == CLOUD[0]:
            folder = p.rootFolder.dataFolders.itemByName(CLOUD[1])
            if folder is None:
                raise RuntimeError("no folder %s in %s" % (CLOUD[1], CLOUD[0]))
            return p, folder
    raise RuntimeError("no project " + CLOUD[0])


def _folder_reader():
    """The shared folder reader (tools/fusion/fusion_folder.py, #213): one listing fetch per scan, loaded
    fresh by the runner on every run."""
    import fusion_folder
    print("  folder reader: %s" % fusion_folder.__file__)
    return fusion_folder


def superseded_name(names, name, day):
    """The name an older copy of `name` takes when a new one replaces it: NAME_SUPERSEDED-<day>, or with -2, -3...
    when the folder already has that name (`names`: the names in the folder)."""
    base = "%s_SUPERSEDED-%s" % (name, day)
    if base not in names:
        return base
    n = 2
    while "%s-%d" % (base, n) in names:
        n += 1
    return "%s-%d" % (base, n)


def replace_own(app, folder, name):
    """Before saving `name`: rename our own previous cloud copy (BASE's files only, each made by this script)
    to NAME_SUPERSEDED-<date>, closing it first if it is open. Cloud files are never deleted (PM rule,
    2026-11-01: a deleted file can't come back). Then check, with the shared reader, that a new file of that
    name can be made without a second copy (it raises if an unreadable entry could be it)."""
    import time
    ff = _folder_reader()
    files, _unknown, _others = ff.read_folder(folder, stop_when=lambda fs, u, o: name in fs)
    found = files.get(name, [])
    if found and ARGS.get("replace") != "1":
        raise RuntimeError("'%s' is already in %s/%s; pass --arg replace=1 to replace it" % (name, *CLOUD))
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        if d.name == name and d.isSaved:
            d.close(False)
    names = set(files)
    for df in found:
        new = superseded_name(names, name, time.strftime("%Y-%m-%d", time.gmtime()))
        df.name = new
        names.add(new)
        print("save: renamed our previous cloud file %s to %s (superseded, not deleted)" % (name, new))
    if found:                       # the listing may lag the rename by a moment
        for _ in range(10):
            files, _unknown, _others = ff.read_folder(folder, wait_s=0)
            if name not in files:
                break
            adsk.doEvents()
            time.sleep(3)
    for w in ff.safe_to_create(folder, name):
        print("save: warning: %s" % w)


def count_after_save(folder, name):
    files, unknown, _others = _folder_reader().read_folder(folder, wait_s=0)
    print("save: the folder now holds %d file(s) named %s%s" % (
        len(files.get(name, [])), name, (" (%d unreadable entries)" % len(unknown)) if unknown else ""))


def step_save(app, doc):
    proj, folder = cloud_folder(app)
    replace_own(app, folder, DOC_NAME)
    app.data.activeProject = proj
    if not doc.saveAs(DOC_NAME, folder, "Spaceship BASE rev %s, DRAFT, built by "
                      "v2/01-CAD-Native/base/base_build.py" % REV, ""):
        raise RuntimeError("saveAs failed")
    print("save: %s saved to %s / %s" % (DOC_NAME, *CLOUD))
    count_after_save(folder, DOC_NAME)


def save_subassemblies(app, design, keys):
    """Each hardware-fitted or bonded subassembly as its own cloud design (Fusion's
    Save Copy As on its component), for its assembly drawing: every assembly keeps
    a drawing (D-89). The copy is the component as built here, in pod coordinates,
    with its parts and hardware; it is remade by every build."""
    import time
    proj, folder = cloud_folder(app)
    app.data.activeProject = proj
    for key in keys:
        pn, name, _vn, _cls, _parent = PARTS[key]
        doc_name = file_name(pn, name, "CAD")
        try:
            replace_own(app, folder, doc_name)
            fut = find_comp(design, key).saveCopyAs(
                doc_name, folder, "Spaceship %s rev %s, DRAFT, copy of %s from base_build.py" % (pn, REV, DOC_NAME), "")
            t0 = time.time()
            while fut.uploadState == adsk.core.UploadStates.UploadProcessing and time.time() - t0 < 240:
                adsk.doEvents()
                time.sleep(1)
            state = {adsk.core.UploadStates.UploadFinished: "saved",
                     adsk.core.UploadStates.UploadFailed: "FAILED",
                     adsk.core.UploadStates.UploadProcessing: "STILL UPLOADING after 240 s"}.get(fut.uploadState, "?")
            print("copy: subassembly %s -> %s: %s (%.0f s)" % (pn, doc_name, state, time.time() - t0))
            count_after_save(folder, doc_name)
        except Exception as e:  # report and go on: the assembly and part designs stay valid
            print("copy: subassembly %s -> %s FAILED: %s" % (pn, doc_name, e))


def step_export(app, design):
    em = design.exportManager
    f3d, step = os.path.join(REPO, F3D_REL), os.path.join(REPO, STEP_REL)
    for path in (f3d, step):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    if not em.execute(em.createFusionArchiveExportOptions(f3d, design.rootComponent)):
        raise RuntimeError("f3d export failed")
    ok = False
    for _ in range(10):
        if em.execute(em.createSTEPExportOptions(step, design.rootComponent)) and os.path.exists(step) \
                and os.path.getsize(step) > 2000:
            ok = True
            break
        adsk.doEvents()
        import time
        time.sleep(3)
    if not ok:
        raise RuntimeError("STEP export failed")
    with open(step, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read().replace(" ", "")
    unit = "cm" if "SI_UNIT(.CENTI.,.METRE.)" in text else ("mm" if "SI_UNIT(.MILLI.,.METRE.)" in text else "?")
    print("export: %s" % F3D_REL)
    print("export: %s (STEP length unit %s, declared in the file; D-13)" % (STEP_REL, unit))
    if "PRODUCT('%s'," % ASSEMBLY[0] not in text:
        raise RuntimeError("STEP: no root product with part number %s" % ASSEMBLY[0])
    if "/*author*/('')" not in text or "/*organization*/('')" not in text:
        raise RuntimeError("STEP header carries an author or organisation; it must stay empty (public repo)")
    box = bbox_mm(design.rootComponent)
    print("  assembly box   %s" % fmt_box(box))
    # read the STEP back in Fusion (it applies the declared unit and the assembly transforms)
    src = app.activeDocument
    imp = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
    d2 = adsk.fusion.Design.cast(imp.products.itemByProductType("DesignProductType"))
    box2 = bbox_mm(d2.rootComponent)
    n_occ = d2.rootComponent.allOccurrences.count
    imp.close(False)
    src.activate()
    diff = max(abs(a - b) for a, b in zip(box, box2))
    print("  STEP re-read   %s  (%d occurrences); largest difference %.3f mm -> %s" % (
        fmt_box(box2), n_occ, diff, "MATCH" if diff < 0.05 else "MISMATCH"))
    if diff >= 0.05:
        raise RuntimeError("STEP box does not match the model")


DATA_REL = "v2/03-Manufacturing/base/110000_%s_BASE_DATA.json" % REV


def export_data(design):
    """Facts read from the CAD for the parts list, cut list and DXF (made
    offline by v2/03-Manufacturing/base/make_outputs.py): parameters, parts
    with mass and box, copies per parent, hole centres, tube cuts, F1 outline."""
    import json
    v = lambda e: ev(design, e)  # noqa: E731
    up = design.userParameters
    params = []
    for p in up:
        text = p.valueType == adsk.fusion.ParameterValueTypes.TextParameterValueType if hasattr(
            adsk.fusion, "ParameterValueTypes") else False
        val = p.textValue if text else (round(p.value * 10.0, 4) if p.unit == "mm" else round(p.value, 4))
        params.append({"name": p.name, "expression": p.expression, "unit": p.unit, "value": val,
                       "comment": p.comment})
    parts = {}
    for key, (pn, name, vn, cls, parent) in PARTS.items():
        comp = find_comp(design, key)
        rec = {"key": key, "pn": pn, "name": name, "name_vi": vn, "class": cls,
               "parent": PARTS[parent][0] if parent else ASSEMBLY[0]}
        if comp.bRepBodies.count:
            b = comp.bRepBodies.item(0)
            rec.update({"mass_kg": round(comp_mass(comp), 4), "box_mm": bbox_mm(b),
                        "volume_mm3": round(b.volume * 1000.0, 1), "material": b.material.name})
        parts[pn] = rec
    copies = {}
    for occ in design.rootComponent.allOccurrences:
        parent = occ.assemblyContext.component.partNumber if occ.assemblyContext else ASSEMBLY[0]
        k = "%s>%s" % (parent, occ.component.partNumber)
        copies[k] = copies.get(k, 0) + 1
    holes = {}
    for key in ("band_l_tube", "band_b_tube"):
        body = find_comp(design, key).bRepBodies.item(0)
        rows = set()
        for org, d in holes_of_all(body):
            rows.add((d[0], d[1], d[2], org[0], org[1], org[2], org[3]))
        holes[PARTS[key][0]] = [{"dia": r[6], "axis": [r[0], r[1], r[2]], "at": [r[3], r[4], r[5]]}
                                for r in sorted(rows, key=lambda r: tuple(-1e9 if x is None else x for x in r))]
    yi, yo = v(Y_MITRE_IN), v("-dl_y1")
    tubes = {
        PARTS["band_l_tube"][0]: {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "Y",
            "outer_face_length": round(v(YB) - yo, 2),
            "inner_face_length": round(v(YB) - yi, 2),
            "front_end": "mitre to DL's outer facet band piece: %.2f deg from square, long point on the outer face"
                         % math.degrees(math.atan2(yi - yo, v("band_t"))),
            "back_end": "square, flush with the back face: its key 111211 inside and the flat end cap 118003 (D-129)"},
        PARTS["band_b_tube"][0]: {
            "section": "100 x 40 x %.1f" % v("band_wall"), "axis": "X",
            "outer_face_length": round(v("pod_w - 2 * band_t - 2 * band_wall"), 2),
            "inner_face_length": round(v("pod_w - 2 * band_t - 2 * band_wall"), 2),
            "front_end": "square at its left end, closed by a welded 1.5 end plate (100 x 40) with its open slot (D-129)",
            "back_end": "the same at its right end; %.1f over both plates" % v("pod_w - 2 * band_t")},
    }
    seal = [{"host": PARTS[h][0], "line": line, "from": a, "to": b, "length_mm": ln}
            for _k, h, line, a, b, ln, _pts in seal_runs(design)]
    out = {"doc": DOC_NAME, "rev": REV, "params": params, "parts": parts, "copies": copies, "holes": holes,
           "tubes": tubes, "seal": seal, "band_finish": up.itemByName("band_finish").textValue}
    if P02_ON:
        globals()["p02_export"](design, out)
    path = os.path.join(REPO, DATA_REL)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print("export: %s (%d parameters, %d parts, %d copy rows)" % (DATA_REL, len(params), len(parts), len(copies)))


def holes_of_all(body):
    """Every hole axis in a body: (centre mm, axis), diameter rounded to 0.01."""
    out = []
    for f in body.faces:
        if f.geometry.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
            g = adsk.core.Cylinder.cast(f.geometry)
            d = round(g.radius * 20.0, 2)
            a = (round(abs(g.axis.x), 3), round(abs(g.axis.y), 3), round(abs(g.axis.z), 3))
            o = [round(c * 10.0, 2) for c in (g.origin.x, g.origin.y, g.origin.z)]
            # keep the two coordinates across the axis; drop the one along it
            for k in range(3):
                if a[k] > 0.99:
                    o[k] = None
            out.append(((o[0], o[1], o[2], d), a))
    return out


# ---------------------------------------------------------------- one part per design

# Each part we make also gets its own saved design, STEP and drawing (a drawing's
# base view shows its whole design; the mechanical check C05 wants a STEP per part).
# Part designs rebuilt with every saved assembly: the band tubes carry the corner keys' holes,
# which follow the joints register.
WITH_ASSEMBLY = ("band_l_tube", "band_b_tube")

# Parts BASE places by reference only: another engineer owns their model, STEP and drawing.
BY_REFERENCE = {
    "key": "the corner keys 111211 to 111214 are the Joints Engineer's (model, STEP and tabulated drawing; "
           "PM ruling 2026-11-01); BASE places them in its band assemblies by reference, at the register's sizes",
}

PART_BUILDS = {
    "band_l_tube": ("step2_band_side_lh", "holes_side_lh"),
    "band_b_tube": ("step3_band_back", "holes_back"),
    "doubler": ("build_doubler",),
    "pin": ("build_pin",),
    "washer": ("build_washer",),
    "key": ("build_back_key",),
}


# Parts whose length runs along the pod's Y axis are turned into their own part
# system for their part design, so the drawing's standard views (Front, Top, Left)
# give a first-angle layout with the length horizontal: two Move features driven by
# parameter expressions. CS-111101: X along the band from its back end (pod Y =
# pod_d/2, D-129), Y from the outer face (pod X = -pod_w/2) inward, Z from the
# band's bottom face (pod Z = glide_h) up. The assembly keeps pod coordinates.
PART_SYSTEM = {
    "band_l_tube": ("90 deg", "pod_d / 2", "pod_w / 2", "-glide_h"),
}


def to_part_system(design, comp, key):
    angle, tx, ty, tz = PART_SYSTEM[key]
    bodies = adsk.core.ObjectCollection.create()
    bodies.add(comp.bRepBodies.item(0))
    mf = comp.features.moveFeatures
    mi = mf.createInput2(bodies)
    mi.defineAsRotate(comp.zConstructionAxis, vi(angle))
    f1 = mf.add(mi)
    f1.name = "MOVE - PART SYSTEM: TURN %s ABOUT Z" % angle.upper()
    bodies = adsk.core.ObjectCollection.create()
    bodies.add(comp.bRepBodies.item(0))
    mi = mf.createInput2(bodies)
    mi.defineAsTranslateXYZ(vi(tx), vi(ty), vi(tz), True)
    f2 = mf.add(mi)
    f2.name = "MOVE - PART SYSTEM: ORIGIN AT THE BACK END, OUTER FACE, BOTTOM"
    print("  part system: turned %s about Z, moved by (%s, %s, %s): %s" % (
        angle, tx, ty, tz, fmt_box(bbox_mm(comp.bRepBodies.item(0)))))


def file_name(pn, name, doctype):
    """PARTNO_REV_DESCRIPTIVE-NAME_DOCTYPE (conventions section 7): ASCII
    capitals, words joined by hyphens."""
    t = name.replace("Ø", "D").replace("(HOLD)", "").upper()
    words = []
    for w in t.replace(" - ", " ").replace("-", " ").split():     # DOOR-END: two words, joined again by a hyphen
        w = "".join(ch for ch in w if ch.isalnum() or ch == ".")
        if w:
            words.append(w)
    return "%s_%s_%s_%s" % (pn, REV, "-".join(words), doctype)


def build_part(app, key):
    pn, name, vn, cls, _parent = PARTS[key]
    doc_name = file_name(pn, name, "CAD")
    close_unsaved_builds(app)
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    up = design.userParameters
    for pname, expr, unit, status, src in skeleton_params():
        up.add(pname, vi(expr), unit, "SKELETON %s: %s" % (status.upper(), src))
    add_base_params(up)
    root = design.rootComponent
    root.partNumber = pn
    root.description = "%s | %s | %s | rev %s | DRAFT" % (name, vn, CLASS_NAME.get(cls, cls), REV)
    print("part %s: %s (%d parameters)" % (pn, doc_name, up.count))
    for fn in PART_BUILDS[key]:
        globals()[fn](design)
    if key in PART_SYSTEM:
        to_part_system(design, root, key)
    lib = app.materialLibraries.itemByName("Fusion Material Library")
    libname, dname, rho = MATERIALS[key]
    mat = lib.materials.itemByName(libname)
    if dname:
        mat = design.materials.itemByName(dname) or design.materials.addByCopy(mat, dname)
        if rho:
            adsk.core.FloatProperty.cast(mat.materialProperties.itemById("structural_Density")).value = rho
    for b in root.bRepBodies:
        b.material = mat
    tl = design.timeline
    bad = timeline_problems(design)
    loose = [sk.name for sk in root.sketches if not sk.isFullyConstrained]
    body = root.bRepBodies.item(0)
    print("  %s  mass %.4f kg; timeline %d items, unhealthy %s; sketches %d, loose %s" % (
        fmt_box(bbox_mm(body)), comp_mass(root), tl.count, bad or 0, root.sketches.count, loose or 0))
    if bad or loose or root.bRepBodies.count != 1:
        raise RuntimeError("part %s failed its checks" % pn)
    if ARGS.get("save") == "1":
        proj, folder = cloud_folder(app)
        replace_own(app, folder, doc_name)
        app.data.activeProject = proj
        if not doc.saveAs(doc_name, folder, "Spaceship %s rev %s, DRAFT, built by base_build.py" % (pn, REV), ""):
            raise RuntimeError("saveAs failed")
        print("  saved %s" % doc_name)
        count_after_save(folder, doc_name)
    if ARGS.get("export") == "1":
        em = design.exportManager
        f3d = os.path.join(REPO, "v2/01-CAD-Native/base/%s.f3d" % doc_name)
        step = os.path.join(REPO, "v2/03-Manufacturing/base/%s.step" % file_name(pn, name, "STEP"))
        if not em.execute(em.createFusionArchiveExportOptions(f3d, root)):
            raise RuntimeError("f3d export failed")
        ok = False
        for _ in range(10):
            if em.execute(em.createSTEPExportOptions(step, root)) and os.path.exists(step) \
                    and os.path.getsize(step) > 1000:
                ok = True
                break
            adsk.doEvents()
            import time
            time.sleep(3)
        if not ok:
            raise RuntimeError("STEP export failed")
        imp = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
        d2 = adsk.fusion.Design.cast(imp.products.itemByProductType("DesignProductType"))
        diff = max(abs(a - b) for a, b in zip(bbox_mm(root), bbox_mm(d2.rootComponent)))
        imp.close(False)
        doc.activate()
        print("  exported %s and %s; STEP re-read box difference %.3f mm -> %s" % (
            os.path.relpath(f3d, REPO), os.path.relpath(step, REPO), diff, "MATCH" if diff < 0.05 else "MISMATCH"))
        if diff >= 0.05:
            raise RuntimeError("STEP box mismatch")
    if ARGS.get("save") == "1" or ARGS.get("keep") != "1":
        doc.close(False)


# Subassemblies that get their own design, for their assembly drawings (D-89: every assembly keeps one)
SUB_DESIGNS = ("band_l", "band_b")
# hosts whose hardware copies are the first ones (the others are pasted from them), so a trim hides them
HOLDS_SHARED_COPIES = ("110101",)


def build_subassembly(app, key):
    """A subassembly as its own design: the whole build again in a new document, then every
    top-level occurrence but this one deleted, so its parts and hardware stand in pod
    coordinates as in the assembly. Made by rebuilding, not by Save Copy As (that hung
    Fusion's cloud save on 2026-11-01)."""
    pn, name, vn, cls, _parent = PARTS[key]
    doc_name = file_name(pn, name, "CAD")
    doc, design = step1_document(app)
    for fn in (step2_band_side_lh, step3_band_back, step4_band_holes, step5_corner_key, step6_p02,
               step7_hardware, step8_materials):
        fn(design)
    root = design.rootComponent
    # trim to this subassembly: delete the others, unless one of them holds the first copy of shared
    # hardware (the back band's rivnuts and stop washers are pasted copies of the side band's), in
    # which case it is hidden instead; a drawing shows what is visible
    hidden = []
    for i in range(root.occurrences.count - 1, -1, -1):
        occ = root.occurrences.item(i)
        if occ.component.partNumber == pn:
            continue
        if occ.component.partNumber in HOLDS_SHARED_COPIES:
            occ.isLightBulbOn = False
            hidden.append(occ.component.partNumber)
        else:
            occ.deleteMe()
    if hidden:
        print("  hidden (they hold the first copies of shared hardware): %s" % ", ".join(hidden))
    root.partNumber = pn
    root.description = "%s | %s | %s | rev %s | DRAFT" % (name, vn, CLASS_NAME.get(cls, cls), REV)
    tl = design.timeline
    bad = timeline_problems(design)
    print("subassembly %s: %s, %d occurrences, %d timeline items, unhealthy %s" % (
        pn, doc_name, root.allOccurrences.count, tl.count, bad or 0))
    if bad:
        doc.close(False)
        raise RuntimeError("unhealthy timeline after trimming to %s" % pn)
    proj, folder = cloud_folder(app)
    replace_own(app, folder, doc_name)
    app.data.activeProject = proj
    if not doc.saveAs(doc_name, folder, "Spaceship %s rev %s, DRAFT, built by base_build.py" % (pn, REV), ""):
        raise RuntimeError("saveAs failed")
    print("  saved %s" % doc_name)
    count_after_save(folder, doc_name)
    doc.close(False)


def save_sub_designs_hidden(app, doc, design, keys):
    """Each subassembly as its own design from ONE build: every other top-level occurrence hidden, the root
    numbered as the subassembly, then Save As under its name; the next follows from the same open document
    (a full rebuild per subassembly ran Fusion past the runner's limit on 2026-11-01). A drawing shows what
    is visible."""
    root = design.rootComponent
    proj, folder = cloud_folder(app)
    app.data.activeProject = proj
    for key in keys:
        pn, name, vn, cls, _parent = PARTS[key]
        doc_name = file_name(pn, name, "CAD")
        for i in range(root.occurrences.count):
            occ = root.occurrences.item(i)
            occ.isLightBulbOn = occ.component.partNumber == pn
        root.partNumber = pn
        root.description = "%s | %s | %s | rev %s | DRAFT" % (name, vn, CLASS_NAME.get(cls, cls), REV)
        replace_own(app, folder, doc_name)
        if not doc.saveAs(doc_name, folder, "Spaceship %s rev %s, DRAFT, built by base_build.py (rest of BASE hidden)"
                          % (pn, REV), ""):
            raise RuntimeError("saveAs failed for %s" % doc_name)
        print("subassembly %s: saved %s, the rest of BASE hidden" % (pn, doc_name))
        count_after_save(folder, doc_name)


# ---------------------------------------------------------------- the next batch (P02)

P02_ON = False


def load_p02():
    """The rest of BASE, batch by batch (base_p02.py, with --arg scope=p02): run in this module's
    namespace, it adds its parameters, parts, steps, hardware and checks to the tables here."""
    global P02_ON
    path = os.path.join(HERE, "base_p02.py")
    with open(path, encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), globals())
    globals()["p02_setup"]()
    P02_ON = True
    print("scope p02: %d more parts, %d more steps, from %s" % (
        len(globals()["P02_BATCH_KEYS"]), len(globals()["P02_STEPS"]), path))


def step6_p02(design):
    """The rest of BASE (base_p02.py), when the run has --arg scope=p02, then the base seal's envelopes on every band
    piece built so far. The pod has no floor (D-132)."""
    if P02_ON:
        for fn in globals()["P02_STEPS"]:
            fn(design)
    else:
        print("step 6: no P02 parts in this run")
    build_seal_envelopes(design)


# ---------------------------------------------------------------- main

def run(_context):
    app = adsk.core.Application.get()
    close_own_documents(app)
    close_unsaved_builds(app)
    try:
        build_run(app)
    except Exception:
        # a run that stops part way leaves no unsaved BASE document for the next team's script (PM, 2026-11-01);
        # saved documents stay as they are; --arg keep=1 keeps the unsaved ones open to look at
        if ARGS.get("keep") != "1":
            close_unsaved_builds(app)
        raise


def build_run(app):
    if ARGS.get("scope") == "p02":
        load_p02()
    if ARGS.get("part"):
        for key in ARGS["part"].split(","):
            build_part(app, key.strip())
        return
    doc, design = step1_document(app)
    steps = [None, None, step2_band_side_lh, step3_band_back, step4_band_holes, step5_corner_key,
             step6_p02, step7_hardware, step8_materials, step9_checks]
    last = min(STOP_AFTER, len(steps) - 1)
    for n in range(2, last + 1):
        steps[n](design)
    print("done through step %d" % last)
    if last == len(steps) - 1 and ARGS.get("sub_only") == "1":
        # the subassembly designs from this one build (others hidden); 110000 itself is not saved again
        keys = [k.strip() for k in ARGS.get("sub_list", ",".join(SUB_DESIGNS)).split(",") if k.strip()]
        save_sub_designs_hidden(app, doc, design, keys)
        doc.close(False)
        return
    if last == len(steps) - 1:
        if ARGS.get("in_place") == "1":
            # save first, so the exports come from a saved version (PR #6 review)
            if not doc.save("rev %s build by v2/01-CAD-Native/base/base_build.py" % REV):
                raise RuntimeError("save failed")
            print("saved: %s, version %s" % (doc.name, doc.dataFile.versionNumber if doc.dataFile else "?"))
        elif ARGS.get("save") == "1":
            step_save(app, doc)
        if ARGS.get("export") == "1":
            step_export(app, design)
            export_data(design)
        if ARGS.get("save") == "1" and ARGS.get("sub_list"):
            save_sub_designs_hidden(app, doc, design,
                                    [k.strip() for k in ARGS["sub_list"].split(",") if k.strip()])
        if ARGS.get("save") == "1" and ARGS.get("sub_assys"):
            save_subassemblies(app, design, [k.strip() for k in ARGS["sub_assys"].split(",") if k.strip()])
    if ARGS.get("in_place") != "1" and ARGS.get("keep") != "1" and ARGS.get("save") != "1":
        doc.close(False)
        print("closed the unsaved build document (pass --arg keep=1 to keep it open)")
    elif ARGS.get("save") == "1" and ARGS.get("in_place") != "1":
        doc.close(False)          # saved and exported: free Fusion for the next run
    if ARGS.get("save") == "1" and ARGS.get("in_place") != "1" and ARGS.get("sub_designs", "0") == "1" \
            and last == len(steps) - 1:
        for key in SUB_DESIGNS:
            try:
                build_subassembly(app, key)
            except Exception as e:  # report and go on: the assembly and part designs stay valid
                print("subassembly %s FAILED: %s" % (PARTS[key][0], e))
                close_unsaved_builds(app)
                for i in range(app.documents.count - 1, -1, -1):     # our own unsaved trimmed copy
                    d = app.documents.item(i)
                    try:
                        dd = adsk.fusion.Design.cast(d.products.itemByProductType("DesignProductType"))
                    except RuntimeError:
                        dd = None
                    if dd and not d.isSaved and dd.rootComponent.partNumber == PARTS[key][0]:
                        d.close(False)
    parts = [k.strip() for k in ARGS.get("also_parts", "").split(",") if k.strip()]
    if ARGS.get("save") == "1" and last == len(steps) - 1:
        if ARGS.get("with_assembly", "1") == "0":
            # --arg with_assembly=0: a short run whose change leaves the band tubes' holes as they are; their part
            # designs and STEPs from the last saved run stay current
            print("part designs %s: not rebuilt in this run (with_assembly=0)" % ", ".join(
                PARTS[k][0] for k in WITH_ASSEMBLY if k in PARTS))
        else:
            parts += [k for k in WITH_ASSEMBLY if k not in parts]
    if parts:
        # one run for the assembly and every part design keeps the shared queue short
        for key in parts:
            if key.strip() in BY_REFERENCE:
                print("part %s: not built here: %s" % (PARTS[key.strip()][0], BY_REFERENCE[key.strip()]))
                continue
            build_part(app, key.strip())
