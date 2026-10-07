import json
from collections import Counter
from pathlib import Path
from typing import Any

from .models import JsonlIssue, JsonlProfile, JsonlWarning


def profile_file(
    path: str | Path, sample_limit: int = 3, high_cardinality_threshold: float = 0.8,
) -> JsonlProfile:
    return profile_lines(
        Path(path).read_text(encoding="utf-8").splitlines(),
        sample_limit,
        high_cardinality_threshold,
    )


def profile_lines(
    lines: list[str], sample_limit: int = 3, high_cardinality_threshold: float = 0.8,
) -> JsonlProfile:
    if not 0 < high_cardinality_threshold <= 1:
        raise ValueError("high_cardinality_threshold must be greater than 0 and at most 1")
    field_counter: Counter[str] = Counter()
    field_type_counters: dict[str, Counter[str]] = {}
    issues: list[JsonlIssue] = []
    samples: list[dict[str, Any]] = []
    valid_records = 0
    field_value_counters: dict[str, Counter[str]] = {}
    nested_field_counter: Counter[str] = Counter()
    record_lengths: list[int] = []

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
        record_lengths.append(len(line))
        field_counter.update(record.keys())
        for field, value in record.items():
            field_type_counters.setdefault(field, Counter()).update(
                [_json_type_name(value)]
            )
            scalar_value = _json_scalar_value(value)
            if scalar_value is not None:
                field_value_counters.setdefault(field, Counter()).update(
                    [scalar_value]
                )
            if isinstance(value, dict):
                nested_field_counter.update(
                    f"{field}.{nested_field}" for nested_field in value.keys()
                )
        if len(samples) < sample_limit:
            samples.append(record)

    field_counts = field_counter.most_common()
    field_type_counts = [
        (field, field_type_counters[field].most_common())
        for field, _count in field_counts
    ]
    field_value_counts = [
        (field, field_value_counters[field].most_common())
        for field, _count in field_counts
        if field in field_value_counters
    ]
    field_absence_counts = [
        (
            field,
            (
                valid_records - count,
                field_type_counters[field].get("null", 0),
            ),
        )
        for field, count in field_counts
    ]
    return JsonlProfile(
        total_lines=len(lines),
        valid_records=valid_records,
        invalid_lines=len(issues),
        field_counts=field_counts,
        field_type_counts=field_type_counts,
        field_value_counts=field_value_counts,
        field_absence_counts=field_absence_counts,
        nested_field_counts=nested_field_counter.most_common(),
        high_cardinality_fields=_high_cardinality_fields(
            field_value_counters, high_cardinality_threshold,
        ),
        record_length_summary=_record_length_summary(record_lengths),
        warnings=_mixed_type_warnings(field_type_counts),
        issues=issues,
        samples=samples,
    )


def _high_cardinality_fields(
    field_value_counters: dict[str, Counter[str]],
    threshold: float,
) -> list[tuple[str, int, int]]:
    high_cardinality_fields: list[tuple[str, int, int]] = []
    for field, value_counter in field_value_counters.items():
        scalar_records = value_counter.total()
        distinct_values = len(value_counter)
        if scalar_records >= 4 and distinct_values / scalar_records >= threshold:
            high_cardinality_fields.append((field, distinct_values, scalar_records))
    return sorted(
        high_cardinality_fields,
        key=lambda item: (-item[1], item[0]),
    )


def _record_length_summary(record_lengths: list[int]) -> dict[str, float] | None:
    if not record_lengths:
        return None
    return {
        "min": min(record_lengths),
        "max": max(record_lengths),
        "average": sum(record_lengths) / len(record_lengths),
    }


def _mixed_type_warnings(
    field_type_counts: list[tuple[str, list[tuple[str, int]]]]
) -> list[JsonlWarning]:
    warnings: list[JsonlWarning] = []
    for field, type_counts in field_type_counts:
        if len(type_counts) <= 1:
            continue
        type_summary = ", ".join(
            f"{type_name}={count}" for type_name, count in type_counts
        )
        warnings.append(
            JsonlWarning(
                field=field,
                message=f"mixed value types: {type_summary}",
            )
        )
    return warnings


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


def _json_scalar_value(value: Any) -> str | None:
    if isinstance(value, (dict, list)):
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)
