"""Offline checks of the INTERIOR layout (no Fusion needed).

    python3 v2/01-CAD-Native/interior/test_interior_offline.py

Same parameters as the Fusion build (interior_model.py, with the skeleton's CSV and the
ceiling's parameters): the light shelf sits along the side and back wall tops under the felt
ceiling and behind the soffit, inside the D-85 budget of 0.4 kg/m with its strips; the ledge
is 1000 long in the right wall's free length, stands off the floating lining and its
brackets land on WALL's stiles; the cable holes are at ELECTRICAL's points; numbers in band.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import interior_model as I  # noqa: E402
import ceiling_model as CM  # noqa: E402

V = I.evaluate()
B = I.boxes(V)


def b6(n):
    return B[n][1]


def gap(a, b):
    return max(max(b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]) for i in range(3))


class Shelf(unittest.TestCase):
    def test_place(self):
        xir, ybl = V["pod_w"] / 2 - V["stack_t"], V["pod_d"] / 2 - V["stack_t"]
        felt = V["pod_h"] - V["stack_t"]
        soffit_back = V["pod_d"] / 2 - V["wall_depth"] + V["cs_front"]
        for n in ("LIGHT SHELF BACK", "LIGHT SHELF LH", "LIGHT SHELF RH", "DOWN CHANNEL RH"):
            b = b6(n)
            self.assertLess(b[5], felt - 30.0, n + " clear of the felt ceiling")
            self.assertGreaterEqual(b[2], soffit_back - 1e-9, n + " behind the soffit")
            self.assertLessEqual(b[1], xir + 1e-9)
            self.assertGreaterEqual(b[0], -xir - 1e-9)
            self.assertLessEqual(b[3], ybl + 1e-9)

    def test_budget(self):
        """D-85: 0.4 kg/m with the strips, averaged over the shelf's length."""
        al, pc = I.MATERIALS["al"][1], I.MATERIALS["pc"][1]
        a_shelf = I.section_area(V, I.shelf_section(I.XIR, -1, "xz"))
        a_dc = I.section_area(V, I.down_channel_section())
        lb = b6("LIGHT SHELF BACK")[1] - b6("LIGHT SHELF BACK")[0]
        ls = b6("LIGHT SHELF RH")[3] - b6("LIGHT SHELF RH")[2]
        length = lb + 2 * ls
        kg = a_shelf * length * 1e-9 * al + a_dc * ls * 1e-9 * al
        kg += (V["dc_w"] - 2 * V["sh_t"]) * V["df_t"] * ls * 1e-9 * pc
        kg += I.STRIP_KG_M[0] * (length + 2 * ls) * 1e-3
        self.assertLessEqual(kg / (length * 1e-3), 0.4, "%.3f kg/m" % (kg / (length * 1e-3)))

    def test_cable_points(self):
        f = dict((n, a) for n, _k, a in I.features())
        self.assertAlmostEqual(I.ev(V, f["LIGHT SHELF BACK"][0]), 355.0)
        self.assertAlmostEqual(I.ev(V, f["LIGHT SHELF RH"][1]), -209.5)
        for n, a in f.items():
            b = b6(n)
            z = V["cab_z"]
            self.assertTrue(b[4] + V["sh_t"] + V["cab_d"] / 2 <= z <= V["sh_z0"] + V["sh_hb"] - V["cab_d"] / 2, n)


class Ledge(unittest.TestCase):
    def test_size_and_place(self):
        b = b6("LEDGE TOP")
        self.assertAlmostEqual(b[3] - b[2], 1000.0)
        free0 = V["pod_d"] / 2 - V["wall_depth"] + V["cs_front"]
        free1 = V["pod_d"] / 2 - V["stack_t"]
        self.assertGreaterEqual(b[2], free0)
        self.assertLessEqual(b[3], free1)
        xir = V["pod_w"] / 2 - V["stack_t"]
        self.assertAlmostEqual(xir - b[1], V["lg_gap"], msg="stands off the floating lining")

    def test_brackets_on_stiles_and_under_the_ledge(self):
        top = b6("LEDGE TOP")
        for n in ("LEDGE BRACKET 1", "LEDGE BRACKET 2"):
            b = b6(n)
            self.assertTrue(top[2] < b[2] and b[3] < top[3], n)
            self.assertAlmostEqual(b[5], top[5] - V["lg_t"])
        ys = sorted((b6(n)[2] + b6(n)[3]) / 2 for n in ("LEDGE BRACKET 1", "LEDGE BRACKET 2"))
        self.assertAlmostEqual(ys[0], 98.63)
        self.assertAlmostEqual(ys[1], 464.32)

    def test_budget(self):
        kg = I.section_area(V, I.ledge_section()) * V["lg_l"] * 1e-9 * I.MATERIALS["al"][1] + 2 * I.HOLD_MASS["bracket"][0]
        self.assertLessEqual(kg, 1.4 + 0.02, "%.2f kg" % kg)


class Fits(unittest.TestCase):
    def test_no_overlaps(self):
        names = list(B)
        # boxes of the U sections hold what sits inside them: the diffuser in the down channel,
        # the brackets under the ledge's top, between its folds (Fusion's clash check sees solids)
        allowed = {("DOWN CHANNEL RH", "DIFFUSER RH"), ("LEDGE TOP", "LEDGE BRACKET 1"), ("LEDGE TOP", "LEDGE BRACKET 2")}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if (a, b) in allowed or (b, a) in allowed:
                    continue
                self.assertGreaterEqual(gap(b6(a), b6(b)), -1e-9, "%s overlaps %s" % (a, b))

    def test_clear_of_the_column(self):
        x0 = 949.0
        for n, (_k, b) in B.items():
            col = (x0, V["pod_w"] / 2 - V["stack_t"], V["pod_d"] / 2 - V["wall_depth"],
                   V["pod_d"] / 2 - V["wall_depth"] + V["cs_front"], 0.0, 2120.0)
            self.assertGreaterEqual(gap(b, col), -1e-9, n)


class Numbers(unittest.TestCase):
    def test_bands(self):
        seen = set()
        for key, (pn, name, vn, kind, mat) in I.PARTS.items():
            self.assertTrue(pn.startswith("81"), key)
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
            self.assertTrue(name.startswith("INTERIOR"), key)


if __name__ == "__main__":
    unittest.main(verbosity=1)
