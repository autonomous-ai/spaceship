"""Check the wall and door sample package. Run from this folder: python3 check_package.py

- the parts list's Status cells use only the five status words: confirmed, source, calculation, assumption, unverified;
- every decision (D-nn), requirement (REQ-...), issue (ISS-nnn) and layout study item (LS-nn) the package cites exists
  in the control pack and the layout study on this branch;
- every test names items the build list defines and HOLDs the HOLD list has, and stays PLANNED or HOLD (guideline §10);
- every part, HOLD and drawing ID cited anywhere is defined in its own list, and nothing reads like a price.
Exits with 1 and a list of problems if any check fails.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, "..", ".."))
FILES = ("README.md", "build-list.md", "parts-list.md", "test-plan.md", "hold-list.md", "drawings-needed.md")
STATUS_WORDS = {"confirmed", "source", "calculation", "assumption", "unverified"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def table_rows(text, first):
    """Rows of the markdown tables whose first cell matches the regex `first`, as lists of cells."""
    out = []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if re.fullmatch(first, cells[0]):
                out.append(cells)
    return out


def main():
    docs = {name: read(os.path.join(HERE, name)) for name in FILES}
    every = "\n".join(docs.values())
    bad = []

    # what exists outside the package
    known = set(re.findall(r"^\| (D-\d{2,3}) \|", read(os.path.join(V2, "00-Control", "decision-log.md")), re.M))
    known |= set(re.findall(r"^\| (REQ-[A-Z]+-\d\d) \|", read(os.path.join(V2, "00-Control", "requirements.md")), re.M))
    with open(os.path.join(V2, "00-Control", "issue-register.csv"), encoding="utf-8") as f:
        known |= {r[0] for r in csv.reader(f) if r and r[0].startswith("ISS-")}
    known |= set(re.findall(r"^\| (LS-\d\d) \|", read(os.path.join(V2, "05-Engineering", "layout-study", "report.md")), re.M))
    for ref in sorted(set(re.findall(r"\b(?:D-\d{2,3}|REQ-[A-Z]+-\d\d|ISS-\d{3}|LS-\d\d)\b", every))):
        if ref not in known:
            bad.append(f"cited but not found: {ref}")

    # the package's own IDs
    parts = {r[0] for r in table_rows(docs["parts-list.md"], r"P\d\d[A-Z]?")}
    holds = {r[0] for r in table_rows(docs["hold-list.md"], r"H\d\d")}
    drawings = {r[0] for r in table_rows(docs["drawings-needed.md"], r"D\d\d")}
    items = set(re.findall(r"^### (S\d) ", docs["build-list.md"], re.M)) | {r[0] for r in table_rows(docs["build-list.md"], r"R\d")}
    for kind, pattern, defined in (("part", r"\bP\d\d[A-Z]?\b", parts), ("HOLD", r"\bH\d\d\b", holds),
                                   ("drawing", r"\bD\d\d\b", drawings), ("item", r"\b[SR]\d\b", items)):
        for ref in sorted(set(re.findall(pattern, every)) - defined):
            bad.append(f"{kind} {ref} is cited but not defined")

    # parts: the status of every number; each clause is "word (what it covers)", clauses split by ";"
    for r in table_rows(docs["parts-list.md"], r"P\d\d[A-Z]?"):
        status = r[5]
        if status in ("—", "-"):
            continue
        while re.search(r"\([^()]*\)", status):                 # drop the notes in brackets, innermost first
            status = re.sub(r"\([^()]*\)", "", status)
        for part in status.split(";"):
            word = part.strip().split(" ")[0]
            if word not in STATUS_WORDS:
                bad.append(f"{r[0]}: status word '{word}' is not one of {sorted(STATUS_WORDS)}")

    # tests: items, HOLDs and status
    tests = table_rows(docs["test-plan.md"], r"T\d\d")
    ids = [r[0] for r in tests]
    if len(ids) != len(set(ids)):
        bad.append("test IDs repeat")
    for r in tests:
        if not re.findall(r"\b[SR]\d\b", r[2]):
            bad.append(f"{r[0]}: names no sample item or rig")
        if not (r[7].startswith("PLANNED") or r[7].startswith("HOLD")):
            bad.append(f"{r[0]}: status '{r[7]}' must be PLANNED or HOLD until real data exists")
        if not re.search(r"\b(?:REQ-[A-Z]+-\d\d|D-\d{2,3})\b", r[6]):
            bad.append(f"{r[0]}: ties to no requirement or decision")
    if f"T01 to {ids[-1]}" not in docs["README.md"]:
        bad.append(f"README.md doesn't give the tests as T01 to {ids[-1]}")

    # public repo: no prices
    for name, text in docs.items():
        if re.search(r"[$€£]|\b(?:USD|VND|EUR)\b", text):
            bad.append(f"{name}: looks like a price or quote")

    if bad:
        print("NOT OK:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print(f"OK: {len(parts)} parts, {len(tests)} tests, {len(holds)} HOLDs, {len(drawings)} drawings, {len(items)} items and rigs; "
          "every cited decision, requirement, issue and layout study item exists.")


if __name__ == "__main__":
    main()
