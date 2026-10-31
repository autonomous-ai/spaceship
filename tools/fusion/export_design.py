#!/usr/bin/env python3
"""Export a saved design for the repo: .f3d (opens on its own) and STEP, checked.

    python3 tools/fusion/export_design.py DESIGN_NAME PART_NUMBER F3D_DIR STEP_DIR [--no-f3d-check]

    e.g. python3 tools/fusion/export_design.py 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD 210101 \\
             v2/01-CAD-Native/wall v2/03-Manufacturing/wall

One copy for every team (PM ruling 2026-10-31, from the WALL Engineer's
export_wall_doc.py). Under the Fusion lock:

1. open or activate DESIGN_NAME; refuse unless it is saved, has no unsaved
   changes and its root part number is PART_NUMBER (so it never exports
   someone else's document);
2. break every Derive link IN MEMORY: a local .f3d that still holds the link
   to the skeleton can't be opened on its own ("New design cannot be created
   from a local file containing external references", Fusion 2706.1), so the
   exported .f3d carries the skeleton's values of this saved version;
3. export F3D_DIR/DESIGN_NAME.f3d and STEP_DIR/PARTNO_REV_NAME_STEP.step
   (Fusion writes cm, declared in the file; D-13), retrying while Fusion
   uploads;
4. re-read the STEP in Fusion and compare its solid box with the design's
   (0.05 mm), and open the exported .f3d as a new document to show it opens
   on its own with a healthy timeline (--no-f3d-check skips this);
5. undo the broken links: the export script ends by raising on purpose, and
   Fusion rolls back every change a failed script made, so the design is back
   in its saved, linked state (checked); the files on disk stay. Then close it
   if this command opened it (an already open design is left open, as found).
   This is why it's one command: done by hand, a forgotten --discard could
   leave broken links in an open document that a later save would keep.

Exit 0 = exported and checked, 1 = refused or a check failed (the design is
still closed without saving), 2 = Fusion not reachable, 3 = lock busy.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_script as rs  # noqa: E402

EXPORT_SCRIPT = '''import os, time
import adsk.core, adsk.fusion
A = %(args)r

def solid_box(design):
    """Box of the solid bodies only (a derived plane would stretch it; STEP has no planes)."""
    bodies = [b for c in design.allComponents for b in c.bRepBodies]
    if not bodies:
        return None
    lo = [min(getattr(b.boundingBox.minPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    hi = [max(getattr(b.boundingBox.maxPoint, a) for b in bodies) * 10.0 for a in "xyz"]
    return [round(v, 2) for v in lo + hi]

def export(em, mk, path, root):
    for _try in range(10):          # right after a save Fusion may still be uploading
        if em.execute(mk(path, root)) and os.path.exists(path) and os.path.getsize(path) > 1000:
            return True
        adsk.doEvents()
        time.sleep(3)
    return False

def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    if design is None or doc.name != A["name"]:
        raise RuntimeError("the active document is %%r, not the design %%r" %% (doc.name, A["name"]))
    root = design.rootComponent
    if root.partNumber != A["pn"]:
        raise RuntimeError("%%r has root part number %%r, not %%r" %% (doc.name, root.partNumber, A["pn"]))
    if not doc.isSaved or doc.isModified:
        raise RuntimeError("save the design before exporting (saved=%%s, modified=%%s)" %% (doc.isSaved, doc.isModified))
    if not doc.name.endswith("_CAD"):
        raise RuntimeError("document name %%r does not end in _CAD" %% doc.name)
    broken = []
    for c in design.allComponents:
        for d in c.features.deriveFeatures:
            try:
                df = d.documentReference.dataFile
                src = "%%s v%%s" %% (df.name, df.versionNumber)
            except Exception:
                src = "a linked design (version not readable)"
            if not d.breakLink():
                raise RuntimeError("could not break the derive link to %%s for the export" %% src)
            broken.append(src)
    print("derive links broken in memory for the export (closed without saving): %%s" %% (broken or "none"))
    f3d = os.path.join(A["repo"], A["f3d_dir"], doc.name + ".f3d")
    step = os.path.join(A["repo"], A["step_dir"], doc.name[:-4] + "_STEP.step")
    for p in (f3d, step):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    em = design.exportManager
    ok_f3d = export(em, em.createFusionArchiveExportOptions, f3d, root)
    ok_step = export(em, em.createSTEPExportOptions, step, root)
    print("export %%s: %%s" %% (os.path.relpath(f3d, A["repo"]), ok_f3d))
    print("export %%s: %%s" %% (os.path.relpath(step, A["repo"]), ok_step))
    if not (ok_f3d and ok_step):
        raise RuntimeError("export failed")
    want = solid_box(design)
    copy = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(step))
    try:
        got = solid_box(adsk.fusion.Design.cast(copy.products.itemByProductType("DesignProductType")))
    finally:
        copy.close(False)
        doc.activate()
    diff = max(abs(a - b) for a, b in zip(want, got)) if want and got else None
    print("solid box: design %%s, STEP %%s, max difference %%s mm" %% (want, got, diff))
    if diff is None or diff > 0.05:
        raise RuntimeError("the STEP re-read does not match the design")
    if A["f3d_check"]:
        f = app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(f3d))
        try:
            fd = adsk.fusion.Design.cast(f.products.itemByProductType("DesignProductType"))
            tl = fd.timeline
            n_items = tl.count             # read everything before the copy is closed: its
            bad = [tl.item(i).name for i in range(n_items)     # objects are gone after (live 2026-10-31)
                   if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
            fbox = solid_box(fd)
        finally:
            f.close(False)
            doc.activate()
        fdiff = max(abs(a - b) for a, b in zip(want, fbox)) if fbox else None
        print(".f3d opens on its own: %%d timeline items, unhealthy %%s, box difference %%s mm" %% (
            n_items, bad, fdiff))
        if bad or fdiff is None or fdiff > 0.05:
            raise RuntimeError("the exported .f3d does not reopen healthy and the same size")
    # Undo the broken links: a script that raises has all its changes rolled
    # back by Fusion, so the design goes back to its saved, linked state even if
    # it can't be closed (an open assembly may keep it loaded). The files stay.
    raise RuntimeError(%(sentinel)r)
'''

SENTINEL = "EXPORTED-OK-LINKS-ROLLED-BACK"

LINK_CHECK = '''import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    n, linked = 0, 0
    for c in design.allComponents:
        for d in c.features.deriveFeatures:
            n += 1
            try:
                if d.documentReference is not None:
                    linked += 1
            except Exception:
                pass
    print("after the export: %d derive feature(s), %d still linked, modified=%s" % (n, linked, doc.isModified))
    if linked != n or doc.isModified:
        raise RuntimeError("the design's derive links did not come back")
'''


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export a saved design for the repo (.f3d that "
                                             "opens on its own, and STEP), checked.")
    ap.add_argument("design", help="the saved design's name, ending in _CAD")
    ap.add_argument("part_number", help="its root component's part number (a guard)")
    ap.add_argument("f3d_dir", help="repo folder for the .f3d, e.g. v2/01-CAD-Native/wall")
    ap.add_argument("step_dir", help="repo folder for the STEP, e.g. v2/03-Manufacturing/wall")
    ap.add_argument("--no-f3d-check", action="store_true", help="skip reopening the .f3d")
    ap.add_argument("--folder", default=rs.DEFAULT_FOLDER)
    ap.add_argument("--url", default=rs.DEFAULT_URL)
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--lock", default=None)
    ap.add_argument("--lock-wait", type=float, default=1200.0)
    ap.add_argument("--label", default=os.environ.get(rs.LABEL_ENV, ""))
    opts = ap.parse_args(argv)

    lock = rs.FusionLock(opts.lock or rs.default_lock_path(opts.url),
                         label=opts.label or "export_design", hold_s=4 * opts.timeout + 300,
                         script="export_design.py %s" % opts.design)
    try:
        lock.acquire(opts.lock_wait, token=os.environ.get(rs.TOKEN_ENV) or None)   # also inside a held lock
    except (rs.LockTimeout, KeyboardInterrupt) as e:
        print("export_design: %s" % (e or "stopped while waiting"), file=sys.stderr)
        return 3
    try:
        mcp = rs.FusionMcp(opts.url, opts.timeout)
        mcp.initialize()
        ok, out = rs.run_in_fusion(mcp, rs.doc_script("open", opts.design, opts.folder))
        if not ok:
            print("export_design: couldn't open %s: %s" % (opts.design, out), file=sys.stderr)
            return 1
        opened_here = any(line.startswith("run_script: opened") for line in (out or "").splitlines())   # the runner may warn first
        try:
            ok, out = rs.run_in_fusion(mcp, EXPORT_SCRIPT % {"args": {
                "name": opts.design, "pn": opts.part_number, "repo": rs.REPO_ROOT,
                "f3d_dir": opts.f3d_dir, "step_dir": opts.step_dir,
                "f3d_check": not opts.no_f3d_check}, "sentinel": SENTINEL})
            exported = not ok and SENTINEL in (out or "")
            for line in (out or "").strip().splitlines():
                if SENTINEL in line or line.startswith(("Traceback", "  File", "    ")):
                    continue
                print("export_design: %s" % line)
            if not exported:
                print("export_design: the export failed (see above); links rolled back", file=sys.stderr)
                ok = False
            else:
                lok, lout = rs.run_in_fusion(mcp, LINK_CHECK, read_only=True)
                print("export_design: %s" % (lout or "").strip())
                ok = lok
        finally:
            if opened_here:
                # nothing of ours is left to save (rolled back); discard is only a backstop
                cok, cout = rs.run_in_fusion(mcp, rs.doc_script("close", opts.design, opts.folder,
                                                                discard=True))
                print("export_design: %s" % ((cout or "").strip() if cok else "CLOSE FAILED: %s" % cout))
            else:
                print("export_design: %s was already open; left open as it was" % opts.design)
        return 0 if ok else 1
    except rs.McpError as e:
        print("export_design: %s" % e, file=sys.stderr)
        return 2
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
