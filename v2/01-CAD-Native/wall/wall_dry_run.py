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
"""

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


def run(_context):
    app = adsk.core.Application.get()
    before = app.activeDocument
    done, failed = [], []
    for spec in [x.strip() for x in ARGS.get("specs", "").split(";") if x.strip()]:
        doc = None
        try:
            builder, part, position = spec.split(":")
            if builder not in BUILDERS:
                raise RuntimeError("bad spec %r" % spec)
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
            doc.activate()
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
