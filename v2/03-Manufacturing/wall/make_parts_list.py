"""Parts list (BOM CSV, with the tube cut list) for a WALL panel position and its cassette, from the CAD.

    python3 v2/03-Manufacturing/wall/make_parts_list.py 210101 510101      # side panel L1 and its cassette
    python3 v2/03-Manufacturing/wall/make_parts_list.py 210202 510202      # back panel B2 and its cassette
    (the cassette's rows are left out until its report exists)

Reads out/<pn>.json (written in Fusion by v2/01-CAD-Native/wall/report_wall_doc.py) for the outer panel
assembly and its cassette, and writes <panel document name>_BOM.csv next to this script, in the columns
the master BOM reads (v2/04-BOM/README.md), plus maker, SKU and tightening torque for bought items
(guideline section 4.3: maker, exact SKU, size, grade, coating and source for every standard part).
Made parts, masses, member lengths, fill pieces and hardware counts come from the CAD: the joint hardware
the panel carries (rivnuts, stop washers, spigots) is modelled, so it is counted from its bodies and checked
against the holes it sits in; bolts are counted from their clearance holes. Bought and hardware items take
the joints register's part numbers (D-63; register table 2.1). The cut-length rows (kind "cut") are the
frame's own cut list; the master BOM skips them.
"""

import csv
import glob
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["level", "part_number", "name", "name_vi", "kind", "material", "finish", "process", "maker", "sku",
          "torque", "qty", "unit", "cut_length_mm", "size_mm", "tolerance", "mass_each_kg", "mass_total_kg", "mass_status",
          "status", "source", "note"]
REG = "joints register V2-ENG-JNT-01 table 2.1 (main, PR #47)"
SEL = "hardware selection V2-ENG-SEL"
TORQUE = "HOLD-01 (D-48): set by the PM from test T06 (half the lowest rivnut spin-out torque)"

# Hardware by register part number. mass: kg each (per metre for items bought by length); "cad" takes the
# modelled body's mass instead (parts we make, whose geometry is the model).
HW = {
    "838001": dict(name="HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", vi="Bulong lục giác chìm M6 × 16",
                   kind="PI", material="steel, property class 8.8 (ISO 898-1)", finish="zinc plated",
                   maker="HOLD: any maker to ISO 4762, picked at the RFQ", sku="ISO 4762 M6 x 16 - 8.8 - zinc plated",
                   torque=TORQUE, mass=0.0062, mstat="calculation",
                   basis="head Ø10 x 6 less the socket, shank Ø6 x 16 at 85% for the thread, 7850 kg/m3"),
    "838002": dict(name="HARDWARE - SOCKET HEAD BOLT - M6 X 25 - ISO 4762 8.8 ZINC",
                   vi="Bulong lục giác chìm M6 × 25 (chốt mối nối khép)", kind="PI",
                   material="steel, property class 8.8 (ISO 898-1)", finish="zinc plated",
                   maker="HOLD: any maker to ISO 4762, picked at the RFQ", sku="ISO 4762 M6 x 25 - 8.8 - zinc plated",
                   torque="snugged, not torqued: a pin (register 2.10)", mass=0.0083, mstat="calculation",
                   basis="head Ø10 x 6 less the socket, shank Ø6 x 25 at 85% for the thread, 7850 kg/m3"),
    "838003": dict(name="HARDWARE - RIVET NUT - M6 - STEEL ZINC - SHEREX CAH2-610-4.2", vi="Tán rút M6 thép mạ kẽm",
                   kind="PI", material="steel 1008/1010 (register H-03, SHX2; D-131 replaced the aluminium CAH3 with "
                                       "the same head and grip)", finish="zinc plated, trivalent passivation",
                   maker="Sherex (PEM)", sku="CAH2-610-4.2", torque=TORQUE, mass=0.0068, mstat="calculation",
                   basis="body Ø9.5 x 14.86 with an M6 bore and a Ø12.96 x 0.76 head (SHX2 sizes), 7850 kg/m3; "
                         "the CAD body is the installed envelope"),
    "838004": dict(name="HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2", vi="Long đen to M6 inox",
                   kind="PI", material="stainless steel A2", finish="none (plain stainless)",
                   maker="HOLD: any maker to ISO 7093-1, picked at the RFQ", sku="ISO 7093-1 - 6.4 x 18 x 1.6 - A2",
                   torque="", mass=0.0028, mstat="calculation", basis="6.4 x 18 x 1.6 (ISO 7093-1), 7900 kg/m3"),
    "838005": dict(name="HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE", vi="Vòng giữ đầu bulong",
                   kind="HOLD", material="elastomer (HOLD-02)", finish="as supplied (elastomer)", maker="HOLD-02", sku="HOLD-02",
                   torque="", mass=0.001, mstat="assumption", basis="a small grommet; part not chosen (HOLD-02)"),
    "831001": dict(name="HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", vi="Chốt định vị Ø8", kind="MP",
                   material="stainless steel A2 (EN 1.4301) bar", finish="bare stainless, as machined; threadlocker on the thread "
                   "when fitted (H-05)",
                   maker="made (register H-05)", sku="", torque="", mass="cad", mstat="calculation",
                   basis="CAD body: the Joints Engineer's STEP (one source, F-189): Ø8 pin to 8 proud of the "
                         "face, M6 x 8 stud, lead-in and hex socket (H-05 sizes PROPOSED)",
                   calc=0.00417, calc_basis="the Joints CAD's 0.00417 kg (BUILD-RECORD)"),
    "831002": dict(name="HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", vi="Long đen chặn nhôm", kind="MP",
                   material="aluminium sheet 1.5, 5000 or 6000 series", finish="mill finish (punched)",
                   maker="made (register H-08)", sku="", torque="", mass="cad", mstat="calculation",
                   basis="CAD body: the Joints Engineer's STEP (one source, F-189): Ø10.5 x Ø20 x 1.5 (H-08)",
                   calc=0.000915, calc_basis="the Joints CAD's 0.000915 kg (BUILD-RECORD)"),
    # the mitre plates (D-131, joints register H-40 to H-42): made hardware, welded into the frame's mitres
    "831007": dict(name="HARDWARE - MITRE PLATE - 20 X 40 - 45 DEG - 2.0 STEEL", vi="Tấm đệm góc vát 20 × 40 - 45° - thép 2.0",
                   kind="MP", material="steel plate 2.0, galvanized Z100, yield 280 MPa or more (as the frame tube, J-FRAME-01)",
                   finish="galvanized Z100; its welds wire-brushed and coated with a 2-component zinc-rich epoxy", maker="made (register H-40)", sku="", torque="",
                   mass="cad", mstat="calculation", basis="CAD body: 28.3 x 40 x 2.0 (H-40), 7850 kg/m3",
                   calc=0.0178, calc_basis="28.3 x 40 x 2.0 at 7850 kg/m3 (register: 17.8 g)"),
    "831008": dict(name="HARDWARE - MITRE PLATE - 20 X 40 TO 40 X 40 - 2.0 STEEL",
                   vi="Tấm đệm góc vát 20 × 40 với 40 × 40 - thép 2.0", kind="MP",
                   material="steel plate 2.0, galvanized Z100, yield 280 MPa or more (as the frame tube, J-FRAME-01)",
                   finish="galvanized Z100; its welds wire-brushed and coated with a 2-component zinc-rich epoxy", maker="made (register H-41)", sku="", torque="",
                   mass="cad", mstat="calculation", basis="CAD body: 44.7 x 40 x 2.0 (H-41), 7850 kg/m3",
                   calc=0.0281, calc_basis="44.7 x 40 x 2.0 at 7850 kg/m3 (register: 28.1 g)"),
    "831009": dict(name="HARDWARE - MITRE PLATE - 40 X 40 - 45 DEG - 2.0 STEEL", vi="Tấm đệm góc vát 40 × 40 - 45° - thép 2.0",
                   kind="MP", material="steel plate 2.0, galvanized Z100, yield 280 MPa or more (as the frame tube, J-FRAME-01)",
                   finish="galvanized Z100; its welds wire-brushed and coated with a 2-component zinc-rich epoxy", maker="made (register H-42)", sku="", torque="",
                   mass="cad", mstat="calculation", basis="CAD body: 56.6 x 40 x 2.0 (H-42), 7850 kg/m3",
                   calc=0.0355, calc_basis="56.6 x 40 x 2.0 at 7850 kg/m3 (register: 35.5 g)"),
    "848001": dict(name="SEALS - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA", vi="Gioăng mối nối 3.97",
                   kind="PI", material="PORON 4701-40 Soft polyurethane foam with PSA",
                   finish="none (foam, PSA liner one side)",
                   maker="Rogers (PORON), PSA laminated and slit by a converter (HOLD-05)",
                   sku="PORON 4701-40 Soft, 3.97 x 8 strip with PSA", torque="", mass=0.0076, mstat="calculation",
                   basis="per metre: 8 x 3.97 at 240 kg/m3 (assumption for the foam's density)"),
    "848004": dict(name="SEALS - CLOSING SEAM BULB SEAL - GAP 4 TO 7 - EPDM OR TPE", vi="Gioăng ống mối nối khép",
                   kind="HOLD", material="EPDM or TPE hollow bulb (HOLD-12)", finish="", maker="HOLD-12",
                   sku="HOLD-12: a low-force bulb whose published working gap covers 4.0-7.0", torque="",
                   mass=0.02, mstat="assumption", basis="per metre: about 20 g for a small hollow bulb"),
    "518001": dict(name="LINING - CASSETTE CLIP", vi="Kẹp treo cassette", kind="HOLD", material="HOLD (H03, HOLD-08)",
                   finish="", maker="HOLD-08", sku="HOLD-08: rated 8.3 kg shear, 8.0 kg pull-out, captive lock",
                   torque="", mass=0.04, mstat="assumption", basis="about 40 g each (D-81's working figure, H-10)"),
    "108002": dict(name="POD - ACP BOND SET - SIKATACK PANEL-50 WITH AKTIVATOR-205, PANEL PRIMER, FIXING TAPE",
                   vi="Bộ keo dán ACP", kind="PI",
                   material="SikaTack Panel-50 (ETA 19/0511), Sika Aktivator-205, Sika Panel Primer, "
                            "SikaTack Panel Fixing Tape", finish="",
                   maker="Sika", sku="SikaTack Panel-50 system (bond spec V2-ENG-BND)", torque="", mass=0.49,
                   mstat="calculation", basis="bond spec: about 8.7 m of 12 x 3 bead per side panel"),
    "848011": dict(name="SEALS - HOOK AND LOOP - 25 MM - LOCATING ONLY", vi="Băng gai dính định vị cassette",
                   kind="PI", material="hook-and-loop or reclosable fastener tape, 25 mm, PSA",
                   finish="", maker="VELCRO Brand, or 3M (one to pick at the RFQ)",
                   sku="VELCRO PS14 hook 25 mm, or 3M Dual Lock SJ3560 25 mm (%s)" % SEL, torque="", mass=0.03,
                   mstat="assumption", basis="per metre: about 30 g for a 25 mm tape"),
    "848012": dict(name="SEALS - CASSETTE EDGE SEAL - 10 X 2.0 TO 2.2 - VERY SOFT FOAM OR FIN",
                   vi="Gioăng mép cassette (rất mềm)", kind="HOLD",
                   material="very soft PSA foam strip 10 x 2.0-2.2, or a fin (R-J18)", finish="", maker="HOLD-13",
                   sku="HOLD-13: no more than about 2 kPa at 20% compression", torque="", mass=0.002,
                   mstat="assumption", basis="per metre: 10 x 2.1 at about 100 kg/m3 (assumption)"),
}


def joints_plates(root=os.path.normpath(os.path.join(HERE, "..", "..", ".."))):
    """The mitre plates' sizes from the Joints Engineer's own STEPs (one source: the blanks may change, as the
    Lead's shorter blank of 2026-11-01 does): each plate's mass basis and its calculated mass made from its
    STEP's box, read with the repo's STEP reader (mm). A plate whose STEP isn't in the repo keeps the register's
    text above."""
    sys.path.insert(0, os.path.join(root, "tools", "checks"))
    import stepfile                                       # noqa: E402  (the repo's own reader)
    for pn, reg in (("831007", "H-40"), ("831008", "H-41"), ("831009", "H-42")):
        paths = glob.glob(os.path.join(root, "v2", "03-Manufacturing", "joints", "%s_P01_*_STEP.step" % pn))
        if not paths:
            continue
        sf = stepfile.StepFile(paths[0])
        pts = [i["frame"].point(q) for i in sf.instances() for q in sf.solid(i["solid"]).points()]
        # in the README's axes: X along the mitre, Y across the frame (its depth), Z the thickness
        size = [max(q[k] for q in pts) - min(q[k] for q in pts) for k in range(3)]
        HW[pn]["basis"] = "CAD body: the Joints Engineer's STEP, %.2f x %.2f x %.2f (%s), 7850 kg/m3" % (
            size[0], size[1], size[2], reg)
        HW[pn]["calc"] = round(size[0] * size[1] * size[2] * 7850e-9, 5)
        HW[pn]["calc_basis"] = "%.2f x %.2f x %.2f at 7850 kg/m3 (the Joints Engineer's STEP)" % tuple(size)


joints_plates()


def load(pn):
    with open(os.path.join(HERE, "out", "%s.json" % pn), encoding="utf-8") as fh:
        return json.load(fh)


_BUILDER_VI = {}


def builder_vi(pn):
    """The Vietnamese name the build script gives part number `pn` (its PARTS table, loaded offline with stand-in
    adsk modules): the fallback when the cloud left a component's description empty (211102 in R1's panel)."""
    if not _BUILDER_VI:
        import types
        wall = os.path.join(HERE, "..", "..", "01-CAD-Native", "wall")
        repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        fake = types.ModuleType("adsk")
        fake.core, fake.fusion = types.ModuleType("adsk.core"), types.ModuleType("adsk.fusion")
        saved = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
        sys.modules.update({"adsk": fake, "adsk.core": fake.core, "adsk.fusion": fake.fusion})
        try:
            jobs = [("wall_side_panel.py", {"part": "panel", "side": sd, "row": r}) for sd in "LR" for r in "12"] + \
                   [("wall_back_panel.py", {"part": "panel", "pos": q}) for q in ("B1", "B2", "B3", "B4")]
            for script, args in jobs:
                path = os.path.join(wall, script)
                ns = {"__name__": "wall_names", "__file__": path, "SCRIPT_ARGS": dict(args, repo_root=repo)}
                with open(path, encoding="utf-8") as fh:
                    exec(compile(fh.read(), path, "exec"), ns)
                for _k, (num, _en, vi) in ns["PARTS"].items():
                    _BUILDER_VI.setdefault(num, vi)
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
    return _BUILDER_VI.get(pn, "")


def vi_name(desc, pn=None):
    parts = [p.strip() for p in (desc or "").split("|")]
    if len(parts) > 1 and parts[1]:
        return parts[1]
    return builder_vi(pn) if pn else ""


def en_name(comp):
    return re.sub(r"^\d+ ", "", comp["name"]).strip()


def holes_in(bodies, d):
    return [h for b in bodies for h in b["holes"] if abs(h["d"] - d) < 0.01 and h["full_circle"]]


def box_of(bodies):
    return [min(b["box"][i] for b in bodies) for i in range(3)] + [max(b["box"][i + 3] for b in bodies) for i in range(3)]


def placed_box_of(comps):
    """The box of these components' copies where they are in the design (the report's placed_box, D-120: a body's
    own box is in its component's space, so a joint-placed or imported copy sits at its own origin there); a
    report from before placed_box falls back to the bodies' own boxes."""
    boxes = [c["placed_box"] for c in comps if c.get("placed_box")]
    if len(boxes) == len([c for c in comps if c["bodies"] or c.get("placed_box")]) and boxes:
        return [min(b[i] for b in boxes) for i in range(3)] + [max(b[i + 3] for b in boxes) for i in range(3)]
    return box_of([b for c in comps for b in c["bodies"]])


def frame_box(rep, members):
    """A D-120 frame's box: its members and mitre plates where they are placed; from a report without placed boxes,
    its members' own boxes (members are built in place; a plate's own box sits at its origin)."""
    plates = [c for c in rep["components"] if c["part_number"] in ("831007", "831008", "831009")]
    if all(c.get("placed_box") for c in members + plates):
        return placed_box_of(members + plates)
    return box_of([m["bodies"][0] for m in members])


def size_of(box):
    return "%g x %g x %g" % tuple(round(box[i + 3] - box[i], 2) for i in range(3))


def member_length(body):
    b = body["box"]
    return round(max(b[i + 3] - b[i] for i in range(3)), 2)


def row(**kw):
    r = {f: "" for f in FIELDS}
    r.update({k: v for k, v in kw.items() if k in FIELDS})
    return r


def hw_row(pn, qty, unit, note, bodies=None, source=REG):
    h = dict(HW[pn])
    mass = h["mass"]
    if mass == "cad":
        if bodies:
            mass = round(sum(b["mass_kg"] for b in bodies) / len(bodies), 5)
        else:                            # a report from before the hardware was modelled
            mass, h["basis"] = h["calc"], h["calc_basis"]
    return row(level=1, part_number=pn, name=h["name"], name_vi=h["vi"], kind=h["kind"], material=h["material"],
               finish=h["finish"], maker=h["maker"], sku=h["sku"], torque=h["torque"], qty=qty, unit=unit,
               mass_each_kg=mass, mass_total_kg=round(mass * qty, 4),
               mass_status="%s: %s" % (h["mstat"], h["basis"]),
               status="HOLD" if h["kind"] == "HOLD" or h["maker"].startswith("HOLD") else "DRAFT",
               source=source, note=note)


def root_names(root, part, assy_en, assy_vi):
    """English and Vietnamese names of a design's root: its description, or, when the cloud left it empty
    (new documents, 2026-10-31), the names made from its frame's or tray's description."""
    names = (root["description"].split(" | ") + ["", ""])[:2]
    if names[0]:
        return names
    en, vi = (part["description"].split(" | ") + ["", ""])[:2]
    return assy_en(en), assy_vi(vi)


def hw_bodies(comps, pn):
    c = comps.get(pn)
    return c["bodies"] if c else []


FILL_TOL = "±2 on length, width and the notches' positions, thickness as supplied (assumption: knife-cut PET batt)"


def fill_bays(panel_pn):
    """WALL's FILL-PIECES.csv rows of one panel, in bay order: each bay's form, number, DXF and fit (D-123,
    D-128; make_fill_pieces.py writes them, check_fill_dxfs.py checks the DXFs against the CAD)."""
    with open(os.path.join(HERE, "FILL-PIECES.csv"), encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["panel"] == panel_pn]
    return sorted(rows, key=lambda r: int(r["bay"]))


def fill_cut(dxf, electrical=False):
    """D-128's process text for a fill piece cut from its DXF."""
    return ("knife cut from its DXF %s: the full outline with every notch (the 60 x 60 notches beside each bolt go "
            "right through the 40 mm batt)%s; no drawing (D-128)" % (dxf, " and ELECTRICAL's cut-outs" if electrical else ""))


def panel_rows(rep):
    rows = []
    root = [c for c in rep["components"] if c["is_root"]][0]
    comps = {c["part_number"]: c for c in rep["components"] if not c["is_root"]}
    prm = {p["name"]: p["value"] for p in rep["parameters"]}
    pn = rep["document"].split("_")[0]
    frame = [c for p, c in comps.items() if p.startswith(("2111", "2112"))][0]
    skin = [c for p, c in comps.items() if p.startswith(("2113", "2114"))][0]
    back = frame["part_number"].startswith("2112")
    lower = "LOWER" in frame["name"]
    members = [c for c in rep["components"] if frame["part_number"] in c.get("parents", [])
               and c["part_number"].startswith("212")]
    fills = [c for c in rep["components"] if c["part_number"].startswith(("2115", "2116"))]
    if members:
        # D-120: the fill pieces go straight into the panel (D-123 cancels the panel's own fill number)
        return panel_rows_d120(rep, root, comps, prm, pn, frame, skin, fills, members, back, lower)
    fill = fills[0]                                        # before D-120: the panel's fill, one part
    name_en, name_vi = root_names(root, frame, lambda n: n.replace("PANEL FRAME", "PANEL ASSY"),
                                  lambda n: n.replace("khung", "cụm tấm"))
    rows.append(None)                                      # the assembly row, once its parts are summed
    fm = round(sum(b["mass_kg"] for b in frame["bodies"]), 3)
    t, ts = prm.get("tube_t", 1.2), prm.get("stud_t", prm.get("tube_t", 1.2))
    rows.append(row(level=1, part_number=frame["part_number"], name=en_name(frame), name_vi=vi_name(frame["description"], frame["part_number"]),
                    kind="MP", material="aluminium tube 6063-T6: perimeter %s x %g, studs 20 x 40 x %g (D-85)" % (
                        "20 x 40" if back else "20 x 40 and 40 x 40", t, ts),
                    finish="mill finish with the bond prep (D-79)",
                    process="saw cut square, CNC or jig drill (holes Ø0.4 from the spigot hole, R-J6), rivnuts and "
                            "stop washers set at the factory, member joints: internal cleats per D-115 (crimped, "
                            "structural adhesive; no welds)",
                    qty=1, unit="pc", size_mm=size_of(box_of(frame["bodies"])), tolerance="per its drawing",
                    mass_each_kg=fm, mass_total_kg=fm,
                    mass_status="calculation: CAD at 2700 kg/m3", status="DRAFT",
                    source="CAD; tube confirmed (D-34, D-54, D-85%s)" % ("" if back else "; 40 x 40 R-J3"),
                    note="member joints: internal cleats per D-115 (the Joints Engineer's register parts, placed when "
                         "they land); rails full length" + (
                        "; 1 x 45 lead-in on the closing-seam face's top edge (R-J9)" if back else "")))
    cut = Counter()
    for b in frame["bodies"]:
        dims = sorted(round(b["box"][i + 3] - b["box"][i], 1) for i in range(3))
        wall = ts if b["name"].startswith("STILE - MID") else t
        sec = "%s x %g" % ("40 x 40" if dims[0] >= 39.9 else "20 x 40", wall)
        cut[(re.sub(r" \d+$", "", b["name"]), sec, member_length(b), b["mass_kg"])] += 1
    for (kind, sec, length, m), q in sorted(cut.items(), key=lambda k: (k[0][0], -k[0][2])):
        rows.append(row(level=2, name="%s (cut length)" % kind, name_vi="thanh nhôm", kind="cut",
                        material="aluminium tube 6063-T6 %s" % sec, qty=q, unit="pc", cut_length_mm=length, size_mm=sec,
                        tolerance="length ±0.5, square ends (assumption, guideline 6.3)",
                        mass_each_kg=round(m, 3), mass_total_kg=round(m * q, 3), mass_status="calculation: CAD",
                        status="DRAFT", source="CAD body length", note="square-cut ends; cut list of %s" % frame["part_number"]))
    sm = round(sum(b["mass_kg"] for b in skin["bodies"]), 3)
    rows.append(row(level=1, part_number=skin["part_number"], name=en_name(skin), name_vi=vi_name(skin["description"], skin["part_number"]),
                    kind="MP", material="ACP 3 mm Alcorest outdoor, PE-type core (HW-SEL A1)",
                    finish="PVDF coated EV3038 Dark Yellow (maker's coil coating; D-12)",
                    process=("CNC router: cut flat from the DXF, outline and holes; no drawing (D-89 part 4)" if back else
                             "CNC router: cut, V-groove and fold the back return (H16)"),
                    qty=1, unit="pc", size_mm=size_of(box_of(skin["bodies"])),
                    tolerance=("ISO 2768-m general tolerance (router cut; assumption until the ACP maker's own)" if back
                               else "per the tabulated skin drawing (D-89)"), mass_each_kg=sm, mass_total_kg=sm,
                    mass_status="calculation: CAD at 3.5 kg/m2 (HW-SEL A1); real kg/m2 HOLD (H16)", status="DRAFT",
                    source="CAD" + ("; holes ELECTRICAL P01 (PR #64)" if "el_inlet_x" in prm else ""),
                    note=("overhangs its frame 1.62 at the closing seam, so the skin seam is 2.26 (R-J16)"
                          if back else "blank and fold line in the skin DXF") + (
                        "; two Ø%g holes for ELECTRICAL's mains inlet and LAN feed-through, in the DXF" % prm["el_inlet_d"]
                        if "el_inlet_x" in prm else "")))
    fl = round(sum(b["mass_kg"] for b in fill["bodies"]), 3)
    pieces = Counter(tuple(sorted((round(b["box"][i + 3] - b["box"][i], 1) for i in range(3)), reverse=True)[:2])
                     for b in fill["bodies"])
    bays = fill_bays(pn)
    rows.append(row(level=1, part_number=fill["part_number"], name=en_name(fill), name_vi=vi_name(fill["description"], fill["part_number"]),
                    kind="MP", material="PET fill 40 mm, 24 kg/m3, Pyrotek Sorberpoly 2D (HW-SEL B)",
                    process="knife cut, one piece per bay, each from its form's DXF: the full outline with every notch "
                            "(the 60 x 60 notches beside each bolt this panel drives go right through the 40 mm batt)%s; "
                            "no drawing (D-128)" % (" and ELECTRICAL's cut-outs" if "el_cut_x0" in prm else ""),
                    qty=1, unit="set",
                    size_mm="; ".join("%d pieces %g x %g x 40" % (q, a, b) for (a, b), q in sorted(pieces.items())),
                    tolerance=FILL_TOL,
                    mass_each_kg=fl, mass_total_kg=fl, mass_status="calculation: CAD at the design's fill density",
                    status="DRAFT", source="CAD; 24 kg/m3 PM ruling 2026-10-31 (T02 confirms, else 32); DXFs checked "
                                           "against the CAD (check_fill_dxfs.py)",
                    note="friction fit in the bays; " + "; ".join(
                        "bay %s: %s %s %s, %s" % (b["bay"], b["form"], b["number"], b["dxf"], b["fit"]) for b in bays) + (
                        "; bay 1's piece cut away for ELECTRICAL's power unit (to the first stud), sleeve and connectors"
                        if "el_cut_x0" in prm else "")))
    rows += hardware_rows(frame, comps, back, lower, prm)
    made = round(sum(r["mass_total_kg"] for r in rows[1:] if r["level"] == 1), 3)
    rows[0] = row(level=0, part_number=pn, name=name_en, name_vi=name_vi, kind="HS",
                  material="see the parts below", qty=1, unit="pc",
                  size_mm=size_of(placed_box_of(list(comps.values()))),
                  mass_total_kg=made, mass_status="calculation: the sum of the rows below (CAD bodies and hardware)",
                  status="DRAFT", source="CAD %s v%s" % (rep["document"], rep["version"]),
                  note="outer panel, bonded and hardware-fitted at the factory; the lining cassette is a separate part "
                       "(D-17)")
    return rows


def mitre_ends(key, prm, upper, back=False):
    """The cut at each end of a frame member (D-117): the mitre runs from the frame's outer corner to its inner
    corner, so a member's end is cut atan(other member's width / its own width) off square (45 where the two are
    the same size, 26.57 on a 40 x 40 meeting a 20 x 40, 63.43 on the 20 x 40); studs are square."""
    import math
    tw, cw = prm.get("tube_w", 20.0), prm.get("corner_w", 40.0)
    top = prm.get("top_h", cw if upper else tw)
    width = {"RAIL BOTTOM": tw, "RAIL TOP": top, "STILE FRONT": tw, "STILE BACK": cw, "STILE OUTER": tw,
             "STILE CENTRE": tw}
    ends = ("STILE OUTER", "STILE CENTRE") if back else ("STILE FRONT", "STILE BACK")   # what a rail meets
    meets = {"RAIL BOTTOM": ends, "RAIL TOP": ends,
             "STILE FRONT": ("RAIL BOTTOM", "RAIL TOP"), "STILE BACK": ("RAIL BOTTOM", "RAIL TOP"),
             "STILE OUTER": ("RAIL BOTTOM", "RAIL TOP"), "STILE CENTRE": ("RAIL BOTTOM", "RAIL TOP")}
    if key not in meets:
        return "square ends (fits between the rails, welded T joints, D-131)"
    angles = ["%.2f" % math.degrees(math.atan(width[o] / width[key])) for o in meets[key]]
    return ("both ends mitred: %s and %s degrees off square (D-117), cut back for the 2 mm mitre plate and welded "
            "(D-131)" % tuple(angles))


def panel_rows_d120(rep, root, comps, prm, pn, frame, skin, pieces, members, back, lower):
    """The parts list of a panel built as D-120 asks (every part its own component): the frame an assembly of
    its member parts, welded (D-131: galvanized steel box tube, D-117's mitred corners welded, the studs' T joints
    welded; D-117's cleats cancelled), the fill pieces straight in the panel, each with its
    number (D-123) and its DXF (D-128), the hardware copies
    counted from the CAD."""
    rows = [None]
    upper = not lower
    name_en, name_vi = root_names(root, frame, lambda n: n.replace("PANEL FRAME", "PANEL ASSY"),
                                  lambda n: n.replace("khung", "cụm tấm"))
    t, ts = prm.get("tube_t", 1.0), prm.get("stud_t", prm.get("tube_t", 1.0))
    member_rows, fm = [], 0.0
    for m in sorted(members, key=lambda c: c["part_number"]):
        b = m["bodies"][0]
        key = re.sub(r"^WALL - FRAME | 40 X 40| - (SIDE|BACK) .*$", "", m["name"].split(" ", 1)[1]).strip()
        dims = sorted(round(b["box"][i + 3] - b["box"][i], 1) for i in range(3))
        sec = "%s x %g" % ("40 x 40" if dims[0] >= 39.9 else "20 x 40",
                           ts if key == "STILE MID" else (prm.get("corner_t", t) if dims[0] >= 39.9 else t))
        q = m.get("copies", 1)
        fm += b["mass_kg"] * q
        member_rows.append(row(level=2, part_number=m["part_number"], name=en_name(m),
                               name_vi=vi_name(m["description"], m["part_number"]), kind="MP",
                               material="steel box tube %s, S280GD+Z (EN 10346) or SGC400 (JIS G3302): certified "
                                        "yield 280 MPa or more, zinc Z100 (J-FRAME-01, D-131)" % sec,
                               finish="pre-galvanized tube, zinc Z100; after welding and grinding every burnt zone "
                                      "wire-brushed and coated with a 2-component zinc-rich epoxy; no hot-dip "
                                      "(J-FRAME-01)",
                               process="saw cut; %s; welded into its frame (D-131); its joint holes are made after "
                                       "welding, in the frame (J-FRAME-01)" % mitre_ends(key, prm, upper, back),
                               qty=q, unit="pc", cut_length_mm=member_length(b), size_mm=sec,
                               tolerance="length ±0.5 (assumption, guideline 6.3); its holes per the frame drawing, "
                                         "made in the welded frame",
                               mass_each_kg=round(b["mass_kg"], 3), mass_total_kg=round(b["mass_kg"] * q, 3),
                               mass_status="calculation: CAD at 7850 kg/m3 (steel; zinc not counted)", status="DRAFT",
                               source="CAD; number from the master BOM's allocation (D-120); steel D-131",
                               note="%s; cut length outer to outer" % mitre_ends(key, prm, upper, back)))
    for pc in sorted((c for c in rep["components"] if c["part_number"] in ("831007", "831008", "831009")),
                     key=lambda c: c["part_number"]):
        q = pc.get("copies", 1)
        r = hw_row(pc["part_number"], q, "pc", "welded into the frame's mitres, one at each corner where its members "
                   "meet (the Joints Engineer's corner detail, D-131)", bodies=pc["bodies"])
        r["level"] = 2
        fm += r["mass_total_kg"]
        member_rows.append(r)
    rows.append(row(level=1, part_number=frame["part_number"], name=en_name(frame),
                    name_vi=vi_name(frame["description"], frame["part_number"]), kind="BS",
                    material="the steel box tube members below and the 4 mitre plates, welded (D-131)",
                    finish="pre-galvanized tube, zinc Z100; every weld and burnt zone wire-brushed and coated with a "
                           "2-component zinc-rich epoxy; no hot-dip (J-FRAME-01); the skin's bond prep per the bond spec",
                    process="weld in a jig: each mitred corner with its 2 mm mitre plate (the Joints Engineer's register "
                            "part), and every stud's T joints (D-131; weld sizes and the coupons per the joints register); "
                            "grind the beads flush on the skin-side and seam faces; wire-brush and touch up every burnt "
                            "zone; check flatness and diagonals; then make every joint hole (spigot hole and slot, "
                            "clearance, access and rivnut holes) by CNC or a drill jig located on the joint faces and "
                            "the spigot hole; set the rivnuts and stop washers after the touch-up (J-FRAME-01)" + (
                                "; the closing seam's top corner weld ground to a 1 x 45 lead-in (R-J9, FR-13)"
                                if back else ""),
                    qty=1, unit="pc",
                    size_mm=size_of(frame_box(rep, members)),
                    tolerance="seam faces flat within 0.5, skin-side faces within ±0.5 of one plane, diagonals equal "
                              "within 1.5, measured after welding and before the holes (J-FRAME-01); hole positions "
                              "Ø0.4 from the round spigot hole (R-J6); the rest per its drawing",
                    mass_each_kg=round(fm, 3), mass_total_kg=round(fm, 3),
                    mass_status="calculation: the members below (CAD); weld metal not counted",
                    status="DRAFT", source="CAD; D-120, D-131 (D-117's mitred corners, welded; its cleats cancelled)",
                    note="an assembly of %d member parts (%d pieces)" % (len(members), sum(m.get("copies", 1)
                                                                                           for m in members))))
    rows += member_rows
    sm = round(sum(b["mass_kg"] for b in skin["bodies"]), 3)
    rows.append(row(level=1, part_number=skin["part_number"], name=en_name(skin),
                    name_vi=vi_name(skin["description"], skin["part_number"]),
                    kind="MP", material="ACP 3 mm Alcorest outdoor, PE-type core (HW-SEL A1)",
                    finish="PVDF coated EV3038 Dark Yellow (maker's coil coating; D-12)",
                    process=("CNC router: cut flat from the DXF, outline and holes; no drawing (D-89 part 4)" if back else
                             "CNC router: cut, V-groove and fold the back return (H16)"),
                    qty=1, unit="pc", size_mm=size_of(box_of(skin["bodies"])),
                    tolerance=("ISO 2768-m general tolerance (router cut; assumption until the ACP maker's own)" if back
                               else "per the tabulated skin drawing (D-89)"), mass_each_kg=sm, mass_total_kg=sm,
                    mass_status="calculation: CAD at 3.5 kg/m2 (HW-SEL A1); real kg/m2 HOLD (H16)", status="DRAFT",
                    source="CAD", note=("overhangs its frame 1.62 at the closing seam, so the skin seam is 2.26 (R-J16)"
                                        if back else "blank and fold line in the skin DXF")))
    bays = fill_bays(pn)
    if sorted(r["number"] for r in bays) != sorted(c["part_number"] for c in pieces for _ in range(c.get("copies", 1))):
        raise SystemExit("%s: fill pieces in the CAD %s, in FILL-PIECES.csv %s" % (
            pn, sorted(c["part_number"] for c in pieces), sorted(r["number"] for r in bays)))
    for c in pieces:
        if c.get("parents") and pn not in c["parents"]:
            raise SystemExit("%s sits in %s, not straight in the panel %s (D-123)" % (c["part_number"], c["parents"], pn))
    for c in sorted(pieces, key=lambda c: c["part_number"]):
        b = c["bodies"][0]
        dims = sorted((round(b["box"][i + 3] - b["box"][i], 1) for i in range(3)), reverse=True)
        q = c.get("copies", 1)
        mine = [r for r in bays if r["number"] == c["part_number"]]
        if len(mine) != q or len({r["dxf"] for r in mine}) != 1:
            raise SystemExit("%s: %d copies in the CAD, %d bays in FILL-PIECES.csv" % (c["part_number"], q, len(mine)))
        rows.append(row(level=1, part_number=c["part_number"], name=en_name(c),
                        name_vi=vi_name(c["description"], c["part_number"]), kind="MP",
                        material="PET fill 40 mm, 24 kg/m3, Pyrotek Sorberpoly 2D (HW-SEL B)",
                        process=fill_cut(mine[0]["dxf"], bool(mine[0]["note"])),
                        qty=q, unit="pc", size_mm="%g x %g x %g (outline and notches in the DXF)" % tuple(dims),
                        tolerance=FILL_TOL,
                        mass_each_kg=round(b["mass_kg"], 3), mass_total_kg=round(b["mass_kg"] * q, 3),
                        mass_status="calculation: CAD at the design's fill density", status="DRAFT",
                        source="CAD; DXF checked against the CAD (check_fill_dxfs.py); number from the master BOM's "
                               "allocation (D-123)",
                        note="friction fit in its bay: " + "; ".join("bay %s %s" % (r["bay"], r["fit"]) for r in mine)))
    # the hardware rules count bodies and holes: give them every copy (a member's holes once per copy; the rivnut
    # copies at spigot sites named so, as the old per-site bodies were)
    frame_flat = dict(frame, bodies=[b for m in members for b in m["bodies"] for _ in range(m.get("copies", 1))])
    comps_flat = dict(comps)
    n_spig = comps.get("831001", {}).get("copies", 0) if comps.get("831001") else 0
    for hp in ("838003", "831002", "831001"):
        c = comps.get(hp)
        if c:
            copies = [dict(c["bodies"][0], name="%s %d" % ("RIVNUT - SPIGOT" if hp == "838003" and k < n_spig else
                                                         c["bodies"][0]["name"], k + 1))
                      for k in range(c.get("copies", 1))]
            comps_flat[hp] = dict(c, bodies=copies)
    rows += hardware_rows(frame_flat, comps_flat, back, lower, prm)
    made = round(sum(r["mass_total_kg"] for r in rows[1:] if r["level"] == 1), 3)
    rows[0] = row(level=0, part_number=pn, name=name_en, name_vi=name_vi, kind="HS",
                  material="see the parts below", qty=1, unit="pc",
                  size_mm=size_of(placed_box_of(list(comps.values()))),
                  mass_total_kg=made, mass_status="calculation: the sum of the rows below (CAD bodies and hardware)",
                  status="DRAFT", source="CAD %s v%s" % (rep["document"], rep["version"]),
                  note="outer panel, bonded and hardware-fitted at the factory; every part its own component (D-120); "
                       "the lining cassette is a separate part (D-17)")
    return rows


def hardware_rows(frame, comps, back, lower, prm):
    """The joint hardware this panel carries, counted from the CAD (bodies where modelled, holes otherwise)."""
    fb = frame["bodies"]
    rv_bodies, sw_bodies, sp_bodies = (hw_bodies(comps, p) for p in ("838003", "831002", "831001"))
    rivnut_holes = len(holes_in(fb, prm.get("rivnut_d", 9.53)))
    pins = [b for b in rv_bodies if "PIN" in b["name"]]
    spig_rv = [b for b in rv_bodies if "SPIGOT" in b["name"]]
    if rv_bodies and len(rv_bodies) != rivnut_holes:
        raise SystemExit("CAD has %d rivnut bodies for %d rivnut holes" % (len(rv_bodies), rivnut_holes))
    rivnuts = len(rv_bodies) or rivnut_holes
    if not rv_bodies:                    # a report from before the hardware was modelled
        spig_rv = [None] * (2 if (lower or back) else 0)
        pins = [None] * (3 if back and len(holes_in([b for b in fb if b["name"] == "STILE - CENTRE"], 9.53)) else 0)
    stopped = rivnuts - len(spig_rv) - len(pins)
    if sw_bodies and len(sw_bodies) != stopped:
        raise SystemExit("CAD has %d stop washers for %d stopped-joint rivnuts" % (len(sw_bodies), stopped))
    centre_holes = [b for b in fb if b["name"] == "STILE - CENTRE"]
    pin_holes = len(holes_in(centre_holes, prm.get("bolt_d", 7.0))) if back else 0
    bolts = len(holes_in(fb, prm.get("bolt_d", 7.0))) - pin_holes        # B1/B3: the pin's plain hole takes no bolt
    top = [b for b in fb if b["name"] == "RAIL - TOP"][0]
    height = round(box_of(fb)[5] - box_of(fb)[2], 2)
    rows = []
    if back:
        bead = round(sum(member_length(b) for b in fb) / 1000.0, 2)
        r = hw_row("108002", 1, "set", "one 12 x 3 joint on every member touching the skin, %.2f m of bead" % bead,
                   source="%s; bond spec V2-ENG-BND (PR #23)" % REG)
        r["mass_each_kg"] = r["mass_total_kg"] = round(0.49 / 8.7 * bead, 3)
        r["mass_status"] = "calculation: the bond spec's 0.49 kg per 8.7 m of bead, on this frame's %.2f m" % bead
        rows.append(r)
    else:
        rows.append(hw_row("108002", 1, "set", "one 12 x 3 joint on every member touching the skin; in-line tape "
                           "HOLD-B2", source="%s; bond spec V2-ENG-BND (PR #23)" % REG))
    roles = []
    if stopped:
        roles.append("%d stopped joints" % stopped)
    if spig_rv:
        roles.append("%d spigot rivnuts" % len(spig_rv))
    if pins:
        roles.append("%d closing-seam pin rivnuts, no stop washer" % len(pins))
    rows.append(hw_row("838003", rivnuts, "pc", "; ".join(roles) + "; CAD bodies at every rivnut hole",
                       bodies=rv_bodies or None))
    if stopped:
        rows.append(hw_row("831002", stopped, "pc", "one under each stopped-joint rivnut's head; sets the 2.26 gap",
                           bodies=sw_bodies or None))
    if spig_rv:
        rows.append(hw_row("831001", len(spig_rv), "pc", "in the top rail's spigot rivnuts, locating the %s above" % (
            "ceiling" if back and not lower else "panel"), bodies=sp_bodies or None))
    if bolts:
        rows.append(hw_row("838001", bolts, "pc", "captive, driven from this panel: %s" % (
            "J-BASE-01 or J-WALL-01 (bottom rail), J-WALL-02 (corner)%s" % ("" if lower else ", J-CEIL-01 (top rail)")
            if back else "J-BASE-01 or J-WALL-01 (bottom rail), J-FRONT-01 (front stile)")))
    if pins:
        rows.append(hw_row("838002", len(pins), "pc", "closing-seam pins, factory-fitted captive in their rivnuts, "
                           "driven across on site (register 2.10)"))
    if bolts or pins:
        rows.append(hw_row("838004", bolts + len(pins), "pc", "one under each bolt head (R-J10)"))
    if bolts:
        rows.append(hw_row("838005", bolts, "pc", "grommet in each Ø19 access hole, holding its bolt (HOLD-02); the "
                           "pins need none"))
    if back:
        if lower:
            rows.append(hw_row("848001", round(member_length(top) / 1000.0, 2), "m",
                               "on the top rail, the nut side of J-WALL-01 (%g)" % member_length(top)))
        if pins:
            rows.append(hw_row("848004", round(height / 1000.0, 2), "m",
                               "on the closing-seam face beside the rivnut heads (R-J7, R-J17), %g" % height))
    else:
        rows.append(hw_row("848001", round((member_length(top) + height) / 1000.0, 2), "m",
                           "on this panel's nut-side faces: the top member (%g) and the back stile's room face (%g)" % (
                               member_length(top), height)))
    return rows


def cassette_rows(rep):
    rows = []
    root = [c for c in rep["components"] if c["is_root"]][0]
    comps = {c["part_number"]: c for c in rep["components"] if not c["is_root"]}
    real = {p: c for p, c in comps.items() if not p.startswith("NO-PN")}
    tray = [c for c in real.values() if " - TRAY - " in c["name"]][0]
    felt = [c for c in real.values() if " - FELT - " in c["name"]][0]
    clips = [c for p, c in comps.items() if p.startswith("NO-PN")][0]
    tb, fb = tray["bodies"][0], felt["bodies"][0]
    made = sum(b["mass_kg"] for c in real.values() for b in c["bodies"])
    pn = rep["document"].split("_")[0]
    back = pn.startswith("5102")
    lower = "LOWER" in tray["name"]
    # ELECTRICAL's features (el_ parameters in the design; ELECTRICAL P01, PR #64)
    el = {q["name"] for q in rep.get("parameters", []) if q["name"].startswith("el_")}
    tray_el = ("; ELECTRICAL's power unit cut-out (304 x 268, plain), the corner slot and the joint's bushing hole, "
               "all in the flat blank" if "el_cut_x0" in el else
               "; ELECTRICAL's light feed bushing hole in the bottom return, in the flat blank" if "el_lt_x" in el else "")
    felt_el = bool(el & {"el_fs_y0", "el_call_y", "el_cut_x0", "el_shelf_d"})
    name_en, name_vi = root_names(root, tray, lambda n: n.replace(" - TRAY - ", " - CASSETTE - "),
                                  lambda n: n.replace("Khay thép lót", "Cassette lót") + " (khay thép + tấm tiêu âm)")
    length = round(max(tb["box"][3] - tb["box"][0], tb["box"][4] - tb["box"][1]), 2)
    height = round(tb["box"][5] - tb["box"][2], 2)
    rows.append(row(level=0, part_number=pn, name=name_en, name_vi=name_vi, kind="BS", material="see the parts below",
                    qty=1, unit="pc", size_mm=size_of(box_of([tb, fb])), mass_total_kg=round(made, 3),
                    mass_status="calculation: CAD bodies of the made parts", status="DRAFT",
                    source="CAD %s v%s" % (rep["document"], rep["version"]),
                    note="floating inner leaf; clips onto the panel frame from inside (D-17, D-47)"))
    rows.append(row(level=1, part_number=tray["part_number"], name=en_name(tray), name_vi=vi_name(tray["description"], tray["part_number"]),
                    kind="MP", material="galvanised steel sheet 0.5, EN 10346 DX51D+Z",
                    finish="hot-dip zinc (coating mass to confirm)", process="laser or punch blank, brake bend (sheet metal)",
                    qty=1, unit="pc", size_mm=size_of(tb["box"]), tolerance="per the tabulated tray drawing (D-89)",
                    mass_each_kg=tb["mass_kg"], mass_total_kg=tb["mass_kg"],
                    mass_status="calculation: CAD at 7850 kg/m3", status="DRAFT",
                    source="CAD; 0.5 confirmed (D-37); lips PM ruling 2026-10-31" + (
                        "; ELECTRICAL P01 (PR #64)" if tray_el else ""),
                    note="34 mm returns turned in as 12 mm lips that hold the felt; flat blank in the DXF" + tray_el))
    rows.append(row(level=1, part_number=felt["part_number"], name=en_name(felt), name_vi=vi_name(felt["description"], felt["part_number"]),
                    kind="MP", material="PET felt 9 mm Dark Gray, grade about 200 kg/m3 (1.8 kg/m2 at 9 mm, Polyx "
                                        "Board 9 data); the factory's felt (D-31; plan VT03-PET)",
                    process=("knife or CNC knife cut from its DXF, the full outline with every opening (ELECTRICAL's); "
                             "no drawing (D-128)" if felt_el else
                             "knife or die cut, a plain rectangle; no drawing (D-89)"), qty=1, unit="pc",
                    size_mm=size_of(fb["box"]) + (" (outline and openings in the DXF)" if felt_el else ""),
                    tolerance="±1 on length, width and the openings' positions (assumption: knife cut)",
                    mass_each_kg=fb["mass_kg"], mass_total_kg=fb["mass_kg"],
                    mass_status="calculation: CAD at 1.8 kg/m2 (Polyx Board 9 data, HW-SEL A3); the factory felt unverified",
                    status="DRAFT", source="CAD" + ("; openings ELECTRICAL P01 (PR #64)" if felt_el else ""),
                    note="held by the tray's lips over the 24 mm air gap (settles H09)"))
    rows += [
        hw_row("518001", len(clips["bodies"]), "pc", "zones reserved on the panel frame's first and last studs; "
               "8.3 kg rated in shear each (register J-LIN-01)"),
        hw_row("848011", 0.2, "m", "4 pads of 50 mm to line the cassette up (assumption); carries no load (D-47)"),
    ]
    seal, where = 0.0, []
    if lower:
        seal += length
        where.append("the top edge against the upper cassette (%g)" % length)
    if back and pn[-2:] in ("01", "03"):
        seal += height
        where.append("the X 0 edge against the next back cassette (%g; the 2.26 gap there is PROPOSED)" % height)
    if seal:
        rows.append(hw_row("848012", round(seal / 1000.0, 2), "m", "only touches across the 2.26 gap, no load (R-J18): "
                           + "; ".join(where)))
    return rows


def main(argv):
    panel = load(argv[1])
    have_cass = len(argv) > 2 and os.path.exists(os.path.join(HERE, "out", "%s.json" % argv[2]))
    if len(argv) > 2 and not have_cass:
        print("no report for %s yet: the panel's rows only" % argv[2])
    out = os.path.join(HERE, "%s_BOM.csv" % panel["document"].rsplit("_CAD", 1)[0])
    rows = panel_rows(panel) + (cassette_rows(load(argv[2])) if have_cass else [])
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    top = [r for r in rows if r["level"] == 0]
    print("wrote %s: %d rows; panel %s kg with its hardware%s" % (
        os.path.basename(out), len(rows), top[0]["mass_total_kg"],
        ", cassette %s kg" % top[1]["mass_total_kg"] if len(top) > 1 else ", no cassette yet"))


if __name__ == "__main__":
    main(sys.argv)
