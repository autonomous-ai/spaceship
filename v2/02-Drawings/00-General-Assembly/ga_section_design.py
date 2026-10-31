"""GA sections as cut copies of the skeleton (the drawing API has no section views).

    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_section_design.py \\
        --doc 100000_P04_POD-SECTION-AA_CAD --doc-new --arg section=AA --save "section A-A" --close
    python3 tools/fusion/run_script.py v2/02-Drawings/00-General-Assembly/ga_section_design.py \\
        --doc 100000_P04_POD-SECTION-BB_CAD --doc-new --arg section=BB --save "section B-B" --close

Each section is its own design: it derives every body and every parameter of
the skeleton 100000_P04_POD-SKELETON_CAD at its NEWEST version (an open copy
of an older version is refused, and the derived body count must match the
skeleton's), splits the bodies the plane crosses, and removes the half
between the plane and the viewer. A base view of the design from the
viewer's side then shows the cut faces, as a section would.

After a skeleton update, rebuild it in place (same file, a new version):
    ... ga_section_design.py --doc 100000_P04_POD-SECTION-AA_CAD --arg section=AA \\
        --arg rebuild=1 --save "section A-A, rebuilt" --close
A new skeleton body that crosses the plane would not be split by updating the
references alone, so the rebuild clears the timeline and builds it again.

A-A: plane X = the door's middle (the door's left and right bottom corners,
     from the skeleton), viewer on the left (-X): the longitudinal section
     through the door and threshold, the floor, the ceiling and the back wall.
B-B: plane Y = 0 (mid depth), viewer at the front (-Y): the cross-section
     through both side walls, the floor, the ceiling and their linings.

Then start_drawing.py makes each design's drawing (screen unlocked), and the
section views go on it. Hatching can't be drawn by the API (no hatch on
sheets); that is on the person list.
"""

import time

import adsk
import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
SKELETON = "100000_P04_POD-SKELETON_CAD"
FOLDER = ("Default Project", "FocusPod v2")

# section: (axis normal to the plane, offset expression from the origin plane,
#           side removed (-1: below the plane, +1: above), name)
SECTIONS = {
    "AA": ("x", "-pod_w_Ref / 2 + (door_xl_Ref + door_xbr_Ref) / 2", -1,
           "SECTION A-A: X at the door's middle, seen from the left"),
    "BB": ("y", "0 mm", -1, "SECTION B-B: Y 0 (mid depth), seen from the front"),
}


def vi(s):
    return adsk.core.ValueInput.createByString(s)


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


def skeleton_file(app: "adsk.core.Application"):
    proj = [p for p in app.data.dataProjects if p.name == FOLDER[0]][0]
    folder = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    hits = find_in_folder(folder, SKELETON)
    if len(hits) != 1:
        raise RuntimeError("expected one %s in %s, found %d" % (SKELETON, "/".join(FOLDER), len(hits)))
    return hits[0]


def skeleton_newest(app: "adsk.core.Application"):
    """(document, opened here, version): the skeleton at its newest version.
    An open copy of an older version is refused (2026-10-31: a section derived
    version 3 of the skeleton after version 4 was saved)."""
    df = skeleton_file(app)
    newest = df.latestVersionNumber
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name == SKELETON:
            have = d.dataFile.versionNumber if d.dataFile else None
            if have != newest:
                raise RuntimeError("%s is open at version %s, but its newest version is %s; close it "
                                   "first" % (SKELETON, have, newest))
            return d, False, newest
    d = app.documents.open(df.latestVersion, False)
    have = d.dataFile.versionNumber if d.dataFile else None
    if have != newest:
        raise RuntimeError("opened %s at version %s, not its newest %s" % (SKELETON, have, newest))
    return d, True, newest


def clear(design: "adsk.fusion.Design"):
    """Empty the design for a rebuild in place: the plane parameter is set to a
    plain value first, so nothing ties it to the derived parameters, then the
    whole timeline goes, then the parameter."""
    p = design.userParameters.itemByName("sec_offset")
    if p:
        p.expression = "0 mm"
    tl = design.timeline
    n = tl.count
    tl.markerPosition = 0
    tl.deleteAllAfterMarker()
    if p:
        p.deleteMe()
    root = design.rootComponent
    if tl.count or root.bRepBodies.count or root.occurrences.count:
        raise RuntimeError("rebuild: the design isn't empty after clearing (%d timeline items, %d bodies)"
                           % (tl.count, root.bRepBodies.count))
    print("rebuild: cleared %d timeline items" % n)


def run(_context):
    app = adsk.core.Application.get()
    sec = ARGS.get("section", "AA")
    axis, offset, side, title = SECTIONS[sec]
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    root = design.rootComponent
    if root.bRepBodies.count or root.occurrences.count or root.features.deriveFeatures.count:
        if ARGS.get("rebuild") != "1":
            raise RuntimeError("%s already has content; add --arg rebuild=1 to rebuild it in place"
                               % doc.name)
        clear(design)
    root.partNumber = "100000-SEC-%s" % sec
    root.description = title

    # 1. derive the whole skeleton, newest version: every body and every (favorite) parameter
    skel_doc, opened, version = skeleton_newest(app)
    skel = adsk.fusion.Design.cast(skel_doc.products.itemByProductType("DesignProductType"))
    skel_bodies = sum(c.bRepBodies.count for c in skel.allComponents)
    doc.activate()
    di = root.features.deriveFeatures.createInput(skel)
    di.isIncludeFavoriteParameters = True
    di.sourceEntities = [skel.rootComponent]
    derive = root.features.deriveFeatures.add(di)
    derive.name = "DERIVE - SKELETON P04 V%s (ALL BODIES, PARAMETERS)" % version
    if opened:
        skel_doc.close(False)
    adsk.doEvents()
    bodies = [b for c in design.allComponents for b in c.bRepBodies]
    print("derived from skeleton version %s: %d bodies (the skeleton has %d), %d parameters" % (
        version, len(bodies), skel_bodies, design.allParameters.count))
    if len(bodies) != skel_bodies:
        raise RuntimeError("derived %d bodies, but the skeleton has %d" % (len(bodies), skel_bodies))

    # 2. the section plane, placed by a parameter built from the skeleton's own
    design.userParameters.add("sec_offset", vi(offset), "mm",
                              "CALCULATION: %s plane offset, from the skeleton's parameters" % sec)
    base = {"x": root.yZConstructionPlane, "y": root.xZConstructionPlane}[axis]
    pin = root.constructionPlanes.createInput()
    pin.setByOffset(base, vi("sec_offset"))
    plane = root.constructionPlanes.add(pin)
    plane.name = "PLANE - %s" % title

    # 3. split the bodies the plane crosses (Fusion's split refuses a body it
    #    doesn't cross), then remove everything on the viewer's side
    cut_at = design.userParameters.itemByName("sec_offset").value      # cm
    k = "xyz".index(axis)

    def span(b: "adsk.fusion.BRepBody"):
        bb = b.boundingBox
        return bb.minPoint.asArray()[k], bb.maxPoint.asArray()[k]

    crossing = adsk.core.ObjectCollection.create()
    for b in bodies:
        lo, hi = span(b)
        if lo < cut_at - 1e-6 and hi > cut_at + 1e-6:
            crossing.add(b)
    if crossing.count:
        sin = root.features.splitBodyFeatures.createInput(crossing, plane, True)
        split = root.features.splitBodyFeatures.add(sin)
        split.name = "SPLIT - BODIES CROSSING %s" % sec
    removed, kept = 0, 0
    for c in design.allComponents:
        for b in list(c.bRepBodies):
            lo, hi = span(b)
            mid = (lo + hi) / 2
            if (mid - cut_at) * side > 0:
                b.parentComponent.features.removeFeatures.add(b)
                removed += 1
            else:
                kept += 1
    adsk.doEvents()
    tl = design.timeline
    bad = [tl.item(i).name for i in range(tl.count)
           if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    box = root.boundingBox
    print("%s: split %d crossing bodies at %s = %.2f mm; removed %d bodies, kept %d; unhealthy %s" % (
        title, crossing.count, axis.upper(), cut_at * 10, removed, kept, bad))
    print("box mm: %s" % [round(v * 10, 1) for v in (box.minPoint.x, box.minPoint.y, box.minPoint.z,
                                                      box.maxPoint.x, box.maxPoint.y, box.maxPoint.z)])
    if bad or kept == 0:
        raise RuntimeError("section checks failed")
