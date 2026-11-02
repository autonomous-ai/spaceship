#!/usr/bin/env python3
"""Tests for build_release_checklist.py (doc code V2-CTL-011): one planted case per rule.

Run: python3 v2/00-Control/test_build_release_checklist.py
"""
import csv
import importlib.util
import io
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

    # D-131's steel members, word for word: CEILING's 412101 (#348 at 3d7c6ae) and WALL's 212101 (#343 at 5afde8e)
    CEILING_TUBE = ("Galvanized steel S280GD+Z or SGC400 (yield 280 MPa or more), Z100",
                    "tube cut to length (mitred ends where it meets the corners, cut back for the 2.0 mitre plate), welded into "
                    "the frame; holes CNC or jig drilled after welding (+/-0.2 from the spigot hole, R-J6)")
    WALL_TUBE = ("steel box tube 20 x 40 x 1.2, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, "
                 "zinc Z100 (J-FRAME-01, D-131)")

    def test_a_galvanized_steel_tube_is_read_as_a_tube_not_sheet(self):
        # the CEILING Drawings Engineer's catch on #362: 'galvanized' alone reads as sheet, so D-131's steel tubes wanted
        # a DXF even with their cut list rows; the tube words now come first (and FRONT's 'GLASS EDGE' tubes too)
        ceiling = row("412101", "make", "CEILING - FRAME SIDE MEMBER - COMMON", self.CEILING_TUBE[0], team="CEILING")
        ceiling["process"] = self.CEILING_TUBE[1]
        wall = row("212101", "make", "WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH", self.WALL_TUBE)
        glass_edge = row("352306", "make", "FRONT - DECOR FRAME DR - FRONT RING GLASS EDGE",
                         "aluminium EN AW-6063-T6 tube 20 x 20 x 1.0", team="FRONT")
        for r in (ceiling, wall, glass_edge):
            r["cut_rows"] = True
        made, _ = run([ceiling, wall, glass_edge], {})
        self.assertEqual([m["flat"] for m in made], ["yes", "yes", "yes"])
        # with no cut list row, a steel tube still wants one
        bare = dict(ceiling)
        del bare["cut_rows"]
        made, _ = run([bare], {})
        self.assertEqual(made[0]["flat"], "no")
        self.assertIn("DXF or cut list", made[0]["gaps"])

    def test_galvanized_sheet_with_no_tube_words_still_needs_its_dxf(self):
        tray = row("513101", "make", "LINING - TRAY - CEILING", "galvanised steel DX51D+Z, 0.5 sheet", team="CEILING")
        tray["cut_rows"] = True     # a cut list row doesn't stand in for a sheet part's DXF
        made, _ = run([tray], {})
        self.assertEqual(made[0]["flat"], "no")

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
        self.assertEqual([(e["part_number"], e["team"], e["gaps"]) for e in extra], [("211102", "WALL", ["BOM row", "drawing", "FAI"])])
        chars = rc.fai_plan(PLAN, BOM)[0]  # K-J01 covers 2111xx
        extra = rc.files_only(rc.files_by_pn(file_map), [], file_map, {}, "unlocked", chars)
        self.assertEqual((extra[0]["fai"], extra[0]["gaps"]), (["K-J01"], ["BOM row", "drawing"]))

    def test_a_tabulated_drawing_covers_a_part_with_no_bom_row(self):
        # 111212 to 111214 have STEP files and no BOM row; 111211's tabulated sheet lists them (D-89, #215)
        file_map = files("211102_P01_WALL-PANEL-FRAME-RH_CAD.f3d", "211102_P01_WALL-PANEL-FRAME-RH_STEP.step")
        chars = rc.fai_plan(PLAN, BOM)[0]
        extra = rc.files_only(rc.files_by_pn(file_map), [], file_map, {}, "unlocked", chars, {"211102": "211101"})
        self.assertEqual((extra[0]["dwg"], extra[0]["gaps"]), ("on 211101, tabulated (D-89)", ["BOM row"]))
        self.assertIn("| on 211101, tabulated (D-89) |", rc.render(extra, [], [], [], "main", "unlocked", {}, ([], [], []),
                                                                   "2026-11-01"))

    def test_the_real_run_passes_the_tabulated_cover_to_those_lines(self):
        # main() hands the same cover to the lines with no BOM row; a run that stops passing it fails here
        import inspect
        import tempfile as _tempfile
        seen, cover = {}, {"211102": "211101"}

        class Stop(Exception):
            pass

        def spy(*args, **kw):
            seen["tab_cover"] = inspect.signature(real).bind(*args, **kw).arguments.get("tab_cover")
            raise Stop

        real, old = rc.files_only, (rc.tabulated_cover, rc.d125_strips)
        rc.files_only, rc.tabulated_cover, rc.d125_strips = spy, (lambda by_pn, text_of: cover), (lambda root=None: {})
        try:
            with _tempfile.TemporaryDirectory() as d, self.assertRaises(Stop):
                rc.main(["--screen", "unlocked", "--out", str(Path(d, "release-checklist.md"))])
        finally:
            rc.files_only = real
            rc.tabulated_cover, rc.d125_strips = old
        self.assertIs(seen.get("tab_cover"), cover)


FRONT_LISTS = "v2/03-Manufacturing/front/"
BLOCK_FILES = {"v2/01-CAD-Native/front/350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_CAD.f3d": "working tree",
               FRONT_LISTS + "350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_STEP.step": "working tree",
               "v2/01-CAD-Native/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_CAD.f3d": "working tree",
               FRONT_LISTS + "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_STEP.step": "working tree"}


class D120Members(unittest.TestCase):
    """FRONT's #320 rows: a frame's members are rows in the frame's own list (or a cut list's member_part); the
    frame has no files of its own, its block's CAD and STEP hold it, and the members are bodies in that STEP."""

    def lists(self):
        block = FRONT_LISTS + "350001_P01_FRONT-DECOR-BLOCK-ASSY-DL_BOM.csv"
        frame = FRONT_LISTS + "351104_P01_FRONT-DECOR-FRAME-DL_BOM.csv"
        return [row("350001", "assembly", "FRONT - DECOR BLOCK ASSY - DL", team="FRONT", src=block),
                row("351104", "make", "FRONT - DECOR FRAME - DL", "weldment assembly: welded frame, 26 tubes as 16 parts", team="FRONT", src=block),
                row("351104", "assembly", "FRONT - DECOR FRAME - DL", "weldment assembly", team="FRONT", src=frame),
                row("352101", "make", "FRONT - DECOR FRAME DL - BACK RING BOTTOM", "aluminium EN AW-6063-T6 tube 20 x 20 x 1.0", team="FRONT", src=frame)]

    def line(self, made, pn):
        return next(m for m in made if m["part_number"] == pn)

    def test_a_member_in_its_frames_list_takes_the_frames_cad_and_step(self):
        made, _ = run(self.lists(), dict(BLOCK_FILES))
        frame, member = self.line(made, "351104"), self.line(made, "352101")
        self.assertTrue(frame["cad"] and frame["step"])            # the frame is held by its block's files
        self.assertTrue(member["cad"] and member["step"], member["gaps"])
        self.assertNotIn("CAD", member["gaps"])
        self.assertNotIn("STEP", member["gaps"])

    def test_without_its_frames_files_a_member_still_lacks_them(self):
        made, _ = run(self.lists(), {})
        member = self.line(made, "352101")
        self.assertFalse(member["cad"] or member["step"])
        self.assertIn("CAD", member["gaps"])

    def test_a_cut_lists_member_part_takes_its_frames_files(self):
        block = FRONT_LISTS + "350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv"
        other = FRONT_LISTS + "359999_P01_FRONT-LOOSE-TUBES_BOM.csv"
        parts = [row("350003", "assembly", "FRONT - DECOR BLOCK ASSY - DR", team="FRONT", src=block),
                 row("351306", "make", "FRONT - DECOR FRAME - DR", "weldment assembly", team="FRONT", src=block),
                 row("352301", "make", "FRONT - DECOR FRAME DR - FRONT RING BOTTOM", "aluminium EN AW-6063-T6 tube 20 x 20 x 1.0", team="FRONT", src=other)]
        cut = {FRONT_LISTS + "351306_P01_FRONT-DECOR-FRAME-DR-TUBE-CUT-LIST.csv":
               "frame,member,member_part,name,section,length_mm,qty,ends,status\n"
               "351306,F01,352301,FRONT RING BOTTOM,6063-T6 aluminium tube 20 x 20 x 1.0,100.9,1,mitred,calculation\n"}
        fai = rc.fai_plan(PLAN, BOM)
        register = BOM.parse_register(REGISTER, "test")
        made, _ = rc.check_parts(parts, register, rc.files_by_pn(BLOCK_FILES), list(BLOCK_FILES), fai, fai[1],
                                 rc.register_products(REGISTER, BOM), "unlocked", BOM, {}, cut, {})
        member = self.line(made, "352301")
        self.assertTrue(member["cad"] and member["step"], member["gaps"])

    def test_every_frame_member_has_an_fai_line_in_the_real_plan(self):
        chars, _, _ = rc.fai_plan((rc.ROOT / rc.FAI).read_text(encoding="utf-8"), BOM)
        for pn in ("352101", "352201", "352322", "212101", "212701", "412001", "412103", "412201"):
            ids = [k for k, pats in chars if any(p.fullmatch(pn) for p in pats)]
            self.assertIn("K-J18", ids, pn)


class MakerDigits(unittest.TestCase):
    ELEC = "v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv"

    def cable(self, **kw):
        r = row("718027", "buy", "ELECTRICAL - CABLE - 4 X 24 AWG SCREENED - BELDEN 9534", team="ELECTRICAL", src=self.ELEC)
        r.update(kw)
        return r

    def test_an_all_digit_maker_number_counts_when_the_row_names_its_maker(self):
        _, bought = run([self.cable(maker="Belden", sku="9534 060100: 4 x 24 AWG stranded, overall foil and drain")], {})
        self.assertEqual(bought[0]["sku"], "yes")
        self.assertNotIn("maker and SKU", bought[0]["state"])

    def test_digits_alone_without_a_maker_still_lack_a_maker(self):
        _, bought = run([self.cable()], {})
        self.assertEqual(bought[0]["sku"], "no")

    def test_the_maker_and_sku_cells_come_from_the_parts_list_itself(self):
        text = ("part_number,name,kind,maker,sku\n"
                "718027,ELECTRICAL - CABLE - 4 X 24 AWG SCREENED - BELDEN 9534,PI,Belden,9534 060100\n")
        parts = rc.with_maker_cells([self.cable()], {self.ELEC: (text, "working tree")})
        self.assertEqual((parts[0]["maker"], parts[0]["sku"]), ("Belden", "9534 060100"))


# CEILING's tube cut list as the CEILING Engineer's #348 has it (15e8a4e), and WALL's as #343 has it (4efa807), word
# for word: their member rows state the end angles in 'deg', for both ends at once, and as square ends
CEILING_CUT = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv"
CEILING_ROWS = """frame,half,member,member_part,name,section,length_mm,qty,ends,holes,status
411101,C1,SIDE,412101,CEILING - FRAME SIDE MEMBER - COMMON,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1491.35,1,"front end mitred 45 deg, back end mitred 63.43 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",side bolt clearance x 4; side bolt access x 4,calculation (from the parameters)
411101,C1,SEAM,412102,CEILING - FRAME SEAM MEMBER - C1,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1491.35,1,"front end mitred 45 deg, back end mitred 63.43 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct","seam pin clearance x 4; 1 x 45 lead-in on the closing face's lower edge, full length",calculation (from the parameters)
411101,C1,FRONT,412103,CEILING - FRAME FRONT MEMBER - C1,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1196.16,1,"both ends mitred 45 deg; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",soffit hanger front x 1,calculation (from the parameters)
411101,C1,BACK,412104,CEILING - FRAME BACK MEMBER 40 X 40 - C1,"galvanized steel 40 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1196.75,1,"both ends mitred 26.57 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",back rivnut x 4; back spigot round x 1; back spigot slot 8.5 x 14 x 1,calculation (from the parameters)
411101,C1,X1,412105,CEILING - FRAME CROSS MEMBER 1 - COMMON,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",soffit hanger x1 x 1; soffit lock x 2,calculation (from the parameters)
411101,C1,X2,412001,CEILING - FRAME CROSS MEMBER - PLAIN - COMMON,"galvanized steel 20 x 40 x 0.8 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",none,calculation (from the parameters)
411101,C1,X3,412001,CEILING - FRAME CROSS MEMBER - PLAIN - COMMON,"galvanized steel 20 x 40 x 0.8 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",none,calculation (from the parameters)
411102,C2,SIDE,412101,CEILING - FRAME SIDE MEMBER - COMMON,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1491.35,1,"front end mitred 45 deg, back end mitred 63.43 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",side bolt clearance x 4; side bolt access x 4,calculation (from the parameters)
411102,C2,SEAM,412202,CEILING - FRAME SEAM MEMBER - C2,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1491.35,1,"front end mitred 45 deg, back end mitred 63.43 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct","seam pin rivnut x 4; seam pin access x 4; 1 x 45 lead-in on the closing face's lower edge, full length",calculation (from the parameters)
411102,C2,FRONT,412203,CEILING - FRAME FRONT MEMBER - C2,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1196.16,1,"both ends mitred 45 deg; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",soffit hanger front x 1,calculation (from the parameters)
411102,C2,BACK,412204,CEILING - FRAME BACK MEMBER 40 X 40 - C2,"galvanized steel 40 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1196.75,1,"both ends mitred 26.57 deg off square; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",back rivnut x 4; back spigot round x 1; back spigot slot 8.5 x 14 x 1,calculation (from the parameters)
411102,C2,X1,412105,CEILING - FRAME CROSS MEMBER 1 - COMMON,"galvanized steel 20 x 40 x 1.0 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",soffit hanger x1 x 1; soffit lock x 2,calculation (from the parameters)
411102,C2,X2,412001,CEILING - FRAME CROSS MEMBER - PLAIN - COMMON,"galvanized steel 20 x 40 x 0.8 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",none,calculation (from the parameters)
411102,C2,X3,412001,CEILING - FRAME CROSS MEMBER - PLAIN - COMMON,"galvanized steel 20 x 40 x 0.8 (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)",1158.99,1,"square cut; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct",none,calculation (from the parameters)
"""
WALL_CUT = "v2/03-Manufacturing/wall/210000_P01_WALL-TUBE-CUT-LIST_BOM.csv"
WALL_ROWS = """frame,position,member,member_part,name,section,length_mm,qty,ends,holes,status
211101,L1,RAIL BOTTOM,212101,WALL - FRAME RAIL BOTTOM - SIDE LOWER - LH,"steel box tube 20 x 40 x 1.2, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)",1483.09,1,"front end mitred 45.00° and back end 63.43° off square, in the frame's plane, long points on its bottom face (the frame's outer edge); cut back for the 2 mm mitre plate (D-117, D-131)","none of its own: every joint hole is made after welding, in the frame (J-FRAME-01; the frame's drawing)",calculation (CAD; number from the master BOM's allocation (D-120); steel D-131)
211101,L1,RAIL TOP,212102,WALL - FRAME RAIL TOP - SIDE LOWER - LH,"steel box tube 20 x 40 x 1.2, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)",1483.09,1,"front end mitred 45.00° and back end 63.43° off square, in the frame's plane, long points on its top face (the frame's outer edge); cut back for the 2 mm mitre plate (D-117, D-131)","none of its own: every joint hole is made after welding, in the frame (J-FRAME-01; the frame's drawing)",calculation (CAD; number from the master BOM's allocation (D-120); steel D-131)
211101,L1,STILE FRONT,212103,WALL - FRAME STILE FRONT - SIDE LOWER - LH,"steel box tube 20 x 40 x 1.2, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)",1139.92,1,"bottom and top ends both mitred 45.00° off square, in the frame's plane, long points on its front face (the frame's outer edge); cut back for the 2 mm mitre plate (D-117, D-131)","none of its own: every joint hole is made after welding, in the frame (J-FRAME-01; the frame's drawing)",calculation (CAD; number from the master BOM's allocation (D-120); steel D-131)
211101,L1,STILE BACK,212104,WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH,"steel box tube 40 x 40 x 1, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)",1140.5,1,"bottom and top ends both mitred 26.57° off square, in the frame's plane, long points on its back face (the frame's outer edge); cut back for the 2 mm mitre plate (D-117, D-131)","none of its own: every joint hole is made after welding, in the frame (J-FRAME-01; the frame's drawing)",calculation (CAD; number from the master BOM's allocation (D-120); steel D-131)
211101,L1,STILE MID,212105,WALL - FRAME STILE MID - SIDE LOWER - LH,"steel box tube 20 x 40 x 0.8, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)",1102.74,5,"square ends (fits between the rails, welded T joints, D-131)","none of its own: every joint hole is made after welding, in the frame (J-FRAME-01; the frame's drawing)",calculation (CAD; number from the master BOM's allocation (D-120); steel D-131)
"""
# every way of writing the ends the tests read (C05's own cases, #357, and the teams' rows): the first nine state
# both end angles, the last four don't
END_WORDINGS = ("front end mitred 45 deg, back end mitred 63.43 deg off square", "45 degrees and 30 Degrees",
                "both ends mitred 45 deg; welded into the frame (D-131, J-FRAME-01)",
                "both ends mitred 26.57 deg off square; welded into the frame", "mitred 30° at both ends",
                "bottom and top ends both mitred 45.00° off square, in the frame's plane",
                "square ends (fits between the rails, welded T joints, D-131)", "square cut",
                "41.01° and 45° from square",
                "front end mitred 45 deg; back end to suit", "both ends mitred to suit; 45 deg plate",
                "mitred to its neighbours (angles on the frame drawing)", "ends both cut to suit")


class D176GA(unittest.TestCase):
    """D-176: the GA (100000) only warns in the Checker's audit and is redrawn at checkpoints, so the release checklist
    shows whether it is current: its recorded sources still have the hashes it was drawn from."""

    def ga(self, tmp, creator="drawgen", sources=None):
        import json
        fitz = __import__("fitz")
        folder = Path(tmp) / rc.GA_DIR
        folder.mkdir(parents=True, exist_ok=True)
        doc = fitz.open()
        doc.new_page()
        doc.set_metadata({"creator": creator})
        txt = json.dumps({"sources": sources or []}, sort_keys=True, separators=(",", ":"))
        doc.xref_set_key(doc.pdf_catalog(), "DrawgenData", "(%s)" % txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))
        path = folder / "100000_P04_POD-SPACESHIP_DWG.pdf"
        doc.save(str(path))
        return path

    def test_current_changed_and_gone(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            step = Path(tmp) / "v2/03-Manufacturing/base/110000_P01_BASE_STEP.step"
            step.parent.mkdir(parents=True)
            step.write_text("ISO-10303-21; base", encoding="utf-8")
            src = [{"path": "v2/03-Manufacturing/base/110000_P01_BASE_STEP.step", "role": "STEP",
                    "sha256_12": rc.sha12(step)}]
            self.ga(tmp, sources=src)
            path, why = rc.ga_current(tmp)
            self.assertEqual((path, why), (rc.GA_DIR + "/100000_P04_POD-SPACESHIP_DWG.pdf", []))
            step.write_text("ISO-10303-21; base, moved", encoding="utf-8")
            self.assertEqual(rc.ga_current(tmp)[1], ["v2/03-Manufacturing/base/110000_P01_BASE_STEP.step changed"])
            step.unlink()
            self.assertEqual(rc.ga_current(tmp)[1], ["v2/03-Manufacturing/base/110000_P01_BASE_STEP.step is gone"])

    def test_a_sheet_the_generator_did_not_make_is_not_the_ga(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.ga(tmp, creator="Autodesk Fusion")
            self.assertEqual(rc.ga_current(tmp), (None, []))

    def test_an_out_of_date_ga_keeps_100000_open(self):
        fai = rc.fai_plan(PLAN, BOM)
        pod = row("100000", "assembly", "POD", team="CONTROL")
        def line(ga):
            made, _ = rc.check_parts([pod], BOM.parse_register(REGISTER, "test"), rc.files_by_pn({}), [], fai, fai[1],
                                     rc.register_products(REGISTER, BOM), "unlocked", BOM, {}, {}, {}, ga=ga)
            return made[0]
        stale = line(("v2/02-Drawings/00-General-Assembly/100000_P04_POD_DWG.pdf", ["v2/04-BOM/x.csv changed"]))
        self.assertIn("GA current (D-176)", stale["gaps"])
        self.assertNotIn("GA current (D-176)", line(("v2/02-Drawings/00-General-Assembly/100000_P04_POD_DWG.pdf", []))["gaps"])
        self.assertIn("out of date", rc.ga_line(("a.pdf", ["v2/04-BOM/x.csv changed"])))
        self.assertIn("current:", rc.ga_line(("a.pdf", [])))

    def test_every_ga_line_says_to_run_the_audit_at_release(self):
        """The sheet's record can't show a change to the generator's own code, so whatever the GA reads, the line says to
        run the Checker's audit at release too (Reviewer 6's P3 on #425, the Lead's ruling)."""
        for ga in (("a.pdf", []), ("a.pdf", ["v2/04-BOM/x.csv changed"]), (None, []), (None, ["not read: OSError"])):
            self.assertIn("At release, run the Checker's audit (#413) too", rc.ga_line(ga), ga)


class D162CutListRow(unittest.TestCase):
    """D-162: a weldment member's drawing is its frame's cut list row, when the row states section, cut length,
    both end angles and quantity; a member keeps its own sheet only where the row can't say it."""
    CUT = FRONT_LISTS + "351104_P01_FRONT-DECOR-FRAME-DL-TUBE-CUT-LIST.csv"
    HEAD = "frame,member,member_part,name,section,length_mm,qty,ends,status\n"
    ROW = {"section": "20 x 40 x 1.0", "length_mm": "1491.35", "qty": "1", "ends": ""}

    def made(self, ends, file_map=None):
        cut = {self.CUT: self.HEAD + f"351104,B01,352101,BACK RING BOTTOM,6063-T6 aluminium tube 20 x 20 x 1.5,272.0,1,{ends},calculation\n"}
        fai = rc.fai_plan(PLAN, BOM)
        register = BOM.parse_register(REGISTER, "test")
        fm = dict(BLOCK_FILES, **(file_map or {}))
        made, _ = rc.check_parts(D120Members().lists(), register, rc.files_by_pn(fm), list(fm), fai, fai[1],
                                 rc.register_products(REGISTER, BOM), "unlocked", BOM, {}, cut, {})
        return next(m for m in made if m["part_number"] == "352101")

    def test_a_full_cut_list_row_is_the_members_drawing(self):
        m = self.made('"41.01° and 45° from square"')
        self.assertTrue(m["dwg"].startswith("its frame's cut list row, 351104 (D-162)"), m["dwg"])
        self.assertNotIn("drawing", m["gaps"])

    def test_a_row_that_sends_the_angles_elsewhere_is_not_a_drawing(self):
        m = self.made('mitred to its neighbours (angles on the frame drawing)')
        self.assertEqual(m["dwg"], "no: its cut list row (D-162) doesn't give both end angles")
        self.assertIn("drawing", m["gaps"])

    def test_square_ends_count_as_both_angles(self):
        self.assertIn("(D-162)", self.made("square both ends")["dwg"])

    def test_the_members_own_sheet_still_counts(self):
        sheet = {"v2/02-Drawings/front/352101_P01_FRONT-DECOR-FRAME-DL-BACK-RING-BOTTOM_DWG.pdf": "working tree"}
        self.assertEqual(self.made('mitred to its neighbours (angles on the frame drawing)', sheet)["dwg"], "yes")

    def drawn(self, ends):
        """True when check_parts takes the member's cut list row, ends as given, for its drawing."""
        return self.made('"%s"' % ends)["dwg"].startswith("its frame's cut list row, 351104 (D-162)")

    def test_angles_in_deg_or_degrees_count_as_well_as_the_degree_sign(self):
        # Reviewer 6 on #354: CEILING's side and seam members, 'front end mitred 45 deg, back end mitred 63.43 deg
        # off square'
        rows = rc.d162_rows({CEILING_CUT: CEILING_ROWS})
        for pn, frame in (("412101", "411101"), ("412102", "411101"), ("412202", "411102")):
            self.assertEqual(rows[pn], (frame, []), pn)
        self.assertEqual(rc.member_row_lacks(dict(self.ROW, ends="45 degrees and 30 Degrees")), [])
        self.assertTrue(self.drawn("front end mitred 45 deg, back end mitred 63.43 deg off square"))

    def test_one_angle_given_for_both_ends_states_both(self):
        # the Lead's rulings: CEILING's front and back members, 'both ends mitred 45 deg' and 'both ends mitred 26.57
        # deg off square'; WALL's front and back stiles, 'bottom and top ends both mitred 45.00° off square'
        rows = rc.d162_rows({CEILING_CUT: CEILING_ROWS, WALL_CUT: WALL_ROWS})
        for pn, frame in (("412103", "411101"), ("412104", "411101"), ("412203", "411102"), ("412204", "411102"),
                          ("212103", "211101"), ("212104", "211101")):
            self.assertEqual(rows[pn], (frame, []), pn)
        self.assertEqual(rc.member_row_lacks(dict(self.ROW, ends="mitred 30° at both ends")), [])
        for ends in ("both ends mitred 45 deg; welded into the frame (D-131, J-FRAME-01)",
                     "bottom and top ends both mitred 45.00° off square, in the frame's plane"):
            self.assertTrue(self.drawn(ends), ends)

    def test_square_ends_need_no_angle(self):
        # WALL's mid stiles, 'square ends (fits between the rails, welded T joints, D-131)'; CEILING's cross members,
        # 'square cut'
        rows = rc.d162_rows({CEILING_CUT: CEILING_ROWS, WALL_CUT: WALL_ROWS})
        self.assertEqual(rows["212105"], ("211101", []))
        self.assertEqual(rows["412105"], ("411101", []))
        self.assertTrue(self.drawn("square ends (fits between the rails, welded T joints, D-131)"))

    def test_one_angle_for_one_end_is_not_both(self):
        for ends in END_WORDINGS[9:]:
            self.assertEqual(rc.member_row_lacks(dict(self.ROW, ends=ends)), ["both end angles"], ends)
            self.assertFalse(self.drawn(ends), ends)
        for ends in END_WORDINGS[:9]:
            self.assertEqual(rc.member_row_lacks(dict(self.ROW, ends=ends)), [], ends)

    def test_every_row_reads_as_c05_reads_it(self):
        # the checklist and C05 give the same answer on every row (C05's member_row_lacks, the Checker's #357)
        _geometry, c_drawings = rc.load_checks()
        if not hasattr(c_drawings, "member_row_lacks"):
            self.skipTest("C05's member_row_lacks comes with the Checker's #357")
        rows = [r for text in (CEILING_ROWS, WALL_ROWS) for r in csv.DictReader(io.StringIO(text))]
        rows += [dict(self.ROW, ends=ends) for ends in END_WORDINGS]
        for r in rows:
            self.assertEqual(rc.member_row_lacks(r), c_drawings.member_row_lacks(r), r["ends"])


class MakerAlternatives(unittest.TestCase):
    """Reviewer 6 on #345: 848011 names two candidates to pick at the RFQ, so it isn't a chosen product yet; an
    all-digit number counts only from the SKU cell."""

    def tape(self, **kw):
        r = row("848011", "buy", "SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY", "hook-and-loop or reclosable fastener tape, 25 mm, PSA")
        r.update(kw)
        return r

    def test_a_maker_or_sku_cell_naming_alternatives_is_not_named(self):
        _, bought = run([self.tape(maker="VELCRO Brand, or 3M (one to pick at the RFQ)",
                                   sku="VELCRO PS14 hook 25 mm, or 3M Dual Lock SJ3560 25 mm (hardware selection V2-ENG-SEL)")], {})
        self.assertEqual(bought[0]["sku"], "no")

    def test_digits_in_the_name_alone_do_not_count(self):
        elec = row("718027", "buy", "ELECTRICAL - CABLE - 4 X 24 AWG SCREENED - BELDEN 9534", team="ELECTRICAL",
                   src="v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv")
        elec.update(maker="Belden", sku="")
        _, bought = run([elec], {})
        self.assertEqual(bought[0]["sku"], "no")


class BoughtParts(unittest.TestCase):
    def test_register_named_part_with_a_test_is_done(self):
        _, bought = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16")], {},
                        tests=[("T06", "T06 rivnut torque with the 838001 bolt")])
        self.assertEqual((bought[0]["sku"], bought[0]["tests"], bought[0]["state"]), ("yes", ["T06"], "done"))

    def test_register_hold_wins_over_the_parts_list(self):
        _, bought = run([row("518001", "buy", "LINING - CASSETTE CLIP - ACME CL-20")], {})
        self.assertEqual((bought[0]["state"], bought[0]["tests"]), ("HOLD", ["T07"]))

    def test_the_register_reads_hold_as_a_whole_word(self):
        text = REGISTER + ("| H-30 | **838009** | HARDWARE - GROMMET | bought | 4 | part DECIDED; the strip holds the seal |\n"
                           "| H-31 | **838010** | HARDWARE - CLIP | bought | 4 | number adopted; product on hold until T07 |\n")
        got = rc.register_products(text, BOM)
        self.assertEqual((got["838009"], got["838010"]), ("named", "hold"))   # "holds" is not HOLD; "on hold" is

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

    FILL_PIECES = ("WALL - CAVITY FILL PIECE F01 240 X 1102.7 - SIDE LOWER - COMMON",
                   "WALL - CAVITY FILL PIECE F09 274.7 X 1078.6 - BACK LOWER - B1")

    def test_a_fill_piece_is_fill_with_its_size_and_code_left_out(self):
        # the WALL Drawings Engineer's catch: the head noun read 'X' from the size, so WALL's fill pieces missed the
        # fill ruling the mechanical check follows (the Lead's ruling on WALL's L1 sample, 2026-11-01)
        for n in self.FILL_PIECES:
            self.assertEqual((rc.head_noun(n), rc.soft_kind(n)), ("FILL", "felt or fill"), n)
        row_text = ("part_number,name,size_mm,material,tolerance_mm\n111501," + self.FILL_PIECES[0] +
                    ",240 x 1102.7 x 40,PET fill 24 kg/m3,±2\n")
        line = self.foam(self.CADS, row_text, name=self.FILL_PIECES[0])
        self.assertEqual((line["flat"], line["dwg"]), ("cut list", "cut list (D-89)"))

    def test_the_checklist_reads_names_with_the_mechanical_checks_own_function(self):
        # one reader for both tools: a change in C05's head_noun reaches the checklist
        common = rc.checks_common()
        old = common.head_noun
        common.head_noun = lambda name: "FELT"
        try:
            self.assertEqual(rc.soft_kind("WALL - PANEL FRAME - SIDE LOWER - LH"), "felt or fill")
        finally:
            common.head_noun = old

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
                 "BASE - SEAL HOLDER - LH", "SEALS - JOINT GASKET - 8 X 3.97", "POD - FIXING TAPE", "WALL - PANEL FRAME - SIDE LOWER - LH",
                 *self.FILL_PIECES, "WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH"]
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


class NoFaiFlag(unittest.TestCase):
    def test_a_made_part_with_no_fai_line_is_listed(self):
        fai = rc.fai_plan(PLAN, BOM)
        frame = row("211101", "make", "WALL - PANEL FRAME", "aluminium 6063-T6 tube, mill finish")
        bracket = row("351999", "make", "FRONT - TEST BRACKET", "aluminium sheet 2 mm, mill finish", team="FRONT")
        made, _ = rc.check_parts([frame, bracket], [], {}, [], fai, fai[1], {}, "unlocked", BOM, {}, {})
        text = rc.render(made, [], [], [], "this working tree", "unlocked", {}, fai, "2026-11-01")
        self.assertIn("## Made parts with no FAI line", text)
        self.assertIn("| FRONT | 351999 | FRONT - TEST BRACKET |", text)
        self.assertNotIn("| WALL | 211101 |", text.split("## Made parts with no FAI line")[1].split("## Made parts and assemblies")[0])
        made, _ = rc.check_parts([frame], [], {}, [], fai, fai[1], {}, "unlocked", BOM, {}, {})
        self.assertIn("Every made number has at least one line in the FAI plan", rc.render(made, [], [], [], "", "unlocked", {}, fai, "2026-11-01"))

    def test_the_real_fai_plan_gives_each_line_a_sample(self):
        text = (rc.ROOT / rc.FAI).read_text(encoding="utf-8")
        for hdr, cells in BOM.table_rows(text):
            if cells and (cells[0].startswith("K-") or cells[0].startswith("F-")):
                self.assertIn("Sample", hdr, cells[0])
                self.assertTrue(cells[hdr.index("Sample")], cells[0])


class FlatPartColumns(unittest.TestCase):
    """FRONT's lists give the cut in a type column; a note that says bonded keeps the drawing (PM, 2026-11-01)."""
    LIST = "v2/03-Manufacturing/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv"
    HEAD = "part_number,name,type,material,finish,note"

    def lacks(self, line):
        return rc.flat_lacks(rc.cut_rows({self.LIST: self.HEAD + "\n" + line + "\n"})["351302"])

    def test_the_type_column_names_the_cut(self):
        line = ('351302,FRONT - DECOR BACK PLATE - DR,"made (laser-cut sheet, no drawing: D-89 part 4)",'
                '"aluminium EN AW-5754-H22 sheet 2.0 mm, general tolerance ISO 2768-m",mill finish,"blind-riveted to the frame"')
        self.assertEqual(self.lacks(line), [])

    def test_a_bonded_part_keeps_its_drawing(self):
        line = ('351302,FRONT - DECOR BACK PLATE - DT,"made (CNC-routed ACP, no drawing: D-89 part 4)",'
                '"ACP 3 mm, general tolerance ISO 2768-m",as supplied,"bonded to the frame"')
        self.assertEqual(self.lacks(line), ["no bends or machined features (its process names bond)"])


class D125PlainStrip(unittest.TestCase):
    """D-125, read as C05 reads it: the checklist calls the mechanical check's own functions (tools/checks), so a
    plain strip or sheet on a full parts-list row counts as drawn in both tools, or in neither."""
    LIST = "v2/03-Manufacturing/interior/810000_P01_INTERIOR-PARTS-LIST_BOM.csv"

    def strip_line(self, d125):
        fai = rc.fai_plan(PLAN, BOM)
        part = row("811299", "make", "INTERIOR - TEST STRIP", "aluminium 5052-H32 sheet", team="CEILING (builds INTERIOR, D-80)", src=self.LIST)
        part["finish"] = "mill finish"
        file_map = files("811299_P01_INTERIOR-TEST-STRIP_CAD.f3d", "811299_P01_INTERIOR-TEST-STRIP_STEP.step",
                         folder="v2/03-Manufacturing/interior/")
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {}, {}, None, d125)
        return made[0]

    def test_it_uses_the_mechanical_checks_own_functions(self):
        c_geometry, c_drawings = rc.load_checks()
        here = Path(c_drawings.__file__).resolve()
        self.assertEqual(here, (rc.ROOT / "tools/checks/c_drawings.py").resolve())
        for name in ("cuboid_sides", "is_strip", "strip_row_lacks", "body_shape", "strip_sides", "prism_shapes",
                     "felt_dxf_lacks", "drawgen_parts"):
            self.assertTrue(callable(getattr(c_drawings, name)), name)
        self.assertTrue(callable(c_geometry.load_step))

    def test_the_strip_list_is_c05s_shared_function(self):
        # the checklist builds no list of its own: it gives c_drawings.strip_sides the per-part STEP files (PR #210)
        seen = {}
        _geometry, c_drawings = rc.load_checks()
        old = c_drawings.strip_sides, c_drawings.strip_row_lacks
        c_drawings.strip_sides = lambda paths, load=None: seen.setdefault("call", (list(paths), load)) and {"211199": (1.5, 28.0, 991.0)}
        c_drawings.strip_row_lacks = lambda root, pn, sides: ([], "list.csv")
        try:
            got = rc.d125_strips()
        finally:
            c_drawings.strip_sides, c_drawings.strip_row_lacks = old
        self.assertEqual(got, {"211199": ([], "list.csv")})
        paths, load = seen["call"]
        self.assertTrue(all(str(x).endswith((".step", ".stp")) for x in paths), paths[:3])
        self.assertIs(load, _geometry.load_step)

    def test_a_full_row_counts_as_drawn(self):
        line = self.strip_line({"811299": ([], self.LIST)})
        self.assertEqual((line["flat"], line["dwg"]), ("row (D-125)", "row: a plain strip or sheet (D-125)"))
        self.assertNotIn("drawing", line["gaps"])

    def test_a_short_row_keeps_the_drawing_and_says_why(self):
        line = self.strip_line({"811299": (["finish", "tolerance"], self.LIST)})
        self.assertTrue(line["dwg"].startswith("no: as a plain strip or sheet (D-125)"), line["dwg"])
        self.assertIn("finish, tolerance", line["dwg"])
        self.assertIn("drawing", line["gaps"])

    def test_no_strip_no_change(self):
        self.assertEqual(self.strip_line({})["dwg"], "no")
        self.assertEqual(self.strip_line(None)["dwg"], "no")

    def test_the_real_run_passes_the_strip_list_on(self):
        # main() reads D-125 and hands that list to check_parts; a run that stops passing it fails here (Reviewer 6, #211)
        import inspect
        import tempfile as _tempfile
        seen, strips = {}, {"811299": ([], self.LIST)}

        class Stop(Exception):
            pass

        def spy(*args, **kw):
            seen["d125"] = inspect.signature(real).bind(*args, **kw).arguments.get("d125")
            raise Stop

        real, old = rc.check_parts, rc.d125_strips
        rc.check_parts, rc.d125_strips = spy, (lambda root=None: strips)
        try:
            with _tempfile.TemporaryDirectory() as d, self.assertRaises(Stop):
                rc.main(["--screen", "unlocked", "--out", str(Path(d, "release-checklist.md"))])
        finally:
            rc.check_parts, rc.d125_strips = real, old
        self.assertIs(seen.get("d125"), strips)


class D125SharedRows(unittest.TestCase):
    """C05's D-125 row cases (tools/checks/tests), run through the function the checklist calls, plus three sizes
    needed and a HOLD grade that counts as stated (PM, 2026-11-01)."""
    ROW = {"part_number": "811205", "name": "INTERIOR - LIGHT SHELF - DIFFUSER RH", "kind": "MP",
           "material": "Opal polycarbonate (grade HOLD: picked with ELECTRICAL's down-light strips)",
           "finish": "opal, as supplied", "process": "cut to length",
           "size_mm": "991.0 long, section 28.0 x 1.5, 1.5 sheet", "tolerance": "±0.5 on cut sizes (assumption)"}
    SIDES = (1.5, 28.0, 991.0)

    def lacks(self, **change):
        import csv as _csv
        import tempfile as _tempfile
        _geometry, c_drawings = rc.load_checks()
        row = {**self.ROW, **change}
        with _tempfile.TemporaryDirectory() as d:
            folder = Path(d, "v2/03-Manufacturing/interior")
            folder.mkdir(parents=True)
            with open(folder / "810000_P01_INTERIOR-PARTS-LIST_BOM.csv", "w", encoding="utf-8", newline="") as f:
                w = _csv.DictWriter(f, fieldnames=list(row))
                w.writeheader()
                w.writerow(row)
            got = c_drawings.strip_row_lacks(d, "811205", self.SIDES)
        return " | ".join(got[0]) if got else None

    def test_c05s_cases(self):
        self.assertEqual(self.lacks(), "")                                       # the full row stands in for a drawing
        self.assertIn("finish", self.lacks(finish=""))
        self.assertIn("the material's grade", self.lacks(material="polycarbonate"))
        self.assertIn("1.5 x 28 x 991", self.lacks(size_mm="980.0 long, section 28.0 x 1.5"))   # not the STEP's length
        self.assertIn("tolerance on the length and the width", self.lacks(tolerance=""))
        self.assertIn("hole", self.lacks(process="cut to length, one cable hole"))
        self.assertIn("tolerance on the width", self.lacks(tolerance="cut length +/-1 (assumption)"))  # 811205's line
        self.assertEqual(self.lacks(tolerance="cut length +/-1, width as supplied (assumption)"), "")  # a bought strip
        self.assertEqual(self.lacks(tolerance="ISO 2768-m"), "")
        self.assertEqual(self.lacks(tolerance="length ±1; width ±0.5"), "")

    def test_three_sizes_needed(self):
        self.assertIn("1.5 x 28 x 991", self.lacks(size_mm="991.0 long, 28.0 wide"))

    def test_a_hold_grade_counts_as_stated_and_shows_hold(self):
        self.assertEqual(self.lacks(), "")          # its grade is on HOLD, and the row still passes D-125
        fai = rc.fai_plan(PLAN, BOM)
        part = row("211199", "make", "WALL - TEST STRIP", "opal polycarbonate (grade HOLD)", team="WALL")
        part["finish"] = "opal, as supplied"
        file_map = files("211199_P01_WALL-TEST-STRIP_CAD.f3d", "211199_P01_WALL-TEST-STRIP_STEP.step")
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {}, {}, None, {"211199": ([], WALL)})
        self.assertEqual((made[0]["dwg"], made[0]["state"]), ("row: a plain strip or sheet (D-125)", "HOLD"))


class D128FeltPieces(unittest.TestCase):
    """D-128, read as C05 reads it (#233): a felt or fill piece with through-openings or edge notches only needs no
    drawing when its DXF and its parts-list row are full; the checklist calls C05's prism_shapes and felt_dxf_lacks."""
    CUT = "v2/03-Manufacturing/wall/510000_P01_LINING-CUT-LIST_SPEC.csv"

    def line(self, d128, cut=None):
        fai = rc.fai_plan(PLAN, BOM)
        felt = row("511302", "make", "LINING - FELT - SIDE UPPER - LH", "PET felt 9 mm Dark Gray")
        file_map = files("511302_P01_LINING-FELT_CAD.f3d", "511302_P01_LINING-FELT_STEP.step",
                         "511302_P01_LINING-FELT_DXF.dxf")
        made, _ = rc.check_parts([felt], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {self.CUT: cut} if cut else {}, {}, None, None, None, d128)
        return made[0]

    def test_a_full_dxf_and_row_stand_in_for_the_drawing(self):
        line = self.line({"511302": []})
        self.assertEqual((line["flat"], line["dwg"]), ("yes", "DXF and row (D-128)"))
        self.assertNotIn("drawing", line["gaps"])

    def test_what_it_lacks_keeps_the_drawing_and_says_so(self):
        line = self.line({"511302": ["a parts-list row", "a DXF it can read (ASCII)"]})
        self.assertEqual(line["dwg"], "no: as a felt or fill piece on its DXF (D-128) it needs a parts-list row; "
                                      "a DXF it can read (ASCII)")
        self.assertIn("drawing", line["gaps"])
        self.assertEqual(self.line({})["dwg"], "no")
        self.assertEqual(self.line(None)["dwg"], "no")

    def test_a_plain_rectangle_passes_on_d89_first(self):
        # C05's order: D-89's cut-list route before D-128, even when D-128's reading would pass too
        cut = "part_number,name,size_mm,material,tolerance_mm\n511302,LINING - FELT,9 x 1442 x 1139.74,PET felt 9 mm,+0 / -2\n"
        self.assertEqual(self.line({"511302": []}, cut)["dwg"], "cut list (D-89)")
        self.assertEqual(self.line({"511302": ["a parts-list row"]}, cut)["dwg"], "cut list (D-89)")

    def test_it_calls_c05s_functions(self):
        # C05's own file index and DXF pick (the highest revision), shapes and reading: nothing of the checklist's own
        c_geometry, c_drawings = rc.load_checks()
        seen = {}
        old = c_geometry.models, c_drawings.prism_shapes, c_drawings.felt_dxf_lacks, c_drawings.index_files
        c_drawings.index_files = lambda root: {"511302": {"DXF": [("P02", "/r/511302_P02_X_DXF.dxf"), ("P01", "/r/511302_P01_X_DXF.dxf")]},
                                               "511303": {"STEP": [("P01", "/r/511303_P01_X_STEP.step")]}}
        c_geometry.models = lambda root: ({}, ["a_STEP.step", "b_STEP.step"])
        c_drawings.prism_shapes = lambda paths, load=None: seen.setdefault("prism", (list(paths), load)) and {"511302": "SHAPE"}
        c_drawings.felt_dxf_lacks = lambda root, pn, shape, dxf: seen.setdefault("lacks", (root, pn, shape, dxf)) and ["X"]
        try:
            got = rc.d128_pieces(["511302", "511303"])
        finally:
            c_geometry.models, c_drawings.prism_shapes, c_drawings.felt_dxf_lacks, c_drawings.index_files = old
        self.assertEqual(got, {"511302": ["X"]})                        # 511303 has no DXF: not read
        self.assertEqual(seen["prism"], (["a_STEP.step", "b_STEP.step"], c_geometry.load_step))
        self.assertEqual(seen["lacks"], (str(rc.ROOT), "511302", "SHAPE", "/r/511302_P02_X_DXF.dxf"))   # the highest revision
        self.assertEqual(rc.d128_pieces([]), {})

    def test_its_dxf_is_c05s_on_the_real_tree(self):
        # every felt or fill piece the checklist reads gets the DXF C05's check_drawings takes for it
        _geometry, c_drawings = rc.load_checks()
        idx = c_drawings.index_files(str(rc.ROOT))
        seen, old = {}, c_drawings.felt_dxf_lacks
        c_drawings.felt_dxf_lacks = lambda root, pn, shape, dxf: seen.setdefault(pn, dxf) and []
        try:
            rc.d128_pieces([pn for pn, kinds in idx.items() if kinds.get("DXF") and pn.startswith("513")])
        finally:
            c_drawings.felt_dxf_lacks = old
        self.assertTrue(seen)
        for pn, dxf in seen.items():
            self.assertEqual(dxf, sorted(idx[pn]["DXF"])[-1][1], pn)

    def test_the_real_run_passes_d128_on(self):
        # main() reads D-128 and hands that reading to check_parts; a run that stops passing it fails here
        import inspect
        import tempfile as _tempfile
        seen, reading = {}, {"511302": []}

        class Stop(Exception):
            pass

        def spy(*args, **kw):
            seen["d128"] = inspect.signature(real).bind(*args, **kw).arguments.get("d128")
            raise Stop

        real, old = rc.check_parts, (rc.d128_pieces, rc.d125_strips, rc.drawgen_parts)
        rc.check_parts = spy
        rc.d128_pieces = lambda candidates, root=None: seen.setdefault("candidates", set(candidates)) is not None and reading
        rc.d125_strips, rc.drawgen_parts = (lambda root=None: {}), (lambda root=None: set())
        try:
            with _tempfile.TemporaryDirectory() as d, self.assertRaises(Stop):
                rc.main(["--screen", "unlocked", "--out", str(Path(d, "release-checklist.md"))])
        finally:
            rc.check_parts = real
            rc.d128_pieces, rc.d125_strips, rc.drawgen_parts = old
        self.assertIs(seen.get("d128"), reading)
        self.assertTrue({"513301", "513302", "513303"} <= seen["candidates"], sorted(seen["candidates"])[:8])   # felt and fill


class MadeHold(unittest.TestCase):
    """A made part with nothing else missing whose own material, grade or status says HOLD shows HOLD, not done
    (PM, 2026-11-01); open gaps show first; the totals count it under Made: HOLD."""
    LIST = WALL
    HEAD = "part_number,name,material,grade,finish,status,mass_status"

    def line(self, material="aluminium 5052-H32 sheet", rows="", drawn=True, head=None):
        fai = rc.fai_plan(PLAN, BOM)
        part = row("211199", "make", "WALL - TEST STRIP", material, team="WALL", src=self.LIST)
        part["finish"] = "mill finish"
        file_map = files("211199_P01_WALL-TEST-STRIP_CAD.f3d", "211199_P01_WALL-TEST-STRIP_STEP.step")
        made, _ = rc.check_parts([part], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "unlocked", BOM, {},
                                 {self.LIST: (head or self.HEAD) + "\n" + rows} if rows else {}, {}, None,
                                 {"211199": ([], self.LIST)} if drawn else {})
        return made[0]

    def test_a_grade_on_hold_shows_hold(self):
        self.assertEqual(self.line(material="opal polycarbonate (grade HOLD)")["state"], "HOLD")
        own = "211199,WALL - TEST STRIP,polycarbonate,HOLD,mill finish,DRAFT,calculation\n"
        self.assertEqual(self.line(rows=own)["state"], "HOLD")                     # a grade column
        status = "211199,WALL - TEST STRIP,polycarbonate PC 2407,,mill finish,HOLD,calculation\n"
        self.assertEqual(self.line(rows=status)["state"], "HOLD")                  # its status
        self.assertEqual(self.line()["state"], "done")

    def test_gaps_show_first(self):
        self.assertEqual(self.line(material="aluminium (alloy HOLD)", drawn=False)["state"], "open: drawing")

    def test_only_its_own_columns_count(self):
        massnote = "211199,WALL - TEST STRIP,polycarbonate PC 2407,,mill finish,DRAFT,real kg/m2 HOLD\n"
        self.assertEqual(self.line(rows=massnote)["state"], "done")

    def test_another_parts_row_naming_it_is_not_read(self):
        # a bracket's row with 211199 in its parent cell reaches 211199's rows (cut_rows); only its own row counts
        head = "part_number,parent,name,material,grade,finish,status,mass_status"
        other = "218101,211199,WALL - BRACKET,aluminium (alloy HOLD),HOLD,mill finish,HOLD,calculation\n"
        reached = rc.cut_rows({self.LIST: head + "\n" + other}).get("211199", [])
        self.assertEqual([cells["part_number"] for cells, _path in reached], ["218101"])
        self.assertEqual(self.line(rows=other, head=head)["state"], "done")
        own = "211199,210101,WALL - TEST STRIP,polycarbonate,HOLD,mill finish,DRAFT,calculation\n"
        self.assertEqual(self.line(rows=other + own, head=head)["state"], "HOLD")

    def test_hold_is_a_whole_word(self):
        for material in ("aluminium 5052-H32, the lip holds the felt", "aluminium 5052-H32 threshold trim",
                         "aluminium 5052-H32 (HOLDER bracket)"):
            self.assertEqual(self.line(material=material)["state"], "done", material)
        own = "211199,WALL - TEST STRIP,polycarbonate PC 2407,,mill finish,DRAFT (holds its shape),calculation\n"
        self.assertEqual(self.line(rows=own)["state"], "done")
        for material in ("aluminium (alloy on hold)", "aluminium 5052 (HOLD-02)"):
            self.assertEqual(self.line(material=material)["state"], "HOLD", material)

    def test_the_totals_count_made_hold(self):
        held = self.line(material="aluminium (alloy HOLD)")
        text = rc.render([held], [], [], [], "main", "unlocked", {}, ([], [], []), "2026-11-01")
        self.assertIn("| Made: HOLD |", text)
        self.assertIn("| WALL | 0 | 0 | 0 | 1 | 0 | 0 | 0 |", text)


class DrawgenParts(unittest.TestCase):
    """D-113 (1): a part tools/drawgen draws is never blocked by a locked screen, because drawgen doesn't run in Fusion;
    the list is drawgen's own registry (tools/drawgen/specs.py), with the numbers its tabulated sheets cover."""

    def line(self, pn, drawgen, mass=1.0):
        rh = row(pn, "make", "WALL - PANEL FRAME - " + pn, "aluminium 6063-T6 tube 20 x 40 x 1.2, mill finish", mass=mass)
        rh["cut_rows"] = True
        file_map = files(f"{pn}_P01_WALL-FRAME_CAD.f3d", f"{pn}_P01_WALL-FRAME_STEP.step")
        fai = rc.fai_plan(PLAN, BOM)
        made, _ = rc.check_parts([rh], [], rc.files_by_pn(file_map), list(file_map), fai, fai[1], {}, "locked", BOM, {}, {},
                                 None, None, None, drawgen)
        return made[0]

    def test_a_part_drawgen_draws_is_never_blocked(self):
        self.assertEqual(self.line("211102", None)["state"], rc.BLOCKED)              # Fusion's: waits for the screen
        self.assertEqual(self.line("211102", set())["state"], rc.BLOCKED)
        self.assertEqual(self.line("211102", {"211102"})["state"], "open: drawing")   # drawgen's: it can draw it now

    def test_a_drawgen_part_with_a_second_gap_shows_both(self):
        # drawgen lifts only the locked screen's hold on the drawing; every other gap still shows (Reviewer 6, #227)
        line = self.line("211102", {"211102"}, mass=None)
        self.assertEqual((line["gaps"], line["state"]), (["drawing", "mass"], "open: drawing, mass"))

    def test_the_list_is_drawgens_own_registry(self):
        got = rc.drawgen_parts()
        # D-128 dropped the fill sheet (211501 to 211504 go on DXFs); 111103 joined with #225
        self.assertTrue({"211101", "211102", "111101", "111103"} <= got, sorted(got))
        self.assertFalse({"211501", "211504"} & got, sorted(got))
        import tempfile as _tempfile
        with _tempfile.TemporaryDirectory() as d:   # a planted registry, read through the same reader
            Path(d, "tools", "drawgen").mkdir(parents=True)
            Path(d, "tools", "drawgen", "specs.py").write_text(
                'SPECS = {"999901": ("wall", "part", {}), "999911": ("wall", "tabulated", {"covers": ["999911", "999912"]})}\n')
            self.assertEqual(rc.drawgen_parts(d), {"999901", "999911", "999912"})

    def test_the_list_is_read_by_c05s_own_reader(self):
        # one reader for both tools (c_drawings.drawgen_parts, #233), so they can't list drawgen's parts apart
        _geometry, c_drawings = rc.load_checks()
        old, seen = c_drawings.drawgen_parts, {}
        c_drawings.drawgen_parts = lambda root: seen.setdefault("root", root) and {"999901"}
        try:
            got = rc.drawgen_parts()
        finally:
            c_drawings.drawgen_parts = old
        self.assertEqual((got, seen["root"]), ({"999901"}, str(rc.ROOT)))

    def test_the_totals_and_notes_say_why(self):
        lines = [self.line("211101", {"211102"}), self.line("211102", {"211102"})]
        text = rc.render(lines, [], [], [], "main", "locked", {}, ([], [], []), "2026-11-01", (), {"211102"})
        self.assertIn("| WALL | 0 | 1 | 1 | 0 | 0 | 0 | 0 |", text)
        self.assertIn("1 wait for the unlocked screen (D-84) and 1 are drawn by tools/drawgen, which a locked screen "
                      "doesn't hold (D-113)", text)
        self.assertIn("its specs.py: 211102)", text)

    def test_the_real_run_passes_drawgens_list_on(self):
        # main() reads drawgen's registry and hands it to check_parts and the notes; a run that stops passing it fails
        import inspect
        import tempfile as _tempfile
        seen, parts = {}, {"211102"}

        class Stop(Exception):
            pass

        def spy_parts(*args, **kw):
            seen["check_parts"] = inspect.signature(real_parts).bind(*args, **kw).arguments.get("drawgen")
            return real_parts(*args, **kw)

        def spy_render(*args, **kw):
            seen["render"] = inspect.signature(real_render).bind(*args, **kw).arguments.get("drawgen")
            raise Stop

        real_parts, real_render, old = rc.check_parts, rc.render, (rc.drawgen_parts, rc.d125_strips)
        rc.check_parts, rc.render = spy_parts, spy_render
        rc.drawgen_parts, rc.d125_strips = (lambda specs=None: parts), (lambda root=None: {})
        try:
            with _tempfile.TemporaryDirectory() as d, self.assertRaises(Stop):
                rc.main(["--screen", "locked", "--out", str(Path(d, "release-checklist.md"))])
        finally:
            rc.check_parts, rc.render = real_parts, real_render
            rc.drawgen_parts, rc.d125_strips = old
        self.assertIs(seen.get("check_parts"), parts)
        self.assertIs(seen.get("render"), parts)


class OpenPrFiles(unittest.TestCase):
    """A branch stacked on a PR that squash-merged since keeps that PR's older copies; main's newer files win."""
    SKIN = "v2/03-Manufacturing/ceiling/411302_P01_CEILING-SKIN-C2_DXF.dxf"
    CUT = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv"
    OWN = "v2/03-Manufacturing/air/611101_P01_AIR-COLUMN-FACE-FRONT_DXF.dxf"

    def stacked(self, d, rebased=False):
        """main, then CEILING's PR (01:00), AIR stacked on it (02:00), then CEILING squash-merged on main (05:00).
        rebased: AIR's copy of CEILING's commit carries a 06:00 committer time, as a rebase gives it, but keeps its
        01:00 author time."""
        import os
        import subprocess

        def g(*a, when="2026-11-01T00:00:00", committed=None):
            env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": committed or when}
            subprocess.run(["git", "-C", d, "-c", "user.email=t@example.com", "-c", "user.name=t", *a],
                           check=True, capture_output=True, text=True, env=env)

        def put(files, when, committed=None):
            for path, text in files.items():
                Path(d, path).parent.mkdir(parents=True, exist_ok=True)
                Path(d, path).write_text(text, encoding="utf-8")
            g("add", "-A", when=when)
            g("commit", "-q", "-m", ", ".join(files), when=when, committed=committed)

        g("init", "-q")
        g("checkout", "-q", "-b", "main")
        put({"v2/01-CAD-Native/README.md": "start"}, "2026-11-01T00:00:00")
        g("checkout", "-q", "-b", "ceiling")
        put({self.SKIN: "old outline", self.CUT: "part_number,cut\n411101,old\n"}, "2026-11-01T01:00:00",
            "2026-11-01T06:00:00" if rebased else None)
        g("checkout", "-q", "-b", "air")
        put({self.OWN: "AIR's face"}, "2026-11-01T02:00:00", "2026-11-01T06:00:00" if rebased else None)
        g("checkout", "-q", "main")
        put({self.SKIN: "merged outline", self.CUT: "part_number,cut\n411101,merged\n"}, "2026-11-01T05:00:00")

    def files_and_texts(self, rebased=False):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.stacked(d, rebased)
            old = rc.ROOT, BOM.ROOT
            rc.ROOT = BOM.ROOT = Path(d)
            BOM.FELL_BACK.clear()
            try:
                files = rc.list_files(["main", "air"], BOM)
                return files, rc.cut_list_texts(files, ["main", "air"]), list(BOM.FELL_BACK)
            finally:
                rc.ROOT, BOM.ROOT = old
                BOM.FELL_BACK.clear()

    def test_a_stacked_branch_old_copies_do_not_hide_main_newer_files(self):
        files, _, _ = self.files_and_texts()
        self.assertEqual(files[self.SKIN], "main")
        self.assertEqual(files[self.OWN], "air")

    def test_a_rebase_does_not_make_an_old_copy_new(self):
        # the rule reads author times: a rebase gives AIR's copy of CEILING's commit a new committer time only
        files, _, fell = self.files_and_texts(rebased=True)
        self.assertEqual(files[self.SKIN], "main")
        self.assertEqual(files[self.OWN], "air")
        self.assertIn(("air", self.SKIN), fell)

    def test_cut_lists_are_read_from_the_ref_that_listed_them(self):
        # not from the newest branch that has a copy: AIR's old copy of CEILING's cut list must not be read
        files, cuts, _ = self.files_and_texts()
        self.assertEqual(files[self.CUT], "main")
        self.assertIn("merged", cuts[self.CUT])

    def test_the_checklist_names_the_files_read_from_main(self):
        _, _, fell = self.files_and_texts()
        self.assertEqual(sorted(fell), [("air", self.CUT), ("air", self.SKIN)])
        BOM.FELL_BACK[:] = fell
        try:
            lines = BOM.fell_back_lines({"air": "PR #91"})
        finally:
            BOM.FELL_BACK.clear()
        self.assertTrue(lines[1].startswith(f"`{self.SKIN}`: PR #91 changed it, but main changed it later"), lines)
        text = rc.render([], [], [], [], "main (abc1234)", "unlocked", {}, ([], [], []), "2026-11-01", fell_back=lines)
        self.assertIn("Read from main although an open PR changed them", text)
        self.assertIn(self.SKIN, text)
        self.assertNotIn("Read from main although", rc.render([], [], [], [], "main", "unlocked", {}, ([], [], []), "2026-11-01"))


class FallBackFilter(unittest.TestCase):
    def test_the_list_names_only_files_the_checklist_reads(self):
        self.assertTrue(rc.read_by_checklist("v2/03-Manufacturing/ceiling/411302_P01_CEILING-SKIN-C2_DXF.dxf", BOM))
        self.assertTrue(rc.read_by_checklist("v2/01-CAD-Native/ceiling/410000_P01_CEILING_CAD.f3d", BOM))
        self.assertTrue(rc.read_by_checklist("v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv", BOM))   # the BOM reads it
        self.assertTrue(rc.read_by_checklist(BOM.REGISTER, BOM))
        self.assertFalse(rc.read_by_checklist("v2/07-Packaging/910000_P01_PACKAGING-PLAN_PKG.md", BOM))
        self.assertFalse(rc.read_by_checklist("v2/07-Packaging/910001_P01_PALLET-1-48X40_PKG.svg", BOM))

    def test_the_notes_leave_out_files_it_never_reads(self):
        skin = "v2/03-Manufacturing/ceiling/411302_P01_CEILING-SKIN-C2_DXF.dxf"
        BOM.FELL_BACK[:] = [("origin/air", skin), ("origin/air", "v2/07-Packaging/910000_P01_PACKAGING-PLAN_PKG.md")]
        try:
            notes = rc.fell_back_notes(BOM, {"origin/air": "PR #91"})
        finally:
            BOM.FELL_BACK.clear()
        self.assertEqual(notes, [f"`{skin}`: PR #91 changed it, but main changed it later"])


class Render(unittest.TestCase):
    def test_totals_count_each_number_once_and_name_the_screen(self):
        a = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16")], {}, tests=[("T06", "838001")])[1]
        b = run([row("838001", "buy", "HARDWARE - BOLT - M6 X 16", team="BASE")], {}, tests=[("T06", "838001")])[1]
        text = rc.render([], a + b, [], ["ELECTRICAL"], "this working tree", "locked", {}, rc.fai_plan(PLAN, BOM), "2026-11-01")
        self.assertIn("| BASE | 0 | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| WALL | 0 | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| **All, each number once** | 0 | 0 | 0 | 0 | 1 | 0 | 0 |", text)
        self.assertIn("| ELECTRICAL | — | — | — | — | — | — | — |", text)
        self.assertIn("**locked**", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
