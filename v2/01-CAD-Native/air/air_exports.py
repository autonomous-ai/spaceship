"""Offline exports for AIR (610000), from the same parameters as the Fusion build.

    python3 v2/01-CAD-Native/air/air_exports.py BUILD_LOG

BUILD_LOG is the output of a passing `air_build.py` run (masses from its MASS lines).
Writes into v2/03-Manufacturing/air/:

- the parts list for the master BOM (D-87 shipping pieces: the soffit with its exhaust fan
  box fitted, the column, two cartridges, the supply fan box joined with the riser);
- 1:1 mm DXF cut files for the flat parts (plates, rails, the ACP + felt faces with their
  openings), seen from the face's outside, origin at the part's lower left corner;
- size and tolerance in every parts-list row (a parts-list row is the cut list, PM ruling
  2026-11-01; D-89 part 4: flat sheet parts on their DXF and row, ISO 2768-m).

Folded parts (cartridge casings, fan box casings, riser, sleeve) get their sizes and wall in
the parts list; their blanks wait for the factory's bend tables (HOLD).
"""

import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import air_model as A  # noqa: E402
import ceiling_exports as CE  # noqa: E402  (build log parser)
import dxf_tools as D  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "v2", "03-Manufacturing", "air")
REV = A.REV

# BOM tree: key, parent, quantity per parent, source
TREE = [
    ("air", None, 1, "D-60 to D-62, D-87; assembly tree"),
    ("column", "air", 1, "D-60, D-61; PM rulings 2026-11-01 (5 mm off the lining, foot on the mat, hooks on DR)"),
    ("col_foot", "column", 1, "PM ruling 2026-11-01 (BASE's two spigots)"),
    ("col_front", "column", 1, "D-61; air report 7e"), ("col_left", "column", 1, "D-61; air report 7e"),
    ("col_ang", "column", 1, "air report 7e: a set of 3 corner angles, two front 9 x 20 x 2 and the back-left 20 x 20 x 2 with the two keyholes"),
    ("col_side_lo", "column", 1, "PM ruling 2026-11-01 (5 mm off the lining)"),
    ("col_side_hi", "column", 1, "PM ruling 2026-11-01 (5 mm off the lining)"),
    ("col_fill", "column", 1, "air report 7e (2 pieces, see the flat cut list)"),
    ("kick", "column", 1, "D-61 (2 pieces: front and left)"),
    ("hub", "column", 1, "D-61, D-70: 180 x 180 zone for the in-house sensor hub"),
    ("cart", "air", 2, "D-61: one cartridge for both paths, ships on its own, slides in on site"),
    ("casing", "cart", 1, "D-61: 2 mm aluminium casing"), ("layer", "cart", 3, "D-61: three 50 mm layers"),
    ("soffit", "air", 1, "D-60, D-61, D-87: ships with the exhaust fan box fitted"),
    ("sof_under", "soffit", 1, "D-87: hinged section with the exhaust grille's opening"),
    ("sof_under_r", "soffit", 1, "D-87: hinged section"), ("sof_under_f", "soffit", 1, "D-87: fixed over the column"),
    ("sof_front", "soffit", 1, "D-61"), ("sof_rail_d", "soffit", 1, "D-87 hooks, PM ruling 2026-11-01"),
    ("sof_rail_r", "soffit", 1, "D-87 hooks, PM ruling 2026-11-01"), ("sof_end", "soffit", 1, "D-87"),
    ("sof_door", "soffit", 1, "PM ruling 2026-11-01 (HOLD-18): carries the door-side rail on the studs' heads"),
    ("sof_fill", "soffit", 1, "air report 7e (2 pieces, see the flat cut list)"),
    ("egrille", "soffit", 1, "air report 7e: exhaust grille 265 x 336"),
    ("stud", "soffit", 4, "PM ruling 2026-11-01: 4 hanger studs into the ceiling's rivnuts (number from the joints register, D-63)"),
    ("hinge", "soffit", 4, "D-87: hinged underside, 2 per section"), ("latch", "soffit", 4, "D-87: 2 push latches per section"),
    ("ebox", "soffit", 1, "D-87: fitted in the soffit at the factory"),
    ("box", "ebox", 1, "air report 7e: 294 x 314 x 173, 2 mm"), ("fan", "ebox", 2, "PM ruling 2026-11-01: 618401 for all four fans"),
    ("sbox", "air", 1, "D-62, D-87: joined with the intake riser"),
    ("box_s", "sbox", 1, "air report 7e: 300 x 155 x 300, 2 mm"),
    ("fan_sup", "sbox", 2, "PM ruling 2026-11-01: the two supply fans belong to AIR's supply box only (FRONT drops them from DR)", "fan"),
    ("riser", "sbox", 1, "D-61: 1 mm steel"),
    ("trans", "sbox", 1, "air report 7e (opening into the column top)"), ("rtrans", "sbox", 1, "air report 7e"),
    ("sleeve", "air", 1, "D-61: through C2's roof slot"), ("rgrille", "air", 1, "D-61"),
]
FINISH = {"col_front": "ACP EV3038 face with Dark Gray felt (D-79)", "col_left": "ACP EV3038 face with Dark Gray felt (D-79)",
          "sof_under": "top band's dark tone (D-60)", "sof_under_r": "top band's dark tone (D-60)",
          "sof_under_f": "top band's dark tone (D-60)", "sof_front": "felt face, Dark Gray (D-79)",
          "kick": "powder coat to match the felt (HOLD)", "egrille": "powder coat to match the underside (HOLD)",
          "rgrille": "powder coat to match the roof (HOLD)", "col_foot": "mill finish (hidden, D-79)",
          "col_ang": "mill finish (hidden, D-79)", "col_side_lo": "mill finish (hidden, D-79)",
          "col_side_hi": "mill finish (hidden, D-79)", "sof_rail_d": "mill finish (hidden, D-79)",
          "sof_rail_r": "mill finish (hidden, D-79)", "sof_end": "mill finish (hidden, D-79)",
          "sof_door": "mill finish (hidden, D-79)",
          "casing": "mill finish (hidden, D-79)", "box": "mill finish (hidden, D-79)", "box_s": "mill finish (hidden, D-79)",
          "riser": "galvanised", "sleeve": "galvanised"}
PROCESS = {"col_foot": "laser cut", "col_side_lo": "laser cut", "col_side_hi": "laser cut", "col_ang": "extruded angle, cut, keyholes milled",
           "sof_rail_d": "laser cut flat bar, forks and holes", "sof_rail_r": "laser cut flat bar, forks", "sof_end": "laser cut",
           "col_front": "CNC routed ACP, felt laminated", "col_left": "CNC routed ACP, felt laminated",
           "sof_under": "CNC routed ACP, felt laminated", "sof_under_r": "CNC routed ACP, felt laminated",
           "sof_under_f": "CNC routed ACP, felt laminated", "sof_front": "CNC routed ACP, felt laminated",
           "kick": "perforated sheet, cut", "egrille": "perforated sheet, cut", "rgrille": "perforated sheet, cut",
           "casing": "sheet metal: cut, folded into a tube (blank HOLD: the factory's bend table)",
           "box": "sheet metal: cut, folded, riveted (blank HOLD)", "box_s": "sheet metal: cut, folded, riveted (blank HOLD)",
           "riser": "sheet metal: cut, folded into a tube (blank HOLD)", "sleeve": "sheet metal: cut, folded into a tube (blank HOLD)",
           "col_fill": "knife cut", "sof_fill": "knife cut", "layer": "knife cut"}
HOLD_MASS = {"hub": (0.0, "assumption: space only (in-house module, its mass is ELECTRICAL's)"),
             "trans": (1.89, "calculation: 0.35 m2 of 2 mm aluminium, the air report's sizing (D-60, 7f), until the AIR "
                       "follow-up designs it into FRONT's reserved space"),
             "rtrans": (1.47, "calculation: a 1 mm galvanised steel duct of 0.187 m2, from the riser's top (139 x 155) to the "
                        "fan box's bottom (300 x 155) over 205, FRONT's reserved space, until the AIR follow-up designs it"),
             "stud": (0.012, "assumption: an M6 shoulder stud, about 12 g"),
             "hinge": (0.04, "assumption: a small concealed hinge, about 40 g"),
             "latch": (0.02, "assumption: a push latch, about 20 g")}


def fname(key, doctype, ext):
    pn, name, _vn, _k, _m = A.PARTS[key]
    return "%s_%s_%s_%s.%s" % (pn, REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype, ext)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def boxes(v):
    return {name: [A.ev(v, e) for e in bx] for _k, name, bx in A.layout()}


def write_dxfs(v):
    """Flat parts, each in its own face plane: XY (plates seen from above, rails), YZ (seen from
    the -X side) or XZ (seen from the room, +Y looking -Y); origin at the lower left."""
    L = boxes(v)
    out = {}

    def plane_of(b):
        d = (b[1] - b[0], b[3] - b[2], b[5] - b[4])
        return "xy" if d[2] <= min(d[0], d[1]) else ("yz" if d[0] <= d[1] else "xz")

    def to2d(b, plane, x, y, z):
        if plane == "xy":
            return x - b[0], y - b[2]
        if plane == "yz":
            return y - b[2], z - b[4]
        return x - b[0], z - b[4]

    feats = {}
    for bname, kind, a in A.features():
        feats.setdefault(bname, []).append((kind, [A.ev(v, e) for e in a]))
    cuts = {}
    for target, cb in A.cutouts():
        cuts.setdefault(target, []).append([A.ev(v, e) for e in cb])
    for key, bodies in (("col_foot", ["COLUMN FOOT PLATE"]), ("col_side_lo", ["COLUMN PLENUM PLATE LOW"]),
                        ("col_side_hi", ["COLUMN PLENUM PLATE HIGH"]), ("sof_rail_d", ["SOFFIT RAIL DOOR"]),
                        ("sof_rail_r", ["SOFFIT RAIL ROOM"]), ("sof_end", ["SOFFIT END PLATE LEFT"]),
                        ("sof_door", ["SOFFIT DOOR PLATE"]),
                        ("col_front", ["COLUMN FACE FRONT"]), ("col_left", ["COLUMN FACE LEFT"]),
                        ("sof_under", ["SOFFIT UNDERSIDE LEFT"]), ("sof_under_r", ["SOFFIT UNDERSIDE RIGHT"]),
                        ("sof_under_f", ["SOFFIT UNDERSIDE FIXED"]), ("sof_front", ["SOFFIT FACE FRONT"]),
                        ("egrille", ["EXHAUST GRILLE"]), ("rgrille", ["ROOF GRILLE"])):
        b = L[bodies[0]]
        pl = plane_of(b)
        w, h = to2d(b, pl, b[1], b[3], b[5])
        ents = [("POLY", "CUT", rect(0, 0, w, h))]
        for kind, a in feats.get(bodies[0], []):
            if kind == "zcircle" and pl == "xy":
                ents.append(("CIRCLE", "CUT", to2d(b, pl, a[0], a[1], 0), a[4] / 2))
            elif kind == "box":
                x0, y0 = to2d(b, pl, a[0], a[2], a[4])
                x1, y1 = to2d(b, pl, a[1], a[3], a[5])
                ents.append(("POLY", "CUT", rect(max(0, min(x0, x1)), max(0, min(y0, y1)), min(w, max(x0, x1)),
                                                 min(h, max(y0, y1)))))
        for c in cuts.get(bodies[0], []):
            x0, y0 = to2d(b, pl, c[0], c[2], c[4])
            x1, y1 = to2d(b, pl, c[1], c[3], c[5])
            ents.append(("POLY", "CUT", rect(max(0, min(x0, x1)), max(0, min(y0, y1)), min(w, max(x0, x1)), min(h, max(y0, y1)))))
        if key in ("kick", "egrille", "rgrille"):
            ents.append(("LINE", "MARK", (0, 0), (w, h)))      # perforation pattern HOLD: marked, not drawn
        p = os.path.join(OUT, fname(key, "DXF", "dxf"))
        D.write_dxf(p, ents)
        out[key] = p
    return out


def flat_cut_list(v):
    L = boxes(v)
    rows = []
    for key, names in (("col_fill", ["COLUMN FILL FRONT", "COLUMN FILL LEFT"]),
                       ("sof_fill", ["SOFFIT FILL UNDER", "SOFFIT FILL FRONT"])):
        pn, name, vn, _k, mat = A.PARTS[key]
        for n in names:
            b = L[n]
            d = sorted((b[1] - b[0], b[3] - b[2], b[5] - b[4]), reverse=True)
            rows.append({"part_number": pn, "piece": n, "name": name, "name_vi": vn, "material": A.MATERIALS[mat][0],
                         "size_mm": "%.1f x %.1f x %.1f" % tuple(d), "qty_per_pod": 1,
                         "tolerance": "knife cut +/-2 (assumption)", "drawing": "none (D-89: plain rectangle)",
                         "note": "openings cut on site to the hub zone / latches: see the AIR drawing" if key else ""})
    pn, name, vn, _k, mat = A.PARTS["layer"]
    rows.append({"part_number": pn, "piece": "LAYER 50", "name": name, "name_vi": vn, "material": A.MATERIALS[mat][0],
                 "size_mm": "%.1f x %.1f x %.1f" % (v["cart_l"], v["cart_w"] - 2 * v["cart_t"], v["lay_t"]),
                 "qty_per_pod": 6, "tolerance": "knife cut +/-2 (assumption)", "drawing": "none (D-89: plain rectangle)",
                 "note": "3 per cartridge, 2 cartridges"})
    return rows


FLAT = {"col_foot", "col_side_lo", "col_side_hi", "sof_rail_d", "sof_rail_r", "sof_end", "sof_door", "kick", "egrille",
        "rgrille"}
SOFT = {"col_fill", "sof_fill", "layer"}
MAKER = {"fan": ("Noctua", "NF-A14 industrialPPC-3000 PWM")}


def size_tol(v, key):
    """(size, tolerance) for a made part's row, from its layout bodies."""
    L = boxes(v)
    names = [n for n, (k, _b) in ((n, (k, b)) for k, n, b in A.layout()) if k == key]
    if key == "layer":
        return "%.0f x %.0f x %.0f" % (v["cart_l"], v["cart_w"] - 2 * v["cart_t"], v["lay_t"]), "knife cut +/-2 (assumption)"
    if key == "casing":
        return "%.0f x %.0f x %.0f, %.0f wall" % (v["cart_w"], v["cart_d"], v["cart_l"], v["cart_t"]), "ISO 2768-m; folded"
    if not names:
        return "", ""
    parts = []
    for n in names:
        b = L[n]
        d = sorted((b[1] - b[0], b[3] - b[2], b[5] - b[4]), reverse=True)
        parts.append("%.1f x %.1f x %.1f" % tuple(d))
    size = "; ".join(sorted(set(parts)))
    if key in SOFT:
        return size, "knife cut +/-2 (assumption); a plain piece, no drawing (D-89)"
    if key in FLAT:
        return size, "ISO 2768-m; flat cut part, no drawing: its DXF is the outline (D-89 part 4)"
    return size, "ISO 2768-m; see the drawing"


# the hardware rows of AIR's parts list, all joints register parts (D-63): key in air_model.HARDWARE -> (parent key,
# material, finish, maker, sku, torque, source)
HARDWARE_ROWS = {
    "lock": ("soffit", "steel, property class 8.8 (ISO 898-1)", "zinc plated",
             "HOLD: any maker to ISO 4762, picked at the RFQ", "ISO 4762 M6 x 25 - 8.8 - zinc plated",
             "snug only, into C1's rivnuts (HOLD-01 for the rivnut)",
             "PM ruling 2026-11-01: two captive lock screws, the 5 mm key; captive retainer HOLD (joints register, D-63)"),
    "grille_bolt": ("air", "steel, property class 8.8 (ISO 898-1)", "zinc plated",
                    "HOLD: any maker to ISO 4762, picked at the RFQ", "ISO 4762 M6 x 16 - 8.8 - zinc plated",
                    "snug only, into the sleeve's rivnuts (HOLD-01 for the rivnut)",
                    "the Air Engineer 2026-11-01 (#265's open item): the roof grille over the sleeve's flange, from the "
                    "roof after the soffit hangs, the 5 mm key (R-J2); joints register H-01"),
    "grille_washer": ("air", "stainless steel A2", "none (plain stainless)",
                      "HOLD: any maker to ISO 7093-1, picked at the RFQ", "ISO 7093-1 - 6.4 x 18 x 1.6 - A2", "",
                      "one under each roof grille bolt's head (R-J10); joints register H-09"),
    "grille_rivnut": ("air", "aluminium 5056", "none (plain aluminium, as supplied)", "Sherex (PEM)", "CAH3-610-4.2",
                      "HOLD-01 (D-48)",
                      "set at the factory in the roof sleeve's top flange, one near each corner, for the grille's bolts; "
                      "joints register H-03"),
}


def parts_list(v, mass):
    per = {}

    def qty_pod(key):
        if key in per:
            return per[key]
        k, parent, q, _s = next(t for t in TREE if t[0] == key)[:4]
        per[key] = q * (qty_pod(parent) if parent else 1)
        return per[key]
    rows, by_key = [], {}
    for t in TREE:
        key, parent, q, src = t[:4]
        pkey = t[4] if len(t) > 4 else key          # a second row of the same part under another parent
        pn, name, vn, kind, mat = A.PARTS[pkey]
        m = mass.get(pn)
        if kind == "HS":
            mass_txt, mstat = "", "calculation (sum of its parts)"
        elif kind == "HOLD":
            hm, hs = HOLD_MASS.get(key, (0.0, "assumption: space only"))
            mass_txt, mstat = "%.3f" % hm, hs
        elif pkey == "fan":
            mass_txt, mstat = "0.300", "assumption (PM ruling 2026-11-01, HOLD until weighed)"
        elif key == "casing":   # a body inside the cartridge component: from its walls
            perim = 2 * (v["cart_w"] + v["cart_d"]) - 4 * v["cart_t"]
            mass_txt = "%.3f" % (perim * v["cart_t"] * v["cart_l"] * 1e-9 * A.MATERIALS["al"][1])
            mstat = "calculation (casing walls x density)"
        elif key == "layer":
            mass_txt = "%.3f" % ((v["cart_w"] - 2 * v["cart_t"]) * v["lay_t"] * v["cart_l"] * 1e-9 * A.MATERIALS["pyro"][1])
            mstat = "calculation (size x 40 kg/m3)"
        else:
            # one entry per body: a part's mass is the sum over its bodies in one occurrence
            each = (sum(m) / max(1, qty_pod(key))) if m else None
            mass_txt, mstat = ("%.3f" % each if each is not None else ""), "calculation (Fusion, CAD geometry x density)"
        size, tol = size_tol(v, pkey) if kind == "MP" else ("", "")
        maker, sku = MAKER.get(pkey, ("HOLD", "HOLD: chosen at the RFQ") if kind == "HOLD" else ("", ""))
        r = {"part_number": pn, "name": name, "name_vi": vn, "kind": kind, "parent": A.PARTS[parent][0] if parent else "",
             "qty_per_parent": q, "qty_per_pod": qty_pod(key), "material": A.MATERIALS[mat][0] if mat else "",
             "finish": FINISH.get(key, ""), "process": PROCESS.get(key, ""), "maker": maker, "sku": sku,
             "torque": "", "size_mm": size, "tolerance": tol, "mass_each_kg": mass_txt,
             "mass_status": mstat, "revision": REV, "status": "HOLD" if kind == "HOLD" or pkey == "fan" else "DRAFT",
             "source": src}
        rows.append(r)
        by_key[key] = r
    kids = {}
    for t in TREE:
        key, parent, q = t[:3]
        if parent:
            kids.setdefault(parent, []).append((key, q))
    for key, (parent, material, finish, maker, sku, torque, src) in HARDWARE_ROWS.items():
        hp = A.HARDWARE[key]
        rows.append({"part_number": hp[0], "name": hp[1], "name_vi": hp[2], "kind": "PI", "parent": A.PARTS[parent][0],
                     "qty_per_parent": hp[3], "qty_per_pod": hp[3], "material": material, "finish": finish, "process": "",
                     "maker": maker, "sku": sku, "torque": torque, "size_mm": "", "tolerance": "",
                     "mass_each_kg": "%.4f" % hp[4], "mass_status": "calculation (joints register sizes)", "revision": REV,
                     "status": "DRAFT", "source": src})
        by_key[key] = rows[-1]
        kids.setdefault(parent, []).append((key, hp[3]))

    def total(key):
        r = by_key[key]
        if r["kind"] != "HS":
            return float(r["mass_each_kg"] or 0.0)
        return sum(q * total(k) for k, q in kids.get(key, []))
    for key, r in by_key.items():
        if r["kind"] == "HS":
            r["mass_each_kg"] = "%.3f" % total(key)
    return rows


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    v = A.evaluate()
    mass, _flat = CE.parse_log(argv[1])
    os.makedirs(OUT, exist_ok=True)
    for k, p in sorted(write_dxfs(v).items()):
        s = D.summary(p)
        print("DXF", os.path.basename(p), "extents", [round(x, 2) for x in s["extents"]])
    for name, rows in (("PARTS-LIST", parts_list(v, mass)),):
        p = os.path.join(OUT, "610000_%s_AIR-%s_BOM.csv" % (REV, name))
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(name, p, len(rows), "rows")
    rows = parts_list(v, mass)
    for r in rows:
        if r["part_number"] in ("610201", "610101", "610301", "610401"):
            print("shipping piece %s %s: %s kg" % (r["part_number"], r["name"], r["mass_each_kg"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
