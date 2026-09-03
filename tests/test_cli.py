import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTest(unittest.TestCase):
    def test_sample_report_runs(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertIn("Valid records: 3", result.stdout)
        self.assertIn("Invalid lines: 2", result.stdout)
        self.assertIn("Field types", result.stdout)
        self.assertIn("- duration_ms: number=1", result.stdout)

    def test_text_report_shows_mixed_type_warnings(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"id": 1}\n')
            handle.write('{"id": "2"}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        self.assertIn("Warnings", result.stdout)
        self.assertIn("- id: mixed value types: number=1, string=1", result.stdout)

    def test_max_issues_limits_text_report_noise(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write("{bad one\n")
            handle.write("{bad two\n")
            handle.write("{bad three\n")
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--max-issues",
                    "2",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        self.assertIn("line 1: invalid JSON", result.stdout)
        self.assertIn("line 2: invalid JSON", result.stdout)
        self.assertNotIn("line 3: invalid JSON", result.stdout)
        self.assertIn("... 1 more issue(s)", result.stdout)

    def test_fields_only_hides_issues_and_samples(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--fields-only",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertIn("Fields", result.stdout)
        self.assertIn("Field types", result.stdout)
        self.assertIn("- timestamp: 3", result.stdout)
        self.assertNotIn("Issues", result.stdout)
        self.assertNotIn("Samples", result.stdout)

    def test_fields_only_can_include_and_exclude_fields(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--fields-only",
                "--include-field",
                "request_id",
                "--include-field",
                "duration_ms",
                "--exclude-field",
                "request_id",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertIn("- duration_ms: 1", result.stdout)
        self.assertIn("- duration_ms: number=1", result.stdout)
        self.assertNotIn("request_id", result.stdout)
        self.assertNotIn("timestamp", result.stdout)

    def test_fields_only_prints_common_scalar_values(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--fields-only",
                "--include-field",
                "level",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertIn("Common values", result.stdout)
        self.assertIn("- level: info=1, warn=1, error=1", result.stdout)
        self.assertNotIn("service:", result.stdout)

    def test_fields_only_prints_missing_and_null_counts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"user": "alice", "mfa": true, "src_ip": "198.51.100.10"}\n')
            handle.write('{"user": "bob", "mfa": null}\n')
            handle.write('{"user": "carol", "src_ip": "203.0.113.8"}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--fields-only",
                    "--include-field",
                    "mfa",
                    "--include-field",
                    "src_ip",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        self.assertIn("Field gaps", result.stdout)
        self.assertIn("- mfa: missing=1, null=1", result.stdout)
        self.assertIn("- src_ip: missing=1, null=0", result.stdout)
        self.assertNotIn("user:", result.stdout)

    def test_max_values_limits_common_value_noise(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"id": "a"}\n')
            handle.write('{"id": "b"}\n')
            handle.write('{"id": "c"}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--fields-only",
                    "--max-values",
                    "2",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        self.assertIn("- id: a=1, b=1", result.stdout)
        self.assertNotIn("c=1", result.stdout)
        self.assertIn("- ... 1 more value(s) for id", result.stdout)

    def test_max_samples_limits_text_report_samples(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--max-samples",
                "1",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertIn("Samples", result.stdout)
        self.assertIn('"request_id": "req-001"', result.stdout)
        self.assertNotIn('"request_id": "req-002"', result.stdout)

    def test_max_samples_zero_hides_text_report_samples(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--max-samples",
                "0",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        self.assertNotIn("Samples", result.stdout)
        self.assertNotIn('"request_id": "req-001"', result.stdout)

    def test_json_fields_only_honors_field_filters(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jsonl_lens",
                str(PROJECT_ROOT / "samples" / "events.jsonl"),
                "--json",
                "--fields-only",
                "--include-field",
                "level",
            ],
            check=True,
            capture_output=True,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["field_counts"], [{"field": "level", "count": 3}])
        self.assertEqual(
            payload["field_type_counts"],
            [{"field": "level", "types": [{"type": "string", "count": 3}]}],
        )
        self.assertEqual(
            payload["field_value_counts"],
            [
                {
                    "field": "level",
                    "values": [
                        {"value": "info", "count": 1},
                        {"value": "warn", "count": 1},
                        {"value": "error", "count": 1},
                    ],
                }
            ],
        )

    def test_json_fields_only_includes_filtered_missing_and_null_counts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"event": "login", "mfa": true}\n')
            handle.write('{"event": "login", "mfa": null}\n')
            handle.write('{"event": "logout"}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--json",
                    "--fields-only",
                    "--include-field",
                    "mfa",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["field_absence_counts"],
            [{"field": "mfa", "missing": 1, "null": 1}],
        )

    def test_fields_only_prints_one_level_nested_fields(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"event": "request", "http": {"method": "GET", "status": 200}}\n')
            handle.write('{"event": "request", "http": {"method": "POST"}}\n')
            handle.write('{"event": "login", "user": {"name": "alice"}}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--fields-only",
                    "--include-field",
                    "http.method",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        self.assertIn("Nested fields", result.stdout)
        self.assertIn("- http.method: 2", result.stdout)
        self.assertNotIn("http.status", result.stdout)
        self.assertNotIn("user.name", result.stdout)

    def test_json_fields_only_includes_filtered_nested_fields(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl") as handle:
            handle.write('{"event": "request", "http": {"method": "GET", "status": 200}}\n')
            handle.write('{"event": "request", "http": {"method": "POST"}}\n')
            handle.flush()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jsonl_lens",
                    handle.name,
                    "--json",
                    "--fields-only",
                    "--include-field",
                    "http.status",
                ],
                check=True,
                capture_output=True,
                env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
                text=True,
            )

        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["nested_field_counts"],
            [{"field": "http.status", "count": 1}],
        )


if __name__ == "__main__":
    unittest.main()
