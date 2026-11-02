#!/usr/bin/env python3
"""Offline tests for fusion_drawing.py, the shared drawing helpers (no Fusion needed).

    python3 tools/fusion/test_fusion_drawing.py
"""

import os
import sys
import types
import contextlib
import io
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fusion_drawing as fd  # noqa: E402
import run_script as rs  # noqa: E402


class P:
    def __init__(self, x, y):
        self.x, self.y = x, y


def fake_adsk():
    a = types.SimpleNamespace()
    a.doEvents = lambda: None
    a.core = types.SimpleNamespace(Point2D=types.SimpleNamespace(create=lambda x, y: P(x, y)))
    a.drawing = types.SimpleNamespace(
        DrawingPoint=types.SimpleNamespace(create=lambda p: types.SimpleNamespace(coordinate=p)),
        DrawingViewStyleTypes=types.SimpleNamespace(VisibleEdgesDrawingViewStyleType="VISIBLE"))
    return a


class Sketch:
    def __init__(self, name):
        self.name, self.chains, self.rings = name, [], []
        self.lines = types.SimpleNamespace(add=lambda pts: self.chains.append([(p.x, p.y) for p in pts]) or "line")
        self.circles = types.SimpleNamespace(
            addByCenterRadius=lambda c, r: self.rings.append(((c.x, c.y), r)) or "circle")


class Sketches:
    def __init__(self):
        self.list = []

    def add(self, name):
        self.list.append(Sketch(name))
        return self.list[-1]

    def item(self, i):
        return self.list[i]

    @property
    def count(self):
        return len(self.list)


class View:
    def __init__(self, inp, stuck, reads_back=None, keeps_scale=None, ignores_input=False):
        # reads_back: {scale asked: scale Fusion reads back}, as seen live; keeps_scale: the view won't change
        # from it; ignores_input: the made view comes at 1:1 whatever the input asked (the README's 1:10 trap)
        self._style, self.stuck = "HIDDEN", stuck
        self.reads_back, self.keeps_scale, self.sets = dict(reads_back or {}), keeps_scale, []
        self._scale = 1.0 if ignores_input else self._read(inp.viewParameters.scaleValue)

    def _read(self, v):
        v = self.keeps_scale if self.keeps_scale is not None else v
        return self.reads_back.get(v, v)

    @property
    def scaleValue(self):
        return self._scale

    @scaleValue.setter
    def scaleValue(self, v):
        self.sets.append(v)
        self._scale = self._read(v)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, v):
        if not self.stuck:
            self._style = v


class Sheet:
    def __init__(self, w=594.0, h=420.0, insert_ok=True, view_stuck=False, dims=0, reads_back=None, keeps_scale=None,
                 ignores_input=False):
        self.width, self.height = w, h
        self.inserted, self.made, self.dims = [], [], []
        self.images = types.SimpleNamespace(createInput=lambda: types.SimpleNamespace(),
                                            insert=lambda ii: self.inserted.append(ii) or insert_ok)
        self.sketches = Sketches()
        self.views = types.SimpleNamespace(
            createBaseViewInput=lambda: types.SimpleNamespace(viewParameters=types.SimpleNamespace()),
            add=lambda inp: self.made.append(View(inp, view_stuck, reads_back, keeps_scale, ignores_input))
            or self.made[-1])
        self.drawingDimensions = types.SimpleNamespace(
            count=dims, addLinearDimension=lambda a, b, p, al: self.dims.append((a, b, p, al)) or "dim")



class HelperTests(unittest.TestCase):
    def setUp(self):
        self.keep = fd.adsk
        fd.adsk = fake_adsk()

    def tearDown(self):
        fd.adsk = self.keep

    def sheet(self, **kw):
        return Sheet(**kw)

    # 1. pictures come in 58.02 mm wide at scale 1
    def test_a_notes_picture_is_scaled_to_its_real_width(self):
        s = self.sheet()
        scale = fd.insert_image(s, "/x/notes.png", 340.0, 90.0, 280.0)
        self.assertAlmostEqual(scale, 280.0 / 58.02)
        ii = s.inserted[0]
        self.assertAlmostEqual(ii.scale, 4.825922, places=5)
        self.assertEqual((ii.position.x, ii.position.y, ii.imageFilePath), (340.0, 90.0, "/x/notes.png"))

    def test_left_at_scale_1_the_text_would_print_tiny(self):
        # CEILING's first drawing: a 280 mm notes picture at scale 1 printed its 3.5 mm text at
        # 3.5 x 58.02 / 280, about 0.7 mm; 2.5 mm text at 120 mm came out about 1.2 mm
        self.assertAlmostEqual(3.5 / fd.image_scale(280.0), 0.725, places=3)

    def test_an_unmeasured_sheet_size_is_refused_unless_measured_width_given(self):
        a0 = self.sheet(w=1189.0, h=841.0)
        with self.assertRaises(RuntimeError):
            fd.insert_image(a0, "/x/n.png", 10, 10, 100)
        self.assertEqual(a0.inserted, [])
        fd.insert_image(a0, "/x/n.png", 10, 10, 100, width_at_scale_1=60.0)
        self.assertAlmostEqual(a0.inserted[0].scale, 100 / 60.0)

    def test_a_portrait_sheet_of_a_measured_size_is_accepted(self):
        self.assertEqual(fd.sheet_size_name(self.sheet(w=297.0, h=420.0)), "A3")

    def test_a_failed_insert_raises(self):
        with self.assertRaises(RuntimeError):
            fd.insert_image(self.sheet(insert_ok=False), "/x/n.png", 10, 10, 100)

    # 2. the first-angle symbol: outline alone in its sketch, circles in another
    def test_the_symbol_outline_is_one_closed_chain_alone_in_its_sketch(self):
        s = self.sheet(w=841.0, h=594.0)                                 # A1, as GA sheet 1
        fd.first_angle_symbol(s, 560.0, 40.0)
        outline, circles = s.sketches.list
        self.assertEqual(outline.name, fd.SYMBOL_NAME)
        self.assertEqual(len(outline.chains), 1)                        # one Lines.add call
        self.assertEqual(outline.chains[0], [(560.0, 37.5), (570.0, 35.0), (570.0, 45.0),
                                             (560.0, 42.5), (560.0, 37.5)])
        self.assertEqual(outline.rings, [])                             # no circles with it
        self.assertEqual(circles.name, fd.SYMBOL_NAME + " CIRCLES")
        self.assertEqual(circles.chains, [])
        self.assertEqual(circles.rings, [((579.0, 40.0), 5.0), ((579.0, 40.0), 2.5)])

    def test_a_second_symbol_on_the_same_sheet_is_refused(self):
        s = self.sheet(w=841.0, h=594.0)
        fd.first_angle_symbol(s, 560.0, 40.0)
        with self.assertRaises(RuntimeError):
            fd.first_angle_symbol(s, 560.0, 40.0)

    # FRONT and CEILING 2026-11-01: an outline edge on the border's line printed as a triangle
    def test_a_symbol_on_the_border_line_is_refused(self):
        s = self.sheet()                                                # A2: frame 20..584 x 10..410
        with self.assertRaises(RuntimeError) as cm:
            fd.first_angle_symbol(s, 20.0, 100.0)                       # left edge on the frame
        self.assertIn("border", str(cm.exception))
        self.assertEqual(s.sketches.list, [])                           # nothing drawn
        with self.assertRaises(RuntimeError):
            fd.first_angle_symbol(s, 300.0, 12.0)                       # foot on the bottom line

    def test_a_symbol_6_mm_in_from_the_border_is_accepted(self):
        s = self.sheet()
        fd.first_angle_symbol(s, 26.0, 21.0)                            # 6 mm in, as FRONT placed it
        self.assertEqual(len(s.sketches.list), 2)

    def test_a_symbol_on_or_near_the_title_block_is_refused(self):
        s = self.sheet()                                                # A2: title block 404..584 x 10..57
        for x0, cy in ((390.0, 30.0), (450.0, 50.0), (450.0, 65.0)):     # touching, inside, 3 mm above
            with self.assertRaises(RuntimeError) as cm:
                fd.first_angle_symbol(s, x0, cy)
            self.assertIn("title block", str(cm.exception))
        fd.first_angle_symbol(s, 450.0, 68.0)                           # 6 mm above it: fine

    def test_by_default_the_symbol_sits_just_left_of_the_title_block(self):
        s = self.sheet()
        fd.first_angle_symbol(s)
        outline = s.sketches.list[0].chains[0]
        xs = [p[0] for p in outline]
        self.assertAlmostEqual(min(xs), 404.0 - 6.0 - 24.0)              # its right end 6 mm from the block
        self.assertAlmostEqual(min(p[1] for p in outline), 21.0 - 5.0)   # foot 6 mm above the frame
        self.assertIsNone(fd.symbol_clear(s, fd.symbol_box(min(xs), 21.0)))

    def test_the_frame_and_title_block_follow_the_sheet_size(self):
        a1 = self.sheet(w=841.0, h=594.0)
        self.assertEqual(fd.frame_box(a1), (20.0, 10.0, 831.0, 584.0))
        self.assertEqual(fd.title_block_box(a1), (651.0, 10.0, 831.0, 57.0))

    # 3. the view style given at creation is ignored by Fusion
    def test_the_view_style_is_set_again_on_the_made_view(self):
        s = self.sheet()
        v = fd.base_view(s, "FRONT", 0.05, (265.0, 410.0))
        self.assertEqual(v.style, "VISIBLE")                            # not the HIDDEN it came with
        self.assertEqual(s.made[0].scaleValue, 0.05)

    def test_the_isometric_scale_seen_live_counts_as_set_and_is_printed_in_full(self):
        # live 2026-11-01, GA sheet 1: the isometric view at 0.0375 was refused by the old 1e-9 check ("stays
        # 0.0375 after setting 0.0375", 6 digits: 1e-9 to 5e-8 off); 1:5 (ELECTRICAL's 711001) and 1:20 passed it
        for off in (2e-9, 2e-8, 5e-8):                       # within what the 6-digit print allows
            s = self.sheet(reads_back={0.0375: 0.0375 + off, 0.2: 0.2, 0.05: 0.05})
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                v = fd.base_view(s, "ISO", 0.0375, (720.0, 430.0))
                fd.base_view(s, "FRONT", 0.2, (265.0, 410.0))
                fd.base_view(s, "TOP", 0.05, (265.0, 235.0))
            self.assertGreater(abs(v.scaleValue - 0.0375), 1e-9)                  # the old check refused it
            self.assertIn("read back %r" % (0.0375 + off), out.getvalue())       # every digit in the run's log
            self.assertEqual(out.getvalue().count("view scale: asked"), 3)

    def test_a_view_that_keeps_another_scale_is_still_an_error(self):
        with self.assertRaises(RuntimeError) as cm:
            with contextlib.redirect_stdout(io.StringIO()):
                fd.base_view(self.sheet(keeps_scale=0.05), "FRONT", 0.0375, (265.0, 410.0))
        self.assertIn("0.05", str(cm.exception))
        self.assertFalse(fd.scale_is(0.05, 0.0375))
        self.assertFalse(fd.scale_is(0.0375 * (1 + 1e-4), 0.0375))     # a real difference, however small
        self.assertFalse(fd.scale_is(0.0375 * (1 + 3e-5), 0.0375))     # and nothing looser than 1e-5 passes
        self.assertFalse(fd.scale_is(1 / 26.67, 1 / 26.7))             # neighbouring scales stay apart
        self.assertTrue(fd.scale_is(1 / 26.6667, 0.0375))              # 1.25e-6 off: taken (1e-6 refused it)

    def test_a_view_made_at_another_scale_is_set_again(self):
        # the README's 1:10 trap: Fusion can ignore the input's scale; the helper sets it again on the made view
        s = self.sheet(ignores_input=True)
        with contextlib.redirect_stdout(io.StringIO()):
            v = fd.base_view(s, "FRONT", 0.1, (265.0, 410.0))
        self.assertEqual(v.sets, [0.1])
        self.assertEqual(v.scaleValue, 0.1)

    def test_a_view_that_keeps_hidden_lines_is_an_error(self):
        with self.assertRaises(RuntimeError):
            fd.base_view(self.sheet(view_stuck=True), "FRONT", 0.05, (265.0, 410.0))

    # 4. the same dimension placed twice
    def test_the_same_dimension_is_placed_once(self):
        s = self.sheet()
        ds = fd.DimensionSet(s, log=lambda m: None)
        a, b = P(202.5, 350.0), P(327.5, 350.0)
        self.assertEqual(ds.linear(a, b, P(265.0, 338.0)), "dim")
        self.assertIsNone(ds.linear(b, a, P(265.0, 330.0)))             # same points, other order
        self.assertEqual(len(s.dims), 1)

    def test_a_width_and_a_height_between_the_same_points_are_both_placed(self):
        s = self.sheet()
        ds = fd.DimensionSet(s, log=lambda m: None)
        a, b = P(0.0, 0.0), P(10.0, 20.0)
        ds.linear(a, b, P(5.0, -8.0))                                   # below: the width
        ds.linear(a, b, P(-8.0, 10.0))                                  # left: the height
        self.assertEqual(len(s.dims), 2)

    def test_a_sheet_with_dimensions_from_an_earlier_run_is_refused(self):
        with self.assertRaises(RuntimeError):
            fd.DimensionSet(self.sheet(dims=4))
        fd.DimensionSet(self.sheet(dims=4), allow_existing=True)


class SharedModuleTests(unittest.TestCase):
    def test_every_script_run_through_the_runner_can_import_it(self):
        script = ("from fusion_drawing import insert_image, first_angle_symbol, base_view, DimensionSet\n"
                  "def run(_c):\n    RESULT.append(insert_image.__module__)\n")
        wrapped = rs.wrap_script(script, "/x/team_script.py", {})
        result, ns = [], {}
        keep = {k: sys.modules.get(k) for k in ("fusion_drawing", "fusion_folder")}
        try:
            exec(compile(wrapped, "wrapper", "exec"), ns)
            ns["_NS"]["RESULT"] = result
            ns["run"](None)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        self.assertEqual(result, ["fusion_drawing"])

    def test_the_runner_sends_this_same_text(self):
        with open(os.path.join(HERE, "fusion_drawing.py"), encoding="utf-8") as fh:
            self.assertEqual(rs.DRAWING_HELPER_SRC, fh.read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
