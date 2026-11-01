#!/usr/bin/env python3
"""Builds and checks the master BOM of Spaceship (FocusPod v2).

Doc code V2-BOM-001, revision P01. Standard library only.

It reads every team's parts list and the joints register's hardware set:
  - parts lists: every v2/03-Manufacturing/<team>/**/*_BOM.csv that has a part_number column (cut lists
    without one are skipped and named in the report), and from v2/07-Packaging/**/*_BOM.csv only the
    packaging items (family 91): a packing list names other teams' parts, which their own lists carry;
  - v2/05-Engineering/joints/joints-register.md: the hardware set table (ID H-nn) and any table
    with a "Part number" column. The joints register owns every fastener and hardware number (D-63);
  - v2/04-BOM/number-allocation.csv: numbers this master BOM gives out before a team's list uses them
    (D-120: frame members and fill pieces). Each row is ALLOCATED or CANCELLED and never reused.

and writes, into v2/04-BOM/ unless --out says otherwise:
  100000_P01_POD-MASTER_BOM.csv               POD, then each assembly with its parts, then the hardware
  100000_P01_POD-MADE-PARTS-BY-PROCESS_BOM.csv made parts, sorted by process
  100000_P01_POD-BOUGHT-PARTS_BOM.csv         bought parts, one row per part number, with their status
  BOM-CHECK.md                                 the check result and what is missing, per team

Usage, from anywhere:
  python3 v2/04-BOM/build_master_bom.py                 # the files in this working tree
  python3 v2/04-BOM/build_master_bom.py --ref origin/main --ref origin/BRANCH ...
        # reads the files from those git refs instead; a later ref adds only the files its branch changed
        # since its merge-base with the first ref, and wins for those
  --out DIR       write the outputs into DIR
  --no-write      check only, write nothing

Exit code 0 when the check passes, 1 when it fails. The check fails on:
  1. a part with no number (not 6 digits);
  2. a duplicate number: one number used for two different items;
  3. a part with no mass;
  4. a hardware item with no row in the joints register;
  5. a reserved old number (D-28);
  6. an allocated number that is badly formed, outside its band (conventions section 6), allocated twice,
     used for a different item, or used after it was cancelled.
Everything else that is missing (no parts list yet, no finish, no process, HOLD items, register
rows with no number) is listed per team as "missing", without failing the check.

"Hardware" means every bought item except AIR (61), ELECTRICAL (71) and PACKAGING (91) items,
whose numbers their own teams give (reading of D-63 and the PM's brief, 2026-10-31).
Masses in kg, sizes in mm. No prices: the parts lists carry none, and this script reads none.
"""
import argparse
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REV = "P01"
BOM_GLOBS = ["v2/03-Manufacturing", "v2/07-Packaging"]
REGISTER = "v2/05-Engineering/joints/joints-register.md"
ALLOCATION = "v2/04-BOM/number-allocation.csv"  # numbers given out before a team's list uses them (D-120)
ALLOCATED = []  # its rows, read by build()
BANDS = {"MP": (1000, 7999), "HS": (1, 999), "BS": (1, 999), "PI": (8000, 8999)}  # NNNN per kind (conventions section 6)
TREE = "v2/00-Control/assembly-tree.md"
# Families with no node in the assembly tree: Vietnamese added by the control pack (conventions.md section 6).
FAMILY_VI = {"83": "Bulông, tán rút, đai ốc, long đen", "84": "Gioăng và băng dính theo mét"}
# Old numbers from the guideline's examples and the earlier attempt: never reused (D-28).
RESERVED_PN = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}
NOT_HARDWARE = {"61", "71", "91"}

# Family codes (conventions.md section 6) -> master BOM group, its node number, the team that lists it.
FAMILIES = [
    ("10", "", "POD - GENERAL ITEMS AND INSTALLATION KIT (family 10)", "Packing and Assembly"),
    ("11", "110000", "BASE", "BASE"),
    ("21", "210000", "WALL", "WALL"),
    ("35", "350000", "FRONT - DECOR", "FRONT"),
    ("36", "360000", "FRONT - DOOR AND GLAZING", "FRONT"),
    ("41", "410000", "CEILING", "CEILING"),
    ("51", "510000", "LINING", "WALL and CEILING"),
    ("61", "610000", "AIR", "CEILING (builds AIR, D-80)"),
    ("71", "710000", "ELECTRICAL", "ELECTRICAL"),
    ("81", "810000", "INTERIOR", "CEILING (builds INTERIOR, D-80)"),
    ("83", "", "HARDWARE: FASTENERS, INSERTS, NUTS, WASHERS (family 83)", "Joints register"),
    ("84", "", "SEALS AND TAPES BY LENGTH (family 84)", "Joints register"),
    ("91", "910000", "PACKAGING", "Packing and Assembly"),
]
FAMILY = {f[0]: f for f in FAMILIES}
# Folders where each team's parts lists live (for "no parts list yet").
EXPECTED_FOLDERS = {
    "BASE": "v2/03-Manufacturing/base/", "WALL": "v2/03-Manufacturing/wall/", "FRONT": "v2/03-Manufacturing/front/",
    "CEILING": "v2/03-Manufacturing/ceiling/", "CEILING (builds AIR, D-80)": "v2/03-Manufacturing/air/",
    "CEILING (builds INTERIOR, D-80)": "v2/03-Manufacturing/interior/", "ELECTRICAL": "v2/03-Manufacturing/electrical/",
    "Packing and Assembly": "v2/07-Packaging/",
}
MASTER_COLS = ["level", "row_type", "group", "part_number", "name", "name_vi", "qty_per_pod", "qty_status",
               "material", "finish", "mass_each_kg", "mass_status", "mass_total_kg", "make_buy", "process",
               "process_status", "product_status", "register_id", "team", "source_file", "note"]


# ------------------------------------------------------------------ reading
def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


FELL_BACK = []  # (ref, path): files a branch changed that base changed later, so base's copy was read


def branch_changes(base, ref, *paths, diff_filter=None):
    """The files ref changed since its merge-base with base, less those base changed later. A branch stacked on a PR
    that has since been squash-merged still carries that PR's older copies (AIR's branch kept CEILING's old lists
    after #32 merged); base's newer copy wins for those. Later means a newer author time: a rebase keeps it (its
    committer time is the rebase's), and a squash merge sets it to the merge. A branch's own edit of a file that base
    changed later is dropped too, until the branch rebases; each dropped file goes in FELL_BACK so the reports name it."""
    mb = git("merge-base", base, ref).strip()
    flt = [f"--diff-filter={diff_filter}"] if diff_filter else []
    changed = git("diff", "--name-only", *flt, mb, ref, "--", *paths).splitlines()
    later = set(git("diff", "--name-only", mb, base, "--", *paths).splitlines())

    def last(tip, path):
        return int(git("log", "-1", "--format=%at", f"{mb}..{tip}", "--", path).strip() or 0)

    keep = []
    for f in changed:
        if f in later and last(ref, f) <= last(base, f):
            if (ref, f) not in FELL_BACK:
                FELL_BACK.append((ref, f))
        else:
            keep.append(f)
    return keep


def print_fell_back(labels=None):
    """Print each parts list or register a branch changed but main changed later (main's copy was read)."""
    for x in fell_back_lines(labels, keep=wanted):
        print("  read from main:", x)


def fell_back_lines(labels=None, keep=None):
    """One line per file read from base although a branch changed it, for the reports; keep(path) filters them."""
    return [f"`{path}`: {(labels or {}).get(ref, ref)} changed it, but main changed it later, so main's copy is read "
            f"until that branch rebases" for ref, path in sorted(FELL_BACK, key=lambda x: (x[1], x[0]))
            if keep is None or keep(path)]


def wanted(path):
    if path in (REGISTER, ALLOCATION):
        return True
    return path.endswith("_BOM.csv") and any(path.startswith(g + "/") for g in BOM_GLOBS) and "/proof/" not in path


def load_sources(refs):
    """Return {path: (text, where)} from the working tree, or from the git refs in order (a later ref wins)."""
    found = {}
    if not refs:
        for g in BOM_GLOBS:
            base = ROOT / g
            if base.exists():
                for p in sorted(base.rglob("*_BOM.csv")):
                    rel = p.relative_to(ROOT).as_posix()
                    if wanted(rel):
                        found[rel] = (p.read_text(encoding="utf-8"), "working tree")
        for extra in (REGISTER, ALLOCATION):
            if (ROOT / extra).exists():
                found[extra] = ((ROOT / extra).read_text(encoding="utf-8"), "working tree")
        return found
    base = refs[0]
    for i, ref in enumerate(refs):
        short = git("rev-parse", "--short", ref).strip()
        names = git("ls-tree", "-r", "--name-only", ref, "--", *BOM_GLOBS, REGISTER, ALLOCATION).splitlines()
        if i:
            # A later ref adds only the files its own branch changed: an old, untouched copy of a file
            # (the joints register on a branch cut before the register moved on) never overrides the first ref,
            # and neither does a stacked branch's old copy of a file the first ref has replaced since.
            changed = set(branch_changes(base, ref, *BOM_GLOBS, REGISTER, ALLOCATION))
            names = [n for n in names if n in changed]
        for rel in names:
            if wanted(rel):
                found[rel] = (git("show", f"{ref}:{rel}"), f"{ref} ({short})")
    return found


def num(value):
    try:
        return float(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None


def first(row, *keys):
    for k in keys:
        v = (row.get(k) or "").strip()
        if v:
            return v
    return ""


def split_finish(material):
    """'aluminium EN AW-6082-T6, finish to match the base band' -> (material, finish)."""
    m = re.search(r"[,;]\s*finish(?:ed)?\b[:\s]*(.+)$", material, re.I)
    if m:
        return material[:m.start()].strip(), m.group(1).strip()
    return material, ""


def make_buy_of(kind):
    """Part classes (assembly-tree.md, guideline 4.1): MP made, BS bonded subassembly, HS subassembly
    with hardware, PI bought, KIT the installation kit; or words such as 'made ...', 'bought ...'."""
    k = kind.strip()
    if k.upper() == "MP":
        return "make"
    if k.upper() in ("BS", "HS", "KIT"):
        return "assembly"
    if k.upper() in ("PI", "HOLD"):
        return "buy"
    low = k.lower()
    if "assembly" in low:
        return "assembly"
    if low.startswith("made") or low.startswith("make"):
        return "make"
    if low.startswith("bought") or low.startswith("buy"):
        return "buy"
    return ""


PROCESS_BY_MATERIAL = [
    (r"\bACP\b|aluminium composite", "ACP sheet: CNC-routed, grooved and folded where it turns"),
    (r"glass", "glass: cut, toughened and laminated by the supplier, to drawing"),
    (r"galvani[sz]ed steel|\bDX51D|steel sheet", "sheet metal: laser-cut and bent"),
    (r"stainless", "stainless: machined or bought as supplied"),
    (r"alumin(i)?um.*(tube|\d+\s*x\s*\d+\s*x\s*\d)|\b6063\b|\b6060\b", "aluminium tube: cut to length, drilled, rivnuts set"),
    (r"alumin(i)?um", "aluminium: machined or cut"),
    (r"felt", "felt: cut to size"),
    (r"\bfill\b|sorberpoly|polyester fibre", "fill: cut to size"),
    (r"plywood|\bply\b", "board: CNC-cut"),
    (r"foam", "foam: cut to size"),
]


def process_of(kind, material):
    m = re.match(r"\s*made\b\s*(.+?)\s*$", kind, re.I)
    if m:
        rest = m.group(1)
        if rest.startswith("(") and rest.endswith(")"):
            rest = rest[1:-1]
        return rest.strip(), "source (parts list)"
    for pattern, label in PROCESS_BY_MATERIAL:
        if re.search(pattern, material, re.I):
            return label, "assumption (from the material)"
    return "", ""


def team_of(path):
    parts = path.split("/")
    if path.startswith("v2/07-Packaging/"):
        return "Packing and Assembly"
    folder = parts[2] if len(parts) > 3 else ""
    return {"air": "CEILING (builds AIR, D-80)", "interior": "CEILING (builds INTERIOR, D-80)"}.get(folder, folder.upper())


RESERVED_AIR = re.compile(r"\breserved air space\b", re.I)
# HOLD as a whole word, in capitals as before: "SEAL HOLDER", "HOLDS" and "THRESHOLD" are not HOLD (Reviewer 6, #211)
HOLD_WORD = re.compile(r"\bHOLD\b")
RESERVED_SEEN = []  # the rows build() skipped as reserved air spaces, for the report (D-105)


def parse_parts_list(path, text, where):
    """One row per line of a team's parts list, normalised. Returns (rows, skipped_reason)."""
    if "CUT-LIST" in path.rsplit("/", 1)[-1].upper():
        # a cut list's rows are cut pieces of parts the parts lists already carry: read as parts they would count
        # twice, and pieces carry no mass of their own
        return [], "a cut list (its rows are cut pieces of the parts in the parts lists)"
    reader = csv.DictReader(io.StringIO(text))
    cols = [c.strip().lower() for c in (reader.fieldnames or [])]
    if "part_number" not in cols:
        return [], "no part_number column (a cut list or another table)"
    raw = [{(k or "").strip().lower(): (v or "") for k, v in r.items()} for r in reader]
    raw = [r for r in raw if any(v.strip() for v in r.values())]
    # The top assembly of the file: its quantity per pod multiplies the children's "qty".
    top_qty = 1.0
    if raw and "qty_per_pod" not in cols:
        kind0 = first(raw[0], "type", "kind", "class")
        if make_buy_of(kind0) == "assembly":
            top_qty = num(first(raw[0], "qty")) or 1.0
    packing = path.startswith("v2/07-Packaging/")
    rows = []
    for i, r in enumerate(raw):
        if packing and family_of(first(r, "part_number")) != "91":
            continue  # a packing list names other teams' parts; only packaging items (family 91) are BOM lines here
        kind = first(r, "make_buy", "type", "kind", "class")
        if RESERVED_AIR.search(kind):
            # a reserved air space in another team's block: the part is AIR's, counted once in AIR's list (D-105)
            RESERVED_SEEN.append((first(r, "part_number"), first(r, "name", "name_en"), path, where))
            continue
        if kind.strip().lower() == "cut":
            continue  # a cut length of the made part above it (its own cut list), not a BOM line
        mb = first(r, "make_buy").lower() or make_buy_of(kind)
        if "qty_per_pod" in cols:
            q, qs = num(first(r, "qty_per_pod")), "source (parts list)"
        else:
            q = num(first(r, "qty"))
            is_top = i == 0 and make_buy_of(first(raw[0], "type", "kind", "class")) == "assembly"
            if q is not None and not is_top and top_qty != 1.0:
                q, qs = q * top_qty, "calculation (qty x its unit's qty per pod)"
            else:
                qs = "source (parts list)"
        material, finish = first(r, "material"), first(r, "finish")
        if not finish:
            material, finish = split_finish(material)
        mass = num(first(r, "unit_mass_kg", "mass_each_kg", "mass_kg", "mass", "kg"))
        mtot, qraw = num(first(r, "mass_total_kg")), num(first(r, "qty"))
        derived = mass is None and mtot is not None and qraw
        if derived:
            mass = mtot / qraw
        process, pstatus = ("", "")
        if mb == "make":
            process, pstatus = (first(r, "process"), "source (parts list)") if first(r, "process") else process_of(kind, material)
        status = first(r, "status")
        name = first(r, "name", "name_en")
        text_all = " ".join([status, kind, name, first(r, "mass_each_kg", "unit_mass_kg")])
        rows.append({
            "part_number": first(r, "part_number"), "name": name, "name_vi": first(r, "name_vi"),
            "qty_per_pod": q, "qty_status": qs, "material": material, "finish": finish,
            "mass_each_kg": mass,
            "mass_status": first(r, "mass_status", "kg_status") or ("calculation (mass total / qty)" if derived else (first(r, "status") if mass is not None else "")),
            "make_buy": mb, "process": process, "process_status": pstatus,
            "product_status": status, "hold": bool(HOLD_WORD.search(text_all)), "team": team_of(path),
            "source_file": f"{path} @ {where}", "note": first(r, "note", "source"), "kind": kind,
        })
    return rows, ""


def table_rows(md_text):
    header = None
    for line in md_text.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        if header is None:
            header = cells
            continue
        yield header, cells


def clean(s):
    return re.sub(r"\*+", "", s).strip()


def parse_register(text, where):
    """Hardware items of the joints register: one per part number, plus one per ID that has no number yet.
    [{'id', 'name', 'part_number', 'qty_per_pod', 'mass_each_kg', 'source_file'}]. Reads the hardware set
    table (ID | Item | ...) and any table with a part-number column; an ID's first cell may sit under any
    header (ID or Item). One ID may have several numbers (a gasket in two thicknesses)."""
    fam = "|".join(FAMILY)
    numbered, unnumbered = {}, {}
    for hdr, cells in table_rows(text):
        h = [x.lower() for x in hdr]
        pn_col = next((i for i, x in enumerate(h) if re.search(r"part\s*(number|no)\b|^pn$", x)), None)
        is_set = h[:2] == ["id", "item"]
        if not is_set and pn_col is None:
            continue
        row = dict(zip(h, cells))
        rid = cells[0] if re.fullmatch(r"H-\d+\w*", clean(cells[0])) else ""
        rid = clean(rid)
        if is_set and not rid:
            continue
        if pn_col is not None:
            m = re.search(r"\b\d{6}\b", cells[pn_col]) if pn_col < len(cells) else None
        else:
            m = next((re.search(r"\b(?:%s)\d{4}\b" % fam, c) for c in cells if re.search(r"\b(?:%s)\d{4}\b" % fam, c)), None)
        pn = m.group(0) if m else ""
        ncol = next((x for x in h if "name" in x), None)
        name = clean(row.get(ncol, "")) if ncol else ""
        if not name:
            item = clean(row.get("item", ""))
            name = "" if re.fullmatch(r"H-\d+\w*", item) else item
        name = name.split(" · ")[0].strip()
        if is_set:
            name = re.split(r"(?<=\.)\s", name, maxsplit=1)[0].rstrip(".")
        qcol = next((x for x in h if "qty" in x or "per pod" in x), None)
        mcol = next((x for x in h if "mass" in x), None)
        entry = {"id": rid, "name": name, "part_number": pn,
                 "qty_per_pod": num(row.get(qcol)) if qcol else None,
                 "mass_each_kg": num(row.get(mcol)) if mcol else None,
                 "source_file": f"{REGISTER} @ {where}"}
        if pn:
            old = numbered.setdefault(pn, entry)
            for k in ("id", "name", "qty_per_pod", "mass_each_kg"):
                old[k] = old[k] if old[k] not in ("", None) else entry[k]
        elif rid or name:
            old = unnumbered.setdefault(rid or name, entry)
            old["name"] = old["name"] or name
    have = {e["id"] for e in numbered.values() if e["id"]}
    return list(numbered.values()) + [e for k, e in unnumbered.items() if not e["id"] or e["id"] not in have]


# ------------------------------------------------------------------ building and checking
def family_of(pn):
    return pn[:2] if re.fullmatch(r"\d{6}", pn or "") else ""


GENERIC = {"HARDWARE", "THE", "FOR", "WITH", "AND", "OF", "A", "AN", "IN", "ON", "TO", "PC", "PCS"}
SIZE = re.compile(r"[A-Z]?\d[\d.]*(?:\s*X\s*[A-Z]?\d[\d.]*)+")


def _up(s):
    s = re.sub(r"\(H-\d+\w*\)", " ", (s or "").upper())  # drop register ID tags such as (H-05)
    s = s.replace("×", " X ").replace("Ø", "D")
    return re.sub(r"(?<=\d)\s*X\s*(?=[\dDM])", " X ", s)


def _sizes(s):
    return [frozenset(p.strip() for p in m.group(0).split("X")) for m in SIZE.finditer(_up(s))]


def _tokens(s, digits):
    toks = {t.strip(".-") for t in re.findall(r"[A-Z0-9][A-Z0-9.\-]*", _up(s))}
    return {t for t in toks if t and (bool(re.search(r"\d", t)) == digits) and t not in GENERIC and t != "X"}


def same_item(a, b):
    """True when a parts-list name and the joints register's name describe the same item: their size groups
    agree (one inside the other, any order), their threads or diameters (M6, D8) agree, they share a word, and
    either most of the shorter name's numbered tokens match or they share two words (a product code on one side
    and a requirement such as 'gap 10 ±5' on the other). Wording and order may differ."""
    sa, sb = _sizes(a), _sizes(b)
    if sa and sb:
        def covered(xs, ys):
            return all(any(x <= y or y <= x for y in ys) for x in xs)
        if not (covered(sa, sb) or covered(sb, sa)):
            return False
    ta, tb = _tokens(a, True), _tokens(b, True)
    wa, wb = _tokens(a, False), _tokens(b, False)
    tha = {x for x in ta if re.fullmatch(r"[MD]\d+(?:\.\d+)?", x)}
    thb = {x for x in tb if re.fullmatch(r"[MD]\d+(?:\.\d+)?", x)}
    if tha and thb and not tha & thb:
        return False  # different thread or diameter: M6 is not M10
    shared_words = wa & wb
    if wa and wb and not shared_words:
        return False
    if ta and tb and len(ta & tb) / min(len(ta), len(tb)) < 0.5 and len(shared_words) < 2:
        return False  # numbers differ and the names share at most one word
    if wa and wb and not (ta and tb):
        return len(shared_words) / min(len(wa), len(wb)) >= 0.5
    return True


def is_hardware(r):
    return r["make_buy"] == "buy" and family_of(r["part_number"]) not in NOT_HARDWARE


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def parse_allocation(text, where):
    """The allocation list's rows: part_number, name, kind (MP, HS, BS or PI), team, parent, qty_per_parent,
    qty_per_pod, basis (what the number is for, from the team's own list), status (ALLOCATED or CANCELLED), note."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        pn = (r.get("part_number") or "").strip()
        if not pn:
            continue
        out.append({"part_number": pn, "name": (r.get("name") or "").strip(), "name_vi": (r.get("name_vi") or "").strip(),
                    "kind": (r.get("kind") or "").strip().upper(),
                    "team": (r.get("team") or "").strip(), "parent": (r.get("parent") or "").strip(),
                    "qty_per_parent": num(r.get("qty_per_parent")), "qty_per_pod": num(r.get("qty_per_pod")),
                    "basis": (r.get("basis") or "").strip(), "status": (r.get("status") or "").strip().upper(),
                    "note": (r.get("note") or "").strip(), "source_file": f"{ALLOCATION} @ {where}"})
    return out


def build(sources):
    parts, skipped, register, reg_where = [], [], [], None
    RESERVED_SEEN.clear()
    ALLOCATED.clear()
    for path in sorted(sources):
        text, where = sources[path]
        if path == REGISTER:
            register, reg_where = parse_register(text, where), where
            continue
        if path == ALLOCATION:
            ALLOCATED.extend(parse_allocation(text, where))
            continue
        rows, why = parse_parts_list(path, text, where)
        if why:
            skipped.append((path, where, why))
        parts.extend(rows)
    return parts, skipped, register, reg_where


def check(parts, register, reg_where, read_paths=()):
    """read_paths: the parts-list files read (some may give no BOM lines, such as a packing list)."""
    fails, missing = [], {}

    def miss(team, msg):
        missing.setdefault(team, []).append(msg)

    reg_numbers = {i["part_number"] for i in register if i["part_number"]}
    reg_by_pn = {i["part_number"]: i for i in register if i["part_number"]}
    names_by_pn = {}
    for r in parts:
        pn, where = r["part_number"], r["source_file"]
        label = f"{pn or '(no number)'} {r['name']}"
        if not re.fullmatch(r"\d{6}", pn):
            fails.append(f"no part number: '{r['name']}' in {where}")
        elif pn in RESERVED_PN:
            fails.append(f"reserved old number {pn} (D-28): '{r['name']}' in {where}")
        else:
            names_by_pn.setdefault(pn, {}).setdefault(norm(r["name"]), []).append(where)
            if family_of(pn) not in FAMILY:
                miss(r["team"], f"{label}: family {family_of(pn)} is not in conventions section 6")
        if r["make_buy"] != "assembly" and r["mass_each_kg"] is None:
            fails.append(f"no mass: {label} in {where}")
        if pn in reg_by_pn and not same_item(r["name"], reg_by_pn[pn]["name"]):
            ri = reg_by_pn[pn]
            fails.append(f"duplicate number {pn}: '{r['name']}' in {where} is not the joints register's {ri['id']} '{ri['name']}'")
        if is_hardware(r) and re.fullmatch(r"\d{6}", pn) and pn not in reg_numbers:
            fails.append(f"hardware with no joints-register row: {label} in {where}")
        if r["make_buy"] == "":
            miss(r["team"], f"{label}: make or buy not stated (type '{r['kind']}')")
        if r["qty_per_pod"] is None:
            miss(r["team"], f"{label}: no quantity per pod")
        if r["make_buy"] in ("make", "buy") and re.search(r"alumin|steel|zinc", r["material"], re.I) \
                and not r["finish"] and not re.search(r"galvani|\+Z\b|stainless|\bA2\b|\bzinc\b|plated|anodi[sz]ed|mill finish|powder|painted", r["material"], re.I):
            miss(r["team"], f"{label}: metal part with no finish (D-79: hidden tubes 6063-T6 mill finish plus the bond prep; visible aluminium black AA20, D-67)")
        if r["make_buy"] == "make" and not r["process"]:
            miss(r["team"], f"{label}: made part with no process")
        if r["hold"]:
            miss(r["team"], f"{label}: HOLD ({r['product_status'] or r['kind']})")
    for pn, names in sorted(names_by_pn.items()):
        if len(names) > 1 and pn not in reg_numbers:  # register numbers are checked against the register's item above
            uses = "; ".join(f"'{n}' in {', '.join(sorted(set(w)))}" for n, w in names.items())
            fails.append(f"duplicate number {pn}: {uses}")
    if reg_where is None:
        miss("Joints register", f"no joints register found at {REGISTER}, so no hardware can be matched")
    else:
        for item in register:
            if not item["part_number"]:
                miss("Joints register", f"{item['id']} {item['name']}: no part number")
    listed_teams = {r["team"] for r in parts}
    for team, folder in EXPECTED_FOLDERS.items():
        if team not in listed_teams:
            read = sorted(p for p in read_paths if p.startswith(folder))
            if read and folder == "v2/07-Packaging/":
                msg = f"no packaging items (family 91) listed yet; {read[0]} names other teams' parts, which their own lists carry"
            elif read:
                msg = f"no BOM lines yet in {', '.join(read)}"
            else:
                msg = f"no parts list yet (expected *_BOM.csv files in {folder})"
            missing.setdefault(team, []).insert(0, msg)
    for fam, node, name, team in FAMILIES:
        if fam in ("10", "83", "84", "91"):
            continue
        if not any(family_of(r["part_number"]) == fam for r in parts) and team in listed_teams:
            miss(team, f"no {node or fam + 'xxxx'} {name} parts listed yet")
    fails += check_allocation(parts, reg_by_pn)
    return fails, missing


def allocation_uses(parts):
    """{allocated number: the team rows that use it}."""
    allocated = {a["part_number"] for a in ALLOCATED}
    uses = {}
    for r in parts:
        if r["part_number"] in allocated:
            uses.setdefault(r["part_number"], []).append(r)
    return uses


def fits_allocation(team_name, allocated_name):
    """A team's name fits an allocated number when it has every word of the allocated name, in any order (it may add
    words). Stricter than same_item, which lets two names that share only 'CEILING' and 'C1' pass."""
    return set(norm(allocated_name).split()) <= set(norm(team_name).split())


def check_allocation(parts, reg_by_pn):
    """D-120: the numbers this master BOM gives out. Fails on a number that is badly formed, outside its kind's band,
    a reserved old number, allocated twice, used for a different item, used after it was cancelled, or a joints
    register number."""
    fails, seen = [], set()
    uses = allocation_uses(parts)
    for a in ALLOCATED:
        pn, label = a["part_number"], f"allocated {a['part_number']} '{a['name']}'"
        if not re.fullmatch(r"\d{6}", pn):
            fails.append(f"{label}: not a 6-digit number")
            continue
        if pn in RESERVED_PN:
            fails.append(f"{label}: a reserved old number (D-28)")
        if family_of(pn) not in FAMILY:
            fails.append(f"{label}: family {family_of(pn)} is not in conventions section 6")
        if a["kind"] not in BANDS:
            fails.append(f"{label}: kind '{a['kind']}' is not MP, HS, BS or PI")
        else:
            lo, hi = BANDS[a["kind"]]
            if not lo <= int(pn[2:]) <= hi:
                fails.append(f"{label}: {pn[2:]} is outside the {a['kind']} band {lo:04d} to {hi:04d} (conventions section 6)")
        if a["status"] not in ("ALLOCATED", "CANCELLED"):
            fails.append(f"{label}: status '{a['status']}' is not ALLOCATED or CANCELLED")
        if pn in seen:
            fails.append(f"{label}: allocated twice")
        seen.add(pn)
        if pn in reg_by_pn:
            fails.append(f"{label}: the joints register already has {pn} ({reg_by_pn[pn]['id']})")
        for r in uses.get(pn, []):
            if a["status"] == "CANCELLED":
                fails.append(f"cancelled number {pn} used: '{r['name']}' in {r['source_file']} (a cancelled number is never reused)")
            elif not fits_allocation(r["name"], a["name"]):
                fails.append(f"allocated number {pn} ('{a['name']}') used for '{r['name']}' in {r['source_file']}")
    return fails


def fmt(x, nd=3):
    if x is None:
        return ""
    return f"{x:.{nd}f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


def node_names(refs=None):
    """{node: (English name, Vietnamese name)} from the assembly tree's node table (`| Node | Name · Vietnamese |`),
    read from the first git ref when refs are given, else from this working tree."""
    if refs:
        text = git("show", f"{refs[0]}:{TREE}")
    else:
        p = ROOT / TREE
        text = p.read_text(encoding="utf-8") if p.exists() else ""
    out = {}
    for hdr, cells in table_rows(text):
        if hdr and hdr[0].lower() == "node" and re.fullmatch(r"\d{6}", cells[0]):
            en, _, vi = cells[1].partition(" · ")
            out[cells[0]] = (en.strip(), vi.strip())
    return out


def group_names(fam, node, nodes):
    """(Vietnamese name, source) of a family row."""
    if node and node in nodes:
        return nodes[node][1], f"{TREE} (node {node})"
    if fam == "10" and "109000" in nodes:
        return nodes["109000"][1], f"{TREE} (node 109000, the installation kit); conventions.md section 6 (family 10)"
    if fam in FAMILY_VI:
        return FAMILY_VI[fam], f"v2/00-Control/conventions.md section 6 (family {fam}; Vietnamese by the control pack)"
    return "", f"v2/00-Control/conventions.md section 6 (family {fam})"


def master_rows(parts, register, nodes=None):
    nodes = node_names() if nodes is None else nodes
    out = []
    pod_mass = sum((r["qty_per_pod"] or 0) * (r["mass_each_kg"] or 0) for r in parts if r["make_buy"] in ("make", "buy"))
    out.append({"level": 0, "row_type": "pod", "group": "POD", "part_number": "100000", "name": "POD - SPACESHIP",
                "name_vi": nodes.get("100000", ("", ""))[1],
                "qty_per_pod": 1.0, "qty_status": "source (assembly tree)", "mass_total_kg": pod_mass,
                "mass_status": "calculation (sum of the listed parts; assemblies with no list count 0)",
                "source_file": f"{TREE} (node 100000)"})
    for fam, node, gname, team in FAMILIES:
        members = sorted((r for r in parts if family_of(r["part_number"]) == fam), key=lambda r: (r["part_number"], r["source_file"]))
        reg_items = [i for i in register if family_of(i["part_number"]) == fam]
        gmass = sum((r["qty_per_pod"] or 0) * (r["mass_each_kg"] or 0) for r in members if r["make_buy"] in ("make", "buy"))
        gvi, gsrc = group_names(fam, node, nodes)
        out.append({"level": 1, "row_type": "assembly", "group": gname, "part_number": node, "name": gname,
                    "name_vi": gvi, "source_file": gsrc,
                    "qty_per_pod": 1.0 if node else None, "qty_status": "source (assembly tree)" if node else "",
                    "mass_total_kg": gmass, "mass_status": "calculation (sum of its listed parts)", "team": team,
                    "note": "" if members else "no parts listed yet"})
        own = [r for r in members if node and r["part_number"] == node]
        if own:
            out[-1]["note"] = f"the team's own total: {fmt(own[0]['mass_each_kg'])} kg ({own[0]['mass_status']})"
        for r in members:
            if node and r["part_number"] == node:
                continue
            total = (r["qty_per_pod"] or 0) * r["mass_each_kg"] if r["mass_each_kg"] is not None and r["make_buy"] != "assembly" else None
            out.append({"level": 2, "row_type": "subassembly" if r["make_buy"] == "assembly" else "part", "group": gname,
                        **{k: r[k] for k in ("part_number", "name", "name_vi", "qty_per_pod", "qty_status", "material", "finish",
                                             "mass_each_kg", "mass_status", "make_buy", "process", "process_status", "team",
                                             "source_file", "note")},
                        "mass_total_kg": total, "product_status": r["product_status"],
                        "register_id": next((i["id"] for i in register if i["part_number"] and i["part_number"] == r["part_number"]), "")})
        for a in ALLOCATED:
            if family_of(a["part_number"]) == fam and a["status"] == "ALLOCATED" \
                    and not any(r["part_number"] == a["part_number"] for r in parts):
                out.append({"level": 2, "row_type": "allocated number", "group": gname, "part_number": a["part_number"],
                            "name": a["name"], "name_vi": a["name_vi"], "qty_per_pod": a["qty_per_pod"],
                            "qty_status": "source (the team's list)",
                            "make_buy": "make" if a["kind"] == "MP" else "buy" if a["kind"] == "PI" else "assembly",
                            "team": a["team"], "source_file": a["source_file"],
                            "note": f"given out by the master BOM (D-120), not in any parts list yet; part of {a['parent']}: {a['basis']}"})
        for i in reg_items:
            if not any(r["part_number"] == i["part_number"] for r in members):
                out.append({"level": 2, "row_type": "hardware (register only)", "group": gname, "part_number": i["part_number"],
                            "name": i["name"], "register_id": i["id"], "qty_per_pod": i["qty_per_pod"], "mass_each_kg": i["mass_each_kg"],
                            "make_buy": "buy", "team": "Joints register", "source_file": i["source_file"],
                            "note": "in the joints register, not in any parts list yet"})
    unnumbered = [i for i in register if not i["part_number"]]
    if unnumbered:
        out.append({"level": 1, "row_type": "assembly", "group": "HARDWARE WITH NO NUMBER", "name": "HARDWARE IN THE JOINTS REGISTER WITH NO PART NUMBER YET",
                    "team": "Joints register", "note": "the joints register owns these numbers (D-63)"})
        for i in unnumbered:
            out.append({"level": 2, "row_type": "hardware (register only)", "group": "HARDWARE WITH NO NUMBER", "name": i["name"],
                        "register_id": i["id"], "qty_per_pod": i["qty_per_pod"], "mass_each_kg": i["mass_each_kg"],
                        "team": "Joints register", "source_file": i["source_file"], "note": "no part number yet"})
    return out


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            w.writerow([fmt(r.get(c)) if isinstance(r.get(c), float) else (r.get(c) if r.get(c) is not None else "") for c in cols])


def made_rows(parts):
    rows = [r for r in parts if r["make_buy"] == "make"]
    return sorted(rows, key=lambda r: (r["process"] or "~", r["part_number"]))


def bought_rows(parts, register):
    by = {}
    for r in parts:
        if r["make_buy"] != "buy":
            continue
        b = by.setdefault(r["part_number"], {"part_number": r["part_number"], "name": r["name"], "qty_per_pod": 0.0,
                                             "material": r["material"], "mass_total_kg": 0.0, "mass_ok": True,
                                             "product_status": set(), "hold": False, "teams": set(), "sources": set()})
        b["qty_per_pod"] += r["qty_per_pod"] or 0
        if r["mass_each_kg"] is None:
            b["mass_ok"] = False
        else:
            b["mass_total_kg"] += (r["qty_per_pod"] or 0) * r["mass_each_kg"]
        b["product_status"].add(r["product_status"])
        b["hold"] = b["hold"] or r["hold"]
        b["teams"].add(r["team"])
        b["sources"].add(r["source_file"])
    reg = {i["part_number"]: i["id"] for i in register if i["part_number"]}
    out = []
    for pn in sorted(by):
        b = by[pn]
        out.append({"part_number": pn, "name": b["name"], "qty_per_pod": b["qty_per_pod"], "qty_status": "calculation (sum of the parts lists)",
                    "material": b["material"], "mass_total_kg": b["mass_total_kg"] if b["mass_ok"] else None,
                    "mass_status": "calculation (qty x mass each)" if b["mass_ok"] else "missing for at least one use",
                    "hardware": "yes" if family_of(pn) not in NOT_HARDWARE else "no (team-numbered family)",
                    "register_id": reg.get(pn, ""), "product_status": "HOLD" if b["hold"] else "; ".join(sorted(s for s in b["product_status"] if s)),
                    "team": ", ".join(sorted(b["teams"])), "source_file": "; ".join(sorted(b["sources"]))})
    return out


def report(parts, skipped, register, reg_where, fails, missing, sources, refs):
    lines = ["# Master BOM check: Spaceship (FocusPod v2)", "",
             "| Doc code | Revision | Status | Date | Owner |", "|---|---|---|---|---|",
             f"| V2-BOM-002 | {REV} | DRAFT, written by `build_master_bom.py` | 2026-10-31 | Control pack |", "",
             "Read from: " + (", ".join(f"`{r}`" for r in refs) if refs else "this working tree") + ".", ""]
    n_parts = sum(r["make_buy"] in ("make", "buy") for r in parts)
    mass = sum((r["qty_per_pod"] or 0) * (r["mass_each_kg"] or 0) for r in parts if r["make_buy"] in ("make", "buy"))
    lines += [f"**Result: {'FAIL' if fails else 'OK'}.** {len(fails)} failure(s) on the five rules; "
              f"{n_parts} part lines ({sum(r['make_buy'] == 'make' for r in parts)} made, {sum(r['make_buy'] == 'buy' for r in parts)} bought, "
              f"{sum(r['hold'] for r in parts)} on HOLD) and {sum(r['make_buy'] == 'assembly' for r in parts)} sub-assembly lines from "
              f"{len([p for p in sources if p not in (REGISTER, ALLOCATION)]) - len(skipped)} parts list(s); {len(register)} hardware items in the joints register "
              f"({sum(1 for i in register if i['part_number'])} with a part number). "
              f"Listed parts weigh {mass:.1f} kg per pod (calculation: quantity x mass each; assemblies with no list count 0, so this is not the pod's weight).", ""]
    lines += ["## Files read", ""]
    for p in sorted(sources):
        lines.append(f"- `{p}` @ {sources[p][1]}" + (" (skipped: " + next(s[2] for s in skipped if s[0] == p) + ")" if any(s[0] == p for s in skipped) else ""))
    if not sources:
        lines.append("- none")
    fell = fell_back_lines(keep=wanted)
    if fell:
        lines += ["", "Read from main although a branch changed them, because main changed them later:", ""]
        lines += [f"- {x}" for x in fell]
    lines += ["", "## Failures", ""]
    lines += [f"- {f}" for f in fails] or ["- none"]
    lines += ["", "## Missing or on HOLD, per team", ""]
    order = [t for t in EXPECTED_FOLDERS] + ["WALL and CEILING", "Joints register"]
    for team in order + sorted(t for t in missing if t not in order):
        if team in missing:
            lines.append(f"**{team}**")
            lines += [f"- {m}" for m in missing[team]]
            lines.append("")
    if RESERVED_SEEN:
        lines += ["## Reserved air spaces, not counted (D-105)", "",
                  "Rows typed reserved air space in another team's block: the part is AIR's and is counted once, in AIR's list.", ""]
        lines += [f"- {pn} {name} in `{path}` @ {where}" for pn, name, path, where in RESERVED_SEEN]
        lines.append("")
    if ALLOCATED:
        uses = allocation_uses(parts)
        free = [a for a in ALLOCATED if a["status"] == "ALLOCATED" and a["part_number"] not in uses]
        cancelled = [a for a in ALLOCATED if a["status"] == "CANCELLED"]
        lines += ["## Numbers given out by the master BOM (D-120)", "",
                  f"From `{ALLOCATION}`: {len(ALLOCATED)} numbers, {len(free)} not in a team's list yet, "
                  f"{len(uses)} in use, {len(cancelled)} cancelled. Each is for one part in its team's list; a team that "
                  "finds two of them identical in form, fit and function uses the lower number for both and asks for the "
                  "other to be cancelled. A cancelled number is never reused.", "",
                  "| Number | Name | Part of | Qty per pod | Status |", "|---|---|---|---:|---|"]
        for a in ALLOCATED:
            state = "in use" if a["part_number"] in uses else a["status"]
            lines.append(f"| {a['part_number']} | {a['name']} | {a['parent']} | {fmt(a['qty_per_pod'])} | {state} |")
        lines.append("")
    lines += ["## Rules", "",
              "Fails: no part number; one number for two different items; no mass; a hardware item (any bought item except AIR 61, ELECTRICAL 71 and PACKAGING 91) with no joints-register row (D-63); a reserved old number (D-28); an allocated number that is badly formed, outside its band, allocated twice, used for a different item, or used after it was cancelled (D-120).",
              "Listed as missing, without failing: no parts list yet, no quantity, make or buy not stated, a metal part with no finish (D-79, D-67), a made part with no process, a HOLD item, a register item with no part number.", ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ref", action="append", default=[], help="git ref to read the files from; repeat for several")
    ap.add_argument("--out", default=str(HERE), help="output folder")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    sources = load_sources(a.ref)
    parts, skipped, register, reg_where = build(sources)
    read_paths = [p for p in sources if p not in (REGISTER, ALLOCATION) and p not in {s[0] for s in skipped}]
    fails, missing = check(parts, register, reg_where, read_paths)
    if not a.no_write:
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        write_csv(out / f"100000_{REV}_POD-MASTER_BOM.csv", MASTER_COLS, master_rows(parts, register, node_names(a.ref)))
        write_csv(out / f"100000_{REV}_POD-MADE-PARTS-BY-PROCESS_BOM.csv",
                  ["process", "process_status", "part_number", "name", "qty_per_pod", "material", "finish", "mass_each_kg", "mass_status", "team", "source_file"],
                  made_rows(parts))
        write_csv(out / f"100000_{REV}_POD-BOUGHT-PARTS_BOM.csv",
                  ["part_number", "name", "qty_per_pod", "qty_status", "material", "mass_total_kg", "mass_status", "hardware", "register_id", "product_status", "team", "source_file"],
                  bought_rows(parts, register))
        (out / "BOM-CHECK.md").write_text(report(parts, skipped, register, reg_where, fails, missing, sources, a.ref), encoding="utf-8")
    print(f"master BOM: {len(parts)} lines from {len([p for p in sources if p not in (REGISTER, ALLOCATION)]) - len(skipped)} parts list(s), "
          f"{len(register)} register hardware items; {sum(len(v) for v in missing.values())} missing items in {len(missing)} teams")
    print_fell_back()
    if fails:
        print("\nFAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("\nOK: no part without a number or a mass, no duplicate number, no unregistered hardware")
    return 0


if __name__ == "__main__":
    sys.exit(main())
