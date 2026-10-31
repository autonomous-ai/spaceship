"""Update the pod skeleton IN PLACE: a new version of the same cloud file.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/skeleton/skeleton_update.py \\
        --doc 100000_P04_POD-SKELETON_CAD --close [--arg dry_run=1] [--arg note="..."]

Parts link to the skeleton's cloud file through Derive. Rebuilding the
skeleton (pod_skeleton.py) makes a NEW file and would cut every link, so value
changes go in here instead (Reviewer 5, P3-1 on PR #24):

1. read the parameter table (PARAMS) and the envelope rules from pod_skeleton.py;
2. in the open skeleton: add missing parameters (in table order), then set each
   parameter's expression, comment and favorite flag from the table. Nothing is
   deleted (a part may derive it); a parameter no longer in the table is listed;
3. recompute and check: timeline healthy, no loose sketch, every envelope and
   anchor where its expressions say, no clash beyond the listed ones;
4. save a new version, then export the f3d, the STEP and the parameter CSV from
   it (same paths as the build);
5. dry_run=1 does 1-3 and stops without saving (close with --discard). Note: a
   skeleton that a linked part keeps loaded stays loaded after --close, with the
   dry run's changes; the next real run checks and saves them.

A check that fails raises, and Fusion rolls every change of this run back.
Changes to the shape (a new body, a new rule in ENVELOPES) need a rebuild and
a new revision; this script refuses them by failing the envelope check.
Linked parts pick the new values up with Document.updateAllReferences().
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def load(rel):
    ns = {"SCRIPT_ARGS": {}, "__name__": "skeleton_module"}
    path = "%s/%s" % (ARGS["repo_root"], rel)
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), ns)
    return ns


def bodies_by_code(design):
    out = {}
    for c in design.allComponents:
        for b in c.bRepBodies:
            code = b.name
            for suffix in (" ENVELOPE", " FACETED", " GLASS"):
                code = code.replace(suffix, "")
            out[code] = b
    return out


def run(_context):
    app = adsk.core.Application.get()
    sk = load("v2/01-CAD-Native/skeleton/pod_skeleton.py")
    et = load("v2/01-CAD-Native/skeleton/edit_test_skeleton.py")
    doc = app.activeDocument
    if doc.name != sk["DOC_NAME"]:
        raise RuntimeError("the active document is %r, not %r (run with --doc %s)"
                           % (doc.name, sk["DOC_NAME"], sk["DOC_NAME"]))
    design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
    up = design.userParameters
    vi = adsk.core.ValueInput.createByString

    # 2. parameters: add the missing ones first (table order keeps dependencies), then sync
    added, changed, comments = [], [], 0
    for name, expr, unit, status, src in sk["PARAMS"]:
        if up.itemByName(name) is None:
            p = up.add(name, vi(expr), unit, "%s: %s" % (status.upper(), src))
            p.isFavorite = True
            added.append(name)
    for name, expr, unit, status, src in sk["PARAMS"]:
        p = up.itemByName(name)
        comment = "%s: %s" % (status.upper(), src)
        if name not in added and p.expression.replace(" ", "") != expr.replace(" ", ""):
            old = p.expression
            p.expression = expr
            changed.append("%s: %s -> %s" % (name, old, expr))
        if p.comment != comment:
            p.comment = comment
            comments += 1
        if not p.isFavorite:
            p.isFavorite = True
    known = {row[0] for row in sk["PARAMS"]}
    extra = [up.item(i).name for i in range(up.count) if up.item(i).name not in known]
    # Descriptions: Fusion keeps the first description of a part number (setting it
    # here reads back unchanged, 2026-10-31), so they are only reported.
    want = sk["descriptions"]()
    desc = []
    stale = ["%s: %r" % (c.partNumber, c.description)
             for c in [design.rootComponent] + [o.component for o in design.rootComponent.occurrences]
             if c.partNumber in want and c.description != want[c.partNumber]]
    adsk.doEvents()
    print("parameters: %d added %s" % (len(added), added))
    for line in changed:
        print("changed:", line)
    print("comments updated: %d; not in the table (kept): %s" % (comments, extra))
    print("descriptions that differ from the table (Fusion keeps the first one; a person edits them): %d" % len(stale))

    # 3. checks
    tl = design.timeline
    unhealthy = [tl.item(i).name for i in range(tl.count)
                 if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    loose = [s.name for c in design.allComponents for s in c.sketches if not s.isFullyConstrained]
    res = et["check"](design, sk["ENVELOPES"], sk["FACET_ANCHORS"])
    hits, bad = sk["clash_check"](bodies_by_code(design))
    print("timeline %d items, unhealthy %s; loose sketches %s" % (tl.count, unhealthy, loose))
    print("envelopes and anchors off their expressions: %s (worst %g mm)" % (res["bad"] or "none", res["worst"]))
    print("clash pairs %d, unexpected %s" % (len(hits), bad))
    print("pod box", sk["box"](design.rootComponent))
    if unhealthy or loose or res["bad"] or bad:
        raise RuntimeError("checks failed: nothing saved, every change rolled back")
    if not (added or changed or comments or doc.isModified):
        print("nothing to change")
        return
    if not (added or changed or comments):
        # A closed document that another open design links to stays loaded with its
        # changes (seen after a dry run, 2026-10-31); the checks above ran on them.
        print("no new changes, but the open skeleton has unsaved ones; checked above")
    if ARGS.get("dry_run") == "1":
        print("dry run: not saved (close with --discard)")
        return

    # 4. new version, then exports from it
    note = ARGS.get("note") or "parameters from pod_skeleton.py"
    if not doc.save("update in place: %s" % note):
        raise RuntimeError("save failed")
    adsk.doEvents()
    print("saved a new version of %s" % doc.name)
    sk["export_files"](design, ARGS["repo_root"])
