"""Assembly drawings for ELECTRICAL's harness and zone assemblies, generated from
the same tables as the parts list and harness list (A2, one sheet each):

    710001 power unit (face layout 1:3 and depth section, parts, leads)
    710011, 710021, 710023, 710024 harnesses (segments, formboard, plugs, test)
    710031 draw wire set
    710041 hub and controls zone (plate layout 1:1, parts)

A harness is defined by its segments, plugs, lengths and test, not by a
projection, so these sheets are drawn from checked data (guideline 6.1), not
from a mesh. The folded enclosure body 711001 has its own Fusion drawing; the
flat plates 711002 and 711005 are defined by their DXF and parts-list row
(D-89 part 4). Called by electrical_docs.py.

Every letter is at least 2.5 mm high (titles 3.5; sheet_kit.py), tables wrap
their cells instead of cutting a value short, view labels go where no line runs
through them, and each sheet is checked for overlapping text before it's saved.
"""

import re

import electrical_model as M
import electrical_parts as EP
import fitz
import sheet_kit as K
from sheet_kit import GREY, INK, MAINS, SELV, SIG

DATE = "2026-11-01"
SOURCE = "electrical_model.py, electrical_parts.py"
COMMON_NOTES = [
    "UNITS: mm. GENERAL TOLERANCE: harness segment lengths +20/-0 mm; positions taken from the route model +/-5 mm;",
    "sheet-metal parts ISO 2768-m (their DXF or drawing rules). Status of every number: parts list and harness list.",
    "Every harness segment is tested in the factory before it ships (D-87): continuity, polarity, no shorts, latch pull,",
    "label with its ID. Cables clip to the cassette tray only (D-26). Supply side = receptacle (female contacts).",
    "Bought parts are named from their datasheets (those still on HOLD give their reason in the parts list 710000); "
    "no order, no supplier contact. From the electrical model and parts data.",
]


def children(pn):
    return [(k, p) for k, p in EP.P.items() if p["parent"] == pn]


def frame(s, pn, name, notes, scale="see views"):
    """Frame, title block and notes; returns the lowest y the content may use."""
    return s.frame_and_title(name, "%s  (assembly)" % pn, 1, 1, scale, DATE, SOURCE, list(notes) + COMMON_NOTES) - 2.0


def plug(s, x, y, color=INK, k=2.0):
    """A plug pair, as on the wiring diagram, k times its size there."""
    s.line(x - 1.6 * k, y - 1.4 * k, x - 0.4 * k, y - 1.4 * k, color, 0.3)
    s.line(x - 0.4 * k, y - 1.4 * k, x - 0.4 * k, y + 1.4 * k, color, 0.3)
    s.line(x - 1.6 * k, y + 1.4 * k, x - 0.4 * k, y + 1.4 * k, color, 0.3)
    s.line(x + 0.4 * k, y - 1.0 * k, x + 0.4 * k, y + 1.0 * k, color, 0.5)


def product(pn):
    """The named product's maker and number for a callout, or HOLD."""
    return EP.PRODUCTS[pn][0] if pn in EP.PRODUCTS else "HOLD"


def sheet_status(status):
    """A bought line held with its reason shows HOLD here and keeps the reason in the parts list (710000)."""
    if status.startswith("HOLD (") and status != EP.HOLD_BUY:
        return "HOLD: the reason is in the parts list 710000"
    return status


def parts_table(s, pn, x, y, w, bottom, shares=(0.27, 0.27, 0.46)):
    """The assembly's parts list lines, every value in full (cells wrap); shares: the name, material and status
    columns' parts of the width the fixed columns leave."""
    s.text(x, y, "PARTS OF %s" % pn, K.TITLE, INK, True)
    named = [("ITEM", 12), ("PART NO.", 20), ("NAME", shares[0]), ("QTY", 14), ("UNIT", 12),
             ("MATERIAL / FINISH", shares[1]), ("STATUS", shares[2])]
    fixed = sum(c for _n, c in named if c > 1)
    cols = [(n, c if c > 1 else (w - fixed) * c) for n, c in named]
    rows = [[str(i), p["part_number"], p["name"], str(p["qty_per_parent"]), EP.unit_of(k),
             ", ".join(t for t in (p["material"], p["finish"]) if t) or "as supplied", sheet_status(p["status"])]
            for i, (k, p) in enumerate(children(pn), start=1)]
    y, left = s.table(x, y + 2.0, cols, rows, bottom)
    if left:
        raise ValueError("the parts of %s need another sheet: %d rows left" % (pn, len(left)))
    return y


def harness_table(s, rows, x, y, w, bottom):
    s.text(x, y, "SEGMENTS", K.TITLE, INK, True)
    named = [("ID", 16), ("CARRIER", 30), ("FROM", 0.15), ("TO", 0.15), ("CABLE", 0.14), ("L mm", 16), ("END A", 0.28),
             ("END B", 0.28)]
    fixed = sum(c for _n, c in named if c > 1)
    cols = [(n, c if c > 1 else (w - fixed) * c) for n, c in named]
    vals = [[h["id"], h["segment"], h["from"], h["to"], h["cable"], str(h["length_mm"]), h["end_a"], h["end_b"]] for h in rows]
    y, left = s.table(x, y + 2.0, cols, vals, bottom)
    if left:
        raise ValueError("the segments need another sheet: %d rows left" % len(left))
    return y


def colour(h):
    return MAINS if "mains" in h["circuit"] else (SIG if h["circuit"] in ("hub I/O", "LAN", "hub sensor", "hub input") else SELV)


RATIOS = (1, 2, 2.5, 5, 10, 20)           # formboard scales (Reviewer 7: print the ratio)


def formboard_ratio(rows, width):
    """The largest standard scale (1:r) at which the longest segment fits the formboard's width."""
    longest = max(h["length_mm"] for h in rows) or 1
    return next(r for r in RATIOS if longest / r <= width - 30.0)


def end_kind(text):
    t = text.lower()
    if "tied" in t:
        return "tie"
    if any(k in text for k in ("Mini-Fit", "RJ45", "keystone")) or any(k in t for k in ("plug", "receptacle", "coupler",
                                                                                          "connector", "lug", "punched")):
        return "strip" if "strip feed" in t and "Mini-Fit" not in text else "plug"
    if "strip feed" in t:
        return "strip"
    return "end"


def end_mark(s, x, y, kind, col):
    """plug: the plug pair; strip: an open ring, the clip-on feed lead onto the strip; tie: a cross, the cord tied off;
    end: a short stroke (a terminal or a part HOLD)."""
    if kind == "plug":
        plug(s, x, y, col)
    elif kind == "strip":
        s.circle(x, y, 1.6, col, 0.4)
    elif kind == "tie":
        s.line(x - 1.8, y - 1.8, x + 1.8, y + 1.8, col, 0.4)
        s.line(x - 1.8, y + 1.8, x + 1.8, y - 1.8, col, 0.4)
    else:
        s.line(x, y - 2.0, x, y + 2.0, col, 0.5)


def formboard(s, rows, x, y, width):
    """Each segment as a line at the formboard's scale, each end drawn as what it is."""
    r = formboard_ratio(rows, width)
    tied = all(end_kind(h["end_a"]) == "tie" for h in rows)
    s.text(x, y, "FORMBOARD 1:%g (lengths to scale along the line; %s)" % (
        r, "cords tied off at both ends" if tied else "a plug pair, a strip feed ring or a stroke at each end"),
        K.TITLE, INK, True)
    x0 = x + 22.0
    pitch = 11.0
    for i, h in enumerate(rows):
        yy = y + 12.0 + i * pitch
        L = h["length_mm"] / r
        col = colour(h)
        s.text(x, yy + 0.9, h["id"], K.BODY, col, True)
        s.line(x0, yy, x0 + L, yy, col, 0.6)
        end_mark(s, x0, yy, end_kind(h["end_a"]), col)
        end_mark(s, x0 + L, yy, end_kind(h["end_b"]), col)
        s.text(x0 + 6.0, yy - 3.9, "%d mm  %s" % (h["length_mm"], h["cable"]), K.BODY, col)   # clear of the end marks
    return y + 12.0 + len(rows) * pitch


def plate_params():
    """The front plate's own build parameters (electrical_parts_cad.py PARTS["front"]), evaluated the way Fusion
    does, without Fusion (a stub stands in for the two adsk names that file reads when it loads)."""
    import sys
    import types
    if "adsk" not in sys.modules:
        adsk = types.ModuleType("adsk")
        core, fusion = types.ModuleType("adsk.core"), types.ModuleType("adsk.fusion")
        fusion.DimensionOrientations = types.SimpleNamespace(HorizontalDimensionOrientation=0, VerticalDimensionOrientation=1)
        adsk.core, adsk.fusion = core, fusion
        sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.fusion": fusion})
    import electrical_parts_cad as C
    vals = {}
    for n, expr, _u, _s, _src in C.PARTS["front"][4]:
        vals[n] = M.evaluate(expr, dict(vals))
    return vals


def tag(s, cx, cy, t, col):
    """A short tag centred in an opening (Reviewer 7: labels inside their boxes)."""
    s.text(cx - s.text_w(t, K.BODY, True) / 2, cy + K.BODY * K.CAP / 2, t, K.BODY, col, True)


def sheet_power_unit(doc, v):
    s = K.Sheet(doc, "A2")
    p = plate_params()
    pn = "710001"
    bottom = frame(s, pn, "ELECTRICAL - POWER UNIT - B2: ASSEMBLY", [
        "Wiring inside the unit: wiring diagram sheet 1 (710000). Leads out: W10a top (6-way), W20a/W24a/W30a/W31a right side.",
        "Factory test of the unit before B2 ships (US 120 V, D-133): ground continuity <= 0.1 ohm; dielectric withstand 1240 V AC "
        "for 1 min, mains to ground (1000 V + 2 x 120 V); the GFCI's TEST button trips it; rails 24 V (PS1, PS2) and 12 V (PS3) +/-3 %.",
    ], scale="1:3 face, 2:1 section (schematic)")
    k = 1.0 / 3.0
    ox, oy = 24.0, 128.0
    W, Hh = p["w"], p["h"]                  # the front plate, which covers the cut-out's felt edge
    X = lambda x: ox + x * k                # noqa: E731  plate mm -> sheet mm
    Z = lambda z: oy - z * k                # noqa: E731
    s.text(ox, 22, "FACE OF THE POWER UNIT, seen from inside the pod (looking toward +Y), 1:3", K.TITLE, INK, True)
    s.rect(X(0), Z(Hh), X(W), Z(0), INK, 0.5)
    gx, zc = p["gfci_x"], p["dev_zc"]
    s.rect(X(gx - p["gfci_w"] / 2), Z(zc + p["gfci_h"] / 2), X(gx + p["gfci_w"] / 2), Z(zc - p["gfci_h"] / 2), MAINS, 0.3)
    for sign in (-1, 1):
        s.circle(X(gx), Z(zc + sign * p["gfci_sp"] / 2), p["gfci_sd"] / 2 * k, INK, 0.2)
    ks = [p["ks_x"] - p["ks_p"] / 2, p["ks_x"] + p["ks_p"] / 2]
    for kx in ks:
        s.rect(X(kx - p["ks_w"] / 2), Z(zc + p["ks_h"] / 2), X(kx + p["ks_w"] / 2), Z(zc - p["ks_h"] / 2), SIG, 0.3)
    dw, dh = p["din_w"] / 2, p["din_h"] / 2
    s.rect(X(p["din_x"] - dw), Z(p["din_zc"] + dh), X(p["din_x"] + dw), Z(p["din_zc"] - dh), MAINS, 0.3)
    for vz in (p["vent_z1"], p["vent_z2"]):
        for i in range(int(p["vent_n"])):
            xc = W / 2 + (i - (p["vent_n"] - 1) / 2) * p["vent_p"]
            s.rect(X(xc - p["vent_l"] / 2), Z(vz + p["vent_w"] / 2), X(xc + p["vent_l"] / 2), Z(vz - p["vent_w"] / 2), GREY, 0.2)
    sx_, sy_ = p["screw_x"], p["screw_y"]
    for cx, cy in ((sx_, sy_), (W - sx_, sy_), (sx_, Hh - sy_), (W - sx_, Hh - sy_)):
        s.circle(X(cx), Z(cy), p["screw_d"] / 2 * k, INK, 0.2)
    tag(s, X(gx), Z(zc), "1", MAINS)
    for kx in ks:
        tag(s, X(kx), Z(zc), "2", SIG)
    tag(s, X(p["din_x"]), Z(p["din_zc"]), "3", MAINS)
    lx = X(W) + 10.0
    y = 42.0
    for t, col in (("1  GFCI receptacle, tamper-resistant duplex NEMA 5-15R, UL 943 Class A (718007, %s)" % product("718007"),
                    MAINS),
                   ("    in a decorator opening %.1f x %.0f, two 6-32 plate screws %.1f apart (718054)" % (
                       p["gfci_w"], p["gfci_h"], p["gfci_sp"]), INK),
                   ("2  LAN keystone jacks, Cat6, snapped into %.1f x %.1f openings (718040, %s)" % (
                       p["ks_w"], p["ks_h"], product("718040")), SIG),
                   ("3  breaker 1P 15 A, UL 489, through its %.0f x %.0f window (718003, %s)" % (
                       p["din_w"], p["din_h"], product("718003")), MAINS),
                   ("US 120 V 60 Hz, UL-listed parts (D-133)", INK)):
        s.text(lx, y, t, K.BODY, col)
        y += s.line_pitch(K.BODY)
    s.para(ox, oy + 6.0, "Plate %.0f x %.0f over the unit (X %.0f-%.0f, Z %.0f-%.0f in the pod), 2 mm off the felt; 4 x M4 at "
           "%.0f / %.0f from the plate's edges." % (W, Hh, v["pu_x0"], v["pu_x1"], v["pu_z0"], v["pu_z1"], sx_, sy_), 250.0)
    # depth section
    sx, sy = 330.0, 30.0
    s.text(sx, 22, "DEPTH SECTION THROUGH B2, 2:1 (toward the skin to the right)", K.TITLE, INK, True)
    layers = [("felt face Y 766", 0), ("cassette 34", 34), ("gap 4", 38), ("frame bay 40", 78), ("bond 3", 81), ("ACP 3", 84)]
    for _lab, d in layers:
        s.line(sx + d * 2, sy + 2, sx + d * 2, sy + 60, GREY, 0.2)
    s.rect(sx, sy + 15, sx + v["pu_d"] * 2, sy + 45, MAINS, 0.5)
    s.label(sx + 3, sy + 31, "power unit, %.0f deep" % v["pu_d"], K.BODY, MAINS)
    down = [(0.0, 4.6 * i) for i in range(8)]
    for lab, d in layers:                                 # each under its line, stepped down where they'd meet
        s.label(sx + d * 2 + 0.6, sy + 65, lab, K.BODY, GREY, around=down)
    s.para(sx, sy + 108, "Unit fixed to B2's frame (fixing HOLD, WALL IF-12); cassette cut-out 4 mm clear all round "
           "(floating lining).", 230.0)
    parts_table(s, pn, 24, 160, 546, bottom, shares=(0.44, 0.30, 0.26))   # the bought names carry maker and number
    # a face view and a section (Reviewer 7): the symbol sits under the section, since the parts list (longer with the
    # named products and D-168's supplies) now reaches the title block
    s.first_angle_symbol(s.W - 10 - 45, 152)
    return s


def sheet_hub(doc, v):
    s = K.Sheet(doc, "A2")
    pn = "710041"
    bottom = frame(s, pn, "ELECTRICAL - HUB AND CONTROLS ZONE: ASSEMBLY", [
        "Hub window, button and knob holes, fixing holes: HOLD until the hub's size (ISS-060) and CEILING's column fixing.",
    ], scale="1:1")
    ox, oy = 30.0, 222.0
    w = v["hub_w"]
    s.text(ox, 24, "HUB AND CONTROLS ZONE PLATE 711005, seen from the pod, 1:1", K.TITLE, INK, True)
    s.rect(ox, oy - w, ox + w, oy, INK, 0.5)
    s.rect(ox + w / 2 - 60, oy - 125 - 35, ox + w / 2 + 60, oy - 125 + 35, SIG, 0.4)
    for i in range(3):
        s.circle(ox + 30 + i * 40, oy - 50, 8.1, INK, 0.3)
    s.circle(ox + 150, oy - 50, 3.75, INK, 0.3)
    for cx, cy in ((10, 10), (w - 10, 10), (10, w - 10), (w - 10, w - 10)):
        s.circle(ox + cx, oy - cy, 2.25, GREY, 0.2)
    s.label(ox + w / 2 - 25, oy - 124, "HUB WINDOW (HOLD)", K.BODY, SIG)
    for cx, lab in ((30, "BOOST"), (70, "TEST"), (110, "CALL"), (150, "LIGHT")):    # centred under each (Reviewer 7)
        s.label(ox + cx - s.text_w(lab, K.BODY) / 2, oy - 33, lab, K.BODY, INK, around=[(0, 0)])
    s.para(ox, oy + 7.0, "180 x 180 on the column's back face, X 957-1137, Z 1110-1290; fuses F3a-F3c behind the plate.", 200.0)
    parts_table(s, pn, 236, 30, 334, bottom)
    s.first_angle_symbol(s.W - 10 - K.TB_W + 2, bottom - 14)   # the plate view (Reviewer 7)
    return s


CONNECTOR_PN = [  # text in the harness ends -> part number
    ("Mini-Fit Jr 2-way receptacle", "718030"), ("Mini-Fit Jr 2-way plug", "718031"),
    ("Mini-Fit Jr 4-way receptacle", "718032"), ("Mini-Fit Jr 4-way plug", "718033"),
    ("Mini-Fit Jr 6-way receptacle", "718045"), ("Mini-Fit Jr 6-way plug", "718046"),
    ("Mini-Fit Jr 10-way receptacle", "718034"), ("Mini-Fit Jr 10-way plug", "718035"),
    ("RJ45 inline coupler", "718039"), ("RJ45 keystone jack", "718040"),
]
CABLE_PN = [("4 x 16 AWG", "718055"), ("6 x 18 AWG", "718029"), ("4 x 18 AWG", "718024"), ("2 x 18 AWG", "718023"), ("6 x 24 AWG", "718025"),
            ("4 x 20 AWG", "718026"), ("4 x 24 AWG", "718027"), ("Cat6", "718028"), ("draw cord", "718044")]


def harness_material(s, rows, x, y, w, bottom):
    """This harness's share of the parts list's lines, counted from its segments."""
    names = {p["part_number"]: p["name"] for p in EP.P.values()}
    cables, conns, holes = {}, {}, set()
    for h in rows:
        for txt, pn in CABLE_PN:
            if txt in h["cable"]:
                cables[pn] = cables.get(pn, 0) + h["length_mm"] / 1000.0
                break
        for end in (h["end_a"], h["end_b"]):
            for txt, pn in CONNECTOR_PN:
                if txt in end:
                    conns[pn] = conns.get(pn, 0) + 1
            cap = re.search(r"Mini-Fit Jr (\d+)-way receptacle, capped with an empty plug housing", end)
            if cap:                                       # the cap is a plug housing too (Reviewer 7, 718033 on 710021)
                plug_pn = dict(CONNECTOR_PN)["Mini-Fit Jr %s-way plug" % cap.group(1)]
                conns[plug_pn] = conns.get(plug_pn, 0) + 1
        if EP.STRIP_FEEDS.get(h["id"]):                   # the clip-on strip feed leads (Reviewer 7)
            conns["718053"] = conns.get("718053", 0) + EP.STRIP_FEEDS[h["id"]]
        for g in (h.get("grommets") or "").replace("(", ",").replace(")", ",").split(","):
            g = g.strip()
            if g.startswith(("G-", "S-")):
                holes.add(g.split(" ")[0])
    s.text(x, y, "MATERIAL FOR THIS HARNESS (its share of the parts list lines, counted from the segments above)",
           K.TITLE, INK, True)
    vals = [[pn, names.get(pn, ""), "%s %s" % (qty, unit)] for pn, qty, unit in
            ([(p, round(q, 2), "m") for p, q in sorted(cables.items())] + [(p, q, "pc") for p, q in sorted(conns.items())])]
    y, left = s.table(x, y + 2.0, [("PART NO.", 24), ("NAME", 150), ("QTY", 30)], vals, bottom)
    if left:
        raise ValueError("the material list needs another sheet")
    y += 2.0 + K.BODY * K.CAP
    if holes:
        y = s.para(x, y, "Bushings and edge-protected slots it passes: %s (Heyco 2836N / edge strip Heyco 12431, parts "
                   "list 718041, 718042)." % ", ".join(sorted(holes)), w)
    if any("Mini-Fit" in h["end_a"] + h["end_b"] for h in rows):
        cables_here = " ".join(h["cable"] for h in rows)
        y = s.para(x, y, "Terminals: Mini-Fit Jr female 39-00-0039 (718036) and male 39-00-0041 (718037) on 18 AWG, one per "
                   "way" + ("; the kit feed's 16 AWG: female 39-00-0078 (718056) and male 39-00-0082 (718057)"
                            if "16 AWG" in cables_here else "") +
                   ("; 24 AWG cores: female 39-00-0047 (718077) and male 39-00-0049 (718078)" if "24 AWG" in cables_here
                    else "") + ".", w)
    return y


def sheet_harness(doc, pn, name, rows):
    s = K.Sheet(doc, "A2")
    r = formboard_ratio(rows, 558)
    bottom = frame(s, pn, name + ": ASSEMBLY", [
        "Segments, ends and lengths from the harness list (710000_P01_ELECTRICAL-HARNESS-LIST_SPEC.csv), same revision.",
    ], scale="formboard 1:%g; tables not to scale" % r)
    y = harness_table(s, rows, 16, 24, 558, bottom)
    y = formboard(s, rows, 16, y + 12, 558)
    y = harness_material(s, rows, 16, y + 10, 558, bottom)
    if y > bottom:
        raise ValueError("%s: the sheet's content runs into its notes" % pn)
    return s


def write(out_dir, v, harness):
    by_pn = {}
    for h in harness:
        by_pn.setdefault(h["harness_pn"], []).append(h)
    written = []
    jobs = [("710001", "ELECTRICAL-POWER-UNIT-B2", lambda d: sheet_power_unit(d, v)),
            ("710041", "ELECTRICAL-HUB-AND-CONTROLS-ZONE", lambda d: sheet_hub(d, v))]
    for pn, stem, nm in (("710011", "ELECTRICAL-HARNESS-LIGHT-FEED-B2-B4", "ELECTRICAL - HARNESS - LIGHT FEED - B2/B4"),
                         ("710021", "ELECTRICAL-HARNESS-TRUNK-B2-R1", "ELECTRICAL - HARNESS - TRUNK - B2/R1"),
                         ("710023", "ELECTRICAL-HARNESS-AIR-COLUMN", "ELECTRICAL - HARNESS - AIR COLUMN"),
                         ("710024", "ELECTRICAL-HARNESS-CALL-LIGHT-R2", "ELECTRICAL - HARNESS - CALL LIGHT - R2"),
                         ("710031", "ELECTRICAL-DRAW-WIRE-CEILING-ROUTE", "ELECTRICAL - DRAW WIRE - CEILING ROUTE")):
        jobs.append((pn, stem, (lambda p, n: (lambda d: sheet_harness(d, p, n, by_pn.get(p, []))))(pn, nm)))
    for pn, stem, fn in jobs:
        doc = fitz.open()
        fn(doc).check()                                   # no overlapping text, no line through a text, in the frame
        path = "%s/%s_%s_%s_DWG.pdf" % (out_dir, pn, M.REV, stem)
        doc.set_metadata({"title": "%s %s %s" % (pn, M.REV, stem), "author": "Autonomous",
                          "creator": "Autonomous", "producer": "PyMuPDF",
                          "creationDate": "D:20261101000000", "modDate": "D:20261101000000"})
        doc.save(path, deflate=True, garbage=4, no_new_id=True)
        doc.close()
        written.append(path)
    return written
