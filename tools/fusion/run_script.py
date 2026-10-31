#!/usr/bin/env python3
"""Run a Fusion API script file through Fusion's built-in MCP server.

Fusion (Autodesk Fusion with the "MCP Server Adapter") answers only on this
machine, at http://127.0.0.1:27182/mcp. This tool sends a script file to it
(JSON-RPC `initialize`, then `tools/call` of `fusion_mcp_execute` with
featureType "script") and prints what the script printed.

The script must define `run(_context)`. It runs inside Fusion, on the ACTIVE
document of the one Fusion app.

One run at a time: the Fusion lock
  Every run takes a machine-wide lock first (a directory made with mkdir,
  which is atomic, default /tmp/fusion-mcp-27182.lock) and keeps it for the
  whole run: document steps, script and screenshot. Other runs wait for it,
  printing who holds it, and give up after --lock-wait seconds (exit 3). The
  lock is removed at the end, also on an error, Ctrl-C or SIGTERM. A lock
  whose run has died (its process is gone) or that is past its expiry is
  cleared by the next run that waits for it.
  For steps that must stay together across several runs (for example a
  script, then a click in Fusion, then another script), hold the lock:
      export FUSION_MCP_LOCK_TOKEN=$(python3 tools/fusion/run_script.py --lock-hold 900)
      python3 tools/fusion/run_script.py step1.py ...   # runs inside the held lock
      python3 tools/fusion/run_script.py --lock-release
  --lock-status prints who holds the lock now.
  Waiting runs are served oldest first. --lock-front REASON puts a run ahead
  of every waiting run (never ahead of the run that holds the lock; it waits
  for that one to end like everyone). It is only for runs the Product Manager
  approved in the project chat; REASON names that approval, and every waiting
  run sees it.

Your own document, by name
  --doc NAME activates the open document called NAME, or opens it from the
  cloud folder (--folder, default "Default Project/FocusPod v2"), before the
  script runs; --doc-new also makes it (a new mm parametric design, saved as
  NAME in that folder) when it doesn't exist yet. After the script and the
  screenshot, --save saves it (a new version) and --close closes it. --close
  refuses to drop unsaved changes unless --discard is given. So a run can
  open its own document, change it, save and close, and leave Fusion as it
  found it for the next run.

Examples
  python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/wall_panel_frame.py
  python3 tools/fusion/run_script.py my_check.py --read-only
  python3 tools/fusion/run_script.py build.py --arg stop_after=3 \
      --screenshot /tmp/step3.png --direction iso-top-right
  python3 tools/fusion/run_script.py add_feature.py --doc PARTNO_P01_NAME_CAD \
      --save "add the rail holes" --close

Script arguments
  Every --arg KEY=VALUE, plus repo_root (the repository root, found from this
  file's location) and script_path, reaches the script as the dict
  SCRIPT_ARGS (values are strings). The script also gets __file__. The file
  is compiled under its real path inside a small wrapper, so tracebacks show
  the real file name and line numbers.

Exit code 0 when the script ran without an exception, 1 when it (or a
document step) raised one (the traceback is printed), 2 when Fusion's MCP
could not be reached, 3 when the Fusion lock could not be taken in time.
Standard library only.
"""

import argparse
import base64
import datetime
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

DEFAULT_URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")
DEFAULT_FOLDER = "Default Project/FocusPod v2"
PROTOCOL_VERSION = "2025-06-18"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LOCK_ENV = "FUSION_MCP_LOCK"           # lock directory, to override the default
# A front-of-queue ticket is stamped this much earlier than now (about 32
# years), so it sorts before every waiting ticket, also for runners from
# before --lock-front, which serve ticket names in plain sorted order.
FRONT_SHIFT_NS = 10 ** 18
TOKEN_ENV = "FUSION_MCP_LOCK_TOKEN"    # run inside a lock held with --lock-hold
LABEL_ENV = "FUSION_MCP_LABEL"         # who is running, shown to waiting runs
OWNER_FILE = "owner.json"
NO_OWNER_GRACE_S = 60      # a lock without owner file older than this is stale
GUARD_STALE_S = 60         # a leftover guard directory older than this is removed
TICKET_GRACE_S = 60        # a ticket this long past its run's give-up time is dropped
HOLD_MAX_S = 3600          # longest --lock-hold


# ---------------------------------------------------------------------------
# The Fusion lock
# ---------------------------------------------------------------------------

class LockTimeout(Exception):
    pass


def default_lock_path(url=DEFAULT_URL):
    """One lock per Fusion MCP port, shared by every checkout on this Mac."""
    if os.environ.get(LOCK_ENV):
        return os.environ[LOCK_ENV]
    port = urllib.parse.urlparse(url).port or 80
    return "/tmp/fusion-mcp-%s.lock" % port


def _utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC")


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:      # exists, belongs to someone else
        return True
    except (OSError, ValueError, TypeError):
        return False
    return True


def describe_owner(owner, now=None):
    if not owner:
        return "a run that is just starting (no owner file yet)"
    now = time.time() if now is None else now
    who = owner.get("label") or "a run"
    what = owner.get("script") or "held lock"
    mins = max(0, int((now - owner.get("since", now)) // 60))
    text = "%s (%s, pid %s) since %s, %d min ago" % (
        who, what, owner.get("pid") or "none, held", owner.get("since_utc", "?"), mins)
    if owner.get("front"):
        text += "; went first in the queue: %s" % owner["front"]
    joined = owner.get("joined")
    if isinstance(joined, dict) and pid_alive(joined.get("pid")):
        text += "; now running %s (pid %s)" % (joined.get("script", "?"), joined.get("pid", "?"))
    return text


class FusionLock:
    """An atomic mkdir lock with an owner file, a wait in a queue, stale clearing.

    pid is the process that keeps the lock alive: this run (default), or None
    for a lock held across runs with --lock-hold (then only `expires` ends it;
    each run that joins the hold moves `expires` out to cover itself).
    Waiters queue: each makes a ticket in <lock>.queue and only the oldest
    live ticket may take the lock, so nobody loses every race.
    """

    def __init__(self, path, label="", script="", hold_s=3600.0, pid="self",
                 host=None, log=None, front=""):
        self.path = path
        self.front = (front or "").strip()   # --lock-front: why this run goes first
        self.queue_dir = path + ".queue"
        self.guard = path + ".guard"
        self.label = label
        self.script = script
        self.hold_s = float(hold_s)
        self.pid = os.getpid() if pid == "self" else pid
        self.host = host or socket.gethostname()   # for people reading the file only
        self.log = log or (lambda msg: print(msg, file=sys.stderr, flush=True))
        self.token = None
        self.ticket = None
        self.owned = False       # we made the lock directory
        self.joined = False      # we run inside a lock held with --lock-hold
        self._said = set()       # messages logged once

    # -- reading ------------------------------------------------------------
    def read_owner(self):
        try:
            with open(os.path.join(self.path, OWNER_FILE), "r", encoding="utf-8") as fh:
                owner = json.load(fh)
            return owner if isinstance(owner, dict) else None
        except (OSError, ValueError):
            return None

    def exists(self):
        """Anything at the lock path counts as held, even if it isn't our lock."""
        return os.path.lexists(self.path)

    def is_foreign(self):
        """Something at the path that this tool didn't make (a file, a link)."""
        return self.exists() and (os.path.islink(self.path) or not os.path.isdir(self.path))

    def describe(self, owner, now=None):
        if self.is_foreign():
            return "something that is not a Fusion lock (a file or a link): remove %s" % self.path
        return describe_owner(owner, now)

    def stale_reason(self, owner, now=None):
        """Why the lock as described by `owner` is stale, or None if it is live."""
        now = time.time() if now is None else now
        if self.is_foreign():
            return None                       # held by something unknown; never touched
        if owner is None:
            try:
                age = now - os.lstat(self.path).st_mtime
            except OSError:
                return None
            return ("no owner file for %d s" % age) if age > NO_OWNER_GRACE_S else None
        expires = owner.get("expires")
        if not isinstance(expires, (int, float)) or now > expires:
            return "expired at %s" % owner.get("expires_utc", expires)
        pid = owner.get("pid")
        # /tmp is local to this Mac, so a pid is checked whatever hostname it reports
        if pid and not pid_alive(pid):
            return "its process %s has ended" % pid
        return None

    def _say_once(self, msg, key=None):
        key = key or msg
        if key not in self._said:
            self._said.add(key)
            self.log(msg)

    # -- the guard: one clearer or extender at a time -------------------------
    def _take_guard(self, wait_s=5.0):
        t0 = time.time()
        while True:
            try:
                os.mkdir(self.guard)
                return True
            except FileExistsError:
                try:
                    if time.time() - os.lstat(self.guard).st_mtime > GUARD_STALE_S:
                        os.rmdir(self.guard)
                        continue
                except OSError:
                    pass
            except OSError as e:
                self._say_once("run_script: can't make %s (%s)" % (self.guard, e))
                return False
            if time.time() - t0 >= wait_s:
                return False
            time.sleep(0.05)

    def _drop_guard(self):
        try:
            os.rmdir(self.guard)
        except OSError:
            pass

    # -- the queue ------------------------------------------------------------
    def _take_ticket(self, deadline):
        os.makedirs(self.queue_dir, exist_ok=True)
        stamp = time.time_ns() - (FRONT_SHIFT_NS if self.front else 0)
        name = "%020d-%d-%s" % (stamp, os.getpid(), uuid.uuid4().hex[:8])
        fd = os.open(os.path.join(self.queue_dir, name), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            ticket = {"pid": os.getpid(), "label": self.label, "script": self.script,
                      "give_up": deadline}
            if self.front:
                ticket["front"] = self.front
            json.dump(ticket, fh)
        self.ticket = name

    def _drop_ticket(self):
        if self.ticket:
            try:
                os.remove(os.path.join(self.queue_dir, self.ticket))
            except OSError:
                pass
            self.ticket = None

    def queue(self, now=None):
        """Live tickets, oldest first. Tickets of ended runs are removed."""
        now = time.time() if now is None else now
        try:
            names = sorted(os.listdir(self.queue_dir))
        except OSError:
            return []
        live = []
        for n in names:
            parts = n.split("-")
            if len(parts) != 3 or not parts[0].isdigit() or not parts[1].isdigit():
                continue
            if n != self.ticket:
                try:
                    with open(os.path.join(self.queue_dir, n), "r", encoding="utf-8") as fh:
                        give_up = float(json.load(fh).get("give_up", 0))
                except (OSError, ValueError, TypeError, AttributeError):
                    give_up = None              # still being written; keep it
                dead = not pid_alive(int(parts[1])) or (
                    give_up is not None and now > give_up + TICKET_GRACE_S)
                if dead:
                    try:
                        os.remove(os.path.join(self.queue_dir, n))
                    except OSError:
                        pass
                    continue
            live.append(n)
        return live

    def front_waiting(self):
        """(label, reason) of the waiting runs that go first (--lock-front)."""
        out = []
        for n in self.queue():
            try:
                with open(os.path.join(self.queue_dir, n), "r", encoding="utf-8") as fh:
                    t = json.load(fh)
            except (OSError, ValueError):
                continue
            if isinstance(t, dict) and t.get("front"):
                out.append((t.get("label") or "a run", t["front"]))
        return out

    # -- taking and giving back --------------------------------------------
    def _write_owner(self, owner):
        tmp = os.path.join(self.path, "%s.%s.tmp" % (OWNER_FILE, uuid.uuid4().hex[:8]))
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(owner, fh, indent=1)
        os.replace(tmp, os.path.join(self.path, OWNER_FILE))

    def acquire(self, wait_s, poll_s=1.0, token=None, note_every_s=30.0):
        if token:
            return self._join(token)
        deadline = time.time() + float(wait_s)
        last_note = 0.0
        self._take_ticket(deadline)
        try:
            while True:
                q = self.queue()
                if self.ticket not in q:          # removed by someone: take a new one
                    self._take_ticket(deadline)
                    q = self.queue()
                ahead = q.index(self.ticket) if self.ticket in q else 0
                owner = None
                if ahead == 0:
                    try:
                        os.mkdir(self.path)
                    except FileExistsError:
                        owner = self.read_owner()
                        why = self.stale_reason(owner)
                        if why and self._clear_stale(owner, why):
                            continue              # the path is gone: try again at once
                    except OSError as e:
                        self._say_once("run_script: can't make the lock %s (%s)" % (self.path, e))
                    else:
                        return self._own()
                else:
                    owner = self.read_owner()
                now = time.time()
                if now >= deadline:
                    raise LockTimeout("Fusion is busy: the lock %s is held by %s%s" % (
                        self.path, self.describe(owner, now),
                        ("; %d run(s) were ahead in the queue" % ahead) if ahead else ""))
                if now - last_note >= note_every_s:
                    self.log("run_script: waiting for Fusion, held by %s%s; giving up in %d s"
                             % (self.describe(owner, now),
                                ("; %d run(s) ahead in the queue" % ahead) if ahead else "",
                                deadline - now))
                    last_note = now
                time.sleep(max(0.01, min(poll_s, deadline - now)))
        finally:
            self._drop_ticket()

    def _own(self):
        try:
            self.token = uuid.uuid4().hex
            now = time.time()
            owner = {
                "token": self.token, "label": self.label, "script": self.script,
                "pid": self.pid, "host": self.host,
                "since": now, "since_utc": _utc(now),
                "expires": now + self.hold_s, "expires_utc": _utc(now + self.hold_s),
            }
            if self.front:
                owner["front"] = self.front
            self._write_owner(owner)
        except BaseException:
            shutil.rmtree(self.path, ignore_errors=True)
            raise
        self.owned = True
        return owner

    def _join(self, token):
        """Run inside a held lock: check the token and move the expiry out far
        enough to cover this run, under the guard, so no waiter can clear the
        hold while this run is in Fusion."""
        if not self._take_guard():
            raise LockTimeout("couldn't check the held Fusion lock %s (its guard %s is busy)"
                              % (self.path, self.guard))
        try:
            owner = self.read_owner()
            if not owner or owner.get("token") != token:
                raise LockTimeout("%s is set, but the Fusion lock %s is not held with that "
                                  "token (it is held by %s)" % (
                                      TOKEN_ENV, self.path,
                                      self.describe(owner) if self.exists() else "nobody"))
            why = self.stale_reason(owner)
            if why:
                raise LockTimeout("the held Fusion lock %s is stale (%s); hold it again"
                                  % (self.path, why))
            now = time.time()
            if owner["expires"] < now + self.hold_s:
                owner["expires"] = now + self.hold_s
                owner["expires_utc"] = _utc(owner["expires"])
            owner["joined"] = {"label": self.label, "script": self.script,
                               "pid": os.getpid(), "since_utc": _utc(now)}
            self._write_owner(owner)
        finally:
            self._drop_guard()
        self.token = token
        self.joined = True
        return owner

    def _unjoin(self):
        if not self._take_guard():
            return
        try:
            owner = self.read_owner()
            joined = owner.get("joined") if owner else None
            if owner and owner.get("token") == self.token and isinstance(joined, dict) \
                    and joined.get("pid") == os.getpid():
                del owner["joined"]
                self._write_owner(owner)
        finally:
            self._drop_guard()

    def _clear_stale(self, seen, why):
        """Remove a stale lock, unless it changed hands since we looked.
        True only when the path is really gone."""
        if not self._take_guard(wait_s=0.5):
            return False
        try:
            cur = self.read_owner()
            same = (cur is None and seen is None) or (
                cur is not None and seen is not None and cur.get("token") == seen.get("token"))
            if not (same and self.stale_reason(cur)):
                return False
            if os.path.isdir(self.path) and not os.path.islink(self.path):
                shutil.rmtree(self.path, ignore_errors=True)
            if self.exists():
                self._say_once("run_script: can't clear the stale Fusion lock %s (%s): "
                               "remove it by hand; waiting until --lock-wait runs out"
                               % (self.path, why), key="cant-clear")
                return False
            self.log("run_script: cleared a stale Fusion lock (%s), left by %s"
                     % (why, describe_owner(seen)))
            return True
        finally:
            self._drop_guard()

    def release(self):
        """Give the lock back if we made it and still own it. A run that joined a
        held lock leaves the hold in place and only takes its "now running" note out."""
        if self.joined:
            self.joined = False
            self._unjoin()
            return False
        if not self.owned:
            return False
        self.owned = False
        cur = self.read_owner()
        if cur and cur.get("token") == self.token:
            shutil.rmtree(self.path, ignore_errors=True)
            return True
        self.log("run_script: the Fusion lock changed hands while this run held it "
                 "(cleared as stale?); left as it is")
        return False

    def release_held(self, token):
        """--lock-release: remove a lock held with --lock-hold, by its token."""
        cur = self.read_owner()
        if not cur or cur.get("token") != token:
            return False
        shutil.rmtree(self.path, ignore_errors=True)
        return True


# ---------------------------------------------------------------------------
# MCP client
# ---------------------------------------------------------------------------

class McpError(Exception):
    pass


class FusionMcp:
    """Minimal MCP client for Fusion's local Streamable HTTP server."""

    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.session_id = None
        self.next_id = 1

    def _post(self, payload, expect_reply=True):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
            headers["MCP-Protocol-Version"] = PROTOCOL_VERSION
        req = urllib.request.Request(
            self.url, data=json.dumps(payload).encode("utf-8"),
            headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.session_id = sid
                body = resp.read().decode("utf-8", errors="replace")
                ctype = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            raise McpError("HTTP %s from %s: %s" % (
                e.code, self.url, e.read().decode("utf-8", "replace")[:500]))
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise McpError("cannot reach Fusion MCP at %s (%s). Is Fusion "
                           "running with the MCP Server Adapter on?" % (self.url, e))
        if not expect_reply:
            return None
        return self._parse(body, ctype, payload.get("id"))

    @staticmethod
    def _parse(body, ctype, want_id):
        if "text/event-stream" in ctype:
            # Streamable HTTP may answer as server-sent events: one JSON-RPC
            # message per "data:" block. Keep the one that answers our id.
            msgs, buf = [], []
            for line in body.splitlines():
                if line.startswith("data:"):
                    buf.append(line[5:].strip())
                elif not line.strip() and buf:
                    msgs.append("\n".join(buf))
                    buf = []
            if buf:
                msgs.append("\n".join(buf))
            for m in msgs:
                try:
                    obj = json.loads(m)
                except ValueError:
                    continue
                if obj.get("id") == want_id:
                    return obj
            raise McpError("no reply for request %s in event stream" % want_id)
        return json.loads(body)

    def request(self, method, params):
        rid = self.next_id
        self.next_id += 1
        reply = self._post({"jsonrpc": "2.0", "id": rid, "method": method,
                            "params": params})
        if "error" in reply:
            raise McpError("%s failed: %s" % (method, json.dumps(reply["error"])))
        return reply.get("result", {})

    def initialize(self):
        self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "spaceship-run-script", "version": "1.1"},
        })
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"},
                   expect_reply=False)

    def call_tool(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})


def tool_payload(result):
    """Return (text_json_or_None, image_bytes_or_None) from a tools/call result."""
    text, image = None, None
    for item in result.get("content", []):
        if item.get("type") == "text" and text is None:
            text = item.get("text", "")
        elif item.get("type") == "image" and image is None:
            image = base64.b64decode(item.get("data", ""))
    parsed = None
    if text:
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = {"message": text, "success": not result.get("isError")}
    if image is None and isinstance(parsed, dict) and parsed.get("base64Data"):
        image = base64.b64decode(parsed["base64Data"])
    return parsed, image


VIEWS = {
    "front": "FrontViewOrientation", "back": "BackViewOrientation",
    "top": "TopViewOrientation", "bottom": "BottomViewOrientation",
    "left": "LeftViewOrientation", "right": "RightViewOrientation",
    "iso-top-right": "IsoTopRightViewOrientation", "iso-top-left": "IsoTopLeftViewOrientation",
    "iso-bottom-right": "IsoBottomRightViewOrientation",
    "iso-bottom-left": "IsoBottomLeftViewOrientation",
}

# Turns the camera and zooms to fit; changes the view only, not the design.
FIT_SCRIPT = '''import adsk.core
def run(_context):
    vp = adsk.core.Application.get().activeViewport
    cam = vp.camera
    cam.viewOrientation = adsk.core.ViewOrientations.%(view)s
    cam.isFitView = True
    cam.isSmoothTransition = False
    vp.camera = cam
    vp.fit()
    vp.refresh()
'''

# The shared folder check (fusion_folder.py): put in front of the scripts this
# runner and start_drawing.py send, and given to every script as a module.
FOLDER_HELPER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fusion_folder.py")
with open(FOLDER_HELPER_PATH, encoding="utf-8") as _fh:
    FOLDER_HELPER_SRC = _fh.read()


# Document steps for --doc, --save and --close. Runs inside Fusion; ARGS is
# filled in by doc_script(). It never closes or saves a document with
# another name, and never calls close(True) (that opens a dialog).
DOC_SCRIPT = '''import adsk.core, adsk.fusion, time
ARGS = %(args)r

def _folder(app, path):
    parts = [p for p in path.split("/") if p]
    proj = None
    for i in range(app.data.dataProjects.count):
        p = app.data.dataProjects.item(i)
        if p.name == parts[0]:
            proj = p
            break
    if proj is None:
        raise RuntimeError("no Fusion project called %%r" %% parts[0])
    folder = proj.rootFolder
    for name in parts[1:]:
        nxt = folder.dataFolders.itemByName(name)
        if nxt is None:
            raise RuntimeError("no folder %%r in %%r" %% (name, path))
        folder = nxt
    return proj, folder

def _open_doc(app, name):
    docs = [app.documents.item(i) for i in range(app.documents.count)]
    docs = [d for d in docs if d.name == name]
    if len(docs) > 1:
        raise RuntimeError("%%d open documents are called %%r; close the extra ones "
                           "first" %% (len(docs), name))
    return docs[0] if docs else None

def run(_context):
    app = adsk.core.Application.get()
    name, mode = ARGS["name"], ARGS["mode"]
    doc = _open_doc(app, name)
    if mode == "open":
        if doc is not None:
            doc.activate()
            print("run_script: activated %%r" %% name)
            return
        proj, folder = _folder(app, ARGS["folder"])
        # the shared check (fusion_folder.py, in front of this script): reads
        # again for up to a minute while an entry can't be read, unless the
        # name turns up
        found, unknown, others = read_folder(folder, stop_when=lambda fs, u, o: name in fs or (
            ARGS.get("create") and not could_be(u, o, "f3d")))
        files = found.get(name, [])
        bad = unknown + [t for items in others.values() for t in items]
        if bad:
            print("run_script: %%d entr%%s of %%s could not be read; skipped: %%s" %% (
                len(bad), "y" if len(bad) == 1 else "ies", ARGS["folder"], "; ".join(bad)))
        if not files and ARGS.get("create"):
            risky = could_be(unknown, others, "f3d")      # --doc-new makes a design
            if risky:
                raise RuntimeError("%%r is not in %%s, but %%s there can't be read and could be it; "
                                   "nothing was opened or made (try again later): %%s" %% (
                                       name, ARGS["folder"], "an entry" if len(risky) == 1 else
                                       "%%d entries" %% len(risky), "; ".join(risky)))
        if len(files) > 1:
            raise RuntimeError("%%d files are called %%r in %%s" %% (len(files), name, ARGS["folder"]))
        if files:
            app.data.activeProject = proj
            # a version saved a moment ago may not open yet (live 2026-10-31, 4 s after
            # a save and close: "Missing key for PIMOpenWorkflowTracker"): try again
            # every 10 s for up to a minute, then give the error. Each new try looks the
            # file up afresh and opens its latest version: the same reference kept
            # failing for a full minute (live 2026-10-31, the #140 batch test)
            target = files[0]
            for attempt in range(7):
                try:
                    doc = app.documents.open(target, True)
                    break
                except Exception as e:
                    if attempt == 6:
                        raise
                    print("run_script: opening %%r failed (%%s); looking it up again in 10 s" %% (
                        name, str(e).strip().splitlines()[-1][:120] if str(e).strip() else type(e).__name__))
                    adsk.doEvents()
                    time.sleep(10)
                    again, _u, _o = read_folder(folder, wait_s=0, stop_when=lambda fs, u, o: name in fs)
                    fresh = again.get(name) or files
                    try:
                        target = fresh[0].latestVersion or fresh[0]
                    except Exception:
                        target = fresh[0]
            if doc is None:
                raise RuntimeError("could not open %%r from %%s" %% (name, ARGS["folder"]))
            doc.activate()
            print("run_script: opened %%r (version %%s) from %%s" %% (
                name, target.versionNumber, ARGS["folder"]))
            return
        if not ARGS.get("create"):
            raise RuntimeError("%%r is not open and not in %%s%%s (add --doc-new to make it)"
                               %% (name, ARGS["folder"], " (some entries there can't be read)" if bad else ""))
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(doc.products.itemByProductType("DesignProductType"))
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = \\
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        app.data.activeProject = proj
        if not doc.saveAs(name, folder, "new, made by run_script.py --doc-new", ""):
            raise RuntimeError("saveAs %%r into %%s failed" %% (name, ARGS["folder"]))
        doc.activate()
        print("run_script: made %%r, a new mm parametric design, saved in %%s"
              %% (name, ARGS["folder"]))
    elif mode == "save":
        if doc is None:
            raise RuntimeError("--save: %%r is not open (did the script close it?)" %% name)
        if not doc.isSaved:
            raise RuntimeError("--save: %%r has never been saved" %% name)
        if not doc.save(ARGS.get("description") or "saved by run_script.py"):
            raise RuntimeError("--save: saving %%r failed" %% name)
        print("run_script: saved %%r" %% name)
    elif mode == "close":
        if doc is None:
            print("run_script: %%r is already closed" %% name)
            return
        if doc.isModified and not ARGS.get("discard"):
            raise RuntimeError("--close: %%r has unsaved changes; add --save, or "
                               "--discard to drop them" %% name)
        if not doc.close(False):
            raise RuntimeError("--close: closing %%r failed" %% name)
        print("run_script: closed %%r" %% name)
    else:
        raise RuntimeError("unknown document step %%r" %% mode)
'''


def doc_script(mode, name, folder=DEFAULT_FOLDER, create=False, description="",
               discard=False):
    return FOLDER_HELPER_SRC + "\n" + DOC_SCRIPT % {"args": {
        "mode": mode, "name": name, "folder": folder, "create": bool(create),
        "description": description, "discard": bool(discard)}}


WRAPPER = '''import base64 as _b64, os as _os, sys as _sys, types as _types
# Fusion keeps Python modules loaded between runs, so a module another team's run
# imported would be used again by any run that imports the same name (live
# 2026-10-31: CEILING got AIR's older module). Before each script, drop every
# cached module whose file is in any worktree of this repo (main checkout
# included) or under /tmp, this run's own included, so every run imports its
# files fresh and a team's own edits show at once. Never __main__; Fusion's and
# Python's own modules are never touched; one odd module can't fail the run.
_TEAM = [_os.path.realpath(p) for p in %(team)r]
# never dropped, even under a team folder: Fusion's add-ins and install, and Python's own
_KEEP = [_os.path.realpath(p) for p in %(keep)r]
for _p in (getattr(_sys, "prefix", ""), getattr(_sys, "base_prefix", ""), _os.path.dirname(_os.__file__)):
    if _p:
        _KEEP.append(_os.path.realpath(_p))
try:
    import adsk as _adsk
    _KEEP.append(_os.path.realpath(_os.path.dirname(_os.path.dirname(_adsk.__file__))))
except Exception:
    pass

def _under(f, roots):
    return any(f == r or f.startswith(r.rstrip("/") + "/") for r in roots)

_dropped = []
for _n in list(_sys.modules):
    if _n == "__main__":
        continue
    try:
        _f = getattr(_sys.modules.get(_n), "__file__", None)
        if isinstance(_f, str) and _under(_os.path.realpath(_f), _TEAM) \
                and not _under(_os.path.realpath(_f), _KEEP):
            _sys.modules.pop(_n, None)
            _dropped.append(_n)
    except Exception:
        pass
if _dropped:
    print("run_script: dropped %%d cached team module(s), so this run imports its own files: %%s" %% (
        len(_dropped), ", ".join(sorted(_dropped)[:12])))
# the shared folder check, from this runner's repo, fresh on every run: a
# script's "from fusion_folder import safe_to_create" finds it (one copy for all)
_FF = _types.ModuleType("fusion_folder")
_FF.__file__ = %(ffpath)r
exec(compile(_b64.b64decode(%(ffsrc)r).decode("utf-8"), %(ffpath)r, "exec"), _FF.__dict__)
_sys.modules["fusion_folder"] = _FF
_SRC = _b64.b64decode(%(src)r).decode("utf-8")
_NS = {"__name__": "__fusion_script__", "__file__": %(path)r,
       "SCRIPT_ARGS": %(args)r}
exec(compile(_SRC, %(path)r, "exec"), _NS)

def run(context):
    return _NS["run"](context)
'''


def git_worktrees(repo_root=None):
    """Every worktree of this repo, the main checkout included (git worktree list)."""
    repo_root = repo_root or REPO_ROOT
    try:
        p = subprocess.run(["git", "-C", repo_root, "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=20)
        trees = [line.split(" ", 1)[1] for line in p.stdout.splitlines() if line.startswith("worktree ")]
        why = None if trees else (p.stderr.strip() or "no worktrees listed")
    except (OSError, subprocess.SubprocessError) as e:
        trees, why = [], str(e)
    if why:
        print("run_script: warning: git worktree list failed (%s); only this checkout and /tmp are "
              "cleared of cached modules" % why[:200], file=sys.stderr)
    return trees or [repo_root]


def team_roots(repo_root=None):
    """The folders whose cached modules the wrapper drops before a script: every
    worktree of this repo, the parent folder of every worktree but the main
    checkout (git lists it first), so a deleted worktree's modules still drop, and
    /tmp (where agents' scratch worktrees live)."""
    trees = git_worktrees(repo_root)
    parents = sorted({os.path.dirname(os.path.abspath(t)) for t in trees[1:]})
    home = os.path.realpath(os.path.expanduser("~"))

    def holds_home(root):            # never sweep the home folder or a folder above it
        r = os.path.realpath(root)
        return r == home or home.startswith(r.rstrip("/") + "/")

    return [r for r in trees + parents if not holds_home(r)] + ["/tmp", "/private/tmp"]


def keep_roots():
    """Folders whose modules are never dropped, even inside a team folder: Fusion's
    add-ins and install (Application Support/Autodesk). The wrapper adds Python's own
    and the adsk package's folders inside Fusion."""
    return [os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Autodesk")]


def wrap_script(source, path, args):
    """Wrap the file so it compiles under its real path (true line numbers)."""
    compile(source, path, "exec")  # fail fast on syntax errors, locally
    return WRAPPER % {"src": base64.b64encode(source.encode("utf-8")).decode("ascii"),
                      "path": path, "args": args, "ffpath": FOLDER_HELPER_PATH,
                      "ffsrc": base64.b64encode(FOLDER_HELPER_SRC.encode("utf-8")).decode("ascii"),
                      "team": team_roots(), "keep": keep_roots()}


def run_in_fusion(mcp, source, read_only=False):
    """Run one script; return (ok, text printed or error)."""
    obj = {"script": source}
    if read_only:
        obj["readOnly"] = True
    result = mcp.call_tool("fusion_mcp_execute", {"featureType": "script", "object": obj})
    parsed, _ = tool_payload(result)
    ok = bool(parsed and parsed.get("success")) and not result.get("isError")
    out = None
    if parsed:
        out = parsed.get("message") if ok else (parsed.get("error") or parsed.get("message"))
    return ok, out


def _emit(out):
    if out:
        sys.stdout.write(out if out.endswith("\n") else out + "\n")
        sys.stdout.flush()


def _sigterm(_signum, _frame):
    # Make SIGTERM and SIGHUP unwind like Ctrl-C, so the lock is given back.
    raise KeyboardInterrupt


def _repo_rel(path):
    try:
        rel = os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


def build_parser():
    ap = argparse.ArgumentParser(
        description="Run a Fusion API script file through Fusion's local MCP server, "
                    "one run at a time (see the module help).")
    ap.add_argument("script", nargs="?", help="Python file that defines run(_context)")
    ap.add_argument("--read-only", action="store_true",
                    help="tell Fusion the script only reads (it may then run "
                         "while a command dialog is open; writes will fail)")
    ap.add_argument("--arg", action="append", default=[], metavar="KEY=VALUE",
                    help="passed to the script in SCRIPT_ARGS (repeatable)")
    ap.add_argument("--screenshot", metavar="PNG",
                    help="after the script, save a screenshot of the active view")
    ap.add_argument("--direction", default="iso-top-right", choices=sorted(VIEWS) + ["current"],
                    help="camera for --screenshot (default iso-top-right); the view is "
                         "turned and zoomed to fit first, except for current")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--timeout", type=float, default=900.0,
                    help="seconds to wait for Fusion on each call (default 900)")
    ap.add_argument("--raw", action="store_true", help="print the raw tool reply")
    doc = ap.add_argument_group("your document")
    doc.add_argument("--doc", metavar="NAME",
                     help="before the script, activate the open document NAME or "
                          "open it from --folder")
    doc.add_argument("--doc-new", action="store_true",
                     help="with --doc: make NAME (new mm parametric design, saved "
                          "in --folder) if it doesn't exist")
    doc.add_argument("--folder", default=DEFAULT_FOLDER,
                     help="cloud folder as Project/Folder/... (default %(default)r)")
    doc.add_argument("--save", nargs="?", const="saved by run_script.py",
                     metavar="DESCRIPTION",
                     help="with --doc: after the script, save NAME as a new version")
    doc.add_argument("--close", action="store_true",
                     help="with --doc: at the end, close NAME")
    doc.add_argument("--discard", action="store_true",
                     help="with --close: close even with unsaved changes")
    lk = ap.add_argument_group("the Fusion lock")
    lk.add_argument("--lock", default=None, metavar="DIR",
                    help="lock directory (default $%s or /tmp/fusion-mcp-PORT.lock)"
                         % LOCK_ENV)
    lk.add_argument("--lock-wait", type=float, default=1200.0, metavar="S",
                    help="seconds to wait for the lock (default 1200), then exit 3")
    lk.add_argument("--label", default=os.environ.get(LABEL_ENV, ""),
                    help="who is running, shown to runs that wait (default $%s)"
                         % LABEL_ENV)
    lk.add_argument("--lock-front", default="", metavar="REASON",
                    help="go ahead of every waiting run (never ahead of the run holding "
                         "the lock). Only for runs the Product Manager approved in the "
                         "project chat; REASON names that approval and is shown to all")
    lk.add_argument("--lock-status", action="store_true",
                    help="print who holds the lock and exit")
    lk.add_argument("--lock-hold", type=float, metavar="S",
                    help="take the lock for S seconds (at most %d) across several "
                         "runs, print its token for $%s, and exit" % (HOLD_MAX_S, TOKEN_ENV))
    lk.add_argument("--lock-release", action="store_true",
                    help="give back the lock held with the token in $%s" % TOKEN_ENV)
    return ap


def lock_commands(opts, lock):
    """--lock-status, --lock-hold, --lock-release; returns an exit code."""
    if opts.lock_status:
        waiting = len(lock.queue())
        fronts = lock.front_waiting()
        queued = ("; %d run(s) waiting" % waiting) if waiting else ""
        if fronts:
            queued += " (%d going first: %s)" % (len(fronts), "; ".join(
                "%s, %s" % f for f in fronts))
        if not lock.exists():
            print("free: %s%s" % (lock.path, queued))
            return 0
        owner = lock.read_owner()
        why = lock.stale_reason(owner)
        print("held: %s by %s%s%s" % (lock.path, lock.describe(owner),
                                     ("; STALE (%s), the next run clears it" % why) if why else "",
                                     queued))
        return 0
    if opts.lock_hold is not None:
        if not 0 < opts.lock_hold <= HOLD_MAX_S:
            print("run_script: --lock-hold takes 1 to %d seconds" % HOLD_MAX_S, file=sys.stderr)
            return 3
        lock.pid = None
        lock.hold_s = opts.lock_hold
        lock.script = "held with --lock-hold for %d s" % opts.lock_hold
        try:
            lock.acquire(opts.lock_wait)
        except LockTimeout as e:
            print("run_script: %s" % e, file=sys.stderr)
            return 3
        print(lock.token)
        return 0
    token = os.environ.get(TOKEN_ENV, "")
    if not token:
        print("run_script: --lock-release needs $%s" % TOKEN_ENV, file=sys.stderr)
        return 3
    if lock.release_held(token):
        print("released: %s" % lock.path)
        return 0
    print("run_script: the lock %s is not held with that token" % lock.path, file=sys.stderr)
    return 3


def main(argv=None):
    ap = build_parser()
    opts = ap.parse_args(argv)
    lock_path = opts.lock or default_lock_path(opts.url)
    label = opts.label or "a run from %s" % os.path.basename(REPO_ROOT)
    if opts.lock_front and not opts.lock_front.strip():
        ap.error("--lock-front needs the reason: which approval in the project chat")
    lock = FusionLock(lock_path, label=label, front=opts.lock_front)

    if opts.lock_status or opts.lock_hold is not None or opts.lock_release:
        return lock_commands(opts, lock)
    if not opts.script:
        ap.error("give a script to run (or --lock-status, --lock-hold, --lock-release)")
    if (opts.doc_new or opts.save is not None or opts.close or opts.discard) and not opts.doc:
        ap.error("--doc-new, --save, --close and --discard work on the document named by --doc")

    script_path = os.path.abspath(opts.script)
    with open(script_path, "r", encoding="utf-8") as fh:
        source = fh.read()
    script_args = {"repo_root": REPO_ROOT, "script_path": script_path}
    for kv in opts.arg:
        if "=" not in kv:
            ap.error("--arg needs KEY=VALUE, got %r" % kv)
        k, v = kv.split("=", 1)
        script_args[k.strip()] = v
    source = wrap_script(source, script_path, script_args)

    # Expiry is only a backstop for a recycled pid: a live run keeps its lock
    # however long it takes, and a dead one is cleared at once.
    calls = 1 + (2 if opts.screenshot else 0) + (1 if opts.doc else 0) + \
        (1 if opts.save is not None else 0) + (1 if opts.close else 0)
    lock.script = "%s in %s" % (_repo_rel(script_path), REPO_ROOT)
    lock.hold_s = calls * opts.timeout + 300

    signal.signal(signal.SIGTERM, _sigterm)
    signal.signal(signal.SIGHUP, _sigterm)
    try:
        lock.acquire(opts.lock_wait, token=os.environ.get(TOKEN_ENV) or None)
    except LockTimeout as e:
        print("run_script: %s" % e, file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("run_script: stopped while waiting for the Fusion lock", file=sys.stderr)
        return 3
    try:
        return _run_locked(opts, source)
    except KeyboardInterrupt:
        print("run_script: stopped; Fusion lock given back. Fusion may still be "
              "running the script.", file=sys.stderr)
        return 1
    finally:
        lock.release()


def _run_locked(opts, source):
    mcp = FusionMcp(opts.url, opts.timeout)
    try:
        mcp.initialize()
        if opts.doc:
            ok, out = run_in_fusion(mcp, doc_script(
                "open", opts.doc, opts.folder, create=opts.doc_new))
            _emit(out)
            if not ok:
                print("run_script: --doc %r failed (see above); the script did not run"
                      % opts.doc, file=sys.stderr)
                return 1
        obj = {"script": source}
        if opts.read_only:
            obj["readOnly"] = True
        result = mcp.call_tool("fusion_mcp_execute",
                               {"featureType": "script", "object": obj})
    except McpError as e:
        print("run_script: %s" % e, file=sys.stderr)
        return 2

    parsed, _ = tool_payload(result)
    if opts.raw:
        print(json.dumps(result, indent=2)[:20000])
    ok = bool(parsed and parsed.get("success")) and not result.get("isError")
    if parsed:
        _emit(parsed.get("message") if ok else (parsed.get("error") or parsed.get("message")))
    if not ok:
        print("run_script: the script raised an exception (see above)", file=sys.stderr)

    shot_rc = 0
    if opts.screenshot:
        shot_rc = take_screenshot(mcp, opts)

    if opts.doc and ok:
        steps = []
        if opts.save is not None:
            steps.append(doc_script("save", opts.doc, opts.folder, description=opts.save))
        if opts.close:
            steps.append(doc_script("close", opts.doc, opts.folder, discard=opts.discard))
        for step in steps:
            try:
                sok, out = run_in_fusion(mcp, step)
            except McpError as e:
                print("run_script: %s" % e, file=sys.stderr)
                return 2
            _emit(out)
            if not sok:
                print("run_script: document step failed (see above)", file=sys.stderr)
                return 1
    elif opts.doc and (opts.save is not None or opts.close):
        print("run_script: the script failed, so %r was not saved or closed" % opts.doc,
              file=sys.stderr)
    if not ok:
        return 1
    return shot_rc


def take_screenshot(mcp, opts):
    """Save a screenshot; 0 when saved, 1 when no image came back, 2 on an MCP error."""
    try:
        if opts.direction != "current":
            mcp.call_tool("fusion_mcp_execute", {"featureType": "script", "object": {
                "script": FIT_SCRIPT % {"view": VIEWS[opts.direction]}}})
        shot = mcp.call_tool("fusion_mcp_read", {
            "queryType": "screenshot", "direction": "current",
            "width": opts.width, "height": opts.height,
            "transparentBackground": False, "antiAliasing": True})
    except McpError as e:
        print("run_script: screenshot failed: %s" % e, file=sys.stderr)
        return 2
    _, png = tool_payload(shot)
    if not png:
        print("run_script: no image in screenshot reply", file=sys.stderr)
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(opts.screenshot)), exist_ok=True)
    with open(opts.screenshot, "wb") as fh:
        fh.write(png)
    print("run_script: screenshot saved to %s" % opts.screenshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
