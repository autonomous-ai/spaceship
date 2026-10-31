"""Offline checks of the AIR layout (no Fusion needed).

    python3 v2/01-CAD-Native/air/test_air_offline.py

Same parameters as the Fusion build (air_model.py, with the skeleton's own CSV).
Checks the D-61 sizes, that the parts don't overlap, that each cartridge keeps
its 5 mm clearance, that the column and soffit sit inside the pod's lining faces
and meet the ceiling cassettes and the roof frame as planned, and that the roof
sleeve passes through the right outer ceiling panel clear of its members.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import air_model as A  # noqa: E402
import ceiling_model as CM  # noqa: E402

V = A.evaluate()
LAY = {name: (key, tuple(A.ev(V, e) for e in bx)) for key, name, bx in A.layout()}


def b6(name):
    return LAY[name][1]


def gap(a, b):
    return max(max(b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]) for i in range(3))


class Sizes(unittest.TestCase):
    def test_d61(self):
        col = b6("COLUMN FACE FRONT")
        self.assertAlmostEqual(col[1] - col[0], V["pod_w"] / 2 - V["stack_t"] - 949.0)
        sof = b6("SOFFIT FACE FRONT")
        self.assertAlmostEqual(sof[5] - sof[4], 220.0)
        self.assertAlmostEqual(sof[4], 2120.0)
        self.assertAlmostEqual(sof[1] - sof[0], V["pod_w"] - 2 * V["stack_t"])
        for name in ("CARTRIDGE SUPPLY", "CARTRIDGE EXHAUST"):
            b = b6(name)
            dims = sorted((b[1] - b[0], b[3] - b[2], b[5] - b[4]))
            self.assertEqual([round(d, 6) for d in dims], [173.0, 314.0, 1750.0], name)
        self.assertAlmostEqual(V["pass_w"], 80.0)
        slot = b6("ROOF SLEEVE")
        self.assertAlmostEqual(slot[1] - slot[0], 285.0)
        self.assertAlmostEqual(slot[3] - slot[2], 294.0)
        self.assertAlmostEqual(slot[2], -620.0)
        self.assertAlmostEqual(slot[3], -326.0)

    def test_column_in_corner(self):
        xir = V["pod_w"] / 2 - V["stack_t"]
        yw = V["pod_d"] / 2 - V["wall_depth"]
        for name in ("COLUMN FACE FRONT", "COLUMN FACE LEFT", "CARTRIDGE SUPPLY", "COLUMN FILL FRONT",
                     "COLUMN FILL LEFT", "KICK GRILLE FRONT", "KICK GRILLE LEFT"):
            b = b6(name)
            self.assertGreaterEqual(b[0], 949.0 - 1e-9, name)
            self.assertLessEqual(b[1], xir + 1e-9, name)
            self.assertGreaterEqual(b[2], yw - 1e-9, name)
            self.assertLessEqual(b[3], yw + V["col_d"] + 1e-9, name)
            self.assertGreaterEqual(b[4], V["floor_t"] - 1e-9, name)
            self.assertLessEqual(b[5], V["dt_zb"] + 1e-9, name)


class Fits(unittest.TestCase):
    def test_no_overlaps(self):
        """No two layout bodies overlap, except the cut-outs the build makes (hub zone in
        the front face and the fill, exhaust grille in the underside)."""
        cut = {(t, "SENSOR HUB ZONE") for t in ("COLUMN FACE FRONT", "COLUMN FILL FRONT")} | {("SOFFIT UNDERSIDE", "EXHAUST GRILLE")}
        names = list(LAY)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if (a, b) in cut or (b, a) in cut:
                    continue
                self.assertGreaterEqual(gap(b6(a), b6(b)), -1e-9, "%s overlaps %s" % (a, b))

    def test_cartridge_clearance(self):
        xir = V["pod_w"] / 2 - V["stack_t"]
        yw = V["pod_d"] / 2 - V["wall_depth"]
        c = b6("CARTRIDGE SUPPLY")
        self.assertAlmostEqual(xir - c[1], 5.0)
        self.assertAlmostEqual(c[2] - yw, 5.0)
        e = b6("CARTRIDGE EXHAUST")
        self.assertAlmostEqual(e[2] - yw, 5.0)
        self.assertAlmostEqual(e[1], b6("EXHAUST FAN BOX")[0])      # the cartridge feeds the fan box

    def test_soffit_meets_ceiling(self):
        """The ceiling cassettes start 3 mm behind the soffit's front face; the soffit's top
        stays under the roof frame; the soffit and the column are flush at the front."""
        cv = CM.evaluate(CM.all_params())
        sof = b6("SOFFIT FACE FRONT")
        cass_front = CM.ev(cv, CM.CASSETTE_CS["C1"][1]) + cv["cs_gap"]
        self.assertAlmostEqual(cass_front - sof[3], cv["cs_gap"])
        self.assertAlmostEqual(cv["cs_front"], V["col_d"])
        roof = V["pod_h"] - V["outer_t"]
        self.assertGreater(roof - sof[5], 10.0)
        self.assertAlmostEqual(b6("COLUMN FACE FRONT")[3], sof[3])

    def test_sleeve_clear_of_ceiling_members(self):
        cv = CM.evaluate(CM.all_params())
        s = b6("ROOF SLEEVE")
        for code, _n, _a, b in CM.frame_members("C2"):
            m = tuple(CM.ev(cv, e) for e in b)
            self.assertGreaterEqual(gap(s, m), 5.0 - 1e-9, "sleeve too close to C2 " + code)
        self.assertAlmostEqual(s[5], V["pod_h"])
        self.assertAlmostEqual(s[4], b6("EXHAUST FAN BOX")[5])

    def test_fans_inside_boxes(self):
        boxes = {"SUPPLY": b6("SUPPLY FAN BOX"), "EXHAUST": b6("EXHAUST FAN BOX")}
        for name, x, y, z in A.fan_points():
            bx = boxes[name.split()[0]]
            cx, cy, cz = A.ev(V, x), A.ev(V, y), A.ev(V, z)
            h = V["fan_s"] / 2
            self.assertGreaterEqual(cx - h, bx[0] + V["box_t"] - 1e-9, name)
            self.assertLessEqual(cx + h, bx[1] - V["box_t"] + 1e-9, name)
            self.assertGreaterEqual(cy - h, bx[2] + V["box_t"] - 1e-9, name)
            self.assertLessEqual(cy + h, bx[3] - V["box_t"] + 1e-9, name)
            self.assertLessEqual(cz + V["fan_t"], bx[5] - V["box_t"] + 1e-9, name)


class Numbers(unittest.TestCase):
    def test_bands(self):
        seen = set()
        for key, (pn, name, vn, kind, mat) in A.PARTS.items():
            self.assertTrue(pn.startswith("61"), key)
            self.assertNotIn(pn, CM.RESERVED)
            self.assertNotIn(pn, seen)
            seen.add(pn)
            n = int(pn[2:])
            if kind == "HS":
                self.assertLessEqual(n, 999, key)
            elif kind == "MP":
                self.assertTrue(1000 <= n <= 7999, key)
            else:
                self.assertTrue(8000 <= n <= 8999, key)


if __name__ == "__main__":
    unittest.main(verbosity=1)
