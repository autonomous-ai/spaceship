"""BASE manufacturing outputs from the CAD's own facts.

    python3 v2/03-Manufacturing/base/make_outputs.py          # parts list + cut list
    PYTHONPATH=<dir with ezdxf> python3 ... --dxf               # also the DXFs (needs ezdxf)

Reads 110000_P01_BASE_DATA.json, which v2/01-CAD-Native/base/base_build.py
writes from the Fusion design (quantities = copies in the CAD, masses = the
CAD's physical properties, sizes = the bodies), and writes:

  110000_P01_BASE_BOM.csv                    parts list for the master BOM (v2/04-BOM)
  110000_P01_BASE-TUBE-CUT-LIST_SPEC.csv     cut lengths and end cuts of the tubes and angle
  111601_P01_..._DXF.dxf                     the glide doubler's outline and hole (D-89 part 4; with --dxf)

The fixed facts per part (material, finish, process, status, source) are in
PART_INFO below. Items the CAD doesn't model (the M10 glide nuts, the sill's M3
screws and rivnuts, the lip seal) are in EXTRA with the rule that gives their
quantity; the lip seal's metres come from the CAD's seal runs (D-132: no floor).
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
DBL_DXF = os.path.join(HERE, "111601_%s_BASE-GLIDE-DOUBLER-COMMON_DXF.dxf" % REV)

AA20 = "black anodised, matte, 20 um (class AA20, EN ISO 7599)"
SCOPE = ("P02 so far: the side bands, the back band, FR1 with its sill (no floor and no threshold, D-132); "
         "the front-left pieces and the intake follow")

# part number: (material, finish, process, mass_status, status, source, note)
PART_INFO = {
    "110000": ("assembly", "", "", "calculation", "DRAFT", "this list (sum of the rows)", SCOPE),
    "110101": ("assembly: band tube with its corner keys, rivnuts, stop washers, spigots, glides and back end cap fitted at the "
               "factory", "", "", "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD",
               "hardware-fitted subassembly (guideline 4.1); carries the back corner key 111211 with its stud bolts set (D-129)"),
    "110103": ("assembly: band tube with its welded end plates, and its rivnuts, stop washers, spigots and glides fitted at the "
               "factory", "", "", "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD",
               "hardware-fitted subassembly; drops in between the side bands' key studs (D-129); 2420 over its end plates"),
    "111101": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 (PM ruling; alloy: assumption)", AA20,
               "saw cut (front mitre, back square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67; section layout study B-BAND", "front end mitred to DL's facet band piece (P02)"),
    "111103": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 with 2 welded 1.5 mm end plates (alloy: assumption)", AA20,
               "saw cut square, weld the end plates, CNC drill, cut the slots, notches and bevels, deburr, anodise",
               "calculation", "DRAFT", "CAD; finish D-67; section layout study B-BAND; D-129 and joints register J-BASE-02 "
               "(FR-15) for the end plates", "2420 over its end plates (D-129: ships at 2420 on pallet 2's 2438 deck)"),
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
               "fixed in each side band's back end at the factory (D-129); the back band drops onto its 2 hook studs"),
    "838001": ("steel, property class 8.8 (ISO 898-1)", "zinc plated (ISO 4042)", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-01",
               "corner keys' hook studs: 2 per key, set 1.8 proud at the factory, threadlocked (J-BASE-02)"),
    "838010": ("stainless steel A2-70 (ISO 3506-1)", "plain stainless, as supplied", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-31 (PR #99)",
               "corner keys' fixing screws: 2 per key from below, no washer (flanged head), factory; head 3.3 under the band"),
    "838004": ("stainless steel A2, 200 HV (ISO 7093-1)", "plain stainless, as supplied", "", "calculation", "DRAFT",
               "CAD envelope; joints register H-09",
               "under the corner keys' fixing bolts"),
    "111601": ("aluminium plate EN AW-6082 T6, 5 mm thick (PM ruling 2026-11-01)", "mill finish (hidden inside the band, D-79)",
               "laser or waterjet cut from 5 mm plate, deburred; no drawing: its DXF and this row (D-89 part 4)",
               "calculation", "DRAFT",
               "CAD; PM rulings 2026-10-31 (band 1.5 with a doubler at each glide; 52 long, hole centred) and 2026-11-01 "
               "(5 mm 6082-T6, the recheck at the steel pod's mass)",
               "54 x 36 x 5 with one Ø13 hole centred; inside the band on its bottom face, clamped by the glide's M10 rivnut"),
    # P02 batch 1 (the right band, FR1 with its sill; F2 and the threshold went, D-132)
    "110102": ("assembly: band tube with its rivnuts, stop washers, spigots and glides fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD", "hardware-fitted subassembly; mirror of 110101"),
    "111102": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 (PM ruling; alloy: assumption)", AA20,
               "saw cut (front mitre, back square), CNC drill, deburr, anodise", "calculation", "DRAFT",
               "CAD; finish D-67", "mirror of 111101; front end mitred to the intake's facet piece; tabulated with 111101"),
    "110106": ("assembly: FR1 with its sill, FRONT's bottom U-channel screwed on, and the glides, fitted at the factory",
               "", "", "calculation", "DRAFT", "CAD; PM ruling 2026-11-01 (the channel ships fitted on the sill)",
               "ships as one piece; on site the fixed glass drops into the fitted channel"),
    "111106": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 with a welded 1.5 mm end plate (alloy: assumption)", AA20,
               "saw cut square, weld the end plate, CNC drill and cut the keyholes, deburr, anodise", "calculation", "DRAFT",
               "CAD; joints register J-BASE-02 (keyhole piece of the inline joint at x_fr_joint)",
               "X 218.5 to x_fr_joint; its glides are levelled by turning their base (no key holes on its visible top)"),
    "111301": ("aluminium sheet EN AW-5005 H14, 2 mm (assumption)", AA20,
               "laser cut, press brake (4 bends), insert 4 M3 flush rivnuts, anodise", "calculation", "DRAFT",
               "CAD; FRONT's answer and the PM ruling of 2026-11-01",
               "ledge flush with the band top, seat under the U-channel, kerb down to the band's bottom line; the glass's "
               "load goes into FR1 (D-132; seat detail with FRONT); flange riveted to FR1 (rivets HOLD)"),
    "118003": ("flat end cap for the 100 x 40 x 1.5 tube's bore, black, no deeper than 2 (D-129; PE assumed, product HOLD)",
               "black", "bonded into the side band's back end at the factory, flush with the back face (adhesive HOLD)",
               "calculation", "HOLD", "CAD envelope; joints register H-27 and J-BASE-02 (D-129: the key sits 2.5 from the end)",
               "closes the side band's back end, face flush with Y = pod_d / 2"),
    "118002": ("levelling glide, M10 stem with a 5 mm hex socket on top, about 36 mm pad, static rating 3.5 kN or more "
               "(PM ruling 2026-11-01: the worst glide carries about 1.7 kN with two people leaning on one wall); base 6.5 mm or "
               "taller, so that screwed fully home against the M10 rivnut's head it holds the band at 8.5 mm: a hard stop "
               "(product HOLD)", "", "",
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
    "118001": ("HOLD (lip seal not named yet)", "HOLD", ""),
}
# tolerance per part: the drawing's, or for a part with no drawing the row's (D-89 parts 3 and 4)
TOLERANCE = {
    "111101": "see its drawing", "111103": "see its drawing",
    "111211": "the Joints Engineer's tabulated drawing 111211 to 111214",
    "111601": "ISO 2768-m; critical hole: Ø13 +0.10/0 for the glide's M10 rivnut (HOLD with the nut), centred +-0.2; DXF 111601",
    "831002": "joints register H-08: thickness +-0.05",
}

# band assemblies that carry glides (one M10 glide nut each) or bought end caps
BAND_ASSEMBLIES = ("110101", "110102", "110103", "110106")

# items not modelled in the CAD: (part number, name, name_vi, type, parent, qty rule, unit,
# material, finish, mass each kg, mass_status, status, source, note)
EXTRA = [
    ("838006", "HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD", "Tán rút M10 cho chân chỉnh", "PI", "band",
     "glides", "pcs", "aluminium or steel (HOLD)", "zinc plated steel or plain aluminium, with the product (HOLD)", 0.006,
     "assumption", "HOLD",
     "number PROPOSED for the joints register (glide nut)",
     "set through the band's 1.5 bottom face and the 5 mm load block, a 6.5 mm grip (PM ruling 2026-11-01), at the factory"),
    ("838007", "HARDWARE - COUNTERSUNK SCREW - M3 X 8 - ISO 10642 A2", "Vít đầu bằng M3 × 8 inox", "PI", "110106",
     "channel", "pcs", "stainless steel A2-70", "plain stainless, as supplied", 0.0006, "assumption", "DRAFT",
     "joints register J-FRONT-04 (838007)", "fixes FRONT's bottom U-channel to the sill at the factory (2 mm key)"),
    ("838008", "HARDWARE - RIVET NUT - M3 - COUNTERSUNK - HOLD", "Tán rút M3 đầu chìm", "PI", "110106",
     "channel", "pcs", "aluminium or steel (HOLD)", "zinc plated steel or plain aluminium, with the product (HOLD)", 0.0005,
     "assumption", "HOLD", "joints register J-FRONT-04 (838008, HOLD-16)", "flush in the sill's seat, at X 269.4, 484.3, 699.2, 905"),
    ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "seal",
     "lip", "m", "soft lip (sweep) seal, EPDM or TPE, black: a leg bonded to the band's inner face and a fin reaching "
     "seal_reach (21.5) below the band's bottom, so it presses on the room floor across the glides' range (product HOLD)",
     "black", 0.08, "assumption", "HOLD",
     "D-132 (PM ruling 2026-11-01: no floor); joints register 118001, renamed for D-132",
     "bonded along each band piece's inner face at the factory; v1's open shadow line under the band stays"),
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
    if rule == "channel":
        return 4 if "111301" in d["parts"] else 0
    raise ValueError(rule)


def size_text(rec):
    b = rec.get("box_mm")
    if not b:
        return ""
    dims = sorted((round(b[3] - b[0], 2), round(b[4] - b[1], 2), round(b[5] - b[2], 2)), reverse=True)
    return " x ".join("%g" % x for x in dims)


# modelled only as space envelopes; listed from EXTRA (the lip seal: in metres, from the CAD's runs, D-132)
BY_LENGTH = ("118001",)


def make_bom(d):
    parts = d["parts"]
    copies = {k: n for k, n in d["copies"].items() if k.split(">")[1] not in BY_LENGTH}
    per_pod = {}
    for k, n in copies.items():
        parent, child = k.split(">")
        mult = 1
        if parent != "110000":
            mult = copies.get("110000>%s" % parent, 1)
        per_pod[child] = per_pod.get(child, 0) + n * mult
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
        if parent == "seal":
            # the lip seal: one row per band assembly, its metres from the CAD's seal runs (D-132)
            per = {}
            for run in d.get("seal", []):
                per[run["host"]] = per.get(run["host"], 0.0) + run["length_mm"] / 1000.0
            for asm in sorted(per):
                if asm not in mass_of:
                    continue
                q = round(per[asm], 3)
                extra_rows.append((pn, name, vn, typ, asm, q, unit, mat, fin, m, ms, st, src, note))
                mass_of[asm] = round(mass_of[asm] + q * m, 4)
        elif parent == "band":
            # one per glide, in the band assembly that holds the glide
            for asm in BAND_ASSEMBLIES:
                q = copies.get("%s>118002" % asm, 0)
                if q:
                    extra_rows.append((pn, name, vn, typ, asm, q, unit, mat, fin, m, ms, st, src, note))
                    mass_of[asm] = round(mass_of[asm] + q * m, 4)
        else:
            if parent != "110000" and parent not in mass_of:
                continue                # its assembly isn't in this build (a later batch)
            q = extra_qty(d, rule, counts_total)
            if not q:
                continue
            extra_rows.append((pn, name, vn, typ, parent, q, unit, mat, fin, m, ms, st, src, note))
            if parent in BAND_ASSEMBLIES:
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
    print("wrote %s" % os.path.relpath(CUT, HERE))


def make_dxf(d):
    import ezdxf
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
                              "EN AW-6082 T6 plate 5 mm - mill finish - ISO 2768-m - mm",
                              "hole Ø%g +0.10/0 centred +-0.2 (the glide's M10 rivnut)" % gh)):
        dm.add_text(line, dxfattribs={"layer": "MARK", "height": 2.5}).set_placement((-gw / 2, gl / 2 + 4 + 4 * (2 - i)))
    ddoc.saveas(DBL_DXF)
    print("wrote %s: %.1f x %.1f, hole Ø%g at x %.1f" % (os.path.relpath(DBL_DXF, HERE), gw, gl, gh, gdx))
    make_dxf_p02(d, ezdxf)


def _dxf(ezdxf, layers):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for name, color in layers:
        doc.layers.add(name, color=color)
    return doc


def make_dxf_p02(d, ezdxf):
    """P02 batch 1 cut files: the sill's flat pattern (bend lines on BEND, inside radius = t, K 0.4: an
    assumption until the bender confirms)."""
    sl = d.get("sill")
    if sl:
        t = sl["t"]
        r, k = t, 0.4
        ba = math.pi / 2 * (r + k * t)            # bend allowance per 90 degree bend
        bd = 2 * (r + t) - ba                     # bend deduction
        legs = sl["legs_outside"]
        order = ("flange", "ledge", "drop", "seat", "kerb")
        flat = [legs[n] - (r + t) * (1 if i in (0, len(order) - 1) else 2) for i, n in enumerate(order)]
        width = sum(flat) + ba * (len(order) - 1)
        doc = _dxf(ezdxf, (("CUT", 7), ("BEND", 5), ("MARK", 1)))
        msp = doc.modelspace()
        ln = sl["length"]
        msp.add_lwpolyline([(0, 0), (ln, 0), (ln, width), (0, width)], close=True, dxfattribs={"layer": "CUT"})
        y = 0.0
        seat_mid = None
        for i, n in enumerate(order[:-1]):
            y += flat[i]
            if order[i + 1] == "seat":
                seat_mid = y + ba + flat[i + 1] / 2
            msp.add_line((0, y + ba / 2), (ln, y + ba / 2), dxfattribs={"layer": "BEND"})
            y += ba
        for x in sl["screws_x"]:
            msp.add_circle((x - sl["x0"], seat_mid), sl["rivnut_hole"] / 2, dxfattribs={"layer": "CUT"})
        msp.add_text("111301 P01 SILL - 2 mm, 4 bends 90 deg on BEND (inside radius %g, K %.1f: assumption) - flat %.2f x %.2f"
                     % (r, k, ln, width), dxfattribs={"layer": "MARK", "height": 5}).set_placement((5, width + 5))
        doc.saveas(os.path.join(HERE, "111301_%s_BASE-SILL-FIXED-GLASS_DXF.dxf" % REV))
        print("wrote the sill's flat pattern: %.2f x %.2f, bend deduction %.3f" % (ln, width, bd))


def main(argv):
    d = load()
    make_bom(d)
    make_cut_list(d)
    if "--dxf" in argv:
        make_dxf(d)


if __name__ == "__main__":
    main(sys.argv[1:])
