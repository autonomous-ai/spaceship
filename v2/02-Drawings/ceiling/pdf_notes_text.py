"""Write a drawing's notes and title data onto its finished PDF as text, in place of the two pictures that
make_drawing_ceiling.py put on the Fusion sheet (offline; CEILING, AIR and INTERIOR drawings).

The mechanical checks (tools/checks, C05) read a drawing's text for its units, material, finish and tolerances,
and a picture holds no text, so the rib's first finished PDF failed them (2026-11-01). Fusion's drawing API can't
put text on a sheet (custom table cells come out blank), so the pictures stay on the native drawing, and here, as
BASE's finish step does (v2/02-Drawings/base/finish_pdfs.py), each is found at the place its spec gives, removed
from the PDF page, and the same words are written in its box: 3.5 mm Arial Unicode (2.5 mm capitals, ISO 3098, as
tools/checks/pdf_traps.py measures; the Vietnamese names need its letters) on the pictures' line pitch, the
headings 4.2 mm. A text block taller than its picture is refused rather than run into what lies below.
"""

import os
import re

import fitz  # PyMuPDF

PT = 72.0 / 25.4                 # points per mm
FONT_PATHS = ["/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]
FONT = "arialuni"
FS, FS_HEAD = 3.5, 4.2           # font sizes, mm: capitals 2.5 and 3.0
NOTE_LH, PAD, NUM_W = 4.2, 2.0, 6.0          # the notes picture's line pitch, margin and number column (render_notes.py)
TITLE_LH, TITLE_COL = 6.5, 38.0              # the title picture's row height and label column
LINE_W = 0.35                    # frame and rule lines, mm
TITLE_HEAD = "TITLE DATA"


def font_file():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("no Arial Unicode font found: %s" % FONT_PATHS)


def wrap(text, width_mm, size_mm, font):
    """Lines of `text` no wider than width_mm at size_mm, broken between words."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.text_length(t, fontsize=size_mm * PT) <= width_mm * PT or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def notes_rows(notes, width_mm, font):
    """[(number or '', line)] for the notes, each wrapped to the text column."""
    rows = []
    for i, n in enumerate(notes):
        for j, line in enumerate(wrap(n, width_mm - 2 * PAD - NUM_W, FS, font)):
            rows.append(("%d." % (i + 1) if j == 0 else "", line))
    return rows


def notes_height(notes, width_mm, font):
    return 2 * PAD + NOTE_LH * (1 + len(notes_rows(notes, width_mm, font)))


def title_height(rows):
    return TITLE_LH * (len(rows) + 1)


def _text(page, x_mm, y_mm, s, size_mm, ffile):
    """s with its baseline at (x_mm, y_mm), page mm from the top left."""
    page.insert_text(fitz.Point(x_mm * PT, y_mm * PT), s, fontsize=size_mm * PT, fontname=FONT, fontfile=ffile)


def _baseline(top_mm, pitch_mm, size_mm):
    """The baseline that centres a row's capitals (0.718 of the size) in its pitch."""
    return top_mm + (pitch_mm + 0.718 * size_mm) / 2.0


def draw_notes(page, x0, y0, width_mm, notes, font, ffile):
    """The notes box with its top left at (x0, y0), page mm from the top left; returns its height."""
    rows = notes_rows(notes, width_mm, font)
    h = notes_height(notes, width_mm, font)
    page.draw_rect(fitz.Rect(x0 * PT, y0 * PT, (x0 + width_mm) * PT, (y0 + h) * PT), color=(0, 0, 0), width=LINE_W * PT)
    y = y0 + PAD
    _text(page, x0 + PAD, _baseline(y, NOTE_LH, FS_HEAD), "NOTES", FS_HEAD, ffile)
    for num, line in rows:
        y += NOTE_LH
        if num:
            _text(page, x0 + PAD, _baseline(y, NOTE_LH, FS), num, FS, ffile)
        _text(page, x0 + PAD + NUM_W, _baseline(y, NOTE_LH, FS), line, FS, ffile)
    return h


def draw_title(page, x0, y0, width_mm, rows, ffile):
    """The title data table with its top left at (x0, y0), page mm from the top left; returns its height."""
    h = title_height(rows)
    k = PT
    page.draw_rect(fitz.Rect(x0 * k, y0 * k, (x0 + width_mm) * k, (y0 + h) * k), color=(0, 0, 0), width=LINE_W * k)
    _text(page, x0 + PAD, _baseline(y0, TITLE_LH, FS), TITLE_HEAD, FS, ffile)
    y = y0 + TITLE_LH
    page.draw_line(fitz.Point((x0 + TITLE_COL) * k, y * k), fitz.Point((x0 + TITLE_COL) * k, (y0 + h) * k),
                   color=(0, 0, 0), width=LINE_W * k)
    for label, value in rows:
        page.draw_line(fitz.Point(x0 * k, y * k), fitz.Point((x0 + width_mm) * k, y * k), color=(0, 0, 0), width=LINE_W * k)
        _text(page, x0 + PAD, _baseline(y, TITLE_LH, FS), label, FS, ffile)
        size = FS_HEAD if label in ("PART NO.", "NAME") else FS
        _text(page, x0 + TITLE_COL + PAD, _baseline(y, TITLE_LH, size), str(value), size, ffile)
        y += TITLE_LH
    return h


def real_images(page):
    """The page's placed images with an xref (a removed one leaves an empty inline image, xref 0)."""
    return [i for i in page.get_image_info(xrefs=True) if i["xref"]]


def picture_at(page, x_mm, top_mm):
    """(xref, Rect) of the one picture whose top left corner is within 1 mm of (x_mm, top_mm), sheet mm from the
    bottom left."""
    want = (x_mm * PT, page.rect.height - top_mm * PT)
    hits = [i for i in real_images(page) if abs(i["bbox"][0] - want[0]) <= PT and abs(i["bbox"][1] - want[1]) <= PT]
    if len(hits) != 1:
        raise RuntimeError("%d pictures with their top left at (%.1f, %.1f) mm" % (len(hits), x_mm, top_mm))
    return hits[0]["xref"], fitz.Rect(hits[0]["bbox"])


LABEL_FS = 3.5 / 0.718          # a view's or a detail's label: 3.5 mm capitals (render_notes.render_label)
LABEL_LH = 6.0                  # mm between a label's lines (render_notes.LABEL_LH)
LABEL_PAD = 1.0
LABEL_LINE = re.compile(r"image (\S+)_LABEL_([A-Z0-9_]+)\.png at \(([-\d.]+), ([-\d.]+)\): True \(([\d.]+) x ([\d.]+) mm")


def label_boxes(log_text, drawing):
    """{view key: (x, top, w, h) mm} of each label picture make_drawing_ceiling.py placed, read from its log (the
    place depends on the view's extent, known only in Fusion); the log prints each picture's bottom left corner."""
    out = {}
    for m in LABEL_LINE.finditer(log_text or ""):
        if m.group(1) != drawing:
            continue
        x, bottom, w, h = (float(m.group(i)) for i in range(3, 7))
        out[m.group(2).lower()] = (x, bottom + h, w, h)
    return out


def draw_label(page, x0, y0, lines, ffile):
    """A label's lines as text from the top left corner (x0, y0), page mm from the top left, as render_label lays
    them out; returns its height."""
    for i, t in enumerate(lines):
        _text(page, x0 + LABEL_PAD, y0 + LABEL_PAD + 0.718 * LABEL_FS + i * LABEL_LH, t, LABEL_FS, ffile)
    return 2 * LABEL_PAD + 0.718 * LABEL_FS + LABEL_LH * (len(lines) - 1)


def replace_pictures(pdf, sp, width_mm, labels=None):
    """In the finished PDF `pdf` (changed in place): the notes and title pictures at sp['images'], and the label
    pictures given as {view key: ((x, top, w, h) mm, [lines])}, become text. Returns [(what, picture height mm,
    text height mm)]."""
    ffile = font_file()
    font = fitz.Font(fontfile=ffile)
    doc = fitz.open(pdf)
    page = doc[0]
    sheet_h = page.rect.height / PT
    out, boxes = [], {}
    n_images, n_paths, text0 = len(real_images(page)), len(page.get_drawings()), page.get_text()
    items = [(what, sp["images"][what]) for what in ("notes", "title")]
    items += [("label " + k, (box[0], box[1])) for k, (box, _lines) in sorted((labels or {}).items())]
    for what, (x_mm, top_mm) in items:
        _xref, rect = picture_at(page, x_mm, top_mm)
        pic_h = rect.height / PT
        if what == "notes":
            need = notes_height(sp["notes"], width_mm, font)
        elif what == "title":
            need = title_height(sp["title"])
        else:
            need = 2 * LABEL_PAD + 0.718 * LABEL_FS + LABEL_LH * (len(labels[what[6:]][1]) - 1)
        if need > pic_h + 0.5:
            raise RuntimeError("%s: the text needs %.1f mm, the picture's box is %.1f" % (what, need, pic_h))
        boxes[what] = rect
        # the picture goes from the page's content, not just hidden: a redaction a little inside its box, no fill,
        # images only (PyMuPDF 1.27 leaves an empty inline image, xref 0, where it was: nothing shows)
        page.add_redact_annot(rect + (1, 1, -1, -1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_NONE)
    if len(real_images(page)) != n_images - len(items) or len(page.get_drawings()) != n_paths or page.get_text() != text0:
        raise RuntimeError("removing the pictures changed more than them: images %d -> %d (%d removed), paths %d -> %d,"
                           " text changed %s" % (n_images, len(real_images(page)), len(items), n_paths,
                                                 len(page.get_drawings()), page.get_text() != text0))
    for what, rect in boxes.items():
        if min(page.get_pixmap(dpi=50, clip=rect).samples) < 250:
            raise RuntimeError("%s: something still shows in the picture's box after removing it" % what)
    for what, (x_mm, top_mm) in items:
        pic_h = boxes[what].height / PT
        y0 = sheet_h - top_mm
        if what == "notes":
            got = draw_notes(page, x_mm, y0, width_mm, sp["notes"], font, ffile)
        elif what == "title":
            got = draw_title(page, x_mm, y0, width_mm, sp["title"], ffile)
        else:
            got = draw_label(page, x_mm, y0, labels[what[6:]][1], ffile)
        out.append((what, pic_h, got))
    doc.subset_fonts()          # embed only the letters used (the whole Arial Unicode is about 15 MB)
    tmp = pdf + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf)
    return out
