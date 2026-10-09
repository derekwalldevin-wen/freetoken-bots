#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "radar", Path(__file__).resolve().parents[1] / "scripts" / "radar.py"
)
radar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)


class FreeIdTests(unittest.TestCase):
    def test_free_marker(self):
        self.assertTrue(radar.is_free_candidate("opencode/longcat-2.5-preview-free"))
        self.assertTrue(radar.is_free_candidate("opencode/space-bunny-free"))
        self.assertTrue(radar.is_free_candidate("opencode/ling-3.1-flash-free"))

    def test_known_allowlist(self):
        self.assertTrue(radar.is_free_candidate("opencode/nemotron-3.5-lightning-free"))

    def test_paid_refused(self):
        self.assertFalse(radar.is_free_candidate("opencode/some-zen-paid"))
        self.assertFalse(radar.is_free_candidate("volcengine/doubao-pro"))

    def test_ensure_free_exits_on_paid(self):
        with self.assertRaises(SystemExit):
            radar.ensure_free_model("opencode/definitely-paid-model")


class ClassifyErrorTests(unittest.TestCase):
    def test_rate_limit(self):
        self.assertEqual(radar.classify_error("HTTP 429 Too Many Requests"), "rate_limit_429")

    def test_quota(self):
        self.assertEqual(radar.classify_error("insufficient credits"), "quota_exhausted")


class ClassifyScanTests(unittest.TestCase):
    def test_eligible_empty_until_probe(self):
        out = radar.classify(
            [
                "opencode/longcat-2.5-preview-free",
                "volcengine/paid-thing",
                "opencode/space-bunny-free",
            ]
        )
        ids = [c["id"] for c in out["candidates"]]
        self.assertEqual(
            ids,
            ["opencode/longcat-2.5-preview-free", "opencode/space-bunny-free"],
        )
        self.assertEqual(out["eligible"], [])


class SyncFailClosedTests(unittest.TestCase):
    def test_sync_without_dry_run_refuses(self):
        ns = argparse_ns(dry_run=False)
        # need a report file for path after dry-run check — dry-run false returns 2 first
        code = radar.cmd_sync(ns)
        self.assertEqual(code, 2)


def argparse_ns(**kwargs):
    class NS:
        pass

    ns = NS()
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


if __name__ == "__main__":
    unittest.main()
