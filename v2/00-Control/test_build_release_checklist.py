#!/usr/bin/env python3
"""Tests for build_release_checklist.py (doc code V2-CTL-011): one planted case per rule.

Run: python3 v2/00-Control/test_build_release_checklist.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("rc", HERE / "build_release_checklist.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
BOM = rc.load_bom()

PLAN = """
| ID | Applies to | Characteristic | Nominal |
|---|---|---|---|
| K-J01 | `2111xx` `4111xx` | Bolt clearance hole | Ø7.0 |
| K-P01 | `210xxx` | Panel size | as stated |

| ID | Check | Pass mark |
|---|---|---|
| F-03 | Every seam and seal: no light | no light |

| Applies to | Part | Test | Source |
|---|---|---|---|
| `518001` | Cassette clip | T07 | test plan |
| `848012` | Edge seal | F-03 | light test |
"""
REGISTER = """
| ID | Part number | Name | Make or buy | Qty | Status |
|---|---|---|---|---|---|
| H-01 | **838001** | HARDWARE - BOLT - M6 X 16 | bought | 72 | PROPOSED number; part DECIDED (R-J2) |
| H-10 | **518001** | LINING - CASSETTE CLIP | bought | 44 | number as CEILING uses it; part HOLD-08 |
| H-22 | **368102** | FRONT - DOOR STRIKE | bought | 1 | adopted; product per FRONT's parts list |
"""
WALL = "v2/03-Manufacturing/wall/210000_P01_WALL_BOM.csv"


def row(pn, make_buy, name="PART", material="", team="WALL", mass=1.0, finish="", hold=False, src=WALL):
    return {"part_number": pn, "make_buy": make_buy, "name": name, "material": material, "process": "", "team": team,
            "mass_each_kg": mass, "finish": finish, "hold": hold, "source_file": f"{src} @ working tree"}


def files(*names, folder="v2/01-CAD-Native/wall/"):
    return {folder + n: "working tree" for n in names}


def run(parts, file_map, screen="unlocked", register_text=REGISTER, tests=()):
    fai = rc.fai_plan(PLAN, BOM)
    register = BOM.parse_register(register_text, "test")
    return rc.check_parts(parts, register, rc.files_by_pn(file_map), list(file_map), fai, list(tests) + fai[1],
                          rc.register_products(register_text, BOM), screen, BOM, {}, {})


ALL_FRAME_FILES = files("211101_P01_WALL-FRAME_CAD.f3d", "211101_P01_WALL-FRAME_STEP.step",
                        "211101_P01_WALL-FRAME_DWG.pdf", "211101_P01_WALL-FRAME-CUT-LIST_BOM.csv")


class FaiPlan(unittest.TestCase):
    def test_reads_characteristics_checks_and_bought_tests(self):
        chars, checks, accept = rc.fai_plan(PLAN, BOM)
        self.assertEqual([c[0] for c in chars], ["K-J01", "K-P01"])
        self.assertTrue(chars[0][1][0].fullmatch("211101"))
        self.assertFalse(any(p.fullmatch("211301") for p in chars[0][1]))  # a skin is not a frame
        self.assertEqual([c[0] for c in checks], ["F-03"])
        self.assertEqual([ids for _, ids in accept], [["T07"], ["F-03"]])

    def test_the_real_plan_parses(self):
        text = (rc.ROOT / rc.FAI).read_text(encoding="utf-8")
        chars, checks, accept = rc.fai_plan(text, BOM)
        self.assertGreater(len(chars), 30)
        self.assertGreater(len(checks), 5)
        self.assertGreater(len(accept), 10)
        self.assertTrue(all(pats for _, pats in chars), "every characteristic names the numbers it applies to")


class MadeParts(unittest.TestCase):
    def frame(self, **kw):
        return row("211101", "make", "WALL - PANEL FRAME", "aluminium 6063-T6 tube 20 x 40 x 1.2, mill finish", **kw)

    def test_done_when_everything_is_in(self):
        file_map = dict(ALL_FRAME_FILES)
        cut = "v2/03-Manufacturing/wall/211101_P01_WALL-FRAME-CUT-LIST_BOM.csv"
        file_map[cut] = "working tree"
        fai = rc.fai_plan(PLAN, BOM)
        made, _ = rc.check_parts([self.frame()], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked",
                                 BOM, {}, {cut: "211101,cut,..."})
        self.assertEqual(made[0]["state"], "done", made[0]["gaps"])

    def test_only_the_drawing_missing_is_blocked_when_the_screen_is_locked(self):
        file_map = files("211101_P01_WALL-FRAME_CAD.f3d", "211101_P01_WALL-FRAME_STEP.step")
        r = self.frame()
        r["cut_rows"] = True
        made, _ = run([r], file_map, screen="locked")
        self.assertEqual(made[0]["state"], rc.BLOCKED)
        made, _ = run([dict(r)], file_map, screen="unlocked")
        self.assertEqual(made[0]["state"], "open: drawing")

    def test_a_tube_needs_its_cut_list(self):
        file_map = files("211101_P01_WALL-FRAME_CAD.f3d", "211101_P01_WALL-FRAME_STEP.step", "211101_P01_WALL-FRAME_DWG.pdf")
        made, _ = run([self.frame()], file_map)
        self.assertEqual(made[0]["gaps"], ["DXF or cut list"])

    def test_a_sheet_part_needs_its_own_dxf(self):
        skin = row("211301", "make", "WALL - SKIN", "ACP 3 mm EV3038")
        file_map = files("210101_P01_WALL-PANEL_CAD.f3d", "210101_P01_WALL-PANEL_STEP.step", "211301_P01_WALL-SKIN_DWG.pdf")
        unit = row("210101", "assembly", "WALL - PANEL ASSY")
        made, _ = run([unit, skin], file_map)
        self.assertEqual(made[1]["gaps"], ["DXF or cut list", "FAI"])  # CAD and STEP come from the assembly's file
        self.assertEqual(made[0]["flat"], "n/a")

    def test_metal_needs_a_finish_and_a_mass(self):
        bare = row("211101", "make", "WALL - PANEL FRAME", "aluminium 6063-T6 tube 20 x 40 x 1.2", mass=None)
        bare["cut_rows"] = True
        made, _ = run([bare], ALL_FRAME_FILES)
        self.assertEqual(made[0]["gaps"], ["mass", "finish"])

    def test_one_line_per_number_in_a_team(self):
        made, _ = run([self.frame(), self.frame()], ALL_FRAME_FILES)
        self.assertEqual(len(made), 1)

    def test_a_part_with_files_but_no_bom_row(self):
        file_map = files("211102_P01_WALL-PANEL-FRAME-RH_CAD.f3d", "211102_P01_WALL-PANEL-FRAME-RH_STEP.step")
        extra = rc.files_only(rc.files_by_pn(file_map), [], file_map, {}, "unlocked")
        self.assertEqual([(e["part_number"], e["team"], e["gaps"]) for e in extra], [("211102", "WALL", ["BOM row", "drawing"])])


class BoughtParts(unittest.TestCase):
    def test_register_named_part_with_a_test_is_done(self):
        _, bought = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16")], {},
                        tests=[("T06", "T06 rivnut torque with the 838001 bolt")])
        self.assertEqual((bought[0]["sku"], bought[0]["tests"], bought[0]["state"]), ("yes", ["T06"], "done"))

    def test_register_hold_wins_over_the_parts_list(self):
        _, bought = run([row("518001", "buy", "LINING - CASSETTE CLIP - ACME CL-20")], {})
        self.assertEqual((bought[0]["state"], bought[0]["tests"]), ("HOLD", ["T07"]))

    def test_register_leaves_it_to_the_list(self):
        _, bought = run([row("368102", "buy", "FRONT - DOOR STRIKE - HOLD", hold=True, team="FRONT")], {})
        self.assertEqual(bought[0]["state"], "HOLD")

    def test_hardware_without_a_register_row(self):
        _, bought = run([row("838099", "buy", "HARDWARE - NUT - M8 - DIN 934")], {})
        self.assertEqual(bought[0]["state"], "open: register row, test")

    def test_team_numbered_parts_need_no_register_row(self):
        _, bought = run([row("718001", "buy", "ELECTRICAL - 12 V SUPPLY - MW LPV-60-12", team="ELECTRICAL")], {})
        self.assertEqual((bought[0]["in_reg"], bought[0]["state"]), (None, "open: test"))


class Render(unittest.TestCase):
    def test_totals_count_each_number_once_and_name_the_screen(self):
        a = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16")], {}, tests=[("T06", "838001")])[1]
        b = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16", team="BASE")], {}, tests=[("T06", "838001")])[1]
        text = rc.render([], a + b, [], ["ELECTRICAL"], "this working tree", "locked", {}, rc.fai_plan(PLAN, BOM), "2026-11-01")
        self.assertIn("| BASE | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| WALL | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| **All, each number once** | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| ELECTRICAL | — | — | — | — | — | — |", text)
        self.assertIn("**locked**", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
