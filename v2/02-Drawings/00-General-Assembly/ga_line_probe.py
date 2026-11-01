"""Line probe for the GA drawings, on the active drawing: how DrawingSketch Lines.add
(a preview API) keeps point chains, seen in a PDF export. A temporary sheet gets one sketch per case (each
sketch is its own PDF layer, named "PROBE <case>"); the sheet is exported; the
drawing is closed WITHOUT saving (PM D-98: nothing is kept), even when a case fails.

Why: GA sheet 1's 5-point closed symbol came out as a triangle in its PDF, and the
B-B hatch (2-point lines, many per sketch, in strips under 1 mm wide) came out as
short vertical scraps (2026-10-31). So each point form is tried three ways: five
separate lines, a hatch of 20 x 20 mm (about 40 lines in one sketch), and a hatch
of a 30 x 0.44 mm strip (tiny lines, as on the B-B walls).
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_line_probe.py \\
        --doc 100000_P04_POD-SECTION-BB_DWG --arg pdf=OUT.pdf
    python3 v2/02-Drawings/00-General-Assembly/ga_pdf_check.py probe OUT.pdf MODE.json

OUT.pdf.json gets the cases; MODE.json the form to use (--arg line_mode_file).
"""
import json
import os
import time

import adsk
import adsk.core
import adsk.drawing

A = globals().get("SCRIPT_ARGS", {})
_ns: dict = {}
with open(os.path.join(A.get("repo_root", "."), "tools", "fusion", "hatch.py"), encoding="utf-8") as _fh:
    exec(compile(_fh.read(), "hatch.py", "exec"), _ns)
hatch_segments, chain_for = _ns["hatch_segments"], _ns["chain_for"]
fill_lines, hatch_chains = _ns["fill_lines"], _ns["chains"]

FORMS = ["plain", "mid", "dup-first", "dup-last"]


def cases():
    """[(label, [chain, ...], own_sketch_per_chain)]: each chain is one Lines.add call."""
    out = []
    for r, form in enumerate(FORMS):
        y = 20.0 + 60.0 * r
        small = [chain_for((20.0 + 12 * k, y), (30.0 + 12 * k, y + 20.0), form) for k in range(5)]
        sq = [(100.0, y), (120.0, y), (120.0, y + 20.0), (100.0, y + 20.0)]
        many = [chain_for(a, b, form) for a, b in hatch_segments(sq, spacing=0.7, angle_deg=45.0)]
        strip = [(140.0, y), (170.0, y), (170.0, y + 0.44), (140.0, y + 0.44)]
        thin = [chain_for(a, b, form) for a, b in hatch_segments(strip, spacing=0.5, angle_deg=135.0)]
        out += [("%s small x5" % form, small, False), ("%s many" % form, many, False),
                ("%s thin" % form, thin, False)]
    # one Lines.add per sketch, many lines joined back and forth (hatch.chains): a 45 degree
    # hatch of a square, and a thin strip filled along its length (both as the GA uses them)
    sq = [(200.0, 140.0), (220.0, 140.0), (220.0, 160.0), (200.0, 160.0)]
    strip = [(240.0, 140.0), (270.0, 140.0), (270.0, 142.0), (240.0, 142.0)]
    out += [("chain zigzag", hatch_chains(hatch_segments(sq, spacing=0.7, angle_deg=45.0), sq), True),
            ("chain strip", hatch_chains(fill_lines(strip), strip), True)]
    out += [("own sketch x5", [[(200.0 + 12 * k, 20.0), (210.0 + 12 * k, 40.0)] for k in range(5)], True),
            ("3pt open", [[(200.0, 80.0), (215.0, 100.0), (230.0, 80.0)]], False),
            ("4pt open", [[(240.0, 85.0), (260.0, 80.0), (260.0, 100.0), (240.0, 95.0)]], False),
            ("5pt closed", [[(270.0, 85.0), (290.0, 80.0), (290.0, 100.0), (270.0, 95.0), (270.0, 85.0)]], False)]
    return [(label, [[list(p) for p in ch] for ch in chains], own) for label, chains, own in out]


def run(_c):
    app = adsk.core.Application.get()
    doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
    if doc is None:
        raise RuntimeError("open a drawing first")
    name = doc.name
    try:
        dwg = doc.drawing
        inp = dwg.sheets.createInput()
        inp.name = "LINE PROBE"
        sh = dwg.sheets.add(inp)
        want = adsk.drawing.SheetSizes.A3ISOSheetSize
        sh.sheetSize = want
        for _ in range(10):
            adsk.doEvents()
            if sh.sheetSize == want and abs(sh.width - 420) <= 1:
                break
            time.sleep(0.5)
        print("probe sheet %g x %g mm" % (sh.width, sh.height))
        report, all_cases = [], cases()
        for label, chains, own in all_cases:
            sk = None
            made = 0
            for j, ch in enumerate(chains):
                if sk is None or own:
                    sk = sh.sketches.add("PROBE %s%s" % (label, (" %d" % j) if own else ""))
                if sk.lines.add([adsk.core.Point2D.create(x, y) for x, y in ch]) is not None:
                    made += 1
            adsk.doEvents()
            report.append({"case": label, "asked": len(chains), "made": made,
                           "count": sk.lines.count if sk else 0})
            print("case %s: %d of %d made, last sketch holds %d" % (label, made, len(chains),
                                                                   sk.lines.count if sk else 0))
        opts = dwg.exportManager.createPDFExportOptions(A["pdf"])
        opts.sheetsToExport = adsk.drawing.PDFSheetsExport.RangePDFSheetsExport
        opts.sheetRange = str(dwg.sheets.count)
        opts.openPDF = False
        ok = dwg.exportManager.execute(opts)
        print("probe pdf %s: %s" % (A["pdf"], ok))
        with open(A["pdf"] + ".json", "w", encoding="utf-8") as fh:
            json.dump({"cases": [list(c) for c in all_cases], "report": report}, fh)
    finally:
        print("closed %s without saving: %s" % (name, doc.close(False)))
