"""Rename WALL's superseded cloud documents to NAME_SUPERSEDED-<date> (D-141: cloud files are never deleted, a
deleted file can't come back), so nobody opens one by its old name.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/rename_superseded.py --label "WALL Engineer: rename"

The documents (WALL's own, each made by WALL's scripts) in Default Project / FocusPod v2:
- 211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_CAD and 211601_P01_WALL-CAVITY-FILL-BACK-LOWER-B1_CAD: D-123 cancels the
  panels' fill set numbers (the pieces are numbered parts straight in the panel);
- 211301_P01_WALL-SKIN-SIDE-LOWER-LH_DWG: the old Fusion sheet of L1's skin; D-139 draws it with the generator.
It also lists the folder's other WALL drawing documents (_DWG, 21xxxx and 51xxxx), without touching them.
A document that is open is closed first (it has no unsaved changes, or the run stops); one already renamed is
skipped; a name that isn't in the folder is reported, not guessed at. Nothing else is touched.
"""

import time

import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})
FOLDER = ("Default Project", "FocusPod v2")
NAMES = [n for n in ARGS.get("names", "").split(";") if n] or [
    "211501_P01_WALL-CAVITY-FILL-SIDE-LOWER-LH_CAD",
    "211601_P01_WALL-CAVITY-FILL-BACK-LOWER-B1_CAD",
    "211301_P01_WALL-SKIN-SIDE-LOWER-LH_DWG",
]


def folder(app):
    for i in range(app.data.dataProjects.count):
        p = app.data.dataProjects.item(i)
        if p.name == FOLDER[0]:
            f = p.rootFolder.dataFolders.itemByName(FOLDER[1])
            if f is None:
                raise RuntimeError("no folder %r" % FOLDER[1])
            return f
    raise RuntimeError("no Fusion project called %r" % FOLDER[0])


def superseded_name(names, name, day):
    """NAME_SUPERSEDED-<day>, or with -2, -3... when the folder already has that name (BASE's rule, base_build.py)."""
    base = "%s_SUPERSEDED-%s" % (name, day)
    if base not in names:
        return base
    n = 2
    while "%s-%d" % (base, n) in names:
        n += 1
    return "%s-%d" % (base, n)


def run(_context):
    from fusion_folder import read_folder     # run_script.py makes it importable and loads it fresh every run
    app = adsk.core.Application.get()
    fold = folder(app)
    files, unknown, _others = read_folder(fold, stop_when=lambda f, u, o: all(n in f for n in NAMES))
    names = set(files)
    day = time.strftime("%Y-%m-%d", time.gmtime())
    for name in NAMES:
        found = files.get(name, [])
        if not found:
            print("RENAME|not in the folder: %s (%d entries unreadable)" % (name, len(unknown)))
            continue
        for i in range(app.documents.count - 1, -1, -1):
            d = app.documents.item(i)
            if d.name == name:
                if d.isModified:
                    raise RuntimeError("%s is open with unsaved changes: not touched" % name)
                d.close(False)
        for df in found:
            new = superseded_name(names, name, day)
            df.name = new
            names.add(new)
            print("RENAME|%s -> %s (superseded, not deleted)" % (name, new))
    others = sorted(n for n in names if n.endswith("_DWG") and n[:2] in ("21", "51") and "SUPERSEDED" not in n)
    print("RENAME|WALL drawing documents left as they are: %s" % (", ".join(others) or "none"))
