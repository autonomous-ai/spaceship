#!/usr/bin/env python3
"""Remove the value of a title block field (default "Created by") from a PDF.

    python3 tools/fusion/pdf_clear_field.py IN.pdf OUT.pdf [--label "Created by"] [--title T] [--status S]

Fusion fills "Created by" with the Fusion account holder's name, and its API
can't change title block text. The repo is public, so this removes that value
before a drawing is committed. It finds the label, takes the words on the
line below it up to the next field value in the same cell (the date), and
redacts them with PyMuPDF: the text is removed from the page content, not
covered. Table lines and all other text are kept. It then re-reads the
output and fails if any word is still there. It never prints the removed
words. Needs PyMuPDF (import fitz).

It then fills the title block's DWG No., Rev., Document status and Title
from the drawing's file name and the master BOM (pdf_title_block.py, which
says how), so every team's finish step fills it; --title and --status set
those two instead, and --no-title-block leaves the block as it is.
"""

import argparse
import os
import re
import sys

import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_title_block as ptb  # noqa: E402  this checkout's copy, next to this file

DATE = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")


def field_words(page, label):
    hits = page.search_for(label)
    if not hits:
        raise SystemExit("label %r not found" % label)
    lab = hits[0]
    words = page.get_text("words")      # x0, y0, x1, y1, word, block, line, n
    below = [w for w in words if w[1] >= lab.y1 - 1 and w[1] <= lab.y1 + 25 and w[0] >= lab.x0 - 1]
    if not below:
        return lab, []
    # only the first text line under the label (the field value), not the
    # next row's labels
    top = min(w[1] for w in below)
    row = [w for w in below if abs(w[1] - top) < 2.0]
    # stop at the date that shares the cell, or 200 pt to the right. Fusion writes it with one or two digits
    # for the day and the month (1/11/26 and 31/10/26 alike): with two required, a one-digit day's date was
    # taken as part of the name and removed, and the re-read then took the next row's labels as left over
    dates = [w for w in row if DATE.fullmatch(w[4])]
    right = min([d[0] for d in dates] + [lab.x0 + 200])
    return lab, [w for w in row if w[2] <= right - 0.5]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--label", default="Created by")
    ap.add_argument("--title", help="title block: the title, instead of the part's name in the master BOM")
    ap.add_argument("--status", help="title block: the document status, instead of the master BOM's")
    ap.add_argument("--no-title-block", action="store_true", help="leave the title block's other fields as they are")
    o = ap.parse_args(argv)
    values = None if o.no_title_block else ptb.values_for(o.src, o.dst, o.title, o.status)
    doc = fitz.open(o.src)
    removed = filled = 0
    for page in doc:
        if not page.search_for(o.label):
            continue
        _lab, words = field_words(page, o.label)
        for w in words:
            page.add_redact_annot(fitz.Rect(w[:4]), fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        removed += len(words)
    for page in doc:
        if values and ptb.fill_page(page, values):
            filled += 1
    doc.save(o.dst, garbage=3, deflate=True)
    doc.close()
    # check the output
    chk = fitz.open(o.dst)
    left = 0
    missing = []
    for i, page in enumerate(chk):
        if page.search_for(o.label):
            left += len(field_words(page, o.label)[1])
        if values:
            missing += ["page %d %s" % (i + 1, f) for f in ptb.check_page(page, values)]
    chk.close()
    print("removed %d word(s) from the %r field; left after re-read: %d" % (removed, o.label, left))
    if values and filled:
        print("title block filled on %d page(s): DWG No. %s, Rev. %s, %s, %s%s" % (
            filled, values["DWG No."], values["Rev."], values["Document status"], values["Title"],
            "; MISSING after the re-read: %s" % ", ".join(missing) if missing else ""))
    elif not o.no_title_block:
        print("title block left as it is (%s)" % ("no NNNNNN_REV_NAME_DWG file name" if not values else "no stock title block found"))
    return 0 if removed and not left and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
