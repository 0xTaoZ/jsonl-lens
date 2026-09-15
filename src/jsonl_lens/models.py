from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JsonlIssue:
    line_number: int
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "line_number": self.line_number,
            "message": self.message,
        }


@dataclass(frozen=True)
class JsonlWarning:
    field: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "field": self.field,
            "message": self.message,
        }


@dataclass(frozen=True)
class JsonlProfile:
    total_lines: int
    valid_records: int
    invalid_lines: int
    field_counts: list[tuple[str, int]]
    field_type_counts: list[tuple[str, list[tuple[str, int]]]]
    field_value_counts: list[tuple[str, list[tuple[str, int]]]]
    field_absence_counts: list[tuple[str, tuple[int, int]]]
    nested_field_counts: list[tuple[str, int]]
    high_cardinality_fields: list[tuple[str, int, int]]
    record_length_summary: dict[str, float] | None
    warnings: list[JsonlWarning]
    issues: list[JsonlIssue]
    samples: list[dict[str, Any]]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_lines": self.total_lines,
            "valid_records": self.valid_records,
            "invalid_lines": self.invalid_lines,
            "field_counts": [
                {"field": field, "count": count}
                for field, count in self.field_counts
            ],
            "field_type_counts": [
                {
                    "field": field,
                    "types": [
                        {"type": type_name, "count": count}
                        for type_name, count in type_counts
                    ],
                }
                for field, type_counts in self.field_type_counts
            ],
            "field_value_counts": [
                {
                    "field": field,
                    "values": [
                        {"value": value, "count": count}
                        for value, count in value_counts
                    ],
                }
                for field, value_counts in self.field_value_counts
            ],
            "field_absence_counts": [
                {"field": field, "missing": missing, "null": null}
                for field, (missing, null) in self.field_absence_counts
            ],
            "nested_field_counts": [
                {"field": field, "count": count}
                for field, count in self.nested_field_counts
            ],
            "high_cardinality_fields": [
                {
                    "field": field,
                    "distinct_values": distinct_values,
                    "records": records,
                }
                for field, distinct_values, records in self.high_cardinality_fields
            ],
            "record_length_summary": self.record_length_summary,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "issues": [issue.to_dict() for issue in self.issues],
            "samples": self.samples,
        }
