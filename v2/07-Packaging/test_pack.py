#!/usr/bin/env python3
"""Regression tests for pack.py. Run: python3 v2/07-Packaging/test_pack.py

Each test that changes the model restores it, so the tests run in any order.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pack  # noqa: E402

# The joints register's section 3.9 as it stands in PR #23 at aed1590, so the parser is tested without the file.
REGISTER_39 = """
### 3.9 Bolt count

| Joint | Bolts | Bolt |
|---|---:|---|
| J-WALL-01 horizontal seams | 16 | M6 × 16 |
| J-WALL-02 back corners | 12 | M6 × 16 |
| J-WALL-03 back closing seams | 6 | M6 × 25 pin |
| J-BASE-01 walls on the base band | 16 | M6 × 16 |
| J-CEIL-01 walls to ceiling | 16 | M6 × 16 |
| J-CEIL-02 ceiling closing seam | 4 | M6 × 25 pin |
| J-FRONT-01 decor to walls | 12 | M6 × 16 |
| **Total** | **82** | 72 × M6 × 16, 10 × M6 × 25 |

### 3.10 Joint IDs against the layout study
"""


def failing(m):
    return [c["id"] for c in m.checks if not c["ok"]]


def test_all_checks_pass():
    m = pack.Model()
    assert m.ok(), failing(m)


def test_outputs_current():
    assert pack.main(["--check"]) == 0, "an output is stale: run python3 v2/07-Packaging/pack.py"


def test_register_parser(tmp=Path(__file__).resolve().parent / "_register_test.md"):
    tmp.write_text(REGISTER_39, encoding="utf-8")
    try:
        rows, total = pack.read_register(tmp)
    finally:
        tmp.unlink()
    assert total == 82
    assert rows == pack.REGISTER_PINNED, rows
    assert sum(c for c, s in rows.values() if s == "M6 x 25") == 10


def test_bolt_change_is_caught():
    st = next(s for s in pack.STEPS if s["n"] == 5)
    saved = copy.deepcopy(st["joints"])
    st["joints"]["J-WALL-02"] -= 1
    try:
        m = pack.Model()
        assert "K7" in failing(m)
    finally:
        st["joints"] = saved
    assert "K7" not in failing(pack.Model())


def test_heavy_piece_is_caught():
    p = pack.PIECE["2-03"]
    saved = p.extra_kg
    p.extra_kg = 5.0          # DR with its riser's share would pass 20 kg
    try:
        assert "K2" in failing(pack.Model())
    finally:
        p.extra_kg = saved


def test_rollup_line_lost_is_caught():
    p = pack.PIECE["2-10"]
    saved = list(p.mass)
    p.mass = [("SOFFIT", 1), ("FANBOX_E", 1)]   # drops the exhaust fans' half of the fans line
    try:
        assert "K1" in failing(pack.Model())
    finally:
        p.mass = saved


def test_overhang_is_caught():
    p = pack.PIECE["1-01"]
    saved = p.dims
    p.dims = pack.S(1455, 1225.5, 12)   # the floor panel with BASE P01's 19.5 mm lap
    try:
        assert "K4" in failing(pack.Model())
    finally:
        p.dims = saved


def test_time_within_limit():
    m = pack.Model()
    clock = m.time_total(pack.CLOCK_LAST_STEP) / 60
    assert clock <= pack.MINE["time_limit_min"].value, clock


def test_glass_order_in_crate():
    assert pack.PIECE[pack.CRATE_TAGS[-1]].step < pack.PIECE[pack.CRATE_TAGS[0]].step


def test_door_before_dt():
    door = next(s["n"] for s in pack.STEPS if "2-02" in s["tags"])
    dt = next(s["n"] for s in pack.STEPS if "2-12" in s["tags"])
    assert door < dt


def test_dr_bolts_before_air_column():
    dr = next(s["n"] for s in pack.STEPS if "2-03" in s["tags"])
    col = next(s["n"] for s in pack.STEPS if "2-11" in s["tags"])
    assert dr < col


def test_status_words():
    allowed = {"confirmed", "source", "calculation", "assumption", "unverified"}
    for k, v in {**pack.MINE, **pack.TIME}.items():
        assert v.status in allowed, (k, v.status)


def test_no_reserved_part_numbers():
    reserved = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}
    used = {p.pn for p in pack.PIECES} | {it["pn"] for it in pack.PACKAGING}
    assert not (used & reserved), used & reserved


def test_clock_matches_model():
    m = pack.Model()
    assert abs(pack.clock_min(pack.STEPS, pack.OTHER_FIXINGS) - m.time_total(pack.CLOCK_LAST_STEP) / 60) < 1e-9


def test_d87_in_the_steps():
    # D-87: corner keys hook in, the fan boxes ride in their parts, the floor foam is bonded, a self-test replaces the 10 min test
    assert all(f["count"] == 0 for f in pack.OTHER_FIXINGS if f["step"] == 2)
    tags = {p.tag for p in pack.PIECES if p.kind == "piece"}
    names = " ".join(p.name for p in pack.PIECES)
    assert "SEAL MAT" not in names and "EXHAUST FAN BOX, WITH" not in names
    assert pack.PIECE["2-10"].kg <= 20 and pack.PIECE["2-17"].kg <= 20
    assert len(tags) == 42
    step20 = next(s for s in pack.STEPS if s["n"] == 20)
    assert all(o["secs"] < 600 for o in step20["ops"])


def test_step_picture_script_and_data():
    import json
    import py_compile
    guide = pack.GUIDE_DIR
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:   # compile outside the repo, so no __pycache__ lands in the guide folder
        py_compile.compile(str(guide / "step_pictures.py"), cfile=str(Path(tmp) / "step_pictures.pyc"), doraise=True)
    data = json.loads(pack.step_bodies_json())
    assert data["source"].endswith("100000_P04_POD-SKELETON_STEP.step")
    views = {"back", "front", "inside"}
    assert data["steps"] and all(s["view"] in views and s["new"] and s["image"].endswith("_IMG.png") for s in data["steps"])
    script = (guide / "step_pictures.py").read_text(encoding="utf-8")
    assert all('"%s":' % v in script for v in views)


def _run_step_pictures(args, fail_save=False):
    """Run step_pictures.run() against a stand-in for Fusion's API, offline. Returns what the script did: pictures
    saved, the layout grid's check-box history, commands executed, how the design was closed."""
    import json
    import os
    import types
    guide = pack.GUIDE_DIR
    log = {"saved": [], "grid": [True], "executed": [], "closed": None}

    class Obj:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    class Coll:
        def __init__(self, items):
            self._items = list(items)

        @property
        def count(self):
            return len(self._items)

        def item(self, i):
            return self._items[i]

        def itemByName(self, name):
            return next((x for x in self._items if x.name == name), None)

    class CheckBox:
        def __init__(self, key):
            self.key = key

        @property
        def isChecked(self):
            return log[self.key][-1]

        @isChecked.setter
        def isChecked(self, v):
            log[self.key].append(bool(v))

    class Command:
        def __init__(self, cid, name, key):
            self.id, self.name, self.controlDefinition, self.key = cid, name, CheckBox(key), key

        def execute(self):
            log["executed"].append(self.name)
            log[self.key].append(not log[self.key][-1])

    log["lock"] = [False]
    log["snap"] = [True]
    commands = Coll([Command("LayoutGridCmd", "Layout Grid", "grid"), Command("GridLockCmd", "Layout Grid Lock", "lock"),
                     Command("SnapCmd", "Snap to Grid", "snap")])
    data = json.load(open(guide / "100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json", encoding="utf-8"))
    names = sorted({b for s in data["steps"] for b in s["new"]}) + ["ROOF ENVELOPE"]
    root = Obj(bRepBodies=[Obj(name=n, isLightBulbOn=True, opacity=1.0) for n in names], allOccurrences=[])
    doc = Obj(name="100000_P04_POD-SKELETON_CAD", products=Obj(itemByProductType=lambda t: Obj(rootComponent=root)),
              activate=lambda: None, close=lambda save: log.__setitem__("closed", save))

    class Docs(Coll):
        def open(self, f, visible):
            return doc

    def save(out, w, h):
        if fail_save:
            return False
        Path(out).write_bytes(b"png")
        log["saved"].append(out)
        return True

    folder = Obj(name="FocusPod v2", dataFiles=Coll([Obj(name="100000_P04_POD-SKELETON_CAD", versionNumber=7)]))
    project = Obj(name="Default Project", rootFolder=Obj(dataFolders=Coll([folder])))
    viewport = Obj(camera=Obj(), fit=lambda: None, saveAsImageFile=save)
    app = Obj(documents=Docs([]), data=Obj(dataProjects=Coll([project]), activeProject=None),
              userInterface=Obj(commandDefinitions=commands), activeViewport=viewport,
              preferences=Obj(gridPreferences=Obj(isLayoutGridShown=True), graphicsPreferences=Obj(), generalPreferences=Obj()))
    adsk = types.ModuleType("adsk")
    adsk.core = types.ModuleType("adsk.core")
    adsk.fusion = types.ModuleType("adsk.fusion")
    adsk.doEvents = lambda: None
    adsk.core.Application = Obj(get=lambda: app)
    adsk.core.Point3D = Obj(create=lambda x, y, z: (x, y, z))
    adsk.core.Vector3D = Obj(create=lambda x, y, z: (x, y, z))
    adsk.fusion.Design = Obj(cast=lambda d: d)
    keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
    sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.fusion": adsk.fusion})
    try:
        path = guide / "step_pictures.py"
        g = {"__name__": "step_pictures_offline", "__file__": str(path), "SCRIPT_ARGS": args}
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), g)
        try:
            g["run"](None)
        except RuntimeError as e:
            log["error"] = str(e)
    finally:
        for k, v in keep.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    log["files"] = sorted(os.path.relpath(p, args.get("out_dir") or args["repo_root"]) for p in log["saved"])
    return log, data


def test_step_pictures_sample_then_full_offline():
    # the picture script's own logic, proven offline before a Fusion run (AGENTS.md: prove a method on a sample)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        repo, out = Path(tmp) / "repo", Path(tmp) / "sample"
        # a sample: only the named steps, into the scratch folder; the grid goes off once and comes back on
        log, data = _run_step_pictures({"repo_root": str(repo), "steps": "2,12,14", "out_dir": str(out)})
        assert "error" not in log, log.get("error")
        assert log["files"] == ["100000_P04_POD-ASSEMBLY-GUIDE-STEP-%02d_IMG.png" % n for n in (2, 12, 14)], log["files"]
        assert not repo.exists(), "a sample wrote into the repository"
        assert log["executed"] == ["Layout Grid", "Layout Grid"] and log["grid"] == [True, False, True], log
        assert log["lock"] == [False] and log["snap"] == [True], "touched a grid setting it must leave alone"
        assert log["closed"] is False, "the design must close without saving"
        # the full set: every step's picture where the guide reads it
        log, data = _run_step_pictures({"repo_root": str(repo)})
        assert "error" not in log, log.get("error")
        assert log["files"] == sorted(s["image"] for s in data["steps"]), log["files"]
        assert log["grid"][-1] is True and log["closed"] is False
        # refused before Fusion opens anything: a step with no picture, or a sample without a scratch folder
        for args in ({"repo_root": str(repo), "steps": "13", "out_dir": str(out)}, {"repo_root": str(repo), "steps": "2"}):
            log, _ = _run_step_pictures(args)
            assert "error" in log and log["closed"] is None and not log["executed"], (args, log)
        # a failed save still puts the grid back and closes without saving
        log, _ = _run_step_pictures({"repo_root": str(repo), "steps": "2", "out_dir": str(out)}, fail_save=True)
        assert "error" in log and log["grid"][-1] is True and log["closed"] is False, log


def test_sizes_follow_the_skeleton():
    # panel sizes are the skeleton's named values, not typed numbers
    b1 = pack.PIECE["1-03"]
    assert b1.dims == pack.S(pack.sk("half_pw"), pack.sk("back_ph"), pack.sk("outer_t"))
    l1 = pack.PIECE["1-05"]
    assert l1.dims == pack.S(pack.sk("side_l"), pack.sk("side_h"), pack.sk("outer_t"))
    f1 = pack.PIECE["1-01"]
    assert f1.dims[2] == pack.sk("floor_t") + pack.sk("mat_t")


def test_register_parser_reads_counts_with_notes(tmp=Path(__file__).resolve().parent / "_register_test2.md"):
    text = REGISTER_39.replace("| **Total** | **82** | 72 × M6 × 16, 10 × M6 × 25 |",
                               "| J-AIR-01 soffit on the ceiling frame | 2 (the lock screws; its 4 hanger studs are set in the factory) | M6 × 25 lock screws; M6 × 16 hanger studs |\n"
                               "| J-BASE-02 base band corner keys | 0 on site (20 in the factory) | M6 × 16 as fixing bolts and hook studs |\n"
                               "| **Total on site** | **84** | 72 × M6 × 16, 12 × M6 × 25 |")
    tmp.write_text(text, encoding="utf-8")
    try:
        rows, total = pack.read_register(tmp)
    finally:
        tmp.unlink()
    assert rows["J-AIR-01"] == (2, "M6 x 25") and rows["J-BASE-02"] == (0, "M6 x 16")
    assert total == 84 and sum(c for c, _ in rows.values()) == 84


def test_power_unit_share_from_electrical():
    # B2 carries the power unit's mass from ELECTRICAL's parts list, not a typed share
    import csv
    with open(pack.ELEC_PARTS, encoding="utf-8") as f:
        unit = next(float(r["mass_each_kg"]) for r in csv.DictReader(f) if r["part_number"] == "710001")
    m = pack.Model()
    b2 = pack.PIECE["1-04"]
    back = m.roll[pack.resolve(m.roll, "B")]["kg_each"]
    assert abs(b2.kg - (back + unit)) < 1e-9, (b2.kg, back, unit)


def _bom_copy(edit, tmp):
    """The master BOM with edit(rows) applied, written to tmp."""
    import csv
    with open(pack.MASTER_BOM, encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols, rows = rd.fieldnames, list(rd)
    edit(rows)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)


def test_numbers_match_the_master_bom():
    # every number on a label is the BOM's number for that name (K13), and the ones the reviewer found are filled
    m = pack.Model()
    by_pn, _ = m.bom
    for tag, pn in (("1-06", "210102"), ("1-09", "210103"), ("1-10", "210104"), ("1-13", "510102"), ("1-14", "510104"),
                    ("1-16", "510103"), ("2-14", "810201"), ("2-16", "810101"), ("1-01", "110401")):
        p = pack.PIECE[tag]
        assert p.pn == pn and by_pn[pn][0] == p.name, (tag, p.pn, p.name)
    assert "K13" not in failing(m)


def test_tbd_piece_takes_its_bom_number(tmp=Path(__file__).resolve().parent / "_bom_test.csv"):
    # when an owner's list lands with the piece's exact name, the label gets the number without a code change
    dr = pack.PIECE["2-03"]
    assert dr.pn_declared.startswith("TBD")

    def add(rows):
        rows.append(dict(rows[-1], part_number="350301", name=dr.name, name_vi="Khối trang trí phải (thử)"))
    _bom_copy(add, tmp)
    try:
        m = pack.Model(bom_path=tmp)
        assert dr.pn == "350301" and dr.vi == "Khối trang trí phải (thử)", (dr.pn, dr.vi)
        assert "2-03" in m.filled and "K13" not in failing(m)
    finally:
        tmp.unlink()
        pack.Model()   # back to the real BOM
    assert dr.pn == dr.pn_declared


def test_number_named_otherwise_is_caught(tmp=Path(__file__).resolve().parent / "_bom_test2.csv"):
    # a label number whose BOM name differs from the piece's name fails K13
    def rename(rows):
        for r in rows:
            if r["part_number"] == "210102":
                r["name"] = "WALL - PANEL ASSY - SIDE LOWER - RH - RENAMED"
    _bom_copy(rename, tmp)
    try:
        assert "K13" in failing(pack.Model(bom_path=tmp))
    finally:
        tmp.unlink()
        pack.Model()


def test_ledge_carton_counts_the_screen_rail_once():
    # the roll-up's ledge line carries the screen rail 818102 since INTERIOR's list merged; no extra mass on top
    m = pack.Model()
    ledge = pack.PIECE["2-16"]
    assert ledge.extra_kg == 0 and abs(ledge.kg - m.roll[pack.resolve(m.roll, "LEDGE")]["kg_each"]) < 1e-9, ledge.kg


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    bad = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL {name}: {e}")
    print(f"{len(tests) - bad} of {len(tests)} passed")
    sys.exit(1 if bad else 0)
