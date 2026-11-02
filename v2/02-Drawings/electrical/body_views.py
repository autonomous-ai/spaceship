"""Where drawing 711001's views put the enclosure body's holes, worked out from its STEP: one rule for the Fusion run
(make_body_drawing.py checks each placed view's circles against it before anything else is drawn) and for the
finished PDF (body_drawing_text.py checks the printed circles the same way and puts the hole tags beside them).

The body's design (the build, electrical_parts_cad.py): X along the width from the end that is datum B in the FRONT
view, Y up from the bottom face (datum A), Z through the depth; the back face is datum C and the returns fold toward
the open side, +Z when zs = +1 (the build prints "returns toward +Z"). The drawing is ISO first-angle (ISO 5456-2):
the view from above below the FRONT, the view from the left on its right and the view from the right on its left, so
the back (C) is next to the FRONT in all three. The bottom is view D, seen in the direction of arrow D (from below):
Fusion's standard Bottom, which is the first-angle view from below turned 180 degrees (Reviewer 7's P1, #173), and
the drawing API can't turn a view, project one or use a named view (it refuses any orientation value past the
standard ones: probe of 2026-11-01). So D stands apart from the projected views, marked as turned.

Each view below gives the direction it looks from (toward the viewer) and the model directions of the sheet's +x and
+y, with the camera's right = looking direction x up.

Fusion's API lists a view's hidden circles too (the probe's Bottom gave H03, behind the bottom wall), while its PDF
prints only the visible ones: the Fusion run allows a hidden hole's circle, the PDF check expects only the seen ones.

Standard library only; the STEP is read with tools/checks/stepfile.py, loaded by its path.
"""

import importlib.util
import os

SIZE_TOL = 0.1          # mm on the sheet: a hole circle's radius against the STEP's
FRONT_LIP = 22.0        # mm, the body's front lips (electrical_parts_cad.py "lip"): the FRONT view looks through the
                        # opening inside them, so a hole in the back shows there (H15, the cord clamp's stud)
POS_TOL = 0.3           # mm on the sheet: a hole circle's centre against the STEP's


def views(zs):
    """{name: (toward, sheet x, sheet y)} as model unit vectors, for a body that opens toward zs * Z."""
    s = 1 if zs > 0 else -1
    return {"front": ((0, 0, s), (s, 0, 0), (0, 1, 0)),
            "bottom": ((0, -1, 0), (s, 0, 0), (0, 0, s)),      # the first-angle view from below: the open side on top
            "d": ((0, -1, 0), (-s, 0, 0), (0, 0, -s)),         # view D, Fusion's Bottom: that view turned 180 degrees
            "top": ((0, 1, 0), (s, 0, 0), (0, 0, -s)),         # the view from above: the open side at the bottom
            "right": ((s, 0, 0), (0, 0, -s), (0, 1, 0)),       # from the right (+X side when zs = +1)
            "left": ((-s, 0, 0), (0, 0, s), (0, 1, 0))}


def dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def lowest(box, axis):
    """The smallest value of (point . axis) over the box (x0, y0, z0, x1, y1, z1), axis a signed unit vector."""
    return sum(box[k] * axis[k] if axis[k] > 0 else box[k + 3] * axis[k] for k in range(3))


def highest(box, axis):
    return -lowest(box, tuple(-a for a in axis))


def load_stepfile(repo):
    """tools/checks/stepfile.py by its path, under a name no other module uses (Fusion keeps modules between runs)."""
    path = os.path.join(repo, "tools", "checks", "stepfile.py")
    spec = importlib.util.spec_from_file_location("ele_body_stepfile", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def step_body(step_path, repo):
    """(box mm, [(centre mm, axis, diameter mm)]) of the STEP's one solid, in the file's top assembly coordinates."""
    sf = load_stepfile(repo)
    s = sf.StepFile(step_path)
    inst = s.instances()
    if len(inst) != 1:
        raise RuntimeError("%s holds %d solids, not the body's one" % (os.path.basename(step_path), len(inst)))
    so = s.solid(inst[0]["solid"])
    frame = inst[0]["frame"]
    holes = []
    for h in so.holes:
        m = h.moved(frame)
        holes.append((tuple(m.center), tuple(m.axis), m.diameter))
    b = so.box                                       # the solid's own coordinates: placed like its holes
    corners = [frame.point((x, y, z)) for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])]
    box = tuple(min(c[k] for c in corners) for k in range(3)) + tuple(max(c[k] for c in corners) for k in range(3))
    return box, holes


def opens_to(box):
    """+1 when the body opens toward +Z (its back face at the low Z end), as the build reads it."""
    return 1 if abs(box[2]) < abs(box[5]) else -1


def along(view, holes, zs):
    """The holes whose axis runs along the view's looking direction, seen or behind a wall."""
    toward = views(zs)[view][0]
    return [h for h in holes if abs(abs(dot(h[1], toward)) - 1.0) < 1e-6]


def seen(view, box, holes, zs, wall=3.0, opening=False):
    """The holes a visible-edges view shows as circles: axis along its looking direction, in the outermost wall on
    the viewer's side (within `wall` mm of the box's face there; a hole in a wall further back is behind that wall
    on this closed-sided body). With `opening`, the FRONT view also shows the back's holes that lie inside the opening
    within the lips (FRONT_LIP), whole: the body is open on that side."""
    toward, ax, ay = views(zs)[view]
    top = highest(box, toward)
    out = [h for h in holes if abs(abs(dot(h[1], toward)) - 1.0) < 1e-6 and top - dot(h[0], toward) <= wall]
    if opening and view == "front":
        low = lowest(box, toward)
        w, ht = highest(box, ax) - lowest(box, ax), highest(box, ay) - lowest(box, ay)
        for h in holes:
            if abs(abs(dot(h[1], toward)) - 1.0) > 1e-6 or dot(h[0], toward) - low > wall:
                continue
            u, v, r = dot(h[0], ax) - lowest(box, ax), dot(h[0], ay) - lowest(box, ay), h[2] / 2.0
            if FRONT_LIP + r <= u <= w - FRONT_LIP - r and FRONT_LIP + r <= v <= ht - FRONT_LIP - r:
                out.append(h)
    return out


def on_sheet(view, box, point, extent, scale, zs):
    """Sheet (x, y) mm of a model point in a view whose part outline spans `extent` (x0, y0, x1, y1 sheet mm)."""
    _toward, ax, ay = views(zs)[view]
    return (extent[0] + (dot(point, ax) - lowest(box, ax)) * scale,
            extent[1] + (dot(point, ay) - lowest(box, ay)) * scale)


def expected(view, box, holes, extent, scale, zs, hidden=False, opening=False):
    """[(x, y, r)] sheet mm of the circles the view shows; with hidden, those of the holes behind a wall instead;
    `opening` as in seen()."""
    pick = seen(view, box, holes, zs, opening=opening)
    if hidden:
        pick = [h for h in along(view, holes, zs) if h not in pick]
    return [on_sheet(view, box, c, extent, scale, zs) + (d / 2.0 * scale,) for c, _a, d in pick]


def compare(view, want, got, may=(), pos_tol=POS_TOL, size_tol=SIZE_TOL):
    """Problems (strings) between the circles a view should show (`want`) and those it shows (`got`), both
    [(x, y, r)] in sheet mm; a circle of `got` may also be one of `may` (a hidden hole's, which Fusion's API lists)."""
    probs, used = [], set()
    for x, y, r in want:
        best = None
        for i, (gx, gy, gr) in enumerate(got):
            if i in used or abs(gr - r) > size_tol:
                continue
            dd = ((gx - x) ** 2 + (gy - y) ** 2) ** 0.5
            if best is None or dd < best[1]:
                best = (i, dd)
        if best is None or best[1] > pos_tol:
            near = min((((gx - x) ** 2 + (gy - y) ** 2) ** 0.5, (gx, gy, gr)) for gx, gy, gr in got) if got else None
            probs.append("%s view: no circle of r %.2f at (%.2f, %.2f)%s" % (
                view, r, x, y, "; nearest %s at %.2f mm" % (tuple(round(v, 2) for v in near[1]), near[0])
                if near else "; the view has no circles"))
        else:
            used.add(best[0])
    for i, (gx, gy, gr) in enumerate(got):
        if i in used:
            continue
        if any(abs(gr - r) <= size_tol and ((gx - x) ** 2 + (gy - y) ** 2) ** 0.5 <= pos_tol for x, y, r in may):
            continue
        probs.append("%s view: a circle of r %.2f at (%.2f, %.2f) that no STEP hole puts there" % (view, gr, gx, gy))
    return probs


def check_view(view, box, holes, extent, scale, zs, got, hidden_ok=False, opening=True):
    """compare() for one view, against the STEP's holes; hidden_ok lets a hidden hole's circle be there (the API)."""
    may = expected(view, box, holes, extent, scale, zs, hidden=True, opening=opening) if hidden_ok else ()
    return compare(view, expected(view, box, holes, extent, scale, zs, opening=opening), got, may)
