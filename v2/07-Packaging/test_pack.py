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
    p.extra_kg = 8.1          # DR with its inner face panel and felt fitted would pass 20 kg (D-130: they ship loose, 2-23)
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
    assert len(tags) == 43    # with DR's loose inner face panel 2-23 (D-130)
    power = next(s for s in pack.STEPS if s["title"].startswith("Power on"))
    assert all(o["secs"] < 600 for o in power["ops"])


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


def test_sizes_follow_the_skeleton():
    # a panel with no CAD yet is the skeleton's named values; one with CAD is at least that, plus what its CAD adds
    b3 = pack.PIECE["1-07"]
    assert b3.dims == pack.S(pack.sk("half_pw"), pack.sk("back_ph"), pack.sk("outer_t"))
    b1, l1 = pack.PIECE["1-03"], pack.PIECE["1-05"]
    sk_b1 = pack.S(pack.sk("half_pw"), pack.sk("back_ph"), pack.sk("outer_t"))
    sk_l1 = pack.S(pack.sk("side_l"), pack.sk("side_h"), pack.sk("outer_t"))
    assert all(d >= s for d, s in zip(b1.dims, sk_b1)) and all(d >= s for d, s in zip(l1.dims, sk_l1)), (b1.dims, l1.dims)
    assert b1.dims[0] == pack.sk("half_pw") and l1.dims[0] == pack.sk("side_l")
    f1 = pack.PIECE["1-01"]
    assert f1.dims[2] == pack.sk("floor_t") + pack.sk("mat_t")


def test_cad_size_outgrowing_its_plan_is_caught():
    # K14: a planned size smaller than the merged CAD fails (the decor blocks were planned as boxes 30 mm too narrow)
    m = pack.Model()
    assert "K14" not in failing(m)
    kind, dims, files = m.cad["2-09"]
    assert kind == "box" and dims[1] > 300, dims          # DL with its hinge-side stops
    dl = pack.PIECE["2-09"]
    saved = dl.dims
    dl.dims = pack.S(2290, 278, 205)                       # the old box
    try:
        assert "K14" in failing(pack.Model())
    finally:
        dl.dims = saved


def test_bundle_parts_each_fit():
    # a bundle or carton is checked part by part: a ledge carton too short for the ledge top fails
    m = pack.Model()
    kind, parts, _ = m.cad["2-16"]
    assert kind == "parts" and {pn for pn, _ in parts} >= {"811101", "818101", "818102"}, parts
    led = pack.PIECE["2-16"]
    saved = led.dims
    led.dims = pack.S(900, 250, 120)
    try:
        assert "K14" in failing(pack.Model())
    finally:
        led.dims = saved


def test_d129_keys_on_the_side_bands():
    # D-129: the side bands carry the back-corner keys; the back band ships with keyholes only, 2420 long
    keys = {p.tag: sum(u for h, u in p.mass if h == "KEY") for p in pack.PIECES}
    assert keys["2-04"] == 0 and keys["2-05"] == 2 and keys["2-06"] == 2 and keys["2-15"] == 2, keys
    m = pack.Model()
    assert m.cad["2-04"][1][0] <= 2420 + 1e-6, m.cad["2-04"]
    tiers, _ = m.tiers2()
    lane = next(ln for t in tiers for ln in t["lanes"] if any(i["tag"] == "2-04" for i in ln["items"]))
    assert lane["length"] <= pack.MINE["pal_long_l_exact"].value, lane["length"]


def test_roof_sleeve_goes_on_after_the_soffit():
    # #263: the roof sleeve and grille ride loose with C2 and go on in their own step, after the soffit hangs
    m = pack.Model()
    kind, c2, _ = m.cad["1-12"]
    assert kind == "box" and c2[2] > 60, c2                 # C2 with the sleeve seated in its slot
    assert m.cad["2-10"][1][2] < 240, m.cad["2-10"]          # the soffit without it
    soffit = next(s["n"] for s in pack.STEPS if "2-10" in s["tags"])
    sleeve = next(s for s in pack.STEPS if s["title"].startswith("Roof sleeve"))
    assert sleeve["n"] == soffit + 1 and sleeve["n"] <= pack.CLOCK_LAST_STEP
    assert [s["n"] for s in pack.STEPS] == list(range(1, len(pack.STEPS) + 1))


def test_design_review_glass_handling():
    # design review 2026-11-01: both people carry DR while stays hold the glass; the door stands on packers; panes tilt up
    def ops(title):
        return [o["text"] for o in next(s for s in pack.STEPS if s["title"].startswith(title))["ops"]]
    ten, eleven = ops("Fixed glass"), ops("Door")
    assert any("glass stay on" in o for o in ten) and any("glass stay off" in o for o in ten), ten
    assert any("tilt" in o for o in ten) and any("tilt" in o for o in eleven), (ten, eleven)
    assert any("packers" in o for o in eleven), eleven
    dr = next(o for o in next(s for s in pack.STEPS if s["title"].startswith("Fixed glass"))["ops"] if "2-03" in o["text"])
    assert dr["who"] == 2, dr                      # DR (2.3 m) is carried by both people
    kit = pack.PIECE["2-22"]
    assert "glass stays" in kit.extra_note and "setting packers" in kit.extra_note, kit.extra_note


def test_install_sheet_numbers():
    # the install sheet (IF-17): room height from the pod's height and the roof work, the floor from the glides' range
    outs = pack.outputs(pack.Model())
    sheet = outs[pack.OUT_INSTALL]
    room = pack.sk("pod_h") + pack.MINE["roof_work"].value
    assert f"at least {room:g} mm" in sheet, room
    assert f"within {pack.MINE['glide_max'].value - pack.MINE['glide_min'].value:g} mm" in sheet
    assert "120 V" in sheet and "{{" not in sheet


def test_elevator_rule():
    # K15: every piece leans into the install sheet's car through its door; DR's wide face needs the wide door
    m = pack.Model()
    assert "K15" not in failing(m) and m.no_lift == [] and "2-03" in m.no_typical, (m.no_lift, m.no_typical)
    car = (pack.MINE["lift_car_w"].value, pack.MINE["lift_car_d"].value, pack.MINE["lift_car_h"].value)
    assert not pack.goes_in(pack.moving_size(pack.PIECE["2-03"]), car, (914, 2134))     # a 36 in door can't take DR
    assert pack.tilt_in(2430, 50, 1295, 2286, 2134)                                         # the back band leans in
    assert not pack.tilt_in(2430, 50, 1295, 2000, 2134)                                     # but not under a 2 m ceiling


def test_export_wood_is_ispm15():
    # every solid-wood packaging part is heat-treated and ISPM 15 stamped, or US ports refuse it
    wood = [it for it in pack.PACKAGING if it.get("wood")]
    assert {it["pn"] for it in wood} == {"918001", "918002", "911001", "911003"}, wood
    assert all("ISPM 15" in it["name"] for it in wood), [it["name"] for it in wood]


def test_roof_grille_bolts_counted_once():
    # J-AIR-03 (#275): step 18 drives the grille's 4 register bolts; no outside-fixing row and no second timing for them
    st = next(s for s in pack.STEPS if s["title"].startswith("Roof sleeve"))
    assert st["joints"] == {"J-AIR-03": 4}, st["joints"]
    assert not [f for f in pack.OTHER_FIXINGS if f["step"] == st["n"]]
    assert not [o for o in st["ops"] if "screw" in o["text"] or "drive" in o["text"]], st["ops"]
    ops, bolts, other = pack.step_ops(st, pack.OTHER_FIXINGS)
    assert bolts == 4 and other == 0 and sum(o["n"] for o in ops if o["src"] == "t_bolt_captive_s") == 4


def test_dr_inner_face_before_the_right_linings():
    # the PM's ruling: DR's inner face can't come off past R1's and R2's cassettes, so the riser step (inner face off
    # and on) comes before the wall linings, and the take-down unclips R1's and R2's cassettes before the inner face
    riser = next(s["n"] for s in pack.STEPS if "2-17" in s["tags"])
    linings = next(s["n"] for s in pack.STEPS if "1-13" in s["tags"])
    column = next(s["n"] for s in pack.STEPS if "2-11" in s["tags"])
    assert riser < linings < column, (riser, linings, column)
    guide = pack.TPL_GUIDE.read_text(encoding="utf-8")
    assert guide.index("R1's and R2's cassettes off their clips first") < guide.index("then DR's inner face")


def test_lanes_follow_the_parts():
    # a lane is as wide as its widest part plus the wrap a side; nothing in a tier passes the deck
    m = pack.Model()
    w = pack.MINE["wrap"].value
    tiers, height = m.tiers2()
    dr_lane = next(ln for t in tiers for ln in t["lanes"] if any(i["tag"] == "2-03" for i in ln["items"]))
    assert abs(dr_lane["width"] - (pack.PIECE["2-03"].dims[1] + 2 * w)) < 1e-9, dr_lane["width"]
    assert all(t["width"] <= pack.MINE["pal_std_l_exact"].value for t in tiers)
    assert height <= pack.lay("max_load_h")
    dt = pack.PIECE["2-12"]
    saved = dt.dims
    dt.dims = pack.S(1699, 420, 203)                       # a DT 114 mm wider no longer fits tier 3
    try:
        assert "K5" in failing(pack.Model())
    finally:
        dt.dims = saved


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
                    ("1-16", "510103"), ("2-14", "810201"), ("2-16", "810101"), ("1-01", "110401"),
                    ("1-03", "210201"), ("1-04", "210202"), ("1-17", "510201"), ("1-18", "510202"),
                    ("2-09", "350001"), ("2-12", "350002"), ("2-03", "350003")):
        p = pack.PIECE[tag]
        assert p.pn == pn and by_pn[pn][0] == p.name, (tag, p.pn, p.name)
    assert "K13" not in failing(m)
    # B3 and B4 carry WALL's names (its CAD files 210203/210204, 510203/510204), so their numbers fill in when WALL's lists merge
    for tag, pos in (("1-07", "B3"), ("1-08", "B4"), ("1-19", "B3"), ("1-20", "B4")):
        assert pack.PIECE[tag].name.endswith("BACK UPPER - " + pos), (tag, pack.PIECE[tag].name)


def test_tbd_piece_takes_its_bom_number(tmp=Path(__file__).resolve().parent / "_bom_test.csv"):
    # when an owner's list lands with the piece's exact name, the label gets the number without a code change;
    # the example is a piece still TBD in the real BOM (it was the air column until AIR's list landed, PR #91)
    tag, dr = next((t, pc) for t, pc in sorted(pack.PIECE.items())
                   if pc.pn_declared.startswith("TBD") and pc.pn == pc.pn_declared)
    vi = dr.vi + " (thử)"

    def add(rows):
        rows.append(dict(rows[-1], part_number="699999", name=dr.name, name_vi=vi))
    _bom_copy(add, tmp)
    try:
        m = pack.Model(bom_path=tmp)
        assert dr.pn == "699999" and dr.vi == vi, (tag, dr.pn, dr.vi)
        assert tag in m.filled and "K13" not in failing(m)
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
