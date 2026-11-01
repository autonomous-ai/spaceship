#!/usr/bin/env python3
"""Offline tests of the ELECTRICAL P01 model, parts and documents (no Fusion).

    python3 v2/01-CAD-Native/electrical/test_electrical_offline.py

Checks:
- the skeleton values in electrical_model.py match the skeleton's CSV;
- F-188: the ceiling route's crossing heights, Z 2330 into the ceiling tray's back return and Z 2337.5
  out of its front return, still come out of the skeleton CSV's numbers (CEILING's tray holes share them);
- every reserved space has a positive size, sits only in the skeleton
  envelopes it lists as intended, uses every intended envelope it lists, and
  doesn't overlap another reserved space (box test, 0.1 mm3);
- the routes stay inside the cassettes' 24 mm gap where the model says they're in it;
- the power unit leaves the lining 4 mm clear and stops short of the skin;
- part numbers: unique, in family 71 (or the joints register's hardware
  numbers), never a reserved old number (D-28);
- every 12 V path stays within 3 % voltage drop; every supply within its 60 W;
- connector counts in the parts list match the harness list's plug ends;
- the flat plates (711002, 711005) meet D-89 part 4 as the mechanical check reads it: their DXF
  writer draws only on the CUT layer, in mm, with every circle; their parts-list rows lack nothing;
- the generated documents are up to date (electrical_docs.py --check);
- the 10 generated sheets (wiring diagram A1, 7 assembly sheets A2), read back from the saved PDFs: every letter at
  least 2.5 mm capital height (title-block labels 1.8), no two texts overlapping, nothing outside the frame, the
  harness list's values in full (never cut short), the light figures from the parts data, and the saved files the
  same as the generators make now.
"""

import csv
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "v2", "05-Engineering", "electrical"))
import electrical_model as M  # noqa: E402
import electrical_parts as EP  # noqa: E402

RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}
REGISTER_HW = {"838001", "838003", "838004"}


class Model(unittest.TestCase):
    def setUp(self):
        self.v = M.values()
        self.sk = M.skeleton_boxes(self.v)

    def test_skeleton_values_match_csv(self):
        path = os.path.join(REPO, "v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv")
        rows = {r["parameter"]: float(r.get("value", r.get("value_mm"))) for r in csv.DictReader(open(path, encoding="utf-8"))}
        for k in M.SKELETON_PARAMS:
            self.assertAlmostEqual(rows[k], M.SKELETON_VALUES[k], places=6, msg=k)

    def test_ceiling_crossing_heights_drift(self):
        """F-188 (Lead's ruling 2026-11-01): the ceiling route enters CEILING's tray 513101 through its back
        return level with B4-CASS's felt-only hole, Z 2330 (z_xc), and leaves through its front return at the
        cable gap's middle, Z 2337.5 (z_cg). CEILING's tray reads the same expressions from the skeleton's
        values. A failure here means the skeleton's numbers (or the lip, felt, tray or hole sizes) moved a
        height: CEILING's tray holes must move with it, so tell CEILING and the Mechanical Checker (F-188)."""
        path = os.path.join(REPO, "v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv")
        rows = {r["parameter"]: float(r.get("value", r.get("value_mm"))) for r in csv.DictReader(open(path, encoding="utf-8"))}
        v = M.values({k: rows[k] for k in M.SKELETON_PARAMS})     # the model's expressions on the CSV's numbers
        # the expression agreed with CEILING: pod_h - stack_t + cass_t - 12 (lip) - 6 (hole radius) - 2
        agreed = rows["pod_h"] - rows["stack_t"] + rows["cass_t"] - 12.0 - 6.0 - 2.0
        self.assertAlmostEqual(v["z_xc"], agreed, places=6, msg="z_xc is no longer the expression agreed with CEILING (F-188)")
        self.assertAlmostEqual(v["z_xc"], 2330.0, places=6, msg="the back crossing moved from Z 2330: move CEILING's tray back hole with it (F-188)")
        self.assertAlmostEqual(v["z_cg"], 2337.5, places=6, msg="the front crossing moved from Z 2337.5: move CEILING's tray front hole with it (F-188)")
        # why 2330: B4-CASS's felt-only hole stays 2 mm below the cassette's 12 mm top lip (D-69), which
        # holds only while the lining top (lin_gap) and the ceiling stack (cav_gap) agree
        b4_top = M.skeleton_boxes(v)["B4-CASS"][5]
        self.assertAlmostEqual(b4_top - v["lip_w"] - (v["z_xc"] + v["grm_s"] / 2), 2.0, places=6,
                               msg="B4-CASS's felt-only hole is no longer 2 mm below its top lip")
        # and inside the tray the wire at 2330 is still in the cable gap, above the felt
        self.assertGreaterEqual(v["z_xc"] - v["dw_h"], v["z_cf"] + v["tray_t"] + v["felt_t"])
        # the bodies that carry the two heights
        boxes = {b["code"]: M.body_box(b, v) for b in M.BODIES}
        for code, z in (("FX-CEIL", 2330.0), ("G-CEIL-B", 2330.0), ("G-CEIL-F", 2337.5)):
            self.assertAlmostEqual((boxes[code][2] + boxes[code][5]) / 2, z, places=6, msg=code)

    def test_edit_test_edits_keep_every_body_a_box(self):
        """Each edit the Fusion edit test makes must leave every reserved space with a positive size, or Fusion
        (which turns an inside-out extrude the right way round) and this model disagree (run of 2026-10-31)."""
        for label, ov in M.EDIT_TEST_EDITS:
            v = M.values_with(ov)
            for b in M.BODIES:
                bx = M.body_box(b, v)
                self.assertTrue(bx[0] < bx[3] and bx[1] < bx[4] and bx[2] < bx[5], "%s: %s %s" % (label, b["code"], bx))

    def test_bodies_positive_and_unique_codes(self):
        codes = [b["code"] for b in M.BODIES]
        self.assertEqual(len(codes), len(set(codes)))
        for b in M.BODIES:
            x0, y0, z0, x1, y1, z1 = M.body_box(b, self.v)
            self.assertTrue(x1 > x0 and y1 > y0 and z1 > z0, b["code"])

    def test_clash_with_skeleton_only_where_intended(self):
        for b in M.BODIES:
            bx = M.body_box(b, self.v)
            allowed = {a for a, _why in b["allow"]}
            for name, s in self.sk.items():
                if name in allowed:
                    continue
                self.assertLessEqual(M.overlap(bx, s), 1.0, "%s clashes with %s" % (b["code"], name))
            for a, why in b["allow"]:
                self.assertGreater(M.overlap(bx, self.sk[a]), 0.0, "%s: allow %s isn't needed" % (b["code"], a))
                self.assertTrue(why, "every intended overlap carries its reason")

    def test_no_overlap_between_reserved_spaces(self):
        boxes = [(b["code"], M.body_box(b, self.v)) for b in M.BODIES]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                self.assertLessEqual(M.overlap(boxes[i][1], boxes[j][1]), 0.1, "%s x %s" % (boxes[i][0], boxes[j][0]))

    def test_routes_inside_the_cable_gap(self):
        v = self.v
        back = (v["y_bf"] + v["tray_t"] + v["felt_t"], v["y_bf"] + v["cass_t"] - v["tray_t"])
        right = (v["x_rf"] + v["tray_t"] + v["felt_t"], v["x_rf"] + v["cass_t"] - v["tray_t"])
        ceil = (v["z_cf"] + v["tray_t"] + v["felt_t"], v["z_cf"] + v["cass_t"] - v["tray_t"])
        for b in M.BODIES:
            if b["kind"] != M.B or not b["code"].startswith(("P", "T1", "L1", "C1", "CALL")) or b["code"] == "PU":
                continue
            x0, y0, z0, x1, y1, z1 = M.body_box(b, v)
            allow = {a for a, _w in b["allow"]}
            if allow & {"B2-CASS", "B4-CASS"}:
                self.assertTrue(back[0] - 1e-6 <= y0 and y1 <= back[1] + 1e-6, b["code"])
            elif allow & {"R1-CASS", "R2-CASS"}:
                self.assertTrue(right[0] - 1e-6 <= x0 and x1 <= right[1] + 1e-6, b["code"])
            elif "C2-CASS" in allow:
                self.assertTrue(ceil[0] - 1e-6 <= z0 and z1 <= ceil[1] + 1e-6, b["code"])

    def test_power_unit_clearances(self):
        v = self.v
        pu = M.body_box([b for b in M.BODIES if b["code"] == "PU"][0], v)
        self.assertAlmostEqual(v["cut_x1"] - pu[3], v["cav_gap"], places=6)    # 4 mm to the cassette cut-out
        skin_back = v["pod_d"] / 2 - 6.0                                       # ACP 3 + bond line 3 (skeleton outer_t note)
        self.assertLess(pu[4], skin_back - 2.0)                                # stops short of the skin
        self.assertAlmostEqual((pu[2] + pu[5]) / 2, 1000.0, places=6)          # PM ruling: face at about 1000 mm
        b2 = self.sk["B2"]
        self.assertTrue(b2[0] <= pu[0] and pu[3] <= b2[3] and b2[2] <= pu[2] and pu[5] <= b2[5])


class Parts(unittest.TestCase):
    def test_numbers(self):
        nums = [p["part_number"] for p in EP.P.values()]
        self.assertEqual(len(nums), len(set(nums)))
        for n in nums:
            self.assertEqual(len(n), 6, n)
            self.assertNotIn(n, RESERVED)
            self.assertTrue(n.startswith("71") or n in REGISTER_HW, n)

    def test_every_part_has_mass_or_is_an_assembly(self):
        for k, p in EP.P.items():
            if p["kind"] != "HS":
                self.assertIsNotNone(p["mass_each_kg"], k)
                self.assertTrue(p["mass_status"], k)
                self.assertTrue(p["status"], k)

    def test_supplies_within_rating(self):
        """Each supply carries its loads within its rating and the Class 2 limit at its voltage (NEC Chapter 9 Table
        11(B): 60 VA at 12 V, 100 VA over 20 to 30 V)."""
        for sid, _k, out, rated, _a, _f, _w in EP.SUPPLIES:
            w = sum(q * wm for (_i, _n, s, _fu, q, wm, _t, _st, _src, _no) in EP.LOADS if s == sid)
            self.assertLessEqual(w, rated, sid)
            volts = EP.BUS_V[sid]
            self.assertIn(volts, (12.0, 24.0), sid)
            self.assertLessEqual(rated, 60.0 if volts <= 20 else 100.0, "%s exceeds the Class 2 limit at %s" % (sid, out))

    def test_kit_on_one_24v_feed_under_its_cap(self):
        """D-168: the kit takes one 24 V Class 2 feed (PS1, CLG-100-24), its 60 W peak under the 80 % cap; one
        source, so no two Class 2 sources can share a 0 V. W30 carries it on two cores per pole."""
        feeds = [(s, w) for (i, _n, s, _fu, q, w, _t, _st, _src, _no) in EP.LOADS if "Voice cockpit" in _n]
        self.assertEqual(feeds, [("PS1", EP.KIT_PEAK_W)])
        ps1 = next(x for x in EP.SUPPLIES if x[0] == "PS1")
        self.assertEqual((ps1[1], ps1[2]), ("ps_kit", "24 V DC"))
        self.assertLessEqual(EP.KIT_PEAK_W, EP.KIT_CAP_W)
        self.assertAlmostEqual(EP.KIT_CAP_W, 0.8 * ps1[3])
        self.assertTrue(EP.P["ps_kit"]["sku"].startswith("CLG-100-24"), EP.P["ps_kit"]["sku"])
        self.assertEqual([s[0] for s in EP.SUPPLIES], ["PS1", "PS2", "PS3"])     # PS4 is gone (D-168)
        w30 = [h for h in EP.harnesses(M.values()) if h["id"].startswith("W30")]
        self.assertTrue(w30 and all(h.get("parallel", 1) == 2 and "16 AWG" in h["cable"] for h in w30))

    def test_each_lead_at_its_supplys_voltage(self):
        """Reviewer 7's P3 on #319 (the Lead, 2026-11-01): every lead that names a positive rail ("+24 V", "+12 V")
        carries the voltage of the supply its circuit names first (D-168: PS1 and PS2 at 24 V, PS3 at 12 V), and every
        circuit fed by a supply names one that exists. W12 once read "+12 V" on a 24 V circuit and only the stale-file
        check caught it."""
        import re
        sids = {sid for sid, *_ in EP.SUPPLIES}
        seen = 0
        for h in EP.harnesses(M.values()):
            rails = {float(x) for x in re.findall(r"\+(\d+(?:\.\d+)?) V", h["conductors"])}
            first = h["circuit"].split()[0]
            if first.startswith("PS"):
                self.assertIn(first, sids, h["id"])
            if not rails:
                continue
            seen += 1
            self.assertTrue(first in sids, "%s names +V but no supply: %s" % (h["id"], h["circuit"]))
            self.assertEqual(rails, {EP.BUS_V[first]}, "%s: %s on %s" % (h["id"], h["conductors"], h["circuit"]))
        self.assertGreater(seen, 10)

    def test_light_strips_in_whole_sections(self):
        """D-168: Häfele's 24 V strips cut every 50 mm, so every run is a whole number of sections."""
        for run in EP.UP_RUNS + (EP.DOWN_ROW,):
            self.assertAlmostEqual(run / EP.SECTION_M, round(run / EP.SECTION_M), places=9, msg=run)
        self.assertAlmostEqual(EP.UP_M, sum(EP.UP_RUNS))

    def test_lights_inside_their_budget(self):
        typ = sum(q * t for (i, _n, _s, _fu, q, _wm, t, _st, _src, _no) in EP.LOADS if i in ("LD04", "LD05", "LD08"))
        self.assertLessEqual(typ, EP.LIGHT_BUDGET_W + 1e-6)   # PM ruling: about 22 W, the hub balancing the channels
        self.assertLessEqual(EP.LIGHT_BUDGET_W, 30.0)          # REQ-AIR-06

    def test_voltage_drop_paths(self):
        import electrical_docs as D
        rows = {h["id"]: h for h in D.harness_rows(M.values())}
        for name, ids in EP.CIRCUIT_PATHS:
            d = sum(float(rows[i]["drop_v"]) for i in ids)
            self.assertLessEqual(d / D.circuit_v(rows[ids[0]]["circuit"]), 0.03, name)

    def test_connector_counts_match_the_harness_ends(self):
        rows = EP.harnesses(M.values())
        ends = " | ".join(h["end_a"] + " | " + h["end_b"] for h in rows)
        rec2 = ends.count("Mini-Fit Jr 2-way receptacle")
        plug2 = ends.count("Mini-Fit Jr 2-way plug")
        self.assertEqual(EP.P["rec2"]["qty_per_parent"], rec2)
        self.assertEqual(EP.P["plug2"]["qty_per_parent"], plug2)
        self.assertEqual(EP.P["rec4"]["qty_per_parent"], ends.count("Mini-Fit Jr 4-way receptacle"))
        self.assertEqual(EP.P["plug4"]["qty_per_parent"], ends.count("Mini-Fit Jr 4-way plug") + 1)  # + the cap
        self.assertEqual(EP.P["rec6"]["qty_per_parent"], ends.count("Mini-Fit Jr 6-way receptacle"))
        self.assertEqual(EP.P["plug6"]["qty_per_parent"], ends.count("Mini-Fit Jr 6-way plug"))
        self.assertEqual(EP.P["rec10"]["qty_per_parent"], ends.count("Mini-Fit Jr 10-way receptacle"))
        self.assertEqual(EP.P["plug10"]["qty_per_parent"], ends.count("Mini-Fit Jr 10-way plug"))
        # the 10-way housings carry the air feed's 4 cores (18 AWG) and the hub link's 6 (24 AWG, the 22-28 AWG terminal)
        f = 2 * EP.P["rec2"]["qty_per_parent"] + 6 * EP.P["rec6"]["qty_per_parent"] + 4 * EP.P["rec10"]["qty_per_parent"]
        m = 2 * EP.P["plug2"]["qty_per_parent"] + 6 * EP.P["plug6"]["qty_per_parent"] + 4 * EP.P["plug10"]["qty_per_parent"]
        self.assertEqual(EP.P["term_f"]["qty_per_parent"], f)
        self.assertEqual(EP.P["term_m"]["qty_per_parent"], m)
        self.assertEqual(EP.P["term_f24"]["qty_per_parent"], 6 * EP.P["rec10"]["qty_per_parent"])
        self.assertEqual(EP.P["term_m24"]["qty_per_parent"], 6 * EP.P["plug10"]["qty_per_parent"])
        # the 4-way housings carry the kit's 16 AWG feeds: their own terminals (the cap housing has none)
        self.assertEqual(EP.P["term_f16"]["qty_per_parent"], 4 * EP.P["rec4"]["qty_per_parent"])
        self.assertEqual(EP.P["term_m16"]["qty_per_parent"], 4 * (EP.P["plug4"]["qty_per_parent"] - 1))


class Bought(unittest.TestCase):
    def test_every_bought_line_named_or_held_with_its_reason(self):
        """The Lead's task of 2026-11-01: each bought line names its product from its own datasheet (maker, part
        number, a link), or stays HOLD with its own reason, never the bare HOLD; the joints register's hardware
        (83xxxx) is the register's to name (D-63)."""
        import re
        for p in EP.P.values():
            pn = p["part_number"]
            if p["kind"] != "PI" or pn.startswith("83"):
                continue
            if p["status"] == EP.NAMED_BUY:
                tag = EP.PRODUCTS[pn][0]
                self.assertTrue(p["maker"] and p["sku"] and "http" in p["source"], pn)
                self.assertTrue(p["name"].endswith(" - " + tag), pn)
                self.assertIsNone(re.search(r"\bHOLD\b", p["name"] + " " + p["status"]), pn)
            else:
                self.assertTrue(p["status"].startswith("HOLD (") and p["status"] != EP.HOLD_BUY, (pn, p["status"]))

    def test_no_bought_number_both_named_and_held(self):
        self.assertEqual(set(EP.PRODUCTS) & set(EP.HOLDS), set())
        self.assertEqual(set(EP.PRODUCTS) | set(EP.HOLDS), {p["part_number"] for p in EP.P.values()} & (
            set(EP.PRODUCTS) | set(EP.HOLDS)), "a product or hold names a number the parts list doesn't have")


class Ties(unittest.TestCase):
    def test_tie_points_follow_their_rule(self):
        """The cable ties' holes in WALL's trays (posted 2026-11-01): one clip each (718043); every hole inside its
        cassette, on the tray's back sheet; neighbours on one cable 300 mm apart at most; none within 150 mm of the
        power unit's cut-out (the floating gap)."""
        v = M.values()
        ties = EP.tie_points(v)
        self.assertEqual(EP.P["clip"]["qty_per_parent"], len(ties))
        cas = M.skeleton_boxes(v)
        cut = (v["pu_x0"] - v["pu_clr"], v["pu_x1"] + v["pu_clr"], v["pu_z0"] - v["pu_clr"], v["pu_z1"] + v["pu_clr"])
        runs = {}
        for c, cable, (x, y, z) in ties:
            b = cas[c]
            self.assertTrue(b[0] <= x <= b[3] and b[1] <= y <= b[4] and b[2] <= z <= b[5], (c, x, y, z))
            self.assertTrue(y == b[4] if c.startswith("B") else x == b[3], "on the tray's back sheet: %s" % c)
            dx = max(cut[0] - x, 0, x - cut[1])
            dz = max(cut[2] - z, 0, z - cut[3])
            if c.startswith("B"):
                self.assertGreaterEqual((dx * dx + dz * dz) ** 0.5, EP.TIE_KEEP - 1e-6, (c, x, z))
            if c == "R1-CASS":            # the cables cross the 5 mm gap to the fixed column at FX-COL with slack
                fx = next(M.body_box(b, v) for b in M.BODIES if b["code"] == "FX-COL")
                self.assertGreaterEqual(y - fx[4], EP.TIE_KEEP - 1e-6, (c, y))
            runs.setdefault((c, cable), []).append(z if c in ("B4-CASS", "R2-CASS") else (x if c == "B2-CASS" else y))
        for key, pos in runs.items():
            pos.sort()
            self.assertTrue(all(b - a <= EP.TIE_SPAN + 1e-6 for a, b in zip(pos, pos[1:])), key)


class Column(unittest.TestCase):
    """The harness route through AIR's column and soffit (agreed by ELECTRICAL and CEILING 2026-11-01, the Lead's ask
    on the 16 clashes): the points both sides build to, the air-path ties, and the air-path cables."""

    def setUp(self):
        self.v = M.values()
        self.box = {b["code"]: M.body_box(b, self.v) for b in M.BODIES}

    def test_points_as_agreed(self):
        v, bx = self.v, self.box
        self.assertEqual([round(x, 2) for x in bx["HUB"]], [971.0, -314.0, 1110.0, 1151.0, -285.0, 1290.0])
        self.assertAlmostEqual(v["y_ent"], -307.0)
        self.assertEqual((v["ent_z1"], v["ent_z1"] + v["ent_dz"]), (1150.0, 1175.0))
        self.assertAlmostEqual(v["ch_x"], 1140.0)
        self.assertAlmostEqual(v["sof_y"], -316.0)
        self.assertAlmostEqual(v["fb_y"], -387.64, places=2)
        self.assertEqual([round(v["tie_ay"] + 100 * k, 2) for k in range(3)], [-597.64, -497.64, -397.64])
        self.assertEqual((v["tie_az1"], v["tie_az2"], v["tie_pz"]), (1960.0, 2040.0, 1905.0))
        # every body of the column's route sits inside the column, the soffit or the fan box's plan, never in DR
        for code in ("G-COL1", "G-COL2", "IN-HUB", "CH-FILL", "PL-UP", "PL-RUN", "PL-JOG", "UP-ANG", "TO-SOF",
                     "G-SOF-B", "G-SOFFIT", "G-SOF-N", "SOF-CH", "G-FB-N", "G-FBOX", "G-FB-B"):
            self.assertGreaterEqual(bx[code][1], v["dr_face_y"] + 0.5 - 1e-6, code)
            self.assertLessEqual(bx[code][3], v["col_xr"] + 2.0 + 1e-6, code)

    def test_points_match_airs_model(self):
        """When AIR's model carries the agreed route (CEILING's harness change), the two sides' points are the same."""
        air_dir = os.path.join(REPO, "v2", "01-CAD-Native", "air")
        if not os.path.exists(os.path.join(air_dir, "air_model.py")):
            self.skipTest("no AIR model in this tree")
        sys.path.insert(0, air_dir)
        try:
            import air_model as A
        finally:
            sys.path.remove(air_dir)
        if not hasattr(A, "harness_points"):
            self.skipTest("AIR's model doesn't carry the agreed route yet")
        va = A.evaluate()
        ev = lambda e: A.ev(va, e) if not isinstance(e, (int, float)) else float(e)  # noqa: E731
        hp = A.harness_points()
        tup = lambda x: tuple(round(ev(e), 2) for e in (x if isinstance(x, (tuple, list)) else (x,)))  # noqa: E731
        hz = tuple(round(ev(e), 2) for e in A.hub_zone())
        b = self.box["HUB"]
        self.assertEqual(hz, tuple(round(x, 2) for x in (b[0], b[3], b[1], b[4], b[2], b[5])))
        v = self.v
        self.assertEqual(tup(hp["leg_y"]), (round(v["y_ent"], 2),))
        self.assertEqual(tup(hp["entry_z"]), (v["ent_z1"], v["ent_z1"] + v["ent_dz"]))
        self.assertEqual(tup(hp["tie_z"]), (v["tie_az1"], v["tie_az2"]))
        self.assertEqual(tup(hp["ch_x"]), (round(v["ch_x"], 2),))
        self.assertEqual(tup(hp["sof_y"]), (round(v["sof_y"], 2),))
        self.assertEqual(tup(hp["box_y"]), (round(v["fb_y"], 2),))
        self.assertEqual(tup(hp["plate_y"]), tuple(round(v["tie_ay"] + 100 * k, 2) for k in range(3)))

    def test_air_path_ties_within_150(self):
        """The Lead's rule (2026-11-01): leads in the air path are tied about every 150 mm, so nothing flutters."""
        v = self.v
        # the exhaust lead up the FR angle: from the fill's top, past the two tie pairs, to the soffit's cordgrip
        up = [v["fill_z1"], v["tie_az1"] + v["tie_pp"] / 2, v["tie_az2"] + v["tie_pp"] / 2, self.box["G-SOF-B"][2]]
        # the supply fan and sensor leads along 611108: from the channel's back to DR's opening
        along = [self.box["PL-RUN"][4]] + [v["tie_ay"] + 100 * k for k in range(3)] + [v["dr_face_y"]]
        for run in (up, sorted(along)):
            gaps = [b - a for a, b in zip(sorted(run), sorted(run)[1:])]
            self.assertTrue(all(g <= 150.0 + 1e-6 for g in gaps), gaps)
        # the exhaust lead leaves the top tie pair with room to bend into the cordgrip (about 40 mm)
        self.assertGreaterEqual(self.box["G-SOF-B"][2] - (v["tie_az2"] + v["tie_pp"]), 40.0)

    def test_air_path_cables_flame_rated(self):
        rows = {h["id"]: h for h in EP.harnesses(self.v)}
        for i in ("W40", "W41", "W42"):
            self.assertIn("plenum", rows[i]["cable"], i)
        self.assertNotIn("W32", rows)        # the column's draw wire is gone: one cable per bushing, no cord in the plenum


class FlatParts(unittest.TestCase):
    """D-89 part 4, read with the mechanical check's own code (tools/checks)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(REPO, "tools", "checks"))
        import c_drawings
        import dxf_layers
        import flat_dxf
        cls.cd, cls.dl, cls.fd = c_drawings, dxf_layers, flat_dxf

    def test_dxf_writer_draws_only_on_cut_in_mm(self):
        import tempfile
        lines = [((0, 0), (180, 0)), ((180, 0), (180, 180)), ((180, 180), (0, 180)), ((0, 180), (0, 0))]
        circles = [((10, 10), 2.25), ((50, 50), 8.1), ((150, 50), 3.75)]
        text = self.fd.dxf_text(lines, circles)
        self.assertEqual(self.dl.drawn_layers(text), {"CUT"})
        self.assertEqual(self.dl.other_layers(text), set())
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "x.dxf")
            self.fd.write(path, lines, circles)
            d = self.cd.dxf_summary(path)
        self.assertEqual(d["units"], "4")
        self.assertEqual(sorted(d["circles"]), [4.5, 7.5, 16.2])

    def test_plate_rows_lack_nothing(self):
        for pn in ("711002", "711005"):
            self.assertEqual(self.cd.flat_row_lacks(REPO, pn), [], pn)

    def test_folded_body_is_not_read_as_flat(self):
        lacks = self.cd.flat_row_lacks(REPO, "711001")
        self.assertTrue(any(x.startswith("no bends or machined features") for x in lacks), lacks)


class Docs(unittest.TestCase):
    def test_documents_up_to_date(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "v2/05-Engineering/electrical/electrical_docs.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


DWG = os.path.join(REPO, "v2", "02-Drawings", "electrical")
WD_PDF = os.path.join(DWG, "710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf")
AS_PDFS = ["710001_P01_ELECTRICAL-POWER-UNIT-B2_DWG.pdf", "710011_P01_ELECTRICAL-HARNESS-LIGHT-FEED-B2-B4_DWG.pdf",
           "710021_P01_ELECTRICAL-HARNESS-TRUNK-B2-R1_DWG.pdf", "710023_P01_ELECTRICAL-HARNESS-AIR-COLUMN_DWG.pdf",
           "710024_P01_ELECTRICAL-HARNESS-CALL-LIGHT-R2_DWG.pdf", "710031_P01_ELECTRICAL-DRAW-WIRE-CEILING-ROUTE_DWG.pdf",
           "710041_P01_ELECTRICAL-HUB-AND-CONTROLS-ZONE_DWG.pdf"]
TB_LABELS = {"PROJECT", "TITLE", "DWG / PART NO.", "REV / STATUS", "UNITS / SCALE", "SHEET", "DATE / BY", "SOURCE"}


class LoadTotal(unittest.TestCase):
    def test_load_table_adds_up_to_the_pod_maximum(self):
        """The install sheet (pack.py) sums w_total_max: the column must give the pod's maximum, the voice kit
        counted once at its 60 W peak, not twice at 48 W per feed (168 W on the first kit branch run)."""
        import electrical_docs as D
        rows = D.load_rows()
        total = sum(float(r["w_total_max"]) for r in rows)
        sup = D.supply_summary()
        self.assertAlmostEqual(total, sum(s[2] for s in sup), places=2)
        kit = [r for r in rows if r["id"] in D.KIT_ROWS]
        self.assertEqual([float(r["w_each_max"]) for r in kit], [EP.KIT_PEAK_W])
        self.assertAlmostEqual(sum(float(r["w_total_max"]) for r in kit), EP.KIT_PEAK_W)
        for r in rows:                                     # each load's current at its own supply's voltage (D-168)
            self.assertAlmostEqual(float(r["a_total_max"]), float(r["w_total_max"]) / EP.BUS_V[r["supply"]], places=2)


class Inside(unittest.TestCase):
    """The power unit's inside layout on the 710001 sheet (Reviewer 7 on #337: the three supplies and the light
    controller, about 233 of the 258 mm inside), and its heat check (calc-results section 6)."""

    def test_layout_fits_the_box(self):
        import assembly_sheets as AS
        items = AS.INSIDE
        for name, a, b, c, d, dep, side in items:
            self.assertTrue(0 <= a < c <= AS.INSIDE_W and 0 <= b < d <= AS.INSIDE_H, name)
            self.assertLessEqual(dep, AS.INSIDE_D, name)

        def overlap(p, q):
            return min(p[3], q[3]) > max(p[1], q[1]) and min(p[4], q[4]) > max(p[2], q[2])
        back = [x for x in items if x[6] == "back"]
        front = [x for x in items if x[6] == "front"]
        for i, p in enumerate(back):
            for q in back[i + 1:]:
                self.assertFalse(overlap(p, q), (p[0], q[0]))
        for p in front:
            for q in back:
                if overlap(p, q):
                    self.assertLessEqual(p[5] + q[5], AS.INSIDE_D, (p[0], q[0]))
        # every supply in the parts list is placed
        placed = " ".join(x[0] for x in items)
        for sid, _k, _o, _w, _a, _f, _why in EP.SUPPLIES:
            self.assertIn(sid, placed)

    def test_vents_clear_the_bare_mains_parts(self):
        """UL 62368-1: no vent slot within 15 mm of a bare mains part's band, and none above one."""
        import unit_heat as U
        f = U.part_params("front")
        x0 = f["vent_x1"] - f["vent_l"] / 2 - f["edge_off"]
        mains_x1 = max(f["din_x"] + f["din_w"] / 2, f["gfci_x"] + 43.9 / 2) - f["edge_off"]
        self.assertGreaterEqual(x0 - mains_x1, 15.0)
        self.assertLessEqual(f["vent_w"], 4.0)

    def test_heat_worst_case_under_every_limit(self):
        import unit_heat as U
        air = U.results(EP, 12.0, U.SHELL_PATH_WORST)[0] + U.STRAT_K
        for name, lim, _src in U.DEVICES:
            self.assertLess(air, lim, name)
        for sid, key, rated, _v, _w, feeds in U.case_supplies(EP):
            knee = U.CLG_KNEE if key == "ps_kit" else U.LPV_KNEE
            peak = sum(q * wm for (_i, _n, s_, _f, q, wm, _t, _st, _src, _no) in EP.LOADS if s_ == sid)
            self.assertLess(peak, U.derated(knee, air) * rated, sid)


    def test_heat_margin_at_a_30c_room(self):
        """The Lead (2026-11-01): Reviewer 7 checks a 30 °C room too. With the same worst loads, every part in the box
        keeps at least 5 K under its own limit (the 60 °C leads left only 2 K, so the unit's leads are 75 °C cables)."""
        import unit_heat as U
        room0 = U.ROOM_C
        try:
            U.ROOM_C = 30.0
            air = U.results(EP, 12.0, U.SHELL_PATH_WORST)[0] + U.STRAT_K
        finally:
            U.ROOM_C = room0
        for name, lim, _src in U.DEVICES:
            self.assertGreaterEqual(lim - air, 5.0, name)

class Sheets(unittest.TestCase):
    """The PM's drawing check, item 1 (2026-11-01), and the guideline's "never shrink the font to fit a page",
    read back from the saved PDFs, independent of the generators' own checks."""

    @classmethod
    def setUpClass(cls):
        import fitz
        import sheet_kit as K
        cls.fitz, cls.K = fitz, K
        cls.pdfs = [(WD_PDF, "A1")] + [(os.path.join(DWG, f), "A2") for f in AS_PDFS]

    def norm(self, t):
        return " ".join(t.split())

    def test_letter_sizes_overlaps_and_frame(self):
        K = self.K
        for path, size in self.pdfs:
            doc = self.fitz.open(path)
            for n, page in enumerate(doc, start=1):
                where = "%s sheet %d" % (os.path.basename(path), n)
                w, h = K.SIZES[size]
                self.assertAlmostEqual(page.rect.width / K.MMPT, w, delta=0.5, msg=where)
                self.assertAlmostEqual(page.rect.height / K.MMPT, h, delta=0.5, msg=where)
                boxes = K.ink_boxes(page)
                self.assertTrue(boxes, where)
                small = [b[5] for b in boxes if b[4] < K.BODY - 1e-6 and not (b[5] in TB_LABELS and b[4] >= K.LABEL - 1e-6)]
                self.assertEqual(small, [], "%s: text under 2.5 mm capital height" % where)
                self.assertEqual(K.overlaps(boxes), [], "%s: overlapping text" % where)
                outside = [b[5] for b in boxes if b[0] < 10 or b[1] < 10 or b[2] > w - 10 or b[3] > h - 10]
                self.assertEqual(outside, [], "%s: text outside the frame" % where)

    def test_harness_list_values_in_full(self):
        import electrical_docs as D
        _files, _v, _rows, harness = D.outputs()
        text = self.norm(self.fitz.open(WD_PDF)[1].get_text())
        for hr in harness:
            for key in ("id", "segment", "function", "cable", "end_a", "end_b"):
                self.assertIn(self.norm(hr[key]), text, "%s %s cut short or missing on the harness list" % (hr["id"], key))
            self.assertNotIn("..", text)

    def test_light_figures_from_the_parts_data(self):
        text = self.norm(self.fitz.open(WD_PDF)[0].get_text())
        self.assertIn("uplight %.2f m and down-light 2 x %.2f m (24 V strips)" % (EP.UP_M, EP.DOWN_ROW), text)

    def test_saved_sheets_are_what_the_generators_make(self):
        import tempfile
        import assembly_sheets as AS
        import electrical_docs as D
        import wiring_diagram as WD
        _files, v, rows, harness = D.outputs()
        with tempfile.TemporaryDirectory() as tmp:
            WD.write(os.path.join(tmp, "wd.pdf"), os.path.join(tmp, "wd%d.png"), v, rows, harness)
            made = [(os.path.join(tmp, "wd.pdf"), WD_PDF)]
            for p in AS.write(tmp, v, harness):
                made.append((p, os.path.join(DWG, os.path.basename(p))))
            self.assertEqual(sorted(os.path.basename(b) for _a, b in made[1:]), sorted(AS_PDFS))
            for new, saved in made:
                a, b = self.fitz.open(new), self.fitz.open(saved)
                self.assertEqual(len(a), len(b), saved)
                for pa, pb in zip(a, b):
                    self.assertEqual(pa.get_text(), pb.get_text(), "%s is stale: rerun electrical_docs.py" % saved)
                    self.assertEqual(tuple(pa.rect), tuple(pb.rect), saved)

    def test_sheets_name_autonomous_only(self):
        """D-140, the owner's rule: the BY field and the PDF author and creator read "Autonomous", and no sheet says
        who or what made it; the notes give only the source (the model and parts data)."""
        for path, _size in self.pdfs:
            doc = self.fitz.open(path)
            name = os.path.basename(path)
            self.assertEqual(doc.metadata["author"], "Autonomous", name)
            self.assertEqual(doc.metadata["creator"], "Autonomous", name)
            for n, page in enumerate(doc, start=1):
                where = "%s sheet %d" % (name, n)
                lines = [ln.strip() for ln in page.get_text().splitlines()]
                self.assertIn("DATE / BY", lines, where)
                value = lines[lines.index("DATE / BY") + 1]
                self.assertTrue(value.endswith(" / Autonomous"), "%s: BY reads %r" % (where, value))
                text = self.norm(page.get_text())
                for words in ("Generated by", "Made by", "ELECTRICAL Engineer"):
                    self.assertNotIn(words, text, where)


if __name__ == "__main__":
    unittest.main(verbosity=1)
