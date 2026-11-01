"""Offline tests for pdf_traps.py: drawing PDFs read back for the PM's four drawing traps (2026-11-01).

The synthetic sheets are written with PyMuPDF on named layers, which it reads back the way it reads Fusion's
exports (a closed outline as one quad, each layer by name). fixtures/fusion-export-831001.pdf is a real Fusion
export (JOINTS' spigot drawing as merged on 2026-11-01): hidden lines in 2 views, a 4-corner symbol, the
value 8 printed twice."""

import os
import sys

import fitz
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import pdf_traps as T  # noqa: E402

MM = 72.0 / 25.4
OUTLINE = [(300, 260), (310, 257.5), (310, 267.5), (300, 265), (300, 260)]
TRIANGLE = [(300, 260), (310, 257.5), (310, 267.5), (300, 260)]
VIEW_1 = [(50 + 5 * i, 50, 53 + 5 * i, 50) for i in range(6)]            # dashes of one hidden line
VIEW_2 = [(200, 60 + 4 * i, 200, 62 + 4 * i) for i in range(5)]           # another view, far away


def P(x, y):
    return fitz.Point(x * MM, y * MM)


def fs(cap):
    return cap / T.CAP * MM


def sheet(tmp_path, name="d.pdf", outline=OUTLINE, hidden=(), dims=("296", "260", "72"), note_cap=2.5,
          tb_cap=1.8, layered=True, one_sketch=False, tb_x=240.0):
    doc = fitz.open()
    page = doc.new_page(width=420 * MM, height=297 * MM)

    def oc(n):
        return doc.add_ocg(n, on=True) if layered else 0
    sym, circ, hid, dim, tb = (oc(n) for n in (T.SYMBOL, T.SYMBOL + " CIRCLES", "Hidden", "FD_Dimensions", "TITLEBLOCK"))
    page.draw_polyline([P(x, y) for x, y in outline], oc=sym)
    for r in (5.0, 2.5):
        page.draw_circle(P(319, 262.5), r * MM, oc=sym if one_sketch else circ)
    for x0, y0, x1, y1 in hidden:
        page.draw_line(P(x0, y0), P(x1, y1), oc=hid)
    for i, d in enumerate(dims):
        page.insert_text(P(60 + 30 * i, 120), d, fontsize=fs(2.5), oc=dim)
    page.insert_text(P(30, 250), "1. GENERAL TOLERANCE: ISO 2768-m.", fontsize=fs(note_cap))
    page.insert_text(P(tb_x, 280), "PROJECT", fontsize=fs(tb_cap), oc=tb)
    path = str(tmp_path / name)
    doc.save(path)
    return path


def rules(fs_):
    return sorted((r, s) for r, s, _m, _f in fs_)


def test_a_clean_sheet_has_no_findings(tmp_path):
    assert T.findings(sheet(tmp_path)) == []


def test_a_triangle_symbol_is_major(tmp_path):
    fs_ = T.findings(sheet(tmp_path, outline=TRIANGLE))
    assert rules(fs_) == [("symbol-outline", "major")]
    assert "3 corners" in fs_[0][2] and "triangle" in fs_[0][2]


def test_the_circles_in_the_outlines_sketch_dont_count_as_corners(tmp_path):
    assert T.findings(sheet(tmp_path, one_sketch=True)) == []


def test_hidden_lines_count_by_view_and_can_be_allowed(tmp_path):
    path = sheet(tmp_path, hidden=VIEW_1 + VIEW_2)
    fs_ = T.findings(path)
    assert rules(fs_) == [("hidden-lines", "minor")]
    assert "2 view region(s)" in fs_[0][2] and "11 dash pieces" in fs_[0][2]
    assert T.findings(path, allow_hidden_views=2) == []
    assert rules(T.findings(path, allow_hidden_views=1)) == [("hidden-lines", "minor")]


def test_small_notes_are_major_and_title_block_labels_may_be_18(tmp_path):
    fs_ = T.findings(sheet(tmp_path, note_cap=1.52))
    assert rules(fs_) == [("letter-height", "major")]
    assert "1.52 mm" in fs_[0][2]
    assert T.findings(sheet(tmp_path, "tb.pdf", tb_cap=1.81)) == []
    assert rules(T.findings(sheet(tmp_path, "tb2.pdf", tb_cap=1.5))) == [("letter-height", "major")]


def test_a_sheet_with_no_layers_finds_its_title_block_by_place(tmp_path):
    assert T.findings(sheet(tmp_path, layered=False, dims=())) == []                     # 1.8 mm label bottom right
    fs_ = T.findings(sheet(tmp_path, "left.pdf", layered=False, dims=(), tb_x=40.0))     # the same label far left
    assert rules(fs_) == [("letter-height", "major")]


def test_a_drawn_title_box_in_the_corner_sets_the_title_block(tmp_path):
    """drawgen's title block is 180 x 90 mm: its 1.8 mm labels near the box's top are still title-block labels."""
    doc = fitz.open()
    page = doc.new_page(width=841 * MM, height=594 * MM)
    page.draw_rect(fitz.Rect(20 * MM, 10 * MM, 831 * MM, 584 * MM))                     # frame
    page.draw_rect(fitz.Rect(651 * MM, 494 * MM, 831 * MM, 584 * MM))                   # title block, 180 x 90
    page.insert_text(P(652, 498), "PROJECT", fontsize=fs(2.0))
    path = str(tmp_path / "g.pdf")
    doc.save(path)
    assert T.findings(path) == []
    doc2 = fitz.open()
    pg2 = doc2.new_page(width=841 * MM, height=594 * MM)
    pg2.draw_rect(fitz.Rect(20 * MM, 10 * MM, 831 * MM, 584 * MM))
    pg2.draw_rect(fitz.Rect(651 * MM, 494 * MM, 831 * MM, 584 * MM))
    pg2.insert_text(P(600, 498), "LABEL OUTSIDE", fontsize=fs(2.0))                    # left of the box
    path2 = str(tmp_path / "g2.pdf")
    doc2.save(path2)
    assert rules(T.findings(path2)) == [("letter-height", "major")]


def test_symbol_layers_holding_only_circles_are_left_out(tmp_path):
    doc = fitz.open()
    page = doc.new_page(width=420 * MM, height=297 * MM)
    a, b, c = (doc.add_ocg(T.SYMBOL + s, on=True) for s in ("(6)", "(7)", "(8)"))       # the proof sheet's layers
    page.draw_polyline([P(x, y) for x, y in OUTLINE], oc=a)
    page.draw_circle(P(319, 262.5), 5 * MM, oc=b)
    page.draw_circle(P(319, 262.5), 2.5 * MM, oc=c)
    path = str(tmp_path / "s.pdf")
    doc.save(path)
    assert T.read(path)[0]["symbol_corners"] == {T.SYMBOL + "(6)": 4}
    assert T.findings(path) == []


def test_a_value_printed_twice_is_minor(tmp_path):
    fs_ = T.findings(sheet(tmp_path, dims=("1218.5", "1451", "1218.5")))
    assert rules(fs_) == [("dimension-twice", "minor")]
    assert "1218.5" in fs_[0][2] and "1451" not in fs_[0][2]


def test_a_real_fusion_export():
    path = os.path.join(HERE, "fixtures", "fusion-export-831001.pdf")
    pg = T.read(path)[0]
    assert pg["symbol_corners"] == {T.SYMBOL: 4}
    assert len(pg["hidden_views"]) == 2 and pg["hidden_pieces"] == 52
    assert pg["small_texts"] == []
    assert rules(T.findings(path)) == [("dimension-twice", "minor"), ("hidden-lines", "minor")]
    assert rules(T.findings(path, allow_hidden_views=2)) == [("dimension-twice", "minor")]


def test_the_command_line(tmp_path, capsys):
    assert T.main([sheet(tmp_path)]) == 0
    assert T.main([sheet(tmp_path, "t.pdf", outline=TRIANGLE)]) == 1
    assert "symbol-outline" in capsys.readouterr().out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
