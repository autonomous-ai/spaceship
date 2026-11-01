#!/usr/bin/env python3
"""drawgen: part drawings straight from each part's STEP, outside Fusion (D-112, D-113).

  tools/drawgen/run.sh generate 211101 111101        # those parts, into v2/02-Drawings/<team>/
  tools/drawgen/run.sh generate --sample             # the sample drawings the PM reviewed first (#202)
  tools/drawgen/run.sh generate --all --out /tmp/x   # every registered part, somewhere else
  tools/drawgen/run.sh check v2/02-Drawings/wall/211101_P01_*_DWG.pdf   # read each PDF back against its STEP
  tools/drawgen/run.sh stale                         # registered drawings whose STEP or lists changed since

A drawing goes to v2/02-Drawings/<team>/PN_REV_NAME_DWG.pdf (conventions section 7). It never overwrites a PDF
that drawgen didn't make (a Fusion drawing): it stops and says so. Each PDF carries its sources and their hashes
(catalog key /DrawgenData), so `stale` can tell when the model moved on and the drawing must be made again.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fitz  # noqa: E402

import compose  # noqa: E402
import inputs  # noqa: E402
import readback  # noqa: E402
import specs  # noqa: E402

DRAWINGS = os.path.join(inputs.REPO, "v2", "02-Drawings")


def made_by_drawgen(path):
    try:
        with fitz.open(path) as d:
            return (d.metadata or {}).get("creator") == "drawgen"
    except Exception:
        return False


def generate(pn, out_dir=None):
    team, kind, spec = specs.SPECS[pn]
    tmp = os.path.join(out_dir or os.path.join(DRAWINGS, team), ".drawgen-%s.pdf" % pn)
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    try:
        rep = compose.make(pn, team, spec, tmp)
        final = os.path.join(os.path.dirname(tmp), rep["dwg"] + ".pdf")
        if os.path.exists(final) and not made_by_drawgen(final):
            raise compose.NotDrawable("%s exists and was not made by drawgen (a Fusion drawing): left as it is"
                                      % inputs.rel(final))
        os.replace(tmp, final)
        return final, rep
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def stale(path):
    """Why a generated drawing is out of date: a source whose hash changed, or the source gone."""
    with fitz.open(path) as d:
        data = readback.read_data(d)
    why = []
    for s in data.get("sources", []):
        p = os.path.join(inputs.REPO, s["path"])
        if not os.path.exists(p):
            why.append("%s is gone" % s["path"])
        elif inputs.sha12(p) != s["sha256_12"]:
            why.append("%s changed" % s["path"])
    return why


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("pns", nargs="*")
    g.add_argument("--sample", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--out", default=None, help="write here instead of v2/02-Drawings/<team>/")
    c = sub.add_parser("check")
    c.add_argument("pdfs", nargs="+")
    sub.add_parser("stale")
    a = ap.parse_args(argv)
    if a.cmd == "generate":
        pns = list(a.pns)
        if a.sample:
            pns += specs.SAMPLE
        if a.all:
            pns += list(specs.SPECS)
        bad = 0
        for pn in dict.fromkeys(pns):
            if pn in getattr(specs, "NO_DRAWING", {}):
                print("%s: no drawing: %s" % (pn, specs.NO_DRAWING[pn]))
                continue
            if pn not in specs.SPECS:
                print("%s: not registered in tools/drawgen/specs.py" % pn)
                bad += 1
                continue
            try:
                final, rep = generate(pn, a.out)
            except compose.NotDrawable as e:
                print("%s: not drawn: %s" % (pn, e))
                bad += 1
                continue
            fails, st = readback.check(final)
            print("%s: %s; read-back %s (%d holes, worst %.4f mm)" % (
                pn, inputs.rel(final) if final.startswith(inputs.REPO) else final, "PASS" if not fails else "FAIL",
                st["holes"], max(st["worst_table"], st["worst_drawn"])))
            for f in fails:
                print("  - " + f)
            bad += bool(fails)
        return 1 if bad else 0
    if a.cmd == "check":
        bad = 0
        for p in a.pdfs:
            fails, st = readback.check(p)
            print("%s: %s" % (os.path.basename(p), "PASS" if not fails else "FAIL"))
            for f in fails:
                print("  - " + f)
            bad += bool(fails)
        return 1 if bad else 0
    if a.cmd == "stale":
        out = 0
        for root, _d, files in os.walk(DRAWINGS):
            for f in sorted(files):
                if f.endswith("_DWG.pdf") and made_by_drawgen(os.path.join(root, f)):
                    why = stale(os.path.join(root, f))
                    if why:
                        out += 1
                        print("%s: %s" % (f, "; ".join(why)))
        print("%d generated drawing%s out of date" % (out, "" if out == 1 else "s"))
        return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
