"""The lower transition (in place of 618103): from the intake riser's top to the supply fan box's bottom, in 1 mm
galvanised steel, built as two wrappers and two cheeks (the Lead's rulings 2026-11-01: the shop build, and the
riser kink rounded, step-bent to about R 100).

The duct is an offset: the air rises out of the riser (inside 137 x 148), turns about 62 degrees left through a
rounded throat, runs up a straight slant that widens toward the box, and turns back up into the box (inside 294 x
149).
- The left wrapper is the duct's left wall: a collar that slips 25 mm into the riser's top, four step bends that
  make the throat's radius, the slant, a kink, and a collar that slips 20 mm into the box's bottom. Both its edges
  carry flanges that lie on the cheeks' inside faces, notched at every bend: square where the bend opens them,
  mitred where it closes them.
- The right wrapper is the duct's right wall: collar, kink, slant, kink, collar, flanged the same way.
- The two cheeks are the front and back walls, one part: a plate with two small kinks (about 4 degrees), because
  the box sits 13.5 mm further forward than the riser. The back cheek is the front one moved back (placements()).
Rivets join the flanges to the cheeks, and the collars to the riser's and the box's walls (those walls drilled at
assembly through the collars' holes); every joint is sealed.

Pod coordinates, mm. Each wall is given by its outer skin, the duct's outside."""

import math

import numpy as np

import geom3 as G
import sheetmetal as S
from tr_params import P

STEEL = "Galvanised steel DX51D+Z, 1.0 mm"
X, Y, Z = np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])


def levels():
    """The collars' outer outlines and the levels."""
    d = dict(bx0=P.rs_x0 + P.rs_t + P.lt_cr, bx1=P.rs_x1 - P.rs_t - P.lt_cr,
             by0=P.rs_y0 + P.rs_t + P.lt_cr, by1=P.rs_y1 - P.rs_t - P.lt_cr,
             tx0=P.sb_x0 + P.sb_t + P.lt_cb, tx1=P.sb_x1 - P.sb_t - P.lt_cb,
             zb0=P.rs_z1 - P.lt_hb, zr=P.rs_z1, zk2=P.sb_z0, zt1=P.sb_z0 + P.lt_ht)
    d["cheek_shift"] = d["by1"] - d["by0"] - P.lt_t     # the back cheek: the front one moved this far back
    d["ty0"] = d["by0"] - P.lt_lean                       # the front cheek's outer face over the box
    return d


def left_profile():
    """The left wrapper's outer skin in (X, Z): the collar, the rounded throat (the circumscribed polygon of an arc
    whose air side has radius lt_throat_r), the slant to the box's left collar, the collar. (points, turn rad)."""
    L = levels()
    ro = P.lt_throat_r - P.lt_t              # the outer skin is nearer the centre, which is outside the duct
    cx, cz = L["bx0"] - ro, L["zr"]
    tx, tz = L["tx0"], L["zk2"]

    def f(th):                                 # zero when the tangent at th passes through the box's left collar
        return (cx - tx) * math.cos(th) + ro - (tz - cz) * math.sin(th)
    lo, hi = math.radians(10), math.radians(85)
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    th = (lo + hi) / 2
    n = int(P.lt_throat_n)
    step = th / n
    rv = ro / math.cos(step / 2)
    pts = [np.array([L["bx0"], L["zb0"]])]
    for j in range(1, n + 1):
        ph = (j - 0.5) * step
        pts.append(np.array([cx + rv * math.cos(ph), cz + rv * math.sin(ph)]))
    pts += [np.array([tx, tz]), np.array([tx, L["zt1"]])]
    return pts, th


def right_profile():
    """The right wrapper's outer skin: it kinks where the left one's first step is, the cheek's kink."""
    L = levels()
    zk1 = left_profile()[0][1][1]
    return [np.array([L["bx1"], L["zb0"]]), np.array([L["bx1"], zk1]), np.array([L["tx1"], L["zk2"]]),
            np.array([L["tx1"], L["zt1"]])]


def cheek_planes():
    """The front cheek's three facets' outer skin planes (point, normal facing the duct's outside): below its first
    kink, the lean, and over the box's edge; and the two kink levels."""
    L = levels()
    zk1 = left_profile()[0][1][1]
    a = np.array([L["bx0"], L["by0"], zk1])
    b = np.array([L["bx0"], L["ty0"], L["zk2"]])
    return (a, -Y), G.plane(a, a + X, b, -Y), (b, -Y), zk1, L["zk2"]


def _plane_y(pl, x, z):
    p, n = pl
    return p[1] - (n[0] * (x - p[0]) + n[2] * (z - p[2])) / n[1]


def _facet(z, zk1, zk2, eps=1e-6):
    return 0 if z <= zk1 + eps else (1 if z <= zk2 + eps else 2)


def _h(theta_rad):
    """How far a wall's outline must run square to a fold at the fold's end: its tangent distance and a margin."""
    return (P.lt_r + P.lt_t) * math.tan(theta_rad / 2) + 0.4


def _angle(n1, n2):
    return math.acos(max(-1.0, min(1.0, float(np.dot(G.unit(n1), G.unit(n2))))))


def relieved(pts, edge_h, fixed=None, amin=None):
    """A wall polygon with a relief at every corner (edge i runs pts[i] to pts[i + 1]; edge_h[i] how long the outline
    must run square to it). Returns (polygon, {(corner, 'prev' or 'next'): relief length along that edge})."""
    amin = P.lt_relief if amin is None else amin
    fixed = fixed or {}
    out, used = [], {}
    n = len(pts)
    for i in range(n):
        A, K, B = pts[i - 1], pts[i], pts[(i + 1) % n]
        a1, a2 = G.relief_need(K, A, B, edge_h[i - 1], edge_h[i], amin, fixed.get((i, "prev")), fixed.get((i, "next")))
        kp, _l1, _l2 = G.kite(K, A, B, a1, a2)
        out += kp
        used[(i, "prev")], used[(i, "next")] = a1, a2
    return out, used


def edge_seg(pts, used, i):
    """Edge i's fold segment, between the reliefs at its two ends."""
    n = len(pts)
    K0, K1 = pts[i], pts[(i + 1) % n]
    d = G.unit(K1 - K0)
    return K0 + used[(i, "next")] * d, K1 - used[((i + 1) % n, "prev")] * d


def wrapper(side):
    """The left or right wrapper: web segments along its profile, a flange on each cheek per segment."""
    t = P.lt_t
    L = levels()
    prof = left_profile()[0] if side == "LEFT" else right_profile()
    low, mid, up, zk1, zk2 = cheek_planes()
    planes_f = [G.offset(p, -t) for p in (low, mid, up)]                   # the front cheek's inside faces
    planes_b = [(p + Y * L["cheek_shift"], n) for p, n in (low, mid, up)]  # the back cheek's inside faces
    out_sign = -1.0 if side == "LEFT" else 1.0
    m = len(prof) - 1
    corners = []
    for k in range(m + 1):
        x, z = prof[k]
        fi = _facet(z, zk1, zk2)            # a point on a cheek kink is on both facets: the same Y
        corners.append((np.array([x, _plane_y(planes_f[fi], x, z), z]), np.array([x, _plane_y(planes_b[fi], x, z), z])))
    dirs = [G.unit(np.array([prof[k + 1][0] - prof[k][0], 0.0, prof[k + 1][1] - prof[k][1]])) for k in range(m)]
    normals = [G.unit(np.array([d[2], 0.0, -d[0]]) * out_sign) for d in dirs]
    seg_pts, seg_h, seg_facet = [], [], []
    for k in range(m):
        (fk, bk), (fk1, bk1) = corners[k], corners[k + 1]
        fi = _facet((prof[k][1] + prof[k + 1][1]) / 2, zk1, zk2)
        h_fold = _h(_angle(normals[k], -planes_f[fi][1]))
        h_lo = _h(_angle(normals[k - 1], normals[k])) if k > 0 else 0.3
        h_hi = _h(_angle(normals[k], normals[k + 1])) if k < m - 1 else 0.3
        seg_pts.append([fk, fk1, bk1, bk])          # edges: front flange fold, step above, back flange fold, step below
        seg_h.append([h_fold, h_hi, h_fold, h_lo])
        seg_facet.append(fi)
    # each step fold is shared by two web segments: its reliefs are the larger of the two segments' needs
    first = [relieved(seg_pts[k], seg_h[k])[1] for k in range(m)]
    fixed = [dict() for _ in range(m)]
    # a flange that leans toward a cheek kink must end far enough from it that its square end stays on its facet
    SQ, MARGIN = 2.5, 0.6
    for k in range(m):
        ez = -normals[k][2]                      # the flange runs into the duct, along the web's inside normal
        dz = dirs[k][2]
        need = (SQ * abs(ez) + MARGIN) / max(dz, 1e-9) + 0.3
        top_kink = abs(prof[k + 1][1] - zk1) < 1e-6 or abs(prof[k + 1][1] - zk2) < 1e-6
        bot_kink = abs(prof[k][1] - zk1) < 1e-6 or abs(prof[k][1] - zk2) < 1e-6
        if ez > 1e-6 and top_kink:
            fixed[k][(1, "prev")] = max(need, first[k][(1, "prev")])
            fixed[k][(2, "next")] = max(need, first[k][(2, "next")])
        if ez < -1e-6 and bot_kink:
            fixed[k][(0, "next")] = max(need, first[k][(0, "next")])
            fixed[k][(3, "prev")] = max(need, first[k][(3, "prev")])
    for k in range(m - 1):
        ua, ub = first[k], first[k + 1]
        s_front = max(ua[(1, "next")], ub[(0, "prev")])
        s_back = max(ua[(2, "prev")], ub[(3, "next")])
        fixed[k][(1, "next")], fixed[k][(2, "prev")] = s_front, s_back
        fixed[k + 1][(0, "prev")], fixed[k + 1][(3, "next")] = s_front, s_back
    polys, useds = zip(*[relieved(seg_pts[k], seg_h[k], fixed[k]) for k in range(m)])
    names = ["%s WEB %d" % (side, k + 1) for k in range(m)]
    holes_web = {k: [] for k in range(m)}
    for k in (0, m - 1):                    # the collars' rivets, through the riser's or the box's wall at assembly
        (fk, bk), (fk1, bk1) = corners[k], corners[k + 1]
        zc = (L["zb0"] + P.rs_z1) / 2 if k == 0 else (L["zk2"] + L["zt1"]) / 2
        a = fk + (fk1 - fk) * (zc - fk[2]) / (fk1[2] - fk[2])
        b = bk + (bk1 - bk) * (zc - bk[2]) / (bk1[2] - bk[2])
        holes_web[k] = G.holes_along(a, b, np.zeros(3), 0.0, 22.0, 70.0, P.rivet_hole)
    walls = [S.Wall(names[k], polys[k], normals[k], holes=holes_web[k]) for k in range(m)]
    folds = []
    for k in range(m - 1):
        s = edge_seg(seg_pts[k], useds[k], 1)
        folds.append(S.Fold(names[k], names[k + 1], s[0], s[1], "%s STEP %d" % (side, k + 1)))
    flange_holes = []
    for k in range(m):
        for which, ei in (("FRONT", 0), ("BACK", 2)):
            s0, s1 = edge_seg(seg_pts[k], useds[k], ei)
            if np.dot(s1 - s0, dirs[k]) < 0:            # s0 at the segment's lower end, next to segment k - 1
                s0, s1 = s1, s0
            fpl = (planes_f if which == "FRONT" else planes_b)[seg_facet[k]]
            n_c = fpl[1] if which == "FRONT" else -fpl[1]        # the flange's outer skin faces its cheek
            # the flange's own plane through its fold line, within microns of the cheek's facet (a shared corner
            # sits on the facet below; the inside faces of two facets meet a few hundredths off the kink line)
            e0 = G.unit(np.cross(n_c, s1 - s0))
            n_f = G.unit(np.cross(s1 - s0, e0))
            if np.dot(n_f, n_c) < 0:
                n_f = -n_f
            e = G.unit(np.cross(n_f, s1 - s0))
            if np.dot(e, -normals[k]) < 0:                        # toward the duct's inside
                e = -e
            w = P.lt_flange_w
            ends = []
            for end_pt, other, nb in ((s0, s1, k - 1), (s1, s0, k + 1)):
                dd = G.unit(end_pt - other)                      # along the fold, outward at this end
                sq = end_pt + e * SQ                             # square to the fold past its zone
                closes = False
                if 0 <= nb < m:
                    lo_, hi_ = (k, nb) if nb > k else (nb, k)
                    closes = float(np.dot(dirs[hi_] - dirs[lo_], e)) > 0     # the bend turns toward the flange
                if closes:
                    half = _angle(normals[k], normals[nb]) / 2
                    ends.append((sq, sq + e * (w - SQ) - dd * ((w - SQ) * math.tan(half) + 0.5)))
                else:
                    ends.append((sq, end_pt + e * w))
            poly = [s0, s1, ends[1][0], ends[1][1], ends[0][1], ends[0][0]]
            zlo = (L["zb0"], zk1, zk2)[seg_facet[k]]
            zhi = (zk1, zk2, L["zt1"])[seg_facet[k]]
            if seg_facet[k] > 0:
                poly = G.clip_z(poly, zlo + 0.6, keep_below=False)      # stay on the cheek's facet under it
            if seg_facet[k] < 2:
                poly = G.clip_z(poly, zhi - 0.6, keep_below=True)
            fname = "%s FLANGE %s %d" % (side, which, k + 1)
            seglen = float(np.linalg.norm(s1 - s0))
            hs = G.holes_along(s0, s1, e, P.flange_hole_in, 9.0, P.rivet_pitch, P.rivet_hole) if seglen >= 18.0 else []
            # a rivet keeps 2 diameters to the flange's every edge, and its hole stays on the cheek's facet under it
            fpoly = poly
            hs = [(c, d) for c, d in hs if G.inside_margin(c, fpoly, n_f, 2 * P.rivet_hole - 1e-6)
                  and _facet(c[2], zk1, zk2) == seg_facet[k]
                  and min(abs(c[2] - zk1), abs(c[2] - zk2)) > P.rivet_hole]
            walls.append(S.Wall(fname, poly, n_f, holes=hs))
            folds.append(S.Fold(names[k], fname, s0, s1, fname))
            flange_holes += [(c, d, which, n_f) for c, d in hs]
    part = S.Part("LT-%s" % side[0], "AIR - RISER TRANSITION - %s WRAPPER" % side, walls, folds, t, P.lt_r,
                  P.k_factor, names[0], P.dens_steel, STEEL)
    part.flange_holes = flange_holes
    return part


def cheek(flange_holes):
    """The cheek, at the front: three facets and two small kinks, holes for the wrappers' front flanges' rivets and
    for its collar's two rivets into the riser's wall (none into the box: the lip angle covers the box's front)."""
    t = P.lt_t
    L = levels()
    low, mid, up, zk1, zk2 = cheek_planes()
    lp, rp = left_profile()[0], right_profile()

    def on(pl, x, z):
        return np.array([x, _plane_y(pl, x, z), z])
    lowp = [on(low, L["bx0"], L["zb0"]), on(low, L["bx1"], L["zb0"]), on(low, L["bx1"], zk1), on(low, L["bx0"], zk1)]
    midp = [on(mid, *lp[1]), on(mid, *rp[1]), on(mid, *rp[2])] + [on(mid, *q) for q in reversed(lp[2:-1])]
    upp = [on(up, L["tx0"], zk2), on(up, L["tx1"], zk2), on(up, L["tx1"], L["zt1"]), on(up, L["tx0"], L["zt1"])]
    k1, k2, free = _h(_angle(low[1], mid[1])), _h(_angle(mid[1], up[1])), 0.3
    h_low, h_mid, h_up = [free, free, k1, free], [k1, free, k2] + [free] * (len(midp) - 3), [k2, free, free, free]
    _r, ul = relieved(lowp, h_low, amin=1.0)
    _r, um = relieved(midp, h_mid, amin=1.0)
    _r, uu = relieved(upp, h_up, amin=1.0)
    a_k1r, a_k1l = max(ul[(2, "next")], um[(1, "prev")]), max(ul[(3, "prev")], um[(0, "next")])
    a_k2r, a_k2l = max(um[(2, "next")], uu[(1, "prev")]), max(um[(3, "prev")], uu[(0, "next")])
    lowr, ul = relieved(lowp, h_low, {(2, "next"): a_k1r, (3, "prev"): a_k1l}, amin=1.0)
    midr, um = relieved(midp, h_mid, {(1, "prev"): a_k1r, (0, "next"): a_k1l, (2, "next"): a_k2r, (3, "prev"): a_k2l},
                        amin=1.0)
    upr, uu = relieved(upp, h_up, {(1, "prev"): a_k2r, (0, "next"): a_k2l}, amin=1.0)
    s1, s2 = edge_seg(lowp, ul, 2), edge_seg(midp, um, 2)
    holes = [[], [], []]
    facets = (low, mid, up)
    for c, d, which, n_f in flange_holes:
        if which == "FRONT":
            cc = c + n_f * t                  # through the cheek: its outer skin is t outside the flange's
            fi = _facet(cc[2], zk1, zk2)
            p, n = facets[fi]
            holes[fi].append((cc - float(np.dot(cc - p, n)) * n, d))     # on the facet's outer skin exactly
    zc = (L["zb0"] + P.rs_z1) / 2
    for x in (L["bx0"] + 32.0, L["bx1"] - 45.0):         # clear of the wrappers' flanges, and of the riser's facet corner
        holes[0].append((on(low, x, zc), P.rivet_hole))
    walls = [S.Wall("CHEEK LOW", lowr, -Y, holes=holes[0]), S.Wall("CHEEK MID", midr, mid[1], holes=holes[1]),
             S.Wall("CHEEK UP", upr, -Y, holes=holes[2])]
    folds = [S.Fold("CHEEK LOW", "CHEEK MID", s1[0], s1[1], "CHEEK KINK 1"),
             S.Fold("CHEEK MID", "CHEEK UP", s2[0], s2[1], "CHEEK KINK 2")]
    return S.Part("LT-C", "AIR - RISER TRANSITION - CHEEK", walls, folds, t, P.lt_r, P.k_factor, "CHEEK MID",
                  P.dens_steel, STEEL)


def parts():
    """(left wrapper, right wrapper, cheek at the front)."""
    lw, rw = wrapper("LEFT"), wrapper("RIGHT")
    return lw, rw, cheek(lw.flange_holes + rw.flange_holes)


def placements():
    """[(part, translation)]: the four pieces of the lower transition in the pod."""
    L = levels()
    return [("LT-L", (0, 0, 0)), ("LT-R", (0, 0, 0)), ("LT-C", (0, 0, 0)), ("LT-C", (0, L["cheek_shift"], 0))]


if __name__ == "__main__":
    prof, th = left_profile()
    print("throat turn %.2f deg, first step at Z %.2f" % (math.degrees(th), prof[1][1]))
    print("left profile", [tuple(np.round(p, 2)) for p in prof])
    print("right profile", [tuple(np.round(p, 2)) for p in right_profile()])
    for Xp in parts():
        sh = Xp.solid()
        n, ok, vol, bb = S.solid_checks(sh)
        print(Xp.name, "solids", n, "valid", ok, "volume %.1f (expected %.1f)" % (vol, Xp.expected_volume()),
              "mass %.3f kg" % (vol * 1e-9 * Xp.density), "box", [round(v, 2) for v in bb])
