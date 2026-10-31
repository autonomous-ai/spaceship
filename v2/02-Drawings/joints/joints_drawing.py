"""The joints' two drawings: views, dimensions and PDF, one Fusion run each, plus a local finish.

    # 1. start the empty drawing (needs the unlocked screen; tools/fusion/README.md)
    python3 tools/fusion/start_drawing.py 831001_P01_HARDWARE-LOCATING-SPIGOT_CAD \\
        831001_P01_HARDWARE-LOCATING-SPIGOT_DWG --folder "Default Project/FocusPod v2/joints" --sheet A3
    # 2. one annotate run: base views, dimensions, configuration and hole tables, raw PDF
    python3 tools/fusion/run_script.py v2/02-Drawings/joints/joints_drawing.py \\
        --doc 831001_P01_HARDWARE-LOCATING-SPIGOT_DWG --folder "Default Project/FocusPod v2/joints" \\
        --arg part=spigot --save "views, dimensions, PDF" --close
    # 3. local finish: clear "Created by", add the notes as PDF text, render a PNG
    python3 v2/02-Drawings/joints/joints_drawing.py finish spigot

The same for part=keys with 111211_P01_BASE-CORNER-KEY-TABULATED_CAD / _DWG (TABULATED:
111211, 111212, 111213, 111214, drawn as the square 111211).

Why the notes go in as PDF text: the drawing API can't write free text on a sheet (custom
table cells come out blank, tools/fusion/README.md), so units, material, finish, tolerance,
hole notes and the tabulated sizes are added to the exported PDF from NOTES below, in the
sheet's free top-right area. Where the API does write text (dimensions, a hole table, the
configuration table of a configured design and its title), the native drawing has it too.
First-angle layout with base views at one scale (PM ruling, README). Offline test:
test_joints_drawing.py.
"""
import os
import sys

try:
    import adsk.core
    import adsk.drawing
except ImportError:          # the local finish and the offline test run without Fusion
    adsk = None

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""

PARTS = {
    "spigot": {
        "drawing": "831001_P01_HARDWARE-LOCATING-SPIGOT_DWG",
        "scale": 5.0,
        # views: name, Fusion orientation name, sheet centre (mm, A3 420 x 297), style
        "views": [("front", "FrontViewOrientationType", (120.0, 185.0), "hidden"),
                  ("top", "TopViewOrientationType", (120.0, 85.0), "visible")],
        "notes": [
            "NOTES (831001 P01, PROPOSED)",
            "1. UNITS MM. ISO FIRST-ANGLE PROJECTION. GENERAL TOLERANCE ISO 2768-m UNLESS STATED.",
            "2. MATERIAL STAINLESS STEEL A2 (1.4301 OR 1.4305). FINISH AS MACHINED, DEBURRED.",
            "3. PIN Ø8 h9 (0 / -0.036), 7.24 ABOVE ITS SHOULDER, LEAD-IN 1 x 45°.",
            "4. STUD M6x1-6g, 8 LONG. HEX SOCKET 4 AF x 3.5 DEEP IN THE PIN'S TOP.",
            "5. FITTED AT THE FACTORY INTO RIVNUT 838003 WITH THREADLOCKER; THE SHOULDER SITS ON",
            "   THE RIVNUT'S 0.76 HEAD, SO THE PIN'S TOP IS 8.00 ABOVE THE TUBE FACE.",
            "6. JOINTS REGISTER H-05. STEP: v2/03-Manufacturing/joints/831001_P01_..._STEP.step",
        ],
    },
    "keys": {
        "drawing": "111211_P01_BASE-CORNER-KEY-TABULATED_DWG",
        "scale": 2.0,
        "views": [("front", "FrontViewOrientationType", (175.0, 185.0), "hidden"),
                  ("right", "RightViewOrientationType", (80.0, 185.0), "visible"),
                  ("top", "TopViewOrientationType", (175.0, 65.0), "hidden")],
        "notes": [
            "NOTES (111211 TO 111214 P01, PROPOSED) - TABULATED",
            "1. UNITS MM. ISO FIRST-ANGLE PROJECTION. GENERAL TOLERANCE ISO 2768-m UNLESS STATED.",
            "2. MATERIAL EN AW-6061-T6. FINISH MILL FINISH, DEBURRED, NO SHARP EDGES.",
            "3. ONE BLOCK 35 x 75, 25 LONG ON ITS CENTRE LINE. THE STUD FACE IS CUT AT ANGLE A",
            "   ABOUT ITS CENTRE LINE, LONG SIDE ON THE OUTSIDE OF THE TURN. SHOWN: 111211 (A = 0).",
            "   PART    A       HAND  LONG SIDE  SHORT SIDE  PER POD  WHERE",
            "   111211  0°      -     25.00      25.00       3        BACK CORNERS, FR1 INLINE",
            "   111212  24.14°  LH    32.84      17.16       1        FRONT LEFT CORNER",
            "   111213  24.02°  RH    32.80      17.20       1        FRONT RIGHT CORNER",
            "   111214  7.25°   LH    27.23      22.77       1        LEFT KNEE",
            "4. H01, H02: M6x1-6H THROUGH, SQUARE TO THE STUD FACE ON ITS CENTRE LINE, 26 AND 60",
            "   ABOVE THE BOTTOM; ±0.1 TO THE CENTRE LINE AND THE BOTTOM. CUT ANGLE ±0.25°.",
            "5. H03, H04: M6x1-6H, THREAD 15 DEEP, DRILL Ø5.0 x 18, FROM THE BOTTOM, 10 FROM THE",
            "   BACK FACE, 7.5 EITHER SIDE OF THE CENTRE LINE.",
            "6. JOINTS REGISTER J-BASE-02; POSITIONS v2/01-CAD-Native/joints/corner-keys.csv;",
            "   ONE STEP PER PART NUMBER IN v2/03-Manufacturing/joints/.",
        ],
        "table_title": "TABULATED 111211 TO 111214: CUT ANGLE A PER PART NUMBER",
    },
}
NOTES_BOX = (232.0, 12.0, 412.0, 150.0)   # sheet mm from the top-left corner: x0, y0, x1, y1
RAW_DIR = ".raw"                           # git-ignored, next to this file


# ------------------------------------------------------------------ geometry (pure, tested offline)
def corner(points, which):
    """The extreme point of a set: 'bl', 'br', 'tl', 'tr' (bottom-left, ...) in sheet x right, y up."""
    sx = 1 if which[1] == "r" else -1
    sy = 1 if which[0] == "t" else -1
    return max(points, key=lambda p: (sy * p[1] * 1000.0 + sx * p[0]))


def plan_dims(part, view, lines, circles, scale):
    """Dimensions to add, as (kind, a, b, place) in sheet mm; a and b are points on the view's
    geometry (line ends or circle centres), kind 'linear' or 'diameter' (b None, a the circle).
    lines: [(x0, y0, x1, y1)], circles: [(cx, cy, r)] in sheet mm."""
    pts = [(l[0], l[1]) for l in lines] + [(l[2], l[3]) for l in lines]
    if not pts:
        return []
    x0 = min(p[0] for p in pts)
    x1 = max(p[0] for p in pts)
    y0 = min(p[1] for p in pts)
    y1 = max(p[1] for p in pts)
    out = []
    if part == "spigot" and view == "front":
        # outline: pin (width 8) over stud (width 6); points at the shoulder and the ends
        bl, tl = corner(pts, "bl"), corner(pts, "tl")
        out.append(("linear", bl, tl, (x0 - 14.0, (y0 + y1) / 2)))                 # 15.24 overall
        shoulder = [p for p in pts if abs(p[0] - x0) < 1e-6]                         # pin's left side
        if shoulder:
            s_lo = min(shoulder, key=lambda p: p[1])
            out.append(("linear", s_lo, tl, (x0 - 6.0, (s_lo[1] + y1) / 2)))       # 7.24 pin
            out.append(("linear", bl, s_lo, (x0 - 6.0, (y0 + s_lo[1]) / 2)))       # 8 stud
            s_lo_r = max([p for p in pts if abs(p[1] - s_lo[1]) < 1e-6], key=lambda p: p[0])
            out.append(("linear", s_lo, s_lo_r, ((x0 + x1) / 2, s_lo[1] + 0.0 - 4.0)))  # Ø8 pin
        stud_bottom = [p for p in pts if abs(p[1] - y0) < 1e-6]
        if len(stud_bottom) >= 2:
            a = min(stud_bottom, key=lambda p: p[0])
            b = max(stud_bottom, key=lambda p: p[0])
            out.append(("linear", a, b, ((x0 + x1) / 2, y0 - 8.0)))                  # Ø6 stud
    elif part == "spigot" and view == "top":
        # hex socket: the two horizontal flats (shortest horizontal lines inside the outline)
        flats = [l for l in lines if abs(l[1] - l[3]) < 1e-6 and abs(l[0] - l[2]) > 1e-6]
        if len(flats) >= 2:
            lo = min(flats, key=lambda l: l[1])
            hi = max(flats, key=lambda l: l[1])
            a = (min(lo[0], lo[2]), lo[1])
            b = (min(hi[0], hi[2]), hi[1])
            out.append(("linear", a, b, (x0 - 8.0, (a[1] + b[1]) / 2)))              # 4 AF
    elif part == "keys" and view == "front":
        bl, tl, br = corner(pts, "bl"), corner(pts, "tl"), corner(pts, "br")
        out.append(("linear", bl, tl, (x0 - 10.0, (y0 + y1) / 2)))                  # 75
        out.append(("linear", bl, br, ((x0 + x1) / 2, y0 - 10.0)))                  # 25
    elif part == "keys" and view == "right":
        bl, br = corner(pts, "bl"), corner(pts, "br")
        out.append(("linear", bl, br, ((x0 + x1) / 2, y0 - 10.0)))                  # 35
        for i, c in enumerate(sorted(circles, key=lambda c: c[1])):                 # 26, 60 from the bottom
            out.append(("linear", bl, (c[0], c[1]), (x0 - 8.0 - 8.0 * i, (y0 + c[1]) / 2)))
        if circles:
            c = min(circles, key=lambda c: c[1])
            out.append(("linear", bl, (c[0], c[1]), ((x0 + c[0]) / 2, y1 + 8.0)))   # 17.5 to the centre line
            out.append(("diameter", (c[0], c[1], c[2]), None, (c[0] + 12.0, c[1] + 10.0)))
    elif part == "keys" and view == "top":
        if circles:
            cs = sorted(circles, key=lambda c: c[1])
            bl = corner(pts, "bl")
            out.append(("linear", bl, (cs[0][0], cs[0][1]), ((x0 + cs[0][0]) / 2, y0 - 8.0)))   # 10 from the back
            out.append(("linear", bl, (cs[0][0], cs[0][1]), (x0 - 8.0, (y0 + cs[0][1]) / 2)))   # 10 from the side
            if len(cs) > 1:
                out.append(("linear", (cs[0][0], cs[0][1]), (cs[-1][0], cs[-1][1]),
                            (x1 + 8.0, (cs[0][1] + cs[-1][1]) / 2)))                              # 15 between
            out.append(("diameter", cs[-1], None, (cs[-1][0] + 12.0, cs[-1][1] + 10.0)))
    return out


# ------------------------------------------------------------------ Fusion side
def _xy(dp):
    c = dp.coordinate
    return (c.x, c.y)


def _curves(view):
    lines, circles, refs = [], [], {}
    vc = view.viewCurves
    for i in range(vc.count):
        c = vc.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            a, b = _xy(c.startPoint), _xy(c.endPoint)
            lines.append((a[0], a[1], b[0], b[1]))
            refs.setdefault((round(a[0], 3), round(a[1], 3)), c.startPoint)
            refs.setdefault((round(b[0], 3), round(b[1], 3)), c.endPoint)
        elif c.type == adsk.drawing.ViewCurveTypes.CircleViewCurveType:
            o = _xy(c.centerPoint)
            r = getattr(c, "radius", None)
            if r is None:
                r = 0.0
            key = (round(o[0], 3), round(o[1], 3))
            if key not in [(round(x, 3), round(y, 3)) for x, y, _r in circles]:
                circles.append((o[0], o[1], r))
            refs.setdefault(key, c.centerPoint)
            refs.setdefault(("curve",) + key, c)
    return lines, circles, refs


def _dpt(x, y):
    return adsk.drawing.DrawingPoint.create(adsk.core.Point2D.create(x, y))


def _ref(refs, p):
    key = (round(p[0], 3), round(p[1], 3))
    if key in refs:
        return refs[key]
    best = min((k for k in refs if k[0] != "curve"), key=lambda k: (k[0] - p[0]) ** 2 + (k[1] - p[1]) ** 2)
    if (best[0] - p[0]) ** 2 + (best[1] - p[1]) ** 2 > 0.01:
        raise RuntimeError("no view point near %s" % (p,))
    return refs[best]


def add_views(sheet, cfg):
    views = {}
    for name, orient, centre, style in cfg["views"]:
        inp = sheet.views.createBaseViewInput()
        vp = inp.viewParameters
        vp.orientation = getattr(adsk.drawing.ViewOrientationTypes, orient)
        vp.scaleValue = cfg["scale"]
        vp.style = (adsk.drawing.DrawingViewStyleTypes.VisibleAndHiddenEdgesDrawingViewStyleType if style == "hidden"
                    else adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType)
        vp.centerMarkOptions.isAppliedToHoles = True
        vp.centerLineOptions.isAppliedToHoles = True
        inp.placementPoint = _dpt(*centre)
        v = sheet.views.add(inp)
        if v is None:
            raise RuntimeError("Views.add returned None for the %s view" % name)
        if abs(v.scaleValue - cfg["scale"]) > 1e-6:
            v.scaleValue = cfg["scale"]          # the input's scale is ignored in this build (README)
        views[name] = v
    return views


def annotate(sheet, part, views, cfg):
    n = 0
    for name, v in views.items():
        lines, circles, refs = _curves(v)
        for kind, a, b, place in plan_dims(part, name, lines, circles, cfg["scale"]):
            if kind == "linear":
                d = sheet.drawingDimensions.addLinearDimension(_ref(refs, a), _ref(refs, b), _dpt(*place), False)
            else:
                curve = refs.get(("curve", round(a[0], 3), round(a[1], 3)))
                d = sheet.drawingDimensions.addDiameterDimension(curve, _dpt(*place)) if curve else None
            if d is None:
                print("  WARNING: %s dimension on the %s view not added" % (kind, name))
            else:
                n += 1
        print("  %s view: %d lines, %d circles" % (name, len(lines), len(circles)))
    return n


def tables(sheet, part, views, cfg, dwg):
    made = []
    if part == "keys":
        try:
            ti = sheet.configurationTables.createInput()
            ti.title = cfg["table_title"]
            if sheet.configurationTables.add(ti):
                made.append("configuration table")
        except Exception as ex:
            print("  NOTE: no configuration table (%s); the PDF notes carry the tabulated sizes" % ex)
        for vname, title, corner_name in (("right", "H01-H02: M6x1-6H THROUGH", "bl"),
                                          ("top", "H03-H04: M6x1-6H x 15", "bl")):
            try:
                lines, circles, refs = _curves(views[vname])
                pts = [(l[0], l[1]) for l in lines] + [(l[2], l[3]) for l in lines]
                inp = sheet.holeTables.createInput()
                inp.view = views[vname]
                inp.originPoint = _ref(refs, corner(pts, corner_name))
                inp.title = title
                if sheet.holeTables.add(inp):
                    made.append("hole table " + title.split(":")[0])
            except Exception as ex:
                print("  NOTE: hole table on the %s view not made (%s)" % (vname, ex))
    return made


def projection_symbol(sheet, x0=236.0, y0=72.0, d=5.0, big=10.0, length=10.0, gap=4.0):
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    p2 = adsk.core.Point2D.create
    pts = [p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
           p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)]
    sk.lines.add(pts)
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)


def run(_context):
    part = ARGS.get("part")
    if part not in PARTS:
        raise RuntimeError("--arg part=spigot or part=keys")
    cfg = PARTS[part]
    app = adsk.core.Application.get()
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("the active document isn't a drawing: open it with --doc %s" % cfg["drawing"])
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views: views can't be deleted by the API, so start a new "
                           "drawing instead of annotating twice" % sheet.views.count)
    print("sheet %s: %.1f x %.1f" % (sheet.name, sheet.width, sheet.height))
    views = add_views(sheet, cfg)
    n = annotate(sheet, part, views, cfg)
    made = tables(sheet, part, views, cfg, dwg)
    projection_symbol(sheet)
    raw = os.path.join(ARGS["repo_root"], "v2/02-Drawings/joints", RAW_DIR, cfg["drawing"] + ".pdf")
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("%s: %d views, %d dimensions, %s; raw PDF %s (finish it locally)" % (
        cfg["drawing"], len(views), n, ", ".join(made) or "no tables", os.path.relpath(raw, ARGS["repo_root"])))


# ------------------------------------------------------------------ local finish (no Fusion)
def add_notes(pdf_in, pdf_out, lines, box=NOTES_BOX):
    """Write the notes as real PDF text in the sheet's free area (box in sheet mm from the top-left)."""
    import fitz
    doc = fitz.open(pdf_in)
    page = doc[0]
    k = page.rect.width / 420.0                     # PDF points per sheet mm (A3 landscape)
    rect = fitz.Rect(box[0] * k, box[1] * k, box[2] * k, box[3] * k)
    left = page.insert_textbox(rect, "\n".join(lines), fontsize=(2.0 / 0.7) * k, fontname="cour")   # 2.0 capital height
    if left < 0:
        raise SystemExit("the notes don't fit their box (%.1f pt short)" % -left)
    doc.save(pdf_out)
    return pdf_out


def finish(part):
    import subprocess
    import fitz
    cfg = PARTS[part]
    raw = os.path.join(HERE, RAW_DIR, cfg["drawing"] + ".pdf")
    clean = os.path.join(HERE, RAW_DIR, cfg["drawing"] + "-clean.pdf")
    out = os.path.join(HERE, cfg["drawing"] + ".pdf")
    repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    subprocess.run([sys.executable, os.path.join(repo, "tools/fusion/pdf_clear_field.py"), raw, clean], check=True)
    add_notes(clean, out, cfg["notes"])
    page = fitz.open(out)[0]
    page.get_pixmap(dpi=110).save(os.path.join(HERE, cfg["drawing"] + "-render.png"))
    print("wrote %s and its render" % os.path.relpath(out, repo))


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "finish":
    finish(sys.argv[2])
