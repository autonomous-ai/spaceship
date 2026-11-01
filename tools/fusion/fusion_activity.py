#!/usr/bin/env python3
"""Is Fusion still working? Check before any force-quit.

    python3 tools/fusion/fusion_activity.py [--minutes 3] [--cpu-seconds 10] [--log FILE]

PM rule (2026-11-01): before a safe restart, read Fusion's log for live
activity, and restart only when it shows none. That night a run that looked
hung (CPU near 0, only the Home page on screen) was in fact busy: Fusion's log
showed it fetching the team folder's listing every 2 seconds for 15 minutes.
A run that was really stuck (a drawing open that never ended) left only
background lines (heartbeats, health checks, menu refreshes) and used no CPU.

So this looks at two things: the work lines of the last --minutes in the
newest AppLogFile*.log in Fusion's log folder (cloud work requests, folder
listing fetches, document opens and saves, workflow starts and ends; not the
background lines), and the CPU Fusion uses over --cpu-seconds (local work,
such as rebuilding a design, logs little but uses CPU).
Exit 0: ACTIVE (work lines, or CPU at 5 % or more): don't restart.
Exit 1: QUIET (neither): a restart may be needed; the Product Manager decides.
Exit 2: no Fusion log or no Fusion process found.
It prints counts only, never log text (the log holds account names).
Standard library only.
"""

import argparse
import datetime
import glob
import os
import re
import subprocess
import sys
import time

LOG_GLOB = os.path.expanduser("~/Library/Application Support/Autodesk/Autodesk Fusion 360/*/logs/AppLogFile*.log")
FUSION_BIN = "/Autodesk Fusion.app/Contents/MacOS/Autodesk Fusion"
LINE_RE = re.compile(r"^(\d{8}T\d{6}) (\w) (\S+) (.*)$")
# cloud work, by Fusion's own workflow tag; health checks, heartbeats and menu data aren't work
BACKGROUND_WORKFLOWS = ("HTTPClient", "SLM_heartbeat", "PushNotificationManager", "HUBFLAGS",
                        "getRecommendedHubs", "Extensions", "updateExtraInfo")
WORKFLOW_RE = re.compile(r"workflow:([A-Za-z0-9_.:-]+)")
FOLDER_FETCH = "Symphonydm::getFolderContents"
STEP_RE = re.compile(r"Workflow (start|end):|documentOpened|\[(Open|ACS|JointConstraint)\]|TextCmdPythonRun")
CPU_BUSY = 5.0          # per cent of one core over the sample


def newest_log(pattern=LOG_GLOB):
    logs = glob.glob(pattern)
    return max(logs, key=os.path.getmtime) if logs else None


def work_counts(lines, now, minutes):
    """{"folder": n, "cloud": n, "steps": n, "last": datetime or None} for the work lines
    of the last `minutes` before now (Fusion's log uses the Mac's local time)."""
    start = now - datetime.timedelta(minutes=minutes)
    c = {"folder": 0, "cloud": 0, "steps": 0, "last": None}
    for line in lines:
        m = LINE_RE.match(line.rstrip("\n"))
        if not m:
            continue
        try:
            t = datetime.datetime.strptime(m.group(1), "%Y%m%dT%H%M%S")
        except ValueError:
            continue
        if t < start or t > now + datetime.timedelta(minutes=1):
            continue
        text = m.group(4)
        w = WORKFLOW_RE.search(text)
        if w and not w.group(1).startswith(BACKGROUND_WORKFLOWS):
            c["folder" if w.group(1).startswith(FOLDER_FETCH) else "cloud"] += 1
        elif STEP_RE.search(text):
            c["steps"] += 1
        else:
            continue
        c["last"] = t
    return c


def fusion_pid():
    """Fusion's process number (read only: never used to stop anything by name)."""
    out = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True, text=True).stdout
    pids = [int(l.split(None, 1)[0]) for l in out.splitlines() if l.strip().endswith(FUSION_BIN)]
    return pids[0] if len(pids) == 1 else None


def parse_cpu_time(text):
    """ps's cumulative CPU time ("[[dd-]hh:]mm:ss.ss") in seconds."""
    days, _, rest = text.strip().rpartition("-")
    secs = 0.0
    for part in rest.split(":"):
        secs = secs * 60 + float(part)
    return secs + (float(days) * 86400 if days else 0.0)


def cpu_seconds(pid):
    out = subprocess.run(["ps", "-o", "time=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return parse_cpu_time(out) if out else None


def cpu_percent(pid, seconds, sleep=time.sleep):
    a = cpu_seconds(pid)
    sleep(seconds)
    b = cpu_seconds(pid)
    if a is None or b is None:
        return None
    return 100.0 * (b - a) / seconds


def verdict(counts, cpu, minutes, seconds):
    work = counts["folder"] + counts["cloud"] + counts["steps"]
    busy_cpu = cpu is not None and cpu >= CPU_BUSY
    what = ("%d work lines in the last %g min (%d folder listing fetches, %d other cloud requests, "
            "%d open/save/workflow steps)%s; CPU %s over %g s"
            % (work, minutes, counts["folder"], counts["cloud"], counts["steps"],
               "; last at %s" % counts["last"].strftime("%H:%M:%S") if counts["last"] else "",
               "%.1f %%" % cpu if cpu is not None else "unknown", seconds))
    if work or busy_cpu:
        return 0, "ACTIVE, don't restart: " + what
    return 1, "QUIET: " + what + " (a restart may be needed; the Product Manager decides)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--minutes", type=float, default=3.0)
    ap.add_argument("--cpu-seconds", type=float, default=10.0)
    ap.add_argument("--log", default=None, help="Fusion's log file (default: the newest)")
    opts = ap.parse_args(argv)
    log = opts.log or newest_log()
    pid = fusion_pid()
    if not log or not os.path.isfile(log) or pid is None:
        print("fusion_activity: no Fusion %s found" % ("log" if not log or not os.path.isfile(log) else "process"))
        return 2
    with open(log, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    cpu = cpu_percent(pid, opts.cpu_seconds)
    code, text = verdict(work_counts(lines, datetime.datetime.now(), opts.minutes), cpu, opts.minutes,
                         opts.cpu_seconds)
    print("fusion_activity: %s" % text)
    return code


if __name__ == "__main__":
    sys.exit(main())
