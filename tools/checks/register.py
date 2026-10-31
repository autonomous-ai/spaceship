#!/usr/bin/env python3
"""The findings register: v2/04-Checks/findings.json is the record,
v2/04-Checks/findings.md is rendered from it for people.

A finding keeps its F-number for life. A run of the checks on main merges
its findings in:
- a new finding gets the next F-number, status OPEN;
- a finding seen again keeps its number; a CLOSED one that comes back is
  reopened;
- an OPEN finding made by a check that ran with its inputs, and that the run
  no longer reports, is CLOSED with the run's revision as evidence.
Findings written by hand (source "manual") close only by hand.

Statuses: OPEN, CLOSED, ACCEPTED (the PM ruled it is intended; give the
D-number). `posted` records where and when the owner was told.

Usage
  python3 tools/checks/register.py render
  python3 tools/checks/register.py set F-004 ACCEPTED --note "D-60: ..."
  python3 tools/checks/register.py posted F-004 "WALL group, 2026-10-31"
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import REPO_ROOT, CHECKS_DIR, CHECK_NAMES, SEVERITIES  # noqa: E402

STATUSES = ("OPEN", "CLOSED", "ACCEPTED")
SEV_ORDER = {s: i for i, s in enumerate(SEVERITIES)}


def paths(root):
    base = os.path.join(root, CHECKS_DIR)
    return os.path.join(base, "findings.json"), os.path.join(base, "findings.md")


def load(root=REPO_ROOT):
    pj, _ = paths(root)
    if not os.path.exists(pj):
        return {"next": 1, "findings": []}
    with open(pj, encoding="utf-8") as fh:
        return json.load(fh)


def save(reg, root=REPO_ROOT):
    pj, pm = paths(root)
    os.makedirs(os.path.dirname(pj), exist_ok=True)
    reg["findings"].sort(key=lambda f: int(f["id"][2:]))
    with open(pj, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(pm, "w", encoding="utf-8") as fh:
        fh.write(render(reg))


def _event(f, date, sha, what):
    f.setdefault("history", []).append({"date": date, "rev": sha, "event": what})


def merge(reg, findings, sha, date=None, checks_run=()):
    """Merge one run's findings (list of Finding.to_dict()) into reg.
    checks_run: the check ids that ran with their inputs, so their missing
    findings can close. Returns (new, reopened, closed) lists of F-numbers."""
    date = date or datetime.date.today().isoformat()
    by_key = {f["key"]: f for f in reg["findings"]}
    seen = set()
    new, reopened, closed = [], [], []
    for d in findings:
        k = d["key"]
        seen.add(k)
        f = by_key.get(k)
        if f is None:
            fid = "F-%03d" % reg["next"]
            reg["next"] += 1
            f = dict(d)
            f.update({"id": fid, "status": "OPEN", "source": "auto", "found": "%s %s" % (date, sha),
                      "posted": ""})
            _event(f, date, sha, "opened")
            reg["findings"].append(f)
            by_key[k] = f
            new.append(fid)
            continue
        for fld in ("message", "fix", "file", "evidence", "severity"):     # owner: set once, changed by hand
            if d.get(fld) not in (None, ""):
                f[fld] = d[fld]
        f["last_seen"] = "%s %s" % (date, sha)
        if f["status"] == "CLOSED":
            f["status"] = "OPEN"
            _event(f, date, sha, "reopened: seen again")
            reopened.append(f["id"])
    ran = set(checks_run)
    for f in reg["findings"]:
        if f["status"] == "OPEN" and f.get("source") == "auto" and f["key"] not in seen and _scope_ran(f, ran):
            f["status"] = "CLOSED"
            f["closed"] = "%s %s" % (date, sha)
            _event(f, date, sha, "closed: the check ran on this revision and no longer finds it")
            closed.append(f["id"])
    return new, reopened, closed


def _scope_ran(f, ran):
    """Did this run cover the check (and model) that made the finding?"""
    model = (f.get("evidence") or {}).get("model")
    if model:
        return "%s:%s" % (f["check"], model) in ran
    return f["check"] in ran


def add_manual(reg, d, date, sha):
    fid = "F-%03d" % reg["next"]
    reg["next"] += 1
    f = dict(d)
    f.update({"id": fid, "status": "OPEN", "source": "manual", "found": "%s %s" % (date, sha), "posted": ""})
    _event(f, date, sha, "opened by hand")
    reg["findings"].append(f)
    return fid


def _cell(s):
    return str(s or "").replace("|", "/").replace("\n", " ").strip()


def render(reg):
    fs = reg["findings"]
    open_ = sorted([f for f in fs if f["status"] == "OPEN"],
                   key=lambda f: (SEV_ORDER.get(f["severity"], 9), int(f["id"][2:])))
    other = sorted([f for f in fs if f["status"] != "OPEN"], key=lambda f: int(f["id"][2:]))
    n_sev = {s: sum(1 for f in open_ if f["severity"] == s) for s in SEVERITIES}
    owners = {}
    for f in open_:
        owners.setdefault(f["owner"] or "unassigned", []).append(f["id"])
    out = []
    out.append("# Mechanical check findings: Spaceship (FocusPod v2)\n")
    out.append("| Doc code | Revision | Status | Owner |")
    out.append("|---|---|---|---|")
    out.append("| V2-CHK-001 | P01 | Live register, rendered from `findings.json` by `tools/checks/register.py` "
               "| Mechanical Checker |\n")
    out.append("Every finding has an owner group and a status. **Severe findings block the owner's merge until "
               "they're fixed** (PM rule). The checks in `tools/checks/` re-run on main after every merge; a finding "
               "the checks no longer see on main closes with that revision as evidence. Findings written by hand "
               "close by hand, with evidence. ACCEPTED means the PM ruled it intended (D-number given).\n")
    out.append("Severity: **severe** = can't be made, assembled or used as drawn; **major** = will cause rework or a "
               "wrong part; **minor** = record keeping. Check codes: " +
               "; ".join("%s %s" % (k, v) for k, v in CHECK_NAMES.items()) + ".\n")
    out.append("## Open: %d (%d severe, %d major, %d minor)\n" % (len(open_), n_sev["severe"], n_sev["major"],
                                                                   n_sev["minor"]))
    if owners:
        out.append("By owner group:\n")
        for o, ids in sorted(owners.items()):
            out.append("- %s: %s" % (o, ", ".join(ids)))
        out.append("")
    out.append("| ID | Severity | Check | Part | Finding | File | Fix | Owner group | Found | Posted |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for f in open_:
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            f["id"], f["severity"], f["check"], _cell(f["subject"]), _cell(f["message"]),
            ("`%s`" % f["file"]) if f.get("file") else "", _cell(f.get("fix")), _cell(f["owner"]),
            _cell(f.get("found")), _cell(f.get("posted"))))
    out.append("\n## Closed and accepted: %d\n" % len(other))
    out.append("| ID | Status | Severity | Check | Part | Finding | Owner group | Found | Closed or accepted |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for f in other:
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            f["id"], f["status"], f["severity"], f["check"], _cell(f["subject"]), _cell(f["message"]),
            _cell(f["owner"]), _cell(f.get("found")), _cell(f.get("closed") or f.get("note"))))
    out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=REPO_ROOT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render")
    s = sub.add_parser("set")
    s.add_argument("id")
    s.add_argument("status", choices=STATUSES)
    s.add_argument("--note", default="")
    s.add_argument("--rev", default="")
    p = sub.add_parser("posted")
    p.add_argument("id")
    p.add_argument("where")
    a = ap.parse_args(argv)
    reg = load(a.root)
    if a.cmd == "set":
        f = next((x for x in reg["findings"] if x["id"] == a.id), None)
        if f is None:
            sys.exit("no finding %s" % a.id)
        today = datetime.date.today().isoformat()
        f["status"] = a.status
        if a.note:
            f["note"] = a.note
        if a.status == "CLOSED":
            f["closed"] = "%s %s %s" % (today, a.rev, a.note)
        _event(f, today, a.rev, "set %s by hand: %s" % (a.status, a.note))
    elif a.cmd == "posted":
        f = next((x for x in reg["findings"] if x["id"] == a.id), None)
        if f is None:
            sys.exit("no finding %s" % a.id)
        f["posted"] = (f.get("posted") + "; " if f.get("posted") else "") + a.where
    save(reg, a.root)
    print("register: %d findings, %d open" % (len(reg["findings"]),
                                              sum(1 for f in reg["findings"] if f["status"] == "OPEN")))


if __name__ == "__main__":
    main()
