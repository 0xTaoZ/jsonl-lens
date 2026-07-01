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
    args = parser.parse_args()

    profile = profile_file(args.path)
    if args.json:
        print(json.dumps(profile.to_dict(), indent=2))
    else:
        print_report(profile)


def print_report(profile: JsonlProfile) -> None:
    print("jsonl-lens")
    print(f"Total lines: {profile.total_lines}")
    print(f"Valid records: {profile.valid_records}")
    print(f"Invalid lines: {profile.invalid_lines}")

    if profile.field_counts:
        print("\nFields")
        for field, count in profile.field_counts:
            print(f"- {field}: {count}")

    if profile.issues:
        print("\nIssues")
        for issue in profile.issues[:5]:
            print(f"- line {issue.line_number}: {issue.message}")

    if profile.samples:
        print("\nSamples")
        for sample in profile.samples:
            print(json.dumps(sample, sort_keys=True))
