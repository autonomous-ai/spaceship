"""Edit test for a WALL design (engineering guideline section 4.4), on a COPY.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/edit_test_wall.py \
        --arg f3d=v2/01-CAD-Native/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Opens the exported .f3d as a new, unsaved document (the saved design is never
touched) and prints a Markdown record:
  1. Reopen check: timeline health, every sketch fully constrained, design type.
  2. Edit two skeleton parameters (wall_depth 1495 -> 1300, side_h -> 1120) and,
     on designs with no fill, one wall rule (stile_pitch_max 400 -> 300), rebuild,
     check health again. A fill pocket is a cut, and a Fusion cut keeps the bodies
     it first cut: when the stud count changes, a pocket can land on a fill piece
     it doesn't know. So the stud rule isn't edited on designs with fill; a change
     in the stud count is a rebuild by the script (rebuild=1).
  3. Every body's box before and after, and the checks that the parts follow:
     lengths follow wall_depth, heights follow side_h, the stile and fill-bay
     counts follow the pitch rule, no stile pitch over the rule.
  4. Revert, rebuild, and confirm every body is back to its "before" box.
Then closes the copy without saving.
"""

import math
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
# side_h 1120, not 1000: ELECTRICAL's trunk holes in R1-CASS sit at fixed heights up to Z 1210 (el_trunk_z +
# el_kit_dz + el_kit_d / 2), and a lower row 1000 high would put its top (Z 1112) under them; ELECTRICAL moves
# the trunk before the rows change that much
# the side studs follow the bolts (stud_c1 to stud_c5, D-131 sample), not stile_pitch_max, so the rule isn't edited
EDITS = [("wall_depth", "1300 mm"), ("side_h", "1120 mm")]
# back wall panels B1-B4 (wall_back_panel.py): the panel width, the row height and the stud rule
# (pod_w 2300 with the skin and frame widths the skeleton would give it: (2300 - 92 - 3 x 2.26) / 2 and
# (2300 - 92 - 2 x 2.26 - 5.5) / 2); back_ph 1080, not 1000: ELECTRICAL's power unit cut-out in B2-CASS reaches
# Z 1134 at a fixed height, and a lower row 1000 high would end at Z 1112, under it
# (the stud count is fixed now, 3 copies held by joints, so the rule isn't edited; the pitch follows half_fw)
EDITS_BACK = [("pod_w", "2300 mm"), ("half_pw", "1100.61 mm"), ("half_fw", "1098.99 mm"), ("back_ph", "1080 mm")]
BACK_PREFIXES = ("2102", "2112", "2114", "2116", "5102", "5112", "5114")


def box(b):
    bb = b.boundingBox
    return tuple(round(v * 10.0, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                              bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z))


def snapshot(design):
    """Every body as placed, one entry per copy (D-120: a part's copies are occurrences of one component):
    {path / body name: box}."""
    root = design.rootComponent
    out = {"%s / %s" % (root.partNumber, b.name): box(b) for b in root.bRepBodies}
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out["%s / %s" % (occ.fullPathName, b.name)] = box(b)
    return out


def health(design):
    """(timeline items, the ones not healthy with Fusion's messages, loose sketches). A timeline group is only a
    container (a STEP import's group reports "unknown": the dry run's probe, 2026-11-01), so it is judged by its own
    items, as the builders judge it (wall_side_panel.py run)."""
    healthy = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    tl = design.timeline
    bad = []
    for i in range(tl.count):
        it = tl.item(i)
        if it.healthState == healthy:
            continue
        if it.isGroup:
            g = adsk.fusion.TimelineGroup.cast(it)
            bad += ["%s / %s (%s)" % (it.name, g.item(j).name, g.item(j).errorOrWarningMessage)
                    for j in range(g.count) if g.item(j).healthState != healthy]
            continue
        bad.append("%s (%s)" % (it.name, it.errorOrWarningMessage))
    loose = [sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
    return tl.count, bad, loose


def pv(design, name, default=None):
    p = design.userParameters.itemByName(name)
    if p is None:                       # a design built before the parameter existed
        return default
    return round(p.value * 10.0, 3) if p.unit == "mm" else round(p.value, 3)


def round_holes(design, prefix):
    """(diameter, axis, centre, span) of the round holes in the bodies whose names start with `prefix`; the
    centre holds the two coordinates across the axis (the one along it is None), the span is the face's extent
    along the axis (low, high)."""
    out = []
    for c in design.allComponents:
        for b in c.bRepBodies:
            if not b.name.startswith(prefix):
                continue
            for f in b.faces:
                if f.geometry.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
                    continue
                g = adsk.core.Cylinder.cast(f.geometry)
                ax = max(range(3), key=lambda i: abs((g.axis.x, g.axis.y, g.axis.z)[i]))
                ctr = [round(v * 10.0, 2) for v in (g.origin.x, g.origin.y, g.origin.z)]
                ctr[ax] = None
                fb = box(f)
                out.append((round(g.radius * 20.0, 2), "xyz"[ax], tuple(ctr), (fb[ax], fb[ax + 3])))
    return out


def has_hole(holes, d, axis, within=None, **at):
    """A hole of diameter d along `axis` whose centre matches every coordinate in `at` (mm) within 0.02 and,
    with `within` (low, high), whose span along the axis lies inside it (0.02 slack)."""
    k = {"x": 0, "y": 1, "z": 2}
    return any(abs(hd - d) < 0.02 and ha == axis and all(c[k[a]] is not None and abs(c[k[a]] - v) < 0.02
                                                           for a, v in at.items()) and
               (within is None or (sp[0] > within[0] - 0.02 and sp[1] < within[1] + 0.02))
               for hd, ha, c, sp in holes)


EL_SIDE = {"510102": ("el_y_kit", "el_y_fx", "el_z_fx", "el_fx_d", "el_trunk_z", "el_kit_dz", "el_kit_d"),
           "510104": ("el_call_y", "el_call_z", "el_shelf_z", "el_grm_s", "el_y_kit")}


def el_side_checks(design, root_pn, before_p, after_p):
    """ELECTRICAL's felt holes in R1-CASS and R2-CASS follow the skeleton (the column's back face moves with
    wall_depth, so the kit, column and call light holes move half or all of the change; heights stay)."""
    if root_pn not in EL_SIDE:
        return []
    holes = round_holes(design, "FELT")
    a = after_p
    dwd = before_p["wall_depth"] - a["wall_depth"]
    out = [("el_y_kit moves half the wall_depth change (%+.2f)" % (dwd / 2.0),
            abs((a["el_y_kit"] - before_p["el_y_kit"]) - dwd / 2.0) < 0.01)]
    if root_pn == "510102":
        out += [("FA-KIT %g hole at Y el_y_kit, Z trunk + %g" % (a["el_kit_d"], a["el_kit_dz"]),
                 has_hole(holes, a["el_kit_d"], "x", y=a["el_y_kit"], z=a["el_trunk_z"] + a["el_kit_dz"])),
                ("FX-COL %g hole follows the column's back face (Y %.2f, Z %g)" % (a["el_fx_d"], a["el_y_fx"],
                                                                                 a["el_z_fx"]),
                 has_hole(holes, a["el_fx_d"], "x", y=a["el_y_fx"], z=a["el_z_fx"]) and
                 abs((a["el_y_fx"] - before_p["el_y_fx"]) - dwd) < 0.01)]
    else:
        out += [("FX-CALL0 and FX-CALL2 %g holes follow the call light line (Y %.2f)" % (a["el_grm_s"], a["el_call_y"]),
                 has_hole(holes, a["el_grm_s"], "x", y=a["el_call_y"], z=a["el_shelf_z"]) and
                 has_hole(holes, a["el_grm_s"], "x", y=a["el_call_y"], z=a["el_call_z"]))]
    return out


EL_BACK = {"510202": ("panel_z0", "tray_t", "el_lt_x", "el_y_bg", "el_grm_d", "el_cut_x0", "el_cut_x1", "el_cut_z0",
                      "el_cut_z1"),
           "510204": ("panel_z0", "seam_gap", "tray_t", "el_lt_x", "el_y_bg", "el_grm_d", "el_shelf_z", "el_shelf_d",
                      "el_ceil_x", "el_ceil_z", "el_grm_s"),
           "210202": ("close_gap", "tube_w", "el_inlet_x", "el_inlet_z", "el_lan_z", "el_inlet_d", "el_cut_z0",
                      "el_cut_z1")}


def inside_of(design, prefix, x, y, z):
    """Is the point (mm) inside a body whose name starts with `prefix`?"""
    pt = adsk.core.Point3D.create(x / 10.0, y / 10.0, z / 10.0)
    inside = adsk.fusion.PointContainment.PointInsidePointContainment
    return any(b.pointContainment(pt) == inside for c in design.allComponents for b in c.bRepBodies
               if b.name.startswith(prefix))


def el_back_checks(design, root_pn, before_p, after_p):
    """ELECTRICAL's features in B2-CASS, B4-CASS and panel B2 after the edit: the joint's bushing holes follow
    the row seam (back_ph), the ceiling route's hole follows the pod width, the unit's openings stay where
    ELECTRICAL puts them and the fill cut-out runs to the first stud."""
    if root_pn not in EL_BACK:
        return []
    a = after_p
    out = []
    if root_pn == "510202":
        holes = round_holes(design, "TRAY")
        top = a["panel_z0"] + a["back_ph"]
        ym, zm = a["el_y_bg"], (a["el_cut_z0"] + a["el_cut_z1"]) / 2.0
        yb, yf = 850.0 - 84.0 + 34.0 - a["tray_t"] / 2, 850.0 - 84.0 + a["tray_t"] + 4.5     # base and felt mid-planes
        x0, x1 = a["el_cut_x0"], a["el_cut_x1"]
        out += [("G-B2-B4 %g hole in the top return follows the row top (Z %.2f)" % (a["el_grm_d"], top),
                 has_hole(holes, a["el_grm_d"], "z", (top - a["tray_t"], top), x=a["el_lt_x"], y=ym)),
                ("plain power unit cut-out at X %g to %g through the tray base and the felt" % (x0, x1),
                 not any(inside_of(design, pre, x, y, zm) for pre, y in (("TRAY", yb), ("FELT", yf))
                         for x in (x0 + 0.5, x1 - 0.5)) and
                 all(inside_of(design, pre, x, y, zm) for pre, y in (("TRAY", yb), ("FELT", yf))
                     for x in (x0 - 1.0, x1 + 1.0)))]
    elif root_pn == "510204":
        bot = a["panel_z0"] + a["back_ph"] + a["seam_gap"]
        tray, felt = round_holes(design, "TRAY"), round_holes(design, "FELT")
        out += [("G-B2-B4 %g hole in the bottom return follows the row seam (Z %.2f)" % (a["el_grm_d"], bot),
                 has_hole(tray, a["el_grm_d"], "z", (bot, bot + a["tray_t"]), x=a["el_lt_x"], y=a["el_y_bg"])),
                # the top lip's band, its 12 turned down from the cassette's top; ELECTRICAL's Ø6.4 tie holes go
                # through the tray's back further down (the Lead's relay of 2026-11-01), so only this band counts
                ("no cable hole through the top lip", not [
                    h for h in tray if h[1] == "y" and h[0] > 3.0 and h[2][2] is not None
                    and h[2][2] > a["pod_h"] - a["outer_t"] - a["lin_gap"] - a["lip_w"] - a["tray_t"] - 1e-6]),
                ("FX-CEIL %g felt hole follows the pod width (X (pod_w - 2 stack_t) / 4 = %.2f), 2 under the lip" % (
                    a["el_grm_s"], a["el_ceil_x"]),
                 has_hole(felt, a["el_grm_s"], "y", x=a["el_ceil_x"], z=a["el_ceil_z"]) and
                 abs((a["el_ceil_x"] - before_p["el_ceil_x"]) - (a["pod_w"] - before_p["pod_w"]) / 4.0) < 0.01),
                ("FX-SHELF %g felt hole at X %g, Z %g" % (a["el_shelf_d"], a["el_lt_x"], a["el_shelf_z"]),
                 has_hole(felt, a["el_shelf_d"], "y", x=a["el_lt_x"], z=a["el_shelf_z"]))]
    else:
        skin = round_holes(design, "SKIN")
        stud = a["close_gap"] / 2.0 + a["stile_pitch"]
        out += [("inlet and LAN %g holes in the skin at X %g" % (a["el_inlet_d"], a["el_inlet_x"]),
                 has_hole(skin, a["el_inlet_d"], "y", x=a["el_inlet_x"], z=a["el_inlet_z"]) and
                 has_hole(skin, a["el_inlet_d"], "y", x=a["el_inlet_x"], z=a["el_lan_z"])),
                ("the unit's fill cut-out runs to the first stud (X %.2f), fill below it" % stud,
                 not inside_of(design, "FILL", stud - 0.3, 824.0, (a["el_cut_z0"] + a["el_cut_z1"]) / 2.0) and
                 inside_of(design, "FILL", stud - 0.3, 824.0, a["el_cut_z0"] - 20.0))]
    return out


def cut_back(w_member, w_other, plate_t=2.0):
    """How far a mitred member's end stands back from the frame's outer corner for the 2 mm plate (Joints, D-131):
    (plate_t / 2) x the mitre's length in the frame plane / the member's own width."""
    return plate_t / 2.0 * math.hypot(w_member, w_other) / w_member


def back_checks(after, p):
    """What must follow on a back wall panel or its cassette (wall_back_panel.py) after EDITS_BACK."""
    def nm(k):
        return k.split(" / ", 1)[-1]
    seam, gap = 2.26, 5.5
    pick = (lambda pre: sorted((v for k, v in after.items() if nm(k).startswith(pre)), key=lambda b: b[0]))
    rails, stiles, mids = pick("RAIL"), pick("STILE"), pick("STILE - MID")
    perim = pick("STILE - OUTER") + pick("STILE - CENTRE")
    bays, skins, trays, felts = pick("FILL"), pick("SKIN"), pick("TRAY"), pick("FELT")
    zones = sorted((v for k, v in after.items() if "CLIP ZONE" in nm(k)), key=lambda b: b[0])
    if any(nm(k) == "RIVNUT" for k in after):       # D-120: copies of one RIVNUT body; the top rail's, less the spigots'
        top = max(r[5] for r in rails) if rails else 0.0
        spig_x = sorted((v[0] + v[3]) / 2.0 for k, v in after.items() if nm(k) == "SPIGOT")
        rivs = [v for k, v in sorted(after.items()) if nm(k) == "RIVNUT" and v[5] > top + 0.1 and v[2] < top + 0.1
                and all(abs((v[0] + v[3]) / 2.0 - x) > 0.5 for x in spig_x)]
    else:
        rivs = [r for k, r in sorted(after.items()) if nm(k).startswith("RIVNUT - TOP RAIL ") and "SPIGOT" not in nm(k)]
    rule = p["stile_pitch_max"]
    n_mid = int(round(p["stile_n_mid"]))                   # fixed (D-135); the pitch follows the width
    out = []
    if rails:
        cb = cut_back(20.0, 20.0)
        out += [("frame width follows half_fw (%g), the rails 2 plate cut-backs shorter" % p["frm_len"],
                 abs(p["frm_len"] - p["half_fw"]) < 0.01 and all(abs((r[3] - r[0]) - (p["frm_len"] - 2 * cb)) < 0.01
                                                                  for r in rails)),
                ("frame stays close_gap / 2 from X 0 at the closing seam (the rail one cut-back further)",
                 all(abs(min(abs(r[0]), abs(r[3])) - (gap / 2 + cb)) < 0.01 for r in rails)),
                ("frame's outer end stays one seam gap off the side frame (pod_w / 2 - 46 - 2.26)",
                 all(abs(max(abs(r[0]), abs(r[3])) - (p["pod_w"] / 2 - 46 - seam - cb)) < 0.01 for r in rails)),
] + ([("perimeter stiles span the row height less 2 plate cut-backs of 1.41 (D-117, D-131)",
                  all(abs((st[5] - st[2]) - (p["pnl_h"] - 2 * cut_back(20.0, 20.0))) < 0.01 for st in perim)
                  and len(perim) == 2),
                 ("studs span the row height - 40", all(abs((st[5] - st[2]) - (p["pnl_h"] - 40)) < 0.01 for st in mids))]
                if perim else
                [("stiles span the row height - 40", all(abs((st[5] - st[2]) - (p["pnl_h"] - 40)) < 0.01
                                                         for st in stiles))]) + [
                ("%d studs, evenly spaced (D-135)" % n_mid, len(mids) == n_mid and all(
                    abs((b[0] - a[0]) - p["stile_pitch"]) < 0.01 for a, b in zip(mids, mids[1:]))),
                ("no stud pitch over %g" % rule, all(b[0] - a[0] <= rule + 0.01 for a, b in zip(mids, mids[1:])))]
    if bays:
        out.append(("fill bays = stud count + 1 (%d)" % (n_mid + 1), len(bays) == n_mid + 1))
    if skins:
        sk = skins[0]
        out.append(("skin is half_pw wide and the row high", abs((sk[3] - sk[0]) - p["half_pw"]) < 0.01 and
                    abs((sk[5] - sk[2]) - p["pnl_h"]) < 0.01))
    if trays:
        tr = trays[0]
        out += [("tray runs cass_len", abs((tr[3] - tr[0]) - p["cass_len"]) < 0.01),
                ("tray height follows cass_h", abs((tr[5] - tr[2]) - p["cass_h"]) < 0.01),
                ("tray stops seam_gap / 2 short of X 0", abs(min(abs(tr[0]), abs(tr[3])) - seam / 2) < 0.01)]
    if felts:
        fe = felts[0]
        out.append(("felt follows the tray, 1 mm clear inside the 0.5 returns",
                    abs((fe[3] - fe[0]) - (p["cass_len"] - 3)) < 0.01 and abs((fe[5] - fe[2]) - (p["cass_h"] - 3)) < 0.01))
    # the frame's low-X end: its perimeter members' outer face there (the outer or centre stile). Not the rails' own
    # ends: D-131 cuts each rail back 1.41 from the corner for the mitre plate (dry run 8: the 220 rule read off the
    # rail's end was 1.41 out), and the 220 rule, the studs and the clip zones are all set from the frame's end
    x_low = min(v[0] for v in rails + perim) if rails else None
    if zones and rails:
        want = sorted({round(x_low + p["stile_pitch"], 2), round(x_low + p["stile_n_mid"] * p["stile_pitch"], 2)})
        out.append(("clip zones sit on the first and last stud", sorted({round(z[0], 2) for z in zones}) == want))
    if rivs and rails:
        pitch = (p["frm_len"] - 440.0) / 3.0
        want = [round(x_low + 220.0 + i * pitch, 2) for i in range(4)]
        got = sorted(round((r[0] + r[3]) / 2.0, 2) for r in rivs)
        out.append(("top rail rivnuts follow the 220 rule %s" % want,
                    len(got) == 4 and all(abs(a - b) < 0.02 for a, b in zip(got, want))))
    return out


def run(_context):
    app = adsk.core.Application.get()
    rel = ARGS["f3d"]
    src = app.activeDocument
    doc = app.importManager.importToNewDocument(
        app.importManager.createFusionArchiveImportOptions("%s/%s" % (ARGS["repo_root"], rel)))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    try:
        record(design, rel)
    finally:
        doc.close(False)
        if src and src.isValid:
            src.activate()


def record(design, rel):
    out = []
    p = out.append
    # the family comes from the file name (<pn>_P01_..._CAD.f3d): the copy's root part number isn't reliable
    # on a document made in the same run (B1 cassette and frame, 2026-10-31 18:25)
    root_pn = os.path.basename(rel).split("_")[0] or design.rootComponent.partNumber
    p("## Edit test: %s" % rel.split("/")[-1])
    p("")
    p("Copy opened as a new, unsaved document and closed without saving. Components: %s." % ", ".join(
        sorted(c.partNumber for c in design.allComponents if c != design.rootComponent)))
    p("")
    n, bad, loose = health(design)
    sketches = sum(c.sketches.count for c in design.allComponents)
    p("1. Reopen: timeline %d items, %d not healthy; sketches %d, %d fully constrained; %s." % (
        n, len(bad), sketches, sketches - len(loose),
        "parametric" if design.designType == adsk.fusion.DesignTypes.ParametricDesignType else "DIRECT"))
    back_wall = root_pn[:4] in BACK_PREFIXES
    edits = EDITS_BACK if back_wall else EDITS
    names = ("pod_w", "half_pw", "half_fw", "back_ph", "stile_pitch_max", "frm_len", "stile_n_mid", "stile_pitch",
             "cass_len", "cass_h", "pnl_h", "pod_h", "outer_t", "lin_gap", "lip_w") + EL_BACK.get(root_pn, ()) \
        if back_wall else ("wall_depth", "side_h", "stile_pitch_max", "frm_len", "stile_n_mid",
                                         # R1 has 7 studs (INTERIOR's two, the Lead's ruling of 2026-11-01)
                                         "stud_c1", "stud_c2", "stud_c3", "stud_c4", "stud_c5", "stud_c6", "stud_c7",
                                         "cass_len", "cass_h",
                                         "lin_front_dy",
                                         "top_h", "pod_h", "panel_z0",
                                         "seam_gap", "outer_t", "lin_gap") + EL_SIDE.get(root_pn, ())
    # R1's two added studs only where the design has them, so the other records stay as they were
    names = tuple(k for k in names if k not in ("stud_c6", "stud_c7") or design.userParameters.itemByName(k))
    before_p = {k: pv(design, k, 20.0 if k == "top_h" else 0.0) for k in names}
    before = snapshot(design)
    if any(k.split(" / ", 1)[-1].startswith("FILL") for k in before):
        edits = [e for e in edits if e[0] != "stile_pitch_max"]      # see step 2 in the docstring
    missing = [k for k, _e in edits if design.userParameters.itemByName(k) is None]
    if missing:
        raise RuntimeError("edit test: %s has no parameter %s" % (rel.split("/")[-1], ", ".join(missing)))
    exprs = {k: design.userParameters.itemByName(k).expression for k, _e in edits}
    for k, e in edits:
        design.userParameters.itemByName(k).expression = e
    adsk.doEvents()
    n2, bad2, loose2 = health(design)
    after_p = {k: pv(design, k, 20.0 if k == "top_h" else 0.0) for k in names}
    after = snapshot(design)
    p("2. Edit %s: rebuild %d items, %d not healthy, %d sketches not fully constrained." % (
        ", ".join("%s -> %s" % (k, e) for k, e in edits), n2, len(bad2), len(loose2)))
    if bad2 or loose2:
        p("")
        p("   Not healthy after the edit: %s" % "; ".join(bad2 + ["sketch %s not fully constrained" % k for k in loose2]))
    p("")
    p("| Parameter | Before | After |")
    p("|---|---|---|")
    for k in names:
        p("| %s | %g | %g |" % (k, before_p[k], after_p[k]))
    p("")
    p("3. Bodies (box in mm: xmin, ymin, zmin, xmax, ymax, zmax):")
    p("")
    p("| Body | Before | After |")
    p("|---|---|---|")
    for k in sorted(set(before) | set(after)):
        p("| %s | %s | %s |" % (k, before.get(k, "-"), after.get(k, "-")))
    p("")
    if back_wall:
        checks = back_checks(after, after_p) + el_back_checks(design, root_pn, before_p, after_p)
    else:
        checks = []
        seam = 2.26
        y0p = 850.0 - after_p["wall_depth"] + seam          # panel front end (2.26 behind the decor back plate)
        y0c = 850.0 - after_p["wall_depth"] + after_p.get("lin_front_dy", 0.0)   # the cassette's front end
        # rows as the builder makes them: the lower panel from panel_z0, side_h high; the upper one from one seam
        # gap above it up to the roof datum pod_h (its cassette floats lin_gap under the roof frame)
        upper = root_pn[4:6] in ("03", "04")
        z0 = after_p["panel_z0"] + (after_p["side_h"] + seam if upper else 0.0)
        z1 = after_p["pod_h"] if upper else after_p["panel_z0"] + after_p["side_h"]
        zc1 = after_p["pod_h"] - after_p["outer_t"] - after_p["lin_gap"] if upper else z1
        def nm(k):          # body name without its component's part number ("PN / NAME")
            return k.split(" / ", 1)[-1]
        # by name prefix: hardware names hold member names too ("RIVNUT - TOP RAIL 1", "RIVNUT - BACK STILE CORNER 1")
        rails = [v for k, v in after.items() if nm(k).startswith("RAIL")]
        stiles = [v for k, v in after.items() if nm(k).startswith("STILE")]
        mids = sorted(v for k, v in after.items() if nm(k).startswith("STILE - MID"))
        bays = [v for k, v in after.items() if nm(k).startswith("FILL")]
        skins = [v for k, v in after.items() if nm(k).startswith("SKIN")]
        trays = [v for k, v in after.items() if nm(k).startswith("TRAY")]
        felts = [v for k, v in after.items() if nm(k).startswith("FELT")]
        zones = [v for k, v in after.items() if "CLIP ZONE" in nm(k)]
        # hardware: the old bodies were named per site; the D-120 copies are one RIVNUT, STOP WASHER, SPIGOT body
        # each, placed: the top rail's are the ones above its top face (a lower panel's J-WALL-01 nut side)
        def on_top_rail(v):
            return v[5] > z1 + 0.1 and v[2] < z1 + 0.1
        if any(nm(k) == "RIVNUT" for k in after):
            spig_y = sorted((v[1] + v[4]) / 2.0 for k, v in after.items() if nm(k) == "SPIGOT")
            rivs = sorted((v for k, v in after.items() if nm(k) == "RIVNUT" and on_top_rail(v) and
                           all(abs((v[1] + v[4]) / 2.0 - y) > 0.5 for y in spig_y)), key=lambda v: v[1])
            washers = sorted((v for k, v in after.items() if nm(k) == "STOP WASHER" and on_top_rail(v)),
                             key=lambda v: v[1])
            spig_front = sorted((v for k, v in after.items() if nm(k) == "SPIGOT"), key=lambda v: v[1])[:1]
        else:
            rivs = sorted(v for k, v in after.items() if nm(k).startswith("RIVNUT - TOP RAIL ") and "SPIGOT" not in nm(k))
            washers = sorted(v for k, v in after.items() if nm(k).startswith("STOP WASHER - TOP RAIL "))
            spig_front = [v for k, v in after.items() if nm(k) == "SPIGOT - TOP RAIL SPIGOT FRONT"]
        # D-131 sample: 5 studs set from the bolts (stud_c1 to stud_c5); every bay's skin within the PM's 2 mm (a
        # clear bay of 275 or less at these heights) and every bolt 30 or more clear of every stud (R-J14)
        n_mid = int(round(after_p["stile_n_mid"]))
        pitch = (after_p["wall_depth"] - seam - 440.0) / 3.0                # len_bolt_pitch (220 rule)
        bolts = [y0p + 220.0 + i * pitch for i in range(4)]
        y_front_in = y0p + 20.0
        # the frame stops skin_t + bond_t (3 + 3) inside the panel's back end: the return's bond line (the Lead, 2026-11-01)
        y_back_in = y0p + (after_p["wall_depth"] - seam - 6) - 40.0
        mid_y = sorted(m[1] for m in mids)
        faces = [y_front_in] + [y for m in sorted(mids, key=lambda m: m[1]) for y in (m[1], m[4])] + [y_back_in]
        clear = [faces[i + 1] - faces[i] for i in range(0, len(faces), 2)]
        if rails:
            checks += [
                # D-117's mitres with D-131's 2 mm plates: each perimeter member stands back from its outer corners
                # by its cut-back (1.41 for 20 to 20 and 40 to 40; 2.24 / 1.12 where a 20 meets a 40)
                ("rails run wall_depth - 2.26 - 6 (the back return and its bond line) less their plate cut-backs", all(
                    abs((r[4] - r[1]) - (after_p["wall_depth"] - seam - 6 - cut_back(r[5] - r[2], 20.0)
                                         - cut_back(r[5] - r[2], 40.0))) < 0.01 for r in rails)),
                ("rails start one cut-back behind the frame's front end (2.26 behind the decor back plate)",
                 all(abs(r[1] - (y0p + cut_back(r[5] - r[2], 20.0))) < 0.01 for r in rails)),
                ("perimeter stiles span the panel height less their plate cut-backs",
                 all(abs((st[5] - st[2]) - (z1 - z0 - cut_back(st[4] - st[1], 20.0)
                                            - cut_back(st[4] - st[1], after_p["top_h"]))) < 0.01
                     for k, st in after.items() if nm(k) in ("STILE - FRONT", "STILE - BACK"))),
                ("studs span the panel height - 20 - top_h", all(abs((st[5] - st[2]) - (z1 - z0 - 20 - after_p["top_h"]))
                                                                 < 0.01 for st in mids)),
                ("%d studs, set from the bolts" % n_mid, len(mids) == n_mid and all(
                    abs((m[1] + m[4]) / 2.0 - (y0p + after_p["stud_c%d" % (k + 1)])) < 0.01
                    for k, m in enumerate(sorted(mids, key=lambda m: m[1])))),
                ("every clear bay 275 or less (the skin's 2 mm limit) %s" % [round(c, 1) for c in clear],
                 all(c <= 275.0 for c in clear)),
                ("every bolt 30 or more clear of every stud (R-J14)",
                 all(min(abs(b - y) for y in mid_y + [m[4] for m in mids]) >= 30.0 - 0.01 and
                     not any(m[1] - 0.01 < b < m[4] + 0.01 for m in mids) for b in bolts)),
            ]
        if bays:
            checks.append(("fill bays = stud count + 1 (%d)" % (n_mid + 1), len(bays) == n_mid + 1))
        if skins:
            sk = skins[0]
            checks.append(("skin runs wall_depth - 2.26 and the panel height", abs((sk[4] - sk[1]) - (after_p["wall_depth"] - seam))
                           < 0.01 and abs((sk[5] - sk[2]) - (z1 - z0)) < 0.01))
        if trays:
            tr = trays[0]
            checks += [("tray runs cass_len", abs((tr[4] - tr[1]) - after_p["cass_len"]) < 0.01),
                       ("tray starts lin_front_dy behind the decor back plate (R: 5, clear of DR's panel)",
                        abs(tr[1] - y0c) < 0.01),
                       ("tray height follows the row (cass_h)", abs((tr[5] - tr[2]) - (zc1 - z0)) < 0.01 and
                        abs(after_p["cass_h"] - (zc1 - z0)) < 0.01)]
        if felts:
            fe = felts[0]
            checks.append(("felt follows the tray, 1 mm clear inside the 0.5 returns",
                           abs((fe[4] - fe[1]) - (after_p["cass_len"] - 3)) < 0.01 and
                           abs((fe[5] - fe[2]) - (zc1 - z0 - 3)) < 0.01))
        if zones:
            checks += [
                ("clip zones sit on the first and last stud",
                 sorted({round(zz[1], 2) for zz in zones}) == sorted({
                     round(y0p + after_p["stud_c1"] - 10.0, 2),
                     round(y0p + after_p["stud_c%d" % int(round(after_p["stile_n_mid"]))] - 10.0, 2)})),
                ("top clip zones follow the top edge", abs(max(zz[5] for zz in zones) - (zc1 - 70)) < 0.01),
            ]
        if rivs:
            pitch = (after_p["wall_depth"] - seam - 440.0) / 3.0        # 220 rule, 4 bolts (R-J14)
            want = [round(y0p + 220.0 + i * pitch, 2) for i in range(4)]
            got = sorted(round((r[1] + r[4]) / 2.0, 2) for r in rivs)
            checks.append(("top rail rivnuts follow the 220 rule %s" % want,
                           len(got) == 4 and all(abs(a - b) < 0.02 for a, b in zip(got, want))))
        if washers and rivs:
            checks.append(("a stop washer under each top rail rivnut",
                           len(washers) == len(rivs) and all(abs((w[1] + w[4]) - (r[1] + r[4])) < 0.04
                                                             for w, r in zip(washers, rivs))))
        if spig_front:
            sp = spig_front[0]
            checks.append(("front spigot follows the panel's front end (+100)",
                           abs((sp[1] + sp[4]) / 2.0 - (y0p + 100.0)) < 0.02))
        checks += el_side_checks(design, root_pn, before_p, after_p)
    for k, e in exprs.items():
        design.userParameters.itemByName(k).expression = e
    adsk.doEvents()
    n3, bad3, loose3 = health(design)
    back = snapshot(design)
    same = all(back.get(k) == v for k, v in before.items()) and set(back) == set(before)
    checks.append(("revert: every body back to its before box, healthy", same and not bad3 and not loose3))
    p("| Check | Result |")
    p("|---|---|")
    for c, ok in checks:
        p("| %s | %s |" % (c, "PASS" if ok else "FAIL"))
    p("")
    p("4. Revert: %d items, %d not healthy, %d sketches not fully constrained; bodies back to before: %s." % (
        n3, len(bad3), len(loose3), same))
    print("\n".join(out))
    if ARGS.get("out"):                     # also write the record to a file (post_wall_doc.py)
        path = os.path.join(ARGS["repo_root"], ARGS["out"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out) + "\n")
    if not all(ok for _c, ok in checks) or bad or loose or bad2 or loose2:
        raise RuntimeError("edit test failed: %s" % [c for c, ok in checks if not ok])
