"""Make the empty first version of drawing 711001 its newest version again, so make_body_drawing.py can draw the
sheet from empty (the GA team's method, PM agreed 2026-10-31: never delete a sheet; a sheet delete then save
crashed Fusion).

    run inside a lock hold, right before make_body_drawing.py (views_redo.sh in the PR notes):
    python3 tools/fusion/run_script.py v2/02-Drawings/electrical/promote_dwg_v1.py --label "ELECTRICAL Engineer"

It opens no document: it finds the drawing in Default Project / FocusPod v2, lists its versions, promotes
version 1 (the empty A2 sheet start_drawing saved) and reads the folder again to check that the newest version
is one higher than before. It refuses while the drawing is open in Fusion (an open copy keeps its old version).
make_body_drawing.py then refuses a sheet that isn't empty, so a wrong version is never drawn on.
"""

import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})
DWG = "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_DWG"
PROJECT, FOLDER = "Default Project", "FocusPod v2"


def _ff():
    """The shared folder reader (tools/fusion/fusion_folder.py), given to every run by run_script.py."""
    import fusion_folder
    return fusion_folder


def find(app: "adsk.core.Application"):
    proj = [p for p in app.data.dataProjects if p.name == PROJECT][0]
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER)
    ff = _ff()
    files, _unknown, _others = ff.read_folder(folder, stop_when=lambda fs, u, o: DWG in fs)
    found = files.get(DWG, [])
    if len(found) != 1:
        raise RuntimeError("%d files are called %s in %s" % (len(found), DWG, FOLDER))
    return found[0]


def run(_context):
    app = adsk.core.Application.get()
    for d in [app.documents.item(i) for i in range(app.documents.count)]:
        if d.name.split(" v")[0] == DWG:
            raise RuntimeError("%s is open in Fusion (%s): close it first" % (DWG, d.name))
    df = find(app)
    before = df.latestVersionNumber
    others = df.versions
    versions = {v.versionNumber: v for v in [others.item(i) for i in range(others.count)] + [df]}
    print("%s: versions %s, newest %d" % (DWG, sorted(versions), before))
    if 1 not in versions:
        raise RuntimeError("version 1 of %s not found" % DWG)
    if before == 1:
        print("version 1 is already the newest: nothing to do")
        return
    if not versions[1].promote():
        raise RuntimeError("promote of version 1 failed")
    after = find(app).latestVersionNumber
    print("promoted version 1: the newest is now version %d (was %d)" % (after, before))
    if after != before + 1:
        raise RuntimeError("the newest version is %d, not %d, after the promote" % (after, before + 1))
