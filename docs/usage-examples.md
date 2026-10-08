# Usage examples

These examples use the bundled sample file, but the same commands work with small application logs, exported cloud events, and other JSON Lines files.

## Inspect a file

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl
```

Use this when you want a quick human-readable report with record counts, field frequency, value types, missing or null fields, one-level nested object paths, high-cardinality scalar fields, record lengths, parse issues, and a few sample records.

## Check a schema quickly

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only
```

This is useful before writing a parser or loading a file into another tool. The output stays focused on field names, how often they appear, the value types seen for each field, nested object paths, high-cardinality scalar fields, and fields that are missing or null in some records.

## Focus on selected fields

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --include-field service
```

Use repeated `--include-field` options when you only care about a few fields from a larger log export. Add `--exclude-field <name>` to hide noisy fields such as timestamps or request IDs from the field summary.

## Check common values

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --include-field service
```

This shows the most common scalar values for selected fields. It is useful for quick checks such as which log levels appear, which service produced most records, or whether a status field contains unexpected values.

Strings that are themselves valid JSON are shown quoted, so a producer that writes `"status": "200"` in some records and `"status": 200` in others shows two values, `"200"` and `200`, instead of one merged count.

Use `--max-values <count>` to keep high-cardinality fields readable:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --max-values 2
```

Fields with at least four scalar values and mostly distinct values are also listed under `High-cardinality fields`. Use that section to notice IDs or trace fields that may be noisy grouping keys.

Hide those noisy fields from `Common values` while keeping them listed as high-cardinality:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --hide-high-cardinality-values
```

Use `--high-cardinality-threshold 0.75` to flag fields with at least 75% distinct scalar values. The default is `0.8`; the minimum sample remains four scalar values. Ratios must be greater than zero and at most one.

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/cardinality.jsonl --json --fields-only --high-cardinality-threshold 0.75 --hide-high-cardinality-values
```

In this sample, `request_id` has three distinct values across four records. It is flagged at `0.75`, but not at the default `0.8`. The `level` field stays visible in common values. Full JSON reports retain raw common-value counts; `--hide-high-cardinality-values` filters text and fields-only JSON summaries.

## Find sparse fields

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field request_id
```

The `Field gaps` section shows how many valid records did not include the field and how many set it to `null`. This is useful when checking whether log enrichment or event collection is consistent.

## Check nested object paths

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field http.method
```

The `Nested fields` section shows one-level object paths such as `http.method` and `http.status`. This is useful when exported logs put request, identity, or cloud event details inside nested objects.

## Check record size drift

The `Record lengths` section shows the shortest, longest, and average source-line length for valid JSON object records. This is a quick way to spot unusually large log events before writing a parser or loading the file into another tool.

## Keep noisy files readable

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-issues 2
```

Large log exports can contain many malformed lines. Limiting the issue list keeps the report short while still showing examples of the problem.

Sample records can also be limited or hidden when you only need the counts:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-samples 1
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-samples 0
```

## Produce JSON for scripts

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --json
```

The JSON output is meant for simple shell scripts, notebooks, or later tooling that needs to make decisions from the profile.
