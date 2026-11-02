"""Offline checks of the ceiling layout (no Fusion needed).

    python3 v2/01-CAD-Native/ceiling/test_ceiling_offline.py

They read the same parameters and layout as the Fusion build
(ceiling_model.py, with the skeleton's parameters from its CSV, P04 as
updated by PR #58) and check the design intent: the stack closes, the frames
are half_fw wide with the 5.5 mm closing gap, the joint holes sit where the
joints register puts them (2.9), the frame pitch is 400 or less, the
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


def poly_area(p):
    return 0.5 * abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))))


def clip_area(subject, clip):
    """Area of the overlap of two convex polygons (Sutherland-Hodgman)."""
    def ccw(p):
        a = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))
        return p if a > 0 else p[::-1]
    out, clip = ccw(subject), ccw(clip)
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]

        def inside(q):
            return (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= -1e-9

        def cross(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            den = (x2 - x1) * dy - (y2 - y1) * dx
            t = ((a[0] - x1) * dy - (a[1] - y1) * dx) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        src, out = out, []
        for k in range(len(src)):
            p, q = src[k], src[(k + 1) % len(src)]
            if inside(q):
                if not inside(p):
                    out.append(cross(p, q))
                out.append(q)
            elif inside(p):
                out.append(cross(p, q))
        if not out:
            return 0.0
    return poly_area(out)


def gap(a, b):
    """Smallest axis-aligned gap between two boxes (negative = overlap depth)."""
    d = []
    for i in range(3):
        d.append(max(b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]))
    return max(d)


class Stack(unittest.TestCase):
    def test_values(self):
        """The ceiling's sizes from the skeleton's own numbers (any skeleton revision)."""
        v = VALS
        self.assertAlmostEqual(v["half_pw"], (v["pod_w"] - 2 * v["outer_t"] - 3 * v["seam_gap"]) / 2)
        self.assertAlmostEqual(v["half_fw"], (v["pod_w"] - 2 * v["outer_t"] - 2 * v["seam_gap"] - v["close_gap"]) / 2)
        self.assertAlmostEqual(round(v["half_fw"], 2), 1198.99)
        self.assertAlmostEqual(round(v["half_pw"], 2), 1200.61)
        self.assertAlmostEqual(v["inner_w"], v["pod_w"] - 2 * v["stack_t"])
        self.assertAlmostEqual(v["fr_pitch"], (v["wall_depth"] - v["tube_w"]) / 4)
        self.assertAlmostEqual(v["cs_w"], v["inner_w"] / 2 - 2 * v["cs_gap"])
        self.assertAlmostEqual(v["cs_d"], v["wall_depth"] - v["stack_t"] - v["cs_front"] - 2 * v["cs_gap"])
        self.assertAlmostEqual(v["gap_h"], 24.0)
        self.assertAlmostEqual(v["rib_off"], v["cs_w"] / 6)
        self.assertAlmostEqual(v["fill_hw"], v["inner_w"] / 4 - v["close_gap"] / 2 - v["tube_w"] - v["fill_c"])
        self.assertEqual(v["cs_front"], 360.0)
        self.assertEqual(v["seam_gap"], 2.26)

    def test_stack_closes(self):
        v = VALS
        self.assertAlmostEqual(v["skin_t"] + v["bond_t"] + v["frame_t"], v["outer_t"])
        self.assertGreaterEqual(v["bond_t"], 0.0)
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
            # the members' outlines touch at the mitres and the cross members' ends but never overlap
            # (D-117: the corners are mitred, so their boxes overlap at the corners; their outlines don't)
            shapes = [(c, [(ev(x), ev(y)) for x, y in pts]) for c, _k, _n, _a, pts, _z0, _z1 in M.member_shapes(half)]
            for i in range(len(shapes)):
                for j in range(i + 1, len(shapes)):
                    area = clip_area(shapes[i][1], shapes[j][1])
                    self.assertLess(area, 1e-6, "%s overlaps %s by %.3f mm2" % (shapes[i][0], shapes[j][0], area))
            xs = [x for _c, b in ms for x in (b[0], b[1])]
            sign = -1 if half == "C1" else 1
            outer = VALS["pod_w"] / 2 - VALS["outer_t"] - VALS["seam_gap"]
            self.assertAlmostEqual(min(xs) if sign < 0 else max(xs), sign * outer)
            self.assertAlmostEqual(max(xs) if sign < 0 else min(xs), sign * VALS["close_gap"] / 2)
            self.assertAlmostEqual(max(xs) - min(xs), VALS["half_fw"])
            back = dict(ms)["BACK"]
            self.assertAlmostEqual(back[1] - back[0], VALS["half_fw"] - 2 * VALS["cb_bs"],
                                   msg="40 x 40 back member over the full width, less its cut-backs for the mitre plates")
            self.assertAlmostEqual(back[3] - back[2], 40.0)

    def test_skins_overhang_at_the_closing_seam(self):
        """Skins 1200.61 over frames 1198.99: flush at the side, 1.62 over the frame at X 0."""
        v = VALS
        for half in ("C1", "C2"):
            sx = ev(M.SKIN_PLACES[half][0])
            b = [ev(e) for e in M.skin_box()]
            x0, x1 = b[0] + sx, b[1] + sx
            fx = [x for _c, mb in M.boxes_mm(v, [(c, bb) for c, _n, _a, bb in M.frame_members(half)]) for x in mb[:2]]
            if half == "C1":
                self.assertAlmostEqual(x0, min(fx))
                self.assertAlmostEqual(x1 - max(fx), v["half_pw"] - v["half_fw"])
            else:
                self.assertAlmostEqual(x1, max(fx))
                self.assertAlmostEqual(x0 - min(fx), -(v["half_pw"] - v["half_fw"]))


class Joints(unittest.TestCase):
    """J-CEIL-01 and J-CEIL-02 holes against the joints register (2.9, 3.5, 3.6) and the PM
    ruling of 2026-10-31 (side edges from Y -645 along the ceiling, back edges on the frame)."""

    def test_rivnut_holes_are_d163s(self):
        """D-163 pins every 838003 hole in the members at Ø10.00, CAL2-610-4.2's knurled round hole (it was CAH2's
        Ø9.53): 20 a ceiling, 8 in C1 (the back member's 4, the soffit's 2 hangers and 2 locks) and 12 in C2 (with the
        seam's 4 pin rivnuts), every rivnut row on the one named value (Reviewer 17's plant on #348: the hole set back
        to Ø9.53 passed every check)."""
        self.assertEqual(VALS["hole_rvn"], 10.0)
        row = [p for p in P if p[0] == "hole_rvn"][0]
        self.assertIn("D-163", row[4])
        self.assertIn("CAL2-610-4.2", row[4])
        counts = {}
        for half in ("C1", "C2"):
            for name, _m, _f, _xyz, d, n, _p, _a in M.joint_holes(half):
                if "RIVNUT" in name or "HANGER" in name or "LOCK" in name:
                    self.assertEqual(d, "hole_rvn", (half, name))
                if d == "hole_rvn":
                    counts[half] = counts.get(half, 0) + int(round(ev(n)))
        self.assertEqual(counts, {"C1": 8, "C2": 12})

    def rows(self, half, name):
        return [xyz for n, _d, xyz in M.hole_positions(VALS, half) if n == name]

    def test_register_positions(self):
        for half in ("C1", "C2"):
            ys = [round(p[1] + 645, 2) for p in self.rows(half, "SIDE BOLT CLEARANCE")]
            self.assertEqual(ys, [220.0, 571.67, 923.33, 1275.0])
            pins = [round(p[1] + 645, 2) for p in self.rows(half, "SEAM PIN CLEARANCE" if half == "C1" else "SEAM PIN RIVNUT")]
            self.assertEqual(pins, [220.0, 571.67, 923.33, 1275.0])
            xs = sorted(round(abs(p[0]) - VALS["close_gap"] / 2, 2) for p in self.rows(half, "BACK RIVNUT"))
            self.assertEqual(xs, [220.0, 473.0, 725.99, 978.99])
            for p in self.rows(half, "BACK RIVNUT"):
                self.assertAlmostEqual(p[1], 824.0)
            for p in self.rows(half, "SIDE BOLT ACCESS"):
                self.assertAlmostEqual(p[2], 2374.0)

    def test_counts(self):
        names = {}
        for half in ("C1", "C2"):
            for n, _d, _p in M.hole_positions(VALS, half):
                names[(half, n)] = names.get((half, n), 0) + 1
        self.assertEqual(names[("C1", "SIDE BOLT CLEARANCE")], 4)
        self.assertEqual(names[("C2", "SIDE BOLT ACCESS")], 4)
        self.assertEqual(names[("C1", "BACK RIVNUT")], 4)
        self.assertEqual(names[("C2", "SEAM PIN RIVNUT")], 4)
        self.assertEqual(names[("C2", "SEAM PIN ACCESS")], 4)
        self.assertNotIn(("C2", "SEAM PIN CLEARANCE"), names)
        self.assertEqual(names[("C1", "BACK SPIGOT ROUND")], 1)
        self.assertEqual(names[("C1", "BACK SPIGOT SLOT")], 1)

    def test_holes_inside_their_faces_and_clear_of_stiles(self):
        """Every hole lies on its member's face with its edge inside the face; every bolt is
        30 mm or more from any member that meets the one it is in (R-J14)."""
        v = VALS
        for half in ("C1", "C2"):
            mem = dict(M.boxes_mm(v, [(c, b) for c, _n, _a, b in M.frame_members(half)]))
            for name, member, face, _xyz, _dia, _n, _p, axis in M.joint_holes(half):
                for n, d, (x, y, z) in M.hole_positions(v, half):
                    if n != name:
                        continue
                    b = mem[member]
                    r = d / 2
                    if face == "bottom":
                        self.assertAlmostEqual(z, b[4])
                        self.assertTrue(b[0] + r + 9 <= x <= b[1] - r - 9 or member == "BACK", (half, n, x))
                        edge = 5.0 if n.startswith("SOFFIT") else 9.0   # soffit hangers and locks on 20 mm faces (HOLD-04)
                        self.assertGreaterEqual(y - r - b[2], edge, (half, n, "rivnut edge distance"))
                        self.assertGreaterEqual(b[3] - (y + r), edge, (half, n))
                    elif member == "FRONT":                   # DT's bolts (J-FRONT-03): the walls face Y
                        self.assertTrue(abs(y - b[2]) < 1e-6 or abs(y - b[3]) < 1e-6, (half, n, y, b))
                        self.assertGreaterEqual(z - r, b[4] + v["tube_t"], (half, n))
                        self.assertLessEqual(z + r, b[5] - v["tube_t"], (half, n))
                        self.assertTrue(b[0] < x < b[1], (half, n, x))
                        for other in ("SIDE", "SEAM"):           # the members that meet the front tube (R-J14)
                            ob = mem[other]
                            g = max(ob[0] - x, x - ob[1])
                            self.assertGreaterEqual(g, 30.0, "%s %s at X %.2f: %.1f from %s" % (half, n, x, g, other))
                    else:
                        self.assertTrue(abs(x - b[0]) < 1e-6 or abs(x - b[1]) < 1e-6, (half, n, x, b))
                        self.assertGreaterEqual(z - r, b[4] + v["tube_t"], (half, n))
                        self.assertLessEqual(z + r, b[5] - v["tube_t"], (half, n))
                        self.assertTrue(b[2] < y < b[3], (half, n, y))
                        for other, ob in mem.items():
                            if other in ("SIDE", "SEAM"):
                                continue
                            g = max(ob[2] - y, y - ob[3])
                            self.assertGreaterEqual(g, 30.0, "%s %s at Y %.2f: %.1f from %s" % (half, n, y, g, other))

    def test_roof_slot_clear_of_c2_bolts(self):
        """D-60 (joints register 3.5): C2's side bolts and access holes stay clear of the roof slot."""
        v = VALS
        slot_x1 = v["slot_x0"] + v["slot_w"]
        for n, d, (x, y, z) in M.hole_positions(v, "C2"):
            if n == "SIDE BOLT ACCESS":
                self.assertGreaterEqual(x - slot_x1, 20.0, "access hole %.1f from the slot" % (x - slot_x1))
        sb = [ev(e) for e in M.roof_slot_box()]
        ox = ev(M.SKIN_PLACES["C2"][0])
        self.assertGreater(sb[0] + ox, 0.0)
        self.assertAlmostEqual(sb[1] + ox, slot_x1)
        self.assertAlmostEqual(sb[2] + ev(M.YW), v["slot_y0"])
        self.assertGreaterEqual(v["slot_y0"] - (ev(M.YW) + v["tube_w"]), 5.0 - 1e-9, "slot clear of the front member")


class DtBolts(unittest.TestCase):
    """J-FRONT-03 (joints register 3.13): DT's 4 bolts through the ceiling's front tubes (the amended D-169 gives C1
    no pin slot: DT keeps its spigots)."""

    def rows(self, half, name):
        return [xyz for n, _d, xyz in M.hole_positions(VALS, half) if n == name]

    def test_register_positions(self):
        c1 = [round(p[0], 2) for p in self.rows("C1", "DT BOLT CLEARANCE")]
        c2 = [round(p[0], 2) for p in self.rows("C2", "DT BOLT CLEARANCE")]
        self.assertEqual(c1, [-981.74, -578.16, -174.58])
        # the rule puts the 4th at 220 + 3 x 403.58 = 1430.74 from C1's frame end (X -1201.74): +229.00 (the register
        # prints +228.99, the same point rounded down)
        self.assertEqual(c2, [229.0])
        for half in ("C1", "C2"):
            self.assertEqual([n for n, _d, _p in M.hole_positions(VALS, half) if "SLOT" in n and "DT" in n], [])
        for half in ("C1", "C2"):
            for p in self.rows(half, "DT BOLT CLEARANCE"):
                self.assertAlmostEqual(p[1], -645.0)              # the front wall, Ø7.0
                self.assertAlmostEqual(p[2], 2374.0)              # DT's bolt line
            for p in self.rows(half, "DT BOLT ACCESS"):
                self.assertAlmostEqual(p[1], -625.0)              # the back wall, from the bay, Ø19
        d = {n: dd for n, dd, _p in M.hole_positions(VALS, "C1")}
        self.assertAlmostEqual(d["DT BOLT CLEARANCE"], 7.0)
        self.assertAlmostEqual(d["DT BOLT ACCESS"], 19.0)

    def test_bolt_clear_of_the_soffit_hanger(self):
        """DT's middle C1 bolt (X -578.16) and the soffit's front hanger rivnut (X -583, on the tube's underside) share
        C1's front tube. Inside it, the bolt's ISO 7093 6.4 x 18 x 1.6 washer and ISO 4762 M6 head (Ø10 x 6) sit on the
        front wall; the rivnut's body (Sherex CAL2-610-4.2: Ø9.91 max, 9.65 max installed length) stands up from the
        bottom wall, its bulge about Ø14 for its first 5. Each pair of boxes must stay 2 mm or more apart."""
        v = VALS
        t = v["tube_t"]
        yf, zb = ev(M.YW) + t, ev(M.ZF0) + t                       # the front wall's and the bottom wall's inner faces
        def boxes_apart(a, b):
            gaps = [max(b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]) for i in range(3)]
            return max(gaps)
        for hx, _hy, _hz in [p for n, _d, p in M.hole_positions(v, "C1") if n == "SOFFIT HANGER FRONT"]:
            hy = ev(M.YW) + v["tube_w"] / 2
            body = (hx - 4.955, hx + 4.955, hy - 4.955, hy + 4.955, zb, zb + 9.65)
            bulge = (hx - 7.0, hx + 7.0, hy - 7.0, hy + 7.0, zb, zb + 5.0)
            for bx, _by, bz in self.rows("C1", "DT BOLT CLEARANCE"):
                washer = (bx - 9.0, bx + 9.0, yf, yf + 1.6, bz - 9.0, bz + 9.0)
                head = (bx - 5.0, bx + 5.0, yf + 1.6, yf + 7.6, bz - 5.0, bz + 5.0)
                for a in (washer, head):
                    for b in (body, bulge):
                        self.assertGreaterEqual(boxes_apart(a, b), 2.0, (bx, hx, a, b))


class Cassette(unittest.TestCase):
    def cassette_outer(self):
        return (ev(M.CS_X0), ev(M.CS_X1), ev(M.CS_Y0), ev(M.CS_Y1), -VALS["tray_h"], 0.0)

    def test_inside_envelope(self):
        """Inside the skeleton's ceiling cassette envelope (C1-CASS / C2-CASS) behind the
        D-60 soffit, with the edge gap all round; top 4 mm under the ceiling frame."""
        v = VALS
        xi = v["pod_w"] / 2 - v["stack_t"]
        y0 = v["pod_d"] / 2 - v["wall_depth"] + v["cs_front"]
        y1 = v["pod_d"] / 2 - v["stack_t"]
        z0 = v["pod_h"] - v["stack_t"]
        env = {"C1": (-xi, 0.0, y0, y1, z0, z0 + v["cass_t"]), "C2": (0.0, xi, y0, y1, z0, z0 + v["cass_t"])}
        for half in ("C1", "C2"):
            b = to_pod(self.cassette_outer(), half)
            e = env[half]
            g = v["cs_gap"]
            for got, want in zip(b, (e[0] + g, e[1] - g, e[2] + g, e[3] - g, e[4], e[5])):
                self.assertAlmostEqual(got, want)

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
            self.assertAlmostEqual(b[2], ev(M.member_back_cs(k)), msg=name + " on the member's back face")
            self.assertGreaterEqual(b[2], ev(M.CS_Y0))
            self.assertLessEqual(b[3], ev(M.CS_Y1))
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
        xs = sorted(ev(x) for x, _y in M.sprinkler_points())
        self.assertAlmostEqual(xs[0], -xs[1])

    def test_fill_strip_kinds(self):
        """With the 360 mm soffit the strips lie in bays 1, 2 and 3: three kinds, each one size."""
        strips = M.fill_strips()
        self.assertEqual([b for _k, b, _x, _n in strips], [1, 2, 3])
        sizes = {}
        for key, bay, b, _n in strips:
            sb = tuple(ev(e) for e in b)
            sizes.setdefault(key, set()).add(round(sb[3] - sb[2], 6))
            self.assertGreaterEqual(sb[3] - sb[2], VALS["fill_min"])
        self.assertEqual(len(sizes), 3)
        for k in sizes:
            self.assertEqual(len(sizes[k]), 1)

    def test_x1_over_the_soffit(self):
        """D-87 hangers: X1 overlaps the soffit's back edge by x1_ov, and its back face (the
        clips' face) stays over the cassette."""
        v = VALS
        x1 = dict(M.boxes_mm(v, [(c, b) for c, _n, _a, b in M.frame_members("C1")]))["X1"]
        soffit_back = ev(M.YW) + v["cs_front"]
        self.assertAlmostEqual(soffit_back - x1[2], v["x1_ov"])
        self.assertGreater(x1[3], soffit_back + v["cs_gap"] - 1.0 - 1e-9, "clip face over the cassette")
        self.assertLessEqual(x1[2] - (ev(M.YW) + v["tube_w"]), 400.0)


class CableHoles(unittest.TestCase):
    def test_shared_height(self):
        """F-188 (PM ruling 2026-11-01): ELECTRICAL's grommets and draw wire take this one height;
        both cassettes' holes sit on it, at today's values Z 2337.5 on X -583 and 583."""
        self.assertAlmostEqual(M.ev(VALS, M.CABLE_HOLE_Z), 2337.5, places=3)
        self.assertAlmostEqual(M.ev(VALS, M.CABLE_HOLE_X["C1"]), -583.0, places=3)
        self.assertAlmostEqual(M.ev(VALS, M.CABLE_HOLE_X["C2"]), 583.0, places=3)
        self.assertEqual(M.CASSETTE_CS["C1"][2], M.CASSETTE_CS["C2"][2])

    def test_hole_in_the_return_gap(self):
        """The hole's centre is mid gap between the tray base and the felt, so the Ø19.1 hole
        stays inside the return (the gap is tray_h - felt_t - 2 tray_t)."""
        zc = M.ev(VALS, M.CABLE_HOLE_ZC)
        self.assertAlmostEqual(zc, -(VALS["tray_t"] + VALS["gap_h"] / 2), places=6)
        self.assertGreater(VALS["gap_h"], VALS["cable_hole"])


class Sprinkler(unittest.TestCase):
    def test_zones_clear(self):
        r = VALS["sprk_d"] / 2
        ribs = M.boxes_mm(VALS, M.rib_boxes())
        hold = M.boxes_mm(VALS, M.clip_boxes() + M.catch_boxes())
        for x, y in M.sprinkler_points():
            cx, cy = ev(x), ev(y)
            zone = (cx - r, cx + r, cy - r, cy + r, -1e9, 1e9)
            for n, b in ribs + hold:
                self.assertFalse(M.overlap(zone, b), "sprinkler zone over " + n)
            for half in ("C1", "C2"):
                pz = to_pod(zone, half)
                for mc, mb in M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)]):
                    self.assertFalse(M.overlap((pz[0], pz[1], pz[2], pz[3], mb[4], mb[5]), mb), "zone under " + mc)
                # the PM's provision (2026-11-01): clear through every layer, so a head goes in later without
                # cutting a member: ELECTRICAL's draw wire runs along the cassette's centre line from the front
                # return's cable hole to the back one (10 mm allowed for the wire and its clips) ...
                wire = ev(M.CABLE_HOLE_X[half])
                self.assertGreaterEqual(min(abs(pz[0] - wire), abs(pz[1] - wire)) if not pz[0] <= wire <= pz[1] else -1,
                                        10.0, "zone over the draw wire (%s)" % half)
                # ... and the roof slot and the AIR sleeve in it (C2) stay 25 or more away
                slot = (VALS["slot_x0"], VALS["slot_x0"] + VALS["slot_w"], VALS["slot_y0"], VALS["slot_y0"] + VALS["slot_d"])
                gap_x = max(slot[0] - pz[1], pz[0] - slot[1])
                gap_y = max(slot[2] - pz[3], pz[2] - slot[3])
                self.assertGreaterEqual(max(gap_x, gap_y), 25.0, "zone near the roof slot (%s)" % half)


class Frames(unittest.TestCase):
    """D-117, D-120 and D-131 (J-FRAME-01): mitred outer corners with a 2.0 mitre plate welded into each, every member
    its own part in galvanized steel at its gauge, no cleats."""

    def shapes(self, half):
        return {c: (k, [(ev(x), ev(y)) for x, y in pts]) for c, k, _n, _a, pts, _z0, _z1 in M.member_shapes(half)}

    def test_mitre_angles(self):
        import math
        for half in ("C1", "C2"):
            sh = self.shapes(half)
            # front corners 45 deg: the cut runs 20 across the 20 tube for 20 along it
            p = sh["SIDE"][1]
            self.assertAlmostEqual(abs(p[3][0] - p[0][0]), abs(p[3][1] - p[0][1]))
            # back corners: the 40 x 40 back member cut 26.57 deg off square, the side 63.43
            dx, dy = abs(p[2][0] - p[1][0]), abs(p[2][1] - p[1][1])
            self.assertAlmostEqual(math.degrees(math.atan2(dx, dy)), 26.57, places=2)
            self.assertAlmostEqual(90.0 - math.degrees(math.atan2(dx, dy)), 63.43, places=2)
            # the outer edges run to the frame's outer corners
            xs = [x for _k, pts in sh.values() for x, _y in pts]
            ys = [y for _k, pts in sh.values() for _x, y in pts]
            self.assertAlmostEqual(max(xs) - min(xs), VALS["half_fw"])
            self.assertAlmostEqual(max(ys) - min(ys), VALS["wall_depth"])
            # the members and the four mitre plates tile the frame's outline (no gap or overlap): their areas add up,
            # each plate mp_t thick along its mitre (J-FRAME-01)
            ring = sum(poly_area(pts) for c, (_k, pts) in sh.items() if c in ("SIDE", "SEAM", "FRONT", "BACK"))
            inner = (VALS["half_fw"] - 2 * VALS["tube_w"]) * (VALS["wall_depth"] - VALS["tube_w"] - VALS["back_w"])
            mitres = 2 * math.hypot(VALS["tube_w"], VALS["tube_w"]) + 2 * math.hypot(VALS["tube_w"], VALS["back_w"])
            self.assertAlmostEqual(ring + VALS["mp_t"] * mitres, VALS["half_fw"] * VALS["wall_depth"] - inner, places=6)

    def test_every_member_its_own_part(self):
        for half in ("C1", "C2"):
            keys = [k for _c, (k, _p) in self.shapes(half).items()]
            for k in keys:
                pn, name, _vn, kind, mat = M.PARTS[k]
                self.assertEqual(kind, "MP", k)
                self.assertEqual(mat, "steel_fr", k)
                self.assertEqual(M.member_wall(k), "tube_t_in" if k == "m_cross" else "tube_t", k)
                self.assertTrue(pn.startswith("412"), k)
            self.assertEqual(keys.count("m_cross"), 2, "X2 and X3 are one common part (412001)")

    def test_cut_list_matches_the_members(self):
        """The committed tube cut list against the members' own outlines (member_shapes, which the build extrudes):
        each row's length at the outer face, both end cuts, section and wall, part numbers and count, and its holes
        (Reviewer 17's plant on #348: a row 10 mm long with a wrong end angle passed every check)."""
        import csv
        import re
        import ceiling_exports as E
        path = os.path.join(E.OUT, "410000_%s_CEILING-TUBE-CUT-LIST_BOM.csv" % E.REV)
        with open(path, newline="", encoding="utf-8") as f:
            rows = {(r["half"], r["member"]): r for r in csv.DictReader(f)}
        self.assertEqual(len(rows), 14)
        extra = {"BACK": ["back spigot slot 8.5 x 14 x 1"],
                 "SEAM": ["1 x 45 lead-in on the closing face's lower edge, full length"]}
        for half, fkey in (("C1", "frame_c1"), ("C2", "frame_c2")):
            holes = {}
            for name, member, _f, _xyz, _d, n, _p, _a in M.joint_holes(half):
                holes.setdefault(member, []).append("%s x %d" % (name.lower(), int(round(ev(n)))))
            for code, key, _name, axis, pts, _z0, _z1 in M.member_shapes(half):
                r = rows[(half, code)]
                q = [(ev(x), ev(y)) for x, y in pts]
                a = 0 if axis == "x" else 1          # along the member
                c = 1 - a                            # across it
                self.assertAlmostEqual(float(r["length_mm"]), max(p[a] for p in q) - min(p[a] for p in q), delta=0.006,
                                       msg=(half, code))

                def cut(i, j):                       # an end edge's angle off square, in degrees
                    return math.degrees(math.atan2(abs(q[j][a] - q[i][a]), abs(q[j][c] - q[i][c])))
                got = (cut(3, 0), cut(1, 2))         # the outline's first end (front, or the side's end) and its other
                text = r["ends"].split(";")[0]
                nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?) deg", text)]
                want = (0.0, 0.0) if text == "square cut" else (nums[0], nums[0]) if text.startswith("both ends") else tuple(nums)
                self.assertEqual(len(want), 2, text)
                for g, w in zip(got, want):
                    self.assertAlmostEqual(g, w, delta=0.006, msg=(half, code, text))
                m = re.search(r"(\d+) x 40 x ([\d.]+)", r["section"])
                self.assertAlmostEqual(float(m.group(1)), max(p[c] for p in q) - min(p[c] for p in q), msg=(half, code))
                self.assertAlmostEqual(float(m.group(2)), ev(M.member_wall(key)), msg=(half, code))
                self.assertEqual((r["frame"], r["member_part"], r["qty"]), (M.PARTS[fkey][0], M.PARTS[key][0], "1"))
                self.assertEqual(sorted(r["holes"].split("; ")), sorted(holes.get(code, []) + extra.get(code, [])) or ["none"],
                                 (half, code))

    def test_cut_list_is_current(self):
        """The committed cut list is what the exports write from today's model."""
        import csv
        import ceiling_exports as E
        path = os.path.join(E.OUT, "410000_%s_CEILING-TUBE-CUT-LIST_BOM.csv" % E.REV)
        with open(path, newline="", encoding="utf-8") as f:
            have = list(csv.DictReader(f))
        want = [{k: str(v) for k, v in r.items()} for r in E.cut_list(VALS)]
        self.assertEqual(have, want)

    def test_parts_list_walls_follow_the_model(self):
        """The parts list's size text and the tube cut list's section carry each member's own wall (D-131: 1.0, the
        plain cross members 0.8); the plain cross member's text once kept the aluminium frame's 1.2."""
        import ceiling_exports as E
        for half in ("C1", "C2"):
            for code, key, _name, sec, _L, _ends, _x in E.member_rows(VALS, half):
                wall = "x %.1f" % ev(M.member_wall(key))
                self.assertIn(wall, sec, (half, code))
                self.assertIn(wall + " tube", E.SIZE_TOL[key](VALS)[0], (half, code, key))

    def test_welded_with_plates_no_cleats(self):
        """D-131 cancels the cleats: no slots; a 2.0 plate in every corner, each member's mitred end cut back half the
        plate's thickness square to the mitre (J-FRAME-01: 1.41, 2.24 and 1.12 along the members)."""
        import math
        self.assertFalse(hasattr(M, "cleat_slots"))
        self.assertAlmostEqual(VALS["cb45"], 1.414, places=3)
        self.assertAlmostEqual(VALS["cb_sb"], 2.236, places=3)
        self.assertAlmostEqual(VALS["cb_bs"], 1.118, places=3)
        for half in ("C1", "C2"):
            sh = self.shapes(half)
            corners = M.plate_corners(half)
            self.assertEqual(sorted(k for _n, k, _o, _i in corners), ["mp45", "mp45", "mp_sb", "mp_sb"])
            for name, key, o, i in corners:
                (ox, oy), (ix, iy) = (ev(o[0]), ev(o[1])), (ev(i[0]), ev(i[1]))
                L = math.hypot(ix - ox, iy - oy)
                self.assertAlmostEqual(L, math.hypot(VALS["tube_w"], VALS["tube_w" if key == "mp45" else "back_w"]))
                # every member corner point near this corner lies mp_t / 2 off the plate's mid-plane line
                near = [(x, y) for _k, pts in sh.values() for x, y in pts
                        if min(math.hypot(x - ox, y - oy), math.hypot(x - ix, y - iy)) < 3.0]
                self.assertEqual(len(near), 4, (half, name))
                for x, y in near:
                    d = abs((ix - ox) * (y - oy) - (iy - oy) * (x - ox)) / L
                    self.assertAlmostEqual(d, VALS["mp_t"] / 2, places=6, msg="%s %s" % (half, name))

    def test_plates_in_the_corner_gaps(self):
        """Each plate (the Joints Engineer's blank, #294, shortened in #308) lies in the gap the two members' cut-backs
        leave at its corner, overlapping neither member, and every corner of it sits 0.5 or more inside the frame's
        outside (the Lead's steer 2026-11-01: nothing stands proud, so the frame's outline is its packing box); the weld
        fills the steps at its ends."""
        for half in ("C1", "C2"):
            sh = self.shapes(half)
            boxes = {c: b for c, b in M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)])}
            xs = [x for b in boxes.values() for x in b[:2]]
            ys = [y for b in boxes.values() for y in b[2:4]]
            for name, pkey, o, i in M.plate_corners(half):
                pl = M.plate_outline(VALS, half, name)
                self.assertEqual(len(pl), 4, (half, name, pl))
                self.assertAlmostEqual(poly_area(pl), VALS["mp_t"] * ev(M.plate_length(pkey)), places=4)
                for c, (_k, pts) in sh.items():
                    self.assertLess(clip_area(pl, pts), 1e-4, "%s %s overlaps %s" % (half, name, c))
                inside = min(min(x - min(xs), max(xs) - x, y - min(ys), max(ys) - y) for x, y in pl)
                self.assertGreaterEqual(inside, 0.5 - 1e-6, "%s %s: a corner %.3f inside the frame's outside" % (half, name, inside))

    def test_plate_blanks_are_the_registers(self):
        """The plates' start and length along the mitre are the Joints Engineer's (frame_steel_check.PLATE_BLANKS, the
        register's H-40 and H-41), read from its file so a change there fails here."""
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "joints", "frame_steel_check.py")
        spec = importlib.util.spec_from_file_location("frame_steel_check_for_ceiling_test", path)
        J = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(J)
        want = {"831007": J.PLATE_BLANKS["20x40 to 20x40, 45 deg"], "831008": J.PLATE_BLANKS["rail to 40x40, 63.43 / 26.57 deg"]}
        for pkey, hw in M.PLATE_HW.items():
            pn = M.HARDWARE[hw][0]
            a, b, x0, length = want[pn]
            self.assertAlmostEqual(ev(M.plate_start(pkey)), x0, msg=pn)
            self.assertAlmostEqual(ev(M.plate_length(pkey)), length, msg=pn)
            self.assertAlmostEqual(VALS["mp_t"], J.PLATE_T, msg=pn)
            self.assertEqual((a, b), (VALS["tube_w"], VALS["tube_w" if pkey == "mp45" else "back_w"]), pn)

    def test_identical_in_both_halves(self):
        """For Control (D-120: identical parts share one number): C2's side member is C1's turned upside
        down (every feature centred across its 40 face, the mitres vertical), and C2's cross member 1 is
        C1's turned end for end (its one hanger hole centred across its width, at the same distance from
        the seam end)."""
        zmid = ev(M.ZF0) + VALS["frame_t"] / 2
        for half in ("C1", "C2"):
            for name, _d, (x, y, z) in M.hole_positions(VALS, half):
                if name.startswith("SIDE BOLT"):
                    self.assertAlmostEqual(z, zmid, msg=name)
        x1 = {}
        for half in ("C1", "C2"):
            mem = dict(M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)]))
            b = mem["X1"]
            seam_end = b[1] if half == "C1" else b[0]
            holes = [(x, y) for n, _d, (x, y, _z) in M.hole_positions(VALS, half) if n == "SOFFIT HANGER X1"]
            self.assertEqual(len(holes), 1)
            hx, hy = holes[0]
            self.assertAlmostEqual(hy, (b[2] + b[3]) / 2, msg="centred across X1")
            x1[half] = abs(hx - seam_end)
        self.assertAlmostEqual(x1["C1"], x1["C2"])


class TurnedCopies(unittest.TestCase):
    """Control's allocation (2026-11-01): the side member 412101 and cross member 1 412105 are one part each for
    both frames, C2's being C1's turned over (412201 and 412205 cancelled). The build places C2's as C1's part
    turned 180 deg about Y or Z with the pod origin sent to M.turned_origin: every feature of C2's own layout must
    land on C1's moved that way (outline with the plate cut-backs, joint holes), or the copy would be the wrong part."""

    def move(self, key, p):
        x, y, z = p
        tx, ty, tz = (ev(e) for e in M.turned_origin(key))
        return (-x + tx, y + ty, -z + tz) if M.TURNED[key] == "y" else (-x + tx, -y + ty, z + tz)

    def features(self, half, code):
        out = []
        for c, _k, _n, _a, pts, z0, z1 in M.member_shapes(half):
            if c == code:
                out += [("corner", (ev(x), ev(y), ev(z))) for x, y in pts for z in (z0, z1)]
        names = {n for n, m, *_rest in M.joint_holes(half) if m == code}
        out += [("hole %s %.2f" % (n, d), xyz) for n, d, xyz in M.hole_positions(VALS, half) if n in names]
        return out

    def test_c2_is_c1_turned(self):
        for key, code in (("m_side", "SIDE"), ("m_x1", "X1")):
            c1, c2 = self.features("C1", code), self.features("C2", code)
            self.assertEqual(len(c1), len(c2), code)
            self.assertGreater(len([f for f in c1 if f[0] != "corner"]), 0, "%s has features to compare" % code)
            for kind, p in c1:
                q = self.move(key, p)
                hits = [f for f in c2 if f[0].split()[0] == kind.split()[0] and
                        max(abs(a - b) for a, b in zip(f[1], q)) < 1e-6]
                self.assertTrue(hits, "%s: C1's %s at %s turned is %s, not on C2's" % (code, kind, p, q))

    def test_one_number_each(self):
        for key in M.TURNED:
            self.assertEqual([c for h in ("C1", "C2") for c, k, *_r in M.member_shapes(h) if k == key],
                             ["SIDE", "SIDE"] if key == "m_side" else ["X1", "X1"])
        self.assertFalse({"412201", "412205"} & {v[0] for v in M.PARTS.values()})


class SleeveFlangeHoles(unittest.TestCase):
    """C2's skin takes a hole under each of the roof sleeve flange's 4 rivnuts (J-AIR-03, CEILING's layout 2026-11-01):
    each 2 hole diameters from the slot's edge (HOLD-04's rule binds at the skin's free edge too), inside the skin, and
    each set bulge (about 14 across) clear of C2's members: the back pair sits behind cross member 1, not in front."""

    def test_holes(self):
        slot = (ev("slot_x0"), ev("slot_x0 + slot_w"), ev("slot_y0"), ev("slot_y0 + slot_d"))
        members = [tuple(ev(e) for e in b) for _c, _n, _a, b in M.frame_members("C2")]
        x1 = [tuple(ev(e) for e in b) for c, _n, _a, b in M.frame_members("C2") if c == "X1"][0]
        r = ev("slv_bulge") / 2
        holes = [(n, ev(x), ev(y)) for n, x, y in M.sleeve_rivnuts()]
        self.assertEqual(len(holes), 4)
        for n, x, y in holes:
            self.assertFalse(slot[0] < x < slot[1] and slot[2] < y < slot[3], n)
            d = min(abs(x - slot[0]) if slot[2] <= y <= slot[3] else 1e9, abs(y - slot[3]) if slot[0] <= x <= slot[1] else 1e9)
            self.assertGreaterEqual(d, 2 * ev("hole_rvn") - 1e-9, "%s: %.2f from the slot" % (n, d))
            for m in members:
                g = max(m[0] - (x + r), (x - r) - m[1], m[2] - (y + r), (y - r) - m[3])
                self.assertGreaterEqual(g, ev("slv_rn_clr") - 1e-9, "%s's bulge meets a C2 member" % n)
        backs = [y for n, _x, y in holes if "BACK LEFT" in n or "BACK RIGHT" in n]
        self.assertTrue(all(y > x1[3] for y in backs), "the back pair behind X1")
        # in the skin's own system (the Fusion cut and the DXF), each hole lands inside the skin
        for n, x, y in M.skin_c2_holes():
            sx, sy = ev(x), ev(y)
            self.assertTrue(-ev("half_pw") < sx < 0 and 0 < sy < ev("wall_depth"), n)

    def test_clearance_holes_pass_a_set_rivnut_at_full_play(self):
        """D-177: each of C2's four skin holes is a Ø17 clearance hole that passes a set rivnut wherever the sleeve lands
        in its slot (1.0 a side) with the holes placed to their tolerance (0.5): the bulge (about 14) and the body
        (9.91) clear its edge; the flange, which runs slv_rn_e past each rivnut on its open sides, covers the hole with
        10.0 outside it (room for the 8-wide butyl ring placed to +/-0.5, with 1.5 to spare); and the back pair's
        bodies clear cross member 1 by 1.5 or more."""
        play = ev("slv_fit") + ev("slv_pos")
        self.assertAlmostEqual(ev("hole_slv"), 17.0)
        self.assertAlmostEqual(ev("slv_fit"), 1.0)
        self.assertAlmostEqual(play, 1.5)
        r = ev("hole_slv") / 2
        self.assertGreaterEqual(r - play, ev("slv_bulge") / 2 - 1e-9, "the bulge passes the hole")
        self.assertGreater(r - play, ev("slv_rn_body") / 2, "the body passes the hole")
        self.assertGreaterEqual(ev("slv_rn_e") - r - play, 8.0 + 0.5 + 1.5 - 1e-9, "room for the ring outside each hole")
        x1 = [tuple(ev(e) for e in b) for c, _n, _a, b in M.frame_members("C2") if c == "X1"][0]
        backs = [(n, ev(y)) for n, _x, y in M.sleeve_rivnuts() if n.split("RIVNUT ")[1].startswith("BACK")]
        self.assertEqual(len(backs), 2)
        for n, y in backs:
            gap = y - ev("slv_rn_body") / 2 - play - x1[3]
            self.assertGreaterEqual(gap, 1.5 - 1e-9, "%s's body to X1 at full play: %.3f" % (n, gap))
        # the build and the DXF cut the clearance size, never the rivnut's own hole
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "ceiling_build.py"), encoding="utf-8") as f:
            build = f.read()
        self.assertIn('circle_cut(comp, body, "SKIN " + name, x, y, "hole_slv", "0 mm", "skin_t", ctx)', build)
        import ceiling_exports as E
        with open(os.path.join(here, "ceiling_exports.py"), encoding="utf-8") as f:
            self.assertIn('v["hole_slv"] / 2)', f.read())
        self.assertIn("4 pass-through openings Ø17", E.SIZE_TOL["skin_c2"](VALS)[0])


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
            if kind == "HS" and key in ("frame_c1", "frame_c2"):
                # D-120: the frames became assemblies of member parts but keep 411101 and 411102, the
                # members' parents in the master BOM's allocation (v2/04-BOM/number-allocation.csv)
                self.assertIn(pn, ("411101", "411102"), key)
            elif kind == "HS":
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
    def test_fill_at_d81s_24(self):
        """D-81: the cassette's PET fill is 24 kg/m3 in the model (its material and fill_t's note), in the parts list
        (each strip's material, and its mass: the strip's area less its notches x fill_t x 24 kg/m3), in the rationale's
        fill heading, and in the code that carries it into Fusion (the build's density line, the report's materials
        sync). Reviewer 17 found #306 merged across #348 put 25 back in all of them while every check passed."""
        import csv
        import ceiling_exports as E
        name, rho, _st, src = M.MATERIALS["fill"]
        self.assertEqual(rho, 24.0)
        self.assertIn("24 kg/m3", name)
        self.assertIn("D-81", src)
        self.assertIn("24 kg/m3", [p for p in P if p[0] == "fill_t"][0][4])
        with open(os.path.join(E.OUT, "410000_%s_CEILING-PARTS-LIST_BOM.csv" % E.REV), newline="", encoding="utf-8") as f:
            rows = {r["part_number"]: r for r in csv.DictReader(f)}

        def area_less(box, cuts):
            xs = sorted({box[0], box[1]} | {min(max(b[i], box[0]), box[1]) for b in cuts for i in (0, 1)})
            ys = sorted({box[2], box[3]} | {min(max(b[i], box[2]), box[3]) for b in cuts for i in (2, 3)})
            area = 0.0
            for xa, xb in zip(xs, xs[1:]):
                for ya, yb in zip(ys, ys[1:]):
                    cx, cy = (xa + xb) / 2, (ya + yb) / 2
                    if not any(b[0] < cx < b[1] and b[2] < cy < b[3] for b in cuts):
                        area += (xb - xa) * (yb - ya)
            return area
        seen = set()
        for key, _bay, box, notches in M.fill_strips():
            if key in seen:
                continue
            seen.add(key)
            pn = M.PARTS[key][0]
            b = [ev(e) for e in box]
            mass = area_less(b, [[ev(e) for e in nb] for _n, nb in notches]) * VALS["fill_t"] * rho * 1e-9
            self.assertEqual(rows[pn]["material"], name, pn)
            self.assertAlmostEqual(float(rows[pn]["mass_each_kg"]), mass, delta=0.0006, msg=pn)
        self.assertEqual(len(seen), 3)
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(E.REPO, "v2", "02-Drawings", "ceiling", "FEATURE-RATIONALE.md"), encoding="utf-8") as f:
            heading = [ln for ln in f if ln.startswith("## Fill")]
        self.assertEqual(len(heading), 1)
        self.assertIn("24 kg/m³", heading[0])
        with open(os.path.join(here, "ceiling_build.py"), encoding="utf-8") as f:
            self.assertIn('adsk.core.FloatProperty.cast(m.materialProperties.itemById("structural_Density")).value = density',
                          f.read())
        with open(os.path.join(here, "ceiling_report.py"), encoding="utf-8") as f:
            report = f.read()
        self.assertIn("def sync_materials(design):", report)
        self.assertIn("= sync_materials(design)", report)

    def test_parts_under_20_kg(self):
        v = VALS
        rho = {k: m[1] for k, m in M.MATERIALS.items()}
        # outer panel: 7 tubes + skin
        def kg_m(w, t):                    # galvanized steel tube w x 40 x t (D-131), kg/m
            return (2 * (w + v["frame_t"]) - 4 * t) * t * 1e-6 * rho["steel_fr"]
        tube, tube_in = kg_m(v["tube_w"], v["tube_t"]), kg_m(v["tube_w"], v["tube_t_in"])
        tube40 = kg_m(v["back_w"], v["tube_t"])
        length = 2 * (v["wall_depth"] - v["back_w"]) + 2 * (v["half_fw"] - 2 * v["tube_w"])   # side, seam, front, X1
        frame = tube * length * 1e-3 + tube_in * 2 * (v["half_fw"] - 2 * v["tube_w"]) * 1e-3 + tube40 * v["half_fw"] * 1e-3
        self.assertAlmostEqual(tube40, 1.225, places=3)       # 40 x 40 x 1.0 steel
        skin = v["half_pw"] * v["wall_depth"] * 1e-6 * 3.5
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


class RibBlank(unittest.TestCase):
    def test_blank_is_the_sections_neutral_length(self):
        """The rib's blank against its section worked independently: the straights between the bends' tangent points
        on the model's hat (inside radius r = t at each bend's inside corner) plus four allowances at K 0.44."""
        import math
        import ceiling_exports as E
        t = r = VALS["tray_t"]
        c, f, h = VALS["rib_crown"] / 2, VALS["rib_fl"], VALS["gap_h"]
        # the hat as the build draws it: flanges z -t..0 out to x -(c + f), webs x -c..-(c - t), crown z -h..-(h - t);
        # each bend's inside corner and the tangent points r from it along both legs
        flange = (c + f) - (c + r)            # free edge to the first bend's tangent on the flange's underside
        web = (h - t - r) - (t + r)           # between the two bends' tangents along the web
        crown = 2 * (c - t - r)               # between the crown's two tangents on its top face
        want = 2 * flange + 2 * web + crown + 4 * math.pi / 2 * (r + 0.44 * t)
        got = E.rib_blank(VALS)
        self.assertAlmostEqual(got["width"], want, places=6)
        self.assertAlmostEqual(got["width"], 89.524, places=3)
        self.assertEqual(len(got["bends"]), 4)
        self.assertAlmostEqual(got["bends"][0], flange + got["bend_allowance"] / 2, places=6)
        self.assertAlmostEqual(got["bends"][0] + got["bends"][3], got["width"], places=6)   # symmetric


class RibFolds(unittest.TestCase):
    def test_folds_at_the_hat_corners(self):
        """The rib's four folds (the Lead's ruling on #335): outside corners at bend_r + t, inside at bend_r = t, each
        outside corner a sheet from its inside partner on both axes; the outside corners are convex, the inside ones
        concave."""
        pts = [(ev(x), ev(z)) for x, z in M.rib_section()]
        t, r = VALS["tray_t"], VALS["bend_r"]
        self.assertAlmostEqual(r, t)
        sides = dict(M.RIB_FOLDS)
        self.assertEqual(sorted(sides), [1, 2, 3, 4, 7, 8, 9, 10])
        for o, i in ((1, 10), (9, 2), (8, 3), (4, 7)):
            self.assertEqual((sides[o], sides[i]), ("outside", "inside"))
            self.assertAlmostEqual(abs(pts[o][0] - pts[i][0]), t, msg=(o, i))
            self.assertAlmostEqual(abs(pts[o][1] - pts[i][1]), t, msg=(o, i))
        self.assertAlmostEqual(ev(M.rib_fold_radius("outside")), r + t)
        self.assertAlmostEqual(ev(M.rib_fold_radius("inside")), r)
        # convex (left turn, the outline runs counter-clockwise in x-z) or concave by the cross product at each corner
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) / 2
        for k, side in M.RIB_FOLDS:
            a, b, c = pts[k - 1], pts[k], pts[(k + 1) % len(pts)]
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            convex = (cross > 0) == (area > 0)
            self.assertEqual(convex, side == "outside", (k, side))


class EditFollows(unittest.TestCase):
    def test_pod_width_change(self):
        """Change a skeleton parameter: the layout follows (cassette, frame, fill)."""
        v2 = M.evaluate(P, {"pod_w": "2600 mm"})
        st, ot = v2["stack_t"], v2["outer_t"]
        self.assertAlmostEqual(v2["half_pw"], (2600 - 2 * ot - 3 * 2.26) / 2)
        self.assertAlmostEqual(v2["half_fw"], (2600 - 2 * ot - 2 * 2.26 - 5.5) / 2)
        self.assertAlmostEqual(v2["cs_w"], (2600 - 2 * st) / 2 - 6)
        self.assertAlmostEqual(v2["fill_hw"], (2600 - 2 * st) / 4 - 2.75 - 25)
        self.assertAlmostEqual(v2["ceil_back_pitch"], (v2["half_fw"] - 440) / 3)
        v3 = M.evaluate(P, {"wall_depth": "1520 mm"})
        self.assertAlmostEqual(v3["fr_pitch"], (1520 - 20) / 4)
        self.assertAlmostEqual(v3["cs_d"], 1520 - st - 360 - 6)


if __name__ == "__main__":
    unittest.main(verbosity=1)
