#!/usr/bin/env python3
"""The text of drawing 711001 (the power unit's folded enclosure body): its data block, general notes and
hole list, from the part's own build parameters (electrical_parts_cad.py PARTS, evaluated the way Fusion
does), and the step that finishes the PDF.

    python3 v2/02-Drawings/electrical/body_drawing_text.py --print [--zs 1]
    python3 v2/02-Drawings/electrical/body_drawing_text.py --pdf RAW.pdf OUT.pdf [--zs 1]

Fusion's drawing API can't put text on a sheet (custom tables stay blank, the title block fields come only
from properties; WALL's finding), so the text goes into the exported PDF here, as real text in the free
block above the title block, where the drawing check and a reader can find it. --pdf first removes the
"Created by" name with tools/fusion/pdf_clear_field.py (the repo is public), then writes the block, then
re-reads the PDF and fails if a required item (units, material, finish, tolerance, hole tags) is missing.

--zs: the side the body opens to in its design, +1 or -1 (the build prints "returns toward +Z/-Z"). The
FRONT view looks at the open side with +Y up, so with -1 the FRONT view's left is the design's X = w; the
hole list gives every position from the datums on the drawing (A bottom face, B the FRONT view's left
face, C the back face), so it reads the same either way.
"""

import argparse
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("SPACESHIP_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAD = os.path.join(REPO, "v2", "01-CAD-Native", "electrical")
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
PN = "711001"
SHEET_H = 420.0                 # A2 landscape, mm
BLOCK = (410.0, 62.0, 584.0, 240.0)   # x0, y0, x1, y1 in sheet mm (origin bottom left): above the title block
PT = 72.0 / 25.4


def _parts_cad():
    """electrical_parts_cad.py's PARTS without Fusion: stub the two adsk names it reads at import."""
    if CAD not in sys.path:
        sys.path.insert(0, CAD)
    if "adsk" not in sys.modules:
        adsk = types.ModuleType("adsk")
        core, fusion = types.ModuleType("adsk.core"), types.ModuleType("adsk.fusion")
        fusion.DimensionOrientations = types.SimpleNamespace(HorizontalDimensionOrientation=0,
                                                             VerticalDimensionOrientation=1)
        adsk.core, adsk.fusion = core, fusion
        sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.fusion": fusion})
    import electrical_parts_cad as C
    return C


def params():
    """The body's own parameters, evaluated (mm), with each one's status."""
    C = _parts_cad()
    M = C.M
    pn, name, vn, stem, plist = C.PARTS["body"]
    vals, status = {}, {}
    for n, expr, _unit, st, _src in plist:
        vals[n] = M.evaluate(expr, dict(vals))
        status[n] = st
    return {"pn": pn, "name": name, "vn": vn, "stem": stem, "v": vals, "status": status, "rev": M.REV}


def holes(p, zs=1):
    """(tag, where, position from the drawing's datums, diameter, note) for every hole, H01... in the build's order."""
    v = p["v"]
    w, d = v["w"], v["d"]
    xb = (lambda x: x) if zs > 0 else (lambda x: w - x)     # X from datum B (the FRONT view's left face)
    depth_lead = d - v["lead_y"]
    depth_sleeve = d - v["sleeve_y"]
    return [
        ("H01", "right return" if zs > 0 else "left return (FRONT view)", "Y %.1f from A, %.1f from C" % (v["lead_z1"], depth_lead),
         v["hole_b"], "lead exit 1, Heyco 2836 bushing"),
        ("H02", "right return" if zs > 0 else "left return (FRONT view)", "Y %.1f from A, %.1f from C" % (v["lead_z2"], depth_lead),
         v["hole_b"], "lead exit 2, Heyco 2836 bushing"),
        ("H03", "top return", "X %.1f from B, %.1f from C" % (xb(v["top_x"]), depth_lead), v["hole_b"],
         "light feed exit, Heyco 2836 bushing"),
        ("H04", "bottom return", "X %.1f from B, %.1f from C" % (xb(v["sleeve_x"]), depth_sleeve), v["sleeve_d"],
         "mains and LAN sleeve entry (20 mm conduit)"),
    ] + [
        ("H%02d" % (5 + i), "front lip", "X %.1f from B, Y %.1f from A" % (xb(x), y), v["clinch_d"],
         "M4 clinch nut (HOLD: nut and hole to confirm)")
        for i, (x, y) in enumerate(((v["clinch_x"], v["clinch_y"]), (w - v["clinch_x"], v["clinch_y"]),
                                    (v["clinch_x"], v["h"] - v["clinch_y"]), (w - v["clinch_x"], v["h"] - v["clinch_y"])))
    ]


def lines(zs=1, date="2026-11-01"):
    """[(text, size_mm, bold)] for the block: data, notes, hole list."""
    p = params()
    v = p["v"]
    out = [("%s %s - DRAWING DATA" % (p["pn"], p["name"]), 3.0, True),
           ("Tên (VN): %s" % p["vn"], 2.5, False),
           ("Rev / status: %s / DRAFT, not for production" % p["rev"], 2.5, False),
           ("UNITS: mm. Scale 1:2 (iso 1:5) on A2. ISO first-angle projection (ISO 5456-2), symbol below.", 2.5, False),
           ("MATERIAL: aluminium 5052-H32, %.1f mm sheet (status: %s)." % (v["t"], p["status"]["t"].lower()), 2.5, False),
           ("FINISH: mill finish, hidden inside the pod (D-79). Deburr every edge.", 2.5, False),
           ("Made by: v2/02-Drawings/electrical/make_body_drawing.py (Fusion) and body_drawing_text.py; %s." % date, 2.5, False),
           ("", 1.5, False),
           ("GENERAL NOTES", 3.0, True),
           ("1. GENERAL TOLERANCE: ISO 2768-m. Hole positions ±0.2; hole diameters +0.1/0.", 2.5, False),
           ("2. Outside size %.0f x %.0f x %.0f (datums A bottom, B left in the FRONT view, C back face); lips %.0f inward."
            % (v["w"], v["h"], v["d"], v["lip"]), 2.5, False),
           ("3. Inside bend radius %.1f (= thickness), K-factor 0.44, square bend reliefs. Cut from the flat pattern"
            % v["t"], 2.5, False),
           ("   711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DXF.dxf (same revision).", 2.5, False),
           ("4. Fit the Heyco 2836 bushings in H01-H03 and the M4 clinch nuts in H05-H08 after folding.", 2.5, False),
           ("5. HOLD (not cut yet): the fixing to B2's frame (WALL, IF-12) and the earth stud hole (PEM data).", 2.5, False),
           ("", 1.5, False),
           ("HOLES (from the build's parameters; Fusion's hole tables give the same in each view)", 3.0, True)]
    for tag, where, pos, dia, note in holes(p, zs):
        out.append(("%s  %s: %s, Ø%.1f THRU, %s" % (tag, where, pos, dia, note), 2.5, False))
    return out


def required_missing(text):
    """The drawing check's text rules for a part drawing (tools/checks/c_drawings.py), read the same way."""
    import re
    up = text.upper()
    miss = []
    if not re.search(r"\bUNITS?\s*[:=]?\s*MM\b", up):
        miss.append("units")
    if not re.search(r"MATERIAL", up) or not re.search(r"ALUMIN|\d{4}", up):
        miss.append("material")
    if not re.search(r"FINISH|ANODI|MILL FINISH", up):
        miss.append("finish")
    if not re.search(r"ISO\s*2768|TOLERANCE", up):
        miss.append("tolerance")
    if not re.search(r"\bH\d{2}\b", up):
        miss.append("hole tags")
    return miss


def write_block(page, rows, block=BLOCK):
    """Rows of text, top down, inside the block (sheet mm, origin bottom left) on a PDF page of an A2 sheet."""
    import fitz
    page.insert_font(fontname="AU", fontfile=FONT)
    x0, y0, x1, y1 = block
    font = fitz.Font(fontfile=FONT)
    for text, size, bold in rows:                     # every line must fit the block's width
        wmm = font.text_length(text, fontsize=size * PT * (1.1 if bold else 1.0)) / PT
        if wmm > x1 - x0 - 4.0:
            raise RuntimeError("a line is %.0f mm wide, the block %.0f: %r" % (wmm, x1 - x0, text[:60]))
    scale = page.rect.height / (SHEET_H * PT)           # the page may not be exactly A2 in points
    y = y1 - 4.0
    for text, size, bold in rows:
        if y - size < y0:
            raise RuntimeError("the text block overflows its space; shorten the notes")
        if text:
            page.insert_text(fitz.Point(x0 * PT * scale, (SHEET_H - y) * PT * scale), text, fontname="AU",
                             fontsize=size * PT * scale * (1.1 if bold else 1.0))
        y -= size * 1.45


def finish_pdf(raw, out, zs=1):
    import fitz
    tmp = out + ".noname.pdf"
    r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "fusion", "pdf_clear_field.py"), raw, tmp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("pdf_clear_field failed: %s" % (r.stdout + r.stderr)[-400:])
    doc = fitz.open(tmp)
    write_block(doc[0], lines(zs))
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    os.remove(tmp)
    text = "\n".join(pg.get_text() for pg in fitz.open(out))
    miss = required_missing(text)
    if miss:
        raise SystemExit("the finished PDF lacks: %s" % ", ".join(miss))
    print("wrote %s: name removed, text block added (units, material, finish, tolerance, %d holes)" % (
        os.path.relpath(out, REPO), len(holes(params(), zs))))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--zs", type=int, default=1, choices=(1, -1))
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--pdf", nargs=2, metavar=("RAW", "OUT"))
    a = ap.parse_args(argv)
    if a.pdf:
        finish_pdf(a.pdf[0], a.pdf[1], a.zs)
    else:
        for text, _s, bold in lines(a.zs):
            print(("** %s" % text) if bold else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
