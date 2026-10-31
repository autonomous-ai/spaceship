#!/usr/bin/env python3
"""Run a Fusion API script file through Fusion's built-in MCP server.

Fusion (Autodesk Fusion with the "MCP Server Adapter") answers only on this
machine, at http://127.0.0.1:27182/mcp. This tool sends a script file to it
(JSON-RPC `initialize`, then `tools/call` of `fusion_mcp_execute` with
featureType "script") and prints what the script printed.

The script must define `run(_context)`. It runs inside Fusion, on the ACTIVE
document, so only one agent may drive Fusion at a time.

Examples
  python3 tools/fusion/run_script.py v2/01-CAD-Native/proof/wall_panel_frame.py
  python3 tools/fusion/run_script.py my_check.py --read-only
  python3 tools/fusion/run_script.py build.py --arg stop_after=3 \
      --screenshot /tmp/step3.png --direction iso-top-right

Script arguments
  Every --arg KEY=VALUE, plus repo_root (the repository root, found from this
  file's location) and script_path, reaches the script as the dict
  SCRIPT_ARGS (values are strings). The script also gets __file__. The file
  is compiled under its real path inside a small wrapper, so tracebacks show
  the real file name and line numbers.

Exit code 0 when the script ran without an exception, 1 when it raised one
(the traceback is printed), 2 when Fusion's MCP could not be reached.
Standard library only.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("FUSION_MCP_URL", "http://127.0.0.1:27182/mcp")
PROTOCOL_VERSION = "2025-06-18"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


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
            "clientInfo": {"name": "spaceship-run-script", "version": "1.0"},
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


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Run a Fusion API script file through Fusion's local MCP server.")
    ap.add_argument("script", help="Python file that defines run(_context)")
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
                    help="seconds to wait for Fusion (default 900)")
    ap.add_argument("--raw", action="store_true", help="print the raw tool reply")
    opts = ap.parse_args(argv)

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

    mcp = FusionMcp(opts.url, opts.timeout)
    try:
        mcp.initialize()
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
        out = parsed.get("message") if ok else (parsed.get("error") or parsed.get("message"))
        if out:
            sys.stdout.write(out if out.endswith("\n") else out + "\n")
    if not ok:
        print("run_script: the script raised an exception (see above)", file=sys.stderr)

    if opts.screenshot:
        try:
            if opts.direction != "current":
                view = VIEWS.get(opts.direction)
                if view is None:
                    ap.error("unknown --direction %r" % opts.direction)
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
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
