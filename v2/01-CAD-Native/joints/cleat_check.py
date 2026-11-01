#!/usr/bin/env python3
"""Frame cleat check for J-FRAME-01 (D-115, D-116, D-117): sizes, masses, glue and metal use, counts.

    python3 v2/01-CAD-Native/joints/cleat_check.py           # prints the tables the joints register quotes
    python3 v2/01-CAD-Native/joints/cleat_check.py --check   # also checks every design rule; exits 1 on a failure

Units: mm, N, MPa, g. Every input below carries its status (conventions §9): confirmed, source, calculation,
assumption or unverified. The joints register (v2/05-Engineering/joints/joints-register.md, J-FRAME-01) quotes the
printed tables, and joints_cleats_build.py reads its sizes and masses from here, so the models and the register
can't drift apart; if an input changes, rerun this, update the register from its output and rebuild the models.

The model, in short:
- Demand: the heaviest bare frame (C1, 3.410 kg) handled before its skin is bonded. In plane: its weight on half
  its length, x2 for handling and x1.5 margin, at one corner (D-117's basis, with C1 in place of the 3.3 kg L1).
  Out of plane: the frame held flat by one member, the far side carried by the two corners at that member's ends.
- A corner cleat is an L cut from a hollow extrusion (walls t), its L in the frame's plane, cut to depth d across
  the frame. Each leg sits in its tube's bore with a glue line on its two side faces (the faces toward the tube's
  40 mm walls). In-plane bending runs through each leg as a couple in its two side walls, lever w - t; the inner
  wall's force passes to the tube through the glue over the leg's length L: tau = M / ((w - t) * L * d).
- The leg's own strength: the two side walls, W = (w - t) * t * d, at fy / gamma_M1.
- Out of plane: the mitre faces bear on the compression side and the cleat carries the tension, lever about half
  the bore plus half the wall.
- A T joint is pinned: a plug glued and crimped into the stud's end puts a tongue through a slot in the rail's
  bay-side wall; it locates the stud and carries shear. The studs are held between the rails, which the corners
  tie, so a T joint carries no pull-out or moment.
"""
import math
import sys

G = 9.81

# --- demand ------------------------------------------------------------------------------------------------
FRAMES_KG = {  # bare frame masses, calculation (CAD geometry x density) as each team's parts list gives them
    "411101 C1": 3.410,  # v2/03-Manufacturing/ceiling/410000_P01_CEILING-PARTS-LIST_BOM.csv
    "411102 C2": 3.407,
    "211103 L2": 3.262,  # v2/03-Manufacturing/wall/210103_P01_..._BOM.csv (R2 the same)
    "211101 L1": 3.105,  # v2/03-Manufacturing/wall/210101_P01_..._BOM.csv (R1 the same)
}
FRAME_LONG = 1495.0        # C1's length along Y, calculation (skeleton P04 via CEILING's parts list)
FRAME_SHORT = 1198.99      # C1's width, the frame width at the closing seam (R-J16), calculation
MEMBER_KG_M = {"20x40x1.2": 2.70e-3 * (2 * (20 + 40) * 1.2 - 4 * 1.2 ** 2),   # 0.373 kg/m, calculation
               "40x40x1.2": 2.70e-3 * (4 * 40 * 1.2 - 4 * 1.2 ** 2)}          # 0.503 kg/m, calculation
HANDLING = 2.0             # dynamic factor for handling a bare frame, assumption (D-117)
MARGIN = 1.5               # margin on top, assumption (D-117)

M_FRAME = max(FRAMES_KG.values())
M_REQ = M_FRAME * G * FRAME_LONG / 2 * HANDLING * MARGIN                    # N*mm, in plane
# out of plane: held flat by the 1199 back member; the rest hangs off the two corners at its ends, lever half
# of the 1495 sides (the T joints are pinned, so the corners carry it all)
M_OOP_REQ = (M_FRAME - MEMBER_KG_M["40x40x1.2"] * FRAME_SHORT / 1000) * G * FRAME_LONG / 2 / 2 * HANDLING * MARGIN

# --- materials ---------------------------------------------------------------------------------------------
TAU_TYP = 10.0     # MPa, SikaFast-5215 NT and -5211 NT lap shear, ISO 4587, 1.5 mm glue line, 23 C (source: PDS)
GAP_MIN, GAP_MAX = 0.5, 3.0   # mm, the glue line the PDS allows (source)
ETA_PICK = 0.71    # glue use at M_REQ for the chosen cleats (D-116, D-117: "the glue at 71%")
ETA_FALLBACK = 0.50  # glue use for the heavier fallback, if T14 shows 71% too close (D-117)
FY = 215.0         # MPa, cleat design yield: assumption (EN 755-2 gives 225 for 6005A-T6 open profiles to 5 mm
                   # and 240 for 6061-T6 tubes, source; hollow profiles taken at 215 until the extruder's
                   # certificate gives the figure)
GAMMA_M1 = 1.10    # material factor, EN 1999-1-1 recommended value, assumption until checked against the edition
RHO = 2.70e-3      # g/mm3, 6005A and 6061, source
T = 1.0            # mm, cleat walls, assumption: HOLD-20 asks the extruder for its minimum
FY_TUBE = 170.0    # MPa, 6063-T6 profiles to 10 mm, EN 755-2 minimum (source), for the slot's bearing

# --- fit ---------------------------------------------------------------------------------------------------
BORES = {"20x40x1.2": 17.6, "20x40x1.0": 18.0, "40x40x1.2": 37.6}   # in-plane bore, calculation from nominal sizes
GAP_NOM = 1.0      # mm, nominal glue line each side, assumption (inside 0.5-3.0 with room for the tube tolerance)
RIB = 0.6          # mm, spacer ribs on each glue face, 1.0 wide, 2 per face: set the smallest glue line, assumption
W_NARROW = BORES["20x40x1.2"] - 2 * GAP_NOM    # 15.6
W_WIDE = BORES["40x40x1.2"] - 2 * GAP_NOM      # 35.6
RIB_W = 1.0        # mm, rib width, assumption
NOTCH_L, NOTCH_W, NOTCH_D = 6.0, 2.0, 1.0   # mm: a crimp boss rib-high and NOTCH_L long, with a notch NOTCH_W wide
                                            # and NOTCH_D deep from its top (0.4 into the wall), assumption
WEB = 1.0          # mm, the T plug's middle web, assumption
NOTCH_AREA = NOTCH_L * RIB - NOTCH_W * NOTCH_D   # net area each boss adds, calculation
RIB_AREA = RIB * RIB_W


def fit_range(w):
    """Bores the leg fits with every glue line inside the PDS's 0.5-3.0: it enters over its ribs with 0.1 to
    spare, and the far glue line, with the ribs on the other side touching, stays at 3.0 or less."""
    return w + 2 * RIB + 0.1, w + RIB + GAP_MAX


OOP_LEVER = 37.6 / 2 + 1.2 / 2   # 19.4, calculation


# --- the cleats --------------------------------------------------------------------------------------------
class Corner:
    """A hollow L corner cleat: leg A of width wa runs La past the corner square, leg B of width wb runs Lb."""

    def __init__(self, pn, name, wa, wb, La, Lb, d):
        self.pn, self.name, self.wa, self.wb, self.La, self.Lb, self.d = pn, name, wa, wb, La, Lb, d

    def area(self):
        """The profile as modelled (joints_cleats_build.py): the hollow L (outer L less the L offset T inside),
        the web on the corner's diagonal (the part inside the chamber), 8 ribs, 2 crimp bosses less notches."""
        wa, wb, La, Lb = self.wa, self.wb, self.La, self.Lb
        outer = wa * (wb + La) + wb * Lb
        inner = (wa - 2 * T) * (wb + La - 2 * T) + (wb - 2 * T) * Lb
        diag = math.hypot(wa - T, wb - T)        # the web runs between the walls' mid-lines at both corners
        cx, cy = (wb - T) / diag, (wa - T) / diag
        inside = diag - T / 2 / min(cx, cy) - T / 2 / max(cx, cy)   # less the lengths inside the walls
        return outer - inner + inside * T + 8 * RIB_AREA + 2 * NOTCH_AREA

    def mass(self):
        return self.area() * self.d * RHO

    def tau(self, M):
        """Glue shear on each leg's inner face at moment M (N*mm): the higher of the two legs."""
        return max(M / ((self.wa - T) * self.La * self.d), M / ((self.wb - T) * self.Lb * self.d))

    def m_rd(self):
        """The narrower leg's strength in plane, N*mm."""
        return (min(self.wa, self.wb) - T) * T * self.d * FY / GAMMA_M1

    def oop(self, M):
        """Out of plane: the mitre faces bear across one 40 mm face's wall and the cleat, at mid-depth, carries
        the tension; lever half the 37.6 bore depth plus half the wall (every member is 40 deep). Returns the
        leg's stress in its two walls and the glue shear on the shorter leg's two faces."""
        F = M / OOP_LEVER
        return F / (2 * T * self.d), F / (2 * min(self.La, self.Lb) * self.d)

    def glue_ml(self):
        """Glue to fill both glue faces of both legs (inner face L, outer face L + the other leg's width) at the
        nominal line, plus the mitre faces at 0.5 (the tube walls' section along the mitre)."""
        faces = (2 * self.La + self.wb) * self.d + (2 * self.Lb + self.wa) * self.d
        mitre = 2 * (20 + 40) * 1.2 * math.sqrt(2) * 0.5
        return (faces * GAP_NOM + mitre) / 1000


def size_corner(pn, name, wa, wb, d, eta):
    """The shortest whole-mm legs that keep the glue at eta of its typical strength at M_REQ."""
    La = math.ceil(M_REQ / ((wa - T) * d * eta * TAU_TYP))
    Lb = math.ceil(M_REQ / ((wb - T) * d * eta * TAU_TYP))
    return Corner(pn, name, wa, wb, La, Lb, d)


CORNERS = [
    size_corner("831003", "corner 20 x 40 to 20 x 40, 45°", W_NARROW, W_NARROW, 28, ETA_PICK),
    size_corner("831005", "corner 40 x 40 to 20 x 40, 26.57° and 63.43°", W_WIDE, W_NARROW, 28, ETA_PICK),
    size_corner("831004", "corner 40 x 40 to 40 x 40, 45°", W_WIDE, W_WIDE, 20, ETA_PICK),
]
FALLBACKS = [  # D-117: the heavier cleats if T14 shows the glue at 71% too close
    size_corner("831003", "corner 20 x 40 to 20 x 40, glue at 50%", W_NARROW, W_NARROW, 32, ETA_FALLBACK),
    size_corner("831005", "corner 40 x 40 to 20 x 40, glue at 50%", W_WIDE, W_NARROW, 32, ETA_FALLBACK),
]


class Plug:
    """The T plug: a hollow box W_NARROW wide and Ls long in the stud (walls T, one middle web), with a solid
    tongue tw thick and tl long that goes through the rail's 1.2 wall into its bore; cut to depth d."""

    def __init__(self, pn, Ls=20.0, tw=6.0, tl=6.0, d=20.0):
        self.pn, self.Ls, self.tw, self.tl, self.d = pn, Ls, tw, tl, d

    def area(self):
        """The profile as modelled: the box and tongue less two chambers (walls T, a WEB in the middle on the
        tongue's line), 4 ribs, 2 crimp bosses (one on each glue face, so it goes in either way) less notches."""
        outer = W_NARROW * self.Ls + self.tw * self.tl
        chambers = 2 * (self.Ls - 2 * T) * (W_NARROW - 2 * T - WEB) / 2
        return outer - chambers + 4 * RIB_AREA + 2 * NOTCH_AREA

    def mass(self):
        return self.area() * self.d * RHO

    def slot(self):
        """The slot in the rail's bay-side wall: the tongue plus the nominal glue line all round."""
        return self.tw + 2 * GAP_NOM, self.d + 2 * GAP_NOM

    def bearing(self, V):
        """Bearing stress on the rail's 1.2 wall at shear V (N), across the face (the ceiling's case) and along
        the rail, if the glue in the slot has let go."""
        return V / (self.tw * 1.2), V / (self.d * 1.2)

    def glue_ml(self):
        in_stud = 2 * self.Ls * self.d * GAP_NOM
        slot = 2 * (self.tw + self.d) * 1.2 * GAP_NOM
        end = (2 * (20 + 40) * 1.2 + 2 * (W_NARROW + self.d) * T) * 0.5     # stud and plug ends on the rail face
        return (in_stud + slot + end) / 1000


PLUG = Plug("831006")
V_T = 300.0   # N, T joint shear to carry: 3 x the highest end reaction, about 0.1 kN on the ceiling's X1 with a
              # soffit hanger (about 5.5 kg) and two cassette clips (about 3.3 kg), assumption on the masses
GLUE_DENSITY = 1.19e-3 * 1000   # g/ml mixed, source (PDS)

# --- counts per frame: the joint count on WALL's and CEILING's models on main (B3, B4 mirror B1, B2) ---------
FRAME_COUNTS = {
    "211101 L1": {"831003": 2, "831005": 2, "831006": 6},
    "211102 R1": {"831003": 2, "831005": 2, "831006": 6},
    "211103 L2": {"831003": 1, "831005": 2, "831004": 1, "831006": 6},
    "211104 R2": {"831003": 1, "831005": 2, "831004": 1, "831006": 6},
    "211201 B1": {"831003": 4, "831006": 4},
    "211202 B2": {"831003": 4, "831006": 4},
    "211203 B3": {"831003": 4, "831006": 4},
    "211204 B4": {"831003": 4, "831006": 4},
    "411101 C1": {"831003": 2, "831005": 2, "831006": 6},
    "411102 C2": {"831003": 2, "831005": 2, "831006": 6},
}


def per_pod():
    out = {}
    for counts in FRAME_COUNTS.values():
        for pn, n in counts.items():
            out[pn] = out.get(pn, 0) + n
    return out


def report():
    print("Demand (calculation): heaviest bare frame %.3f kg; in plane %.1f N*m; out of plane %.1f N*m"
          % (M_FRAME, M_REQ / 1000, M_OOP_REQ / 1000))
    print("Fit: narrow legs %.1f wide, %.1f over the ribs, fit bores %.1f to %.1f; wide legs %.1f, fit %.1f to %.1f"
          % ((W_NARROW, W_NARROW + 2 * RIB) + fit_range(W_NARROW) + (W_WIDE,) + fit_range(W_WIDE)))
    print()
    print("| Part | Cleat | Legs (mm) | Depth | Mass (g) | Glue at M_req | Leg strength | Out of plane: leg, glue |")
    print("|---|---|---|---:|---:|---:|---:|---|")
    for c in CORNERS + FALLBACKS:
        legs = "%.1f x %d and %.1f x %d" % (c.wa, c.La, c.wb, c.Lb)
        s, g = c.oop(M_OOP_REQ)
        print("| %s | %s | %s | %d | %.1f | %.2f MPa (%.0f%%) | %.1f N·m | %.0f MPa, %.1f MPa |"
              % (c.pn, c.name, legs, c.d, c.mass(), c.tau(M_REQ), 100 * c.tau(M_REQ) / TAU_TYP, c.m_rd() / 1000, s, g))
    sw, sl = PLUG.slot()
    b1, b2 = PLUG.bearing(V_T)
    print("| %s | T plug | box %.1f x %.0f in the stud, tongue %.0f x %.0f | %.0f | %.1f | slot %.0f x %.0f | bearing at %.1f kN: %.0f and %.0f MPa (6063-T6 %.0f) | — |"
          % (PLUG.pn, W_NARROW, PLUG.Ls, PLUG.tw, PLUG.tl, PLUG.d, PLUG.mass(), sw, sl, V_T / 1000, b1, b2, FY_TUBE))
    print()
    pod = per_pod()
    unit = {c.pn: c for c in CORNERS}
    unit[PLUG.pn] = PLUG
    total_g = total_ml = 0.0
    print("| Part | Per pod | Mass each (g) | Mass per pod (kg) | Glue each (ml) |")
    print("|---|---:|---:|---:|---:|")
    for pn in ("831003", "831004", "831005", "831006"):
        u = unit[pn]
        total_g += pod[pn] * u.mass()
        total_ml += pod[pn] * u.glue_ml()
        print("| %s | %d | %.1f | %.3f | %.1f |" % (pn, pod[pn], u.mass(), pod[pn] * u.mass() / 1000, u.glue_ml()))
    print("| cleats | %d | | %.3f | |" % (sum(pod.values()), total_g / 1000))
    print("| glue, 108003 | %.0f ml | | %.3f | |" % (total_ml, total_ml * GLUE_DENSITY / 1000))
    print("| **in all** | | | **%.2f** | |" % ((total_g + total_ml * GLUE_DENSITY) / 1000))
    print()
    print("| Frame | 831003 | 831004 | 831005 | 831006 |")
    print("|---|---:|---:|---:|---:|")
    for f, counts in FRAME_COUNTS.items():
        print("| %s | %s |" % (f, " | ".join(str(counts.get(pn, 0)) for pn in ("831003", "831004", "831005", "831006"))))
    print("| per pod | %s |" % " | ".join(str(pod[pn]) for pn in ("831003", "831004", "831005", "831006")))


def check():
    bad = []
    if not (60e3 < M_REQ < 90e3 and 10e3 < M_OOP_REQ < M_REQ):
        bad.append("demand out of its expected range: %.1f and %.1f N*m" % (M_REQ / 1000, M_OOP_REQ / 1000))
    pod = per_pod()
    if sum(pod[pn] for pn in ("831003", "831004", "831005")) != 40 or pod["831006"] != 52:
        bad.append("counts: want 40 corners and 52 T joints per pod, got %s" % pod)
    for c in CORNERS:
        if c.tau(M_REQ) > ETA_PICK * TAU_TYP + 1e-9:
            bad.append("%s: glue at %.2f MPa, over %.0f%%" % (c.pn, c.tau(M_REQ), 100 * ETA_PICK))
        if c.m_rd() < M_REQ:
            bad.append("%s: leg strength %.1f N*m under %.1f" % (c.pn, c.m_rd() / 1000, M_REQ / 1000))
        s, g = c.oop(M_OOP_REQ)
        if s > FY / GAMMA_M1 or g > ETA_PICK * TAU_TYP:
            bad.append("%s: out of plane, leg %.0f MPa or glue %.1f MPa too high" % (c.pn, s, g))
        if c.mass() > 20.0:
            bad.append("%s: %.1f g, over D-115's 20 g" % (c.pn, c.mass()))
    for f in FALLBACKS:   # only if T14 calls for them (D-117); over 20 g is the PM's call then, so a note
        if f.tau(M_REQ) > ETA_FALLBACK * TAU_TYP + 1e-9 or f.d > 37.6 - 2 * GAP_MIN:
            bad.append("fallback %s: glue %.2f MPa or %d deep" % (f.pn, f.tau(M_REQ), f.d))
        elif f.mass() > 20.0:
            print("note: the 50%% fallback %s is %.1f g, over D-115's 20 g: the PM rules if T14 calls for it"
                  % (f.pn, f.mass()))
    for name, bore in BORES.items():
        w = W_WIDE if bore > 30 else W_NARROW
        lo, hi = fit_range(w)
        if not lo <= bore <= hi:
            bad.append("%s bore %.1f outside the leg's fit range %.1f-%.1f" % (name, bore, lo, hi))
        if not (GAP_MIN <= RIB and bore - w - RIB <= GAP_MAX):
            bad.append("%s: glue line outside %.1f-%.1f" % (name, GAP_MIN, GAP_MAX))
    b1, b2 = PLUG.bearing(V_T)
    if max(b1, b2) > FY_TUBE / GAMMA_M1:
        bad.append("T plug: bearing %.0f MPa over the tube's %.0f" % (max(b1, b2), FY_TUBE / GAMMA_M1))
    sw, sl = PLUG.slot()
    if (40 - sl) / 2 < 8.0:
        bad.append("T slot %.0f across a 40 face leaves under 8 mm each side" % sl)
    if PLUG.mass() > 9.0:
        bad.append("T plug %.1f g, over D-117's 9 g" % PLUG.mass())
    return bad


if __name__ == "__main__":
    report()
    if "--check" in sys.argv:
        problems = check()
        print("\n" + ("NOT OK:\n  " + "\n  ".join(problems) if problems else "OK: every design rule holds"))
        sys.exit(1 if problems else 0)
