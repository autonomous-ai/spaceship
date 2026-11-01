"""Heat inside the power unit 711001: a steady heat balance of the closed box, for #319's heat point and the PM's
conditions of 2026-11-01 (the worst case keeps every device under its own rating, with a margin).

    python3 v2/05-Engineering/electrical/unit_heat.py          # print the section calc-results carries

The model has four nodes: the supplies' cases S (lumped), the folded shell B (1.0 mm aluminium), the inside air A and
the front plate P (1.5 mm aluminium, black anodised). Heat leaves by four paths:
  - the plate's outer face to the pod air: natural convection on a vertical plate and radiation;
  - the vent slots in the plate: stack flow through every row at its own height (orifice law, Cd 0.6), the inside
    air taken as well mixed;
  - the shell to the room: across the gap behind the box to the outer skin, and through the side flanges and B2's
    steel members into the skin (both into the room air, behind the pod's back wall);
  - small paths through the cavity fill around the shell.
The supplies sit flat on the shell's back wall (README section 3), so most of their heat goes into the shell by
contact. The shell-to-room path carries most of the heat and is the least certain number here, so the worst case
takes it at half its value (an assumption that covers a fill-packed gap and poor flange contact).

Every input carries its status (conventions section 9). Geometry comes from the CAD parameters (711001, 711002),
loads from the load table and the PM's rulings, losses from the supplies' own sheets.
"""

import math
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAD = os.path.join(REPO, "v2", "01-CAD-Native", "electrical")

SIGMA = 5.67e-8                 # W/(m2 K4), Stefan-Boltzmann (source: standard value)
RHO_AIR, CP_AIR = 1.10, 1007.0  # kg/m3, J/(kg K): air near 45 °C (source: standard values)
CD = 0.6                        # orifice discharge coefficient of a punched slot (source: standard value)
K_AIR = 0.026                   # W/(m K), still air (source: standard value)

# ---- the case (statuses in the notes)
ROOM_C = 28.0       # assumption: a warm US office (ASHRAE 55's summer comfort band tops out near 27-28 °C)
POD_OVER_ROOM = 4.0  # DECIDED: the pod holds at most 4 K over the room (D-50)
KIT_AVG_W = 40.0    # DECIDED: the voice kit's average (D-88), the PM's case for this check
LIGHTS_W = 22.0     # DECIDED: the hub holds the three light channels at about 22 W (PM ruling 2026-11-01)
FANS_HUB_W = 19.2   # calculation: four fans at the 65 l/s boost (supply pair 73 % and exhaust pair 65 % speed at
                    # 53 l/s, x 65/53, cube law on the 6.6 W maker figure each) 16.1 W + hub 3 W + sensor 0.05 W
OUTLET_A = 12.0     # calculation: the user outlets at 80 % of the 15 A breaker, the most a circuit carries steady
SHELL_PATH_WORST = 0.5  # assumption: the shell-to-room path at half its estimate in the worst case

# ---- supplies' losses at part load and 115 V (the Lead, 2026-11-01: part-load 120 V efficiencies)
# Mean Well's CLG-100 sheet draws efficiency against load at 115 V (its 48 V model; the 24 V model has the same
# 88.5 % at full load): read from the curve, source. The LPV-60 sheet gives one figure per model (83 % at 12 V, 86 % at
# 24 V, at 230 V and full load) and no curve: its part-load figures take the CLG-100's 115 V curve shape, scaled to the
# LPV-60's full-load figure less one point for 115 V (assumption, to measure on the prototype). Below 10 % load the
# loss stays at its 10 % value (assumption).
CLG_115 = ((0.10, 0.690), (0.20, 0.785), (0.30, 0.825), (0.40, 0.840), (0.50, 0.855), (0.60, 0.867), (0.70, 0.875),
           (0.80, 0.880), (0.90, 0.883), (1.00, 0.885))
FULL_115 = {"ps_kit": (0.885, "source: Mean Well CLG-100 sheet, its 115 V curve (48 V model; the 24 V has the same 88.5 %)"),
            "ps_cv24": (0.85, "assumption: LPV-60-24's 86 % (sheet, 230 V) less one point at 115 V, on the CLG-100's curve shape"),
            "ps_cv": (0.82, "assumption: LPV-60-12's 83 % (sheet, 230 V) less one point at 115 V, on the CLG-100's curve shape")}
MODEL = {"ps_kit": "CLG-100-24", "ps_cv24": "LPV-60-24", "ps_cv": "LPV-60-12"}


def eff_115(key, frac):
    """A supply's efficiency at 115 V and a load fraction of its rating."""
    x = min(max(frac, CLG_115[0][0]), 1.0)
    for (x0, e0), (x1, e1) in zip(CLG_115, CLG_115[1:]):
        if x <= x1:
            shape = e0 + (e1 - e0) * (x - x0) / (x1 - x0)
            break
    return FULL_115[key][0] * shape / CLG_115[-1][1]


def supply_loss_115(key, rated, p_out):
    """W lost in a supply at p_out (at least the loss at 10 % load)."""
    p = max(p_out, 0.10 * rated)
    eta = eff_115(key, p / rated)
    return p / eta - p


# ---- other heat inside the box (outlet terms scale with the outlets' current squared)
CTRL_W = 2.0        # assumption: the light controller's own draw (LTECH gives none for the LT-995) at the 22 W light load
BREAKER_W_15 = 2.0  # source: Eaton FAZ-NA-L catalog, 2 W per pole at 15 A (C15)
GFCI_W_12 = 1.5     # assumption: the GFCI receptacle's contacts and sensing at 12 A
WIRE_OHM = 0.8 * 0.0096   # calculation: 0.8 m of 14 AWG (L and N to the receptacle) at 9.6 mΩ/m (60 °C)
FUSE_OHM = 0.01785  # source: Littelfuse ATOF 5 A, typical cold resistance 17.85 mΩ (F1, F2)
OUTLET_TYP_A = 3.0  # assumption: laptops, a monitor and chargers, about 360 W, the most a work pod draws for hours


def other_heat(outlet_a, fuse_amps):
    """{name: W} of the heat inside the box besides the supplies."""
    return {"light controller": CTRL_W,
            "breaker": BREAKER_W_15 * (outlet_a / 15.0) ** 2,
            "GFCI receptacle": GFCI_W_12 * (outlet_a / 12.0) ** 2,
            "mains wiring to the receptacle": WIRE_OHM * outlet_a ** 2,
            "fuses F1, F2": sum(FUSE_OHM * a ** 2 for a in fuse_amps)}

# ---- the thermal network's coefficients
H_CONV_IN = 2.5     # W/(m2 K), natural convection inside a small closed box (assumption; textbook range 2-4)
H_CONV_CASE = 3.5   # W/(m2 K), the supplies' cases to the inside air (assumption)
EPS = {"case": 0.9, "plate": 0.8, "shell": 0.07, "skin": 0.9}   # emissivities: plastic, anodised, mill finish, painted
CONTACT_W_K = 1.0   # W/K, the supply stack's back face on the shell (assumption: a 0.3 mm mean air film on part of it)
GAP_BACK_M = 0.009  # m, the shell's back to the skin: 6 mm to the frame's skin side + the 3 mm bond line (route model)
SKIN_AREA_M2 = 0.15  # m2, the skin area the heat spreads over behind the box (assumption: about twice the box's back)
H_SKIN_OUT = 9.0    # W/(m2 K), the skin's outer face to the room: convection 3.5 + radiation 5.5 (assumption)
FLANGE_W_K = 1.0    # W/K, each pair of side flanges into B2's members (assumption)
STUD_W_K = 0.6      # W/K, the two members into the skin (calculation: a steel fin bonded to the skin, 45 mm reach)
FILL_W_K = 0.05     # W/K, through the cavity fill around the top and bottom (assumption)


def _cad():
    """electrical_parts_cad.py without Fusion: stub the adsk names it reads at import."""
    if CAD not in sys.path:
        sys.path.insert(0, CAD)
    if "adsk" not in sys.modules:
        adsk = types.ModuleType("adsk")
        core, fusion = types.ModuleType("adsk.core"), types.ModuleType("adsk.fusion")
        fusion.DimensionOrientations = types.SimpleNamespace(HorizontalDimensionOrientation=0,
                                                             VerticalDimensionOrientation=1)
        adsk.core, adsk.fusion = core, fusion
        sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.fusion": fusion})
    import electrical_parts_cad as C
    return C


def part_params(key):
    C = _cad()
    vals = {}
    for n, expr, _unit, _st, _src in C.PARTS[key][4]:
        vals[n] = C.M.evaluate(expr, dict(vals))
    return vals


def geometry():
    """Box and plate sizes (m) and the vent rows [(height above the box's bottom m, open area m2)] from the CAD."""
    b, f = part_params("body"), part_params("front")
    n_rows = int(f["vent_rows"])
    zs = [f["vent_zb"] + r * f["vent_rp"] for r in range(n_rows)] + [f["vent_zt"] - r * f["vent_rp"] for r in range(n_rows)]
    rows = [((z - f["edge_off"]) / 1000.0, f["vent_n"] * f["vent_l"] * f["vent_w"] / 1e6) for z in zs]
    return {"w": b["w"] / 1000.0, "h": b["h"] / 1000.0, "d": b["d"] / 1000.0, "lip": b["lip"] / 1000.0,
            "plate_w": f["w"] / 1000.0, "plate_h": f["h"] / 1000.0, "rows": rows}


def vent_flow(rows, t_in, t_out):
    """Outflow (m3/s) through vent rows at their heights, driven by the stack: the inside pressure at the floor
    (p0) is found so the mass in equals the mass out."""
    g = 9.81
    r_out, r_in = 353.0 / (t_out + 273.15), 353.0 / (t_in + 273.15)

    def net(p0):
        s = 0.0
        for z, a in rows:
            dp = p0 + (r_out - r_in) * g * z
            rho = r_in if dp > 0 else r_out
            s += math.copysign(rho * CD * a * math.sqrt(2 * abs(dp) / rho), dp)
        return s
    lo, hi = -5.0, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if net(mid) > 0 else (mid, hi)
    p0 = (lo + hi) / 2
    return sum(CD * a * math.sqrt(2 * (p0 + (r_out - r_in) * g * z) / r_in)
               for z, a in rows if p0 + (r_out - r_in) * g * z > 0)


def case_supplies(EP):
    """[(id, part key, rated W, output V, load W in the heat case, feeds)]: the kit at its average split over its
    feeds, the lights at the hub's budget, the fans at the boost and the hub."""
    kit = [x for x in EP.SUPPLIES if "voice" in x[5]]
    out = []
    for sid, key, outv, rated, _a, feeds, _why in EP.SUPPLIES:
        if "voice" in feeds:
            load = KIT_AVG_W / len(kit)
        elif "lights" in feeds:
            load = LIGHTS_W
        else:
            load = FANS_HUB_W
        out.append((sid, key, rated, float(outv.split()[0]), load, feeds))
    return out


# ---- the devices in the box and their own limits (sources: the makers' sheets, read 2026-11-01)
LPV_KNEE = (45.0, 70.0, 0.60)    # source: Mean Well LPV-60 derating at 115 V: full load to 45 °C, 60 % at 70 °C
CLG_KNEE = (50.0, 70.0, 0.60)    # source: Mean Well CLG-100: full load to 50 °C, 60 % at 70 °C
DEVICES = (   # name, limit °C, source
    ("light controller LTECH LT-995", 65.0, "LTECH LT-995 sheet: -30 to +65 °C"),
    ("GFCI receptacle P&S 1597TRW", 66.0, "Legrand CS3339: -35 to +66 °C"),
    ("Mean Well supplies, the units themselves", 70.0, "LPV-60 and CLG-100 sheets: -30 to +70 °C, by their derating curves"),
    ("LAN keystone jacks Panduit NK688MWH", 75.0, "Panduit COSP588: -10 to +75 °C"),
    ("Cat6 cable Belden 3612", 75.0, "Belden 3612 sheet: 75 °C"),
    ("12 and 24 V leads in the unit: Belden 5302UE and 5304UE (CMR), Southwire 94664 (CL3)", 75.0,
     "Belden's sheets and Southwire spec 13090: 75 °C"),
    ("hub link Belden 9536 in the unit", 80.0, "Belden 9536 sheet: 80 °C as UL AWM 2464, the rating for wiring inside equipment"),
    ("lever connectors WAGO 221-415", 85.0, "WAGO: T85, surrounding air 85 °C at most"),
    ("fuse holders Littelfuse FHAC0001ZXJ", 105.0, "Littelfuse OL-FHAC0001ZXJ: 105 °C"),
    ("bushings Heyco 2836N", 105.0, "Heyco: -18 to +105 °C"),
    ("mains wire Alpha Wire 461419 (UL 1015)", 105.0, "Alpha Wire: UL 1015 AWM 105 °C"),
)
STRAT_K = 3.0       # assumption: the box's upper air above the mixed mean (no fan inside)


def derated(knee, t):
    """Fraction of rated load a supply may carry at air temperature t (its maker's straight-line derating)."""
    t0, t1, f1 = knee
    if t <= t0:
        return 1.0
    return max(f1, 1.0 - (1.0 - f1) * (t - t0) / (t1 - t0))


CASE_SIZE = {"ps_cv": (0.1625, 0.0425, 0.032), "ps_cv24": (0.1625, 0.0425, 0.032),   # source: the sheets, L x W x H
             "ps_kit": (0.2222, 0.068, 0.0388)}


def stack_areas(keys):
    """(area on the shell's back wall, area open to the air) of the supplies lying flat on the back wall, m2."""
    back = sum(CASE_SIZE[k][0] * CASE_SIZE[k][1] for k in keys)
    open_ = back + sum(2 * (CASE_SIZE[k][0] + CASE_SIZE[k][1]) * CASE_SIZE[k][2] for k in keys)
    return back, open_


def solve(p_supplies, p_air, geo, t_pod, t_room, shell_k=1.0, stack=None):
    """Steady node temperatures (°C) and the heat on each path (W)."""
    import numpy as np
    w, h, d = geo["w"], geo["h"], geo["d"]
    a_stack_back, a_stack = stack or stack_areas(["ps_cv"] * 4)
    a_shell_in = w * h - a_stack_back + 2 * h * d + 2 * w * d
    a_plate_in = (w - 2 * geo["lip"]) * (h - 2 * geo["lip"])
    a_plate_out = geo["plate_w"] * geo["plate_h"]
    t = t_pod + 15.0
    for _ in range(80):
        tk = t + 273.15
        hr = 4 * SIGMA * tk ** 3
        g_sa = a_stack * H_CONV_CASE
        g_sp = a_stack_back * 0.8 * hr / (1 / EPS["case"] + 1 / EPS["plate"] - 1)
        g_ba = a_shell_in * H_CONV_IN
        g_ap = a_plate_in * H_CONV_IN
        h_po = 1.42 * (max(t - t_pod, 1.0) / geo["plate_h"]) ** 0.25 + EPS["plate"] * hr * 0.92
        g_ppod = a_plate_out * h_po
        g_gap = w * h * (K_AIR / GAP_BACK_M + EPS["shell"] * hr)
        g_skin = H_SKIN_OUT * SKIN_AREA_M2
        g_room = shell_k * (1 / (1 / g_gap + 1 / g_skin) + 1 / (1 / (2 * 160 * 0.001 * h / d) + 1 / FLANGE_W_K
                                                                 + 1 / STUD_W_K) + FILL_W_K)
        q = vent_flow(geo["rows"], max(t, t_pod + 0.5), t_pod)
        g_v = RHO_AIR * CP_AIR * q
        m = np.array([[CONTACT_W_K + g_sa + g_sp, -CONTACT_W_K, -g_sa, -g_sp],
                      [-CONTACT_W_K, CONTACT_W_K + g_ba + g_room, -g_ba, 0.0],
                      [-g_sa, -g_ba, g_sa + g_ba + g_ap + g_v, -g_ap],
                      [-g_sp, 0.0, -g_ap, g_sp + g_ap + g_ppod]])
        r = np.array([p_supplies, g_room * t_room, p_air + g_v * t_pod, g_ppod * t_pod])
        s, b, a, p = np.linalg.solve(m, r)
        if abs(a - t) < 0.005:
            break
        t = 0.5 * (t + a)
    return {"case": s, "shell": b, "air": a, "plate": p, "vent_ls": q * 1000,
            "q_vent": g_v * (a - t_pod), "q_plate": g_ppod * (p - t_pod), "q_room": g_room * (b - t_room)}


OLD_ROWS = [(0.025, 800e-6), (0.120, 800e-6)]   # the plate before this check: 2 rows of 5 slots 40 x 4 (main, #353)


def results(EP, outlet_a, shell_k, rows=None):
    """One case: (inside air °C, supply losses W, other heat W, the solve's dict)."""
    geo = geometry()
    if rows is not None:
        geo = dict(geo, rows=rows)
    sup = case_supplies(EP)
    losses = sum(supply_loss_115(k, r, w) for _s, k, r, _v, w, _f in sup)
    fuses = [w / v for _s, _k, _r, v, w, f in sup if "voice" in f or "lights" in f]
    other = sum(other_heat(outlet_a, fuses).values())
    r = solve(losses, other, geo, ROOM_C + POD_OVER_ROOM, ROOM_C, shell_k, stack_areas([x[1] for x in sup]))
    return r["air"], losses, other, r


def section_md(EP):
    """calc-results' section 6: the heat inside the power unit, its worst case, and each device against its limit."""
    L = []
    A = L.append
    sup = case_supplies(EP)
    A("## 6. Heat inside the power unit (711001)")
    A("")
    A("The supplies, the breaker, the GFCI receptacle and the light controller share the closed box; its air sets each "
      "part's temperature. A steady heat balance (`unit_heat.py`): the supplies sit flat on the shell's back wall; heat "
      "leaves through the front plate to the pod, through the vent slots by stack flow, and through the shell into "
      "B2's skin and members to the room. The last path carries most of it and is the least certain, so the worst case "
      "takes it at half (assumption). Case: room %.0f °C (assumption: a warm office), the pod %.0f K over it (D-50); "
      "the voice kit at its %.0f W average (D-88), the lights at the hub's %.0f W (PM ruling), the fans at the 65 l/s "
      "boost with the hub, %.1f W (calculation)." % (ROOM_C, POD_OVER_ROOM, KIT_AVG_W, LIGHTS_W, FANS_HUB_W))
    A("")
    A("| Supply | Model | Load W | Efficiency at 115 V | Loss W | Basis |")
    A("|---|---|---:|---:|---:|---|")
    for sid, key, rated, _v, w, _f in sup:
        A("| %s | %s | %.1f | %.1f %% | %.1f | %s |" % (sid, MODEL[key], w, 100 * eff_115(key, max(w, 0.1 * rated) / rated),
                                                     supply_loss_115(key, rated, w), FULL_115[key][1]))
    fuses = [w / v for _s, _k, _r, v, w, f in sup if "voice" in f or "lights" in f]
    A("")
    A("Other heat in the box: the light controller %.1f W (assumption), the breaker %.1f W per pole at 15 A (Eaton), "
      "the GFCI receptacle about %.1f W at 12 A (assumption), the receptacle's mains wiring and the fuses (calculation); "
      "with the user outlets at %.0f A (laptops, a monitor, chargers: assumption) that is %.1f W, at their 12 A "
      "continuous limit %.1f W." % (CTRL_W, BREAKER_W_15, GFCI_W_12, OUTLET_TYP_A,
                                     sum(other_heat(OUTLET_TYP_A, fuses).values()), sum(other_heat(12.0, fuses).values())))
    A("")
    A("| Inside air, °C | the plate before (2 rows of 5 slots) | this plate (8 rows of 3 slots, right side) |")
    A("|---|---:|---:|")
    cases = (("outlets at %.0f A, shell path as estimated" % OUTLET_TYP_A, OUTLET_TYP_A, 1.0),
             ("outlets at %.0f A, shell path at half" % OUTLET_TYP_A, OUTLET_TYP_A, SHELL_PATH_WORST),
             ("**worst:** outlets at 12 A, shell path at half", 12.0, SHELL_PATH_WORST))
    for label, amps, k in cases:
        A("| %s | %.1f | %.1f |" % (label, results(EP, amps, k, OLD_ROWS)[0], results(EP, amps, k)[0]))
    worst = results(EP, 12.0, SHELL_PATH_WORST)[0]
    t_dev = worst + STRAT_K
    A("")
    A("**Worst case, each part against its own limit:** the box's air at %.1f °C, %.0f K more for the upper part (no "
      "fan inside, assumption): **%.1f °C**." % (worst, STRAT_K, t_dev))
    A("")
    A("| Part | Its limit | Margin at %.0f °C |" % t_dev)
    A("|---|---|---:|")
    for name, lim, src in DEVICES:
        A("| %s | %.0f °C (%s) | %.0f K |" % (name, lim, src, lim - t_dev))
    for sid, key, rated, _v, _w, feeds in sup:
        loads = [q * wm for (_i, _n, s_, _f, q, wm, _t, _st, _src, _no) in EP.LOADS if s_ == sid]
        peak = (EP.KIT_PEAK_W / len([x for x in sup if "voice" in x[5]])) if "voice" in feeds else sum(loads)
        frac = derated(CLG_KNEE if key == "ps_kit" else LPV_KNEE, t_dev)
        A("| %s %s at its peak load, %.1f W | %.0f W at %.0f °C (%.0f %% of %.0f W, its maker's derating) | %.0f W |" % (
            sid, MODEL[key], peak, frac * rated, t_dev, 100 * frac, rated, frac * rated - peak))
    A("")
    A("Room temperature (the case above takes %.0f °C, a warm office): with the same worst loads, each room gives "
      "these upper-air temperatures and the tightest part's margin:" % ROOM_C)
    A("")
    A("| Room | Upper air | Tightest part | Its margin |")
    A("|---:|---:|---|---:|")
    room0 = globals()["ROOM_C"]
    try:
        for room in (28.0, 30.0, 32.0):
            globals()["ROOM_C"] = room
            t = results(EP, 12.0, SHELL_PATH_WORST)[0] + STRAT_K
            name, lim, _src = min(DEVICES, key=lambda d: d[1] - t)
            A("| %.0f °C | %.1f °C | %s (%.0f °C) | %.0f K |" % (room, t, name, lim, lim - t))
    finally:
        globals()["ROOM_C"] = room0
    A("")
    A("The breaker is calibrated at 40 °C and carries 0.5 %% less per K above (Eaton): %.1f A at %.0f °C, over the "
      "outlets' 12 A continuous limit. These figures are a calculation; the prototype's test measures the box's air "
      "with the kit at 40 W (a dummy load) and the outlets loaded." % (15.0 * (1 - 0.005 * max(0.0, t_dev - 40.0)), t_dev))
    A("")
    return "\n".join(L)


if __name__ == "__main__":
    sys.path.insert(0, CAD)
    import electrical_parts as EP
    print(section_md(EP))
    geo = geometry()
    print("box %.0f x %.0f x %.0f mm, plate %.0f x %.0f, vent rows (z mm, mm2): %s" % (
        geo["w"] * 1e3, geo["h"] * 1e3, geo["d"] * 1e3, geo["plate_w"] * 1e3, geo["plate_h"] * 1e3,
        [(round(z * 1e3), round(a * 1e6)) for z, a in geo["rows"]]))
