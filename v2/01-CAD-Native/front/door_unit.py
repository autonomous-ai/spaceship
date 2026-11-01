"""360001 FRONT - DOOR UNIT (Cụm cửa kính): native, parameter-driven. Spaceship / FocusPod v2.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py \
        --doc 360001_P01_FRONT-DOOR-UNIT_CAD --doc-new --save "P01 build"
    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/door_unit.py \
        --doc 360001_P01_FRONT-DOOR-UNIT_CAD --arg step=export --close

step=build (default) empties the active design (it must be this unit's
document) and builds it; step=export writes the .f3d, STEP, DXF, parts list
and the edit-test anchors from the saved version.

The door unit (D-56): the 4+4 leaf, the 85 mm aluminium kick strip with the
drop seal (D-40, D-57), the hinges and the pull. The hinges and pull are HOLD
(D-46): reserved spaces only, and the glass gets no holes or cut-outs for them
until a rated set is named (PM ruling on the FRONT plan). The glass runs 25 mm
down into the kick strip and the strip keeps the skeleton's 7 mm kick_gap
(PM rulings, 2026-10-31). The door opens outward (open-questions Q3, ISS-055).
No latch on the glass (PM ruling 2026-10-31): a 35 N magnetic door-stop catch
in DT's underside holds the door at its top latch corner, with its strike
clipped on the leaf's top edge, and the leaf is 2 mm shorter at the top for
the catch's 6 mm gap; the latch edge carries the door's half of a 180 deg
magnetic seal pair; the hinges hold the door at its closed position.

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
    print("helper module %s: %s" % (m.__name__, m.__file__))
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
    ("kick_x0", XL + " + door_xl", "mm", "calculation", "strip end and leaf hinge edge = the skeleton door's left edge"),
    ("kick_x1", XL + " + door_xbr", "mm", "calculation",
     "strip end under the latch edge = the skeleton door's bottom-right corner"),
    ("kick_zb", "thresh_h + kick_gap", "mm", "calculation", "strip bottom = threshold top + the skeleton's kick_gap (7, PM ruling)"),
    ("door_top_cut", "2 mm", "mm", "decided",
     "PM ruling 2026-10-31: the leaf is 2 mm shorter at the top, so the gap to DT is 6 mm, inside the 5 to 10 mm the "
     "Sugatsune HT-MSG62 door-stop catch needs (datasheet)"),
    ("leaf_zt", "door_zt - door_top_cut", "mm", "calculation", "top of the leaf"),
    ("kick_h", "door_zb - kick_zb", "mm", "calculation", "strip height: 78 on skeleton P03"),
    ("kick_len", "kick_x1 - kick_x0", "mm", "calculation", "cut length of the strip and the drop seal"),
    ("kick_pocket_d", "door_glass_engage + gu_base", "mm", "calculation", "glazing pocket depth"),
    ("kick_wall", "(kick_d - gu_w) / 2", "mm", "calculation",
     "strip side walls: 4 with the skeleton's 20 mm kick_d (each a hollow wall, D-85)"),
    ("kick_web", "3 mm", "mm", "assumption", "web between the glazing pocket and the drop-seal cavity"),
    # D-85 (weight): the strip is hollow, same outside shape and finish: each 4 mm side wall is two skins round a chamber
    ("kick_skin", "1 mm", "mm", "assumption", "extrusion skin of the hollow side walls and their closing flanges (6063, 1.0 mm)"),
    ("kick_ch_w", "kick_wall - 2 * kick_skin", "mm", "calculation", "chamber inside each side wall: 2 mm"),
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
    ("hinge_z3", "leaf_zt - 250 mm", "mm", "assumption", "top hinge centre 250 below the glass top; HOLD H01"),
    ("hinge_z2", "(hinge_z1 + hinge_z3) / 2", "mm", "assumption", "middle hinge at mid-span; HOLD H01"),
    ("lock_zc", "floor_top + 1050 mm", "mm", "assumption",
     "pull centre 1050 above the finished floor (usual handle height); floor_top is the skeleton's floor on its mat"),
    # no latch on the glass (PM ruling 2026-10-31): the door is held at the top by a magnetic door-stop catch in DT's
    # underside; its strike clips on the leaf's top edge at the latch corner
    ("st_l", "62 mm", "mm", "source", "Sugatsune HT-MSG62 strike plate, 62 long (datasheet D2, Dec 2020)"),
    ("st_h", "22 mm", "mm", "source", "strike plate, 22 down the glass faces (datasheet)"),
    ("st_a", "14.1 mm", "mm", "source", "strike HT-MSG62-U10 (10 mm glass), A = 14.1; on the 8.76 laminate with a 1.2 mm shim, HOLD (PM ruling)"),
    ("st_top", "1.5 mm", "mm", "assumption", "strike plate over the glass top edge, steel plus packing"),
    ("st_end", "25 mm", "mm", "assumption", "the strike's latch-side end, in from the leaf's top latch corner"),
    ("ms_w", "fg_gap / 2", "mm", "assumption", "the door's half of the 180 deg magnetic seal pair fills half the 4 mm gap"),
    ("ms_t", "1.5 mm", "mm", "assumption", "the seal profile over each glass face"),
    ("pull_cc", "300 mm", "mm", "source", "HOLD candidate Häfele 903.10.390 pull pair, 300 mm centres, Ø19 (selection C2)"),
    ("pull_len", "pull_cc + 60 mm", "mm", "assumption", "bar 30 mm past each fixing"),
    ("pull_w", "40 mm", "mm", "assumption", "reserved width: the Ø19 bar and its fixing roses"),
    ("pull_stand", "70 mm", "mm", "assumption", "reserved projection from each glass face"),
    ("pull_back", "100 mm", "mm", "assumption", "pull axis 100 mm in from the latch edge"),
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
    # D-104: the strike body is a stand-in (its own clip over the leaf's top edge is the overlap), so ENVELOPE
    "STRIKE": ("368102", "FRONT - DOOR STRIKE - ENVELOPE", "Đế hít cửa"),
    "MSEAL": ("368006", "FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD", "Gioăng nam châm 180° phía cửa (chờ chọn)"),
    "PULL": ("368103", "FRONT - DOOR PULL PAIR - HOLD", "Tay nắm cửa (chờ chọn)"),
}

# Overlaps made on purpose, with the reason; any other clash over 1 mm3 fails the build.
EXPECTED = [
    (("H1", "LEAF"), "HOLD hinge space wraps the leaf's hinge edge: the named hinge will clamp the glass there"),
    (("H2", "LEAF"), "as H1"),
    (("H3", "LEAF"), "as H1"),
    (("STRIKE", "LEAF"), "the catch's strike plate clips over the leaf's top edge"),
]

# Edit-test anchors: (key, bounding-box index 0..5 = xmin ymin zmin xmax ymax zmax, expression).
ANCHORS = [
    ("LEAF", 0, "kick_x0"), ("LEAF", 3, "kick_x1"), ("LEAF", 2, "door_zb - door_glass_engage"),
    ("LEAF", 5, "leaf_zt"), ("LEAF", 1, GY0), ("LEAF", 4, GY1),
    ("KICK", 0, "kick_x0"), ("KICK", 3, "kick_x1"), ("KICK", 2, "kick_zb"), ("KICK", 5, "door_zb"),
    ("KICK", 1, KY0), ("KICK", 4, KY1),
    ("USEAL", 2, "door_zb - kick_pocket_d"), ("USEAL", 5, "door_zb"), ("USEAL", 1, UY0), ("USEAL", 4, UY1),
    ("GSA", 2, "kick_zb"), ("GSA", 5, "kick_zb + gsa_h"), ("GSA", 4, UY1), ("GSA", 3, "kick_x1"),
    ("H1", 2, "hinge_z1 - hinge_clamp_h / 2"), ("H3", 5, "hinge_z3 + hinge_clamp_h / 2"),
    ("H2", 0, "hinge_x0"), ("H2", 3, "kick_x0 + hinge_clamp_w"),
    ("STRIKE", 5, "leaf_zt + st_top"), ("STRIKE", 2, "leaf_zt - st_h"),
    ("MSEAL", 2, "door_zb"), ("MSEAL", 5, "leaf_zt"),
    ("PULL", 1, GY0 + " - pull_stand"), ("PULL", 4, GY1 + " + pull_stand"), ("PULL", 5, "pull_zc + pull_len / 2"),
]

ENVELOPE_MAT = "ENVELOPE - mass carried in the parts list (1 kg/m3)"


SCOPES = {"unit": None, "leaf": "LEAF", "kick": "KICK"}   # part-only designs for the part drawings


def scope_doc(scope):
    """Document name for a scope: the unit, or one part on its own (same parameters, same sketches)."""
    if scope == "unit":
        return DOC_NAME
    pn, nm, _vn = PARTS[SCOPES[scope]]
    return "%s_%s_%s_CAD" % (pn, REV, nm.replace("+", "-").replace(" - ", "-").replace(" ", "-"))


def build(app):
    scope = ARGS.get("scope", "unit")
    only = SCOPES[scope]
    rpn, rname, rvn = (PN, NAME, VN) if only is None else PARTS[only]
    design = L.start_design(app, rpn, "%s | %s | %s" % (rname, rvn, REV))
    sk_params, sk_path, sk_rev = L.load_skeleton_params(ARGS["repo_root"])
    L.add_params(design, sk_params)
    L.add_params(design, L.LIB_PARAMS)
    L.add_params(design, L.GLASS_PARAMS)
    L.add_params(design, OWN)
    root = design.rootComponent
    for name, expr in (("kick_cav_h", "gsa_h"),):
        if L.ev(design, name) < L.ev(design, expr):
            raise RuntimeError("%s (%.1f) is smaller than %s (%.1f)" % (name, L.ev(design, name), expr, L.ev(design, expr)))
    comps, bodies = {}, {}

    def want(key):
        return only is None or key == only

    def comp(key):
        pn, nm, vn = PARTS[key]
        c = L.new_comp(root, pn, nm, vn, REV)
        comps[key] = c
        return c

    # 361001 leaf: the skeleton's trapezoid, extended 25 mm down into the strip with a vertical latch-side
    # end (the extension sits inside the strip, so the visible outline is the skeleton's).
    if want("LEAF"):
        c = comp("LEAF")
        bodies["LEAF"] = L.prism(design, c, "LEAF", ("x", "z"), [
            ("kick_x0", "door_zb - door_glass_engage"), ("kick_x1", "door_zb - door_glass_engage"),
            ("kick_x1", "door_zb"), (latch_x("leaf_zt"), "leaf_zt"), ("kick_x0", "leaf_zt")],
            "y", GY0, GY1, "DOOR LEAF GLASS 4+4", "OUTLINE - DOOR LEAF (SKELETON TRAPEZOID + 25 MM INTO THE KICK STRIP)",
            "EXTRUDE - DOOR LEAF 8.76")

    # 361002 kick strip: H section, glazing pocket on top, drop-seal cavity below, hollow side walls (D-85)
    if want("KICK"):
        c = comp("KICK")
        bodies["KICK"] = L.prism(design, c, "KICK", ("y", "z"), [
            (KY0, "kick_zb"), (UY0, "kick_zb"), (UY0, "kick_zb + kick_cav_h"), (UY1, "kick_zb + kick_cav_h"),
            (UY1, "kick_zb"), (KY1, "kick_zb"), (KY1, "door_zb"), (UY1, "door_zb"),
            (UY1, "door_zb - kick_pocket_d"), (UY0, "door_zb - kick_pocket_d"), (UY0, "door_zb"), (KY0, "door_zb")],
            "x", "kick_x0", "kick_x1", "KICK STRIP", "SECTION - KICK STRIP (H: GLAZING POCKET OVER DROP-SEAL CAVITY)",
            "EXTRUDE - KICK STRIP LENGTH")
        for side, y0 in (("OUTSIDE", KY0 + " + kick_skin"), ("POD SIDE", UY1 + " + kick_skin")):
            sk = L.poly(design, c, c.yZConstructionPlane, ("y", "z"), 0, "SECTION - KICK STRIP CHAMBER - " + side,
                        [(y0, "kick_zb + kick_skin"), (y0 + " + kick_ch_w", "kick_zb + kick_skin"),
                         (y0 + " + kick_ch_w", "door_zb - kick_skin"), (y0, "door_zb - kick_skin")])
            L.extrude_span(c, sk, "x", "kick_x0", "kick_x1", adsk.fusion.FeatureOperations.CutFeatureOperation,
                           [bodies["KICK"]], "CUT - KICK STRIP CHAMBER - " + side + " (D-85)")

    # 368002 silicone U-seal round the glass edge in the pocket
    if want("USEAL"):
        c = comp("USEAL")
        bodies["USEAL"] = L.prism(design, c, "USEAL", ("y", "z"), [
            (UY0, "door_zb - kick_pocket_d"), (UY1, "door_zb - kick_pocket_d"), (UY1, "door_zb"), (GY1, "door_zb"),
            (GY1, "door_zb - door_glass_engage"), (GY0, "door_zb - door_glass_engage"), (GY0, "door_zb"),
            (UY0, "door_zb")],
            "x", "kick_x0", "kick_x1", "GLAZING U-SEAL", "SECTION - GLAZING U-SEAL", "EXTRUDE - GLAZING U-SEAL LENGTH")

    # 368001 drop seal: catalogue section, bonded to the pod-side wall of the cavity, flush with the strip bottom
    if want("GSA"):
        c = comp("GSA")
        bodies["GSA"] = L.prism(design, c, "GSA", ("y", "z"), [
            (UY1 + " - gsa_t", "kick_zb"), (UY1, "kick_zb"), (UY1, "kick_zb + gsa_h"), (UY1 + " - gsa_t", "kick_zb + gsa_h")],
            "x", "kick_x0", "kick_x1", "DROP SEAL ENVELOPE (CATALOGUE SECTION)", "SECTION - DROP SEAL GSA 11.6 X 40",
            "EXTRUDE - DROP SEAL CUT LENGTH")

    # HOLD spaces for the hinges (into the DL pocket) and the pull; the catch's strike; the seal half
    for key, zc in (("H1", "hinge_z1"), ("H2", "hinge_z2"), ("H3", "hinge_z3")):
        if want(key):
            c = comp(key)
            bodies[key] = L.box_body(design, c, key, ("hinge_x0", "kick_x0 + hinge_clamp_w"),
                                     ("-glass_y - hinge_clamp_t / 2", "-glass_y + hinge_clamp_t / 2"),
                                     ("%s - hinge_clamp_h / 2" % zc, "%s + hinge_clamp_h / 2" % zc),
                                     "HOLD HINGE SPACE " + key, "PLAN - HOLD HINGE SPACE " + key)
    if want("STRIKE"):
        c = comp("STRIKE")
        sx1 = "(%s - st_end)" % latch_x("leaf_zt")
        bodies["STRIKE"] = L.box_body(design, c, "STRIKE", ("%s - st_l" % sx1, sx1),
                                      ("-glass_y - st_a / 2", "-glass_y + st_a / 2"), ("leaf_zt - st_h", "leaf_zt + st_top"),
                                      "FRONT - DOOR STRIKE - ENVELOPE")
    if want("MSEAL"):
        c = comp("MSEAL")
        dx = lambda z: "((fg_lc + ms_w - fg_lnz * (%s)) / fg_lnx)" % z
        bodies["MSEAL"] = L.prism(design, c, "MSEAL", ("x", "z"), [
            (L.door_x("door_zb"), "door_zb"), (dx("door_zb"), "door_zb"), (dx("leaf_zt"), "leaf_zt"),
            (L.door_x("leaf_zt"), "leaf_zt")], "y", GY0 + " - ms_t", GY1 + " + ms_t",
            "180 MAGNETIC SEAL - DOOR HALF (HOLD PRODUCT)", "OUTLINE - 180 MAGNETIC SEAL DOOR HALF",
            "EXTRUDE - 180 MAGNETIC SEAL DOOR HALF")
    if want("PULL"):
        c = comp("PULL")
        bodies["PULL"] = L.box_body(design, c, "PULL-OUT", ("pull_x - pull_w / 2", "pull_x + pull_w / 2"),
                                    (GY0 + " - pull_stand", GY0), ("pull_zc - pull_len / 2", "pull_zc + pull_len / 2"),
                                    "HOLD PULL SPACE - OUTSIDE")
        bodies["PULL-IN"] = L.box_body(design, c, "PULL-IN", ("pull_x - pull_w / 2", "pull_x + pull_w / 2"),
                                       (GY1, GY1 + " + pull_stand"), ("pull_zc - pull_len / 2", "pull_zc + pull_len / 2"),
                                       "HOLD PULL SPACE - POD SIDE")

    # materials and looks
    mats = {"LEAF": ("Glass 4+4 laminated (2376 kg/m3, calculation)", "Glass", 2376.0),
            "KICK": ("Aluminium EN AW-6063-T6 (2700 kg/m3)", "Aluminum", 2700.0),
            "USEAL": ("Silicone rubber (1200 kg/m3, assumption)", "Rubber, Silicone", 1200.0),
            "STRIKE": ("Stainless steel SUS430 (7700 kg/m3)", "Steel", 7700.0)}
    looks = {"LEAF": ["Glass - Smoked", "Glass (Smoked)", "Glass - Window", "Glass"],
             "KICK": ["Paint - Enamel Glossy (Black)", "Aluminum - Anodized Glossy (Black)", "Plastic - Matte (Black)"],
             "USEAL": ["Rubber - Soft (Black)", "Plastic - Matte (Black)"],
             "GSA": ["Plastic - Matte (Grey)", "Paint - Enamel Glossy (Grey)"],
             "HOLD": ["Paint - Enamel Glossy (Red)", "Plastic - Glossy (Red)"],
             "STRIKE": ["Steel - Satin", "Stainless Steel - Satin"],
             "MSEAL": ["Plastic - Matte (Grey)", "Paint - Enamel Glossy (Grey)"]}
    for k, b in bodies.items():
        b.material = L.material(design, *mats[k]) if k in mats else L.material(design, ENVELOPE_MAT, "Aluminum", 1.0)
        a = L.appearance(design, looks.get(k) or looks["HOLD"])
        if a:
            b.appearance = a

    # checks
    expected = [(k, r) for k, r in EXPECTED if all(x in bodies for x in k)]
    n_tl, bad, loose = L.health(design)
    hits, bad_clash = L.clash_check(bodies, expected)
    print("scope %s: design for %s %s" % (scope, rpn, rname))
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
    missing = [k for k, _r in expected if frozenset(k) not in hit_set]
    print("listed pairs that do not clash:", missing)
    for key in ("LEAF", "KICK", "USEAL"):
        if key in comps:
            print("MASS|%s|%s|%.3f kg" % (key, PARTS[key][0], L.comp_mass(comps[key])))
    print("unit box", L.box(root))
    for name in ("kick_h", "kick_len", "kick_cav_h", "kick_wall", "leaf_zt", "pull_x", "hinge_z1", "hinge_z2", "hinge_z3"):
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
    ("361002", "FRONT - DOOR KICK STRIP", "Thanh chân cửa nhôm", 1, "made (extruded hollow profile, custom die; D-85)", "aluminium EN AW-6063-T6, finish black anodised matte 20 um (AA20, the base band's finish, D-67)",
     "cad", "calculation (CAD, 2700 kg/m3)", "DRAFT", "D-40, D-57; PM rulings on the FRONT plan",
     "cut length = kick_len; glass retention in the pocket HOLD (J-FRONT-02)"),
    ("368001", "FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112", "Ron chân cửa tự động", 1, "bought, cut to length", "athmer Schall-Ex GSA 1-1112, black RAL 9005", 0.6,
     "assumption (D-56)", "source (product); bond to aluminium HOLD", "hardware selection C4", "cut from 1208 to kick_len"),
    ("368002", "FRONT - GLAZING U-SEAL - BOHLE BO5201735", "Gioăng chữ U silicone", 1, "bought by length", "Bohle BO5201735 silicone U-profile seal", "cad",
     "calculation (CAD, 1200 kg/m3 assumption)", "source (product); fit on 8.76 laminate unverified",
     "hardware selection C5", "length = kick_len"),
    ("368101", "FRONT - DOOR HINGE - HOLD", "Bản lề cửa (chờ chọn)", 3, "bought, HOLD",
     "not named: rated for the 8.76 laminate, at least 60 kg and the 1176 mm width; holds the door at its closed "
     "position; two-part lift-off, the frame halves ship fitted in DL; hung on site with the 5 mm key (PM rulings)",
     0.6, "assumption (D-56)", "HOLD (D-46, ISS-002)", "hardware selection C1", "reserved space only"),
    ("368102", "FRONT - DOOR STRIKE", "Bát hít cửa", 1, "bought",
     "stainless steel SUS430 strike with CR packing, finish as supplied", 0.023, "source (Sugatsune datasheet, 22.9 g)",
     "source (product); on the 8.76 laminate with a 1.2 mm shim: HOLD", "hardware selection C7; PM rulings 2026-10-31",
     "its catch 368007 sits in DT's underside; no latch on the glass"),
    ("368006", "FRONT - 180 MAGNETIC SEAL - HALF 2 OF 2 - HOLD", "Gioăng nam châm 180° phía cửa (chờ chọn)", 1,
     "bought, HOLD", "magnetic 180 deg glass-to-glass seal, door half; product not named", 0.15, "assumption",
     "HOLD: product for the 8.76 laminate and a 4 mm gap", "PM ruling 2026-10-31", "pairs with 368003 on the fixed pane"),
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
    chambers = [[(y - y0, z - kz) for y, z in outline_mm(design, "SECTION - KICK STRIP CHAMBER - " + side,
                                                         "361002 FRONT - DOOR KICK STRIP", ("y", "z"))]
                for side in ("OUTSIDE", "POD SIDE")]
    L.write_dxf_polyline(os.path.join(root_dir, DXF_KICK_REL), [kick] + chambers)
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
        maker = sku = ""
        if pn in L.REGISTER_ITEMS:    # the joints register's name (the CAD name was checked above), maker and SKU
            name, vn, maker, sku = L.REGISTER_ITEMS[pn]
        rows.append([pn, name, vn, typ, mat, qty, "" if mass is None else mass, mstat, status, src, note, maker, sku])
    unit = sum(r[5] * r[6] for r in rows[1:] if r[6] != "")
    rows[0][6] = round(unit, 2)
    rows[0][7] = "calculation (sum of the rows below)"
    path = os.path.join(root_dir, BOM_REL)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(L.PARTS_LIST_COLUMNS)
        w.writerows(L.parts_list_row(r) for r in rows)
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


SHOTS = [("v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT-FRONT_IMG.png", "front"),
         ("v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT-ISO_IMG.png", "iso-top-right")]


def run(_context):
    """step: build | export | post (export, pictures, edit test with --arg edits=...) | all (build, save, post)."""
    app = adsk.core.Application.get()
    step = ARGS.get("step", "build")
    scope = ARGS.get("scope", "unit")
    doc = app.activeDocument
    want_doc = scope_doc(scope)
    if doc is None or not doc.name.startswith(want_doc):
        raise RuntimeError("active document is %r, not %s: open it with the runner's --doc" % (
            doc.name if doc else None, want_doc))
    if scope != "unit" and step != "build":
        raise RuntimeError("a part-only design is only built (the runner's --save keeps it)")
    L.run_steps(app, ARGS, HERE, step, build, export_all, SHOTS, ANCHORS_REL)
