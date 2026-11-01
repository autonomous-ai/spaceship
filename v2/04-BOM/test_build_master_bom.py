#!/usr/bin/env python3
"""Tests for build_master_bom.py: one planted fault per rule, plus the readers.

Doc code V2-BOM-003, revision P01. Standard library only.
Usage: python3 v2/04-BOM/test_build_master_bom.py
"""
import importlib.util
import sys
import unittest

sys.dont_write_bytecode = True
from pathlib import Path

spec = importlib.util.spec_from_file_location("bom", Path(__file__).with_name("build_master_bom.py"))
bom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bom)

FRONT = "v2/03-Manufacturing/front/360001_P01_FRONT-DOOR-UNIT_BOM.csv"
CEIL = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv"
CUT = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-TUBE-CUT-LIST_BOM.csv"
ELEC = "v2/03-Manufacturing/electrical/710000_P01_ELECTRICAL_BOM.csv"

FRONT_HDR = "part_number,name,name_vi,type,material,qty,unit_mass_kg,mass_status,status,source,note\n"
CEIL_HDR = "part_number,name,name_vi,kind,parent,qty_per_parent,qty_per_pod,material,mass_each_kg,mass_status,revision,status,source\n"
REGISTER = """# Joints register

### 2.1 Hardware set

| ID | Item | Data | Status |
|---|---|---|---|
| H-01 | **Bolt, stopped joints.** M6 x 16, ISO 4762 | data | DECIDED |
| H-09 | **Head washer.** ISO 7093 | data | DECIDED |

### Part numbers

| ID | Part number | Item | Qty per pod | Mass kg |
|---|---|---|---|---|
| H-01 | 830101 | Bolt M6 x 16 | 72 | 0.007 |
| H-09 | 830201 | Head washer 6.4 x 18 | 82 | 0.003 |
"""


def door(rows):
    return FRONT_HDR + "360001,FRONT - DOOR UNIT,Cụm cửa,assembly,-,1,50,calculation,DRAFT,x,\n" + rows


def run(sources):
    src = {p: (t, "test") for p, t in sources.items()}
    parts, skipped, register, reg_where = bom.build(src)
    fails, missing = bom.check(parts, register, reg_where)
    return parts, skipped, register, fails, missing


GOOD_DOOR = door("361001,FRONT - DOOR LEAF,Kính,made to drawing (glass supplier),4+4 laminated glass,1,43.9,calculation,DRAFT,x,\n"
                 "830101,BOLT M6 X 16,Bu lông,\"bought, captive\",steel 8.8 zinc plated,4,0.007,source,DRAFT,x,\n")


class Rules(unittest.TestCase):
    def test_clean_list_passes(self):
        _, _, register, fails, _ = run({FRONT: GOOD_DOOR, bom.REGISTER: REGISTER})
        self.assertEqual(fails, [])
        self.assertEqual({i["part_number"] for i in register}, {"830101", "830201"})

    def test_no_part_number_fails(self):
        _, _, _, fails, _ = run({FRONT: GOOD_DOOR + ",FRONT - MYSTERY PART,,made (cut),aluminium,1,1.0,calculation,DRAFT,x,\n", bom.REGISTER: REGISTER})
        self.assertTrue(any(f.startswith("no part number") for f in fails), fails)

    def test_duplicate_number_fails(self):
        other = door("361001,FRONT - SOMETHING ELSE,,made (cut),aluminium,1,1.0,calculation,DRAFT,x,\n")
        _, _, _, fails, _ = run({FRONT: GOOD_DOOR, FRONT.replace("360001_P01_FRONT-DOOR-UNIT", "360009_P01_X"): other, bom.REGISTER: REGISTER})
        self.assertTrue(any(f.startswith("duplicate number 361001") for f in fails), fails)

    def test_same_item_in_two_lists_is_not_a_duplicate(self):
        again = door("830101,BOLT M6 X 16,Bu lông,\"bought, captive\",steel,2,0.007,source,DRAFT,x,\n")
        _, _, _, fails, _ = run({FRONT: GOOD_DOOR, FRONT.replace("360001_P01_FRONT-DOOR-UNIT", "360002_P01_FIXED"): again, bom.REGISTER: REGISTER})
        self.assertFalse(any(f.startswith("duplicate") for f in fails), fails)

    def test_no_mass_fails(self):
        ceil = CEIL_HDR + "518001,LINING - CASSETTE CLIP - HOLD,,HOLD,cassette,6,12,HOLD envelope,HOLD,HOLD,P01,HOLD,D-47\n"
        _, _, _, fails, missing = run({CEIL: ceil, bom.REGISTER: REGISTER})
        self.assertTrue(any(f.startswith("no mass: 518001") for f in fails), fails)
        self.assertTrue(any("HOLD" in m for m in missing["CEILING"]), missing)

    def test_unregistered_hardware_fails(self):
        _, _, _, fails, _ = run({FRONT: door("368101,FRONT - DOOR HINGE - HOLD,,\"bought, HOLD\",not named,3,0.6,assumption,HOLD,x,\n"), bom.REGISTER: REGISTER})
        self.assertTrue(any(f.startswith("hardware with no joints-register row: 368101") for f in fails), fails)

    def test_electrical_parts_are_not_hardware(self):
        elec = "part_number,name,type,material,qty,unit_mass_kg,mass_status,status\n710001,ELECTRICAL - 12 V SUPPLY,bought,PSU,1,0.9,source,DRAFT\n"
        _, _, _, fails, _ = run({ELEC: elec, bom.REGISTER: REGISTER})
        self.assertEqual(fails, [])

    def test_reserved_number_fails(self):
        _, _, _, fails, _ = run({FRONT: door("350011,FRONT - OLD NUMBER,,made (cut),aluminium,1,1.0,calculation,DRAFT,x,\n"), bom.REGISTER: REGISTER})
        self.assertTrue(any(f.startswith("reserved old number 350011") for f in fails), fails)


class Readers(unittest.TestCase):
    def test_cut_list_is_skipped(self):
        _, skipped, _, _, _ = run({CUT: "frame,half,member,name,section,length_mm,qty,ends,status\n411101,C1,SIDE,SIDE,tube,1495,1,square,calc\n"})
        self.assertEqual([s[0] for s in skipped], [CUT])

    def test_a_cut_list_with_part_numbers_is_skipped_too(self):
        cut = "v2/03-Manufacturing/air/610000_P01_AIR-FLAT-CUT-LIST_BOM.csv"
        parts, skipped, _, fails, _ = run({cut: "part_number,name,size_mm,material\n611104,AIR - COLUMN FILL,30 x 180 x 2105,PET fill\n"})
        self.assertEqual(([s[0] for s in skipped], parts, fails), ([cut], [], []))

    def test_a_reserved_air_space_is_not_counted(self):
        dr = "v2/03-Manufacturing/front/350003_P01_FRONT-DECOR-BLOCK-ASSY-DR_BOM.csv"
        text = (FRONT_HDR + "350003,FRONT - DECOR BLOCK ASSY - DR,Khối DR,assembly,-,1,34.5,calculation,DRAFT,x,\n"
                "351403,FRONT - AIR TRANSITION - LOWER - DR,Ống,reserved air space (detail by AIR),-,1,1.5,assumption,DRAFT,x,\n"
                "351402,FRONT - AIR INTAKE RISER - DR,Ống,reserved air space,-,1,,,DRAFT,x,\n")
        parts, _, _, fails, _ = run({dr: text})
        self.assertEqual([p["part_number"] for p in parts], ["350003"])
        self.assertEqual(fails, [])
        self.assertEqual([r[0] for r in bom.RESERVED_SEEN], ["351403", "351402"])

    def test_unit_quantity_multiplies_children(self):
        twice = FRONT_HDR + "360001,FRONT - DOOR UNIT,,assembly,-,2,50,calculation,DRAFT,x,\n361001,FRONT - DOOR LEAF,,made (cut),glass,1,43.9,calculation,DRAFT,x,\n"
        parts, _, _, _, _ = run({FRONT: twice})
        leaf = next(r for r in parts if r["part_number"] == "361001")
        self.assertEqual(leaf["qty_per_pod"], 2.0)

    def test_qty_per_pod_column_wins(self):
        ceil = CEIL_HDR + "411301,CEILING - SKIN - COMMON,,MP,assy,1,2,\"ACP 3 mm EV3038\",6.3,calculation,P01,DRAFT,x\n"
        parts, _, _, _, _ = run({CEIL: ceil})
        self.assertEqual(parts[0]["qty_per_pod"], 2.0)
        self.assertEqual(parts[0]["make_buy"], "make")

    def test_finish_is_split_from_the_material(self):
        parts, _, _, _, missing = run({FRONT: door("361002,FRONT - DOOR KICK STRIP,,made (machined),\"aluminium EN AW-6082-T6, finish black anodised AA20\",1,2.1,calculation,DRAFT,x,\n")})
        strip = next(r for r in parts if r["part_number"] == "361002")
        self.assertEqual(strip["finish"], "black anodised AA20")
        self.assertFalse(any("no finish" in m for m in missing.get("FRONT", [])))

    def test_metal_with_no_finish_is_missing(self):
        _, _, _, _, missing = run({CEIL: CEIL_HDR + "411101,CEILING - PANEL FRAME - C1,,MP,assy,1,1,Aluminium 6063-T6,3.3,calculation,P01,DRAFT,x\n"})
        self.assertTrue(any("no finish" in m for m in missing["CEILING"]), missing)

    def test_team_with_no_list_is_missing(self):
        _, _, _, _, missing = run({FRONT: GOOD_DOOR, bom.REGISTER: REGISTER})
        self.assertIn("no parts list yet", missing["WALL"][0])
        self.assertNotIn("FRONT", [t for t, m in missing.items() if any("no parts list yet" in x for x in m)])

    def test_register_items_without_numbers_are_listed(self):
        reg = REGISTER.split("### Part numbers")[0]
        _, _, register, _, missing = run({bom.REGISTER: reg})
        self.assertEqual([i["id"] for i in register], ["H-01", "H-09"])
        self.assertEqual(len(missing["Joints register"]), 2)


WALL = "v2/03-Manufacturing/wall/210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv"
WALL_HDR = "level,part_number,name_en,name_vi,class,material,qty,unit,cut_length_mm,size_mm,mass_each_kg,mass_total_kg,status,source,notes\n"
REGISTER_V3 = """### 2.1 Hardware set

| ID | Item | Data | Status |
|---|---|---|---|
| H-01 | **Bolt, stopped joints.** M6 x 16 | data | DECIDED |
| H-04 | **Joint gasket.** PORON | data | source |

**Part numbers**

| Item | Part number | Name · Vietnamese | Class | Status |
|---|---|---|---|---|
| H-01 | **838001** | HARDWARE - SOCKET HEAD BOLT - M6 X 16 · Bulong | bought | PROPOSED |
| H-04 | **848001** | HARDWARE - JOINT GASKET - 8 X 3.97 · Gioang | bought by length | PROPOSED |
| H-04 | **848002** | HARDWARE - JOINT GASKET - 8 X 9.53 · Gioang | bought by length | PROPOSED |
"""


class WallAndRegisterV3(unittest.TestCase):
    def test_wall_classes_cut_rows_and_mass_totals(self):
        wall = WALL_HDR + (
            "0,210101,WALL - PANEL ASSY - SIDE LOWER - LH,,BS,see parts below,1,pc,,,,11.351,calculation,CAD,\n"
            "1,211101,WALL - PANEL FRAME - SIDE LOWER - LH,,MP,\"aluminium tube 20 x 40 x 1.2, finish mill (D-79)\",1,pc,,,3.307,3.307,calculation,CAD,\n"
            "2,,RAIL - BOTTOM (cut length),,cut,aluminium tube,1,pc,1489.74,,0.554,0.554,calculation,CAD,\n"
            "1,211501,WALL - CAVITY FILL - SIDE LOWER - LH,,MP,PET fill 40 mm,4,pc,,,,1.901,calculation,CAD,\n"
            "1,838001,CAPTIVE BOLT - M6 x 16,,PI,steel 8.8 zinc,7,pc,,,0.007,0.049,source,register H-01,\n")
        parts, _, _, fails, _ = run({WALL: wall, bom.REGISTER: REGISTER_V3})
        self.assertEqual(fails, [])
        by = {r["part_number"]: r for r in parts}
        self.assertEqual(by["210101"]["make_buy"], "assembly")          # BS is a bonded subassembly
        self.assertEqual(by["211101"]["make_buy"], "make")
        self.assertNotIn("", by)                                         # the cut row is not a BOM line
        self.assertAlmostEqual(by["211501"]["mass_each_kg"], 1.901 / 4)  # mass each from the total
        self.assertEqual(by["838001"]["make_buy"], "buy")

    def test_register_item_column_and_two_numbers_for_one_id(self):
        _, _, register, _, missing = run({bom.REGISTER: REGISTER_V3})
        self.assertEqual(sorted(i["part_number"] for i in register), ["838001", "848001", "848002"])
        self.assertEqual({i["id"] for i in register}, {"H-01", "H-04"})
        self.assertTrue(all(i["name"].startswith("HARDWARE") for i in register), register)
        self.assertNotIn("Joints register", missing)                     # every ID has a number

    def test_register_number_named_differently_is_not_a_duplicate(self):
        a = door("838001,BOLT M6 X 16,,bought,steel,4,0.007,source,DRAFT,x,\n")
        b = door("838001,CAPTIVE SOCKET SCREW M6,,bought,steel,2,0.007,source,DRAFT,x,\n")
        _, _, _, fails, _ = run({FRONT: a, FRONT.replace("360001_P01_FRONT-DOOR-UNIT", "360002_P01_FIXED"): b, bom.REGISTER: REGISTER_V3})
        self.assertFalse(any(f.startswith("duplicate") for f in fails), fails)

    def test_unnumbered_hardware_fails_once(self):
        wall = WALL_HDR + "1,,RIVNUT - M6,,PI,aluminium 5056,9,pc,,,0.004,0.036,source,register H-03,\n"
        _, _, _, fails, _ = run({WALL: wall, bom.REGISTER: REGISTER_V3})
        self.assertEqual(len(fails), 1, fails)
        self.assertTrue(fails[0].startswith("no part number"), fails)


REGISTER_V4 = REGISTER_V3 + """| H-05 | **831001** | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS · Chot | made | PROPOSED |
"""


class RegisterItems(unittest.TestCase):
    def fails_for(self, rows):
        _, _, _, fails, _ = run({WALL: WALL_HDR + rows, bom.REGISTER: REGISTER_V4})
        return fails

    def test_same_item_in_other_words_passes(self):
        rows = ("1,838001,CAPTIVE BOLT - M6 x 16 - ISO 4762 - 8.8 - ZINC,,PI,steel 8.8 zinc,7,pc,,,0.007,0.049,source,x,\n"
                "1,831001,LOCATING SPIGOT - D8 x M6 (H-05),,MP,stainless,2,pc,,,0.004,0.008,assumption,x,\n")
        self.assertEqual(self.fails_for(rows), [])

    def test_wrong_bolt_length_fails(self):
        f = self.fails_for("1,838001,BOLT - M6 x 25 - ISO 4762 - 8.8,,PI,steel,2,pc,,,0.009,0.018,source,x,\n")
        self.assertTrue(any(x.startswith("duplicate number 838001") for x in f), f)

    def test_old_gasket_size_on_a_new_number_fails(self):
        f = self.fails_for("1,848001,GASKET - PORON 4701-40 SOFT 3.18 x 10 WITH PSA,,PI,PORON,2.6,m,,,0.01,0.026,source,x,\n")
        self.assertTrue(any(x.startswith("duplicate number 848001") for x in f), f)

    def test_same_item_helper(self):
        self.assertTrue(bom.same_item("WASHER ISO 7093-1 6.4 x 18 x 1.6 A2", "HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2"))
        self.assertFalse(bom.same_item("RIVNUT - M6 - SHEREX CAH3-610-4.2", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC"))
        # a product name for a register item described by its requirement is the same item
        self.assertTrue(bom.same_item("BASE - BASE SEAL - FLOOR EDGE - PEMKO S88BL (HOLD)", "BASE - BASE SEAL - GAP 10 ±5"))
        # a different thread is a different item, however much else matches
        self.assertFalse(bom.same_item("HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE", "HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2"))
        # the old cassette-edge gasket is not the new soft seal
        self.assertFalse(bom.same_item("SEALS - CASSETTE EDGE GASKET - 10 X 3.18 - PSA FOAM", "SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN"))


class RefsAndPacking(unittest.TestCase):
    def test_an_untouched_old_copy_on_a_branch_does_not_override_the_first_ref(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            def g(*a):
                return subprocess.run(["git", "-C", d, "-c", "user.email=t@example.com", "-c", "user.name=t", *a],
                                      check=True, capture_output=True, text=True).stdout
            g("init", "-q")
            g("checkout", "-q", "-b", "main")
            reg = Path(d, bom.REGISTER)
            reg.parent.mkdir(parents=True)
            reg.write_text("register v1", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "v1")
            g("checkout", "-q", "-b", "team")
            lst = Path(d, "v2/03-Manufacturing/front/360001_P01_X_BOM.csv")
            lst.parent.mkdir(parents=True)
            lst.write_text("part_number\n", encoding="utf-8")
            g("add", "-A")
            g("commit", "-q", "-m", "team list")
            g("checkout", "-q", "main")
            reg.write_text("register v2", encoding="utf-8")
            g("commit", "-q", "-am", "v2")
            old = bom.ROOT
            bom.ROOT = Path(d)
            try:
                src = bom.load_sources(["main", "team"])
            finally:
                bom.ROOT = old
        self.assertEqual(src[bom.REGISTER][0], "register v2")              # main's newer register wins
        self.assertIn("v2/03-Manufacturing/front/360001_P01_X_BOM.csv", src)  # the branch's own list is read

    def test_a_stacked_branch_keeps_no_old_copy_of_a_list_main_merged_since(self):
        # AIR's branch sat on CEILING's PR; CEILING then squash-merged a newer list. Main's list wins until AIR
        # changes that list itself, later.
        import os
        import subprocess
        import tempfile
        ceil = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv"
        air = "v2/03-Manufacturing/air/610000_P01_AIR-PARTS-LIST_BOM.csv"
        with tempfile.TemporaryDirectory() as d:
            def g(*a, when="2026-11-01T00:00:00"):
                env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
                return subprocess.run(["git", "-C", d, "-c", "user.email=t@example.com", "-c", "user.name=t", *a],
                                      check=True, capture_output=True, text=True, env=env).stdout

            def put(path, text, msg, when):
                Path(d, path).parent.mkdir(parents=True, exist_ok=True)
                Path(d, path).write_text(text, encoding="utf-8")
                g("add", "-A")
                g("commit", "-q", "-m", msg, when=when)

            g("init", "-q")
            g("checkout", "-q", "-b", "main")
            put(bom.REGISTER, "register", "start", "2026-11-01T00:00:00")
            g("checkout", "-q", "-b", "ceiling")
            put(ceil, "part_number\n411301\n", "CEILING, first version", "2026-11-01T01:00:00")
            g("checkout", "-q", "-b", "air")
            put(air, "part_number\n611101\n", "AIR", "2026-11-01T02:00:00")
            g("checkout", "-q", "main")
            put(ceil, "part_number\n411301\n411302\n", "CEILING (#32), squash-merged", "2026-11-01T05:00:00")
            old = bom.ROOT
            bom.ROOT = Path(d)
            try:
                src = bom.load_sources(["main", "air"])
                g("checkout", "-q", "air")
                put(ceil, "part_number\n411301\n411302\n611999\n", "AIR edits CEILING's list", "2026-11-01T06:00:00")
                later = bom.load_sources(["main", "air"])
            finally:
                bom.ROOT = old
        self.assertIn("411302", src[ceil][0])                # main's merged list, not AIR's old copy
        self.assertTrue(src[ceil][1].startswith("main"), src[ceil][1])
        self.assertTrue(src[air][1].startswith("air"))       # AIR's own list is read
        self.assertIn("611999", later[ceil][0])              # AIR's own later change wins

    def test_a_rebase_keeps_the_author_time_and_a_dropped_branch_edit_is_named(self):
        # A rebase gives each commit a new committer time and keeps its author time: AIR's rebased copy of CEILING's
        # old list (authored 01:00, committed 06:00) still loses to CEILING's squash merge on main (05:00). And a
        # branch's own edit of the joints register, older than main's, falls back to main's copy and is listed.
        import os
        import subprocess
        import tempfile
        ceil = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv"
        with tempfile.TemporaryDirectory() as d:
            def g(*a, when="2026-11-01T00:00:00", committed=None):
                env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": committed or when}
                return subprocess.run(["git", "-C", d, "-c", "user.email=t@example.com", "-c", "user.name=t", *a],
                                      check=True, capture_output=True, text=True, env=env).stdout

            def put(path, text, when, committed=None):
                Path(d, path).parent.mkdir(parents=True, exist_ok=True)
                Path(d, path).write_text(text, encoding="utf-8")
                g("add", "-A", when=when)
                g("commit", "-q", "-m", path, when=when, committed=committed)

            g("init", "-q")
            g("checkout", "-q", "-b", "main")
            put(bom.REGISTER, "register v1", "2026-11-01T00:00:00")
            g("checkout", "-q", "-b", "air")
            put(ceil, "part_number\n411301\n", "2026-11-01T01:00:00", committed="2026-11-01T06:00:00")
            put(bom.REGISTER, "register v1, AIR's edit", "2026-11-01T02:00:00", committed="2026-11-01T06:00:00")
            g("checkout", "-q", "main")
            put(ceil, "part_number\n411301\n411302\n", "2026-11-01T05:00:00")
            put(bom.REGISTER, "register v2", "2026-11-01T05:30:00")
            old = bom.ROOT
            bom.ROOT = Path(d)
            bom.FELL_BACK.clear()
            try:
                src = bom.load_sources(["main", "air"])
                fell = list(bom.FELL_BACK)
                lines = bom.fell_back_lines({"air": "PR #91"}, keep=bom.wanted)
            finally:
                bom.ROOT = old
                bom.FELL_BACK.clear()
        self.assertIn("411302", src[ceil][0])               # main's merged list, by author time
        self.assertEqual(src[bom.REGISTER][0], "register v2")
        self.assertEqual(sorted(fell), [("air", ceil), ("air", bom.REGISTER)])
        self.assertEqual(len(lines), 2)
        self.assertTrue(any(x.startswith(f"`{bom.REGISTER}`: PR #91 changed it, but main changed it later") for x in lines), lines)

    def test_a_packing_list_adds_only_packaging_items(self):
        pk = ("label,part_number,name,name_vi,pallet,kg,kg_status,class\n"
              "1-01,111501,BASE - SEAL MAT - F1,,1,1.05,calculation,MP\n"
              "1-02,TBD (BASE),BASE - SEAL MAT - F2,,1,1.05,calculation,MP\n"
              "P-1,910001,PACKAGING - PALLET 48 X 40,,1,18.0,source,PI\n")
        parts, _, _, fails, _ = run({"v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv": pk})
        self.assertEqual([r["part_number"] for r in parts], ["910001"])
        self.assertEqual(parts[0]["mass_each_kg"], 18.0)
        self.assertEqual(fails, [])

    def test_a_packing_list_without_packaging_items_says_so(self):
        path = "v2/07-Packaging/910000_P01_PACKING-LIST_BOM.csv"
        pk = "label,part_number,name,kg\n1-01,111501,BASE - SEAL MAT - F1,1.05\n"
        src = {path: (pk, "test")}
        parts, skipped, register, reg_where = bom.build(src)
        _, missing = bom.check(parts, register, reg_where, [path])
        self.assertTrue(missing["Packing and Assembly"][0].startswith("no packaging items"), missing)


class NumberAllocation(unittest.TestCase):
    """D-120: the master BOM gives out frame-member and fill-piece numbers before a team's list uses them."""
    HDR = "part_number,name,name_vi,kind,team,parent,qty_per_parent,qty_per_pod,basis,status,note\n"
    ROW = ("412101,CEILING - FRAME SIDE MEMBER - C1,Trần trái - thanh cạnh của khung,MP,CEILING,411101,1,1,"
           "\"aluminium 20 x 40 x 1.2, 1455.00 long\",ALLOCATED,\n")

    def go(self, alloc, team_rows=""):
        sources = {bom.ALLOCATION: self.HDR + alloc}
        if team_rows:
            sources[CEIL] = CEIL_HDR + team_rows
        return run(sources)

    def test_a_free_number_is_a_master_row_with_no_mass(self):
        parts, _, register, fails, _ = self.go(self.ROW)
        self.assertEqual(fails, [])
        rows = [r for r in bom.master_rows(parts, register, {}) if r.get("row_type") == "allocated number"]
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["part_number"], r["group"], r["make_buy"], r["qty_per_pod"]), ("412101", "CEILING", "make", 1.0))
        self.assertIsNone(r.get("mass_each_kg"))
        self.assertIn("not in any parts list yet", r["note"])     # the mechanical check reads it as a placeholder
        self.assertEqual(r["name_vi"], "Trần trái - thanh cạnh của khung")
        pod = bom.master_rows(parts, register, {})[0]
        self.assertEqual(pod["mass_total_kg"], 0)                 # it adds no mass

    def test_a_team_using_it_for_the_same_item_takes_it(self):
        team = "412101,CEILING - FRAME SIDE MEMBER - C1,,MP,411101,1,1,aluminium 6063-T6,0.31,calculation,P01,DRAFT,list\n"
        parts, _, register, fails, _ = self.go(self.ROW, team)
        self.assertEqual(fails, [])
        self.assertFalse([r for r in bom.master_rows(parts, register, {}) if r.get("row_type") == "allocated number"])
        self.assertIn("| 412101 | CEILING - FRAME SIDE MEMBER - C1 | 411101 | 1 | in use |",
                      bom.report(parts, [], register, {}, fails, {}, {}, []))

    def test_a_team_using_it_for_another_item_fails(self):
        team = "412101,CEILING - SKIN - C1,,MP,410101,1,1,ACP 3 mm,6.2,calculation,P01,DRAFT,list\n"
        _, _, _, fails, _ = self.go(self.ROW, team)
        self.assertTrue(any(f.startswith("allocated number 412101") and "CEILING - SKIN - C1" in f for f in fails), fails)

    def test_a_cancelled_number_is_never_reused(self):
        team = "412101,CEILING - FRAME SIDE MEMBER - C1,,MP,411101,1,1,aluminium 6063-T6,0.31,calculation,P01,DRAFT,list\n"
        _, _, _, fails, _ = self.go(self.ROW.replace("ALLOCATED", "CANCELLED"), team)
        self.assertTrue(any(f.startswith("cancelled number 412101 used") for f in fails), fails)
        parts, _, register, fails2, _ = self.go(self.ROW.replace("ALLOCATED", "CANCELLED"))
        self.assertEqual(fails2, [])
        self.assertFalse([r for r in bom.master_rows(parts, register, {}) if r.get("row_type") == "allocated number"])

    def test_bad_rows_fail(self):
        bad = (self.ROW.replace("412101", "410501")                          # an assembly-band number for a made part
               + self.ROW.replace("412101", "211000")                       # a reserved old number (D-28)
               + self.ROW.replace("412101", "992101")                       # no such family
               + self.ROW + self.ROW                                        # allocated twice
               + self.ROW.replace("412101", "412102").replace("ALLOCATED", "TAKEN"))
        _, _, _, fails, _ = self.go(bad)
        for want in ("allocated 410501", "outside the MP band", "allocated 211000", "reserved old number",
                     "family 99 is not in conventions", "allocated twice", "status 'TAKEN'"):
            self.assertTrue(any(want in f for f in fails), (want, fails))

    def test_a_joints_register_number_is_never_given_out(self):
        # the register's H-01 renumbered 838001 here, so as a bought item it sits in its band and only the clash fires
        row = self.ROW.replace("412101", "838001").replace(",MP,", ",PI,")
        _, _, _, fails, _ = run({bom.ALLOCATION: self.HDR + row, bom.REGISTER: REGISTER.replace("830101", "838001")})
        self.assertEqual(fails, ["allocated 838001 'CEILING - FRAME SIDE MEMBER - C1': the joints register already has 838001 (H-01)"])

    def test_a_number_must_have_six_digits(self):
        for bad in ("41210", "4121011", "41210A"):
            _, _, _, fails, _ = self.go(self.ROW.replace("412101", bad))
            self.assertEqual(fails, [f"allocated {bad} 'CEILING - FRAME SIDE MEMBER - C1': not a 6-digit number"], bad)

    def test_the_kind_must_be_one_of_the_four(self):
        _, _, _, fails, _ = self.go(self.ROW.replace(",MP,", ",XX,"))
        self.assertEqual(fails, ["allocated 412101 'CEILING - FRAME SIDE MEMBER - C1': kind 'XX' is not MP, HS, BS or PI"])

    def test_the_real_list_is_clean(self):
        path = bom.ROOT / bom.ALLOCATION
        text = path.read_text(encoding="utf-8")
        alloc = bom.parse_allocation(text, "working tree")
        self.assertGreater(len(alloc), 0)
        self.assertEqual(len({a["part_number"] for a in alloc}), len(alloc))
        bom.ALLOCATED[:] = alloc
        try:
            fails = bom.check_allocation([], {})
        finally:
            bom.ALLOCATED.clear()
        self.assertEqual(fails, [])
        for a in alloc:
            self.assertTrue(a["name"] and a["name_vi"] and a["basis"] and a["parent"], a["part_number"])
            self.assertIn(a["team"], ("WALL", "CEILING"))


class FallBackReport(unittest.TestCase):
    """The files read from main over a branch's own edit: the report's section, its filter and the printed lines."""
    CEIL = "v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv"
    FELL = [("origin/air", CEIL), ("origin/air", "v2/03-Manufacturing/air/NOTES.md"),
            ("origin/air", "v2/07-Packaging/910000_P01_PACKAGING-PLAN_PKG.md")]

    def setUp(self):
        bom.FELL_BACK[:] = self.FELL

    def tearDown(self):
        bom.FELL_BACK.clear()

    def test_the_report_lists_only_the_lists_it_reads(self):
        text = bom.report([], [], [], {}, [], {}, {}, ["origin/main", "origin/air"])
        self.assertIn("Read from main although a branch changed them, because main changed them later:", text)
        self.assertIn(f"- `{self.CEIL}`: origin/air changed it, but main changed it later", text)
        self.assertNotIn("NOTES.md", text)                 # not a parts list: the BOM never reads it
        self.assertNotIn("PACKAGING-PLAN", text)           # a packing output, not the packing list

    def test_no_fallback_no_section(self):
        bom.FELL_BACK.clear()
        self.assertNotIn("Read from main although", bom.report([], [], [], {}, [], {}, {}, []))

    def test_main_prints_them(self):
        import contextlib
        import io
        out, old = io.StringIO(), bom.load_sources
        bom.load_sources = lambda refs: {}
        try:
            with contextlib.redirect_stdout(out):
                bom.main(["--no-write", "--ref", "origin/main", "--ref", "origin/air"])
        finally:
            bom.load_sources = old
        self.assertIn(f"  read from main: `{self.CEIL}`: origin/air changed it", out.getvalue())
        self.assertNotIn("NOTES.md", out.getvalue())

    def test_the_lines_are_printed(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            bom.print_fell_back({"origin/air": "PR #91"})
        self.assertEqual(out.getvalue().splitlines(),
                         [f"  read from main: `{self.CEIL}`: PR #91 changed it, but main changed it later, so main's copy is "
                          "read until that branch rebases"])


class FamilyRows(unittest.TestCase):
    def test_family_rows_have_vietnamese_names_and_sources(self):
        nodes = bom.node_names()
        self.assertEqual(nodes["110000"], ("BASE", "Đế / sàn"))
        rows = bom.master_rows([], [], nodes)
        for r in rows:
            if r["row_type"] in ("pod", "assembly") and r.get("group") != "HARDWARE WITH NO NUMBER":
                self.assertTrue(r.get("name_vi"), r["name"])
                self.assertTrue(r.get("source_file"), r["name"])
        pod = rows[0]
        self.assertEqual((pod["part_number"], pod["name_vi"]), ("100000", "Pod hoàn chỉnh"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
