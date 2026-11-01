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


# The second register layout (BASE): | ID | Feature | Function | Size, position | Constraint | Status |
FR2_ROW = re.compile(r"^\|\s*(F[A-Z]{1,2}-\d+[A-Z]?)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*$")
DIA = re.compile(r"Ø\s*([\d.]+)")
NUM = re.compile(r"[-−+]?\d+(?:\.\d+)?")


def feature_rows_b(team, pn=None):
    """Rows of the second register layout that name a hole size: [{id, title, dia, wall, numbers, function,
    status, file, keyhole}]."""
    out = []
    for p in sorted(glob.glob(os.path.join(DRAWINGS, team, "FEATURE-RATIONALE*.md"))):
        section = ""
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    section = line
                    continue
                m = FR2_ROW.match(line.rstrip("\n"))
                if not m:
                    continue
                named = re.findall(r"(?<!\d)\d{6}(?!\d)", section)
                if pn and named and pn not in named:
                    continue        # a section about other parts
                title, fn, size = m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
                d = DIA.search(title) or DIA.search(size)
                if not d:
                    continue
                low = (title + " " + size).lower()
                wall = next((w for w in ("top", "bottom", "inner", "outer") if w + " wall" in low), None)
                nums = [float(n.replace("−", "-")) for n in NUM.findall(size.replace("−", "-"))]
                out.append({"id": m.group(1), "title": title, "dia": float(d.group(1).rstrip(".")), "wall": wall,
                            "numbers": nums, "function": fn, "mating": fn, "status": m.group(6).strip(),
                            "keyhole": "keyhole" in low, "file": rel(p), "section": section.strip("# \n")})
    return out


def match_feature_b(rows, dia, wall, entry, keyhole=False, along=None):
    """The row for a hole of this size on this wall; when several rows fit, the one whose size cell names the
    hole's pod coordinate along the member (axis index `along`)."""
    cands = [r for r in rows if abs(r["dia"] - dia) < 0.011 and (r["wall"] in (None, wall)) and
             r["keyhole"] == keyhole]
    if len(cands) <= 1:
        return cands[0] if cands else None
    ks = [along] if along is not None else range(3)
    hit = [r for r in cands if any(any(abs(n - entry[k]) < 0.006 for n in r["numbers"]) for k in ks)]
    return hit[0] if len(hit) == 1 else None
