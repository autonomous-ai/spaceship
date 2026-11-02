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
EL_SIDE_EXPECT = {"1": {"el_y_kit": 240.5, "el_y_cx": -298.0, "el_trunk_z": 1100.0, "el_kit_d": 60.0, "el_grm_d": 19.1,
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
                             "FX-COL": (v["el_y_cx"], v["el_trunk_z"], v["el_grm_d"])}
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
                  ("B2", "panel"): {"el_inlet_x": 120.0, "el_inlet_z": 313.0, "el_lan_z": 375.0, "el_inlet_d": 24.0,
                                    "el_sl_x": 150.0, "el_cut_x0": 91.0, "el_cut_z0": 866.0, "el_cut_z1": 1134.0}}


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
        for pos, part in (("B1", "cassette"), ("B3", "cassette"), ("B1", "panel"), ("B4", "panel"), ("B2", "frame")):
            ns = load_back(pos, part)
            self.assertEqual([q[0] for q in ns["WALL_PARAMS"] if q[0].startswith("el_")], [], (pos, part))

    @unittest.skip("B2's layout waits (PM 2026-11-01: the unit's 373 bay with cross members; D-133 changes the unit)")
    def test_unit_clears_the_first_stud_by_4_75(self):
        """PM ruling 2026-10-31 20:35 UTC: 0.75 is too tight; the unit stands 4.75 clear of B2's first stud (the
        stud's face is at X 395.747, which the messages round to 395.75)."""
        cass, panel = self.resolved("B2", "cassette"), self.resolved("B2", "panel")
        stud = panel["close_gap"] / 2 + panel["stile_pitch"]
        self.assertAlmostEqual(stud - (cass["el_pu_x0"] + cass["el_pu_w"]), 4.75, delta=0.005)

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
