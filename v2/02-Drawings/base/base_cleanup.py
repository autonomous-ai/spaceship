"""Tidy BASE's own documents in the shared Fusion before a drawing redo.

    python3 tools/fusion/run_script.py v2/02-Drawings/base/base_cleanup.py \
        --arg close_prefixes=111101_P01_,111103_P01_ --arg supersede=110103_P01_BASE-BAND-ASSY-BACK_DWG

close_prefixes: close every open document whose name starts with one of these BASE part numbers
(designs a drawing start left open, a drawing whose annotate run failed), dropping unsaved changes.
supersede: BASE's own cloud files, by exact name in Default Project / FocusPod v2, to rename
NAME_SUPERSEDED-<date> (-2, -3... if that name is taken), so a new start can make NAME again. Cloud
files are never deleted (PM rule, 2026-11-01: a deleted file can't come back); the drawing register
marks the old one superseded. Only BASE part numbers (11xxxx) are accepted, so no other team's
document is touched.
"""

import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})
CLOUD = ("Default Project", "FocusPod v2")


def own(name):
    return name[:2] == "11" and name[:6].isdigit() and name[6:11] == "_P01_"


def run(_context):
    app = adsk.core.Application.get()
    prefixes = [p for p in ARGS.get("close_prefixes", "").split(",") if p[:2] == "11" and p[:6].isdigit()]
    if ARGS.get("delete"):
        raise RuntimeError("delete is gone: cloud files are never deleted (PM rule); use supersede")
    olds = [n for n in ARGS.get("supersede", "").split(",") if n and own(n)]
    closed = []
    for i in range(app.documents.count - 1, -1, -1):
        d = app.documents.item(i)
        if any(d.name.startswith(p) for p in prefixes):
            closed.append(d.name)
            d.close(False)
    print("closed %d of our own documents: %s" % (len(closed), ", ".join(closed) or "none"))
    if not olds:
        return
    folder = None
    for p in app.data.dataProjects:
        if p.name == CLOUD[0]:
            folder = p.rootFolder.dataFolders.itemByName(CLOUD[1])
    if folder is None:
        raise RuntimeError("no folder %s / %s" % CLOUD)
    import time
    import fusion_folder              # the shared reader (#213): one listing fetch per scan
    print("folder reader: %s" % fusion_folder.__file__)
    files, _unknown, _others = fusion_folder.read_folder(folder, wait_s=0)
    names = set(files)
    day = time.strftime("%Y-%m-%d", time.gmtime())
    done = []
    for n in olds:
        for df in files.get(n, []):
            base, k = "%s_SUPERSEDED-%s" % (n, day), 2
            new = base
            while new in names:
                new, k = "%s-%d" % (base, k), k + 1
            df.name = new
            names.add(new)
            done.append("%s -> %s" % (n, new))
    print("renamed our own cloud files (superseded, not deleted): %s" % ("; ".join(done) or "none"))
