#!/usr/bin/env python3
"""Offline test of export_design.py's in-Fusion script, against a fake Fusion API in
which a closed document's objects are gone, as in Fusion (live run 2026-10-31:
"An API Object refers to a deleted Object" after the reopened .f3d was closed).

    python3 tools/fusion/test_export_design.py
"""

import os
import shutil
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import export_design as ed  # noqa: E402


class Gone(RuntimeError):
    pass


class Doc:
    """A document whose objects raise once it is closed."""

    def __init__(self, name, box, items=3):
        self.name, self.closed, self.isSaved, self.isModified = name, False, True, False
        doc = self

        class Live:
            def __getattribute__(self, attr):
                if object.__getattribute__(doc, "closed") and not attr.startswith("__"):
                    raise Gone("4 : An API Object refers to a deleted Object")
                return object.__getattribute__(self, attr)

        def pt(x, y, z):
            p = Live()
            p.x, p.y, p.z = x, y, z
            return p

        body = Live()
        body.boundingBox = Live()
        body.boundingBox.minPoint, body.boundingBox.maxPoint = pt(*box[:3]), pt(*box[3:])
        comp = Live()
        comp.bRepBodies = [body]
        comp.features = Live()
        derive = Live()
        derive.documentReference = types.SimpleNamespace(dataFile=types.SimpleNamespace(name="SKEL", versionNumber=4))
        derive.breakLink = lambda: True
        comp.features.deriveFeatures = [derive]
        comp.partNumber = "100000-SEC-AA"
        item = Live()
        item.name, item.healthState = "Extrude1", "healthy"
        timeline = Live()
        timeline.count = items
        timeline.item = lambda i: item
        self.design = Live()
        self.design.rootComponent = comp
        self.design.allComponents = [comp]
        self.design.timeline = timeline
        self.design.exportManager = types.SimpleNamespace(
            createFusionArchiveExportOptions=lambda path, root: path,
            createSTEPExportOptions=lambda path, root: path,
            execute=lambda path: (open(path, "wb").write(b"x" * 2000) and True))
        self.products = types.SimpleNamespace(itemByProductType=lambda t: self.design)

    def close(self, save):
        self.closed = True
        return True

    def activate(self):
        return True


class ExportScriptTests(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="export-design-test-")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def run_script(self):
        box = (-37.35, -85.0, 0.0, 125.0, 85.0, 240.0)       # cm, as Fusion reports
        doc = Doc("100000_P04_POD-SECTION-AA_CAD", box)
        copies = []

        def import_new(opts):
            c = Doc("copy", box)
            copies.append(c)
            return c

        app = types.SimpleNamespace(activeDocument=doc, importManager=types.SimpleNamespace(
            createSTEPImportOptions=lambda p: p, createFusionArchiveImportOptions=lambda p: p,
            importToNewDocument=import_new))
        adsk = types.ModuleType("adsk")
        adsk.doEvents = lambda: None
        adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app))
        adsk.fusion = types.SimpleNamespace(
            Design=types.SimpleNamespace(cast=lambda d: d),
            FeatureHealthStates=types.SimpleNamespace(HealthyFeatureHealthState="healthy"))
        src = ed.EXPORT_SCRIPT % {"args": {"name": doc.name, "pn": "100000-SEC-AA", "repo": self.repo,
                                           "f3d_dir": "f3d", "step_dir": "step", "f3d_check": True},
                                  "sentinel": ed.SENTINEL}
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.fusion": adsk.fusion})
        try:
            ns = {}
            exec(compile(src, "export_design", "exec"), ns)
            ns["run"](None)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        return copies

    def test_the_script_ends_with_the_planned_rollback_not_a_deleted_object(self):
        with self.assertRaises(RuntimeError) as cm:
            self.run_script()
        self.assertEqual(str(cm.exception), ed.SENTINEL)        # exported, checked, links rolled back
        self.assertTrue(os.path.exists(os.path.join(self.repo, "f3d", "100000_P04_POD-SECTION-AA_CAD.f3d")))
        self.assertTrue(os.path.exists(os.path.join(self.repo, "step", "100000_P04_POD-SECTION-AA_STEP.step")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
