"""Set the active WALL design's Front (ViewCube) to "seen from inside the pod", for its drawings.

    python3 tools/fusion/run_script.py v2/02-Drawings/wall/set_front.py \
        --doc 211101_P01_WALL-PANEL-FRAME-SIDE-LOWER-LH_CAD --arg inside=+x --save "front = seen from inside"

The designs are in pod coordinates, where a side panel's face looks along X. Fusion's drawing views
use the model's ViewCube, and the drawing API offers only the standard views (no rotation), so the
panel face must be the model's Front for the plan views to line up below and above it in
first-angle. This turns the camera to look at the panel from the room side (`inside`: +x for a left
wall panel, -x for a right one, -y for a back panel), with +Z up, and makes that the Front. Then:
    Front  = the panel seen from inside the pod: X(view) along the panel, Y(view) = +Z
    Top    = from above (first-angle: below the Front);  Bottom = from below (above the Front)
    Left / Right = the panel's ends (first-angle: the view from the left goes on the right)
Geometry doesn't change; save the document afterwards (runner --save).
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def run(_context):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    bodies = [b for c in design.allComponents for b in c.bRepBodies]
    lo = [min(getattr(b.boundingBox.minPoint, a) for b in bodies) for a in "xyz"]
    hi = [max(getattr(b.boundingBox.maxPoint, a) for b in bodies) for a in "xyz"]
    mid = [(p + q) / 2 for p, q in zip(lo, hi)]
    inside = ARGS.get("inside", "+x").lower()
    axis = "xyz".index(inside[1])
    sign = 1 if inside[0] == "+" else -1
    eye = list(mid)
    eye[axis] += sign * 1000.0                     # 10 m out on the room side (cm)
    vp = app.activeViewport
    cam = vp.camera
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = adsk.core.Point3D.create(*mid)
    cam.eye = adsk.core.Point3D.create(*eye)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
    cam.isSmoothTransition = False
    vp.camera = cam
    vp.fit()
    if not vp.setCurrentAsFront():
        raise RuntimeError("setCurrentAsFront failed")
    c = vp.camera
    print("front set: looking from %s toward the panel; eye %s target %s up %s" % (
        inside, [round(v * 10, 1) for v in (c.eye.x, c.eye.y, c.eye.z)],
        [round(v * 10, 1) for v in (c.target.x, c.target.y, c.target.z)],
        [round(v, 3) for v in (c.upVector.x, c.upVector.y, c.upVector.z)]))
