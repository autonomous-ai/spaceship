"""v1 (Indoor Pod V3) weight from its materials BOM, as a range, plus a STEP cross-check.

The BOM (2026-10-29) is newer than the STEP (2026-10-14), so the BOM is the main
source. The STEP only cross-checks the big items. Known conflict (already on the
Control Engineer's issue list): the BOM lists 9 mm inner and floor boards, the
drawings and the STEP show 15 mm ply.
"""
import csv
import functools
import os
from collections import OrderedDict

import openpyxl

from inputs import p
from shapes import chs_kgm, plate_kg, steel_rhs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BOM_PATH = os.path.join(REPO, "sources", "v1", "indoor-pod-v3-bom-v5-2026-10-29.xlsx")
STEP_CSV = os.path.join(HERE, "..", "data", "v1_step_solids.csv")

# BOM group code -> guideline assembly
GROUP_ASSY = {"FL": "BASE", "FLR": "BASE", "LW": "WALL", "RW": "WALL", "BWL": "WALL",
              "BWC": "WALL", "BWR": "WALL", "CL": "CEILING", "DL": "FRONT", "DR": "FRONT",
              "DT": "FRONT", "GL": "FRONT", "GW": "FRONT", "TB": "INTERIOR", "VT": "WALL"}

# purchased items: (kg each, parameter name or None, assembly)
BOUGHT = {
    "Chân tăng chỉnh D50 ren M12": ("foot_kg", "BASE"),
    "Quạt thông gió 200x200x60": ("fan_v1_kg", "AIR"),
    "Đèn ốp trần vuông 170x170": ("light_kg", "ELECTRICAL"),
    "Công tắc (mặt 86x86)": ("plate_kg", "ELECTRICAL"),
    "Ổ cắm điện (mặt 86x86)": ("plate_kg", "ELECTRICAL"),
    "Ổ mạng LAN (mặt 86x86)": ("plate_kg", "ELECTRICAL"),
    "Jack LAN": ("plate_kg", "ELECTRICAL"),
    "Jack nguồn": ("plate_kg", "ELECTRICAL"),
    "Bản lề cửa kính": ("hinge_kg", "FRONT"),
    "Tay nắm cửa kính 300 mm": ("handle_kg", "FRONT"),
}
SCREW_KG = {"Vít M8x60": 0.035, "Vít M8x40": 0.026, "Tán cấy M8x20": 0.010}  # assumption: steel M8 hardware


def read_bom():
    """BOM lines (read once; callers must not change the returned rows)."""
    return _read_bom()


@functools.lru_cache(maxsize=1)
def _read_bom():
    wb = openpyxl.load_workbook(BOM_PATH, data_only=True)
    ws = wb["BOM"]
    rows, group = [], None
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] is not None and isinstance(r[0], str) and "—" in r[0]:
            group = r[0].split("—")[0].strip()
            continue
        if not isinstance(r[0], (int, float)):
            continue
        code, item, mat, spec, L, W, T, qty, tot_len, area, note = r[1:12]
        rows.append(dict(code=code, item=item, mat=mat, spec=spec, L=L, W=W, T=T, qty=qty,
                         tot_len=tot_len, area=area, note=note, group=group))
    return tuple(rows)


def line_mass(r, case):
    """Mass of one BOM line in kg. case: 'bom', 'lo' or 'drawing' (15 mm boards, high densities)."""
    spec, qty = r["spec"], r["qty"] or 0
    rho_ply = {"bom": p("rho_ply"), "lo": p("rho_ply_lo"), "drawing": p("rho_ply_hi")}[case]
    rho_tim = {"bom": p("rho_timber"), "lo": p("rho_timber_lo"), "drawing": p("rho_timber_hi")}[case]
    if spec.startswith("Hộp thép"):
        b, h = [float(x) for x in spec.split()[-1].split("x")]
        t = {(100, 50): p("t_steel_50x100"), (20, 20): p("t_steel_20_v1"), (60, 30): p("t_steel_30x60"),
             (16, 16): p("t_steel_16"), (60, 20): p("t_steel_60x20")}[(b, h)]
        return r["tot_len"] * steel_rhs(b, h, t), "steel tube"
    if spec.startswith("Ống thép"):
        return r["tot_len"] * chs_kgm(100, p("t_steel_d100"), p("rho_steel")), "steel tube"
    if spec.startswith("Thanh gỗ 40x40"):
        return r["tot_len"] * 0.04 * 0.04 * rho_tim, "timber"
    if spec.startswith("Ván gỗ"):
        t = float(spec.split()[2])
        if case == "drawing" and t == 9:
            t = 15.0  # drawings and STEP: 15 mm ply for inner lining and floor boards
        return plate_kg(r["area"], t, rho_ply), "board"
    if spec.startswith("Tấm nhôm 2 mm"):
        return r["area"] * p("acp2_kgm2"), "ACP skin"
    if spec.startswith("Tấm nhôm 3 mm"):
        return r["area"] * p("acp3_kgm2"), "ACP skin"
    if spec.startswith("Kính"):
        return r["area"] * 0.010 * p("rho_glass"), "glass"
    if spec.startswith(("Pát", "Bản mã", "Bản thép")):
        L, W, T = r["L"], r["W"], r["T"]
        t = 3.0 if "3 mm" in spec else 2.0
        if spec.startswith("Pát thép bẻ góc"):
            area = L * (W + T) * 1e-6   # bent bracket: leg lengths W and T
        else:
            area = L * W * 1e-6
        return qty * plate_kg(area, t, p("rho_steel")), "steel plate"
    if spec in SCREW_KG:
        return qty * SCREW_KG[spec], "fasteners"
    if spec in BOUGHT:
        return qty * p(BOUGHT[spec][0]), "bought"
    raise ValueError(f"unmapped BOM line {r['code']} {spec}")


def assembly_of(r):
    if r["spec"] in BOUGHT:
        return BOUGHT[r["spec"]][1]
    if r["item"] in ("Ốp trong", "Ốp trang trí mặt trong"):
        return "LINING"
    return GROUP_ASSY[r["group"].split("-")[0] if r["group"] else "VT"]


def v1_weights():
    rows = read_bom()
    out = OrderedDict()
    lines = []
    for case in ("lo", "bom", "drawing"):
        by_assy = OrderedDict((a, 0.0) for a in ("BASE", "WALL", "FRONT", "CEILING", "LINING", "AIR", "ELECTRICAL", "INTERIOR"))
        for r in rows:
            kg, kind = line_mass(r, case)
            by_assy[assembly_of(r)] += kg
            if case == "bom":
                lines.append((r["code"], r["spec"], kind, assembly_of(r), kg))
        out[case] = by_assy
    return out, lines


def biggest_v1_parts():
    """Shipping pieces of v1 named in its BOM sheet, with BOM-based weights (central case)."""
    rows = read_bom()
    pieces = OrderedDict()
    for r in rows:
        if r["spec"] in BOUGHT or r["spec"] in SCREW_KG:
            continue
        grp = r["code"].split("-")[0]
        kg, _ = line_mass(r, "bom")
        pieces[grp] = pieces.get(grp, 0.0) + kg
    return pieces


# ---------------------------------------------------------------- STEP cross-check
def step_rows():
    with open(STEP_CSV) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in r:
            r[k] = float(r[k])
        r["t"] = 2 * r["volume_mm3"] / r["area_mm2"]   # thin-wall thickness estimate
    return rows


def step_crosscheck():
    """Quantities of the big v1 items as modelled in the STEP vs the BOM (central densities)."""
    rows = step_rows()
    q = OrderedDict((k, 0.0) for k in ("board_15", "board_12", "board_6", "skin_2", "glass_10", "timber", "base_tube"))
    for r in rows:
        o1, o2, o3 = r["obb1"], r["obb2"], r["obb3"]
        vol_dm3 = r["volume_mm3"] / 1e6
        if 9.3 <= o1 <= 10.7 and o3 > 1900:
            q["glass_10"] += r["volume_mm3"] / 10 / 1e6               # m2
        elif 14 <= o1 <= 16 and o2 > 500:
            q["board_15"] += r["volume_mm3"] / 15 / 1e6
        elif 11 <= o1 <= 13 and o2 > 500:
            q["board_12"] += r["volume_mm3"] / 12 / 1e6
        elif 5.5 <= o1 <= 6.5 and o2 > 200:
            q["board_6"] += r["volume_mm3"] / 6 / 1e6
        elif 1.8 <= o1 <= 2.2 and o2 > 200:
            q["skin_2"] += r["volume_mm3"] / 2 / 1e6
        elif 38 <= o1 <= 43 and 38 <= o2 <= 58 and o3 > 400:
            q["timber"] += vol_dm3 / 1000                               # m3
        elif r["cz"] < 130 and 1.8 <= r["t"] <= 2.2 and o3 > 100:
            q["base_tube"] += vol_dm3 / 1000                            # m3 of steel
    bom = read_bom()
    b = OrderedDict((k, 0.0) for k in q)
    for r in bom:
        s = r["spec"]
        if s.startswith("Ván gỗ 9 mm"):
            b["board_15"] += r["area"]            # same parts; BOM says 9 mm
        elif s.startswith("Ván gỗ 6 mm"):
            b["board_6"] += r["area"]
        elif s.startswith("Tấm nhôm 2 mm"):
            b["skin_2"] += r["area"]
        elif s.startswith("Kính"):
            b["glass_10"] += r["area"]
        elif s.startswith("Thanh gỗ"):
            b["timber"] += r["tot_len"] * 0.0016
        elif s.startswith("Hộp thép") and r["group"].startswith("FL"):
            bb, hh = [float(x) for x in s.split()[-1].split("x")]
            t = {(100, 50): p("t_steel_50x100"), (20, 20): p("t_steel_20_v1"), (60, 30): p("t_steel_30x60")}[(bb, hh)]
            b["base_tube"] += r["tot_len"] * steel_rhs(bb, hh, t) / p("rho_steel")
    rho_ply, rho_tim = p("rho_ply"), p("rho_timber")
    kg = lambda k, v, thick: {  # noqa: E731
        "board_15": v * thick * 1e-3 * rho_ply, "board_12": v * 12e-3 * rho_ply, "board_6": v * 6e-3 * rho_ply,
        "skin_2": v * p("acp2_kgm2"), "glass_10": v * 10e-3 * p("rho_glass"),
        "timber": v * rho_tim, "base_tube": v * p("rho_steel")}[k]
    table = []
    for k in q:
        table.append((k, b[k], q[k], kg(k, b[k], 9.0), kg(k, q[k], 15.0)))
    return table
