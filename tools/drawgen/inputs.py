"""What a drawing reads besides the STEP: the team parts list row (name, material, finish, revision, process,
tolerance, mass, cut list), the feature rationale register (why each hole is there, what fits it), and the
file names (conventions section 7). Read only; never edits a source.
"""

import csv
import glob
import hashlib
import os
import re

from geom import REPO

MANUF = os.path.join(REPO, "v2", "03-Manufacturing")
DRAWINGS = os.path.join(REPO, "v2", "02-Drawings")
NAME_RE = re.compile(r"^(\d{6})_([PR]\d{2})_([A-Z0-9-]+)_([A-Z]+)\.([a-z0-9]+)$")


def rel(p):
    return os.path.relpath(p, REPO)


def sha12(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


KEYS_CSV = os.path.join(REPO, "v2", "01-CAD-Native", "joints", "corner-keys.csv")


def key_rows(pn):
    """Joints' corner and inline keys fitted in this part's ends (corner-keys.csv, the key sheet 111211's
    positions): one row per key, in pod coordinates."""
    if not os.path.exists(KEYS_CSV):
        return []
    with open(KEYS_CSV, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if pn in (r.get("carrier_key_in_its_end") or "")]


def own_step(pn):
    """The part's own STEP file (PN_REV_NAME_STEP.step) under v2/03-Manufacturing, newest revision."""
    hits = []
    for p in glob.glob(os.path.join(MANUF, "**", "%s_*_STEP.step" % pn), recursive=True):
        m = NAME_RE.match(os.path.basename(p))
        if m and m.group(1) == pn and "/proof/" not in p:
            hits.append((m.group(2), p))
    return sorted(hits)[-1][1] if hits else None


def parse_name(path):
    m = NAME_RE.match(os.path.basename(path))
    if not m:
        return None
    return {"pn": m.group(1), "rev": m.group(2), "name": m.group(3), "doc": m.group(4)}


def ascii_name(name):
    """'WALL - PANEL FRAME - SIDE LOWER - LH' -> 'WALL-PANEL-FRAME-SIDE-LOWER-LH' (conventions 7)."""
    s = name.upper().replace("Ø", "D").replace("×", "X")
    s = re.sub(r"[^A-Z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def team_lists(team):
    return sorted(glob.glob(os.path.join(MANUF, team, "*.csv")))


def parts_row(pn, team):
    """The richest parts-list row for pn in the team's lists, with the level-2 rows under it (the cut list),
    and the file it came from."""
    best = None
    for p in team_lists(team):
        with open(p, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for i, r in enumerate(rows):
            if (r.get("part_number") or "").strip() != pn:
                continue
            subs = []
            lvl = (r.get("level") or "").strip()
            for r2 in rows[i + 1:]:
                l2 = (r2.get("level") or "").strip()
                if (r2.get("part_number") or "").strip() or not l2 or (lvl and l2 <= lvl):
                    break
                subs.append(r2)
            filled = sum(1 for v in r.values() if (v or "").strip())
            if best is None or filled > best[0]:
                best = (filled, r, subs, p)
    if best is None:
        return None, [], None
    return best[1], best[2], best[3]


def cut_list_rows(team, cfg, pn):
    """A welded frame's cut list from the team CSV its entry names (D-162), as the parts list's level-2 cut rows read,
    and that file: its rows whose frame is pn, one per member number (D-120: one number is one member; a number with
    two lengths, two ends texts or two pairs of end angles is refused), the quantity their sum, the name the member's
    number and its parts-list name (names exactly as the parts lists: FRONT's cut lists name each tube's place, so a
    part used in four rings would print one ring's; the cut list's own name only for a member with no parts-list
    row). The columns CEILING, WALL and FRONT share: member_part, name, section, length_mm, qty, ends (holes when
    present). With FRONT's end_a_deg and end_b_deg, the end angles the model check uses come from them (see
    column_angles), and an ends text that gives both angles must agree with them. Welded-in made parts the entry names
    (a frame's mitre plates) follow, from their parts-list rows, as having their own drawing."""
    path = os.path.join(MANUF, team, cfg["file"])
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("frame") or "").strip() == pn]
    base = os.path.basename(path)
    out, by = [], {}
    for r in rows:
        num = (r.get("member_part") or "").strip()
        if not num:
            raise ValueError("cut list %s: a row of %s has no member number" % (base, pn))
        length, ends = (r.get("length_mm") or "").strip(), (r.get("ends") or "").strip()
        angles = column_angles(r.get("end_a_deg"), r.get("end_b_deg"))
        if angles is False:
            raise ValueError("cut list %s: member %s's end angle columns '%s' and '%s' don't give a number each" % (
                base, num, (r.get("end_a_deg") or "").strip(), (r.get("end_b_deg") or "").strip()))
        said = ends_angles(ends)
        if angles and said is not None and any(abs(a - b) > 1e-6 for a, b in zip(said, angles)):
            raise ValueError("cut list %s: member %s's ends text gives %s, its end angle columns %s" % (
                base, num, ", ".join("%g°" % a for a in said), ", ".join("%g°" % a for a in angles)))
        q = float((r.get("qty") or "1").strip() or 1)
        if num in by:
            o = by[num]
            if (o["cut_length_mm"], o["note"], o.get("angles")) != (length, ends, angles):
                raise ValueError("cut list %s: member %s has two lengths or two ends texts or two pairs of end "
                                 "angles (D-120)" % (base, num))
            o["_q"] += q
            continue
        listed = (parts_row(num, team)[0] or {}).get("name", "").strip()
        o = {"kind": "cut", "member_part": num, "name": "%s %s" % (num, listed or (r.get("name") or "").strip()),
             "size_mm": (r.get("section") or "").strip(), "material": (r.get("section") or "").strip(),
             "cut_length_mm": length, "tolerance": cfg.get("tolerance", ""), "note": ends,
             "holes": (r.get("holes") or "").strip(), "_q": q}
        if angles:
            o["angles"] = angles
        by[num] = o
        out.append(o)
    if not out:
        raise ValueError("cut list %s has no row for %s" % (os.path.basename(path), pn))
    for wpn in cfg.get("welded_in", ()):
        row = parts_row(wpn, team)[0]
        if not row:
            raise ValueError("welded-in part %s has no parts-list row" % wpn)
        q = (row.get("qty_per_parent") or row.get("qty") or "").strip()
        out.append({"kind": "cut", "member_part": wpn, "name": "%s %s" % (wpn, (row.get("name") or "").strip()),
                    "size_mm": (row.get("material") or "").strip(), "material": (row.get("material") or "").strip(),
                    "cut_length_mm": "-", "tolerance": "",
                    "note": "welded in; no drawing of its own, its parts-list row defines it (D-125)",
                    "_q": float(q or 0)})
    for o in out:
        q = o.pop("_q")
        o["qty"] = ("%d" % q) if q == int(q) else ("%g" % q)
    return out, path


ANGLE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:°|deg\b)")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def column_angles(a, b):
    """A cut list row's two end angles from square, sorted, from its end_a_deg and end_b_deg columns (FRONT's): each
    cell's steepest cut, as the model check measures each end ('50.9 and 0.0 (two cuts)' is 50.9; that end's other
    cut is on the tube's own sheet). None when the file has neither column or both cells are blank; False when only
    one gives a number."""
    if a is None and b is None:
        return None
    cells = [(c or "").strip() for c in (a, b)]
    if not any(cells):
        return None
    got = [[float(x) for x in NUMBER.findall(c)] for c in cells]
    if not all(got):
        return False
    return sorted(max(g) for g in got)


def ends_cell(note, tol=""):
    """A cut list row's ends as the sheet prints them: the text as written, shortened to 'square-cut ends' only when
    it says square and gives no angle (agreed with the generator's owner: 'mitred 63.43 deg off square' keeps its
    angle)."""
    words = (note or "") + " " + (tol or "")
    square = "square" in words.lower() and not ANGLE.search(words)
    return ("%s; %s" % ("square-cut ends" if square else (note or ""), (tol or "").split(",")[0])).strip("; ")


def ends_angles(text):
    """The two end cuts' angles from square a cut list's ends text gives, sorted, or None when it gives none it can
    be read for: 'square ...' with no angle is 0 and 0; one angle with 'both' is that angle twice; two angles are
    those."""
    t = text or ""
    found = [float(x) for x in ANGLE.findall(t)]
    if not found:
        return [0.0, 0.0] if "square" in t.lower() else None
    if len(found) == 1:
        return [found[0], found[0]] if re.search(r"\bboth\b", t, re.I) else None
    if len(found) == 2:
        return sorted(found)
    return None


# ------------------------------------------------------------------ feature rationale

FR_ROW = re.compile(r"^\|\s*(F\d+[A-Z]?)\s*\|\s*(\d{6})\s+([^|]*?)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
                    r"\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|")
HOLES_CELL = re.compile(r"Ø\s*([\d.]+)\s+along\s+([xyz])\s*,\s*\d+\s*:\s*(.*)$", re.I)
PAIR = re.compile(r"\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)")


def feature_rows(pn, team):
    """Hole rows of the feature rationale registers that name pn: [{id, body, dia, axis, centres, function,
    mating, tolerance, status, file}]. Centres are the two pod coordinates across the axis."""
    out = []
    for p in sorted(glob.glob(os.path.join(DRAWINGS, team, "FEATURE-RATIONALE*.md"))):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                m = FR_ROW.match(line)
                if not m or m.group(2) != pn:
                    continue
                hc = HOLES_CELL.search(m.group(4).strip())
                if not hc:
                    continue
                out.append({"id": m.group(1), "body": m.group(3).strip(), "dia": float(hc.group(1)),
                            "axis": hc.group(2).upper(),
                            "centres": [(float(a), float(b)) for a, b in PAIR.findall(hc.group(3))],
                            "function": m.group(5).strip(), "mating": m.group(6).strip(),
                            "rule": m.group(7).strip(), "tolerance": m.group(10).strip(),
                            "status": m.group(12).strip(), "file": rel(p)})
    return out


def match_feature(rows, body_name, dia, axis_letter, centre3):
    """The register row for a hole: same body, Ø within 0.01, same axis, a listed centre within 0.05."""
    idx = {"X": (1, 2), "Y": (0, 2), "Z": (0, 1)}[axis_letter]
    c = (centre3[idx[0]], centre3[idx[1]])
    for r in rows:
        if r["axis"] != axis_letter or abs(r["dia"] - dia) > 0.011:
            continue
        if body_name and r["body"] and r["body"].upper() != body_name.upper():
            continue
        if any(abs(a - c[0]) < 0.051 and abs(b - c[1]) < 0.051 for a, b in r["centres"]):
            return r
    return None


def short_function(fn):
    """The register's function cell up to its first ':' or ';' (the clause that names the feature), whole: the
    table wraps it, never cuts it."""
    return re.split(r"[:;]", fn)[0].strip()


def part_numbers_in(text):
    return re.findall(r"(?<!\d)(\d{6})(?!\d)", text or "")


# The other register layouts (BASE's: | ID | Feature | Function | Size, position | ...; CEILING's: | Feature ID |
# Feature | Size, offset, pitch | Function | ...): the header row names the columns, read per table.
ROW = re.compile(r"^\|(.*)\|\s*$")
FID = re.compile(r"^F[A-Z0-9]{0,6}-[A-Z0-9-]*\d[A-Z]?$")
DIA = re.compile(r"Ø\s*([\d.]+)")
DIA_WALL = re.compile(r"Ø\s*([\d.]+)[^Ø;]*?\b(top|bottom|inner|outer)\s+wall", re.I)
NUM = re.compile(r"[-−+]?\d+(?:\.\d+)?")


def feature_rows_b(team, pn=None, sizeless=False):
    """Rows of the other register layouts that name a hole size: [{id, title, dias, walls, numbers, function,
    status, file, keyhole}]; with sizeless, the rows that name none too (an open-ended slot's)."""
    out = []
    for p in sorted(glob.glob(os.path.join(DRAWINGS, team, "FEATURE-RATIONALE*.md"))):
        section, cols = "", None
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    section, cols = line, None
                    continue
                m = ROW.match(line.rstrip("\n"))
                if not m:
                    cols = None if not line.strip() else cols
                    continue
                cells = [c.strip() for c in m.group(1).split("|")]
                low = [c.lower() for c in cells]
                if low and low[0] in ("id", "feature id"):
                    cols = low
                    continue
                if cols is None or not cells or not FID.match(cells[0]):
                    continue
                named = re.findall(r"(?<!\d)\d{6}(?!\d)", section)
                if pn and named and pn not in named:
                    continue        # a section about other parts
                def get(key):
                    """The cell of the column named key (exactly, else the first that starts with it)."""
                    for exact in (True, False):
                        for i, c in enumerate(cols):
                            if i < len(cells) and (c == key if exact else c.startswith(key)):
                                return cells[i]
                    return ""
                title, fn, size = get("feature"), get("function"), get("size")
                both = title + " " + size
                dias = [float(d.rstrip(".")) for d in DIA.findall(both)]
                if not dias and not sizeless:
                    continue
                walls = {float(d.rstrip(".")): w.lower() for d, w in DIA_WALL.findall(both)}
                wall_any = next((w for w in ("top", "bottom", "inner", "outer") if w + " wall" in both.lower()), None)
                nums = [float(n.replace("−", "-")) for n in NUM.findall(size.replace("−", "-").replace("∓", "-"))]
                out.append({"id": cells[0], "title": title, "dias": dias, "dia": dias[0] if dias else None, "walls": walls,
                            "wall": wall_any if not walls else None, "numbers": nums, "function": fn, "mating": fn,
                            "status": get("status"), "keyhole": "keyhole" in both.lower(), "file": rel(p),
                            "section": section.strip("# \n")})
    return out


def match_open_slot_b(rows, width, mouth):
    """The row for an open-ended slot: a slot its row calls open, whose size cell names its width and its mouth."""
    def has(r, v):
        return any(abs(abs(n) - v) < 0.006 for n in r["numbers"])
    c = [r for r in rows if "slot" in r["title"].lower() and "open" in r["title"].lower() and has(r, width) and
         has(r, mouth)]
    return c[0] if len(c) == 1 else None


def match_feature_b(rows, dia, wall, entry, keyhole=False, along=None):
    """The row for a hole of this size on this wall; when several rows fit, the one whose size cell names the
    hole's pod coordinate along the member (axis index `along`)."""
    def fits(r):
        d = next((x for x in r.get("dias", [r["dia"]]) if abs(x - dia) < 0.011), None)
        if d is None:
            return False
        w = r.get("walls", {}).get(d, r.get("wall"))
        return w in (None, wall)
    cands = [r for r in rows if fits(r) and r["keyhole"] == keyhole]
    if len(cands) <= 1:
        return cands[0] if cands else None
    ks = [along] if along is not None else range(3)
    # a register writes a mirrored pair's coordinate once, as ∓222.75: compare sizes, not signs
    hit = [r for r in cands if any(any(abs(abs(n) - abs(entry[k])) < 0.006 for n in r["numbers"]) for k in ks)]
    return hit[0] if len(hit) == 1 else None
