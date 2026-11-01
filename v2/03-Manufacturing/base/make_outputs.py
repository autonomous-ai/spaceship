"""BASE manufacturing outputs from the CAD's own facts.

    python3 v2/03-Manufacturing/base/make_outputs.py          # parts list + cut list
    PYTHONPATH=<dir with ezdxf> python3 ... --dxf               # also the DXFs (needs ezdxf)

Reads 110000_P01_BASE_DATA.json, which v2/01-CAD-Native/base/base_build.py
writes from the Fusion design (quantities = copies in the CAD, masses = the
CAD's physical properties, sizes = the bodies), and writes:

  110000_P01_BASE_BOM.csv                    parts list for the master BOM (v2/04-BOM)
  110000_P01_BASE-TUBE-CUT-LIST_SPEC.csv     cut lengths and end cuts of the tubes and angle
  111601_P01_..._DXF.dxf                     the glide doubler's outline and hole (D-89 part 4; with --dxf)
  <sill members>_P01_..._DXF.dxf             the welded sill's members: the bent profile's flat pattern, the door-end
                                             plate's blank (D-120; with --dxf)

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
    "838003": ("steel 1008/1010 (maker)", "zinc plated, trivalent passivation (maker)", "", "calculation", "DRAFT",
               "CAD envelope (as set); mass: calculation from the joints register's sizes (body Ø9.50 x 14.86, head "
               "Ø12.96 x 0.76, M6 bore, steel 7850 kg/m3), as AIR's and CEILING's lists; joints register H-03; "
               "Sherex CAH2-610-4.2 (steel, D-131)",
               "set at the factory; torque HOLD-01"),
    "111211": ("aluminium EN AW-6061 T6 block 30 x 35 x 75 (joints register J-BASE-02; sizes from the Joints Engineer 2026-11-01)",
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
    "110104": ("assembly: FL1 and FL2 (with its welded door-end block), the knee key 111214 in FL1's knee end with its 2 "
               "fixing screws and 2 hook studs, DL's 2 spigots in rivnuts and FL2's glide, fitted at the factory", "", "",
               "calculation", "DRAFT", "CAD 110000_P01_BASE_CAD; joints register J-BASE-02, J-FRONT-02",
               "goes on along the left side band's front key studs, then down 10 (J-BASE-02); DL stands on its 2 spigots"),
    "111104": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 with a welded 1.5 mm end plate (alloy: assumption)", AA20,
               "saw cut (both ends mitred), weld the corner end plate, CNC drill and cut the keyholes, deburr, anodise",
               "calculation", "DRAFT", "CAD; joints register J-BASE-02 (keyhole piece of the front left corner, carrier of "
               "the knee key 111214), J-FRONT-02 (DL's round spigot)",
               "DL's first facet; no glide (112 long between two keyed ends)"),
    "111105": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 with a welded 1.5 mm knee end plate, a welded 7 mm "
               "door-end block and a welded 2 mm door-end plate (alloy: assumption)", AA20,
               "saw cut (knee mitre, door end square to X), weld the knee end plate, the door-end block and the door-end "
               "plate, grind flush, CNC drill and cut the keyholes, deburr, anodise", "calculation", "DRAFT",
               "CAD; joints register J-BASE-02 (keyhole piece of the knee), J-FRONT-02 (DL's slot spigot); the door-end "
               "plate: the PM's ruling of 2026-11-01 on the door's hinge side (as D-150)",
               "DL's second facet, its block out to DL's door face (in view at the door opening, D-132); the door-end plate "
               "carries that face on inward to the kick strip's back line, from the band's bottom line up, with the lip "
               "118001 under it: the face FRONT's hinge-side brush closes on; on it, a welded strike pad (HOLD, 8 at most) for "
               "the drop seal's release button (FB-33); one glide"),
    "111212": ("aluminium EN AW-6061 T6 block (joints register J-BASE-02)", "mill finish (hidden)",
               "the Joints Engineer's part", "calculation", "DRAFT",
               "joints register J-BASE-02; the Joints Engineer's part (model, STEP and tabulated drawing 111211 to 111214), "
               "placed here by reference", "fixed in the left side band's front end at the factory; FL1 drops onto its 2 hook studs"),
    "111214": ("aluminium EN AW-6061 T6 block (joints register J-BASE-02)", "mill finish (hidden)",
               "the Joints Engineer's part", "calculation", "DRAFT",
               "joints register J-BASE-02; the Joints Engineer's part (model, STEP and tabulated drawing 111211 to 111214), "
               "placed here by reference", "fixed in FL1's knee end at the factory; FL2 goes on onto its 2 hook studs"),
    "110106": ("assembly: FR1 with its sill, FRONT's bottom U-channel screwed on, and the glides, fitted at the factory",
               "", "", "calculation", "DRAFT", "CAD; PM ruling 2026-11-01 (the channel ships fitted on the sill)",
               "ships as one piece; on site the fixed glass drops into the fitted channel"),
    "111106": ("aluminium 6063-T6 rectangular tube 100 x 40 x 1.5 with a welded 1.5 mm end plate (alloy: assumption)", AA20,
               "saw cut square, weld the end plate, CNC drill and cut the keyholes, deburr, anodise", "calculation", "DRAFT",
               "CAD; joints register J-BASE-02 (keyhole piece of the inline joint at x_fr_joint)",
               "X 218.5 to x_fr_joint; its glides are levelled by turning their base (no key holes on its visible top)"),
    "111301": ("welded: the bent profile and the door-end plate (D-120 members, below)", AA20,
               "weld the door-end plate into the bent profile all round (filler 5356: assumption), grind its outer face "
               "flush, anodise; then set the 4 M3 flush rivnuts 838008 in the seat", "calculation", "DRAFT",
               "CAD; FRONT's answer and the PM ruling of 2026-11-01; the door-end plate: D-150 (Reviewer 8's P1 on #303); "
               "members: D-120 (the Lead's ruling of 2026-11-01)",
               "the welded sill: ledge flush with the band top, seat under the U-channel, kerb down to the band's bottom "
               "line; the glass's load goes into FR1 (D-132); flange riveted to FR1 (rivets HOLD). Its door end is closed "
               "by the welded plate down to the band's bottom line, the lip 118001 along its bottom edge: the face FRONT's "
               "brush seal 368008 closes on (D-150). Its other end (X 965 = FR1's joint + 50) is closed by the intake's "
               "closing plate (batch 3)"),
    "111111": ("aluminium sheet EN AW-5005 H14, 2 mm (assumption)", AA20,
               "laser cut from its DXF, deburred, anodised black with the band", "calculation", "DRAFT",
               "CAD; D-165 (Control's number, the Lead's ruling of 2026-11-01: a made part, as no catalogue cap is 2 deep); "
               "D-129 (the key sits 2.5 from the side band's end); FR1's door end: D-132",
               "the tube end cap, 97 x 37 x 2, 3 a pod: a side band's back end (face flush with Y = pod_d / 2) or FR1's door "
               "end (face flush with X 218.5, at the door opening, in view), fixed into the band's open end at the factory "
               "with adhesive (product HOLD); no drawing: its DXF and this row (D-89 part 4)"),
    "111602": ("zinc-plated free-cutting steel without lead (11SMn30 / AISI 1215 or similar, assumption), turned in one piece: an M10 x 1.5 stem and a base "
               "40 across, 7.6 tall", "zinc plated, clear passivated (assumption)",
               "turned from bar, M10 x 1.5 rolled or cut, the 5 mm hex socket broached in the stem's top, zinc plated",
               "calculation", "DRAFT",
               "CAD; D-164 (the Lead's ruling of 2026-11-01 on the Sourcing Engineer's table: no catalogue glide has M10, a "
               "5 mm top socket, a base of 40 or less, 7.6 tall and 3.5 kN); static rating 3.5 kN or more with margin, "
               "proved by BASE test BT-04 (3.5 kN on its load block); the 8.5 stop: PM ruling on F-018",
               "the levelling glide, made to BASE's drawing; preset at the factory (D-87), levelled before the walls go on, up "
               "from the highest floor spot, never below 8.5 mm (the base screwed home on the M10 rivnut's 0.81 to 0.97 head: a "
               "hard stop): with a 5 mm hex key from above through the band top, or under FR1 (no holes in its top, in view) by "
               "turning the base (FB-24)"),
}

# bought items: (maker, exact SKU or standard designation, torque with its basis); HOLD where the
# product isn't named yet (its issue in the status and note). Standard fasteners are ordered by
# their standard designation from any maker; the catalogue number comes with the RFQ.
BOUGHT = {
    "838003": ("Sherex", "CAL2-610-4.2 (D-163: knurled round body, round hole 10.00 +0.10)",
               "HOLD-01: set and torque from the rivnut test (D-48); spin-out 4 N m or more in the real tubes (T06)"),
    "838001": ("standard part, any maker (catalogue number at RFQ)", "ISO 4762 M6 x 16 - 8.8, zinc plated",
               "HOLD: into the corner key's M6 threads, from the joint test J-T6 (joints register)"),
    "838004": ("standard part, any maker (catalogue number at RFQ)", "ISO 7093-1 - 6 - 200 HV - A2", ""),
    "838010": ("standard part, any maker (catalogue number at RFQ)", "ISO 7380-2 M6 x 12 - A2-70",
               "HOLD: into the corner key's M6 thread, from the joint test J-T6 (joints register)"),
    "838006": ("Sherex", "CAL2-1015-7.9 (D-163: knurled round body, round hole 13.50 +0.15)",
               "HOLD: set from the rivnut test (D-48); spin-out from T06"),
    "118001": ("Trim-Lok (candidate, BT-06 decides)", "X2248", ""),
    # the sill's channel fixings (joints register J-FRONT-04, H-28 and H-29): the screw is a standard part; the
    # rivnut's product is HOLD-16, and the screw's torque follows from it by D-48's rule
    "838007": ("HOLD: any maker to ISO 10642, picked at the RFQ", "ISO 10642 M3 x 8 - A2-70",
               "HOLD-16: set when the M3 rivnut 838008 is named, half its lowest spin-out torque (D-48's rule)"),
    "838008": ("HOLD-16: product to suit the sill's 2 mm seat wall (joints register H-29)", "HOLD-16",
               "HOLD-16: named with its grip and hole data (joints register); the screw's torque follows (D-48's rule)"),
}
# tolerance per part: the drawing's, or for a part with no drawing the row's (D-89 parts 3 and 4)
TOLERANCE = {
    "111101": "see its drawing", "111103": "see its drawing",
    "111211": "the Joints Engineer's tabulated drawing 111211 to 111214",
    "111212": "the Joints Engineer's tabulated drawing 111211 to 111214",
    "111214": "the Joints Engineer's tabulated drawing 111211 to 111214",
    "111104": "see its drawing", "111105": "see its drawing", "111602": "see its drawing",
    "111601": "ISO 2768-m; critical hole: Ø13.50 +0.15/0 for the glide's M10 rivnut 838006 (D-163), centred +-0.2; DXF 111601",
    "111111": "ISO 2768-m; outline 97 x 37 -0.2/-0.4 so it slides into the bore (assumption); DXF 111111",
    "111303": "ISO 2768-m; flat 2 mm plate, no holes; outline to the profile's inside faces, 0 to 0.5 gap for the weld "
              "(assumption); DXF 111303",
    "831002": "joints register H-08: thickness +-0.05",
}

# band assemblies that carry glides (one M10 glide nut each) or bought end caps
BAND_ASSEMBLIES = ("110101", "110102", "110103", "110104", "110106")

# items not modelled in the CAD: (part number, name, name_vi, type, parent, qty rule, unit,
# material, finish, mass each kg, mass_status, status, source, note)
EXTRA = [
    ("838006", "HARDWARE - RIVET NUT - M10 - FOR THE LEVELLING GLIDE - HOLD", "Tán rút M10 cho chân chỉnh", "PI", "band",
     "glides", "pcs", "steel C1008/1010 (maker)", "zinc plated with yellow trivalent chromate, SFS-01-001 SC2 (maker)", 0.0088,
     "source", "HOLD",
     "D-163: Sherex CAL2-1015-7.9, knurled round body, in a round hole 13.50 +0.15; the maker's drawing CAL2-1015-7.9 "
     "rev B: weight 0.0088 kg, grip 3.8 to 7.9, installed length 10.80 max, head Ø16.76 to 18.04 x 0.81 to 0.97; joints "
     "register (glide nut); T06's spin-out test confirms it",
     "set through the band's 1.5 bottom face and the 5 mm load block, a 6.5 mm grip (PM ruling 2026-11-01), at the factory"),
    ("838007", "HARDWARE - COUNTERSUNK SCREW - M3 X 8 - ISO 10642 A2", "Vít đầu côn lục giác chìm M3 × 8 inox", "PI", "110106",
     "channel", "pcs", "stainless steel A2-70", "plain stainless, as supplied", 0.0006, "assumption", "DRAFT",
     "joints register J-FRONT-04 (838007)", "fixes FRONT's bottom U-channel to the sill at the factory (2 mm key)"),
    ("838008", "HARDWARE - RIVET NUT - M3 - COUNTERSUNK HEAD - HOLD", "Tán rút M3 đầu côn", "PI", "110106",
     "channel", "pcs", "aluminium or steel (HOLD)", "zinc plated steel or plain aluminium, with the product (HOLD)", 0.0005,
     "assumption", "HOLD", "joints register J-FRONT-04 (838008, HOLD-16)", "flush in the sill's seat, at X 269.4, 484.3, 699.2, 905"),
    ("118001", "BASE - BASE SEAL - LIP - ROOM FLOOR - HOLD", "Gioăng môi sát sàn", "PI", "seal",
     "lip", "m", "soft lip (sweep) seal, EPDM or TPE, black: a leg bonded to the band's inner face and a fin reaching "
     "seal_reach (21.5) below the band's bottom, so it presses on the room floor across the glides' range. Candidate: "
     "Trim-Lok X2248, dense EPDM flap 19 to 20 long on a 14.2 x 2.3 leg with 3M acrylic tape, the leg set about 4 below "
     "the band's edge so the flap reaches about 23.5; BT-06 decides, an extrusion to BASE's drawing if it fails",
     "black", 0.08, "assumption", "HOLD",
     "D-132 (PM ruling 2026-11-01: no floor); joints register 118001, renamed for D-132; the candidate: the Sourcing "
     "Engineer's table and BASE's call (the Lead, 2026-11-01); its maker's drawing is on the owner's RFQ list",
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
        return parent_counts.get("111602", 0)
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

# bought parts whose mass isn't their CAD body's: the rivnut is modelled as set (10.16 long, the space it takes),
# but it weighs what it weighs before setting. Calculation from the joints register's CAH2-610-4.2 sizes (body
# Ø9.50 x 14.86, head Ø12.96 x 0.76, an M6 bore at the thread's minor diameter Ø4.92 through both, steel
# 7850 kg/m3: 857 mm3, 6.7 g), the figure AIR's and CEILING's lists give, so every list has one mass for 838003.
MASS_EACH = {"838003": 0.0067}


# the welded sill's members (D-120): their numbers come from Control, so their rows are keyed by the CAD's key
PART_INFO_BY_KEY = {
    "sill_bent": ("aluminium sheet EN AW-5005 H14, 2 mm (assumption)", AA20,
                  "laser cut, press brake (4 bends: inside radius = t, K 0.4, assumption; flat pattern in its DXF)",
                  "calculation", "DRAFT", "CAD; FRONT's answer and the PM ruling of 2026-11-01",
                  "member of the welded sill 111301: the bent profile with the 4 seat holes for the M3 rivnuts"),
    "sill_plate": ("aluminium sheet EN AW-5005 H14, 2 mm (assumption)", AA20,
                   "laser cut flat from the blank in its DXF; its 3 corners relieved C3 where they meet the profile's inside radii",
                   "calculation", "DRAFT", "CAD; D-150 (Reviewer 8's P1 on #303)",
                   "member of the welded sill 111301: the door-end plate, welded in all round, its outer face flush"),
}


def part_info(pn, rec):
    return PART_INFO[pn] if pn in PART_INFO else PART_INFO_BY_KEY[rec["key"]]


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
    mass_of.update({pn: m for pn, m in MASS_EACH.items() if pn in parts})
    # assembly masses: children's copies x mass, from the bottom up (the welded sill sits inside FR1's assembly)
    kids = {}
    for k, n in copies.items():
        parent, child = k.split(">")
        kids.setdefault(parent, []).append((child, n))

    def asm_mass(pn):
        if pn not in kids:
            return mass_of.get(pn, 0.0)
        return sum(n * asm_mass(c) for c, n in kids[pn])
    for asm in sorted(set(kids) - {"110000"}):
        mass_of[asm] = round(asm_mass(asm), 4)
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
                q = copies.get("%s>111602" % asm, 0)
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
        mat, fin, proc, ms, st, src, note = part_info(pn, rec)
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
    def emit(level, pn, parent, qpp, qpod):
        body.append(row(level, pn, parent, qpp, qpod))
        for c, n2 in sorted(kids.get(pn, [])):
            emit(level + 1, c, pn, n2, n2 * qpod)
        for r in extra_rows:
            if r[4] == pn:
                (xpn, name, vn, typ, xparent, q, unit, mat, fin, m, ms, st, src, note) = r
                body.append([level + 1, xpn, name, vn, typ, xparent, q, q * qpod, unit, mat, fin, "", "", "%.4f" % m,
                             "%.3f" % (m * q * qpod), ms, st, src, note] + tail(xpn))
    for child in sub:
        n = copies["110000>%s" % child]
        emit(1, child, "110000", n, n)
        total += n * mass_of.get(child, 0.0)
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
                              "hole Ø%g +0.15/0 centred +-0.2 (the glide's M10 rivnut 838006, D-163)" % gh)):
        dm.add_text(line, dxfattribs={"layer": "MARK", "height": 2.5}).set_placement((-gw / 2, gl / 2 + 4 + 4 * (2 - i)))
    ddoc.saveas(DBL_DXF)
    print("wrote %s: %.1f x %.1f, hole Ø%g at x %.1f" % (os.path.relpath(DBL_DXF, HERE), gw, gl, gh, gdx))
    # the tube end cap 111111 (D-165; D-89 part 4): the band's bore, 2 mm sheet, no holes
    if "111111" in d["parts"]:
        cw = param(d, "band_t") - 2 * param(d, "band_wall")
        ch = param(d, "band_h") - 2 * param(d, "band_wall")
        cdoc = _dxf(ezdxf, (("CUT", 7), ("MARK", 1)))
        cm_ = cdoc.modelspace()
        cm_.add_lwpolyline([(0, 0), (ch, 0), (ch, cw), (0, cw)], close=True, dxfattribs={"layer": "CUT"})
        for i, line in enumerate(("111111 P01 TUBE END CAP - 97 X 37 X 2 - AL BLACK - 3 a pod",
                                  "EN AW-5005 H14 sheet 2 mm - anodised black AA20 - ISO 2768-m - mm",
                                  "outline -0.2/-0.4 so it slides into the band's bore; bonded flush (adhesive HOLD)")):
            cm_.add_text(line, dxfattribs={"layer": "MARK", "height": 2.5}).set_placement((0, cw + 4 + 4 * (2 - i)))
        cpath = os.path.join(HERE, "111111_%s_BASE-TUBE-END-CAP-97-X-37-X-2-AL-BLACK_DXF.dxf" % REV)
        cdoc.saveas(cpath)
        print("wrote %s: %.1f x %.1f" % (os.path.relpath(cpath, HERE), ch, cw))
    make_dxf_p02(d, ezdxf)


def _dxf(ezdxf, layers):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    for name, color in layers:
        doc.layers.add(name, color=color)
    return doc


END_PLATE_RELIEF = 3.0   # mm, 45 deg chamfer: clears an inside bend radius of up to 3 (the sill's is t = 2: assumption)


def end_plate_blank(outline, relieve, c):
    """The door-end plate's cut outline: the CAD outline (u, w in mm) with a c x 45 deg chamfer at each corner listed in
    relieve (indices into outline), the point toward the previous corner first. A chamfer of c clears an inside bend
    radius r <= c: the bend's fillet meets each face r from the corner, and between those points it lies inside the
    chamfer line."""
    out = []
    n = len(outline)
    for i, (u, w) in enumerate(outline):
        if i not in relieve:
            out.append((u, w))
            continue
        for j in (i - 1, (i + 1) % n):
            pu, pw = outline[j]
            dl = math.hypot(pu - u, pw - w)
            if dl < c * (2 if j % n in relieve else 1) + 1:
                raise ValueError("end plate: edge %d-%d (%.1f) too short for a C%g relief" % (i, j % n, dl, c))
            out.append((u + (pu - u) / dl * c, w + (pw - w) / dl * c))
    return out


def dxf_name(pn, name):
    """PARTNO_REV_DESCRIPTIVE-NAME_DXF.dxf (conventions section 7), as base_build.py's file_name."""
    words = []
    for w in name.replace("Ø", "D").replace("(HOLD)", "").upper().replace(" - ", " ").replace("-", " ").split():
        w = "".join(ch for ch in w if ch.isalnum() or ch == ".")
        if w:
            words.append(w)
    return "%s_%s_%s_DXF.dxf" % (pn, REV, "-".join(words))


def make_dxf_p02(d, ezdxf):
    """P02 batch 1 cut files, one per member of the welded sill (D-120): the bent profile's flat pattern (bend lines on
    BEND, inside radius = t, K 0.4: an assumption until the bender confirms) and the door-end plate's blank."""
    sl = d.get("sill")
    if not sl:
        return
    names = {pn: rec["name"] for pn, rec in d["parts"].items()}
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
    msp.add_text("%s %s SILL BENT PROFILE - 2 mm, 4 bends 90 deg on BEND (inside radius %g, K %.1f: assumption) - flat "
                 "%.2f x %.2f" % (sl["pn_bent"], REV, r, k, ln, width),
                 dxfattribs={"layer": "MARK", "height": 5}).set_placement((5, width + 5))
    doc.saveas(os.path.join(HERE, dxf_name(sl["pn_bent"], names[sl["pn_bent"]])))
    print("wrote the sill's bent profile's flat pattern: %.2f x %.2f, bend deduction %.3f" % (ln, width, bd))
    ep = sl.get("end_plate")
    if ep:
        # the door-end plate's blank, welded in: its outline is the profile's inner faces (from the CAD), with a 45 deg
        # relief at each corner that meets an inside bend, so it clears the bend radius r; the weld closes the small
        # gap at the bend it wraps round
        pts = end_plate_blank(ep["outline"], ep["inside_bend_corners"], END_PLATE_RELIEF)
        doc = _dxf(ezdxf, (("CUT", 7), ("MARK", 1)))
        msp = doc.modelspace()
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
        u_max = max(u for u, _w in ep["outline"])
        w_max = max(w for _u, w in ep["outline"])
        msp.add_text("%s %s SILL DOOR-END PLATE - 2 mm, 1 off, welded in all round - %.1f x %.1f, reliefs C%g"
                     % (sl["pn_plate"], REV, u_max, w_max, END_PLATE_RELIEF),
                     dxfattribs={"layer": "MARK", "height": 5}).set_placement((0, w_max + 5))
        doc.saveas(os.path.join(HERE, dxf_name(sl["pn_plate"], names[sl["pn_plate"]])))
        print("wrote the sill's door-end plate's blank: %.1f x %.1f, %d corners relieved C%g"
              % (u_max, w_max, len(ep["inside_bend_corners"]), END_PLATE_RELIEF))


def main(argv):
    d = load()
    make_bom(d)
    make_cut_list(d)
    if "--dxf" in argv:
        make_dxf(d)


if __name__ == "__main__":
    main(sys.argv[1:])
