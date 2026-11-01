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
            self.assertAlmostEqual(back[1] - back[0], VALS["half_fw"], msg="40 x 40 back member over the full width")
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


class Frames(unittest.TestCase):
    """D-117 and D-120 (the Joints Engineer's corner design, Control's member numbers): mitred outer
    corners, every member its own part, the cross members' cleat slots."""

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
            # the members tile the frame's outline (no gap or overlap): their areas add up
            ring = sum(poly_area(pts) for c, (_k, pts) in sh.items() if c in ("SIDE", "SEAM", "FRONT", "BACK"))
            inner = (VALS["half_fw"] - 2 * VALS["tube_w"]) * (VALS["wall_depth"] - VALS["tube_w"] - VALS["back_w"])
            self.assertAlmostEqual(ring, VALS["half_fw"] * VALS["wall_depth"] - inner, places=6)

    def test_every_member_its_own_part(self):
        for half in ("C1", "C2"):
            keys = [k for _c, (k, _p) in self.shapes(half).items()]
            for k in keys:
                pn, name, _vn, kind, mat = M.PARTS[k]
                self.assertEqual(kind, "MP", k)
                self.assertEqual(mat, "al", k)
                self.assertTrue(pn.startswith("412"), k)
            self.assertEqual(keys.count("m_cross"), 2, "X2 and X3 are one common part (412001)")

    def test_cleat_slots(self):
        for half in ("C1", "C2"):
            mem = dict(M.boxes_mm(VALS, [(c, b) for c, _n, _a, b in M.frame_members(half)]))
            slots = M.cleat_slots(half)
            self.assertEqual(len(slots), 6)
            for name, member, xf, y, z, wy, hz in slots:
                y, z, wy, hz = ev(y), ev(z), ev(wy), ev(hz)
                self.assertEqual((wy, hz), (8.0, 22.0))
                k = name.split()[-1]                     # X1, X2 or X3
                cm = mem[k]
                # inside the cross member's footprint on the side or seam member's face
                self.assertGreaterEqual(y - wy / 2, cm[2] - 1e-9, name)
                self.assertLessEqual(y + wy / 2, cm[3] + 1e-9, name)
                self.assertGreaterEqual(z - hz / 2, cm[4] - 1e-9, name)
                self.assertLessEqual(z + hz / 2, cm[5] + 1e-9, name)
                # on the bay-side face of its member
                m = mem[member]
                self.assertTrue(abs(ev(xf) - m[0]) < 1e-9 or abs(ev(xf) - m[1]) < 1e-9, name)
                # clear of every joint hole on that face by 30 (D-117: the bolts' clearance covers them)
                for hn, d, (hx, hy, hz2) in M.hole_positions(VALS, half):
                    if abs(hx - ev(xf)) < 1e-6:
                        self.assertGreaterEqual(abs(hy - y), 30.0, "%s vs %s" % (name, hn))

    def test_identical_in_both_halves(self):
        """For Control (D-120: identical parts share one number): C2's side member is C1's turned upside
        down (every feature centred across its 40 face, the mitres vertical), and C2's cross member 1 is
        C1's turned end for end (its one hanger hole centred across its width, at the same distance from
        the seam end)."""
        zmid = ev(M.ZF0) + VALS["frame_t"] / 2
        for half in ("C1", "C2"):
            for name, member, _x, _y, z, _w, _h in M.cleat_slots(half):
                if member == "SIDE":
                    self.assertAlmostEqual(ev(z), zmid)
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
    def test_parts_under_20_kg(self):
        v = VALS
        rho = {k: m[1] for k, m in M.MATERIALS.items()}
        # outer panel: 7 tubes + skin
        tube = (2 * (v["tube_w"] + v["frame_t"]) - 4 * v["tube_t"]) * v["tube_t"] * 1e-6 * rho["al"]   # kg/m
        tube40 = (2 * (v["back_w"] + v["frame_t"]) - 4 * v["tube_t"]) * v["tube_t"] * 1e-6 * rho["al"]
        length = 2 * (v["wall_depth"] - v["back_w"]) + 4 * (v["half_fw"] - 2 * v["tube_w"])
        frame = tube * length * 1e-3 + tube40 * v["half_fw"] * 1e-3
        self.assertAlmostEqual(tube40, 0.503, places=3)
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
