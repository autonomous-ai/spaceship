"""Notes and drawing-data blocks for a WALL drawing, as PNG images the drawing script inserts on the sheet.

    python3 v2/02-Drawings/wall/make_sheet_images.py frame 211101

Fusion's drawing API can't put text on a sheet (custom tables stay blank, title block fields come only
from properties), but it can insert images (Sheet.images). So the drawing's general notes, its data
block (number, title, revision, status, scale, units, projection) and its parts or cut list are
written here from the CAD report (v2/03-Manufacturing/wall/out/<pn>.json) and rendered at 300 dpi with
Arial Unicode (Vietnamese names need it). Output: .images/<pn>_<block>.png (git-ignored) and a JSON
with each image's size in mm, which the drawing script reads to place them.
"""

import json
import os
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "..", "..", "03-Manufacturing", "wall", "out")
IMG = os.path.join(HERE, ".images")
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
DPI = 300
PT = 72.0 / 25.4          # points per mm


def load(pn):
    with open(os.path.join(OUT_JSON, "%s.json" % pn), encoding="utf-8") as fh:
        return json.load(fh)


def render(name, lines, width_mm, size_pt=7.0, lead=1.35, title=None, border=True):
    """Lines of text (wrapped to width_mm) in a bordered block, rendered to PNG. Returns (path, w_mm, h_mm)."""
    font = fitz.Font(fontfile=FONT)
    pad = 2.0 * PT
    w = width_mm * PT
    words_lines = []
    for ln in lines:
        bold = ln.startswith("**")
        txt = ln.strip("*")
        cur = ""
        for word in txt.split(" "):
            trial = (cur + " " + word).strip()
            if font.text_length(trial, fontsize=size_pt) > w - 2 * pad and cur:
                words_lines.append((cur, bold))
                cur = "    " + word if not bold else word
            else:
                cur = trial if not cur.startswith("    ") or trial.startswith("    ") else trial
        words_lines.append((cur, bold))
    h = 2 * pad + len(words_lines) * size_pt * lead + (size_pt * 1.6 if title else 0)
    doc = fitz.open()
    page = doc.new_page(width=w, height=h)
    page.insert_font(fontname="AU", fontfile=FONT)
    y = pad + size_pt
    if title:
        page.insert_text((pad, y + 1), title, fontname="AU", fontsize=size_pt * 1.25)
        y += size_pt * 1.6
    for txt, bold in words_lines:
        page.insert_text((pad, y), txt, fontname="AU", fontsize=size_pt * (1.08 if bold else 1.0))
        y += size_pt * lead
    if border:
        page.draw_rect(fitz.Rect(0.5, 0.5, w - 0.5, h - 0.5), color=(0, 0, 0), width=0.6)
    os.makedirs(IMG, exist_ok=True)
    path = os.path.join(IMG, name + ".png")
    page.get_pixmap(dpi=DPI).save(path)
    return path, round(w / PT, 2), round(h / PT, 2)


def frame_blocks(pn, src=None):
    rep = load(src or pn)
    frame = [c for c in rep["components"] if not c["is_root"] and c["part_number"] == pn][0]
    bodies = sorted(frame["bodies"], key=lambda b: b["name"])
    mass = sum(b["mass_kg"] for b in bodies)
    cut = {}
    for b in bodies:
        bx = b["box"]
        length = round(max(bx[i + 3] - bx[i] for i in range(3)), 2)
        sec = "40 × 40 × 1.2" if "BACK" in b["name"] else "20 × 40 × 1.2"
        key = (b["name"].rstrip("0123456789 ").strip(), sec, length)
        cut[key] = cut.get(key, 0) + 1
    name_en, name_vi = frame["description"].split(" | ")[:2]
    data = [
        "**%s_P01_%s_DWG" % (pn, name_en.replace(" - ", "-").replace(" ", "-")),
        "%s · %s" % (name_en, name_vi),
        "Part %s · Rev P01 · Status DRAFT, not released for manufacture" % pn,
        "Units mm · Scale 1:5 on A2 · ISO first-angle projection (symbol below)",
        "Material: aluminium tube 6063-T6 mill finish (PM ruling 2026-10-31) · Mass %.2f kg (CAD)" % mass,
        "Native CAD %s v%s · STEP and parts list in v2/03-Manufacturing/wall/" % (rep["document"], rep["version"]),
    ]
    notes = [
        "**GENERAL NOTES",
        "1. Views. FRONT = the frame seen from inside the pod: X(2D) along the panel, +Y of the pod, from the "
        "front end; Y(2D) = +Z. TOP below it, BOTTOM above it, LEFT (the front end) on its right, RIGHT (the back "
        "end) on its left. Pod position L1: left wall, lower row; pod system per conventions.md section 4.",
        "2. Datums. A = bottom face of the bottom rail (stands on the base band, pod Z 112.26). B = front face of the "
        "front stile (pod Y -642.74, 2.26 seam to the decor block). C = outer face (pod X -1244, bonded to the skin).",
        "3. Hole tables: one per drilled face, origin at that view's lower left corner, X/Y in mm. Ø7.0 = M6 bolt "
        "clearance (captive M6 × 16 ISO 4762 with an ISO 7093-1 washer). Ø19 = key access and grommet retainer. "
        "Ø9.53 +0.10/0 = Sherex CAH3-610-4.2 rivnut over a 1.5 mm stop washer. Ø8.5 and the 8.5 × 14 slot (along X) = "
        "locating spigots. Bolts at the 220 rule on every edge; corner rivnuts on the bolt line Y 824 (pod). Reasons: "
        "FEATURE-RATIONALE-210101.md.",
        "4. Hole position Ø0.4 (±0.2) from the round spigot hole in the bottom rail, by CNC or drill jig (PM ruling F-009).",
        "5. Cut list (square ends, tube 6063-T6): " + "; ".join(
            "%s %s × %g × %d" % (k[0], k[1], k[2], q) for k, q in sorted(cut.items())) + ".",
        "6. Member joints HOLD (H11): butt joints shown, rails run the full length. Cut lengths ±0.5 (assumption) "
        "until the frame maker's capability is known (guideline 6.3).",
        "7. HOLD: member joints (H11), captive bolt retainer (HOLD-02), rivnut torque (HOLD-01). P01 DRAFT.",
    ]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None)]


def comp_of(rep, pn):
    return [c for c in rep["components"] if not c["is_root"] and c["part_number"] == pn][0]


def data_block(pn, comp, rep, scale, sheet, material, mass):
    name_en, name_vi = comp["description"].split(" | ")[:2]
    return [
        "**%s_P01_%s_DWG" % (pn, name_en.replace(" - ", "-").replace(" ", "-")),
        "%s · %s" % (name_en, name_vi),
        "Part %s · Rev P01 · Status DRAFT, not released for manufacture" % pn,
        "Units mm · Scale %s on %s · ISO first-angle projection (symbol below)" % (scale, sheet),
        "Material: %s · Mass %.2f kg (CAD)" % (material, mass),
        "Native CAD %s v%s · STEP, DXF and parts list in v2/03-Manufacturing/wall/" % (rep["document"], rep["version"]),
    ]


VIEWS_NOTE = ("Views. FRONT = seen from inside the pod: X(2D) along the panel (+Y of the pod, from the front end); "
              "Y(2D) = +Z. TOP below it, BOTTOM above it, LEFT (the front end) on its right, RIGHT (the back end) on "
              "its left. Position L1: left wall, lower row (pod system, conventions.md section 4).")


def skin_blocks(pn, src=None):
    rep = load(src or pn)
    c = comp_of(rep, pn)
    b = c["bodies"][0]["box"]
    length, ret, height = b[4] - b[1], b[3] - b[0], b[5] - b[2]
    mass = sum(x["mass_kg"] for x in c["bodies"])
    data = data_block(pn, c, rep, "1:5", "A2", "ACP 3 mm Alcorest outdoor EV3038 Dark Yellow (HW-SEL A1; D-12)", mass)
    notes = [
        "**GENERAL NOTES",
        "1. " + VIEWS_NOTE,
        "2. Datums. A = bottom edge (pod Z 112.26); B = front edge (pod Y -642.74, 2.26 seam to the decor block); "
        "C = back face (bonded to the frame through the 3 mm bond line).",
        "3. Blank %.2f × %.2f (DXF %s_P01_..._DXF.dxf): main face %.2f plus the %.2f back return, outer-face lengths. "
        "The return is V-grooved on the back face along the BEND line and folded 90° to cover the frame's back end "
        "at the corner (D-55). Fold allowance 0 and the groove rest thickness: HOLD H16 (the ACP maker's rule)." % (
            ret + length, height, pn, length, ret),
        "4. Bond to the frame: SikaTack Panel-50, one 12 × 3 joint on every frame member, laid face down on a flat "
        "table with the ACP face as datum (bond spec, joints register PR #23; in-line tape HOLD-B2).",
        "5. Edges flush with the frame's top and bottom: the outside reveal is the 2.26 seam gap (D-23).",
        "6. Protect the coloured face; film stays on until the panel is installed.",
    ]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None)]


def tray_blocks(pn, src=None):
    rep = load(src or pn)
    c = comp_of(rep, pn)
    mass = sum(x["mass_kg"] for x in c["bodies"])
    b = c["bodies"][0]["box"]
    data = data_block(pn, c, rep, "1:5", "A2", "galvanised steel sheet 0.5, EN 10346 DX51D+Z", mass)
    notes = [
        "**GENERAL NOTES",
        "1. " + VIEWS_NOTE,
        "2. Datums. A = bottom return's outer face; B = front return's outer face (the decor back plate line, pod Y "
        "-645); C = back face of the base (4 mm from the frame).",
        "3. Sheet metal 0.5 mm: returns %.0f deep overall, turned in as 12 mm lips that hold the felt (PM ruling "
        "2026-10-31, option 1). Inside bend radius 0.5 (1 × t), K-factor 0.44, square corner relief: assumptions "
        "until the factory's tooling sets them (guideline 9). Flat blank in the DXF from Fusion's flat pattern." % (
            b[3] - b[0]),
        "4. The felt (511301) drops in behind the lips, 1 mm clear inside the returns; no glue (settles H09 for the walls).",
        "5. Clip fixings on the base: HOLD (H03, HOLD-08), zones reserved on the first and last intermediate stiles "
        "of the frame; nothing else fixes the tray to the frame (floating, D-17).",
        "6. Burr-free edges; zinc coating mass to confirm with the supplier.",
    ]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None)]


def parts_rows(bom_csv, top_pn):
    """Rows of the BOM CSV under one assembly (level 0 row = top_pn), for the drawing's parts list."""
    import csv
    rows, inside = [], False
    with open(bom_csv, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["level"] == "0":
                inside = r["part_number"] == top_pn
                continue
            if inside and r["level"] == "1":
                rows.append(r)
    return rows


def assembly_blocks(pn, kind, src=None):
    rep = load(src or pn)
    root = [c for c in rep["components"] if c["is_root"]][0]
    bom = os.path.join(OUT_JSON, "..", "210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_BOM.csv")
    rows = parts_rows(bom, pn)
    mass = sum(b["mass_kg"] for c in rep["components"] if not c["part_number"].startswith("NO-PN")
               for b in c["bodies"])
    name_en, name_vi = root["description"].split(" | ")[:2]
    data = [
        "**%s_P01_%s_DWG" % (pn, name_en.replace(" - ", "-").replace(" ", "-")),
        "%s · %s" % (name_en, name_vi),
        "Assembly %s · Rev P01 · Status DRAFT, not released for manufacture" % pn,
        "Units mm · Scale 1:5 on A2 · ISO first-angle projection (symbol below)",
        "Made parts %.2f kg (CAD) plus the bought items in the list" % mass,
        "Native CAD %s v%s · BOM %s" % (rep["document"], rep["version"], os.path.basename(bom)),
    ]
    plist = ["**PARTS LIST (item · part number · name · qty · status)"]
    for i, r in enumerate(rows, 1):
        plist.append("%d · %s · %s · %s %s · %s" % (i, r["part_number"] or "no PN yet", r["name_en"], r["qty"],
                                                  r["unit"], r["status"].split(";")[0]))
    if kind == "panel":
        notes = [
            "**GENERAL NOTES",
            "1. " + VIEWS_NOTE,
            "2. Stack outside to inside: ACP skin 3 (211301), bond line 3 (SikaTack Panel-50, 12 × 3 on every member), "
            "frame 40 (211101, 6063-T6), PET fill 40 in the bays (211501): outer panel 46. Then the 4 mm gap and the "
            "lining cassette 34 (510101, a separate part): 84 in all (PM ruling 2026-10-31).",
            "3. Site joints (joints register, PR #23): J-BASE-01 to the base band, 4 captive M6 × 16 driven down "
            "through the bottom rail; J-FRONT-01 to the decor block, 3 driven forward through the front stile; "
            "J-WALL-01 to L2, 4 rivnuts in the top rail (L2 drives); J-WALL-02 to B1, 3 rivnuts in the 40 × 40 back "
            "stile (B1 drives). Seam gap 2.26 at each, set by the 1.5 mm stop washers.",
            "4. Factory fits: rivnuts with stop washers, the 2 spigots in the top rail, the captive bolts with their "
            "retainers (HOLD-02), the gaskets on the nut-side faces (PORON 4701-40, HOLD-05). Fill pockets 60 × 60 "
            "left open beside every bolt this panel drives.",
            "5. Bond: panel bonded face down on a flat table; no standing, stacking or shipping before 72 h (bond spec).",
            "6. HOLD: member joints (H11), retainer (HOLD-02), torque (HOLD-01), gasket converter (HOLD-05).",
        ]
    else:
        notes = [
            "**GENERAL NOTES",
            "1. " + VIEWS_NOTE,
            "2. Floating inner leaf (D-17): tray 511101 (0.5 mm, 34 mm returns, 12 mm lips) holds the 9 mm felt "
            "511301 behind its lips over a 24 mm air gap. It hangs on captive clips with a rated load (D-47), never a "
            "screw; 4 mm clear of the frame.",
            "3. Clips HOLD (H03): 4 zones reserved on the first and last intermediate stiles of the panel frame, 100 "
            "from the top and bottom, clear of every key access hole and fill pocket.",
            "4. Hook-and-loop only to line it up (D-47). PORON gasket round the outer edge (HOLD-05, H14).",
            "5. It runs from the decor back plate (pod Y -645) to past the back lining's face (Y 800), closing the "
            "inside corner (D-57). Cables in the air gap clip to the tray only (D-26).",
        ]
    return [("data", data, 150.0, None), ("parts", plist, 150.0, None), ("notes", notes, 150.0, None)]


def main(argv):
    kind, pn = argv[1], argv[2]
    src = argv[3] if len(argv) > 3 else None      # read another design's report (the part sits in it too)
    if kind in ("panel", "cassette"):
        blocks = assembly_blocks(pn, kind, src)
    else:
        blocks = {"frame": frame_blocks, "skin": skin_blocks, "tray": tray_blocks}[kind](pn, src)
    meta = {}
    for name, lines, width, title in blocks:
        path, w, h = render("%s_%s" % (pn, name), lines, width, title=title)
        meta[name] = {"path": path, "w_mm": w, "h_mm": h}
        print("%s: %.1f x %.1f mm -> %s" % (name, w, h, os.path.relpath(path, HERE)))
    with open(os.path.join(IMG, "%s_images.json" % pn), "w") as fh:
        json.dump(meta, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv)
