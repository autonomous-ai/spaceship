#!/usr/bin/env python3
"""Run the offline mechanical checks on a checked-out tree and report.

  python3 tools/checks/run_checks.py                      # this checkout
  python3 tools/checks/run_checks.py --root /path/to/main --rev 1eec888 --update

--root      the tree to check (default: this repository)
--rev       the revision label for the report (default: git HEAD of --root)
--update    merge the findings into the register (v2/04-Checks/findings.json
            and findings.md under --register-root, default this repository),
            and write v2/04-Checks/results/latest.{json,md} and
            v2/04-Checks/fastener-schedule.csv there
--json      print the findings as JSON instead of the summary

Exit code: 0 when no severe finding is open in this run, 1 when one is.

The Fusion checks (C01 exact clash and gaps, C03 tool access, C07 thread
engagement, C08 alignment in the native assembly) run separately through the
locked runner: see tools/checks/README.md.
"""

import argparse
import csv
import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import REPO_ROOT, CHECKS_DIR, CHECK_NAMES, SEVERITIES, rel, pn_class  # noqa: E402
import c_geometry  # noqa: E402
import c_parts  # noqa: E402
import c_drawings  # noqa: E402
import c_stacks  # noqa: E402
import register  # noqa: E402
import stepfile as sf  # noqa: E402


def git_rev(root):
    try:
        return subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              timeout=20).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def contacts_from(bodies, tol=0.2):
    out = []
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            if a.part_number == b.part_number:
                continue
            if sf.box_gap(a.box, b.box) <= tol:
                out.append((a.part_number, b.part_number, a.file))
    return out


def run(root, rev):
    findings, ran, inputs = [], set(), {}
    # geometry
    mdls, per_part = c_geometry.models(root)
    rules = c_geometry.load_gap_rules(root)
    for mdl, bodies in mdls.items():
        inputs["bodies_" + mdl] = len(bodies)
        if not bodies:
            continue
        findings += c_geometry.check_shell(root, mdl, bodies)
        if c_geometry.shell_ready(mdl, bodies):
            ran |= {"C01", "C01:" + mdl}
        if rules:
            findings += c_geometry.check_gap_rules(root, mdl, bodies, rules)
            ran |= {"C02:" + mdl}
    asm = mdls["assembly"]
    if any(b.solid.holes for b in asm):
        findings += c_geometry.check_alignment(root, "assembly", asm)
        findings += c_geometry.check_unmatched(root, "assembly", asm)
        findings += c_geometry.check_hole_sizes(root, "assembly", asm)
        ran |= {"C08", "C08:assembly"}
    stack_fs, stack_report = c_stacks.check_stacks(root)
    findings += stack_fs
    if stack_report:
        ran.add("C02:stacks")
    # parts lists
    plists = c_parts.find_parts_lists(root)
    inputs["parts_lists"] = [rel(root, p) for p, _r in plists]
    materials = {row["part_number"]: " ".join(x for x in (row["material"], row["grade"]) if x)
                 for _p, rows in plists for row in rows if row["part_number"]}
    if plists:
        findings += c_parts.check_parts_lists(root, plists)
        ran |= {"C06", "C07", "C10", "C11"}
    # per-part STEP checks
    srules = c_geometry.load_bend_rules(root)
    for p in per_part:
        findings += c_geometry.check_part_features(root, p, materials, srules)
    if per_part:
        ran.add("C09")
    inputs["part_steps"] = [rel(root, p) for p in per_part]
    # STEP products for the BOM match and the drawings
    step_products, holes_by_pn, usage = {}, {}, {}
    for p in per_part:
        s = c_geometry.load_step(p)
        counts, _tops = s.usage_counts()
        for prod in s.products():
            pn = prod["part_number"]
            d = step_products.setdefault(pn, {"files": set(), "count": 0, "name": prod["name"]})
            d["files"].add(rel(root, p))
            d["count"] = max(d["count"], counts.get(pn, 0))
        for inst in s.instances():
            so = s.solid(inst["solid"])
            holes_by_pn.setdefault(inst["part_number"], so.holes)
            usage.setdefault(inst["part_number"], []).append((rel(root, p), 1, [" / ".join(inst["path"][1:])]))
    if plists:
        findings += c_parts.check_cad_match(root, plists, step_products)
        findings += c_parts.check_mixed_metals(root, plists, contacts_from(asm))
    # shipping
    ship_fs, ship_report, ship_src = c_parts.check_shipping(root)
    findings += ship_fs
    if ship_src:
        ran.add("C04")
    # drawings
    # parts we make need drawings; assemblies only once they exist in CAD (not the skeleton, a reference)
    made = {row["part_number"] for p, rows in plists for row in rows if pn_class(row["part_number"]) == "part"
            and not (c_parts.is_master(rel(root, p)) and c_parts.is_placeholder(row))}
    made |= {pn for pn, d in step_products.items() if pn_class(pn) in ("part", "assembly")
             and not all("/skeleton/" in f for f in d["files"])}
    names = {row["part_number"]: row["name"] for _p, rows in plists for row in rows}
    names.update({pn: d["name"] for pn, d in step_products.items() if pn not in names})
    if made:
        findings += c_drawings.check_drawings(root, made, holes_by_pn, names)
        ran.add("C05")
    schedule = c_parts.fastener_schedule(root, plists, usage)
    return {"rev": rev, "date": datetime.date.today().isoformat(), "inputs": inputs,
            "ran": sorted(ran), "findings": [f.to_dict() for f in findings], "stacks": stack_report,
            "shipping": ship_report, "shipping_source": ship_src, "fastener_schedule": schedule}


def report_md(res, reg_ids):
    L = []
    L.append("# Mechanical check run: %s on %s\n" % (res["rev"], res["date"]))
    L.append("Offline checks (`tools/checks/run_checks.py`) on revision `%s`. The Fusion checks (exact clash, "
             "tool access, thread engagement) are recorded separately when they run.\n" % res["rev"])
    n = {s: sum(1 for f in res["findings"] if f["severity"] == s) for s in SEVERITIES}
    L.append("**Findings in this run: %d** (%d severe, %d major, %d minor). Register numbers in brackets.\n" % (
        len(res["findings"]), n["severe"], n["major"], n["minor"]))
    L.append("## What ran\n")
    L.append("| Check | Ran on this revision | Findings |")
    L.append("|---|---|---|")
    for c, name in CHECK_NAMES.items():
        k = sum(1 for f in res["findings"] if f["check"] == c)
        ran = any(r == c or r.startswith(c + ":") for r in res["ran"])
        L.append("| %s %s | %s | %d |" % (c, name, "yes" if ran else "no inputs yet", k))
    L.append("\nInputs: %s\n" % json.dumps(res["inputs"]))
    L.append("## Findings\n")
    L.append("| Register | Severity | Check | Subject | Finding | Owner |")
    L.append("|---|---|---|---|---|---|")
    for f in sorted(res["findings"], key=lambda f: (SEVERITIES.index(f["severity"]), f["check"])):
        L.append("| %s | %s | %s | %s | %s | %s |" % (reg_ids.get(f["key"], ""), f["severity"], f["check"],
                                                    f["subject"].replace("|", "/"),
                                                    f["message"].replace("|", "/"), f["owner"]))
    L.append("\n## Tolerance stacks (C02)\n")
    L.append("| Stack | Joint | What | Needs | Nominal | Worst case | RSS (info) | State | Missing |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for s in res["stacks"]:
        need = ("%s to %s" % (s["min"], s["max"])) if s["max"] is not None else (">= %s" % s["min"])
        L.append("| %s | %s | %s | %s | %.2f | %.2f to %.2f | %.2f to %.2f | %s | %s |" % (
            s["stack_id"], s["joint"], s["what"], need, s["nominal"], s["wc_min"], s["wc_max"], s["rss_min"],
            s["rss_max"], s["state"], "; ".join(s["missing"])))
    L.append("\n## Shipping pieces (C04), from `%s`\n" % res["shipping_source"])
    L.append("| Piece | kg | Size mm | Ships as | Status |")
    L.append("|---|---|---|---|---|")
    for s in res["shipping"]:
        L.append("| %s %s | %s | %s | %s | %s |" % (s["id"], s["name"].replace("|", "/"), s["kg"],
                                                  " x ".join("%g" % d for d in s["dims"]), s["ships_as"], s["status"]))
    L.append("\n## Fastener schedule (C07)\n")
    L.append("%d fastener lines; full table in `v2/04-Checks/fastener-schedule.csv`.\n" % len(res["fastener_schedule"]))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=REPO_ROOT)
    ap.add_argument("--ref", default="", help="check this git ref (e.g. origin/main) in a fresh export instead of --root")
    ap.add_argument("--register-root", default=REPO_ROOT)
    ap.add_argument("--rev", default=None)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    export_dir = None
    if a.ref:
        from common import export_ref
        root, sha = export_ref(a.ref)
        export_dir = root
        a.rev = a.rev or sha
    try:
        return _main(a, root)
    finally:
        if export_dir:                      # the export is about 22 MB: never leave it behind
            import shutil
            shutil.rmtree(export_dir, ignore_errors=True)


def _main(a, root):
    if a.update and a.rev and not a.ref and git_rev(root) not in ("unknown", a.rev[:len(git_rev(root))]):
        # a register update must describe the tree it checked: refuse a label that names another revision
        print("refusing --update: --rev %s but the tree checked is at %s; use --ref to check that revision"
              % (a.rev, git_rev(root)), file=sys.stderr)
        return 2
    rev = a.rev or git_rev(root)
    res = run(root, rev)
    reg_ids = {}
    if a.update:
        reg = register.load(a.register_root)
        new, reopened, closed = register.merge(reg, res["findings"], rev, res["date"], res["ran"])
        register.save(reg, a.register_root)
        reg_ids = {f["key"]: f["id"] for f in reg["findings"]}
        out = os.path.join(a.register_root, CHECKS_DIR, "results")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "latest.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False, default=str)
            fh.write("\n")
        with open(os.path.join(out, "latest.md"), "w", encoding="utf-8") as fh:
            fh.write(report_md(res, reg_ids))
        sched = os.path.join(a.register_root, CHECKS_DIR, "fastener-schedule.csv")
        cols = ["part_number", "name", "size", "length_mm", "grade", "finish", "torque_nm", "qty_parts_list",
                "qty_cad", "where_cad", "maker", "sku", "status", "parts_list", "engagement"]
        with open(sched, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for row in res["fastener_schedule"]:
                w.writerow(row)
        print("register: new %s, reopened %s, closed %s" % (new or "-", reopened or "-", closed or "-"))
    if a.json:
        print(json.dumps(res["findings"], indent=1, ensure_ascii=False))
    else:
        n = {s: sum(1 for f in res["findings"] if f["severity"] == s) for s in SEVERITIES}
        print("rev %s: %d findings (%d severe, %d major, %d minor); ran %s" % (
            rev, len(res["findings"]), n["severe"], n["major"], n["minor"], ", ".join(res["ran"])))
        for f in res["findings"]:
            print("  %-6s %-4s %s | %s" % (f["severity"], f["check"], reg_ids.get(f["key"], ""), f["subject"]))
    return 1 if any(f["severity"] == "severe" for f in res["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
