#!/usr/bin/env python3
"""Offline tests for sheet_notes.py: rendering and placement.

    python3 tools/fusion/test_sheet_notes.py
"""

import os
import sys
import tempfile
import unittest

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheet_notes as sn  # noqa: E402


class NotesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="notes-test-")

    def test_render_is_exactly_the_width_at_300_dpi(self):
        png = os.path.join(self.tmp, "n.png")
        _p, w_px, h_px, h_mm = sn.render("# NOTES\nAll dimensions in mm.\n\nĐế / sàn, Trần.",
                                         150.0, 2.5, png)
        self.assertAlmostEqual(w_px, round(150.0 / 25.4 * sn.DPI), delta=1)
        self.assertAlmostEqual(h_px, h_mm / 25.4 * sn.DPI, delta=2)
        pix = fitz.Pixmap(png)
        self.assertEqual((pix.width, pix.height), (w_px, h_px))
        self.assertEqual(pix.xres, sn.DPI)

    def test_vietnamese_text_survives(self):
        png = os.path.join(self.tmp, "v.pdf")
        # render to a PDF page instead of a PNG to read the text back
        doc = fitz.open()
        page = doc.new_page(width=300, height=100)
        page.insert_textbox(fitz.Rect(5, 5, 295, 95), "Đế / sàn, Vách, Trần, Lớp tiêu âm",
                            fontsize=10, fontname="AU", fontfile=sn.FONT)
        doc.save(png)
        self.assertIn("Lớp tiêu âm", fitz.open(png)[0].get_text())

    def test_placement_puts_the_lower_left_corner_where_asked(self):
        old = (sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR)
        try:
            for anchor in ("lower-left", "upper-left", "center"):
                sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR = 0.0846667, anchor
                x, y, scale = sn.placement(600.0, 250.0, 200.0, 2362, 900)
                w = 2362 * sn.MM_PER_PX_AT_SCALE_1 * scale
                h = 900 * sn.MM_PER_PX_AT_SCALE_1 * scale
                self.assertAlmostEqual(w, 200.0, places=6)
                ll = {"lower-left": (x, y), "upper-left": (x, y - h), "center": (x - w / 2, y - h / 2)}[anchor]
                self.assertAlmostEqual(ll[0], 600.0, places=6)
                self.assertAlmostEqual(ll[1], 250.0, places=6)
        finally:
            sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR = old

    def test_unmeasured_mapping_refuses(self):
        old = (sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR)
        try:
            sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR = None, None
            with self.assertRaises(RuntimeError):
                sn.placement(0, 0, 100, 100, 100)
        finally:
            sn.MM_PER_PX_AT_SCALE_1, sn.ANCHOR = old

    def test_insert_script_compiles(self):
        compile(sn.INSERT_SCRIPT % {"args": {"name": "N", "sheet": 1, "png": "/x.png", "px": 1.0,
                                             "py": 2.0, "scale": 0.5, "label": "n.txt"}}, "f", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
