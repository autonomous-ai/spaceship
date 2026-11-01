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
        self.assertAlmostEqual(col[1] - col[0], V["pod_w"] / 2 - V["stack_t"] - V["col_gap"] - 949.0)
        sof = b6("SOFFIT FACE FRONT")
        top = b6("SOFFIT RAIL ROOM")
        self.assertAlmostEqual(sof[4], 2120.0, msg="the underside stays at Z 2120 (D-61)")
        self.assertGreaterEqual(V["pod_h"] - V["outer_t"] - top[5], 4.0, "rails clear of the ceiling frame")
        self.assertGreater(sof[5], V["pod_h"] - V["stack_t"], "front face reaches above the ceiling's felt face")
        self.assertAlmostEqual(sof[1] - sof[0], V["pod_w"] - 2 * V["stack_t"] - 2 * V["col_gap"])
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
            self.assertGreaterEqual(b[4], V["floor_t"] + V["mat_t"] - 1e-9, name)
            self.assertLessEqual(b[5], V["dt_zb"] + 1e-9, name)


class Fits(unittest.TestCase):
    def test_no_overlaps(self):
        """No two layout bodies overlap, except the cut-outs the build makes (hub zone in
        the front face and the fill, exhaust grille in the underside)."""
        cut = {(t, "SENSOR HUB ZONE") for t in ("COLUMN FACE FRONT", "COLUMN FILL FRONT")} | {("SOFFIT UNDERSIDE LEFT", "EXHAUST GRILLE")}
        # the stud and lock shanks pass through the rails' forks and holes (cut features)
        cut |= {(r, n) for r in ("SOFFIT RAIL DOOR", "SOFFIT RAIL ROOM") for n in LAY if n.endswith("SHANK")}
        cut |= {("SOFFIT FACE FRONT", n) for n in LAY if n.startswith("STUD") and n.endswith("ROOM HEAD")}   # head pockets
        # the casings are hollow: their bulkheads and linings sit inside (D-121; FanBoxInside checks them)
        cut |= {("%s FAN BOX" % t, n) for t in ("EXHAUST", "SUPPLY") for _k, n, _b in A.fan_box_inner() if t in n}
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
        self.assertAlmostEqual(xir - c[1], 5.0, msg="5 off the floating side lining")
        self.assertAlmostEqual(c[0] - (b6("COLUMN FACE LEFT")[1]), 27.0, msg="27 of fill at the column's left face (air report #110)")
        for plate in ("COLUMN PLENUM PLATE LOW", "COLUMN PLENUM PLATE HIGH"):
            self.assertGreaterEqual(gap(c, b6(plate)), -1e-9, plate)
        yd = V["dr_acc_face_y"]
        self.assertAlmostEqual(c[2] - yd, 5.0)
        e = b6("CARTRIDGE EXHAUST")
        self.assertAlmostEqual(e[2] - yd, 5.0)
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
        self.assertGreater(roof - sof[5], 4.0)
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
            self.assertGreaterEqual(cx - h, bx[0] + V["fbox_t"] - 1e-9, name)
            self.assertLessEqual(cx + h, bx[1] - V["fbox_t"] + 1e-9, name)
            self.assertGreaterEqual(cy - h, bx[2] + V["fbox_t"] - 1e-9, name)
            self.assertLessEqual(cy + h, bx[3] - V["fbox_t"] + 1e-9, name)
            if name.startswith("EXHAUST"):
                # D-121: under the sealed bulkhead at the open top, blowing straight into the roof sleeve
                self.assertAlmostEqual(cz + V["fan_t"], bx[5] - V["blk_t"], msg=name)
            else:
                self.assertLessEqual(cz + V["fan_t"], bx[5] - V["fbox_t"] + 1e-9, name)


class FanBoxInside(unittest.TestCase):
    """D-121 (the Air Engineer's layout, PM ruling 2026-11-01) inside the 3 mm casings: the bulkheads and the linings
    stay inside each casing's walls, clear of the fans and of each other; the exhaust fans keep about 35 mm to the
    side linings; the lined areas are the Air Engineer's (0.103 and 0.046 m2)."""

    def inner(self, tag):
        return [(n, b6(n)) for _k, n, _b in A.fan_box_inner() if tag in n]

    def test_inside_the_walls(self):
        for tag, casing in (("EXHAUST", "EXHAUST FAN BOX"), ("SUPPLY", "SUPPLY FAN BOX")):
            c, t = b6(casing), V["fbox_t"]
            opens = dict(A.FAN_BOX_OPEN[casing])
            for name, b in self.inner(tag):
                for axis, lo, hi in (("x", 0, 1), ("y", 2, 3), ("z", 4, 5)):
                    wall_lo = 0.0 if opens.get(axis) == -1 else t       # an open face has no wall to stay inside
                    wall_hi = 0.0 if opens.get(axis) == 1 else t
                    self.assertGreaterEqual(b[lo], c[lo] + wall_lo - 1e-9, "%s %s" % (name, axis))
                    self.assertLessEqual(b[hi], c[hi] - wall_hi + 1e-9, "%s %s" % (name, axis))

    def test_clear_of_the_fans_and_each_other(self):
        fans = []
        for name, x, y, z in A.fan_points():
            cx, cy, cz = A.ev(V, x), A.ev(V, y), A.ev(V, z)
            h = V["fan_s"] / 2
            fans.append((name, (cx - h, cx + h, cy - h, cy + h, cz, cz + V["fan_t"])))
        parts = self.inner("EXHAUST") + self.inner("SUPPLY")
        for i, (a, ba) in enumerate(parts):
            for name, bf in fans:
                self.assertGreaterEqual(gap(ba, bf), -1e-9, "%s overlaps %s" % (a, name))
            for b, bb in parts[i + 1:]:
                self.assertGreaterEqual(gap(ba, bb), -1e-9, "%s overlaps %s" % (a, b))
        side = [b for n, b in parts if "EXHAUST SIDE" in n]
        for name, bf in fans:
            if name.startswith("EXHAUST"):
                clear = min(bf[2] - side[0][3], side[1][2] - bf[3])
                self.assertAlmostEqual(clear, 34.0, delta=1.5, msg=name)

    def test_lined_areas(self):
        def wall_area(b, normal):
            d = (b[1] - b[0], b[3] - b[2], b[5] - b[4])
            return {"x": d[1] * d[2], "y": d[0] * d[2]}[normal] * 1e-6
        e = sum(wall_area(b, "y" if "SIDE" in n else "x") for n, b in self.inner("EXHAUST") if "LINING" in n)
        s_ = sum(wall_area(b, "x") for n, b in self.inner("SUPPLY") if "LINING" in n)
        self.assertAlmostEqual(e, 0.103, delta=0.003)
        self.assertAlmostEqual(s_, 0.046, delta=0.002)

    def test_bores_on_the_fans(self):
        bores = [(n, a) for n, kind, a in A.features() if n.startswith("FAN BOX BULKHEAD")]
        self.assertEqual(len(bores), 4)
        for (bn, a), (fn, x, y, _z) in zip(bores, A.fan_points()):
            self.assertIn(fn.split()[0], bn)
            self.assertAlmostEqual(A.ev(V, a[0]), A.ev(V, x))
            self.assertAlmostEqual(A.ev(V, a[1]), A.ev(V, y))
            b = b6(bn)
            self.assertAlmostEqual(A.ev(V, a[2]), b[4])                 # the bore runs through the bulkhead
            self.assertAlmostEqual(A.ev(V, a[3]), b[5])


class D120Copies(unittest.TestCase):
    """D-120 (every part one component, identical parts placed as copies): the copies of each part are the same
    size; a stud or screw is one unit (head and shank joined); the right front corner angle is the left one turned
    180 deg about Y, sent to (its x1, y0, z1): every corner of the left angle's outline lands on the right one's."""

    def test_copies_same_size(self):
        size = {}
        for k, n, bx in A.units():
            if k in A.COPIES:
                b = [A.ev(V, e) for e in bx]
                size.setdefault(k, []).append((round(b[1] - b[0], 6), round(b[3] - b[2], 6), round(b[5] - b[4], 6)))
        self.assertEqual(sorted(size), ["hinge", "latch", "lin_es", "lin_s", "lock", "stud"])
        for k, sizes in size.items():
            self.assertEqual(len(set(sizes)), 1, "%s: %s" % (k, sizes))
        self.assertEqual({k: len(v) for k, v in size.items()},
                         {"hinge": 4, "latch": 4, "lin_es": 2, "lin_s": 2, "lock": 2, "stud": 4})

    def test_joined_units(self):
        for k, n, bx in A.units():
            if k not in A.JOINED:
                continue
            u = [A.ev(V, e) for e in bx]
            head, shank = b6(n + " HEAD"), b6(n + " SHANK")
            self.assertEqual(u, [head[0], head[1], head[2], head[3], head[4], shank[5]], n)
            self.assertTrue(head[0] <= shank[0] and shank[1] <= head[1] and head[2] <= shank[2] and shank[3] <= head[3], n)

    def test_right_angle_is_the_left_turned(self):
        fl, fr = b6("COLUMN ANGLE FL"), b6("COLUMN ANGLE FR")
        pts_l = [(A.ev(V, x), A.ev(V, y)) for x, y in A.angle_pts("FL", *[("%r mm" % v) for v in (fl[0], fl[1], fl[2], fl[3])])]
        pts_r = [(A.ev(V, x), A.ev(V, y)) for x, y in A.angle_pts("FR", *[("%r mm" % v) for v in (fr[0], fr[1], fr[2], fr[3])])]
        # the left angle in its own frame (low corner at the origin), turned about Y, sent to (x1, y0, z1) of the right
        moved = {(round(-(x - fl[0]) + fr[1], 6), round((y - fl[2]) + fr[2], 6)) for x, y in pts_l}
        self.assertEqual(moved, {(round(x, 6), round(y, 6)) for x, y in pts_r})
        self.assertAlmostEqual(fl[5] - fl[4], fr[5] - fr[4])          # the same height, so the turn's -z fits

    def test_cartridge_body_is_its_casing(self):
        self.assertEqual(A.PARTS[A.BODY_KEY["cart"]][0], "611301")


class D87(unittest.TestCase):
    """PM rulings 2026-11-01: hooks, locks, the column foot and 5 mm off the linings."""

    def test_off_the_linings(self):
        xir = V["pod_w"] / 2 - V["stack_t"]
        for name, (key, bx) in LAY.items():
            if key in ("box_s", "trans", "riser", "rtrans", "sleeve", "rgrille"):
                continue
            self.assertLessEqual(bx[1], xir - 5.0 + 1e-9, name)
            self.assertGreaterEqual(bx[0], -xir + 5.0 - 1e-9, name)

    def test_foot_on_the_mat(self):
        self.assertAlmostEqual(b6("COLUMN FOOT PLATE")[4], 12.0)

    def test_studs_and_locks_on_the_ceiling_rivnuts(self):
        cv = CM.evaluate(CM.all_params())
        holes = []
        for half in ("C1", "C2"):
            holes += [(n, p) for n, _d, p in CM.hole_positions(cv, half) if n.startswith("SOFFIT")]
        for name in [n for n in LAY if n.endswith("SHANK")]:
            bx = b6(name)
            c = ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2)
            self.assertTrue(any(abs(p[0] - c[0]) < 1e-6 and abs(p[1] - c[1]) < 1e-6 for _n, p in holes), name)
            self.assertAlmostEqual(bx[5], cv["pod_h"] - cv["outer_t"] - V["rvn_head"])   # up to the rivnut head
        self.assertEqual(len(holes), 6)

    def test_forks_open_toward_the_door_and_slide_clear(self):
        """Each fork runs from its rail's door-side edge to the stud; a stud slide mm behind
        its place is clear of both rails' edges, so the soffit lifts straight up."""
        for bname, kind, a in A.features():
            if bname.startswith("SOFFIT RAIL") and kind == "box":
                rail = b6(bname)
                y0, y1 = A.ev(V, a[2]), A.ev(V, a[3])
                self.assertAlmostEqual(y0, rail[2])
                self.assertGreater(y1, y0)
                self.assertLess(y1 - V["slide"] + V["stud_d"] / 2, rail[2], "stud head clear of %s's edge" % bname)

    def test_hub_fits_between_the_angles(self):
        hub, fl, fr = b6("SENSOR HUB ZONE"), b6("COLUMN ANGLE FL"), b6("COLUMN ANGLE FR")
        self.assertGreaterEqual(hub[0], fl[1] - 1e-9)
        self.assertLessEqual(hub[1], fr[0] + 1e-9)
        self.assertAlmostEqual(hub[1] - hub[0], 180.0)

    def test_keyholes_drop_onto_the_studs(self):
        ks = [a for b, k, a in A.features() if b == "COLUMN ANGLE BL" and k == "box"]
        self.assertEqual(len(ks), 2)
        for a in ks:
            self.assertAlmostEqual(A.ev(V, a[5]) - A.ev(V, a[4]), V["key_drop"])
        self.assertLess(V["key_drop"] - 8.0, 3.0, "the column drops onto BASE's 8 mm spigots as it hooks on")


class Hold18(unittest.TestCase):
    """PM ruling 2026-11-01 (HOLD-18): M6 x 16 socket head studs, 6 mm heads, 1.5 clear under each,
    the soffit underside kept at Z 2120."""

    def test_stud_reaches_the_rivnut(self):
        exposed = V["pod_h"] - V["outer_t"] - V["rvn_head"] - b6("SOFFIT RAIL DOOR")[4]
        self.assertAlmostEqual(exposed + V["stud_eng"], V["stud_l"])
        self.assertGreaterEqual(V["stud_eng"], 6.0, "at least one diameter of thread engaged")

    def test_head_room(self):
        for name in [n for n in LAY if n.startswith(("STUD", "LOCK")) and n.endswith("HEAD")]:
            h = b6(name)
            self.assertAlmostEqual(h[5] - h[4], V["hd_h"])
            room = (h[0], h[1], h[2], h[3], h[4] - V["hd_c"], h[4])
            for other, (_k, ob) in LAY.items():
                if other == name or (other == "SOFFIT FACE FRONT" and "ROOM" in name):
                    continue
                self.assertGreaterEqual(gap(room, ob), -1e-9, "%s: %s under its head" % (name, other))


class FrontInterface(unittest.TestCase):
    """PM rulings 2026-11-01: the column and the whole soffit start at the room-side face of DR's
    access panel, FRONT's named value dr_acc_face_y, so neither overlaps the panel; DR's riveted
    band behind the soffit stays (the soffit isn't sealed to DR)."""

    DOOR_SIDE = ("COLUMN FOOT PLATE", "COLUMN FACE LEFT", "COLUMN ANGLE BL", "COLUMN PLENUM PLATE LOW",
                 "COLUMN PLENUM PLATE HIGH", "SOFFIT UNDERSIDE LEFT", "SOFFIT UNDERSIDE RIGHT",
                 "SOFFIT UNDERSIDE FIXED", "SOFFIT RAIL DOOR", "SOFFIT DOOR PLATE")

    def test_door_side_on_the_panel_face(self):
        yd = V["dr_acc_face_y"]
        self.assertAlmostEqual(yd, -643.5)
        for name in self.DOOR_SIDE:
            self.assertAlmostEqual(b6(name)[2], yd, msg=name)
        for name, (_k, bx) in LAY.items():
            if _k not in ("box_s", "blk_s", "lin_s", "trans", "riser", "rtrans", "sleeve", "rgrille", "stud", "lock"):
                self.assertGreaterEqual(bx[2], yd - 1e-9, "%s reaches into DR's access panel" % name)

    def test_door_rail_clear_of_the_sleeve(self):
        self.assertLessEqual(b6("SOFFIT RAIL DOOR")[3], b6("ROOF SLEEVE")[2] - 1.0 + 1e-9)
        self.assertAlmostEqual(b6("SOFFIT RAIL DOOR")[3] - b6("SOFFIT RAIL DOOR")[2], 22.5)

    def test_same_as_front(self):
        """AIR's copies of FRONT's named values carry FRONT's expressions and units (no drift);
        checked against FRONT's DR model whenever its file is in this checkout."""
        mine = {p[0]: (p[1], p[2]) for p in A.AIR_PARAMS if p[0] in A.FRONT_NAMED}
        self.assertEqual(set(mine), set(A.FRONT_NAMED))
        self.assertEqual(mine["dr_acc_face_y"][0], "-pod_d / 2 + decor_d - dr_back_t + dr_acc_t")
        root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        theirs = A.front_named(os.environ.get("FRONT_REPO", root))
        if theirs is None:
            self.skipTest("FRONT's DR model (%s) is not in this checkout yet" % A.FRONT_FILE)
        for name in A.FRONT_NAMED:
            self.assertIn(name, theirs, "FRONT no longer publishes %s" % name)
            self.assertEqual(theirs[name], mine[name], "%s drifted from FRONT's DR model" % name)


class EditTest(unittest.TestCase):
    """Every cut and hole feature lands in its body for each change the edit test makes: a cut
    that finds nothing turns a timeline item unhealthy in Fusion (a soffit latch's cut did, at
    pod_w 2600, until the fill stopped short of the latch line)."""

    def test_cuts_land_for_every_edit(self):
        for edit in [[]] + A.EDITS:
            v = A.evaluate(overrides=dict(edit))
            lay = {n: tuple(A.ev(v, e) for e in bx) for _k, n, bx in A.layout()}
            for target, cb in A.cutouts():
                c, t = tuple(A.ev(v, e) for e in cb), lay[target]
                self.assertTrue(all(min(t[2 * i + 1], c[2 * i + 1]) - max(t[2 * i], c[2 * i]) > 1e-6 for i in range(3)),
                                "%s: a cut in %s finds nothing" % (edit, target))
            for bname, kind, a in A.features():
                t = lay[bname]
                if kind == "box":
                    c = tuple(A.ev(v, e) for e in a)
                elif kind == "zcircle":
                    x, y, z0, z1, d = (A.ev(v, e) for e in a)
                    c = (x - d / 2, x + d / 2, y - d / 2, y + d / 2, z0, z1)
                else:
                    x, z, y0, y1, d = (A.ev(v, e) for e in a)
                    c = (x - d / 2, x + d / 2, y0, y1, z - d / 2, z + d / 2)
                self.assertTrue(all(min(t[2 * i + 1], c[2 * i + 1]) - max(t[2 * i], c[2 * i]) > 1e-6 for i in range(3)),
                                "%s: a %s in %s finds nothing" % (edit, kind, bname))


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
