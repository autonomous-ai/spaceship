#!/usr/bin/env python3
"""Start a new Fusion drawing of a saved design, with nobody at the Mac.

    python3 tools/fusion/start_drawing.py DESIGN_NAME DRAWING_NAME [--sheet A2] [--keep-open]

Fusion's API can't create a drawing in this build: manual creation needs a
drawing template (.f2t) with view placeholders, a saved drawing (.f2d) is
refused as a template, and automatic creation hung (tools/fusion/README.md).
So this command uses Fusion's own Create Drawing command and presses its two
buttons through macOS accessibility, all inside the Fusion lock:

1. take the Fusion lock (it waits its turn like any run);
2. refuse, before opening anything, when DRAWING_NAME is already in --folder or
   an entry there can't be read and could be it (an unreadable entry known to
   be another kind of file only gets a warning), and unless Fusion is idle
   (Home screen included),
   no unsaved drawing is open, the Mac's screen isn't locked and accessibility
   can see Fusion's windows (it can't while the screen is locked);
3. open or activate DESIGN_NAME (refused if it has unsaved changes) and queue
   Create Drawing (its dialog defaults: Manual, From scratch, ISO, mm);
4. press OK in that dialog and wait for the new drawing;
5. press Cancel in the Base View dialog that Fusion then opens by itself;
6. set the sheet size (read back and checked), save the drawing as
   DRAWING_NAME in --folder, close it (unless --keep-open), and close the
   design again if this command opened it;
7. check that no dialog is left, and give the lock back.

Cleanup, whenever a step fails after the dialog was queued (also on SIGTERM,
SIGHUP, Ctrl-C and lost contact with Fusion): Cancel through accessibility
first, as a person would press it; Fusion's own cancel (a read-only script
that starts Fusion's Select command) only when Fusion says its Create Drawing
or Base View dialog is open but accessibility has seen no dialog on two polls
in a row, never while Fusion is busy; then the unsaved drawing it made is
closed, and the design if this command opened it (never with unsaved changes). Nothing ends a command by script any more: terminateActiveCommand()
on an open Create Drawing killed Fusion on 2026-10-31.

Exit 0 = saved, 1 = failed or refused (Fusion left idle), 2 = Fusion not
reachable, 3 = the Fusion lock was busy past --lock-wait, 4 = Fusion was left
with a dialog open (a person must press Cancel in Fusion).
Then add views with the drawing API (base views only): run_script.py with
--doc DRAWING_NAME.
"""

import argparse
import json
import os
import plistlib
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_script as rs  # noqa: E402

CREATE_CMD = "FusionDrawingCreateFromComponentsCommand"
BASE_VIEW_CMD = "FusionDrawingViewBaseCommand"
IDLE_CMD = "SelectCommand"
IDLE_CMDS = (IDLE_CMD, "")    # with no document open (Home screen) Fusion reports no active command
TITLES = {CREATE_CMD: "Create Drawing", BASE_VIEW_CMD: "Base View"}
# ISO landscape sheet sizes, mm
SHEETS = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4": (297, 210)}

# Clicks button argv[1] in the Fusion dialog for argv[2] ("Create Drawing" or
# "Base View"): the AXDialog window with OK and Cancel whose title, or one of
# whose texts, names it. Fusion's Qt dialogs may expose no title; then the one
# and only dialog with OK and Cancel is used (Fusion's palettes have neither),
# and "ambiguous" is returned when there are several.
AX_CLICK = '''on run argv
  set target to item 1 of argv
  set hint to item 2 of argv
  set found to {}
  tell application "System Events"
    tell (first process whose name is "Autodesk Fusion")
      repeat with w in (every window whose subrole is "AXDialog")
        set bn to name of every button of w
        if bn contains "OK" and bn contains "Cancel" then
          set isNamed to false
          try
            if (title of w as text) contains hint then set isNamed to true
          end try
          try
            if (name of w as text) contains hint then set isNamed to true
          end try
          try
            repeat with t in (value of every static text of w)
              if (t as text) contains hint then set isNamed to true
            end repeat
          end try
          if isNamed then
            click (first button of w whose name is target)
            return "clicked by title"
          end if
          set end of found to w
        end if
      end repeat
      if (count of found) is 1 then
        click (first button of (item 1 of found) whose name is target)
        return "clicked the only dialog"
      end if
      if (count of found) is 0 then return "none"
      return "ambiguous"
    end tell
  end tell
end run
'''

# Lists Fusion's dialog windows that have OK and Cancel, as "WxH" each.
AX_DIALOGS = '''tell application "System Events"
  tell (first process whose name is "Autodesk Fusion")
    set out to ""
    repeat with w in (every window whose subrole is "AXDialog")
      set bn to name of every button of w
      if bn contains "OK" and bn contains "Cancel" then
        set s to size of w
        set out to out & ((item 1 of s) as text) & "x" & ((item 2 of s) as text) & " "
      end if
    end repeat
    return out
  end tell
end tell
'''

AX_WINDOW_COUNT = '''tell application "System Events"
  tell (first process whose name is "Autodesk Fusion")
    return count of windows
  end tell
end tell
'''

STATE_SCRIPT = '''import adsk.core, adsk.drawing
def run(_c):
    app = adsk.core.Application.get()
    drawings = []
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.objectType == adsk.drawing.DrawingDocument.classType() and not d.isSaved:
            drawings.append(d.name)
    print("CMD=%s" % app.userInterface.activeCommand)
    print("UNSAVED_DRAWINGS=%d" % len(drawings))
'''

# Fusion's own cancel, needing no accessibility; runs read-only, so it works
# while a dialog is open. LAST RESORT only, when accessibility can't see the
# dialog: on 2026-10-31 terminateActiveCommand() on an open Create Drawing
# killed Fusion, so it is no longer used; starting the Select command closed
# a Create Drawing dialog safely once (locked screen, same day).
FUSION_CANCEL_SCRIPT = '''import adsk.core
def run(_c):
    ui = adsk.core.Application.get().userInterface
    before = ui.activeCommand
    s = ui.commandDefinitions.itemById("SelectCommand").execute()
    print("Fusion cancel (Select queued): active %s, queued %s" % (before, s))
'''

QUEUE_SCRIPT = '''import adsk.core
def run(_c):
    app = adsk.core.Application.get()
    proj = [p for p in app.data.dataProjects if p.name == %(project)r][0]
    app.data.activeProject = proj        # without it Create Drawing picked the wrong project and crashed
    doc = app.activeDocument
    if doc.name != %(design)r or not doc.isSaved:
        raise RuntimeError("the active document is %%r, not the saved design %%r" %% (doc.name, %(design)r))
    if doc.isModified:
        raise RuntimeError("%%s has unsaved changes; save or close it first (Create Drawing could ask to save)" %% doc.name)
    ok = app.userInterface.commandDefinitions.itemById(%(cmd)r).execute()
    print("queued Create Drawing for %%s: %%s" %% (doc.name, ok))
'''

# The shared folder check (tools/fusion/fusion_folder.py), put in front of the
# scripts that look at the folder: it reads the folder again for up to a minute
# while an entry can't be read, and an entry that stays unreadable blocks only
# when it could be the drawing being made (PM ruling 2026-10-31). One copy for
# the runner, this command and every team script.
LIST_FOLDER = rs.FOLDER_HELPER_SRC + "\n"

SAVE_SCRIPT = '''import adsk.core, adsk.drawing, time
def run(_c):
    app = adsk.core.Application.get()
    docs = [app.documents.item(i) for i in range(app.documents.count)]
    docs = [d for d in docs if d.objectType == adsk.drawing.DrawingDocument.classType() and not d.isSaved]
    if len(docs) != 1:
        raise RuntimeError("expected one unsaved drawing, found %%d" %% len(docs))
    doc = adsk.drawing.DrawingDocument.cast(docs[0])
    doc.activate()
    proj = [p for p in app.data.dataProjects if p.name == %(project)r][0]
    folder = proj.rootFolder
    for part in %(subfolders)r:
        folder = folder.dataFolders.itemByName(part)
    for w in safe_to_create(folder, %(name)r, "f2d"):       # raises if it isn't safe
        print("warning: %%s" %% w)
    sheet = doc.drawing.sheets.item(0)
    want = getattr(adsk.drawing.SheetSizes, %(sheet)r + "ISOSheetSize")
    sheet.sheetSize = want
    w, h = %(size)r
    # Fusion applies a new size in steps (live 2026-10-31: read 420 x 420 just
    # after setting A2), so let it finish and look again before judging; the
    # size value itself must be right too
    seen = []
    for attempt in range(10):
        adsk.doEvents()
        got = (sheet.sheetSize, sheet.width, sheet.height)
        seen.append("value %%s, %%g x %%g" %% got)
        if got[0] == want and abs(got[1] - w) <= 1 and abs(got[2] - h) <= 1:
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("the sheet isn't %(sheet)s %%g x %%g mm (size value %%s) after %%d looks; last seen: %%s"
                           %% (w, h, want, len(seen), "; ".join(seen[-3:])))
    print("sheet %%s: %%g x %%g mm, size value %%s, after %%d look(s); %%d views" %% (
        sheet.name, sheet.width, sheet.height, sheet.sheetSize, len(seen), sheet.views.count))
    if not doc.saveAs(%(name)r, folder, %(desc)r, ""):
        raise RuntimeError("saveAs failed")
    adsk.doEvents()
    print("SAVED_SHEET=%%s: %%g x %%g mm, size value %%s" %% (sheet.name, sheet.width, sheet.height, sheet.sheetSize))
    print("saved %%s" %% %(name)r)
    if %(close)r:
        print("closed: %%s" %% doc.close(False))
'''

# The precheck's look at the folder (read-only), with LIST_FOLDER in front.
FOLDER_SCRIPT = '''import adsk.core, json
def run(_c):
    app = adsk.core.Application.get()
    proj = [p for p in app.data.dataProjects if p.name == %(project)r][0]
    folder = proj.rootFolder
    for part in %(subfolders)r:
        folder = folder.dataFolders.itemByName(part)
    files, unknown, others = read_folder(folder)
    print("FOLDER_JSON=" + json.dumps({"unknown": could_be(unknown, others, "f2d"),
                                       "others": cannot_be(others, "f2d"),
                                       "has_design": %(design)r in files, "has_drawing": %(name)r in files}))
'''


# Closing a drawing can close other documents with it (seen live 2026-10-31:
# the next index was gone), so the list is read again after every close.
CLOSE_UNSAVED_SCRIPT = '''import adsk.core, adsk.drawing
def run(_c):
    app = adsk.core.Application.get()
    for _ in range(20):
        hit = None
        for i in range(app.documents.count):
            try:
                d = app.documents.item(i)
            except Exception:
                break                 # the list changed under us: read it again
            if d.objectType == adsk.drawing.DrawingDocument.classType() and not d.isSaved:
                hit = d
                break
        if hit is None:
            break
        name = hit.name
        print("closed unsaved drawing %s: %s" % (name, hit.close(False)))
        adsk.doEvents()
'''


class StartError(Exception):
    pass


def session_locked():
    """True when the Mac's console session is locked (ioreg IOConsoleUsers)."""
    out = subprocess.run(["ioreg", "-n", "Root", "-d1", "-a"], capture_output=True, timeout=30).stdout
    data = plistlib.loads(out)
    data = data[0] if isinstance(data, list) else data
    return any(u.get("CGSSessionScreenIsLocked") for u in data.get("IOConsoleUsers", []))


class Steps:
    """Talks to Fusion (MCP), its dialogs (accessibility) and the Mac. Split
    out so the offline tests can replace all three."""

    def __init__(self, url, timeout):
        self.mcp = rs.FusionMcp(url, timeout)
        self.mcp.initialize()

    def run(self, source, read_only=False):
        return rs.run_in_fusion(self.mcp, source, read_only)

    def state(self):
        ok, out = self.run(STATE_SCRIPT, read_only=True)
        if not ok:
            raise StartError("couldn't read Fusion's state: %s" % out)
        vals = dict(line.split("=", 1) for line in (out or "").splitlines() if "=" in line)
        return vals.get("CMD", ""), int(vals.get("UNSAVED_DRAWINGS", "0"))

    def folder(self, project, subfolders, design, name):
        """(unknown, others, has_design, has_drawing); see LIST_FOLDER."""
        ok, out = self.run(LIST_FOLDER + FOLDER_SCRIPT % {"project": project, "subfolders": subfolders,
                                                          "design": design, "name": name}, read_only=True)
        if not ok:
            raise StartError("couldn't list the folder: %s" % out)
        for line in (out or "").splitlines():
            if line.startswith("FOLDER_JSON="):
                v = json.loads(line.split("=", 1)[1])
                return v["unknown"], v["others"], v["has_design"], v["has_drawing"]
        raise StartError("the folder check printed no result: %s" % (out or "").strip()[:200])

    def fusion_cancel(self):
        ok, out = self.run(FUSION_CANCEL_SCRIPT, read_only=True)
        return ok, out

    @staticmethod
    def osa(script, *args):
        p = subprocess.run(["osascript", "-"] + list(args), input=script, text=True,
                           capture_output=True, timeout=30)
        if p.returncode != 0:
            raise StartError("accessibility call failed: %s" % p.stderr.strip()[:300])
        return p.stdout.strip()

    def click(self, button, title):
        return self.osa(AX_CLICK, button, title)

    def dialogs(self):
        return self.osa(AX_DIALOGS).split()

    def ax_window_count(self):
        try:
            return int(self.osa(AX_WINDOW_COUNT) or "0")
        except (StartError, ValueError):
            return 0

    @staticmethod
    def session_locked():
        return session_locked()


def wait_for(steps, pred, timeout_s, poll_s=1.0):
    """Poll Fusion's state until pred(cmd, unsaved) is true; return the last state."""
    t0 = time.time()
    while True:
        cmd, unsaved = steps.state()
        if pred(cmd, unsaved):
            return cmd, unsaved, True
        if time.time() - t0 >= timeout_s:
            return cmd, unsaved, False
        time.sleep(poll_s)


def cancel_dialogs(steps, log, tries=4, poll_s=1.0):
    """Get Fusion back to idle. Cancel through accessibility FIRST (what a person
    would press). Fusion's own cancel only when Fusion says one of this
    command's two dialogs is open (Create Drawing, Base View) but accessibility
    has seen no dialog on two polls in a row (a dialog can take seconds to
    show); never while Fusion is busy or in any other command (PM ruling
    2026-10-31, after ending an open Create Drawing by script killed Fusion).
    True when Fusion is idle and no OK/Cancel dialog is listed. Works without
    MCP too (accessibility only)."""
    unseen = 0
    for _ in range(tries):
        try:
            cmd, _u = steps.state()
            mcp_ok = True
        except (StartError, rs.McpError) as e:
            log("cleanup: can't read Fusion's state (%s)" % e)
            cmd, mcp_ok = None, False
        try:
            left = steps.dialogs()
            ax_ok = True
        except StartError as e:
            log("cleanup: accessibility can't list dialogs (%s)" % e)
            left, ax_ok = [], False
        if mcp_ok and cmd in IDLE_CMDS and not left:
            return True
        if left:
            unseen = 0
            try:
                log("cleanup: accessibility Cancel: %s" % steps.click("Cancel", TITLES.get(cmd, "")))
            except StartError as e:
                log("cleanup: %s" % e)
        elif mcp_ok and cmd in (CREATE_CMD, BASE_VIEW_CMD):
            unseen += 1
            if unseen < 2:
                log("cleanup: Fusion is in %s but accessibility sees no dialog (%s); looking again"
                    % (cmd, "it answers" if ax_ok else "it fails"))
            else:
                # its dialog is open but can't be pressed: last resort, Select only
                log("cleanup: still no dialog visible to accessibility; Fusion's own cancel")
                unseen = 0
                try:
                    ok, out = steps.fusion_cancel()
                    log("cleanup: %s" % (out or "").strip() if ok else "cleanup: Fusion cancel failed: %s" % out)
                except (StartError, rs.McpError) as e:
                    log("cleanup: Fusion cancel failed: %s" % e)
        else:
            unseen = 0
            if mcp_ok:
                log("cleanup: Fusion is busy (active command %s); not touching it, waiting" % (cmd or "none"))
        time.sleep(poll_s)
    try:
        cmd, _u = steps.state()
    except (StartError, rs.McpError):
        return False
    try:
        left = steps.dialogs()
    except StartError:
        left = []                 # accessibility unavailable: trust Fusion's own state
    return cmd in IDLE_CMDS and not left


def precheck(steps, design="", name="", folder=rs.DEFAULT_FOLDER, log=None):
    """Refuse before opening anything; None when it's safe to start. An entry
    of the drawing's folder that Fusion can't read refuses only when it could
    be the new drawing; otherwise it is logged and the start goes on (PM ruling
    2026-10-31: one bad entry must not block every team)."""
    if name:
        project, *subfolders = [p for p in folder.split("/") if p]
        unknown, others, _has_design, has_drawing = steps.folder(project, subfolders, design, name)
        if has_drawing:
            return "%s is already in %s; nothing was started" % (name, folder)
        if unknown:
            return ("%s of %s can't be read, so it could be %s; nothing was started (try again "
                    "later, or move that entry out)" % ("; ".join(unknown), folder, name))
        if others and log:
            log("warning: %s of %s can't be read by name, but %s not a drawing, so not %s; going on"
                % ("; ".join(others), folder, "it is" if len(others) == 1 else "they are", name))
    cmd, unsaved = steps.state()
    if cmd not in IDLE_CMDS:
        return "Fusion isn't idle (active command %s); nothing was started" % cmd
    if unsaved:
        return "%d unsaved drawing(s) already open; save or close them first" % unsaved
    try:
        if steps.session_locked():
            return "the Mac's screen is locked, so its dialogs can't be pressed; nothing was started"
    except Exception as e:  # noqa: BLE001 - a missing ioreg must refuse, not crash
        return "couldn't read the screen-lock state (%s); nothing was started" % e
    if steps.ax_window_count() < 1:
        return ("accessibility can't see Fusion's windows (screen locked, or no accessibility "
                "permission for this terminal); nothing was started")
    return None


def start_drawing(steps, design, name, folder, sheet, keep_open, log, waits=None, status=None):
    """The sequence; raises StartError with what went wrong. status["queued"] is
    set once a dialog may be open, so the caller knows to clean up."""
    w = {"dialog": 30, "drawing": 90, "base_view": 30, "idle": 20, "poll": 1.0}
    w.update(waits or {})
    status = status if status is not None else {}
    project, *subfolders = [p for p in folder.split("/") if p]

    why = precheck(steps, design, name, folder, log)
    if why:
        raise StartError(why)

    ok, out = steps.run(rs.doc_script("open", design, folder))
    if not ok:
        raise StartError("couldn't open %s: %s" % (design, out))
    log((out or "").strip())
    # any line: the runner may print a warning first (live 2026-10-31: "1 entry
    # ... could not be read; skipped", and the design was then left open)
    opened_here = any(line.startswith("run_script: opened") for line in (out or "").splitlines())
    status["opened_here"] = opened_here
    ok, out = steps.run(QUEUE_SCRIPT % {"project": project, "design": design, "cmd": CREATE_CMD})
    if not ok:
        raise StartError("couldn't queue Create Drawing: %s" % out)
    status["queued"] = True
    log((out or "").strip())

    cmd, _u, seen = wait_for(steps, lambda c, u: c == CREATE_CMD, w["dialog"], w["poll"])
    if not seen:
        raise StartError("the Create Drawing dialog didn't open (active command %s)" % cmd)
    how = steps.click("OK", TITLES[CREATE_CMD])
    if not how.startswith("clicked"):
        raise StartError("couldn't press OK in Create Drawing (%s)" % how)
    log("pressed OK in Create Drawing (%s)" % how)

    cmd, unsaved, made = wait_for(steps, lambda c, u: u >= 1 and c != CREATE_CMD, w["drawing"], w["poll"])
    if not made:
        raise StartError("no new drawing after OK (active command %s)" % cmd)
    log("new drawing is open")

    # Fusion opens the Base View dialog by itself, a few seconds later
    cmd, _u, seen = wait_for(steps, lambda c, u: c == BASE_VIEW_CMD, w["base_view"], w["poll"])
    if seen:
        how = steps.click("Cancel", TITLES[BASE_VIEW_CMD])
        if not how.startswith("clicked"):
            raise StartError("couldn't press Cancel in Base View (%s)" % how)
        log("pressed Cancel in Base View (%s)" % how)
    else:
        log("no Base View dialog within %d s (active command %s)" % (w["base_view"], cmd))
    cmd, _u, idle = wait_for(steps, lambda c, u: c == IDLE_CMD, w["idle"], w["poll"])
    if not idle:
        raise StartError("Fusion didn't go idle after the dialogs (active command %s)" % cmd)

    ok, out = steps.run(LIST_FOLDER + SAVE_SCRIPT % {"project": project, "subfolders": subfolders, "name": name,
                                       "sheet": sheet, "size": SHEETS[sheet], "close": not keep_open,
                                       "desc": "drawing of %s, started by start_drawing.py" % design})
    if not ok:
        raise StartError("couldn't save the drawing: %s" % out)
    log((out or "").strip())
    status["saved"] = True
    if opened_here:                      # leave Fusion as we found it
        close_design(steps, design, folder, status, log)
    if steps.dialogs():                  # a late dialog must not greet the next run
        raise StartError("a dialog is still open after saving")


def close_design(steps, design, folder, status, log):
    """Close the design this command opened, once. Never with unsaved changes:
    the runner's close step refuses those (no discard), so they stay open."""
    if not status.get("opened_here") or status.get("design_closed"):
        return
    status["design_closed"] = True
    try:
        ok, out = steps.run(rs.doc_script("close", design, folder))
        log((out or "").strip() if ok else "left %s open: %s" % (design, (out or "").strip()[:200]))
    except (StartError, rs.McpError) as e:
        log("couldn't close %s: %s" % (design, e))


def run_with_cleanup(steps, design, name, folder, sheet, keep_open, log, waits=None):
    """start_drawing plus cleanup; returns the exit code."""
    status = {}
    try:
        start_drawing(steps, design, name, folder, sheet, keep_open, log, waits, status)
        log("done: %s" % name)
        return 0
    except (StartError, rs.McpError, KeyboardInterrupt) as e:
        kind = "lost contact with Fusion" if isinstance(e, rs.McpError) else \
            "stopped" if isinstance(e, KeyboardInterrupt) else "FAILED"
        print("start_drawing: %s: %s" % (kind, e), file=sys.stderr)
        if not status.get("queued"):
            if not isinstance(e, rs.McpError):
                close_design(steps, design, folder, status, log)   # Reviewer 5, P3 on #101
            return 2 if isinstance(e, rs.McpError) else 1
        idle = cancel_dialogs(steps, log)
        if not idle:
            print("start_drawing: Fusion may still have a dialog open: press Cancel in Fusion",
                  file=sys.stderr)
            return 4
        if not status.get("saved"):
            try:
                ok, out = steps.run(CLOSE_UNSAVED_SCRIPT)
                if out:
                    log(out.strip())
            except (StartError, rs.McpError) as e2:
                print("start_drawing: couldn't close the unsaved drawing: %s" % e2, file=sys.stderr)
        close_design(steps, design, folder, status, log)          # Reviewer 5, P3 on #101
        return 2 if isinstance(e, rs.McpError) else 1


def _stop(_signum, _frame):
    raise KeyboardInterrupt


def install_signal_handlers():
    """A kill (SIGTERM, SIGHUP, a tool timeout) counts as a failure with cleanup."""
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGHUP, _stop)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Start a new Fusion drawing of a saved design, "
                                             "with nobody at the Mac (see the module help).")
    ap.add_argument("design", help="the saved design's name in --folder")
    ap.add_argument("drawing", help="name for the new drawing, e.g. PARTNO_P01_NAME_DWG")
    ap.add_argument("--folder", default=rs.DEFAULT_FOLDER)
    ap.add_argument("--sheet", default="A2", choices=sorted(SHEETS))
    ap.add_argument("--keep-open", action="store_true", help="leave the drawing open")
    ap.add_argument("--url", default=rs.DEFAULT_URL)
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds per Fusion call")
    ap.add_argument("--lock", default=None)
    ap.add_argument("--lock-wait", type=float, default=1200.0)
    ap.add_argument("--lock-front", default="", metavar="REASON",
                    help="go ahead of every waiting run (never ahead of the run holding the "
                         "lock); only for runs the Product Manager approved, see run_script.py")
    ap.add_argument("--label", default=os.environ.get(rs.LABEL_ENV, ""))
    opts = ap.parse_args(argv)

    def log(msg):
        print("start_drawing: %s" % msg, flush=True)

    install_signal_handlers()
    lock = rs.FusionLock(opts.lock or rs.default_lock_path(opts.url),
                         label=opts.label or "start_drawing", hold_s=900,
                         script="start_drawing.py %s -> %s" % (opts.design, opts.drawing),
                         front=opts.lock_front)
    try:
        lock.acquire(opts.lock_wait, token=os.environ.get(rs.TOKEN_ENV) or None)
    except rs.LockTimeout as e:
        print("start_drawing: %s" % e, file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("start_drawing: stopped while waiting for the Fusion lock", file=sys.stderr)
        return 3
    try:
        try:
            steps = Steps(opts.url, opts.timeout)
        except rs.McpError as e:
            print("start_drawing: %s" % e, file=sys.stderr)
            return 2
        return run_with_cleanup(steps, opts.design, opts.drawing, opts.folder, opts.sheet,
                                opts.keep_open, log)
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
