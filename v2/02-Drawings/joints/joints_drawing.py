"""The joints' two drawings: views, dimensions and PDF, one Fusion run each, plus a local finish.

    # 1. start the empty drawing (needs the unlocked screen; tools/fusion/README.md)
    python3 tools/fusion/start_drawing.py 831001_P01_HARDWARE-LOCATING-SPIGOT_CAD \\
        831001_P01_HARDWARE-LOCATING-SPIGOT_DWG --folder "Default Project/FocusPod v2/joints" --sheet A3
    # 2. one annotate run: it checks the screen is unlocked, opens the drawing itself, adds the
    #    base views, dimensions and projection symbol, exports the raw PDF, saves and closes
    python3 tools/fusion/run_script.py v2/02-Drawings/joints/joints_drawing.py --arg part=spigot,keys
    # 3. local finish: clear "Created by", add the notes as PDF text, render a PNG
    python3 v2/02-Drawings/joints/joints_drawing.py finish spigot

The same for part=keys with 111211_P01_BASE-CORNER-KEY-TABULATED_CAD / _DWG (TABULATED:
111211, 111212, 111213, 111214, drawn as the square 111211).

Why the notes go in as PDF text: the drawing API can't write free text on a sheet (custom
table cells come out blank, tools/fusion/README.md), so units, material, finish, tolerance,
hole notes and the tabulated sizes are added to the exported PDF from the notes below, in
the sheet's free top-right area; the dimensions are native. No hole or configuration tables:
the API can't place them, and they land on the top-right corner (README).
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

RIGHT_HOLES = lambda cs: [c for c in cs if c[2] and c[0] < 130]           # the stud face's view, solid
TOP_HOLES = lambda cs: [c for c in cs if not c[2] and 130 < c[0] < 230 and c[1] > 195]   # from above, hidden

PARTS = {
    "spigot": {
        "drawing": "831001_P01_HARDWARE-LOCATING-SPIGOT_DWG",
        "scale": 5.0,
        # TABULATED since the Lead's ruling of 2026-11-01 (J-FRONT-03): 831010 is 831001 with the pin 3 longer
        "title": "HARDWARE - LOCATING SPIGOT - TABULATED: 831001, 831010",
        # views: name, Fusion orientation name, sheet centre (mm, A3 420 x 297, from the bottom left), style
        "views": [("front", "FrontViewOrientationType", (120.0, 185.0), "hidden"),
                  ("top", "TopViewOrientationType", (120.0, 85.0), "visible")],
        # the two sizes the table varies, lettered on the front view in the finish (Reviewer 10 on #346: the view
        # printed 831001's 7.24 and 15.24, which disagree with 831010's row): Fusion's value -> the letter
        "letters": [("7.24", "L"), ("15.24", "L + 8")],
        "notes": [
            "NOTES (831001, 831010 P01, PROPOSED) - TABULATED",
            "1. UNITS MM. SCALE 5:1. ISO FIRST-ANGLE PROJECTION. GENERAL TOLERANCE ISO 2768-m UNLESS STATED.",
            "2. MATERIAL STAINLESS STEEL A2 (1.4301 OR 1.4305). FINISH PASSIVATED, DEBURRED.",
            "3. PIN Ø8 h9 (0 / -0.036), LEAD-IN 1 x 45°. THE FRONT VIEW'S L IS THE PIN ABOVE ITS SHOULDER AND "
            "L + 8 IS ITS OVERALL LENGTH; THE TABLE GIVES BOTH FOR EACH PART.",
            {"indent": 5.0,
             "table": [["PART", "L", "PROUD", "OVERALL", "POD", "WHERE"],
                       ["831001", "7.24", "8.00", "15.24", "24", "BAND, SEAMS, CEILING, DL, DR"],
                       ["831010", "10.24", "11.00", "18.24", "2", "DR'S LEDGE, UNDER DT"]]},
            "4. STUD M6x1-6g, 8 LONG (SHOWN AT THE 6g MEAN MAJOR Ø5.88). HEX SOCKET 4 AF x 3.5 DEEP.",
            "5. FITTED AT THE FACTORY INTO RIVNUT 838003 WITH THREADLOCKER; THE SHOULDER SITS ON THE RIVNUT'S "
            "0.76 HEAD, SO THE PIN'S TOP STANDS THE TABLE'S PROUD ABOVE THE FACE THE RIVNUT IS SET IN.",
            "6. JOINTS REGISTER H-05, H-45. ONE STEP PER PART NUMBER IN v2/03-Manufacturing/joints/.",
        ],
    },
    "keys": {
        "drawing": "111211_P01_BASE-CORNER-KEY-TABULATED_DWG",
        "title": "BASE - CORNER KEY - TABULATED: 111211, 111212, 111213, 111214",
        "scale": 2.0,
        "views": [("front", "FrontViewOrientationType", (175.0, 185.0), "hidden"),
                  ("right", "RightViewOrientationType", (80.0, 185.0), "visible"),
                  ("top", "TopViewOrientationType", (175.0, 65.0), "hidden")],
        "notes": [
            "NOTES (111211 TO 111214 P01, PROPOSED) - TABULATED",
            "1. UNITS MM. ISO FIRST-ANGLE PROJECTION. GENERAL TOLERANCE ISO 2768-m UNLESS STATED.",
            "2. MATERIAL EN AW-6061-T6. FINISH MILL FINISH, DEBURRED, NO SHARP EDGES.",
            "3. ONE BLOCK 35 x 75, 30 LONG ON ITS CENTRE LINE. THE STUD FACE IS CUT AT ANGLE A ABOUT ITS CENTRE "
            "LINE, LONG SIDE ON THE OUTSIDE OF THE TURN. THE THREE VIEWS SHOW 111211 (A = 0); VIEW B SHOWS "
            "111212 FROM ABOVE; 111213 IS 111212'S OPPOSITE HAND (MIRRORED ABOUT THE CENTRE LINE).",
            {"indent": 5.0,
             "table": [["PART", "A", "HAND", "LONG SIDE", "SHORT SIDE", "PER POD", "WHERE"],
                       ["111211", "0°", "-", "30.00", "30.00", "3", "BACK CORNERS, FR1 INLINE"],
                       ["111212", "24.14°", "LH", "37.84", "22.16", "1", "FRONT LEFT CORNER"],
                       ["111213", "24.02°", "RH", "37.80", "22.20", "1", "FRONT RIGHT CORNER"],
                       ["111214", "7.25°", "LH", "32.23", "27.77", "1", "LEFT KNEE"]]},
            "4. H01, H02: M6x1-6H THROUGH, SQUARE TO THE STUD FACE ON ITS CENTRE LINE, 26 AND 60 ABOVE THE "
            "BOTTOM; ±0.1 TO THE CENTRE LINE AND THE BOTTOM. CUT ANGLE ±0.25°. THE VIEWS SHOW THE TAPPED HOLES "
            "AT THE 6H MEAN MINOR Ø5.04 (TAP DRILL Ø5.0).",
            "5. H03, H04: M6x1-6H, THREAD 15 DEEP, DRILL Ø5.0 x 18, FROM THE BOTTOM, 10.5 FROM THE BACK FACE, "
            "7.0 EITHER SIDE OF THE CENTRE LINE.",
            "6. JOINTS REGISTER J-BASE-02; POSITIONS v2/01-CAD-Native/joints/corner-keys.csv; ONE STEP PER PART "
            "NUMBER IN v2/03-Manufacturing/joints/.",
        ],
        # hole tags and thread callouts at the holes (guideline 6.2): (which circle, lines, text offset in mm)
        "tag_hole_dia": 5.04,
        "tags": [
            (lambda cs: min(RIGHT_HOLES(cs), key=lambda c: c[1]), ["H02", "M6x1-6H THRU"], (9.0, 1.0)),
            (lambda cs: max(RIGHT_HOLES(cs), key=lambda c: c[1]), ["H01", "M6x1-6H THRU"], (9.0, 1.0)),
            (lambda cs: min(TOP_HOLES(cs), key=lambda c: c[1]), ["H04 M6x1-6H", "15 DEEP"], (-23.0, -1.0)),
            (lambda cs: max(TOP_HOLES(cs), key=lambda c: c[1]), ["H03 M6x1-6H", "15 DEEP"], (9.0, 1.5)),
        ],
        "view_b": {"origin": (290.0, 170.0),
                   "label": "VIEW B, 2:1: 111212 (LH, FRONT LEFT CORNER) FROM ABOVE"},
    },
}
NOTES_BOX = (232.0, 12.0, 404.0, 150.0)   # sheet mm from the top-left corner: x0, y0, x1, y1
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
            if len(cs) > 1:     # from the corner, never centre to centre: two hidden circles' centres
                # gave a dimension with no model link, which showed the sheet distance (28 for 14)
                out.append(("linear", bl, (cs[-1][0], cs[-1][1]), (x1 + 8.0, (y0 + cs[-1][1]) / 2)))  # 24.5
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


def projection_symbol(sheet, x0=236.0, y0=72.0, d=5.0, big=10.0, length=10.0, gap=4.0):
    sk = sheet.sketches.add("PROJECTION SYMBOL - FIRST ANGLE")
    p2 = adsk.core.Point2D.create
    pts = [p2(x0, y0 - d / 2), p2(x0 + length, y0 - big / 2), p2(x0 + length, y0 + big / 2),
           p2(x0, y0 + d / 2), p2(x0, y0 - d / 2)]
    sk.lines.add(pts)
    cx = x0 + length + gap + big / 2
    sk.circles.addByCenterRadius(p2(cx, y0), big / 2)
    sk.circles.addByCenterRadius(p2(cx, y0), d / 2)


FOLDER = ("Default Project", "FocusPod v2", "joints")


def screen_locked():
    """True while the Mac's screen is locked: opening a drawing then has hung Fusion (README)."""
    import plistlib
    import subprocess
    out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=30).stdout
    users = plistlib.loads(out).get("IOConsoleUsers") or []
    return any(u.get("CGSSessionScreenIsLocked") for u in users)


def open_drawing(app, name):
    proj = next(p for p in app.data.dataProjects if p.name == FOLDER[0])
    folder = proj.rootFolder
    for part in FOLDER[1:]:
        folder = folder.dataFolders.itemByName(part)
        if folder is None:
            raise RuntimeError("no folder %s" % "/".join(FOLDER))
    found = []
    for i in range(folder.dataFiles.count):
        try:
            df = folder.dataFiles.item(i)
            if df.name == name and df.fileExtension == "f2d":
                found.append(df)
        except Exception:
            continue                    # an entry that can't be read now isn't ours to open
    if len(found) != 1:
        raise RuntimeError("%d drawings called %s in %s" % (len(found), name, "/".join(FOLDER)))
    return app.documents.open(found[0], True)


def run(_context):
    """--arg part=spigot, part=keys or part=spigot,keys (both drawings in one run, one queue place)."""
    parts = [p.strip() for p in ARGS.get("part", "").split(",") if p.strip()]
    if not parts or any(p not in PARTS for p in parts):
        raise RuntimeError("--arg part=spigot, keys or spigot,keys")
    app = adsk.core.Application.get()
    failed = []
    for part in parts:
        cfg = PARTS[part]
        if screen_locked():
            failed.append("%s (the screen is locked: not opened, it could hang Fusion)" % cfg["drawing"])
            continue
        doc = open_drawing(app, cfg["drawing"])
        try:
            annotate_and_export(app, doc, part, cfg)
            if not doc.save("Views, dimensions and PDF by v2/02-Drawings/joints/joints_drawing.py"):
                raise RuntimeError("saving the drawing failed")
            print("saved %s (new version)" % cfg["drawing"])
        except Exception as ex:
            failed.append("%s (%s)" % (cfg["drawing"], ex))
        finally:
            print("closed %s: %s" % (cfg["drawing"], doc.close(False)))
    if failed:
        raise RuntimeError("not done: " + "; ".join(failed))


def annotate_and_export(app, doc, part, cfg):
    dwg = adsk.drawing.Drawing.cast(app.activeProduct)
    if dwg is None:
        raise RuntimeError("%s didn't open as a drawing" % cfg["drawing"])
    try:                              # draw the design's newest saved version
        print("references updated: %s" % doc.updateAllReferences())
    except Exception as ex:
        print("  NOTE: references not updated (%s)" % ex)
    sheet = dwg.activeSheet
    if sheet.views.count:
        raise RuntimeError("the sheet already has %d views: views can't be deleted by the API, so start a new "
                           "drawing instead of annotating twice" % sheet.views.count)
    print("sheet %s: %.1f x %.1f" % (sheet.name, sheet.width, sheet.height))
    views = add_views(sheet, cfg)
    n = annotate(sheet, part, views, cfg)
    projection_symbol(sheet)
    raw = os.path.join(ARGS["repo_root"], "v2/02-Drawings/joints", RAW_DIR, cfg["drawing"] + ".pdf")
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    opts = dwg.exportManager.createPDFExportOptions(raw)
    opts.openPDF = False
    opts.useLineWeights = True
    if not dwg.exportManager.execute(opts):
        raise RuntimeError("PDF export failed")
    print("%s: %d views, %d dimensions; raw PDF %s (finish it locally)" % (
        cfg["drawing"], len(views), n, os.path.relpath(raw, ARGS["repo_root"])))


# ------------------------------------------------------------------ local finish (no Fusion)
# Sizes and line styles match what Fusion writes into the PDF (read from the key sheet's export): visible
# outlines 1.44 pt, thin lines 0.72 pt, dimension text 13.9 pt (3.5 mm capitals), arrowheads 3.5 x 1.2 mm.
NOTE_MM = 2.5 / 0.718                  # Helvetica size for 2.5 mm capitals (ISO 3098; the D-114 visual pass)
DIM_MM = 3.5 / 0.718                   # 3.5 mm capitals, as Fusion's dimensions
W_THICK, W_THIN = 1.44, 0.72           # pt
HIDDEN = "[7.4 2.8] 0"                 # pt: 2.6 mm dashes, 1 mm gaps, as Fusion's hidden lines
CHAIN = "[17 2.8 2.8 2.8] 0"           # pt: centre lines
FONT = "helv"


class Sheet:
    """Drawing on a PDF page in sheet mm from the top-left corner (an A3 page is 420 x 297)."""

    def __init__(self, page):
        import fitz
        self.fitz, self.page, self.k = fitz, page, page.rect.width / 420.0
        self.font = fitz.Font(FONT)     # its widths count ±, ° and Ø as drawn; fitz.get_text_length doesn't

    def pt(self, p):
        return self.fitz.Point(p[0] * self.k, p[1] * self.k)

    def line(self, a, b, width=W_THIN, dashes=None):
        self.page.draw_line(self.pt(a), self.pt(b), color=(0, 0, 0), width=width, dashes=dashes)

    def poly(self, pts, width=W_THICK, closed=True):
        self.page.draw_polyline([self.pt(p) for p in pts] + ([self.pt(pts[0])] if closed else []),
                                color=(0, 0, 0), width=width)

    def circle(self, c, r, width=W_THIN, dashes=None):
        self.page.draw_circle(self.pt(c), r * self.k, color=(0, 0, 0), width=width, dashes=dashes)

    def arrow(self, tip, toward, length=3.5, width=1.2):
        """A filled arrowhead with its tip at tip, its tail toward the point toward."""
        import math
        dx, dy = toward[0] - tip[0], toward[1] - tip[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        base = (tip[0] + ux * length, tip[1] + uy * length)
        a = (base[0] - uy * width / 2, base[1] + ux * width / 2)
        b = (base[0] + uy * width / 2, base[1] - ux * width / 2)
        self.page.draw_polyline([self.pt(tip), self.pt(a), self.pt(b), self.pt(tip)], color=(0, 0, 0),
                                fill=(0, 0, 0), width=0)

    def text(self, p, s, size_mm=NOTE_MM, align="left", rotate=0):
        """Text with its baseline at p (sheet mm); align left, centre or right."""
        size = size_mm * self.k
        w = self.font.text_length(s, fontsize=size) / self.k
        x = p[0] - (w if align == "right" else w / 2 if align == "centre" else 0.0)
        self.page.insert_text(self.pt((x, p[1])), s, fontsize=size, fontname=FONT, rotate=rotate)
        return w

    def width(self, s, size_mm=NOTE_MM):
        return self.font.text_length(s, fontsize=size_mm * self.k) / self.k


def wrap(sheet, text, width, size_mm=NOTE_MM):
    """Words to lines no wider than width (mm)."""
    lines, cur = [], ""
    for w in text.split(" "):
        trial = (cur + " " + w) if cur else w
        if not cur or sheet.width(trial, size_mm) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def add_notes(pdf_in, pdf_out, notes, box=NOTES_BOX):
    """Write the notes as real PDF text in the sheet's free area (box in sheet mm from the top-left), at 2.5 mm
    capitals. A note is a paragraph (a numbered one hangs its lines after its number) or a table:
    {"table": [[cells], ...], "cols": [column offsets in mm]}. Returns the y (mm) where the notes end."""
    import fitz
    doc = fitz.open(pdf_in)
    sh = Sheet(doc[0])
    x0, y, x1, y1 = box[0], box[1], box[2], box[3]
    pitch = NOTE_MM * 1.35
    for note in notes:
        if isinstance(note, dict):           # columns as wide as their widest cell, 3.5 mm apart
            ncol = len(note["table"][0])
            widths = [max(sh.width(r[i]) for r in note["table"]) for i in range(ncol)]
            xs = [x0 + note.get("indent", 5.0)]
            for w in widths[:-1]:
                xs.append(xs[-1] + w + 3.5)
            if xs[-1] + widths[-1] > x1:
                raise SystemExit("the table is wider than the notes box")
            for row in note["table"]:
                y += pitch
                for cell, x in zip(row, xs):
                    sh.text((x, y), cell)
            continue
        head = note.split(" ", 1)[0] if note[:1].isdigit() and note.split(" ", 1)[0].endswith(".") else ""
        indent = sh.width(head + " ") if head else 0.0
        for i, line in enumerate(wrap(sh, note[len(head) + 1:] if head else note, x1 - x0 - indent)):
            y += pitch
            if i == 0 and head:
                sh.text((x0, y), head)
            sh.text((x0 + indent, y), line)
    if y + NOTE_MM * 0.35 > y1:
        raise SystemExit("the notes don't fit their box (they reach %.1f mm, the box ends at %.1f)" % (y, y1))
    doc.save(pdf_out)
    return y


# ------------------------------------------------------------------ letters for a tabulated sheet's sizes
def view_spans(page, x_max=None):
    """Every text span on the page left of x_max (sheet mm; the notes box's left edge by default):
    [(text, direction, span)]. The views' dimension values are real text in Fusion's PDF (ArialMT)."""
    k = page.rect.width / 420.0
    x_max = NOTES_BOX[0] if x_max is None else x_max
    out = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                if sp["text"].strip() and sp["bbox"][2] / k < x_max:
                    out.append((sp["text"].strip(), tuple(ln["dir"]), sp))
    return out


def letter_dims(pdf_in, pdf_out, letters):
    """A tabulated sheet's varying sizes as letters: each (value, letter) takes the one dimension value Fusion
    printed on the views (it must be there exactly once), removes its text from the page (a redaction; the
    dimension's lines and arrows stay) and writes the letter on the same baseline, centred where the value was,
    at its size and in its direction. Fails unless the re-read finds every letter and none of the values."""
    import fitz
    doc = fitz.open(pdf_in)
    page = doc[0]
    spans = view_spans(page)
    todo = []
    for value, letter in letters:
        hits = [(d, sp) for t, d, sp in spans if t == value]
        if len(hits) != 1:
            raise SystemExit("letters: %r is on the views %d times (want once)" % (value, len(hits)))
        todo.append((hits[0][0], hits[0][1], value, letter))
    for _d, sp, _v, _l in todo:
        page.add_redact_annot(fitz.Rect(sp["bbox"]), fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    font = fitz.Font(FONT)
    for d, sp, _v, letter in todo:
        size = sp["size"]
        w = font.text_length(letter, fontsize=size)
        x0, y0, x1, y1 = sp["bbox"]
        ox, oy = sp["origin"]
        if abs(d[0]) > 0.99:                      # left to right
            page.insert_text(fitz.Point((x0 + x1) / 2 - w / 2, oy), letter, fontsize=size, fontname=FONT)
        elif d[1] < -0.99:                        # bottom to top, as Fusion writes a vertical dimension's value
            page.insert_text(fitz.Point(ox, (y0 + y1) / 2 + w / 2), letter, fontsize=size, fontname=FONT,
                             rotate=90)
        else:
            raise SystemExit("letters: %r runs in direction %s, not handled" % (sp["text"], d))
    doc.save(pdf_out)
    doc.close()
    got = view_spans(fitz.open(pdf_out)[0])
    texts = [t for t, _d, _s in got]
    for d, _sp, value, letter in todo:
        if value in texts or [dd for t, dd, _s in got if t == letter] != [d]:
            raise SystemExit("letters: after the re-read %r is still there or %r isn't, once, in its direction"
                             % (value, letter))


# ------------------------------------------------------------------ hole tags at the holes (guideline 6.2)
def hole_circles(page, dia_on_sheet, tol=0.3):
    """Centres (sheet mm) of the circles of one diameter on the sheet: the solid ones Fusion writes as curves
    and the hidden ones it writes as short straight dashes (clustered, then fitted). [(x, y, solid)]."""
    import math
    k = page.rect.width / 420.0
    out, pts = [], []
    for d in page.get_drawings():
        r = d["rect"]
        kinds = {it[0] for it in d["items"]}
        if kinds == {"c"} and abs(r.width / k - dia_on_sheet) < tol and abs(r.height / k - dia_on_sheet) < tol:
            out.append(((r.x0 + r.x1) / 2 / k, (r.y0 + r.y1) / 2 / k, True))
        elif kinds == {"l"} and max(r.width, r.height) / k < 3.5 and abs((d.get("width") or 0) - W_THIN) < 0.05:
            for it in d["items"]:
                pts += [(it[1].x / k, it[1].y / k), (it[2].x / k, it[2].y / k)]
    groups = []                                  # dash ends within 3.5 mm of a group join it
    for p in pts:
        near = [g for g in groups if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 3.5 for q in g)]
        merged = [p] + [q for g in near for q in g]
        groups = [g for g in groups if g not in near] + [merged]
    for g in groups:
        for _round in range(3):           # fit, then drop ends that aren't on the circle (a leader's stub)
            if len(g) < 12:
                break
            cx, cy = sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)
            ds = sorted(math.hypot(p[0] - cx, p[1] - cy) for p in g)
            med = ds[len(ds) // 2]
            kept = [p for p in g if abs(math.hypot(p[0] - cx, p[1] - cy) - med) < 0.4]
            if len(kept) == len(g):
                break
            g = kept
        if len(g) < 12:
            continue
        cx, cy = sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)
        ds = [math.hypot(p[0] - cx, p[1] - cy) for p in g]
        mean = sum(ds) / len(ds)
        octants = {int((math.atan2(p[1] - cy, p[0] - cx) + math.pi) / (math.pi / 4)) % 8 for p in g}
        if abs(2 * mean - dia_on_sheet) < tol and max(abs(v - mean) for v in ds) < 0.25 and len(octants) == 8:
            out.append((cx, cy, False))           # dashes all round: a circle, not a slot's ends or a cone
    return sorted(out)


def add_tags(sheet, tags, circles):
    """Each tag: (pick, lines, (dx, dy)): pick chooses its circle from hole_circles' list; the text's first
    baseline is (dx, dy) mm from the circle's centre; a leader runs from the text to the circle's edge."""
    import math
    for pick, lines, (dx, dy) in tags:
        cx, cy, _solid = pick(circles)
        r = TAG_HOLE_R
        w = max(sheet.width(s) for s in lines)
        tx, ty = (cx + dx, cy + dy) if dx > 0 else (cx + dx - w, cy + dy)    # left of the hole: ends dx away
        for i, s in enumerate(lines):
            sheet.text((tx, ty + i * NOTE_MM * 1.35), s)
        # leader from the text block's side nearest the hole, at its first line's middle, to the circle's edge
        sx = tx - 1.0 if dx > 0 else tx + w + 1.0
        sy = ty - NOTE_MM * 0.36
        ang = math.atan2(sy - cy, sx - cx)
        edge = (cx + r * math.cos(ang), cy + r * math.sin(ang))
        sheet.line((sx, sy), edge)
        sheet.arrow(edge, (sx, sy))


# ------------------------------------------------------------------ the angled key from above (111212)
def view_b(sheet, origin, scale=2.0, a_deg=-24.14):
    """111212 from above, drawn from the model's sizes (the drawing's design is saved as 111211, so Fusion
    can't show this cut): the block 30 long on its centre line and 35 across, its stud face cut at angle A
    about the centre line; the hook stud holes square to that face; the fixing holes from below. Sheet x is
    the key's X (along the carrier toward the joint), sheet up is its Y. Returns the extent (x0, y0, x1, y1)."""
    import math
    L, W, d_hole = 30.0, 35.0, 5.04
    t = math.tan(math.radians(a_deg))
    x_top, x_bot = L + (W / 2) * t, L - (W / 2) * t          # the +Y and -Y ends of the stud face
    S = lambda p: (origin[0] + p[0] * scale, origin[1] - p[1] * scale)
    corners = [(0, -W / 2), (x_bot, -W / 2), (x_top, W / 2), (0, W / 2)]
    sheet.poly([S(p) for p in corners], width=W_THICK)
    # the hook stud holes: square to the stud face through its centre-line point C, hidden
    fx, fy = (x_top - x_bot), W                              # along the face, from its -Y end to its +Y end
    n = math.hypot(fx, fy)
    ux, uy = fx / n, fy / n                                  # along the face
    nx, ny = uy, -ux                                         # into the block (toward the back face)
    if nx > 0:
        nx, ny = -nx, -ny
    C = (L, 0.0)
    for side in (-1, 1):
        p0 = (C[0] + side * ux * d_hole / 2, C[1] + side * uy * d_hole / 2)
        tback = -p0[0] / nx                                  # to the back face, x = 0
        sheet.line(S(p0), S((p0[0] + nx * tback, p0[1] + ny * tback)), dashes=HIDDEN)
    out_end = (C[0] - nx * 8.0, C[1] - ny * 8.0)              # the axis, out past the face
    back = (C[0] + nx * (-C[0] / nx), C[1] + ny * (-C[0] / nx))
    sheet.line(S(back), S(out_end), dashes=CHAIN)
    # the fixing holes from below, hidden, with centre marks
    for y in (-7.0, 7.0):
        sheet.circle(S((10.5, y)), d_hole / 2 * scale, dashes=HIDDEN)
        sheet.line(S((10.5 - 4.5, y)), S((10.5 + 4.5, y)), dashes=CHAIN)
        sheet.line(S((10.5, y - 4.5)), S((10.5, y + 4.5)), dashes=CHAIN)
    # the long side (-Y), measured below; its end's extension line is also angle A's reference line
    y_dim = -W / 2 - 6.0
    sheet.line(S((0, -W / 2 - 1.0)), S((0, y_dim - 2.0)))
    sheet.line(S((x_bot, -W / 2 - 1.0)), S((x_bot, -W / 2 - 13.0)))
    sheet.line(S((0, y_dim)), S((x_bot, y_dim)))
    sheet.arrow(S((0, y_dim)), S((x_bot, y_dim)))
    sheet.arrow(S((x_bot, y_dim)), S((0, y_dim)))
    sheet.text(((S((0, 0))[0] + S((x_bot, 0))[0]) / 2, S((0, y_dim))[1] - 1.2), "%.2f" % x_bot, DIM_MM, "centre")
    # the short side (+Y), measured above
    y_dim2 = W / 2 + 6.0
    sheet.line(S((0, W / 2 + 1.0)), S((0, y_dim2 + 2.0)))
    sheet.line(S((x_top, W / 2 + 1.0)), S((x_top, y_dim2 + 2.0)))
    sheet.line(S((0, y_dim2)), S((x_top, y_dim2)))
    sheet.arrow(S((0, y_dim2)), S((x_top, y_dim2)))
    sheet.arrow(S((x_top, y_dim2)), S((0, y_dim2)))
    sheet.text(((S((0, 0))[0] + S((x_top, 0))[0]) / 2, S((0, y_dim2))[1] - 1.2), "%.2f" % x_top, DIM_MM, "centre")
    # angle A at the long end: between the extension line (straight down) and the face carried on past it
    R = 7.5                                                  # model mm, so 15 on the sheet
    face_dir = (-ux, -uy) if uy > 0 else (ux, uy)            # along the face, away from the block, -Y
    sheet.line(S((x_bot, -W / 2)), S((x_bot + face_dir[0] * (R + 3.0), -W / 2 + face_dir[1] * (R + 3.0))))
    a0 = math.atan2(-1.0, 0.0)                               # straight down (-Y)
    a1 = math.atan2(face_dir[1], face_dir[0])
    steps = 24
    arc = [S((x_bot + R * math.cos(a0 + (a1 - a0) * i / steps), -W / 2 + R * math.sin(a0 + (a1 - a0) * i / steps)))
           for i in range(steps + 1)]
    sheet.poly(arc, width=W_THIN, closed=False)
    sheet.arrow(arc[0], arc[2])
    sheet.arrow(arc[-1], arc[-3])
    mid = S((x_bot + (R + 1.5) * math.cos((a0 + a1) / 2), -W / 2 + (R + 1.5) * math.sin((a0 + a1) / 2)))
    sheet.text((mid[0] + 1.0, mid[1] + 1.5), "A = %.2f°" % abs(a_deg), DIM_MM)
    # the hole direction, named at the axis past the face
    tip = S(out_end)
    sheet.text((tip[0] + 1.5, tip[1] - 1.0), "H01, H02 SQUARE")
    sheet.text((tip[0] + 1.5, tip[1] - 1.0 + NOTE_MM * 1.35), "TO THE STUD FACE")
    xs = [S(p)[0] for p in corners] + [S(out_end)[0]]
    ys = [S(p)[1] for p in corners]
    top = S((0, y_dim2))[1] - 1.2 - DIM_MM * 0.72                            # the short side's text, its top
    return (min(xs), top, max(xs), max(ys) + 13.0 * scale)


def finish(part):
    import subprocess
    import fitz
    cfg = PARTS[part]
    raw = os.path.join(HERE, RAW_DIR, cfg["drawing"] + ".pdf")
    clean = os.path.join(HERE, RAW_DIR, cfg["drawing"] + "-clean.pdf")
    out = os.path.join(HERE, cfg["drawing"] + ".pdf")
    repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    # the shared step: clears "Created by" and fills the title block (number, revision, status, title)
    cmd = [sys.executable, os.path.join(repo, "tools/fusion/pdf_clear_field.py"), raw, clean]
    if cfg.get("title"):
        cmd += ["--title", cfg["title"]]
    subprocess.run(cmd, check=True)
    if cfg.get("letters"):                 # before the notes: the table repeats the values
        letter_dims(clean, clean + ".tmp", cfg["letters"])
        os.replace(clean + ".tmp", clean)
    end = add_notes(clean, out, cfg["notes"])
    doc = fitz.open(out)
    sheet = Sheet(doc[0])
    if cfg.get("tags"):
        circles = hole_circles(doc[0], cfg["tag_hole_dia"] * cfg["scale"])
        picked = [pick(circles) for pick, _l, _o in cfg["tags"]]
        if len({(round(c[0], 1), round(c[1], 1)) for c in picked}) != len(picked):
            raise SystemExit("hole tags: two tags picked the same hole: %s" % picked)
        add_tags(sheet, cfg["tags"], circles)
    if cfg.get("view_b"):
        vb = cfg["view_b"]
        x0, y0, x1, y1 = view_b(sheet, vb["origin"], cfg["scale"])
        if y0 - 4.0 - 2 * NOTE_MM < end:
            raise SystemExit("view B (from %.1f mm) runs into the notes (to %.1f mm)" % (y0, end))
        sheet.text((x0, y0 - 3.0), vb["label"], NOTE_MM)
    doc.save(out + ".tmp")
    doc.close()
    os.replace(out + ".tmp", out)
    page = fitz.open(out)[0]
    page.get_pixmap(dpi=110).save(os.path.join(HERE, cfg["drawing"] + "-render.png"))
    print("wrote %s and its render" % os.path.relpath(out, repo))


TAG_HOLE_R = 5.04                       # the tapped holes as drawn at 2:1 (Ø5.04 x 2 / 2), mm on the sheet

if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "finish":
    finish(sys.argv[2])
