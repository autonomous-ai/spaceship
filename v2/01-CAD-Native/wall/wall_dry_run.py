"""Dry runs of WALL designs: each built in a NEW, UNSAVED document and closed without saving (nothing reaches the
cloud), to prove a changed method before a real build (D-118). The builders run with dry=1: their checks run
(timeline health with Fusion's messages, loose sketches, clashes over every placed copy, masses), a fill form whose
number isn't allocated yet gets a temporary label, and the mitre plates are skipped while Joints' STEPs are
missing; the skeleton's values are copied from pod_skeleton.py (link=parse), so no cloud derive is needed.
Nothing is saved, exported or edit-tested.

    python3 tools/fusion/run_script.py <late loader> --arg target=v2/01-CAD-Native/wall/wall_dry_run.py \
        --arg specs="side:panel:L1;back:panel:B1;side:cassette:L1" --label "WALL Engineer: dry run"

Each spec is BUILDER:PART:POSITION, as wall_batch.py's without the mode. A failing spec is printed (DRY|FAIL) and
the next one runs; the script never raises, and the document that was active is active again at the end.

probe:import:PN (PN one of the Joints Engineer's STEPs in v2/03-Manufacturing/joints, say 831008) instead imports
that STEP into a blank unsaved design the way the builders do (into a sub-component, then renamed, given a
material, a joint origin, a rigid joint and a second copy) and prints the timeline's health after each step, with
every group's own items (dry runs 5 and 6 found each STEP import's group in error with no message).
"""

import glob
import os
import traceback

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
BUILDERS = {"side": "v2/01-CAD-Native/wall/wall_side_panel.py", "back": "v2/01-CAD-Native/wall/wall_back_panel.py"}


def builder_args(builder, part, position):
    if builder == "side":
        return {"part": part, "side": position[0], "row": position[1]}
    return {"part": part, "pos": position}


def timeline_report(design, tag):
    """Every timeline item's health and message, a group's own items under it, and the occurrence tree."""
    tl = design.timeline
    for i in range(tl.count):
        it = tl.item(i)
        print("PROBE|%s|%d %s|group %s|health %s|%s" % (tag, i, it.name, it.isGroup, it.healthState,
                                                        (it.errorOrWarningMessage or "").replace("\n", " ")[:200]))
        if it.isGroup:
            g = adsk.fusion.TimelineGroup.cast(it)
            for j in range(g.count):
                ch = g.item(j)
                ent = None
                try:
                    ent = ch.entity
                except Exception:                    # noqa: BLE001  (diagnostics only)
                    pass
                print("PROBE|%s|    %s|health %s|%s|%s" % (tag, ch.name, ch.healthState, (
                    ch.errorOrWarningMessage or "").replace("\n", " ")[:200], ent.objectType if ent else None))

    def tree(comp, depth):
        for k in range(comp.occurrences.count):
            o = comp.occurrences.item(k)
            c = o.component
            print("PROBE|%s|tree %s%s | pn %r | bodies %d" % (tag, "  " * depth, o.name, c.partNumber,
                                                             c.bRepBodies.count))
            tree(c, depth + 1)
    tree(design.rootComponent, 0)


def probe_import(app, design, repo_root, pn):
    """The builders' import of a Joints STEP, step by step, with the timeline's health after each."""
    root = design.rootComponent
    paths = glob.glob(os.path.join(repo_root, "v2/03-Manufacturing/joints/%s_P01_*_STEP.step" % pn))
    if not paths:
        raise RuntimeError("no Joints STEP for %s" % pn)
    frame_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    frame = frame_occ.component
    frame.name = "PROBE FRAME"
    timeline_report(design, "0 frame made")
    opts = app.importManager.createSTEPImportOptions(paths[0])
    opts.isViewFit = False
    if not app.importManager.importToTarget(opts, frame):
        raise RuntimeError("import failed")
    timeline_report(design, "1 imported into the frame")
    occ = frame.occurrences.item(frame.occurrences.count - 1)
    c = occ.component
    while c.bRepBodies.count == 0 and c.occurrences.count == 1:
        c = c.occurrences.item(0).component
    c.name = "%s PROBE PART" % pn
    c.partNumber = pn
    c.description = "probe"
    c.bRepBodies.item(0).name = "PROBE BODY"
    timeline_report(design, "2 renamed")
    lib = app.materialLibraries.itemByName("Fusion Material Library")
    mat = design.materials.addByCopy(lib.materials.itemByName("Aluminum"), "PROBE STEEL 7850")
    adsk.core.FloatProperty.cast(mat.materialProperties.itemById("structural_Density")).value = 7850.0
    c.bRepBodies.item(0).material = mat
    timeline_report(design, "3 material")
    jin = c.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(c.originConstructionPoint))
    jin.zAxisEntity = c.yConstructionAxis
    jin.xAxisEntity = c.xConstructionAxis
    ref = c.jointOrigins.add(jin)
    timeline_report(design, "4 joint origin in the part")
    sk = frame.sketches.add(frame.xYConstructionPlane)
    pt = sk.sketchPoints.add(adsk.core.Point3D.create(5.0, 3.0, 0.0))
    cin = frame.jointOrigins.createInput(adsk.fusion.JointGeometry.createByPoint(pt))
    tgt = frame.jointOrigins.add(cin)
    first = list(frame.allOccurrencesByComponent(c))[0]
    jn = root.joints.createInput(ref.createForAssemblyContext(first.createForAssemblyContext(frame_occ)),
                                 tgt.createForAssemblyContext(frame_occ))
    jn.setAsRigidJointMotion()
    root.joints.add(jn)
    timeline_report(design, "5 root joint moves the first copy")
    copy = frame.occurrences.addExistingComponent(c, adsk.core.Matrix3D.create())
    timeline_report(design, "6 second copy added to the frame")
    print("PROBE|done %s: second copy %s" % (pn, copy.name))


def run(_context):
    app = adsk.core.Application.get()
    before = app.activeDocument
    done, failed = [], []
    for spec in [x.strip() for x in ARGS.get("specs", "").split(";") if x.strip()]:
        doc = None
        try:
            builder, part, position = spec.split(":")
            if builder not in BUILDERS and builder != "probe":
                raise RuntimeError("bad spec %r" % spec)
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
            doc.activate()
            if builder == "probe":
                print("DRY|start %s (unsaved document)" % spec)
                probe_import(app, design, ARGS["repo_root"], position)
                done.append(spec)
                print("DRY|done %s" % spec)
                continue
            path = os.path.join(ARGS["repo_root"], BUILDERS[builder])
            # link=parse: the skeleton's values copied from pod_skeleton.py, so the unsaved document needs no cloud
            # derive (a real build derives them from the cloud skeleton)
            sargs = dict(builder_args(builder, part, position), repo_root=ARGS["repo_root"], dry="1", link="parse")
            ns = {"__name__": "__fusion_script__", "__file__": path, "SCRIPT_ARGS": sargs}
            print("DRY|start %s (unsaved document)" % spec)
            with open(path, "r", encoding="utf-8") as fh:
                exec(compile(fh.read(), path, "exec"), ns)
            ns["run"](None)
            done.append(spec)
            print("DRY|done %s" % spec)
        except Exception as exc:                          # noqa: BLE001  (report, close, go on)
            failed.append(spec)
            print("DRY|FAIL %s: %s" % (spec, exc))
            print(traceback.format_exc()[-1500:])
        finally:
            if doc is not None and doc.isValid:
                try:
                    doc.close(False)                     # never saved
                except Exception as exc:                 # noqa: BLE001
                    print("DRY|could not close the dry-run document: %s" % exc)
    if before is not None and before.isValid:
        before.activate()
    print("DRY|summary: %d done, %d failed%s" % (len(done), len(failed), (": " + ", ".join(failed)) if failed else ""))
