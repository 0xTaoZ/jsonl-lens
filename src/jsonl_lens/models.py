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
class JsonlProfile:
    total_lines: int
    valid_records: int
    invalid_lines: int
    field_counts: list[tuple[str, int]]
    field_type_counts: list[tuple[str, list[tuple[str, int]]]]
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
            "issues": [issue.to_dict() for issue in self.issues],
            "samples": self.samples,
        }
