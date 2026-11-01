#!/usr/bin/env python3
"""Offline test of GA sheet 1's layout, before it costs a Fusion run.

    python3 v2/02-Drawings/00-General-Assembly/test_ga_layout.py

ga_elevations.py places its views by centre point and can't move them after
(API limit), so the layout must be right the first time: at 1:20 on A1 every
view fits inside the frame, no two views touch (room for dimensions), none
covers the title block, and the views sit in ISO first-angle order. The pod's
size comes from the skeleton's parameter table, so a skeleton change that
would push a view off the sheet fails here.
"""

import csv
import math
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "fusion"))          # fusion_drawing, as the runner gives it
CSV = os.path.join(REPO, "v2", "01-CAD-Native", "skeleton", "100000_P04_POD-SKELETON-PARAMETERS.csv")

SHEET = (841.0, 594.0)                 # A1 landscape, ISO 5457
FRAME = (20.0, 10.0, 831.0, 584.0)     # ISO 5457 frame: 20 mm filing margin at the left, 10 elsewhere (assumption: Fusion's A1 frame follows it)
TITLE_BLOCK = (651.0, 10.0, 831.0, 80.0)   # ISO 7200 title block, 180 mm wide at the bottom right (assumption: up to 70 mm tall)
MIN_GAP = 20.0                          # space between views for dimension lines (assumption)


def load_layout(full=False):
    """LAYOUT and SCALE from ga_elevations.py, run with a stand-in for Fusion's adsk
    (with full=True, the whole namespace)."""
    vo = types.SimpleNamespace(**{n: n for n in (
        "FrontViewOrientationType", "BackViewOrientationType", "LeftViewOrientationType",
        "RightViewOrientationType", "TopViewOrientationType", "IsoTopRightViewOrientationType")})
    adsk = types.ModuleType("adsk")
    adsk.core = types.ModuleType("adsk.core")
    adsk.drawing = types.ModuleType("adsk.drawing")
    adsk.drawing.ViewOrientationTypes = vo
    adsk.fusion = types.ModuleType("adsk.fusion")
    keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing", "adsk.fusion")}
    sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing,
                        "adsk.fusion": adsk.fusion})
    try:
        ns = {"__name__": "ga_elevations", "SCRIPT_ARGS": {"repo_root": REPO}}
        with open(os.path.join(HERE, "ga_elevations.py"), encoding="utf-8") as fh:
            exec(compile(fh.read(), "ga_elevations.py", "exec"), ns)
    finally:
        for k, v in keep.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return ns if full else (ns["LAYOUT"], ns["SCALE"])


def pod_size():
    with open(CSV, encoding="utf-8") as fh:
        rows = {r["parameter"]: float(r["value"]) for r in csv.DictReader(fh)}
    return rows["pod_w"], rows["pod_d"], rows["pod_h"]


def boxes():
    """{view: (x0, y0, x1, y1)} in sheet mm, each view centred on its point."""
    layout, scale = load_layout()
    w, d, h = pod_size()
    out = {}
    for name, _orientation, (cx, cy) in layout:
        if name in ("front", "back"):
            bw, bh = w * scale, h * scale
        elif name in ("left", "right"):
            bw, bh = d * scale, h * scale
        elif name == "top":
            bw, bh = w * scale, d * scale
        else:                                   # isometric at 0.75 x the scale
            s = scale * 0.75
            bw = (w + d) * math.cos(math.radians(30)) * s
            bh = (h + (w + d) * math.sin(math.radians(30))) * s
        out[name] = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
    return out


def gap(a, b):
    """Clear distance between two boxes (0 or less when they touch)."""
    dx = max(b[0] - a[2], a[0] - b[2])
    dy = max(b[1] - a[3], a[1] - b[3])
    return max(dx, dy)


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.b = boxes()

    def test_every_view_is_inside_the_frame(self):
        for name, (x0, y0, x1, y1) in self.b.items():
            self.assertTrue(FRAME[0] <= x0 and x1 <= FRAME[2] and FRAME[1] <= y0 and y1 <= FRAME[3],
                            "%s view %s is outside the frame %s" % (name, (x0, y0, x1, y1), FRAME))

    def test_views_keep_room_for_dimensions(self):
        names = sorted(self.b)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                self.assertGreaterEqual(gap(self.b[a], self.b[b]), MIN_GAP, "%s and %s" % (a, b))

    def test_no_view_covers_the_title_block(self):
        for name, box in self.b.items():
            self.assertGreater(gap(box, TITLE_BLOCK), 0, name)

    def test_first_angle_order(self):
        c = {n: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for n, b in self.b.items()}
        # ISO first angle: the view from the right sits left of the front view, the
        # view from the left right of it, the view from above below it
        self.assertLess(c["right"][0], c["front"][0])
        self.assertLess(c["front"][0], c["left"][0])
        self.assertLess(c["left"][0], c["back"][0])
        self.assertLess(c["top"][1], c["front"][1])
        self.assertAlmostEqual(c["top"][0], c["front"][0])
        for n in ("right", "left", "back"):
            self.assertAlmostEqual(c[n][1], c["front"][1])

    def test_the_notes_keep_clear_of_the_views_the_title_block_and_the_symbol(self):
        ns = load_layout(full=True)
        x, y = ns["NOTES_AT"]
        notes = (x, y, x + ns["NOTES_WIDTH"], y + ns["NOTES_MAX_HEIGHT"])
        self.assertTrue(FRAME[0] <= notes[0] and notes[2] <= FRAME[2] and FRAME[1] <= notes[1]
                        and notes[3] <= FRAME[3], notes)
        for name, box in self.b.items():
            self.assertGreaterEqual(gap(box, notes), 10.0, name)
        self.assertGreater(gap(notes, TITLE_BLOCK), 0)
        symbol = (560.0, 35.0, 589.0, 45.0)                    # step_dims draws it there
        self.assertGreater(gap(notes, symbol), 0)

    def test_a_notes_picture_taller_than_its_box_is_refused(self):
        # 2026-11-01: the D-132 note made the picture 115.7 mm tall, past the 110 the layout
        # test had kept for it, and nothing checked; step_notes now measures the PNG first
        import struct
        import tempfile
        ns = load_layout(full=True)

        def png(w, h):
            fd, path = tempfile.mkstemp(suffix=".png")
            with os.fdopen(fd, "wb") as fh:
                fh.write(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h))
            self.addCleanup(os.remove, path)
            return path

        self.assertAlmostEqual(ns["png_height_mm"](png(3308, 1367), 280.0), 115.7, places=1)
        placed = []
        ns["insert_image"] = lambda *a: placed.append(a) or 1.0
        x, y = ns["NOTES_AT"]
        ns["ARGS"].update(notes_px=str(x), notes_py=str(y))
        ns["ARGS"]["notes_png"] = png(1000, 600)                  # 168 mm tall at 280 wide
        with self.assertRaises(RuntimeError):
            ns["step_notes"](None)
        self.assertEqual(placed, [])
        ns["ARGS"]["notes_png"] = png(3308, 1367)                 # 115.7 mm: fits
        ns["step_notes"](None)
        self.assertEqual(len(placed), 1)

    def test_the_section_view_lands_where_the_hatch_first_mode_predicts(self):
        # live B-B, 2026-11-01: placed at (230, 230), its extent was (167.5, 170, 292.5, 290) for the
        # design's 2500 x 2400 box (x by z) at 1:20; the hatch-first mode draws for this place before the view
        vo = types.SimpleNamespace(FrontViewOrientationType="F", LeftViewOrientationType="L")
        adsk = types.ModuleType("adsk")
        adsk.core = types.ModuleType("adsk.core")
        adsk.drawing = types.ModuleType("adsk.drawing")
        adsk.drawing.ViewOrientationTypes = vo
        adsk.fusion = types.ModuleType("adsk.fusion")
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing", "adsk.fusion")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing,
                            "adsk.fusion": adsk.fusion})
        try:
            ns = {"__name__": "ga_section_sheet", "SCRIPT_ARGS": {"repo_root": REPO}}
            with open(os.path.join(HERE, "ga_section_sheet.py"), encoding="utf-8") as fh:
                exec(compile(fh.read(), "ga_section_sheet.py", "exec"), ns)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        lo, hi = [-1250.0, 0.0, 0.0], [1250.0, 850.0, 2400.0]
        _name, _o, center, _axis, (sx, sy) = ns["SECTIONS"]["BB"]
        self.assertEqual(ns["predicted_extent"](center, lo, hi, sx, sy), (167.5, 170.0, 292.5, 290.0))
        _name, _o, center, _axis, (sx, sy) = ns["SECTIONS"]["AA"]           # sheet x along -Y: 1700 deep
        lo, hi = [-200.0, -850.0, 0.0], [1250.0, 850.0, 2400.0]
        self.assertEqual(ns["predicted_extent"](center, lo, hi, sx, sy), (187.5, 170.0, 272.5, 290.0))

    def test_overall_sizes_are_measured_between_the_true_extremes(self):
        # live 2026-10-31: the end point nearest a corner of the extent gave 2390 for 2400
        # and 1602 for 1700 on the faceted front; now the extreme end points, checked
        ns = load_layout(full=True)
        P = types.SimpleNamespace
        pts = [P(coordinate=P(x=x, y=y)) for x, y in ((0, 5), (3, 0), (10, 1), (9, 12), (1, 11))]
        lo_x, hi_x, lo_y, hi_y = (ns["xy"](p) for p in (lambda v: [min(pts, key=lambda p: p.coordinate.x),
                                                                     max(pts, key=lambda p: p.coordinate.x),
                                                                     min(pts, key=lambda p: p.coordinate.y),
                                                                     max(pts, key=lambda p: p.coordinate.y)])(None))
        ns["line_ends"] = lambda view: pts                          # the view's curve end points
        got = [ns["xy"](p) for p in ns["extremes"](None)]
        self.assertEqual(got, [lo_x, hi_x, lo_y, hi_y])
        self.assertEqual(got, [(0, 5), (10, 1), (3, 0), (9, 12)])

    def test_the_symbol_is_a_closed_trapezoid_and_the_pdf_check_expects_it(self):
        ns = load_layout(full=True)
        sides = ns["SYMBOL_SIDES"]
        self.assertEqual(len(sides), 4)
        for k in range(4):                                       # each side starts where the last ended
            self.assertEqual(sides[k][1], sides[(k + 1) % 4][0])
        ends = sorted({p for s in sides for p in s})
        self.assertEqual(ends, [(560.0, 37.5), (560.0, 42.5), (570.0, 35.0), (570.0, 45.0)])
        sys.path.insert(0, HERE)
        import ga_pdf_check
        self.assertEqual(ns["SYMBOL_SIDES"], ga_pdf_check.SYMBOL)
        import fusion_drawing                                     # the shared helper draws this outline
        ring = fusion_drawing.symbol_outline(ns["_X0"], ns["_CY"], ns["_D"], ns["_BIG"], ns["_LEN"])
        self.assertEqual(ring, [sides[0][0]] + [b for _a, b in sides])

    def test_the_sizes_come_from_the_skeleton(self):
        w, d, h = pod_size()
        self.assertEqual((w, d, h), (2500.0, 1700.0, 2400.0))   # D-01, D-21
        fx0, _, fx1, _ = self.b["front"]
        self.assertAlmostEqual(fx1 - fx0, 125.0)                 # 2500 at 1:20


if __name__ == "__main__":
    unittest.main(verbosity=2)
