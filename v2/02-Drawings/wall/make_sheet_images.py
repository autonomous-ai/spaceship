"""Notes and drawing-data blocks for a WALL drawing, as PNG images the drawing script inserts on the sheet.

    python3 v2/02-Drawings/wall/make_sheet_images.py frame 211101         # kinds: frame frame_back skin tray
    python3 v2/02-Drawings/wall/make_sheet_images.py panel 210101         #        panel cassette (any position)

Fusion's drawing API can't put text on a sheet (custom tables stay blank, title block fields come only
from properties), but it can insert images (Sheet.images). So the drawing's general notes, its data
block (number, title, revision, status, scale, units, projection) and its parts or cut list are
written here from the CAD report (v2/03-Manufacturing/wall/out/<pn>.json) and rendered at 300 dpi with
Arial Unicode (Vietnamese names need it). Output: .images/<pn>_<block>.png (git-ignored) and a JSON
with each image's size in mm, which the drawing script reads to place them.
"""

import json
import os
import re
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


def tab_rows(kind, back):
    """D-89: identical or mirrored skins and trays share one tabulated drawing. The rows (part number, position,
    hand, size) come from the build scripts' own parameters, resolved offline the way Fusion resolves them
    (v2/01-CAD-Native/wall/test_wall_offline.py), so they match the designs."""
    sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "wall"))
    import test_wall_offline as t
    out = []
    for code in (("B1", "B2", "B3", "B4") if back else ("L1", "R1", "L2", "R2")):
        if back:
            ns = t.load_back(code, "skin" if kind == "skin" else "tray")
        else:
            ns = t.load(part="skin" if kind == "skin" else "tray", side=code[0], row=code[1])
        v = t.resolve(ns)
        pn = ns["PARTS"]["skin" if kind == "skin" else "tray"][0]
        hand = ("LH" if code in ("L1", "L2", "B1", "B3") else "RH")
        if kind == "skin":
            size = ("%.2f × %.2f, flat" % (v["pnl_len"], v["pnl_h"]) if back else
                    "%.2f × %.2f, back return %.0f (blank %.2f × %.2f)" % (v["pnl_len"], v["pnl_h"], v["outer_t"],
                                                                        v["pnl_len"] + v["outer_t"], v["pnl_h"]))
        else:
            size = "%.2f × %.2f × %.0f deep" % (v["cass_len"], v["cass_h"], v["tray_h"])
        out.append("%s · %s · %s · %s" % (pn, code, hand, size))
    return out


def render(name, lines, width_mm, size_pt=10.0, lead=1.35, title=None, border=True):
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


POS_WORDS = {"L1": "left wall, lower row", "R1": "right wall, lower row", "L2": "left wall, upper row",
             "R2": "right wall, upper row", "B1": "back wall, lower row, left half", "B2": "back wall, lower row, "
             "right half", "B3": "back wall, upper row, left half", "B4": "back wall, upper row, right half"}


def comp_of(rep, pn):
    return [c for c in rep["components"] if not c["is_root"] and c["part_number"] == pn][0]


def position(rep):
    """Position code and its facts, from the design's part number: 21/51, an odd 4th digit for the side walls
    (2101, 2111, 2113, 2115, 5101, 5111, 5113) and an even one for the back (2102, 2112, ...), then 01-04
    (side L1 R1 L2 R2, back B1 B2 B3 B4)."""
    pn = rep["document"].split("_")[0]
    back = int(pn[3]) % 2 == 0
    code = ("B%d" % int(pn[4:])) if back else ["L1", "R1", "L2", "R2"][int(pn[4:]) - 1]
    return {"code": code, "back": back, "row": 1 if code in ("L1", "R1", "B1", "B2") else 2,
            "right": code in ("R1", "R2", "B2", "B4"), "words": POS_WORDS.get(code, code)}


def views_note(pos):
    if pos["back"]:
        ends = ("the corner end on the left, the closing seam on the right" if not pos["right"] else
                "the closing seam on the left, the corner end on the right")
        return ("Views. FRONT = seen from inside the pod: X(2D) = +X of the pod (%s); Y(2D) = +Z. TOP below it, "
                "BOTTOM above it, LEFT (the view from the left end) on its right, RIGHT on its left. Position %s: %s "
                "(pod system, conventions.md section 4)." % (ends, pos["code"], pos["words"]))
    if pos["right"]:
        return ("Views. FRONT = seen from inside the pod: X(2D) = -Y of the pod (the back end on the left, the front "
                "end on the right); Y(2D) = +Z. TOP below it, BOTTOM above it, LEFT (the back end) on its right, RIGHT "
                "(the front end) on its left. Position %s: %s (pod system, conventions.md section 4)." % (
                    pos["code"], pos["words"]))
    return ("Views. FRONT = seen from inside the pod: X(2D) = +Y of the pod (the front end on the left); Y(2D) = +Z. "
            "TOP below it, BOTTOM above it, LEFT (the front end) on its right, RIGHT (the back end) on its left. "
            "Position %s: %s (pod system, conventions.md section 4)." % (pos["code"], pos["words"]))


def box_of(bodies):
    return [min(b["box"][i] for b in bodies) for i in range(3)] + [max(b["box"][i + 3] for b in bodies) for i in range(3)]


def data_block(pn, comp, rep, scale, sheet, material, mass, kind="Part"):
    name_en, name_vi = comp["description"].split(" | ")[:2]
    return [
        "**%s_P01_%s_DWG" % (pn, name_en.replace(" - ", "-").replace(" ", "-")),
        "%s · %s" % (name_en, name_vi),
        "%s %s · Rev P01 · Status DRAFT, not released for manufacture" % (kind, pn),
        "Units mm · Scale %s on %s · ISO first-angle projection (symbol below)" % (scale, sheet),
        "Material: %s · Mass %.2f kg (CAD)" % (material, mass),
        "Native CAD %s v%s · STEP, DXF and parts list in v2/03-Manufacturing/wall/" % (rep["document"], rep["version"]),
    ]


def rivnut_sku(rep):
    """The Sherex rivnut a design carries (838003): from its component's name, else from the rivnut_d parameter's
    source (a frame's design holds no rivnut); CAH2-610-4.2, the part before D-163, for a report with neither."""
    for c in rep.get("components", []):
        m = re.search(r"SHEREX (\S+)", c["name"]) if c["part_number"] == "838003" else None
        if m:
            return m.group(1)
    for p in rep.get("parameters", []):
        m = re.search(r"Sherex (C[A-Z]+\d-\d+-[\d.]+\d)", p.get("comment") or "") if p["name"] == "rivnut_d" else None
        if m:
            return m.group(1)
    return "CAH2-610-4.2"


def frame_blocks(pn, src=None):
    rep = load(src or pn)
    pos = position(rep)
    frame = comp_of(rep, pn)
    prm = {p["name"]: p["value"] for p in rep["parameters"]}
    # D-120: a rebuilt frame holds no bodies itself; its members are parts, the studs copies of one
    members = [c for c in rep["components"] if c["part_number"].startswith("212") and pn in c.get("parents", [])]
    if members:
        bodies = [dict(c["bodies"][0], part=c["part_number"]) for c in members for _ in range(c.get("copies", 1))]
    else:
        bodies = sorted(frame["bodies"], key=lambda b: b["name"])
    mass = sum(b["mass_kg"] for b in bodies)
    bx = box_of(bodies)
    cut = {}
    for b in bodies:
        d = sorted(round(b["box"][i + 3] - b["box"][i], 2) for i in range(3))
        wall = prm.get("stud_t", 0.8) if b["name"].startswith("STILE - MID") else (
            prm.get("corner_t", prm.get("tube_t", 1.0)) if d[0] >= 39.9 else prm.get("tube_t", 1.0))
        sec = "%s × %.1f" % ("40 × 40" if d[0] >= 39.9 else "20 × 40", wall)
        key = (("%s %s" % (b["part"], b["name"])) if members else b["name"].rstrip("0123456789 ").strip(), sec, d[2])
        cut[key] = cut.get(key, 0) + 1
    # D-163: the rivnut hole and part as the frame's own CAD has them (Ø10.00 +0.10/0 and CAL2-610-4.2 from its
    # rebuild): a frame's design holds no rivnut, so its part comes from the rivnut_d parameter's source
    rv_sku = rivnut_sku(rep)
    rv = "Ø%.2f +0.10/0 = Sherex %s rivnut" % (prm.get("rivnut_d", 9.53), rv_sku)
    data = data_block(pn, frame, rep, "1:5", "A2", "steel box tube S280GD+Z (EN 10346) or SGC400 (JIS G3302), "
                      "yield 280 MPa or more, zinc Z100, pre-galvanized; welded (D-131, J-FRAME-01)", mass)
    if pos["back"]:
        seam_x = bx[3] if not pos["right"] else bx[0]
        datums = ("2. Datums. A = bottom face of the bottom rail (pod Z %.2f, on the %s). B = the closing-seam face "
                  "of the centre stile (pod X %.2f: half the 5.5 closing gap, R-J11), the drawing's %s edge. C = outer "
                  "face (pod Y %.2f, bonded to the skin)." % (bx[2], "base band" if pos["row"] == 1 else "lower panel",
                                                                seam_x, "left" if pos["right"] else "right", bx[4]))
        holes = ("3. Hole tables: one per drilled face, origin at datum B's lower corner of that view, X/Y in mm. "
                 "Ø7.0 = M6 bolt clearance (captive M6 × 16 ISO 4762 with an ISO 7093-1 washer): bottom rail, outer "
                 "stile (corner)%s. Ø19 = key access and grommet retainer. " + rv + " (steel, zinc plated): "
                 "top rail%s. %s Ø8.5 round by the closing seam and the 8.5 × 14 slot along the edge at the corner end "
                 "= locating spigots (ST-02). Bolts at 220, 473.00, 725.99, 978.99 from the frame's ends; corner bolts "
                 "at 220, 559.31, 898.61 on Y 824. Reasons: FEATURE-RATIONALE-%s.md." % (
                     ", top rail (ceiling)" if pos["row"] == 2 else "",
                     " (4 for the panel above with stop washers, 2 spigot)" if pos["row"] == 1 else " (2 spigot, for the ceiling)",
                     "Centre stile: 3 plain Ø7.0 that the next panel's pins pass through." if not pos["right"] else
                     "Centre stile: 3 Ø%.2f pin rivnuts (no stop washer) with Ø19 access behind them." % prm.get("rivnut_d", 9.53),
                     rep["document"].split("_")[0].replace("2112", "2102")))
        extra = ("1 × 45° lead-in on the top edge of the closing-seam face, ground into the corner weld (R-J9, "
                 "FR-13). " if members else "1 × 45° lead-in on the top edge of the closing-seam face (R-J9). ")
    else:
        datums = ("2. Datums. A = bottom face of the bottom rail (pod Z %.2f, on the %s). B = front face of the front "
                  "stile (pod Y %.2f, 2.26 seam to the decor block), the drawing's %s edge. C = outer face (pod X %.0f, "
                  "bonded to the skin)." % (bx[2], "base band" if pos["row"] == 1 else "lower panel", bx[1],
                                            "right" if pos["right"] else "left", bx[0] if not pos["right"] else bx[3]))
        holes = ("3. Hole tables: one per drilled face, origin at datum B's lower corner of that view, X/Y in mm. "
                 "Ø7.0 = M6 bolt clearance (captive M6 × 16 ISO 4762 with an ISO 7093-1 washer). Ø19 = key access "
                 "and grommet retainer. " + rv + " (steel, zinc plated) over a 1.5 mm stop washer. Ø8.5 "
                 "and the 8.5 × %g slot (along X) = locating spigots. Bolts at the 220 rule on every edge; corner " % (
                     prm.get("spigot_slot", 14.0)) +
                 "rivnuts on the bolt line Y 824 (pod)%s. Reasons: FEATURE-RATIONALE-%s.md." % (
                     "; ceiling rivnuts on Z 2374 from Y -645 at 351.67 (the ceiling's rule)" if pos["row"] == 2 else "",
                     rep["document"].split("_")[0].replace("2111", "2101")))
        extra = ""
    notes = [
        "**GENERAL NOTES",
        "1. " + views_note(pos),
        datums,
        holes,
        ("4. Hole position Ø0.4 (±0.2) from the round spigot hole in the bottom rail, by CNC or drill jig (F-009); "
         "every joint hole is made after welding and the touch-up, the jig located on the joint faces and the spigot "
         "hole (J-FRAME-01)." if members else
         "4. Hole position Ø0.4 (±0.2) from the round spigot hole in the bottom rail, by CNC or drill jig (F-009)."),
        ("5. Cut list, ends per note 6, steel box tube (walls per J-FRAME-01, D-131): " if members else
         "5. Cut list, square ends: ") + "; ".join(
            "%s: %s tube, length %g, qty %d" % (k[0].title().replace(" - ", " "), k[1], k[2], q)
            for k, q in sorted(cut.items())) + ".",
        ("6. Welded frame (D-131): the 4 perimeter members run to the outer corners, mitred there (D-117: 45° where "
         "the two are the same size; 26.57° on a 40 × 40 meeting a 20 × 40, 63.43° on the 20 × 40), each member cut "
         "back so a 2 mm mitre plate (joints register 831007 to 831009) fits in the mitre, centred on the mitre "
         "line: 1.41 off each member where the two are the same size, 2.24 off a 20 × 40 and 1.12 off a 40 × 40 where "
         "they meet. The plate is welded in, its edges ground flush on the skin and seam faces. The studs fit square "
         "between the rails and are welded there. Weld coupons prove the corner before the first frame is welded. "
         "Pre-galvanized tube, zinc Z100; after welding and grinding, every weld and burnt zone wire-brushed and "
         "coated with a 2-component zinc-rich epoxy; no hot-dip and no vent holes (J-FRAME-01). Each "
         "member is its own part (D-120). %sCut lengths outer to outer after the cut-back, ±0.5 (assumption) until "
         "the frame maker's capability is known (guideline 6.3)." % extra) if members else
        ("6. Member joints: internal cleats per D-115 (internal corner and T cleats, crimped, with structural "
         "adhesive; no welds); the cleats are the joints register's parts, placed when they land. Rails run "
         "the full length, stiles fit between them. %sCut lengths ±0.5 (assumption) until the frame maker's "
         "capability is known (guideline 6.3)." % extra),
        ("7. Rivnuts and stop washers are set at the factory after the zinc-rich touch-up (J-FRAME-01; see the panel "
         "assembly). Seam faces flat within 0.5, skin-side faces within ±0.5 of one plane, diagonals equal within "
         "1.5, measured after welding and before the holes (J-FRAME-01). HOLD: captive bolt retainer (HOLD-02), "
         "torque (HOLD-01). P01 DRAFT." if members else
         "7. Rivnuts and stop washers are set at the factory (see the panel assembly). HOLD: captive bolt retainer "
         "(HOLD-02), torque (HOLD-01). P01 DRAFT."),
        "8. Lengths and hole positions without their own tolerance: ISO 2768-1 class m (steel tube, sawn and "
        "drilled), for the frame maker to confirm (guideline 3.2). Deburr every cut end and hole; break sharp "
        "edges 0.2 max. Hole tables: X to the right, Y up in each view, from the origin named in the table title.",
    ]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None)]


def skin_blocks(pn, src=None):
    rep = load(src or pn)
    pos = position(rep)
    c = comp_of(rep, pn)
    b = c["bodies"][0]["box"]
    mass = sum(x["mass_kg"] for x in c["bodies"])
    data = data_block(pn, c, rep, "1:5", "A2", "ACP 3 mm Alcorest outdoor EV3038 Dark Yellow (HW-SEL A1; D-12)", mass)
    if pos["back"]:
        w, height = b[3] - b[0], b[5] - b[2]
        body = [
            "2. Datums. A = bottom edge (pod Z %.2f); B = the closing-seam edge (pod X %.2f, 1.62 past the frame), the "
            "drawing's %s edge; C = back face (bonded to the frame through the 3 mm bond line)." % (
                b[2], b[3] if not pos["right"] else b[0], "left" if pos["right"] else "right"),
            "3. Blank %.2f × %.2f, flat (DXF %s_P01_..._DXF.dxf). Flush with the frame at the corner, top and bottom; "
            "1.62 past the frame at the closing seam, so the skin seam there is 2.26 like every other (R-J16)." % (
                w, height, pn),
        ]
    else:
        length, ret, height = b[4] - b[1], b[3] - b[0], b[5] - b[2]
        body = [
            "2. Datums. A = bottom edge (pod Z %.2f); B = front edge (pod Y %.2f, 2.26 seam to the decor block), the "
            "drawing's %s edge; C = back face (bonded to the frame through the 3 mm bond line)." % (
                b[2], b[1], "right" if pos["right"] else "left"),
            "3. Blank %.2f × %.2f (DXF %s_P01_..._DXF.dxf): main face %.2f plus the %.2f back return, outer-face "
            "lengths. The return is V-grooved on the back face along the BEND line and folded 90° to cover the frame's "
            "back end at the corner (D-55), 3 mm off it: bonded there like the main face (note 4). Fold allowance 0 "
            "and the groove rest thickness: HOLD H16." % (
                ret + length, height, pn, length, ret),
        ]
    table = ["**TABULATED DRAWING (D-89): ONE SHAPE, THESE PART NUMBERS (part · position · hand · size)"] + \
        tab_rows("skin", pos["back"]) + ["Shown: %s. %s" % (pn, "All four are the same flat rectangle, except 211402 "
                                                          "(B2): two Ø24 holes for ELECTRICAL's inlet and LAN, placed "
                                                          "on the panel drawing 210202 and in its DXF." if pos["back"]
                                                          else "RH is the mirror of LH; L1 = L2 and R1 = R2.")]
    notes = ["**GENERAL NOTES", "1. " + views_note(pos)] + body + [
        ("4. Bond to the frame: Sikaflex-252, one joint at least 12 wide × 3 on every frame member, the 3 set by "
         "fixing-tape pieces in line with the bead; both faces pre-treated with an abrasive pad, Aktivator-205 and "
         "Primer-210; laid face down on a flat table with the ACP face as datum (bond spec section 8, D-137; "
         "HOLD-B6); on a side skin also one joint, 3 mm thick and as wide as the return allows up to 12, between "
         "the return and the frame's back end: every skin face that meets a frame is bonded, none touches it "
         "(D-137)." if not pos["back"] else
         "4. Bond to the frame: Sikaflex-252, one joint at least 12 wide × 3 on every frame member, the 3 set by "
         "fixing-tape pieces in line with the bead; both faces pre-treated with an abrasive pad, Aktivator-205 and "
         "Primer-210; laid face down on a flat table with the ACP face as datum (bond spec section 8, D-137; "
         "HOLD-B6)."),
        "5. Edges flush with the frame's top and bottom: the outside reveal is the 2.26 seam gap (D-23).",
        "6. Protect the coloured face; film stays on until the panel is installed.",
    ]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None), ("table", table, 150.0, None)]


def tray_blocks(pn, src=None):
    rep = load(src or pn)
    pos = position(rep)
    c = comp_of(rep, pn)
    mass = sum(x["mass_kg"] for x in c["bodies"])
    b = c["bodies"][0]["box"]
    felt = pn[:3] + "3" + pn[4:] if pn.startswith("5111") else pn[:3] + "4" + pn[4:]
    data = data_block(pn, c, rep, "1:5", "A2", "galvanised steel sheet 0.5, EN 10346 DX51D+Z", mass)
    if pos["back"]:
        datum = ("2. Datums. A = bottom return's outer face (pod Z %.2f); B = the return at the X 0 end (pod X %.2f, "
                 "1.13 short of X 0: a 2.26 gap to the next back cassette, PM ruling 2026-10-31), the drawing's %s edge; "
                 "C = back face of the base (4 mm from the frame)." % (
                     b[2], b[3] if not pos["right"] else b[0], "left" if pos["right"] else "right"))
        depth = b[4] - b[1]
    else:
        datum = ("2. Datums. A = bottom return's outer face (pod Z %.2f); B = front return's outer face (the decor "
                 "back plate line, pod Y %.2f), the drawing's %s edge; C = back face of the base (4 mm from the frame)." % (
                     b[2], b[1], "right" if pos["right"] else "left"))
        depth = b[3] - b[0]
    notes = [
        "**GENERAL NOTES",
        "1. " + views_note(pos),
        datum,
        "3. Sheet metal 0.5 mm: returns %.0f deep overall, turned in as 12 mm lips that hold the felt (PM ruling "
        "2026-10-31, option 1). Inside bend radius 0.5 (1 × t), K-factor 0.44, square corner relief: assumptions "
        "until the factory's tooling sets them (guideline 9). Flat blank in the DXF from Fusion's flat pattern." % depth,
        "4. The felt (%s) drops in behind the lips, 1 mm clear inside the returns; no glue." % felt,
        "5. Clip fixings on the base: HOLD (H03, HOLD-08), zones reserved on the panel frame's first and last studs; "
        "nothing else fixes the tray to the frame (floating, D-17).",
        "6. Burr-free edges; zinc coating mass to confirm with the supplier.",
    ]
    table = ["**TABULATED DRAWING (D-89): ONE CONSTRUCTION, THESE PART NUMBERS (part · position · hand · size)"] + \
        tab_rows("tray", pos["back"]) + ["Shown: %s. LH and RH are the same tray (no handed feature); the flat "
                                         "blank of each is its own DXF." % pn + (
                                             " ELECTRICAL's features: 511202 (B2) has the power unit cut-out 304 × 268, "
                                             "the corner slot and a Ø19.1 bushing hole; 511204 (B4) a Ø19.1 bushing hole "
                                             "in its bottom return; placed on the cassette drawings 510202 and 510204 "
                                             "and in their DXFs." if pos["back"] else "")]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None), ("table", table, 150.0, None)]



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


def panel_bom(pn):
    """The panel's parts list CSV, which also holds its cassette: 5101 0n -> 2101 0n, 5102 0n -> 2102 0n."""
    import glob
    panel = ("210" + pn[3:]) if pn.startswith("510") else pn
    found = glob.glob(os.path.join(OUT_JSON, "..", "%s_P01_*_BOM.csv" % panel))
    if len(found) != 1:
        raise SystemExit("no parts list for %s (run make_parts_list.py first)" % panel)
    return found[0]


JOINTS = {
    "L1": "J-BASE-01 to the base band, 4 captive M6 × 16 driven down through the bottom rail; J-FRONT-01 to the decor "
          "block, 3 driven forward through the front stile; J-WALL-01 to L2, 4 rivnuts in the top rail (L2 drives); "
          "J-WALL-02 to B1, 3 rivnuts in the 40 × 40 back stile (B1 drives).",
    "L2": "J-WALL-01 to L1, 4 captive M6 × 16 driven down through the bottom rail; J-FRONT-01 to the decor block, 3 "
          "driven forward through the front stile; J-CEIL-01, 4 rivnuts in the 40 × 40 top member's room face on the "
          "ceiling's rule (the ceiling drives); J-WALL-02 to B3, 3 rivnuts in the 40 × 40 back stile (B3 drives).",
    "B1": "J-BASE-01 to the base band, 4 captive M6 × 16 driven down through the bottom rail; J-WALL-02 to L1, 3 "
          "driven out through the outer stile into L1's rivnuts; J-WALL-01 to B3, 4 rivnuts in the top rail (B3 "
          "drives); closing seam to B2: 3 plain Ø7.0 for B2's pins.",
    "B3": "J-WALL-01 to B1, 4 captive M6 × 16 driven down through the bottom rail; J-WALL-02 to L2, 3 driven out "
          "through the outer stile; J-CEIL-01, 4 driven up through the top rail into the ceiling's back member, and 2 "
          "spigots for the ceiling; closing seam to B4: 3 plain Ø7.0 for B4's pins.",
}
JOINTS["R1"] = JOINTS["L1"].replace("L2", "R2").replace("B1", "B2")
JOINTS["R2"] = JOINTS["L2"].replace("L1", "R1").replace("B3", "B4")
JOINTS["B2"] = JOINTS["B1"].replace("L1", "R1").replace("B3", "B4").replace(
    "closing seam to B2: 3 plain Ø7.0 for B2's pins", "closing seam to B1: 3 rivnuts with factory-fitted M6 × 25 pins "
    "(no stop washer), driven across on site")
JOINTS["B4"] = JOINTS["B3"].replace("L2", "R2").replace("B1", "B2").replace(
    "closing seam to B4: 3 plain Ø7.0 for B4's pins", "closing seam to B3: 3 rivnuts with factory-fitted M6 × 25 pins")


def el_lines(rep, pos, kind):
    """ELECTRICAL's features in this design (its el_ parameters; ELECTRICAL P01, PR #64; the PM's rulings of
    2026-10-31), placed from the drawing's datums: A = the bottom (pod Z of the part's bottom), B = the front end
    (side walls, pod Y -645) or the X 0 end (back walls, pod X 1.13), as the part drawings define them. Empty when the
    design has none."""
    pv = {q["name"]: q["value"] for q in rep.get("parameters", [])}
    if not any(k.startswith("el_") for k in pv):
        return []
    za = pv["panel_z0"] + ((pv.get("back_ph", 0.0) if pos["back"] else pv.get("side_h", 0.0)) + pv["seam_gap"]
                           if pos["row"] == 2 else 0.0)
    if pos["back"]:
        xb = pv["seam_gap"] / 2.0

        def at(x, z):
            return "%.2f from B, %.2f from A (pod X %g, Z %g)" % (abs(x - xb), z - za, x, z)
    else:
        yb = pv["pod_d"] / 2.0 - pv["wall_depth"]

        def at(y, z):
            return "%.2f from B, %.2f from A (pod Y %g, Z %g)" % (y - yb, z - za, y, z)
    out = []
    code = pos["code"]
    if kind == "cassette" and code == "R1":
        yl = pv["pod_d"] / 2.0 - pv["stack_t"]
        out += ["felt slot FS-CNR %g × %g, lower front corner at %s, hidden behind B2-CASS (F43)" % (
                    pv["el_fs_y1"] - pv["el_fs_y0"], 2 * pv["el_fs_dz"], at(yl + pv["el_fs_y0"], pv["el_trunk_z"] - pv["el_fs_dz"])),
                "felt hole FA-KIT Ø%g at %s, with a felt plug (F35)" % (pv["el_kit_d"], at(pv["el_y_kit"], pv["el_trunk_z"] + pv["el_kit_dz"])),
                "felt hole FX-COL Ø%g at %s (F36)" % (pv["el_grm_d"], at(pv["el_y_cx"], pv["el_trunk_z"]))]
    elif kind == "cassette" and code == "R2":
        out += ["felt holes FX-CALL0 and FX-CALL2 Ø%g at %s and %s (F37)" % (
            pv["el_grm_s"], at(pv["el_call_y"], pv["el_shelf_z"]), at(pv["el_call_y"], pv["el_call_z"]))]
    elif kind == "cassette" and code == "B2":
        out += ["power unit cut-out %g × %g through the tray base and the felt, plain, lower corner at %s; the unit "
                "stays 4 clear all round; its front plate 320 × 284 covers the felt edge by 8 all round, 2 off the felt "
                "on four nylon spacers, so the lining face stays clear of other features in that band (F44, F46)" % (
                    pv["el_cut_x1"] - pv["el_cut_x0"], pv["el_cut_z1"] - pv["el_cut_z0"],
                                                       at(pv["el_cut_x0"], pv["el_cut_z0"])),
                "bushing hole G-B2-B4 Ø%g in the top return at %.2f from B, Y %g (the cable gap's middle) (F39)" % (
                    pv["el_grm_d"], abs(pv["el_lt_x"] - pv["seam_gap"] / 2.0), pv["el_y_bg"]),
                "corner slot S-CNR %g × %g in the end return, Y %g to %g, Z %g to %g (%.2f to %.2f from A) (F45)" % (
                    2 * pv["el_cs_h"], 2 * pv["el_cs_dz"], pv["el_y_xc"] - pv["el_cs_h"], pv["el_y_xc"] + pv["el_cs_h"],
                    pv["el_trunk_z"] - pv["el_cs_dz"], pv["el_trunk_z"] + pv["el_cs_dz"],
                    pv["el_trunk_z"] - pv["el_cs_dz"] - za, pv["el_trunk_z"] + pv["el_cs_dz"] - za)]
    elif kind == "cassette" and code == "B4":
        out += ["bushing hole G-B2-B4 Ø%g in the bottom return at %.2f from B, Y %g (F39)" % (
                    pv["el_grm_d"], abs(pv["el_lt_x"] - pv["seam_gap"] / 2.0), pv["el_y_bg"]),
                "felt hole FX-SHELF Ø%g at %s (F42)" % (pv["el_shelf_d"], at(pv["el_lt_x"], pv["el_shelf_z"])),
                "felt hole FX-CEIL Ø%g at %s, 2 under the top lip: no cable hole goes through a lip (F40)" % (
                    pv["el_grm_s"], at(pv["el_ceil_x"], pv["el_ceil_z"]))]
    elif kind == "panel" and code == "B2":
        out += ["skin holes Ø%g for the mains inlet and the LAN feed-through at %s and %s (F38)" % (
                    pv["el_inlet_d"], at(pv["el_inlet_x"], pv["el_inlet_z"]), at(pv["el_inlet_x"], pv["el_lan_z"])),
                "fill left out in the first bay for the power unit (to the first stud), the sleeve and the connectors "
                "(F47); the unit's fixing to the frame HOLD (IF-12)"]
    if not out:
        return []
    return ["ELECTRICAL's features (ELECTRICAL P01, PR #64; FEATURE-RATIONALE): " + "; ".join(out) + "."]


def assembly_blocks(pn, kind, src=None):
    rep = load(src or pn)
    pos = position(rep)
    root = [c for c in rep["components"] if c["is_root"]][0]
    bom = panel_bom(pn)
    rows = parts_rows(bom, pn)
    mass = sum(float(r["mass_total_kg"] or 0) for r in rows)
    name_en, name_vi = (root["description"].split(" | ") + ["", ""])[:2]
    if not name_en:                       # the cloud left the root description empty: the parts list's name
        import csv
        with open(bom, encoding="utf-8") as fh:
            top = [r for r in csv.DictReader(fh) if r["level"] == "0" and r["part_number"] == pn][0]
        name_en, name_vi = top["name"], top["name_vi"]
    data = [
        "**%s_P01_%s_DWG" % (pn, name_en.replace(" - ", "-").replace(" ", "-")),
        "%s · %s" % (name_en, name_vi),
        "Assembly %s · Rev P01 · Status DRAFT, not released for manufacture" % pn,
        "Units mm · Scale 1:5 on A2 · ISO first-angle projection (symbol below)",
        "Mass %.2f kg: the parts list's rows (CAD bodies and hardware)" % mass,
        "Native CAD %s v%s · BOM %s" % (rep["document"], rep["version"], os.path.basename(bom)),
    ]
    plist = ["**PARTS LIST (item · part number · name · qty · status)"]
    for i, r in enumerate(rows, 1):
        plist.append("%d · %s · %s · %s %s · %s" % (i, r["part_number"] or "no PN yet", r.get("name") or r.get("name_en"),
                                                  r["qty"], r["unit"], r["status"].split(";")[0]))
    pns = {r["part_number"][:4]: r["part_number"] for r in rows if r["part_number"]}
    if kind == "panel":
        frame = pns.get("2112") or pns.get("2111")
        skin = pns.get("2114") or pns.get("2113")
        fills = sorted({r["part_number"] for r in rows if r["part_number"][:4] in ("2115", "2116")})
        # before D-120 one fill part; after it the numbered pieces straight in the panel (D-123), cut from DXFs (D-128)
        fill = fills[0] if len(fills) == 1 else "pieces %s, each cut from its DXF (D-128)" % ", ".join(fills)
        cass = "51" + pn[2:]
        notes = [
            "**GENERAL NOTES",
            "1. " + views_note(pos),
            "2. Stack outside to inside: ACP skin 3 (%s), bond line 3 (Sikaflex-252, 12 × 3 on every member), "
            "frame 40 (%s, welded galvanized steel, D-131), PET fill 40 in the bays (%s): outer panel 46. Then the 4 mm gap and the lining "
            "cassette 34 (%s, a separate part): 84 in all." % (skin, frame, fill, cass),
            "3. Site joints (joints register): %s Seam gap 2.26 at each stopped joint, set by the 1.5 mm stop washers."
            % JOINTS.get(pos["code"], ""),
            "4. Factory fits: rivnuts with stop washers, the spigots in the top rail, the captive bolts with their "
            "retainers (HOLD-02), the gaskets on the nut-side faces (PORON 4701-40, HOLD-05)%s. Fill pockets 60 × 60 "
            "left open beside every bolt this panel drives." % (
                ", the closing-seam bulb seal (HOLD-12)" if pos["code"] in ("B2", "B4") else ""),
            "5. Bond: panel bonded face down on a flat table; no standing, stacking or shipping before 72 h (bond spec).",
            "6. Frame welded at the corners (mitre plates) and the T joints (D-131). HOLD: retainer (HOLD-02), torque (HOLD-01), gasket "
            "converter (HOLD-05).",
        ]
    else:
        tray = pns.get("5112") or pns.get("5111")
        felt = pns.get("5114") or pns.get("5113")
        if pos["back"]:
            run = ("It runs from the side lining's face to 1.13 short of X 0: a 2.26 gap to the next back cassette with "
                   "the soft edge seal H-14 (PM ruling 2026-10-31).")
        else:
            run = ("It runs from the decor back plate (pod Y -645) to past the back lining's face (Y 800), closing the "
                   "inside corner (D-57).")
        if pos["row"] == 2:
            run += " The upper cassette floats 4 mm under the ceiling frame (D-57)."
        notes = [
            "**GENERAL NOTES",
            "1. " + views_note(pos),
            "2. Floating inner leaf (D-17): tray %s (0.5 mm, 34 mm returns, 12 mm lips) holds the 9 mm felt %s behind "
            "its lips over a 24 mm air gap. It hangs on captive clips with a rated load (D-47), never a screw; 4 mm "
            "clear of the frame." % (tray, felt),
            "3. Clips HOLD (H03): 4 zones reserved on the panel frame's first and last studs, 100 from the top and "
            "bottom, clear of every key access hole and fill pocket.",
            "4. Hook-and-loop only to line it up (D-47). Where it meets another cassette, the very soft edge seal "
            "848012 only touches across the 2.26 gap (R-J18, HOLD-13).",
            "5. " + run + " Cables in the air gap clip to the tray only (D-26).",
        ]
    for line in el_lines(rep, pos, kind):
        notes.append("%d. %s" % (len(notes), line))
    return [("data", data, 150.0, None), ("parts", plist, 150.0, None), ("notes", notes, 150.0, None)]


def main(argv):
    kind, pn = argv[1], argv[2]
    src = argv[3] if len(argv) > 3 else None      # read another design's report (the part sits in it too)
    if kind in ("panel", "cassette"):
        blocks = assembly_blocks(pn, kind, src)
    else:
        if kind == "fill":
            raise SystemExit("no fill drawing: the fill pieces are cut from their DXFs (D-128); see FILL-PIECES.md")
        blocks = {"frame": frame_blocks, "frame_back": frame_blocks, "skin": skin_blocks,
                  "tray": tray_blocks}[kind](pn, src)
    meta = {}
    for name, lines, width, title in blocks:
        path, w, h = render("%s_%s" % (pn, name), lines, width, title=title)
        meta[name] = {"path": path, "w_mm": w, "h_mm": h}
        print("%s: %.1f x %.1f mm -> %s" % (name, w, h, os.path.relpath(path, HERE)))
    with open(os.path.join(IMG, "%s_images.json" % pn), "w") as fh:
        json.dump(meta, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv)
