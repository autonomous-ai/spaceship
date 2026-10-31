"""Offline checks of the WALL build scripts, without Fusion.

    python3 v2/01-CAD-Native/wall/test_wall_offline.py

Loads wall_side_panel.py with a stand-in `adsk` module, resolves every
parameter expression the way Fusion would (skeleton P03 first, then the wall
parameters), and checks the values the design relies on: the frame and
cassette sizes, the stile pitch rule, the part numbers and the file names.
"""

import math
import os
import re
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def load(part="panel", side="L", row="1"):
    """Import wall_side_panel.py with fake adsk modules and the given args."""
    fake = types.ModuleType("adsk")
    fake.core = types.ModuleType("adsk.core")
    fake.fusion = types.ModuleType("adsk.fusion")
    sys.modules.update({"adsk": fake, "adsk.core": fake.core, "adsk.fusion": fake.fusion})
    path = os.path.join(HERE, "wall_side_panel.py")
    ns = {"__name__": "wall_side_panel", "__file__": path,
          "SCRIPT_ARGS": {"part": part, "side": side, "row": row, "repo_root": REPO}}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    return ns


def load_back(pos="B1", part="panel"):
    """Import wall_back_panel.py (which runs wall_side_panel.py as its library) with fake adsk modules."""
    fake = types.ModuleType("adsk")
    fake.core = types.ModuleType("adsk.core")
    fake.fusion = types.ModuleType("adsk.fusion")
    sys.modules.update({"adsk": fake, "adsk.core": fake.core, "adsk.fusion": fake.fusion})
    path = os.path.join(HERE, "wall_back_panel.py")
    ns = {"__name__": "wall_back_panel", "__file__": path,
          "SCRIPT_ARGS": {"pos": pos, "part": part, "repo_root": REPO}}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    return ns


# PM rulings of 2026-10-31 that skeleton P04 (PR #24) carries, applied here until it merges: outer panel
# 46 (stack 84), seam gap 2.26 at every site joint, side rows of (wall_h - 2 * seam_gap) / 2.
PENDING_P04 = [("seam_gap", "2.26 mm"), ("outer_t", "46 mm"), ("stack_t", "84 mm"), ("panel_z0", "wall_z0 + seam_gap")]
PENDING_P04_DERIVED = [("side_h", "(wall_h - 2 * seam_gap) / 2")]


def skeleton_with_pending(ns):
    skel = list(ns["skeleton_params"](REPO))
    pending = dict(PENDING_P04)
    skel = [(n, pending[n], u, "confirmed", "pending P04") if n in pending else (n, e, u, st, src)
            for n, e, u, st, src in skel]
    for n, e in PENDING_P04:
        if n not in [p[0] for p in skel]:
            row = (n, e, "mm", "confirmed", "pending P04")
            # plain values first (others use them), expressions last (they use others)
            skel.insert(0, row) if re.fullmatch(r"[\d.]+ mm", e) else skel.append(row)
    if "2 * seam_gap" not in dict((p[0], p[1]) for p in skel)["side_h"]:
        skel = [(n, dict(PENDING_P04_DERIVED).get(n, e), u, st, src) for n, e, u, st, src in skel]
    return skel


def resolve(ns, override=None):
    """All parameter values in mm (or plain numbers), skeleton first, as Fusion evaluates them."""
    skel = skeleton_with_pending(ns)
    by = {p[0]: p for p in skel}
    names = set(ns["SKELETON_NAMES"])
    todo = set(names)
    for _n, expr, _u, _s, _src in ns["WALL_PARAMS"]:
        todo |= ns["names_in"](expr)
    want = set()
    while todo:
        n = todo.pop()
        if n in by and n not in want:
            want.add(n)
            todo |= ns["names_in"](by[n][1])
    vals = {}
    for name, expr, _unit, _status, _src in [p for p in skel if p[0] in want] + list(ns["WALL_PARAMS"]):
        vals[name] = (override or {}).get(name, evaluate(expr, vals)) if name in (override or {}) else evaluate(expr, vals)
    return vals


def evaluate(expr, vals):
    py = re.sub(r"(\d)\s*mm\b", r"\1", expr)
    return eval(py, {"__builtins__": {}}, dict(vals, ceil=math.ceil, floor=math.floor, abs=abs))


# joints register V2-ENG-JNT-01 table 2.1 (main, PR #47): numbers and names of the hardware WALL models
REGISTER_HW = {"838003": "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2",
               "831002": "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL",
               "831001": "HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS"}


class WallSidePanelTest(unittest.TestCase):

    def test_parameters_resolve_to_the_decided_sizes(self):
        v = resolve(load())
        self.assertEqual(v["wall_depth"], 1495)          # D-49
        self.assertAlmostEqual(v["side_h"], 1142.74)     # (2290 - 2 x 2.26) / 2, PM ruling on F-008
        self.assertEqual(v["tube_d"], 40)                # D-34: 20 x 40 x 1.2, behind the 3 mm bond line
        self.assertAlmostEqual(v["pnl_len"], 1492.74)    # 1495 less the decor seam gap
        self.assertAlmostEqual(v["frm_len"], 1489.74)    # less the 3 mm back return
        self.assertEqual(v["stile_n_mid"], 3)
        self.assertAlmostEqual(v["stile_pitch"], 364.935)   # (1489.74 - 10 - 20) / 4, 40 mm back stile
        self.assertLessEqual(v["stile_pitch"], v["stile_pitch_max"])   # D-16, D-34
        self.assertEqual(v["corner_w"], 40)
        self.assertAlmostEqual(v["stile_len"], 1102.74)
        self.assertAlmostEqual(v["side_jnt_pitch"], 351.37)  # 3 bolts, 220 from each end of 1142.74 (R-J14)
        self.assertAlmostEqual(v["len_bolt_pitch"], 350.913, places=3)  # 220 from the ends, 4 even (R-J14)
        self.assertEqual(v["access_d"], 19)              # FR-03: passes the 18 mm head washer
        self.assertEqual(v["bolt_line_y"], 824)          # R-J15: back panel tube centre
        self.assertEqual(v["bolt_d"], 7)                 # PM ruling on F-009
        self.assertEqual(v["tube_t"], 1.2)               # D-85: perimeter members keep 1.2 (they carry the rivnuts)
        self.assertEqual(v["stud_t"], 1.0)               # D-85: intermediate studs at 1.0
        self.assertAlmostEqual(v["rivnut_head_t"] + v["stopw_t"], v["seam_gap"])   # the 2.26 metal stop (R-J5)
        self.assertLess(v["spigot_thread_l"], v["rivnut_len"] + v["rivnut_head_t"])  # thread stays in the rivnut
        self.assertEqual(v["tray_h"], 34)                # returns the full cassette depth, lips hold the felt
        self.assertEqual(v["gap_h"], 24)                 # air gap behind the felt (D-17's 25 less the lip sheet)
        self.assertAlmostEqual(v["cass_len"], 1445)      # decor back plate to past the back cassette's face (D-57)
        self.assertAlmostEqual(v["cass_h"], 1142.74)
        self.assertEqual(v["stack_t"], v["outer_t"] + 4 + v["cass_t"])  # 46 + 4 gap + 34 = 84 (PM ruling)
        self.assertEqual(v["outer_t"], v["skin_t"] + v["bond_t"] + v["tube_d"])

    def test_upper_cassette_floats_under_the_roof_frame(self):
        v = resolve(load(part="cassette", row="2"))
        self.assertAlmostEqual(v["cass_h"], 1142.74 - 46 - 4)   # D-57: lin_gap under the roof frame

    def test_upper_panel_has_the_40_mm_top_member_and_ceiling_bolt_height(self):
        v = resolve(load(row="2"))
        self.assertEqual(v["top_h"], 40)                 # R-J3: 40 x 40 top member on L2, R2
        self.assertAlmostEqual(v["stile_len"], 1142.74 - 20 - 40)
        self.assertAlmostEqual(2400 - v["ceil_bolt_dz"], 2374)   # R-J15: ceiling frame tube centre
        self.assertEqual(resolve(load(row="1"))["top_h"], 20)

    def test_corner_rivnuts_follow_the_back_panel_edge(self):
        """Joints register 2.9: the back corner's 3 bolts run along the back panel's 1118.61 edge."""
        lo, up = resolve(load(row="1")), resolve(load(row="2"))
        for v, want in ((lo, (332.26, 671.57, 1010.87)), (up, (1453.13, 1792.44, 2131.74))):
            for k, w in enumerate(want):
                self.assertAlmostEqual(v["corner_z0"] + v["bolt_edge"] + k * v["corner_bolt_pitch"], w, delta=0.01)

    def test_part_designs_have_their_own_names(self):
        self.assertEqual(load(part="frame")["DOC_NAME"], "211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD")
        self.assertEqual(load(part="tray")["DOC_NAME"], "511101_P01_LINING-TRAY-SIDE-LOWER-LH_CAD")
        self.assertEqual(load(part="skin", side="R", row="2")["DOC_NAME"], "211304_P01_WALL-SKIN-SIDE-UPPER-RH_CAD")

    def test_stile_rule_holds_when_the_wall_depth_changes(self):
        ns = load()
        for depth in (1200, 1495, 1600, 2000):
            vals = resolve(ns, override={"wall_depth": depth})
            self.assertLessEqual(vals["stile_pitch"], 400, depth)
            self.assertGreater(vals["stile_pitch"], 200, depth)

    def test_every_bolt_is_30_clear_of_every_stile(self):
        """R-J14: every bolt along the panel at least 30 mm from any stile face (the 60 mm key pocket fits)."""
        v = resolve(load())
        y0 = 0.0                                          # panel front end
        stiles = [(y0, y0 + 20)] + [(y0 + k * v["stile_pitch"], y0 + k * v["stile_pitch"] + 20)
                                    for k in range(1, int(v["stile_n_mid"]) + 1)] + [(v["frm_len"] - 40, v["frm_len"])]
        for i in range(int(v["n_len_bolt"])):
            yb = y0 + v["bolt_edge"] + i * v["len_bolt_pitch"]
            gap = min(min(abs(yb - a), abs(yb - b)) if not a <= yb <= b else -1 for a, b in stiles)
            self.assertGreaterEqual(gap, 30, "bolt %d at %.2f" % (i, yb))

    def test_part_numbers_and_names(self):
        seen = {}
        for side in ("L", "R"):
            for row in ("1", "2"):
                ns = load(side=side, row=row)
                for key, (pn, name, vn) in ns["PARTS"].items():
                    if pn.startswith("NO-PN"):
                        self.assertTrue(name.startswith("HOLD"), name)
                        continue
                    if key in ns["HW_PARTS"]:       # shared joint hardware: the register's numbers, used by many
                        self.assertIn(pn, REGISTER_HW)
                        self.assertEqual(name, REGISTER_HW[pn])
                        continue
                    self.assertRegex(pn, r"^(21|51)\d{4}$")
                    self.assertNotIn(pn, ns["RESERVED"])
                    self.assertNotIn(pn, seen, "%s used twice" % pn)
                    seen[pn] = name
                    self.assertTrue(vn)
        self.assertEqual(seen["210101"], "WALL - PANEL ASSY - SIDE LOWER - LH")
        self.assertEqual(seen["211101"], "WALL - PANEL FRAME - SIDE LOWER - LH")
        self.assertEqual(seen["211301"], "WALL - SKIN - SIDE LOWER - LH")
        self.assertEqual(seen["510101"], "LINING - CASSETTE - SIDE LOWER - LH")
        self.assertEqual(seen["210104"], "WALL - PANEL ASSY - SIDE UPPER - RH")

    def test_document_names_follow_the_file_rule(self):
        self.assertEqual(load()["DOC_NAME"], "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD")
        self.assertEqual(load(part="cassette")["DOC_NAME"], "510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD")

    def test_every_wall_parameter_has_a_status_and_source(self):
        ns = load()
        for name, expr, unit, status, src in ns["WALL_PARAMS"]:
            self.assertIn(status, ("confirmed", "source", "calculation", "assumption", "unverified"), name)
            self.assertGreater(len(src), 10, name)

    def test_no_number_is_copied_from_the_skeleton(self):
        """The wall script must not restate skeleton values; it derives them from the skeleton."""
        ns = load()
        skel_names = {p[0] for p in skeleton_with_pending(ns)}
        for name, _e, _u, _s, _src in ns["WALL_PARAMS"]:
            self.assertNotIn(name, skel_names, name)
        for n in ns["SKELETON_NAMES"]:
            self.assertIn(n, skel_names, n)


class WallBackPanelTest(unittest.TestCase):

    def test_back_sizes_follow_the_register(self):
        for pos in ("B1", "B2", "B3", "B4"):
            v = resolve(load_back(pos))
            self.assertAlmostEqual(v["half_pw"], 1200.61, places=2)     # skin width (R-J16)
            self.assertAlmostEqual(v["frm_len"], 1198.99, places=2)     # frame width, register 2.8
            self.assertAlmostEqual(v["pnl_h"], 1118.61, places=2)       # both rows, register 2.8
            self.assertEqual(v["stile_n_mid"], 2)                       # D-85: 2 studs at 393
            self.assertAlmostEqual(v["stile_pitch"], 393.0, places=2)
            self.assertAlmostEqual(v["len_bolt_pitch"], 253.0, places=2)   # register 2.9: 220, 473, 725.99, 978.99
            self.assertAlmostEqual(v["side_jnt_pitch"], 339.31, delta=0.01)  # register 2.9: 220, 559.31, 898.61
            self.assertAlmostEqual(v["cass_len"], 1164.87, places=2)    # side lining face to 1.13 short of X 0
            self.assertEqual(v["stud_t"], 1.0)
        self.assertAlmostEqual(resolve(load_back("B1"))["cass_h"], 1118.61, places=2)
        self.assertAlmostEqual(resolve(load_back("B3"))["cass_h"], 1116.87, places=2)   # floats 4 under the roof frame

    def test_back_bolts_are_30_clear_of_every_stile(self):
        v = resolve(load_back("B2"))
        stiles = [(i * v["stile_pitch"], i * v["stile_pitch"] + 20) for i in range(int(v["stile_n_mid"]) + 2)]
        bolts = [220 + i * v["len_bolt_pitch"] for i in range(4)]
        for b in bolts:
            self.assertGreaterEqual(min(min(abs(b - a), abs(b - z)) for a, z in stiles), 30)   # R-J14

    def test_back_part_numbers_names_and_documents(self):
        seen = {}
        for pos in ("B1", "B2", "B3", "B4"):
            ns = load_back(pos)
            for key, (pn, name, vn) in ns["PARTS"].items():
                if pn.startswith("NO-PN") or key in ns["HW_PARTS"]:
                    continue
                self.assertRegex(pn, r"^(21|51)\d{4}$")
                self.assertNotIn(pn, ns["RESERVED"])
                self.assertNotIn(pn, seen, "%s used twice" % pn)
                seen[pn] = name
        self.assertEqual(seen["210201"], "WALL - PANEL ASSY - BACK LOWER - B1")
        self.assertEqual(seen["211204"], "WALL - PANEL FRAME - BACK UPPER - B4")
        self.assertEqual(seen["510202"], "LINING - CASSETTE - BACK LOWER - B2")
        self.assertEqual(load_back("B1")["DOC_NAME"], "210201_P01_WALL-PANEL-ASSY-BACK-LOWER-B1_CAD")
        self.assertEqual(load_back("B3", "cassette")["DOC_NAME"], "510203_P01_LINING-CASSETTE-BACK-UPPER-B3_CAD")
        side = load()
        for pn in seen:
            self.assertNotIn(pn, [p[0] for p in side["PARTS"].values()])

    def test_back_frame_and_skin_ends_meet_the_corner_gap(self):
        for pos, sign in (("B1", -1), ("B2", 1), ("B3", -1), ("B4", 1)):
            ns = load_back(pos)
            v = resolve(ns)
            lo, hi = evaluate(ns["X_LOW"], v), evaluate(ns["X_HIGH"], v)
            slo, shi = evaluate(ns["XS_LOW"], v), evaluate(ns["XS_HIGH"], v)
            outer = 1250 - 46 - 2.26                                  # side frame's room face less the corner gap
            self.assertAlmostEqual(max(abs(lo), abs(hi)), outer, places=2)
            self.assertAlmostEqual(max(abs(slo), abs(shi)), outer, places=2)   # skin flush at the stopped edge
            self.assertAlmostEqual(min(abs(lo), abs(hi)), 2.75, places=2)      # frame: half the closing gap
            self.assertAlmostEqual(min(abs(slo), abs(shi)), 1.13, places=2)    # skin: half the 2.26 seam (R-J16)
            self.assertEqual(sign * (lo + hi) > 0, True)

    def test_back_restates_no_skeleton_number(self):
        skel_names = {p[0] for p in load()["skeleton_params"](REPO)}
        for name, _e, _u, _s, _src in load_back("B2")["WALL_PARAMS"]:
            self.assertNotIn(name, skel_names, name)

    def test_back_parameters_have_status_and_source(self):
        for pos in ("B1", "B4"):
            ns = load_back(pos)
            for name, expr, unit, status, source in ns["WALL_PARAMS"]:
                self.assertIn(status, ("confirmed", "source", "calculation", "assumption", "unverified"), name)
                self.assertTrue(source, name)


if __name__ == "__main__":
    unittest.main()
