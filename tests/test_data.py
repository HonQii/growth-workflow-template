"""Offline contract tests. Fixtures do not prove live account access."""
import argparse
import base64
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "growth/scripts"))
import data as cli
from growth_data import core, providers, reports
from growth_data.compare import compare

APPLE = {"enabled": True, "app_id": "123", "report": "discovery", "timezone": "UTC"}
PLAY = {"enabled": True, "package_name": "com.example.app", "bucket": "example", "breakdown": "country", "timezone": "UTC"}
GSC = {"enabled": True, "site_url": "sc-domain:example.com", "dimensions": ["date"]}
WINDOW = {"start": "2024-01-01", "end": "2024-01-01"}


def csv_bytes(fields, values, encoding="utf-8", delimiter=","):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=delimiter)
    writer.writerow(fields)
    writer.writerows(values)
    return stream.getvalue().encode(encoding)


def apple_csv(count=10, day="2024-01-01", device="iPhone"):
    fields = ["Date", "App Name", "App Apple Identifier", *reports.APPLE_DIMENSIONS["discovery"], "Counts", "Unique Counts"]
    return csv_bytes(fields, [[day, "Example", "123", "Impression", "No page", "App Store search", "", device, "18", "USA", count, 5]], delimiter="\t")


def play_csv(day="2024-01-01", acquisitions=5, visitors=10):
    return csv_bytes(["Date", "Package name", "Country", *reports.PLAY_METRICS],
                     [[day, "com.example.app", "US", acquisitions, visitors, "50%"]], encoding="utf-16")


class FakeHTTP:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def next(self, url, kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def json(self, url, **kwargs):
        return self.next(url, kwargs)

    def request(self, url, **kwargs):
        return self.next(url, kwargs)


class ParserTests(unittest.TestCase):
    def test_utf16_play_and_gzipped_apple(self):
        play = reports.normalize(play_csv(), "play", PLAY, WINDOW)
        self.assertEqual(play[0]["metrics"], {"acquisitions": 5, "visitors": 10, "conversion_rate": .5})
        apple = reports.normalize(gzip.compress(apple_csv()), "apple", APPLE, WINDOW)
        self.assertEqual(apple[0]["metrics"]["counts"], 10)

    def test_identity_schema_and_conflicts(self):
        with self.assertRaisesRegex(core.DataError, "other than"):
            reports.normalize(apple_csv().replace(b"123", b"456"), "apple", APPLE, WINDOW)
        with self.assertRaisesRegex(core.DataError, "Unsupported Apple"):
            reports.normalize(apple_csv().replace(b"Counts\t", b"Count\t"), "apple", APPLE, WINDOW)
        a = reports.normalize(apple_csv(), "apple", APPLE, WINDOW)
        self.assertEqual(reports.deduplicate(a+a), a)
        with self.assertRaisesRegex(core.DataError, "Conflicting"):
            reports.deduplicate(a + reports.normalize(apple_csv(20), "apple", APPLE, WINDOW))

    def test_null_is_not_zero_and_invalid_counts_fail(self):
        self.assertIsNone(reports.number("-"))
        self.assertEqual(reports.number("0"), 0)
        for value in ("NaN", "Infinity", "-1", "1.5", "3%"):
            with self.assertRaises(core.DataError):
                reports.number(value)
        self.assertEqual(reports.number("5%", rate=True), .05)

    def test_downloads_and_traffic_source_keep_their_grain(self):
        settings = dict(APPLE, report="downloads")
        fields = ["Date", "App Name", "App Apple Identifier", *reports.APPLE_DIMENSIONS["downloads"], "Counts"]
        raw = csv_bytes(fields, [["2024-01-01", "Example", "123", "First-time Download", "1.0", "iPhone", "18", "App Store search", "Product page", "false", "USA", 8]])
        rows = reports.normalize(raw, "apple", settings, WINDOW)
        self.assertEqual(rows[0]["dimensions"]["Download Type"], "First-time Download")
        self.assertEqual(rows[0]["metrics"], {"counts": 8})
        fields = ["Date", "Package name", "Traffic source", "Search term", "UTM source", "UTM campaign", *reports.PLAY_METRICS]
        raw = csv_bytes(fields, [["2024-01-01", "com.example.app", "Google Play search", "food", "", "", 5, 10, ".5"]])
        rows = reports.normalize(raw, "play", dict(PLAY, breakdown="traffic_source"), WINDOW)
        self.assertEqual(rows[0]["dimensions"]["Search term"], "food")
        self.assertEqual(rows[0]["metrics"]["conversion_rate"], .5)

    def test_source_mismatch_outside_window_still_fails(self):
        raw = apple_csv(day="2023-01-01").replace(b"123", b"999")
        with self.assertRaises(core.DataError):
            reports.normalize(raw, "apple", APPLE, WINDOW)

    def test_detailed_report_is_rejected(self):
        raw = apple_csv().replace(b"Counts\tUnique Counts", b"Campaign\tCounts\tUnique Counts").replace(b"10\t5", b"campaign\t10\t5")
        with self.assertRaisesRegex(core.DataError, "Detailed"):
            reports.normalize(raw, "apple", APPLE, WINDOW)


class AdapterTests(unittest.TestCase):
    def test_gsc_daily_queries_preserve_filters_and_aggregation(self):
        row = {"keys": ["2024-01-01"], "clicks": 3, "impressions": 10, "ctr": .3, "position": 2.5}
        http = FakeHTTP([{"rows": [row], "responseAggregationType": "byProperty"}, {}])
        settings = dict(GSC, filter_groups=[{"filters": [{"dimension": "country", "expression": "usa"}]}])
        rows, raw, meta, errors = providers.gsc_fetch(http, settings, {"start": "2024-01-01", "end": "2024-01-02"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(meta["response_aggregation"], "byProperty")
        self.assertEqual(http.calls[1][1]["body"]["startDate"], "2024-01-02")
        self.assertEqual(http.calls[0][1]["body"]["dimensionFilterGroups"], settings["filter_groups"])

    def test_gsc_pagination_and_repeated_page(self):
        batch = [{"keys": ["2024-01-01", f"https://example.com/{i}"], "clicks": 0, "impressions": 1, "ctr": 0, "position": 1} for i in range(25000)]
        page = {"rows": batch, "responseAggregationType": "byPage"}
        http = FakeHTTP([page, {}])
        rows, *_ = providers.gsc_fetch(http, dict(GSC, dimensions=["date", "page"]), WINDOW)
        self.assertEqual(len(rows), 25000)
        self.assertEqual(http.calls[1][1]["body"]["startRow"], 25000)
        with self.assertRaisesRegex(core.DataError, "repeated"):
            providers.gsc_fetch(FakeHTTP([page, page]), dict(GSC, dimensions=["date", "page"]), WINDOW)

    def apple_prefix(self):
        return [{"data": [{"id": "req", "attributes": {"accessType": "ONGOING"}}]},
                {"data": [{"id": "report", "attributes": {"name": "App Store Discovery and Engagement"}}]},
                {"data": [{"id": "old", "attributes": {"granularity": "DAILY", "processingDate": "2024-01-02"}},
                          {"id": "new", "attributes": {"granularity": "DAILY", "processingDate": "2024-02-02"}}]}]

    def segment(self, raw):
        return {"id": "seg", "attributes": {"url": "https://download.example/secret-signed-url", "checksum": hashlib.md5(raw).hexdigest(), "sizeInBytes": len(raw)}}

    def test_apple_latest_instance_replaces_entire_date(self):
        old = apple_csv(10)
        old2 = apple_csv(7, device="iPad")
        new = apple_csv(12)
        http = FakeHTTP(self.apple_prefix() + [{"data": [self.segment(old), self.segment(old2)]}, old, old2,
                                             {"data": [self.segment(new)]}, new])
        rows, raw, meta, errors = providers.apple_fetch(http, APPLE, WINDOW)
        self.assertEqual(len(rows), 1)  # The disappeared iPad row must not survive correction.
        self.assertEqual(rows[0]["metrics"]["counts"], 12)
        self.assertEqual(meta["event_date_revisions"]["2024-01-01"]["processing_date"], "2024-02-02")
        self.assertNotIn("secret-signed-url", core.canonical(meta))
        download_calls = [kwargs for url, kwargs in http.calls if "download.example" in url]
        self.assertTrue(all(kwargs["authenticated"] is False for kwargs in download_calls))

    def test_apple_standard_suffix_is_recognized(self):
        prefix = self.apple_prefix()
        prefix[1]["data"][0]["attributes"]["name"] += " Standard"
        self.assertEqual(providers.apple_report(FakeHTTP(prefix[:2]), APPLE), "report")

    def test_apple_incomplete_revision_fails_without_using_stale_data(self):
        old = apple_csv()
        http = FakeHTTP(self.apple_prefix() + [{"data": [self.segment(old)]}, old, {"data": []}])
        with self.assertRaisesRegex(core.DataError, "no segments"):
            providers.apple_fetch(http, APPLE, WINDOW)

    def test_apple_requires_setup_and_checks_checksum(self):
        with self.assertRaisesRegex(core.DataError, "ONGOING"):
            providers.apple_report(FakeHTTP([{"data": []}]), APPLE)
        segment = self.segment(apple_csv())
        http = FakeHTTP(self.apple_prefix() + [{"data": [segment]}, apple_csv(99)])
        with self.assertRaisesRegex(core.DataError, "MD5"):
            providers.apple_fetch(http, APPLE, WINDOW)

    def test_play_missing_month_retains_other_month_and_pins_generation(self):
        raw = play_csv()
        http = FakeHTTP([{"generation": "42", "md5Hash": base64.b64encode(hashlib.md5(raw).digest()).decode()}, raw,
                         core.DataError("http_404", "Missing", "unavailable")])
        rows, raw_parts, meta, errors = providers.play_fetch(http, PLAY, {"start": "2024-01-01", "end": "2024-02-01"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(errors[0]["month"], "202402")
        self.assertIn("alt=media&generation=42", http.calls[1][0])
        self.assertIn("stats%2Fstore_performance", http.calls[0][0])

    def test_fetch_failure_does_not_report_zero_or_write_snapshot(self):
        args = argparse.Namespace(command="fetch")
        config = {"project": "test", "sources": {"gsc": GSC}}
        with tempfile.TemporaryDirectory() as folder, patch.object(cli, "GROWTH", Path(folder)):
            out = cli.run_source(args, config, "gsc", WINDOW, FakeHTTP([core.DataError("http_403", "Denied", "unavailable")]))
            self.assertEqual(out["status"], "unavailable")
            self.assertIsNone(out["row_count"])
            self.assertFalse((Path(folder)/".local-data").exists())


class ComparisonTests(unittest.TestCase):
    def snapshot(self, root, day, clicks, impressions, source="gsc", extra=None):
        out = core.result(source, "test", {"start": day, "end": day})
        out["definition"] = providers.describe(source, GSC if source == "gsc" else APPLE)
        out["limitations"] = []
        metrics = {"clicks": clicks, "impressions": impressions, "ctr": clicks/impressions if impressions else 0, "position": 2} if source == "gsc" else {"counts": clicks, "unique_counts": impressions}
        rows = [{"date": day, "dimensions": {}, "metrics": metrics}]
        core.coverage(out, rows, out["requested_window"])
        if extra:
            out.update(extra)
        return core.save_snapshot(Path(root), out, rows, [])

    def test_comparison_null_zero_baseline_and_no_unique_sum(self):
        with tempfile.TemporaryDirectory() as root:
            a = self.snapshot(root, "2024-01-01", 0, 10)
            b = self.snapshot(root, "2024-01-02", 2, 20)
            metrics = compare(a["manifest_path"], b["manifest_path"])["groups"][0]["metrics"]
            self.assertIsNone(metrics["clicks"]["relative_change"])
            self.assertEqual(metrics["ctr"]["after"], .1)
            a = self.snapshot(root, "2024-01-01", 10, 5, "apple")
            b = self.snapshot(root, "2024-01-02", 20, 6, "apple")
            self.assertNotIn("unique_counts", compare(a["manifest_path"], b["manifest_path"])["groups"][0]["metrics"])

    def test_incompatible_scope_partial_and_modified_rows_fail(self):
        with tempfile.TemporaryDirectory() as root:
            a = self.snapshot(root, "2024-01-01", 1, 10)
            for extra in ({"project": "other"}, {"status": "partial"}, {"dates_without_rows": ["2024-01-02"]}):
                b = self.snapshot(root, "2024-01-02", 2, 20, extra=extra)
                with self.assertRaises(core.DataError):
                    compare(a["manifest_path"], b["manifest_path"])
            b = self.snapshot(root, "2024-01-02", 2, 20)
            Path(b["rows_path"]).write_text("[]")
            with self.assertRaisesRegex(core.DataError, "changed"):
                compare(a["manifest_path"], b["manifest_path"])

    def test_repeated_snapshot_is_not_an_accumulator(self):
        with tempfile.TemporaryDirectory() as root:
            a = self.snapshot(root, "2024-01-01", 1, 10)
            b = self.snapshot(root, "2024-01-01", 1, 10)
            self.assertNotEqual(a["manifest_path"], b["manifest_path"])
            self.assertEqual(Path(a["rows_path"]).read_bytes(), Path(b["rows_path"]).read_bytes())
            with self.assertRaisesRegex(core.DataError, "non-overlapping"):
                compare(a["manifest_path"], b["manifest_path"])


class CLITests(unittest.TestCase):
    def test_copied_workspace_cli_runs_without_template_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([sys.executable, str(ROOT / "scripts/init.py"), temp], check=True, capture_output=True)
            growth = Path(temp)/"growth"
            config = growth/"config.local.json"
            config.write_text(json.dumps({"project": "test", "sources": {"play": PLAY}}))
            report = Path(temp)/"input.csv"
            report.write_bytes(play_csv())
            command = [sys.executable, str(growth/"scripts/data.py")]
            doctor = subprocess.run(command+["doctor", "all"], capture_output=True, text=True)
            self.assertEqual(doctor.returncode, 0, doctor.stdout)
            self.assertFalse(json.loads(doctor.stdout)["results"][0]["access_verified"])
            imported = subprocess.run(command+["import", "play", "--start", "2024-01-01", "--end", "2024-01-01", "--file", str(report)], capture_output=True, text=True)
            self.assertEqual(imported.returncode, 0, imported.stdout+imported.stderr)
            out = json.loads(imported.stdout)
            self.assertEqual(out["row_count"], 1)
            self.assertTrue(Path(out["manifest_path"]).is_file())
            self.assertIn(str(growth), out["manifest_path"])
            invalid = subprocess.run(command+["fetch", "gsc", "--start", "secret"], capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertNotIn("secret", invalid.stdout + invalid.stderr)
            self.assertEqual(json.loads(invalid.stdout)["error_code"], "invalid_arguments")

    def test_all_sources_isolates_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp)/"config.json"
            config.write_text(json.dumps({"project": "test", "sources": {"gsc": GSC, "play": PLAY}}))
            outputs = [{"status": "unavailable", "source": "gsc"}, {"status": "ok", "source": "play"}]
            with patch.object(cli, "run_source", side_effect=outputs) as runner, patch("sys.stdout", new_callable=io.StringIO) as output:
                exit_code = cli.main(["--config", str(config), "fetch", "all", "--start", "2024-01-01", "--end", "2024-01-01"])
            self.assertEqual(exit_code, 2)
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(len(json.loads(output.getvalue())["results"]), 2)

    def test_http_retries_are_bounded_and_errors_are_sanitized(self):
        import urllib.error
        from unittest.mock import Mock
        http = core.HTTP(lambda: "private-token", "api.example.com")
        http.opener = Mock()
        http.opener.open.side_effect = [urllib.error.HTTPError("https://api.example.com/?secret", 503, "private-body", {}, io.BytesIO(b"private-body")) for _ in range(3)]
        with patch.object(core.time, "sleep") as sleep:
            with self.assertRaises(core.DataError) as raised:
                http.request("https://api.example.com/")
        self.assertEqual(http.opener.open.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(raised.exception.code, "http_503")
        self.assertNotIn("private", str(raised.exception))
        self.assertEqual(http.opener.open.call_args.kwargs["timeout"], 30)

    def test_immature_import_is_partial_even_when_event_date_is_old(self):
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp)/"report.tsv"
            report.write_bytes(apple_csv())
            args = argparse.Namespace(command="import", file=[report], processing_date="2024-01-02")
            with patch.object(cli, "GROWTH", Path(temp)):
                out = cli.run_source(args, {"project": "test", "sources": {"apple": APPLE}}, "apple", WINDOW)
            self.assertEqual(out["status"], "partial")
            self.assertEqual(out["row_count"], 1)

    def test_transport_refuses_credential_forwarding(self):
        http = core.HTTP(lambda: "secret", "api.example.com")
        with self.assertRaisesRegex(core.DataError, "another host"):
            http.request("https://evil.example.com/")
        with self.assertRaises(core.DataError):
            http.request("http://api.example.com/")


if __name__ == "__main__":
    unittest.main()
