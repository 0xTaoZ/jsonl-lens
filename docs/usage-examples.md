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
