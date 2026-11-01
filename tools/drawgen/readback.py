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
        if not (nm.startswith(pn) or (inst["name"] or "").startswith(pn) or os.path.basename(step_path).startswith(pn + "_")):
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
        if not (nm.startswith(pn) or (inst["name"] or "").startswith(pn) or os.path.basename(step_path).startswith(pn + "_")):
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
        where = "chamfer at the %s end" % ("+" if ch["sgn"] > 0 else "-")
        if not fs:
            fails.append("%s: the STEP has no face where the drawing says" % where)
            continue
        qs = [q for f in fs for q in f["pts"]]
        la = max(dot(q, lax) for q in qs) - min(dot(q, lax) for q in qs)
        ls = max(dot(q, side) for q in qs) - min(dot(q, side) for q in qs)
        v = _num(ch["text"])
        if v is None or abs(v - la) > tol or abs(v - ls) > tol or not ch["text"].endswith("x 45°"):
            fails.append("%s: the sheet says %s, the STEP's legs %.3f and %.3f" % (where, ch["text"], la, ls))
        tip = ch["tip"]
        if not _text_near(texts, ch["text"], (tip[0], tip[1], tip[0], tip[1])):
            fails.append("%s: its size %s is not printed by it" % (where, ch["text"]))
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
