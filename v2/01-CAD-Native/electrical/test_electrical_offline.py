#!/usr/bin/env python3
"""Offline tests of the ELECTRICAL P01 model, parts and documents (no Fusion).

    python3 v2/01-CAD-Native/electrical/test_electrical_offline.py

Checks:
- the skeleton values in electrical_model.py match the skeleton's CSV;
- every reserved space has a positive size, sits only in the skeleton
  envelopes it lists as intended, uses every intended envelope it lists, and
  doesn't overlap another reserved space (box test, 0.1 mm3);
- the routes stay inside the cassettes' 24 mm gap where the model says they're in it;
- the power unit leaves the lining 4 mm clear and stops short of the skin;
- part numbers: unique, in family 71 (or the joints register's hardware
  numbers), never a reserved old number (D-28);
- every 12 V path stays within 3 % voltage drop; every supply within its 60 W;
- connector counts in the parts list match the harness list's plug ends;
- the generated documents are up to date (electrical_docs.py --check).
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
        rows = {r["parameter"]: float(r["value_mm"]) for r in csv.DictReader(open(path, encoding="utf-8"))}
        for k in M.SKELETON_PARAMS:
            self.assertAlmostEqual(rows[k], M.SKELETON_VALUES[k], places=6, msg=k)

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
        for sid, _k, _o, rated, _a, _f, _w in EP.SUPPLIES:
            w = sum(q * wm for (_i, _n, s, _fu, q, wm, _t, _st, _src, _no) in EP.LOADS if s == sid)
            self.assertLessEqual(w, rated, sid)
            self.assertLessEqual(rated, 60.0, "a 12 V Class 2 source is at most 60 VA")

    def test_lights_inside_30_w(self):
        w = sum(q * wm for (i, _n, _s, _fu, q, wm, _t, _st, _src, _no) in EP.LOADS if i in ("LD04", "LD05"))
        self.assertLessEqual(w, 30.0)

    def test_voltage_drop_paths(self):
        import electrical_docs as D
        rows = {h["id"]: h for h in D.harness_rows(M.values())}
        for name, ids in EP.CIRCUIT_PATHS:
            d = sum(float(rows[i]["drop_v"]) for i in ids)
            self.assertLessEqual(d / 12.0, 0.03, name)

    def test_connector_counts_match_the_harness_ends(self):
        rows = EP.harnesses(M.values())
        ends = " | ".join(h["end_a"] + " | " + h["end_b"] for h in rows)
        rec2 = ends.count("Mini-Fit Jr 2-way receptacle")
        plug2 = ends.count("Mini-Fit Jr 2-way plug")
        self.assertEqual(EP.P["rec2"]["qty_per_parent"], rec2)
        self.assertEqual(EP.P["plug2"]["qty_per_parent"], plug2)
        self.assertEqual(EP.P["rec4"]["qty_per_parent"], ends.count("Mini-Fit Jr 4-way receptacle"))
        self.assertEqual(EP.P["plug4"]["qty_per_parent"], ends.count("Mini-Fit Jr 4-way plug") + 1)  # + the cap
        self.assertEqual(EP.P["rec10"]["qty_per_parent"], ends.count("Mini-Fit Jr 10-way receptacle"))
        self.assertEqual(EP.P["plug10"]["qty_per_parent"], ends.count("Mini-Fit Jr 10-way plug"))
        f = 2 * EP.P["rec2"]["qty_per_parent"] + 4 * EP.P["rec4"]["qty_per_parent"] + 10 * EP.P["rec10"]["qty_per_parent"]
        m = 2 * EP.P["plug2"]["qty_per_parent"] + 4 * (EP.P["plug4"]["qty_per_parent"] - 1) + 10 * EP.P["plug10"]["qty_per_parent"]
        self.assertEqual(EP.P["term_f"]["qty_per_parent"], f)
        self.assertEqual(EP.P["term_m"]["qty_per_parent"], m)


class Docs(unittest.TestCase):
    def test_documents_up_to_date(self):
        r = subprocess.run([sys.executable, os.path.join(REPO, "v2/05-Engineering/electrical/electrical_docs.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
