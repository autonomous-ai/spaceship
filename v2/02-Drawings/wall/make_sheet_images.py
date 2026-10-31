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


def frame_blocks(pn, src=None):
    rep = load(src or pn)
    pos = position(rep)
    frame = comp_of(rep, pn)
    bodies = sorted(frame["bodies"], key=lambda b: b["name"])
    prm = {p["name"]: p["value"] for p in rep["parameters"]}
    mass = sum(b["mass_kg"] for b in bodies)
    bx = box_of(bodies)
    cut = {}
    for b in bodies:
        d = sorted(round(b["box"][i + 3] - b["box"][i], 2) for i in range(3))
        wall = prm.get("stud_t", 1.0) if b["name"].startswith("STILE - MID") else prm.get("tube_t", 1.2)
        sec = "%s × %.1f" % ("40 × 40" if d[0] >= 39.9 else "20 × 40", wall)
        key = (b["name"].rstrip("0123456789 ").strip(), sec, d[2])
        cut[key] = cut.get(key, 0) + 1
    data = data_block(pn, frame, rep, "1:5", "A2", "aluminium tube 6063-T6, mill finish (D-79)", mass)
    if pos["back"]:
        seam_x = bx[3] if not pos["right"] else bx[0]
        datums = ("2. Datums. A = bottom face of the bottom rail (pod Z %.2f, on the %s). B = the closing-seam face "
                  "of the centre stile (pod X %.2f: half the 5.5 closing gap, R-J11), the drawing's %s edge. C = outer "
                  "face (pod Y %.2f, bonded to the skin)." % (bx[2], "base band" if pos["row"] == 1 else "lower panel",
                                                                seam_x, "left" if pos["right"] else "right", bx[4]))
        holes = ("3. Hole tables: one per drilled face, origin at datum B's lower corner of that view, X/Y in mm. "
                 "Ø7.0 = M6 bolt clearance (captive M6 × 16 ISO 4762 with an ISO 7093-1 washer): bottom rail, outer "
                 "stile (corner)%s. Ø19 = key access and grommet retainer. Ø9.53 +0.10/0 = Sherex CAH3-610-4.2 rivnut: "
                 "top rail%s. %s Ø8.5 round by the closing seam and the 8.5 × 14 slot along the edge at the corner end "
                 "= locating spigots (ST-02). Bolts at 220, 473.00, 725.99, 978.99 from the frame's ends; corner bolts "
                 "at 220, 559.31, 898.61 on Y 824. Reasons: FEATURE-RATIONALE-%s.md." % (
                     ", top rail (ceiling)" if pos["row"] == 2 else "",
                     " (4 for the panel above with stop washers, 2 spigot)" if pos["row"] == 1 else " (2 spigot, for the ceiling)",
                     "Centre stile: 3 plain Ø7.0 that the next panel's pins pass through." if not pos["right"] else
                     "Centre stile: 3 Ø9.53 pin rivnuts (no stop washer) with Ø19 access behind them.",
                     rep["document"].split("_")[0].replace("2112", "2102")))
        extra = "1 × 45° lead-in on the top edge of the closing-seam face (R-J9). "
    else:
        datums = ("2. Datums. A = bottom face of the bottom rail (pod Z %.2f, on the %s). B = front face of the front "
                  "stile (pod Y %.2f, 2.26 seam to the decor block), the drawing's %s edge. C = outer face (pod X %.0f, "
                  "bonded to the skin)." % (bx[2], "base band" if pos["row"] == 1 else "lower panel", bx[1],
                                            "right" if pos["right"] else "left", bx[0] if not pos["right"] else bx[3]))
        holes = ("3. Hole tables: one per drilled face, origin at datum B's lower corner of that view, X/Y in mm. "
                 "Ø7.0 = M6 bolt clearance (captive M6 × 16 ISO 4762 with an ISO 7093-1 washer). Ø19 = key access "
                 "and grommet retainer. Ø9.53 +0.10/0 = Sherex CAH3-610-4.2 rivnut over a 1.5 mm stop washer. Ø8.5 "
                 "and the 8.5 × 14 slot (along X) = locating spigots. Bolts at the 220 rule on every edge; corner "
                 "rivnuts on the bolt line Y 824 (pod)%s. Reasons: FEATURE-RATIONALE-%s.md." % (
                     "; ceiling rivnuts on Z 2374 from Y -645 at 351.67 (the ceiling's rule)" if pos["row"] == 2 else "",
                     rep["document"].split("_")[0].replace("2111", "2101")))
        extra = ""
    notes = [
        "**GENERAL NOTES",
        "1. " + views_note(pos),
        datums,
        holes,
        "4. Hole position Ø0.4 (±0.2) from the round spigot hole in the bottom rail, by CNC or drill jig (F-009).",
        "5. Cut list (square ends, tube 6063-T6; studs 1.0 wall, D-85): " + "; ".join(
            "%s %s × %g × %d" % (k[0], k[1], k[2], q) for k, q in sorted(cut.items())) + ".",
        "6. Member joints HOLD (H11): butt joints shown, rails run the full length. %sCut lengths ±0.5 "
        "(assumption) until the frame maker's capability is known (guideline 6.3)." % extra,
        "7. Rivnuts and stop washers are set at the factory (see the panel assembly). HOLD: member joints (H11), "
        "captive bolt retainer (HOLD-02), torque (HOLD-01). P01 DRAFT.",
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
            "back end at the corner (D-55). Fold allowance 0 and the groove rest thickness: HOLD H16." % (
                ret + length, height, pn, length, ret),
        ]
    table = ["**TABULATED DRAWING (D-89): ONE SHAPE, THESE PART NUMBERS (part · position · hand · size)"] + \
        tab_rows("skin", pos["back"]) + ["Shown: %s. %s" % (pn, "All four are the same flat rectangle, except 211402 "
                                                          "(B2): two Ø24 holes for ELECTRICAL's inlet and LAN, placed "
                                                          "on the panel drawing 210202 and in its DXF." if pos["back"]
                                                          else "RH is the mirror of LH; L1 = L2 and R1 = R2.")]
    notes = ["**GENERAL NOTES", "1. " + views_note(pos)] + body + [
        "4. Bond to the frame: SikaTack Panel-50, one 12 × 3 joint on every frame member, laid face down on a flat "
        "table with the ACP face as datum (bond spec, joints register; in-line tape HOLD-B2).",
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


def fill_blocks(pn, src=None):
    """Cavity fill (D-89: the fill bays have pockets, so they get a drawing; one tabulated drawing per family).
    Pocket positions come from the panel's own frame: one 60 x 60 x 40 pocket beside each Ø19 access hole,
    given from datum A (the fill's bottom face) and datum B (its front edge on a side panel, its closing-seam
    edge on a back panel)."""
    rep = load(src or pn)
    pos = position(rep)
    c = comp_of(rep, pn)
    bodies = c["bodies"]
    fb = box_of(bodies)
    mass = sum(b["mass_kg"] for b in bodies)
    panel = load(("2101" if pn.startswith("2115") else "2102") + pn[4:])
    frame = [k for k in panel["components"] if k["part_number"].startswith(("2111", "2112"))][0]
    prm = {q["name"]: q["value"] for q in panel["parameters"]}
    pw = prm.get("pocket_w", 60.0)
    along = 0 if pos["back"] else 1                      # x for the back wall, y for a side wall
    if pos["back"]:
        b_edge = fb[3] if not pos["right"] else fb[0]    # the closing-seam edge of the fill
    else:
        b_edge = fb[1]                                   # the front edge
    a_edge, height = fb[2], fb[5] - fb[2]
    width = fb[3 + along] - fb[along]
    rows = []
    for b in frame["bodies"]:
        for h in b["holes"]:
            if abs(h["d"] - prm.get("access_d", 19.0)) > 0.01 or not h["full_circle"]:
                continue
            ctr = h["centre"]
            if b["name"] in ("RAIL - BOTTOM", "RAIL - TOP"):
                u = abs(ctr[along] - b_edge)
                v = (0.0, pw) if b["name"] == "RAIL - BOTTOM" else (height - pw, height)
                kind = "bottom bolt" if b["name"] == "RAIL - BOTTOM" else "ceiling bolt"
                rows.append((kind, (u - pw / 2, u + pw / 2), v))
            else:
                z = ctr[2] - a_edge
                at_b = b["name"] in ("STILE - FRONT", "STILE - CENTRE")
                kind = {"STILE - FRONT": "decor bolt", "STILE - CENTRE": "closing-seam pin",
                        "STILE - OUTER": "corner bolt"}.get(b["name"], b["name"])
                rows.append((kind, (0.0, pw) if at_b else (width - pw, width), (z - pw / 2, z + pw / 2)))
    rows.sort(key=lambda r: (r[0], r[1][0], r[2][0]))
    data = data_block(pn, c, rep, "1:5", "A2", "PET fill 40 mm, 24 kg/m³, Pyrotek Sorberpoly 2D (HW-SEL B)", mass)
    notes = [
        "**GENERAL NOTES",
        "1. " + views_note(pos),
        "2. Datums. A = bottom face of the pieces (pod Z %.2f, on the bottom rail). B = the %s (pod %s %.2f). "
        "Pieces are knife-cut to the bays between the studs, 40 thick, friction fit (D-34)." % (
            a_edge, "closing-seam edge" if pos["back"] else "front edge", "X" if pos["back"] else "Y", b_edge),
        "3. %d pieces, %s; overall %.2f × %.2f × 40. Tolerance ±2 on length and width (assumption: knife-cut PET "
        "batt), thickness as supplied." % (len(bodies), "; ".join(sorted({"%.1f × %.1f" % tuple(sorted(
            (bb["box"][3 + along] - bb["box"][along], bb["box"][5] - bb["box"][2]), reverse=True)) for bb in bodies})),
            width, height),
        "4. Pockets: 60 × 60 × 40 left out beside each bolt this panel drives, so the 5 mm key reaches its Ø19 access "
        "hole from inside before the cassette goes on (joints register FR-10, 2.3). Positions below, in mm from B "
        "(along the panel) and A (up).",
    ]
    pockets = ["**POCKETS (kind · from B · from A), each 60 × 60 × 40 through the fill"] + [
        "%s · %.2f–%.2f · %.2f–%.2f" % (k, u[0], u[1], v[0], v[1]) for k, u, v in rows]
    if pos["back"]:
        tab = ["**TABULATED DRAWING (D-89): THE BACK FILLS (part · position · pockets)",
               "211601 · B1 · as shown: bottom bolts, corner bolts",
               "211602 · B2 · as B1 (mirrored), plus 3 closing-seam pin pockets at B, at the corner pockets' heights; "
               "the first bay left out for ELECTRICAL's power unit, sleeve and connectors (panel drawing 210202, F47)",
               "211603 · B3 · as B1, plus 4 ceiling bolt pockets at the top, at the bottom pockets' positions from B",
               "211604 · B4 · as B3 (mirrored), plus the 3 closing-seam pin pockets"]
    else:
        tab = ["**TABULATED DRAWING (D-89): THE SIDE FILLS (part · position · hand)",
               "211501 · L1 · LH · as shown", "211502 · R1 · RH · mirror of 211501",
               "211503 · L2 · LH · same as 211501 (the upper panel's bolts and pockets sit at the same places)",
               "211504 · R2 · RH · mirror of 211501"]
    return [("data", data, 150.0, None), ("notes", notes, 150.0, None), ("pockets", pockets, 150.0, None),
            ("table", tab, 150.0, None)]


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
        fill = pns.get("2116") or pns.get("2115")
        cass = "51" + pn[2:]
        notes = [
            "**GENERAL NOTES",
            "1. " + views_note(pos),
            "2. Stack outside to inside: ACP skin 3 (%s), bond line 3 (SikaTack Panel-50, 12 × 3 on every member), "
            "frame 40 (%s, 6063-T6), PET fill 40 in the bays (%s): outer panel 46. Then the 4 mm gap and the lining "
            "cassette 34 (%s, a separate part): 84 in all." % (skin, frame, fill, cass),
            "3. Site joints (joints register): %s Seam gap 2.26 at each stopped joint, set by the 1.5 mm stop washers."
            % JOINTS.get(pos["code"], ""),
            "4. Factory fits: rivnuts with stop washers, the spigots in the top rail, the captive bolts with their "
            "retainers (HOLD-02), the gaskets on the nut-side faces (PORON 4701-40, HOLD-05)%s. Fill pockets 60 × 60 "
            "left open beside every bolt this panel drives." % (
                ", the closing-seam bulb seal (HOLD-12)" if pos["code"] in ("B2", "B4") else ""),
            "5. Bond: panel bonded face down on a flat table; no standing, stacking or shipping before 72 h (bond spec).",
            "6. HOLD: member joints (H11), retainer (HOLD-02), torque (HOLD-01), gasket converter (HOLD-05).",
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
        blocks = {"frame": frame_blocks, "frame_back": frame_blocks, "skin": skin_blocks,
                  "tray": tray_blocks, "fill": fill_blocks}[kind](pn, src)
    meta = {}
    for name, lines, width, title in blocks:
        path, w, h = render("%s_%s" % (pn, name), lines, width, title=title)
        meta[name] = {"path": path, "w_mm": w, "h_mm": h}
        print("%s: %.1f x %.1f mm -> %s" % (name, w, h, os.path.relpath(path, HERE)))
    with open(os.path.join(IMG, "%s_images.json" % pn), "w") as fh:
        json.dump(meta, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv)
