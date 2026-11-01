#!/usr/bin/env python3
"""Tests of GA sheet 1, the whole pod (tools/drawgen/pod_assembly.py). Run in drawgen's own environment:

    <venv>/bin/python tools/drawgen/tests/test_pod_assembly.py          # prints "N of N passed"

1. The master BOM's tree: each part counts under its first-level assembly; rows without a part number are no items.
2. The STEP set is the whole-pod check's (tools/checks/run_fusion_checks.pick_steps), so the GA and the clash check
   always look at the same pod.
3. A top part with no number, or one the master BOM doesn't hold, or one under a first-level row the entry leaves
   out, stops the sheet with a message naming the file.
4. The sheet draws from today's STEPs and reads back PASS: one table row per first-level assembly, a balloon on each
   one a STEP has, the two heights (2400 to the roof skin, 2402 overall) measured again.
5. The read-back is not a rubber stamp: it fails a table cell that differs from the master BOM, a balloon moved off
   its assembly, a STEP changed since the sheet was drawn, and a STEP of the pod the sheet doesn't name.
"""

import csv
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import fitz  # noqa: E402

import inputs  # noqa: E402
import pod_assembly as P  # noqa: E402
import readback  # noqa: E402
from compose import NotDrawable  # noqa: E402

TMP = tempfile.mkdtemp(prefix="drawgen-pod-test-")
_MADE = {}


def _made():
    """The pod's sheet, drawn once per run."""
    if "pod" not in _MADE:
        _MADE["pod"] = P.generate(os.path.join(TMP, "sheet"))
    return _MADE["pod"]


def _with_data(src, dst, change):
    """A copy of a sheet whose drawing data is changed by change(data) (the drawing itself stays)."""
    doc = fitz.open(src)
    data = readback.read_data(doc)
    change(data)
    txt = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    esc = txt.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    doc.xref_set_key(doc.pdf_catalog(), "DrawgenData", "(%s)" % esc)
    doc.save(dst)
    doc.close()
    return dst


def _master(rows):
    path = os.path.join(TMP, "master_%d.csv" % len(os.listdir(TMP)))
    cols = ["level", "row_type", "part_number", "name", "name_vi", "qty_per_pod", "material", "finish"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for lv, pn, name in rows:
            w.writerow({"level": lv, "row_type": "x", "part_number": pn, "name": name, "name_vi": name,
                        "qty_per_pod": "1", "material": "", "finish": ""})
    return path


def test_each_part_counts_under_its_first_level_assembly():
    path = _master([("0", "100000", "POD"), ("1", "", "KIT FAMILY"), ("2", "109001", "KIT PART"),
                    ("1", "210000", "WALL"), ("2", "210101", "PANEL"), ("3", "211101", "FRAME"),
                    ("2", "210102", "PANEL 2"), ("1", "350000", "DECOR"), ("2", "350001", "DL"),
                    ("1", "910000", "PACKAGING")])
    own, first, up = P.master_tree(path)
    assert own["part_number"] == "100000"
    assert [r["part_number"] for r in first] == ["210000", "350000", "910000"]       # the family row has no number
    assert up["211101"] == "210000" and up["210102"] == "210000" and up["350001"] == "350000"
    assert up["210000"] == "210000" and "109001" not in up                             # under a row with no number


def test_the_step_set_is_the_whole_pod_checks():
    sys.path.insert(0, os.path.join(inputs.REPO, "tools", "checks"))
    import run_fusion_checks
    want = sorted(os.path.abspath(p) for p in run_fusion_checks.pick_steps(inputs.REPO, "pod"))
    assert [os.path.abspath(p) for p in P.pod_steps()] == want
    assert not any("/skeleton/" in p for p in want)


def test_top_parts_must_be_numbered_and_in_the_master_bom():
    path = _master([("0", "100000", "POD"), ("1", "210000", "WALL"), ("2", "210101", "PANEL"),
                    ("1", "910000", "PACKAGING"), ("2", "910001", "CRATE")])
    tops = {"a.step": [("210101", "210101 PANEL", [])], "b.step": [(None, "Body1", [])],
            "c.step": [("399999", "399999 NOT LISTED", [])], "d.step": [("910001", "910001 CRATE", [])]}
    keep = (P.top_parts, P.skeleton_rev, P._step_date)
    P.top_parts = lambda p: tops[os.path.basename(p)]
    P.skeleton_rev = lambda root=None: "P04"
    P._step_date = lambda p: ("2026-11-01", "12:00:00")
    try:
        ok = P.PodAssy("100000", "ga", {"leave_out": ["910000"]}, master=path, steps=["a.step"])
        assert [it.pn for it in ok.items] == ["210000"] and len(ok.items[0].occs) == 1
        assert ok.dwg_name == "100000_P04_POD_DWG" and ok.kind == "pod"
        for bad, words in (("b.step", "without a part number"), ("c.step", "isn't under a first-level assembly"),
                           ("d.step", "leaves out")):
            try:
                P.PodAssy("100000", "ga", {"leave_out": ["910000"]}, master=path, steps=["a.step", bad])
                raise AssertionError("%s was drawn" % bad)
            except NotDrawable as e:
                assert words in str(e) and bad in str(e), (bad, str(e))
    finally:
        P.top_parts, P.skeleton_rev, P._step_date = keep


def test_the_sheet_draws_and_reads_back():
    final, rep = _made()
    fails, st = P.check(final)
    assert not fails, fails
    first = [r for r in P.master_tree(os.path.join(inputs.REPO, P.MASTER_REL))[1]
             if r["part_number"].strip() not in P.entry()["leave_out"]]
    assert st["rows"] == len(first) and st["steps"] == len(P.pod_steps())
    assert st["balloons"] == len([b for b in rep["data"]["balloons"]]) > 0
    hs = sorted(float(p["value"]) for g in rep["data"]["interfaces"] for p in g["points"])
    assert hs == [2400.0, 2402.0], hs                     # the roof skin (D-21) and the grille's top, from the floor
    assert os.path.basename(final) == "100000_%s_POD-SPACESHIP_DWG.pdf" % P.skeleton_rev()


def test_readback_fails_a_table_cell_that_differs_from_the_master_bom():
    final, _rep = _made()
    src = os.path.join(inputs.REPO, P.MASTER_REL)
    alt = os.path.join(TMP, "altered_master.csv")
    with open(src, encoding="utf-8") as f:
        txt = f.read()
    assert ",210000,WALL," in txt
    with open(alt, "w", encoding="utf-8") as f:
        f.write(txt.replace(",210000,WALL,", ",210000,WALL - CHANGED,", 1))

    def point_at_alt(d):
        for s in d["sources"]:
            if s["role"] == "parts list":
                s["path"] = alt
                s["sha256_12"] = inputs.sha12(alt)
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_table.pdf"), point_at_alt))
    assert any("NAME" in f and "CHANGED" in f for f in fails), fails


def test_readback_fails_a_balloon_moved_off_its_assembly():
    final, _rep = _made()

    def move(d):
        b = d["balloons"][0]
        b["tip3d"] = [b["tip3d"][0], b["tip3d"][1] - 3000.0, b["tip3d"][2]]     # out of the pod
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_moved.pdf"), move))
    assert any(f.startswith("balloon %d:" % _rep["data"]["balloons"][0]["no"]) for f in fails), fails


def test_readback_fails_a_changed_or_missing_step():
    final, _rep = _made()

    def stale(d):
        [s for s in d["sources"] if s["role"] == "STEP"][0]["sha256_12"] = "0" * 12
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_stale.pdf"), stale))
    assert any("changed since the sheet was drawn" in f for f in fails), fails

    def dropped(d):
        d["sources"] = [s for s in d["sources"] if not s["path"].endswith("_P01_AIR_STEP.step")]
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_dropped.pdf"), dropped))
    assert any("_P01_AIR_STEP.step is in the pod's STEPs now but not on the sheet" in f for f in fails), fails


def _box(x0, y0, z0, x1, y1, z1):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def test_a_free_stretch_ends_on_the_nearest_material_each_way():
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    import assembly as A
    # an L profile on the left (like DL's stop 351103: its face at X -942 only 2 mm deep), a plate on the right,
    # a farther plate behind it
    ell = BRepAlgoAPI_Fuse(_box(-972, -690, 0, -942, -688, 100), _box(-972, -690, 0, -970, -670, 100)).Shape()
    bodies = [P.Body("350000", ("350001", "351103"), ell), P.Body("360000", ("360002", "368003"),
                                                                  _box(90, -705, 0, 92, -693, 100)),
              P.Body("360000", ("360002", "361003"), _box(200, -705, 0, 210, -693, 100))]
    ends = P.free_run(bodies, "x", (-373.5, -700, 50), {"y": (-850, -640)})
    assert abs(ends["lo"][0] - (-942.0)) < 1e-6 and ends["lo"][1].chain[-1] == "351103"
    assert abs(ends["hi"][0] - 90.0) < 1e-6 and ends["hi"][1].chain[-1] == "368003"
    for e_ in (ends["lo"], ends["hi"]):             # the end's point is on its body, not in the L's open middle
        assert A._in_or_on([e_[1].solid], e_[2]), e_[2]
    spec = {"along": "x", "beam": {"y": (-850, -640)}, "ends": [["351103"], ["368003", "361003"]]}
    m = P.measure(bodies, spec, (-373.5, -700, 50), 0.0)
    assert m is not None and abs(m[0] - 1032.0) < 1e-6 and (m[3], m[4]) == ("351103", "368003")
    assert P.measure(bodies, dict(spec, ends=[["351103"], ["361003"]]), (-373.5, -700, 50), 0.0) is None
    try:                                            # a body across the start: no free stretch there
        P.free_run(bodies, "x", (91.0, -700, 50), {"y": (-850, -640)})
        raise AssertionError("a start inside a body was measured")
    except ValueError as e:
        assert "368003" in str(e)
    up = P.measure([P.Body("510000", ("410000", "510301"), _box(-500, -500, 2316.5, 500, 500, 2350))],
                   {"along": "z", "ends": [["floor"], ["510301"]]}, (0.0, 0.0, 1200.0), 0.0)
    assert up is not None and abs(up[0] - 2316.5) < 1e-6 and up[3] == "floor" and abs(up[1][2]) < 1e-9


def test_the_door_turns_outward_about_its_pivot_and_must_not_run_into_anything():
    leaf = P.Body("360000", ("360001", "361001"), _box(0, -5, 0, 1000, 5, 2000))
    hinge = P.Body("360000", ("360001", "368101"), _box(-20, -20, 300, 100, 20, 400))
    wall = P.Body("210000", ("210101",), _box(-500, 100, 0, -400, 200, 2000))
    spec = {"unit": "360001", "pivot": [-5.0, -10.0], "angle": 90, "left_out": ["368101"]}
    out = P.turned_door([leaf, hinge, wall], spec)
    assert len(out) == 2 and not any(b.named(["368101"]) for b in out)        # the hinge's HOLD space left out
    b = [x for x in out if x.named(["361001"])][0].box
    # (x, y) -> (px + (y - py), py - (x - px)): the leaf stands out in front, its inner face (y 5) now at X 10
    assert all(abs(u - v) < 1e-6 for u, v in zip(b, (0.0, -1015.0, 0.0, 10.0, -15.0, 2000.0))), b
    post = P.Body("350000", ("350001",), _box(0, -600, 0, 50, -500, 2000))     # in the open leaf's way
    try:
        P.turned_door([leaf, post], spec)
        raise AssertionError("an open door through a post was drawn")
    except NotDrawable as e:
        assert "runs into 350001" in str(e)


def test_the_mass_is_the_weight_rollups_pod():
    path = os.path.join(TMP, "rollup.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("| Assembly | kg |\n|---|---:|\n| WALL | 82.7 |\n| **Pod as shipped** | **393.0** |\n")
    assert P.rollup_mass(path) == ("393.0", path)
    with open(path, "w", encoding="utf-8") as f:
        f.write("| Assembly | kg |\n| WALL | 82.7 |\n")
    try:
        P.rollup_mass(path)
        raise AssertionError("a roll-up without the pod's row gave a mass")
    except NotDrawable as e:
        assert "Pod as shipped" in str(e)


def test_the_sheet_has_its_clear_sizes_position_codes_and_mass():
    final, rep = _made()
    fails, st = P.check(final)
    assert not fails, fails
    e = P.entry()
    x = rep["data"]["extra"]
    assert [r["name"] for r in x["sizes"]] == [s["name"] for s in e["clear"]]
    assert st["clear sizes"] == len(e["clear"])
    assert st["codes"] == sum(len(v) for v in e["codes"].values()) == 10
    assert sorted(c["code"] for c in x["codes"]) == ["B1", "B2", "B3", "B4", "C1", "C2", "L1", "L2", "R1", "R2"]
    assert x["mass"]["kg"] == P.rollup_mass()[0]
    by = {r["name"]: r for r in x["sizes"]}
    assert (by["inside width"]["lo_pn"], by["inside width"]["hi_pn"]) == ("510101", "510102")
    assert by["door clear width"]["lo_pn"] == "351103"           # DL's stop, not the open leaf, sets it
    assert by["door clear width at the head"]["value"] < by["door clear width"]["value"] < \
        by["door clear width at the foot"]["value"]                 # the slanted edge: narrower going up


def test_readback_fails_a_changed_clear_size_a_code_off_its_panel_and_a_stale_mass():
    final, rep = _made()

    def size(d):
        d["extra"]["sizes"][0]["value"] += 1.0
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_size.pdf"), size))
    assert any("measured again" in f for f in fails), fails

    def code(d):
        c = d["extra"]["codes"][0]
        c["centre"] = [c["centre"][0] + 200.0, c["centre"][1]]
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_code.pdf"), code))
    assert any("sits off its panel" in f for f in fails), fails

    def mass(d):
        for s in d["sources"]:
            if s["role"] == "mass":
                s["kg"] = "999.9"
        d["extra"]["mass"]["kg"] = "999.9"
    fails, _st = P.check(_with_data(final, os.path.join(TMP, "t_mass.pdf"), mass))
    assert any("roll-up gives the pod" in f for f in fails) and any(f.startswith("MASS:") for f in fails), fails


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for t in tests:
        try:
            t()
            ok += 1
            print("PASS %s" % t.__name__)
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            print("FAIL %s: %s" % (t.__name__, e))
    print("%d of %d passed" % (ok, len(tests)))
    shutil.rmtree(TMP, ignore_errors=True)
    return 0 if ok == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
