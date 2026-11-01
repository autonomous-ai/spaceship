"""350002 FRONT - DECOR BLOCK ASSY - DT (Khối trang trí trên): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dt_block.py \
        --doc 350002_P01_FRONT-DECOR-BLOCK-ASSY-DT_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dt_block.py \
        --doc 350002_P01_FRONT-DECOR-BLOCK-ASSY-DT_CAD --arg step=export --close

Stage 1 of the top decor block:
- the outer shape: the skeleton's DT (plan with v1's lower facet and the joint to DR along v1's line to X 449, its
  bottom slope over DL, the top chamfer), from DT's underside (dt_zb) to the roof;
- 351201 the 3 mm ACP skin, by shelling that shape, left open at the back (back plate) and where DT meets DR and DL;
- 351202 the back plate (ACP, behind it the soffit, D-60);
- the slot in the underside where the fixed pane's top channel enters (PM ruling 2026-10-31);
- 368007 the magnetic door-stop catch (Sugatsune HT-MSG62, 35 N), hanging from the underside behind the door's top
  latch corner, where the door's strike meets it (PM ruling: no latch on the glass; 6 mm gap, the catch's 5 to 10);
- 351203 the door's top stop under DT and 368005 the frame-stop seal (athmer PS 1515 P Flex) on it, sealing on the
  leaf's inner face along its top, short of the catch.
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
PN = "350002"
NAME = "FRONT - DECOR BLOCK ASSY - DT"
VN = "Khối trang trí trên (cụm)"
DOC_NAME = "%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_BOM.csv" % (PN, REV)
DXF_SKIN_REL = "v2/03-Manufacturing/front/351201_%s_FRONT-DECOR-SKIN-DT_DXF.dxf" % REV
CUT_REL = "v2/03-Manufacturing/front/351204_%s_FRONT-DECOR-FRAME-DT-TUBE-CUT-LIST.csv" % REV
DXF_BACK_REL = "v2/03-Manufacturing/front/351202_%s_FRONT-DECOR-BACK-PLATE-DT_DXF.dxf" % REV
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_ANCHORS.json" % (PN, REV)

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"
GY = "-glass_y"
ZT = "fg_vis_zt"                   # DT's underside = dt_zb
YBP = "(%s - dt_stop_gap)" % YB    # the back plate's back face, 2.26 in front of the ceiling (J-FRONT-03)


def jf3_x(i):
    """X of the i-th of the 4 J-FRONT-03 bolts (register 2.9: 220 in from each end of DT's edge, even between)."""
    return "(jf3_x0 + jf3_e + %d * (%s + dt_xr - jf3_x0 - 2 * jf3_e) / 3)" % (i, XL)


def latch_x(z):
    return "(%s + door_xbr - (door_xbr - door_xtr) * ((%s) - door_zb) / (door_zt - door_zb))" % (XL, z)


CATCH_X = "(%s - st_end - st_l / 2)" % latch_x("leaf_zt")      # the catch's centre, over the strike's centre


OWN = [
    ("dt_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dt_back_t", "2 mm", "mm", "confirmed",
     "back plate 2 mm aluminium: J-FRONT-03 puts the ceiling bolts' rivnuts in it, 1.0 to 2.7 thick at each bolt "
     "(HOLD-10: 2 mm; PM ruling 2026-11-01)"),
    # ---- J-FRONT-03 (joints register; PM ruling 2026-11-01): DT's back plate bolted to the ceiling's front tubes
    ("dt_stop_gap", "2.26 mm", "mm", "source",
     "J-FRONT-03: DT's back plate stands 2.26 in front of the ceiling's front face (Y -645), the stopped seam's gap "
     "(rivnut head 0.76 on a 1.5 stop washer, R-J5)"),
    ("jf3_x0", "-1201.74 mm", "mm", "source", "joints register 2.9: DT's bolt line starts at C1's frame end, X -1201.74"),
    ("jf3_e", "220 mm", "mm", "source", "R-J13: the end bolts 220 in from each end of the edge"),
    ("jf3_z", "2374 mm", "mm", "source", "R-J15: the bolt line on the ceiling's front tube centre, Z 2374"),
    ("jf3_hole", "9.53 mm", "mm", "source", "rivnut 838003 hole 9.53 +0.10/0 (joints register H-03)"),
    ("jf3_tail", "14 mm", "mm", "calculation",
     "holes in the top back tube's back wall round the rivnut tails and the bolt tips, as J-FRONT-01's"),
    ("fr_wtop", "40 mm", "mm", "confirmed",
     "the back ring's top tube 40 x 20, so the J-FRONT-03 rivnut tails at Z 2374 go into it (PM ruling 2026-11-01)"),
    # DT's two locating spigots stand on DR's ledge (J-FRONT-03; PM ruling 2026-11-01): a round hole and a slot
    # along X, 140 apart, in DT's bottom back tube; clearance in the skin for the rivnut heads
    ("sp_x1", "-pod_w / 2 + dt_xr - 179 mm", "mm", "confirmed",
     "the round spigot hole, X 270: 36 in from the left end of DR's ledge tube (X 234 to 449)"),
    ("sp_dx", "140 mm", "mm", "confirmed", "the slot 140 from the round hole (PM ruling 2026-11-01)"),
    ("sp_y", "-pod_d / 2 + decor_d - 12.88 mm", "mm", "calculation",
     "the spigots' Y, -657.88: the middle of where DR's ledge tube (Y -666.5 to -646.5) and DT's bottom back tube "
     "overlap"),
    ("sp_hole", "8.5 mm", "mm", "source", "R-J13: spigot hole 8.5 round at one end, 8.5 x 14 slot at the other"),
    ("sp_slot", "14 mm", "mm", "source", "R-J13: the slot 14 long along the edge"),
    ("sp_skin", "16 mm", "mm", "calculation",
     "the underside's notch over DR's ledge reaches this far past each spigot, clear of the rivnut heads (12.96)"),
    ("stop_fl", "20 mm", "mm", "source",
     "the top stop's flange under DT's underside (the 20 x 20 x 2 angle), screwed up into the rail F02"),
    ("stop_hole", "4.3 mm", "mm", "source",
     "ISO 273 fine clearance for M4 countersunk screws through the flange, 2.1 diameters from its free edge "
     "(screw and rivnut: joints register numbers HOLD)"),
    ("dt_m", "(dl_zo - dt_zb) / dl_w", "", "calculation", "rise of the slope DT shares with DL, per unit of X"),
    ("dt_k", "sqrt(1 + dt_m * dt_m)", "", "calculation", "for pushing the slope line in by the skin"),
    ("slot_clear", "1 mm", "mm", "assumption", "fitting clearance each side of the glass channel in the skin slot"),
    # the door's top: the leaf 2 mm short of the skeleton top for the catch's 6 mm gap (PM ruling)
    ("door_top_cut", "2 mm", "mm", "decided", "PM ruling 2026-10-31: 6 mm gap from the leaf to DT for the catch"),
    ("leaf_zt", "door_zt - door_top_cut", "mm", "calculation", "top of the door leaf"),
    # the strike on the leaf (door unit): HT-MSG62-U10, 62 long, A 14.1, its latch-side end st_end from the corner
    ("st_l", "62 mm", "mm", "source", "Sugatsune HT-MSG62 strike plate, 62 long (datasheet D2, Dec 2020)"),
    ("st_a", "14.1 mm", "mm", "source", "strike HT-MSG62-U10, A = 14.1"),
    ("st_end", "25 mm", "mm", "assumption", "as the door unit: the strike's end in from the leaf's top latch corner"),
    # the catch body under DT (datasheet sizes): 62 long, 20 deep, hangs 26 below its mounting face
    ("ca_l", "62 mm", "mm", "source", "Sugatsune HT-MSG62 catch, 62 long (datasheet)"),
    ("ca_d", "20 mm", "mm", "source", "catch body depth 20 (datasheet)"),
    ("ca_h", "26 mm", "mm", "source", "catch body with its bracket, 26 below the frame (datasheet)"),
    # the door's top stop and its seal
    ("stop_gap", "4 mm", "mm", "source", "athmer PS 1515 P Flex works in a 2 to 6 mm frame gap (selection C3): 4 nominal"),
    ("ps_s", "15 mm", "mm", "source", "athmer PS 1515 P Flex, 15 x 15 (selection C3)"),
    ("stop_t", "2 mm", "mm", "assumption", "top stop: an aluminium angle leg 2 thick"),
    ("stop_h", "20 mm", "mm", "source",
     "top stop: a standard 20 x 20 x 2 aluminium angle (EN 755-9); its leg hangs 20 below DT's underside, past the seal"),
    ("stop_end", "10 mm", "mm", "assumption", "the seal and stop stop 10 short of the catch"),
    # ---- the tube frame (stage 2): v1's front and back frames of 16 mm steel box (sources/v1 decor frame drawing),
    # in 6063-T6 aluminium tube (D-79), as DR's
    ("fr_w", "20 mm", "mm", "calculation",
     "frame tube 20 x 20 x 1.5, 6063-T6 (D-79): bending stiffness about v1's 16 x 16 x 1 steel box, as DR"),
    ("fr_t", "1.5 mm", "mm", "calculation", "frame tube wall, as fr_w"),
    ("rail_clear", "-pod_d / 2 + decor_d - dt_stop_gap - dt_back_t - 2 * fr_w - (-glass_y + gu_prof_w / 2)", "mm",
     "calculation",
     "the catch and stop rail sits against the back ring's bottom tube, so it stands 2.24 behind the fixed glass's "
     "top channel (its back face at Y -691.5); J-FRONT-03 moved the back ring 1.26 forward"),
    # the lower front facet and the top chamfer as lines, for the frame
    ("dt_fdx", "fix_xtr - dt_x2", "mm", "calculation", "lower front facet in plan, along X"),
    ("dt_fdy", "pod_d / 2 - dt_y2", "mm", "calculation", "lower front facet in plan, along Y"),
    ("dt_fl", "sqrt(dt_fdx * dt_fdx + dt_fdy * dt_fdy)", "mm", "calculation", "lower front facet length in plan"),
    ("dt_fnx", "dt_fdy / dt_fl", "", "calculation", "lower front facet normal into DT, X"),
    ("dt_fny", "dt_fdx / dt_fl", "", "calculation", "lower front facet normal into DT, Y"),
    ("dt_fc", "dt_fnx * (-pod_w / 2 + fix_xtr) + dt_fny * (-pod_d / 2)", "mm", "calculation", "lower front facet constant"),
    ("dt_cl", "sqrt((pod_d / 2 - ch_yb) * (pod_d / 2 - ch_yb) + (pod_h - ch_zlo) * (pod_h - ch_zlo))", "mm",
     "calculation", "length of the top chamfer in the side view"),
    ("dt_cny", "-(pod_h - ch_zlo) / dt_cl", "", "calculation", "top chamfer outward normal, Y"),
    ("dt_cnz", "(pod_d / 2 - ch_yb) / dt_cl", "", "calculation", "top chamfer outward normal, Z"),
    ("dt_cc", "dt_cny * (-pod_d / 2) + dt_cnz * ch_zlo", "mm", "calculation", "top chamfer line constant"),
    ("dt_jl", "sqrt((dt_xr - fix_xtr) * (dt_xr - fix_xtr) + (pod_d / 2 - ch_yb) * (pod_d / 2 - ch_yb))", "mm",
     "calculation", "length of the DT-DR joint line in plan (v1's line to X 449)"),
    ("dt_jnx", "-(pod_d / 2 - ch_yb) / dt_jl", "", "calculation", "DT-DR joint normal into DT, X"),
    ("dt_jny", "(dt_xr - fix_xtr) / dt_jl", "", "calculation", "DT-DR joint normal into DT, Y"),
    ("dt_jc", "dt_jnx * (-pod_w / 2 + fix_xtr) + dt_jny * (-pod_d / 2)", "mm", "calculation", "DT-DR joint constant"),
]

PARTS = {
    "SKIN": ("351201", "FRONT - DECOR SKIN - DT", "Tấm ốp alu khối trên"),
    "BACK": ("351202", "FRONT - DECOR BACK PLATE - DT", "Tấm hậu khối trên"),
    "STOP": ("351203", "FRONT - DOOR TOP STOP - DT", "Nẹp chặn cửa trên"),
    "PS": ("368005", "FRONT - FRAME-STOP SEAL", "Gioăng chặn cửa trên"),
    "CATCH": ("368007", "FRONT - DOOR CATCH - IN DT", "Nam châm hít cửa"),
    "FRAME": ("351204", "FRONT - DECOR FRAME - DT", "Khung trang trí trên (hàn)"),
}

EXPECTED = []
FRAME_PN = "351204"
S20 = "20 x 20 x 1.5"
S40 = "40 x 20 x 1.5"          # the back ring's top tube B03 (fr_wtop 40): the J-FRONT-03 rivnut tails go into it


def frame_members():
    """DT's welded tube frame as data (as DR's): a back ring just in front of the back plate, a tube along the lower
    front facet, a tube under the top chamfer, the rail over the door's catch and top stop, and cross tubes."""
    yb0, yb1 = "(%s - dt_back_t - fr_w)" % YBP, "(%s - dt_back_t)" % YBP
    zb3 = "(%s + dt_skin_t)" % ZT
    bot, top = FL.line(0, 1, ZT), FL.line(0, -1, "-pod_h")
    right = FL.line(-1, 0, "-(%s + dt_xr)" % XL)
    # DT stands on the slope over DL: z - dt_zb = dt_m (XL + dl_w - x); pushed 3 in, the joint's seal gap (HOLD)
    slope = FL.line("dt_m / dt_k", "1 / dt_k", "(dt_zb + dt_m * (%s + dl_w)) / dt_k" % XL)
    M = []

    def add(key, name, axes, pts, along, a, b, axis=(0, 1), ends=None, lengthwise=False):
        M.append({"key": key, "name": name, "axes": axes, "pts": pts, "along": along, "a": a, "b": b,
                  "section": S40 if key == "B03" else S20, "axis": axis, "lengthwise": lengthwise,
                  "ends": ends or "mitred to its neighbours (angles on the frame drawing)"})

    back = FL.ring([(bot, "dt_skin_t", "fr_w"), (right, "0 mm", "fr_w"), (top, "dt_skin_t", "fr_wtop"),
                    (slope, "dt_skin_t", "fr_w")])
    for k, (key, nm) in enumerate((("B01", "BACK RING BOTTOM"), ("B02", "BACK RING DR JOINT"), ("B03", "BACK RING TOP"),
                                   ("B04", "BACK RING SLOPE OVER DL"))):
        add(key, nm, ("x", "z"), back[k], "y", yb0, yb1)
    # a post in the middle of the back ring, as v1
    xm = "((%s + dl_w + %s + dt_xr) / 2 - fr_w / 2)" % (XL, XL)
    add("B05", "BACK RING POST", ("x", "z"), [(xm, "%s + fr_w" % zb3), ("%s + fr_w" % xm, "%s + fr_w" % zb3),
                                             ("%s + fr_w" % xm, "pod_h - dt_skin_t - fr_wtop"), (xm, "pod_h - dt_skin_t - fr_wtop")],
        "y", yb0, yb1, axis=(1, 2), ends="square both ends")
    # along the lower front facet (plan), on the underside skin
    fac = FL.line("dt_fnx", "dt_fny", "dt_fc")
    f3, f23 = FL.push(fac, "dt_skin_t"), FL.push(fac, "dt_skin_t + fr_w")
    joint = FL.line("dt_jnx", "dt_jny", "dt_jc")
    xl_bot = "(%s + dl_w - (dt_skin_t - dt_skin_t * dt_k) / dt_m)" % XL     # the pushed slope at the underside skin
    left = FL.line(1, 0, "(%s + dt_x2)" % XL)                       # starts at the facet's corner
    add("F01", "FRONT FACET TUBE", ("x", "y"), [FL.meet(f3, left), FL.meet(f3, joint), FL.meet(f23, joint),
                                                FL.meet(f23, left)], "z", zb3, "%s + fr_w" % zb3,
        ends="left end square, right end cut to the DR joint line")
    # the rail the catch 368007 and the top stop 351203 screw into, just behind the glass's top channel
    yr0 = "(%s + gu_prof_w / 2 + rail_clear)" % GY
    yr1 = "(%s + fr_w)" % yr0
    xdt = "(%s + dt_xr)" % XL
    add("F02", "CATCH AND STOP RAIL", ("x", "y"), [(xl_bot, yr0), FL.meet(joint, FL.line(0, 1, yr0)),
                                                    FL.meet(joint, FL.line(1, 0, xdt)), (xdt, yr1), (xl_bot, yr1)],
        "z", zb3, "%s + fr_w" % zb3, ends="left end square, right end cut to the DR joint line")
    # under the top chamfer, along X (side view: a square laid on the chamfer)
    chl = FL.line("-dt_cny", "-dt_cnz", "-dt_cc")
    c3, c23 = FL.push(chl, "dt_skin_t"), FL.push(chl, "dt_skin_t + fr_w")
    yf_in = "(-dt_y2 + dt_skin_t / dt_fny)"                       # the facet's inside face at its left end
    pf = FL.meet(c3, FL.line(1, 0, yf_in))                         # its top front corner, the most forward point
    t0 = FL.line("dt_cnz", "-dt_cny", "dt_cnz * %s - dt_cny * %s" % pf)
    t1 = FL.push(t0, "fr_w")
    sq = [FL.meet(c3, t0), FL.meet(c3, t1), FL.meet(c23, t1), FL.meet(c23, t0)]
    x_ch1 = "((dt_jc - dt_jny * %s) / dt_jnx)" % yf_in             # the joint line at the tube's front
    add("F03", "CHAMFER TUBE ALONG X", ("y", "z"), sq, "x", "(%s + dt_x2)" % XL, x_ch1, lengthwise=True,
        ends="left end square at the facet corner, right end square short of the DR joint")
    # cross tubes: on the underside from the facet tube to the rail (one over the catch), and under the chamfer
    # from the chamfer tube to the back ring's top
    for key, nm, x0 in (("R01", "UNDERSIDE CROSS TUBE LEFT", "(%s + dt_x2 + 280 mm)" % XL),
                        ("R02", "UNDERSIDE CROSS TUBE OVER THE CATCH", "(%s - fr_w / 2)" % CATCH_X)):
        x1 = "(%s + fr_w)" % x0
        add(key, nm, ("x", "y"), [FL.meet(f23, FL.line(1, 0, x0)), FL.meet(f23, FL.line(1, 0, x1)), (x1, yr0), (x0, yr0)],
            "z", zb3, "%s + fr_w" % zb3, axis=(1, 2), ends="front end cut to the facet tube, back end square to the rail")
    ch_pts = [FL.meet(c3, t1), FL.meet(c3, FL.line(0, 1, "pod_h - dt_skin_t")), (yb0, "pod_h - dt_skin_t"),
              FL.meet(c23, FL.line(1, 0, yb0)), FL.meet(c23, t1)]
    for key, nm, x0 in (("C01", "CHAMFER CROSS TUBE LEFT", "(%s + dt_x2 + 280 mm)" % XL),
                        ("C02", "CHAMFER CROSS TUBE MIDDLE", "(%s - fr_w / 2)" % CATCH_X),
                        ("C03", "CHAMFER CROSS TUBE RIGHT", "(%s - 2 * fr_w)" % x_ch1)):
        add(key, nm, ("y", "z"), ch_pts, "x", x0, "%s + fr_w" % x0,
            ends="front end square to the chamfer tube, back end square to the back ring's top")
    return M



# part-only designs for the part drawings (a base view shows its whole design): the full block is built and checked,
# then every other component is removed
SCOPES = {"assy": None, "frame": "FRAME", "skin": "SKIN", "stop": "STOP"}


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

    # ---- 351201 skin: the skeleton's DT shape, shelled
    c = comp("SKIN")
    plan = [(XL, YBP), (XL, "-dl_y1"), (XL + " + dl_x2 + 4 mm", "-dt_y3"), (XL + " + dt_x2", "-dt_y2"),
            (XL + " + fix_xtr", YF), (XL + " + dt_xr", "-ch_yb"), (XL + " + dt_xr", YBP)]
    f = prism(c, ("x", "y"), plan, "z", "dt_zb", "pod_h", "PLAN - DT FACETS (SKELETON)", "EXTRUDE - DT OUTER SHAPE")
    skin = f.bodies.item(0)
    prism(c, ("x", "z"), [(XL, "dt_zb"), (XL + " + dl_w", "dt_zb"), (XL, "dl_zo")], "y", YF, YB,
          "SLOPE - DT BOTTOM OVER DL", "CUT - DT BOTTOM SLOPE", CUT, skin)
    prism(c, ("y", "z"), [(YF, "ch_zlo"), ("-ch_yb", "pod_h"), (YF, "pod_h")], "x", XL, XR,
          "CHAMFER - DT TOP FRONT", "CUT - DT TOP CHAMFER", CUT, skin)
    yb, xj = L.ev(design, YBP), L.ev(design, XL + " + dt_xr")
    open_faces, kinds = adsk.core.ObjectCollection.create(), []
    for fc in skin.faces:
        p = fc.pointOnFace
        _ok, n = fc.evaluator.getNormalAtPoint(p)
        px, py = p.x * 10, p.y * 10
        if abs(n.y - 1) < 1e-6 and abs(py - yb) < 0.05:
            kinds.append("back")
        elif abs(n.z) < 1e-6 and n.x > 0.5:
            kinds.append("DR joint")            # DT's right end: the face on v1's line and the face at X 449
        elif n.z < -0.2 and n.x < -0.2:
            kinds.append("DL joint")            # the slope DT sits on over DL
        else:
            continue
        open_faces.add(fc)
    if sorted(kinds) != ["DL joint", "DR joint", "DR joint", "back"]:
        raise RuntimeError("faces to leave open: found %s" % kinds)
    si = c.features.shellFeatures.createInput(open_faces, False)
    si.insideThickness = L.vi("dt_skin_t")
    c.features.shellFeatures.add(si).name = "SHELL - DT SKIN 3 MM (OPEN AT THE BACK AND AT DL, DR)"
    # slot in the underside for the fixed pane's top channel, from the pane's free edge to DR
    # its left end where the pane's free edge leaves the skin's top face: the edge leans left going up, so at the
    # skin's bottom face the slot would leave a 0.6 mm sliver of the pane's corner in the skin (FRONT combined check)
    zs1 = ZT + " + dt_skin_t + 1 mm"
    slot = [(L.free_x(zs1), GY + " - gu_prof_w / 2 - slot_clear"),
            (L.diag_x(ZT, "gu_prof_d"), GY + " - gu_prof_w / 2 - slot_clear"),
            (L.diag_x(ZT, "gu_prof_d"), GY + " + gu_prof_w / 2 + slot_clear"),
            (L.free_x(zs1), GY + " + gu_prof_w / 2 + slot_clear")]
    prism(c, ("x", "y"), slot, "z", ZT + " - 1 mm", ZT + " + dt_skin_t + 1 mm",
          "SLOT - FIXED GLASS TOP CHANNEL", "CUT - SKIN SLOT FOR THE TOP CHANNEL", CUT, skin)
    # J-FRONT-03: the underside is notched open to its back edge over DR's ledge, round both spigots and their rivnut
    # heads (a hole there would sit 10 from the edge); hidden where DT sits on DR
    nx0, nx1 = "(sp_x1 - sp_skin)", "(sp_x1 + sp_dx + (sp_slot - sp_hole) / 2 + sp_skin)"
    prism(c, ("x", "y"), [(nx0, "sp_y - sp_skin"), (nx1, "sp_y - sp_skin"), (nx1, YBP + " + 1 mm"), (nx0, YBP + " + 1 mm")],
          "z", ZT + " - 1 mm", ZT + " + dt_skin_t + 1 mm", "NOTCH - OVER DR'S LEDGE SPIGOTS", "CUT - UNDERSIDE NOTCH", CUT, skin)
    skin.name = "DT SKIN ACP 3"
    bodies["SKIN"] = skin

    # ---- 351202 back plate, inside the skin's ends
    c = comp("BACK")
    # its lower-left edge follows the slope over DL, pushed in by the skin
    xb = "(%s + dl_w + dt_skin_t * (dt_k - 1) / dt_m)" % XL
    # the pushed-in slope meets the top skin's inner face before the left end (dl_zo is 3 under the roof), so the
    # plate's top-left corner is on the slope: a quadrilateral
    xt = "(%s + dl_w - (pod_h - dt_skin_t - dt_zb - dt_skin_t * dt_k) / dt_m)" % XL
    back = [(xb, "dt_zb + dt_skin_t"), (XL + " + dt_xr", "dt_zb + dt_skin_t"), (XL + " + dt_xr", "pod_h - dt_skin_t"),
            (xt, "pod_h - dt_skin_t")]
    f = prism(c, ("x", "z"), back, "y", YBP + " - dt_back_t", YBP, "OUTLINE - DT BACK PLATE", "EXTRUDE - DT BACK PLATE")
    bp = f.bodies.item(0)
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - J-FRONT-03 RIVNUTS (4)",
                   [(jf3_x(i), "jf3_z") for i in range(4)], "jf3_hole")
    L.extrude_span(c, sk, "y", YBP + " - dt_back_t - 1 mm", YBP + " + 1 mm", CUT, [bp], "CUT - J-FRONT-03 RIVNUT HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    bp.name = "DT BACK PLATE AL 2"
    bodies["BACK"] = bp

    # ---- the catch under DT, behind the strike (the door stops against it), and the top stop with its seal
    sx1 = "(%s - st_end)" % latch_x("leaf_zt")
    ca_y0 = GY + " + st_a / 2"                       # the strike's pod-side face when the door is shut
    c = comp("CATCH")
    bodies["CATCH"] = L.box_body(design, c, "CATCH", ("%s - st_l / 2 - ca_l / 2" % sx1, "%s - st_l / 2 + ca_l / 2" % sx1),
                                 (ca_y0, ca_y0 + " + ca_d"), (ZT + " - ca_h", ZT), "CATCH HT-MSG62 ENVELOPE")
    gi = GY + " + glass_t / 2"                        # the leaf's inner face
    x_stop0 = "(%s + door_xl)" % XL                    # from the hinge edge
    x_stop1 = "(%s - st_l / 2 - ca_l / 2 - stop_end)" % sx1
    c = comp("PS")
    bodies["PS"] = L.box_body(design, c, "PS", (x_stop0, x_stop1), (gi, gi + " + stop_gap"),
                              (ZT + " - ps_s", ZT), "FRAME-STOP SEAL PS 1515 - TOP (COMPRESSED TO THE GAP)")
    c = comp("STOP")
    # an angle: the leg the seal sits on, and a flange under DT's underside screwed up into the rail F02
    ys0 = "(%s + stop_gap)" % gi
    ang = [(ys0, ZT + " - stop_h"), ("%s + stop_t" % ys0, ZT + " - stop_h"), ("%s + stop_t" % ys0, ZT + " - stop_t"),
           ("%s + stop_fl" % ys0, ZT + " - stop_t"), ("%s + stop_fl" % ys0, ZT), (ys0, ZT)]
    f = prism(c, ("y", "z"), ang, "x", x_stop0, x_stop1, "SECTION - DOOR TOP STOP (ANGLE)", "EXTRUDE - DOOR TOP STOP")
    stp = f.bodies.item(0)
    yh = "(%s + stop_t + (stop_fl - stop_t) / 2)" % ys0
    sk = L.circles(design, c, c.xYConstructionPlane, ("x", "y"), 0, "HOLES - TOP STOP SCREWS (5)",
                   [("(%s + 50 mm + %d * (%s - %s - 100 mm) / 4)" % (x_stop0, k, x_stop1, x_stop0), yh) for k in range(5)],
                   "stop_hole")
    L.extrude_span(c, sk, "z", ZT + " - stop_t - 1 mm", ZT + " + 1 mm", CUT, [stp], "CUT - TOP STOP SCREW HOLES",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    stp.name = "DOOR TOP STOP ANGLE 20 X 20 X 2"
    bodies["STOP"] = stp

    # ---- 351204 the welded tube frame (stage 2): a weldment assembly, each tube its own component with Control's
    # member number (D-120, #232); the three chamfer cross tubes are copies of one component
    c = comp("FRAME")
    members = frame_members()
    mparts = FL.member_parts(ARGS["repo_root"], FRAME_PN, MP.DT_MEMBERS)
    print("COPIES|%s" % FL.check_copies(members, mparts, lambda e: L.ev(design, e)))
    native, mcomps, moccs = FL.build_member_components(design, c, L, members, "fr_t", mparts, REV)
    frame_occ = root.allOccurrencesByComponent(c).item(0)
    tubes = FL.root_bodies(frame_occ, native, moccs)
    bodies.update(tubes)
    # J-FRONT-03: holes in the top back tube's back wall round the rivnut tails and bolt tips (in 352203 itself)
    yb1 = YBP + " - dt_back_t"
    mc = mcomps["B03"]
    sk = L.circles(design, mc, mc.xZConstructionPlane, ("x", "z"), 0, "HOLES - J-FRONT-03 RIVNUT TAILS (4)",
                   [(jf3_x(i), "jf3_z") for i in range(4)], "jf3_tail")
    L.extrude_span(mc, sk, "y", yb1 + " - fr_t - 1 mm", yb1 + " + 0.5 mm", CUT, [native["B03"]],
                   "CUT - J-FRONT-03 RIVNUT TAILS", profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    # J-FRONT-03: the spigot hole and slot in the bottom back tube's bottom wall, over DR's ledge (in 352201)
    zb3 = ZT + " + dt_skin_t"
    mc = mcomps["B01"]
    sk = L.circles(design, mc, mc.xYConstructionPlane, ("x", "y"), 0, "HOLES - SPIGOT ROUND AND SLOT ENDS",
                   [("sp_x1", "sp_y"), ("sp_x1 + sp_dx - (sp_slot - sp_hole) / 2", "sp_y"),
                    ("sp_x1 + sp_dx + (sp_slot - sp_hole) / 2", "sp_y")], "sp_hole")
    L.extrude_span(mc, sk, "z", zb3 + " - 1 mm", zb3 + " + fr_t + 0.5 mm", CUT, [native["B01"]], "CUT - SPIGOT HOLE AND SLOT ENDS",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    sl = [("sp_x1 + sp_dx - (sp_slot - sp_hole) / 2", "sp_y - sp_hole / 2"),
          ("sp_x1 + sp_dx + (sp_slot - sp_hole) / 2", "sp_y - sp_hole / 2"),
          ("sp_x1 + sp_dx + (sp_slot - sp_hole) / 2", "sp_y + sp_hole / 2"),
          ("sp_x1 + sp_dx - (sp_slot - sp_hole) / 2", "sp_y + sp_hole / 2")]
    prism(mc, ("x", "y"), sl, "z", zb3 + " - 1 mm", zb3 + " + fr_t + 0.5 mm", "SLOT - SPIGOT (MIDDLE)",
          "CUT - SPIGOT SLOT MIDDLE", CUT, native["B01"])

    # the selected ACP's 0.21 mm skins give 3.5 kg/m2 (selection VT01), as WALL, CEILING and AIR count it
    acp = L.material(design, "ACP 3 mm PE core EV3038, 0.21 mm skins (3.5 kg/m2, calculation)", "Aluminum", 3500.0 / 3.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    al6063 = L.material(design, "Aluminium 6063-T6 tube (2700 kg/m3)", "Aluminum", 2700.0)
    for k in native:
        native[k].material = al6063
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    for k, m in (("SKIN", acp), ("BACK", alu), ("STOP", alu), ("PS", env), ("CATCH", env)):
        bodies[k].material = m
    looks = {"SKIN": ["Paint - Enamel Glossy (Yellow)"], "BACK": ["Aluminum - Satin"],
             "STOP": ["Paint - Enamel Glossy (Black)"], "PS": ["Plastic - Matte (Black)"],
             "CATCH": ["Plastic - Matte (Black)"]}
    looks.update({k: ["Aluminum - Satin"] for k in tubes})
    for k, b in bodies.items():
        a = L.appearance(design, looks[k])
        if a:
            (native[k] if k in native else b).appearance = a      # a tube's look on its own component's body

    n_tl, bad, loose = L.health(design)
    hits, bad_clash = L.clash_check(bodies, EXPECTED)
    print("skeleton parameters: %s (%s), %d loaded" % (os.path.relpath(sk_path, ARGS["repo_root"]), sk_rev, len(sk_params)))
    print("bodies %d, timeline %d items, unhealthy %d, loose sketches %d, parameters %d" % (
        len(bodies), n_tl, len(bad), len(loose), design.userParameters.count))
    for k, b in bodies.items():
        bb = L.box(b)
        print("BODY|%s|%s|%g x %g x %g|%s|%.3f kg" % (k, b.name, round(bb[3] - bb[0], 2), round(bb[4] - bb[1], 2),
                                                     round(bb[5] - bb[2], 2), bb, b.physicalProperties.mass))
    print("clash pairs %d, unexpected %d" % (len(hits), len(bad_clash)))
    uniq = {mc_.partNumber: mc_ for mc_ in mcomps.values()}
    print("FRAME|%d tubes as %d parts, %.2f kg, %d shells failed" % (
        len(tubes), len(uniq), FL.frame_mass(frame_occ, moccs),
        sum(1 for mc_ in uniq.values() if mc_.features.shellFeatures.count != 1)))
    print("DT box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DT checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))
    if SCOPES[scope] is not None:
        keep = PARTS[SCOPES[scope]][0]
        for occ in [root.occurrences.item(i) for i in range(root.occurrences.count)]:
            if occ.component.partNumber != keep:
                occ.deleteMe()
        print("scope %s: kept %s only, %d components left" % (scope, keep, root.occurrences.count))


ANCHORS = [
    ("SKIN", 0, "-pod_w / 2"), ("SKIN", 3, "dt_xr - pod_w / 2"), ("SKIN", 2, "dt_zb"), ("SKIN", 5, "pod_h"),
    ("SKIN", 1, "-pod_d / 2"), ("SKIN", 4, "-pod_d / 2 + decor_d - dt_stop_gap"),
    ("BACK", 4, "-pod_d / 2 + decor_d - dt_stop_gap"), ("BACK", 1, "-pod_d / 2 + decor_d - dt_stop_gap - dt_back_t"),
    ("BACK", 3, "dt_xr - pod_w / 2"), ("CATCH", 5, "dt_zb"), ("CATCH", 2, "dt_zb - ca_h"),
    ("PS", 1, "-glass_y + glass_t / 2"), ("STOP", 2, "dt_zb - stop_h"),
    # the frame's sides, each on the tube that reaches it (every tube its own component, D-120)
    ("B02", 3, "dt_xr - pod_w / 2"), ("B01", 2, "dt_zb + dt_skin_t"), ("B03", 5, "pod_h - dt_skin_t"),
    ("B04", 4, "-pod_d / 2 + decor_d - dt_stop_gap - dt_back_t"),
]

# what each tube's row says about its holes and fixings (the cuts in build(); none on the copies)
MEMBER_NOTES = {
    "B01": "J-FRONT-03: spigot hole 8.5 at X 270 and slot 8.5 x 14 at X 410 in its bottom wall, over DR's ledge",
    "B03": "40 x 20 (fr_wtop); J-FRONT-03: 4 holes 14 in its back wall at Z 2374 for the back plate's rivnut tails",
    "F02": "carries the catch 368007 and the top stop 351203 (their screw holes drilled to the parts at assembly, "
           "not modelled yet)",
    "R02": "over the catch 368007 (its screw holes drilled at assembly, not modelled yet)",
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
    seal_len = L.ev(design, "(%s - st_l / 2 - ca_l / 2 - stop_end) - (-pod_w / 2 + door_xl)" % ("(%s - st_end)" % latch_x("leaf_zt")))
    ev = lambda e: L.ev(design, e)
    members = frame_members()
    tube_m = sum(FL.member_numbers(m, ev)["length"] for m in members) / 1000.0
    gt = "general tolerance ISO 2768-m"
    # one row per tube part (D-120, Control's numbers in #232): its copies counted in the quantity
    mparts = FL.member_parts(root_dir, FRAME_PN, MP.DT_MEMBERS)
    member_rows, seen = [], set()
    for m in members:
        pn, mname, mvn = mparts[m["key"]]
        if pn in seen:
            continue
        seen.add(pn)
        keys = [k for k in MP.DT_MEMBERS if MP.DT_MEMBERS[k] == pn]
        num = FL.member_numbers(m, ev)
        note = "member%s %s of the frame %s; %.1f long, ends: %s" % (
            "s" if len(keys) > 1 else "", ", ".join(keys), FRAME_PN, num["length"], m["ends"])
        if m["key"] in MEMBER_NOTES:
            note += "; " + MEMBER_NOTES[m["key"]]
        member_rows.append((pn, mname, mvn, len(keys), "made: tube cut to length, ends as its cut list row",
                            "aluminium EN AW-6063-T6 tube %s, finish: mill finish (hidden, D-79)" % m["section"], "cad",
                            "calculation (CAD, 2700 kg/m3, shelled)", "DRAFT", "number allocation (D-120, #232)", note))
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-49, D-79; PM rulings 2026-10-31; this build",
         "skin bonded to the welded tube frame 351204; goes on after the door hangs (packing plan)"),
        ("351201", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1, bonded to "
         "the frame", "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 3.5 kg/m2: selection VT01)", "DRAFT",
         "D-12, D-49; skeleton DT shape", "one flat panel per outside face: " + DXF_SKIN_REL.split("/")[-1] +
         "; bond to the frame per the joints register's ACP bond spec"),
        (FRAME_PN, PARTS["FRAME"][1], PARTS["FRAME"][2], 1, "weldment assembly: %d tubes as %d parts below, "
         "TIG-welded (cut list %s)" % (len(members), len(member_rows), CUT_REL.split("/")[-1]),
         "aluminium EN AW-6063-T6 tube 20 x 20 x 1.5 and 40 x 20 x 1.5, finish: mill finish (hidden, D-79)", None, "",
         "DRAFT", "v1 decor frame drawing (front and back frames); D-79; D-120 (each tube its own part, #232)",
         "%.1f m of tube; welds per its weldment drawing; J-FRONT-03's holes in 352201 and 352203" % tube_m),
    ] + member_rows + [
        ("351202", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made (laser-cut sheet, no drawing: D-89 part 4)",
         "aluminium EN AW-5754-H22 sheet 2.0 mm, finish mill finish (hidden, D-79); " + gt, "cad",
         "calculation (CAD, 2700 kg/m3)", "DRAFT",
         "joints register J-FRONT-03 (HOLD-10 met by 2 mm aluminium); PM ruling 2026-11-01",
         "DXF " + DXF_BACK_REL.split("/")[-1] + "; 4 holes 9.53 +0.10/0 for the rivnuts 838003 with their stop "
         "washers (counted in the joints register) on Z 2374 (critical: on the ceiling's bolt line); behind it the "
         "soffit (D-60); blind-riveted to the frame (HOLD: rivet)"),
        ("351203", PARTS["STOP"][1], PARTS["STOP"][2], 1, "made (aluminium angle, cut to length)",
         "aluminium EN AW-6063-T6, finish black anodised matte 20 um (AA20)", "cad", "calculation (CAD)", "DRAFT",
         "selection C3 (frame gap 2 to 6)", "screwed up through DT's underside into the frame's rail F02"),
        ("368005", "FRONT - FRAME-STOP SEAL", "Gioăng chặn cửa", 1,
         "bought by length", "athmer PS 1515 P Flex, PVC co-extrusion, self-adhesive", 0.05, "assumption",
         "source (product)", "hardware selection C3; joints register", "top run %.0f mm (DL's run in DL's list)" % seal_len),
        ("368007", PARTS["CATCH"][1], PARTS["CATCH"][2], 1, "bought", "Sugatsune HT-MSG62: silicone body, SUS304 "
         "bracket, neodymium magnet; finish as supplied", 0.052, "source (Sugatsune datasheet, 52.2 g)",
         "source (product)", "hardware selection C7; PM rulings 2026-10-31",
         "door stop and 35 N catch; its strike 368102 is on the leaf; 3 x M4 x 12 up into the frame's rail F02 and "
         "the cross tube R02 over it"),
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
    import csv
    with open(os.path.join(root_dir, CUT_REL), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "member", "part_number", "name", "section", "length_mm", "qty", "ends", "status"])
        w.writerows(tuple(r[:2]) + (mparts[r[1]][0],) + tuple(r[2:]) for r in FL.cut_list_rows(members, ev, FRAME_PN))
    print("cut list %s: %d tubes, %.2f m" % (CUT_REL, len(members), tube_m))
    back_comp = [c for c in design.allComponents if c.partNumber == PARTS["BACK"][0]][0]
    try:
        res = FL.write_plate_dxf(os.path.join(root_dir, DXF_BACK_REL), back_comp.bRepBodies.item(0))
        print("DXF %s: %s x %s, %d holes, origin at pod %s" % (DXF_BACK_REL, res[0], res[1], res[2], res[3]))
    except Exception as exc:
        print("DXF %s FAILED: %r" % (DXF_BACK_REL, exc))
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as fh:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % ((PARTS[k][0], PARTS[k][1]) if k in PARTS else mparts[k][:2]), "index": i,
             "expression": e} for k, i, e in ANCHORS]},
            fh, indent=1, ensure_ascii=False)
    before, after, diff = L.step_reread(app, doc, design, step)
    print("STEP re-read in Fusion: model box %s, STEP box %s, max diff %.3f mm" % (before, after, diff))


SHOTS = [("v2/01-CAD-Native/front/350002_P01_FRONT-DECOR-BLOCK-ASSY-DT-FRONT_IMG.png", "front"),
         ("v2/01-CAD-Native/front/350002_P01_FRONT-DECOR-BLOCK-ASSY-DT-ISO_IMG.png", "iso-top-right")]


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
