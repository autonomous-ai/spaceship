"""Step pictures for the assembly guide, from the Fusion model, in two parts:

    python3 tools/fusion/run_script.py v2/02-Drawings/30-Assembly-Instructions/step_pictures.py \
        --arg out_dir=/some/scratch/folder --label "Packing and Assembly Engineer"
    python3 v2/02-Drawings/30-Assembly-Instructions/clean_pictures.py /some/scratch/folder   # writes img/
    python3 v2/07-Packaging/pack.py                     # puts each picture under its step in the guide

A sample first (AGENTS.md: prove a method on a sample before using it at scale): add --arg steps=2,11,14 to the run,
and look at what clean_pictures.py writes (with --out to a scratch folder) before the full set.

Reads 100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json, which v2/07-Packaging/pack.py writes from its label map.
Opens the skeleton's cloud design 100000_P04_POD-SKELETON_CAD from "Default Project/FocusPod v2" itself, because a STEP
import drops the body names (first run, 2026-10-31). It refuses to start when that design is already open in Fusion, so
it never touches anyone's session; it changes only what shows (light bulbs, opacity, the camera), never saves, and
closes the design without saving. For each step it shows the bodies fitted so far (the step's new bodies solid, the
earlier ones faded), turns the camera (from behind for the shell, from the front for the decor and the glass, from
above with the ceiling and front hidden for the linings) and saves the step into out_dir (...-STEP-NN_IMG.png) with a
transparent background. That capture leaves out Fusion's layout grid, the axes and the origin mark and keeps every
part, solid or faded (probe, 2026-11-01, steps 2, 11 and 14), so none of Fusion's settings change: the API has no
switch for the layout grid, and that setting is shared by everyone using this Fusion. A picture with every body hidden
is no help either, as Fusion then draws a different, smaller grid (sample 2b). clean_pictures.py puts each picture on
white for the guide.

Fusion draws pictures only on a live screen, so run it when the screen is unlocked (D-84). The bodies are the
skeleton's envelopes; pictures of the parts themselves replace these as each part's CAD merges.
"""

import json
import os
import plistlib
import subprocess

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


def screen_locked():
    """True while the Mac's screen is locked, from macOS's console session record (ioreg); None if it can't be read."""
    try:
        out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=10).stdout
        users = plistlib.loads(out).get("IOConsoleUsers", [])
    except Exception:
        return None
    return any(u.get("CGSSessionScreenIsLocked") for u in users)


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


def point_cm(p_mm):
    return adsk.core.Point3D.create(p_mm[0] / 10.0, p_mm[1] / 10.0, p_mm[2] / 10.0)


def save(vp, path, step):
    """The viewport as a PNG with a transparent background: no layout grid, axes or origin mark, the parts as drawn."""
    opts = adsk.core.SaveImageFileOptions.create(path)
    opts.width, opts.height, opts.isBackgroundTransparent = WIDTH, HEIGHT, True
    if not vp.saveAsImageFileWithOptions(opts):
        raise RuntimeError("Fusion saved no picture for step %d; is the screen unlocked?" % step)


def run(_context):
    app = adsk.core.Application.get()
    only = {int(x) for x in str(ARGS.get("steps") or "").split(",") if x.strip()}   # a sample: these steps only
    out_dir = ARGS.get("out_dir")   # the raw pairs go here; clean_pictures.py writes the guide's pictures
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    unknown = sorted(only - {s["step"] for s in data["steps"]})
    if unknown:
        raise RuntimeError("no picture for step(s) %s; the steps with pictures are %s" % (unknown, [s["step"] for s in data["steps"]]))
    if not out_dir:
        raise RuntimeError("out_dir=... is needed: the raw pictures go to a scratch folder, never straight into the guide")
    if screen_locked():   # checked when the run starts, not when it was queued
        raise RuntimeError("the screen is locked: Fusion draws no pictures on a locked screen (D-84); run again when it is unlocked")
    doc = open_skeleton(app)
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        hide_helpers(design.rootComponent)
        named = bodies_by_name(design.rootComponent)
        wanted = {b for s in data["steps"] for b in s["new"]}
        missing = sorted(wanted - set(named))
        if missing:
            raise RuntimeError("bodies not found in the design: %s" % missing)
        for group in named.values():
            for body in group:
                body.isLightBulbOn = False
        vp = app.activeViewport
        os.makedirs(out_dir, exist_ok=True)
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
            if only and s["step"] not in only:
                continue   # the bodies above still build up, so a sample step looks as it will in the full set
            cam = vp.camera
            cam.eye = point_cm(VIEWS[s["view"]])
            cam.target = point_cm(TARGET)
            cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
            cam.isSmoothTransition = False
            vp.camera = cam
            vp.fit()
            out = os.path.join(out_dir, os.path.basename(s["image"]))
            save(vp, out, s["step"])
            made += 1
            print("STEP %d: %s (%d new bodies, %s view)" % (s["step"], out, len(s["new"]), s["view"]))
        print("PICTURES: %d of %d" % (made, len(only) if only else len(data["steps"])))
    finally:
        doc.close(False)
