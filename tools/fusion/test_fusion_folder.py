#!/usr/bin/env python3
"""Offline tests for fusion_folder.py, the shared safe-to-create check.

    python3 tools/fusion/test_fusion_folder.py
"""

import base64
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fusion_folder as ff  # noqa: E402
import run_script as rs  # noqa: E402


class Unreadable(Exception):
    pass


class File:
    versionNumber = 1

    def __init__(self, name=None, ext=None):
        self._n, self._e = name, ext

    @property
    def name(self):
        if self._n is None:
            raise Unreadable("name")
        return self._n

    @property
    def fileExtension(self):
        if self._e is None:
            raise Unreadable("extension")
        return self._e


class Files:
    """item(i) raises for "boom" entries until `heal_after` reads of the folder."""

    def __init__(self, items, heal_after=None):
        self.items, self.reads, self.heal_after = items, 0, heal_after

    @property
    def count(self):
        self.reads += 1                    # one count per pass over the folder
        return len(self.items)

    def item(self, i):
        it = self.items[i]
        if it == "boom":
            if self.heal_after is not None and self.reads > self.heal_after:
                return File("HEALED_CAD", "f3d")
            raise Unreadable("3 : InternalValidationError : invalid argument index")
        return it


class Folder:
    def __init__(self, items, heal_after=None):
        self.dataFiles = Files(items, heal_after)


class Clock:
    def __init__(self):
        self.t, self.sleeps = 0.0, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def check(folder, name, ext="f3d", wait=60.0):
    c = Clock()
    return ff.safe_to_create(folder, name, ext, wait_s=wait, pause_s=5.0, sleep=c.sleep, now=c.now), c


class ReadFolderTests(unittest.TestCase):
    def test_a_clean_folder_is_read_once(self):
        c = Clock()
        files, unknown, others = ff.read_folder(Folder([File("A_CAD", "f3d"), File("B_DWG", "f2d")]),
                                                sleep=c.sleep, now=c.now)
        self.assertEqual(sorted(files), ["A_CAD", "B_DWG"])
        self.assertEqual((unknown, others, c.sleeps), ([], {}, []))

    def test_a_flickering_entry_is_read_again_until_it_heals(self):
        c = Clock()
        folder = Folder([File("A_CAD", "f3d"), "boom"], heal_after=3)
        files, unknown, others = ff.read_folder(folder, sleep=c.sleep, now=c.now)
        self.assertEqual(sorted(files), ["A_CAD", "HEALED_CAD"])
        self.assertEqual(unknown, [])
        self.assertEqual(len(c.sleeps), 3)                      # read 4 times, 5 s apart

    def test_it_gives_up_after_a_minute(self):
        c = Clock()
        files, unknown, _ = ff.read_folder(Folder(["boom"]), sleep=c.sleep, now=c.now)
        self.assertEqual(sum(c.sleeps), 60.0)                   # PM ruling: up to a minute
        self.assertIn("invalid argument index", unknown[0])

    def test_kinds_of_unreadable_entries(self):
        c = Clock()
        files, unknown, others = ff.read_folder(
            Folder([File(None, "f2d"), File(None, "f3d"), File(None, None), "boom"]), wait_s=0,
            sleep=c.sleep, now=c.now)
        self.assertEqual(files, {})
        self.assertEqual([u.split(" (")[0] for u in unknown], ["entry 2", "entry 3"])
        self.assertEqual({k: [t.split(" (")[0] for t in v] for k, v in others.items()},
                         {"f2d": ["entry 0"], "f3d": ["entry 1"]})

    def test_an_open_step_stops_as_soon_as_its_file_is_there(self):
        c = Clock()
        files, unknown, _ = ff.read_folder(Folder([File("A_CAD", "f3d"), "boom"]), sleep=c.sleep, now=c.now,
                                           stop_when=lambda fs: "A_CAD" in fs)
        self.assertIn("A_CAD", files)
        self.assertEqual(c.sleeps, [])                          # no waiting for the broken entry


class SafeToCreateTests(unittest.TestCase):
    def test_a_free_name_in_a_clean_folder(self):
        warnings, c = check(Folder([File("A_CAD", "f3d")]), "NEW_CAD")
        self.assertEqual((warnings, c.sleeps), ([], []))

    def test_a_name_that_is_there_is_refused(self):
        with self.assertRaises(RuntimeError) as cm:
            check(Folder([File("NEW_CAD", "f3d")]), "NEW_CAD")
        self.assertIn("already in the folder", str(cm.exception))

    def test_an_entry_that_stays_unreadable_is_refused(self):
        with self.assertRaises(RuntimeError) as cm:
            check(Folder([File("A_CAD", "f3d"), "boom"]), "NEW_CAD")
        self.assertIn("could be NEW_CAD", str(cm.exception))

    def test_a_flicker_that_heals_within_the_minute_is_not_refused(self):
        # ELECTRICAL's stop, 2026-10-31: one entry was briefly unreadable
        warnings, c = check(Folder([File("A_CAD", "f3d"), "boom"], heal_after=2), "NEW_CAD")
        self.assertEqual(warnings, [])
        self.assertLess(sum(c.sleeps), 60.0)

    def test_an_unreadable_entry_of_another_kind_only_warns(self):
        warnings, _ = check(Folder([File("A_CAD", "f3d"), File(None, "f2d")]), "NEW_CAD", "f3d")
        self.assertEqual(len(warnings), 1)
        self.assertIn("isn't a .f3d", warnings[0])

    def test_the_same_kind_is_refused(self):
        with self.assertRaises(RuntimeError):
            check(Folder([File(None, "f2d")]), "NEW_DWG", "f2d")


class SharedCopyTests(unittest.TestCase):
    """The runner gives every script this module, and puts it in front of its own steps."""

    def test_every_script_run_through_the_runner_can_import_it(self):
        script = ("from fusion_folder import safe_to_create, read_folder\n"
                  "def run(_c):\n    RESULT.append((safe_to_create.__name__, read_folder.__module__))\n")
        wrapped = rs.wrap_script(script, "/x/team_script.py", {})
        result = []
        ns = {}
        keep = sys.modules.get("fusion_folder")
        try:
            exec(compile(wrapped, "wrapper", "exec"), ns)
            ns["_NS"]["RESULT"] = result
            ns["run"](None)
        finally:
            if keep is not None:
                sys.modules["fusion_folder"] = keep
        self.assertEqual(result, [("safe_to_create", "fusion_folder")])

    def test_the_runner_and_the_drawing_start_send_this_same_text(self):
        import start_drawing as sd
        with open(os.path.join(HERE, "fusion_folder.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertEqual(rs.FOLDER_HELPER_SRC, src)
        self.assertTrue(sd.LIST_FOLDER.startswith(src))
        self.assertTrue(rs.doc_script("open", "N", create=True).startswith(src))
        self.assertIn(base64.b64encode(src.encode("utf-8")).decode("ascii"), rs.wrap_script("def run(c): pass", "/x.py", {}))


class DocStepTests(unittest.TestCase):
    """The runner's --doc step itself, against a fake Fusion API."""

    def run_doc(self, items, create, heal_after=None):
        folder = Folder(items, heal_after)
        folder.dataFolders = types.SimpleNamespace(itemByName=lambda n: None)
        opened, made = [], []

        class Doc:
            def __init__(self, name):
                self.name = name

            def activate(self):
                return True

            def saveAs(self, name, f, desc, tag):
                made.append(name)
                return True

        proj = types.SimpleNamespace(name="Default Project", rootFolder=folder)
        projects = types.SimpleNamespace(count=1, item=lambda i: proj)
        docs = types.SimpleNamespace(count=0, item=None, open=lambda f, v: opened.append(f.name) or Doc(f.name),
                                     add=lambda t: Doc("new"))
        app = types.SimpleNamespace(documents=docs, data=types.SimpleNamespace(dataProjects=projects,
                                                                               activeProject=None))
        design = types.SimpleNamespace(designType=None, fusionUnitsManager=types.SimpleNamespace())
        adsk = types.ModuleType("adsk")
        adsk.doEvents = lambda: None
        adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app),
                                          DocumentTypes=types.SimpleNamespace(FusionDesignDocumentType=0))
        adsk.fusion = types.SimpleNamespace(Design=types.SimpleNamespace(cast=lambda p: design),
                                            DesignTypes=types.SimpleNamespace(ParametricDesignType=0),
                                            DistanceUnits=types.SimpleNamespace(MillimeterDistanceUnits=0))
        Doc.products = types.SimpleNamespace(itemByProductType=lambda t: None)
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.fusion": adsk.fusion})
        src = rs.doc_script("open", "NEW_CAD", "Default Project", create=create)
        src = src.replace("WAIT_S = 60.0", "WAIT_S = 0.0")        # no real waiting in a test
        try:
            ns = {}
            exec(compile(src, "doc_step", "exec"), ns)
            ns["run"](None)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        return opened, made

    def test_a_new_design_is_refused_while_an_entry_that_could_be_it_stays_unreadable(self):
        with self.assertRaises(RuntimeError) as cm:
            self.run_doc([File("A_CAD", "f3d"), "boom"], create=True)
        self.assertIn("could be it", str(cm.exception))

    def test_a_new_design_is_made_when_the_only_unreadable_entry_is_a_drawing(self):
        opened, made = self.run_doc([File("A_CAD", "f3d"), File(None, "f2d")], create=True)
        self.assertEqual((opened, made), ([], ["NEW_CAD"]))

    def test_a_design_that_is_there_opens_despite_an_unreadable_entry(self):
        opened, made = self.run_doc([File("NEW_CAD", "f3d"), "boom"], create=True)
        self.assertEqual((opened, made), (["NEW_CAD"], []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
