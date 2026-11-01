"""Export a saved ceiling drawing's PDF again, after letting Fusion settle, without changing the drawing.

    python3 tools/fusion/run_script.py v2/02-Drawings/ceiling/reexport_pdf.py --arg parts=tray --arg wait=10 \\
        --label "CEILING Engineer"

For each part key: open its drawing from Default Project / FocusPod v2 (or take it if it's open already), run
Fusion's event loop for `wait` seconds, export the PDF to .raw/<drawing>_REEXPORT.pdf and close the drawing
without saving. Made to learn whether the tray's empty hole table (its second drawing, 2026-11-01) was only not
filled yet when the annotate run exported it straight after making it: check_drawing_pdf.py --pdf reads it back.
Only the ceiling's own drawings (drawing_specs.SPECS) can be named.
"""

import os
import sys
import time

import adsk.core
import adsk.drawing

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
_CAD = os.path.normpath(os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
for _n, _d in (("drawing_specs", HERE), ("ceiling_model", _CAD)):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != _d:
        del sys.modules[_n]
for _d in (_CAD, HERE):
    if _d in sys.path:
        sys.path.remove(_d)
    sys.path.insert(0, _d)
import drawing_specs as S  # noqa: E402

FOLDER = ("Default Project", "FocusPod v2")


def open_drawing(app, name):
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name.split(" v")[0] == name:
            if d.isModified:
                raise RuntimeError("%s is open with unsaved changes; left alone" % d.name)
            d.activate()
            return d, False
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == FOLDER[0])
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    from fusion_folder import read_folder
    files, _unknown, _others = read_folder(folder, stop_when=lambda fs, _u, _o: name in fs)
    hits = files.get(name, [])
    if len(hits) != 1:
        raise RuntimeError("%d file(s) called %s in %s" % (len(hits), name, "/".join(FOLDER)))
    d = app.documents.open(hits[0], True)
    d.activate()
    return d, True


def run(_context):
    app = adsk.core.Application.get()
    wait = float(ARGS.get("wait", "10"))
    parts = [p for p in ARGS.get("parts", "").split(",") if p]
    unknown = [p for p in parts if p not in S.SPECS]
    if not parts or unknown:
        raise RuntimeError("name the ceiling's drawings by their spec keys; unknown: %s" % unknown)
    for part in parts:
        name = S.SPECS[part]["drawing"]
        doc, opened = open_drawing(app, name)
        try:
            dwg = adsk.drawing.Drawing.cast(app.activeProduct)
            if dwg is None:
                raise RuntimeError("%s did not open as a drawing" % name)
            t0 = time.time()
            while time.time() - t0 < wait:
                adsk.doEvents()
                time.sleep(0.25)
            sheet = dwg.activeSheet
            print("%s: views %d, dimensions %d, hole tables %d, after %.0f s" % (
                doc.name, sheet.views.count, sheet.drawingDimensions.count, sheet.holeTables.count, wait))
            raw = os.path.join(HERE, ".raw", "%s_REEXPORT.pdf" % name)
            os.makedirs(os.path.dirname(raw), exist_ok=True)
            opts = dwg.exportManager.createPDFExportOptions(raw)
            opts.openPDF = False
            opts.useLineWeights = True
            if not dwg.exportManager.execute(opts):
                raise RuntimeError("PDF export failed")
            print("re-exported:", raw)
        finally:
            if opened:
                print("%s closed without saving: %s" % (name, doc.close(False)))
