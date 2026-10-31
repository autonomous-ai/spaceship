"""Spaceship (FocusPod v2) WALL: one back wall panel (B1 to B4) and its lining cassette.

Native, parameter-driven Fusion design, built by script into the ACTIVE document, the same way as
wall_side_panel.py, whose helpers it uses (it runs that file first as a library, then replaces its
tables and builders with the back wall's). One run builds one document:

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_back_panel.py \
        --doc 210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD --doc-new --arg pos=B1 --arg part=panel \
        --arg post=1 --close --discard

Options (--arg KEY=VALUE): pos=B1|B2|B3|B4 (B1 lower left, B2 lower right, B3 upper left, B4 upper right,
seen from outside facing the door, conventions.md section 4); part=panel|cassette|frame|skin|fill|tray|felt;
rebuild=1; post=1; skeleton=NAME; stop_after=N (as wall_side_panel.py).

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

import adsk.core      # noqa: E402  (already imported by the library; named here for readers)
import adsk.fusion    # noqa: E402

COL = "L" if POSITION in ("B1", "B3") else "R"
ROW = _ROW
BPOS = int(POSITION[1])
CODE = POSITION
LEVEL = "LOWER" if ROW == 1 else "UPPER"
VN = "%s %s" % ("dưới" if ROW == 1 else "trên", "trái" if COL == "L" else "phải")
PARTS = {
    "assy": ("2102%02d" % BPOS, "WALL - PANEL ASSY - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - cụm tấm %s" % VN),
    "frame": ("2112%02d" % BPOS, "WALL - PANEL FRAME - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - khung %s" % VN),
    "skin": ("2114%02d" % BPOS, "WALL - SKIN - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - tấm ốp alu %s" % VN),
    "fill": ("2116%02d" % BPOS, "WALL - CAVITY FILL - BACK %s - %s" % (LEVEL, POSITION), "Vách hậu - bông PET %s" % VN),
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

_KEEP = {"skin_t", "tube_w", "bond_t", "tube_d", "tube_t", "stud_t", "stile_pitch_max", "skin_setback", "fill_t",
         "bolt_d", "access_d", "rivnut_d", "spigot_d", "spigot_slot", "spigot_edge", "bolt_edge", "pocket_w", "felt_t",
         "tray_t", "tray_h", "lip_w", "bend_r", "felt_c", "gap_h", "clip_zone_h", "clip_zone_dz", "bolt_line_y",
         "stopw_od", "stopw_id", "stopw_t", "rivnut_head_d", "rivnut_head_t", "rivnut_body_d", "rivnut_len", "m6_d",
         "spigot_pin_d", "spigot_proud", "spigot_thread_l"}
WALL_PARAMS = [p for p in WALL_PARAMS if p[0] in _KEEP] + [
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
    ("stile_n_mid", "ceil((frm_len - tube_w) / stile_pitch_max) - 1", "", "calculation",
     "intermediate stiles so that no stile pitch exceeds stile_pitch_max"),
    ("stile_pitch", "(frm_len - tube_w) / (stile_n_mid + 1)", "mm", "calculation", "equal stile pitch, centre to centre"),
    ("stile_len", "frm_h - 2 * tube_w", "mm", "calculation", "stiles between the full-width rails (butt joints)"),
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


def pattern_x(comp, bodies, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for bd in bodies:
        coll.add(bd)
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, comp.xConstructionAxis, vi(count_expr), vi(pitch_expr),
        adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    pin.setDirectionTwo(comp.zConstructionAxis, vi("1"), vi("1 mm"))     # see wall_side_panel.pattern_y
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


def name_by_x(comp, known, first, prefix):
    group = [first] + [bd for bd in comp.bRepBodies if not any(bd == k for k in known) and not bd == first]
    group.sort(key=lambda bd: bd.boundingBox.minPoint.x)
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along X: %s" % prefix)
    out = {}
    for i, bd in enumerate(group):
        bd.name = "%s %d" % (prefix, i + 1)
        out[bd.name] = bd
    return out


def build_panel(design, root):
    out = {}
    want = WANT[PART]
    frame, skin, fill = (new_comp(root, k) if k in want else None for k in ("frame", "skin", "fill"))
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin, fill) if c))
    if STOP_AFTER <= 1:
        return out
    yf = (Y_FRAME_OUT, Y_FRAME_IN)
    zs = ("(%s) + tube_w" % Z0, "(%s) - top_h" % Z1)
    if frame:
        out["RAIL - BOTTOM"] = tube_x(design, frame, "RAIL - BOTTOM", (X_LOW, X_HIGH), yf, (Z0, "(%s) + tube_w" % Z0))
        out["RAIL - TOP"] = tube_x(design, frame, "RAIL - TOP", (X_LOW, X_HIGH), yf, ("(%s) - top_h" % Z1, Z1))
        lo_name, hi_name = ("STILE - OUTER", "STILE - CENTRE") if COL == "L" else ("STILE - CENTRE", "STILE - OUTER")
        out[lo_name] = tube_z(design, frame, lo_name, (X_LOW, "(%s) + tube_w" % X_LOW), yf, zs)
        out[hi_name] = tube_z(design, frame, hi_name, ("(%s) - tube_w" % X_HIGH, X_HIGH), yf, zs)
        mid = tube_z(design, frame, "STILE - MID 1", ("(%s) + stile_pitch" % X_LOW, "(%s) + stile_pitch + tube_w" % X_LOW),
                     yf, zs, "stud_t")
        out["STILE - MID 1"] = mid
        pattern_x(frame, [mid], "stile_n_mid", "stile_pitch", "STILES - MID")
        out.update(name_by_x(frame, list(out.values()), mid, "STILE - MID"))
        print("step 2-3: frame %s, %d mid stiles at %.2f" % (size(bbox(out["RAIL - BOTTOM"])),
                                                           round(design.userParameters.itemByName("stile_n_mid").value),
                                                           design.userParameters.itemByName("stile_pitch").value * 10.0))
    if skin:
        plate = box(design, skin, "SKIN PLATE", (XS_LOW, XS_HIGH), (Y_SKIN_IN, Y_OUT),
                    ("(%s) + skin_setback" % Z0, "(%s) - skin_setback" % Z1)).bodies.item(0)
        plate.name = "SKIN - ACP 3, OVERHANGS THE FRAME 1.62 AT THE CLOSING SEAM"
        out[plate.name] = plate
        print("step 4: skin", size(bbox(plate)))
    if fill:
        bay = box(design, fill, "FILL BAY 1", ("(%s) + tube_w" % X_LOW, "(%s) + stile_pitch" % X_LOW), yf,
                  zs).bodies.item(0)
        bay.name = "FILL - BAY 1"
        out[bay.name] = bay
        pattern_x(fill, [bay], "stile_n_mid + 1", "stile_pitch", "FILL BAYS")
        out.update(name_by_x(fill, list(out.values()), bay, "FILL - BAY"))
        back_pockets(design, fill, yf, zs)
        print("step 5: fill, %d bays" % sum(1 for k in out if k.startswith("FILL")))
    if frame:
        back_joint_features(design, frame, out)
    if PART == "panel":
        build_hardware(design, root, out)
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "ALUMINIUM TUBE 6063-T6 MILL")
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


def back_pockets(design, fill, yf, zs):
    """Fill pockets (FR-10) beside every bolt this panel drives: the bottom rail's bolts (J-BASE-01 or
    J-WALL-01), the top rail's ceiling bolts (upper panels, J-CEIL-01), the corner bolts in the outer stile
    (J-WALL-02) and, on B2/B4, the closing seam's pin bolts in the centre stile."""
    n = int(round(design.userParameters.itemByName("n_len_bolt").value))
    z_bot = "(%s) + tube_w" % Z0
    for i, xc in enumerate(bolt_xs(n)):
        box(design, fill, "FILL POCKET BOTTOM BOLT %d" % (i + 1), ("(%s) - pocket_w / 2" % xc, "(%s) + pocket_w / 2" % xc),
            yf, (z_bot, "(%s) + pocket_w" % z_bot), "cut")
        if ROW == 2:
            z_top = "(%s) - top_h" % Z1
            box(design, fill, "FILL POCKET CEILING BOLT %d" % (i + 1),
                ("(%s) - pocket_w / 2" % xc, "(%s) + pocket_w / 2" % xc), yf, ("(%s) - pocket_w" % z_top, z_top), "cut")
    ends = [("CORNER", _outer_x(), 1 if COL == "L" else -1)]
    if COL == "R":
        ends.append(("CLOSING SEAM", _centre_x(), 1))
    for label, xe, sgn in ends:
        x_in = "(%s) + %s * tube_w" % (xe, "1" if sgn > 0 else "-1")
        xr = (x_in, "(%s) %s pocket_w" % (x_in, "+" if sgn > 0 else "-"))
        for j in range(3):
            zc = "(%s) + bolt_edge + %d * side_jnt_pitch" % (Z0, j)
            box(design, fill, "FILL POCKET %s BOLT %d" % (label, j + 1), xr, yf,
                ("(%s) - pocket_w / 2" % zc, "(%s) + pocket_w / 2" % zc), "cut")


def lead_in(design, frame, top, xc):
    """1 x 45 degree lead-in on the top edge of the closing-seam face (register 2.10, R-J9): the top rail's outer
    top edge at its seam end, along Y."""
    xv, zv = ev(design, xc), ev(design, Z1)
    eds = [e for e in top.edges if e.geometry.objectType == adsk.core.Line3D.classType()
           and all(abs(v.geometry.x * 10 - xv) < 0.01 and abs(v.geometry.z * 10 - zv) < 0.01
                   for v in (e.startVertex, e.endVertex))]
    if len(eds) != 1:
        raise RuntimeError("lead-in: expected 1 top edge at the closing-seam face, got %d" % len(eds))
    coll = adsk.core.ObjectCollection.create()
    coll.add(eds[0])
    cin = frame.features.chamferFeatures.createInput2()
    cin.chamferEdgeSets.addEqualDistanceChamferEdgeSet(coll, vi("lead_in"), False)
    f = frame.features.chamferFeatures.add(cin)
    f.name = "CHAMFER - CLOSING SEAM LEAD-IN (R-J9)"
    return f


def back_joint_features(design, frame, out):
    t = "tube_t"
    bot, top = out["RAIL - BOTTOM"], out["RAIL - TOP"]
    outer, centre = out["STILE - OUTER"], out["STILE - CENTRE"]
    x_b1, n_b, p_b = "(%s) + bolt_edge" % X_LOW, "n_len_bolt", "len_bolt_pitch"
    zb0, zb1, zt0, zt1 = Z0, "(%s) + tube_w" % Z0, "(%s) - top_h" % Z1, Z1
    # bottom rail, bolt side: J-BASE-01 (B1, B2) or J-WALL-01 (B3, B4). Spigots: the round hole 100 from the
    # closing-seam end, so the closing gap is set by the round spigots and their distance to the seam face
    # (register 2.11, ST-02: 5.2 to 5.8), and the slot along the edge 100 from the corner end
    a = hole(design, frame, bot, "z", zb0, +1, {"x": x_b1, "y": YC}, "bolt_d", t, "BOTTOM RAIL BOLT CLEARANCE 1")
    b = hole(design, frame, bot, "z", zb1, -1, {"x": x_b1, "y": YC}, "access_d", t, "BOTTOM RAIL KEY ACCESS 1")
    pattern_feat(frame, [a, b], "x", n_b, p_b, "BOTTOM RAIL BOLT HOLES")
    sgn_out = 1 if COL == "L" else -1
    x_round = "(%s) - %d * spigot_edge" % (_centre_x(), sgn_out)
    x_slot = "(%s) + %d * spigot_edge" % (_outer_x(), sgn_out)
    hole(design, frame, bot, "z", zb0, +1, {"x": x_round, "y": YC}, "spigot_d", t, "BOTTOM RAIL SPIGOT ROUND")
    half = "(spigot_slot - spigot_d) / 2"
    box(design, frame, "BOTTOM RAIL SPIGOT SLOT", ("(%s) - %s" % (x_slot, half), "(%s) + %s" % (x_slot, half)),
        ("(%s) - spigot_d / 2" % YC, "(%s) + spigot_d / 2" % YC), (zb0, "(%s) + %s" % (zb0, t)), "cut", bot)
    for i, sg in enumerate(("-", "+")):
        hole(design, frame, bot, "z", zb0, +1, {"x": "(%s) %s %s" % (x_slot, sg, half), "y": YC}, "spigot_d", t,
             "BOTTOM RAIL SPIGOT SLOT END %d" % (i + 1))
    if ROW == 1:
        # top rail, nut side of J-WALL-01 to B3/B4: rivnuts at the 220 rule, 2 spigot rivnuts 100 from the ends
        r = hole(design, frame, top, "z", zt1, -1, {"x": x_b1, "y": YC}, "rivnut_d", t, "TOP RAIL RIVNUT 1")
        pattern_feat(frame, [r], "x", n_b, p_b, "TOP RAIL RIVNUTS")
        hw_site("TOP RAIL", "z", zt1, -1, {"x": x_b1, "y": YC}, ("x", n_b, p_b))
    else:
        # top rail, bolt side of J-CEIL-01's back edge (the ceiling's 40 x 40 back member holds the rivnuts):
        # Ø7.0 up through the top wall, Ø19 in the bottom wall; spigot rivnuts for the ceiling (FR-04)
        a = hole(design, frame, top, "z", zt1, -1, {"x": x_b1, "y": YC}, "bolt_d", t, "TOP RAIL CEILING BOLT CLEARANCE 1")
        b = hole(design, frame, top, "z", zt0, +1, {"x": x_b1, "y": YC}, "access_d", t, "TOP RAIL CEILING KEY ACCESS 1")
        pattern_feat(frame, [a, b], "x", n_b, p_b, "TOP RAIL CEILING BOLT HOLES")
    # spigot rivnuts 100 from each end, holding the spigots for the panel above (B3, B4) or the ceiling (C1, C2)
    for k, xs in (("LOW X", "(%s) + spigot_edge" % X_LOW), ("HIGH X", "(%s) - spigot_edge" % X_HIGH)):
        hole(design, frame, top, "z", zt1, -1, {"x": xs, "y": YC}, "rivnut_d", t, "TOP RAIL SPIGOT RIVNUT %s" % k)
        hw_site("TOP RAIL SPIGOT %s" % k, "z", zt1, -1, {"x": xs, "y": YC}, washer=False, spigot=True)
    # outer stile, bolt side of J-WALL-02 (corner): Ø7.0 in its outer wall, Ø19 in its bay-side wall, on the
    # bolt line Y 824, at the 220 rule up the back panel's edge
    xo, xo_in = _outer_x(), "(%s) + %d * tube_w" % (_outer_x(), sgn_out)
    z_j1 = "(%s) + bolt_edge" % Z0
    a = hole(design, frame, outer, "x", xo, sgn_out, {"y": "bolt_line_y", "z": z_j1}, "bolt_d", t,
             "OUTER STILE CORNER BOLT CLEARANCE 1")
    b = hole(design, frame, outer, "x", xo_in, -sgn_out, {"y": "bolt_line_y", "z": z_j1}, "access_d", t,
             "OUTER STILE CORNER KEY ACCESS 1")
    pattern_feat(frame, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "OUTER STILE CORNER BOLT HOLES")
    # centre stile, the closing seam (R-J11): B1/B3 a plain Ø7.0 in the seam wall; B2/B4 the rivnut (no stop
    # washer) in the seam wall and the Ø19 access in the bay-side wall for driving the pin bolt
    xc, sgn_c = _centre_x(), (1 if COL == "L" else -1)            # toward the seam
    xc_in = "(%s) - %d * tube_w" % (xc, sgn_c)
    if COL == "L":
        a = hole(design, frame, centre, "x", xc, -sgn_c, {"y": YC, "z": z_j1}, "bolt_d", t, "CENTRE STILE PIN HOLE 1")
        pattern_feat(frame, [a], "z", "n_side_jnt", "side_jnt_pitch", "CENTRE STILE PIN HOLES")
    else:
        a = hole(design, frame, centre, "x", xc, -sgn_c, {"y": YC, "z": z_j1}, "rivnut_d", t,
                 "CENTRE STILE PIN RIVNUT 1")
        b = hole(design, frame, centre, "x", xc_in, sgn_c, {"y": YC, "z": z_j1}, "access_d", t,
                 "CENTRE STILE PIN KEY ACCESS 1")
        pattern_feat(frame, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "CENTRE STILE PIN HOLES")
        # the pin's rivnut has no stop washer: the closing gap is set by the spigots (register 2.10)
        hw_site("CENTRE STILE PIN", "x", xc, -sgn_c, {"y": YC, "z": z_j1}, ("z", "n_side_jnt", "side_jnt_pitch"),
                washer=False)
    lead_in(design, frame, top, xc)
    print("step 6: joint features: %d hole features (before patterns)" % frame.features.holeFeatures.count)


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
        body = tray.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(fc.geometry.normal.y) > 0.99), key=lambda fc: fc.area)
        fp = tray.flatPattern or tray.createFlatPattern(big)
        print("FLAT|%s|%s" % (tray.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    return tray.bRepBodies.item(0)


def build_cassette(design, root):
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
