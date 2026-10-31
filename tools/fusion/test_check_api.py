#!/usr/bin/env python3
"""Tests for check_api.py.  python3 tools/fusion/test_check_api.py

The parsing and the completed definitions are tested on small made-up files.
The end-to-end check needs this Mac's Fusion install and mypy; run it with a
python that has mypy (it is skipped otherwise, and says so).
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_api as ca  # noqa: E402

WRAPPER = textwrap.dedent('''\
    class Drawing(adsk.core.Product):
        def _get_exportManager(self) -> "adsk.drawing.DrawingExportManager":
            return _drawing.Drawing__get_exportManager(self)

        def _get_sheets(self) -> "adsk.drawing.Sheets":
            r"""** This property is not officially supported and its behavior may change. **"""
            return _drawing.Drawing__get_sheets(self)

        def _get_name(self) -> "str":
            return _drawing.Drawing__get_name(self)

        def _set_name(self, value: "str") -> "void":
            return _drawing.Drawing__set_name(self, value)

        def tidy(self, how: "int") -> "bool":
            return _drawing.Drawing_tidy(self, how)

    # Register Drawing in _drawing:
    _drawing.Drawing_swigregister(Drawing)
    Drawing.exportManager = property(Drawing._get_exportManager, doc="")
    Drawing.sheets = property(Drawing._get_sheets, doc="not officially supported")
    Drawing.name = property(Drawing._get_name, Drawing._set_name, doc="")

    class ViewOrientationTypes(object):
        FrontViewOrientationType = _drawing.ViewOrientationTypes_FrontViewOrientationType
        BackViewOrientationType = _drawing.ViewOrientationTypes_BackViewOrientationType
''')

DEFS = textwrap.dedent('''\
    from __future__ import annotations
    from collections.abc import Iterator

    from . import core

    class Drawing(core.Product):
        def __init__(self):
            pass
        @property
        def exportManager(self) -> DrawingExportManager:
            return DrawingExportManager()

    class ViewOrientationTypes():
        def __init__(self):
            pass
        FrontViewOrientationType = 0
''')


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="check-api-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rel, text):
        p = os.path.join(self.tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def test_wrapper_members(self):
        w = ca.wrapper_members(self.write("drawing.py", WRAPPER))["Drawing"]
        self.assertEqual(w["props"]["sheets"], ("adsk.drawing.Sheets", False))
        self.assertEqual(w["props"]["name"], ("str", True))
        self.assertEqual(w["methods"], {"tidy": "bool"})
        consts = ca.wrapper_members(self.write("d2.py", WRAPPER))["ViewOrientationTypes"]["consts"]
        self.assertEqual(consts, {"FrontViewOrientationType", "BackViewOrientationType"})

    def test_completed_definitions_add_only_what_is_missing(self):
        install = os.path.join(self.tmp, "adsk")
        self.write("adsk/drawing.py", WRAPPER)
        self.write("adsk/defs/adsk/drawing.py", DEFS)
        self.write("adsk/defs/adsk/__init__.py", "")
        out = os.path.join(self.tmp, "out")
        os.makedirs(out)
        added = ca.complete_definitions(install, out)
        with open(os.path.join(out, "adsk", "drawing.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn('def sheets(self) -> "adsk.drawing.Sheets": ...', src)
        self.assertIn("@name.setter", src)
        self.assertIn("def tidy(*args: Any, **kwargs: Any) -> \"bool\": ...", src)
        self.assertIn("BackViewOrientationType: int = 0", src)
        self.assertEqual(src.count("def exportManager"), 1)     # already there: not added twice
        self.assertTrue(src.startswith("from __future__ import annotations\n"))
        self.assertEqual(added, 5)                              # sheets, name + setter, tidy, Back...
        compile(src, "drawing.py", "exec")


def have_mypy():
    return importlib.util.find_spec("mypy") is not None


@unittest.skipUnless(ca.find_install() and have_mypy(),
                     "needs this Mac's Fusion install and mypy (run with a python that has it)")
class EndToEndTests(unittest.TestCase):
    def check(self, source):
        d = tempfile.mkdtemp(prefix="check-api-e2e-")
        try:
            p = os.path.join(d, "script.py")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(textwrap.dedent(source))
            r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "check_api.py"),
                                "script.py"], cwd=d, capture_output=True, text=True, timeout=600)
            return r.returncode, r.stdout
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_real_names_pass_including_unofficial_ones(self):
        code, out = self.check('''\
            import adsk.core, adsk.drawing

            def run(_c):
                app = adsk.core.Application.get()
                doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
                sheet = doc.drawing.sheets.item(0)       # works, but not in the definitions
                inp = sheet.views.createBaseViewInput()
                inp.viewParameters.orientation = adsk.drawing.ViewOrientationTypes.FrontViewOrientationType
                print(sheet.views.add(inp).scaleValue)

            def extent(view: "adsk.drawing.View"):
                return view.viewCurves.count
            ''')
        self.assertEqual(code, 0, out)

    def test_wrong_names_and_arguments_fail(self):
        code, out = self.check('''\
            import adsk.core, adsk.drawing

            def run(_c):
                app = adsk.core.Application.get()
                doc = adsk.drawing.DrawingDocument.cast(app.activeDocument)
                sheet = doc.drawing.sheets.item(0)
                print(sheet.veiws.count)
                print(adsk.drawing.ViewOrientationTypes.FrontViewOrientationTyp)
                sheet.images.insert(1, 2, 3, 4, 5, 6, 7)

            def extent(view: "adsk.drawing.View"):
                return view.viewCurvs
            ''')
        self.assertEqual(code, 1, out)
        for what in ('"veiws"', '"FrontViewOrientationTyp"', 'Too many arguments for "insert"',
                     '"viewCurvs"'):
            self.assertIn(what, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
