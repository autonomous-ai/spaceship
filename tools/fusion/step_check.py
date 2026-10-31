#!/usr/bin/env python3
"""Read a STEP file without Fusion: length unit, products, solids, bounding box.

    python3 tools/fusion/step_check.py FILE.step [--expect "xmin,ymin,zmin,xmax,ymax,zmax"]

The bounding box is taken from every VERTEX_POINT, so it is exact for
straight-edged parts. It ignores assembly transforms, so it is only right when
all components sit at the origin (true for the proof part; the tool says so
when it finds a transform). Exit 1 if --expect is given and differs by more
than 0.01 mm, or if the length unit is not millimetre. Standard library only.
"""

import argparse
import re
import sys


def parse(path):
    text = open(path, "r", encoding="utf-8", errors="replace").read()
    # join continuation lines: STEP entities end with ';'
    ents = {}
    for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)", text, re.S):
        ents[int(m.group(1))] = " ".join(m.group(2).split())
    return text, ents


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step")
    ap.add_argument("--expect", help="xmin,ymin,zmin,xmax,ymax,zmax in mm")
    o = ap.parse_args(argv)
    text, ents = parse(o.step)

    schema = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", text)
    print("schema:   %s" % (schema.group(1) if schema else "?"))
    milli = any("SI_UNIT(.MILLI.,.METRE.)" in v.replace(" ", "") for v in ents.values())
    inch = any("'INCH'" in v.upper() for v in ents.values())
    unit = "mm" if milli and not inch else ("inch" if inch else "other")
    print("length:   %s" % unit)
    products = sorted({re.match(r"PRODUCT\s*\(\s*'([^']*)'", v).group(1)
                       for v in ents.values() if re.match(r"PRODUCT\s*\(", v)})
    print("products: %d" % len(products))
    for p in products:
        print("  - %s" % p)
    solids = sum(1 for v in ents.values() if v.startswith("MANIFOLD_SOLID_BREP"))
    print("solids:   %d" % solids)
    transforms = [v for v in ents.values() if v.startswith("ITEM_DEFINED_TRANSFORMATION")]

    pts = []
    for v in ents.values():
        m = re.match(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*\)", v)
        if m:
            cp = ents.get(int(m.group(1)), "")
            c = re.match(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", cp)
            if c:
                pts.append([float(x) for x in c.group(1).split(",")])
    if not pts:
        print("no vertices found")
        return 1
    box = [min(p[i] for p in pts) for i in range(3)] + [max(p[i] for p in pts) for i in range(3)]
    print("vertices: %d" % len(pts))
    print("bbox mm:  X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (
        box[0], box[3], box[1], box[4], box[2], box[5]))
    if transforms:
        ident = all(re.search(r"\(\s*0\.?0*E?\+?0*\s*,\s*0\.?0*E?\+?0*\s*,\s*0\.?0*E?\+?0*\s*\)", t)
                    for t in transforms)
        print("note:     %d assembly transforms found; the box assumes components at the origin"
              % len(transforms))
    rc = 0 if unit == "mm" else 1
    if o.expect:
        want = [float(x) for x in o.expect.split(",")]
        diff = max(abs(a - b) for a, b in zip(box, want))
        print("expect:   largest difference %.4f mm -> %s" % (diff, "MATCH" if diff <= 0.01 else "MISMATCH"))
        if diff > 0.01:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
