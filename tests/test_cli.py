import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
