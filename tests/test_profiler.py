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

    def test_profile_lines_counts_json_value_types_by_field(self):
        lines = [
            '{"id": 1, "ok": true, "tags": ["prod"], "meta": {"ip": "127.0.0.1"}}',
            '{"id": "2", "ok": false, "tags": null, "meta": {}}',
            '{"id": 3, "ok": true, "tags": ["test"], "meta": null}',
        ]

        profile = profile_lines(lines)
        field_types = dict(profile.field_type_counts)

        self.assertEqual(field_types["id"], [("number", 2), ("string", 1)])
        self.assertEqual(field_types["ok"], [("boolean", 3)])
        self.assertEqual(field_types["tags"], [("array", 2), ("null", 1)])
        self.assertEqual(field_types["meta"], [("object", 2), ("null", 1)])
        self.assertEqual(
            [(warning.field, warning.message) for warning in profile.warnings],
            [
                ("id", "mixed value types: number=2, string=1"),
                ("tags", "mixed value types: array=2, null=1"),
                ("meta", "mixed value types: object=2, null=1"),
            ],
        )

    def test_profile_lines_counts_common_scalar_values_by_field(self):
        lines = [
            '{"level": "info", "status": 200, "ok": true, "tags": ["api"]}',
            '{"level": "error", "status": 500, "ok": false, "tags": ["worker"]}',
            '{"level": "info", "status": 200, "ok": true, "tags": ["api"]}',
        ]

        profile = profile_lines(lines)
        field_values = dict(profile.field_value_counts)

        self.assertEqual(field_values["level"], [("info", 2), ("error", 1)])
        self.assertEqual(field_values["status"], [("200", 2), ("500", 1)])
        self.assertEqual(field_values["ok"], [("true", 2), ("false", 1)])
        self.assertNotIn("tags", field_values)

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
