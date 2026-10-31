#!/usr/bin/env python3
"""Offline tests for export_drawing.py: the name strip, the name check, the PNGs.

    python3 tools/fusion/test_export_drawing.py

No Fusion: the tests make small PDFs with PyMuPDF that look like Fusion's
title block ("Created by" with the account holder's name under it).
"""

import json
import os
import sys
import tempfile
import unittest

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import export_drawing as ed  # noqa: E402


def make_pdf(path, pages=1, name_under_label="Jane Roe", stray=None):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=842, height=595)
        page.insert_text((600, 520), "Created by", fontsize=8)
        page.insert_text((600, 532), "%s   31/10/26" % name_under_label, fontsize=8)
        page.insert_text((100, 100), "GA-%d ELEVATIONS  2500  1700  2400" % (i + 1), fontsize=12)
        if stray:
            page.insert_text((100, 200), stray, fontsize=10)
    doc.save(path)
    doc.close()


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="export-test-")
        self.out = os.path.join(self.tmp, "out")
        self.names = os.path.join(self.tmp, "names.json")
        with open(self.names, "w") as fh:
            json.dump(["jane.roe", "Jane Roe"], fh)

    def test_name_is_removed_and_pngs_written(self):
        raw = os.path.join(self.tmp, "raw.pdf")
        make_pdf(raw, pages=2)
        pdf, pngs, pages = ed.check_and_render(raw, ed.account_words(self.names), self.out,
                                               "100000_P04_POD-GENERAL-ASSEMBLY_DWG", 40)
        self.assertEqual(pages, 2)
        self.assertTrue(os.path.isfile(pdf))
        self.assertEqual([os.path.basename(p) for p in pngs],
                         ["100000_P04_POD-GENERAL-ASSEMBLY_DWG-render.png",
                          "100000_P04_POD-GENERAL-ASSEMBLY_DWG-render-p2.png"])
        text = " ".join(p.get_text() for p in fitz.open(pdf)).lower()
        self.assertNotIn("jane", text)
        self.assertNotIn("roe", text)
        self.assertIn("created by", text)          # the label stays
        self.assertIn("elevations", text)          # the drawing stays

    def test_a_name_elsewhere_stops_the_export(self):
        raw = os.path.join(self.tmp, "raw.pdf")
        make_pdf(raw, stray="checked by Jane")
        with self.assertRaises(RuntimeError) as cm:
            ed.check_and_render(raw, ed.account_words(self.names), self.out, "X_DWG", 40)
        self.assertNotIn("jane", str(cm.exception).lower())   # the message never shows the name
        self.assertFalse(os.path.exists(os.path.join(self.out, "X_DWG.pdf")))

    def test_short_name_parts_are_checked_as_whole_words(self):
        with open(self.names, "w") as fh:
            json.dump(["d", "DD HH"], fh)
        self.assertEqual(ed.account_words(self.names), {"dd", "hh"})
        raw = os.path.join(self.tmp, "raw.pdf")
        make_pdf(raw, name_under_label="DD HH", stray="add the hh-free note")   # 'add' is not 'dd'
        with self.assertRaises(RuntimeError):                                  # but 'hh-free' holds hh
            ed.check_and_render(raw, ed.account_words(self.names), self.out, "Y_DWG", 40)
        make_pdf(raw, name_under_label="DD HH", stray="add a padded note")
        pdf, _p, _n = ed.check_and_render(raw, ed.account_words(self.names), self.out, "Y_DWG", 40)
        self.assertTrue(os.path.isfile(pdf))

    def test_export_script_compiles(self):
        compile(ed.EXPORT_SCRIPT % {"name": "N", "raw": "/x/raw.pdf", "sheets": "1-2",
                                    "names": "/x/n.json"}, "fusion", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
