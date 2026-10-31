"""Finish BASE drawing PDFs: name strip, title data and notes as text, PNG.

    python3 v2/02-Drawings/base/finish_pdfs.py 111101 [111103 ...]

For each part number: takes the raw export from .raw/ (base_drawings.py),
removes the account holder's name under "Created by" with
tools/fusion/pdf_clear_field.py, writes the title data, notes and (for
assemblies) the parts list onto the sheet as PDF text, saves the repo copy
next to this file and renders a PNG to check by eye. Needs PyMuPDF.

The drawing API can't place text on a sheet in this build, so this text is
added to the PDF, not to the native drawing; it comes from the same sources
as the parts list (v2/03-Manufacturing/base/make_outputs.py PART_INFO) and
the CAD's exported facts (110000_P01_BASE_DATA.json).
"""

import importlib.util
import json
import os
import subprocess
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAKE = os.path.join(REPO, "v2/03-Manufacturing/base/make_outputs.py")
DATA = os.path.join(REPO, "v2/03-Manufacturing/base/110000_P01_BASE_DATA.json")
BOM = os.path.join(REPO, "v2/03-Manufacturing/base/110000_P01_BASE_BOM.csv")
CLEAR = os.path.join(REPO, "tools/fusion/pdf_clear_field.py")

spec = importlib.util.spec_from_file_location("make_outputs", MAKE)
mo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mo)

DWG = {
    "111101": ("111101_P01_BASE-BAND-TUBE-SIDE-LH_DWG", "1:5 (view from the left 1:2)", "A2"),
    "111103": ("111103_P01_BASE-BAND-TUBE-BACK_DWG", "1:5 (view from the left 1:2)", "A1"),
    "111601": ("111601_P01_BASE-GLIDE-DOUBLER-COMMON_DWG", "2:1", "A4"),
    "111401": ("111401_P01_BASE-FLOOR-PANEL-F1_DWG", "1:10 (edge 1:1)", "A3"),
    "111501": ("111501_P01_BASE-SEAL-MAT-F1_DWG", "1:10", "A3"),
    "110000": ("110000_P01_BASE_DWG", "1:10", "A2"),
}

TOL = {
    "tube": "General tolerances, PROPOSED until the shop confirms them: cut length +0/-0.5; hole positions "
            "±0.2 from datum C along the band and ±0.2 from datum B across it (joints register R-J6: "
            "Ø7.0 bolt holes on the wall side positioned ±0.2 from the spigot hole); rivnut holes Ø9.53 +0.10/0 "
            "(maker). Not ISO 2768 on the anodised faces.",
    "plate": "General tolerances, PROPOSED: outline ±0.5 (CNC); thickness as supplied (plywood ±0.3, "
             "foam ±0.3); not ISO 2768 on wood or foam (guideline §3.2).",
    "assembly": "Assembly: parts to their own drawings; positions from skeleton P04 (110000_P01_BASE_CAD).",
}

DATUMS = {
    "111101": "Part system CS-111101: X along the band from its back end, Y from the outer face inward, Z from the "
              "bottom face up. In the pod: X(part) = 847 - Y(pod), Y(part) = X(pod) + 1250, Z(part) = Z(pod) - 10. "
              "Datums: A = top face (the walls stand on it), B = outer face, C = back end face. Origin O = C x B "
              "at the bottom. 2D: front view X-2D = X, Y-2D = Z; view from above X-2D = X, Y-2D = Y.",
    "111103": "Part in pod coordinates (conventions §4): X along the band, Y toward the back face, Z up. Datums: "
              "A = top face, B = outer (back) face Y = 850, C = left end face X = -1210. Origin O = C x inner face "
              "for the hole table; dimensions from C.",
    "111601": "Part system: X across the band, Y along it, origin at the plate centre. Hole Ø13 3 mm off centre "
              "toward the pod side (gl_dx).",
    "111401": "Pod coordinates: X to the right wall, Y to the back. Outline from the band's inner faces less "
              "the 4 mm seal gap; seam half-lap 13 wide, 4.5 deep, on the +X edge. Top face up.",
    "111501": "Pod coordinates, as F1; bonded under F1 at the factory (D-87).",
    "110000": "Pod coordinates (conventions §4): origin on the room floor at the pod centre, +X right, +Y back, +Z up.",
}

HOLES = {
    "111101": "Top wall: rivnut holes Ø9.53 for J-BASE-01 (4 bolts with stop washers, 2 spigots) at Y 26 "
              "(wall tube centre line); glide key holes Ø10. Bottom wall: glide nut holes Ø13. "
              "Positions: the hole table and the dimensions from datum C.",
    "111103": "As 111101, for B1 and B2 (frame-end rule, 220 / 100 mm), glides at 150 from each end and the middle.",
    "111601": "One hole Ø13 for the glide's M10 rivnut.",
    "111401": "No holes.",
    "111501": "No holes.",
    "110000": "Holes on the part drawings.",
}


def kind_of(pn):
    return {"111101": "tube", "111103": "tube", "110000": "assembly"}.get(pn, "plate")


def text_block(pn):
    d = json.load(open(DATA, encoding="utf-8"))
    rec = d["parts"].get(pn, {})
    name = rec.get("name", "BASE") if pn != "110000" else "BASE (sample P01: back-left corner and F1)"
    vn = rec.get("name_vi", "Đế / sàn")
    mat, fin, proc, ms, st, src, note = mo.PART_INFO.get(pn, ("", "", "", "", "DRAFT", "", ""))
    mass = rec.get("mass_kg")
    dwg, scale, size = DWG[pn]
    lines = [
        "%s  %s  /  %s" % (pn, name, vn),
        "Drawing %s   Rev P01   Status DRAFT (not for production)   Sheet 1/1, %s   Scale %s" % (dwg, size, scale),
        "UNITS: mm.  Projection: ISO first angle (ISO 5456-2), symbol at right.  Do not scale.",
        "Material: %s" % (mat or "see the parts list"),
        "Finish: %s" % (fin or "none"),
        "Process: %s" % (proc or "-"),
        "Mass: %s" % (("%.3f kg (calculation from CAD)" % mass) if mass else "see the parts list"),
        "Tolerances: %s" % TOL[kind_of(pn)],
        "Datums and axes: %s" % DATUMS[pn],
        "Holes: %s" % HOLES[pn],
        "Sources: CAD 110000_P01_BASE_CAD and the part's own design; feature reasons in "
        "v2/02-Drawings/base/FEATURE-RATIONALE.md; status of every number in base_build.py.",
        "Made by the BASE Engineer (AI agent), v2/02-Drawings/base/base_drawings.py, 2026-11-01.",
    ]
    if pn == "110000":
        import csv
        lines.append("PARTS LIST (from 110000_P01_BASE_BOM.csv):")
        with open(BOM, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["level"] in ("1", "2"):
                    lines.append("  %s%s  %s  x %s %s" % ("  " if r["level"] == "2" else "", r["part_number"],
                                                         r["name"], r["qty_per_pod"], r["unit"]))
    return lines


def finish(pn):
    dwg = DWG[pn][0]
    raw = os.path.join(HERE, ".raw", dwg + ".pdf")
    out = os.path.join(HERE, dwg + ".pdf")
    tmp = os.path.join(HERE, ".raw", dwg + "-clean.pdf")
    subprocess.run([sys.executable, CLEAR, raw, tmp], check=True)
    doc = fitz.open(tmp)
    page = doc[0]
    w, h = page.rect.width, page.rect.height
    lines = text_block(pn)
    fs = 6.0 if w > 1000 else 5.0
    bh = (len(lines) + 2) * fs * 1.6
    box = fitz.Rect(20, h - 20 - bh, w * 0.62, h - 20)      # bottom left, clear of the views and tables
    page.insert_textbox(box, "\n".join(lines), fontsize=fs, fontname="helv", align=0)
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    os.remove(tmp)
    png = os.path.join(HERE, dwg.replace("_DWG", "_IMG") + ".png")
    d2 = fitz.open(out)
    d2[0].get_pixmap(dpi=110).save(png)
    text = d2[0].get_text()
    d2.close()
    missing = [k for k in ("mm", "first angle", "Material", "Finish", "Tolerances") if k not in text]
    print("%s: %s, %s%s" % (pn, os.path.relpath(out, REPO), os.path.relpath(png, REPO),
                            ("; MISSING TEXT %s" % missing) if missing else "; text check OK"))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        finish(arg)
