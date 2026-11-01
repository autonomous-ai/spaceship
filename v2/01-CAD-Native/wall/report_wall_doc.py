"""Read-only report of the active WALL design, written as JSON for the parts list and feature rationale.

    python3 tools/fusion/run_script.py v2/01-CAD-Native/wall/report_wall_doc.py --read-only \
        --doc 210101_P01_WALL-PANEL-ASSY-SIDE-LOWER-LH_CAD --arg out=v2/03-Manufacturing/wall/out/210101.json

Writes: document name and version, every component (part number, name, description), every body
(name, box, volume, area, mass, material), every hole (diameter, axis, centre, the wall it goes
through) and every user parameter (expression, value, comment). Nothing in the design changes.
"""

import json
import os

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})


def r(v, n=3):
    return round(v, n)


def box(b):
    bb = b.boundingBox
    return [r(v * 10.0, 2) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                     bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)]


def holes(body):
    """Full-circle holes from their cylindrical faces: true axis from the surface, so a half arc of a
    slot reports its real centre too (flagged partial)."""
    out = []
    for f in body.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
            continue
        g = adsk.core.Cylinder.cast(f.geometry)
        ax = max(range(3), key=lambda i: abs((g.axis.x, g.axis.y, g.axis.z)[i]))
        o = (g.origin.x * 10, g.origin.y * 10, g.origin.z * 10)
        fb = box(f)
        lo, hi = fb[ax], fb[ax + 3]
        # project the surface origin onto the face's span to get the centre in the other two axes
        ctr = [r(o[i], 2) for i in range(3)]
        ctr[ax] = None
        full = all(abs((fb[i + 3] - fb[i]) - g.radius * 20) < 0.05 for i in range(3) if i != ax)
        out.append({"d": r(g.radius * 20, 2), "axis": "xyz"[ax], "centre": ctr, "from": lo, "to": hi,
                    "full_circle": full})
    return out


def run(_context):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    rep = {"document": doc.name, "version": doc.dataFile.versionNumber if doc.dataFile else None,
           "saved": doc.isSaved, "modified": doc.isModified, "components": [], "parameters": []}
    root = design.rootComponent
    for c in design.allComponents:
        # D-120: a part placed several times is one component with several copies (occurrences); the copies'
        # parents tell the assembly tree (a frame's members, a fill's pieces, the panel's hardware)
        occs = [] if c == root else [root.allOccurrencesByComponent(c).item(i)
                                     for i in range(root.allOccurrencesByComponent(c).count)]
        parents = sorted({(o.assemblyContext.component.partNumber if o.assemblyContext else root.partNumber)
                          for o in occs})
        comp: dict = {"part_number": c.partNumber, "name": c.name, "description": c.description,
                      "is_root": c == root, "copies": 1 if c == root else len(occs), "parents": parents,
                      "bodies": []}
        for b in c.bRepBodies:
            pp = b.physicalProperties
            comp["bodies"].append({"name": b.name, "box": box(b), "volume_mm3": r(b.volume * 1000.0, 1),
                                   "area_mm2": r(b.area * 100.0, 1), "mass_kg": r(pp.mass, 4),
                                   "material": b.material.name if b.material else None, "holes": holes(b)})
        rep["components"].append(comp)
    for p in design.userParameters:
        rep["parameters"].append({"name": p.name, "expression": p.expression, "unit": p.unit,
                                  "value": r(p.value * 10.0, 4) if p.unit == "mm" else r(p.value, 4),
                                  "comment": p.comment})
    path = os.path.join(ARGS["repo_root"], ARGS["out"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print("wrote %s: %d components, %d bodies, %d holes, %d parameters" % (
        ARGS["out"], len(rep["components"]), sum(len(c["bodies"]) for c in rep["components"]),
        sum(len(b["holes"]) for c in rep["components"] for b in c["bodies"]), len(rep["parameters"])))
