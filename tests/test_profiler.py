import unittest

from jsonl_lens.profiler import profile_lines


class ProfilerTest(unittest.TestCase):
    def test_profile_lines_counts_fields_and_issues(self):
        lines = [
            '{"level": "info", "service": "api", "message": "started"}',
            '{"level": "error", "service": "worker", "trace_id": "abc"}',
            '{bad json',
            '["not", "object"]',
            "",
        ]

        profile = profile_lines(lines)

        self.assertEqual(profile.total_lines, 5)
        self.assertEqual(profile.valid_records, 2)
        self.assertEqual(profile.invalid_lines, 3)
        self.assertIn(("level", 2), profile.field_counts)
        self.assertIn(("trace_id", 1), profile.field_counts)

    def test_profile_lines_keeps_sample_records(self):
        lines = [
            '{"id": 1}',
            '{"id": 2}',
            '{"id": 3}',
        ]

        profile = profile_lines(lines, sample_limit=2)

        self.assertEqual(profile.samples, [{"id": 1}, {"id": 2}])


if __name__ == "__main__":
    unittest.main()
