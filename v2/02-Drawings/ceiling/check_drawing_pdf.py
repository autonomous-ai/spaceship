"""Read a finished ceiling drawing PDF back and check what the eye can miss (offline, D-114).

    python3 v2/02-Drawings/ceiling/check_drawing_pdf.py rib [--log ANNOTATE_LOG]
    (finish_drawings.py runs it on each drawing it finishes)

Checks, each against drawing_specs.py:
- the sheet size;
- the first-angle symbol: a picture of it (render_notes.render_symbol) at its size where symbol_place puts it;
  or, on a drawing with the symbol drawn as a sketch, read from the layer Fusion names after the sketch: exactly the
  four sides of the outline (the narrow end 5 high, away from the circles; the wide end 10 high; 10 long) and two
  circles (radius 5 and 2.5) centred to its right. Sketch outlines came out triangles twice (sharing a sketch with
  the circles, and on A1 in a sketch of its own), so the drawings now use the picture;
- each scale label picture at the size it was drawn at (10 px per mm, so its lettering is 3.5 mm), with its top
  left corner where the spec puts it (the labels' places need the annotate log's view extents);
- the notes and the title data as text where their pictures were (the finish step writes them, pdf_notes_text.py):
  every word of the spec's, in order;
- hidden lines only inside the views the spec draws with hidden lines (needs the log; without
  it, none at all when the spec has no such view);
- every text at least 2.5 mm high (font size), the title block's own labels at least 1.8;
- on a drawing with a hole table: the table has at least one row under its header (the tray's second drawing
  printed an empty table, which the eye can take for a part with no holes);
- every size the spec lists (drawing_specs.spec sizes) printed as a dimension exactly once (ISO 129-1), outside the
  title block and the hole table (the rib's crown went missing when the sizes moved to the outer faces);
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
                pairs = [(it[1], it[2])]
            elif it[0] == "qu":         # PyMuPDF reads a closed 4-point path as one quad
                q = it[1]
                pairs = [(q.ul, q.ur), (q.ur, q.lr), (q.lr, q.ll), (q.ll, q.ul)]
            elif it[0] == "re":
                r = it[1]
                pairs = [(r.tl, r.tr), (r.tr, r.br), (r.br, r.bl), (r.bl, r.tl)]
            else:
                continue
            for p0, p1 in pairs:
                a = (round(p0.x * MM, 1), round(height - p0.y * MM, 1))
                b = (round(p1.x * MM, 1), round(height - p1.y * MM, 1))
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
    for im in page.get_image_info(xrefs=True):
        if not im["xref"]:              # what a removed picture leaves (pdf_notes_text.py): nothing shows
            continue
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


def spans_mm(page, height):
    """[(text, font size mm, x0, y0, x1, y1)] in sheet mm, origin bottom left."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                t = sp["text"].strip()
                if t:
                    x0, y0, x1, y1 = sp["bbox"]
                    out.append((t, sp["size"] * MM, x0 * MM, height - y1 * MM, x1 * MM, height - y0 * MM))
    return out


def hole_table_box(spans, width):
    """(x0, y0, x1, y1) of the hole table, from its header row ('Hole', 'X Dim', 'Y Dim', 'Description') down to
    its last row, or None when there is no header. Rows are the spans under the header, inside its width and inside
    the frame (the border's zone letters stand just outside it, at the same height)."""
    head = [s for s in spans if s[0] == "Hole"]
    for h in head:
        row = [s for s in spans if abs(s[3] - h[3]) < 1.5 and s[0] in ("X Dim", "Y Dim", "Description")]
        if len(row) == 3:
            x0, x1 = h[2] - 3.0, min(max(s[4] for s in row) + 30.0, width - 10.0)
            under = [s for s in spans if x0 <= s[2] <= x1 and h[3] - 60.0 < s[3] < h[3] - 1.0]
            y0 = min([s[3] for s in under] + [h[3]]) - 1.0
            return (x0, y0, x1, h[5] + 12.0), under
    return None, []


def table_problems(spans, sp, width):
    if not sp.get("holes"):
        return []
    box, rows = hole_table_box(spans, width)
    if box is None:
        return ["the spec has holes but the sheet has no hole table header"]
    if not rows:
        return ["the hole table has no rows under its header (Fusion had not filled it when the PDF was made?)"]
    return []


def text_boxes(sp):
    """{'notes' | 'title': (x0, y0, x1, y1)}: where the finish step writes the notes and the title data as text
    (pdf_notes_text.py), sheet mm from the bottom left."""
    import pdf_notes_text as T
    font = fitz.Font(fontfile=T.font_file())
    out = {}
    for what, h in (("notes", T.notes_height(sp["notes"], S.IMG_W, font)), ("title", T.title_height(sp["title"]))):
        x, top = sp["images"][what]
        out[what] = (x, top - h, x + S.IMG_W, top)
    return out


def block_text(page, height, box):
    """The words inside a box (sheet mm), line by line from the top, each line left to right, one space apart."""
    x0, y0, x1, y1 = box
    clip = fitz.Rect(x0 / MM, (height - y1) / MM, x1 / MM, (height - y0) / MM)
    lines = {}
    for w in page.get_text("words", clip=clip):
        lines.setdefault(round(w[3] * 2) / 2, []).append(w)     # by baseline, to half a point
    return " ".join(w[4] for _y, ws in sorted(lines.items()) for w in sorted(ws, key=lambda w: w[0]))


def text_block_problems(page, height, sp):
    """The notes and the title data as text in their boxes, every word of the spec's, in order (the finish step
    writes them in place of the pictures Fusion was given)."""
    bad = []
    boxes = text_boxes(sp)
    want = {"notes": "NOTES " + " ".join("%d. %s" % (i + 1, n) for i, n in enumerate(sp["notes"])),
            "title": "TITLE DATA " + " ".join("%s %s" % (k, v) for k, v in sp["title"])}
    for what, text in want.items():
        got = block_text(page, height, boxes[what])
        exp = " ".join(text.split())
        if got != exp:
            i = next((k for k, (a, b) in enumerate(zip(got, exp)) if a != b), min(len(got), len(exp)))
            bad.append("the %s text differs from the spec at character %d: read %r, want %r" % (
                what, i, got[max(0, i - 30):i + 30], exp[max(0, i - 30):i + 30]))
    return bad


def size_problems(spans, sp, width, boxes=None):
    """Each listed size printed once as a dimension: a span of that text at dimension size (over 4 mm), outside the
    title block (180 x 47 in the frame's corner), the hole table and the notes and title data boxes."""
    want = sp.get("sizes") or []
    if not want:
        return []
    box, _rows = hole_table_box(spans, width)
    tb = (width - 10.0 - 180.0, 10.0)

    def counted(s):
        if s[1] <= 4.0:
            return False
        if s[2] >= tb[0] and s[3] <= tb[1] + 47.0:
            return False
        if box and box[0] <= s[2] <= box[2] and box[1] <= s[3] <= box[3]:
            return False
        if any(b[0] <= s[2] <= b[2] and b[1] <= s[3] <= b[3] for b in (boxes or {}).values()):
            return False
        return True
    got = Counter(s[0] for s in spans if counted(s))
    return ["size %s is printed %d times (the spec wants it once)" % (v, got.get(v, 0)) for v in want
            if got.get(v, 0) != 1]


def text_problems(page, doc, boxes=None):
    """Letter heights and names over the whole sheet; a dimension value printed twice is a warning (outside the
    notes and title data boxes, whose part number and sizes are words, not dimensions)."""
    bad, warn = [], []
    height = page.rect.height * MM
    spans, dims = [], []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                t = sp["text"].strip()
                if not t:
                    continue
                spans.append((t, sp["size"] * MM))
                x, y = sp["bbox"][0] * MM, height - sp["bbox"][3] * MM
                if not any(q[0] <= x <= q[2] and q[1] <= y <= q[3] for q in (boxes or {}).values()):
                    dims.append((t, sp["size"] * MM))
    for t, size in spans:
        least = 1.8 if t in TITLE_LABELS else 2.5
        if size < least - 0.02:
            bad.append("text %r is %.2f mm (at least %.1f)" % (t, size, least))
        if NAMES.search(t):
            bad.append("an account name in the text: %r" % t)
    for k, v in (doc.metadata or {}).items():
        if v and NAMES.search(str(v)):
            bad.append("an account name in the metadata (%s)" % k)
    nums = Counter(t for t, size in dims if size > 4.0 and re.fullmatch(r"[Ø]?\d+(\.\d+)?", t))
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
    ext = extents_from_log(log_text) if log_text else {}
    wanted = []
    x0, cy = S.symbol_place(sp["sheet"])
    if any(d.get("layer") == SYMBOL for d in page.get_drawings()):
        bad += symbol_problems(page, h, (x0, cy))         # a drawing with the symbol drawn as a sketch
    else:                                                 # the symbol as a picture (render_notes.render_symbol)
        m = S.SYMBOL_PX_MARGIN
        wanted.append(("first-angle symbol", (x0 - m, cy + 5.0 + m),
                       png_size_mm(os.path.join(notes_dir, "FIRST_ANGLE_SYMBOL.png"))))
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
    tb, warn = text_problems(page, doc, text_boxes(sp))
    bad += tb
    bad += text_block_problems(page, h, sp)
    spans = spans_mm(page, h)
    bad += table_problems(spans, sp, w)
    bad += size_problems(spans, sp, w, text_boxes(sp))
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
