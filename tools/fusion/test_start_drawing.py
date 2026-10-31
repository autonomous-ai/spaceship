#!/usr/bin/env python3
"""Offline tests for start_drawing.py: the dialog sequence against a fake Fusion.

    python3 tools/fusion/test_start_drawing.py

No Fusion and no accessibility: FakeFusion plays Fusion's command states and
its two dialogs as seen on Mac 1 on 2026-10-31 (Create Drawing opens, OK makes
the drawing after a few seconds, then Fusion opens Base View by itself).
"""

import json
import os
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
                 base_view_after=4, start_cmd=sd.IDLE_CMD, unsaved=0, opened=False):
        self.opened = opened
        self.cmd = start_cmd
        self.unsaved = unsaved
        self.dialog_opens = dialog_opens
        self.ok_found = ok_found
        self.base_view = base_view
        self.drawing_after = drawing_after
        self.base_view_after = base_view_after
        self.queued = False
        self.pending = []          # (polls left, action)
        self.ran, self.clicks, self.saved = [], [], []

    def _tick(self):
        nxt = []
        for left, action in self.pending:
            if left <= 1:
                action()
            else:
                nxt.append((left - 1, action))
        self.pending = nxt

    def state(self):
        self._tick()
        return self.cmd, self.unsaved

    def run(self, source, read_only=False):
        if "ARGS = {" in source:
            mode = "close" if "'mode': 'close'" in source else "open"
            self.ran.append(mode)
            if mode == "close":
                return True, "run_script: closed 'X'"
            return True, ("run_script: opened 'X'" if self.opened else "run_script: activated 'X'")
        if sd.CREATE_CMD in source and "execute()" in source:
            self.ran.append("queue")
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

    def click(self, button):
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
                return True
            if button == "Cancel":
                self.cmd = sd.IDLE_CMD
                return True
            return False
        if self.cmd == sd.BASE_VIEW_CMD and button in ("OK", "Cancel"):
            self.cmd = sd.IDLE_CMD
            return True
        return False


def go(fake, **kw):
    logs = []
    sd.start_drawing(fake, "100000_P04_POD-SKELETON_CAD", "X_P01_TEST_DWG",
                     "Default Project/FocusPod v2", kw.get("sheet", "A2"), False,
                     logs.append, waits=FAST)
    return logs


class SequenceTests(unittest.TestCase):
    def test_happy_path_presses_ok_then_cancel_and_saves(self):
        f = FakeFusion()
        logs = go(f, sheet="A1")
        self.assertEqual(f.ran, ["open", "queue", "save"])
        self.assertEqual(f.clicks, ["OK", "Cancel"])
        self.assertEqual(f.cmd, sd.IDLE_CMD)
        self.assertEqual(f.unsaved, 0)
        self.assertIn("'A1' + \"ISOSheetSize\"", f.saved[0])
        self.assertIn("'X_P01_TEST_DWG'", f.saved[0])
        self.assertTrue(any("pressed Cancel in Base View" in m for m in logs))

    def test_a_design_it_opened_is_closed_again(self):
        f = FakeFusion(opened=True)
        go(f)
        self.assertEqual(f.ran, ["open", "queue", "save", "close"])

    def test_no_base_view_dialog_still_saves(self):
        f = FakeFusion(base_view=False)
        logs = go(f)
        self.assertEqual(f.clicks, ["OK"])
        self.assertEqual(f.ran[-1], "save")
        self.assertTrue(any("no Base View dialog" in m for m in logs))

    def test_dialog_that_never_opens_stops_before_any_click(self):
        f = FakeFusion(dialog_opens=False)
        with self.assertRaises(sd.StartError) as cm:
            go(f)
        self.assertIn("didn't open", str(cm.exception))
        self.assertEqual(f.clicks, [])

    def test_missing_ok_button_fails_and_cleanup_leaves_fusion_idle(self):
        f = FakeFusion(ok_found=False)
        with self.assertRaises(sd.StartError):
            go(f)
        self.assertEqual(f.cmd, sd.CREATE_CMD)              # the dialog is still open...
        self.assertTrue(sd.cancel_dialogs(f, lambda m: None, poll_s=0.001))
        self.assertEqual(f.cmd, sd.IDLE_CMD)                # ...until cleanup presses Cancel
        self.assertIn("Cancel", f.clicks)

    def test_busy_fusion_is_not_touched(self):
        f = FakeFusion(start_cmd="SketchCreate")
        with self.assertRaises(sd.StartError) as cm:
            go(f)
        self.assertIn("isn't idle", str(cm.exception))
        self.assertEqual(f.ran, [])

    def test_an_unsaved_drawing_already_open_stops_it(self):
        f = FakeFusion(unsaved=1)
        with self.assertRaises(sd.StartError) as cm:
            go(f)
        self.assertIn("unsaved drawing", str(cm.exception))
        self.assertEqual(f.ran, [])

    def test_slow_drawing_times_out_cleanly(self):
        f = FakeFusion(drawing_after=10 ** 6)
        with self.assertRaises(sd.StartError) as cm:
            go(f)
        self.assertIn("no new drawing", str(cm.exception))

    def test_scripts_compile(self):
        for src in (sd.STATE_SCRIPT, sd.CLOSE_UNSAVED_SCRIPT,
                    sd.QUEUE_SCRIPT % {"project": "P", "design": "D", "cmd": sd.CREATE_CMD},
                    sd.SAVE_SCRIPT % {"project": "P", "subfolders": ["F"], "name": "N",
                                      "sheet": "A2", "close": True, "desc": "d"}):
            compile(src, "fusion", "exec")


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

    def test_bad_sheet_is_refused(self):
        p = subprocess.run([sys.executable, os.path.join(HERE, "start_drawing.py"), "D", "N",
                            "--sheet", "B"], capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
