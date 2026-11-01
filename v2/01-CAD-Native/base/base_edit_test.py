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
]


def load_build():
    # the run's own settings (scope, batch2), so P02's batches load as the build loaded them
    ns = {"__name__": "base_build", "__file__": BUILD, "SCRIPT_ARGS": dict(globals().get("SCRIPT_ARGS", {}))}
    with open(BUILD, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), BUILD, "exec"), ns)
    return ns


# P02 batch 1's parts we make (base_p02.py): measured too, so a skeleton edit is shown to move them (not only to
# leave the timeline healthy)
P02_KEYS = ("band_r_tube", "fr1", "sill")


def expected_boxes(b, design):
    v = lambda e: b["ev"](design, e)  # noqa: E731
    XL, XR, YB = b["XL"], b["XR"], b["YB"]
    ym = min(v("-dl_y1"), v(b["Y_MITRE_IN"]))
    out = {
        "band_l_tube": (v(XL), ym, v("glide_h"), v("%s + band_t" % XL), v(YB), v("wall_z0")),
        "band_b_tube": (v("%s + band_t" % XL), v("%s - band_t" % YB), v("glide_h"), v("%s - band_t" % XR), v(YB),
                        v("wall_z0")),
    }
    if "X_FR0" in b:            # the same expressions as base_p02.py's steps
        XR_, X_FR0 = b["XR_"], b["X_FR0"]
        out["band_r_tube"] = (v("%s - band_t" % XR_), min(v("-dr_yc"), v(b["Y_MITRE_IN_R"])), v("glide_h"), v(XR_),
                              v(YB), v("wall_z0"))
        out["fr1"] = (v(X_FR0), v("-pod_d / 2"), v("glide_h"), v("x_fr_joint"), v("-pod_d / 2 + band_t"), v("wall_z0"))
        out["sill"] = (v(X_FR0), v("-pod_d / 2 + band_t"), v("glide_h"), v("sl_x1"), v("-glass_y + ch_w / 2 + sl_t"),
                       v("wall_z0"))
    if "fl1" in b["PARTS"]:     # batch 2: DL's two facets (FL2 with its welded door-end block)
        XL_, IL2X, IL2Y = b["XL_"], b["IL2_X"], b["IL2_Y"]
        out["fl1"] = (v(XL_), v("-dl_y2"), v("glide_h"), v(IL2X), v(b["Y_MITRE_IN"]), v("wall_z0"))
        # FL2's door-end plate (the hinge-side ruling) runs inward to the kick strip's back line
        out["fl2"] = (v("%s + dl_x2" % XL_), v("-dl_y3"), v("glide_h"), v("%s + dl_w" % XL_),
                      max(v(IL2Y), v(b["Y_KICK_BACK"])), v("wall_z0"))
    return out


def expected_side_holes(b, design):
    v = lambda e: b["ev"](design, e)  # noqa: E731
    n = int(round(v("jb_n")))
    y0, ln = v("%s + seam_gap" % b["YW"]), v("side_l")          # L1 on the band (skeleton P04)
    ys = [y0 + v("jb_e") + i * (ln - 2 * v("jb_e")) / (n - 1) for i in range(n)]
    ys += [y0 + v("sp_e"), y0 + ln - v("sp_e")]
    x = v("%s + jb_x" % b["XL"])
    return sorted((round(x, 2), round(y, 2)) for y in ys)


def expected_back_corner(b, design):
    """D-129: the back key's fixing holes (X, Y) and stud bolt holes (Y, Z) in the left side band, and the
    back band's slot ends (Y, Z), from the same expressions as the build."""
    v = lambda e: b["ev"](design, e)  # noqa: E731
    yc = v("pod_d / 2 - band_t / 2")
    xf = -v("pod_w / 2 - band_t + band_wall + ck_x - ck_e")
    xf2 = -v("pod_w / 2 - band_t + band_wall + ck_x - ck_e2")      # D-144: the stepped hole
    fix = [(xf, yc + v("ck_fy")), (xf2, yc - v("ck_fy"))]
    studs = [(yc, v("glide_h + band_wall + %s" % z)) for z in ("st_z1", "st_z2")]
    slot = [(yc, v("glide_h + band_wall + st_z2 + bs_end"))]
    return fix, studs, slot


def measure_back_corner(b, design):
    side = b["find_comp"](design, "band_l_tube").bRepBodies.item(0)
    back = b["find_comp"](design, "band_b_tube").bRepBodies.item(0)
    ev = b["ev"]
    return (b["centres"](side, ev(design, "ck_fix_hole"), "z"), b["centres"](side, ev(design, "st_hole"), "x"),
            b["centres"](back, ev(design, "kh_slot"), "x"))


def expected_p02_holes(b, design):
    """P02's holes the test measures too (Reviewer 8's P3 on #303), from the same expressions as base_p02.py's steps:
    {what: (part key, hole diameter, axis, centres)}. The sill's channel rivnuts follow FRONT's linked glass lines and
    FR1's joint (as FRONT's channel holes do); FR1's keyholes and glides; the RH band's J-BASE-01 and spigot rivnuts."""
    v = lambda e: b["ev"](design, e)  # noqa: E731
    if "X_FR0" not in b:
        return {}
    X_FR0, XR_ = b["X_FR0"], b["XR_"]
    r2 = lambda pts: sorted((round(p, 2), round(q, 2)) for p, q in pts)  # noqa: E731
    gy, yc = v("-glass_y"), v("-pod_d / 2 + band_t / 2")
    sill = [(v("ch_screw_x1 + %d * ch_screw_p" % i), gy) for i in range(3)] + [(v("ch_screw_x4"), gy)]
    z1, z2, kh = v("glide_h + band_wall + st_z1"), v("glide_h + band_wall + st_z2"), v("kh_drop")
    glides = [(v("%s + gl_e_f" % X_FR0), yc), (v("x_fr_joint - gl_e_f"), yc)]
    n = int(round(v("jb_n")))
    y0, ln, xb = v("base_side_y0"), v("side_l"), v("%s - jb_x" % XR_)
    rh = [(xb, y0 + v("jb_e") + i * (ln - 2 * v("jb_e")) / (n - 1)) for i in range(n)]
    rh += [(xb, y0 + v("sp_e")), (xb, y0 + ln - v("sp_e"))]
    return {
        "sill channel rivnut holes (X, Y)": ("sill", v("ch_rn_hole"), "z", r2(sill)),
        "FR1 keyhole entries (Y, Z)": ("fr1", v("kh_entry"), "x", r2([(yc, z1 - kh), (yc, z2 - kh)])),
        "FR1 keyhole seats (Y, Z)": ("fr1", v("kh_slot"), "x", r2([(yc, z1), (yc, z2)])),
        "FR1 glide nut holes (X, Y)": ("fr1", v("gl_nut_hole"), "z", r2(glides)),
        "side band RH rivnut holes (X, Y)": ("band_r_tube", v("rn_hole"), "z", r2(rh)),
    }


def measure_p02_holes(b, design):
    return {what: b["centres"](b["find_comp"](design, key).bRepBodies.item(0), dia, ax)
            for what, (key, dia, ax, _w) in expected_p02_holes(b, design).items()}


def same_points(got, want):
    return len(got) == len(want) and all(abs(a[0] - c[0]) < 0.05 and abs(a[1] - c[1]) < 0.05
                                         for a, c in zip(sorted(got), sorted(want)))


def found(got, want):
    return all(any(abs(g[0] - w[0]) < 0.05 and abs(g[1] - w[1]) < 0.05 for g in got) for w in want)


def measure(b, design):
    boxes = {}
    for key in ("band_l_tube", "band_b_tube") + (P02_KEYS if "X_FR0" in b else ()) + \
            (("fl1", "fl2") if "fl1" in b["PARTS"] else ()):
        comp = b["find_comp"](design, key)
        boxes[key] = b["bbox_mm"](comp.bRepBodies.item(0))
    body = b["find_comp"](design, "band_l_tube").bRepBodies.item(0)
    holes = b["centres"](body, b["ev"](design, "rn_hole"), "z")
    return boxes, holes


def unhealthy(design):
    """As the build's check: a timeline group (the key's STEP import makes one) is judged by its members."""
    return BUILD_NS["timeline_problems"](design)


def compare(got, want, tol=0.05):
    return max(abs(a - c) for a, c in zip(got, want))


BUILD_NS = {}


def run(_context):
    b = load_build()
    b["load_p02"]()             # P02's names and parts (batch 1), as the build's --arg scope=p02
    BUILD_NS.update(b)
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
        before_bc = measure_back_corner(b, design)
        before_p02 = measure_p02_holes(b, design)
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
            got_bc, want_bc = measure_back_corner(b, design), expected_back_corner(b, design)
            ok_bc = all(found(g, w) for g, w in zip(got_bc, want_bc))
            print("  back corner (D-129): key fixing and stud bolt holes, slot ends: %s" % (
                "follow" if ok_bc else "OFF: got %s want %s" % (got_bc, want_bc)))
            if not ok_bc:
                failures.append(label + ": back corner holes")
            got_p02 = measure_p02_holes(b, design)
            for what, (_k, _d, _a, want_pts) in expected_p02_holes(b, design).items():
                ok = same_points(got_p02[what], want_pts)
                print("  %s: %d, %s" % (what, len(got_p02[what]), "follow" if ok else
                                        "OFF: got %s want %s" % (got_p02[what], want_pts)))
                if not ok:
                    failures.append("%s: %s" % (label, what))
        for name, expr in original.items():
            up.itemByName(name).expression = expr
        adsk.doEvents()
        design.computeAll()
        after_boxes, after_holes = measure(b, design)
        worst = max(compare(after_boxes[k], before_boxes[k]) for k in before_boxes)
        back = worst < 0.01 and after_holes == before_holes and measure_back_corner(b, design) == before_bc \
            and measure_p02_holes(b, design) == before_p02 and not unhealthy(design)
        print("revert to the design values: largest difference %.4f mm, holes %s, timeline %s -> %s" % (
            worst, "same" if after_holes == before_holes else "DIFFERENT",
            "healthy" if not unhealthy(design) else "UNHEALTHY", "RESTORED" if back else "NOT RESTORED"))
        if not back:
            failures.append("revert")
    finally:
        doc.close(False)
        if src is not None:         # the build may have closed its own saved document already (2026-11-01, run D)
            src.activate()
    print("RESULT: %s" % ("PASS, every part we make follows its parameters and comes back" if not failures
                          else "FAIL %s" % failures))
    if failures:
        raise RuntimeError("edit test failed: %s" % failures)
