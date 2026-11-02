"""Point the active view at a detail, for a screenshot checked by eye (D-118: a sample is checked
by eye before a method runs at scale).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/ceiling/view_camera.py \\
        --doc 411101_P01_CEILING-PANEL-FRAME-C1_CAD --arg eye=-1100,950,2500 --arg target=-1190,830,2374 \\
        --arg png=/path/corner.png --close --discard --label "CEILING Engineer"

eye and target are pod coordinates in mm; up is +Z. hide=PN,PN hides the occurrences of those part
numbers (to see a detail behind them, such as a cleat slot behind a cross member's end); the run's
--close --discard drops that. Changes nothing else. png=PATH saves the view from the viewport itself
(Viewport.saveAsImageFile): the runner's --screenshot --direction current came back as a far view of the
whole scene in the C1 sample (2026-11-01), so the camera set here didn't reach it.
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def run(_context):
    app = adsk.core.Application.get()
    hide = [p for p in ARGS.get("hide", "").split(",") if p]
    if hide:
        design = adsk.fusion.Design.cast(app.activeProduct)
        for occ in design.rootComponent.allOccurrences:
            if occ.component.partNumber in hide:
                occ.isLightBulbOn = False
    vp = app.activeViewport
    cam = vp.camera
    ex, ey, ez = (float(v) / 10.0 for v in ARGS["eye"].split(","))
    tx, ty, tz = (float(v) / 10.0 for v in ARGS["target"].split(","))
    cam.isFitView = False
    cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    cam.eye = adsk.core.Point3D.create(ex, ey, ez)
    cam.target = adsk.core.Point3D.create(tx, ty, tz)
    cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
    cam.isSmoothTransition = False
    vp.camera = cam
    vp.refresh()
    adsk.doEvents()
    print("camera: eye %s, target %s" % (ARGS["eye"], ARGS["target"]))
    if ARGS.get("png"):
        ok = vp.saveAsImageFile(ARGS["png"], int(ARGS.get("w", "1600")), int(ARGS.get("h", "1000")))
        print("image saved to %s: %s" % (ARGS["png"], ok))
        if not ok:
            raise RuntimeError("the viewport image was not saved")
