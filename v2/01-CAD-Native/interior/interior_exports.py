"""Offline exports for INTERIOR (810000), from the same parameters as the Fusion build.

    python3 v2/01-CAD-Native/interior/interior_exports.py BUILD_LOG

BUILD_LOG is the output of a passing `interior_build.py` run (masses from its MASS lines).
Writes into v2/03-Manufacturing/interior/:

- the parts list for the master BOM, each row with its size and tolerance (a parts-list row is
  the cut list, PM ruling 2026-11-01), maker and SKU for bought items or HOLD;
- flat blanks of the folded parts as 1:1 mm DXF (CUT outline with the cable holes, BEND lines), by
  the K-factor rule with the model's inside radius (sh_r, lg_r: the sheet, the Lead's ruling on
  #335) and K 0.44 (an assumption until the factory's bend table sets it): the three shelf
  profiles and the ledge. A flat runs from the back flange's free edge (y 0) to the lip's.
"""

import csv
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ceiling"))
import interior_model as I  # noqa: E402
import ceiling_exports as CE  # noqa: E402  (build log parser)
import dxf_tools as D  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "v2", "03-Manufacturing", "interior")
REV = I.REV
K = 0.44

TREE = [   # key, parent, qty per parent, source
    ("interior", None, 1, "D-70; assembly tree"),
    ("ledge_assy", "interior", 1, "D-70, D-85"),
    ("ledge", "ledge_assy", 1, "D-70: 1000 mm ledge; D-85: 1.5 mm folded aluminium"),
    ("bracket", "ledge_assy", 2, "on WALL's R1 stiles at Y 98.63 and 464.32, on stand-offs through R1-CASS (WALL interface)"),
    ("shelf_assy", "interior", 1, "D-70, D-85 (0.4 kg/m with the strips)"),
    ("shelf_back", "shelf_assy", 1, "D-70; feed hole at X 355 (ELECTRICAL)"),
    ("shelf_lh", "shelf_assy", 1, "D-70"),
    ("shelf_rh", "shelf_assy", 1, "D-70; call-light drop hole at Y -209.5 (ELECTRICAL)"),
    # D-126: the down-light's bought profile set (718101 to 718104) is listed by ELECTRICAL, in its family;
    # INTERIOR models the profile under 718101 in this assembly but doesn't list it twice
    ("rail", "interior", 1, "D-70: a screen up to about 900 wide; on stand-offs to R2's stiles (WALL interface)"),
]
FINISH = {"ledge": "powder coat, charcoal to match the felt (RAL HOLD)", "shelf_back": "powder coat, charcoal (RAL HOLD)",
          "shelf_lh": "powder coat, charcoal (RAL HOLD)", "shelf_rh": "powder coat, charcoal (RAL HOLD)",
          "lprofile": "black anodised, to match the charcoal shelf (HOLD)", "lcover": "satin, as supplied",
          "lcap": "black, as supplied", "lclip": "as supplied"}
# a part whose material grade isn't chosen yet: HOLD in the status column until it is (C11)
GRADE_HOLD = {}
PROCESS = {"ledge": "laser cut, brake bend (2 bends)", "shelf_back": "laser cut, brake bend (2 bends), cable hole",
           "shelf_lh": "laser cut, brake bend (2 bends)", "shelf_rh": "laser cut, brake bend (2 bends), cable hole",
           "lprofile": "bought; cut to 991", "lcover": "bought; cut to 991", "lcap": "bought", "lclip": "bought"}
SKU = {   # D-126: the type picked from public catalogues only; the product stays HOLD until named
    "bracket": "HOLD: rated for a 225 N lean at the ledge's front edge x 3",
    "rail": "HOLD: VESA rail for a screen up to 900 wide, about 10 kg",
    "lprofile": "HOLD: surface LED aluminium profile of the Tech-Light P13-2 type, 23 x 12.5 outside, 20 inside at the strip base (two 8 mm strips), rated for 12 W/m (ELECTRICAL confirms)",
    "lcover": "HOLD: clip-in satin cover for that profile, at least 86 % of the light (D-127: 350 lx or more on the ledge; ELECTRICAL names the product)",
    "lcap": "HOLD: end caps for that profile, one with a cable entry",
    "lclip": "HOLD: mounting clips for that profile",
}


def fname(key, doctype, ext):
    pn, name, _vn, _k, _m = I.PARTS[key]
    return "%s_%s_%s_%s.%s" % (pn, REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype, ext)


def blank(legs_outer, t, r=None):
    r = t if r is None else r
    ba = math.pi / 2 * (r + K * t)
    so = r + t
    flats = []
    nb = len(legs_outer) - 1
    for i, L in enumerate(legs_outer):
        cut = (so if i > 0 else 0) + (so if i < nb else 0)
        flats.append(L - cut)
    width, bends, x = 0.0, [], 0.0
    for i, f in enumerate(flats):
        x += f
        if i < nb:
            bends.append(x + ba / 2)
            x += ba
    return x, bends


def flat_holes(v, key, name, a0, a1):
    """[(x, y, radius)] of a shelf's cable holes in its flat: x along the part from its low end, y from the back
    flange's free edge (the flat's y 0, its first leg). A hole zc above the shelf's underside is sh_hb - zc from that
    edge, on the flange's straight run (it once sat at width - zc, measured from the lip's end, in the second fold's
    zone: the drawing generator's bent sheet match found it, 2026-11-01)."""
    out = []
    for bname, _k, a in I.features():
        if bname != name:
            continue
        lo = min(I.ev(v, a0), I.ev(v, a1))
        along = (I.ev(v, a[0]) if key == "shelf_back" else I.ev(v, a[1])) - lo
        zc = I.ev(v, a[1] if key == "shelf_back" else a[2]) - v["sh_z0"]     # up the back flange
        out.append((along, v["sh_hb"] - zc, I.ev(v, a[4]) / 2))
    return out


def write_dxfs(v):
    out = {}
    lay = {name: (key, kind, data) for key, name, kind, data in I.layout()}
    feats = {b: a for b, _k, a in I.features()}
    for key, name, t in (("shelf_back", "LIGHT SHELF BACK", v["sh_t"]), ("shelf_lh", "LIGHT SHELF LH", v["sh_t"]),
                         ("shelf_rh", "LIGHT SHELF RH", v["sh_t"]),
                         ("ledge", "LEDGE TOP", v["lg_t"])):
        _k, kind, (sec, a0, a1) = lay[name]
        L = abs(I.ev(v, a1) - I.ev(v, a0))
        # outside leg lengths, from the first free edge: the blank's width by the K-factor rule, at the model's own
        # inside radius
        if key == "ledge":
            outer, r = [v["lg_lip"], v["lg_d"], v["lg_up"]], v["lg_r"]
        else:
            outer, r = [v["sh_hb"], v["sh_d"], v["sh_hl"]], v["sh_r"]
        width, bends = blank(outer, t, r)
        ents = [("POLY", "CUT", [(0, 0), (L, 0), (L, width), (0, width)])]
        for y in bends:
            ents.append(("LINE", "BEND", (0, y), (L, y)))
        for along, y, rad in flat_holes(v, key, name, a0, a1):
            ents.append(("CIRCLE", "CUT", (along, y), rad))
        p = os.path.join(OUT, fname(key, "DXF", "dxf"))
        D.write_dxf(p, ents)
        out[key] = (p, width, L)
    return out


def sizes(v):
    lay = I.boxes(v)

    def dims(name):
        b = lay[name][1]
        return sorted((b[1] - b[0], b[3] - b[2], b[5] - b[4]), reverse=True)
    out = {}
    for key, name, t, tol in (("ledge", "LEDGE TOP", v["lg_t"], "cut +/-0.5, bent +/-0.5 (assumption)"),
                              ("shelf_back", "LIGHT SHELF BACK", v["sh_t"], "cut +/-0.5, bent +/-0.5 (assumption)"),
                              ("shelf_lh", "LIGHT SHELF LH", v["sh_t"], "cut +/-0.5, bent +/-0.5 (assumption)"),
                              ("shelf_rh", "LIGHT SHELF RH", v["sh_t"], "cut +/-0.5, bent +/-0.5 (assumption)"),
                              ):
        d = dims(name)
        out[key] = ("%.1f long, section %.1f x %.1f, %.1f sheet" % (d[0], d[1], d[2], t), tol)
    pl = dims("LED PROFILE RH")[0]
    out["lprofile"] = ("%.0f long; %.0f x %.1f outside, %.0f inside at the strip base" % (pl, v["lp_w"], v["lp_h"], v["lp_in"]),
                       "cut length +/-1 (assumption); section as supplied")
    out["lcover"] = ("%.0f long, for the %.0f-wide profile" % (pl, v["lp_w"]), "cut length +/-1 (assumption); section as supplied")
    return out


def parts_list(v, mass):
    per = {}

    def qty_pod(key):
        if key not in per:
            _k, parent, q, _s = next(t for t in TREE if t[0] == key)
            per[key] = q * (qty_pod(parent) if parent else 1)
        return per[key]
    st = sizes(v)
    rows, by_key = [], {}
    for key, parent, q, src in TREE:
        pn, name, vn, kind, mat = I.PARTS[key]
        m = mass.get(pn)
        if kind == "HS":
            mass_txt, mstat = "", "calculation (sum of its parts)"
        elif kind == "HOLD":
            hm, hs = I.HOLD_MASS[key]
            mass_txt, mstat = "%.3f" % hm, hs
        else:
            each = (sum(m) / max(1, len(m))) if m else None
            mass_txt, mstat = ("%.3f" % each if each is not None else ""), "calculation (Fusion, CAD geometry x density)"
        size, tol = st.get(key, ("", ""))
        r = {"part_number": pn, "name": name, "name_vi": vn, "kind": kind, "parent": I.PARTS[parent][0] if parent else "",
             "qty_per_parent": q, "qty_per_pod": qty_pod(key), "material": I.MATERIALS[mat][0] if mat else "",
             "finish": FINISH.get(key, ""), "process": PROCESS.get(key, ""),
             "maker": "HOLD" if kind == "HOLD" else "", "sku": SKU.get(key, ""),
             "torque": "", "size_mm": size, "tolerance": tol,
             "mass_each_kg": mass_txt, "mass_status": mstat, "revision": REV,
             "status": "HOLD" if kind == "HOLD" or key in GRADE_HOLD else "DRAFT", "source": src}
        if key in GRADE_HOLD:
            r["material"] = "%s (grade HOLD: %s)" % (r["material"], GRADE_HOLD[key])
        rows.append(r)
        by_key[key] = r
    kids = {}
    for key, parent, q, _s in TREE:
        if parent:
            kids.setdefault(parent, []).append((key, q))

    others = other_teams_children(set(r["part_number"] for r in rows))

    def total(key):
        r = by_key[key]
        if r["kind"] != "HS":
            return float(r["mass_each_kg"] or 0.0)
        return sum(q * total(k) for k, q in kids.get(key, [])) + sum(q * m for _pn, q, m in others.get(r["part_number"], []))
    for key, r in by_key.items():
        if r["kind"] == "HS":
            r["mass_each_kg"] = "%.3f" % total(key)
            theirs = others.get(r["part_number"])
            if theirs:
                r["mass_status"] = "calculation (sum of its parts, with %s from other teams' lists)" % ", ".join(
                    sorted(pn for pn, _q, _m in theirs))
    return rows


def other_teams_children(listed):
    """{assembly part number: [(part number, qty per parent, mass each)]} of the rows in the other teams' parts lists
    that name one of INTERIOR's assemblies as their parent: ELECTRICAL's LED profile, cover, end caps and clips sit in
    the light shelf 810201 (the PM's ruling 2026-11-01, Reviewer 16), so its mass counts them."""
    import glob
    out = {}
    for path in sorted(glob.glob(os.path.join(REPO, "v2", "03-Manufacturing", "*", "*PARTS-LIST_BOM.csv"))):
        if os.path.abspath(os.path.dirname(path)) == os.path.abspath(OUT):
            continue
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("parent") in listed and r.get("part_number") not in listed:
                    out.setdefault(r["parent"], []).append(
                        (r["part_number"], float(r.get("qty_per_parent") or 0), float(r.get("mass_each_kg") or 0)))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    v = I.evaluate()
    mass, _flat = CE.parse_log(argv[1])
    os.makedirs(OUT, exist_ok=True)
    for key, (p, w, L) in sorted(write_dxfs(v).items()):
        print("DXF %s blank %.2f x %.1f" % (os.path.basename(p), w, L))
    rows = parts_list(v, mass)
    p = os.path.join(OUT, "810000_%s_INTERIOR-PARTS-LIST_BOM.csv" % REV)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("parts list", p, len(rows), "rows")
    for r in rows:
        if r["kind"] == "HS":
            print("%s %s %s kg" % (r["part_number"], r["name"], r["mass_each_kg"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
