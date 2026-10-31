"""Spaceship (FocusPod v2) WALL: one side wall panel and its lining cassette.

Native, parameter-driven Fusion design, built by script into the ACTIVE
document (open your own document first, for example with the runner's
--doc-new NAME). One run builds one document:

    part=panel     the outer panel assembly: frame, ACP skin, PET fill
    part=cassette  the lining cassette: steel tray, felt, clip zones (HOLD)

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_side_panel.py \
        --doc-new 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD \
        --arg part=panel --arg side=L --arg row=1 --save "build P01" --close

Options (--arg KEY=VALUE):
    part=panel|cassette   which document to build (default panel): the outer panel assembly, or the cassette
    part=frame|skin|fill|tray|felt   one manufactured part alone in its own design, for its part drawing
                          (a Fusion drawing view always shows the whole design); same code, same parameters
    side=L|R              left (-X) or right (+X) wall, seen from outside facing the door
    row=1|2               lower (1) or upper (2) panel
    stop_after=N          stop after step N, for step-by-step checks
    rebuild=1             empty the active design first (only a design this script built:
                          its root part number must be the one this run builds)
    skeleton=NAME         skeleton cloud file to derive from (default 100000_P04_POD-SKELETON_CAD)
    post=1                after a clean build, save the document here and run post_wall_doc.py's steps in the
                          same run (export, report, flat DXF, edit test); close with --close --discard
    link=derive|parse     how the skeleton parameters come in (default derive)

Coordinates: the pod system of conventions.md section 4 (origin on the room
floor at the pod centre, +X right, +Y back, +Z up), the same as skeleton P03,
so every part sits where it goes in the pod and the WALL and GA assemblies
insert these designs without a transform.

Parameters: the skeleton is the single source of the pod sizes. The design
links to the saved skeleton (cloud file `skeleton`, default
100000_P04_POD-SKELETON_CAD) with Fusion's Derive: every skeleton parameter
arrives as <name>_Ref and follows each new skeleton version
(Document.updateAllReferences). The wall then adds one alias per skeleton name
it uses (side_h = side_h_Ref, ...) so its own expressions read plainly, and its
own parameters below. Inside Fusion, change an alias (side_h, wall_depth) and
every body follows (edit test, edit_test_wall.py). link=parse instead copies
the values from pod_skeleton.py's PARAMS (offline tests and emergencies only).

Every sketch is fully constrained (the run fails otherwise), every feature,
body and sketch is named by its function, and each part is its own component
with its part number (conventions.md section 6, DECIDED by the PM).
"""

import ast
import math
import os
import re

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
REV = "P01"
PART = ARGS.get("part", "panel")
SIDE = ARGS.get("side", "L").upper()
ROW = int(ARGS.get("row", "1"))
STOP_AFTER = int(ARGS.get("stop_after", "99"))
S = -1 if SIDE == "L" else 1          # sign of X for this side
INSIDE = "+x" if SIDE == "L" else "-x"   # the room side, for the drawings' Front (set_front.py)
SKELETON_REL = "v2/01-CAD-Native/skeleton/pod_skeleton.py"
MM = 0.1                               # Fusion API lengths are cm

WANT = {"panel": ("frame", "skin", "fill"), "frame": ("frame",), "skin": ("skin",), "fill": ("fill",),
        "cassette": ("tray", "felt", "clip"), "tray": ("tray",), "felt": ("felt",)}
if SIDE not in ("L", "R") or ROW not in (1, 2) or PART not in WANT:
    raise ValueError("side must be L or R, row 1 or 2, part one of %s" % sorted(WANT))
PANEL_SIDE = PART in ("panel", "frame", "skin", "fill")

# ---------------------------------------------------------------- part numbers and names

POS = {("L", 1): 1, ("R", 1): 2, ("L", 2): 3, ("R", 2): 4}[(SIDE, ROW)]
CODE = "%s%d" % (SIDE, ROW)            # position code, conventions.md section 4
HAND = "LH" if SIDE == "L" else "RH"
LEVEL = "LOWER" if ROW == 1 else "UPPER"
VN_SIDE = "Vách trái" if SIDE == "L" else "Vách phải"
VN_LEVEL = "dưới" if ROW == 1 else "trên"

# key: (part number, English name, Vietnamese name). Numbers follow conventions.md
# section 6: WALL 21 (assemblies 0001-0999, made parts 1000-7999), LINING 51.
# Status: confirmed (PM ruling in the WALL group, 2026-10-31: numbers per
# conventions section 6, checked against D-28's reserved list).
PARTS = {
    "assy": ("2101%02d" % POS, "WALL - PANEL ASSY - SIDE %s - %s" % (LEVEL, HAND),
             "%s - cụm tấm %s" % (VN_SIDE, VN_LEVEL)),
    "frame": ("2111%02d" % POS, "WALL - PANEL FRAME - SIDE %s - %s" % (LEVEL, HAND),
              "%s - khung %s" % (VN_SIDE, VN_LEVEL)),
    "skin": ("2113%02d" % POS, "WALL - SKIN - SIDE %s - %s" % (LEVEL, HAND),
             "%s - tấm ốp alu %s" % (VN_SIDE, VN_LEVEL)),
    "fill": ("2115%02d" % POS, "WALL - CAVITY FILL - SIDE %s - %s" % (LEVEL, HAND),
             "%s - bông PET %s" % (VN_SIDE, VN_LEVEL)),
    "cass": ("5101%02d" % POS, "LINING - CASSETTE - SIDE %s - %s" % (LEVEL, HAND),
             "Cassette lót %s %s (khay thép + tấm tiêu âm)" % (VN_SIDE.lower(), VN_LEVEL)),
    "tray": ("5111%02d" % POS, "LINING - TRAY - SIDE %s - %s" % (LEVEL, HAND),
             "Khay thép lót %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "felt": ("5113%02d" % POS, "LINING - FELT - SIDE %s - %s" % (LEVEL, HAND),
             "Tấm tiêu âm %s %s" % (VN_SIDE.lower(), VN_LEVEL)),
    "clip": ("NO-PN-HOLD-H03", "HOLD - CASSETTE CLIP ZONES (H03, NO PART NAMED)",
             "Vùng dành cho kẹp treo cassette (HOLD)"),
}
# joint hardware the panel carries from the factory, numbered by the joints register (V2-ENG-JNT-01, table 2.1;
# PROPOSED numbers, D-63): one component each in the panel assembly
HW_PARTS = {
    "rivnut": ("838003", "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "Tán rút M6"),
    "stopw": ("831002", "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm"),
    "spigot": ("831001", "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8"),
}
PARTS.update(HW_PARTS)
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005",
            "350011", "830001", "830005"}          # D-28
for _k, (_pn, _n, _v) in PARTS.items():
    if _pn in RESERVED:
        raise RuntimeError("reserved part number %s (D-28)" % _pn)
ROOT_KEY = {"panel": "assy", "cassette": "cass"}.get(PART, PART)
DOC_NAME = "%s_%s_%s_CAD" % (PARTS[ROOT_KEY][0], REV, re.sub(r"[^A-Z0-9]+", "-", PARTS[ROOT_KEY][1]).strip("-"))

# ---------------------------------------------------------------- wall parameters

# name, expression, unit, status, source. A parameter may use any skeleton
# parameter and the ones above it. Statuses per conventions.md section 9.
WALL_PARAMS = [
    # outer panel
    ("tube_w", "20 mm", "mm", "confirmed",
     "D-34, D-54: aluminium tube 20 x 40 x 1.2; the 20 mm face carries the skin, so the 40 mm runs through the "
     "wall (outer_t = ACP 3 + frame 40). The joint register may turn it for the bond width (HOLD)"),
    ("tube_d", "outer_t - skin_t - bond_t", "mm", "calculation", "frame depth = outer panel 46 - skin 3 - bond 3 = 40 (D-34)"),
    ("tube_t", "1.2 mm", "mm", "confirmed",
     "D-34, D-54, D-85: perimeter members (rails, front and back stiles) keep the 1.2 mm wall; they carry the rivnuts "
     "(grip check passed)"),
    ("stud_t", "1.0 mm", "mm", "confirmed",
     "D-85 (weight): intermediate studs at a 1.0 mm wall; they carry no rivnut, only the skin's bond line"),
    ("stile_pitch_max", "400 mm", "mm", "confirmed", "D-16, D-34: members 400 mm apart or less, to keep the ACP flat"),
    ("pnl_len", "wall_depth - seam_gap", "mm", "calculation",
     "D-49 depth 1495 less the 2.26 gap at the decor back plate (PM ruling on F-008): 1492.74"),
    ("pnl_h", "side_h", "mm", "calculation", "skeleton side_h: 2 sheets per side wall (D-23) with the seam gaps"),
    ("skin_ret", "outer_t - skin_t", "mm", "assumption",
     "back return of the side skin: covers the frame's back end at the corner, where the side skin covers the back "
     "panel's edge (D-55; sample drawing D04). V-groove and fold per the ACP maker (HOLD H16)"),
    ("skin_setback", "0 mm", "mm", "assumption",
     "skin edge set back from the frame's top and bottom edges: 0, so the outside reveal equals the 2.26 seam gap "
     "(D-23: crisp, aligned reveals; joints register 2.8 leaves the setback to the WALL drawing)"),
    ("frm_len", "pnl_len - skin_t", "mm", "calculation", "the frame stops at the inside of the skin's back return"),
    ("frm_h", "pnl_h", "mm", "assumption",
     "the frame fills the skeleton envelope height; seam and base gasket gaps are set by the joint register (HOLD)"),
    ("corner_w", "40 mm", "mm", "confirmed",
     "the side panel's back member is 40 x 40 x 1.2 (PM ruling on the joints register, item 3, 2026-10-31; "
     "register F2, FR-06): the back corner joint needs a 37+ mm overlap for the rivnut and the bolt"),
    ("stile_n_mid", "ceil((frm_len - tube_w / 2 - corner_w / 2) / stile_pitch_max) - 1", "", "calculation",
     "intermediate stiles so that no stile pitch (centre to centre) exceeds stile_pitch_max"),
    ("stile_pitch", "(frm_len - tube_w / 2 - corner_w / 2) / (stile_n_mid + 1)", "mm", "calculation",
     "equal stile pitch, centre to centre, from the front stile to the 40 mm back stile"),
    ("top_h", "tube_w" if ROW == 1 else "corner_w", "mm", "confirmed" if ROW == 2 else "calculation",
     "top member height: 20 on a lower panel; 40 x 40 on an upper panel, where the ceiling bolts in (PM ruling "
     "R-J3, joints register FR-06)"),
    ("stile_len", "frm_h - tube_w - top_h", "mm", "calculation", "stiles fit between the full-length rails (butt joints)"),
    ("ceil_bolt_dz", "pod_h - ceil_bolt_z", "mm", "calculation",
     "J-CEIL-01 side bolts on the ceiling frame tube's centre: the skeleton's ceil_bolt_z, Z 2374 on P04 (joints "
     "register R-J15, FR-07)"),
    ("fill_t", "tube_d", "mm", "calculation", "40 mm PET fill fills the frame depth (D-34; layout study 40 mm)"),
    # site joints, joints register V2-ENG-JNT-01 P01 (ce1f415): M6 x 20 ISO 4762 captive bolts into Sherex
    # CAH3-610-4.2 rivnuts, bolts and corner members DECIDED by the PM (2026-10-31); positions PROPOSED there
    ("bolt_d", "7 mm", "mm", "confirmed", "PM ruling on F-009: bolt holes 7.0 (0.51 float), position tolerance "
     "0.4 (+-0.2) from the spigot hole, CNC or drill jig (joints register FR-02)"),
    ("access_d", "19 mm", "mm", "calculation",
     "register FR-03: passes the 18 mm head washer (ISO 7093-1, R-J10), the M6 head and the 5 mm key; holds the "
     "grommet retainer (H-02)"),
    ("bolt_line_y", "pod_d / 2 - skin_t - bond_t - tube_d / 2", "mm", "confirmed",
     "J-WALL-02 bolt line on the back panel's tube centre, Y 824 (joints register R-J15, FR-07)"),
    ("rivnut_d", "9.53 mm", "mm", "source", "Sherex CAH3-610-4.2 hole 9.53 +0.10 (HW-SEL A5; register H-03)"),
    ("spigot_d", "8.5 mm", "mm", "assumption", "register FR-05: hole for the 8 mm locating spigot H-05"),
    ("spigot_slot", "14 mm", "mm", "assumption", "register FR-05: slot length for the second spigot"),
    ("spigot_edge", "spigot_inset", "mm", "calculation",
     "the skeleton's spigot_inset: spigots 100 from each end of the edge (PM ruling 2026-10-31, R-J13)"),
    ("bolt_edge", "bolt_edge_inset", "mm", "calculation",
     "the skeleton's bolt_edge_inset: end bolts 220 in from the panel's ends, evenly spaced, every bolt 30 or more "
     "from any stile (PM ruling 2026-10-31, R-J14)"),
    ("n_side_jnt", "3", "", "source", "register J-WALL-02, J-FRONT-01: 3 bolts up each side panel"),
    ("side_jnt_pitch", "(pnl_h - 2 * bolt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "equal pitch of the 3 bolts up the corner and decor joints"),
    ("pocket_w", "60 mm", "mm", "assumption", "register FR-10: fill left out 60 x 60 next to each bolt for the key"),
    ("corner_z0", "panel_z0" if ROW == 1 else "panel_z0 + back_ph + seam_gap", "mm", "calculation",
     "bottom of the back panel row this side panel meets at the corner (B1/B2 or B3/B4, skeleton P04)"),
    ("corner_bolt_pitch", "(back_ph - 2 * bolt_edge) / (n_side_jnt - 1)", "mm", "calculation",
     "J-WALL-02 bolts run along the back panel's edge: 220, 559.31, 898.61 on its 1118.61 (joints register 2.9)"),
    ("n_len_bolt", "n_base_bolt", "", "calculation",
     "the skeleton's n_base_bolt (4): the same count on J-WALL-01 and the J-CEIL-01 side edges (register 2.9)"),
    ("ceil_bolt_pitch", "(wall_depth - 2 * bolt_edge) / (n_len_bolt - 1)", "mm", "calculation",
     "J-CEIL-01 side edge: 4 bolts along the ceiling's 1495 from Y -645 (its front edge), 220 rule, pitch 351.67 on "
     "P04; CEILING drills the same (PM ruling 2026-10-31 16:55; joints register 2.9)"),
    ("len_bolt_pitch", "(pnl_len - 2 * bolt_edge) / (n_len_bolt - 1)", "mm", "calculation",
     "even pitch of the bolts along the panel"),
    # lining cassette
    ("felt_t", "9 mm", "mm", "source", "plan VT03-PET 9 mm PET felt; HW-SEL A3; D-31 (the factory's felt)"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm"),
    ("tray_h", "cass_t", "mm", "confirmed",
     "PM ruling 2026-10-31 (WALL group, option 1): the wall cassettes use the ceiling's tray, returns the full "
     "cassette depth (34) turned in as lips that hold the felt, no ribs; settles H09 for the walls"),
    ("lip_w", "12 mm", "mm", "confirmed", "PM ruling 2026-10-31 (WALL group, option 1): 12 mm lips hold the felt edge"),
    ("bend_r", "tray_t", "mm", "assumption",
     "inside bend radius 1 x t for 0.5 mm DX51D (the sheet metal rule's bend radius is its Thickness); the factory's "
     "tooling sets it (guideline 9)"),
    ("felt_c", "1 mm", "mm", "assumption", "felt edge clearance inside the returns, as the ceiling cassette"),
    ("gap_h", "tray_h - felt_t - 2 * tray_t", "mm", "calculation",
     "air gap between the tray base and the felt (24): the acoustic gap (D-17) and the cable path (D-26)"),
    ("cass_len", "wall_depth - stack_t + cass_t", "mm", "calculation",
     "= 1448: from the decor back plate to past the back cassette's face, closing the inside corner (D-57)"),
    ("cass_h", "side_h" if ROW == 1 else "side_h - outer_t - lin_gap", "mm", "calculation",
     "lower: the panel height; upper: stops lin_gap under the roof frame so it floats (D-57)"),
    ("clip_zone_h", "60 mm", "mm", "assumption", "height of each reserved clip zone (H03: no clip named)"),
    ("clip_zone_dz", "100 mm", "mm", "assumption", "clip zone centre from the cassette's top and bottom edges (H03)"),
    # joint hardware bodies (register 2.1 sizes): the rivnut as its installed envelope, threads at 6 mm
    ("stopw_od", "20 mm", "mm", "source", "joints register H-08: stop washer Ø10.5 x Ø20 x 1.5 (PROPOSED part)"),
    ("stopw_id", "10.5 mm", "mm", "source", "joints register H-08"),
    ("stopw_t", "1.5 mm", "mm", "source", "joints register H-08: rivnut head 0.76 + washer 1.5 = the 2.26 stop (R-J5)"),
    ("rivnut_head_d", "12.96 mm", "mm", "source", "Sherex CAH3-610-4.2 head Ø12.96 (joints register H-03, SHX)"),
    ("rivnut_head_t", "0.76 mm", "mm", "source", "Sherex CAH3-610-4.2 head 0.76 ±0.08 (H-03, SHX)"),
    ("rivnut_body_d", "9.5 mm", "mm", "source", "Sherex CAH3-610-4.2 body Ø9.50 max (H-03, SHX)"),
    ("rivnut_len", "10.16 mm", "mm", "source",
     "Sherex CAH3-610-4.2 installed length 10.16 max under the head (H-03, SHX); the bulge inside the tube is not "
     "modelled"),
    ("m6_d", "6 mm", "mm", "calculation", "M6 threads shown at their 6 mm major diameter (no modelled thread)"),
    ("spigot_pin_d", "8 mm", "mm", "source", "joints register H-05: Ø8 stainless pin (PROPOSED, assumption sizes)"),
    ("spigot_proud", "8 mm", "mm", "source", "joints register H-05: stands 8 proud (read as: of the joint face)"),
    ("spigot_thread_l", "10 mm", "mm", "assumption",
     "M6 thread into the spigot rivnut; H-05 gives no length; 10 stays inside the rivnut's 10.16"),
]

# kg/m3, status, source; used for body materials (mass properties)
DENSITY = {
    "frame": (2700.0, "source", "6063-T6 mill finish (PM ruling 2026-10-31, hidden frame tubes): 2.70 g/cm3"),
    "skin": (3.5 / 0.003, "calculation", "HW-SEL A1: 3.5 kg/m2 for 3 mm Alcorest / 3 mm; real kg/m2 HOLD (H16)"),
    "fill": (24.0, "confirmed", "PM ruling 2026-10-31: 24 kg/m3 by default, the grade Pyrotek lists (the wall sample's "
                                "T02 confirms it, else 32)"),
    "tray": (7850.0, "source", "steel 7850 kg/m3 (EN 10346 DX51D+Z)"),
    "felt": (1.8 / 0.009, "source", "Polyx Board 9: 1.8 kg/m2 at 9 mm (HW-SEL A3 opt 2); the factory felt is unverified"),
    "zone": (1.0, "assumption", "reserved zone, not a part: near-zero density so it adds no mass"),
    "rivnut": (2640.0, "source", "aluminium 5056 (Sherex CAH3 series): 2.64 g/cm3"),
    "stopw": (2700.0, "calculation", "5000- or 6000-series aluminium sheet (H-08): 2.70 g/cm3 (5052 2.68, 6061 2.70)"),
    "spigot": (7900.0, "source", "stainless steel (H-05): 7.9 g/cm3"),
}

# ---------------------------------------------------------------- helpers


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def ev(design, expr):
    """Expression value in mm."""
    return design.unitsManager.evaluateExpression(expr, "mm") * 10.0


def skeleton_params(repo_root):
    """PARAMS of pod_skeleton.py, parsed with ast (no code is run)."""
    path = os.path.join(repo_root, SKELETON_REL)
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PARAMS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("no PARAMS in " + path)


def names_in(expr):
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", expr)) - {"mm", "ceil", "floor", "abs", "round"}


def needed_skeleton(skel, wall):
    """The skeleton parameters the wall expressions use, with their own dependencies, in skeleton order."""
    by_name = {p[0]: p for p in skel}
    want, todo = set(), set()
    for _n, expr, _u, _s, _src in wall:
        todo |= names_in(expr)
    for extra in ("pod_w", "pod_d", "pod_h", "wall_z0", "side_h", "stack_t", "outer_t", "cass_t", "lin_gap"):
        todo.add(extra)
    while todo:
        n = todo.pop()
        if n in by_name and n not in want:
            want.add(n)
            todo |= names_in(by_name[n][1])
    return [p for p in skel if p[0] in want]


SKELETON_NAMES = ("pod_w", "pod_d", "pod_h", "wall_depth", "wall_z0", "panel_z0", "side_h", "back_ph", "stack_t",
                  "outer_t", "cass_t", "lin_gap", "seam_gap", "skin_t", "bond_t", "bolt_edge_inset", "spigot_inset",
                  "n_base_bolt", "ceil_bolt_z")       # the skeleton parameters the wall uses (P04, as updated in #58)


def derive_skeleton(app, design, name):
    """Link the design to the saved skeleton with Fusion's Derive (favorite parameters only), as
    tools/fusion/README.md 'Linking a part to the skeleton' describes. Returns the version derived."""
    proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
    folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
    files = None
    for _attempt in range(3):           # the file list can change under us while others save (17:32 glitch)
        try:
            files = [folder.dataFiles.item(i) for i in range(folder.dataFiles.count)]
            break
        except RuntimeError:
            adsk.doEvents()
    files = [f for f in (files or []) if f.name == name]
    if not files:
        raise RuntimeError("skeleton %r not found in Default Project / FocusPod v2" % name)
    part_doc = app.activeDocument
    # if the skeleton is already open (its owner may be working in it), use that and never close it
    already = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name == name]
    skel_doc = already[0] if already else app.documents.open(files[0], False)          # invisible
    try:
        skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
        part_doc.activate()
        root = design.rootComponent
        di = root.features.deriveFeatures.createInput(skel)
        di.isIncludeFavoriteParameters = True
        di.sourceEntities = [skel.rootComponent.xYConstructionPlane]   # parameters only
        d = root.features.deriveFeatures.add(di)
        d.timelineObject.name = "DERIVE - SKELETON PARAMETERS (%s)" % name
        for pl in root.constructionPlanes:          # the derived plane only carries the link; keep it hidden
            if pl.isLightBulbOn and "PLANE - " not in pl.name:
                pl.isLightBulbOn = False
    finally:
        if not already:
            skel_doc.close(False)
        part_doc.activate()
    return files[0].versionNumber


def add_params(design, repo_root):
    app = adsk.core.Application.get()
    if ARGS.get("link", "derive") == "derive":
        skel_name = ARGS.get("skeleton", "100000_P04_POD-SKELETON_CAD")
        ver = derive_skeleton(app, design, skel_name)
        for n in SKELETON_NAMES:
            ref = design.allParameters.itemByName(n + "_Ref")
            if ref is None:
                raise RuntimeError("the skeleton has no favorite parameter %s (derived as %s_Ref)" % (n, n))
            design.userParameters.add(n, vi(n + "_Ref"), ref.unit, "LINKED: %s_Ref, derived from %s v%d (skeleton is "
                                                                 "the single source)" % (n, skel_name, ver))
        n_skel = len(SKELETON_NAMES)
    else:
        skel = skeleton_params(repo_root)
        used = needed_skeleton(skel, WALL_PARAMS)
        for name, expr, unit, status, src in used:
            design.userParameters.add(name, vi(expr), unit, "%s: %s [copied from pod_skeleton.py PARAMS, link=parse]" % (
                status.upper(), src))
        n_skel = len(used)
    for name, expr, unit, status, src in WALL_PARAMS:
        p = design.userParameters.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
        if p is None:
            raise RuntimeError("could not add parameter " + name)
    return n_skel, len(WALL_PARAMS)


def new_comp(parent, key, sheet_metal=False):
    pn, name, vn = PARTS[key]
    tr = adsk.core.Matrix3D.create()
    occ = parent.occurrences.addNewSheetMetalComponent(tr) if sheet_metal else parent.occurrences.addNewComponent(tr)
    c = occ.component
    c.name = ("%s %s" % (pn, name)).strip()
    c.partNumber = pn
    c.description = "%s | %s | %s" % (name, vn, REV)
    return c


def sx(expr):
    """X coordinate expression on this side: expr is the distance from the pod centre plane."""
    return "-(%s)" % expr if S < 0 else "(%s)" % expr


def span(design, a, b):
    """Order two coordinate expressions by value: (low, high)."""
    return (a, b) if ev(design, a) <= ev(design, b) else (b, a)


def xy_plane(comp, z_expr, design, label):
    if abs(ev(design, z_expr)) < 1e-9:
        return comp.xYConstructionPlane
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, vi(z_expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    return pl


def box(design, comp, label, xr, yr, zr, op="new", body=None, plane=None):
    """Axis-aligned box: a fully constrained rectangle on the XY plane at z0 (corners dimensioned
    from the sketch origin by the parameter expressions), extruded along +Z to z1.
    op: new | cut | join (cut and join act on `body`). Returns the feature."""
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    x0, x1, y0, y1 = (ev(design, e) for e in (xr[0], xr[1], yr[0], yr[1]))
    pl = plane or xy_plane(comp, zr[0], design, label + " BOTTOM")
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0 * MM, y0 * MM, 0), adsk.core.Point3D.create(x1 * MM, y1 * MM, 0))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            s0, s1 = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(s0.y - s1.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for p in (ln.startSketchPoint, ln.endSketchPoint):
            if all(p != q for q in pts):
                pts.append(p)

    def near(x, y):
        return min(pts, key=lambda p: (p.geometry.x - x * MM) ** 2 + (p.geometry.y - y * MM) ** 2)
    c00, c10, c01 = near(x0, y0), near(x1, y0), near(x0, y1)
    dims = sk.sketchDimensions
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    tp = adsk.core.Point3D.create((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
    dims.addDistanceDimension(c00, c10, H, tp).parameter.expression = "(%s) - (%s)" % (xr[1], xr[0])
    dims.addDistanceDimension(c00, c01, V, tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    if abs(x0) < 1e-6:
        gc.addVerticalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, H, tp).parameter.expression = "abs(%s)" % xr[0]
    if abs(y0) < 1e-6:
        gc.addHorizontalPoints(c00, sk.originPoint)
    else:
        dims.addDistanceDimension(sk.originPoint, c00, V, tp).parameter.expression = "abs(%s)" % yr[0]
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
           "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
           "join": adsk.fusion.FeatureOperations.JoinFeatureOperation}
    ext_in = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), ops[op])
    ext_in.setDistanceExtent(False, vi("(%s) - (%s)" % (zr[1], zr[0])))
    if op != "new" and body is not None:
        ext_in.participantBodies = body if isinstance(body, list) else [body]
    ext = comp.features.extrudeFeatures.add(ext_in)
    ext.name = "%s - %s" % ({"new": "EXTRUDE", "cut": "CUT", "join": "JOIN"}[op], label)
    return ext


def tube(design, comp, label, xr, yr, zr, along, t="tube_t"):
    """Hollow member (20 x 40 or 40 x 40, wall t): outer box, then the bore cut through its length.
    along: 'y' (rail) or 'z' (stile); t: 'tube_t' (perimeter, 1.2) or 'stud_t' (intermediate studs, 1.0, D-85)."""
    ext = box(design, comp, label + " TUBE", xr, yr, zr)
    b = ext.bodies.item(0)
    xr, yr, zr = span(design, *xr), span(design, *yr), span(design, *zr)
    bx = ("(%s) + %s" % (xr[0], t), "(%s) - %s" % (xr[1], t))
    if along == "y":
        box(design, comp, label + " BORE", bx, yr, ("(%s) + %s" % (zr[0], t), "(%s) - %s" % (zr[1], t)), "cut", b)
    else:
        box(design, comp, label + " BORE", bx, ("(%s) + %s" % (yr[0], t), "(%s) - %s" % (yr[1], t)), zr, "cut", b)
    b.name = label
    return b


def pattern_y(comp, bodies, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for b in bodies:
        coll.add(b)
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, comp.yConstructionAxis, vi(count_expr), vi(pitch_expr),
        adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    # Fusion 2706 defaults direction two to 3 instances at 0 mm when it isn't set, which stacks 3
    # identical bodies on every instance (found on the first L1 build, 2026-10-31): set it to 1.
    pin.setDirectionTwo(comp.zConstructionAxis, vi("1"), vi("1 mm"))
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


AXES = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def origin_plane(comp, axis):
    """The origin plane normal to a model axis."""
    return {"x": comp.yZConstructionPlane, "y": comp.xZConstructionPlane, "z": comp.xYConstructionPlane}[axis]


def plane_at(design, comp, axis, expr, label):
    """Construction plane normal to `axis` at coordinate `expr`. An offset runs along the origin plane's
    normal, which need not point along +axis (Fusion's XZ plane), so the sign follows that normal."""
    base = origin_plane(comp, axis)
    if abs(ev(design, expr)) < 1e-9:
        return base
    n = base.geometry.normal
    sign = 1 if {"x": n.x, "y": n.y, "z": n.z}[axis] > 0 else -1
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(base, vi(expr if sign > 0 else "-(%s)" % expr))
    pl = comp.constructionPlanes.add(pin)
    pl.name = "PLANE - %s" % label
    o = pl.geometry.origin
    got = {"x": o.x, "y": o.y, "z": o.z}[axis] * 10.0
    if abs(got - ev(design, expr)) > 0.01:
        raise RuntimeError("plane %s landed at %s = %.2f, not %.2f" % (label, axis, got, ev(design, expr)))
    return pl


def sketch_axis_of(sk, model_axis):
    """Which sketch axis ('x' or 'y') a model axis maps to on this sketch."""
    o = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, 0))
    e = sk.modelToSketchSpace(adsk.core.Point3D.create(*AXES[model_axis]))
    return "x" if abs(e.x - o.x) > abs(e.y - o.y) else "y"


def hole(design, comp, body, axis, plane_expr, into, pos, dia, depth, label):
    """A simple hole feature on a plane normal to `axis` at `plane_expr`, drilled `into` (+1 or -1 along
    the axis) for `depth`. pos: {model axis: coordinate expression} for the two in-plane axes. The centre
    point is dimensioned from the sketch origin by those expressions, so the sketch is fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "HOLE CENTRE - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    pt = sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM)))
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(pt, sk.originPoint)
        else:
            g = pt.geometry
            tp = adsk.core.Point3D.create(g.x + 0.5, g.y + 0.5, 0)
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, pt, H if sa == "x" else V,
                                                     tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    hin = comp.features.holeFeatures.createSimpleInput(vi(dia))
    hin.setPositionBySketchPoint(pt)
    hin.setDistanceExtent(vi(depth))
    n = pl.geometry.normal
    if into * {"x": n.x, "y": n.y, "z": n.z}[axis] > 0:
        hin.isDefaultDirection = False       # a hole runs against the plane normal unless flipped
    hin.participantBodies = [body]
    h = comp.features.holeFeatures.add(hin)
    h.name = "HOLE - %s" % label
    return h


def rect_on_x(design, comp, x_expr, yr, zr, label):
    """Fully constrained rectangle on a plane normal to X at x_expr, spanning model Y yr and Z zr."""
    yr, zr = span(design, *yr), span(design, *zr)
    pl = plane_at(design, comp, "x", x_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    x = ev(design, x_expr)
    y0, y1, z0, z1 = (ev(design, e) for e in (yr[0], yr[1], zr[0], zr[1]))

    def sp(y, z):
        return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, z * MM))
    rect = sk.sketchCurves.sketchLines.addTwoPointRectangle(sp(y0, z0), sp(y1, z1))
    gc = sk.geometricConstraints
    for ln in rect:
        if not any(c.objectType in (adsk.fusion.HorizontalConstraint.classType(),
                                    adsk.fusion.VerticalConstraint.classType()) for c in ln.geometricConstraints):
            a, b = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            (gc.addHorizontal if abs(a.y - b.y) < 1e-9 else gc.addVertical)(ln)
    pts = []
    for ln in rect:
        for q in (ln.startSketchPoint, ln.endSketchPoint):
            if all(q != o for o in pts):
                pts.append(q)

    def near(y, z):
        t = sp(y, z)
        return min(pts, key=lambda q: (q.geometry.x - t.x) ** 2 + (q.geometry.y - t.y) ** 2)
    c00, c10, c01 = near(y0, z0), near(y1, z0), near(y0, z1)
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    ay, az = sketch_axis_of(sk, "y"), sketch_axis_of(sk, "z")
    o = {"x": H, "y": V}
    mid = sp((y0 + y1) / 2, (z0 + z1) / 2)
    tp = adsk.core.Point3D.create(mid.x, mid.y, 0)
    sk.sketchDimensions.addDistanceDimension(c00, c10, o[ay], tp).parameter.expression = "(%s) - (%s)" % (yr[1], yr[0])
    sk.sketchDimensions.addDistanceDimension(c00, c01, o[az], tp).parameter.expression = "(%s) - (%s)" % (zr[1], zr[0])
    for axis, val, e in ((ay, y0, yr[0]), (az, z0, zr[0])):
        if abs(val) < 1e-6:
            (gc.addVerticalPoints if axis == "x" else gc.addHorizontalPoints)(c00, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, c00, o[axis], tp).parameter.expression = "abs(%s)" % e
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    return sk


def pattern_feat(comp, feats, axis, count_expr, pitch_expr, label):
    coll = adsk.core.ObjectCollection.create()
    for f in feats:
        coll.add(f)
    ax = {"x": comp.xConstructionAxis, "y": comp.yConstructionAxis, "z": comp.zConstructionAxis}[axis]
    pin = comp.features.rectangularPatternFeatures.createInput(
        coll, ax, vi(count_expr), vi(pitch_expr), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    other = comp.zConstructionAxis if axis != "z" else comp.xConstructionAxis
    pin.setDirectionTwo(other, vi("1"), vi("1 mm"))      # see pattern_y
    pat = comp.features.rectangularPatternFeatures.add(pin)
    pat.name = "PATTERN - %s" % label
    return pat


HW_SITES = []          # rivnut sites recorded by the joint features, built as bodies by build_hardware
ALLOWED_CLASH = []     # body name pairs that overlap by design (a spigot's thread in its rivnut's bore)


def hw_site(label, axis, face, into, pos, pat=None, washer=True, spigot=False):
    """Record a rivnut hole for the hardware bodies: the same plane, centre and pattern as the hole.
    into: the hole's direction into the tube; the head and any washer stand the other way, in the joint gap."""
    HW_SITES.append({"label": label, "axis": axis, "face": face, "out": -into, "pos": pos, "pat": pat,
                     "washer": washer, "spigot": spigot})


def cyl(design, comp, label, axis, plane_expr, out, pos, od, length, bore=None):
    """New body: a cylinder (or a tube, with `bore`) on a plane normal to `axis` at `plane_expr`, extruded `out`
    (+1 or -1 along the axis) by `length`. The circle's centre is dimensioned from the sketch origin by the `pos`
    expressions and its diameters by `od` and `bore`, so the sketch is fully constrained."""
    pl = plane_at(design, comp, axis, plane_expr, label)
    sk = comp.sketches.add(pl)
    sk.name = "SKETCH - %s" % label
    c = {axis: ev(design, plane_expr)}
    for a, e in pos.items():
        c[a] = ev(design, e)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(c["x"] * MM, c["y"] * MM, c["z"] * MM))
    circles = sk.sketchCurves.sketchCircles
    outer = circles.addByCenterRadius(ctr, ev(design, od) / 2.0 * MM)
    cp = outer.centerSketchPoint
    H = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    V = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    g = cp.geometry
    tp = adsk.core.Point3D.create(g.x + 0.7, g.y + 0.7, 0)
    for a, e in pos.items():
        sa = sketch_axis_of(sk, a)
        if abs(ev(design, e)) < 1e-6:
            (sk.geometricConstraints.addVerticalPoints if sa == "x" else
             sk.geometricConstraints.addHorizontalPoints)(cp, sk.originPoint)
        else:
            sk.sketchDimensions.addDistanceDimension(sk.originPoint, cp, H if sa == "x" else V,
                                                     tp).parameter.expression = "abs(%s)" % e
    sk.sketchDimensions.addDiameterDimension(outer, tp).parameter.expression = od
    if bore:
        inner = circles.addByCenterRadius(cp, ev(design, bore) / 2.0 * MM)
        sk.sketchDimensions.addDiameterDimension(inner, tp).parameter.expression = bore
    if not sk.isFullyConstrained:
        raise RuntimeError("sketch not fully constrained: " + sk.name)
    v, k = ev(design, plane_expr), "xyz".index(axis)
    for dirn in (adsk.fusion.ExtentDirections.PositiveExtentDirection,
                 adsk.fusion.ExtentDirections.NegativeExtentDirection):
        profs = [sk.profiles.item(i) for i in range(sk.profiles.count)]
        prof = max(profs, key=lambda q: q.profileLoops.count) if bore else profs[0]
        ein = comp.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ein.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(vi(length)), dirn)
        f = comp.features.extrudeFeatures.add(ein)
        b = bbox(f.bodies.item(0))
        if abs((b[k] if out > 0 else b[k + 3]) - v) < 0.01:
            f.name = "EXTRUDE - %s" % label
            return f.bodies.item(0)
        f.deleteMe()
    raise RuntimeError("cylinder %s: neither direction starts on its plane" % label)


def join_bodies(comp, target, tools, label):
    coll = adsk.core.ObjectCollection.create()
    for t in tools:
        coll.add(t)
    cin = comp.features.combineFeatures.createInput(target, coll)
    cin.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    f = comp.features.combineFeatures.add(cin)
    f.name = "COMBINE - %s" % label
    return f.bodies.item(0) if f.bodies.count else target


def name_along(comp, axis, known, first, prefix):
    """Name a pattern's bodies and its original by their order along +axis: PREFIX 1..n."""
    k = "xyz".index(axis)
    group = [first] + [b for b in comp.bRepBodies if not any(b == q for q in known) and not b == first]
    group.sort(key=lambda b: (b.boundingBox.minPoint.x, b.boundingBox.minPoint.y, b.boundingBox.minPoint.z)[k])
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along %s: %s" % (axis, prefix))
    out = {}
    for i, b in enumerate(group):
        b.name = "%s %d" % (prefix, i + 1)
        out[b.name] = b
    return out


def build_hardware(design, root, out):
    """The joint hardware the panel carries from the factory, as bodies (joints register 2.1; sizes H-03, H-05,
    H-08): at every rivnut hole an H-03 rivnut, with an H-08 stop washer under its head at a stopped joint, and an
    H-05 spigot in each spigot rivnut. One body per site, patterned like its holes, so an edit moves them with
    the holes. The rivnut is its installed envelope: head, and the body to its installed length (the bulge inside
    the tube is not modelled); threads are shown at 6 mm. The bolts stay in the parts list (bought, ISO)."""
    if not HW_SITES:
        return
    comps = {}
    n0 = len(out)
    for s in HW_SITES:
        ax, face, o, pos, lab = s["axis"], s["face"], s["out"], s["pos"], s["label"]
        sg = "+" if o > 0 else "-"
        made = []
        if s["washer"]:
            c = comps.get("stopw") or comps.setdefault("stopw", new_comp(root, "stopw"))
            w = cyl(design, c, "STOP WASHER %s" % lab, ax, face, o, pos, "stopw_od", "stopw_t", "stopw_id")
            made.append((c, w, "STOP WASHER - %s" % lab))
            head0 = "(%s) %s stopw_t" % (face, sg)
        else:
            head0 = face
        c = comps.get("rivnut") or comps.setdefault("rivnut", new_comp(root, "rivnut"))
        head = cyl(design, c, "RIVNUT HEAD %s" % lab, ax, head0, o, pos, "rivnut_head_d", "rivnut_head_t", "m6_d")
        shank = cyl(design, c, "RIVNUT BODY %s" % lab, ax, head0, -o, pos, "rivnut_body_d", "rivnut_len", "m6_d")
        made.append((c, join_bodies(c, head, [shank], "RIVNUT %s" % lab), "RIVNUT - %s" % lab))
        if s["spigot"]:
            c = comps.get("spigot") or comps.setdefault("spigot", new_comp(root, "spigot"))
            top = "(%s) %s rivnut_head_t" % (head0, sg)
            pin = cyl(design, c, "SPIGOT PIN %s" % lab, ax, top, o, pos, "spigot_pin_d",
                      "spigot_proud - rivnut_head_t" + (" - stopw_t" if s["washer"] else ""))
            thread = cyl(design, c, "SPIGOT THREAD %s" % lab, ax, top, -o, pos, "m6_d", "spigot_thread_l")
            made.append((c, join_bodies(c, pin, [thread], "SPIGOT %s" % lab), "SPIGOT - %s" % lab))
        for c, b, name in made:
            if s["pat"]:
                pax, cnt, pitch = s["pat"]
                known = [q for q in c.bRepBodies if not q == b]
                pattern_feat(c, [b], pax, cnt, pitch, name)
                out.update(name_along(c, pax, known, b, name))
            else:
                b.name = name
                out[name] = b
        if s["spigot"]:
            rv = [nm for c, b, nm in made if nm.startswith("RIVNUT")][0]
            sp = [nm for c, b, nm in made if nm.startswith("SPIGOT")][0]
            if s["pat"]:
                cnt = int(round(design.userParameters.itemByName(s["pat"][1]).value)) if not s["pat"][1].isdigit() \
                    else int(s["pat"][1])
                ALLOWED_CLASH.extend(("%s %d" % (rv, i + 1), "%s %d" % (sp, i + 1)) for i in range(cnt))
            else:
                ALLOWED_CLASH.append((rv, sp))
    for key, label in (("rivnut", "ALUMINIUM 5056 RIVNUT"), ("stopw", "ALUMINIUM STOP WASHER"),
                       ("spigot", "STAINLESS SPIGOT")):
        if key in comps:
            set_material(design, list(comps[key].bRepBodies), key, label)
    print("step 7: joint hardware, %d bodies in %d components (%s)" % (
        len(out) - n0, len(comps), ", ".join(c.partNumber for c in comps.values())))


def settle_props(app, root, pn, desc, seconds=30.0):
    """The cloud can overwrite the root component's part number and description: --doc-new's first upload
    finishing after a short build (the skin, 2026-10-31) put the document's timestamp name in the part
    number, and new documents came out of their save with an empty description (B1, R1). Wait until the
    document has its data file and both have held for a second, setting them again when they change."""
    import time
    t0, held = time.time(), 0
    while time.time() - t0 < seconds:
        adsk.doEvents()
        if root.partNumber != pn or root.description != desc:
            root.partNumber = pn
            root.description = desc
            held = 0
        elif app.activeDocument.dataFile is not None:
            held += 1
            if held >= 5:
                return True
        time.sleep(0.2)
    return root.partNumber == pn and root.description == desc


def save_holding_props(app, doc, root, pn, desc, note, tries=3):
    """Save, wait for the upload to finish (the data file's version moves on), and check the part number and
    description came through; if the upload reset them, set them again and save again."""
    import time
    for attempt in range(1, tries + 1):
        if not settle_props(app, root, pn, desc):
            raise RuntimeError("root part number / description would not hold before the save (%r, %r)" % (
                root.partNumber, root.description))
        before = doc.dataFile.versionNumber if doc.dataFile else 0
        if not doc.save(note if attempt == 1 else "%s (part number and description set again)" % note):
            raise RuntimeError("save failed")
        t0 = time.time()
        while time.time() - t0 < 90.0 and not (doc.dataFile and doc.dataFile.versionNumber > before):
            adsk.doEvents()
            time.sleep(0.25)
        for _i in range(12):                    # 3 s more for the cloud to send any property back
            adsk.doEvents()
            time.sleep(0.25)
        if root.partNumber == pn and root.description == desc:
            return doc.dataFile.versionNumber if doc.dataFile else None
        print("the save reset the root properties (%r, %r); setting them again" % (root.partNumber, root.description))
    raise RuntimeError("root part number / description did not survive %d saves" % tries)


def name_by_y(comp, known, first, prefix):
    """Name the pattern's copies and the original by their order along +Y: PREFIX 1..n.
    Fusion API objects compare with == but are not hashable, so `known` is a list."""
    group = [first] + [b for b in comp.bRepBodies if not any(b == k for k in known) and not b == first]
    group.sort(key=lambda b: b.boundingBox.minPoint.y)
    if not group[0] == first:
        raise RuntimeError("pattern went the wrong way along Y: %s" % prefix)
    out = {}
    for i, b in enumerate(group):
        b.name = "%s %d" % (prefix, i + 1)
        out[b.name] = b
    return out


def bbox(entity):
    b = entity.boundingBox
    return [round(v * 10.0, 2) for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                                         b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


def size(b):
    return "%g x %g x %g" % (round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2))


def set_material(design, bodies, key, label):
    lib = adsk.core.Application.get().materialLibraries.itemByName("Fusion Material Library")
    base = lib.materials.itemByName("Aluminum")
    name = "%s %g kg/m3 (%s)" % (label, round(DENSITY[key][0], 1), DENSITY[key][1])
    mat = design.materials.itemByName(name)
    if mat is None:
        mat = design.materials.addByCopy(base, name)
        mat.materialProperties.itemById("structural_Density").value = DENSITY[key][0]
    for b in bodies:
        b.material = mat
    return mat


def clash_check(bodies, allowed=()):
    """Pairwise solid intersections over 1 mm3; fails on any pair not in `allowed`."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            ba, bb = bbox(a), bbox(b)
            if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                continue
            t1, t2 = tbm.copy(a), tbm.copy(b)
            tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            vol = t1.volume * 1000.0 if t1 else 0.0
            if vol > 1.0:
                hits.append((a.name, b.name, round(vol)))
    bad = [h for h in hits if frozenset(h[:2]) not in {frozenset(p) for p in allowed}]
    return hits, bad


def clear_design(design):
    """rebuild=1: empty a design this script built before (same root part number)."""
    tl = design.timeline
    if tl.count:
        tl.moveToBeginning()
        tl.deleteAllAfterMarker()
    for i in range(design.userParameters.count - 1, -1, -1):
        design.userParameters.item(i).deleteMe()
    for i in range(design.materials.count - 1, -1, -1):
        m = design.materials.item(i)
        if " kg/m3 (" in m.name:
            try:
                m.deleteMe()
            except Exception:       # still in use by nothing after the timeline is gone; ignore
                pass


# ---------------------------------------------------------------- geometry expressions

X_OUT = sx("pod_w / 2")                          # outer face of the skin
X_SKIN_IN = sx("pod_w / 2 - skin_t")             # inner face of the skin
X_FRAME_OUT = sx("pod_w / 2 - skin_t - bond_t")  # outer face of the frame, behind the 3 mm bond line
X_FRAME_IN = sx("pod_w / 2 - outer_t")           # inner face of the frame (side frames' inner face)
X_IN = sx("pod_w / 2 - stack_t")                 # room-side face of the lining (felt face)
X_TRAY_BACK = sx("pod_w / 2 - stack_t + cass_t")   # back face of the tray base (4 mm from the frame)
X_FELT_FACE = sx("pod_w / 2 - stack_t + tray_t")   # felt's room face, behind the lips
X_FELT_BACK = sx("pod_w / 2 - stack_t + tray_t + felt_t")

# panel envelope: the skeleton's side panel (seam gaps at the decor, on the band and at the row seam)
Y_FRONT = "pod_d / 2 - wall_depth + seam_gap"    # panel front end: 2.26 behind the decor back plate (F-008)
Y_BACK = "pod_d / 2"                             # outer face of the back wall
Y_FRAME_BACK = "pod_d / 2 - skin_t"              # inside of the skin's back return
Y_CASS_FRONT = "pod_d / 2 - wall_depth"          # the lining starts at the decor back plate (skeleton P04)
Y_CASS_BACK = "pod_d / 2 - stack_t + cass_t"     # side lining end, past the back lining (D-57)

# rows as skeleton P04: panel_z0 = the walls' bottom, one seam_gap above the band top (F-008)
Z0 = "panel_z0" if ROW == 1 else "panel_z0 + side_h + seam_gap"
Z1 = "panel_z0 + side_h" if ROW == 1 else "pod_h"
Z_SKIN0 = "(%s) + skin_setback" % Z0
Z_SKIN1 = "(%s) - skin_setback" % Z1 if ROW == 1 else Z1   # the upper skins run to the roof datum
Z_CASS1 = Z1 if ROW == 1 else "pod_h - outer_t - lin_gap"


def build_panel(design, root):
    out = {}
    want = WANT[PART]
    frame, skin, fill = (new_comp(root, k) if k in want else None for k in ("frame", "skin", "fill"))
    print("step 1: components %s" % ", ".join(c.name for c in (root, frame, skin, fill) if c))
    if STOP_AFTER <= 1:
        return out
    xf = (X_FRAME_OUT, X_FRAME_IN)
    yf = (Y_FRONT, Y_FRAME_BACK)
    zs = ("(%s) + tube_w" % Z0, "(%s) - top_h" % Z1)
    if frame:
        build_frame(design, frame, out, xf, yf, zs)
    if skin:
        build_skin(design, skin, out)
    if fill:
        build_fill(design, fill, out, xf, zs)
    if frame:
        joint_features(design, frame, fill, out)
    if PART == "panel":
        build_hardware(design, root, out)
    set_material(design, [b for k, b in out.items() if k.startswith(("RAIL", "STILE"))], "frame",
                 "ALUMINIUM TUBE 6063-T6 MILL")
    set_material(design, [b for k, b in out.items() if k.startswith("SKIN")], "skin", "ACP 3 MM EV3038")
    set_material(design, [b for k, b in out.items() if k.startswith("FILL")], "fill", "PET FILL 40 MM")
    return out


def build_frame(design, frame, out, xf, yf, zs):
    # rails run the full frame length; stiles fit between them (butt joints, member joint method HOLD H11)
    out["RAIL - BOTTOM"] = tube(design, frame, "RAIL - BOTTOM", xf, yf, (Z0, "(%s) + tube_w" % Z0), "y")
    out["RAIL - TOP"] = tube(design, frame, "RAIL - TOP", xf, yf, ("(%s) - top_h" % Z1, Z1), "y")
    print("step 2: rails", [(k, size(bbox(v))) for k, v in out.items()])
    if STOP_AFTER <= 2:
        return out
    out["STILE - FRONT"] = tube(design, frame, "STILE - FRONT", xf, (Y_FRONT, "(%s) + tube_w" % Y_FRONT), zs, "z")
    out["STILE - BACK"] = tube(design, frame, "STILE - BACK", xf, ("(%s) - corner_w" % Y_FRAME_BACK, Y_FRAME_BACK),
                               zs, "z")
    mid = tube(design, frame, "STILE - MID 1", xf,
               ("(%s) + stile_pitch" % Y_FRONT, "(%s) + stile_pitch + tube_w" % Y_FRONT), zs, "z", "stud_t")
    out["STILE - MID 1"] = mid
    pattern_y(frame, [mid], "stile_n_mid", "stile_pitch", "STILES - MID")
    out.update(name_by_y(frame, list(out.values()), mid, "STILE - MID"))
    print("step 3: stiles, %d mid at pitch %.2f" % (
        round(design.userParameters.itemByName("stile_n_mid").value),
        design.userParameters.itemByName("stile_pitch").value * 10.0))


def build_skin(design, skin, out):
    yskin = (Y_FRONT, Y_BACK)
    zskin = (Z_SKIN0, Z_SKIN1)
    plate = box(design, skin, "SKIN PLATE", (X_OUT, X_SKIN_IN), yskin, zskin).bodies.item(0)
    box(design, skin, "SKIN BACK RETURN", (X_SKIN_IN, sx("pod_w / 2 - skin_t - skin_ret")),
        (Y_FRAME_BACK, Y_BACK), zskin, "join", plate)
    plate.name = "SKIN - ACP 3 WITH BACK RETURN"
    out[plate.name] = plate
    print("step 4: skin", size(bbox(plate)))


def build_fill(design, fill, out, xf, zs):
    # fill bays: one per bay between the stiles; the last bay (against the 40 mm back stile) is its own box
    bay = box(design, fill, "FILL BAY 1", xf, ("(%s) + tube_w" % Y_FRONT, "(%s) + stile_pitch" % Y_FRONT),
              zs).bodies.item(0)
    bay.name = "FILL - BAY 1"
    out[bay.name] = bay
    pattern_y(fill, [bay], "stile_n_mid", "stile_pitch", "FILL BAYS")
    out.update(name_by_y(fill, list(out.values()), bay, "FILL - BAY"))
    last = box(design, fill, "FILL BAY LAST", xf, ("(%s) + stile_n_mid * stile_pitch + tube_w" % Y_FRONT,
                                                    "(%s) - corner_w" % Y_FRAME_BACK), zs).bodies.item(0)
    last.name = "FILL - BAY %d" % (sum(1 for k in out if k.startswith("FILL")) + 1)
    out[last.name] = last
    # pockets beside every bolt this panel drives (FR-10): one cut per bolt, at the bolt's own rule, with no
    # fixed target, so it cuts whichever fill piece it meets in the fill component, also after an edit changes
    # the stile count (a pattern of a cut can't reach other bodies: PATTERN_FEATURES_NO_PASTE_INT_EDGES; a fixed
    # target list misses the pieces an edit adds)
    z_rail_top = "(%s) + tube_w" % Z0
    # the bottom rail's bolts (J-BASE-01 on a lower panel, J-WALL-01 on an upper one) follow the 220 rule (R-J14)
    n_now = int(round(design.userParameters.itemByName("n_len_bolt").value))
    ys = ["(%s) + bolt_edge + %d * len_bolt_pitch" % (Y_FRONT, i) for i in range(n_now)]
    for i, yc in enumerate(ys):
        box(design, fill, "FILL POCKET BOTTOM BOLT %d" % (i + 1), xf,
            ("(%s) - pocket_w / 2" % yc, "(%s) + pocket_w / 2" % yc), (z_rail_top, "(%s) + pocket_w" % z_rail_top),
            "cut")
    z_j1 = "(%s) + bolt_edge" % Z0
    for j in range(3):
        zc = "(%s) + %d * side_jnt_pitch" % (z_j1, j)
        box(design, fill, "FILL POCKET DECOR BOLT %d" % (j + 1), xf,
            ("(%s) + tube_w" % Y_FRONT, "(%s) + tube_w + pocket_w" % Y_FRONT),
            ("(%s) - pocket_w / 2" % zc, "(%s) + pocket_w / 2" % zc), "cut")
    print("step 5: fill, %d bays, pockets at every bolt this panel drives" % sum(1 for k in out if k.startswith("FILL")))


def joint_features(design, frame, fill, out):
    """Site joint holes per the joints register (V2-ENG-JNT-01 P01, ce1f415). The fill pockets are in step 5."""
    xc = sx("pod_w / 2 - skin_t - bond_t - tube_d / 2")     # centre line of the frame depth
    y_b1 = "(%s) + bolt_edge" % Y_FRONT                     # 220 rule on every edge (R-J14)
    n_b, p_b = "n_len_bolt", "len_bolt_pitch"
    t = "tube_t"
    bot, top = out["RAIL - BOTTOM"], out["RAIL - TOP"]
    front, back = out["STILE - FRONT"], out["STILE - BACK"]
    zb0, zb1 = Z0, "(%s) + tube_w" % Z0                      # bottom rail bottom and top faces
    zt1 = Z1                                                 # top rail top face
    # bottom rail, bolt side of J-BASE-01 (lower) or J-WALL-01 (upper): FR-02 + FR-03 at each bay
    # bottom rail: J-BASE-01 (lower) or J-WALL-01 bolt side (upper), both at the 220 rule
    a = hole(design, frame, bot, "z", zb0, +1, {"x": xc, "y": y_b1}, "bolt_d", t, "BOTTOM RAIL BOLT CLEARANCE 1")
    b = hole(design, frame, bot, "z", zb1, -1, {"x": xc, "y": y_b1}, "access_d", t, "BOTTOM RAIL KEY ACCESS 1")
    pattern_feat(frame, [a, b], "y", n_b, p_b, "BOTTOM RAIL BOLT HOLES")
    # bottom rail locating: round spigot hole at the front end, slot along X at the back-corner end (FR-05)
    hole(design, frame, bot, "z", zb0, +1, {"x": xc, "y": "(%s) + spigot_edge" % Y_FRONT}, "spigot_d", t,
         "BOTTOM RAIL SPIGOT ROUND")
    ys = "(%s) - spigot_edge" % Y_BACK
    half = "(spigot_slot - spigot_d) / 2"
    box(design, frame, "BOTTOM RAIL SPIGOT SLOT", ("(%s) - %s" % (xc, half), "(%s) + %s" % (xc, half)),
        ("(%s) - spigot_d / 2" % ys, "(%s) + spigot_d / 2" % ys), (zb0, "(%s) + %s" % (zb0, t)), "cut", bot)
    for i, sgn in enumerate(("-", "+")):
        hole(design, frame, bot, "z", zb0, +1, {"x": "(%s) %s %s" % (xc, sgn, half), "y": ys}, "spigot_d", t,
             "BOTTOM RAIL SPIGOT SLOT END %d" % (i + 1))
    if ROW == 1:
        # top rail, nut side of J-WALL-01: rivnut at each bay (FR-01) and 2 spigot rivnuts (FR-04)
        r = hole(design, frame, top, "z", zt1, -1, {"x": xc, "y": y_b1}, "rivnut_d", t, "TOP RAIL RIVNUT 1")
        pattern_feat(frame, [r], "y", n_b, p_b, "TOP RAIL RIVNUTS")
        hw_site("TOP RAIL", "z", zt1, -1, {"x": xc, "y": y_b1}, ("y", n_b, p_b))
        for k, ys_ in (("FRONT", "(%s) + spigot_edge" % Y_FRONT), ("BACK", "(%s) - spigot_edge" % Y_BACK)):
            hole(design, frame, top, "z", zt1, -1, {"x": xc, "y": ys_}, "rivnut_d", t, "TOP RAIL SPIGOT RIVNUT %s" % k)
            hw_site("TOP RAIL SPIGOT %s" % k, "z", zt1, -1, {"x": xc, "y": ys_}, washer=False, spigot=True)
    if ROW == 2:
        # 40 x 40 top member, nut side of J-CEIL-01 side edges: a rivnut in its room-side face at each bay middle
        # positions follow the ceiling's edge, not this panel's: from Y -645 at pitch 351.67 (PM ruling 16:55)
        y_c1 = "(%s) + bolt_edge" % Y_CASS_FRONT
        r = hole(design, frame, top, "x", X_FRAME_IN, S, {"y": y_c1, "z": "pod_h - ceil_bolt_dz"}, "rivnut_d", t,
                 "TOP MEMBER CEILING RIVNUT 1")
        pattern_feat(frame, [r], "y", n_b, "ceil_bolt_pitch", "TOP MEMBER CEILING RIVNUTS")
        hw_site("TOP MEMBER CEILING", "x", X_FRAME_IN, S, {"y": y_c1, "z": "pod_h - ceil_bolt_dz"},
                ("y", n_b, "ceil_bolt_pitch"))
    z_j1 = "(%s) + bolt_edge" % Z0
    # front stile, bolt side of J-FRONT-01 (decor block): FR-02 in the front wall, FR-03 in the back wall
    a = hole(design, frame, front, "y", Y_FRONT, +1, {"x": xc, "z": z_j1}, "bolt_d", t, "FRONT STILE BOLT CLEARANCE 1")
    b = hole(design, frame, front, "y", "(%s) + tube_w" % Y_FRONT, -1, {"x": xc, "z": z_j1}, "access_d", t,
             "FRONT STILE KEY ACCESS 1")
    pattern_feat(frame, [a, b], "z", "n_side_jnt", "side_jnt_pitch", "FRONT STILE BOLT HOLES")
    # 40 x 40 back stile, nut side of J-WALL-02 (back corner): rivnut in the room-side face (FR-01, FR-06)
    r = hole(design, frame, back, "x", X_FRAME_IN, S, {"y": "bolt_line_y", "z": "corner_z0 + bolt_edge"},
             "rivnut_d", t, "BACK STILE CORNER RIVNUT 1")
    pattern_feat(frame, [r], "z", "n_side_jnt", "corner_bolt_pitch", "BACK STILE CORNER RIVNUTS")
    hw_site("BACK STILE CORNER", "x", X_FRAME_IN, S, {"y": "bolt_line_y", "z": "corner_z0 + bolt_edge"},
            ("z", "n_side_jnt", "corner_bolt_pitch"))
    holes = sum(c.features.holeFeatures.count for c in [frame])
    print("step 6: joint features: %d hole features (before patterns)" % holes)


def build_tray(design, root, tray, yc, zc):
    """Sheet metal tray, the ceiling tray's recipe (v2/01-CAD-Native/ceiling): base flange on the plane of the
    tray back, returns tray_h deep toward the room, 12 mm lips turned in to hold the felt. Edge flanges need the
    sheet metal component active. Bend position and lip direction are tried both ways and kept only when the
    outer faces land on the cassette outline."""
    rule = design.designSheetMetalRules.itemByName("GALV STEEL 0.5 - LINING TRAY")
    if rule is None:
        rule = design.designSheetMetalRules.addByCopy(tray.activeSheetMetalRule, "GALV STEEL 0.5 - LINING TRAY")
    rule.thickness.expression = "%.4f mm" % ev(design, "tray_t")   # a rule takes values only (Fusion 2706)
    rule.bendRadius.expression = "Thickness"                        # = bend_r (1 x t)
    rule.kFactor = 0.44
    rule.twoBendReliefShape = adsk.fusion.TwoBendReliefShapes.SquareTwoBendReliefShape
    tray.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == tray][0]
    occ.activate()
    want_yz = [ev(design, e) for e in (span(design, *yc) + span(design, *zc))]
    xb = ev(design, X_TRAY_BACK)
    try:
        sk = rect_on_x(design, tray, X_TRAY_BACK, yc, zc, "TRAY BASE OUTLINE")
        ff = tray.features.flangeFeatures
        base = None
        for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                       adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
            bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
            bfi.orientation = orient
            f = ff.add(bfi)
            b = bbox(f.bodies.item(0))
            back, room = (b[0], b[3]) if S < 0 else (b[3], b[0])     # the room is toward -S
            if abs(back - xb) < 0.01 and abs(room - (xb - S * ev(design, "tray_t"))) < 0.01:
                base = f
                break
            f.deleteMe()
        if base is None:
            raise RuntimeError("tray: no base flange side lies on the room side of the tray back")
        base.name = "BASE - TRAY"
        body = tray.bRepBodies.item(0)
        body.name = "TRAY - STEEL 0.5 WITH RETURNS AND LIPS"
        xr = xb - S * ev(design, "tray_t")      # room-side face of the base (the room is toward -S)

        def x_edges(x, keep):
            return [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
                    and abs(e.startVertex.geometry.x * 10 - x) < 0.01 and abs(e.endVertex.geometry.x * 10 - x) < 0.01
                    and keep(e)]
        eds = x_edges(xr, lambda e: True)
        if len(eds) != 4:
            raise RuntimeError("tray: expected 4 base edges on the room side, got %d" % len(eds))
        ret = None
        for pos in (adsk.fusion.BendPositionTypes.InsideBendPositionType,
                    adsk.fusion.BendPositionTypes.OutsideBendPositionType):
            efi = ff.createEdgeFlangeInput([], vi("tray_h - tray_t - bend_r"))
            for e in eds:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            efi.bendPositionType = pos
            f = ff.add(efi)
            b = bbox(tray.bRepBodies.item(0))
            if all(abs(g - w) < 0.05 for g, w in zip([b[1], b[4], b[2], b[5]], want_yz)):
                ret = f
                break
            f.deleteMe()
        if ret is None:
            raise RuntimeError("tray: no bend position keeps the returns' outer faces on the outline")
        ret.name = "FLANGE - TRAY RETURNS"
        body = tray.bRepBodies.item(0)
        b = bbox(body)
        xt = b[3] if S < 0 else b[0]         # the returns' tips, at the room side

        def off_outline(e):
            q = e.startVertex.geometry
            return min(abs(q.y * 10 - b[1]), abs(q.y * 10 - b[4]), abs(q.z * 10 - b[2]), abs(q.z * 10 - b[5])) > 0.05 \
                and e.length * 10 > 100
        inner = x_edges(xt, off_outline)
        if len(inner) != 4:
            raise RuntimeError("tray: expected 4 inner tip edges, got %d" % len(inner))
        lip = None
        x_room = ev(design, X_IN)
        for flip in (False, True):
            efi = ff.createEdgeFlangeInput([], vi("lip_w"))
            for e in inner:
                efi.edgeDefinitions.addFullLengthEdge(e)
            efi.isFlipped = flip
            efi.isMiteredCorners = True
            efi.heightDatumType = adsk.fusion.FlangeHeightDatumTypes.OuterFacesFlangeHeightDatumType
            f = ff.add(efi)
            b2 = bbox(tray.bRepBodies.item(0))
            room = b2[3] if S < 0 else b2[0]
            inside = all(abs(g - w) < 0.05 for g, w in zip([b2[1], b2[4], b2[2], b2[5]], want_yz)) and \
                abs(room - x_room) < 0.05
            if inside and f.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                lip = f
                break
            f.deleteMe()
        if lip is None:
            raise RuntimeError("tray: no lip direction keeps the lips inside the outline at the room face")
        lip.name = "FLANGE - TRAY LIPS HOLDING THE FELT"
        body = tray.bRepBodies.item(0)
        big = max((fc for fc in body.faces if fc.geometry.objectType == adsk.core.Plane.classType()
                   and abs(fc.geometry.normal.x) > 0.99), key=lambda fc: fc.area)
        fp = tray.flatPattern or tray.createFlatPattern(big)
        print("FLAT|%s|%s" % (tray.partNumber, size(bbox(fp.flatBody))))
    finally:
        design.activateRootComponent()
    return tray.bRepBodies.item(0)


def build_cassette(design, root):
    out = {}
    want = WANT[PART]
    tray = new_comp(root, "tray", sheet_metal=True) if "tray" in want else None
    felt = new_comp(root, "felt") if "felt" in want else None
    clip = new_comp(root, "clip") if "clip" in want else None
    print("step 1: components %s" % ", ".join(c.name for c in (root, tray, felt, clip) if c))
    if STOP_AFTER <= 1:
        return out
    yc = (Y_CASS_FRONT, Y_CASS_BACK)
    zc = (Z0, Z_CASS1)
    if tray:
        pan = build_tray(design, root, tray, yc, zc)
        out[pan.name] = pan
        print("step 2: tray", size(bbox(pan)))
        set_material(design, [pan], "tray", "GALVANISED STEEL 0.5")
    if felt:
        fb = box(design, felt, "FELT", (X_FELT_FACE, X_FELT_BACK),
                 ("(%s) + tray_t + felt_c" % yc[0], "(%s) - tray_t - felt_c" % yc[1]),
                 ("(%s) + tray_t + felt_c" % zc[0], "(%s) - tray_t - felt_c" % zc[1])).bodies.item(0)
        fb.name = "FELT - PET 9 HELD BY THE TRAY LIPS"
        out[fb.name] = fb
        print("step 3: felt", size(bbox(fb)))
        set_material(design, [fb], "felt", "PET FELT 9 MM DARK GRAY")
    if not clip:
        return out
    # reserved zones for the captive clips (H03): in the 4 mm gap between the frame's inner face and the
    # tray back, on the first and last intermediate stiles of the panel frame, near the top and bottom
    ys = [("(%s) + stile_pitch" % Y_FRONT, "(%s) + stile_pitch + tube_w" % Y_FRONT),
          ("(%s) + stile_n_mid * stile_pitch" % Y_FRONT, "(%s) + stile_n_mid * stile_pitch + tube_w" % Y_FRONT)]
    zs = [("(%s) + clip_zone_dz - clip_zone_h / 2" % Z0, "(%s) + clip_zone_dz + clip_zone_h / 2" % Z0),
          ("(%s) - clip_zone_dz - clip_zone_h / 2" % Z_CASS1, "(%s) - clip_zone_dz + clip_zone_h / 2" % Z_CASS1)]
    n = 0
    for zi, zr in enumerate(zs):
        for yi, yr in enumerate(ys):
            n += 1
            b = box(design, clip, "CLIP ZONE %d" % n, (X_FRAME_IN, X_TRAY_BACK), yr, zr).bodies.item(0)
            b.name = "HOLD - CLIP ZONE %d (%s %s)" % (n, "BOTTOM" if zi == 0 else "TOP", "FRONT" if yi == 0 else "BACK")
            out[b.name] = b
    print("step 4: %d clip zones (HOLD H03)" % n)
    set_material(design, [b for k, b in out.items() if k.startswith("HOLD")], "zone", "RESERVED ZONE")
    return out


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("the active document is not a Fusion design")
    root = design.rootComponent
    pn = PARTS[ROOT_KEY][0]
    if design.userParameters.count or root.occurrences.count or root.bRepBodies.count:
        if ARGS.get("rebuild") != "1":
            raise RuntimeError("the active design is not empty; pass rebuild=1 to rebuild it")
        if root.partNumber != pn and not app.activeDocument.name.startswith(pn + "_"):
            # a root part number set while --doc-new's first upload is still running can be
            # overwritten by it (seen on the first cassette build), so the document name counts too
            raise RuntimeError("refusing to rebuild: root part number is %r, not %s" % (root.partNumber, pn))
        clear_design(design)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    n_skel, n_wall = add_params(design, ARGS["repo_root"])
    root.partNumber = pn
    desc = "%s | %s | %s | position %s" % (PARTS[ROOT_KEY][1], PARTS[ROOT_KEY][2], REV, CODE)
    root.description = desc
    print("document %s (expected name %s): %d skeleton + %d wall parameters" % (
        app.activeDocument.name, DOC_NAME, n_skel, n_wall))
    bodies = build_panel(design, root) if PANEL_SIDE else build_cassette(design, root)
    tl = design.timeline
    bad_items = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    print("timeline %d items, unhealthy %d, sketches %d, loose %d" % (
        tl.count, len(bad_items), sum(c.sketches.count for c in design.allComponents), len(loose)))
    for name, b in sorted(bodies.items()):
        print("BODY|%s|%s|%s|%s" % (b.parentComponent.partNumber, name, size(bbox(b)), bbox(b)))
    hits, bad = clash_check(list(bodies.values()), ALLOWED_CLASH)
    print("clash pairs %d, unexpected %d %s" % (len(hits), len(bad), bad))
    for c in design.allComponents:
        if c.bRepBodies.count:
            pp = c.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
            print("MASS|%s|%s|%.3f kg|%d bodies" % (c.partNumber, c.name, pp.mass, c.bRepBodies.count))
    root.partNumber = pn            # again at the end, in case an upload overwrote them (see settle_props)
    root.description = desc
    allb = list(bodies.values())
    print("root part number %s, bodies box %s" % (root.partNumber, [
        round(min(bbox(b)[i] for b in allb), 2) for i in range(3)] + [round(max(bbox(b)[i + 3] for b in allb), 2)
                                                                    for i in range(3)]))
    if bad_items or loose or bad:
        raise RuntimeError("checks failed (unhealthy %s, loose %s, clashes %s)" % (bad_items, loose, bad))
    if ARGS.get("post") == "1":
        doc = app.activeDocument
        # the drawings' Front = the panel seen from inside the pod, saved with the build (set_front.py)
        sf = os.path.join(ARGS["repo_root"], "v2/02-Drawings/wall/set_front.py")
        sf_ns = {"__name__": "__fusion_set_front__", "__file__": sf, "SCRIPT_ARGS": {"inside": INSIDE}}
        with open(sf, "r", encoding="utf-8") as fh:
            exec(compile(fh.read(), sf, "exec"), sf_ns)
        sf_ns["run"](None)
        ver = save_holding_props(app, doc, root, pn, desc, "%s build: %s" % (REV, ARGS.get("note", "wall_side_panel.py")))
        print("saved %s (version %s), part number %s, description %r" % (doc.name, ver, root.partNumber,
                                                                         root.description[:60]))
        path = os.path.join(ARGS["repo_root"], "v2/01-CAD-Native/wall/post_wall_doc.py")
        ns = {"__name__": "__fusion_post__", "__file__": path, "SCRIPT_ARGS": dict(ARGS, pn=pn)}
        with open(path, "r", encoding="utf-8") as fh:
            exec(compile(fh.read(), path, "exec"), ns)
        ns["run"](None)
