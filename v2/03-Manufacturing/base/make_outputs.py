"""BASE manufacturing outputs from the CAD's own facts.

    python3 v2/03-Manufacturing/base/make_outputs.py          # parts list + cut list
    PYTHONPATH=<dir with ezdxf> python3 ... --dxf               # also F1's DXF (needs ezdxf)

Reads 110000_P01_BASE_DATA.json, which v2/01-CAD-Native/base/base_build.py
writes from the Fusion design (quantities = copies in the CAD, masses = the
CAD's physical properties, sizes = the bodies), and writes:

  110000_P01_BASE_BOM.csv                    parts list for the master BOM (v2/04-BOM)
  110000_P01_BASE-TUBE-CUT-LIST_SPEC.csv     cut lengths and end cuts of the tubes and angle
  111401_P01_BASE-FLOOR-PANEL-F1_DXF.dxf     F1's CNC outline, 1:1, mm (with --dxf)
  111501_P01_..._DXF.dxf                     the F1 foam mat's outline (D-89 part 3; with --dxf)
  111601_P01_..._DXF.dxf                     the glide doubler's outline and hole (D-89 part 4; with --dxf)

The fixed facts per part (material, finish, process, status, source) are in
PART_INFO below. Items the CAD doesn't model (bolts, M10 glide nuts, the end
cap, the edge seal) are in EXTRA with the rule that gives their quantity.
Hardware numbers are the joints register's (D-63; PR #23 hardware table).
"""

import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "P01"
DATA = os.path.join(HERE, "110000_%s_BASE_DATA.json" % REV)
BOM = os.path.join(HERE, "110000_%s_BASE_BOM.csv" % REV)
CUT = os.path.join(HERE, "110000_%s_BASE-TUBE-CUT-LIST_SPEC.csv" % REV)
DXF = os.path.join(HERE, "111401_%s_BASE-FLOOR-PANEL-F1_DXF.dxf" % REV)
MAT_DXF = os.path.join(HERE, "111501_%s_BASE-FLOOR-MAT-F1-CLOSED-CELL-3-MM-FOAM_DXF.dxf" % REV)
DBL_DXF = os.path.join(HERE, "111601_%s_BASE-GLIDE-DOUBLER-COMMON_DXF.dxf" % REV)

AA20 = "black anodised, matte, 20 um (class AA20, EN ISO 7599)"
SCOPE = "P01 sample scope: the back-left corner and F1; the rest of BASE follows in P02"

# part number: (material, finish, process, mass_status, status, source, note)
PART_INFO = {
    "110000": ("assembly", "", "", "calculation", "DRAFT", "this list (sum of the rows)", SCOPE),
    "110101": ("assembly: band tube with its rivnuts, stop washers, spigots and glides fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD", "hardware-fitted subassembly (guideline 4.1)"),
    "110103": ("assembly: band tube with its rivnuts, stop washers, spigots and glides fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD", "hardware-fitted subassembly; carries the BR bracket rivnuts too"),
    "111101": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 (PM ruling; alloy: assumption)", AA20,
               "saw cut (front mitre, back square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67; section layout study B-BAND", "front end mitred to DL's facet band piece (P02)"),
    "111103": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 (PM ruling; alloy: assumption)", AA20,
               "saw cut (square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67; section layout study B-BAND", "2420 long: fits the 96 x 48 in pallet (layout study B1)"),
    "110401": ("bonded subassembly: F1 plywood with its foam mat bonded underneath at the factory (D-87); adhesive spec HOLD",
               "", "bond (spec HOLD)", "calculation", "DRAFT", "CAD; D-87", "ships as one piece"),
    "111401": ("poplar-core plywood 9 mm with a hard face veneer, low-emission (E1 / CARB P2 class, HOLD), about 450 kg/m3 (assumption, D-85)",
               "hard face veneer with a factory clear lacquer, top face (assumption; product HOLD)",
               "CNC router: outline and the seam half-lap", "calculation", "DRAFT",
               "CAD; D-72 (9 mm floor), packing plan (1219 max with the lap)", "1218.5 wide including the 13 mm lap"),
    "111501": ("closed-cell foam, cross-linked PE or EPDM, 3 mm thick, about 200 kg/m3 (assumption; product HOLD, ISS-085)",
               "", "cut to the panel outline, bonded under F1 at the factory (D-87)", "calculation", "HOLD", "CAD; D-76, D-87",
               "under F1"),
    "831001": ("stainless steel A2 round bar, turned, M6 stud (assumption)", "passivated stainless, bright (assumption)",
               "lathe, thread, chamfer",
               "calculation", "DRAFT", "CAD; joints register H-05 (PROPOSED sizes)",
               "screwed into its rivnut with threadlocker at the factory"),
    "831002": ("aluminium sheet 1.5, 5000 or 6000 series (joints register H-08)", "mill finish (hidden)", "punch",
               "calculation", "DRAFT", "CAD; joints register H-08", "under each J-BASE-01 bolt rivnut's head"),
    "838003": ("aluminium 5056 (maker)", "plain aluminium, as supplied (maker)", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-03; Sherex CAH3-610-4.2", "set at the factory; torque HOLD-01"),
    "111211": ("aluminium EN AW-6061 T6 block 25 x 35 x 75 (joints register J-BASE-02; sizes from the Joints Engineer 2026-11-01)",
               "mill finish (hidden)",
               "saw, mill; drill and tap 2 x M6 through the end face and 2 x M6 with 15 of full thread in the bottom (PM ruling on F-017)",
               "calculation", "DRAFT", "joints register J-BASE-02 (PR #99); the Joints Engineer's part (model, STEP and "
               "tabulated drawing 111211 to 111214, PM ruling 2026-11-01), placed here by reference",
               "fixed in the back band's end at the factory; the side band drops onto its 2 hook studs"),
    "838001": ("steel, property class 8.8 (ISO 898-1)", "zinc plated (ISO 4042)", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-01",
               "corner keys' hook studs: 2 per key, set 1.8 proud at the factory, threadlocked (J-BASE-02)"),
    "838010": ("stainless steel A2-70 (ISO 3506-1)", "plain stainless, as supplied", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-31 (PR #99)",
               "corner keys' fixing screws: 2 per key from below, no washer (flanged head), factory; head 3.3 under the band"),
    "838004": ("stainless steel A2, 200 HV (ISO 7093-1)", "plain stainless, as supplied", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-09",
               "under the corner keys' fixing bolts"),
    "111601": ("aluminium sheet EN AW-5754 H22, 3 mm thick (assumption)", "mill finish (hidden inside the band, D-79)",
               "laser or waterjet cut from 3 mm sheet, deburred; no drawing: its DXF and this row (D-89 part 4)",
               "calculation", "DRAFT",
               "CAD; PM rulings 2026-10-31 (band 1.5 with a doubler at each glide; 52 long, hole centred)",
               "52 x 36 x 3 with one Ø13 hole centred; inside the band on its bottom face, clamped by the glide's M10 rivnut"),
    "118002": ("levelling glide, M10 stem with a 5 mm hex socket on top, about 36 mm pad; base 6.5 mm or taller, so that "
               "screwed fully home against the M10 rivnut's head it holds the band at 8.5 mm: a hard stop (product HOLD)", "", "",
               "assumption", "HOLD", "layout study B-GLIDE 0.15 kg; lowest setting: PM ruling on F-018 (joints register PR #99)",
               "preset at the factory (D-87); levelled from above through the band top before the walls go on, up from the "
               "highest floor spot, never below 8.5 mm"),
}

# bought items: (maker, exact SKU or standard designation, torque with its basis); HOLD where the
# product isn't named yet (its issue in the status and note). Standard fasteners are ordered by
# their standard designation from any maker; the catalogue number comes with the RFQ.
BOUGHT = {
    "838003": ("Sherex", "CAH3-610-4.2", "HOLD-01: set and torque from the rivnut test (D-48)"),
    "838001": ("standard part, any maker (catalogue number at RFQ)", "ISO 4762 M6 x 16 - 8.8, zinc plated",
               "HOLD: into the corner key's M6 threads, from the joint test J-T6 (joints register)"),
    "838004": ("standard part, any maker (catalogue number at RFQ)", "ISO 7093-1 - 6 - 200 HV - A2", ""),
    "838010": ("standard part, any maker (catalogue number at RFQ)", "ISO 7380-2 M6 x 12 - A2-70",
               "HOLD: into the corner key's M6 thread, from the joint test J-T6 (joints register)"),
    "838006": ("HOLD (glide nut not named yet)", "HOLD", "HOLD: with the glide nut's set test"),
    "118002": ("HOLD (glide not named yet)", "HOLD", ""),
    "118003": ("HOLD (end cap not named yet)", "HOLD", ""),
    "118001": ("HOLD-06 (candidate Pemko)", "HOLD-06 (candidate S88BL)", ""),
}
# tolerance per part: the drawing's, or for a part with no drawing the row's (D-89 parts 3 and 4)
TOLERANCE = {
    "111101": "see its drawing", "111103": "see its drawing",
    "111211": "the Joints Engineer's tabulated drawing 111211 to 111214",
    "111401": "see its drawing",
    "111501": "outline +-1 (knife cut), thickness +-0.3 (assumption); DXF 111501",
    "111601": "ISO 2768-m; critical hole: Ø13 +0.10/0 for the glide's M10 rivnut (HOLD with the nut), centred +-0.2; DXF 111601",
    "831002": "joints register H-08: thickness +-0.05",
}

# items not modelled in the CAD: (part number, name, name_vi, type, parent, qty rule, unit,
# material, finish, mass each kg, mass_status, status, source, note)
EXTRA = [
    ("838006", "HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE (HOLD)", "Tán rút M10 cho chân chỉnh", "PI", "band",
     "glides", "pcs", "aluminium or steel (HOLD)", "", 0.006, "assumption", "HOLD",
     "number PROPOSED for the joints register (glide nut)", "set through the band's 1.5 bottom face and the 3 mm doubler (grip 4.5) at the factory"),
    ("118003", "BASE - TUBE END CAP - 100 X 40 - BLACK (HOLD)", "Nút bịt đầu ống 100x40", "PI", "110101",
     "endcap", "pcs", "PE or PP insert cap for a 100 x 40 x 2.0 tube, black (product HOLD)", "", 0.01, "assumption", "HOLD",
     "number PROPOSED for the joints register", "closes the side band's back end, face flush with Y = pod_d / 2"),
    ("118001", "BASE - BASE SEAL - FLOOR EDGE - FIXED 4 GAP", "Gioăng mép sàn", "PI", "110000",
     "edgeseal", "m", "silicone bulb, self-adhesive; candidate Pemko S88BL 12.7 x 6.4 (hardware selection D pick 1; "
     "gap range unverified; product HOLD-06)", "",
     0.05, "assumption", "HOLD",
     "joints register H-06 (118001); BASE proposes the seal at the floor's edge against the band's inner face, not under the band",
     "along F1's edges at the band; keeps v1's open shadow line under the band"),
]


def load():
    with open(DATA, "r", encoding="utf-8") as fh:
        return json.load(fh)


def param(d, name):
    for p in d["params"]:
        if p["name"] == name:
            return p["value"]
    raise KeyError(name)


def extra_qty(d, rule, parent_counts):
    if rule == "glides":
        return parent_counts.get("118002", 0)
    if rule == "endcap":
        return 1
    if rule == "edgeseal":
        f = d["floor_f1"]
        # F1's left edge (along Y) and back edge (along X) meet the band
        return round(((f["y1"] - f["y0"]) + (f["x_seam"] - f["x0"])) / 1000.0, 3)
    raise ValueError(rule)


def size_text(rec):
    b = rec.get("box_mm")
    if not b:
        return ""
    dims = sorted((round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2)), reverse=True)
    return " x ".join("%g" % x for x in dims)


def make_bom(d):
    parts, copies = d["parts"], d["copies"]
    per_pod = {}
    for k, n in copies.items():
        parent, child = k.split(">")
        mult = 1
        if parent != "110000":
            mult = copies.get("110000>%s" % parent, 1)
        per_pod[child] = per_pod.get(child, 0) + n * mult
    rows = []
    mass_of = {}
    for pn, rec in parts.items():
        if rec.get("mass_kg") is not None:
            mass_of[pn] = rec["mass_kg"]
    # assembly masses: children's copies x mass (calculation)
    for asm in sorted({k.split(">")[0] for k in copies} - {"110000"}):
        tot = 0.0
        for k, n in copies.items():
            parent, child = k.split(">")
            if parent == asm:
                tot += n * mass_of.get(child, 0.0)
        mass_of[asm] = round(tot, 4)
    counts_total = dict(per_pod)
    extra_rows = []
    for (pn, name, vn, typ, parent, rule, unit, mat, fin, m, ms, st, src, note) in EXTRA:
        if parent == "band":
            # one per glide, in the band assembly that holds the glide
            for asm in ("110101", "110103"):
                q = copies.get("%s>118002" % asm, 0)
                if q:
                    extra_rows.append((pn, name, vn, typ, asm, q, unit, mat, fin, m, ms, st, src, note))
                    mass_of[asm] = round(mass_of[asm] + q * m, 4)
        else:
            q = extra_qty(d, rule, counts_total)
            extra_rows.append((pn, name, vn, typ, parent, q, unit, mat, fin, m, ms, st, src, note))
            if parent in ("110101", "110103"):
                mass_of[parent] = round(mass_of[parent] + q * m, 4)
    header = ["level", "part_number", "name", "name_vi", "type", "parent", "qty_per_parent", "qty_per_pod", "unit",
              "material", "finish", "process", "size_mm", "unit_mass_kg", "mass_total_kg", "mass_status", "status",
              "source", "note", "tolerance", "maker", "sku", "torque_nm"]

    def tail(pn):
        maker, sku, tq = BOUGHT.get(pn, ("", "", ""))
        return [TOLERANCE.get(pn, ""), maker, sku, tq]

    def row(level, pn, parent, qpp, qpod, unit="pcs"):
        rec = parts[pn]
        mat, fin, proc, ms, st, src, note = PART_INFO[pn]
        m = mass_of.get(pn, 0.0)
        return [level, pn, rec["name"], rec["name_vi"], rec["class"], parent, qpp, qpod, unit, mat, fin, proc,
                size_text(rec), "%.4f" % m, "%.3f" % (m * qpod), ms, st, src, note] + tail(pn)
    # top: 110000
    sub = []
    for k in sorted(copies):
        parent, child = k.split(">")
        if parent == "110000":
            sub.append(child)
    total = 0.0
    body = []
    for child in sub:
        n = copies["110000>%s" % child]
        body.append(row(1, child, "110000", n, n))
        total += n * mass_of.get(child, 0.0)
        for k in sorted(copies):
            p2, c2 = k.split(">")
            if p2 == child:
                body.append(row(2, c2, child, copies[k], copies[k] * n))
        for r in extra_rows:
            if r[4] == child:
                (pn, name, vn, typ, parent, q, unit, mat, fin, m, ms, st, src, note) = r
                body.append([2, pn, name, vn, typ, parent, q, q * n, unit, mat, fin, "", "", "%.4f" % m,
                             "%.3f" % (m * q * n), ms, st, src, note] + tail(pn))
    for r in extra_rows:
        if r[4] == "110000":
            (pn, name, vn, typ, parent, q, unit, mat, fin, m, ms, st, src, note) = r
            body.append([1, pn, name, vn, typ, parent, q, q, unit, mat, fin, "", "", "%.4f" % m, "%.3f" % (m * q),
                         ms, st, src, note] + tail(pn))
            total += m * q
    mat, fin, proc, ms, st, src, note = PART_INFO["110000"]
    top = [0, "110000", "BASE", "Đế / sàn", "assembly", "100000", 1, 1, "pcs", mat, fin, proc, "", "%.4f" % total,
           "%.3f" % total, ms, st, src, note] + tail("110000")
    with open(BOM, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerow(top)
        for r in body:
            w.writerow(r)
    print("wrote %s: %d rows, BASE P01 mass %.2f kg (sample scope)" % (os.path.relpath(BOM, HERE), len(body) + 1, total))


def make_cut_list(d):
    names = {pn: rec["name"] for pn, rec in d["parts"].items()}
    with open(CUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["item", "name", "section", "material", "qty_per_pod", "cut_length_outer_face_mm",
                    "cut_length_inner_face_mm", "tolerance", "front_or_first_end", "back_or_second_end", "finish",
                    "status", "source"])
        copies = d["copies"]
        for pn, t in sorted(d["tubes"].items()):
            q = sum(n for k, n in copies.items() if k.endswith(">%s" % pn))
            w.writerow([pn, names[pn], t["section"], PART_INFO[pn][0], q, "%.2f" % t["outer_face_length"],
                        "%.2f" % t["inner_face_length"], "length +0/-0.5, end angle +-0.25 deg (assumption)",
                        t["front_end"], t["back_end"], PART_INFO[pn][1], "calculation (CAD)", "110000_P01_BASE_CAD"])
        # D-89: a plain knife-cut sheet needs no drawing when the cut list gives its size,
        # material, tolerance and part number
        for pn in ("111501",):
            rec = d["parts"].get(pn)
            if not rec:
                continue
            b = rec["box_mm"]
            q = sum(n for k, n in copies.items() if k.endswith(">%s" % pn))
            w.writerow([pn, rec["name"], "sheet %.0f thick" % (b[5] - b[2]), PART_INFO[pn][0], q, "%.1f" % (b[3] - b[0]),
                        "%.1f" % (b[4] - b[1]), "+-1 on each side (assumption)", "knife-cut rectangle, X x Y as listed",
                        "bonded under its floor panel, flush with its outline (D-87)", "", "calculation (CAD)",
                        "110000_P01_BASE_CAD"])
    print("wrote %s" % os.path.relpath(CUT, HERE))


def make_dxf(d):
    import ezdxf
    f = d["floor_f1"]
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for name, color in (("CUT", 7), ("POCKET-HALF-DEPTH", 3), ("MARK", 1)):
        doc.layers.add(name, color=color)
    msp = doc.modelspace()
    # F1 in its own 2D system CS-111401: X(2D) = pod X, Y(2D) = pod Y, origin = pod origin projected
    pts = [(f["x0"], f["y0"]), (f["x_lap"], f["y0"]), (f["x_lap"], f["y1"]), (f["x0"], f["y1"])]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
    lap = [(f["x_seam"], f["y0"]), (f["x_lap"], f["y0"]), (f["x_lap"], f["y1"]), (f["x_seam"], f["y1"])]
    msp.add_lwpolyline(lap, close=True, dxfattribs={"layer": "POCKET-HALF-DEPTH"})
    msp.add_text("F1 111401 P01 - top face up - POCKET depth %.1f from the top - mm" % f["lap_depth"],
                 dxfattribs={"layer": "MARK", "height": 20}).set_placement((f["x0"] + 50, f["y0"] + 50))
    doc.saveas(DXF)
    # the floor mat under F1 (soft goods, D-89): its knife-cut outline, same system as F1
    m = d["parts"]["111501"]["box_mm"]
    mdoc = ezdxf.new("R2010", setup=True)
    mdoc.units = ezdxf.units.MM
    mdoc.header["$INSUNITS"] = 4
    mdoc.header["$MEASUREMENT"] = 1
    for name, color in (("CUT", 7), ("MARK", 1)):
        mdoc.layers.add(name, color=color)
    mm_ = mdoc.modelspace()
    mm_.add_lwpolyline([(m[0], m[1]), (m[3], m[1]), (m[3], m[4]), (m[0], m[4])], close=True, dxfattribs={"layer": "CUT"})
    mm_.add_text("111501 P01 FLOOR MAT F1 - closed-cell foam 3 mm - knife cut +-1 - mm",
                 dxfattribs={"layer": "MARK", "height": 20}).set_placement((m[0] + 50, m[1] + 50))
    mdoc.saveas(MAT_DXF)
    print("wrote %s: %.1f x %.1f" % (os.path.relpath(MAT_DXF, HERE), m[3] - m[0], m[4] - m[1]))
    # the glide doubler (D-89 part 4: a flat part cut from sheet goes on its DXF and its parts-list row):
    # its own 2D system, X across the band (gd_w), Y along it (gd_l), origin at the plate centre
    gw, gl, gh, gdx = (param(d, k) for k in ("gd_w", "gd_l", "gl_nut_hole", "gl_dx"))
    ddoc = ezdxf.new("R2010", setup=True)
    ddoc.units = ezdxf.units.MM
    ddoc.header["$INSUNITS"] = 4
    ddoc.header["$MEASUREMENT"] = 1
    for name, color in (("CUT", 7), ("MARK", 1)):
        ddoc.layers.add(name, color=color)
    dm = ddoc.modelspace()
    dm.add_lwpolyline([(-gw / 2, -gl / 2), (gw / 2, -gl / 2), (gw / 2, gl / 2), (-gw / 2, gl / 2)], close=True,
                      dxfattribs={"layer": "CUT"})
    dm.add_circle((gdx, 0.0), gh / 2, dxfattribs={"layer": "CUT"})
    for i, line in enumerate(("111601 P01 GLIDE DOUBLER - COMMON - qty per the parts list",
                              "EN AW-5754 H22 sheet 3 mm - mill finish - ISO 2768-m - mm",
                              "hole Ø%g +0.10/0 centred +-0.2 (the glide's M10 rivnut)" % gh)):
        dm.add_text(line, dxfattribs={"layer": "MARK", "height": 2.5}).set_placement((-gw / 2, gl / 2 + 4 + 4 * (2 - i)))
    ddoc.saveas(DBL_DXF)
    print("wrote %s: %.1f x %.1f, hole Ø%g at x %.1f" % (os.path.relpath(DBL_DXF, HERE), gw, gl, gh, gdx))
    w = f["x_lap"] - f["x0"]
    h = f["y1"] - f["y0"]
    print("wrote %s: outline %.1f x %.1f (with the lap), pocket %.1f wide, %.1f deep" % (
        os.path.relpath(DXF, HERE), w, h, f["x_lap"] - f["x_seam"], f["lap_depth"]))
    if w > 1219.0:
        raise SystemExit("F1 is %.1f wide with its lap: over the 1219 of the 48 in pallet" % w)


def main(argv):
    d = load()
    make_bom(d)
    make_cut_list(d)
    if "--dxf" in argv:
        make_dxf(d)


if __name__ == "__main__":
    main(sys.argv[1:])
