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

REV = "P01"
PN = "350001"
NAME = "FRONT - DECOR BLOCK ASSY - DL"
VN = "Khối trang trí trái (cụm)"
DOC_NAME = "%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DL_BOM.csv" % (PN, REV)
DXF_SKIN_REL = "v2/03-Manufacturing/front/351101_%s_FRONT-DECOR-SKIN-DL_DXF.dxf" % REV
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
]

PARTS = {
    "SKIN": ("351101", "FRONT - DECOR SKIN - DL", "Tấm ốp alu khối trái"),
    "BACK": ("351102", "FRONT - DECOR BACK PLATE - DL", "Tấm hậu khối trái"),
    "STOP": ("351103", "FRONT - DOOR HINGE-SIDE STOP - DL", "Nẹp chặn cửa phía bản lề"),
    "PS": ("368005", "FRONT - DOOR SEAL - FRAME STOP - ATHMER PS 1515 P FLEX - HINGE SIDE", "Gioăng chặn cửa phía bản lề"),
}

EXPECTED = []


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

    acp = L.material(design, "ACP 3 mm PE core EV3038 (1300 kg/m3, calculation)", "Aluminum", 1300.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    for k, b in bodies.items():
        b.material = acp if k == "SKIN" else (alu if k.startswith("ST") or k == "BACK" else env)
        a = L.appearance(design, ["Paint - Enamel Glossy (Yellow)"] if k in ("SKIN", "BACK") else
                         (["Paint - Enamel Glossy (Black)"] if k.startswith("ST") else ["Plastic - Matte (Black)"]))
        if a:
            b.appearance = a

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
    print("DL box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DL checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))


ANCHORS = [
    ("SKIN", 0, "-pod_w / 2"), ("SKIN", 3, "dl_w - pod_w / 2"), ("SKIN", 2, "wall_z0"), ("SKIN", 5, "dl_zo"),
    ("SKIN", 1, "-dl_y3"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 3, "dl_w - pod_w / 2 - dl_skin_t"), ("PS", 0, "door_xl - pod_w / 2"), ("PS", 5, "leaf_zt"),
    ("STOP", 3, "door_xl + ps_s - pod_w / 2"),
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
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-19, D-49; PM rulings 2026-10-31; this build",
         "stage 1: no frame yet (stage 2, ISS-045); ships with the hinges' frame halves fitted (packing plan)"),
        ("351101", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1",
         "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 1300 kg/m3)", "DRAFT",
         "D-12, D-49; skeleton DL shape", "three hinge pockets (HOLD sizes); panel split and flat patterns: stage 2"),
        ("351102", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made (laser-cut sheet)",
         "aluminium EN AW-5754-H22 sheet 2.0, finish mill (hidden, D-79)", "cad", "calculation (CAD, 2700 kg/m3)",
         "DRAFT", "joints register J-FRONT-01 (HOLD-10 answered: 2 mm aluminium)",
         "6 holes 9.53 for the rivnuts 838003 (counted in the joints register) on X -1224, 3 per side panel"),
        ("351103", PARTS["STOP"][1], PARTS["STOP"][2], 1, "made (aluminium angle, 4 lengths between the hinges)",
         "aluminium EN AW-6063-T6, finish black anodised matte 20 um (AA20)", "cad", "calculation (CAD)", "DRAFT",
         "selection C3 (frame gap 2 to 6)", "screwed to DL's frame: fixings stage 2"),
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
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as fh:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % (PARTS[k][0], PARTS[k][1]), "index": i, "expression": e} for k, i, e in ANCHORS]},
            fh, indent=1, ensure_ascii=False)
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
