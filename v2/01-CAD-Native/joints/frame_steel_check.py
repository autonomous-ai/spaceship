#!/usr/bin/env python3
"""Steel frame check for J-FRAME-01 (D-131): gauges, steel grade, masses, the corner lift, seam bolts, rivnuts, welds.

    python3 v2/01-CAD-Native/joints/frame_steel_check.py           # print the tables the joints register quotes
    python3 v2/01-CAD-Native/joints/frame_steel_check.py --check   # also check every rule; exit 1 on a failure

D-131 (PM ruling 2026-11-01): the wall and ceiling frames become welded, galvanized steel box tube with the same
outside sections, 20 x 40 and 40 x 40, so every hole, rivnut and joint position stays. Start gauges: 1.0 mm for the
perimeters and every member that takes a rivnut, 0.8 mm for inner members if the check allows. D-135 (the same day):
every wall bay under the ACP 275 mm clear or less, so the side panels get 5 studs and the back panels 3; the ceiling
keeps its spacing. PM ruling the same day, for margin against under-gauge tube and weak welds: 1.2 mm for the side
panels' rails and front stiles (L1, L2 and their mirrors), and every frame at 90% or less at the thinnest wall.

Units: mm, N, MPa, kg. Every input carries its status (conventions section 9): confirmed, source, calculation,
assumption or unverified. The joints register (v2/05-Engineering/joints/joints-register.md, J-FRAME-01) quotes the
printed tables; if an input changes, rerun this and update the register from its output.

The model, in short (D-117's load cases, which the PM accepted for the cleats, applied to welded steel):
- Corner lift, in plane: the bare frame handled before its skin is bonded, its weight on half its long side, x2 for
  handling and x1.5 margin, at one corner. The corner's two members carry it all (welded T joints only help).
- Out of plane: the frame held flat by one short member, the rest carried by the two corners at its ends; at a
  corner that moment is bending in one member and torsion in the other, so the lower of the two governs.
- Resistance: EN 1993-1-1's section classes from the walls' c/t, with EN 1993-1-3's core thickness (the nominal
  wall less its zinc). Plastic modulus for class 1 and 2, elastic for 3, effective for 4 (EN 1993-1-5, the
  compression wall's effective width). Checked at the nominal wall and at the thinnest wall the spec accepts.
- Seam bolts and rivnuts: the joints' highest bolt loads (J-T1's basis) against the wall's pull-through round the
  rivnut's bulge and the bolt's bearing in its hole; the rivnut's own strength is shown by test (T06, J-T1).
- Corners: mitred, with a plate welded into each mitre. A plain mitre is a knee joint whose kinked walls carry less
  than the tube: EN 1993-1-8's knee rule (valid from 2.5 mm walls, so only an indication here) gives
  kappa = 3 / sqrt(b0/t0) + 1 / (1 + 2 b0/h0) of the tube's moment. A plate at least 1.5 t thick in the mitre makes it a
  stiffened knee that carries the tube's moment. The weld coupons (J-T7) prove it.
- Welds: a full-perimeter fillet round each stud end (T joint) against the T joints' shear.
"""
import glob
import importlib.util
import math
import os
import sys

G = 9.81
RHO = 7.85e-6                    # kg/mm3, steel (source: EN 1991-1-1 Table A.4, 77 to 78.5 kN/m3)
# (name, fy, fu) in MPa, the standards' minimums (source). ACCEPTED: the grades the spec allows (yield 280 or more);
# the others are shown to say why they aren't.
ACCEPTED = (
    ("S280GD+Z, EN 10346", 280.0, 360.0),
    ("SGC400, JIS G3302", 295.0, 400.0),
)
NOT_ACCEPTED = (
    ("S250GD+Z, EN 10346", 250.0, 330.0),
    ("STKR400, JIS G3466", 245.0, 400.0),
    ("S235JRH, EN 10219-1", 235.0, 360.0),
)
ZINC = 0.014          # mm, both faces' zinc at Z100 (EN 10346; 100 g/m2 at 7.14 g/cm3, calculation), the coating the
                      # PM confirmed for every frame (indoors); taken off the wall for strength (EN 1993-1-3 3.2.4)
WALL_MIN = 0.95       # the thinnest wall accepted, as a share of the nominal, measured through the zinc (assumption:
                      # the spec's incoming check; the tube standards allow up to -10%)
GAMMA_M0, GAMMA_M2 = 1.0, 1.25   # EN 1993-1-1 and 1-8 recommended values (source)
BETA_W = 0.85                    # fillet weld correlation factor, EN 1993-1-8 Table 4.1 (0.85 for S275; taken for
                                 # every grade, the safe side here; source)
HANDLING, MARGIN = 2.0, 1.5      # D-117's corner check (assumption, PM-accepted)
PERIMETER_T, INNER_T = 1.0, 0.8  # mm, the gauges this check sets (D-131's start values)
SIDE_T = 1.2                     # mm, the side panels' rails and front stiles (PM ruling 2026-11-01)
MAX_USE = 0.90                   # every frame's corner lift at the thinnest accepted wall (PM ruling 2026-11-01)
PLATE_T = 2.0                    # mm, the plate in each mitre (PROPOSED; at least 1.5 x the 1.0 wall)
PLATE_GAP = 0.5                  # mm: each square end of a plate sits at least this far inside the frame's faces, on
                                 # both plate faces (the Lead's steer, 2026-11-01: a plate the mitre's full size pokes
                                 # out at the outer corner by its half thickness x the cut's cosine; the all-round
                                 # weld fills the step and is ground flush)
# corner plates, per corner type: (the two members' widths in the frame's plane, the narrower first; where the blank
# starts along the mitre line from the frame's outer corner; its length along that line). Laser-cut blanks, the
# length to 0.1 and the start to 0.05 (calculation; plate_corners() checks them; the joints CAD README places them).
# Each is 40 across the frame (its depth) and PLATE_T thick.
PLATE_BLANKS = {"20x40 to 20x40, 45 deg": (20.0, 20.0, 1.75, 26.5),
                "rail to 40x40, 63.43 / 26.57 deg": (20.0, 40.0, 3.15, 41.5),
                "40x40 to 40x40, 45 deg": (40.0, 40.0, 1.75, 54.8)}
PLATES = {k: v[3] for k, v in PLATE_BLANKS.items()}    # the blank's length, for its mass
PLATE_PNS = {"20x40 to 20x40, 45 deg": "831007", "rail to 40x40, 63.43 / 26.57 deg": "831008",
             "40x40 to 40x40, 45 deg": "831009"}       # joints register H-40 to H-42
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PLATE_DIR = os.path.join(REPO, "v2", "03-Manufacturing", "joints")


def _stepfile():
    """The mechanical check's own STEP reader (tools/checks/stepfile.py), loaded by its path, not copied."""
    spec = importlib.util.spec_from_file_location("stepfile_for_frame_steel_check",
                                                  os.path.join(REPO, "tools", "checks", "stepfile.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dxf_extents(path):
    """(xmin, ymin, xmax, ymax) of an R12 DXF's LINE entities and its $INSUNITS (4 is mm)."""
    with open(path, encoding="latin-1") as fh:
        rows = [ln.strip() for ln in fh]
    pairs = list(zip(rows[0::2], rows[1::2]))
    xs, ys, units, in_ents = [], [], None, False
    for i, (code, val) in enumerate(pairs):
        if code == "9" and val == "$INSUNITS" and i + 1 < len(pairs):
            units = pairs[i + 1][1]
        elif code == "2" and val == "ENTITIES":
            in_ents = True
        elif code == "0" and val == "ENDSEC":
            in_ents = False
        elif in_ents and code in ("10", "11"):
            xs.append(float(val))
        elif in_ents and code in ("20", "21"):
            ys.append(float(val))
    return ((min(xs), min(ys), max(xs), max(ys)) if xs and ys else None), units


def plate_exports():
    """Each plate's committed STEP and DXF against its blank (Reviewer 6 on #308): the STEP's one solid from the
    frame's outer corner (X from the blank's start, Y 0 to 40 across the frame, Z the half thickness either side),
    carrying its own part number; the DXF the blank alone from its own corner (0 to the length, 0 to 40, in mm).
    Returns [(part number, STEP box, DXF extents, problems)], all in mm."""
    sf = _stepfile()
    out = []
    for kind, (_a, _b, x0, length) in PLATE_BLANKS.items():
        pn = PLATE_PNS[kind]
        problems, sbox, dbox = [], None, None
        steps = glob.glob(os.path.join(PLATE_DIR, pn + "_P[0-9][0-9]_*_STEP.step"))
        dxfs = glob.glob(os.path.join(PLATE_DIR, pn + "_P[0-9][0-9]_*_DXF.dxf"))
        if len(steps) != 1:
            problems.append("%d STEP files, want 1" % len(steps))
        else:
            st = sf.StepFile(steps[0])
            insts = st.instances()
            boxes = [sf.world_box(st.solid(i["solid"]), i["frame"]) for i in insts]
            if len(boxes) != 1 or boxes[0] is None:
                problems.append("its STEP has %d solids, want 1" % len(boxes))
            else:
                sbox = boxes[0]
                want = (x0, 0.0, -PLATE_T / 2, x0 + length, 40.0, PLATE_T / 2)
                if any(abs(g - w) > 0.01 for g, w in zip(sbox, want)):
                    problems.append("STEP box X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f, want X %.2f..%.2f Y 0..40 Z -%.1f..%.1f"
                                    % (sbox[0], sbox[3], sbox[1], sbox[4], sbox[2], sbox[5], x0, x0 + length,
                                       PLATE_T / 2, PLATE_T / 2))
                if insts[0]["part_number"] != pn:
                    problems.append("its STEP carries part number %r" % insts[0]["part_number"])
        if len(dxfs) != 1:
            problems.append("%d DXF files, want 1" % len(dxfs))
        else:
            dbox, units = dxf_extents(dxfs[0])
            if units != "4":
                problems.append("its DXF's units are %r, want 4 (mm)" % units)
            if dbox is None or any(abs(g - w) > 0.01 for g, w in zip(dbox, (0.0, 0.0, length, 40.0))):
                problems.append("DXF extents %s, want 0..%.2f x 0..40" % (
                    "none" if dbox is None else "%.2f..%.2f x %.2f..%.2f" % (dbox[0], dbox[2], dbox[1], dbox[3]), length))
        out.append((pn, sbox, dbox, problems))
    return out


def plate_corners(a, b, x0, length, half=PLATE_T / 2):
    """How far each corner of a plate's two square ends sits inside the frame's outline (negative: outside it).
    The corner in the frame's plane: member A along +x (0 <= y <= a), member B along +y (0 <= x <= b), the outer
    corner at the origin and the inner one at (b, a); the plate's mid-plane on the mitre line between them, its
    faces half a thickness either side. Found from the corner's coordinates, so no face is assumed to be the one."""
    L = math.hypot(a, b)
    u, n = (b / L, a / L), (-a / L, b / L)

    def inside(x, y):
        if x < 0 or y < 0:
            return -math.hypot(min(x, 0.0), min(y, 0.0))
        if x > b and y > a:                                   # in the frame's opening
            return -min(x - b, y - a)
        return min(x, y, math.hypot(max(b - x, 0.0), max(a - y, 0.0)))
    return {"%s end, %s face" % (end, face): inside(s * u[0] + t * n[0], s * u[1] + t * n[1])
            for end, s in (("outer", x0), ("inner", x0 + length)) for face, t in (("one", half), ("other", -half))}

# the aluminium frames they replace: bare frame and panel masses from each team's parts list on main (calculation)
AL_FRAME_KG = {"L1": 3.105, "L2": 3.262, "B1": 2.366, "C1": 3.410}
PANEL_KG = {"L1": 11.29, "L2": 11.406, "B1": 8.687, "C1": 10.371}


def rounded_rect(w, h, r, n=24):
    """Outline of a w x h rectangle with corner radius r, centred on the origin, counter-clockwise."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def poly_props(p):
    """Area and second moments about the x and y axes of a closed polygon."""
    A = Ix = Iy = 0.0
    for (x0, y0), (x1, y1) in zip(p, p[1:] + p[:1]):
        c = x0 * y1 - x1 * y0
        A += c
        Ix += (y0 * y0 + y0 * y1 + y1 * y1) * c
        Iy += (x0 * x0 + x0 * x1 + x1 * x1) * c
    return A / 2, Ix / 12, Iy / 12


class Tube:
    """A cold-formed box tube: depth h in the bending plane, width w across it, wall t, corner radii 2t outside and
    t inside (EN 10219-2's usual values; assumption until the tube maker's drawing)."""

    def __init__(self, h, w, t):
        self.h, self.w, self.t = h, w, t
        self.ro, self.ri = 2.0 * t, 1.0 * t
        Ao, Io, _ = poly_props(rounded_rect(w, h, self.ro))      # x along w, y along h: Ix bends about the w axis
        Ai, Ii, _ = poly_props(rounded_rect(w - 2 * t, h - 2 * t, self.ri))
        self.A, self.I = Ao - Ai, Io - Ii
        self.W_el = self.I / (h / 2)
        self.W_pl = self._w_pl()

    def _half_width(self, W, H, r, y):
        y = abs(y)
        if y > H / 2:
            return 0.0
        if y <= H / 2 - r:
            return W / 2
        return W / 2 - r + math.sqrt(max(0.0, r * r - (y - (H / 2 - r)) ** 2))

    def _w_pl(self, n=4000):
        """Plastic modulus: twice the first moment of the half section about the centroid, by strips."""
        h, w, t = self.h, self.w, self.t
        dy = (h / 2) / n
        s = 0.0
        for k in range(n):
            y = (k + 0.5) * dy
            b = 2 * (self._half_width(w, h, self.ro, y) - self._half_width(w - 2 * t, h - 2 * t, self.ri, y))
            s += b * y * dy
        return 2 * s

    def kg_per_m(self):
        return self.A * RHO * 1000.0

    def section_class(self, fy):
        """EN 1993-1-1 Table 5.2 for a box in bending: the compression wall (w wide) is an internal part in
        compression, the side walls (h deep) internal parts in bending; c = width - 3t for hollow sections."""
        eps = math.sqrt(235.0 / fy)
        ct_f, ct_w = (self.w - 3 * self.t) / self.t, (self.h - 3 * self.t) / self.t
        cf = 1 if ct_f <= 33 * eps else 2 if ct_f <= 38 * eps else 3 if ct_f <= 42 * eps else 4
        cw = 1 if ct_w <= 72 * eps else 2 if ct_w <= 83 * eps else 3 if ct_w <= 124 * eps else 4
        return max(cf, cw)

    def w_eff(self, fy):
        """Effective modulus for class 4: the compression wall's effective width by EN 1993-1-5 4.4 (internal part,
        uniform compression, k_sigma 4); the side walls stay fully effective (class 1 in these tubes)."""
        eps = math.sqrt(235.0 / fy)
        c = self.w - 3 * self.t
        lam = (c / self.t) / (28.4 * eps * 2.0)
        rho = 1.0 if lam <= 0.673 else min(1.0, (lam - 0.055 * 4) / lam ** 2)
        dA = (1 - rho) * c * self.t
        yr = self.h / 2 - self.t / 2
        A_eff = self.A - dA
        yc = -dA * yr / A_eff                        # the centroid moves away from the lost strip
        I_eff = (self.I - dA * yr * yr) - A_eff * yc * yc
        return I_eff / (self.h / 2 + abs(yc))

    def m_rd(self, fy):
        """(bending resistance in N*mm, the class it was taken at)."""
        cls = self.section_class(fy)
        W = self.W_pl if cls <= 2 else self.W_el if cls == 3 else self.w_eff(fy)
        return W * fy / GAMMA_M0, cls

    def t_rd(self, fy):
        """Torsion resistance of the closed thin-walled section (N*mm): 2 A_m t fy / sqrt(3)."""
        return 2 * (self.h - self.t) * (self.w - self.t) * self.t * fy / math.sqrt(3) / GAMMA_M0


def core(t, share=1.0):
    """The wall that carries load: the measured wall (share of the nominal) less the zinc."""
    return t * share - ZINC


def in_plane(b, d, t):
    """A member bending in the frame's plane: depth b (its face on the skin side), width d across the frame."""
    return Tube(b, d, t)


def across(b, d, t):
    """The same member bending across the frame: depth d."""
    return Tube(d, b, t)


# --- the frames: members (count, length, b in the frame's plane, d across it, role), mm. Perimeter members are
# mitred and given at their full outer length (a little high for the mass); studs and cross members fit between the
# perimeter's inner faces. Sizes from WALL's and CEILING's parts lists on main; the added stud is the PM's ruling.
FRAMES = {   # key: (title, per pod, long side, members)
    "L1": ("211101 L1 (R1 its mirror)", 2, 1495.0, [
        (2, 1495.0, 20, 40, "rail"), (1, 1143.0, 20, 40, "front stile"), (1, 1143.0, 40, 40, "back stile"),
        (3, 1103.0, 20, 40, "stud"), (2, 1103.0, 20, 40, "stud, added for D-135")]),
    "L2": ("211103 L2 (R2 its mirror)", 2, 1495.0, [
        (1, 1495.0, 20, 40, "bottom rail"), (1, 1495.0, 40, 40, "top member"), (1, 1118.6, 20, 40, "front stile"),
        (1, 1118.6, 40, 40, "back stile"), (3, 1058.6, 20, 40, "stud"),
        (2, 1058.6, 20, 40, "stud, added for D-135")]),
    "B1": ("211201 B1 (B2, B3, B4 alike)", 4, 1199.0, [
        (2, 1199.0, 20, 40, "rail"), (2, 1118.6, 20, 40, "stile"), (2, 1078.6, 20, 40, "stud"),
        (1, 1078.6, 20, 40, "stud, added for D-135")]),
    "C1": ("411101 C1 (C2 alike)", 2, 1495.0, [
        (2, 1495.0, 20, 40, "side and seam members"), (1, 1199.0, 20, 40, "front member"),
        (1, 1199.0, 40, 40, "back member"), (1, 1159.0, 20, 40, "cross member 1 (soffit rivnuts)"),
        (2, 1159.0, 20, 40, "cross members 2 and 3")]),
}
INNER_ROLES = ("stud", "cross members 2 and 3")   # no site bolt, spigot, stopped-joint rivnut or hanger stud
CORNERS = {   # corner types per frame, from WALL's and CEILING's models on main
    "L1": {"20x40 to 20x40, 45 deg": 2, "rail to 40x40, 63.43 / 26.57 deg": 2},
    "L2": {"20x40 to 20x40, 45 deg": 1, "rail to 40x40, 63.43 / 26.57 deg": 2, "40x40 to 40x40, 45 deg": 1},
    "B1": {"20x40 to 20x40, 45 deg": 4},
    "C1": {"20x40 to 20x40, 45 deg": 2, "rail to 40x40, 63.43 / 26.57 deg": 2},
}


def plate_kg(kind):
    return PLATES[kind] * 40.0 * PLATE_T * RHO


def plates_kg(key):
    return sum(n * plate_kg(k) for k, n in CORNERS[key].items())


def kappa_plain(b0, h0, t0):
    """EN 1993-1-8's share of the tube's moment an unstiffened welded knee carries (indication: walls under 2.5)."""
    return min(1.0, 3 / math.sqrt(b0 / t0) + 1 / (1 + 2 * b0 / h0))


SIDE_ROLES = ("rail", "bottom rail", "front stile")   # in the side panels L1 and L2 (and their mirrors)


def gauge(role, perimeter=PERIMETER_T, key=None):
    """A member's wall: 0.8 inner, 1.2 for the side panels' rails and front stiles, else the perimeter's."""
    if role.startswith(INNER_ROLES):
        return INNER_T
    if key in ("L1", "L2") and role in SIDE_ROLES and perimeter == PERIMETER_T:
        return SIDE_T
    return perimeter


def frame_kg(members, perimeter=PERIMETER_T, share=1.0, key=None):
    """Tube mass at the measured wall (share of the nominal), zinc included; with key, the corner plates too."""
    m = sum(n * L / 1000.0 * in_plane(b, d, gauge(role, perimeter, key) * share).kg_per_m()
            for n, L, b, d, role in members)
    return m + (plates_kg(key) if key else 0.0)


def corner_lift(key, grade, perimeter=PERIMETER_T, share=1.0, inner_everywhere=False):
    """(need, have, class) in N*mm: the in-plane moment at the frame's weakest corner."""
    _title, _n, L, members = FRAMES[key]
    gauge_of = (lambda role: INNER_T) if inner_everywhere else (lambda role: gauge(role, perimeter, key))
    m = sum(n * Ln / 1000.0 * in_plane(b, d, gauge_of(role) * share).kg_per_m() for n, Ln, b, d, role in members)
    m += plates_kg(key)
    need = m * G * L / 2 * HANDLING * MARGIN
    _name, fy, _fu = grade
    corner = [in_plane(b, d, core(gauge_of(role), share)) for _n, _L, b, d, role in members
              if not role.startswith(INNER_ROLES)]
    have, cls = min(tb.m_rd(fy) for tb in corner)
    return need, have, cls


def worst_lift(grades, perimeter=PERIMETER_T, share=1.0):
    """(use, frame key, grade name, class) of the highest corner-lift use over the frames and grades."""
    out = []
    for key in FRAMES:
        for g in grades:
            need, have, cls = corner_lift(key, g, perimeter, share)
            out.append((need / have, key, g[0], cls))
    return max(out)


def out_of_plane(key, grade):
    """(need, have) in N*mm: held flat by its short member (the 40 x 40 if it has one), the rest on two corners."""
    _title, _n, L, members = FRAMES[key]
    m = frame_kg(members, key=key)
    _c, Lh, b, d, role = max((mb for mb in members if mb[1] < L), key=lambda mb: mb[3] * mb[2])
    held = Lh / 1000.0 * in_plane(b, d, gauge(role, key=key)).kg_per_m()
    need = (m - held) * G * L / 2 / 2 * HANDLING * MARGIN
    t = core(PERIMETER_T, WALL_MIN)
    fy = grade[1]
    return need, min(across(20, 40, t).m_rd(fy)[0], in_plane(20, 40, t).t_rd(fy))


# --- seam bolts and rivnuts (joints register 2.6 and J-T1) ----------------------------------------------------
BOLT_LOADS = {"walls": 200.0, "DL (the door's side)": 533.0}  # N per bolt: J-T1's pass loads / 3 (assumption, J-T1)
GRIP = (0.70, 4.20)              # rivnut 838003's grip range, Sherex CAH2-610-4.2 steel (source: SHX2)
STOP_WASHER = 1.5                # H-08, under the stopped joints' rivnut heads (register H-08)
BULGE = 13.0                     # set rivnut's bulge diameter, about its head's 12.96 (assumption)
HEAD_WASHER = 18.0               # 838004 under each bolt head (register H-09)
FU_MIN = min(g[2] for g in ACCEPTED)


def pull_through(t, d):
    """Wall punching round a ring of diameter d at 0.6 fu, the thinnest accepted core wall (calculation)."""
    return 0.6 * FU_MIN * math.pi * d * core(t, WALL_MIN)


def bearing(t, dia=6.0):
    """M6 shank bearing in its Ø7.0 hole, EN 1993-1-8 Table 3.4 with alpha_b 1 and k1 2.5 (calculation)."""
    return 2.5 * 1.0 * FU_MIN * dia * core(t, WALL_MIN) / GAMMA_M2


# --- welds ---------------------------------------------------------------------------------------------------
V_T = 300.0       # N, T joint shear: 3 x about 0.1 kN, the ceiling's cross member 1 with a soffit hanger (about
                  # 5.5 kg) and two cassette clips (about 3.3 kg) (assumption, D-117's figure)


def t_joint_weld(t_stud):
    """Full-perimeter fillet weld round a 20 x 40 stud end, throat 0.7 x the stud's core wall (assumption):
    resistance by EN 1993-1-8's simplified method at the lowest accepted fu (N)."""
    fvw = FU_MIN / math.sqrt(3) / (BETA_W * GAMMA_M2)
    return fvw * 0.7 * core(t_stud, WALL_MIN) * 2 * (20 + 40)


def report():
    print("Gauges: %.1f mm for the side panels' rails and front stiles; %.1f mm for every other perimeter member, every"
          " 40 x 40 member and any member with a site bolt, spigot, stopped-joint rivnut or hanger stud; %.1f mm for the"
          " studs and the ceiling's cross members 2 and 3. Every frame at %.0f%% or less at the thinnest wall."
          % (SIDE_T, PERIMETER_T, INNER_T, 100 * MAX_USE))
    print("Steel: yield 280 MPa or more (" + "; ".join("%s, fy %g, fu %g" % g for g in ACCEPTED) + "); zinc Z100;"
          " the wall measured at %.0f%% of its nominal or more. Strength uses the core wall (less %.3f mm"
          " of zinc)." % (100 * WALL_MIN, ZINC))
    print()
    print("| Tube, core wall at the thinnest accepted | kg/m (nominal) | In plane M_Rd (N·m), class | Across M_Rd (N·m) | Torsion T_Rd (N·m) |")
    print("|---|---:|---:|---:|---:|")
    for b, d, t in ((20, 40, INNER_T), (20, 40, PERIMETER_T), (20, 40, SIDE_T), (40, 40, INNER_T), (40, 40, PERIMETER_T)):
        if True:
            tc = core(t, WALL_MIN)
            ip, ac = in_plane(b, d, tc), across(b, d, tc)
            m_ip, c_ip = min(ip.m_rd(g[1]) for g in ACCEPTED)
            m_ac = min(ac.m_rd(g[1])[0] for g in ACCEPTED)
            t_r = min(ip.t_rd(g[1]) for g in ACCEPTED)
            print("| %dx%dx%.1f (%.3f) | %.3f | %.0f, class %d | %.0f | %.0f |" % (
                b, d, t, tc, in_plane(b, d, t).kg_per_m(), m_ip / 1000, c_ip, m_ac / 1000, t_r / 1000))
    print()
    print("| Frame | Per pod | Aluminium frame (kg) | Steel frame (kg) | Panel (kg) | Corner lift need / have (N·m), thinnest wall | Use | Out of plane need / have (N·m) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    tot_al = tot_st = 0.0
    rows = {}
    for key, (title, per_pod, _L, members) in FRAMES.items():
        m = frame_kg(members, key=key)
        panel = PANEL_KG[key] - AL_FRAME_KG[key] + m
        need, have, _cls = min((corner_lift(key, g, share=WALL_MIN) for g in ACCEPTED), key=lambda r: r[1] / r[0])
        oop = min((out_of_plane(key, g) for g in ACCEPTED), key=lambda r: r[1] / r[0])
        rows[key] = (m, panel, need, have) + oop
        tot_al += per_pod * AL_FRAME_KG[key]
        tot_st += per_pod * m
        print("| %s | %d | %.2f | %.2f | %.1f | %.0f / %.0f | %.0f%% | %.0f / %.0f |" % (
            title, per_pod, AL_FRAME_KG[key], m, panel, need / 1000, have / 1000, 100 * need / have,
            oop[0] / 1000, oop[1] / 1000))
    no_stud = sum(FRAMES[k][1] * n * L / 1000.0 * in_plane(b, d, INNER_T).kg_per_m()
                  for k in FRAMES for n, L, b, d, role in FRAMES[k][3] if role.startswith("stud, added"))
    print("| the pod's 10 wall and ceiling frames | 10 | %.1f | %.1f | | | | |" % (tot_al, tot_st))
    print("Steel adds %.1f kg to the 10 frames: %.1f for the steel, %.1f for the added studs (calculation; the decor"
          " cores and DR are FRONT's count). Each panel keeps its other parts as its list gives them (the added"
          " stud's bond bead and the fill it displaces are left out, tens of grams)."
          % (tot_st - tot_al, tot_st - tot_al - no_stud, no_stud))
    print()
    print("| Corner lift, worst frame | Nominal wall | Wall at %.0f%% |" % (100 * WALL_MIN))
    print("|---|---:|---:|")
    for label, grades in (("accepted grades (yield 280 or more)", ACCEPTED),) + tuple(
            (g[0], (g,)) for g in NOT_ACCEPTED):
        a = worst_lift(grades)
        b = worst_lift(grades, share=WALL_MIN)
        print("| %s | %.0f%% (%s, class %d) | %.0f%% (class %d) |" % (label, 100 * a[0], a[1], a[3], 100 * b[0], b[3]))
    p12 = worst_lift(NOT_ACCEPTED, perimeter=1.2, share=WALL_MIN)
    d12 = sum(FRAMES[k][1] * (frame_kg(FRAMES[k][3], perimeter=1.2) - frame_kg(FRAMES[k][3], key=k) + plates_kg(k))
              for k in FRAMES)
    tc = core(PERIMETER_T, WALL_MIN)
    k20, k40 = kappa_plain(40, 20, tc), kappa_plain(40, 40, tc)
    use_plain = worst_lift(ACCEPTED, share=WALL_MIN)[0] / k20
    print("Corners: a plain mitre would carry about %.2f of a 20 x 40 tube's moment and %.2f of a 40 x 40's"
          " (EN 1993-1-8's knee rule at the %.3f core wall; valid from 2.5 mm, so an indication): the worst corner lift"
          " would be about %.0f%%. With the %.1f mm plate in each mitre (a stiffened knee, plate at least 1.5 t) the corner"
          " carries the tube's moment: the use is the table's." % (k20, k40, tc, 100 * use_plain, PLATE_T))
    n_plates = {k: sum(FRAMES[f][1] * CORNERS[f].get(k, 0) for f in FRAMES) for k in PLATES}
    print("Corner plates per pod: " + ", ".join("%d of %s (%.1f x 40 x %.1f from %.2f along the mitre, %.1f g; ends"
                                                " %.2f inside the faces, %.2f at full size)" % (
        n, k, PLATES[k], PLATE_T, PLATE_BLANKS[k][2], 1000 * plate_kg(k), min(plate_corners(*PLATE_BLANKS[k]).values()),
        min(plate_corners(PLATE_BLANKS[k][0], PLATE_BLANKS[k][1], 0.0, math.hypot(*PLATE_BLANKS[k][:2])).values()))
        for k, n in n_plates.items()) +
          "; %.2f kg in all (in the frame masses above)." % sum(n * plate_kg(k) for k, n in n_plates.items()))
    print("Plate exports against their blanks: " + "; ".join(
        "%s STEP X %s, DXF %s: %s" % (pn, "%.2f..%.2f" % (sb[0], sb[3]) if sb else "?",
                                      "%.2f x %.2f" % (db[2] - db[0], db[3] - db[1]) if db else "?",
                                      "match" if not probs else ", ".join(probs))
        for pn, sb, db, probs in plate_exports()) + ".")
    print("Every perimeter at 1.2 mm: %.0f%% at worst with any grade above, the wall at %.0f%%, for %.1f kg more a pod."
          % (100 * p12[0], 100 * WALL_MIN, d12))
    for key in ("L2", "C1"):
        n8, h8, c8 = min((corner_lift(key, g, inner_everywhere=True) for g in ACCEPTED), key=lambda r: r[1] / r[0])
        print("Every member at %.1f mm, %s: corner lift %.0f against %.0f N·m (class %d): %s."
              % (INNER_T, FRAMES[key][0], n8 / 1000, h8 / 1000, c8, "fails" if n8 > h8 else "passes"))
    print()
    print("| Seam bolts and rivnuts, thinnest accepted wall | 0.8 mm | 1.0 mm |")
    print("|---|---:|---:|")
    print("| Rivnut 838003 grip, bare wall / with the 1.5 stop washer (range 0.70 to 4.20) | %.2f / %.2f | %.2f / %.2f |"
          % (INNER_T * WALL_MIN, INNER_T + STOP_WASHER, PERIMETER_T * WALL_MIN, PERIMETER_T + STOP_WASHER))
    print("| Pull-through round the rivnut's bulge (kN) | %.1f | %.1f |" % (pull_through(0.8, BULGE) / 1000,
                                                                       pull_through(1.0, BULGE) / 1000))
    print("| Pull-through round the bolt head's 18 mm washer (kN) | %.1f | %.1f |" % (
        pull_through(0.8, HEAD_WASHER) / 1000, pull_through(1.0, HEAD_WASHER) / 1000))
    print("| M6 bearing in the Ø7.0 hole (kN) | %.1f | %.1f |" % (bearing(0.8) / 1000, bearing(1.0) / 1000))
    print("Highest bolt loads: " + ", ".join("%s %.2f kN" % (k, v / 1000) for k, v in BOLT_LOADS.items()) +
          " (J-T1's pass loads are 3 x these). The rivnut's own strength (CAH2-610-4.2, steel) is shown by T06 and"
          " J-T1 in the steel tube, not by a figure.")
    print("T joint weld, full perimeter, throat 0.7 x the core wall: %.1f kN in a 0.8 stud, %.1f kN in 1.0, against"
          " %.1f kN shear." % (t_joint_weld(0.8) / 1000, t_joint_weld(1.0) / 1000, V_T / 1000))
    return rows


def check():
    bad = []
    rows = report()
    for key, (m, panel, need, have, oop_need, oop_have) in rows.items():
        title = FRAMES[key][0]
        if need > MAX_USE * have:
            bad.append("%s: corner lift %.0f N*m over %.0f%% of %.0f" % (title, need / 1000, 100 * MAX_USE, have / 1000))
        if oop_need > oop_have:
            bad.append("%s: out of plane %.0f N*m over %.0f" % (title, oop_need / 1000, oop_have / 1000))
        if panel > 20.0:
            bad.append("%s: the panel is %.1f kg, over 20 (D-131)" % (title, panel))
    for t in (INNER_T, PERIMETER_T):
        if not (GRIP[0] <= t * WALL_MIN and t + STOP_WASHER <= GRIP[1]):
            bad.append("rivnut grip: %.2f or %.2f outside %.2f to %.2f" % (t * WALL_MIN, t + STOP_WASHER, *GRIP))
        if pull_through(t, BULGE) < 3 * max(BOLT_LOADS.values()):
            bad.append("pull-through in %.1f under 3 x the highest bolt load" % t)
        if bearing(t) < 3 * max(BOLT_LOADS.values()):
            bad.append("bearing in %.1f under 3 x the highest bolt load" % t)
    if t_joint_weld(INNER_T) < V_T:
        bad.append("T joint weld under the shear")
    if PLATE_T < 1.5 * max(PERIMETER_T, SIDE_T):
        bad.append("mitre plate thinner than 1.5 x the wall: not a stiffened knee")
    for kind, (a, b, x0, length) in PLATE_BLANKS.items():
        worst = min(plate_corners(a, b, x0, length).values())
        if worst < PLATE_GAP - 1e-9:
            bad.append("mitre plate %s: a square end %.3f inside the frame's faces, under %.1f" % (kind, worst, PLATE_GAP))
        if min(plate_corners(a, b, 0.0, math.hypot(a, b)).values()) >= 0:      # the rule is checked, not assumed
            bad.append("a full-size %s plate stays inside the frame: the trim isn't needed, re-check" % kind)
        if a > b:
            bad.append("mitre plate %s: the narrower member first" % kind)
    for pn, _sb, _db, probs in plate_exports():          # the committed exports are the blanks, not only the table
        bad.extend("mitre plate %s: %s" % (pn, pr) for pr in probs)
    if sum(sum(c.values()) * FRAMES[f][1] for f, c in CORNERS.items()) != 40:
        bad.append("corner count: want 40 a pod")
    # the rules are checked, not assumed: 0.8 perimeters must fail, and so must the weakest grade left out
    n8, h8, _c = corner_lift("L2", ACCEPTED[0], inner_everywhere=True)
    if n8 <= h8:
        bad.append("0.8 mm perimeters pass the corner lift: the 1.0 rule isn't needed, re-check")
    if worst_lift(NOT_ACCEPTED, share=WALL_MIN)[0] <= MAX_USE:
        bad.append("every grade under 280 MPa keeps 90%% at the thinnest wall: the 280 MPa rule isn't needed, re-check")
    return bad


if __name__ == "__main__":
    if "--check" in sys.argv:
        problems = check()
        print("\n" + ("NOT OK:\n  " + "\n  ".join(problems) if problems else "OK: every rule holds"))
        sys.exit(1 if problems else 0)
    report()
