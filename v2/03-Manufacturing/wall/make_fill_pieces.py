"""The distinct WALL cavity-fill pieces for D-120 (each piece its own component and number), from the build
scripts' own formulas: the bays between the frame members and the pockets left beside every bolt the panel
drives (FR-10), plus B2's ELECTRICAL cut-outs (F47).

    python3 v2/03-Manufacturing/wall/make_fill_pieces.py

Writes FILL-PIECES.md and FILL-PIECES.csv here: every bay of the 8 positions with its size and pockets (u along
the wall from the bay's low corner, v up from the bay's bottom, mm), grouped into distinct forms. Two bays share a
form when one piece fits both, as made or turned over (pockets go through the 40 mm fill, so a turned piece is
the same piece): one number per form (D-123), for the master BOM to allocate.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "01-CAD-Native", "wall"))
import test_wall_offline as t  # noqa: E402  (loads the build scripts with stand-in adsk modules)


def R(x):
    return round(x, 1)


def clip(rect, bay):
    u0, u1, v0, v1 = rect
    b0, b1, c0, c1 = bay
    a0, a1, w0, w1 = max(u0, b0), min(u1, b1), max(v0, c0), min(v1, c1)
    if a1 - a0 > 0.05 and w1 - w0 > 0.05:
        return (R(a0 - b0), R(a1 - b0), R(w0 - c0), R(w1 - c0))
    return None


def side_pieces():
    out = []
    for code, side, row in (("L1", "L", "1"), ("R1", "R", "1"), ("L2", "L", "2"), ("R2", "R", "2")):
        v = t.resolve(t.load("fill", side, row))
        y_front = v["pod_d"] / 2 - v["wall_depth"] + v["seam_gap"]
        z0 = v["panel_z0"] + (0 if row == "1" else v["side_h"] + v["seam_gap"])
        z1 = v["panel_z0"] + v["side_h"] if row == "1" else v["pod_h"]
        p, n, tw, pw = v["stile_pitch"], int(round(v["stile_n_mid"])), v["tube_w"], v["pocket_w"]
        zs = (z0 + tw, z1 - v["top_h"])
        bays = [(y_front + tw + k * p, y_front + (k + 1) * p) for k in range(n)] + \
            [(y_front + n * p + tw, v["pod_d"] / 2 - v["skin_t"] - v["corner_w"])]
        pockets = [(y_front + v["bolt_edge"] + i * v["len_bolt_pitch"] - pw / 2,
                    y_front + v["bolt_edge"] + i * v["len_bolt_pitch"] + pw / 2, zs[0], zs[0] + pw)
                   for i in range(int(round(v["n_len_bolt"])))]
        pockets += [(y_front + tw, y_front + tw + pw, z0 + v["bolt_edge"] + j * v["side_jnt_pitch"] - pw / 2,
                     z0 + v["bolt_edge"] + j * v["side_jnt_pitch"] + pw / 2) for j in range(3)]
        for k, (b0, b1) in enumerate(bays):
            pk = sorted(filter(None, (clip(r, (b0, b1, zs[0], zs[1])) for r in pockets)))
            out.append({"position": code, "bay": k + 1, "w": R(b1 - b0), "h": R(zs[1] - zs[0]), "pockets": pk,
                        "fill": "2115%02d" % {"L1": 1, "R1": 2, "L2": 3, "R2": 4}[code], "note": ""})
    return out


def back_pieces():
    out = []
    for code in ("B1", "B2", "B3", "B4"):
        v = t.resolve(t.load_back(code, "fill"))
        col, row = ("L" if code in ("B1", "B3") else "R"), (1 if code in ("B1", "B2") else 2)
        xlo = (-v["close_gap"] / 2 - v["half_fw"]) if col == "L" else v["close_gap"] / 2
        xhi = xlo + v["half_fw"]
        z0 = v["panel_z0"] if row == 1 else v["panel_z0"] + v["back_ph"] + v["seam_gap"]
        z1 = v["panel_z0"] + v["back_ph"] if row == 1 else v["panel_z0"] + v["back_oh"]
        p, n, tw, pw = v["stile_pitch"], int(round(v["stile_n_mid"])), v["tube_w"], v["pocket_w"]
        zs = (z0 + tw, z1 - v["top_h"])
        bays = [(xlo + tw + k * p, xlo + (k + 1) * p) for k in range(n + 1)]
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
        if code == "B2":                 # ELECTRICAL's cut-outs in the first bay (EL_PARAMS; rationale F47)
            pv = t.resolve(t.load_back("B2", "panel"))
            stud = xlo + p + tw / 2
            pockets += [(pv["el_cut_x0"], stud, pv["el_cut_z0"], pv["el_cut_z1"]),
                        (pv["el_sl_x"] - pv["el_sl_w"] / 2, pv["el_sl_x"] + pv["el_sl_w"] / 2,
                         pv["el_inlet_z"] - pv["el_inlet_d"] / 2, pv["el_cut_z0"]),
                        (pv["el_inlet_x"] - pv["el_inlet_d"] / 2, pv["el_sl_x"] + pv["el_sl_w"] / 2,
                         pv["el_inlet_z"] - pv["el_inlet_d"] / 2, pv["el_lan_z"] + pv["el_inlet_d"] / 2)]
        for k, (b0, b1) in enumerate(bays):
            pk = sorted(filter(None, (clip(r, (b0, b1, zs[0], zs[1])) for r in pockets)))
            out.append({"position": code, "bay": k + 1, "w": R(b1 - b0), "h": R(zs[1] - zs[0]), "pockets": pk,
                        "fill": "2116%02d" % int(code[1]),
                        "note": "ELECTRICAL cut-outs (power unit, sleeve, inlet and LAN)" if code == "B2" and k == 0 else ""})
    return out


def form_key(pc):
    w, h = pc["w"], pc["h"]
    keys = []
    for fu in (False, True):
        for fv in (False, True):
            keys.append((w, h, tuple(sorted((R(w - u1) if fu else u0, R(w - u0) if fu else u1,
                                             R(h - v1) if fv else v0, R(h - v0) if fv else v1)
                                            for u0, u1, v0, v1 in pc["pockets"]))))
    return min(keys)


def main():
    pieces = side_pieces() + back_pieces()
    groups = {}
    for pc in pieces:
        groups.setdefault(form_key(pc), []).append(pc)
    forms = sorted(groups.items(), key=lambda kv: (kv[1][0]["fill"], kv[1][0]["bay"]))
    md = ["# WALL cavity-fill pieces (D-120, D-123)", "",
          "Generated by `make_fill_pieces.py` from the build scripts' formulas (bays between the frame members, "
          "60 x 60 pockets beside every bolt the panel drives, B2's ELECTRICAL cut-outs). Sizes in mm, 40 thick, "
          "u along the wall from the bay's low corner (side walls: from the front; back walls: from the lower X), "
          "v up from the bay's bottom. Bays that one piece fits, as made or turned over, share a form: one number "
          "per form, for the master BOM to allocate.", "",
          "%d bays in the 8 positions, %d distinct forms." % (len(pieces), len(forms)), "",
          "| Form | Size w x h | Pockets (u, v ranges) | Bays it fills | Number |", "|---|---|---|---|---|"]
    rows = []
    for i, (key, members) in enumerate(forms, 1):
        first = members[0]
        pk = "; ".join("u %g-%g, v %g-%g" % r for r in first["pockets"])
        where = ", ".join("%s bay %d" % (m["position"], m["bay"]) for m in members)
        note = " (%s)" % first["note"] if first["note"] else ""
        md.append("| F%02d | %g x %g | %s%s | %s | to allocate |" % (i, first["w"], first["h"], pk, note, where))
        for m in members:
            rows.append({"form": "F%02d" % i, "position": m["position"], "bay": m["bay"], "fill": m["fill"],
                         "w_mm": first["w"], "h_mm": first["h"], "t_mm": 40, "pockets": pk, "note": first["note"]})
    with open(os.path.join(HERE, "FILL-PIECES.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    with open(os.path.join(HERE, "FILL-PIECES.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote FILL-PIECES.md and .csv: %d bays, %d distinct forms" % (len(pieces), len(forms)))


if __name__ == "__main__":
    main()
