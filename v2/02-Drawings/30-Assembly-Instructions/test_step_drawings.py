#!/usr/bin/env python3
"""Tests for step_drawings.py, run with the drawing generator's own Python:

    $HOME/.cache/spaceship-drawgen/venv-ocp7.8.1-mupdf1.27.2/bin/python v2/02-Drawings/30-Assembly-Instructions/test_step_drawings.py

The whole set is drawn once into a scratch folder (about 2 minutes) and every test reads that draw: the pictures redraw
byte for byte the same as the committed ones, each picture's balloons are exactly the step's parts, every part the
step's text names is in its picture (or left out on purpose, and said so), and the read-back catches a balloon that is
missing, wrong or off its part.
"""
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True          # no __pycache__ in the guide's folder
sys.path.insert(0, str(HERE))
import step_drawings as sd  # noqa: E402

pack = sd.pack
_DRAW = {}


def drawn():
    """{step: (pdf bytes, png bytes, record, parts as drawn)} for every picture step, drawn once."""
    if not _DRAW:
        with tempfile.TemporaryDirectory() as tmp:
            for n in sd.picture_steps():
                pdf, png, rec = sd.draw_step(n, tmp)
                lift = sd.EXPLODE.get(n, {})
                parts = [sd.exploded(p, lift[p.label]) if p.step == n and p.label in lift else p for p in sd.parts_up_to(n)]
                sd.render(pdf, png)
                _DRAW[n] = (pdf, png.read_bytes(), rec, parts)
    return _DRAW


def test_the_set_redraws_byte_for_byte_as_committed():
    # a fresh draw of every step equals the committed picture byte for byte (the --check), and no other picture is in img/
    bad = [n for n, (_pdf, png, _r, _p) in drawn().items()
           if not pack.step_image(n).exists() or pack.step_image(n).read_bytes() != png]
    assert not bad, "pictures not current (run step_drawings.py): %s" % bad
    extra = sorted({p.name for p in sd.IMG.glob("*-STEP-*_IMG.png")} - {pack.step_image(n).name for n in drawn()})
    assert not extra, extra


def test_every_picture_reads_back_clean():
    for n, (pdf, _png, rec, parts) in drawn().items():
        faults = sd.check_pdf(pdf, rec, parts)
        assert not faults, (n, faults)


def test_balloons_are_the_steps_parts():
    # each picture balloons exactly what the step's Parts line names (and the parts fitted here that ship with an earlier
    # piece); a step's earlier parts are never ballooned
    for n, (_pdf, _png, rec, _parts) in drawn().items():
        st = next(s for s in pack.STEPS if s["n"] == n)
        assert sorted(b["label"] for b in rec["balloons"]) == sorted(sd.new_labels(st)), (n, rec["balloons"])
        assert set(rec["new"]) == set(sd.new_labels(st)), n


def _codes():
    """{position code or label: label} for every piece the text can name: its label, and its position code if it has one."""
    out = {}
    for p in pack.PIECES:
        if p.kind != "piece":
            continue
        out[p.tag] = p.tag
        if p.pos and p.pos != "-":
            out[p.pos] = p.tag
    return out


def test_every_part_the_text_names_is_drawn():
    # a part the step's text names (by its packing label or its position code) and fitted by then is in the picture,
    # or the picture says it was left out so the step shows; and nothing new is drawn that the text doesn't name
    codes = _codes()
    for n, (_pdf, _png, rec, _parts) in drawn().items():
        st = next(s for s in pack.STEPS if s["n"] == n)
        text = " ".join([st["A"], st["B"], st.get("caution", ""), st["check"]] + list(st["tags"]))
        named = {codes[w] for w in codes if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(w), text)}
        fitted = {t for s in pack.STEPS if s["n"] <= n for t in s["tags"]}
        drawable = {t for t in fitted if t in pack.CAD or t in pack.SKEL}
        missing = sorted(t for t in named & drawable if t not in rec["drawn"] and t not in rec["hidden"])
        assert not missing, (n, missing)
        unnamed = sorted(set(rec["new"]) - set(sd.new_labels(st)))
        assert not unnamed, (n, unnamed)
        assert set(rec["hidden"]).isdisjoint(rec["new"]), n           # a cut-away never hides the step's own parts


def test_parts_without_cad_are_dashed_and_marked():
    # a piece with no CAD entry is drawn from its skeleton block, dashed, and its balloon carries CAD TO COME
    for n, (pdf, _png, rec, _parts) in drawn().items():
        for b in rec["balloons"]:
            assert (b["label"] in rec["no_cad"]) == (b["tbc"] is not None), (n, b)
        assert all(t not in pack.CAD for t in rec["no_cad"]), (n, rec["no_cad"])
    doc = sd.fitz.open("pdf", drawn()[5][0])           # step 5: B3 and B4 have no CAD yet
    dashed = [d for d in doc[0].get_drawings() if d.get("dashes") and d["dashes"] not in ("[] 0", "")]
    assert dashed, "step 5 draws no dashed line"


def test_readback_catches_a_wrong_missing_or_misplaced_balloon():
    pdf, _png, rec, parts = drawn()[4]
    assert not sd.check_pdf(pdf, rec, parts)
    label = rec["balloons"][0]["label"]
    # the label rubbed out of its balloon
    doc = sd.fitz.open("pdf", pdf)
    page = doc[0]
    for r in page.search_for(label):
        page.add_redact_annot(r)
    page.apply_redactions(images=0, graphics=0)
    faults = sd.check_pdf(doc.tobytes(), rec, parts)
    assert any("holds 0 texts" in f for f in faults), faults
    # another label written in its place, at the same spot and size
    doc = sd.fitz.open("pdf", pdf)
    page = doc[0]
    span = next(sp for b in page.get_text("dict")["blocks"] for ln in b.get("lines", []) for sp in ln["spans"]
                if sp["text"].strip() == label)
    page.add_redact_annot(sd.fitz.Rect(span["bbox"]))
    page.apply_redactions(images=0, graphics=0)
    page.insert_text(span["origin"], "1-05", fontsize=span["size"], fontname="helv")
    faults = sd.check_pdf(doc.tobytes(), rec, parts)
    assert any("the step names" in f for f in faults), faults
    # a leader that ends 50 mm off its part: its 3D end moved toward the viewer, out of the surface it was on
    nv = sd.camera(4).n
    moved = dict(rec, balloons=[dict(b, tip3d=tuple(b["tip3d"][k] + 50.0 * nv[k] for k in range(3))) if i == 0 else b
                                for i, b in enumerate(rec["balloons"])])
    faults = sd.check_pdf(pdf, moved, parts)
    assert any("off its part" in f for f in faults), faults


def test_cad_picks_match_pack():
    # the pictures pick each piece's solids by pack.py's own CAD rules: the same count as pack.cad_solids, piece by piece
    for tag, spec in pack.CAD.items():
        for sp in spec.get("parts", [spec]):
            mine, theirs = len(sd.pick(sp)), len(pack.cad_solids(sp)[0])
            assert mine == theirs, (tag, mine, theirs)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    bad = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS %s" % name)
        except AssertionError as e:
            bad += 1
            print("FAIL %s: %s" % (name, e))
    print("%d of %d passed" % (len(tests) - bad, len(tests)))
    sys.exit(1 if bad else 0)
