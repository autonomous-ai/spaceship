#!/usr/bin/env python3
"""Every committed generator sheet, read back and redrawn with the code in this tree (the Lead's ask, 2026-11-01:
Reviewer 14 on #380 found that nothing reads main's committed drawings back with the current generator code, so a
generator PR that tightens the read-back could leave main with sheets that now fail, and nothing would flag it).

For each PDF under v2/02-Drawings that tools/drawgen made (its creator field says drawgen):
- it is read back with the tree's own read-back (readback.check for a part sheet, assembly.check for an assembly
  sheet), and every failure is reported;
- it is drawn again from its entry with the tree's own code, into a temporary folder (never over the committed sheet),
  and the bytes are compared: the generator draws the same bytes from the same sources (the date comes from the
  STEP's header), so a sheet that differs is out of date. The report says why: its sources changed since it was
  drawn (the sheet's own record of its sources and their hashes), or else the generator's code changed;
- a sheet with no entry left to draw it from, or one its entry now refuses to draw, is reported as such.

Run it in drawgen's own Python environment (OCC and PyMuPDF): tools/checks/drawgen_audit.sh [--json FILE]
[--only PN ...]. It prints one line a sheet and a summary, and exits 1 when any sheet fails or doesn't redraw the
same. It writes nothing in the tree.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_sheets(drawings_dir, is_generated):
    """The generator's sheets: every *_DWG.pdf under drawings_dir that is_generated(path) says drawgen made."""
    out = []
    for root, _dirs, files in os.walk(drawings_dir):
        for f in files:
            p = os.path.join(root, f)
            if f.endswith("_DWG.pdf") and is_generated(p):
                out.append(p)
    return sorted(out)


def audit(sheets, kind_of, readback, redraw, stale_of, rel=os.path.basename):
    """One result per sheet. kind_of(pn): 'part', 'assembly' or None (no entry); readback(path, kind): its failures;
    redraw(pn, kind, out_dir): the path of a fresh drawing (raises to refuse); stale_of(path): why its sources moved."""
    results = []
    tmp = tempfile.mkdtemp(prefix="drawgen-audit-")
    try:
        for i, p in enumerate(sheets):
            pn = os.path.basename(p)[:6]
            kind = kind_of(pn)
            r = {"sheet": rel(p), "pn": pn, "kind": kind, "readback": [], "redraw": None, "why": []}
            if kind is None:
                r["redraw"] = "no entry"
                r["why"] = ["no entry in tools/drawgen draws %s any more, so it can't be drawn again" % pn]
                results.append(r)
                continue
            r["readback"] = list(readback(p, kind))
            out = os.path.join(tmp, "%03d" % i)
            os.makedirs(out)
            try:
                new = redraw(pn, kind, out)
            except Exception as e:             # the entry refuses it now (compose.NotDrawable and the like)
                r["redraw"] = "not drawn"
                r["why"] = ["its entry doesn't draw it now: %s" % e]
                results.append(r)
                continue
            with open(p, "rb") as fa, open(new, "rb") as fb:
                same = fa.read() == fb.read()
            r["redraw"] = "same" if same else "differs"
            if not same:
                moved = list(stale_of(p))
                r["why"] = moved or ["its sources are as they were, so the generator's code draws it differently now"]
            results.append(r)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return results


def bad(r):
    return bool(r["readback"]) or r["redraw"] != "same"


def report(results):
    """The lines to print and the summary line."""
    lines = []
    for r in results:
        rb = "PASS" if not r["readback"] else "FAIL (%d)" % len(r["readback"])
        if r["redraw"] == "no entry":
            rb = "not read back"
        lines.append("%s: read-back %s; redraw %s%s" % (r["sheet"], rb, r["redraw"],
                                                        (": " + "; ".join(r["why"])) if r["why"] else ""))
        lines.extend("  - " + f for f in r["readback"])
    n = len(results)
    failing = sum(1 for r in results if r["readback"])
    differ = [r for r in results if r["redraw"] == "differs"]
    code = sum(1 for r in differ if r["why"] and r["why"][0].startswith("its sources are as they were"))
    other = sum(1 for r in results if r["redraw"] in ("no entry", "not drawn"))
    summary = ("%d generator sheet%s: %d read back and redraw the same; %d fail the read-back; %d no longer redraw "
               "byte for byte (%d by the generator's code, %d with changed sources); %d can't be drawn again" % (
                   n, "" if n == 1 else "s", sum(1 for r in results if not bad(r)), failing, len(differ), code,
                   len(differ) - code, other))
    return lines, summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=None, help="also write the results here")
    ap.add_argument("--only", nargs="*", default=None, help="these part numbers only")
    a = ap.parse_args(argv)
    sys.path.insert(0, os.path.join(REPO, "tools", "drawgen"))
    import assembly                                  # noqa: E402  (drawgen's own modules, from this tree)
    import drawgen                                   # noqa: E402
    import readback as rb                            # noqa: E402
    import specs                                     # noqa: E402

    asm = assembly.assemblies()

    def kind_of(pn):
        return "assembly" if pn in asm else ("part" if pn in specs.SPECS else None)

    def read(path, kind):
        return (assembly.check(path) if kind == "assembly" else rb.check(path))[0]

    def redraw(pn, kind, out):
        if kind == "assembly":
            team, entry = asm[pn]
            return assembly.generate(pn, team, entry, out)[0]
        return drawgen.generate(pn, out)[0]

    sheets = find_sheets(os.path.join(REPO, "v2", "02-Drawings"), drawgen.made_by_drawgen)
    if a.only:
        sheets = [p for p in sheets if os.path.basename(p)[:6] in set(a.only)]
    results = audit(sheets, kind_of, read, redraw, drawgen.stale, rel=lambda p: os.path.relpath(p, REPO))
    lines, summary = report(results)
    print("\n".join(lines + [summary]))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "sheets": results}, fh, indent=1)
    return 1 if any(bad(r) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
