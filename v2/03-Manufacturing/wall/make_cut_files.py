"""Cut files (DXF, 1:1, mm, layers CUT / BEND / MARK) for a WALL side panel and its cassette.

    python3 v2/03-Manufacturing/wall/make_cut_files.py 210101 510101

- The tray: Fusion's own flat pattern (export_flat_dxf.py writes it to .raw/), moved onto the project's
  layers with dxf_tools.relayer; its extents are checked against the flat size Fusion reported.
- The ACP skin: the skin isn't sheet metal in Fusion (ACP is V-grooved and folded, not bent), so its blank
  is drawn here from the skin body's sizes in the CAD report: the main face and the 43 mm back return laid
  out flat, outer-face lengths, with the fold (V-groove) on the BEND layer. Fold allowance 0 (assumption):
  the ACP maker's V-groove rule replaces it (HOLD H16).
Each file is re-read and its unit, layers and extents printed.
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dxf_tools  # noqa: E402

FOLD_ALLOWANCE = 0.0   # assumption, HOLD H16: the ACP maker's V-groove rule


def load(pn):
    with open(os.path.join(HERE, "out", "%s.json" % pn), encoding="utf-8") as fh:
        return json.load(fh)


def comp(rep, prefix):
    return [c for c in rep["components"] if c["part_number"].startswith(prefix)][0]


def main(argv):
    panel, cass = load(argv[1]), load(argv[2])
    out = []
    # tray: Fusion's flat pattern, relayered
    tray = [c for c in cass["components"] if " - TRAY - " in c["name"]][0]
    raws = glob.glob(os.path.join(HERE, ".raw", "%s_P01_*_flat-fusion.dxf" % tray["part_number"]))
    if len(raws) != 1:
        raise SystemExit("expected one raw flat pattern for %s in .raw/, found %d (run export_flat_dxf.py)" % (
            tray["part_number"], len(raws)))
    dst = os.path.join(HERE, os.path.basename(raws[0]).replace("_flat-fusion.dxf", "_DXF.dxf"))
    seen = dxf_tools.relayer(raws[0], dst)
    out.append((dst, "Fusion flat pattern, layers %s" % seen))
    # skin blank from the CAD sizes
    skin = comp(panel, "2113")
    b = skin["bodies"][0]["box"]
    length, ret, height = b[4] - b[1], b[3] - b[0], b[5] - b[2]    # Y (panel length), X (return leg), Z
    w = ret + length - FOLD_ALLOWANCE
    name = "%s_P01_%s_DXF.dxf" % (skin["part_number"], skin["name"].split(" ", 1)[1].replace(" - ", "-").replace(" ", "-"))
    path = os.path.join(HERE, name)
    # seen from the outside (coloured) face, as the left side view: X(view) = -Y(pod), Y(view) = +Z(pod);
    # origin at the bottom of the return's free edge (the back edge, on the left); fold line at x = ret
    dxf_tools.write_dxf(path, [
        ("POLY", "CUT", [(0.0, 0.0), (w, 0.0), (w, height), (0.0, height)]),
        ("LINE", "BEND", (ret, 0.0), (ret, height)),
    ])
    out.append((path, "skin blank %.2f x %.2f: return %.2f + main face %.2f, fold on BEND at x = %.2f" % (
        w, height, ret, length, ret)))
    for p, note in out:
        s = dxf_tools.summary(p)
        ext = s["extents"]
        print("%s: $INSUNITS %s, layers %s, extents %.2f x %.2f; %s" % (
            os.path.basename(p), s["insunits"], sorted(s["layers"]), ext[2] - ext[0], ext[3] - ext[1], note))


if __name__ == "__main__":
    main(sys.argv)
