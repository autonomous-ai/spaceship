"""TABULATED drawings (D-89 part 1): parts of one shape family on one sheet, each part number in the table.

Made for blanks cut from sheet or batt whose outline has square notches through the thickness (the WALL cavity
fill bays): each piece's outline comes from the exact projection of its STEP solid along its thickness, and the
notches are read from that outline (the cells of the outline's own grid that lie inside the piece's box but
outside the piece). A piece whose outline has an edge at an angle or a curve is refused: that is not this kind.
"""

import math
import os

import geom
import inputs
import project
from compose import NotDrawable, Part, VD, fmt, scale_text, title_block, ISO_SCALES
from geom import vdot, axis_name
from project import View
from sheet import Sheet, W_VIS, W_THIN


def find_step(pn, team):
    """The part's own STEP, else the team assembly STEP that holds it (with the revision of that file)."""
    own = inputs.own_step(pn)
    if own:
        return own
    folder = os.path.join(inputs.MANUF, team)
    for f in sorted(os.listdir(folder)):
        nm = inputs.parse_name(os.path.join(folder, f))
        if not nm or nm["doc"] != "STEP":
            continue
        try:
            for name, solids in geom.read_step(os.path.join(folder, f)):
                if geom.part_number_of(name) == pn and solids:
                    return os.path.join(folder, f)
        except RuntimeError:
            continue
    return None


def notches(prims):
    """Square notches through the piece: (x0, y0, w, h) from the outline's lower-left corner, and the box."""
    lines = [p for p in prims if p.vis and p.kind == "line"]
    if any(p.kind != "line" for p in prims if p.vis):
        raise NotDrawable("outline has curves")
    for p in lines:
        if abs(p.p[0] - p.q[0]) > 1e-6 and abs(p.p[1] - p.q[1]) > 1e-6:
            raise NotDrawable("outline has an edge at an angle")
    xs = sorted({round(v, 4) for p in lines for v in (p.p[0], p.q[0])})
    ys = sorted({round(v, 4) for p in lines for v in (p.p[1], p.q[1])})

    def inside(x, y):
        n = 0
        for p in lines:
            (x1, y1), (x2, y2) = p.p, p.q
            if (y1 > y) != (y2 > y):
                xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if xi > x:
                    n += 1
        return n % 2 == 1
    out_cells = set()
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if not inside((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2):
                out_cells.add((i, j))
    # connected groups of outside cells, each a notch
    seen, groups = set(), []
    for c in sorted(out_cells):
        if c in seen:
            continue
        stack, grp = [c], []
        seen.add(c)
        while stack:
            a = stack.pop()
            grp.append(a)
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                b = (a[0] + d[0], a[1] + d[1])
                if b in out_cells and b not in seen:
                    seen.add(b)
                    stack.append(b)
        groups.append(grp)
    x0, y0 = xs[0], ys[0]
    res = []
    for g in groups:
        i0, i1 = min(c[0] for c in g), max(c[0] for c in g) + 1
        j0, j1 = min(c[1] for c in g), max(c[1] for c in g) + 1
        if (i1 - i0) * (j1 - j0) != len(g):
            raise NotDrawable("a cut-out that is not a square notch")
        res.append((xs[i0] - x0, ys[j0] - y0, xs[i1] - xs[i0], ys[j1] - ys[j0]))
    res.sort(key=lambda r: (r[0], r[1]))
    return res, (x0, y0, xs[-1], ys[-1])


class Piece:
    pass


def pieces_of(pn, team):
    step = find_step(pn, team)
    if not step:
        raise NotDrawable("%s: no STEP holds it" % pn)
    bodies, unit = geom.load_part(step, pn)
    b = [bb.box for bb in bodies]
    box = [min(x[k] for x in b) for k in range(3)] + [max(x[3 + k] for x in b) for k in range(3)]
    size = [box[3 + k] - box[k] for k in range(3)]
    k = min(range(3), key=lambda i: size[i])
    # seen from the pod's centre side (the room side), as the frames are
    sign = -1 if box[k] + box[3 + k] > 0 else 1
    n = tuple(float(sign) if i == k else 0.0 for i in range(3))
    name = next(nm for nm, (vn, vx, vy) in project.POD_VIEWS.items() if vdot(vn, n) > 0.9999)
    view = View(name, *project.POD_VIEWS[name])
    out = []
    for bb in bodies:
        pr = [p for p in project.project(bb.shape, view) if p.vis]
        nt, ext = notches(pr)
        pc = Piece()
        pc.pn, pc.body, pc.prims, pc.notches, pc.ext = pn, bb.name, pr, nt, ext
        pc.w, pc.h = ext[2] - ext[0], ext[3] - ext[1]
        pc.t = bb.size[k]
        pc.view = view
        out.append(pc)
    out.sort(key=lambda p: (p.body, p.ext[0]))
    return out, step, unit, view


def make(pns, team, spec, out_path):
    """One TABULATED sheet for the part numbers pns (the first names the file); returns a report."""
    first = Part.__new__(Part)
    first.pn, first.team = pns[0], team
    first.step = find_step(pns[0], team)
    nm = inputs.parse_name(first.step)
    first.rev = nm["rev"] if nm["pn"] == pns[0] else None
    first.row, first.cut_rows, first.list_file = inputs.parts_row(pns[0], team)
    if not first.row:
        raise NotDrawable("%s has no parts-list row" % pns[0])
    if first.rev is None:       # a part inside an assembly file: its parts list's revision (the Checker's rule 2)
        first.rev = inputs.parse_name(first.list_file)["rev"]
    first.name = first.row["name"].strip()
    first.name_vi = (first.row.get("name_vi") or "").strip()
    first.file_name = inputs.ascii_name(first.name)
    data = []
    for pn in pns:
        pcs, step, unit, view = pieces_of(pn, team)
        row, _subs, lf = inputs.parts_row(pn, team)
        data.append({"pn": pn, "pieces": pcs, "step": step, "unit": unit, "view": view, "row": row, "list": lf})
    sh = Sheet(spec.get("sheet", "A1"), title="%s %s (TABULATED)" % (first.pn, first.name),
               subject="%s_%s_%s_DWG %s DRAFT" % (first.pn, first.rev, first.file_name, first.rev),
               keywords="drawgen; D-112; D-89 TABULATED; " + "; ".join(
                   "%s %s sha256:%s" % (d["pn"], inputs.rel(d["step"]), inputs.sha12(d["step"])) for d in data))
    W, H = sh.W, sh.H
    # representative views: the first part's pieces, in the order they sit
    rep = data[0]
    scale = spec.get("scale", 0.2)
    x = 40.0
    top = H - 40.0
    vds = []
    for i, pc in enumerate(rep["pieces"]):
        vd = VD(pc.view, pc.prims, scale)
        vd.place_ll(x, top - pc.h * scale)
        for p in pc.prims:
            sh.line(vd.S(p.p), vd.S(p.q), W_VIS)
        e = pc.ext
        a, b = vd.S((e[0], e[1])), vd.S((e[2], e[3]))
        sh.dim_linear((a[0], a[1]), (b[0], a[1]), "down", 8.0, fmt(pc.w), 2.5)
        sh.dim_linear((a[0], a[1]), (a[0], b[1]), "left", 8.0, fmt(pc.h), 2.5)
        for j, (nx, ny, nw, nh) in enumerate(pc.notches, 1):
            c = vd.S((e[0] + nx + nw / 2, e[1] + ny + nh / 2))
            sh.text(c[0], c[1], "N%d" % j, 2.5, "center", valign="mid", bold=True)
        sh.origin_mark(vd.S((e[0], e[1])), "O%d" % (i + 1))
        sh.text((a[0] + b[0]) / 2, a[1] - 20, "%s  %s" % (pc.body, scale_text(scale)), 3.0, "center", bold=True)
        sh.text((a[0] + b[0]) / 2, a[1] - 24, "as %s" % rep["pn"], 2.3, "center")
        vds.append(vd)
        x = b[0] + 46.0
    sh.flush()
    v = rep["view"]
    sh.text(40.0, top - max(pc.h for pc in rep["pieces"]) * scale - 36,
            "Views of %s from the room side, %s; X = %s, Y = %s (pod axes); origin On at each piece's lower-left "
            "corner; +X right, +Y up." % (rep["pn"], project.LOOK_WORDS.get(v.looking, v.looking), axis_name(v.x),
                                          axis_name(v.y)), 2.5)
    # the table
    cols = [("PART", 15, "c"), ("NAME", 58, "l"), ("PIECE", 24, "l"), ("W (mm)", 15, "r"), ("H (mm)", 15, "r"),
            ("T (mm)", 12, "r"), ("NOTCHES THRU: LOWER-LEFT CORNER X, Y AND SIZE (mm) FROM ON", 120, "l")]
    rows = []
    for d in data:
        for i, pc in enumerate(d["pieces"], 1):
            nts = "; ".join("N%d at X %s, Y %s, %s x %s" % (j, fmt(nx), fmt(ny), fmt(nw), fmt(nh))
                            for j, (nx, ny, nw, nh) in enumerate(pc.notches, 1)) or "none"
            rows.append([d["pn"], d["row"]["name"], pc.body, fmt(pc.w), fmt(pc.h), fmt(pc.t), nts])
    tx = max(vd.box()[2] for vd in vds) + 30.0
    tx = min(tx, W - 10 - sum(c[1] for c in cols) - 6)
    ty = sh.table(tx, H - 30.0, cols, rows, size=2.3, row_h=4.6,
                  title=["TABULATED DRAWING (D-89): covers %s" % ", ".join(pns),
                         "each piece seen from the room side; the RH parts are the mirror image of the LH parts; "
                         "upper parts are shorter; every value read from that part's STEP"], title_size=2.6)
    # notes
    row = first.row
    notes = [
        "UNITS: mm. Do not scale the drawing. ISO first-angle projection (ISO 5456-2).",
        "MATERIAL: %s. FINISH: none (as supplied)." % row.get("material", ""),
        "Process: %s." % (row.get("process") or "").rstrip("."),
        "TOLERANCE: %s (parts list)." % (row.get("tolerance") or ""),
        "Notches go through the full thickness; they leave room for the key at each bolt this panel drives "
        "(feature rationale F13).",
        "Sources: " + "; ".join("%s from %s (sha256 %s, declared unit %s, read in mm)" % (
            d["pn"], inputs.rel(d["step"]), inputs.sha12(d["step"]), d["unit"]["declared"]) for d in data) +
        ". Made by tools/drawgen (D-112) from those STEPs: regenerate, never edit the PDF.",
    ]
    nx, ny = 40.0, top - max(pc.h for pc in rep["pieces"]) * scale - 52
    sh.text(nx, ny, "NOTES", 3.0, bold=True)
    ny -= 5
    for i, t in enumerate(notes, 1):
        sh.text(nx, ny, "%d." % i, 2.5)
        ny = sh.paragraph(nx + 5, ny, t, 2.5, 420, lead=1.42) - 1.2
    spec = dict(spec)
    spec["_scale"] = scale
    first.placement = None
    title_block(sh, first, spec, scale, [], "2026-11-01")
    sh.border()
    sh.meta["creationDate"] = "D:20261101000000Z"
    sh.meta["modDate"] = sh.meta["creationDate"]
    sh.data = {"generator": "drawgen 1.0", "pn": first.pn, "rev": first.rev, "tabulated": pns,
               "sources": [{"role": "STEP", "pn": d["pn"], "path": inputs.rel(d["step"]),
                            "sha256_12": inputs.sha12(d["step"])} for d in data],
               "pieces": [{"pn": d["pn"], "body": pc.body, "w": pc.w, "h": pc.h, "t": pc.t, "notches": pc.notches}
                          for d in data for pc in d["pieces"]], "views": [], "features": []}
    sh.save(out_path)
    return {"dwg": "%s_%s_%s_DWG" % (first.pn, first.rev, first.file_name), "rows": len(rows)}
