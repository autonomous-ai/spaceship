"""Finish BASE drawing PDFs: name strip, title data and notes as text, PNG.

    python3 v2/02-Drawings/base/finish_pdfs.py 111401 [110401 ...]

For each part number: takes the raw export from .raw/ (base_drawings.py),
removes the account holder's name under "Created by" with
tools/fusion/pdf_clear_field.py, writes the title data, notes and (for
assemblies) the parts list onto the sheet as PDF text, saves the repo copy
next to this file and renders a PNG to check by eye. Needs PyMuPDF.

The notes print with 2.5 mm capitals (ISO 3098). The band tubes 111101 to
111103 are drawn by the drawing generator (D-112, tools/drawgen), so they
are refused here: finishing them would overwrite the generator's sheet.

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

# drawn by the drawing generator (D-112): not finished here
GENERATOR = {"111101", "111102", "111103"}

DWG = {
    "111401":("111401_P01_BASE-FLOOR-PANEL-F1_DWG", "1:10", "A3"),
    "110000": ("110000_P01_BASE_DWG", "1:10", "A2"),
    "110101": ("110101_P01_BASE-BAND-ASSY-SIDE-LH_DWG", "1:5 (iso 1:10)", "A2"),
    "110103": ("110103_P01_BASE-BAND-ASSY-BACK_DWG", "1:5 (iso 1:10)", "A1"),
    "110401": ("110401_P01_BASE-FLOOR-PANEL-ASSY-F1_DWG", "1:10 (iso 1:20)", "A3"),
}
# No drawing (D-89): 111601 (part 4: DXF and parts-list row), 111501 (part 3: DXF and cut list).

TOL = {
    "tube": "General tolerances, PROPOSED until the shop confirms them: cut length +0/-0.5; hole positions "
            "±0.2 from datum C along the band and ±0.2 from datum B across it (joints register R-J6: "
            "Ø7.0 bolt holes on the wall side positioned ±0.2 from the spigot hole); rivnut holes Ø9.53 +0.10/0 "
            "(maker). Not ISO 2768 on the anodised faces.",
    "plate": "General tolerances, PROPOSED: outline ±0.5 (CNC); thickness as supplied (plywood ±0.3, "
             "foam ±0.3); not ISO 2768 on wood or foam (guideline §3.2).",
    "assembly": "Assembly: parts to their own drawings (the doubler 111601 to its DXF and parts-list row, the foam "
                "mat 111501 to its DXF, D-89); positions from skeleton P04 (110000_P01_BASE_CAD), hardware as the "
                "joints register (J-BASE-01, J-BASE-02).",
}

DATUMS = {
    "111601":"Part system: X across the band, Y along it, origin at the plate centre. Hole Ø13 3 mm off centre "
              "toward the pod side (gl_dx).",
    "111211": "Part system: X into the band from the end face (X 0), Y across the band (centred), Z up from the "
              "key's bottom. Datums: A = bottom face (sits on the band's bottom wall, pod Z 11.5), B = end face "
              "(flush with the band's end), C = the Y faces' centre plane. Block 25 x 35 x 75.",
    "111401": "Pod coordinates: X to the right wall, Y to the back. Outline from the band's inner faces less "
              "the 4 mm seal gap; seam half-lap 13 wide, 4.5 deep, on the +X edge. Top face up.",
    "110000": "Pod coordinates (conventions §4): origin on the room floor at the pod centre, +X right, +Y back, +Z up.",
    "110101": "Pod coordinates (conventions §4), as built: the side band LH, X -1250 to -1210, Y -670 to 847, "
              "on its glides. Factory-fitted: rivnuts with stop washers and spigots (J-BASE-01), glide doublers, "
              "glides preset (D-87), end cap. The keyholes take the back key's studs (J-BASE-02); the front end "
              "carries the front corner key 111212 (P02). GLIDES: level up from the highest floor spot; never below "
              "8.5 mm under the band (the keys' screw heads hang 3.3; the glide's base is the stop).",
    "110103": "Pod coordinates (conventions §4), as built: the back band, X -1210 to 1210, Y 810 to 850, on its "
              "glides. Factory-fitted: rivnuts, stop washers and spigots for B1 and B2 (J-BASE-01), glide doublers, "
              "glides preset (D-87), and a back corner key 111211 in each end with its 2 button head fixing screws "
              "and 2 hook studs (J-BASE-02). GLIDES: level up from the highest floor spot; never below 8.5 mm under "
              "the band (the keys' screw heads hang 3.3; the glide's base is the stop).",
    "110401": "Pod coordinates (conventions §4), as built: floor panel F1 with its 3 mm foam mat bonded underneath "
              "at the factory (D-87), the mat under the lap too; ply Z 3 to 12, floor top Z 12 (skeleton floor_top). "
              "Adhesive HOLD.",
}

HOLES = {
    "111601":"One hole Ø13 for the glide's M10 rivnut.",
    "111211": "Bottom: 2 x M6, 15 of full thread (tap drill Ø5.0 x 18), for the M6 x 12 button head fixing screws, "
              "10 from the back face and 7.5 either side of the centre line. End face: 2 x M6 tapped through, for "
              "the hook studs, 26 and 60 above the bottom (pod Z 37.5 and 71.5) on the centre line (joints register "
              "J-BASE-02; PM ruling on F-017).",
    "111401": "No holes.",
    "110000": "Holes on the part drawings.",
    "110101": "Holes on the part drawings (111101).",
    "110103": "Holes on the part drawings (111103, 111211).",
    "110401": "No holes.",
}


# sheets whose views reach the bottom left: their notes go on the right, above the title block
NOTES_RIGHT = {"111401", "110401"}


def kind_of(pn):
    if pn[2:4] == "00" or pn[2] == "0":             # xx0000 to xx0999: assemblies (conventions section 5)
        return "assembly"
    return {"111101": "tube", "111103": "tube"}.get(pn, "plate")


def text_block(pn):
    d = json.load(open(DATA, encoding="utf-8"))
    rec = d["parts"].get(pn, {})
    name = rec.get("name", "BASE") if pn != "110000" else "BASE (sample P01: back-left corner and F1)"
    is_asm = kind_of(pn) == "assembly"
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
    if is_asm:
        import csv
        lines.append("PARTS LIST (from 110000_P01_BASE_BOM.csv):")
        with open(BOM, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if pn == "110000" and r["level"] in ("1", "2"):
                    lines.append("  %s%s  %s  x %s %s" % ("  " if r["level"] == "2" else "", r["part_number"],
                                                         r["name"], r["qty_per_pod"], r["unit"]))
                elif pn != "110000" and r["parent"] == pn:
                    lines.append("  %s  %s  x %s %s" % (r["part_number"], r["name"], r["qty_per_parent"], r["unit"]))
    return lines


def finish(pn):
    if pn in GENERATOR:
        raise SystemExit("%s is drawn by the drawing generator (D-112); not finished here" % pn)
    dwg = DWG[pn][0]
    raw = os.path.join(HERE, ".raw", dwg + ".pdf")
    out = os.path.join(HERE, dwg + ".pdf")
    tmp = os.path.join(HERE, ".raw", dwg + "-clean.pdf")
    subprocess.run([sys.executable, CLEAR, raw, tmp], check=True)
    doc = fitz.open(tmp)
    page = doc[0]
    w, h = page.rect.width, page.rect.height
    lines = text_block(pn)
    mm = 72.0 / 25.4
    # letters at least 2.5 mm tall: ISO 3098 measures the capital height, about 0.72 of the font size in Arial,
    # so the font size is 3.5 mm (the old 5 to 6 pt printed 1.3 to 1.5 mm letters)
    fs = 3.5 * mm
    if pn in NOTES_RIGHT:     # the views fill the bottom left: right side, above the projection symbol and title block
        x0, x1, bottom = w * 0.56, w - 24 * mm, h - 75 * mm
    else:                     # bottom left, inside the frame (20 mm in on the left) and clear of the title block
        x0, x1, bottom = 22 * mm, w * 0.545, h - 14 * mm
    chars = max(40, int((x1 - x0) / (fs * 0.5)))       # Arial's average letter is about half the font size wide
    rows = sum(1 + len(line) // chars for line in lines)
    box = fitz.Rect(x0, bottom - (rows + 2) * fs * 1.45, x1, bottom)
    # a font with the Vietnamese letters
    font = next((f for f in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf")
                 if os.path.exists(f)), None)
    if font:
        rc = page.insert_textbox(box, "\n".join(lines), fontsize=fs, fontname="arialuni", fontfile=font, align=0)
    else:
        rc = page.insert_textbox(box, "\n".join(lines), fontsize=fs, fontname="helv", align=0)
    if rc < 0:                # PyMuPDF writes nothing when the text doesn't fit
        raise SystemExit("%s: the notes need %.1f mm more height than the box" % (pn, -rc / mm))
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
