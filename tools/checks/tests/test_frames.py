"""D-131's frame check (tools/checks/c_frames.py): steel callouts and gauges on every frame member, from the lists
and the CAD, against the Joints Engineer's own table."""

import csv
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import c_frames  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# a stand-in for v2/01-CAD-Native/joints/frame_steel_check.py with the same names and rules (2026-11-01)
SPEC = '''
ACCEPTED = (("S280GD+Z, EN 10346", 280.0, 360.0), ("SGC400, JIS G3302", 295.0, 400.0))
PERIMETER_T, INNER_T, SIDE_T = 1.0, 0.8, 1.2
FRAMES = {
    "L1": ("211101 L1", 2, 1495.0, [(2, 1495.0, 20, 40, "rail"), (1, 1143.0, 20, 40, "front stile"),
                                    (1, 1143.0, 40, 40, "back stile"), (3, 1103.0, 20, 40, "stud"),
                                    (2, 1103.0, 20, 40, "stud, added for D-135")]),
    "B1": ("211201 B1", 4, 1199.0, [(2, 1199.0, 20, 40, "rail"), (2, 1118.6, 20, 40, "stile"),
                                    (3, 1078.6, 20, 40, "stud")]),
    "C1": ("411101 C1", 2, 1495.0, [(2, 1495.0, 20, 40, "side and seam members"), (1, 1199.0, 20, 40, "front member"),
                                    (1, 1199.0, 40, 40, "back member"),
                                    (1, 1159.0, 20, 40, "cross member 1 (soffit rivnuts)"),
                                    (2, 1159.0, 20, 40, "cross members 2 and 3")]),
}
INNER_ROLES = ("stud", "cross members 2 and 3")
SIDE_ROLES = ("rail", "bottom rail", "front stile")


def gauge(role, perimeter=PERIMETER_T, key=None):
    if role.startswith(INNER_ROLES):
        return INNER_T
    if key in ("L1", "L2") and role in SIDE_ROLES and perimeter == PERIMETER_T:
        return SIDE_T
    return perimeter
'''

REGISTER = ("### 3.16 J-OTHER\n| Parts | 999001 to 999002 |\n"
            "### 3.17 J-FRAME-01: the wall and ceiling frames, welded galvanized steel (D-131)\n"
            "| Ruling | D-131 |\n"
            "| Parts | WALL's 211101 to 211102 (L1, R1) and 211201 (B1); CEILING's 411101 and 411102 (C1, C2): steel |\n")

STEEL = "galvanized steel tube S280GD+Z Z100"
FIN = "pre-galvanized Z100; welds touched up with 2-component zinc-rich epoxy (J-FRAME-01)"


def _tree(tmp_path, rows=None):
    j = tmp_path / "v2/01-CAD-Native/joints"
    j.mkdir(parents=True)
    (j / "frame_steel_check.py").write_text(SPEC)
    r = tmp_path / "v2/05-Engineering/joints"
    r.mkdir(parents=True)
    (r / "joints-register.md").write_text(REGISTER)
    w = tmp_path / "v2/03-Manufacturing/wall"
    w.mkdir(parents=True)
    rows = rows if rows is not None else _l1_rows()
    cols = ["level", "part_number", "name", "material", "finish", "qty", "size_mm"]
    with open(w / "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for row in rows:
            wr.writerow({k: row.get(k, "") for k in cols})
    return str(tmp_path)


def _l1_rows(material=STEEL, finish=FIN, stud="0.8", stile_back="40 x 40 x 1.0"):
    return [
        {"level": "0", "part_number": "210101", "name": "WALL - PANEL ASSY - SIDE LOWER - LH", "qty": "1"},
        {"level": "1", "part_number": "211101", "name": "WALL - PANEL FRAME - SIDE LOWER - LH", "material": material,
         "finish": finish, "qty": "1"},
        {"level": "2", "name": "RAIL - BOTTOM (cut length)", "material": material + " 20 x 40 x 1.2", "qty": "1",
         "size_mm": "20 x 40 x 1.2"},
        {"level": "2", "name": "STILE - FRONT (cut length)", "material": material, "qty": "1", "size_mm": "20 x 40 x 1.2"},
        {"level": "2", "name": "STILE - BACK (cut length)", "material": material, "qty": "1", "size_mm": stile_back},
        {"level": "2", "name": "STILE - MID (cut length)", "material": material, "qty": "5",
         "size_mm": "20 x 40 x " + stud},
        {"level": "1", "part_number": "838003", "name": "HARDWARE - RIVET NUT - M6", "material": "steel", "qty": "9"},
    ]


def test_the_frames_and_gauges_come_from_the_register_and_the_joints_check(tmp_path):
    root = _tree(tmp_path)
    assert c_frames.frame_numbers(root) == ["211101", "211102", "211201", "411101", "411102"]
    spec = c_frames.load_spec(root)
    assert spec.gauge("rail", key="L1") == 1.2 and c_frames.expected_gauge(spec, "L1", "stud") == 0.8
    assert c_frames.expected_gauge(spec, "L1", "stud", site_joint=True) == 1.0      # a site joint: perimeter gauge
    assert c_frames.load_spec(str(tmp_path / "nowhere")) is None


def test_member_names_map_to_the_tables_roles():
    r = c_frames.member_role
    assert r("L1", "RAIL - TOP (cut length)") == "rail" and r("L1", "STILE - MID (cut length)") == "stud"
    assert r("L1", "WALL - FRAME STILE BACK 40 X 40 - SIDE LOWER - LH") == "back stile"
    assert r("L2", "RAIL - TOP (cut length)") == "top member" and r("L2", "RAIL - BOTTOM") == "bottom rail"
    assert r("B1", "STILE - CENTRE (cut length)") == "stile" and r("B1", "STILE - MID") == "stud"
    assert r("C1", "CROSS MEMBER 1 X1") == "cross member 1 (soffit rivnuts)"
    assert r("C1", "CEILING - FRAME CROSS MEMBER - PLAIN - COMMON") == "cross members 2 and 3"
    assert r("C1", "BACK MEMBER 40X40 BACK") == "back member" and r("C1", "SEAM MEMBER SEAM") == "side and seam members"
    assert c_frames.frame_key("WALL - PANEL FRAME - BACK LOWER - B1") == "B1"
    assert c_frames.frame_key("CEILING - PANEL FRAME - C2") == "C1"


def test_a_steel_frame_at_its_gauges_passes_and_aluminium_is_one_major_finding(tmp_path):
    root = _tree(tmp_path)
    spec = c_frames.load_spec(root)
    fs, steel = c_frames.check_frame_lists(root, spec, ["211101"])
    assert fs == [] and steel == {"211101": True}
    root = _tree(tmp_path / "al", _l1_rows(material="aluminium tube 6063-T6", finish="mill finish"))
    fs, steel = c_frames.check_frame_lists(root, spec, ["211101"])
    assert [(f.rule, f.severity) for f in fs] == [("frame-steel", "major")] and steel == {"211101": False}
    assert "4 member rows" in fs[0].message and "doesn't name the zinc" in fs[0].message and fs[0].owner == "WALL"
    assert fs[0].evidence["model"] == "frames"


def test_a_thin_member_is_severe_a_thick_one_minor_and_the_callout_needs_grade_zinc_and_touch_up(tmp_path):
    spec = c_frames.load_spec(_tree(tmp_path / "s"))
    fs, _s = c_frames.check_frame_lists(_tree(tmp_path / "a", _l1_rows(stud="0.6")), spec, ["211101"])
    assert [(f.rule, f.severity) for f in fs] == [("frame-gauge", "severe")] and "0.60 thick" in fs[0].message
    fs, _s = c_frames.check_frame_lists(_tree(tmp_path / "b", _l1_rows(stud="1.0")), spec, ["211101"])
    assert [(f.rule, f.severity) for f in fs] == [("frame-gauge", "minor")]
    fs, _s = c_frames.check_frame_lists(_tree(tmp_path / "c", _l1_rows(stile_back="20 x 40 x 1.0")), spec, ["211101"])
    assert "the table's back stile is 40 x 40" in fs[0].message
    lacks = c_frames.callout_lacks
    assert lacks(spec, "galvanized steel tube DX51D Z100") == [
        "an accepted grade (S280GD+Z or SGC400, or a stated yield of 280 MPa or more)"]
    assert lacks(spec, "galvanized steel DX51D Z100, yield 280 MPa or more by 3 tensile tests") == []
    assert lacks(spec, "galvanized steel S280GD+Z Z275") == ["Z100 zinc (it reads Z275)"]
    fs, _s = c_frames.check_frame_lists(_tree(tmp_path / "d", _l1_rows(finish="pre-galvanized Z100")), spec, ["211101"])
    assert [f.rule for f in fs] == ["frame-steel"] and "zinc-rich touch-up" in fs[0].message


class _Face:
    def __init__(self, normal, origin):
        self.kind, self.normal, self.origin = "plane", normal, origin


class _Hole:
    def __init__(self, d):
        self.diameter = d


def _tube(box, wall, holes=()):
    """A body whose box is `box` and whose walls are `wall` thick across its two short axes."""
    ext = [box[k + 3] - box[k] for k in range(3)]
    n = max(range(3), key=lambda k: ext[k])
    faces = []
    for k in range(3):
        if k == n:
            continue
        e = [0.0, 0.0, 0.0]
        e[k] = 1.0
        lo, hi = box[k], box[k + 3]
        for x, sgn in ((lo, -1), (hi, 1), (lo + wall, 1), (hi - wall, -1)):
            o = [0.0, 0.0, 0.0]
            o[k] = x
            faces.append(_Face(tuple(sgn * v for v in e), tuple(o)))
    solid = types.SimpleNamespace(faces=faces, holes=[_Hole(d) for d in holes])
    return types.SimpleNamespace(label="210101 / 211101 WALL - PANEL FRAME - SIDE LOWER - LH:1 / Body", box=box,
                                 solid=solid, file="v2/03-Manufacturing/wall/210101_P01_X_STEP.step")


def _l1_bodies(stud_wall=0.8, rail_wall=1.2):
    x0, x1 = -1244.0, -1204.0
    return [_tube((x0, -643, 112, x1, 847, 132), rail_wall), _tube((x0, -643, 1235, x1, 847, 1255), rail_wall),
            _tube((x0, -643, 132, x1, -623, 1235), 1.2), _tube((x0, 807, 132, x1, 847, 1235), 1.0),
            _tube((x0, -278, 132, x1, -258, 1235), stud_wall), _tube((x0, 87, 132, x1, 107, 1235), stud_wall)]


def test_the_cad_reads_each_members_role_from_where_it_sits_and_its_wall(tmp_path):
    spec = c_frames.load_spec(_tree(tmp_path))
    mem = c_frames.cad_members(_l1_bodies(), "211101")
    roles = [r for _b, r, _s in c_frames.cad_roles("L1", mem)]
    assert roles == ["rail", "rail", "front stile", "back stile", "stud", "stud"]
    names = {"211101": "WALL - PANEL FRAME - SIDE LOWER - LH"}
    assert c_frames.check_frame_cad("", spec, ["211101"], _l1_bodies(), names, {"211101": True}) == []
    fs = c_frames.check_frame_cad("", spec, ["211101"], _l1_bodies(rail_wall=1.0), names, {"211101": True})
    assert [(f.rule, f.severity) for f in fs] == [("frame-cad-gauge", "severe")] and "rail" in fs[0].message
    # aluminium-era studs at 1.0: thicker than the steel gauge, reported only once the list says steel
    assert c_frames.check_frame_cad("", spec, ["211101"], _l1_bodies(stud_wall=1.0), names, {"211101": False}) == []
    fs = c_frames.check_frame_cad("", spec, ["211101"], _l1_bodies(stud_wall=1.0), names, {"211101": True})
    assert [(f.rule, f.severity) for f in fs] == [("frame-cad-gauge", "minor")]
    # a stud with a site joint (a Ø9.53 rivnut hole) takes the perimeter gauge
    bodies = _l1_bodies()
    bodies[4] = _tube(bodies[4].box, 0.8, holes=(9.53,))
    fs = c_frames.check_frame_cad("", spec, ["211101"], bodies, names, {"211101": True})
    assert fs and "with a site joint" in fs[0].message and fs[0].severity == "severe"


def test_the_real_joints_check_keeps_the_names_this_reads():
    if not os.path.exists(os.path.join(REPO, c_frames.SPEC_PY)):
        return
    spec = c_frames.load_spec(REPO)
    assert spec is not None and set(spec.FRAMES) >= {"L1", "L2", "B1", "C1"}
    for key, (_t, _n, _l, members) in spec.FRAMES.items():
        for m in members:
            assert c_frames.table_member(spec, key, m[4].split(",")[0]) is not None
    assert c_frames.frame_numbers(REPO)
