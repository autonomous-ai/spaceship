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


def title_block(path, date, name=NAME, label=True):
    doc = fitz.open()
    page = doc.new_page(width=1190, height=842)
    if label:
        page.insert_text((100, 100), "Created by", fontsize=7)
    if name:
        page.insert_text((100, 110), name, fontsize=7)      # the value line, about 8 pt under the label
    page.insert_text((220, 110), date, fontsize=7)          # the date in the same cell
    page.insert_text((100, 128), "Approved by", fontsize=7)  # the next row, about 19 pt under the label
    page.insert_text((220, 128), "Checked by", fontsize=7)
    doc.save(path)
    doc.close()


def run(src, dst, *more):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = pcf.main([src, dst] + list(more))
    return rc, out.getvalue()


def field(path):
    page = fitz.open(path)[0]
    return [w[4] for w in pcf.field_words(page, "Created by")[1]]


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
        self.assertEqual(field(dst), ["Autonomous"])       # the owner: Autonomous, never a person
        self.assertEqual(fitz.open(dst).metadata["author"], "Autonomous")

    def test_two_digit_day(self):
        self.check("31/10/26")

    def test_one_digit_day(self):
        # Fusion's date on the 1st to the 9th of a month: with two digits required, the date was removed as
        # part of the name and the re-read took the next row's labels as left over (exit 1)
        self.check("1/11/26")

    def test_one_digit_day_and_month(self):
        self.check("5/3/2027")

    def files(self):
        tmp = tempfile.mkdtemp()
        return os.path.join(tmp, "in.pdf"), os.path.join(tmp, "out.pdf"), os.path.join(tmp, "again.pdf")

    def test_a_second_run_changes_nothing(self):
        src, dst, again = self.files()
        title_block(src, "31/10/26")
        self.assertEqual(run(src, dst)[0], 0)
        rc, out = run(dst, again, "--restamp")
        self.assertEqual(rc, 0, out)
        self.assertIn("removed 0 word(s)", out)                 # the earlier stamp isn't counted as removed
        self.assertEqual(field(again), ["Autonomous"])          # once, not twice
        self.assertEqual(fitz.open(again)[0].get_text().count("Autonomous"), 1)

    def test_an_emptied_field_is_stamped_and_the_next_row_kept(self):
        # a committed drawing whose name was removed before: "the first line under the label" was the
        # next row's labels, so clearing it again would have removed "Approved by" and "Checked by"
        src, dst, _ = self.files()
        title_block(src, "31/10/26", name=None)
        rc, out = run(src, dst, "--restamp")
        self.assertEqual(rc, 0, out)
        text = fitz.open(dst)[0].get_text()
        for keep in ("Approved by", "Checked by", "31/10/26"):
            self.assertIn(keep, text)
        self.assertEqual(field(dst), ["Autonomous"])

    def test_a_fresh_export_must_have_had_a_name_to_remove(self):
        # without --restamp, nothing to remove means the name sits somewhere it wasn't looked for
        src, dst, _ = self.files()
        title_block(src, "31/10/26", name=None)
        self.assertEqual(run(src, dst)[0], 1)

    def test_a_pdf_without_the_label_gets_only_its_author_with_restamp(self):
        src, dst, _ = self.files()
        title_block(src, "31/10/26", name="drawgen", label=False)   # drawgen's or ELECTRICAL's own block
        rc, out = run(src, dst, "--restamp")
        self.assertEqual(rc, 0, out)
        self.assertEqual(fitz.open(dst).metadata["author"], "Autonomous")
        self.assertIn("drawgen", fitz.open(dst)[0].get_text())     # its own sheet is left as it is
        self.assertEqual(run(src, dst)[0], 1)                      # the finish step needs the label

    def test_date_pattern(self):
        for ok in ("1/11/26", "31/10/26", "5/3/2027", "01/01/26"):
            self.assertTrue(pcf.DATE.fullmatch(ok), ok)
        for bad in ("Approved", "26", "1-11-26", "111/1/26"):
            self.assertFalse(pcf.DATE.fullmatch(bad), bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
