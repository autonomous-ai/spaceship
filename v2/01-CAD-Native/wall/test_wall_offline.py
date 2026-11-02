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
    """A parameter expression as Fusion evaluates it: lengths in mm, angles ("deg") in radians, tan() on them."""
    py = re.sub(r"(\d)\s*mm\b", r"\1", expr)
    py = re.sub(r"(\d+(?:\.\d+)?)\s*deg\b", r"(\1 * pi / 180)", py)
    return eval(py, {"__builtins__": {}}, dict(vals, ceil=math.ceil, floor=math.floor, abs=abs, tan=math.tan,
                                               pi=math.pi))


# joints register V2-ENG-JNT-01 table 2.1 (main, PR #47): numbers and names of the hardware WALL models
def register_hw():
    """{part number: English name} of the joints register's hardware rows (| H-nn | **NNNNNN** | NAME · Vietnamese |),
    so WALL's hardware names are checked against the register itself."""
    path = os.path.join(HERE, "..", "..", "05-Engineering", "joints", "joints-register.md")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\|\s*H-\d+\s*\|\s*\*\*(\d{6})\*\*\s*\|\s*([^·|]+?)\s*·", line)
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


REGISTER_HW = register_hw()


class WallSidePanelTest(unittest.TestCase):

    def test_parameters_resolve_to_the_decided_sizes(self):
        v = resolve(load())
        self.assertEqual(v["wall_depth"], 1495)          # D-49
        self.assertAlmostEqual(v["side_h"], 1142.74)     # (2290 - 2 x 2.26) / 2, PM ruling on F-008
        self.assertEqual(v["tube_d"], 40)                # D-34: 20 x 40 x 1.2, behind the 3 mm bond line
        self.assertAlmostEqual(v["pnl_len"], 1492.74)    # 1495 less the decor seam gap
        self.assertAlmostEqual(v["frm_len"], 1486.74)    # less the 3 mm back return and its 3 mm bond line
        self.assertEqual(v["stile_n_mid"], 5)               # D-131 sample: 5 studs set from the bolts
        self.assertEqual([round(v["stud_c%d" % k], 2) for k in range(1, 6)], [270.0, 520.91, 746.37, 971.83, 1222.74])
        self.assertEqual(v["stile_pitch_max"], 300)         # PM 2026-11-01: the skin's 2 mm limit
        self.assertEqual(v["corner_w"], 40)
        self.assertAlmostEqual(v["stile_len"], 1102.74)
        self.assertAlmostEqual(v["side_jnt_pitch"], 351.37)  # 3 bolts, 220 from each end of 1142.74 (R-J14)
        self.assertAlmostEqual(v["len_bolt_pitch"], 350.913, places=3)  # 220 from the ends, 4 even (R-J14)
        self.assertEqual(v["access_d"], 19)              # FR-03: passes the 18 mm head washer
        self.assertEqual(v["bolt_line_y"], 824)          # R-J15: back panel tube centre
        self.assertEqual(v["bolt_d"], 7)                 # PM ruling on F-009
        self.assertEqual(v["tube_t"], 1.2)               # Joints' gauges (PM 05:29): side rails and front stiles
        self.assertEqual(v["corner_t"], 1.0)             # the 40 x 40 members
        self.assertEqual(v["stud_t"], 0.8)               # the studs
        self.assertEqual(v["plate_t"], 2)                # the mitre plate (Joints' corner detail)
        self.assertEqual(resolve(load_back("B1"))["tube_t"], 1.0)   # back perimeters
        self.assertAlmostEqual(v["rivnut_head_t"] + v["stopw_t"], v["seam_gap"])   # the 2.26 metal stop (R-J5)
        # the spigot is Joints' 831001 STEP (F-189): its pin top stands where WALL's rule puts it, and its M6 stud
        # stays inside the rivnut below its origin on the rivnut head
        sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools", "checks"))
        import stepfile
        sf = stepfile.StepFile(os.path.join(HERE, "..", "..", "03-Manufacturing", "joints",
                                            "831001_P01_HARDWARE-LOCATING-SPIGOT_STEP.step"))
        zs = [p[2] for i in sf.instances() for p in sf.solid(i["solid"]).points()]
        self.assertAlmostEqual(max(zs), v["spigot_proud"] - v["rivnut_head_t"], places=2)
        self.assertLess(-min(zs), v["rivnut_len"] + v["rivnut_head_t"])
        self.assertEqual(v["tray_h"], 34)                # returns the full cassette depth, lips hold the felt
        self.assertEqual(v["gap_h"], 24)                 # air gap behind the felt (D-17's 25 less the lip sheet)
        self.assertAlmostEqual(v["cass_len"], 1445)      # decor back plate to past the back cassette's face (D-57)
        r = resolve(load("cassette", "R", "1"))           # the right side starts at Y -640, clear of DR's panel
        self.assertAlmostEqual(r["pod_d"] / 2 - r["wall_depth"] + r["lin_front_dy"], -640.0)
        self.assertAlmostEqual(r["cass_len"], 1440)
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

    def test_ceiling_rivnuts_follow_the_ceiling_edge(self):
        v = resolve(load(row="2"))
        ys = [850 - v["wall_depth"] + v["bolt_edge"] + i * v["ceil_bolt_pitch"] for i in range(int(v["n_len_bolt"]))]
        for got, want in zip(ys, [-425.0, -73.33, 278.33, 630.0]):      # register 2.9, PM ruling 16:55
            self.assertAlmostEqual(got, want, delta=0.01)

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

    def side_bays(self, v):
        """Clear bays (mm) between the front stile, the studs and the 40 x 40 back stile."""
        faces = [20.0] + [v["stud_c%d" % k] + d * 10.0 for k in range(1, int(v["stile_n_mid"]) + 1) for d in (-1, 1)] + \
            [v["frm_len"] - 40.0]
        return [faces[i + 1] - faces[i] for i in range(0, len(faces), 2)]

    def test_stud_layout_holds_when_the_wall_depth_changes(self):
        """The studs follow the bolts: every clear bay within the skin's 2 mm limit (275 or less) and not pinched,
        over the edit test's depths and beyond."""
        ns = load()
        for depth in (1300, 1400, 1495, 1550):
            vals = resolve(ns, override={"wall_depth": depth})
            bays = self.side_bays(vals)
            self.assertLessEqual(max(bays), 275.0, (depth, bays))
            self.assertGreater(min(bays), 100.0, (depth, bays))

    def test_every_bolt_is_30_clear_of_every_stile(self):
        """R-J14: every bolt along the panel at least 30 mm from any stile face (the 60 mm key pocket fits)."""
        v = resolve(load())
        y0 = 0.0                                          # panel front end
        stiles = [(y0, y0 + 20)] + [(y0 + v["stud_c%d" % k] - 10, y0 + v["stud_c%d" % k] + 10)
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
                    self.assertTrue(pn not in seen or (name.endswith("- COMMON") and seen[pn] == name), "%s used twice" % pn)
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
            self.assertEqual(v["stile_n_mid"], 3)                       # PM 2026-11-01: 3 studs, the skin's 2 mm
            self.assertAlmostEqual(v["stile_pitch"], 294.75, places=2)
            self.assertAlmostEqual(v["len_bolt_pitch"], 253.0, places=2)   # register 2.9: 220, 473, 725.99, 978.99
            self.assertAlmostEqual(v["side_jnt_pitch"], 339.31, delta=0.01)  # register 2.9: 220, 559.31, 898.61
            self.assertAlmostEqual(v["cass_len"], 1164.87, places=2)    # side lining face to 1.13 short of X 0
            self.assertEqual(v["stud_t"], 0.8)                         # D-131 start value, Joints' check
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
                self.assertTrue(pn not in seen or (name.endswith("- COMMON") and seen[pn] == name), "%s used twice" % pn)
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

    def test_bolt_lines_match_the_skeleton(self):
        """WALL's own formulas give the skeleton's bolt lines (skeleton v4, #94): drift fails here."""
        params = list(load()["skeleton_params"](REPO))
        if "ceil_side_pitch" not in [q[0] for q in params]:
            self.skipTest("skeleton before v4")
        sk = {}
        for _pass in range(3):                       # the skeleton's own order, a few passes for forward names
            for name, expr, _u, _st, _src in params:
                if name not in sk:
                    try:
                        sk[name] = evaluate(expr, sk)
                    except NameError:
                        pass
        side, back = resolve(load(row="2")), resolve(load_back("B3"))
        self.assertAlmostEqual(side["ceil_bolt_pitch"], sk["ceil_side_pitch"], places=3)
        self.assertAlmostEqual(850 - side["wall_depth"], sk["ceil_side_y0"], places=3)
        self.assertAlmostEqual(side["len_bolt_pitch"], sk["side_base_pitch"], places=3)
        self.assertAlmostEqual(back["len_bolt_pitch"], sk["back_base_pitch"], places=3)
        self.assertAlmostEqual(back["len_bolt_pitch"], sk["ceil_back_pitch"], places=3)

    def test_back_parameters_have_status_and_source(self):
        for pos in ("B1", "B4"):
            ns = load_back(pos)
            for name, expr, unit, status, source in ns["WALL_PARAMS"]:
                self.assertIn(status, ("confirmed", "source", "calculation", "assumption", "unverified"), name)
                self.assertTrue(source, name)


# ELECTRICAL P01 (electrical_model.py, PR #64) with the PM's final sizes of 2026-10-31 20:38 UTC: where its
# features sit in the right linings (mm)
EL_SIDE_EXPECT = {"1": {"el_y_kit": 240.5, "el_y_fx": -312.0, "el_z_fx": 1162.5, "el_fx_d": 32.0, "el_trunk_z": 1100.0, "el_kit_d": 60.0,
                        "el_fs_y0": 2.0, "el_fs_y1": 20.0, "el_fs_dz": 60.0, "el_kit_dz": 80.0},
                  "2": {"el_call_y": -209.5, "el_call_z": 1450.0, "el_shelf_z": 2250.0, "el_grm_s": 12.0}}


class ElectricalInterfaceSideTest(unittest.TestCase):

    def test_side_values_match_electrical(self):
        for row, want in EL_SIDE_EXPECT.items():
            v = resolve(load("cassette", "R", row))
            for k, x in want.items():
                self.assertAlmostEqual(v[k], x, places=3, msg=k)

    def test_only_the_right_cassettes_carry_them(self):
        for part, side, row in (("cassette", "L", "1"), ("cassette", "L", "2"), ("panel", "R", "1"),
                                ("frame", "R", "2"), ("skin", "R", "1")):
            ns = load(part, side, row)
            self.assertEqual([q[0] for q in ns["WALL_PARAMS"] if q[0].startswith("el_")], [], (part, side, row))

    def test_felt_openings_stay_inside_the_felt_before_and_after_the_edit_test(self):
        """As built and under the edit test's skeleton edit (wall_depth 1300, side_h 1120), every felt opening
        lies inside its felt with 1 mm round it (the build refuses otherwise)."""
        for row in ("1", "2"):
            for over in (None, {"wall_depth": 1300.0, "side_h": 1120.0}):
                v = resolve(load("cassette", "R", row), over)
                fy = (850.0 - v["wall_depth"] + v["lin_front_dy"] + 1.5, v["pod_d"] / 2 - v["stack_t"] + v["cass_t"] - 1.5)
                z0 = v["panel_z0"] + (0.0 if row == "1" else v["side_h"] + v["seam_gap"])
                z1 = v["panel_z0"] + v["side_h"] if row == "1" else v["pod_h"] - v["outer_t"] - v["lin_gap"]
                fz = (z0 + 1.5, z1 - 1.5)
                if row == "1":
                    yb = v["pod_d"] / 2 - v["stack_t"]
                    boxes = {"FS-CNR": (yb + v["el_fs_y0"], yb + v["el_fs_y1"], v["el_trunk_z"] - v["el_fs_dz"],
                                        v["el_trunk_z"] + v["el_fs_dz"])}
                    holes = {"FA-KIT": (v["el_y_kit"], v["el_trunk_z"] + v["el_kit_dz"], v["el_kit_d"]),
                             "FX-COL": (v["el_y_fx"], v["el_z_fx"], v["el_fx_d"])}
                else:
                    boxes = {}
                    holes = {"FX-CALL0": (v["el_call_y"], v["el_shelf_z"], v["el_grm_s"]),
                             "FX-CALL2": (v["el_call_y"], v["el_call_z"], v["el_grm_s"])}
                for k, (y, z, d) in holes.items():
                    boxes[k] = (y - d / 2, y + d / 2, z - d / 2, z + d / 2)
                for k, (y0, y1, za, zb) in boxes.items():
                    self.assertTrue(fy[0] + 1 <= y0 and y1 <= fy[1] - 1 and fz[0] + 1 <= za and zb <= fz[1] - 1,
                                    "%s row %s %s: %s not inside %s %s" % (k, row, over, (y0, y1, za, zb), fy, fz))


# B2 and B4 (ELECTRICAL P01, PR #64; the PM's rulings of 2026-10-31 20:38 to 21:20 UTC)
EL_BACK_EXPECT = {("B2", "cassette"): {"el_cut_x0": 91.0, "el_cut_x1": 395.0, "el_cut_z0": 866.0, "el_cut_z1": 1134.0,
                                       "el_lt_x": 346.0, "el_y_bg": 787.5, "el_y_xc": 781.5, "el_grm_d": 19.1},
                  ("B4", "cassette"): {"el_lt_x": 346.0, "el_shelf_z": 2250.0, "el_ceil_x": 583.0, "el_ceil_z": 2330.0,
                                       "el_grm_s": 12.0, "el_shelf_d": 16.0},
                  # ELECTRICAL's B2 inputs (2026-11-01): the jack moved to X 170 for 50 from the mains everywhere; the
                  # mains passage moved to X 127 (17:47 UTC); the bend room: the mains jog from Z 750 to X 137, the LAN
                  # band Z 391 to 440 (18:05 UTC)
                  ("B2", "panel"): {"el_inlet_x": 120.0, "el_inlet_z": 313.0, "el_lan_x": 170.0, "el_lan_z": 375.0,
                                    "el_inlet_d": 24.0, "el_cut_x0": 91.0, "el_cut_z0": 866.0, "el_cut_z1": 1134.0,
                                    "el_ps_mains_x": 127.0, "el_ps_lan_x": 207.0, "el_rn_xl1": 160.0, "el_rn_xu1": 110.0,
                                    "el_ch_jog_z": 750.0, "el_ch_jog_x1": 137.0, "el_ch_l_band": 49.0}}


class ElectricalInterfaceBackTest(unittest.TestCase):

    def resolved(self, pos, part, over=None):
        ns = load_back(pos, part)
        if not any(q[0].startswith("el_") for q in ns["WALL_PARAMS"]):
            self.skipTest("this branch's back builder has no ELECTRICAL features yet")
        return resolve(ns, over)

    def test_back_values_match_electrical(self):
        for (pos, part), want in EL_BACK_EXPECT.items():
            v = self.resolved(pos, part)
            for k, x in want.items():
                self.assertAlmostEqual(v[k], x, places=3, msg="%s %s %s" % (pos, part, k))

    def test_only_b2_and_b4_carry_them(self):
        for pos, part in (("B1", "cassette"), ("B3", "cassette"), ("B1", "panel"), ("B4", "panel"), ("B1", "frame")):
            ns = load_back(pos, part)
            self.assertEqual([q[0] for q in ns["WALL_PARAMS"] if q[0].startswith("el_")], [], (pos, part))
        # B2's frame carries the unit (the Lead's approval of WALL's B2 frame, 2026-11-01): only its fixings' names
        ns = load_back("B2", "frame")
        self.assertEqual(sorted(q[0] for q in ns["WALL_PARAMS"] if q[0].startswith("el_")),
                         sorted(("el_pu_zc", "el_pu_h") + ns["B2_FRAME_EL"]))

    def test_b2_unit_sits_on_its_cross_members(self):
        """D-131's first stud is behind the unit, so two cross members from the centre stile to the second stud carry
        it, a rivnut head (0.76) off its bottom and top (ELECTRICAL: the unit sits on the heads); the unit, its 4 rivnuts
        and both passages lie on the members, clear of their welded ends; the top-front clip zone lies on the stub."""
        v = self.resolved("B2", "panel")
        x_lo, x_hi = v["close_gap"] / 2 + v["tube_w"], v["close_gap"] / 2 + 2 * v["stile_pitch"]
        self.assertAlmostEqual(x_hi - x_lo, 569.5, delta=0.01)
        u0, u1 = v["el_pu_zc"] - v["el_pu_h"] / 2, v["el_pu_zc"] + v["el_pu_h"] / 2
        self.assertAlmostEqual(v["xm_z0"] + v["tube_w"] + v["rivnut_head_t"], u0, places=6)
        self.assertAlmostEqual(v["xm_z1"] - v["tube_w"] - v["rivnut_head_t"], u1, places=6)
        self.assertAlmostEqual(v["xm_z0"], 849.24, delta=0.005)
        self.assertAlmostEqual(v["xm_z1"], 1150.76, delta=0.005)
        c = self.resolved("B2", "cassette")                               # the unit's X lives in the cassette's list
        self.assertGreater(c["el_pu_x0"] - x_lo, 50)                       # the closing seam's pin bolt access
        self.assertGreater(x_hi - (c["el_pu_x0"] + c["el_pu_w"]), 150)
        holes = [(v["el_rn_xl1"], v["rivnut_d"]), (v["el_rn_xl2"], v["rivnut_d"]),
                 (v["el_ps_mains_x"], v["el_ps_mains_dt"]), (v["el_ps_lan_x"], v["el_ps_lan_dt"])]
        for x, d in holes + [(v["el_rn_xu1"], v["rivnut_d"]), (v["el_rn_xu2"], v["rivnut_d"])]:
            self.assertGreater(x - d / 2 - x_lo, 10)
            self.assertGreater(x_hi - x - d / 2, 10)
        holes.sort()
        # the lower member's top wall: a ligament of at least one rivnut hole (Ø10) between hole edges (assumption);
        # 18 between the mains passage and the first rivnut since ELECTRICAL moved the passage to X 127
        for (xa, da), (xb, db) in zip(holes, holes[1:]):
            self.assertGreaterEqual(xb - db / 2 - (xa + da / 2), v["rivnut_d"], (xa, xb))
        # and a rivnut's head (CAL2-610-4.2: Ø12.95 at most, D-163) sits flat, clear of each passage's edge
        for xr in (v["el_rn_xl1"], v["el_rn_xl2"]):
            for xp, dp in ((v["el_ps_mains_x"], v["el_ps_mains_dt"]), (v["el_ps_lan_x"], v["el_ps_lan_dt"])):
                self.assertGreater(abs(xr - xp) - 12.95 / 2 - dp / 2, 10, (xr, xp))
        # the first stud (below the unit) stays clear of the passages under the lower member
        stud = (v["close_gap"] / 2 + v["stile_pitch"], v["close_gap"] / 2 + v["stile_pitch"] + v["tube_w"])
        for x, d in ((v["el_ps_mains_x"], v["el_ps_mains_db"]), (v["el_ps_lan_x"], v["el_ps_lan_db"])):
            self.assertGreater(stud[0] - (x + d / 2), 50)
        z_top = c["panel_z0"] + c["back_ph"]
        zone = (z_top - c["clip_top_dz"] - c["clip_zone_h"] / 2, z_top - c["clip_top_dz"] + c["clip_zone_h"] / 2)
        stub = (c["xm_z1"], z_top - c["top_h"])
        self.assertGreaterEqual(zone[0], stub[0] - 1e-6)
        self.assertLessEqual(zone[1], stub[1] + 1e-6)
        self.assertGreater(zone[0] - c["el_cut_z1"], 15)                   # clear of the tray's unit cut-out

    def test_b2_fill_cut_keeps_the_cables_apart(self):
        """B2's fill cut behind the skin (ELECTRICAL's envelopes and channels, 2026-11-01): the mains side of the cut
        (the cleared strip and its jog) stays 50 or more from the LAN side (the band along the jack's top and its channel
        up to the passage), as ELECTRICAL's rule asks; the jack sits right of the inlet's box; and each cable has room
        for its bend (ELECTRICAL's bend check, 2026-11-01 18:05 UTC)."""
        ns = load_back("B2", "panel")
        v = resolve(ns)
        cuts = {lab: [evaluate(e, v) for e in xr + zr] for lab, xr, zr in ns["B2_CUTS"]}
        mains_right = max(cuts["MAINS CHANNEL"][1], cuts["MAINS JOG"][1])
        band = dict((lab, [evaluate(e, v) for e in xr + zr]) for lab, xr, zr in ns["B2_ISLAND_NOTCHES"])["LAN BAND"]
        self.assertGreaterEqual(band[0] - cuts["MAINS CHANNEL"][1], 50.0)                # at the band (62)
        self.assertGreaterEqual(v["el_ps_lan_x"] - v["el_ch_l_w"] / 2 - mains_right, 50.0)   # at the jog (62)
        self.assertGreater(v["el_lan_x"] - v["el_jack_h"], v["el_inlet_x"] + v["el_box_r"])  # the jack clear of the box
        # ELECTRICAL's numbers: the jog from Z 750 to X 137, the band Z 391 to 440
        self.assertAlmostEqual(cuts["MAINS JOG"][2], 750.0, places=6)
        self.assertAlmostEqual(cuts["MAINS JOG"][1], 137.0, places=6)
        self.assertAlmostEqual(cuts["MAINS CHANNEL"][3], 750.0, places=6)
        self.assertAlmostEqual(band[2], 391.0, places=6)
        self.assertAlmostEqual(band[3], 440.0, places=6)
        # the mains cord's S-bend (two equal arcs) from its channel's middle up to the passage: 4 x its 9.2 diameter,
        # 37 (Southwire's SJEOOW 14/3 sheet, via ELECTRICAL), fits in the jog's height
        d, h = v["el_ps_mains_x"] - (v["el_ch_m_x1"] - 10.0), cuts["MAINS JOG"][3] - cuts["MAINS JOG"][2]
        self.assertGreaterEqual(((h / 2) ** 2 + (d / 2) ** 2) / d, 4 * 9.2)
        # the Cat6's S-bend at 4 x its diameter, 24, from the jack's centre over to its riser's, fits in the band
        d, r = v["el_ps_lan_x"] - v["el_lan_x"], 24.0
        self.assertLessEqual(2 * (r ** 2 - (r - d / 2) ** 2) ** 0.5, band[3] - band[2])

    def test_b2_frame_members_and_bays(self):
        """B2's frame: the perimeter, studs 2 and 3, and the four members round the unit, each with a number key the
        allocation's names reach; its fill: bays 1 and 2 split below and above the unit, then bays 3 and 4."""
        ns = load_back("B2", "panel")
        for key in ("CROSS - LOWER", "CROSS - UPPER", "STUD - BELOW UNIT", "STUD - STUB"):
            self.assertIn(key, ns["MEMBER_WORDS"])
        words = sorted(ns["MEMBER_WORDS"].values(), key=len)
        for i, w in enumerate(words):        # a longer word that holds a shorter one is matched first (longest wins)
            for w2 in words[i + 1:]:
                if w in w2:
                    self.assertGreater(len(w2), len(w))

    def test_openings_stay_inside_through_the_edit_test(self):
        """As built and under the back edit (pod_w 2300, back_ph 1080): the cut-out lies 30 inside B2-CASS and
        under its top lip; B4's felt holes lie inside its felt, FX-CEIL 2 under the top lip."""
        edit = {"pod_w": 2300.0, "half_pw": 1100.61, "half_fw": 1098.99, "back_ph": 1080.0}
        for over in (None, edit):
            v = self.resolved("B2", "cassette", over)
            top, x_end = v["panel_z0"] + v["back_ph"], v["pod_w"] / 2 - v["stack_t"]
            self.assertTrue(v["seam_gap"] / 2 + 30 <= v["el_cut_x0"] and v["el_cut_x1"] <= x_end - 30, over)
            self.assertTrue(v["panel_z0"] + 30 <= v["el_cut_z0"] and v["el_cut_z1"] <= top - v["lip_w"] - 30, over)
            w = self.resolved("B4", "cassette", over)
            lip = w["pod_h"] - w["outer_t"] - w["lin_gap"] - w["lip_w"]
            self.assertAlmostEqual(lip - (w["el_ceil_z"] + w["el_grm_s"] / 2), 2.0, places=6)
            felt_x = (w["seam_gap"] / 2 + 1.5, w["pod_w"] / 2 - w["stack_t"] - 1.5)
            for x, d in ((w["el_ceil_x"], w["el_grm_s"]), (w["el_lt_x"], w["el_shelf_d"])):
                self.assertTrue(felt_x[0] + 1 <= x - d / 2 and x + d / 2 <= felt_x[1] - 1, (over, x))

    def test_front_plate_band_is_clear_of_the_lips(self):
        """ELECTRICAL's front plate covers the felt edge by 8 all round: that band stays clear of B2-CASS's lips."""
        v = self.resolved("B2", "cassette")
        self.assertGreater(v["el_cut_x0"] - 8, v["seam_gap"] / 2 + v["lip_w"])
        self.assertLess(v["el_cut_z1"] + 8, v["panel_z0"] + v["back_ph"] - v["lip_w"])
        self.assertGreater(v["el_cut_z0"] - 8, v["panel_z0"] + v["lip_w"])


class PolygonPlanTest(unittest.TestCase):
    """poly_plan: straight sides get their constraint and each tied group of corners one dimension, so a sketch is
    fully constrained with nothing repeated (the L1 run of 2026-11-01 failed on a repeated dimension)."""

    def plan(self):
        return load("panel", "L", "1")["poly_plan"]

    def test_mitre_triangle(self):
        sides, dims = self.plan()([(-2.0, -2.0), (-2.0, 22.0), (22.0, 22.0)],
                                  [("ya", "za"), ("ya", "zc"), ("yc", "zc")])
        self.assertEqual(sides, [(0, "V"), (1, "H")])
        self.assertEqual(dims, [(0, "x", "ya"), (0, "y", "za"), (1, "y", "zc"), (2, "x", "yc")])
        self.assertEqual(len(sides) + len(dims), 2 * 3)          # 3 corners, 2 degrees of freedom each

    def test_slanted_triangle_and_rectangle(self):
        plan = self.plan()
        sides, dims = plan([(0.0, 0.0), (1.0, 0.5), (0.3, 2.0)], [("a", "b"), ("c", "d"), ("e", "f")])
        self.assertEqual((sides, len(dims)), ([], 6))
        sides, dims = plan([(0.0, 0.0), (5.0, 0.0), (5.0, 3.0), (0.0, 3.0)],
                           [("x0", "y0"), ("x1", "y0"), ("x1", "y1"), ("x0", "y1")])
        self.assertEqual(len(sides) + len(dims), 2 * 4)
        self.assertEqual([d[2] for d in dims], ["x0", "y0", "x1", "y1"])

    def test_tied_corners_must_share_their_expression(self):
        with self.assertRaises(ValueError):
            self.plan()([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0)], [("a", "b"), ("a2", "c"), ("d", "c")])


class FillPiecesInThePanelTest(unittest.TestCase):
    """D-123: the panels' fill numbers are cancelled; the pieces go straight into the panel assembly."""

    def test_no_fill_part_or_number(self):
        with self.assertRaises(ValueError):
            load("fill", "L", "1")
        ns = load("panel", "L", "1")
        self.assertNotIn("fill", ns["PARTS"])
        self.assertIn("fill", ns["WANT"]["panel"])

    def test_every_bay_gets_its_allocated_number(self):
        """A real build takes each bay's number from the allocation by form and size; a size written "240.0" in
        FILL-PIECES.csv must still find "F01 240 X 1102.7" (dry run 8 left F01 and F04 unnumbered)."""
        import csv
        ns = load("panel", "L", "1")
        rows = list(csv.DictReader(open(os.path.join(REPO, "v2/03-Manufacturing/wall/FILL-PIECES.csv"),
                                        encoding="utf-8")))
        for code in sorted({r["position"] for r in rows}):
            # a form whose number isn't allocated yet has none in the list: its bays get none (a real build stops)
            want = {int(r["bay"]): r["number"] for r in rows if r["position"] == code and r["number"]}
            got = ns["fill_numbers"](REPO, code)
            self.assertEqual({b: v[0] for b, v in got.items()}, want, code)
            for bay, (pn, name, vn) in got.items():
                self.assertIn(" FILL PIECE ", name, (code, bay))
                self.assertTrue(vn, (code, bay))


class FillDxfTest(unittest.TestCase):
    """D-128: each fill-piece form is cut from its own DXF (make_fill_pieces.py); the DXFs match the CAD."""

    def mf(self):
        sys.path.insert(0, os.path.join(HERE, "..", "..", "03-Manufacturing", "wall"))
        import make_fill_pieces
        return make_fill_pieces

    def test_outline_shapes(self):
        mf = self.mf()
        notch = mf.outline(100, 50, [(0, 10, 10, 20)])               # a notch in the left edge
        self.assertEqual((len(notch), len(notch[0])), (1, 8))
        self.assertAlmostEqual(sum(mf.area(lp) for lp in notch), 5000 - 100)
        hole = mf.outline(100, 50, [(40, 60, 20, 30)])              # an opening inside: a second, clockwise loop
        self.assertEqual([len(lp) for lp in hole], [4, 4])
        self.assertLess(mf.area(hole[1]), 0)
        merged = mf.outline(100, 50, [(80, 100, 10, 40), (70, 90, 20, 30)])   # overlapping openings merge
        self.assertEqual((len(merged), len(merged[0])), (1, 12))
        self.assertAlmostEqual(sum(mf.area(lp) for lp in merged), 5000 - mf.open_area(100, 50, [(80, 100, 10, 40),
                                                                                              (70, 90, 20, 30)]))
        with self.assertRaises(ValueError):                         # openings touching at a corner only
            mf.outline(100, 50, [(20, 30, 20, 30), (30, 40, 30, 40)])
        with self.assertRaises(ValueError):                         # a cut right across: two pieces
            mf.outline(100, 50, [(40, 60, 0, 50)])

    def test_labels_follow_the_shape(self):
        """A form keeps its label (and so its number) while its shape stays, and a new form takes the next free
        label: in (panel, bay) order, R1's sixth stud put two new forms between L1's and L2's, and every later label
        found another form's number at the same size."""
        mf = self.mf()

        def pc(panel, bay, w, pockets=()):
            return {"panel": panel, "bay": bay, "w": w, "h": 1000.0, "pockets": sorted(pockets)}
        a, b, c = pc("210101", 1, 240.0, [(0.0, 60.0, 0.0, 60.0)]), pc("210103", 1, 230.9), pc("210102", 6, 100.0)
        groups = {mf.form_key(x): [x] for x in (a, b, c)}
        prev = {"F01": (mf.form_key(a), "211515", tuple(a["pockets"])), "F02": (mf.form_key(b), "211516", ())}
        got = [(f, m[0]["w"]) for f, _k, m in mf.label_forms(groups, prev, {"F02": [], "F03": []})]
        # c sorts between a and b by panel, but takes F04: after the last list's labels and the live F03
        self.assertEqual(got, [("F01", 240.0), ("F02", 230.9), ("F04", 100.0)])

    def test_an_unnumbered_form_recut_keeps_its_label(self):
        """A form not yet numbered (no allocation row, no DXF) whose pieces are re-cut in the same bays keeps its label,
        as B2's F19 and F22 did when ELECTRICAL moved the mains passage and widened the bend room (2026-11-01); a
        numbered form never does (a new shape is a new form), nor one re-cut into other bays."""
        mf = self.mf()

        def pc(pos, bay, w, pockets=()):
            return {"panel": "2102%02d" % int(pos[1]), "position": pos, "bay": bay, "w": w, "h": 717.0,
                    "pockets": sorted(pockets)}
        old19, new19 = pc("B2", 1, 274.7, [(0.0, 100.2, 677.0, 717.0)]), pc("B2", 1, 274.7, [(0.0, 114.2, 617.8, 717.0)])
        old22, new22 = pc("B2", 7, 99.0, [(0.0, 23.0, 418.2, 458.2)]), pc("B2", 7, 99.0, [(0.0, 37.0, 359.0, 458.2)])
        num, renum = pc("B1", 1, 274.7, [(0.0, 60.0, 0.0, 60.0)]), pc("B1", 1, 274.7, [(0.0, 70.0, 0.0, 60.0)])
        prev = {"F09": (mf.form_key(num), "211614", tuple(num["pockets"]), {("B1", 1)}),
                "F19": (mf.form_key(old19), "", tuple(old19["pockets"]), {("B2", 1)}),
                "F22": (mf.form_key(old22), "", tuple(old22["pockets"]), {("B2", 7)})}
        groups = {mf.form_key(x): [x] for x in (new19, new22, renum)}
        got = {m[0]["position"] + str(m[0]["bay"]): f for f, _k, m in mf.label_forms(groups, prev, {"F09": []})}
        self.assertEqual(got, {"B21": "F19", "B27": "F22", "B11": "F23"})
        # re-cut into another bay: a new label
        moved = pc("B2", 2, 274.7, [(0.0, 114.2, 617.8, 717.0)])
        got = [f for f, _k, _m in mf.label_forms({mf.form_key(moved): [moved]}, prev, {})]
        self.assertEqual(got, ["F23"])

    def test_the_list_is_current(self):
        """FILL-PIECES.csv reads back as exactly the forms the build scripts give now (rerun make_fill_pieces.py
        after a layout change), so each form keeps its label on the next run."""
        mf = self.mf()
        prev = mf.previous_forms(os.path.join(REPO, "v2/03-Manufacturing/wall/FILL-PIECES.csv"))
        self.assertEqual({v[0] for v in prev.values()}, {mf.form_key(p) for p in mf.side_pieces() + mf.back_pieces()})

    def test_fill_dxfs_match_the_cad(self):
        sys.path.insert(0, os.path.join(HERE, "..", "..", "03-Manufacturing", "wall"))
        import contextlib
        import io
        import check_fill_dxfs
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = check_fill_dxfs.main()
        self.assertEqual(rc, 0, out.getvalue()[-2000:])
        self.assertIn(" 0 mismatches", out.getvalue())
        self.assertNotIn("BAD ", out.getvalue())


class TrayCableTieTest(unittest.TestCase):
    """ELECTRICAL's 20 cable-tie holes (the Lead's relay of 2026-11-01 11:37 UTC): Ø6.4 in R1's, R2's, B4's and B2's tray
    backs at ELECTRICAL's places, each inside its tray's back with room round it; none in L1, L2, B1 or B3."""

    WANT = {"R1": ("y", [767.0, 657.0, 476.2, 295.5, 185.5, 23.8, -150.0], "el_trunk_z", 1100.0),
            "R2": ("z", [1476.0, 1688.7, 1901.3, 2114.0, 2224.0], "el_call_y", -209.5)}

    def test_side_trays_carry_electricals_ties(self):
        for code, (axis, along, fixed, at) in self.WANT.items():
            ns = load(part="cassette", side=code[0], row=code[1])
            v = resolve(ns)
            sites = ns["TIE_SITES"][code]
            self.assertEqual(len(sites), len(along))
            self.assertAlmostEqual(v["el_tie_d"], 6.4, places=6)
            got = sorted(v[s_[0] if axis == "y" else s_[1]] for s_ in sites)
            self.assertEqual(got, sorted(along))
            self.assertAlmostEqual(v[fixed], at, places=1)
            # inside the tray's back with 5 round it
            y0 = v["pod_d"] / 2 - v["wall_depth"] + v["lin_front_dy"]
            y1 = v["pod_d"] / 2 - v["stack_t"] + v["cass_t"]
            z0 = v["panel_z0"] if code[1] == "1" else v["panel_z0"] + v["side_h"] + v["seam_gap"]
            z1 = v["panel_z0"] + v["side_h"] if code[1] == "1" else v["pod_h"] - v["outer_t"] - v["lin_gap"]
            for ye, ze in sites:
                yy, zz = v[ye], v[ze]
                self.assertTrue(y0 + 5 + 3.2 <= yy <= y1 - 5 - 3.2, (code, yy))
                self.assertTrue(z0 + 5 + 3.2 <= zz <= z1 - 5 - 3.2, (code, zz))
        for side, row in (("L", "1"), ("L", "2")):
            self.assertNotIn(side + row, load(part="cassette", side=side, row=row)["TIE_SITES"])

    def test_back_trays_name_electricals_ties(self):
        v = resolve(load(part="cassette", side="R", row="1"))      # the table holds every el_ value
        ns = load(part="cassette", side="R", row="1")
        table = {p[0]: p for p in ns["EL_PARAMS"]}
        self.assertEqual([float(table["el_tie_b4_z%d" % i][1].split()[0]) for i in range(1, 6)],
                         [1363.6, 1645.8, 1927.9, 2210.0, 2270.0])
        # B2's ties are held by ELECTRICAL's rules (past the unit's cut-out, inside the corner end), so read their values
        b2 = resolve(load_back("B2", "cassette"))
        self.assertEqual([round(b2["el_tie_b2_x%d" % i], 2) for i in range(1, 4)], [545.0, 844.25, 1143.5])
        self.assertTrue(v)


class InteriorFixingsTest(unittest.TestCase):
    """INTERIOR's fixings on D-131's studs (the Lead's rulings of 2026-11-01): R1's ledge brackets on studs Y -240,
    103.6, 329.1 and 700 (two of them added), rivnuts at Z 815 and 1045; R2's screen rail on studs Y -121.8 and 580,
    rivnuts at Z 1320 and 1380; Ø16 clearance holes in the lining; R2's bottom-back clip zone moved up clear of them."""

    def ys(self, side, row):
        ns = load("panel", side, row)
        v = resolve(ns)
        y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
        n = int(round(v["stile_n_mid"]))
        return ns, v, [round(y_front + v["stud_c%d" % k], 1) for k in range(1, n + 1)]

    def test_studs_and_fixings(self):
        ns, v, ys = self.ys("R", "1")
        self.assertEqual(ys, [-372.7, -240.0, -121.8, 103.6, 329.1, 580.0, 700.0])
        self.assertEqual([ys[k - 1] for k in ns["INT_FIX"]["R1"]], [-240.0, 103.6, 329.1, 700.0])
        self.assertEqual((v["int_rn_z1"], v["int_rn_z2"]), (815.0, 1045.0))
        ns2, v2, ys2 = self.ys("R", "2")
        self.assertEqual([ys2[k - 1] for k in ns2["INT_FIX"]["R2"]], [-121.8, 580.0])
        self.assertEqual((v2["int_rn_z1"], v2["int_rn_z2"]), (1320.0, 1380.0))
        _ns, _v, ys_l = self.ys("L", "1")
        self.assertEqual(ys_l, [-372.7, -121.8, 103.6, 329.1, 580.0])           # L1 keeps D-131's five

    def test_bays_stay_under_the_skin_limit_and_clear_of_bolts(self):
        """Every R1 bay is no wider than L1's widest (so the skin keeps its 2 mm), and the added studs stand 30 or more
        clear of every bolt (R-J14)."""
        def bays(side):
            _n, v, ys = self.ys(side, "1")
            y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
            edges = [y_front + v["tube_w"]] + [y + d * v["tube_w"] / 2 for y in ys for d in (-1, 1)]
            return [edges[i + 1] - edges[i] for i in range(0, len(edges) - 1, 2)]
        self.assertLessEqual(max(bays("R")), max(bays("L")) + 1e-6)
        ns, v, ys = self.ys("R", "1")
        tw = v["tube_w"]
        y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
        bolts = [y_front + v["bolt_edge"] + i * v["len_bolt_pitch"] for i in range(int(round(v["n_len_bolt"])))]
        for y in (ys[1], ys[6]):
            self.assertGreaterEqual(min(abs(y - b) for b in bolts) - tw / 2, 30.0, y)

    def test_clearances_against_clips_and_ties(self):
        for side_row, code in ((("R", "1"), "R1"), (("R", "2"), "R2")):
            ns = load("cassette", *side_row)
            v = resolve(ns)
            y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
            z0 = v["panel_z0"] + (0 if code == "R1" else v["side_h"] + v["seam_gap"])
            n = int(round(v["stile_n_mid"]))
            last = y_front + v["stud_c%d" % n]
            back_low = v["clip_dz_back_low"] if code == "R2" else v["clip_zone_dz"]
            zone = (z0 + back_low - v["clip_zone_h"] / 2, z0 + back_low + v["clip_zone_h"] / 2)
            fixes = [(y_front + v["stud_c%d" % k], z) for k in ns["INT_FIX"][code]
                     for z in (v["int_rn_z1"], v["int_rn_z2"])]
            for y, z in fixes:
                if abs(y - last) < 1:                          # on the stud with the back clips
                    self.assertTrue(z + v["int_clr_d"] / 2 < zone[0] or z - v["int_clr_d"] / 2 > zone[1], (code, z, zone))
            ties = [(v[a] if a in v else None, v[b] if b in v else None) for a, b in ns["TIE_SITES"][code]]
            for ty, tz in ties:
                for y, z in fixes:
                    gap = max(abs(ty - y), abs(tz - z)) - (v["int_clr_d"] + v["el_tie_d"]) / 2
                    self.assertGreater(gap, 10.0, (code, ty, tz, y, z))
        self.assertAlmostEqual(z0 + back_low - v["clip_zone_h"] / 2, 1397.26, delta=0.01)


class CassetteLedgeTest(unittest.TestCase):
    """The Lead's ruling of 2026-11-01: a wall cassette's weight sits on a ledge on the lower frame's bottom rail
    (WALL's sizes, accepted): one part for L1 and R1, its leg the 2.26 seam gap under the frame, lower panels only."""

    def test_l1_and_r1_get_the_same_ledge(self):
        vl, vr = resolve(load(side="L")), resolve(load(side="R"))
        for k in ("ledge_len", "ledge_rivet_pitch", "ledge_rivet_e", "ledge_rivet_z", "ledge_out", "ledge_up",
                  "ledge_t", "ledge_rivet_d", "ledge_rivet_n"):
            self.assertAlmostEqual(vl[k], vr[k], places=6, msg=k)
        self.assertAlmostEqual(vl["ledge_len"], 1430.0, places=2)
        # the ledge starts where R1's cassette does, 5 in, on both sides
        y0 = vl["pod_d"] / 2 - vl["wall_depth"] + vl["ledge_front_dy"] + vl["ledge_end"]
        self.assertAlmostEqual(y0, -635.0, places=2)
        self.assertAlmostEqual(vr["pod_d"] / 2 - vr["wall_depth"] + vr["lin_front_dy"] + vr["ledge_end"], y0, places=2)

    def test_b1_and_b2_get_the_same_back_ledge(self):
        nb1, nb2 = load_back("B1"), load_back("B2")
        v1, v2 = resolve(nb1), resolve(nb2)
        for k in ("ledge_len", "ledge_rivet_pitch", "ledge_rivet_e", "ledge_rivet_z", "ledge_out", "ledge_t"):
            self.assertAlmostEqual(v1[k], v2[k], places=6, msg=k)
        self.assertAlmostEqual(v1["ledge_len"], 1154.87, places=1)
        self.assertEqual(nb1["PARTS"]["ledge"][0], "211801")
        self.assertNotIn("ledge_len", resolve(load_back("B3")))

    def test_rivet_pattern_is_symmetric_and_clear_of_the_ends(self):
        v = resolve(load())
        first = v["ledge_rivet_e"]
        last = first + (v["ledge_rivet_n"] - 1) * v["ledge_rivet_pitch"]
        self.assertAlmostEqual(v["ledge_len"] - last, first, places=6)
        # centre to the upright's top edge at least 2 x the rivet (edge distance); the countersink's edge at least 2t
        # clear of the bend and of the top edge; the head's depth leaves land in the upright (the Lead's 1.5 ruling)
        top = v["ledge_pad_t"] + v["ledge_t"] + v["ledge_up"]            # the upright's top above the leg's bottom
        centre = v["ledge_pad_t"] + v["ledge_t"] + v["ledge_rivet_z"]
        self.assertGreaterEqual(top - centre, 2 * v["rivet_d"])
        self.assertGreaterEqual(centre - v["ledge_csk_d"] / 2 - (v["ledge_t"] + v["ledge_r"]), 2 * v["ledge_t"])
        self.assertGreaterEqual(top - centre - v["ledge_csk_d"] / 2, 2 * v["ledge_t"])
        csk_depth = (v["ledge_csk_d"] - v["ledge_rivet_d"]) / 2 / math.tan(v["rivet_csk_angle"] / 2)
        self.assertGreaterEqual(v["ledge_t"] - csk_depth, v["ledge_t"] / 3)     # land under the countersink
        self.assertGreaterEqual(v["ledge_csk_d"], v["rivet_head_d"])            # no head stands proud

    def test_the_leg_sits_the_squeezed_pad_under_the_frame_and_lower_panels_only(self):
        """Joints' pad (PORON 4701-40, 320 grade, 2.36 standard) squeezed about 2% to 2.31 under the cassettes, so
        the leg sits that far under the frame and the lining doesn't move; inside the foam's ±10% of 2.36."""
        v = resolve(load())
        self.assertAlmostEqual(v["ledge_pad_t"], 2.31, places=6)
        self.assertTrue(2.36 * 0.9 <= v["ledge_pad_t"] <= 2.36 * 1.1)
        self.assertNotIn("ledge_len", resolve(load(row="2")))


class MemberEndsTest(unittest.TestCase):
    """The Lead's ruling of 2026-11-01: the frame drawing's cut list is each member's drawing, so every member row
    names each end's angle by its end and the long points' face, and they are the STEP's (check_member_ends.py)."""

    def cme(self):
        sys.path.insert(0, os.path.join(HERE, "..", "..", "03-Manufacturing", "wall"))
        import check_member_ends
        return check_member_ends

    def test_every_d120_panel_lists_its_member_ends_as_its_step(self):
        cme = self.cme()
        steps = cme.panel_steps()
        self.assertTrue(steps, "no D-120 panel STEP found")
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cme.main(["x"] + steps)
        self.assertEqual(rc, 0, out.getvalue()[-2000:])

    def test_the_tube_cut_list_is_current(self):
        """210000_P01_WALL-TUBE-CUT-LIST_BOM.csv (the weldment drawings' cut list, D-162) is the panel lists' member
        rows as they stand: regenerated from copies of the lists, it equals the committed file."""
        import glob
        import shutil
        import tempfile
        mf = os.path.join(HERE, "..", "..", "03-Manufacturing", "wall")
        sys.path.insert(0, mf)
        import make_parts_list
        with tempfile.TemporaryDirectory() as tmp:
            for p in glob.glob(os.path.join(mf, "210[12]0[1-4]_P01_*_BOM.csv")):
                shutil.copy(p, tmp)
            make_parts_list.write_cut_list(tmp)
            with open(os.path.join(tmp, make_parts_list.CUT_LIST), encoding="utf-8") as fh:
                fresh = fh.read()
        with open(os.path.join(mf, make_parts_list.CUT_LIST), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), fresh)
        self.assertIn("212101", fresh)

    def test_a_flipped_rail_is_caught(self):
        cme = self.cme()
        import csv
        import glob
        import tempfile
        mf = os.path.join(HERE, "..", "..", "03-Manufacturing", "wall")
        step = glob.glob(os.path.join(mf, "210101_P01_*_STEP.step"))[0]
        bom = glob.glob(os.path.join(mf, "210101_P01_*_BOM.csv"))[0]
        rows = list(csv.DictReader(open(bom, encoding="utf-8")))
        rail = [r for r in rows if r["part_number"].startswith("212") and "RAIL BOTTOM" in r["name"]][0]
        m = re.search(r"front end mitred ([\d.]+)° and back end ([\d.]+)°", rail["note"])
        self.assertTrue(m, rail["note"])
        rail["note"] = rail["note"].replace(m.group(0), "front end mitred %s° and back end %s°" % (m.group(2),
                                                                                                    m.group(1)))
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "210101_flipped_BOM.csv")
            with open(p, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
            bad = cme.check(step, p)
        self.assertTrue(any(rail["part_number"] in b and "low end" in b for b in bad), bad)
        self.assertTrue(any(rail["part_number"] in b and "high end" in b for b in bad), bad)


class EditTestBackChecksTest(unittest.TestCase):
    """The edit test's back-panel checks read a D-131 frame right: each rail stops 1.41 short of the frame's corner
    for the mitre plate, and the 220 rule is set from the frame's end, not the rail's (dry run 8, B1 after the edit:
    the frame end X -1101.74, the rails from -1100.33, the rivnuts at 220 + 3 x 219.66 from the frame end)."""

    def setUp(self):
        fake = types.ModuleType("adsk")
        fake.core = types.ModuleType("adsk.core")
        fake.fusion = types.ModuleType("adsk.fusion")
        sys.modules.update({"adsk": fake, "adsk.core": fake.core, "adsk.fusion": fake.fusion})
        sys.path.insert(0, HERE)
        import edit_test_wall
        self.et = edit_test_wall
        self.p = {"pod_w": 2300, "half_pw": 1100.61, "half_fw": 1098.99, "back_ph": 1080, "stile_pitch_max": 300,
                  "frm_len": 1098.99, "stile_n_mid": 3, "stile_pitch": 269.748, "cass_len": 1064.87, "cass_h": 1080,
                  "pnl_h": 1080}
        f = "211201 FRAME:1+"
        self.after = {
            f + "212501 RAIL BOTTOM:1 / RAIL - BOTTOM": (-1100.33, 804.0, 112.26, -4.16, 844.0, 132.26),
            f + "212502 RAIL TOP:1 / RAIL - TOP": (-1100.33, 804.0, 1172.26, -4.16, 844.0, 1192.26),
            f + "212503 STILE OUTER:1 / STILE - OUTER": (-1101.74, 804.0, 113.67, -1081.74, 844.0, 1190.85),
            f + "212504 STILE CENTRE:1 / STILE - CENTRE": (-22.75, 804.0, 113.67, -2.75, 844.0, 1190.85),
            f + "212505 STILE MID:1 / STILE - MID": (-831.99, 804.0, 132.26, -811.99, 844.0, 1172.26),
            f + "212505 STILE MID:2 / STILE - MID": (-562.25, 804.0, 132.26, -542.25, 844.0, 1172.26),
            f + "212505 STILE MID:3 / STILE - MID": (-292.5, 804.0, 132.26, -272.5, 844.0, 1172.26),
            "211401 SKIN:1 / SKIN - ACP 3": (-1101.74, 847.0, 112.26, -1.13, 850.0, 1192.26),
            "831001 SPIGOT:1 / SPIGOT": (-1005.74, 820.0, 1185.02, -997.74, 828.0, 1200.26),
            "831001 SPIGOT:2 / SPIGOT": (-106.75, 820.0, 1185.02, -98.75, 828.0, 1200.26),
        }
        for i, (x0, x1) in enumerate(((-888.22, -875.26), (-668.56, -655.6), (-448.89, -435.93), (-229.23, -216.27),
                                      (-1008.22, -995.26), (-109.23, -96.27)), 1):
            z0 = 1183.6 if i <= 4 else 1182.1
            self.after["838003 RIVNUT:%d / RIVNUT" % i] = (x0, 817.52, z0, x1, 830.48, z0 + 10.92)

    def check(self, after):
        return {name.split(" [")[0]: ok for name, ok in self.et.back_checks(after, self.p)}

    def test_rivnuts_from_the_frame_end_pass(self):
        got = self.check(self.after)
        self.assertTrue(got["top rail rivnuts follow the 220 rule"], got)
        self.assertTrue(all(got.values()), got)

    def test_rivnuts_set_from_the_rail_end_fail(self):
        moved = {k: ((v[0] + 1.41, v[1], v[2], v[3] + 1.41, v[4], v[5]) if k.endswith("RIVNUT") and v[2] > 1183
                     else v) for k, v in self.after.items()}
        self.assertFalse(self.check(moved)["top rail rivnuts follow the 220 rule"])


if __name__ == "__main__":
    unittest.main()
