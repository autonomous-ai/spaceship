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
        for n in ("LIGHT SHELF BACK", "LIGHT SHELF LH", "LIGHT SHELF RH", "LED PROFILE RH"):
            b = b6(n)
            self.assertLess(b[5], felt - 30.0, n + " clear of the felt ceiling")
            self.assertGreaterEqual(b[2], soffit_back - 1e-9, n + " behind the soffit")
            self.assertLessEqual(b[1], xir + 1e-9)
            self.assertGreaterEqual(b[0], -xir - 1e-9)
            self.assertLessEqual(b[3], ybl + 1e-9)

    def test_budget(self):
        """D-85: 0.4 kg/m with the strips, averaged over the shelf's length; D-126 accepts up to 0.41 for this
        shelf with the bought LED profile (its real mass replaces the estimate once ELECTRICAL names it)."""
        al = I.MATERIALS["al"][1]
        a_shelf = I.section_area(V, I.shelf_section(I.XIR, -1, "xz"))
        lb = b6("LIGHT SHELF BACK")[1] - b6("LIGHT SHELF BACK")[0]
        ls = b6("LIGHT SHELF RH")[3] - b6("LIGHT SHELF RH")[2]
        lp = b6("LED PROFILE RH")[3] - b6("LED PROFILE RH")[2]
        length = lb + 2 * ls
        kg = a_shelf * length * 1e-9 * al
        # D-126: the bought profile set under the right run (its masses are assumptions until it is named)
        hm = I.HOLD_MASS
        kg += hm["lprofile"][0] + hm["lcover"][0] + 2 * hm["lcap"][0] + 4 * hm["lclip"][0]
        kg += I.STRIP_KG_M[0] * (length + 2 * lp) * 1e-3
        self.assertLessEqual(kg / (length * 1e-3), 0.41, "%.3f kg/m" % (kg / (length * 1e-3)))

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
        allowed = {("LEDGE TOP", "LEDGE BRACKET 1"), ("LEDGE TOP", "LEDGE BRACKET 2")}
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


class FitGaps(unittest.TestCase):
    """D-174 (the PM's ruling 2026-11-01): no shelf run is cut to the exact gap it fits in. Each stops sh_fit (1.25) short
    of both faces: the side runs of the soffit face and the back run's lip, the back run of the two side linings."""

    def test_runs_stop_short_of_their_faces(self):
        g = V["sh_fit"]
        self.assertGreaterEqual(g, 1.0)
        self.assertLessEqual(g, 1.5)
        back, lh, rh = b6("LIGHT SHELF BACK"), b6("LIGHT SHELF LH"), b6("LIGHT SHELF RH")
        yface, ybl, xil, xir = (I.ev(V, e) for e in (I.YFACE, I.YBL, I.XIL, I.XIR))
        for side in (lh, rh):
            self.assertAlmostEqual(side[2] - yface, g, msg="off the soffit face")
            self.assertAlmostEqual((ybl - V["sh_d"]) - side[3], g, msg="off the back run's lip")
            self.assertAlmostEqual(side[3] - side[2], 991.0 - 2 * g)
        self.assertAlmostEqual(back[0] - xil, g, msg="off the left lining")
        self.assertAlmostEqual(xir - back[1], g, msg="off the right lining")
        self.assertAlmostEqual(back[1] - back[0], 2332.0 - 2 * g)


class DownLight(unittest.TestCase):
    """D-126: the LED profile under the right run takes ELECTRICAL's two 8 mm strips (20 inside or more),
    runs the side run's own length (from the soffit's face to the corner joint), so every clip fixes to
    the side run and no end shows past it (Reviewer 6), and sits under the shelf, 15 off the lining."""

    def test_profile(self):
        b = b6("LED PROFILE RH")
        side = b6("LIGHT SHELF RH")
        self.assertGreaterEqual(V["lp_in"], 2 * 8.0 + 4.0 - 1e-9, "two 8 mm strips with room")
        self.assertAlmostEqual(b[3] - b[2], 991.0 - 2 * V["sh_fit"], msg="988.5 long: the run's 991 less its fit gaps (D-174)")
        self.assertAlmostEqual(b[2], side[2], msg="from the run's end by the soffit's face")
        self.assertAlmostEqual(b[3], side[3], msg="to the side run's end: nothing past it")
        self.assertGreaterEqual(b[0], side[0] - 1e-9, "within the side run's bottom")
        led = b6("LEDGE TOP")
        self.assertLessEqual(b[2], led[2])
        # 35.75 with the run's D-174 fit gap (the profile stops 1.25 sooner); 34.5 before it
        self.assertLessEqual(led[3] - b[3], 36.0, "the ledge's last 35.75 lit from beside it")
        xir = V["pod_w"] / 2 - V["stack_t"]
        self.assertAlmostEqual(xir - b[1], V["lp_x0"])
        self.assertAlmostEqual(b[5], V["sh_z0"], msg="on the shelf's underside")
        self.assertAlmostEqual(b[5] - b[4], V["lp_h"])


class Folds(unittest.TestCase):
    """Real folds (the Lead's ruling 2026-11-01 on #335): each fold of the bent parts has its inside corner filleted to
    the sheet and its outside corner to twice the sheet, so the model, its STEP and its DXF (K 0.44) agree; the DXF's
    cable holes sit on the back flange's straight run, where the model puts them."""

    def sections(self):
        lay = {key: (name, kind, data) for key, name, kind, data in I.layout()}
        return {k: (lay[k][0], [(I.ev(V, u), I.ev(V, z)) for u, z in lay[k][2][0]]) for k in I.BENT}

    def test_folds_at_the_corners(self):
        for key, (name, pts) in self.sections().items():
            t, r = (V["lg_t"], V["lg_r"]) if key == "ledge" else (V["sh_t"], V["sh_r"])
            self.assertAlmostEqual(r, t, msg="inside radius = the sheet (the Lead's ruling)")
            bs = I.bends(key)
            self.assertEqual(sorted(i for i, _s, _r in bs), [0, 1, 4, 5], name)
            for i, side, rexpr in bs:
                self.assertAlmostEqual(I.ev(V, rexpr), r if side == "inside" else r + t, msg=(name, i))
            # each outside corner's inside partner sits one sheet in on both axes: the fold's centre is shared
            for o, n in ((0, 5), (1, 4)):
                (uo, zo), (ui, zi) = pts[o], pts[n]
                self.assertAlmostEqual(abs(uo - ui), t, msg=(name, o, n))
                self.assertAlmostEqual(abs(zo - zi), t, msg=(name, o, n))
            # the straight runs stay longer than the fold zones (r + t each end)
            for a, b in zip(pts, pts[1:] + pts[:1]):
                length = abs(a[0] - b[0]) + abs(a[1] - b[1])
                if length > t + 1e-9:
                    self.assertGreater(length, 2 * (r + t), (name, a, b))

    def test_dxf_holes_on_the_back_flange(self):
        import interior_exports as E
        lay = {name: data for _key, name, _kind, data in I.layout()}
        for key, name, n in (("shelf_back", "LIGHT SHELF BACK", 1), ("shelf_lh", "LIGHT SHELF LH", 0),
                             ("shelf_rh", "LIGHT SHELF RH", 1)):
            t, r = V["sh_t"], V["sh_r"]
            _w, bends = E.blank([V["sh_hb"], V["sh_d"], V["sh_hl"]], t, r)
            ba = 3.141592653589793 / 2 * (r + E.K * t)
            holes = E.flat_holes(V, key, name, lay[name][1], lay[name][2])
            self.assertEqual(len(holes), n, name)
            for x, y, rad in holes:
                self.assertAlmostEqual(y, 20.0, msg=name)       # the 40 flange, 20 from its free edge
                self.assertGreater(y - rad, 0.0, name)
                self.assertLess(y + rad, bends[0] - ba / 2, "%s: the hole reaches the first fold's zone" % name)
                self.assertGreater(x - rad, 0.0, name)

    def test_brackets_clear_the_inside_bend(self):
        """The bracket envelope's top back corner sits at the ledge's inside fold corner; a fillet of radius r there
        fills only the corner triangle u + w > -r, so a 45 deg relief br_rel of r or more keeps them apart."""
        cx, cz = [(I.ev(V, u), I.ev(V, z)) for u, z in I.ledge_section()][4]
        self.assertGreaterEqual(V["br_rel"], V["lg_r"] + 1.0)
        for key, name, kind, data in I.layout():
            if key != "bracket":
                continue
            pts = [(I.ev(V, u), I.ev(V, z)) for u, z in data[0]]
            self.assertAlmostEqual(max(p[0] for p in pts), cx, msg=name)
            self.assertAlmostEqual(max(p[1] for p in pts), cz, msg=name)
            for x, z in pts:                               # every corner stays on the far side of the relief line
                self.assertLessEqual((x - cx) + (z - cz), -V["br_rel"] + 1e-9, (name, x, z))


class Numbers(unittest.TestCase):
    def test_bands(self):
        seen = set()
        for key, (pn, name, vn, kind, mat) in I.PARTS.items():
            if key in I.PROFILE_PN:
                # D-126: the bought down-light profile takes ELECTRICAL's number (Control's allocation)
                self.assertEqual(pn, "718101", key)
                self.assertTrue(name.startswith("ELECTRICAL"), key)
                continue
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
