"""Offline tests of the ceiling drawing method's fixes after the first rib sample (2026-11-01):
each size dimensioned once, scale labels, and the PDF read-back check (on PDFs made here).

    python3 -m pytest -q v2/02-Drawings/ceiling/test_drawings_offline.py
"""

import os
import sys
import tempfile
import unittest

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_drawing_pdf as C  # noqa: E402
import drawing_specs as S  # noqa: E402

PT = 72 / 25.4


class Sizes(unittest.TestCase):
    def test_rib_sizes_once(self):
        """The rib's overall sizes in the order the drawing adds them (view from above, front
        view, view from the left): 44 and 1034, then 20 (the crown, a new size) and 24; the view
        from the left repeats 1034 and 24, so it gets none (the first sample printed both twice)."""
        done = []
        got = [S.new_size(done, "X", 44.0), S.new_size(done, "Y", 1034.0),
               S.new_size(done, "X", 20.0), S.new_size(done, "Z", 24.0),
               S.new_size(done, "Y", 1034.0), S.new_size(done, "Z", 24.0)]
        self.assertEqual(got, [True, True, True, True, False, False])
        self.assertEqual(done, [("X", 44.0), ("Y", 1034.0), ("X", 20.0), ("Z", 24.0)])

    def test_same_size_other_axis_is_kept(self):
        done = []
        self.assertTrue(S.new_size(done, "X", 24.0))
        self.assertTrue(S.new_size(done, "Z", 24.0))
        self.assertFalse(S.new_size(done, "Z", 24.04))


class Labels(unittest.TestCase):
    def test_scale_text(self):
        self.assertEqual([S.scale_text(x) for x in (2.0, 1.0, 0.2, 0.1, 0.05)], ["2:1", "1:1", "1:5", "1:10", "1:20"])

    def test_rib_front_view_label(self):
        self.assertEqual(S.labels(S.SPECS["rib"]), {"front": "SCALE 2:1"})
        self.assertEqual(S.labels(S.SPECS["tray"]), {})

    def test_title_scale_line(self):
        row = dict(S.SPECS["rib"]["title"])["SCALE"]
        self.assertEqual(row, "1:5, front view 2:1")


def sheet_pdf(path, outline, with_circles=True, images=()):
    """An A2 page with the symbol drawn as Fusion layers it (outline and circles in their own
    layers) and grey boxes standing in for images: images = [(x0, top, w, h)] in sheet mm."""
    doc = fitz.open()
    page = doc.new_page(width=594 * PT, height=420 * PT)
    H = 420

    def pt(x, y):
        return fitz.Point(x * PT, (H - y) * PT)
    ocg = doc.add_ocg(C.SYMBOL)
    for a, b in zip(outline, outline[1:]):
        page.draw_line(pt(*a), pt(*b), oc=ocg)
    if with_circles:
        occ = doc.add_ocg(C.SYMBOL + " CIRCLES")
        x0, y0 = outline[0][0], (outline[0][1] + outline[3][1]) / 2
        for r in (5.0, 2.5):
            page.draw_circle(pt(x0 + 19, y0), r * PT, oc=occ)
    for x0, top, w, h in images:
        pix = fitz.Pixmap(fitz.csGRAY, fitz.IRect(0, 0, 20, 10), False)
        pix.clear_with(200)
        page.insert_image(fitz.Rect(x0 * PT, (H - top) * PT, (x0 + w) * PT, (H - top + h) * PT), pixmap=pix,
                          keep_proportion=False)
    doc.save(path)
    return path


def outline_at(x0, y0):
    return [(x0, y0 - 2.5), (x0 + 10, y0 - 5), (x0 + 10, y0 + 5), (x0, y0 + 2.5), (x0, y0 - 2.5)]


class Symbol(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def read(self, outline, **kw):
        doc = fitz.open(sheet_pdf(os.path.join(self.tmp, "s.pdf"), outline, **kw))
        return C.symbol_problems(doc[0], 420.0, S.symbol_place("A2"))

    def test_right_symbol_passes(self):
        self.assertEqual(self.read(outline_at(*S.symbol_place("A2"))), [])

    def test_first_sample_triangle_fails(self):
        """The first rib sample's outline: one corner moved to the sheet's frame corner."""
        x0, y0 = S.symbol_place("A2")
        bad = outline_at(x0, y0)
        bad[0] = bad[-1] = (20.0, 10.0)
        self.assertTrue(any("outline" in p for p in self.read(bad)))

    def test_outline_as_one_quad_passes(self):
        """Fusion's export of the outline alone in its sketch (the second rib sample): one closed 4-point path,
        which PyMuPDF reads as a single quad item, not four lines."""
        x0, y0 = S.symbol_place("A2")
        doc = fitz.open()
        page = doc.new_page(width=594 * PT, height=420 * PT)
        pt = lambda x, y: fitz.Point(x * PT, (420 - y) * PT)
        ocg = doc.add_ocg(C.SYMBOL)
        quad = fitz.Quad(pt(x0, y0 + 2.5), pt(x0 + 10, y0 + 5), pt(x0, y0 - 2.5), pt(x0 + 10, y0 - 5))
        page.draw_quad(quad, oc=ocg)
        occ = doc.add_ocg(C.SYMBOL + " CIRCLES")
        for r in (5.0, 2.5):
            page.draw_circle(pt(x0 + 19, y0), r * PT, oc=occ)
        path = os.path.join(self.tmp, "q.pdf")
        doc.save(path)
        page = fitz.open(path)[0]
        self.assertTrue(any(it[0] == "qu" for d in page.get_drawings() for it in d["items"]), "the test draws a quad")
        self.assertEqual(C.symbol_problems(page, 420.0, (x0, y0)), [])

    def test_missing_circles_fail(self):
        self.assertTrue(any("circle" in p for p in self.read(outline_at(*S.symbol_place("A2")), with_circles=False)))


class Images(unittest.TestCase):
    def test_sizes_and_places(self):
        tmp = tempfile.mkdtemp()
        sp = S.SPECS["rib"]
        notes = sp["images"]["notes"]
        good = sheet_pdf(os.path.join(tmp, "g.pdf"), outline_at(*S.symbol_place("A2")),
                         images=[(notes[0], notes[1], 170.0, 75.4)])
        boxes = C.image_boxes(fitz.open(good)[0], 420.0)
        self.assertEqual(C.image_problems(boxes, [("notes", notes, (170.0, 75.4))]), [])
        # the first sample: inserted at Fusion's own 58 mm width
        small = sheet_pdf(os.path.join(tmp, "b.pdf"), outline_at(*S.symbol_place("A2")),
                          images=[(notes[0], notes[1] - 49.7, 58.0, 25.7)])
        boxes = C.image_boxes(fitz.open(small)[0], 420.0)
        self.assertEqual(len(C.image_problems(boxes, [("notes", notes, (170.0, 75.4))])), 1)

    def test_extents_from_log(self):
        log = ("view front extent (66.0, 336.0, 154.0, 384.0) scale 2 style visible\n"
               "view top   extent (105.6, 96.6, 114.4, 303.4)\n")
        self.assertEqual(C.extents_from_log(log), {"front": (66.0, 336.0, 154.0, 384.0),
                                                   "top": (105.6, 96.6, 114.4, 303.4)})


def text_pdf(path, texts, size_mm=4.89, width=841, height=594):
    """An A1 page with plain texts: [(text, x, y)] in sheet mm (y of the text's baseline, origin bottom left)."""
    doc = fitz.open()
    page = doc.new_page(width=width * PT, height=height * PT)
    for t, x, y in texts:
        page.insert_text(fitz.Point(x * PT, (height - y) * PT), t, fontsize=size_mm * PT)
    doc.save(path)
    return fitz.open(path)[0]


HEADER = [("HOLES - FRONT VIEW", 730.0, 578.0), ("Hole", 686.0, 570.0), ("X Dim", 707.0, 570.0),
          ("Y Dim", 732.0, 570.0), ("Description", 779.0, 570.0)]


class HoleTable(unittest.TestCase):
    """The tray's second drawing printed its hole table with a header and no rows; the PDF check passed it."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def spans(self, texts):
        page = text_pdf(os.path.join(self.tmp, "t.pdf"), texts, size_mm=3.49)
        return C.spans_mm(page, 594.0)

    def test_empty_table_fails(self):
        """Only the header, and the border's zone letters A and B just outside the frame at the same height."""
        sp = self.spans(HEADER + [("A", 832.3, 563.0), ("B", 832.3, 514.0)])
        self.assertEqual(len(C.table_problems(sp, {"holes": "front"}, 841.0)), 1)

    def test_table_with_a_row_passes(self):
        sp = self.spans(HEADER + [("A1", 686.0, 563.0), ("580.00", 707.0, 563.0), ("-12.50", 732.0, 563.0),
                                  ("Ø19.10 THRU", 779.0, 563.0)])
        self.assertEqual(C.table_problems(sp, {"holes": "front"}, 841.0), [])

    def test_no_table_when_the_spec_has_holes_fails(self):
        self.assertEqual(len(C.table_problems(self.spans([("NOTES", 660.0, 500.0)]), {"holes": "front"}, 841.0)), 1)

    def test_no_holes_no_check(self):
        self.assertEqual(C.table_problems([], {"holes": None}, 841.0), [])


class SizesOnce(unittest.TestCase):
    """Each listed size printed once: the rib's crown 20 went missing when the sizes moved to the outer faces."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def problems(self, texts, sizes):
        page = text_pdf(os.path.join(self.tmp, "s.pdf"), texts)
        return C.size_problems(C.spans_mm(page, 594.0), {"sizes": sizes, "holes": None}, 841.0)

    def test_missing_crown_fails(self):
        got = self.problems([("44", 107.0, 86.0), ("1034", 90.0, 194.0), ("24", 50.0, 357.0)], ["44", "1034", "20", "24"])
        self.assertEqual(got, ["size 20 is printed 0 times (the spec wants it once)"])

    def test_twice_fails_and_title_block_text_is_not_counted(self):
        got = self.problems([("1160", 194.0, 175.0), ("1160", 194.0, 480.0), ("1045", 68.0, 284.0),
                             ("1045", 700.0, 30.0)], ["1160", "1045"])
        self.assertEqual(got, ["size 1160 is printed 2 times (the spec wants it once)"])

    def test_all_once_passes(self):
        self.assertEqual(self.problems([("1160", 194.0, 175.0), ("1045", 68.0, 284.0), ("34", 68.0, 491.0)],
                                       ["1160", "1045", "34"]), [])

    def test_specs_list_their_sizes(self):
        self.assertEqual(S.SPECS["rib"]["sizes"], ["44", "1034", "20", "24"])
        self.assertEqual(S.SPECS["rib"]["faces"], {"front": ["bottom"]})
        self.assertIsNone(S.SPECS["cassette"]["holes"])


if __name__ == "__main__":
    unittest.main()
