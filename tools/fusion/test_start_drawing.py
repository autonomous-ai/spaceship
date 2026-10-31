#!/usr/bin/env python3
"""Offline tests for start_drawing.py: the dialog sequence against a fake Fusion.

    python3 tools/fusion/test_start_drawing.py

No Fusion, no accessibility, no screen: FakeFusion plays Fusion's command
states and its two dialogs as seen on Mac 1 on 2026-10-31 (Create Drawing
opens, OK makes the drawing after a few seconds, then Fusion opens Base View
by itself), plus the screen lock, accessibility and Fusion's own cancel.
"""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
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
                 mcp_dies_after_queue=False, ax_works=True):
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
        self.queued = False
        self.pending = []          # (polls left, action)
        self.ran, self.clicks, self.saved, self.cancels = [], [], [], 0

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
                return True, "run_script: closed 'X'"
            return True, ("run_script: opened 'X' (version 1)" if self.opened
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

    def test_cleanup_uses_fusions_own_cancel_first(self):
        f = FakeFusion(ok_found=False)                          # OK can't be pressed
        code, _logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertGreaterEqual(f.cancels, 1)
        self.assertEqual(f.clicks, ["OK"])                      # no accessibility Cancel needed

    def test_cleanup_falls_back_to_accessibility_cancel(self):
        f = FakeFusion(ok_found=False, fusion_cancel_works=False)
        code, _logs = go(f)
        self.assertEqual(code, 1)
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertIn("Cancel", f.clicks)

    def test_dialog_left_open_exits_4(self):
        f = FakeFusion(ok_found=False, fusion_cancel_works=False)
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

        def killed(button, title):
            orig(button, title)
            raise KeyboardInterrupt                              # as the handler does
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

    def test_scripts_compile(self):
        for src in (sd.STATE_SCRIPT, sd.CLOSE_UNSAVED_SCRIPT, sd.FUSION_CANCEL_SCRIPT,
                    sd.QUEUE_SCRIPT % {"project": "P", "design": "D", "cmd": sd.CREATE_CMD},
                    sd.SAVE_SCRIPT % {"project": "P", "subfolders": ["F"], "name": "N",
                                      "sheet": "A2", "size": (594, 420), "close": True, "desc": "d"}):
            compile(src, "fusion", "exec")

    def test_session_lock_reader_parses_ioreg(self):
        self.assertIn(sd.session_locked(), (True, False))


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
