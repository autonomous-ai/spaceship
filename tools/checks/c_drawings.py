#!/usr/bin/env python3
"""C05 drawing completeness.

Every part we make (part numbers xx1000 to xx7999) has a drawing, and every
assembly (xx0001 to xx0999) has an assembly drawing, named
PARTNO_REV_NAME_DWG.pdf (conventions section 7) with the same revision as its
CAD and STEP. In each part drawing's text: units, material, finish, a
tolerance rule, the projection, and the holes (tags H01..., a hole table, or
diameter callouts) against the holes the STEP of that part has.

Reads PDF text with PyMuPDF when it is installed, else with pdftotext. The
text test can't see symbols drawn as lines (the first-angle symbol); those
are noted, not failed.
"""

import math
import os
import re
import shutil
import subprocess

from common import Finding, owner_for, rel, walk_files, parse_file_name, pn_class, is_soft
import dxf_layers
import stepfile as sf


def pdf_text(path):
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass
    exe = shutil.which("pdftotext")
    if exe:
        out = subprocess.run([exe, "-layout", path, "-"], capture_output=True, text=True, timeout=60)
        return out.stdout
    return None


# D-112: part drawings made by the STEP-driven generator (tools/drawgen) say so in the PDF's Creator or Producer
# field. They are checked by the same rules; a finding on one goes to the generator's group, which regenerates it.
GENERATOR = re.compile(r"\bdrawgen\b", re.I)
GENERATOR_OWNER = "Drawing Generator"
GENERATOR_FIX = " This drawing was made by tools/drawgen (D-112): fix the generator and regenerate it."


def made_by_generator(path):
    """True when the PDF's Creator or Producer field names drawgen (D-112)."""
    try:
        import fitz  # PyMuPDF
        try:
            with fitz.open(path) as doc:
                meta = doc.metadata or {}
        except Exception:
            return False
        return any(GENERATOR.search(str(meta.get(k) or "")) for k in ("creator", "producer"))
    except ImportError:
        pass
    exe = shutil.which("pdfinfo")
    if exe:
        out = subprocess.run([exe, path], capture_output=True, text=True, timeout=60).stdout
        return any(GENERATOR.search(line) for line in out.splitlines() if line.startswith(("Creator:", "Producer:")))
    return False


def index_files(root):
    """pn -> {doctype: [(rev, path)]} for every conventions-named file."""
    idx = {}
    for top in ("v2/01-CAD-Native", "v2/02-Drawings", "v2/03-Manufacturing"):
        for p in walk_files(root, top):
            m = parse_file_name(p)
            if not m:
                continue
            idx.setdefault(m["pn"], {}).setdefault(m["doc"], []).append((m["rev"], p))
    return idx


def hole_axes(step_holes):
    """Distinct hole axes (holes on one axis through two tube walls count once)."""
    axes = []
    for h in step_holes:
        for a in axes:
            if abs(abs(sum(x * y for x, y in zip(a.axis, h.axis))) - 1.0) < 1e-4:
                d = [h.center[k] - a.center[k] for k in range(3)]
                t = sum(d[k] * a.axis[k] for k in range(3))
                lat = (sum(x * x for x in d) - t * t) ** 0.5
                if lat < 0.05:
                    break
        else:
            axes.append(h)
    return axes


def two_wall_axes(holes):
    """Hole axes of one body with holes in two walls (a tube drilled through both walls): D-113 wants a section or
    the opposite view for them."""
    return sum(1 for a in hole_axes(holes)
               if sum(1 for h in holes if abs(abs(sum(x * y for x, y in zip(a.axis, h.axis))) - 1.0) < 1e-4 and
                      _off_axis(h.center, a) < 0.05) >= 2)


def _off_axis(p, a):
    d = [p[k] - a.center[k] for k in range(3)]
    t = sum(d[k] * a.axis[k] for k in range(3))
    return max(sum(x * x for x in d) - t * t, 0.0) ** 0.5


def body_shape(solid):
    """A body's shape, however it is placed or turned: face and hole counts, hole sizes and the total length of
    its straight edges. Copies of one part share it (seven washers at different angles); a frame's members of
    different lengths don't."""
    edges = sum(sum((a[k] - b[k]) ** 2 for k in range(3)) ** 0.5 for f in solid.faces for a, b in f.lines)
    return (len(solid.faces), len(solid.holes), tuple(sorted(round(h.diameter, 2) for h in solid.holes)),
            round(edges, 1))


# D-113 (PM, 2026-11-01), for the generator's drawings: a section (or the opposite view) wherever holes go through
# both walls of a tube, labelled; and bent parts stay in Fusion
SECTION_LABEL = re.compile(r"\bSECTION\s+([A-Z])\s*[-\u2013]\s*\1\b|\b([A-Z])\s*[-\u2013]\s*\2\b|\bVIEW(?:ED)?\s+(?:[A-Z]\b|FROM\b)")


# D-89 (PM rule, 2026-11-01): a part covered by a tabulated drawing that lists its part number counts
# as drawn; a plain knife-cut felt or fill rectangle needs no drawing when the cut list gives its size,
# material, tolerance and part number.
TABULATED = re.compile(r"\bTABULATED\b", re.I)


def tabulated_cover(idx):
    """pn -> [(rev, pdf, drawing pn)] for the part numbers listed in a tabulated drawing. A tabulated drawing
    says TABULATED in its text; it covers every other number of its own family and kind (parts for a part
    drawing, assemblies for an assembly drawing) that its text lists, so a mating part named in a note or an
    assembly drawing's parts list doesn't count."""
    cover = {}
    for own, files in idx.items():
        kind = pn_class(own)
        if kind not in ("part", "assembly"):
            continue
        for rv, p in files.get("DWG", []):
            if not p.lower().endswith(".pdf"):
                continue
            text = pdf_text(p)
            if not text or not TABULATED.search(text):
                continue
            for n in sorted(set(re.findall(r"(?<!\d)(\d{6})(?!\d)", text))):
                if n != own and n[:2] == own[:2] and pn_class(n) == kind:
                    cover.setdefault(n, []).append((rv, p, own))
    return cover


def _cell(row, pattern):
    return [(k, (v or "").strip()) for k, v in row.items() if k and re.search(pattern, k, re.I) and (v or "").strip()]


FEATURE_WORDS = re.compile(r"\b(?:pockets?|notch(?:es)?|holes?|slots?|cut-?outs?)\b", re.I)     # D-89: these keep the drawing


def cut_list_lacks(root, pn, thickness=False):
    """D-89: None when no list has a row for pn (a cell that is exactly the number), else (what the most
    complete row lacks of size, thickness when asked (soft goods other than felt and fill), material and
    tolerance, its file, the features the row names: pockets, notches, holes). A cut list is a .csv with "cut"
    in its name, and a parts-list row that gives the same serves as one (PM ruling 2026-11-01, as the release
    checklist reads it): every .csv under v2/03-Manufacturing and v2/02-Drawings counts."""
    from common import read_csv
    best = None
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                if not any((v or "").strip() == pn for v in row.values() if isinstance(v, str)):
                    continue
                lacks = []
                sizes = _cell(row, r"size|dimension|length|width|thick|^[lwt]_?mm$")
                if not any(re.search(r"\d", v) for _k, v in sizes):
                    lacks.append("size")
                thick = any(re.search(r"\d", v) for _k, v in _cell(row, r"thick|^t_?mm$")) or any(
                    len(re.findall(r"\d+(?:\.\d+)?", v)) >= 3 and re.search(r"[x×]", v, re.I) for _k, v in sizes)
                if thickness and not thick:
                    lacks.append("thickness")
                if not _cell(row, r"material|grade"):
                    lacks.append("material")
                if not _cell(row, r"tol") and not any(re.search(r"±|\+/-", v or "") for v in row.values()
                                                      if isinstance(v, str)):
                    lacks.append("tolerance")
                feats = sorted({m.group(0).lower() for v in row.values() if isinstance(v, str)
                                for m in FEATURE_WORDS.finditer(v)})
                if best is None or len(lacks) + len(feats) < len(best[0]) + len(best[2]):
                    best = (lacks, rel(root, p), feats)
    return best


# D-125 (PM, 2026-11-01), extending D-89: a plain straight-cut strip or sheet with no features passes on a full
# parts-list line instead of a drawing: material and grade, thickness, length, width, finish and tolerance.
def cuboid_sides(solid):
    """The three sides of a body that is a plain rectangular block (six flat faces in three square pairs, no holes,
    no bends), smallest first; None for any other shape."""
    fs = solid.faces
    if len(fs) != 6 or any(f.kind != "plane" for f in fs) or solid.holes or solid.bends:
        return None
    dirs = []
    for f in fs:
        if not any(abs(abs(sum(a * b for a, b in zip(f.normal, d))) - 1.0) < 1e-6 for d in dirs):
            dirs.append(f.normal)
    if len(dirs) != 3 or any(abs(sum(a * b for a, b in zip(dirs[i], dirs[j]))) > 1e-6
                             for i in range(3) for j in range(i + 1, 3)):
        return None
    pts = list(solid.points())
    if not pts:
        return None
    sides = [max(sum(a * b for a, b in zip(p, d)) for p in pts) - min(sum(a * b for a, b in zip(p, d)) for p in pts)
             for d in dirs]
    return tuple(round(x, 3) for x in sorted(sides))


def is_strip(sides):
    """A strip or sheet rather than a block or a bar: thin, at most 25 mm and half its width (as flat_plate reads a
    sheet)."""
    return bool(sides) and sides[0] <= 25.0 and sides[0] <= 0.5 * sides[1]


def strip_sides(step_paths, load=None):
    """D-125's per-part strip list: part number -> the three sides (smallest first) of its one shape, for each part
    whose bodies, across all the given STEP files, have a single shape (body_shape: copies and the same part in a
    second file count once) and that shape is a plain rectangular block thin enough to be a strip or sheet
    (cuboid_sides, is_strip). A part with two or more shapes, a thick block or a bar, or any other shape is left
    out. load: path -> a parsed STEP (stepfile.StepFile when not given). The release checklist calls this rather
    than copying it: keep its name and arguments."""
    if load is None:
        import stepfile
        load = stepfile.StepFile
    shapes = {}
    for p in step_paths:
        s = load(p)
        for inst in s.instances():
            so = s.solid(inst["solid"])
            shapes.setdefault(inst["part_number"], {}).setdefault(body_shape(so), so)
    out = {}
    for pn, by_shape in shapes.items():
        if len(by_shape) != 1:
            continue
        sides = cuboid_sides(next(iter(by_shape.values())))
        if is_strip(sides):
            out[pn] = sides
    return out


PLUS_MINUS = re.compile(r"±|\+\s*/\s*-|\+\s*\d+(?:\.\d+)?\s*/\s*-?\s*\d")    # ±0.5, +/-1, +0/-0.5, +0.10/0


def tolerance_cover(tolerance_texts, row_texts):
    """D-125 (PM, 2026-11-01): which cut sizes, of 'length' and 'width', a parts-list line's tolerance covers. One
    general tolerance covers both (ISO 2768, or a ± on the cut sizes, all sizes, or no size named); otherwise each
    takes its own (a ± naming the length or the width). A bought strip whose width comes from the supplier says
    "width as supplied" anywhere in its line. A ± on the thickness, bends, angles, holes or flatness covers neither;
    the thickness takes the sheet's own tolerance, as its grade names it."""
    cover = set()
    if any(re.search(r"\bwidth\s+as\s+supplied\b", t or "", re.I) for t in row_texts):
        cover.add("width")
    for text in tolerance_texts:
        for clause in re.split(r"[;,]", text or ""):
            if re.search(r"ISO\s*2768", clause, re.I):
                cover |= {"length", "width"}
                continue
            if not PLUS_MINUS.search(clause):
                continue
            named = False
            if re.search(r"\blength|\blong\b", clause, re.I):
                cover.add("length")
                named = True
            if re.search(r"\bwidth|\bwide\b", clause, re.I):
                cover.add("width")
                named = True
            if not named and not re.search(r"thick|\bbent\b|\bbend|angle|°|hole|position|flat|square", clause, re.I):
                cover |= {"length", "width"}          # on the cut sizes, all sizes, or no size named
    return cover


def strip_row_lacks(root, pn, sides):
    """D-125: None when no list has a row for pn; else (what the most complete row lacks, its file). A full row
    gives the material with its grade (a grade on HOLD counts as stated, as C11 holds such rows; the part stays HOLD
    until the grade is named), the thickness, width and length as in the STEP, the finish, a tolerance covering both
    cut sizes (tolerance_cover), and names no feature (hole, slot, notch, pocket, cut-out). Any .csv under
    v2/03-Manufacturing or v2/02-Drawings counts, as for D-89. The release checklist calls this function (and
    cuboid_sides, is_strip) rather than copying it: keep their names and arguments."""
    from common import read_csv
    from c_parts import GRADE_HINT, VAGUE_FINISH
    best = None
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                if not any((v or "").strip() == pn for v in row.values() if isinstance(v, str)):
                    continue
                lacks = []
                mat = " ".join(v for _k, v in _cell(row, r"material|grade"))
                if not mat:
                    lacks.append("material")
                elif not (GRADE_HINT.search(mat) or re.search(r"\b(?:grade|alloy)\b\s*:?\s*\w", mat, re.I)):
                    lacks.append("the material's grade")
                nums = [float(x) for _k, v in _cell(row, r"size|dimension|length|width|thick|^[lwt]_?mm$")
                        for x in re.findall(r"\d+(?:\.\d+)?", v)]
                if any(not any(abs(n - x) <= max(0.1, 0.002 * x) for n in nums) for x in sides):
                    lacks.append("thickness, width and length as in its STEP (%s mm)" % " x ".join("%g" % x for x in sides))
                fin = " ".join(v for _k, v in _cell(row, r"finish"))
                if not fin or VAGUE_FINISH.search(fin):
                    lacks.append("finish")
                texts = [v for v in row.values() if isinstance(v, str)]
                tols = [v for _k, v in _cell(row, r"tol")] + [v for v in texts if PLUS_MINUS.search(v)]
                missing = [x for x in ("length", "width") if x not in tolerance_cover(tols, texts)]
                if missing:
                    lacks.append("a tolerance on the %s (one general tolerance on the cut sizes, such as ISO 2768-m "
                                 "or '±0.5 on cut sizes', or one for each; 'width as supplied' for a bought strip)"
                                 % " and the ".join(missing))
                feats = sorted({m.group(0).lower() for v in row.values() if isinstance(v, str)
                                for m in FEATURE_WORDS.finditer(v)})
                if feats:
                    lacks.append("a plain piece (its row names %s)" % " and ".join(feats))
                if best is None or len(lacks) < len(best[0]):
                    best = (lacks, rel(root, p))
    return best


# D-128 (PM, 2026-11-01), extending D-89 part (3): a felt or fill piece cut from sheet or roll, with through-openings
# or edge notches only, needs no drawing when its DXF gives the full outline with every opening and its parts-list row
# gives material, density or grade, thickness, tolerance and part number. A pocket or any other depth feature keeps the
# drawing. The release checklist calls prism_shapes and felt_dxf_lacks rather than copying them: keep their names and
# arguments.
def _d(a, b):
    return sum(x * y for x, y in zip(a, b))


def prism_shape(solid):
    """D-128: a body cut from sheet or roll with through features only. Two flat faces at the sheet's two levels;
    every other face square to them (flat walls, or round ones whose axis runs along the sheet's normal). Returns
    ({'thickness', 'sides', 'loops'}, '') or (None, why)."""
    planes = [f for f in solid.faces if f.kind == "plane"]
    pts = list(solid.points())
    if not planes or not pts:
        return None, "its STEP has no flat faces"
    dirs = []
    for f in planes:
        if not any(abs(abs(_d(f.normal, d)) - 1.0) < 1e-6 for d in dirs):
            dirs.append(f.normal)
    def extent(d):
        v = [_d(p, d) for p in pts]
        return max(v) - min(v), min(v), max(v)
    n = min(dirs, key=lambda d: extent(d)[0])
    t, lo, hi = extent(n)
    top = []
    for f in solid.faces:
        if f.kind == "plane":
            c = abs(_d(f.normal, n))
            if c > 1 - 1e-6:
                lvl = _d(f.origin, n)
                if abs(lvl - lo) < 0.01 or abs(lvl - hi) < 0.01:
                    if abs(lvl - hi) < 0.01:
                        top.append(f)
                    continue
                return None, "a face sits between the sheet's two faces (a pocket or a step)"
            if c > 1e-4:
                return None, "a face sits at an angle to the sheet (a chamfer or bevel)"
        elif f.kind == "cylinder":
            if abs(abs(_d(f.normal, n)) - 1.0) > 1e-4:
                return None, "a round face runs across the sheet"
        else:
            return None, "a %s face (not a straight through-cut)" % f.kind
    if not top:
        return None, "no face at the sheet's top level"
    # the top face's closed boundaries: the outline and each opening
    edges = []
    for f in top:
        for a, b in f.lines:
            edges.append((a, b))
        for arc in f.arcs:
            edges.append((arc[2], arc[3]))
    key = lambda p: tuple(round(x, 2) for x in p)
    count = {}
    for a, b in edges:
        k = frozenset((key(a), key(b)))
        count[k] = count.get(k, 0) + 1
    edges = [(a, b) for a, b in edges if count[frozenset((key(a), key(b)))] == 1 or key(a) == key(b)]
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(key(a))] = find(key(b))
    loops = len({find(key(a)) for a, _b in edges})
    # the outline's two sides: along the longest straight edge in the top face, and across it
    longest = max((e for f in top for e in f.lines), key=lambda e: math.dist(*e), default=None)
    if longest is None:
        return None, "the sheet face has no straight edge"
    d1 = sf.norm(sf._sub(longest[1], longest[0]))
    d2 = sf.norm(sf.cross(n, d1))
    s1 = extent(d1)[0]
    s2 = extent(d2)[0]
    return {"thickness": round(t, 3), "sides": tuple(round(x, 2) for x in sorted((s1, s2))), "loops": loops}, ""


def prism_shapes(step_paths, load=None):
    """D-128's per-part shapes: part number -> (prism_shape's dict, '') when its bodies, across all the given STEP
    files, have one shape (body_shape) cut straight through from sheet or roll, or (None, why) for one shape that
    isn't, or (None, 'two or more shapes') for more. load: path -> a parsed STEP (stepfile.StepFile when not given)."""
    if load is None:
        import stepfile
        load = stepfile.StepFile
    shapes = {}
    for p in step_paths:
        s = load(p)
        for inst in s.instances():
            so = s.solid(inst["solid"])
            shapes.setdefault(inst["part_number"], {}).setdefault(body_shape(so), so)
    out = {}
    for pn, by_shape in shapes.items():
        out[pn] = prism_shape(next(iter(by_shape.values()))) if len(by_shape) == 1 else \
            (None, "its STEP holds two or more shapes under this number")
    return out


UNITS = {"0": 1.0, "1": 25.4, "4": 1.0, "5": 10.0, "6": 1000.0}


def _records(pairs):
    """[(section, block name or None, record type, [(code, value), ...])] for every record of a DXF."""
    out, sec, blk, cur, want_sec, want_blk = [], None, None, None, False, False
    for c, v in pairs:
        if c == "0":
            if cur is not None:
                out.append(cur)
                cur = None
            if v == "SECTION":
                want_sec = True
            elif v == "ENDSEC":
                sec = None
            elif v == "EOF":
                break
            elif sec == "BLOCKS" and v == "BLOCK":
                want_blk = True
            elif sec == "BLOCKS" and v == "ENDBLK":
                blk = None
            elif sec in ("ENTITIES", "BLOCKS"):
                cur = (sec, blk, v, [])
            continue
        if want_sec and c == "2":
            sec, want_sec = v.upper(), False
        elif want_blk and c == "2":
            blk, want_blk = v, False
        elif cur is not None:
            cur[3].append((c, v))
    if cur is not None:
        out.append(cur)
    return out


def _entities(records):
    """The drawn entities of the ENTITIES section and of each block, a POLYLINE with its VERTEX records."""
    ents, blocks, i = [], {}, 0
    while i < len(records):
        sec, blk, typ, g = records[i]
        i += 1
        if typ in ("VERTEX", "SEQEND"):
            continue
        e = {"type": typ, "g": dict(g), "seq": g, "verts": []}
        if typ == "POLYLINE":
            while i < len(records) and records[i][2] == "VERTEX":
                e["verts"].append(dict(records[i][3]))
                i += 1
            if i < len(records) and records[i][2] == "SEQEND":
                i += 1
        (blocks.setdefault(blk, []) if sec == "BLOCKS" and blk else ents).append(e)
    return ents, blocks


def dxf_shapes(path):
    """The closed shapes a DXF draws, without a library: only what the drawing places (its ENTITIES and the blocks an
    INSERT places, nested), as D-89 reads a DXF. {'loops', 'open', 'size': (w, L) of everything drawn, in mm}."""
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    units = next((pairs[k + 1][1] for k, (c, v) in enumerate(pairs[:-1]) if c == "9" and v == "$INSUNITS"), None)
    ents, blocks = _entities(_records(pairs))
    scale = UNITS.get(units or "0", 1.0)
    segs, pts = [], []
    loops = 0
    def num(g, c, dflt=0.0):
        try:
            return float(g.get(c, dflt))
        except ValueError:
            return dflt
    def emit(items, tf, depth=0):
        nonlocal loops
        for e in items:
            g, typ = e["g"], e["type"]
            if typ == "CIRCLE":
                cx, cy = tf(num(g, "10"), num(g, "20"))
                r = num(g, "40") * tf.s
                pts.extend([(cx - r, cy - r), (cx + r, cy + r)])
                loops += 1
            elif typ == "LINE":
                a, b = tf(num(g, "10"), num(g, "20")), tf(num(g, "11"), num(g, "21"))
                segs.append((a, b))
                pts.extend([a, b])
            elif typ == "ARC":
                cx, cy, r = num(g, "10"), num(g, "20"), num(g, "40")
                a0, a1 = math.radians(num(g, "50")), math.radians(num(g, "51"))
                if a1 <= a0:
                    a1 += 2 * math.pi
                ps = [tf(cx + r * math.cos(a0 + (a1 - a0) * i / 16), cy + r * math.sin(a0 + (a1 - a0) * i / 16))
                      for i in range(17)]
                segs.append((ps[0], ps[-1]))
                pts.extend(ps)
            elif typ in ("POLYLINE", "LWPOLYLINE"):
                if typ == "POLYLINE":
                    vs = [tf(num(x, "10"), num(x, "20")) for x in e["verts"]]
                else:
                    xs = [float(v) for c, v in e["seq"] if c == "10"]
                    ys = [float(v) for c, v in e["seq"] if c == "20"]
                    vs = [tf(x, y) for x, y in zip(xs, ys)]
                pts.extend(vs)
                if vs and (int(num(g, "70")) & 1 or (len(vs) > 2 and math.dist(vs[0], vs[-1]) < 1e-6)):
                    loops += 1
                else:
                    segs.extend(zip(vs, vs[1:]))
            elif typ == "INSERT" and depth < 8:
                bx, by = num(g, "10"), num(g, "20")
                sx, sy = num(g, "41", 1.0), num(g, "42", 1.0)
                rot = math.radians(num(g, "50"))
                def sub(x, y, tf=tf, bx=bx, by=by, sx=sx, sy=sy, rot=rot):
                    x, y = x * sx, y * sy
                    return tf(bx + x * math.cos(rot) - y * math.sin(rot), by + x * math.sin(rot) + y * math.cos(rot))
                sub.s = tf.s * abs(sx)
                emit(blocks.get(g.get("2", ""), []), sub, depth + 1)
    def base(x, y):
        return (x * scale, y * scale)
    base.s = scale
    emit(ents, base)
    key = lambda p: (round(p[0], 2), round(p[1], 2))
    deg, parent = {}, {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in segs:
        ka, kb = key(a), key(b)
        deg[ka] = deg.get(ka, 0) + 1
        deg[kb] = deg.get(kb, 0) + 1
        parent[find(ka)] = find(kb)
    comps = {}
    for node in deg:
        comps.setdefault(find(node), []).append(node)
    opens = 0
    for nodes in comps.values():
        if all(deg[x] == 2 for x in nodes):
            loops += 1
        else:
            opens += 1
    if not pts:
        return {"loops": loops, "open": opens, "size": (0.0, 0.0), "units": units}
    w = max(p[0] for p in pts) - min(p[0] for p in pts)
    h = max(p[1] for p in pts) - min(p[1] for p in pts)
    return {"loops": loops, "open": opens, "size": tuple(round(x, 2) for x in sorted((w, h))), "units": units}


DENSITY = re.compile(r"\d+(?:[.,]\d+)?\s*(?:kg|g)\s*/\s*m\s*[23²³]|\bgsm\b|\bdensity\b", re.I)
DEPTH_WORDS = re.compile(r"\bpockets?\b|\bdepth\b|\bblind\b|\brebate|\bcounterbor", re.I)   # not "stepped": a stepped outline is a through cut


def felt_row_lacks(root, pn, thickness=None):
    """D-128: None when no list has a row for pn; else (what the most complete row lacks, its file): material,
    density or grade (a density such as 25 kg/m3, or a grade as C11 reads one), the thickness (the STEP's, when
    known), tolerance, and no pocket or other depth feature named."""
    from common import read_csv
    from c_parts import GRADE_HINT
    best = None
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                if not any((v or "").strip() == pn for v in row.values() if isinstance(v, str)):
                    continue
                lacks = []
                mat = " ".join(v for _k, v in _cell(row, r"material|grade|density"))
                if not mat:
                    lacks.append("material")
                elif not (DENSITY.search(mat) or GRADE_HINT.search(mat)):
                    lacks.append("density or grade")
                sizes = _cell(row, r"size|dimension|thick|^t_?mm$")
                nums = [float(x) for _k, v in sizes for x in re.findall(r"\d+(?:\.\d+)?", v)]
                nums += [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*mm\b", mat)]    # "PET felt 9 mm"
                if thickness is not None and not any(abs(n - thickness) <= 0.2 for n in nums):
                    lacks.append("thickness (%g mm, as in its STEP)" % thickness)
                elif thickness is None and not nums:
                    lacks.append("thickness")
                if not _cell(row, r"tol") and not any(PLUS_MINUS.search(v or "") for v in row.values()
                                                      if isinstance(v, str)):
                    lacks.append("tolerance")
                depth = sorted({m.group(0).lower() for v in row.values() if isinstance(v, str)
                                for m in DEPTH_WORDS.finditer(v)})
                if depth:
                    lacks.append("through features only (its row names %s)" % " and ".join(depth))
                if best is None or len(lacks) < len(best[0]):
                    best = (lacks, rel(root, p))
    return best


def felt_dxf_lacks(root, pn, shape, dxf_path):
    """D-128: what a felt or fill piece still lacks for its DXF and parts-list row to stand in for a drawing; [] when
    nothing. shape: prism_shapes' entry for pn ((dict, '') or (None, why)), None when no STEP shows the piece."""
    lacks = []
    sh, why = shape if shape else (None, "no STEP shows it")
    if sh is None:
        lacks.append("a piece cut straight through (%s)" % why)
    try:
        with open(dxf_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        text = ""
    others = dxf_layers.other_layers(text) if text else set()
    if others:
        lacks.append("a DXF on the CUT and MARK layers only (it also draws on %s)" % ", ".join(sorted(others)))
    d = dxf_shapes(dxf_path) if text and not text.startswith("AutoCAD Binary DXF") else None
    if d is None:
        lacks.append("a DXF it can read (ASCII)")
    elif sh is not None:
        if d["open"]:
            lacks.append("a DXF whose lines all close (%d open)" % d["open"])
        if d["loops"] != sh["loops"]:
            lacks.append("the full outline with every opening in its DXF (the STEP has %d closed shapes, the DXF %d)"
                         % (sh["loops"], d["loops"]))
        if any(abs(a - b) > max(0.5, 0.002 * b) for a, b in zip(d["size"], sh["sides"])):
            lacks.append("a DXF outline the size of the STEP's (%g x %g mm; the DXF draws %g x %g)"
                         % (sh["sides"] + d["size"]))
    row = felt_row_lacks(root, pn, sh["thickness"] if sh else None)
    if row is None:
        lacks.append("a parts-list row")
    elif row[0]:
        lacks.append("in its row in %s: %s" % (row[1], ", ".join(row[0])))
    return lacks


def soft_kind(name):
    """'felt or fill', 'soft' (foam, gasket, seal, tape) or '' by the name's head noun (D-89)."""
    if not is_soft(name):
        return ""
    return "felt or fill" if is_soft(name, kinds=("FELT", "FILL")) else "soft"


# D-89 part 4 (PM rule, 2026-11-01): a flat part cut from sheet (laser, waterjet or CNC router) with no bends
# and no machined features needs no drawing when its DXF gives the full outline and every hole, and its
# parts-list row gives material, thickness, finish, a general tolerance (ISO 2768-m) and any critical hole note.
# The row is read exactly as the release checklist reads it (v2/00-Control/build_release_checklist.py,
# flat_lacks; same patterns); the check adds what only the files show: a line on the DXF's BEND layer means
# folded (Reviewer 6's hardening), the STEP shows no bends, pockets or blind holes, and the DXF has every hole.
SHEET_CUT = re.compile(r"laser|water\s*-?\s*jet|router|routed", re.I)
NOT_FLAT = re.compile(r"bend|bent|fold|brake|groove|\blap\b|half-lap|rebate|pocket|machin|\bmill(?:ed|ing)?\b|drill|"
                      r"\btap(?:ped|ping)?\b|thread|countersink|counterbore|ream|\bturn(?:ed|ing)?\b|lathe|chamfer|weld|"
                      r"bond", re.I)
BEND_LAYER = re.compile(r"\b(?:BEND|FOLD)", re.I)
METAL = re.compile(r"alumin|steel|zinc", re.I)     # D-99: part 4 is for flat metal sheet (the checklist's METAL)
ACP = re.compile(r"\bACP\b|aluminium composite", re.I)   # D-100: and flat ACP (the checklist's ACP)


def dxf_other_layers(text):
    """D-89 (4): the layers other than CUT and MARK that a DXF draws on; None when it can't be read. One reader,
    shared with the release checklist (tools/checks/dxf_layers.py), so the two tools can't drift."""
    return dxf_layers.other_layers(text)


def dxf_summary(path):
    """What the D-89 part 4 hole check needs from a DXF, read without a library: {'units': $INSUNITS,
    'circles': [diameters of the CIRCLE entities it draws]}; None when it can't be read as ASCII DXF. Which layers
    it draws on is the shared reader's job (dxf_layers), not this one's."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    if not text.strip() or text.startswith("AutoCAD Binary DXF"):
        return None
    lines = text.splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines) - 1, 2)]
    out = {"units": None, "circles": []}
    sec, cur = None, None
    for k, (code, val) in enumerate(pairs):
        if code == "2" and k and pairs[k - 1] == ("0", "SECTION"):
            sec, cur = val.upper(), None
        elif code == "0" and val == "ENDSEC":
            sec, cur = None, None
        elif code == "9" and val == "$INSUNITS" and k + 1 < len(pairs):
            out["units"] = pairs[k + 1][1]
        elif sec == "ENTITIES" and code == "0":
            cur = val.upper()
        elif sec == "ENTITIES" and cur == "CIRCLE" and code == "40":
            try:
                out["circles"].append(round(2.0 * float(val), 2))
            except ValueError:
                pass
    return out


def _rows_naming(root, pn):
    """Every row of a .csv under v2/03-Manufacturing or v2/02-Drawings with a cell that is exactly pn, as
    ({column: value}, file): the rows a D-89 reading may use (the checklist reads the same files)."""
    from common import read_csv
    for top in ("v2/03-Manufacturing", "v2/02-Drawings"):
        for p in walk_files(root, top, exts=(".csv",)):
            for row in read_csv(p):
                cells = {(k or "").strip(): (v or "").strip() for k, v in row.items()
                         if isinstance(k, str) and isinstance(v, str)}
                if pn in cells.values():
                    yield cells, rel(root, p)


def flat_row_lacks(root, pn):
    """D-89 (4), as the checklist's flat_lacks: what the best row lacks for a flat part cut from sheet to go
    without a drawing; None when no row has the number."""
    best = None
    for cells, _p in _rows_naming(root, pn):
        def has(pattern):
            return [v for k, v in cells.items() if re.search(pattern, k, re.I) and v]
        process = " ".join(has(r"process"))
        material = " ".join(has(r"material|grade"))
        sizes = has(r"size|dimension|length|width|thick|^[lwt]_?mm$")
        thick = any(re.search(r"\d", v) for v in has(r"thick|^t_?mm$")) or any(
            len(re.findall(r"\d+(?:\.\d+)?", v)) >= 3 and re.search(r"[x×]", v, re.I) for v in sizes) or bool(
            re.search(r"\d+(?:\.\d+)?\s*mm\b", material))
        not_flat = sorted({m.group(0).lower() for m in NOT_FLAT.finditer(process)})
        lacks = [n for n, ok in (
            ("metal or ACP sheet (D-99, D-100)", bool(METAL.search(material) or ACP.search(material))),
            ("a cut by laser, waterjet or router in its process", bool(SHEET_CUT.search(process))),
            ("no bends or machined features (its process names %s)" % ", ".join(not_flat), not not_flat),
            ("material", bool(material)), ("thickness", thick), ("finish", bool(has(r"finish"))),
            ("an ISO 2768 general tolerance", any("2768" in v for v in cells.values()))) if not ok]
        if best is None or len(lacks) < len(best):
            best = lacks
    return best


def flat_cut_lacks(root, pn, files, holes, flat):
    """D-89 part 4: what keeps this part from going without a drawing (empty when it may). flat: the STEP's
    (ok, thickness, why), or None when no STEP holds the part."""
    why = []
    dxfs = sorted(files.get("DXF", []))
    if not dxfs:
        return ["it has no DXF of its own"]
    rv, dxf = dxfs[-1]
    try:
        with open(dxf, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        text = ""
    other = dxf_other_layers(text)
    d = dxf_summary(dxf)
    if other is None or d is None:
        return ["its DXF can't be read, so it can't be shown flat"]
    if other:
        other = sorted(other)
        bend = [l for l in other if BEND_LAYER.search(l)]
        why.append("its DXF draws on %s; only CUT and MARK pass%s" % (", ".join(other), ", so it is folded" if bend else ""))
    if d["units"] not in (None, "4"):
        why.append("its DXF isn't in mm ($INSUNITS %s)" % d["units"])
    cad_revs = {r for r, _p in files.get("CAD", []) + files.get("STEP", [])}
    if cad_revs and rv not in cad_revs:
        why.append("its DXF is revision %s but its CAD/STEP is %s" % (rv, "/".join(sorted(cad_revs))))
    if flat is not None and not flat[0]:
        why.append(flat[2])
    want = {}
    for h in hole_axes(holes or []):          # every hole in the STEP must be in the DXF, by diameter
        k = round(h.diameter, 1)
        want[k] = want.get(k, 0) + 1
    for dia, n in sorted(want.items()):
        got = sum(1 for c in d["circles"] if abs(c - dia) <= 0.1)
        if got < n:
            why.append("its DXF has %d of the %d Ø%g holes in its STEP" % (got, n, dia))
    lacks = flat_row_lacks(root, pn)
    worked = [l for l in (lacks or []) if l.startswith("no bends or machined features")]
    # a folded or machined part keeps its drawing: say why, and leave out the row's other gaps
    not_flat = [w for w in why if "only CUT and MARK pass" in w or w == (flat[2] if flat is not None and not flat[0] else None)]
    if not_flat or worked:
        return not_flat + ["its row's process names %s" % l.split("names ", 1)[-1].rstrip(")") for l in worked]
    if lacks is None:
        why.append("no parts list or cut list has a row for it")
    elif lacks:
        why.append("its row lacks %s" % "; ".join(lacks))
    return why


def policy(root, key, default):
    p = os.path.join(root, "v2/04-Checks/config/policy.csv")
    if os.path.exists(p):
        import csv
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("key") == key and row.get("value"):
                    return row["value"].strip()
    return default


def screen_locked():
    """True when this Mac's console session is locked (ioreg IOConsoleUsers), as tools/fusion/start_drawing.py
    reads it; None when it can't tell (not a Mac, no ioreg)."""
    import plistlib
    try:
        out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=30).stdout
        data = plistlib.loads(out)
    except Exception:
        return None
    data = data[0] if isinstance(data, list) else data
    return any(u.get("CGSSessionScreenIsLocked") for u in data.get("IOConsoleUsers", []))


def hidden_lines_allowed(root):
    """drawing file name -> the number of views that keep hidden lines on purpose, from
    v2/04-Checks/config/hidden-lines-allow.csv (drawing, views, reason, ruling)."""
    from common import read_csv
    p = os.path.join(root, "v2/04-Checks/config/hidden-lines-allow.csv")
    out = {}
    for row in (read_csv(p) if os.path.exists(p) else []):
        try:
            out[(row.get("drawing") or "").strip()] = int(row.get("views") or 0)
        except ValueError:
            pass
    return out


def drawing_traps(pdf, allowed_views=0):
    """The PM's four drawing traps read back from the PDF (pdf_traps.py, ELECTRICAL's read-back, 2026-11-01):
    text under 2.5 mm capital height (title-block labels under 1.8) and a first-angle symbol without 4 corners are
    major; hidden lines in more views than allowed and a dimension value printed twice are minor. One entry per
    rule, the sheets of a multi-sheet PDF joined: [(rule, severity, message, fix)]. [] when PyMuPDF isn't there."""
    try:
        import pdf_traps
        found = pdf_traps.findings(pdf, allowed_views)
    except ImportError:
        return []
    merged = {}
    for rule, sev, msg, fix in found:
        if rule in merged:
            merged[rule] = (rule, sev, merged[rule][2] + " " + msg, fix)
        else:
            merged[rule] = (rule, sev, msg, fix)
    return list(merged.values())


def drawgen_parts(root):
    """D-113: the numbers tools/drawgen draws, from its own registry (tools/drawgen/specs.py, plain data): every
    number it registers and the numbers a registered tabulated sheet covers. Empty when there is no registry."""
    import importlib.util
    path = os.path.join(root, "tools", "drawgen", "specs.py")
    if not os.path.exists(path):
        return set()
    spec = importlib.util.spec_from_file_location("drawgen_specs_c05", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = set()
    for pn, (_team, kind, conf) in getattr(mod, "SPECS", {}).items():
        out.add(pn)
        if kind == "tabulated":
            out.update((conf or {}).get("covers", []))
    return out


def missing_drawing_severity(root, pn=None, drawgen=None):
    """The severity of a missing drawing for a part we make, from config/policy.csv: severe or major, or
    auto-screen-lock (D-84): major while the screen is locked, severe otherwise or when it can't tell. A part
    tools/drawgen draws (drawgen: drawgen_parts) stays severe on a locked screen: drawgen doesn't wait for it (D-113)."""
    v = policy(root, "missing_drawing_severity", "severe")
    if v == "auto-screen-lock":
        if pn is not None and pn in (drawgen if drawgen is not None else drawgen_parts(root)):
            return "severe"
        return "major" if screen_locked() else "severe"
    return v


# ----------------------------------------------------------------- who made it (the owner's rule, 2026-11-01)
# A drawing's Created by field and its PDF author read "Autonomous"; any other name is flagged, and so is any
# person's name anywhere in a drawing PDF or its metadata. The names looked for come at run time from the repo's
# own git history (authors, committers, their e-mail names), git's user.name, this machine's user and the optional
# SPACESHIP_PERSON_NAMES list, so no name is written into the repo; a hit is shown masked.

AUTHOR = "Autonomous"
# the title blocks' created-by labels: Fusion's 'Created by', drawgen's 'MADE BY', ELECTRICAL's 'DATE / BY'
BY_LABELS = (("created", "by"), ("made", "by"), ("drawn", "by"), ("designed", "by"), ("date", "/", "by"),
             ("author",))
# words that start the next cell on a title block's line
CELL_WORDS = {"approved", "checked", "tolerances", "tolerance", "document", "title", "rev", "rev.", "date", "sheet",
              "scale", "size", "units", "mass", "projection", "material", "finish", "status", "project", "part",
              "drawing", "dwg", "source", "technical", "reference"}
DATE = re.compile(r"\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
HOME = re.compile(r"(?:/Users/|/home/|[A-Za-z]:\\Users\\)([^/\\\s]+)")
NOT_PEOPLE = re.compile(r"github|claude|\[bot\]|noreply|autonomous|harness|anthropic|openai|codex", re.I)


def person_names(repo=None):
    """The person names to look for (see above), from sources outside the repo's files."""
    from common import REPO_ROOT
    names = set()
    try:
        out = subprocess.run(["git", "-C", repo or REPO_ROOT, "log", "--format=%an%n%cn%n%ae%n%ce"],
                             capture_output=True, text=True, timeout=60).stdout
        out += "\n" + subprocess.run(["git", "-C", repo or REPO_ROOT, "config", "user.name"],
                                     capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        out = ""
    out += "\n" + "\n".join(x.strip() for x in os.environ.get("SPACESHIP_PERSON_NAMES", "").split(","))
    try:
        import pwd
        gecos = (pwd.getpwuid(os.getuid()).pw_gecos or "").split(",")[0].strip()
        if " " in gecos:                    # a full name in the account record, not a bare login
            out += "\n" + gecos
    except (ImportError, KeyError):
        pass
    for line in out.splitlines():
        line = line.strip()
        if not line or NOT_PEOPLE.search(line):
            continue
        if "@" in line:                     # an e-mail: the words of its name part ('jane.roe' gives Jane, Roe)
            names |= {w for w in re.split(r"[._+\-\d]+", line.split("@")[0]) if len(w) >= 3 and w.isalpha()}
        elif len(re.sub(r"\W", "", line)) >= 3:
            names.add(line)
            names |= {w for w in line.split() if len(w) >= 3 and w.isalpha()}
    return sorted(n for n in names if not NOT_PEOPLE.search(n))


def mask(name):
    return " ".join(w[0] + "*" * (len(w) - 1) for w in name.split())


def _rows(words):
    """Words in rows by their height on the sheet (PyMuPDF's own lines split a title block's cells)."""
    rows = []
    for w in sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0])):
        yc, h = (w[1] + w[3]) / 2, w[3] - w[1]
        if rows and abs(yc - rows[-1][0]) < 0.5 * max(1.0, min(h, rows[-1][1])):
            rows[-1][2].append(w)
        else:
            rows.append([yc, h, [w]])
    return [(yc, h, sorted(ws, key=lambda w: w[0])) for yc, h, ws in rows]


def _by_values(page):
    """[(label, value)] for each created-by field on a page: the words right of the label on its row up to the next
    cell, else the first row of words under it in its cell; dates are left out."""
    words = page.get_text("words")
    out = []
    for yc, h, ws in _rows(words):
        toks = [w[4].strip(":").lower() for w in ws]
        for i in range(len(toks)):
            lab = next((l for l in BY_LABELS if tuple(toks[i:i + len(l)]) == l), None)
            if lab is None:
                continue
            if i > 0 and ws[i][0] - ws[i - 1][2] < 0.8 * h:
                continue        # inside a sentence ('... .md. Made by tools/drawgen ...'): a note, not a field
            j = i + len(lab)
            k = next((m for m in range(j, len(toks)) if toks[m] in CELL_WORDS or
                      any(tuple(toks[m:m + len(l)]) == l for l in BY_LABELS)), len(toks))
            same = ws[j:k]
            raw = [w[4] for w in ws[i:j]]
            if same and not all(t.isupper() or not t.isalpha() for t in raw) and not raw[-1].endswith(":"):
                continue        # 'Made by the BASE Engineer (AI agent), ...' runs on as a sentence of the notes:
                                # a field label is upper case ('MADE BY', 'DATE / BY'), ends in a colon, or stands
                                # alone on its row with its value under it (Fusion's 'Created by')
            x0 = ws[i][0]
            x_end = ws[k][0] if k < len(ws) else x0 + 200.0
            if same:
                val = " ".join(w[4] for w in same)
            else:
                below = [(ryc, rws) for ryc, _rh, rws in _rows([w for w in words if x0 - 1 <= w[0] < x_end])
                         if yc + 0.6 * h < ryc <= yc + 3.0 * h]
                val = " ".join(w[4] for w in below[0][1]) if below else ""
            val = DATE.sub(" ", val)
            if lab == ("date", "/", "by") and "/" in val:
                val = val.rsplit("/", 1)[1]
            val = re.sub(r"^[\s/|:\-]+|[\s/|:\-]+$", "", re.sub(r"\s+", " ", val))
            out.append((" ".join(lab).upper(), val))
    return out


# the Lead's ruling (2026-11-01): notes carry no maker line either; a note may name the source (which STEP and its
# revision), never an agent, a role or a script as the maker
NOTE_VERBS = ("made", "created", "drawn", "designed", "generated", "produced", "prepared")
MAKER_END = re.compile(r"\s*(?:[,;]|\.(?:\s|$)|\s(?:from|using|with|for|on|at|in)\s)", re.I)


def _note_makers(page):
    """[(phrase, maker)] for each maker line in a page's text that isn't a title block field: 'Made by X',
    'Generated by X' and the like, running on as a sentence; the maker is the words after 'by' up to a comma, a full
    stop or 'from ...'."""
    out = []
    for yc, h, ws in _rows(page.get_text("words")):
        toks = [w[4].strip(":").lower() for w in ws]
        for i in range(len(toks) - 1):
            if toks[i] not in NOTE_VERBS or toks[i + 1] != "by":
                continue
            raw = [w[4] for w in ws[i:i + 2]]
            k = next((m for m in range(i + 2, len(toks)) if toks[m] in CELL_WORDS or
                      any(tuple(toks[m:m + len(l)]) == l for l in BY_LABELS)), len(toks))
            same = ws[i + 2:k]
            starts_cell = i == 0 or ws[i][0] - ws[i - 1][2] >= 0.8 * h
            if starts_cell and (toks[i], "by") in BY_LABELS and (
                    not same or all(t.isupper() or not t.isalpha() for t in raw) or raw[-1].endswith(":")):
                continue        # the title block's own field: _by_values reads it
            maker = MAKER_END.split(" ".join(w[4] for w in ws[i + 2:]), 1)[0].strip(" :")
            if maker:
                out.append((" ".join(raw), maker))
    return out


def drawing_people(pdf, names):
    """(author problems, person hits) for one drawing PDF: what its created-by fields and metadata author read when
    not 'Autonomous', and every person's name, e-mail address or home folder in its text, notes or metadata."""
    import fitz  # PyMuPDF
    probs, hits = [], set()
    with fitz.open(pdf) as doc:
        meta = doc.metadata or {}
        xmp = doc.get_xml_metadata() or ""
        texts = [str(v) for v in meta.values() if v] + [re.sub(r"<[^>]+>", " ", xmp)]
        seen_by, makers = [], []
        for n, page in enumerate(doc, start=1):
            texts.append(page.get_text())
            for a in page.annots() or []:
                texts += [str(v) for v in (a.info or {}).values() if v]
            for lab, val in _by_values(page):
                seen_by.append((n, lab, val))
            for phrase, maker in _note_makers(page):
                if maker.strip().lower() != AUTHOR.lower():
                    makers.append((n, phrase, maker))
        if not seen_by:
            probs.append("no Created by field in its title block")
        for v in sorted({val for _n, _l, val in seen_by if val.strip().lower() != AUTHOR.lower()}):
            pages = sorted({n for n, _l, val in seen_by if val == v})
            labs = sorted({l for _n, l, val in seen_by if val == v})
            probs.append("its %s field reads %s (sheet %s)" % ("/".join(labs), "'%s'" % v if v else "nothing",
                                                              ", ".join(map(str, pages))))
        for phrase, maker in sorted({(p, m) for _n, p, m in makers}):
            pages = sorted({n for n, p, m in makers if (p, m) == (phrase, maker)})
            probs.append("a note names '%s' as its maker ('%s ...', sheet %s)" % (maker, phrase, ", ".join(map(str, pages))))
        author = (meta.get("author") or "").strip()
        if author.lower() != AUTHOR.lower():
            probs.append("its PDF author reads %s" % ("'%s'" % author if author else "nothing"))
        m = re.search(r"<dc:creator>(.*?)</dc:creator>", xmp, re.S)
        if m:
            xc = re.sub(r"<[^>]+>|\s+", " ", m.group(1)).strip()
            if xc.lower() != AUTHOR.lower():
                probs.append("its XMP creator reads '%s'" % xc)
    blob = "\n".join(texts)
    covered = set()
    for name in sorted(names, key=len, reverse=True):       # a full name once, not again word by word
        if name.lower() in covered:
            continue
        if re.search(r"(?<![\w])%s(?![\w])" % re.escape(name), blob, re.I):
            hits.add("a person's name (%s)" % mask(name))
            covered |= {w.lower() for w in name.split()}
    for e in EMAIL.findall(blob):
        hits.add("an e-mail address (%s@...)" % mask(e.split("@")[0]))
    for u in HOME.findall(blob):
        hits.add("a home folder path (/Users/%s/...)" % mask(u))
    return probs, sorted(hits)


def check_drawing_people(root, names=None):
    """C05 drawing-author (major) for every drawing PDF under v2/02-Drawings, and person-name (severe) for every PDF
    there, proof sheets included."""
    try:
        import fitz  # noqa: F401
    except ImportError:
        return [], False
    names = person_names() if names is None else names
    fs = []
    # every PDF for a person's name, the pipeline's proof drawings too (the repo is public); the Created by rule for
    # the drawings themselves (proof/ holds the pipeline's test sheets, left out of the part checks too)
    for p in walk_files(root, "v2/02-Drawings", exts=(".pdf",), skip=("/.raw/", "/__pycache__/")):
        r = rel(root, p)
        try:
            probs, hits = drawing_people(p, names)
        except Exception:                       # a PDF that won't open is the drawing checks' business
            continue
        if "/proof/" in "/" + r:
            probs = []
        gen = made_by_generator(p)
        owner = GENERATOR_OWNER if gen else owner_for(r, (parse_file_name(r) or {}).get("pn", ""))
        subj = os.path.splitext(os.path.basename(r))[0]
        if hits:
            fs.append(Finding("C05", "person-name", subj, "severe",
                              "%s carries %s in its text or metadata; the repo is public and drawings carry no "
                              "person's name (the owner's rule, 2026-11-01)." % (os.path.basename(r), ", ".join(hits)),
                              "Take it out of the drawing and its PDF metadata, and export again." +
                              (GENERATOR_FIX if gen else ""), r, owner, {"model": "pdf-people"}))
        if probs:
            fs.append(Finding("C05", "drawing-author", subj, "major",
                              "%s: %s; the owner's rule (2026-11-01) is that a drawing's Created by field and its PDF "
                              "author read '%s', and the notes name no other maker (the Lead's ruling)." % (
                                  os.path.basename(r), "; ".join(probs), AUTHOR),
                              "Set the title block's Created by (or Made by) field and the PDF's author to '%s', drop "
                              "any maker line from the notes (a note may name the source: which STEP and its revision; "
                              "never an agent, a role or a script as the maker), and export again." % AUTHOR +
                              (GENERATOR_FIX if gen else ""), r, owner,
                              {"model": "pdf-people"}))
    return fs, True


def check_drawings(root, part_numbers, holes_by_pn, names=None, faces_by_pn=None, src_by_pn=None, flat_by_pn=None,
                   bends_by_pn=None, two_wall_by_pn=None, cuboid_by_pn=None, prism_by_pn=None):
    """part_numbers: the made parts and assemblies to check (from the parts
    lists and the STEP products). holes_by_pn: pn -> list of holes.
    faces_by_pn: pn -> face count of each of its bodies (a plain rectangle has 6).
    src_by_pn: pn -> the STEP or parts list it comes from, for the owner of a part without files of its own."""
    names = names or {}
    faces_by_pn = faces_by_pn or {}
    src_by_pn = src_by_pn or {}
    flat_by_pn = flat_by_pn or {}      # pn -> (ok, thickness, why) from the STEP (D-89 part 4)
    bends_by_pn = bends_by_pn or {}    # pn -> most bends in one of its bodies (D-113)
    two_wall_by_pn = two_wall_by_pn or {}   # pn -> hole axes through two walls of one body (D-113)
    cuboid_by_pn = cuboid_by_pn or {}  # pn -> sides of its one shape when that is a plain rectangular block (D-125)
    prism_by_pn = prism_by_pn or {}    # pn -> (its one shape cut straight through from sheet, or None, why) (D-128)
    fs = []
    idx = index_files(root)
    drawgen = drawgen_parts(root) if policy(root, "missing_drawing_severity", "severe") == "auto-screen-lock" else set()
    hidden_allow = hidden_lines_allowed(root)            # drawings that keep hidden lines on purpose
    def missing_for(pn):                                 # PM rulings D-73, D-84, D-97 (config/policy.csv), D-113
        return missing_drawing_severity(root, pn, drawgen)
    tab = tabulated_cover(idx)                            # D-89
    from common import reserved_spaces
    reserved = reserved_spaces(root)
    for pn in sorted(part_numbers):
        cls = pn_class(pn)
        if cls not in ("part", "assembly"):
            continue
        files = idx.get(pn, {})
        dwgs = files.get("DWG", [])
        pdfs = [(rv, p) for rv, p in dwgs if p.lower().endswith(".pdf")]
        where = (files.get("STEP") or files.get("CAD") or [("", "")])[0][1]
        r_where = rel(root, where) if where else ""
        owner = owner_for(r_where or src_by_pn.get(pn, ""), pn)
        if pn[:2] in ("83", "84"):        # shared hardware: its drawing is the joints register's, wherever it's modelled
            owner = owner_for("", pn)
        label = ("%s %s" % (pn, names.get(pn, ""))).strip()
        if pn in reserved:                          # a reserved space: open under its designer, no drawing yet
            rr = reserved[pn]
            fs.append(Finding("C05", "reserved-space", pn, "major",
                              "%s is a reserved space until %s designs it (%s): %s." % (
                                  label, rr.get("owner") or "its designer", rr.get("ruling") or "", rr.get("why") or ""),
                              "Design the part, then take it off v2/04-Checks/config/reserved-spaces.csv; its drawing "
                              "and seams are checked from then on.", r_where, rr.get("owner") or owner))
            continue
        if not pdfs and pn in tab:                 # D-89: listed in a tabulated drawing, so drawn
            cad_revs = {rv for rv, _p in files.get("CAD", []) + files.get("STEP", [])}
            tab_revs = {rv for rv, _p, _own in tab[pn]}
            if cad_revs and not (tab_revs & cad_revs):
                rv, tp, own = sorted(tab[pn])[-1]
                gen = made_by_generator(tp)
                fs.append(Finding("C05", "rev-mismatch", pn, "major",
                                  "%s: its tabulated drawing %s is revision %s but its CAD/STEP is revision %s." % (
                                      label, os.path.basename(tp), "/".join(sorted(tab_revs)),
                                      "/".join(sorted(cad_revs))),
                                  "Export the drawing, CAD and STEP from the same revision (guideline section 4.2)." +
                                  (GENERATOR_FIX if gen else ""),
                                  rel(root, tp), GENERATOR_OWNER if gen else owner))
            continue
        kind = soft_kind(names.get(pn, ""))
        if not pdfs and kind == "soft" and files.get("DXF"):
            continue        # D-89 (3): a DXF gives the outline of a foam, gasket, seal or tape, any shape
        if not pdfs and kind:
            # D-89 (2) felt or fill, (3) other soft goods: a plain knife-cut rectangle or strip needs no drawing
            # when its cut-list or parts-list row gives size (thickness too, for (3)), material, tolerance and
            # part number; a piece with pockets, notches or holes keeps its drawing (or, for (3), a DXF)
            row = cut_list_lacks(root, pn, thickness=(kind == "soft"))
            n_holes = len(hole_axes(holes_by_pn.get(pn, [])))
            n_faces = max(faces_by_pn.get(pn) or [0])
            if row is not None and not row[0] and not row[2] and not n_holes and n_faces <= 6:
                continue
            d128 = ""
            if kind == "felt or fill" and files.get("DXF"):
                # D-128: with through-openings or edge notches only, its DXF and a full row stand in for a drawing
                lacks128 = felt_dxf_lacks(root, pn, prism_by_pn.get(pn), sorted(files["DXF"])[-1][1])
                if not lacks128:
                    continue
                d128 = " D-128 (a felt or fill piece on its DXF and parts-list row) doesn't apply: it needs %s." % (
                    "; ".join(lacks128))
            why = []
            if row is not None and row[2]:
                why.append("its row names %s, so it isn't a plain rectangle" % " and ".join(row[2]))
            elif n_holes:
                why.append("it isn't a plain rectangle (its STEP has %d hole axes)" % n_holes)
            elif n_faces > 6:
                why.append("it isn't a plain rectangle (a body in its STEP has %d faces, a block has 6: pockets "
                           "or notches)" % n_faces)
            if row is None:
                why.append("no cut list or parts list has a row for it")
            elif row[0]:
                why.append("its row in %s doesn't give %s" % (row[1], ", ".join(row[0])))
            need = ("a drawing" if kind == "felt or fill" else "a DXF of its outline or a drawing")
            fs.append(Finding("C05", "no-drawing", pn, "major",
                              "%s has no drawing, and D-89's cut-list route doesn't apply: %s.%s" % (
                                  label, "; ".join(why), d128),
                              "For a plain knife-cut rectangle or strip, give part number, size%s, material and "
                              "tolerance in its parts-list or cut-list row (D-89)%s; otherwise make %s." % (
                                  ", thickness" if kind == "soft" else "",
                                  "; for a felt or fill piece with through-openings or edge notches, its DXF with the "
                                  "full outline and every opening and a row with material, density or grade, "
                                  "thickness and tolerance (D-128)" if kind == "felt or fill" else "", need),
                              r_where, owner))
            continue
        d125 = ""
        sides = cuboid_by_pn.get(pn)
        if not pdfs and cls == "part" and not kind and is_strip(sides):
            row = strip_row_lacks(root, pn, sides)
            if row is not None and not row[0]:
                continue        # D-125: a plain straight-cut strip or sheet, given in full by its parts-list row
            d125 = " D-125 (a plain straight-cut strip or sheet on a full parts-list row) doesn't apply: %s." % (
                "no parts list has a row for it" if row is None else
                "its row in %s doesn't give %s" % (row[1], ", ".join(row[0])))
        if not pdfs and cls == "part" and files.get("DXF"):
            # D-89 part 4: a flat sheet part goes on its DXF and its parts-list row
            lacks = flat_cut_lacks(root, pn, files, holes_by_pn.get(pn), flat_by_pn.get(pn))
            if not lacks:
                continue
            fs.append(Finding("C05", "no-drawing", pn, missing_for(pn),
                              "%s has no drawing, and D-89 part 4 (flat sheet part on its DXF) doesn't apply: %s.%s" % (
                                  label, "; ".join(lacks), d125),
                              "Make its drawing; or, for a flat part cut from sheet with no bends and no machined "
                              "features, give the full outline and every hole in its DXF and material, thickness, "
                              "finish, ISO 2768-m and any critical hole note in its parts-list row (D-89 part 4).",
                              r_where, owner))
            continue
        if not pdfs:
            fs.append(Finding("C05", "no-drawing", pn, missing_for(pn) if cls == "part" else "major",
                              "%s has no drawing PDF (%s_REV_NAME_DWG.pdf under v2/02-Drawings)%s.%s" % (
                                  label, pn, " though its CAD is in %s" % r_where if r_where else "", d125),
                              "Make the ISO first-angle drawing, export it through the name strip, and commit it.",
                              r_where, owner))
            continue
        revs = {rv for rv, _p in pdfs}
        cad_revs = {rv for rv, _p in files.get("CAD", []) + files.get("STEP", [])}
        rv, pdf = sorted(pdfs)[-1]
        rp = rel(root, pdf)
        gen = made_by_generator(pdf)
        if gen:                                     # D-112: the generator's group fixes its own drawings
            owner, gen_fix = GENERATOR_OWNER, GENERATOR_FIX
        else:
            gen_fix = ""
        if gen and bends_by_pn.get(pn):
            fs.append(Finding("C05", "generated-bent-part", pn, "major",
                              "%s has %d bends in its STEP, but its drawing %s was made by tools/drawgen; D-113 keeps "
                              "bent parts, brackets included, in Fusion." % (label, bends_by_pn[pn], os.path.basename(rp)),
                              "Leave this part to Fusion: take it off the generator's list and delete the generated "
                              "drawing once Fusion's is in (D-113).", rp, owner))
        if cad_revs and not (revs & cad_revs):
            fs.append(Finding("C05", "rev-mismatch", pn, "major",
                              "%s: drawing revision %s but CAD/STEP revision %s." % (
                                  label, "/".join(sorted(revs)), "/".join(sorted(cad_revs))),
                              "Export the drawing, CAD and STEP from the same revision (guideline section 4.2)." + gen_fix,
                              rp, owner))
        # the PM's drawing traps, read back from what reached the paper: every drawing, the wiring diagram too
        for rule, sev, msg, fix in drawing_traps(pdf, hidden_allow.get(os.path.basename(pdf), 0)):
            fs.append(Finding("C05", rule, pn, sev, "%s drawing %s: %s" % (label, os.path.basename(rp), msg),
                              fix + gen_fix, rp, owner))
        if "WIRING-DIAGRAM" in os.path.basename(pdf).upper():
            continue        # D-93: ELECTRICAL's wiring diagram draws 710000 (routes and joints on sheet 3); a schematic
        text = pdf_text(pdf)
        if text is None:
            continue
        up = text.upper()
        lacks = []
        if not re.search(r"\bUNITS?\s*[:=]?\s*MM\b", up):
            lacks.append("units (mm)")
        if cls == "part":
            if not re.search(r"MATERIAL", up) or re.search(r"MATERIAL\s*:?\s*(SEE PARTS LIST)?\s*$", up, re.M) and \
                    not re.search(r"EN AW|\d{4}|DX51|A2|A4|STEEL|ALUMIN|ACP|PET", up):
                lacks.append("material")
            if not re.search(r"FINISH|ANODI|POWDER|ZINC|GALV|PAINT|MILL FINISH", up):
                lacks.append("finish")
        if not re.search(r"ISO\s*2768|ISO\s*22081|GENERAL TOLERANCE|TOLERANCE|±|\+/-", up):
            lacks.append("tolerances (a general rule or values on the dimensions)")
        if gen and two_wall_by_pn.get(pn) and not SECTION_LABEL.search(up):
            fs.append(Finding("C05", "no-section", pn, "major",
                              "%s has %d hole axes through two walls in its STEP, but its generated drawing %s has no "
                              "section label (SECTION A-A, or A-A) and no opposite view label (VIEW B, VIEW FROM)." % (
                                  label, two_wall_by_pn[pn], os.path.basename(rp)),
                              "Draw a section through those holes, hatched per ISO 128-50, or the opposite view, and "
                              "label it (D-113)." + gen_fix, rp, owner))
        if lacks:
            fs.append(Finding("C05", "drawing-content", pn, "major",
                              "%s drawing %s doesn't state: %s." % (label, os.path.basename(rp), ", ".join(lacks)),
                              "Add them to the title block or the notes (guideline sections 3.1, 6.3, 9)." + gen_fix,
                              rp, owner))
        n_axes = len(hole_axes(holes_by_pn.get(pn, [])))
        if cls == "part" and n_axes:
            tags = set(re.findall(r"\bH\d{2}\b", up))
            table = bool(re.search(r"X\s*\(MM\)", up) and re.search(r"Y\s*\(MM\)", up))
            dia = len(re.findall(r"[Ø⌀]\s*\d", text))
            if not tags and not table and not dia:
                fs.append(Finding("C05", "holes-not-dimensioned", pn, "severe",
                                  "%s has %d hole axes in its STEP, but drawing %s has no hole tags, no hole table "
                                  "and no diameter callouts." % (label, n_axes, os.path.basename(rp)),
                                  "Tag every hole (H01...), dimension it to its centre from the datums or put it in "
                                  "a hole table with X (mm) and Y (mm) (guideline section 6.2)." + gen_fix, rp, owner))
            elif tags and len(tags) < n_axes and not table:
                fs.append(Finding("C05", "holes-untagged", pn, "major",
                                  "%s has %d hole axes in its STEP but %d hole tags on drawing %s and no hole "
                                  "table." % (label, n_axes, len(tags), os.path.basename(rp)),
                                  "Tag the rest, or show they share a tag through a pattern note." + gen_fix, rp,
                                  owner))
    return fs
