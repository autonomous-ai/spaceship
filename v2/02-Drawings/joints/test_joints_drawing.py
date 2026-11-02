#!/usr/bin/env python3
"""Offline test of joints_drawing.py: no Fusion needed.

    python3 v2/02-Drawings/joints/test_joints_drawing.py

1. Lays out each view's edges in sheet mm the way Fusion draws a base view (front: X right,
   Z up; top: X right, Y up; right: Y right, Z up; README), runs plan_dims and checks that
   every dimension measures the model size it is meant to (distance / scale).
2. Writes the notes into a blank A3 PDF with add_notes and reads them back with the same
   patterns the mechanical check uses for a drawing's content (tools/checks/c_drawings.py):
   units, material, finish, tolerance, hole tags, and TABULATED with every part number.
"""
import importlib.util
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("joints_drawing", os.path.join(HERE, "joints_drawing.py"))
JD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(JD)

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def view_geometry(part, view, scale, centre):
    """(lines, circles) in sheet mm for a view, from the model's edges (mm)."""
    cx, cy = centre
    segs, circs = [], []
    if part == "spigot" and view == "front":           # X right, Z up; origin on the shoulder
        r_pin, r_stud, top, ch = 4.0, 3.0, 7.24, 1.0
        segs += [(-r_pin, 0, -r_pin, top - ch), (r_pin, 0, r_pin, top - ch),
                 (-r_pin, top - ch, -r_pin + ch, top), (r_pin, top - ch, r_pin - ch, top),
                 (-r_pin + ch, top, r_pin - ch, top),
                 (-r_pin, 0, -r_stud, 0), (r_stud, 0, r_pin, 0),
                 (-r_stud, -8, -r_stud, 0), (r_stud, -8, r_stud, 0), (-r_stud, -8, r_stud, -8),
                 (-2.31, top - 3.5, 2.31, top - 3.5)]  # hidden: the socket's bottom
        zc = (top - 8.0) / 2
        off = (0.0, zc)
    elif part == "spigot" and view == "top":           # X right, Y up
        circs += [(0, 0, 4.0), (0, 0, 3.0)]
        r = 4.0 / 3 ** 0.5
        import math
        v = [(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))) for k in range(6)]
        segs += [(v[k][0], v[k][1], v[(k + 1) % 6][0], v[(k + 1) % 6][1]) for k in range(6)]
        off = (0.0, 0.0)
    elif part == "keys" and view == "front":           # X right, Z up: 30 x 75
        segs += [(0, 0, 30, 0), (30, 0, 30, 75), (30, 75, 0, 75), (0, 75, 0, 0)]
        for z in (26, 60):                              # hidden: stud holes along X
            segs += [(0, z - 2.5, 30, z - 2.5), (0, z + 2.5, 30, z + 2.5)]
        segs += [(8.0, 0, 8.0, 18), (13.0, 0, 13.0, 18)]  # hidden: fixing holes
        off = (15.0, 37.5)
    elif part == "keys" and view == "right":           # Y right, Z up: the stud face 35 x 75
        segs += [(-17.5, 0, 17.5, 0), (17.5, 0, 17.5, 75), (17.5, 75, -17.5, 75), (-17.5, 75, -17.5, 0)]
        circs += [(0, 26, 2.5), (0, 60, 2.5)]
        off = (0.0, 37.5)
    elif part == "keys" and view == "top":             # X right, Y up: 30 x 35
        segs += [(0, -17.5, 30, -17.5), (30, -17.5, 30, 17.5), (30, 17.5, 0, 17.5), (0, 17.5, 0, -17.5)]
        segs += [(0, -2.5, 30, -2.5), (0, 2.5, 30, 2.5)]  # hidden: stud holes seen from above
        circs += FIXING_HOLES                              # hidden: fixing holes (111211's, D-144)
        off = (15.0, 0.0)
    to = lambda x, y: (cx + (x - off[0]) * scale, cy + (y - off[1]) * scale)
    lines = [to(a, b) + to(c, d) for a, b, c, d in segs]
    circles = [to(x, y) + (r * scale,) for x, y, r in circs]
    return lines, circles


FIXING_HOLES = [(17.8, -6.0, 2.5), (10.5, 6.0, 2.5)]


def measured(kind, a, b, place, scale):
    if kind == "diameter":
        return round(2 * a[2] / scale, 2)
    xs, ys = (min(a[0], b[0]), max(a[0], b[0])), (min(a[1], b[1]), max(a[1], b[1]))
    vertical = place[0] < xs[0] - 1e-6 or place[0] > xs[1] + 1e-6
    return round((ys[1] - ys[0] if vertical else xs[1] - xs[0]) / scale, 2)


WANT = {
    ("spigot", "front"): [15.24, 7.24, 8.0, 8.0, 6.0],
    ("spigot", "top"): [4.0],
    ("keys", "front"): [75.0, 30.0],
    ("keys", "right"): [35.0, 26.0, 60.0, 17.5],      # no diameters: the callouts give the size (#324)
    ("keys", "top"): [17.8, 11.5, 23.5, 10.5],        # D-144: the stepped hole's x and y, the other's y and x
}

for part, cfg in JD.PARTS.items():
    for name, _orient, centre, _style in cfg["views"]:
        lines, circles = view_geometry(part, name, cfg["scale"], centre)
        dims = JD.plan_dims(part, name, lines, circles, cfg["scale"])
        got = [measured(k, a, b, p, cfg["scale"]) for k, a, b, p in dims]
        check(got == WANT[(part, name)], "%s %s view dimensions %s (want %s)" % (part, name, got, WANT[(part, name)]))
        # every dimension point is on the view's geometry (a line end or a circle centre)
        pts = {(round(l[0], 3), round(l[1], 3)) for l in lines} | {(round(l[2], 3), round(l[3], 3)) for l in lines}
        pts |= {(round(c[0], 3), round(c[1], 3)) for c in circles}
        on = all((round(a[0], 3), round(a[1], 3)) in pts and (b is None or (round(b[0], 3), round(b[1], 3)) in pts)
                 for _k, a, b, _p in dims)
        check(on, "%s %s view: every dimension attaches to view geometry" % (part, name))
        # no view runs into the notes box or off the sheet
        xs = [l[0] for l in lines] + [l[2] for l in lines]
        ys = [l[1] for l in lines] + [l[3] for l in lines]
        bx0, by0, bx1, by1 = JD.NOTES_BOX
        clear = max(xs) < bx0 - 5 or min(ys) > 297 - by1 + 5
        check(clear and min(xs) > 10 and min(ys) > 10 and max(ys) < 287,
              "%s %s view stays on the sheet and clear of the notes box" % (part, name))
        # every dimension's text well inside the frame (x 20 to 410, y 10 to 287): Fusion puts a vertical
        # dimension's text up to about 8 left of its placement (the key sheet's 60 read back at x 18.7 for a
        # placement at 29, on the frame line; the visual pass, 2026-11-01), so placements keep 12 clear of the
        # frame's sides; a horizontal one's text sits up to about 5 above it, so 8 clear of its top and bottom
        far = [p for _k, _a, _b, p in dims if not (32 <= p[0] <= 398 and 18 <= p[1] <= 279)]
        check(not far, "%s %s view: every dimension placed inside the frame with room for its text %s"
              % (part, name, far))

_saved = FIXING_HOLES[:]
FIXING_HOLES[:] = [(10.5, -7.0, 2.5), (10.5, 7.0, 2.5)]
_cfg = JD.PARTS["keys"]
_name, _o, _centre, _st = [v for v in _cfg["views"] if v[0] == "top"][0]
_lines, _circles = view_geometry("keys", "top", _cfg["scale"], _centre)
_got = [measured(k, a, b, pl, _cfg["scale"]) for k, a, b, pl in JD.plan_dims("keys", "top", _lines, _circles, _cfg["scale"])]
check(_got == [10.5, 10.5, 24.5], "keys top view, holes in line: no x dimension twice %s" % _got)
FIXING_HOLES[:] = _saved

# the top view's hole tags name the holes the table names (Reviewer 6 on #324: H03 and H04 were swapped against it)
_cfg = JD.PARTS["keys"]
_t = [v for v in _cfg["views"] if v[0] == "top"][0][2]
_row = [r for r in [n for n in _cfg["notes"] if isinstance(n, dict)][0]["table"] if r[0] == "111211"][0]
_want = {}
for _name, _xy in zip(("H03", "H04"), _row[5].split(";")):
    _x, _y = [float(v.replace("+", "")) for v in _xy.split(",")]
    _want[_name] = (_x, _y)
_sheet = lambda X, Y: (_t[0] + (X - 15.0) * _cfg["scale"], 297.0 - (_t[1] + Y * _cfg["scale"]))   # PDF x, y down
_circles = [_sheet(*xy) + (False,) for xy in ((10.5, 6.0), (17.8, -6.0))]         # hidden, as Fusion draws them
_back = lambda c: (round((c[0] - _t[0]) / _cfg["scale"] + 15.0, 2), round((297.0 - c[1] - _t[1]) / _cfg["scale"], 2))
_got = {lines[0].split()[0]: _back(pick(_circles)) for pick, lines, _o in _cfg["tags"]
        if lines[0].split()[0] in ("H03", "H04")}
check(_got == _want, "keys top view: H03 and H04 tag the holes the table gives them %s (want %s)" % (_got, _want))

# notes as PDF text, read back the way the mechanical check reads a drawing
try:
    import fitz
except ImportError:
    fitz = None
if fitz is None:
    check(False, "PyMuPDF is installed (needed for the notes)")
else:
    tmp = tempfile.mkdtemp()
    for part, cfg in JD.PARTS.items():
        blank = os.path.join(tmp, part + "-blank.pdf")
        doc = fitz.open()
        doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
        doc.save(blank)
        out = os.path.join(tmp, part + ".pdf")
        JD.add_notes(blank, out, cfg["notes"])
        page = fitz.open(out)[0]
        text = page.get_text()
        up = text.upper()
        k = page.rect.width / 420.0
        spans = [sp for b in page.get_text("dict")["blocks"] for ln in b.get("lines", []) for sp in ln["spans"]
                 if sp["text"].strip()]
        check(min(sp["size"] for sp in spans) >= 2.5 / 0.718 * k - 0.01,
              "%s notes: letters 2.5 mm high or more (Helvetica capitals; the D-114 pass)" % part)
        check(max(sp["bbox"][2] for sp in spans) <= JD.NOTES_BOX[2] * k + 0.5 and
              max(sp["bbox"][3] for sp in spans) <= JD.NOTES_BOX[3] * k,
              "%s notes: inside their box, clear of the frame" % part)
        check(bool(re.search(r"\bUNITS?\s*[:=]?\s*MM\b", up)), "%s notes: units mm" % part)
        check(bool(re.search(r"MATERIAL", up) and re.search(r"EN AW|\d{4}|A2|STEEL|ALUMIN", up)), "%s notes: material" % part)
        check(bool(re.search(r"FINISH", up)), "%s notes: finish" % part)
        check(bool(re.search(r"ISO\s*2768", up)), "%s notes: general tolerance" % part)
        check("Ø" in text and "±" in text or part == "spigot", "%s notes: Ø and ± read back" % part)
        if part == "keys":
            tags = set(re.findall(r"\bH\d{2}\b", up))
            check(tags >= {"H01", "H02", "H03", "H04"}, "keys notes: hole tags H01-H04 for the 4 hole axes")
            check(bool(re.search(r"\bTABULATED\b", up)), "keys notes: says TABULATED")
            nums = set(re.findall(r"(?<!\d)(\d{6})(?!\d)", text))
            check({"111211", "111212", "111213", "111214"} <= nums, "keys notes: list every part number")
        if part == "spigot":         # Reviewer 10 on #346: the tabulated spigot sheet, tested as the key sheet is
            check(bool(re.search(r"\bTABULATED\b", up)), "spigot notes: says TABULATED")
            nums = set(re.findall(r"(?<!\d)(\d{6})(?!\d)", text))
            check({"831001", "831010"} <= nums, "spigot notes: list both part numbers")
            check(any("L + 8" in ln for ln in text.splitlines()), "spigot notes: 'L + 8' on one line")

# the spigot sheet's table and letters (Reviewer 10 on #346): the view letters exactly the two sizes the table varies,
# and the table, the drawn part and the parts list agree
_sp = JD.PARTS["spigot"]
_tab = [n for n in _sp["notes"] if isinstance(n, dict)][0]["table"]
_hd = _tab[0]
_rows = {r[0]: dict(zip(_hd, r)) for r in _tab[1:]}
check(set(_rows) == {"831001", "831010"}, "spigot table: 831001 and 831010 (%s)" % sorted(_rows))
for _pn, _r in _rows.items():
    _L, _pr, _ov = float(_r["L"]), float(_r["PROUD"]), float(_r["OVERALL"])
    check(abs(_ov - (_L + 8.0)) < 1e-9 and abs(_pr - (_L + 0.76)) < 1e-9,
          "spigot table %s: OVERALL = L + 8 (the stud) and PROUD = L + 0.76 (the rivnut's head) (%s)" % (_pn, _r))
_vary = [c for c in _hd if c not in ("PART", "POD", "WHERE") and len({r[c] for r in _rows.values()}) > 1]
check(sorted(v for v, _l in _sp["letters"]) == sorted([_rows["831001"]["L"], _rows["831001"]["OVERALL"]]) and
      dict(_sp["letters"]) == {_rows["831001"]["L"]: "L", _rows["831001"]["OVERALL"]: "L + 8"},
      "spigot letters: the view's 831001 values (the saved design's) become L and L + 8 (%s; the table varies %s; "
      "PROUD isn't on the view)" % (_sp["letters"], _vary))
check(not any("F2" in r["WHERE"] or "FLOOR" in r["WHERE"] for r in _rows.values()),
      "spigot table: no floor panel F2 (D-132)")
import csv as _csv
_spec = os.path.join(HERE, "..", "..", "03-Manufacturing", "joints", "V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv")
with open(_spec, newline="", encoding="utf-8") as _f:
    _qty = {r.get("part_number") or r.get("pn") or "": r for r in _csv.DictReader(_f)}
_qcol = next((c for c in ("qty_per_pod", "qty", "quantity") if c in next(iter(_qty.values()))), None)
for _pn, _r in _rows.items():
    _got = _qty.get(_pn, {}).get(_qcol, "") if _qcol else ""
    check(_got != "" and float(_got) == float(_r["POD"]),
          "spigot table %s: POD %s matches the parts list (%s)" % (_pn, _r["POD"], _got))

# hole tags: the circles Fusion writes, solid (curves) and hidden (short straight dashes)
if fitz is not None:
    import math
    doc = fitz.open()
    page = doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
    k = page.rect.width / 420.0
    page.draw_circle(fitz.Point(80 * k, 70 * k), 5.04 * k, width=1.44)                  # solid, Ø10.08 on the sheet
    for i in range(16):                                                                 # hidden: 16 dashes round
        a0, a1 = 2 * math.pi * i / 16, 2 * math.pi * (i + 0.6) / 16
        p0 = fitz.Point((166 + 5.04 * math.cos(a0)) * k, (220 + 5.04 * math.sin(a0)) * k)
        p1 = fitz.Point((166 + 5.04 * math.cos(a1)) * k, (220 + 5.04 * math.sin(a1)) * k)
        page.draw_line(p0, p1, width=0.72)
    for i in range(10):                                                                 # a hidden cone's sides:
        y = 150 + i * 1.2                                                               # dashes, not a circle
        page.draw_line(fitz.Point(160 * k, y * k), fitz.Point(160 * k, (y + 0.8) * k), width=0.72)
        page.draw_line(fitz.Point(170 * k, y * k), fitz.Point(170 * k, (y + 0.8) * k), width=0.72)
    found = JD.hole_circles(page, 10.08)
    check([(round(c[0]), round(c[1]), c[2]) for c in found] == [(80, 70, True), (166, 220, False)],
          "hole circles: the solid and the hidden one found, the cone's dashes not (%s)" % found)

    # view B, 111212 from above, where the sheet puts it: its sizes read back from the sheet
    doc = fitz.open()
    page = doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
    vb_x, vb_y = JD.PARTS["keys"]["view_b"]["origin"]
    x0, y0, x1, y1 = JD.view_b(JD.Sheet(page), (vb_x, vb_y))
    text = page.get_text()
    for want in ("37.84", "22.16", "A = 24.14°", "H01, H02 SQUARE", "TO THE STUD FACE"):
        check(want in text, "view B shows %s" % want)
    check(abs((x0 - vb_x)) < 1e-6 and x1 > vb_x + 37.84 * 2 and y1 < 240.0 - 3.0,
          "view B: starts at the back face, reaches past the long side, ends 3 or more above the title block "
          "(%.1f)" % y1)
    # and clear of the notes by finish()'s rule (2026-11-01: longer notes stopped the finish 2 mm into view B)
    blank = os.path.join(tmp, "vb-blank.pdf")
    d2 = fitz.open()
    d2.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
    d2.save(blank)
    end = JD.add_notes(blank, os.path.join(tmp, "vb-notes.pdf"), JD.PARTS["keys"]["notes"])
    check(y0 - 4.0 - 2 * JD.NOTE_MM >= end,
          "view B (from %.1f mm) clear of the key sheet's notes (to %.1f mm), as finish() checks" % (y0, end))
    tan = math.tan(math.radians(24.14))
    check(abs(30 + 17.5 * tan - 37.84) < 0.005 and abs(30 - 17.5 * tan - 22.16) < 0.005,
          "view B: the long and short sides follow A = 24.14° about the centre line (as the table)")

# the lettering: on a page with Fusion-like dimension values (vertical, bottom to top, and one horizontal) and a line,
# the two values become letters in their direction, the other value and the line stay, and a value that isn't
# there exactly once stops it
if fitz is not None:
    doc = fitz.open()
    page = doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
    k = page.rect.width / 420.0
    page.insert_text(fitz.Point(82.5 * k, 118.28 * k), "15.24", fontsize=13.86, fontname="helv", rotate=90)
    page.insert_text(fitz.Point(88.06 * k, 96.77 * k), "7.24", fontsize=13.86, fontname="helv", rotate=90)
    page.insert_text(fitz.Point(115.0 * k, 159.0 * k), "5.88", fontsize=13.86, fontname="helv")
    page.draw_line(fitz.Point(84.0 * k, 80.0 * k), fitz.Point(84.0 * k, 130.0 * k), width=0.72)   # a dimension line
    src, dst = os.path.join(tmp, "letters-in.pdf"), os.path.join(tmp, "letters-out.pdf")
    doc.save(src)
    JD.letter_dims(src, dst, [("7.24", "L"), ("15.24", "L + 8")])
    pg = fitz.open(dst)[0]
    got = {t: d for t, d, _s in JD.view_spans(pg)}
    check(got.get("L") == (0.0, -1.0) and got.get("L + 8") == (0.0, -1.0) and "5.88" in got
          and "7.24" not in got and "15.24" not in got,
          "letters: 7.24 and 15.24 become L and L + 8, bottom to top; 5.88 stays (%s)" % got)
    check(any(it[0] == "l" for d in pg.get_drawings() for it in d["items"]), "letters: the dimension line stays")
    try:
        JD.letter_dims(src, dst, [("9.99", "L")])
        check(False, "letters: a value not on the views stops the finish")
    except SystemExit:
        check(True, "letters: a value not on the views stops the finish")

# a value two sizes share (the spigot's pin Ø8, left to right, and its stud's 8 long, bottom to top): "h" relabels only
# the left-to-right one, the other stays; without a way it stops, as the value is there twice
if fitz is not None:
    doc = fitz.open()
    page = doc.new_page(width=420 / 25.4 * 72, height=297 / 25.4 * 72)
    k = page.rect.width / 420.0
    page.insert_text(fitz.Point(88.0 * k, 131.0 * k), "8", fontsize=13.86, fontname="helv", rotate=90)
    page.insert_text(fitz.Point(119.0 * k, 113.0 * k), "8", fontsize=13.86, fontname="helv")
    page.insert_text(fitz.Point(115.0 * k, 159.0 * k), "5.88", fontsize=13.86, fontname="helv")
    src, dst = os.path.join(tmp, "relabel-in.pdf"), os.path.join(tmp, "relabel-out.pdf")
    doc.save(src)
    JD.letter_dims(src, dst, [("8", "Ø8 h9", "h"), ("5.88", "M6")])
    got = [(t, d) for t, d, _s in JD.view_spans(fitz.open(dst)[0])]
    check(sorted(got) == sorted([("8", (0.0, -1.0)), ("Ø8 h9", (1.0, 0.0)), ("M6", (1.0, 0.0))]),
          "relabel: the left-to-right 8 becomes Ø8 h9 and 5.88 M6; the bottom-to-top 8 stays (%s)" % got)
    try:
        JD.letter_dims(src, dst, [("8", "Ø8 h9")])
        check(False, "relabel: a value on the views twice, with no way given, stops the finish")
    except SystemExit:
        check(True, "relabel: a value on the views twice, with no way given, stops the finish")

# the spigot sheet itself: its pin's diameter reads Ø8 h9 and the stud M6 on the views, and no dimension value is
# printed twice (the mechanical check's ISO 129-1 rule, which counts Fusion's dimension texts)
if fitz is not None:
    _pdf = os.path.join(HERE, JD.PARTS["spigot"]["drawing"] + ".pdf")
    _v = [(t, d) for t, d, _s in JD.view_spans(fitz.open(_pdf)[0])]
    check(_v.count(("Ø8 h9", (1.0, 0.0))) == 1 and _v.count(("M6", (1.0, 0.0))) == 1 and
          not [t for t, _d in _v if t in ("5.88", "7.24", "15.24")],
          "spigot sheet: the views read Ø8 h9 and M6 once, and L and L + 8 for the table's sizes (%s)" % _v)
    _spec = importlib.util.spec_from_file_location("pdf_traps", os.path.join(HERE, "..", "..", "..", "tools", "checks",
                                                                             "pdf_traps.py"))
    _pt = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_pt)
    _tw = [f for f in _pt.findings(_pdf) if f[0] == "dimension-twice"]
    check(not _tw, "spigot sheet: no dimension value printed twice (%s)" % _tw)

print("\n%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
