#!/usr/bin/env python3
"""Fill a Fusion drawing PDF's title block: drawing number, revision, document status, title and creator.

    python3 tools/fusion/pdf_title_block.py IN.pdf OUT.pdf [--title T] [--status S] [--bom CSV]

Fusion's stock title block leaves DWG No., Rev. and Document status blank and prints the design's file name
under Title, and its API can't set them (tools/fusion/README.md). This writes them into the exported PDF as
real text in their cells, the way the teams add their notes:

- DWG No. and Rev. from the drawing's file name, NNNNNN_REV_NAME_DWG (conventions section 7: the revision in
  the file name, the title block and the BOM is the same);
- Title: the part's name in the master BOM (v2/04-BOM/100000_P01_POD-MASTER_BOM.csv), else the file name's
  NAME part, or --title; the design's file name that Fusion printed there is removed;
- Document status: the part's status in the master BOM (DRAFT, HOLD and so on, conventions section 9), else
  DRAFT, or --status;
- Created by: "Autonomous" (the owner, 2026-11-01: every drawing names Autonomous as its creator, never a
  person), in place of the account holder's name Fusion prints there; the date stays. The PDF's author
  metadata is set to it too.

It finds the cells by their labels, so any sheet size works, then re-reads the output and fails if a value
isn't in its cell. Each cell is emptied before it is written, so running it again changes nothing. A page
with no Fusion title block is left as it is. pdf_clear_field.py runs this after it clears "Created by", so
every team's finish step fills the block. Needs PyMuPDF (import fitz).
"""

import argparse
import csv
import os
import re
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.normpath(os.path.join(HERE, "..", "..", "v2", "04-BOM", "100000_P01_POD-MASTER_BOM.csv"))
FILE_NAME = re.compile(r"(\d{6})_([A-Z]\d{2})_(.+?)_DWG")
STATUSES = ("DRAFT", "HOLD", "REVIEW", "FA-APPROVED", "PRODUCTION-APPROVED")
FONT = "helv"
# pt, the largest that fits its cell; never under 10 pt, whose capitals are 2.5 mm (Helvetica's are 0.718 of
# the size), the smallest letters a drawing may use (ISO 3098; the D-114 visual pass)
SIZES = {"DWG No.": (18.0, 16.0, 14.0, 12.0, 10.0), "Title": (14.0, 12.0, 11.0, 10.0),
         "Rev.": (14.0, 12.0, 11.0, 10.0), "Document status": (14.0, 12.0, 11.0, 10.0)}
ONE_LINE = ("DWG No.", "Rev.", "Document status")   # set on one baseline at the cell's foot, as Fusion's own values
# The owner (2026-11-01): every drawing names Autonomous as its creator, never a person. Fusion prints the
# account holder's name under "Created by"; the finish step removes it and writes this instead, and sets the
# PDF's author to it.
CREATOR = "Autonomous"
CREATED_BY = "Created by"
DATE = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")
# The Created by value line on Fusion's stock block, measured on a fresh export (2706.1, A2, 2026-11-01): its
# baseline 14.54 pt under the bottom of the label's box, at 13.86 pt (the size Fusion prints the name and date);
# the next row's labels end 28.3 pt under it. The block is the same size on every sheet. A word is on the value
# line when its box ends 5 to 23 pt under the label's: never the next row (on a field that was emptied before,
# "the first line under the label" was the next row's labels).
CREATED_VALUE_DY, CREATED_VALUE_SIZE = 14.54, 13.86
CREATED_BAND = (5.0, 23.0)
CREATOR_SIZES = (13.86, 12.0, 11.0, 10.0)
META_KEYS = ("title", "subject", "keywords", "creator", "producer", "creationDate", "modDate", "trapped")


def parse_name(*paths):
    """(number, revision, NAME) from the first path named NNNNNN_REV_NAME_DWG..., or None."""
    for p in paths:
        m = FILE_NAME.search(os.path.basename(p or ""))
        if m:
            return m.group(1), m.group(2), m.group(3)
    return None


def bom_row(number, bom=BOM):
    """(name, status) of the part in the master BOM, or (None, None)."""
    if not bom or not os.path.exists(bom):
        return None, None
    with open(bom, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if (r.get("part_number") or "").strip() == number and (r.get("name") or "").strip():
                word = re.split(r"[\s;:,(]", (r.get("product_status") or "").strip().upper())[0]
                return r["name"].strip(), (word if word in STATUSES else None)
    return None, None


def values_for(src, dst, title=None, status=None, bom=BOM):
    """{field: text} for the title block, or None when the file name doesn't give the number."""
    parsed = parse_name(dst, src)
    if not parsed:
        return None
    number, rev, name = parsed
    bom_name, bom_status = bom_row(number, bom)
    return {"DWG No.": number, "Rev.": rev,
            "Document status": (status or bom_status or "DRAFT").upper(),
            "Title": (title or bom_name or name.replace("-", " ")).upper()}


def _label(page, text, row_of=None, left_of=None):
    """The first hit of a label, optionally on the same row as another label and to its left."""
    for r in page.search_for(text):
        if row_of is not None and abs(r.y0 - row_of.y0) > 2.0:
            continue
        if left_of is not None and r.x0 >= left_of.x0:
            continue
        return r
    return None


def cells(page):
    """{field: fitz.Rect} for the values of DWG No., Rev., Document status and Title, or {} when the page has
    no Fusion title block. Rows and columns come from the labels; the block's right and bottom edges from its
    own lines, with fallbacks at the stock block's sizes."""
    dwg = _label(page, "DWG No.")
    if dwg is None:
        return {}
    title = _label(page, "Title", row_of=dwg, left_of=dwg)
    status = None
    for r in page.search_for("Document status"):
        if abs(r.x0 - dwg.x0) < 2.0 and r.y1 < dwg.y0:
            status = r
    rev = None
    for r in page.search_for("Rev."):
        if abs(r.x0 - dwg.x0) < 2.0 and r.y0 > dwg.y1:
            rev = r
            break
    if not (title and status and rev):
        return {}
    date = _label(page, "Date of issue", row_of=rev)
    right, bottom = dwg.x0 + 170.0, rev.y1 + 19.0
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] != "l":
                continue
            p, q = it[1], it[2]
            if abs(p.y - q.y) < 0.5 and dwg.y0 - 6 < p.y < dwg.y0 and max(p.x, q.x) > dwg.x0 + 20:
                right = max(p.x, q.x)                                   # the line above the DWG No. row
            if abs(p.x - q.x) < 0.5 and rev.x0 < p.x < right and min(p.y, q.y) < rev.y0 and max(p.y, q.y) > rev.y1:
                bottom = max(p.y, q.y)                                  # a divider in the Rev. row
    return {
        "DWG No.": fitz.Rect(dwg.x0, dwg.y1 + 1, right - 3, rev.y0 - 4),
        "Document status": fitz.Rect(status.x0, status.y1 + 1, right - 3, dwg.y0 - 4),
        "Rev.": fitz.Rect(rev.x0, rev.y1 + 1, (date.x0 - 4) if date else rev.x0 + 22, bottom - 2),
        "Title": fitz.Rect(title.x0, title.y1 + 1, dwg.x0 - 5, bottom - 2),
    }


def redact_word(page, w):
    """Mark one word (a get_text("words") entry) for removal through a thin strip across its middle: PyMuPDF
    removes every character whose box touches the area, and a word's full box (a large value's ascenders) can
    reach the label above it, which then went too."""
    mid = (w[1] + w[3]) / 2.0
    page.add_redact_annot(fitz.Rect(w[0], mid - 1.0, w[2], mid + 1.0), fill=False)


def label_hits(page, label):
    """The places of `label` written exactly so, case included: PyMuPDF's search ignores case, and drawgen's
    own block says "CREATED BY", which must never be taken for Fusion's "Created by"."""
    return [r for r in page.search_for(label)
            if page.get_textbox(r).split("\n")[0].strip() == label]   # its own line; the value under it can touch


def created_by(page, label=CREATED_BY):
    """(label box, value words, date word or None) on the Created by value line, or None when the page has no
    such label. Value words are the line's words left of the date (or within 200 pt of the label)."""
    hits = label_hits(page, label)
    if not hits:
        return None
    lab = hits[0]
    line = [w for w in page.get_text("words") if lab.x0 - 1 <= w[0] <= lab.x0 + 200 and w[1] > lab.y0 + 1
            and CREATED_BAND[0] <= w[3] - lab.y1 <= CREATED_BAND[1]]
    dates = sorted((w for w in line if DATE.fullmatch(w[4])), key=lambda w: w[0])
    right = dates[0][0] if dates else lab.x0 + 200
    return lab, [w for w in line if w[2] <= right - 0.5], (dates[0] if dates else None)


def _cell_right(page, lab):
    """x of the cell's right line next to the label (the vertical line across it), or a stock-size guess."""
    xs = [it[1].x for d in page.get_drawings() for it in d["items"] if it[0] == "l"
          and abs(it[1].x - it[2].x) < 0.5 and lab.x0 + 20 < it[1].x < lab.x0 + 220
          and min(it[1].y, it[2].y) < lab.y0 and max(it[1].y, it[2].y) > lab.y1]
    return min(xs) if xs else lab.x0 + 165.0


def stamp_creator(page, creator=CREATOR, label=CREATED_BY):
    """Put `creator` on the Created by value line, after removing the words there (the account holder's name,
    or an earlier stamp); the date stays. Returns the size written, or None when the page has no such label.
    The baseline and size come from the line's own text (the date), else from the stock block's."""
    found = created_by(page, label)
    if found is None:
        return None
    lab, words, date = found
    spans = [sp for b in page.get_text("dict")["blocks"] for ln in b.get("lines", []) for sp in ln["spans"]
             if sp["text"].strip() and lab.x0 - 1 <= sp["bbox"][0] <= lab.x0 + 200 and sp["bbox"][1] > lab.y0 + 1
             and CREATED_BAND[0] <= sp["bbox"][3] - lab.y1 <= CREATED_BAND[1]]
    spans.sort(key=lambda sp: not DATE.fullmatch(sp["text"].strip()))   # the date's line and size first
    base, size0 = (spans[0]["origin"][1], spans[0]["size"]) if spans else (lab.y1 + CREATED_VALUE_DY,
                                                                            CREATED_VALUE_SIZE)
    for w in words:
        redact_word(page, w)
    if words:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    right = (date[0] - 4.0) if date else _cell_right(page, lab) - 3.0
    first = max(10.0, min(size0, CREATOR_SIZES[0]))
    for size in (first,) + tuple(s for s in CREATOR_SIZES if s < first):
        if fitz.Font(FONT).text_length(creator, fontsize=size) <= right - lab.x0:
            page.insert_text((lab.x0, base), creator, fontsize=size, fontname=FONT)
            return size
    raise SystemExit("title block: %r doesn't fit the %s cell" % (creator, label))


def set_author(doc, creator=CREATOR):
    """The PDF's author metadata: `creator`; the other fields are kept."""
    meta = {k: v for k, v in (doc.metadata or {}).items() if k in META_KEYS and v}
    meta["author"] = creator
    doc.set_metadata(meta)


def write(page, rect, text, sizes, one_line=False):
    """Put text in rect at the largest size that fits; return the size, or None if none fits. One line sits on a
    baseline near the cell's foot (its capitals, 0.718 of the size, and descenders inside the cell); the title
    wraps inside its cell."""
    for size in sizes:
        if one_line:
            if fitz.Font(FONT).text_length(text, fontsize=size) <= rect.width and 0.97 * size <= rect.height:
                page.insert_text((rect.x0, rect.y1 - 0.25 * size), text, fontsize=size, fontname=FONT)
                return size
        elif page.insert_textbox(rect, text, fontsize=size, fontname=FONT) >= 0:
            return size
    return None


def fill_page(page, values):
    """Fill one page's title block; returns {field: size} written, or {} when the page has none. Each cell is
    emptied first (the design's file name Fusion printed under Title, or an earlier fill), so a second run
    writes every value once."""
    found = cells(page)
    if not found:
        return {}
    for c in found.values():              # whole words that start in the cell, even if they run past it
        for w in page.get_text("words"):
            if c.x0 - 1 <= w[0] < c.x1 and w[1] < c.y1 and w[3] > c.y0 and (w[1] + w[3]) / 2.0 > c.y0:
                redact_word(page, w)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    out = {}
    for field, rect in found.items():
        size = write(page, rect, values[field], SIZES[field], field in ONE_LINE)
        if size is None:
            raise SystemExit("title block: %r doesn't fit its cell" % values[field])
        out[field] = size
    return out


def check_page(page, values):
    """Fields whose value isn't in its cell after a re-read."""
    found = cells(page)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    return [f for f, rect in found.items() if norm(values[f]) not in norm(page.get_text("text", clip=rect + (-2, -2, 2, 2)))]


def fill(src, dst, values):
    """Fill every page with a title block; returns the number of pages filled. Raises SystemExit on a miss."""
    doc = fitz.open(src)
    pages = sum(1 for page in doc if fill_page(page, values))
    for page in doc:
        stamp_creator(page)
    set_author(doc)
    doc.save(dst, garbage=3, deflate=True)
    doc.close()
    chk = fitz.open(dst)
    missing = [(i + 1, f) for i, page in enumerate(chk) for f in check_page(page, values)]
    chk.close()
    if missing:
        raise SystemExit("title block: not found after the re-read: %s" % missing)
    return pages


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--title", help="the title, instead of the part's name in the master BOM")
    ap.add_argument("--status", help="the document status, instead of the master BOM's")
    ap.add_argument("--bom", default=BOM, help="the master BOM CSV (default: the repo's)")
    o = ap.parse_args(argv)
    values = values_for(o.src, o.dst, o.title, o.status, o.bom)
    if values is None:
        print("title block: no NNNNNN_REV_NAME_DWG file name, left as it is")
        return 0
    pages = fill(o.src, o.dst, values)
    print("title block: %d page(s) filled: DWG No. %s, Rev. %s, %s, %s" % (
        pages, values["DWG No."], values["Rev."], values["Document status"], values["Title"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
