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
EDITS = [("wall_depth", "1300 mm"), ("side_h", "1120 mm"), ("stile_pitch_max", "300 mm")]
# back wall panels B1-B4 (wall_back_panel.py): the panel width, the row height and the stud rule
# (pod_w 2300 with the skin and frame widths the skeleton would give it: (2300 - 92 - 3 x 2.26) / 2 and
# (2300 - 92 - 2 x 2.26 - 5.5) / 2); back_ph 1080, not 1000: ELECTRICAL's power unit cut-out in B2-CASS reaches
# Z 1134 at a fixed height, and a lower row 1000 high would end at Z 1112, under it
EDITS_BACK = [("pod_w", "2300 mm"), ("half_pw", "1100.61 mm"), ("half_fw", "1098.99 mm"), ("back_ph", "1080 mm"),
              ("stile_pitch_max", "300 mm")]
BACK_PREFIXES = ("2102", "2112", "2114", "2116", "5102", "5112", "5114")


def box(b):
    bb = b.boundingBox
    return tuple(round(v * 10.0, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                              bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z))


def snapshot(design):
    return {"%s / %s" % (c.partNumber, b.name): box(b) for c in design.allComponents for b in c.bRepBodies}


def health(design):
    tl = design.timeline
    bad = ["%s (%s)" % (tl.item(i).name, tl.item(i).errorOrWarningMessage) for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
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


EL_SIDE = {"510102": ("el_y_kit", "el_y_cx", "el_trunk_z", "el_kit_dz", "el_kit_d", "el_grm_d"),
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
                ("FX-COL %g hole follows the column's back face (Y %.2f)" % (a["el_grm_d"], a["el_y_cx"]),
                 has_hole(holes, a["el_grm_d"], "x", y=a["el_y_cx"], z=a["el_trunk_z"]) and
                 abs((a["el_y_cx"] - before_p["el_y_cx"]) - dwd) < 0.01)]
    else:
        out += [("FX-CALL0 and FX-CALL2 %g holes follow the call light line (Y %.2f)" % (a["el_grm_s"], a["el_call_y"]),
                 has_hole(holes, a["el_grm_s"], "x", y=a["el_call_y"], z=a["el_shelf_z"]) and
                 has_hole(holes, a["el_grm_s"], "x", y=a["el_call_y"], z=a["el_call_z"]))]
    return out


EL_BACK = {"510202": ("panel_z0", "tray_t", "el_lt_x", "el_y_bg", "el_grm_d", "el_cut_x0", "el_cut_x1", "el_cut_z0",
                      "el_cut_z1"),
           "510204": ("panel_z0", "seam_gap", "tray_t", "el_lt_x", "el_y_bg", "el_grm_d", "el_shelf_z", "el_shelf_d"),
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
        out += [("G-B2-B4 %g hole in the top return follows the row top (Z %.2f)" % (a["el_grm_d"], top),
                 has_hole(holes, a["el_grm_d"], "z", (top - a["tray_t"], top), x=a["el_lt_x"], y=ym)),
                ("G-PU-TOP %g hole in the cut-out's top return (Z %.2f)" % (a["el_grm_d"], a["el_cut_z1"]),
                 has_hole(holes, a["el_grm_d"], "z", (a["el_cut_z1"], a["el_cut_z1"] + a["tray_t"]),
                          x=a["el_lt_x"], y=ym)),
                ("power unit cut-out open at X %g to %g, its returns outside it" % (a["el_cut_x0"], a["el_cut_x1"]),
                 not inside_of(design, "TRAY", a["el_cut_x0"] + 0.2, ym, zm) and
                 not inside_of(design, "TRAY", a["el_cut_x1"] - 0.2, ym, zm) and
                 inside_of(design, "TRAY", a["el_cut_x0"] - a["tray_t"] / 2, ym, zm) and
                 inside_of(design, "TRAY", a["el_cut_x1"] + a["tray_t"] / 2, ym, zm))]
    elif root_pn == "510204":
        bot = a["panel_z0"] + a["back_ph"] + a["seam_gap"]
        tray, felt = round_holes(design, "TRAY"), round_holes(design, "FELT")
        out += [("G-B2-B4 %g hole in the bottom return follows the row seam (Z %.2f)" % (a["el_grm_d"], bot),
                 has_hole(tray, a["el_grm_d"], "z", (bot, bot + a["tray_t"]), x=a["el_lt_x"], y=a["el_y_bg"])),
                ("no cable hole through the top lip (FX-CEIL waits for its felt-only height)",
                 not [h for h in tray if h[1] == "y" and h[0] > 3.0]),
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


def back_checks(after, p):
    """What must follow on a back wall panel or its cassette (wall_back_panel.py) after EDITS_BACK."""
    def nm(k):
        return k.split(" / ", 1)[-1]
    seam, gap = 2.26, 5.5
    pick = (lambda pre: sorted((v for k, v in after.items() if nm(k).startswith(pre)), key=lambda b: b[0]))
    rails, stiles, mids = pick("RAIL"), pick("STILE"), pick("STILE - MID")
    bays, skins, trays, felts = pick("FILL"), pick("SKIN"), pick("TRAY"), pick("FELT")
    zones = sorted((v for k, v in after.items() if "CLIP ZONE" in nm(k)), key=lambda b: b[0])
    rivs = [r for k, r in sorted(after.items()) if nm(k).startswith("RIVNUT - TOP RAIL ") and "SPIGOT" not in nm(k)]
    rule = p["stile_pitch_max"]
    n_mid = math.ceil((p["frm_len"] - 20) / rule) - 1
    out = []
    if rails:
        out += [("frame width follows half_fw (%g)" % p["frm_len"],
                 abs(p["frm_len"] - p["half_fw"]) < 0.01 and all(abs((r[3] - r[0]) - p["frm_len"]) < 0.01 for r in rails)),
                ("frame stays close_gap / 2 from X 0 at the closing seam",
                 all(abs(min(abs(r[0]), abs(r[3])) - gap / 2) < 0.01 for r in rails)),
                ("frame's outer end stays one seam gap off the side frame (pod_w / 2 - 46 - 2.26)",
                 all(abs(max(abs(r[0]), abs(r[3])) - (p["pod_w"] / 2 - 46 - seam)) < 0.01 for r in rails)),
                ("stiles span the row height - 40", all(abs((st[5] - st[2]) - (p["pnl_h"] - 40)) < 0.01
                                                         for st in stiles)),
                ("stud count follows the %g mm rule (%d)" % (rule, n_mid), len(mids) == n_mid),
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
    if zones and rails:
        x_low = min(r[0] for r in rails)
        want = sorted({round(x_low + p["stile_pitch"], 2), round(x_low + p["stile_n_mid"] * p["stile_pitch"], 2)})
        out.append(("clip zones sit on the first and last stud", sorted({round(z[0], 2) for z in zones}) == want))
    if rivs and rails:
        x_low = min(r[0] for r in rails)
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
             "cass_len", "cass_h", "pnl_h") + EL_BACK.get(root_pn, ()) if back_wall else ("wall_depth", "side_h", "stile_pitch_max", "frm_len", "stile_n_mid",
                                         "stile_pitch", "cass_len", "cass_h", "top_h", "pod_h", "panel_z0",
                                         "seam_gap", "outer_t", "lin_gap") + EL_SIDE.get(root_pn, ())
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
        y0c = 850.0 - after_p["wall_depth"]                 # the lining starts at the decor back plate
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
        rivs = sorted(v for k, v in after.items() if nm(k).startswith("RIVNUT - TOP RAIL ") and "SPIGOT" not in nm(k))
        washers = sorted(v for k, v in after.items() if nm(k).startswith("STOP WASHER - TOP RAIL "))
        spig_front = [v for k, v in after.items() if nm(k) == "SPIGOT - TOP RAIL SPIGOT FRONT"]
        rule = after_p["stile_pitch_max"]
        n_mid = math.ceil((after_p["wall_depth"] - seam - 3 - 10 - 20) / rule) - 1
        if rails:
            checks += [
                ("rails run wall_depth - 2.26 - 3", all(abs((r[4] - r[1]) - (after_p["wall_depth"] - seam - 3)) < 0.01
                                                        for r in rails)),
                ("frame starts 2.26 behind the decor back plate", all(abs(r[1] - y0p) < 0.01 for r in rails)),
                ("stiles span the panel height - 20 - top_h", all(abs((st[5] - st[2]) - (z1 - z0 - 20 - after_p["top_h"]))
                                                                  < 0.01 for st in stiles)),
                ("mid stile count follows the %g mm rule (%d)" % (rule, n_mid), len(mids) == n_mid),
                ("no stile pitch over %g" % rule, all(b[1] - a[1] <= rule + 0.01 for a, b in zip(mids, mids[1:]))),
            ]
        if bays:
            checks.append(("fill bays = mid stile count + 1 (%d)" % (n_mid + 1), len(bays) == n_mid + 1))
        if skins:
            sk = skins[0]
            checks.append(("skin runs wall_depth - 2.26 and the panel height", abs((sk[4] - sk[1]) - (after_p["wall_depth"] - seam))
                           < 0.01 and abs((sk[5] - sk[2]) - (z1 - z0)) < 0.01))
        if trays:
            tr = trays[0]
            checks += [("tray runs cass_len", abs((tr[4] - tr[1]) - after_p["cass_len"]) < 0.01),
                       ("tray starts at the decor back plate", abs(tr[1] - y0c) < 0.01),
                       ("tray height follows the row (cass_h)", abs((tr[5] - tr[2]) - (zc1 - z0)) < 0.01 and
                        abs(after_p["cass_h"] - (zc1 - z0)) < 0.01)]
        if felts:
            fe = felts[0]
            checks.append(("felt follows the tray, 1 mm clear inside the 0.5 returns",
                           abs((fe[4] - fe[1]) - (after_p["cass_len"] - 3)) < 0.01 and
                           abs((fe[5] - fe[2]) - (zc1 - z0 - 3)) < 0.01))
        if zones:
            checks += [
                ("clip zones sit on the first and last mid stile",
                 sorted({round(zz[1], 2) for zz in zones}) == sorted({round(y0p + after_p["stile_pitch"], 2),
                                                                      round(y0p + after_p["stile_n_mid"] *
                                                                            after_p["stile_pitch"], 2)})),
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
