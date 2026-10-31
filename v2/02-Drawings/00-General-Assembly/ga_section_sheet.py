"""GA sheets 2 and 3: a section view on the drawing of a cut copy, with hatch.

    python3 tools/fusion/start_drawing.py 100000_P04_POD-SECTION-AA_CAD 100000_P04_POD-SECTION-AA_DWG --sheet A2
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_section_sheet.py \\
        --doc 100000_P04_POD-SECTION-AA_DWG --arg section=AA --save "section A-A view" --close

The drawing is of the cut copy made by ga_section_design.py, so its base view
from the viewer's side shows the cut faces. This script places that view at
1:20, then hatches every cut face: it opens the section design, finds the
planar faces lying on the section plane, maps their loops onto the sheet
through the view's extent, and draws 45 degree lines 3 mm apart in a sheet
sketch (tools/fusion/hatch.py, pasted in; the API has no hatch). Adjacent
bodies alternate 45 and 135 degrees so their boundary reads.
"""

import os

import adsk.core
import adsk.drawing
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
SCALE = 1.0 / 20.0
VO = adsk.drawing.ViewOrientationTypes
# section: (design name, orientation, sheet centre, plane axis, how model maps onto the sheet)
SECTIONS = {
    # seen from the left (-X): sheet x runs along -Y (the front, -Y, is on the right), sheet y along +Z
    "AA": ("100000_P04_POD-SECTION-AA_CAD", VO.LeftViewOrientationType, (230.0, 230.0), "x", ("-y", "z")),
    # seen from the front (-Y): sheet x along +X, sheet y along +Z
    "BB": ("100000_P04_POD-SECTION-BB_CAD", VO.FrontViewOrientationType, (230.0, 230.0), "y", ("x", "z")),
}

_hatch_src = open(os.path.join(ARGS.get("repo_root", "."), "tools/fusion/hatch.py"), encoding="utf-8").read()
_ns = {}
exec(compile(_hatch_src, "hatch.py", "exec"), _ns)
hatch_segments = _ns["hatch_segments"]


def p2(x, y):
    return adsk.core.Point2D.create(x, y)


def dpt(x, y):
    return adsk.drawing.DrawingPoint.create(p2(x, y))


def extent(view: "adsk.drawing.View"):
    xs, ys = [], []
    vc = view.viewCurves
    for i in range(vc.count):
        c = vc.item(i)
        if c.type == adsk.drawing.ViewCurveTypes.LineViewCurveType:
            for p in (c.startPoint, c.endPoint):
                xs.append(p.coordinate.x)
                ys.append(p.coordinate.y)
    return min(xs), min(ys), max(xs), max(ys)


def model_box(design: "adsk.fusion.Design"):
    bodies = [b for c in design.allComponents for b in c.bRepBodies]
    lo = [min(getattr(b.boundingBox.minPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    hi = [max(getattr(b.boundingBox.maxPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    return lo, hi


def cut_loops(design: "adsk.fusion.Design", axis, at_mm):
    """Outer and inner loops (model mm) of planar faces lying on the section plane, per body."""
    k = "xyz".index(axis)
    out = []
    for c in design.allComponents:
        for b in c.bRepBodies:
            loops = []
            for f in b.faces:
                if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                    continue
                geo = adsk.core.Plane.cast(f.geometry)
                n = [geo.normal.x, geo.normal.y, geo.normal.z]
                if abs(abs(n[k]) - 1.0) > 1e-6:
                    continue
                if abs(geo.origin.asArray()[k] * 10.0 - at_mm) > 0.01:
                    continue
                for lp in f.loops:
                    pts = []
                    for co in lp.coEdges:
                        e = co.edge
                        sv, ev = (e.startVertex, e.endVertex) if not co.isOpposedToEdge else (e.endVertex, e.startVertex)
                        pts.append([v * 10.0 for v in sv.geometry.asArray()])
                    loops.append(pts)
            if loops:
                out.append((b.name, loops))
    return out


def run(_context):
    app = adsk.core.Application.get()
    sec = ARGS.get("section", "AA")
    design_name, orientation, center, axis, (sx, sy) = SECTIONS[sec]
    doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
    sheet = doc.drawing.sheets.item(0)
    if sheet.views.count == 0:
        inp = sheet.views.createBaseViewInput()
        vp = inp.viewParameters
        vp.orientation = orientation
        vp.scaleValue = SCALE
        vp.style = adsk.drawing.DrawingViewStyleTypes.VisibleEdgesDrawingViewStyleType
        inp.placementPoint = dpt(*center)
        v = sheet.views.add(inp)
        if abs(v.scaleValue - SCALE) > 1e-9:
            v.scaleValue = SCALE
        print("placed the %s view at %s, 1:%g" % (sec, center, 1 / v.scaleValue))
    view = sheet.views.item(0)
    ex = extent(view)

    # the section design, for the cut faces
    sdoc = None
    for i in range(app.documents.count):
        if app.documents.item(i).name == design_name:
            sdoc = app.documents.item(i)
    opened = sdoc is None
    if opened:
        proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
        folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
        df = [folder.dataFiles.item(i) for i in range(folder.dataFiles.count)
              if folder.dataFiles.item(i).name == design_name][0]
        sdoc = app.documents.open(df, False)
    design = adsk.fusion.Design.cast(sdoc.products.itemByProductType("DesignProductType"))
    at = design.userParameters.itemByName("sec_offset").value * 10.0
    lo, hi = model_box(design)
    loops = cut_loops(design, axis, at)
    if opened:
        sdoc.close(False)
    doc.activate()

    def to_sheet(p):
        def coord(spec):
            neg = spec.startswith("-")
            k = "xyz".index(spec[-1])
            return (hi[k] - p[k]) if neg else (p[k] - lo[k])
        return (ex[0] + coord(sx) * SCALE, ex[1] + coord(sy) * SCALE)

    sk = sheet.sketches.add("HATCH - SECTION %s" % sec)
    n_seg = 0
    for i, (body, body_loops) in enumerate(loops):
        poly = [[to_sheet(p) for p in lp] for lp in body_loops]
        for a, b in hatch_segments(poly, spacing=3.0, angle_deg=45.0 if i % 2 == 0 else 135.0):
            sk.lines.add([p2(*a), p2(*b)])
            n_seg += 1
    print("section %s at %.2f mm: %d cut bodies hatched, %d lines; view extent %s" % (
        sec, at, len(loops), n_seg, tuple(round(v, 1) for v in ex)))
