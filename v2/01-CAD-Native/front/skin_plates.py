"""Plate solvers for the decor blocks' skin span check (D-131): numpy only, so any repo python runs them.

- navier_rect: the exact centre deflection of a simply supported rectangle under a centre point load (Navier
  double series), the reference the others are checked against.
- ss_fd: a simply supported bay of any shape on a raster (cells of h mm): the plate equation split into two
  Poisson problems with zero edges (Navier's split, exact for straight-edged convex bays), each solved by
  conjugate gradients on the 5-point Laplacian. Its zero line sits half a cell outside the bay, so it reads a
  little high (on the safe side): 1 % at h = 1 mm, 1.4 % at h = 2 mm on the rectangles below.
- bfs: Bogner-Fox-Schmit plate elements (bicubic Hermite: w, w_x, w_y, w_xy per node) on a raster, for bays with
  free edges (pockets, slots, open joints). Held nodes: w = 0 (simple support) or w = w_x = w_y = 0 (clamped);
  every other edge is free. Solved by block Cholesky across the bay's shorter side. Exact to 0.02 % on simply
  supported rectangles at h = 10 mm, and a free-edged strip reads as a beam; but a simple support along a
  staircase (an edge at an angle to the raster) acts as a clamp, so bfs is only used where the simply supported
  edges run along the raster (or, for a clamped edge, at any angle).
- fsm: finite strips for a folded skin between two ring tubes (a prism with diaphragm ends): bending (D) and
  membrane action (the two 0.21 mm aluminium skins) in each strip, harmonics along the length. It shows how
  well a fold with no tube behind it holds its line.

    python3 skin_plates.py        # prints the self-test against the series (about 2 minutes)

Sources and statuses (as WALL's make_acp_spans.py):
- skin: 3 mm ACP with 0.21 mm aluminium skins, PE core (HW-SEL A1): source
- E 70 000 MPa and Poisson 0.33 for the skins: source (handbook values for aluminium)
- D = E t d^2 / (2 (1 - nu^2)), d = 3 - 0.21 between the skins' centres, the core left out: calculation
- membrane stiffness of the two skins, E 2 t / (1 - nu^2), the core left out: calculation
"""
import math

import numpy as np

E, NU, T_SKIN, T_PANEL = 70000.0, 0.33, 0.21, 3.0
D_ACP = E * T_SKIN * (T_PANEL - T_SKIN) ** 2 / (2 * (1 - NU * NU))
A_ACP = E * 2 * T_SKIN / (1 - NU * NU)


# ---------------------------------------------------------------- reference

def navier_rect(a, b, P=100.0, D=D_ACP, N=1501):
    """exact centre deflection (mm) of a simply supported a x b rectangle under P (N) at its centre."""
    m = np.arange(1, N + 1, 2, dtype=float)
    M, Nn = np.meshgrid(m, m, indexing="ij")
    return 4 * P / (math.pi ** 4 * a * b * D) * float((1.0 / ((M / a) ** 2 + (Nn / b) ** 2) ** 2).sum())


# ---------------------------------------------------------------- simply supported bay, Navier's split

def _lap(phi, mask, h):
    p = np.zeros((phi.shape[0] + 2, phi.shape[1] + 2))
    p[1:-1, 1:-1] = np.where(mask, phi, 0.0)
    out = (p[2:, 1:-1] + p[:-2, 1:-1] + p[1:-1, 2:] + p[1:-1, :-2] - 4 * p[1:-1, 1:-1]) / (h * h)
    return np.where(mask, out, 0.0)


def _poisson(mask, rhs, h, tol=1e-10, maxit=200000):
    """-lap x = rhs on the mask, x = 0 outside, by conjugate gradients."""
    x = np.zeros_like(rhs)
    r = np.where(mask, rhs, 0.0)
    p = r.copy()
    rs = float((r * r).sum())
    r0 = math.sqrt(rs)
    for _it in range(maxit):
        Ap = -_lap(p, mask, h)
        a = rs / float((p * Ap).sum())
        x += a * p
        r -= a * Ap
        rn = float((r * r).sum())
        if math.sqrt(rn) < tol * r0:
            return x
        p = r + (rn / rs) * p
        rs = rn
    raise RuntimeError("conjugate gradients did not converge")


def ss_fd(mask, h, load, P=100.0, D=D_ACP):
    """deflection (mm) at the load cell (j, i) of a simply supported bay (bool mask of h mm cells)."""
    j, i = load
    b = np.zeros(mask.shape)
    b[j, i] = P / D / (h * h)
    m = _poisson(mask, b, h)            # m = -lap w: lap lap w = P delta / D
    w = _poisson(mask, m, h)
    return float(w[j, i])


# ---------------------------------------------------------------- Bogner-Fox-Schmit plate elements

def _hermite(xi, h):
    f = [1 - 3 * xi ** 2 + 2 * xi ** 3, h * (xi - 2 * xi ** 2 + xi ** 3), 3 * xi ** 2 - 2 * xi ** 3, h * (-xi ** 2 + xi ** 3)]
    d1 = [(-6 * xi + 6 * xi ** 2) / h, 1 - 4 * xi + 3 * xi ** 2, (6 * xi - 6 * xi ** 2) / h, -2 * xi + 3 * xi ** 2]
    d2 = [(-6 + 12 * xi) / h ** 2, (-4 + 6 * xi) / h, (6 - 12 * xi) / h ** 2, (-2 + 6 * xi) / h]
    return f, d1, d2


def _element_k(h, D, nu=NU):
    """16 x 16 stiffness of an h x h element; nodes (0,0), (1,0), (1,1), (0,1), each (w, w_x, w_y, w_xy)."""
    g, wts = np.polynomial.legendre.leggauss(5)
    g, wts = (g + 1) / 2, wts / 2
    nodes = [(0, 0), (1, 0), (1, 1), (0, 1)]
    C = D * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    K = np.zeros((16, 16))
    for xi, wx in zip(g, wts):
        fx, dx, ddx = _hermite(xi, h)
        for eta, wy in zip(g, wts):
            fy, dy, ddy = _hermite(eta, h)
            B = np.zeros((3, 16))
            for a, (ia, ja) in enumerate(nodes):
                vx, sx = (0, 1) if ia == 0 else (2, 3)
                vy, sy = (0, 1) if ja == 0 else (2, 3)
                for k, (px, py) in enumerate([(vx, vy), (sx, vy), (vx, sy), (sx, sy)]):
                    B[0, 4 * a + k] = ddx[px] * fy[py]
                    B[1, 4 * a + k] = fx[px] * ddy[py]
                    B[2, 4 * a + k] = 2 * dx[px] * dy[py]
            K += B.T @ C @ B * wx * wy * h * h
    return K


def bfs(cells, held, load, h, P=100.0, D=D_ACP, clamped=None):
    """deflection (mm) at the load node (j, i) of a plate made of the True cells (h mm squares) under P there.
    held: bool (nv + 1, nu + 1) nodes with w = 0; clamped: nodes with w = w_x = w_y = 0 too; other edges free."""
    return float(bfs_field(cells, held, [(load, P)], h, D, clamped)[load])


def bfs_field(cells, held, loads, h, D=D_ACP, clamped=None):
    """nodal deflections (nv + 1, nu + 1) under loads [((j, i), P)], as bfs."""
    if cells.shape[1] > cells.shape[0]:             # run the blocks across the shorter side (isotropic plate)
        return bfs_field(cells.T.copy(), held.T.copy(), [((j, i)[::-1], P) for (j, i), P in loads], h, D,
                         None if clamped is None else clamped.T.copy()).T
    nv, nu = cells.shape
    Ke = _element_k(h, D)
    ncol, nrow = nu + 1, nv + 1
    m = 4 * ncol
    A = [np.zeros((m, m)) for _ in range(nrow)]
    B = [np.zeros((m, m)) for _ in range(nrow - 1)]
    nodes = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for j, i in zip(*np.nonzero(cells)):
        for a, (xa, ya) in enumerate(nodes):
            ra, ca = j + ya, i + xa
            for b, (xb, yb) in enumerate(nodes):
                rb, cb = j + yb, i + xb
                blk = Ke[4 * a:4 * a + 4, 4 * b:4 * b + 4]
                if ra == rb:
                    A[ra][4 * ca:4 * ca + 4, 4 * cb:4 * cb + 4] += blk
                elif rb == ra + 1:
                    B[ra][4 * ca:4 * ca + 4, 4 * cb:4 * cb + 4] += blk
    act = np.zeros((nrow, ncol), bool)
    act[:-1, :-1] |= cells
    act[1:, :-1] |= cells
    act[:-1, 1:] |= cells
    act[1:, 1:] |= cells
    rhs = [np.zeros(m) for _ in range(nrow)]
    for (lj, li), P in loads:
        rhs[lj][4 * li] += P
    for r in range(nrow):
        for c in range(ncol):
            fix = [0, 1, 2, 3] if not act[r, c] else []
            if act[r, c] and held[r, c]:
                fix = [0]
            if act[r, c] and clamped is not None and clamped[r, c]:
                fix = [0, 1, 2]
            for d in fix:
                k = 4 * c + d
                A[r][k, :] = 0
                A[r][:, k] = 0
                A[r][k, k] = 1.0
                if r > 0:
                    B[r - 1][:, k] = 0
                if r < nrow - 1:
                    B[r][k, :] = 0
                rhs[r][k] = 0.0
    S, y = [], []
    for r in range(nrow):
        Sr, br = A[r].copy(), rhs[r].copy()
        if r > 0:
            Sr -= B[r - 1].T @ np.linalg.solve(S[-1], B[r - 1])
            br -= B[r - 1].T @ np.linalg.solve(S[-1], y[-1])
        S.append(Sr)
        y.append(br)
    x = [None] * nrow
    for r in range(nrow - 1, -1, -1):
        br = y[r] - (B[r] @ x[r + 1] if r < nrow - 1 else 0)
        x[r] = np.linalg.solve(S[r], br)
    return np.array([[x[r][4 * c] for c in range(ncol)] for r in range(nrow)])


# ---------------------------------------------------------------- finite strips: a folded skin between two rings

def _strip_k(b, k, L, Db=D_ACP, Am=A_ACP, nu=NU):
    g, wt = np.polynomial.legendre.leggauss(6)
    xi, wt = (g + 1) / 2, wt / 2
    Kb, Km = np.zeros((4, 4)), np.zeros((4, 4))
    C = np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    for x, w in zip(xi, wt):
        N = np.array([1 - 3 * x ** 2 + 2 * x ** 3, b * (x - 2 * x ** 2 + x ** 3), 3 * x ** 2 - 2 * x ** 3, b * (-x ** 2 + x ** 3)])
        N1 = np.array([(-6 * x + 6 * x ** 2) / b, 1 - 4 * x + 3 * x ** 2, (6 * x - 6 * x ** 2) / b, -2 * x + 3 * x ** 2])
        N2 = np.array([(-6 + 12 * x) / b ** 2, (-4 + 6 * x) / b, (6 - 12 * x) / b ** 2, (-2 + 6 * x) / b])
        Bb = np.vstack([N2, -k * k * N, 2 * k * N1])
        Kb += Bb.T @ (Db * C) @ Bb * w * b
        Lf, Ld = np.array([1 - x, x]), np.array([-1 / b, 1 / b])
        Bm = np.vstack([np.concatenate([Ld, [0, 0]]), np.concatenate([[0, 0], -k * Lf]), np.concatenate([k * Lf, Ld])])
        Km += Bm.T @ (Am * C) @ Bm * w * b
    K = np.zeros((8, 8))
    K[np.ix_([2, 3, 6, 7], [2, 3, 6, 7])] = Kb          # w1 th1 w2 th2
    K[np.ix_([0, 4, 1, 5], [0, 4, 1, 5])] = Km          # u1 u2 v1 v2
    return K * L / 2


def _strip_t(alpha):
    c, s = math.cos(alpha), math.sin(alpha)
    t = np.array([[c, s, 0, 0], [0, 0, 1, 0], [-s, c, 0, 0], [0, 0, 0, 1]])
    T = np.zeros((8, 8))
    T[:4, :4] = t
    T[4:, 4:] = t
    return T


def polyline(corners, per_mm=5.0):
    """subdivide a cross-section polyline into strips about per_mm wide; returns points and the corners' indices."""
    pts, idx = [tuple(corners[0])], [0]
    for (x1, y1), (x2, y2) in zip(corners, corners[1:]):
        n = max(2, int(round(math.hypot(x2 - x1, y2 - y1) / per_mm)))
        pts += [(x1 + (x2 - x1) * t / n, y1 + (y2 - y1) * t / n) for t in range(1, n + 1)]
        idx.append(len(pts) - 1)
    return pts, idx


def fsm(pts, held, load, L, P=100.0, mmax=299):
    """deflection (mm), normal to the skin, at cross-section node `load` and mid-length, of a folded skin between
    two ring tubes L apart (diaphragm ends); nodes in `held` are held by a tube along the whole length."""
    n = len(pts)
    j = load if load < n - 1 else load - 1
    a = math.atan2(pts[j + 1][1] - pts[j][1], pts[j + 1][0] - pts[j][0])
    nrm = (-math.sin(a), math.cos(a))
    fixed = [4 * h + d for h in held for d in (0, 1, 2)]
    free = [d for d in range(4 * n) if d not in fixed]
    total = np.zeros(4 * n)
    for mm in range(1, mmax + 1, 2):
        k = mm * math.pi / L
        K = np.zeros((4 * n, 4 * n))
        for i in range(n - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            T = _strip_t(math.atan2(y2 - y1, x2 - x1))
            idx = list(range(4 * i, 4 * i + 8))
            K[np.ix_(idx, idx)] += T.T @ _strip_k(math.hypot(x2 - x1, y2 - y1), k, L) @ T
        f = np.zeros(4 * n)
        s = math.sin(k * L / 2)
        f[4 * load] = P * nrm[0] * s
        f[4 * load + 1] = P * nrm[1] * s
        d = np.zeros(4 * n)
        d[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
        total += d * s
    return float(total[4 * load] * nrm[0] + total[4 * load + 1] * nrm[1])


# ---------------------------------------------------------------- self-test

def selftest():
    """rows (case, method, value, reference) proving each solver on a case with a known answer."""
    rows = []
    for a, b in ((373.0, 1078.6), (300.0, 300.0), (179.0, 735.0)):
        ex = navier_rect(a, b)
        for h in (2.0, 1.0):
            nu, nv = int(round(a / h)) | 1, int(round(b / h)) | 1
            hh = math.sqrt(a / nu * b / nv)
            rows.append(("simply supported %.0f x %.1f" % (a, b), "ss_fd, h %.1f" % hh,
                         ss_fd(np.ones((nv, nu), bool), hh, (nv // 2, nu // 2)), ex))
    for a, b, h in ((300.0, 300.0, 10.0), (180.0, 740.0, 10.0)):
        nu, nv = int(a / h), int(b / h)
        held = np.zeros((nv + 1, nu + 1), bool)
        held[0, :] = held[-1, :] = held[:, 0] = held[:, -1] = True
        rows.append(("simply supported %.0f x %.0f" % (a, b), "bfs, h %.0f" % h,
                     bfs(np.ones((nv, nu), bool), held, (nv // 2, nu // 2), h), navier_rect(a, b)))
    # a free-edged strip 600 x 100, simply supported ends, 100 N spread across mid-span: beam theory
    L, b, h = 600.0, 100.0, 10.0
    nu, nv = int(L / h), int(b / h)
    held = np.zeros((nv + 1, nu + 1), bool)
    held[:, 0] = held[:, -1] = True
    loads = [((j, nu // 2), 100.0 * (0.5 if j in (0, nv) else 1.0) / nv) for j in range(nv + 1)]
    W = bfs_field(np.ones((nv, nu), bool), held, loads, h)
    rows.append(("free-edged strip 600 x 100, line load", "bfs, h 10", float(W[nv // 2, nu // 2]),
                 100.0 * L ** 3 / (48 * D_ACP * (1 - NU ** 2) * b)))
    # folded strips: a flat face between two held edges is the simply supported rectangle
    pts, _idx = polyline([(0, 0), (300, 0)], per_mm=10)
    rows.append(("simply supported 300 x 734 as one flat strip set", "fsm",
                 abs(fsm(pts, [0, len(pts) - 1], len(pts) // 2, 734.0)), navier_rect(300, 734)))
    return rows


if __name__ == "__main__":
    for case, method, val, ref in selftest():
        print("%-45s %-14s %.4f mm  reference %.4f  (%+.2f%%)" % (case, method, val, ref, 100 * (val / ref - 1)))
