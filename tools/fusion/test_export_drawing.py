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
import run_script as rs  # noqa: E402


def make_pdf(path, pages=1, name_under_label="Jane Roe", stray=None):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=842, height=595)
        page.insert_text((600, 520), "Created by", fontsize=8)
        page.insert_text((600, 532), name_under_label, fontsize=8)
        # the date in the same cell, 120 pt right of the label as Fusion lays it out (with it 3 spaces
        # after the name, "Autonomous" had no room to replace the name: #290's stamp)
        page.insert_text((720, 532), "31/10/26", fontsize=8)
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

    def test_the_title_block_is_filled_from_the_drawing_name(self):
        # Reviewer 5 on the GUI L1 (85900e0): DWG No. and Rev. were empty because the cleaned
        # file was called clean.pdf, so the shared fill (#222) found no drawing number in it
        import test_pdf_title_block as tptb
        raw = os.path.join(self.tmp, "raw.pdf")
        tptb.sheet(raw)
        names = os.path.join(self.tmp, "names2.json")
        with open(names, "w") as fh:
            json.dump([tptb.NAME], fh)
        pdf, _pngs, _n = ed.check_and_render(raw, ed.account_words(names), self.out,
                                             "211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG", 40)
        page = fitz.open(pdf)[0]
        cells = tptb.ptb.cells(page)
        cell = lambda f: " ".join(page.get_text("text", clip=cells[f]).split())
        self.assertEqual((cell("DWG No."), cell("Rev.")), ("211101", "P01"))
        self.assertIn("WALL", cell("Title"))
        self.assertNotIn("_CAD", cell("Title"))                  # the design's file name is gone

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

    def test_the_tools_run_inside_a_held_lock_with_its_token(self):
        # one session can hold the lock for several steps (open, draw, export)
        import subprocess
        for tool, args in (("export_drawing.py", ["D_DWG", self.tmp]),
                           ("export_design.py", ["D_CAD", "D", self.tmp, self.tmp])):
            lockdir = os.path.join(tempfile.mkdtemp(prefix="exp-lock-"), "fusion.lock")
            hold = rs.FusionLock(lockdir, label="held", pid=None, hold_s=60, log=lambda m: None)
            hold.acquire(1)
            env = dict(os.environ, **{rs.TOKEN_ENV: hold.token})
            p = subprocess.run([sys.executable, os.path.join(HERE, tool)] + args + [
                "--lock", lockdir, "--lock-wait", "0.3", "--url", "http://127.0.0.1:9/mcp", "--timeout", "2"],
                capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(p.returncode, 2, "%s: %s" % (tool, p.stderr[-300:]))     # past the lock, to Fusion
            self.assertIn("cannot reach Fusion", p.stderr, tool)
            self.assertEqual(hold.read_owner()["token"], hold.token, tool)
            self.assertTrue(hold.release_held(hold.token))

    def test_export_script_compiles(self):
        compile(ed.EXPORT_SCRIPT % {"name": "N", "raw": "/x/raw.pdf", "sheets": "1-2",
                                    "names": "/x/n.json"}, "fusion", "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
