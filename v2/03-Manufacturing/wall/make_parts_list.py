"""Parts list (BOM CSV, with the tube cut list) for a WALL panel position, from the CAD reports.

    python3 v2/03-Manufacturing/wall/make_parts_list.py 210101 510101

Reads out/<pn>.json (written in Fusion by v2/01-CAD-Native/wall/report_wall_doc.py) for the panel
assembly and its cassette, and writes <panel pn>_P01_<NAME>_BOM.csv next to this script. Made parts,
masses, member lengths and fill pieces come from the CAD; bought items, hardware counts and statuses
come from the tables below, each with its source. Hardware has no part number yet: the joints
register owns that list (PM ruling, 2026-10-31), so the column says so instead of inventing one.
"""

import csv
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "P01"
FIELDS = ["level", "part_number", "name_en", "name_vi", "class", "material", "qty", "unit", "cut_length_mm",
          "size_mm", "mass_each_kg", "mass_total_kg", "status", "source", "notes"]
CLASS = {"21": "MP", "51": "MP"}       # made parts; assemblies set below
REG = "joints register V2-ENG-JNT-01 P01 (PR #23)"
NO_PN = "not yet numbered: the joints register owns the hardware list (PM ruling 2026-10-31)"


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


def size_of(box):
    return "%g x %g x %g" % tuple(round(box[i + 3] - box[i], 2) for i in range(3))


def member_length(body):
    b = body["box"]
    return round(max(b[i + 3] - b[i] for i in range(3)), 2)


def panel_rows(rep):
    rows = []
    root = [c for c in rep["components"] if c["is_root"]][0]
    comps = {c["part_number"]: c for c in rep["components"] if not c["is_root"]}
    mass = sum(b["mass_kg"] for c in comps.values() for b in c["bodies"])
    pn = rep["document"].split("_")[0]
    name = re.sub(r"-", " ", rep["document"].split("_")[2]).replace("ASSY SIDE", "ASSY - SIDE")
    frame = [c for p, c in comps.items() if p.startswith("2111")][0]
    skin = [c for p, c in comps.items() if p.startswith("2113")][0]
    fill = [c for p, c in comps.items() if p.startswith("2115")][0]
    rivnuts = len(holes_in(frame, 9.53))
    bolts_driven = len(holes_in(frame, 7.0))          # this panel is the bolt side at each 7.0 hole (F-009)
    seam_rivnuts = rivnuts - 2                        # 2 hold the seam spigots (FR-04)
    rows.append([0, pn, "WALL - PANEL ASSY - SIDE LOWER - LH" if pn == "210101" else name, vi_name(root["description"]),
                 "BS", "see parts below", 1, "pc", "", size_of([min(b["box"][i] for c in comps.values() for b in c["bodies"])
                                                                for i in range(3)] +
                                                               [max(b["box"][i + 3] for c in comps.values() for b in c["bodies"])
                                                                for i in range(3)]),
                 "", round(mass, 3), "calculation", "CAD %s v%s (made parts only; add the bond and hardware rows)" % (
                     rep["document"], rep["version"]), "outer panel; the lining cassette is a separate part (D-17)"])
    fm = round(sum(b["mass_kg"] for b in frame["bodies"]), 3)
    rows.append([1, frame["part_number"], en_name(frame), vi_name(frame["description"]), "MP",
                 "aluminium tube 20 x 40 x 1.2 and 40 x 40 x 1.2; alloy, temper and finish HOLD (ISS-034, H15)", 1, "pc",
                 "", size_of([min(b["box"][i] for b in frame["bodies"]) for i in range(3)] +
                             [max(b["box"][i + 3] for b in frame["bodies"]) for i in range(3)]), fm, fm, "calculation",
                 "CAD body masses at 2700 kg/m3", "member joints HOLD (H11): butt joints modelled, rails full length"])
    cut = Counter()
    for b in frame["bodies"]:
        sec = "40 x 40 x 1.2" if "BACK" in b["name"] else "20 x 40 x 1.2"
        kind = re.sub(r" \d+$", "", b["name"])
        cut[(kind, sec, member_length(b), b["mass_kg"])] += 1
    for (kind, sec, length, m), q in sorted(cut.items(), key=lambda k: (k[0][0], -k[0][2])):
        rows.append([2, "", "%s (cut length)" % kind, "thanh nhôm", "cut", "aluminium tube %s" % sec, q, "pc",
                     length, sec, round(m, 3), round(m * q, 3), "calculation",
                     "CAD body length; tube size confirmed (D-34, D-54; 40 x 40 PM ruling R-J3)",
                     "square-cut butt ends; joint method HOLD (H11)"])
    sm = round(sum(b["mass_kg"] for b in skin["bodies"]), 3)
    sb = skin["bodies"][0]
    rows.append([1, skin["part_number"], en_name(skin), vi_name(skin["description"]), "MP",
                 "ACP 3 mm Alcorest outdoor EV3038 Dark Yellow, PE-type core (HW-SEL A1; D-12)", 1, "pc", "",
                 size_of(sb["box"]), sm, sm, "calculation",
                 "CAD body at 3.5 kg/m2 (HW-SEL A1 calculation); real kg/m2 HOLD (H16)",
                 "with a 40 mm back return, V-grooved and folded (D-55); blank in the DXF"])
    fl = round(sum(b["mass_kg"] for b in fill["bodies"]), 3)
    pieces = Counter((round(b["box"][4] - b["box"][1], 1), round(b["box"][5] - b["box"][2], 1),
                      round(b["box"][3] - b["box"][0], 1)) for b in fill["bodies"])
    rows.append([1, fill["part_number"], en_name(fill), vi_name(fill["description"]), "MP",
                 "PET fill 40 mm, 32 kg/m3, Pyrotek Sorberpoly 2D (D-54; HW-SEL B)", len(fill["bodies"]), "pc", "",
                 "; ".join("%d x (%g x %g x %g)" % (q, *k) for k, q in sorted(pieces.items())), "", fl, "calculation",
                 "CAD bodies at 32 kg/m3 (D-54), pockets cut",
                 "one piece per bay, friction fit; 60 x 60 pocket left out beside each bolt this panel drives (FR-10)"])
    # bought items and hardware (counts from the CAD's holes; data from the sources named)
    bead_m = round(sum(member_length(b) for b in frame["bodies"]) / 1000.0, 2)
    rows += [
        [1, "", "BOND - SIKATACK PANEL-50 WITH PANEL FIXING TAPE, 12 x 3 JOINT", "keo dán", "PI",
         "SikaTack Panel-50 (ETA 19/0511) + Aktivator-205 + Panel Primer", bead_m, "m of bead", "", "12 x 3 joint", "",
         0.49, "source (system); calculation (length, mass)", "bond spec V2-ENG-BND (PR #23) section 2",
         "bead on every member touching the skin; in-line tape HOLD-B2; 72 h before handling"],
        [1, "", "RIVNUT - M6 - SHEREX CAH3-610-4.2", "tán rút M6", "PI", "aluminium 5056", rivnuts, "pc", "",
         "hole 9.53 +0.10", "", "", "source", "%s H-03; HW-SEL A5" % REG,
         "%d seam (top rail, J-WALL-01), 2 spigot (FR-04), the rest corner (back stile, J-WALL-02); PN: %s" % (
             len([h for h in holes_in(frame, 9.53) if h["axis"] == "z"]) - 2, NO_PN)],
        [1, "", "STOP WASHER - AL - D10.5 x D20 x 1.5 (H-08)", "long đen chặn", "MP", "aluminium sheet 1.5", seam_rivnuts,
         "pc", "", "10.5 x 20 x 1.5", "", "", "assumption (PROPOSED part)", "%s H-08" % REG,
         "under each site-joint rivnut head; sets the 2.26 seam gap; PN: %s" % NO_PN],
        [1, "", "LOCATING SPIGOT - D8 x M6 (H-05)", "chốt định vị", "MP", "stainless", 2, "pc", "", "8 proud", "", "",
         "assumption (PROPOSED part)", "%s H-05, FR-04" % REG, "in the top rail's spigot rivnuts, for L2; PN: %s" % NO_PN],
        [1, "", "CAPTIVE BOLT - M6 x 16 - ISO 4762 - 8.8 - ZINC", "bu lông lục giác chìm M6 x 16", "PI", "steel 8.8 zinc",
         bolts_driven, "pc", "", "M6 x 16", "", "", "source (standard); confirmed (head type R-J2)", "%s H-01" % REG,
         "driven from this panel into the base band (4) and the decor block (3); PN: %s" % NO_PN],
        [1, "", "CAPTIVE RETAINER FOR THE M6 BOLT (H-02)", "vòng giữ bu lông", "PI", "HOLD", bolts_driven, "pc", "", "",
         "", "", "HOLD (HOLD-02)", "%s H-02" % REG, "part not chosen"],
        [1, "", "GASKET - PORON 4701-40 SOFT 3.18 x 10 WITH PSA", "gioăng", "PI", "PORON 4701-40 Soft",
         round((member_length([b for b in frame["bodies"] if b["name"] == "RAIL - TOP"][0]) +
                (sb["box"][5] - sb["box"][2])) / 1000.0, 2), "m", "", "10 x 3.18", "", "", "source (product); HOLD (converter, HOLD-05)",
         "%s H-04, FR-11; HW-SEL D" % REG, "on this panel's nut-side faces: top rail (L1-L2 seam) and back stile (corner); D22 holes at the rivnuts"],
    ]
    return rows


def cassette_rows(rep):
    rows = []
    root = [c for c in rep["components"] if c["is_root"]][0]
    comps = {c["part_number"]: c for c in rep["components"] if not c["is_root"]}
    real = {p: c for p, c in comps.items() if not p.startswith("NO-PN")}
    mass = sum(b["mass_kg"] for c in real.values() for b in c["bodies"])
    pn = rep["document"].split("_")[0]
    tray = [c for p, c in real.items() if p.startswith("5111")][0]
    felt = [c for p, c in real.items() if p.startswith("5113")][0]
    clips = [c for p, c in comps.items() if p.startswith("NO-PN")][0]
    tb, fb = tray["bodies"][0], felt["bodies"][0]
    perim = round(2 * ((tb["box"][4] - tb["box"][1]) + (tb["box"][5] - tb["box"][2])) / 1000.0, 2)
    rows.append([0, pn, "LINING - CASSETTE - SIDE LOWER - LH", vi_name(root["description"]), "BS", "see parts below", 1,
                 "pc", "", size_of([min(tb["box"][i], fb["box"][i]) for i in range(3)] +
                                   [max(tb["box"][i + 3], fb["box"][i + 3]) for i in range(3)]), "", round(mass, 3),
                 "calculation", "CAD %s v%s (tray and felt; add clips and fixings)" % (rep["document"], rep["version"]),
                 "floating inner leaf, clips onto the panel frame from inside (D-17, D-47)"])
    rows.append([1, tray["part_number"], en_name(tray), vi_name(tray["description"]), "MP",
                 "galvanised steel sheet 0.5, EN 10346 DX51D+Z (coating mass to confirm)", 1, "pc", "", size_of(tb["box"]),
                 tb["mass_kg"], tb["mass_kg"], "calculation", "CAD body at 7850 kg/m3; 0.5 confirmed (D-37)",
                 "34 mm returns turned in as 12 mm lips that hold the felt (PM ruling 2026-10-31, option 1); "
                 "sheet metal, flat blank in the DXF"])
    rows.append([1, felt["part_number"], en_name(felt), vi_name(felt["description"]), "MP",
                 "PET felt 9 mm Dark Gray, the factory's felt (D-31; plan VT03-PET)", 1, "pc", "", size_of(fb["box"]),
                 fb["mass_kg"], fb["mass_kg"], "calculation; unverified (felt data)",
                 "CAD body at 200 kg/m3 (1.8 kg/m2, Polyx Board 9 data, HW-SEL A3)",
                 "inside the tray, held by its lips over the 24 mm air gap (settles H09 for the walls)"])
    rows += [
        [1, "", "CASSETTE CLIP, CAPTIVE, RATED (HOLD)", "kẹp treo cassette", "PI", "HOLD", len(clips["bodies"]), "pc", "",
         "zones reserved in the CAD", "", "", "HOLD (H03, HOLD-08)", "D-47; HW-SEL A8; %s J-LIN-01" % REG,
         "7.7 kg rated in shear each (HW-SEL A8 calculation); candidate Häfele KEKU EH, unrated"],
        [1, "", "HOOK-AND-LOOP, LOCATING ONLY", "miếng dán Velcro", "PI", "VELCRO PS14 hook 25 mm or 3M Dual Lock SJ3560",
         "", "m", "", "25 wide", "", "", "source (products); quantity not designed", "HW-SEL A8; D-47",
         "lines the cassette up; carries no load"],
        [1, "", "GASKET - PORON 4701-40 SOFT 3.18 WITH PSA, CASSETTE EDGE", "gioăng mép cassette", "PI",
         "PORON 4701-40 Soft", perim, "m", "", "10-20 wide x 3.18", "", "", "source (product); HOLD (converter, H14)",
         "HW-SEL D; sample package P14", "round the cassette's outer edge"],
    ]
    return rows


def main(argv):
    panel_pn, cass_pn = argv[1], argv[2]
    panel, cass = load(panel_pn), load(cass_pn)
    name = panel["document"].rsplit("_CAD", 1)[0]
    out = os.path.join(HERE, "%s_BOM.csv" % name)
    rows = panel_rows(panel) + cassette_rows(cass)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        for r in rows:
            w.writerow(r)
    print("wrote %s: %d rows; panel made parts %.3f kg, cassette tray + felt %.3f kg" % (
        os.path.relpath(out, os.path.join(HERE, "..", "..", "..")), len(rows), rows[0][11],
        [r for r in rows if r[0] == 0][1][11]))


if __name__ == "__main__":
    main(sys.argv)
