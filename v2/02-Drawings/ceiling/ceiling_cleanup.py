"""Tidy CEILING's own documents in the shared Fusion around a drawing run (BASE's base_cleanup.py
pattern, #142).

    python3 tools/fusion/run_script.py v2/02-Drawings/ceiling/ceiling_cleanup.py \\
        --arg close=513102_P01_LINING-RIB-CEILING_CAD --arg delete=513102_P01_LINING-RIB-CEILING_DWG \\
        --label "CEILING Engineer"

close: designs or drawings to close if they are open, by exact name, never with unsaved changes
(one with changes is reported and left alone). start_drawing.py can't close the design it opened
while the new drawing is open, because the open drawing keeps its own copy of the design loaded
(two open documents then carry the name); after annotate_many.py closes the drawing, this closes
the design. Nothing is opened.

delete: drawings to remove from Default Project / FocusPod v2 by exact name, so a drawing can be
started again (start_drawing.py refuses a name that is already there): a sample drawing whose
method changed. Only the ceiling's own drawings are accepted (the DWG names in drawing_specs.py),
and only when no copy is open. Every name given that is not the ceiling's own is refused, so no
other team's document can be touched.
"""

import os
import sys

import adsk.core

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


def own_names():
    designs = {sp["design"] for sp in S.SPECS.values()}
    drawings = {sp["drawing"] for sp in S.SPECS.values()}
    return designs, drawings


def open_docs(app, name):
    return [app.documents.item(i) for i in range(app.documents.count)
            if app.documents.item(i).name.split(" v")[0] == name]


def run(_context):
    app = adsk.core.Application.get()
    designs, drawings = own_names()
    close = [n for n in ARGS.get("close", "").split(",") if n]
    delete = [n for n in ARGS.get("delete", "").split(",") if n]
    foreign = [n for n in close if n not in designs | drawings] + [n for n in delete if n not in drawings]
    if foreign:
        raise RuntimeError("not the ceiling's own documents, refused: %s" % foreign)
    for name in close:
        while True:
            # read the list again after every close: closing a drawing can close other documents with it
            hits = [d for d in open_docs(app, name) if not d.isModified]
            left = [d.name for d in open_docs(app, name) if d.isModified]
            if left:
                print("%s: open with unsaved changes, left open" % ", ".join(left))
            if not hits:
                break
            print("%s: closed %s" % (hits[0].name, hits[0].close(False)))
        if not open_docs(app, name):
            print("%s: not open" % name)
    if not delete:
        return
    for name in delete:
        if open_docs(app, name):
            raise RuntimeError("%s is open; close it before deleting" % name)
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == FOLDER[0])
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    # the shared folder reader (tools/fusion/fusion_folder.py, given to every script by the runner)
    from fusion_folder import read_folder
    files, _unknown, _others = read_folder(folder, stop_when=lambda fs, _u, _o: all(n in fs for n in delete))
    for name in delete:
        hits = files.get(name, [])
        if len(hits) != 1:
            print("%s: %d file(s) of that name in %s, nothing deleted" % (name, len(hits), "/".join(FOLDER)))
            continue
        df = hits[0]
        print("%s: version %s, deleted %s" % (name, df.versionNumber, df.deleteMe()))
