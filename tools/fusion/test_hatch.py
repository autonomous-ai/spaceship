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

    def test_a_thin_strip_is_filled_with_long_lines_along_it(self):
        # Fusion's PDF export merges lines under about 1 mm into wrong paths (live probe
        # 2026-11-01), so a thin strip gets lines along it, not short 45 degree strokes
        skin = [(0, 0), (120, 0), (120, 1.7), (0, 1.7)]          # a 34 mm cassette at 1:20
        segs = hatch.fill_lines(skin)
        self.assertEqual(len(segs), 6)                            # 1.7 / 0.3 apart
        for a, b in segs:
            self.assertAlmostEqual(abs(b[1] - a[1]), 0.0, places=6)   # along the strip
            self.assertGreater(math.dist(a, b), 119.0)
        tilted = [(0, 0), (100, 100), (101, 99), (1, -1)]         # a strip at 45 degrees
        self.assertAlmostEqual(hatch.long_edge_angle(tilted), 45.0)

    def test_a_wide_face_keeps_the_45_degree_hatch(self):
        block = [(0, 0), (17, 0), (17, 40), (0, 40)]
        for a, b in hatch.fill_lines(block, index=0):
            self.assertAlmostEqual(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180, 45, places=6)
        for a, b in hatch.fill_lines(block, index=1):
            self.assertAlmostEqual(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180, 135, places=6)


class ChainTests(unittest.TestCase):
    """One Lines.add call per face: the hatch lines joined back and forth."""

    def test_a_convex_face_is_one_chain_through_every_line(self):
        sq = [(0, 0), (20, 0), (20, 20), (0, 20)]
        segs = hatch_segments(sq, spacing=0.7)
        ch = hatch.chains(segs, sq)
        self.assertEqual(len(ch), 1)
        self.assertEqual(len(ch[0]), 2 * len(segs))
        pairs = {tuple(sorted((tuple(map(lambda v: round(v, 6), ch[0][i])), tuple(map(lambda v: round(v, 6), ch[0][i + 1])))))
                 for i in range(0, len(ch[0]), 2)}
        want = {tuple(sorted((tuple(map(lambda v: round(v, 6), a)), tuple(map(lambda v: round(v, 6), b))))) for a, b in segs}
        self.assertEqual(pairs, want)                             # every hatch line is in the chain
        for i in range(1, len(ch[0]) - 1, 2):                    # links stay on the outline or inside
            mid = ((ch[0][i][0] + ch[0][i + 1][0]) / 2, (ch[0][i][1] + ch[0][i + 1][1]) / 2)
            self.assertTrue(hatch._inside(sq, *mid) or hatch._on_outline(sq, *mid))

    def test_a_strip_fill_is_one_chain(self):
        skin = [(0, 0), (120, 0), (120, 1.7), (0, 1.7)]
        ch = hatch.chains(hatch.fill_lines(skin), skin)
        self.assertEqual([len(c) for c in ch], [12])

    def test_a_link_that_would_leave_the_face_starts_a_new_chain(self):
        u = [(0, 0), (30, 0), (30, 20), (20, 20), (20, 5), (10, 5), (10, 20), (0, 20)]   # a U
        segs = hatch_segments(u, spacing=1.0, angle_deg=0.0)       # rows across both arms
        ch = hatch.chains(segs, u)
        self.assertGreater(len(ch), 1)
        for c in ch:
            for i in range(1, len(c) - 1, 2):
                mid = ((c[i][0] + c[i + 1][0]) / 2, (c[i][1] + c[i + 1][1]) / 2)
                self.assertTrue(hatch._inside(u, *mid) or hatch._on_outline(u, *mid))

    def test_chain_form_is_two_points(self):
        self.assertEqual(hatch.chain_for((0, 0), (1, 1), "chain"), [(0, 0), (1, 1)])



class PiecesTests(unittest.TestCase):
    """2026-11-01 07:55: long chains came out garbled in the PDF, 4-point chains exact."""

    def test_a_long_chain_is_cut_into_pieces_of_three_segments(self):
        chain = [(float(i), float(i % 2)) for i in range(9)]           # 8 segments
        got = hatch.pieces(chain)
        self.assertEqual([len(p) - 1 for p in got], [3, 3, 2])
        for a, b in zip(got, got[1:]):
            self.assertEqual(a[-1], b[0])                              # each starts where the last ended
        segs = [(p[i], p[i + 1]) for p in got for i in range(len(p) - 1)]
        self.assertEqual(segs, [(chain[i], chain[i + 1]) for i in range(8)])   # every segment once

    def test_a_short_chain_stays_whole(self):
        for n in (2, 3, 4):
            chain = [(float(i), 0.0) for i in range(n)]
            self.assertEqual(hatch.pieces(chain), [chain])

    def test_edge_links_never_cut_a_corner(self):
        # 08:23: the piece whose link cut the square's corner collapsed in the PDF
        sq = [(230.0, 200.0), (250.0, 200.0), (250.0, 220.0), (230.0, 220.0)]   # the probe's square
        segs = hatch.hatch_segments(sq, spacing=2.0)
        free = hatch.chains(segs, sq)
        edged = hatch.chains(segs, sq, edge_links=True)
        self.assertGreater(len(edged), len(free))                     # chains end at the corners
        for ch in edged:
            for i in range(1, len(ch) - 1, 2):                        # every link: ch[i] -> ch[i + 1]
                self.assertTrue(hatch._on_one_edge(sq, ch[i], ch[i + 1]), (ch[i], ch[i + 1]))
        drawn = sorted(tuple(sorted((ch[i], ch[i + 1]))) for ch in edged for i in range(0, len(ch) - 1, 2))
        self.assertEqual(drawn, sorted(tuple(sorted(s)) for s in segs))   # every hatch line still once

    def test_spaced_lines_keep_every_end_clear_of_earlier_points_and_corners(self):
        # 08:42 probe: Fusion pulled points 2.05 and 2.06 mm from earlier points onto them
        sq = [(230.0, 200.0), (250.0, 200.0), (250.0, 220.0), (230.0, 220.0)]
        segs = hatch.hatch_segments(sq, spacing=2.0)
        kept, shortened, dropped = hatch.spaced(segs, fixed=sq)
        ends = [p for s in kept for p in s]
        for i, p in enumerate(ends):
            for q in sq:
                self.assertGreaterEqual(math.dist(p, q), hatch.SNAP_MM - 1e-9)
            for q in ends[:i - (i % 2)]:                                   # every earlier line's ends
                self.assertGreaterEqual(math.dist(p, q), hatch.SNAP_MM - 1e-9)
        for a, b in kept:
            self.assertGreaterEqual(math.dist(a, b), hatch.MIN_LINE_MM)
        self.assertEqual(len(kept) + dropped, len(segs))
        self.assertGreater(len(kept), len(segs) // 2)                     # the hatch still reads as one

    def test_spaced_lines_stay_on_their_own_line(self):
        a, b = (0.0, 0.0), (10.0, 10.0)
        (kept,), _s, _d = hatch.spaced([(a, b)], fixed=[(0.0, 0.0)])
        p, q = kept
        self.assertAlmostEqual(p[0], p[1])                                 # moved along the 45 degree line
        self.assertGreaterEqual(math.dist(p, a), hatch.SNAP_MM)
        self.assertEqual(q, b)

    def test_the_thin_face_answer_from_the_probe(self):
        import json
        import tempfile
        d = tempfile.mkdtemp()
        old, new = os.path.join(d, "old.json"), os.path.join(d, "new.json")
        with open(old, "w") as fh:
            json.dump({"mode": "chain"}, fh)                           # from before the thin answer
        with open(new, "w") as fh:
            json.dump({"mode": "pairs", "thin": "own-sketch"}, fh)
        self.assertEqual(hatch.read_thin_mode(old), "none")
        self.assertEqual((hatch.read_line_mode(new), hatch.read_thin_mode(new)), ("pairs", "own-sketch"))
        self.assertEqual(hatch.chain_for((0, 0), (1, 1), "pairs"), [(0, 0), (1, 1)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
