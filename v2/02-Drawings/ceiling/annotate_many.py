"""Annotate several started ceiling drawings in one Fusion run (the fair-share queue rule,
PM ruling 2026-11-01: fold work into fewer, bigger runs).

    python3 tools/fusion/run_script.py v2/02-Drawings/ceiling/annotate_many.py \\
        --arg parts=frame_c1,frame_c2,cassette --label "CEILING Engineer" --timeout 1200

For each part key of drawing_specs.SPECS: open its drawing (made by tools/fusion/start_drawing.py)
from Default Project / FocusPod v2, add the views, dimensions, hole table, symbol, notes and
title images and the PDF (make_drawing_ceiling.annotate), save it and close it. A drawing that
fails is closed without saving and the run goes on to the next; the run fails at the end if
any did. Then strip the name field from each PDF with tools/fusion/pdf_clear_field.py.
"""

import importlib
import os
import sys
import time
import traceback

import adsk.core
import adsk.drawing

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
# Fusion keeps modules loaded between runs, and a run from another worktree may have loaded its
# own copy of these: drop any copy from another folder, so the imports below take this
# worktree's files (the drawing scripts here, the ceiling model next to them)
_CAD = os.path.normpath(os.path.join(HERE, "..", "..", "01-CAD-Native", "ceiling"))
for _n, _d in (("drawing_specs", HERE), ("make_drawing_ceiling", HERE), ("render_notes", HERE),
               ("ceiling_model", _CAD), ("ceiling_checks", _CAD), ("ceiling_build", _CAD)):
    _f = getattr(sys.modules.get(_n), "__file__", None)
    if _f and os.path.dirname(os.path.abspath(_f)) != _d:
        del sys.modules[_n]
for _d in (_CAD, HERE):
    if _d in sys.path:
        sys.path.remove(_d)
    sys.path.insert(0, _d)
import drawing_specs as S  # noqa: E402
importlib.reload(S)
import make_drawing_ceiling as MD  # noqa: E402
importlib.reload(MD)

FOLDER = ("Default Project", "FocusPod v2")


def open_drawing(app, name):
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name.split(" v")[0] == name:
            d.activate()
            return d
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == FOLDER[0])
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    found = None
    for _try in range(3):              # the folder's file list can fail while it changes
        try:
            files = [folder.dataFiles.item(i) for i in range(folder.dataFiles.count)]
            found = [f for f in files if f.name == name]
            break
        except RuntimeError:
            time.sleep(2)
            adsk.doEvents()
    if not found:
        raise RuntimeError("drawing %r is not in %s (start it first)" % (name, "/".join(FOLDER)))
    app.data.activeProject = proj
    d = app.documents.open(found[0], True)
    d.activate()
    return d


def run(_context):
    app = adsk.core.Application.get()
    MD.ARGS = ARGS
    failed = []
    for part in [p for p in ARGS["parts"].split(",") if p]:
        name = S.SPECS[part]["drawing"]
        t0 = time.time()
        doc = None
        try:
            doc = open_drawing(app, name)
            MD.annotate(part)
            print("saved %s: %s (%.0f s)" % (name, doc.save("views, dimensions, notes (annotate_many.py)"), time.time() - t0))
            doc.close(False)
        except Exception:                 # noqa: BLE001 (report, close, go on)
            failed.append(part)
            print("FAILED %s:\\n%s" % (name, traceback.format_exc()))
            if doc is not None:
                doc.close(False)
    if failed:
        raise RuntimeError("drawings that failed: %s" % failed)
