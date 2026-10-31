"""Build the bolt-joint test fixture for the Fusion check (C03, C07) and
export it as STEP. Run ONLY through the locked runner:

  python3 tools/fusion/run_script.py tools/checks/tests/fixtures/make_bolt_fixture.py \
      --arg out=<abs path>/bolt-joints.step

Four copies of the joints register's in-member joint (section 2.2), side
by side along X, each: a 1.2 mm bolt-side wall with a 6.6 hole, the 2.26
stop gap, a 1.2 mm nut-side wall with a 9.53 hole, a rivnut (body 9.5 OD,
thread modelled as a 5.0 bore, installed length 10.16), and the far wall of
a 20-deep tube (inner face 18.8 below the nut-side wall's outer face).
Bolts: M6 x 16 (right), M6 x 25 (runs into the far wall), M6 x 8 (engages
only part of the rivnut), M6 x 16 with a plate 20 mm above its head (tool
blocked). Known answers are in tests/test_fusion_results.py.
The script makes its own document, exports, and closes it without saving.
"""

import adsk.core
import adsk.fusion

ARGS = globals().get("SCRIPT_ARGS", {})
MM = 0.1


def P(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def box(tbm, x0, y0, z0, x1, y1, z1):
    c = P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob = adsk.core.OrientedBoundingBox3D.create(c, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                                                (x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    return tbm.createBox(ob)


def cyl(tbm, x, y, z0, z1, d):
    return tbm.createCylinderOrCone(P(x, y, z0), d / 2 * MM, P(x, y, z1), d / 2 * MM)


def cut(tbm, body, tool):
    tbm.booleanOperation(body, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType)
    return body


def add(root, pn, name, body):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "%s %s" % (pn, name)
    comp.partNumber = pn
    if root.parentDesign.designType == adsk.fusion.DesignTypes.DirectDesignType:
        b = comp.bRepBodies.add(body)
    else:
        bf = comp.features.baseFeatures.add()
        bf.startEdit()
        b = comp.bRepBodies.add(body, bf)
        bf.finishEdit()
    b.name = name
    return occ


def run(_context):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        root.partNumber = "CHECK-FIXTURE"
        tbm = adsk.fusion.TemporaryBRepManager.get()
        cases = [("A", 16.0, False), ("B", 25.0, False), ("C", 8.0, False), ("D", 16.0, True)]
        for i, (tag, L, blocked) in enumerate(cases):
            x = i * 100.0
            # bolt-side wall: Z 0 to 1.2, hole 6.6
            add(root, "21190%d" % i, "WALL - TEST WALL BOLT SIDE %s" % tag,
                cut(tbm, box(tbm, x - 30, -30, 0, x + 30, 30, 1.2), cyl(tbm, x, 0, -1, 3, 6.6)))
            # nut-side wall: Z -3.46 to -2.26, hole 9.53
            add(root, "21191%d" % i, "WALL - TEST WALL NUT SIDE %s" % tag,
                cut(tbm, box(tbm, x - 30, -30, -3.46, x + 30, 30, -2.26), cyl(tbm, x, 0, -5, 0, 9.53)))
            # rivnut: body 9.5 OD, bore 5.0 (thread minor), from the stop face Z -2.26 down to -12.42
            rn = cut(tbm, cyl(tbm, x, 0, -12.42, -2.26, 9.5), cyl(tbm, x, 0, -13, -1, 5.0))
            add(root, "83810%d" % i, "HARDWARE - RIVNUT - M6 %s" % tag, rn)
            # far wall of the 20-deep tube: Z -22.26 to -21.06, no hole
            add(root, "21192%d" % i, "WALL - TEST FAR WALL %s" % tag, box(tbm, x - 30, -30, -22.26, x + 30, 30, -21.06))
            # bolt: head 10 x 6 on top of the bolt-side wall, shank 6 x L down from Z 1.2
            # (the 0.4 mm overlap of shank and rivnut bore stands for the thread: allowed as BOLT-IN-THREAD)
            bolt = cyl(tbm, x, 0, 1.2 - L, 1.2, 6.0)
            tbm.booleanOperation(bolt, cyl(tbm, x, 0, 1.2, 7.2, 10.0), adsk.fusion.BooleanTypes.UnionBooleanType)
            add(root, "83800%d" % i, "HARDWARE - BOLT - M6 X %d ISO 4762 %s" % (L, tag), bolt)
            if blocked:
                add(root, "21193%d" % i, "WALL - TEST BLOCKING PLATE %s" % tag,
                    box(tbm, x - 30, -30, 27.2, x + 30, 30, 30.2))
        em = design.exportManager
        ok = em.execute(em.createSTEPExportOptions(ARGS["out"], root))
        print("export %s: %s" % (ARGS["out"], ok))
        if not ok:
            raise RuntimeError("STEP export failed")
    finally:
        doc.close(False)
