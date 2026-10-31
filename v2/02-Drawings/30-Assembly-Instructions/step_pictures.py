"""Step pictures for the assembly guide, from the Fusion model (UNVERIFIED: not run yet, the Mac's screen was locked).

    python3 tools/fusion/run_script.py v2/02-Drawings/30-Assembly-Instructions/step_pictures.py \
        --label "Packing and Assembly Engineer"
    python3 v2/07-Packaging/pack.py          # puts each picture under its step in the guide

Reads 100000_P04_POD-ASSEMBLY-GUIDE-STEP-BODIES_DATA.json, which v2/07-Packaging/pack.py writes from its label map.
Opens skeleton P04's STEP as a new document of its own, never the shared cloud skeleton. For each step it shows the
bodies fitted so far: the step's new bodies solid, the earlier ones faded. It turns the camera (from behind for the
shell, from the front for the decor and the glass, from above with the ceiling and front hidden for the linings) and
saves img/100000_P04_POD-ASSEMBLY-GUIDE-STEP-NN_IMG.png. It closes its document without saving.

Fusion draws pictures only on a live screen, so run it when the screen is unlocked (D-84). The bodies are the
skeleton's envelopes; pictures of the parts themselves replace these as each part's CAD merges.
"""

import json
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = os.path.dirname(os.path.abspath(__file__))
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


def point_cm(p_mm):
    return adsk.core.Point3D.create(p_mm[0] / 10.0, p_mm[1] / 10.0, p_mm[2] / 10.0)


def run(_context):
    app = adsk.core.Application.get()
    repo = ARGS.get("repo_root") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    step_file = os.path.join(repo, data["source"])
    doc = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step_file))
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
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
                    body.opacity = FADED
            for name in s["new"]:
                for body in named[name]:
                    body.opacity = 1.0
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
        doc.close(False)
