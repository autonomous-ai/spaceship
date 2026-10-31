"""Offline checks of the ceiling layout (no Fusion needed).

    python3 v2/01-CAD-Native/ceiling/test_ceiling_offline.py

They read the same parameters and layout as the Fusion build
(ceiling_model.py, with the skeleton P03's parameters from its CSV) and check
the design intent: the stack closes, the frame pitch is 400 or less, the
cassette sits inside its envelope with its gaps, it never touches the frame,
the fill clears every member, clip and catch, everything on the cassette is
symmetric about its centre line (so one part serves both halves), and the
part numbers sit in their bands and avoid the reserved list.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ceiling_model as M  # noqa: E402

P = M.all_params()
VALS = M.evaluate(P)


def ev(e, vals=VALS):
    return M.ev(vals, e)


def to_pod(box, half, vals=VALS):
    """CS-510301 box -> pod box for the cassette at C1 or C2."""
    ox, oy, oz = (ev(e, vals) for e in M.CASSETTE_CS[half])
    return (box[0] + ox, box[1] + ox, box[2] + oy, box[3] + oy, box[4] + oz, box[5] + oz)


def gap(a, b):
    """Smallest axis-aligned gap between two boxes (negative = overlap depth)."""
    d = []
    for i in range(3):
        d.append(max(b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]))
    return max(d)


class Stack(unittest.TestCase):
    def test_values(self):
        self.assertAlmostEqual(VALS["c_w"], 1203.61)
        self.assertEqual(VALS["inner_w"], 2338.0)
        self.assertAlmostEqual(VALS["fr_pitch"], 368.75)
        self.assertEqual(VALS["cs_w"], 1163.0)
        self.assertEqual(VALS["cs_d"], 1408.0)
        self.assertEqual(VALS["gap_h"], 24.0)
        self.assertAlmostEqual(VALS["rib_off"], 1163.0 / 6)
        self.assertAlmostEqual(VALS["fill_hw"], 584.5 - 1.13 - 20 - 5)

    def test_stack_closes(self):
        v = VALS
        self.assertAlmostEqual(v["acp_t"] + v["fr_d"], v["outer_t"])
        self.assertAlmostEqual(v["outer_t"] + v["lin_gap"] + v["cass_t"], v["stack_t"])
        top = ev(M.CASSETTE_CS["C1"][2])
        self.assertAlmostEqual(top + v["lin_gap"], ev(M.ZF0), msg="cassette top 4 mm under the frame")
        self.assertAlmostEqual(top - v["tray_h"], v["pod_h"] - v["stack_t"], msg="felt face at the inside height")
        self.assertAlmostEqual(v["tray_t"] + v["gap_h"] + v["felt_t"] + v["tray_t"], v["tray_h"])

    def test_frame_pitch(self):
        self.assertLessEqual(VALS["fr_pitch"], 400.0)
        for half in ("C1", "C2"):
            ms = M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)])
            self.assertEqual(len(ms), 7)
            ys = sorted((b[2] + b[3]) / 2 for c, b in ms if c not in ("SIDE", "SEAM"))
            for a, b in zip(ys, ys[1:]):
                self.assertLessEqual(b - a, 400.0 + 1e-9)
            for i in range(len(ms)):
                for j in range(i + 1, len(ms)):
                    self.assertGreaterEqual(gap(ms[i][1], ms[j][1]), -1e-9, "%s overlaps %s" % (ms[i][0], ms[j][0]))
            xs = [x for _c, b in ms for x in (b[0], b[1])]
            sign = -1 if half == "C1" else 1
            self.assertAlmostEqual(min(xs) if sign < 0 else max(xs), sign * (1207.0 - 2.26))
            self.assertAlmostEqual(max(xs) if sign < 0 else min(xs), sign * 1.13)


class Cassette(unittest.TestCase):
    def cassette_outer(self):
        return (ev(M.CS_X0), ev(M.CS_X1), ev(M.CS_Y0), ev(M.CS_Y1), -VALS["tray_h"], 0.0)

    def test_inside_envelope(self):
        # skeleton C1-CASS / C2-CASS envelopes: X -1169..0 / 0..1169, Y -645..769, Z 2319..2353
        env = {"C1": (-1169.0, 0.0, -645.0, 769.0, 2319.0, 2353.0), "C2": (0.0, 1169.0, -645.0, 769.0, 2319.0, 2353.0)}
        for half in ("C1", "C2"):
            b = to_pod(self.cassette_outer(), half)
            e = env[half]
            g = VALS["cs_gap"]
            self.assertAlmostEqual(b[0], e[0] + g)
            self.assertAlmostEqual(b[1], e[1] - g)
            self.assertAlmostEqual(b[2], e[2] + g)
            self.assertAlmostEqual(b[3], e[3] - g)
            self.assertAlmostEqual(b[4], e[4])
            self.assertAlmostEqual(b[5], e[5])

    def parts(self):
        """Every cassette body we can describe as a box, in CS-510301."""
        out = M.boxes_mm(VALS, M.clip_boxes() + M.catch_boxes() + M.rib_boxes())
        for key, bay, b, _n in M.fill_strips():
            out.append(("FILL %d" % bay, tuple(ev(e) for e in b)))
        out.append(("TRAY", self.cassette_outer()))
        return out

    def test_floating(self):
        """Nothing of the cassette reaches into a frame member, except the clip and
        catch envelopes, which mount on member faces (zero overlap)."""
        for half in ("C1", "C2"):
            members = M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)])
            for name, b in self.parts():
                pb = to_pod(b, half)
                for mc, mb in members:
                    g = gap(pb, mb)
                    if name.startswith(("CLIP", "CATCH")):
                        self.assertGreaterEqual(g, -1e-9, "%s %s into %s" % (half, name, mc))
                    elif name.startswith("FILL"):
                        self.assertGreaterEqual(g, VALS["fill_c"] - 1e-9, "%s %s too close to %s (%.2f)" % (half, name, mc, g))
                    else:
                        self.assertGreaterEqual(g, VALS["lin_gap"] - 1e-9, "%s %s too close to %s" % (half, name, mc))

    def test_clips_on_members_over_ribs(self):
        for name, b in M.boxes_mm(VALS, M.clip_boxes()):
            xc = (b[0] + b[1]) / 2
            self.assertAlmostEqual(abs(xc), VALS["rib_off"], msg=name)
            k = int(name.split()[1][1])
            self.assertAlmostEqual(b[3], k * VALS["fr_pitch"], msg=name + " on the member's front face")
            self.assertGreaterEqual(b[2], ev(M.CS_Y0))
        self.assertEqual(len(M.clip_boxes()), 6)
        self.assertEqual(len(M.catch_boxes()), 2)

    def test_fill_clear_of_clips_after_notches(self):
        """The fill keeps fill_c from every clip and catch once its notches are cut."""
        hold = M.boxes_mm(VALS, M.clip_boxes() + M.catch_boxes())
        for key, bay, b, notches in M.fill_strips():
            sb = tuple(ev(e) for e in b)
            nbs = [tuple(ev(e) for e in nb) for _n, nb in notches]
            for hn, hb in hold:
                grown = (hb[0] - VALS["fill_c"], hb[1] + VALS["fill_c"], hb[2] - VALS["fill_c"], hb[3] + VALS["fill_c"],
                         hb[4], hb[5])
                if not M.overlap(sb, grown):
                    continue
                self.assertTrue(any(M.overlap(grown, nb) and all(
                    nb[2 * i] <= grown[2 * i] + 1e-9 and nb[2 * i + 1] >= grown[2 * i + 1] - 1e-9 for i in range(2))
                    for nb in nbs), "bay %d: no notch clears %s" % (bay, hn))

    def test_common_part_symmetry(self):
        """Mirror about the cassette centre line maps every feature onto another."""
        def mirror(b):
            return (-b[1], -b[0]) + tuple(b[2:])
        for group in (M.clip_boxes(), M.catch_boxes(), M.rib_boxes()):
            boxes = [b for _n, b in M.boxes_mm(VALS, group)]
            for b in boxes:
                self.assertTrue(any(all(abs(p - q) < 1e-9 for p, q in zip(mirror(b), c)) for c in boxes))
        for key, bay, b, _n in M.fill_strips():
            sb = tuple(ev(e) for e in b)
            self.assertAlmostEqual(sb[0], -sb[1])
        for x, _y in M.light_points():
            self.assertEqual(ev(x), 0.0)
        self.assertEqual(ev(M.sprinkler_point()[0]), 0.0)

    def test_fill_strip_kinds(self):
        """Bays 0 and 1 give the same strip (one part, 2 off); bays 2 and 3 differ."""
        strips = M.fill_strips()
        sizes = {}
        for key, bay, b, _n in strips:
            sb = tuple(ev(e) for e in b)
            sizes.setdefault(key, set()).add(round(sb[3] - sb[2], 6))
        self.assertEqual(sizes["fill_a"], {338.75})
        self.assertEqual(len(sizes["fill_b"]), 1)
        self.assertEqual(len(sizes["fill_c"]), 1)

    def test_lights_clear(self):
        ribs = M.boxes_mm(VALS, M.rib_boxes())
        r = VALS["ring_od"] / 2
        for x, y in M.light_points():
            cx, cy = ev(x), ev(y)
            for rn, rb in ribs:
                self.assertGreater(min(abs(cx - rb[0]), abs(cx - rb[1])), r, "light plate over " + rn)
            self.assertGreater(cy - r, ev(M.CS_Y0) + VALS["lip_w"])
            self.assertLess(cy + r, ev(M.CS_Y1) - VALS["lip_w"])


class Numbers(unittest.TestCase):
    def test_bands(self):
        seen = set()
        for key, (pn, name, vn, kind, mat) in M.PARTS.items():
            self.assertEqual(len(pn), 6, key)
            self.assertNotIn(pn, M.RESERVED, key)
            self.assertNotIn(pn, seen, key)
            seen.add(pn)
            fam, nnnn = pn[:2], int(pn[2:])
            self.assertIn(fam, ("41", "51"), key)
            if kind == "HS":
                self.assertLessEqual(nnnn, 999, key)
            elif kind == "MP":
                self.assertTrue(1000 <= nnnn <= 7999, key)
            else:
                self.assertTrue(8000 <= nnnn <= 8999, key)
            if fam == "51":
                self.assertTrue(pn.startswith(("5103", "513", "518")), key)
            self.assertTrue(name.split(" - ")[0] in ("CEILING", "LINING"), key)
            self.assertTrue(vn.strip(), key)


class Weight(unittest.TestCase):
    def test_parts_under_20_kg(self):
        v = VALS
        rho = {k: m[1] for k, m in M.MATERIALS.items()}
        # outer panel: 7 tubes + skin
        tube = (2 * (v["tube_w"] + v["fr_d"]) - 4 * v["tube_t"]) * v["tube_t"] * 1e-6 * rho["al"]   # kg/m
        length = 2 * v["wall_depth"] + 5 * (v["c_w"] - 2 * v["tube_w"])
        frame = tube * length * 1e-3
        skin = v["c_w"] * v["wall_depth"] * 1e-6 * 3.5
        self.assertLess(frame + skin, 20.0)
        # cassette: tray + felt + fill + ribs, plus the layout study's clip allowance
        area = v["cs_w"] * v["cs_d"] * 1e-6
        tray = (area + 2 * (v["cs_w"] + v["cs_d"]) * (v["tray_h"] + v["lip_w"]) * 1e-6) * v["tray_t"] * 1e-3 * rho["steel"]
        felt = area * 1.8
        fill = 2 * v["fill_hw"] * v["cs_d"] * 1e-6 * v["fill_t"] * 1e-3 * 32
        rib = 2 * (v["rib_crown"] + 2 * v["gap_h"] + 2 * v["rib_fl"]) * v["cs_d"] * 1e-6 * v["tray_t"] * 1e-3 * rho["steel"]
        cass = tray + felt + fill + rib + area * 0.6
        self.assertLess(cass, 20.0)
        self.assertGreater(cass, 10.0)


class FlatPattern(unittest.TestCase):
    def test_blank(self):
        f = M.tray_flat(VALS)
        self.assertGreater(f["blank_w"], VALS["cs_w"])
        self.assertLess(f["blank_w"], VALS["cs_w"] + 2 * (VALS["tray_h"] + VALS["lip_w"]))
        self.assertAlmostEqual(f["bend_allowance"], math.pi / 2 * (0.5 + 0.44 * 0.5))


class EditFollows(unittest.TestCase):
    def test_pod_width_change(self):
        """Change a skeleton parameter: the layout follows (cassette, frame, fill)."""
        v2 = M.evaluate(P, {"pod_w": "2600 mm"})
        self.assertAlmostEqual(v2["c_w"], 1257.0 - 3.39)
        self.assertAlmostEqual(v2["cs_w"], (2600 - 162) / 2 - 6)
        self.assertAlmostEqual(v2["fill_hw"], (2600 - 162) / 4 - 1.13 - 25)
        v3 = M.evaluate(P, {"wall_depth": "1520 mm"})
        self.assertAlmostEqual(v3["fr_pitch"], (1520 - 20) / 4)
        self.assertAlmostEqual(v3["cs_d"], 1520 - 81 - 6)


if __name__ == "__main__":
    unittest.main(verbosity=1)
