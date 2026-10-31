"""Edit test for the proof part (engineering guideline section 4.4).

Works on a COPY: it opens the exported .f3d archive as a new document, so the
saved design is never touched. Run it with:

    python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/edit_test.py

What it does, and prints as a Markdown record:
  1. Reopen check: the .f3d opens with a healthy timeline, every sketch fully
     constrained, named features and named user parameters with units.
  2. Before: bounding box, volume and hole centres of every body.
  3. Edit: frame_width 1470 -> 1170 mm and rail_hole_pitch_max 500 -> 300 mm,
     rebuild, check the timeline again, measure again.
  4. Which bodies changed. Expected: front stile moves, the three rails get
     shorter, the two drilled rails get 5 holes at the new pitch, the skin
     gets narrower; the rear stile does not change.
  5. Revert both parameters, rebuild, and confirm every body is back to the
     "before" values. Then close the copy without saving.
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
F3D_REL = "v2/01-CAD-Native/proof/V2-SWL-00_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD.f3d"
EDITS = [("frame_width", "1170 mm"), ("rail_hole_pitch_max", "300 mm")]
HOLE_DIA_MM = 6.6
EXPECT_CHANGED = {"WALL - FRAME STILE - FRONT - TUBE", "WALL - FRAME RAIL - BOTTOM - TUBE",
                  "WALL - FRAME RAIL - TOP - TUBE", "WALL - FRAME RAIL - MID - TUBE",
                  "WALL - SKIN ACP 3 - SIDE LOWER - LH - SHEET"}
EXPECT_SAME = {"WALL - FRAME STILE - REAR - TUBE"}


def mm(v):
    return round(v * 10.0, 3)


def box(b):
    bb = b.boundingBox
    return (mm(bb.minPoint.x), mm(bb.minPoint.y), mm(bb.minPoint.z),
            mm(bb.maxPoint.x), mm(bb.maxPoint.y), mm(bb.maxPoint.z))


def holes(b):
    pts = set()
    for f in b.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and \
                abs(g.radius * 20.0 - HOLE_DIA_MM) < 0.01:
            ax = (abs(round(g.axis.x)), abs(round(g.axis.y)), abs(round(g.axis.z)))
            o = (mm(g.origin.x), mm(g.origin.y), mm(g.origin.z))
            # keep the two coordinates across the hole axis
            key = tuple(round(o[i], 2) for i in range(3) if not ax[i])
            pts.add(key)
    return sorted(pts)


def snapshot(design):
    snap = {}
    for comp in design.allComponents:
        for b in comp.bRepBodies:
            snap[b.name] = {"box": box(b), "vol_mm3": round(b.volume * 1000.0, 1), "holes": holes(b)}
    return snap


def health(design):
    tl = design.timeline
    bad = []
    for i in range(tl.count):
        it = tl.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            bad.append("%s (%s)" % (it.name, it.errorOrWarningMessage))
    loose = [sk.name for c in design.allComponents for sk in c.sketches if not sk.isFullyConstrained]
    return tl.count, bad, loose


def pv(design, name):
    p = design.userParameters.itemByName(name)
    return round(p.value * 10.0, 3) if p.unit == "mm" else round(p.value, 3)


def fmt_box(b):
    return "X %g..%g, Y %g..%g, Z %g..%g" % (b[0], b[3], b[1], b[4], b[2], b[5])


def run(_context):
    app = adsk.core.Application.get()
    path = "%s/%s" % (ARGS["repo_root"], F3D_REL)
    src = app.activeDocument
    doc = app.importManager.importToNewDocument(
        app.importManager.createFusionArchiveImportOptions(path))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    try:
        record(design)
    finally:
        doc.close(False)
        if src and src.isValid:
            src.activate()


def record(design):
    out = []
    p = out.append
    p("## Edit test record")
    p("")
    p("Copy: `%s` opened as a new, unsaved document (closed without saving at the end)." % F3D_REL)
    p("")
    n, bad, loose = health(design)
    sketches = sum(c.sketches.count for c in design.allComponents)
    p("### 1. Reopen check")
    p("")
    p("- Timeline: %d items, %d not healthy%s" % (n, len(bad), (": " + "; ".join(bad)) if bad else ""))
    p("- Sketches: %d, fully constrained: %d%s" % (sketches, sketches - len(loose),
                                                  (" (NOT: %s)" % ", ".join(loose)) if loose else ""))
    p("- Design type: %s" % ("parametric (history captured)"
                             if design.designType == adsk.fusion.DesignTypes.ParametricDesignType
                             else "DIRECT (no history)"))
    p("- User parameters (%d):" % design.userParameters.count)
    p("")
    p("| Name | Expression | Unit |")
    p("|---|---|---|")
    for up in design.userParameters:
        p("| %s | `%s` | %s |" % (up.name, up.expression, up.unit or "(count)"))
    p("")
    reopen_ok = not bad and not loose
    before = snapshot(design)
    p_before = {k: pv(design, k) for k in ("frame_width", "rail_hole_pitch_max", "rail_hole_count",
                                          "rail_hole_pitch", "skin_width")}

    for name, expr in EDITS:
        design.userParameters.itemByName(name).expression = expr
    adsk.doEvents()
    n2, bad2, loose2 = health(design)
    after = snapshot(design)
    p_after = {k: pv(design, k) for k in p_before}

    p("### 2. Edit")
    p("")
    p("| Parameter | Before | After |")
    p("|---|---|---|")
    for k in p_before:
        p("| %s | %g | %g |" % (k, p_before[k], p_after[k]))
    p("")
    p("Rebuild: %d timeline items, %d not healthy%s; sketches not fully constrained: %d" % (
        n2, len(bad2), (": " + "; ".join(bad2)) if bad2 else "", len(loose2)))
    p("")
    p("### 3. Bodies before and after")
    p("")
    p("| Body | Changed | Bounding box before (mm) | Bounding box after (mm) | Volume mm3 before -> after | Holes before -> after |")
    p("|---|---|---|---|---|---|")
    changed = set()
    for name in sorted(before):
        b, a = before[name], after.get(name)
        ch = a is None or b != a
        if ch:
            changed.add(name)
        p("| %s | %s | %s | %s | %g -> %g | %d -> %d |" % (
            name, "yes" if ch else "no", fmt_box(b["box"]), fmt_box(a["box"]) if a else "-",
            b["vol_mm3"], a["vol_mm3"] if a else 0, len(b["holes"]), len(a["holes"]) if a else 0))
    p("")
    for name in sorted(before):
        if after[name]["holes"] != before[name]["holes"] and after[name]["holes"]:
            p("- %s hole centres after: %s" % (name, after[name]["holes"]))
    p("")
    right = changed == EXPECT_CHANGED and not (changed & EXPECT_SAME)
    p("Expected to change: %s. Expected unchanged: %s. Result: %s." % (
        ", ".join(sorted(EXPECT_CHANGED)), ", ".join(sorted(EXPECT_SAME)),
        "the right bodies changed" if right else "UNEXPECTED: changed = %s" % sorted(changed)))
    p("")

    for name, _expr in EDITS:
        orig = {"frame_width": "1470 mm", "rail_hole_pitch_max": "500 mm"}[name]
        design.userParameters.itemByName(name).expression = orig
    adsk.doEvents()
    n3, bad3, loose3 = health(design)
    back = snapshot(design)
    same = back == before
    p("### 4. Revert")
    p("")
    p("frame_width back to 1470 mm, rail_hole_pitch_max back to 500 mm. Timeline: %d not healthy; "
      "sketches not fully constrained: %d. Every body equal to the before values: %s." % (
          len(bad3), len(loose3), "yes" if same else "NO"))
    p("")
    ok = reopen_ok and not bad2 and not loose2 and right and same and not bad3 and not loose3
    p("**RESULT: %s**" % ("PASS (CAD check on a copy; not a physical test)" if ok else "FAIL"))
    print("\n".join(out))
    if not ok:
        raise RuntimeError("edit test failed")
