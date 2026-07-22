# Usage examples

These examples use the bundled sample file, but the same commands work with small application logs, exported cloud events, and other JSON Lines files.

## Inspect a file

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl
```

Use this when you want a quick human-readable report with record counts, field frequency, value types, parse issues, and a few sample records.

## Check a schema quickly

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only
```

This is useful before writing a parser or loading a file into another tool. The output stays focused on field names, how often they appear, and the value types seen for each field.

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

Use `--max-values <count>` to keep high-cardinality fields readable:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --max-values 2
```

## Keep noisy files readable

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-issues 2
```

Large log exports can contain many malformed lines. Limiting the issue list keeps the report short while still showing examples of the problem.

## Produce JSON for scripts

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --json
```

The JSON output is meant for simple shell scripts, notebooks, or later tooling that needs to make decisions from the profile.
