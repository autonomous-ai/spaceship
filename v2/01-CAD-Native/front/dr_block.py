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

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"      # DR's front face and back face (Y -850, -645)
GY = "-glass_y"
ZB, ZT = "fg_vis_zb", "fg_vis_zt"                  # band top and DT's underside

OWN = [
    ("dr_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dr_back_t", "3 mm", "mm", "assumption", "back plate and inner panel in the same 3 mm ACP"),
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
    ("ri_gap", "60 mm", "mm", "assumption",
     "the riser's open foot stands 60 mm over DR's open base, so the air rises straight into it; it also clears the "
     "fixed glass channel by 2.8 mm (the channel reaches X 956 at Z 153)"),
    ("slot_clear", "1 mm", "mm", "assumption", "fitting clearance each side of the glass channel in DR's skin slot"),
    ("ri_t", "1 mm", "mm", "source", "D-60 air table: 1 mm galvanised steel"),
    # supply fan box (D-60 air table)
    ("fb_w", "300 mm", "mm", "source", "D-60 air table: fan box 300 x 155 x 300"),
    ("fb_y0", "-847 mm", "mm", "source", "D-60 air table: fan box Y -847 to -692"),
    ("fb_d", "155 mm", "mm", "source", "D-60 air table"),
    ("fb_z0", "1650 mm", "mm", "source", "D-60 air table: fan box Z 1650 to 1950"),
    ("fb_clear", "5 mm", "mm", "assumption", "clearance from the fan box to the fixed glass's hidden channel"),
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
]

PARTS = {
    "SKIN": ("351301", "FRONT - DECOR SKIN - DR", "Tấm ốp alu khối phải"),
    "BACK": ("351302", "FRONT - DECOR BACK PLATE - DR", "Tấm hậu khối phải"),
    "INNER": ("351303", "FRONT - DECOR INNER PANEL - DR", "Tấm trong tháo được khối phải"),
    "FELT": ("351304", "FRONT - DECOR INNER PANEL FELT - DR", "Nỉ tấm trong khối phải"),
    "RISER": ("351402", "FRONT - AIR INTAKE RISER - DR", "Ống gió đứng khối phải"),
    "TLOW": ("351403", "FRONT - AIR TRANSITION - LOWER - DR", "Ống chuyển hướng dưới"),
    "FBOX": ("351404", "FRONT - SUPPLY FAN BOX - DR", "Hộp quạt cấp"),
    "TUP": ("351405", "FRONT - AIR TRANSITION - UPPER - DR", "Ống chuyển hướng trên"),
    "FAN1": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM - 1", "Quạt 12 V"),
    "FAN2": ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM - 2", "Quạt 12 V"),
}

# Overlaps made on purpose, with the reason; any other clash over 1 mm3 fails the build.
EXPECTED = [
    (("TLOW", "RISER"), "the lower transition space starts inside the riser's top end, where they join"),
    (("TLOW", "FBOX"), "the lower transition space meets the fan box inlet"),
    (("TUP", "FBOX"), "the upper transition space meets the fan box outlet"),
    (("TUP", "TUP2"), "two halves of one duct space"),
]


def build(app):
    design = L.start_design(app, PN, "%s | %s | %s" % (NAME, VN, REV))
    sk_params, sk_path, sk_rev = L.load_skeleton_params(ARGS["repo_root"])
    L.add_params(design, sk_params)
    L.add_params(design, L.LIB_PARAMS)
    L.add_params(design, L.GLASS_PARAMS)
    L.add_params(design, OWN)
    root = design.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    comps, bodies = {}, {}

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(root, pn, nm, vn, REV)
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

    # ---- 351302 fixed back plate: behind the air column, the side wall and the soffit
    c = comp("BACK")
    # its lower-left corner follows the inner-edge skin (the glass line pushed in by dr_skin_t) below the point
    # where that line crosses the column face, so the plate never cuts into the skin
    tip_z = "((fg_rc + dr_skin_t - fg_rnx * dr_col_x0) / fg_rnz)"
    zs = ZB + " + dr_skin_t"
    back = [(L.right_x(zs, "dr_skin_t"), zs), (XR + " - dr_skin_t", zs),
            (XR + " - dr_skin_t", "pod_h - dr_skin_t"), (XL + " + dt_xr", "pod_h - dr_skin_t"),
            (XL + " + dt_xr", ZT), ("dr_col_x0", ZT), ("dr_col_x0", tip_z)]
    f = prism(c, ("x", "z"), back, "y", YB + " - dr_back_t", YB, "OUTLINE - DR BACK PLATE", "EXTRUDE - DR BACK PLATE")
    bp = f.bodies.item(0)
    prism(c, ("x", "z"), [("op_x0", "op_z0"), ("op_x0 + op_w", "op_z0"), ("op_x0 + op_w", "op_z0 + op_h"),
                          ("op_x0", "op_z0 + op_h")], "y", YB + " - dr_back_t - 1 mm", YB + " + 1 mm",
          "OPENING - INTO THE AIR COLUMN TOP", "CUT - OPENING INTO THE AIR COLUMN", CUT, bp)
    bp.name = "DR BACK PLATE ACP 3"
    bodies["BACK"] = bp

    # ---- 351303 removable inner panel and 351304 its felt: the part of the back face seen from inside
    inner = [("dr_col_x0", tip_z), ("dr_col_x0", ZT), (L.diag_x(ZT, "dr_skin_t"), ZT), L.g_K("dr_skin_t")]
    c = comp("INNER")
    f = prism(c, ("x", "z"), inner, "y", YB + " - dr_back_t", YB, "OUTLINE - DR INNER PANEL (SEEN FROM INSIDE)",
              "EXTRUDE - DR INNER PANEL")
    bodies["INNER"] = f.bodies.item(0)
    bodies["INNER"].name = "DR INNER PANEL ACP 3"
    c = comp("FELT")
    f = prism(c, ("x", "z"), inner, "y", YB, YB + " + felt_t", "OUTLINE - DR INNER PANEL FELT", "EXTRUDE - FELT 9")
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

    # ---- materials
    acp = L.material(design, "ACP 3 mm PE core EV3038 (1300 kg/m3, calculation)", "Aluminum", 1300.0)
    felt = L.material(design, "PET felt 9 mm (200 kg/m3, calculation: 1.8 kg/m2)", "Aluminum", 200.0)
    steel = L.material(design, "Galvanised steel (7850 kg/m3)", "Steel", 7850.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    for k, m in (("SKIN", acp), ("BACK", acp), ("INNER", acp), ("FELT", felt), ("RISER", steel),
                 ("TLOW", env), ("FBOX", alu), ("TUP", env), ("TUP2", env), ("FAN1", env), ("FAN2", env)):
        bodies[k].material = m
    looks = {"SKIN": ["Paint - Enamel Glossy (Yellow)"], "BACK": ["Paint - Enamel Glossy (Yellow)"],
             "INNER": ["Paint - Enamel Glossy (Yellow)"], "FELT": ["Fabric (Gray)", "Plastic - Matte (Grey)"],
             "RISER": ["Steel - Satin", "Paint - Enamel Glossy (Grey)"],
             "FBOX": ["Aluminum - Satin"], "FAN1": ["Plastic - Matte (Black)"], "FAN2": ["Plastic - Matte (Black)"],
             "TLOW": ["Paint - Enamel Glossy (Red)"], "TUP": ["Paint - Enamel Glossy (Red)"],
             "TUP2": ["Paint - Enamel Glossy (Red)"]}
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
    print("base opening over the band piece: %.4f m2 (profile area)" % (sk_in.profiles.item(0).areaProperties().area / 1e4))
    print("DR box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DR checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))


ANCHORS = [
    ("SKIN", 0, "fix_xtr - pod_w / 2"), ("SKIN", 3, "pod_w / 2"), ("SKIN", 2, "fg_vis_zb"), ("SKIN", 5, "pod_h"),
    ("SKIN", 1, "-pod_d / 2"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 0, "dt_xr - pod_w / 2"), ("BACK", 3, "pod_w / 2 - dr_skin_t"), ("BACK", 5, "pod_h - dr_skin_t"),
    ("INNER", 3, "dr_col_x0"), ("INNER", 5, "fg_vis_zt"), ("FELT", 4, "-pod_d / 2 + decor_d + felt_t"),
    ("RISER", 2, "fg_vis_zb + dr_skin_t + ri_gap"), ("RISER", 5, "ri_zt"), ("RISER", 0, "ri_x0"),
    ("FBOX", 0, "fb_x0"), ("FBOX", 2, "fb_z0"), ("FBOX", 5, "fb_z0 + fb_h"),
    ("TUP", 5, "op_z0 + op_h"),
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
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-49, D-59, D-60; PM rulings 2026-10-31; this build",
         "stage 1: no frame yet (stage 2)"),
        ("351301", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1",
         "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 1300 kg/m3)", "DRAFT",
         "D-12, D-49; skeleton DR shape", "panel split and flat patterns: stage 2"),
        ("351302", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made", "ACP 3 mm", "cad", "calculation (CAD)", "DRAFT",
         "D-60 air table (opening 203 x 215)", "behind the air column, the side wall and the soffit"),
        ("351303", PARTS["INNER"][1], PARTS["INNER"][2], 1, "made, removable", "ACP 3 mm", "cad", "calculation (CAD)",
         "DRAFT", "D-59, D-60", "lifts off for the fan box; fixings stage 2"),
        ("351304", PARTS["FELT"][1], PARTS["FELT"][2], 1, "made (cut from felt sheet), bonded to 351303",
         "9 mm PET felt, Dark Gray", "cad", "calculation (CAD, 1.8 kg/m2)", "DRAFT; emission certificate HOLD",
         "D-31; hardware selection A3", ""),
        ("351402", PARTS["RISER"][1], PARTS["RISER"][2], 1, "made (sheet metal duct)", "1 mm galvanised steel", "cad",
         "calculation (CAD, 7850 kg/m3)", "DRAFT", "D-60 air table", "open foot 45 mm over the base opening; mounts stage 2"),
        ("351403", PARTS["TLOW"][1], PARTS["TLOW"][2], 1, "reserved duct space", "-", 1.5, "assumption",
         "HOLD: the Air Engineer's transition detail", "D-60 air table", ""),
        ("351404", PARTS["FBOX"][1], PARTS["FBOX"][2], 1, "made", "2 mm aluminium, 50 mm lining inside", 5.1,
         "source (D-60 air table, box and transition)", "DRAFT; lining and bulkhead HOLD (air detail)",
         "D-60 air table", "mounts stage 2"),
        ("351405", PARTS["TUP"][1], PARTS["TUP"][2], 1, "reserved duct space", "-", 0.0, "included in 351404's 5.1 kg",
         "HOLD: the Air Engineer's transition detail", "D-60 air table", ""),
        ("618401", "AIR - FAN - NOCTUA NF-A14 INDUSTRIALPPC-3000 PWM", "Quạt 12 V", 2, "bought",
         "Noctua NF-A14 industrialPPC-3000 PWM, 12 V", 0.3, "assumption (D-60 air table)", "HOLD: product (PM ruling, one number for all four fans)",
         "hardware selection F1", "on the fan box bulkhead, blowing up"),
    ]
    total = L.write_parts_list(design, os.path.join(root_dir, BOM_REL), rows, PN, NAME, VN)
    print("parts list %s: %d rows, unit mass %.2f kg" % (BOM_REL, len(rows), total))
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as fh:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % (PARTS[k][0], PARTS[k][1]), "index": i, "expression": e} for k, i, e in ANCHORS]},
            fh, indent=1, ensure_ascii=False)
    print("anchors %s: %d" % (ANCHORS_REL, len(ANCHORS)))
    before, after, diff = L.step_reread(app, doc, design, step)
    print("STEP re-read in Fusion: model box %s, STEP box %s, max diff %.3f mm" % (before, after, diff))


def run(_context):
    app = adsk.core.Application.get()
    step = ARGS.get("step", "build")
    doc = app.activeDocument
    if doc is None or not doc.name.startswith(DOC_NAME):
        raise RuntimeError("active document is %r, not %s: open it with the runner's --doc" % (
            doc.name if doc else None, DOC_NAME))
    if step == "build":
        build(app)
    elif step == "export":
        export_all(app)
    else:
        raise RuntimeError("unknown step " + step)
