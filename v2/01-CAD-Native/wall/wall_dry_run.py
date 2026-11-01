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

With --arg post=1 --arg out_dir=ABS (a folder outside the repo), each built design also gets its CAD report
(report_wall_doc.py) and a STEP written there, so the parts list and the offline STEP checks can run on them; a
build whose only failure is its end checks (a clash, say) still gets them, marked so. Panel specs (or the parts
named in --arg edit=panel,frame) also get the edit test (edit_test_wall.py) on an .f3d copy there. Nothing goes to
the repo.

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


def dry_post(app, design, spec, note=""):
    """The dry run's stand-in for post_wall_doc.py: the CAD report and a STEP of the unsaved design, both into
    out_dir (never the repo)."""
    out_dir = ARGS.get("out_dir", "")
    if not out_dir or not os.path.isabs(out_dir) or os.path.realpath(out_dir).startswith(
            os.path.realpath(ARGS["repo_root"])):
        raise RuntimeError("post=1 needs an absolute out_dir outside the repo, got %r" % out_dir)
    os.makedirs(out_dir, exist_ok=True)
    root = design.rootComponent
    pn = root.partNumber
    path = os.path.join(ARGS["repo_root"], "v2/01-CAD-Native/wall/report_wall_doc.py")
    ns = {"__name__": "__fusion_report__", "__file__": path,
          "SCRIPT_ARGS": {"repo_root": ARGS["repo_root"], "out": os.path.join(out_dir, "%s.json" % pn)}}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    ns["run"](None)
    step = os.path.join(out_dir, "%s_P01_DRY_STEP.step" % pn)
    em = design.exportManager
    ok = em.execute(em.createSTEPExportOptions(step, root))
    print("DRY|post %s%s: report %s.json, STEP %s (%s, %d bytes)" % (
        spec, note, pn, os.path.basename(step), ok, os.path.getsize(step) if os.path.isfile(step) else 0))
    if spec.split(":")[1] not in ARGS.get("edit", "panel").split(","):
        return
    # the edit test on a copy, as post_wall_doc.py runs it: the .f3d of this unsaved design (link=parse, so it holds
    # no outside reference), opened as its own unsaved document by edit_test_wall.py and closed without saving
    f3d = os.path.join(out_dir, "%s_P01_DRY.f3d" % pn)
    if not em.execute(em.createFusionArchiveExportOptions(f3d, root)):
        raise RuntimeError("the .f3d export for the edit test failed")
    path = os.path.join(ARGS["repo_root"], "v2/01-CAD-Native/wall/edit_test_wall.py")
    rel = lambda q: os.path.relpath(q, ARGS["repo_root"])          # noqa: E731  (the test joins repo_root + "/" + f3d)
    ns = {"__name__": "__fusion_edit__", "__file__": path,
          "SCRIPT_ARGS": {"repo_root": ARGS["repo_root"], "f3d": rel(f3d),
                          "out": rel(os.path.join(out_dir, "edit-%s.md" % pn))}}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    ns["run"](None)
    design.parentDocument.activate()
    print("DRY|post %s: edit test written to edit-%s.md" % (spec, pn))


def probe_ledge(design, repo_root, position):
    """probe:ledge:L1 - the cassette ledge's fold tried every way in a blank unsaved design (dry run 10 found no
    edge-flange setting that landed the leg on its outline): the side builder's parameters and helpers, the upright's
    base flange as build_ledge makes it, then for each long bottom edge of the upright, each height datum, bend
    position and flip, the edge flange's box and health printed (PROBE|...) and the flange deleted."""
    path = os.path.join(repo_root, BUILDERS["side"])
    sargs = dict(builder_args("side", "panel", position), repo_root=repo_root, dry="1", link="parse")
    ns = {"__name__": "__fusion_script__", "__file__": path, "SCRIPT_ARGS": sargs}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    root = design.rootComponent
    ns["add_params"](design, repo_root)
    ev, vi, sx, bbox = ns["ev"], ns["vi"], ns["sx"], ns["bbox"]
    s_, z0, xf_e, y0 = ns["S"], ns["Z0"], ns["X_FRAME_IN"], ns["LEDGE_Y0"]
    ledge = ns["new_comp"](root, "ledge", sheet_metal=True)
    rule = design.designSheetMetalRules.addByCopy(ledge.activeSheetMetalRule, "PROBE - LEDGE RULE")
    rule.thickness.expression = "%.4f mm" % ev(design, "ledge_t")
    rule.bendRadius.expression = "Thickness"
    rule.kFactor = 0.44
    ledge.activeSheetMetalRule = rule
    occ = [o for o in root.occurrences if o.component == ledge][0]
    occ.activate()
    yr = (y0, "%s + ledge_len" % y0)
    zr = ("(%s) - ledge_pad_t - ledge_t" % z0, "(%s) + ledge_up" % z0)
    xf, t = ev(design, xf_e), ev(design, "ledge_t")
    zb = ev(design, zr[0])
    print("PROBE|want X %.2f to %.2f, Y %.2f to %.2f, Z %.2f to %.2f" % (
        xf, ev(design, sx("pod_w / 2 - outer_t - ledge_out")), ev(design, yr[0]), ev(design, yr[1]), zb,
        ev(design, zr[1])))
    sk = ns["rect_on_x"](design, ledge, xf_e, yr, zr, "PROBE UPRIGHT")
    ff = ledge.features.flangeFeatures
    base = None
    for orient in (adsk.fusion.FlangeOrientations.SideOneFlangeOrientation,
                   adsk.fusion.FlangeOrientations.SideTwoFlangeOrientation):
        bfi = ff.createBaseFlangeInput([sk.profiles.item(0)])
        bfi.orientation = orient
        f = ff.add(bfi)
        b = bbox(f.bodies.item(0))
        print("PROBE|base orientation %s: box %s" % (orient, b))
        back, room = (b[0], b[3]) if s_ < 0 else (b[3], b[0])
        if abs(back - xf) < 0.01 and abs(room - (xf - s_ * t)) < 0.01:
            base = f
            break
        f.deleteMe()
    if base is None:
        print("PROBE|no base flange orientation on the room side")
        design.activateRootComponent()
        return
    datums = [n for n in dir(adsk.fusion.FlangeHeightDatumTypes) if n.endswith("Type")]
    positions = [n for n in dir(adsk.fusion.BendPositionTypes) if n.endswith("Type")]
    print("PROBE|height datums %s; bend positions %s" % (datums, positions))
    for xe in (xf - s_ * t, xf):                       # the upright's room-side and frame-side bottom edges
        for dn in datums:
            for pn_ in positions:
                for flip in (False, True):
                    tag = "edge x %.2f, %s, %s, flip %s" % (xe, dn, pn_, flip)
                    body = ledge.bRepBodies.item(0)
                    eds = [e for e in body.edges if e.geometry.objectType == adsk.core.Line3D.classType()
                           and e.length * 10 > 100
                           and all(abs(v.geometry.x * 10 - xe) < 0.01 and abs(v.geometry.z * 10 - zb) < 0.01
                                   for v in (e.startVertex, e.endVertex))]
                    if len(eds) != 1:
                        print("PROBE|%s: %d edges found" % (tag, len(eds)))
                        continue
                    try:
                        efi = ff.createEdgeFlangeInput([], vi("ledge_out - ledge_t - ledge_r"))
                        efi.edgeDefinitions.addFullLengthEdge(eds[0])
                        efi.heightDatumType = getattr(adsk.fusion.FlangeHeightDatumTypes, dn)
                        efi.bendPositionType = getattr(adsk.fusion.BendPositionTypes, pn_)
                        efi.isFlipped = flip
                        f = ff.add(efi)
                        print("PROBE|%s: health %s, box %s" % (tag, f.healthState, bbox(ledge.bRepBodies.item(0))))
                        f.deleteMe()
                    except Exception as exc:              # noqa: BLE001  (print, go on)
                        print("PROBE|%s: FAILED %s" % (tag, str(exc).splitlines()[0][:160]))
    design.activateRootComponent()


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
                if part == "ledge":
                    probe_ledge(design, ARGS["repo_root"], position)
                else:
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
            try:
                ns["run"](None)
            except RuntimeError as exc:
                # the end checks failed (printed above): the design is whole, so the dry post steps still run
                if ARGS.get("post") == "1" and str(exc).startswith("checks failed"):
                    dry_post(app, design, spec, " (ITS END CHECKS FAILED, see above)")
                raise
            if ARGS.get("post") == "1":
                dry_post(app, design, spec)
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
