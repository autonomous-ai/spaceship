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


if __name__ == "__main__":
    unittest.main()
