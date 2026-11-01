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
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
import threading
import time
import types
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
        self.slow_delay = delay    # for a script holding SLOW_IN_FUSION
        self.serial = False        # True: one script at a time, like Fusion's main thread
        self.main = threading.Lock()
        self.active = 0
        self.max_active = 0
        self.scripts = []          # (arrival time, script text)
        self.done = []             # (end time, script text)
        self.open_log = None       # where a STUCK_OPEN / OPEN_ENDS script logs its open
        self.open_end_after = 1.5  # an OPEN_ENDS script's open ends this long after it started
        self.mutex = threading.Lock()
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self):
        return "http://127.0.0.1:%d/mcp" % self.server_address[1]

    def stop(self):
        self.shutdown()
        self.server_close()

    def log_open(self, text):
        """A line as the wrapper writes it inside Fusion (run_script.WRAPPER)."""
        with open(self.open_log, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S UTC ", time.gmtime()) + text + "\n")


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
            m = re.search(r"_SRC = _b64.b64decode\('([A-Za-z0-9+/=]+)'\)", script)   # the script, not the folder helper
            if m:                                  # the runner's wrapper: unwrap
                script = base64.b64decode(m.group(1)).decode("utf-8")
            with srv.mutex:
                srv.scripts.append((time.time(), script))
            if "STUCK_OPEN_IN_FUSION" in script or "OPEN_ENDS_IN_FUSION" in script:
                srv.log_open("start open ZZ_P00_STUCK-SAMPLE_DWG v1 visible; run: TEST: stuck.py")
                if "OPEN_ENDS_IN_FUSION" in script:
                    threading.Timer(srv.open_end_after, srv.log_open,
                                    ["end open ZZ_P00_STUCK-SAMPLE_DWG v1 after 1.5 s: ok"]).start()
            with (srv.main if srv.serial else contextlib.nullcontext()):
                with srv.mutex:
                    srv.active += 1
                    srv.max_active = max(srv.max_active, srv.active)
                time.sleep(srv.slow_delay if "SLOW_IN_FUSION" in script else srv.delay)
                with srv.mutex:
                    srv.active -= 1
                    srv.done.append((time.time(), script))
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

    def test_joined_run_moves_the_hold_expiry_out(self):
        # review P2: a 1 s hold and a joined run of 3 s must not let a waiter in
        holder = self.lock(pid=None, hold_s=1)
        holder.acquire(1)
        joiner = self.lock(hold_s=3)
        owner = joiner.acquire(0.2, token=holder.token)
        self.assertGreaterEqual(owner["expires"], time.time() + 2.5)
        self.assertEqual(self.lock().read_owner()["joined"]["pid"], os.getpid())
        t0 = time.time()
        with self.assertRaises(rs.LockTimeout):
            self.lock().acquire(1.5, poll_s=0.05)        # the original hold ran out at 1 s
        self.assertGreaterEqual(time.time() - t0, 1.4)
        self.assertFalse(any("cleared" in m for m in self.logs))
        time.sleep(max(0, owner["expires"] - time.time()) + 0.1)
        late = self.lock()
        late.acquire(2, poll_s=0.05)                      # once the joined run's time is up
        self.assertTrue(late.owned)
        late.release()

    def test_a_plain_file_at_the_lock_path_counts_as_held(self):
        # review P2: no spin, no "cleared" flood, give up on time
        with open(self.path, "w") as fh:
            fh.write("not a lock")
        old = time.time() - 3600
        os.utime(self.path, (old, old))
        lk = self.lock()
        self.assertTrue(lk.exists())
        t0 = time.time()
        with self.assertRaises(rs.LockTimeout) as cm:
            lk.acquire(1.0, poll_s=0.05, note_every_s=100)
        self.assertLess(time.time() - t0, 2.0)
        self.assertIn("not a Fusion lock", str(cm.exception))
        self.assertTrue(os.path.isfile(self.path))       # left alone
        self.assertLessEqual(len(self.logs), 2)

    def test_a_stale_lock_that_cannot_be_removed_ends_the_wait_on_time(self):
        write_owner(self.path, token="old", pid=dead_pid(), since=time.time(),
                    expires=time.time() + 3600)
        os.chmod(self.path, 0o555)                       # owner.json can't be deleted
        try:
            lk = self.lock()
            t0 = time.time()
            with self.assertRaises(rs.LockTimeout):
                lk.acquire(1.0, poll_s=0.05, note_every_s=100)
            self.assertLess(time.time() - t0, 2.0)
            self.assertEqual(sum("can't clear" in m for m in self.logs), 1)
            self.assertFalse(any("cleared a stale" in m for m in self.logs))
        finally:
            os.chmod(self.path, 0o755)

    def test_dead_process_is_cleared_whatever_hostname_it_reports(self):
        write_owner(self.path, token="old", pid=dead_pid(), host="another-name.lan",
                    since=time.time(), expires=time.time() + 3600)
        lk = self.lock()
        lk.acquire(2, poll_s=0.05)
        self.assertTrue(any("has ended" in m for m in self.logs))
        lk.release()

    def test_waiters_get_the_lock_oldest_first(self):
        holder = self.lock()
        holder.acquire(1)
        order, threads = [], []

        def waiter(i):
            lk = rs.FusionLock(self.path, label="w%d" % i, log=lambda m: None)
            lk.acquire(20, poll_s=0.02)
            order.append(i)
            time.sleep(0.05)
            lk.release()

        for i in range(5):
            th = threading.Thread(target=waiter, args=(i,))
            th.start()
            threads.append(th)
            time.sleep(0.15)                              # tickets in a known order
        self.assertEqual(len(self.lock().queue()), 5)
        holder.release()
        for th in threads:
            th.join(30)
        self.assertEqual(order, [0, 1, 2, 3, 4])
        self.assertEqual(self.lock().queue(), [])

    # --lock-front (PM ruling 2026-10-31: only for runs the PM approved)
    def test_a_front_run_goes_ahead_of_older_waiters_but_never_the_holder(self):
        holder = self.lock()
        holder.acquire(1)
        order, threads = [], []

        def waiter(i, front):
            lk = rs.FusionLock(self.path, label="w%s" % i, log=lambda m: None, front=front)
            lk.acquire(20, poll_s=0.02)
            order.append(i)
            time.sleep(0.05)
            lk.release()

        for i, front in ((0, ""), (1, ""), ("F1", "PM approved: test 1"), (2, ""),
                         ("F2", "PM approved: test 2")):
            th = threading.Thread(target=waiter, args=(i, front))
            th.start()
            threads.append(th)
            time.sleep(0.15)                              # tickets in a known order
        time.sleep(0.3)
        self.assertEqual(order, [])                       # nobody took it from the holder
        self.assertEqual(self.lock().read_owner()["token"], holder.token)
        self.assertEqual([r for _l, r in self.lock().front_waiting()],
                         ["PM approved: test 1", "PM approved: test 2"])
        holder.release()
        for th in threads:
            th.join(30)
        self.assertEqual(order, ["F1", "F2", 0, 1, 2])

    def test_a_front_ticket_sorts_first_for_runners_without_the_option(self):
        # main before #101 serves sorted ticket names with three parts, the
        # first two digits: a front ticket must come first there too
        normal = self.lock()
        normal._take_ticket(time.time() + 60)
        front = self.lock(front="PM approved: test")
        front._take_ticket(time.time() + 60)
        old_style = sorted(n for n in os.listdir(self.path + ".queue")
                           if len(n.split("-")) == 3 and n.split("-")[0].isdigit()
                           and n.split("-")[1].isdigit())
        self.assertEqual(old_style, [front.ticket, normal.ticket])
        self.assertEqual(self.lock().queue(), [front.ticket, normal.ticket])
        normal._drop_ticket()
        front._drop_ticket()

    def test_the_front_reason_is_shown_to_everyone_waiting(self):
        f = self.lock(front="PM approved: cancel test")
        f.acquire(1)
        with self.assertRaises(rs.LockTimeout) as cm:
            self.lock().acquire(0.2, poll_s=0.05)
        self.assertIn("went first in the queue: PM approved: cancel test", str(cm.exception))
        f.release()

    def test_a_dead_waiters_ticket_is_dropped(self):
        holder = self.lock()
        holder.acquire(1)
        os.makedirs(self.path + ".queue", exist_ok=True)
        ghost = "%020d-%d-deadbeef" % (1, dead_pid())          # oldest, but its run is gone
        with open(os.path.join(self.path + ".queue", ghost), "w") as fh:
            json.dump({"pid": 0, "give_up": time.time() + 999}, fh)
        threading.Timer(0.3, holder.release).start()
        lk = self.lock()
        lk.acquire(5, poll_s=0.05)
        self.assertTrue(lk.owned)
        self.assertNotIn(ghost, os.listdir(self.path + ".queue"))
        lk.release()

    def test_joined_run_takes_its_note_out_when_it_ends(self):
        holder = self.lock(pid=None, hold_s=60)
        holder.acquire(1)
        joiner = self.lock(hold_s=5)
        joiner.acquire(0.2, token=holder.token)
        self.assertIn("joined", self.lock().read_owner())
        self.assertIn("now running", rs.describe_owner(self.lock().read_owner()))
        self.assertFalse(joiner.release())
        owner = self.lock().read_owner()
        self.assertNotIn("joined", owner)               # the hold stays, the note goes
        self.assertEqual(owner["token"], holder.token)
        self.assertTrue(self.lock().release_held(holder.token))

    def test_extend_keeps_the_lock_or_the_joined_hold_and_says_why(self):
        # PM ruling 2026-11-01: while a timed-out run waits for Fusion, no waiter may
        # clear its lock as expired
        lk = self.lock(hold_s=2)
        lk.acquire(1)
        self.assertTrue(lk.extend(600, note="waiting for Fusion to finish"))
        owner = lk.read_owner()
        self.assertGreater(owner["expires"], time.time() + 590)
        self.assertIn("waiting for Fusion to finish", rs.describe_owner(owner))
        self.assertTrue(lk.release())
        self.assertFalse(lk.extend(600))                   # not ours any more
        holder = self.lock(pid=None, hold_s=2)
        holder.acquire(1)
        joiner = self.lock(hold_s=1)
        joiner.acquire(0.2, token=holder.token)
        self.assertTrue(joiner.extend(600, note="busy"))
        self.assertGreater(self.lock().read_owner()["expires"], time.time() + 590)
        joiner.release()
        self.assertNotIn("busy", self.lock().read_owner())  # the note goes with the run
        self.assertTrue(self.lock().release_held(holder.token))

    def test_finished_joined_run_is_not_shown_as_running(self):
        owner = {"label": "x", "since": time.time(), "joined": {"script": "s.py", "pid": dead_pid()}}
        self.assertNotIn("now running", rs.describe_owner(owner))

    def test_unremovable_lock_without_owner_says_so_once(self):
        os.mkdir(self.path)
        os.chmod(self.path, 0o555)
        old = time.time() - rs.NO_OWNER_GRACE_S - 5
        os.utime(self.path, (old, old))
        sub = os.path.join(self.path, "x")             # can't be made: the folder is read-only
        try:
            os.chmod(self.path, 0o755)
            os.mkdir(sub)
            os.chmod(self.path, 0o555)                  # the lock folder can't be emptied
            os.utime(self.path, (old, old))
            with self.assertRaises(rs.LockTimeout):
                self.lock().acquire(2.5, poll_s=0.05, note_every_s=100)
            self.assertEqual(sum("can't clear" in m for m in self.logs), 1)
        finally:
            os.chmod(self.path, 0o755)

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
        code, _out, err = self.runner(self.script, "--url", "http://127.0.0.1:9/mcp",
                                      "--timeout", "2")
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(self.lockdir))
        self.assertNotIn("keeping the Fusion lock", err)      # nothing to wait for

    def write(self, name, marker):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as fh:
            fh.write("def run(_context):\n    print(%r)\n" % marker)
        return path

    def test_a_timed_out_call_keeps_the_lock_until_fusion_answers(self):
        # PM ruling 2026-11-01. Live 00:15: a build ran past its time limit, the runner
        # gave the lock back at once, and the next run started on a busy Fusion.
        # a free Fusion runs the read-only check at once; the build holds it for 4 s
        self.fake.serial, self.fake.delay, self.fake.slow_delay = True, 0.05, 4.0
        slow, second = self.write("slow.py", "SLOW_IN_FUSION"), self.write("second.py", "SECOND_RUN")
        p1 = self.runner(slow, "--url", self.fake.url, "--timeout", "1", "--busy-poll", "0.5",
                         "--busy-wait", "30", wait=False)
        t0 = time.time()
        while not self.fake.scripts and time.time() - t0 < 10:
            time.sleep(0.05)
        p2 = self.runner(second, "--url", self.fake.url, "--lock-wait", "60", wait=False)
        _out1, err1 = p1.communicate(timeout=60)
        _out2, err2 = p2.communicate(timeout=60)
        self.assertEqual(p1.returncode, 2, err1)
        self.assertEqual(p2.returncode, 0, err2)
        self.assertIn("keeping the Fusion lock", err1)
        self.assertIn("Fusion answers again", err1)
        slow_end = [t for t, s in self.fake.done if "SLOW_IN_FUSION" in s][0]
        second_in = [t for t, s in self.fake.scripts if "SECOND_RUN" in s][0]
        self.assertGreaterEqual(second_in, slow_end)        # the next run waited for Fusion itself
        self.assertFalse(os.path.exists(self.lockdir))

    def test_a_fusion_that_never_answers_gets_the_lock_back_with_a_loud_warning(self):
        self.fake.serial, self.fake.delay, self.fake.slow_delay = True, 0.05, 6.0
        slow = self.write("slow.py", "SLOW_IN_FUSION")
        t0 = time.time()
        code, _out, err = self.runner(slow, "--url", self.fake.url, "--timeout", "1",
                                      "--busy-poll", "0.5", "--busy-wait", "2")
        self.assertEqual(code, 2)
        self.assertIn("WARNING: Fusion still hasn't answered", err)
        self.assertLess(time.time() - t0, 5.5)              # gave up after the wait, not the script
        self.assertFalse(os.path.exists(self.lockdir))

    # Stuck in an open (PM ruling 2026-11-01). Live 03:39: an open never ended, the
    # read-only check after the timeout was answered at once, the session went on, and
    # its next open crashed Fusion at 03:55.
    def stuck_run(self, marker="STUCK_OPEN_IN_FUSION", limit="2"):
        self.fake.delay, self.fake.slow_delay = 0.05, 6.0     # Fusion answers the check at once
        self.fake.open_log = self.lockdir + ".opens.log"
        stuck = self.write("stuck.py", "SLOW_IN_FUSION " + marker)
        return self.runner(stuck, "--url", self.fake.url, "--timeout", "1", "--busy-poll", "0.5",
                           "--busy-wait", "30", "--open-limit", limit)

    def test_an_open_that_never_ends_flags_fusion_unhealthy_even_though_it_answers(self):
        code, _out, err = self.stuck_run()
        self.assertEqual(code, rs.EXIT_UNHEALTHY, err)
        self.assertIn("Fusion answers again", err)                 # the check alone would pass it
        self.assertIn("FUSION IS UNHEALTHY", err)
        self.assertIn("ZZ_P00_STUCK-SAMPLE_DWG v1", err)
        with open(rs.unhealthy_path(self.lockdir)) as fh:
            flag = json.load(fh)
        self.assertEqual([o["what"] for o in flag["opens"]], ["ZZ_P00_STUCK-SAMPLE_DWG v1"])
        self.assertEqual(flag["fusion_pid"], rs.fusion_pid())
        self.assertEqual(flag["fusion_pids"], rs.fusion_pids())
        self.assertFalse(os.path.exists(self.lockdir))            # the lock goes back; runs refuse

    def test_after_the_flag_every_run_refuses_without_sending_fusion_anything(self):
        self.stuck_run()
        sent = len(self.fake.scripts)
        second = self.write("second.py", "SECOND_RUN")
        code, _out, err = self.runner(second, "--url", self.fake.url)
        self.assertEqual(code, rs.EXIT_UNHEALTHY, err)
        self.assertIn("flagged unhealthy", err)
        self.assertIn("did not start", err)
        _c, token, _e = self.runner("--lock-hold", "60")
        token = token.strip()
        code2, _o, err2 = self.runner(second, "--url", self.fake.url, env={rs.TOKEN_ENV: token})
        self.assertEqual(code2, rs.EXIT_UNHEALTHY, err2)          # inside a held lock too: a session stops
        self.runner("--lock-release", env={rs.TOKEN_ENV: token})
        self.assertEqual(len(self.fake.scripts), sent)            # nothing reached Fusion

    def test_an_open_that_ends_within_the_grace_is_not_flagged(self):
        self.fake.open_end_after = 4.0                            # after the timeout and the check
        code, _out, err = self.stuck_run("OPEN_ENDS_IN_FUSION", limit="20")
        self.assertEqual(code, 2, err)                            # a timeout, as before
        self.assertIn("hasn't ended", err)
        self.assertNotIn("FUSION IS UNHEALTHY", err)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lockdir)))

    def test_a_timeout_without_an_open_is_not_flagged(self):
        self.fake.delay, self.fake.slow_delay = 0.05, 4.0
        self.fake.open_log = self.lockdir + ".opens.log"
        code, _out, err = self.runner(self.write("slow.py", "SLOW_IN_FUSION"), "--url", self.fake.url,
                                      "--timeout", "1", "--busy-poll", "0.5", "--busy-wait", "30")
        self.assertEqual(code, 2, err)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lockdir)))

    def test_an_open_left_by_an_earlier_run_is_not_this_runs(self):
        # a dangling start line written before this run took the lock isn't this run's
        self.fake.open_log = self.lockdir + ".opens.log"
        self.fake.log_open("start open OLD_P00_SAMPLE_CAD v3 HIDDEN; run: TEST: earlier.py")
        self.fake.delay, self.fake.slow_delay = 0.05, 4.0
        code, _out, err = self.runner(self.write("slow.py", "SLOW_IN_FUSION"), "--url", self.fake.url,
                                      "--timeout", "1", "--busy-poll", "0.5", "--busy-wait", "30",
                                      "--open-limit", "1")
        self.assertEqual(code, 2, err)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lockdir)))

    def test_the_doc_step_installs_the_open_logger_too(self):
        # Reviewer 5 on #269: opens in the --doc step were logged only once a wrapped
        # script had installed the logger (not right after a Fusion start)
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--doc", "X_P01_CAD",
                                      "--label", "TEST")
        self.assertEqual(code, 0, err)
        doc = [sc for _t, sc in self.fake.scripts if "'mode': 'open'" in sc]
        self.assertEqual(len(doc), 1)
        self.assertIn("_OPENLOG = %r" % rs.open_log_path(self.lockdir), doc[0])
        self.assertIn("'TEST: noop.py'", doc[0])                  # this run's label on its opens

    def write_flag(self, pid):
        with open(rs.unhealthy_path(self.lockdir), "w") as fh:
            json.dump({"flagged_utc": "2026-11-01 03:55:00 UTC", "fusion_pid": pid, "by": "TEST",
                       "opens": [{"started": "2026-11-01 03:39:45 UTC", "what": "ZZ_P00_X_DWG v1",
                                  "run": "TEST: box.py"}]}, fh)

    def test_a_flag_from_before_a_fusion_restart_is_cleared(self):
        self.write_flag(dead_pid())                               # that Fusion process is gone
        code, _out, err = self.runner(self.script, "--url", self.fake.url)
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.fake.scripts), 1)               # the run went on
        self.assertIn("it has restarted (now process", err)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lockdir)))

    def test_status_shows_the_flag_and_clear_unhealthy_removes_it(self):
        self.write_flag(rs.fusion_pid())                          # the Fusion running now
        _c, out, _e = self.runner("--lock-status")
        self.assertIn("UNHEALTHY", out)
        self.assertIn("ZZ_P00_X_DWG v1", out)
        code, out, _e = self.runner("--clear-unhealthy")
        self.assertEqual(code, 0)
        self.assertIn("cleared the unhealthy flag", out)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lockdir)))
        code, out, err = self.runner(self.script, "--url", self.fake.url)
        self.assertEqual(code, 0, err)

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

    def test_bad_direction_is_refused_before_the_lock(self):
        code, _out, err = self.runner(self.script, "--url", self.fake.url,
                                      "--screenshot", os.path.join(self.tmp, "x.png"),
                                      "--direction", "sideways")
        self.assertEqual(code, 2)
        self.assertIn("--direction", err)
        self.assertEqual(self.fake.scripts, [])
        self.assertFalse(os.path.exists(self.lockdir))

    def test_screenshot_then_save_and_close(self):
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--doc", "X_P01_CAD",
                                      "--screenshot", os.path.join(self.tmp, "x.png"),
                                      "--save", "--close")
        self.assertEqual(code, 0, err)
        kinds = []
        for _t, s in self.fake.scripts:
            if "ARGS = {" in s:
                kinds.append(eval(s.split("ARGS = ", 1)[1].split("\n", 1)[0])["mode"])
            elif "viewOrientation" in s:
                kinds.append("fit")
            elif s == "":
                kinds.append("shot")
            else:
                kinds.append("script")
        self.assertEqual(kinds, ["open", "script", "fit", "shot", "save", "close"])

    def test_lock_front_waits_for_the_hold_and_shows_in_status(self):
        code, out, _ = self.runner("--lock-hold", "60")
        token = out.strip()
        p = self.runner(self.script, "--url", self.fake.url, "--label", "cancel test",
                        "--lock-front", "PM approved: live test", wait=False)
        time.sleep(1.5)
        code, out, _ = self.runner("--lock-status")
        self.assertIn("1 going first: cancel test, PM approved: live test", out)
        self.assertIsNone(p.poll())                       # still waiting behind the hold
        self.assertEqual(self.fake.scripts, [])
        self.runner("--lock-release", env={rs.TOKEN_ENV: token})
        out, err = p.communicate(timeout=60)
        self.assertEqual(p.returncode, 0, err)
        self.assertEqual(len(self.fake.scripts), 1)

    def test_lock_front_needs_a_reason(self):
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--lock-front", "  ")
        self.assertEqual(code, 2)
        self.assertIn("needs the reason", err)

    def test_status_reports_a_plain_file_as_held(self):
        with open(self.lockdir, "w") as fh:
            fh.write("x")
        code, out, _ = self.runner("--lock-status")
        self.assertEqual(code, 0)
        self.assertIn("held:", out)
        self.assertIn("not a Fusion lock", out)

    def test_doc_options_need_doc(self):
        code, _out, err = self.runner(self.script, "--url", self.fake.url, "--save")
        self.assertEqual(code, 2)          # argparse error
        self.assertIn("--doc", err)

    def test_doc_script_compiles(self):
        for mode in ("open", "save", "close"):
            compile(rs.doc_script(mode, "N", create=True, description="d"), mode, "exec")



class OpenLogTests(unittest.TestCase):
    """Every document open is logged next to the lock, start and end (PM 2026-11-01: a
    drawing open started at 00:23 and never ended, and nothing said what it was)."""

    def fake_core(self):
        import types
        core = types.ModuleType("adsk.core")
        core.RESULT = []

        class Documents:
            def open(self, dataFile, visible=True):
                if dataFile.name == "BAD_CAD":
                    raise RuntimeError("3 : the open failed")
                return "opened %s" % dataFile.name
        core.Documents = Documents
        return core

    def run_wrapped(self, core, log, name, visible):
        import types
        adsk = types.ModuleType("adsk")
        adsk.core = core
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "fusion_folder")}
        sys.modules.update({"adsk": adsk, "adsk.core": core})
        script = ("import adsk.core\n"
                  "class F:\n    name = %r\n    versionNumber = 4\n"
                  "def run(_c):\n    adsk.core.RESULT.append(adsk.core.Documents().open(F(), %r))\n" % (name, visible))
        try:
            ns = {}
            exec(compile(rs.wrap_script(script, "/x/team.py", {}, open_log=log, run_label="TEST run: team.py"),
                         "wrapper", "exec"), ns)
            ns["run"](None)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    def lines(self, log):
        with open(log) as fh:
            return fh.read().splitlines()

    def test_a_hidden_open_is_logged_at_start_and_end(self):
        log = os.path.join(tempfile.mkdtemp(), "opens.log")
        core = self.fake_core()
        self.run_wrapped(core, log, "X_P01_CAD", False)
        self.assertEqual(core.RESULT, ["opened X_P01_CAD"])
        start, end = self.lines(log)
        self.assertIn("start open X_P01_CAD v4 HIDDEN; run: TEST run: team.py", start)
        self.assertRegex(end, r"end open X_P01_CAD v4 after [0-9.]+ s: ok$")

    def test_a_failed_open_is_logged_and_still_raises(self):
        log = os.path.join(tempfile.mkdtemp(), "opens.log")
        with self.assertRaises(RuntimeError):
            self.run_wrapped(self.fake_core(), log, "BAD_CAD", True)
        start, end = self.lines(log)
        self.assertIn("start open BAD_CAD v4 visible", start)
        self.assertIn("error 3 : the open failed", end)

    def test_the_logger_is_installed_once_per_fusion_session(self):
        # Fusion keeps the class between runs: a second run must not log every open twice
        log = os.path.join(tempfile.mkdtemp(), "opens.log")
        core = self.fake_core()
        self.run_wrapped(core, log, "X_P01_CAD", True)
        self.run_wrapped(core, log, "Y_P01_CAD", True)
        self.assertEqual([l.split(" open ")[1].split(" v4")[0] for l in self.lines(log) if " start " in l],
                         ["X_P01_CAD", "Y_P01_CAD"])

    def test_the_log_sits_next_to_the_lock(self):
        self.assertEqual(rs.open_log_path("/tmp/x.lock"), "/tmp/x.lock.opens.log")


class OpenGuardTests(unittest.TestCase):
    """The open log decides after a timeout whether Fusion is stuck in an open."""

    LOG = ["2026-11-01 03:39:14 UTC start open ZZ_P00_PROMOTE-SAMPLE_CAD v2 visible; run: a run from wt-ga: box.py",
           "2026-11-01 03:39:16 UTC end open ZZ_P00_PROMOTE-SAMPLE_CAD v2 after 2.0 s: ok",
           "2026-11-01 03:39:45 UTC start open ZZ_P00_PROMOTE-SAMPLE_DWG v1 visible; run: a run from wt-ga: box.py"]

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="openguard-")
        self.lock = os.path.join(self.tmp, "fusion.lock")
        self.log = rs.open_log_path(self.lock)

    def write(self, lines, mode="w"):
        with open(self.log, mode, encoding="utf-8") as fh:
            fh.write("".join(l + "\n" for l in lines))

    def test_the_live_log_of_0339_shows_the_drawing_open_that_never_ended(self):
        self.write(self.LOG)
        self.assertEqual(rs.unfinished_opens(self.log),
                         [{"started": "2026-11-01 03:39:45 UTC", "what": "ZZ_P00_PROMOTE-SAMPLE_DWG v1",
                           "run": "a run from wt-ga: box.py"}])

    def test_only_lines_after_the_runs_offset_count(self):
        self.write(self.LOG)
        offset = rs.open_log_size(self.log)
        self.assertEqual(rs.unfinished_opens(self.log, offset), [])
        self.write(["2026-11-01 04:00:00 UTC start open A B_CAD v3 HIDDEN; run: x",       # a space in the name
                    "2026-11-01 04:00:01 UTC end open A B_CAD v3 after 1.0 s: error 3 : timed out after 30 s",
                    "2026-11-01 04:00:02 UTC start open (name unreadable) visible; run: y"], "a")
        self.assertEqual([o["what"] for o in rs.unfinished_opens(self.log, offset)], ["(name unreadable)"])

    def test_the_wrappers_own_lines_parse(self):
        # tie the reader to the writer: lines made by the real wrapper code
        t = OpenLogTests()
        t.run_wrapped(t.fake_core(), self.log, "X_P01_CAD", False)
        self.assertEqual(rs.unfinished_opens(self.log), [])
        with open(self.log) as fh:
            start = fh.read().splitlines()[0]
        self.write([start])
        self.assertEqual([o["what"] for o in rs.unfinished_opens(self.log)], ["X_P01_CAD v4"])

    def test_no_log_means_nothing_unfinished(self):
        self.assertEqual(rs.unfinished_opens(self.log), [])
        self.assertEqual(rs.open_log_size(self.log), 0)

    START = 1793504385.0           # 2026-11-01 03:39:45 UTC, the stuck open's start line

    def guard(self, end_at=None, limit=600.0, first=150.0, pids=(4242,)):
        """guard_opens on a fake wall clock starting `first` s after the open's start (as after
        start_drawing's 120 s call timeout); the open ends `end_at` s after its start, if given."""
        clock = {"t": self.START + first}

        def sleep(s):
            clock["t"] += s
            if end_at is not None and clock["t"] >= self.START + end_at:
                self.write(["2026-11-01 03:44:45 UTC end open ZZ_P00_PROMOTE-SAMPLE_DWG v1 after 300.0 s: ok"], "a")
        msgs = []
        left = rs.guard_opens(self.lock, 0, "TEST: box.py", limit_s=limit, poll_s=10.0, log=msgs.append,
                              wall=lambda: clock["t"], sleep=sleep, pids=lambda: list(pids))
        return left, msgs, clock["t"] - self.START

    def test_the_start_time_reads_as_utc(self):
        self.assertEqual(rs._started_epoch({"started": "2026-11-01 03:39:45 UTC"}), self.START)
        self.assertIsNone(rs._started_epoch({"started": "soon"}))

    def test_a_slow_open_that_ends_before_the_limit_is_not_flagged(self):
        # Reviewer 5 on #269: start_drawing's calls time out at 120 s; a cloud open that takes
        # 5 minutes and then ends must not stop every team
        self.write(self.LOG)
        left, msgs, age = self.guard(end_at=300.0)
        self.assertEqual(left, [])
        self.assertEqual(age, 300.0)
        self.assertFalse(os.path.exists(rs.unhealthy_path(self.lock)))
        self.assertIn("hasn't ended", msgs[0])
        self.assertIn("10 min old", msgs[0])

    def test_an_open_still_pending_at_the_limit_writes_the_flag(self):
        self.write(self.LOG)
        left, msgs, age = self.guard()
        self.assertEqual([o["what"] for o in left], ["ZZ_P00_PROMOTE-SAMPLE_DWG v1"])
        self.assertEqual(age, 600.0)                                  # counted from its start line
        with open(rs.unhealthy_path(self.lock)) as fh:
            flag = json.load(fh)
        self.assertEqual((flag["fusion_pids"], flag["fusion_pid"], flag["by"]), ([4242], 4242, "TEST: box.py"))
        self.assertTrue(any("FUSION IS UNHEALTHY" in m for m in msgs))

    def test_an_open_already_past_the_limit_is_flagged_at_once(self):
        # run_script's 900 s timeout: the open is older than the limit when the check starts
        self.write(self.LOG)
        left, _msgs, age = self.guard(first=900.0)
        self.assertEqual(len(left), 1)
        self.assertEqual(age, 900.0)                                  # no extra wait

    def test_an_unreadable_start_time_counts_from_when_it_was_seen(self):
        self.write(["junk UTC start open Q_DWG v1 visible; run: x"])
        self.assertEqual(rs.unfinished_opens(self.log), [])           # not an open line at all
        self.write(["2026-13-45 99:99:99 UTC start open Q_DWG v1 visible; run: x"])
        left, _msgs, _age = self.guard(limit=60.0)
        self.assertEqual([o["what"] for o in left], ["Q_DWG v1"])

    def flagged(self):
        self.write(self.LOG)
        self.guard()                                                  # flag written with process 4242
        self.assertTrue(os.path.exists(rs.unhealthy_path(self.lock)))

    def refusal(self, now, notes=None):
        return rs.unhealthy_refusal(self.lock, log=(notes.append if notes is not None else lambda m: None),
                                    pids=lambda: now)

    def test_no_flag_no_refusal(self):
        self.assertIsNone(self.refusal([4242]))

    def test_the_same_fusion_process_is_refused(self):
        self.flagged()
        why = self.refusal([4242])
        self.assertIn("ZZ_P00_PROMOTE-SAMPLE_DWG v1", why)
        self.assertIn("restarted", why)

    def test_one_new_fusion_process_or_none_clears_the_flag(self):
        for now, said in (([5151], "it has restarted (now process 5151)"), ([], "it isn't running")):
            self.flagged()
            notes = []
            self.assertIsNone(self.refusal(now, notes))
            self.assertIn(said, notes[0])
            self.assertFalse(os.path.exists(rs.unhealthy_path(self.lock)))

    def test_two_fusion_processes_keep_the_flag(self):
        # Reviewer 5 on #269: during a relaunch overlap the stuck process may still run
        self.flagged()
        self.assertIsNotNone(self.refusal([4242, 5151]))
        self.assertIsNotNone(self.refusal([5151, 6262]))
        self.assertIsNotNone(self.refusal(None))                      # ps unreadable: keep it

    def test_a_flag_without_process_numbers_or_unreadable_is_kept(self):
        with open(rs.unhealthy_path(self.lock), "w") as fh:
            fh.write("{not json")
        self.assertIsNotNone(self.refusal([5151]))
        with open(rs.unhealthy_path(self.lock), "w") as fh:
            json.dump({"fusion_pid": None, "fusion_pids": None, "opens": []}, fh)
        self.assertIsNotNone(self.refusal([5151]))

    def test_a_flag_from_before_this_change_still_clears_on_a_restart(self):
        with open(rs.unhealthy_path(self.lock), "w") as fh:
            json.dump({"fusion_pid": 4242, "opens": []}, fh)             # #269's flag: one number
        self.assertIsNotNone(self.refusal([4242]))
        self.assertIsNone(self.refusal([5151]))

    def test_the_process_list_reader(self):
        out = ("  101 /Applications/Other.app/Contents/MacOS/Other\n"
               "  202 /Users/x/Applications/Autodesk Fusion.app/Contents/MacOS/Autodesk Fusion\n"
               "  303 /Users/x/b43a/Autodesk Fusion.app/Contents/MacOS/Autodesk Fusion\n")
        fake = lambda *a, **k: types.SimpleNamespace(stdout=out)
        self.assertEqual(rs.fusion_pids(run=fake), [202, 303])

        def broken(*a, **k):
            raise OSError("no ps")
        self.assertIsNone(rs.fusion_pids(run=broken))

    def test_a_doc_step_installs_the_logger_and_labels_its_opens(self):
        t = OpenLogTests()
        core = t.fake_core()
        adsk = types.ModuleType("adsk")
        adsk.core, adsk.fusion = core, types.ModuleType("adsk.fusion")
        keep = {k: sys.modules.get(k) for k in ("adsk", "adsk.core", "adsk.fusion")}
        sys.modules.update({"adsk": adsk, "adsk.core": core, "adsk.fusion": adsk.fusion})
        try:
            exec(compile(rs.doc_script("open", "N_CAD", open_log=self.log, run_label="TEST: doc step"),
                         "doc_step", "exec"), {})

            class F:
                name, versionNumber = "Y_P01_CAD", 2
            core.Documents().open(F(), True)
        finally:
            for k, v in keep.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        with open(self.log) as fh:
            lines = fh.read().splitlines()
        self.assertIn("start open Y_P01_CAD v2 visible; run: TEST: doc step", lines[0])
        self.assertRegex(lines[1], r"end open Y_P01_CAD v2 after [0-9.]+ s: ok$")


class FreshModulesTests(unittest.TestCase):
    """Fusion keeps Python modules between runs: every run must import its own files,
    not a module of the same name another run loaded (live 2026-10-31), and a team's
    own edits must show on its next run (PM rule for the #156 follow-up)."""

    def setUp(self):
        self.keep = (rs.REPO_ROOT, rs.git_worktrees, list(sys.path))
        not_tmp = os.path.expanduser("~/Library/Caches")
        if not os.path.isdir(not_tmp):
            not_tmp = os.path.expanduser("~")
        self.dirs = [tempfile.mkdtemp(prefix="wt-under-tmp-", dir="/tmp"),       # like AIR's scratch worktree
                     tempfile.mkdtemp(prefix="wt-not-tmp-", dir=not_tmp)]        # like the team worktrees
        self.trees = {"MAIN": os.path.join(self.dirs[1], "main-checkout"),     # git lists it first
                      "A": os.path.join(self.dirs[0], "wtA"), "B": os.path.join(self.dirs[1], "worktrees", "wtB"),
                      "C": os.path.join(self.dirs[1], "worktrees", "wtC")}
        for key, root in self.trees.items():
            self.helper(key, key)
            with open(os.path.join(root, "script.py"), "w") as fh:
                fh.write("import os, sys\n"
                         "sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))\n"
                         "import shared_helper\n"
                         "def run(_c):\n    RESULT.append(shared_helper.VALUE)\n")
        rs.git_worktrees = lambda repo_root=None: list(self.trees.values())     # what git would list

    def helper(self, key, value):
        lib = os.path.join(self.trees[key], "lib")
        os.makedirs(lib, exist_ok=True)
        with open(os.path.join(lib, "shared_helper.py"), "w") as fh:
            fh.write("VALUE = %r\n" % value)

    def tearDown(self):
        rs.REPO_ROOT, rs.git_worktrees, path = self.keep
        sys.path[:] = path
        sys.modules.pop("shared_helper", None)
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def run_as(self, key, result):
        rs.REPO_ROOT = self.trees[key]
        path = os.path.join(self.trees[key], "script.py")
        with open(path) as fh:
            wrapped = rs.wrap_script(fh.read(), path, {})
        ns = {}
        exec(compile(wrapped, "wrapper", "exec"), ns)                 # what Fusion runs
        ns["_NS"]["RESULT"] = result
        ns["run"](None)
        return result

    def test_two_worktrees_under_different_parents_both_orders(self):
        self.assertEqual(self.run_as("A", []) + self.run_as("B", []) + self.run_as("A", []), ["A", "B", "A"])
        self.assertEqual(self.run_as("B", []) + self.run_as("A", []) + self.run_as("B", []), ["B", "A", "B"])

    def test_a_run_from_the_main_checkout_gets_its_own(self):
        self.assertEqual(self.run_as("A", []) + self.run_as("MAIN", []) + self.run_as("B", []),
                         ["A", "MAIN", "B"])

    def test_an_edited_own_helper_shows_on_the_next_run(self):
        self.assertEqual(self.run_as("A", []), ["A"])
        self.helper("A", "A, edited")
        self.assertEqual(self.run_as("A", []), ["A, edited"])

    def test_a_deleted_worktrees_module_still_drops(self):
        # Reviewer 5's note on #157: a worktree removed after its run loaded a module
        self.assertEqual(self.run_as("C", []), ["C"])
        self.assertTrue(sys.modules["shared_helper"].__file__.startswith(self.trees["C"]))
        del self.trees["C"]                                          # no longer in git's list
        self.assertEqual(self.run_as("B", []), ["B"])                # its parent folder still covers it

    def test_the_main_checkouts_parent_is_not_swept(self):
        roots = rs.team_roots()
        self.assertIn(os.path.dirname(self.trees["B"]), roots)         # the worktrees' folder
        self.assertNotIn(os.path.dirname(self.trees["MAIN"]), roots)   # not the main checkout's parent

    def test_a_failing_git_list_warns(self):
        rs.git_worktrees = self.keep[1]
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            trees = rs.git_worktrees("/nonexistent-folder-for-a-test")
        self.assertEqual(trees, ["/nonexistent-folder-for-a-test"])
        self.assertIn("warning: git worktree list failed", err.getvalue())

    def test_the_home_folder_and_above_are_never_swept(self):
        # PM, after #157: a worktree right in the home folder must not make home a root
        home = os.path.realpath(os.path.expanduser("~"))
        rs.git_worktrees = lambda repo_root=None: [self.trees["MAIN"], os.path.join(home, "a-worktree"),
                                                   self.trees["A"]]
        roots = [os.path.realpath(r) for r in rs.team_roots()]
        self.assertNotIn(home, roots)
        self.assertFalse(any(home.startswith(r.rstrip("/") + "/") for r in roots), roots)
        self.assertIn(os.path.realpath(self.trees["A"]), roots)

    def test_modules_under_fusions_add_in_folder_are_never_dropped(self):
        # a team folder that happens to hold a Fusion add-in: the add-in's module stays
        addins = os.path.join(self.trees["B"], "Autodesk", "AddIns")
        os.makedirs(addins)
        with open(os.path.join(addins, "fake_addin_module.py"), "w") as fh:
            fh.write("LOADED = True\n")
        sys.path.insert(0, addins)
        import fake_addin_module
        keep_roots = rs.keep_roots
        rs.keep_roots = lambda: keep_roots() + [addins]
        try:
            self.assertEqual(self.run_as("B", []), ["B"])
            self.assertIs(sys.modules.get("fake_addin_module"), fake_addin_module)   # not dropped
        finally:
            rs.keep_roots = keep_roots
            sys.modules.pop("fake_addin_module", None)

    def test_main_python_and_odd_modules_are_safe(self):
        import json as _json
        main = sys.modules.get("__main__")

        class Odd:                                                    # its __file__ can't be read
            @property
            def __file__(self):
                raise RuntimeError("odd module")

        sys.modules["odd_test_module"] = Odd()
        try:
            self.assertEqual(self.run_as("A", []), ["A"])           # the run still works
        finally:
            sys.modules.pop("odd_test_module", None)
        self.assertIs(sys.modules["json"], _json)                     # Python's own: kept
        self.assertIs(sys.modules.get("__main__"), main)              # never dropped
        self.assertIn("fusion_folder", sys.modules)                   # given to every run, fresh

    def test_the_team_roots(self):
        rs.git_worktrees = self.keep[1]
        roots = rs.team_roots()
        self.assertIn(rs.REPO_ROOT, [os.path.abspath(r) for r in roots] + [rs.REPO_ROOT])
        self.assertIn("/private/tmp", roots)

if __name__ == "__main__":
    unittest.main(verbosity=2)
