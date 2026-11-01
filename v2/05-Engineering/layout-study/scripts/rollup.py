"""Weight roll-up on skeleton P04 (ISS-081, F-010): the decided build recounted with tonight's rulings and CAD masses.

The base is this study's decided build (option B1 with the final stack, skeleton P03). Each line is replaced where a
newer number exists: the teams' CAD masses (CEILING PR #32, FRONT PRs #27, #28 and #105, the WALL group's L1), the air parts as
sized for D-60 (the air report, section 7f), and this study's own model re-run at skeleton P04's sizes for the parts with
no CAD yet. On top: the PM's adopted savings (ruling after PR #38) and allowances for parts not designed yet. Every line
carries its status and its source (SOURCES in inputs.py). run_all.py writes weight-rollup.md and out/parts-decided-P04.csv
from here, and its --check proves they reproduce. The mechanical check sums the CSV for F-010 and leaves out the voice kit's
line, which is outside the cap (PR #40).
"""
import os
import sys

from inputs import override, p
from shapes import al_rhs, plate_kg
from v2_model import FINAL, final_leaf_kg, final_outer_kg, parts_for, total

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "acoustics-air"))
import calc as AA  # noqa: E402  (the air report's own model: D-60's air parts)

SKELETON_CSV = os.path.join(HERE, "..", "..", "..", "01-CAD-Native", "skeleton", "100000_P04_POD-SKELETON-PARAMETERS.csv")


def _skeleton():
    import csv
    with open(SKELETON_CSV, encoding="utf-8") as f:
        return {r["parameter"]: float(r["value"]) for r in csv.DictReader(f)}


SKEL = _skeleton()


def skel(name):
    """A named value of skeleton P04 (S33), linked by its name; a missing name stops the study."""
    if name not in SKEL:
        raise KeyError(f"skeleton P04 has no parameter {name!r} ({SKELETON_CSV})")
    return SKEL[name]


# ---------------------------------------------------------------------------------------- CAD masses on main
MANUF = os.path.join(HERE, "..", "..", "..", "03-Manufacturing")


def read_parts_list(path):
    """The rows of a merged parts list: dicts with level, pn, name, material, qty, kg (the row's total mass)."""
    import csv
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            kg = r.get("mass_total_kg") or ""
            each = r.get("mass_each_kg") or r.get("unit_mass_kg") or ""
            if not kg and each:
                kg = float(each) * float(r.get("qty") or 1)
            out.append(dict(level=int(r.get("level") or 0), pn=(r.get("part_number") or "").strip(), name=r.get("name", ""),
                            material=r.get("material", ""), qty=float(r.get("qty") or r.get("qty_per_parent") or 0),
                            kg=float(kg or 0), each=float(each or 0)))
    return out


def wall_side_cad(n):
    """WALL's side panel 21010n and its lining cassette 51010n from the merged parts list (PRs #41, #104): the made
    parts and the bond set per panel; the hardware stays in the fixings kit's line, the clips in the named clips' line."""
    import glob
    import re
    path = glob.glob(os.path.join(MANUF, "wall", f"21010{n}_P01_*_BOM.csv"))[0]
    rows = read_parts_list(path)
    by = {r["pn"]: r for r in rows if r["pn"]}
    fr, sk, fi, asm, cas = f"21110{n}", f"21130{n}", f"21150{n}", f"21010{n}", f"51010{n}"
    frame = rows.index(by[fr])
    mids = [r for r in rows[frame + 1:] if r["level"] == 2 and "STILE - MID" in r["name"].upper()]
    rho = float(re.search(r"(\d+(?:\.\d+)?)\s*kg/m3", by[fi]["material"]).group(1))
    t_mid = float(re.search(r"x\s*(\d+(?:\.\d+)?)\s*$", mids[0]["material"].strip()).group(1))
    panel = rows[rows.index(by[asm]) + 1:rows.index(by[cas])]
    hardware = sum(r["kg"] for r in panel if r["level"] == 1 and r["pn"] not in (fr, sk, fi, "108002"))
    seals = sum(by[k]["kg"] for k in ("848011", "848012") if k in by and rows.index(by[k]) > rows.index(by[cas]))
    return dict(path=os.path.basename(path), frame=by[fr]["kg"], skin=by[sk]["kg"], fill=by[fi]["kg"], fill_rho=rho,
                bond=by["108002"]["kg"], mid_kg=sum(r["kg"] for r in mids), mid_n=int(sum(r["qty"] for r in mids)),
                mid_t=t_mid, hardware=hardware, tray=by[f"51110{n}"]["kg"], felt=by[f"51130{n}"]["kg"], cass_seals=seals,
                clips=by["518001"]["kg"])


WALL_SIDE = {n: wall_side_cad(n) for n in (1, 2, 3, 4)}      # L1, R1, L2, R2 (S34)
WALL_L1 = WALL_SIDE[1]


def wall_back_cad(n):
    """WALL's back panel 21020n and its lining cassette 51020n from the merged parts list (PR #152): the made parts and
    the bond set per panel; the hardware stays in the fixings kit's line, the clips in the named clips' line."""
    import glob
    import re
    path = glob.glob(os.path.join(MANUF, "wall", f"21020{n}_P01_*_BOM.csv"))[0]
    rows = read_parts_list(path)
    by = {r["pn"]: r for r in rows if r["pn"]}
    fr, sk, fi, cas = f"21120{n}", f"21140{n}", f"21160{n}", f"51020{n}"
    mids = [r for r in rows[rows.index(by[fr]) + 1:rows.index(by[sk])]
            if r["level"] == 2 and "STILE - MID" in r["name"].upper()]
    rho = float(re.search(r"(\d+(?:\.\d+)?)\s*kg/m3", by[fi]["material"]).group(1))
    t_mid = float(re.search(r"x\s*(\d+(?:\.\d+)?)\s*$", mids[0]["material"].strip()).group(1))
    seals = sum(by[k]["kg"] for k in ("848011", "848012") if k in by and rows.index(by[k]) > rows.index(by[cas]))
    return dict(path=os.path.basename(path), frame=by[fr]["kg"], skin=by[sk]["kg"], fill=by[fi]["kg"], fill_rho=rho,
                bond=by["108002"]["kg"], mid_kg=sum(r["kg"] for r in mids), mid_n=int(sum(r["qty"] for r in mids)),
                mid_t=t_mid, tray=by[f"51120{n}"]["kg"], felt=by[f"51140{n}"]["kg"], cass_seals=seals)


WALL_BACK = {n: wall_back_cad(n) for n in (1, 2)}            # B1 and B2, the lower back panels (S50)
FRONT_DOOR_LIST = os.path.join(MANUF, "front", "360001_P01_FRONT-DOOR-UNIT_BOM.csv")        # PR #27 (S36)


def front_door_cad(path=FRONT_DOOR_LIST):
    """FRONT's door unit from its merged parts list (PR #27): the unit's total, the leaf and the kick strip."""
    by = {r["pn"]: r for r in read_parts_list(path) if r["pn"]}
    return dict(unit=by["360001"]["kg"], leaf=by["361001"]["kg"], kick=by["361002"]["kg"])


FRONT_DOOR = front_door_cad()
FRONT_FIXED_LIST = os.path.join(MANUF, "front", "360002_P01_FRONT-FIXED-GLASS-UNIT_BOM.csv")  # PR #28 (S37)


def front_fixed_cad(path=FRONT_FIXED_LIST):
    """FRONT's fixed glass unit from its merged parts list (PR #28): the unit's total and the pane."""
    by = {r["pn"]: r for r in read_parts_list(path) if r["pn"]}
    return dict(unit=by["360002"]["kg"], pane=by["361003"]["kg"])


FRONT_FIXED = front_fixed_cad()
FRONT_DECOR_PN = {"DL": "350001", "DT": "350002", "DR": "350003"}                           # PR #105 (S51)


def front_decor_cad(block):
    """FRONT's decor block from its merged parts list (PR #105): the block's total, its skin, its welded frame and how
    many tubes it has, and the reserved air spaces it lists with no mass (AIR's parts, counted in AIR's lines). The
    block's row must be the sum of the rows under it."""
    import csv
    import glob
    import re
    pn = FRONT_DECOR_PN[block]
    path = glob.glob(os.path.join(MANUF, "front", f"{pn}_P01_*_BOM.csv"))[0]
    with open(path, encoding="utf-8") as f:
        types = {r["part_number"]: r["type"] for r in csv.DictReader(f)}
    rows = read_parts_list(path)
    by = {r["pn"]: r for r in rows if r["pn"]}
    rest = sum(r["kg"] for r in rows if r["pn"] != pn)
    if abs(rest - by[pn]["kg"]) > 0.01:
        raise ValueError(f"{os.path.basename(path)}: the block's row {by[pn]['kg']} isn't the sum of its rows {rest:.3f}")
    skin = [r for r in rows if "DECOR SKIN" in r["name"]]
    frame = [r for r in rows if "DECOR FRAME" in r["name"]]
    tubes = re.search(r"welded frame, (\d+) tubes", types[frame[0]["pn"]])
    return dict(path=os.path.basename(path), pn=pn, unit=by[pn]["kg"], skin=skin[0]["kg"], frame=frame[0]["kg"],
                tubes=int(tubes.group(1)), reserved=[k for k, t in types.items() if t == "reserved air space"])


FRONT_DECOR = {b: front_decor_cad(b) for b in ("DL", "DT", "DR")}


def dr_channels_kg(path=FRONT_FIXED_LIST):
    """The fixed glass's right and diagonal U-channels with their U-seal, which ship fitted in DR (D-68), kg: the
    U-profile's and the U-seal's masses in its parts list (S37) shared by the four pieces' lengths in the profile's note,
    as the packing plan shares them."""
    import csv
    import re
    with open(path, encoding="utf-8") as f:
        rows = {r["part_number"]: r for r in csv.DictReader(f)}
    m = re.search(r"outer lengths ([\d.]+) / ([\d.]+) / ([\d.]+) / ([\d.]+) mm \(bottom, right, diagonal, top\)",
                  rows["368004"]["note"])
    if not m:
        raise ValueError(f"{os.path.basename(path)}: no piece lengths in the U-profile's note")
    bottom, right, diag, top = (float(x) for x in m.groups())
    kg = sum(float(rows[k]["unit_mass_kg"]) * float(rows[k]["qty"] or 1) for k in ("368004", "368002"))
    return kg * (right + diag) / (bottom + right + diag + top)
BASE_LIST = os.path.join(MANUF, "base", "110000_P01_BASE_BOM.csv")                           # PR #55 (S44)


def base_cad(path=BASE_LIST):
    """BASE's P01 sample from its merged parts list (PR #55): the back-left corner and F1, unit masses by part number. The
    right side band and F2 are taken as the mirrors of the left side band and F1; the front bands and front corner keys
    come in BASE P02."""
    by = {}
    for r in read_parts_list(path):
        if r["pn"] and r["pn"] not in by:
            by[r["pn"]] = r
    return dict(band_side=by["111101"]["each"], band_back=by["111103"]["each"], key_back=by["111211"]["each"],
                doubler=by["111601"]["each"], glide=by["118002"]["each"], floor=by["111401"]["each"],
                mat=by["111501"]["each"])


BASE_CAD = base_cad()
JOINTS_LIST = os.path.join(MANUF, "joints", "V2-MFG-JNT-01_P01_JOINTS-MADE-HARDWARE_SPEC.csv")  # PR #139 (S45)


def joints_cad(path=JOINTS_LIST):
    """The joints' made hardware from its merged list (PR #139): the corner key family and the spigots and stop washers,
    as (count per pod, kg each) by part number."""
    import csv
    with open(path, encoding="utf-8") as f:
        return {r["part_number"]: (int(float(r["qty_per_pod"])), float(r["mass_each_kg"])) for r in csv.DictReader(f)}


JOINTS = joints_cad()
REGISTER = os.path.join(HERE, "..", "..", "joints", "joints-register.md")                    # D-116 (S48)
FIXING_PNS = ("838001", "838002", "838003", "838004", "838005", "848001", "848004")  # bolts, rivnuts, washers, retainers,
                                                                                    # joint gasket, closing-seam bulb seal


def register_counts(path=REGISTER):
    """Per-pod counts of the site fixings from the joints register's part-number table (H-rows): the M6 x 16 bolts on site
    and in the factory, then the first number of each other row (pieces, or metres for the gasket and the bulb seal)."""
    import re
    out = {}
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 7 or not cells[1].startswith("H-"):
            continue
        pn = cells[2].strip("* ")
        if pn not in FIXING_PNS or pn in out:
            continue
        cell = cells[5]
        if pn == "838001":
            out[pn] = sum(float(n) for n in re.findall(r"(\d+) (?:on site|in the factory)", cell))
        else:
            out[pn] = float(re.search(r"\d+(?:\.\d+)?", cell).group(0))
    return out


def fixings_unit_kg():
    """Each fixing's mass from the merged parts lists (WALL's L1 list first, then CEILING's): per piece, or per metre."""
    import glob
    out = {}
    for path in [glob.glob(os.path.join(MANUF, "wall", "210101_P01_*_BOM.csv"))[0], CEILING_LIST]:
        for r in read_parts_list(path):
            if r["pn"] in FIXING_PNS and r["pn"] not in out and r["each"]:
                out[r["pn"]] = r["each"]
    return out


def fixings_kg():
    """The site fixings by the joints register's counts and the parts lists' masses (D-116, S48)."""
    n, kg = register_counts(), fixings_unit_kg()
    return sum(n[pn] * kg[pn] for pn in FIXING_PNS)
CEILING_LIST = os.path.join(MANUF, "ceiling", "410000_P01_CEILING-PARTS-LIST_BOM.csv")       # PR #32 (S35)


def ceiling_cad(path=CEILING_LIST):
    """CEILING's panels C1 and C2 and the common cassette from the merged parts list (PR #32): each panel's frame, skin and
    bond set; per cassette the tray, its ribs, the felt and the three fill bays at the list's fill density. The clips and
    catches stay in the named clips' line, the hardware and seals in the fixings kit's line."""
    import re
    by, pod = {}, {}
    for r in read_parts_list(path):
        if r["pn"] and r["pn"] not in by:
            by[r["pn"]] = r
    import csv
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pod.setdefault(r["part_number"], float(r.get("qty_per_pod") or 0))
    ncass = pod["510301"]
    fills = [by[k]["each"] for k in ("513301", "513302", "513303")]
    rho = float(re.search(r"(\d+(?:\.\d+)?)\s*kg/m3", by["513301"]["material"]).group(1))
    return dict(c1=by["411101"]["each"] + by["411301"]["each"] + by["108002"]["each"],
                c2=by["411102"]["each"] + by["411302"]["each"] + by["108002"]["each"], bond=by["108002"]["each"],
                frames=(by["411101"]["each"], by["411102"]["each"]), skins=(by["411301"]["each"], by["411302"]["each"]),
                tray=by["513101"]["each"], ribs=by["513102"]["each"] * pod["513102"] / ncass, felt=by["513201"]["each"],
                fill=sum(fills), fill_rho=rho)


CEILING = ceiling_cad()
ELEC_LIST = os.path.join(MANUF, "electrical", "710000_P01_ELECTRICAL-PARTS-LIST_BOM.csv")      # PR #64 (S43)


def electrical_cad(path=ELEC_LIST):
    """ELECTRICAL from its merged parts list (PR #64): the total as shipped, the power unit, and the LED strip per metre;
    and the parts it lists under another team's assembly, by host (S53: D-126's down-light profile, cover, end caps and
    clips under INTERIOR's light shelf 810201). 710000's total leaves those out; the host's line carries them."""
    import csv
    with open(path, encoding="utf-8") as f:
        rows = {r["part_number"]: r for r in csv.DictReader(f)}
    hosted = {}
    for r in rows.values():
        if r["parent"] and r["parent"] not in rows:          # its parent is another team's part
            hosted.setdefault(r["parent"], []).append((r["part_number"], float(r["qty_per_parent"]), float(r["mass_each_kg"])))
    return dict(total=float(rows["710000"]["mass_each_kg"]), power_unit=float(rows["710001"]["mass_each_kg"]),
                hub=float(rows["710041"]["mass_each_kg"]), cord=float(rows["719001"]["mass_each_kg"]),
                strip_kgm=float(rows["718050"]["mass_each_kg"]), strip_m=float(rows["718050"]["qty_per_pod"]),
                hosted=hosted)


ELEC = electrical_cad()
INTERIOR_LIST = os.path.join(MANUF, "interior", "810000_P01_INTERIOR-PARTS-LIST_BOM.csv")     # PR #92 (S46)


SHELF_REPLACED = ("811204", "811205")     # D-126 (S53): the down-light channel and diffuser, replaced by ELECTRICAL's bought profile


def interior_cad(path=INTERIOR_LIST, hosted=None):
    """INTERIOR from its merged parts list (PR #92): the work-wall ledge, the light shelf (its LED strip is ELECTRICAL's)
    and the screen rail (HOLD). The shelf assembly 810201 also holds ELECTRICAL's down-light profile parts, listed in
    ELECTRICAL's parts list under it (S53), and they ship with it; the channel and diffuser they replaced (D-126) are left
    out while INTERIOR's list still carries them."""
    import csv
    with open(path, encoding="utf-8") as f:
        rows = {r["part_number"]: r for r in csv.DictReader(f)}
    kg = lambda pn: float(rows[pn]["mass_each_kg"])
    gone = [pn for pn in SHELF_REPLACED if pn in rows and rows[pn]["parent"] == "810201"]
    gone_kg = sum(float(rows[pn]["qty_per_parent"]) * kg(pn) for pn in gone)
    elec = (hosted or {}).get("810201", [])
    elec_kg = sum(q * m for _pn, q, m in elec)
    return dict(ledge=kg("810101"), shelf=kg("810201") - gone_kg + elec_kg, rail=kg("818102"),
                total=kg("810000") - gone_kg + elec_kg, shelf_listed=kg("810201"), shelf_gone=gone, shelf_gone_kg=gone_kg,
                shelf_elec=[pn for pn, _q, _m in elec], shelf_elec_kg=elec_kg)


def shelf_note():
    """What the light shelf's CAD mass holds beyond INTERIOR's 810201 (S53), for the line texts."""
    it, out = INTERIOR, []
    if it["shelf_elec"]:
        out.append(f"with ELECTRICAL's down-light profile, cover, end caps and clips {it['shelf_elec'][0]} to "
                   f"{it['shelf_elec'][-1]} ({it['shelf_elec_kg']:.3f}), listed under 810201 (S53)")
    if it["shelf_gone"]:
        out.append(f"less the channel and diffuser {' and '.join(it['shelf_gone'])} ({it['shelf_gone_kg']:.3f}) that D-126 "
                   "replaced, which INTERIOR's list still carries")
    return "; ".join(out)


INTERIOR = interior_cad(hosted=ELEC["hosted"])
AIR_LIST = os.path.join(MANUF, "air", "610000_P01_AIR-PARTS-LIST_BOM.csv")                    # PR #91 (S52)
AIR_FBOX_T_CAD = 2.0      # mm: the fan box casings as PR #91's CAD builds them; D-124's 3 mm comes with the AIR follow-up
AIR_RISER_FOOT_KG = 0.5   # kg: the air report's allowance for the riser's foot and the mesh band piece (assumption)


def air_cad(path=AIR_LIST):
    """AIR from its parts list (PR #91): each number's mass (its first row: the fans sit under both fan boxes), the
    densities the CAD gives the column's and soffit's fill and the cartridge layers, and the layers per cartridge."""
    import csv
    import re
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.setdefault(r["part_number"], r)
    rho = lambda pn: float(re.search(r"(\d+(?:\.\d+)?)\s*kg/m3", rows[pn]["material"]).group(1))
    return dict(kg={pn: float(r["mass_each_kg"]) for pn, r in rows.items()}, fill_rho=rho("611104"),
                sof_fill_rho=rho("611203"), layer_rho=rho("611302"), n_layers=float(rows["611302"]["qty_per_parent"]))


AIR = air_cad()


def air_unmodelled():
    """What AIR's CAD doesn't model yet, sized as the air report sizes it (calc.py d60_parts): each fan box's 2 mm
    bulkhead (less the two fan bores) and its 50 mm linings at 32 kg/m3 where they fit (D-121), kg."""
    import math
    t_fb, holes = AA.CASINGS[AA.FANBOX_CASING][2] / 1000, 2 * math.pi / 4 * AA.FAN_BORE ** 2
    bulk_kg_m2 = AA.MAT["alu"][0] * AA.FANBOX_BULKHEAD_MM / 1000
    (bx0, bx1), (by0, by1), _bz = AA.D60["sup_box"]
    (ex0, ex1), (ey0, ey1), _ez = AA.D60["exh_box"]
    rooms = AA.fanbox_rooms()
    lin = lambda side: rooms[side]["lined"] * AA.D60["lin"] / 1000 * AA.FANBOX_LINING_KG_M3
    return {"supply bulkhead": (((bx1 - bx0) / 1000 - 2 * t_fb) * ((by1 - by0) / 1000 - 2 * t_fb) - holes) * bulk_kg_m2,
            "exhaust bulkhead": (((ex1 - ex0) / 1000 - t_fb) * ((ey1 - ey0) / 1000 - 2 * t_fb) - holes) * bulk_kg_m2,
            "supply linings": lin("supply"), "exhaust linings": lin("exhaust")}


def air_parts(fill):
    """AIR's lines from its CAD (S52), by the pieces the packing plan reads: [(item, kg, status, source)]. On top of the
    CAD: the changes already ruled that the AIR follow-up builds (the CAD has the earlier values until it merges): the
    column's and the soffit's fill at `fill` (D-81; the CAD has 32 kg/m3), the cartridge layers at 32 kg/m3 (D-116; the
    CAD has 40) and the fan box casings in 3 mm (D-124; the CAD has 2 mm); and what the CAD doesn't model yet, sized as
    the air report sizes it: each fan box's 2 mm bulkhead and its 50 mm linings where they fit (D-121), and the riser's
    foot and mesh band piece. The fans are a line of their own."""
    k, t3, un = AIR["kg"], AA.CASINGS[AA.FANBOX_CASING][2], air_unmodelled()
    rooms = AA.fanbox_rooms()
    layer = k["611302"] * AA.CART_LAYER_KG_M3 / AIR["layer_rho"]
    cart = k["611301"] + AIR["n_layers"] * layer
    col_fill, sof_fill = k["611104"] * fill / AIR["fill_rho"], k["611203"] * fill / AIR["sof_fill_rho"]
    sc = t3 / AIR_FBOX_T_CAD
    col = k["610101"] - k["611104"] + col_fill
    sof = k["610201"] - k["610402"] - k["611203"] + sof_fill
    sbox = k["611402"] * sc + k["618102"] + k["618103"] + un["supply bulkhead"] + un["supply linings"]
    ebox = k["611401"] * sc + un["exhaust bulkhead"] + un["exhaust linings"]
    cad = "S52, CAD on main: AIR parts list "
    lay = (f"{AIR['n_layers']:.0f} layers 611302 at {AA.CART_LAYER_KG_M3:.0f} kg/m3 (D-116; the CAD has "
           f"{AIR['layer_rho']:.0f} until the AIR follow-up)")
    return [
        ("Supply cartridge, in the air column", cart, "calculation (CAD)",
         f"{cad}610301 P01: casing 611301 {k['611301']:.3f} (2.0 mm, D-121), " + lay),
        ("Exhaust cartridge, in the soffit", cart, "calculation (CAD)", f"{cad}610301 P01, the same part"),
        ("Air column 610101: felt-covered faces, corner angles, foot and plenum plates, fill, kick grille", col,
         "calculation (CAD)", f"{cad}610101 P01 {k['610101']:.3f}, its fill 611104 at {fill:g} kg/m3 (D-81; the CAD has "
         f"{AIR['fill_rho']:.0f} until the AIR follow-up); the hub zone 618101 is the in-house module's (no mass here)"),
        ("Soffit 610201: underside sections, front face, rails, end and door-side plates, fill, exhaust grille, hangers, "
         "hinges, latches, lock screws", sof, "calculation (CAD); hinges, latches and studs HOLD",
         f"{cad}610201 P01 {k['610201']:.3f} less its exhaust fan box {k['610402']:.3f} (the next line but one), its fill "
         f"611203 at {fill:g} kg/m3 (D-81; the CAD has {AIR['sof_fill_rho']:.0f})"),
        ("Supply fan box 610401 with its two transitions, in the right block", sbox,
         "calculation (CAD at 2 mm, scaled to D-124's 3 mm); transitions HOLD at their sized masses",
         f"{cad}610401 P01: {sbox:.2f} kg = casing 611402 {k['611402'] * sc:.2f} (the CAD's {k['611402']:.3f} at "
         f"{AIR_FBOX_T_CAD:g} mm x {t3:g}/{AIR_FBOX_T_CAD:g}: D-124's {t3:g} mm casing, which the model gets in the AIR "
         f"follow-up) + transitions 618102 {k['618102']:.2f} and 618103 {k['618103']:.2f} (HOLD, sized) + not in the CAD "
         f"yet (D-121, the air report's sizes): a {AA.FANBOX_BULKHEAD_MM:g} mm bulkhead {un['supply bulkhead']:.2f} and "
         f"50 mm linings at {AA.FANBOX_LINING_KG_M3:g} kg/m3 where they fit, {rooms['supply']['lined']:.3f} m2, "
         f"{un['supply linings']:.2f}; the fans are in their own line"),
        ("Exhaust fan box 610402, in the soffit", ebox,
         "calculation (CAD at 2 mm, scaled to D-124's 3 mm)",
         f"{cad}610402 P01: {ebox:.2f} kg = casing 611401 {k['611401'] * sc:.2f} (the CAD's {k['611401']:.3f} at "
         f"{AIR_FBOX_T_CAD:g} mm x {t3:g}/{AIR_FBOX_T_CAD:g}: D-124's {t3:g} mm casing, which the model gets in the AIR "
         f"follow-up) + not in the CAD yet (D-121, the air report's sizes): the fans' "
         f"sealed {AA.FANBOX_BULKHEAD_MM:g} mm bulkhead {un['exhaust bulkhead']:.2f} and 50 mm linings where they fit, "
         f"{rooms['exhaust']['lined']:.3f} m2, {un['exhaust linings']:.2f}; the fans are in their own line"),
        ("Intake riser 611501, in the right block", k["611501"] + AIR_RISER_FOOT_KG + AA.BOOT_KG,
         "calculation (CAD); foot, mesh and boot assumption",
         f"{cad}611501 P01 {k['611501']:.3f} (1 mm galvanised steel, 139 x 155 x 1340; D-130's 150 deep comes with the "
         f"AIR follow-up), {AIR_RISER_FOOT_KG:g} kg for its foot and the mesh band piece's extra over the band it replaces, "
         f"and {AA.BOOT_KG:g} kg for D-130's sealed intake boot and the cartridges' gaskets (the air report's assumptions)"),
        ("Roof slot grille 611602 and roof sleeve 611601, with C2", k["611602"] + k["611601"], "calculation (CAD)",
         f"{cad}611602 P01 {k['611602']:.3f} and 611601 P01 {k['611601']:.3f}: the sleeve fills C2's roof slot, so it "
         "can't ride on the exhaust fan box while the soffit is lifted and slid onto its studs; it ships with the grille "
         "and C2 and drops in through the slot after the soffit hangs, onto a gasket on the fan box's top (the Air "
         "Engineer, 2026-11-01)"),
    ]
KEY_PNS = ("111211", "111212", "111213", "111214")            # the corner key family: square, front LH and RH, knee LH

CAP_KG = 420.0          # confirmed, D-37 and D-54
TARGET_KG = 410.0       # confirmed: D-81's target for the pod as shipped (S40)
D71_KG = 429.3          # the PM's running estimate (D-71, S39), for the cross-check
D71_LEFT_OUT = 1.3 + 0.5 + 2.1   # corner tubes, bond, floor foam: D-71's "not in the sum yet" (S39)

# Skeleton P04 sizes, mm (S33)
P04 = dict(side_w=skel("side_l"), side_h=skel("side_h"), side_up_h=skel("side_h"), back_w=skel("half_pw"),
           back_h=skel("back_ph"), ceil_w=skel("half_pw"), wall_depth=skel("wall_depth"), frame_d=skel("frame_t"),
           back_fw=skel("half_fw"),                    # linked to the skeleton's named values (S33)
           # not named in the skeleton: the linings and the floor panels, from its build record (S33)
           side_cass_l=1445.0, side_cass_lo_h=1142.74, side_cass_up_h=1092.74, back_cass_w=1166.0,
           back_cass_lo_h=1118.61, back_cass_up_h=1116.87, floor_w=1210.0, floor_d=1455.0)
# The teams' CAD masses, kg (status calculation: CAD geometry x density)
WALL_L1_BOND = WALL_L1["bond"]                                 # S34: WALL's bond set per side panel
CEIL_PANEL, CEIL_CASS = 9.586, 9.816   # kg: PR #32's first list (P03 build), the estimates before its CAD merged
CEIL_TRAY = (1163.0, 1048.0)                                  # S35: the cassette tray's outline as built
CEIL_FILL_M2 = 1.11674 * (0.33875 + 0.33875 + 0.27475)        # S35: the three fill strips on each cassette's back
DOOR_UNIT_DRAFT = 50.17       # kg: the door unit in PR #27's first parts list (S36), the estimate before its CAD merged
DOOR_GLASS = FRONT_DOOR["leaf"]                               # S36: the 4+4 leaf, CAD on main
FIXED_UNIT_DRAFT = 29.58      # kg: the fixed glass unit in PR #28's first parts list (S37), the estimate before its CAD merged
FIXED_GLASS = FRONT_FIXED["pane"]                             # S37: the 4+4 pane, CAD on main
LIP_KG = 0.43                 # confirmed, D-69: each wall cassette with the 12 mm lips (S39)
CORNER_TUBES_KG = 1.3         # confirmed, D-63 (S39)
BOND_OVER_KG = 0.5            # calculation, PR #23 via D-71: bond over this study's 0.25 kg/m2 (S39)
FLOOR_T, FOAM_KG = skel("floor_t"), 2.1  # confirmed, D-72 (9 mm plywood); calculation, D-76 (3 mm foam, about 200 kg/m3)
SKEL_STACK = skel("stack_t")  # mm: outer panel 46 + the floating lining, wall face to lining face (S33)
# D-81, the PM's weight ruling on PR #38 (S40): adopted now, two of them provisional on a test or a check
FILL_LIGHT = 24.0             # kg/m3: the default now, provisional on T02 (D-54, D-81); the grade Pyrotek lists and the
                              # sample tests
CLIP_KG, CATCH_KG = 0.04, 0.10  # assumption: clip-only fixing, no rails (adopted), about 40 g a clip and 100 g a catch
                                # lanyard until H03 and H04 name them
BAND_T_LIGHT = 1.5            # mm: the base band's wall (adopted, provisional on BASE's check; this study's 2.0 is S07's)
# Budgets and allowances for parts that aren't designed yet (assumption)
SHELF_KGM_ALLOW, SHELF_KGM = 0.6, 0.4  # kg/m: the light shelf with its LED strip (D-70): the first allowance, and D-85's
                                       # budget as a 1.2 mm aluminium angle
SHELF_BRACKETS_KG = 0.4       # kg: its brackets at about 400 mm
LEDGE_KG_ALLOW, LEDGE_KG = 2.3, 1.4    # kg: the work wall's 1000 mm ledge (D-70): 12 mm ply at 650 kg/m3 with 2 brackets,
                                       # and D-85's budget in 1.5 mm folded aluminium (1000 x 240 developed) with 2 brackets
# D-85, the PM's pick toward the 410 kg target (S41)
T_STUD_LIGHT = 1.0            # mm: inner studs of the wall panels' 20 x 40 frames; the perimeters keep D-34's 1.2 for the
                              # rivnuts, and the ceiling's inner members stay 1.2 for the overhead clips and catches (D-85)
BACK_STUDS = 2                # inner studs in each back outer panel: 393 mm centres, inside D-16's 400 (this study counted 3)
KICK_KG, KICK_KG_HOLLOW = 2.094, 1.0  # kg: the solid kick strip of PR #27's first list (S36) and D-85's hollow budget
FLOOR_RHO_LIGHT = 450.0       # kg/m3: poplar-core 9 mm plywood against this study's 600 (S13); D-85, settled by D-86
CLEATS_KG = 1.2               # kg per pod: the WALL and CEILING frames' internal cleats with their glue, 14.9 g corner cleats
                              # and 6.7 g T plugs (D-117, S49; assumption until the Joints Engineer's cleat models land)
ELEC_KG_RELAYED = 4.94        # kg: ELECTRICAL as relayed before its CAD merged (S43), the estimate in the swap table
ELEC_LIGHTS_KG, CALL_LIGHT_M = 0.26, 0.9  # kg and m: the relayed lights and call light the estimate's strip share used
LOAD_BLOCKS_KG = 0.4          # kg per pod: an aluminium load block inside the band at each glide (D-86, BASE's calculation)
# Parked by D-85, and the rejected glass options
LAM33_T, LAM44_T = 6.76, 8.76  # mm: 3+3 and 4+4 laminate (glass 3 + 0.76 PVB + 3, as the 4+4 is 4 + 0.76 + 4)
FELT_KGM2_LIGHT = 1.4         # kg/m2: a lighter 9 mm PET felt, against Polyx Board 9's 1.8 (S11)
FILL_LIGHTER = 18.0           # kg/m3: Pyrotek's lightest listed grade (hardware selection, fill row: 18, 24, 32, 48, 60)

def base_parts():
    """This study's decided build on skeleton P03 (option B1 with the final stack)."""
    return parts_for("plan", FINAL)


def base_parts_kg(pid):
    """kg each of one part in this study's decided build (P03)."""
    return [pt for pt in base_parts() if pt.pid == pid][0].kg


def ceil_back_delta_kg():
    """A 40 x 40 back member over the 20 x 40 member it replaces, one ceiling half wide (FR-06: C1 and C2; calculation)."""
    return (al_rhs(40, 40, p("t_al_final")) - al_rhs(20, 40, p("t_al_final"))) * P04["ceil_w"] * 1e-3


def top_delta_kg():
    """A 40 x 40 top member over the 20 x 40 member it replaces, one side panel long (FR-06: L2 and R2; calculation)."""
    return (al_rhs(40, 40, p("t_al_final")) - al_rhs(20, 40, p("t_al_final"))) * P04["side_w"] * 1e-3


def stile_delta_kg():
    """A 40 x 40 back stile over the 20 x 40 member it replaces, one side panel high (calculation)."""
    return (al_rhs(40, 40, p("t_al_final")) - al_rhs(20, 40, p("t_al_final"))) * P04["side_h"] * 1e-3


def cassette_faces_m2():
    """Faces of the 8 wall cassettes (P04) and the 2 ceiling cassettes (PR #32's tray outline), m2."""
    walls = 2 * (P04["side_cass_l"] * (P04["side_cass_lo_h"] + P04["side_cass_up_h"])
                 + P04["back_cass_w"] * (P04["back_cass_lo_h"] + P04["back_cass_up_h"])) * 1e-6
    return walls, 2 * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6


def named_clips_kg():
    """Clip-only fixing (adopted): 4 clips on each wall cassette, 6 on each ceiling cassette, 2 catches each (D-47)."""
    return (8 * 4 + 2 * 6) * CLIP_KG + 2 * 2 * CATCH_KG


def shelf_m():
    """The light shelf along the tops of the side and back walls (D-70): the inside width, and each side wall's inside run
    from the back lining to the soffit (air report D60), m."""
    (x0, x1), (y0, y1), _z = AA.D60["soffit"]
    side = P04["wall_depth"] - SKEL_STACK - (y1 - y0)
    return (2 * side + (x1 - x0)) / 1000


ADOPTED = dict(fill=FILL_LIGHT, clip_only=True, band_t=BAND_T_LIGHT, kit_outside=True,     # D-81
               budgets=True, back2=True, studs10=True, kick=True, floor=True)               # D-85
OFF = dict(fill=p("fill_pet_kgm3"), clip_only=False, band_t=p("t_al_base"), kit_outside=False,
           budgets=False, back2=False, studs10=False, kick=False, floor=False)


def back_cad_kg(n, fill, kgm_s, n_back):
    """WALL's back panel B<n> from its CAD (S50): its made parts and bond set, with the fill at `fill` and the inner studs
    at `kgm_s` kg/m, `n_back` of them (so an adopted saving switched off is priced as for the model)."""
    w = WALL_BACK[n]
    return (w["frame"] + w["skin"] + w["fill"] * fill / w["fill_rho"] + w["bond"]
            + w["mid_kg"] * (kgm_s / al_rhs(20, P04["frame_d"], w["mid_t"]) - 1)
            + (n_back - w["mid_n"]) * P04["back_h"] * 1e-3 * kgm_s)


def back_est_kg(fill, kgm12, kgm_s, n_back):
    """This study's model of one back outer panel at the P04 size (S33): frame under the skin, `n_back` inner studs."""
    with override(fill_pet_kgm3=fill):
        back = final_outer_kg(P04["back_w"], P04["back_h"], P04["frame_d"], FINAL)
    return (back - 3 * P04["back_h"] * 1e-3 * kgm12 + n_back * P04["back_h"] * 1e-3 * kgm_s
            - 2 * (P04["back_w"] - P04["back_fw"]) * 1e-3 * kgm12)


def lines(**adopt):
    """[(group, item, qty, kg_each, status, source)] for the pod on skeleton P04: tonight's numbers with the PM's adopted
    savings (D-81, D-85). Group LATER is outside the 420 kg cap (the voice kit, D-11). A keyword switches an adopted
    saving back off (its value in OFF); applied() prices each saving that way."""
    a = dict(ADOPTED, **adopt)
    fill, rails, band_t = a["fill"], not a["clip_only"], a["band_t"]
    kgm12 = al_rhs(20, P04["frame_d"], p("t_al_final"))
    kgm_s = al_rhs(20, P04["frame_d"], T_STUD_LIGHT) if a["studs10"] else kgm12
    stud_d = kgm12 - kgm_s                                   # kg/m less on each inner stud (D-85)
    n_back = BACK_STUDS if a["back2"] else 3
    studs_txt = f"; inner studs at {T_STUD_LIGHT:.1f} mm (D-85)" if a["studs10"] else ""
    lighter = fill != p("fill_pet_kgm3")
    prov = "; fill provisional" if lighter else ""
    base = {pt.pid: pt for pt in base_parts()}
    L = []
    side_a = P04["side_w"] * P04["side_h"] * 1e-6
    fill_d = (p("fill_pet_kgm3") - fill) * P04["frame_d"] * 1e-3      # kg/m2 less with the lighter fill
    with override(fill_pet_kgm3=fill):
        up = final_outer_kg(P04["side_w"], P04["side_up_h"], P04["frame_d"], FINAL)
    def side(n):
        w = WALL_SIDE[n]
        return (w["frame"] + w["skin"] + w["fill"] * fill / w["fill_rho"] + w["bond"]
                + w["mid_kg"] * (kgm_s / al_rhs(20, P04["frame_d"], w["mid_t"]) - 1))
    for item, a_, b_ in (("L1 and R1, lower side outer panels", 1, 2), ("L2 and R2, upper side outer panels", 3, 4)):
        wa, wb = WALL_SIDE[a_], WALL_SIDE[b_]
        L.append(("WALL", item, 2, (side(a_) + side(b_)) / 2, "calculation (CAD)" + prov,
                  f"S34, CAD on main: WALL parts lists 21010{a_} and 21010{b_} P01: frames {wa['frame']:.3f} and "
                  f"{wb['frame']:.3f} (mid stiles at {wa['mid_t']:g} mm), skins {wa['skin']:.3f}, fill {wa['fill']:.3f} at "
                  f"{wa['fill_rho']:g} kg/m3, bond sets {wa['bond']:.2f}; their hardware stays in the fixings kit's line"))
    est_back = back_est_kg(fill, kgm12, kgm_s, n_back)
    b1, b2 = WALL_BACK[1], WALL_BACK[2]
    cad1, cad2 = (back_cad_kg(n, fill, kgm_s, n_back) for n in (1, 2))
    L.append(("WALL", "B1 to B4, back outer panels", 4, (cad1 + cad2 + 2 * est_back) / 4, "calculation (part CAD)" + prov,
              f"part CAD on main: B1 and B2 from WALL parts lists 210201 and 210202 P01 (S50): frames {b1['frame']:.3f} and "
              f"{b2['frame']:.3f} (mid stiles at {b1['mid_t']:g} mm), skins {b1['skin']:.3f} and {b2['skin']:.3f}, fill "
              f"{b1['fill']:.3f} and {b2['fill']:.3f} at {b1['fill_rho']:g} kg/m3, bond sets {b1['bond']:.2f}: {cad1:.2f} and "
              f"{cad2:.2f} kg; their hardware stays in the fixings kit's line. B3 and B4 stay this study's model at the P04 "
              f"size (S33), {est_back:.2f} kg each: frame {P04['back_fw']} under the {P04['back_w']} skin, fill {fill:g} kg/m3"
              + ("; 2 inner studs at 393 mm centres, inside D-16 (D-85)" if a["back2"] else "") + studs_txt))
    L.append(("WALL", "40 x 40 corner edge tubes beyond the panels' own", 1,
              CORNER_TUBES_KG - 4 * stile_delta_kg() - 2 * top_delta_kg() - 2 * ceil_back_delta_kg(), "calculation",
              "D-63's 1.3 kg less the 40 x 40 members the panels' CAD carries: the four side panels' back stiles, L2 and R2's "
              "tops and the ceiling halves' back members (S34, S35, S39)"))
    back_a = P04["back_w"] * P04["back_h"] * 1e-6
    L.append(("WALL", "Bond over this study's 0.25 kg/m2, beyond the panels in CAD", 1,
              BOND_OVER_KG - sum(WALL_SIDE[n]["bond"] - p("bond_kgm2") * side_a for n in (1, 2, 3, 4))
              - sum(WALL_BACK[n]["bond"] - p("bond_kgm2") * back_a for n in (1, 2))
              - 2 * (CEILING["bond"] - p("bond_kgm2") * P04["ceil_w"] * P04["wall_depth"] * 1e-6), "calculation",
              "D-71's 0.5 kg (PR #23) less the share of the panels whose CAD carries their bond: the four side panels, B1 and "
              "B2, and the ceiling halves (S34, S35, S39, S50)"))
    for item, a_, b_, hh in (("side, lower", 1, 2, P04["side_cass_lo_h"]), ("side, upper", 3, 4, P04["side_cass_up_h"])):
        wa, wb = WALL_SIDE[a_], WALL_SIDE[b_]
        cas = sum(w_["tray"] + w_["felt"] + w_["cass_seals"] for w_ in (wa, wb)) / 2
        face = P04["side_cass_l"] * hh * 1e-6
        L.append(("LINING", f"Wall cassette, {item}, with 12 mm lips" + ("" if rails else ", no clip rails"), 2,
                  cas + (p("leaf_clip_kgm2") * face if rails else 0.0), "calculation (CAD)",
                  f"S34, CAD on main: WALL parts lists 51010{a_} and 51010{b_} P01: trays {wa['tray']:.3f} with their lips, "
                  f"felts {wa['felt']:.3f} and {wb['felt']:.3f}, hook-and-loop and seals; their clips are in the named clips' "
                  "line" + (", + this study's 0.6 kg/m2 clip-and-rail allowance" if rails else "")))
    cb = sum(WALL_BACK[n]["tray"] + WALL_BACK[n]["felt"] + WALL_BACK[n]["cass_seals"] for n in (1, 2)) / 2
    face = P04["back_cass_w"] * P04["back_cass_lo_h"] * 1e-6
    L.append(("LINING", "Wall cassette, back, lower, with 12 mm lips" + ("" if rails else ", no clip rails"), 2,
              cb + (p("leaf_clip_kgm2") * face if rails else 0.0), "calculation (CAD)",
              f"S50, CAD on main: WALL parts lists 510201 and 510202 P01: trays {b1['tray']:.3f} and {b2['tray']:.3f} with "
              f"their lips, felts {b1['felt']:.3f} and {b2['felt']:.3f}, hook-and-loop and seals; their clips are in the named "
              "clips' line" + (", + this study's 0.6 kg/m2 clip-and-rail allowance" if rails else "")))
    w, h = P04["back_cass_w"], P04["back_cass_up_h"]
    L.append(("LINING", "Wall cassette, back, upper, with 12 mm lips" + ("" if rails else ", no clip rails"), 2,
              final_leaf_kg(w, h) - (0.0 if rails else p("leaf_clip_kgm2") * w * h * 1e-6) + LIP_KG,
              "calculation; lips confirmed", "this study's model at the P04 size (S33)"
              + ("" if rails else " without its 0.6 kg/m2 clip-and-rail allowance (clip-only, D-81)")
              + ", + 0.43 kg of lips (D-69)"))
    cg = CEILING
    L.append(("CEILING", "Ceiling outer panels C1 and C2, with their bond line", 2, (cg["c1"] + cg["c2"]) / 2,
              "calculation (CAD)", f"S35, CAD on main: CEILING parts list 410000 P01: frames {cg['frames'][0]:.3f} and "
              f"{cg['frames'][1]:.3f} (the 40 x 40 back member, inner members at 1.2 mm, D-85), skins {cg['skins'][0]:.3f} and "
              f"{cg['skins'][1]:.3f}, bond sets {cg['bond']:.3f}; the hardware and seals stay in the fixings kit's line"))
    rails_kg = p("leaf_clip_kgm2") * CEIL_TRAY[0] * CEIL_TRAY[1] * 1e-6 if rails else 0.0
    L.append(("LINING", "Ceiling cassettes, one part for both halves", 2,
              cg["tray"] + cg["ribs"] + cg["felt"] + cg["fill"] * fill / cg["fill_rho"] + rails_kg, "calculation (CAD)" + prov,
              f"S35, CAD on main: CEILING parts list 510301 P01: tray {cg['tray']:.3f}, 2 ribs, felt {cg['felt']:.3f}, fill bays "
              f"{cg['fill']:.3f} at {cg['fill_rho']:g} kg/m3" + (f", scaled to {fill:g}" if fill != cg["fill_rho"] else "")
              + "; its clips and catches are in the named clips' line"
              + (", + this study's 0.6 kg/m2 clip-and-rail allowance" if rails else "")))
    if not rails:
        L.append(("LINING", "Named clips and catches: 44 clips and 4 catch lanyards", 1, named_clips_kg(), "assumption",
                  "allowance: about 40 g a clip and 100 g a lanyard until H03 and H04 name them (clip-only, D-81)"))
    kgm_band = al_rhs(100, 40, band_t)
    thin = band_t != p("t_al_base")
    bc = BASE_CAD
    scale = kgm_band / al_rhs(100, 40, BAND_T_LIGHT)           # BASE's tubes are 1.5 mm; a 2.0 mm wall scales them
    for pid, cad, pn in (("B-BAND-BACK", bc["band_back"], "111103"), ("B-BAND-SIDE", bc["band_side"], "111101")):
        pt = base[pid]
        L.append(("BASE", f"{pt.name.split(' - ', 1)[1].capitalize()}, {band_t:g} mm wall", pt.qty, cad * scale,
                  "calculation (CAD)" + ("; confirmed (1.5 mm)" if thin else ""),
                  f"S44, CAD on main: BASE parts list {pn} P01" + (" (the right side as the left's mirror)" if pn == "111101" else "")
                  + ("" if thin else f", scaled to a {band_t:g} mm wall") + "; its hardware stays in the fixings kit's line"))
    for pid in ("B-BAND-FRONT-L", "B-BAND-FRONT-R"):
        pt = base[pid]
        L.append(("BASE", f"{pt.name.split(' - ', 1)[1].capitalize()}, {band_t:g} mm wall", pt.qty, pt.dims[0] * 1e-3 * kgm_band,
                  "calculation" + ("; confirmed (1.5 mm)" if thin else ""),
                  "this study's model" + (f", {band_t:g} mm wall (D-81; BASE's check passed, D-86)" if thin else "")
                  + "; P03 lengths, P04's faceted front band is about 0.2 m shorter; BASE P02 models it"))
    key = base["B-KEY"]
    keys = [JOINTS[pn] for pn in KEY_PNS]
    n_keys = sum(q for q, _ in keys)
    assert n_keys == key.qty, (n_keys, key.qty)
    L.append(("BASE", "Corner key", key.qty, sum(q * kg for q, kg in keys) / n_keys, "calculation (CAD)",
              "S45, CAD on main: the joints' made hardware list, the corner key family 111211 to 111214, 30 mm thick (3 square, "
              "front LH and RH, knee LH)"))
    glide = base["B-GLIDE"]
    L.append(("BASE", glide.name.split(" - ", 1)[1].capitalize(), glide.qty, bc["glide"], "assumption (CAD, HOLD)",
              "S44, CAD on main: BASE parts list 118002 P01, a levelling glide on HOLD"))
    thr = base["B-THRESH"]
    L.append(("BASE", thr.name.split(" - ", 1)[1].capitalize(), thr.qty, thr.kg, thr.status,
              "this study's model (D-72's 13 mm profile isn't modelled yet)"))
    if thin:
        L.append(("BASE", "Glide load blocks: BASE's glide doublers, one at each glide", 1, glide.qty * bc["doubler"],
                  "calculation (CAD)", f"S44, CAD on main: BASE parts list 111601 P01, {glide.qty} x {bc['doubler']:.4f} kg, a "
                  "52 x 36 x 3 aluminium doubler inside the band at each glide (D-86's load block); one line, as the packing "
                  "plan shares it out by glide"))
    fa = P04["floor_w"] * P04["floor_d"] * 1e-6
    L.append(("BASE", "Floor panels, 9 mm poplar-core plywood with a hard face veneer", 2,
              bc["floor"] + (0.0 if a["floor"] else plate_kg(fa, FLOOR_T, p("rho_ply") - FLOOR_RHO_LIGHT)),
              "confirmed (9 mm, poplar core); calculation (CAD)",
              "S44, CAD on main: BASE parts list 111401 P01 (F2 as F1's mirror), D-85, D-86; the castor and edge tests on the "
              "sample are planned" + ("" if a["floor"] else "; + 600 kg/m3 plywood's extra")))
    L.append(("BASE", "Floor mat, 3 mm firm closed-cell foam", 1, 2 * bc["mat"], "calculation (CAD)",
              "S44, CAD on main: BASE parts list 111501 P01 under F1, and F2's the same (D-76)"))
    for pid, b, extra in (("F-DL", "DL", "; the door's 3 hinges are in the door unit's line, the 2 mm back plate takes "
                                        "J-FRONT-01's rivnuts"),
                          ("F-DR", "DR", "; AIR's riser, transitions and supply fan box are reserved air spaces in it with no "
                                         "mass, counted in AIR's lines (PM ruling 2026-11-01); the fixed glass's right and "
                                         "diagonal channels, fitted in it, are in the fixed glass unit's line"),
                          ("F-DT", "DT", "; with the door's magnetic catch 368007 and the top stop")):
        pt, dc = base[pid], FRONT_DECOR[b]
        L.append(("FRONT", pt.name.split(" - ", 1)[1].capitalize(), pt.qty, dc["unit"], "calculation (CAD)",
                  f"S51, CAD on main: FRONT parts list {dc['pn']} P01: skin {dc['skin']:.3f}, welded frame "
                  f"{dc['frame']:.3f} ({dc['tubes']} tubes), plates, stops and seals {dc['unit'] - dc['skin'] - dc['frame']:.3f}"
                  + extra))
    fd = FRONT_DOOR
    L.append(("FRONT", "Door unit 360001: 4+4 leaf, hollow kick strip, drop seal, hinges, strike, magnetic seal, pull", 1,
              fd["unit"] + (0.0 if a["kick"] else KICK_KG - fd["kick"]), "calculation (CAD); hinges and pull HOLD",
              f"S36, CAD on main: FRONT parts list 360001 P01: leaf {fd['leaf']:.3f}, kick strip {fd['kick']:.3f} (hollow, "
              "D-85), drop seal, U-seal, 3 hinges, the strike and the magnetic seal half (D-83), the pull pair"
              + ("" if a["kick"] else f"; + the solid strip's {KICK_KG - fd['kick']:.2f} kg")))
    L.append(("FRONT", "Fixed glass unit 360002: 4+4 pane, U-profile, U-seal and magnetic seal half", 1, FRONT_FIXED["unit"],
              "calculation (CAD); magnetic seal HOLD", f"S37, CAD on main: FRONT parts list 360002 P01: pane "
              f"{FRONT_FIXED['pane']:.3f}, U-profile, U-seal and one half of the magnetic seal (D-83)"))
    for name, kg, status, source in air_parts(fill):
        filled = lighter and (name.startswith("Air column") or name.startswith("Soffit"))
        loose = name.startswith("Intake riser") or name.startswith("Supply fan box")
        L.append(("AIR", name + ("; ships loose, fitted on site" if loose else ""), 1, kg,
                  status + ("; fill provisional" if filled else ""),
                  source + ("; goes into the right block through its removable inner face (D-59), so the block ships at "
                            "20 kg or less (D-03)" if loose else "")))
    L.append(("AIR", "Four 12 V fans", 1, 4 * AIR["kg"]["618401"], "assumption",
              "S52: AIR parts list 618401 x 4, 0.3 kg each until the sample is weighed"))
    pt = base["K-SEALS"]
    L.append(("BASE", "Base seal and cable grommets", pt.qty, pt.kg - p("door_edge_seal_kg"), pt.status,
              f"this study's model (S20): the seal under the floor and band and the sealed cable holes; its "
              f"{p('door_edge_seal_kg'):.1f} kg of door edge seals is in FRONT's parts lists now (the frame-stop seals in DL "
              "and DT, the magnetic seal pair on the door and the fixed glass), so it isn't counted again (PM ruling "
              "2026-11-01)"))
    el = ELEC
    L.append(("ELECTRICAL", "Switches and harness, power unit, cord set, hub zone and lights (ELECTRICAL)", 1, el["total"],
              "calculation (CAD)", f"S43, CAD on main: ELECTRICAL parts list 710000 P01: the power unit in B2 "
              f"{el['power_unit']:.2f}, the hub and controls zone {el['hub']:.2f}, the cord set {el['cord']:.2f}, the harnesses, "
              f"cables and connectors, and the lights ({el['strip_m']:.2f} m of shelf and down-light strip, the call light). "
              "The light shelf's strip is counted here only; the down-light profile parts listed under INTERIOR's shelf "
              "are in the shelf's line (S53)"))
    it = INTERIOR
    strip = el["strip_kgm"] * shelf_m()                     # the shelf uplight's LED strip, in ELECTRICAL's line (S43)
    if a["budgets"]:
        L.append(("INTERIOR", "Light shelf along the side and back wall tops (its LED strip is in ELECTRICAL's line)", 1,
                  it["shelf"], "calculation (CAD)", "S46, CAD on main: INTERIOR parts list 810201 P01: the back and side "
                  "shelves" + (", " + shelf_note() if shelf_note() else "") + "; the LED strips are in ELECTRICAL's line"))
        L.append(("INTERIOR", "Work-wall ledge, 1000 mm, with the screen rail", 1, it["ledge"] + it["rail"],
                  "calculation (CAD); brackets and screen rail HOLD",
                  f"S46, CAD on main: INTERIOR parts list 810101 P01, the ledge and its 2 brackets ({it['ledge']:.3f}), and "
                  f"818102, the screen rail on HOLD ({it['rail']:.2f}); one line, as the packing plan ships them together"))
    else:
        L.append(("INTERIOR", "Light shelf along the side and back wall tops (its LED strip is in ELECTRICAL's line)", 1,
                  SHELF_KGM_ALLOW * shelf_m() + SHELF_BRACKETS_KG - strip, "assumption",
                  f"the first allowance: {shelf_m():.2f} m at {SHELF_KGM_ALLOW:g} kg/m plus 0.4 kg of brackets (D-70), less its "
                  "LED strip"))
        L.append(("INTERIOR", "Work-wall ledge, 1000 mm, with the screen rail", 1, LEDGE_KG_ALLOW + it["rail"], "assumption",
                  "the first allowance: 1000 x 200 x 12 mm ply at 650 kg/m3 plus 2 brackets (D-70), and the screen rail"))
    (ns, ks), (nw, kw) = JOINTS["831001"], JOINTS["831002"]
    rc = register_counts()
    L.append(("WALL", "M6 bolts, rivnuts, washers, retainers, joint gaskets and seals, spigots and stop washers, frame cleats", 1,
              fixings_kg() + ns * ks + nw * kw + CLEATS_KG, "calculation (part CAD); cleats assumption",
              f"part CAD on main: the joints register's counts (S48: {rc['838001']:.0f} M6 x 16 and {rc['838002']:.0f} M6 x 25 "
              f"bolts, {rc['838003']:.0f} rivnuts, {rc['838004']:.0f} washers, {rc['838005']:.0f} retainers, {rc['848001']:g} m of "
              f"joint gasket, {rc['848004']:g} m of closing-seam seal) at the parts lists' masses ({fixings_kg():.2f} kg, D-116); "
              f"{ns} spigots and {nw} stop washers from the joints' made hardware list ({ns * ks + nw * kw:.2f} kg, S45); and a "
              f"{CLEATS_KG:.1f} kg allowance for the internal frame cleats with their glue, 14.9 g corner cleats and "
              f"6.7 g T plugs (D-117, S49), until their models land"))
    pt = base["E-VOICE-RESERVE"]
    if a["kit_outside"]:
        L.append(("LATER", "Voice cockpit kit reserve, outside the 420 kg cap", 1, pt.kg, pt.status,
                  "the kit ships later as an add-on (D-11); the cap is for the pod as shipped (D-81)"))
    else:
        L.append(("ELECTRICAL", "Voice cockpit kit reserve", 1, pt.kg, pt.status, "this study's model (D-11)"))
    return L


def basis(row):
    """Where a line's mass comes from: CAD merged on main, CAD in a team's open PR, or this study's estimate."""
    _g, _item, _q, _kg, st, src = row
    if src.startswith("part CAD on main"):
        return "CAD, main (part)"
    if "CAD on main" in src:
        return "CAD, main"
    if "(CAD)" in st or "(ELECTRICAL)" in st:
        return "CAD, open PR"
    return "estimate"


def cad_swaps():
    """Each line now read from CAD on main: (line, qty, this study's estimate kg each, CAD kg each, source)."""
    kgm12, kgm10 = al_rhs(20, P04["frame_d"], p("t_al_final")), al_rhs(20, P04["frame_d"], T_STUD_LIGHT)
    with override(fill_pet_kgm3=FILL_LIGHT):
        l1_est = final_outer_kg(P04["side_w"], P04["side_h"], P04["frame_d"], FINAL) - 3 * P04["side_h"] * 1e-3 * (kgm12 - kgm10)
    w, h = P04["side_cass_l"], P04["side_cass_lo_h"]
    cass_est = final_leaf_kg(w, h) - p("leaf_clip_kgm2") * w * h * 1e-6 + LIP_KG
    rows = {r[1].split(" (")[0].split(", with")[0]: r for r in lines() if basis(r) == "CAD, main"}
    door = next(r for r in lines() if r[1].startswith("Door unit 360001"))
    with override(fill_pet_kgm3=FILL_LIGHT):
        l2_est = (final_outer_kg(P04["side_w"], P04["side_up_h"], P04["frame_d"], FINAL)
                  - 3 * P04["side_up_h"] * 1e-3 * (kgm12 - kgm10))
    hu = P04["side_cass_up_h"]
    up_est = final_leaf_kg(w, hu) - p("leaf_clip_kgm2") * w * hu * 1e-6 + LIP_KG
    bw, bh = P04["back_cass_w"], P04["back_cass_lo_h"]
    cb_est = final_leaf_kg(bw, bh) - p("leaf_clip_kgm2") * bw * bh * 1e-6 + LIP_KG
    return [("L1 and R1, lower side outer panels", 2, l1_est, rows["L1 and R1, lower side outer panels"][3],
             "WALL 210101 and 210102 P01, PRs #41 and #104"),
            ("L2 and R2, upper side outer panels", 2, l2_est, rows["L2 and R2, upper side outer panels"][3],
             "WALL 210103 and 210104 P01, PR #104"),
            ("Wall cassette, side, lower", 2, cass_est, rows["Wall cassette, side, lower"][3],
             "WALL 510101 and 510102 P01, PRs #41 and #104"),
            ("Wall cassette, side, upper", 2, up_est, rows["Wall cassette, side, upper"][3], "WALL 510103 and 510104 P01, PR #104"),
            ("B1 and B2, lower back outer panels", 2, back_est_kg(FILL_LIGHT, kgm12, kgm10, BACK_STUDS),
             sum(back_cad_kg(n, FILL_LIGHT, kgm10, BACK_STUDS) for n in (1, 2)) / 2, "WALL 210201 and 210202 P01, PR #152"),
            ("Wall cassette, back, lower", 2, cb_est, rows["Wall cassette, back, lower"][3],
             "WALL 510201 and 510202 P01, PR #152"),
            ("Door unit 360001", 1, DOOR_UNIT_DRAFT - (KICK_KG - KICK_KG_HOLLOW), door[3],
             "FRONT 360001 P01, PR #27 (the estimate: its first list with D-85's 1.0 kg kick strip)"),
            ("Fixed glass unit 360002", 1, FIXED_UNIT_DRAFT, FRONT_FIXED["unit"],
             "FRONT 360002 P01, PR #28 (the estimate: its first list)"),
            ("Decor block DL, left", 1, base_parts_kg("F-DL"), FRONT_DECOR["DL"]["unit"],
             "FRONT 350001 P01, PR #105 (the estimate: this study's model from v1's shapes)"),
            ("Decor block DR, right", 1, base_parts_kg("F-DR"), FRONT_DECOR["DR"]["unit"],
             "FRONT 350003 P01, PR #105 (the estimate: this study's model from v1's shapes)"),
            ("Decor block DT, top", 1, base_parts_kg("F-DT"), FRONT_DECOR["DT"]["unit"],
             "FRONT 350002 P01, PR #105 (the estimate: this study's model from v1's shapes)"),
            ("Door edge seals on 3 sides, in the seal kit", 1, p("door_edge_seal_kg"), 0.0,
             "now in FRONT 350001, 350002, 360001 and 360002 P01 (PR #105; PM ruling 2026-11-01)"),
            ("Ceiling outer panels C1 and C2", 2, CEIL_PANEL + p("bond_kgm2") * P04["ceil_w"] * P04["wall_depth"] * 1e-6,
             (CEILING["c1"] + CEILING["c2"]) / 2, "CEILING 410101 and 410102 P01, PR #32 (the estimate: its first list)"),
            ("Ceiling cassettes", 2, CEIL_CASS - CEIL_FILL_M2 * (p("fill_pet_kgm3") - FILL_LIGHT) * P04["frame_d"] * 1e-3,
             next(r for r in lines() if r[1].startswith("Ceiling cassettes"))[3],
             "CEILING 510301 P01, PR #32 (the estimate: its first list)"),
            ("ELECTRICAL, as shipped", 1, ELEC_KG_RELAYED, ELEC["total"], "ELECTRICAL 710000 P01, PR #64 (the estimate: as relayed)"),
            ("Site fixings: bolts, rivnuts, washers, retainers, gaskets, seals", 1, base_parts_kg("K-FIX"), fixings_kg(),
             "the joints register's counts at the parts lists' masses (D-116); the estimate: this study's 78 bolts, 38 cam "
             "connectors that no longer exist and gasket at 60 g/m"),
            ("Light shelf (its LED strip in ELECTRICAL's line)", 1,
             SHELF_KGM * shelf_m() + SHELF_BRACKETS_KG - ELEC_LIGHTS_KG * shelf_m() / (shelf_m() + CALL_LIGHT_M),
             INTERIOR["shelf"], "INTERIOR 810201 P01, PR #92" + (", " + shelf_note() if shelf_note() else "")
             + " (the estimate: D-85's budget less the strip share)"),
            ("Work-wall ledge", 1, LEDGE_KG, INTERIOR["ledge"], "INTERIOR 810101 P01, PR #92 (the estimate: D-85's budget)"),
            ("Screen rail (not in the estimate)", 1, 0.0, INTERIOR["rail"], "INTERIOR 818102 P01, HOLD, PR #92")] + base_swaps()


def base_swaps():
    """BASE's swaps (PR #55): (line, qty, this study's estimate kg each, CAD kg each, source)."""
    base = {pt.pid: pt for pt in base_parts()}
    kgm = al_rhs(100, 40, BAND_T_LIGHT)
    fa = P04["floor_w"] * P04["floor_d"] * 1e-6
    bc = BASE_CAD
    return [("Base band piece, back", 1, base["B-BAND-BACK"].dims[0] * 1e-3 * kgm, bc["band_back"], "BASE 111103 P01, PR #55"),
            ("Base band piece, side", 2, base["B-BAND-SIDE"].dims[0] * 1e-3 * kgm, bc["band_side"], "BASE 111101 P01, PR #55"),
            ("Corner keys, the 30 mm family", 6, base["B-KEY"].kg, sum(q * kg for q, kg in (JOINTS[pn] for pn in KEY_PNS)) / 6,
             "joints 111211 to 111214 P01, PR #139"),
            ("Glide load blocks (D-86's 0.4 kg), now glide doublers", 8, LOAD_BLOCKS_KG / 8, bc["doubler"],
             "BASE 111601 P01, PRs #55 and #138"),
            ("Spigots and stop washers (not in this study's fixings kit)", 1, 0.0,
             JOINTS["831001"][0] * JOINTS["831001"][1] + JOINTS["831002"][0] * JOINTS["831002"][1],
             "joints 831001 and 831002 P01, PR #139"),
            ("Floor panel", 2, plate_kg(fa, FLOOR_T, FLOOR_RHO_LIGHT) + fa * 0.3, bc["floor"], "BASE 111401 P01, PR #55"),
            ("Floor mat", 1, FOAM_KG, 2 * bc["mat"], "BASE 111501 P01, PR #55")]


def pod_kg(rows=None):
    """The pod as shipped: every line but the voice kit (group LATER)."""
    return sum(q * kg for g, _, q, kg, _, _ in (rows or lines()) if g != "LATER")


def applied():
    """The adopted savings, D-81 then D-85 (S40, S41): (kg, what, status, owner). Each is priced by switching it on in
    lines(), in this order, from the build with none of them, so the table adds up to the part list exactly."""
    walls_m2, ceil_m2 = cassette_faces_m2()
    band_m = sum(pt.dims[0] * pt.qty for pt in base_parts() if pt.pid.startswith("B-BAND")) * 1e-3
    items = [
        ("clip_only", f"Clip-only cassette fixing, no rails: 44 named clips and 4 catch lanyards ({named_clips_kg():.1f} kg "
         f"allowance) replace this study's 0.6 kg/m2 clip-and-rail allowance over {walls_m2 + ceil_m2:.1f} m2 of cassettes",
         "adopted (D-81); the clip gets named with a rated load and a captive lock (H03), T01 and T07 confirm",
         "WALL and CEILING"),
        ("fill", f"Cavity fill at {FILL_LIGHT:g} kg/m3 instead of {p('fill_pet_kgm3'):g}: the wall panels, the ceiling "
         "cassettes, the air column and the soffit. The cartridges' 50 mm layers stay at 32, the density their published "
         "absorption is for", "provisional (D-81): back to 32 kg/m3 if T02 fails (D-54)", "WALL, CEILING, AIR"),
        ("band_t", f"Base band with a {BAND_T_LIGHT:g} mm wall instead of {p('t_al_base'):.1f} mm, {band_m:.1f} m of it; the "
         "same outside size and finish", "adopted (D-81); BASE's check passed, with a load block at each glide (D-86)",
         "BASE"),
        ("kit_outside", "The voice kit's reserve moves outside the cap: the kit ships later as an add-on (D-11)",
         "adopted (D-81); the cap is for the pod as shipped", "PM"),
        ("budgets", f"Weight budgets for the light shelf ({SHELF_KGM:g} kg/m) and the ledge (1.5 mm folded aluminium), now "
         "INTERIOR's CAD; against the first allowances, the ledge in "
         "1.5 mm folded aluminium", "adopted (D-85): the designs keep to them", "INTERIOR, WALL"),
        ("back2", f"Back outer panels with {BACK_STUDS} inner studs, not 3: 393 mm centres, inside D-16's 400 mm (this study "
         "counted from the outer width)", "adopted (D-85)", "WALL"),
        ("studs10", f"Wall panels' inner studs at {T_STUD_LIGHT:.1f} mm wall; the perimeter members keep 1.2 mm for the "
         "rivnuts (D-34), and the ceiling's inner members stay 1.2 mm for the overhead cassette clips and safety catches",
         "adopted (D-85)", "WALL"),
        ("kick", "Door kick strip as a hollow profile with 2 mm walls; the same outside and finish", "adopted (D-85)",
         "FRONT"),
        ("floor", f"Floor panels in poplar-core 9 mm plywood, about {FLOOR_RHO_LIGHT:.0f} kg/m3 against "
         f"{p('rho_ply'):.0f}, with a hard face veneer; the same finish on top", "adopted (D-85, D-86); the castor and "
         "edge tests on the factory sample are planned", "BASE"),
    ]
    state = dict(OFF)
    prev = pod_kg(lines(**state))
    out = []
    for key, what, status, owner in items:
        state[key] = ADOPTED[key]
        now = pod_kg(lines(**state))
        out.append((prev - now, what, status, owner))
        prev = now
    return out


def col_soffit_faces_m2():
    """The air column's two felt-covered faces and the soffit's underside and front face (air report D60), m2."""
    (cx0, cx1), (cy0, cy1), (cz0, cz1) = AA.D60["col"]
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = AA.D60["soffit"]
    return ((cx1 - cx0 + cy1 - cy0) * (cz1 - cz0) + (sy1 - sy0 + sz1 - sz0) * (sx1 - sx0)) * 1e-6


def perimeter_saving_kg():
    """The 20 x 40 perimeter members of the wall and ceiling outer panels at T_STUD_LIGHT instead of 1.2 mm (rejected)."""
    P = P04
    perim_m = 4 * 2 * (P["side_w"] + P["side_h"]) + 4 * 2 * (P["back_w"] + P["back_h"]) + 2 * 2 * (P["ceil_w"] + P["wall_depth"])
    return (al_rhs(20, 40, p("t_al_final")) - al_rhs(20, 40, T_STUD_LIGHT)) * perim_m * 1e-3


def parked():
    """The candidates D-85 parks: (kg, what, what settles it, owner)."""
    felt_m2 = sum(cassette_faces_m2()) + col_soffit_faces_m2()
    return [
        (pod_kg(lines()) - pod_kg(lines(fill=FILL_LIGHTER)), f"Cavity fill at {FILL_LIGHTER:g} kg/m3 instead of "
         f"{FILL_LIGHT:g}", "the wall sample: no published absorption, and it may slump in the upright panels",
         "WALL, CEILING"),
        ((p("pet9_kgm2") - FELT_KGM2_LIGHT) * felt_m2, f"A lighter 9 mm felt, {FELT_KGM2_LIGHT:g} kg/m2 against "
         f"{p('pet9_kgm2'):g}, the same Dark Gray, on {felt_m2:.1f} m2", "the wall sample: the inside absorption uses Polyx "
         "Board 9's 1.8 kg/m2 data, and the face is the look", "Hardware, LINING"),
    ]


REJECTED = (
    ("Fixed glass in 3+3 laminate", f"saves about {FIXED_GLASS * (1 - LAM33_T / LAM44_T):.1f} kg, but a 3+3 pane bends "
     "58 mm at its free edge under a person leaning on it; it stays 4+4 (D-82)"),
    ("The frame perimeters at 1.0 mm", f"saves about {perimeter_saving_kg():.1f} kg, but the 1.2 mm perimeters carry every "
     "rivnut joint (D-85)"),
    ("Door leaf in 3+3 laminate", f"saves about {DOOR_GLASS * (1 - LAM33_T / LAM44_T):.1f} kg; rejected in D-81, D-46 "
     "stands"),
    ("Lighter faces on the air column and soffit", "2 mm ACP gives 26.1 dB(A) at 53 l/s and 30.5 at the boost, against "
     "26 and 30 (air report model)"),
    ("Side outer panels at a 500 mm stud pitch", "saves about 1.7 kg but reopens D-16: the visible ACP may oil-can"),
    ("0.4 mm lining tray", "saves about 12.7 kg but costs 1 dB (D-37)"),
    ("Lighter cartridge casings, 1.2 mm aluminium", "about 27.8 dB(A) at 53 l/s against the 26 target (air report section 7d)"),
    ("Intake riser in 0.8 mm steel", "saves about 1.7 kg but gives 30.03 dB(A) at the 65 l/s boost against 30 (air report model)"),
    ("Lighter ACP on the walls and ceiling", "it is the outer sound leaf; less mass loses dB"),
)


def rollup_csv(rows):
    head = ["group", "item", "qty", "kg_each", "kg_total", "status", "source", "basis"]
    out = [",".join(head)]
    for row in rows:
        g, item, q, kg, st, src = row
        cells = [g, item, str(q), f"{kg:.3f}", f"{q * kg:.2f}", st, src, basis(row)]
        out.append(",".join('"' + c.replace('"', '""') + '"' if ("," in c or '"' in c) else c for c in cells))
    return "\n".join(out) + "\n"


def rollup_md(rows):
    tot = pod_kg(rows)
    later = sum(q * kg for g, _, q, kg, _, _ in rows if g == "LATER")
    by = {}
    for g, _i, q, kg, _s, _src in rows:
        by[g] = by.get(g, 0.0) + q * kg
    ap, op = applied(), parked()
    model_l1 = final_outer_kg(P04["side_w"], P04["side_h"], P04["frame_d"], FINAL)
    shipped = [r for r in rows if r[0] != "LATER" and "glass" not in r[1].lower() and "door unit" not in r[1].lower()]
    ship_kg = lambda r: r[3] + (dr_channels_kg() if r[1].startswith("Decor block - right") else 0.0)  # DR with its channels
    heavy = max(shipped, key=ship_kg)
    loose = sum(r[3] for r in rows if r[0] == "AIR" and (r[1].startswith("Intake riser") or r[1].startswith("Supply fan box")))
    gap = lambda x: f"{abs(x):.1f} kg {'over' if x > 0 else 'under'}"
    md = []
    md.append("<!-- weight-rollup.md is generated by scripts/run_all.py (scripts/rollup.py). Edit the scripts, never this file. -->")
    md.append("# Weight roll-up on skeleton P04")
    md.append("")
    md.append(f"**As shipped, the pod comes to {tot:.1f} kg: {gap(tot - CAP_KG)} the {CAP_KG:.0f} kg cap and {gap(tot - TARGET_KG)} "
              f"the {TARGET_KG:.0f} kg target** (calculation). The voice kit's {later:.1f} kg reserve rides outside the cap, "
              f"{tot + later:.1f} kg with it. This is the live count: it is re-run whenever a part's CAD merges or the skeleton "
              "moves (see the end).")
    md.append("")
    md.append("- **Basis.** This study's decided build on skeleton P03, recounted on P04 with tonight's numbers: the teams' CAD "
              "masses where they exist (the next section lists them; AIR's with the changes its follow-up builds), "
              "the PM's adopted savings (D-81, D-85), budgets and allowances for parts not designed yet, and this "
              "study's model at P04's sizes "
              "for the rest. Every line has its status and source below and in `out/parts-decided-P04.csv`.")
    md.append(f"- **Cross-check.** This study's model gives L1 {model_l1:.2f} kg at the P04 size with 32 kg/m3 fill and 1.2 mm "
              f"studs; WALL's CAD on main gives {sum(WALL_L1[k] for k in ('frame', 'skin', 'fill', 'bond')):.2f} kg with "
              f"24 kg/m3 fill and 1.0 mm mid stiles.")
    nm = heavy[1].split(",")[0]
    nm = nm.split(" - ")[1] + " decor block" if nm.startswith("Decor block - ") else nm.lower()
    dr = FRONT_DECOR["DR"]["unit"]
    dr_ship = dr + dr_channels_kg()
    fan2 = 2 * AIR["kg"]["618401"]
    sof = sum(r[3] for r in rows if r[0] == "AIR" and (r[1].startswith("Soffit") or r[1].startswith("Exhaust fan box")))
    md.append(f"- **20 kg rule (D-03).** The intake riser joined to the supply fan box with its two fans "
              f"({loose + fan2:.1f} kg, D-87) ships loose and goes into the right decor block on site through its removable "
              f"inner face (D-59), so the block ships at {dr_ship:.1f} kg ({dr:.2f} kg from its CAD, S51, and "
              f"{dr_ship - dr:.2f} kg of the fixed glass's right and diagonal channels fitted in it); fitted in the factory it "
              f"would be about {dr_ship + loose + fan2:.0f} kg, over the rule. The soffit ships with its exhaust fan box and fans fitted "
              f"({sof + fan2:.1f} kg, D-87), and B2 with the power unit inside at about 11.9 kg (ELECTRICAL, S43). The "
              f"heaviest piece apart from the glass is the {nm} at {ship_kg(heavy):.1f} kg as shipped, against D-108's 19.0 kg "
              "for the right block; the door unit and the fixed glass unit are glass and exempt.")
    allow = {r[1].split(",")[0].split(" along")[0]: r[2] * r[3] for r in rows
             if "Light shelf" in r[1] or "ledge" in r[1] or "Named clips" in r[1]}
    md.append(f"- **Interior and allowances.** The light shelf ({allow['Light shelf']:.1f} kg) and the work-wall ledge with "
              f"the screen rail ({allow['Work-wall ledge']:.1f} kg) are INTERIOR's CAD (D-70, D-85); the named clips "
              f"({allow['Named clips and catches: 44 clips and 4 catch lanyards']:.1f} kg) stay an allowance (assumption) until "
              f"they're named, and so do the WALL and CEILING frames' internal cleats ({CLEATS_KG:.1f} kg with their glue, D-117), "
              f"carried on the fixings kit's line; the two ceiling lights go (D-70), {2 * p('light_kg'):.1f} kg less.")
    md.append("")
    md.append("| Assembly | kg |")
    md.append("|---|---:|")
    for g in ("WALL", "LINING", "CEILING", "BASE", "FRONT", "AIR", "ELECTRICAL", "INTERIOR"):
        if g in by:
            md.append(f"| {g} | {by[g]:.1f} |")
    md.append(f"| **Pod as shipped** | **{tot:.1f}** |")
    md.append(f"| Cap (D-37, D-54) | {CAP_KG:.0f} ({gap(tot - CAP_KG)}) |")
    md.append(f"| Target (PM) | {TARGET_KG:.0f} ({gap(tot - TARGET_KG)}) |")
    md.append(f"| Voice cockpit kit reserve, later (D-11) | {later:.1f}, outside the cap |")
    md.append("")
    sw = cad_swaps()
    md.append("## CAD masses in place of estimates")
    md.append("")
    md.append("Each line read from a team's merged parts list (CAD on main), against the estimate this study carried for it "
              "(its model at the P04 size with the adopted savings).")
    md.append("")
    md.append("| Line | Qty | Estimate kg each | CAD kg each | Difference kg each | CAD |")
    md.append("|---|---:|---:|---:|---:|---|")
    for line, q, est, cad, src in sw:
        md.append(f"| {line} | {q} | {est:.2f} | {cad:.2f} | {cad - est:+.2f} | {src} |")
    md.append(f"| **In all** | | | | **{sum(q * (cad - est) for _l, q, est, cad, _s in sw):+.2f}** | |")
    md.append("")
    n = {b: sum(1 for r in rows if basis(r) == b) for b in ("CAD, main", "CAD, main (part)", "CAD, open PR", "estimate")}
    md.append(f"Lines by basis: {n['CAD, main']} from CAD on main, {n['CAD, main (part)']} partly, {n['CAD, open PR']} from "
              f"CAD in a team's open PR, {n['estimate']} estimated.")
    md.append("")
    md.append("## Every line")
    md.append("")
    md.append("| Assembly | Item | Qty | kg each | kg | Status | Source | Basis |")
    md.append("|---|---|---:|---:|---:|---|---|---|")
    for row in rows:
        g, item, q, kg, st, src = row
        md.append(f"| {g} | {item} | {q} | {kg:.2f} | {q * kg:.2f} | {st} | {src} | {basis(row)} |")
    md.append("")
    md.append("Sources S33 to S39 are in section 10 of the report (`scripts/inputs.py`).")
    md.append("")
    md.append("## Savings applied (D-81, D-85)")
    md.append("")
    md.append("| Saves kg | What changes | Status | Owner |")
    md.append("|---:|---|---|---|")
    for kg, what, st, owner in ap:
        md.append(f"| {kg:.1f} | {what} | {st} | {owner} |")
    md.append(f"| **{sum(a[0] for a in ap):.1f}** | **in all** | | |")
    md.append("")
    md.append("## Parked (D-85)")
    md.append("")
    md.append(f"{gap(tot - TARGET_KG).capitalize()} the {TARGET_KG:.0f} kg target, which stays (D-85). The wall sample "
              "settles the fill and the felt (FRONT's CAD settled the decor frames, PR #105). Each keeps the look and the "
              "sound targets.")
    md.append("")
    md.append("| Saves kg | What changes | What settles it | Owner |")
    md.append("|---:|---|---|---|")
    for kg, what, risk, owner in op:
        md.append(f"| {kg:.1f} | {what} | {risk} | {owner} |")
    md.append("")
    md.append("Looked at and rejected:")
    md.append("")
    for name, why in REJECTED:
        md.append(f"- {name}: {why}.")
    md.append("")
    md.append("## When this is re-run")
    md.append("")
    md.append("- **Skeleton P04, updated in place (PRs #58 and #94):** this count reads the skeleton's named values for the "
              "panel sizes (side_l, side_h, back_ph, half_pw, half_fw, wall_depth, frame_t, stack_t, floor_t), so a skeleton "
              "change reaches it on the next run. The linings and the floor panels aren't named in the skeleton and come from "
              "its build record. The 13 mm threshold profile and the bolt counts (86 in the joints register) follow BASE's CAD "
              "and the register.")
    md.append("- **Each part PR that merges:** its CAD masses replace this study's model masses line by line (the table of "
              "CAD masses above lists those already in; B3 and B4 and the upper back cassettes and a few allowances are "
              "still estimates; AIR's lines carry the changes its follow-up builds). The fixings kit counts the joints register's hardware at the parts lists' "
              "masses (D-116), so it follows the register.")
    d60 = AA.d60_paths()
    md.append(f"- **BASE's support behind the intake mesh:** if it leaves less than {AA.D60_FREE['intake']:.3f} m2 free, the air "
              f"report re-runs the fan noise ({AA.layout_noise12(d60, 53.0)[2]:.1f} / {AA.layout_noise12(d60, 65.0)[2]:.1f} "
              "dB(A) at 53 / 65 l/s now).")
    md.append("- **D-83:** a 35 N magnetic catch in DT and a magnetic seal pair on the glass edges replace the door lock "
              "(0.84 kg in FRONT's door unit); the door line follows FRONT's CAD.")
    md.append("- **The tests:** T02 (fill), T07 (clips), T10 (weights) and the castor and edge tests on the floor sample "
              "(D-86) replace the provisional and assumed lines.")
    md.append("")
    return "\n".join(md)


def rollup_files():
    rows = lines()
    return {"weight-rollup.md": rollup_md(rows), "out/parts-decided-P04.csv": rollup_csv(rows)}


if __name__ == "__main__":
    rows = lines()
    print(rollup_md(rows))
