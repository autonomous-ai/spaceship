"""Offline exports for the ceiling, from the same parameters as the Fusion build.

    python3 v2/01-CAD-Native/ceiling/ceiling_exports.py BUILD_LOG

BUILD_LOG is the output of a passing `ceiling_build.py` run (with export=1).
Writes into v2/03-Manufacturing/ceiling/:

- 513101 tray: Fusion's own flat-pattern DXF (from .raw/), put on the CUT /
  BEND / MARK layers; geometry unchanged.
- 513102 rib blank, 513201 felt, 513301-513303 fill strips, 411301 skin: 1:1 mm DXF cut files drawn from the parameters (these
  parts are flat or bent from a plain strip).
- the parts list for the master BOM and the tube cut list (CSV).

Masses in the parts list are Fusion's (the MASS lines of the build log),
from the materials in ceiling_model.MATERIALS.
"""

import csv
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ceiling_model as M  # noqa: E402
import dxf_tools as D  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "v2", "03-Manufacturing", "ceiling")
REV = M.REV


def fname(key, doctype, ext):
    pn, name, _vn, _k, _m = M.PARTS[key]
    return "%s_%s_%s_%s.%s" % (pn, REV, re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-"), doctype, ext)


def parse_log(path):
    mass, flat = {}, None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("MASS|"):
            _t, occ_path, pn, kg = line.split("|")
            mass.setdefault(pn, []).append(float(kg.split()[0]))
        elif line.startswith("FLAT|"):
            flat = [float(x) for x in re.findall(r"-?\d+\.?\d*", line.split("|")[2])]
    return mass, flat


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def write_flat_parts(v):
    out = {}
    # felt: outline, the sprinkler reserves as MARK circles; origin at its front-left corner
    fw = v["cs_w"] - 2 * (v["tray_t"] + v["felt_c"])
    fd = v["cs_d"] - 2 * (v["tray_t"] + v["felt_c"])
    y_off = v["cs_gap"] + v["tray_t"] + v["felt_c"]
    ents = [("POLY", "CUT", rect(0, 0, fw, fd))]
    for sx, sy in M.sprinkler_points():
        ents.append(("CIRCLE", "MARK", (fw / 2 + M.ev(v, sx), M.ev(v, sy) - y_off), v["sprk_d"] / 2))
    p = os.path.join(OUT, fname("felt", "DXF", "dxf"))
    D.write_dxf(p, ents)
    out["felt"] = p
    # fill strips: outline with notches, origin at the strip's front-left corner
    done = set()
    for key, bay, box, notches in M.fill_strips():
        if key in done:
            continue
        done.add(key)
        b = [M.ev(v, e) for e in box]
        x0, x1, y0, y1 = b[0], b[1], b[2], b[3]
        cuts = []
        for _n, nb in notches:
            n = [M.ev(v, e) for e in nb]
            if M.overlap(tuple(b), tuple(n)):
                cuts.append((max(n[0], x0), min(n[1], x1), max(n[2], y0), min(n[3], y1)))
        pts = notched_outline(x0, x1, y0, y1, cuts)
        ents = [("POLY", "CUT", [(x - x0, y - y0) for x, y in pts])]
        p = os.path.join(OUT, fname(key, "DXF", "dxf"))
        D.write_dxf(p, ents)
        out[key] = p
    # skin: plain rectangle
    p = os.path.join(OUT, fname("skin", "DXF", "dxf"))
    D.write_dxf(p, [("POLY", "CUT", rect(0, 0, v["c_w"], v["wall_depth"]))])
    out["skin"] = p
    # rib blank: developed width across the hat, length along the rib; bend lines on BEND
    rb = rib_blank(v)
    L = v["cs_d"] - 2 * v["tray_t"] - 2 * v["rib_end"]
    ents = [("POLY", "CUT", rect(0, 0, rb["width"], L))]
    for x in rb["bends"]:
        ents.append(("LINE", "BEND", (x, 0), (x, L)))
    p = os.path.join(OUT, fname("rib", "DXF", "dxf"))
    D.write_dxf(p, ents)
    out["rib"] = p
    return out


def notched_outline(x0, x1, y0, y1, cuts):
    """Rectangle with rectangular notches cut from its front (y0) and back (y1) edges."""
    front = sorted([c for c in cuts if abs(c[2] - y0) < 1e-6], key=lambda c: c[0])
    back = sorted([c for c in cuts if abs(c[3] - y1) < 1e-6], key=lambda c: -c[0])
    inner = [c for c in cuts if c not in front and c not in back]
    if inner:
        raise ValueError("notch inside the strip, not on an edge: %s" % inner)
    pts = [(x0, y0)]
    for c in front:
        pts += [(c[0], y0), (c[0], c[3]), (c[1], c[3]), (c[1], y0)]
    pts += [(x1, y0), (x1, y1)]
    for c in back:
        pts += [(c[1], y1), (c[1], c[2]), (c[0], c[2]), (c[0], y1)]
    pts.append((x0, y1))
    return pts


def rib_blank(v, k=0.44):
    """Hat rib 0.5 mm: flange, web, crown, web, flange with four 90 degree bends (r = t)."""
    t, r = v["tray_t"], v["tray_t"]
    ba = math.pi / 2 * (r + k * t)
    c, f, h = v["rib_crown"], v["rib_fl"], v["gap_h"]
    # outside dimensions -> flats between bends
    fl = f - (r + t)
    web = h - 2 * (r + t)
    crown = c - 2 * (r + t)
    segs = [fl, ba, web, ba, crown, ba, web, ba, fl]
    bends, x = [], 0.0
    for i, s in enumerate(segs):
        if i % 2 == 1:
            bends.append(x + s / 2)
        x += s
    return {"width": x, "bends": bends, "bend_allowance": ba}


def write_tray_dxf():
    raw = os.path.join(OUT, ".raw", "513101_%s_LINING-TRAY-CEILING_flat-fusion.dxf" % REV)
    dst = os.path.join(OUT, fname("tray", "DXF", "dxf"))
    seen = D.relayer(raw, dst)
    return dst, seen


def parts_list(v, mass):
    """Rows for the master BOM: the ceiling (both halves) as it ships."""
    q = {  # quantity per parent, parent
        "ceiling": (1, None), "assy_c1": (1, "ceiling"), "assy_c2": (1, "ceiling"),
        "frame_c1": (1, "assy_c1"), "frame_c2": (1, "assy_c2"), "skin": (1, "assy_c1|assy_c2"),
        "cassette": (2, "ceiling"), "tray": (1, "cassette"), "rib": (2, "cassette"), "felt": (1, "cassette"),
        "clip": (6, "cassette"), "catch": (2, "cassette"),
    }
    for key, _bay, _b, _n in M.fill_strips():
        q[key] = (q.get(key, (0, "cassette"))[0] + 1, "cassette")
    per_pod = {"ceiling": 1, "assy_c1": 1, "assy_c2": 1, "frame_c1": 1, "frame_c2": 1, "skin": 2, "cassette": 2}
    for k in [k for k in q if k not in per_pod]:
        per_pod[k] = q[k][0] * 2
    rows = []
    for key, (pn, name, vn, kind, mat) in M.PARTS.items():
        if key not in q:
            continue                     # a fill kind this layout doesn't use
        m = mass.get(pn)
        each = round(m[0], 3) if m else None
        if kind == "HOLD":
            mass_txt, status = "HOLD", "HOLD (no part named; envelope only)"
        elif kind == "HS":
            mass_txt, status = "", "calculation (sum of its parts)"
        else:
            mass_txt, status = ("%.3f" % each) if each is not None else "", "calculation (Fusion, CAD geometry x density)"
        matname = M.MATERIALS[mat][0] if mat else ""
        src = {
            "frame_c1": "D-16, D-34, D-54, D-55; PM ruling 2026-10-31 (3 cross members)",
            "frame_c2": "D-16, D-34, D-54, D-55; PM ruling 2026-10-31 (3 cross members)",
            "skin": "build plan VT01; D-12; D-42",
            "tray": "D-17, D-37; PM ruling 2026-10-31 (12 mm lip)",
            "rib": "PM ruling 2026-10-31 (2 ribs); rib joint HOLD",
            "felt": "D-17, D-31; felt fixing HOLD H09",
            "fill_a": "D-24, D-54; fixing HOLD H10", "fill_b": "D-24, D-54; fixing HOLD H10",
            "fill_c": "D-24, D-54; fixing HOLD H10", "fill_d": "D-24, D-54; fixing HOLD H10",
            "clip": "D-47; H03, ISS-076", "catch": "D-47; H04, ISS-076",
            "cassette": "D-17, D-24, D-41, D-47; PM ruling 2026-10-31 (one part for both halves)",
        }.get(key, "assembly tree; conventions s6")
        rows.append({
            "part_number": pn, "name": name, "name_vi": vn, "kind": kind, "parent": q[key][1] or "",
            "qty_per_parent": q[key][0], "qty_per_pod": per_pod[key], "material": matname,
            "mass_each_kg": mass_txt, "mass_status": status, "revision": REV,
            "status": "DRAFT" if kind != "HOLD" else "HOLD", "source": src,
        })
    # assemblies: sum of parts (HOLD envelopes not counted)
    by_key = {k: r for k, r in zip([k for k in M.PARTS if k in q], rows)}

    def total(key):
        r = by_key[key]
        if r["kind"] != "HS":
            return float(r["mass_each_kg"]) if r["mass_each_kg"] not in ("", "HOLD") else 0.0
        s = 0.0
        for k2, (n, parent) in q.items():
            if parent and key in parent.split("|"):
                s += n * total(k2)
        return s
    for k, r in by_key.items():
        if r["kind"] == "HS":
            r["mass_each_kg"] = "%.3f" % total(k)
    return rows


def cut_list(v):
    rows = []
    for half, key in (("C1", "frame_c1"), ("C2", "frame_c2")):
        pn = M.PARTS[key][0]
        for code, name, axis, b in M.frame_members(half):
            bb = [M.ev(v, e) for e in b]
            L = (bb[1] - bb[0]) if axis == "x" else (bb[3] - bb[2])
            rows.append({"frame": pn, "half": half, "member": code, "name": name,
                         "section": "aluminium 20 x 40 x 1.2 (alloy HOLD, ISS-034)",
                         "length_mm": "%.2f" % L, "qty": 1, "ends": "square cut; frame joint HOLD (H11)",
                         "status": "calculation (from the parameters)"})
    return rows


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    log = argv[1]
    v = M.evaluate(M.all_params())
    mass, flat = parse_log(log)
    os.makedirs(OUT, exist_ok=True)
    written = write_flat_parts(v)
    tray, seen = write_tray_dxf()
    written["tray"] = tray
    print("tray DXF layers:", seen)
    for k, p in sorted(written.items()):
        s = D.summary(p)
        print("DXF", os.path.basename(p), "units", s["insunits"], "layers", sorted(s["layers"]), "extents",
              [round(x, 2) for x in s["extents"]])
    rows = parts_list(v, mass)
    p = os.path.join(OUT, "410000_%s_CEILING-PARTS-LIST_BOM.csv" % REV)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("parts list", p, len(rows), "rows")
    rows = cut_list(v)
    p = os.path.join(OUT, "410000_%s_CEILING-TUBE-CUT-LIST_BOM.csv" % REV)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("cut list", p, len(rows), "rows")
    if flat:
        fb = M.tray_flat(v)
        print("flat body (Fusion) %.2f x %.2f, blank (K-factor calc) %.2f x %.2f" % (
            flat[3] - flat[0], flat[4] - flat[1], fb["blank_d"], fb["blank_w"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
