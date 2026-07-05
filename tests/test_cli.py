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


if __name__ == "__main__":
    unittest.main()
