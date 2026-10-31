"""350003 FRONT - DECOR BLOCK ASSY - DR (Khối trang trí phải): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dr_block.py \
        --doc 350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dr_block.py \
        --doc 350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD --arg step=export --close

Stage 1 of the right decor block (the decor detail sample):
- the outer shape: the skeleton's DR (its front outline, corner facet, the DT
  joint along v1's line and the top chamfer), with its bottom on the base band
  top (PM ruling 2026-10-31) and its inner edge on the fixed pane's lines
  (front_lib.GLASS_PARAMS), so DR and the pane share one definition;
- 351301 the 3 mm ACP skin, made by shelling that shape (open at the back and
  at the faces DT sits on), with the 15 mm slot the pane's hidden channel
  enters through and the opening in its underside onto the base band;
- 351302 the fixed back plate, with the opening into the air column's top;
- 351303 the removable inner panel and 351304 its 9 mm felt: the part of DR's
  back face that shows inside the pod, between the glass edge, the air column
  and the soffit (D-59, D-60);
- the air parts the D-60 table puts in DR (the Air Engineer's sizes, status
  source): the 1 mm steel intake riser, the supply fan box with its two 12 V
  fans, and the two transitions as reserved duct spaces. The room-side intake
  is a slotted section of the base band under DR (PM ruling 2026-10-31): DR's
  underside opens onto the band top, sealed, and the block's bottom is the
  plenum the riser's raised foot draws from. The base is open over the whole
  band piece, back to the closing plate (PM ruling).
The aluminium frame inside the skin is stage 2.
"""

import importlib.util
import json
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(globals().get("__file__") or ARGS.get("script_path", "")))


def load_lib():
    spec = importlib.util.spec_from_file_location("front_lib_run", os.path.join(HERE, "front_lib.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


L = load_lib()


def load_frame_lib():
    spec = importlib.util.spec_from_file_location("frame_lib_run", os.path.join(HERE, "frame_lib.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


FL = load_frame_lib()

REV = "P01"
PN = "350003"
NAME = "FRONT - DECOR BLOCK ASSY - DR"
VN = "Khối trang trí phải (cụm)"
DOC_NAME = "%s_%s_FRONT-DECOR-BLOCK-ASSY-DR_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv" % (PN, REV)
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DR_ANCHORS.json" % (PN, REV)
DXF_SKIN_REL = "v2/03-Manufacturing/front/351301_%s_FRONT-DECOR-SKIN-DR_DXF.dxf" % REV
CUT_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-FRAME-DR-TUBE-CUT-LIST.csv" % ("351306", REV)
# flat parts cut from sheet: their DXF gives the outline and every hole, so they need no drawing (D-89 part 4)
DXF_FLAT = {"BACK": "351302_%s_FRONT-DECOR-BACK-PLATE-DR_DXF.dxf" % REV,
            "ACCESS": "351305_%s_FRONT-DECOR-ACCESS-PANEL-DR_DXF.dxf" % REV,
            "INNER": "351303_%s_FRONT-DECOR-INNER-PANEL-DR_DXF.dxf" % REV,
            "FELT": "351304_%s_FRONT-DECOR-INNER-PANEL-FELT-DR_DXF.dxf" % REV}

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"      # DR's front face and back face (Y -850, -645)
GY = "-glass_y"
ZB, ZT = "fg_vis_zb", "fg_vis_zt"                  # band top and DT's underside

OWN = [
    ("dr_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dr_back_t", "2 mm", "mm", "source",
     "joints register J-FRONT-01: the back plate is aluminium 1.0 to 2.7 thick at each bolt, for the rivnuts (HOLD-10)"),
    ("dr_strip_x0", "jf_x - 2 * jf_hole - 0.5 mm", "mm", "calculation",
     "the fixed back strip's inner edge, 2 hole diameters plus 0.5 from the J-FRONT-01 rivnut holes (mechanical "
     "check C09); the rest of the back comes off for the air unit (D-87)"),
    ("dr_acc_t", "3 mm", "mm", "calculation",
     "access panel 3 mm aluminium: it carries the air column's 10 kg on two hook studs 222 mm from its screwed edge "
     "(PM ruling 2026-11-01); 2 mm would see about 110 MPa if the column pulls 50 N, 3 mm about 50 MPa"),
    ("dr_band_dz", "35 mm", "mm", "calculation",
     "the back plate's top band starts this far above DT's underside: the removable panels' top edges land 35 on the "
     "frame's band tube, so the access panel's top bolts sit 2 hole diameters from its edge and the rivnuts 2 from "
     "the tube's edge (C09); the access panel keeps 45 over the opening into the column"),
    ("dr_stud_x", "971 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): the air column's two hook studs at X 971"),
    ("dr_stud_z1", "1700 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): lower hook stud Z 1700"),
    ("dr_stud_z2", "1850 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): upper hook stud Z 1850"),
    ("felt_t", "9 mm", "mm", "source", "the factory's 9 mm PET felt (D-31; hardware selection A3)"),
    ("dr_col_x0", "949 mm", "mm", "source", "D-60 air table: the air column's left face, X 949 (column X 949 to 1169)"),
    # intake (PM rulings 2026-10-31): room air enters through the mesh band piece under DR and goes up into the block
    # through its base, open over the whole band piece back to the closing plate, so the opening matches the mesh
    # (0.028 m2 free or more, the D-60 air table); BASE designs the block's support behind the mesh
    ("dr_f_len", "sqrt(dr_xc * dr_xc + (pod_d / 2 - dr_yc) * (pod_d / 2 - dr_yc))", "mm", "calculation",
     "length of DR's corner facet in plan"),
    ("dr_fnx", "(pod_d / 2 - dr_yc) / dr_f_len", "", "calculation", "corner facet outward normal, X"),
    ("dr_fny", "-dr_xc / dr_f_len", "", "calculation", "corner facet outward normal, Y"),
    ("dr_fc", "dr_fnx * (pod_w / 2 - dr_xc) + dr_fny * (-pod_d / 2)", "mm", "calculation", "corner facet line constant"),
    # intake riser, 1 mm galvanised steel (D-60 air table)
    ("ri_x0", "956 mm", "mm", "source", "D-60 air table: riser X 956 to 1095"),
    ("ri_w", "139 mm", "mm", "source", "D-60 air table: riser 139 wide"),
    ("ri_y0", "-803 mm", "mm", "source", "D-60 air table: riser Y -803 to -648"),
    ("ri_d", "155 mm", "mm", "source", "D-60 air table: riser 155 deep"),
    ("ri_zt", "1445 mm", "mm", "source", "D-60 air table: riser up to Z 1445"),
    ("ri_gap", "140 mm", "mm", "assumption",
     "the riser's open foot stands 140 mm over DR's open base, so the air rises straight into it and the riser clears "
     "the back frame's inner-edge member by 6 mm (the glass line runs to X 950 there); was 60 before the frame"),
    ("slot_clear", "1 mm", "mm", "assumption", "fitting clearance each side of the glass channel in DR's skin slot"),
    ("ri_t", "1 mm", "mm", "source", "D-60 air table: 1 mm galvanised steel"),
    # supply fan box (D-60 air table)
    ("fb_w", "300 mm", "mm", "source", "D-60 air table: fan box 300 x 155 x 300"),
    ("fb_y0", "-847 mm", "mm", "source", "D-60 air table: fan box Y -847 to -692"),
    ("fb_d", "155 mm", "mm", "source", "D-60 air table"),
    ("fb_z0", "1650 mm", "mm", "source", "D-60 air table: fan box Z 1650 to 1950"),
    ("fb_clear", "12 mm", "mm", "assumption",
     "fan box to the fixed glass's hidden channel: 12, so the front frame's 20 mm inner-edge member fits between them "
     "with 4 mm to spare (was 5 before the frame)"),
    ("fb_x0", "((fg_dc + gu_prof_d + fb_clear - fg_dnz * fb_z0) / fg_dnx)", "mm", "calculation",
     "fan box left side: the D-60 table's X 645 cut into the fixed glass channel (FRONT combined check, 2026-10-31), "
     "so the box sits fb_clear clear of the channel at its lower-left corner (about X 662) and follows the glass line"),
    ("fb_h", "300 mm", "mm", "source", "D-60 air table"),
    ("fb_t", "2 mm", "mm", "source", "D-60 air table: 2 mm aluminium"),
    ("fan_s", "140 mm", "mm", "source", "Noctua NF-A14 industrialPPC-3000 PWM, 140 x 140 x 25 (hardware selection F1)"),
    ("fan_t", "25 mm", "mm", "source", "as fan_s"),
    # opening from DR into the air column's top (D-60 air table)
    ("op_x0", "961 mm", "mm", "source", "D-60 air table: opening X 961 to 1164"),
    ("op_w", "203 mm", "mm", "source", "D-60 air table: 203 x 215"),
    ("op_z0", "1895 mm", "mm", "source", "D-60 air table: opening Z 1895 to 2110"),
    ("op_h", "215 mm", "mm", "source", "D-60 air table"),
    # ---- the tube frame (stage 2): v1's front and back frames of 16 mm steel box (sources/v1 decor frame drawing),
    # in 6063-T6 aluminium tube (D-79)
    ("fr_w", "20 mm", "mm", "calculation",
     "frame tube 20 x 20 x 1.5, 6063-T6 (D-79): bending stiffness E*I = 4.5e8 N.mm2, about v1's 16 x 16 x 1 steel box "
     "(4.7e8), at 0.30 kg/m against 0.47"),
    ("fr_t", "1.5 mm", "mm", "calculation", "frame tube wall, as fr_w"),
    ("fr_wb", "80 mm", "mm", "calculation",
     "bolt-line tube 80 x 20 x 1.5 behind the fixed strip: the J-FRONT-01 rivnut tails and bolt tips go into it "
     "through 14 mm holes (HOLD-10: the plate with the frame behind), and the access panel lands 37 on its other "
     "side, wide enough for its bolts and rivnuts at 2 diameters from every edge (C09); 3 clear of the duct spaces"),
    ("fr_wbot", "40 mm", "mm", "assumption", "back ring's bottom tube 40 x 20 x 1.5: the access panel's lower bolts"),
    ("fr_wband", "60 mm", "mm", "assumption",
     "band tube 60 x 20 x 1.5 at DT's underside: the access panel's top bolts and the top band's rivets land on it"),
    ("fr_h1", "724 mm", "mm", "source", "v1 decor frame drawing (front frame): first cross tube 724 above the bottom"),
    ("fr_hole_jf", "14 mm", "mm", "calculation",
     "hole in the bolt-line tube's back wall round each J-FRONT-01 rivnut: body 9.50 max and its bulge (SHX), and the "
     "bolt tip, go into the tube"),
    ("fr_hole_rn", "9.53 mm", "mm", "source", "joints register H-03: hole for the rivnut 838003 (Sherex CAH3-610-4.2)"),
    ("ab_hole", "7 mm", "mm", "source",
     "the pod's M6 clearance hole, 7.0 (D-64, D-75; the mechanical check's hole rule M6-CLEARANCE-7) for the bolts "
     "838001; the frame's rivnut heads (0.76 proud, SHX) sit in the access panel's 1 mm perimeter gasket (HOLD)"),
    ("ab_x", "pod_w / 2 - dr_skin_t - fr_wb + 2 * fr_hole_rn + 2 mm", "mm", "calculation",
     "access panel bolts on the bolt-line tube: the rivnut 2 diameters plus 2 from the tube's inner edge (C09)"),
    ("ab_z0", "300 mm", "mm", "assumption", "lowest access panel bolt on the bolt-line tube"),
    ("ab_p", "350 mm", "mm", "assumption", "pitch of the 6 access panel bolts on the bolt-line tube"),
    ("ab_x1", "dr_col_x0 + 45 mm", "mm", "assumption", "access panel's top and bottom bolts, left"),
    ("ab_x2", "pod_w / 2 - dr_skin_t - fr_wb - 2 * fr_hole_rn - 3 mm", "mm", "calculation",
     "access panel's top and bottom bolts, right: their rivnuts 2 diameters plus 3 from the end of the bottom and "
     "band tubes (C09)"),
    ("ab_zb", "fg_vis_zb + fr_wbot / 2", "mm", "calculation",
     "access panel's bottom bolts: the middle of the 40 bottom tube, so the rivnut is 2 diameters from both its edges"),
    ("ab_zt", "fg_vis_zt + 2 * fr_hole_rn + 1 mm", "mm", "calculation",
     "access panel's top bolts: their rivnuts 2 diameters plus 1 above the band tube's lower edge (C09)"),
    # the top chamfer and the DT joint as lines, for the frame
    ("dr_cl", "sqrt((pod_d / 2 - ch_yb) * (pod_d / 2 - ch_yb) + (pod_h - ch_zlo) * (pod_h - ch_zlo))", "mm",
     "calculation", "length of the top chamfer in the side view"),
    ("dr_cny", "-(pod_h - ch_zlo) / dr_cl", "", "calculation", "top chamfer outward normal, Y"),
    ("dr_cnz", "(pod_d / 2 - ch_yb) / dr_cl", "", "calculation", "top chamfer outward normal, Z"),
    ("dr_cc", "dr_cny * (-pod_d / 2) + dr_cnz * ch_zlo", "mm", "calculation", "top chamfer line constant"),
    ("dr_jl", "sqrt((dt_xr - fix_xtr) * (dt_xr - fix_xtr) + (pod_d / 2 - ch_yb) * (pod_d / 2 - ch_yb))", "mm",
     "calculation", "length of the DR-DT joint line in plan (v1's line to X 449)"),
    ("dr_jnx", "(pod_d / 2 - ch_yb) / dr_jl", "", "calculation", "DR-DT joint normal into DR, X"),
    ("dr_jny", "-(dt_xr - fix_xtr) / dr_jl", "", "calculation", "DR-DT joint normal into DR, Y"),
    ("dr_jc", "dr_jnx * (-pod_w / 2 + fix_xtr) + dr_jny * (-pod_d / 2)", "mm", "calculation", "DR-DT joint line constant"),
]

AIR_ASSY = ("350004", "FRONT - AIR SUPPLY ASSY - DR", "Cụm cấp gió khối phải")
PARTS = {
    "SKIN": ("351301", "FRONT - DECOR SKIN - DR", "Tấm ốp alu khối phải"),
    "BACK": ("351302", "FRONT - DECOR BACK PLATE - DR", "Tấm hậu khối phải"),
    "ACCESS": ("351305", "FRONT - DECOR ACCESS PANEL - DR", "Tấm thăm khối phải"),
    "INNER": ("351303", "FRONT - DECOR INNER PANEL - DR", "Tấm trong tháo được khối phải"),
    "FELT": ("351304", "FRONT - DECOR INNER PANEL FELT - DR", "Nỉ tấm trong khối phải"),
    "RISER": ("351402", "FRONT - AIR INTAKE RISER - DR", "Ống gió đứng khối phải"),
    "TLOW": ("351403", "FRONT - AIR TRANSITION - LOWER - DR", "Ống chuyển hướng dưới"),
    "FBOX": ("351404", "FRONT - SUPPLY FAN BOX - DR", "Hộp quạt cấp"),
    "TUP": ("351405", "FRONT - AIR TRANSITION - UPPER - DR", "Ống chuyển hướng trên"),
    "FAN1": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM - 1", "Quạt 12 V"),
    "FAN2": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM - 2", "Quạt 12 V"),
    "FRAME": ("351306", "FRONT - DECOR FRAME - DR", "Khung trang trí phải (hàn)"),
}

# Overlaps made on purpose, with the reason; any other clash over 1 mm3 fails the build.
EXPECTED = [
    (("TLOW", "RISER"), "the lower transition space starts inside the riser's top end, where they join"),
    (("TLOW", "FBOX"), "the lower transition space meets the fan box inlet"),
    (("TUP", "FBOX"), "the upper transition space meets the fan box outlet"),
    (("TUP", "TUP2"), "two halves of one duct space"),
]


FRAME_PN = "351306"
FRAME = ("351306", "FRONT - DECOR FRAME - DR", "Khung trang trí phải (hàn)")
S20, S40, S60, S80 = "20 x 20 x 1.5", "40 x 20 x 1.5", "60 x 20 x 1.5", "80 x 20 x 1.5"
ACCESS_BOLTS = ([("ab_x", "ab_z0 + %d * ab_p" % k) for k in range(6)] + [("ab_x1", "ab_zb"), ("ab_x2", "ab_zb")] +
                [("ab_x1", "ab_zt"), ("ab_x2", "ab_zt")])


def frame_members():
    """DR's welded tube frame as data: each tube a polygon on an origin plane, extruded along the third axis.
    Front ring just inside the front skin, back ring just in front of the back plates, and tubes between them along
    the corner facet, the top chamfer and the DT joint, clear of the air parts and of the air unit's way in (D-87:
    no back-ring tube crosses the opening behind the access and inner panels)."""
    yf0, yf1 = "(%s + dr_skin_t)" % YF, "(%s + dr_skin_t + fr_w)" % YF
    yb0, yb1 = "(%s - dr_back_t - fr_w)" % YB, "(%s - dr_back_t)" % YB
    xf = "((dr_fc - dr_skin_t - dr_fny * %s) / dr_fnx)" % yf0           # inner facet face at the front ring's face
    zch = "((dr_cc - dr_skin_t - dr_cny * %s) / dr_cnz)" % yf0          # inner chamfer face there
    xj = "(%s + fix_xtr + (%s - %s) * (dt_xr - fix_xtr) / (pod_d / 2 - ch_yb))" % (XL, yf1, YF)  # DT joint, ring back
    bot, top = FL.line(0, 1, ZB), FL.line(0, -1, "-pod_h")
    right, dtjb, ledge = FL.line(-1, 0, "-pod_w / 2"), FL.line(1, 0, "(%s + dt_xr)" % XL), FL.line(0, -1, "-dt_zb")
    diag, rl = FL.line("fg_dnx", "fg_dnz", "fg_dc"), FL.line("fg_rnx", "fg_rnz", "fg_rc")
    facf, chf, dtjf = FL.line(-1, 0, "-" + xf), FL.line(0, -1, "-" + zch), FL.line(1, 0, xj)
    sk3, sk23 = "dr_skin_t", "dr_skin_t + fr_w"
    M = []

    def add(key, name, axes, pts, along, a, b, section=S20, axis=(0, 1), ends=None):
        M.append({"key": key, "name": name, "axes": axes, "pts": pts, "along": along, "a": a, "b": b,
                  "section": section, "axis": axis,
                  "ends": ends or "mitred to its neighbours (angles on the frame drawing)"})

    front = FL.ring([(bot, "0 mm", "fr_w"), (facf, "0 mm", "fr_w"), (chf, "0 mm", "fr_w"), (dtjf, "0 mm", "fr_w"),
                     (diag, sk3, "fr_w"), (rl, sk3, "fr_w")])
    for k, (key, nm) in enumerate((("F01", "FRONT RING BOTTOM"), ("F02", "FRONT RING FACET SIDE"),
                                   ("F03", "FRONT RING TOP"), ("F04", "FRONT RING DT JOINT"),
                                   ("F05", "FRONT RING DIAGONAL"), ("F06", "FRONT RING GLASS EDGE"))):
        add(key, nm, ("x", "z"), front[k], "y", yf0, yf1)
    back = FL.ring([(bot, "0 mm", "fr_wbot"), (right, sk3, "fr_wb"), (top, sk3, "fr_w"), (dtjb, "0 mm", "fr_w"),
                    (ledge, "0 mm", "fr_w"), (diag, sk3, "fr_w"), (rl, sk3, "fr_w")])
    for k, (key, nm, sec) in enumerate((("B01", "BACK RING BOTTOM", S40), ("B02", "BACK RING BOLT LINE", S80),
                                        ("B03", "BACK RING TOP", S20), ("B04", "BACK RING DT JOINT", S20),
                                        ("B05", "BACK RING DT LEDGE", S20), ("B06", "BACK RING DIAGONAL", S20),
                                        ("B07", "BACK RING GLASS EDGE", S20))):
        add(key, nm, ("x", "z"), back[k], "y", yb0, yb1, sec)
    # cross tubes in the front ring: v1's 724, and the shelf the fan box stands on
    rl23, dg23 = FL.push(rl, sk23), FL.push(diag, sk23)
    for key, nm, edge, z0 in (("F07", "FRONT RING CROSS 724", rl23, "%s + fr_h1" % ZB),
                              ("F08", "FRONT RING FAN BOX SHELF", dg23, "fb_z0 - fr_w")):
        z1 = "%s + fr_w" % z0
        add(key, nm, ("x", "z"), [FL.meet(edge, FL.line(0, 1, z0)), ("(%s - fr_w)" % xf, z0), ("(%s - fr_w)" % xf, z1),
                                  FL.meet(edge, FL.line(0, 1, z1))], "y", yf0, yf1,
            ends="left end cut to the glass-edge tube's slope, right end square")
    # band tube under the back plate's top band, between the DT joint tube and the bolt-line tube
    xb0, xb1 = "(%s + dt_xr + fr_w)" % XL, "(%s - dr_skin_t - fr_wb)" % XR
    add("B08", "BACK RING BAND", ("x", "z"), [(xb0, ZT), (xb1, ZT), (xb1, "%s + fr_wband" % ZT), (xb0, "%s + fr_wband" % ZT)],
        "y", yb0, yb1, S60, ends="square both ends")
    # along the corner facet (plan), from the front ring's facet tube to the bolt-line tube; none beside the riser,
    # which stands 3 mm inside the facet skin
    fac = FL.line("-dr_fnx", "-dr_fny", "-dr_fc")
    f3, f23 = FL.push(fac, sk3), FL.push(fac, sk23)
    xs = "(%s - dr_skin_t)" % XR
    fac_pts = [FL.meet(f3, FL.line(1, 0, xf)), FL.meet(f3, FL.line(1, 0, xs)), (xs, yb0), FL.meet(f23, FL.line(0, 1, yb0)),
               FL.meet(f23, FL.line(1, 0, xf))]
    for key, nm, z0 in (("C01", "FACET TUBE BOTTOM", ZB), ("C02", "FACET TUBE KNEE", "fix_zk - fr_w / 2"),
                        ("C03", "FACET TUBE FAN BOX SHELF", "fb_z0 - fr_w"), ("C04", "FACET TUBE FAN BOX TOP", "fb_z0 + fb_h - fr_w"),
                        ("C05", "FACET TUBE TOP", "%s - fr_w" % zch)):
        add(key, nm, ("x", "y"), fac_pts, "z", z0, "%s + fr_w" % z0,
            ends="front end square to the facet tube's side, back end square, back corner cut to the side skin")
    # along the top chamfer (side view), from the front ring's top tube up to the back ring's top tube
    chl = FL.line("-dr_cny", "-dr_cnz", "-dr_cc")
    c3, c23 = FL.push(chl, sk3), FL.push(chl, sk23)
    zs_top = "(pod_h - dr_skin_t)"
    ch_pts = [(yf0, zch), FL.meet(c3, FL.line(0, 1, zs_top)), (yb0, zs_top), FL.meet(c23, FL.line(1, 0, yb0)),
              FL.meet(c23, FL.line(0, 1, zch))]
    xc_l, xc_r = "(%s + dt_xr + fr_w)" % XL, "(%s - 2 * fr_w)" % xf
    for key, nm, x0 in (("C06", "CHAMFER TUBE LEFT", xc_l), ("C07", "CHAMFER TUBE MIDDLE", "((%s + %s) / 2 - fr_w / 2)" % (xc_l, xc_r)),
                        ("C08", "CHAMFER TUBE RIGHT", xc_r)):
        add(key, nm, ("y", "z"), ch_pts, "x", x0, "%s + fr_w" % x0,
            ends="lower end sits on the front ring's top tube, upper end square to the back ring's top tube")
    # along the DT joint (plan), on the ledge DT stands on: the joint turns at X 449 from v1's slanted line to
    # straight back, so two tubes mitred at the turn
    jl = FL.line("dr_jnx", "dr_jny", "dr_jc")
    j20 = FL.push(jl, "fr_w")
    xdt, xdt20 = "(%s + dt_xr)" % XL, "(%s + dt_xr + fr_w)" % XL
    turn_o, turn_i = FL.meet(jl, FL.line(1, 0, xdt)), FL.meet(j20, FL.line(1, 0, xdt20))
    add("C09", "DT JOINT TUBE SLANTED", ("x", "y"), [FL.meet(jl, FL.line(0, 1, yf1)), turn_o, turn_i,
                                                     FL.meet(j20, FL.line(0, 1, yf1))],
        "z", ZT, "%s + fr_w" % ZT, ends="front end square to the front ring, back end mitred to C10")
    add("C10", "DT JOINT TUBE STRAIGHT", ("x", "y"), [turn_o, (xdt, yb0), (xdt20, yb0), turn_i], "z", ZT, "%s + fr_w" % ZT,
        axis=(0, 1), ends="front end mitred to C09, back end square to the back ring")
    return M


# part-only designs for the part drawings (a base view shows its whole design): the full block is built and checked,
# then every other component is removed
SCOPES = {"assy": None, "frame": "FRAME", "skin": "SKIN"}


def scope_doc(scope):
    if scope == "assy":
        return DOC_NAME
    pn, nm, _vn = PARTS[SCOPES[scope]]
    return "%s_%s_%s_CAD" % (pn, REV, nm.replace(" - ", "-").replace(" ", "-"))


def build(app):
    scope = ARGS.get("scope", "assy")
    rpn, rname, rvn = (PN, NAME, VN) if SCOPES[scope] is None else PARTS[SCOPES[scope]]
    design = L.start_design(app, rpn, "%s | %s | %s" % (rname, rvn, REV))
    sk_params, sk_path, sk_rev = L.load_skeleton_params(ARGS["repo_root"])
    L.add_params(design, sk_params)
    L.add_params(design, L.LIB_PARAMS)
    L.add_params(design, L.GLASS_PARAMS)
    L.add_params(design, L.JF_PARAMS)
    L.add_params(design, OWN)
    root = design.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    comps, bodies = {}, {}
    # D-87: the riser, the transitions, the fan box and its fans ship joined (14.9 kg) with plug-in connectors and
    # slide into DR through its inner face on site, so they form one sub-assembly
    air = L.new_comp(root, AIR_ASSY[0], AIR_ASSY[1], AIR_ASSY[2], REV)
    AIR_KEYS = ("RISER", "TLOW", "FBOX", "TUP", "FAN1", "FAN2")

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(air if key in AIR_KEYS else root, pn, nm, vn, REV)
        comps[key] = c
        return c

    def prism(c, axes, pts, along, a, b, sketch, feat, op=NEW, body=None):
        sk = L.poly(design, c, L.plane_of(c, axes), axes, 0, sketch, pts)
        return L.extrude_span(c, sk, along, a, b, op, [body] if body else None, feat)

    # ---- 351301 skin: the outer shape, then shelled
    c = comp("SKIN")
    outline = [L.g_BR("0 mm"), (XR, ZB), (XR, "pod_h"), (XL + " + fix_xtr", "pod_h"), L.g_TR("0 mm"), L.g_K("0 mm")]
    f = prism(c, ("x", "z"), outline, "y", YF, YB, "FRONT - DR OUTLINE (BAND TOP TO ROOF, INNER EDGE ON THE GLASS LINES)",
              "EXTRUDE - DR OUTER SHAPE")
    skin = f.bodies.item(0)
    prism(c, ("x", "y"), [(XR + " - dr_xc", YF), (XR, "-dr_yc"), (XR, YF)], "z", "0 mm", "pod_h",
          "CORNER FACET - DR", "CUT - DR CORNER FACET", CUT, skin)
    prism(c, ("x", "y"), [(XL + " + fix_xtr", YF), (XL + " + dt_xr", "-ch_yb"), (XL + " + dt_xr", YB),
                          (XL + " + fix_xtr", YB)], "z", "dt_zb", "pod_h",
          "JOINT - DR TO DT (v1 LINE TO X 449)", "CUT - DR TO DT JOINT", CUT, skin)
    prism(c, ("y", "z"), [(YF, "ch_zlo"), ("-ch_yb", "pod_h"), (YF, "pod_h")], "x", XL, XR,
          "CHAMFER - DR TOP FRONT", "CUT - DR TOP CHAMFER", CUT, skin)
    # faces left open: the back face (inner panel and back plate go there) and the faces DT sits on
    yb, dtz, jx = L.ev(design, YB), L.ev(design, "dt_zb"), L.ev(design, XL + " + dt_xr")
    open_faces = adsk.core.ObjectCollection.create()
    kinds = []
    for fc in skin.faces:
        p = fc.pointOnFace
        ok, n = fc.evaluator.getNormalAtPoint(p)
        px, py, pz = p.x * 10, p.y * 10, p.z * 10
        if abs(n.y - 1) < 1e-6 and abs(py - yb) < 0.05:
            kinds.append("back")
        elif pz > dtz + 0.05 and abs(n.z) < 1e-6 and n.x < -0.5 and n.y >= -1e-6:
            kinds.append("DT joint")
        elif abs(n.z - 1) < 1e-6 and abs(pz - dtz) < 0.05:
            kinds.append("DT ledge")
        else:
            continue
        open_faces.add(fc)
    if sorted(kinds) != ["DT joint", "DT joint", "DT ledge", "back"]:
        raise RuntimeError("faces to leave open: found %s" % kinds)
    si = c.features.shellFeatures.createInput(open_faces, False)
    si.insideThickness = L.vi("dr_skin_t")
    sh = c.features.shellFeatures.add(si)
    sh.name = "SHELL - DR SKIN 3 MM (OPEN AT THE BACK AND AT DT)"
    # the slot the pane's hidden channel enters through: right edge and diagonal, gu_prof_w wide, gu_prof_d deep
    slot = [(L.right_x(ZB), ZB), (L.right_x(ZB, "gu_prof_d"), ZB), L.g_K("gu_prof_d"),
            (L.diag_x(ZT, "gu_prof_d"), ZT), (L.diag_x(ZT), ZT), L.g_K("0 mm")]
    prism(c, ("x", "z"), slot, "y", GY + " - gu_prof_w / 2 - slot_clear", GY + " + gu_prof_w / 2 + slot_clear",
          "SLOT - GLASS CHANNEL ALONG THE INNER EDGE", "CUT - SKIN SLOT FOR THE GLASS CHANNEL", CUT, skin)
    # the base, open inside the skins from the front face round the corner facet and the side back to the closing
    # plate; the left edge is the inner-edge skin (the glass line pushed in by the skin)
    def ff(e):        # front face / facet corner, both pushed in by e
        return ("((dr_fc - %s - dr_fny * (%s + %s)) / dr_fnx)" % (e, YF, e), "(%s + %s)" % (YF, e))

    def fs(e):        # facet / side corner, both pushed in by e
        return ("(%s - %s)" % (XR, e), "((dr_fc - %s - dr_fnx * (%s - %s)) / dr_fny)" % (e, XR, e))
    xl = L.right_x(ZB + " + dr_skin_t", "dr_skin_t")
    yend = YB + " - dr_back_t"
    intake = [(xl, "(%s + dr_skin_t)" % YF), ff("dr_skin_t"), fs("dr_skin_t"), ("(%s - dr_skin_t)" % XR, yend), (xl, yend)]
    prism(c, ("x", "y"), intake, "z", ZB + " - 1 mm", ZB + " + dr_skin_t + 1 mm",
          "INTAKE - DR BASE OPEN OVER THE MESH BAND PIECE", "CUT - BASE OPENING OVER THE BAND PIECE", CUT, skin)
    skin.name = "DR SKIN ACP 3"
    bodies["SKIN"] = skin

    # ---- 351302 fixed back plate (aluminium, J-FRONT-01): a strip on the right wall's bolt line and the band behind
    # the soffit; 351305 the access panel between it and the air column comes off, so the air unit slides in (D-87)
    tip_z = "((fg_rc + dr_skin_t - fg_rnx * dr_col_x0) / fg_rnz)"
    zs = ZB + " + dr_skin_t"
    c = comp("BACK")
    zband = ZT + " + dr_band_dz"
    back = [("dr_strip_x0", zs), (XR + " - dr_skin_t", zs), (XR + " - dr_skin_t", "pod_h - dr_skin_t"),
            (XL + " + dt_xr", "pod_h - dr_skin_t"), (XL + " + dt_xr", zband), ("dr_strip_x0", zband)]
    f = prism(c, ("x", "z"), back, "y", YB + " - dr_back_t", YB, "OUTLINE - DR BACK PLATE (FIXED STRIP AND TOP BAND)",
              "EXTRUDE - DR BACK PLATE")
    bp = f.bodies.item(0)
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - J-FRONT-01 RIVNUTS (6)",
                   [("jf_x", "jf_z%d" % i) for i in range(1, 7)], "jf_hole")
    L.extrude_span(c, sk, "y", YB + " - dr_back_t - 1 mm", YB + " + 1 mm", CUT, [bp], "CUT - J-FRONT-01 RIVNUT HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    bp.name = "DR BACK PLATE AL 2"
    bodies["BACK"] = bp
    c = comp("ACCESS")
    acc = [(L.right_x(zs, "dr_skin_t"), zs), ("dr_strip_x0", zs), ("dr_strip_x0", zband), ("dr_col_x0", zband),
           ("dr_col_x0", tip_z)]
    # the removable panels sit on the frame's back face, Y -647, so they stand 1 mm proud of the 2 mm fixed plate
    ya, yb_acc = YB + " - dr_back_t", YB + " - dr_back_t + dr_acc_t"
    f = prism(c, ("x", "z"), acc, "y", ya, yb_acc, "OUTLINE - DR ACCESS PANEL (REMOVABLE, D-87)",
              "EXTRUDE - DR ACCESS PANEL")
    ap = f.bodies.item(0)
    prism(c, ("x", "z"), [("op_x0", "op_z0"), ("op_x0 + op_w", "op_z0"), ("op_x0 + op_w", "op_z0 + op_h"),
                          ("op_x0", "op_z0 + op_h")], "y", ya + " - 1 mm", yb_acc + " + 1 mm",
          "OPENING - INTO THE AIR COLUMN TOP", "CUT - OPENING INTO THE AIR COLUMN", CUT, ap)
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - ACCESS PANEL BOLTS OVER THE RIVNUTS (10)",
                   ACCESS_BOLTS, "ab_hole")
    L.extrude_span(c, sk, "y", ya + " - 1 mm", yb_acc + " + 1 mm", CUT, [ap], "CUT - ACCESS PANEL BOLT HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - AIR COLUMN HOOK STUD RIVNUTS (2)",
                   [("dr_stud_x", "dr_stud_z1"), ("dr_stud_x", "dr_stud_z2")], "jf_hole")
    L.extrude_span(c, sk, "y", ya + " - 1 mm", yb_acc + " + 1 mm", CUT, [ap], "CUT - HOOK STUD RIVNUT HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    ap.name = "DR ACCESS PANEL AL 3"
    bodies["ACCESS"] = ap

    # ---- 351303 removable inner panel and 351304 its felt: the part of the back face seen from inside
    inner = [("dr_col_x0", tip_z), ("dr_col_x0", zband), (XL + " + dt_xr", zband), (XL + " + dt_xr", ZT),
             (L.diag_x(ZT, "dr_skin_t"), ZT), L.g_K("dr_skin_t")]
    yi0, yi1 = YB + " - dr_back_t", YB + " - dr_back_t + dr_skin_t"
    c = comp("INNER")
    f = prism(c, ("x", "z"), inner, "y", yi0, yi1, "OUTLINE - DR INNER PANEL (SEEN FROM INSIDE)",
              "EXTRUDE - DR INNER PANEL")
    bodies["INNER"] = f.bodies.item(0)
    bodies["INNER"].name = "DR INNER PANEL ACP 3"
    c = comp("FELT")
    f = prism(c, ("x", "z"), inner, "y", yi1, yi1 + " + felt_t", "OUTLINE - DR INNER PANEL FELT", "EXTRUDE - FELT 9")
    bodies["FELT"] = f.bodies.item(0)
    bodies["FELT"].name = "DR INNER PANEL FELT 9"

    # ---- air parts from the D-60 table
    c = comp("RISER")
    rect = [("ri_x0", "ri_y0"), ("ri_x0 + ri_w", "ri_y0"), ("ri_x0 + ri_w", "ri_y0 + ri_d"), ("ri_x0", "ri_y0 + ri_d")]
    f = prism(c, ("x", "y"), rect, "z", ZB + " + dr_skin_t + ri_gap", "ri_zt", "PLAN - INTAKE RISER OUTER",
              "EXTRUDE - INTAKE RISER")
    rb = f.bodies.item(0)
    inner_r = [("ri_x0 + ri_t", "ri_y0 + ri_t"), ("ri_x0 + ri_w - ri_t", "ri_y0 + ri_t"),
               ("ri_x0 + ri_w - ri_t", "ri_y0 + ri_d - ri_t"), ("ri_x0 + ri_t", "ri_y0 + ri_d - ri_t")]
    prism(c, ("x", "y"), inner_r, "z", ZB + " + dr_skin_t + ri_gap - 1 mm", "ri_zt + 1 mm", "PLAN - INTAKE RISER BORE",
          "CUT - INTAKE RISER BORE", CUT, rb)
    rb.name = "INTAKE RISER 1 MM STEEL"
    bodies["RISER"] = rb
    c = comp("TLOW")
    f = prism(c, ("x", "z"), [("ri_x0", "ri_zt"), ("ri_x0 + ri_w", "ri_zt"), ("fb_x0 + fb_w", "fb_z0"), ("fb_x0", "fb_z0")],
              "y", "ri_y0", "ri_y0 + ri_d", "SIDE - LOWER TRANSITION SPACE", "EXTRUDE - LOWER TRANSITION SPACE")
    bodies["TLOW"] = f.bodies.item(0)
    bodies["TLOW"].name = "HOLD LOWER TRANSITION DUCT SPACE"
    c = comp("FBOX")
    box = [("fb_x0", "fb_y0"), ("fb_x0 + fb_w", "fb_y0"), ("fb_x0 + fb_w", "fb_y0 + fb_d"), ("fb_x0", "fb_y0 + fb_d")]
    f = prism(c, ("x", "y"), box, "z", "fb_z0", "fb_z0 + fb_h", "PLAN - FAN BOX OUTER", "EXTRUDE - FAN BOX")
    fbb = f.bodies.item(0)
    bore = [("fb_x0 + fb_t", "fb_y0 + fb_t"), ("fb_x0 + fb_w - fb_t", "fb_y0 + fb_t"),
            ("fb_x0 + fb_w - fb_t", "fb_y0 + fb_d - fb_t"), ("fb_x0 + fb_t", "fb_y0 + fb_d - fb_t")]
    prism(c, ("x", "y"), bore, "z", "fb_z0 - 1 mm", "fb_z0 + fb_h + 1 mm", "PLAN - FAN BOX BORE", "CUT - FAN BOX BORE",
          CUT, fbb)
    fbb.name = "SUPPLY FAN BOX 2 MM (LINING AND BULKHEAD: AIR DETAIL)"
    bodies["FBOX"] = fbb
    for i, key in enumerate(("FAN1", "FAN2")):
        c = comp(key)
        x0 = "fb_x0 + fb_w / 2 - fan_s - 2 mm" if i == 0 else "fb_x0 + fb_w / 2 + 2 mm"
        y0 = "fb_y0 + fb_d / 2 - fan_s / 2"
        f = prism(c, ("x", "y"), [(x0, y0), ("%s + fan_s" % x0, y0), ("%s + fan_s" % x0, "%s + fan_s" % y0),
                                  (x0, "%s + fan_s" % y0)], "z", "fb_z0 + fb_h / 2", "fb_z0 + fb_h / 2 + fan_t",
                  "PLAN - FAN %d" % (i + 1), "EXTRUDE - FAN %d (CATALOGUE ENVELOPE)" % (i + 1))
        bodies[key] = f.bodies.item(0)
        bodies[key].name = "FAN %d NF-A14 ENVELOPE" % (i + 1)
    c = comp("TUP")
    # over the fan box, then back toward the opening, kept clear of the corner facet (which is at X 1192 at Y -720)
    yb_in = YB + " - dr_back_t"
    tup = [("fb_x0", "fb_y0"), ("fb_x0 + fb_w", "fb_y0"), ("fb_x0 + fb_w", "fb_y0 + fb_d - 2 * fb_t"),
           ("op_x0 + op_w", "fb_y0 + fb_d - 2 * fb_t"), ("op_x0 + op_w", yb_in), ("fb_x0", yb_in)]
    f = prism(c, ("x", "y"), tup, "z", "fb_z0 + fb_h", "op_z0 + op_h", "PLAN - UPPER TRANSITION SPACE",
              "EXTRUDE - UPPER TRANSITION SPACE")
    bodies["TUP"] = f.bodies.item(0)
    bodies["TUP"].name = "HOLD UPPER TRANSITION DUCT SPACE"
    drop = [("fb_x0 + fb_w", "fb_y0 + fb_d - 2 * fb_t"), ("op_x0 + op_w", "fb_y0 + fb_d - 2 * fb_t"),
            ("op_x0 + op_w", yb_in), ("fb_x0 + fb_w", yb_in)]
    f = prism(c, ("x", "y"), drop, "z", "op_z0", "fb_z0 + fb_h", "PLAN - UPPER TRANSITION DROP TO THE OPENING",
              "EXTRUDE - UPPER TRANSITION DROP")
    bodies["TUP2"] = f.bodies.item(0)
    bodies["TUP2"].name = "HOLD UPPER TRANSITION DUCT SPACE - DROP"

    # ---- 351306 the welded tube frame (stage 2)
    c = comp("FRAME")
    tubes = FL.build_members(design, c, L, frame_members(), "fr_t")
    bodies.update(tubes)
    yb1 = YB + " - dr_back_t"
    for key, name, centres, dia in (
            ("B02", "HOLES - J-FRONT-01 RIVNUT TAILS AND BOLT TIPS (6)", [("jf_x", "jf_z%d" % i) for i in range(1, 7)],
             "fr_hole_jf"),
            ("B02", "HOLES - ACCESS PANEL RIVNUTS ON THE BOLT-LINE TUBE (6)", ACCESS_BOLTS[:6], "fr_hole_rn"),
            ("B01", "HOLES - ACCESS PANEL RIVNUTS ON THE BOTTOM TUBE (2)", ACCESS_BOLTS[6:8], "fr_hole_rn"),
            ("B08", "HOLES - ACCESS PANEL RIVNUTS ON THE BAND TUBE (2)", ACCESS_BOLTS[8:10], "fr_hole_rn")):
        sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, name, centres, dia)
        L.extrude_span(c, sk, "y", yb1 + " - fr_t - 1 mm", yb1 + " + 0.5 mm", CUT, [tubes[key]],
                       "CUT - " + name.split(" - ", 1)[1],
                       profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])

    # ---- materials
    acp = L.material(design, "ACP 3 mm PE core EV3038 (1300 kg/m3, calculation)", "Aluminum", 1300.0)
    felt = L.material(design, "PET felt 9 mm (200 kg/m3, calculation: 1.8 kg/m2)", "Aluminum", 200.0)
    steel = L.material(design, "Galvanised steel (7850 kg/m3)", "Steel", 7850.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    al6063 = L.material(design, "Aluminium 6063-T6 tube (2700 kg/m3)", "Aluminum", 2700.0)
    for k in tubes:
        bodies[k].material = al6063
    for k, m in (("SKIN", acp), ("BACK", alu), ("ACCESS", alu), ("INNER", acp), ("FELT", felt), ("RISER", steel),
                 ("TLOW", env), ("FBOX", alu), ("TUP", env), ("TUP2", env), ("FAN1", env), ("FAN2", env)):
        bodies[k].material = m
    looks = {"SKIN": ["Paint - Enamel Glossy (Yellow)"], "BACK": ["Aluminum - Satin"], "ACCESS": ["Aluminum - Satin"],
             "INNER": ["Paint - Enamel Glossy (Yellow)"], "FELT": ["Fabric (Gray)", "Plastic - Matte (Grey)"],
             "RISER": ["Steel - Satin", "Paint - Enamel Glossy (Grey)"],
             "FBOX": ["Aluminum - Satin"], "FAN1": ["Plastic - Matte (Black)"], "FAN2": ["Plastic - Matte (Black)"],
             "TLOW": ["Paint - Enamel Glossy (Red)"], "TUP": ["Paint - Enamel Glossy (Red)"],
             "TUP2": ["Paint - Enamel Glossy (Red)"]}
    looks.update({k: ["Aluminum - Satin"] for k in tubes})
    for k, b in bodies.items():
        a = L.appearance(design, looks[k])
        if a:
            b.appearance = a

    # ---- checks
    n_tl, bad, loose = L.health(design)
    hits, bad_clash = L.clash_check(bodies, EXPECTED)
    print("skeleton parameters: %s (%s), %d loaded" % (os.path.relpath(sk_path, ARGS["repo_root"]), sk_rev, len(sk_params)))
    print("bodies %d, timeline %d items, unhealthy %d, loose sketches %d, parameters %d" % (
        len(bodies), n_tl, len(bad), len(loose), design.userParameters.count))
    for k, b in bodies.items():
        bb = L.box(b)
        print("BODY|%s|%s|%g x %g x %g|%s|%.1f cm3|%.3f kg" % (k, b.name, round(bb[3] - bb[0], 2), round(bb[4] - bb[1], 2),
                                                             round(bb[5] - bb[2], 2), bb, b.volume, b.physicalProperties.mass))
    print("clash pairs %d, unexpected %d" % (len(hits), len(bad_clash)))
    for a, b, v in hits:
        print("CLASH|%s|%s|%d mm3|%s" % (a, b, v, "UNEXPECTED" if (a, b, v) in bad_clash else "listed"))
    sk_in = comps["SKIN"].sketches.itemByName("INTAKE - DR BASE OPEN OVER THE MESH BAND PIECE")
    gross = sk_in.profiles.item(0).areaProperties().area / 1e4
    zb_cm = L.ev(design, ZB) / 10.0
    feet = 0.0
    for k in tubes:
        for fc in bodies[k].faces:
            ok, n = fc.evaluator.getNormalAtPoint(fc.pointOnFace)
            if n.z < -0.999 and abs(fc.pointOnFace.z - zb_cm) < 0.005:
                feet += fc.area / 1e4
    print("base opening over the band piece: %.4f m2 gross, %.4f m2 under the frame's bottom tubes, %.4f m2 free "
          "(0.028 or more: PM ruling)" % (gross, feet, gross - feet))
    print("FRAME|%d tubes, %.2f kg, %d shells failed" % (len(tubes), L.comp_mass(comps["FRAME"]),
          sum(1 for k in tubes if not any(f.name.startswith("SHELL - TUBE %s " % k) for f in comps["FRAME"].features.shellFeatures))))
    print("DR box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DR checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))
    if SCOPES[scope] is not None:
        keep = PARTS[SCOPES[scope]][0]
        for occ in [root.occurrences.item(i) for i in range(root.occurrences.count)]:
            if occ.component.partNumber != keep:
                occ.deleteMe()
        print("scope %s: kept %s only, %d components left" % (scope, keep, root.occurrences.count))


ANCHORS = [
    ("SKIN", 0, "fix_xtr - pod_w / 2"), ("SKIN", 3, "pod_w / 2"), ("SKIN", 2, "fg_vis_zb"), ("SKIN", 5, "pod_h"),
    ("SKIN", 1, "-pod_d / 2"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 0, "dt_xr - pod_w / 2"), ("BACK", 3, "pod_w / 2 - dr_skin_t"), ("BACK", 5, "pod_h - dr_skin_t"),
    ("ACCESS", 3, "dr_strip_x0"), ("ACCESS", 5, "fg_vis_zt + dr_band_dz"),
    ("ACCESS", 4, "-pod_d / 2 + decor_d - dr_back_t + dr_acc_t"),
    ("INNER", 3, "dr_col_x0"), ("INNER", 5, "fg_vis_zt + dr_band_dz"),
    ("FELT", 4, "-pod_d / 2 + decor_d - dr_back_t + dr_skin_t + felt_t"),
    ("RISER", 2, "fg_vis_zb + dr_skin_t + ri_gap"), ("RISER", 5, "ri_zt"), ("RISER", 0, "ri_x0"),
    ("FBOX", 0, "fb_x0"), ("FBOX", 2, "fb_z0"), ("FBOX", 5, "fb_z0 + fb_h"),
    ("TUP", 5, "op_z0 + op_h"),
    ("FRAME", 0, "((fg_dc + dr_skin_t - fg_dnz * (fg_vis_zt)) / fg_dnx)"), ("FRAME", 3, "pod_w / 2 - dr_skin_t"),
    ("FRAME", 1, "-pod_d / 2 + dr_skin_t"), ("FRAME", 4, "-pod_d / 2 + decor_d - dr_back_t"),
    ("FRAME", 2, "fg_vis_zb"), ("FRAME", 5, "pod_h - dr_skin_t"),
]


def export_all(app):
    design = adsk.fusion.Design.cast(app.activeProduct)
    doc = app.activeDocument
    L.ensure_saved_part_number(doc, design, PN)
    root_dir = ARGS["repo_root"]
    f3d = L.export(design, root_dir, F3D_REL, "f3d")
    step = L.export(design, root_dir, STEP_REL, "step")
    print("export %s: %d bytes" % (F3D_REL, os.path.getsize(f3d)))
    print("export %s: %d bytes" % (STEP_REL, os.path.getsize(step)))
    ev = lambda e: L.ev(design, e)
    members = frame_members()
    frame_comp = [c for c in design.allComponents if c.partNumber == FRAME_PN][0]
    tube_m = sum(FL.member_numbers(m, ev)["length"] for m in members) / 1000.0
    gt = "general tolerance ISO 2768-m"
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-49, D-59, D-60, D-79, D-87; PM rulings 2026-10-31 "
         "and 2026-11-01; this build", "skin bonded to the welded tube frame 351306; plates and panels on the frame"),
        ("351301", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1, bonded to "
         "the frame", "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 1300 kg/m3)", "DRAFT",
         "D-12, D-49; skeleton DR shape", "one flat panel per outside face: " + DXF_SKIN_REL.split("/")[-1] +
         "; bond to the frame per the joints register's ACP bond spec"),
        (FRAME_PN, FRAME[1], FRAME[2], 1, "made: welded frame, %d tubes (cut list %s)" % (len(members),
         CUT_REL.split("/")[-1]), "aluminium EN AW-6063-T6 tube 20 x 20 x 1.5, 40 x 20 x 1.5, 60 x 20 x 1.5 and 80 x 20 x 1.5, "
         "finish: mill finish (hidden, D-79)", "cad", "calculation (CAD, 2700 kg/m3, tubes shelled)", "DRAFT",
         "v1 decor frame drawing (front and back frames); D-79; joints register HOLD-10",
         "%.1f m of tube; rivnuts 838003 fitted in the factory: 10 for the access panel bolts; the bolt-line tube has "
         "6 holes 14 for the J-FRONT-01 rivnut tails" % tube_m),
        ("351302", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made (laser-cut sheet, no drawing: D-89 part 4)",
         "aluminium EN AW-5754-H22 sheet 2.0 mm, finish: mill finish (hidden, D-79); " + gt, "cad",
         "calculation (CAD, 2700 kg/m3)", "DRAFT", "joints register J-FRONT-01 (HOLD-10 answered: 2 mm aluminium)",
         "DXF " + DXF_FLAT["BACK"] + "; fixed: the strip on X +1224 with 6 holes 9.53 +0.10/0 for the rivnuts 838003 "
         "(critical: on the wall's bolt line), and the band behind the soffit; blind-riveted to the frame (HOLD: rivet)"),
        ("351305", PARTS["ACCESS"][1], PARTS["ACCESS"][2], 1, "made (laser-cut sheet, no drawing: D-89 part 4), "
         "removable", "aluminium EN AW-5754-H22 sheet 3.0 mm, finish: mill finish (hidden, D-79); " + gt, "cad",
         "calculation (CAD, 2700 kg/m3)", "DRAFT", "D-60 air table (opening 203 x 215); D-87; PM ruling 2026-11-01 "
         "(column hook studs, panel carries the 10 kg column)",
         "DXF " + DXF_FLAT["ACCESS"] + "; 10 bolts M6 x 16 838001 with washers 838004 through holes 7.0 into rivnuts "
         "838003 in the frame, a 1 mm perimeter gasket over the rivnut heads (HOLD: gasket tape); 2 holes 9.53 "
         "+0.10/0 at X 971, Z 1700 and 1850 for rivnuts 838003 "
         "with the column's 2 hook studs (this joint to be added to the joints register); comes off after the column "
         "and the inner panel, so the air unit 350004 slides in"),
        ("351303", PARTS["INNER"][1], PARTS["INNER"][2], 1, "made (CNC-routed ACP, no drawing: D-89 part 4), "
         "removable", "ACP 3 mm, finish as supplied (the felt covers its face); " + gt, "cad", "calculation (CAD)",
         "DRAFT", "D-59, D-60",
         "DXF " + DXF_FLAT["INNER"] + "; lifts off for the fan box; held on the frame by 4 clips (HOLD: clip, "
         "assumed 0.04 kg each)"),
        ("351304", PARTS["FELT"][1], PARTS["FELT"][2], 1, "made (laser-cut PET felt sheet, no drawing: D-89 part 4), "
         "glued to 351303 at the factory", "PET felt 9 mm, finish Dark Gray (D-79); outline +/-2, " + gt, "cad",
         "calculation (CAD, 1.8 kg/m2)",
         "DRAFT; emission certificate HOLD", "D-31; hardware selection A3", "DXF " + DXF_FLAT["FELT"]),
        ("350004", AIR_ASSY[1], AIR_ASSY[2], 1, "assembly, joined at the factory (D-87)", "-", None, "", "DRAFT",
         "D-87", "ships joined, 14.9 kg (D-60 table), slides into DR through its inner face; plug-in connectors; the "
         "fan box stands on the frame's shelf tubes F08 and C03 (fixing HOLD: air detail)"),
        ("351402", PARTS["RISER"][1], PARTS["RISER"][2], 1, "made (sheet metal duct)", "1 mm galvanised steel", "cad",
         "calculation (CAD, 7850 kg/m3)", "DRAFT", "D-60 air table", "open foot 140 mm over the base opening"),
        ("351403", PARTS["TLOW"][1], PARTS["TLOW"][2], 1, "reserved duct space", "-", 1.5, "assumption",
         "HOLD: the Air Engineer's transition detail", "D-60 air table", ""),
        ("351404", PARTS["FBOX"][1], PARTS["FBOX"][2], 1, "made", "2 mm aluminium, 50 mm lining inside", 5.1,
         "source (D-60 air table, box and transition)", "DRAFT; lining and bulkhead HOLD (air detail)",
         "D-60 air table", "12 from the fixed glass channel, so the frame's inner-edge tube fits"),
        ("351405", PARTS["TUP"][1], PARTS["TUP"][2], 1, "reserved duct space", "-", 0.0, "included in 351404's 5.1 kg",
         "HOLD: the Air Engineer's transition detail", "D-60 air table", ""),
        ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V", 2, "bought",
         "Noctua NF-A14 industrialPPC-3000 PWM, 12 V", 0.3, "assumption (D-60 air table)", "HOLD: product (PM ruling, one number for all four fans)",
         "hardware selection F1", "on the fan box bulkhead, blowing up"),
    ]
    total = L.write_parts_list(design, os.path.join(root_dir, BOM_REL), rows, PN, NAME, VN)
    print("parts list %s: %d rows, unit mass %.2f kg" % (BOM_REL, len(rows), total))
    # the skin's panels laid flat (one ACP panel per outside face, 45 degree mitred edges as v1), 1:1 in mm
    skin_comp = [c for c in design.allComponents if c.partNumber == PARTS["SKIN"][0]][0]
    try:
        placed = L.write_panels_dxf(os.path.join(root_dir, DXF_SKIN_REL), L.skin_panels(skin_comp.bRepBodies.item(0)))
        print("DXF skin panels %s: %d panels %s" % (DXF_SKIN_REL, len(placed), placed))
    except Exception as exc:          # the model exports stand; the flat patterns are reported and retried
        print("DXF skin panels FAILED: %r" % (exc,))
    # the tube cut list (no part_number column: the frame row above carries the part)
    import csv
    with open(os.path.join(root_dir, CUT_REL), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "member", "name", "section", "length_mm", "qty", "ends", "status"])
        w.writerows(FL.cut_list_rows(members, ev, FRAME_PN))
    print("cut list %s: %d tubes, %.2f m" % (CUT_REL, len(members), tube_m))
    for key, fn in DXF_FLAT.items():
        comp_ = [c for c in design.allComponents if c.partNumber == PARTS[key][0]][0]
        try:
            res = FL.write_plate_dxf(os.path.join(root_dir, "v2/03-Manufacturing/front", fn), comp_.bRepBodies.item(0))
            print("DXF %s: %s x %s, %d holes, origin at pod %s" % (fn, res[0], res[1], res[2], res[3]))
        except Exception as exc:
            print("DXF %s FAILED: %r" % (fn, exc))
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as fh:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % (PARTS[k][0], PARTS[k][1]), "index": i, "expression": e} for k, i, e in ANCHORS]},
            fh, indent=1, ensure_ascii=False)
    print("anchors %s: %d" % (ANCHORS_REL, len(ANCHORS)))
    before, after, diff = L.step_reread(app, doc, design, step)
    print("STEP re-read in Fusion: model box %s, STEP box %s, max diff %.3f mm" % (before, after, diff))


SHOTS = [("v2/01-CAD-Native/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR-FRONT_IMG.png", "front"),
         ("v2/01-CAD-Native/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR-ISO_IMG.png", "iso-top-right")]


def run(_context):
    """step: build | export | post (export, pictures, edit test with --arg edits=...) | all (build, save, post)."""
    app = adsk.core.Application.get()
    step = ARGS.get("step", "build")
    doc = app.activeDocument
    scope = ARGS.get("scope", "assy")
    want_doc = scope_doc(scope)
    if doc is None or not doc.name.startswith(want_doc):
        raise RuntimeError("active document is %r, not %s: open it with the runner's --doc" % (
            doc.name if doc else None, want_doc))
    if scope != "assy" and step != "build":
        raise RuntimeError("a part-only design is only built (the runner's --save keeps it)")
    L.run_steps(app, ARGS, HERE, step, build, export_all, SHOTS, ANCHORS_REL)
