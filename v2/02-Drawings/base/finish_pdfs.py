"""Finish BASE drawing PDFs: name strip, title data and notes as text, PNG.

    python3 v2/02-Drawings/base/finish_pdfs.py 111106 [111301 ...]

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
    "110000": ("110000_P01_BASE_DWG", "1:10", "A2"),
    "110101": ("110101_P01_BASE-BAND-ASSY-SIDE-LH_DWG", "1:5 (iso 1:10)", "A2"),
    "110103": ("110103_P01_BASE-BAND-ASSY-BACK_DWG", "1:5 (iso 1:10)", "A1"),
    "110102": ("110102_P01_BASE-BAND-ASSY-SIDE-RH_DWG", "1:5 (iso 1:10)", "A2"),
    "110104": ("110104_P01_BASE-BAND-ASSY-FRONT-LH_DWG", "1:1 (iso 1:2)", "A3"),
    "110106": ("110106_P01_BASE-BAND-ASSY-FRONT-FIXED-GLASS_DWG", "1:2 (iso 1:4)", "A2"),
    "111106": ("111106_P01_BASE-BAND-TUBE-FRONT-FIXED-GLASS_DWG", "1:5 (end view 1:2)", "A3"),
    "111301": ("111301_P01_BASE-SILL-FIXED-GLASS_DWG", "1:5 (section 1:1)", "A3"),
    # Fusion sheets the generator can't draw yet (D-139; the Lead's ruling of 2026-11-01; DRAWING-RECORD.md)
    "111104": ("111104_P01_BASE-BAND-TUBE-FRONT-FACET-1-LH_DWG", "1:1 (iso 1:2)", "A3"),
    "111105": ("111105_P01_BASE-BAND-TUBE-FRONT-FACET-2-LH_DWG", "1:2 (iso 1:4)", "A3"),
    "111602": ("111602_P01_BASE-LEVELLING-GLIDE-M10-D40_DWG", "2:1", "A3"),
}
# No drawing (D-89): 111601 (part 4: DXF and parts-list row). No floor (D-132).

TOL = {
    "tube": "General tolerances, PROPOSED until the shop confirms them: cut length +0/-0.5; hole positions "
            "±0.2 from datum C along the band and ±0.2 from datum B across it (joints register R-J6: "
            "Ø7.0 bolt holes on the wall side positioned ±0.2 from the spigot hole); rivnut holes Ø10.00 +0.10/0 "
            "and the glide's rivnut hole Ø13.50 +0.15/0 (D-163). Not ISO 2768 on the anodised faces.",
    "plate": "General tolerances, PROPOSED: outline ±0.5 (CNC); thickness as supplied (guideline §3.2).",
    "turned": "General tolerances ISO 2768-m. Thread M10 x 1.5-6g (ISO 965-1) along the stem (assumption). Base height "
              "7.61 ±0.05 (D-164's 7.6): with the M10 rivnut's head (0.81 to 0.97) it sets the band's lowest setting, 8.5 "
              "(PM ruling on F-018). Hex socket 5 across flats, +0.02/+0.14, to fit a 5 mm hex key (as ISO 4762's s 5; "
              "assumption). Static rating 3.5 kN or more, proved by BT-04 (D-164).",
    "sheet": "General tolerances ISO 2768-m (linear) on the flat pattern; bends 90 deg +-0.5 deg, inside radius = t "
             "(assumption until the bender confirms); leg lengths +-0.3 to the outside of the bends; rivnut holes "
             "Ø5.0 +0.1/0 (HOLD with the rivnut).",
    "assembly": "Assembly: parts to their own drawings (the doubler 111601 to its DXF and parts-list row, D-89); "
                "positions from skeleton P04 (110000_P01_BASE_CAD), hardware as the joints register (J-BASE-01, "
                "J-BASE-02). The lip seal 118001 is bonded along each band's inner face at the factory (D-132).",
}

DATUMS = {
    "111601": "Part system: X across the band, Y along it, origin at the plate centre. Hole Ø13 3 mm off centre "
              "toward the pod side (gl_dx).",
    "111104": "Part system CS-111104: X along FL1's outer face from its corner end (the long point of the 24.14 deg "
              "mitre, on DL's outer facet), Y inward square to it, Z up from the band's bottom face. Datums: A = the "
              "top face (DL's seat), B = the corner end plate's outer face, C = the outer face (Y 0). The corner end "
              "is closed by a welded 1.5 plate (ground flush, anodised with FL1); the knee end is a 7.25 deg mitre, "
              "open, with the knee key 111214 inside.",
    "111105": "Part system CS-111105: X along FL2's outer face from its knee end (the long point of the 7.25 deg mitre), "
              "Y inward square to it, Z up from the band's bottom face. Datums: A = the top face (DL's seat), B = the "
              "knee end plate's outer face, C = the outer face (Y 0). At the door end: a 7 mm block welded on to reach "
              "DL's door face, and a 2 mm plate welded into it, flush with DL's door face, from FL2's inner face to the "
              "kick strip's back line (112.6 wide), from the band's bottom face to its top, its back edge a full round "
              "R1 (the PM's hinge-side ruling); on the plate's door face the strike pad 8 x 12 x 65 (thickness HOLD), "
              "from the bottom face up, centred on the glass line. Weld, grind flush and anodise with FL2: one part.",
    "111602": "Part system: Z the glide's axis, up from the base's bottom face (on the room floor). Datums: A = the "
              "base's bottom face, B = the axis. Turned in one piece from zinc-plated free-cutting steel without lead "
              "(11SMn30 / AISI 1215 or similar, assumption), zinc plated, clear passivated (D-164).",
    "111211": "Part system: X into the band from the end face (X 0), Y across the band (centred), Z up from the "
              "key's bottom. Datums: A = bottom face (sits on the band's bottom wall, pod Z 11.5), B = end face "
              "(flush with the band's end), C = the Y faces' centre plane. Block 25 x 35 x 75.",
    "110000": "Pod coordinates (conventions §4): origin on the room floor at the pod centre, +X right, +Y back, +Z up.",
    "111106": "Pod coordinates: X along the band from the door opening (X 218.5) to the joint x_fr_joint (X 915), Y from "
              "the front face (-850) inward, Z up. Datums: A = top face, B = front (outer) face, C = the left end face "
              "(door opening). The right end is closed by a welded 1.5 mm end plate with 2 keyholes.",
    "111301": "Pod coordinates: X along the sill from the door opening (X 218.5) to X 965. Section (view from the left, "
              "1:1): flange down FR1's inner face, ledge flush with the band top (Z 110), drop, seat under the U-channel "
              "(Z 93 to 95), kerb down to the band's bottom line (Z 10; no floor, D-132). Datums: A = the ledge's top face, B = the flange's outer face "
              "(Y -810), C = the left end. Bends 90 deg, inside radius 2 (assumption, the bender confirms).",
    "110101": "Pod coordinates (conventions §4), as built: the side band LH, X -1250 to -1210, Y -670 to 850, "
              "on its glides. Factory-fitted: rivnuts with stop washers and spigots (J-BASE-01), glide doublers, "
              "glides preset (D-87); in its back end the corner key 111211 against the inner wall, with its 2 fixing "
              "screws and its 2 stud bolts set 1.8 off the inner wall, and the flat end cap 118003 (J-BASE-02, D-129); "
              "the front end carries the front corner key 111212 (P02). GLIDES: level up from the highest floor spot; "
              "never below 8.5 mm under the band (the keys' screw heads hang 3.3; the glide's base is the stop).",
    "110102": "Pod coordinates (conventions §4), as built: the side band RH, X 1210 to 1250, Y -672 to 850, on "
              "its glides; 110101's mirror. Factory-fitted: rivnuts with stop washers and spigots (J-BASE-01), glide "
              "load blocks, glides preset (D-87); in its back end the corner key 111211 (turned 180 deg) against the "
              "inner wall, with its 2 fixing screws and 2 stud bolts set 1.8 off the inner wall, and the flat end cap "
              "118003 (J-BASE-02, D-129, D-144); the front end carries the front corner key 111213 (with the intake, "
              "P02 batch 3). GLIDES: level up from the highest floor spot; never below 8.5 mm under the band.",
    "110104": "Pod coordinates (conventions §4), as built: DL's two facet pieces, FL1 (X -1250 to -1135) and FL2 "
              "with its welded door-end block (to DL's door face, X -972). Factory-fitted: the knee key 111214 in FL1's "
              "knee end with its 2 fixing screws and 2 hook studs (heads 1.8 off its stud face), FL2's glide with its "
              "load block, the lip seal along the inner faces; no base spigots for DL (D-169: it locates on pins at "
              "its seam face). On site it goes on along the left side band's front key studs, then down 10 (J-BASE-02); "
              "FL2 goes on FL1's knee studs the same way at the factory. GLIDE: level up from the highest floor spot "
              "before DL goes on.",
    "110106": "Pod coordinates (conventions §4), as built: FR1 (X 218.5 to 915, Y -850 to -810) with its sill and "
              "FRONT's bottom U-channel screwed on at the factory, its 2 glides with load blocks, the flat end cap at "
              "the door opening (D-132) and the lip seal along its inner face. FR1 goes on last: along the intake's "
              "inline key studs (111215, D-144), then down 10 (J-BASE-02). Its glides are levelled by turning their "
              "base (no key holes on its visible top).",
    "110103": "Pod coordinates (conventions §4), as built: the back band, X -1210 to 1210 over its welded end "
              "plates, Y 810 to 850, on its glides. Factory-fitted: rivnuts, stop washers and spigots for B1 and B2 "
              "(J-BASE-01), glide doublers, glides preset (D-87). It is lowered straight down between the side bands: "
              "each end plate's open slot takes a side band's 2 key studs, their heads coming up through the bottom "
              "wall's notches (J-BASE-02, D-129); nobody lifts it or stands on it until B1 and B2 are bolted on. "
              "GLIDES: level up from the highest floor spot; never below 8.5 mm under the band (the glide's base is "
              "the stop).",
}

HOLES = {
    "111601": "One hole Ø13.50 +0.15/0 for the glide's M10 rivnut 838006 (D-163).",
    "111104": "Top wall: none (DL's base spigot went with D-169). Bottom wall: the knee key's 2 fixing holes Ø7.0, 10.5 from its back face and 7.0 either side of its "
              "centre line (J-BASE-02, 111214). Corner end plate: 2 keyholes, a Ø12 entry 10 below each seat and a "
              "6.5 slot up to it, the seats 27.5 and 61.5 above the bottom face on the plate's centre line (J-BASE-02, "
              "the front corner key 111212's studs).",
    "111105": "Top wall: the glide's key hole Ø8 (DL's base spigot went with D-169). "
              "Bottom wall: the glide's rivnut hole Ø13.50 +0.15/0 (D-163). Knee end plate: 2 keyholes, a Ø12 entry 10 "
              "below each seat and a 6.5 slot up to it, the seats 27.5 and 61.5 above the bottom face on the plate's "
              "centre line (J-BASE-02, the knee key 111214's studs).",
    "111602": "Hex socket 5 across flats, 6 deep, in the stem's top: a 5 mm hex key turns the glide from above through "
              "the band top's Ø8 key hole (BASE feature rationale FB-06, FG-03).",
    "111211": "Bottom: 2 x M6, 15 of full thread (tap drill Ø5.0 x 18), for the M6 x 12 button head fixing screws, "
              "10 from the back face and 7.5 either side of the centre line. End face: 2 x M6 tapped through, for "
              "the hook studs, 26 and 60 above the bottom (pod Z 37.5 and 71.5) on the centre line (joints register "
              "J-BASE-02; PM ruling on F-017).",
    "110000": "Holes on the part drawings.",
    "111106": "Bottom wall: 2 glide nut holes Ø13 (X 293.5 and 840), no holes on its top (in view in front of the glass). "
              "End plate at X 915: 2 keyholes, Ø12 entry 10 below each seat and a 6.5 slot up to it, seats at Z 37.5 "
              "and 71.5 on the band's centre line (joints register J-BASE-02, the intake's inline key 111215, D-144).",
    "111301": "Seat: 4 holes Ø5 for the flush M3 rivnuts (838008, HOLD) at X 269.4, 484.3, 699.2 and 905 on the glass line "
              "(Y -699). Flange: blind rivet holes to FR1, HOLD.",
    "110101": "Holes on the part drawings (111101; the key 111211 on the Joints Engineer's sheet).",
    "110103": "Holes, slots and notches on the part drawing (111103).",
    "110102": "Holes on the part drawing (111102; the keys on the Joints Engineer's sheet).",
    "110104": "Holes on the part drawings (111104, 111105; the knee key 111214 on the Joints Engineer's sheet).",
    "110106": "Holes on the part drawings (111106, 111301).",
}


# sheets whose views reach the bottom left: their notes go on the right, above the title block
NOTES_RIGHT = {"110000", "111602", "111104", "111105"}


def kind_of(pn):
    if pn[2:4] == "00" or pn[2] == "0":             # xx0000 to xx0999: assemblies (conventions section 5)
        return "assembly"
    return {"111101": "tube", "111102": "tube", "111103": "tube", "111104": "tube", "111105": "tube", "111106": "tube",
            "111301": "sheet", "111602": "turned"}.get(pn, "plate")


def text_block(pn):
    d = json.load(open(DATA, encoding="utf-8"))
    rec = d["parts"].get(pn, {})
    name = rec.get("name", "BASE") if pn != "110000" else "BASE (P02: the band ring so far; no floor, D-132)"
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


# the owner's rule (Mechanical Checker's C05, 2026-11-01): a drawing's Created by field and its PDF author read this
AUTHOR = "Autonomous"


def fill_created_by(page):
    """Write AUTHOR in the title block's Created by cell, where pdf_clear_field took the account holder's name out:
    on the line under the label, at its left edge, as large as the date left on that line."""
    labs = page.search_for("Created by")
    if not labs:
        raise SystemExit("no Created by field on the sheet")
    lab = labs[0]
    lh = lab.y1 - lab.y0
    row = [w for w in page.get_text("words")
           if lab.y1 - 0.5 < w[1] < lab.y1 + 3 * lh and lab.x0 - 1 <= w[0] < lab.x0 + 200]
    if any(w[4].strip(",.") == AUTHOR for w in row):
        return                  # the shared name strip (tools/fusion, PR #290) already wrote it
    ref = min(row, key=lambda w: w[1]) if row else None
    hgt = (ref[3] - ref[1]) if ref else 2 * lh
    base = (ref[3] if ref else lab.y1 + hgt) - 0.22 * hgt
    page.insert_text((lab.x0, base), AUTHOR, fontsize=max(hgt / 1.15, 3.5 * 72.0 / 25.4), fontname="helv")


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
    fill_created_by(page)
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
    meta = {k: v for k, v in (doc.metadata or {}).items() if k not in ("format", "encryption")}
    meta["author"] = AUTHOR
    doc.set_metadata(meta)
    doc.subset_fonts()        # embed only the letters used: the whole Arial Unicode made each sheet 15 MB
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    os.remove(tmp)
    png = os.path.join(HERE, dwg.replace("_DWG", "_IMG") + ".png")
    d2 = fitz.open(out)
    d2[0].get_pixmap(dpi=110).save(png)
    text = d2[0].get_text()
    d2.close()
    missing = [k for k in ("mm", "first angle", "Material", "Finish", "Tolerances", AUTHOR) if k not in text]
    print("%s: %s, %s%s" % (pn, os.path.relpath(out, REPO), os.path.relpath(png, REPO),
                            ("; MISSING TEXT %s" % missing) if missing else "; text check OK"))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        finish(arg)
