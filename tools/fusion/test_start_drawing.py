#!/usr/bin/env python3
"""Offline tests for start_drawing.py: the dialog sequence against a fake Fusion.

    python3 tools/fusion/test_start_drawing.py

No Fusion, no accessibility, no screen: FakeFusion plays Fusion's command
states and its two dialogs as seen on Mac 1 on 2026-10-31 (Create Drawing
opens, OK makes the drawing after a few seconds, then Fusion opens Base View
by itself), plus the screen lock, accessibility and Fusion's own cancel.
"""

import json
import contextlib
import io
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_script as rs  # noqa: E402
import start_drawing as sd  # noqa: E402

FAST = {"dialog": 0.5, "drawing": 0.5, "base_view": 0.3, "idle": 0.3, "poll": 0.005}


class FakeFusion:
    def __init__(self, dialog_opens=True, ok_found=True, base_view=True, drawing_after=3,
                 base_view_after=4, start_cmd=sd.IDLE_CMD, unsaved=0, opened=False,
                 locked=False, ax_windows=3, modified=False, fusion_cancel_works=True,
                 mcp_dies_after_queue=False, ax_works=True, ax_sees_dialogs=True,
                 folder_bad=(), folder_others=(), drawing_exists=False, open_warning=""):
        self.opened = opened
        self.cmd = start_cmd
        self.unsaved = unsaved
        self.dialog_opens = dialog_opens
        self.ok_found = ok_found
        self.base_view = base_view
        self.drawing_after = drawing_after
        self.base_view_after = base_view_after
        self.locked = locked
        self.ax_windows = ax_windows
        self.modified = modified
        self.fusion_cancel_works = fusion_cancel_works
        self.mcp_dies_after_queue = mcp_dies_after_queue
        self.ax_works = ax_works
        self.ax_sees_dialogs = ax_sees_dialogs
        self.folder_bad = list(folder_bad)
        self.folder_others = list(folder_others)
        self.drawing_exists = drawing_exists
        self.open_warning = open_warning
        self.folder_checks = 0
        self.queued = False
        self.pending = []          # (polls left, action)
        self.ran, self.clicks, self.saved, self.cancels, self.closes = [], [], [], 0, []

    def _tick(self):
        nxt = []
        for left, action in self.pending:
            if left <= 1:
                action()
            else:
                nxt.append((left - 1, action))
        self.pending = nxt

    def _mcp(self):
        if self.mcp_dies_after_queue and self.queued:
            raise rs.McpError("cannot reach Fusion MCP (fake)")

    # -- MCP side
    def state(self):
        self._mcp()
        self._tick()
        return self.cmd, self.unsaved

    def run(self, source, read_only=False):
        self._mcp()
        if "ARGS = {" in source:
            mode = "close" if "'mode': 'close'" in source else "open"
            self.ran.append(mode)
            if mode == "close":
                self.closes.append(source)
                return True, "run_script: closed 'X'"
            return True, self.open_warning + ("run_script: opened 'X' (version 1)" if self.opened
                                              else "run_script: activated 'X'")
        if sd.CREATE_CMD in source and "execute()" in source:
            self.ran.append("queue")
            if self.modified:
                return False, "X has unsaved changes; save or close it first"
            self.queued = True
            if self.dialog_opens:
                self.pending.append((1, lambda: setattr(self, "cmd", sd.CREATE_CMD)))
            return True, "queued"
        if "saveAs" in source:
            self.ran.append("save")
            if self.cmd != sd.IDLE_CMD:
                return False, "Cannot perform 'script' while a command dialog is open"
            self.unsaved -= 1
            self.saved.append(source)
            return True, "saved"
        if "closed unsaved drawing" in source:
            self.ran.append("close-unsaved")
            self.unsaved = 0
            return True, ""
        raise AssertionError("unexpected script")

    def folder(self, project, subfolders, design, name):
        self._mcp()
        self.folder_checks += 1
        return ([str(b) for b in self.folder_bad], [str(o) for o in self.folder_others],
                True, self.drawing_exists)

    def fusion_cancel(self):
        self._mcp()
        self.cancels += 1
        if self.fusion_cancel_works and self.cmd in (sd.CREATE_CMD, sd.BASE_VIEW_CMD):
            self.cmd = sd.IDLE_CMD
        return True, "Fusion cancel: done"

    # -- accessibility and the Mac
    def session_locked(self):
        return self.locked

    def ax_window_count(self):
        return self.ax_windows

    def dialogs(self):
        if not self.ax_works:
            raise sd.StartError("accessibility call failed (fake)")
        self._tick()                  # Fusion's UI moves on even when MCP doesn't answer
        if not self.ax_sees_dialogs:
            return []
        return ["395x445"] if self.cmd in (sd.CREATE_CMD, sd.BASE_VIEW_CMD) else []

    def click(self, button, title):
        if not self.ax_works:
            raise sd.StartError("accessibility call failed (fake)")
        self.clicks.append(button)
        if self.cmd == sd.CREATE_CMD:
            if button == "OK" and self.ok_found:
                self.cmd = "busy"

                def made():
                    self.cmd = sd.IDLE_CMD
                    self.unsaved += 1
                    if self.base_view:
                        self.pending.append((self.base_view_after,
                                             lambda: setattr(self, "cmd", sd.BASE_VIEW_CMD)))
                self.pending.append((self.drawing_after, made))
                return "clicked by title"
            if button == "Cancel":
                self.cmd = sd.IDLE_CMD
                return "clicked by title"
            return "none"
        if self.cmd == sd.BASE_VIEW_CMD and button in ("OK", "Cancel"):
            self.cmd = sd.IDLE_CMD
            return "clicked by title"
        return "none"


class CleanupStub:
    """Fusion seen by cancel_dialogs alone: one state and one dialog list per poll."""
    def __init__(self, states, dialog_lists):
        self.states, self.lists = list(states), list(dialog_lists)
        self.clicks, self.cancels, self.log = [], 0, []

    def state(self):
        return (self.states.pop(0) if len(self.states) > 1 else self.states[0]), 0

    def dialogs(self):
        return self.lists.pop(0) if len(self.lists) > 1 else self.lists[0]

    def click(self, button, title):
        self.clicks.append(button)
        return "clicked by title"

    def fusion_cancel(self):
        self.cancels += 1
        return True, "Fusion cancel (Select queued)"


def go(fake, **kw):
    logs = []
    code = sd.run_with_cleanup(fake, "100000_P04_POD-SKELETON_CAD", "X_P01_TEST_DWG",
                               "Default Project/FocusPod v2", kw.get("sheet", "A2"), False,
                               logs.append, waits=FAST)
    return code, logs


class SequenceTests(unittest.TestCase):
    def test_happy_path_presses_ok_then_cancel_and_saves(self):
        f = FakeFusion()
        code, logs = go(f, sheet="A1")
        self.assertEqual(code, 0)
        self.assertEqual(f.ran, ["open", "queue", "save"])
        self.assertEqual(f.clicks, ["OK", "Cancel"])
        self.assertEqual((f.cmd, f.unsaved), (sd.IDLE_CMD, 0))
        self.assertIn("'A1' + \"ISOSheetSize\"", f.saved[0])
        self.assertIn("(841, 594)", f.saved[0])                 # read back and checked
        self.assertTrue(any("pressed Cancel in Base View" in m for m in logs))

    def test_a_failed_start_closes_the_design_it_opened_without_discarding(self):
        # Reviewer 5, P3 on #101: the cleanup closed the unsaved drawing but not the design
        f = FakeFusion(opened=True, ok_found=False)              # fails after the dialog was queued
        code, _logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual(f.ran, ["open", "queue", "close-unsaved", "close"])
        self.assertIn("'discard': False", f.closes[-1])          # unsaved changes are never dropped

    def test_a_start_refused_after_opening_closes_the_design_too(self):
        f = FakeFusion(opened=True, modified=True)               # the queue step refuses
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.ran, ["open", "queue", "close"])

    def test_a_design_that_was_already_open_is_left_open(self):
        f = FakeFusion(opened=False, ok_found=False)
        go(f)
        self.assertNotIn("close", f.ran)

    def test_a_design_opened_after_a_runner_warning_is_still_closed_again(self):
        # live 2026-10-31: the open step printed "1 entry ... could not be read;
        # skipped" first, and the design was left open
        f = FakeFusion(opened=True, open_warning="run_script: 1 entry of F could not be read (positions 40); skipped\n")
        self.assertEqual(go(f)[0], 0)
        self.assertEqual(f.ran, ["open", "queue", "save", "close"])

    def test_a_design_it_opened_is_closed_again(self):
        f = FakeFusion(opened=True)
        self.assertEqual(go(f)[0], 0)
        self.assertEqual(f.ran, ["open", "queue", "save", "close"])

    def test_no_base_view_dialog_still_saves(self):
        f = FakeFusion(base_view=False)
        code, logs = go(f)
        self.assertEqual(code, 0)
        self.assertEqual(f.clicks, ["OK"])
        self.assertTrue(any("no Base View dialog" in m for m in logs))

    # review P1: refuse before anything is opened
    def test_locked_screen_is_refused_before_anything_opens(self):
        f = FakeFusion(locked=True)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual((f.ran, f.clicks), ([], []))

    def test_no_accessibility_view_of_fusion_is_refused_before_anything_opens(self):
        f = FakeFusion(ax_windows=0)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual((f.ran, f.clicks), ([], []))

    def test_cleanup_presses_cancel_through_accessibility_first(self):
        # PM ruling 2026-10-31: ending an open Create Drawing by script killed Fusion
        f = FakeFusion(ok_found=False)                          # OK can't be pressed
        code, _logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertEqual(f.clicks, ["OK", "Cancel"])
        self.assertEqual(f.cancels, 0)                          # Fusion's own cancel never used

    def test_fusions_own_cancel_only_when_accessibility_sees_no_dialog(self):
        f = FakeFusion(ok_found=False)
        f.ax_sees_dialogs = False                               # the dialog is up, accessibility can't see it
        code, logs = go(f)
        self.assertEqual(code, 1)
        self.assertGreaterEqual(f.cancels, 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertTrue(any("Fusion's own cancel" in m for m in logs))

    def test_a_dialog_seen_late_gets_accessibility_cancel_not_fusions(self):
        st = CleanupStub([sd.CREATE_CMD, sd.CREATE_CMD, sd.IDLE_CMD], [[], ["395x445"], []])
        self.assertTrue(sd.cancel_dialogs(st, st.log.append, tries=4, poll_s=0))
        self.assertEqual((st.clicks, st.cancels), (["Cancel"], 0))

    def test_fusions_own_cancel_needs_two_polls_without_a_dialog(self):
        st = CleanupStub([sd.BASE_VIEW_CMD, sd.BASE_VIEW_CMD, sd.IDLE_CMD], [[], [], []])
        self.assertTrue(sd.cancel_dialogs(st, st.log.append, tries=4, poll_s=0))
        self.assertEqual((st.clicks, st.cancels), ([], 1))

    def test_busy_or_other_commands_are_never_cancelled(self):
        for cmd in ("busy", "SketchCreate"):
            st = CleanupStub([cmd] * 9, [[]] * 9)
            self.assertFalse(sd.cancel_dialogs(st, st.log.append, tries=6, poll_s=0))
            self.assertEqual((st.clicks, st.cancels), ([], 0), cmd)

    def test_closing_the_unsaved_drawing_survives_documents_closing_with_it(self):
        # live 2026-10-31: closing the drawing also closed a document Fusion had
        # opened for it, and the next index raised "Bad index parameter"
        class Doc:
            def __init__(self, name, drawing, saved, docs, takes=()):
                self.name, self.drawing, self.isSaved, self.docs, self.takes = name, drawing, saved, docs, takes
                self.objectType = "Drawing" if drawing else "Design"

            def close(self, _save):
                for d in (self,) + tuple(self.takes):
                    self.docs.remove(d)
                return True

        class Docs(list):
            @property
            def count(self):
                return len(self)

            def item(self, i):
                if not 0 <= i < len(self):
                    raise RuntimeError("3 : Bad index parameter")
                return self[i]

        docs = Docs()
        hidden = Doc("ref", False, True, docs)
        docs.extend([Doc("A_CAD", False, True, docs), hidden,
                     Doc("Untitled", True, False, docs, takes=(hidden,))])
        app = types.SimpleNamespace(documents=docs)
        adsk = types.ModuleType("adsk")
        adsk.doEvents = lambda: None
        adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app))
        adsk.drawing = types.SimpleNamespace(DrawingDocument=types.SimpleNamespace(classType=lambda: "Drawing"))
        saved = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing})
        try:
            ns = {}
            exec(compile(sd.CLOSE_UNSAVED_SCRIPT, "close_unsaved", "exec"), ns)
            ns["run"](None)
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        self.assertEqual([d.name for d in docs], ["A_CAD"])

    def test_the_fusion_cancel_script_does_not_terminate_the_command(self):
        self.assertNotIn("terminateActiveCommand(", sd.FUSION_CANCEL_SCRIPT)
        self.assertIn('itemById("SelectCommand").execute()', sd.FUSION_CANCEL_SCRIPT)

    # the folder guard (Reviewer 5 on #86)
    def test_unreadable_folder_entry_is_refused_before_anything_opens(self):
        f = FakeFusion(folder_bad=[7])
        code, logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual((f.ran, f.clicks), ([], []))

    def test_an_unreadable_entry_that_is_not_a_drawing_only_warns(self):
        # PM ruling 2026-10-31: one bad entry must not block every team
        f = FakeFusion(folder_others=["entry 4 (a .f3d file, name unreadable)"])
        code, logs = go(f)
        self.assertEqual(code, 0)
        self.assertTrue(any("warning" in m and "entry 4" in m for m in logs))

    def test_the_folder_check_is_the_shared_one(self):
        # the lister moved to fusion_folder.py (its own tests): one copy for every team
        self.assertTrue(sd.LIST_FOLDER.startswith(rs.FOLDER_HELPER_SRC))
        self.assertIn('safe_to_create(folder, %(name)r, "f2d")', sd.SAVE_SCRIPT)
        self.assertIn("read_folder(folder, stop_when=", sd.FOLDER_SCRIPT)

    def test_steps_folder_reads_the_result_line(self):
        st = sd.Steps.__new__(sd.Steps)                         # no MCP needed
        seen = []
        st.run = lambda src, read_only=False: (seen.append((src, read_only)) or True, (
            'note\nFOLDER_JSON={"unknown": ["entry 3 (kind unknown, name unreadable)"], '
            '"others": [], "has_design": true, "has_drawing": false}\n'))
        self.assertEqual(st.folder("P", ["F"], "D", "N"),
                         (["entry 3 (kind unknown, name unreadable)"], [], True, False))
        self.assertTrue(seen[0][1])                             # read-only
        self.assertIn("def read_folder", seen[0][0])                # the shared fusion_folder.py

    def test_an_existing_drawing_name_is_refused_before_anything_opens(self):
        f = FakeFusion(drawing_exists=True)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual((f.ran, f.clicks), ([], []))

    def test_dialog_left_open_exits_4(self):
        f = FakeFusion(ok_found=False, fusion_cancel_works=False, ax_sees_dialogs=False)
        f.click = lambda button, title: "none"                  # nothing can close it
        sd_cancel = sd.cancel_dialogs
        try:
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0: sd_cancel(steps, log, 2, 0.001)
            self.assertEqual(go(f)[0], 4)
        finally:
            sd.cancel_dialogs = sd_cancel

    # review P2s
    def test_modified_design_is_refused_and_nothing_is_queued(self):
        f = FakeFusion(modified=True)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.ran, ["open", "queue"])              # the queue step refused
        self.assertFalse(f.queued)
        self.assertEqual(f.clicks, [])

    def test_lost_mcp_after_the_queue_still_cancels_by_accessibility(self):
        f = FakeFusion(mcp_dies_after_queue=True)
        sd_cancel = sd.cancel_dialogs
        try:
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0: sd_cancel(steps, log, 2, 0.001)
            code, logs = go(f)
        finally:
            sd.cancel_dialogs = sd_cancel
        self.assertIn(code, (2, 4))
        self.assertIn("Cancel", f.clicks)                       # tried without MCP

    def test_sigterm_counts_as_a_failure_with_cleanup(self):
        old = (signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGHUP))
        try:
            sd.install_signal_handlers()
            with self.assertRaises(KeyboardInterrupt):
                signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        finally:
            signal.signal(signal.SIGTERM, old[0])
            signal.signal(signal.SIGHUP, old[1])
        f = FakeFusion(ok_found=False)
        orig = f.click

        hits = []

        def killed(button, title):
            res = orig(button, title)
            if not hits:                                         # the kill lands once, mid-run
                hits.append(button)
                raise KeyboardInterrupt                          # as the handler does
            return res
        f.click = killed
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)                     # cleaned up

    # earlier behaviour
    def test_dialog_that_never_opens_stops_before_any_click(self):
        f = FakeFusion(dialog_opens=False)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.clicks, [])

    def test_home_screen_with_no_document_counts_as_idle(self):
        f = FakeFusion(start_cmd="")                            # Fusion just restarted, no document
        self.assertEqual(go(f)[0], 0)
        self.assertEqual(f.ran, ["open", "queue", "save"])

    def test_busy_fusion_is_not_touched(self):
        f = FakeFusion(start_cmd="SketchCreate")
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.ran, [])

    def test_an_unsaved_drawing_already_open_stops_it(self):
        f = FakeFusion(unsaved=1)
        self.assertEqual(go(f)[0], 1)
        self.assertEqual(f.ran, [])

    def test_a_drawing_that_never_finishes_is_reported_as_a_person_job(self):
        f = FakeFusion(drawing_after=10 ** 6)                   # Fusion stays busy, no dialog to cancel
        sd_cancel = sd.cancel_dialogs
        try:
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0: sd_cancel(steps, log, 2, 0.001)
            code, _ = go(f)
        finally:
            sd.cancel_dialogs = sd_cancel
        self.assertEqual(code, 4)                               # never claims Fusion is idle
        self.assertEqual(f.cancels, 0)                          # never touched while busy

    @unittest.skipUnless(shutil.which("osacompile"), "osacompile is macOS only")
    def test_every_applescript_compiles(self):
        # Reviewer 5 / WALL, 2026-10-31: AX_CLICK used the reserved word "named" and
        # never compiled, which the offline fakes could not see.
        # found, not listed, so a new AppleScript can't be left out
        scripts = {k: v for k, v in vars(sd).items()
                   if isinstance(v, str) and 'tell application "' in v}
        self.assertGreaterEqual(set(scripts), {"AX_CLICK", "AX_DIALOGS", "AX_WINDOW_COUNT"})
        for label, src in sorted(scripts.items()):
            with tempfile.TemporaryDirectory() as d:
                p = subprocess.run(["osacompile", "-o", os.path.join(d, "x.scpt"), "-e", src],
                                   capture_output=True, text=True, timeout=60)
            self.assertEqual(p.returncode, 0, "%s: %s" % (label, p.stderr))

    def test_scripts_compile(self):
        for src in (sd.STATE_SCRIPT, sd.CLOSE_UNSAVED_SCRIPT, sd.FUSION_CANCEL_SCRIPT,
                    sd.QUEUE_SCRIPT % {"project": "P", "design": "D", "cmd": sd.CREATE_CMD},
                    sd.LIST_FOLDER + sd.FOLDER_SCRIPT % {"project": "P", "subfolders": ["F"],
                                                         "design": "D", "name": "N"},
                    sd.LIST_FOLDER + sd.SAVE_SCRIPT % {"project": "P", "subfolders": ["F"], "name": "N",
                                                       "sheet": "A2", "size": (594, 420), "close": True,
                                                       "desc": "d"}):
            compile(src, "fusion", "exec")

    def test_session_lock_reader_parses_ioreg(self):
        self.assertIn(sd.session_locked(), (True, False))


class SaveScriptTests(unittest.TestCase):
    """SAVE_SCRIPT itself, run against a fake Fusion API: the sheet-size read-back
    (Reviewer 5's live run, 2026-10-31: A2 read 420 x 420 just after setting it)."""

    def run_save(self, script, settle_after=2, final_value=None):
        events = {"n": 0}
        sizes = {"A2ISOSheetSize": (594.0, 420.0), "A3ISOSheetSize": (420.0, 297.0)}

        class Sheet:
            name = "Sheet1"
            views = types.SimpleNamespace(count=0)

            def __init__(self):
                self._value, self._wh, self._target, self._at = "A3ISOSheetSize", (420.0, 297.0), None, 0

            @property
            def sheetSize(self):
                return self._value

            @sheetSize.setter
            def sheetSize(self, v):
                self._value = final_value or v
                self._target = sizes[v]
                self._wh = (self._wh[0], sizes[v][1])         # half applied, as seen live
                self._at = events["n"] + settle_after

            def _now(self):
                if self._target and events["n"] >= self._at:
                    self._wh = self._target
                return self._wh

            @property
            def width(self):
                return self._now()[0]

            @property
            def height(self):
                return self._now()[1]

        sheet, saved = Sheet(), []
        doc = types.SimpleNamespace(
            isSaved=False, objectType="Drawing", activate=lambda: True,
            drawing=types.SimpleNamespace(sheets=types.SimpleNamespace(item=lambda i: sheet)),
            saveAs=lambda name, folder, desc, tag: saved.append(name) or True, close=lambda save: True)
        folder = types.SimpleNamespace(dataFiles=types.SimpleNamespace(count=0, item=None))
        folder.dataFolders = types.SimpleNamespace(itemByName=lambda n: folder)
        app = types.SimpleNamespace(
            documents=types.SimpleNamespace(count=1, item=lambda i: doc),
            data=types.SimpleNamespace(dataProjects=[types.SimpleNamespace(name="P", rootFolder=folder)]))
        adsk = types.ModuleType("adsk")
        adsk.doEvents = lambda: events.__setitem__("n", events["n"] + 1)
        adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app))
        adsk.drawing = types.SimpleNamespace(
            DrawingDocument=types.SimpleNamespace(classType=lambda: "Drawing", cast=lambda d: d),
            SheetSizes=types.SimpleNamespace(**{k: k for k in sizes}))
        src = sd.LIST_FOLDER + script % {"project": "P", "subfolders": ["F"], "name": "N", "sheet": "A2",
                                         "size": (594, 420), "close": True, "desc": "d"}
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing")}
        sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing})
        real_sleep, out = time.sleep, io.StringIO()
        time.sleep = lambda s: None
        try:
            ns = {}
            exec(compile(src, "save", "exec"), ns)
            with contextlib.redirect_stdout(out):
                ns["run"](None)
        finally:
            time.sleep = real_sleep
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        return saved, out.getvalue()

    def test_a_size_that_settles_after_a_moment_is_saved(self):
        saved, out = self.run_save(sd.SAVE_SCRIPT, settle_after=2)
        self.assertEqual(saved, ["N"])
        self.assertIn("after 2 look(s)", out)
        self.assertIn("SAVED_SHEET=Sheet1: 594 x 420 mm, size value A2ISOSheetSize", out)

    def test_a_wrong_size_value_is_refused(self):
        with self.assertRaises(RuntimeError) as cm:
            self.run_save(sd.SAVE_SCRIPT, settle_after=0, final_value="A3ISOSheetSize")
        self.assertIn("isn't A2", str(cm.exception))

    def test_a_size_that_never_settles_is_refused_after_ten_looks(self):
        with self.assertRaises(RuntimeError) as cm:
            self.run_save(sd.SAVE_SCRIPT, settle_after=10 ** 6)
        self.assertIn("after 10 looks", str(cm.exception))
        self.assertIn("420 x 420", str(cm.exception))


class CommandLineTests(unittest.TestCase):
    def test_busy_lock_exits_3_without_touching_fusion(self):
        tmp = tempfile.mkdtemp(prefix="startdwg-test-")
        lockdir = os.path.join(tmp, "fusion.lock")
        os.mkdir(lockdir)
        with open(os.path.join(lockdir, rs.OWNER_FILE), "w") as fh:
            json.dump({"token": "t", "label": "WALL engineer", "pid": os.getpid(),
                       "since": time.time(), "expires": time.time() + 60}, fh)
        p = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "D", "N",
                            "--lock", lockdir, "--lock-wait", "0.3", "--url", "http://127.0.0.1:9/mcp"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 3)
        self.assertIn("WALL engineer", p.stderr)

    def test_it_runs_inside_a_held_lock_with_its_token_and_leaves_the_hold(self):
        tmp = tempfile.mkdtemp(prefix="startdwg-test-")
        lockdir = os.path.join(tmp, "fusion.lock")
        hold = rs.FusionLock(lockdir, label="held for a live test", pid=None, hold_s=60, log=lambda m: None)
        hold.acquire(1)
        env = dict(os.environ, **{rs.TOKEN_ENV: hold.token})
        p = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "D", "N",
                            "--lock", lockdir, "--lock-wait", "0.3", "--url", "http://127.0.0.1:9/mcp",
                            "--timeout", "2"], capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(p.returncode, 2, p.stderr)              # got past the lock to Fusion
        self.assertEqual(hold.read_owner()["token"], hold.token)  # the hold is still there
        self.assertTrue(hold.release_held(hold.token))

    def test_unreachable_fusion_exits_2_and_gives_the_lock_back(self):
        tmp = tempfile.mkdtemp(prefix="startdwg-test-")
        lockdir = os.path.join(tmp, "fusion.lock")
        p = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "D", "N",
                            "--lock", lockdir, "--url", "http://127.0.0.1:9/mcp", "--timeout", "2"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(os.path.exists(lockdir))

    def test_bad_sheet_is_refused(self):
        p = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "D", "N",
                            "--sheet", "B"], capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
