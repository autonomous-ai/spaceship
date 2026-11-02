"""The transitions' rivets: each hole's mate, the stack it closes (the sheets and their thickness, the grip the
Joints register picks the rivet for), and the set rivet's head and tail as solids, so the clearance and overlap
checks see them.

A hole's mate is a hole of another sheet (or of the same part's other wall: the shell's corner tabs) on the same
axis, the two outer skins no further apart than the two sheets. A hole with no mate goes through the fan box's or
the riser's wall, drilled at assembly through it; any other lone hole is a fault.

The rivet is set from the stack's outer face (outside the duct), its tail on the far side, except where that face
is inside the fan box (the floor's flange on the box's back wall): there it is set from inside the duct, before the
shell goes on, and its tail is inside the box."""

import numpy as np

from tr_params import P

# the set rivet's envelope (source: the Joints Engineer's pick, 2026-11-01, ISO 15973 closed end, aluminium body and
# steel mandrel, the maker's sheets): a dome head 12 across and 2.5 high; and a closed-end tail 7 across standing 8
# proud of the stack (assumption: the body less the grip, plus its closed end)
HEAD_D, HEAD_H = 12.0, 2.5
TAIL_D, TAIL_L = 7.0, 8.0
# the rivet for each grip (the Joints Engineer's pick): 4 x 8 (grip 0.5 to 3.5), 4 x 9.5 (3.5 to 5.0), and for the
# 5.0 stacks, which sit on the line between two lengths, a 1.0 aluminium washer under the head and 4 x 11 (5.0 to 6.5)
RIVETS = ((3.5, "4 x 8", 0.0), (4.5, "4 x 9.5", 0.0), (5.5, "4 x 11, a 1.0 aluminium washer under the head", 1.0))


def rivet_for(grip):
    """(the rivet, the washer's thickness under its head) for a stack's grip."""
    for top, name, washer in RIVETS:
        if grip <= top + 1e-9:
            return name, washer
    raise ValueError("no rivet picked for a %.1f grip" % grip)

STEEL_GALV = "galvanised steel"
ALU = "aluminium"


def _mat(material):
    return STEEL_GALV if "steel" in material.lower() else ALU


def walls_of_others():
    """The fan box's and the riser's walls a lone hole may go through: (name, axis, outer face along the axis,
    thickness, material, the box's inside lies toward -axis or +axis of the wall, bounds)."""
    bx0, bx1, by0, by1 = P.sb_x0, P.sb_x1, P.sb_y0, P.sb_y1
    z0, z1, tb = P.sb_z0, P.sb_z0 + P.sb_h, P.sb_t
    rx0, rx1, ry0, ry1 = P.rs_x0, P.rs_x1, P.rs_y0, P.rs_y1
    out = []
    # (name, outward axis, outer face coordinate along the axis, thickness, material, box: (x, y, z) bounds)
    for name, ax, face, lo, hi in (
            ("FAN BOX FRONT WALL", np.array([0.0, -1, 0]), -by0, (bx0, by0, z0), (bx1, by0 + tb, z1)),
            ("FAN BOX BACK WALL", np.array([0.0, 1, 0]), by1, (bx0, by1 - tb, z0), (bx1, by1, z1)),
            ("FAN BOX LEFT WALL", np.array([-1.0, 0, 0]), -bx0, (bx0, by0, z0), (bx0 + tb, by1, z1)),
            ("FAN BOX RIGHT WALL", np.array([1.0, 0, 0]), bx1, (bx1 - tb, by0, z0), (bx1, by1, z1))):
        out.append(dict(name=name, n=ax, face=face, t=tb, mat=ALU, lo=np.array(lo), hi=np.array(hi), box=True))
    for name, ax, face, lo, hi in (
            ("RISER FRONT WALL", np.array([0.0, -1, 0]), -ry0, (rx0, ry0, 252.0), (rx1, ry0 + P.rs_t, P.rs_z1)),
            ("RISER BACK WALL", np.array([0.0, 1, 0]), ry1, (rx0, ry1 - P.rs_t, 252.0), (rx1, ry1, P.rs_z1)),
            ("RISER LEFT WALL", np.array([-1.0, 0, 0]), -rx0, (rx0, ry0, 252.0), (rx0 + P.rs_t, ry1, P.rs_z1)),
            ("RISER RIGHT WALL", np.array([1.0, 0, 0]), rx1, (rx1 - P.rs_t, ry0, 252.0), (rx1, ry1, P.rs_z1))):
        out.append(dict(name=name, n=ax, face=face, t=P.rs_t, mat=STEEL_GALV, lo=np.array(lo), hi=np.array(hi),
                        box=False))
    return out


def inside_box(p):
    """Inside the fan box's casing (its air space)."""
    return (P.sb_x0 + P.sb_t < p[0] < P.sb_x1 - P.sb_t and P.sb_y0 + P.sb_t < p[1] < P.sb_y1 - P.sb_t
            and P.sb_z0 < p[2] < P.sb_z0 + P.sb_h)


def holes(pieces, inside_out=()):
    """Every hole of every placed copy: key, copy, wall, centre on the face toward the duct's outside, that face's
    normal, diameter, the sheet's thickness and material. A copy in inside_out ((key, copy number)) has its outer skin
    toward the duct's inside (the back cheek is the front one moved back), so its holes are taken on its other face."""
    out = []
    for key, part, copies in pieces:
        for ci, mv in enumerate(copies):
            mv = np.asarray(mv, float)
            flip = (key, ci + 1) in inside_out
            for w in part.walls.values():
                for c, d in w.holes:
                    c = np.asarray(c, float) + mv
                    n = w.n.copy()
                    if flip:
                        c, n = c - n * part.t, -n
                    out.append(dict(key=key, copy=ci + 1, wall=w.name, c=c, n=n, d=float(d), t=part.t,
                                    mat=_mat(part.material)))
    return out


def stacks(pieces, tol=0.05, inside_out=()):
    """The rivets: [dict(sheets=[hole, ...] outermost first, other=the box's or riser's wall or None, grip (the
    sheets' thicknesses), gap (any slip clearance or tab gap left in the stack), axis, base (the axis through the
    origin's foot), s_out and s_in (the stack's outer and inner faces along the axis), head_dir (+1: set from the
    outer face)] and the faults (lone holes with no wall to go into)."""
    hs = holes(pieces, inside_out)
    others = walls_of_others()
    used = [False] * len(hs)
    out, faults = [], []
    for i, a in enumerate(hs):
        if used[i]:
            continue
        used[i] = True
        group = [a]
        for j in range(i + 1, len(hs)):
            b = hs[j]
            if used[j] or abs(abs(float(np.dot(a["n"], b["n"]))) - 1.0) > 1e-6:
                continue
            dv = b["c"] - a["c"]
            ax = float(np.dot(dv, a["n"]))
            if np.linalg.norm(dv - ax * a["n"]) > tol or abs(ax) > a["t"] + b["t"] + 0.5:
                continue
            group.append(b)
            used[j] = True
        n = group[0]["n"]
        # each sheet's span along the axis (low, high): from its outer skin through its thickness, along its own normal
        spans = [tuple(sorted((float(np.dot(h["c"], n)), float(np.dot(h["c"] - h["n"] * h["t"], n))))) for h in group]
        order = np.argsort([-s[1] for s in spans])
        group = [group[k] for k in order]
        spans = [spans[k] for k in order]
        s_out, s_in = spans[0][1], spans[-1][0]
        other = None
        if len(group) == 1:
            c = group[0]["c"]
            for w in others:
                if abs(abs(float(np.dot(w["n"], n))) - 1.0) > 1e-6:
                    continue
                lo, hi = w["lo"], w["hi"]
                inside = all(lo[k] - 1e-6 <= c[k] <= hi[k] + 1e-6 for k in range(3) if abs(n[k]) < 0.5)
                if not inside:
                    continue
                wn = float(np.dot(n, w["n"]))                             # +1 or -1
                w_out = w["face"] * wn                                    # the wall's outer face along n
                w_in = w_out - w["t"] * wn
                w_lo, w_hi = min(w_out, w_in), max(w_out, w_in)
                if abs(w_lo - s_out) < 0.6 or abs(w_hi - s_in) < 0.6:     # the sheet lies on it, either side
                    other = dict(w, lo_s=w_lo, hi_s=w_hi)
                    break
            if other is None:
                faults.append("a hole with no mate: %s %d %s at %s" % (group[0]["key"], group[0]["copy"],
                                                                         group[0]["wall"], np.round(c, 2)))
                continue
            s_out, s_in = max(s_out, other["hi_s"]), min(s_in, other["lo_s"])
        c0 = group[0]["c"]
        base = c0 - n * float(np.dot(c0, n))
        outer, inner = group[0], group[-1]
        # the head on the stack's outer face, the tail past its inner face: on a sheet's own face (its own normal),
        # or on the box's or riser's wall face when that wall is the outermost or innermost layer
        if other is not None and other["hi_s"] >= spans[0][1] - 1e-9:
            head_c, head_n = base + n * other["hi_s"], n.copy()
        else:
            head_c, head_n = outer["c"].copy(), outer["n"].copy()
        if other is not None and other["lo_s"] <= spans[-1][0] + 1e-9:
            tail_c, tail_n = base + n * other["lo_s"], -n
        else:
            tail_c, tail_n = inner["c"] - inner["n"] * inner["t"], -inner["n"]
        head_dir = 1.0
        if inside_box(head_c + head_n * (HEAD_H / 2)):
            head_dir = -1.0                                               # set from inside the duct
            head_c, head_n, tail_c, tail_n = tail_c, tail_n, head_c, head_n
        grip = sum(h["t"] for h in group) + (other["t"] if other else 0.0)
        rivet, washer = rivet_for(grip)
        out.append(dict(sheets=group, other=other, grip=round(grip, 3), gap=round(s_out - s_in - grip, 3), axis=n,
                        base=base, s_out=s_out, s_in=s_in, head_dir=head_dir, head_c=head_c, head_n=head_n,
                        tail_c=tail_c, tail_n=tail_n, rivet=rivet, washer=washer))
    return out, faults


def describe(st):
    """The stack in words: 'aluminium 2.0 + aluminium 2.0' or 'galvanised steel 1.0 + fan box 3.0 (aluminium)'."""
    bits = ["%s %.1f" % (h["mat"], h["t"]) for h in st["sheets"]]
    if st["other"]:
        bits.append("%s %.1f (%s)" % (st["other"]["name"].lower(), st["other"]["t"], st["other"]["mat"]))
    return " + ".join(bits)


def solids(sts):
    """Each rivet's head (with its washer, if any) and tail as cylinders: [(name, shape)]."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    def cyl(p, d, r, h):
        return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*map(float, p)), gp_Dir(*map(float, d))), r, h).Shape()
    out = []
    for i, st in enumerate(sts):
        head = cyl(st["head_c"], st["head_n"], HEAD_D / 2, HEAD_H + st["washer"])
        tail = cyl(st["tail_c"], st["tail_n"], TAIL_D / 2, TAIL_L)
        f = BRepAlgoAPI_Fuse(head, tail)
        f.Build()
        h0 = st["sheets"][0]
        out.append(("RIVET %d %s %d %s" % (i + 1, h0["key"], h0["copy"], h0["wall"]), f.Shape()))
    return out


def table(sts):
    """Counts per kind of stack: {(description, grip, rivet): count}."""
    out = {}
    for st in sts:
        k = (describe(st), st["grip"], st["rivet"])
        out[k] = out.get(k, 0) + 1
    return out
