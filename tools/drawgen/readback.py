"""Read a generated drawing back and check it against its STEP, independently of how it was drawn.

What it checks (the brief's acceptance tests):
1. every hole the repo's own STEP reader finds (tools/checks/stepfile.py: no OCC) is in a hole table, and each
   table row's X and Y equal the hole's centre projected into that table's view, from the drawing's origin,
   within 0.05 mm;
2. each tagged hole is drawn in its view as a true circle (cubic Bezier quarter arcs on one centre and radius,
   never a polygon), at the place its STEP centre projects to, within 0.05 mm true size, and the view's origin
   mark sits on the origin;
3. the drawing's text carries what the mechanical check reads (UNITS: mm, MATERIAL, FINISH, TOLERANCE,
   X (mm), Y (mm), a section label when holes go through two walls) and the PDF's Creator is drawgen.

The view placement comes from the drawing's own data (catalog key /DrawgenData); a wrong placement makes the
circles miss the STEP centres, so it can't hide an error.
"""

import json
import csv
import math
import os
import re
import sys

import fitz

MM = 72.0 / 25.4
TOL = 0.05

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))


def _stepfile():
    p = os.path.join(REPO, "tools", "checks")
    if p not in sys.path:
        sys.path.insert(0, p)
    import stepfile
    return stepfile


def read_data(doc):
    t, v = doc.xref_get_key(doc.pdf_catalog(), "DrawgenData")
    if t != "string":
        raise ValueError("no /DrawgenData in the PDF")
    return json.loads(v)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def table_rows(page):
    """{tag: (x, y, size)} from the hole tables' text: a line that starts with a tag and two numbers."""
    # each cell is its own text item, so a row is the words on one baseline (within 0.6 pt)
    words = sorted(page.get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    lines, cur, cy = {}, None, None
    for w in words:
        y = (w[1] + w[3]) / 2
        if cy is None or abs(y - cy) > 0.6:
            cur = len(lines)
            cy = y
            lines[cur] = []
        lines[cur].append(w)
    rows = {}
    for ws in lines.values():
        ws.sort(key=lambda w: w[0])
        words = [w[4] for w in ws]
        for i in range(len(words) - 3):
            if re.fullmatch(r"H\d{2}", words[i]):
                try:
                    x, y = float(words[i + 1]), float(words[i + 2])
                except ValueError:
                    continue
                rows[words[i]] = (x, y, words[i + 3])
    return rows


def pdf_circles(page, sheet_h):
    """Closed paths made only of cubic Beziers whose ends and mid-points lie on one circle: (cx, cy, r, n) in
    sheet mm (y up)."""
    out = []
    for d in page.get_drawings():
        items = d["items"]
        if not items or any(it[0] != "c" for it in items):
            continue
        pts = []
        for it in items:
            p0, c1, c2, p1 = it[1], it[2], it[3], it[4]
            pts.append((p0, c1, c2, p1))
        ends = [(p[0].x / MM, sheet_h - p[0].y / MM) for p in pts]
        cx = sum(e[0] for e in ends) / len(ends)
        cy = sum(e[1] for e in ends) / len(ends)
        r = sum(math.hypot(e[0] - cx, e[1] - cy) for e in ends) / len(ends)
        if r <= 0:
            continue
        ok = True
        for p0, c1, c2, p1 in pts:
            # the curve's mid-point (t = 0.5) on the same circle
            mx = (p0.x + 3 * c1.x + 3 * c2.x + p1.x) / 8 / MM
            my = sheet_h - (p0.y + 3 * c1.y + 3 * c2.y + p1.y) / 8 / MM
            e = (p0.x / MM, sheet_h - p0.y / MM)
            if abs(math.hypot(mx - cx, my - cy) - r) > 1e-3 * r + 1e-4 or abs(math.hypot(e[0] - cx, e[1] - cy) - r) > 1e-4 + 1e-4 * r:
                ok = False
                break
        closed = math.dist((pts[0][0].x, pts[0][0].y), (pts[-1][3].x, pts[-1][3].y)) < 1e-3
        if ok and closed:
            out.append((cx, cy, r, len(pts)))
    return out


def text_boxes(page, sheet_h):
    """Every text item's box in sheet mm (x0, y0, x1, y1, text), one per span the PDF holds."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            upright = abs(ln.get("dir", (1, 0))[0]) < 0.5        # written up or down the sheet
            for sp in ln.get("spans", []):
                t = sp["text"].strip()
                if not t:
                    continue
                x0, y0, x1, y1 = sp["bbox"]
                out.append((x0 / MM, sheet_h - y1 / MM, x1 / MM, sheet_h - y0 / MM, t, upright))
    return out


def _ink_box(b, size_cut=0.2):
    """A text box shrunk to its ink: the PDF's box reaches above the capitals and below the baseline (across the
    line, which is the sheet's X for text written upward)."""
    x0, y0, x1, y1, t, upright = b
    if upright:
        w = x1 - x0
        return (x0 + w * size_cut, y0 + 0.1, x1 - w * size_cut, y1 - 0.1, t)
    h = y1 - y0
    return (x0 + 0.1, y0 + h * size_cut, x1 - 0.1, y1 - h * size_cut, t)


def outline_paths(page, sheet_h, width_mm=0.5):
    """The part's visible outlines (strokes of the visible-line width) as point lists in sheet mm (curves sampled
    for the touch test only)."""
    out = []
    for d in page.get_drawings():
        w = d.get("width") or 0
        if d.get("type") not in ("s", "fs") or abs(w / MM - width_mm) > 0.02:
            continue
        for it in d["items"]:
            if it[0] == "l":
                pts = [it[1], it[2]]
            elif it[0] == "c":
                p0, c1, c2, p1 = it[1], it[2], it[3], it[4]
                pts = []
                for k in range(9):
                    t = k / 8.0
                    a, b_, c, e = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
                    pts.append(fitz.Point(a * p0.x + b_ * c1.x + c * c2.x + e * p1.x,
                                          a * p0.y + b_ * c1.y + c * c2.y + e * p1.y))
            else:
                continue
            out.append([(p.x / MM, sheet_h - p.y / MM) for p in pts])
    return out


def _seg_hits_box(p, q, box):
    """True when segment p-q passes through the box (Liang-Barsky clip)."""
    x0, y0, x1, y1 = box[:4]
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            r = qq / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def all_strokes(page, sheet_h):
    """Every line the page draws (strokes, and the edges of fills, any width) as segments in sheet mm; curves as
    short chords."""
    segs = []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                pts = [it[1], it[2]]
            elif it[0] == "c":
                p0, c1, c2, p1 = it[1], it[2], it[3], it[4]
                pts = []
                for k in range(9):
                    t = k / 8.0
                    a, b_, c, e = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
                    pts.append(fitz.Point(a * p0.x + b_ * c1.x + c * c2.x + e * p1.x,
                                          a * p0.y + b_ * c1.y + c * c2.y + e * p1.y))
            elif it[0] == "re":
                r = it[1]
                pts = [r.tl, r.tr, r.br, r.bl, r.tl]
            elif it[0] == "qu":
                q = it[1]
                pts = [q.ul, q.ur, q.lr, q.ll, q.ul]
            else:
                continue
            pp = [(p.x / MM, sheet_h - p.y / MM) for p in pts]
            segs.extend(zip(pp[:-1], pp[1:]))
    return segs


def _c_drawings():
    _stepfile()                 # puts tools/checks on the path
    import c_drawings
    return c_drawings


def note_makers(doc):
    """[(sheet, phrase)] for each note that names a maker other than Autonomous: an agent, a role, a script or tool, a
    team or a person. A process is no maker ("holes made by drilling after welding", "made by bending the flange").
    The Lead's ruling on #302; the rule is the mechanical check's own (tools/checks/c_drawings.py: its reading of
    'made by ...' lines and names_a_maker), so the two can't differ."""
    cd = _c_drawings()
    out = []
    for n, page in enumerate(doc, start=1):
        for phrase, maker in cd._note_makers(page):
            if maker.strip().lower() != "autonomous" and cd.names_a_maker(maker):
                out.append((n, "%s %s" % (phrase, maker)))
    return out


def clashes(doc):
    """On every page: texts that touch each other, texts that touch a part outline, and lines that run through a
    text's letters (a leader or a dimension line that stops at the text doesn't): [(page, what)]."""
    found = []
    for pi, page in enumerate(doc):
        H = page.rect.height / MM
        boxes = [_ink_box(b) for b in text_boxes(page, H)]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    found.append((pi + 1, "text '%s' touches text '%s'" % (a[4][:30], b[4][:30])))
        paths = outline_paths(page, H)
        for a in boxes:
            for pts in paths:
                if any(_seg_hits_box(pts[k], pts[k + 1], a) for k in range(len(pts) - 1)):
                    found.append((pi + 1, "text '%s' touches an outline" % a[4][:30]))
                    break
        cells = {}
        for sg in all_strokes(page, H):
            (x0, y0), (x1, y1) = sg
            for i in range(int(min(x0, x1) // 10), int(max(x0, x1) // 10) + 1):
                for j in range(int(min(y0, y1) // 10), int(max(y0, y1) // 10) + 1):
                    cells.setdefault((i, j), []).append(sg)
        for a in boxes:
            inner = (a[0] + 0.1, a[1] + 0.1, a[2] - 0.1, a[3] - 0.1)
            if inner[0] >= inner[2] or inner[1] >= inner[3]:
                continue
            near = {id(sg): sg for i in range(int(inner[0] // 10), int(inner[2] // 10) + 1)
                    for j in range(int(inner[1] // 10), int(inner[3] // 10) + 1) for sg in cells.get((i, j), ())}
            if any(_seg_hits_box(p, q, inner) for p, q in near.values()):
                found.append((pi + 1, "a line runs through text '%s'" % a[4][:30]))
    return found


def step_holes(step_path, pn):
    """Every hole run of the part's solids in the file's top coordinates, from the repo's STEP reader."""
    sf = _stepfile().StepFile(step_path)
    out = []
    for inst in sf.instances():
        nm = inst["part_number"] or ""
        if not (nm.startswith(pn) or (inst["name"] or "").startswith(pn) or os.path.basename(step_path).startswith(pn + "_")
                or any((x or "").startswith(pn) for x in inst.get("path", ()))):    # a welded frame's members (D-120)
            continue
        s = sf.solid(inst["solid"])
        fr = inst["frame"]
        occ = tuple(round(v, 3) for v in tuple(fr.o) + tuple(fr.x) + tuple(fr.y))   # the occurrence's placement
        for h in s.holes:
            hm = h.moved(fr)
            out.append({"c": tuple(hm.center), "axis": tuple(hm.axis), "dia": hm.diameter, "occ": occ})
    return out


def _num(t):
    try:
        return float(t.split()[0])
    except (ValueError, IndexError, AttributeError):
        return None


def _text_near(texts, want, box, pad=25.0):
    """True when the sheet has the text `want` inside box (sheet mm) grown by pad."""
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    return any(t[4] == want and t[0] >= x0 and t[2] <= x1 and t[1] >= y0 and t[3] <= y1 for t in texts)


def step_faces(step_path, pn, pm=None):
    """Every face of the part's solids from the repo's STEP reader, placed (as step_planes): kind, points, and for a
    cylinder its axis point, direction, radius and whether it is concave."""
    sfm = _stepfile()
    sf = sfm.StepFile(step_path)
    out = []
    for inst in sf.instances():
        nm = inst["part_number"] or ""
        if not (nm.startswith(pn) or (inst["name"] or "").startswith(pn) or os.path.basename(step_path).startswith(pn + "_")
                or any((x or "").startswith(pn) for x in inst.get("path", ()))):    # a welded frame's members (D-120)
            continue
        s = sf.solid(inst["solid"])
        fr = inst["frame"]

        def mv(q):
            q = fr.point(q)
            if pm:
                q = tuple(sum(pm["m"][i][j] * q[j] for j in range(3)) + pm["t"][i] for i in range(3))
            return q

        def rot(v):
            v = fr.vector(v)
            if pm:
                v = tuple(sum(pm["m"][i][j] * v[j] for j in range(3)) for i in range(3))
            return v
        key = (inst["solid"], tuple(round(v, 3) for v in fr.o) + tuple(round(v, 3) for v in fr.x))
        for f in s.faces:
            d = {"kind": f.kind, "pts": [mv(q) for q in f.points], "solid": key}
            if f.kind == "plane" and f.normal is not None:
                d["n"] = rot(f.normal)
            if f.kind == "cylinder" and f.origin is not None:
                d.update({"o": mv(f.origin), "d": rot(f.normal), "r": f.radius, "concave": sfm._concave(f)})
            if f.kind == "conical_surface":     # its edge circles (a countersink's: the hole's and the outer one)
                d["circles"] = [(mv(a[0].o), a[1]) for a in f.arcs]
            out.append(d)
    return out


def open_slot_fails(data, faces, rows, texts, tol=TOL):
    """Each open slot against the STEP (the repo's reader, no OCC): a concave half-round end of its radius on its
    axis; its table row's X and Y at that axis in its view; and the sizes its view prints, measured from the part's
    own points in the wall it goes through: the width, the radius, the end's centre to the edge, the mouth at the
    edge (the nearest corners either side) and the taper's length (from the last corners at the width)."""
    fails = []
    views = {v["origin"]: v for v in data["views"] if v["origin"]}
    allp = [q for f in faces for q in f["pts"]]
    for f in data["features"]:
        if f["kind"] != "open_slot":
            continue
        if not allp:
            fails.append("%s: the STEP has no faces for this part" % f["tag"])
            continue
        ax, r = f["axis"], f["r"]
        hit = [c for c in faces if c["kind"] == "cylinder" and c.get("concave") and abs(c["r"] - r) < 0.005 and
               abs(abs(dot(c["d"], ax)) - 1) < 1e-4 and _line_dist(f["entry"], c["o"], c["d"]) < tol]
        if not hit:
            fails.append("%s: the STEP has no half-round end R%.2f on the slot's axis" % (f["tag"], r))
            continue
        cy = hit[0]
        d = cy["d"]
        ts = [dot(sub(q, cy["o"]), d) for q in cy["pts"]]
        t0, t1 = min(ts), max(ts)
        cc = tuple(cy["o"][i] + d[i] * (t0 + t1) / 2 for i in range(3))
        along = f["along"]
        lat = (ax[1] * along[2] - ax[2] * along[1], ax[2] * along[0] - ax[0] * along[2], ax[0] * along[1] - ax[1] * along[0])
        near = []
        for q in allp:
            t = dot(sub(q, cy["o"]), d)
            if t0 - 1e-3 <= t <= t1 + 1e-3:
                qq = sub(q, cc)
                a_, l_ = dot(qq, along), dot(qq, lat)
                if abs(l_) < 6 * r:
                    near.append((a_, l_))
        edge = max(a_ for a_, _l in near)
        at_edge = [l_ for a_, l_ in near if abs(a_ - edge) < 1e-3 and abs(l_) > r - 1e-3]
        lpos, lneg = [l_ for l_ in at_edge if l_ > 0], [-l_ for l_ in at_edge if l_ < 0]
        mouth = (min(lpos) + min(lneg)) if lpos and lneg else None
        sides = [a_ for a_, l_ in near if abs(abs(l_) - r) < 1e-3 and -1e-3 < a_ < edge - 1e-3]
        taper = (edge - max(sides)) if sides and mouth and mouth > 2 * r + 1e-3 else 0.0
        got = {"width": 2 * cy["r"], "r": cy["r"], "edge": edge, "mouth": mouth, "taper": taper}
        dims = f.get("dims") or {}
        if not dims:
            fails.append("%s: the open slot is not sized in any view" % f["tag"])
        for key, txt in dims.items():
            v = _num(txt.lstrip("R"))
            if v is None or got.get(key) is None or abs(v - got[key]) > tol:
                fails.append("%s: its view prints %s %s, the STEP %s" % (f["tag"], key, txt, got.get(key)))
            elif f.get("dims_box") and not _text_near(texts, txt, f["dims_box"]):
                fails.append("%s: its %s %s is not printed by its view" % (f["tag"], key, txt))
        if dims and "taper" not in dims and taper > tol:
            fails.append("%s: the STEP's slot tapers over %.2f, the sheet gives no taper" % (f["tag"], taper))
        row = rows.get(f["tag"])
        v = views.get(f["table_origin"])
        if row and v:
            Ov = v.get("origin3d") or data["origin"]
            ex, ey = dot(sub(cc, Ov), v["x"]), dot(sub(cc, Ov), v["y"])
            if math.hypot(ex - row[0], ey - row[1]) > tol:
                fails.append("%s: table X %s Y %s, the STEP's slot end at X %.2f Y %.2f" % (f["tag"], row[0], row[1], ex, ey))
    return fails


def _fmt(v):
    t = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def _norm(v):
    L = math.sqrt(dot(v, v)) or 1.0
    return tuple(c / L for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _table_cells(page, sheet_h, x0, top, widths):
    """The data rows of a ruled table drawn from (x0, top) with these column widths: each full-width band (a row's
    rectangle, or the space between full-width rules) below its header row, each cell's words in reading order."""
    x1 = x0 + sum(widths)
    bands, ys = set(), set()
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "re":
                R = it[1]
                if abs(R.x0 / MM - x0) < 0.6 and abs(R.x1 / MM - x1) < 0.6:
                    bands.add((round(sheet_h - R.y0 / MM, 2), round(sheet_h - R.y1 / MM, 2)))
            elif it[0] == "l":
                p, q = it[1], it[2]
                if abs(p.y - q.y) < 0.05 and abs(min(p.x, q.x) / MM - x0) < 0.6 and abs(max(p.x, q.x) / MM - x1) < 0.6:
                    ys.add(round(sheet_h - p.y / MM, 2))
    ys = sorted(ys, reverse=True)
    bands |= set(zip(ys, ys[1:]))
    bands = sorted((b for b in bands if b[0] <= top + 0.1 and b[0] - b[1] > 1.0), key=lambda b: -b[0])
    words = [(w[0] / MM, sheet_h - w[3] / MM, w[2] / MM, sheet_h - w[1] / MM, w[4]) for w in page.get_text("words")]
    cuts = [x0]
    for wd in widths:
        cuts.append(cuts[-1] + wd)
    rows, header = [], False
    for hi, lo in bands:
        band = [w for w in words if lo < (w[1] + w[3]) / 2 < hi and x0 < (w[0] + w[2]) / 2 < x1]
        if not band:
            continue
        cells = []
        for c0, c1 in zip(cuts, cuts[1:]):
            ws = sorted((w for w in band if c0 < (w[0] + w[2]) / 2 < c1), key=lambda w: (-round(w[3], 1), w[0]))
            cells.append(" ".join(w[4] for w in ws))
        if not header:
            header = cells[0].upper() == "ITEM"
            continue
        rows.append(cells)
    return rows


def cut_list_fails(doc, data):
    """A frame's cut list (D-162: the members' drawing), read from the sheet against its team file: every row's
    member number and name, profile, cut length, quantity and ends, word for word and in order, and no row more or
    fewer than the file gives."""
    cl = data.get("cut_list")
    if not cl:
        return []
    src = next((s_ for s_ in data["sources"] if s_["role"] == "cut list"), None)
    if not src:
        return ["the sheet has a cut list but names no cut list file"]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import inputs as _inputs
    cfg = {"file": os.path.join(REPO, src["path"]), "welded_in": cl.get("welded_in", []),
           "tolerance": cl.get("tolerance", "")}
    try:
        rows, _p = _inputs.cut_list_rows(cl.get("team", ""), cfg, data["pn"])
    except ValueError as e:
        return ["cut list: %s" % e]
    want = [[str(i + 1), r["name"], r["size_mm"], r["cut_length_mm"], r["qty"],
             _inputs.ends_cell(r["note"], r["tolerance"])] for i, r in enumerate(rows)]
    got = _table_cells(doc[cl["page"]], data["sheet_h"], cl["x"], cl["top"], cl["widths"])
    fails = []
    if len(got) != len(want):
        fails.append("the cut list prints %d rows, %s gives %d" % (len(got), os.path.basename(src["path"]), len(want)))
    heads = ["ITEM", "MEMBER", "PROFILE", "CUT LENGTH", "QTY", "ENDS"]
    for i, (g, w) in enumerate(zip(got, want), 1):
        for h, gc, wc in zip(heads, g, w):
            if " ".join(gc.split()) != " ".join(wc.split()):
                fails.append("cut list row %d %s: '%s' where %s gives '%s'" % (i, h, gc[:60], os.path.basename(src["path"]),
                                                                              wc[:60]))
    return fails


def end_cut_fails(data, faces, texts, near=30.0):
    """Every end cut of every member, found by the repo's reader: on each solid that is a member (longest along the
    line square to its two longest flat faces that aren't parallel), a flat face 1.1° to 88.9° from square to that
    line and 6 mm or more across the member the way it slopes (a mitre, a compound cut's main face; not a 1 x 45°
    bevel). Its angle from square
    must print within `near` mm of where a drawn view puts the face (FRONT's #320: 8 tubes printed none, their
    mitres seen only face on). A part the assembly STEP holds several times passes when one copy (the drawn one)
    does."""
    by = {}
    for f in faces:
        if f["kind"] == "plane" and f.get("n") and len(f["pts"]) >= 3:
            by.setdefault(f["solid"], []).append(f)
    views = [v for v in data["views"] if v.get("off") and v.get("scale")]
    per_solid = []
    for sid, fs in by.items():
        def span(f):
            return max(math.dist(a, b) for a in f["pts"] for b in f["pts"])
        fs_s = sorted(fs, key=lambda f: -span(f))
        n1 = _norm(fs_s[0]["n"])
        n2 = next((_norm(f["n"]) for f in fs_s[1:] if abs(dot(_norm(f["n"]), n1)) < 0.5), None)
        if n2 is None:
            continue
        ax = _norm(_cross(n1, n2))
        allp = [q for f in fs for q in f["pts"]]
        ext = lambda d: max(dot(q, d) for q in allp) - min(dot(q, d) for q in allp)
        if ext(ax) < 1.5 * max(ext(n1), ext(n2)):
            continue                # not a member: a plate, a block
        fails = []
        for f in fs:
            n = _norm(f["n"])
            c = abs(dot(n, ax))
            if not (0.019 < c < 0.9998):
                continue
            u = _norm(_cross(ax, n))        # along the cut's hinge line, across the member
            w = _norm(_cross(u, ax))        # across the member the way the cut slopes
            across = max(dot(q, w) for q in f["pts"]) - min(dot(q, w) for q in f["pts"])
            if across < 6.0:
                continue            # a 1 x 45° bevel or a small facet: narrow the way it slopes (bevels are checked
                                    # as chamfers)
            want = _fmt(math.degrees(math.acos(c))) + "°"
            cen = tuple(sum(q[i] for q in f["pts"]) / len(f["pts"]) for i in range(3))
            ok = False
            for v in views:
                P = lambda q: (v["off"][0] + v["scale"] * dot(q, v["x"]), v["off"][1] + v["scale"] * dot(q, v["y"]))
                pt = P(cen)
                pp = [P(q) for q in f["pts"]]
                reach = near + 1.5 * max(math.dist(a, b) for a in pp for b in pp)     # the label sits by the cut's arc
                if any(t[4] == want and math.hypot((t[0] + t[2]) / 2 - pt[0], (t[1] + t[3]) / 2 - pt[1]) <= reach
                       for t in texts):
                    ok = True
                    break
            if not ok:
                fails.append("an end cut %s from square (at %.1f, %.1f, %.1f) is printed nowhere near its end" % (
                    want, cen[0], cen[1], cen[2]))
        per_solid.append(fails)
    if data.get("occurrences", 1) > 1 and per_solid:
        return [] if any(not f for f in per_solid) else per_solid[0]
    return [x for f in per_solid for x in f]


def flat_fails(data, texts, page_text, tol=TOL):
    """A bent part's flat pattern, against its DXF read again here (no OCC) and the model's flanges as the sheet
    records them: every bend row on one of the DXF's BEND lines, as many rows as lines; each chain's bend lines where
    its outside flange lengths, fold angles, the inside radius and the printed K-factor put them, and its flat as long
    as the DXF's (so a DXF that doesn't fit the model, or a wrong K-factor, fails: the Lead's ruling); the flat's
    overall size, the K-factor and every bend's tag printed."""
    fl = data.get("flat")
    if not fl:
        return []
    import dxf as dxfmod
    d = dxfmod.Dxf(os.path.join(REPO, fl["dxf"]))
    box = d.cut_box()
    bends = d.bend_lines()
    fails = []
    if len(bends) != len(fl["rows"]):
        fails.append("the bend table has %d rows, the DXF %d bend lines" % (len(fl["rows"]), len(bends)))
    for row in fl["rows"]:
        ax = 0 if row["axis"] == "x" else 1
        at = box[ax] + row["at"]
        if not any(abs(a[ax] - b[ax]) < 1e-6 and abs(a[ax] - at) < 0.01 for a, b in bends):
            fails.append("bend %s (%s %s) is on no BEND line of the DXF" % (row["tag"], row["axis"], _fmtv(row["at"])))
    k = fl["k"]
    vg = fl.get("vgroove")
    for ci, ch in enumerate(fl["chains"]):
        t, fls, angs = ch["t"], ch["flanges"], ch["angles"]
        radii = [r if r is not None else fl["r"] for r in ch["radii"]]
        if vg:          # a V-groove: the flat develops along the outer face, each fold's outside arc R (0: sharp)
            ro = [r_ or 0.0 for r_ in ch.get("radii_out") or [None] * len(angs)]
            ossb = [ro[i] * math.tan(math.radians(angs[i]) / 2) for i in range(len(angs))]
            ba = [math.radians(angs[i]) * ro[i] for i in range(len(angs))]
        else:
            ossb = [(radii[i] + t) * math.tan(math.radians(angs[i]) / 2) for i in range(len(angs))]
            ba = [math.radians(angs[i]) * (radii[i] + k * t) for i in range(len(angs))]
        x, pos = 0.0, []
        for i, L in enumerate(fls):
            x += L - (ossb[i - 1] if i > 0 else 0.0) - (ossb[i] if i < len(angs) else 0.0)
            if i < len(angs):
                pos.append(x + ba[i] / 2)
                x += ba[i]
        ax = ch["dxf_axis"]
        lines = [a[ax] for a, b in bends if abs(a[ax] - b[ax]) < 1e-6]
        for p_ in pos:
            want = (box[2 + ax] - p_) if ch["reversed"] else (box[ax] + p_)
            if not any(abs(l_ - want) <= tol for l_ in lines):
                fails.append("chain %d: the model's flanges%s put a bend line at %s %s; the DXF has none there" % (
                    ci + 1, " (a V-groove)" if vg else " at K %s and R%s" % (_fmtv(k), _fmtv(fl["r"])), "xy"[ax],
                    _fmtv(want - box[ax])))
        if abs(x - (box[2 + ax] - box[ax])) > tol:
            fails.append("chain %d: the model's flat is %s long, the DXF's %s" % (ci + 1, _fmtv(x), _fmtv(box[2 + ax] - box[ax])))
    v = fl.get("view")
    if v:
        for want in (_fmtv(box[2] - box[0]), _fmtv(box[3] - box[1])):
            if not _text_near(texts, want, v["box"], pad=20.0):
                fails.append("the flat's size %s is not printed by it" % want)
    for row in fl["rows"]:
        if row.get("printed_at") and not _text_near(texts, row["tag"], row["printed_at"], pad=2.5):
            fails.append("bend %s's tag is not printed on its line" % row["tag"])
    if not vg and ("K-factor %s" % _fmt3(k)) not in " ".join(page_text.split()):
        fails.append("the K-factor %s is not printed" % _fmt3(k))
    return fails


def csk_fails(data, faces, holes, page, tol=TOL):
    """Countersinks (D-143) against the STEP (the repo's reader): each cone of the STEP with two circles on a hole's
    axis, the smaller the hole's, is a countersink: its outer diameter and included angle (from the circles' radii and
    the distance between them) must be printed in that hole's row ('CSK Ød x a°'), and every printed countersink must
    be one of the STEP's."""
    fails = []
    found = []
    for f in faces:
        cs = f.get("circles") or []
        if f["kind"] != "conical_surface" or len(cs) < 2:
            continue
        rs = sorted({round(r, 4) for _c, r in cs})
        if len(rs) != 2:
            continue
        small = next(c for c, r in cs if abs(r - rs[0]) < 1e-3)
        big = next(c for c, r in cs if abs(r - rs[1]) < 1e-3)
        h = next((h for h in holes if abs(h["dia"] / 2 - rs[0]) < 0.005 and
                  math.dist(sub(small, h["c"]), tuple(dot(sub(small, h["c"]), h["axis"]) * a for a in h["axis"])) < 0.02),
                 None)
        if h is None:
            continue
        depth = math.dist(small, big)
        ang = 2 * math.degrees(math.atan2(rs[1] - rs[0], depth)) if depth > 1e-9 else 180.0
        found.append({"hole": h, "dia": 2 * rs[1], "angle": ang, "centre": big})
    rows = {f_["tag"]: f_ for f_ in data["features"] if f_["kind"] == "hole"}
    printed = {}
    for tag in rows:
        txt = row_size_text(page, tag) or ""
        m = re.search(r"CSK\s+Ø([\d.]+)\s*x\s*([\d.]+)°", txt)
        if m:
            printed[tag] = (float(m.group(1)), float(m.group(2)))
    used = set()
    for c in found:
        # the row of this hole: the one whose table position is the STEP hole's (the hole table check ties them)
        tag = next((t for t, f_ in rows.items() if abs(f_["dia"] - c["hole"]["dia"]) < 0.011 and
                    math.dist(f_["entry"], c["centre"]) < tol), None)
        if tag is None or tag not in printed:
            fails.append("a countersink Ø%s x %s° of the STEP (its hole Ø%s) is called out nowhere" % (
                _fmtv(c["dia"]), _fmtv(c["angle"]), _fmtv(c["hole"]["dia"])))
            continue
        used.add(tag)
        d_, a_ = printed[tag]
        if abs(d_ - c["dia"]) > 0.011 or abs(a_ - c["angle"]) > 0.051:
            fails.append("%s: its row says CSK Ø%s x %s°; the STEP's is Ø%s x %s°" % (
                tag, _fmtv(d_), _fmtv(a_), _fmtv(c["dia"]), _fmtv(c["angle"])))
    for tag in printed:
        if tag not in used:
            fails.append("%s: its row calls out a countersink the STEP hasn't" % tag)
    return fails


def vgroove_radius_fails(data, faces):
    """A V-grooved panel's folds against the STEP's own faces (the repo's reader): each fold's outside radius, as the
    sheet records it, must be a convex cylinder of the STEP along that run's bend lines (Reviewer 6 on #341: the
    read-back took it from the sheet's own record)."""
    fl = data.get("flat")
    if not fl or not fl.get("vgroove") or not fl.get("map"):
        return []
    fails = []
    for ci, (ch, mc) in enumerate(zip(fl["chains"], fl["map"]["chains"])):
        ax = mc["axis"]
        for j, r in enumerate(ch.get("radii_out") or []):
            if not r:
                fails.append("chain %d's fold %d is recorded sharp" % (ci + 1, j + 1))
                continue
            if not any(f["kind"] == "cylinder" and "d" in f and not f.get("concave") and abs(f["r"] - r) < 0.01
                       and abs(abs(dot(f["d"], ax)) - 1) < 1e-6 for f in faces):
                fails.append("chain %d's fold %d: the STEP has no outside arc R%s along its bend line" % (
                    ci + 1, j + 1, _fmtv(r)))
    return fails


def _flat_where(mp, P):
    """A point of the sheet's place in the DXF by the sheet's record of how its flanges unfold (its own reading, not
    the generator's code): across a chain's bends from the flange it lies on, along them from the other chain's base
    flange or the part's extent along the bend lines; None off the flanges' straight parts or at a corner."""
    box, ch = mp["box"], mp["chains"]

    def on(c, f):
        q = dot(P, f["D"]) - f["m0"]
        return abs(dot(P, f["N"]) - f["o0"]) <= c["t"] + 0.01 and f["lo"] - 0.01 <= q <= f["hi"] + 0.01

    def val(c, f):
        across = f["base"] + dot(P, f["D"]) - f["m0"]
        return (box[2 + c["ax"]] - across) if c["rev"] else (box[c["ax"]] + across)
    hits = {(ci, j) for ci, c in enumerate(ch) for j, f in enumerate(c["flanges"]) if on(c, f)}
    xy = [None, None]
    al = mp.get("along")
    if al:
        if len(hits) != 1:
            return None
        (_ci, j), = hits
        xy[ch[0]["ax"]] = val(ch[0], ch[0]["flanges"][j])
        w = dot(P, al["a"]) - al["w0"]
        xy[al["ax"]] = (box[al["ax"]] + w) if al["sense"] > 0 else (box[2 + al["ax"]] - w)
        return tuple(xy)
    jA, jB = mp["base"]
    if hits == {(0, jA), (1, jB)}:
        ja, jb = jA, jB
    elif len(hits) == 1 and not hits & {(0, jA), (1, jB)}:
        (ci, j), = hits
        ja, jb = (j, jB) if ci == 0 else (jA, j)
    else:
        return None
    xy[ch[0]["ax"]] = val(ch[0], ch[0]["flanges"][ja])
    xy[ch[1]["ax"]] = val(ch[1], ch[1]["flanges"][jb])
    return tuple(xy)


def flat_hole_fails(data, holes, faces, tol=TOL):
    """A bent part's round holes in its flat pattern, counted both ways (Reviewer 6 on #335): every hole of the STEP
    (the repo's reader) placed in the flat by the sheet's record of how its flanges unfold, on a DXF circle of its
    size within tol, and every DXF circle on one of them. Each recorded flange must be a face of the STEP (a plane
    of its normal, within the sheet's thickness of the flange's line, along at least half its straight part), so the
    record can't place the holes on a sheet the model doesn't have."""
    fl = data.get("flat")
    if not fl:
        return []
    mp = fl.get("map")
    if not mp:
        return ["the sheet doesn't record how its flanges unfold, so the flat's holes can't be checked"]
    import dxf as dxfmod
    d = dxfmod.Dxf(os.path.join(REPO, fl["dxf"]))
    fails = []
    planes = [f for f in faces if f["kind"] == "plane" and "n" in f and f["pts"]]
    for ci, c in enumerate(mp["chains"]):
        for j, f in enumerate(c["flanges"]):
            def fits(pf):
                if abs(abs(dot(pf["n"], f["N"])) - 1) > 1e-6:
                    return False
                if any(abs(dot(p, f["N"]) - f["o0"]) > c["t"] + 0.01 for p in pf["pts"]):
                    return False
                qs = [dot(p, f["D"]) - f["m0"] for p in pf["pts"]]
                return min(max(qs), f["hi"]) - max(min(qs), f["lo"]) >= 0.5 * (f["hi"] - f["lo"])
            if not any(fits(pf) for pf in planes):
                fails.append("chain %d's flange %d, as the sheet records it, is no face of the STEP" % (ci + 1, j + 1))
    if fails:
        return fails
    groups = {}
    for h in holes:
        groups.setdefault(h.get("occ"), []).append(h)
    hs = holes
    if len(groups) > 1:
        # a part used more than once in its assembly STEP: the occurrence whose holes all sit on the recorded flanges
        fit = [g for g in groups.values() if all(_flat_where(mp, h["c"]) is not None for h in g)]
        hs = fit[0] if fit else list(groups.values())[0]
    circles = [(c, r) for lay, c, r in d.circles if d.role(lay) == "cut"]
    if len(circles) != len(hs):
        fails.append("the flat's DXF has %d round holes, the STEP %d" % (len(circles), len(hs)))
    used = set()
    for h in hs:
        xy = _flat_where(mp, h["c"])
        if xy is None:
            fails.append("STEP hole Ø%s at (%s, %s, %s) is on no flange's straight part" % (
                (_fmtv(h["dia"]),) + tuple(_fmtv(x) for x in h["c"])))
            continue
        cand = sorted((math.hypot(cc[0] - xy[0], cc[1] - xy[1]), i) for i, (cc, rr) in enumerate(circles)
                      if i not in used and abs(2 * rr - h["dia"]) < 0.011)
        if cand and cand[0][0] <= tol:
            used.add(cand[0][1])
        else:
            fails.append("STEP hole Ø%s unfolds to (%s, %s) in the flat; the DXF has no hole of its size there" % (
                _fmtv(h["dia"]), _fmtv(xy[0]), _fmtv(xy[1])))
    for i, (cc, rr) in enumerate(circles):
        if i not in used:
            fails.append("the flat's DXF has a Ø%s hole at (%s, %s) that is on no STEP hole" % (
                _fmtv(2 * rr), _fmtv(cc[0]), _fmtv(cc[1])))
    return fails


def _cutout_loops(mp, faces):
    """The cut-outs of a bent part that aren't round holes, from the STEP's own faces (the repo's reader): in each
    flange the sheet records, the faces through the sheet (planes square to it, cylinders along its normal) that join
    into closed shapes whose outward normals point into the shape (a void in the flange), round holes aside. Each:
    its edge on one skin as points (3D), its centre (3D) and its points."""
    out = []
    for c in mp["chains"]:
        for f in c["flanges"]:
            N, D, t = f["N"], f["D"], c["t"]

            def inside(p):
                q = dot(p, D) - f["m0"]
                return abs(dot(p, N) - f["o0"]) <= t + 0.01 and f["lo"] - 0.01 <= q <= f["hi"] + 0.01
            side = []
            for fc in faces:
                if not fc["pts"] or not all(inside(p) for p in fc["pts"]):
                    continue
                if fc["kind"] == "plane" and "n" in fc and abs(dot(fc["n"], N)) < 1e-6:
                    side.append(fc)
                elif fc["kind"] == "cylinder" and "d" in fc and abs(abs(dot(fc["d"], N)) - 1) < 1e-6:
                    side.append(fc)
            # join faces that share a point into shapes
            key = lambda p: tuple(round(v, 3) for v in p)
            parent = list(range(len(side)))

            def root(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i
            owner = {}
            for i, fc in enumerate(side):
                for p in fc["pts"]:
                    k = key(p)
                    if k in owner:
                        parent[root(i)] = root(owner[k])
                    else:
                        owner[k] = i
            comps = {}
            for i in range(len(side)):
                comps.setdefault(root(i), []).append(side[i])
            for fcs in comps.values():
                if all(fc["kind"] == "cylinder" for fc in fcs):
                    continue                # a round hole: the holes' check
                pts = [p for fc in fcs for p in fc["pts"]]
                ctr = tuple(sum(p[k] for p in pts) / len(pts) for k in range(3))
                planes = [fc for fc in fcs if fc["kind"] == "plane"]
                if not all(dot(sub(ctr, tuple(sum(p[k] for p in fc["pts"]) / len(fc["pts"]) for k in range(3))),
                               fc["n"]) > 0 for fc in planes):
                    continue                # an edge of the flange's outline, not a void in it
                # the edge on one skin: each face's points on the skin nearest N's low side, as segments and arcs
                lo_ = min(dot(p, N) for p in pts)
                skin = lambda fc: [p for p in fc["pts"] if abs(dot(p, N) - lo_) < 0.01]
                edge = []
                for fc in fcs:
                    ps = skin(fc)
                    uniq = []
                    for p in ps:
                        if not any(math.dist(p, u) < 1e-4 for u in uniq):
                            uniq.append(p)
                    if fc["kind"] == "plane" and len(uniq) == 2:
                        a, b = uniq
                        n_ = max(1, int(math.ceil(math.dist(a, b) / 1.0)))
                        edge.append([tuple(a[k] + (b[k] - a[k]) * i / n_ for k in range(3)) for i in range(n_ + 1)])
                    elif fc["kind"] == "cylinder" and len(uniq) == 2:
                        o = fc["o"]
                        o = tuple(o[k] + N[k] * (lo_ - dot(o, N)) for k in range(3))      # its axis on that skin
                        u = sub(uniq[0], o)
                        r = math.sqrt(dot(u, u))
                        u = tuple(x / r for x in u)
                        v = (N[1] * u[2] - N[2] * u[1], N[2] * u[0] - N[0] * u[2], N[0] * u[1] - N[1] * u[0])
                        w = sub(uniq[1], o)
                        ang = math.atan2(dot(w, v), dot(w, u))
                        # the arc that bulges away from the shape's middle (the void's edge)
                        arcs = [ang, ang - 2 * math.pi] if ang > 0 else [ang, ang + 2 * math.pi]
                        mids = [tuple(o[k] + r * (math.cos(a_ / 2) * u[k] + math.sin(a_ / 2) * v[k]) for k in range(3))
                                for a_ in arcs]
                        a_ = max(zip(arcs, mids), key=lambda am: math.dist(am[1], ctr))[0]
                        n_ = max(4, int(math.ceil(abs(a_) * r / 0.5)))
                        edge.append([tuple(o[k] + r * (math.cos(a_ * i / n_) * u[k] + math.sin(a_ * i / n_) * v[k])
                                           for k in range(3)) for i in range(n_ + 1)])
                    else:
                        edge.append(None)
                # a void closes on itself: on the skin every end of its edge meets exactly one other (a notch in the
                # outline, such as a corner relief, is open where it leaves the flange's edge)
                ends = {}
                for e in edge:
                    if e is None:
                        continue
                    for p in (e[0], e[-1]):
                        k = tuple(round(v, 2) for v in p)
                        ends[k] = ends.get(k, 0) + 1
                if not ends or any(n_ != 2 for n_ in ends.values()):
                    continue
                # its centre and extent from the whole edge (round ends and corners included)
                ep = [p for e in edge if e for p in e]
                ctr = tuple((min(p[k] for p in ep) + max(p[k] for p in ep)) / 2 for k in range(3))
                if any(math.dist(ctr, o_["centre"]) < 0.01 for o_ in out):
                    continue                # the flange both runs share: met from each
                out.append({"centre": ctr, "pts": ep, "edge": edge})
    return out


def flat_cutout_fails(data, faces, tol=TOL):
    """A bent part's cut-outs that aren't round holes (#335's follow-up, the Lead: 511202 and other trays), counted
    both ways: each cut-out the STEP has (found from its own faces, _cutout_loops) unfolds, by the sheet's record of
    its flanges, onto one of the DXF's cut shapes inside the outline, point for point within tol both ways; each of
    the DXF's on one of the STEP's; and each one's table row gives its centre and its size as the STEP has them."""
    fl = data.get("flat")
    if not fl or not fl.get("map"):
        return []
    import dxf as dxfmod
    d = dxfmod.Dxf(os.path.join(REPO, fl["dxf"]))
    mp = fl["map"]
    loops = d.cut_components()[1:]
    cuts = _cutout_loops(mp, faces)
    fails = []
    if len(cuts) != len(loops):
        fails.append("the flat's DXF cuts %d shapes inside its outline besides round holes, the STEP has %d cut-outs" % (
            len(loops), len(cuts)))
    used = set()
    for c in cuts:
        if any(e is None for e in c["edge"]):
            fails.append("a cut-out of the STEP round (%s) has an edge this check can't follow" % ", ".join(
                _fmtv(x) for x in c["centre"]))
            continue
        flat = [[_flat_where(mp, p) for p in e] for e in c["edge"]]
        if any(q is None for e in flat for q in e):
            fails.append("the STEP's cut-out round (%s) isn't on one flange's straight part" % ", ".join(
                _fmtv(x) for x in c["centre"]))
            continue
        segs = [("L", e[i], e[i + 1]) for e in flat for i in range(len(e) - 1)]
        mine = dxfmod._Grid(segs, tol)
        hit = None
        for i, lp in enumerate(loops):
            if i in used:
                continue
            g = dxfmod._Grid(lp["prims"], tol)
            if all(g.dist(q) <= tol for e in flat for q in e) and \
                    all(mine.dist(q) <= tol for pr in lp["prims"] for q in dxfmod._samples(pr, 1.0)):
                hit = i
                break
        if hit is None:
            q = _flat_where(mp, c["centre"])
            fails.append("the STEP's cut-out unfolds round (%s) in the flat; the DXF has no cut-out of its shape there" % (
                ", ".join(_fmtv(x) for x in q) if q else "?"))
        else:
            used.add(hit)
    for i, lp in enumerate(loops):
        if i not in used:
            b = lp["box"]
            fails.append("the flat's DXF has a %s x %s cut-out at (%s, %s) that is on no cut-out of the STEP" % (
                _fmtv(b[2] - b[0]), _fmtv(b[3] - b[1]), _fmtv((b[0] + b[2]) / 2), _fmtv((b[1] + b[3]) / 2)))
    return fails, cuts


def row_size_text(page, tag):
    """A table row's SIZE cell in full, its wrapped lines too: the words after the row's X and Y, before its DEPTH
    (THRU..., or a depth), on the row's line and the lines under it until the next row."""
    words = sorted(page.get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    for i, w in enumerate(words):
        if w[4] != tag:
            continue
        y = (w[1] + w[3]) / 2
        line = sorted([v for v in words if abs((v[1] + v[3]) / 2 - y) <= 0.6 and v[0] > w[0]], key=lambda v: v[0])
        if len(line) < 3:
            continue
        try:
            float(line[0][4]), float(line[1][4])
        except ValueError:
            continue
        x0 = line[1][2]
        depth = next((v for v in line[2:] if v[4].startswith("THRU") or v[4].endswith("deep")), None)
        x1 = depth[0] if depth else 1e9
        cell = [v for v in line[2:] if v[0] >= x0 and v[2] <= x1]
        nxt = min([(v[1] + v[3]) / 2 for v in words if (v[1] + v[3]) / 2 > y + 0.6 and re.fullmatch(r"H\d{2}", v[4])
                   and abs(v[0] - w[0]) < 2.0] or [y + 30.0])
        below = sorted([v for v in words if y + 0.6 < (v[1] + v[3]) / 2 < nxt - 0.6 and v[0] >= x0 and v[2] <= x1],
                       key=lambda v: ((v[1] + v[3]) / 2, v[0]))
        under, last = [], y
        for v in below:            # the cell's wrapped lines: each one line under the last (a gap ends the cell)
            vy = (v[1] + v[3]) / 2
            if vy - last > 14.0 and not (under and abs(vy - (under[-1][1] + under[-1][3]) / 2) <= 0.6):
                break
            if not under or abs(vy - (under[-1][1] + under[-1][3]) / 2) > 0.6:
                last = vy
            under.append(v)
        return " ".join(v[4] for v in cell + under)
    return None


def cutout_row_fails(data, rows, cuts, page, tol=TOL):
    """Each cut-out's table row against the STEP's cut-outs (_cutout_loops): its X and Y the centre of one, from its
    view's origin, and its size and direction that one's extent along the view's X and Y."""
    fails = []
    views = {v["origin"]: v for v in data["views"] if v["origin"]}
    O = data["origin"]
    for f in data["features"]:
        if f["kind"] != "cutout":
            continue
        if f["tag"] not in rows:
            fails.append("%s: no row in the tables" % f["tag"])
            continue
        x, y, _w = rows[f["tag"]]
        size = row_size_text(page, f["tag"])
        m = re.search(r"(?:CUT-OUT|SLOT)\s+([\d.]+)\s*x\s*([\d.]+).*?along\s+([XY])", size or "")
        if not m:
            fails.append("%s: its size '%s' doesn't read as 'L x W along X or Y'" % (f["tag"], size))
            continue
        a_, b_, ax = float(m.group(1)), float(m.group(2)), m.group(3)
        L, W = (b_, a_) if size.strip().startswith("SLOT") else (a_, b_)      # a slot reads width x length
        v = views[f["table_origin"]]
        Ov = v.get("origin3d") or O
        best = None
        for c in cuts:
            cx, cy = dot(sub(c["centre"], Ov), v["x"]), dot(sub(c["centre"], Ov), v["y"])
            ex = max(dot(p, v["x"]) for p in c["pts"]) - min(dot(p, v["x"]) for p in c["pts"])
            ey = max(dot(p, v["y"]) for p in c["pts"]) - min(dot(p, v["y"]) for p in c["pts"])
            dd = math.hypot(cx - float(x), cy - float(y))
            if best is None or dd < best[0]:
                best = (dd, ex, ey)
        if best is None or best[0] > tol:
            fails.append("%s: table X %s Y %s is the centre of no cut-out of the STEP within %s mm" % (f["tag"], x, y, tol))
            continue
        want = (L, W) if ax == "X" else (W, L)
        if abs(best[1] - want[0]) > tol or abs(best[2] - want[1]) > tol:
            fails.append("%s: the STEP's cut-out there is %s along X and %s along Y; its row says %s" % (
                f["tag"], _fmtv(best[1]), _fmtv(best[2]), size))
    return fails




def _fmtv(v):
    t = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def _fmt3(v):
    t = ("%.3f" % v).rstrip("0").rstrip(".")
    return t or "0"


def _line_dist(p, a, d):
    v = sub(p, a)
    L = math.sqrt(dot(d, d)) or 1.0
    t = dot(v, d) / L
    return math.sqrt(max(dot(v, v) - t * t, 0.0))


def flat_feature_fails(data, planes, texts, tol=TOL):
    """Notches and chamfers against the STEP's own flat faces (the repo's reader, no OCC): each notch's back face and
    two sides are where the drawing says, and its width, length and place across, measured from those faces and the
    part's own end and side faces, are what the sheet prints beside it (a notch said to be the same as the drawn one
    measures the same); each chamfer's faces have the legs its callout gives, equal, at 45°."""
    fails = []
    views_all = data.get("views", [])
    allp = [q for f in planes for q in f["pts"]]
    if not allp:
        return ["the STEP has no flat faces for this part"]
    for k, nt in enumerate(data.get("notches", [])):
        lax, ac = nt["lax"], nt["across"]
        sv = [dot(q, lax) for q in allp]
        end = max(sv) if nt["sgn"] > 0 else min(sv)
        a_all = [dot(q, ac) for q in allp]
        plo, phi = min(a_all), max(a_all)
        sb, lo, hi = nt["s_back"], nt["lo"], nt["hi"]
        s0, s1 = min(end, sb), max(end, sb)
        back = [f for f in planes if abs(abs(dot(f["n"], lax)) - 1) < 1e-4 and
                all(abs(dot(q, lax) - sb) < 0.01 and lo - 0.01 <= dot(q, ac) <= hi + 0.01 for q in f["pts"])]
        sides = [[f for f in planes if abs(abs(dot(f["n"], ac)) - 1) < 1e-4 and
                  all(abs(dot(q, ac) - a_) < 0.01 for q in f["pts"]) and
                  abs(min(dot(q, lax) for q in f["pts"]) - s0) < 0.01 and
                  abs(max(dot(q, lax) for q in f["pts"]) - s1) < 0.01] for a_ in (lo, hi)]
        where = "notch at the %s end" % ("+" if nt["sgn"] > 0 else "-")
        if not back or not sides[0] or not sides[1]:
            fails.append("%s: the STEP has no notch faces where the drawing says" % where)
            continue
        got = {"width": hi - lo, "length": abs(end - sb)}
        tx = nt["texts"]
        if not tx:
            fails.append("%s: not sized on the sheet" % where)
            continue
        ref = phi if abs(tx["ref"] - phi) < abs(tx["ref"] - plo) else plo
        got["pos"] = min(abs(ref - lo), abs(ref - hi))
        for key in ("width", "length", "pos"):
            v = _num(tx[key])
            if v is None or abs(v - got[key]) > tol:
                fails.append("%s: the sheet's %s %s, the STEP %.3f" % (where, key, tx[key], got[key]))
        if nt["drawn"] and nt["box"]:
            for key in ("width", "length", "pos"):
                if not _text_near(texts, tx[key], nt["box"]):
                    fails.append("%s: its %s %s is not printed by its view" % (where, key, tx[key]))
    for ch in data.get("chamfers", []):
        n, lax, side = ch["n"], ch["lax"], ch["side_n"]
        p0 = ch["pts"][0]
        fs = [f for f in planes if abs(abs(dot(f["n"], n)) - 1) < 1e-4 and
              all(abs(dot(sub(q, p0), n)) < 0.01 for q in f["pts"])]
        where = "chamfer along the member" if ch.get("long") else "chamfer at the %s end" % ("+" if ch["sgn"] > 0 else "-")
        if not fs:
            fails.append("%s: the STEP has no face where the drawing says" % where)
            continue
        qs = [q for f in fs for q in f["pts"]]
        d1, d2 = ch.get("leg_dirs") or (lax, side)      # an end bevel: along the member and the side; a long one: across
        la = max(dot(q, d1) for q in qs) - min(dot(q, d1) for q in qs)
        ls = max(dot(q, d2) for q in qs) - min(dot(q, d2) for q in qs)
        v = _num(ch["text"])
        if v is None or abs(v - la) > tol or abs(v - ls) > tol or not ch["text"].endswith("x 45°"):
            fails.append("%s: the sheet says %s, the STEP's legs %.3f and %.3f" % (where, ch["text"], la, ls))
        # the callout by the chamfer itself, as the STEP places it (Reviewer 6 on #331: a callout moved 40 to 67 mm
        # away, its record moved with it, still passed): within 25 mm (plus 1.5 times the chamfer's narrower side on
        # paper) of the middle of its faces, as some drawn view projects them
        cen = tuple(sum(q[i] for q in qs) / len(qs) for i in range(3))
        near_it = False
        for v in [v for v in views_all if v.get("off") and v.get("scale")]:
            P = lambda q: (v["off"][0] + v["scale"] * dot(q, v["x"]), v["off"][1] + v["scale"] * dot(q, v["y"]))
            pc = P(cen)
            pp = [P(q) for q in qs]
            narrow = min(max(a[0] for a in pp) - min(a[0] for a in pp), max(a[1] for a in pp) - min(a[1] for a in pp))
            reach = 25.0 + 1.5 * narrow
            if any(t[4] == ch["text"] and math.hypot((t[0] + t[2]) / 2 - pc[0], (t[1] + t[3]) / 2 - pc[1]) <= reach
                   for t in texts):
                near_it = True
                break
        if not near_it:
            fails.append("%s: its size %s is not printed by it" % (where, ch["text"]))
        tip = ch["tip"]
        at = ch.get("box") or (tip[0], tip[1], tip[0], tip[1])
        if not _text_near(texts, ch["text"], at, pad=2.5 if ch.get("box") else 25.0):
            fails.append("%s: its size %s is not where the sheet's record puts it" % (where, ch["text"]))
    return fails


def two_wall_pairs(features, tol=0.05):
    """Holes through two walls of one member: two holes of one body on one line, the line between their centres
    running along their axis (parallel holes side by side in one wall are not a pair; BASE's FR1, 2026-11-01)."""
    hs = [f for f in features if f["kind"] == "hole"]
    out = []
    for i, f in enumerate(hs):
        for g in hs[i + 1:]:
            if g["body"] != f["body"] or abs(abs(dot(g["axis"], f["axis"])) - 1) > 1e-6:
                continue
            d = sub(g["entry"], f["entry"])
            along = abs(dot(d, f["axis"]))
            across = math.sqrt(max(0.0, dot(d, d) - along * along))
            if across < tol and along > 0.5:
                out.append((f["tag"], g["tag"]))
    return out


def key_note_fails(text, matched, krows, tol=0.1, holes=None):
    """Each key row (corner-keys.csv) needs its note on the sheet ("Key PN, JOINT, ... meet Hxx and Hyy;"), and the
    two holes it names must be the part's holes at the key's screw positions there (centres from the STEP). A HOLD
    note for the key stands in only while the STEP really has no hole at either screw position (holes: the STEP's
    hole centres, from the independent reader)."""
    flat = re.sub(r"\s+", " ", text)
    out = []
    for r in krows:
        want = [(float(r["fix_hole_1_x"]), float(r["fix_hole_1_y"])), (float(r["fix_hole_2_x"]), float(r["fix_hole_2_y"]))]
        m = re.search(r"Key %s, %s, .*?meet (H\d+) and (H\d+);" % (r["part_number"], re.escape(r["joint"])), flat)
        if not m:
            held = re.search(r"HOLD: Joints' key file puts key %s, %s, in this end" % (
                r["part_number"], re.escape(r["joint"])), flat)
            if held and holes is not None:
                there = [h for h in holes if min(math.dist((h["c"][0], h["c"][1]), w) for w in want) < 0.5]
                if there:
                    out.append("key %s (%s): a HOLD note, but the STEP has a hole at its screw position %s: draw the "
                               "key note" % (r["part_number"], r["joint"], tuple(round(v, 2) for v in there[0]["c"][:2])))
                continue
            out.append("no orientation note for key %s (%s)" % (r["part_number"], r["joint"]))
            continue
        got = []
        for tg in m.groups():
            c = matched.get(tg)
            d = min(math.dist((c[0], c[1]), w) for w in want) if c else None
            if d is None or d > tol:
                out.append("key %s (%s): its note names %s, which is not at one of the key's screw positions %s" % (
                    r["part_number"], r["joint"], tg, want))
            got.append(c)
        if all(got) and math.dist(got[0][:2], got[1][:2]) < tol:
            out.append("key %s (%s): its note names the same hole twice" % (r["part_number"], r["joint"]))
    return out


def check(pdf_path, step_path=None, verbose=False):
    """Run every check on one drawing; returns (failures, stats)."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    data = read_data(doc)
    fails = []
    stats = {"rows": 0, "holes": 0, "circles": 0, "worst_table": 0.0, "worst_drawn": 0.0}
    step_path = step_path or os.path.join(REPO, [s for s in data["sources"] if s["role"] == "STEP"][0]["path"])
    views = {v["origin"]: v for v in data["views"] if v["origin"]}
    O = data["origin"]
    rows = table_rows(page)
    feats = {f["tag"]: f for f in data["features"]}
    holes = step_holes(step_path, data["pn"])
    pm = data.get("placement")
    if pm:
        # the part file is in its own system: place it as the drawing says, and check that placement against the
        # assembly STEP it came from (every hole of the part there, within 0.05)
        m, t = pm["m"], pm["t"]
        mv = lambda p: tuple(sum(m[i][j] * p[j] for j in range(3)) + t[i] for i in range(3))
        holes = [{"c": mv(h["c"]), "axis": tuple(sum(m[i][j] * h["axis"][j] for j in range(3)) for i in range(3)),
                  "dia": h["dia"]} for h in holes]
        asm = step_holes(os.path.join(REPO, pm["assembly"]), data["pn"])
        for h in holes:
            if not any(abs(a["dia"] - h["dia"]) < 0.011 and math.dist(a["c"], h["c"]) < TOL for a in asm):
                fails.append("placed hole Ø%.2f at (%.2f, %.2f, %.2f) is not in %s" % (
                    (h["dia"],) + h["c"] + (pm["assembly"],)))
    stats["holes"] = len(holes)
    # 1. table rows against the STEP
    used = set()
    matched = {}            # tag -> the STEP hole centre its table row matched (the independent reader's)
    for tag, f in feats.items():
        if tag not in rows:
            fails.append("%s: no row in the hole tables" % tag)
            continue
        x, y, size = rows[tag]
        stats["rows"] += 1
        # an open slot's round end reads as a hole of its width at the end's centre (the repo's reader)
        if f["kind"] != "hole":
            continue
        v = views[f["table_origin"]]
        best = None
        for i, h in enumerate(holes):
            if abs(abs(dot(h["axis"], v["n"])) - 1) > 1e-6 or abs(h["dia"] - f["dia"]) > 0.011:
                continue
            Ov = v.get("origin3d") or O        # a view with its own origin (an angled face's)
            ex, ey = dot(sub(h["c"], Ov), v["x"]), dot(sub(h["c"], Ov), v["y"])
            d = math.hypot(ex - x, ey - y)
            if best is None or d < best[0]:
                best = (d, i, ex, ey)
        if best is None or best[0] > TOL:
            fails.append("%s: table X %s Y %s matches no STEP hole of Ø%s within %s mm%s" % (
                tag, x, y, f["dia"], TOL, "" if best is None else " (nearest %.3f away)" % best[0]))
            continue
        stats["worst_table"] = max(stats["worst_table"], best[0])
        matched[tag] = holes[best[1]]["c"]
        # the same axis can carry runs in two walls of different sizes; mark every run on this axis of this size
        used.update(j for j, h in enumerate(holes) if abs(h["dia"] - f["dia"]) < 0.011 and
                    abs(abs(dot(h["axis"], v["n"])) - 1) < 1e-6 and
                    math.hypot(dot(sub(h["c"], Ov), v["x"]) - best[2], dot(sub(h["c"], Ov), v["y"]) - best[3]) < TOL)
    if data.get("occurrences", 1) > 1 and used:
        drawn_occ = {holes[j].get("occ") for j in used}
        skip = {j for j, h in enumerate(holes) if h.get("occ") not in drawn_occ}
    else:
        skip = set()
    for j, h in enumerate(holes):
        if j not in used and j not in skip:
            fails.append("STEP hole Ø%.2f at (%.2f, %.2f, %.2f) is in no hole table" % ((h["dia"],) + h["c"]))
    # 2. drawn circles
    circles = pdf_circles(page, data["sheet_h"])
    stats["circles"] = len(circles)
    for tag, f in feats.items():
        if f["kind"] != "hole" or not f["drawn_in"]:
            continue
        v = views[f["drawn_in"]]
        s = v["scale"]
        want = (v["off"][0] + s * dot(f["entry"], v["x"]), v["off"][1] + s * dot(f["entry"], v["y"]))
        r = f["dia"] / 2 * s
        hit = [c for c in circles if abs(c[2] - r) < 1e-3 and math.hypot(c[0] - want[0], c[1] - want[1]) < 0.5]
        if not hit:
            fails.append("%s: no true circle Ø%s drawn at its place in view %s" % (tag, f["dia"], f["drawn_in"]))
            continue
        c = min(hit, key=lambda c: math.hypot(c[0] - want[0], c[1] - want[1]))
        # back to true size in the view, and compare with the STEP's own centre (independent reader)
        cx, cy = (c[0] - v["off"][0]) / s, (c[1] - v["off"][1]) / s
        near = [h for h in holes if abs(abs(dot(h["axis"], v["n"])) - 1) < 1e-6 and abs(h["dia"] - f["dia"]) < 0.011]
        d = min((math.hypot(dot(h["c"], v["x"]) - cx, dot(h["c"], v["y"]) - cy) for h in near), default=1e9)
        stats["worst_drawn"] = max(stats["worst_drawn"], d)
        if d > TOL:
            fails.append("%s: drawn circle centre is %.3f mm from the STEP hole (limit %s)" % (tag, d, TOL))
    for name, v in (views.items() if data["features"] else []):
        s = v["scale"]
        Ov = v.get("origin3d") or O
        o = (v["off"][0] + s * dot(Ov, v["x"]), v["off"][1] + s * dot(Ov, v["y"]))
        if not any(abs(c[2] - 1.2) < 1e-3 and math.hypot(c[0] - o[0], c[1] - o[1]) < 1e-3 for c in circles):
            fails.append("origin mark %s is not on the origin" % name)
    # 3. what the mechanical check reads
    text = page.get_text()
    up = text.upper()
    needs = [("UNITS: mm", r"UNITS:\s*MM\b"), ("MATERIAL", r"MATERIAL:"), ("FINISH", r"FINISH:"),
             ("TOLERANCE", r"TOLERANCE")]
    if data["features"]:
        needs += [("X (mm)", r"X \(MM\)"), ("Y (mm)", r"Y \(MM\)")]
    for need, pat in needs:
        if not re.search(pat, up):
            fails.append("text lacks %s" % need)
    # 4. keys fitted in the part's ends: a note for each key Joints' file puts there, naming the two holes that sit
    # where that file puts the key's screws
    ksrc = [s_ for s_ in data["sources"] if s_["role"] == "key positions"]
    if ksrc:
        with open(os.path.join(REPO, ksrc[0]["path"]), newline="", encoding="utf-8") as fh:
            krows = [r for r in csv.DictReader(fh) if data["pn"] in (r.get("carrier_key_in_its_end") or "")]
        fails += key_note_fails(text, matched, krows, holes=holes)
    if " " in text or "­" in text:
        fails.append("the text layer has non-breaking spaces or soft hyphens (search breaks)")
    if (doc.metadata or {}).get("creator") != "drawgen":
        fails.append("PDF Creator is not drawgen")
    # the owner's rule: every drawing names "Autonomous" as its creator, never a person
    if (doc.metadata or {}).get("author") != "Autonomous":
        fails.append("PDF author is not Autonomous")
    if not re.search(r"CREATED BY\s+Autonomous\b", page.get_text()):
        fails.append("the title block's CREATED BY is not Autonomous")
    for pg, phrase in note_makers(doc):
        fails.append("sheet %d: a note names a maker ('%s')" % (pg, phrase))
    for pg, what in clashes(doc):
        fails.append("sheet %d: %s" % (pg, what))
    faces = step_faces(step_path, data["pn"], data.get("placement"))
    tb = text_boxes(page, data["sheet_h"])
    if data.get("notches") or data.get("chamfers") or any(f["kind"] == "open_slot" for f in data["features"]):
        fails += open_slot_fails(data, faces, rows, tb)
        fails += flat_feature_fails(data, [f for f in faces if f["kind"] == "plane" and "n" in f and f["pts"]], tb)
    fails += end_cut_fails(data, faces, tb)
    fails += cut_list_fails(doc, data)
    if any(s_["role"] == "flat pattern" for s_ in data["sources"]) and not data.get("flat"):
        fails.append("a bent part's sheet has no record of its flat pattern")
    fails += flat_fails(data, tb, page.get_text())
    fails += flat_hole_fails(data, holes, faces)
    fails += csk_fails(data, faces, holes, page)
    fails += vgroove_radius_fails(data, faces)
    if data.get("flat"):
        cf = flat_cutout_fails(data, faces)
        if cf:
            fails += cf[0]
            fails += cutout_row_fails(data, rows, cf[1], page)
    two_wall = bool(two_wall_pairs(data["features"]))
    if two_wall and not re.search(r"SECTION [A-Z]-[A-Z]", up):
        fails.append("holes through two walls but no SECTION label")
    if verbose:
        print(json.dumps(stats))
    return fails, stats


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        f, st = check(p)
        print("%s: %s; %d table rows, %d STEP holes, worst table %.4f mm, worst drawn %.4f mm" % (
            os.path.basename(p), "PASS" if not f else "FAIL", st["rows"], st["holes"], st["worst_table"],
            st["worst_drawn"]))
        for x in f:
            print("  - " + x)
        bad += bool(f)
    sys.exit(1 if bad else 0)
