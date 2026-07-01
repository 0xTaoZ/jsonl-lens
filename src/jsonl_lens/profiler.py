import json
from collections import Counter
from pathlib import Path
from typing import Any

from .models import JsonlIssue, JsonlProfile


def profile_file(path: str | Path, sample_limit: int = 3) -> JsonlProfile:
    return profile_lines(Path(path).read_text(encoding="utf-8").splitlines(), sample_limit)


def profile_lines(lines: list[str], sample_limit: int = 3) -> JsonlProfile:
    field_counter: Counter[str] = Counter()
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
        if len(samples) < sample_limit:
            samples.append(record)

    return JsonlProfile(
        total_lines=len(lines),
        valid_records=valid_records,
        invalid_lines=len(issues),
        field_counts=field_counter.most_common(),
        issues=issues,
        samples=samples,
    )
