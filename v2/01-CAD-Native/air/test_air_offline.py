"""Offline checks of the AIR layout (no Fusion needed).

    python3 v2/01-CAD-Native/air/test_air_offline.py

Same parameters as the Fusion build (air_model.py, with the skeleton's own CSV).
Checks the D-61 sizes, that the parts don't overlap, that each cartridge keeps
its 5 mm clearance, that the column and soffit sit inside the pod's lining faces
and meet the ceiling cassettes and the roof frame as planned, and that the roof
sleeve passes through the right outer ceiling panel clear of its members.
"""

import os
import re
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


def pieces(name, v=V):
    """The boxes a layout body is made of, where its own box would overlap its neighbours though its shape doesn't:
    the roof sleeve's walls (in the slot) and its top flange (on the skin); the upper transition's part over the box
    and its part beside it (each piece's box; transition_outlines gives the shapes)."""
    ev = lambda e: A.ev(v, e)
    if name == "ROOF SLEEVE":
        b = tuple(ev(e) for e in A.layout_box(name))
        walls = (ev("slot_x0"), ev("slot_x0 + slot_w"), ev("slot_y0"), ev("slot_y0 + slot_d"), b[4], ev("pod_h"))
        fx0, fx1, fy0, fy1 = (ev(e) for e in A.sleeve_flange())
        return [walls, (fx0, fx1, fy0, fy1, ev("pod_h"), ev("pod_h + slv_t"))]
    lb = A.leg_boxes(name, b6(name) if v is V else tuple(ev(e) for e in A.layout_box(name)), ev)
    if lb:
        return lb
    if name == "SUPPLY TRANSITION":
        out = []
        for pts, z0, z1 in A.transition_outlines():
            xs, ys = [ev(x) for x, _y in pts], [ev(y) for _x, y in pts]
            out.append((min(xs), max(xs), min(ys), max(ys), ev(z0), ev(z1)))
        return out
    return [b6(name)] if v is V else [tuple(ev(e) for e in A.layout_box(name))]


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
        slot = pieces("ROOF SLEEVE")[0]          # the walls in the slot (the flange lies on the skin round it)
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
        cut = {("SOFFIT UNDERSIDE LEFT", "EXHAUST GRILLE")}          # (the hub zone is ELECTRICAL's hub now: no AIR body)
        # the stud and lock shanks pass through the rails' forks and holes (cut features)
        cut |= {(r, n) for r in ("SOFFIT RAIL DOOR", "SOFFIT RAIL ROOM") for n in LAY if n.endswith("SHANK")}
        cut |= {("SOFFIT FACE FRONT", n) for n in LAY if (n.startswith("STUD") and n.endswith("ROOM HEAD"))
                or (n.startswith("LOCK") and n.endswith("HEAD"))}                              # head pockets
        cut |= {("SOFFIT DOOR PLATE", n + " HEAD") for n, _b in A.door_stud_pockets()}           # (PocketsHold checks them)
        # the casings are hollow: their bulkheads and linings sit inside (D-121; FanBoxInside checks them)
        cut |= {("%s FAN BOX" % t, n) for t in ("EXHAUST", "SUPPLY") for _k, n, _b in A.fan_box_inner() if t in n}
        # the bonded fill is notched round each strap (a cut-out the build makes)
        cut |= {("SOFFIT FILL UNDER LEFT", "CARTRIDGE STRAP 1"), ("SOFFIT FILL UNDER RIGHT", "CARTRIDGE STRAP 2"),
                ("SOFFIT FILL UNDER LEFT", "CARTRIDGE STRAP PAD 1"), ("SOFFIT FILL UNDER RIGHT", "CARTRIDGE STRAP PAD 2")}
        # and cut out over the fan box's mount angles and the mounts on them (it swings down past them)
        cut |= {(f, n) for f in ("SOFFIT FILL UNDER RIGHT", "SOFFIT FILL UNDER OVER THE COLUMN") for n in LAY
                if n.startswith("FAN BOX MOUNT")}
        names = list(LAY)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if (a, b) in cut or (b, a) in cut:
                    continue
                for pa in pieces(a):
                    for pb in pieces(b):
                        self.assertGreaterEqual(gap(pa, pb), -1e-9, "%s overlaps %s" % (a, b))

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
        walls, flange = pieces("ROOF SLEEVE")
        for code, _n, _a, b in CM.frame_members("C2"):
            m = tuple(CM.ev(cv, e) for e in b)
            self.assertGreaterEqual(gap(walls, m), 5.0 - 1e-9, "sleeve too close to C2 " + code)
        self.assertAlmostEqual(walls[5], V["pod_h"])
        self.assertAlmostEqual(flange[4], V["pod_h"], msg="the flange lies on C2's skin")
        self.assertAlmostEqual(walls[4], b6("EXHAUST FAN BOX")[5])

    def test_fans_inside_boxes(self):
        boxes = {"SUPPLY": b6("SUPPLY FAN BOX"), "EXHAUST": b6("EXHAUST FAN BOX")}
        for name, x, y, z in A.fan_points():
            bx = boxes[name.split()[0]]
            opens = dict(A.FAN_BOX_OPEN[name.split()[0] + " FAN BOX"])
            cx, cy, cz = A.ev(V, x), A.ev(V, y), A.ev(V, z)
            h = V["fan_s"] / 2
            # inside the walls; on an open face (the exhaust box's left, where the cartridge's air comes in) inside the box
            self.assertGreaterEqual(cx - h, bx[0] + (0.0 if opens.get("x") == -1 else V["fbox_t"]) - 1e-9, name)
            self.assertLessEqual(cx + h, bx[1] - (0.0 if opens.get("x") == 1 else V["fbox_t"]) + 1e-9, name)
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
        bores = [(n, a) for n, kind, a in A.features() if n.startswith("FAN BOX BULKHEAD") and A.ev(V, a[4]) > 20]
        self.assertEqual(len(bores), 4)                 # (the fans' screw holes: BulkheadOpenings)
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
        self.assertEqual(sorted(size), ["hinge", "latch", "lin_es", "lin_s", "lock", "lt_br", "m_ang", "mount", "pad",
                                        "st_ang", "st_pad", "strap", "stud"])
        for k, sizes in size.items():
            self.assertEqual(len(set(sizes)), 1, "%s: %s" % (k, sizes))
        self.assertEqual({k: len(v) for k, v in size.items()},
                         {"hinge": 4, "latch": 4, "lin_es": 2, "lin_s": 2, "lock": 2, "pad": 2, "stud": 4, "lt_br": 4,
                          "m_ang": 2, "mount": 4, "st_ang": 4, "st_pad": 2, "strap": 2})

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

    def test_foot_on_the_floor_top(self):
        # the column's foot stands on the skeleton's floor top: Z 0 since D-132 took the floor out (was Z 12 on the mat)
        self.assertAlmostEqual(b6("COLUMN FOOT PLATE")[4], V["floor_top"])

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
        self.assertEqual(len(holes), 8)    # 2 + 2 hanger rivnuts, 4 lock rivnuts (C2's 2 unused: cross member 1 is one part)

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
        hub, fl, fr = tuple(A.ev(V, e) for e in A.hub_zone()), b6("COLUMN ANGLE FL"), b6("COLUMN ANGLE FR")
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
                if other == name or (other == "SOFFIT FACE FRONT" and ("ROOM" in name or name.startswith("LOCK"))):
                    continue
                if other == "SOFFIT DOOR PLATE" and name.endswith("DOOR HEAD"):     # its pocket (PocketsHold)
                    continue
                self.assertGreaterEqual(gap(room, ob), -1e-9, "%s: %s under its head" % (name, other))


class PocketsHold(unittest.TestCase):
    """The door-side plate's pockets hold each door-side stud's head and the room under it (HOLD-18's 1.5), and
    land in the plate whichever panel face DR has."""

    def test_heads_inside_their_pockets(self):
        plate = b6("SOFFIT DOOR PLATE")
        for n, bx in A.door_stud_pockets():
            p = tuple(A.ev(V, e) for e in bx)
            h = b6(n + " HEAD")
            self.assertLessEqual(p[0], h[0] - V["hd_c"] + 1e-9, n)          # the head plus hd_c across
            self.assertGreaterEqual(p[1], h[1] + V["hd_c"] - 1e-9, n)
            self.assertLessEqual(p[4], h[4] - V["hd_c"] + 1e-9, n)          # the room under the head, up to its top
            self.assertGreaterEqual(p[5], h[5] - 1e-9, n)
            self.assertLessEqual(p[2], plate[2] + 1e-9, n)                  # through the plate's thickness
            self.assertGreaterEqual(p[3], plate[3] - 1e-9, n)
            self.assertLess(gap(p, plate), 0.0, n)                          # the cut finds the plate


class SleeveOneSolid(unittest.TestCase):
    """The flange's opening is the sleeve walls' inside, so the flange covers the walls' top edges all round (one solid:
    cut at the slot's outline it left the flange on an edge only, two solids in the first saved build's STEP)."""

    def test_flange_on_the_wall_tops(self):
        ox0, ox1, oy0, oy1 = (A.ev(V, e) for e in A.sleeve_opening())
        fx0, fx1, fy0, fy1 = (A.ev(V, e) for e in A.sleeve_flange())
        sx0, sw, sy0, sd, t = (V[k] for k in ("slot_x0", "slot_w", "slot_y0", "slot_d", "slv_t"))
        self.assertAlmostEqual(ox0 - sx0, t)
        self.assertAlmostEqual(sx0 + sw - ox1, t)
        self.assertAlmostEqual(oy0 - sy0, t)
        self.assertAlmostEqual(sy0 + sd - oy1, t)
        self.assertTrue(fx0 < sx0 and fx1 > sx0 + sw and fy0 < sy0 and fy1 > sy0 + sd)   # the flange reaches past the walls


class BulkheadOpenings(unittest.TestCase):
    """The fan bulkheads (611403, 611404), by the Lead's rule (2026-11-01): a fan bore is an opening, and keeps at least
    2 x the sheet and 3 mm of material to every edge and to the next bore; the fans' screw holes are fasteners and keep
    2 diameters to every edge and to each other. The exhaust bulkhead's left edge is free (the box is open on that
    face); every other edge meets the casing."""

    def holes(self, tag):
        out = {"bore": [], "screw": []}
        for n, k, a in A.features():
            if n == "FAN BOX BULKHEAD " + tag:
                d = A.ev(V, a[4])
                out["bore" if d > 20 else "screw"].append((A.ev(V, a[0]), A.ev(V, a[1]), d))
        return out

    def test_bores_webs(self):
        need = max(2 * V["blk_t"], 3.0)
        for tag in ("EXHAUST", "SUPPLY"):
            b = b6("FAN BOX BULKHEAD " + tag)
            h = self.holes(tag)
            self.assertEqual(len(h["bore"]), 2, tag)
            for x, y, d in h["bore"]:
                r = d / 2
                for edge in (x - r - b[0], b[1] - x - r, y - r - b[2], b[3] - y - r):
                    self.assertGreaterEqual(edge, need - 1e-9, tag)
            (x1, y1, d1), (x2, y2, d2) = h["bore"]
            self.assertGreaterEqual(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 - (d1 + d2) / 2, need - 1e-9, tag)

    def test_screw_holes_two_diameters(self):
        for tag in ("EXHAUST", "SUPPLY"):
            b = b6("FAN BOX BULKHEAD " + tag)
            h = self.holes(tag)
            self.assertEqual(len(h["screw"]), 8, tag)
            for x, y, d in h["screw"]:
                for edge in (x - b[0], b[1] - x, y - b[2], b[3] - y):
                    self.assertGreaterEqual(edge, 2 * d - 1e-9, "%s screw at %.1f, %.1f" % (tag, x, y))
            s = h["screw"]
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    c2c = ((s[i][0] - s[j][0]) ** 2 + (s[i][1] - s[j][1]) ** 2) ** 0.5
                    self.assertGreaterEqual(c2c, 2 * max(s[i][2], s[j][2]) - 1e-9, tag)
            for x, y, d in h["screw"]:              # each screw clear of the bores
                for bx, by, bd in h["bore"]:
                    self.assertGreater(((x - bx) ** 2 + (y - by) ** 2) ** 0.5 - bd / 2 - d / 2, 2 * V["blk_t"], tag)


class FrontScrews(unittest.TestCase):
    """FRONT's panel screws that stand 7.6 into AIR's space (DR rebuild, 2026-11-01): every AIR body keeps
    fr_scr_clr off each washer and head, except where AIR relieves them, and the reliefs hold them: B08's three
    through the soffit's door-side plate (round, the washer plus the clearance) and into the fill under the exhaust
    cartridge (pockets); nothing shows from below (the underside stays whole); the cartridge 4 clear over B01's."""

    RELIEVED = {"SOFFIT DOOR PLATE": "round", "SOFFIT FILL UNDER": "pocket"}

    def test_clear_or_relieved(self):
        pockets = {n: tuple(A.ev(V, e) for e in bx) for n, bx in A.b08_fill_pockets()}
        clr = V["fr_scr_clr"]
        for sname, wb, hb in A.front_screw_boxes():
            parts = [tuple(A.ev(V, e) for e in wb), tuple(A.ev(V, e) for e in hb)]
            for other, (_k, _ob) in LAY.items():
                for piece in pieces(other):
                    for part in parts:
                        g = gap(part, piece)
                        if g >= clr - 1e-9:
                            continue
                        how = self.RELIEVED.get(other) if sname.startswith("B08") else None
                        self.assertIsNotNone(how, "%s is %.2f off %s's washer or head (wants %g)" % (other, g, sname, clr))
                        if how == "pocket":
                            p = pockets[sname]
                            for k in range(3):
                                if k == 1:          # the head's door side is the plate's business, not the fill's
                                    self.assertGreaterEqual(p[3], part[3] + clr - 1e-9, sname)
                                    continue
                                self.assertLessEqual(p[2 * k], part[2 * k] - clr + 1e-9, sname)
                                self.assertGreaterEqual(p[2 * k + 1], part[2 * k + 1] + clr - 1e-9, sname)

    def test_door_plate_reliefs_round_the_washers(self):
        holes = [(n, a) for n, k, a in A.features() if n == "SOFFIT DOOR PLATE" and k == "ycircle"]
        b08 = [(x, z) for name, x, z in A.FRONT_SCREWS if name.startswith("B08")]
        self.assertEqual(len(holes), len(b08))
        for (_n, a), (x, z) in zip(holes, b08):
            self.assertEqual((a[0], a[1]), (x, z))
            self.assertGreaterEqual(A.ev(V, a[4]) / 2 - V["fr_wsh_d"] / 2, V["fr_scr_clr"] - 1e-9)
            self.assertAlmostEqual(A.ev(V, a[2]), V["dr_acc_face_y"])

    def test_nothing_shows_from_below(self):
        """The undersides carry no relief: their one cut is the exhaust grille's opening (the Ø12 washers stop 2.1
        over the undersides' top face, so the 1 mm relief the Ø18 washers needed is gone)."""
        under = ("SOFFIT UNDERSIDE LEFT", "SOFFIT UNDERSIDE RIGHT", "SOFFIT UNDERSIDE FIXED")
        cuts = [(t, tuple(A.ev(V, e) for e in b)) for t, b in A.cutouts() if t in under]
        eg = b6("EXHAUST GRILLE")
        self.assertEqual([(t, b[:4]) for t, b in cuts], [("SOFFIT UNDERSIDE LEFT", eg[:4])])
        self.assertFalse([n for n, _k, _a in A.features() if n in under[:2]])
        # the fixed part's one hole (ELECTRICAL's exhaust fan leads, 2026-11-01) opens into the column under it, so it
        # can't be seen: wholly inside the column's plan between its front angles' legs and its front face
        col, fr, und = b6("COLUMN FACE FRONT"), b6("COLUMN ANGLE FR"), b6("SOFFIT UNDERSIDE FIXED")
        for n, k, a in A.features():
            if n == "SOFFIT UNDERSIDE FIXED":
                x, y, z0, z1, d = (A.ev(V, e) for e in a)
                self.assertEqual(k, "zcircle")
                self.assertGreaterEqual(x - d / 2, b6("COLUMN ANGLE FL")[1], "over the column, right of its left angle")
                if z1 - z0 < V["face_t"] - 1e-9:
                    # the felt cut back round the cordgrip (ELECTRICAL 2026-11-01 15:47): a recess in the felt only, over
                    # the column's top, clear of the FR angle's legs and short of the underside's room edge
                    self.assertAlmostEqual(z1 - z0, V["face_felt"])
                    self.assertLessEqual(x + d / 2, fr[1] - V["ang_t"], "clear of the FR angle's side leg")
                    self.assertLessEqual(y + d / 2, fr[3] - V["ang_t"], "clear of the FR angle's front leg")
                    self.assertGreaterEqual(und[3] - (y + d / 2), 3.0, "short of the underside's room edge")
                    continue
                self.assertLessEqual(x + d / 2, fr[0], "left of its right angle")
                self.assertLessEqual(y + d / 2, col[2] + 1e-9, "behind the column's front face")
        for sname, wb, _hb in A.front_screw_boxes():
            if sname.startswith("B08"):
                top = max(b6(n)[5] for n in under)
                self.assertGreaterEqual(A.ev(V, wb[4]) - top, V["fr_scr_clr"] - 1e-9, sname)

    def test_cartridge_over_b01(self):
        """4 over B01's washers (the Lead's ruling), its top 5 under the column's opening, and the base plenum under
        it at least the air report's 120 (126 on today's floor, 138 once D-132 takes the floor out)."""
        c = b6("CARTRIDGE SUPPLY")
        for sname, wb, _hb in A.front_screw_boxes():
            if sname.startswith("B01"):
                self.assertAlmostEqual(c[4] - A.ev(V, wb[5]), 4.0, msg=sname)
        self.assertAlmostEqual(V["op_z0"] - c[5], 5.0)
        self.assertGreaterEqual(c[4] - b6("COLUMN FOOT PLATE")[5], V["plen_lo"] - 1e-9)


class PlaceCheck(unittest.TestCase):
    """The Fusion run's position check (air_checks.place_check) fed the layout's own boxes by part number, as
    bodies_by_number reads the model: every unit found, worst 0. The soffit's lock screws are hardware (838002),
    and looking their key up among the parts stopped the dry run of 2026-11-01 08:15 after the whole build passed."""

    def test_the_layout_passes(self):
        import air_checks as K
        got = {}
        for k, _name, bx in A.units():
            got.setdefault(K.number_of(k), []).append([A.ev(V, e) for e in bx])
        worst, bad = K.place_check(got, V)
        self.assertEqual(bad, [])
        self.assertAlmostEqual(worst, 0.0)
        self.assertEqual(K.number_of("lock"), A.HARDWARE["lock"][0])

    def test_every_key_has_a_number(self):
        import air_checks as K
        for k in {k for k, _n, _b in A.units()}:
            self.assertTrue(K.number_of(k))


class FrontInterface(unittest.TestCase):
    """PM rulings 2026-11-01: the column and the whole soffit start at the room-side face of DR's
    access panel, FRONT's named value dr_acc_face_y, so neither overlaps the panel; DR's riveted
    band behind the soffit stays (the soffit isn't sealed to DR)."""

    DOOR_SIDE = ("COLUMN FOOT PLATE", "COLUMN FACE LEFT", "COLUMN ANGLE BL", "COLUMN PLENUM PLATE LOW",
                 "COLUMN PLENUM PLATE HIGH", "SOFFIT UNDERSIDE LEFT", "SOFFIT UNDERSIDE RIGHT",
                 "SOFFIT UNDERSIDE FIXED", "SOFFIT RAIL DOOR", "SOFFIT DOOR PLATE")

    def test_door_side_on_the_panel_face(self):
        yd = V["dr_acc_face_y"]          # FRONT's named value, read from its DR model (Y -643.5 on #105's DR, -641.14 on its stops)
        theirs = A.front_table(A.REPO_ROOT)["dr_acc_face_y"]
        self.assertAlmostEqual(yd, CM.evaluate(CM.all_params() + [p for p in A.front_entries(have={q[0] for q in CM.all_params()})])["dr_acc_face_y"])
        self.assertEqual(theirs[1], dict((p[0], p[1]) for p in A.all_params())["dr_acc_face_y"])
        for name in self.DOOR_SIDE:
            # the underside sections keep the 2 mm joint at the door edge (the Lead's ruling on the soffit hinge)
            want = yd + V["us_jg"] if name.startswith("SOFFIT UNDERSIDE") else yd
            self.assertAlmostEqual(b6(name)[2], want, msg=name)
        for name, (_k, bx) in LAY.items():
            if _k not in ("box_s", "blk_s", "lin_s", "trans", "riser", "rtrans", "sleeve", "rgrille", "stud", "lock",
                          "lip", "pad", "buffer"):
                self.assertGreaterEqual(bx[2], yd - 1e-9, "%s reaches into DR's access panel" % name)

    def test_door_rail_clear_of_the_sleeve(self):
        """1 clear of the roof sleeve, and wide enough to carry each door-side stud's whole head on its fork (22.5 wide
        with DR's panel face at Y -643.5, 20.14 at -641.14: the head's door-side edge still 1.14 inside it)."""
        r = b6("SOFFIT RAIL DOOR")
        self.assertLessEqual(r[3], pieces("ROOF SLEEVE")[0][2] - 1.0 + 1e-9)
        for n, _b in A.door_stud_pockets():
            h = b6(n + " HEAD")
            self.assertLessEqual(r[2], h[2] - 1.0 + 1e-9, n)
            self.assertGreaterEqual(r[3], h[3] + 1.0 - 1e-9, n)

    def test_same_as_front(self):
        """AIR keeps no copy of FRONT's named values (the Lead, 2026-11-01): its list holds only the place they
        go, and the parameters AIR builds carry FRONT's own expressions and units, read from FRONT's DR model,
        with every input those expressions use that the skeleton and the ceiling don't define."""
        self.assertFalse([p[0] for p in A.AIR_PARAMS if p[0] in A.FRONT_NAMED], "a copy of FRONT's value in AIR's list")
        self.assertEqual([p[0] for p in A.AIR_PARAMS].count("@FRONT"), 1)
        theirs = A.front_named(A.REPO_ROOT)
        self.assertIsNotNone(theirs, "FRONT's DR model (%s) is not in this checkout" % A.FRONT_FILE)
        built = {p[0]: (p[1], p[2]) for p in A.all_params()}
        for name in A.FRONT_NAMED:
            self.assertIn(name, theirs, "FRONT no longer publishes %s" % name)
            self.assertEqual(built[name], theirs[name], name)
        names = [p[0] for p in A.all_params()]
        self.assertEqual(len(names), len(set(names)), "a parameter twice")
        for name, expr, _u, _st, _src in A.all_params():        # each parameter after every one it uses
            for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr):
                if ident in names:
                    self.assertLess(names.index(ident), names.index(name), "%s uses %s before it is made" % (name, ident))

    def test_front_inputs_come_along(self):
        """A new input in FRONT's expression comes into AIR's parameters with it, in FRONT's order, without a copy in
        AIR's list. FRONT's dr_pnl_gap came this way (D-142's panel gap); and a test input added to the panel face's
        expression, in a copy of FRONT's model, comes along too and moves the face by its value."""
        import tempfile
        have = {p[0] for p in CM.all_params()}
        names = [p[0] for p in A.front_entries(have=have)]
        self.assertIn("dr_pnl_gap", names)
        self.assertLess(names.index("dr_pnl_gap"), names.index("dr_acc_face_y"))
        with open(os.path.join(A.REPO_ROOT, A.FRONT_FILE), encoding="utf-8") as f:
            src = f.read()
        m = re.search(r'\n([ \t]*)\("dr_acc_face_y", "([^"]+)"', src)
        self.assertIsNotNone(m, "FRONT's DR model names its panel face dr_acc_face_y")
        new = (src[:m.start()] + '\n%s("dr_test_t", "1 mm", "mm", "assumption", "test input"),' % m.group(1)
               + '\n%s("dr_acc_face_y", "%s + dr_test_t"' % (m.group(1), m.group(2)) + src[m.end():])
        base = CM.evaluate(CM.all_params() + A.front_entries(have=have))["dr_acc_face_y"]
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, os.path.dirname(A.FRONT_FILE)))
            with open(os.path.join(d, A.FRONT_FILE), "w", encoding="utf-8") as f:
                f.write(new)
            got = A.front_entries(d, have)
            gn = [p[0] for p in got]
            self.assertIn("dr_test_t", gn)
            self.assertLess(gn.index("dr_test_t"), gn.index("dr_acc_face_y"))
            v = CM.evaluate(CM.all_params() + got)
            self.assertAlmostEqual(v["dr_acc_face_y"], base + 1.0, places=6)


class HarnessRoute(unittest.TestCase):
    """ELECTRICAL's hub and harness through the column and soffit, as agreed with ELECTRICAL on 2026-11-01."""

    def feats(self, body, kind):
        return [tuple(A.ev(V, e) for e in a) for n, k, a in A.features() if n == body and k == kind]

    def test_no_hub_body(self):
        self.assertNotIn("hub", A.PARTS)
        self.assertNotIn("SENSOR HUB ZONE", LAY)
        hub = tuple(A.ev(V, e) for e in A.hub_zone())
        self.assertEqual([round(c, 2) for c in hub], [971.0, 1151.0, -314.0, -285.0, 1110.0, 1290.0])

    def test_fr_angle_points(self):
        """FR is FL turned 180 deg about Y (TURNED): FL's holes, mirrored about the angle's mid-height and moved to the
        right side leg, must land on the agreed points (ELECTRICAL 15:47): entries Ø11.1 at Y -307, Z 1150 and 1175;
        tie pairs Ø6.4 at Z 1960/1975 and 2090/2105."""
        fl, fr = b6("COLUMN ANGLE FL"), b6("COLUMN ANGLE FR")
        got = []
        for y, z, x0, x1, d in self.feats("COLUMN ANGLE FL", "xcircle"):
            self.assertAlmostEqual(x0, fl[0])
            self.assertAlmostEqual(x1 - x0, V["ang_t"])
            got.append((round(y, 2), round(fr[4] + fr[5] - z, 2), d))         # where FR shows it
        self.assertEqual(got, [(-307.0, 1150.0, 11.1), (-307.0, 1175.0, 11.1), (-307.0, 1960.0, 6.4), (-307.0, 1975.0, 6.4),
                               (-307.0, 2090.0, 6.4), (-307.0, 2105.0, 6.4)])
        for _y, z, d in got:          # the opening rule's rim (2 x the sheet, 3 or more) to the angle's ends
            self.assertGreaterEqual(min(z - d / 2 - fr[4], fr[5] - (z + d / 2)), max(2 * V["ang_t"], 3.0))
        for y, _z, d in got:                                                  # the opening rule's 4 mm rims (2 x 2 mm)
            self.assertGreaterEqual(min(y - d / 2 - fr[2], fr[3] - (y + d / 2)), 2 * V["ang_t"] - 1e-9)

    def test_channels_and_holes(self):
        cuts = {t: [] for t in ("COLUMN FILL FRONT", "SOFFIT FILL UNDER OVER THE COLUMN")}
        for t, b in A.cutouts():
            if t in cuts:
                cuts[t].append(tuple(round(A.ev(V, e), 2) for e in b))
        self.assertIn((1128.0, 1152.0, -321.0, -297.0, 1290.0, 1890.0), cuts["COLUMN FILL FRONT"])
        # the hub's cut in the fill runs to the FR angle (X 1152): no sliver between the entries and the hub
        self.assertIn((971.0, 1152.0, -337.0, -285.0, 1110.0, 1290.0), cuts["COLUMN FILL FRONT"])
        self.assertAlmostEqual(b6("COLUMN ANGLE FR")[0], 1152.0)
        (x, y, z0, z1, d), (fx, fy, fz0, fz1, fd) = self.feats("SOFFIT UNDERSIDE FIXED", "zcircle")
        self.assertEqual((round(x, 2), round(y, 2), d), (1140.0, -316.0, 12.0))
        self.assertGreaterEqual(b6("SOFFIT UNDERSIDE FIXED")[3] - (y + d / 2), 2 * 3.0)   # 6 rim on 3 mm ACP
        self.assertEqual((fx, fy, fd, fz0, fz1 - fz0), (x, y, 30.0, z0, V["face_felt"]))   # the felt cut back, ACP left
        (bx, by, bz0, bz1, bd), = self.feats("EXHAUST FAN BOX", "zcircle")
        self.assertEqual((round(bx, 2), round(by, 2), bd), (1140.0, -392.64, 12.0))
        # the leads' Ø25 path up through the far-end lining: wholly inside it, 5 or more of lining all round
        (px, py, pz0, pz1, pd), = self.feats("FAN BOX LINING EXHAUST FAR END", "zcircle")
        lee = b6("FAN BOX LINING EXHAUST FAR END")
        self.assertEqual((px, py, pz0, pz1, pd), (bx, by, lee[4], lee[5], 25.0))
        self.assertGreaterEqual(min(px - pd / 2 - lee[0], lee[1] - (px + pd / 2), py - pd / 2 - lee[2],
                                    lee[3] - (py + pd / 2)), 5.0 - 1e-9)
        lin = b6("FAN BOX LINING EXHAUST SIDE 2")
        self.assertGreaterEqual(lin[2] - (by + bd / 2), 6.0, "the box's hole clear of its room-side lining")
        ch = [c for c in cuts["SOFFIT FILL UNDER OVER THE COLUMN"] if c[0] == 1128.0]
        self.assertEqual(len(ch), 1)
        self.assertLessEqual(ch[0][2], by - bd / 2)                            # the channel reaches both holes
        self.assertGreaterEqual(ch[0][3], y + d / 2)
        ties = self.feats("COLUMN PLENUM PLATE HIGH", "xcircle")
        self.assertEqual(sorted((round(t[0], 2), t[1]) for t in ties),
                         [(-597.64, 1905.0), (-597.64, 1920.0), (-497.64, 1905.0), (-497.64, 1920.0), (-397.64, 1905.0),
                          (-397.64, 1920.0)])
        plate = b6("COLUMN PLENUM PLATE HIGH")
        for ty, tz, _x0, _x1, td in ties:
            self.assertGreaterEqual(tz - td / 2 - plate[4], 6.0, "tie above the plate's bottom edge")
            self.assertTrue(plate[2] < ty - td / 2 and ty + td / 2 < plate[3])


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
                elif kind == "xcircle":
                    y, z, x0, x1, d = (A.ev(v, e) for e in a)
                    c = (x0, x1, y - d / 2, y + d / 2, z - d / 2, z + d / 2)
                else:
                    x, z, y0, y1, d = (A.ev(v, e) for e in a)
                    c = (x - d / 2, x + d / 2, y0, y1, z - d / 2, z + d / 2)
                self.assertTrue(all(min(t[2 * i + 1], c[2 * i + 1]) - max(t[2 * i], c[2 * i]) > 1e-6 for i in range(3)),
                                "%s: a %s in %s finds nothing" % (edit, kind, bname))


# FRONT's DR frame where the supply box assembly meets it (its DR STEP on #313 at 541fe7f, 350003 P01, with D-137's
# 3 mm glue line: every tube 3 off its skin; read 2026-11-01): the shelf tube F08 and the cross tube F07 in the front
# ring (Y -844 to -824, the skin's inner face at -847), the back ring's diagonal tube B06's inner edge in side view
# (X, Z), C04's inner face in plan, the band tube B08's underside and the bolt-line tube B02's face
SKIN_IN = -847.0
F08 = dict(x0=671.63, x1=1029.7, y0=-844.0, y1=-824.0, z1=1650.0)
F07 = dict(x1=1029.7, y1=-824.0, z0=834.0, z1=854.0)
B06_INNER = ((281.73, 2100.0), (773.68, 1532.22))      # the diagonal tube, then the glass-edge tube B07 below it
B07_INNER = ((773.68, 1532.22), (967.52, 150.0))
C04_INNER = ((1049.7, -817.11), (1217.23, -666.5))
B08_Z0, B02_X0 = 2120.0, 1164.0


def seg_dist(p, seg):
    """Distance from point p to the segment seg."""
    (ax, ay), (bx, by) = seg
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return ((p[0] - ax - t * dx) ** 2 + (p[1] - ay - t * dy) ** 2) ** 0.5


def crosses(s1, s2):
    """Whether two segments cross."""
    def o(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    (p, q), (r, t) = s1, s2
    return o(p, q, r) * o(p, q, t) < 0 and o(r, t, p) * o(r, t, q) < 0


def side_of(p, line):
    """Signed distance of point p from the line through line's two points (positive to its left)."""
    (ax, ay), (bx, by) = line
    L = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    return ((bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax)) / L


class SupplyBoxRest(unittest.TestCase):
    """PM rulings 2026-11-01: the box 25 mm back from DR's skin no longer reaches F08, so a lip angle reaches onto it on
    two rubber pads; a buffer on the riser against F07 holds the assembly upright with DR's inner panel off; the outlet's
    seal carries no load."""

    def test_box_where_ruled(self):
        b = b6("SUPPLY FAN BOX")
        self.assertEqual((b[0], b[1], b[2]), (680.0, 980.0, -819.0))
        self.assertAlmostEqual(F08["y1"] - b[2], -5.0, msg="5 mm from F08's back face to the box's front")

    def test_lip_reaches_f08(self):
        lip = b6("FAN BOX LIP ANGLE SUPPLY")
        self.assertAlmostEqual(lip[2] - SKIN_IN, 2.0, msg="the lip's tip 2 mm off DR's skin")
        self.assertAlmostEqual(lip[3], b6("SUPPLY FAN BOX")[2], msg="the lip's upright leg on the box's front wall")
        self.assertGreaterEqual(F08["y1"] - lip[2], 18.0 - 1e-9, msg="the foot covers 18 of F08's 20")
        self.assertAlmostEqual(F08["x1"] - lip[1], 5.0, msg="5 mm short of F02")
        self.assertGreaterEqual(lip[0], F08["x0"], "on F08 at its left end")
        self.assertAlmostEqual(lip[4], F08["z1"] + V["pad_t"], msg="the lip rests on the pads")

    def test_pads_on_f08_under_the_lip(self):
        lip = b6("FAN BOX LIP ANGLE SUPPLY")
        xs = []
        for side in ("LEFT", "RIGHT"):
            p = b6("FAN BOX PAD %s" % side)
            self.assertTrue(F08["x0"] <= p[0] and p[1] <= F08["x1"] and F08["y0"] <= p[2] and p[3] <= F08["y1"], side)
            self.assertTrue(lip[0] <= p[0] and p[1] <= lip[1] and lip[2] <= p[2] and p[3] <= lip[3], side)
            self.assertAlmostEqual(p[4], F08["z1"])
            self.assertAlmostEqual(p[5], lip[4])
            xs.append((p[0] + p[1]) / 2)
        # the assembly's weight centre, about X 940 (CEILING's estimate 2026-11-01: the riser carries half the mass at
        # X 1025), sits between the pads with room either way
        self.assertTrue(xs[0] + 100 < 940.0 < xs[1] - 50, xs)

    def test_buffer_touches_f07_from_the_riser(self):
        buf, riser = b6("RISER BUFFER"), b6("INTAKE RISER")
        self.assertAlmostEqual(buf[2], F07["y1"], msg="set to touch F07's back face")
        self.assertAlmostEqual(riser[2] - buf[3], V["rvn_head"], msg="on the rivnut's head on the riser's front face")
        self.assertTrue(riser[0] <= buf[0] and buf[1] <= F07["x1"], "its whole face on F07, inside the riser's width")
        self.assertAlmostEqual((buf[4] + buf[5]) / 2, (F07["z0"] + F07["z1"]) / 2)
        self.assertTrue(F07["z0"] <= buf[4] and buf[5] <= F07["z1"])

    def test_riser_off_the_panel(self):
        self.assertGreaterEqual(A.ev(V, A.YB_FRAME) - b6("INTAKE RISER")[3], 6.0, "6 mm and more off DR's frame face")


class SupplyTransition(unittest.TestCase):
    """PM rulings 2026-11-01 and the air report #283: the upper transition fills the passage beside the box, the box's
    front line to DR's frame face, Z 1895 to 2110, clear of the corner facet's tube C04; the lower one is FRONT's
    trapezoid, clear of DR's diagonal tube."""

    def test_full_depth(self):
        for pts, z0, z1 in A.transition_outlines():
            ys = [A.ev(V, y) for _x, y in pts]
            self.assertAlmostEqual(min(ys), b6("SUPPLY FAN BOX")[2])
            self.assertAlmostEqual(max(ys), -646.5)
        (top, z0, z1), (side, z2, z3) = A.transition_outlines()
        # up to DR's opening's top, FRONT's Z 2102 (the 12:42 ruling's narrower opening, read from FRONT's model)
        self.assertEqual([A.ev(V, z) for z in (z0, z1, z2, z3)], [1950.0, 2102.0, 1895.0, 1950.0])
        self.assertEqual(max(A.ev(V, x) for x, _y in top + side), 1146.0, "the opening's right edge, FRONT's X 1146")
        self.assertAlmostEqual(A.ev(V, side[0][0]), b6("SUPPLY FAN BOX")[1], msg="beside the box from its right end")

    def test_clear_of_c04_b08_b02(self):
        for pts, _z0, z1 in A.transition_outlines():
            for x, y in pts:
                p = (A.ev(V, x), A.ev(V, y))
                self.assertGreaterEqual(side_of(p, C04_INNER), 3.0 - 1e-6, "corner %s inside 3 mm of C04" % (p,))
            self.assertLessEqual(A.ev(V, z1), B08_Z0 - 10.0 + 1e-9)
            # #313's glue line brought B02 to X 1164: the transition keeps C04's 3 mm (ut_clr) from it too
            self.assertLessEqual(max(A.ev(V, x) for x, _y in pts), B02_X0 - V["ut_clr"] + 1e-9)
        # C04's front end runs straight back along X 1050.85 to Y -820.11: the outline's front corner stays clear of it
        self.assertLess(A.ev(V, "ut_xf"), C04_INNER[0][0] - 6.0)

    def test_lower_transition_clear_of_b06(self):
        """FRONT's trapezoid, in side view, against the back ring's diagonal and glass-edge tubes' inner edges (they lie
        in the depth the transition spans, Y -666.5 to -646.5): no edge crosses them, and the box's lower-left corner,
        the nearest point, keeps FRONT's 4 mm."""
        pts = [(A.ev(V, x), A.ev(V, z)) for x, z in A.riser_transition_outline()]
        edges = list(zip(pts, pts[1:] + pts[:1]))
        for tube in (B06_INNER, B07_INNER):
            for e in edges:
                self.assertFalse(crosses(e, tube), "%s crosses %s" % (e, tube))
                d = min(seg_dist(e[0], tube), seg_dist(e[1], tube), seg_dist(tube[0], e), seg_dist(tube[1], e))
                self.assertGreaterEqual(d, 3.9, "edge %s within %.2f of %s" % (e, d, tube))
            self.assertGreater(side_of(pts[0], tube), 0.0, "the trapezoid lies inside DR, right of %s" % (tube,))
        lay = b6("RISER TRANSITION")          # over the riser's depth, as FRONT reserves it (Reviewer 7)
        self.assertEqual((lay[2], lay[3]), (b6("INTAKE RISER")[2], b6("INTAKE RISER")[3]))

    def test_riser_chamfer_clear_of_the_facet_skin(self):
        """The Lead's ruling 2026-11-01: the riser's front-right edge cut 8 x 8 keeps 6 from DR's corner facet skin. The
        skin's inner face in plan, measured on #313's DR STEP (780aa83) 1.2 off the riser's old corner: through
        (1098.8, -803.89), along C04's direction."""
        p0 = (1098.8, -803.89)
        (ax, ay), (bx, by) = C04_INNER
        L = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        n = ((by - ay) / L, -(bx - ax) / L)                 # the facet's normal, out of DR
        def gap(q):
            return -((q[0] - p0[0]) * n[0] + (q[1] - p0[1]) * n[1])
        corner = (b6("INTAKE RISER")[1], b6("INTAKE RISER")[2])
        self.assertAlmostEqual(gap(corner), 1.2, delta=0.05)         # the edge as it was: the measurement agrees
        for x, y in A.riser_chamfer():
            q = (A.ev(V, x), A.ev(V, y))
            if q != corner:
                self.assertGreaterEqual(gap(q), 6.0, "chamfer end %s only %.2f from the facet skin" % (q, gap(q)))


class TransitionRivets(unittest.TestCase):
    """The AIR Transitions Engineer's 24 rivet holes (their list, 2026-11-01 15:18: each hole's wall and its centre on
    that wall's outer face, pod mm), made in the riser's and the box casing's flats (the Lead's ruling: no hole drilled
    on site). Each goes through its wall face to face, 2 diameters from every edge (the fastener rule), clear of the
    riser's chamfer, the box's linings and its bulkhead."""
    LIST = {  # (body, wall): [(x, y, z)] on the wall's outer face
        ("SUPPLY FAN BOX", "back"): [(750.9, -664.0, 1891.5), (805.3, -664.0, 1891.5), (859.7, -664.0, 1891.5),
                                     (914.1, -664.0, 1891.5)],
        ("SUPPLY FAN BOX", "front"): [(748.0, -819.0, 1941.0), (802.7, -819.0, 1941.0), (857.3, -819.0, 1941.0),
                                      (912.0, -819.0, 1941.0)],
        ("SUPPLY FAN BOX", "left"): [(680.0, -691.0, 1660.0), (680.0, -741.5, 1660.0), (680.0, -792.0, 1660.0)],
        ("SUPPLY FAN BOX", "right"): [(980.0, -691.0, 1660.0), (980.0, -741.5, 1660.0), (980.0, -792.0, 1660.0)],
        ("INTAKE RISER", "back"): [(1051.5, -653.0, 1373.5), (992.5, -653.0, 1373.5)],
        ("INTAKE RISER", "front"): [(1051.5, -803.0, 1373.5), (992.5, -803.0, 1373.5)],
        ("INTAKE RISER", "left"): [(959.0, -677.5, 1373.5), (959.0, -728.0, 1373.5), (959.0, -778.5, 1373.5)],
        ("INTAKE RISER", "right"): [(1098.0, -677.5, 1373.5), (1098.0, -728.0, 1373.5), (1098.0, -778.5, 1373.5)],
    }

    def holes(self):
        """{(body, wall): sorted [(x, y, z) on the outer face]} from the model, with each hole's (depth, d)."""
        out = {}
        for n, k, a in A.transition_rivets():
            b = b6(n)
            if k == "xcircle":
                y, z, x0, x1, d = (A.ev(V, e) for e in a)
                wall, x = ("left", x0) if abs(x0 - b[0]) < 1e-9 else ("right", x1)
                self.assertTrue(abs(x0 - b[0]) < 1e-9 or abs(x1 - b[1]) < 1e-9, (n, a))
                out.setdefault((n, wall), []).append(((round(x, 2), round(y, 2), round(z, 2)), x1 - x0, d))
            else:
                x, z, y0, y1, d = (A.ev(V, e) for e in a)
                self.assertEqual(k, "ycircle")
                wall, y = ("front", y0) if abs(y0 - b[2]) < 1e-9 else ("back", y1)
                self.assertTrue(abs(y0 - b[2]) < 1e-9 or abs(y1 - b[3]) < 1e-9, (n, a))
                out.setdefault((n, wall), []).append(((round(x, 2), round(y, 2), round(z, 2)), y1 - y0, d))
        return out

    def test_the_list(self):
        got = self.holes()
        self.assertEqual(sum(len(h) for h in got.values()), 24)
        self.assertEqual(set(got), set(self.LIST))
        for key, want in self.LIST.items():
            pts = sorted(p for p, _t, _d in got[key])
            for p, q in zip(pts, sorted(want)):
                self.assertTrue(all(abs(a - b) < 0.05 for a, b in zip(p, q)), (key, p, q))   # the list has one decimal
            for _p, t, d in got[key]:
                self.assertAlmostEqual(t, V["rs_t"] if key[0] == "INTAKE RISER" else V["fbox_t"])   # face to face
                self.assertAlmostEqual(d, 4.1)

    def test_edges_and_neighbours(self):
        got, d = self.holes(), V["tr_rv_d"]
        for (n, wall), hs in got.items():
            b = b6(n)
            for (x, y, z), _t, _d in hs:
                along = (y, b[2], b[3]) if wall in ("left", "right") else (x, b[0], b[1])
                self.assertGreaterEqual(min(along[0] - along[1], along[2] - along[0]), 2 * d, (n, wall, x, y, z))
                self.assertGreaterEqual(min(z - b[4], b[5] - z), 2 * d, (n, wall, x, y, z))
        # the riser's chamfer: its front holes left of it, its right-wall holes behind it
        r = b6("INTAKE RISER")
        for (x, _y, _z), _t, _d in got[("INTAKE RISER", "front")]:
            self.assertLessEqual(x + d / 2, r[1] - V["rs_ch"] - 2 * d)
        for (_x, y, _z), _t, _d in got[("INTAKE RISER", "right")]:
            self.assertGreaterEqual(y - d / 2, r[2] + V["rs_ch"] + 2 * d)
        # the box: front and back holes between the end walls' linings; end-wall holes under the bulkhead
        l1, l2, blk = b6("FAN BOX LINING SUPPLY END 1"), b6("FAN BOX LINING SUPPLY END 2"), b6("FAN BOX BULKHEAD SUPPLY")
        for wall in ("front", "back"):
            for (x, _y, _z), _t, _d in got[("SUPPLY FAN BOX", wall)]:
                self.assertTrue(l1[1] + d < x - d / 2 and x + d / 2 < l2[0] - d, (wall, x))
        for wall in ("left", "right"):
            for (_x, _y, z), _t, _d in got[("SUPPLY FAN BOX", wall)]:
                self.assertLess(z + d / 2, blk[4] - d, (wall, z))


class SleeveFlange(unittest.TestCase):
    """J-AIR-03 and HOLD-04's edge rule, CEILING's layout 2026-11-01: each of the grille's 4 rivnuts 2 hole diameters
    (19.06) from every free edge, the skin's slot edge too; their set bulges (about 14 across) clear of C2's members."""

    def setUp(self):
        self.cv = CM.evaluate(CM.all_params())
        self.flange = tuple(A.ev(V, e) for e in A.sleeve_flange())
        self.slot = (V["slot_x0"], V["slot_x0"] + V["slot_w"], V["slot_y0"], V["slot_y0"] + V["slot_d"])
        self.rn = [(n, A.ev(V, x), A.ev(V, y)) for n, x, y in A.sleeve_rivnuts()]

    def test_edge_rule(self):
        fx0, fx1, fy0, fy1 = self.flange
        sx0, sx1, sy0, sy1 = self.slot
        for n, x, y in self.rn:
            in_slot_x, in_slot_y = sx0 < x < sx1, sy0 < y < sy1
            to_slot = (sx0 - x) if in_slot_y else (y - sy1)          # left side or back side
            self.assertTrue(in_slot_x or in_slot_y, n)
            for d in (to_slot, x - fx0, fx1 - x, y - fy0, fy1 - y):
                self.assertGreaterEqual(d, 2 * V["hole_rvn"] - 1e-9, "%s: %.2f from an edge" % (n, d))

    def test_bulges_clear_of_c2_members(self):
        for code, _n, _a, b in CM.frame_members("C2"):
            m = tuple(CM.ev(self.cv, e) for e in b)
            for n, x, y in self.rn:
                r = V["slv_bulge"] / 2
                gap_xy = max(m[0] - (x + r), (x - r) - m[1], m[2] - (y + r), (y - r) - m[3])
                self.assertGreaterEqual(gap_xy, V["slv_rn_clr"] - 1e-9, "%s's bulge meets C2 %s" % (n, code))

    def test_same_layout_as_the_ceiling(self):
        """The rivnut layout's names are the ceiling's too (C2's skin holes): where the ceiling's model has them, AIR's
        copies say the same."""
        theirs = {p[0]: p[1] for p in CM.all_params()}
        for name, expr, _u, _st, _src in A.AIR_PARAMS:
            if name.startswith("slv_rn") or name == "slv_bulge":
                self.assertIn(name, A.AIR_MAY_DEFINE)
                if name in theirs:
                    self.assertEqual(" ".join(theirs[name].split()), " ".join(expr.split()), name)

    def test_grille_covers_the_flange_and_takes_the_bolts(self):
        g = b6("ROOF GRILLE")
        self.assertEqual(tuple(g[:4]), self.flange)
        self.assertAlmostEqual(g[4], V["pod_h"] + V["slv_t"], msg="on the flange")
        holes = sorted((A.ev(V, a[0]), A.ev(V, a[1])) for n, k, a in A.features() if n == "ROOF GRILLE")
        self.assertEqual(holes, sorted((x, y) for _n, x, y in self.rn))


DR_STEP = os.path.join(HERE, "..", "..", "03-Manufacturing", "front", "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step")


def step_vertices(path, prefix):
    """{solid name: set of (x, y, z) vertices, mm} for the solids whose name starts with one of `prefix`, read from a
    Fusion STEP (cm) by following each MANIFOLD_SOLID_BREP's references to its VERTEX_POINTs."""
    import re
    with open(path, encoding="utf-8", errors="replace") as f:
        data = f.read().split("DATA;", 1)[1]
    ents = {int(m.group(1)): m.group(2) for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)", data, re.S)}
    ref = re.compile(r"#(\d+)")
    out = {}
    for k, v in ents.items():
        m = re.match(r"MANIFOLD_SOLID_BREP\s*\(\s*'([^']*)'", v)
        if not m or not m.group(1).startswith(prefix):
            continue
        seen, stack, pts = set(), [k], set()
        while stack:
            e = stack.pop()
            if e in seen:
                continue
            seen.add(e)
            body = ents.get(e, "")
            if body.startswith("VERTEX_POINT"):
                q = ents[int(ref.findall(body)[0])]
                nums = re.findall(r"[-\d.E+]+", q.split("(", 2)[2])
                pts.add(tuple(round(float(x) * 10, 2) for x in nums[:3]))
                continue
            if not body.startswith(("AXIS2_PLACEMENT", "DIRECTION", "CARTESIAN_POINT")):
                stack += [int(x) for x in ref.findall(body)]
        out[m.group(1).split()[0]] = pts
    return out


@unittest.skipUnless(os.path.isfile(DR_STEP), "FRONT's DR STEP isn't in this checkout")
class DrFrameDrift(unittest.TestCase):
    """AIR's copies of DR's frame values (the box's rest on F08 and F07, the transition's clearance to C04, the lower
    transition's to B06) against FRONT's DR STEP in this checkout: when FRONT rebuilds DR, this says what moved."""

    @classmethod
    def setUpClass(cls):
        cls.v = step_vertices(DR_STEP, ("F07 ", "F08 ", "C04 ", "C01 ", "B06 "))

    def test_f08_shelf(self):
        pts = self.v["F08"]
        self.assertAlmostEqual(max(p[0] for p in pts), V["dr_f08_x1"], places=1)
        self.assertAlmostEqual(max(p[2] for p in pts), V["sb_z0"], places=1, msg="F08's top is the box's floor line")
        self.assertAlmostEqual(min(p[1] for p in pts), F08["y0"], places=1)
        self.assertAlmostEqual(max(p[1] for p in pts), F08["y1"], places=1)

    def test_f07_cross(self):
        pts = self.v["F07"]
        zs = sorted({p[2] for p in pts if p[0] == max(q[0] for q in pts)})
        self.assertAlmostEqual((zs[0] + zs[-1]) / 2, V["dr_f07_zc"], places=1)
        self.assertAlmostEqual(max(p[0] for p in pts), V["dr_f08_x1"], places=1)
        self.assertAlmostEqual(max(p[1] for p in pts), F07["y1"], places=1)

    def test_c04_inner_face(self):
        # D-120 (#313): the facet tubes C01, C04 and C05 are one part placed 3 times, differing only in height, so its
        # one body (named C01's) gives C04's plan; DR models before #313 name C04's own body
        pts = self.v.get("C04") or self.v["C01"]
        top = max(p[2] for p in pts)
        plan = {(p[0], p[1]) for p in pts if p[2] == top}
        for x, y in ((V["dr_fac_xa"], V["dr_fac_ya"]), (V["dr_fac_xb"], V["dr_fac_yb"])):
            self.assertTrue(any(abs(x - a) < 0.05 and abs(y - b) < 0.05 for a, b in plan), (x, y, sorted(plan)))

    def test_b06_inner_edge(self):
        xz = {(p[0], p[2]) for p in self.v["B06"]}
        for x, z in B06_INNER:
            self.assertTrue(any(abs(x - a) < 0.05 and abs(z - b) < 0.05 for a, b in xz), (x, z))


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
