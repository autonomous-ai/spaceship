"""GA sheets 2 and 3: a section view on the drawing of a cut copy, with hatch.

    python3 tools/fusion/start_drawing.py 100000_P04_POD-SECTION-AA_CAD 100000_P04_POD-SECTION-AA_DWG --sheet A2
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_section_sheet.py \\
        --doc 100000_P04_POD-SECTION-AA_DWG --arg section=AA --save "section A-A view" --close

The drawing is of the cut copy made by ga_section_design.py, so its base view
from the viewer's side shows the cut faces. This script places that view at
1:20, then hatches every cut face: it opens the section design, finds the
planar faces lying on the section plane, maps their loops onto the sheet
through the view's extent, and draws lines in sheet sketches
(tools/fusion/hatch.py, pasted in; the API has no hatch). ISO 128-50: a face
narrower than 2 mm on the sheet (a skin, frame or cassette layer at 1:20) is
filled with lines 0.3 mm apart running along the strip, so it reads solid;
wider faces get 45 degree lines 2 mm apart, adjacent bodies alternating 45 and
135 degrees.

Lines.add is a preview API, and Fusion's PDF export doesn't always keep what
it holds (live probe 2026-11-01: a sketch of many lines loses its first point,
lines under about 1 mm are merged into wrong paths; one chain per sketch is
kept exactly). So the session first probes it (ga_pdf_check.py probe) and
passes the form that works: --arg line_mode_file=PROBE.json. In the "chain"
form each face's lines are joined into chains, one sketch per chain. With no
working form, the view is placed and the hatch is left out (a GAP line says
so). The chains asked are written to NAME.hatch.json next to the export, and
ga_pdf_check.py hatch checks the PDF line by line against it. A sheet that is
hatched already is refused: redo it from the drawing's first version
(ga_promote.py), never by deleting (a delete then save crashed Fusion).
"""

import json
import os
import time

import adsk
import adsk.core
import adsk.drawing
import adsk.fusion
from fusion_drawing import base_view         # shared helper (tools/fusion), given by run_script.py

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
chain_for, read_line_mode, spacing_for = _ns["chain_for"], _ns["read_line_mode"], _ns["spacing_for"]
fill_lines, hatch_chains, pieces, read_thin_mode = _ns["fill_lines"], _ns["chains"], _ns["pieces"], _ns["read_thin_mode"]
MAX_SKETCHES = 3000     # one sketch per chain, piece or line: past this the sheet would be unworkable


def find_in_folder(folder, name):
    """The DataFiles called name, read safely: the shared check (fusion_folder.py,
    given to every script by run_script.py) when the runner has it, else a guarded
    look (a runner from before PR #121). A folder entry can flicker right after a
    Fusion restart (2026-10-31: DataFiles.item raised "invalid argument index")."""
    try:
        from fusion_folder import read_folder
    except ImportError:
        read_folder = None
    if read_folder is not None:
        files, _unknown, _others = read_folder(folder, stop_when=lambda fs, u, o: name in fs)
        return files.get(name, [])
    hits = []
    for _ in range(12):
        hits = []
        for i in range(folder.dataFiles.count):
            try:
                f = folder.dataFiles.item(i)
                if f.name == name:
                    hits.append(f)
            except Exception:
                pass
        if hits:
            break
        adsk.doEvents()
        time.sleep(5)
    return hits


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
        # the shared helper sets the style (visible edges) and scale again and checks them
        v = base_view(sheet, orientation, SCALE, center)
        print("placed the %s view at %s, 1:%g" % (sec, center, 1 / v.scaleValue))
    view = sheet.views.item(0)
    ex = extent(view)
    old = [sheet.sketches.item(i) for i in range(sheet.sketches.count)]
    print("sketches on the sheet: %s" % ([(k.name, k.lines.count) for k in old] or "none"))
    if any(k.name.startswith("HATCH - SECTION") for k in old):
        # no deletes (2026-10-31: a delete then save crashed Fusion): to draw it again,
        # promote the drawing's first version (ga_promote.py) and run this again
        raise RuntimeError("the sheet is hatched already; promote the drawing's first version to redo it")
    # the form of Lines.add that draws a straight line, from this session's live probe
    mode = read_line_mode(ARGS.get("line_mode_file"), ARGS.get("line_mode", "plain"))
    thin_mode = read_thin_mode(ARGS.get("line_mode_file"), ARGS.get("thin_mode", "none"))
    if mode == "none" or thin_mode == "none":
        print("GAP: no hatch drawn: the line probe found no form that draws %s exactly, so the hatch "
              "waits for a fix (the view is placed)" % ("a straight line" if mode == "none" else "thin faces' lines"))
        return

    # the section design, for the cut faces
    sdoc = None
    for i in range(app.documents.count):
        if app.documents.item(i).name == design_name:
            sdoc = app.documents.item(i)
    opened = sdoc is None
    if opened:
        proj = [p for p in app.data.dataProjects if p.name == "Default Project"][0]
        folder = proj.rootFolder.dataFolders.itemByName("FocusPod v2")
        hits = find_in_folder(folder, design_name)
        if len(hits) != 1:
            raise RuntimeError("expected one %s in the team folder, found %d" % (design_name, len(hits)))
        df = hits[0]
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

    base = "HATCH - SECTION %s" % sec
    record, n_seg, failed, filled = {}, 0, 0, 0
    # every sketch's chains, planned first (2026-11-01 probes: Fusion's PDF export keeps one short
    # chain per sketch exactly but garbles long chains and lines under 1 mm apart): a thin face's fill
    # lines (0.3 mm apart, along the strip) one per sketch; other faces' 45 degree lines, 2 mm apart,
    # in the probe's form: one chain, 4-point pieces, or one line per sketch; the old one-sketch forms
    # put every line in a single sketch
    plan, single = [], []
    for i, (body, body_loops) in enumerate(loops):
        poly = [[to_sheet(p) for p in lp] for lp in body_loops]
        thin = spacing_for(poly) < 1.0
        filled += thin
        segs = fill_lines(poly, i)
        n_seg += len(segs)
        if thin or mode == "own-sketch":
            plan += [[[a, b]] for a, b in segs]
        elif mode == "chain":
            plan += [[ch] for ch in hatch_chains(segs, poly)]
        elif mode == "pairs":
            plan += [[pc] for ch in hatch_chains(segs, poly) for pc in pieces(ch)]
        else:
            single += [chain_for(a, b, mode) for a, b in segs]
    if single:
        plan.append(single)
    if len(plan) > MAX_SKETCHES:
        raise RuntimeError("the hatch would take %d sketches, more than %d; nothing drawn" % (len(plan), MAX_SKETCHES))
    for k, chains_ in enumerate(plan, 1):
        name = "%s %03d" % (base, k)
        sk = sheet.sketches.add(name)
        for ch in chains_:
            if sk.lines.add([p2(*q) for q in ch]) is None:      # None when it fails
                failed += 1
        record[name] = [[list(q) for q in ch] for ch in chains_]
        if k % 50 == 0:
            adsk.doEvents()
    n_sk = len(plan)
    adsk.doEvents()
    print("section %s at %.2f mm: %d cut faces (%d thin, filled along), %d hatch lines in %d sketch(es), "
          "the %r form (thin faces %r), %d failed; view extent %s" % (
              sec, at, len(loops), filled, n_seg, n_sk, mode, thin_mode, failed, tuple(round(v, 1) for v in ex)))
    if failed:
        raise RuntimeError("%d hatch sketch line(s) weren't made; nothing kept" % failed)
    # what was asked, per sketch, for the line-by-line check of the export (ga_pdf_check.py
    # hatch reads NAME.hatch.json next to NAME.pdf)
    out = os.path.join(ARGS.get("repo_root", "."), "v2", "02-Drawings", "00-General-Assembly",
                       "%s.hatch.json" % doc.name)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"drawing": doc.name, "form": mode, "thin": thin_mode, "layers": record}, fh)
    print("hatch record: %s (%d sketch(es))" % (os.path.basename(out), len(record)))
