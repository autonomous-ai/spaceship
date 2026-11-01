#!/usr/bin/env python3
"""Tests of drawgen's assembly sheets (tools/drawgen/assembly.py). Run in drawgen's own environment:

    <venv>/bin/python tools/drawgen/tests/test_assembly.py          # prints "N of N passed"
    <venv>/bin/python -m pytest -q tools/drawgen/tests/test_assembly.py

1. The sample sheets (BASE's side band 110101, CEILING's panel C1 410101, AIR's air column 610101) draw from their
   team STEPs and lists on this tree and read back: every table row equals its parts-list row, every balloon sits on
   its part in the STEP, every part the STEP has carries a balloon, the interface sizes measure again from the STEP,
   and no label touches a line.
2. The same sources give the same bytes.
3. The read-back is not a rubber stamp: it fails a table cell that differs from the list, a balloon moved off its
   part, a balloon that names another part, a part of the STEP without a balloon, and a line through a label.
4. Rows the STEP doesn't model get a * and no balloon; a part the STEP puts under the assembly but the list doesn't
   is drawn as a reference outline with a note naming its own parent.
5. Quantities by length are in metres (family 84); wrapped cells join back word for word; a cell with Ø wraps to
   its printed width.
6. A sheet never goes over a PDF drawgen didn't make (a Fusion drawing).
7. Spigots and glide stems a section cuts along are drawn whole (ISO 128-50); one the plane misses isn't drawn.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import fitz  # noqa: E402

import assembly  # noqa: E402
import readback  # noqa: E402
from compose import NotDrawable  # noqa: E402
from sheet import Sheet  # noqa: E402

TMP = tempfile.mkdtemp(prefix="drawgen-asm-test-")
SAMPLE = ["110101", "410101", "610101"]
_MADE = {}


def _made(pn):
    """The sample sheet, drawn once per run."""
    if pn not in _MADE:
        team, entry = assembly.assemblies()[pn]
        final, rep = assembly.generate(pn, team, entry, os.path.join(TMP, "sample"))
        _MADE[pn] = (final, rep)
    return _MADE[pn]


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


def test_samples_draw_and_read_back():
    for pn in SAMPLE:
        final, rep = _made(pn)
        fails, st = assembly.check(final)
        assert not fails, (pn, fails)
        assert st["rows"] > 0 and st["balloons"] > 0, (pn, st)
    _f, rep = _made("110101")
    assert rep["data"]["interfaces"] and len(rep["data"]["interfaces"][0]["points"]) == 10


def test_same_sources_same_bytes():
    team, entry = assembly.assemblies()["410101"]
    a = assembly.generate("410101", team, entry, os.path.join(TMP, "a"))[0]
    b = assembly.generate("410101", team, entry, os.path.join(TMP, "b"))[0]
    with open(a, "rb") as fa, open(b, "rb") as fb:
        assert fa.read() == fb.read()


def test_readback_fails_a_table_cell_that_differs_from_the_list():
    final, _rep = _made("610101")
    data = readback.read_data(fitz.open(final))
    src = os.path.join(assembly.inputs.REPO, [s for s in data["sources"] if s["role"] == "parts list"][0]["path"])
    alt = os.path.join(TMP, "altered_list.csv")
    with open(src, encoding="utf-8") as f:
        txt = f.read()
    assert "AIR - COLUMN FOOT PLATE," in txt
    with open(alt, "w", encoding="utf-8") as f:
        f.write(txt.replace("AIR - COLUMN FOOT PLATE,", "AIR - COLUMN FOOT PLATE - CHANGED,", 1))

    def point_at_alt(d):
        for s in d["sources"]:
            if s["role"] == "parts list":
                s["path"] = alt
    bad = _with_data(final, os.path.join(TMP, "t_table.pdf"), point_at_alt)
    fails, _st = assembly.check(bad)
    assert any("table item 1 NAME" in f and "CHANGED" in f for f in fails), fails


def test_readback_fails_a_balloon_moved_off_its_part():
    final, _rep = _made("110101")

    def move(d):
        b = d["balloons"][0]
        b["tip3d"] = [b["tip3d"][0] + 30.0, b["tip3d"][1], b["tip3d"][2]]
    bad = _with_data(final, os.path.join(TMP, "t_moved.pdf"), move)
    fails, _st = assembly.check(bad)
    assert any("balloon 1:" in f for f in fails), fails


def test_readback_fails_a_balloon_that_names_another_part():
    final, _rep = _made("110101")

    def rename(d):
        d["balloons"][0]["pn"] = "831002"
    bad = _with_data(final, os.path.join(TMP, "t_rename.pdf"), rename)
    fails, _st = assembly.check(bad)
    assert any("names 831002" in f for f in fails), fails


def test_readback_fails_a_part_without_a_balloon():
    final, _rep = _made("610101")

    def drop(d):
        d["balloons"] = [b for b in d["balloons"] if b["pn"] != "611104"]
    bad = _with_data(final, os.path.join(TMP, "t_drop.pdf"), drop)
    fails, _st = assembly.check(bad)
    assert any("611104 is in the STEP but has no balloon" in f for f in fails), fails


def test_readback_fails_a_line_through_a_label():
    final, _rep = _made("410101")
    doc = fitz.open(final)
    page = doc[0]
    data = readback.read_data(doc)
    xs, top = data["table"]["x"], data["table"]["rows"][0]["top"]
    mm = 72.0 / 25.4
    y = (data["sheet_h"] - (top - 2.0)) * mm
    sh = page.new_shape()
    sh.draw_line(fitz.Point((xs[2] + 2) * mm, y), fitz.Point((xs[3] - 2) * mm, y))
    sh.finish(width=0.25 * mm, color=(0, 0, 0))
    sh.commit()
    bad = os.path.join(TMP, "t_line.pdf")
    doc.save(bad)
    fails, _st = assembly.check(bad)
    assert any("a line runs through text" in f for f in fails), fails


def test_unmodelled_rows_and_reference_parts():
    _f, rep = _made("410101")
    assert set(rep["data"]["unmodelled"]) >= {"838001", "838003", "848001"}, rep["data"]["unmodelled"]
    text = fitz.open(_made("410101")[0])[0].get_text()
    assert "3*" in text and "not in the STEP" in text
    _f, rep = _made("610101")
    assert rep["data"]["refs"] == ["610301"]
    text = fitz.open(_made("610101")[0])[0].get_text()
    assert "reference outline" in text and "under 610000" in " ".join(text.split())


def test_units_join_and_printed_widths():
    assert assembly.unit_of({"part_number": "848001"}) == "m"
    assert assembly.unit_of({"part_number": "838003", "unit": "pcs"}) == ""
    assert assembly.qty_text("4") == "4" and assembly.qty_text("1.199") == "1.199"
    assert assembly._join(["BASE - TUBE END CAP - BLACK -", "HOLD"]) == "BASE - TUBE END CAP - BLACK - HOLD"
    assert assembly._join(["SHEREX CAH3-", "610-4.2"]) == "SHEREX CAH3-610-4.2"
    sh = Sheet("A1")
    t = "HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL"
    lines = assembly.wrap2(sh, t, 2.5, 72.0)
    y = 500.0
    for ln in lines:
        sh.text(100.0, y, ln, 2.5)
        y -= 5.0
    sh.flush()
    mm = 72.0 / 25.4
    for b in sh.page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                assert (sp["bbox"][2] - sp["bbox"][0]) / mm <= 72.0 + 0.05, (sp["text"], sp["bbox"])
    assert assembly._join(lines) == t


def test_shafts_cut_along_their_axis_are_drawn_whole():
    """ISO 128-50: the entry's spigots and glide stems are drawn whole where a section cuts them, not hatched; a
    spigot the plane doesn't cut (in front of section C) is not drawn in it at all."""
    team, entry = assembly.assemblies()["110101"]
    assert set(entry["unhatched"]) == {"831001", "118002"}
    assy = assembly.Assy("110101", team, entry)
    views = assembly.plan_views(assy)
    secs = {v.letter: v for v in views.values() if v.kind == "section"}
    for letter, v in secs.items():
        hatched = {assy.occs[i].item.pn for i, _l in v.hatch}
        assert not hatched & {"831001", "118002"}, (letter, hatched)
    drawn = lambda v, pn: any(ps for o, ps in zip(assy.occs, v.prims) if o.item.pn == pn)
    assert drawn(secs["A"], "118002") and drawn(secs["B"], "831001")
    assert not drawn(secs["C"], "831001"), "a spigot in front of section C is drawn in it"
    assert {assy.occs[i].item.pn for i, _l in secs["A"].hatch} >= {"111101", "111601"}


def test_never_goes_over_a_fusion_drawing():
    out = os.path.join(TMP, "fusion")
    os.makedirs(out, exist_ok=True)
    _f, rep = _made("410101")
    d = fitz.open()
    d.new_page()
    d.set_metadata({"creator": "Autodesk Fusion"})
    d.save(os.path.join(out, rep["dwg"] + ".pdf"))
    team, entry = assembly.assemblies()["410101"]
    try:
        assembly.generate("410101", team, entry, out)
        raise AssertionError("went over a Fusion drawing")
    except NotDrawable as e:
        assert "not made by drawgen" in str(e)


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
