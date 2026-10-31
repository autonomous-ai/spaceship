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
TOKEN_ENV = "FUSION_MCP_LOCK_TOKEN"    # run inside a lock held with --lock-hold
LABEL_ENV = "FUSION_MCP_LABEL"         # who is running, shown to waiting runs
OWNER_FILE = "owner.json"
NO_OWNER_GRACE_S = 60      # a lock without owner file older than this is stale
CLEAR_GUARD_STALE_S = 60   # a leftover clearing guard older than this is removed
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
    return "%s (%s, pid %s) since %s, %d min ago" % (
        who, what, owner.get("pid") or "none, held", owner.get("since_utc", "?"), mins)


class FusionLock:
    """An atomic mkdir lock with an owner file, a wait and stale clearing.

    pid is the process that keeps the lock alive: this run (default), or None
    for a lock held across runs with --lock-hold (then only `expires` ends it).
    """

    def __init__(self, path, label="", script="", hold_s=3600.0, pid="self",
                 host=None, log=None):
        self.path = path
        self.label = label
        self.script = script
        self.hold_s = float(hold_s)
        self.pid = os.getpid() if pid == "self" else pid
        self.host = host or socket.gethostname()
        self.log = log or (lambda msg: print(msg, file=sys.stderr, flush=True))
        self.token = None
        self.owned = False       # we made the lock directory
        self.joined = False      # we run inside a lock held with --lock-hold

    # -- reading ------------------------------------------------------------
    def read_owner(self):
        try:
            with open(os.path.join(self.path, OWNER_FILE), "r", encoding="utf-8") as fh:
                owner = json.load(fh)
            return owner if isinstance(owner, dict) else None
        except (OSError, ValueError):
            return None

    def exists(self):
        return os.path.isdir(self.path)

    def stale_reason(self, owner, now=None):
        """Why the lock as described by `owner` is stale, or None if it is live."""
        now = time.time() if now is None else now
        if owner is None:
            try:
                age = now - os.stat(self.path).st_mtime
            except OSError:
                return None
            return ("no owner file for %d s" % age) if age > NO_OWNER_GRACE_S else None
        expires = owner.get("expires")
        if not isinstance(expires, (int, float)) or now > expires:
            return "expired at %s" % owner.get("expires_utc", expires)
        pid = owner.get("pid")
        if pid and owner.get("host") == self.host and not pid_alive(pid):
            return "its process %s has ended" % pid
        return None

    # -- taking and giving back --------------------------------------------
    def acquire(self, wait_s, poll_s=1.0, token=None, note_every_s=30.0):
        if token:
            return self._join(token)
        deadline = time.time() + float(wait_s)
        last_note = 0.0
        while True:
            try:
                os.mkdir(self.path)
            except FileExistsError:
                owner = self.read_owner()
                why = self.stale_reason(owner)
                if why:
                    self._clear_stale(owner, why)
                    continue
                now = time.time()
                if now >= deadline:
                    raise LockTimeout("Fusion is busy: the lock %s is held by %s" % (
                        self.path, describe_owner(owner, now)))
                if now - last_note >= note_every_s:
                    self.log("run_script: waiting for Fusion, held by %s; giving up in %d s"
                             % (describe_owner(owner, now), deadline - now))
                    last_note = now
                time.sleep(max(0.01, min(poll_s, deadline - now)))
                continue
            try:
                self.token = uuid.uuid4().hex
                now = time.time()
                owner = {
                    "token": self.token, "label": self.label, "script": self.script,
                    "pid": self.pid, "host": self.host,
                    "since": now, "since_utc": _utc(now),
                    "expires": now + self.hold_s, "expires_utc": _utc(now + self.hold_s),
                }
                tmp = os.path.join(self.path, OWNER_FILE + ".tmp")
                with open(tmp, "w", encoding="utf-8") as fh:
                    json.dump(owner, fh, indent=1)
                os.replace(tmp, os.path.join(self.path, OWNER_FILE))
            except BaseException:
                shutil.rmtree(self.path, ignore_errors=True)
                raise
            self.owned = True
            return owner

    def _join(self, token):
        owner = self.read_owner()
        if not owner or owner.get("token") != token:
            raise LockTimeout("%s is set, but the Fusion lock %s is not held with that "
                              "token (it is held by %s)" % (
                                  TOKEN_ENV, self.path,
                                  describe_owner(owner) if self.exists() else "nobody"))
        why = self.stale_reason(owner)
        if why:
            raise LockTimeout("the held Fusion lock %s is stale (%s); hold it again"
                              % (self.path, why))
        self.token = token
        self.joined = True
        return owner

    def _clear_stale(self, seen, why):
        """Remove a stale lock, unless it changed hands since we looked."""
        guard = self.path + ".clear"
        try:
            os.mkdir(guard)
        except FileExistsError:
            try:
                if time.time() - os.stat(guard).st_mtime > CLEAR_GUARD_STALE_S:
                    os.rmdir(guard)
            except OSError:
                pass
            time.sleep(0.2)
            return
        try:
            cur = self.read_owner()
            same = (cur is None and seen is None) or (
                cur is not None and seen is not None and cur.get("token") == seen.get("token"))
            if same and self.stale_reason(cur):
                shutil.rmtree(self.path, ignore_errors=True)
                self.log("run_script: cleared a stale Fusion lock (%s), left by %s"
                         % (why, describe_owner(seen)))
        finally:
            try:
                os.rmdir(guard)
            except OSError:
                pass

    def release(self):
        """Give the lock back if we made it and still own it."""
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

# Document steps for --doc, --save and --close. Runs inside Fusion; ARGS is
# filled in by doc_script(). It never closes or saves a document with
# another name, and never calls close(True) (that opens a dialog).
DOC_SCRIPT = '''import adsk.core, adsk.fusion
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
        files = [folder.dataFiles.item(i) for i in range(folder.dataFiles.count)]
        files = [f for f in files if f.name == name]
        if len(files) > 1:
            raise RuntimeError("%%d files are called %%r in %%s" %% (len(files), name, ARGS["folder"]))
        if files:
            app.data.activeProject = proj
            doc = app.documents.open(files[0], True)
            if doc is None:
                raise RuntimeError("could not open %%r from %%s" %% (name, ARGS["folder"]))
            doc.activate()
            print("run_script: opened %%r (version %%s) from %%s" %% (
                name, files[0].versionNumber, ARGS["folder"]))
            return
        if not ARGS.get("create"):
            raise RuntimeError("%%r is not open and not in %%s (add --doc-new to make it)"
                               %% (name, ARGS["folder"]))
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
    return DOC_SCRIPT % {"args": {
        "mode": mode, "name": name, "folder": folder, "create": bool(create),
        "description": description, "discard": bool(discard)}}


WRAPPER = '''import base64 as _b64
_SRC = _b64.b64decode(%(src)r).decode("utf-8")
_NS = {"__name__": "__fusion_script__", "__file__": %(path)r,
       "SCRIPT_ARGS": %(args)r}
exec(compile(_SRC, %(path)r, "exec"), _NS)

def run(context):
    return _NS["run"](context)
'''


def wrap_script(source, path, args):
    """Wrap the file so it compiles under its real path (true line numbers)."""
    compile(source, path, "exec")  # fail fast on syntax errors, locally
    return WRAPPER % {"src": base64.b64encode(source.encode("utf-8")).decode("ascii"),
                      "path": path, "args": args}


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
    ap.add_argument("--direction", default="iso-top-right",
                    help="camera for --screenshot: front, back, top, bottom, left, "
                         "right, iso-top-right, iso-top-left, ..., or current. The "
                         "view is turned and zoomed to fit first (default iso-top-right)")
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
        if not lock.exists():
            print("free: %s" % lock.path)
            return 0
        owner = lock.read_owner()
        why = lock.stale_reason(owner)
        print("held: %s by %s%s" % (lock.path, describe_owner(owner),
                                   ("; STALE (%s), the next run clears it" % why) if why else ""))
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
    lock = FusionLock(lock_path, label=label)

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

    if opts.screenshot:
        try:
            if opts.direction != "current":
                view = VIEWS.get(opts.direction)
                if view is None:
                    print("run_script: unknown --direction %r" % opts.direction, file=sys.stderr)
                    return 1
                mcp.call_tool("fusion_mcp_execute", {"featureType": "script", "object": {
                    "script": FIT_SCRIPT % {"view": view}}})
            shot = mcp.call_tool("fusion_mcp_read", {
                "queryType": "screenshot", "direction": "current",
                "width": opts.width, "height": opts.height,
                "transparentBackground": False, "antiAliasing": True})
        except McpError as e:
            print("run_script: screenshot failed: %s" % e, file=sys.stderr)
            return 1 if not ok else 2
        _, png = tool_payload(shot)
        if png:
            os.makedirs(os.path.dirname(os.path.abspath(opts.screenshot)), exist_ok=True)
            with open(opts.screenshot, "wb") as fh:
                fh.write(png)
            print("run_script: screenshot saved to %s" % opts.screenshot)
        else:
            print("run_script: no image in screenshot reply", file=sys.stderr)

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
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
