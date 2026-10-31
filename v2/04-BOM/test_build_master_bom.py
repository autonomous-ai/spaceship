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
