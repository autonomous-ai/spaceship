"""350001 FRONT - DECOR BLOCK ASSY - DL (Khối trang trí trái): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dl_block.py \
        --doc 350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/dl_block.py \
        --doc 350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_CAD --arg step=export --close

Stage 1 of the left decor block, which carries the door (D-19):
- the outer shape: the skeleton's DL (plan with v1's two facets, from the base band top to the slope DT sits on);
- 351101 the 3 mm ACP skin, by shelling that shape, left open at the back (back plate) and on the slope under DT;
  the three hinge pockets are cut where the door unit's HOLD hinge spaces enter DL (160 mm, D-30's candidate);
- 351102 the back plate;
- 351103 the door's hinge-side stop and 368005 the frame-stop seal (athmer PS 1515 P Flex) on it, sealing on the
  leaf's inner face along its hinge edge, broken at each hinge (the hinges are HOLD, D-46).
The aluminium frame, which takes the door's moment (ISS-045), is stage 2.
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
PN = "350001"
NAME = "FRONT - DECOR BLOCK ASSY - DL"
VN = "Khối trang trí trái (cụm)"
DOC_NAME = "%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_BOM.csv" % (PN, REV)
DXF_SKIN_REL = "v2/03-Manufacturing/front/351101_%s_FRONT-DECOR-SKIN-DL_DXF.dxf" % REV
CUT_REL = "v2/03-Manufacturing/front/351104_%s_FRONT-DECOR-FRAME-DL-TUBE-CUT-LIST.csv" % REV
DXF_BACK_REL = "v2/03-Manufacturing/front/351102_%s_FRONT-DECOR-BACK-PLATE-DL_DXF.dxf" % REV
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_ANCHORS.json" % (PN, REV)

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"
GY = "-glass_y"
ZB = "wall_z0"

OWN = [
    ("dl_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dl_back_t", "2 mm", "mm", "source",
     "joints register J-FRONT-01: the back plate is aluminium 1.0 to 2.7 thick at each bolt, for the rivnuts (HOLD-10)"),
    ("door_top_cut", "2 mm", "mm", "decided", "PM ruling 2026-10-31: the leaf 2 mm short of the skeleton top (catch gap)"),
    ("leaf_zt", "door_zt - door_top_cut", "mm", "calculation", "top of the door leaf"),
    # the door unit's HOLD hinge spaces (same parameters as door_unit.py)
    ("hinge_clamp_h", "120 mm", "mm", "assumption", "reserved height per hinge; HOLD H01 (as the door unit)"),
    ("hinge_clamp_t", "40 mm", "mm", "assumption", "reserved thickness across the glass; HOLD H01 (as the door unit)"),
    ("hinge_pocket_d", "160 mm", "mm", "source", "the HOLD candidate's 160 mm frame pocket in DL (D-30, D-46)"),
    ("hinge_x0", XL + " + dl_w - hinge_pocket_d", "mm", "calculation", "inner end of the hinge pocket"),
    ("hinge_z1", "door_zb + 250 mm", "mm", "assumption", "as the door unit; HOLD H01"),
    ("hinge_z3", "leaf_zt - 250 mm", "mm", "assumption", "as the door unit; HOLD H01"),
    ("hinge_z2", "(hinge_z1 + hinge_z3) / 2", "mm", "assumption", "as the door unit; HOLD H01"),
    ("hinge_clear", "2 mm", "mm", "assumption", "the pocket's clearance round the hinge space"),
    # the hinge-side stop and its seal
    ("stop_gap", "4 mm", "mm", "source", "athmer PS 1515 P Flex works in a 2 to 6 mm frame gap (selection C3): 4 nominal"),
    ("ps_s", "15 mm", "mm", "source", "athmer PS 1515 P Flex, 15 x 15 (selection C3)"),
    ("stop_t", "2 mm", "mm", "assumption", "stop: an aluminium angle leg 2 thick on DL's door-side face"),
    ("stop_reach", "door_xl - dl_w + ps_s", "mm", "calculation", "the stop reaches from DL's face across the 11 mm gap and 15 over the glass"),
    ("hinge_skip", "10 mm", "mm", "assumption", "the stop and seal stop 10 short of each hinge space"),
    # ---- the tube frame (stage 2): v1's DL frame (16 mm steel box, 60 x 20 hinge members; sources/v1 decor frame
    # drawing) in 6063-T6 aluminium tube (D-79). It carries the door: hinges -> hinge post -> rings -> bolt-line
    # post -> back plate -> J-FRONT-01 bolts -> left wall (ISS-045)
    ("fr_w", "20 mm", "mm", "calculation", "frame tube 20 x 20 x 1.5, 6063-T6 (D-79), as DR and DT"),
    ("fr_t", "1.5 mm", "mm", "calculation", "frame tube wall, as fr_w"),
    ("fr_wb", "60 mm", "mm", "assumption",
     "bolt-line post 60 x 20 x 1.5 behind the back plate: the J-FRONT-01 rivnut tails go into it through 14 mm holes "
     "(HOLD-10), mirror of DR's"),
    ("fr_wh", "60 mm", "mm", "assumption",
     "hinge post 60 x 20 x 1.5 behind the three hinge pockets, 60 across the glass plane, as v1's 60 x 20 members: "
     "the hinges' frame halves screw into it (holes when the hinge is named, HOLD H01)"),
    ("fr_hole_jf", "14 mm", "mm", "calculation", "hole round each J-FRONT-01 rivnut in the bolt-line post, as DR"),
    ("dl_m", "(dl_zo - dt_zb) / dl_w", "", "calculation", "rise of the slope DT sits on, per unit of X"),
    ("dl_k", "sqrt(1 + dl_m * dl_m)", "", "calculation", "for pushing the slope line in"),
    ("dl_l1", "sqrt(dl_x2 * dl_x2 + (dl_y2 - dl_y1) * (dl_y2 - dl_y1))", "mm", "calculation", "outer facet length in plan"),
    ("dl_l2", "sqrt((dl_x3 - dl_x2) * (dl_x3 - dl_x2) + (dl_y3 - dl_y2) * (dl_y3 - dl_y2))", "mm", "calculation",
     "front facet length in plan"),
    ("fr_z2", "(hinge_z1 + hinge_z2) / 2 - fr_w / 2", "mm", "calculation", "ring between hinges 1 and 2"),
    ("fr_z3", "(hinge_z2 + hinge_z3) / 2 - fr_w / 2", "mm", "calculation", "ring between hinges 2 and 3"),
    ("fr_z4", "dt_zb + dl_m * dl_skin_t - dl_skin_t * dl_k - fr_w", "mm", "calculation",
     "top ring, just under the slope at DL's door-side face"),
]

PARTS = {
    "SKIN": ("351101", "FRONT - DECOR SKIN - DL", "Tấm ốp alu khối trái"),
    "BACK": ("351102", "FRONT - DECOR BACK PLATE - DL", "Tấm hậu khối trái"),
    "STOP": ("351103", "FRONT - DOOR HINGE-SIDE STOP - DL", "Nẹp chặn cửa phía bản lề"),
    "PS": ("368005", "FRONT - DOOR SEAL - FRAME STOP - ATHMER PS 1515 P FLEX - HINGE SIDE", "Gioăng chặn cửa phía bản lề"),
    "FRAME": ("351104", "FRONT - DECOR FRAME - DL", "Khung trang trí trái (hàn)"),
}

EXPECTED = []
FRAME_PN = "351104"
S20, S60 = "20 x 20 x 1.5", "60 x 20 x 1.5"


def frame_members():
    """DL's welded tube frame as data: a back ring with the 60 mm bolt-line post, four plan rings (bottom, between
    the hinges, top), and the 60 mm hinge post and the door-side front post in lengths between the rings."""
    yb0, yb1 = "(%s - dl_back_t - fr_w)" % YB, "(%s - dl_back_t)" % YB
    M = []

    def add(key, name, axes, pts, along, a, b, section=S20, axis=(0, 1), ends=None):
        M.append({"key": key, "name": name, "axes": axes, "pts": pts, "along": along, "a": a, "b": b,
                  "section": section, "axis": axis, "ends": ends or "mitred to its neighbours (angles on the frame drawing)"})

    # back ring, in the back plate's plane
    bot, door = FL.line(0, 1, ZB), FL.line(-1, 0, "-(%s + dl_w)" % XL)
    slope = FL.line("-dl_m / dl_k", "-1 / dl_k", "-(dt_zb + dl_m * (%s + dl_w)) / dl_k" % XL)
    left = FL.line(1, 0, XL)
    back = FL.ring([(bot, "dl_skin_t", "fr_w"), (door, "dl_skin_t", "fr_w"), (slope, "dl_skin_t", "fr_w"),
                    (left, "dl_skin_t", "fr_wb")])
    for k, (key, nm, sec) in enumerate((("B01", "BACK RING BOTTOM", S20), ("B02", "BACK RING DOOR SIDE", S20),
                                        ("B03", "BACK RING SLOPE UNDER DT", S20), ("B04", "BACK RING BOLT LINE", S60))):
        add(key, nm, ("x", "z"), back[k], "y", yb0, yb1, sec)
    # plan rings: door side, back, outer facet, front facet (the 7 mm front face gets no tube)
    p_door = FL.line(-1, 0, "-(%s + dl_w)" % XL)
    p_back = FL.line(0, -1, "dl_y1")
    f1 = FL.line("(dl_y2 - dl_y1) / dl_l1", "dl_x2 / dl_l1",
                 "(dl_y2 - dl_y1) / dl_l1 * (%s) + dl_x2 / dl_l1 * (-dl_y1)" % XL)
    f2 = FL.line("(dl_y3 - dl_y2) / dl_l2", "(dl_x3 - dl_x2) / dl_l2",
                 "(dl_y3 - dl_y2) / dl_l2 * (%s + dl_x2) + (dl_x3 - dl_x2) / dl_l2 * (-dl_y2)" % XL)
    p_front = FL.line(0, 1, "-dl_y3")
    # the 7 mm front face is too short for a tube: the door-side tube's front end follows the front skin and the
    # front facet, and the front facet tube stops on the door-side tube's inner face
    P = FL.push
    d3, d23 = P(p_door, "dl_skin_t"), P(p_door, "dl_skin_t + fr_w")
    k0, k20 = p_back, P(p_back, "fr_w")
    o3, o23 = P(f1, "dl_skin_t"), P(f1, "dl_skin_t + fr_w")
    q3, q23 = P(f2, "dl_skin_t"), P(f2, "dl_skin_t + fr_w")
    fr3, fr23 = P(p_front, "dl_skin_t"), P(p_front, "dl_skin_t + fr_w")
    E, A, B, C = FL.meet(fr3, q3), FL.meet(fr3, d3), FL.meet(d3, k0), FL.meet(d23, k20)
    D, D2 = FL.meet(q3, d23), FL.meet(q23, d23)
    G, G2, K, K2 = FL.meet(k0, o3), FL.meet(k20, o23), FL.meet(o3, q3), FL.meet(o23, q23)
    ring_parts = (("D", "DOOR SIDE", [E, A, B, C, D], (1, 2)), ("K", "BACK", [B, G, G2, C], (0, 1)),
                  ("O", "OUTER FACET", [G, K, K2, G2], (0, 1)), ("F", "FRONT FACET", [K, D, D2, K2], (0, 1)))
    levels = [("1", "BOTTOM", "%s + dl_skin_t" % ZB), ("2", "BETWEEN HINGES 1 AND 2", "fr_z2"),
              ("3", "BETWEEN HINGES 2 AND 3", "fr_z3"), ("4", "TOP", "fr_z4")]
    for n, lv, z0 in levels:
        for tag, nm, pts, ax in ring_parts:
            add("R%s%s" % (n, tag), "RING %s - %s" % (lv, nm), ("x", "y"), pts, "z", z0, "%s + fr_w" % z0, axis=ax)
    # the hinge post and the door-side front post, in lengths between the rings
    xh1 = "(hinge_x0 - hinge_clear)"
    hp = [("%s - fr_w" % xh1, "%s - fr_wh / 2" % GY), (xh1, "%s - fr_wh / 2" % GY), (xh1, "%s + fr_wh / 2" % GY),
          ("%s - fr_w" % xh1, "%s + fr_wh / 2" % GY)]
    fp = [E, A, FL.meet(fr23, d3), FL.meet(fr23, d23), D]
    spans = [("%s + dl_skin_t + fr_w" % ZB, "fr_z2"), ("fr_z2 + fr_w", "fr_z3"), ("fr_z3 + fr_w", "fr_z4")]
    for i, (z0, z1) in enumerate(spans):
        add("H%d" % (i + 1), "HINGE POST %d (HINGE H%d)" % (i + 1, i + 1), ("x", "y"), hp, "z", z0, z1, S60,
            ends="square both ends, between the rings")
        M[-1]["lengthwise"] = True
        add("P%d" % (i + 1), "DOOR-SIDE FRONT POST %d" % (i + 1), ("x", "y"), fp, "z", z0, z1,
            ends="square both ends, between the rings")
        M[-1]["lengthwise"] = True
    return M


def build(app):
    design = L.start_design(app, PN, "%s | %s | %s" % (NAME, VN, REV))
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

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(root, pn, nm, vn, REV)
        comps[key] = c
        return c

    def prism(c, axes, pts, along, a, b, sketch, feat, op=NEW, body=None):
        sk = L.poly(design, c, L.plane_of(c, axes), axes, 0, sketch, pts)
        return L.extrude_span(c, sk, along, a, b, op, [body] if body else None, feat)

    # ---- 351101 skin: the skeleton's DL shape, shelled, with the hinge pockets
    c = comp("SKIN")
    plan = [(XL, YB), (XL, "-dl_y1"), (XL + " + dl_x2", "-dl_y2"), (XL + " + dl_x3", "-dl_y3"),
            (XL + " + dl_w", "-dl_y3"), (XL + " + dl_w", YB)]
    f = prism(c, ("x", "y"), plan, "z", ZB, "pod_h", "PLAN - DL FACETS (SKELETON)", "EXTRUDE - DL OUTER SHAPE")
    skin = f.bodies.item(0)
    prism(c, ("x", "z"), [(XL, "dl_zo"), (XL + " + dl_w", "dt_zb"), (XL + " + dl_w", "pod_h"), (XL, "pod_h")],
          "y", YF, YB, "SLOPE - DL TOP UNDER DT", "CUT - DL TOP SLOPE", CUT, skin)
    yb = L.ev(design, YB)
    open_faces, kinds = adsk.core.ObjectCollection.create(), []
    for fc in skin.faces:
        p = fc.pointOnFace
        _ok, n = fc.evaluator.getNormalAtPoint(p)
        if abs(n.y - 1) < 1e-6 and abs(p.y * 10 - yb) < 0.05:
            kinds.append("back")
        elif n.x > 0.2 and n.z > 0.2:
            kinds.append("DT joint")
        else:
            continue
        open_faces.add(fc)
    if sorted(kinds) != ["DT joint", "back"]:
        raise RuntimeError("faces to leave open: found %s" % kinds)
    si = c.features.shellFeatures.createInput(open_faces, False)
    si.insideThickness = L.vi("dl_skin_t")
    c.features.shellFeatures.add(si).name = "SHELL - DL SKIN 3 MM (OPEN AT THE BACK AND UNDER DT)"
    for i, zc in enumerate(("hinge_z1", "hinge_z2", "hinge_z3")):
        prism(c, ("x", "y"), [("hinge_x0 - hinge_clear", GY + " - hinge_clamp_t / 2 - hinge_clear"),
                              (XL + " + dl_w + 1 mm", GY + " - hinge_clamp_t / 2 - hinge_clear"),
                              (XL + " + dl_w + 1 mm", GY + " + hinge_clamp_t / 2 + hinge_clear"),
                              ("hinge_x0 - hinge_clear", GY + " + hinge_clamp_t / 2 + hinge_clear")],
              "z", "%s - hinge_clamp_h / 2 - hinge_clear" % zc, "%s + hinge_clamp_h / 2 + hinge_clear" % zc,
              "POCKET - HINGE H%d (HOLD SPACE)" % (i + 1), "CUT - HINGE POCKET H%d IN THE SKIN" % (i + 1), CUT, skin)
    skin.name = "DL SKIN ACP 3"
    bodies["SKIN"] = skin

    # ---- 351102 back plate: up to the slope under DT
    c = comp("BACK")
    slope_z = lambda x: "(dl_zo + (dt_zb - dl_zo) * ((%s) - (%s)) / dl_w)" % (x, XL)
    xl_in, xr_in = XL + " + dl_skin_t", XL + " + dl_w - dl_skin_t"
    f = prism(c, ("x", "z"), [(xl_in, ZB + " + dl_skin_t"), (xr_in, ZB + " + dl_skin_t"), (xr_in, slope_z(xr_in)),
                              (xl_in, slope_z(xl_in))], "y", YB + " - dl_back_t", YB, "OUTLINE - DL BACK PLATE",
              "EXTRUDE - DL BACK PLATE")
    bodies["BACK"] = f.bodies.item(0)
    # J-FRONT-01: six rivnut holes on the left wall's front member line, 3 per side panel (220 rule)
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - J-FRONT-01 RIVNUTS (6)",
                   [("-jf_x", "jf_z%d" % i) for i in range(1, 7)], "jf_hole")
    L.extrude_span(c, sk, "y", YB + " - dl_back_t - 1 mm", YB + " + 1 mm", CUT, [bodies["BACK"]],
                   "CUT - J-FRONT-01 RIVNUT HOLES", profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])
    bodies["BACK"].name = "DL BACK PLATE AL 2"

    # ---- the hinge-side stop and its seal, between the hinge spaces
    gi = GY + " + glass_t / 2"
    xs0, xs1 = XL + " + dl_w", XL + " + dl_w + stop_reach"
    spans = [("door_zb", "hinge_z1 - hinge_clamp_h / 2 - hinge_skip"),
             ("hinge_z1 + hinge_clamp_h / 2 + hinge_skip", "hinge_z2 - hinge_clamp_h / 2 - hinge_skip"),
             ("hinge_z2 + hinge_clamp_h / 2 + hinge_skip", "hinge_z3 - hinge_clamp_h / 2 - hinge_skip"),
             ("hinge_z3 + hinge_clamp_h / 2 + hinge_skip", "leaf_zt")]
    c_ps, c_st = comp("PS"), comp("STOP")
    for i, (z0, z1) in enumerate(spans):
        b = L.box_body(design, c_ps, "PS%d" % (i + 1), (XL + " + door_xl", XL + " + door_xl + ps_s"), (gi, gi + " + stop_gap"),
                       (z0, z1), "FRAME-STOP SEAL PS 1515 - HINGE SIDE %d" % (i + 1))
        bodies["PS%d" % (i + 1)] = b
        b = L.box_body(design, c_st, "ST%d" % (i + 1), (xs0, xs1), (gi + " + stop_gap", gi + " + stop_gap + stop_t"),
                       (z0, z1), "HINGE-SIDE STOP %d (ANGLE LEG)" % (i + 1))
        bodies["ST%d" % (i + 1)] = b

    # ---- 351104 the welded tube frame (stage 2)
    c = comp("FRAME")
    tubes = FL.build_members(design, c, L, frame_members(), "fr_t")
    sk = L.circles(design, c, c.xZConstructionPlane, ("x", "z"), 0, "HOLES - J-FRONT-01 RIVNUT TAILS AND BOLT TIPS (6)",
                   [("-jf_x", "jf_z%d" % i) for i in range(1, 7)], "fr_hole_jf")
    yb1 = YB + " - dl_back_t"
    L.extrude_span(c, sk, "y", yb1 + " - fr_t - 1 mm", yb1 + " + 0.5 mm", CUT, [tubes["B04"]],
                   "CUT - J-FRONT-01 RIVNUT TAILS AND BOLT TIPS",
                   profiles=[sk.profiles.item(i) for i in range(sk.profiles.count)])

    acp = L.material(design, "ACP 3 mm PE core EV3038 (1300 kg/m3, calculation)", "Aluminum", 1300.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    al6063 = L.material(design, "Aluminium 6063-T6 tube (2700 kg/m3)", "Aluminum", 2700.0)
    for k, b in tubes.items():
        b.material = al6063
        a = L.appearance(design, ["Aluminum - Satin"])
        if a:
            b.appearance = a
    for k, b in bodies.items():
        b.material = acp if k == "SKIN" else (alu if k.startswith("ST") or k == "BACK" else env)
        a = L.appearance(design, ["Paint - Enamel Glossy (Yellow)"] if k in ("SKIN", "BACK") else
                         (["Paint - Enamel Glossy (Black)"] if k.startswith("ST") else ["Plastic - Matte (Black)"]))
        if a:
            b.appearance = a
    bodies.update(tubes)

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
    print("FRAME|%d tubes, %.2f kg, %d shells failed" % (len(tubes), L.comp_mass(comps["FRAME"]),
          sum(1 for k in tubes if not any(f.name.startswith("SHELL - TUBE %s " % k) for f in comps["FRAME"].features.shellFeatures))))
    print("DL box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DL checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))


ANCHORS = [
    ("SKIN", 0, "-pod_w / 2"), ("SKIN", 3, "dl_w - pod_w / 2"), ("SKIN", 2, "wall_z0"), ("SKIN", 5, "dl_zo"),
    ("SKIN", 1, "-dl_y3"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 3, "dl_w - pod_w / 2 - dl_skin_t"), ("PS", 0, "door_xl - pod_w / 2"), ("PS", 5, "leaf_zt"),
    ("STOP", 3, "door_xl + ps_s - pod_w / 2"),
    ("FRAME", 0, "-pod_w / 2 + dl_skin_t"), ("FRAME", 3, "dl_w - pod_w / 2 - dl_skin_t"), ("FRAME", 2, "wall_z0 + dl_skin_t"),
    ("FRAME", 4, "-pod_d / 2 + decor_d - dl_back_t"), ("FRAME", 1, "-dl_y3 + dl_skin_t"),
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
    seal_len = L.ev(design, "leaf_zt - door_zb - 3 * (hinge_clamp_h + 2 * hinge_skip)")
    ev = lambda e: L.ev(design, e)
    members = frame_members()
    tube_m = sum(FL.member_numbers(m, ev)["length"] for m in members) / 1000.0
    gt = "general tolerance ISO 2768-m"
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-19, D-49, D-79; PM rulings 2026-10-31; this build",
         "skin bonded to the welded tube frame 351104; ships with the hinges' frame halves fitted (packing plan)"),
        ("351101", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1, bonded to "
         "the frame", "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 1300 kg/m3)", "DRAFT",
         "D-12, D-49; skeleton DL shape", "three hinge pockets (HOLD sizes); one flat panel per outside face: " +
         DXF_SKIN_REL.split("/")[-1] + "; bond to the frame per the joints register's ACP bond spec"),
        (FRAME_PN, PARTS["FRAME"][1], PARTS["FRAME"][2], 1, "made: welded frame, %d tubes (cut list %s)" % (
            len(members), CUT_REL.split("/")[-1]), "aluminium EN AW-6063-T6 tube 20 x 20 x 1.5 and 60 x 20 x 1.5, "
         "finish mill (hidden, D-79)", "cad", "calculation (CAD, 2700 kg/m3, tubes shelled)", "DRAFT",
         "v1 decor frame drawing (DL frame, 60 x 20 hinge members); D-79; joints register HOLD-10, ISS-045",
         "%.1f m of tube; the door's load: hinges, hinge post H1 to H3, rings, bolt-line post B04 (6 holes 14 for "
         "the J-FRONT-01 rivnut tails), back plate, bolts; hinge fixing holes when the hinge is named (HOLD H01)" % tube_m),
        ("351102", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made (laser-cut sheet, no drawing: D-89 part 4)",
         "aluminium EN AW-5754-H22 sheet 2.0 mm, finish mill (hidden, D-79); " + gt, "cad",
         "calculation (CAD, 2700 kg/m3)", "DRAFT", "joints register J-FRONT-01 (HOLD-10 answered: 2 mm aluminium)",
         "DXF " + DXF_BACK_REL.split("/")[-1] + "; 6 holes 9.53 +0.10/0 for the rivnuts 838003 (counted in the joints "
         "register) on X -1224, 3 per side panel (critical: on the wall's bolt line); blind-riveted to the frame "
         "(HOLD: rivet)"),
        ("351103", PARTS["STOP"][1], PARTS["STOP"][2], 1, "made (aluminium angle, 4 lengths between the hinges)",
         "aluminium EN AW-6063-T6, finish black anodised matte 20 um (AA20)", "cad", "calculation (CAD)", "DRAFT",
         "selection C3 (frame gap 2 to 6)", "screwed through DL's door-side skin into the frame's door-side tubes"),
        ("368005", "FRONT - DOOR SEAL - FRAME STOP - ATHMER PS 1515 P FLEX", "Gioăng chặn cửa", 1, "bought by length",
         "athmer PS 1515 P Flex, PVC co-extrusion, self-adhesive", 0.07, "assumption", "source (product)",
         "hardware selection C3; joints register", "hinge-side run %.0f mm in 4 pieces (DT's run in DT's list)" % seal_len),
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
        w.writerow(["frame", "member", "name", "section", "length_mm", "qty", "ends", "status"])
        w.writerows(FL.cut_list_rows(members, ev, FRAME_PN))
    print("cut list %s: %d tubes, %.2f m" % (CUT_REL, len(members), tube_m))
    back_comp = [c for c in design.allComponents if c.partNumber == PARTS["BACK"][0]][0]
    try:
        res = FL.write_plate_dxf(os.path.join(root_dir, DXF_BACK_REL), back_comp.bRepBodies.item(0))
        print("DXF %s: %s x %s, %d holes, origin at pod %s" % (DXF_BACK_REL, res[0], res[1], res[2], res[3]))
    except Exception as exc:
        print("DXF %s FAILED: %r" % (DXF_BACK_REL, exc))
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as fh:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % (PARTS[k][0], PARTS[k][1]), "index": i, "expression": e} for k, i, e in ANCHORS]},
            fh, indent=1, ensure_ascii=False)
    before, after, diff = L.step_reread(app, doc, design, step)
    print("STEP re-read in Fusion: model box %s, STEP box %s, max diff %.3f mm" % (before, after, diff))


SHOTS = [("v2/01-CAD-Native/front/350001_P01_FRONT-DECOR-BLOCK-ASSY-DL-FRONT_IMG.png", "front"),
         ("v2/01-CAD-Native/front/350001_P01_FRONT-DECOR-BLOCK-ASSY-DL-ISO_IMG.png", "iso-top-right")]


def run(_context):
    """step: build | export | post (export, pictures, edit test with --arg edits=...) | all (build, save, post)."""
    app = adsk.core.Application.get()
    step = ARGS.get("step", "build")
    doc = app.activeDocument
    if doc is None or not doc.name.startswith(DOC_NAME):
        raise RuntimeError("active document is %r, not %s: open it with the runner's --doc" % (
            doc.name if doc else None, DOC_NAME))
    design = adsk.fusion.Design.cast(app.activeProduct)
    if step == "post" and not any(c.partNumber == FRAME_PN for c in design.allComponents):
        print("the saved design has no frame yet (stage 1): rebuilding it with the frame first")
        step = "all"
        ARGS.setdefault("desc", "P01 stage 2: welded tube frame 351104 (hinge post, bolt-line post, rings)")
    L.run_steps(app, ARGS, HERE, step, build, export_all, SHOTS, ANCHORS_REL)
