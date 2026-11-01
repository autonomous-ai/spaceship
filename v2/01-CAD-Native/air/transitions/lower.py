"""The lower transition (in place of 618103): from the intake riser's top to the supply fan box's bottom, made as
two folded halves of 1 mm galvanised steel (the Lead's ruling 2026-11-01: the shop build).

The duct is an offset of four plane walls, from the riser's outline at Z 1445 to the box's at Z 1650: the left and
right walls lean left (about 53.5 and 30.3 degrees off vertical), the front and back walls lean forward about 4
degrees, since the box sits 13.5 mm further forward than the riser. Each wall kinks to vertical at both ends into a
collar that slips inside the riser's top (25 deep) and inside the box's bottom (20 deep), riveted through and
sealed. Half A is the left wall and the front wall, folded at their common corner; half B the right wall and the
back wall. Each half carries a seam flange that laps inside the other half's wall: the front wall's flange on the
right wall, the back wall's flange on the left wall. Corners where two folds meet get a relief.

Pod coordinates, mm. Every wall is given by its outer skin (the duct's outside)."""

import math

import numpy as np

import geom3 as G
import sheetmetal as S
from tr_params import P

STEEL = "Galvanised steel DX51D+Z, 1.0 mm"


def outlines():
    """The collars' outer outlines: (x0, x1, y0, y1) at the riser and at the box, and the four levels."""
    bot = (P.rs_x0 + P.rs_t + P.lt_cr, P.rs_x1 - P.rs_t - P.lt_cr, P.rs_y0 + P.rs_t + P.lt_cr, P.rs_y1 - P.rs_t - P.lt_cr)
    top = (P.sb_x0 + P.sb_t + P.lt_cb, P.sb_x1 - P.sb_t - P.lt_cb, P.sb_y0 + P.sb_t + P.lt_cb, P.sb_y1 - P.sb_t - P.lt_cb)
    z = (P.rs_z1 - P.lt_hb, P.rs_z1, P.sb_z0, P.sb_z0 + P.lt_ht)
    return bot, top, z


def corners():
    (bx0, bx1, by0, by1), (tx0, tx1, ty0, ty1), (_zb0, zk1, zk2, _zt1) = outlines()
    a = np.array
    return dict(bFL=a([bx0, by0, zk1]), bFR=a([bx1, by0, zk1]), bBL=a([bx0, by1, zk1]), bBR=a([bx1, by1, zk1]),
                tFL=a([tx0, ty0, zk2]), tFR=a([tx1, ty0, zk2]), tBL=a([tx0, ty1, zk2]), tBR=a([tx1, ty1, zk2]))


def planes():
    K = corners()
    return dict(L=G.plane(K["bFL"], K["bBL"], K["tFL"], (-1, 0, 0)), R=G.plane(K["bFR"], K["bBR"], K["tFR"], (1, 0, 0)),
                F=G.plane(K["bFL"], K["bFR"], K["tFL"], (0, -1, 0)), B=G.plane(K["bBL"], K["bBR"], K["tBL"], (0, 1, 0)))


def _h(theta_rad):
    """The length a wall's outline must run square to a fold at the fold's end: the fold's tangent distance on
    its outer skin, at most (r + t) tan(angle / 2), and a margin."""
    return (P.lt_r + P.lt_t) * math.tan(theta_rad / 2) + 0.4


def _angle(n1, n2):
    return math.acos(max(-1.0, min(1.0, float(np.dot(G.unit(n1), G.unit(n2))))))


def relieved(pts, edge_h, fixed=None, amin=None):
    """A wall polygon with a relief at every corner. Edge i runs from pts[i] to pts[i + 1]; edge_h[i] is how long
    the outline must run square to that edge at its ends (0.3 for a free edge). fixed {(corner, 'prev' or 'next'):
    a} pins a relief's length along an edge (a fold two walls share). Returns (polygon, {(corner, side): a})."""
    amin = P.lt_relief if amin is None else amin
    fixed = fixed or {}
    n = len(pts)
    out, used = [], {}
    for i in range(n):
        A, K, B = pts[i - 1], pts[i], pts[(i + 1) % n]
        a1, a2 = G.relief_need(K, A, B, edge_h[i - 1], edge_h[i], amin, fixed.get((i, "prev")), fixed.get((i, "next")))
        kp, _l1, _l2 = G.kite(K, A, B, a1, a2)
        out += kp
        used[(i, "prev")], used[(i, "next")] = a1, a2
    return out, used


def edge_seg(pts, used, i):
    """Edge i's fold segment, between the two reliefs at its ends."""
    n = len(pts)
    K0, K1 = pts[i], pts[(i + 1) % n]
    d = G.unit(K1 - K0)
    return K0 + used[(i, "next")] * d, K1 - used[((i + 1) % n, "prev")] * d


def shared(pts_a, h_a, ia, pts_b, h_b, ib):
    """Reliefs for a fold two walls share: edge ia of wall a is edge ib of wall b, run the other way. Each end's
    relief along the fold is the larger of the two walls' needs, so the fold segment is the same in both."""
    _pa, ua = relieved(pts_a, h_a)
    _pb, ub = relieved(pts_b, h_b)
    na, nb = len(pts_a), len(pts_b)
    # wall a's edge ia: corner ia ('next') to corner ia+1 ('prev'); in wall b the same line runs from corner ib+1
    # ('prev' side at its end) ... b's edge ib goes from pts_b[ib] (= a's corner ia+1) to pts_b[ib+1] (= a's ia)
    s0 = max(ua[(ia, "next")], ub[((ib + 1) % nb, "prev")])
    s1 = max(ua[((ia + 1) % na, "prev")], ub[(ib, "next")])
    fa = {(ia, "next"): s0, ((ia + 1) % na, "prev"): s1}
    fb = {((ib + 1) % nb, "prev"): s0, (ib, "next"): s1}
    return fa, fb


def _tab(seg, direction, depth):
    """A collar tab hanging from a kink segment: [s0, s1, s1 + v, s0 + v]."""
    s0, s1 = seg
    v = np.asarray(direction, float) * depth
    return [s0, s1, s1 + v, s0 + v]


def _flange(seg, plane, toward, width):
    """A seam flange in `plane` from the fold segment, width toward `toward`: its outline."""
    s0, s1 = seg
    _p, n = plane
    e = G.unit(np.cross(n, s1 - s0))
    if np.dot(e, toward) < 0:
        e = -e
    return [s0, s1, s1 + e * width, s0 + e * width], e


def _collar_holes(seg, direction, depth, n_out, end=20.0, pitch=70.0, only=None):
    """Rivet holes along a collar tab's middle, on its outer skin."""
    s0, s1 = seg
    mid = np.asarray(direction, float) * depth / 2
    hs = G.holes_along(s0 + mid, s1 + mid, np.zeros(3), 0.0, end, pitch, P.rivet_hole)
    if only is not None:
        hs = [h for h in hs if only(h[0])]
    return hs


def halves():
    """(half A, half B) as sheetmetal.Part, in pod coordinates."""
    t, r, k = P.lt_t, P.lt_r, P.k_factor
    (bx0, bx1, by0, by1), (tx0, tx1, ty0, ty1), (zb0, zk1, zk2, zt1) = outlines()
    K = corners()
    PL = planes()
    Li, Ri = G.offset(PL["L"], -t), G.offset(PL["R"], -t)

    def at_z(line, z):
        return G.line_plane(line, (np.array([0, 0, z]), np.array([0, 0, 1.0])))
    FRs = G.plane_line(PL["F"], Ri)          # half A's seam fold: the front wall meets the right wall's inside
    BLs = G.plane_line(PL["B"], Li)          # half B's seam fold: the back wall meets the left wall's inside
    bFRs, tFRs = at_z(FRs, zk1), at_z(FRs, zk2)
    bBLs, tBLs = at_z(BLs, zk1), at_z(BLs, zk2)
    up, down = np.array([0, 0, 1.0]), np.array([0, 0, -1.0])

    nL, nR, nF, nB = PL["L"][1], PL["R"][1], PL["F"][1], PL["B"][1]
    X, Y = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    free = 0.3

    # ---------------- half A: the left wall (base) and the front wall, folded at their corner
    Lp = [K["bFL"], K["bBL"], K["tBL"], K["tFL"]]       # edges: kink L1, back edge (free), kink L2, corner fold
    hL = [_h(_angle(nL, -X)), free, _h(_angle(nL, -X)), _h(_angle(nL, nF))]
    Fp = [K["bFL"], K["tFL"], tFRs, bFRs]               # edges: corner fold, kink F2, seam fold, kink F1
    hF = [_h(_angle(nL, nF)), _h(_angle(nF, -Y)), _h(_angle(nF, nR)), _h(_angle(nF, -Y))]
    fa, fb = shared(Lp, hL, 3, Fp, hF, 0)
    LM, uL = relieved(Lp, hL, fa)
    FM, uF = relieved(Fp, hF, fb)
    fl = edge_seg(Lp, uL, 3)
    lb, lt = edge_seg(Lp, uL, 0), edge_seg(Lp, uL, 2)
    fb_, ft_, fs = edge_seg(Fp, uF, 3), edge_seg(Fp, uF, 1), edge_seg(Fp, uF, 2)
    FS, eFS = _flange(fs, Ri, (0, 1, 0), P.seam_w)
    seam_a = G.holes_along(fs[0], fs[1], eFS, P.seam_hole_in, P.rivet_end, P.rivet_pitch, P.rivet_hole)

    # ---------------- half B: the right wall (base) and the back wall, folded at their corner
    Rp = [K["bFR"], K["tFR"], K["tBR"], K["bBR"]]       # edges: front edge (free), kink R2, corner fold, kink R1
    hR = [free, _h(_angle(nR, X)), _h(_angle(nR, nB)), _h(_angle(nR, X))]
    Bp = [K["bBR"], K["tBR"], tBLs, bBLs]               # edges: corner fold, kink B2, seam fold, kink B1
    hB = [_h(_angle(nR, nB)), _h(_angle(nB, Y)), _h(_angle(nB, nL)), _h(_angle(nB, Y))]
    ra, rb_fix = shared(Rp, hR, 2, Bp, hB, 0)
    RM, uR = relieved(Rp, hR, ra)
    BM, uB = relieved(Bp, hB, rb_fix)
    br = edge_seg(Rp, uR, 2)
    rb, rt = edge_seg(Rp, uR, 3), edge_seg(Rp, uR, 1)
    bb, bt, bs = edge_seg(Bp, uB, 3), edge_seg(Bp, uB, 1), edge_seg(Bp, uB, 2)
    BS, eBS = _flange(bs, Li, (0, -1, 0), P.seam_w)
    seam_b = G.holes_along(bs[0], bs[1], eBS, P.seam_hole_in, P.rivet_end, P.rivet_pitch, P.rivet_hole)

    walls_a = [
        S.Wall("LEFT WALL", LM, nL, holes=[(c + nL * t, d) for c, d in seam_b]),
        S.Wall("FRONT WALL", FM, nF),
        S.Wall("LEFT COLLAR - RISER", _tab(lb, down, P.lt_hb), -X, holes=_collar_holes(lb, down, P.lt_hb, -X)),
        S.Wall("LEFT COLLAR - BOX", _tab(lt, up, P.lt_ht), -X, holes=_collar_holes(lt, up, P.lt_ht, -X)),
        S.Wall("FRONT COLLAR - RISER", _tab(fb_, down, P.lt_hb), -Y,
               holes=_collar_holes(fb_, down, P.lt_hb, -Y, only=lambda c: c[0] < P.rs_x1 - 40)),
        S.Wall("FRONT COLLAR - BOX", _tab(ft_, up, P.lt_ht), -Y),          # no rivets under the lip angle
        S.Wall("FRONT SEAM FLANGE", FS, nR, holes=seam_a),
    ]
    folds_a = [S.Fold("LEFT WALL", "FRONT WALL", fl[0], fl[1], "CORNER"),
               S.Fold("LEFT WALL", "LEFT COLLAR - RISER", lb[0], lb[1], "KINK L1"),
               S.Fold("LEFT WALL", "LEFT COLLAR - BOX", lt[0], lt[1], "KINK L2"),
               S.Fold("FRONT WALL", "FRONT COLLAR - RISER", fb_[0], fb_[1], "KINK F1"),
               S.Fold("FRONT WALL", "FRONT COLLAR - BOX", ft_[0], ft_[1], "KINK F2"),
               S.Fold("FRONT WALL", "FRONT SEAM FLANGE", fs[0], fs[1], "SEAM")]
    walls_b = [
        S.Wall("RIGHT WALL", RM, nR, holes=[(c + nR * t, d) for c, d in seam_a]),
        S.Wall("BACK WALL", BM, nB),
        S.Wall("RIGHT COLLAR - RISER", _tab(rb, down, P.lt_hb), X, holes=_collar_holes(rb, down, P.lt_hb, X)),
        S.Wall("RIGHT COLLAR - BOX", _tab(rt, up, P.lt_ht), X, holes=_collar_holes(rt, up, P.lt_ht, X)),
        S.Wall("BACK COLLAR - RISER", _tab(bb, down, P.lt_hb), Y, holes=_collar_holes(bb, down, P.lt_hb, Y)),
        S.Wall("BACK COLLAR - BOX", _tab(bt, up, P.lt_ht), Y, holes=_collar_holes(bt, up, P.lt_ht, Y)),
        S.Wall("BACK SEAM FLANGE", BS, nL, holes=seam_b),
    ]
    folds_b = [S.Fold("RIGHT WALL", "BACK WALL", br[0], br[1], "CORNER"),
               S.Fold("RIGHT WALL", "RIGHT COLLAR - RISER", rb[0], rb[1], "KINK R1"),
               S.Fold("RIGHT WALL", "RIGHT COLLAR - BOX", rt[0], rt[1], "KINK R2"),
               S.Fold("BACK WALL", "BACK COLLAR - RISER", bb[0], bb[1], "KINK B1"),
               S.Fold("BACK WALL", "BACK COLLAR - BOX", bt[0], bt[1], "KINK B2"),
               S.Fold("BACK WALL", "BACK SEAM FLANGE", bs[0], bs[1], "SEAM")]
    A = S.Part("LT-A", "AIR - RISER TRANSITION - HALF A (LEFT AND FRONT)", walls_a, folds_a, t, r, k, "LEFT WALL",
               P.dens_steel, STEEL)
    B = S.Part("LT-B", "AIR - RISER TRANSITION - HALF B (RIGHT AND BACK)", walls_b, folds_b, t, r, k, "RIGHT WALL",
               P.dens_steel, STEEL)
    return A, B


if __name__ == "__main__":
    A, B = halves()
    for X in (A, B):
        sh = X.solid()
        n, ok, vol, bb = S.solid_checks(sh)
        print(X.name, "solids", n, "valid", ok, "volume %.1f (expected %.1f)" % (vol, X.expected_volume()),
              "mass %.3f kg" % (vol * 1e-9 * X.density), "box", [round(v, 2) for v in bb])
        for b in X.bend_lines():
            print("   %-8s %7.3f deg %-4s BA %.4f" % (b[0], b[3], b[4], b[5]))
