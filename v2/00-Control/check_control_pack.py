#!/usr/bin/env python3
"""Re-runs the acceptance checks of the Spaceship (FocusPod v2) control pack.

Doc code V2-CTL-007, revision P01. Standard library only.
Usage (from anywhere):  python3 v2/00-Control/check_control_pack.py
Exit code 0 when every check is OK, 1 otherwise. These are document checks only:
they prove the pack is complete and consistent, not that any design is right.
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCOPE = ["sources/v1", "docs", "v2"]
# Old numbers from the guideline's examples and the earlier V5 attempt: never reused in v2 (D-28).
RESERVED_PN = {"110006", "110002", "120001", "211000", "210001", "210003", "210005", "350011", "830001", "830005"}
PLACEHOLDERS = {"", "-", "—", "–", "?", "tbd", "tba", "todo", "n/a", "na", "none", "nobody", "unknown"}
STATUS_WORD = re.compile(r"^(confirmed|source|calculation|assumption|unverified|proposed|decided)\b", re.I)
failures = []


def fail(check, msg):
    failures.append(f"{check}: {msg}")


def is_placeholder(value):
    v = (value or "").strip().lower().rstrip(".")
    return v in PLACEHOLDERS or v.startswith("tbd")


def table_rows(md_text):
    """Yield (header_cells, row_cells) for every Markdown table row."""
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


# ---------------------------------------------------------------- 1. register
def check_register():
    name = "1 register"
    rows = list(csv.DictReader(open(HERE / "document-register.csv", encoding="utf-8")))
    need = ["doc_code", "path", "revision", "status", "date", "source", "relation"]
    codes = set()
    for r in rows:
        for k in need:
            if not (r.get(k) or "").strip():
                fail(name, f"row {r.get('doc_code')} has an empty '{k}'")
        if r["doc_code"] in codes:
            fail(name, f"duplicate doc code {r['doc_code']}")
        codes.add(r["doc_code"])
    file_rows = {r["path"]: r for r in rows if not r["path"].endswith("/")}
    folder_rows = [r["path"] for r in rows if r["path"].endswith("/")]
    files = []
    for top in SCOPE:
        for p in sorted((ROOT / top).rglob("*")):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in p.relative_to(ROOT).parts):
                files.append(rel)
    exact = [f for f in files if f in file_rows]
    by_folder = [f for f in files if f not in file_rows and any(f.startswith(d) for d in folder_rows)]
    missing = [f for f in files if f not in file_rows and f not in by_folder]
    for f in missing:
        fail(name, f"file not in the register: {f}")
    for path, r in file_rows.items():
        if not (ROOT / path).exists() and not r["status"].upper().startswith("PLANNED"):
            fail(name, f"register row points to a missing file: {path}")
    step = file_rows.get("sources/v1/indoor-pod-v3-assembly.step")
    if not step or "no feature history" not in step["notes"].lower():
        fail(name, "the v1 STEP row must say it has no feature history")
    print(f"[1] register: {len(files)} files in {', '.join(SCOPE)}; {len(exact)} with their own row, "
          f"{len(by_folder)} covered by a folder row, {len(missing)} missing")


# ------------------------------------------------------------ 2. assembly tree
def check_tree():
    name = "2 assembly tree"
    tree = (HERE / "assembly-tree.md").read_text(encoding="utf-8")
    reqs = (HERE / "requirements.md").read_text(encoding="utf-8")
    if_defined = set()
    vt_rows, bp_cover, nodes_in_if = {}, {}, set()
    for hdr, cells in table_rows(tree):
        first = cells[0]
        if hdr[0] == "IF":
            if_defined.add(first)
            nodes_in_if.update(re.findall(r"\b(BASE|WALL|FRONT|CEILING|LINING|AIR|ELECTRICAL|INTERIOR|PACKAGING)\b", cells[1]))
        if hdr[0] == "Plan code":
            vt_rows[first] = cells
        if hdr[0].startswith("Plan item"):
            ids = set(int(n) for n in re.findall(r"BP-(\d+)", first))
            m = re.search(r"BP-(\d+)\s*…\s*BP-(\d+)", first)
            if m:
                ids.update(range(int(m.group(1)), int(m.group(2)) + 1))
            for i in ids:
                bp_cover[i] = cells
    want_vt = ["VT01", "VT02", "VT03-PET", "VT03-ST", "VT04", "VT05", "VT06", "VT07", "VT08", "VT09", "VT10", "VT11", "VT12"]
    for vt in want_vt:
        c = vt_rows.get(vt)
        if not c or is_placeholder(c[2]) or is_placeholder(c[3]):
            fail(name, f"plan code {vt} not mapped to a node and use")
    bp_ids = sorted(set(int(n) for n in re.findall(r"^\| BP-(\d+) \|", reqs, re.M)))
    if bp_ids != list(range(1, 31)):
        fail(name, f"requirements.md lists BP items {bp_ids[:3]}...{bp_ids[-3:]}, expected BP-01...BP-30")
    for i in bp_ids:
        c = bp_cover.get(i)
        if not c or is_placeholder(c[1]) or not c[2]:
            fail(name, f"BP-{i:02d} not mapped to a node with interfaces")
    referenced = set(re.findall(r"IF-\d\d", tree))
    for ref in sorted(referenced - if_defined):
        fail(name, f"{ref} is referenced but not defined in the interface table")
    for node in ["BASE", "WALL", "FRONT", "CEILING", "LINING", "AIR", "ELECTRICAL", "INTERIOR", "PACKAGING"]:
        if node not in nodes_in_if:
            fail(name, f"node {node} has no interface")
    print(f"[2] assembly tree: {len(want_vt)} plan codes, {len(bp_ids)} plan items, {len(if_defined)} interfaces")


# ------------------------------------------------------------ 3. issue register
SEEDED = {
    "ISS-001": ["glass door", "fixed glass"], "ISS-002": ["hinges", "handle"], "ISS-003": ["seal"],
    "ISS-004": ["lights"], "ISS-005": ["wiring", "power inlet"], "ISS-006": ["table"],
    "ISS-007": ["VT03"], "ISS-008": ["Cách ấm tốt", "Cách âm tốt"], "ISS-009": ["weight target", "sound target"],
    "ISS-010": ["slot pattern"], "ISS-011": ["M6", "20x20"], "ISS-012": ["1500", "200", "1700"],
    "ISS-013": ["2400", "2405"], "ISS-014": ["Pat V"], "ISS-015": ["Velcro"], "ISS-016": ["ACP"],
    "ISS-017": ["6 leveling feet", "8 foot instances"], "ISS-018": ["9 mm", "15 mm"],
    "ISS-019": ["2 square", "1 'Ceiling Light'"], "ISS-020": ["2405", "2417"],
}


def check_issues():
    name = "3 issue register"
    rows = list(csv.DictReader(open(HERE / "issue-register.csv", encoding="utf-8")))
    need = ["id", "area", "issue", "action", "who_confirms", "close_condition", "status"]
    ids = set()
    for r in rows:
        for k in need:
            if not (r.get(k) or "").strip():
                fail(name, f"{r.get('id')} has an empty '{k}'")
        for k in ("action_by", "who_confirms", "close_condition"):
            if is_placeholder(r.get(k)):
                fail(name, f"{r.get('id')} has a placeholder '{k}': '{r.get(k)}'")
        if r["status"] not in ("OPEN", "PROPOSED", "DECIDED", "CLOSED"):
            fail(name, f"{r['id']} has status '{r['status']}'")
        if r["id"] in ids:
            fail(name, f"duplicate id {r['id']}")
        ids.add(r["id"])
    by_id = {r["id"]: r for r in rows}
    for i, words in SEEDED.items():
        text = by_id.get(i, {}).get("issue", "").lower()
        for w in words:
            if w.lower() not in text:
                fail(name, f"seeded issue {i} should mention '{w}'")
    counts = {s: sum(r["status"] == s for r in rows) for s in ("OPEN", "PROPOSED", "DECIDED", "CLOSED")}
    print(f"[3] issue register: {len(rows)} issues ({counts}); {len(SEEDED)} seeded issues checked; no placeholder owners")


# ------------------------------------------------------------ 4. conventions and part numbers
def check_conventions():
    name = "4 conventions"
    text = (HERE / "conventions.md").read_text(encoding="utf-8")
    for s in ["Origin O", "+X", "+Y", "+Z", "Left / right", "seen from outside", "Right-handed",
              "first-angle", "Part numbers —", "FF NNNN", "PARTNO_REV_DESCRIPTIVE-NAME_DOCTYPE.ext",
              "ISO 129-1", "ISO 5456-2", "ISO 1101", "ISO 5459", "ISO 2768-1", "ISO 22081",
              "confirmed", "source", "calculation", "assumption", "unverified", "P01", "R01",
              "[ASSEMBLY] - [FUNCTION/PART] - [LOCATION] - [VARIANT]"]:
        if s.lower() not in text.lower():
            fail(name, f"missing '{s}'")
    svg = HERE / "pod-coordinate-system.svg"
    if "pod-coordinate-system.svg" not in text or not svg.exists():
        fail(name, "the axes diagram is missing or not linked")
    else:
        try:
            ET.parse(svg)
        except ET.ParseError as e:
            fail(name, f"diagram is not valid XML: {e}")
    if "```" not in text:
        fail(name, "no text diagram of the axes")
    # The reserved list must be written out in full in the never-reuse rule.
    rule = next((l for l in text.splitlines() if "Never reuse an old number" in l), "")
    for pn in sorted(RESERVED_PN):
        if pn not in rule:
            fail(name, f"reserved number {pn} missing from the never-reuse rule")
    # No v2 part number may be a reserved old number: example table, tree nodes, any master BOM.
    used = []
    for hdr, cells in table_rows(text):
        if hdr[0].lower() == "part number":
            used.append(("conventions.md", cells[0]))
    for hdr, cells in table_rows((HERE / "assembly-tree.md").read_text(encoding="utf-8")):
        if hdr[0].lower() == "node":
            used.append(("assembly-tree.md", cells[0]))
    bom_dir = ROOT / "v2" / "04-BOM"
    for bom in (sorted(bom_dir.glob("*.csv")) if bom_dir.exists() else []):
        for r in csv.DictReader(open(bom, encoding="utf-8")):
            for k, v in r.items():
                if k and "part" in k.lower() and "number" in k.lower():
                    used.append((bom.name, v))
    for where, pn in used:
        for num in re.findall(r"\b\d{6}\b", pn or ""):
            if num in RESERVED_PN:
                fail(name, f"{where} uses reserved old number {num}")
    print(f"[4] conventions: axes, sides, diagram, ISO list, names, part numbers, files, revisions, statuses; "
          f"{len(used)} v2 part numbers clear of the {len(RESERVED_PN)} reserved old numbers")


# ------------------------------------------------------------ 5. requirements
def check_requirements():
    name = "5 requirements"
    text = (HERE / "requirements.md").read_text(encoding="utf-8")
    n, seen = 0, set()
    for hdr, cells in table_rows(text):
        if not re.match(r"^(REQ-[A-Z]+-\d+|BP-\d+)$", cells[0]):
            continue
        n += 1
        if cells[0] in seen:
            fail(name, f"duplicate requirement id {cells[0]}")
        seen.add(cells[0])
        h = [x.lower() for x in hdr]
        try:
            st, so = cells[h.index("status")], cells[h.index("source")]
        except (ValueError, IndexError):
            fail(name, f"{cells[0]} sits in a table without Status and Source columns")
            continue
        if is_placeholder(so):
            fail(name, f"{cells[0]} has no source")
        parts = [p.strip() for p in re.split(r";(?![^()]*\))", st)]
        if not parts or any(not STATUS_WORD.match(p) for p in parts):
            fail(name, f"{cells[0]} has status '{st}'")
    if n == 0:
        fail(name, "no requirement rows found")
    print(f"[5] requirements: {n} lines, each with a real status and a source, no duplicate ids")


# ------------------------------------------------------------ 6. decision log
def check_decisions():
    name = "6 decision log"
    text = (HERE / "decision-log.md").read_text(encoding="utf-8")
    seen = []
    for hdr, cells in table_rows(text):
        if not re.match(r"^D-\d{2,3}$", cells[0]):
            continue
        seen.append(cells[0])
        h = [x.lower() for x in hdr]
        row = dict(zip(h, cells))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", row.get("date", "")):
            fail(name, f"{cells[0]} has no ISO date")
        for k in ("decision", "reason", "what it affects"):
            if is_placeholder(row.get(k, "")):
                fail(name, f"{cells[0]} has an empty '{k}'")
    if len(seen) != len(set(seen)):
        fail(name, "duplicate decision ids")
    if not seen:
        fail(name, "no decisions found")
    cited = set()
    for f in sorted(HERE.iterdir()):
        if f.suffix in (".md", ".csv"):
            cited.update(re.findall(r"\bD-\d{2,3}\b", f.read_text(encoding="utf-8")))
    for d in sorted(cited - set(seen)):
        fail(name, f"{d} is cited but not in the decision log")
    print(f"[6] decision log: {len(seen)} decisions, each with date, decision, reason and what it affects; "
          f"every decision cited in the pack exists")


if __name__ == "__main__":
    for check in (check_register, check_tree, check_issues, check_conventions, check_requirements, check_decisions):
        check()
    if failures:
        print("\nFAIL")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("\nOK: all 6 control pack checks met")
