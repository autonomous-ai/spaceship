"""Step pictures for the assembly guide, from the Fusion model.

    python3 tools/fusion/run_script.py v2/02-Drawings/30-Assembly-Instructions/step_pictures.py \
        --label "Packing and Assembly Engineer"
    python3 v2/07-Packaging/pack.py          # puts each picture under its step in the guide

Reads 100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json, which v2/07-Packaging/pack.py writes from its label map.
Opens the skeleton's cloud design 100000_P04_POD-SKELETON_CAD from "Default Project/FocusPod v2" itself, because a STEP
import drops the body names (first run, 2026-10-31). It refuses to start when that design is already open in Fusion, so
it never touches anyone's session; it changes only what shows (light bulbs, opacity, the camera), never saves, and
closes the design without saving. For each step it shows the bodies fitted so far: the step's new bodies solid, the
earlier ones faded. It hides the layout grid and its ruler labels (and turns them back on at the end), turns the camera (from behind for
the shell, from the front for the decor and the glass, from above with the ceiling and front hidden for the linings) and saves img/100000_P04_POD-ASSEMBLY-GUIDE-STEP-NN_IMG.png.

Fusion draws pictures only on a live screen, so run it when the screen is unlocked (D-84). The bodies are the
skeleton's envelopes; pictures of the parts themselves replace these as each part's CAD merges.
"""

import json
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "100000_P04_POD-SKELETON_CAD"
FOLDER = "Default Project/FocusPod v2"
DATA = os.path.join(HERE, "100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json")
WIDTH, HEIGHT = 1600, 1000
# Eye positions in mm, pod coordinates (conventions section 4: +X right, +Y back, +Z up); every view looks at TARGET.
VIEWS = {
    "back": (-4200.0, 5200.0, 4300.0),
    "front": (3600.0, -5600.0, 3400.0),
    "inside": (600.0, -3200.0, 6200.0),
}
TARGET = (0.0, 0.0, 1100.0)
FADED = 0.35
INSIDE_HIDE = ("C1 ENVELOPE", "C2 ENVELOPE", "DL FACETED", "DR FACETED", "DT FACETED", "DOOR GLASS", "FIXED GLASS",
               "KICK ENVELOPE")


def bodies_by_name(root):
    out = {}
    for b in root.bRepBodies:
        out.setdefault(b.name, []).append(b)
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            out.setdefault(b.name, []).append(b)
    return out


def open_skeleton(app):
    """Open the skeleton's cloud design; refuse when it is open already (someone else's session)."""
    for i in range(app.documents.count):
        if app.documents.item(i).name == DOC_NAME:
            raise RuntimeError("%s is open in Fusion already; not touching it. Close it, then run again." % DOC_NAME)
    parts = FOLDER.split("/")
    proj = next((app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)
                 if app.data.dataProjects.item(i).name == parts[0]), None)
    if proj is None:
        raise RuntimeError("no Fusion project called %r" % parts[0])
    folder = proj.rootFolder
    for name in parts[1:]:
        folder = folder.dataFolders.itemByName(name)
        if folder is None:
            raise RuntimeError("no folder %r in %r" % (name, FOLDER))
    files, unreadable = [], 0
    for i in range(folder.dataFiles.count):
        try:   # one unreadable entry (being uploaded, deleted) must not stop the rest (as the runner does, PR #86)
            f = folder.dataFiles.item(i)
            if f.name == DOC_NAME:
                files.append(f)
        except Exception:
            unreadable += 1
    if unreadable:
        print("%d entries of %s could not be read; skipped" % (unreadable, FOLDER))
    if len(files) != 1:
        raise RuntimeError("%d files called %s in %s" % (len(files), DOC_NAME, FOLDER))
    app.data.activeProject = proj
    doc = app.documents.open(files[0], True)
    if doc is None:
        raise RuntimeError("could not open %s" % DOC_NAME)
    doc.activate()
    print("opened %s version %s (read only in practice: never saved)" % (DOC_NAME, files[0].versionNumber))
    return doc


def hide_helpers(root):
    comps = [root] + [o.component for o in root.allOccurrences]
    for c in comps:
        for attr in ("isSketchFolderLightBulbOn", "isConstructionFolderLightBulbOn", "isOriginFolderLightBulbOn",
                     "isJointsFolderLightBulbOn"):
            try:
                setattr(c, attr, False)
            except Exception:   # a folder this component doesn't have; nothing to hide
                pass


def set_opacity(body, value):
    """Fade a body; if Fusion won't set opacity on this body, it just stays solid (the picture still shows the step)."""
    try:
        body.opacity = value
    except Exception:
        pass


def hide_grid(app):
    """Turn the layout grid and its ruler labels off for the pictures; returns a function that turns them back on.
    The grid is an application-wide setting, so the run always puts it back for everyone else using Fusion.
    It prints what it finds, so a run that can't switch it off still tells us where to look."""
    ui = app.userInterface
    undo, report = [], []
    for i in range(ui.commandDefinitions.count):
        try:
            cd = ui.commandDefinitions.item(i)
            name = (cd.name or "").lower()
            if "grid" not in name and "grid" not in cd.id.lower():
                continue
            ctl = cd.controlDefinition
            checked = getattr(ctl, "isChecked", None)
            report.append("%s | %s | %s | checked=%r" % (cd.id, cd.name, type(ctl).__name__ if ctl else None, checked))
            if checked is True and "layout grid" in name and "lock" not in name and "snap" not in name:
                cd.execute()
                for _ in range(3):
                    adsk.doEvents()
                after = getattr(ctl, "isChecked", None)
                if after is True:   # the command didn't toggle it: try the check box itself
                    try:
                        ctl.isChecked = False
                        adsk.doEvents()
                    except Exception:
                        pass
                    after = getattr(ctl, "isChecked", None)
                report.append("  turned off: %r" % (after is False))
                if after is False:
                    undo.append(cd)
        except Exception as e:   # one odd command must not stop the pictures
            report.append("  (skipped one command: %s)" % type(e).__name__)
    print("GRID: " + "; ".join(report) if report else "GRID: no grid command found")

    def restore():
        for cd in undo:
            try:
                cd.execute()
                for _ in range(3):
                    adsk.doEvents()
                print("GRID: %s back on" % cd.name)
            except Exception as e:
                print("GRID: could not turn %s back on: %s" % (cd.name, e))
    return restore


def point_cm(p_mm):
    return adsk.core.Point3D.create(p_mm[0] / 10.0, p_mm[1] / 10.0, p_mm[2] / 10.0)


def run(_context):
    app = adsk.core.Application.get()
    repo = ARGS.get("repo_root") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    doc = open_skeleton(app)
    restore_grid = lambda: None
    try:
        restore_grid = hide_grid(app)
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        hide_helpers(design.rootComponent)
        named = bodies_by_name(design.rootComponent)
        wanted = {b for s in data["steps"] for b in s["new"]}
        missing = sorted(wanted - set(named))
        if missing:
            raise RuntimeError("bodies not found in the STEP: %s" % missing)
        for group in named.values():
            for body in group:
                body.isLightBulbOn = False
        vp = app.activeViewport
        shown, made = [], 0
        for s in data["steps"]:
            for name in shown:
                for body in named[name]:
                    set_opacity(body, FADED)
            for name in s["new"]:
                for body in named[name]:
                    set_opacity(body, 1.0)
            shown += s["new"]
            hide = INSIDE_HIDE if s["view"] == "inside" else ()
            for name in shown:
                for body in named[name]:
                    body.isLightBulbOn = name not in hide
            cam = vp.camera
            cam.eye = point_cm(VIEWS[s["view"]])
            cam.target = point_cm(TARGET)
            cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
            cam.isSmoothTransition = False
            vp.camera = cam
            vp.fit()
            out = os.path.join(repo, s["image"])
            os.makedirs(os.path.dirname(out), exist_ok=True)
            if not vp.saveAsImageFile(out, WIDTH, HEIGHT):
                raise RuntimeError("Fusion saved no picture for step %d; is the screen unlocked?" % s["step"])
            made += 1
            print("STEP %d: %s (%d new bodies, %s view)" % (s["step"], s["image"], len(s["new"]), s["view"]))
        print("PICTURES: %d of %d" % (made, len(data["steps"])))
    finally:
        restore_grid()
        doc.close(False)
