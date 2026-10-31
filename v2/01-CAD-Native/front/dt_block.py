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
    return m


L = load_lib()

REV = "P01"
PN = "350002"
NAME = "FRONT - DECOR BLOCK ASSY - DT"
VN = "Khối trang trí trên (cụm)"
DOC_NAME = "%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_BOM.csv" % (PN, REV)
DXF_SKIN_REL = "v2/03-Manufacturing/front/351201_%s_FRONT-DECOR-SKIN-DT_DXF.dxf" % REV
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-DECOR-BLOCK-ASSY-DT_ANCHORS.json" % (PN, REV)

XL, XR = "-pod_w / 2", "pod_w / 2"
YF, YB = "-pod_d / 2", "-pod_d / 2 + decor_d"
GY = "-glass_y"
ZT = "fg_vis_zt"                   # DT's underside = dt_zb


def latch_x(z):
    return "(%s + door_xbr - (door_xbr - door_xtr) * ((%s) - door_zb) / (door_zt - door_zb))" % (XL, z)


OWN = [
    ("dt_skin_t", "3 mm", "mm", "source", "ACP 3 mm, EV3038 Dark Yellow (D-12; hardware selection A1)"),
    ("dt_back_t", "3 mm", "mm", "assumption", "back plate in the same 3 mm ACP"),
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
    ("stop_h", "ps_s + 3 mm", "mm", "assumption", "top stop hangs 18 below DT's underside, past the seal"),
    ("stop_end", "10 mm", "mm", "assumption", "the seal and stop stop 10 short of the catch"),
]

PARTS = {
    "SKIN": ("351201", "FRONT - DECOR SKIN - DT", "Tấm ốp alu khối trên"),
    "BACK": ("351202", "FRONT - DECOR BACK PLATE - DT", "Tấm hậu khối trên"),
    "STOP": ("351203", "FRONT - DOOR TOP STOP - DT", "Nẹp chặn cửa trên"),
    "PS": ("368005", "FRONT - DOOR SEAL - FRAME STOP - ATHMER PS 1515 P FLEX - TOP", "Gioăng chặn cửa trên"),
    "CATCH": ("368007", "FRONT - DOOR CATCH - SUGATSUNE HT-MSG62", "Nam châm hít cửa"),
}

EXPECTED = []


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

    # ---- 351201 skin: the skeleton's DT shape, shelled
    c = comp("SKIN")
    plan = [(XL, YB), (XL, "-dl_y1"), (XL + " + dl_x2 + 4 mm", "-dt_y3"), (XL + " + dt_x2", "-dt_y2"),
            (XL + " + fix_xtr", YF), (XL + " + dt_xr", "-ch_yb"), (XL + " + dt_xr", YB)]
    f = prism(c, ("x", "y"), plan, "z", "dt_zb", "pod_h", "PLAN - DT FACETS (SKELETON)", "EXTRUDE - DT OUTER SHAPE")
    skin = f.bodies.item(0)
    prism(c, ("x", "z"), [(XL, "dt_zb"), (XL + " + dl_w", "dt_zb"), (XL, "dl_zo")], "y", YF, YB,
          "SLOPE - DT BOTTOM OVER DL", "CUT - DT BOTTOM SLOPE", CUT, skin)
    prism(c, ("y", "z"), [(YF, "ch_zlo"), ("-ch_yb", "pod_h"), (YF, "pod_h")], "x", XL, XR,
          "CHAMFER - DT TOP FRONT", "CUT - DT TOP CHAMFER", CUT, skin)
    yb, xj = L.ev(design, YB), L.ev(design, XL + " + dt_xr")
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
    slot = [(L.free_x(ZT + " - 1 mm"), GY + " - gu_prof_w / 2 - slot_clear"),
            (L.diag_x(ZT, "gu_prof_d"), GY + " - gu_prof_w / 2 - slot_clear"),
            (L.diag_x(ZT, "gu_prof_d"), GY + " + gu_prof_w / 2 + slot_clear"),
            (L.free_x(ZT + " - 1 mm"), GY + " + gu_prof_w / 2 + slot_clear")]
    prism(c, ("x", "y"), slot, "z", ZT + " - 1 mm", ZT + " + dt_skin_t + 1 mm",
          "SLOT - FIXED GLASS TOP CHANNEL", "CUT - SKIN SLOT FOR THE TOP CHANNEL", CUT, skin)
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
    f = prism(c, ("x", "z"), back, "y", YB + " - dt_back_t", YB, "OUTLINE - DT BACK PLATE", "EXTRUDE - DT BACK PLATE")
    bodies["BACK"] = f.bodies.item(0)
    bodies["BACK"].name = "DT BACK PLATE ACP 3"

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
    bodies["STOP"] = L.box_body(design, c, "STOP", (x_stop0, x_stop1), (gi + " + stop_gap", gi + " + stop_gap + stop_t"),
                                (ZT + " - stop_h", ZT), "DOOR TOP STOP (ANGLE LEG)")

    acp = L.material(design, "ACP 3 mm PE core EV3038 (1300 kg/m3, calculation)", "Aluminum", 1300.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    for k, m in (("SKIN", acp), ("BACK", acp), ("STOP", alu), ("PS", env), ("CATCH", env)):
        bodies[k].material = m
    looks = {"SKIN": ["Paint - Enamel Glossy (Yellow)"], "BACK": ["Paint - Enamel Glossy (Yellow)"],
             "STOP": ["Paint - Enamel Glossy (Black)"], "PS": ["Plastic - Matte (Black)"],
             "CATCH": ["Plastic - Matte (Black)"]}
    for k, b in bodies.items():
        a = L.appearance(design, looks[k])
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
    print("DT box", L.box(root))
    if bad or loose or bad_clash:
        raise RuntimeError("DT checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))


ANCHORS = [
    ("SKIN", 0, "-pod_w / 2"), ("SKIN", 3, "dt_xr - pod_w / 2"), ("SKIN", 2, "dt_zb"), ("SKIN", 5, "pod_h"),
    ("SKIN", 1, "-pod_d / 2"), ("SKIN", 4, "-pod_d / 2 + decor_d"),
    ("BACK", 3, "dt_xr - pod_w / 2"), ("CATCH", 5, "dt_zb"), ("CATCH", 2, "dt_zb - ca_h"),
    ("PS", 1, "-glass_y + glass_t / 2"), ("STOP", 2, "dt_zb - stop_h"),
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
    seal_len = L.ev(design, "(%s - st_l / 2 - ca_l / 2 - stop_end) - (-pod_w / 2 + door_xl)" % ("(%s - st_end)" % latch_x("leaf_zt")))
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-49; PM rulings 2026-10-31; this build",
         "stage 1: no frame yet (stage 2); goes on after the door hangs (packing plan)"),
        ("351201", PARTS["SKIN"][1], PARTS["SKIN"][2], 1, "made: ACP panels, 45 deg mitred joints as v1",
         "ACP 3 mm EV3038 Dark Yellow, PE core", "cad", "calculation (CAD, 1300 kg/m3)", "DRAFT",
         "D-12, D-49; skeleton DT shape", "panel split and flat patterns: stage 2"),
        ("351202", PARTS["BACK"][1], PARTS["BACK"][2], 1, "made", "ACP 3 mm", "cad", "calculation (CAD)", "DRAFT",
         "this build", "behind it the soffit (D-60)"),
        ("351203", PARTS["STOP"][1], PARTS["STOP"][2], 1, "made (aluminium angle, cut to length)",
         "aluminium EN AW-6063-T6, finish black anodised matte 20 um (AA20)", "cad", "calculation (CAD)", "DRAFT",
         "selection C3 (frame gap 2 to 6)", "screwed to DT's frame: fixings stage 2"),
        ("368005", "FRONT - DOOR SEAL - FRAME STOP - ATHMER PS 1515 P FLEX", "Gioăng chặn cửa", 1,
         "bought by length", "athmer PS 1515 P Flex, PVC co-extrusion, self-adhesive", 0.05, "assumption",
         "source (product)", "hardware selection C3; joints register", "top run %.0f mm (DL's run in DL's list)" % seal_len),
        ("368007", PARTS["CATCH"][1], PARTS["CATCH"][2], 1, "bought", "Sugatsune HT-MSG62: silicone body, SUS304 "
         "bracket, neodymium magnet; finish as supplied", 0.052, "source (Sugatsune datasheet, 52.2 g)",
         "source (product)", "hardware selection C7; PM rulings 2026-10-31",
         "door stop and 35 N catch; its strike 368102 is on the leaf; 3 x M4 x 12 into DT's frame (stage 2)"),
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


SHOTS = [("v2/01-CAD-Native/front/350002_P01_FRONT-DECOR-BLOCK-ASSY-DT-FRONT_IMG.png", "front"),
         ("v2/01-CAD-Native/front/350002_P01_FRONT-DECOR-BLOCK-ASSY-DT-ISO_IMG.png", "iso-top-right")]


def run(_context):
    """step: build | export | post (export, pictures, edit test with --arg edits=...) | all (build, save, post)."""
    app = adsk.core.Application.get()
    step = ARGS.get("step", "build")
    doc = app.activeDocument
    if doc is None or not doc.name.startswith(DOC_NAME):
        raise RuntimeError("active document is %r, not %s: open it with the runner's --doc" % (
            doc.name if doc else None, DOC_NAME))
    L.run_steps(app, ARGS, HERE, step, build, export_all, SHOTS, ANCHORS_REL)
