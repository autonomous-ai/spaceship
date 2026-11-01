#!/usr/bin/env python3
"""Offline tests for pdf_clear_field.py: no Fusion needed, PyMuPDF only.

    python3 tools/fusion/test_pdf_clear_field.py

Each test writes a small PDF laid out like Fusion's title block (the "Created by" label, the value line under
it with the name and the date, and the next row's labels close below), runs the tool and reads the result back.
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fitz  # noqa: E402  PyMuPDF
import pdf_clear_field as pcf  # noqa: E402

NAME = "Testa Personne"          # a made-up name, standing in for the account holder's


def title_block(path, date):
    doc = fitz.open()
    page = doc.new_page(width=1190, height=842)
    page.insert_text((100, 100), "Created by", fontsize=7)
    page.insert_text((100, 110), NAME, fontsize=7)          # the value line, about 8 pt under the label
    page.insert_text((220, 110), date, fontsize=7)          # the date in the same cell
    page.insert_text((100, 128), "Approved by", fontsize=7)  # the next row, about 19 pt under the label
    page.insert_text((220, 128), "Checked by", fontsize=7)
    doc.save(path)
    doc.close()


def run(src, dst):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = pcf.main([src, dst])
    return rc, out.getvalue()


class ClearField(unittest.TestCase):
    def check(self, date):
        tmp = tempfile.mkdtemp()
        src, dst = os.path.join(tmp, "in.pdf"), os.path.join(tmp, "out.pdf")
        title_block(src, date)
        rc, out = run(src, dst)
        text = fitz.open(dst)[0].get_text()
        self.assertEqual(rc, 0, out)
        self.assertIn("removed 2 word(s)", out)
        self.assertIn("left after re-read: 0", out)
        for w in NAME.split():
            self.assertNotIn(w, text)
            self.assertNotIn(w, out)                       # the tool never prints the removed words
        self.assertIn(date, text)                          # the date bounds the field and stays
        self.assertIn("Approved by", text)                 # the next row is never touched
        self.assertIn("Checked by", text)

    def test_two_digit_day(self):
        self.check("31/10/26")

    def test_one_digit_day(self):
        # Fusion's date on the 1st to the 9th of a month: with two digits required, the date was removed as
        # part of the name and the re-read took the next row's labels as left over (exit 1)
        self.check("1/11/26")

    def test_one_digit_day_and_month(self):
        self.check("5/3/2027")

    def test_date_pattern(self):
        for ok in ("1/11/26", "31/10/26", "5/3/2027", "01/01/26"):
            self.assertTrue(pcf.DATE.fullmatch(ok), ok)
        for bad in ("Approved", "26", "1-11-26", "111/1/26"):
            self.assertFalse(pcf.DATE.fullmatch(bad), bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
