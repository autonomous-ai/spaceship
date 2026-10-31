#!/usr/bin/env python3
"""Offline tests for run_script.py: the Fusion lock and the document steps.

    python3 tools/fusion/test_run_script.py

No Fusion needed. A fake MCP server (standard library http.server) stands in
for Fusion: it answers initialize and tools/call, takes a while on each
script, and records how many scripts ran at the same time. Every test uses
its own lock directory in a temporary folder, never the real lock.
"""

import base64
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_script as rs  # noqa: E402

RUNNER = os.path.join(HERE, "run_script.py")


class FakeFusion(http.server.ThreadingHTTPServer):
    """Answers like Fusion's MCP. Each script call sleeps `delay` seconds."""

    daemon_threads = True

    def __init__(self, delay=0.6):
        super().__init__(("127.0.0.1", 0), FakeHandler)
        self.delay = delay
        self.active = 0
        self.max_active = 0
        self.scripts = []          # (arrival time, script text)
        self.mutex = threading.Lock()
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self):
        return "http://127.0.0.1:%d/mcp" % self.server_address[1]

    def stop(self):
        self.shutdown()
        self.server_close()


class FakeHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_a):
        pass

    def do_POST(self):
        srv = self.server
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if "id" not in body:                       # notification
            self.send_response(202)
            self.end_headers()
            return
        result = {}
        if body["method"] == "tools/call":
            args = body["params"]["arguments"]
            script = args.get("object", {}).get("script", "")
            m = re.search(r"_b64.b64decode\('([A-Za-z0-9+/=]+)'\)", script)
            if m:                                  # the runner's wrapper: unwrap
                script = base64.b64decode(m.group(1)).decode("utf-8")
            with srv.mutex:
                srv.active += 1
                srv.max_active = max(srv.max_active, srv.active)
                srv.scripts.append((time.time(), script))
            time.sleep(srv.delay)
            with srv.mutex:
                srv.active -= 1
            fail = "RAISE_IN_FUSION" in script
            text = json.dumps({"success": not fail,
                               "message": "fake ran %d chars" % len(script),
                               "error": "Traceback: raised" if fail else None})
            result = {"content": [{"type": "text", "text": text}], "isError": fail}
        reply = json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": result}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Mcp-Session-Id", "fake-session")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)


def dead_pid():
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def write_owner(path, **owner):
    os.mkdir(path)
    with open(os.path.join(path, rs.OWNER_FILE), "w") as fh:
        json.dump(owner, fh)


class LockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fusionlock-test-")
        self.path = os.path.join(self.tmp, "fusion.lock")
        self.logs = []

    def lock(self, **kw):
        kw.setdefault("log", self.logs.append)
        return rs.FusionLock(self.path, label="test", **kw)

    def test_take_and_give_back(self):
        lk = self.lock()
        owner = lk.acquire(1)
        self.assertTrue(os.path.isdir(self.path))
        self.assertEqual(lk.read_owner()["token"], owner["token"])
        self.assertEqual(owner["pid"], os.getpid())
        self.assertTrue(lk.release())
        self.assertFalse(os.path.exists(self.path))

    def test_second_taker_times_out_while_held(self):
        a = self.lock()
        a.acquire(1)
        t0 = time.time()
        with self.assertRaises(rs.LockTimeout) as cm:
            self.lock().acquire(0.5, poll_s=0.05)
        self.assertGreaterEqual(time.time() - t0, 0.45)
        self.assertIn("test", str(cm.exception))
        a.release()

    def test_waiter_gets_it_after_release(self):
        a = self.lock()
        a.acquire(1)
        threading.Timer(0.4, a.release).start()
        b = self.lock()
        b.acquire(5, poll_s=0.05)
        self.assertTrue(b.owned)
        b.release()

    def test_dead_process_lock_is_cleared(self):
        write_owner(self.path, token="old", pid=dead_pid(), host=self.lock().host,
                    since=time.time(), expires=time.time() + 3600)
        lk = self.lock()
        lk.acquire(2, poll_s=0.05)
        self.assertNotEqual(lk.read_owner()["token"], "old")
        self.assertTrue(any("has ended" in m for m in self.logs))
        lk.release()

    def test_expired_lock_is_cleared_even_if_pid_alive(self):
        write_owner(self.path, token="old", pid=os.getpid(), host=self.lock().host,
                    since=time.time() - 100, expires=time.time() - 1)
        lk = self.lock()
        lk.acquire(2, poll_s=0.05)
        self.assertTrue(any("expired" in m for m in self.logs))
        lk.release()

    def test_live_lock_is_not_cleared(self):
        write_owner(self.path, token="live", pid=os.getpid(), host=self.lock().host,
                    since=time.time(), expires=time.time() + 3600)
        with self.assertRaises(rs.LockTimeout):
            self.lock().acquire(0.3, poll_s=0.05)
        self.assertEqual(self.lock().read_owner()["token"], "live")

    def test_lock_without_owner_file_waits_then_clears_when_old(self):
        os.mkdir(self.path)                     # a run between mkdir and its owner file
        with self.assertRaises(rs.LockTimeout):
            self.lock().acquire(0.3, poll_s=0.05)
        old = time.time() - rs.NO_OWNER_GRACE_S - 5
        os.utime(self.path, (old, old))         # ... that died there
        lk = self.lock()
        lk.acquire(2, poll_s=0.05)
        self.assertTrue(lk.owned)
        lk.release()

    def test_release_leaves_a_lock_that_changed_hands(self):
        lk = self.lock()
        lk.acquire(1)
        with open(os.path.join(self.path, rs.OWNER_FILE), "w") as fh:
            json.dump({"token": "someone-else", "expires": time.time() + 60}, fh)
        self.assertFalse(lk.release())
        self.assertTrue(os.path.isdir(self.path))

    def test_held_lock_join_and_release(self):
        holder = self.lock(pid=None, hold_s=60)
        holder.acquire(1)
        token = holder.token
        self.assertIsNone(holder.read_owner()["pid"])
        joiner = self.lock()
        joiner.acquire(0.2, token=token)
        self.assertTrue(joiner.joined)
        self.assertFalse(joiner.release())      # a joined run doesn't give it back
        self.assertTrue(os.path.isdir(self.path))
        with self.assertRaises(rs.LockTimeout):
            self.lock().acquire(0.2, token="wrong")
        self.assertTrue(self.lock().release_held(token))
        self.assertFalse(os.path.exists(self.path))

    def test_racing_takers_get_it_one_at_a_time(self):
        inside, peak, done = [0], [0], []
        mutex = threading.Lock()

        def worker():
            lk = rs.FusionLock(self.path, label="t", log=lambda m: None)
            lk.acquire(20, poll_s=0.01)
            with mutex:
                inside[0] += 1
                peak[0] = max(peak[0], inside[0])
            time.sleep(0.02)
            with mutex:
                inside[0] -= 1
            lk.release()
            done.append(1)

        threads = [threading.Thread(target=worker) for _ in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(30)
        self.assertEqual(len(done), 12)
        self.assertEqual(peak[0], 1)


class RunnerTests(unittest.TestCase):
    """The command line, against a fake Fusion."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fusionrun-test-")
        self.lockdir = os.path.join(self.tmp, "fusion.lock")
        self.script = os.path.join(self.tmp, "noop.py")
        with open(self.script, "w") as fh:
            fh.write("def run(_context):\n    print('hello from the script')\n")
        self.fake = FakeFusion()

    def tearDown(self):
        self.fake.stop()

    def runner(self, *args, env=None, wait=True):
        cmd = [sys.executable, RUNNER] + list(args) + ["--lock", self.lockdir]
        e = dict(os.environ)
        e.pop(rs.TOKEN_ENV, None)
        e.update(env or {})
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=e)
        if not wait:
            return p
        out, err = p.communicate(timeout=60)
        return p.returncode, out, err

    def test_runs_never_overlap(self):
        procs = [self.runner(self.script, "--url", self.fake.url, "--label", "run%d" % i,
                             wait=False) for i in range(4)]
        codes = []
        for p in procs:
            p.communicate(timeout=60)
            codes.append(p.returncode)
        self.assertEqual(codes, [0, 0, 0, 0])
        self.assertEqual(len(self.fake.scripts), 4)
        self.assertEqual(self.fake.max_active, 1)
        self.assertFalse(os.path.exists(self.lockdir))

    def test_busy_lock_exits_3_and_names_the_holder(self):
        write_owner(self.lockdir, token="t", label="WALL engineer", script="wall.py",
                    pid=os.getpid(), host=rs.FusionLock(self.lockdir).host,
                    since=time.time(), since_utc="now", expires=time.time() + 60)
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--lock-wait", "0.5")
        self.assertEqual(code, 3)
        self.assertIn("WALL engineer", err)
        self.assertEqual(self.fake.scripts, [])

    def test_hold_then_run_inside_then_release(self):
        code, out, _ = self.runner("--lock-hold", "60")
        self.assertEqual(code, 0)
        token = out.strip()
        code, out, _ = self.runner("--lock-status")
        self.assertIn("held:", out)
        # a run without the token waits and gives up; with it, it runs at once
        code, _, _ = self.runner(self.script, "--url", self.fake.url, "--lock-wait", "0.3")
        self.assertEqual(code, 3)
        code, out, _ = self.runner(self.script, "--url", self.fake.url,
                                   env={rs.TOKEN_ENV: token})
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.isdir(self.lockdir))   # still held
        code, out, _ = self.runner("--lock-release", env={rs.TOKEN_ENV: token})
        self.assertEqual(code, 0)
        code, out, _ = self.runner("--lock-status")
        self.assertIn("free:", out)

    def test_doc_steps_run_in_order_around_the_script(self):
        code, out, err = self.runner(self.script, "--url", self.fake.url, "--doc", "X_P01_CAD",
                                     "--save", "test save", "--close")
        self.assertEqual(code, 0, err)
        modes = []
        for _t, s in self.fake.scripts:
            if "ARGS = {" in s:
                args = eval(s.split("ARGS = ", 1)[1].split("\n", 1)[0])  # our own repr
                modes.append(args["mode"])
                self.assertEqual(args["name"], "X_P01_CAD")
            else:
                modes.append("script")
        self.assertEqual(modes, ["open", "script", "save", "close"])

    def test_failed_script_skips_save_and_close(self):
        bad = os.path.join(self.tmp, "bad.py")
        with open(bad, "w") as fh:
            fh.write("def run(_context):\n    raise RuntimeError('RAISE_IN_FUSION')\n")
        code, _out, err = self.runner(bad, "--url", self.fake.url, "--doc", "X_P01_CAD",
                                      "--save", "--close")
        self.assertEqual(code, 1)
        self.assertEqual(len(self.fake.scripts), 2)      # open + script, no save or close
        self.assertIn("not saved or closed", err)
        self.assertFalse(os.path.exists(self.lockdir))

    def test_unreachable_fusion_gives_back_the_lock(self):
        code, _out, _err = self.runner(self.script, "--url", "http://127.0.0.1:9/mcp",
                                       "--timeout", "2")
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(self.lockdir))

    def test_sigterm_gives_back_the_lock(self):
        self.fake.delay = 5
        p = self.runner(self.script, "--url", self.fake.url, wait=False)
        t0 = time.time()
        while not os.path.isdir(self.lockdir) and time.time() - t0 < 10:
            time.sleep(0.05)
        self.assertTrue(os.path.isdir(self.lockdir))
        time.sleep(0.3)
        p.terminate()
        p.communicate(timeout=10)
        self.assertFalse(os.path.exists(self.lockdir))

    def test_doc_options_need_doc(self):
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--save")
        self.assertEqual(code, 2)          # argparse error
        self.assertIn("--doc", err)

    def test_doc_script_compiles(self):
        for mode in ("open", "save", "close"):
            compile(rs.doc_script(mode, "N", create=True, description="d"), mode, "exec")


if __name__ == "__main__":
    unittest.main(verbosity=2)
