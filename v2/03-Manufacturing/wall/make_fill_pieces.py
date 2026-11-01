"""The distinct WALL cavity-fill pieces for D-120 (each piece its own component and number), from the build
scripts' own formulas: the bays between the frame members and the pockets left beside every bolt the panel
drives (FR-10), plus B2's ELECTRICAL cut-outs (F47) and its bays round the power unit.

    python3 v2/03-Manufacturing/wall/make_fill_pieces.py

Writes FILL-PIECES.md and FILL-PIECES.csv here: every bay of the 8 positions with its size and pockets (u along
the wall from the bay's low corner, v up from the bay's bottom, mm), grouped into distinct forms. Two bays share a
form when one piece fits both, as made or turned over (pockets go through the 40 mm fill, so a turned piece is
the same piece): one number per form (D-123), allocated by the master BOM (number-allocation.csv, #198). The
pieces go straight into their panel assembly (the panel column); D-123 cancels the panels' own fill numbers.

D-128 (PM, 2026-11-01): the pockets go right through the 40 mm batt, so they are edge notches, and a fill piece
with through-openings or edge notches needs no drawing when its DXF gives the full outline with every opening and
its parts-list row gives material, density, thickness, tolerance and part number. So each form also gets its own
DXF here, `<number>_P01_<NAME>_DXF.dxf` (1:1, mm, CUT layer only): the w x h rectangle less every notch and
opening, as seen in the form's first bay (u to the right, v up, origin at the bay's low corner), at the build
scripts' exact sizes (the lists round to 0.1). The CSV says for each bay how its piece goes in: as cut, or turned
over (left to right or top to bottom), or end for end.

A form keeps its label, and so its number, while its shape stays: labels come from the list as last
written (FILL-PIECES.csv), and a new form takes the next free label, so it never shifts the others. (In
(panel, bay) order, R1's sixth stud put two new forms between L1's and L2's, and every later label then
found another form's number at the same size.) A live number's DXF never changes here: if it would, the
run stops before writing anything (`--allow-change` only after a ruling).
"""

import csv
import glob
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "wall"))
import dxf_tools  # noqa: E402
import test_wall_offline as t  # noqa: E402  (loads the build scripts with stand-in adsk modules)


def R(x):
    return round(x, 1)


def clip(rect, bay):
    """The part of an opening inside a bay, in the bay's u, v, exact (not rounded), or None."""
    u0, u1, v0, v1 = rect
    b0, b1, c0, c1 = bay
    a0, a1, w0, w1 = max(u0, b0), min(u1, b1), max(v0, c0), min(v1, c1)
    if a1 - a0 > 0.05 and w1 - w0 > 0.05:
        return (a0 - b0, a1 - b0, w0 - c0, w1 - c0)
    return None


def piece(position, bay, b0, b1, zs, openings, panel, note):
    """One bay's piece: sizes and openings rounded to 0.1 for the lists and for matching forms, and exact
    (the build scripts' own values) for the DXF."""
    raw = sorted(filter(None, (clip(r, (b0, b1, zs[0], zs[1])) for r in openings)))
    return {"position": position, "bay": bay, "w": R(b1 - b0), "h": R(zs[1] - zs[0]),
            "pockets": sorted(tuple(R(x) for x in r) for r in raw), "panel": panel, "note": note,
            "w_raw": b1 - b0, "h_raw": zs[1] - zs[0], "pockets_raw": raw}


def side_pieces():
    out = []
    for code, side, row in (("L1", "L", "1"), ("R1", "R", "1"), ("L2", "L", "2"), ("R2", "R", "2")):
        v = t.resolve(t.load("panel", side, row))
        y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
        z0 = v["panel_z0"] + (0 if row == "1" else v["side_h"] + v["seam_gap"])
        z1 = v["panel_z0"] + v["side_h"] if row == "1" else v["pod_h"]
        n, tw, pw = int(round(v["stile_n_mid"])), v["tube_w"], v["pocket_w"]
        zs = (z0 + tw, z1 - v["top_h"])
        # the studs stand clear of the bolts (stud_c1 to stud_cN from the frame's front end, D-131 sample)
        edges = [y_front + tw] + [y_front + v["stud_c%d" % k] + d * tw / 2 for k in range(1, n + 1) for d in (-1, 1)] + \
            [v["pod_d"] / 2 - v["skin_t"] - v["bond_t"] - v["corner_w"]]     # the back stile, one bond line in
        bays = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
        pockets = [(y_front + v["bolt_edge"] + i * v["len_bolt_pitch"] - pw / 2,
                    y_front + v["bolt_edge"] + i * v["len_bolt_pitch"] + pw / 2, zs[0], zs[0] + pw)
                   for i in range(int(round(v["n_len_bolt"])))]
        pockets += [(y_front + tw, y_front + tw + pw, z0 + v["bolt_edge"] + j * v["side_jnt_pitch"] - pw / 2,
                     z0 + v["bolt_edge"] + j * v["side_jnt_pitch"] + pw / 2) for j in range(3)]
        for k, (b0, b1) in enumerate(bays):
            out.append(piece(code, k + 1, b0, b1, zs, pockets,
                             "2101%02d" % {"L1": 1, "R1": 2, "L2": 3, "R2": 4}[code], ""))
    return out


def back_pieces():
    out = []
    for code in ("B1", "B2", "B3", "B4"):
        ns = t.load_back(code, "panel")
        v = t.resolve(ns)
        col, row = ("L" if code in ("B1", "B3") else "R"), (1 if code in ("B1", "B2") else 2)
        xlo = (-v["close_gap"] / 2 - v["half_fw"]) if col == "L" else v["close_gap"] / 2
        xhi = xlo + v["half_fw"]
        z0 = v["panel_z0"] if row == 1 else v["panel_z0"] + v["back_ph"] + v["seam_gap"]
        z1 = v["panel_z0"] + v["back_ph"] if row == 1 else v["panel_z0"] + v["back_oh"]
        p, n, tw, pw = v["stile_pitch"], int(round(v["stile_n_mid"])), v["tube_w"], v["pocket_w"]
        zs = (z0 + tw, z1 - v["top_h"])
        xs = [(xlo + tw + k * p, xlo + (k + 1) * p) for k in range(n + 1)]
        pockets = []
        for i in range(int(round(v["n_len_bolt"]))):
            xc = xlo + v["bolt_edge"] + i * v["len_bolt_pitch"]
            pockets.append((xc - pw / 2, xc + pw / 2, zs[0], zs[0] + pw))
            if row == 2:
                pockets.append((xc - pw / 2, xc + pw / 2, zs[1] - pw, zs[1]))
        ends = [(xlo if col == "L" else xhi, 1 if col == "L" else -1)] + ([(xlo, 1)] if col == "R" else [])
        for xe, sg in ends:
            xin = xe + sg * tw
            for j in range(3):
                zc = z0 + v["bolt_edge"] + j * v["side_jnt_pitch"]
                pockets.append((min(xin, xin + sg * pw), max(xin, xin + sg * pw), zc - pw / 2, zc + pw / 2))
        # (x range, z range, openings, note) per bay, in the builder's order (back_bays)
        bays = [(x, zs, pockets, "") for x in xs]
        if code == "B2":
            # the builder's own bays and cuts round the power unit (the Lead's approval of WALL's B2 frame and ELECTRICAL's
            # envelopes, 2026-11-01): bays 1 and 2 below and above the cross members, then 3 and 4, then the piece between
            # the mains and LAN channels (B2_ISLAND); B2_CUTS through bay 1's piece below the unit
            def ev(e):
                return t.evaluate(e, v)

            def rects(cuts):
                return [(ev(x0), ev(x1), ev(z0_), ev(z1_)) for _l, (x0, x1), (z0_, z1_) in cuts]
            lo, up = (zs[0], v["xm_z0"]), (v["xm_z1"], zs[1])
            (ix0, ix1), (iz0, iz1) = ns["B2_ISLAND"]
            bays = ([(xs[0], lo, pockets + rects(ns["B2_CUTS"]), "ELECTRICAL's cut-outs: the inlet's box, the jack, "
                                                                 "the mains and LAN channels"),
                     (xs[1], lo, pockets, ""), (xs[0], up, pockets, ""), (xs[1], up, pockets, "")]
                    + [(x, zs, pockets, "") for x in xs[2:]]
                    + [((ev(ix0), ev(ix1)), (ev(iz0), ev(iz1)), rects(ns["B2_ISLAND_NOTCHES"]),
                        "between the mains and LAN channels")])
        for k, ((b0, b1), zr, opens, note) in enumerate(bays):
            out.append(piece(code, k + 1, b0, b1, zr, opens, "2102%02d" % int(code[1]), note))
    return out


def outline(w, h, holes):
    """The cut loops of a w x h piece less the openings (u0, u1, v0, v1): an opening that reaches an edge makes a
    notch, overlapping openings merge. Closed loops of (u, v) corners, each corner once: the outline first
    (anticlockwise), then any opening inside it (clockwise). Exact, on the grid of every edge coordinate: a cell is
    material when its centre is in no opening; the loops follow the cell edges between material and the rest, with
    the material on the left. Raises when two openings only touch at a corner (an ambiguous loop) or the piece falls
    apart into more than one."""
    us = sorted({0.0, float(w)} | {float(x) for r in holes for x in r[:2] if 0 < x < w})
    vs = sorted({0.0, float(h)} | {float(y) for r in holes for y in r[2:] if 0 < y < h})

    def solid(i, j):
        if not (0 <= i < len(us) - 1 and 0 <= j < len(vs) - 1):
            return False
        uc, vc = (us[i] + us[i + 1]) / 2.0, (vs[j] + vs[j + 1]) / 2.0
        return not any(u0 < uc < u1 and v0 < vc < v1 for u0, u1, v0, v1 in holes)

    nxt = {}
    for i in range(len(us) - 1):
        for j in range(len(vs) - 1):
            if not solid(i, j):
                continue
            for a, b, nb in (((i, j), (i + 1, j), (i, j - 1)), ((i + 1, j), (i + 1, j + 1), (i + 1, j)),
                             ((i + 1, j + 1), (i, j + 1), (i, j + 1)), ((i, j + 1), (i, j), (i - 1, j))):
                if not solid(*nb):
                    nxt.setdefault(a, []).append(b)
    if any(len(v) > 1 for v in nxt.values()):
        raise ValueError("two openings touch at a corner only: the outline is ambiguous")
    loops = []
    while nxt:
        start = min(nxt)
        loop, cur = [start], nxt.pop(start)[0]
        while cur != start:
            loop.append(cur)
            cur = nxt.pop(cur)[0]
        pts = [(us[i], vs[j]) for i, j in loop]
        keep = [p for k, p in enumerate(pts)        # drop the points where the loop runs straight on
                if not (pts[k - 1][0] == p[0] == pts[(k + 1) % len(pts)][0] or
                        pts[k - 1][1] == p[1] == pts[(k + 1) % len(pts)][1])]
        loops.append(keep)
    outer = [lp for lp in loops if area(lp) > 0]
    if len(outer) != 1:
        raise ValueError("the piece falls apart into %d pieces" % len(outer))
    return outer + [lp for lp in loops if area(lp) < 0]


def area(loop):
    """Signed area of a closed loop (anticlockwise positive)."""
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(loop, loop[1:] + loop[:1])) / 2.0


def open_area(w, h, holes):
    """The area the openings take out of the piece (their union inside it), by the same grid."""
    us = sorted({0.0, float(w)} | {float(x) for r in holes for x in r[:2] if 0 < x < w})
    vs = sorted({0.0, float(h)} | {float(y) for r in holes for y in r[2:] if 0 < y < h})
    tot = 0.0
    for i in range(len(us) - 1):
        for j in range(len(vs) - 1):
            uc, vc = (us[i] + us[i + 1]) / 2.0, (vs[j] + vs[j + 1]) / 2.0
            if any(u0 < uc < u1 and v0 < vc < v1 for u0, u1, v0, v1 in holes):
                tot += (us[i + 1] - us[i]) * (vs[j + 1] - vs[j])
    return tot


FITS = {(False, False): "as cut", (True, False): "turned over left to right",
        (False, True): "turned over top to bottom", (True, True): "end for end (turned round in its plane)"}


def flipped(pc, fu, fv):
    w, h = pc["w"], pc["h"]
    return tuple(sorted((R(w - u1) if fu else u0, R(w - u0) if fu else u1, R(h - v1) if fv else v0,
                         R(h - v0) if fv else v1) for u0, u1, v0, v1 in pc["pockets"]))


def fit(pc, form_piece):
    """How the form's piece (cut as in its DXF) goes into this bay."""
    want = tuple(sorted(form_piece["pockets"]))
    for (fu, fv), words in FITS.items():
        if flipped(pc, fu, fv) == want:
            return words
    raise ValueError("%s bay %d does not take its form's piece" % (pc["position"], pc["bay"]))


def numbers():
    """{form: [(part number, name), ...]} of the live rows in the master BOM's allocation (D-123; names "... FILL
    PIECE Fnn W X H ..."): an older layout's rows for the same form name may still be live, so the caller picks the
    row at the form's own size."""
    out = {}
    with open(os.path.join(ROOT, "v2", "04-BOM", "number-allocation.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            m = re.search(r"FILL PIECE (F\d\d) ", r["name"])
            if m and r.get("status", "").upper() != "CANCELLED":
                out.setdefault(m.group(1), []).append((r["part_number"], r["name"]))
    return out


def dxf_name(pn, name):
    """conventions section 7: PARTNO_REV_DESCRIPTIVE-NAME_DOCTYPE.ext, the name in capitals joined by hyphens. A size's
    decimal point becomes a hyphen too (1102.7 -> 1102-7): the name field takes letters, digits and hyphens only, and
    the checks find a part's files by that pattern (a DXF named 1102.7 wasn't read as the piece's DXF)."""
    words = re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-")
    return "%s_P01_%s_DXF.dxf" % (pn, words)


def form_key(pc):
    w, h = pc["w"], pc["h"]
    keys = []
    for fu in (False, True):
        for fv in (False, True):
            keys.append((w, h, tuple(sorted((R(w - u1) if fu else u0, R(w - u0) if fu else u1,
                                             R(h - v1) if fv else v0, R(h - v0) if fv else v1)
                                            for u0, u1, v0, v1 in pc["pockets"]))))
    return min(keys)


def previous_forms(path):
    """{form: (form key, number, the pockets in its DXF's frame)} of the list as last written (FILL-PIECES.csv)."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["form"] in out:
                continue
            pk = sorted(tuple(float(x) for x in m)
                        for m in re.findall(r"u ([\d.]+)-([\d.]+), v ([\d.]+)-([\d.]+)", r["pockets"]))
            out[r["form"]] = (form_key({"w": float(r["w_mm"]), "h": float(r["h_mm"]), "pockets": pk}), r["number"],
                              tuple(pk))
    return out


def label_forms(groups, prev, live):
    """[(form, key, members)] in label order: a form found in the last list (same key: size and pockets, as made or
    turned over) keeps its label; a new form takes the next label after every label in the last list and in the
    live allocation (`live`), in (panel, bay) order."""
    by_key = {v[0]: f for f, v in prev.items()}
    nxt = max([int(f[1:]) for f in list(prev) + list(live)] + [0]) + 1
    out = []
    for key, members in sorted(groups.items(), key=lambda kv: (kv[1][0]["panel"], kv[1][0]["bay"])):
        if key in by_key:
            form = by_key[key]
        else:
            form, nxt = "F%02d" % nxt, nxt + 1
        out.append((form, key, members))
    return sorted(out, key=lambda x: int(x[0][1:]))


def main():
    pieces = side_pieces() + back_pieces()
    groups = {}
    for pc in pieces:
        groups.setdefault(form_key(pc), []).append(pc)
    nums = numbers()
    prev = previous_forms(os.path.join(HERE, "FILL-PIECES.csv"))
    forms = label_forms(groups, prev, nums)
    md = ["# WALL cavity-fill pieces (D-120, D-123, D-128)", "",
          "Generated by `make_fill_pieces.py` from the build scripts' formulas (bays between the frame members, "
          "60 x 60 pockets beside every bolt the panel drives, B2's ELECTRICAL cut-outs). Sizes in mm, 40 thick, "
          "u along the wall from the bay's low corner (side walls: from the front; back walls: from the lower X), "
          "v up from the bay's bottom. Bays that one piece fits, as made or turned over, share a form: one number "
          "per form, allocated by the master BOM (D-123).", "",
          "The pockets go right through the 40 mm batt, so they are edge notches: each form is knife cut from its "
          "own DXF (the full outline with every notch and opening, CUT layer, 1:1 mm, seen in its first bay: u to "
          "the right, v up) and needs no drawing (D-128); its parts-list rows give material, density, thickness, "
          "tolerance and part number. The fit column of FILL-PIECES.csv says how each bay takes its piece.", "",
          "%d bays in %d positions, %d distinct forms. B2's bays follow its frame round the power unit (the Lead's "
          "approval of WALL's B2 frame, 2026-11-01) and ELECTRICAL's cut-outs behind its skin." % (
              len(pieces), len({p["position"] for p in pieces}), len(forms)), "",
          "| Form | Number | Size w x h | Notches and openings (u, v ranges) | Bays it fills | DXF |",
          "|---|---|---|---|---|---|"]
    rows, made, unnumbered, writes, changed = [], [], [], [], []
    for form, key, members in forms:
        # the bay its DXF is seen in: the last list's, so a kept form's DXF stays as it was cut
        old = prev.get(form)
        first = next((m for m in members if old and tuple(m["pockets"]) == old[2]), members[0])
        loops = outline(first["w_raw"], first["h_raw"], first["pockets_raw"])
        want = first["w_raw"] * first["h_raw"] - open_area(first["w_raw"], first["h_raw"], first["pockets_raw"])
        if abs(sum(area(lp) for lp in loops) - want) > 0.01:
            raise SystemExit("form %s: the DXF loops enclose %.2f mm2, the piece is %.2f" % (
                form, sum(area(lp) for lp in loops), want))
        # its number: a live allocation row for this form at this size, else "to allocate" (no DXF until then)
        at_size = [r for r in nums.get(form, []) if "%s %g X %g" % (form, first["w"], first["h"]) in r[1]]
        if len(at_size) > 1:
            raise SystemExit("two live numbers for form %s %g x %g: %s" % (form, first["w"], first["h"], at_size))
        pn, name = at_size[0] if at_size else ("", "")
        if not pn:
            dxf = ""
            unnumbered.append("%s %g x %g" % (form, first["w"], first["h"]))
        else:
            dxf = dxf_name(pn, name)
            ents = [("POLY", "CUT", lp) for lp in loops]
            path = os.path.join(HERE, dxf)
            if os.path.exists(path):        # a live number's cut file stays as it is
                with tempfile.TemporaryDirectory() as td:
                    dxf_tools.write_dxf(os.path.join(td, "new.dxf"), ents, layers=("CUT",))
                    with open(os.path.join(td, "new.dxf"), "rb") as a, open(path, "rb") as b:
                        if a.read() != b.read():
                            changed.append("%s (%s %g x %g)" % (pn, form, first["w"], first["h"]))
            writes.append((path, ents))
            made.append((dxf, loops, want))
        pk = "; ".join("u %g-%g, v %g-%g" % r for r in first["pockets"])
        where = ", ".join("%s bay %d" % (m["position"], m["bay"]) for m in members)
        note = " (%s)" % first["note"] if first["note"] else ""
        md.append("| %s | %s | %g x %g | %s%s | %s | %s |" % (form, pn or "to allocate", first["w"], first["h"], pk, note,
                                                          where, ("`%s`" % dxf) if dxf else "when numbered"))
        for m in members:
            rows.append({"form": form, "position": m["position"], "bay": m["bay"], "panel": m["panel"],
                         "w_mm": first["w"], "h_mm": first["h"], "t_mm": 40, "pockets": pk, "note": first["note"],
                         "number": pn, "dxf": dxf, "fit": fit(m, first)})
    if changed and "--allow-change" not in sys.argv:
        raise SystemExit("nothing written: the cut file of live number(s) %s would change; a live number keeps its "
                         "shape (a new shape is a new form, with a new number), so rerun with --allow-change only "
                         "after a ruling" % ", ".join(changed))
    for path, ents in writes:
        dxf_tools.write_dxf(path, ents, layers=("CUT",))
    gone = sorted(set(prev) - {f for f, _k, _m in forms})
    for f in gone:
        print("form %s (%s) is no longer in this layout: Control cancels its number" % (f, prev[f][1] or "no number"))
    with open(os.path.join(HERE, "FILL-PIECES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    with open(os.path.join(HERE, "FILL-PIECES.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    # the DXFs of forms no longer in the list (an older layout's) go, so no stale cut file stays beside the new ones
    keep = {d for d, _l, _w in made}
    for old in sorted(glob.glob(os.path.join(HERE, "211[56][0-9][0-9]_P01_WALL-CAVITY-FILL-PIECE-*_DXF.dxf"))):
        if os.path.basename(old) not in keep:
            os.remove(old)
            print("removed %s (not a form of this layout)" % os.path.basename(old))
    if unnumbered:
        print("TO ALLOCATE (no live number at this size): %s" % "; ".join(unnumbered))
    for dxf, loops, want in made:
        sm = dxf_tools.summary(os.path.join(HERE, dxf))
        e = sm["extents"]
        print("%s: $INSUNITS %s, layers %s, extents %.1f x %.1f, %d loop(s) (%d corners), %.0f mm2" % (
            dxf, sm["insunits"], sorted(sm["layers"]), e[2] - e[0], e[3] - e[1], len(loops),
            sum(len(lp) for lp in loops), want))
    print("wrote FILL-PIECES.md and .csv: %d bays, %d distinct forms, %d DXFs" % (len(pieces), len(forms), len(made)))


if __name__ == "__main__":
    main()
