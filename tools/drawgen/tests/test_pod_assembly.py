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
