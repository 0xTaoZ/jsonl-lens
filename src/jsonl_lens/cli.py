import argparse
import json

from .models import JsonlProfile
from .profiler import profile_file


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="jsonl-lens",
        description="Inspect a JSON Lines file.",
    )
    parser.add_argument("path", help="Path to a .jsonl file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the profile as JSON for scripts",
    )
    parser.add_argument(
        "--fields-only",
        action="store_true",
        help="Print only field names, counts, and value types",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=5,
        help="Maximum number of issues to print in the text report",
    )
    parser.add_argument(
        "--max-values",
        type=int,
        default=5,
        help="Maximum number of common values to print per field",
    )
    parser.add_argument(
        "--include-field",
        action="append",
        default=[],
        help="Only show this field in field summaries; can be repeated",
    )
    parser.add_argument(
        "--exclude-field",
        action="append",
        default=[],
        help="Hide this field from field summaries; can be repeated",
    )
    args = parser.parse_args()
    if args.max_issues < 0:
        parser.error("--max-issues must be 0 or greater")
    if args.max_values < 0:
        parser.error("--max-values must be 0 or greater")

    profile = profile_file(args.path)
    if args.json and args.fields_only:
        print(
            json.dumps(
                field_summary_to_dict(
                    profile,
                    include_fields=args.include_field,
                    exclude_fields=args.exclude_field,
                    max_values=args.max_values,
                ),
                indent=2,
            )
        )
    elif args.json:
        print(json.dumps(profile.to_dict(), indent=2))
    elif args.fields_only:
        print_field_report(
            profile,
            include_fields=args.include_field,
            exclude_fields=args.exclude_field,
            max_values=args.max_values,
        )
    else:
        print_report(
            profile,
            max_issues=args.max_issues,
            max_values=args.max_values,
            include_fields=args.include_field,
            exclude_fields=args.exclude_field,
        )


def field_summary_to_dict(
    profile: JsonlProfile,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
    max_values: int = 5,
) -> dict[str, object]:
    field_counts = _filter_field_counts(
        profile.field_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )
    field_type_counts = _filter_field_type_counts(
        profile.field_type_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )
    field_value_counts = _filter_field_value_counts(
        profile.field_value_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
        max_values=max_values,
    )
    return {
        "field_counts": [
            {"field": field, "count": count}
            for field, count in field_counts
        ],
        "field_type_counts": [
            {
                "field": field,
                "types": [
                    {"type": type_name, "count": count}
                    for type_name, count in type_counts
                ],
            }
            for field, type_counts in field_type_counts
        ],
        "field_value_counts": [
            {
                "field": field,
                "values": [
                    {"value": value, "count": count}
                    for value, count in value_counts
                ],
            }
            for field, value_counts, _hidden_count in field_value_counts
        ],
    }


def print_field_report(
    profile: JsonlProfile,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
    max_values: int = 5,
) -> None:
    field_counts = _filter_field_counts(
        profile.field_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )
    field_type_counts = _filter_field_type_counts(
        profile.field_type_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
    )
    field_value_counts = _filter_field_value_counts(
        profile.field_value_counts,
        include_fields=include_fields,
        exclude_fields=exclude_fields,
        max_values=max_values,
    )

    if field_counts:
        print("Fields")
        for field, count in field_counts:
            print(f"- {field}: {count}")

    if field_type_counts:
        print("\nField types")
        for field, type_counts in field_type_counts:
            summary = ", ".join(
                f"{type_name}={count}" for type_name, count in type_counts
            )
            print(f"- {field}: {summary}")

    if field_value_counts:
        print("\nCommon values")
        for field, value_counts, hidden_count in field_value_counts:
            summary = ", ".join(
                f"{value}={count}" for value, count in value_counts
            )
            print(f"- {field}: {summary}")
            if hidden_count > 0:
                print(f"- ... {hidden_count} more value(s) for {field}")


def print_report(
    profile: JsonlProfile,
    max_issues: int = 5,
    max_values: int = 5,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> None:
    print("jsonl-lens")
    print(f"Total lines: {profile.total_lines}")
    print(f"Valid records: {profile.valid_records}")
    print(f"Invalid lines: {profile.invalid_lines}")

    if profile.field_counts or profile.field_type_counts:
        print()
        print_field_report(
            profile,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            max_values=max_values,
        )

    if profile.warnings:
        print("\nWarnings")
        for warning in profile.warnings:
            print(f"- {warning.field}: {warning.message}")

    if profile.issues:
        print("\nIssues")
        visible_issues = profile.issues[:max_issues]
        for issue in visible_issues:
            print(f"- line {issue.line_number}: {issue.message}")
        hidden_count = len(profile.issues) - len(visible_issues)
        if hidden_count > 0:
            print(f"- ... {hidden_count} more issue(s)")

    if profile.samples:
        print("\nSamples")
        for sample in profile.samples:
            print(json.dumps(sample, sort_keys=True))


def _filter_field_counts(
    field_counts: list[tuple[str, int]],
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> list[tuple[str, int]]:
    return [
        (field, count)
        for field, count in field_counts
        if _field_is_visible(field, include_fields, exclude_fields)
    ]


def _filter_field_type_counts(
    field_type_counts: list[tuple[str, list[tuple[str, int]]]],
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> list[tuple[str, list[tuple[str, int]]]]:
    return [
        (field, type_counts)
        for field, type_counts in field_type_counts
        if _field_is_visible(field, include_fields, exclude_fields)
    ]


def _filter_field_value_counts(
    field_value_counts: list[tuple[str, list[tuple[str, int]]]],
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
    max_values: int = 5,
) -> list[tuple[str, list[tuple[str, int]], int]]:
    return [
        (field, value_counts[:max_values], max(len(value_counts) - max_values, 0))
        for field, value_counts in field_value_counts
        if _field_is_visible(field, include_fields, exclude_fields)
    ]


def _field_is_visible(
    field: str,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> bool:
    include_set = set(include_fields or [])
    exclude_set = set(exclude_fields or [])
    if include_set and field not in include_set:
        return False
    return field not in exclude_set
