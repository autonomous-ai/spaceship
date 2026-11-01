"""Offline exports for the ceiling, from the same parameters as the Fusion build.

    python3 v2/01-CAD-Native/ceiling/ceiling_exports.py BUILD_LOG

BUILD_LOG is the output of a passing `ceiling_build.py` run (with export=1).
Writes into v2/03-Manufacturing/ceiling/:

- 513101 tray: Fusion's own flat-pattern DXF (from .raw/), put on the CUT /
  BEND / MARK layers; geometry unchanged.
- 513102 rib blank, 513201 felt, 513301-513303 fill strips, 411301 and 411302 skins (C2 with the
  roof slot): 1:1 mm DXF cut files drawn from the parameters (these parts are flat or bent from
  a plain strip). Skins are drawn seen from above, X right, Y toward the back, origin at the
  skin's front edge on its closing-seam end (C1 mirrored so its seam end is at x = 0 too).
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


# material, finish, maker, SKU and torque of the joint hardware, worded as the joints register
# 2.1 and WALL's parts lists give them (one wording per register number)
TQ_RIVNUT = "HOLD-01 (D-48): set by the PM from test T06 (half the lowest rivnut spin-out torque)"
HW_SPEC = {
    "838001": ("steel, property class 8.8 (ISO 898-1)", "zinc plated", "HOLD: any maker to ISO 4762, picked at the RFQ",
               "ISO 4762 M6 x 16 - 8.8 - zinc plated", TQ_RIVNUT),
    "838002": ("steel, property class 8.8 (ISO 898-1)", "zinc plated", "HOLD: any maker to ISO 4762, picked at the RFQ",
               "ISO 4762 M6 x 25 - 8.8 - zinc plated", "snug only: a pin, not a clamp (joints register 2.10)"),
    "838003": ("steel 1008/1010", "zinc plated, trivalent passivation", "Sherex (PEM)", "CAL2-610-4.2", TQ_RIVNUT),
    "838004": ("stainless steel A2", "none (plain stainless)", "HOLD: any maker to ISO 7093-1, picked at the RFQ",
               "ISO 7093-1 - 6.4 x 18 x 1.6 - A2", ""),
    "838005": ("elastomer (HOLD-02)", "as supplied (elastomer)", "HOLD-02", "HOLD-02", ""),
    "831002": ("aluminium sheet 1.5, 5000 or 6000 series", "mill finish (punched)", "made (register H-08)", "", ""),
    "831007": ("galvanized steel 2.0, S280GD+Z or SGC400, Z100 (the frames' own steel)", "welded in; zinc-rich touch-up "
               "with the frame's welds", "made (register H-40, J-FRAME-01)", "", ""),
    "831008": ("galvanized steel 2.0, S280GD+Z or SGC400, Z100 (the frames' own steel)", "welded in; zinc-rich touch-up "
               "with the frame's welds", "made (register H-41, J-FRAME-01)", "", ""),
    "848001": ("PORON 4701-40 Soft polyurethane foam with PSA", "none (foam, PSA liner one side)",
               "Rogers (PORON), PSA laminated and slit by a converter (HOLD-05)", "PORON 4701-40 Soft, 3.97 x 8 strip with PSA", ""),
    "848004": ("EPDM or TPE hollow bulb (HOLD-12)", "as supplied", "HOLD-12", "HOLD-12: hollow bulb, working gap 4 to 7", ""),
}


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
    # skins: C1 a plain rectangle, C2 with the roof slot (D-61), from the C2 seam end
    p = os.path.join(OUT, fname("skin_c1", "DXF", "dxf"))
    D.write_dxf(p, [("POLY", "CUT", rect(0, 0, v["half_pw"], v["wall_depth"]))])
    out["skin_c1"] = p
    seam = v["seam_gap"] / 2
    yw = M.ev(v, M.YW)
    sx0, sy0 = v["slot_x0"] - seam, v["slot_y0"] - yw
    p = os.path.join(OUT, fname("skin_c2", "DXF", "dxf"))
    holes = [("CIRCLE", "CUT", (M.ev(v, x) - M.ev(v, "slot_x0") + sx0, M.ev(v, y) - yw), v["hole_rvn"] / 2)
             for _n, x, y in M.sleeve_rivnuts()]          # under the roof sleeve flange's 4 rivnuts (J-AIR-03)
    D.write_dxf(p, [("POLY", "CUT", rect(0, 0, v["half_pw"], v["wall_depth"])),
                    ("POLY", "CUT", rect(sx0, sy0, sx0 + v["slot_w"], sy0 + v["slot_d"]))] + holes)
    out["skin_c2"] = p
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
    """Hat rib 0.5 mm: flange, web, crown, web, flange with four 90 degree bends (r = t). The hat's bends alternate:
    a flange's bend has its outside on the flange's top face, which runs on over the web's thickness to the web's
    inside face, so the flange's outside length is f + t; the webs' and the crown's outsides are the webs' outer
    faces and the crown's underside (h and c). Each straight is its outside length less r + t at each bent end. (The
    flange was once taken as f, so the blank came out 1 mm short, 88.52 for 89.52, folding to 43 wide for 44: the
    D-114 pass on #306 found it.)"""
    t, r = v["tray_t"], v["tray_t"]
    ba = math.pi / 2 * (r + k * t)
    c, f, h = v["rib_crown"], v["rib_fl"], v["gap_h"]
    # outside lengths -> straights between bends
    fl = (f + t) - (r + t)
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


MEMBER_ENDS = {   # D-117, the Joints Engineer's corner design
    "SIDE": "front end mitred 45 deg, back end mitred 63.43 deg off square", "SEAM": "front end mitred 45 deg, back end mitred 63.43 deg off square",
    "FRONT": "both ends mitred 45 deg", "BACK": "both ends mitred 26.57 deg off square",  # each cut back for its 2.0 plate (J-FRAME-01)
    "X1": "square cut", "X2": "square cut", "X3": "square cut",
}


def member_rows(v, half):
    """[(code, part key, name, section, outer length, ends, features)] of one frame's members."""
    holes = {}
    for name, member, _f, _xyz, _d, n, _p, _a in M.joint_holes(half):
        holes.setdefault(member, []).append("%s x %d" % (name.lower(), int(round(M.ev(v, n)))))
    boxes = {c: [M.ev(v, e) for e in b] for c, _n, _a, b in M.frame_members(half)}
    out = []
    for code, key, name, axis, _pts, _z0, _z1 in M.member_shapes(half):
        bb = boxes[code]
        L = (bb[1] - bb[0]) if axis == "x" else (bb[3] - bb[2])
        sec = "%s x 40 x %.1f" % ("40" if code == "BACK" else "20", M.ev(v, M.member_wall(key)))
        extra = list(holes.get(code, []))
        if code == "BACK":
            extra.append("back spigot slot 8.5 x 14 x 1")
        if code == "SEAM":
            extra.append("1 x 45 lead-in on the closing face's lower edge, full length")
        out.append((code, key, name, sec, L, MEMBER_ENDS[code], extra))
    return out


def _sizes():
    """(size, tolerance) per made part and assembly: a parts-list row is the cut list for soft
    goods and plain parts (PM ruling 2026-11-01 on the Checker's pre-check)."""
    def fills(key):
        def f(v):
            for k, _bay, box, _n in M.fill_strips(v):
                if k == key:
                    b = [M.ev(v, e) for e in box]
                    return ("%.1f x %.1f x %.0f" % (b[1] - b[0], b[3] - b[2], v["fill_t"]),
                            "cut +/-2 (assumption); no drawing (D-128): %s gives the full outline with every notch"
                            % fname(key, "DXF", "dxf"))
            return "", ""
        return f
    return {
        "ceiling": lambda v: ("%.2f x %.2f x %.0f (X x Y x Z)" % (2 * v["half_pw"] + v["seam_gap"], v["wall_depth"], v["stack_t"]), ""),
        "assy_c1": lambda v: ("%.2f x %.2f x %.0f" % (v["half_pw"], v["wall_depth"], v["outer_t"]), ""),
        "assy_c2": lambda v: ("%.2f x %.2f x %.0f" % (v["half_pw"], v["wall_depth"], v["outer_t"]), ""),
        "frame_c1": lambda v: ("%.2f x %.2f x %.0f" % (v["half_fw"], v["wall_depth"], v["frame_t"]),
                               "welded in a jig (J-FRAME-01): diagonals equal within 1.5 and the skin-side faces within +/-0.5 of one plane, measured after welding (J-FRAME-01); outer size +/-0.5 (assumption); spigot to closing face +/-0.1 (ST-04)"),
        "frame_c2": lambda v: ("%.2f x %.2f x %.0f" % (v["half_fw"], v["wall_depth"], v["frame_t"]),
                               "welded in a jig (J-FRAME-01): diagonals equal within 1.5 and the skin-side faces within +/-0.5 of one plane, measured after welding (J-FRAME-01); outer size +/-0.5 (assumption); spigot to closing face +/-0.1 (ST-04)"),
        **{key: (lambda code, h: (lambda v: next(("%s tube, %.2f long at the outer face, %s" % (sec, L, ends),
                                                  "cut length +/-0.5, mitre angles +/-0.25 deg (assumption); holes and slots +/-0.2 "
                                                  "from the round spigot hole (R-J6)")
                                                 for c, _k, _n, sec, L, ends, _x in member_rows(v, h) if c == code)))(code, h)
           for h, code, key in [("C1", "SIDE", "m_side"), ("C1", "X1", "m_x1")]
           + [(h, code, "m_%s_%s" % (code.lower(), h.lower())) for h in ("C1", "C2") for code in ("SEAM", "FRONT", "BACK")]},
        "m_cross": lambda v: ("20 x 40 x %.1f tube, %.2f long, square cut, no holes"
                              % (M.ev(v, M.member_wall("m_cross")), v["half_fw"] - 2 * v["tube_w"]),
                              "cut length +/-0.5 (assumption)"),
        "skin_c1": lambda v: ("%.2f x %.2f x %.0f" % (v["half_pw"], v["wall_depth"], v["skin_t"]),
                              "ISO 2768-m; no drawing (D-89 part 4): its DXF is the outline"),
        "skin_c2": lambda v: ("%.2f x %.2f x %.0f, roof slot %.0f x %.0f" % (v["half_pw"], v["wall_depth"], v["skin_t"], v["slot_w"], v["slot_d"]),
                              "ISO 2768-m; roof slot from the closing-seam edge and the front edge +/-0.5 (critical: the roof sleeve passes through it, D-61); no drawing (D-89 part 4)"),
        "cassette": lambda v: ("%.0f x %.0f x %.0f (%.0f with the fill)" % (v["cs_w"], v["cs_d"], v["tray_h"], v["tray_h"] + v["fill_t"]),
                               "+/-1 assembled (assumption)"),
        "tray": lambda v: ("%.0f x %.0f x %.0f, 0.5 sheet" % (v["cs_w"], v["cs_d"], v["tray_h"]), "cut +/-0.2, bent +/-0.5 (assumption)"),
        "rib": lambda v: ("hat %.0f x %.0f x %.1f long, 0.5 sheet" % (v["rib_crown"] + 2 * v["rib_fl"], v["gap_h"],
                                                                     v["cs_d"] - 2 * v["tray_t"] - 2 * v["rib_end"]), "length +/-1, bends +/-0.5 (assumption)"),
        "felt": lambda v: ("%.1f x %.1f x %.0f" % (v["cs_w"] - 2 * (v["tray_t"] + v["felt_c"]), v["cs_d"] - 2 * (v["tray_t"] + v["felt_c"]), v["felt_t"]),
                           "knife cut +/-1 (assumption); two sprinkler zones marked, nothing cut"),
        "fill_a": fills("fill_a"), "fill_b": fills("fill_b"), "fill_c": fills("fill_c"), "fill_d": fills("fill_d"),
    }


SIZE_TOL = _sizes()


def parts_list(v, mass):
    """Rows for the master BOM: the ceiling (both halves) as it ships."""
    q = {  # quantity per parent, parent
        "ceiling": (1, None), "assy_c1": (1, "ceiling"), "assy_c2": (1, "ceiling"),
        "frame_c1": (1, "assy_c1"), "frame_c2": (1, "assy_c2"), "skin_c1": (1, "assy_c1"), "skin_c2": (1, "assy_c2"),
        **{"m_%s_%s" % (m, h): (1, "frame_" + h) for h in ("c1", "c2") for m in ("seam", "front", "back")},
        "m_side": (1, "frame_c1|frame_c2"), "m_x1": (1, "frame_c1|frame_c2"),     # one part each for both frames
        "m_cross": (2, "frame_c1|frame_c2"),
        "cassette": (2, "ceiling"), "tray": (1, "cassette"), "rib": (2, "cassette"), "felt": (1, "cassette"),
        "clip": (6, "cassette"), "catch": (2, "cassette"),
    }
    for key, _bay, _b, _n in M.fill_strips():
        q[key] = (q.get(key, (0, "cassette"))[0] + 1, "cassette")
    per_pod = {"ceiling": 1, "assy_c1": 1, "assy_c2": 1, "frame_c1": 1, "frame_c2": 1, "skin_c1": 1, "skin_c2": 1,
               "cassette": 2, "m_cross": 4, "m_side": 2, "m_x1": 2,
               **{"m_%s_%s" % (m, h): 1 for h in ("c1", "c2") for m in ("seam", "front", "back")}}
    for k in [k for k in q if k not in per_pod]:
        per_pod[k] = q[k][0] * 2
    rows = []
    for key, (pn, name, vn, kind, mat) in M.PARTS.items():
        if key not in q:
            continue                     # a fill kind this layout doesn't use
        m = mass.get(pn)
        each = round(m[0], 3) if m else None
        if kind == "HOLD":
            hm, hst, hsrc = M.HOLD_MASS[key]
            mass_txt, status = "%.3f" % hm, hst
        elif kind == "HS":
            mass_txt, status = "", "calculation (sum of its parts)"
        else:
            mass_txt, status = ("%.3f" % each) if each is not None else "", "calculation (Fusion, CAD geometry x density)"
        matname = M.MATERIALS[mat][0] if mat else ""
        if key in ("frame_c1", "frame_c2"):
            # the welded frame's own row names its steel (D-131, J-FRAME-01); its members' rows carry the gauges
            matname = "%s: the members below, welded" % M.MATERIALS["steel_fr"][0]
        size, tol = SIZE_TOL.get(key, (lambda vv: ("", "")))(v)
        src = {
            "frame_c1": "D-16, D-34, D-55; D-131 and J-FRAME-01 (welded galvanized steel, the mitre plates, the gauges); D-117 (mitred corners), D-120 (member parts); PM rulings 2026-10-31 (3 cross members; frame 1198.99; bolt lines per the joints register); R-J3 40 x 40 back member; J-CEIL-01, J-CEIL-02",
            "frame_c2": "D-16, D-34, D-55; D-131 and J-FRAME-01 (welded galvanized steel, the mitre plates, the gauges); D-117 (mitred corners), D-120 (member parts); PM rulings 2026-10-31 (3 cross members; frame 1198.99; bolt lines per the joints register); R-J3 40 x 40 back member; J-CEIL-01, J-CEIL-02",
            **{k: "D-120 (number from the master BOM's allocation); D-117 (mitred corners); D-131 and J-FRAME-01 (galvanized steel 20 x 40 and 40 x 40 R-J3, 1.0 or 0.8 wall, cut back for the 2.0 mitre plates); joints register J-CEIL-01, J-CEIL-02"
               for k in M.PARTS if k.startswith("m_")},
            "skin_c1": "build plan VT01; D-12; D-42; skeleton half_pw 1200.61",
            "skin_c2": "build plan VT01; D-12; D-42; skeleton half_pw 1200.61; D-61 roof slot 285 x 294 (PM ruling 2026-10-31: two skins)",
            "tray": "D-17, D-37; PM ruling 2026-10-31 (12 mm lip)",
            "rib": "PM ruling 2026-10-31 (2 ribs); rib joint HOLD",
            "felt": "D-17, D-31; felt fixing HOLD H09",
            "fill_a": "D-24, D-54; fixing HOLD H10", "fill_b": "D-24, D-54; fixing HOLD H10",
            "fill_c": "D-24, D-54; fixing HOLD H10", "fill_d": "D-24, D-54; fixing HOLD H10",
            "clip": "D-47, D-81; joints register H-10; HOLD-08, ISS-076", "catch": "D-47; joints register H-11; HOLD-08, ISS-076",
            "cassette": "D-17, D-24, D-41, D-47; PM ruling 2026-10-31 (one part for both halves)",
        }.get(key, "assembly tree; conventions s6")
        if kind == "HOLD":
            src = "%s; mass: %s" % (src, M.HOLD_MASS[key][2])
        rows.append({
            "part_number": pn, "name": name, "name_vi": vn, "kind": kind, "parent": q[key][1] or "",
            "qty_per_parent": q[key][0], "qty_per_pod": per_pod[key], "material": matname,
            "finish": M.FINISH.get(key, ""), "process": M.PROCESS.get(key, ""),
            "maker": "HOLD-08" if kind == "HOLD" else "", "sku": ({"clip": "HOLD-08: rated 4.9 kg pull-out each (ceiling, J-LIN-01), captive lock; latches when pushed home, so a ceiling cassette holds itself before its two catches go on (Packing's assembly review, PM ruling 2026-11-01)",
                                                                  "catch": "HOLD-08: 48 kg working load per lanyard (T08)"}.get(key, "")),
            "torque": "", "size_mm": size, "tolerance": tol,
            "mass_each_kg": mass_txt, "mass_status": status, "revision": REV,
            "status": "DRAFT" if kind != "HOLD" else "HOLD", "source": src,
        })
    # the ACP bond set, shared with WALL (joints register H-12, number 108002): one bonded skin per ceiling outer
    # panel, mass from the bond spec's 0.28 kg/m2 (section 8 keeps the 12 x 3 joint for D-131's steel frames)
    bond_each = v["half_pw"] * v["wall_depth"] * 1e-6 * 0.28
    rows.append({
        "part_number": "108002",
        "name": "POD - ACP BOND SET - SIKAFLEX-252 WITH AKTIVATOR-205, PRIMER-210, FIXING TAPE",
        "name_vi": "Bộ keo dán ACP", "kind": "PI", "parent": "assy_c1|assy_c2", "qty_per_parent": 1,
        "qty_per_pod": 2, "material": "Sikaflex-252 system (bond spec section 8, D-131)", "finish": "", "process": "",
        "maker": "Sika", "sku": "Sikaflex-252 system (bond spec V2-ENG-BND section 8): Sikaflex-252, Sika Aktivator-205 and Sika Primer-210 on both faces, SikaTack Panel Fixing Tape 3 x 12",
        "torque": "", "size_mm": "", "tolerance": "",
        "mass_each_kg": "%.3f" % bond_each,
        "mass_status": "calculation", "revision": REV, "status": "DRAFT",
        "source": "joints register H-12 (108002); bond spec section 8 (D-131): 0.28 kg/m2 x %.3f m2 per ceiling outer panel" % (
            v["half_pw"] * v["wall_depth"] * 1e-6),
    })
    q["bond"] = (1, "assy_c1|assy_c2")
    keys = [k for k in M.PARTS if k in q] + ["bond"]
    by_key = {k: r for k, r in zip(keys, rows)}
    # joint hardware fitted in the factory (joints register 2.1 numbers, D-63): one row per
    # half, since C1 and C2 carry different sets
    plates = {"plate45": "H-40", "plate_sb": "H-41"}     # welded into the frames' corners (D-131, J-FRAME-01)
    for hk, (pn, name, vn, kind, unit, n1, n2, kg, mstat) in M.HARDWARE.items():
        for half, expr in (("assy_c1", n1), ("assy_c2", n2)):
            n = M.ev(v, expr)
            if n <= 0:
                continue
            qty = round(n, 3) if unit == "m" else int(round(n))
            key = "%s_%s" % (hk, half)
            parent = ("frame_c1" if half == "assy_c1" else "frame_c2") if hk in plates else half
            q[key] = (qty, parent)
            mat, fin, maker, sku, tq = HW_SPEC[pn]
            if hk in plates:
                process = "laser cut from the frames' 2.0 galvanized steel, welded into the frame's corner (J-FRAME-01)"
                source = "joints register %s (%s), J-FRAME-01 (D-131); the joints CAD README's placement; per piece; " \
                         "mass %s" % (plates[hk], pn, mstat)
            else:
                process = "punched (a part we make)" if kind == "MP" else ""
                source = "joints register V2-ENG-JNT-01 2.1 (%s), 3.5 J-CEIL-01 / 3.6 J-CEIL-02; per %s; mass %s" % (
                    pn, "metre" if unit == "m" else "piece", mstat)
            r = {"part_number": pn, "name": name, "name_vi": vn, "kind": kind, "parent": parent,
                 "qty_per_parent": qty, "qty_per_pod": qty, "material": mat, "finish": fin,
                 "process": process,
                 "maker": maker, "sku": sku, "torque": tq, "size_mm": "", "tolerance": "",
                 "mass_each_kg": "%.4f" % kg, "mass_status": mstat.split(":")[0],
                 "revision": REV, "status": "HOLD" if kind == "HOLD" else "DRAFT",
                 "source": source}
            rows.append(r)
            by_key[key] = r

    def total(key):
        r = by_key[key]
        if r["kind"] != "HS":
            return float(r["mass_each_kg"]) if r["mass_each_kg"] not in ("",) else 0.0   # per piece or per metre
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
    """The tube cut list: one row per member of each frame (D-120's member parts), with the outer
    length, the end cuts (D-117) and the holes and slots. The member's number goes in member_part, as FRONT's cut
    lists key it: a part_number column with a qty makes the checks read the file as a parts list (C06, C11), and the
    parts list already carries each member's row."""
    rows = []
    for half, fkey in (("C1", "frame_c1"), ("C2", "frame_c2")):
        for code, key, name, sec, L, ends, extra in member_rows(v, half):
            rows.append({"frame": M.PARTS[fkey][0], "half": half, "member": code, "member_part": M.PARTS[key][0],
                         "name": M.PARTS[key][1],
                         "section": "galvanized steel %s (S280GD+Z or SGC400, yield 280 MPa or more, Z100; D-131)" % sec,
                         "length_mm": "%.2f" % L, "qty": 1,
                         "ends": "%s; welded into the frame (D-131, J-FRAME-01): corners with the 2.0 mitre plates, T joints direct" % ends,
                         "holes": "; ".join(extra) or "none",
                         "status": "calculation (from the parameters)"})
    return rows


def flat_cut_list(v):
    """Felt and fill pieces with size, material, tolerance and part number: D-89 (PM ruling
    2026-11-01) lets a plain knife-cut felt or fill rectangle go without a drawing when this
    list gives them, and D-128 (PM ruling 2026-11-01) the notched fill strips too: their DXF gives the full outline
    with every notch, and this row the material, density, thickness, tolerance and part number."""
    rows = []
    fw = v["cs_w"] - 2 * (v["tray_t"] + v["felt_c"])
    fd = v["cs_d"] - 2 * (v["tray_t"] + v["felt_c"])
    pn, name, vn, _k, mat = M.PARTS["felt"]
    rows.append({"part_number": pn, "name": name, "name_vi": vn, "material": M.MATERIALS[mat][0],
                 "size_mm": "%.1f x %.1f x %.0f" % (fw, fd, v["felt_t"]), "qty_per_pod": 2,
                 "tolerance": "knife cut +/-1 (assumption)", "drawing": "none (D-89: plain rectangle)",
                 "cut_file": fname("felt", "DXF", "dxf"),
                 "note": "2 sprinkler drop zones D%.0f marked on the MARK layer, nothing cut (REQ-US-01)" % v["sprk_d"]})
    seen = set()
    for key, _bay, box, notches in M.fill_strips(v):
        if key in seen:
            continue
        seen.add(key)
        b = [M.ev(v, e) for e in box]
        pn, name, vn, _k, mat = M.PARTS[key]
        n = sum(1 for _n, nb in notches if M.overlap(tuple(b), tuple(M.ev(v, e) for e in nb)))
        rows.append({"part_number": pn, "name": name, "name_vi": vn, "material": M.MATERIALS[mat][0],
                     "size_mm": "%.1f x %.1f x %.0f" % (b[1] - b[0], b[3] - b[2], v["fill_t"]), "qty_per_pod": 2,
                     "tolerance": "cut +/-2 (assumption)",
                     "drawing": "none (D-128: its DXF gives the full outline with every notch)",
                     "cut_file": fname(key, "DXF", "dxf"), "note": "%d notches clearing clips and catches by fill_c" % n})
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
