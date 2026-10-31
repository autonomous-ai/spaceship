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


def resolve(ns):
    """All parameter values in mm (or plain numbers), skeleton first, as Fusion evaluates them."""
    skel = ns["skeleton_params"](REPO)
    used = ns["needed_skeleton"](skel, ns["WALL_PARAMS"])
    vals = {}
    for name, expr, _unit, _status, _src in list(used) + list(ns["WALL_PARAMS"]):
        vals[name] = evaluate(expr, vals)
    return vals


def evaluate(expr, vals):
    py = re.sub(r"(\d)\s*mm\b", r"\1", expr)
    return eval(py, {"__builtins__": {}}, dict(vals, ceil=math.ceil, floor=math.floor, abs=abs))


class WallSidePanelTest(unittest.TestCase):

    def test_parameters_resolve_to_the_decided_sizes(self):
        v = resolve(load())
        self.assertEqual(v["wall_depth"], 1495)          # D-49
        self.assertEqual(v["side_h"], 1145)              # skeleton: (2400 - 110) / 2
        self.assertEqual(v["tube_d"], 40)                # D-34: 20 x 40 x 1.2
        self.assertEqual(v["frm_len"], 1492)             # 1495 - 3 mm back return
        self.assertEqual(v["stile_n_mid"], 3)
        self.assertAlmostEqual(v["stile_pitch"], 368.0)
        self.assertLessEqual(v["stile_pitch"], v["stile_pitch_max"])   # D-16, D-34
        self.assertEqual(v["stile_len"], 1105)
        self.assertEqual(v["tray_ret"], 25)              # D-17
        self.assertEqual(v["cass_len"], 1448)            # D-57
        self.assertEqual(v["cass_h"], 1145)
        self.assertEqual(v["stack_t"], v["outer_t"] + 4 + v["cass_t"])  # 43 + 4 gap + 34 = 81 (D-16, D-42)

    def test_upper_cassette_floats_under_the_roof_frame(self):
        v = resolve(load(part="cassette", row="2"))
        self.assertEqual(v["cass_h"], 1098)              # D-57: 4 mm under the roof frame

    def test_stile_rule_holds_when_the_wall_depth_changes(self):
        ns = load()
        for depth in (1200, 1495, 1600, 2000):
            vals = {}
            skel = ns["skeleton_params"](REPO)
            for name, expr, _u, _s, _src in list(ns["needed_skeleton"](skel, ns["WALL_PARAMS"])) + list(
                    ns["WALL_PARAMS"]):
                vals[name] = depth if name == "wall_depth" else evaluate(expr, vals)
            self.assertLessEqual(vals["stile_pitch"], 400, depth)
            self.assertGreater(vals["stile_pitch"], 200, depth)

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
        """The wall script must not restate skeleton values; it reads them from pod_skeleton.py."""
        ns = load()
        skel_names = {p[0] for p in ns["skeleton_params"](REPO)}
        for name, _e, _u, _s, _src in ns["WALL_PARAMS"]:
            self.assertNotIn(name, skel_names, name)


if __name__ == "__main__":
    unittest.main()
