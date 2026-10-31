#!/usr/bin/env python3
"""Offline tests for hatch.py.  python3 tools/fusion/test_hatch.py"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hatch  # noqa: E402
from hatch import hatch_segments  # noqa: E402


def inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


class HatchTests(unittest.TestCase):
    def test_square_at_45_degrees(self):
        sq = [(0, 0), (10, 0), (10, 10), (0, 10)]
        segs = hatch_segments(sq, spacing=1.0)
        self.assertGreater(len(segs), 10)
        for a, b in segs:
            self.assertAlmostEqual(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180, 45, places=6)
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            self.assertTrue(inside(sq, *mid))
            for p in (a, b):                      # ends on the outline
                self.assertTrue(min(abs(p[0]), abs(p[0] - 10), abs(p[1]), abs(p[1] - 10)) < 1e-9)
        # total hatch length = area / spacing for a convex shape
        self.assertAlmostEqual(sum(math.dist(a, b) for a, b in segs), 100.0, delta=1.5)

    def test_hole_is_left_empty(self):
        outer = [(0, 0), (20, 0), (20, 20), (0, 20)]
        hole = [(5, 5), (15, 5), (15, 15), (5, 15)]
        segs = hatch_segments([outer, hole], spacing=1.0)
        for a, b in segs:
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            self.assertFalse(inside(hole, *mid))
        self.assertAlmostEqual(sum(math.dist(a, b) for a, b in segs), 300.0, delta=3.0)

    def test_thin_strip_and_other_angle(self):
        strip = [(0, 0), (100, 0), (100, 2.3), (0, 2.3)]      # a 2.3 mm skin at 1:1
        segs = hatch_segments(strip, spacing=2.0, angle_deg=135.0)
        self.assertEqual(len(segs), 36)                         # 72.3 mm across the lines / 2 mm
        for a, b in segs:
            self.assertTrue(-1e-9 <= min(a[1], b[1]) and max(a[1], b[1]) <= 2.3 + 1e-9)

    def test_concave_l_shape(self):
        ell = [(0, 0), (10, 0), (10, 3), (3, 3), (3, 10), (0, 10)]
        for a, b in hatch_segments(ell, spacing=0.7):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            self.assertTrue(inside(ell, *mid))

    def test_degenerate_input(self):
        self.assertEqual(hatch_segments([], 1.0), [])
        self.assertEqual(hatch_segments([(0, 0), (0, 0), (0, 0)], 1.0), [])



class LineFormTests(unittest.TestCase):
    """The point list for one straight line, in the form the live probe picked."""

    def test_each_form(self):
        a, b = (0.0, 0.0), (4.0, 2.0)
        self.assertEqual(hatch.chain_for(a, b, "plain"), [a, b])
        self.assertEqual(hatch.chain_for(a, b, "own-sketch"), [a, b])
        self.assertEqual(hatch.chain_for(a, b, "mid"), [a, (2.0, 1.0), b])
        self.assertEqual(hatch.chain_for(a, b, "dup-first"), [a, a, b])
        self.assertEqual(hatch.chain_for(a, b, "dup-last"), [a, b, b])

    def test_no_working_form_draws_nothing(self):
        with self.assertRaises(ValueError):
            hatch.chain_for((0, 0), (1, 1), "none")

    def test_the_form_is_read_from_the_probe_file(self):
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"mode": "mid"}, fh)
        try:
            self.assertEqual(hatch.read_line_mode(fh.name), "mid")
        finally:
            os.remove(fh.name)
        self.assertEqual(hatch.read_line_mode(None), "plain")


class ThinFaceTests(unittest.TestCase):
    """ISO 128-50: faces too thin to hatch are filled (lines FILL_MM apart)."""

    def test_a_skin_strip_is_filled(self):
        skin = [(0, 0), (120, 0), (120, 0.15), (0, 0.15)]      # 3 mm ACP at 1:20
        self.assertAlmostEqual(hatch.face_width(skin), 0.15, delta=0.01)
        self.assertEqual(hatch.spacing_for(skin), hatch.FILL_MM)

    def test_a_wide_face_is_hatched(self):
        block = [(0, 0), (17, 0), (17, 40), (0, 40)]            # a decor block, 343 x 800 at 1:20
        self.assertGreater(hatch.face_width(block), hatch.THIN_MM)
        self.assertEqual(hatch.spacing_for(block), hatch.HATCH_MM)

    def test_a_hole_makes_a_frame_thin(self):
        outer = [(0, 0), (20, 0), (20, 20), (0, 20)]
        hole = [(1, 1), (19, 1), (19, 19), (1, 19)]               # a 1 mm frame
        area, per = hatch.loop_area_perimeter([outer, hole])
        self.assertAlmostEqual(area, 400 - 324)
        self.assertAlmostEqual(per, 80 + 72)
        self.assertEqual(hatch.spacing_for([outer, hole]), hatch.FILL_MM)

    def test_a_filled_strip_reads_solid(self):
        skin = [(0, 0), (120, 0), (120, 1.7), (0, 1.7)]          # a 34 mm cassette at 1:20
        segs = hatch_segments(skin, spacing=hatch.spacing_for(skin))
        self.assertGreater(len(segs), 150)                         # 120 x 0.707 / 0.5
        self.assertLess(len(segs), 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
