"""Mass helpers. All lengths in mm, masses in kg."""
import math

from inputs import p


def rhs_area_mm2(b, h, t):
    """Cross-section of a rectangular hollow section with square corners (slightly conservative)."""
    return 2 * t * (b + h) - 4 * t * t


def rhs_kgm(b, h, t, rho):
    """kg per metre of a rectangular hollow section."""
    return rhs_area_mm2(b, h, t) * 1e-6 * rho


def chs_kgm(d, t, rho):
    """kg per metre of a round tube."""
    return math.pi * (d - t) * t * 1e-6 * rho


def plate_kg(area_m2, t_mm, rho):
    return area_m2 * t_mm * 1e-3 * rho


def steel_rhs(b, h, t):
    return rhs_kgm(b, h, t, p("rho_steel"))


def al_rhs(b, h, t):
    return rhs_kgm(b, h, t, p("rho_al"))


def frame_length_mm(w, h, pitch):
    """Perimeter plus intermediate members across the short side, spaced along the long side.

    A layout-level estimate: the CAD sets the real members. Returns total member length in mm.
    """
    long_side, short_side = max(w, h), min(w, h)
    bays = max(1, math.ceil(long_side / pitch))
    return 2 * (w + h) + (bays - 1) * short_side
