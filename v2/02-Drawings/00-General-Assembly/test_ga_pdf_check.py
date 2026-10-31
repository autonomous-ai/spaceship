#!/usr/bin/env python3
"""Offline tests for ga_pdf_check.py, on small PDFs written the way Fusion writes them
(each drawing sketch an optional content layer, coordinates scaled by a 0.06 cm).

    python3 v2/02-Drawings/00-General-Assembly/test_ga_pdf_check.py
"""

import json
import os
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
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


class ProbeTests(unittest.TestCase):
    def run_probe(self, drawn):
        """drawn: {case label: [path, ...]}; the cases are the probe script's own."""
        spec = {"cases": [["01 2pt", [[[20, 20], [50, 50]]], False],
                          ["02 2pt x5", [[[20 + 12 * k, 70], [30 + 12 * k, 90]] for k in range(5)], False],
                          ["06 mid x5", [[[20 + 12 * k, 110], [25 + 12 * k, 120], [30 + 12 * k, 130]]
                                         for k in range(5)], False]]}
        d = tempfile.mkdtemp()
        pdf = os.path.join(d, "probe.pdf")
        with open(pdf, "wb") as fh:
            fh.write(fake_pdf({"PROBE " + k: v for k, v in drawn.items()}))
        with open(pdf + ".json", "w") as fh:
            json.dump(spec, fh)
        out = os.path.join(d, "mode.json")
        mode = pc.probe(pdf, out)
        with open(out) as fh:
            self.assertEqual(json.load(fh)["mode"], mode)
        return mode

    def test_plain_lines_that_come_out_right(self):
        mode = self.run_probe({"01 2pt": [seg_path((20, 20), (50, 50))],
                               "02 2pt x5": [seg_path((20 + 12 * k, 70), (30 + 12 * k, 90)) for k in range(5)]})
        self.assertEqual(mode, "plain")

    def test_scraps_like_the_live_b_b_hatch_are_not_taken_for_lines(self):
        # live 2026-10-31: 2-point lines came out as short vertical back-and-forth pieces
        scraps = [[("m", (50, 20)), ("l", (50, 20.4)), ("l", (50, 20)), ("l", (50, 20.4))]]
        mode = self.run_probe({"01 2pt": scraps, "02 2pt x5": scraps,
                               "06 mid x5": [[("m", (20 + 12 * k, 110)), ("l", (25 + 12 * k, 120)),
                                              ("l", (30 + 12 * k, 130))] for k in range(5)]})
        self.assertEqual(mode, "mid")

    def test_no_probe_export_gives_none(self):
        out = os.path.join(tempfile.mkdtemp(), "mode.json")
        self.assertEqual(pc.probe("/nonexistent/probe.pdf", out), "none")
        with open(out) as fh:
            self.assertEqual(json.load(fh)["mode"], "none")

    def test_nothing_right_gives_none(self):
        self.assertEqual(self.run_probe({"01 2pt": [seg_path((0, 0), (1, 0))]}), "none")


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

    def test_off_angle_hatch_lines_are_reported(self):
        good = [seg_path((10 + k, 10), (20 + k, 20)) for k in range(5)]
        self.assertEqual(pc.check_hatch(self.write({"HATCH - SECTION AA": good}), "HATCH - SECTION AA", 5), [])
        bad = good + [seg_path((50, 10), (50, 20))]
        self.assertTrue(pc.check_hatch(self.write({"HATCH - SECTION AA": bad}), "HATCH - SECTION AA", 5))
        self.assertTrue(pc.check_hatch(self.write({"HATCH - SECTION AA": good}), "HATCH - SECTION AA", 50))


if __name__ == "__main__":
    unittest.main(verbosity=2)
