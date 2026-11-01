#!/usr/bin/env python3
"""Offline tests for fusion_activity.py (no Fusion, no log of the Mac's own).

    python3 tools/fusion/test_fusion_activity.py
"""

import datetime
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fusion_activity as fa  # noqa: E402

NOW = datetime.datetime(2026, 11, 1, 8, 9, 0)


def line(hhmmss, thread, text):
    return "20261101T%s I %s %s\n" % (hhmmss, thread, text)


FETCH = ("GET 200 https://api.example/symphonydm/v2/folders/urn/content?offset=0&limit=100 - "
         "workflow:Symphonydm::getFolderContents attempt:0")
BACKGROUND = [
    line("080700", "37417598", "PUT 200 https://f360sc.example/api/v1/sessions/x - workflow:SLM_heartbeat attempt:0"),
    line("080701", "37416441", "GET 200 https://js.example/hds/fusion_status.json - workflow:HTTPClient attempt:0"),
    line("080702", ".37414717", "[HubDetailsCmdDef::onIsApplicable] isRegionalizationEnabled : Disabled"),
    line("080703", ".37414717", "IdleUserCheck: Timeout"),
    line("080704", "39005266", "Thread FeaturePackExpirationTask has been started"),
]


class ActivityTests(unittest.TestCase):
    def check(self, lines, cpu):
        return fa.verdict(fa.work_counts(lines, NOW, 3), cpu, 3, 10)

    def test_a_busy_folder_scan_is_active_even_with_no_cpu(self):
        # live 2026-11-01 00:54-01:09 UTC: 117 folder fetches in 3 min, CPU under 1 %
        code, text = self.check([line("0808%02d" % s, ".39251969", FETCH) for s in range(0, 60, 2)], 0.9)
        self.assertEqual(code, 0)
        self.assertIn("30 folder listing fetches", text)

    def test_background_lines_alone_are_quiet(self):
        # live 2026-11-01 00:23-00:51 UTC: a drawing open that never ended left only these
        code, text = self.check(BACKGROUND, 0.2)
        self.assertEqual(code, 1)
        self.assertIn("QUIET", text)

    def test_local_work_shows_as_cpu(self):
        self.assertEqual(self.check(BACKGROUND, 40.0)[0], 0)

    def test_work_before_the_window_does_not_count(self):
        self.assertEqual(self.check([line("075000", ".1", FETCH)], 0.2)[0], 1)

    def test_an_open_that_starts_is_work(self):
        code, text = self.check([line("080800", ".37414717", "Workflow start: OpenDrawing 1-6ae6868e")], 0.0)
        self.assertEqual(code, 0)
        self.assertIn("1 open/save/workflow steps", text)

    def test_the_report_never_holds_log_text(self):
        secret = line("080800", "1", "[OS3] GET 200 /oss/objects/someone__gmail123_Recents - workflow:WIPRequest4")
        _code, text = self.check([secret] + BACKGROUND, 0.0)
        self.assertNotIn("gmail", text)
        self.assertNotIn("oss/objects", text)

    def test_cpu_time_from_ps(self):
        self.assertAlmostEqual(fa.parse_cpu_time("05:10.50"), 310.5)
        self.assertAlmostEqual(fa.parse_cpu_time("1:02:03.45"), 3723.45)
        self.assertAlmostEqual(fa.parse_cpu_time("2-01:00:00"), 2 * 86400 + 3600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
