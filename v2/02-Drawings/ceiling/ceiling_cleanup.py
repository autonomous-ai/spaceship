"""Tidy CEILING's own documents in the shared Fusion around a drawing run (BASE's base_cleanup.py
pattern, #142).

    python3 tools/fusion/run_script.py v2/02-Drawings/ceiling/ceiling_cleanup.py \\
        --arg close=513101_P01_LINING-TRAY-CEILING_CAD --arg supersede=513101_P01_LINING-TRAY-CEILING_DWG \\
        --label "CEILING Engineer"

close: designs or drawings to close if they are open, by exact name, never with unsaved changes
(one with changes is reported and left alone). start_drawing.py can't close the design it opened
while the new drawing is open, because the open drawing keeps its own copy of the design loaded
(two open documents then carry the name); after annotate_many.py closes the drawing, this closes
the design. Nothing is opened.

supersede: drawings to rename in Default Project / FocusPod v2 to NAME_SUPERSEDED-<UTC date> (then -2,
-3 while that name is taken), so the drawing can be started again under its proper name
(start_drawing.py refuses a name that is already there). Nothing is ever deleted: the PM's rule
(2026-11-01) keeps every cloud file, since a deleted file can't come back; the old one is recorded in
DRAWING-REGISTER.md. After the renames the folder is read again until the old names are gone, so the
start that follows finds the name free. Only the ceiling's own drawings are accepted (the DWG names in
drawing_specs.py), and only when no copy is open; every other name is refused, so no other team's
document can be touched. A rename keeps links: anything that inserted the old drawing still shows it.
"""

import os
import sys
import time

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


def superseded_name(name, taken, date):
    """NAME_SUPERSEDED-<date>, or with -2, -3 ... when that name is already in the folder."""
    base = "%s_SUPERSEDED-%s" % (name, date)
    if base not in taken:
        return base
    k = 2
    while "%s-%d" % (base, k) in taken:
        k += 1
    return "%s-%d" % (base, k)


def run(_context):
    app = adsk.core.Application.get()
    designs, drawings = own_names()
    if ARGS.get("delete"):
        raise RuntimeError("delete= is gone: the PM's rule (2026-11-01) keeps every cloud file; "
                           "use supersede= (renames the old drawing NAME_SUPERSEDED-<date>)")
    close = [n for n in ARGS.get("close", "").split(",") if n]
    supersede = [n for n in ARGS.get("supersede", "").split(",") if n]
    foreign = [n for n in close if n not in designs | drawings] + [n for n in supersede if n not in drawings]
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
    if not supersede:
        return
    for name in supersede:
        if open_docs(app, name):
            raise RuntimeError("%s is open; close it before renaming it" % name)
    proj = next(app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                if app.data.dataProjects.item(i).name == FOLDER[0])
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    # the shared folder reader (tools/fusion/fusion_folder.py, given to every script by the runner)
    from fusion_folder import read_folder
    files, _unknown, _others = read_folder(folder, stop_when=lambda fs, _u, _o: all(n in fs for n in supersede))
    date = time.strftime("%Y-%m-%d", time.gmtime())
    renamed = []
    for name in supersede:
        hits = files.get(name, [])
        if len(hits) != 1:
            print("%s: %d file(s) of that name in %s, nothing renamed" % (name, len(hits), "/".join(FOLDER)))
            continue
        df = hits[0]
        new = superseded_name(name, set(files), date)
        version = df.versionNumber
        df.name = new
        renamed.append(name)
        print("%s: version %s, renamed %s" % (name, version, new))
    if not renamed:
        return
    # the folder listing can lag a rename: read it again until the old names are gone
    for _ in range(6):
        files, _unknown, _others = read_folder(folder, stop_when=lambda fs, _u, _o: not any(n in fs for n in renamed))
        still = [n for n in renamed if n in files]
        if not still:
            print("folder read again: %s free" % ", ".join(renamed))
            return
        time.sleep(5)
    raise RuntimeError("still listed after the rename: %s" % still)
