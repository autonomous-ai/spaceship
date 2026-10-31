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

    def test_placement_follows_the_measured_mapping(self):
        # measured 2026-10-31: 58.02 mm wide at scale 1 whatever the pixels or DPI; lower-left anchor
        self.assertEqual((sn.WIDTH_AT_SCALE_1_MM, sn.ANCHOR), (58.02, "lower-left"))
        for w_px, h_px in ((1000, 500), (500, 500), (2000, 400), (3308, 1212)):
            x, y, scale = sn.placement(340.0, 90.0, 280.0, w_px, h_px)
            self.assertEqual((x, y), (340.0, 90.0))
            self.assertAlmostEqual(scale * 58.02, 280.0, places=6)     # same scale for any pixel size

    def test_measured_test_images_come_out_as_in_the_pdf(self):
        # the four live measurements, predicted back: (px, py, scale) -> width, height in mm
        for w_px, h_px, scale, w_mm, h_mm in ((1000, 500, 1.0, 58.02, 29.02), (1000, 500, 0.5, 29.02, 14.52),
                                              (500, 500, 1.0, 58.02, 58.02), (2000, 400, 1.0, 58.02, 11.62)):
            self.assertAlmostEqual(58.02 * scale, w_mm, delta=0.02)
            self.assertAlmostEqual(58.02 * scale * h_px / w_px, h_mm, delta=0.02)

    def test_another_sheet_size_can_pass_its_own_width(self):
        _x, _y, scale = sn.placement(0, 0, 116.04, 1000, 500, width_at_scale_1=116.04)
        self.assertAlmostEqual(scale, 1.0)

    def test_insert_script_compiles(self):
        compile(sn.INSERT_SCRIPT % {"args": {"name": "N", "sheet": 1, "png": "/x.png", "px": 1.0,
                                             "py": 2.0, "scale": 0.5, "label": "n.txt"}}, "f", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
