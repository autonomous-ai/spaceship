"""D-178 (the Lead, 2026-11-01): a maker's standard panel cut-out, cited by the maker's own drawing (Neutrik's D-size:
Ø24 with two Ø3.2 screw holes on 19 x 24, each 15.3 from its centre), stands as an edge and spacing exception, but
only on the parts that carry that connector, each listed by part and feature in config/cutout-exceptions.csv. A new
use needs its own row, and only the cut-out's own webs are excused."""

import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_geometry as cg  # noqa: E402
import stepfile as sf  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROWS = cg.load_cutout_exceptions(ROOT)


def _d_size(x, z, main=24.0, screw=3.2, pitch=(19.0, 24.0), y=848.5, flip=False):
    """Holes as B2's skin has them: axis -Y, in the X-Z plane at the skin's mid-thickness (WALL's 210202 STEP)."""
    w, h = pitch[0] / 2.0, pitch[1] / 2.0
    s = -1.0 if flip else 1.0
    return [sf.Hole(1, (x, y, z), (0.0, -1.0, 0.0), main, 3.0, []),
            sf.Hole(2, (x + w, y, z + s * h), (0.0, -1.0, 0.0), screw, 3.0, []),
            sf.Hole(3, (x - w, y, z - s * h), (0.0, -1.0, 0.0), screw, 3.0, [])]


def _covered(rows, holes):
    pairs = cg.cutout_pairs(rows, holes)
    mains = {a for a, _b in pairs}
    return [h.center for h in holes if id(h) in mains]


def test_the_rows_list_b2s_two_cut_outs_and_711003s_by_part_feature_and_maker_drawing():
    assert sorted(ROWS) == ["211402", "711003"]
    b2 = {r["place"]: r for r in ROWS["211402"]}
    assert sorted(b2) == ["X 120 Z 313", "X 170 Z 375"]
    assert "NE8FDY-C6-B" in b2["X 170 Z 375"]["feature"] and "ST-NE8FDY-C6" in b2["X 170 Z 375"]["maker_drawing"]
    assert "NAC3MPX-TOP" in b2["X 120 Z 313"]["feature"] and "ST-NAC3MPX-TOP" in b2["X 120 Z 313"]["maker_drawing"]
    (box,) = ROWS["711003"]
    assert box["place"] == "" and "ST-NAC3MPX-TOP" in box["maker_drawing"]
    for rows in ROWS.values():
        for r in rows:
            assert r["ruling"].startswith("D-178") and r["status"].startswith("source") and r["pitch_mm"] == "19 x 24"
    # the pattern's screws sit 15.3 from the centre: the Lead's figure
    assert math.hypot(9.5, 12.0) == pytest.approx(15.3, abs=0.01)


def test_b2s_lan_jack_and_inlet_are_covered_at_their_places_and_nowhere_else():
    lan, inlet = _d_size(170.0, 375.0), _d_size(120.0, 313.0, flip=True)      # either diagonal: front or rear view
    assert _covered(ROWS["211402"], lan + inlet) == [(170.0, 848.5, 375.0), (120.0, 848.5, 313.0)]
    assert _covered(ROWS["211402"], _d_size(120.0, 375.0)) == []          # the jack's old place: no row there
    assert _covered(ROWS["211402"], lan + _d_size(300.0, 375.0)) == [(170.0, 848.5, 375.0)]   # a third: its own row
    assert _covered(ROWS.get("211401", []), _d_size(170.0, 375.0)) == []    # B1's skin: no row, no exception
    assert _covered(ROWS["211402"], _d_size(120.0, 313.0, main=23.8)) == [(120.0, 848.5, 313.0)]   # the inlet's Ø23.8
    assert _covered(ROWS["211402"], _d_size(170.0, 375.0, main=23.8)) == []   # the jack's drawing says Ø24 at least


def test_711003_has_one_cut_out_anywhere_and_a_second_is_not_covered():
    one = _d_size(40.0, 25.0, y=0.0)
    assert _covered(ROWS["711003"], one) == [(40.0, 0.0, 25.0)]
    assert len(_covered(ROWS["711003"], one + _d_size(140.0, 25.0, y=0.0))) == 1


def test_only_the_makers_pattern_matches():
    rows = ROWS["711003"]
    assert _covered(rows, _d_size(0.0, 0.0, main=24.5)) == []            # a bigger main hole thins the web
    assert _covered(rows, _d_size(0.0, 0.0, screw=3.4)) == []            # a bigger screw hole, the same
    assert _covered(rows, _d_size(0.0, 0.0, pitch=(0.0, 30.61))) == []   # 15.3 out but not on 19 x 24
    assert _covered(rows, _d_size(0.0, 0.0, pitch=(19.3, 24.0))) == []   # off the maker's 0.1
    assert _covered(rows, _d_size(0.0, 0.0, pitch=(24.0, 19.0))) == [(0.0, 848.5, 0.0)]   # turned 90 degrees
    holes = _d_size(0.0, 0.0)
    holes[2] = sf.Hole(3, (-9.5, 848.5, 12.0), (0.0, -1.0, 0.0), 3.2, 3.0, [])    # both screws on one side
    assert _covered(rows, holes) == []
    extra = _d_size(0.0, 0.0) + [sf.Hole(4, (-9.5, 848.5, 12.0), (0.0, -1.0, 0.0), 3.2, 3.0, [])]
    assert _covered(rows, extra) == []                                    # three screw holes: not this pattern


def _arc(center, axis, xdir, r):
    fr = sf.Frame.from_axes(center, axis, xdir)
    p = fr.point((r, 0.0, 0.0))
    return (fr, r, p, p, True)


def _plate(holes, width=120.0, height=80.0, t=1.5):
    """A flat plate in XY (Z 0 to t) with through holes (x, y, d)."""
    s = sf.Solid(1, "rear box")
    corners = [(0, 0), (width, 0), (width, height), (0, height)]
    lt = [((*corners[i], t), (*corners[(i + 1) % 4], t)) for i in range(4)]
    lb = [((*corners[i], 0.0), (*corners[(i + 1) % 4], 0.0)) for i in range(4)]
    rt = [_arc((x, y, t), (0, 0, 1), (1, 0, 0), d / 2) for x, y, d in holes]
    rb = [_arc((x, y, 0.0), (0, 0, 1), (1, 0, 0), d / 2) for x, y, d in holes]
    s.faces.append(sf.Face(1, "plane", (0, 0, t), (0, 0, 1), None, True, [p for ln in lt for p in ln], rt, lt))
    s.faces.append(sf.Face(2, "plane", (0, 0, 0), (0, 0, -1), None, True, [p for ln in lb for p in ln], rb, lb))
    for k, (x, y, d) in enumerate(holes):
        s.faces.append(sf.Face(3 + k, "cylinder", (x, y, 0), (0, 0, 1), d / 2, False, [rt[k][2], rb[k][2]],
                               [rt[k], rb[k]], []))
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        n = sf.norm(((b[1] - a[1]), -(b[0] - a[0]), 0.0))
        s.faces.append(sf.Face(20 + i, "plane", (*a, 0.0), n, None, True, [(*a, 0.0), (*b, 0.0), (*a, t), (*b, t)],
                               [], [((*a, 0.0), (*b, 0.0)), ((*a, t), (*b, t))]))
    s.box = (0, 0, 0, width, height, t)
    s.thickness = sf._sheet_thickness(s)
    s.holes = sf._holes(s)
    return s


def _run(monkeypatch, tmp_path, plate, rows, pn="711003"):
    class FakeStep:
        def instances(self):
            return [{"solid": 1, "part_number": pn, "name": "ELECTRICAL - INLET REAR BOX", "path": [pn],
                     "frame": sf.Frame()}]

        def solid(self, sid):
            return plate
    monkeypatch.setitem(cg.load_step.__defaults__[0], str(tmp_path / "x.step"), FakeStep())
    fs = cg.check_part_features(str(tmp_path), str(tmp_path / "x.step"), {}, [], hole_rules=[], edge_exceptions={},
                                cutout_exceptions=rows)
    return sorted((f.rule, f.evidence.get("web_mm", f.evidence.get("edge_mm"))) for f in fs)


def test_the_check_excuses_only_the_cut_outs_own_webs(monkeypatch, tmp_path):
    d_size = lambda x, y: [(x, y, 24.0), (x + 9.5, y + 12.0, 3.2), (x - 9.5, y - 12.0, 3.2)]
    plate = _plate(d_size(60.0, 40.0))
    assert len(plate.holes) == 3
    # no row: each screw hole's web to the Ø24 is 1.7 mm against 3 (2 x 1.5 mm, and 3 for laser cutting)
    assert _run(monkeypatch, tmp_path, plate, {}) == [("opening-web", 1.71), ("opening-web", 1.71)]
    assert _run(monkeypatch, tmp_path, plate, {"711003": ROWS["711003"]}) == []
    assert _run(monkeypatch, tmp_path, plate, {"711004": ROWS["711003"]}) == [("opening-web", 1.71)] * 2   # its plate: own row
    placed = [dict(ROWS["711003"][0], place="X 20 Y 40")]
    assert _run(monkeypatch, tmp_path, plate, {"711003": placed}) == [("opening-web", 1.71)] * 2
    # the cut-out's distance to the part's edge keeps its rule: a 2 mm rim from the Ø24 to the left edge
    plate = _plate(d_size(14.0, 40.0) + [(100.0, 40.0, 3.2)])
    got = _run(monkeypatch, tmp_path, plate, {"711003": ROWS["711003"]})
    assert ("opening-web", 2.0) in got and not any(v == 1.71 for _r, v in got)
    assert ("edge-distance", 4.5) in got                                  # the screw at X 4.5 keeps 2 diameters
