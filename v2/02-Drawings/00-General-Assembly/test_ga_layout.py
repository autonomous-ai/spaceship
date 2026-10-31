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
CSV = os.path.join(REPO, "v2", "01-CAD-Native", "skeleton", "100000_P04_POD-SKELETON-PARAMETERS.csv")

SHEET = (841.0, 594.0)                 # A1 landscape, ISO 5457
FRAME = (20.0, 10.0, 831.0, 584.0)     # ISO 5457 frame: 20 mm filing margin at the left, 10 elsewhere (assumption: Fusion's A1 frame follows it)
TITLE_BLOCK = (651.0, 10.0, 831.0, 80.0)   # ISO 7200 title block, 180 mm wide at the bottom right (assumption: up to 70 mm tall)
MIN_GAP = 20.0                          # space between views for dimension lines (assumption)


def load_layout():
    """LAYOUT and SCALE from ga_elevations.py, run with a stand-in for Fusion's adsk."""
    vo = types.SimpleNamespace(**{n: n for n in (
        "FrontViewOrientationType", "BackViewOrientationType", "LeftViewOrientationType",
        "RightViewOrientationType", "TopViewOrientationType", "IsoTopRightViewOrientationType")})
    adsk = types.ModuleType("adsk")
    adsk.core = types.ModuleType("adsk.core")
    adsk.drawing = types.ModuleType("adsk.drawing")
    adsk.drawing.ViewOrientationTypes = vo
    keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing")}
    sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing})
    try:
        ns = {"__name__": "ga_elevations"}
        with open(os.path.join(HERE, "ga_elevations.py"), encoding="utf-8") as fh:
            exec(compile(fh.read(), "ga_elevations.py", "exec"), ns)
    finally:
        for k, v in keep.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return ns["LAYOUT"], ns["SCALE"]


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

    def test_the_sizes_come_from_the_skeleton(self):
        w, d, h = pod_size()
        self.assertEqual((w, d, h), (2500.0, 1700.0, 2400.0))   # D-01, D-21
        fx0, _, fx1, _ = self.b["front"]
        self.assertAlmostEqual(fx1 - fx0, 125.0)                 # 2500 at 1:20


if __name__ == "__main__":
    unittest.main(verbosity=2)
