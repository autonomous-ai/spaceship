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

FAST = {"dialog": 0.5, "drawing": 0.5, "base_view": 0.3, "idle": 0.3, "poll": 0.005, "press": 0.05}


class FakeFusion:
    def __init__(self, dialog_opens=True, ok_found=True, base_view=True, drawing_after=3,
                 base_view_after=4, start_cmd=sd.IDLE_CMD, unsaved=0, opened=False,
                 locked=False, ax_windows=3, modified=False, fusion_cancel_works=True,
                 mcp_dies_after_queue=False, ax_works=True, ax_sees_dialogs=True,
                 folder_bad=(), folder_others=(), drawing_exists=False, open_warning="",
                 ax_late=0, ax_errors=0, ax_error_after_click=False, late_swaps_to_base_view=False):
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
        self.ax_late = ax_late                    # clicks that find no dialog yet (it isn't in accessibility)
        self.ax_errors = ax_errors                # clicks that fail as the dialog settles ("Invalid index")
        self.ax_error_after_click = ax_error_after_click   # a press that works but reports an error
        self.late_swaps_to_base_view = late_swaps_to_base_view
        self.click_log = []                       # (button, Fusion's command at the click)
        self.click_titles = []                    # (button, the dialog title it was asked to press in)
        self.ok_raises = None                     # an exception every OK press raises (a timed-out call)
        self.mcp_dies_after_ok = False            # MCP lost once OK is pressed
        self.ok_done = False
        self.close_out = "DESIGN_CLOSED: every open copy of X"   # what the design close prints
        self.queue_src = ""

    def _tick(self):
        nxt = []
        for left, action in self.pending:
            if left <= 1:
                action()
            else:
                nxt.append((left - 1, action))
        self.pending = nxt

    def _mcp(self):
        if (self.mcp_dies_after_queue and self.queued) or (self.mcp_dies_after_ok and self.ok_done):
            raise rs.McpError("cannot reach Fusion MCP (fake)")

    # -- MCP side
    def state(self):
        self._mcp()
        self._tick()
        return self.cmd, self.unsaved

    def run(self, source, read_only=False):
        self._mcp()
        if "NAME, KEY, STATE =" in source:        # the design close (CLOSE_DESIGN_SCRIPT)
            self.ran.append("close")
            self.closes.append(source)
            return True, self.close_out
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
            self.queue_src = source
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
        self.click_log.append((button, self.cmd))
        self.click_titles.append((button, title))
        if button == "OK" and self.ok_raises is not None:
            raise self.ok_raises
        dialog = self.cmd in (sd.CREATE_CMD, sd.BASE_VIEW_CMD)
        if dialog and self.ax_late:
            self.ax_late -= 1
            if self.late_swaps_to_base_view:      # meanwhile Fusion moves on to another dialog
                self.cmd = sd.BASE_VIEW_CMD
            return "none"
        if dialog and self.ax_errors:
            self.ax_errors -= 1
            raise sd.StartError("accessibility call failed: Can't get button 1 ... Invalid index. (-1719)")
        how = self._press(button)
        if self.ax_error_after_click and how.startswith("clicked"):
            self.ax_error_after_click = False
            raise sd.StartError("accessibility call failed: Can't get button 1 ... Invalid index. (-1719)")
        return how

    def _press(self, button):
        if self.cmd == sd.CREATE_CMD:
            if button == "OK" and self.ok_found:
                self.ok_done = True
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
        self.assertNotIn("close(True)", f.closes[-1])            # unsaved changes are never dropped
        self.assertIn("nothing closed", f.closes[-1])            # (DesignCloseTests runs that script)

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

    # 2026-11-01 06:36 and 07:06: Fusion reported the dialog's command before the dialog showed up to
    # accessibility, and a press found "none" or hit "Invalid index"; the cleanup found it a second later
    def test_a_dialog_not_yet_visible_to_accessibility_is_pressed_on_a_retry(self):
        f = FakeFusion(ax_late=3)                               # OK finds no dialog three times
        code, logs = go(f)
        self.assertEqual(code, 0, logs)
        self.assertEqual(f.clicks[:4], ["OK"] * 4)
        self.assertEqual(len(f.saved), 1)

    def test_base_views_cancel_not_yet_visible_is_pressed_on_a_retry(self):
        f = FakeFusion()
        real = f.click

        def click(button, title):                              # the Base View dialog shows up late
            if button == "Cancel" and f.cmd == sd.BASE_VIEW_CMD and f.clicks.count("Cancel") < 2:
                f.clicks.append(button)
                return "none"
            return real(button, title)
        f.click = click
        code, logs = go(f)
        self.assertEqual(code, 0, logs)
        self.assertEqual(f.clicks.count("Cancel"), 3)
        self.assertEqual(len(f.saved), 1)

    def test_an_accessibility_error_while_the_dialog_settles_is_tried_again(self):
        code, logs = go(FakeFusion(ax_errors=2))
        self.assertEqual(code, 0, logs)

    def test_a_press_that_worked_but_reported_an_error_goes_on(self):
        # the click went through, then accessibility lost the button: Fusion has left the dialog, so the
        # checks after the press decide (a new drawing is there)
        f = FakeFusion(ax_error_after_click=True)
        code, logs = go(f)
        self.assertEqual(code, 0, logs)
        self.assertEqual(f.clicks.count("OK"), 1)               # not pressed again
        self.assertEqual(len(f.saved), 1)

    def test_a_retry_never_presses_in_another_dialog(self):
        # while OK is retried, Fusion moves on to Base View: the retry stops; OK is never sent to Base View
        f = FakeFusion(ax_late=1, late_swaps_to_base_view=True)
        code, _logs = go(f)
        self.assertEqual(code, 1)                               # no new drawing after that: the start fails
        self.assertNotIn(("OK", sd.BASE_VIEW_CMD), f.click_log)
        self.assertEqual(f.cmd, sd.IDLE_CMD)                    # and the cleanup got Fusion idle

    def test_a_dialog_never_seen_fails_after_the_press_time(self):
        # accessibility never finds the dialog: the press gives up after its time, and as the cleanup's Cancel
        # can't find it either, the start reports a dialog left open for a person (exit 4), as before
        f = FakeFusion(ax_late=10 ** 6)
        code, logs = go(f)
        self.assertEqual(code, 4, logs)
        self.assertGreater(f.clicks.count("OK"), 1)
        self.assertEqual(len(f.saved), 0)

    # 2026-11-01 07:41: CEILING's OK press hit the 30 s accessibility timeout; the start tool didn't catch
    # it, so its cleanup never ran and the Create Drawing dialog stayed open for every later run
    def test_an_accessibility_timeout_is_a_start_error(self):
        def timed_out(*_a, **_k):
            raise subprocess.TimeoutExpired("osascript", 30)
        with self.assertRaises(sd.StartError) as cm:
            sd.Steps.osa(sd.AX_CLICK, "OK", "Create Drawing", run=timed_out)
        self.assertIn("timed out", str(cm.exception))

    def test_a_timed_out_ok_press_still_cleans_up(self):
        f = FakeFusion()
        f.ok_raises = sd.StartError("accessibility call timed out after 30 s")
        code, logs = go(f)
        self.assertEqual(code, 1, logs)
        self.assertEqual(f.cmd, sd.IDLE_CMD)                      # the dialog was cancelled
        self.assertEqual(f.click_titles[-1], ("Cancel", "Create Drawing"))   # in that exact dialog
        self.assertEqual(f.cancels, 0)                            # through accessibility, not Fusion's own
        self.assertEqual(len(f.saved), 0)

    def test_an_unexpected_error_still_cleans_up(self):
        # any error that escapes the steps (here the raw timeout, as before the fix) gets the cleanup too
        f = FakeFusion()
        f.ok_raises = subprocess.TimeoutExpired("osascript", 30)
        code, logs = go(f)
        self.assertEqual(code, 1, logs)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertEqual(f.click_titles[-1], ("Cancel", "Create Drawing"))

    def test_with_fusion_unreadable_before_ok_the_cleanup_asks_for_create_drawing(self):
        # MCP lost once Create Drawing is queued: Fusion can't name its command, so the cleanup asks for the
        # dialog the start was at, Create Drawing (Reviewer 5, P3 on #301: assert the exact title)
        f = FakeFusion(mcp_dies_after_queue=True)
        go(f)
        cancels = [t for b, t in f.click_titles if b == "Cancel"]
        self.assertTrue(cancels)
        self.assertEqual(set(cancels), {"Create Drawing"})

    def test_with_fusion_unreadable_after_ok_the_cleanup_asks_for_base_view(self):
        f = FakeFusion(drawing_after=1, base_view_after=1)      # Base View opens while the cleanup looks
        f.mcp_dies_after_ok = True
        code, logs = go(f)
        cancels = [t for b, t in f.click_titles if b == "Cancel"]
        self.assertTrue(cancels, logs)
        self.assertEqual(set(cancels), {"Base View"})
        self.assertEqual(f.cmd, sd.IDLE_CMD)                    # the Base View dialog was cancelled

    def test_a_dialog_while_fusion_is_idle_or_elsewhere_is_never_pressed(self):
        # Reviewer 5, P2 on #301: with Fusion idle and someone's Preferences dialog open, the cleanup pressed
        # Cancel in it. Now it presses nothing, and the start ends with exit 4 for a person to look
        for cmd in (sd.IDLE_CMD, "SketchCreate"):
            st = CleanupStub([cmd] * 9, [["600x400"]] * 9)
            self.assertFalse(sd.cancel_dialogs(st, st.log.append, tries=4, poll_s=0, expect=sd.BASE_VIEW_CMD))
            self.assertEqual((st.clicks, st.cancels), ([], 0), cmd)
            self.assertTrue(any("nothing pressed" in m for m in st.log), cmd)
        f = FakeFusion(ok_found=False)
        real_dialogs = f.dialogs

        def dialogs():                                          # a foreign dialog stays after ours is gone
            return real_dialogs() or ["600x400"]
        f.dialogs = dialogs
        f.fusion_cancel_works = True
        code, _logs = go(f)
        self.assertEqual(code, 4)

    def test_a_dialog_closing_just_after_the_cancel_is_not_a_problem(self):
        # right after the press Fusion is idle while the dialog is still listed for a moment
        st = CleanupStub([sd.CREATE_CMD, sd.IDLE_CMD, sd.IDLE_CMD], [["395x445"], ["395x445"], []])
        self.assertTrue(sd.cancel_dialogs(st, st.log.append, tries=4, poll_s=0))
        self.assertEqual(st.clicks, ["Cancel"])

    def test_cleanup_presses_cancel_through_accessibility_first(self):
        # PM ruling 2026-10-31: ending an open Create Drawing by script killed Fusion
        f = FakeFusion(ok_found=False)                          # OK can't be pressed
        code, _logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertEqual(set(f.clicks[:-1]), {"OK"})             # OK tried for the press time, then
        self.assertEqual(f.clicks[-1], "Cancel")                # the cleanup's Cancel through accessibility
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
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0, **kw: sd_cancel(steps, log, 2, 0.001, **kw)
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
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0, **kw: sd_cancel(steps, log, 2, 0.001, **kw)
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
            sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0, **kw: sd_cancel(steps, log, 2, 0.001, **kw)
            code, _ = go(f)
        finally:
            sd.cancel_dialogs = sd_cancel
        self.assertEqual(code, 4)                               # never claims Fusion is idle
        self.assertEqual(f.cancels, 0)                          # never touched while busy

    @unittest.skipUnless(shutil.which("osacompile"), "osacompile is macOS only")
    def run_main(self, make_fake, timed_out_after_queue, open_stuck=False, flag_pid="none", batch=None):
        """start_drawing's main() with a fake Fusion and a lock in a temporary folder;
        returns (exit code, the wait call seen or None, lock dir). open_stuck: the call
        that times out has started an open that never ends (logged as the wrapper does);
        flag_pid: write an unhealthy flag for that Fusion process first."""
        import signal
        import tempfile
        lockdir = os.path.join(tempfile.mkdtemp(prefix="sdlock-"), "fusion.lock")
        seen = {"steps": 0}
        what = ["100000_P04_POD-SKELETON_CAD", "X_P01_TEST_DWG"]
        if batch:                                       # --batch FILE instead of DESIGN DRAWING
            self.batch_file = os.path.join(os.path.dirname(lockdir), "starts.txt")
            with open(self.batch_file, "w") as fh:
                fh.write("".join("%s %s %s\n" % b for b in batch))
            what = ["--batch", self.batch_file]
        if flag_pid != "none":
            with open(rs.unhealthy_path(lockdir), "w") as fh:
                json.dump({"flagged_utc": "2026-11-01 03:55:00 UTC", "fusion_pid": flag_pid,
                           "opens": [{"started": "2026-11-01 03:39:45 UTC", "what": "ZZ_P00_X_DWG v1",
                                      "run": "TEST"}]}, fh)

        def fake_steps(url, timeout, mcp=None):
            seen["steps"] += 1
            f = make_fake()
            if timed_out_after_queue:
                def _mcp():                             # Fusion stops answering in time
                    if f.queued:
                        if open_stuck and not seen.get("logged"):
                            seen["logged"] = True
                            with open(rs.open_log_path(lockdir), "a") as fh:
                                fh.write("2026-11-01 03:39:45 UTC start open 100000_P04_POD-SKELETON_CAD v4 "
                                         "HIDDEN; run: TEST: start_drawing.py\n")
                        mcp.timed_out = True
                        raise rs.McpTimeout("Fusion MCP didn't answer within 1 s (fake)")
                f._mcp = _mcp
            return f

        def fake_wait(url, lock, wait_s, poll_s, log=None, **_kw):
            seen["wait"] = (os.path.isdir(lockdir), wait_s, poll_s)
            return True

        keep = (sd.Steps, rs.wait_for_fusion, sd.run_with_cleanup, sd.cancel_dialogs,
                signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGHUP))
        orig_run, orig_cancel = sd.run_with_cleanup, sd.cancel_dialogs
        sd.Steps, rs.wait_for_fusion = fake_steps, fake_wait
        sd.run_with_cleanup = lambda *a, **_k: orig_run(*a[:7], waits=FAST)   # run_batch passes waits 8th
        sd.cancel_dialogs = lambda steps, log, tries=4, poll_s=1.0, **kw: orig_cancel(steps, log, 2, 0.001, **kw)
        env_token = os.environ.pop(rs.TOKEN_ENV, None)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = sd.main(what + ["--lock", lockdir,
                                       "--busy-wait", "60", "--busy-poll", "2", "--open-limit", "0.3"])
        finally:
            (sd.Steps, rs.wait_for_fusion, sd.run_with_cleanup, sd.cancel_dialogs) = keep[:4]
            signal.signal(signal.SIGTERM, keep[4])
            signal.signal(signal.SIGHUP, keep[5])
            if env_token is not None:
                os.environ[rs.TOKEN_ENV] = env_token
        self.steps_made = seen["steps"]
        return code, seen.get("wait"), lockdir

    def test_a_timed_out_call_keeps_the_lock_until_fusion_answers(self):
        # as run_script.py (#181): the lock is given back only after Fusion answers again
        code, wait, lockdir = self.run_main(lambda: FakeFusion(), timed_out_after_queue=True)
        self.assertIn(code, (2, 4))
        self.assertEqual(wait, (True, 60.0, 2.0))             # waited while still holding the lock
        self.assertFalse(os.path.exists(lockdir))              # then gave it back

    def test_an_open_that_never_ends_after_a_timeout_flags_fusion_unhealthy(self):
        # as run_script.py (PM ruling 2026-11-01): Fusion answers, but the open never ended
        code, wait, lockdir = self.run_main(lambda: FakeFusion(), timed_out_after_queue=True, open_stuck=True)
        self.assertEqual(code, rs.EXIT_UNHEALTHY)
        self.assertIsNotNone(wait)
        with open(rs.unhealthy_path(lockdir)) as fh:
            self.assertEqual([o["what"] for o in json.load(fh)["opens"]], ["100000_P04_POD-SKELETON_CAD v4"])
        self.assertFalse(os.path.exists(lockdir))

    def test_a_flagged_fusion_is_refused_before_anything_is_sent(self):
        code, wait, lockdir = self.run_main(lambda: FakeFusion(), timed_out_after_queue=False,
                                            flag_pid=rs.fusion_pid())
        self.assertEqual(code, rs.EXIT_UNHEALTHY)
        self.assertEqual(self.steps_made, 0)                   # never talked to Fusion
        self.assertIsNone(wait)
        self.assertFalse(os.path.exists(lockdir))

    BATCH = [("D%d_CAD" % i, "D%d_DWG" % i, "A2") for i in range(1, 4)]

    def test_the_design_open_installs_the_open_logger(self):
        # Reviewer 5 on #269: start_drawing's own scripts skip the runner's wrapper, so its
        # design open was logged only after some run_script run had installed the logger
        made = []

        def make():
            f = FakeFusion(opened=True)
            f.sources, orig = [], f.run

            def run(src, read_only=False):
                f.sources.append(src)
                return orig(src, read_only)
            f.run = run
            made.append(f)
            return f
        code, _wait, lockdir = self.run_main(make, timed_out_after_queue=False)
        self.assertEqual(code, 0)
        opens = [src for src in made[0].sources if "ARGS = {" in src and "'mode': 'open'" in src]
        self.assertEqual(len(opens), 1)
        self.assertIn("_OPENLOG = %r" % rs.open_log_path(lockdir), opens[0])
        self.assertIn("start_drawing.py 100000_P04_POD-SKELETON_CAD -> X_P01_TEST_DWG", opens[0])

    def test_a_flagged_fusion_refuses_a_batch_before_any_start(self):
        # the hand merge of #140 and #269: the refusal comes before the batch's first start
        code, wait, lockdir = self.run_main(lambda: FakeFusion(opened=True), timed_out_after_queue=False,
                                            flag_pid=rs.fusion_pid(), batch=self.BATCH)
        self.assertEqual(code, rs.EXIT_UNHEALTHY)
        self.assertEqual(self.steps_made, 0)
        self.assertIsNone(wait)
        self.assertFalse(os.path.exists(self.batch_file + ".rest"))      # the list stays as it was
        self.assertFalse(os.path.exists(lockdir))

    def test_a_batch_start_stuck_in_an_open_flags_fusion_and_keeps_the_rest(self):
        # the batch stops at the timed-out start, #183's wait keeps the lock, then #269's check
        # finds the open that never ended and flags Fusion; the rest file keeps every start
        code, wait, lockdir = self.run_main(lambda: FakeFusion(opened=True), timed_out_after_queue=True,
                                            open_stuck=True, batch=self.BATCH)
        self.assertEqual(code, rs.EXIT_UNHEALTHY)
        self.assertEqual(wait, (True, 60.0, 2.0))
        self.assertTrue(os.path.exists(rs.unhealthy_path(lockdir)))
        self.assertEqual(sd.read_batch(self.batch_file + ".rest", "A2"), self.BATCH)   # failed first, then the rest
        self.assertFalse(os.path.exists(lockdir))

    def test_a_start_without_a_timeout_gives_the_lock_back_at_once(self):
        code, wait, lockdir = self.run_main(lambda: FakeFusion(), timed_out_after_queue=False)
        self.assertEqual(code, 0)
        self.assertIsNone(wait)
        self.assertFalse(os.path.exists(lockdir))

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
                    sd.QUEUE_SCRIPT % {"project": "P", "design": "D", "cmd": sd.CREATE_CMD,
                                       "state": sd.STATE_MODULE, "key": "k"},
                    sd.CLOSE_DESIGN_SCRIPT % {"name": "D", "key": "k", "state": sd.STATE_MODULE},
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


class BatchTests(unittest.TestCase):
    """--batch (PM rule 2026-10-31: up to 6 starts or about 15 minutes per lock hold)."""

    PAIRS = [("D%d_CAD" % i, "D%d_DWG" % i, "A2") for i in range(1, 4)]

    def batch(self, fake, pairs=None, **kw):
        logs = []
        out = sd.run_batch(fake, pairs or self.PAIRS, "Default Project/FocusPod v2", logs.append,
                           waits=FAST, **kw)
        return out, logs

    def test_every_start_is_saved_and_closed(self):
        f = FakeFusion(opened=True)
        (code, done, failed, left), _ = self.batch(f)
        self.assertEqual((code, len(done), failed, left), (0, 3, None, []))
        self.assertEqual(f.ran, ["open", "queue", "save", "close"] * 3)
        self.assertEqual(len(f.saved), 3)

    def test_it_stops_at_the_first_failure(self):
        f = FakeFusion(opened=True)
        real_click, oks = f.click, []

        def click(button, title):
            if button == "OK":
                oks.append(1)
                if len(oks) >= 2:
                    return "none"                               # the 2nd start can't press OK, retries too
            return real_click(button, title)

        f.click = click
        (code, done, failed, left), logs = self.batch(f)
        self.assertEqual(code, 1)
        self.assertEqual([d[1] for d in done], ["D1_DWG"])
        self.assertEqual(failed, (("D2_CAD", "D2_DWG", "A2"), 1))
        self.assertEqual(left, [("D3_CAD", "D3_DWG", "A2")])
        self.assertEqual(f.cmd, sd.IDLE_CMD)                    # the failed start cleaned up
        self.assertTrue(any("stopped at D2_DWG" in m for m in logs))

    def test_a_start_that_saved_then_failed_is_not_written_back(self):
        # Reviewer 5, P3 on #140: written back, its own check refuses it on the next hold
        # ("already in the folder") and the list stalls there every hold
        f = FakeFusion(opened=True)
        real_dialogs = f.dialogs

        def dialogs():
            if len(f.saved) == 2 and not getattr(f, "late", False):     # a late dialog after the 2nd save
                f.late = True
                return ["a late dialog"]
            return real_dialogs()
        f.dialogs = dialogs
        (code, done, failed, left), logs = self.batch(f)
        self.assertEqual(code, 1)
        self.assertEqual([d[1] for d in done], ["D1_DWG", "D2_DWG"])
        self.assertIsNone(failed)                                       # nothing to start again
        self.assertEqual(left, [("D3_CAD", "D3_DWG", "A2")])
        self.assertTrue(any("D2_DWG was saved before it failed" in m for m in logs))
        d = tempfile.mkdtemp(prefix="batch-test-")
        rest = os.path.join(d, "starts.txt.rest")
        sd.write_rest(rest, failed, left)
        self.assertEqual(sd.read_batch(rest, "A2"), [("D3_CAD", "D3_DWG", "A2")])

    def test_at_most_six_starts_per_hold(self):
        pairs = [("D%d_CAD" % i, "D%d_DWG" % i, "A2") for i in range(1, 9)]
        (code, done, failed, left), logs = self.batch(FakeFusion(opened=True), pairs)
        self.assertEqual((code, len(done), failed, len(left)), (0, 6, None, 2))
        self.assertEqual(left[0][1], "D7_DWG")

    def test_no_start_begins_after_the_time_budget(self):
        clock = iter([0.0, 16 * 60.0, 16 * 60.0])        # t0; the 1st start never waits; the 2nd check is late
        (code, done, failed, left), logs = self.batch(FakeFusion(opened=True), now=lambda: next(clock))
        self.assertEqual((code, len(done), len(left)), (0, 1, 2))
        self.assertTrue(any("about 15 minutes per hold" in m for m in logs))

    def test_the_batch_file(self):
        d = tempfile.mkdtemp(prefix="batch-test-")
        p = os.path.join(d, "starts.txt")
        with open(p, "w") as fh:
            fh.write("# WALL skins\n210101_P01_A_CAD 210101_P01_A_DWG\n\n210102_P01_B_CAD\t210102_P01_B_DWG A1\n")
        self.assertEqual(sd.read_batch(p, "A2"), [("210101_P01_A_CAD", "210101_P01_A_DWG", "A2"),
                                                  ("210102_P01_B_CAD", "210102_P01_B_DWG", "A1")])
        for bad, why in (("X_CAD\n", "expected DESIGN DRAWING"), ("X_CAD X_DWG B9\n", "sheet 'B9'"),
                         ("A_CAD X_DWG\nB_CAD X_DWG\n", "twice"), ("# only a comment\n", "no starts")):
            with open(p, "w") as fh:
                fh.write(bad)
            with self.assertRaises(ValueError) as cm:
                sd.read_batch(p, "A2")
            self.assertIn(why, str(cm.exception))

    def test_what_is_left_goes_to_the_rest_file_failed_first(self):
        d = tempfile.mkdtemp(prefix="batch-test-")
        rest = os.path.join(d, "starts.txt.rest")
        sd.write_rest(rest, (("D2_CAD", "D2_DWG", "A2"), 1), [("D3_CAD", "D3_DWG", "A1")])
        with open(rest) as fh:
            lines = fh.read().splitlines()
        self.assertEqual(lines[1:], ["D2_CAD D2_DWG A2", "D3_CAD D3_DWG A1"])
        self.assertTrue(lines[0].startswith("# failed (exit 1)"))
        self.assertEqual(sd.read_batch(rest, "A2")[0], ("D2_CAD", "D2_DWG", "A2"))   # runs again as is

    def test_a_bad_batch_file_is_refused_before_the_lock(self):
        d = tempfile.mkdtemp(prefix="batch-test-")
        p = os.path.join(d, "starts.txt")
        with open(p, "w") as fh:
            fh.write("only_one_name\n")
        lockdir = os.path.join(d, "fusion.lock")
        r = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "--batch", p,
                            "--lock", lockdir, "--url", "http://127.0.0.1:9/mcp", "--timeout", "2"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1)
        self.assertIn("line 1", r.stderr)
        self.assertFalse(os.path.exists(lockdir))


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


class FDoc:
    """An open Fusion document, as the design close sees it."""
    def __init__(self, name, docs, modified=False, drawing=False, stays=False, takes=()):
        self.name, self.docs, self.isModified, self.stays, self.takes = name, docs, modified, stays, takes
        self.objectType = "Drawing" if drawing else "Design"
        self.isSaved, self.isValid, self.closes = True, True, []

    def close(self, save):
        self.closes.append(save)
        if not self.stays:
            for d in (self,) + tuple(self.takes):
                if d in self.docs:
                    self.docs.remove(d)
                    d.isValid = False
        return True


class FDocs(list):
    @property
    def count(self):
        return len(self)

    def item(self, i):
        if not 0 <= i < len(self):
            raise RuntimeError("3 : Bad index parameter")
        return self[i]


def in_fusion(source, docs, active=None):
    """Run an in-Fusion script of start_drawing against fake documents; returns what it printed."""
    executed = []
    cmd = types.SimpleNamespace(execute=lambda: executed.append(True) or True)
    app = types.SimpleNamespace(
        documents=docs, activeDocument=active,
        data=types.SimpleNamespace(dataProjects=[types.SimpleNamespace(name="Default Project")], activeProject=None),
        userInterface=types.SimpleNamespace(commandDefinitions=types.SimpleNamespace(itemById=lambda _i: cmd)))
    adsk = types.ModuleType("adsk")
    adsk.doEvents = lambda: None
    adsk.core = types.SimpleNamespace(Application=types.SimpleNamespace(get=lambda: app))
    adsk.drawing = types.SimpleNamespace(DrawingDocument=types.SimpleNamespace(classType=lambda: "Drawing"))
    saved = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.drawing")}
    sys.modules.update({"adsk": adsk, "adsk.core": adsk.core, "adsk.drawing": adsk.drawing})
    out = io.StringIO()
    try:
        ns = {}
        exec(compile(source, "in_fusion", "exec"), ns)
        with contextlib.redirect_stdout(out):
            ns["run"](None)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return out.getvalue(), executed


class DesignCloseTests(unittest.TestCase):
    """The design close (Lead, 2026-11-01, from BASE: twice that day, 110103 at 07:36 and the sill 111301 at
    09:30, Fusion had two open documents with the design's name after Create Drawing, the runner's close step
    refused them, and the design stayed open): this start's own document is found by the document itself,
    every extra copy with the name is closed too, and nothing is closed when any copy has unsaved changes."""

    def setUp(self):
        self.addCleanup(sys.modules.pop, sd.STATE_MODULE, None)

    def queue(self, doc, docs, key="k1"):
        out, executed = in_fusion(sd.QUEUE_SCRIPT % {"project": "Default Project", "design": "X_CAD",
                                                      "cmd": sd.CREATE_CMD, "state": sd.STATE_MODULE,
                                                      "key": key}, docs, active=doc)
        self.assertEqual(executed, [True])                      # Create Drawing was queued
        return out

    def close(self, docs, key="k1"):
        return in_fusion(sd.CLOSE_DESIGN_SCRIPT % {"name": "X_CAD", "key": key, "state": sd.STATE_MODULE},
                         docs)[0]

    def test_the_queue_step_keeps_the_document_it_queues_from(self):
        docs = FDocs()
        ours = FDoc("X_CAD", docs)
        docs.append(ours)
        self.queue(ours, docs)
        self.assertIs(sys.modules[sd.STATE_MODULE].designs["k1"], ours)

    def test_two_open_copies_are_both_closed_this_starts_own_first(self):
        docs = FDocs()
        ours, extra = FDoc("X_CAD", docs), FDoc("X_CAD", docs)
        docs.append(ours)
        self.queue(ours, docs)
        docs.insert(0, extra)                                   # Create Drawing left a second one, listed first
        out = self.close(docs)
        self.assertEqual(list(docs), [])
        self.assertEqual((ours.closes, extra.closes), ([False], [False]))   # never close(True)
        self.assertLess(out.index("closed this start's copy"), out.index("closed an extra copy"))
        self.assertIn("this start's copy among them", out)
        self.assertIn("DESIGN_CLOSED", out)
        self.assertNotIn("k1", sys.modules[sd.STATE_MODULE].designs)        # used once

    def test_unsaved_changes_in_any_copy_close_nothing_and_say_so(self):
        for which in ("extra", "ours"):
            docs = FDocs()
            ours = FDoc("X_CAD", docs, modified=which == "ours")
            extra = FDoc("X_CAD", docs, modified=which == "extra")
            docs.append(ours)
            sys.modules.pop(sd.STATE_MODULE, None)
            if which == "extra":
                self.queue(ours, docs)
            else:                                               # the queue step refuses a modified design
                in_fusion(sd.CLOSE_DESIGN_SCRIPT % {"name": "-", "key": "", "state": sd.STATE_MODULE}, docs)
            docs.append(extra)
            out = self.close(docs)
            self.assertEqual(list(docs), [ours, extra], which)
            self.assertEqual((ours.closes, extra.closes), ([], []), which)
            self.assertIn("DESIGN_LEFT_OPEN", out)
            self.assertIn("nothing closed", out)

    def test_without_the_kept_document_every_copy_counts_as_extra(self):
        # Fusion restarted between the queue and the close, or a start from before this change
        docs = FDocs()
        a, b = FDoc("X_CAD", docs), FDoc("X_CAD", docs)
        docs.extend([a, b])
        out = self.close(docs, key="not-kept")
        self.assertEqual(list(docs), [])
        self.assertIn("not known", out)
        self.assertIn("DESIGN_CLOSED", out)

    def test_other_documents_are_never_touched(self):
        docs = FDocs()
        ours = FDoc("X_CAD", docs)
        others = [FDoc("Y_CAD", docs, modified=True), FDoc("X_CAD", docs, drawing=True),
                  FDoc("X_DWG", docs, drawing=True), FDoc("X_CAD (1)", docs)]
        docs.append(ours)
        self.queue(ours, docs)
        docs.extend(others)
        out = self.close(docs)
        self.assertEqual(list(docs), others)
        self.assertEqual([d.closes for d in others], [[], [], [], []])
        self.assertIn("DESIGN_CLOSED", out)

    def test_a_copy_that_stays_open_is_tried_once_and_reported(self):
        docs = FDocs()
        ours, stuck = FDoc("X_CAD", docs), FDoc("X_CAD", docs, stays=True)
        docs.append(ours)
        self.queue(ours, docs)
        docs.append(stuck)
        out = self.close(docs)
        self.assertEqual(list(docs), [stuck])
        self.assertEqual(stuck.closes, [False])
        self.assertIn("DESIGN_LEFT_OPEN", out)
        self.assertIn("still open after their close", out)

    def test_a_copy_that_went_with_an_earlier_close_is_skipped(self):
        docs = FDocs()
        extra = FDoc("X_CAD", docs)
        ours = FDoc("X_CAD", docs, takes=(extra,))
        docs.append(ours)
        self.queue(ours, docs)
        docs.append(extra)
        out = self.close(docs)
        self.assertEqual((list(docs), extra.closes), ([], []))
        self.assertIn("DESIGN_CLOSED", out)

    def test_already_closed(self):
        self.assertIn("already closed", self.close(FDocs()))

    def test_the_start_closes_with_its_own_key_and_reports_a_copy_left_open(self):
        f = FakeFusion(opened=True)
        f.close_out = ("open copies of X: 2 (this start's copy among them)\n"
                       "DESIGN_LEFT_OPEN: 1 of the 2 open copies of X have unsaved changes; nothing closed")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code, logs = go(f)
        self.assertEqual(code, 0)                               # the drawing was made and saved
        self.assertEqual(f.ran, ["open", "queue", "save", "close"])
        # the key the queue step kept the design under (a 32-digit hex word in its text)
        keys = [k for k in f.queue_src.replace("'", " ").split() if len(k) == 32]
        self.assertEqual(len(keys), 1)
        self.assertIn(keys[0], f.closes[-1])                    # the close looks for the same document
        self.assertIn("was left open", err.getvalue())
        self.assertIn("nothing closed", err.getvalue())
        self.assertTrue(any("DESIGN_LEFT_OPEN" in m for m in logs))


if __name__ == "__main__":
    unittest.main(verbosity=2)
