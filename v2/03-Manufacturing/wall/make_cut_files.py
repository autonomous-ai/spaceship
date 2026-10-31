"""Cut files (DXF, 1:1, mm, layers CUT / BEND / MARK) for a WALL panel (side or back) and its cassette.

    python3 v2/03-Manufacturing/wall/make_cut_files.py 210101 510101      # side panel L1
    python3 v2/03-Manufacturing/wall/make_cut_files.py 210202 510202      # back panel B2

- The tray: Fusion's own flat pattern (export_flat_dxf.py writes it to .raw/), moved onto the project's
  layers with dxf_tools.relayer; its extents are checked against the flat size Fusion reported.
- The ACP skin: the skin isn't sheet metal in Fusion (ACP is V-grooved and folded, not bent), so its blank
  is drawn here from the skin body's sizes in the CAD report: the main face and the 43 mm back return laid
  out flat, outer-face lengths, with the fold (V-groove) on the BEND layer. Fold allowance 0 (assumption):
  the ACP maker's V-groove rule replaces it (HOLD H16). A back panel's skin is flat: a rectangle, with the
  round holes the CAD has in it (B2: ELECTRICAL's inlet and LAN holes).
- The felt, when it has ELECTRICAL's openings (R1, R2, B2, B4): seen from the room, its outline with the
  round holes the CAD has in it and the rectangular openings from the design's el_ parameters (R1's corner
  slot, B2's cut-out for the power unit). A felt with no openings stays a parts-list row (D-89).
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


def felt_file(cass):
    """The felt's cut file when it has ELECTRICAL's openings, else None (a plain rectangle: parts-list row only)."""
    felt = [c for c in cass["components"] if " - FELT - " in c["name"]][0]
    fb = felt["bodies"][0]
    b = fb["box"]
    pv = {q["name"]: q["value"] for q in cass["parameters"]}
    back = felt["part_number"].startswith("5114")
    thick = "y" if back else "x"
    # seen from the room: the back felt with +X to the right; a right-wall felt (room toward -X) with the back
    # end on the left; Y(view) = Z(pod) - the felt's bottom
    if back:
        def view(x, y, z):
            return (x - b[0], z - b[2])
        w = b[3] - b[0]
    else:
        def view(x, y, z):
            return (b[4] - y, z - b[2])
        w = b[4] - b[1]
    height = b[5] - b[2]
    ents = [("POLY", "CUT", [(0.0, 0.0), (w, 0.0), (w, height), (0.0, height)])]
    for h in fb["holes"]:
        if h["axis"] == thick and h["full_circle"]:
            c = [v if v is not None else 0.0 for v in h["centre"]]
            ents.append(("CIRCLE", "CUT", view(*c), h["d"] / 2.0))
    rects = []
    if "el_fs_y0" in pv:                            # R1: the corner slot (FS-CNR)
        yb = pv["pod_d"] / 2.0 - pv["stack_t"]
        rects.append(((yb + pv["el_fs_y0"], yb + pv["el_fs_y1"]), (pv["el_trunk_z"] - pv["el_fs_dz"],
                                                                   pv["el_trunk_z"] + pv["el_fs_dz"])))
    if back and "el_cut_x0" in pv:                 # B2: the power unit cut-out, flush with the tray's
        rects.append(((pv["el_cut_x0"], pv["el_cut_x1"]), (pv["el_cut_z0"], pv["el_cut_z1"])))
    for (a0, a1), (z0, z1) in rects:
        pts = [view(a, a, z) for a, z in ((a0, z0), (a1, z0), (a1, z1), (a0, z1))]
        ents.append(("POLY", "CUT", pts))
    if len(ents) == 1:
        return None
    name = "%s_P01_%s_DXF.dxf" % (felt["part_number"], felt["name"].split(" ", 1)[1].replace(" - ", "-").replace(" ", "-"))
    path = os.path.join(HERE, name)
    dxf_tools.write_dxf(path, ents)
    return (path, "felt blank %.2f x %.2f seen from the room, %d openings (ELECTRICAL)" % (w, height, len(ents) - 1))


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
    skin = [c for c in panel["components"] if c["part_number"].startswith(("2113", "2114"))][0]
    b = skin["bodies"][0]["box"]
    name = "%s_P01_%s_DXF.dxf" % (skin["part_number"], skin["name"].split(" ", 1)[1].replace(" - ", "-").replace(" ", "-"))
    path = os.path.join(HERE, name)
    if skin["part_number"].startswith("2114"):
        # back panel: flat, seen from the outside face (from +Y): X(view) = -X(pod), Y(view) = +Z(pod)
        w, height = b[3] - b[0], b[5] - b[2]
        rounds = [("CIRCLE", "CUT", (b[3] - h["centre"][0], h["centre"][2] - b[2]), h["d"] / 2.0)
                  for h in skin["bodies"][0]["holes"] if h["axis"] == "y" and h["full_circle"]]
        dxf_tools.write_dxf(path, [("POLY", "CUT", [(0.0, 0.0), (w, 0.0), (w, height), (0.0, height)])] + rounds)
        seam = "right" if b[0] + b[3] > 0 else "left"         # seen from outside (+X to the left), the seam edge
        out.append((path, "skin blank %.2f x %.2f, flat; the closing-seam edge (1.62 past the frame) on the %s%s" % (
            w, height, seam, "; %d round holes (%s)" % (len(rounds), ", ".join(
                "Ø%g at %.2f, %.2f" % (e[3] * 2, e[2][0], e[2][1]) for e in rounds)) if rounds else "")))
    else:
        length, ret, height = b[4] - b[1], b[3] - b[0], b[5] - b[2]    # Y (panel length), X (return leg), Z
        w = ret + length - FOLD_ALLOWANCE
        # seen from the outside (coloured) face: from -X for the left wall (the back edge on the left), from +X
        # for the right wall (the back edge on the right); X(view) along the panel, Y(view) = +Z(pod); origin at
        # the blank's bottom left; fold line where the return meets the main face
        right = b[0] + b[3] > 0
        fold = w - ret if right else ret
        dxf_tools.write_dxf(path, [
            ("POLY", "CUT", [(0.0, 0.0), (w, 0.0), (w, height), (0.0, height)]),
            ("LINE", "BEND", (fold, 0.0), (fold, height)),
        ])
        out.append((path, "skin blank %.2f x %.2f: return %.2f + main face %.2f, fold on BEND at x = %.2f (%s wall)" % (
            w, height, ret, length, fold, "right" if right else "left")))
    felt_dxf = felt_file(cass)
    if felt_dxf:
        out.append(felt_dxf)
    for p, note in out:
        s = dxf_tools.summary(p)
        ext = s["extents"]
        print("%s: $INSUNITS %s, layers %s, extents %.2f x %.2f; %s" % (
            os.path.basename(p), s["insunits"], sorted(s["layers"]), ext[2] - ext[0], ext[3] - ext[1], note))


if __name__ == "__main__":
    main(sys.argv)
