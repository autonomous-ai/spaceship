"""Edit test for a WALL design (engineering guideline section 4.4), on a COPY.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/edit_test_wall.py \
        --arg f3d=v2/01-CAD-Native/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d

Opens the exported .f3d as a new, unsaved document (the saved design is never
touched) and prints a Markdown record:
  1. Reopen check: timeline health, every sketch fully constrained, design type.
  2. Edit two skeleton parameters (wall_depth 1495 -> 1300, side_h -> 1000) and
     one wall rule (stile_pitch_max 400 -> 300), rebuild, check health again.
  3. Every body's box before and after, and the checks that the parts follow:
     lengths follow wall_depth, heights follow side_h, the stile and fill-bay
     counts follow the pitch rule, no stile pitch over the rule.
  4. Revert, rebuild, and confirm every body is back to its "before" box.
Then closes the copy without saving.
"""

import math

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
EDITS = [("wall_depth", "1300 mm"), ("side_h", "1000 mm"), ("stile_pitch_max", "300 mm")]


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


def pv(design, name):
    p = design.userParameters.itemByName(name)
    return round(p.value * 10.0, 3) if p.unit == "mm" else round(p.value, 3)


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
    root_pn = design.rootComponent.partNumber
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
    names = ("wall_depth", "side_h", "stile_pitch_max", "frm_len", "stile_n_mid", "stile_pitch", "cass_len",
             "cass_h")
    before_p = {k: pv(design, k) for k in names}
    before = snapshot(design)
    exprs = {k: design.userParameters.itemByName(k).expression for k, _e in EDITS}
    for k, e in EDITS:
        design.userParameters.itemByName(k).expression = e
    adsk.doEvents()
    n2, bad2, loose2 = health(design)
    after_p = {k: pv(design, k) for k in names}
    after = snapshot(design)
    p("2. Edit %s: rebuild %d items, %d not healthy, %d sketches not fully constrained." % (
        ", ".join("%s -> %s" % (k, e) for k, e in EDITS), n2, len(bad2), len(loose2)))
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
    checks = []
    y0 = 850.0 - after_p["wall_depth"]
    z0 = 110.0
    if any("RAIL" in k for k in after):      # a panel (an imported copy gets a new root part number)
        rails = [v for k, v in after.items() if "RAIL" in k]
        stiles = [v for k, v in after.items() if "STILE" in k]
        mids = sorted(v for k, v in after.items() if "STILE - MID" in k)
        bays = [v for k, v in after.items() if "FILL" in k]
        skin = [v for k, v in after.items() if "SKIN" in k][0]
        n_mid = math.ceil((after_p["wall_depth"] - 3 - 10 - 20) / 300.0) - 1
        checks += [
            ("rails run wall_depth - 3", all(abs((r[4] - r[1]) - (after_p["wall_depth"] - 3)) < 0.01 for r in rails)),
            ("frame starts at the decor back plate (Y = 850 - wall_depth)", all(abs(r[1] - y0) < 0.01 for r in rails)),
            ("stiles span side_h - 40", all(abs((s[5] - s[2]) - (after_p["side_h"] - 40)) < 0.01 for s in stiles)),
            ("mid stile count follows the 300 mm rule (%d)" % n_mid, len(mids) == n_mid),
            ("fill bays = mid stiles + 1", len(bays) == len(mids) + 1),
            ("no stile pitch over 300", all(b[1] - a[1] <= 300.01 for a, b in zip(mids, mids[1:]))),
            ("skin runs wall_depth and side_h - reveal", abs((skin[4] - skin[1]) - after_p["wall_depth"]) < 0.01 and
             abs((skin[5] - skin[2]) - (after_p["side_h"] - 4)) < 0.01),
        ]
    else:
        tray = [v for k, v in after.items() if "TRAY" in k][0]
        felt = [v for k, v in after.items() if "FELT" in k][0]
        zones = [v for k, v in after.items() if "CLIP ZONE" in k]
        checks += [
            ("tray runs cass_len", abs((tray[4] - tray[1]) - after_p["cass_len"]) < 0.01),
            ("tray starts at the decor back plate", abs(tray[1] - y0) < 0.01),
            ("tray and felt height follow side_h", abs((tray[5] - tray[2]) - after_p["side_h"]) < 0.01 and
             abs((felt[5] - felt[2]) - after_p["side_h"]) < 0.01),
            ("clip zones sit on the first and last mid stile",
             sorted({round(zz[1], 2) for zz in zones}) == sorted({round(y0 + after_p["stile_pitch"], 2),
                                                                  round(y0 + after_p["stile_n_mid"] *
                                                                        after_p["stile_pitch"], 2)})),
            ("top clip zones follow the top edge", max(zz[5] for zz in zones) == round(
                z0 + after_p["side_h"] - 100 + 30, 2)),
        ]
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
    if not all(ok for _c, ok in checks) or bad or loose or bad2 or loose2:
        raise RuntimeError("edit test failed: %s" % [c for c, ok in checks if not ok])
