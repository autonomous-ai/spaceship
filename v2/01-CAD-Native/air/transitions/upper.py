"""The upper transition (in place of 618102): from the supply fan box's open top to the opening into the air column,
in 2 mm aluminium, built as a shell, a floor and turning vanes (the Lead's rulings 2026-11-01: the shop build; vanes,
as the air report assumes).

The shell is an upturned tray: a roof with five walls folded down from its edges (front, facet, right, back, left),
each pair of walls joined by a corner tab riveted inside the next wall. Its front and left walls drop 18 mm over the
box's walls as skirts; its back wall stands on DR's frame face and carries the outlet window, with the gasket
(848013) on its outer face around it. The facet wall keeps clear of the corner facet's tubes (C04, the front ring's
facet side tube). The floor closes the shell's bottom beside and behind the box: a flat L with a ramp beside the box
up to the front wall (clear of the cross tube over the box), and flanges up the shell's walls and the box's walls.

Pod coordinates, mm; each wall by its outer skin."""

import math

import numpy as np

import geom3 as G
import rivets as R
import tr_sheetmetal as S
from tr_params import P

AL = "Aluminium 5052-H32, 2.0 mm (alloy HOLD)"
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])
ROOF_RELIEF = 8.0          # along every roof fold from each roof corner (more than r + t, square kites)


def frame():
    """The shell's outline: its roof corners A..E (plan) and levels."""
    t = P.ut_t
    x0 = P.sb_x0 - P.ut_c - t
    yf = P.sb_y0 - P.ut_c - t
    yb, xr = P.ut_back_y, P.ut_right_x
    u = G.unit(np.array([P.c04_bx - P.c04_ax, P.c04_by - P.c04_ay, 0.0]))
    n_fac = np.array([u[1], -u[0], 0.0])                 # the facet's outward normal (front right)
    B = np.array([P.fac_x, yf, 0.0])
    C = B + u * ((xr - P.fac_x) / u[0])
    return dict(t=t, x0=x0, yf=yf, yb=yb, xr=xr, zr=P.ut_roof_z, zs=P.ut_skirt_z, zf=P.ut_floor_z, u=u, n_fac=n_fac,
                A=np.array([x0, yf, 0.0]), B=B, C=C, D=np.array([xr, yb, 0.0]), E=np.array([x0, yb, 0.0]),
                ypocket=P.sb_y1 + P.ut_c)


def _at(p, z):
    return np.array([p[0], p[1], z])


def _seg_from(K0, K1, a0, a1):
    d = G.unit(K1 - K0)
    return K0 + a0 * d, K1 - a1 * d


def _pin(poly, i, seg, other_need):
    """Reliefs pinning edge i of poly to the fold segment seg (two points on that edge's line)."""
    n = len(poly)
    K0, K1 = poly[i], poly[(i + 1) % n]
    d = G.unit(K1 - K0)
    s0 = float(np.dot(seg[0] - K0, d))
    s1 = float(np.dot(seg[1] - K0, d))
    lo, hi = min(s0, s1), max(s0, s1)
    return {(i, "next"): lo, ((i + 1) % n, "prev"): float(np.linalg.norm(K1 - K0)) - hi}


def _relieve(poly, h, fixed, amin=5.0):
    out, used = [], {}
    n = len(poly)
    for i in range(n):
        A, K, B = poly[i - 1], poly[i], poly[(i + 1) % n]
        a1, a2 = G.relief_need(K, A, B, h[i - 1], h[i], amin, fixed.get((i, "prev")), fixed.get((i, "next")))
        kp, _l1, _l2 = G.kite(K, A, B, a1, a2)
        out += kp
        used[(i, "prev")], used[(i, "next")] = a1, a2
    return out, used


def _h(theta_rad):
    return (P.ut_r + P.ut_t) * math.tan(theta_rad / 2) + 0.4


def _angle(n1, n2):
    return math.acos(max(-1.0, min(1.0, float(np.dot(G.unit(n1), G.unit(n2))))))


TAB_Z0 = 1952.0            # corner tabs start above the box's top (1950) and the floor's flanges (to 1949)
TAB_GAP = 0.2              # a corner tab stands this far off the wall it is riveted to: one sheet, not a closed loop


def _slot(poly, h, keep, ei, n_wall, top_edge):
    """Split a wall's side edge ei (vertical) at TAB_Z0: above it the tab's fold, below it the plain edge, between
    them a relief slot into the wall (square to the edge, deeper than the fold's tangent distance). Returns the new
    polygon, edge h list, kept corners and the top edge's new index."""
    m = len(poly)
    K0, K1 = poly[ei], poly[(ei + 1) % m]
    up = K1[2] > K0[2]
    zt = TAB_Z0
    d = G.unit(K1 - K0)
    cen = sum(poly) / m
    inward = G.unit(np.cross(n_wall, d))
    if np.dot(cen - K0, inward) < 0:
        inward = -inward
    depth = _h(math.pi / 2) + 0.6
    ws = 1.5
    p_tab = K0 + d * ((zt - K0[2]) / d[2])                   # where the tab's fold starts, on the edge
    p_low = K0 + d * ((zt - ws - K0[2]) / d[2]) if up else K0 + d * ((zt - ws - K0[2]) / d[2])
    if up:      # K0 low -> K1 high: plain edge, slot, then the fold up to K1
        ins = [p_low, p_low + inward * depth, p_tab + inward * depth, p_tab]
        hins = [0.3, 0.3, 0.3, h[ei]]
        new_h = h[:ei] + [0.3] + hins + h[ei + 1:]
    else:       # K0 high -> K1 low: the fold down to the slot, then the plain edge
        ins = [p_tab, p_tab + inward * depth, p_low + inward * depth, p_low]
        hins = [0.3, 0.3, 0.3, 0.3]
        new_h = h[:ei] + [h[ei]] + hins + h[ei + 1:]
    new_poly = poly[:ei + 1] + ins + poly[ei + 1:]
    shift = {i: (i if i <= ei else i + 4) for i in range(m)}
    new_keep = {shift[k] for k in keep} | {ei + 1, ei + 2, ei + 3, ei + 4}
    new_top = shift[top_edge] if top_edge <= ei else top_edge + 4
    return new_poly, new_h, new_keep, new_top


def _tab_edge(poly, line):
    """The index of the slotted polygon's edge on the original side edge's line (two points) that runs between
    TAB_Z0 and the wall's top: the tab's fold."""
    a0, a1 = line
    d = G.unit(a1 - a0)
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        on = all(np.linalg.norm(np.cross(q - a0, d)) < 1e-6 for q in (a, b))
        if on and abs(min(a[2], b[2]) - TAB_Z0) < 1e-6 and max(a[2], b[2]) > TAB_Z0 + 50:
            return i
    raise ValueError("no tab edge on the line")

def shell(holes=None):
    F = frame()
    t, zr, zs, zf = F["t"], F["zr"], F["zs"], F["zf"]
    A, B, C, D, E, u, nfac = F["A"], F["B"], F["C"], F["D"], F["E"], F["u"], F["n_fac"]
    # the roof and its five fold segments, each ROOF_RELIEF in from the roof's corners
    roof = [_at(q, zr) for q in (A, B, C, D, E)]
    rfix = {}
    for i in range(5):
        rfix[(i, "next")], rfix[((i + 1) % 5, "prev")] = ROOF_RELIEF, ROOF_RELIEF
    h_roof = [_h(math.pi / 2), _h(math.pi / 2), _h(math.pi / 2), _h(math.pi / 2), _h(math.pi / 2)]
    roof_r, ur = _relieve(roof, h_roof, rfix)
    segs = [_seg_from(roof[i], roof[(i + 1) % 5], ROOF_RELIEF, ROOF_RELIEF) for i in range(5)]
    # the walls (outer skins). Corners: front outer at A and B; left inner at A, outer at E; facet inner at B, outer
    # at C; right inner at C, outer at D; back inner at D and E. Inner walls stop at the next wall's inside face.
    g = TAB_GAP
    Bi = B + u * ((t + g) / u[1])                        # the facet's outer line, TAB_GAP inside the front wall
    s_c = (F["xr"] - B[0] + (t + g) * nfac[0]) / u[0]
    Ci = B + u * s_c - nfac * (t + g)                    # TAB_GAP inside the facet's inside face, at the right wall
    Ci = np.array([F["xr"], Ci[1], 0.0])
    yr = P.ramp_y
    Pr = B + u * ((yr - B[1]) / u[1])                    # the ramp's foot under the facet
    front = [_at(A, zs), _at(B, zs), _at(B, zr), _at(A, zr)]
    left = [np.array([F["x0"], F["yf"] + t + g, zs]), np.array([F["x0"], F["ypocket"], zs]),
            np.array([F["x0"], F["ypocket"], zf]), np.array([F["x0"], F["yb"], zf]),
            np.array([F["x0"], F["yb"], zr]), np.array([F["x0"], F["yf"] + t + g, zr])]
    facet = [_at(Bi, zs), _at(Pr, zf), _at(C, zf), _at(C, zr), _at(Bi, zr)]
    Dr = np.array([F["xr"], F["yb"] - t - g, 0.0])     # the right wall stops TAB_GAP inside the back wall
    right = [_at(Ci, zf), _at(Dr, zf), _at(Dr, zr), _at(Ci, zr)]
    back = [np.array([F["x0"] + t + g, F["yb"], zf]), np.array([F["xr"], F["yb"], zf]),
            np.array([F["xr"], F["yb"], zr]), np.array([F["x0"] + t + g, F["yb"], zr])]
    free = 0.3
    h90 = _h(math.pi / 2)
    a_fac = _angle(-Y, nfac)            # the facet's tab onto the front wall
    a_rt = _angle(X, nfac)              # the right wall's tab onto the facet
    walls_def = {
        "FRONT": (front, -Y, [free, free, h90, free], 2, 0),
        "LEFT": (left, -X, [free, free, free, free, h90, h90], 4, 4),
        "FACET": (facet, nfac, [free, free, free, h90, _h(a_fac)], 3, 1),
        "RIGHT": (right, X, [free, h90, h90, _h(a_rt)], 2, 2),
        "BACK": (back, Y, [free, free, h90, h90], 2, 3),
    }
    walls, folds = [], []
    holes = holes or {}
    roof_wall = S.Wall("ROOF", roof_r, Z, holes=holes.get("ROOF", []))
    walls.append(roof_wall)
    # each tab's edge: (wall, edge index): the tab runs from TAB_Z0 up; below it a relief slot frees the fold's end
    tab_edges = {("LEFT", 5), ("FACET", 4), ("RIGHT", 3), ("RIGHT", 1), ("BACK", 3)}
    built = {}
    for name, (poly, n, h, top_edge, roof_edge) in walls_def.items():
        poly = list(poly)
        h = list(h)
        keep = set()
        for (wn, ei) in sorted(tab_edges, key=lambda x: -x[1]):
            if wn != name:
                continue
            poly, h, keep, top_edge = _slot(poly, h, keep, ei, n, top_edge)
        fx = _pin(poly, top_edge, segs[roof_edge], None)
        pr, used = _relieve_keep(poly, h, fx, keep)
        built[name] = (poly, pr, used, n)
        folds.append(S.Fold("ROOF", name, segs[roof_edge][0], segs[roof_edge][1], "ROOF - " + name))
    # corner tabs: (wall, its side edge index, the plane the tab lies on (point, the tab's outer normal), direction,
    # name, width, riveted). The back-right tab isn't riveted: a rivet through the back wall would stand in the
    # 2.36 mm gap to DR's panel, and one through the right wall within 6 mm of DR's bolt-line tube. It lies behind
    # the back wall's strip right of the window (the gasket's land) and carries the gasket's push in bearing; its
    # edge stops 0.5 mm clear of the window.
    tabs = [("LEFT", 5, (np.array([0, F["yf"] + t + g, 0]), -Y), X, "TAB LEFT TO FRONT", P.ut_tab_w, True),
            ("FACET", 4, (np.array([0, F["yf"] + t + g, 0]), -Y), -X, "TAB FACET TO FRONT", P.ut_tab_w, True),
            ("RIGHT", 3, (Bi - nfac * (t + g), nfac), -u, "TAB RIGHT TO FACET", P.ut_tab_w, True),
            ("RIGHT", 1, (np.array([0, F["yb"] - t - g, 0]), Y), -X, "TAB RIGHT TO BACK",
             F["xr"] - P.win_x1 - 0.5, False),
            ("BACK", 3, (np.array([F["x0"] + t + g, 0, 0]), -X), -Y, "TAB BACK TO LEFT", P.ut_tab_w, True)]
    tab_walls, tab_rivets = [], []
    for wname, ei, (pp, pn), e, tname, w, riveted in tabs:
        poly, pr, used, n = built[wname]
        n_ = len(poly)
        orig = walls_def[wname][0]
        ei = _tab_edge(poly, (orig[ei], orig[(ei + 1) % len(orig)]))
        K0, K1 = poly[ei], poly[(ei + 1) % n_]
        d = G.unit(K1 - K0)
        s0 = K0 + used[(ei, "next")] * d
        s1 = K1 - used[((ei + 1) % n_, "prev")] * d
        # project the tab's direction into its plane, square to the fold line
        e = G.unit(e - np.dot(e, pn) * pn)
        e = G.unit(e - np.dot(e, d) * d)
        tpoly = [s0, s1, s1 + e * w, s0 + e * w]
        th = [(s0 + (s1 - s0) * f + e * (w / 2), P.rivet_hole) for f in (0.25, 0.75)] if riveted else []
        tab_walls.append(S.Wall(tname, tpoly, pn, holes=th))
        if th:
            tab_rivets.append((tname, th, pn))
        folds.append(S.Fold(wname, tname, s0, s1, tname))
    for name, (poly, pr, used, n) in built.items():
        cut = []
        if name == "BACK":
            cut = [[np.array([P.win_x0, F["yb"], P.win_z0]), np.array([P.win_x1, F["yb"], P.win_z0]),
                    np.array([P.win_x1, F["yb"], P.win_z1]), np.array([P.win_x0, F["yb"], P.win_z1])]]
        walls.append(S.Wall(name, pr, n, cutouts=cut, holes=holes.get(name, [])))
    walls += tab_walls
    part = S.Part("UT-S", "AIR - SUPPLY TRANSITION - SHELL", walls, folds, t, P.ut_r, P.k_factor, "ROOF", P.dens_al, AL)
    part.tab_rivets = tab_rivets
    return part


def _relieve_keep(poly, h, fixed, keep, amin=5.0):
    """_relieve, but the corners in `keep` stay as they are (a fold that ends there already meets a square edge)."""
    out, used = [], {}
    n = len(poly)
    for i in range(n):
        A, K, B = poly[i - 1], poly[i], poly[(i + 1) % n]
        if i in keep:
            out.append(K)
            used[(i, "prev")], used[(i, "next")] = 0.0, 0.0
            continue
        a1, a2 = G.relief_need(K, A, B, h[i - 1], h[i], amin, fixed.get((i, "prev")), fixed.get((i, "next")))
        kp, _l1, _l2 = G.kite(K, A, B, a1, a2)
        out += kp
        used[(i, "prev")], used[(i, "next")] = a1, a2
    return out, used


def floor(holes=None, keep=None):
    """The floor: an L under the shell beside and behind the box, a ramp up to the front wall's bottom edge, and
    flanges up the shell's inside faces (cut low under the window) and the box's back wall. Its edges along the box's
    right wall stand 1.5 mm off it, sealed; a 1 mm slit at the box's back corner frees the back flange's fold."""
    F = frame()
    t, zs, zf = F["t"], F["zs"], F["zf"]
    u, nfac = F["u"], F["n_fac"]
    fin = (F["B"] - nfac * t, u)                         # the facet's inside face line (plan)

    def fac_at_y(y):
        p, d = fin
        return p + d * ((y - p[1]) / d[1])

    def fac_at_x(x):
        p, d = fin
        return p + d * ((x - p[0]) / d[0])
    xb, yb_in = P.sb_x1 + P.ut_c + 1.0, F["yb"] - t       # the beside part's edge by the box; the back wall's inside
    xr_in, xl_in = F["xr"] - t, F["x0"] + t
    yk = P.sb_y1 + P.ut_c                                 # the back flange on the box's back wall (its outer face)
    yr, yfr = P.ramp_y, F["yf"] + t
    h_slit = _h(math.pi / 2)
    V = [np.array([xb, yr]), fac_at_y(yr)[:2], fac_at_x(xr_in)[:2], np.array([xr_in, yb_in]),
         np.array([xl_in, yb_in]), np.array([xl_in, yk]), np.array([xb - 1.0, yk]),
         np.array([xb - 1.0, yk + h_slit]), np.array([xb, yk + h_slit])]
    base = [np.array([v[0], v[1], zf]) for v in V]
    ramp = [base[1].copy(), base[0].copy(), np.array([xb, yfr, zs]), np.array([fac_at_y(yfr)[0], yfr, zs])]
    n_ramp = G.unit(np.cross(ramp[1] - ramp[0], ramp[3] - ramp[0]))
    if n_ramp[2] > 0:
        n_ramp = -n_ramp
    free = 0.3
    h90 = _h(math.pi / 2)
    a_ramp = _angle(-Z, n_ramp)
    # base edges: ramp fold, facet, right, back, left, box back, slit, slit, free along the box
    h_base = [_h(a_ramp), h90, h90, h90, h90, h90, free, free, free]
    # ramp edges: base fold (other way), free along the box, front flange, facet flange
    a_front = _angle(n_ramp, -Y)
    h_ramp = [_h(a_ramp), free, _h(a_front), _h(_angle(n_ramp, nfac))]
    bu = _relieve_keep(base, h_base, {}, keep={6, 7, 8})[1]
    ru = _relieve_keep(ramp, h_ramp, {}, keep=set())[1]
    # the ramp fold: base edge 0 (V0 -> V1) is ramp edge 0 run the other way (ramp[0] = V1, ramp[1] = V0)
    s_l = max(bu[(0, "next")], ru[(1, "prev")])
    s_r = max(bu[(1, "prev")], ru[(0, "next")])
    bfix = {(0, "next"): s_l, (1, "prev"): s_r}
    rfix = {(1, "prev"): s_l, (0, "next"): s_r}
    base_r, bu = _relieve_keep(base, h_base, bfix, keep={6, 7, 8})
    ramp_r, ru = _relieve_keep(ramp, h_ramp, rfix, keep=set())

    def seg(poly, used, i):
        n = len(poly)
        K0, K1 = poly[i], poly[(i + 1) % n]
        d = G.unit(K1 - K0)
        return K0 + used[(i, "next")] * d, K1 - used[((i + 1) % n, "prev")] * d
    holes = holes or {}
    walls = [S.Wall("BASE", base_r, -Z, holes=holes.get("BASE", [])), S.Wall("RAMP", ramp_r, n_ramp)]
    flange_rivets = []
    sr = seg(base, bu, 0)
    folds = [S.Fold("BASE", "RAMP", sr[0], sr[1], "RAMP")]
    w = P.ut_tab_w
    # flanges: (wall, edge, the flange's outer normal (the face it lies on), name, the most height it may have)
    fl = [("BASE", base, bu, 1, nfac, "FLANGE FACET LOW"), ("BASE", base, bu, 2, X, "FLANGE RIGHT"),
          ("BASE", base, bu, 3, Y, "FLANGE BACK"), ("BASE", base, bu, 4, -X, "FLANGE LEFT"),
          ("BASE", base, bu, 5, -Y, "FLANGE BOX BACK"), ("RAMP", ramp, ru, 3, nfac, "FLANGE FACET RAMP"),
          ("RAMP", ramp, ru, 2, -Y, "FLANGE FRONT")]
    mitre = {"FLANGE FACET LOW": (_angle(-Z, n_ramp) / 2, None), "FLANGE FACET RAMP": (None, _angle(-Z, n_ramp) / 2)}
    for wall, poly, used, i, nn, name in fl:
        # the box back flange's rivets are set from the duct's side (rivets.py), their heads on the flange's inside
        # face: the hole keeps the head clear of the fold's inside round (t + r + half the head + 0.5), and 2
        # diameters to the free edge
        hole_in = P.ut_t + P.ut_r + R.HEAD_D / 2 + 0.5 if name == "FLANGE BOX BACK" else 8.5
        wf = max(w, math.ceil((hole_in + 2 * P.rivet_hole) * 2) / 2)
        s0, s1 = seg(poly, used, i)
        d = G.unit(s1 - s0)
        e = G.unit(np.cross(nn, d))
        if e[2] < 0:
            e = -e                                      # the flanges stand up
        L = float(np.linalg.norm(s1 - s0))
        sq = h90                                        # square to the fold past its zone, then free
        m0, m1 = mitre.get(name, (None, None))

        def end(p, along, half):
            """The flange's end: square for sq, then mitred back by half the bend's angle when a bend closes it."""
            if half is None:
                return [p + e * wf]
            return [p + e * sq, p + e * wf - along * ((wf - sq) * math.tan(half) + 0.5)]
        top0 = end(s0, -d, m0)                  # at s0, 'back along the fold' is -d
        top1 = end(s1, d, m1)
        if name == "FLANGE BACK":
            # under the window the flange stops 3 mm short of the window's bottom edge
            zlim = P.win_z0 - 3.0 - (zf + t)
            ts = sorted(float(np.dot(np.array([x, s0[1], s0[2]]) - s0, d)) for x in (P.win_x0 - 6.0, P.win_x1 + 6.0))
            ta, tb = max(ts[0], 0.0), min(ts[1], L)
            pts = [s0, s1, s1 + e * wf]
            if tb < L - 1e-6:
                pts += [s0 + d * tb + e * wf]
            pts += [s0 + d * tb + e * zlim, s0 + d * ta + e * zlim]
            if ta > 1e-6:
                pts += [s0 + d * ta + e * wf, s0 + e * wf]
        else:
            pts = [s0, s1] + top1 + list(reversed(top0))
        hs = G.holes_along(s0, s1, e, hole_in, 12.0, 60.0, P.rivet_hole) if L >= 24.0 else []
        hs = [(c, dd) for c, dd in hs if G.inside_margin(c, pts, nn, 2 * P.rivet_hole - 1e-6)]
        if keep is not None:
            hs = [(c, dd) for c, dd in hs if keep(c, nn)]
        walls.append(S.Wall(name, pts, nn, holes=hs))
        flange_rivets.append((name, hs, nn))
        folds.append(S.Fold(wall, name, s0, s1, name))
    part = S.Part("UT-F", "AIR - SUPPLY TRANSITION - FLOOR", walls, folds, t, P.ut_r, P.k_factor, "BASE", P.dens_al, AL)
    part.flange_rivets = flange_rivets
    return part


def vane(name, V, d_in, d_out, n_lead, n_leg, span_axis, lo, hi, tab_on, tab_dir_lo, tab_dir_hi, lead_len=None,
         leg_len=None):
    """A turning vane, 1 mm aluminium: a straight lead along d_in, a curve of inside radius vane_r turning 90 degrees
    to d_out, a straight leg along d_out. V is the corner where the lead's and the leg's outer (convex) faces meet;
    n_lead, n_leg those faces' outward normals. The vane spans span_axis from lo to hi, wall face to wall face, and
    the end tabs fold off its lead or leg ('lead' / 'leg') onto those faces, toward tab_dir_lo / tab_dir_hi."""
    t, r = P.vane_t, P.vane_r
    dt = (r + t)                                   # a 90 degree fold's tangent distance on the outer skin
    V = np.asarray(V, float)
    a = np.asarray(span_axis, float)
    lead0 = V - d_in * (dt + (P.vane_lead if lead_len is None else lead_len))
    leg1 = V + d_out * (dt + (P.vane_leg if leg_len is None else leg_len))
    plo, phi = V + a * (lo - float(np.dot(V, a))), V + a * (hi - float(np.dot(V, a)))
    lead = [lead0 + (plo - V), V + (plo - V), V + (phi - V), lead0 + (phi - V)]
    leg = [V + (plo - V), leg1 + (plo - V), leg1 + (phi - V), V + (phi - V)]
    h_tab = (1.0 + t) * math.tan(math.pi / 4) + 0.4
    h_turn = (r + t) + 0.4
    rel = 5.0
    if tab_on == "leg":
        lp, lh = leg, [h_tab, 0.3, h_tab, h_turn]       # edges: lo end (tab), free end, hi end (tab), the curve
        fixed = {(0, "prev"): rel, (3, "next"): rel}            # the curve's ends; the tabs start past its zone
        poly_t, used_t = _relieve(lp, lh, fixed, amin=2.0)
        poly_o, used_o = _relieve(lead, [0.3, h_turn, 0.3, 0.3], {(1, "next"): rel, (2, "prev"): rel}, amin=2.0)
        tab_wall_poly, tab_edges = lp, (0, 2)
    else:
        lp, lh = lead, [h_tab, h_turn, h_tab, 0.3]      # edges: lo end (tab), the curve, hi end (tab), free end
        fixed = {(1, "next"): rel, (2, "prev"): rel}
        poly_t, used_t = _relieve(lp, lh, fixed, amin=2.0)
        poly_o, used_o = _relieve(leg, [0.3, 0.3, 0.3, h_turn], {(3, "next"): rel, (0, "prev"): rel}, amin=2.0)
        tab_wall_poly, tab_edges = lp, (0, 2)
    W = []
    lead_name, leg_name = name + " LEAD", name + " LEG"
    if tab_on == "leg":
        W += [S.Wall(leg_name, poly_t, n_leg), S.Wall(lead_name, poly_o, n_lead)]
    else:
        W += [S.Wall(lead_name, poly_t, n_lead), S.Wall(leg_name, poly_o, n_leg)]
    curve = (V + (plo - V) + a * rel, V + (phi - V) - a * rel)
    folds = [S.Fold(lead_name, leg_name, curve[0], curve[1], name + " CURVE", r=r)]
    owner = leg_name if tab_on == "leg" else lead_name
    holes = []
    for ei, tdir, tag in ((tab_edges[0], tab_dir_lo, "LO"), (tab_edges[1], tab_dir_hi, "HI")):
        n_ = len(tab_wall_poly)
        K0, K1 = tab_wall_poly[ei], tab_wall_poly[(ei + 1) % n_]
        d = G.unit(K1 - K0)
        s0, s1 = K0 + used_t[(ei, "next")] * d, K1 - used_t[((ei + 1) % n_, "prev")] * d
        tn = np.asarray(tdir, float)
        e = G.unit(tn - np.dot(tn, d) * d)
        tab_n = a * (-1.0 if tag == "LO" else 1.0)          # a tab's outer skin faces the wall it lies on
        tw = P.vane_tab
        tname = "%s TAB %s" % (name, tag)
        c = (s0 + s1) / 2 + e * (tw / 2)
        # a tab on the shell's back wall is bonded, not riveted: DR's panel is 2.36 mm behind that wall
        riveted = float(np.dot(tab_n, Y)) < 0.99
        W.append(S.Wall(tname, [s0, s1, s1 + e * tw, s0 + e * tw], tab_n, holes=[(c, P.rivet_hole)] if riveted else []))
        folds.append(S.Fold(owner, tname, s0, s1, tname))
        if riveted:
            holes.append((c, tab_n))
    part = S.Part("UT-V", name, W, folds, t, 1.0, P.k_factor, owner, P.dens_al, "Aluminium 5052-H32, 1.0 mm (alloy HOLD)")
    part.tab_holes = holes
    return part


def vanes():
    """The two vane sets. Over the box (the turn from up to across): vane1_n vanes along the mitre from the outlet's
    left edge under the roof (X 733, Z 2110) to its right edge at the box's top (X 927, Z 1950), spanning the duct's
    depth wall to wall, tabs on their legs riveted to the front and back walls. Beside the box (the turn from across
    to back, into the window): two vanes standing floor to roof, tabs on their leads riveted to the floor and roof."""
    F = frame()
    t = F["t"]
    yf_in, yb_in = F["yf"] + t, F["yb"] - t
    zr_in, zf_in = F["zr"] - t, F["zf"] + t
    out = []
    x_a, z_a, x_b, z_b = P.sb_x0 + P.sb_t + P.sb_lin_t, zr_in, P.sb_x1 - P.sb_t - P.sb_lin_t, P.sb_z0 + P.sb_h
    n = int(P.vane1_n)
    for i in range(1, n + 1):
        V = np.array([x_a + (x_b - x_a) * i / (n + 1), 0.0, z_a + (z_b - z_a) * i / (n + 1)])
        out.append(vane("AIR - SUPPLY TRANSITION - VANE A%d" % i, V, Z, X, -X, Z, Y, yf_in, yb_in, "leg", -Z, -Z))
    # beside the box: each vane's lead (25, carrying its tabs) starts past the box's right side, and its leg ends
    # short of the back wall; the outer one keeps 24 mm inside the facet wall
    for i, (vx, vy) in enumerate(((1045.0, -690.0), (1092.0, -735.0))):
        V = np.array([vx, vy, 0.0])
        out.append(vane("AIR - SUPPLY TRANSITION - VANE B%d" % (i + 1), V, X, Y, -Y, X, Z, zf_in, zr_in, "lead", Y, Y,
                        lead_len=25.0, leg_len=6.0))
    return out


def _wall_of(part, c, n_hint):
    """The wall of a part whose outer skin holds point c (within 0.01 mm) and faces n_hint, or None."""
    for w in part.walls.values():
        if abs(float(np.dot(c - w.pts[0], w.n))) < 1e-2 and float(np.dot(w.n, n_hint)) > 0.99:
            return w.name
    return None


def parts():
    """The upper transition's parts with their rivet holes matched: the shell, the floor and the vanes.
    - the shell's corner tabs and the floor's flanges: their rivets through the walls they lie on;
    - the vanes' tabs: through the shell's front and back walls (the vanes over the box) or its roof and the
      floor's base (the vanes beside the box);
    - the front skirt: rivets into the box's front wall (drilled at assembly through these holes); the left skirt
      sits on the box's lined end wall, sealed only;
    - the floor's back flange on the box's back wall: rivets drilled through the box's wall at assembly, set from
      inside the duct before the shell goes on.
    No other hole: each would leak air into DR."""
    F = frame()
    t = F["t"]
    sh0, fl0, vs = shell(), floor(), vanes()
    sh_holes, fl_holes = {}, {}

    def add(store, part, c, n, d=None):
        name = _wall_of(part, c, n)
        if name is None:
            raise ValueError("no wall of %s under a rivet at %s" % (part.name, np.round(c, 2)))
        store.setdefault(name, []).append((c, d or P.rivet_hole))
    for tname, hs, pn in sh0.tab_rivets:
        for c, _d in hs:
            add(sh_holes, sh0, c + pn * (t + TAB_GAP), pn)
    for fname, hs, nn in fl0.flange_rivets:
        for c, _d in hs:
            if not rivet_ok(c, nn):
                continue
            if fname == "FLANGE BOX BACK":
                continue                                 # the box's back wall is drilled at assembly
            add(sh_holes, sh0, c + nn * t, nn)
    for v in vs:
        for c, n in v.tab_holes:
            target = fl0 if n[2] < -0.99 else sh0
            add(fl_holes if target is fl0 else sh_holes, target, c + n * t, n)
    # the front skirt's rivets into the box's front wall, between the box's end linings
    zs = (P.ut_skirt_z + P.sb_z0 + P.sb_h) / 2
    for x in np.linspace(LINING_X0 + 15.0, LINING_X1 - 15.0, 4):
        sh_holes.setdefault("FRONT", []).append((np.array([x, F["yf"], zs]), P.rivet_hole))
    sh1, fl1 = shell(sh_holes), floor(fl_holes, keep=lambda c, n: rivet_ok(c, n))
    return sh1, fl1, vs



LINING_X0 = P.sb_x0 + P.sb_t + P.sb_lin_t          # the box's free outlet between its 50 mm end linings
LINING_X1 = P.sb_x1 - P.sb_t - P.sb_lin_t


def rivet_ok(c, n):
    """A rivet through the shell or the box may go here: not through the shell's back wall (DR's removable panel is
    2.36 mm behind it), not through the shell's right wall within 6 mm of DR's bolt-line tube's depth, not through the
    box's walls where its linings are."""
    if float(np.dot(n, Y)) > 0.99:                       # a flange or tab on the back wall
        return False
    if float(np.dot(n, X)) > 0.99:
        # the right wall beside DR's bolt-line tube (its front face Y c04_by, its left face X bolt_tube_x0): the head
        # (HEAD_D across, HEAD_H proud) keeps 6 mm to the tube's corner
        dx = P.bolt_tube_x0 - P.ut_right_x - R.HEAD_H
        lim = P.c04_by - math.sqrt(max(0.0, 6.0 ** 2 - dx ** 2)) - R.HEAD_D / 2
        if c[1] > lim:
            return False
    if float(np.dot(n, -Y)) > 0.99 and abs(c[1] - (P.sb_y1 + P.ut_c)) < 1e-6:
        return LINING_X0 + 10.0 <= c[0] <= LINING_X1 - 10.0     # the box's back wall: between its linings
    return True


if __name__ == "__main__":
    F = frame()
    print("facet B %s C %s" % (np.round(F["B"], 2), np.round(F["C"], 2)))
    sh_, fl_, vs_ = parts()
    for part in [sh_, fl_] + vs_:
        sh = part.solid()
        n, ok, vol, bb = S.solid_checks(sh)
        print(part.name, "solids", n, "valid", ok, "volume %.1f (expected %.1f)" % (vol, part.expected_volume()),
              "mass %.3f kg" % (vol * 1e-9 * part.density), "box", [round(v, 2) for v in bb])
        for b in part.bend_lines():
            print("   %-22s %7.3f deg %-4s BA %.4f" % (b[0], b[3], b[4], b[5]))
