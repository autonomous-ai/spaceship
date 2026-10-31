"""Spaceship (v2) parts, weights and joints for each material set and panel split.

Coordinates (local to this study until the control pack fixes the pod system):
X to the right seen from outside the door, Y from front to back, Z up, origin at
the front-left corner of the footprint on the room floor. Sizes are mm, masses kg.
"""
import csv
import functools
import math
import os
from collections import OrderedDict
from dataclasses import dataclass, field, replace

from inputs import p
from shapes import al_rhs, frame_length_mm, plate_kg, steel_rhs
from v1_weights import STEP_CSV, line_mass, read_bom

ASSEMBLIES = ("BASE", "WALL", "FRONT", "CEILING", "LINING", "AIR", "ELECTRICAL", "INTERIOR")


@dataclass
class Part:
    pid: str
    name: str
    name_vi: str
    assy: str
    dims: tuple          # shipping envelope (a, b, c) in mm, any order
    qty: int
    kg: float            # each
    ship: str            # upright | long | glass | box
    status: str = "calculation"
    note: str = ""

    @property
    def total(self):
        return self.kg * self.qty


# ---------------------------------------------------------------- material sets
PLAN = dict(key="plan", label="v2 as planned", frame="steel", ply=True, core=None, floor="raised",
            front="glass10", table=True, seals=False, vents=False, fill=False, voice=False, sensor=False)
LIGHT = dict(key="light", label="Spaceship light indoor build", frame="al", ply=False, core=None, floor="thin",
             front="glass8", table=False, seals=True, vents=True, fill=True, voice=True, sensor=True,
             prefit=False, captive=False, cams=False, prehung=False, ordered=False, sound_kgm2=0.0, ceiling_sound=True)
# DECIDED fast-assembly build (PM ruling 2026-10-31): same parts and weight, more done in the factory
FAST = dict(LIGHT, key="fast", label="Spaceship light build, fast assembly (DECIDED)",
            prefit=True, captive=True, cams=True, prehung=True, ordered=True)
PLAN.update(prefit=False, captive=False, cams=False, prehung=False, ordered=False, sound_kgm2=0.0, ceiling_sound=True)
CAM_JOINTS = ("J-WALL-01", "J-WALL-02", "J-WALL-03", "J-WALL-04", "J-CEIL-02")


def variant(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


# ---------------------------------------------------------------- geometry
def geom():
    wall_h = p("pod_h") - p("glide_h") - p("base_h")          # 2290
    t = p("wall_t_plan")
    tc = p("ceil_t") or t
    inner_w = p("pod_w") - 2 * t                               # 2424, back wall and ceiling between side walls
    back_h = wall_h - tc                                       # back wall stands under the ceiling
    return dict(wall_h=wall_h, t=t, tc=tc, inner_w=inner_w, back_h=back_h, depth=p("wall_depth"),
                inner_d=p("wall_depth") - t)


# ---------------------------------------------------------------- unit masses
def frame_kgm(m, depth=None):
    """kg/m of a wall or ceiling frame member; the decor core keeps 20 x 20 (depth=20)."""
    d = p("frame_depth") if depth is None else depth
    if m["frame"] == "steel":
        return steel_rhs(20, d, p("t_steel_20"))
    return al_rhs(20, d, p("t_al_20"))


def panel_kg(w, h, m, felt_area=0.0, ceiling=False):
    """One wall or ceiling panel. Felt is included only when it is pre-fitted in the factory (m['prefit'])."""
    area = w * h * 1e-6
    kg = area * p("acp3_kgm2")
    if m.get("prefit") and not m.get("leaf"):
        kg += felt_area * (p("pet9_kgm2") + p("felt_fix_kgm2"))
    if m.get("sound_kgm2") and not m.get("leaf") and (not ceiling or m.get("ceiling_sound", True)):
        kg += area * m["sound_kgm2"]
    if m["core"] is None:
        pitch = p("stud_pitch_ply") if m["ply"] else p("stud_pitch_acp")
        kg += frame_length_mm(w, h, pitch) * 1e-3 * frame_kgm(m)
        if m["ply"]:
            kg += plate_kg(area, 6, p("rho_ply")) + area * p("bond_kgm2")
        else:
            kg += area * p("bond_kgm2")
        if m["fill"]:
            kg += area * p("fill_kgm2") * p("frame_depth") / 20.0      # fill scales with cavity depth
    else:
        perim = 2 * (w + h) * 1e-3 * frame_kgm(m)            # edge frame only; the core carries the skin
        core = p("foam25_kgm2") + p("al05_kgm2") if m["core"] == "foam" else p("hc10_kgm2")
        kg += perim + area * (core + 2 * p("bond_kgm2"))
    return kg


def glass_kg(area, m):
    f = m["front"]
    if f == "glass10":
        return plate_kg(area, 10, p("rho_glass"))
    if f == "glass8":
        return plate_kg(area, 8, p("rho_glass"))
    if f == "lam44":
        return plate_kg(area, 8, p("rho_glass")) + area * p("pvb_kgm2")
    if f.startswith("acrylic"):
        return plate_kg(area, float(f[len("acrylic"):]), p("rho_pmma"))
    raise ValueError(f)


FRONT_LABEL = {"glass10": "10 mm tempered glass", "glass8": "8 mm tempered glass", "lam44": "4+4 laminated glass, frameless",
               "acrylic8": "8 mm smoked acrylic", "acrylic10": "10 mm smoked acrylic"}


# ---------------------------------------------------------------- v1-derived inputs
@functools.lru_cache(maxsize=1)
def step_solids():
    with open(STEP_CSV) as f:
        return {int(r["solid"]): {k: float(v) for k, v in r.items()} for r in csv.DictReader(f)}


# STEP solids of the decor skins and the glass, matched to BOM lines by size and position (see report).
DECOR_SKIN_SOLIDS = {"DL": (43, 44, 68), "DR": (77, 78, 79, 80, 81, 82, 127), "DT": (128, 129, 147, 148, 149, 150)}
GLASS_SOLIDS = {"door": 238, "fixed": 239}


def decor_skin_area(block):
    s = step_solids()
    return sum(s[i]["volume_mm3"] for i in DECOR_SKIN_SOLIDS[block]) / 3.0 / 1e6     # 3 mm skins, m2


def decor_skin_area_bom(block):
    return sum(r["area"] for r in read_bom() if r["code"].startswith(block + "-") and r["spec"].startswith("Tấm nhôm 3"))


def glass_area(which):
    return step_solids()[GLASS_SOLIDS[which]]["volume_mm3"] / 10.0 / 1e6               # 10 mm in the STEP, m2


def decor_tube_length(block):
    """Total frame tube length of a decor block from the v1 BOM (16x16 and 60x20), m."""
    return sum(r["tot_len"] for r in read_bom() if r["code"].startswith(block + "-") and r["spec"].startswith("Hộp thép"))


def decor_kg(block, m):
    kg = decor_skin_area(block) * p("acp3_kgm2") + decor_tube_length(block) * frame_kgm(m, depth=20)
    kg += 4 * 0.05   # 4 V-brackets per block, assumption
    return kg


def table_kg():
    return sum(line_mass(r, "bom")[0] for r in read_bom() if r["code"].startswith("TB-"))


def raised_frame_parts():
    """The plan's raised floor (50x100 outer frame, 2 x 30x60 joists) as knock-down bars, using v1's frame outline."""
    parts = []
    rows = [r for r in read_bom() if r["code"].startswith("FL-") and r["spec"] == "Hộp thép 100x50"]
    kgm = steel_rhs(100, 50, p("t_steel_50x100"))
    for r in rows:
        L = r["L"]
        parts.append(Part(f"B-RAIL-{r['code']}", f"BASE - FRAME RAIL 50x100 - L{L:g}", "Khung sàn - thép hộp 50x100",
                          "BASE", (L, 100, 50), int(r["qty"]), L * 1e-3 * kgm, "long" if L > 1683 else "upright",
                          note="v1 outline; welded in v1, knock-down here"))
    kgj = steel_rhs(30, 60, p("t_steel_30x60"))
    parts.append(Part("B-JOIST", "BASE - JOIST 30x60 - L2400", "Nan đỡ ván sàn - thép hộp 30x60", "BASE",
                      (2400, 60, 30), 2, 2.4 * kgj, "long"))
    parts.append(Part("B-FOOT", "BASE - LEVELLING FOOT M10", "Chân tăng đưa M10", "BASE", (60, 60, 80), 6, p("foot_kg"), "box",
                      "assumption"))
    parts.append(Part("B-BRACKET", "BASE - CORNER BRACKET", "Pát góc khung sàn", "BASE", (150, 100, 60), 4, 0.35, "box",
                      "assumption", "bolted corners replace v1 welds"))
    return parts


# ---------------------------------------------------------------- base options
def base_parts(m, split_long):
    g = geom()
    parts = []
    if m["floor"] == "raised":
        parts += raised_frame_parts()
        w, d = 1184.5, 1428.0    # v1 floor board size (drawings: 15 mm ply)
        parts.append(Part("B-BOARD", "BASE - FLOOR BOARD", "Ván sàn", "BASE", (d, w, 15), 2,
                          plate_kg(w * d * 1e-6, 15, p("rho_ply")), "upright"))
        parts.append(Part("B-THRESH", "BASE - FRONT EDGE TRIM", "Ốp mép sàn trước", "BASE", (1917, 204, 3), 1,
                          1.917 * 0.204 * p("acp3_kgm2"), "long"))
        return parts
    # thin floor or no floor: an aluminium base ring that is also the outside base band
    kgm = al_rhs(100, 40, p("t_al_base"))
    side_l = p("pod_d") - 40                     # side rails run from the back corner to the front facet
    back_l = p("pod_w") - 2 * 40                 # back rail sits between the side rails: 2420 fits a 96 in pallet
    rails = [("BACK", back_l, 1), ("SIDE", side_l, 2), ("FRONT-L", 300, 1), ("FRONT-R", 1050, 1)]
    for name, L, q in rails:
        if split_long and L > p("pal_std_l") and L <= 1683:
            parts.append(Part(f"B-BAND-{name}", f"BASE - BASE BAND PIECE 100x40 - {name}", "Viền chân nhôm", "BASE",
                              (L, 100, 40), q, L * 1e-3 * kgm, "upright", note="stands upright on the 48x40"))
        elif split_long and L > 1683:
            n = math.ceil(L / 1683)
            parts.append(Part(f"B-BAND-{name}", f"BASE - BASE BAND PIECE 100x40 - {name} (1/{n})", "Viền chân nhôm",
                              "BASE", (L / n, 100, 40), q * n, L / n * 1e-3 * kgm + 0.1, "upright",
                              note="split with a splice plate"))
        else:
            parts.append(Part(f"B-BAND-{name}", f"BASE - BASE BAND PIECE 100x40 - {name}", "Viền chân nhôm", "BASE",
                              (L, 100, 40), q, L * 1e-3 * kgm, "long" if L > p("pal_std_l") else "upright"))
    parts.append(Part("B-KEY", "BASE - CORNER KEY", "Ke góc đế", "BASE", (120, 80, 40), 6, 0.15, "box", "assumption"))
    parts.append(Part("B-GLIDE", "BASE - LEVELLING GLIDE (hex from above)", "Chân chỉnh cao", "BASE", (50, 50, 40), 8,
                      p("glide_kg"), "box", "assumption"))
    parts.append(Part("B-THRESH", "BASE - DOOR THRESHOLD, LOW", "Ngưỡng cửa thấp", "BASE", (1176, 60, 20), 1, 1.2, "upright",
                      "assumption", "about 20 mm high; replaces the 100 mm band across the door only"))
    if m["floor"] == "thin":
        w, d = g["inner_w"] / 2, g["inner_d"]
        parts.append(Part("B-FLOOR", "BASE - THIN FLOOR PANEL 15 mm", "Tấm sàn mỏng", "BASE", (d, w, 15), 2,
                          plate_kg(w * d * 1e-6, 15, p("rho_ply")) + w * d * 1e-6 * 0.3, "upright",
                          note="15 mm ply + 0.3 kg/m2 finish; lies on the room floor on a 3 mm seal mat"))
    return parts


# ---------------------------------------------------------------- panels per split
def wall_layout(split):
    """Returns [(pid, name, name_vi, assy, w, h, qty)] for walls and ceiling."""
    g = geom()
    out = []
    if split in ("bands", "rows3"):
        n = rows_of(split)[0]
        tag = "BAND" if split == "bands" else "ROW"
        out.append((f"W-SIDE-{tag}", f"WALL - SIDE {tag}", "Vách hông - băng", "WALL", g["depth"], g["wall_h"] / n, 2 * n))
        out.append((f"W-BACK-{tag}", f"WALL - BACK {tag}", "Vách hậu - băng", "WALL", g["inner_w"] / 2, g["back_h"] / n, 2 * n))
    else:
        out.append(("W-SIDE-LO", "WALL - SIDE PANEL - LOWER", "Vách hông - khung dưới", "WALL", g["depth"], g["wall_h"] / 2, 2))
        out.append(("W-SIDE-UP", "WALL - SIDE PANEL - UPPER", "Vách hông - khung trên", "WALL", g["depth"], g["wall_h"] / 2, 2))
        if split == "tallback":
            out.append(("W-BACK-FULL", "WALL - BACK PANEL - FULL HEIGHT", "Vách hậu - khung cao", "WALL", g["inner_w"] / 2, g["back_h"], 2))
        else:
            out.append(("W-BACK-LO", "WALL - BACK PANEL - LOWER", "Vách hậu - khung dưới", "WALL", g["inner_w"] / 2, g["back_h"] / 2, 2))
            out.append(("W-BACK-UP", "WALL - BACK PANEL - UPPER", "Vách hậu - khung trên", "WALL", g["inner_w"] / 2, g["back_h"] / 2, 2))
    out.append(("C-HALF", "CEILING - HALF PANEL WITH FAN OPENING", "Trần - nửa khung", "CEILING", g["inner_w"] / 2, g["depth"], 2))
    return out


def felt_layout():
    """Felt panels (LINING) go on last with Velcro; their split does not follow the wall split."""
    g = geom()
    side_h = g["wall_h"] / 2
    return [("L-FELT-SIDE", "LINING - PET FELT - SIDE", "Tấm tiêu âm PET - vách hông", g["inner_d"], side_h, 4),
            ("L-FELT-BACK", "LINING - PET FELT - BACK", "Tấm tiêu âm PET - vách hậu", g["inner_w"] / 2, g["back_h"] / 2, 4),
            ("L-FELT-CEIL", "LINING - PET FELT - CEILING", "Tấm tiêu âm PET - trần", g["inner_w"] / 2, g["inner_d"], 2)]


def decor_parts(m, split_long):
    g = geom()
    envelopes = {"DL": (278, g["wall_h"]), "DR": (1016, g["wall_h"]), "DT": (1697, 280)}
    names = {"DL": ("FRONT - DECOR BLOCK - LEFT", "Khung trang trí - khối trái"),
             "DR": ("FRONT - DECOR BLOCK - RIGHT", "Khung trang trí - khối phải"),
             "DT": ("FRONT - DECOR BLOCK - TOP", "Khung trang trí - khối trên")}
    parts = []
    for b, (w, h) in envelopes.items():
        kg = decor_kg(b, m)
        long_dim = max(w, h)
        if split_long and long_dim > 1683:
            n = 2
            dims = (w, h / n, p("decor_depth")) if h >= w else (w / n, h, p("decor_depth"))
            parts.append(Part(f"F-{b}", names[b][0] + " (half)", names[b][1] + " (nửa)", "FRONT", dims, n, kg / n + 0.3,
                              "upright", note="split for 48x40; seam crosses the black faceted front (look risk)"))
        else:
            parts.append(Part(f"F-{b}", names[b][0], names[b][1], "FRONT", (w, h, p("decor_depth")), 1, kg,
                              "long" if long_dim > 1683 else "upright"))
    return parts


def front_parts(m, split_long):
    parts = decor_parts(m, split_long)
    for which, w, h, pid, name, vi in (("door", p("glass_door_w"), p("glass_door_h"), "F-GLASS-DOOR", "FRONT - GLASS DOOR", "Cửa kính"),
                                       ("fixed", p("glass_fixed_w"), p("glass_fixed_h"), "F-GLASS-FIXED", "FRONT - FIXED GLASS", "Vách kính cố định")):
        t = {"glass10": 10, "glass8": 8, "lam44": 9, "acrylic8": 8, "acrylic10": 10}[m["front"]]
        parts.append(Part(pid, f"{name} ({FRONT_LABEL[m['front']]})", vi, "FRONT", (h, w, t), 1, glass_kg(glass_area(which), m),
                          "glass", note="weight from the finished shape in the STEP; exempt from the 20 kg rule"))
    hw = 3 * p("hinge_kg") + p("handle_kg")
    if m["seals"]:
        g_len = 2 * (p("glass_fixed_h") + p("glass_fixed_w")) * 1e-3
        hw += p("drop_seal_kg") + g_len * p("glazing_profile_kgm")
    parts.append(Part("F-HW", "FRONT - DOOR AND GLAZING HARDWARE KIT", "Phụ kiện cửa và kính", "FRONT", (600, 400, 150), 1, hw,
                      "box", "assumption", "3 hinges, pull" + (", drop seal, sealed glazing profiles" if m["seals"] else "")))
    return parts


def service_parts(m):
    final = m.get("stack") == "final"
    if final:
        parts = [Part("A-FAN", "AIR - INLINE FAN (S&P TD-350/100-125, sound study's pick)", "Quạt thông gió", "AIR", (350, 280, 280), 2,
                      p("fan_final_kg"), "box", "source")]
    else:
        parts = [Part("A-FAN", "AIR - CEILING FAN (Panasonic FV-15AUL1 per plan)", "Quạt thông gió", "AIR", (300, 300, 200), 2,
                      p("fan_kg"), "box", "unverified")]
    if m["vents"] and final:
        # splitter silencers that sit inside the decor blocks, shipped as their own parts (sizes assumed to fit the blocks)
        parts.append(Part("A-SIL-DR", "AIR - SPLITTER SILENCER FOR THE RIGHT DECOR BLOCK (2 mm Al casing)", "Bộ tiêu âm khối phải", "AIR",
                          (1100, 300, 160), 1, p("sil_right_kg"), "upright", "source", "slides into the mounted block from inside"))
        parts.append(Part("A-SIL-DT", "AIR - SPLITTER SILENCER FOR THE TOP DECOR BLOCK (2 mm Al casing)", "Bộ tiêu âm khối trên", "AIR",
                          (1000, 240, 160), 1, p("sil_top_kg"), "upright", "source", "slides into the mounted block from inside"))
    elif m["vents"]:
        parts.append(Part("A-SILENCER", "AIR - SILENCED VENT BOX", "Hộp tiêu âm cửa gió", "AIR", (450, 300, 120), 2,
                          p("silencer_kg"), "box", "assumption"))
    if final:
        parts.append(Part("K-SEALS", "KIT - DOOR EDGE SEALS, BASE SEAL, CABLE GROMMETS", "Gioăng cửa, gioăng đế", "BASE", (600, 300, 100), 1,
                          p("door_edge_seal_kg") + p("base_seal_kg") + p("grommet_kg"), "box", "source"))
        parts.append(Part("F-DECOR-FILL", "FRONT - PET FILL PIECES FOR THE DECOR BLOCKS (loose)", "Bông PET khối trang trí", "FRONT",
                          (1200, 400, 300), 1, decor_fill_kg(), "box", "calculation",
                          "ships loose: inside the right decor block it would make that block over 20 kg"))
    elec = 3 * p("plate_kg") + 2 * p("light_kg") + p("harness_kg")
    if m["sensor"]:
        elec += p("sensor_kg")
    parts.append(Part("E-KIT", "ELECTRICAL - SWITCHES, LIGHTS, HARNESS", "Bộ điện: công tắc, đèn, dây", "ELECTRICAL",
                      (600, 400, 200), 1, elec, "box", "assumption"))
    if m["voice"]:
        parts.append(Part("E-VOICE-RESERVE", "ELECTRICAL - VOICE COCKPIT KIT RESERVE (later)", "Dự phòng bộ voice cockpit",
                          "ELECTRICAL", (0, 0, 0), 1, p("voice_kit_kg"), "none", "assumption",
                          "weight held in the budget only; the kit ships later"))
    if m["table"]:
        parts.append(Part("I-TABLE", "INTERIOR - TABLE (v1), FLAT-PACKED", "Bàn", "INTERIOR", (1000, 600, 120), 1, table_kg(),
                          "upright", note="v1 BOM table: top, leg and base packed flat; removed in the light build"))
    return parts


# ---------------------------------------------------------------- joints
def rows_of(split):
    """Panel rows in (side wall, back wall)."""
    return {"bands": (5, 5), "tallback": (2, 1), "rows3": (3, 3)}.get(split, (2, 2))


def bolts_on(length_mm):
    """Bolt count along one joint edge. Count estimate only: the joint register sets the real pitch."""
    return max(2, math.ceil(length_mm / p("bolt_pitch")))


def joints(split, m, split_long):
    """Joint list: (joint id, description, edges, bolts, access, step). Lengths in mm."""
    g = geom()
    J = []
    side_rows, back_rows = rows_of(split)
    sh, bh = g["wall_h"] / side_rows, g["back_h"] / back_rows
    J.append(("J-WALL-01", "side wall: panel to panel, horizontal seam", 2 * (side_rows - 1), bolts_on(g["depth"])))
    J.append(("J-WALL-02", "back wall: panel to panel, horizontal seam", 2 * (back_rows - 1), bolts_on(g["inner_w"] / 2)))
    J.append(("J-WALL-03", "back wall: left half to right half, vertical seam", back_rows, bolts_on(bh)))
    J.append(("J-WALL-04", "side wall to back wall, corner", 2 * back_rows, bolts_on(bh)))
    J.append(("J-BASE-01", "walls to base band", 2 + 2, None))   # filled below
    J[-1] = ("J-BASE-01", "walls to base band", 4, 2 * bolts_on(g["depth"]) // 2 + 0)
    J.append(("J-CEIL-01", "ceiling halves to walls (side and back edges)", 4, None))
    J[-1] = ("J-CEIL-01", "ceiling halves to walls (side and back edges)", 4, 0)
    J.append(("J-CEIL-02", "ceiling half to ceiling half", 1, bolts_on(g["depth"])))
    J.append(("J-FRONT-01", "decor blocks to walls, ceiling and base", 3, 0))
    J.append(("J-FRONT-02", "door hinges and fixed-glass profiles", 1, 3 * 2 + 4))
    J.append(("J-AIR-01", "fans into ceiling halves", 2, 2))
    if m["floor"] == "raised":
        J.append(("J-BASE-02", "raised frame corners and joists", 4 + 4, 4))
    else:
        corners = 4 + (2 if True else 0)
        J.append(("J-BASE-02", "base band corner keys and front joints", corners, 2))
        if split_long:
            J.append(("J-BASE-03", "base band splices", 1, 4))
    if split_long:
        J.append(("J-FRONT-03", "decor half to decor half", 3, 4))
    # fix the edge-based counts
    out = []
    for jid, desc, edges, per_edge in J:
        if jid == "J-BASE-01":
            bolts = 2 * bolts_on(g["depth"]) + 2 * bolts_on(g["inner_w"] / 2)
            out.append((jid, desc, 4, bolts))
        elif jid == "J-CEIL-01":
            bolts = 2 * (bolts_on(g["depth"]) + bolts_on(g["inner_w"] / 2))
            out.append((jid, desc, 4, bolts))
        elif jid == "J-FRONT-01":
            out.append((jid, desc, 3, 6 + 6 + 6))    # 6 per block: 4 to the wall or ceiling, 2 to base or block
        else:
            out.append((jid, desc, edges, edges * per_edge))
    return out


def gasket_length_m(split):
    """Gasket on every panel joint (seal before mass), m."""
    g = geom()
    side_rows, back_rows = rows_of(split)
    L = 2 * (side_rows - 1) * g["depth"] + 2 * (back_rows - 1) * g["inner_w"] / 2 + g["back_h"]   # in-wall seams
    L += 2 * g["back_h"] + 2 * g["depth"] + g["inner_w"]                                       # corners, base
    L += 2 * g["depth"] + g["inner_w"] + g["depth"]                                            # ceiling edges and seam
    L += 2 * g["wall_h"] + 1697                                                                # decor to walls/ceiling
    return L * 1e-3


def connectors(split):
    """Cable connectors where the harness crosses a panel seam (power inlet low on the back wall, switches at
    the back wall centre, fans and lights in the ceiling). The voice cockpit route shares the same crossings."""
    back_rows = rows_of(split)[1]
    return (back_rows - 1) + 1 + 1   # back wall seams, back wall to ceiling, ceiling half to half


# ---------------------------------------------------------------- full part list
def felt_on(pid, w, h):
    """Felt area pre-fitted on one wall or ceiling panel (inner face, less the strip left loose over each joint)."""
    g = geom()
    if pid.startswith("W-SIDE"):
        w_eff = w * g["inner_d"] / g["depth"]
    elif pid.startswith("C-"):
        w, h = w, h * g["inner_d"] / g["depth"]
        w_eff = w
    else:
        w_eff = w
    return max(0.0, (w_eff - p("strip_w")) * (h - p("strip_w")) * 1e-6)


def parts_for(split, m, split_long=False):
    parts = []
    felt_area_on_panels = 0.0
    if m.get("stack") == "final":
        return final_stack_parts(split, m, split_long)
    for pid, name, vi, assy, w, h, q in wall_layout(split):
        fa = felt_on(pid, w, h)
        felt_area_on_panels += fa * q
        on_panel = m.get("prefit") and not m.get("leaf")
        t = p("wall_t_plan") + (9 if on_panel else 0)
        parts.append(Part(pid, name + (" WITH FELT" if on_panel else ""), vi, assy, (h, w, t), q,
                          panel_kg(w, h, m, fa, assy == "CEILING"), "upright"))
        if m.get("leaf"):
            # inner leaf: the sound mass and the felt as one piece clipped on from inside (keeps outside seams as planned)
            x = m.get("sound_kgm2", 0.0) if (assy != "CEILING" or m.get("ceiling_sound", True)) else 0.0
            area = w * h * 1e-6
            kg = fa * (p("pet9_kgm2") + p("felt_fix_kgm2")) + area * x + area * 0.6   # 0.6 kg/m2 clip rail, assumption
            lt = 9 + 3 + x / p("rho_mass_layer") * 1000
            parts.append(Part("L-LEAF-" + pid[2:], "LINING - INNER LEAF (sound mass + felt) FOR " + pid, "Lớp trong: khối lượng + tiêu âm",
                              "LINING", (h, w, lt), q, kg, "upright", "calculation", "clips onto the panel frame from inside"))
    if m.get("leaf"):
        pass
    elif m.get("prefit"):
        total_felt = sum(w * h * q for _, _, _, w, h, q in felt_layout()) * 1e-6
        strip = max(0.0, total_felt - felt_area_on_panels)
        parts.append(Part("L-STRIP", "LINING - LOOSE FELT STRIPS OVER JOINTS", "Dải tiêu âm che mối nối", "LINING", (1500, 300, 60), 1,
                          strip * (p("pet9_kgm2") + p("felt_fix_kgm2")), "box", "calculation",
                          "the rest of the felt is pre-fitted on the panels (weight counted in WALL and CEILING)"))
    else:
        for pid, name, vi, w, h, q in felt_layout():
            a = w * h * 1e-6
            parts.append(Part(pid, name, vi, "LINING", (h, w, 9), q, a * (p("pet9_kgm2") + p("felt_fix_kgm2")), "upright"))
    parts += base_parts(m, split_long)
    parts += front_parts(m, split_long)
    parts += service_parts(m)
    nb, nc = fastener_counts(split, m, split_long)
    fixings = nb * p("bolt_kg") + nc * p("cam_kg")
    if m["seals"]:
        fixings += gasket_length_m(split) * p("gasket_kgm")
    parts.append(Part("K-FIX", "KIT - M6 BOLTS, RIVNUTS" + (", CAM CONNECTORS" if nc else "") + (", JOINT GASKETS" if m["seals"] else ""),
                      "Bộ bu lông M6, gioăng", "WALL", (400, 300, 150), 1, fixings, "box", "calculation",
                      f"{nb} M6 bolts" + (f", {nc} cam or clip connectors" if nc else "")))
    return parts


def fastener_counts(split, m, split_long=False):
    """(M6 bolts, cam or clip connectors) on site."""
    J = joints(split, m, split_long)
    cams = sum(j[3] for j in J if m.get("cams") and j[0] in CAM_JOINTS)
    return sum(j[3] for j in J) - cams, cams


def by_assembly(parts):
    d = OrderedDict((a, 0.0) for a in ASSEMBLIES)
    for pt in parts:
        d[pt.assy] += pt.total
    return d


def total(parts):
    return sum(pt.total for pt in parts)


# ---------------------------------------------------------------- final wall stack (sound study, DECIDED)
FINAL = dict(FAST, key="final", label="Spaceship decided build: light build, fast assembly, sound walls, 4+4 laminated front",
             front="lam44", stack="final", leaf=True, fill=True)


def final_outer_kg(w, h, depth, m, with_fill=True):
    """Outer panel: ACP 3 mm bonded to a 20 x depth aluminium frame at 400 mm, cavity filled with PET."""
    area = w * h * 1e-6
    frame = frame_length_mm(w, h, p("stud_pitch_acp")) * 1e-3 * al_rhs(20, depth, p("t_al_final"))
    fill = depth * 1e-3 * p("fill_pet_kgm3") if with_fill else 0.0
    return area * (p("acp3_kgm2") + p("bond_kgm2") + fill) + frame


def final_leaf_kg(w, h, fill_depth=0.0):
    """Lining cassette (inner leaf): 0.5 mm steel tray 25 mm deep with 9 mm felt across its face, on clips.
    fill_depth > 0: the cavity fill rides on the back of the cassette (used for the ceiling, see report)."""
    area = w * h * 1e-6
    tray = (area + 2 * (w + h) * 1e-3 * p("tray_depth") * 1e-3) * p("tray_t") * 1e-3 * p("rho_steel")
    return tray + area * (p("pet9_kgm2") + p("felt_fix_kgm2") + p("leaf_clip_kgm2") + fill_depth * 1e-3 * p("fill_pet_kgm3"))


def final_stack_parts(split, m, split_long=False):
    """Parts of the final stack: outer panels and their cassettes ship separately; the rest as the fast build."""
    with_t = dict(wall_t_plan=p("final_wall_t"), ceil_t=p("final_ceil_t"))
    from inputs import override
    with override(**with_t):
        g = geom()
        parts = []
        for pid, name, vi, assy, w, h, q in wall_layout(split):
            depth = p("final_ceil_depth") if assy == "CEILING" else p("final_wall_depth")
            fill_on_cassette = assy == "CEILING" and m.get("ceil_fill_on_cassette", True)
            parts.append(Part(pid, name + (" (outer: ACP + frame)" if fill_on_cassette else " (outer: ACP + frame + fill)"), vi, assy,
                              (h, w, 3 + depth), q, final_outer_kg(w, h, depth, m, not fill_on_cassette), "upright"))
            if assy == "CEILING":
                lw, lh = w, g["inner_d"]
            elif pid.startswith("W-SIDE"):
                lw, lh = g["inner_d"], h
            else:
                lw, lh = w, h
            fd = depth if fill_on_cassette else 0.0
            parts.append(Part("L-CASS-" + pid[2:], "LINING - CASSETTE FOR " + pid + (" (steel tray + felt + ceiling fill)" if fd else " (steel tray + felt)"),
                              "Khay lót trong + tiêu âm", "LINING", (lh, lw, p("tray_depth") + 9 + fd), q, final_leaf_kg(lw, lh, fd),
                              "upright", "calculation", "floating inner leaf, clips on from inside"))
        parts += base_parts(m, split_long)
        parts += front_parts(m, split_long)
        parts += service_parts(m)
        nb, nc = fastener_counts(split, m, split_long)
        fixings = nb * p("bolt_kg") + nc * p("cam_kg") + gasket_length_m(split) * p("gasket_kgm")
        parts.append(Part("K-FIX", "KIT - M6 BOLTS, RIVNUTS, CAM CONNECTORS, JOINT GASKETS", "Bộ bu lông M6, gioăng", "WALL",
                          (400, 300, 150), 1, fixings, "box", "calculation", f"{nb} M6 bolts, {nc} cam or clip connectors"))
        return parts


def decor_fill_kg():
    """PET fill lining the decor blocks: area x 75 mm x fill density."""
    return p("decor_fill_m2") * 0.075 * p("fill_pet_kgm3")
