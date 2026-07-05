import json
from collections import Counter
from pathlib import Path
from typing import Any

from .models import JsonlIssue, JsonlProfile


def profile_file(path: str | Path, sample_limit: int = 3) -> JsonlProfile:
    return profile_lines(Path(path).read_text(encoding="utf-8").splitlines(), sample_limit)


def profile_lines(lines: list[str], sample_limit: int = 3) -> JsonlProfile:
    field_counter: Counter[str] = Counter()
    field_type_counters: dict[str, Counter[str]] = {}
    issues: list[JsonlIssue] = []
    samples: list[dict[str, Any]] = []
    valid_records = 0

    for index, line in enumerate(lines, start=1):
        if not line.strip():
            issues.append(JsonlIssue(index, "blank line"))
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            issues.append(JsonlIssue(index, f"invalid JSON: {error.msg}"))
            continue

        if not isinstance(record, dict):
            issues.append(JsonlIssue(index, "record is not a JSON object"))
            continue

        valid_records += 1
        field_counter.update(record.keys())
        for field, value in record.items():
            field_type_counters.setdefault(field, Counter()).update(
                [_json_type_name(value)]
            )
        if len(samples) < sample_limit:
            samples.append(record)

    field_counts = field_counter.most_common()
    return JsonlProfile(
        total_lines=len(lines),
        valid_records=valid_records,
        invalid_lines=len(issues),
        field_counts=field_counts,
        field_type_counts=[
            (field, field_type_counters[field].most_common())
            for field, _count in field_counts
        ],
        issues=issues,
        samples=samples,
    )


def _json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__
