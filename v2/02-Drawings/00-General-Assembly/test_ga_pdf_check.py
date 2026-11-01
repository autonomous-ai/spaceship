#!/usr/bin/env python3
"""Offline tests for ga_pdf_check.py, on small PDFs written the way Fusion writes them
(each drawing sketch an optional content layer, coordinates scaled by a 0.06 cm).

    python3 v2/02-Drawings/00-General-Assembly/test_ga_pdf_check.py
"""

import os
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools", "fusion"))
import ga_pdf_check as pc  # noqa: E402

RAW = 1.0 / (0.06 * pc.PT_MM)          # PDF units per sheet mm under Fusion's 0.06 cm


def fake_pdf(layer_paths):
    """layer_paths: {layer name: [[("m"|"l", (x, y)), ...], ...]} in sheet mm; a circle is
    ("circle", (cx, cy, r)) and becomes four c pieces."""
    objs, props, body = [], [], [b"q .06 0 0 .06 0 0 cm "]
    for k, (name, paths) in enumerate(layer_paths.items(), start=1):
        objs.append(b"%d 0 obj\n<< /Type /OCG /Name (%s) >>\nendobj\n" % (k, name.encode()))
        props.append(b"/oc%d %d 0 R" % (k, k))
        body.append(b"/OC/oc%d BDC 0 G " % k)
        for path in paths:
            for op, p in path:
                if op == "circle":
                    cx, cy, r = p
                    body.append(b"%d %d m " % (round((cx + r) * RAW), round(cy * RAW)))
                    for ex, ey in ((cx, cy + r), (cx - r, cy), (cx, cy - r), (cx + r, cy)):
                        body.append(b"0 0 0 0 %d %d c " % (round(ex * RAW), round(ey * RAW)))
                else:
                    body.append(b"%d %d %s " % (round(p[0] * RAW), round(p[1] * RAW), op.encode()))
            body.append(b"S ")
        body.append(b"EMC ")
    body.append(b"Q")
    stream = zlib.compress(b"".join(body))
    page = b"99 0 obj\n<< /Resources << /Properties << %s >> >> >>\nendobj\n" % b" ".join(props)
    return (b"%PDF-1.4\n" + b"".join(objs) + page + b"100 0 obj\n<< /Length %d /Filter /FlateDecode >>\nstream\n"
            % len(stream) + stream + b"\nendstream\nendobj\n%%EOF\n")


def seg_path(a, b):
    return [("m", a), ("l", b)]


class ReadBackTests(unittest.TestCase):
    def test_layers_are_named_and_in_sheet_mm(self):
        lay = pc.layers(fake_pdf({"HATCH - SECTION BB": [seg_path((10.0, 20.0), (30.0, 40.0))]}))
        self.assertEqual(list(lay), ["HATCH - SECTION BB"])
        (a, b), = pc.segments(lay["HATCH - SECTION BB"])
        self.assertAlmostEqual(a[0], 10.0, places=1)
        self.assertAlmostEqual(b[1], 40.0, places=1)

    def test_a_chain_with_a_middle_point_is_one_line(self):
        got = pc.merge_collinear([((0, 0), (5, 5)), ((5, 5), (10, 10)), ((10, 10), (20, 10))])
        self.assertTrue(pc.same_segments(got, [((0, 0), (10, 10)), ((10, 10), (20, 10))]))

    def test_zero_length_pieces_are_left_out(self):
        self.assertEqual(pc.segments([[("m", (1, 1)), ("l", (1, 1)), ("l", (2, 1))]]), [((1, 1), (2, 1))])


class SheetCheckTests(unittest.TestCase):
    def write(self, layers):
        path = os.path.join(tempfile.mkdtemp(), "sheet.pdf")
        with open(path, "wb") as fh:
            fh.write(fake_pdf(layers))
        return path

    def test_the_live_triangle_symbol_fails_and_the_trapezoid_passes(self):
        circles = [[("circle", (579.0, 40.0, 5.0))], [("circle", (579.0, 40.0, 2.5))]]
        tri = [[("m", (560, 37.5)), ("l", (560, 37.5)), ("l", (570, 35)), ("l", (570, 45)), ("l", (560, 37.5))]]
        self.assertTrue(pc.check_symbol(self.write({"PROJECTION SYMBOL - FIRST ANGLE": tri + circles})))
        sides = [seg_path(a, b) for a, b in pc.SYMBOL]
        self.assertEqual(pc.check_symbol(self.write({"PROJECTION SYMBOL - FIRST ANGLE": sides + circles})), [])

    def test_an_outline_only_section_has_its_view_and_no_hatch_or_probe_layer(self):
        # PM ruling 2026-11-01 10:1x: the GA sections at 1:20 are in outline only
        view = [seg_path((167.5, 170 + k), (292.5, 170 + k)) for k in range(36)]
        self.assertEqual(pc.check_outline(self.write({"Visible": view, "BORDER": view[:4]}), 30), [])
        left = self.write({"Visible": view, "HATCH - SECTION BB 001": [seg_path((1, 1), (3, 3))]})
        self.assertTrue(any("hatch or probe" in p for p in pc.check_outline(left, 30)))
        probe = self.write({"Visible": view, "PROBE INSET 0.00 001": [seg_path((1, 1), (3, 3))]})
        self.assertTrue(pc.check_outline(probe, 30))
        self.assertTrue(any("Visible" in p for p in pc.check_outline(self.write({"Visible": view[:3]}), 30)))

    def test_a_line_drawn_back_and_forth_is_one_line(self):
        # Fusion's export writes a 2-point line as m B l A l B l A
        twice = [[("m", (20, 20)), ("l", (10, 10)), ("l", (20, 20)), ("l", (10, 10))]]
        self.assertEqual(len(pc.drawn_lines(twice)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
