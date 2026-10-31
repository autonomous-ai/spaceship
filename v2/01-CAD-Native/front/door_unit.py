"""360001 FRONT - DOOR UNIT (Cụm cửa kính): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py \
        --doc 360001_P01_FRONT-DOOR-UNIT_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py \
        --doc 360001_P01_FRONT-DOOR-UNIT_CAD --arg step=export --close

step=build (default) empties the active design (it must be this unit's
document) and builds it; step=export writes the .f3d, STEP, DXF, parts list
and the edit-test anchors from the saved version.

The door unit hangs as one factory-fitted piece (D-56): the 4+4 leaf, the
85 mm aluminium kick strip with the drop seal (D-40, D-57), and the hinges,
lock and pull. The hinges, lock and pull are HOLD (D-46): they are reserved
spaces only, and the glass gets no holes or cut-outs for them until a rated
set is named (PM ruling on the FRONT plan). The glass runs 25 mm down into the
kick strip and the strip keeps a 7 mm floor gap (PM ruling on the FRONT
plan, 2026-10-31). The door opens outward (open-questions Q3, ISS-055).

Every size comes from the skeleton's parameter list (front_lib), so the leaf
is the skeleton's measured trapezoid and moves with it.
"""

import csv
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
PN = "360001"
NAME = "FRONT - DOOR UNIT"
VN = "Cụm cửa kính"
DOC_NAME = "%s_%s_FRONT-DOOR-UNIT_CAD" % (PN, REV)
F3D_REL = "v2/01-CAD-Native/front/%s.f3d" % DOC_NAME
STEP_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DOOR-UNIT_STEP.step" % (PN, REV)
BOM_REL = "v2/03-Manufacturing/front/%s_%s_FRONT-DOOR-UNIT_BOM.csv" % (PN, REV)
ANCHORS_REL = "v2/01-CAD-Native/front/%s_%s_FRONT-DOOR-UNIT_ANCHORS.json" % (PN, REV)
DXF_LEAF_REL = "v2/03-Manufacturing/front/361001_%s_FRONT-DOOR-LEAF-4-4-LAMINATED_DXF.dxf" % REV
DXF_KICK_REL = "v2/03-Manufacturing/front/361002_%s_FRONT-DOOR-KICK-STRIP_DXF.dxf" % REV

XL = "-pod_w / 2"
GY0, GY1 = "-glass_y - glass_t / 2", "-glass_y + glass_t / 2"     # glass faces: outside, pod side
KY0, KY1 = "-glass_y - kick_d / 2", "-glass_y + kick_d / 2"       # kick strip faces
UY0, UY1 = "-glass_y - gu_w / 2", "-glass_y + gu_w / 2"           # glazing pocket and seal cavity walls


def latch_x(z):
    """X of the leaf's slanted latch edge at height z (expression)."""
    return "(%s + door_xbr - (door_xbr - door_xtr) * ((%s) - door_zb) / (door_zt - door_zb))" % (XL, z)


# name, expression, unit, status, source. The skeleton's own list is loaded first.
OWN = [
    ("door_glass_engage", "25 mm", "mm", "decided",
     "PM ruling on the FRONT plan, 2026-10-31: the glass runs 25 mm down into the kick strip, so the visible "
     "glass bottom stays at the skeleton's door_zb"),
    ("kick_floor_gap", "7 mm", "mm", "decided",
     "PM ruling on the FRONT plan, 2026-10-31: the drop seal's rated floor gap (athmer Schall-Ex GSA, 51 dB "
     "joint at a 7 mm gap; hardware selection C4)"),
    ("kick_x0", XL + " + door_xl", "mm", "calculation", "strip end and leaf hinge edge = the skeleton door's left edge"),
    ("kick_x1", XL + " + door_xbr", "mm", "calculation",
     "strip end under the latch edge = the skeleton door's bottom-right corner"),
    ("kick_zb", "thresh_h + kick_floor_gap", "mm", "calculation", "strip bottom = threshold top + floor gap"),
    ("kick_h", "door_zb - kick_zb", "mm", "calculation", "strip height: 78 on skeleton P03"),
    ("kick_len", "kick_x1 - kick_x0", "mm", "calculation", "cut length of the strip and the drop seal"),
    ("gu_w", "12 mm", "mm", "source",
     "glazing pocket = inner width of the Bohle BO5201571 U-profile 15 x 15 x 1.5 (15 - 2 x 1.5), the channel "
     "the BO5201735 silicone U-seal is made for (hardware selection C5)"),
    ("gu_base", "2 mm", "mm", "assumption", "U-seal base under the glass edge; HOLD for Bohle's BO5201735 section drawing"),
    ("kick_pocket_d", "door_glass_engage + gu_base", "mm", "calculation", "glazing pocket depth"),
    ("kick_wall", "(kick_d - gu_w) / 2", "mm", "calculation",
     "strip side walls: 4 with the skeleton's 20 mm kick_d, machined from 20 x 80 flat bar"),
    ("kick_web", "3 mm", "mm", "assumption", "web between the glazing pocket and the drop-seal cavity"),
    ("kick_cav_h", "kick_h - kick_pocket_d - kick_web", "mm", "calculation", "drop-seal cavity height; must hold gsa_h"),
    ("gsa_t", "11.6 mm", "mm", "source", "athmer Schall-Ex GSA 1-1112 section 11.6 x 40 (hardware selection C4)"),
    ("gsa_h", "40 mm", "mm", "source", "athmer Schall-Ex GSA 1-1112 section 11.6 x 40 (hardware selection C4)"),
    ("hinge_clamp_h", "120 mm", "mm", "assumption", "reserved height per hinge on the glass; HOLD H01 until a rated hinge is named"),
    ("hinge_clamp_w", "100 mm", "mm", "assumption", "reserved width on the glass from its hinge edge; HOLD H01"),
    ("hinge_clamp_t", "40 mm", "mm", "assumption", "reserved thickness across the glass; HOLD H01"),
    ("hinge_pocket_d", "160 mm", "mm", "source",
     "the HOLD candidate dormakaba OFFICE 11.233 needs a 160 mm frame pocket in DL (D-30, D-46; selection C1)"),
    ("hinge_x0", XL + " + dl_w - hinge_pocket_d", "mm", "calculation", "inner end of the hinge pocket in DL (DL door face at XL + dl_w)"),
    ("hinge_z1", "door_zb + 250 mm", "mm", "assumption", "bottom hinge centre 250 above the visible glass bottom; HOLD H01"),
    ("hinge_z3", "door_zt - 250 mm", "mm", "assumption", "top hinge centre 250 below the glass top; HOLD H01"),
    ("hinge_z2", "(hinge_z1 + hinge_z3) / 2", "mm", "assumption", "middle hinge at mid-span; HOLD H01"),
    ("lock_zc", "floor_t + 1050 mm", "mm", "assumption",
     "lock and pull centre 1050 above the finished floor (usual door handle height); HOLD H02"),
    ("lock_h", "159 mm", "mm", "source",
     "reserved space = the HOLD candidate's body, dormakaba STUDIO Rondo 10.200, 159 x 65 (selection C7)"),
    ("lock_w", "65 mm", "mm", "source", "as lock_h"),
    ("lock_t", "40 mm", "mm", "assumption", "reserved thickness across the glass; HOLD H02"),
    ("lock_x1", latch_x("lock_zc + lock_h / 2"), "mm", "calculation",
     "the lock space ends at the latch edge's X at its top corner, so it never passes the edge"),
    ("pull_cc", "300 mm", "mm", "source", "HOLD candidate Häfele 903.10.390 pull pair, 300 mm centres, Ø19 (selection C2)"),
    ("pull_len", "pull_cc + 60 mm", "mm", "assumption", "bar 30 mm past each fixing"),
    ("pull_w", "40 mm", "mm", "assumption", "reserved width: the Ø19 bar and its fixing roses"),
    ("pull_stand", "70 mm", "mm", "assumption", "reserved projection from each glass face"),
    ("pull_back", "100 mm", "mm", "assumption", "pull axis 100 mm in from the latch edge, clear of the lock space"),
    ("pull_zc", "lock_zc", "mm", "assumption", "pull centred at the lock height"),
    ("pull_x", latch_x("pull_zc + pull_len / 2") + " - pull_back", "mm", "calculation",
     "pull axis X, measured from the latch edge at the bar's top end"),
]

# key: part number, component name, Vietnamese name
PARTS = {
    "LEAF": ("361001", "FRONT - DOOR LEAF - 4+4 LAMINATED", "Tấm kính cửa 4+4"),
    "KICK": ("361002", "FRONT - DOOR KICK STRIP", "Thanh chân cửa nhôm"),
    "GSA": ("368001", "FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112", "Ron chân cửa tự động"),
    "USEAL": ("368002", "FRONT - GLAZING U-SEAL - BOHLE BO5201735", "Gioăng chữ U silicone"),
    "H1": ("368101", "FRONT - DOOR HINGE - HOLD - H1 BOTTOM", "Bản lề cửa dưới (chờ chọn)"),
    "H2": ("368101", "FRONT - DOOR HINGE - HOLD - H2 MIDDLE", "Bản lề cửa giữa (chờ chọn)"),
    "H3": ("368101", "FRONT - DOOR HINGE - HOLD - H3 TOP", "Bản lề cửa trên (chờ chọn)"),
    "LOCK": ("368102", "FRONT - DOOR LOCK - HOLD", "Khóa cửa (chờ chọn)"),
    "PULL": ("368103", "FRONT - DOOR PULL PAIR - HOLD", "Tay nắm cửa (chờ chọn)"),
}

# Overlaps made on purpose, with the reason; any other clash over 1 mm3 fails the build.
EXPECTED = [
    (("H1", "LEAF"), "HOLD hinge space wraps the leaf's hinge edge: the named hinge will clamp the glass there"),
    (("H2", "LEAF"), "as H1"),
    (("H3", "LEAF"), "as H1"),
    (("LOCK", "LEAF"), "HOLD lock space wraps the leaf at the latch edge: a glass lock clamps the leaf"),
]

# Edit-test anchors: (key, bounding-box index 0..5 = xmin ymin zmin xmax ymax zmax, expression).
ANCHORS = [
    ("LEAF", 0, "kick_x0"), ("LEAF", 3, "kick_x1"), ("LEAF", 2, "door_zb - door_glass_engage"),
    ("LEAF", 5, "door_zt"), ("LEAF", 1, GY0), ("LEAF", 4, GY1),
    ("KICK", 0, "kick_x0"), ("KICK", 3, "kick_x1"), ("KICK", 2, "kick_zb"), ("KICK", 5, "door_zb"),
    ("KICK", 1, KY0), ("KICK", 4, KY1),
    ("USEAL", 2, "door_zb - kick_pocket_d"), ("USEAL", 5, "door_zb"), ("USEAL", 1, UY0), ("USEAL", 4, UY1),
    ("GSA", 2, "kick_zb"), ("GSA", 5, "kick_zb + gsa_h"), ("GSA", 4, UY1), ("GSA", 3, "kick_x1"),
    ("H1", 2, "hinge_z1 - hinge_clamp_h / 2"), ("H3", 5, "hinge_z3 + hinge_clamp_h / 2"),
    ("H2", 0, "hinge_x0"), ("H2", 3, "kick_x0 + hinge_clamp_w"),
    ("LOCK", 3, "lock_x1"), ("LOCK", 2, "lock_zc - lock_h / 2"),
    ("PULL", 1, GY0 + " - pull_stand"), ("PULL", 4, GY1 + " + pull_stand"), ("PULL", 5, "pull_zc + pull_len / 2"),
]

ENVELOPE_MAT = "ENVELOPE - mass carried in the parts list (1 kg/m3)"


def build(app):
    design = L.start_design(app, PN, "%s | %s | %s" % (NAME, VN, REV))
    sk_params, sk_path, sk_rev = L.load_skeleton_params(ARGS["repo_root"])
    L.add_params(design, sk_params)
    L.add_params(design, L.LIB_PARAMS)
    L.add_params(design, OWN)
    root = design.rootComponent
    for name, expr in (("kick_cav_h", "gsa_h"),):
        if L.ev(design, name) < L.ev(design, expr):
            raise RuntimeError("%s (%.1f) is smaller than %s (%.1f)" % (name, L.ev(design, name), expr, L.ev(design, expr)))
    comps, bodies = {}, {}

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(root, pn, nm, vn, REV)
        comps[key] = c
        return c

    # 361001 leaf: the skeleton's trapezoid, extended 25 mm down into the strip with a vertical latch-side
    # end (the extension sits inside the strip, so the visible outline is the skeleton's).
    c = comp("LEAF")
    bodies["LEAF"] = L.prism(design, c, "LEAF", ("x", "z"), [
        ("kick_x0", "door_zb - door_glass_engage"), ("kick_x1", "door_zb - door_glass_engage"),
        ("kick_x1", "door_zb"), (XL + " + door_xtr", "door_zt"), ("kick_x0", "door_zt")],
        "y", GY0, GY1, "DOOR LEAF GLASS 4+4", "OUTLINE - DOOR LEAF (SKELETON TRAPEZOID + 25 MM INTO THE KICK STRIP)",
        "EXTRUDE - DOOR LEAF 8.76")

    # 361002 kick strip: H section, glazing pocket on top, drop-seal cavity below, extruded along the door
    c = comp("KICK")
    bodies["KICK"] = L.prism(design, c, "KICK", ("y", "z"), [
        (KY0, "kick_zb"), (UY0, "kick_zb"), (UY0, "kick_zb + kick_cav_h"), (UY1, "kick_zb + kick_cav_h"),
        (UY1, "kick_zb"), (KY1, "kick_zb"), (KY1, "door_zb"), (UY1, "door_zb"),
        (UY1, "door_zb - kick_pocket_d"), (UY0, "door_zb - kick_pocket_d"), (UY0, "door_zb"), (KY0, "door_zb")],
        "x", "kick_x0", "kick_x1", "KICK STRIP", "SECTION - KICK STRIP (H: GLAZING POCKET OVER DROP-SEAL CAVITY)",
        "EXTRUDE - KICK STRIP LENGTH")

    # 368002 silicone U-seal round the glass edge in the pocket
    c = comp("USEAL")
    bodies["USEAL"] = L.prism(design, c, "USEAL", ("y", "z"), [
        (UY0, "door_zb - kick_pocket_d"), (UY1, "door_zb - kick_pocket_d"), (UY1, "door_zb"), (GY1, "door_zb"),
        (GY1, "door_zb - door_glass_engage"), (GY0, "door_zb - door_glass_engage"), (GY0, "door_zb"),
        (UY0, "door_zb")],
        "x", "kick_x0", "kick_x1", "GLAZING U-SEAL", "SECTION - GLAZING U-SEAL", "EXTRUDE - GLAZING U-SEAL LENGTH")

    # 368001 drop seal: catalogue section, bonded to the pod-side wall of the cavity, flush with the strip bottom
    c = comp("GSA")
    bodies["GSA"] = L.prism(design, c, "GSA", ("y", "z"), [
        (UY1 + " - gsa_t", "kick_zb"), (UY1, "kick_zb"), (UY1, "kick_zb + gsa_h"), (UY1 + " - gsa_t", "kick_zb + gsa_h")],
        "x", "kick_x0", "kick_x1", "DROP SEAL ENVELOPE (CATALOGUE SECTION)", "SECTION - DROP SEAL GSA 11.6 X 40",
        "EXTRUDE - DROP SEAL CUT LENGTH")

    # HOLD spaces: hinges (into the DL pocket), lock and pull. No holes in the glass for them.
    for key, zc in (("H1", "hinge_z1"), ("H2", "hinge_z2"), ("H3", "hinge_z3")):
        c = comp(key)
        bodies[key] = L.box_body(design, c, key, ("hinge_x0", "kick_x0 + hinge_clamp_w"),
                                 ("-glass_y - hinge_clamp_t / 2", "-glass_y + hinge_clamp_t / 2"),
                                 ("%s - hinge_clamp_h / 2" % zc, "%s + hinge_clamp_h / 2" % zc),
                                 "HOLD HINGE SPACE " + key, "PLAN - HOLD HINGE SPACE " + key)
    c = comp("LOCK")
    bodies["LOCK"] = L.box_body(design, c, "LOCK", ("lock_x1 - lock_w", "lock_x1"),
                                ("-glass_y - lock_t / 2", "-glass_y + lock_t / 2"),
                                ("lock_zc - lock_h / 2", "lock_zc + lock_h / 2"), "HOLD LOCK SPACE")
    c = comp("PULL")
    out = L.box_body(design, c, "PULL-OUT", ("pull_x - pull_w / 2", "pull_x + pull_w / 2"),
                     (GY0 + " - pull_stand", GY0), ("pull_zc - pull_len / 2", "pull_zc + pull_len / 2"),
                     "HOLD PULL SPACE - OUTSIDE")
    ins = L.box_body(design, c, "PULL-IN", ("pull_x - pull_w / 2", "pull_x + pull_w / 2"),
                     (GY1, GY1 + " + pull_stand"), ("pull_zc - pull_len / 2", "pull_zc + pull_len / 2"),
                     "HOLD PULL SPACE - POD SIDE")
    bodies["PULL"] = out
    bodies["PULL-IN"] = ins

    # materials and looks
    glass = L.material(design, "Glass 4+4 laminated (2376 kg/m3, calculation)", "Glass", 2376.0)
    alu = L.material(design, "Aluminium EN AW-6082-T6 (2700 kg/m3)", "Aluminum", 2700.0)
    sil = L.material(design, "Silicone rubber (1200 kg/m3, assumption)", "Rubber, Silicone", 1200.0)
    env = L.material(design, ENVELOPE_MAT, "Aluminum", 1.0)
    bodies["LEAF"].material = glass
    bodies["KICK"].material = alu
    bodies["USEAL"].material = sil
    for k in ("GSA", "H1", "H2", "H3", "LOCK", "PULL", "PULL-IN"):
        bodies[k].material = env
    looks = {"LEAF": ["Glass - Smoked", "Glass (Smoked)", "Glass - Window", "Glass"],
             "KICK": ["Paint - Enamel Glossy (Black)", "Aluminum - Anodized Glossy (Black)", "Plastic - Matte (Black)"],
             "USEAL": ["Rubber - Soft (Black)", "Plastic - Matte (Black)"],
             "GSA": ["Plastic - Matte (Grey)", "Paint - Enamel Glossy (Grey)"],
             "HOLD": ["Paint - Enamel Glossy (Red)", "Plastic - Glossy (Red)"]}
    for k, b in bodies.items():
        a = L.appearance(design, looks["HOLD" if k[0] in "HLP" and k not in ("LEAF",) else k])
        if a:
            b.appearance = a

    # checks
    n_tl, bad, loose = L.health(design)
    hits, bad_clash = L.clash_check(bodies, EXPECTED)
    print("skeleton parameters: %s (%s), %d loaded" % (os.path.relpath(sk_path, ARGS["repo_root"]), sk_rev, len(sk_params)))
    print("bodies %d, timeline %d items, unhealthy %d, loose sketches %d, parameters %d" % (
        len(bodies), n_tl, len(bad), len(loose), design.userParameters.count))
    for k, b in bodies.items():
        bb = L.box(b)
        print("BODY|%s|%s|%g x %g x %g|%s" % (k, b.name, round(bb[3] - bb[0], 2), round(bb[4] - bb[1], 2),
                                              round(bb[5] - bb[2], 2), bb))
    print("clash pairs %d, expected %d, unexpected %d" % (len(hits), len(hits) - len(bad_clash), len(bad_clash)))
    for a, b, v in hits:
        print("CLASH|%s|%s|%d mm3|%s" % (a, b, v, "UNEXPECTED" if (a, b, v) in bad_clash else "listed"))
    hit_set = {frozenset((a, b)) for a, b, _v in hits}
    missing = [k for k, _r in EXPECTED if frozenset(k) not in hit_set]
    print("listed pairs that do not clash:", missing)
    for key in ("LEAF", "KICK", "USEAL"):
        print("MASS|%s|%s|%.3f kg" % (key, PARTS[key][0], L.comp_mass(comps[key])))
    print("unit box", L.box(root))
    for name in ("kick_h", "kick_len", "kick_cav_h", "kick_wall", "lock_x1", "pull_x", "hinge_z1", "hinge_z2", "hinge_z3"):
        print("PARAM|%s|%.2f" % (name, L.ev(design, name)))
    if bad or loose or bad_clash or missing:
        raise RuntimeError("door unit checks failed (unhealthy %s, loose %s, clashes %s, missing %s)" % (
            bad, loose, bad_clash, missing))


# ---------------------------------------------------------------- export

def outline_mm(design, sketch_name, comp_name, axes):
    """Corner points (mm) of a polygon sketch, in model coordinates along `axes`, in loop order."""
    comp = [c for c in design.allComponents if c.name == comp_name][0]
    sk = comp.sketches.itemByName(sketch_name)
    lines = [sk.sketchCurves.sketchLines.item(i) for i in range(sk.sketchCurves.sketchLines.count)]
    pts = []
    for ln in lines:
        p = sk.sketchToModelSpace(ln.startSketchPoint.geometry)
        pts.append(tuple(round(getattr(p, a) * 10.0, 4) for a in axes))
    return pts


BOM_ROWS = [
    # pn, name, Vietnamese name, qty, type, material, mass kg ("cad" = from the model), mass status, status, source, note
    ("360001", NAME, VN, 1, "assembly, fitted at the factory (D-56)", "-", None, "", "DRAFT",
     "D-46, D-56; this build", "hangs as one unit on the HOLD hinges"),
    ("361001", "FRONT - DOOR LEAF - 4+4 LAMINATED", "Tấm kính cửa 4+4", 1, "made to drawing (glass supplier)", "4+4 laminated glass of toughened, heat-soaked panes, 8.76, grey",
     "cad", "calculation (CAD, 2376 kg/m3)", "DRAFT; product HOLD (ISS-074)", "D-27, D-46; skeleton outline (v1 STEP)",
     "no holes or cut-outs until the hinges, lock and pull are named"),
    ("361002", "FRONT - DOOR KICK STRIP", "Thanh chân cửa nhôm", 1, "made (machined from 20 x 80 flat bar)", "aluminium EN AW-6082-T6, finish to match the base band",
     "cad", "calculation (CAD, 2700 kg/m3)", "DRAFT", "D-40, D-57; PM rulings on the FRONT plan",
     "cut length = kick_len; glass retention in the pocket HOLD (J-FRONT-02)"),
    ("368001", "FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112", "Ron chân cửa tự động", 1, "bought, cut to length", "athmer Schall-Ex GSA 1-1112, black RAL 9005", 0.6,
     "assumption (D-56)", "source (product); bond to aluminium HOLD", "hardware selection C4", "cut from 1208 to kick_len"),
    ("368002", "FRONT - GLAZING U-SEAL - BOHLE BO5201735", "Gioăng chữ U silicone", 1, "bought by length", "Bohle BO5201735 silicone U-profile seal", "cad",
     "calculation (CAD, 1200 kg/m3 assumption)", "source (product); fit on 8.76 laminate unverified",
     "hardware selection C5", "length = kick_len"),
    ("368101", "FRONT - DOOR HINGE - HOLD", "Bản lề cửa (chờ chọn)", 3, "bought, HOLD",
     "not named: the set must be rated for the 8.76 laminate, at least 60 kg (PM ruling: the 50.2 kg unit plus a "
     "margin) and the 1176 mm width", 0.6, "assumption (D-56)", "HOLD (D-46, ISS-002)", "hardware selection C1",
     "reserved space only"),
    ("368102", "FRONT - DOOR LOCK - HOLD", "Khóa cửa (chờ chọn)", 1, "bought, HOLD",
     "not named: rated with the hinges for at least 60 kg and the 1176 mm width (PM ruling)", 0.84,
     "source (HOLD candidate STUDIO 10.200, selection C7)", "HOLD (D-46, ISS-002)", "hardware selection C7",
     "reserved space only; the latch side has no frame for a strike"),
    ("368103", "FRONT - DOOR PULL PAIR - HOLD", "Tay nắm cửa (chờ chọn)", 1, "bought, HOLD", "not named", 0.8, "assumption (D-56)", "HOLD", "hardware selection C2",
     "reserved space only"),
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
    # DXF 1:1 in mm. Leaf: the front view seen from outside, X(dxf) = X(pod) - kick_x0, Y(dxf) = Z(pod) - leaf bottom.
    x0, zb = L.ev(design, "kick_x0"), L.ev(design, "door_zb - door_glass_engage")
    leaf = [(x - x0, z - zb) for x, z in outline_mm(design, "OUTLINE - DOOR LEAF (SKELETON TRAPEZOID + 25 MM INTO THE KICK STRIP)",
                                                    "361001 FRONT - DOOR LEAF - 4+4 LAMINATED", ("x", "z"))]
    L.write_dxf_polyline(os.path.join(root_dir, DXF_LEAF_REL), [leaf])
    # Kick strip section seen from the hinge end (looking toward +X): X(dxf) = Y(pod) - outside face, Y(dxf) = Z(pod) - strip bottom.
    y0, kz = L.ev(design, KY0), L.ev(design, "kick_zb")
    kick = [(y - y0, z - kz) for y, z in outline_mm(design, "SECTION - KICK STRIP (H: GLAZING POCKET OVER DROP-SEAL CAVITY)",
                                                    "361002 FRONT - DOOR KICK STRIP", ("y", "z"))]
    L.write_dxf_polyline(os.path.join(root_dir, DXF_KICK_REL), [kick])
    print("DXF leaf corners:", [(round(a, 2), round(b, 2)) for a, b in leaf])
    print("DXF kick strip section corners:", [(round(a, 2), round(b, 2)) for a, b in kick])
    # parts list: names and masses from the model
    by_pn = {}
    for c in design.allComponents:
        if c.partNumber and c != design.rootComponent:
            by_pn.setdefault(c.partNumber, []).append(c)
    rows = []
    for pn, name, vn, qty, typ, mat, mass, mstat, status, src, note in BOM_ROWS:
        comps = by_pn.get(pn, [design.rootComponent] if pn == PN else [])
        if not comps:
            raise RuntimeError("no component for " + pn)
        if pn != PN and len(comps) != qty:
            raise RuntimeError("%s: %d components in CAD, %d in the parts list" % (pn, len(comps), qty))
        if not comps[0].name.startswith("%s %s" % (pn, name)) and pn != PN:
            raise RuntimeError("%s: CAD name %r does not match the parts list name %r" % (pn, comps[0].name, name))
        if mass == "cad":
            mass = round(L.comp_mass(comps[0]), 3)
        rows.append([pn, name, vn, typ, mat, qty, "" if mass is None else mass, mstat, status, src, note])
    unit = sum(r[5] * r[6] for r in rows[1:] if r[6] != "")
    rows[0][6] = round(unit, 2)
    rows[0][7] = "calculation (sum of the rows below)"
    path = os.path.join(root_dir, BOM_REL)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part_number", "name", "name_vi", "type", "material", "qty", "unit_mass_kg", "mass_status",
                    "status", "source", "note"])
        w.writerows(rows)
    print("parts list %s: %d rows, unit mass %.2f kg" % (BOM_REL, len(rows), unit))
    # anchors for the edit test
    names = {k: (PARTS[k][1] if k in PARTS else PARTS["PULL"][1]) for k in [a[0] for a in ANCHORS]}
    with open(os.path.join(root_dir, ANCHORS_REL), "w", encoding="utf-8") as f:
        json.dump({"document": DOC_NAME, "f3d": F3D_REL, "anchors": [
            {"component": "%s %s" % (PARTS[k][0], names[k]), "index": i, "expression": e} for k, i, e in ANCHORS]},
            f, indent=1, ensure_ascii=False)
    print("anchors %s: %d" % (ANCHORS_REL, len(ANCHORS)))
    # re-read the STEP in Fusion and compare its box with the model's
    imp = app.importManager
    before = L.box(design.rootComponent)
    sdoc = imp.importToNewDocument(imp.createSTEPImportOptions(step))
    sdes = adsk.fusion.Design.cast(sdoc.products.itemByProductType("DesignProductType"))
    after = L.box(sdes.rootComponent)
    sdoc.close(False)
    doc.activate()
    print("STEP re-read in Fusion: model box %s, STEP box %s, max diff %.3f mm" % (
        before, after, max(abs(a - b) for a, b in zip(before, after))))


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
