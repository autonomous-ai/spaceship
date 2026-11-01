#!/usr/bin/env python3
"""Replace the value of a title block field (default "Created by") in a PDF with "Autonomous".

    python3 tools/fusion/pdf_clear_field.py IN.pdf OUT.pdf [--label "Created by"] [--title T] [--status S]
    python3 tools/fusion/pdf_clear_field.py IN.pdf OUT.pdf --restamp --no-title-block   (a committed PDF)

Fusion fills "Created by" with the Fusion account holder's name, and its API
can't change title block text. The repo is public, and the owner wants every
drawing to name Autonomous as its creator, never a person (2026-11-01). So
this finds the label, takes the words on the value line under it up to the
date that shares the cell, redacts them with PyMuPDF (the text is removed
from the page content, not covered), and writes "Autonomous" there; the date,
table lines and all other text are kept. It sets the PDF's author metadata to
"Autonomous". It then re-reads the output and fails unless the field reads
exactly "Autonomous". It never prints the removed words. Only the value line
is read: words whose box ends 5 to 23 pt under the label's (on an emptied
field, "the first line under the label" was the next row's labels).

--restamp is for drawings already committed: their field may be empty or
stamped already, so nothing need be removed, and a PDF without Fusion's
title block (drawgen's, ELECTRICAL's) passes with only its author set.
Needs PyMuPDF (import fitz).

It then fills the title block's DWG No., Rev., Document status and Title
from the drawing's file name and the master BOM (pdf_title_block.py, which
says how), so every team's finish step fills it; --title and --status set
those two instead, and --no-title-block leaves the block as it is.
"""

import argparse
import os
import sys

import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_title_block as ptb  # noqa: E402  this checkout's copy, next to this file

DATE = ptb.DATE    # Fusion writes the day and the month with one or two digits (1/11/26 and 31/10/26 alike)


def field_words(page, label):
    """(label box, the value line's words left of the date). The date bounds the field and stays; with two
    digits required, a one-digit day's date was once taken as part of the name and removed."""
    found = ptb.created_by(page, label)
    if found is None:
        raise SystemExit("label %r not found" % label)
    return found[0], found[1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--label", default="Created by")
    ap.add_argument("--title", help="title block: the title, instead of the part's name in the master BOM")
    ap.add_argument("--status", help="title block: the document status, instead of the master BOM's")
    ap.add_argument("--no-title-block", action="store_true", help="leave the title block's other fields as they are")
    ap.add_argument("--creator", default=ptb.CREATOR, help="what the field and the PDF's author say (default %(default)r)")
    ap.add_argument("--restamp", action="store_true",
                    help="a committed drawing: the field may be empty or stamped already, and a PDF without the "
                         "label passes with only its author set")
    o = ap.parse_args(argv)
    values = None if o.no_title_block else ptb.values_for(o.src, o.dst, o.title, o.status)
    stamp = o.creator.split()
    doc = fitz.open(o.src)
    removed = filled = labelled = 0
    for page in doc:
        if not ptb.label_hits(page, o.label):
            continue
        labelled += 1
        _lab, words = field_words(page, o.label)
        removed += len([w for w in words if w[4] not in stamp])          # an earlier stamp isn't counted
        ptb.stamp_creator(page, o.creator, o.label)
    ptb.set_author(doc, o.creator)
    for page in doc:
        if values and ptb.fill_page(page, values):
            filled += 1
    doc.save(o.dst, garbage=3, deflate=True)
    doc.close()
    # check the output: each field reads exactly the creator, and the author is set
    chk = fitz.open(o.dst)
    left = wrong = 0
    missing = []
    for i, page in enumerate(chk):
        if ptb.label_hits(page, o.label):
            got = [w[4] for w in field_words(page, o.label)[1]]
            left += len([w for w in got if w not in stamp])
            wrong += got != stamp
        if values:
            missing += ["page %d %s" % (i + 1, f) for f in ptb.check_page(page, values)]
    author = (chk.metadata or {}).get("author")
    chk.close()
    print("removed %d word(s) from the %r field on %d page(s); left after re-read: %d; the field reads %r%s; "
          "author %r" % (removed, o.label, labelled, left, o.creator,
                         "" if not wrong else " on %d page(s) only" % (labelled - wrong), author))
    if values and filled:
        print("title block filled on %d page(s): DWG No. %s, Rev. %s, %s, %s%s" % (
            filled, values["DWG No."], values["Rev."], values["Document status"], values["Title"],
            "; MISSING after the re-read: %s" % ", ".join(missing) if missing else ""))
    elif not o.no_title_block:
        print("title block left as it is (%s)" % ("no NNNNNN_REV_NAME_DWG file name" if not values else "no stock title block found"))
    found_it = labelled and (removed or o.restamp)     # a fresh export always has the name to remove
    return 0 if (found_it or (o.restamp and not labelled)) and not left and not wrong and not missing \
        and author == o.creator else 1


if __name__ == "__main__":
    sys.exit(main())
