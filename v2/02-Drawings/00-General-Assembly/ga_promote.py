"""Make a drawing's sheet again without deleting anything: promote an earlier version.

    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_promote.py \\
        --arg name=100000_P04_POD-GENERAL-ASSEMBLY_DWG --arg version=1 --arg latest=3

Version 1 of a GA drawing is the empty sheet start_drawing.py saved. Promoting it
makes a new newest version with that empty sheet, so ga_elevations.py or
ga_section_sheet.py can draw it again; the versions in between stay in the
history. Why not delete the sheet: on 2026-10-31 deleting the old sheet and
saving crashed Fusion (PM: redo without deleting a sheet).

Refuses when the drawing is open in Fusion (an open copy would keep the old
version), when its newest version isn't `latest` (someone else changed it), or
when `version` isn't there. Run with no document open; it opens nothing.
"""

import time

import adsk
import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})
FOLDER = ("Default Project", "FocusPod v2")


def find(folder, name):
    """The DataFile called name (the shared check, fusion_folder.py, given to every
    script by run_script.py, reads the folder safely after a restart)."""
    from fusion_folder import read_folder
    files, _unknown, _others = read_folder(folder, stop_when=lambda fs, u, o: name in fs)
    hits = files.get(name, [])
    if len(hits) != 1:
        raise RuntimeError("expected one %s in %s, found %d" % (name, "/".join(FOLDER), len(hits)))
    return hits[0]


def run(_context):
    app = adsk.core.Application.get()
    name, version, latest = ARGS["name"], int(ARGS["version"]), int(ARGS["latest"])
    for i in range(app.documents.count):
        if app.documents.item(i).name == name:
            raise RuntimeError("%s is open in Fusion; close it before promoting a version" % name)
    proj = [p for p in app.data.dataProjects if p.name == FOLDER[0]][0]
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    df = find(folder, name)
    if df.latestVersionNumber != latest:
        raise RuntimeError("%s is at version %d, not %d as expected; nothing promoted"
                           % (name, df.latestVersionNumber, latest))
    versions = df.versions
    old = [versions.item(i) for i in range(versions.count) if versions.item(i).versionNumber == version]
    if len(old) != 1:
        raise RuntimeError("%s has no single version %d (%d versions)" % (name, version, versions.count))
    if not old[0].promote():
        raise RuntimeError("promoting version %d of %s failed" % (version, name))
    newest = latest
    for _ in range(30):                     # up to a minute for the new version to show
        adsk.doEvents()
        newest = find(folder, name).latestVersionNumber
        if newest > latest:
            break
        time.sleep(2)
    else:
        raise RuntimeError("promoted version %d of %s, but the newest is still %d after a minute"
                           % (version, name, newest))
    print("promoted %s version %d: the newest is now version %d (versions %d to %d stay in the history)"
          % (name, version, newest, version + 1, latest))
