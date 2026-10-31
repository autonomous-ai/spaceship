#!/usr/bin/env python3
"""Builds the release checklist of Spaceship (FocusPod v2): what stands between the design and a
manufacturing release, part by part.

Doc code V2-CTL-010, revision P01. Standard library only.

Reads, from this working tree or from git refs (the master BOM's rule: a later ref adds only the files its
own branch changed since it left the first):
  - every team's parts list and the joints register, through v2/04-BOM/build_master_bom.py;
  - the files in v2/01-CAD-Native, v2/02-Drawings and v2/03-Manufacturing named
    PARTNO_REV_NAME_DOCTYPE.ext (conventions.md section 7);
  - the FAI plan, v2/06-Verification/fai-plan.md, always from this working tree (the control pack owns it):
    which characteristics apply to which numbers, and which test accepts each bought part;
  - the tests: the wall and door sample's test plan, the joints register's tests, the FAI plan's checks.
Writes v2/00-Control/release-checklist.md, or --out.

A made part or assembly is done when it has native CAD (its own file or its assembly's), STEP, a DXF if it
is sheet or cut from sheet (a cut list if it is tube), its own drawing, a BOM row with its mass and, for
metal, its finish, and FAI characteristics. D-89, read as the mechanical check reads it (tools/checks/c_drawings.py):
a part counts as drawn when a drawing whose text says TABULATED lists its number (same family and kind); a plain
felt or fill rectangle counts as drawn, and cut, when a cut-list or parts-list row gives its number, size,
material and tolerance; another soft good (foam, gasket, seal, tape, by the name's head noun) counts as drawn
by its DXF, or, as a plain strip or rectangle, by such a row that also gives its thickness. A part found only in
the folders has no BOM row. When the
drawing is a made part's only gap and the Mac's screen is locked, the part is blocked by the locked screen:
the drawing start needs it unlocked (D-84). Otherwise a part with a gap is open.
A bought part is done when it has a joints-register row (hardware only, D-63), a maker and SKU, and a
test. Its product is on HOLD when the joints register says so (register numbers), or its parts list does.

Usage:  python3 v2/00-Control/build_release_checklist.py [--open-prs | --ref REF ...] [--out FILE]
                [--screen auto|locked|unlocked]
--open-prs fetches origin and reads origin/main plus every open PR's branch that changes parts.
Nothing here releases anything: it lists what is missing (guideline milestone 4; REQ-DOC-02).
"""
import argparse
import csv
import datetime
import importlib.util
import io
import json
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TREES = ["v2/01-CAD-Native", "v2/02-Drawings", "v2/03-Manufacturing"]
FAI = "v2/06-Verification/fai-plan.md"
TEST_PLAN = "v2/06-Samples/wall-door-sample/test-plan.md"
FILE_RE = re.compile(r"^(\d{6})_([PR]\d\d)_([A-Z0-9-]+?)_(CAD|STEP|DXF|DWG|BOM|SPEC|CALC|FAI|INS|PKG|IMG)\.(\w+)$")
SHEET = re.compile(r"\bACP\b|sheet|galvani[sz]ed|DX51D|felt|\bfill\b|foam|\bply\b|plywood|glass|mesh|laminate", re.I)
TUBE = re.compile(r"\btube\b|\d+\s*x\s*\d+\s*x\s*\d|profile|6063|\bframe\b", re.I)
METAL = re.compile(r"alumin|steel|zinc", re.I)
COATED = re.compile(r"galvani|\+Z\b|stainless|\bA2\b|\bzinc\b|plated|anodi[sz]ed|mill finish|powder|painted", re.I)
SKU = re.compile(r"\b(?=[A-Z0-9.\-]*\d)(?=[A-Z0-9.\-]*[A-Z])[A-Z0-9][A-Z0-9.\-]{3,}\b|\b(?:ISO|EN|DIN) \d{3,}")
PRODUCT_HOLD = re.compile(r"\b(?:part|strip|product|system)\b[^;]*\bHOLD", re.I)
PRODUCT_NAMED = re.compile(r"\b(?:part|product|system)\b[^;]*\b(?:DECIDED|source)\b", re.I)
TEST_ID = re.compile(r"\b(?:T\d\d|J-T\d+|F-\d\d)\b")
FOLDER_TEAM = {"base": "BASE", "wall": "WALL", "front": "FRONT", "ceiling": "CEILING", "electrical": "ELECTRICAL",
               "air": "CEILING (builds AIR, D-80)", "interior": "CEILING (builds INTERIOR, D-80)"}
BLOCKED = "blocked: only the drawing, which waits for the unlocked screen (D-84)"
SOFT_HEADS = re.compile(r"(?:[A-Z]+-)*(?:FILLS?|FELTS?|FOAMS?|GASKETS?|SEALS?|TAPES?)")
FEATURES = re.compile(r"pocket|notch|hole|slot|cut-?out|chamfer|radius|radii|bevel", re.I)
TABULATED = re.compile(r"\bTABULATED\b", re.I)


def load_bom():
    spec = importlib.util.spec_from_file_location("bom", ROOT / "v2/04-BOM/build_master_bom.py")
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    mod.ROOT = ROOT
    return mod


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def open_pr_refs(bom):
    """origin/main, then each open PR's branch that changes a parts list, the joints register or a part's file,
    oldest first so a newer branch wins for the same path. Also returns {ref: label}."""
    git("fetch", "-q", "origin")
    out = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "100", "--json", "number,headRefName"],
                         cwd=ROOT, check=True, capture_output=True, text=True).stdout
    found = []
    for p in json.loads(out or "[]"):
        ref = f"origin/{p['headRefName']}"
        try:
            mb = git("merge-base", "origin/main", ref).strip()
        except subprocess.CalledProcessError:
            continue  # the branch is gone
        changed = git("diff", "--name-only", mb, ref, "--", *TREES, "v2/07-Packaging", bom.REGISTER).split()
        if any(c.endswith("_BOM.csv") or c == bom.REGISTER or FILE_RE.match(c.rsplit("/", 1)[-1]) for c in changed):
            found.append((int(git("log", "-1", "--format=%ct", ref).strip() or 0), ref, f"PR #{p['number']}"))
    found.sort()
    labels = {"origin/main": "main", **{ref: label for _, ref, label in found}}
    return ["origin/main"] + [ref for _, ref, _ in found], labels


def list_files(refs):
    """{path: where} for the three trees: the working tree, or the first ref plus each later ref's own changes."""
    if not refs:
        out = {}
        for t in TREES:
            base = ROOT / t
            if base.exists():
                out.update({p.relative_to(ROOT).as_posix(): "working tree" for p in base.rglob("*") if p.is_file()})
        return out
    files = {f: refs[0] for f in git("ls-tree", "-r", "--name-only", refs[0], "--", *TREES).split()}
    for ref in refs[1:]:
        mb = git("merge-base", refs[0], ref).strip()
        files.update({f: ref for f in git("diff", "--name-only", "--diff-filter=AM", mb, ref, "--", *TREES).split()})
    return files


def read_text(path, refs, local_first=False):
    p = ROOT / path
    if (local_first or not refs) and p.exists():
        return p.read_text(encoding="utf-8")
    for ref in reversed(refs):
        try:
            return git("show", f"{ref}:{path}")
        except subprocess.CalledProcessError:
            continue
    return ""


def local_copy(path, where, refs, tmp):
    """A file on disk: this working tree's, or the bytes from the ref that gave it, written under tmp."""
    if not refs or where == "working tree":
        return ROOT / path
    out = Path(tmp) / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(subprocess.run(["git", "-C", str(ROOT), "show", f"{where}:{path}"], check=True, capture_output=True).stdout)
    return out


def screen_state(choice):
    if choice in ("locked", "unlocked"):
        return choice
    try:
        out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=10).stdout
        users = plistlib.loads(out).get("IOConsoleUsers", [])
        return "locked" if any(u.get("CGSSessionScreenIsLocked") for u in users) else "unlocked"
    except Exception:
        return "unknown"


def patterns(cell):
    return [re.compile(p.replace("x", r"\d")) for p in re.findall(r"`([0-9x]{6})`", cell)]


def fai_plan(text, bom):
    """(characteristics [(K-id, patterns)], checks [(F-id, text)], accept [(patterns, [test ids])])."""
    chars, checks, accept = [], [], []
    for hdr, cells in bom.table_rows(text):
        if re.fullmatch(r"K-[A-Z]\d\d", cells[0]) and len(cells) > 1:
            chars.append((cells[0], patterns(cells[1])))
        elif re.fullmatch(r"F-\d\d", cells[0]):
            checks.append((cells[0], " ".join(cells)))
        elif hdr and hdr[0].strip().lower() == "applies to" and len(cells) > 2:
            accept.append((patterns(cells[0]), TEST_ID.findall(cells[2])))
    return chars, checks, accept


def test_rows(sample_text, register_text, checks, bom):
    rows = []
    for text in (sample_text, register_text):
        for hdr, cells in bom.table_rows(text):
            if re.fullmatch(r"T\d\d|J-T\d+", cells[0]):
                rows.append((cells[0], " ".join(cells)))
    return rows + checks


def register_products(register_text, bom):
    """{part number: 'hold' | 'named' | 'defer'} from the status cell of the joints register's part-number table:
    its part, strip, product or system on HOLD; named (DECIDED or from a source); or left to the parts list."""
    status = {}
    for hdr, cells in bom.table_rows(register_text):
        if not cells or not re.fullmatch(r"H-\d+\w*", cells[0]):
            continue
        m = re.search(r"\*\*(\d{6})\*\*", " ".join(cells[1:2]))
        if m:
            last = cells[-1]
            status[m.group(1)] = "hold" if PRODUCT_HOLD.search(last) else ("named" if PRODUCT_NAMED.search(last) else "defer")
    return status


def files_by_pn(paths):
    by = {}
    for p in paths:
        m = FILE_RE.match(p.rsplit("/", 1)[-1])
        if m:
            by.setdefault(m.group(1), {}).setdefault(m.group(4), []).append(p)
    return by


def head_noun(name):
    """The last word of a part name's function field, as the mechanical check reads it (tools/checks/common.py):
    'BASE - SEAL HOLDER - LH' gives HOLDER, 'LINING - FILL - CEILING - BAY A' gives FILL."""
    fields = [f.strip() for f in (name or "").upper().split(" - ")]
    func = fields[1] if len(fields) > 1 else fields[0]
    words = re.findall(r"[A-Z][A-Z-]*", func)
    return words[-1] if words else ""


def soft_kind(name):
    """'felt or fill', 'soft' (foam, gasket, seal, tape) or '' by the name's head noun (D-89)."""
    h = head_noun(name)
    if not SOFT_HEADS.fullmatch(h):
        return ""
    return "felt or fill" if h.rstrip("S").endswith(("FELT", "FILL")) else "soft"


def is_cut_list(path):
    """A cut list, as the mechanical check reads one: a .csv with "cut" in its name, in the drawing or
    manufacturing folders."""
    name = path.rsplit("/", 1)[-1].lower()
    return name.endswith(".csv") and "cut" in name and path.startswith(("v2/02-Drawings/", "v2/03-Manufacturing/"))


def kind_of(pn):
    n = int(pn[2:])
    return "assembly" if n <= 999 else ("part" if n <= 7999 else "other")


def pdf_text(path):
    """A PDF's text: PyMuPDF if it is installed, else pdftotext; None when neither is there."""
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass
    exe = shutil.which("pdftotext")
    if exe:
        return subprocess.run([exe, "-layout", str(path), "-"], capture_output=True, text=True, timeout=60).stdout
    return None


def tabulated_cover(by_pn, text_of):
    """D-89: {number: drawing number} for every number that a tabulated drawing lists. A tabulated drawing's
    text says TABULATED; it covers the other numbers of its own family and kind in its text, so a mating part
    named in a note doesn't count (as the mechanical check reads it)."""
    cover = {}
    for own, kinds in by_pn.items():
        if kind_of(own) not in ("part", "assembly"):
            continue
        for path in kinds.get("DWG", []):
            text = text_of(path) if path.lower().endswith(".pdf") else None
            if not text or not TABULATED.search(text):
                continue
            for n in sorted(set(re.findall(r"(?<!\d)(\d{6})(?!\d)", text))):
                if n != own and n[:2] == own[:2] and kind_of(n) == kind_of(own):
                    cover.setdefault(n, own)
    return cover


def cut_rows(cut_texts):
    """{number: [(row, path)]}: the cut-list rows with a cell that is exactly the number."""
    out = {}
    for path, text in cut_texts.items():
        try:
            for row in csv.DictReader(io.StringIO(text)):
                cells = {(k or "").strip(): (v or "").strip() for k, v in row.items() if isinstance(k, str) and isinstance(v, str)}
                for n in {v for v in cells.values() if re.fullmatch(r"\d{6}", v)}:
                    out.setdefault(n, []).append((cells, path))
        except csv.Error:
            continue
    return out


def cut_list_lacks(rows, thickness=False):
    """What the best row (a cut list's or a parts list's) lacks of size, material and tolerance, and, for soft
    goods other than felt and fill, thickness (D-89; the mechanical check's columns); None when no row has the
    number."""
    best = None
    for cells, _path in rows:
        def has(pattern):
            return [v for k, v in cells.items() if re.search(pattern, k, re.I) and v]
        sizes = has(r"size|dimension|length|width|thick|^[lwt]_?mm$")
        thick = any(re.search(r"\d", v) for v in has(r"thick|^t_?mm$")) or any(
            len(re.findall(r"\d+(?:\.\d+)?", v)) >= 3 and re.search(r"[x×]", v, re.I) for v in sizes)
        lacks = [n for n, ok in (
            ("size", any(re.search(r"\d", v) for v in sizes)),
            ("thickness", thick or not thickness),
            ("material", bool(has(r"material|grade"))),
            ("tolerance", bool(has(r"tol")) or any(re.search(r"±|\+/-", v) for v in cells.values()))) if not ok]
        if FEATURES.search(" ".join(cells.values())):
            lacks.append("a plain rectangle (it names pockets, notches or holes)")
        if best is None or len(lacks) < len(best):
            best = lacks
    return best


def where_of(r, labels):
    where = r["source_file"].split(" @ ", 1)[-1]
    ref = where.split(" (", 1)[0]
    return labels.get(ref, "this tree" if ref == "working tree" else ref)


def check_parts(parts, register, by_pn, paths, fai, tests, reg_status, screen, bom, labels, cut_texts, tab_cover=None):
    chars, _, accept = fai
    tab_cover = tab_cover or {}
    by_cut_row = cut_rows(cut_texts)
    reg = {i["part_number"]: i for i in register if i["part_number"]}
    cut_lists = [p for p in paths if is_cut_list(p)]
    made, bought, last_unit, seen = [], [], {}, {}
    for r in parts:
        pn, src = r["part_number"], r["source_file"].split(" @ ")[0]
        unit = src.rsplit("/", 1)[-1][:6]
        if r["make_buy"] == "assembly":
            last_unit[src] = pn
        key = (r["team"], pn or r["name"])
        if key in seen:  # the same part again in this team's lists: one line, every source named
            seen[key]["from"].add(where_of(r, labels))
            continue
        holders = [h for h in (pn, last_unit.get(src, ""), unit) if h]
        if r["make_buy"] in ("make", "assembly"):
            text = " ".join([r["material"], r["process"], r["name"]])
            cad = any(by_pn.get(h, {}).get("CAD") for h in holders)
            step = any(by_pn.get(h, {}).get("STEP") for h in holders)
            soft = soft_kind(r["name"]) if r["make_buy"] != "assembly" else ""
            by_cut = bool(soft) and cut_list_lacks(by_cut_row.get(pn, []), thickness=soft == "soft") == []
            if r["make_buy"] == "assembly":
                flat = "n/a"
            elif by_cut:
                flat = "cut list"
            elif SHEET.search(text):
                flat = "yes" if by_pn.get(pn, {}).get("DXF") else "no"
            elif TUBE.search(text):
                team_dir = src.rsplit("/", 1)[0] + "/"
                listed = any(c.startswith(team_dir) and pn in cut_texts.get(c, "") for c in cut_lists)
                flat = "yes" if listed or r.get("cut_rows") else "no"
            else:
                flat = "n/a"
            if by_pn.get(pn, {}).get("DWG"):
                dwg = "yes"
            elif pn in tab_cover:
                dwg = f"on {tab_cover[pn]}, tabulated (D-89)"
            elif by_cut:
                dwg = "cut list (D-89)"
            elif soft == "soft" and by_pn.get(pn, {}).get("DXF"):
                dwg = "DXF (D-89)"
            else:
                dwg = "no"
            mass = r["mass_each_kg"] is not None or r["make_buy"] == "assembly"
            metal = METAL.search(r["material"] or "")
            finish = "n/a" if not metal or r["make_buy"] == "assembly" else (
                "yes" if r["finish"] or COATED.search(r["material"]) else "no")
            ids = [i for i, pats in chars if any(p.fullmatch(pn) for p in pats)]
            gaps = [n for n, ok in (("CAD", cad), ("STEP", step), ("DXF or cut list", flat != "no"), ("drawing", not dwg.startswith("no")),
                                    ("mass", mass), ("finish", finish != "no"), ("FAI", bool(ids))) if not ok]
            line = {**r, "bom_row": True, "cad": cad, "step": step, "flat": flat, "dwg": dwg, "mass_ok": mass,
                    "finish_ok": finish, "fai": ids, "gaps": gaps, "from": {where_of(r, labels)}}
            line["state"] = state_of(gaps, screen)
            made.append(line)
            seen[key] = line
        elif r["make_buy"] == "buy":
            hw = bom.family_of(pn) not in bom.NOT_HARDWARE
            in_reg = (pn in reg) if hw else None
            given = reg_status.get(pn, "defer")  # the register wins where it states the product (D-63)
            hold = given == "hold" or (given == "defer" and bool(r["hold"]))
            words = " ".join([r["name"], r["material"]])
            sku = "HOLD" if hold else ("yes" if given == "named" or SKU.search(words) else "no")
            rid = reg.get(pn, {}).get("id", "")
            found = {t for pats, ids in accept if any(p.fullmatch(pn) for p in pats) for t in ids}
            found |= {tid for tid, t in tests if pn and (re.search(rf"\b{pn}\b", t) or (rid and re.search(rf"\b{rid}\b", t)))}
            gaps = [n for n, ok in (("register row", in_reg is not False), ("maker and SKU", sku == "yes"),
                                    ("test", bool(found))) if not ok]
            state = "HOLD" if sku == "HOLD" else ("done" if not gaps else "open: " + ", ".join(gaps))
            line = {**r, "in_reg": in_reg, "rid": rid, "sku": sku, "tests": sorted(found), "state": state,
                    "from": {where_of(r, labels)}}
            bought.append(line)
            seen[key] = line
    return made, bought


def state_of(gaps, screen):
    if not gaps:
        return "done"
    if gaps == ["drawing"] and screen == "locked":
        return BLOCKED
    return "open: " + ", ".join(gaps)


def files_only(by_pn, parts, files, labels, screen):
    """Made parts found in the folders whose number no parts list carries: no BOM row."""
    listed = {r["part_number"] for r in parts}
    out = []
    for pn, kinds in sorted(by_pn.items()):
        if pn in listed or pn == "100000" or not ({"CAD", "STEP", "DXF", "DWG"} & set(kinds)):
            continue
        some = next(p for ps in kinds.values() for p in ps)
        team = next((FOLDER_TEAM[s] for s in some.split("/") if s in FOLDER_TEAM), "other")
        names = {re.sub(FILE_RE, r"\3", p.rsplit("/", 1)[-1]) for ps in kinds.values() for p in ps}
        gaps = ["BOM row"] + [k for k, n in (("CAD", "CAD"), ("STEP", "STEP"), ("drawing", "DWG")) if not kinds.get(n)]
        out.append({"part_number": pn, "name": sorted(names)[0].replace("-", " "), "team": team, "bom_row": False,
                    "cad": bool(kinds.get("CAD")), "step": bool(kinds.get("STEP")), "flat": "yes" if kinds.get("DXF") else "—",
                    "dwg": bool(kinds.get("DWG")), "mass_ok": False, "finish_ok": "—", "fai": [], "gaps": gaps,
                    "state": state_of(gaps, screen),
                    "from": {labels.get(files[p], "this tree" if files[p] == "working tree" else files[p])
                             for ps in kinds.values() for p in ps}})
    return out


def yn(v):
    return "yes" if v is True else ("no" if v is False else str(v))


def counts(lines):
    return (sum(r["state"] == "done" for r in lines), sum(r["state"].startswith("open") for r in lines),
            sum(r["state"].startswith("blocked") for r in lines), sum(r["state"] == "HOLD" for r in lines))


def render(made, bought, register, no_list, ref_note, screen, files, fai, today):
    chars, checks, accept = fai
    out = ["# Release checklist: Spaceship (FocusPod v2)", "",
           "| Doc code | Revision | Status | Date | Owner |", "|---|---|---|---|---|",
           f"| V2-CTL-009 | P01 | DRAFT, written by `build_release_checklist.py` | {today} | Control pack |", "",
           "What stands between the design and a manufacturing release, part by part. Nothing here is released "
           "(guideline milestone 4, REQ-DOC-02). Re-run it whenever parts merge.", "",
           f"Read from: {ref_note}. The Mac's screen at run time: **{screen}**. {len(files)} files in the CAD, drawing "
           f"and manufacturing folders; the FAI plan's {len(chars)} characteristics, {len(checks)} functional checks and "
           f"{len(accept)} bought-part test lines.", "",
           "**Done**: nothing missing from the columns below; a test counts once it is named, and its result belongs in the FAI plan. "
           "**Open**: something missing that can be done now. **Blocked**: only the drawing is "
           "missing and the screen is locked; the drawing start needs it unlocked (D-84). **HOLD**: the product isn't named yet.", "",
           "## Totals per team", "",
           "| Team | Made: done | Made: open | Made: blocked by the locked screen | Bought: done | Bought: open | Bought: HOLD |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    teams = sorted({r["team"] for r in made + bought} | set(no_list))
    for t in teams:
        m = [r for r in made if r["team"] == t]
        b = [r for r in bought if r["team"] == t]
        if not m and not b:
            out.append(f"| {t} | — | — | — | — | — | — |")
            continue
        md, mo, mb, _ = counts(m)
        bd, bo, _, bh = counts(b)
        out.append(f"| {t} | {md} | {mo} | {mb} | {bd} | {bo} | {bh} |")
    um = list({r["part_number"] or r["name"]: r for r in made}.values())
    ub = list({r["part_number"] or r["name"]: r for r in bought}.values())
    md, mo, mb, _ = counts(um)
    bd, bo, _, bh = counts(ub)
    out.append(f"| **All, each number once** | {md} | {mo} | {mb} | {bd} | {bo} | {bh} |")
    if no_list:
        out += ["", "No parts list yet: " + ", ".join(sorted(no_list)) + "."]
    only_dwg = sum(r["gaps"] == ["drawing"] for r in um)
    no_dwg = sum("drawing" in r["gaps"] for r in um)
    out += ["", f"{no_dwg} of the {len(um)} made numbers have no drawing yet; for {only_dwg} of them the drawing is the only "
                f"gap, so {'they wait for the unlocked screen' if screen == 'locked' else 'their drawings can start now'} (D-84)."]
    gap_count = {}
    for r in um:
        for g in r["gaps"]:
            gap_count[g] = gap_count.get(g, 0) + 1
    if gap_count:
        out += ["", "What the open made numbers miss: " + ", ".join(f"{g} {n}" for g, n in
                                                                  sorted(gap_count.items(), key=lambda x: -x[1])) + "."]
    out += ["", "## Made parts and assemblies", ""]
    for t in teams:
        m = [r for r in made if r["team"] == t]
        if not m:
            continue
        out += [f"### {t}", "", "| Part | Name | From | BOM row | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in m:
            out.append(f"| {r['part_number'] or '(no number)'} | {r['name']} | {', '.join(sorted(r['from']))} | {yn(r['bom_row'])} | "
                       f"{yn(r['cad'])} | {yn(r['step'])} | {r['flat']} | {yn(r['dwg'])} | {yn(r['mass_ok'])} | {r['finish_ok']} | "
                       f"{', '.join(r['fai']) or 'no'} | {r['state']} |")
        out.append("")
    out += ["## Bought parts", ""]
    for t in teams:
        b = [r for r in bought if r["team"] == t]
        if not b:
            continue
        out += [f"### {t}", "", "| Part | Name | From | Register | Maker and SKU | Test | State |", "|---|---|---|---|---|---|---|"]
        for r in b:
            reg = "n/a (team-numbered)" if r["in_reg"] is None else ((r["rid"] or "yes") if r["in_reg"] else "no")
            out.append(f"| {r['part_number'] or '(no number)'} | {r['name']} | {', '.join(sorted(r['from']))} | {reg} | {r['sku']} | "
                       f"{', '.join(r['tests']) or 'no'} | {r['state']} |")
        out.append("")
    used = {r["part_number"] for r in made + bought}
    spare = [i for i in register if i["part_number"] and i["part_number"] not in used]
    if spare:
        out += ["## Joints-register items no parts list uses yet", "", "| Part | Register | Name |", "|---|---|---|"]
        out += [f"| {i['part_number']} | {i['id']} | {i['name']} |" for i in spare]
        out.append("")
    out += ["## How it's built", "",
            "`python3 v2/00-Control/build_release_checklist.py --open-prs` reads origin/main and every open PR that changes "
            "parts, through the master BOM's reader (a later branch adds only the files it changed), the files named "
            "`PARTNO_REV_NAME_DOCTYPE.ext` in `v2/01-CAD-Native`, `v2/02-Drawings` and `v2/03-Manufacturing`, the FAI plan "
            "(`v2/06-Verification/fai-plan.md`) and the test plans. Without `--open-prs` it reads this working tree.", "",
            "- A part's CAD and STEP may sit in its assembly's file; its DXF and drawing carry its own number, except as D-89 allows, "
            "read as the mechanical check reads them: a drawing whose text says TABULATED covers the other numbers of its family and kind "
            "that it lists; a felt or fill piece needs no drawing or DXF when a cut-list or parts-list row gives its number, size, material "
            "and tolerance and names no pockets, notches or holes (the mechanical check also counts the holes and faces in its STEP); "
            "another soft good cut from sheet or roll (foam, gasket, seal or tape, by the name's last word in its function field) needs no "
            "drawing when its DXF gives the outline, or, as a plain strip or rectangle, when such a row also gives its thickness.",
            "- A DXF is asked of sheet, felt, fill, foam, ply and glass parts; a cut list (or the list's cut rows) of tube parts.",
            "- Finish is asked of metal parts: a `finish` column, or a coating named in the material.",
            "- FAI: the plan's characteristics whose patterns match the number. Bought parts: the plan's section H, or a test "
            "that names the number or its register ID.",
            "- A register number's product status comes from the joints register: on HOLD, or named (DECIDED or from a source), "
            "or left to the parts list; a team number's from its parts list.", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the release checklist")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--open-prs", action="store_true", help="read origin/main and the open PRs' branches")
    ap.add_argument("--out", default=str(HERE / "release-checklist.md"))
    ap.add_argument("--screen", default="auto", choices=["auto", "locked", "unlocked"])
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args(argv)
    bom = load_bom()
    refs, labels = (open_pr_refs(bom) if a.open_prs else (a.ref, {}))
    if refs:
        shas = {r: git("rev-parse", "--short", r).strip() for r in refs}
        ref_note = ", ".join(f"{labels.get(r, r)} ({shas[r]})" for r in refs)
    else:
        ref_note = "this working tree"
    sources = bom.load_sources(refs)
    parts, skipped, register, reg_where = bom.build(sources)
    for path, (text, _) in sources.items():  # a frame whose list carries its cut rows has its cut list
        if path.endswith("_BOM.csv") and re.search(r"^\d*,?,[^\n]*,cut,", text, re.M | re.I):
            for r in parts:
                if r["source_file"].startswith(path) and TUBE.search(r["material"] or ""):
                    r["cut_rows"] = True
    files = list_files(refs)
    cut_texts = {p: read_text(p, refs) for p in files  # every list a D-89 row may sit in, and the tube cut lists
                 if p.endswith(".csv") and p.startswith(("v2/02-Drawings/", "v2/03-Manufacturing/")) or "CUT-LIST" in p}
    fai = fai_plan(read_text(FAI, refs, local_first=True), bom)
    register_text = sources.get(bom.REGISTER, ("", ""))[0]
    tests = test_rows(read_text(TEST_PLAN, refs), register_text, fai[1], bom)
    screen = screen_state(a.screen)
    by_pn = files_by_pn(files)
    with tempfile.TemporaryDirectory() as tmp:
        tab_cover = tabulated_cover(by_pn, lambda path: pdf_text(local_copy(path, files[path], refs, tmp)))
    made, bought = check_parts(parts, register, by_pn, list(files), fai, tests, register_products(register_text, bom),
                               screen, bom, labels, cut_texts, tab_cover)
    made += files_only(by_pn, parts, files, labels, screen)
    listed = {r["team"] for r in parts}
    no_list = [t for t in bom.EXPECTED_FOLDERS if t not in listed and t != "Packing and Assembly"]
    Path(a.out).write_text(render(made, bought, register, no_list, ref_note, screen, files, fai, a.date), encoding="utf-8")
    done = sum(r["state"] == "done" for r in made + bought)
    print(f"release checklist: {len(made)} made lines, {len(bought)} bought lines, {done} done; screen {screen}; written to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
