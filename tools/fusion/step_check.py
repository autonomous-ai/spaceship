#!/usr/bin/env python3
"""Read a STEP file without Fusion: length unit, products, solids, bounding box.

    python3 tools/fusion/step_check.py FILE.step [--expect "xmin,ymin,zmin,xmax,ymax,zmax"]

It reports the length unit the file declares (Fusion's API writes STEP in cm
even when the design is in mm; that is exact, since every CAD reads the unit
from the file) and prints the bounding box in mm by applying that unit. The
box is taken from every VERTEX_POINT, so it is exact for straight-edged parts.
It ignores assembly transforms, so it is only right when all components sit
at the origin (true for the proof part; the tool says so when it finds a
transform). Exit 1 if --expect is given and differs by more than 0.01 mm, or
if no length unit is declared. Standard library only. It never edits the file.
"""

UNIT_MM = {".MILLI.": 1.0, ".CENTI.": 10.0, "$": 1000.0, ".DECI.": 100.0}

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
    # the length unit used by the geometry context(s)
    scale, unit = None, None
    for v in ents.values():
        flat = v.replace(" ", "")
        if "GLOBAL_UNIT_ASSIGNED_CONTEXT" in flat and "GEOMETRIC_REPRESENTATION_CONTEXT" in flat:
            refs = re.search(r"GLOBAL_UNIT_ASSIGNED_CONTEXT\(\(([^)]*)\)\)", flat)
            for ref in (refs.group(1).split(",") if refs else []):
                u = ents.get(int(ref.strip("#")), "").replace(" ", "")
                m = re.search(r"LENGTH_UNIT\(\).*SI_UNIT\(([^,]*),\.METRE\.\)", u)
                if m:
                    scale, unit = UNIT_MM.get(m.group(1)), m.group(1)
                elif "LENGTH_UNIT" in u and "CONVERSION_BASED_UNIT" in u:
                    unit = "conversion-based (e.g. inch): not handled"
    names = {".MILLI.": "mm", ".CENTI.": "cm", "$": "m", ".DECI.": "dm"}
    print("length:   %s, declared in the file" % names.get(unit, unit))
    if scale is None:
        print("no SI length unit found for the geometry")
        return 1
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
    box = [min(p[i] for p in pts) * scale for i in range(3)] + \
          [max(p[i] for p in pts) * scale for i in range(3)]
    print("vertices: %d" % len(pts))
    print("bbox mm:  X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f  (file values x %g)" % (
        box[0], box[3], box[1], box[4], box[2], box[5], scale))
    if transforms:
        print("note:     %d assembly transforms found; the box assumes components at the origin"
              % len(transforms))
    rc = 0
    if o.expect:
        want = [float(x) for x in o.expect.split(",")]
        diff = max(abs(a - b) for a, b in zip(box, want))
        print("expect:   largest difference %.4f mm -> %s" % (diff, "MATCH" if diff <= 0.01 else "MISMATCH"))
        if diff > 0.01:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
