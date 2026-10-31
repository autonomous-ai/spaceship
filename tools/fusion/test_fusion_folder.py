#!/usr/bin/env python3
"""Offline tests for fusion_folder.py, the shared safe-to-create check.

    python3 tools/fusion/test_fusion_folder.py
"""

import base64
import contextlib
import io
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
                                           stop_when=lambda fs, u, o: "A_CAD" in fs)
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

    def test_a_warn_only_entry_does_not_hold_fusion(self):
        # Reviewer 5, P3 on #121: an unreadable .f2d can't be a new design, so no minute of waiting
        warnings, c = check(Folder([File("A_CAD", "f3d"), File(None, "f2d")]), "NEW_CAD", "f3d")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(c.sleeps, [])

    def test_it_still_waits_while_an_unread_entry_could_be_the_new_file(self):
        c = Clock()
        with self.assertRaises(RuntimeError):
            ff.safe_to_create(Folder([File(None, "f2d"), "boom"]), "NEW_CAD", "f3d", sleep=c.sleep, now=c.now)
        self.assertEqual(sum(c.sleeps), 60.0)                   # the unknown entry is waited for

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

    def test_the_drawing_starts_folder_look_stops_once_nothing_unread_could_be_the_drawing(self):
        import start_drawing as sd
        self.assertIn('not could_be(u, o, "f2d")', sd.FOLDER_SCRIPT)
        self.assertIn('safe_to_create(folder, %(name)r, "f2d")', sd.SAVE_SCRIPT)   # stops the same way

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

    def run_doc(self, items, create, heal_after=None, wait=False, open_fails=0):
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
        fails = [open_fails]

        def open_doc(f, v):
            if fails[0]:
                fails[0] -= 1
                raise RuntimeError("1 : Missing key for PIMOpenWorkflowTracker")
            opened.append(f.name)
            return Doc(f.name)

        docs = types.SimpleNamespace(count=0, item=None, open=open_doc, add=lambda t: Doc("new"))
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
        if not wait:
            src = src.replace("WAIT_S = 60.0", "WAIT_S = 0.0")    # no real waiting in a test
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

    def test_a_new_design_does_not_wait_on_a_warn_only_entry(self):
        # Reviewer 5, P3 on #121: with the real one-minute wait left on, an unreadable
        # .f2d must not hold Fusion
        import time
        t0 = time.monotonic()
        opened, made = self.run_doc([File("A_CAD", "f3d"), File(None, "f2d")], create=True, wait=True)
        self.assertEqual(made, ["NEW_CAD"])
        self.assertLess(time.monotonic() - t0, 2.0)

    def test_a_design_saved_a_moment_ago_is_opened_on_a_second_try(self):
        # live 2026-10-31: opening a design 4 s after its save raised "Missing key for PIMOpenWorkflowTracker"
        import time as _time
        real_sleep, waits = _time.sleep, []
        _time.sleep = lambda s: waits.append(s)
        try:
            opened, made = self.run_doc([File("NEW_CAD", "f3d")], create=False, open_fails=2)
        finally:
            _time.sleep = real_sleep
        self.assertEqual((opened, made, waits), (["NEW_CAD"], [], [10, 10]))

    def test_each_new_try_opens_a_fresh_reference(self):
        # live 2026-10-31 (#140 batch test): the same reference kept failing for a full
        # minute; a reference looked up again opens
        import time as _time
        handed = []

        class FreshFile(File):
            latestVersion = None                             # the fake has no version history

        class FreshFiles(Files):
            def item(self, i):
                f = FreshFile("NEW_CAD", "f3d")              # a new reference on every look
                handed.append(f)
                return f

        folder = types.SimpleNamespace(dataFiles=FreshFiles([None]))
        stale = []

        def open_doc(f, v):
            if f is handed[0]:                               # the first reference never opens
                stale.append(f)
                raise RuntimeError("1 : Missing key for PIMOpenWorkflowTracker")
            return types.SimpleNamespace(name=f.name, activate=lambda: True)

        real_sleep = _time.sleep
        _time.sleep = lambda s: None
        try:
            opened = self.run_open_with(folder, open_doc)
        finally:
            _time.sleep = real_sleep
        self.assertEqual((len(stale), opened), (1, "NEW_CAD"))  # one failure, then the fresh one opened

    def test_a_look_up_that_fails_keeps_the_old_reference(self):
        # PM, on #167: if reading the folder again fails, the tries go on with the
        # reference from before instead of ending early
        import time as _time

        class FlakyFiles(Files):
            looks = 0

            @property
            def count(self):
                self.looks += 1
                if self.looks > 1:                           # every look after the first fails
                    raise RuntimeError("3 : InternalValidationError : the folder can't be read")
                return len(self.items)

        first = File("NEW_CAD", "f3d")
        folder = types.SimpleNamespace(dataFiles=FlakyFiles([first]))
        tries = []

        def open_doc(f, v):
            tries.append(f)
            if len(tries) < 3:
                raise RuntimeError("1 : Missing key for PIMOpenWorkflowTracker")
            return types.SimpleNamespace(name=f.name, activate=lambda: True)

        real_sleep = _time.sleep
        _time.sleep = lambda s: None
        try:
            opened = self.run_open_with(folder, open_doc)
        finally:
            _time.sleep = real_sleep
        self.assertEqual(opened, "NEW_CAD")
        self.assertEqual(tries, [first, first, first])        # the old reference, tried again
        self.assertEqual(folder.dataFiles.looks, 3)           # it did look again, twice

    def run_open_with(self, folder, open_doc):
        """The --doc open step against a fake Fusion with this folder and open()."""
        folder.dataFolders = types.SimpleNamespace(itemByName=lambda n: None)
        proj = types.SimpleNamespace(name="Default Project", rootFolder=folder)
        app = types.SimpleNamespace(
            documents=types.SimpleNamespace(count=0, item=None, open=open_doc),
            data=types.SimpleNamespace(dataProjects=types.SimpleNamespace(count=1, item=lambda i: proj),
                                       activeProject=None))
        adsk = types.ModuleType("adsk")
        adsk.doEvents = lambda: None
        adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app))
        adsk.fusion = types.SimpleNamespace()
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.fusion": adsk.fusion})
        out = io.StringIO()
        try:
            ns = {}
            exec(compile(rs.doc_script("open", "NEW_CAD", "Default Project"), "doc_step", "exec"), ns)
            with contextlib.redirect_stdout(out):
                ns["run"](None)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        return "NEW_CAD" if "opened 'NEW_CAD'" in out.getvalue() else out.getvalue()

    def test_a_design_that_is_there_opens_despite_an_unreadable_entry(self):
        opened, made = self.run_doc([File("NEW_CAD", "f3d"), "boom"], create=True)
        self.assertEqual((opened, made), (["NEW_CAD"], []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
