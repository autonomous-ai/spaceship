"""Parts list (BOM CSV, with the tube cut list) for a WALL side panel position and its cassette, from the CAD.

    python3 v2/03-Manufacturing/wall/make_parts_list.py 210101 510101

Reads out/<pn>.json (written in Fusion by v2/01-CAD-Native/wall/report_wall_doc.py) for the outer panel
assembly and its cassette, and writes <panel document name>_BOM.csv next to this script, in the columns
the master BOM reads (v2/04-BOM/README.md). Made parts, masses, member lengths, fill pieces and hardware
counts come from the CAD (hole counts by size); bought and hardware items take the joints register's part
numbers (D-63; PR #23 table 2.1), with masses worked out here from their standard sizes (calculation) or
the register's working figure. Items the register hasn't numbered yet keep a blank number and say so.
The cut-length rows (kind "cut") are the frame's own cut list; the master BOM skips them.
"""

import csv
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["level", "part_number", "name", "name_vi", "kind", "material", "finish", "process", "qty", "unit",
          "cut_length_mm", "size_mm", "mass_each_kg", "mass_total_kg", "mass_status", "status", "source", "note"]
REG = "joints register V2-ENG-JNT-01 (PR #23) table 2.1"

# Hardware by register part number: name, Vietnamese, kind, material, finish, mass each (kg), mass status, basis
HW = {
    "838001": ("HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16", "PI",
               "steel 8.8", "zinc plated", 0.0062, "calculation",
               "head Ø10 × 6 less the socket, shank Ø6 × 16 at 85% for the thread, steel 7850 kg/m3"),
    "838003": ("HARDWARE - RIVET NUT - M6 - SHEREX CAH3-610-4.2", "Tán rút M6", "PI", "aluminium 5056", "plain",
               0.0023, "calculation", "body Ø9.5 × 14.86 with an M6 bore and a Ø12.96 × 0.76 head (SHX sizes), 2700 kg/m3"),
    "838004": ("HARDWARE - WASHER - M6 LARGE - ISO 7093-1 6.4 X 18 A2", "Long đen to M6 inox", "PI", "stainless A2",
               "plain", 0.0028, "calculation", "6.4 × 18 × 1.6 (ISO 7093-1), 7900 kg/m3"),
    "838005": ("HARDWARE - CAPTIVE RETAINER - M6 HEAD - GROMMET FOR 19 HOLE", "Vòng giữ đầu bulong", "HOLD",
               "elastomer (HOLD-02)", "", 0.001, "assumption", "a small grommet; part not chosen (HOLD-02)"),
    "831001": ("HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS", "Chốt định vị Ø8", "MP", "stainless", "plain",
               0.0049, "calculation", "Ø8 × 8 proud plus an M6 × 10 thread (register H-05 sizes), 7900 kg/m3"),
    "831002": ("HARDWARE - STOP WASHER - Ø10.5 X Ø20 X 1.5 - AL", "Long đen chặn nhôm", "MP",
               "aluminium sheet 1.5, 5000 or 6000 series", "mill", 0.0009, "calculation", "Ø10.5 × Ø20 × 1.5, 2700 kg/m3"),
    "848001": ("HARDWARE - JOINT GASKET - 8 X 3.97 - PORON 4701-40 PSA", "Gioăng mối nối 3.97", "PI",
               "PORON 4701-40 Soft with PSA", "", 0.0076, "calculation",
               "per metre: 8 × 3.97 at 240 kg/m3 (assumption for the foam's density)"),
    "518001": ("LINING - CASSETTE CLIP", "Kẹp treo cassette", "HOLD", "HOLD (H03, HOLD-08)", "", 0.04, "assumption",
               "about 40 g each (D-81's working figure, joints register H-10)"),
    "108002": ("POD - ACP BOND SET - SIKATACK PANEL-50 SYSTEM", "Bộ keo dán ACP", "PI",
               "SikaTack Panel-50 (ETA 19/0511), Aktivator-205, Panel Primer, Panel Fixing Tape", "", 0.49, "calculation",
               "bond spec: about 8.7 m of 12 x 3 bead per side panel (joints register follow-up, relayed by the PM)"),
    "848011": ("SEALS - HOOK-AND-LOOP - 25 MM - LOCATING ONLY", "Miếng dán Velcro định vị", "PI",
               "VELCRO PS14 hook 25 mm or 3M Dual Lock SJ3560", "", 0.03, "assumption",
               "per metre: about 30 g for a 25 mm tape; 1.6 m for the 8 wall cassettes (register)"),
    "848012": ("SEALS - CASSETTE EDGE GASKET - 10 X 3.18 - PSA FOAM", "Gioăng mép cassette", "PI",
               "PORON 4701-40 Soft with PSA, 10 x 3.18", "", 0.0076, "calculation",
               "per metre: 10 x 3.18 at 240 kg/m3 (assumption for the foam's density); 29% squeeze in the 2.26 gap"),
}


def load(pn):
    with open(os.path.join(HERE, "out", "%s.json" % pn), encoding="utf-8") as fh:
        return json.load(fh)


def vi_name(desc):
    parts = [p.strip() for p in (desc or "").split("|")]
    return parts[1] if len(parts) > 1 else ""


def en_name(comp):
    return re.sub(r"^\d+ ", "", comp["name"]).strip()


def holes_in(comp, d):
    return [h for b in comp["bodies"] for h in b["holes"] if abs(h["d"] - d) < 0.01 and h["full_circle"]]


def box_of(bodies):
    return [min(b["box"][i] for b in bodies) for i in range(3)] + [max(b["box"][i + 3] for b in bodies) for i in range(3)]


def size_of(box):
    return "%g x %g x %g" % tuple(round(box[i + 3] - box[i], 2) for i in range(3))


def member_length(body):
    b = body["box"]
    return round(max(b[i + 3] - b[i] for i in range(3)), 2)


def row(**kw):
    r = {f: "" for f in FIELDS}
    r.update({k: v for k, v in kw.items() if k in FIELDS})
    return r


def hw_row(pn, qty, unit, note, source=REG):
    name, vn, kind, mat, fin, mass, mstat, basis = HW[pn]
    return row(level=1, part_number=pn, name=name, name_vi=vn, kind=kind, material=mat, finish=fin, qty=qty, unit=unit,
               mass_each_kg=mass, mass_total_kg=round(mass * qty, 4), mass_status="%s: %s" % (mstat, basis),
               status="HOLD" if kind == "HOLD" else "DRAFT", source=source, note=note)


def panel_rows(rep):
    rows = []
    root = [c for c in rep["components"] if c["is_root"]][0]
    comps = {c["part_number"]: c for c in rep["components"] if not c["is_root"]}
    frame = [c for p, c in comps.items() if p.startswith(("2111", "2112"))][0]
    skin = [c for p, c in comps.items() if p.startswith(("2113", "2114"))][0]
    fill = [c for p, c in comps.items() if p.startswith(("2115", "2116"))][0]
    made = sum(b["mass_kg"] for c in comps.values() for b in c["bodies"])
    pn = rep["document"].split("_")[0]
    name_en, name_vi = (root["description"].split(" | ") + ["", ""])[:2]
    rows.append(row(level=0, part_number=pn, name=name_en, name_vi=name_vi, kind="HS",
                    material="see the parts below", qty=1, unit="pc",
                    size_mm=size_of(box_of([b for c in comps.values() for b in c["bodies"]])),
                    mass_total_kg=round(made, 3), mass_status="calculation: CAD bodies of the made parts",
                    status="DRAFT", source="CAD %s v%s" % (rep["document"], rep["version"]),
                    note="outer panel, bonded and hardware-fitted at the factory; the lining cassette is a separate part (D-17)"))
    fm = round(sum(b["mass_kg"] for b in frame["bodies"]), 3)
    rows.append(row(level=1, part_number=frame["part_number"], name=en_name(frame), name_vi=vi_name(frame["description"]),
                    kind="MP", material="aluminium tube 6063-T6, 20 x 40 x 1.2 and 40 x 40 x 1.2",
                    finish="mill finish with the bond prep (D-79)",
                    process="saw cut square, CNC or jig drill (holes Ø0.4 from the spigot hole), member joints HOLD (H11)",
                    qty=1, unit="pc", size_mm=size_of(box_of(frame["bodies"])), mass_each_kg=fm, mass_total_kg=fm,
                    mass_status="calculation: CAD at 2700 kg/m3", status="DRAFT",
                    source="CAD; tube confirmed (D-34, D-54; 40 x 40 R-J3)", note="members butt-jointed, rails full length"))
    cut = Counter()
    for b in frame["bodies"]:
        dims = sorted(round(b["box"][i + 3] - b["box"][i], 1) for i in range(3))
        sec = "40 x 40 x 1.2" if dims[0] >= 39.9 else "20 x 40 x 1.2"   # the two short sides of the tube
        cut[(re.sub(r" \d+$", "", b["name"]), sec, member_length(b), b["mass_kg"])] += 1
    for (kind, sec, length, m), q in sorted(cut.items(), key=lambda k: (k[0][0], -k[0][2])):
        rows.append(row(level=2, name="%s (cut length)" % kind, name_vi="thanh nhôm", kind="cut",
                        material="aluminium tube 6063-T6 %s" % sec, qty=q, unit="pc", cut_length_mm=length, size_mm=sec,
                        mass_each_kg=round(m, 3), mass_total_kg=round(m * q, 3), mass_status="calculation: CAD",
                        status="DRAFT", source="CAD body length", note="square-cut ends; cut list of %s" % frame["part_number"]))
    sm = round(sum(b["mass_kg"] for b in skin["bodies"]), 3)
    rows.append(row(level=1, part_number=skin["part_number"], name=en_name(skin), name_vi=vi_name(skin["description"]),
                    kind="MP", material="ACP 3 mm Alcorest outdoor, PE-type core (HW-SEL A1)",
                    finish="PVDF coated EV3038 Dark Yellow (maker's coil coating; D-12)",
                    process="CNC router: cut, V-groove and fold the back return (H16)", qty=1, unit="pc",
                    size_mm=size_of(box_of(skin["bodies"])), mass_each_kg=sm, mass_total_kg=sm,
                    mass_status="calculation: CAD at 3.5 kg/m2 (HW-SEL A1); real kg/m2 HOLD (H16)", status="DRAFT",
                    source="CAD", note="blank and fold line in the skin DXF"))
    fl = round(sum(b["mass_kg"] for b in fill["bodies"]), 3)
    pieces = Counter((round(b["box"][4] - b["box"][1], 1), round(b["box"][5] - b["box"][2], 1)) for b in fill["bodies"])
    rows.append(row(level=1, part_number=fill["part_number"], name=en_name(fill), name_vi=vi_name(fill["description"]),
                    kind="MP", material="PET fill 40 mm, 24 kg/m3, Pyrotek Sorberpoly 2D (HW-SEL B)",
                    process="knife cut to the bays, 60 x 60 pockets left open at the bolts", qty=1, unit="set",
                    size_mm="; ".join("%d pieces %g x %g x 40" % (q, a, b) for (a, b), q in sorted(pieces.items())),
                    mass_each_kg=fl, mass_total_kg=fl, mass_status="calculation: CAD at the design's fill density",
                    status="DRAFT", source="CAD; 24 kg/m3 PM ruling 2026-10-31 (T02 confirms, else 32)",
                    note="friction fit in the bays"))
    # hardware fitted in this panel, counted from the CAD's holes
    rivnuts = len(holes_in(frame, 9.53))
    bolts = len(holes_in(frame, 7.0))
    spigot_rivnuts = 2 if "LOWER" in frame["name"] else 0
    top = [b for b in frame["bodies"] if b["name"] == "RAIL - TOP"][0]
    height = round(box_of(frame["bodies"])[5] - box_of(frame["bodies"])[2], 2)
    rows += [
        hw_row("108002", 1, "set", "one 12 x 3 joint on every member touching the skin; in-line tape HOLD-B2",
               source="%s; bond spec V2-ENG-BND (PR #23)" % REG),
        hw_row("838003", rivnuts, "pc", "%d stopped joints (J-WALL-01 or J-CEIL-01, and J-WALL-02) and %d spigot rivnuts" % (
            rivnuts - spigot_rivnuts, spigot_rivnuts)),
        hw_row("831002", rivnuts - spigot_rivnuts, "pc", "one under each stopped-joint rivnut's head; sets the 2.26 gap"),
    ]
    if spigot_rivnuts:
        rows.append(hw_row("831001", spigot_rivnuts, "pc", "in the top rail's spigot rivnuts, locating the panel above"))
    rows += [
        hw_row("838001", bolts, "pc", "captive, driven from this panel: J-BASE-01 or J-WALL-01 (bottom rail), J-FRONT-01"),
        hw_row("838004", bolts, "pc", "one under each bolt head (R-J10)"),
        hw_row("838005", bolts, "pc", "grommet in each Ø19 access hole, holding its bolt (HOLD-02)"),
        hw_row("848001", round((member_length(top) + height) / 1000.0, 2), "m",
               "on this panel's nut-side faces: the top member (%g) and the back stile's room face (%g)" % (
                   member_length(top), height)),
    ]
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
    name_en, name_vi = (root["description"].split(" | ") + ["", ""])[:2]
    perim = round(2 * ((tb["box"][4] - tb["box"][1]) + (tb["box"][5] - tb["box"][2])) / 1000.0, 2)
    rows.append(row(level=0, part_number=pn, name=name_en, name_vi=name_vi, kind="BS", material="see the parts below",
                    qty=1, unit="pc", size_mm=size_of(box_of([tb, fb])), mass_total_kg=round(made, 3),
                    mass_status="calculation: CAD bodies of the made parts", status="DRAFT",
                    source="CAD %s v%s" % (rep["document"], rep["version"]),
                    note="floating inner leaf; clips onto the panel frame from inside (D-17, D-47)"))
    rows.append(row(level=1, part_number=tray["part_number"], name=en_name(tray), name_vi=vi_name(tray["description"]),
                    kind="MP", material="galvanised steel sheet 0.5, EN 10346 DX51D+Z",
                    finish="hot-dip zinc (coating mass to confirm)", process="laser or punch blank, brake bend (sheet metal)",
                    qty=1, unit="pc", size_mm=size_of(tb["box"]), mass_each_kg=tb["mass_kg"], mass_total_kg=tb["mass_kg"],
                    mass_status="calculation: CAD at 7850 kg/m3", status="DRAFT",
                    source="CAD; 0.5 confirmed (D-37); lips PM ruling 2026-10-31",
                    note="34 mm returns turned in as 12 mm lips that hold the felt; flat blank in the DXF"))
    rows.append(row(level=1, part_number=felt["part_number"], name=en_name(felt), name_vi=vi_name(felt["description"]),
                    kind="MP", material="PET felt 9 mm Dark Gray, the factory's felt (D-31; plan VT03-PET)",
                    process="knife or die cut", qty=1, unit="pc", size_mm=size_of(fb["box"]),
                    mass_each_kg=fb["mass_kg"], mass_total_kg=fb["mass_kg"],
                    mass_status="calculation: CAD at 1.8 kg/m2 (Polyx Board 9 data, HW-SEL A3); the factory felt unverified",
                    status="DRAFT", source="CAD", note="held by the tray's lips over the 24 mm air gap (settles H09)"))
    rows += [
        hw_row("518001", len(clips["bodies"]), "pc", "zones reserved on the first and last intermediate stiles; "
               "8.3 kg rated in shear each (register J-LIN-01)"),
        hw_row("848011", 0.2, "m", "4 pads of 50 mm to line the cassette up (assumption); carries no load (D-47)"),
        hw_row("848012", perim, "m", "round the cassette's outer edge, sealing the 2.26 gap to the next cassette; "
               "converter HOLD (H14)"),
    ]
    return rows


def main(argv):
    panel, cass = load(argv[1]), load(argv[2])
    out = os.path.join(HERE, "%s_BOM.csv" % panel["document"].rsplit("_CAD", 1)[0])
    rows = panel_rows(panel) + cassette_rows(cass)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    top = [r for r in rows if r["level"] == 0]
    print("wrote %s: %d rows; made parts %s kg (panel) and %s kg (cassette)" % (
        os.path.basename(out), len(rows), top[0]["mass_total_kg"], top[1]["mass_total_kg"]))


if __name__ == "__main__":
    main(sys.argv)
