"""Export the sheet-metal parts' flat patterns from the active WALL design as raw Fusion DXFs: a cassette's tray
(exactly one), and a lower panel's cassette ledge (the Lead's ruling of 2026-11-01; a panel with no sheet-metal part
exports nothing).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/export_flat_dxf.py --read-only \
        --doc 510101_P01_LINING-CASSETTE-SIDE-LOWER-LH_CAD --arg pn=510101 --close

Writes v2/03-Manufacturing/wall/.raw/<tray pn>_<rev>_<NAME>_flat-fusion.dxf (git-ignored). The offline
step make_cut_files.py moves it onto the CUT / BEND / MARK layers and checks it. Nothing in the design
changes.
"""

import os
import re

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design.rootComponent.partNumber != ARGS.get("pn"):
        raise RuntimeError("active design's root part number is %r, not %r" % (design.rootComponent.partNumber,
                                                                              ARGS.get("pn")))
    flat = [c for c in design.allComponents if c != design.rootComponent and c.flatPattern]
    trays = [c for c in flat if c.partNumber.startswith("511")]
    if ARGS.get("pn", "").startswith("51") and len(trays) != 1:
        raise RuntimeError("expected one tray component with a flat pattern, found %d" % len(trays))
    for part in flat:
        fp = part.flatPattern
        b = fp.flatBody.boundingBox
        size = [round((getattr(b.maxPoint, a) - getattr(b.minPoint, a)) * 10.0, 2) for a in "xyz"]
        name = "%s_P01_%s" % (part.partNumber, re.sub(r"[^A-Z0-9]+", "-", part.name.split(" ", 1)[1]).strip("-"))
        rel = "v2/03-Manufacturing/wall/.raw/%s_flat-fusion.dxf" % name
        path = os.path.join(ARGS["repo_root"], rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        em = design.exportManager
        ok = em.execute(em.createDXFFlatPatternExportOptions(path, fp))
        print("FLAT|%s|%s" % (part.partNumber, size))
        print("export %s: %s" % (rel, ok))
        if not ok:
            raise RuntimeError("flat pattern export failed for %s" % part.partNumber)
    if not flat:
        print("FLAT|none: no sheet-metal part in this design")
