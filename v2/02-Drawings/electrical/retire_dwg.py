"""Free the name of drawing 711001 so start_drawing.py can start it fresh: the old drawing is renamed, kept, never
deleted (a deleted cloud file can't come back). Promoting an old version is not used: Fusion Engineer 2's test on
2026-11-01 got an empty file that wouldn't open (PM warning).

    run inside a lock hold, right before start_drawing.py (the PR notes give the whole sequence):
    python3 tools/fusion/run_script.py v2/02-Drawings/electrical/retire_dwg.py --label "ELECTRICAL Engineer"

It opens no document. It refuses while the drawing is open in Fusion, or when the new name is taken; after the
rename it reads the folder again and checks that the old name is free and the new one is there.
"""

import adsk.core

DWG = "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG"
RETIRED = DWG + "_SUPERSEDED-2026-11-01"
PROJECT, FOLDER = "Default Project", "FocusPod v2"


def listing(app: "adsk.core.Application", want):
    import fusion_folder as ff                     # the shared folder reader, given to every run by run_script.py
    proj = [p for p in app.data.dataProjects if p.name == PROJECT][0]
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER)
    files, unknown, others = ff.read_folder(folder, stop_when=lambda fs, u, o: want(fs) and not ff.could_be(u, o, "f2d"))
    if ff.could_be(unknown, others, "f2d"):
        raise RuntimeError("an entry in %s can't be read and could be a drawing: nothing renamed" % FOLDER)
    return files


def run(_context):
    app = adsk.core.Application.get()
    for d in [app.documents.item(i) for i in range(app.documents.count)]:
        if d.name.split(" v")[0] in (DWG, RETIRED):
            raise RuntimeError("%s is open in Fusion: close it first" % d.name)
    files = listing(app, lambda fs: DWG in fs)
    found = files.get(DWG, [])
    if len(found) != 1:
        raise RuntimeError("%d files are called %s in %s" % (len(found), DWG, FOLDER))
    if RETIRED in files:
        raise RuntimeError("%s is taken already" % RETIRED)
    df = found[0]
    print("%s: version %d; renaming it %s (kept, not deleted)" % (DWG, df.latestVersionNumber, RETIRED))
    df.name = RETIRED
    files = listing(app, lambda fs: RETIRED in fs)
    if DWG in files or RETIRED not in files:
        raise RuntimeError("after the rename the folder has %s: %s, %s: %s" % (
            DWG, DWG in files, RETIRED, RETIRED in files))
    print("renamed: %s is free for start_drawing.py" % DWG)
