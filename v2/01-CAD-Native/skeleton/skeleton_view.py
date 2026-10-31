"""Camera presets for the skeleton renders (view only; the design is not changed).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/skeleton_view.py \\
        --doc 100000_P04_POD-SKELETON_CAD --arg view=front-iso \\
        --screenshot OUT.png --direction current

Views are named by pod direction (conventions.md section 4: front = the door
side, -Y; right = +X seen from outside facing the door), never by Fusion's
view names. Coordinates below are mm in the pod system.
"""

import adsk.core

ARGS = globals().get("SCRIPT_ARGS", {})

# view: (eye, target, fit)
VIEWS = {
    "front-iso": ((3200, -5200, 3600), (0, 0, 1150), True),     # front, right, above
    "back-iso": ((-3200, 5200, 3600), (0, 0, 1150), True),      # back, left, above
    "top": ((0, 0, 9000), (0, 0, 0), True),
    "base-front": ((900, -2700, 700), (150, -760, 80), False),  # front base band, DL and DR feet
    "back-top": ((-1400, 3200, 3300), (0, 830, 2330), False),   # back top edge, seams
}


def run(_context):
    app = adsk.core.Application.get()
    eye, target, fit = VIEWS[ARGS.get("view", "front-iso")]
    vp = app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.eye = adsk.core.Point3D.create(*(v / 10.0 for v in eye))
    cam.target = adsk.core.Point3D.create(*(v / 10.0 for v in target))
    up = (0, 1, 0) if ARGS.get("view") == "top" else (0, 0, 1)
    cam.upVector = adsk.core.Vector3D.create(*up)
    cam.isFitView = fit
    vp.camera = cam
    if fit:
        vp.fit()
    vp.refresh()
    print("view %s: eye %s target %s" % (ARGS.get("view", "front-iso"), eye, target))
