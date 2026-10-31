#!/usr/bin/env python3
"""Offline tests for hatch.py.  python3 tools/fusion/test_hatch.py"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
