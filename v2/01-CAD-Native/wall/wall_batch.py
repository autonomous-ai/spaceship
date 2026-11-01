"""Build several WALL designs in one Fusion run (PM ruling 2026-10-31: each team keeps at most 3 runs in the
Fusion queue; fold work into fewer, bigger runs).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/wall_batch.py --label "WALL Engineer: batch" \
        --timeout 3000 --arg specs="new:side:panel:R1;rebuild:side:frame:R1;new:back:cassette:B1"

Each spec is MODE:BUILDER:PART:POSITION. MODE is new (make the document), rebuild (open it and rebuild
the design the script made), auto (rebuild it if it is in the folder, else make it) or front (only save the
drawings' Front, seen from inside the pod); BUILDER is side (wall_side_panel.py, positions L1 R1 L2 R2) or back
(wall_back_panel.py, positions B1-B4); PART is panel, cassette, frame, skin, tray or felt (a fill spec is skipped:
D-123 cancels the panels' fill numbers, the pieces are built in the panel). The document
name is the builder's own (`<pn>_P01_<NAME>_CAD`) in Default Project / FocusPod v2, opened the way
run_script.py --doc opens one. For each spec the builder runs in a fresh namespace with post=1, so it
builds, checks, saves (holding the part number and description), exports, reports and edit-tests, and then
the document is closed without saving (the post step breaks the skeleton link in memory only). A failing
spec is printed (BATCH|FAIL), its document is closed without saving, and the batch goes on; the script
itself never raises, so no other document is touched by a rollback. Only documents this batch opened are
closed.
"""

import os
import traceback

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
FOLDER = ("Default Project", "FocusPod v2")
BUILDERS = {"side": "v2/01-CAD-Native/wall/wall_side_panel.py", "back": "v2/01-CAD-Native/wall/wall_back_panel.py"}


def folder(app):
    proj = None
    for i in range(app.data.dataProjects.count):
        p = app.data.dataProjects.item(i)
        if p.name == FOLDER[0]:
            proj = p
            break
    if proj is None:
        raise RuntimeError("no Fusion project called %r" % FOLDER[0])
    f = proj.rootFolder.dataFolders.itemByName(FOLDER[1])
    if f is None:
        raise RuntimeError("no folder %r" % FOLDER[1])
    return proj, f


def find_file(fold, name):
    """The folder's files called `name`, through the shared folder reader (tools/fusion/fusion_folder.py, #213:
    one fetch of the folder per pass; it reads again while an entry can't be read, and stops once `name` is
    found). The old per-entry reads took minutes per scan (Fusion Engineer 2's log study, 2026-11-01)."""
    from fusion_folder import read_folder     # run_script.py makes it importable and loads it fresh every run
    files, _unknown, _others = read_folder(fold, stop_when=lambda f, u, o: name in f)
    return files.get(name, [])


def builder_args(builder, part, position):
    if builder == "side":
        return {"part": part, "side": position[0], "row": position[1]}
    return {"part": part, "pos": position}


def doc_name(app, builder, part, position):
    """The document name the builder itself uses, from a dry load of its tables (no Fusion calls)."""
    path = os.path.join(ARGS["repo_root"], BUILDERS[builder])
    ns = {"__name__": "__wall_name__", "__file__": path,
          "SCRIPT_ARGS": dict(builder_args(builder, part, position), repo_root=ARGS["repo_root"])}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    return ns["DOC_NAME"]


def inside_of(builder, part, position):
    """The room side the builder uses for the drawings' Front (its INSIDE)."""
    path = os.path.join(ARGS["repo_root"], BUILDERS[builder])
    ns = {"__name__": "__wall_inside__", "__file__": path,
          "SCRIPT_ARGS": dict(builder_args(builder, part, position), repo_root=ARGS["repo_root"])}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    return ns["INSIDE"]


def open_or_make(app, name, make, allow_existing=False):
    """(document, opened by us, existed before). make: create it when it is not in the folder; an existing one
    is refused unless allow_existing (mode auto)."""
    docs = [app.documents.item(i) for i in range(app.documents.count)]
    docs = [d for d in docs if d.name == name]
    if len(docs) > 1:
        raise RuntimeError("%d open documents are called %r" % (len(docs), name))
    if docs:
        docs[0].activate()
        return docs[0], False, True
    proj, fold = folder(app)
    files = find_file(fold, name)
    if len(files) > 1:
        raise RuntimeError("%d files are called %r" % (len(files), name))
    if files:
        if make and not allow_existing:
            raise RuntimeError("%r already exists; use rebuild" % name)
        app.data.activeProject = proj
        doc = app.documents.open(files[0], True)
        if doc is None:
            raise RuntimeError("could not open %r" % name)
        doc.activate()
        print("BATCH|opened %s (version %s)" % (name, files[0].versionNumber))
        return doc, True, True
    if not make:
        raise RuntimeError("%r is not in %s (use new)" % (name, FOLDER[1]))
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    app.data.activeProject = proj
    if not doc.saveAs(name, fold, "new, made by wall_batch.py", ""):
        raise RuntimeError("saveAs %r failed" % name)
    doc.activate()
    print("BATCH|made %s" % name)
    return doc, True, False


SKELETON = "100000_P04_POD-SKELETON_CAD"

# D-131 (PM, 2026-11-01): the frames turn to welded, galvanized steel, L1 first as the sample panel; the other
# panels follow after its review (Lead). Specs for a held position are skipped, so a queued run builds no panel
# out of turn. "ALL" holds every position (while the builder is being changed).
ON_HOLD = {"R1", "L2", "R2", "B1", "B2", "B3", "B4"}


def preflight(app):
    """Before making any document: every skeleton name the builders link must be a favorite of the cloud
    skeleton's latest version (an 18:53 batch found skin_t gone and left three empty documents). Opens the
    skeleton invisibly and closes it again, unless it was already open (then it is left as it was)."""
    names = set()
    for builder, args in (("side", {"part": "panel", "side": "L", "row": "1"}),
                          ("back", {"part": "panel", "pos": "B1"})):
        path = os.path.join(ARGS["repo_root"], BUILDERS[builder])
        ns = {"__name__": "__wall_names__", "__file__": path, "SCRIPT_ARGS": dict(args, repo_root=ARGS["repo_root"])}
        with open(path, "r", encoding="utf-8") as fh:
            exec(compile(fh.read(), path, "exec"), ns)
        names |= set(ns["SKELETON_NAMES"])
    _proj, fold = folder(app)
    files = find_file(fold, SKELETON)
    if not files:
        return sorted(names), "skeleton not found"
    already = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name == SKELETON]
    if already and (already[0].isModified or not already[0].dataFile
                    or already[0].dataFile.versionNumber != files[0].versionNumber):
        return sorted(names), "open in Fusion but not as its latest saved version v%s" % files[0].versionNumber
    active = app.activeDocument
    doc = already[0] if already else app.documents.open(files[0], False)
    try:
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        favs = {design.userParameters.item(i).name for i in range(design.userParameters.count)
                if design.userParameters.item(i).isFavorite}
        missing = sorted(names - favs)
        return missing, "version %s" % files[0].versionNumber
    finally:
        if not already:
            doc.close(False)
        if active is not None and active.isValid:
            active.activate()


def run(_context):
    app = adsk.core.Application.get()
    specs = [s.strip() for s in ARGS.get("specs", "").split(";") if s.strip()]
    done, failed = [], []
    try:                                   # a batch of front-only specs needs no skeleton
        missing, ver = preflight(app) if any(not s_.startswith("front:") for s_ in specs) else ([], "not needed")
    except Exception as exc:                              # noqa: BLE001
        missing, ver = ["(pre-flight failed: %s)" % exc], "?"
    if missing:
        print("BATCH|FAIL pre-flight: skeleton %s %s lacks favorites %s; nothing made" % (SKELETON, ver, missing))
        print("BATCH|summary: 0 done, %d failed: pre-flight" % len(specs))
        return
    print("BATCH|pre-flight: skeleton %s has every linked favorite" % ver)
    for spec in specs:
        doc, opened = None, False
        try:
            mode, builder, part, position = spec.split(":")
            if mode not in ("new", "rebuild", "front", "auto") or builder not in BUILDERS:
                raise RuntimeError("bad spec %r" % spec)
            if "ALL" in ON_HOLD or position in ON_HOLD:
                print("BATCH|skip %s: on hold (D-131: L1 is the steel sample; the others wait for its review)" % spec)
                continue
            if part == "fill":           # D-123: no fill part any more; its pieces are built in the panel
                print("BATCH|skip %s: the panel's fill number is cancelled (D-123); the fill pieces are built "
                      "straight into the panel and cut from their DXFs (D-128)" % spec)
                continue
            name = doc_name(app, builder, part, position)
            print("BATCH|start %s -> %s" % (spec, name))
            doc, opened, existed = open_or_make(app, name, mode in ("new", "auto"), allow_existing=mode == "auto")
            if mode == "front":                # the drawings' Front only (designs built before it was saved)
                if doc.isModified:
                    raise RuntimeError("%r has unsaved changes" % name)
                sf = os.path.join(ARGS["repo_root"], "v2/02-Drawings/wall/set_front.py")
                inside = inside_of(builder, part, position)
                sf_ns = {"__name__": "__fusion_set_front__", "__file__": sf, "SCRIPT_ARGS": {"inside": inside}}
                with open(sf, "r", encoding="utf-8") as fh:
                    exec(compile(fh.read(), sf, "exec"), sf_ns)
                sf_ns["run"](None)
                if not doc.save("front = seen from inside the pod"):
                    raise RuntimeError("save failed")
                done.append(name)
                print("BATCH|done %s (front %s)" % (name, inside))
                continue
            path = os.path.join(ARGS["repo_root"], BUILDERS[builder])
            sargs = dict(builder_args(builder, part, position), repo_root=ARGS["repo_root"], post="1",
                         note=ARGS.get("note", "batch build"))
            if mode == "rebuild" or (mode == "auto" and existed):
                sargs["rebuild"] = "1"
            ns = {"__name__": "__fusion_script__", "__file__": path, "SCRIPT_ARGS": sargs}
            with open(path, "r", encoding="utf-8") as fh:
                exec(compile(fh.read(), path, "exec"), ns)
            print("BATCH|builder file %s" % os.path.realpath(path))    # by full path, never by module name
            ns["run"](None)
            done.append(name)
            print("BATCH|done %s" % name)
        except Exception as exc:                          # noqa: BLE001  (report, close, go on)
            failed.append(spec)
            print("BATCH|FAIL %s: %s" % (spec, exc))
            print(traceback.format_exc()[-1500:])
        finally:
            if doc is not None and opened and doc.isValid:
                try:
                    doc.close(False)                     # never saves; the build saved what it built
                except Exception as exc:                 # noqa: BLE001
                    print("BATCH|could not close %s: %s" % (doc.name, exc))
    print("BATCH|summary: %d done, %d failed%s" % (len(done), len(failed), (": " + ", ".join(failed)) if failed else ""))
