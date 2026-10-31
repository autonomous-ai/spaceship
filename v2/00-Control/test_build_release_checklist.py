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


def dxf_doc(*entities):
    """A small ASCII DXF: the layer table names CUT, BEND and MARK; then one entity per (type, layer)."""
    head = ["0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER"]
    for name in ("CUT", "BEND", "MARK"):
        head += ["0", "LAYER", "2", name, "70", "0"]
    head += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    body = []
    for typ, layer in entities:
        body += ["0", typ, "8", layer, "10", "0.0", "20", "0.0", "11", "100.0", "21", "0.0"]
    return "\n".join(head + body + ["0", "ENDSEC", "0", "EOF"]) + "\n"


def files(*names, folder="v2/01-CAD-Native/wall/"):
    return {folder + n: "working tree" for n in names}


def run(parts, file_map, screen="unlocked", register_text=REGISTER, tests=(), tab_cover=None):
    fai = rc.fai_plan(PLAN, BOM)
    register = BOM.parse_register(register_text, "test")
    return rc.check_parts(parts, register, rc.files_by_pn(file_map), list(file_map), fai, list(tests) + fai[1],
                          rc.register_products(register_text, BOM), screen, BOM, {}, {}, tab_cover or {})


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

    def test_the_joints_folders_belong_to_joints(self):
        file_map = files("831002_P01_HARDWARE-STOP-WASHER_STEP.step", folder="v2/03-Manufacturing/joints/")
        extra = rc.files_only(rc.files_by_pn(file_map), [], file_map, {}, "unlocked")
        self.assertEqual([(e["part_number"], e["team"]) for e in extra], [("831002", "JOINTS")])

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


class D89Drawings(unittest.TestCase):
    """D-89, read as the mechanical check reads it (tools/checks/c_drawings.py)."""
    DWG = "v2/02-Drawings/wall/211101_P01_WALL-PANEL-FRAME-SIDE-LOWER_DWG.pdf"
    TEXT = "UNITS: mm\nTABULATED DRAWING\nPART NO | SIDE\n211101 | LH\n211102 | RH\nRIVNUT 838003 IN EVERY H01\n210101"

    def test_a_tabulated_drawing_covers_its_family_and_kind(self):
        by_pn = {"211101": {"DWG": [self.DWG]}}
        self.assertEqual(rc.tabulated_cover(by_pn, lambda _p: self.TEXT), {"211102": "211101"})  # not 838003, not 210101
        self.assertEqual(rc.tabulated_cover(by_pn, lambda _p: self.TEXT.replace("TABULATED ", "")), {})

    def test_a_number_on_a_tabulated_drawing_counts_as_drawn(self):
        rh = row("211102", "make", "WALL - PANEL FRAME - RH", "aluminium 6063-T6 tube 20 x 40 x 1.2, mill finish")
        rh["cut_rows"] = True
        file_map = files("211102_P01_WALL-FRAME-RH_CAD.f3d", "211102_P01_WALL-FRAME-RH_STEP.step")
        fai = rc.fai_plan(PLAN, BOM)
        made, _ = rc.check_parts([rh], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {}, {},
                                 {"211102": "211101"})
        self.assertEqual(made[0]["dwg"], "on 211101, tabulated (D-89)")
        self.assertEqual(made[0]["state"], "done")

    CUT = "v2/03-Manufacturing/wall/510000_P01_LINING-CUT-LIST_SPEC.csv"
    FELT_FILES = files("511301_P01_LINING-FELT_CAD.f3d", "511301_P01_LINING-FELT_STEP.step")

    def felt(self, header="part_number,name,size_mm,material,tolerance_mm",
             line="511301,LINING - FELT,9 x 1442 x 1139.74,PET felt 9 mm,+0 / -2"):
        fai = rc.fai_plan(PLAN, BOM)
        felt = row("511301", "make", "LINING - FELT - SIDE LOWER - LH", "PET felt 9 mm Dark Gray")
        made, _ = rc.check_parts([felt], [], rc.files_by_pn(self.FELT_FILES), list(self.FELT_FILES), fai, fai[1], {}, "unlocked",
                                 BOM, {}, {self.CUT: header + "\n" + line + "\n"})
        return made[0]

    def test_a_felt_rectangle_on_a_full_cut_list_row_needs_no_drawing_or_dxf(self):
        line = self.felt()
        self.assertEqual((line["flat"], line["dwg"]), ("cut list", "cut list (D-89)"))
        self.assertEqual(line["gaps"], ["FAI"])  # this test plan has no felt characteristic

    def test_a_tolerance_may_sit_in_any_cell(self):
        line = self.felt("part_number,name,size_mm,material,note", "511301,LINING - FELT,9 x 1442 x 1139.74,PET felt,±2 on each side")
        self.assertEqual(line["dwg"], "cut list (D-89)")

    def test_no_tolerance_or_a_pocket_keeps_the_drawing(self):
        self.assertEqual(self.felt("part_number,name,size_mm,material", "511301,LINING - FELT,9 x 1442 x 1139.74,PET felt")["gaps"],
                         ["DXF or cut list", "drawing", "FAI"])
        self.assertIn("drawing", self.felt(line="511301,LINING - FELT - 60 X 60 POCKETS,9 x 1442 x 1139.74,PET felt,+0 / -2")["gaps"])

    def test_a_metal_part_never_skips_its_drawing_by_a_cut_list(self):
        fai = rc.fai_plan(PLAN, BOM)
        tray = row("511101", "make", "LINING - TRAY", "galvanised steel 0.5")
        file_map = files("511101_P01_TRAY_CAD.f3d", "511101_P01_TRAY_STEP.step", "511101_P01_TRAY_DXF.dxf")
        made, _ = rc.check_parts([tray], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {self.CUT: "part_number,size_mm,material,tolerance\n511101,1442 x 1139,steel,1\n"})
        self.assertEqual(made[0]["dwg"], "no")

    def test_what_counts_as_a_cut_list(self):
        self.assertTrue(rc.is_cut_list(self.CUT))
        self.assertTrue(rc.is_cut_list("v2/02-Drawings/ceiling/410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv"))
        self.assertFalse(rc.is_cut_list("v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY_BOM.csv"))
        self.assertFalse(rc.is_cut_list("v2/03-Manufacturing/wall/make_cut_files.py"))


class D89SoftGoods(unittest.TestCase):
    """D-89 (3): foam, gaskets, seals and tape: a DXF of the outline, or for a plain strip or rectangle a row with
    size, thickness, material, tolerance and number. Felt and fill: a row with size, material and tolerance."""
    FOAM = "BASE - FLOOR FOAM - F1"

    def foam(self, file_names, csv_text=None, name=FOAM):
        fai = rc.fai_plan(PLAN, BOM)
        part = row("111501", "make", name, "closed-cell PE foam 3 mm", team="BASE",
                   src="v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv")
        file_map = files(*file_names, folder="v2/03-Manufacturing/base/")
        lists = {"v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv": csv_text} if csv_text else {}
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {}, lists)
        return made[0]

    CADS = ("111501_P01_BASE-FLOOR-FOAM_CAD.f3d", "111501_P01_BASE-FLOOR-FOAM_STEP.step")

    def test_a_dxf_draws_a_foam_part_of_any_shape(self):
        line = self.foam(self.CADS + ("111501_P01_BASE-FLOOR-FOAM_DXF.dxf",))
        self.assertEqual((line["flat"], line["dwg"]), ("yes", "DXF (D-89)"))

    def test_a_plain_foam_rectangle_needs_its_thickness_on_the_row(self):
        head = "part_number,name,size_mm,material,tolerance_mm"
        no_t = self.foam(self.CADS, head + "\n111501,BASE - FLOOR FOAM - F1,1210 x 1455,PE foam,±2\n")
        self.assertEqual((no_t["flat"], no_t["dwg"]), ("no", "no"))
        with_t = self.foam(self.CADS, head + ",thickness_mm\n111501,BASE - FLOOR FOAM - F1,1210 x 1455,PE foam,±2,3\n")
        self.assertEqual((with_t["flat"], with_t["dwg"]), ("cut list", "cut list (D-89)"))
        three = self.foam(self.CADS, head + "\n111501,BASE - FLOOR FOAM - F1,1210 x 1455 x 3,PE foam,±2\n")
        self.assertEqual(three["dwg"], "cut list (D-89)")

    def test_the_name_decides_what_is_a_soft_good(self):
        self.assertEqual(self.foam(self.CADS + ("111501_P01_BASE-SEAL-MAT_DXF.dxf",), name="BASE - SEAL MAT - F1")["dwg"], "no")
        self.assertEqual(rc.soft_kind("FRONT - DROP SEAL - ATHMER"), "soft")
        self.assertEqual(rc.soft_kind("BASE - SEAL HOLDER - LH"), "")
        self.assertEqual(rc.soft_kind("WALL - CAVITY FILL - SIDE LOWER - LH"), "felt or fill")

    def test_a_felt_row_in_a_parts_list_serves_as_its_cut_list(self):
        fai = rc.fai_plan(PLAN, BOM)
        felt = row("511301", "make", "LINING - FELT - SIDE LOWER - LH", "PET felt 9 mm")
        file_map = files("511301_P01_LINING-FELT_CAD.f3d", "511301_P01_LINING-FELT_STEP.step")
        lists = {WALL: "part_number,name,size_mm,material,tolerance\n511301,LINING - FELT,9 x 1442 x 1139.74,PET felt,±2\n"}
        made, _ = rc.check_parts([felt], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {}, lists)
        self.assertEqual(made[0]["dwg"], "cut list (D-89)")

    def test_the_name_rule_matches_the_mechanical_check(self):
        path = rc.ROOT / "tools/checks/common.py"
        if not path.exists():
            self.skipTest("no mechanical check in this tree")
        spec = importlib.util.spec_from_file_location("checks_common", path)
        common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(common)
        names = ["LINING - FELT - SIDE LOWER - LH", "LINING - FILL - CEILING - BAY A", "WALL - CAVITY FILL - SIDE LOWER - LH",
                 "BASE - SEAL MAT - F1", "BASE - FLOOR FOAM - F1", "FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112",
                 "BASE - SEAL HOLDER - LH", "SEALS - JOINT GASKET - 8 X 3.97", "POD - FIXING TAPE", "WALL - PANEL FRAME - SIDE LOWER - LH"]
        for n in names:
            self.assertEqual(rc.head_noun(n), common.head_noun(n), n)
            self.assertEqual(bool(rc.soft_kind(n)), common.is_soft(n), n)
            self.assertEqual(rc.soft_kind(n) == "felt or fill", common.is_soft(n, kinds=("FELT", "FILL")), n)


class D89FlatSheetParts(unittest.TestCase):
    """D-89 (4): a flat part cut from sheet goes without a drawing on its own DXF and a full parts-list row."""
    LIST = "v2/03-Manufacturing/front/360000_P01_FRONT_BOM.csv"
    HEAD = "part_number,name,material,thickness_mm,finish,process,tolerance,note"
    GOOD = "361101,FRONT - COVER PLATE,aluminium 5754-H22,2,black anodised AA20,laser cut,ISO 2768-m,"

    def plate(self, line=GOOD, head=HEAD, dxf=True, make_buy="make", pn="361101", dxf_text=None):
        dxf_text = dxf_text or dxf_doc(("LWPOLYLINE", "CUT"), ("CIRCLE", "CUT"), ("TEXT", "MARK"))
        fai = rc.fai_plan(PLAN, BOM)
        part = row(pn, make_buy, "FRONT - COVER PLATE", "aluminium 5754-H22", team="FRONT", src=self.LIST)
        part["finish"] = "black anodised AA20"
        names = [f"{pn}_P01_FRONT-COVER-PLATE_CAD.f3d", f"{pn}_P01_FRONT-COVER-PLATE_STEP.step"]
        names += [f"{pn}_P01_FRONT-COVER-PLATE_DXF.dxf"] if dxf else []
        file_map = files(*names, folder="v2/03-Manufacturing/front/")
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {self.LIST: head + "\n" + line + "\n"}, {}, lambda _pn: [dxf_text] if dxf else [])
        return made[0]

    def test_a_laser_cut_plate_with_its_dxf_and_a_full_row_is_drawn(self):
        line = self.plate()
        self.assertEqual((line["flat"], line["dwg"]), ("yes", "DXF and row (D-89)"))
        self.assertNotIn("drawing", line["gaps"])

    def test_each_missing_item_keeps_the_drawing(self):
        self.assertEqual(self.plate(dxf=False)["dwg"], "no")
        self.assertEqual(self.plate(self.GOOD.replace("ISO 2768-m", "±0.2"))["dwg"], "no")
        self.assertEqual(self.plate(self.GOOD.replace("black anodised AA20", ""))["dwg"], "no")
        self.assertEqual(self.plate(self.GOOD.replace(",2,", ",,"))["dwg"], "no")
        self.assertEqual(self.plate(self.GOOD.replace("laser cut", "punch"))["dwg"], "no")

    def test_bent_machined_or_bonded_parts_keep_the_drawing(self):
        for process in ("laser cut, brake bend", "laser cut, tap M6", "CNC router: outline and the seam half-lap",
                        "router cut, then bonded to the frame", "waterjet, countersink 4 holes"):
            self.assertEqual(self.plate(self.GOOD.replace("laser cut", '"%s"' % process))["dwg"], "no", process)

    def test_a_mill_finish_is_not_milling(self):
        line = self.plate(self.GOOD.replace("black anodised AA20", "mill finish"))
        self.assertEqual(line["dwg"], "DXF and row (D-89)")

    def test_thickness_may_sit_in_the_material(self):
        head = "part_number,name,material,finish,process,tolerance"
        line = "361101,FRONT - COVER PLATE,aluminium 5754-H22 2 mm,black anodised AA20,waterjet,ISO 2768-m"
        self.assertEqual(self.plate(line, head)["dwg"], "DXF and row (D-89)")

    def test_an_assembly_always_keeps_its_drawing(self):
        line = self.GOOD.replace("361101", "360101")
        self.assertEqual(self.plate(line, make_buy="assembly", pn="360101")["dwg"], "no")


class D89Layers(unittest.TestCase):
    """D-89 (4) can't be fooled by a process word: its DXF may draw only on the CUT and MARK layers; a line on any
    other layer (BEND, a pocket, an engraving, a half-lap) keeps the drawing (PM ruling 2026-11-01)."""

    def test_reading_the_layers(self):
        self.assertEqual(rc.dxf_other_layers(dxf_doc(("LINE", "CUT"), ("TEXT", "MARK"))), set())  # BEND only in the layer table
        self.assertEqual(rc.dxf_other_layers(dxf_doc(("LINE", "CUT"), ("LINE", "BEND"))), {"BEND"})
        self.assertEqual(rc.dxf_other_layers(dxf_doc(("LWPOLYLINE", "cut"), ("LINE", "bend"), ("LWPOLYLINE", "POCKET-HALF-DEPTH"))),
                         {"BEND", "POCKET-HALF-DEPTH"})
        self.assertIsNone(rc.dxf_other_layers(""))
        self.assertIsNone(rc.dxf_other_layers("AutoCAD Binary DXF\r\n\x1a\x00"))

    @staticmethod
    def blocks(*defs):
        """A BLOCKS section: the *Model_Space header, then (name, [(type, layer, inserted block)]) per block."""
        out = "0\nSECTION\n2\nBLOCKS\n0\nBLOCK\n8\n0\n2\n*Model_Space\n0\nENDBLK\n8\n0\n"
        for name, ents in defs:
            out += f"0\nBLOCK\n8\n0\n2\n{name}\n"
            for typ, layer, ref in ents:
                out += f"0\n{typ}\n8\n{layer}\n" + (f"2\n{ref}\n" if ref else "")
            out += "0\nENDBLK\n8\n0\n"
        return out + "0\nENDSEC\n"

    @staticmethod
    def placing(*inserts):
        """A DXF whose ENTITIES hold a CUT line and one INSERT per (block, layer)."""
        tail = "".join(f"0\nINSERT\n8\n{layer}\n2\n{name}\n" for name, layer in inserts)
        return dxf_doc(("LINE", "CUT")).replace("0\nENDSEC\n0\nEOF", tail + "0\nENDSEC\n0\nEOF")

    def test_a_stored_block_counts_only_where_it_is_placed(self):
        arrows = self.blocks(("_ARCHTICK", [("LWPOLYLINE", "0", "")]), ("_CLOSEDFILLED", [("SOLID", "0", "")]))
        self.assertEqual(rc.dxf_other_layers(arrows + dxf_doc(("LINE", "CUT"))), set())  # written, never placed
        tab = self.blocks(("TAB", [("LINE", "BEND", "")]))
        self.assertEqual(rc.dxf_other_layers(tab + dxf_doc(("LINE", "CUT"))), set())
        self.assertEqual(rc.dxf_other_layers(tab + self.placing(("TAB", "CUT"))), {"BEND"})

    def test_layer_0_shapes_take_the_insert_layer_and_nesting_counts(self):
        plain = self.blocks(("HOLE", [("CIRCLE", "0", "")]))
        self.assertEqual(rc.dxf_other_layers(plain + self.placing(("HOLE", "CUT"))), set())
        self.assertEqual(rc.dxf_other_layers(plain + self.placing(("HOLE", "ENGRAVE"))), {"ENGRAVE"})
        nested = self.blocks(("TAB", [("LINE", "BEND", "")]), ("OUTER", [("INSERT", "0", "TAB"), ("LINE", "0", "")]))
        self.assertEqual(rc.dxf_other_layers(nested + self.placing(("OUTER", "CUT"))), {"BEND"})

    def test_polyline_records_are_not_lines(self):
        polyline = dxf_doc(("POLYLINE", "CUT")).replace("0\nENDSEC\n0\nEOF", "0\nVERTEX\n8\n0\n0\nSEQEND\n8\n0\n0\nENDSEC\n0\nEOF")
        self.assertEqual(rc.dxf_other_layers(polyline), set())

    def test_both_tools_use_the_one_shared_reader(self):
        """The checklist and the mechanical check import tools/checks/dxf_layers.py, so they can't drift."""
        checks = rc.ROOT / "tools/checks"
        self.assertEqual(Path(rc.DXF_LAYERS.__file__).resolve(), (checks / "dxf_layers.py").resolve())
        sys.path.insert(0, str(checks))
        try:
            import c_drawings
        finally:
            sys.path.remove(str(checks))
        samples = [dxf_doc(("LINE", "CUT"), ("TEXT", "MARK")), dxf_doc(("LINE", "CUT"), ("LINE", "BEND")),
                   self.blocks(("_ARCHTICK", [("LWPOLYLINE", "0", "")])) + dxf_doc(("LINE", "CUT")),
                   self.blocks(("TAB", [("LINE", "BEND", "")])) + self.placing(("TAB", "CUT")), ""]
        for i, text in enumerate(samples):
            self.assertEqual(c_drawings.dxf_other_layers(text), rc.dxf_other_layers(text), i)

    def run_part(self, dxf_text, process="laser", pn="511101", name="LINING - TRAY - SIDE LOWER - LH"):
        fai = rc.fai_plan(PLAN, BOM)
        lst = "v2/03-Manufacturing/wall/510000_P01_LINING_BOM.csv"
        part = row(pn, "make", name, "galvanised steel sheet 0.5 mm", src=lst)
        part["finish"] = "hot-dip zinc"
        file_map = files(f"{pn}_P01_PART_CAD.f3d", f"{pn}_P01_PART_STEP.step", f"{pn}_P01_PART_DXF.dxf", folder="v2/03-Manufacturing/wall/")
        csv_text = ("part_number,name,material,thickness_mm,finish,process,tolerance\n"
                    f"{pn},{name},galvanised steel DX51D+Z,0.5,hot-dip zinc,{process},ISO 2768-m\n")
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {lst: csv_text}, {}, lambda _pn: [dxf_text])
        return made[0]

    def test_a_folded_tray_whose_row_says_only_laser_keeps_its_drawing(self):
        folded = self.run_part(dxf_doc(("LINE", "CUT"), ("SPLINE", "CUT"), ("LINE", "BEND"), ("LINE", "BEND"), ("LINE", "MARK")))
        self.assertEqual(folded["dwg"], "no: its DXF draws on BEND; only CUT and MARK pass (D-89)")
        self.assertIn("drawing", folded["gaps"])
        self.assertEqual(self.run_part(dxf_doc(("LINE", "CUT"), ("LINE", "MARK")))["dwg"], "DXF and row (D-89)")

    def test_a_routed_half_lap_or_an_engraving_keeps_the_drawing(self):
        floor = self.run_part(dxf_doc(("LWPOLYLINE", "CUT"), ("LWPOLYLINE", "POCKET-HALF-DEPTH"), ("TEXT", "MARK")),
                              process="CNC router", pn="111401", name="BASE - FLOOR PANEL - F1")
        self.assertEqual(floor["dwg"], "no: its DXF draws on POCKET-HALF-DEPTH; only CUT and MARK pass (D-89)")
        engraved = self.run_part(dxf_doc(("LINE", "CUT"), ("TEXT", "ENGRAVE")))
        self.assertEqual(engraved["dwg"], "no: its DXF draws on ENGRAVE; only CUT and MARK pass (D-89)")

    def test_an_unreadable_dxf_keeps_the_drawing(self):
        self.assertEqual(self.run_part("")["dwg"], "no: its DXF can't be read (D-89)")


class Rulings93To99(unittest.TestCase):
    """D-93: 710000 is drawn by its wiring diagram. D-95: the corner keys count under JOINTS. D-99: D-89 part (4) is
    for flat metal sheet."""

    def made(self, part, file_map, lists=None, dxf_text=None):
        fai = rc.fai_plan(PLAN, BOM)
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 lists or {}, {}, (lambda _pn: [dxf_text]) if dxf_text else None)
        return made[0]

    def test_the_wiring_diagram_draws_710000(self):
        unit = row("710000", "assembly", "ELECTRICAL", "", team="ELECTRICAL", src="v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL_BOM.csv")
        file_map = files("710000_P01_ELECTRICAL_CAD.f3d", "710000_P01_ELECTRICAL_STEP.step", folder="v2/01-CAD-Native/electrical/")
        file_map.update(files("710000_P01_ELECTRICAL-WIRING-DIAGRAM_DWG.pdf", folder="v2/02-Drawings/electrical/"))
        line = self.made(unit, file_map)
        self.assertEqual(line["dwg"], "yes: its wiring diagram, routes and joints on sheet 3 (D-93)")
        self.assertNotIn("drawing", line["gaps"])

    def test_the_corner_keys_count_under_joints(self):
        key = row("111211", "make", "BASE - CORNER KEY - BACK - COMMON", "aluminium 6061-T6, mill finish", team="BASE",
                  src="v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv")
        self.assertEqual(self.made(key, {})["team"], "JOINTS")

    def test_a_part_modelled_in_a_joints_folder_counts_under_joints(self):
        washer = row("831002", "make", "HARDWARE - STOP WASHER - D10.5 X D20 X 1.5 - AL", "aluminium sheet 1.5 mm, mill finish")
        file_map = files("831002_P01_HARDWARE-STOP-WASHER_STEP.step", folder="v2/03-Manufacturing/joints/")
        self.assertEqual(self.made(washer, file_map)["team"], "JOINTS")
        self.assertEqual(self.made(washer, {})["team"], "WALL")

    def test_flat_sheet_part_four_is_for_metal_only(self):
        lst = "v2/03-Manufacturing/front/360000_P01_FRONT_BOM.csv"
        glass = row("361001", "make", "FRONT - DOOR LEAF - 4+4 LAMINATED", "4+4 laminated toughened glass", team="FRONT", src=lst)
        file_map = files("361001_P01_DOOR-LEAF_CAD.f3d", "361001_P01_DOOR-LEAF_STEP.step", "361001_P01_DOOR-LEAF_DXF.dxf",
                         folder="v2/03-Manufacturing/front/")
        csv_text = ("part_number,name,material,thickness_mm,finish,process,tolerance\n"
                    "361001,FRONT - DOOR LEAF,4+4 laminated toughened glass,8.76,clear,waterjet,ISO 2768-m\n")
        line = self.made(glass, file_map, {lst: csv_text}, dxf_doc(("LWPOLYLINE", "CUT")))
        self.assertEqual(line["dwg"], "no")
        self.assertEqual(rc.flat_lacks(rc.cut_rows({lst: csv_text})["361001"]), ["metal or ACP sheet (D-99, D-100)"])

    def test_a_flat_acp_skin_counts_and_a_folded_one_keeps_its_drawing(self):
        lst = "v2/03-Manufacturing/ceiling/410000_P01_CEILING_BOM.csv"
        skin = row("411301", "make", "CEILING - SKIN - COMMON", "ACP 3 mm EV3038", team="CEILING", src=lst)
        skin["finish"] = "PVDF EV3038"
        file_map = files("411301_P01_CEILING-SKIN_CAD.f3d", "411301_P01_CEILING-SKIN_STEP.step", "411301_P01_CEILING-SKIN_DXF.dxf",
                         folder="v2/03-Manufacturing/ceiling/")
        csv_text = ("part_number,name,material,finish,process,tolerance\n"
                    "411301,CEILING - SKIN - COMMON,ACP 3 mm EV3038,PVDF EV3038,CNC routed,ISO 2768-m\n")
        flat = self.made(skin, file_map, {lst: csv_text}, dxf_doc(("LWPOLYLINE", "CUT"), ("TEXT", "MARK")))
        self.assertEqual(flat["dwg"], "DXF and row (D-89)")
        folded = self.made(skin, file_map, {lst: csv_text}, dxf_doc(("LWPOLYLINE", "CUT"), ("LINE", "V-GROOVE"), ("LINE", "BEND")))
        self.assertEqual(folded["dwg"], "no: its DXF draws on BEND, V-GROOVE; only CUT and MARK pass (D-89)")


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
