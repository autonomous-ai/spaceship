"""FRONT combined check: the FRONT sub-assemblies together, in a new unsaved document.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/front/front_check.py \
        --arg parts=v2/01-CAD-Native/front/360001_P01_FRONT-DOOR-UNIT_CAD.f3d,v2/01-CAD-Native/front/360002_P01_FRONT-FIXED-GLASS-UNIT_CAD.f3d,...

Imports each exported .f3d into one new document (all are built in place in
the pod system, so no transform), then:
- intersects every body of one sub-assembly with every body of the others and
  prints each overlap over 1 mm3 with its box (FAIL if any is not listed in
  EXPECTED below);
- measures the clearances listed in GAPS (minimum distance between bodies);
- works out the glass band through which a viewer outside sees the soffit's
  underside (the CEILING Engineer's soffit, sizes from the D-60 air table).
The document is closed without saving.
"""

import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})

# body-name pairs (prefix match) that may overlap, with the reason
EXPECTED = []

# clearances to measure: (label, body name A, body name B)
GAPS = [
    ("supply fan box to the fixed glass channel", "SUPPLY FAN BOX", "GLAZING U-PROFILE"),
    ("lower transition space to the fixed glass channel", "HOLD LOWER TRANSITION", "GLAZING U-PROFILE"),
    ("intake riser to the fixed glass channel", "INTAKE RISER", "GLAZING U-PROFILE"),
    ("fixed pane to DR's skin (through the slot)", "FIXED GLASS 4+4", "DR SKIN ACP 3"),
    ("glass channel to DR's skin", "GLAZING U-PROFILE", "DR SKIN ACP 3"),
    ("door leaf to the fixed pane", "DOOR LEAF GLASS 4+4", "FIXED GLASS 4+4"),
    ("kick strip to the fixed glass channel", "KICK STRIP", "GLAZING U-PROFILE"),
    ("door leaf to DR's skin", "DOOR LEAF GLASS 4+4", "DR SKIN ACP 3"),
    ("door leaf top to DT's skin (the catch gap, 6 by ruling)", "DOOR LEAF GLASS 4+4", "DT SKIN ACP 3"),
    ("catch to the strike (0 = the door stop touches)", "CATCH HT-MSG62",
     ("FRONT - DOOR STRIKE", "CATCH STRIKE HT-MSG62")),      # D-104 name, or the build before it
    ("catch to the door leaf", "CATCH HT-MSG62", "DOOR LEAF GLASS 4+4"),
    ("top seal to the door leaf (0 = sealing)", "FRAME-STOP SEAL PS 1515 - TOP", "DOOR LEAF GLASS 4+4"),
    ("hinge-side seal to the door leaf (0 = sealing)", "FRAME-STOP SEAL PS 1515 - HINGE SIDE", "DOOR LEAF GLASS 4+4"),
    ("hinge-side stop to the hinge spaces", "HINGE-SIDE STOP", "HOLD HINGE SPACE"),
    ("DL's skin to the hinge spaces (pocket clearance)", "DL SKIN ACP 3", "HOLD HINGE SPACE"),
    ("door leaf to DL's skin", "DOOR LEAF GLASS 4+4", "DL SKIN ACP 3"),
    ("fixed glass channel to DT's skin (slot clearance)", "GLAZING U-PROFILE", "DT SKIN ACP 3"),
    ("fixed pane to DT's skin", "FIXED GLASS 4+4", "DT SKIN ACP 3"),
    ("pull spaces to DR's skin", "HOLD PULL SPACE", "DR SKIN ACP 3"),
]

# the soffit (CEILING), D-60 air table: X -1169 to 1169, Y -645 to -285, Z 2120 to 2340 (source)
SOFFIT_Y0, SOFFIT_Y1, SOFFIT_ZB = -645.0, -285.0, 2120.0
VIEWERS = [("standing", 1650.0, 1000.0), ("standing", 1650.0, 2000.0), ("standing", 1650.0, 4000.0),
           ("seated", 1200.0, 1000.0), ("seated", 1200.0, 2000.0), ("seated", 1200.0, 4000.0)]


def mm_box(b):
    bb = b.boundingBox
    return [round(v * 10.0, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                         bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]


def run(_context):
    app = adsk.core.Application.get()
    root_dir = ARGS["repo_root"]
    parts = [p.strip() for p in ARGS["parts"].split(",") if p.strip()]
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        im = app.importManager
        groups = {}
        for rel in parts:
            before = root.occurrences.count
            if not im.importToTarget(im.createFusionArchiveImportOptions(os.path.join(root_dir, rel)), root):
                raise RuntimeError("import failed: " + rel)
            occ = root.occurrences.item(before)
            bodies = []

            def walk(o):
                for i in range(o.bRepBodies.count):
                    bodies.append(o.bRepBodies.item(i))
                for k in range(o.childOccurrences.count):
                    walk(o.childOccurrences.item(k))
            walk(occ)
            groups[os.path.basename(rel)] = bodies
            print("imported %s: %d bodies" % (os.path.basename(rel), len(bodies)))
        tbm = adsk.fusion.TemporaryBRepManager.get()
        allowed = {frozenset(k) for k, _r in EXPECTED}
        names = list(groups)
        bad, hits = [], 0
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                for a in groups[names[i]]:
                    for b in groups[names[j]]:
                        ba, bb = mm_box(a), mm_box(b)
                        if not all(ba[k] < bb[k + 3] - 1e-6 and bb[k] < ba[k + 3] - 1e-6 for k in range(3)):
                            continue
                        t1, t2 = tbm.copy(a), tbm.copy(b)
                        tbm.booleanOperation(t1, t2, adsk.fusion.BooleanTypes.IntersectionBooleanType)
                        vol = t1.volume * 1000.0 if t1 else 0.0
                        if vol > 1.0:
                            hits += 1
                            key = frozenset((a.name, b.name))
                            listed = any(all(any(n.startswith(p) for n in key) for p in k) for k in allowed)
                            box = t1.boundingBox
                            print("OVERLAP|%s|%s|%d mm3|box %s|%s" % (a.name, b.name, round(vol), [round(v * 10, 2) for v in (
                                box.minPoint.x, box.minPoint.y, box.minPoint.z, box.maxPoint.x, box.maxPoint.y,
                                box.maxPoint.z)], "listed" if listed else "NOT LISTED"))
                            if not listed:
                                bad.append((a.name, b.name, round(vol)))
        print("overlaps between sub-assemblies: %d, not listed: %d" % (hits, len(bad)))
        allb = [b for g in groups.values() for b in g]
        mm = app.measureManager
        for label, na, nb in GAPS:
            ca = [b for b in allb if b.name.startswith(na)]
            cb = [b for b in allb if b.name.startswith(nb)]
            if not ca or not cb:
                print("GAP|%s|not measured (bodies missing)" % label)
                continue
            d = min(mm.measureMinimumDistance(x, y).value * 10.0 for x in ca for y in cb)
            print("GAP|%s|%.2f mm" % (label, d))
        # sight lines: the glass's outer face and the visible glass top from the model
        leaf = [b for b in allb if b.name.startswith("DOOR LEAF GLASS")]
        pane = [b for b in allb if b.name.startswith("FIXED GLASS 4+4")]
        if leaf:
            yg = mm_box(leaf[0])[1]
            tops = [("door", mm_box(leaf[0])[5])]
            if pane:
                tops.append(("fixed pane (visible top = DT's underside)", SOFFIT_ZB))
            print("SIGHT|glass outer face Y %.2f; soffit underside Z %.0f from Y %.0f to %.0f (D-60 air table)" % (
                yg, SOFFIT_ZB, SOFFIT_Y0, SOFFIT_Y1))
            for who, ze, dist in VIEWERS:
                # a ray through the glass at height zg reaches Z = SOFFIT_ZB at y = yg + (SOFFIT_ZB - zg) * dist / (zg - ze)
                def zg_for(y_hit):
                    dy = y_hit - yg
                    return (SOFFIT_ZB * dist + dy * ze) / (dist + dy)
                z_lo, z_hi = zg_for(SOFFIT_Y1), zg_for(SOFFIT_Y0)
                print("SIGHT|%s, eye %.0f, %.0f m from the glass|soffit underside seen through Z %.0f to %.0f (%.0f mm of glass); "
                      "DT's underside behind the glass above that" % (who, ze, dist / 1000.0, z_lo, z_hi, z_hi - z_lo))
        if bad:
            raise RuntimeError("overlaps not listed: %s" % bad)
    finally:
        doc.close(False)
