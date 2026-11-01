"""D-174 (the Lead, 2026-11-01, after Reviewer 16's find on INTERIOR's light shelf): a made part that meets other
parts' faces with no gap at both ends of a run of 100 mm or more is a major finding when those parts are fitted
separately, minor inside one made assembly. A gap of at least 1 mm at each end (a hole at least 1 mm over the part
it takes) clears it, and so does a row marking the fit as press, adjustable (slots or shims) or set at assembly."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_geometry as cg  # noqa: E402
import stepfile as sf  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def _box(label, box, file):
    """A body whose solid is its box's six flat faces, outward normals."""
    x0, y0, z0, x1, y1, z1 = box
    faces = []
    for k, (lo, hi) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
        for val, sgn in ((lo, -1.0), (hi, 1.0)):
            n = [0.0, 0.0, 0.0]
            n[k] = sgn
            o = [x0, y0, z0]
            o[k] = val
            i, j = [a for a in range(3) if a != k]
            pts = []
            for a in (box[i], box[i + 3]):
                for b in (box[j], box[j + 3]):
                    q = [0.0, 0.0, 0.0]
                    q[k], q[i], q[j] = val, a, b
                    pts.append(tuple(q))
            faces.append(sf.Face(len(faces) + 1, "plane", tuple(o), tuple(n), None, True, pts, [], []))
    solid = sf.Solid(1, label.split(" / ")[-2])
    solid.faces = faces
    return cg.Body(label, solid, sf.Frame(), box, file, "", None)


INT = "v2/03-Manufacturing/interior/810000_P01_INTERIOR_STEP.step"
AIR = "v2/03-Manufacturing/air/610000_P01_AIR_STEP.step"


def _shelf(x0, x1, file=INT, parent="810201 INTERIOR - LIGHT SHELF ASSY:1"):
    return _box("810000_P01_INTERIOR_CAD:1 / %s / 811202 INTERIOR - LIGHT SHELF - SIDE LH:1 / Body1" % parent,
                (x0, 0, 0, x1, 20, 40), file)


def _fixed(name, x0, x1, file=AIR, parent="610201 AIR - SOFFIT:1"):
    return _box("610000_P01_AIR_CAD:1 / %s / %s:1 / Body1" % (parent, name), (x0, -10, -10, x1, 30, 50), file)


def run(bodies, rows=None):
    return cg.check_tight_fits(ROOT, "assembly", bodies, rows or {})


def test_a_run_cut_to_the_exact_gap_between_separately_fitted_parts_is_major():
    a, b = _fixed("611202 AIR - SOFFIT FACE - FRONT", -20, 0), _fixed("611209 AIR - SOFFIT TOP RAIL", 991, 1011)
    (f,) = run([_shelf(0, 991), a, b])
    assert f.rule == "tight-fit" and f.severity == "major" and f.owner == "CEILING"
    assert f.subject == "assembly 811202 INTERIOR - LIGHT SHELF - SIDE LH along X"
    assert "runs 991.0 mm along X" in f.message and "0.00 and 0.00 mm clear" in f.message
    assert "(AIR's)" in f.message and "agree with AIR which side changes" in f.fix
    assert f.evidence["gaps_mm"] == [0.0, 0.0] and f.evidence["inside"] is False


def test_a_gap_of_1_mm_at_an_end_clears_it_and_less_does_not():
    a, b = _fixed("611202 AIR - SOFFIT FACE - FRONT", -20, 0), _fixed("611209 AIR - SOFFIT TOP RAIL", 992.2, 1012)
    assert run([_shelf(0, 991), a, b]) == []                                # 1.2 mm at one end
    b = _fixed("611209 AIR - SOFFIT TOP RAIL", 991.5, 1012)
    (f,) = run([_shelf(0, 991), a, b])                                      # 0.5 mm: still tight
    assert f.evidence["gaps_mm"] == [0.0, 0.5]


def test_a_hole_needs_1_mm_over_the_part_in_all():
    skin = "411302 CEILING - SKIN - C2"
    cfile = "v2/03-Manufacturing/ceiling/410000_P01_CEILING_STEP.step"
    sides = lambda g: [_fixed(skin, -20, -g, file=cfile, parent="410102 CEILING - PANEL ASSY - C2:1"),
                       _fixed(skin, 285 + g, 305, file=cfile, parent="410102 CEILING - PANEL ASSY - C2:1")]
    sleeve = _box("610000_P01_AIR_CAD:1 / 610601 AIR - ROOF:1 / 611601 AIR - ROOF SLEEVE:1 / Body1",
                  (0, 0, 0, 285, 20, 40), AIR)
    (f,) = run([sleeve] + sides(0.4))                                       # 0.8 mm over the sleeve in all
    assert "in a hole of 411302 CEILING - SKIN - C2 (CEILING's), 0.80 mm clear in all" in f.message
    assert run([sleeve] + sides(0.6)) == []                                 # 1.2 mm over it


def test_inside_one_made_assembly_it_is_minor():
    p = "810201 INTERIOR - LIGHT SHELF ASSY:1"
    a = _box("810000_P01_INTERIOR_CAD:1 / %s / 811201 INTERIOR - LIGHT SHELF - BACK:1 / Body1" % p, (-20, 0, 0, 0, 20, 40), INT)
    b = _box("810000_P01_INTERIOR_CAD:1 / %s / 811203 INTERIOR - LIGHT SHELF - END:1 / Body1" % p, (991, 0, 0, 1011, 20, 40), INT)
    (f,) = run([_shelf(0, 991), a, b])
    assert f.severity == "minor" and "one made assembly" in f.message and "agree with" not in f.fix


def test_a_marked_fit_seals_fasteners_and_short_parts_are_left_alone():
    a, b = _fixed("611202 AIR - SOFFIT FACE - FRONT", -20, 0), _fixed("611209 AIR - SOFFIT TOP RAIL", 991, 1011)
    for mark in ("press fit", "adjustable: slotted holes", "shimmed to fit", "set at assembly (welded into the frame)"):
        assert run([_shelf(0, 991), a, b], {"811202": "INTERIOR - LIGHT SHELF - SIDE LH; fit: %s" % mark}) == [], mark
    seal = _fixed("848001 HARDWARE - SEAM GASKET", 991, 1011)                # a seal at one end: nothing held there
    assert run([_shelf(0, 991), a, seal]) == []
    assert run([_shelf(0, 90), a, _fixed("611209 AIR - SOFFIT TOP RAIL", 90, 110)]) == []   # under 100 mm: no run
