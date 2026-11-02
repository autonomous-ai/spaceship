#!/usr/bin/env python3
"""The text of drawing 711001 (the power unit's folded enclosure body) and the step that finishes its PDF: the data
block, general notes and hole table from the part's own build parameters (electrical_parts_cad.py PARTS, evaluated
the way Fusion does), the hole tags beside the holes, and the read-back checks.

    python3 v2/02-Drawings/electrical/body_drawing_text.py --print
    python3 v2/02-Drawings/electrical/body_drawing_text.py --pdf RAW.pdf OUT.pdf

Fusion's drawing API can't put text on a sheet (custom tables stay blank, the title block fields come only from
properties; WALL's finding), so the text goes into the exported PDF here, as real text: the block above the title
block, and the tags H01-H08, each beside its hole in the view that shows the hole as a circle. --pdf:

1. checks the hole table against the body's STEP (every row is one STEP hole, every STEP hole one row), and each
   view's printed circles against the STEP's holes as that view shows them (body_views.py; the Fusion run wrote
   the views' outlines next to the raw PDF, RAW.views.json); a turned or misplaced view stops it;
2. stamps "Autonomous" under Created by, sets the PDF author and fills the title block (tools/fusion/
   pdf_clear_field.py, the shared finish step; D-140);
3. writes the block, puts each tag where it crosses no line and no other text, puts the two pitch dimensions
   of H05-H08 in brackets (they are for reference, the table gives the positions; D-143: no position is
   controlled twice), and marks view D: "D (turned 180°)" over it and arrow D under the FRONT, pointing up at the
   bottom (Fusion's Bottom is the view from below turned 180 degrees, and the API can't turn it: Reviewer 7's P1);
4. sets the creator to "Autonomous", keeps only the glyphs it uses of the font (the whole Arial Unicode made the
   sheet 15.3 MB; Reviewer 7, #173), saves, and re-reads the PDF: units, material, finish, tolerance, the table,
   every tag beside its circle, centre marks on every hole (Fusion's "Smart Centers" layer), view D's mark and
   arrow, Autonomous in Created by, author and creator, no maker line, and the drawing traps (tools/checks:
   letters, symbol, hidden lines, sizes printed twice).

Letter sizes are capital heights (ISO 3098), as the reviewers measure them: 2.5 mm for every line, 3.5 mm for the
headings. The font size is the capital height / 0.716, Arial's capital H measured by rendering it (716 px high at
1000 pt). A line too long for the block wraps at a space, indented under its first line.

Datums: A the bottom face, B the face on the FRONT view's left, C the back face. The side the body opens to comes
from its STEP (the back face at the low Z end: the returns fold toward +Z).
"""

import argparse
import json
import re
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("SPACESHIP_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAD = os.path.join(REPO, "v2", "01-CAD-Native", "electrical")
STEP = os.path.join(REPO, "v2", "03-Manufacturing", "electrical", "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_STEP.step")
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
PN = "711001"
SHEET_W, SHEET_H = 594.0, 420.0     # A2 landscape, mm
FRAME = (20.0, 10.0, 584.0, 410.0)  # Fusion's ISO frame: 20 mm in on the left, 10 on the other sides
TITLE = (404.0, 10.0, 584.0, 57.0)  # its title block, 180 x 47 in the frame's bottom right corner
BLOCK = (410.0, 62.0, 584.0, 315.0)   # x0, y0, x1, y1 in sheet mm (origin bottom left): above the title block, 12 under view D
PT = 72.0 / 25.4
CAP = 0.716                     # Arial (Unicode) capital H height / font size: rendered at 1000 pt, 716 px (confirmed)
LEAD = 1.9                      # baseline to baseline, in capital heights
BODY_H, HEAD_H = 2.5, 3.5       # capital heights, mm: notes and headings (ISO 3098, the reviewers' minimum)
CREATOR = "Autonomous"          # D-140: the drawing's creator, author and Created by
# the H05-H08 pitch dimensions (Fusion prints them, the finish step puts them in brackets as reference): pitch()
ROW_H = 5.5                     # table row, mm: 2.5 mm letters with 1.5 mm above and below
# hole table columns: heading, width mm (the note takes the rest)
COLUMNS = (("TAG", 10.0), ("FACE", 21.0), ("FROM B", 16.0), ("FROM A", 16.0), ("FROM C", 16.0), ("Ø THRU", 16.0),
           ("NOTE", None))
MARKS = "Smart Centers"         # Fusion's PDF layer of centre marks and centre lines (probe of 2026-11-01)
D_LABEL = "D (turned 180°)"     # over view D: Fusion's Bottom, the view from below turned 180 degrees
TAG_NEAR = 6.0                  # mm: the most a tag's box may stand off its circle (the real sheet: 5.1 on the lips)
TAG_GAP = 0.8                   # mm: a tag's whole text box (the font's ascent and descent) keeps this clear of
                                # every line, circle and other text


def _parts_cad():
    """electrical_parts_cad.py's PARTS without Fusion: stub the two adsk names it reads at import."""
    if CAD not in sys.path:
        sys.path.insert(0, CAD)
    if "adsk" not in sys.modules:
        adsk = types.ModuleType("adsk")
        core, fusion = types.ModuleType("adsk.core"), types.ModuleType("adsk.fusion")
        fusion.DimensionOrientations = types.SimpleNamespace(HorizontalDimensionOrientation=0,
                                                             VerticalDimensionOrientation=1)
        adsk.core, adsk.fusion = core, fusion
        sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.fusion": fusion})
    import electrical_parts_cad as C
    return C


def _views():
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import body_views as BV
    return BV


def params():
    """The body's own parameters, evaluated (mm), with each one's status."""
    C = _parts_cad()
    M = C.M
    pn, name, vn, stem, plist = C.PARTS["body"]
    vals, status = {}, {}
    for n, expr, _unit, st, _src in plist:
        vals[n] = M.evaluate(expr, dict(vals))
        status[n] = st
    return {"pn": pn, "name": name, "vn": vn, "stem": stem, "v": vals, "status": status, "rev": M.REV}


def hole_rows(p, zs=1):
    """(tag, face, from B, from A, from C, diameter, note) for every hole, H01... in the build's order; the distance
    along the hole's own axis is None (the hole goes through that wall)."""
    v = p["v"]
    w, h, d = v["w"], v["h"], v["d"]
    xb = (lambda x: x) if zs > 0 else (lambda x: w - x)     # from datum B, the FRONT view's left face
    side = "right side" if zs > 0 else "left side"           # the build's X = w wall, as the FRONT view shows it
    rows = [("H01", side, None, v["lead_z1"], d - v["lead_y"], v["hole_b"], "lead exit 1, Heyco 2836N bushing"),
            ("H02", side, None, v["lead_z2"], d - v["lead_y"], v["hole_b"], "lead exit 2, Heyco 2836N bushing"),
            ("H03", "top", xb(v["top_x"]), None, d - v["lead_y"], v["hole_b"], "light feed exit, Heyco 2836N bushing"),
            ("H04", "bottom", xb(v["mn_x"]), None, d - v["fr_y"], v["mn_d"], "mains cord entry, Heyco SB 625-7 bushing")]
    for i, (x, y) in enumerate(((v["clinch_x"], v["clinch_y"]), (w - v["clinch_x"], v["clinch_y"]),
                                (v["clinch_x"], h - v["clinch_y"]), (w - v["clinch_x"], h - v["clinch_y"]))):
        rows.append(("H%02d" % (5 + i), "front lip", xb(x), y, None, v["clinch_d"], "M4 clinch nut, PEM CLA-M4-1"))
    rows.append(("H09", "bottom", xb(v["estud_x"]), None, d - v["estud_y"], v["estud_d"], "M5 earth stud, PEM FHA-M5-12"))
    rows.append(("H10", "bottom", xb(v["ln_x"]), None, d - v["fr_y"], v["ln_d"], "LAN cable entry, Heyco SB 437-5 bushing"))
    fix = "M6 fixing to WALL's cross member"
    for tag, face, x in (("H11", "bottom", v["fixb_x1"]), ("H12", "bottom", v["fix_x2"]),
                         ("H13", "top", v["fixt_x1"]), ("H14", "top", v["fix_x2"])):
        rows.append((tag, face, xb(x), None, d - v["fr_y"], v["fix_d"], fix))
    rows.append(("H15", "back", xb(v["clamp_x"]), v["clamp_y"], None, v["estud_d"], "mains cord clamp stud, PEM FHA-M5-12"))
    return rows


def datum_distances(centre, box, zs):
    """(from B, from A, from C) of a model point, mm: B the FRONT view's left face, A the bottom, C the back."""
    x, y, z = centre
    return (x - box[0] if zs > 0 else box[3] - x, y - box[1], z - box[2] if zs > 0 else box[5] - z)


FACES = {"left side": (0, "low"), "right side": (0, "high"), "bottom": (1, "low"), "top": (1, "high"),
         "back": (2, "low"), "front lip": (2, "high")}


def check_rows(rows, box, holes, zs, tol=0.05):
    """Problems between the hole table and the STEP's holes: each row one hole (its two distances, its diameter and
    its face), each hole one row."""
    probs, used = [], set()
    size = (box[3] - box[0], box[4] - box[1], box[5] - box[2])
    for tag, face, b, a, c, dia, _note in rows:
        given = (b, a, c)
        through = [k for k in range(3) if given[k] is None]
        if len(through) != 1:
            probs.append("%s: %d distances given, not 2" % (tag, 3 - len(through)))
            continue
        k = through[0]
        fk, end = FACES[face]
        if fk != k:
            probs.append("%s: a hole in the %s goes along axis %d, not %d" % (tag, face, fk, k))
            continue
        at_face = 0.0 if end == "low" else size[k]
        # two walls facing each other can have holes on one line (the bottom's and the top's fixing holes): a row
        # takes the hole in its own wall
        hits, elsewhere = [], []
        for i, (centre, axis, hd) in enumerate(holes):
            dist = datum_distances(centre, box, zs)
            if abs(abs(axis[k]) - 1.0) > 1e-6 or abs(hd - dia) > tol:
                continue
            if all(abs(dist[j] - given[j]) <= tol for j in range(3) if j != k):
                (hits if abs(dist[k] - at_face) <= 3.0 else elsewhere).append((i, dist))
        if not hits and elsewhere:
            probs.append("%s: the STEP hole is not in the %s (%.1f along its axis)" % (tag, face, elsewhere[0][1][k]))
            continue
        if len(hits) != 1:
            probs.append("%s: %d STEP holes of Ø%.1f at %s in the %s" % (tag, len(hits), dia, given, face))
            continue
        if hits[0][0] in used:
            probs.append("%s: its STEP hole is another row's too" % tag)
        used.add(hits[0][0])
    for i, (centre, _axis, hd) in enumerate(holes):
        if i not in used:
            probs.append("a STEP hole of Ø%.1f at %s has no row" % (hd, tuple(round(v, 2) for v in centre)))
    return probs


def pitch(p=None):
    """The H05-H08 pitch as Fusion prints it: (across, up) between the clinch nuts' centres, from the parameters."""
    v = (p or params())["v"]
    return ("%g" % round(v["w"] - 2 * v["clinch_x"], 3), "%g" % round(v["h"] - 2 * v["clinch_y"], 3))


def fmt(x):
    return "—" if x is None else "%.1f" % x


def dia(x):
    """A hole's diameter as the table prints it: 19.1, 5.0, 5.94 (two decimals only when the second counts)."""
    t = "%.2f" % x
    return t[:-1] if t.endswith("0") else t


def lines(date="2026-11-01"):
    """[(text, size_mm, bold)] for the block's text: data and notes; the hole table follows them."""
    p = params()
    v = p["v"]
    return [("DRAWING DATA", HEAD_H, True),
            ("Part: %s %s" % (p["pn"], p["name"]), BODY_H, False),
            ("Tên (VN): %s" % p["vn"], BODY_H, False),
            ("Rev / status: %s / DRAFT, not for production" % p["rev"], BODY_H, False),
            ("UNITS: mm. Scale 1:2 (iso 1:5) on A2. ISO first-angle projection (ISO 5456-2), symbol below.", BODY_H, False),
            ("MATERIAL: aluminium 5052-H32, %.1f mm sheet (status: %s)." % (v["t"], p["status"]["t"].lower()), BODY_H, False),
            ("FINISH: mill finish, hidden inside the pod (D-79). Deburr every edge.", BODY_H, False),
            ("SOURCE: the 711001 %s STEP and CAD (same revision), %s." % (p["rev"], date), BODY_H, False),
            ("", 1.5, False),
            ("GENERAL NOTES", HEAD_H, True),
            ("1. GENERAL TOLERANCE: ISO 2768-m. Hole positions ±0.2; hole diameters +0.1/0, the PEM holes H05-H09 "
             "and H15 +0.08/0.", BODY_H, False),
            ("2. Outside size %.0f x %.0f x %.0f (datums A bottom, B left in the FRONT view, C back face); lips %.0f inward."
             % (v["w"], v["h"], v["d"], v["lip"]), BODY_H, False),
            ("3. Inside bend radius %.1f (= thickness), K-factor 0.44, square bend reliefs. Cut from the flat pattern"
             % v["t"], BODY_H, False),
            ("   711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DXF.dxf (same revision).", BODY_H, False),
            ("4. Fit the Heyco 2836N bushings in H01-H03 after folding, and the Heyco snap bushings SB 625-7 in H04 and "
             "SB 437-5 in H10 from inside the box, head inside. Press the PEM CLA-M4-1 clinch nuts into H05-H08 "
             "from inside the box, head inside, so the plate's screws pull them onto the lips (PEM CL-18). Press the "
             "FHA-M5-12 studs into H09 (earth) and H15 (the cord's clamp) head outside, with PEM's anvil for sheet up to 1.5 mm (FH-18). The order "
             "with the folding is the factory's, with its tooling.", BODY_H, False),
            ("5. H11-H14 fix the unit to WALL's two cross members in B2 (IF-12): an M6 screw with a washer through "
             "each, from inside the box, into the member's rivnut. H09's place is an assumption until the unit's "
             "inside layout (the factory's).", BODY_H, False),
            ("6. (%s) and (%s): the H05-H08 pitch, for reference; the hole table gives the positions." % pitch(p),
             BODY_H, False),
            ("7. View D: the bottom, seen in the direction of arrow D (from below), drawn turned 180°: datum B is on its "
             "right, C at its top.", BODY_H, False),
            ("", 1.5, False),
            ("HOLE TABLE (positions from the datums A, B, C)", HEAD_H, True)]


def table_cells(rows):
    """The table's text: a heading row, then one row per hole."""
    out = [[c for c, _w in COLUMNS]]
    for tag, face, b, a, c, d, note in rows:
        out.append([tag, face, fmt(b), fmt(a), fmt(c), "Ø" + dia(d), note])
    return out


def required_missing(text):
    """The drawing check's text rules for a part drawing (tools/checks/c_drawings.py), read the same way."""
    import re
    up = text.upper()
    miss = []
    if not re.search(r"\bUNITS?\s*[:=]?\s*MM\b", up):
        miss.append("units")
    if not re.search(r"MATERIAL", up) or not re.search(r"ALUMIN|\d{4}", up):
        miss.append("material")
    if not re.search(r"FINISH|ANODI|MILL FINISH", up):
        miss.append("finish")
    if not re.search(r"ISO\s*2768|TOLERANCE", up):
        miss.append("tolerance")
    if not re.search(r"\bH\d{2}\b", up):
        miss.append("hole tags")
    return miss


def font_size(h):
    """PDF font size (mm) for a capital height h (mm)."""
    return h / CAP


def wrap(rows, width, font):
    """Rows whose text fits `width` (mm): a longer line breaks at spaces, the rest indented 3 spaces."""
    out = []
    for text, h, bold in rows:
        fit = lambda t: font.text_length(t, fontsize=font_size(h)) <= width      # noqa: E731
        if not text or fit(text):
            out.append((text, h, bold))
            continue
        lead = "   " if not text.startswith(" ") else text[:len(text) - len(text.lstrip(" "))] + "   "
        words, line = text.split(" "), ""
        for wd in words:
            trial = (line + " " + wd) if line else wd
            if line and not fit(trial):
                out.append((line, h, bold))
                trial = lead + wd
            line = trial
        if not fit(line):
            raise RuntimeError("a word is wider than the block: %r" % line[:60])
        out.append((line, h, bold))
    return out


class Sheet:
    """Sheet mm (origin bottom left) on a PDF page of an A2 sheet (origin top left, points)."""

    def __init__(self, page):
        self.page = page
        self.k = page.rect.height / (SHEET_H * PT)       # the page may not be exactly A2 in points

    def pt(self, x, y):
        import fitz
        return fitz.Point(x * PT * self.k, (SHEET_H - y) * PT * self.k)

    def mm(self, p):
        return (p.x / (PT * self.k), SHEET_H - p.y / (PT * self.k))

    def rect_mm(self, r):
        """(x0, y0, x1, y1) sheet mm of a PDF rect."""
        (x0, y1), (x1, y0) = self.mm(r.tl), self.mm(r.br)
        return (x0, y0, x1, y1)

    def text(self, x, y, s, h, rotate=0):
        """Text with its baseline starting at (x, y) sheet mm, capital height h."""
        self.page.insert_text(self.pt(x, y), s, fontname="AU", fontsize=font_size(h) * PT * self.k, rotate=rotate)

    def line(self, x0, y0, x1, y1, width=0.25):
        self.page.draw_line(self.pt(x0, y0), self.pt(x1, y1), color=(0, 0, 0), width=width * PT * self.k)


def write_block(page, rows, table, block=BLOCK):
    """Rows of text, top down, inside the block, then the hole table under them. Sizes are capital heights; long
    lines wrap; a table cell that doesn't fit its column stops the run. Returns the rows as written."""
    import fitz
    page.insert_font(fontname="AU", fontfile=FONT)
    sh = Sheet(page)
    x0, y0, x1, y1 = block
    font = fitz.Font(fontfile=FONT)
    rows = wrap(rows, x1 - x0 - 4.0, font)
    y = y1 - 4.0
    for text, h, _bold in rows:
        y -= h                                          # the line's capital top to its baseline
        if y < y0:
            raise RuntimeError("the text block overflows its space; shorten the notes")
        if text:
            sh.text(x0, y, text, h)
        y -= h * (LEAD - 1.0)
    # the table: its top a little under the heading's baseline
    widths = [w for _c, w in COLUMNS[:-1]]
    widths.append(x1 - x0 - 4.0 - sum(widths))
    top = y + BODY_H * (LEAD - 1.0) - 1.5
    bottom = top - ROW_H * len(table)
    if bottom < y0:
        raise RuntimeError("the hole table overflows the block; shorten the notes")
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)
    for i, cells in enumerate(table):
        base = top - ROW_H * (i + 1) + 1.5
        for j, cell in enumerate(cells):
            if font.text_length(cell, fontsize=font_size(BODY_H)) > widths[j] - 2.0:
                raise RuntimeError("table cell %r is wider than its column (%.0f mm)" % (cell, widths[j]))
            sh.text(xs[j] + 1.0, base, cell, BODY_H)
    for i in range(len(table) + 1):
        sh.line(xs[0], top - ROW_H * i, xs[-1], top - ROW_H * i)
    for x in xs:
        sh.line(x, top, x, bottom)
    return rows


# ---------------------------------------------------------------- reading the raw PDF


def geometry(page):
    """(segments, circles, text boxes) on the page, sheet mm: segments (x0, y0, x1, y1, layer), circles
    (cx, cy, r, layer) from closed paths of 4 or more curves with a square box (a full turn: Fusion's bend-corner
    arcs are single open curves), text boxes (x0, y0, x1, y1, text)."""
    sh = Sheet(page)
    segs, circles, texts = [], [], []
    for d in page.get_drawings():
        items = d["items"]
        layer = d.get("layer") or ""
        if items and all(it[0] == "c" for it in items) and len(items) >= 4 and \
                abs(items[0][1].x - items[-1][4].x) < 0.05 and abs(items[0][1].y - items[-1][4].y) < 0.05:
            x0, y0, x1, y1 = sh.rect_mm(d["rect"])
            w, h = x1 - x0, y1 - y0
            if w > 0 and abs(w - h) <= 0.02 * w + 0.02:
                circles.append(((x0 + x1) / 2, (y0 + y1) / 2, (w + h) / 4, layer))
                continue
        for it in items:
            if it[0] == "l":
                segs.append(sh.mm(it[1]) + sh.mm(it[2]) + (layer,))
            elif it[0] == "re":
                x0, y0, x1, y1 = sh.rect_mm(it[1])
                segs += [(x0, y0, x1, y0, layer), (x1, y0, x1, y1, layer), (x1, y1, x0, y1, layer),
                         (x0, y1, x0, y0, layer)]
            elif it[0] == "qu":
                q = [sh.mm(p) for p in (it[1].ul, it[1].ur, it[1].lr, it[1].ll)]
                segs += [q[i] + q[(i + 1) % 4] + (layer,) for i in range(4)]
            elif it[0] == "c":
                pts = [sh.mm(p) for p in it[1:5]]
                segs += [pts[i] + pts[i + 1] + (layer,) for i in range(3)]   # the control polygon holds the curve
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                if sp["text"].strip():
                    import fitz
                    texts.append(sh.rect_mm(fitz.Rect(sp["bbox"])) + (sp["text"].strip(),))
    return segs, circles, texts


def _seg_hits_box(s, b):
    """Does segment s (x0, y0, x1, y1) touch box b (x0, y0, x1, y1)?"""
    (ax, ay, bx, by), (x0, y0, x1, y1) = s[:4], b
    if max(ax, bx) < x0 or min(ax, bx) > x1 or max(ay, by) < y0 or min(ay, by) > y1:
        return False
    if x0 <= ax <= x1 and y0 <= ay <= y1:
        return True
    dx, dy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, ax - x0), (dx, x1 - ax), (-dy, ay - y0), (dy, y1 - ay)):    # Liang-Barsky
        if abs(p) < 1e-12:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


def _boxes_touch(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def tag_spot(cx, cy, r, w, h, segs, circles, texts, keep_out, gap=TAG_GAP):
    """Where a tag's text box w x h (sheet mm) goes beside its circle: the first spot around it, nearest first,
    whose box (grown by `gap`) touches no segment, no circle, no text and no keep-out box. Returns the box's
    lower-left corner or None."""
    k = 0.7071
    for dist in (0.8, 1.5, 2.5, 3.5, 5.0):
        rr = r + dist
        for ux, uy, ax, ay in ((k, k, 0, 0), (-k, k, 1, 0), (k, -k, 0, 1), (-k, -k, 1, 1),
                               (1, 0, 0, 0.5), (-1, 0, 1, 0.5), (0, 1, 0.5, 0), (0, -1, 0.5, 1)):
            px, py = cx + ux * rr, cy + uy * rr
            x0, y0 = px - ax * w, py - ay * h
            box = (x0 - gap, y0 - gap, x0 + w + gap, y0 + h + gap)
            if any(_seg_hits_box(s, box) for s in segs):
                continue
            if any(_boxes_touch(box, (c[0] - c[2], c[1] - c[2], c[0] + c[2], c[1] + c[2])) for c in circles):
                continue
            if any(_boxes_touch(box, t[:4]) for t in texts) or any(_boxes_touch(box, z) for z in keep_out):
                continue
            if not (FRAME[0] < box[0] and FRAME[1] < box[1] and box[2] < FRAME[2] and box[3] < FRAME[3]):
                continue
            return x0, y0
    return None


def hole_circles(circles, layers=("Visible", "")):
    """The part's circles: Fusion prints them on its "Visible" layer or on none (the probe's sheet had both), never
    on a named sketch's or symbol's layer."""
    return [c for c in circles if c[3] in layers]


def view_problems(views_json, circles, box, holes, zs):
    """Each view's printed circles (in its outline, grown 1 mm) against the STEP's holes as the view shows them;
    returns (problems, [(view, tag-less circle (x, y, r))] for the circles found)."""
    BV = _views()
    probs, found = [], []
    for name, rec in sorted(views_json["views"].items()):
        if name == "iso":
            continue
        ex = rec["extent"]
        got = [(x, y, r) for x, y, r, _l in circles if ex[0] - 1 <= x <= ex[2] + 1 and ex[1] - 1 <= y <= ex[3] + 1]
        probs += BV.check_view(name, box, holes, ex, views_json["scale"], zs, got)
        found += [(name, c) for c in got]
    return probs, found


def tags_for(rows, views_json, box, holes, zs):
    """[(tag, view, x, y, r)]: each hole's circle on the sheet, in the view that shows it as a circle."""
    BV = _views()
    out = []
    size = (box[3] - box[0], box[4] - box[1], box[5] - box[2])
    for tag, face, b, a, c, dia, _note in rows:
        k = [b, a, c].index(None)
        at_face = 0.0 if FACES[face][1] == "low" else size[k]   # the row's own wall (two walls can share a line)
        for centre, axis, hd in holes:
            dist = datum_distances(centre, box, zs)
            if abs(abs(axis[k]) - 1.0) < 1e-6 and abs(hd - dia) <= 0.05 and abs(dist[k] - at_face) <= 3.0 and all(
                    abs(dist[j] - [b, a, c][j]) <= 0.05 for j in range(3) if j != k):
                for name, rec in views_json["views"].items():
                    if name != "iso" and (centre, axis, hd) in BV.seen(name, box, holes, zs, opening=True):
                        x, y = BV.on_sheet(name, box, centre, rec["extent"], views_json["scale"], zs)
                        out.append((tag, name, x, y, hd / 2.0 * views_json["scale"]))
    return out


def reference_dims(page, values=None):
    """Put the pitch dimensions' values in brackets: each value is found once, its text taken out (lines kept) and
    written again as (value), centred where it was, in its direction. Returns the number done."""
    import fitz
    hits = {v: [] for v in (values or pitch())}
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                if sp["text"].strip() in hits:
                    hits[sp["text"].strip()].append((sp, ln["dir"]))
    for v, found in hits.items():
        if len(found) != 1:
            raise RuntimeError("the pitch dimension %s is printed %d times, not once" % (v, len(found)))
    for v, ((sp, d),) in hits.items():
        # only the glyphs' own band: Fusion sets the pitch's text so close under the width's (2026-11-01, 12:10 UTC)
        # that their text boxes overlap, and a redaction of the whole box took the width's 296 with it
        bb = fitz.Rect(sp["bbox"])
        if abs(d[0]) >= abs(d[1]):
            m = bb.height * 0.3
            band = fitz.Rect(bb.x0, bb.y0 + m, bb.x1, bb.y1 - m)
        else:
            m = bb.width * 0.3
            band = fitz.Rect(bb.x0 + m, bb.y0, bb.x1 - m, bb.y1)
        page.add_redact_annot(band)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    font = fitz.Font(fontfile=FONT)
    page.insert_font(fontname="AU", fontfile=FONT)
    for v, ((sp, d),) in hits.items():
        text = "(%s)" % v
        size = sp["size"]
        length = font.text_length(text, fontsize=size)
        bb = fitz.Rect(sp["bbox"])
        ox, oy = sp["origin"]
        if abs(d[0]) >= abs(d[1]):          # left to right
            page.insert_text(fitz.Point((bb.x0 + bb.x1) / 2 - length / 2, oy), text, fontname="AU", fontsize=size)
        else:                               # bottom to top: rotated a quarter turn
            page.insert_text(fitz.Point(ox, (bb.y0 + bb.y1) / 2 + length / 2), text, fontname="AU", fontsize=size,
                             rotate=90)
    return len(hits)


def centre_mark_problems(circles, segs, tol=0.15, layer=MARKS):
    """Each hole circle needs its centre mark on Fusion's mark layer: a cross at its centre, and the centre lines
    reaching past the circle on both sides, across and up (Fusion draws the cross and dashes beyond the circle)."""
    probs = []
    marks = [s for s in segs if s[4] == layer]
    for x, y, r in circles:
        hz = [s for s in marks if abs(s[1] - y) <= tol and abs(s[3] - y) <= tol]
        vt = [s for s in marks if abs(s[0] - x) <= tol and abs(s[2] - x) <= tol]
        cross = any(min(s[0], s[2]) <= x <= max(s[0], s[2]) for s in hz) and \
            any(min(s[1], s[3]) <= y <= max(s[1], s[3]) for s in vt)
        past = (min([min(s[0], s[2]) for s in hz] or [x]) < x - r and max([max(s[0], s[2]) for s in hz] or [x]) > x + r
                and min([min(s[1], s[3]) for s in vt] or [y]) < y - r and max([max(s[1], s[3]) for s in vt] or [y]) > y + r)
        if not (cross and past):
            probs.append("no centre mark on the circle r %.2f at (%.2f, %.2f)" % (r, x, y))
    return probs


def view_d_marks(page, views_json, segs, texts):
    """Arrow D under the FRONT, pointing up at the bottom, with its letter; "D (turned 180°)" over view D. Each
    is placed where it touches no line and no text; returns their boxes (sheet mm) for the read-back."""
    import fitz
    sh = Sheet(page)
    font = fitz.Font(fontfile=FONT)
    size = font_size(HEAD_H)
    asc, desc = font.ascender * size, -font.descender * size
    fe, de = views_json["views"]["front"]["extent"], views_json["views"]["d"]["extent"]
    x = (fe[0] + fe[2]) / 2
    tail, tip = fe[1] - 15.0, fe[1] - 2.0
    wd = font.text_length("D", fontsize=size)
    arrow_box = (x - 1.0, tail, x + 1.8 + wd, tip)
    lw = font.text_length(D_LABEL, fontsize=size)
    lx, ly = (de[0] + de[2]) / 2 - lw / 2, de[3] + 3.0
    label_box = (lx, ly - desc, lx + lw, ly + asc)
    for what, box in (("arrow D", arrow_box), ("view D's mark", label_box)):
        grown = (box[0] - TAG_GAP, box[1] - TAG_GAP, box[2] + TAG_GAP, box[3] + TAG_GAP)
        hits = [s for s in segs if _seg_hits_box(s, grown)] + [t for t in texts if _boxes_touch(grown, t[:4])]
        if hits:
            raise SystemExit("%s would touch %s" % (what, hits[0]))
    shaft_top = tip - 3.0                                    # the head: 3 long, 15 degrees each side (ISO 128)
    sh.line(x, tail, x, shaft_top, width=0.35)
    page.draw_polyline([sh.pt(x, tip), sh.pt(x - 0.8, shaft_top), sh.pt(x + 0.8, shaft_top), sh.pt(x, tip)],
                       color=(0, 0, 0), fill=(0, 0, 0), width=0.1 * PT * sh.k, closePath=True)
    sh.text(x + 1.8, tail + 1.0, "D", HEAD_H)
    sh.text(lx, ly, D_LABEL, HEAD_H)
    return arrow_box, label_box



def _ptb():
    """tools/fusion/pdf_title_block.py, this checkout's copy (the shared title block reader)."""
    d = os.path.join(REPO, "tools", "fusion")
    if d not in sys.path:
        sys.path.insert(0, d)
    import pdf_title_block
    return pdf_title_block


def pdf_title():
    """The PDF's title: the part's number, revision and name from the master BOM (Reviewer 7 on #173: not
    Fusion's 'Sheet1'), as the other ELECTRICAL drawings carry it."""
    name, _status = _ptb().bom_row(PN)
    if not name:
        raise RuntimeError("%s has no name in the master BOM" % PN)
    return "%s P01 %s" % (PN, name)


def iso_date(page):
    """Fusion prints the drawing's date as d/m/yy on the Created by line (1/11/26); write it as 2026-11-01, the
    form the reviewers asked for (#173). Only the date's glyph band is taken out (the lines stay), and the new date
    goes on the same baseline at the same size, ending where the old one ended and kept 4 pt clear of the value on
    its left. Returns the ISO date."""
    import fitz
    found = _ptb().created_by(page)
    if found is None or found[2] is None:
        raise RuntimeError("no date on the title block's Created by line")
    _lab, left, word = found
    day, month, year = (int(v) for v in word[4].split("/"))
    iso = "%04d-%02d-%02d" % (year + 2000 if year < 100 else year, month, day)
    box = fitz.Rect(word[:4])
    spans = [sp for blk in page.get_text("dict")["blocks"] for ln in blk.get("lines", []) for sp in ln["spans"]
             if sp["text"].strip() == word[4] and fitz.Rect(sp["bbox"]).intersects(box)]
    if len(spans) != 1:
        raise RuntimeError("the date %s is printed %d times on its line, not once" % (word[4], len(spans)))
    sp = spans[0]
    m = box.height * 0.3
    page.add_redact_annot(fitz.Rect(box.x0, box.y0 + m, box.x1, box.y1 - m))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    font = fitz.Font(fontfile=FONT)
    page.insert_font(fontname="AU", fontfile=FONT)
    size = sp["size"]
    floor = max([w[2] for w in left] + [box.x0 - 200]) + 4.0
    least = font_size(BODY_H) * PT * Sheet(page).k            # 2.5 mm capitals at the least
    while size > least and box.x1 - font.text_length(iso, fontsize=size) < floor:
        size -= 0.1
    x0 = box.x1 - font.text_length(iso, fontsize=size)
    if x0 < floor:
        raise RuntimeError("the date %s doesn't fit its cell beside the Created by value" % iso)
    page.insert_text(fitz.Point(x0, sp["origin"][1]), iso, fontname="AU", fontsize=size)
    return iso

def clear_field(raw, out):
    """The shared finish step: Autonomous under Created by and as the PDF's author, the title block filled."""
    r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "fusion", "pdf_clear_field.py"), raw, out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("pdf_clear_field failed: %s" % (r.stdout + r.stderr)[-400:])
    print(r.stdout.strip())


def finish_pdf(raw, out, views_path=None, step=STEP):
    import fitz
    BV = _views()
    box, holes = BV.step_body(step, REPO)
    zs = BV.opens_to(box)
    views_json = json.load(open(views_path or raw[:-4] + ".views.json"))
    rows = hole_rows(params(), zs)
    probs = check_rows(rows, box, holes, zs)
    src = fitz.open(raw)
    segs, circles, texts = geometry(src[0])
    src.close()
    vp, _found = view_problems(views_json, hole_circles(circles), box, holes, zs)
    probs += vp
    if probs:
        raise SystemExit("711001 drawing stopped before the text went in:\n  " + "\n  ".join(probs))
    tmp = out + ".stamped.pdf"
    clear_field(raw, tmp)
    doc = fitz.open(tmp)
    page = doc[0]
    reference_dims(page)
    date = iso_date(page)                      # the source line carries the drawing's own date
    write_block(page, lines(date), table_cells(rows))
    segs, circles, texts = geometry(page)
    view_d_marks(page, views_json, segs, texts)
    # the tags, after everything else, so they keep clear of it all
    segs, circles, texts = geometry(page)
    font = fitz.Font(fontfile=FONT)
    size = font_size(BODY_H)
    asc, desc = font.ascender * size, -font.descender * size     # the text box a reader's tools see, mm
    for tag, view, x, y, r in tags_for(rows, views_json, box, holes, zs):
        w = font.text_length(tag, fontsize=size)
        spot = tag_spot(x, y, r, w, asc + desc, segs, circles, texts, [BLOCK, TITLE])
        if spot is None:
            raise SystemExit("no free place for the %s tag beside its circle in the %s view" % (tag, view))
        Sheet(page).text(spot[0], spot[1] + desc, tag, BODY_H)          # the baseline above the box's foot
        texts.append((spot[0], spot[1], spot[0] + w, spot[1] + asc + desc, tag))
    meta = dict(doc.metadata or {})
    doc.set_metadata({k: v for k, v in {"title": pdf_title(), "author": CREATOR, "creator": CREATOR,
                                        "producer": meta.get("producer"), "creationDate": meta.get("creationDate"),
                                        "modDate": meta.get("modDate")}.items() if v})
    doc.subset_fonts()
    doc.save(out, garbage=4, deflate=True)
    doc.close()
    os.remove(tmp)
    probs = read_back(out, views_json, box, holes, zs, rows)
    if probs:
        raise SystemExit("the finished PDF fails its read-back:\n  " + "\n  ".join(probs))
    print("wrote %s (%.2f MB): Autonomous as creator, text block and hole table, %d tags, pitch in brackets; "
          "read back clean" % (os.path.relpath(out, REPO), os.path.getsize(out) / 1e6, len(rows)))


def read_back(path, views_json, box, holes, zs, rows):
    """Everything the finished PDF must show, read from it alone."""
    import fitz
    probs = []
    doc = fitz.open(path)
    page = doc[0]
    text = page.get_text()
    probs += ["lacks %s" % m for m in required_missing(text)]
    segs, circles, texts = geometry(page)
    parts = hole_circles(circles)
    vp, found = view_problems(views_json, parts, box, holes, zs)
    probs += vp
    probs += centre_mark_problems([c for _v, c in found], segs)
    fe, de = views_json["views"]["front"]["extent"], views_json["views"]["d"]["extent"]
    lab = [t for t in texts if t[4] == D_LABEL and de[0] <= (t[0] + t[2]) / 2 <= de[2] and 0 < t[1] - de[3] < 8]
    letter = [t for t in texts if t[4] == "D" and fe[0] < t[0] < fe[2] and fe[1] - 20 < t[1] < fe[1]]
    if len(lab) != 1 or len(letter) != 1:
        probs.append("view D's mark over it (%d) or arrow D's letter under the FRONT (%d) is not there once" % (
            len(lab), len(letter)))
    words = [t[4] for t in texts]
    for cells in table_cells(rows)[1:]:
        if not all(c in words for c in cells[:2] + cells[5:6]):
            probs.append("the table row of %s doesn't read back" % cells[0])
    for tag, view, x, y, r in tags_for(rows, views_json, box, holes, zs):
        near = [t for t in texts if t[4] == tag and not _boxes_touch(t[:4], BLOCK)]
        if len(near) != 1:
            probs.append("%s: %d tags outside the block" % (tag, len(near)))
        else:                       # the gap from the circle to the tag's nearest point
            bx = min(max(x, near[0][0]), near[0][2])
            by = min(max(y, near[0][1]), near[0][3])
            gap = ((bx - x) ** 2 + (by - y) ** 2) ** 0.5 - r
            if gap > TAG_NEAR:
                probs.append("%s: its tag is %.1f mm from its circle in the %s view" % (tag, gap, view))
    for v in pitch():
        if words.count("(%s)" % v) != 1 or v in words:
            probs.append("the pitch %s isn't printed once as (%s)" % (v, v))
    pv = params()["v"]
    sizes = ("%g" % pv["w"], "%g" % pv["h"], "%g" % pv["d"])
    for v in sizes:                                                 # the overall sizes, each once, still there
        if words.count(v) != 1:
            probs.append("the overall size %s is printed %d times, not once" % (v, words.count(v)))
    # no line through a dimension's value: its glyphs' band (the inner 60 % across the text) touches no segment
    for x0, y0, x1, y1, t in texts:
        if t in sizes or t in ["(%s)" % v for v in pitch()]:
            if (x1 - x0) >= (y1 - y0):
                m = (y1 - y0) * 0.2
                band = (x0, y0 + m, x1, y1 - m)
            else:
                m = (x1 - x0) * 0.2
                band = (x0 + m, y0, x1 - m, y1)
            hit = [sg for sg in segs if _seg_hits_box(sg, band)]
            if hit:
                probs.append("a line runs through the dimension %s (%s)" % (t, tuple(round(c, 1) for c in hit[0][:4])))
    meta = doc.metadata or {}
    if meta.get("author") != CREATOR or meta.get("creator") != CREATOR:
        probs.append("author %r, creator %r" % (meta.get("author"), meta.get("creator")))
    if meta.get("title") != pdf_title():
        probs.append("the PDF's title is %r, not %r" % (meta.get("title"), pdf_title()))
    found = _ptb().created_by(page)
    if found is None or found[2] is not None:
        probs.append("Fusion's d/m/yy date is still on the Created by line")
    elif not any(re.fullmatch(r"20\d\d-\d\d-\d\d", w[4]) for w in found[1]):
        probs.append("the Created by line has no date written as 2026-11-01")
    xmp = doc.get_xml_metadata() or ""
    if "creator" in xmp.lower() and CREATOR not in xmp:
        probs.append("its XMP names a creator other than %s" % CREATOR)
    fonts = [f for f in doc.get_page_fonts(0) if f[1] in ("ttf", "Type0", "TrueType", "cff")]
    big = [f[3] for f in fonts if "AU" in f[4] and "+" not in f[3]]
    if big:
        probs.append("fonts embedded whole: %s" % big)
    doc.close()
    if os.path.getsize(path) > 1_000_000:
        probs.append("the PDF is %.1f MB" % (os.path.getsize(path) / 1e6))
    sys.path.insert(0, os.path.join(REPO, "tools", "checks"))
    import c_drawings
    import pdf_traps
    p1, hits = c_drawings.drawing_people(path, [])
    probs += p1 + ["a name: %s" % (h,) for h in hits]
    probs += ["%s %s: %s" % (rule, sev, msg) for rule, sev, msg, _fix in pdf_traps.findings(path)]
    return probs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--pdf", nargs=2, metavar=("RAW", "OUT"))
    ap.add_argument("--views", help="the views' outlines the Fusion run wrote (default RAW.views.json)")
    a = ap.parse_args(argv)
    if a.pdf:
        finish_pdf(a.pdf[0], a.pdf[1], a.views)
    else:
        BV = _views()
        box, holes = BV.step_body(STEP, REPO)
        zs = BV.opens_to(box)
        rows = hole_rows(params(), zs)
        for text, _s, bold in lines():
            print(("** %s" % text) if bold else text)
        for cells in table_cells(rows):
            print(" | ".join(cells))
        probs = check_rows(rows, box, holes, zs)
        print("table against the STEP: %s" % ("; ".join(probs) if probs else "every row one STEP hole, every hole one row"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
