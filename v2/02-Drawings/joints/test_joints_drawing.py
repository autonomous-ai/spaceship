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
    elif part == "keys" and view == "front":           # X right, Z up: 25 x 75
        segs += [(0, 0, 25, 0), (25, 0, 25, 75), (25, 75, 0, 75), (0, 75, 0, 0)]
        for z in (26, 60):                              # hidden: stud holes along X
            segs += [(0, z - 2.5, 25, z - 2.5), (0, z + 2.5, 25, z + 2.5)]
        segs += [(7.5, 0, 7.5, 18), (12.5, 0, 12.5, 18)]  # hidden: fixing holes
        off = (12.5, 37.5)
    elif part == "keys" and view == "right":           # Y right, Z up: the stud face 35 x 75
        segs += [(-17.5, 0, 17.5, 0), (17.5, 0, 17.5, 75), (17.5, 75, -17.5, 75), (-17.5, 75, -17.5, 0)]
        circs += [(0, 26, 2.5), (0, 60, 2.5)]
        off = (0.0, 37.5)
    elif part == "keys" and view == "top":             # X right, Y up: 25 x 35
        segs += [(0, -17.5, 25, -17.5), (25, -17.5, 25, 17.5), (25, 17.5, 0, 17.5), (0, 17.5, 0, -17.5)]
        segs += [(0, -2.5, 25, -2.5), (0, 2.5, 25, 2.5)]  # hidden: stud holes seen from above
        circs += [(10, -7.5, 2.5), (10, 7.5, 2.5)]        # hidden: fixing holes
        off = (12.5, 0.0)
    to = lambda x, y: (cx + (x - off[0]) * scale, cy + (y - off[1]) * scale)
    lines = [to(a, b) + to(c, d) for a, b, c, d in segs]
    circles = [to(x, y) + (r * scale,) for x, y, r in circs]
    return lines, circles


def measured(kind, a, b, place, scale):
    if kind == "diameter":
        return round(2 * a[2] / scale, 2)
    xs, ys = (min(a[0], b[0]), max(a[0], b[0])), (min(a[1], b[1]), max(a[1], b[1]))
    vertical = place[0] < xs[0] - 1e-6 or place[0] > xs[1] + 1e-6
    return round((ys[1] - ys[0] if vertical else xs[1] - xs[0]) / scale, 2)


WANT = {
    ("spigot", "front"): [15.24, 7.24, 8.0, 8.0, 6.0],
    ("spigot", "top"): [4.0],
    ("keys", "front"): [75.0, 25.0],
    ("keys", "right"): [35.0, 26.0, 60.0, 17.5, 5.0],
    ("keys", "top"): [10.0, 10.0, 15.0, 5.0],
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
        out = JD.add_notes(blank, os.path.join(tmp, part + ".pdf"), cfg["notes"])
        text = fitz.open(out)[0].get_text()
        up = text.upper()
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

print("\n%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
