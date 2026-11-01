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


class ProbeTests(unittest.TestCase):
    @staticmethod
    def spec():
        """Probe cases like the probe script's: per form, five lines, a hatch, a thin strip."""
        import hatch
        out = []
        for r, form in enumerate(("plain", "mid", "dup-first", "dup-last")):
            y = 20.0 + 60.0 * r
            out.append(["%s small x5" % form, [hatch.chain_for((20.0 + 12 * k, y), (30.0 + 12 * k, y + 20), form)
                                               for k in range(5)], False])
            sq = [(100.0, y), (120.0, y), (120.0, y + 20.0), (100.0, y + 20.0)]
            out.append(["%s many" % form, [hatch.chain_for(a, b, form) for a, b in
                                           hatch.hatch_segments(sq, spacing=0.7)], False])
            strip = [(140.0, y), (170.0, y), (170.0, y + 0.44), (140.0, y + 0.44)]
            out.append(["%s thin" % form, [hatch.chain_for(a, b, form) for a, b in
                                           hatch.hatch_segments(strip, spacing=0.5, angle_deg=135.0)], False])
        return out

    def run_probe(self, drawn_for):
        """drawn_for(label, chains) -> the paths Fusion "drew" for that case."""
        spec = self.spec()
        d = tempfile.mkdtemp()
        pdf = os.path.join(d, "probe.pdf")
        with open(pdf, "wb") as fh:
            fh.write(fake_pdf({"PROBE " + label: drawn_for(label, chains) for label, chains, _own in spec}))
        with open(pdf + ".json", "w") as fh:
            json.dump({"cases": spec}, fh)
        out = os.path.join(d, "mode.json")
        mode = pc.probe(pdf, out)
        with open(out) as fh:
            self.assertEqual(json.load(fh)["mode"], mode)
        return mode

    @staticmethod
    def as_asked(chains):
        return [[("m", tuple(ch[0]))] + [("l", tuple(p)) for p in ch[1:]] for ch in chains]

    def test_plain_lines_that_come_out_right(self):
        self.assertEqual(self.run_probe(lambda label, chains: self.as_asked(chains)), "plain")

    def test_a_form_that_breaks_only_with_many_lines_is_not_taken(self):
        # the B-B hatch had 230 lines in one sketch: five good lines aren't proof enough
        def drawn(label, chains):
            if label == "plain many":
                return [[("m", (100, 20)), ("l", (100, 20.4)), ("l", (100, 20))]]
            return self.as_asked(chains)
        self.assertEqual(self.run_probe(drawn), "mid")

    def test_scraps_like_the_live_b_b_hatch_are_not_taken_for_lines(self):
        # live 2026-10-31: 2-point lines came out as short vertical back-and-forth pieces
        def drawn(label, chains):
            if label.startswith("mid"):
                return self.as_asked(chains)
            return [[("m", (50, 20)), ("l", (50, 20.4)), ("l", (50, 20)), ("l", (50, 20.4))]]
        self.assertEqual(self.run_probe(drawn), "mid")

    def test_no_probe_export_gives_none(self):
        out = os.path.join(tempfile.mkdtemp(), "mode.json")
        self.assertEqual(pc.probe("/nonexistent/probe.pdf", out), "none")
        with open(out) as fh:
            self.assertEqual(json.load(fh)["mode"], "none")

    def new_spec(self):
        """The probe's cases at the GA's own spacings (2026-11-01 07:55)."""
        import hatch
        sq = [(200.0, 200.0), (220.0, 200.0), (220.0, 220.0), (200.0, 220.0)]
        chains = hatch.chains(hatch.hatch_segments(sq, spacing=2.0), sq)
        strip = [(260.0, 205.0), (290.0, 205.0), (290.0, 206.5), (260.0, 206.5)]
        return self.spec() + [
            ["chain zigzag 2mm", chains, True],
            ["pairs 2mm", [p for ch in hatch.chains(hatch.hatch_segments(sq, spacing=2.0), sq, edge_links=True)
                           for p in hatch.pieces(ch)], True],
            ["thin own", [[a, b] for a, b in hatch.fill_lines(strip)], True],
            ["own sketch x5", [[(200.0 + 12 * k, 20.0), (210.0 + 12 * k, 40.0)] for k in range(5)], True],
            ["4pt open", [[(240.0, 85.0), (260.0, 80.0), (260.0, 100.0), (240.0, 95.0)]], False],
            ["5pt closed", [[(270.0, 85.0), (290.0, 80.0), (290.0, 100.0), (270.0, 95.0), (270.0, 85.0)]], False]]

    def decide(self, bad):
        """The probe's answer when the cases in `bad` (and every one-sketch form) come out wrong."""
        spec = self.new_spec()
        d = tempfile.mkdtemp()
        pdf = os.path.join(d, "probe.pdf")
        wrong = lambda label: label in bad or any(label.startswith(f) for f in ("plain", "mid", "dup"))
        with open(pdf, "wb") as fh:
            fh.write(fake_pdf({"PROBE " + label: ([seg_path((0, 0), (1, 0))] if wrong(label) else self.as_asked(chains))
                               for label, chains, _own in spec}))
        with open(pdf + ".json", "w") as fh:
            json.dump({"cases": spec}, fh)
        out = os.path.join(d, "mode.json")
        pc.probe(pdf, out)
        with open(out) as fh:
            got = json.load(fh)
        return got["mode"], got["thin"], pc.main(["need-mode", out])

    def test_long_chains_garbled_gives_pairs_and_thin_lines_one_per_sketch(self):
        # the live answer of 07:55 at the GA's own spacings: chains break, pieces and single lines don't
        self.assertEqual(self.decide({"chain zigzag 2mm"}), ("pairs", "own-sketch", 0))

    def test_a_chain_that_comes_out_right_is_taken_first(self):
        self.assertEqual(self.decide(set()), ("chain", "own-sketch", 0))

    def test_thin_faces_dont_hold_the_hatch_back(self):
        # PM ruling 2026-11-01: thin faces are left in outline, so the hatch goes on without a form for them
        self.assertEqual(self.decide({"thin own"}), ("chain", "none", 0))

    def test_one_line_per_sketch_is_the_last_form(self):
        self.assertEqual(self.decide({"chain zigzag 2mm", "pairs 2mm"}), ("own-sketch", "own-sketch", 0))

    def test_nothing_right_gives_none(self):
        self.assertEqual(self.run_probe(lambda label, chains: [seg_path((0, 0), (1, 0))]), "none")


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

    def test_the_hatch_is_checked_line_by_line_against_its_record(self):
        # ga_section_sheet.py writes NAME.hatch.json next to the PDF: the chains asked, per sketch
        d = tempfile.mkdtemp()
        pdf = os.path.join(d, "X_DWG.pdf")
        chain = [[10, 10], [20, 20], [20, 22], [10, 12]]
        with open(pdf[:-4] + ".hatch.json", "w") as fh:
            json.dump({"layers": {"HATCH - SECTION AA 001": [chain]}}, fh)
        good = [[("m", (10, 10)), ("l", (20, 20)), ("l", (20, 22)), ("l", (10, 12))]]
        with open(pdf, "wb") as fh:
            fh.write(fake_pdf({"HATCH - SECTION AA 001": good}))
        self.assertEqual(pc.check_hatch(pdf, "HATCH - SECTION AA", 3), [])
        bad = [[("m", (10, 10)), ("l", (20, 20)), ("l", (20, 22)), ("l", (10, 14))]]   # one end moved
        with open(pdf, "wb") as fh:
            fh.write(fake_pdf({"HATCH - SECTION AA 001": bad}))
        self.assertTrue(any("differ" in p for p in pc.check_hatch(pdf, "HATCH - SECTION AA", 3)))

    def test_without_a_record_only_the_count_is_checked(self):
        lines = [seg_path((10 + k, 10), (20 + k, 20)) for k in range(5)]
        path = self.write({"HATCH - SECTION AA 001": lines})
        self.assertEqual(pc.check_hatch(path, "HATCH - SECTION AA", 5), [])
        self.assertTrue(pc.check_hatch(path, "HATCH - SECTION AA", 50))

    def test_a_line_drawn_back_and_forth_is_one_line(self):
        # Fusion's export writes a 2-point line as m B l A l B l A
        twice = [[("m", (20, 20)), ("l", (10, 10)), ("l", (20, 20)), ("l", (10, 10))]]
        self.assertEqual(len(pc.drawn_lines(twice)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
