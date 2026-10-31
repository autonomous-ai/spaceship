"""360002 FRONT - FIXED GLASS UNIT (Cụm vách kính cố định): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/fixed_glass.py \
        --doc 360002_P01_FRONT-FIXED-GLASS-UNIT_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/fixed_glass.py \
        --doc 360002_P01_FRONT-FIXED-GLASS-UNIT_CAD --arg step=export --close

The fixed pane is the skeleton's measured pentagon (v1 body 222), frameless
as in v1 (D-27). Its visible outline is the skeleton's: the left edge faces
the door, the right and diagonal edges follow DR, the top meets DT's
underside and the bottom meets the base band top. On those four edges the
pane runs `fg_bite` (11.5 mm) past the visible line into hidden glazing
channels: the Bohle BO5201571 aluminium U-profile with the BO5201735
silicone U-seal (hardware selection C5, the pick), so no profile shows
(same rule as the door's 25 mm into its kick strip, PM ruling on the FRONT
plan). The channels sit inside DR and DT behind slots in their skins, and in
the base band under the pane: those slots and the channel fixings belong to
the DR, DT and BASE designs. The free left edge carries the 180° glass-to-
glass seal to the door (Bohle BO5281018). That edge runs parallel to the door's latch
edge at the seal's 4 mm (PM ruling 2026-10-31), not on the skeleton's
fix_xbl / fix_xtl line, which gave 2.4 to 3.6 mm.

Fit order (PROPOSED, for the assembly guide): base band with the bottom
channel, then the pane set in it and held, then DR slid in from the right
onto the pane's right edges, then DT lowered onto its top edge.
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
PN = "360002"
NAME = "FRONT - FIXED GLASS UNIT"
VN = "Cụm vách kính cố định"
DOC_NAME = "%s_%s_FRONT-FIXED-GLASS-UNIT_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-FIXED-GLASS-UNIT_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-FIXED-GLASS-UNIT_BOM.csv" % (PN, REV)
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-FIXED-GLASS-UNIT_ANCHORS.json" % (PN, REV)
DXF_GLASS_REL = "v2/03-Manufacturing/front/361003_%s_FRONT-FIXED-GLASS-4-4-LAMINATED_DXF.dxf" % REV

XL, XR = "-pod_w / 2", "pod_w / 2"
GY = "-glass_y"


def door_x(z):
    """X of the door's latch edge line (skeleton door corners) at height z."""
    return "((fg_lc - fg_lnz * (%s)) / fg_lnx)" % z


def left_x(z):
    """X of the pane's free left edge at height z: parallel to the door's latch edge, fg_gap away
    (PM ruling 2026-10-31; replaces the skeleton's fix_xbl / fix_xtl edge, which ran 2.4 to 3.6 mm off)."""
    return "((fg_lc + fg_gap - fg_lnz * (%s)) / fg_lnx)" % z


# Corners of the outline pushed out by d on the bottom, right, diagonal and top edges (the left edge stays).
def BL(d):
    z = "(fg_vis_zb - %s)" % d
    return (left_x(z), z)


def BR(d):
    z = "(fg_vis_zb - %s)" % d
    return ("((fg_rc + %s - fg_rnz * %s) / fg_rnx)" % (d, z), z)


def K(d):
    return ("(((fg_rc + %s) * fg_dnz - (fg_dc + %s) * fg_rnz) / fg_det)" % (d, d),
            "((fg_rnx * (fg_dc + %s) - fg_dnx * (fg_rc + %s)) / fg_det)" % (d, d))


def TR(d):
    z = "(fg_vis_zt + %s)" % d
    return ("((fg_dc + %s - fg_dnz * %s) / fg_dnx)" % (d, z), z)


def TL(d):
    z = "(fg_vis_zt + %s)" % d
    return (left_x(z), z)


def outline(d):
    return [BL(d), BR(d), K(d), TR(d), TL(d)]


def band(d):
    """C-shaped band between the visible outline (offset 0) and offset d, open along the free left edge."""
    return outline("0 mm") + [TL(d), TR(d), K(d), BR(d), BL(d)]


OWN = [
    ("fg_vis_zb", "wall_z0", "mm", "calculation",
     "visible bottom of the pane = the base band top (DR and DL stop there too, PM ruling 2026-10-31)"),
    ("fg_vis_zt", "dt_zb", "mm", "calculation", "visible top of the pane = DT's underside"),
    ("gu_prof_w", "15 mm", "mm", "source", "Bohle BO5201571 aluminium U-profile 15 x 15 x 1.5 (hardware selection C5)"),
    ("gu_prof_d", "15 mm", "mm", "source", "as gu_prof_w"),
    ("gu_prof_t", "1.5 mm", "mm", "source", "as gu_prof_w"),
    ("gu_w", "gu_prof_w - 2 * gu_prof_t", "mm", "calculation", "inner width of the U-profile = the U-seal's outer width"),
    ("gu_base", "2 mm", "mm", "assumption", "U-seal base under the glass edge; HOLD for Bohle's BO5201735 section drawing"),
    ("gu_in_d", "gu_prof_d - gu_prof_t", "mm", "calculation", "inner depth of the U-profile"),
    ("fg_bite", "gu_in_d - gu_base", "mm", "calculation",
     "glass edge cover in the channel: 11.5; HOLD for the glass supplier's minimum"),
    ("fg_gap", "4 mm", "mm", "decided",
     "PM ruling 2026-10-31: the pane's free edge runs parallel to the door's latch edge at the 4 mm the "
     "180 deg seal needs (Bohle BO5281018, 4 mm between 8 mm edges, hardware selection C3)"),
    # door latch edge line (skeleton door corners), unit normal toward the fixed pane
    ("fg_l_len", "sqrt((door_xbr - door_xtr) * (door_xbr - door_xtr) + (door_zt - door_zb) * (door_zt - door_zb))",
     "mm", "calculation", "length of the door's latch edge"),
    ("fg_lnx", "(door_zt - door_zb) / fg_l_len", "", "calculation", "door latch edge normal toward the pane, X"),
    ("fg_lnz", "(door_xbr - door_xtr) / fg_l_len", "", "calculation", "door latch edge normal toward the pane, Z"),
    ("fg_lc", "fg_lnx * (%s + door_xbr) + fg_lnz * door_zb" % XL, "mm", "calculation", "door latch edge line constant"),
    # right edge line (skeleton bottom-right corner to the knee) and diagonal (knee to top-right), unit outward normals
    ("fg_r_len", "sqrt((fix_xbr - fix_xk) * (fix_xbr - fix_xk) + (fix_zk - fix_zb) * (fix_zk - fix_zb))", "mm",
     "calculation", "length of the skeleton's right edge"),
    ("fg_rnx", "(fix_zk - fix_zb) / fg_r_len", "", "calculation", "right edge outward normal, X"),
    ("fg_rnz", "(fix_xk - fix_xbr) / fg_r_len", "", "calculation", "right edge outward normal, Z"),
    ("fg_rc", "fg_rnx * (%s - fix_xbr) + fg_rnz * fix_zb" % XR, "mm", "calculation", "right edge line constant"),
    ("fg_d_len", "sqrt((pod_w - fix_xtr - fix_xk) * (pod_w - fix_xtr - fix_xk) + (fix_zt - fix_zk) * (fix_zt - fix_zk))",
     "mm", "calculation", "length of the skeleton's diagonal edge"),
    ("fg_dnx", "(fix_zt - fix_zk) / fg_d_len", "", "calculation", "diagonal edge outward normal, X"),
    ("fg_dnz", "(pod_w - fix_xtr - fix_xk) / fg_d_len", "", "calculation", "diagonal edge outward normal, Z"),
    ("fg_dc", "fg_dnx * (%s - fix_xk) + fg_dnz * fix_zk" % XR, "mm", "calculation", "diagonal edge line constant"),
    ("fg_det", "fg_rnx * fg_dnz - fg_rnz * fg_dnx", "", "calculation", "for the knee corner"),
]

PARTS = {
    "GLASS": ("361003", "FRONT - FIXED GLASS - 4+4 LAMINATED", "Tấm kính cố định 4+4"),
    "UPROF": ("368004", "FRONT - GLAZING U-PROFILE - BOHLE BO5201571", "Thanh U nhôm kẹp kính"),
    "USEAL": ("368002", "FRONT - GLAZING U-SEAL - BOHLE BO5201735", "Gioăng chữ U silicone"),
    "S180": ("368003", "FRONT - GLASS-TO-GLASS SEAL 180 - BOHLE BO5281018", "Gioăng kính-kính 180°"),
}

EXPECTED = []

ANCHORS = [
    ("GLASS", 2, "fg_vis_zb - fg_bite"), ("GLASS", 5, "fg_vis_zt + fg_bite"),
    ("GLASS", 1, GY + " - glass_t / 2"), ("GLASS", 4, GY + " + glass_t / 2"),
    ("GLASS", 3, "(fg_rc + fg_bite - fg_rnz * (fg_vis_zb - fg_bite)) / fg_rnx"),
    ("UPROF", 2, "fg_vis_zb - gu_prof_d"), ("UPROF", 5, "fg_vis_zt + gu_prof_d"),
    ("UPROF", 1, GY + " - gu_prof_w / 2"), ("UPROF", 4, GY + " + gu_prof_w / 2"),
    ("UPROF", 3, "(fg_rc + gu_prof_d - fg_rnz * (fg_vis_zb - gu_prof_d)) / fg_rnx"),
    ("USEAL", 2, "fg_vis_zb - gu_in_d"), ("USEAL", 5, "fg_vis_zt + gu_in_d"),
    ("USEAL", 1, GY + " - gu_w / 2"), ("USEAL", 4, GY + " + gu_w / 2"),
    ("S180", 2, "fg_vis_zb"), ("S180", 5, "fg_vis_zt"),
]


def build(app):
    design = L.start_design(app, PN, "%s | %s | %s" % (NAME, VN, REV))
    sk_params, sk_path, sk_rev = L.load_skeleton_params(ARGS["repo_root"])
    L.add_params(design, sk_params)
    L.add_params(design, L.LIB_PARAMS)
    L.add_params(design, OWN)
    root = design.rootComponent
    comps, bodies = {}, {}
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(root, pn, nm, vn, REV)
        comps[key] = c
        return c

    def slab(c, pts, y0, y1, sketch, feat, op=NEW, body=None):
        sk = L.poly(design, c, c.xZConstructionPlane, ("x", "z"), 0, sketch, pts)
        return L.extrude_span(c, sk, "y", y0, y1, op, [body] if body else None, feat)

    # 361003 the pane: the skeleton pentagon pushed fg_bite into the four channels
    c = comp("GLASS")
    f = slab(c, outline("fg_bite"), GY + " - glass_t / 2", GY + " + glass_t / 2",
             "OUTLINE - FIXED GLASS (SKELETON PENTAGON + BITE ON 4 EDGES)", "EXTRUDE - FIXED GLASS 8.76")
    bodies["GLASS"] = f.bodies.item(0)
    bodies["GLASS"].name = "FIXED GLASS 4+4"

    # 368004 U-profile: a 15 mm band round the four held edges, then the 12 x 13.5 channel cut out of it
    c = comp("UPROF")
    f = slab(c, band("gu_prof_d"), GY + " - gu_prof_w / 2", GY + " + gu_prof_w / 2",
             "BAND - U-PROFILE OUTER (4 EDGES, MITRED)", "EXTRUDE - U-PROFILE BAR")
    b = f.bodies.item(0)
    slab(c, band("gu_in_d"), GY + " - gu_w / 2", GY + " + gu_w / 2",
         "BAND - U-PROFILE CHANNEL", "CUT - U-PROFILE CHANNEL 12 X 13.5", CUT, b)
    b.name = "GLAZING U-PROFILE (4 PIECES, MITRED)"
    bodies["UPROF"] = b

    # 368002 silicone U-seal: fills the channel, less the glass edge
    c = comp("USEAL")
    f = slab(c, band("gu_in_d"), GY + " - gu_w / 2", GY + " + gu_w / 2",
             "BAND - U-SEAL OUTER", "EXTRUDE - U-SEAL")
    b = f.bodies.item(0)
    slab(c, band("fg_bite"), GY + " - glass_t / 2", GY + " + glass_t / 2",
         "BAND - U-SEAL GLASS SLOT", "CUT - U-SEAL GLASS SLOT", CUT, b)
    b.name = "GLAZING U-SEAL (4 PIECES)"
    bodies["USEAL"] = b

    # 368003 180 deg seal: fills the 4 mm gap between the door's latch edge and the pane's free edge
    c = comp("S180")
    lb, lt = BL("0 mm"), TL("0 mm")
    pts = [lb, lt, (door_x(lt[1]), lt[1]), (door_x(lb[1]), lb[1])]
    f = slab(c, pts, GY + " - glass_t / 2 - 1.5 mm", GY + " + glass_t / 2 + 1.5 mm",
             "OUTLINE - 180 SEAL SPACE ON THE FREE EDGE", "EXTRUDE - 180 SEAL SPACE")
    bodies["S180"] = f.bodies.item(0)
    bodies["S180"].name = "180 SEAL ENVELOPE (THE 4 MM GAP)"

    glass = L.material(design, "Glass 4+4 laminated (2376 kg/m3, calculation)", "Glass", 2376.0)
    alu = L.material(design, "Aluminium (2700 kg/m3)", "Aluminum", 2700.0)
    sil = L.material(design, "Silicone rubber (1200 kg/m3, assumption)", "Rubber, Silicone", 1200.0)
    env = L.material(design, "ENVELOPE - mass carried in the parts list (1 kg/m3)", "Aluminum", 1.0)
    for k, m in (("GLASS", glass), ("UPROF", alu), ("USEAL", sil), ("S180", env)):
        bodies[k].material = m
    looks = {"GLASS": ["Glass - Smoked", "Glass (Smoked)", "Glass - Window", "Glass"],
             "UPROF": ["Aluminum - Anodized Glossy (Black)", "Paint - Enamel Glossy (Black)"],
             "USEAL": ["Rubber - Soft (Black)", "Plastic - Matte (Black)"],
             "S180": ["Plastic - Matte (Grey)", "Paint - Enamel Glossy (Grey)"]}
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
        print("BODY|%s|%s|%g x %g x %g|%s|%.1f cm3" % (k, b.name, round(bb[3] - bb[0], 2), round(bb[4] - bb[1], 2),
                                                      round(bb[5] - bb[2], 2), bb, b.volume))
    print("clash pairs %d, unexpected %d" % (len(hits), len(bad_clash)))
    for a, b, v in hits:
        print("CLASH|%s|%s|%d mm3" % (a, b, v))
    for key in ("GLASS", "UPROF", "USEAL"):
        print("MASS|%s|%s|%.3f kg" % (key, PARTS[key][0], L.comp_mass(comps[key])))
    for name in ("fg_bite", "fg_rnx", "fg_rnz", "fg_dnx", "fg_dnz", "fg_vis_zb", "fg_vis_zt"):
        print("PARAM|%s|%.4f" % (name, L.ev(design, name) if name.startswith("fg_v") or name == "fg_bite"
                                 else design.userParameters.itemByName(name).value))
    # gap to the door's latch edge, horizontal and square to the edge, for the 180 deg seal
    for z in ("fg_vis_zb", "(fg_vis_zb + fg_vis_zt) / 2", "door_zt"):
        h = L.ev(design, left_x(z)) - L.ev(design, door_x(z))
        print("GAP|z %s|%.2f mm horizontal, %.2f mm square to the edge" % (
            z, h, h * design.userParameters.itemByName("fg_lnx").value))
    if bad or loose or bad_clash:
        raise RuntimeError("fixed glass checks failed (unhealthy %s, loose %s, clashes %s)" % (bad, loose, bad_clash))


def edge_lengths(design, d):
    """Lengths of the four held edges at offset d (bottom, right, diagonal, top), mm."""
    pts = [tuple(L.ev(design, e) for e in p) for p in outline(d)]
    import math
    seg = [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[3]), (pts[3], pts[4])]
    return [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in seg]


def export_all(app):
    design = adsk.fusion.Design.cast(app.activeProduct)
    doc = app.activeDocument
    L.ensure_saved_part_number(doc, design, PN)
    root_dir = ARGS["repo_root"]
    f3d = L.export(design, root_dir, F3D_REL, "f3d")
    step = L.export(design, root_dir, STEP_REL, "step")
    print("export %s: %d bytes" % (F3D_REL, os.path.getsize(f3d)))
    print("export %s: %d bytes" % (STEP_REL, os.path.getsize(step)))
    # pane DXF, front view from outside: X(dxf) = X(pod) - leftmost X of the pane, Y(dxf) = Z(pod) - its bottom
    pts = [tuple(L.ev(design, e) for e in p) for p in outline("fg_bite")]
    x0, z0 = min(p[0] for p in pts), min(p[1] for p in pts)
    L.write_dxf_polyline(os.path.join(root_dir, DXF_GLASS_REL), [[(x - x0, z - z0) for x, z in pts]])
    print("DXF pane corners:", [(round(x - x0, 2), round(z - z0, 2)) for x, z in pts])
    outer = edge_lengths(design, "gu_prof_d")
    mouth = edge_lengths(design, "0 mm")
    print("U-profile cut lengths, long point (outer) / short point (mouth): %s / %s mm" % (
        [round(v, 1) for v in outer], [round(v, 1) for v in mouth]))
    seal_len = sum(edge_lengths(design, "gu_in_d"))
    free_len = L.ev(design, "sqrt((%s - %s) * (%s - %s) + (fg_vis_zt - fg_vis_zb) * (fg_vis_zt - fg_vis_zb))" % (
        TL("0 mm")[0], BL("0 mm")[0], TL("0 mm")[0], BL("0 mm")[0]))
    rows = [
        (PN, NAME, VN, 1, "assembly", "-", None, "", "DRAFT", "D-27, D-46; this build",
         "fit order PROPOSED: band channel, pane, DR, DT"),
        ("361003", PARTS["GLASS"][1], PARTS["GLASS"][2], 1, "made to drawing (glass supplier)",
         "4+4 laminated glass of toughened, heat-soaked panes, 8.76, grey", "cad", "calculation (CAD, 2376 kg/m3)",
         "DRAFT; product HOLD (ISS-074)", "D-27, D-46; skeleton outline (v1 STEP body 222)",
         "visible outline = skeleton; +fg_bite on the 4 held edges; no holes"),
        ("368004", PARTS["UPROF"][1], PARTS["UPROF"][2], 1, "bought by length, 4 pieces mitred",
         "Bohle BO5201571 aluminium U-profile 15 x 15 x 1.5", "cad", "calculation (CAD, 2700 kg/m3)",
         "source (product)", "hardware selection C5",
         "outer lengths %s mm (bottom, right, diagonal, top)" % " / ".join("%.0f" % v for v in outer)),
        ("368002", PARTS["USEAL"][1], PARTS["USEAL"][2], 1, "bought by length, 4 pieces",
         "Bohle BO5201735 silicone U-profile seal", "cad", "calculation (CAD, 1200 kg/m3 assumption)",
         "source (product); fit on 8.76 laminate unverified", "hardware selection C5",
         "about %.0f mm in all" % seal_len),
        ("368003", PARTS["S180"][1], PARTS["S180"][2], 1, "bought, cut to length", "Bohle BO5281018, clear PVC", 0.2,
         "assumption", "HOLD: fit on the 8.76 laminate unverified; no dB data (the 4 mm gap is now designed in)",
         "hardware selection C3", "length about %.0f mm on the pane's free edge" % free_len),
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
