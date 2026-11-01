"""Everything after a WALL build, in one Fusion run (the lock is shared by five engineers).

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/post_wall_doc.py \
        --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --arg pn=210101 --close --discard

The export breaks the design's Derive link in memory so the .f3d opens on its own, which is why the run
closes with --discard: the cloud design keeps its link.

On the active, saved design: export_wall_doc.py (.f3d and STEP, STEP re-read), report_wall_doc.py (CAD
report JSON), export_flat_dxf.py (cassettes: the tray's flat pattern) and edit_test_wall.py (on a copy of
the exported .f3d; its record goes to v2/01-CAD-Native/wall/out/edit-<pn>.md). Each step is its own
script, run here in turn; the first that raises stops the run.
"""

import os

ARGS = globals().get("SCRIPT_ARGS", {})
HERE = "v2/01-CAD-Native/wall"


def step(rel, **extra):
    path = os.path.join(ARGS["repo_root"], HERE, rel)
    ns = {"__name__": "__fusion_step__", "__file__": path, "SCRIPT_ARGS": dict(ARGS, **extra)}
    with open(path, "r", encoding="utf-8") as fh:
        exec(compile(fh.read(), path, "exec"), ns)
    print("== %s (file %s)" % (rel, os.path.realpath(path)))     # helpers by full path, never by module name
    ns["run"](None)


def run(_context):
    import adsk.core
    pn = ARGS["pn"]
    name = adsk.core.Application.get().activeDocument.name
    step("export_wall_doc.py")
    step("report_wall_doc.py", out="v2/03-Manufacturing/wall/out/%s.json" % pn)
    if pn.startswith("51"):
        step("export_flat_dxf.py")
    step("edit_test_wall.py", f3d="%s/%s.f3d" % (HERE, name), out="%s/out/edit-%s.md" % (HERE, pn))
