"""D-131 (J-FRAME-01): the wall and ceiling frames in welded, galvanized steel, every member at its gauge.

Read from the source, never copied:
- which frames: the joints register's J-FRAME-01 table, its Parts row (211101 to 211104, 211201 to 211204, 411101 and
  411102 on 2026-11-01);
- each member's gauge: the Joints Engineer's own check, v2/01-CAD-Native/joints/frame_steel_check.py: its FRAMES table
  (roles per frame) and gauge(role, key=...) (1.2 for the side panels' rails and front stiles, 0.8 for studs and the
  ceiling's cross members 2 and 3, 1.0 for the rest); the register's text rule on top: any member with a site
  joint (spigot, rivnut or access hole) takes the perimeter gauge;
- the accepted steel: the same file's ACCEPTED grades (yield 280 MPa or more) and its ZINC (Z100).

Checked (C11, scope 'frames', so only a run that found the spec can close these findings):
- frame-steel (major): each frame's own row and every member row name galvanized steel, an accepted grade (or a
  stated yield of 280 MPa or more) and Z100; the frame's finish names the zinc and the zinc-rich touch-up on the welds;
- frame-gauge (severe when a member row is thinner than its gauge, minor when thicker or its role can't be told):
  every steel member row's wall against its role's gauge, and its section against the role's;
- frame-cad-gauge (severe when thinner, minor when thicker once the list says steel): every member body's wall as the
  CAD models it, its role read from where it sits in its frame.
"""

import importlib.util
import os
import re

from common import Finding, owner_for, rel, walk_files, read_csv

SPEC_PY = "v2/01-CAD-Native/joints/frame_steel_check.py"
REGISTER = "v2/05-Engineering/joints/joints-register.md"
SCOPE = "frames"

SECTION = re.compile(r"\b(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\b", re.I)
STEEL = re.compile(r"\bsteel\b", re.I)
NOT_STEEL = re.compile(r"\balumin(?:i?um)\b|\b6063\b|\b6061\b|\bstainless\b", re.I)
ZINC = re.compile(r"\bZ\s?(\d{2,3})\b")
YIELD = re.compile(r"(\d{3})\s*MPa", re.I)
GALV = re.compile(r"galvani[sz]|\bZ\s?\d{2,3}\b|\bzinc\b", re.I)
TOUCH_UP = re.compile(r"zinc[- ]rich", re.I)
SITE_HOLES = (8.5, 9.53, 9.63, 19.0)        # spigot, rivnut (838003's hole, +0.10), access hole (joints register)


# ----------------------------------------------------------------- the spec

def load_spec(root):
    """The Joints Engineer's frame check as a module (by its path, under a name of its own), or None."""
    p = os.path.join(root, SPEC_PY)
    if not os.path.exists(p):
        return None
    spec = importlib.util.spec_from_file_location("joints_frame_steel_check_%x" % (hash(p) & 0xffffff), p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name in ("FRAMES", "gauge", "ACCEPTED", "PERIMETER_T"):
        if not hasattr(mod, name):
            return None
    return mod


def frame_numbers(root):
    """J-FRAME-01's frames from its Parts row: '211101 to 211104 (...) and 211201 to 211204 (...); 411101 and 411102'."""
    p = os.path.join(root, REGISTER)
    if not os.path.exists(p):
        return []
    inside, out = False, []
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("### "):
                inside = "J-FRAME-01" in line
                continue
            if inside and line.startswith("| Parts |"):
                text = line.split("|")[2]
                for a, b in re.findall(r"\b(\d{6})\s+to\s+(\d{6})\b", text):
                    out += ["%06d" % n for n in range(int(a), int(b) + 1)]
                out += [n for n in re.findall(r"\b(\d{6})\b", re.sub(r"\b\d{6}\s+to\s+\d{6}\b", "", text))]
                break
    return sorted(set(out))


def frame_key(name):
    """The Joints table's frame for a frame or member name: L1 (side lower), L2 (side upper), B1 (back), C1 (ceiling);
    mirrors and copies share their key (R1 is L1's mirror, B2 to B4 are like B1, C2 like C1)."""
    n = (name or "").upper()
    if "CEILING" in n:
        return "C1"
    if "SIDE" in n and "LOWER" in n:
        return "L1"
    if "SIDE" in n and "UPPER" in n:
        return "L2"
    if "BACK" in n and re.search(r"\b(LOWER|UPPER|B[1-4])\b", n):
        return "B1"
    return None


def _w(*words):
    return re.compile(r"\b" + r"\W+".join(words) + r"\b", re.I)


# member names as the teams write them (WALL: 'RAIL - BOTTOM', 'STILE - MID'; the D-120 numbers: 'FRAME RAIL BOTTOM',
# 'FRAME STILE BACK 40 X 40'; CEILING: 'SIDE MEMBER', 'CROSS MEMBER 2', 'CROSS MEMBER - PLAIN') to the Joints table's
# roles; the first match wins
ROLE_RULES = {
    "L1": [(_w("STILE", "MID"), "stud"), (_w("STUD"), "stud"), (_w("STILE", "FRONT"), "front stile"),
           (_w("FRONT", "STILE"), "front stile"), (_w("STILE", "BACK"), "back stile"), (_w("BACK", "STILE"), "back stile"),
           (_w("RAIL"), "rail")],
    "L2": [(_w("STILE", "MID"), "stud"), (_w("STUD"), "stud"), (_w("STILE", "FRONT"), "front stile"),
           (_w("FRONT", "STILE"), "front stile"), (_w("STILE", "BACK"), "back stile"), (_w("BACK", "STILE"), "back stile"),
           (_w("RAIL", "BOTTOM"), "bottom rail"), (_w("BOTTOM", "RAIL"), "bottom rail"), (_w("RAIL", "TOP"), "top member"),
           (_w("TOP", "RAIL"), "top member"), (_w("TOP", "MEMBER"), "top member")],
    "B1": [(_w("STILE", "MID"), "stud"), (_w("STUD"), "stud"), (_w("RAIL"), "rail"), (_w("STILE"), "stile")],
    "C1": [(_w("CROSS", "MEMBER", "1"), "cross member 1 (soffit rivnuts)"), (re.compile(r"\bX1\b"), "cross member 1 (soffit rivnuts)"),
           (_w("CROSS", "MEMBER"), "cross members 2 and 3"), (re.compile(r"\bX[23]\b"), "cross members 2 and 3"),
           (_w("SIDE", "MEMBER"), "side and seam members"), (_w("SEAM", "MEMBER"), "side and seam members"),
           (re.compile(r"^\s*(SIDE|SEAM)\b", re.I), "side and seam members"),
           (_w("FRONT", "MEMBER"), "front member"), (re.compile(r"^\s*FRONT\b", re.I), "front member"),
           (_w("BACK", "MEMBER"), "back member"), (re.compile(r"^\s*BACK\b", re.I), "back member")],
}


def member_role(key, name):
    for pat, role in ROLE_RULES.get(key, []):
        if pat.search(name or ""):
            return role
    return None


def table_member(spec, key, role):
    """The Joints table's member for a role: (count, length, b in the frame's plane, d across it, role) or None."""
    for m in spec.FRAMES.get(key, (None, 0, 0, []))[3]:
        if m[4] == role or m[4].startswith(role + ","):
            return m
    return None


def expected_gauge(spec, key, role, site_joint=False):
    g = spec.gauge(role, key=key)
    return max(g, spec.PERIMETER_T) if site_joint else g


def accepted_grades(spec):
    return [a[0].split(",")[0].strip() for a in spec.ACCEPTED]


def callout_lacks(spec, text):
    """What a material text lacks for J-FRAME-01's steel: [] when it names galvanized steel, an accepted grade (or a
    yield of the least accepted one or more) and Z100."""
    lacks = []
    if NOT_STEEL.search(text) or not STEEL.search(text):
        return ["galvanized steel (it reads '%s')" % text.strip()[:80]]
    fy_min = min(a[1] for a in spec.ACCEPTED)
    grades = accepted_grades(spec)
    if not any(g.upper().replace("+Z", "") in text.upper() for g in grades) and \
            not any(float(v) >= fy_min for v in YIELD.findall(text)):
        lacks.append("an accepted grade (%s, or a stated yield of %.0f MPa or more)" % (" or ".join(grades), fy_min))
    z = ZINC.findall(text)
    if not z:
        lacks.append("its zinc, Z100")
    elif any(v != "100" for v in z):
        lacks.append("Z100 zinc (it reads Z%s)" % z[0])
    return lacks


# ----------------------------------------------------------------- the lists

def _nk(row):
    return {re.sub(r"[^a-z0-9]+", "_", (k or "").strip().lower()).strip("_"): (v or "").strip()
            for k, v in row.items() if k is not None}


MEMBER_WORDS = re.compile(r"\b(RAIL|STILE|STUD|MEMBER|TUBE|X[123])\b", re.I)


def is_member_row(row):
    name = " ".join(x for x in (row.get("name", ""), row.get("member", "")) if x)
    return bool(MEMBER_WORDS.search(name)) and not re.search(r"\bHARDWARE\b", name, re.I)


def frame_rows(root, frames):
    """{frame pn: {"rows": [(file, line, row)], "members": [(file, line, row)]}} from the teams' CSVs: a frame's own row
    (its part number), and its members as the lists give them: rows one level under it (WALL's panel lists), rows
    whose frame or parent column names it (CEILING's tube cut list, a parts list's parent)."""
    out = {pn: {"rows": [], "members": []} for pn in frames}
    for p in walk_files(root, "v2/03-Manufacturing", exts=(".csv",)):
        try:
            rows = [_nk(r) for r in read_csv(p)]
        except (UnicodeDecodeError, OSError):
            continue
        r_ = rel(root, p)
        cur, cur_level = None, None
        for i, row in enumerate(rows, start=2):
            pn = row.get("part_number", "")
            lvl = row.get("level", "")
            lvl = int(lvl) if lvl.isdigit() else None
            if pn in out:
                out[pn]["rows"].append((r_, i, row))
                cur, cur_level = (pn, lvl) if lvl is not None else (None, None)
                continue
            if cur and lvl is not None and lvl > cur_level:
                if is_member_row(row):
                    out[cur]["members"].append((r_, i, row))
                continue
            if lvl is not None:
                cur = None
            owner = row.get("frame") or row.get("parent") or ""
            if owner in out and is_member_row(row):
                out[owner]["members"].append((r_, i, row))
    return out


def _member_name(row):
    return " ".join(x for x in (row.get("name", ""), row.get("member", "")) if x)


def _member_text(row):
    return " ".join(x for x in (row.get("material", ""), row.get("section", "")) if x)


def _section(row):
    """(a, b, wall) from the row's size, section, material or name ('20 x 40 x 1.2'), the wall under 5 mm."""
    for k in ("size_mm", "section", "material", "name"):
        for a, b, t in SECTION.findall(row.get(k, "")):
            if float(t) < 5.0:
                return float(a), float(b), float(t)
    return None


def check_frame_lists(root, spec, frames, rows=None):
    """frame-steel and frame-gauge findings, and {frame pn: True} for frames whose own row is steel."""
    fs, steel = [], {}
    rows = rows if rows is not None else frame_rows(root, frames)
    for pn in frames:
        d = rows.get(pn) or {"rows": [], "members": []}
        if not d["rows"]:
            continue                    # not listed yet: the BOM checks say so
        f0 = d["rows"][0][0]
        name = d["rows"][0][2].get("name", "")
        key = frame_key(name)
        owner = owner_for(f0, pn)
        lacks = []
        for f, i, row in d["rows"]:
            mat = row.get("material", "")
            ls = callout_lacks(spec, mat)
            if ls:
                lacks.append("its row (%s line %d) lacks %s" % (os.path.basename(f), i, "; ".join(ls)))
            fin = row.get("finish", "")
            if not GALV.search(fin):
                lacks.append("its finish (%s line %d) doesn't name the zinc ('%s')" % (os.path.basename(f), i, fin[:60]))
            elif not TOUCH_UP.search(fin + " " + row.get("process", "")):
                lacks.append("its finish (%s line %d) doesn't name the zinc-rich touch-up on the welds" % (
                    os.path.basename(f), i))
        steel[pn] = not any(callout_lacks(spec, r.get("material", "")) for _f, _i, r in d["rows"])
        bad_members, gauge_bad, thin, unknown = [], [], False, []
        for f, i, row in d["members"]:
            ls = callout_lacks(spec, _member_text(row))
            if ls:
                bad_members.append("%s (%s line %d)" % (_member_name(row) or "?", os.path.basename(f), i))
                continue
            role = member_role(key, _member_name(row))
            if role is None or table_member(spec, key, role) is None:
                unknown.append("%s (%s line %d)" % (_member_name(row), os.path.basename(f), i))
                continue
            sec = _section(row)
            want = expected_gauge(spec, key, role)
            if sec is None:
                gauge_bad.append("%s gives no wall (wants %.1f, %s)" % (_member_name(row), want, role))
                thin = True
                continue
            m = table_member(spec, key, role)
            if sorted(sec[:2]) != sorted((float(m[2]), float(m[3]))):
                gauge_bad.append("%s is %g x %g, the table's %s is %g x %g" % (
                    _member_name(row), sec[0], sec[1], role, m[2], m[3]))
            if abs(sec[2] - want) > 0.01:
                gauge_bad.append("%s is %.2f thick, the %s's gauge is %.1f" % (_member_name(row), sec[2], role, want))
                thin = thin or sec[2] < want
        if bad_members:
            lacks.append("%d member row%s not in J-FRAME-01's steel: %s" % (
                len(bad_members), "s" if len(bad_members) > 1 else "", ", ".join(bad_members[:6])))
        if lacks:
            gauges = "/".join("%.1f" % g for g in sorted({getattr(spec, a) for a in ("SIDE_T", "PERIMETER_T", "INNER_T")
                                                         if hasattr(spec, a)}, reverse=True))
            fs.append(Finding(
                "C11", "frame-steel", pn, "major",
                "%s %s: D-131 makes it welded galvanized steel (joints register J-FRAME-01: %s, Z100, %s mm gauges, "
                "zinc-rich touch-up on the welds), but %s." % (
                    pn, name, " or ".join(accepted_grades(spec)), gauges, "; ".join(lacks)),
                "Give the frame's row and each member row the steel, its grade and Z100, and the frame's finish the "
                "zinc and the weld touch-up, as J-FRAME-01 gives them (D-131).", f0, owner,
                {"model": SCOPE, "key": key}))
        if gauge_bad or unknown:
            fs.append(Finding(
                "C11", "frame-gauge", pn, "severe" if thin else "minor",
                "%s %s: %s%s (gauges from the Joints Engineer's frame_steel_check.py, J-FRAME-01)." % (
                    pn, name, "; ".join(gauge_bad),
                    ("; " if gauge_bad else "") + "can't tell the role in J-FRAME-01's table of %s" % ", ".join(unknown)
                    if unknown else ""),
                "Set each member's wall to its gauge (J-FRAME-01), and name members as the table does.", f0, owner,
                {"model": SCOPE, "key": key}))
    return fs, steel


# ----------------------------------------------------------------- the CAD

def wall_thickness(solid):
    """The smallest distance between two opposite flat faces of a body: a tube's wall."""
    planes = [f for f in solid.faces if f.kind == "plane"]
    best = None
    for i, a in enumerate(planes):
        for b in planes[i + 1:]:
            if sum(x * y for x, y in zip(a.normal, b.normal)) < -0.999999:
                gap = abs(sum((pa - pb) * n for pa, pb, n in zip(a.origin, b.origin, a.normal)))
                if gap > 0.05 and (best is None or gap < best):
                    best = gap
    return best


def _close(x, v, tol=0.6):
    return abs(x - v) <= tol


def cad_members(bodies, pn):
    """The member bodies of frame `pn` in a model (their labels name the frame), each with its box axes."""
    out = []
    for b in bodies:
        if not re.search(r"(?<!\d)%s(?!\d)" % pn, b.label or ""):
            continue
        ext = [b.box[k + 3] - b.box[k] for k in range(3)]
        n = max(range(3), key=lambda k: ext[k])
        others = sorted(ext[k] for k in range(3) if k != n)
        if ext[n] < 100.0 or not all(any(_close(e, v) for v in (20.0, 40.0)) for e in others):
            continue                    # a plate, a rivnut, a washer: not a tube member
        out.append((b, n, ext))
    return out


def cad_roles(key, members):
    """[(body, role, site_joint)] from where each member sits in its frame: on the outline or inside it, along the
    studs (walls: Z) or the cross members (ceiling: X) or across them, front (-Y) or back, low or high."""
    if not members:
        return []
    lo = [min(b.box[k] for b, _n, _e in members) for k in range(3)]
    hi = [max(b.box[k + 3] for b, _n, _e in members) for k in range(3)]
    depth = min(range(3), key=lambda k: hi[k] - lo[k])
    stud_axis = 0 if key == "C1" else 2
    out = []
    for b, n, ext in members:
        across = [k for k in range(3) if k not in (n, depth)]
        if n == depth or not across:
            out.append((b, None, False))
            continue
        w = across[0]
        edge = _close(b.box[w], lo[w]) or _close(b.box[w + 3], hi[w])
        site = any(any(abs(h.diameter - d) <= 0.2 for d in SITE_HOLES) for h in b.solid.holes)
        along = n == stud_axis
        if not edge:
            role = ("cross member 1 (soffit rivnuts)" if site else "cross members 2 and 3") if key == "C1" else "stud"
        elif key == "C1":
            role = "side and seam members" if not along else (
                "front member" if _close(b.box[1], lo[1]) else "back member")
        elif key == "B1":
            role = "stile" if along else "rail"
        else:                           # L1, L2: stiles along the studs, front (-Y) or back; rails across them
            if along:
                role = "front stile" if _close(b.box[1], lo[1]) else "back stile"
            elif key == "L1":
                role = "rail"
            else:
                role = "bottom rail" if _close(b.box[2], lo[2]) else "top member"
        out.append((b, role, site and not edge))
    return out


def check_frame_cad(root, spec, frames, bodies, names, steel):
    """frame-cad-gauge findings. names: frame pn -> its name (for its key); steel: frame pn -> its list says steel."""
    fs = []
    for pn in frames:
        mem = cad_members(bodies, pn)
        if not mem:
            continue
        key = frame_key(names.get(pn) or next((b.label for b, _n, _e in mem), ""))
        if key is None:
            continue
        bad, thin = [], False
        for b, role, site in cad_roles(key, mem):
            short = (b.label or "").split(" / ")[-1]
            if role is None or table_member(spec, key, role) is None:
                bad.append("%s: can't tell its role" % short)
                continue
            t = wall_thickness(b.solid)
            want = expected_gauge(spec, key, role, site)
            if t is None:
                continue
            if t < want - 0.02:
                bad.append("%s (%s%s) is %.2f thick, its gauge is %.1f" % (
                    short, role, ", with a site joint" if site else "", t, want))
                thin = True
            elif t > want + 0.02 and steel.get(pn):
                bad.append("%s (%s) is %.2f thick, its gauge is %.1f" % (short, role, t, want))
        if bad:
            f = mem[0][0].file
            fs.append(Finding(
                "C11", "frame-cad-gauge", pn, "severe" if thin else "minor",
                "%s's members in the CAD (%s): %s (gauges from the Joints Engineer's frame_steel_check.py, "
                "J-FRAME-01, D-131)." % (pn, os.path.basename(f), "; ".join(bad[:8])),
                "Model each member at its gauge and export the STEP again (the drawings and masses come from it).",
                f, owner_for(f, pn), {"model": SCOPE, "key": key}))
    return fs


def check_frames(root, bodies):
    """All three, and whether the spec was found (only then do the 'frames' findings count as checked)."""
    spec = load_spec(root)
    frames = frame_numbers(root)
    if spec is None or not frames:
        return [], False
    rows = frame_rows(root, frames)
    fs, steel = check_frame_lists(root, spec, frames, rows)
    names = {pn: (d["rows"][0][2].get("name", "") if d["rows"] else "") for pn, d in rows.items()}
    fs += check_frame_cad(root, spec, frames, bodies, names, steel)
    return fs, True
