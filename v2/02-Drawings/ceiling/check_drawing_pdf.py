"""Read a finished ceiling drawing PDF back and check what the eye can miss (offline, D-114).

    python3 v2/02-Drawings/ceiling/check_drawing_pdf.py rib [--log ANNOTATE_LOG]
    (finish_drawings.py runs it on each drawing it finishes)

Checks, each against drawing_specs.py:
- the sheet size;
- the first-angle symbol, read from the layer Fusion names after its sketch: exactly the four
  sides of the outline (the narrow end 5 high, away from the circles; the wide end 10 high; 10
  long) where symbol_place puts it, and two circles (radius 5 and 2.5) centred to its right.
  The first rib sample's outline came out a triangle when it shared a sketch with the circles;
- each image (notes, title data, the scale labels) at the size it was drawn at (10 px per mm,
  so its lettering is 2.5 mm), with its top left corner where the spec puts it (the labels'
  places need the annotate log's view extents);
- hidden lines only inside the views the spec draws with hidden lines (needs the log; without
  it, none at all when the spec has no such view);
- every text at least 2.5 mm high (font size), the title block's own labels at least 1.8;
- no account name in the text or the metadata ("Created by" is cleared by pdf_clear_field.py).
Warns (look by eye) when a dimension value is printed more than once: either two features of
the same size or a size given twice (ISO 129-1: each size once).
Prints "CHECK PDF <drawing>: PASS" or "FAIL" with the reasons; exits 1 on FAIL.
"""

import argparse
import os
import re
import struct
import sys
from collections import Counter

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drawing_specs as S  # noqa: E402

MM = 25.4 / 72
SYMBOL = "PROJECTION SYMBOL - FIRST ANGLE"
TITLE_LABELS = {"Dept.", "Technical reference", "Created by", "Approved by", "Document type",
                "Document status", "Title", "DWG No.", "Rev.", "Date of issue", "Sheet"}
NAMES = re.compile(r"duy|huynh|uiv@|gmail", re.I)
VIEW_LINE = re.compile(r"view (\w+)\s+extent \(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)")


def png_size_mm(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w / S.PX_MM, h / S.PX_MM


def extents_from_log(text):
    """{view: (x0, y0, x1, y1)} from make_drawing_ceiling.py's 'view ... extent (...)' lines."""
    return {m.group(1): tuple(float(m.group(i)) for i in range(2, 6)) for m in VIEW_LINE.finditer(text)}


def segments(page, layer, height):
    """The straight lines of one layer, in sheet mm (origin bottom left), each once (Fusion's export
    writes a 2-point line back and forth)."""
    out = set()
    for d in page.get_drawings():
        if d.get("layer") != layer:
            continue
        for it in d["items"]:
            if it[0] == "l":
                a = (round(it[1].x * MM, 1), round(height - it[1].y * MM, 1))
                b = (round(it[2].x * MM, 1), round(height - it[2].y * MM, 1))
                if a != b:
                    out.add(tuple(sorted((a, b))))
    return sorted(out)


def circles(page, layer, height):
    """(cx, cy, r) of each closed curve path of one layer, sheet mm."""
    out = []
    for d in page.get_drawings():
        if d.get("layer") != layer or not any(it[0] == "c" for it in d["items"]):
            continue
        r = d["rect"]
        out.append((round((r.x0 + r.x1) / 2 * MM, 1), round(height - (r.y0 + r.y1) / 2 * MM, 1),
                    round((r.x1 - r.x0) / 2 * MM, 1)))
    return sorted(set(out))


def symbol_problems(page, height, at, d=5.0, big=10.0, length=10.0, gap=4.0, tol=0.3):
    x0, y0 = at
    want = sorted(tuple(sorted(s)) for s in [
        ((x0, y0 - d / 2), (x0 + length, y0 - big / 2)), ((x0 + length, y0 - big / 2), (x0 + length, y0 + big / 2)),
        ((x0 + length, y0 + big / 2), (x0, y0 + d / 2)), ((x0, y0 + d / 2), (x0, y0 - d / 2))])
    got = segments(page, SYMBOL, height)
    bad = []

    def near(s, t):
        return all(abs(p - q) <= tol for a, b in zip(s, t) for p, q in zip(a, b))
    if len(got) != 4 or not all(any(near(w, g) for g in got) for w in want):
        bad.append("symbol outline is not the 4-sided first-angle outline at %s: read %s" % (at, got))
    cx = x0 + length + gap + big / 2
    cs = circles(page, SYMBOL + " CIRCLES", height)
    for r in (big / 2, d / 2):
        if not any(abs(c[0] - cx) <= tol and abs(c[1] - y0) <= tol and abs(c[2] - r) <= tol for c in cs):
            bad.append("symbol circle r %g at (%g, %g) missing: read %s" % (r, cx, y0, cs))
    return bad


def image_boxes(page, height):
    """Each image's (x0, top, width, height) in sheet mm."""
    out = []
    for im in page.get_image_info():
        b = fitz.Rect(im["bbox"])
        out.append((b.x0 * MM, height - b.y0 * MM, b.width * MM, b.height * MM))
    return out


def image_problems(boxes, wanted, tol_size=0.5, tol_place=1.0):
    """wanted: [(what, (x0, top) or None, (w, h))]; each needs one image of that size (and place)."""
    bad = []
    for what, place, (w, h) in wanted:
        hit = [b for b in boxes if abs(b[2] - w) <= tol_size and abs(b[3] - h) <= tol_size and
               (place is None or (abs(b[0] - place[0]) <= tol_place and abs(b[1] - place[1]) <= tol_place))]
        if not hit:
            bad.append("%s image: none %.1f x %.1f mm%s; images on the sheet: %s" % (
                what, w, h, "" if place is None else " with its top left at (%.1f, %.1f)" % place,
                ", ".join("%.1f x %.1f at (%.1f, %.1f)" % (b[2], b[3], b[0], b[1]) for b in boxes)))
    return bad


def hidden_problems(page, height, sp, ext):
    hidden_views = {k for k, v in sp.get("styles", {}).items() if v == "hidden"}
    pieces = []
    for d in page.get_drawings():
        if d.get("layer") == "Hidden":
            r = d["rect"]
            pieces.append(((r.x0 + r.x1) / 2 * MM, height - (r.y0 + r.y1) / 2 * MM))
    if not pieces:
        return [], "no hidden lines"
    if not ext:
        if hidden_views:
            return [], "%d hidden-line pieces; no log, so not placed in views" % len(pieces)
        return ["%d hidden-line pieces, but the spec draws no view with hidden lines" % len(pieces)], ""
    where = Counter()
    for x, y in pieces:
        hit = [k for k, (x0, y0, x1, y1) in ext.items() if x0 - 1 <= x <= x1 + 1 and y0 - 1 <= y <= y1 + 1]
        where[hit[0] if hit else "outside the views"] += 1
    bad = ["%d hidden-line pieces in the %s view, drawn with visible edges only" % (n, k)
           for k, n in sorted(where.items()) if k not in hidden_views]
    return bad, "hidden-line pieces per view: %s" % dict(where)


def text_problems(page, doc):
    bad, warn = [], []
    spans = [(sp["text"].strip(), sp["size"] * MM) for b in page.get_text("dict")["blocks"]
             for ln in b.get("lines", []) for sp in ln["spans"] if sp["text"].strip()]
    for t, size in spans:
        least = 1.8 if t in TITLE_LABELS else 2.5
        if size < least - 0.02:
            bad.append("text %r is %.2f mm (at least %.1f)" % (t, size, least))
        if NAMES.search(t):
            bad.append("an account name in the text: %r" % t)
    for k, v in (doc.metadata or {}).items():
        if v and NAMES.search(str(v)):
            bad.append("an account name in the metadata (%s)" % k)
    nums = Counter(t for t, size in spans if size > 4.0 and re.fullmatch(r"[Ø]?\d+(\.\d+)?", t))
    warn += ["dimension value %s is printed %d times: two features, or one size given twice?" % (t, n)
             for t, n in sorted(nums.items()) if n > 1]
    return bad, warn


def check(key, pdf=None, log_text=None, notes_dir=None):
    sp = S.SPECS[key]
    pdf = pdf or os.path.join(HERE, sp["drawing"] + ".pdf")
    notes_dir = notes_dir or os.path.join(HERE, ".notes")
    doc = fitz.open(pdf)
    page = doc[0]
    w, h = page.rect.width * MM, page.rect.height * MM
    bad, info = [], []
    sw, sh = S.SHEETS[sp["sheet"]]
    if abs(w - sw) > 1 or abs(h - sh) > 1:
        bad.append("sheet %.1f x %.1f, the spec wants %s" % (w, h, sp["sheet"]))
    bad += symbol_problems(page, h, S.symbol_place(sp["sheet"]))
    ext = extents_from_log(log_text) if log_text else {}
    wanted = []
    for what in ("notes", "title"):
        png = os.path.join(notes_dir, "%s_%s.png" % (sp["drawing"], what.upper()))
        wanted.append((what, sp["images"][what], png_size_mm(png)))
    for view in S.labels(sp):
        png = os.path.join(notes_dir, "%s_LABEL_%s.png" % (sp["drawing"], view.upper()))
        lw, lh = png_size_mm(png)
        place = None
        if view in ext:
            x0, y0, x1, _y1 = ext[view]
            place = ((x0 + x1) / 2 - lw / 2, y0 - S.LABEL_GAP - (14.0 if view == "top" else 0.0))
        wanted.append(("%s view scale label" % view, place, (lw, lh)))
    bad += image_problems(image_boxes(page, h), wanted)
    hb, hinfo = hidden_problems(page, h, sp, ext)
    bad += hb
    if hinfo:
        info.append(hinfo)
    tb, warn = text_problems(page, doc)
    bad += tb
    return bad, warn, info


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--pdf")
    ap.add_argument("--log")
    o = ap.parse_args(argv)
    log_text = open(o.log, encoding="utf-8", errors="replace").read() if o.log else None
    bad, warn, info = check(o.key, o.pdf, log_text)
    name = S.SPECS[o.key]["drawing"]
    for line in info:
        print("  " + line)
    for line in warn:
        print("  WARNING: " + line)
    for line in bad:
        print("  " + line)
    print("CHECK PDF %s: %s" % (name, "FAIL (%d)" % len(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
