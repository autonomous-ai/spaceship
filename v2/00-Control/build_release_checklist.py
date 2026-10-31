#!/usr/bin/env python3
"""Builds the release checklist of Spaceship (FocusPod v2): what stands between the design and a
manufacturing release, part by part.

Doc code V2-CTL-010, revision P01. Standard library only.

Reads, from this working tree or from git refs (same rule as the master BOM: a later ref adds only
the files its own branch changed):
  - every team's parts list and the joints register, through v2/04-BOM/build_master_bom.py;
  - the files in v2/01-CAD-Native, v2/02-Drawings and v2/03-Manufacturing, named
    PARTNO_REV_NAME_DOCTYPE.ext (conventions.md section 7);
  - the FAI plan, v2/06-Verification/fai-plan.md: which characteristics apply to which numbers;
  - the tests: the wall and door sample's test plan, the joints register's tests and the FAI plan's
    functional checks.
Writes v2/00-Control/release-checklist.md, or --out.

A made part or assembly is done when it has native CAD (its own file or its assembly's), STEP, a DXF
if it is sheet or cut (a cut list if it is tube), a drawing, a BOM row with its mass and, for metal,
its finish, and FAI characteristics. When the drawing is its only gap and the Mac's screen is locked,
it is blocked by the locked screen (D-84); otherwise it is open.
A bought part is done when it has a joints-register row (hardware only, D-63), a maker and SKU that
aren't on HOLD, and a test. HOLD items are counted apart.

Usage:  python3 v2/00-Control/build_release_checklist.py [--ref REF ...] [--out FILE]
                [--screen auto|locked|unlocked]
Nothing here releases anything: it lists what's missing (guideline milestone 4; REQ-DOC-02).
"""
import argparse
import datetime
import importlib.util
import plistlib
import re
import subprocess
import sys
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
SKU = re.compile(r"\b(?=[A-Z0-9.\-]*\d)(?=[A-Z0-9.\-]*[A-Z])[A-Z0-9][A-Z0-9.\-]{3,}\b|\bISO \d{3,}|\bEN \d{3,}")


def load_bom():
    spec = importlib.util.spec_from_file_location("bom", ROOT / "v2/04-BOM/build_master_bom.py")
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    mod.ROOT = ROOT
    return mod


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def list_files(refs):
    """Paths in the three trees: the working tree, or the first ref plus each later ref's own changes."""
    if not refs:
        out = []
        for t in TREES:
            base = ROOT / t
            if base.exists():
                out += [p.relative_to(ROOT).as_posix() for p in base.rglob("*") if p.is_file()]
        return sorted(out)
    files = set(git("ls-tree", "-r", "--name-only", refs[0], "--", *TREES).split())
    for ref in refs[1:]:
        mb = git("merge-base", refs[0], ref).strip()
        files |= set(git("diff", "--name-only", "--diff-filter=AM", mb, ref, "--", *TREES).split())
    return sorted(files)


def read_text(path, refs):
    try:
        if refs:
            for ref in reversed(refs):
                try:
                    return git("show", f"{ref}:{path}")
                except subprocess.CalledProcessError:
                    continue
            return ""
        p = ROOT / path
        return p.read_text(encoding="utf-8") if p.exists() else ""
    except Exception:
        return ""


def screen_state(choice):
    if choice in ("locked", "unlocked"):
        return choice
    try:
        out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=10).stdout
        users = plistlib.loads(out).get("IOConsoleUsers", [])
        return "locked" if any(u.get("CGSSessionScreenIsLocked") for u in users) else "unlocked"
    except Exception:
        return "unknown"


def fai_rows(text, bom):
    rows = []
    for hdr, cells in bom.table_rows(text):
        if not re.fullmatch(r"[KF]-[A-Z]?\d\d", cells[0]):
            continue
        pats = re.findall(r"`([0-9x]{6})`", cells[1]) if cells[0].startswith("K-") else []
        rows.append((cells[0], [re.compile(p.replace("x", r"\d")) for p in pats], " ".join(cells)))
    return rows


def test_rows(sample_text, register_text, fai, bom):
    rows = []
    for text in (sample_text, register_text):
        for hdr, cells in bom.table_rows(text):
            if re.fullmatch(r"T\d\d|T-\d\d|J-T\d+", cells[0]):
                rows.append((cells[0], " ".join(cells)))
    rows += [(i, t) for i, _, t in fai if i.startswith("F-")]
    return rows


def files_by_pn(paths):
    by = {}
    for p in paths:
        m = FILE_RE.match(p.rsplit("/", 1)[-1])
        if m:
            by.setdefault(m.group(1), {}).setdefault(m.group(4), []).append(p)
    return by


def check_parts(parts, register, by_pn, paths, fai, tests, screen, bom):
    reg = {i["part_number"]: i for i in register if i["part_number"]}
    cut_lists = [p for p in paths if "CUT-LIST" in p]
    made, bought, last_unit = [], [], {}
    for r in parts:
        pn, src = r["part_number"], r["source_file"].split(" @ ")[0]
        unit = src.rsplit("/", 1)[-1][:6]
        if r["make_buy"] == "assembly":
            last_unit[src] = pn
        holders = [pn, last_unit.get(src, ""), unit]
        if r["make_buy"] in ("make", "assembly"):
            text = " ".join([r["material"], r["process"], r["name"]])
            has = lambda kind: any(by_pn.get(h, {}).get(kind) for h in holders if h)  # noqa: E731
            cad, step = has("CAD"), has("STEP")
            if r["make_buy"] == "assembly":
                flat = "n/a"
            elif SHEET.search(text):
                flat = "yes" if by_pn.get(pn, {}).get("DXF") else "no"
            elif TUBE.search(text):
                team_dir = src.rsplit("/", 1)[0] + "/"
                flat = "yes" if any(c.startswith(team_dir) and pn in read_cache.get(c, "") for c in cut_lists) or r.get("cut_rows") else "no"
            else:
                flat = "n/a"
            dwg = bool(by_pn.get(pn, {}).get("DWG"))
            mass = r["mass_each_kg"] is not None or r["make_buy"] == "assembly"
            metal = METAL.search(r["material"] or "")
            finish = "n/a" if not metal or r["make_buy"] == "assembly" else ("yes" if r["finish"] or COATED.search(r["material"]) else "no")
            ids = [i for i, pats, _ in fai if any(p.fullmatch(pn) for p in pats)]
            gaps = [n for n, ok in (("CAD", cad), ("STEP", step), ("DXF or cut list", flat != "no"), ("drawing", dwg),
                                    ("mass", mass), ("finish", finish != "no"), ("FAI", bool(ids))) if not ok]
            if not gaps:
                state = "done"
            elif gaps == ["drawing"] and screen == "locked":
                state = "blocked: the drawing waits for the unlocked screen (D-84)"
            else:
                state = "open: " + ", ".join(gaps)
            made.append({**r, "cad": cad, "step": step, "flat": flat, "dwg": dwg, "mass_ok": mass, "finish_ok": finish,
                         "fai": ids, "state": state})
        elif r["make_buy"] == "buy":
            fam = pn[:2] if re.fullmatch(r"\d{6}", pn) else ""
            hw = fam not in bom.NOT_HARDWARE
            in_reg = (pn in reg) if hw else None
            words = " ".join([r["name"], r["material"]])
            sku = "HOLD" if r["hold"] else ("yes" if SKU.search(words) else "no")
            rid = reg.get(pn, {}).get("id", "")
            keys = [k for k in [pn, rid] + SKU.findall(words) if k and len(k) >= 4]
            found = sorted({tid for tid, t in tests if any(k in t for k in keys)})
            gaps = [n for n, ok in (("register row", in_reg is not False), ("maker and SKU", sku == "yes"), ("test", bool(found))) if not ok]
            state = "HOLD" if sku == "HOLD" else ("done" if not gaps else "open: " + ", ".join(gaps))
            bought.append({**r, "in_reg": in_reg, "rid": rid, "sku": sku, "tests": found, "state": state})
    return made, bought


read_cache = {}


def yn(v):
    return "yes" if v is True else ("no" if v is False else str(v))


def render(made, bought, register, teams_no_list, refs, screen, files_seen, fai_count):
    today = datetime.date.today().isoformat()
    out = ["# Release checklist: Spaceship (FocusPod v2)", "",
           "| Doc code | Revision | Status | Date | Owner |", "|---|---|---|---|---|",
           f"| V2-CTL-009 | P01 | DRAFT, written by `build_release_checklist.py` | {today} | Control pack |", "",
           "What stands between the design and a manufacturing release, part by part. Nothing here is released (guideline milestone 4, REQ-DOC-02). "
           "Re-run it whenever parts merge.", "",
           f"Read from: {', '.join(f'`{r}`' for r in refs) if refs else 'this working tree'}. "
           f"The Mac's screen at run time: **{screen}**. {len(files_seen)} files in the CAD, drawing and manufacturing folders; {fai_count} FAI plan lines.", "",
           "**Done** means every item is in. **Blocked** means only the drawing is missing while the screen is locked (D-84). **HOLD** means the product isn't named yet.", "",
           "## Totals per team", "",
           "| Team | Made: done | Made: open | Made: blocked | Bought: done | Bought: open | Bought: HOLD |", "|---|---:|---:|---:|---:|---:|---:|"]
    teams = sorted({r["team"] for r in made + bought} | set(teams_no_list))
    for t in teams:
        m = [r for r in made if r["team"] == t]
        b = [r for r in bought if r["team"] == t]
        if t in teams_no_list and not m and not b:
            out.append(f"| {t} | — | — | — | — | — | — |")
            continue
        out.append(f"| {t} | {sum(r['state'] == 'done' for r in m)} | {sum(r['state'].startswith('open') for r in m)} | "
                   f"{sum(r['state'].startswith('blocked') for r in m)} | {sum(r['state'] == 'done' for r in b)} | "
                   f"{sum(r['state'].startswith('open') for r in b)} | {sum(r['state'] == 'HOLD' for r in b)} |")
    tm = sum(len([r for r in made]) for _ in [0])
    out.append(f"| **All** | {sum(r['state'] == 'done' for r in made)} | {sum(r['state'].startswith('open') for r in made)} | "
               f"{sum(r['state'].startswith('blocked') for r in made)} | {sum(r['state'] == 'done' for r in bought)} | "
               f"{sum(r['state'].startswith('open') for r in bought)} | {sum(r['state'] == 'HOLD' for r in bought)} |")
    if teams_no_list:
        out += ["", "No parts list yet: " + ", ".join(sorted(teams_no_list)) + "."]
    out += ["", "## Made parts and assemblies", ""]
    for t in teams:
        m = [r for r in made if r["team"] == t]
        if not m:
            continue
        out += [f"### {t}", "", "| Part | Name | CAD | STEP | DXF or cut list | Drawing | Mass | Finish | FAI | State |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for r in m:
            out.append(f"| {r['part_number'] or '(no number)'} | {r['name']} | {yn(r['cad'])} | {yn(r['step'])} | {r['flat']} | {yn(r['dwg'])} | "
                       f"{yn(r['mass_ok'])} | {r['finish_ok']} | {', '.join(r['fai']) or 'no'} | {r['state']} |")
        out.append("")
    out += ["## Bought parts", ""]
    for t in teams:
        b = [r for r in bought if r["team"] == t]
        if not b:
            continue
        out += [f"### {t}", "", "| Part | Name | Register | Maker and SKU | Test | State |", "|---|---|---|---|---|---|"]
        seen = set()
        for r in b:
            key = (r["part_number"], r["name"])
            if key in seen:
                continue
            seen.add(key)
            reg = "n/a (team-numbered)" if r["in_reg"] is None else (r["rid"] or "yes") if r["in_reg"] else "no"
            out.append(f"| {r['part_number'] or '(no number)'} | {r['name']} | {reg} | {r['sku']} | {', '.join(r['tests']) or 'no'} | {r['state']} |")
        out.append("")
    used = {r["part_number"] for r in made + bought}
    spare = [i for i in register if i["part_number"] and i["part_number"] not in used]
    if spare:
        out += ["## Joints-register items no parts list uses yet", "", "| Part | Register | Name |", "|---|---|---|"]
        out += [f"| {i['part_number']} | {i['id']} | {i['name']} |" for i in spare]
        out.append("")
    out += ["## How it's built", "",
            "`python3 v2/00-Control/build_release_checklist.py` reads the parts lists and the joints register through the master BOM's reader, the files named "
            "`PARTNO_REV_NAME_DOCTYPE.ext` in `v2/01-CAD-Native`, `v2/02-Drawings` and `v2/03-Manufacturing`, the FAI plan's patterns and the test plans. "
            "A part's CAD and STEP may sit in its assembly's file; its DXF and drawing must carry its own number. `--ref origin/main --ref origin/BRANCH` "
            "shows open branches without merging them.", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the release checklist")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--out", default=str(HERE / "release-checklist.md"))
    ap.add_argument("--screen", default="auto", choices=["auto", "locked", "unlocked"])
    a = ap.parse_args(argv)
    bom = load_bom()
    sources = bom.load_sources(a.ref)
    parts, skipped, register, reg_where = bom.build(sources)
    # Rows of kind 'cut' (a frame's cut lengths) were skipped by the reader: mark the frames that have them.
    for path, (text, _) in sources.items():
        if path.endswith("_BOM.csv") and re.search(r"^\d*,?,[^\n]*,cut,", text, re.M | re.I):
            for r in parts:
                if r["source_file"].startswith(path) and TUBE.search(r["material"] or ""):
                    r["cut_rows"] = True
    paths = list_files(a.ref)
    for p in paths:
        if "CUT-LIST" in p:
            read_cache[p] = read_text(p, a.ref)
    fai = fai_rows(read_text(FAI, a.ref), bom)
    tests = test_rows(read_text(TEST_PLAN, a.ref), sources.get(bom.REGISTER, ("", ""))[0], fai, bom)
    screen = screen_state(a.screen)
    made, bought = check_parts(parts, register, files_by_pn(paths), paths, fai, tests, screen, bom)
    read_paths = [p for p in sources if p != bom.REGISTER and p not in {s[0] for s in skipped}]
    listed = {r["team"] for r in parts}
    no_list = [t for t, folder in bom.EXPECTED_FOLDERS.items() if t not in listed and t != "Packing and Assembly"]
    Path(a.out).write_text(render(made, bought, register, no_list, a.ref, screen, paths, len(fai)), encoding="utf-8")
    done = sum(r["state"] == "done" for r in made + bought)
    print(f"release checklist: {len(made)} made lines, {len(bought)} bought lines, {done} done; screen {screen}; written to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
