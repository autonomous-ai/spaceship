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
                         # The PM's weight ruling after PR #38 makes 24 kg/m3 the cavity fill's default, back to 32 if
                         # T02 fails; the cartridges' 50 mm layers stay at 32 for their published absorption. This model
                         # keeps 32 for its masses; the layout study's weight roll-up counts the lighter cavity fill.
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

    def r_low(self):
        """Low case for the 125-250 Hz risks (Reviewer 3 P2-4, PM ruling 5): no finite-panel gain, and an
        F0_DIP_DB dip in the one-third octaves within 1/3 octave of the mass-air-mass resonance f0."""
        if self.r_data is not None:
            return self.r()
        if len(self.leaves) == 1:
            lf = self.leaves[0]
            return octave(lambda f: r_single(lf, f))
        l1, l2 = self.leaves
        d = self.cavity / 1000
        filled = self.fill >= 0.5 * self.cavity
        f0 = math.sqrt(1.8 * RHO0 * C0 ** 2 * (l1.m + l2.m) / (d * l1.m * l2.m)) / (2 * math.pi)

        def r(f):
            dip = F0_DIP_DB if abs(math.log2(f / f0)) <= 1 / 3 + 1e-9 else 0.0
            return r_double(l1, l2, d, filled, self.conn, f) - dip
        return octave(r)


F0_DIP_DB = 4.0   # ASSUME (Reviewer 3): measured double walls often dip about 4 dB at f0; the central model has none


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
# PM ruling 5 (2026-10-31): use the published absorption, down to 100 Hz, of the felt picked. The pick is the
# factory's 9 mm PET felt (DECIDED, tested in the wall sample), which has no data; Polyx Board 9 is the same
# thickness and mass (9 mm, 1800 g/m2) and publishes ISO 354 data from 100 Hz (type A: no insulation, no air gap).
# One-third octaves 100..5000 Hz read from the vector chart in its data sheet (path coordinates, +/-0.01); they
# give its printed NRC 0.30 and alpha_w 0.25 (H). Source: https://aid.co/wp-content/uploads/2024/10/Polyx-Board-9-No-Insulation-No-Air-Gap.pdf
POLYX9_THIRDS = (0.02, 0.01, 0.00, 0.03, 0.05, 0.09, 0.11, 0.17, 0.24,
                 0.35, 0.40, 0.51, 0.57, 0.66, 0.78, 0.90, 0.95, 0.98)
POLYX9 = tuple(round(sum(POLYX9_THIRDS[3 * i:3 * i + 3]) / 3, 3) for i in range(6))
ALPHA = {
    # The felt sits on the cassette face with a 25 mm gap behind it; the published data has no gap, so the gap's
    # extra absorption at 250-1000 Hz is not counted (conservative). The wall sample measures it down to 100 Hz.
    "felt_gap": POLYX9,
    "felt_direct": POLYX9,
    "cube_gap": (0.05, 0.30, 0.60, 0.95, 0.95, 0.85),        # Autex Cube 12 mm + 25 mm air gap (HW felt row), old proxy
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
LINING_DATA = {   # absorption of the splitter lining layers, 125..4k Hz
    25.0: (0.08, 0.27, 0.48, 0.63, 0.71, 0.75),   # Pyrotek Sorberpoly 2D 25 mm, 32 kg/m3, ISO 354 (HW fill row)
    37.5: (0.12, 0.37, 0.65, 0.77, 0.78, 0.79),   # ASSUME: linear between the 25 and 50 mm data (custom thickness)
    50.0: (0.16, 0.47, 0.82, 0.90, 0.84, 0.83),   # Pyrotek Sorberpoly 2D 50 mm, ISO 354 (HW fill row)
}
# Fix pass (PM rulings 1, 2, 8; 2026-10-31). The decor is 205 mm deep (measured from v1, PM brief; D-39 is
# being corrected), so the 212 mm cartridges and both S&P fans (ØD 221 and 204) no longer fit. New cartridge:
# three 25 mm Pyrotek layers (published data, no interpolation) around two 40 mm passages = 155 mm + casing.
# The space left in front of it, toward the pod, is filled with the walls' 40 mm polyester fill, so casing, fill
# and the decor's inner ACP face act as a filled double wall. Both paths sit side by side in the right decor
# block, which is 1016 mm wide (layout study parts list F-DR 2290 x 1016 x 235); the top block (280 mm) is
# too small for the flow. Supply grille low, exhaust grille high (PM ruling 8).
DECOR_DEPTH = 0.205                     # m, source: PM brief (measured from v1)
DECOR_CLEAR = DECOR_DEPTH - 2 * 0.003   # m inside the 3 mm ACP faces: calculation
SIL_GAP = 0.040                         # m, each air passage
SIL_PS = 2 / SIL_GAP                    # lined perimeter over free area, per metre: calculation
SIL_LINING_MM = 25.0
SIL_LINING_ALPHA = LINING_DATA[SIL_LINING_MM]
SIL_CAP_DB = 40.0                                         # ASSUME: flanking limit per band
SIL_DERATE = 0.8                                          # ASSUME: Sabine formula derated (central case)
# DECIDED (PM, 2026-10-31, after the fix pass): exhaust high. With the slots kept on the top face (D-29), the
# exhaust passage runs down from a high grille to its fans at the foot of the block, which blow up a riser between
# the two cartridges to the slot. The top block can't take the exhaust without a riser (t_fans shows why).
RISER_ON = True
SIL_W = (0.96 - 0.15) / 2               # m, cartridge width: two cartridges and the riser in ~960 mm clear: calculation
RISER = (0.15, 3 * 0.025 + 2 * 0.040, 2.0)   # m: width, depth, length (CAD HOLD)
RISER_KG_M2 = 7850 * 0.0010                  # riser casing, 1.0 mm galvanised steel: calculation
SIL_L = 1.8                             # m of lined passage; plus a 0.3 m fan box at the top
FANBOX_L = 0.3
SIL_PATHS = {   # name: (length m, free area m2, casing face width toward the pod m, depth x width m)
    "supply": (SIL_L, 2 * SIL_GAP * SIL_W, SIL_W, (3 * 0.025 + 2 * SIL_GAP, SIL_W)),
    "exhaust": (SIL_L, 2 * SIL_GAP * SIL_W, SIL_W, (3 * 0.025 + 2 * SIL_GAP, SIL_W)),
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
    """Both cartridges: casing with end caps over the lined passages and the fan box, the 25 mm linings, and the
    polyester fill between each cartridge and the decor's inner face (calculation)."""
    _, mat, t = CASINGS[casing]
    kg_m2 = MAT[mat][0] * t / 1000
    tot = 0.0
    for L, area, b, (dep, wid) in SIL_PATHS.values():
        dep_o = dep + 2 * t / 1000
        tot += (2 * (dep_o + wid) * (L + FANBOX_L) + 2 * dep_o * wid) * kg_m2
        tot += (3 * wid * L + 2 * (wid + dep) * FANBOX_L) * LINING_KG_M3 * SIL_LINING_MM / 1000
        tot += wid * (L + FANBOX_L) * (DECOR_CLEAR - dep_o) * FILL_KG_M3
    return tot


# ---------------------------------------------------------------------------
# The right decor block's real shape (skeleton P03) and the D-60 air parts
# ---------------------------------------------------------------------------
# PR #11 (D-51) sized the air path to the layout study's F-DR box, 2290 x 1016 x 235. Skeleton P03, measured from
# v1, shows the block's glass-side edge following the fixed glass, so a cartridge behind its inner face has about
# 145 mm of width at the foot; its flat top is the 27 mm strip behind the top chamfer. D-60 (PM, 2026-10-31) moves
# the silencers inside the pod: an air column in the front-right corner and a soffit above the door head.
# Skeleton P04 parameters, mm (v2/01-CAD-Native/skeleton/100000_P04_POD-SKELETON-PARAMETERS.csv; the front is
# source, measured from v1's STEP; the 84 mm stack (outer 46 + gap 4 + cassette 34), the right block standing on the
# base band top at Z 110 and the 1495 mm wall depth are decided there; the side lining face X 1166 is a calculation):
SKEL = dict(xr=1250.0, yf=-850.0, decor_d=205.0, fix_xbr=302.0, fix_zb=102.0, fix_xk=501.0, fix_zk=1521.0,
            fix_xtr=1480.0, dt_zb=2120.0, dt_xr=1699.0, dr_xc=198.0, dr_yc=672.0, ch_zlo=2200.0, ch_yb=672.0,
            stack_t=84.0, outer_t=46.0, cass_t=34.0, floor_t=15.0, pod_h=2400.0, dr_zb=110.0, wall_depth=1495.0,
            band_t=40.0, band_h=100.0, glide_h=10.0)
DECOR_SKIN = 3.0   # mm, the decor's ACP faces (D-49: 199 mm clear inside two 3 mm faces)


def dr_edge_x(z):
    """X (mm) of the right block's glass-side edge at height z: the fixed glass's right edge, then its top edge."""
    s = SKEL
    if z <= s["fix_zk"]:
        x0, z0, x1, z1 = s["xr"] - s["fix_xbr"], s["fix_zb"], s["xr"] - s["fix_xk"], s["fix_zk"]
    else:
        x0, z0, x1, z1 = s["xr"] - s["fix_xk"], s["fix_zk"], -s["xr"] + s["fix_xtr"], s["dt_zb"]
    return x0 + (z - z0) * (x1 - x0) / (z1 - z0)


def dr_facet_x(y):
    """X (mm) of the corner facet's inside face at depth y (facet from (xr - dr_xc, yf) to (xr, -dr_yc))."""
    s = SKEL
    dx, dy = s["dr_xc"], s["yf"] * -1 - s["dr_yc"]
    return s["xr"] - dx + (y - s["yf"]) * dx / dy - DECOR_SKIN * math.hypot(dx, dy) / dy


def dr_clear_width(z, depth):
    """Clear width (mm) at height z (below the top block) for a box `depth` mm deep set against the block's inner
    face, between its glass-side face and the corner facet, inside the 3 mm skins (calculation)."""
    s = SKEL
    y_front = s["yf"] + s["decor_d"] - DECOR_SKIN - depth
    return min(dr_facet_x(y_front), s["xr"] - DECOR_SKIN) - (dr_edge_x(z) + DECOR_SKIN)


def dr_volume_m3():
    """Volume inside the right block's skins, m3: plan sections from the skeleton outline, with the top-block joint
    and the top chamfer above Z 2120 (calculation, 2 mm by 5 mm grid)."""
    s = SKEL
    y0, y1 = s["yf"] + DECOR_SKIN, s["yf"] + s["decor_d"] - DECOR_SKIN
    vol = 0.0
    for zi in range(int(s["dr_zb"] + DECOR_SKIN), int(s["pod_h"] - DECOR_SKIN), 5):
        z = zi + 2.5
        area = 0.0
        for yi in range(int(y0), int(y1), 2):
            y = yi + 1.0
            if z > s["ch_zlo"] and y < s["yf"] + (z - s["ch_zlo"]) * (s["yf"] * -1 - s["ch_yb"]) / (s["pod_h"] - s["ch_zlo"]) + DECOR_SKIN:
                continue                                      # cut by the top chamfer
            xl = dr_edge_x(min(z, s["dt_zb"])) + DECOR_SKIN
            if z > s["dt_zb"]:                                # joint to the top block: X 230 at the front to 449
                xj = -s["xr"] + s["fix_xtr"] + (min(y, -s["ch_yb"]) - s["yf"]) * (s["dt_xr"] - s["fix_xtr"]) / (s["yf"] * -1 - s["ch_yb"])
                xl = xj + DECOR_SKIN
            xr = min(dr_facet_x(y), s["xr"] - DECOR_SKIN)
            area += max(0.0, xr - xl) * 2
        vol += area * 5
    return vol * 1e-9


# D-60 air parts (DECIDED by the PM on 2026-10-31; sizes are this calculation). Pod coordinates, mm.
D60 = dict(
    skin=12.0,                       # felt-covered faces: 3 mm ACP + 9 mm felt, as the linings (ASSUME construction)
    fill=27.0,                       # polyester fill between each cartridge and the faces toward the pod (27 mm
                                     # at the column's left face on P04, 29-30 elsewhere; the smallest is used)
    cart=(173.0, 314.0, 1750.0),     # one cartridge size for both paths: casing outer width, stack depth, length
    gap=80.0, ngap=2, lin=50.0,      # two 80 mm passages between three 50 mm Pyrotek Sorberpoly 2D layers (HW fill row)
    col=((949.0, 1166.0), (-645.0, -285.0), (15.0, 2120.0)),         # air column outer: X, Y, Z (P04: 217 wide,
                                                                     # its left face stays behind the block)
    soffit=((-1166.0, 1166.0), (-645.0, -285.0), (2120.0, 2340.0)),  # soffit outer: X, Y, Z
    kick=(25.0, 125.0),              # supply kick grille on the column's front and left faces, Z
    sup_box=((645.0, 945.0), (-847.0, -692.0), (1650.0, 1950.0)),    # supply fan box in the right block
    dr_open=((961.0, 1161.0), (1895.0, 2110.0)),                     # opening in the block's inner face: X, Z
    riser_lo=(139.0, 155.0, 1340.0),  # lower riser behind the column: width, depth, length
    riser_up=(250.0, 155.0, 400.0),   # upper riser and turn into the fan box
    exh_grille=((-1150.0, -885.0), (-633.0, -297.0)),                # on the soffit's underside: X, Y
    exh_box=((867.0, 1161.0), (-640.0, -326.0), (2162.0, 2335.0)),   # exhaust fan box in the soffit's right end
    roof=((872.0, 1157.0), (-630.0, -336.0)),                        # roof slot: X, Y
)
D60_FREE = dict(kick=0.032, intake=0.028, exh_grille=0.036, roof=0.040)   # m2 free areas used (calculation, D60_SIZES)


def band_under_dr_mm():
    """Length (mm) of the front base band under the right block on skeleton P04: its front face from the fixed
    glass's edge to the corner facet, plus the facet (BUILD-RECORD pass D, BAND-FR)."""
    s = SKEL
    return (s["xr"] - s["dr_xc"] - dr_edge_x(s["dr_zb"])) + math.hypot(s["dr_xc"], s["yf"] * -1 - s["dr_yc"])


# Intake routes on skeleton P04 (PM ruling, 2026-10-31: option "mesh", DECIDED). P04 runs the 40 x 100 front band
# flush under the right block and along its facet, so room air can reach the block's underside only through that band
# piece; the 10 mm glide gap under it is all that is open otherwise. Open heights and free ratios: ASSUME.
INTAKE_OPTIONS = (
    ("glide", "The 10 mm glide gap under the band only (skeleton P04 as it is)", SKEL["glide_h"], 1.0),
    ("mesh", "The band piece under the block becomes a flush black mesh with the same outline (DECIDED)", 95.0, 0.80),
    ("short", "The band stops short under the block, with a mesh set back", 90.0, 0.90),
    ("louvre", "A louvred band piece", 80.0, 0.65),
)
D60_INTAKE = "mesh"


def intake_free(key):
    for k, _, h, ratio in INTAKE_OPTIONS:
        if k == key:
            return band_under_dr_mm() * h * ratio / 1e6
    raise KeyError(key)


D60_FREE["intake"] = intake_free(D60_INTAKE)
FRAME_ANGLE_KG_M = 0.26    # aluminium angle 25 x 25 x 2 mm for the column and soffit frames (calculation: 2.7 g/cm3)
CASS_KG_M2 = 7850 * 0.0005 + TRAY_KG_M2 + PET_FELT9_KG_M2   # ceiling lining cassette: 0.5 mm tray, returns, felt


def d60_cartridge_kg(casing="al20"):
    """One D-60 cartridge: casing over the stack, end frames over 30% of each end, three 50 mm layers (calculation)."""
    _, mat, t = CASINGS[casing]
    kg_m2 = MAT[mat][0] * t / 1000
    w, d, L = (x / 1000 for x in D60["cart"])
    sheet = 2 * (w + d) * L + 2 * 0.3 * w * d
    lining = (D60["ngap"] + 1) * D60["lin"] / 1000 * (w - 0.004) * L * LINING_KG_M3
    return sheet * kg_m2 + lining


def d60_parts(casing="al20"):
    """(part, size, kg, basis) for the D-60 air parts; fans are counted apart in fans_kg (calculation)."""
    al = MAT["alu"][0] * 2.0 / 1000
    st = MAT["steel"][0] * 1.0 / 1000
    face = ACP3_KG_M2 + PET_FELT9_KG_M2
    (cx0, cx1), (cy0, cy1), (cz0, cz1) = D60["col"]
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = D60["soffit"]
    w, d, L = (x / 1000 for x in D60["cart"])
    fill = D60["fill"] / 1000
    col_w, col_d, col_h = (cx1 - cx0) / 1000, (cy1 - cy0) / 1000, (cz1 - cz0) / 1000
    sof_l, sof_d, sof_h = (sx1 - sx0) / 1000, (sy1 - sy0) / 1000, (sz1 - sz0) / 1000
    lo_w, lo_d, lo_l = (x / 1000 for x in D60["riser_lo"])
    up_w, up_d, up_l = (x / 1000 for x in D60["riser_up"])
    box = 2 * (0.30 * 0.155 + 0.30 * 0.30 + 0.155 * 0.30)
    ebox = 2 * (0.294 * d + 0.294 * w + d * w)
    rows = [
        ("Supply cartridge, in the air column", f"{D60['cart'][0]:.0f} x {D60['cart'][1]:.0f} x {D60['cart'][2]:.0f}",
         d60_cartridge_kg(casing), f"{CASINGS[casing][0]} casing, three 50 mm layers at {LINING_KG_M3:.0f} kg/m3"),
        ("Exhaust cartridge, in the soffit", "same", d60_cartridge_kg(casing), "same part"),
        ("Air column: felt-covered faces, fill, frame, kick grille, hub plate", f"{col_w*1000:.0f} x {col_d*1000:.0f} x {col_h*1000:.0f}",
         (col_w + col_d) * col_h * face + fill * (w + d) * L * FILL_KG_M3
         + 4 * col_h * FRAME_ANGLE_KG_M + 0.6, "faces 3 mm ACP + 9 mm felt; 30 mm fill; 4 corner angles; 0.6 kg grille and plate (assumption)"),
        ("Soffit: felt-covered faces, fill, frame, exhaust grille", f"{sof_l*1000:.0f} x {sof_d*1000:.0f} x {sof_h*1000:.0f}",
         (sof_d + sof_h) * sof_l * face + fill * (w + d) * L * FILL_KG_M3 + 2 * sof_l * FRAME_ANGLE_KG_M + 0.9,
         "underside and front face as the column; 2 angles; 0.5 kg hangers and 0.4 kg grille (assumption)"),
        ("Supply fan box and transition, in the right block", "300 x 155 x 300 + transition",
         (box + 0.35) * al + 0.6 * 0.050 * LINING_KG_M3, "2 mm aluminium, 50 mm lining; transition 0.35 m2 (calculation)"),
        ("Exhaust fan box and roof sleeve, in the soffit", "294 x 314 x 173",
         (ebox + 0.093) * al + 0.42 * 0.050 * LINING_KG_M3, "2 mm aluminium, 50 mm lining"),
        ("Intake riser with a mesh allowance, in the right block", f"{lo_w*1000:.0f}-{up_w*1000:.0f} x {lo_d*1000:.0f} x {(lo_l+up_l)*1000:.0f}",
         (2 * (lo_w + lo_d) * lo_l + 2 * (up_w + up_d) * up_l) * st + 0.5,
         "1 mm galvanised steel; 0.5 kg for its foot and the mesh band piece's extra over the band it replaces (assumption)"),
        ("Roof slot grille and sleeve", "285 x 294", 0.5, "assumption"),
    ]
    return rows


def d60_air_kg(casing="al20"):
    return sum(r[2] for r in d60_parts(casing))


def d60_ceiling_saving_kg():
    """Ceiling lining the soffit replaces: its depth along the full inner width (calculation)."""
    (sx0, sx1), (sy0, sy1), _ = D60["soffit"]
    return (sx1 - sx0) / 1000 * (sy1 - sy0) / 1000 * CASS_KG_M2


def d60_vents(derate):
    """Speech path through the D-60 vents: [(free area m2, IL per band)] for the two cartridges (calculation)."""
    w, d, L = (x / 1000 for x in D60["cart"])
    area = D60["ngap"] * D60["gap"] / 1000 * (w - 0.004)
    il = [min(1.05 * a ** 1.4 * 2 / (D60["gap"] / 1000) * L * derate, SIL_CAP_DB) for a in LINING_DATA[D60["lin"]]]
    return [(area, il), (area, il)]


def flat(x):
    return [x] * 6


def taus(rb, off=0.0):
    return [10 ** (-(r + off) / 10) for r in rb]


def elements(cfg, sc, wb, gb):
    g = GEOM[cfg["geom"]]
    a = areas(g)
    s = SCEN[sc]
    off = s["r_off"]

    def rr(key):   # the low case carries the 125-250 Hz risks (PM ruling 5)
        return wb[key].r_low() if sc == "low" else wb[key].r()
    el = [("walls", a["walls"], taus(rr(cfg["wall"]), off)),
          ("ceiling", a["ceiling"], taus(rr(cfg.get("ceiling", cfg["wall"])), off)),
          ("glass", a["glass"], taus(gb[cfg["glass"]].r(), off)),
          ("front decor", a["decor"], taus(rr("_DECOR_FILL" if cfg.get("decor_fill") else "_DECOR"), off))]
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
        for area, il in d60_vents(s["sil_derate"]):     # D-60 cartridges (the speech path out through the vents)
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
    ("Silenced vents (D-60: cartridges in the air column and the soffit, intake riser in the right decor block)",
     dict(vents="silenced"), round(d60_air_kg("al20") - d60_ceiling_saving_kg() - 3.0, 1),
     "calculation: the D-60 air parts less the ceiling lining the soffit replaces and the 3 kg in the layout study's rest"),
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


def pod_total_kg(cfg, wb, gb):
    """Whole pod, all light fixes on: rest of pod + wall and ceiling build-ups (with felt, fill, frame) + front."""
    kg = REST_KG + EXTRA_FIX_KG
    kg += wb[cfg["wall"]].kg_m2 * OUT_WALL_M2 + wb[cfg.get("ceiling", cfg["wall"])].kg_m2 * OUT_CEIL_M2
    kg += gb[cfg["glass"]].kg_m2 * GLASS_M2 + FRONT_EXTRA_KG.get(cfg["glass"], 0.0)
    kg += d60_air_kg(cfg.get("casing", "al20")) - d60_ceiling_saving_kg() - 3.0   # D-60 air parts, less the ceiling
                                                        # lining the soffit replaces and the study's 2 x 1.5 kg boxes
    kg += fans_kg() - 3.0                                  # 12 V fans; less the study's 2 x 1.5 kg fans
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

# Duct-side sound power per octave, A-weighted per band, dB(A), 125..4000 Hz (S&P TD SILENT ECOWATT catalogue via
# HW fan rows, duty points read off the curve figure: source, approximate). Kept to show the 5c1003b design.
FAN_BANDS = {
    "S&P TD-350/100-125 ECOWATT, 8 V (69 l/s @ 30 Pa)": dict(
        inlet=(25, 44, 53, 45, 39, 34), outlet=(27, 42, 54, 44, 37, 32), lwa=54, watts=15, kg=5.0),
    "S&P TD-500/150-160 ECOWATT, 4 V (56 l/s @ 42 Pa)": dict(
        inlet=(25, 37, 49, 46, 37, 29), outlet=(25, 37, 49, 46, 37, 29), lwa=51, watts=10, kg=6.0,
        casing=(25, 36, 40, 41, 24, 21)),   # radiated (casing) sound at 4 V, 44 dB(A): same catalogue, as read by
}                                           # Reviewer 3 (source)
TD500 = "S&P TD-500/150-160 ECOWATT, 4 V (56 l/s @ 42 Pa)"


def sys_dp(q_ls, area):
    """Pressure drop of one vent path at q_ls through a splitter of free area `area` (square law)."""
    v = q_ls / 1000 / area
    return SYS_K * 0.5 * RHO0 * v * v


MIX_EFF = 0.8   # PM ruling 8: assumed mixing (ventilation) effectiveness for CO2


def heat_w(people, kit=False):
    return (people * (AIR["sensible_w_person"] + AIR["laptop_w"]) + AIR["lights_w"] + AIR["front_light_w"]
            + AIR["controls_w"] + (AIR["voice_kit_w"] if kit else 0.0))


def co2_rows():
    v = areas(GEOM["v2"])["volume"]
    g = AIR["people"] * AIR["co2_per_person_ls"]
    rows = []
    for q in (26.0, 40.0, 53.0, 70.0):
        rise = g / q * 1e6
        tau_min = v / (q / 1000) / 60
        dt = heat_w(2) / (RHO0 * CP_AIR * q / 1000)
        dt_kit = heat_w(2, True) / (RHO0 * CP_AIR * q / 1000)
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


FAN_SPEED_DB = {"supply": 0.0, "exhaust": 2.5}   # ASSUME (5c1003b design): exhaust path needed a little more speed


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


def fan_noise_old(fan_key, q_ls, derate=SIL_DERATE):
    """The 5c1003b design (212 mm cartridges with 37.5 mm linings in 230-235 mm blocks, TD fans loose in the
    felt-lined cavity), now with the fans' casing sound added (Reviewer 3 P1-1), with today's felt data.
    Returns (duct, breakout + casing, total) dB(A)."""
    room = inside_room_terms()
    fan = FAN_BANDS[fan_key]
    casing_leaf = plate("al20", [layer("alu", 2.0)])
    face = acp()
    flow_db = 50 * math.log10(q_ls / 70.0)
    alpha = LINING_DATA[37.5]
    duct = brk = 0.0
    for name, side, r, L, area in (("supply", "outlet", 1.0, 2.0, 0.050), ("exhaust", "inlet", 1.5, 1.5, 0.028)):
        bands = [x + flow_db + FAN_SPEED_DB[name] for x in fan[side]]
        cas = [x + flow_db + FAN_SPEED_DB[name] for x in fan.get("casing", (-99,) * 6)]
        for i, f in enumerate(BANDS):
            a_db = max(1.05 * alpha[i] ** 1.4 * 40.0 * derate, 0.5)
            duct += 10 ** ((bands[i] - min(a_db * L, SIL_CAP_DB) - end_reflection(f, area) + room(r, i)) / 10)
            k = a_db / 4.343
            tau = 10 ** (-(r_single(casing_leaf, f) + finite_gain(f, 1.0)) / 10)
            w_cav = 10 ** (bands[i] / 10) * tau * (0.5 / area) * (1 - math.exp(-k * L)) / k + 10 ** (cas[i] / 10)
            a_cav = 1.5 * ALPHA["felt_direct"][i] + 0.05      # ASSUME: 1.5 m2 of felt lining in the block
            r_face = r_single(face, f) + finite_gain(f, 0.8)
            brk += 10 ** ((10 * math.log10(w_cav) - r_face + 10 * math.log10(0.8 / a_cav) + room(1.2, i)) / 10)
    return 10 * math.log10(duct), 10 * math.log10(brk), 10 * math.log10(duct + brk)


def old_flow_for(target_dba, fan_key):
    lo, hi = 10.0, 120.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if fan_noise_old(fan_key, mid)[2] > target_dba:
            hi = mid
        else:
            lo = mid
    return lo


# 12 V fans (PM ruling 1: recheck at the new low pressure, use 12 V if it meets both targets). Two per path in
# parallel, on a bulkhead in the cartridge's lined fan box, so no fan casing radiates into the decor cavity:
# the side toward the pod goes down the lined passages, the other side is ducted airtight to the top slot.
G0 = 9.81
FAN12 = {   # Noctua spec page (search result, 2026-10-31): 3000 rpm, 269.3 m3/h, 6.58 mm H2O, 41.3 dB(A)
    "Noctua NF-A14 industrialPPC-3000 PWM": dict(qmax=269.3, pmax=6.58 * G0, lpa=41.3, kg=0.3),  # kg: ASSUME
}
FAN_PICK = "Noctua NF-A14 industrialPPC-3000 PWM"
FAN12_N = 2                 # per path, side by side in the fan box
FAN_ARR = {"supply": "parallel", "exhaust": "parallel"}   # "series" only for the top-block check
LW_FROM_LP = 11.0           # ASSUME: maker's dB(A) taken as sound pressure 1 m away in a free field (Lw = Lp + 11)
SPEED_LAW = 50.0            # dB per decade of speed (fan law; the same law as the flow scaling above)
_td = FAN_BANDS[TD500]["inlet"]
_tot = 10 * math.log10(sum(10 ** (x / 10) for x in _td))
FAN12_REL = tuple(x - _tot for x in _td)   # ASSUME: spectrum shape of the TD-500 (no octave data for 12 V fans)
RISER_K = 1.5   # ASSUME: riser entry and two bends, at the riser's own speed
AIR_CASING = "al20"


def path_dp(name, q_ls):
    _, area, _, _ = SIL_PATHS[name]
    v = q_ls / 1000 / area
    k = SYS_K + (RISER_K * (area / (RISER[0] * RISER[1])) ** 2 if RISER_ON and name == "exhaust" else 0.0)
    return k * 0.5 * RHO0 * v * v


def fan_speed(fan, q_ls, dp, n=FAN12_N):
    """Speed fraction of each of n parallel fans for q_ls at dp, on a straight-line fan curve between the
    published free-air flow and maximum pressure (ASSUME shape), scaled by the fan laws. None if out of reach."""
    qf = q_ls * 3.6 / n

    def p(s):
        return fan["pmax"] * s * s * (1 - qf / (fan["qmax"] * s))
    if p(1.0) < dp:
        return None
    lo, hi = qf / fan["qmax"], 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if p(mid) >= dp:
            hi = mid
        else:
            lo = mid
    return hi


def double_wall_r(casing):
    """R of casing | polyester fill | decor inner ACP face, octaves; ties at 0.6 m points (ASSUME). No
    finite-panel gain here (conservative). Returns (R list, fill depth m)."""
    _, mat, t = CASINGS[casing]
    leaf = plate(casing, [layer(mat, t)])
    d = DECOR_CLEAR - (SIL_PATHS["supply"][3][0] + 2 * t / 1000)
    return octave(lambda f: r_double(leaf, acp(), d, True, ("point", 0.6), f)), d


def breakout_tl(f, kg_m2, a_m, b_m):
    """Breakout TL of a rectangular duct wall: ASHRAE Handbook, HVAC Applications, noise chapter (Cummings):
    10 lg(f q^2 / (a + b)) + 17 below f_L = 24134 / sqrt(a b), else 20 lg(q f) - 31; q in lb/ft2, a and b in
    inches (formula source, not re-checked online). It counts the poor coupling of plane waves to the walls."""
    q = kg_m2 / 4.882
    a, b = a_m / 0.0254, b_m / 0.0254
    if f < 24134 / math.sqrt(a * b):
        return 10 * math.log10(f * q * q / (a + b)) + 17
    return 20 * math.log10(q * f) - 31


def fan12_noise(fan_key, q_ls, casing=AIR_CASING, derate=SIL_DERATE, tone_250=0.0):
    """LpA at a seated head (1.0 m from the supply grille, 1.5 m from the exhaust grille, 1.2 m from the decor
    face) from both paths: the duct path through cartridge and grille, plus breakout toward the pod. Passages:
    ASHRAE duct breakout through the casing alone (the inner face's mass is not counted below f0), then the
    filled double wall's extra loss only in bands fully above f0. Fan box: diffuse field through the double wall.
    Returns (duct, breakout, total, speeds), or None if out of reach."""
    fan = FAN12[fan_key]
    room = inside_room_terms()
    rdw, gap = double_wall_r(casing)
    _, mat, t = CASINGS[casing]
    leaf = plate(casing, [layer(mat, t)])
    rc = octave(lambda f: r_single(leaf, f))
    face = acp()
    f0 = math.sqrt(1.8 * RHO0 * C0 ** 2 * (leaf.m + face.m) / (gap * leaf.m * face.m)) / (2 * math.pi)
    duct = brk = 0.0
    speeds = {}
    for name, r in (("supply", 1.0), ("exhaust", 1.5)):
        L, area, b, (dep, wid) = SIL_PATHS[name]
        dp = path_dp(name, q_ls)
        s = fan_speed(fan, q_ls, dp) if FAN_ARR[name] == "parallel" else fan_speed(fan, q_ls, dp / FAN12_N, 1)
        if s is None:
            return None
        speeds[name] = s
        lw = fan["lpa"] + LW_FROM_LP + SPEED_LAW * math.log10(s) + 10 * math.log10(FAN12_N)
        side = [lw - 3.0 + x + (tone_250 if i == 1 else 0.0) for i, x in enumerate(FAN12_REL)]
        box_lined = 2 * (wid + dep) * FANBOX_L + wid * dep
        s_over_a = 10 * math.log10(2 * (wid + dep) * L / (wid * dep))
        to_pod = 10 * math.log10(wid / (2 * (wid + dep)))          # only the face toward the pod
        tl_min = 10 * math.log10(2 * L * (1 / wid + 1 / dep))
        rw, rd, rl = RISER
        for i, f in enumerate(BANDS):
            a_db = max(1.05 * SIL_LINING_ALPHA[i] ** 1.4 * SIL_PS * derate, 0.5)
            duct += 10 ** ((side[i] - min(a_db * L, SIL_CAP_DB) - end_reflection(f, area) + room(r, i)) / 10)
            kl = a_db * L / 4.343
            mean = (1 - math.exp(-kl)) / kl                          # mean duct power along the lined length
            il_face = max(0.0, rdw[i] - rc[i]) if f / math.sqrt(2) > f0 else 0.0
            tl = max(breakout_tl(f, leaf.m, wid, dep), tl_min)
            lw_pass = side[i] + 10 * math.log10(mean) + s_over_a + to_pod - tl - il_face
            al = SIL_LINING_ALPHA[i]
            lw_box = side[i] + 10 * math.log10(wid * FANBOX_L / (box_lined * al / (1 - al))) - rdw[i]
            w = 10 ** (lw_pass / 10) + 10 ** (lw_box / 10)
            if RISER_ON and name == "exhaust":   # riser: the fans' slot side, unattenuated, behind the same fill and face
                tl_r = max(breakout_tl(f, RISER_KG_M2, rw, rd), 10 * math.log10(2 * rl * (1 / rw + 1 / rd)))
                w += 10 ** ((side[i] + 10 * math.log10(2 * (rw + rd) * rl / (rw * rd))
                             + 10 * math.log10(rw / (2 * (rw + rd))) - tl_r - il_face) / 10)
            brk += w * 10 ** (room(1.2, i) / 10)
    return 10 * math.log10(duct), 10 * math.log10(brk), 10 * math.log10(duct + brk), speeds


def fan12_flow_for(target_dba, fan_key=FAN_PICK, casing=AIR_CASING, tone_250=0.0):
    """Highest flow at or under target_dba that the fans can reach."""
    lo, hi = 10.0, 150.0
    for _ in range(50):
        mid = (lo + hi) / 2
        res = fan12_noise(fan_key, mid, casing, tone_250=tone_250)
        if res is None or res[2] > target_dba:
            hi = mid
        else:
            lo = mid
    return lo


def fans_kg(fan_key=FAN_PICK):
    return len(SIL_PATHS) * FAN12_N * FAN12[fan_key]["kg"]


def riser_kg():
    return 2 * (RISER[0] + RISER[1]) * RISER[2] * RISER_KG_M2 if RISER_ON else 0.0


# ---------------------------------------------------------------------------
# Air paths built from parts (D-60 recheck). The same methods as fan12_noise, with each part's own size, so layouts
# on the real right block can be compared. A path has the fans, the parts between the fans and the grille inside
# the pod ("pod"), and the parts between the fans and the opening to the room ("room"). Sound inside comes from the
# duct path through the "pod" parts and the grille, and from breakout of every part that faces the pod.
# ---------------------------------------------------------------------------
BEND_K = 0.8     # ASSUME: rectangular 90 degree bend, no turning vanes, at its own speed
GRILLE_K = 2.0   # PR #11's inside diffuser and outside grille (SYS_K), each at its own free-area speed
DUCT_F = 0.02    # ASSUME: friction factor of a smooth sheet-metal duct


def part(kind, length, wid, dep, gap=SIL_GAP, ngap=2, lin=25.0, face=True, fill=0.040, bends=0, wall="al20",
         free=None, ps=None, rad=None):
    """One part of an air path, m. kind "split": ngap passages of `gap` between layers `lin` mm thick, passages
    `wid` wide, `dep` the stack depth; "lined": a duct lined on its walls, with its free area and lined perimeter over
    free area `ps` per metre; "plain": an unlined duct. face: it faces the pod; fill: the gap (m) between its wall and
    the face toward the pod (filled with polyester if 20 mm or more); rad: its width radiating toward the pod
    (default wid); wall: a CASINGS key."""
    _, mat, t = CASINGS[wall]
    p = dict(kind=kind, L=length, wid=wid, dep=dep, gap=gap, ngap=ngap, lin=lin, face=face, fill=fill, bends=bends,
             wall=wall, kg_m2=MAT[mat][0] * t / 1000, rad=rad or wid)
    if kind == "split":
        p["free"], p["ps"] = ngap * gap * wid, 2 / gap
    elif kind == "lined":
        p["free"], p["ps"] = free, ps
    else:
        p["free"], p["ps"] = free or wid * dep, 0.0
    return p


def part_il(p, derate):
    if p["kind"] == "plain":
        return [0.0] * 6
    return [min(1.05 * a ** 1.4 * p["ps"] * p["L"] * derate, SIL_CAP_DB) for a in LINING_DATA[p["lin"]]]


def part_k(p):
    """Loss coefficient at the part's own free-area speed. A splitter takes PR #11's entry 0.5, exit 1.0 and 2.0
    per 1.8 m of 40 mm passages, scaled by length over passage width (calculation from SYS_K)."""
    if p["kind"] == "split":
        return 0.5 + 1.0 + 2.0 * p["L"] / 1.8 * 0.040 / p["gap"] + BEND_K * p["bends"]
    if p["kind"] == "lined":
        return 0.5 + 1.0 + 2.0 * p["L"] / 1.8 + BEND_K * p["bends"]
    return DUCT_F * p["L"] * (p["wid"] + p["dep"]) / (2 * p["wid"] * p["dep"]) + BEND_K * p["bends"]


def leaf_of(wall):
    _, mat, t = CASINGS[wall]
    return plate(wall, [layer(mat, t)])


def wall_pair_r(wall, gap):
    """R of a part's wall | gap | the felt-covered face toward the pod (ACP 3 mm), octaves, and f0 (Sharp, ties at
    0.6 m points as in double_wall_r; the gap is filled if 20 mm or more)."""
    w = leaf_of(wall)
    face = acp()
    r = octave(lambda f: r_double(w, face, gap, gap >= 0.020, ("point", 0.6), f))
    f0 = math.sqrt(1.8 * RHO0 * C0 ** 2 * (w.m + face.m) / (gap * w.m * face.m)) / (2 * math.pi)
    return r, f0


def path_dp12(path, q_ls):
    dp = 0.0
    for p in path["pod"] + path["room"]:
        v = q_ls / 1000 / p["free"]
        dp += part_k(p) * 0.5 * RHO0 * v * v
    for k, area in path.get("extra", ()):
        v = q_ls / 1000 / area
        dp += k * 0.5 * RHO0 * v * v
    for area in (path["grille"], path["opening"]):
        v = q_ls / 1000 / area
        dp += GRILLE_K * 0.5 * RHO0 * v * v
    return dp


def path_noise12(path, q_ls, derate=SIL_DERATE, tone_250=0.0, fan_key=FAN_PICK):
    """(duct, breakout, total dB(A), fan speed, pressure Pa) at a seated head, or None if out of the fans' reach."""
    fan = FAN12[fan_key]
    room = inside_room_terms()
    dp = path_dp12(path, q_ls)
    s = fan_speed(fan, q_ls, dp)
    if s is None:
        return None
    lw = fan["lpa"] + LW_FROM_LP + SPEED_LAW * math.log10(s) + 10 * math.log10(FAN12_N)
    side = [lw - 3.0 + x + (tone_250 if i == 1 else 0.0) for i, x in enumerate(FAN12_REL)]
    cum = [0.0] * 6
    for p in path["pod"]:
        cum = [c + x for c, x in zip(cum, part_il(p, derate))]
    duct = sum(10 ** ((side[i] - min(cum[i], 2 * SIL_CAP_DB) - end_reflection(f, path["grille"])
                       + room(path["r"], i)) / 10) for i, f in enumerate(BANDS))
    rf = path.get("r_face", 1.2)
    brk = 0.0
    for chain in (path["pod"], path["room"]):
        cum = [0.0] * 6
        for p in chain:
            if p["face"]:
                rdw, f0 = wall_pair_r(p["wall"], max(p["fill"], 0.005))
                rc = octave(lambda f: r_single(leaf_of(p["wall"]), f))
                rate = [max(1.05 * a ** 1.4 * p["ps"] * derate, 0.5) for a in LINING_DATA[p["lin"]]]
                for i, f in enumerate(BANDS):
                    kl = rate[i] * p["L"] / 4.343
                    mean = 1.0 if p["kind"] == "plain" else (1 - math.exp(-kl)) / kl
                    il_face = max(0.0, rdw[i] - rc[i]) if f / math.sqrt(2) > f0 else 0.0
                    tl = max(breakout_tl(f, p["kg_m2"], p["wid"], p["dep"]),
                             10 * math.log10(2 * p["L"] * (1 / p["wid"] + 1 / p["dep"])))
                    lwb = (side[i] - cum[i] + 10 * math.log10(mean) + 10 * math.log10(p["rad"] * p["L"] / (p["wid"] * p["dep"]))
                           - tl - il_face)
                    brk += 10 ** ((lwb + room(rf, i)) / 10)
            cum = [c + x for c, x in zip(cum, part_il(p, derate))]
    bx = path.get("box")
    if bx:   # lined fan box, reverberant, behind a filled double wall (as fan12_noise)
        rdw, _ = wall_pair_r("al20", bx["fill"])
        lined = 2 * (bx["wid"] + bx["dep"]) * bx["h"] + bx["wid"] * bx["dep"]
        al = LINING_DATA[bx["lin"]]
        for i in range(6):
            lwb = side[i] + 10 * math.log10(bx["rad_area"] / (lined * al[i] / (1 - al[i]))) - rdw[i]
            brk += 10 ** ((lwb + room(rf, i)) / 10)
    return 10 * math.log10(duct), 10 * math.log10(brk), 10 * math.log10(duct + brk), s, dp


def layout_noise12(paths, q_ls, **kw):
    """Both paths at the same flow: (duct, breakout, total dB(A), [speeds], [Pa], [path totals]) or None."""
    res = [path_noise12(p, q_ls, **kw) for p in paths]
    if any(r is None for r in res):
        return None
    tot = [10 * math.log10(sum(10 ** (r[k] / 10) for r in res)) for k in range(3)]
    return tot[0], tot[1], tot[2], [r[3] for r in res], [r[4] for r in res], [r[2] for r in res]


def layout_flow_for(paths, target_dba, **kw):
    """Highest flow at or under target_dba that the fans can reach."""
    lo, hi = 10.0, 150.0
    for _ in range(50):
        mid = (lo + hi) / 2
        r = layout_noise12(paths, mid, **kw)
        if r is None or r[2] > target_dba:
            hi = mid
        else:
            lo = mid
    return lo


# Layouts compared on the real right block. Sizes in m; widths from dr_clear_width for a 159 mm cartridge set
# against the inner face, less 5 mm each side (calculation). The top strip slot: 21 mm clear (27 mm strip less two
# skins) x 790 mm (X 452 to 1244), 75% free, 0.0124 m2 (calculation). Left block: a 100 mm deep box against its
# inner face is 189 mm wide, a lined duct of 0.0135 m2 free (calculation from skeleton P03). Top block: its section
# is 0.030 to 0.038 m2 inside the skins; lined 25 mm, 0.017 m2 free, P/S 33 per m (calculation).
TOP_STRIP_FREE = 0.021 * 0.790 * 0.75
CART_D = 3 * 0.025 + 2 * SIL_GAP          # PR #11's 155 mm stack


def col_w(z0, z1):
    """Mean clear width (m) of a 159 mm cartridge in the right block's column between z0 and z1, 5 mm each side."""
    return (dr_clear_width(z0, 159) + 2 * dr_clear_width((z0 + z1) / 2, 159) + dr_clear_width(z1, 159)) / 4000 - 0.010


def layouts():
    lo, up = col_w(110, 700), col_w(700, 1300)
    column = [part("split", 0.59, lo, CART_D, fill=0.005), part("split", 0.60, up, CART_D, fill=0.005)]
    to_strip = part("plain", 0.2, 0.30, 0.12, fill=0.005, free=0.030)
    sup_box = dict(wid=0.31, dep=0.155, h=0.30, fill=0.005, lin=25.0, rad_area=0.31 * 0.30)
    exh_box = dict(wid=0.30, dep=0.155, h=0.20, fill=0.005, lin=25.0, rad_area=0.30 * 0.20)

    def sup(pod_parts, room_parts=column, grille=0.03, opening=0.025):
        return dict(pod=pod_parts, room=room_parts, box=sup_box, grille=grille, opening=opening, r=1.0)
    a = [sup([part("split", 0.45, 0.39, CART_D, fill=0.005)]),
         dict(pod=[part("split", 0.45, 0.26, CART_D, fill=0.005)], room=[to_strip], box=exh_box,
              grille=0.0225, opening=TOP_STRIP_FREE, r=1.5)]
    b = [sup([part("split", 0.65, 0.40, CART_D, fill=0.005), part("split", 0.45, 0.26, CART_D, fill=0.005, bends=2)]),
         dict(pod=[part("lined", 1.55, 0.18, 0.10, fill=0.005, free=0.0135, ps=1 / 0.075 + 2 / 0.18)],
              room=[part("plain", 1.6, 0.16, 0.12, fill=0.005, free=0.017, bends=2), to_strip], box=exh_box,
              grille=0.0225, opening=TOP_STRIP_FREE, r=1.5)]
    dt_exh = dict(pod=[part("lined", 1.25, 0.20, 0.16, fill=0.005, free=0.017, ps=33.0, bends=1)], room=[to_strip],
                  box=exh_box, grille=0.0225, opening=TOP_STRIP_FREE, r=1.5)
    c = [sup([part("split", 0.55, 0.40, CART_D, fill=0.005), part("split", 0.30, 0.26, CART_D, fill=0.005, bends=2)]),
         dt_exh]
    c_roof = [sup([part("split", 0.35, 0.40, CART_D, fill=0.005), part("split", 0.30, 0.30, CART_D, fill=0.005, bends=2)],
                  [part("lined", 1.3, 0.25, 0.17, fill=0.005, free=0.040, ps=6.25, bends=1)], opening=0.030),
              dict(dt_exh, grille=0.03, opening=0.05)]
    pr11 = [dict(pod=[part("split", SIL_L, SIL_W, CART_D)], room=[], grille=2 * SIL_GAP * SIL_W,
                 opening=2 * SIL_GAP * SIL_W, r=1.0, box=dict(wid=SIL_W, dep=CART_D, h=FANBOX_L, fill=0.040, lin=25.0,
                                                               rad_area=SIL_W * FANBOX_L)),
            dict(pod=[part("split", SIL_L, SIL_W, CART_D)], room=[part("plain", RISER[2], RISER[0], RISER[1], wall="st10")],
                 grille=2 * SIL_GAP * SIL_W, opening=2 * SIL_GAP * SIL_W, r=1.5, extra=((RISER_K, RISER[0] * RISER[1]),),
                 box=dict(wid=SIL_W, dep=CART_D, h=FANBOX_L, fill=0.040, lin=25.0, rad_area=SIL_W * FANBOX_L))]
    return dict(a=a, b=b, c=c, c_roof=c_roof, pr11=pr11, d60=d60_paths())


def d60_paths(casing="al20"):
    """D-60 as sized here: supply up the riser in the right block, through its fans, down the air column's cartridge
    to the kick grille; exhaust from the soffit's far-end grille along its cartridge to its fans and the roof slot."""
    w, d, L = (x / 1000 for x in D60["cart"])
    gap, n, lin = D60["gap"] / 1000, D60["ngap"], D60["lin"]
    fill = D60["fill"] / 1000
    lo_w, lo_d, lo_l = (x / 1000 for x in D60["riser_lo"])
    up_w, up_d, up_l = (x / 1000 for x in D60["riser_up"])
    supply = dict(
        pod=[part("split", L, w - 0.004, d - 0.004, gap=gap, ngap=n, lin=lin, fill=fill, rad=w + d, bends=1, wall=casing)],
        room=[part("plain", lo_l, lo_w, lo_d, fill=fill, free=(lo_w - 0.002) * (lo_d - 0.002), wall="st10"),   # behind the column
              part("plain", up_l, up_w, up_d, fill=0.005, free=(up_w - 0.002) * (up_d - 0.002), bends=2, wall="st10")],
        box=dict(wid=0.30, dep=0.155, h=0.30, fill=0.040, lin=50.0, rad_area=0.30 * 0.30),
        grille=D60_FREE["kick"], opening=D60_FREE["intake"], r=1.0)
    exhaust = dict(
        pod=[part("split", L, w - 0.004, d - 0.004, gap=gap, ngap=n, lin=lin, fill=fill, rad=w + d, bends=1, wall=casing)],
        room=[part("plain", 0.10, 0.285, 0.294, face=False)],
        box=dict(wid=0.294, dep=d, h=w, fill=fill, lin=50.0, rad_area=0.294 * (d + w)),
        grille=D60_FREE["exh_grille"], opening=D60_FREE["roof"], r=1.5)
    return [supply, exhaust]


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
            ("Light 0.8 mm cartridge casings (rejected: misses the fan-noise target, section 7d)", dict(base, **dict(DECIDED_STACK, casing="al08")))]
    for label, cfg in rows:
        kg = pod_total_kg(cfg, wb, gb)
        b = band(cfg, wb, gb)
        out.append(row([label, cfg["wall"], cfg["ceiling"], gb[cfg["glass"]].name, CASINGS[cfg["casing"]][0],
                        f"{kg:.0f}", " / ".join(f"{x:.1f}" for x in b)]))
    return "\n".join(out), rows


def t_air():
    rows, v, g = co2_rows()
    out = [f"Inside volume {v:.2f} m3; CO2 from 2 people {g * 1000:.1f} ml/s. The last column uses a mixing "
           f"effectiveness of {MIX_EFF} (PM ruling 8); the others assume perfect mixing.", "",
           "| Fresh air l/s | Air changes /h | Minutes per change | CO2 rise ppm | CO2 ppm, room 400 | CO2 ppm, room 600 | Minutes to 95% | Heat rise K | Heat rise K with voice kit | CO2 ppm, room 600, mixing 0.8 |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for q, ach, mins, rise, c4, c6, t95, dt, dtk in rows:
        out.append(row([f"{q:.0f}", f"{ach:.0f}", f"{mins:.1f}", f"{rise:.0f}", f"{c4:.0f}", f"{c6:.0f}",
                        f"{t95:.0f}", f"{dt:.1f}", f"{dtk:.1f}", f"{600 + rise / MIX_EFF:.0f}"]))
    k4 = RHO0 * CP_AIR * 4.0 / 1000
    one = 600 + AIR["co2_per_person_ls"] / 26.0 * 1e6 / MIX_EFF
    out.append("")
    out.append(f"Flow that keeps the inside 4 K or less over the room: one person {heat_w(1) / k4:.0f} l/s, two people "
               f"{heat_w(2) / k4:.0f} l/s, two with the voice-kit reserve {heat_w(2, True) / k4:.0f} l/s. One person at the "
               f"26 l/s floor (D-44), room 600, mixing 0.8: {one:.0f} ppm.")
    out.append(f"CO2 after 2 h at 40 l/s from 400 ppm (room 400): {co2_after(40, 120, 400, 400):.0f} ppm; "
               f"after 3 h at 26 l/s, room 600: {co2_after(26, 180, 600, 600):.0f} ppm.")
    return "\n".join(out)


def t_fans():
    out = ["| Fans and cartridges (PR #11, right block taken as a box) | Fits the real right block | Fans kg | Cartridges, fill, riser kg | At 53 l/s: fan speed supply / exhaust | At 53 l/s: duct / breakout / total dB(A) | Boost flow at 30 dB(A) l/s | At 70 l/s: total dB(A) |",
           "|---|---|---:|---:|---|---|---:|---:|"]
    a, b = fan_noise_old(TD500, 53.0), fan_noise_old(TD500, 70.0)
    out.append(row(["2 x S&P TD-500/150-160 SILENT, 4 V, as at 5c1003b, with casing sound", "no (ØD 221 mm)", "12.0",
                    "29.8", "4 V", " / ".join(f"{x:.1f}" for x in a), f"{old_flow_for(30.0, TD500):.0f}", f"{b[2]:.1f}"]))
    global SIL_W, SIL_PATHS, RISER_ON, FAN_ARR
    keep = (SIL_W, SIL_PATHS, RISER_ON, FAN_ARR)
    dep = keep[1]["supply"][3][0]

    def paths(ws, we, le=SIL_L):
        return {"supply": (SIL_L, 2 * SIL_GAP * ws, ws, (dep, ws)), "exhaust": (le, 2 * SIL_GAP * we, we, (dep, we))}
    cases = (
        ("Exhaust high with a riser: exhaust fans at the foot, 150 mm steel riser, 405 mm cartridges (D-51, replaced by D-60)",
         "al20", 0.0, dict(riser=True, w=(keep[0], keep[0]), le=SIL_L, arr="parallel", fits="no: needs 960 mm")),
        ("Same, with a 5 dB fan tone at 250 Hz (risk)", "al20", 5.0,
         dict(riser=True, w=(keep[0], keep[0]), le=SIL_L, arr="parallel", fits="no: needs 960 mm")),
        ("Both grilles low, no riser, 450 mm cartridges (not chosen: exhaust low)", "al20", 0.0,
         dict(riser=False, w=(0.45, 0.45), le=SIL_L, arr="parallel", fits="no: needs 900 mm")),
        ("Exhaust in the top block, no riser: 266 mm wide, 1.35 m, two fans in series (they can't sit side by side)",
         "al20", 0.0, dict(riser=False, w=(0.45, 0.266), le=1.35, arr="series", fits="no: the top block is 119 to 199 mm deep")))
    for label, ck, tone, v in cases:
        SIL_W, RISER_ON = v["w"][0], v["riser"]
        SIL_PATHS = paths(v["w"][0], v["w"][1], v["le"])
        FAN_ARR = {"supply": "parallel", "exhaust": v["arr"]}
        r53 = fan12_noise(FAN_PICK, 53.0, ck, tone_250=tone)
        r70 = fan12_noise(FAN_PICK, 70.0, ck, tone_250=tone)
        kg = cartridge_kg(ck) + riser_kg()
        if r53 is None:
            cells = ["out of reach", "out of reach"]
        else:
            cells = [f"{r53[3]['supply'] * 100:.0f}% / {r53[3]['exhaust'] * 100:.0f}%", " / ".join(f"{x:.1f}" for x in r53[:3])]
        out.append(row([label, v["fits"], f"{fans_kg():.1f}", f"{kg:.1f}"] + cells +
                       [f"{fan12_flow_for(30.0, FAN_PICK, ck, tone):.0f}", f"{r70[2]:.1f}" if r70 else "out of reach"]))
        SIL_W, SIL_PATHS, RISER_ON, FAN_ARR = keep
    return "\n".join(out)


def path_max_flow(path):
    """Highest flow (l/s) the path's fan pair reaches at full speed."""
    lo, hi = 10.0, 200.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if fan_speed(FAN12[FAN_PICK], mid, path_dp12(path, mid)) is None:
            hi = mid
        else:
            lo = mid
    return lo


def t_silencer():
    """The D-60 cartridge, both paths, with each casing."""
    w, d, L = (x / 1000 for x in D60["cart"])
    il = part_il(d60_paths()[0]["pod"][0], SIL_DERATE)
    out = ["| Cartridge casing | Air parts kg | Passage IL 125 | 250 | 500 | 1k | 2k | 4k dB | Casing + 30 mm fill + felt-covered face R 125 | 250 | 500 | 1k | 2k | 4k dB | At 53 l/s dB(A) | Flow at 30 dB(A) l/s |",
           "|---|---:|" + "---:|" * 14]
    for ck in ("al20", "al08"):
        rdw, _ = wall_pair_r(ck, D60["fill"] / 1000)
        paths = d60_paths(ck)
        r = layout_noise12(paths, 53.0)
        out.append(row([CASINGS[ck][0] + (" (pick)" if ck == AIR_CASING else ""), f"{d60_air_kg(ck):.1f}"]
                       + [f"{x:.0f}" for x in il] + [f"{x:.0f}" for x in rdw]
                       + [f"{r[2]:.1f}" if r else "out of reach", f"{layout_flow_for(paths, 30.0):.0f}"]))
    sup, exh = d60_paths()
    out.append("")
    out.append("Pressure per path, supply / exhaust: " + "; ".join(
        f"{q:.0f} l/s {path_dp12(sup, q):.0f} / {path_dp12(exh, q):.0f} Pa" for q in (26, 53, 65))
        + f". At full speed the supply pair reaches {path_max_flow(sup):.0f} l/s and the exhaust pair "
          f"{path_max_flow(exh):.0f} l/s.")
    return "\n".join(out)


def t_dr():
    """The right decor block's clear section by height (skeleton P03)."""
    out = ["| Height Z mm | Glass-side edge X mm | Clear width for a 159 mm deep cartridge mm | Clear width at the full 199 mm depth mm | Inner face seen from inside mm |",
           "|---:|---:|---:|---:|---:|"]
    for z in (115, 500, 1000, 1521, 1800, 2117):
        out.append(row([f"{z}", f"{dr_edge_x(z):.0f}", f"{dr_clear_width(z, 159):.0f}", f"{dr_clear_width(z, 199):.0f}",
                        f"{SKEL['xr'] - SKEL['stack_t'] - dr_edge_x(z):.0f}"]))
    need = 2 * (CART_D + 0.004) * SIL_W * (SIL_L + FANBOX_L) + RISER[0] * RISER[1] * RISER[2]
    out.append("")
    out.append(f"Inside its skins the block holds {dr_volume_m3():.2f} m3. Its flat top is the strip from Y "
               f"-{SKEL['ch_yb']:.0f} to -{SKEL['yf'] * -1 - SKEL['decor_d']:.0f}, "
               f"{SKEL['ch_yb'] - (SKEL['yf'] * -1 - SKEL['decor_d']):.0f} mm deep; the rest of the top is the "
               f"chamfer. PR #11's layout needs {(2 * SIL_W + RISER[0]) * 1000:.0f} mm of width over "
               f"{(SIL_L + FANBOX_L) * 1000:.0f} mm, {need:.2f} m3 with the fan boxes and riser.")
    return "\n".join(out)


LAYOUT_ROWS = (
    ("pr11", "PR #11 (D-51), taking the right block as a 1016 x 2290 box",
     "two 405 mm cartridges and a riser in the block: doesn't fit"),
    ("a", "(a) right block only", "supply up the block's column; exhaust in its upper part, out the 27 mm top strip"),
    ("b", "(b) right and left blocks", "supply in the right block; exhaust up the left block and across the top block"),
    ("c", "(c) right and top blocks", "supply in the right block; exhaust along the top block"),
    ("c_roof", "(c) improved, exhaust out a roof slot: the best inside the decor",
     "as (c), with the column as a plain duct and bigger openings"),
    ("d60", "(e) D-60 as sized here", "an air column in the front-right inside corner and a soffit above the door head"),
)


def t_layouts():
    out = ["| Layout | Where the air path runs | At 53 l/s dB(A) | At 65 l/s dB(A) | At 33 l/s dB(A) | Flow at 26 dB(A) l/s | Flow at 30 dB(A) l/s | Fan speed at 53 l/s, supply / exhaust |",
           "|---|---|---:|---:|---:|---:|---:|---|"]
    lay = layouts()
    for key, label, where in LAYOUT_ROWS:
        paths = lay[key]
        r53, r65, r33 = (layout_noise12(paths, q) for q in (53.0, 65.0, 33.0))
        cell = lambda r: "out of reach" if r is None else f"{r[2]:.1f}"
        speed = "out of reach" if r53 is None else " / ".join(f"{x:.0%}" for x in r53[3])
        out.append(row([label, where, cell(r53), cell(r65), cell(r33), f"{layout_flow_for(paths, 26.0):.0f}",
                        f"{layout_flow_for(paths, 30.0):.0f}", speed]))
    return "\n".join(out)


def t_d60():
    """D-60 noise inside, path by path."""
    paths = d60_paths()
    out = ["| Flow l/s | Supply fans: speed, pressure | Supply duct / breakout / total dB(A) | Exhaust fans: speed, pressure | Exhaust duct / breakout / total dB(A) | Inside, both paths dB(A) |",
           "|---:|---|---|---|---|---:|"]
    for q in (26.0, 33.0, 53.0, 65.0, 70.0):
        res = [path_noise12(p, q) for p in paths]
        cells = []
        for r in res:
            cells += (["out of reach", ""] if r is None else
                      [f"{r[3]:.0%}, {r[4]:.0f} Pa", " / ".join(f"{x:.1f}" for x in r[:3])])
        tot = layout_noise12(paths, q)
        out.append(row([f"{q:.0f}"] + cells + ["out of reach" if tot is None else f"{tot[2]:.1f}"]))
    t53 = layout_noise12(paths, 53.0, tone_250=5.0)
    one = []
    for q in (53.0, 65.0):
        ds, de = path_dp12(paths[0], q), path_dp12(paths[1], q)
        one.append(((ds - de) / 2, fan_speed(FAN12[FAN_PICK], q, (ds + de) / 2)))
    r = layout_noise12(paths, 53.0)
    out.append("")
    out.append(f"Two fan signals keep both paths at the same flow: at 53 l/s the supply pair runs at {r[3][0]:.0%} and the "
               f"exhaust pair at {r[3][1]:.0%}. One shared signal would run both at about {one[0][1]:.0%} and leave the pod "
               f"{one[0][0]:.1f} Pa below the room at 53 l/s ({one[1][0]:.1f} Pa at 65 l/s).")
    out.append(f"Flow at 26 dB(A): {layout_flow_for(paths, 26.0):.0f} l/s; at 30 dB(A): {layout_flow_for(paths, 30.0):.0f} l/s "
               f"(targets, D-52: 26 dB(A) or less at 53 l/s, 30 or less at the 65 l/s boost). With a 5 dB fan tone at "
               f"250 Hz (risk): {t53[2]:.1f} dB(A) at 53 l/s and {layout_flow_for(paths, 30.0, tone_250=5.0):.0f} l/s at 30 dB(A).")
    return "\n".join(out)


def t_intake():
    """Intake routes on skeleton P04 (PM ruling: the mesh)."""
    out = ["| Intake route | Free area m2 | Speed at 53 l/s m/s | At 53 l/s dB(A) | At 65 l/s dB(A) | Flow at 30 dB(A) l/s |",
           "|---|---:|---:|---:|---:|---:|"]
    keep = D60_FREE["intake"]
    for key, label, _, _ in INTAKE_OPTIONS:
        D60_FREE["intake"] = intake_free(key)
        paths = d60_paths()
        r53, r65 = layout_noise12(paths, 53.0), layout_noise12(paths, 65.0)
        cell = lambda r: "out of reach" if r is None else f"{r[2]:.1f}"
        out.append(row([label, f"{D60_FREE['intake']:.4f}", f"{0.053 / D60_FREE['intake']:.1f}", cell(r53), cell(r65),
                        f"{layout_flow_for(paths, 30.0):.0f}"]))
    D60_FREE["intake"] = keep
    out.append("")
    out.append(f"The band piece under the block is {band_under_dr_mm():.0f} mm long (skeleton P04). Open heights and free "
               f"ratios are assumptions until the mesh is picked.")
    return "\n".join(out)


def t_d60_parts(wb, gb):
    out = ["| Part | Size mm | kg | Basis |", "|---|---|---:|---|"]
    rows = d60_parts()
    for name, size, kg, basis in rows:
        out.append(row([name, size, f"{kg:.1f}", basis]))
    fans = fans_kg()
    air = d60_air_kg() + fans
    old = cartridge_kg("al20") + riser_kg() + fans
    save = d60_ceiling_saving_kg()
    out.append(row(["Four 12 V fans", "140 x 140 x 25", f"{fans:.1f}", "0.3 kg each (assumption)"]))
    out.append(row(["**Air parts in all**", "", f"**{air:.1f}**", "heaviest part under the 20 kg rule: "
                    f"{max(r[2] for r in rows):.1f} kg"]))
    out.append(row(["Less the ceiling lining the soffit replaces", f"{(D60['soffit'][0][1] - D60['soffit'][0][0]):.0f} x "
                    f"{(D60['soffit'][1][1] - D60['soffit'][1][0]):.0f}", f"-{save:.1f}", "0.5 mm tray, returns and felt"]))
    out.append(row(["Less PR #11's cartridges, fill, riser and fans", "", f"-{old:.1f}", "the model's earlier air parts"]))
    out.append(row(["**Change to the pod**", "", f"**{air - save - old:+.1f}**", "the DECIDED stack in this model goes "
                    f"to {pod_total_kg(dict(dict(PLAN, **FIX_ALL), **DECIDED_STACK), wb, gb):.0f} kg"]))
    return "\n".join(out)


def t_d60_sizes():
    """The size table for the CEILING and FRONT Engineers (D-60): pod coordinates, mm."""
    D = D60
    w, d, L = D["cart"]
    (cx0, cx1), (cy0, cy1), (cz0, cz1) = D["col"]
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = D["soffit"]
    sk, fl, cl = D["skin"], D["fill"], 5.0
    cart_x = (cx1 - cl - w, cx1 - cl)
    cart_y = (cy0 + cl, cy0 + cl + d)
    cart_z = (D["kick"][1] + 10, D["kick"][1] + 10 + L)
    (bx0, bx1), (by0, by1), (bz0, bz1) = D["sup_box"]
    (ox0, ox1), (oz0, oz1) = D["dr_open"]
    lo_w, lo_d, lo_l = D["riser_lo"]
    up_w, up_d, up_l = D["riser_up"]
    (gx0, gx1), (gy0, gy1) = D["exh_grille"]
    (ex0, ex1), (ey0, ey1), (ez0, ez1) = D["exh_box"]
    (rx0, rx1), (ry0, ry1) = D["roof"]
    kick_len = (cx1 - cx0 - 2 * sk) + (cy1 - cy0 - 2 * sk)
    ex_cart_x = (ex0 - L, ex0)
    ex_cart_z = (sz0 + sk + fl, sz0 + sk + fl + w)
    riser_x0 = dr_edge_x(SKEL["dr_zb"]) + DECOR_SKIN + 5
    f = lambda a, b: f"{a:.0f} to {b:.0f}"
    rows = [
        ("Air column, outer", f"{cx1 - cx0:.0f} x {cy1 - cy0:.0f} x {cz1 - cz0:.0f}",
         f"X {f(cx0, cx1)}, Y {f(cy0, cy1)}, Z {f(cz0, cz1)}",
         f"front and left faces felt-covered ({sk:.0f} mm: 3 mm ACP + 9 mm felt); the front face lifts off full height for "
         f"service; back on the right block's inner face, right side on the side lining"),
        ("Supply cartridge", f"{w:.0f} x {d:.0f} x {L:.0f}, {d60_cartridge_kg():.1f} kg",
         f"X {f(*cart_x)}, Y {f(*cart_y)}, Z {f(*cart_z)}",
         f"2 mm aluminium casing; two {D['gap']:.0f} mm passages running up and down between three {D['lin']:.0f} mm "
         f"Pyrotek Sorberpoly 2D layers parallel to the front face; {fl:.0f} mm polyester fill to the front and left "
         f"faces; {cl:.0f} mm clear on the other sides to slide it out"),
        ("Kick grille, supply out", f"{D['kick'][1] - D['kick'][0]:.0f} tall x {kick_len:.0f} along the front and left faces",
         f"Z {f(*D['kick'])}", f"{D60_FREE['kick']:.3f} m2 free or more (60%); base plenum Z {f(cz0, cart_z[0])} under "
         f"the cartridge"),
        ("Opening from the right block into the column top", f"{ox1 - ox0:.0f} x {oz1 - oz0:.0f}",
         f"in the block's inner face at X {f(ox0, ox1)}, Z {f(oz0, oz1)}",
         f"supply air from the fan box; column top plenum Z {f(cart_z[1], cz1)}"),
        ("Sensor hub and controls", "180 x 180 zone, up to 29 deep",
         f"on the column's front face, centred X {(cx0 + cx1) / 2:.0f}, Z 1200",
         "no fill behind it; a 30 x 30 mm cable chase in the column's front-left corner runs up to the top plenum and on "
         "to the fans; the supply fan inlet sensor (D-50) sits in the fan box inlet"),
        ("Supply fans and box", f"{bx1 - bx0:.0f} x {by1 - by0:.0f} x {bz1 - bz0:.0f}",
         f"X {f(bx0, bx1)}, Y {f(by0, by1)}, Z {f(bz0, bz1)}, inside the right block",
         "two Noctua NF-A14 industrialPPC-3000 PWM on a level bulkhead, blowing up; 2 mm aluminium, 50 mm lining; 44 mm "
         "fill to the block's inner face, which lifts off here (D-59); a transition carries the air right to the opening"),
        ("Intake riser", f"{lo_w:.0f} to {up_w:.0f} wide x {lo_d:.0f} deep x {lo_l + up_l:.0f}",
         f"X {riser_x0:.0f} to {riser_x0 + lo_w:.0f}, Y {SKEL['yf'] + SKEL['decor_d'] - DECOR_SKIN - lo_d:.0f} to "
         f"{SKEL['yf'] + SKEL['decor_d'] - DECOR_SKIN:.0f}, Z 105 to {105 + lo_l:.0f}, behind the column; then it widens "
         f"and turns into the fan box inlet below Z {bz0:.0f}",
         "1 mm galvanised steel, 0.021 m2 free or more"),
        ("Intake (FRONT and BASE)", f"band piece {band_under_dr_mm():.0f} long x {SKEL['band_h']:.0f} tall",
         f"the front base band under the right block: its front face from X {dr_edge_x(SKEL['dr_zb']):.0f} to "
         f"{SKEL['xr'] - SKEL['dr_xc']:.0f} and along the corner facet, Z {SKEL['glide_h']:.0f} to {SKEL['dr_zb']:.0f}",
         f"a flush black mesh with the band's outline, 80% free over 95 mm, {D60_FREE['intake']:.3f} m2 free (PM, "
         f"2026-10-31); the block gets its own support behind it (BASE); a closing plate at Y -645 from Z 15 to "
         f"{SKEL['dr_zb']:.0f} separates the space under the block from the pod; the riser opens down into that space"),
        ("Soffit, outer", f"{sx1 - sx0:.0f} x {sy1 - sy0:.0f} x {sz1 - sz0:.0f}",
         f"X {f(sx0, sx1)}, Y {f(sy0, sy1)}, Z {f(sz0, sz1)}",
         f"underside and front face felt-covered, front face flush with the column's; the underside lifts off in sections; "
         f"the ceiling lining cassettes start at Y {sy1:.0f} ({SKEL['wall_depth'] - SKEL['stack_t'] - (sy1 - sy0):.0f} long); headroom {sz0:.0f}, "
         f"as the door head"),
        ("Exhaust grille", f"{gx1 - gx0:.0f} x {gy1 - gy0:.0f}", f"soffit underside, X {f(gx0, gx1)}, Y {f(gy0, gy1)}",
         f"{D60_FREE['exh_grille']:.3f} m2 free or more (40%)"),
        ("Exhaust cartridge", "same part, lying along X", f"X {f(*ex_cart_x)}, Y {f(*cart_y)}, Z {f(*ex_cart_z)}",
         "passages along X; fill and clearances as the column"),
        ("Exhaust fans and box", f"{ex1 - ex0:.0f} x {ey1 - ey0:.0f} x {ez1 - ez0:.0f}",
         f"X {f(ex0, ex1)}, Y {f(ey0, ey1)}, Z {f(ez0, ez1)}, the soffit's right end",
         "two NF-A14 lying flat, blowing up into the roof sleeve; 2 mm aluminium, 50 mm lining"),
        ("Roof slot (CEILING)", f"{rx1 - rx0:.0f} x {ry1 - ry0:.0f}",
         f"through the roof panel above the exhaust box, X {f(rx0, rx1)}, Y {f(ry0, ry1)}",
         f"sleeve through the {SKEL['pod_h'] - SKEL['outer_t'] - sz1:.0f} mm gap and the {SKEL['outer_t']:.0f} mm roof panel; grille 50% free or more, {D60_FREE['roof']:.3f} m2 free; "
         f"{(SKEL['pod_h'] - SKEL['dr_zb']) / 1000:.1f} m above the intake"),
        ("Clearances", "", "", "5 mm round each cartridge and fan box; door top Z 2116 to the soffit 4 mm, so check the "
         f"door's swing; the soffit top, Z {sz1:.0f}, is {SKEL['pod_h'] - SKEL['outer_t'] - sz1:.0f} mm under the roof panel"),
    ]
    out = ["| Item | Size mm | Where (pod coordinates, mm) | Notes |", "|---|---|---|---|"]
    out += [row(list(r)) for r in rows]
    return "\n".join(out)


GLASS_Y = -699.0   # mm, the door and fixed glass mid-plane (skeleton glass_y, source: v1 STEP)


def soffit_view(eye_z, dist):
    """For a viewer outside, eye at eye_z mm, dist mm in front of the glass: the band of glass height (Z mm) through
    which the soffit's underside shows, and how deep (Y) into it the view reaches. The glass top is at Z 2119 and the
    top block's underside, flush with the soffit's, runs at Z 2120 from the glass back to Y -645 (calculation)."""
    (_, _), (sy0, sy1), (sz0, _) = D60["soffit"]
    def z_glass(y_hit):   # height where the sight line to (y_hit, sz0) crosses the glass plane
        return eye_z + (sz0 - eye_z) * dist / (dist + (y_hit - GLASS_Y))
    lo, hi = z_glass(sy1), min(z_glass(sy0), SKEL["dt_zb"] - 1)
    return lo, hi


def t_soffit_view():
    out = ["| Viewer outside | Glass band that shows the soffit's underside, Z mm | Glass height showing it mm |", "|---|---|---:|"]
    for eye, label in ((1650.0, "standing"), (1200.0, "seated")):
        for dist in (1000.0, 2000.0, 4000.0):
            lo, hi = soffit_view(eye, dist)
            out.append(row([f"{label}, eye {eye:.0f} mm, {dist / 1000:.0f} m from the glass", f"{lo:.0f} to {hi:.0f}", f"{hi - lo:.0f}"]))
    return "\n".join(out)


def t_recirc():
    """Recirculation check (D-58, ISS-078): numbers for the method in report section 7f."""
    q = 0.065
    r_cap = math.sqrt(q / (math.pi * 0.1))
    (cx0, cx1), (cy0, cy1), _ = D60["col"]
    (gx0, gx1), (gy0, gy1) = D60["exh_grille"]
    inside = math.sqrt(((cx0 + cx1) / 2 - (gx0 + gx1) / 2) ** 2 + (cy1 - (gy0 + gy1) / 2) ** 2
                       + (D60["soffit"][2][0] - sum(D60["kick"]) / 2) ** 2) / 1000
    rows = [
        ("Intake to roof slot, height apart", f"{(SKEL['pod_h'] - SKEL['dr_zb']) / 1000:.2f} m",
         f"Z {SKEL['dr_zb']:.0f} to {SKEL['pod_h']:.0f} (skeleton P04); D-58 asks 1 m or more"),
        ("Intake capture distance at 65 l/s, where its pull falls to 0.1 m/s", f"{r_cap:.2f} m",
         "quarter-sphere sink at the floor and the pod's front, v = Q / (pi r^2); 0.1 m/s room air (assumption)"),
        ("Exhaust leaving the roof slot at 65 l/s", f"{q / D60_FREE['roof']:.1f} m/s, upward", f"{D60_FREE['roof']:.3f} m2 free"),
        ("Exhaust over the room at boost", "4 K or less", "D-50 holds the inside within 4 K of the room"),
        ("Largest recirculated share that keeps the inlet within 0.5 K", f"{0.5 / 4.0:.1%}", "0.5 K / 4 K (D-58's test limit)"),
        ("Supply kick grille to exhaust grille, inside the pod", f"{inside:.1f} m", "short-circuit inside the pod"),
    ]
    out = ["| Check | Value | Basis |", "|---|---|---|"]
    out += [row(list(r)) for r in rows]
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
    out["dr"] = t_dr()
    out["layouts"] = t_layouts()
    out["d60"] = t_d60()
    out["silencer"] = t_silencer()
    out["d60_parts"] = t_d60_parts(wb, gb)
    out["intake"] = t_intake()
    out["d60_sizes"] = t_d60_sizes()
    out["soffit_view"] = t_soffit_view()
    out["recirc"] = t_recirc()
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
