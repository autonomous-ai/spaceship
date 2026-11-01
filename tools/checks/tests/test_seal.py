"""The floor seal line (C01 seal-gap; the Lead's ask of 2026-11-01): the pod's seal line traced as closed rings in
horizontal cuts, every gap wider than 1 mm reported with its width, place and open area.

The two open paths found by eye on 2026-11-01 are the proof: D-150's door end, on the real floor-band geometry from
before and after the fixes (fixtures/seal-floor-before.json.gz and -after.json.gz, saved from the STEPs, their
sources inside), and the door's hinge side, on the real door and DL with FL2, its plate, its lip and the hinge-end
brush placed as BASE and FRONT posted them (BASE's batch 2 STEP isn't exported yet)."""

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_seal as cs  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
TRAVEL = [(re.compile(r"\bDROP SEAL\b", re.I), 20.0, "hardware selection C4")]
SMALL = (-700.0, -600.0, 700.0, 600.0)


def ring(front=(), z1=100.0):
    """A closed ring of walls round (0, 0) from the floor to z1, its front wall (Y -420 to -400) given as pieces."""
    walls = [cs.box("110000_P01_BASE_CAD:1 / 111103 BASE - BACK:1 / BACK", -500, 400, 0, 500, 420, z1),
             cs.box("110000_P01_BASE_CAD:1 / 111101 BASE - LEFT:1 / LEFT", -520, -420, 0, -500, 420, z1),
             cs.box("110000_P01_BASE_CAD:1 / 111102 BASE - RIGHT:1 / RIGHT", 500, -420, 0, 520, 420, z1)]
    return walls + list(front)


def front(gaps, z1=100.0):
    """The front wall from X -500 to 500 with the given gaps [(x0, x1)]."""
    out, x = [], -500.0
    for i, (g0, g1) in enumerate(sorted(gaps) + [(500.0, 500.0)]):
        if g0 > x:
            out.append(cs.box("360001_P01_FRONT_CAD:1 / 36100%d FRONT - PIECE %d:1 / P" % (i, i), x, -420, 0, g0, -400, z1))
        x = g1
    return out


def run(shapes, travel=TRAVEL, xy=SMALL, z_top=None):
    z_top = z_top if z_top is not None else max(s.box[5] for s in shapes)
    ops, states, _use = cs.seal_line(shapes, z_top, travel, {}, xy=xy)
    return ops, states


def in_window(o, x0, x1, y0, y1):
    return any(x0 <= m[0] <= x1 and y0 <= m[1] <= y1 for m in o["mids"])


# ----------------------------------------------------------------- the method, on rings of boxes

def test_a_closed_ring_is_sealed_and_a_slot_is_an_opening_with_its_area():
    ops, states = run(ring(front([])))
    assert ops == [] and all(s["state"] == "sealed" for s in states)
    ops, _s = run(ring(front([(-2.25, 2.25)])))
    assert len(ops) == 1
    o = ops[0]
    assert abs(o["w_min"] - 4.5) < 1e-6 and abs(o["w_max"] - 4.5) < 1e-6
    assert o["z0"] == 0.0 and o["z1"] == 100.0 and abs(o["area"] - 450.0) < 1e-6
    assert in_window(o, -3, 3, -421, -399)


def test_one_mm_is_sealed_and_anything_wider_is_open():
    assert run(ring(front([(-0.5, 0.5)])))[0] == []
    ops, _s = run(ring(front([(-0.6, 0.6)])))
    assert len(ops) == 1 and abs(ops[0]["w_max"] - 1.2) < 1e-6


def test_every_gap_on_the_ring_is_reported_and_their_areas_add():
    ops, _s = run(ring(front([(-302.25, -297.75), (294.5, 305.5)])))
    got = sorted((round(o["w_max"], 3), round(o["area"], 1)) for o in ops)
    assert got == [(4.5, 450.0), (11.0, 1100.0)]
    # an opening only part of the way up: the wall below it closes the rest
    shapes = ring(front([(-2.25, 2.25)])) + [cs.box("368008 FRONT - BRUSH:1", -2.25, -420, 0, 2.25, -400, 40)]
    ops, _s = run(shapes)
    assert len(ops) == 1 and ops[0]["z0"] == 40.0 and abs(ops[0]["area"] - 4.5 * 60) < 1e-6


def test_a_slanted_gap_is_measured_square_across_it():
    # the front closed by two pieces whose facing ends are cut at 30 degrees, 3 mm apart square to the cut
    t = math.radians(30.0)
    d = 3.0 / math.cos(t)                     # the same gap along X
    a = [(-500, -420), (-10, -420), (-10 + 20 * math.tan(t), -400), (-500, -400)]
    b = [(-10 + d, -420), (500, -420), (500, -400), (-10 + d + 20 * math.tan(t), -400)]
    shapes = ring([cs.prism("361001 FRONT - A:1", a, 0, 100), cs.prism("361002 FRONT - B:1", b, 0, 100)])
    ops, _s = run(shapes)
    assert len(ops) == 1 and abs(ops[0]["w_max"] - 3.0) < 0.01, ops[0]["w_max"]


def test_the_drop_seal_goes_down_to_the_floor_within_its_travel():
    # the door's kick strip from Z 10 up, its drop seal under it modelled up, flush with the strip's bottom
    door = [cs.box("361002 FRONT - DOOR KICK STRIP:1", -300, -420, 10, 300, -400, 100),
            cs.box("368001 FRONT - DROP SEAL - ATHMER SCHALL-EX GSA 1-1112:1", -300, -415, 10, 300, -405, 50)]
    shapes = ring(front([(-300, 300)]) + door)
    ops, _s = run(shapes)
    assert ops == []
    ops, _s = run(shapes, travel=[])
    assert len(ops) == 1 and ops[0]["z0"] == 0.0 and ops[0]["z1"] == 10.0 and ops[0]["w_max"] > 500
    ops, _s = run(shapes, travel=[(re.compile(r"DROP SEAL"), 4.0, "")])
    assert len(ops) == 1 and ops[0]["z1"] == 6.0


def _wall_with_hole(label, x0, x1, y0, y1, z0, z1, cx, cz, r):
    """A wall along X (Y y0..y1) with a round hole through it along Y, centre (cx, cz), radius r."""
    def arc(y, start, span):
        return ("arc", (cx, y, cz), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), r, start, span)
    faces = []
    for y, n in ((y0, (0, -1, 0)), (y1, (0, 1, 0))):
        w = cs._plane_face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], n)
        w.edges += [arc(y, 0.0, math.pi), arc(y, math.pi, math.pi)]
        faces.append(w)
    for poly, n in (([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1)),
                    ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
                    ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], (-1, 0, 0)),
                    ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0))):
        faces.append(cs._plane_face(poly, n))
    for start in (0.0, math.pi):              # the hole's wall in two halves, as Fusion writes it
        w = cs._WFace()
        w.kind, w.o, w.ax, w.r, w.half = "cyl", (cx, y0, cz), (0.0, 1.0, 0.0), r, None
        p0 = (cx + r * math.cos(start), cz + r * math.sin(start))
        p1 = (cx + r * math.cos(start + math.pi), cz + r * math.sin(start + math.pi))
        w.edges = [arc(y0, start, math.pi), arc(y1, start, math.pi),
                   ("seg", (p0[0], y0, p0[1]), (p0[0], y1, p0[1])), ("seg", (p1[0], y0, p1[1]), (p1[0], y1, p1[1]))]
        zs = [cz + r * math.sin(start + k * math.pi / 8) for k in range(9)]
        w.zlo, w.zhi = min(zs), max(zs)
        faces.append(w)
    return cs.Shape(label, faces)


def test_a_hole_through_a_wall_counts_its_round_area():
    wall = _wall_with_hole("111106 BASE - FRONT:1", -500, 500, -420, -400, 0, 100, 0.0, 50.0, 5.0)
    ops, _s = run(ring([wall]))
    assert len(ops) == 1
    o = ops[0]
    # cut 1 mm apart across the round face, each in the middle of its step: the widest is 0.5 mm off the centre
    assert abs(o["w_max"] - 2.0 * math.sqrt(25.0 - 0.25)) < 1e-6
    assert abs(o["z0"] - 45.0) < 1e-6 and abs(o["z1"] - 55.0) < 1e-6
    assert abs(o["area"] - math.pi * 25.0) < 0.02 * math.pi * 25.0, o["area"]


# ----------------------------------------------------------------- D-150's door end, on the real floor band

def _door_end(ops):
    return [o for o in ops if in_window(o, 205, 232, -815, -680) and o["z0"] < 105.0 - 1e-6]


def test_the_door_end_open_before_d150_is_found_and_closed_after():
    before, _src = cs.load_shapes(os.path.join(FIX, "seal-floor-before.json.gz"))
    ops, states = run(before, xy=(-1260.0, -860.0, 1260.0, 860.0), z_top=110.0)
    assert all(s["open_rows"] == 0 and s["unpaired_faces"] == 0 for s in states)
    door = _door_end(ops)
    # under the sill's open end, from the floor to the band's bottom line: FR1's lip ends 95.5 mm short of the drop
    # seal (the path round both seals that Reviewer 8 found on #303)
    low = [o for o in door if o["z0"] == 0.0 and abs(o["z1"] - 10.0) < 1e-6]
    assert len(low) == 1 and abs(low[0]["w_max"] - 95.5) < 0.1, [(o["z0"], o["z1"], o["w_max"]) for o in door]
    # and the slot between the kick strip's end (X 214) and the sill's end (X 218.46) on up
    slot = [o for o in door if o["z0"] >= 10.0 - 1e-6 and abs(o["w_min"] - 4.46) < 0.01]
    assert slot and max(o["z1"] for o in slot) >= 93.0
    names = {l for o in slot for p in o["pairs"] for l in p}
    assert any("361002" in l for l in names) and any("111301" in l for l in names)

    after, _src = cs.load_shapes(os.path.join(FIX, "seal-floor-after.json.gz"))
    ops, states = run(after, xy=(-1260.0, -860.0, 1260.0, 860.0), z_top=110.0)
    assert all(s["open_rows"] == 0 and s["unpaired_faces"] == 0 for s in states)
    assert _door_end(ops) == [], [(o["z0"], o["z1"], o["w_max"]) for o in _door_end(ops)]
    # what is left there is FRONT's own, above the kick strip: the door's magnetic seal half starts at Z 105 and the
    # fixed pane's at Z 110, 2 mm apart (a real opening, 10 mm²)
    top = [o for o in ops if in_window(o, 205, 232, -715, -680)]
    assert len(top) == 1 and top[0]["z0"] == 105.0 and abs(top[0]["w_max"] - 2.02) < 0.01


# ----------------------------------------------------------------- the hinge side, as BASE and FRONT posted it

def _fl2(plate=False, brush=False):
    """FL2 under DL with its lip (BASE, 2026-11-01: its door end reaches Y -802.6 at X -972), and the ruled fixes:
    BASE's 2 mm plate flush with DL's door face (X -972) to the kick strip's back line (Y -689), from the band's
    bottom line up, with an L lip under it; FRONT's hinge-end brush on the 11 mm slot, from the floor to Z 105."""
    b = "110000_P01_BASE_CAD:1 / "
    out = [cs.box(b + "111105 BASE - BAND TUBE - FL2:1 / FRONT", -1250, -850, 10, -972, -802.6, 110),
           cs.box(b + "111105 BASE - BAND TUBE - FL2:1 / SIDE", -1250, -850, 10, -1210, -660, 110),
           cs.box(b + "118001 BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD (5):1 / FRONT", -1210, -802.6, 0, -972, -792.6, 25),
           cs.box(b + "118001 BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD (5):1 / SIDE", -1210, -802.6, 0, -1200, -652, 25)]
    if plate:
        out += [cs.box(b + "111107 BASE - FL2 DOOR-END PLATE:1 / PLATE", -974, -802.6, 10, -972, -689, 110),
                cs.prism(b + "118001 BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD (6):1 / L",
                         [(-984, -802.6), (-972, -802.6), (-972, -689), (-984, -689)], 0, 10)]
    if brush:
        out.append(cs.box("360001_P01_FRONT-DOOR-UNIT_CAD:1 / 368009 FRONT - DOOR KICK STRIP HINGE END SEAL - BRUSH"
                          " - HOLD:1 / BRUSH", -972, -709, 0, -961, -689, 105))
    return out


def _hinge(ops):
    return [o for o in ops if in_window(o, -1000, -940, -860, -660)]


def test_the_hinge_side_before_and_after_its_ruling():
    after, _src = cs.load_shapes(os.path.join(FIX, "seal-floor-after.json.gz"))
    xy = (-1260.0, -860.0, 1260.0, 860.0)
    # before: FL2 stops at X -972, Y -802.6 and nothing reaches the kick strip's hinge end (X -961, Y -709): the
    # window under DL in front of the door plane and the 11 mm slot are one opening, about 1 dm² (BASE's count)
    ops, _s = run(after + _fl2(), xy=xy, z_top=110.0)
    hinge = _hinge(ops)
    assert len(hinge) == 1, [(o["z0"], o["z1"], o["w_max"]) for o in hinge]
    o = hinge[0]
    # 88.7 from the drop seal's corner to the lip's (X -972, Y -792.6) under the kick strip, 84.3 from the kick
    # strip's corner (X -961, Y -709) where the lip reaches up to Z 25, 94.2 to FL2's own corner (Y -802.6) above
    # it, and 99.8 to the door glass's corner over the kick strip (Z 105 to 110)
    assert o["z0"] == 0.0 and abs(o["z1"] - 110.0) < 1e-6
    assert abs(o["w_min"] - math.hypot(11.0, 83.6)) < 0.01 and abs(o["w_max"] - math.hypot(11.0, 99.2)) < 0.05
    assert 9000.0 < o["area"] < 10600.0, o["area"]
    # BASE's plate and lip in: the 11 mm slot to the kick strip's end is left, from the floor to Z 105
    ops, _s = run(after + _fl2(plate=True), xy=xy, z_top=110.0)
    hinge = _hinge(ops)
    assert len(hinge) == 1 and abs(hinge[0]["w_min"] - 11.0) < 1e-6 and abs(hinge[0]["w_max"] - 11.0) < 1e-6
    assert hinge[0]["z0"] == 0.0 and abs(hinge[0]["z1"] - 105.0) < 1e-6 and abs(hinge[0]["area"] - 1155.0) < 1e-6
    # FRONT's brush in too: closed
    ops, _s = run(after + _fl2(plate=True, brush=True), xy=xy, z_top=110.0)
    assert _hinge(ops) == []


# ----------------------------------------------------------------- findings

def test_findings_name_the_parts_their_owners_and_the_total(tmp_path):
    # no skeleton table in tmp_path: the cuts go up to Z 110, so the ring does too
    shapes = ring(front([(-2.25, 2.25)], z1=110.0), z1=110.0)
    for s in shapes:
        s.file = "v2/03-Manufacturing/front/x.step" if "FRONT" in s.label else "v2/03-Manufacturing/base/x.step"
    fs, rep = cs.check_seal_line(str(tmp_path), "assembly", shapes)
    assert rep["total_mm2"] == 495.0 and rep["cuts"] >= 1 and len(rep["openings"]) == 1
    (f,) = fs
    assert f.check == "C01" and f.rule == "seal-gap" and f.severity == "severe"
    assert f.subject == "floor seal line 361000 | 361001" and f.owner == "FRONT"
    assert f.evidence["model"] == "seal-line" and f.evidence["area_mm2"] == 495.0
    assert "4.5 mm wide" in f.message and "open area 495 mm²" in f.message and "1, 495 mm² in all" in f.message
    # two openings between the same two parts: told apart by place, then by height
    pieces = [cs.box("360001_P01_FRONT_CAD:1 / 361009 FRONT - PIECE:1 / A", -500, -420, 0, -2.25, -400, 110),
              cs.box("360001_P01_FRONT_CAD:1 / 361009 FRONT - PIECE:1 / B", 2.25, -420, 0, 500, -400, 110),
              cs.box("360001_P01_FRONT_CAD:1 / 361008 FRONT - FILL:1 / F", -2.25, -420, 30, 2.25, -400, 60)]
    fs, rep = cs.check_seal_line(str(tmp_path), "assembly", ring(pieces, z1=110.0))
    assert sorted(f.subject for f in fs) == ["floor seal line 361009 at X 0 Y -420 Z 0",
                                             "floor seal line 361009 at X 0 Y -420 Z 60"], [f.subject for f in fs]
    # parts that stop short of the band's top leave the cuts above with no ring at all: said so, not passed
    fs, rep = cs.check_seal_line(str(tmp_path), "assembly", ring(front([])))
    assert [f.rule for f in fs] and all(f.rule == "seal-no-ring" for f in fs) and rep["no_ring_cuts"]
