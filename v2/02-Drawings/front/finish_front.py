"""Finish FRONT's Fusion drawing PDFs: name strip and title block, then the notes and the title data as PDF text.

    python3 v2/02-Drawings/front/finish_front.py KEY [KEY ...]      (keys of drawing_specs.SPECS, e.g. fixed_unit)

For each drawing: takes Fusion's raw export from .raw/ (make_drawing_front.py), runs the shared finish step
tools/fusion/pdf_clear_field.py (Created by and the PDF author read "Autonomous", the title block's DWG No., Rev.,
status and title filled), then takes out the two pictures make_drawing_front.py placed for the notes and the title
data (Fusion's drawing API can't place text, render_notes.py) and writes the same content in their place as real PDF
text and lines, in the same layout: 2.5 mm capitals (ISO 3098), the same wrapping, the same boxes. So the notes can
be searched, copied and read by the mechanical checks (C05 reads units, material, finish and tolerances from a
drawing's text), as the other teams' Fusion sheets do (BASE's finish_pdfs.py). Then it re-reads the PDF and fails
unless every note line and title value is there as text and no picture is left; and it renders the sheet as NAME_IMG.png to check by
eye. The font is subset-embedded. Needs PyMuPDF.
"""

import os
import re
import subprocess
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import drawing_specs as S  # noqa: E402
import render_notes as RN  # noqa: E402  the pictures' own layout numbers (PX_MM, sizes, wrapping)

CLEAR = os.path.join(REPO, "tools", "fusion", "pdf_clear_field.py")
MM = 72.0 / 25.4


def font_path():
    for p in RN.FONT_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("no Arial Unicode font found (render_notes.FONT_PATHS)")


def em_mm(h_mm):
    """The em of render_notes.font(h_mm), in mm: the same rounding to whole pixels."""
    return int(round(h_mm * RN.PX_MM / 0.72)) / RN.PX_MM


def wrap(font, s, em, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.text_length(t, fontsize=em) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Sheet:
    """Writes on one page in mm from a box's top-left corner, scaled as the picture was placed."""

    def __init__(self, page, rect, scale, fontfile):
        self.page, self.r, self.k, self.ff = page, rect, scale, fontfile
        self.font = fitz.Font(fontfile=fontfile)

    def pt(self, x, y):
        return fitz.Point(self.r.x0 + x * self.k * MM, self.r.y0 + y * self.k * MM)

    def text(self, x, y_top, s, em):
        """s with its ascender line at y_top (Pillow's default anchor, as render_notes drew it)."""
        base = y_top + self.font.ascender * em
        self.page.insert_text(self.pt(x, base), s, fontsize=em * self.k * MM, fontname="AU", fontfile=self.ff)

    def line(self, x0, y0, x1, y1, w):
        self.page.draw_line(self.pt(x0, y0), self.pt(x1, y1), color=(0, 0, 0), width=w * self.k * MM)

    def box(self, w, h, lw):
        self.page.draw_rect(fitz.Rect(self.pt(lw / 2, lw / 2), self.pt(w - lw / 2, h - lw / 2)), color=(0, 0, 0),
                            width=lw * self.k * MM)


def write_notes(sh, sp):
    """render_notes.render_notes, as text."""
    W, pad, num, lh = RN.S.IMG_W, 2.0, 6.0, 4.2
    f, fb = em_mm(2.5), em_mm(3.0)
    rows = [("NOTES", fb, None)]
    for i, n in enumerate(sp["notes"]):
        for j, line in enumerate(wrap(sh.font, n, f, W - 2 * pad - num)):
            rows.append((line, f, "%d." % (i + 1) if j == 0 else ""))
    H = pad * 2 + lh * len(rows)
    sh.box(W, H, 0.3)
    y = pad
    for text, ff, n in rows:
        if n is None:
            sh.text(pad, y, text, ff)
        else:
            if n:
                sh.text(pad, y, n, ff)
            sh.text(pad + num, y, text, ff)
        y += lh
    return H, [t for t, _f, _n in rows]


def write_title(sh, sp):
    """render_notes.render_title, as text."""
    W, lh, col = RN.S.IMG_W, 6.5, 38.0
    f, fb = em_mm(2.5), em_mm(3.0)
    rows = sp["title"]
    H = lh * (len(rows) + 1) + 0.6
    sh.box(W, H, 0.4)
    sh.text(2.0, 1.0, "TITLE DATA (the title block fields can't be set by script)", f)
    y = lh
    for label, value in rows:
        sh.line(0, y, W, y, 0.2)
        sh.text(2.0, y + 1.6, label, f)
        ff = fb if label in ("PART NO.", "NAME") else f
        sh.text(col + 2.0, y + (1.2 if ff is fb else 1.6), str(value), ff)
        y += lh
    sh.line(col, lh, col, H, 0.2)
    return H, [str(v) for _l, v in rows] + [l for l, _v in rows]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def finish(key):
    sp = S.SPECS[key]
    name = sp["drawing"]
    raw = os.path.join(HERE, ".raw", name + ".pdf")
    out = os.path.join(HERE, name + ".pdf")
    if not os.path.exists(raw):
        raise FileNotFoundError("no raw export %s (make_drawing_front.py makes it)" % raw)
    r = subprocess.run([sys.executable, CLEAR, raw, out], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("pdf_clear_field failed on %s: %s" % (name, (r.stderr or r.stdout).strip()[-400:]))
    doc = fitz.open(out)
    page = doc[0]
    pics = sorted((fitz.Rect(i["bbox"]) for i in page.get_image_info()), key=lambda b: b.y0)
    if len(pics) != 2:
        raise RuntimeError("%s: %d pictures on the sheet, expected the notes and the title data" % (name, len(pics)))
    for b in pics:
        page.add_redact_annot(b)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_NONE)
    ff = font_path()
    want = []
    for b, writer in zip(pics, (write_notes, write_title)):
        k = b.width / (RN.S.IMG_W * MM)               # the scale Fusion placed the picture at
        h, texts = writer(Sheet(page, b, k, ff), sp)
        if h * k * MM > b.height + 1.0:
            raise RuntimeError("%s: the text box (%.1f mm) is taller than its picture's place (%.1f mm)" % (
                name, h * k, b.height / MM))
        want += texts
    doc.subset_fonts()
    doc.save(out + ".tmp", garbage=4, deflate=True)
    doc.close()
    os.replace(out + ".tmp", out)
    # read back: every line and value as text, no picture left, the creator stamp kept
    doc = fitz.open(out)
    got = norm(" ".join(p.get_text() for p in doc))
    missing = [t for t in want if norm(t) and norm(t) not in got]
    left = sum(len(p.get_images()) for p in doc)
    if missing or left:
        raise RuntimeError("%s: read-back failed: %d text(s) missing (%s), %d picture(s) left" % (
            name, len(missing), missing[:3], left))
    if doc.metadata.get("author") != "Autonomous":
        raise RuntimeError("%s: the PDF author isn't Autonomous" % name)
    pix = doc[0].get_pixmap(dpi=100)
    png = os.path.join(HERE, re.sub(r"_DWG$", "_IMG", name) + ".png")      # conventions section 7: DOCTYPE IMG
    pix.save(png)
    print("%s: notes and title data as text (%d lines and values read back), %.1f MB; render %s %dx%d" % (
        name, len(want), os.path.getsize(out) / 1e6, os.path.basename(png), pix.width, pix.height))


def main(keys):
    if not keys:
        raise SystemExit(__doc__)
    for key in keys:
        finish(key)


if __name__ == "__main__":
    main(sys.argv[1:])
