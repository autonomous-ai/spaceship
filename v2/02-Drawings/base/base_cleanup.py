"""Tidy BASE's own documents in the shared Fusion before a drawing redo.

    python3 tools/fusion/run_script.py v2/02-Drawings/base/base_cleanup.py \
        --arg close_prefixes=111101_P01_,111103_P01_ --arg delete=111101_P01_BASE-BAND-TUBE-SIDE-LH_DWG

close_prefixes: close every open document whose name starts with one of these BASE part numbers
(designs a drawing start left open, a drawing whose annotate run failed), dropping unsaved changes.
delete: BASE's own cloud files to remove by exact name in Default Project / FocusPod v2 (an empty
drawing left by a failed run, so a new start can make it again). Only BASE part numbers (11xxxx)
are accepted, so no other team's document is touched.
"""

import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})
CLOUD = ("Default Project", "FocusPod v2")


def own(name):
    return name[:2] == "11" and name[:6].isdigit() and name[6:11] == "_P01_"


def run(_context):
    app = adsk.core.Application.get()
    prefixes = [p for p in ARGS.get("close_prefixes", "").split(",") if p[:2] == "11" and p[:6].isdigit()]
    deletes = [n for n in ARGS.get("delete", "").split(",") if n and own(n)]
    closed = []
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        if any(d.name.startswith(p) for p in prefixes):
            closed.append(d.name)
            d.close(False)
    print("closed %d of our own documents: %s" % (len(closed), ", ".join(closed) or "none"))
    if not deletes:
        return
    folder = None
    for p in app.data.dataProjects:
        if p.name == CLOUD[0]:
            folder = p.rootFolder.dataFolders.itemByName(CLOUD[1])
    if folder is None:
        raise RuntimeError("no folder %s / %s" % CLOUD)
    import fusion_folder              # the shared reader (#213): one listing fetch per scan
    print("folder reader: %s" % fusion_folder.__file__)
    files, _unknown, _others = fusion_folder.read_folder(folder, wait_s=0)
    gone = []
    for n in deletes:
        for df in files.get(n, []):
            df.deleteMe()
            gone.append(n)
    print("deleted our own cloud files: %s" % (", ".join(gone) or "none"))
