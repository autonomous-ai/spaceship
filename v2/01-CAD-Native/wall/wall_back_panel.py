"""Spaceship (FocusPod v2) WALL: one back wall panel (B1 to B4) and its lining cassette.

Native, parameter-driven Fusion design, built by script into the ACTIVE document, the same way as
wall_side_panel.py, whose helpers it uses (it runs that file first as a library, then replaces its
tables and builders with the back wall's). One run builds one document:

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_back_panel.py \
        --doc 210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD --doc-new --arg pos=B1 --arg part=panel \
        --arg post=1 --close --discard

Options (--arg KEY=VALUE): pos=B1|B2|B3|B4 (B1 lower left, B2 lower right, B3 upper left, B4 upper right,
seen from outside facing the door, conventions.md section 4); part=panel|cassette|frame|skin|tray|felt (the
fill pieces are built in the panel, D-123); rebuild=1; post=1; skeleton=NAME; stop_after=N (as
wall_side_panel.py). D-117 and D-120: the frame is an assembly of member parts mitred at its 4 corners, the fill
pieces numbered parts straight in the panel, the hardware copies of one part each. D-131: the frame is
welded, galvanized steel box tube in the same sections (corners and T joints welded, no cleats).

Geometry (skeleton P04, pod coordinates): the panel lies in the XZ plane; its thickness runs along Y, with
the ACP's outer face at Y +850 and the room toward -Y. Rows follow the skeleton (B1/B2 from panel_z0, B3/B4
from one seam gap above them up to one seam gap under the ceiling frame). Across the width:
- the outer end meets the side panel's 40 x 40 back stile across the 2.26 corner gap (stopped joint);
- the centre end is the closing seam at X 0 (joints register R-J11, R-J16): the frame stops 2.75 from X 0
  (5.5 frame gap) while the skin stays half_pw wide and overhangs it by 1.62, so the skin seam is 2.26.
Joints, per the joints register (PR #23, #46): every bolted edge at the 220 rule (R-J14), bolt lines on the
tube centre (R-J15, Y 824), Ø7.0 clearance and Ø19 access, Sherex rivnuts on stop washers, spigots 100 from
the ends. The closing seam is a pin joint: B2/B4 hold the rivnut (no stop washer) and the M6 × 25 pin bolt,
driven from their own bay; B1/B3 have a plain Ø7.0 hole.
"""

import os
ARGS = globals().get("SCRIPT_ARGS", {})
POSITION = ARGS.get("pos", "B1").upper()
if POSITION not in ("B1", "B2", "B3", "B4"):
    raise ValueError("pos must be B1, B2, B3 or B4")
_ROW = 1 if POSITION in ("B1", "B2") else 2
SCRIPT_ARGS = dict(ARGS, side="L", row=str(_ROW), part=ARGS.get("part", "panel"))
_LIB = os.path.join(ARGS["repo_root"], "v2/01-CAD-Native/wall/wall_side_panel.py")
with open(_LIB, "r", encoding="utf-8") as _fh:
    exec(compile(_fh.read(), _LIB, "exec"), globals())       # helpers; tables and builders replaced below
# the library's names, bound here as well so tools/fusion/check_api.py (which can't follow the exec) sees them
(HW_PARTS, MM, PART, RESERVED, REV, STOP_AFTER, WANT, bbox, box, ev, hole, hw_site, new_comp,
 pattern_feat, plane_at, re, set_material, size, sketch_axis_of, span, vi, el_params, el_inside, EL_KIND,
 child, member_numbers, fill_numbers, plated_mitre_triangles, place_hardware, poly_on, fill_fits,
 place_piece_copies, sketch_points, place_copies, mitre_plates) = [
    globals()[_n] for _n in (
        "HW_PARTS", "MM", "PART", "RESERVED", "REV", "STOP_AFTER", "WANT", "bbox", "box", "ev",
        "hole", "hw_site", "new_comp", "pattern_feat", "plane_at", "re", "set_material", "size", "sketch_axis_of",
        "span", "vi", "el_params", "el_inside", "EL_KIND", "child", "member_numbers", "fill_numbers",
        "plated_mitre_triangles", "place_hardware", "poly_on", "fill_fits", "place_piece_copies", "sketch_points",
        "place_copies", "mitre_plates")]

import adsk.core      # noqa: E402  (already imported by the library; named here for readers)
import adsk.fusion    # noqa: E402

COL = "L" if POSITION in ("B1", "B3") else "R"
B2_PENDING = ("B2's frame layout (the unit's 373 mm bay framed with welded cross members, PM 2026-11-01; the unit "
              "changes for D-133) is not built yet, so B2's frame, panel and cassette are not made from the even rule")
INSIDE = "-y"                              # the room side of the back wall, for the drawings' Front
ROW = _ROW
BPOS = int(POSITION[1])
CODE = POSITION
LEVEL = "LOWER" if ROW == 1 else "UPPER"
VN = "%s %s" % ("dưới" if ROW == 1 else "trên", "trái" if COL == "L" else "phải")
PARTS = {
    "assy": ("2102%02d" % BPOS, "WALL - PANEL ASSY - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - cụm tấm %s" % VN),
    "frame": ("2112%02d" % BPOS, "WALL - PANEL FRAME - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - khung %s" % VN),
    "skin": ("2114%02d" % BPOS, "WALL - SKIN - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - tấm ốp alu %s" % VN),
    "cass": ("5102%02d" % BPOS, "LINING - CASSETTE - BACK %s - %s" % (LEVEL, POSITION),
             "Cassette lót vách hậu %s (khay thép + tấm tiêu âm)" % VN),
    "tray": ("5112%02d" % BPOS, "LINING - TRAY - BACK %s - %s" % (LEVEL, POSITION), "Khay thép lót vách hậu %s" % VN),
    "felt": ("5114%02d" % BPOS, "LINING - FELT - BACK %s - %s" % (LEVEL, POSITION), "Tấm tiêu âm vách hậu %s" % VN),
    "clip": ("NO-PN-HOLD-H03", "HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED)", "Vùng dành cho kẹp treo cassette (HOLD)"),
}
PARTS.update(HW_PARTS)                     # the joint hardware, numbered by the joints register (library)
for _k, (_pn, _n, _v) in PARTS.items():
    if _pn in RESERVED:
        raise RuntimeError("reserved part number %s (D-28)" % _pn)
ROOT_KEY = {"panel": "assy", "cassette": "cass"}.get(PART, PART)
DOC_NAME = "%s_%s_%s_CAD" % (PARTS[ROOT_KEY][0], REV, re.sub(r"[^A-Z0-9]+", "-", PARTS[ROOT_KEY][1]).strip("-"))
SKELETON_NAMES = ("pod_w", "pod_d", "pod_h", "panel_z0", "back_ph", "back_oh", "half_pw", "half_fw", "close_gap",
                  "stack_t", "outer_t", "cass_t", "lin_gap", "seam_gap", "skin_t", "bond_t", "bolt_edge_inset",
                  "spigot_inset", "n_base_bolt")       # skeleton P04 as updated in place (#58)

_KEEP = {"skin_t", "tube_w", "bond_t", "tube_d", "stud_t", "plate_t", "stile_pitch_max", "skin_setback", "fill_t",
         "bolt_d", "access_d", "rivnut_d", "spigot_d", "spigot_slot", "spigot_edge", "bolt_edge", "pocket_w", "felt_t",
         "tray_t", "tray_h", "lip_w", "bend_r", "felt_c", "gap_h", "clip_zone_h", "clip_zone_dz", "bolt_line_y",
         "stopw_od", "stopw_id", "stopw_t", "rivnut_head_d", "rivnut_head_t", "rivnut_body_d", "rivnut_len", "m6_d",
         "spigot_pin_d", "spigot_proud"}
WALL_PARAMS = [p for p in WALL_PARAMS if p[0] in _KEEP] + [
    ("tube_t", "1.0 mm", "mm", "source",
     "the Joints Engineer's gauges for D-131 (2026-11-01): a back panel's perimeter members (rails, outer and centre "
     "stiles) at 1.0; the studs 0.8"),
    ("lead_in", "1 mm", "mm", "source",
     "joints register 2.10 (R-J9): 1 x 45 degree lead-in on the top edge of each closing-seam face, so the panel "
     "beside it drops in past it without catching the bulb seal"),
    ("pnl_len", "half_pw", "mm", "calculation", "skeleton half_pw: the back panel's skin width (1200.61 on P04)"),
    ("frm_len", "half_fw", "mm", "calculation",
     "the skeleton's half_fw, 1198.99: the frame stops close_gap / 2 from X 0 and 1.62 short of its skin (R-J16)"),
    ("pnl_h", "back_ph" if ROW == 1 else "back_oh - back_ph - seam_gap", "mm", "calculation",
     "skeleton back row height (1118.61 on P04)"),
    ("frm_h", "pnl_h", "mm", "calculation", "the frame fills the row height; the seam gaps are outside it (P04)"),
    ("top_h", "tube_w", "mm", "calculation", "the back panels' top rails stay 20 x 40 (the ceiling's back member is "
                                            "the 40 x 40, R-J3)"),
    ("stile_n_mid", "3", "", "calculation",
     "PM ruling 2026-11-01 (D-135): 3 studs on a back panel, so the skin flexes 1.99 mm under a 100 N push at 274.75 "
     "clear (make_acp_spans.py); a fixed count (the studs are copies held by joints), the pitch follows the width, and "
     "the build refuses a pitch over stile_pitch_max"),
    ("stile_pitch", "(frm_len - tube_w) / (stile_n_mid + 1)", "mm", "calculation", "equal stile pitch, centre to centre"),
    ("stile_len", "frm_h - 2 * tube_w", "mm", "calculation",
     "studs between the rails (square ends, welded T joints, D-131); the perimeter stiles run the full height, mitred (D-117) and welded"),
    ("n_len_bolt", "n_base_bolt", "", "calculation",
     "the skeleton's n_base_bolt (4): also on the horizontal seam and the ceiling back edge (register 2.9; the "
     "skeleton's n_ceil_back_bolt 3 is an old assumption, flagged)"),
    ("len_bolt_pitch", "(frm_len - 2 * bolt_edge) / (n_len_bolt - 1)", "mm", "calculation",
     "253.00 on P04: 220, 473.00, 725.99, 978.99 from the frame's ends (register 2.9; the skeleton's back_base_pitch "
     "uses the 1200.61 skin and gives 253.54, flagged to its owner)"),
    ("n_side_jnt", "3", "", "source", "3 bolts on the back corner and on the closing seam (register 2.9)"),
    ("side_jnt_pitch", "(pnl_h - 2 * bolt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "339.31 on P04: 220, 559.31, 898.61 up the 1118.61 edge (register 2.9)"),
    ("cass_len", "pod_w / 2 - stack_t - seam_gap / 2", "mm", "assumption",
     "PROPOSED (WALL): from the side lining's face to seam_gap / 2 short of X 0. Each cassette hangs on its own "
     "panel's frame and the closing seam moves (5.2 to 5.8, register 2.11), so the skeleton's touching edges at X 0 "
     "could clash; a 2.26 gap matches the skin seam above it (R-J16) and takes the H-14 edge seal"),
    ("cass_h", "pnl_h" if ROW == 1 else "pod_h - outer_t - lin_gap - (panel_z0 + back_ph + seam_gap)", "mm",
     "calculation", "lower: the row height; upper: up to lin_gap under the ceiling frame, floating (D-57; P04)"),
]
# ELECTRICAL's interface features (the library's EL_PARAMS): B2's power unit cut-out, slots and holes in
# B2-CASS, the light feed holes in B4-CASS, the inlet holes and fill cut-outs in panel B2
WALL_PARAMS = WALL_PARAMS + el_params(POSITION, EL_KIND)

# ---------------------------------------------------------------- geometry expressions (back wall)

Y_OUT = "pod_d / 2"
Y_SKIN_IN = "pod_d / 2 - skin_t"
Y_FRAME_OUT = "pod_d / 2 - skin_t - bond_t"
Y_FRAME_IN = "pod_d / 2 - outer_t"
Y_IN = "pod_d / 2 - stack_t"
Y_TRAY_BACK = "pod_d / 2 - stack_t + cass_t"
Y_FELT_FACE = "pod_d / 2 - stack_t + tray_t"
Y_FELT_BACK = "pod_d / 2 - stack_t + tray_t + felt_t"
YC = "pod_d / 2 - skin_t - bond_t - tube_d / 2"      # the frame's centre line in Y (= bolt_line_y, 824)

# across the width: the outer (corner) end and the centre (closing seam) end
# the frame runs half_fw from close_gap / 2 off X 0, the skin half_pw from seam_gap / 2 off X 0, so both outer
# ends meet the side frame's room face one seam_gap away (X -+1201.74 on P04)
X_CASS_OUT = "-(pod_w / 2 - stack_t)" if COL == "L" else "(pod_w / 2 - stack_t)"
if COL == "L":
    X_LOW, X_HIGH = "-close_gap / 2 - half_fw", "-close_gap / 2"                       # frame
    XS_LOW, XS_HIGH = "-seam_gap / 2 - half_pw", "-seam_gap / 2"                       # skin
else:
    X_LOW, X_HIGH = "close_gap / 2", "close_gap / 2 + half_fw"
    XS_LOW, XS_HIGH = "seam_gap / 2", "seam_gap / 2 + half_pw"
XC_LOW, XC_HIGH = (X_CASS_OUT, "-seam_gap / 2") if COL == "L" else ("seam_gap / 2", X_CASS_OUT)   # lining

Z0 = "panel_z0" if ROW == 1 else "panel_z0 + back_ph + seam_gap"
Z1 = "panel_z0 + back_ph" if ROW == 1 else "panel_z0 + back_oh"
Z_CASS1 = Z1 if ROW == 1 else "pod_h - outer_t - lin_gap"


def tube_x(design, comp, label, xr, yr, zr, t="tube_t"):
    """Hollow member running along X (a rail): outer box, then the bore through its length (wall t)."""
    ext = box(design, comp, label + " TUBE", xr, yr, zr)
    b = ext.bodies.item(0)
    yr2, zr2 = span(design, *yr), span(design, *zr)
    box(design, comp, label + " BORE", xr, ("(%s) + %s" % (yr2[0], t), "(%s) - %s" % (yr2[1], t)),
        ("(%s) + %s" % (zr2[0], t), "(%s) - %s" % (zr2[1], t)), "cut", b)
    b.name = label
    return b


def tube_z(design, comp, label, xr, yr, zr, t="tube_t"):
    """Hollow member running along Z (a stile): t is tube_t for the perimeter, stud_t for the studs (D-85)."""
    ext = box(design, comp, label + " TUBE", xr, yr, zr)
    b = ext.bodies.item(0)
    xr2, yr2 = span(design, *xr), span(design, *yr)
    box(design, comp, label + " BORE", ("(%s) + %s" % (xr2[0], t), "(%s) - %s" % (xr2[1], t)),
        ("(%s) + %s" % (yr2[0], t), "(%s) - %s" % (yr2[1], t)), zr, "cut", b)
    b.name = label
    return b


def poly_on_y(design, comp, y_expr, pts, label):
    """The library's poly_on on a plane normal to Y (the back frame's plane): pts = [(x_expr, z_expr), ...]."""
    return poly_on(design, comp, "y", y_expr, pts, label)


def tri_cut_y(design, comp, body, tri, label, what):
    """A triangle in the back frame's plane, cut through one member's depth (Y): a mitre (D-117) or the
    closing seam's lead-in (R-J9)."""
    sk, pl = poly_on_y(design, comp, "(%s) - 1 mm" % Y_FRAME_IN, tri, "%s %s" % (what, label))
    depth = "tube_d + 2 mm" if pl.geometry.normal.y > 0 else "-(tube_d + 2 mm)"
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                   adsk.fusion.FeatureOperations.CutFeatureOperation)
    ei.setDistanceExtent(False, vi(depth))
    ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    f.name = "CUT - %s %s" % (what, label)
    return f


def back_corners():
    """The back frame's 4 corners (D-117): (label, rail, stile, outer corner, inner corner). All four members are
    20 x 40, so the mitre from the outer corner to the inner corner is 45 degrees."""
    xo, xc = _outer_x(), _centre_x()
    to = "+" if COL == "L" else "-"          # from the outer end into the panel
    tc = "-" if COL == "L" else "+"          # from the centre end into the panel
    zb, zt = "(%s) + tube_w" % Z0, "(%s) - top_h" % Z1
    return [("BOTTOM OUTER", "RAIL - BOTTOM", "STILE - OUTER", (xo, Z0), ("(%s) %s tube_w" % (xo, to), zb)),
            ("BOTTOM CENTRE", "RAIL - BOTTOM", "STILE - CENTRE", (xc, Z0), ("(%s) %s tube_w" % (xc, tc), zb)),
            ("TOP OUTER", "RAIL - TOP", "STILE - OUTER", (xo, Z1), ("(%s) %s tube_w" % (xo, to), zt)),
            ("TOP CENTRE", "RAIL - TOP", "STILE - CENTRE", (xc, Z1), ("(%s) %s tube_w" % (xc, tc), zt))]


def build_frame_back(design, frame, out, yf, zs):
    """D-120 and D-131 for a back frame: each member its own component with its master BOM number (the frame keeps
    its number and parents them, D-123), welded in the factory: the 4 perimeter members run to the frame's outer
    corners, mitred there (D-117's geometry) and welded; the studs fit square between the rails and are welded
    there, one component placed by a pattern of copies; no cleat slots (D-131 cancels the cleats). Returns
    {member key: (component, body)}."""
    nums = member_numbers(ARGS["repo_root"], frame.partNumber)
    need = ["RAIL - BOTTOM", "RAIL - TOP", "STILE - OUTER", "STILE - CENTRE", "STILE - MID"]
    missing = [k for k in need if k not in nums]
    if missing:
        raise RuntimeError("no master BOM numbers for %s of frame %s (number-allocation.csv; B3 and B4 get theirs "
                           "when their lists exist, D-123)" % (missing, frame.partNumber))
    members, occs = {}, {}

    def make(key, xr, zr, along, t="tube_t"):
        c, occ = child(frame, *nums[key])
        b = (tube_x if along == "x" else tube_z)(design, c, key, xr, yf, zr, t)
        members[key], occs[key] = (c, b), occ
        return b
    make("RAIL - BOTTOM", (X_LOW, X_HIGH), (Z0, "(%s) + tube_w" % Z0), "x")
    make("RAIL - TOP", (X_LOW, X_HIGH), ("(%s) - top_h" % Z1, Z1), "x")
    if STOP_AFTER <= 2:
        return members
    lo_key, hi_key = ("STILE - OUTER", "STILE - CENTRE") if COL == "L" else ("STILE - CENTRE", "STILE - OUTER")
    make(lo_key, (X_LOW, "(%s) + tube_w" % X_LOW), (Z0, Z1), "z")
    make(hi_key, ("(%s) - tube_w" % X_HIGH, X_HIGH), (Z0, Z1), "z")
    for label, rail, stile, o, i in back_corners():
        # all four members 20 x 40 (the top rail too: top_h = tube_w), so every cut-back is 1.41 (Joints, D-131)
        rt, st = plated_mitre_triangles(design, o, i, "top_h" if "TOP" in label else "tube_w", "tube_w")
        tri_cut_y(design, members[rail][0], members[rail][0].bRepBodies.item(0), rt, "%s (%s)" % (label, rail), "MITRE")
        tri_cut_y(design, members[stile][0], members[stile][0].bRepBodies.item(0), st, "%s (%s)" % (label, stile),
                  "MITRE")
    mitre_plates(design, frame, [(c[0], "top_h" if "TOP" in c[0] else "tube_w", "tube_w") for c in back_corners()])
    if ev(design, "stile_pitch") > ev(design, "stile_pitch_max") + 1e-6:
        raise RuntimeError("stud pitch %.2f over stile_pitch_max %.2f: the panel needs another stud (stile_n_mid)" % (
            ev(design, "stile_pitch"), ev(design, "stile_pitch_max")))
    n = int(round(design.userParameters.itemByName("stile_n_mid").value))
    xr = lambda k: ("(%s) + %d * stile_pitch" % (X_LOW, k), "(%s) + %d * stile_pitch + tube_w" % (X_LOW, k))  # noqa: E731
    make("STILE - MID", xr(1), zs, "z", "stud_t")
    # the other studs: copies of the one part, each held by a rigid joint at its place (place_copies, as on the side
    # walls; the occurrence pattern in the frame came out unhealthy in the L1 run of 2026-11-01)
    sc = members["STILE - MID"][0]
    y_out = max(yf, key=lambda e: ev(design, e))
    src = sketch_points(design, sc, "y", y_out, [(xr(1)[0], zs[0])], "STUD REFERENCE")[0]
    dst = sketch_points(design, frame, "y", y_out, [(xr(k)[0], zs[0]) for k in range(2, n + 1)], "STUD PLACES")
    ys = sorted(ev(design, e) for e in yf)
    boxes = [(ev(design, xr(k)[0]), ys[0], ev(design, zs[0]), ev(design, xr(k)[1]), ys[1], ev(design, zs[1]))
             for k in range(2, n + 1)]
    place_copies(design, frame, sc, src, dst, boxes, "STUD")
    for key, (c, _b) in members.items():
        members[key] = (c, c.bRepBodies.item(0))
        out[key] = c.bRepBodies.item(0)
        out[key].name = key
    print("step 2-3: frame of %d member parts, %d stud copies at pitch %.2f, 4 mitred corners" % (
        len(members), round(design.userParameters.itemByName("stile_n_mid").value),
        design.userParameters.itemByName("stile_pitch").value * 10.0))
    return members


def build_panel(design, root):
    if POSITION == "B2" and PART in ("panel", "frame"):
        raise RuntimeError(B2_PENDING)
    out = {}
    want = WANT[PART]
    frame, skin = (new_comp(root, k) if k in want else None for k in ("frame", "skin"))
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin) if c))
    if STOP_AFTER <= 1:
        return out
    yf = (Y_FRAME_OUT, Y_FRAME_IN)
    zs = ("(%s) + tube_w" % Z0, "(%s) - top_h" % Z1)
    members = build_frame_back(design, frame, out, yf, zs) if frame else {}
    if skin:
        plate = box(design, skin, "SKIN PLATE", (XS_LOW, XS_HIGH), (Y_SKIN_IN, Y_OUT),
                    ("(%s) + skin_setback" % Z0, "(%s) - skin_setback" % Z1)).bodies.item(0)
        plate.name = "SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM"
        out[plate.name] = plate
        print("step 4: skin", size(bbox(plate)))
        out[plate.name] = el_skin_holes(design, skin, plate)
    if "fill" in want:
        build_fill_back(design, root, out, yf, zs, members)
    if frame:
        back_joint_features(design, members, out)
    if PART == "panel":
        place_hardware(design, root, members, out)
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "STEEL BOX TUBE GALVANIZED")
    set_material(design, [b for k, b in out.items() if k.startswith("SKIN")], "skin", "ACP 3 MM EV3038")
    set_material(design, [b for k, b in out.items() if k.startswith("FILL")], "fill", "PET FILL 40 MM")
    return out


def _outer_x():
    return X_LOW if COL == "L" else X_HIGH


def _centre_x():
    return X_HIGH if COL == "L" else X_LOW


def bolt_xs(n_expr_count):
    """X of the bolts along a horizontal edge at the 220 rule, from the frame's low end."""
    n = int(round(n_expr_count))
    return ["(%s) + bolt_edge + %d * len_bolt_pitch" % (X_LOW, i) for i in range(n)]


def back_notches(design, zs):
    """The fill's notches (FR-10), 60 x 60 right through the 40 mm batt, beside every bolt this panel drives: the
    bottom rail's bolts (J-BASE-01 or J-WALL-01), the top rail's ceiling bolts (upper panels, J-CEIL-01), the
    corner bolts in the outer stile (J-WALL-02) and, on B2/B4, the closing seam's pin bolts in the centre stile.
    [(label, x range, z range)]."""
    out = []
    n = int(round(design.userParameters.itemByName("n_len_bolt").value))
    for i, xc in enumerate(bolt_xs(n)):
        xr = ("(%s) - pocket_w / 2" % xc, "(%s) + pocket_w / 2" % xc)
        out.append(("BOTTOM BOLT %d" % (i + 1), xr, (zs[0], "(%s) + pocket_w" % zs[0])))
        if ROW == 2:
            out.append(("CEILING BOLT %d" % (i + 1), xr, ("(%s) - pocket_w" % zs[1], zs[1])))
    ends = [("CORNER", _outer_x(), 1 if COL == "L" else -1)]
    if COL == "R":
        ends.append(("CLOSING SEAM", _centre_x(), 1))
    for label, xe, sgn in ends:
        x_in = "(%s) %s tube_w" % (xe, "+" if sgn > 0 else "-")
        xr = (x_in, "(%s) %s pocket_w" % (x_in, "+" if sgn > 0 else "-"))
        for j in range(3):
            zc = "(%s) + bolt_edge + %d * side_jnt_pitch" % (Z0, j)
            out.append(("%s BOLT %d" % (label, j + 1), xr, ("(%s) - pocket_w / 2" % zc, "(%s) + pocket_w / 2" % zc)))
    return out


def build_fill_back(design, parent, out, yf, zs, members):
    """D-120: each bay's piece a numbered part straight in the panel assembly (D-123; WALL's FILL-PIECES list gives
    each bay's form and how it goes in): the box of its bay with the notches beside every bolt this panel drives,
    each cut right through the piece it falls in (D-128). A bay whose form an earlier bay has takes a copy of that
    part, as cut or turned round (the library's place_piece_copies)."""
    nums = fill_numbers(ARGS["repo_root"], CODE)
    fits = fill_fits(ARGS["repo_root"], CODE)
    n = int(round(design.userParameters.itemByName("stile_n_mid").value))
    bays = [("(%s) + tube_w + %d * stile_pitch" % (X_LOW, k), "(%s) + %d * stile_pitch" % (X_LOW, k + 1))
            for k in range(n + 1)]
    if sorted(nums) != list(range(1, len(bays) + 1)):
        raise RuntimeError("fill numbers for %s cover bays %s; the frame has %d bays" % (CODE, sorted(nums), len(bays)))
    ys = sorted(yf, key=lambda e: ev(design, e))
    pieces, built = [], {}
    for k, xr in enumerate(bays):
        pn = nums[k + 1][0]
        if pn in built:
            pieces.append((None, xr, pn))
            continue
        c = child(parent, *nums[k + 1])[0]
        b = box(design, c, "FILL PIECE BAY %d" % (k + 1), xr, yf, zs).bodies.item(0)
        b.name = "FILL - BAY %d" % (k + 1)
        built[pn] = (c, None, (ys[0], xr[0], zs[0]), "x")
        pieces.append((c, xr, pn))

    def bay_of(xr):
        xm = (ev(design, xr[0]) + ev(design, xr[1])) / 2.0
        hit = [i for i, (_c, (x0, x1), _pn) in enumerate(pieces)
               if min(ev(design, x0), ev(design, x1)) < xm < max(ev(design, x0), ev(design, x1))]
        if len(hit) != 1:
            raise RuntimeError("fill notch at X %.1f falls in %d pieces" % (xm, len(hit)))
        return hit[0]
    ym = (ev(design, yf[0]) + ev(design, yf[1])) / 2.0
    copy_open = {}
    for label, xr, zr in back_notches(design, zs):
        i = bay_of(xr)
        c = pieces[i][0]
        if c is None:                          # a copy: its part already carries this notch, as cut or turned
            copy_open.setdefault(i, []).append(((ev(design, xr[0]) + ev(design, xr[1])) / 2.0, ym,
                                                (ev(design, zr[0]) + ev(design, zr[1])) / 2.0))
            continue
        box(design, c, "FILL NOTCH " + label, xr, yf, zr, "cut", c.bRepBodies.item(0))
    el_fill_cutouts(design, pieces[0][0], yf)
    copies = []
    for i, (c, xr, pn) in enumerate(pieces):
        if c is None:
            want = (ev(design, xr[0]), ev(design, ys[0]), ev(design, zs[0]),
                    ev(design, xr[1]), ev(design, ys[1]), ev(design, zs[1]))
            corners = {"low": (ys[0], xr[0], zs[0]), "high_turned": (ys[1], xr[1], zs[0])}
            copies.append((pn, want, corners, fits.get(i + 1, "as cut"), copy_open.get(i, [])))
    place_piece_copies(design, parent, built, copies, "FILL PIECE")
    for c, _xr, _pn in pieces:
        if c is None:
            continue
        if c.bRepBodies.count != 1:
            raise RuntimeError("fill piece %s split into %d bodies" % (c.name, c.bRepBodies.count))
        b = c.bRepBodies.item(0)
        out[b.name] = b
    print("step 5: fill, %d piece parts in %d bays (%d copies), notches at every bolt this panel drives" % (
        len(built), len(pieces), len(copies)))


def lead_in_d117(design, members):
    """1 x 45 degree lead-in on the top edge of the closing-seam face (register 2.10, R-J9), so the panel beside it
    drops in past it without catching the bulb seal. With D-117's mitre that corner is half top rail, half centre
    stile: the same triangle is cut from each, through the frame's depth."""
    xc = _centre_x()
    tc = "-" if COL == "L" else "+"          # from the centre end into the panel
    oc = "+" if COL == "L" else "-"          # out of the panel, past the seam face
    tri = [("(%s) %s lead_in" % (xc, tc), Z1), ("(%s) %s 1 mm" % (xc, oc), "(%s) + 1 mm" % Z1),
           (xc, "(%s) - lead_in" % Z1)]
    for key in ("RAIL - TOP", "STILE - CENTRE"):
        c = members[key][0]
        tri_cut_y(design, c, c.bRepBodies.item(0), tri, "(%s)" % key, "CLOSING SEAM LEAD-IN (R-J9)")


def back_joint_features(design, members, out):
    """Site joint holes per the joints register (V2-ENG-JNT-01 P01), each in its member's own component (D-120)."""
    t = "tube_t"
    (bc, _b), (tc, _t), (oc, _o), (cc, _c) = (members[k] for k in ("RAIL - BOTTOM", "RAIL - TOP", "STILE - OUTER",
                                                                   "STILE - CENTRE"))

    def body(c):
        return c.bRepBodies.item(0)
    x_b1, n_b, p_b = "(%s) + bolt_edge" % X_LOW, "n_len_bolt", "len_bolt_pitch"
    zb0, zb1, zt0, zt1 = Z0, "(%s) + tube_w" % Z0, "(%s) - top_h" % Z1, Z1
    # bottom rail, bolt side: J-BASE-01 (B1, B2) or J-WALL-01 (B3, B4). Spigots: the round hole 100 from the
    # closing-seam end, so the closing gap is set by the round spigots and their distance to the seam face
    # (register 2.11, ST-02: 5.2 to 5.8), and the slot along the edge 100 from the corner end
    a = hole(design, bc, body(bc), "z", zb0, +1, {"x": x_b1, "y": YC}, "bolt_d", t, "BOTTOM RAIL BOLT CLEARANCE 1")
    b = hole(design, bc, body(bc), "z", zb1, -1, {"x": x_b1, "y": YC}, "access_d", t, "BOTTOM RAIL KEY ACCESS 1")
    pattern_feat(bc, [a, b], "x", n_b, p_b, "BOTTOM RAIL BOLT HOLES")
    sgn_out = 1 if COL == "L" else -1
    x_round = "(%s) - %d * spigot_edge" % (_centre_x(), sgn_out)
    x_slot = "(%s) + %d * spigot_edge" % (_outer_x(), sgn_out)
    hole(design, bc, body(bc), "z", zb0, +1, {"x": x_round, "y": YC}, "spigot_d", t, "BOTTOM RAIL SPIGOT ROUND")
    half = "(spigot_slot - spigot_d) / 2"
    box(design, bc, "BOTTOM RAIL SPIGOT SLOT", ("(%s) - %s" % (x_slot, half), "(%s) + %s" % (x_slot, half)),
        ("(%s) - spigot_d / 2" % YC, "(%s) + spigot_d / 2" % YC), (zb0, "(%s) + %s" % (zb0, t)), "cut", body(bc))
    for i, sg in enumerate(("-", "+")):
        hole(design, bc, body(bc), "z", zb0, +1, {"x": "(%s) %s %s" % (x_slot, sg, half), "y": YC}, "spigot_d", t,
             "BOTTOM RAIL SPIGOT SLOT END %d" % (i + 1))
    if ROW == 1:
        # top rail, nut side of J-WALL-01 to B3/B4: rivnuts at the 220 rule, 2 spigot rivnuts 100 from the ends
        r = hole(design, tc, body(tc), "z", zt1, -1, {"x": x_b1, "y": YC}, "rivnut_d", t, "TOP RAIL RIVNUT 1")
        pattern_feat(tc, [r], "x", n_b, p_b, "TOP RAIL RIVNUTS")
        hw_site("TOP RAIL", "z", zt1, -1, {"x": x_b1, "y": YC}, ("x", n_b, p_b), member="RAIL - TOP")
    else:
        # top rail, bolt side of J-CEIL-01's back edge (the ceiling's 40 x 40 back member holds the rivnuts):
        # Ø7.0 up through the top wall, Ø19 in the bottom wall; spigot rivnuts for the ceiling (FR-04)
        a = hole(design, tc, body(tc), "z", zt1, -1, {"x": x_b1, "y": YC}, "bolt_d", t,
                 "TOP RAIL CEILING BOLT CLEARANCE 1")
        b = hole(design, tc, body(tc), "z", zt0, +1, {"x": x_b1, "y": YC}, "access_d", t,
                 "TOP RAIL CEILING KEY ACCESS 1")
        pattern_feat(tc, [a, b], "x", n_b, p_b, "TOP RAIL CEILING BOLT HOLES")
    # spigot rivnuts 100 from each end, holding the spigots for the panel above (B3, B4) or the ceiling (C1, C2)
    for k, xs in (("LOW X", "(%s) + spigot_edge" % X_LOW), ("HIGH X", "(%s) - spigot_edge" % X_HIGH)):
        hole(design, tc, body(tc), "z", zt1, -1, {"x": xs, "y": YC}, "rivnut_d", t, "TOP RAIL SPIGOT RIVNUT %s" % k)
        hw_site("TOP RAIL SPIGOT %s" % k, "z", zt1, -1, {"x": xs, "y": YC}, washer=False, spigot=True,
                member="RAIL - TOP")
    # outer stile, bolt side of J-WALL-02 (corner): Ø7.0 in its outer wall, Ø19 in its bay-side wall, on the
    # bolt line Y 824, at the 220 rule up the back panel's edge
    xo, xo_in = _outer_x(), "(%s) + %d * tube_w" % (_outer_x(), sgn_out)
    z_j1 = "(%s) + bolt_edge" % Z0
    a = hole(design, oc, body(oc), "x", xo, sgn_out, {"y": "bolt_line_y", "z": z_j1}, "bolt_d", t,
             "OUTER STILE CORNER BOLT CLEARANCE 1")
    b = hole(design, oc, body(oc), "x", xo_in, -sgn_out, {"y": "bolt_line_y", "z": z_j1}, "access_d", t,
             "OUTER STILE CORNER KEY ACCESS 1")
    pattern_feat(oc, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "OUTER STILE CORNER BOLT HOLES")
    # centre stile, the closing seam (R-J11): B1/B3 a plain Ø7.0 in the seam wall; B2/B4 the rivnut (no stop
    # washer) in the seam wall and the Ø19 access in the bay-side wall for driving the pin bolt
    xc, sgn_c = _centre_x(), (1 if COL == "L" else -1)            # toward the seam
    xc_in = "(%s) - %d * tube_w" % (xc, sgn_c)
    if COL == "L":
        a = hole(design, cc, body(cc), "x", xc, -sgn_c, {"y": YC, "z": z_j1}, "bolt_d", t, "CENTRE STILE PIN HOLE 1")
        pattern_feat(cc, [a], "z", "n_side_jnt", "side_jnt_pitch", "CENTRE STILE PIN HOLES")
    else:
        a = hole(design, cc, body(cc), "x", xc, -sgn_c, {"y": YC, "z": z_j1}, "rivnut_d", t,
                 "CENTRE STILE PIN RIVNUT 1")
        b = hole(design, cc, body(cc), "x", xc_in, sgn_c, {"y": YC, "z": z_j1}, "access_d", t,
                 "CENTRE STILE PIN KEY ACCESS 1")
        pattern_feat(cc, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "CENTRE STILE PIN HOLES")
        # the pin's rivnut has no stop washer: the closing gap is set by the spigots (register 2.10)
        hw_site("CENTRE STILE PIN", "x", xc, -sgn_c, {"y": YC, "z": z_j1}, ("z", "n_side_jnt", "side_jnt_pitch"),
                washer=False, member="STILE - CENTRE")
    lead_in_d117(design, members)
    for key, (c, _bb) in members.items():
        members[key] = (c, c.bRepBodies.item(0))
        out[key] = c.bRepBodies.item(0)
    print("step 6: joint features in the member parts: %d hole features (before patterns)" % sum(
        c.features.holeFeatures.count for c, _bb in members.values()))


def rect_on_y(design, comp, y_expr, xr, zr, label):
    """Fully constrained rectangle on a plane normal to Y at y_expr, spanning model X xr and Z zr."""
    xr, zr = span(design, *xr), span(design, *zr)
    pl = plane_at(design, comp, "y", y_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    y = ev(design, y_expr)
    x0, x1, z0, z1 = (ev(design, e) for e in (xr[0], xr[1], zr[0], zr[1]))

    def sp(x, z):
        return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, z * MM))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(sp(x0, z0), sp(x1, z1))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            p0, p1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(p0.y - p1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for q in (ln.startSketchPoint, ln.endSketchPoint):
            if all(q != o for o in pts):
                pts.append(q)

    def near(x, z):
        tg = sp(x, z)
        return min(pts, key=lambda q: (q.geometry.x - tg.x) ** 2 + (q.geometry.y - tg.y) ** 2)
    c00, c10, c01 = near(x0, z0), near(x1, z0), near(x0, z1)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    ax, az = sketch_axis_of(sk, "x"), sketch_axis_of(sk, "z")
    o = {"x": H, "y": V}
    mid = sp((x0 + x1) / 2, (z0 + z1) / 2)
    tp = adsk.core.Point3D.create(mid.x, mid.y, 0)
    sk.sketchDimensions.addDistanceDimension(c00, c10, o[ax], tp).parameter.expression = "(%s) - (%s)" % (xr[1], xr[0])
    sk.sketchDimensions.addDistanceDimension(c00, c01, o[az], tp).parameter.expression = "(%s) - (%s)" % (zr[1], zr[0])
    for axis, val, e in ((ax, x0, xr[0]), (az, z0, zr[0])):
        if abs(val) < 1e-6:
            (gc.addVerticalPoints if axis == "x" else gc.addHorizontalPoints)(c00, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c00, o[axis], tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk


def round_cut(design, comp, body, axis, plane_expr, into, pos, dia, depth, label):
    """A round cut of diameter `dia` (an extrude cut, not a hole feature, so it sits in sheet metal too): a circle
    on the plane normal to `axis` at `plane_expr`, its centre dimensioned from the sketch origin by the `pos`
    expressions and its diameter by `dia` (fully constrained), cut `depth` along `into` (+1 or -1 along the
    axis), cutting `body` only."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM))
    circ = sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, ev(design, dia) / 2.0 * MM)
    pt = circ.centerSketchPoint
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(pt, sk.originPoint)
        else:
            g = pt.geometry
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, H if sa == "x" else V,
                                                     adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
                                                     ).parameter.expression = "abs(%s)" % e
    g = pt.geometry
    sk.sketchDimensions.addDiameterDimension(circ, adsk.core.Point3D.create(g.x + 1.0, g.y + 1.0, 0)
                                             ).parameter.expression = dia
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    n = pl.geometry.normal
    dist = depth if into * {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else "-(%s)" % depth
    ext_in = comp.features.extrudeFeatures.createInput(sk.profiles.item(0),
                                                       adsk.fusion.FeatureOperations.CutFeatureOperation)
    ext_in.setDistanceExtent(False, vi(dist))
    ext_in.participantBodies = [body]
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "CUT - %s" % label
    return ext


def el_tray_features(design, tray):
    """ELECTRICAL's features in the back trays (EL_PARAMS). B2-CASS: the power unit cut-out, plain (folded
    returns round a rectangular hole can't come from a flat blank: their tabs overlap at the corners; PROPOSED by
    WALL 2026-10-31 21:08 UTC), so the unit's leads go straight into the cable gap; the light feed's bushing hole
    in the tray's top return (the B2/B4 joint); the corner slot in the end return. B4-CASS: the light feed's
    bushing hole in its bottom return (the same joint). No cable hole goes through a lip (PM rule 2026-10-31
    21:01 UTC: felt only, or a full steel face with its bushing, never a notch): the ceiling route crosses the
    felt only (el_felt_cuts_back)."""
    if POSITION not in ("B2", "B4"):
        return
    body = tray.bRepBodies.item(0)
    outline = (span(design, XC_LOW, XC_HIGH), span(design, Z0, Z_CASS1))
    grm = ("el_lt_x", "el_y_bg")
    if POSITION == "B2":
        el_inside(design, "the power unit cut-out", [("el_cut_x0", "el_cut_x1") + outline[0],
                                                     ("el_cut_z0", "el_cut_z1") + outline[1]], 30.0)
        box(design, tray, "POWER UNIT CUT-OUT", ("el_cut_x0", "el_cut_x1"),
            ("(%s) - tray_t - 1 mm" % Y_TRAY_BACK, "(%s) + 1 mm" % Y_TRAY_BACK), ("el_cut_z0", "el_cut_z1"), "cut", body)
        body = tray.bRepBodies.item(0)
        round_cut(design, tray, body, "z", "(%s) - tray_t - 1 mm" % Z_CASS1, +1, {"x": grm[0], "y": grm[1]},
                  "el_grm_d", "tray_t + 2 mm", "HOLE G-B2-B4 IN THE TOP RETURN")
        body = tray.bRepBodies.item(0)
        el_inside(design, "S-CNR", [("el_trunk_z - el_cs_dz", "el_trunk_z + el_cs_dz") + outline[1]], 30.0)
        box(design, tray, "SLOT S-CNR IN THE END RETURN", ("(%s) - tray_t - 1 mm" % XC_HIGH, "(%s) + 1 mm" % XC_HIGH),
            ("el_y_xc - el_cs_h", "el_y_xc + el_cs_h"), ("el_trunk_z - el_cs_dz", "el_trunk_z + el_cs_dz"), "cut", body)
        names = "plain cut-out, G-B2-B4, S-CNR"
    else:
        round_cut(design, tray, body, "z", "(%s) - 1 mm" % Z0, +1, {"x": grm[0], "y": grm[1]}, "el_grm_d",
                  "tray_t + 2 mm", "HOLE G-B2-B4 IN THE BOTTOM RETURN")
        names = "G-B2-B4"
    if tray.bRepBodies.count != 1:
        raise RuntimeError("the tray split into %d bodies at ELECTRICAL's features" % tray.bRepBodies.count)
    print("step 2b: ELECTRICAL features in %s's tray: %s" % (POSITION, names))


def el_felt_cuts_back(design, felt, fb, xr, zr):
    """ELECTRICAL's openings in the back felts. B2: the power unit cut-out, flush with the tray's, 4 clear of the
    unit (the felt edge there has no lip: the unit's face plate covers it, ELECTRICAL). B4: the light shelf's feed
    hole (FX-SHELF) and the ceiling route's crossing (FX-CEIL, 2 under the top lip), felt only."""
    if POSITION not in ("B2", "B4"):
        return fb
    fx = ("(%s) + tray_t + felt_c" % xr[0], "(%s) - tray_t - felt_c" % xr[1])
    fz = ("(%s) + tray_t + felt_c" % zr[0], "(%s) - tray_t - felt_c" % zr[1])
    if POSITION == "B2":
        cx, cz = ("el_cut_x0", "el_cut_x1"), ("el_cut_z0", "el_cut_z1")
        el_inside(design, "the felt's cut-out", [cx + fx, cz + fz], 1.0)
        box(design, felt, "FELT CUT-OUT POWER UNIT", cx, ("(%s) - 1 mm" % Y_IN,
                                                                           "(%s) + 1 mm" % Y_FELT_BACK), cz, "cut", fb)
        names = "cut-out"
    else:
        for label, x, z, d in (("FX-SHELF LIGHT SHELF FEED", "el_lt_x", "el_shelf_z", "el_shelf_d"),
                               ("FX-CEIL CEILING ROUTE", "el_ceil_x", "el_ceil_z", "el_grm_s")):
            el_inside(design, label.split()[0], [("(%s) - (%s) / 2" % (x, d), "(%s) + (%s) / 2" % (x, d)) + fx,
                                                 ("(%s) - (%s) / 2" % (z, d), "(%s) + (%s) / 2" % (z, d)) + fz], 1.0)
            hole(design, felt, felt.bRepBodies.item(0), "y", Y_FELT_FACE, +1, {"x": x, "z": z}, d, "felt_t + 1 mm",
                 "FELT " + label)
        names = "FX-SHELF, FX-CEIL"
    if felt.bRepBodies.count != 1:
        raise RuntimeError("the felt split into %d bodies at ELECTRICAL's openings" % felt.bRepBodies.count)
    print("step 3b: ELECTRICAL openings in %s's felt: %s" % (POSITION, names))
    return felt.bRepBodies.item(0)


def el_skin_holes(design, skin, plate):
    """Panel B2: the mains inlet's and the LAN feed-through's Ø24 holes in the ACP (ELECTRICAL, v1's back-wall
    positions moved clear of the closing seam)."""
    if POSITION != "B2":
        return plate
    sx_, sz_ = span(design, XS_LOW, XS_HIGH), ("(%s) + skin_setback" % Z0, "(%s) - skin_setback" % Z1)
    for label, z in (("MAINS INLET", "el_inlet_z"), ("LAN FEED-THROUGH", "el_lan_z")):
        el_inside(design, label, [("el_inlet_x - el_inlet_d / 2", "el_inlet_x + el_inlet_d / 2") + sx_,
                                  ("(%s) - el_inlet_d / 2" % z, "(%s) + el_inlet_d / 2" % z) + sz_], 20.0)
        hole(design, skin, skin.bRepBodies.item(0), "y", Y_OUT, -1, {"x": "el_inlet_x", "z": z}, "el_inlet_d",
             "skin_t + 1 mm", "SKIN %s" % label)
    print("step 4b: B2 skin: the inlet and LAN holes")
    return skin.bRepBodies.item(0)


def el_fill_cutouts(design, piece, yf):
    """Panel B2: bay 1's fill piece cut away where ELECTRICAL's parts sit: the power unit (its cut-out size, run on
    to the first stud so no sliver of fill is left beside it), the mains and LAN sleeve, and the inlet and LAN
    connectors behind the skin (one cut-out to the sleeve, so no thin strip stays between them). Right through
    the piece: a knife cut (D-128)."""
    if POSITION != "B2":
        return
    ys = ("(%s) - 1 mm" % yf[1], "(%s) + 1 mm" % yf[0])
    cuts = [("FILL CUT-OUT POWER UNIT", ("el_cut_x0", "(%s) + stile_pitch + tube_w / 2" % X_LOW), ("el_cut_z0", "el_cut_z1")),
            ("FILL CUT-OUT SLEEVE", ("el_sl_x - el_sl_w / 2", "el_sl_x + el_sl_w / 2"),
             ("el_inlet_z - el_inlet_d / 2", "el_cut_z0")),
            ("FILL CUT-OUT INLET AND LAN", ("el_inlet_x - el_inlet_d / 2", "el_sl_x + el_sl_w / 2"),
             ("el_inlet_z - el_inlet_d / 2", "el_lan_z + el_inlet_d / 2"))]
    pb = bbox(piece.bRepBodies.item(0))
    for label, xr, zr in cuts:
        want = [ev(design, e) for e in xr + zr]
        if not (pb[0] < max(want[:2]) and pb[3] > min(want[:2]) and pb[2] < max(want[2:]) and pb[5] > min(want[2:])):
            raise RuntimeError("%s misses bay 1's fill piece" % label)
        box(design, piece, label, xr, ys, zr, "cut", piece.bRepBodies.item(0))
        if piece.bRepBodies.count != 1:
            raise RuntimeError("%s split bay 1's fill piece" % label)
    print("step 5b: B2 fill: bay 1's piece cut for the power unit, the sleeve, the inlet and LAN")


def build_tray_y(design, root, tray, xr, zr):
    """The side tray's recipe with the base on a plane normal to Y (Y_TRAY_BACK) and the returns toward -Y."""
    rule = design.designSheetMetalRules.itemByName("GALV STEEL 0.5 - LINING TRAY")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(tray.activeSheetMetalRule, "GALV STEEL 0.5 - LINING TRAY")
    rule.thickness.expression = "%.4f mm" % ev(design, "tray_t")
    rule.bendRadius.expression = "Thickness"
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    tray.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == tray][0]
    occ.activate()
    want_xz = [ev(design, e) for e in (span(design, *xr) + span(design, *zr))]
    yb, tt = ev(design, Y_TRAY_BACK), ev(design, "tray_t")
    try:
        sk = rect_on_y(design, tray, Y_TRAY_BACK, xr, zr, "TRAY BASE OUTLINE")
        ff = tray.features.flangeFeatures
        base = None
        for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                       adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
            bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
            bfi.orientation = orient
            f = ff.add(bfi)
            b = bbox(f.bodies.item(0))
            if abs(b[4] - yb) < 0.01 and abs(b[1] - (yb - tt)) < 0.01:      # the room is toward -Y
                base = f
                break
            f.deleteMe()
        if base is None:
            raise RuntimeError("tray: no base flange side lies on the room side of the tray back")
        base.name = "BASE - TRAY"
        body = tray.bRepBodies.item(0)
        body.name = "TRAY - STEEL 0.5 WITH RETURNS AND LIPS"

        def y_edges(y, keep):
            return [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
                    and abs(e.startVertex.geometry.y * 10 - y) < 0.01 and abs(e.endVertex.geometry.y * 10 - y) < 0.01
                    and keep(e)]
        eds = y_edges(yb - tt, lambda e: True)
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
            if all(abs(g - w) < 0.05 for g, w in zip([b[0], b[3], b[2], b[5]], want_xz)):
                ret = f
                break
            f.deleteMe()
        if ret is None:
            raise RuntimeError("tray: no bend position keeps the returns' outer faces on the outline")
        ret.name = "FLANGE - TRAY RETURNS"
        body = tray.bRepBodies.item(0)
        b = bbox(body)
        yt = b[1]                              # the returns' tips, at the room side (-Y)

        def off_outline(e):
            q = e.startVertex.geometry
            return min(abs(q.x * 10 - b[0]), abs(q.x * 10 - b[3]), abs(q.z * 10 - b[2]), abs(q.z * 10 - b[5])) > 0.05 \
                and e.length * 10 > 100
        inner = y_edges(yt, off_outline)
        if len(inner) != 4:
            raise RuntimeError("tray: expected 4 inner tip edges, got %d" % len(inner))
        lip = None
        y_room = ev(design, Y_IN)
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput([], vi("lip_w"))
            for e in inner:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = bbox(tray.bRepBodies.item(0))
            inside = all(abs(g - w) < 0.05 for g, w in zip([b2[0], b2[3], b2[2], b2[5]], want_xz)) and \
                abs(b2[1] - y_room) < 0.05
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("tray: no lip direction keeps the lips inside the outline at the room face")
        lip.name = "FLANGE - TRAY LIPS HOLDING THE FELT"
        el_tray_features(design, tray)
        body = tray.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(adsk.core.Plane.cast(fc.geometry).normal.y) > 0.99), key=lambda fc: fc.area)
        fp = tray.flatPattern or tray.createFlatPattern(big)
        print("FLAT|%s|%s" % (tray.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    return tray.bRepBodies.item(0)


def build_cassette(design, root):
    if POSITION == "B2":
        raise RuntimeError(B2_PENDING)     # its clip zones sit on the studs
    out = {}
    want = WANT[PART]
    tray = new_comp(root, "tray", sheet_metal=True) if "tray" in want else None
    felt = new_comp(root, "felt") if "felt" in want else None
    clip = new_comp(root, "clip") if "clip" in want else None
    print("step 1: components %s" % ", ".join(c.name for c in (root, tray, felt, clip) if c))
    if STOP_AFTER <= 1:
        return out
    xr, zr = (XC_LOW, XC_HIGH), (Z0, Z_CASS1)
    if tray:
        pan = build_tray_y(design, root, tray, xr, zr)
        out[pan.name] = pan
        print("step 2: tray", size(bbox(pan)))
        set_material(design, [pan], "tray", "GALVANISED STEEL 0.5")
    if felt:
        fb = box(design, felt, "FELT", ("(%s) + tray_t + felt_c" % xr[0] if COL == "R" else "(%s) + tray_t + felt_c" % xr[0],
                                        "(%s) - tray_t - felt_c" % xr[1]),
                 (Y_FELT_BACK, Y_FELT_FACE), ("(%s) + tray_t + felt_c" % zr[0], "(%s) - tray_t - felt_c" % zr[1])
                 ).bodies.item(0)
        fb.name = "FELT - PET 9 HELD BY THE TRAY LIPS"
        out[fb.name] = fb
        print("step 3: felt", size(bbox(fb)))
        set_material(design, [fb], "felt", "PET FELT 9 MM DARK GRAY")
        out[fb.name] = el_felt_cuts_back(design, felt, fb, xr, zr)
    if not clip:
        return out
    # clip zones (H03): in the 4 mm gap between the frame's room face and the tray back, on the panel frame's
    # first and last intermediate stiles, 100 from the cassette's top and bottom
    n_mid = int(round(design.userParameters.itemByName("stile_n_mid").value))
    xs = [("(%s) + stile_pitch" % X_LOW, "(%s) + stile_pitch + tube_w" % X_LOW),
          ("(%s) + %d * stile_pitch" % (X_LOW, n_mid), "(%s) + %d * stile_pitch + tube_w" % (X_LOW, n_mid))]
    zs = [("(%s) + clip_zone_dz - clip_zone_h / 2" % Z0, "(%s) + clip_zone_dz + clip_zone_h / 2" % Z0),
          ("(%s) - clip_zone_dz - clip_zone_h / 2" % Z_CASS1, "(%s) - clip_zone_dz + clip_zone_h / 2" % Z_CASS1)]
    n = 0
    for zi, zz in enumerate(zs):
        for xi, xx in enumerate(xs):
            n += 1
            bd = box(design, clip, "CLIP ZONE %d" % n, xx, (Y_TRAY_BACK, Y_FRAME_IN), zz).bodies.item(0)
            bd.name = "HOLD - CLIP ZONE %d (%s %s)" % (n, "BOTTOM" if zi == 0 else "TOP", "LOW X" if xi == 0 else "HIGH X")
            out[bd.name] = bd
    print("step 4: %d clip zones (HOLD H03)" % n)
    set_material(design, [b for k, b in out.items() if k.startswith("HOLD")], "zone", "RESERVED ZONE")
    return out
