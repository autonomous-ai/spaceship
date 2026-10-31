#!/usr/bin/env python3
"""Spaceship (FocusPod v2) - sound and fresh-air check.

Every result printed here is a CALCULATION, not a test. Each input carries its
status (source / calculation / assumption / unverified) next to it, and the
source keys point at SRC below or at the bought-part table
v2/05-Engineering/hardware/selection.md ("HW").

Usage
  python3 calc.py            print every table used in report.md
  python3 calc.py --verify   rebuild the tables and confirm report.md quotes
                             each one exactly (exit 1 if any differs)

Pure Python 3 standard library. Units: mm, m, kg, Pa, Hz, dB, l/s, W.

Models (reasoning in report.md)
  Single leaf   Sharp (1978): field-incidence mass law below fc/2, damped
                coincidence above fc (loss factor = material + radiation),
                straight line on log f between.
  Sandwich      faces + core; coincidence from the bending/shear dispersion
                (stiff honeycomb core keeps a low fc; a soft foam core has none
                but gets a dilatational dip).
  Double leaf   Sharp (1978): mass-air-mass f0 with the 1.8 factor,
                R1+R2+20lg(fd)-29 up to fl = c/(2 pi d), R1+R2+6 above,
                -8 dB if the cavity is not filled; studs (line or point)
                cap it. Stud term = energy mean of both leaf orders.
  Octaves       each octave 125-4000 Hz = energy mean of its 1/3 octaves.
  Pod           diffuse field inside: IL = 10lg(1 + A_in / sum(S tau)),
                then ISO 23351-1 style D_S,A on a standard speech spectrum.
  Leaks         open area with tau = 1; seals/gaskets as 10 mm strips with
                their own sound reduction.
  Silencer      lined plenum, Sabine 1.05 a^1.4 P/S dB per metre, derated,
                capped by casing flanking.
  Air           well-mixed CO2 and heat balance; EC fan on a square-law
                system curve, fan laws for speed, assumed fan spectrum.
"""

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
SRC = {
    "SHARP": "Sharp B.H. (1978) Prediction methods for the sound transmission of building elements, "
             "Noise Control Eng. 11(2):53-63, as set out in Bies, Hansen & Howard, Engineering Noise "
             "Control 5th ed., ch. 7 (method)",
    "ISO23351": "ISO 23351-1:2020: D_S,A is the reduction of the A-weighted sound power of standard speech, "
                "octave bands 125 Hz-8 kHz, reverberation room per ISO 3741. "
                "https://akustiikka.turkuamk.fi/en/speech-level-reduction/ (checked 2026-10-31)",
    "ISO3382": "ISO 3382-3:2012 Table 1 normal-effort speech, octave levels at 1 m, as widely reproduced; "
               "paywalled text not re-checked (unverified against the standard). Only the shape matters.",
    "IEC61672": "IEC 61672-1 A-weighting at octave centres (standard values)",
    "ETB_E": "Engineering ToolBox Young's modulus table, "
             "https://www.engineeringtoolbox.com/young-modulus-d_417.html (checked 2026-10-31)",
    "ASI_ABS": "Acoustical Surfaces absorption table, "
               "https://www.acousticalsurfaces.com/acoustic_IOI/101_13.htm (checked 2026-10-31)",
    "V1_BOM": "sources/v1/indoor-pod-v3-bom-v5-2026-10-29.xlsx",
    "V1_DWG": "sources/v1/drawings/wood-parts.pdf",
    "PLAN": "v2/00-Control/v2-build-plan.pdf and v2/PLAN.md",
    "BRIEF": "Milestone 1 brief and Lead updates of 2026-10-31",
    "HW": "v2/05-Engineering/hardware/selection.md",
    "ASSUME": "assumption made here; report.md 'Assumptions' gives the reason and the test that closes it",
}

# ---------------------------------------------------------------------------
# Bands, speech spectrum, A-weighting, air
# ---------------------------------------------------------------------------
BANDS = (125, 250, 500, 1000, 2000, 4000)
SPEECH_DB = (49.9, 54.3, 58.0, 52.0, 44.8, 38.8)   # ISO3382 (8 kHz band adds < 0.05 dB here)
A_WEIGHT = (-16.1, -8.6, -3.2, 0.0, 1.2, 1.0)      # IEC61672
C0 = 343.0       # m/s, air 20 C
RHO0 = 1.204     # kg/m3, air 20 C
CP_AIR = 1005.0  # J/(kg K)

# ---------------------------------------------------------------------------
# Materials: density kg/m3, E Pa, Poisson, internal loss factor (incl. mounting)
# ---------------------------------------------------------------------------
MAT = {
    "alu":     (2700.0, 69e9,  0.33, 0.010),   # ETB_E E; density standard; eta ASSUME
    "ldpe":    (920.0,  0.3e9, 0.40, 0.050),   # ETB_E (0.11-0.45 GPa); density, eta ASSUME
    "ply":     (600.0,  8e9,   0.30, 0.020),   # density HW plywood row; E, eta ASSUME
    "hdf":     (900.0,  4e9,   0.30, 0.020),   # ETB_E (MDF 4 GPa); density, eta ASSUME
    "steel":   (7850.0, 200e9, 0.30, 0.010),   # ETB_E; eta ASSUME
    "glass":   (2500.0, 70e9,  0.22, 0.030),   # EN 572-1 (HW glass rows); eta ASSUME (mounted)
    "pmma":    (1190.0, 3.2e9, 0.37, 0.040),   # ETB_E acrylic 3.2 GPa; density HW acrylic row; eta ASSUME
}
ACP3_KG_M2 = 3.5         # Alcorest EV3038 3 mm x 0.21 mm skins (the plan's VT01): HW VT01 row; maker publishes no
                         # kg/m2, so this is a calculation (skins 1.14 + PE core 2.32-2.42). The layout study uses
                         # 3.8 (3A DIBOND, 0.3 mm skins), which is the heavier, conservative case for weight.
ACP3_SKIN_MM = 0.21      # Alcorest catalogue, HW VT01 row (source)
PET_FELT9_KG_M2 = 1.8    # HW VT03 felt row
FILL_KG_M3 = 32.0        # Pyrotek Sorberpoly 2D polyester, 32 kg/m3: the density its ISO 354 data is for (HW fill row).
                         # 24 kg/m3 exists but has no published absorption, so the lighter fill is not used (PM rule).
TRAY_KG_M2 = 0.26        # calculation: 25 mm steel tray returns, 4.6 m edge per 1.72 m2 x 0.025 m x 3.93 kg/m2
HC_CORE_KG_M3 = 60.0     # ASSUME: aluminium honeycomb core density (HW sandwich rows give panel kg/m2)
HC_CORE_G = 150e6        # ASSUME: honeycomb core shear modulus, low end of typical aluminium honeycomb
FOAM_CORE_KG_M3 = 40.0   # ASSUME: rigid PU foam core
FOAM_CORE_G = 3e6        # ASSUME: shear modulus of 40 kg/m3 rigid PU foam
FOAM_CORE_E = 4e6        # ASSUME: through-thickness modulus of the same foam

# ---------------------------------------------------------------------------
# Leaves
# ---------------------------------------------------------------------------
def layer(mat, t_mm):
    return (mat, t_mm)


def lam(layers):
    """Mass kg/m2, bending stiffness N m, stiffness-weighted loss factor of bonded layers."""
    z, rows = 0.0, []
    for mat, t_mm in layers:
        rho, e, nu, eta = MAT[mat]
        h = t_mm / 1000.0
        rows.append((rho * h, e / (1 - nu * nu), h, z + h / 2, eta))
        z += h
    m = sum(r[0] for r in rows)
    ea = sum(r[1] * r[2] for r in rows)
    zn = sum(r[1] * r[2] * r[3] for r in rows) / ea
    bs = [r[1] * (r[2] ** 3 / 12 + r[2] * (r[3] - zn) ** 2) for r in rows]
    b = sum(bs)
    return m, b, sum(bi * r[4] for bi, r in zip(bs, rows)) / b


def f_crit(m, b):
    return C0 ** 2 / (2 * math.pi) * math.sqrt(m / b)


class Leaf:
    """m kg/m2, fc Hz (inf = no coincidence), eta, optional dilatational dip fd Hz."""

    def __init__(self, name, m, fc, eta, fd=None):
        self.name, self.m, self.fc, self.eta, self.fd = name, m, fc, eta, fd


def plate(name, layers, kg_m2=None):
    m, b, eta = lam(layers)
    m = kg_m2 if kg_m2 is not None else m
    return Leaf(name, m, f_crit(m, b), eta)


def acp(extra=(), name="ACP 3"):
    skins = [layer("alu", ACP3_SKIN_MM), layer("ldpe", 3 - 2 * ACP3_SKIN_MM), layer("alu", ACP3_SKIN_MM)]
    m_l, b, eta = lam(skins + list(extra))
    m = ACP3_KG_M2 + (m_l - lam(skins)[0])
    return Leaf(name, m, f_crit(m, b), eta)


def sandwich(name, total_mm, face_mm, core_rho, core_g, core_e=None):
    """Two aluminium faces on a core with no bending stiffness of its own."""
    rho, e, nu, eta = MAT["alu"]
    tf, tc = face_mm / 1000, (total_mm - 2 * face_mm) / 1000
    d = tc + tf
    b = 2 * e / (1 - nu * nu) * (tf ** 3 / 12 + tf * (d / 2) ** 2)
    m = 2 * rho * tf + core_rho * tc
    s = core_g * d * d / tc                       # shear stiffness per unit width
    if s <= m * C0 ** 2:
        fc = float("inf")                         # shear waves subsonic: no coincidence
    else:
        fc = math.sqrt(m * C0 ** 4 * s / (b * (s - m * C0 ** 2))) / (2 * math.pi)
    fd = None
    if core_e:
        fd = math.sqrt(2 * core_e / (tc * rho * tf)) / (2 * math.pi)
    return Leaf(name, m, fc, eta, fd)


# ---------------------------------------------------------------------------
# Sound reduction (Sharp 1978)
# ---------------------------------------------------------------------------
SIGMA_MAX = 3.0   # ASSUME: peak radiation efficiency of a finite panel at coincidence


def eta_total(leaf, f):
    if leaf.fc == float("inf") or f < leaf.fc:
        sigma = SIGMA_MAX if leaf.fc != float("inf") and f >= leaf.fc else 0.0
    else:
        sigma = min(1 / math.sqrt(max(1e-9, 1 - leaf.fc / f)), SIGMA_MAX)
    return leaf.eta + RHO0 * C0 * sigma / (2 * math.pi * f * leaf.m)


def r_single(leaf, f):
    m, fc = leaf.m, leaf.fc

    def mass_law(x):
        return 20 * math.log10(x * m) - 47

    def damped(x):
        return 20 * math.log10(x * m) + 10 * math.log10(2 * eta_total(leaf, x) * x / (math.pi * fc)) - 47

    if fc == float("inf") or f < 0.5 * fc:
        r = mass_law(f)
    elif f >= fc:
        r = damped(f)
    else:
        r1, r2 = mass_law(0.5 * fc), damped(fc)
        r = r1 + (r2 - r1) * math.log10(f / (0.5 * fc)) / math.log10(2)
    if leaf.fd and abs(math.log2(f / leaf.fd)) <= 1 / 3 + 1e-9:
        r -= 6.0                                   # ASSUME: dilatational dip depth
    return r


EMPTY_PENALTY = 8.0   # ASSUME: unfilled cavity loses this much between f0 and the stud limit


def r_double(l1, l2, d, filled, conn, f):
    m1, m2 = l1.m, l2.m
    f0 = math.sqrt(1.8 * RHO0 * C0 ** 2 * (m1 + m2) / (d * m1 * m2)) / (2 * math.pi)
    fl = C0 / (2 * math.pi * d)
    r1, r2 = r_single(l1, f), r_single(l2, f)
    both = Leaf("both", m1 + m2, min(l1.fc, l2.fc), (l1.eta * m1 + l2.eta * m2) / (m1 + m2))
    rm = r_single(both, f)
    if f <= f0:
        return rm
    rd = r1 + r2 + 20 * math.log10(f * d) - 29 if f < fl else r1 + r2 + 6
    if not filled:
        rd = max(rm, rd - EMPTY_PENALTY)
    if conn[0] == "none":
        return rd
    taus = []
    for ma, mb, fc_rad in ((m1, m2, l2.fc), (m2, m1, l1.fc)):
        fc_rad = min(fc_rad, 20000.0)
        ratio = 20 * math.log10(ma / (ma + mb))
        if conn[0] == "line":
            dr = 10 * math.log10(conn[1] * fc_rad) + ratio - 18
        else:
            dr = 20 * math.log10(conn[1] * fc_rad) + ratio - 45
        taus.append(10 ** (-(rm + max(dr, 0.0)) / 10))
    rb = -10 * math.log10(sum(taus) / 2)
    return min(rd, rb)


PANEL_M2 = {"v1": 3.4, "v2": 1.7}   # skin panel size: v1 side wall 1496 x 2300 (V1_BOM); v2 frame ~1500 x 1145
                                     # (calculation from the plan's 2-per-side split)


def finite_gain(f, s_m2):
    """Sewell (1970) finite-panel mass law minus the field-incidence mass law used by Sharp, floored at 0:
    R = 20 lg(pi f m / rho c) - 10 lg[ln(k sqrt S) + 0.16]  vs  20 lg(f m) - 47. Raises R at 125-500 Hz
    for small panels. Source: Sewell, J. Sound Vib. 12(1) 1970; as given in Hopkins, Sound Insulation (2007)."""
    k = 2 * math.pi * f / C0
    corr = 20 * math.log10(math.pi / (RHO0 * C0)) + 47 - 10 * math.log10(max(math.log(k * math.sqrt(s_m2)) + 0.16, 1.0))
    return max(0.0, corr)


def octave(fun):
    out = []
    for fb in BANDS:
        taus = [10 ** (-fun(fb * 2 ** (k / 3)) / 10) for k in (-1, 0, 1)]
        out.append(-10 * math.log10(sum(taus) / 3))
    return out


def weights():
    w = [10 ** ((s + a) / 10) for s, a in zip(SPEECH_DB, A_WEIGHT)]
    return [x / sum(w) for x in w]


W_SPEECH = weights()


def r_speech(rb):
    return -10 * math.log10(sum(w * 10 ** (-r / 10) for w, r in zip(W_SPEECH, rb)))


class Build:
    """Build-up per m2: one leaf, or two leaves with a cavity."""

    def __init__(self, key, name, leaves, cavity=0, fill=0, conn=("none",), felt=True,
                 frame_kg_m2=0.0, thick=None, r_data=None, basis="model", extra_kg_m2=0.0, felt_gap=False):
        self.key, self.name, self.leaves = key, name, leaves
        self.cavity, self.fill, self.conn, self.felt = cavity, fill, conn, felt
        self.r_data, self.basis, self.thick = r_data, basis, thick
        self.felt_mount = "direct" if (len(leaves) == 2 and not felt_gap) else "gap"   # felt on the inner leaf, or spaced
        self.panel_m2 = PANEL_M2["v1"] if key.startswith("V1") else PANEL_M2["v2"]
        self.kg_m2 = (sum(l.m for l in leaves) + (PET_FELT9_KG_M2 if felt else 0)
                      + FILL_KG_M3 * fill / 1000 + frame_kg_m2 + extra_kg_m2)
        self._r = None

    def r(self):
        if self._r is None:
            if self.r_data is not None:
                self._r = list(self.r_data)
            elif len(self.leaves) == 1:
                lf = self.leaves[0]
                self._r = octave(lambda f: r_single(lf, f) + finite_gain(f, self.panel_m2))
            else:
                l1, l2 = self.leaves
                filled = self.fill >= 0.5 * self.cavity
                self._r = octave(lambda f: r_double(l1, l2, self.cavity / 1000, filled, self.conn, f)
                                 + finite_gain(f, self.panel_m2))
        return self._r


# ---------------------------------------------------------------------------
# Frames (kg per m2 of wall) = tube kg/m x 3.7 m of tube per m2
# (calculation: a plan-size frame ~1.5 x 1.15 m with one middle member)
# ---------------------------------------------------------------------------
TUBE_M_PER_M2 = 3.7          # older frames: v1 wood, plan steel (members ~600 mm)
TUBE_M_PER_M2_400 = 5.0      # DECIDED aluminium frames, members at 400 mm: a 1500 x 1145 panel has 5 x 1.1 m
                             # + 2 x 1.5 m = 8.5 m of tube per 1.72 m2 (calculation)
TUBE_KG_M = {
    "steel 20x20x1.0": 0.597,   # calculation (4*20-4*1)*1*7.85e-3; HW steel-tube row
    "alu 20x20x1.5": 0.300,     # calculation (4*20-4*1.5)*1.5*2.70e-3; HW aluminium-tube row
    "alu 20x40x1.5": 0.462,     # calculation; HW aluminium-tube row
    "alu 20x40x1.2": 0.373,     # calculation (2*(20+40)-4*1.2)*1.2*2.70e-3; DECIDED if the rivnut grip check passes
    "alu 25x100x1.5": 0.988,    # calculation (2*(25+100)-4*1.5)*1.5*2.70e-3; HW aluminium-tube row
    "alu 20x60x1.5": 0.624,     # calculation; HW aluminium-tube row
    "alu 20x100x1.5": 0.948,    # calculation; HW aluminium-tube row
    "wood 40x40": 0.80,         # ASSUME 500 kg/m3 timber
}


def frame(t):
    if t.startswith("alu"):
        return TUBE_KG_M[t] * TUBE_M_PER_M2_400      # all aluminium frames at the DECIDED 400 mm pitch
    return TUBE_KG_M[t] * TUBE_M_PER_M2


def walls():
    a3 = acp()
    a3p6 = acp([layer("ply", 6)], "ACP 3 + ply 6")
    al2p6 = plate("Al 2 + ply 6", [layer("alu", 2), layer("ply", 6)])
    p15 = plate("ply 15", [layer("ply", 15)])
    p9 = plate("ply 9", [layer("ply", 9)])
    p4 = plate("ply 4", [layer("ply", 4)])
    h3 = plate("HDF 3", [layer("hdf", 3)])
    s05 = plate("steel 0.5", [layer("steel", 0.5)])
    h6 = plate("2 x HDF 3", [layer("hdf", 3), layer("hdf", 3)])
    al1 = plate("aluminium 1.0", [layer("alu", 1.0)])
    hc10 = sandwich("Al honeycomb 10", 10, 0.5, HC_CORE_KG_M3, HC_CORE_G)
    hc20 = sandwich("Al honeycomb 20", 20, 0.5, HC_CORE_KG_M3, HC_CORE_G)
    fc20 = sandwich("foam core 20", 20, 0.5, FOAM_CORE_KG_M3, FOAM_CORE_G, FOAM_CORE_E)
    wd, st, al, al20 = frame("wood 40x40"), frame("steel 20x20x1.0"), frame("alu 20x40x1.5"), frame("alu 20x20x1.5")
    al100 = frame("alu 20x100x1.5")
    al60 = frame("alu 20x60x1.5")
    L = [
        Build("V1-DWG", "v1 as drawn: Al 2 + ply 6 / 40 empty, wood studs / ply 15",
              [al2p6, p15], 40, 0, ("line", 1.1), False, wd, 63),
        Build("V1-BOM", "v1 per BOM: Al 2 + ply 6 / 40 empty, wood studs / ply 9",
              [al2p6, p9], 40, 0, ("line", 1.1), False, wd, 57),
        Build("PLAN", "Plan: ACP 3 + ply 6 / 20 steel frame, empty / felt 9",
              [a3p6], felt=True, frame_kg_m2=st, thick=38),
        Build("PLAN-NOPLY", "Plan without plywood: ACP 3 / 20 / felt 9",
              [a3], felt=True, frame_kg_m2=st, thick=32),
        Build("SW-HC10", "Sandwich: ACP-faced Al honeycomb 10 / felt 9",
              [hc10], felt=True, frame_kg_m2=al20, thick=19),
        Build("SW-HC20", "Sandwich: Al honeycomb 20 / felt 9",
              [hc20], felt=True, frame_kg_m2=al20, thick=29),
        Build("SW-FOAM20", "Sandwich: Al-faced foam core 20 / felt 9",
              [fc20], felt=True, frame_kg_m2=al20, thick=29),
        Build("SW-FOAM20-DL", "Foam core 20 / 30 fill, shared studs / HDF 3 + felt 9",
              [fc20, h3], 30, 30, ("line", 0.6), True, al, 62),
        Build("DL-HDF", "ACP 3 / 40 fill, shared studs / HDF 3 + felt 9",
              [a3, h3], 40, 40, ("line", 0.6), True, al, 55),
        Build("DL-PLY4", "ACP 3 / 40 fill, shared studs / ply 4 + felt 9",
              [a3, p4], 40, 40, ("line", 0.6), True, al, 56),
        Build("DL-HDF-DEC", "ACP 3 / 40 fill / HDF 3 on resilient pads + felt 9",
              [a3, h3], 40, 40, ("point", 0.6), True, al, 58),
        Build("DL-ST", "ACP 3 / 40 fill, shared studs / steel 0.5 + felt 9",
              [a3, s05], 40, 40, ("line", 0.6), True, al, 53),
        Build("DL-ST-DEC", "ACP 3 / 40 fill / steel 0.5 on resilient pads + felt 9",
              [a3, s05], 40, 40, ("point", 0.6), True, al, 56),
        Build("DL-P6-PLY4", "ACP 3 + ply 6 / 40 fill, shared studs / ply 4 + felt 9",
              [a3p6, p4], 40, 40, ("line", 0.6), True, al, 62),
        Build("DL-HDF-60", "ACP 3 / 60 fill, shared studs / HDF 3 + felt 9",
              [a3, h3], 60, 60, ("line", 0.6), True, al60, 75),
        Build("DL-HDF-40-FL", "ACP 3 / 40 fill / HDF 3 floating (no stud bridge) + felt 9",
              [a3, h3], 40, 40, ("none",), True, al, 55),
        Build("DL-HDF-60-FL", "ACP 3 / 60 fill / HDF 3 floating + felt 9",
              [a3, h3], 60, 60, ("none",), True, al60, 75),
        Build("DL-ST-40-FL", "ACP 3 / 40 fill / steel 0.5 floating + felt 9",
              [a3, s05], 40, 40, ("none",), True, al, 53),
        Build("DL-ST-60-FL", "ACP 3 / 60 fill / steel 0.5 floating + felt 9",
              [a3, s05], 60, 60, ("none",), True, al60, 73),
        Build("DL-2HDF-60-FL", "ACP 3 / 60 fill / 2 x HDF 3 floating + felt 9",
              [a3, h6], 60, 60, ("none",), True, al60, 78),
        Build("DL-P6-HDF-60-FL", "ACP 3 + ply 6 / 60 fill / HDF 3 floating + felt 9",
              [a3p6, h3], 60, 60, ("none",), True, al60, 81),
        Build("DL-P6-P9-60-FL", "ACP 3 + ply 6 / 60 fill / ply 9 floating + felt 9",
              [a3p6, p9], 60, 60, ("none",), True, al60, 87),
        Build("DL-ST-100-FL", "ACP 3 / 100 fill / steel 0.5 floating + felt 9",
              [a3, s05], 100, 100, ("none",), True, al100, 113),
        Build("DL-AL1-60-FL", "ACP 3 / 60 fill / aluminium 1.0 floating + felt 9",
              [a3, al1], 60, 60, ("none",), True, al60, 73),
        Build("DL-AL1-100-FL", "ACP 3 / 100 fill / aluminium 1.0 floating + felt 9",
              [a3, al1], 100, 100, ("none",), True, al100, 113),
        Build("DL-ST-40-FLG", "ACP 3 / 40 fill / floating cassette: steel 0.5 tray, 25 air, felt 9",
              [a3, s05], 40, 40, ("none",), True, al, 81, extra_kg_m2=TRAY_KG_M2, felt_gap=True),
        Build("DL-ST-40-FLG-12", "ACP 3 / 20x40x1.2 frame, 40 fill / floating cassette: steel 0.5 tray, 25 air, felt 9",
              [a3, s05], 40, 40, ("none",), True, frame("alu 20x40x1.2"), 81, extra_kg_m2=TRAY_KG_M2, felt_gap=True),
        Build("DL-ST4-40-FLG-12", "ACP 3 / 20x40x1.2 frame, 40 fill / floating cassette: steel 0.4 tray, 25 air, felt 9",
              [a3, plate("steel 0.4", [layer("steel", 0.4)])], 40, 40, ("none",), True, frame("alu 20x40x1.2"), 81,
              extra_kg_m2=TRAY_KG_M2 * 0.8, felt_gap=True),
        Build("DL-ST-100-FLG", "ACP 3 / 100 fill / floating cassette: steel 0.5 tray, 25 air, felt 9",
              [a3, s05], 100, 100, ("none",), True, al100, 141, extra_kg_m2=TRAY_KG_M2, felt_gap=True),
        Build("DL-HDF-100-DEC", "ACP 3 / 100 fill / HDF 3 on resilient pads + felt 9",
              [a3, h3], 100, 100, ("point", 0.6), True, al100, 115),
        Build("DL-ST-100-DEC", "ACP 3 / 100 fill / steel 0.5 on resilient pads + felt 9",
              [a3, s05], 100, 100, ("point", 0.6), True, al100, 113),
        Build("DL-P6-P9-DEC", "ACP 3 + ply 6 / 40 fill / ply 9 on resilient pads + felt 9",
              [a3p6, p9], 40, 40, ("point", 0.6), True, al, 67),
        Build("DL-P6-P9-100-DEC", "ACP 3 + ply 6 / 100 fill / ply 9 on resilient pads + felt 9",
              [a3p6, p9], 100, 100, ("point", 0.6), True, al100, 127),
        Build("DL-2HDF-100-DEC", "ACP 3 / 100 fill / 2 x HDF 3 on resilient pads + felt 9",
              [a3, h6], 100, 100, ("point", 0.6), True, al100, 118),
    ]
    return {b.key: b for b in L}


# Measured 1/3-octave R, 80-5000 Hz, lab, bare glass (HW glass rows; Eastman "Acoustic glazing data"
# booklet 2018, tests EMN TR16-105 / TR16-106 / TR16-269, checked 2026-10-31). Float glass data; toughening
# is assumed not to change R (unverified).
THIRDS_8MM = (16, 30, 28, 29, 29, 28, 30, 31, 33, 34, 35, 34, 32, 31, 32, 36, 39, 41, 44)
THIRDS_10MM = (24, 29, 27, 29, 30, 31, 32, 32, 33, 35, 34, 33, 32, 32, 36, 39, 42, 44, 47)
THIRDS_44Q = (20, 30, 28, 29, 29, 30, 31, 31, 33, 35, 36, 37, 39, 40, 39, 39, 39, 43, 47)


def thirds_to_octaves(t):
    """80..5000 Hz thirds -> 125..4000 Hz octaves (energy mean of the three thirds in each octave)."""
    out = []
    for i in range(6):
        trio = t[1 + 3 * i: 4 + 3 * i]
        out.append(-10 * math.log10(sum(10 ** (-x / 10) for x in trio) / 3))
    return out


# Front panes: measured octave sets where published; acrylic stays on the model (published PMMA sound
# figures disagree with each other, HW acrylic row).
GLASS = {
    "G8": ("Tempered 8 mm", 20.0, thirds_to_octaves(THIRDS_8MM)),
    "G10": ("Tempered 10 mm (v1)", 25.0, thirds_to_octaves(THIRDS_10MM)),
    "L44": ("Laminated acoustic 4+4 (8.76 mm)", 21.0, thirds_to_octaves(THIRDS_44Q)),
    "A8": ("Smoked acrylic 8 mm", 9.5, None),
    "A10": ("Smoked acrylic 10 mm", 11.9, None),
    "A12": ("Smoked acrylic 12 mm", 14.3, None),
}


# An acrylic door needs an aluminium hinge-edge stile (HW C9, DECIDED baseline): 10 x 50 stile 2.71 kg + two
# 3 x 60 cover strips 1.95 kg + EPDM pads 0.31 kg + 16 M6 bolts 0.19 kg - acrylic it replaces 1.27 kg (calculation)
FRONT_EXTRA_KG = {"A8": 3.9, "A10": 3.9, "A12": 3.9}


def panes():
    out = {}
    for key, (label, kg, rdata) in GLASS.items():
        if key == "G8":
            lf = plate(label, [layer("glass", 8)])
        elif key == "G10":
            lf = plate(label, [layer("glass", 10)])
        elif key == "L44":
            _, b4, _ = lam([layer("glass", 4)])
            # ASSUME: acoustic PVB couples the plies weakly (stiffness 1.5 x two loose plies) and damps (eta 0.15)
            lf = Leaf(label, kg, f_crit(kg, 3 * b4), 0.15)
        else:
            lf = plate(label, [layer("pmma", int(key[1:]))])
        basis = "measured, lab (Eastman via HW)" if rdata else "model (Sharp)"
        b = Build(key, label, [lf], felt=False, r_data=rdata, basis=basis)
        b.kg_m2 = kg
        out[key] = b
    return out


def extras(wb):
    a3 = acp()
    wb["_DECOR"] = Build("_DECOR", "Front decor: ACP 3 / ~150 air, 16x16 frame / ACP 3",
                         [a3, a3], 150, 0, ("line", 0.3), False)
    wb["_DECOR_FILL"] = Build("_DECOR_FILL", "Front decor with 75 mm PET fill",
                              [a3, a3], 150, 75, ("line", 0.3), False)
    wb["_FLOOR_RAISED"] = Build("_FLOOR_RAISED", "Raised floor: ply 15 over an open frame",
                                [plate("ply 15", [layer("ply", 15)])], felt=False)
    wb["_FLOOR_THIN"] = Build("_FLOOR_THIN", "Thin floor on the room's slab", [], felt=False,
                              r_data=[50.0] * 6)
    return wb


# ---------------------------------------------------------------------------
# Absorption inside (alpha 125..4k)
# ---------------------------------------------------------------------------
ALPHA = {
    # PET felt: no 9 mm panel with published octave data was found (HW felt rows). Autex Cube ISO 354 data is
    # used as the proxy (source; 12 mm is 3 mm thicker than the plan's 9 mm, so slightly optimistic):
    "felt_gap": (0.05, 0.30, 0.60, 0.95, 0.95, 0.85),        # Autex Cube 12 mm + 25 mm air gap (HW felt row)
    "felt_direct": (0.05, 0.10, 0.30, 0.65, 0.90, 0.95),     # Autex Cube 12 mm, direct on a hard face
    "pet_thick": (0.05, 0.20, 0.60, 0.90, 1.00, 1.00),       # Autex Cube 24 mm, direct
    "glass": (0.18, 0.06, 0.04, 0.03, 0.02, 0.02),           # ASI_ABS heavy plate glass
    "ply": (0.28, 0.22, 0.17, 0.09, 0.10, 0.11),             # ASI_ABS plywood paneling
    "wood_floor": (0.15, 0.11, 0.10, 0.07, 0.06, 0.07),      # ASI_ABS wood floor
    "hard_floor": (0.02, 0.03, 0.03, 0.03, 0.03, 0.02),      # ASI_ABS tile on concrete
    "metal": (0.18, 0.06, 0.04, 0.03, 0.02, 0.02),           # ASSUME painted ACP = heavy glass row
}

# ---------------------------------------------------------------------------
# Geometry (inside faces)
# ---------------------------------------------------------------------------
GEOM = {
    "v1": dict(w=2.372, d=1.480, h=2.223),   # V1_BOM inside size, source
    "v2": dict(w=2.42, d=1.50, h=2.30),      # calculation from PLAN outside size; build-ups ASSUME
}
DOOR_W, DOOR_H = 1.1756, 2.011               # V1_BOM GL-01 (kept in v2: same look)
DOOR_M2 = DOOR_W * DOOR_H
FIXED_M2 = 3.425 - DOOR_M2                   # finished fixed-glass shape from the v1 STEP (layout study, 68.5 kg at
                                             # 8 mm = 3.425 m2 door + fixed); the BOM's 2138.5 x 723.7 is its bounding box
GLASS_M2 = DOOR_M2 + FIXED_M2
OUT_WALL_M2 = 2 * 1.5 * 2.29 + 2.424 * 2.252  # layout-study panel areas: 2 sides 1500 x 2290 + back 2424 x 2252
OUT_CEIL_M2 = 2.424 * 1.5                       # layout-study ceiling 2424 x 1500
REST_KG = 102.4   # layout study (branch super-tab/7667a51, commit cb7009f, work in progress): 'Spaceship light
                  # indoor build' total 303.0 kg minus walls+ceiling 103.0, felt 29.0 and glass 68.5. Includes the
                  # thin floor and base band, decor blocks, door hardware with drop seal and glazing profiles,
                  # fans, 2 silencer boxes, electrics and a 4 kg voice-kit reserve.


def areas(g):
    w, d, h = g["w"], g["d"], g["h"]
    return dict(walls=w * h + 2 * d * h, ceiling=w * d, floor=w * d, front=w * h,
                glass=GLASS_M2, decor=w * h - GLASS_M2, volume=w * d * h)


# ---------------------------------------------------------------------------
# Leaks, seals, vents
# ---------------------------------------------------------------------------
SCEN = {   # all ASSUME (reasons in report.md)
    "low": dict(gap_side=5.0, gap_top=5.0, gap_bottom=10.0, joint=0.30, seal_r=25.0, gasket_r=28.0,
                sil_derate=0.6, r_off=-2.0, alpha_k=0.85, floor_bonus=0.0, open_vent_il=0.0, cable_mm2=900.0),
    "central": dict(gap_side=3.5, gap_top=3.5, gap_bottom=8.0, joint=0.15, seal_r=32.0, gasket_r=33.0,
                    sil_derate=0.8, r_off=0.0, alpha_k=1.0, floor_bonus=3.0, open_vent_il=3.0, cable_mm2=600.0),
    "high": dict(gap_side=2.0, gap_top=2.0, gap_bottom=5.0, joint=0.05, seal_r=38.0, gasket_r=38.0,
                 sil_derate=1.0, r_off=2.0, alpha_k=1.15, floor_bonus=6.0, open_vent_il=6.0, cable_mm2=300.0),
}
SEAL_STRIP = 0.010                   # m, equivalent width of a sealed strip (ASSUME)
JOINT_LEN = {"v1": 28.9, "v2": 34.0}  # m of panel-to-panel joints (calculation, report.md)
BASE_LEN = {"v1": 7.7, "v2": 7.8}     # m, floor perimeter (calculation)
VENT_OPEN = {"v1": 2 * 0.0295,        # calculation from V1_DWG sheet 9: per fan unit 2 x 20 slots 76 x 10 mm
             "plan": 2 * 0.020}       # ASSUME: plan shows slot patterns but no size

# Silencers (DECIDED 2026-10-31): splitter cartridges inside the hollow front decor blocks, outside the pod's
# sound shell, next to their fans. Two 50 mm air passages between three 25 mm lining layers, so the lined
# perimeter over free area P/S = 40 per metre (calculation). Supply: right block, vertical, 175 x 500 x 2000 mm.
# Exhaust: top block, horizontal, 175 x 280 x 1500 mm. The fan's sound also breaks out through the cartridge
# casing into the felt-lined decor cavity and then through the decor's inner ACP face into the pod.
SIL_PS = 40.0
LINING_DATA = {   # absorption of the splitter lining layers, 125..4k Hz
    25.0: (0.08, 0.27, 0.48, 0.63, 0.71, 0.75),   # Pyrotek Sorberpoly 2D 25 mm, 32 kg/m3, ISO 354 (HW fill row)
    37.5: (0.12, 0.37, 0.65, 0.77, 0.78, 0.79),   # ASSUME: linear between the 25 and 50 mm data (custom thickness)
    50.0: (0.16, 0.47, 0.82, 0.90, 0.84, 0.83),   # Pyrotek Sorberpoly 2D 50 mm, ISO 354 (HW fill row)
}
SIL_LINING_MM = 37.5                               # DECIDED with the PM: three 37.5 mm layers, two 50 mm gaps
SIL_LINING_ALPHA = LINING_DATA[SIL_LINING_MM]
SIL_CAP_DB = 40.0                                         # ASSUME: flanking limit per band
SIL_DERATE = 0.8                                          # ASSUME: Sabine formula derated (central case)
SIL_PATHS = {   # name: (length m, free area m2, casing face width toward the decor cavity m, depth x width m)
    "supply": (2.0, 0.050, 0.5, (0.2125, 0.500)),    # 3 x 37.5 lining + 2 x 50 gaps = 212.5 mm deep
    "exhaust": (1.5, 0.028, 0.5, (0.2125, 0.280)),
}
CASINGS = {     # DECIDED: al20
    "al08": ("aluminium 0.8 mm", "alu", 0.8),
    "al20": ("aluminium 2.0 mm", "alu", 2.0),
    "st10": ("steel 1.0 mm", "steel", 1.0),
}
LINING_KG_M3 = 40.0    # polyester lining board, about 40 kg/m3 (ASSUME)


def silencer_il(length, derate=1.0):
    return [min(1.05 * a ** 1.4 * SIL_PS * length * derate, SIL_CAP_DB) for a in SIL_LINING_ALPHA]


def cartridge_kg(casing):
    _, mat, t = CASINGS[casing]
    kg_m2 = MAT[mat][0] * t / 1000
    tot = 0.0
    for L, area, b, (dep, wid) in SIL_PATHS.values():
        tot += 2 * (dep + wid) * L * kg_m2 + 3 * wid * L * LINING_KG_M3 * SIL_LINING_MM / 1000
    return tot


def flat(x):
    return [x] * 6


def taus(rb, off=0.0):
    return [10 ** (-(r + off) / 10) for r in rb]


def elements(cfg, sc, wb, gb):
    g = GEOM[cfg["geom"]]
    a = areas(g)
    s = SCEN[sc]
    off = s["r_off"]
    el = [("walls", a["walls"], taus(wb[cfg["wall"]].r(), off)),
          ("ceiling", a["ceiling"], taus(wb[cfg.get("ceiling", cfg["wall"])].r(), off)),
          ("glass", a["glass"], taus(gb[cfg["glass"]].r(), off)),
          ("front decor", a["decor"], taus(wb["_DECOR_FILL" if cfg.get("decor_fill") else "_DECOR"].r(), off))]
    if cfg["floor"] == "raised":
        el.append(("floor", a["floor"], taus(wb["_FLOOR_RAISED"].r(), off + s["floor_bonus"])))
    else:
        el.append(("floor", a["floor"], taus(wb["_FLOOR_THIN"].r(), off)))
        if cfg.get("base_seal"):
            el.append(("base joint", BASE_LEN[cfg["geom"]] * SEAL_STRIP, flat(10 ** (-s["gasket_r"] / 10))))
        else:
            el.append(("base joint", BASE_LEN[cfg["geom"]] * 0.001, flat(1.0)))
    if cfg.get("door_seals"):
        el.append(("door edge seals", (2 * DOOR_H + DOOR_W) * SEAL_STRIP, flat(10 ** (-s["seal_r"] / 10))))
    else:
        el.append(("door edge gaps", (2 * DOOR_H * s["gap_side"] + DOOR_W * s["gap_top"]) / 1000, flat(1.0)))
    if cfg.get("drop_seal"):
        el.append(("door bottom", DOOR_W * SEAL_STRIP, flat(10 ** (-s["seal_r"] / 10))))
    else:
        el.append(("door bottom", DOOR_W * s["gap_bottom"] / 1000, flat(1.0)))
    fg_len = 5.5   # m, fixed-glass edge (calculation from the BOM outline)
    if cfg.get("glass_seals"):
        el.append(("fixed glass edges", fg_len * SEAL_STRIP, flat(10 ** (-s["gasket_r"] / 10))))
    else:
        el.append(("fixed glass edges", fg_len * s["joint"] / 1000, flat(1.0)))
    jl = JOINT_LEN[cfg["geom"]]
    if cfg.get("gaskets"):
        el.append(("panel joints", jl * SEAL_STRIP, flat(10 ** (-s["gasket_r"] / 10))))
    else:
        el.append(("panel joints", jl * s["joint"] / 1000, flat(1.0)))
    if cfg["vents"] == "silenced":
        st_v = [0.0] * 6
        ar_v = 0.0
        for L, area, _, _ in SIL_PATHS.values():
            il = silencer_il(L, s["sil_derate"])
            st_v = [x + area * 10 ** (-y / 10) for x, y in zip(st_v, il)]
            ar_v += area
        el.append(("vents", ar_v, [x / ar_v for x in st_v]))
    else:
        el.append(("vents", VENT_OPEN[cfg["vents"]], flat(10 ** (-s["open_vent_il"] / 10))))
    if cfg.get("grommets"):
        el.append(("cable holes", 2 * 0.0004, flat(10 ** (-30 / 10))))
    else:
        el.append(("cable holes", s["cable_mm2"] * 1e-6, flat(1.0)))
    k = s["alpha_k"]
    def lining(build_key):
        if cfg["lining"] != "felt":
            return ALPHA["ply"]
        return ALPHA["felt_gap"] if wb[build_key].felt_mount == "gap" else ALPHA["felt_direct"]
    ceil_alpha = ALPHA["pet_thick"] if cfg.get("ceil_absorber") else lining(cfg.get("ceiling", cfg["wall"]))
    ab = [(a["walls"], lining(cfg["wall"])),
          (a["ceiling"], ceil_alpha),
          (a["glass"], ALPHA["glass"]),
          (a["decor"], ALPHA["felt_direct"] if cfg.get("decor_felt") else ALPHA["metal"]),
          (a["floor"], ALPHA["wood_floor"] if cfg["floor"] == "raised" else ALPHA["hard_floor"])]
    ain = [sum(ar * min(0.99, al[i] * k) for ar, al in ab) for i in range(6)]
    return el, ain


def pod(cfg, sc, wb, gb):
    el, ain = elements(cfg, sc, wb, gb)
    st = [sum(ar * t[i] for _, ar, t in el) for i in range(6)]
    il = [10 * math.log10(1 + ain[i] / st[i]) for i in range(6)]
    dsa = -10 * math.log10(sum(w * 10 ** (-x / 10) for w, x in zip(W_SPEECH, il)))
    sh = {n: sum(W_SPEECH[i] * ar * t[i] / st[i] * 10 ** (-il[i] / 10) for i in range(6)) for n, ar, t in el}
    tot = sum(sh.values())
    return dict(il=il, dsa=dsa, share={n: v / tot for n, v in sh.items()})


# ---------------------------------------------------------------------------
# Configurations and weights
# ---------------------------------------------------------------------------
V1 = dict(geom="v1", wall="V1-DWG", glass="G10", floor="raised", vents="v1", lining="ply")
PLAN = dict(geom="v2", wall="PLAN", glass="G10", floor="raised", vents="plan", lining="felt")
FIXES = [
    # label, change, kg added to the pod, kg basis
    ("Door edge seals on 3 sides", dict(door_seals=True), 1.0, "HW door-seal rows, about 0.2 kg/m x 5.2 m"),
    ("Door drop seal", dict(drop_seal=True), 1.0, "HW drop-seal row"),
    ("Fixed glass in sealed U-profiles", dict(glass_seals=True), 0.0, "profiles are already in the layout study's rest"),
    ("Gaskets on every panel joint", dict(gaskets=True), 1.0, "HW gasket row, about 0.03 kg/m x 34 m"),
    ("Silenced vents (splitter silencers in the decor blocks)", dict(vents="silenced"), round(cartridge_kg("al20") - 3.0, 1),
     "calculation: two cartridges with 2 mm aluminium casings, less the 3 kg already in the layout study's rest"),
    ("Thin floor with base seal (DECIDED, D-05)", dict(floor="thin", base_seal=True), 0.5,
     "HW base-seal row; the floor itself is in the weight study"),
    ("Sealed cable holes", dict(grommets=True), 0.1, "HW grommet row"),
]
FIX_ALL = {}
for _l, _c, _k, _b in FIXES:
    FIX_ALL.update(_c)
FIX_KG = sum(k for _, _, k, _ in FIXES)


# Fix mass not already inside REST_KG (layout study): door edge seals 1.0, joint gaskets 1.0, base seal 0.5,
# grommets 0.1 (calculation); the silencer cartridges are added by casing, less the study's 2 x 1.5 kg boxes.
EXTRA_FIX_KG = 2.6
FAN_KG = 6.0           # S&P TD-500/150-160 ECOWATT, 6.0 kg (HW fan row); the PM asked to use 6 kg per fan


def pod_total_kg(cfg, wb, gb):
    """Whole pod, all light fixes on: rest of pod + wall and ceiling build-ups (with felt, fill, frame) + front."""
    kg = REST_KG + EXTRA_FIX_KG
    kg += wb[cfg["wall"]].kg_m2 * OUT_WALL_M2 + wb[cfg.get("ceiling", cfg["wall"])].kg_m2 * OUT_CEIL_M2
    kg += gb[cfg["glass"]].kg_m2 * GLASS_M2 + FRONT_EXTRA_KG.get(cfg["glass"], 0.0)
    kg += cartridge_kg(cfg.get("casing", "al20")) - 3.0
    kg += 2 * (FAN_KG - 1.5)           # TD-500 fans at 6 kg each; the layout study's rest carries 1.5 kg each
    return kg


def wall_kg(wb, key):
    return wb[key].kg_m2 * (OUT_WALL_M2 + OUT_CEIL_M2)


def pod_kg(cfg, wb, gb):
    """kg that this study changes: wall+ceiling build-ups, glass, fixes. Not the whole pod."""
    kg = wb[cfg["wall"]].kg_m2 * OUT_WALL_M2 + wb[cfg.get("ceiling", cfg["wall"])].kg_m2 * OUT_CEIL_M2
    kg += gb[cfg["glass"]].kg_m2 * GLASS_M2
    for _, change, k, _ in FIXES:
        if all(cfg.get(kk) == vv for kk, vv in change.items()):
            kg += k
    return kg


# ---------------------------------------------------------------------------
# Air
# ---------------------------------------------------------------------------
AIR = dict(
    people=2,
    co2_per_person_ls=0.0052,   # ASSUME, consistent with BRIEF (26 l/s -> 800 ppm from 400 ppm)
    room_ppm=(400.0, 600.0),    # BRIEF uses 400 (outdoor); 600 = typical occupied office (ASSUME)
    sensible_w_person=75.0,     # ASSUME seated office work
    laptop_w=30.0,              # ASSUME per person
    lights_w=15.0,              # HW lights: 6 x Haefele Loox5 LED 2094 at 2.5 W (source)
    front_light_w=6.0,          # HW lights: 2 m Haefele Loox5 LED 2162 at 3.0 W/m (source)
    controls_w=3.0,             # HW CO2 controller row - provisional
    voice_kit_w=60.0,           # reserve for the later voice cockpit kit: ASSUME, same as the layout study
)
SYS_K = 7.5   # ASSUME: entry 0.5 + outside slot grille 2.0 + inside diffuser 2.0 + exit 1.0 + splitter 2.0
# The plan's Panasonic FV-15AUL1 has no published curve and its manual forbids ceiling mounting (HW): not used.

# Duct-side sound power per octave, A-weighted per band, dB(A), 125..4000 Hz, at a duty point near
# 70 l/s (S&P TD-350/100-125 SILENT ECOWATT, 8 V, point 5, about 250 m3/h = 69 l/s at about 30 Pa;
# S&P catalogue values via HW fan rows, duty point read off the curve figure: source, approximate).
FAN_BANDS = {
    "S&P TD-350/100-125 ECOWATT, 8 V (69 l/s @ 30 Pa)": dict(
        inlet=(25, 44, 53, 45, 39, 34), outlet=(27, 42, 54, 44, 37, 32), lwa=54, watts=15, kg=5.0),
    "S&P TD-500/150-160 ECOWATT, 4 V (56 l/s @ 42 Pa)": dict(
        inlet=(25, 37, 49, 46, 37, 29), outlet=(25, 37, 49, 46, 37, 29), lwa=51, watts=10, kg=6.0),
}


def sys_dp(q_ls, area):
    """Pressure drop of one vent path at q_ls through a splitter of free area `area` (square law)."""
    v = q_ls / 1000 / area
    return SYS_K * 0.5 * RHO0 * v * v


def co2_rows():
    v = areas(GEOM["v2"])["volume"]
    g = AIR["people"] * AIR["co2_per_person_ls"]
    rows = []
    for q in (26.0, 40.0, 53.0, 70.0):
        rise = g / q * 1e6
        tau_min = v / (q / 1000) / 60
        heat = (AIR["people"] * (AIR["sensible_w_person"] + AIR["laptop_w"]) + AIR["lights_w"]
                + AIR["front_light_w"] + AIR["controls_w"])
        dt = heat / (RHO0 * CP_AIR * q / 1000)
        dt_kit = (heat + AIR["voice_kit_w"]) / (RHO0 * CP_AIR * q / 1000)
        ach = q / 1000 * 3600 / v
        rows.append((q, ach, 60 / ach, rise, AIR["room_ppm"][0] + rise, AIR["room_ppm"][1] + rise,
                     3 * tau_min, dt, dt_kit))
    return rows, v, g


def co2_after(q_ls, minutes, start_ppm, room_ppm):
    v = areas(GEOM["v2"])["volume"]
    g = AIR["people"] * AIR["co2_per_person_ls"]
    ss = room_ppm + g / q_ls * 1e6
    return ss + (start_ppm - ss) * math.exp(-q_ls / 1000 * minutes * 60 / v)


def end_reflection(f, area_m2):
    """Duct end reflection loss for an opening flush with a surface (ASHRAE HVAC Applications,
    noise chapter: ERL = 10 lg[1 + (0.7 c / (pi f D))^2]; formula source, not re-checked online)."""
    d = math.sqrt(4 * area_m2 / math.pi)
    return 10 * math.log10(1 + (0.7 * C0 / (math.pi * f * d)) ** 2)


FAN_SPEED_DB = {"supply": 0.0, "exhaust": 2.5}   # ASSUME: the exhaust path (28 Pa at 70 l/s) needs a little
                                                  # more speed than the TD-500 4 V point; the supply (9 Pa) less


def inside_room_terms():
    a = areas(GEOM["v2"])
    s_tot = a["walls"] + a["ceiling"] + a["floor"] + a["front"]
    ain = [(a["walls"] + a["ceiling"]) * ALPHA["felt_gap"][i] + a["glass"] * ALPHA["glass"][i]
           + a["decor"] * ALPHA["metal"][i] + a["floor"] * ALPHA["hard_floor"][i] for i in range(6)]

    def room(r, i):
        abar = ain[i] / s_tot
        rc = ain[i] / (1 - abar)
        return 10 * math.log10(2 / (4 * math.pi * r * r) + 4 / rc)
    return room


def fan_noise_inside(fan_key, casing="al20", q_ls=70.0, derate=SIL_DERATE):
    """LpA at a seated head (1.0 m from the supply grille, 1.5 m from the exhaust grille, 1.2 m from the decor
    faces) from both fans: the duct path through each splitter plus breakout through the cartridge casing,
    the felt-lined decor cavity and the decor's inner ACP face. Returns (duct dB(A), breakout dB(A), total)."""
    room = inside_room_terms()
    fan = FAN_BANDS[fan_key]
    _, mat, t = CASINGS[casing]
    casing_leaf = plate(casing, [layer(mat, t)])
    face = acp()
    flow_db = 50 * math.log10(q_ls / 70.0)
    duct = brk = 0.0
    for name, side, r in (("supply", "outlet", 1.0), ("exhaust", "inlet", 1.5)):
        L, area, b, _ = SIL_PATHS[name]
        bands = [x + flow_db + FAN_SPEED_DB[name] for x in fan[side]]
        il = silencer_il(L, derate)
        for i, f in enumerate(BANDS):
            duct += 10 ** ((bands[i] - il[i] - end_reflection(f, area) + room(r, i)) / 10)
            a_db = max(1.05 * SIL_LINING_ALPHA[i] ** 1.4 * SIL_PS * derate, 0.5)
            k = a_db / 4.343
            tau = 10 ** (-(r_single(casing_leaf, f) + finite_gain(f, 1.0)) / 10)
            lw_cav = bands[i] + 10 * math.log10(tau * (b / area) * (1 - math.exp(-k * L)) / k)
            a_cav = 1.5 * ALPHA["felt_direct"][i] + 0.05      # ASSUME: 1.5 m2 of felt lining in the block
            r_face = r_single(face, f) + finite_gain(f, 0.8)
            lw_pod = lw_cav - r_face + 10 * math.log10(0.8 / a_cav)
            brk += 10 ** ((lw_pod + room(1.2, i)) / 10)
    return 10 * math.log10(duct), 10 * math.log10(brk), 10 * math.log10(duct + brk)


def flow_for(target_dba, fan_key, casing="al20"):
    lo, hi = 10.0, 120.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if fan_noise_inside(fan_key, casing, mid)[2] > target_dba:
            hi = mid
        else:
            lo = mid
    return lo


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def row(c):
    return "| " + " | ".join(c) + " |"


def t_walls(wb):
    out = ["| Key | Build, outside / cavity / inside | kg/m2 with frame | mm | 125 | 250 | 500 | 1k | 2k | 4k | R speech |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, b in wb.items():
        if k.startswith("_"):
            continue
        r = b.r()
        out.append(row([k, b.name, f"{b.kg_m2:.1f}", f"{b.thick}"] + [f"{x:.0f}" for x in r] + [f"{r_speech(r):.1f}"]))
    return "\n".join(out)


def t_wallmatch(wb):
    """Wall-only comparison: lightest build-up whose R speech reaches each v1 reading."""
    out = ["| Target (wall element only) | Lightest build that reaches it | kg/m2 | mm | R speech | Walls + ceiling kg |",
           "|---|---|---:|---:|---:|---:|"]
    cands = [b for k, b in wb.items() if not k.startswith("_") and not k.startswith("V1")]
    for vk in ("V1-BOM", "V1-DWG"):
        goal = r_speech(wb[vk].r())
        ok = [b for b in cands if r_speech(b.r()) >= goal - 0.05]
        if not ok:
            best = max(cands, key=lambda b: r_speech(b.r()))
            out.append(row([f"{vk} ({goal:.1f})", f"none; best is {best.key} at {r_speech(best.r()):.1f}", "", "", "", ""]))
            continue
        b = min(ok, key=lambda x: x.kg_m2)
        out.append(row([f"{vk} ({goal:.1f})", f"{b.key}: {b.name}", f"{b.kg_m2:.1f}", f"{b.thick}",
                        f"{r_speech(b.r()):.1f}", f"{b.kg_m2 * (OUT_WALL_M2 + OUT_CEIL_M2):.0f}"]))
    return "\n".join(out)


def t_panes(gb):
    out = ["| Key | Front pane | kg/m2 | Door kg | Door + fixed kg | 125 | 250 | 500 | 1k | 2k | 4k | R speech | Basis |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for k, b in gb.items():
        r = b.r()
        out.append(row([k, b.name, f"{b.kg_m2:.1f}", f"{b.kg_m2 * DOOR_M2:.0f}", f"{b.kg_m2 * GLASS_M2:.0f}"]
                       + [f"{x:.0f}" for x in r] + [f"{r_speech(r):.1f}", b.basis]))
    return "\n".join(out)


def band(cfg, wb, gb):
    return [pod(cfg, s, wb, gb)["dsa"] for s in ("low", "central", "high")]


def t_fixes(wb, gb):
    out = ["| Step | Change | D_S,A low | central | high | Gain (central) | kg added |",
           "|---|---|---:|---:|---:|---:|---:|"]
    cfg = dict(PLAN, glass="G8")
    prev = band(cfg, wb, gb)
    out.append(row(["0", "Spaceship as planned, 8 mm glass"] + [f"{x:.1f}" for x in prev] + ["", ""]))
    for i, (label, change, kg, _) in enumerate(FIXES, 1):
        cfg = dict(cfg, **change)
        cur = band(cfg, wb, gb)
        out.append(row([str(i), label] + [f"{x:.1f}" for x in cur] + [f"{cur[1] - prev[1]:+.1f}", f"{kg:.1f}"]))
        prev = cur
    return "\n".join(out), cfg


def t_pods(wb, gb, fixed):
    named = [
        ("v1 as drawn (inner ply 15)", V1),
        ("v1 per BOM (inner ply 9)", dict(V1, wall="V1-BOM")),
        ("Spaceship as planned (10 mm glass)", PLAN),
        ("Spaceship as planned, 8 mm glass", dict(PLAN, glass="G8")),
        ("+ all light fixes (plan wall)", fixed),
        ("+ fixes, plan wall without plywood", dict(fixed, wall="PLAN-NOPLY")),
        ("+ fixes, light double wall DL-HDF", dict(fixed, wall="DL-HDF")),
        ("+ fixes, DL-HDF decoupled", dict(fixed, wall="DL-HDF-DEC")),
        ("+ fixes, DL-ST (steel 0.5 inner skin)", dict(fixed, wall="DL-ST")),
        ("+ fixes, DL-ST decoupled", dict(fixed, wall="DL-ST-DEC")),
        ("+ fixes, honeycomb sandwich SW-HC20", dict(fixed, wall="SW-HC20")),
        ("+ fixes, foam sandwich + inner skin", dict(fixed, wall="SW-FOAM20-DL")),
        ("DECIDED stack, 4+4 laminated front", dict(fixed, **DECIDED_STACK)),
        ("DECIDED stack with the acrylic experiment", dict(fixed, **dict(DECIDED_STACK, glass="A10"))),
    ]
    out = ["| Pod | D_S,A low | central | high |", "|---|---:|---:|---:|"]
    res = {}
    for name, cfg in named:
        b = band(cfg, wb, gb)
        res[name] = (b, cfg)
        out.append(row([name] + [f"{x:.1f}" for x in b]))
    return "\n".join(out), res


def t_fronts(wb, gb, base):
    out = ["| Front pane (door + fixed) | kg | D_S,A low | central | high | vs 8 mm |", "|---|---:|---:|---:|---:|---:|"]
    ref = band(dict(base, glass="G8"), wb, gb)[1]
    for k, b in gb.items():
        bb = band(dict(base, glass=k), wb, gb)
        out.append(row([b.name, f"{b.kg_m2 * GLASS_M2:.0f}"] + [f"{x:.1f}" for x in bb] + [f"{bb[1] - ref:+.1f}"]))
    return "\n".join(out)


def t_share(wb, gb, cfgs):
    names = list(cfgs)
    keys = None
    cols = {}
    for n in names:
        sh = pod(cfgs[n], "central", wb, gb)["share"]
        cols[n] = sh
        keys = keys or list(sh)
    out = ["| Path (share of speech sound getting out) | " + " | ".join(names) + " |",
           "|---|" + "---:|" * len(names)]
    for k in keys:
        out.append(row([k] + [f"{100 * cols[n].get(k, 0):.0f}%" for n in names]))
    return "\n".join(out)


def t_curve(wb, gb, base):
    """Best predicted D_S,A for each total pod weight, all light fixes on (Lead request).
    Two fronts: glass (8 mm tempered or 4+4 laminated) and smoked acrylic 10 mm."""
    wall_keys = [k for k in wb if not k.startswith("_") and not k.startswith("V1")]
    out = []
    for title, fronts in (("Glass front (8 mm tempered or 4+4 laminated)", ("G8", "L44")),
                          ("Smoked acrylic 10 mm front", ("A10",))):
        combos = []
        for wk in wall_keys:
            for ck in wall_keys:
                for gk in fronts:
                    cfg = dict(base, wall=wk, ceiling=ck, glass=gk)
                    combos.append((pod_total_kg(cfg, wb, gb), pod(cfg, "central", wb, gb)["dsa"], cfg))
        out += [f"{title}:", "",
                "| Pod budget kg | Best wall / ceiling / front | Total kg | D_S,A low / central / high |",
                "|---:|---|---:|---|"]
        for budget in range(280, 521, 20):
            ok = [c for c in combos if c[0] <= budget]
            if not ok:
                out.append(row([str(budget), "nothing fits", "", ""]))
                continue
            kg, d, cfg = max(ok, key=lambda c: (round(c[1], 1), -c[0]))
            bb = band(cfg, wb, gb)
            out.append(row([str(budget), f"{cfg['wall']} / {cfg['ceiling']} / {gb[cfg['glass']].name}",
                            f"{kg:.0f}", " / ".join(f"{x:.1f}" for x in bb)]))
        out.append("")
    return "\n".join(out).rstrip()


DECIDED_WALLS = ("DL-HDF-40-FL", "DL-ST-40-FL", "DL-ST-40-FLG", "DL-ST-40-FLG-12")
# DECIDED 2026-10-31: 4+4 laminated front (frameless like v1), 40 mm ceiling frames, splitter silencers in the
# decor blocks with 2 mm aluminium casings, 20x40x1.2 frames (rivnut grip check passed), fill stays 32 kg/m3.
DECIDED_STACK = dict(wall="DL-ST-40-FLG-12", ceiling="DL-ST-40-FLG-12", glass="L44", casing="al20")


def t_recommend(wb, gb, base):
    out = ["| Case | Walls | Ceiling | Front | Silencer casing | Total kg | D_S,A low / central / high |",
           "|---|---|---|---|---|---:|---|"]
    rows = [("DECIDED stack", dict(base, **DECIDED_STACK)),
            ("Same with 20x40x1.5 frames", dict(base, **dict(DECIDED_STACK, wall="DL-ST-40-FLG", ceiling="DL-ST-40-FLG"))),
            ("Same with a 0.4 mm tray (rejected: costs 1 dB)", dict(base, **dict(DECIDED_STACK, wall="DL-ST4-40-FLG-12", ceiling="DL-ST4-40-FLG-12"))),
            ("Same, felt flat on the ceiling lining (no gap)", dict(base, **dict(DECIDED_STACK, ceiling="DL-ST-40-FL"))),
            ("Acrylic experiment: 10 mm with hinge stile", dict(base, **dict(DECIDED_STACK, glass="A10"))),
            ("Light 0.8 mm casings (fails the noise target)", dict(base, **dict(DECIDED_STACK, casing="al08")))]
    for label, cfg in rows:
        kg = pod_total_kg(cfg, wb, gb)
        b = band(cfg, wb, gb)
        out.append(row([label, cfg["wall"], cfg["ceiling"], gb[cfg["glass"]].name, CASINGS[cfg["casing"]][0],
                        f"{kg:.0f}", " / ".join(f"{x:.1f}" for x in b)]))
    return "\n".join(out), rows


def t_air():
    rows, v, g = co2_rows()
    out = [f"Inside volume {v:.2f} m3; CO2 from 2 people {g * 1000:.1f} ml/s.", "",
           "| Fresh air l/s | Air changes /h | Minutes per change | CO2 rise ppm | CO2 ppm, room 400 | CO2 ppm, room 600 | Minutes to 95% | Heat rise K | Heat rise K with voice kit |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for q, ach, mins, rise, c4, c6, t95, dt, dtk in rows:
        out.append(row([f"{q:.0f}", f"{ach:.0f}", f"{mins:.1f}", f"{rise:.0f}", f"{c4:.0f}", f"{c6:.0f}",
                        f"{t95:.0f}", f"{dt:.1f}", f"{dtk:.1f}"]))
    out.append("")
    out.append(f"CO2 after 2 h at 40 l/s from 400 ppm (room 400): {co2_after(40, 120, 400, 400):.0f} ppm; "
               f"after 3 h at 26 l/s, room 600: {co2_after(26, 180, 600, 600):.0f} ppm.")
    return "\n".join(out)


FAN_DECIDED = "S&P TD-500/150-160 ECOWATT, 4 V (56 l/s @ 42 Pa)"


def t_fans():
    out = ["| Fan, 2 mm aluminium casings | Duct LwA dB(A) at its data point | Inside at 53 l/s: duct / breakout / total dB(A) | Inside at 70 l/s: duct / breakout / total | Flow for 25 dB(A) l/s |",
           "|---|---:|---|---|---:|"]
    for k, fan in FAN_BANDS.items():
        a = fan_noise_inside(k, "al20", 53.0)
        b = fan_noise_inside(k, "al20", 70.0)
        out.append(row([k + (" (DECIDED)" if k == FAN_DECIDED else ""), f"{fan['lwa']}",
                        " / ".join(f"{x:.1f}" for x in a), " / ".join(f"{x:.1f}" for x in b),
                        f"{flow_for(25.0, k, 'al20'):.0f}"]))
    return "\n".join(out)


def t_silencer():
    out = ["| Splitter (2 mm aluminium casing unless noted) | Two cartridges kg | Supply path IL 125 | 250 | 500 | 1k | 2k | 4k dB | Inside at 53 l/s dB(A) | at 70 l/s | Flow for 25 dB(A) l/s |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    global SIL_LINING_ALPHA, SIL_LINING_MM
    keep = (SIL_LINING_ALPHA, SIL_LINING_MM)
    cases = [(f"lining {mm:g} mm" + (" (DECIDED)" if mm == keep[1] else ""), mm, "al20") for mm in (25.0, 37.5, 50.0)]
    cases += [("lining 37.5 mm, casing aluminium 0.8 mm", 37.5, "al08"), ("lining 37.5 mm, casing steel 1.0 mm", 37.5, "st10")]
    for label, mm, ck in cases:
        SIL_LINING_MM, SIL_LINING_ALPHA = mm, LINING_DATA[mm]
        il = silencer_il(SIL_PATHS["supply"][0], SIL_DERATE)
        out.append(row([label, f"{cartridge_kg(ck):.1f}"] + [f"{x:.0f}" for x in il]
                       + [f"{fan_noise_inside(FAN_DECIDED, ck, 53.0)[2]:.1f}", f"{fan_noise_inside(FAN_DECIDED, ck, 70.0)[2]:.1f}",
                          f"{flow_for(25.0, FAN_DECIDED, ck):.0f}"]))
    SIL_LINING_ALPHA, SIL_LINING_MM = keep
    out.append("")
    out.append(f"Pressure drop at 70 l/s: supply {sys_dp(70, SIL_PATHS['supply'][1]):.0f} Pa, exhaust "
               f"{sys_dp(70, SIL_PATHS['exhaust'][1]):.0f} Pa. The 50 mm lining needs a 250 mm deep cartridge, "
               f"which does not fit the decor blocks.")
    return "\n".join(out)


def tables():
    wb = extras(walls())
    gb = panes()
    out = {}
    out["walls"] = t_walls(wb)
    out["wallmatch"] = t_wallmatch(wb)
    out["panes"] = t_panes(gb)
    out["fixes"], fixed = t_fixes(wb, gb)
    out["pods"], res = t_pods(wb, gb, fixed)
    v1b = res["v1 as drawn (inner ply 15)"][0]
    out["fronts"] = t_fronts(wb, gb, dict(fixed, **DECIDED_STACK))
    out["share"] = t_share(wb, gb, {"v1": V1, "Plan, 8 mm": dict(PLAN, glass="G8"),
                                    "Plan + fixes": fixed, "DECIDED stack": dict(fixed, **DECIDED_STACK)})
    ref_kg = pod_kg(dict(PLAN, glass="G8"), wb, gb)
    out["curve"] = t_curve(wb, gb, fixed)
    out["recommend"], _ = t_recommend(wb, gb, fixed)
    out["air"] = t_air()
    out["silencer"] = t_silencer()
    out["fans"] = t_fans()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    out = tables()
    if a.verify:
        rep = (HERE / "report.md").read_text(encoding="utf-8")
        bad = [k for k, v in out.items() if v not in rep]
        for k in bad:
            print(f"MISMATCH: table '{k}' differs from report.md")
        print("verify:", "OK, all", len(out), "tables match report.md" if not bad else f"{len(bad)} table(s) differ")
        return 1 if bad else 0
    for k, v in out.items():
        print(f"<!-- calc.py: {k} -->")
        print(v)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
