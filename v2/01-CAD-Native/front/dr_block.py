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
- 351305 the removable inner face panel (D-130: one panel where there were an
  access panel and the inner panel 351303, now cancelled) and 351304 its 9 mm
  felt on the part that shows inside the pod, between the glass edge, the air
  column and the soffit (D-59, D-60);
- reserved air spaces where AIR's supply fan box assembly goes (the D-60 table's
  sizes): the intake riser, the fan box with its two fans and the two
  transitions. AIR designs and lists those parts (PM ruling 2026-11-01). The room-side intake
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
    print("helper module %s: %s" % (m.__name__, m.__file__))
    return m


L = load_lib()


def load_frame_lib():
    spec = importlib.util.spec_from_file_location("frame_lib_run", os.path.join(HERE, "frame_lib.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("helper module %s: %s" % (m.__name__, m.__file__))
    return m


FL = load_frame_lib()


def load_member_pns():
    spec = importlib.util.spec_from_file_location("frame_members_pn_run", os.path.join(HERE, "frame_members_pn.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("helper module %s: %s" % (m.__name__, m.__file__))
    return m


MP = load_member_pns()

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
WELD_BOM_REL = "v2/03-Manufacturing/front/351306_%s_FRONT-DECOR-FRAME-DR_BOM.csv" % REV   # the weldment's own parts list (D-120)
# flat parts cut from sheet: their DXF gives the outline and every hole, so they need no drawing (D-89 part 4)
DXF_FLAT = {"BACK": "351302_%s_FRONT-DECOR-BACK-PLATE-DR_DXF.dxf" % REV,
            "ACCESS": "351305_%s_FRONT-DECOR-INNER-FACE-PANEL-DR-REMOVABLE_DXF.dxf" % REV,
            "FELT": "351304_%s_FRONT-DECOR-INNER-PANEL-FELT-DR_DXF.dxf" % REV}

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"      # DR's front face and back face (Y -850, -645)
GY = "-glass_y"
ZB, ZT = "fg_vis_zb", "fg_vis_zt"                  # band top and DT's underside

OWN = [
    ("dr_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dr_back_t", "1.5 mm", "mm", "confirmed",
     "joints register J-FRONT-01: the back plate is aluminium 1.0 to 2.7 thick at each bolt, for the rivnuts (HOLD-10); "
     "1.5, not 2, so DR stays under 20 kg (D-03; PM ruling 2026-11-01)"),
    ("dr_strip_x0", "jf_x - 2 * jf_hole - 0.5 mm", "mm", "calculation",
     "the fixed back strip's inner edge, 2 hole diameters plus 0.5 from the J-FRONT-01 rivnut holes (mechanical "
     "check C09); the rest of the back comes off for the air unit (D-87)"),
    ("dr_acc_t", "3 mm", "mm", "calculation",
     "access panel 3 mm aluminium: it carries the air column's 10 kg on two hook studs 222 mm from its screwed edge "
     "(PM ruling 2026-11-01); 2 mm would see about 110 MPa if the column pulls 50 N, 3 mm about 50 MPa"),
    # D-130 (PM rulings 2026-11-01, Joints' seal and stop pair): one removable inner face panel, on stops off the frame
    ("dr_rn_head", "0.76 mm", "mm", "source",
     "rivnut 838003 head 0.76 +/-0.08 (joints register H-03: Sherex CAH2-610-4.2, zinc-plated steel, D-131)"),
    ("dr_stop_w", "1.6 mm", "mm", "source",
     "an 838004 washer (ISO 7093 6.4 x 18, 1.6 thick) on each rivnut head: the panel's stop (Joints, D-130)"),
    ("dr_pnl_gap", "dr_rn_head + dr_stop_w", "mm", "calculation",
     "the inner face panel stands 2.36 off the frame on its stops; the 4.0 seal 848013 is squeezed to it (D-130)"),
    ("dr_seal_w", "8 mm", "mm", "source", "848013 access panel seal, about 8 wide (joints register H-34; D-130)"),
    ("dr_seal_t", "4 mm", "mm", "source", "848013 access panel seal, 4.0 thick very soft foam (joints register H-34)"),
    ("dr_pitch", "400 mm", "mm", "source", "the panel's screws about 400 apart (Joints' seal and stop pair, D-130)"),
    ("dr_drop", "40 mm", "mm", "calculation",
     "service: with the column off, the panel drops 40 to clear the soffit's underside (its top edge is 35 over it), "
     "then comes out (PM ruling 2026-11-01)"),
    ("dr_pull", "100 mm", "mm", "calculation", "service: how far out the model shows the dropped panel coming"),
    ("dr_acc_face_y", "-pod_d / 2 + decor_d - dr_back_t + dr_pnl_gap + dr_acc_t", "mm", "calculation",
     "named value for AIR (PM rulings 2026-11-01, D-130): the room-side face of DR's inner face panel, where AIR's "
     "air column and soffit start; Y -641.14, the 3 mm panel 2.36 off the frame on its stops"),
    ("dr_piece_x0", "1150 mm", "mm", "confirmed",
     "with the band behind the soffit dropped, the back plate keeps a short piece from here to the side above the "
     "access panel: the soffit stops at X 1161 (AIR), 11 short of it (PM ruling 2026-11-01)"),
    ("dr_band_dz", "35 mm", "mm", "calculation",
     "the back plate's top band starts this far above DT's underside: the removable panels' top edges land 35 on the "
     "frame's band tube, so the access panel's top bolts sit 2 hole diameters from its edge and the rivnuts 2 from "
     "the tube's edge (C09); the access panel keeps 45 over the opening into the column"),
    ("dr_stud_x", "971 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): the air column's two hook studs at X 971"),
    ("dr_stud_z1", "1700 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): lower hook stud Z 1700"),
    ("dr_stud_z2", "1850 mm", "mm", "source", "PM ruling 2026-11-01 (CEILING): upper hook stud Z 1850"),
    ("felt_t", "9 mm", "mm", "source", "the factory's 9 mm PET felt (D-31; hardware selection A3)"),
    ("dr_col_x0", "949 mm", "mm", "source", "air report 7f (AIR #91): the air column's left face, X 949 (column X 949 "
     "to 1161)"),
    ("dr_col_x1", "1161 mm", "mm", "source", "air report 7f (AIR #91; calc.py D60 col): the air column's right edge, "
     "X 1161, AIR's named value (D-130)"),
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
    # opening from DR into the air column's top (D-60 air table)
    ("op_x0", "961 mm", "mm", "source", "air report 7f: the opening into the column from X 961"),
    ("op_w", "dr_col_x1 - op_x0", "mm", "calculation",
     "D-130: the opening runs to the column's edge, 200 wide (air report 7f: 200 x 215; the old table's 203 retired)"),
    ("op_z0", "1895 mm", "mm", "source", "D-60 air table: opening Z 1895 to 2110"),
    ("op_h", "215 mm", "mm", "source", "D-60 air table"),
    # ---- the tube frame (stage 2): v1's front and back frames of 16 mm steel box (sources/v1 decor frame drawing),
    # in 6063-T6 aluminium tube (D-79)
    ("fr_w", "20 mm", "mm", "calculation",
     "frame tube 20 x 20 x 1.5, 6063-T6 (D-79): bending stiffness E*I = 4.5e8 N.mm2, about v1's 16 x 16 x 1 steel box "
     "(4.7e8), at 0.30 kg/m against 0.47"),
    ("fr_t", "1.5 mm", "mm", "calculation",
     "frame tube wall 1.5 where AIR's supply fan box (8.8 kg) stands: the shelf tubes F08 and C03"),
    ("fr_t_rn", "1.2 mm", "mm", "confirmed",
     "wall of the ledge tube B05, which carries DT's two spigot rivnuts: 1.2, as D-85 kept the wall panels' "
     "perimeter members for their rivnuts (PM ruling 2026-11-01); the tubes under the inner face panel take fr_t_pnl"),
    ("fr_t_pnl", "1.5 mm", "mm", "source",
     "wall of the tubes under the inner face panel that take its rivnuts: 1.5 or more, as 1.0 is marginal for an M6 "
     "rivnut (Joints, D-130)"),
    ("fr_t_sk", "1.0 mm", "mm", "confirmed",
     "wall of the tubes that only hold the skin and the plates: 1.0, as D-85's inner studs (PM ruling 2026-11-01, DR "
     "under 20 kg, D-03); E*I 3.2e8 N.mm2, two thirds of v1's 16 x 16 x 1 steel box, with the ACP bonded on"),
    ("fr_wb", "80 mm", "mm", "calculation",
     "bolt-line tube 80 x 20 x 1.5 behind the fixed strip: the J-FRONT-01 rivnut tails and bolt tips go into it "
     "through 14 mm holes (HOLD-10: the plate with the frame behind), and the access panel lands 37 on its other "
     "side, wide enough for its bolts and rivnuts at 2 diameters from every edge (C09); 3 clear of the duct spaces"),
    ("fr_wbot", "40 mm", "mm", "assumption", "back ring's bottom tube 40 x 20 x 1.5: the access panel's lower bolts"),
    ("fr_wband", "60 mm", "mm", "assumption",
     "band tube 60 x 20 x 1.5 at DT's underside: the access panel's top bolts and the top band's rivets land on it"),
    ("fr_h1", "724 mm", "mm", "source", "v1 decor frame drawing (front frame): first cross tube 724 above the bottom"),
    # D-131 skin spans (PM ruling 2026-11-01): the front face's top bay, above the fan box shelf, flexed 5.0 mm under
    # 100 N; one cross tube at its mid-height brings it to 1.7 (skin_spans.py), so AIR's fan box stands back from the
    # skin, behind that tube (which also keeps the fans' vibration off the skin)
    ("fb_gap", "5 mm", "mm", "assumption", "the fan box's front, clear behind the front ring's cross tube F09"),
    ("fb_y0", "-pod_d / 2 + dr_skin_t + fr_w + fb_gap", "mm", "calculation",
     "fan box front, Y -822: the D-60 table's -847 moved 25 back behind the cross tube F09 (PM ruling 2026-11-01, D-131); "
     "AIR's model follows (sb_yf)"),
    ("fr_hole_jf", "14 mm", "mm", "calculation",
     "hole in the bolt-line tube's back wall round each J-FRONT-01 rivnut: body 9.50 max and its bulge (SHX), and the "
     "bolt tip, go into the tube"),
    ("fr_hole_rn", "9.53 mm", "mm", "source",
     "joints register H-03: hole for the rivnut 838003 (Sherex CAH2-610-4.2, zinc-plated steel, D-131; HOLD-04)"),
    # J-FRONT-02 (PM ruling 2026-11-01): DR stands on 2 spigots on BASE's support behind the mesh piece, a round hole
    # and a slot along X in the bottom back tube's bottom wall
    ("dr_sp_x1", "1050 mm", "mm", "confirmed", "J-FRONT-02: DR's round spigot hole (PM ruling 2026-11-01)"),
    ("dr_sp_x2", "1147 mm", "mm", "confirmed", "J-FRONT-02: DR's spigot slot, along X (PM ruling 2026-11-01)"),
    ("sp_hole", "8.5 mm", "mm", "source", "R-J13: spigot hole 8.5 round at one end, 8.5 x 14 slot at the other"),
    ("sp_slot", "14 mm", "mm", "source", "R-J13: the slot 14 long along the edge"),
    # J-FRONT-03 (PM ruling 2026-11-01): DT's two spigots stand in rivnuts in the top of DR's ledge tube B05
    ("dt_sp_x1", "-pod_w / 2 + dt_xr - 179 mm", "mm", "confirmed",
     "J-FRONT-03: DT's round-hole spigot on DR's ledge, X 270, 36 in from the ledge tube's left end"),
    ("dt_sp_dx", "140 mm", "mm", "confirmed", "J-FRONT-03: DT's slot spigot 140 from the first (PM ruling 2026-11-01)"),
    ("dt_sp_y", "-pod_d / 2 + decor_d - 12.88 mm", "mm", "calculation",
     "J-FRONT-03: the spigots' Y, -657.88, the middle of where DR's ledge tube and DT's bottom back tube overlap"),
    ("ab_hole", "7 mm", "mm", "source",
     "the pod's M6 clearance hole, 7.0 (D-64, D-75; the mechanical check's hole rule M6-CLEARANCE-7) for the inner "
     "face panel's screws 838001"),
    ("ab_x", "pod_w / 2 - dr_skin_t - fr_wb + 2 * fr_hole_rn + 2 mm", "mm", "calculation",
     "the panel's screw line on the bolt-line tube: the rivnut 2 diameters plus 2 from the tube's inner edge (C09)"),
    ("ab_zt", "fg_vis_zt + 2 * fr_hole_rn + 1 mm", "mm", "calculation",
     "the panel's screw line on the band tube: its rivnuts 2 diameters plus 1 above the tube's lower edge (C09)"),
    ("dr_sc_clear", "40 mm", "mm", "calculation",
     "the panel's end screws 40 from the corners of its screw line, clear of the frame's welded corners (D-130)"),
    ("dr_hd_d", "12 mm", "mm", "source",
     "a plain M6 washer under each panel screw's head, ISO 7089 6.4 x 12 x 1.6 (PM ruling 2026-11-01: the socket "
     "heads stay, one 5 mm key on site; the 18 mm washer made every felt hole break out; Joints numbers it)"),
    ("dr_felt_web", "3 mm", "mm", "calculation",
     "felt left between each felt hole and the felt's edge (PM ruling 2026-11-01)"),
    ("dr_felt_hole", "dr_hd_d + 2 mm", "mm", "calculation",
     "closed felt holes over the panel's screw heads: the washer and 1 mm round it, each plugged with felt cut from "
     "the same sheet (no bare socket heads on the room side); the screws stand 10 from the felt's edges, so "
     "dr_felt_web stays (PM rulings 2026-11-01)"),
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
# the back plate's band behind the soffit: dropped once CEILING confirms the soffit's own 2 mm door-side plate closes
# that area with no gap for air or sound (PM ruling 2026-11-01: one structure there, not two); a short piece from
# dr_piece_x0 to the side stays above the access panel, where the soffit (X up to 1161) doesn't reach
DROP_BAND = False
# the air parts' spaces carry this after their name in the CAD (PM ruling 2026-11-01: AIR designs and lists the parts)
RESERVED_AIR = ("RISER", "TLOW", "FBOX", "TUP")
RESERVED_SUFFIX = " - RESERVED AIR SPACE"


def cad_name(key):
    """The component's name in the CAD: number, name, and the reserved-space mark for the air parts."""
    return "%s %s%s" % (PARTS[key][0], PARTS[key][1], RESERVED_SUFFIX if key in RESERVED_AIR else "")
# every air part is an AIR number in AIR's tree, designed by AIR (PM ruling 2026-11-01, so nothing is counted twice):
# DR keeps only the spaces the riser, the fan box and the two transitions take. They are typed "reserved air space",
# carry no mass and need no drawing; the CAD names say so too
RESERVED_TYPE = "reserved air space"
RESERVED_STATUS = "HOLD: reserved air space; AIR designs and lists the part (PM ruling 2026-11-01)"
PARTS = {
    "SKIN": ("351301", "FRONT - DECOR SKIN - DR", "Tấm ốp alu khối phải"),
    "BACK": ("351302", "FRONT - DECOR BACK PLATE - DR", "Tấm hậu khối phải"),
    # D-130's notes (the PM, 2026-11-01): 351305 renamed DR's removable inner face panel, the one panel since D-130
    "ACCESS": ("351305", "FRONT - DECOR INNER FACE PANEL - DR - REMOVABLE", "Tấm mặt trong tháo được khối phải"),
    "FELT": ("351304", "FRONT - DECOR INNER PANEL FELT - DR", "Nỉ tấm trong khối phải"),
    "SEAL": ("848013", "SEALS - ACCESS PANEL SEAL - 4.0 THICK - VERY SOFT FOAM PSA",
             "Gioăng tấm thăm - xốp rất mềm dày 4.0, keo dán sẵn"),
    "RISER": ("351402", "FRONT - AIR INTAKE RISER - DR", "Ống gió đứng khối phải"),
    "TLOW": ("351403", "FRONT - AIR TRANSITION - LOWER - DR", "Ống chuyển hướng dưới"),
    "FBOX": ("351404", "FRONT - SUPPLY FAN BOX - DR", "Hộp quạt cấp"),
    "TUP": ("351405", "FRONT - AIR TRANSITION - UPPER - DR", "Ống chuyển hướng trên"),
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
# tube sections and walls (PM ruling 2026-11-01): skin-only tubes 1.0, rivnut tubes 1.2, the fan box shelf 1.5
S20, S40, S60, S80 = "20 x 20 x 1.0", "40 x 20 x 1.5", "60 x 20 x 1.5", "80 x 20 x 1.5"   # D-130: rivnut walls 1.5
S20_SHELF = "20 x 20 x 1.5"
S20_RN = "20 x 20 x 1.2"            # (no tube now: the ledge tube takes the panel's rivnuts too, so 1.5)
S20_PNL = "20 x 20 x 1.5"           # the ledge, diagonal and glass-edge tubes: the panel's rivnuts (D-130, Joints)
WALL = {"20 x 20 x 1.0": "fr_t_sk", "20 x 20 x 1.2": "fr_t_rn", "40 x 20 x 1.5": "fr_t_pnl", "60 x 20 x 1.5": "fr_t_pnl",
        "80 x 20 x 1.5": "fr_t_pnl", "20 x 20 x 1.5": "fr_t"}
# D-130: the inner face panel's screw and seal line runs on the middles of the frame tubes under its edges, each
# line a*x + b*z = c with its normal into the panel; edge k runs along tube PANEL_LINES[k] from corner k to corner k+1
PANEL_LINES = [
    ("B01", FL.line(0, 1, "fg_vis_zb + fr_wbot / 2")),                    # the bottom tube, Z 130
    ("B02", FL.line(-1, 0, "-ab_x")),                                      # the bolt-line tube, X 1188
    ("B08", FL.line(0, -1, "-ab_zt")),                                     # the band tube, Z 2140
    ("B04", FL.line(1, 0, "-pod_w / 2 + dt_xr + fr_w / 2")),               # the DT joint tube: the 30 mm step
    ("B05", FL.line(0, -1, "-(fg_vis_zt - fr_w / 2)")),                    # DT's ledge tube, Z 2110
    ("B06", FL.line("fg_dnx", "fg_dnz", "fg_dc + dr_skin_t + fr_w / 2")),  # the diagonal tube's middle
    ("B07", FL.line("fg_rnx", "fg_rnz", "fg_rc + dr_skin_t + fr_w / 2")),  # the glass-edge tube's middle
]
# screws per edge, about dr_pitch apart (Joints' 400) and dr_sc_clear from the corners: 21 in all
SCREWS_PER_EDGE = [2, 6, 3, 0, 2, 3, 5]
# where an edge's last screw stands further from its end corner than dr_sc_clear: the glass-edge tube's lowest
# screw is moved up so its felt hole keeps the web at the air column's edge and its washer clears the column's left
# face (PM ruling 2026-11-01; AIR clears the other heads it sits on)
END_CLEAR = {6: "dr_sc_col"}
# and where an edge's first screw stands further from its start corner: the band tube B08's screw by the bolt-line
# tube keeps two rivnut-hole diameters and 0.5 to the band tube's square end (C09; it was 18.9 at dr_sc_clear)
START_CLEAR = {2: "dr_sc_b08"}
for _k in range(len(PANEL_LINES)):
    _u, _v = FL.meet(PANEL_LINES[_k - 1][1], PANEL_LINES[_k][1])
    OWN.append(("dr_pl%dx" % _k, _u, "mm", "calculation", "the inner face panel's screw line, corner %d, X" % _k))
    OWN.append(("dr_pl%dz" % _k, _v, "mm", "calculation", "the inner face panel's screw line, corner %d, Z" % _k))
for _k in range(len(PANEL_LINES)):
    _j = (_k + 1) % len(PANEL_LINES)
    OWN.append(("dr_pe%d" % _k, "sqrt((dr_pl%dx - dr_pl%dx) * (dr_pl%dx - dr_pl%dx) + (dr_pl%dz - dr_pl%dz) * "
                "(dr_pl%dz - dr_pl%dz))" % (_j, _k, _j, _k, _j, _k, _j, _k), "mm", "calculation",
                "the inner face panel's screw line along tube %s, its length" % PANEL_LINES[_k][0]))
OWN.append(("dr_sc_b08", "ab_x - (pod_w / 2 - dr_skin_t - fr_wb) + 2 * fr_hole_rn + 0.5 mm", "mm", "calculation",
            "the band tube B08's screw by the bolt-line tube from the screw line's corner: two rivnut-hole diameters and "
            "0.5 from B08's square end at the bolt-line tube (C09's rule)"))
OWN.append(("dr_sc_col", "(dr_pl0x - (dr_col_x0 - dr_felt_hole / 2 - dr_felt_web)) * dr_pe6 / (dr_pl0x - dr_pl6x)",
            "mm", "calculation",
            "the glass-edge tube B07's lowest screw from the screw line's bottom corner: its felt hole keeps "
            "dr_felt_web of felt at the air column's edge (X dr_col_x0) and its washer stands clear of the column's "
            "left face (PM ruling 2026-11-01)"))


def panel_screws():
    """[(tube, (x, z))]: the inner face panel's screws, evenly along each edge of its line from dr_sc_clear to
    dr_sc_clear short of its corners (D-130)."""
    out = []
    for k, (key, _l) in enumerate(PANEL_LINES):
        n, j = SCREWS_PER_EDGE[k], (k + 1) % len(PANEL_LINES)
        c0, c1 = START_CLEAR.get(k, "dr_sc_clear"), END_CLEAR.get(k, "dr_sc_clear")
        for i in range(n):
            t = "((%s + %d * (dr_pe%d - %s - %s) / %d) / dr_pe%d)" % (c0, i, k, c0, c1, n - 1, k)
            out.append((key, ("dr_pl%dx + (dr_pl%dx - dr_pl%dx) * %s" % (k, j, k, t),
                              "dr_pl%dz + (dr_pl%dz - dr_pl%dz) * %s" % (k, j, k, t))))
    return out


def felt_outline():
    """The felt's outline as (x, z) expressions: the glass's slanted edges on the left, the air column's edge on the
    right (X dr_col_x0), DT's underside (the soffit's underside) at the top; its foot where the glass-edge line meets
    the column's edge."""
    tip_z = "((fg_rc + dr_skin_t - fg_rnx * dr_col_x0) / fg_rnz)"
    return [("dr_col_x0", tip_z), ("dr_col_x0", ZT), (L.diag_x(ZT, "dr_skin_t"), ZT), L.g_K("dr_skin_t")]


def felt_holes(evf):
    """[(x, z) expressions] of the panel's screws under the felt, each a closed felt hole dr_felt_hole across with at
    least dr_felt_web of felt to the felt's edge; raises when a hole would break out of the felt, or when a washer
    would reach the air column's left face (X dr_col_x0), so neither can come back unseen (PM rulings 2026-11-01).
    evf: an expression's value in mm (Fusion's in the build, the offline evaluator in the drawing specs)."""
    poly = [(evf(u), evf(v)) for u, v in felt_outline()]
    r_h, web = evf("dr_felt_hole") / 2.0, evf("dr_felt_web")
    x_col, r_w = evf("dr_col_x0"), evf("dr_hd_d") / 2.0
    out, bad = [], []
    for key, pt in panel_screws():
        x, z = evf(pt[0]), evf(pt[1])
        inside, d = False, 1e9
        for i in range(len(poly)):
            (x1, z1), (x2, z2) = poly[i], poly[(i + 1) % len(poly)]
            if (z1 > z) != (z2 > z) and x < x1 + (z - z1) * (x2 - x1) / (z2 - z1):
                inside = not inside
            dx, dz = x2 - x1, z2 - z1
            t = max(0.0, min(1.0, ((x - x1) * dx + (z - z1) * dz) / (dx * dx + dz * dz)))
            d = min(d, ((x1 + t * dx - x) ** 2 + (z1 + t * dz - z) ** 2) ** 0.5)
        if abs(x - x_col) < r_w + 2.0:
            bad.append("%s's screw at X %.1f, Z %.1f: its washer comes within %.1f of the air column's left face "
                       "(X %.0f)" % (key, x, z, abs(x - x_col) - r_w, x_col))
        if inside or d < r_h:
            if not inside or d < r_h + web - 0.01:
                bad.append("%s's screw at X %.1f, Z %.1f: its felt hole leaves %.2f of felt to the felt's edge "
                           "(%.1f needed)" % (key, x, z, (d - r_h) if inside else -(d + r_h), web))
            out.append(pt)
    if bad:
        raise RuntimeError("the inner face panel's screws and the felt: " + "; ".join(bad))
    return out


def seal_outline(push):
    """The seal's edge: the screw line pushed by `push` (into the panel when positive), corner for corner."""
    lines = [FL.push(l, push) for _k, l in PANEL_LINES]
    return [FL.meet(lines[k - 1], lines[k]) for k in range(len(lines))]


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

    def add(key, name, axes, pts, along, a, b, section=S20, axis=(0, 1), ends=None, t=None):
        M.append({"key": key, "name": name, "axes": axes, "pts": pts, "along": along, "a": a, "b": b,
                  "section": section, "t": t or WALL[section], "axis": axis,
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
                                        ("B05", "BACK RING DT LEDGE", S20_PNL), ("B06", "BACK RING DIAGONAL", S20_PNL),
                                        ("B07", "BACK RING GLASS EDGE", S20_PNL))):
        add(key, nm, ("x", "z"), back[k], "y", yb0, yb1, sec, t="fr_t_pnl" if sec == S20_PNL else None)
    # cross tubes in the front ring: v1's 724, and the shelf the fan box stands on
    rl23, dg23 = FL.push(rl, sk23), FL.push(diag, sk23)
    # F09 (D-131 skin spans, PM ruling 2026-11-01): across the front face's top bay at its mid-height, between the
    # shelf tube F08 and the top tube F03 (whose underside is the inner chamfer face less fr_w at the ring's face)
    z_f09 = "((fb_z0 + %s - fr_w) / 2 - fr_w / 2)" % zch
    for key, nm, edge, z0, sec in (("F07", "FRONT RING CROSS 724", rl23, "%s + fr_h1" % ZB, S20),
                                   ("F08", "FRONT RING FAN BOX SHELF", dg23, "fb_z0 - fr_w", S20_SHELF),
                                   ("F09", "FRONT RING CROSS OVER THE FAN BOX", dg23, z_f09, S20)):
        z1 = "%s + fr_w" % z0
        add(key, nm, ("x", "z"), [FL.meet(edge, FL.line(0, 1, z0)), ("(%s - fr_w)" % xf, z0), ("(%s - fr_w)" % xf, z1),
                                  FL.meet(edge, FL.line(0, 1, z1))], "y", yf0, yf1, sec,
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
    # (no tube at the knee: the shelf tube C03 is 100 above it; dropped with the middle chamfer tube to keep DR under
    # 19 kg as shipped, PM ruling 2026-11-01)
    for key, nm, z0 in (("C01", "FACET TUBE BOTTOM", ZB),
                        ("C03", "FACET TUBE FAN BOX SHELF", "fb_z0 - fr_w"), ("C04", "FACET TUBE FAN BOX TOP", "fb_z0 + fb_h - fr_w"),
                        ("C05", "FACET TUBE TOP", "%s - fr_w" % zch)):
        add(key, nm, ("x", "y"), fac_pts, "z", z0, "%s + fr_w" % z0, S20_SHELF if key == "C03" else S20,
            ends="front end square to the facet tube's side, back end square, back corner cut to the side skin")
    # along the top chamfer (side view), from the front ring's top tube up to the back ring's top tube
    chl = FL.line("-dr_cny", "-dr_cnz", "-dr_cc")
    c3, c23 = FL.push(chl, sk3), FL.push(chl, sk23)
    zs_top = "(pod_h - dr_skin_t)"
    ch_pts = [(yf0, zch), FL.meet(c3, FL.line(0, 1, zs_top)), (yb0, zs_top), FL.meet(c23, FL.line(1, 0, yb0)),
              FL.meet(c23, FL.line(0, 1, zch))]
    xc_l, xc_r = "(%s + dt_xr + fr_w)" % XL, "(%s - 2 * fr_w)" % xf
    for key, nm, x0 in (("C06", "CHAMFER TUBE LEFT", xc_l),
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
SCOPES = {"assy": None, "frame": "FRAME", "skin": "SKIN", "felt": "FELT", "panel": "ACCESS"}


def scope_part(scope):
    """(part number, name, Vietnamese name) of the part a part-only design keeps."""
    return AIR_ASSY if SCOPES[scope] == "AIR" else PARTS[SCOPES[scope]]


def scope_doc(scope):
    if scope == "assy":
        return DOC_NAME
    pn, nm, _vn = scope_part(scope)
    return "%s_%s_%s_CAD" % (pn, REV, nm.replace(" - ", "-").replace(" ", "-"))


def build(app):
    scope = ARGS.get("scope", "assy")
    rpn, rname, rvn = (PN, NAME, VN) if SCOPES[scope] is None else scope_part(scope)
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
    air = L.new_comp(root, AIR_ASSY[0], AIR_ASSY[1] + " - RESERVED AIR SPACE", AIR_ASSY[2], REV)
    AIR_KEYS = ("RISER", "TLOW", "FBOX", "TUP")

    def comp(key):
        pn, nm, vn = PARTS[key]
        if key in RESERVED_AIR:       # PM ruling 2026-11-01: AIR designs and lists these parts
            nm += RESERVED_SUFFIX
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
    zs = ZB + " + dr_skin_t"
    c = comp("BACK")
    zband = ZT + " + dr_band_dz"
    if DROP_BAND:   # the strip, and above the access panel a short piece from dr_piece_x0 to the side
        back = [("dr_strip_x0", zs), (XR + " - dr_skin_t", zs), (XR + " - dr_skin_t", "pod_h - dr_skin_t"),
                ("dr_piece_x0", "pod_h - dr_skin_t"), ("dr_piece_x0", zband), ("dr_strip_x0", zband)]
    else:           # the strip and the band behind the soffit, down to the soffit's underside over the inner panel
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
    # ---- 351305 the inner face panel (D-130; PM rulings 2026-11-01): ONE removable 3 mm aluminium panel over the
    # whole opening the air unit goes in by (D-87), where there were two panels and a seam AIR's riser and transitions
    # left no room to back; on stops 2.36 off the frame (an 838004 washer on each rivnut head), sealed all round by
    # 848013 on the frame's tubes, held by M6 x 16 socket heads at about 400 mm; it ships loose and goes on after the
    # air unit. Its outline: the old access panel and inner panel together, its top on the band tube B08 (and on DT's
    # ledge tube left of X 449, under the soffit's underside)
    c = comp("ACCESS")
    acc = [(L.right_x(zs, "dr_skin_t"), zs), ("dr_strip_x0", zs), ("dr_strip_x0", zband), (XL + " + dt_xr", zband),
           (XL + " + dt_xr", ZT), (L.diag_x(ZT, "dr_skin_t"), ZT), L.g_K("dr_skin_t")]
    # placed from AIR's named value itself, so the face AIR builds on and the panel can never drift apart (an
    # unused user parameter is not recomputed when the skeleton changes: the edit test caught it stale)
    ya, yb_acc = "dr_acc_face_y - dr_acc_t", "dr_acc_face_y"
    f = prism(c, ("x", "z"), acc, "y", ya, yb_acc, "OUTLINE - DR INNER FACE PANEL (REMOVABLE, D-87, D-130)",
              "EXTRUDE - DR INNER FACE PANEL")
    ap = f.bodies.item(0)
    prism(c, ("x", "z"), [("op_x0", "op_z0"), ("op_x0 + op_w", "op_z0"), ("op_x0 + op_w", "op_z0 + op_h"),
                          ("op_x0", "op_z0 + op_h")], "y", ya + " - 1 mm", yb_acc + " + 1 mm",
          "OPENING - INTO THE AIR COLUMN TOP", "CUT - OPENING INTO THE AIR COLUMN", CUT, ap)
    screws = panel_screws()
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - THE PANEL'S SCREWS (%d)" % len(screws),
                   [pt for _k, pt in screws], "ab_hole")
    L.extrude_span(c, sk, "y", ya + " - 1 mm", yb_acc + " + 1 mm", CUT, [ap], "CUT - THE PANEL'S SCREW HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - AIR COLUMN HOOK STUD RIVNUTS (2)",
                   [("dr_stud_x", "dr_stud_z1"), ("dr_stud_x", "dr_stud_z2")], "jf_hole")
    L.extrude_span(c, sk, "y", ya + " - 1 mm", yb_acc + " + 1 mm", CUT, [ap], "CUT - HOOK STUD RIVNUT HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    ap.name = "DR INNER FACE PANEL AL 3"
    bodies["ACCESS"] = ap

    # ---- 351304 the felt, glued on the panel's left part: the face seen from inside, beside the air column, up to
    # the soffit's underside at DT's underside (Z 2120, D-61) (351303, the ACP inner panel, is cancelled: D-130)
    inner = felt_outline()
    c = comp("FELT")
    f = prism(c, ("x", "z"), inner, "y", yb_acc, yb_acc + " + felt_t", "OUTLINE - DR INNER FACE PANEL FELT",
              "EXTRUDE - FELT 9")
    bodies["FELT"] = f.bodies.item(0)
    bodies["FELT"].name = "DR INNER FACE PANEL FELT 9"
    # closed holes in the felt over the panel's screws, so no bare socket head shows on the room side; each plugged
    # with felt cut from the same sheet (PM rulings 2026-11-01); felt_holes() refuses a hole that breaks out
    felt_pts = felt_holes(lambda e: L.ev(design, e))
    if felt_pts:
        sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0,
                       "HOLES - OVER THE PANEL'S SCREW HEADS, PLUGGED (%d)" % len(felt_pts), felt_pts, "dr_felt_hole")
        L.extrude_span(c, sk, "y", yb_acc + " - 1 mm", yb_acc + " + felt_t + 1 mm", CUT, [bodies["FELT"]],
                       "CUT - FELT HOLES OVER THE SCREW HEADS", profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    print("FELT HOLES|%d closed holes %.0f over the panel's %d screws, at least %.0f of felt to its edge" % (
        len(felt_pts), L.ev(design, "dr_felt_hole"), len(panel_screws()), L.ev(design, "dr_felt_web")))

    # ---- 848013 the panel's seal (D-130, joints register H-34): one loop on the frame's tubes along the screw line,
    # 4.0 very soft foam squeezed to the 2.36 stop gap; cut round each stop washer when fitted (Joints, option (a))
    c = comp("SEAL")
    ys0 = YB + " - dr_back_t"
    f = prism(c, ("x", "z"), seal_outline("-dr_seal_w / 2"), "y", ys0, ya, "OUTLINE - 848013 SEAL, OUTER EDGE",
              "EXTRUDE - 848013 SEAL (SQUEEZED TO THE STOP GAP)")
    seal = f.bodies.item(0)
    prism(c, ("x", "z"), seal_outline("dr_seal_w / 2"), "y", ys0 + " - 1 mm", ya + " + 1 mm",
          "OUTLINE - 848013 SEAL, INNER EDGE", "CUT - 848013 SEAL, INSIDE THE LOOP", CUT, seal)
    seal.name = "848013 PANEL SEAL 4.0 SQUEEZED TO 2.36"
    bodies["SEAL"] = seal


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
    rb.name = "RESERVED AIR SPACE - INTAKE RISER (AIR 611501)"
    bodies["RISER"] = rb
    c = comp("TLOW")
    f = prism(c, ("x", "z"), [("ri_x0", "ri_zt"), ("ri_x0 + ri_w", "ri_zt"), ("fb_x0 + fb_w", "fb_z0"), ("fb_x0", "fb_z0")],
              "y", "ri_y0", "ri_y0 + ri_d", "SIDE - LOWER TRANSITION SPACE", "EXTRUDE - LOWER TRANSITION SPACE")
    bodies["TLOW"] = f.bodies.item(0)
    bodies["TLOW"].name = "RESERVED AIR SPACE - LOWER TRANSITION (AIR 618103)"
    c = comp("FBOX")
    box = [("fb_x0", "fb_y0"), ("fb_x0 + fb_w", "fb_y0"), ("fb_x0 + fb_w", "fb_y0 + fb_d"), ("fb_x0", "fb_y0 + fb_d")]
    f = prism(c, ("x", "y"), box, "z", "fb_z0", "fb_z0 + fb_h", "PLAN - FAN BOX OUTER", "EXTRUDE - FAN BOX")
    fbb = f.bodies.item(0)
    bore = [("fb_x0 + fb_t", "fb_y0 + fb_t"), ("fb_x0 + fb_w - fb_t", "fb_y0 + fb_t"),
            ("fb_x0 + fb_w - fb_t", "fb_y0 + fb_d - fb_t"), ("fb_x0 + fb_t", "fb_y0 + fb_d - fb_t")]
    prism(c, ("x", "y"), bore, "z", "fb_z0 - 1 mm", "fb_z0 + fb_h + 1 mm", "PLAN - FAN BOX BORE", "CUT - FAN BOX BORE",
          CUT, fbb)
    fbb.name = "RESERVED AIR SPACE - SUPPLY FAN BOX (AIR 610401)"
    bodies["FBOX"] = fbb
    # the supply fans are AIR's too (618401 in AIR's supply box 610401, PM ruling 2026-11-01): inside this space
    c = comp("TUP")
    # over the fan box, then back toward the opening, kept clear of the corner facet (which is at X 1192 at Y -720)
    yb_in = YB + " - dr_back_t"
    tup = [("fb_x0", "fb_y0"), ("fb_x0 + fb_w", "fb_y0"), ("fb_x0 + fb_w", "fb_y0 + fb_d - 2 * fb_t"),
           ("op_x0 + op_w", "fb_y0 + fb_d - 2 * fb_t"), ("op_x0 + op_w", yb_in), ("fb_x0", yb_in)]
    f = prism(c, ("x", "y"), tup, "z", "fb_z0 + fb_h", "op_z0 + op_h", "PLAN - UPPER TRANSITION SPACE",
              "EXTRUDE - UPPER TRANSITION SPACE")
    bodies["TUP"] = f.bodies.item(0)
    bodies["TUP"].name = "RESERVED AIR SPACE - UPPER TRANSITION (AIR 618102)"
    drop = [("fb_x0 + fb_w", "fb_y0 + fb_d - 2 * fb_t"), ("op_x0 + op_w", "fb_y0 + fb_d - 2 * fb_t"),
            ("op_x0 + op_w", yb_in), ("fb_x0 + fb_w", yb_in)]
    f = prism(c, ("x", "y"), drop, "z", "op_z0", "fb_z0 + fb_h", "PLAN - UPPER TRANSITION DROP TO THE OPENING",
              "EXTRUDE - UPPER TRANSITION DROP")
    bodies["TUP2"] = f.bodies.item(0)
    bodies["TUP2"].name = "RESERVED AIR SPACE - UPPER TRANSITION DROP (AIR 618102)"

    # ---- 351306 the welded tube frame (stage 2): a weldment assembly, each tube its own component with Control's
    # member number (D-120, #232); the three facet tubes and the two chamfer tubes are copies
    c = comp("FRAME")
    members = frame_members()
    mparts = FL.member_parts(ARGS["repo_root"], FRAME_PN, MP.DR_MEMBERS)
    print("COPIES|%s" % FL.check_copies(members, mparts, lambda e: L.ev(design, e)))
    native, mcomps, moccs = FL.build_member_components(design, c, L, members, "fr_t", mparts, REV)
    frame_occ = root.allOccurrencesByComponent(c).item(0)
    tubes = FL.root_bodies(frame_occ, native, moccs)
    bodies.update(tubes)
    yb1 = YB + " - dr_back_t"
    # J-FRONT-01's tails, and the inner face panel's rivnuts on the screw line, each tube's in that tube (D-130)
    holes = [("B02", "HOLES - J-FRONT-01 RIVNUT TAILS AND BOLT TIPS (6)", [("jf_x", "jf_z%d" % i) for i in range(1, 7)],
              "fr_hole_jf")]
    for key, _l in PANEL_LINES:
        pts = [pt for k, pt in panel_screws() if k == key]
        if pts:
            holes.append((key, "HOLES - THE INNER FACE PANEL'S RIVNUTS ON %s (%d)" % (key, len(pts)), pts, "fr_hole_rn"))
    for key, name, centres, dia in holes:
        mc = mcomps[key]                     # each hole in its own tube's component
        sk = L.circles(design, mc, mc.xZConstructionPlane, ("x", "z"), 0, name, centres, dia)
        L.extrude_span(mc, sk, "y", yb1 + " - fr_t_pnl - 1 mm", yb1 + " + 0.5 mm", CUT, [native[key]],
                       "CUT - " + name.split(" - ", 1)[1],
                       profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    # J-FRONT-02: the spigot hole and slot (along X) in the bottom back tube's bottom wall, on its centre line
    ysb = "(%s - dr_back_t - fr_w / 2)" % YB
    mc = mcomps["B01"]
    sk = L.circles(design, mc, mc.xYConstructionPlane, ("x", "y"), 0, "HOLES - J-FRONT-02 SPIGOT ROUND AND SLOT ENDS",
                   [("dr_sp_x1", ysb), ("dr_sp_x2 - (sp_slot - sp_hole) / 2", ysb),
                    ("dr_sp_x2 + (sp_slot - sp_hole) / 2", ysb)], "sp_hole")
    L.extrude_span(mc, sk, "z", ZB + " - 1 mm", ZB + " + fr_t_pnl + 0.5 mm", CUT, [native["B01"]],
                   "CUT - J-FRONT-02 SPIGOT HOLE AND SLOT ENDS", profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    sl = [("dr_sp_x2 - (sp_slot - sp_hole) / 2", "%s - sp_hole / 2" % ysb), ("dr_sp_x2 + (sp_slot - sp_hole) / 2", "%s - sp_hole / 2" % ysb),
          ("dr_sp_x2 + (sp_slot - sp_hole) / 2", "%s + sp_hole / 2" % ysb), ("dr_sp_x2 - (sp_slot - sp_hole) / 2", "%s + sp_hole / 2" % ysb)]
    prism(mc, ("x", "y"), sl, "z", ZB + " - 1 mm", ZB + " + fr_t_pnl + 0.5 mm", "SLOT - J-FRONT-02 SPIGOT (MIDDLE)",
          "CUT - J-FRONT-02 SPIGOT SLOT MIDDLE", CUT, native["B01"])
    # J-FRONT-03: rivnuts for DT's two spigots in the top of the ledge tube
    mc = mcomps["B05"]
    sk = L.circles(design, mc, mc.xYConstructionPlane, ("x", "y"), 0, "HOLES - J-FRONT-03 SPIGOT RIVNUTS (2)",
                   [("dt_sp_x1", "dt_sp_y"), ("dt_sp_x1 + dt_sp_dx", "dt_sp_y")], "fr_hole_rn")
    L.extrude_span(mc, sk, "z", ZT + " - fr_t_rn - 0.5 mm", ZT + " + 1 mm", CUT, [native["B05"]],
                   "CUT - J-FRONT-03 SPIGOT RIVNUTS", profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])

    # ---- materials
    # the selected ACP's 0.21 mm skins give 3.5 kg/m2, as WALL, CEILING and AIR count it (selection VT01; acoustics
    # and air report, calculation from the maker's skin spec)
    acp = L.material(design, "ACP 3 mm PE core EV3038, 0.21 mm skins (3.5 kg/m2, calculation)", "Aluminum", 3500.0 / 3.0)
    felt = L.material(design, "PET felt 9 mm (200 kg/m3, calculation: 1.8 kg/m2)", "Aluminum", 200.0)
    steel = L.material(design, "Galvanised steel (7850 kg/m3)", "Steel", 7850.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    al6063 = L.material(design, "Aluminium 6063-T6 tube (2700 kg/m3)", "Aluminum", 2700.0)
    for k in native:
        native[k].material = al6063
    for k, m in (("SKIN", acp), ("BACK", alu), ("ACCESS", alu), ("FELT", felt), ("SEAL", env), ("RISER", env),
                 ("TLOW", env), ("FBOX", env), ("TUP", env), ("TUP2", env)):
        bodies[k].material = m
    looks = {"SKIN": ["Paint - Enamel Glossy (Yellow)"], "BACK": ["Aluminum - Satin"], "ACCESS": ["Aluminum - Satin"],
             "FELT": ["Fabric (Gray)", "Plastic - Matte (Grey)"], "SEAL": ["Plastic - Matte (Black)"],
             "RISER": ["Steel - Satin", "Paint - Enamel Glossy (Grey)"],
             "FBOX": ["Aluminum - Satin"],
             "TLOW": ["Paint - Enamel Glossy (Red)"], "TUP": ["Paint - Enamel Glossy (Red)"],
             "TUP2": ["Paint - Enamel Glossy (Red)"]}
    looks.update({k: ["Aluminum - Satin"] for k in tubes})
    for k, b in bodies.items():
        a = L.appearance(design, looks[k])
        if a:
            (native[k] if k in native else b).appearance = a      # a tube's look on its own component's body

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
    uniq = {mc_.partNumber: mc_ for mc_ in mcomps.values()}
    print("FRAME|%d tubes as %d parts, %.2f kg, %d shells failed" % (
        len(tubes), len(uniq), FL.frame_mass(frame_occ, moccs),
        sum(1 for mc_ in uniq.values() if mc_.features.shellFeatures.count != 1)))
    print("DR box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DR checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))
    if SCOPES[scope] is None:
        service_path(app, design, root, bodies, prism, zs, zband, ya, yb_acc, acc)
    if SCOPES[scope] is not None:
        keep = scope_part(scope)[0]
        nested = SCOPES[scope] in AIR_KEYS          # inside 350004: keep that sub-assembly, then only this part in it
        for occ in [root.occurrences.item(i) for i in range(root.occurrences.count)]:
            if occ.component.partNumber not in (keep, AIR_ASSY[0] if nested else keep):
                occ.deleteMe()
        if nested:
            for occ in [air.occurrences.item(i) for i in range(air.occurrences.count)]:
                if occ.component.partNumber != keep:
                    occ.deleteMe()
        left = root.occurrences.count + (air.occurrences.count if nested else 0)
        print("scope %s: kept %s only, %d components left" % (scope, keep, left))


SERVICE_PICTURE = "v2/01-CAD-Native/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR-SERVICE-PATH_IMG.png"


def service_path(app, design, root, bodies, prism, zs, zband, ya, yb_acc, acc):
    """The inner face panel's service path (PM ruling 2026-11-01), shown and checked, then taken out of the model
    (an envelope, not a part, so it never reaches the STEP or the parts list): with the column off, the panel and its
    felt drop dr_drop, so the panel's top passes under the soffit's underside (Z 2120), then come out dr_pull toward
    the room. The envelope may touch only the panel and its felt; its margins to the soffit's underside and to
    BASE's closing plate (Y -645 under DR, D-62) are printed for the whole-pod check."""
    c = L.new_comp(root, "", "SERVICE PATH - DR INNER FACE PANEL (NOT A PART)", "", REV)
    sweep = [(L.diag_x(ZT, "dr_skin_t"), ZT), (XL + " + dt_xr", ZT), (XL + " + dt_xr", zband), ("dr_strip_x0", zband),
             ("dr_strip_x0", zs + " - dr_drop"), (L.right_x(zs, "dr_skin_t"), zs + " - dr_drop"),
             (L.g_K("dr_skin_t")[0], L.g_K("dr_skin_t")[1] + " - dr_drop"), (L.diag_x(ZT, "dr_skin_t"), ZT + " - dr_drop")]
    f = prism(c, ("x", "z"), sweep, "y", ya, yb_acc + " + felt_t", "SERVICE PATH - THE PANEL DROPS",
              "EXTRUDE - SERVICE PATH DROP")
    drop = f.bodies.item(0)
    drop.name = "SERVICE PATH - PANEL DROPPING"
    dropped = [(x, "%s - dr_drop" % z) for x, z in acc]
    f = prism(c, ("x", "z"), dropped, "y", ya, yb_acc + " + felt_t + dr_pull", "SERVICE PATH - THE PANEL COMES OUT",
              "EXTRUDE - SERVICE PATH OUT")
    out = f.bodies.item(0)
    out.name = "SERVICE PATH - PANEL COMING OUT"
    others = {k: b for k, b in bodies.items() if k not in ("ACCESS", "FELT")}
    others.update({"PATH_DROP": drop, "PATH_OUT": out})
    hits, bad = L.clash_check(others, EXPECTED + [(("PATH_DROP", "PATH_OUT"), "one path, two moves")])
    ev = lambda e: L.ev(design, e)
    top, soffit = ev(zband + " - dr_drop"), ev(ZT)
    low, plate = ev(zs + " - dr_drop"), ev(YB)
    print("SERVICE PATH|%s|top after the drop Z %.1f, %.1f under the soffit's underside (Z %.1f)|bottom after the drop "
          "Z %.1f, its back face Y %.2f, %.2f in front of the closing plate's line (Y %.1f)" % (
              "clear of every other part in DR" if not bad else "BLOCKED BY %s" % bad, top, soffit - top, soffit,
              low, ev(ya), ev(ya) - plate, plate))
    L.take_shots(app, ARGS["repo_root"], app.activeDocument, [(SERVICE_PICTURE, "iso-top-left")])
    occs = root.allOccurrencesByComponent(c)
    for occ in [occs.item(i) for i in range(occs.count)]:
        occ.deleteMe()
    if bad or soffit - top <= 0 or ev(ya) - plate <= 0:
        raise RuntimeError("the inner face panel's service path is blocked: %s" % bad)


ANCHORS = [
    ("SKIN", 0, "fix_xtr - pod_w / 2"), ("SKIN", 3, "pod_w / 2"), ("SKIN", 2, "fg_vis_zb"), ("SKIN", 5, "pod_h"),
    ("SKIN", 1, "-pod_d / 2"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 0, "dr_piece_x0" if DROP_BAND else "dt_xr - pod_w / 2"), ("BACK", 3, "pod_w / 2 - dr_skin_t"), ("BACK", 5, "pod_h - dr_skin_t"),
    ("ACCESS", 3, "dr_strip_x0"), ("ACCESS", 5, "fg_vis_zt + dr_band_dz"), ("ACCESS", 4, "dr_acc_face_y"),
    ("ACCESS", 1, "-pod_d / 2 + decor_d - dr_back_t + dr_pnl_gap"),
    ("FELT", 3, "dr_col_x0"), ("FELT", 5, "fg_vis_zt"), ("FELT", 4, "dr_acc_face_y + felt_t"),
    ("SEAL", 4, "-pod_d / 2 + decor_d - dr_back_t + dr_pnl_gap"), ("SEAL", 3, "ab_x + dr_seal_w / 2"),
    ("RISER", 2, "fg_vis_zb + dr_skin_t + ri_gap"), ("RISER", 5, "ri_zt"), ("RISER", 0, "ri_x0"),
    ("FBOX", 0, "fb_x0"), ("FBOX", 2, "fb_z0"), ("FBOX", 5, "fb_z0 + fb_h"),
    ("TUP", 5, "op_z0 + op_h"),
    # the frame's sides, each on a single tube that reaches it (every tube its own component, D-120)
    ("B06", 0, "((fg_dc + dr_skin_t - fg_dnz * (fg_vis_zt)) / fg_dnx)"), ("B02", 3, "pod_w / 2 - dr_skin_t"),
    ("F02", 1, "-pod_d / 2 + dr_skin_t"), ("B04", 4, "-pod_d / 2 + decor_d - dr_back_t"),
    ("F01", 2, "fg_vis_zb"), ("B03", 5, "pod_h - dr_skin_t"),
]

# what each tube's row says about its holes and fixings (the cuts in build(); none on the copies)
MEMBER_NOTES = {    # {n}: the inner face panel's rivnuts in that tube (D-130), counted from its screw line
    "B01": "40 x 20 x 1.5; {n} rivnuts 838003 for the inner face panel's screws (Z 130); J-FRONT-02: spigot hole 8.5 "
           "at X 1050 and slot 8.5 x 14 at X 1147 in its bottom wall, over BASE's support behind the mesh",
    "B02": "80 x 20 x 1.5; 6 holes 14 in its back wall round the J-FRONT-01 rivnut tails (X 1224); {n} rivnuts 838003 "
           "for the inner face panel's screws (X 1188)",
    "B05": "20 x 20 x 1.5; 2 rivnuts 838003 in its top for DT's spigots 831001 (J-FRONT-03, X 270 and 410) and {n} in "
           "its back wall for the inner face panel's screws (Z 2110)",
    "B06": "20 x 20 x 1.5; {n} rivnuts 838003 for the inner face panel's screws, on its middle",
    "B07": "20 x 20 x 1.5; {n} rivnuts 838003 for the inner face panel's screws, on its middle",
    "B08": "60 x 20 x 1.5; {n} rivnuts 838003 for the inner face panel's screws (Z 2140)",
    "F08": "20 x 20 x 1.5: carries the fan box's shelf",
    "F09": "20 x 20 x 1.0: holds the front skin across the top bay over the fan box, 1.72 mm under 100 N (5.01 without "
           "it; D-131 skin spans, PM ruling 2026-11-01); the fan box stands 5 behind it",
    "C03": "20 x 20 x 1.5: carries the fan box's shelf",
}


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
    tube_m = sum(FL.member_numbers(m, ev)["length"] for m in members) / 1000.0
    gt = "general tolerance ISO 2768-m"
    seal_m = sum(ev("dr_pe%d" % k) for k in range(len(PANEL_LINES))) / 1000.0
    n_screws = len(panel_screws())
    n_felt = len(felt_holes(ev))
    # one row per tube part (D-120, Control's numbers in #232): its copies counted in the quantity
    mparts = FL.member_parts(root_dir, FRAME_PN, MP.DR_MEMBERS)
    member_rows, seen = [], set()
    for m in members:
        pn, mname, mvn = mparts[m["key"]]
        if pn in seen:
            continue
        seen.add(pn)
        keys = [k for k in MP.DR_MEMBERS if MP.DR_MEMBERS[k] == pn]
        num = FL.member_numbers(m, ev)
        note = "member%s %s of the frame %s; %.1f long, ends: %s" % (
            "s" if len(keys) > 1 else "", ", ".join(keys), FRAME_PN, num["length"], m["ends"])
        if m["key"] in MEMBER_NOTES:
            note += "; " + MEMBER_NOTES[m["key"]].format(n=sum(1 for k, _p in panel_screws() if k == m["key"]))
        member_rows.append((pn, mname, mvn, len(keys), "made: tube cut to length, ends as its cut list row",
                            "aluminium EN AW-6063-T6 tube %s, finish: mill finish (hidden, D-79)" % m["section"], "cad",
                            "calculation (CAD, 2700 kg/m3, shelled)", "DRAFT", "number allocation (D-120, #232)", note))
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-49, D-59, D-60, D-79, D-87; PM rulings 2026-10-31 "
         "and 2026-11-01; this build", "skin bonded to the welded tube frame 351306; plates and panels on the frame"),
        ("351301", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1, bonded to "
         "the frame", "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 3.5 kg/m2: selection VT01)", "DRAFT",
         "D-12, D-49; skeleton DR shape", "one flat panel per outside face: " + DXF_SKIN_REL.split("/")[-1] +
         "; bond to the frame per the joints register's ACP bond spec"),
        (FRAME_PN, FRAME[1], FRAME[2], 1, "weldment assembly: welded frame, %d tubes as %d parts (parts list %s; cut list %s), TIG-welded" % (
            len(members), len(member_rows), WELD_BOM_REL.split("/")[-1], CUT_REL.split("/")[-1]),
         "aluminium EN AW-6063-T6 tube: 20 x 20 x 1.0 (skin only), 40, 60 and 80 x 20 x 1.2 (rivnuts), 20 x 20 x 1.5 "
         "(fan box shelf), finish: mill finish (hidden, D-79)", None, "", "DRAFT",
         "v1 decor frame drawing (front and back frames); D-79; joints register HOLD-10; D-120 (each tube its own "
         "part, #232)", "%.1f m of tube; welds per its weldment drawing; rivnuts 838003 fitted in the factory: %d for "
         "the inner face panel's screws, each with an 838004 stop washer on its head (D-130), and 2 for DT's spigots "
         "831001 (in the bottom, bolt-line, band, ledge, diagonal and glass-edge tubes)" % (tube_m, n_screws)),
    ] + member_rows + [
        ("351302", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made (laser-cut sheet, no drawing: D-89 part 4)",
         "aluminium EN AW-5754-H22 sheet 1.5 mm, finish: mill finish (hidden, D-79); " + gt, "cad",
         "calculation (CAD, 2700 kg/m3)", "DRAFT", "joints register J-FRONT-01 (1.0 to 2.7 at each bolt, HOLD-10); "
         "1.5 mm by PM ruling 2026-11-01 (DR under 20 kg)",
         "DXF " + DXF_FLAT["BACK"] + "; fixed: the strip on X +1224 with 6 holes 9.53 +0.10/0 for the rivnuts 838003 "
         "(critical: on the wall's bolt line), and the band behind the soffit; blind-riveted to the frame (HOLD: rivet)"),
        ("351305", PARTS["ACCESS"][1], PARTS["ACCESS"][2], 1, "made (laser-cut sheet; its drawing gives the "
         "flatness, about 0.5 mm, D-130), removable", "aluminium EN AW-5754-H22 sheet 3.0 mm, finish: mill finish "
         "(hidden, D-79); " + gt, "cad", "calculation (CAD, 2700 kg/m3)", "DRAFT",
         "D-60 air table; D-87; D-130 (one panel, its stops and seal; the opening 200 x 215 to the column's edge); "
         "PM rulings 2026-11-01 (the column's hook studs, the panel carries the 10 kg column)",
         "one removable inner face panel (D-130) over the opening the air unit goes in by: DXF " + DXF_FLAT["ACCESS"] +
         "; on stops 2.36 off the frame (an 838004 washer on each rivnut head), sealed all round by 848013, held by "
         "%d M6 x 16 socket heads 838001 (ISO 4762, the one 5 mm key on site), each on a plain washer 12 (ISO 7089; "
         "Joints numbers it), about 400 apart into rivnuts 838003 in the frame's tube walls (Joints' counts); the "
         "heads stand 7.6 proud of its room face and AIR clears the ones it covers (its supply cartridge lifted 6, "
         "reliefs at the soffit); the glass-edge tube's lowest screw stands 10 left of the air column's edge; 2 holes "
         "9.53 +0.10/0 at X 971, Z 1700 and 1850 for rivnuts 838003 with the column's 2 hook studs (J-AIR-02); its "
         "room-side face is AIR's named value dr_acc_face_y; ships loose with its screws and felt and goes on after "
         "the air unit; for service the column comes off, then the panel drops 40 and comes out under the soffit (PM "
         "rulings 2026-11-01)" % n_screws),
        ("351304", PARTS["FELT"][1], PARTS["FELT"][2], 1, "made (laser-cut PET felt sheet, no drawing: D-128, its DXF "
         "matches its STEP), glued to 351305 at the factory", "PET felt 9 mm, finish Dark Gray (D-79); outline +/-2, " + gt, "cad",
         "calculation (CAD, 1.8 kg/m2)",
         "DRAFT; emission certificate HOLD", "D-31; hardware selection A3",
         "DXF " + DXF_FLAT["FELT"] + "; %d closed holes %.0f over the panel's screw heads under it, at least %.0f of "
         "felt to its edge, each plugged with felt cut from the same sheet (PM rulings 2026-11-01: no bare socket "
         "heads on the room side)" % (n_felt, ev("dr_felt_hole"), ev("dr_felt_web"))),
        ("848013", PARTS["SEAL"][1], PARTS["SEAL"][2], 1, "bought by length",
         "very soft foam strip with PSA, 4.0 thick, about 8 wide (product HOLD-19)", 0.02,
         "assumption (soft foam, about 4 g/m)", "HOLD: product (HOLD-19)", "joints register H-34; D-130",
         "one loop on the frame's tubes round the inner face panel, %.2f m along its screw line, squeezed from 4.0 to "
         "2.36 on the panel's stops; cut round each of the %d stop washers when fitted (Joints)" % (seal_m, n_screws)),
        ("350004", AIR_ASSY[1], AIR_ASSY[2], 1, RESERVED_TYPE, "-", None,
         "not counted: AIR's supply fan box assembly 610401 (AIR #91)", RESERVED_STATUS, "D-87; PM ruling 2026-11-01",
         "the space AIR's supply fan box assembly takes (riser, transitions, fan box and its two fans), its own pallet "
         "piece; it slides into DR through its inner face and stands on the frame's shelf tube F08; its fan box "
         "stands 25 back from the front skin, behind the cross tube F09 (PM ruling 2026-11-01, D-131), so its base "
         "reaches forward onto F08 (AIR's detail)"),
        ("351402", PARTS["RISER"][1], PARTS["RISER"][2], 1, RESERVED_TYPE, "-", None,
         "not counted: AIR's intake riser 611501 (AIR #91)", RESERVED_STATUS, "D-60 air table; PM ruling 2026-11-01",
         "the space AIR's intake riser takes; its open foot stands 140 mm over the base opening"),
        ("351403", PARTS["TLOW"][1], PARTS["TLOW"][2], 1, RESERVED_TYPE, "-", None,
         "not counted: AIR's riser transition 618103 (AIR #91)", RESERVED_STATUS, "D-60 air table; PM ruling 2026-11-01",
         "the space AIR's riser transition takes, riser top to fan box inlet"),
        ("351404", PARTS["FBOX"][1], PARTS["FBOX"][2], 1, RESERVED_TYPE, "-", None,
         "not counted: AIR's supply fan box 610401 (AIR #91)", RESERVED_STATUS, "D-60 air table; PM ruling 2026-11-01",
         "the space AIR's supply fan box takes; 12 from the fixed glass channel, so the frame's inner-edge tube fits; "
         "its front 5 behind the cross tube F09 (Y -822; PM ruling 2026-11-01, D-131)"),
        ("351405", PARTS["TUP"][1], PARTS["TUP"][2], 1, RESERVED_TYPE, "-", None,
         "not counted: AIR's supply transition 618102 (AIR #91)", RESERVED_STATUS, "D-60 air table; PM ruling 2026-11-01",
         "the space AIR's supply transition takes, fan box outlet to the access panel's opening"),
    ]
    total, weld_total = FL.write_weldment_lists(L, design, root_dir, rows, FRAME_PN, member_rows, WELD_BOM_REL, BOM_REL,
                                                (PN, NAME, VN))
    print("parts list %s: %d parts, %.2f kg" % (WELD_BOM_REL, len(member_rows), weld_total))
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
        w.writerow(["frame", "member", "member_part", "name", "section", "length_mm", "qty", "ends", "status"])
        w.writerows(tuple(r[:2]) + (mparts[r[1]][0],) + tuple(r[2:]) for r in FL.cut_list_rows(members, ev, FRAME_PN))
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
            {"component": cad_name(k) if k in PARTS else "%s %s" % mparts[k][:2], "index": i, "expression": e}
            for k, i, e in ANCHORS]},
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
