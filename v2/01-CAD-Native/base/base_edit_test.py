"""Edit test for 110000 BASE (guideline section 4.4), run on a copy.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/base/base_edit_test.py

Opens the exported native file (v2/01-CAD-Native/base/110000_P01_BASE_CAD.f3d)
as a new, unsaved copy, so the cloud file is never touched. Then, for each
edit set below: change the parameters, recompute, check that the timeline
stays healthy, and measure every part we make against its own expressions
(boxes, plus the rivnut hole centres in the side band's top wall). Last it
puts the design values back and checks that every body returns to where it
started. The copy is closed without saving.

The hardware copies (rivet nuts, pins, glides) are placed by the build script
at the hole positions; they don't move with an edit in the native file. A
rebuild places them again (see the manifest). They are not measured here.
"""

import os

import adsk.core
import adsk.fusion

HERE = os.path.dirname(os.path.abspath(globals().get("__file__", ".")))
BUILD = os.path.join(HERE, "base_build.py")
F3D = os.path.join(HERE, "110000_P01_BASE_CAD.f3d")

# edit sets: (label, {parameter: new expression})
EDITS = [
    ("pod size and wall depth (skeleton)", {"pod_w": "2700 mm", "pod_d": "1800 mm", "wall_depth": "1595 mm"}),
    ("band section and glide height (skeleton + BASE)", {"band_h": "120 mm", "glide_h": "15 mm", "band_wall": "2.5 mm"}),
    ("DL facet, joint and pin spacing (skeleton + BASE)", {"dl_x2": "110 mm", "dl_y1": "650 mm", "jb_e": "260 mm",
                                                           "sp_e": "120 mm", "jb_n": "5"}),
    ("floor and bracket (BASE)", {"fl_gap": "6 mm", "fl_t": "12 mm", "lap_w": "25 mm", "br_leg": "50 mm",
                                  "br_len": "60 mm"}),
]


def load_build():
    ns = {"__name__": "base_build", "__file__": BUILD, "SCRIPT_ARGS": {}}
    with open(BUILD, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), BUILD, "exec"), ns)
    return ns


def expected_boxes(b, design):
    v = lambda e: b["ev"](design, e)  # noqa: E731
    XL, XR, YB, YW = b["XL"], b["XR"], b["YB"], b["YW"]
    ym = min(v("-dl_y1"), v(b["Y_MITRE_IN"]))
    return {
        "band_l_tube": (v(XL), ym, v("glide_h"), v("%s + band_t" % XL), v("%s - cap_t" % YB), v("wall_z0")),
        "band_b_tube": (v("%s + band_t" % XL), v("%s - band_t" % YB), v("glide_h"), v("%s - band_t" % XR), v(YB),
                        v("wall_z0")),
        "bracket": (v("%s + band_t + rn_head_t" % XL), v("%s - band_t - rn_head_t - br_leg" % YB), v("br_z0"),
                    v("%s + band_t + rn_head_t + br_leg" % XL), v("%s - band_t - rn_head_t" % YB), v("br_z0 + br_len")),
        "floor_f1": (v("%s + band_t + fl_gap" % XL), v(YW), v("mat_t"), v("-fl_seam / 2 + lap_w"),
                     v("%s - band_t - fl_gap" % YB), v("mat_t + fl_t")),
        "mat_f1": (v("%s + band_t + fl_gap" % XL), v(YW), 0.0, v("-fl_seam / 2"), v("%s - band_t - fl_gap" % YB),
                   v("mat_t")),
    }


def expected_side_holes(b, design):
    v = lambda e: b["ev"](design, e)  # noqa: E731
    n = int(round(v("jb_n")))
    y0, ln = v("%s + seam_gap" % b["YW"]), v("side_l")          # L1 on the band (skeleton P04)
    ys = [y0 + v("jb_e") + i * (ln - 2 * v("jb_e")) / (n - 1) for i in range(n)]
    ys += [y0 + v("sp_e"), y0 + ln - v("sp_e")]
    x = v("%s + jb_x" % b["XL"])
    return sorted((round(x, 2), round(y, 2)) for y in ys)


def measure(b, design):
    boxes = {}
    for key in ("band_l_tube", "band_b_tube", "bracket", "floor_f1", "mat_f1"):
        comp = b["find_comp"](design, key)
        boxes[key] = b["bbox_mm"](comp.bRepBodies.item(0))
    body = b["find_comp"](design, "band_l_tube").bRepBodies.item(0)
    holes = b["centres"](body, b["ev"](design, "rn_hole"), "z")
    return boxes, holes


def unhealthy(design):
    tl = design.timeline
    ok = adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState
    return ["%s: %s" % (tl.item(i).name, tl.item(i).errorOrWarningMessage)
            for i in range(tl.count) if tl.item(i).healthState != ok]


def compare(got, want, tol=0.05):
    return max(abs(a - c) for a, c in zip(got, want))


def run(_context):
    b = load_build()
    app = adsk.core.Application.get()
    src = app.activeDocument
    doc = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(F3D))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    failures = []
    try:
        up = design.userParameters
        print("edit test on a copy of %s (root %s, %d user parameters, %d timeline items)" % (
            os.path.relpath(F3D, b["REPO"]), design.rootComponent.partNumber, up.count, design.timeline.count))
        before_boxes, before_holes = measure(b, design)
        original = {}
        for label, edits in EDITS:
            for name, expr in edits.items():
                p = up.itemByName(name)
                if p is None:
                    raise RuntimeError("no parameter " + name)
                original.setdefault(name, p.expression)
                p.expression = expr
            adsk.doEvents()
            design.computeAll()
            bad = unhealthy(design)
            boxes, holes = measure(b, design)
            want = expected_boxes(b, design)
            print("edit: %s -> %s" % (label, ", ".join("%s = %s" % kv for kv in edits.items())))
            print("  timeline: %s" % ("healthy" if not bad else "UNHEALTHY %s" % bad))
            if bad:
                failures.append(label + ": timeline")
            for key, box in boxes.items():
                d = compare(box, want[key])
                print("  %-36s %s  %s" % (b["PARTS"][key][1], b["fmt_box"](box),
                                          "follows" if d < 0.05 else "OFF by %.3f mm" % d))
                if d >= 0.05:
                    failures.append("%s: %s" % (label, key))
            wh = expected_side_holes(b, design)
            same = len(holes) == len(wh) and all(abs(a[0] - c[0]) < 0.05 and abs(a[1] - c[1]) < 0.05
                                                 for a, c in zip(holes, wh))
            print("  side band rivnut holes (X, Y): %d, %s" % (len(holes), "follow" if same else
                                                               "OFF: got %s want %s" % (holes, wh)))
            if not same:
                failures.append(label + ": side band holes")
        for name, expr in original.items():
            up.itemByName(name).expression = expr
        adsk.doEvents()
        design.computeAll()
        after_boxes, after_holes = measure(b, design)
        worst = max(compare(after_boxes[k], before_boxes[k]) for k in before_boxes)
        back = worst < 0.01 and after_holes == before_holes and not unhealthy(design)
        print("revert to the design values: largest difference %.4f mm, holes %s, timeline %s -> %s" % (
            worst, "same" if after_holes == before_holes else "DIFFERENT",
            "healthy" if not unhealthy(design) else "UNHEALTHY", "RESTORED" if back else "NOT RESTORED"))
        if not back:
            failures.append("revert")
    finally:
        doc.close(False)
        src.activate()
    print("RESULT: %s" % ("PASS, every part we make follows its parameters and comes back" if not failures
                          else "FAIL %s" % failures))
    if failures:
        raise RuntimeError("edit test failed: %s" % failures)
