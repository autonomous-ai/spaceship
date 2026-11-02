"""The AIR transitions' checks as tests. Run with the drawing generator's OCC venv:

    ~/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python -m unittest test_transitions -v

The clearance test reads FRONT's DR and glass STEPs from the checkout (a few minutes): until FRONT's #313 lands on
main it skips; the build (build.py --dr --glass) runs the same check on the STEPs given."""

import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)

import build  # noqa: E402
import check_flat  # noqa: E402
import clearance  # noqa: E402
import lower  # noqa: E402
import rivets  # noqa: E402
import tr_sheetmetal as S  # noqa: E402
import tr_params  # noqa: E402
from tr_params import P  # noqa: E402

DR = os.path.join(REPO, "v2", "03-Manufacturing", "front", "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step")
GLASS = os.path.join(REPO, "v2", "03-Manufacturing", "front", "360002_P01_FRONT-FIXED-GLASS-UNIT_STEP.step")


class Params(unittest.TestCase):
    def test_every_number_has_a_status_and_source(self):
        for name, _v, _u, status, source in tr_params.PARAMS:
            self.assertIn(status, ("confirmed", "source", "calculation", "assumption"), name)
            self.assertTrue(source.strip(), name)


class Shape(unittest.TestCase):
    def test_the_lower_ducts_walls_widen_at_20_degrees_or_less(self):
        """The Lead's ruling: the slant's walls at most 20 degrees apart, with the riser's top at Z 1386."""
        self.assertLessEqual(lower.divergence_deg(), P.lt_div_max)
        self.assertEqual(P.rs_z1, 1386.0)

    def test_the_lower_duct_never_narrows_below_its_collar(self):
        lp, rp = lower.left_profile()[0], lower.right_profile()
        for z in np.linspace(P.rs_z1, P.sb_z0, 50):
            xl = np.interp(z, [q[1] for q in lp[1:-1]], [q[0] for q in lp[1:-1]]) if z >= lp[1][1] else lp[0][0]
            xr = np.interp(z, [q[1] for q in rp[:-1]], [q[0] for q in rp[:-1]])
            self.assertGreaterEqual(xr - xl, rp[0][0] - lp[0][0] - 1e-6, z)

    def test_the_cheek_keeps_4_mm_to_drs_skin_facet(self):
        ch = lower.parts()[2]
        worst = min(lower.skin_distance(p) for w in ch.walls.values() for p in w.pts)
        self.assertGreaterEqual(worst, P.skin_rule)


class Parts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="airtr-")
        cls.pieces = build.pieces()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_each_part_is_one_valid_solid_of_its_defined_volume(self):
        for key, part, _copies in self.pieces:
            n, ok, vol, _bb = S.solid_checks(part.solid())
            self.assertEqual(n, 1, key)
            self.assertTrue(ok, key)
            self.assertAlmostEqual(vol, part.expected_volume(), delta=1e-6 * part.expected_volume(), msg=key)

    def test_each_dxf_matches_the_flat_developed_from_its_step(self):
        for key, part, _copies in self.pieces:
            step = os.path.join(self.tmp, key + ".step")
            dxf = os.path.join(self.tmp, key + ".dxf")
            S.write_step([(key + " " + part.name, part.solid())], step, part.name)
            S.write_dxf(dxf, S.flat_outline(part.flat_regions()), part.flat_holes(), part.bend_lines(),
                        part.flat_cutouts())
            faults, dev = check_flat.check(step, dxf, tr_params.P.k_factor, verbose=False)
            self.assertEqual(faults, [], key)
            self.assertEqual(len(dev["folds"]), len(part.folds), key)

    def test_the_flat_check_fails_a_wrong_dxf(self):
        """A bend line moved 0.5 mm, an outline edge moved 0.1 mm and a flat developed at K 0.33 each fail."""
        part = lower.wrapper("RIGHT")                  # a fresh part: this test changes its K
        step = os.path.join(self.tmp, "neg.step")
        S.write_step([(part.name, part.solid())], step, part.name)
        loops = S.flat_outline(part.flat_regions())
        bends = part.bend_lines()
        moved = [(b[0], b[1] + np.array([0.5, 0.0]), b[2] + np.array([0.5, 0.0])) + tuple(b[3:]) for b in bends[:1]]
        bad_bend = os.path.join(self.tmp, "neg_bend.dxf")
        S.write_dxf(bad_bend, loops, part.flat_holes(), moved + bends[1:])
        bad_outline = os.path.join(self.tmp, "neg_outline.dxf")
        lp = [list(loops[0])]
        lp[0][0] = (lp[0][0][0] + 0.1, lp[0][0][1])
        S.write_dxf(bad_outline, lp + loops[1:], part.flat_holes(), bends)
        part.k = 0.33
        part._analyse()
        part._develop()
        bad_k = os.path.join(self.tmp, "neg_k.dxf")
        S.write_dxf(bad_k, S.flat_outline(part.flat_regions()), part.flat_holes(), part.bend_lines())
        for path in (bad_bend, bad_outline, bad_k):
            faults, _dev = check_flat.check(step, path, tr_params.P.k_factor, verbose=False)
            self.assertTrue(faults, path)

    def test_every_rivet_hole_has_its_mate(self):
        sts, faults = rivets.stacks(self.pieces, inside_out=build.INSIDE_OUT)
        self.assertEqual(faults, [])
        self.assertTrue(all(st["grip"] in (2.0, 3.0, 4.0, 5.0) for st in sts), sorted({st["grip"] for st in sts}))
        # each stack has its picked rivet; the 5.0 stacks, between two lengths, a washer under the head
        self.assertTrue(all(st["washer"] == (1.0 if st["grip"] == 5.0 else 0.0) for st in sts))

    def test_no_rivet_through_the_shells_back_wall(self):
        """DR's removable panel is 2.36 mm behind it: a rivet's head or tail would stand in that gap."""
        sh = [p for k, p, _c in self.pieces if k == "UT-S"][0]
        self.assertEqual(sh.walls["BACK"].holes, [])
        for w in sh.walls.values():
            for c, _d in w.holes:
                self.assertFalse(float(np.dot(w.n, [0, 1, 0])) > 0.99, w.name)

    def test_no_piece_or_set_rivet_overlaps_another_the_fan_box_or_the_riser(self):
        named = []
        for key, part, copies in self.pieces:
            sh = part.solid()
            for i, c in enumerate(copies):
                named.append(("%s %d" % (key, i + 1), build.moved(sh, c)))
        sts, _f = rivets.stacks(self.pieces, inside_out=build.INSIDE_OUT)
        self.assertEqual(build.overlaps(named + rivets.solids(sts)), [])

    @unittest.skipUnless(os.path.isfile(DR) and os.path.isfile(GLASS), "FRONT's DR and glass STEPs aren't here")
    def test_six_mm_to_every_dr_tube_and_the_glass_and_four_to_its_skin(self):
        paths = []
        for key, part, copies in self.pieces:
            sh = part.solid()
            path = os.path.join(self.tmp, "clear_%s.step" % key)
            S.write_step([("%s %s %d" % (key, part.name, i + 1), build.moved(sh, c)) for i, c in enumerate(copies)],
                         path, part.name)
            paths.append(path)
        sts, _f = rivets.stacks(self.pieces, inside_out=build.INSIDE_OUT)
        rpath = os.path.join(self.tmp, "clear_rivets.step")
        S.write_step(rivets.solids(sts), rpath, "set rivets")
        rows = clearance.distances(DR, GLASS, paths + [rpath], near=30.0)
        worst = min((r for r in rows if r[2] in ("tube", "glass")), key=lambda r: r[3])
        self.assertGreaterEqual(worst[3], clearance.RULE - 1e-6, "%s is %.2f mm from %s" % (worst[0], worst[3], worst[1]))
        skin = min((r for r in rows if r[2] == "skin"), key=lambda r: r[3])
        self.assertGreaterEqual(skin[3], clearance.SKIN_RULE - 1e-6, "%s is %.2f mm from DR's skin" % (skin[0], skin[3]))


if __name__ == "__main__":
    unittest.main()
