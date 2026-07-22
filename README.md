# jsonl-lens

A small Python CLI for inspecting JSON Lines files.

It counts valid and invalid lines, summarizes which fields appear, shows common scalar values, and prints a few sample records. It is meant for quick checks on application logs, exported events, and small data files.

## Quick start

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

More examples are in [docs/usage-examples.md](docs/usage-examples.md).

## Example output

```text
jsonl-lens
Total lines: 5
Valid records: 3
Invalid lines: 2

Fields
- timestamp: 3
- level: 3
- service: 3
- message: 3
- request_id: 2
- duration_ms: 1
- job_id: 1

Field types
- timestamp: string=3
- level: string=3
- service: string=3
- message: string=3
- request_id: string=2
- duration_ms: number=1
- job_id: string=1

Common values
- timestamp: 2026-07-01T08:00:00Z=1, 2026-07-01T08:00:02Z=1, 2026-07-01T08:00:05Z=1
- level: info=1, warn=1, error=1
- service: api=2, worker=1
- message: request handled=1, slow request=1, job failed=1
- request_id: req-001=1, req-002=1
- duration_ms: 1430=1
- job_id: job-77=1

Issues
- line 4: invalid JSON: Expecting property name enclosed in double quotes
- line 5: record is not a JSON object
```

JSON output is available for scripts:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --json
```

Large files can produce a noisy issue list. Limit the text report when you only need the first few examples:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-issues 2
```

For a quick schema check, print only field counts and value types:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only
```

Focus field summaries on a few fields:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --include-field service
```

Limit common-value output when a field has many distinct values:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --fields-only --include-field level --max-values 2
```

## Why this exists

JSONL is easy to produce, but messy files are common. A small inspection tool is useful before writing a parser, importing data, or sharing a sample bug report.

## Next ideas

- add nested object field summaries
