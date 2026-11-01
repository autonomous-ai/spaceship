"""Late-binding loader for BASE's Fusion runs.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/base/late_base.py \
        --arg targets=v2/01-CAD-Native/base/base_build.py,v2/01-CAD-Native/base/base_edit_test.py \
        --arg ready=/path/to/flag ...

tools/fusion/run_script.py reads its script when it starts, then waits for
the shared Fusion lock, so a run queued long ago would build old code. This
loader is what waits in the queue; it reads each target only when the lock is
granted, then runs the targets one after another in the same run (fewer,
bigger runs keep the shared queue short). Every other --arg reaches each
target unchanged as SCRIPT_ARGS.

--arg ready=FILE: if FILE does not exist when the lock is granted, stop at
once with "NOT READY" (the lock goes back within seconds) instead of running
code that is half-way through an edit.
"""

import os


def run(context):
    args = dict(globals().get("SCRIPT_ARGS", {}))
    root = args.get("repo_root") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    flag = args.get("ready")
    if flag and not os.path.exists(flag):
        raise RuntimeError("NOT READY: %s is missing, so nothing ran" % flag)
    targets = [t.strip() for t in args.pop("targets", "").split(",") if t.strip()]
    if not targets:
        raise RuntimeError("no targets")
    for rel_path in targets:
        path = os.path.join(root, rel_path)
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        ns = {"__name__": "__fusion_script__", "__file__": path, "SCRIPT_ARGS": dict(args, script_path=path)}
        exec(compile(source, path, "exec"), ns)
        print("== late_base: running %s (%s)" % (rel_path, path))
        ns["run"](context)
        print("== late_base: %s finished" % rel_path)
