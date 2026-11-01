"""Drawing index for WALL (PM ruling D-89): which drawing covers which part numbers.

    python3 v2/02-Drawings/wall/make_drawing_index.py

D-89: each position's panel assembly, frame and cassette assembly has its own drawing; identical or
mirrored skins and trays share one tabulated drawing listing every part number it covers; the felts, plain
knife-cut rectangles, have no drawing: their parts-list rows give size, material, tolerance and part number.
D-128: the felts with ELECTRICAL's openings and every fill piece (their notches go right through the batt) are
cut from their DXFs, with material, density, thickness, tolerance and part number in their rows: no drawing. Writes DRAWING-INDEX.csv (drawing, part numbers covered, status) and
DRAWING-INDEX.md next to this script. A drawing's status is "done" once its PDF is in this folder.
"""

import csv
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIDE = (("L1", "LOWER-LH"), ("R1", "LOWER-RH"), ("L2", "UPPER-LH"), ("R2", "UPPER-RH"))
BACK = (("B1", "LOWER-B1"), ("B2", "LOWER-B2"), ("B3", "UPPER-B3"), ("B4", "UPPER-B4"))


def fill_forms():
    """(part number, DXF) of each fill-piece form with a number, from WALL's FILL-PIECES.csv (D-123, D-128)."""
    with open(os.path.join(HERE, "..", "..", "03-Manufacturing", "wall", "FILL-PIECES.csv"), encoding="utf-8") as fh:
        return sorted({(r["number"], r["dxf"]) for r in csv.DictReader(fh) if r["number"]})


def rows():
    fusion_assy, gen = ("the drawing generator's assembly mode (D-158)",
                        "the drawing generator, from the STEP (D-139)")
    out = [("210000_P01_WALL_DWG", ["210000"], "WALL assembly: the 8 panels and 8 cassettes (wall_assembly.py); %s"
            % fusion_assy)]
    for i, (code, tag) in enumerate(SIDE, 1):
        out += [("2101%02d_P01_WALL-PANEL-ASSY-SIDE-%s_DWG" % (i, tag), ["2101%02d" % i],
                 "panel assembly %s; %s" % (code, fusion_assy)),
                ("2111%02d_P01_WALL-PANEL-FRAME-SIDE-%s_DWG" % (i, tag), ["2111%02d" % i],
                 "frame %s, welded steel with its members (D-131); %s" % (code, gen)),
                ("5101%02d_P01_LINING-CASSETTE-SIDE-%s_DWG" % (i, tag), ["5101%02d" % i],
                 "cassette %s; %s" % (code, fusion_assy))]
    for i, (code, tag) in enumerate(BACK, 1):
        out += [("2102%02d_P01_WALL-PANEL-ASSY-BACK-%s_DWG" % (i, tag), ["2102%02d" % i],
                 "panel assembly %s; %s" % (code, fusion_assy)),
                ("2112%02d_P01_WALL-PANEL-FRAME-BACK-%s_DWG" % (i, tag), ["2112%02d" % i],
                 "frame %s, welded steel with its members (D-131); %s" % (code, gen)),
                ("5102%02d_P01_LINING-CASSETTE-BACK-%s_DWG" % (i, tag), ["5102%02d" % i],
                 "cassette %s; %s" % (code, fusion_assy))]
    # one generator sheet per part (D-139): the side skins V-grooved and folded (#341), the trays and the ledges bent
    # sheet (#335; the ledges' countersinks, #371)
    for i, (code, tag) in enumerate(SIDE, 1):
        out += [("2113%02d_P01_WALL-SKIN-SIDE-%s_DWG" % (i, tag), ["2113%02d" % i],
                 "side skin %s, V-grooved and folded at its 2 mm outside radius (D-161); %s" % (code, gen)),
                ("5111%02d_P01_LINING-TRAY-SIDE-%s_DWG" % (i, tag), ["5111%02d" % i],
                 "side tray %s, bent sheet; %s" % (code, gen))]
    for i, (code, tag) in enumerate(BACK, 1):
        out += [("5112%02d_P01_LINING-TRAY-BACK-%s_DWG" % (i, tag), ["5112%02d" % i],
                 "back tray %s, bent sheet; %s" % (code, gen))]
    out += [("211701_P01_WALL-CASSETTE-LEDGE-SIDE-LOWER-COMMON_DWG", ["211701"],
             "the side cassette ledge (L1 and R1), a bent 1.5 angle with its rivets' countersinks (the Lead's rulings "
             "of 2026-11-01); %s" % gen),
            ("211801_P01_WALL-CASSETTE-LEDGE-BACK-LOWER_DWG", ["211801"],
             "the back cassette ledge (B1 and B2), with B1's rebuild; %s" % gen),
            ("(on the frame drawings' cut lists, D-162)", ["212101", "212102", "212103", "212104", "212105"],
             "L1's frame members: each member's row in its frame drawing's cut list is its drawing (D-162; "
             "210000_P01_WALL-TUBE-CUT-LIST_BOM.csv); the other frames' members join as their frames are rebuilt")]
    forms = fill_forms()
    out.append(("(no drawing, D-128)", [pn for pn, _dxf in forms],
                "fill pieces: 40 mm PET batt, each of the %d forms knife cut from its own DXF, the full outline with every "
                "notch (the 60 x 60 notches beside the bolts go right through the batt; B2's piece also has "
                "ELECTRICAL's cut-outs), with material, density, thickness, tolerance and part number in its parts-list "
                "row; the pieces go straight into the panel assemblies, whose drawings show each in place "
                "(FILL-PIECES.md); the panels' own fill numbers 211501-211504 and 211601-211604 are cancelled (D-123)"
                % len(forms)))
    out.append(("(no drawing, D-89 part 4)", ["211401", "211402", "211403", "211404"],
                "back skins: flat ACP cut by CNC router from their DXFs (outline and holes, B2's inlet and LAN "
                "holes included); material, thickness, finish and ISO 2768-m in the parts-list rows"))
    for code_list, fam, what, el in ((range(1, 5), "5113", "side felt", "511302 (R1) and 511304 (R2)"),
                                     (range(1, 5), "5114", "back felt", "511402 (B2) and 511404 (B4)")):
        out.append(("(no drawing, D-89)", ["%s%02d" % (fam, i) for i in code_list],
                    "%s: knife-cut pieces; size, material, tolerance and part number in the parts list; %s carry "
                    "ELECTRICAL's openings and are cut from their DXFs, outline and every opening, with material, grade, thickness, "
                    "tolerance and part number in their rows: no drawing (D-128)" % (what, el)))
    return out


# WALL's cloud documents in Default Project / FocusPod v2 renamed NAME_SUPERSEDED-<date> by rename_superseded.py
# (D-141: never deleted), so nobody opens one by its old name: (old name, date, why)
_D158 = "D-158: the drawing generator draws every sheet now (the Lead's word, 2026-11-01)"
SUPERSEDED = [
    ("211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_CAD", "2026-11-01", "D-123 cancels the panels' fill set numbers"),
    ("211601_P01_WALL-CAVITY-FILL-BACK-LOWER-B1_CAD", "2026-11-01", "D-123 cancels the panels' fill set numbers"),
    ("211301_P01_WALL-SKIN-SIDE-LOWER-LH_DWG", "2026-11-01", _D158 + "; its sheet is the generator's in this folder"),
    ("210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_DWG", "2026-11-01", _D158 + "; it showed the aluminium frame"),
    ("210102_P01_WALL-PANEL-ASSY-SIDE-LOWER-RH_DWG", "2026-11-01", _D158 + "; it showed the aluminium frame"),
    ("211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_DWG", "2026-11-01", _D158 + "; it showed the aluminium frame (the GUI "
                                                                    "copy someone else made is left as it is)"),
    ("211102_P01_WALL-PANEL-FRAME-SIDE-LOWER-RH_DWG", "2026-11-01", _D158 + "; it showed the aluminium frame"),
    ("510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_DWG", "2026-11-01", _D158 + "; the assembly mode draws the cassette"),
    ("511101_P01_LINING-TRAY-SIDE-LOWER-LH_DWG", "2026-11-01", _D158 + "; its sheet is the generator's in this folder"),
    ("211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_DWG", "2026-11-01", "D-123 cancels the fill set; D-128 cuts the pieces "
                                                                   "from their DXFs"),
]


def main():
    done = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(HERE, "*_DWG.pdf"))}
    table = [(d, " ".join(pns), "done" if d in done else ("cut list" if d.startswith("(") else "to do"), note)
             for d, pns, note in rows()]
    with open(os.path.join(HERE, "DRAWING-INDEX.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["drawing", "covers", "status", "note"])
        w.writerows(table)
    md = ["# WALL drawing index (D-89)", "",
          "Generated by `make_drawing_index.py`. Each position's panel assembly, frame and cassette assembly has its "
          "own drawing; identical or mirrored skins and trays share one tabulated drawing; the plain felts are "
          "defined by their parts-list rows (size, material, tolerance, part number); the fill pieces and the felts "
          "with ELECTRICAL's openings are cut from their DXFs, with full rows (D-128).", "",
          "| Drawing | Covers | Status | Note |", "|---|---|---|---|"]
    md += ["| %s | %s | %s | %s |" % r for r in table]
    md += ["", "## Superseded cloud documents (D-141)", "",
           "WALL's own Fusion documents in Default Project / FocusPod v2 that are no longer current, renamed "
           "NAME_SUPERSEDED-<date> by `v2/01-CAD-Native/wall/rename_superseded.py`, never deleted, so nobody opens one "
           "by its old name.", "", "| Document | Renamed to | Why |", "|---|---|---|"]
    md += ["| %s | %s_SUPERSEDED-%s | %s |" % (n, n, d, why) for n, d, why in SUPERSEDED]
    with open(os.path.join(HERE, "DRAWING-INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("wrote DRAWING-INDEX.csv and .md: %d drawings (%d done), %d cut-list families" % (
        sum(1 for r in table if not r[0].startswith("(")), sum(1 for r in table if r[2] == "done"),
        sum(1 for r in table if r[0].startswith("("))))


if __name__ == "__main__":
    main()
