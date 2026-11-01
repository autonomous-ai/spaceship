#!/usr/bin/env python3
"""Offline tests for pdf_title_block.py and its use in pdf_clear_field.py: no Fusion needed, PyMuPDF only.

    python3 tools/fusion/test_pdf_title_block.py

Each test writes an A3 page laid out like Fusion's stock title block (its labels, the line above the Title and
DWG No. row, the dividers in the Rev. row, the design's file name under Title, a made-up name under Created by),
runs the tool and reads the result back.
"""

import contextlib
import csv
import io
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fitz  # noqa: E402  PyMuPDF
import pdf_clear_field as pcf  # noqa: E402
import pdf_title_block as ptb  # noqa: E402

NAME = "Testa Personne"          # a made-up name, standing in for the account holder's
LABELS = [  # label, x, baseline: the stock block's places on an A3 sheet (points)
    ("Dept.", 654.8, 688.6), ("Technical reference", 722.8, 688.6), ("Created by", 819.2, 688.6),
    ("Approved by", 992.0, 688.6), ("Document type", 819.2, 716.9), ("Document status", 992.0, 716.9),
    ("Title", 819.2, 745.3), ("DWG No.", 992.0, 745.3), ("Rev.", 992.0, 793.4), ("Date of issue", 1020.4, 793.4),
    ("Sheet", 1122.5, 793.4)]


def sheet(path, cad_name="211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD", block=True):
    doc = fitz.open()
    page = doc.new_page(width=1191, height=842)
    page.insert_text((60, 60), "NOTES: TITLE AND REV. ARE IN THE TITLE BLOCK", fontsize=9)  # look-alike words elsewhere
    if block:
        for text, x, y in LABELS:
            page.insert_text((x, y), text, fontsize=7)
        page.draw_line((816.3, 737.2), (1162.1, 737.2))
        page.draw_line((989.2, 785.4), (1162.1, 785.4))
        page.draw_line((1017.6, 785.4), (1017.6, 813.7))
        page.draw_line((1119.6, 785.4), (1119.6, 813.7))
        page.insert_text((819.2, 767.0), cad_name, fontsize=10)  # longer than its cell, as a long design name can be
        page.insert_text((819.2, 704.0), NAME, fontsize=12)              # as Fusion prints it, beside the date
        page.insert_text((940.1, 704.0), "1/11/26", fontsize=12)
    doc.save(path)
    doc.close()


def bom(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["part_number", "name", "product_status"])
        w.writerows(rows)
    return path


def quiet(fn, *a, **k):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = fn(*a, **k)
    return rc, out.getvalue()


class TitleBlock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "raw.pdf")
        self.dst = os.path.join(self.tmp, "211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG.pdf")
        self.bom = bom(os.path.join(self.tmp, "bom.csv"),
                       [["211101", "WALL - PANEL FRAME - SIDE LOWER - LH", "DRAFT"],
                        ["111103", "BASE - BAND TUBE - BACK", "HOLD (BASE: band wall)"]])

    def cell_text(self, field):
        page = fitz.open(self.dst)[0]
        return " ".join(page.get_text("text", clip=ptb.cells(page)[field]).split())

    def test_fills_number_revision_status_and_title(self):
        sheet(self.src)
        rc, out = quiet(ptb.main, [self.src, self.dst, "--bom", self.bom])
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.cell_text("DWG No."), "211101")
        self.assertEqual(self.cell_text("Rev."), "P01")
        self.assertEqual(self.cell_text("Document status"), "DRAFT")
        self.assertEqual(self.cell_text("Title"), "WALL - PANEL FRAME - SIDE LOWER - LH")
        text = fitz.open(self.dst)[0].get_text()
        self.assertNotIn("_CAD", text)                        # the design's file name is gone from Title
        self.assertIn("NOTES: TITLE AND REV.", text)          # nothing else is touched

    def test_letters_are_at_least_2_5_mm(self):
        sheet(self.src)
        quiet(ptb.main, [self.src, self.dst, "--bom", self.bom])
        page = fitz.open(self.dst)[0]
        cells = ptb.cells(page)
        for field, rect in cells.items():
            sizes = [s["size"] for b in page.get_text("dict", clip=rect)["blocks"] for ln in b.get("lines", [])
                     for s in ln["spans"] if s["text"].strip() and s["size"] > 7.5]    # its label is 7 pt
            self.assertTrue(sizes and min(sizes) >= 10.0, (field, sizes))       # 10 pt: 2.5 mm capitals

    def test_status_hold_from_the_bom(self):
        dst = os.path.join(self.tmp, "111103_P01_BASE-BAND-TUBE-BACK_DWG.pdf")
        sheet(self.src, "111103_P01_BASE-BAND-TUBE-BACK_CAD")
        quiet(ptb.main, [self.src, dst, "--bom", self.bom])
        self.dst = dst
        self.assertEqual(self.cell_text("Document status"), "HOLD")
        self.assertEqual(self.cell_text("Title"), "BASE - BAND TUBE - BACK")

    def test_title_and_status_given(self):
        sheet(self.src)
        quiet(ptb.main, [self.src, self.dst, "--bom", self.bom, "--title", "Family: 211101 to 211104",
                         "--status", "review"])
        self.assertEqual(self.cell_text("Title"), "FAMILY: 211101 TO 211104")
        self.assertEqual(self.cell_text("Document status"), "REVIEW")

    def test_part_not_in_the_bom_takes_the_file_name(self):
        dst = os.path.join(self.tmp, "999901_P02_POD-SAMPLE-PART_DWG.pdf")
        sheet(self.src, "999901_P02_POD-SAMPLE-PART_CAD")
        quiet(ptb.main, [self.src, dst, "--bom", self.bom])
        self.dst = dst
        self.assertEqual(self.cell_text("Title"), "POD SAMPLE PART")
        self.assertEqual(self.cell_text("Rev."), "P02")
        self.assertEqual(self.cell_text("Document status"), "DRAFT")

    def test_no_part_number_in_the_name_leaves_it(self):
        sheet(self.src)
        dst = os.path.join(self.tmp, "out.pdf")
        rc, out = quiet(ptb.main, [self.src, dst, "--bom", self.bom])
        self.assertEqual(rc, 0)
        self.assertIn("left as it is", out)
        self.assertFalse(os.path.exists(dst))

    def test_a_page_without_the_block_is_left(self):
        sheet(self.src, block=False)
        rc, out = quiet(ptb.main, [self.src, self.dst, "--bom", self.bom])
        self.assertEqual(rc, 0, out)
        self.assertIn("0 page(s) filled", out)

    def test_the_finish_step_clears_the_name_and_fills_the_block(self):
        sheet(self.src)
        old = ptb.BOM
        ptb.BOM = self.bom
        try:
            rc, out = quiet(pcf.main, [self.src, self.dst])
        finally:
            ptb.BOM = old
        self.assertEqual(rc, 0, out)
        self.assertIn("left after re-read: 0", out)
        self.assertIn("title block filled on 1 page(s)", out)
        text = fitz.open(self.dst)[0].get_text()
        for w in NAME.split():
            self.assertNotIn(w, text)
            self.assertNotIn(w, out)
        self.assertIn("1/11/26", text)
        self.assertEqual(self.cell_text("DWG No."), "211101")

    def test_the_creator_sits_on_the_date_line_in_its_cell(self):
        sheet(self.src)
        ptb.fill(self.src, self.dst, ptb.values_for(self.src, self.dst, bom=self.bom))
        page = fitz.open(self.dst)[0]
        lab = page.search_for("Created by")[0]
        auto = page.search_for("Autonomous")
        self.assertEqual(len(auto), 1)
        a, date = auto[0], page.search_for("1/11/26")[0]
        self.assertAlmostEqual(a.x0, lab.x0, delta=1.0)                # left in the cell
        self.assertAlmostEqual(a.y1, date.y1, delta=1.0)               # on the date's line
        self.assertLess(a.x1, date.x0)                                  # and left of it
        self.assertGreaterEqual(a.y1 - a.y0, 10.0 * 0.718)             # never under 2.5 mm capitals
        self.assertNotIn("Testa", page.get_text())
        self.assertEqual(fitz.open(self.dst).metadata["author"], "Autonomous")

    def test_filling_twice_writes_every_value_once(self):
        sheet(self.src)
        values = ptb.values_for(self.src, self.dst, bom=self.bom)
        ptb.fill(self.src, self.dst, values)
        again = self.dst.replace(".pdf", "-again.pdf")
        ptb.fill(self.dst, again, values)
        text = fitz.open(again)[0].get_text()
        for v in ("211101", "P01", "DRAFT", "Autonomous"):
            self.assertEqual(text.count(v), 1, v)
        self.assertEqual(self.cell_text_of(again, "DWG No."), "211101")

    def cell_text_of(self, path, field):
        page = fitz.open(path)[0]
        return " ".join(page.get_text("text", clip=ptb.cells(page)[field]).split())

    def test_the_finish_step_can_leave_the_block(self):
        sheet(self.src)
        rc, out = quiet(pcf.main, [self.src, self.dst, "--no-title-block"])
        self.assertEqual(rc, 0, out)
        self.assertIn("_CAD", fitz.open(self.dst)[0].get_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
