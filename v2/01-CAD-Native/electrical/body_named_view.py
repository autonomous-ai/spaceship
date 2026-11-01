"""The named view "711001 VIEW FROM BELOW" in the enclosure body's design (711001), for its drawing's view from
below: looking up (+Y), with the open side (the front) at the top of the view and the design's X = 0 end (datum B)
on the left, the way ISO first-angle projection draws the view from below above the FRONT view.

Fusion's standard Bottom orientation gives that view turned 180 degrees (Reviewer 7's P1 on #173, 2026-11-01:
H04 printed 55 from the right and 18 from the front, against 55 from B and 18 from C), and the drawing API can't
turn a view or project one; its base view can take a named view of the design instead. The view only adds a
camera to the design: no geometry changes.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/electrical/body_named_view.py --label "ELECTRICAL" \\
        --doc 711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD --save "named view 711001 VIEW FROM BELOW" --close

The build (electrical_parts_cad.py) calls add_view_from_below(replace=True) after it sets the design's Front, so a
rebuild keeps the view and moves its camera with the body's size. Run on its own, this changes nothing when the
view is there with the same camera, and stops when a view of that name has another camera.
"""

import adsk.core
import adsk.fusion

NAME = "711001 VIEW FROM BELOW"
BODY_CAD = "711001_P01_ELECTRICAL-POWER-UNIT-ENCLOSURE-BODY_CAD"
OUT = 1000.0                    # cm: the eye 10 m below the body's centre


def body_box(design: "adsk.fusion.Design"):
    """The enclosure body's box in the design's coordinates (cm): its one solid, through its occurrence."""
    root = design.rootComponent
    boxes = [b.boundingBox for b in root.bRepBodies]
    for i in range(root.allOccurrences.count):
        occ = root.allOccurrences.item(i)
        boxes += [occ.bRepBodies.item(j).boundingBox for j in range(occ.bRepBodies.count)]
    if len(boxes) != 1:
        raise RuntimeError("the design holds %d solids, not the body's one" % len(boxes))
    return boxes[0]


def wanted(box: "adsk.core.BoundingBox3D"):
    """(target, eye, up, zs) for the view from below; zs is the side the body opens to, as the build reads it."""
    lo, hi = box.minPoint, box.maxPoint
    zs = 1 if abs(lo.z) < abs(hi.z) else -1                 # the returns fold toward +Z or -Z (the build's rule)
    mid = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2)
    eye = (mid[0], mid[1] - OUT, mid[2])
    return mid, eye, (0.0, 0.0, float(zs)), zs


def _same(a, b, tol=1e-6):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


def _xyz(p):
    return (p.x, p.y, p.z)


def add_view_from_below(app: "adsk.core.Application", design: "adsk.fusion.Design", replace=False):
    """Add the named view, or check the one there (with replace, set its camera). Returns "added", "kept" or
    "moved"."""
    target, eye, up, zs = wanted(body_box(design))
    views = design.namedViews
    have = None
    for i in range(views.count):
        if views.item(i).name == NAME:
            have = views.item(i)
    if have is not None:
        cam = have.camera
        if _same(_xyz(cam.target), target) and _same(_xyz(cam.eye), eye) and _same(_xyz(cam.upVector), up):
            print("named view %s: there already, same camera" % NAME)
            return "kept"
        if replace:
            cam.target = adsk.core.Point3D.create(*target)
            cam.eye = adsk.core.Point3D.create(*eye)
            cam.upVector = adsk.core.Vector3D.create(*up)
            have.camera = cam
            print("named view %s: camera moved to the body's centre %s cm" % (NAME, [round(v, 3) for v in target]))
            return "moved"
        raise RuntimeError("named view %s is there with another camera (eye %s, up %s): look before changing it" % (
            NAME, [round(v, 3) for v in _xyz(cam.eye)], [round(v, 3) for v in _xyz(cam.upVector)]))
    cam = app.activeViewport.camera                          # a copy to fill in
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = adsk.core.Point3D.create(*target)
    cam.eye = adsk.core.Point3D.create(*eye)
    cam.upVector = adsk.core.Vector3D.create(*up)
    nv = views.add(cam, NAME)
    if nv is None:
        raise RuntimeError("NamedViews.add returned None")
    got = nv.camera
    if not (_same(_xyz(got.target), target) and _same(_xyz(got.eye), eye) and _same(_xyz(got.upVector), up)):
        raise RuntimeError("the named view's camera reads back as eye %s target %s up %s" % (
            _xyz(got.eye), _xyz(got.target), _xyz(got.upVector)))
    print("named view %s added: looking +Y from below, up %sZ (the open side), target %s cm" % (
        NAME, "+" if zs > 0 else "-", [round(v, 3) for v in target]))
    return "added"


def run(_context):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith(BODY_CAD):
        raise RuntimeError("the active document is %r, not %s" % (app.activeDocument.name, BODY_CAD))
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError("the active product is not a design")
    add_view_from_below(app, design)
    views = design.namedViews
    print("named views now: %s" % ", ".join(views.item(i).name for i in range(views.count)))
