"""BASE manufacturing outputs from the CAD's own facts.

    python3 v2/03-Manufacturing/base/make_outputs.py          # parts list + cut list
    PYTHONPATH=<dir with ezdxf> python3 ... --dxf               # also F1's DXF (needs ezdxf)

Reads 110000_P01_BASE_DATA.json, which v2/01-CAD-Native/base/base_build.py
writes from the Fusion design (quantities = copies in the CAD, masses = the
CAD's physical properties, sizes = the bodies), and writes:

  110000_P01_BASE_BOM.csv                    parts list for the master BOM (v2/04-BOM)
  110000_P01_BASE-TUBE-CUT-LIST_SPEC.csv     cut lengths and end cuts of the tubes and angle
  111401_P01_BASE-FLOOR-PANEL-F1_DXF.dxf     F1's CNC outline, 1:1, mm (with --dxf)

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

AA20 = "black anodised, matte, 20 um (class AA20, EN ISO 7599)"
SCOPE = "P01 sample scope: the back-left corner and F1; the rest of BASE follows in P02"

# part number: (material, finish, process, mass_status, status, source, note)
PART_INFO = {
    "110000": ("assembly", "", "", "calculation", "DRAFT", "this list (sum of the rows)", SCOPE),
    "110101": ("assembly: band tube with its rivnuts, stop washers, spigots and glides fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD", "hardware-fitted subassembly (guideline 4.1)"),
    "110103": ("assembly: band tube with its rivnuts, stop washers, spigots and glides fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD", "hardware-fitted subassembly; carries the BR bracket rivnuts too"),
    "111101": ("aluminium 6063-T6 rectangular tube 100 x 40 x 2.0 (wall: assumption, HOLD-07; alloy: assumption)", AA20,
               "saw cut (front mitre, back square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67; section layout study B-BAND", "front end mitred to DL's facet band piece (P02)"),
    "111103": ("aluminium 6063-T6 rectangular tube 100 x 40 x 2.0 (wall: assumption, HOLD-07; alloy: assumption)", AA20,
               "saw cut (square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67; section layout study B-BAND", "2420 long: fits the 96 x 48 in pallet (layout study B1)"),
    "111201": ("aluminium 6063-T6 equal angle 60 x 60 x 5 (assumption)", AA20 + " (visible inside at floor level; assumption)",
               "saw cut, drill, deburr, anodise", "calculation", "DRAFT", "CAD",
               "COMMON: BL in P01, BR (same part, turned) in P02"),
    "111401": ("plywood 9 mm, low-emission (E1 / CARB P2 class, HOLD), 600 kg/m3 (assumption, layout study rho_ply)",
               "factory wood-look finish (HOLD)", "CNC router: outline and the seam half-lap", "calculation", "DRAFT",
               "CAD; D-72 (9 mm floor), packing plan (1219 max with the lap)", "1218.5 wide including the 13 mm lap"),
    "111501": ("closed-cell foam, cross-linked PE or EPDM, 3 mm, about 200 kg/m3 (assumption; product HOLD, ISS-085)",
               "", "cut to the panel outline", "calculation", "HOLD", "CAD; D-76", "under F1"),
    "831001": ("stainless steel A2 round bar, turned, M6 stud (assumption)", "", "lathe, thread, chamfer",
               "calculation", "DRAFT", "CAD; joints register H-05 (PROPOSED sizes)",
               "screwed into its rivnut with threadlocker at the factory"),
    "831002": ("aluminium sheet 1.5, 5000 or 6000 series (joints register H-08)", "mill finish (hidden)", "punch",
               "calculation", "DRAFT", "CAD; joints register H-08", "under each J-BASE-01 bolt rivnut's head"),
    "838003": ("aluminium 5056 (maker)", "", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-03; Sherex CAH3-610-4.2", "set at the factory; torque HOLD-01"),
    "118002": ("levelling glide, M10 stem with a 5 mm hex socket on top, about 36 mm pad (product HOLD)", "", "",
               "assumption", "HOLD", "layout study B-GLIDE 0.15 kg", "adjusted from above through the band top before the walls go on"),
}

# items not modelled in the CAD: (part number, name, name_vi, type, parent, qty rule, unit,
# material, finish, mass each kg, mass_status, status, source, note)
EXTRA = [
    ("838001", "HARDWARE - SOCKET HEAD BOLT - M6 X 16 - ISO 4762 8.8 ZINC", "Bulong lục giác chìm M6 × 16", "PI", "110000",
     "bracket", "pcs", "steel 8.8, zinc plated", "", 0.0065, "calculation", "DRAFT",
     "joints register H-01 (D-63); mass from nominal ISO 4762 geometry", "corner bracket BL: 2 per leg, site fitted"),
    ("838004", "HARDWARE - HEAD WASHER - 6.4 X 18 X 1.6 - ISO 7093-1 A2", "Long đen lớn M6", "PI", "110000",
     "bracket", "pcs", "stainless A2", "", 0.0028, "calculation", "DRAFT",
     "joints register H-09 (D-63); mass pi/4 (18^2 - 6.4^2) 1.6 x 7.9 g/cm3", "under each bracket bolt head"),
    ("838006", "HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE (HOLD)", "Tán rút M10 cho chân chỉnh", "PI", "band",
     "glides", "pcs", "aluminium or steel (HOLD)", "", 0.006, "assumption", "HOLD",
     "number PROPOSED for the joints register (glide nut)", "set in the band's bottom wall at the factory"),
    ("118003", "BASE - TUBE END CAP - 100 X 40 - BLACK (HOLD)", "Nút bịt đầu ống 100x40", "PI", "110101",
     "endcap", "pcs", "PE or PP insert cap for a 100 x 40 x 2.0 tube, black (product HOLD)", "", 0.01, "assumption", "HOLD",
     "number PROPOSED for the joints register", "closes the side band's back end, face flush with Y = pod_d / 2"),
    ("118001", "BASE - BASE SEAL - FLOOR EDGE - PEMKO S88BL (HOLD)", "Gioăng mép sàn", "PI", "110000",
     "edgeseal", "m", "silicone bulb 12.7 x 6.4, self-adhesive (hardware selection D pick 1; gap range unverified)", "",
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
    if rule == "bracket":
        return 4 * parent_counts.get("111201", 0)
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
    for asm in ("110101", "110103"):
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
              "source", "note"]

    def row(level, pn, parent, qpp, qpod, unit="pcs"):
        rec = parts[pn]
        mat, fin, proc, ms, st, src, note = PART_INFO[pn]
        m = mass_of.get(pn, 0.0)
        return [level, pn, rec["name"], rec["name_vi"], rec["class"], parent, qpp, qpod, unit, mat, fin, proc,
                size_text(rec), "%.4f" % m, "%.3f" % (m * qpod), ms, st, src, note]
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
                             "%.3f" % (m * q * n), ms, st, src, note])
    for r in extra_rows:
        if r[4] == "110000":
            (pn, name, vn, typ, parent, q, unit, mat, fin, m, ms, st, src, note) = r
            body.append([1, pn, name, vn, typ, parent, q, q, unit, mat, fin, "", "", "%.4f" % m, "%.3f" % (m * q),
                         ms, st, src, note])
            total += m * q
    mat, fin, proc, ms, st, src, note = PART_INFO["110000"]
    top = [0, "110000", "BASE", "Đế / sàn", "assembly", "100000", 1, 1, "pcs", mat, fin, proc, "", "%.4f" % total,
           "%.3f" % total, ms, st, src, note]
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
        w.writerow(["item", "name", "section", "qty_per_pod", "cut_length_outer_face_mm", "cut_length_inner_face_mm",
                    "front_or_first_end", "back_or_second_end", "finish", "status", "source"])
        copies = d["copies"]
        for pn, t in sorted(d["tubes"].items()):
            q = sum(n for k, n in copies.items() if k.endswith(">%s" % pn))
            w.writerow([pn, names[pn], t["section"], q, "%.2f" % t["outer_face_length"], "%.2f" % t["inner_face_length"],
                        t["front_end"], t["back_end"], PART_INFO[pn][1], "calculation (CAD)",
                        "110000_P01_BASE_CAD; tolerance +0 / -0.5 on length (assumption)"])
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
