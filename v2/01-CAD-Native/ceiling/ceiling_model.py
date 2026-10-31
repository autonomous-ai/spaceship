"""Spaceship (FocusPod v2) CEILING: parameters and layout, without Fusion.

The Fusion build (`ceiling_build.py`), the offline tests and the exports
(parts list, cut list, flat pattern check) all read this file, so the layout
is written once.

Parameters come from two places:

1. The pod skeleton P03 (`../skeleton/100000_P03_POD-SKELETON-PARAMETERS.csv`),
   loaded at build time with its own names, expressions, statuses and sources.
   No skeleton number is copied here.
2. The ceiling's own parameters (`CEILING_PARAMS` below), written as
   expressions of the skeleton's. Each carries its status and source
   (conventions.md section 9).

Coordinates (conventions.md section 4): pod origin on the room floor at the
pod centre, +X right (seen from outside, facing the door), +Y back, +Z up.
The ceiling cassette is one part for both halves (COMMON, PM ruling
2026-10-31); it has its own system CS-510301, see `CASSETTE_CS`.
"""

import csv
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "P01"


def current_skeleton_csv():
    """The skeleton's parameter list with the highest revision in ../skeleton/."""
    found = glob.glob(os.path.join(HERE, "..", "skeleton", "100000_P[0-9][0-9]_POD-SKELETON-PARAMETERS.csv"))
    if not found:
        raise FileNotFoundError("no skeleton parameter CSV next to the ceiling folder")
    path = max(found, key=lambda f: os.path.basename(f)[7:10])
    return os.path.abspath(path), os.path.basename(path)[7:10]


SKELETON_CSV, SKELETON_REV = current_skeleton_csv()


def use_skeleton(path):
    """Point the model at another skeleton parameter list (for a test build against an
    open skeleton PR); returns its revision."""
    global SKELETON_CSV, SKELETON_REV
    SKELETON_CSV = os.path.abspath(path)
    SKELETON_REV = os.path.basename(path)[7:10]
    return SKELETON_REV

# Ceiling parameters the skeleton may take over; the skeleton's own then wins.
SKELETON_MAY_DEFINE = {"seam_gap"}

PM_RULING = "PM ruling on the CEILING plan, 2026-10-31"

# name, expression, unit ("mm" or "" for a count), status, source.
# A parameter may use only the skeleton's parameters and the ones above it.
CEILING_PARAMS = [
    # ---- outer panel C1 / C2: frame and skin (D-16, D-34, D-42, D-55)
    ("seam_gap", "2.26 mm", "mm", "confirmed",
     "PM ruling 2026-10-31 (Fusion group): the Joints Engineer's 2.26 mm, set by a metal stop washer, on every frame-to-frame seam; the skeleton's own value replaces this one once it carries it"),
    ("acp_t", "3 mm", "mm", "source", "build plan VT01: ACP 3 mm, Dark Yellow EV3038 (selection A1); in the 81 mm stack (D-42)"),
    ("tube_w", "20 mm", "mm", "confirmed", "D-34, D-54: aluminium 20 x 40 x 1.2 members (the 20 mm face lies in the plane of the panel)"),
    ("tube_t", "1.2 mm", "mm", "confirmed", "D-54: the frames stay 1.2 mm (rivnut grip check passed)"),
    ("fr_d", "40 mm", "mm", "confirmed", "D-34, D-42: the frame is the 40 mm face of the 20 x 40 tube"),
    ("bond_t", "outer_t - acp_t - fr_d", "mm", "calculation",
     "bond line between the frame and the skin: the skeleton's outer panel less skin and frame (0 at P03's 43; 3 at outer_t 46, PM ruling 2026-10-31: 3 ACP + 3 bond + 40 frame)"),
    ("fr_n", "3", "", "confirmed", PM_RULING + ": 3 cross members between the side and seam members"),
    ("fr_pitch", "(wall_depth - tube_w) / (fr_n + 1)", "mm", "calculation",
     "centre spacing of the cross members, front member to back member: (1495 - 20) / 4 = 368.75, 400 or less (D-16)"),
    ("c_w", "pod_w / 2 - outer_t - 3 * seam_gap / 2", "mm", "calculation",
     "ceiling half width between the side frame and the centre seam, less a seam gap at the side and half a gap at the centre (D-55, seam ruling): 1203.61"),
    # ---- the cassette: one part for both halves (CS-510301)
    ("cs_front", "360 mm", "mm", "confirmed",
     "D-60 soffit over the door head, 360 deep and 220 tall (Z 2120 to 2340), flush with the air column's face (PM rulings 2026-10-31, air group); the cassettes stop at its back face (PM ruling 2026-10-31)"),
    ("cs_gap", "3 mm", "mm", "assumption",
     "edge gap round the cassette to the next lining, the other cassette or the top decor block; the 3.2 mm PORON gasket (selection D) just touches across it"),
    ("cs_w", "inner_w / 2 - 2 * cs_gap", "mm", "calculation", "cassette width: half the 2338 inside width less a gap each side = 1163"),
    ("cs_d", "wall_depth - stack_t - cs_front - 2 * cs_gap", "mm", "calculation",
     "cassette length front to back: the 1414 envelope (decor back plate to the back lining face) less the soffit and a gap each end = 1408 with no soffit"),
    ("tray_t", "0.5 mm", "mm", "confirmed", "D-37: galvanised steel tray 0.5 mm (DX51D+Z, selection B)"),
    ("tray_h", "cass_t", "mm", "calculation",
     PM_RULING + ": the returns run the full cassette depth (34) and turn in under the felt edge"),
    ("lip_w", "12 mm", "mm", "confirmed", PM_RULING + ": a 12 mm lip under the felt edge"),
    ("bend_r", "tray_t", "mm", "assumption", "inside bend radius 1 x t for 0.5 mm DX51D (the sheet metal rule's bend radius is its Thickness); the factory's tooling sets it (guideline 9)"),
    ("felt_t", "9 mm", "mm", "confirmed", "D-17: 9 mm PET felt on the cassette face (plan VT03-PET)"),
    ("felt_c", "1 mm", "mm", "assumption", "felt edge clearance inside the returns, so the felt drops onto the lips"),
    ("gap_h", "tray_h - felt_t - 2 * tray_t", "mm", "calculation",
     "air gap between the tray base and the felt (24): the cable path (D-41) and the acoustic gap (D-17)"),
    ("rib_n", "2", "", "confirmed", PM_RULING + ": 2 ribs keep the felt flat"),
    ("rib_off", "cs_w / 6", "mm", "calculation",
     "rib centre from the cassette centre line: with 2 ribs the felt spans 3 equal widths of cs_w / 3 = 388"),
    ("rib_crown", "20 mm", "mm", "assumption", "flat width of the rib that carries the felt"),
    ("rib_fl", "12 mm", "mm", "assumption", "rib top flange width against the tray base; the rib-to-tray joint is HOLD"),
    ("rib_end", "5 mm", "mm", "assumption", "clearance from each rib end to the returns"),
    ("fill_t", "40 mm", "mm", "confirmed", "D-24, D-54: 40 mm PET fill at 32 kg/m3 rides on the cassette back"),
    ("fill_c", "5 mm", "mm", "assumption",
     "fill clearance to the frame members, clips and catches, so the cassette never touches the frame (D-17)"),
    ("fill_min", "100 mm", "mm", "assumption", "a fill strip shorter than this isn't made (a bay mostly over the soffit)"),
    ("fill_hw", "inner_w / 4 - seam_gap / 2 - tube_w - fill_c", "mm", "calculation",
     "half length of a fill strip, set by the seam member over the cassette's inner edge and used on both sides, so both cassettes stay the same part"),
    # ---- HOLD envelopes: space kept for parts not yet named (guideline 4.3)
    ("clip_w", "40 mm", "mm", "assumption", "clip space along X; HOLD H03 / ISS-076 until a clip is named with its rating"),
    ("clip_d", "30 mm", "mm", "assumption", "clip space out from the member face; HOLD H03 / ISS-076"),
    ("clip_h", "30 mm", "mm", "assumption", "clip space above the tray; HOLD H03 / ISS-076"),
    ("catch_w", "40 mm", "mm", "assumption", "safety catch space along X; HOLD H04 / ISS-076"),
    ("catch_d", "30 mm", "mm", "assumption", "safety catch space out from the member face; HOLD H04 / ISS-076"),
    ("catch_h", "40 mm", "mm", "assumption", "safety catch space above the tray, up the member face; HOLD H04 / ISS-076"),
    # ---- lights, cables, sprinkler reserve
    ("light_hole", "58 mm", "mm", "source", "Haefele Loox5 LED 2094: recess in a 58 mm hole (selection E, 20D5-115A)"),
    ("light_n", "3", "", "calculation", "6 downlights over the ceiling (selection E plan row) = 3 per cassette, on its centre line"),
    ("ring_od", "100 mm", "mm", "assumption", "light plate size (square): a rigid seat on the felt for the light's springs"),
    ("ring_t", "1 mm", "mm", "assumption", "light plate thickness, galvanised steel; the light's clamping range is unverified (selection E)"),
    ("cable_hole", "20 mm", "mm", "assumption", "cable hole in the front and back returns for a grommet; grommet HOLD"),
    ("sprk_d", "150 mm", "mm", "assumption", "reserved round zone for a later sprinkler drop (REQ-US-01)"),
]

# Part numbers: CEILING 41xxxx, ceiling cassette 5103xx (assemblies) and
# 513xxx (parts), LINING bought items 518xxx (PM ruling 2026-10-31,
# conventions section 6). Checked against the reserved list by the tests.
RESERVED = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}

# key: part number, name, Vietnamese name, kind (MP made, PI bought, HS
# assembly, HOLD envelope), material key
PARTS = {
    "ceiling": ("410000", "CEILING", "Trần", "HS", None),
    "assy_c1": ("410101", "CEILING - PANEL ASSY - C1", "Trần - tấm trái (cụm)", "HS", None),
    "assy_c2": ("410102", "CEILING - PANEL ASSY - C2", "Trần - tấm phải (cụm)", "HS", None),
    "frame_c1": ("411101", "CEILING - PANEL FRAME - C1", "Trần trái - khung nhôm", "MP", "al"),
    "frame_c2": ("411102", "CEILING - PANEL FRAME - C2", "Trần phải - khung nhôm", "MP", "al"),
    "skin": ("411301", "CEILING - SKIN - COMMON", "Trần - tấm ốp alu (dùng chung trái/phải)", "MP", "acp"),
    "cassette": ("510301", "LINING - CASSETTE - CEILING - COMMON", "Cassette trần (dùng chung trái/phải)", "HS", None),
    "tray": ("513101", "LINING - TRAY - CEILING", "Khay thép cassette trần", "MP", "steel"),
    "rib": ("513102", "LINING - RIB - CEILING", "Gân đỡ tấm tiêu âm trần", "MP", "steel"),
    "felt": ("513201", "LINING - FELT - CEILING", "Tấm tiêu âm PET 9 mm - trần", "MP", "felt"),
    "fill_a": ("513301", "LINING - FILL - CEILING - BAY A", "Bông PET 40 mm - trần - ô A", "MP", "fill"),
    "fill_b": ("513302", "LINING - FILL - CEILING - BAY B", "Bông PET 40 mm - trần - ô B", "MP", "fill"),
    "fill_c": ("513303", "LINING - FILL - CEILING - BAY C", "Bông PET 40 mm - trần - ô C", "MP", "fill"),
    "fill_d": ("513304", "LINING - FILL - CEILING - BAY D", "Bông PET 40 mm - trần - ô D", "MP", "fill"),
    "ring": ("513401", "LINING - LIGHT PLATE - CEILING", "Tấm đỡ đèn âm trần", "MP", "steel"),
    "clip": ("518001", "LINING - CASSETTE CLIP - HOLD", "Kẹp treo cassette (chờ chọn)", "HOLD", "hold"),
    "catch": ("518002", "LINING - CEILING SAFETY CATCH - HOLD", "Dây an toàn cassette trần (chờ chọn)", "HOLD", "hold"),
}

# material key: name in the CAD, density kg/m3, status, source
MATERIALS = {
    "al": ("Aluminium 6063-T6 (alloy HOLD, ISS-034)", 2700.0, "source", "aluminium density; alloy and temper open (ISS-034, H15)"),
    "steel": ("Galvanised steel DX51D+Z", 7850.0, "source", "EN 10346 DX51D+Z (selection B): 0.5 mm = 3.93 kg/m2"),
    "acp": ("ACP 3 mm EV3038, 3.5 kg/m2", 3.5 / 0.003, "calculation", "3.5 kg/m2 (layout study acp3_kgm2, PM ruling) / 3 mm"),
    "felt": ("PET felt 9 mm, 1.8 kg/m2", 1.8 / 0.009, "calculation", "1.8 kg/m2 (layout study pet9_kgm2) / 9 mm; the factory's felt is unverified (D-31)"),
    "fill": ("PET fill 32 kg/m3 (Sorberpoly 2D)", 32.0, "confirmed", "D-54: 32 kg/m3 until the wall sample tests 25"),
    "hold": ("HOLD envelope - no mass", 1.0, "assumption", "space only; the real part's mass comes with its datasheet"),
}

# The cassette's own system CS-510301 (one part, used at C1-CASS and C2-CASS):
# origin at the cassette envelope's centre line (X), its front plane (Y: the
# decor's back plate Y -645, or the soffit's back face, cs_front behind it, D-60) and its top (Z, the tray base top, 4 mm under the
# roof frame). Axes parallel to the pod's. Pod position of the origin:
CASSETTE_CS = {
    "C1": ("-inner_w / 4", "pod_d / 2 - wall_depth + cs_front", "pod_h - stack_t + cass_t"),
    "C2": ("inner_w / 4", "pod_d / 2 - wall_depth + cs_front", "pod_h - stack_t + cass_t"),
}

# ---------------------------------------------------------------- expressions

_MM = re.compile(r"(?<![A-Za-z_])(\d+(?:\.\d+)?)\s*mm\b")


def to_python(expr):
    """Fusion expression -> Python expression in mm (only what this pack uses).
    Fusion separates function arguments with ";"."""
    return _MM.sub(r"\1", expr).replace(";", ",")


def load_skeleton(path=None):
    """[(name, expression, unit, status, source)] from the skeleton's own CSV."""
    path = path or SKELETON_CSV
    rows = []
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append((r["parameter"], r["expression"], "mm", r["status"],
                         "skeleton %s: %s" % (SKELETON_REV, r["source"])))
    return rows


def all_params(skeleton_rows=None):
    sk = skeleton_rows if skeleton_rows is not None else load_skeleton()
    have = {r[0] for r in sk}
    clash = [p[0] for p in CEILING_PARAMS if p[0] in have and p[0] not in SKELETON_MAY_DEFINE]
    if clash:
        raise ValueError("ceiling parameter names clash with the skeleton: %s" % clash)
    return list(sk) + [p for p in CEILING_PARAMS if p[0] not in have]


def evaluate(params, overrides=None):
    """Values in mm (or plain numbers) for every parameter, in order."""
    env = {"ceil": math.ceil, "floor": math.floor, "abs": abs, "min": min, "max": max, "sqrt": math.sqrt}
    overrides = overrides or {}
    vals = {}
    for name, expr, _unit, _st, _src in params:
        e = overrides.get(name, expr)
        vals[name] = float(eval(to_python(e), {"__builtins__": {}}, dict(env, **vals)))
    return vals


def ev(vals, expr):
    env = {"ceil": math.ceil, "floor": math.floor, "abs": abs, "min": min, "max": max}
    return float(eval(to_python(expr), {"__builtins__": {}}, dict(env, **vals)))


# ---------------------------------------------------------------- layout
# Every body is a box given by six expressions (x0, x1, y0, y1, z0, z1), in
# the frame named by `frame`: "pod" (pod system) or "cs" (CS-510301).

YW = "(pod_d / 2 - wall_depth)"      # front plane of the walls and ceiling (decor back plate)
YB = "(pod_d / 2)"                   # back face
ZF0 = "(pod_h - outer_t)"            # underside of the ceiling frame
ZF1 = "(pod_h - outer_t + fr_d)"     # top of the frame (the bond line and the skin sit above it)
ZSKIN = "(pod_h - acp_t)"            # underside of the skin


def frame_members(half):
    """Members of one ceiling frame in the pod system. half 'C1' (-X) or 'C2' (+X).
    Returns [(code, name, axis, (x0, x1, y0, y1, z0, z1))]; axis = the long axis."""
    s = -1 if half == "C1" else 1

    def xr(a, b):            # a, b measured outward from the seam edge (X = seam_gap / 2), as expressions
        a, b = "seam_gap / 2 + %s" % a, "seam_gap / 2 + %s" % b
        lo, hi = ("-(%s)" % b, "-(%s)" % a) if s < 0 else ("(%s)" % a, "(%s)" % b)
        return lo, hi
    out = []
    side = xr("c_w - tube_w", "c_w")
    seam = xr("0 mm", "tube_w")
    inner = xr("tube_w", "c_w - tube_w")
    out.append(("SIDE", "SIDE MEMBER", "y", side + (YW, YB, ZF0, ZF1)))
    out.append(("SEAM", "SEAM MEMBER", "y", seam + (YW, YB, ZF0, ZF1)))
    out.append(("FRONT", "FRONT MEMBER", "x", inner + (YW, YW + " + tube_w", ZF0, ZF1)))
    out.append(("BACK", "BACK MEMBER", "x", inner + (YB + " - tube_w", YB, ZF0, ZF1)))
    for k in range(1, 4):
        y0 = "%s + %d * fr_pitch" % (YW, k)
        out.append(("X%d" % k, "CROSS MEMBER %d" % k, "x", inner + (y0, y0 + " + tube_w", ZF0, ZF1)))
    return out


def skin_box():
    """The skin (COMMON) in its own system: origin at one end of its front edge, Z = 0
    on the frame top, running toward -X. Placed at C1 with its origin on the seam edge
    (X = -seam_gap / 2) and at C2 with its origin on the side edge (X = seam_gap / 2 + c_w):
    a plain rectangle, so the same part fits both."""
    return ("-c_w", "0 mm", "0 mm", "wall_depth", "0 mm", "acp_t")


SKIN_PLACES = {"C1": ("-seam_gap / 2", YW, ZSKIN), "C2": ("seam_gap / 2 + c_w", YW, ZSKIN)}


# cassette, in CS-510301
CS_X0, CS_X1 = "(-cs_w / 2)", "(cs_w / 2)"
CS_Y0, CS_Y1 = "cs_gap", "(cs_gap + cs_d)"
FELT_Z0, FELT_Z1 = "(-tray_h + tray_t)", "(-tray_h + tray_t + felt_t)"


def member_front_cs(k):
    """Y in CS-510301 of the front face of frame member k (0 = front member,
    1..3 = cross members, 4 = back member). The cassette origin sits cs_front
    behind the front plane YW (D-60 soffit)."""
    return "(%d * fr_pitch - cs_front)" % k


def member_back_cs(k):
    return "(%s + tube_w)" % member_front_cs(k)


def clip_boxes():
    """6 clips: on the back faces of cross members 1..3, over the ribs. The back face keeps
    every clip over the cassette for any soffit up to about 385 mm (D-60)."""
    out = []
    for k in (1, 2, 3):
        for side in (-1, 1):
            xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
            yb = member_back_cs(k)
            out.append(("CLIP X%d %s" % (k, "L" if side < 0 else "R"),
                        ("%s - clip_w / 2" % xc, "%s + clip_w / 2" % xc, yb, "%s + clip_d" % yb, "0 mm", "clip_h")))
    return out


def catch_boxes():
    """2 safety catches: on the front face of cross member 2, over the ribs (the clips use its back face)."""
    out = []
    for side in (-1, 1):
        xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
        yf = member_front_cs(2)
        out.append(("CATCH %s" % ("L" if side < 0 else "R"),
                    ("%s - catch_w / 2" % xc, "%s + catch_w / 2" % xc, "%s - catch_d" % yf, yf, "0 mm", "catch_h")))
    return out


FILL_KEYS = ("fill_a", "fill_b", "fill_c", "fill_d")


def fill_strips(vals=None):
    """Fill strips on the tray back, one per frame bay that lies over the cassette.
    Which bays get a strip is decided from the values at build time (vals); the boxes
    stay expressions, so the strips follow later edits. Strips of the same size and
    notches are one part. Returns [(key, bay, (x0, x1, y0, y1, z0, z1), [notch boxes])]."""
    vals = vals if vals is not None else evaluate(all_params())
    strips, kinds = [], {}
    for bay in range(4):
        y0 = "max(%s + tube_w; cs_gap) + fill_c" % member_front_cs(bay)
        y1 = "min(%s; cs_gap + cs_d) - fill_c" % member_front_cs(bay + 1)
        if ev(vals, y1) - ev(vals, y0) < vals["fill_min"]:
            continue
        box = ("-fill_hw", "fill_hw", y0, y1, "0 mm", "fill_t")
        bv = tuple(ev(vals, e) for e in box)
        notches, sig = [], []
        for name, b in clip_boxes() + catch_boxes():
            nb = ("%s - fill_c" % b[0], "%s + fill_c" % b[1], "%s - fill_c" % b[2], "%s + fill_c" % b[3], "0 mm", "fill_t")
            nv = tuple(ev(vals, e) for e in nb)
            if overlap(bv, nv):
                notches.append((name, nb))
                sig.append((round(nv[0], 3), round(nv[1], 3), round(nv[2] - bv[2], 3), round(nv[3] - bv[2], 3)))
        key = (round(bv[3] - bv[2], 3), tuple(sorted(sig)))
        if key not in kinds:
            kinds[key] = FILL_KEYS[len(kinds)]
        strips.append((kinds[key], bay, box, notches))
    return strips


def light_points():
    """Light centres in CS-510301 (X, Y): on the centre line, at 1/6, 3/6, 5/6 of the length."""
    return [("0 mm", "cs_gap + cs_d * %d / 6" % (2 * i + 1)) for i in range(3)]


def sprinkler_points():
    """Two candidate zones for a later sprinkler drop (REQ-US-01), one each side so the
    cassette stays one part: in the middle of the outer felt spans (X' +-cs_w / 3) and of the
    first frame bay over the cassette, clear of ribs, lights, clips and members."""
    y = "%s + (fr_pitch - tube_w) / 2" % member_back_cs(1)
    return [("-cs_w / 3", y), ("cs_w / 3", y)]


def rib_boxes():
    """Rib outline boxes (for clash checks); the rib itself is a hat section."""
    out = []
    for side in (-1, 1):
        xc = "(%s * rib_off)" % ("-1" if side < 0 else "1")
        out.append(("RIB %s" % ("L" if side < 0 else "R"),
                    ("%s - rib_crown / 2 - rib_fl" % xc, "%s + rib_crown / 2 + rib_fl" % xc,
                     CS_Y0 + " + tray_t + rib_end", CS_Y1 + " - tray_t - rib_end", FELT_Z1, "-tray_t")))
    return out


def boxes_mm(vals, boxes):
    return [(n, tuple(ev(vals, e) for e in b)) for n, b in boxes]


def overlap(a, b, tol=1e-6):
    return all(a[2 * i] < b[2 * i + 1] - tol and b[2 * i] < a[2 * i + 1] - tol for i in range(3))


# ---------------------------------------------------------------- flat pattern of the tray

def tray_flat(vals, k=0.44):
    """Flat blank of the tray (mm) by the K-factor rule, for checking Fusion's flat
    pattern: outside sizes w x d, returns tray_h deep overall (two bends each), lips
    lip_w wide (outside), inside radius r = t. Each 90 degree bend takes r + t off
    each straight it meets (outside setback) and adds its bend allowance."""
    t, r = vals["tray_t"], vals["bend_r"]
    ba = math.pi / 2 * (r + k * t)
    w, d, h, lip = vals["cs_w"], vals["cs_d"], vals["tray_h"], vals["lip_w"]
    so = r + t
    base_w, base_d = w - 2 * so, d - 2 * so
    ret = h - 2 * so
    lip_f = lip - so
    side = 2 * ba + ret + lip_f
    return {"bend_allowance": ba, "blank_w": base_w + 2 * side, "blank_d": base_d + 2 * side, "k_factor": k,
            "return_flat": ret, "lip_flat": lip_f}


if __name__ == "__main__":
    p = all_params()
    v = evaluate(p)
    for n in ("c_w", "fr_pitch", "cs_w", "cs_d", "gap_h", "rib_off", "fill_hw", "inner_w"):
        print(n, round(v[n], 3))
    print(tray_flat(v))
