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
        "--max-issues",
        type=int,
        default=5,
        help="Maximum number of issues to print in the text report",
    )
    args = parser.parse_args()
    if args.max_issues < 0:
        parser.error("--max-issues must be 0 or greater")

    profile = profile_file(args.path)
    if args.json:
        print(json.dumps(profile.to_dict(), indent=2))
    else:
        print_report(profile, max_issues=args.max_issues)


def print_report(profile: JsonlProfile, max_issues: int = 5) -> None:
    print("jsonl-lens")
    print(f"Total lines: {profile.total_lines}")
    print(f"Valid records: {profile.valid_records}")
    print(f"Invalid lines: {profile.invalid_lines}")

    if profile.field_counts:
        print("\nFields")
        for field, count in profile.field_counts:
            print(f"- {field}: {count}")

    if profile.field_type_counts:
        print("\nField types")
        for field, type_counts in profile.field_type_counts:
            summary = ", ".join(
                f"{type_name}={count}" for type_name, count in type_counts
            )
            print(f"- {field}: {summary}")

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
