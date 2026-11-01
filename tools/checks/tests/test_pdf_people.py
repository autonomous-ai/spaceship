"""The owner's rule (2026-11-01): a drawing's Created by field and its PDF author read "Autonomous"; any other name
is flagged, and so is any person's name anywhere in a drawing PDF or its metadata. The names here are made up."""

import os
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_drawings as cd  # noqa: E402

NAMES = ["Jane Roe", "Jane", "Roe"]


def _pdf(path, rows, author="Autonomous", creator="Fusion Drawings", xmp_creator=None, annot=None):
    """A one-sheet PDF with text at (x, y) points; metadata as given."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=1191, height=842)
    for x, y, text in rows:
        page.insert_text((x, y), text, fontsize=7)
    if annot:
        a = page.add_text_annot((100, 100), "note")
        a.set_info(title=annot)
        a.update()
    doc.set_metadata({"author": author, "creator": creator, "producer": "test"})
    if xmp_creator:
        doc.set_xml_metadata('<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-'
                             'syntax-ns#"><rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>'
                             '<rdf:Seq><rdf:li>%s</rdf:li></rdf:Seq></dc:creator></rdf:Description></rdf:RDF>'
                             '</x:xmpmeta>' % xmp_creator)
    doc.save(path)
    doc.close()
    return path


# the three title blocks on main: Fusion's (label row, value under it, the next cell on the same row), drawgen's
# (MADE BY over its value, APPROVED next to it), ELECTRICAL's (DATE / BY with its value on the same row)
FUSION = [(819, 690, "Created by"), (992, 690, "Approved by"), (819, 701, "Autonomous"), (932, 701, "31/10/26")]
DRAWGEN = [(849, 595, "MADE BY"), (1025, 595, "APPROVED"), (849, 605, "Autonomous"), (1025, 605, "not released"),
           (849, 622, "PROJECTION")]
ELEC = [(643, 785, "DATE / BY"), (751, 785, "2026-11-01 / Autonomous"), (643, 798, "SOURCE electrical_model.py")]


def _vals(path):
    with fitz.open(path) as d:
        return [v for pg in d for v in cd._by_values(pg)]


def test_each_title_block_gives_its_created_by_value(tmp_path):
    assert _vals(_pdf(str(tmp_path / "f.pdf"), FUSION)) == [("CREATED BY", "Autonomous")]
    assert _vals(_pdf(str(tmp_path / "g.pdf"), DRAWGEN)) == [("MADE BY", "Autonomous")]
    assert _vals(_pdf(str(tmp_path / "e.pdf"), ELEC)) == [("DATE / BY", "Autonomous")]
    blank = [r for r in FUSION if r[2] != "Autonomous"]
    assert _vals(_pdf(str(tmp_path / "b.pdf"), blank)) == [("CREATED BY", "")]       # the date isn't a name
    # a sentence in the notes that says who made the drawing isn't the field (drawgen's sheet 2 after #291)
    note = [(100, 300, "Source: FEATURE-RATIONALE.md. Made by tools/drawgen (D-112) from that STEP.")]
    assert _vals(_pdf(str(tmp_path / "n.pdf"), DRAWGEN + note)) == [("MADE BY", "Autonomous")]


def test_a_drawing_that_reads_autonomous_everywhere_passes(tmp_path):
    for rows in (FUSION, DRAWGEN, ELEC):
        assert cd.drawing_people(_pdf(str(tmp_path / "ok.pdf"), rows), NAMES) == ([], [])


def test_any_other_name_and_a_blank_or_missing_field_are_flagged(tmp_path):
    rows = [r if r[2] != "Autonomous" else (r[0], r[1], "ELECTRICAL Engineer") for r in FUSION]
    probs, hits = cd.drawing_people(_pdf(str(tmp_path / "a.pdf"), rows, author="ELECTRICAL Engineer"), NAMES)
    assert probs == ["its CREATED BY field reads 'ELECTRICAL Engineer' (sheet 1)",
                     "its PDF author reads 'ELECTRICAL Engineer'"] and hits == []
    probs, _h = cd.drawing_people(_pdf(str(tmp_path / "b.pdf"), [(100, 100, "NOTES: none")], author=""), NAMES)
    assert probs == ["no Created by field in its title block", "its PDF author reads nothing"]
    probs, _h = cd.drawing_people(_pdf(str(tmp_path / "c.pdf"), FUSION, xmp_creator="Fusion user"), NAMES)
    assert probs == ["its XMP creator reads 'Fusion user'"]


def test_a_persons_name_anywhere_is_found_and_shown_masked(tmp_path):
    rows = [r if r[2] != "Autonomous" else (r[0], r[1], "Jane Roe") for r in FUSION]
    probs, hits = cd.drawing_people(_pdf(str(tmp_path / "a.pdf"), rows), NAMES)
    assert "its CREATED BY field reads 'Jane Roe' (sheet 1)" in probs
    assert hits == ["a person's name (J*** R**)"]                   # once, masked
    # in the notes, an annotation's author, the metadata, an e-mail, a home folder path
    _p, hits = cd.drawing_people(_pdf(str(tmp_path / "b.pdf"), FUSION + [(100, 300, "checked: roe")]), NAMES)
    assert hits == ["a person's name (R**)"]
    _p, hits = cd.drawing_people(_pdf(str(tmp_path / "c.pdf"), FUSION, annot="Jane"), NAMES)
    assert hits == ["a person's name (J***)"]
    _p, hits = cd.drawing_people(_pdf(str(tmp_path / "d.pdf"), FUSION + [(100, 300, "ask x.y@example.com")]), [])
    assert hits == ["an e-mail address (x**@...)"]
    _p, hits = cd.drawing_people(_pdf(str(tmp_path / "e.pdf"), FUSION, creator="/Users/janer/fusion"), [])
    assert hits == ["a home folder path (/Users/j****/...)"]
    # whole words only: 'Roebuck' isn't 'Roe'
    assert cd.drawing_people(_pdf(str(tmp_path / "f.pdf"), FUSION + [(100, 300, "ROEBUCK HINGE")]), NAMES) == ([], [])


def test_every_drawing_pdf_is_checked_and_the_generators_go_to_its_group(tmp_path):
    _pdf(str(tmp_path / "v2/02-Drawings/base/111401_P01_BASE-X_DWG.pdf"), [r for r in FUSION if r[2] != "Autonomous"],
         author="")
    _pdf(str(tmp_path / "v2/02-Drawings/base/111101_P01_BASE-Y_DWG.pdf"),
         [r if r[2] != "Autonomous" else (r[0], r[1], "tools/drawgen (D-112)") for r in DRAWGEN], author="",
         creator="drawgen")
    _pdf(str(tmp_path / "v2/02-Drawings/wall/V2-SWL-01_P01_WALL-X_DWG.pdf"), FUSION)
    # a proof sheet: no Created by rule, but a person's name there still counts (the repo is public)
    _pdf(str(tmp_path / "v2/02-Drawings/proof/V2-SWL-00_P01_WALL-Z_DWG.pdf"), [(100, 100, "drawn: Jane Roe")], author="")
    fs, ran = cd.check_drawing_people(str(tmp_path), names=NAMES)
    got = sorted((f.rule, f.subject, f.severity, f.owner) for f in fs)
    assert ran and got == [("drawing-author", "111101_P01_BASE-Y_DWG", "major", "Drawing Generator"),
                           ("drawing-author", "111401_P01_BASE-X_DWG", "major", "BASE"),
                           ("person-name", "V2-SWL-00_P01_WALL-Z_DWG", "severe", "Fusion Engineer 2")]
    assert all(f.evidence["model"] == "pdf-people" for f in fs)


def test_the_names_come_from_outside_the_repos_files(tmp_path, monkeypatch):
    monkeypatch.setenv("SPACESHIP_PERSON_NAMES", "Jane Roe, Claude Bot, x")
    names = cd.person_names(repo=str(tmp_path))            # no git history there
    assert {"Jane Roe", "Jane", "Roe"} <= set(names) and not any("Claude" in n for n in names) and "x" not in names
    assert cd.mask("Jane Roe") == "J*** R**"
