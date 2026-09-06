# jsonl-lens

A small Python CLI for inspecting JSON Lines files.

It counts valid and invalid lines, summarizes which fields appear, shows common scalar values, reports missing or null fields, reports one-level nested object paths, shows a compact record-length summary, and prints a few sample records. It is meant for quick checks on application logs, exported events, and small data files.

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
- http: 2
- duration_ms: 1
- job_id: 1
- job: 1

Field types
- timestamp: string=3
- level: string=3
- service: string=3
- message: string=3
- request_id: string=2
- http: object=2
- duration_ms: number=1
- job_id: string=1
- job: object=1

Common values
- timestamp: 2026-07-01T08:00:00Z=1, 2026-07-01T08:00:02Z=1, 2026-07-01T08:00:05Z=1
- level: info=1, warn=1, error=1
- service: api=2, worker=1
- message: request handled=1, slow request=1, job failed=1
- request_id: req-001=1, req-002=1
- duration_ms: 1430=1
- job_id: job-77=1

Field gaps
- request_id: missing=1, null=0
- http: missing=1, null=0
- duration_ms: missing=2, null=0
- job_id: missing=2, null=0
- job: missing=2, null=0

Nested fields
- http.method: 2
- http.status: 2
- job.attempt: 1

Record lengths
- min=132, max=171, average=152.7 characters

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

Limit or hide sample records when the field summary is enough:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-samples 1
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --max-samples 0
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

JSONL is easy to produce, but messy files are common. A small inspection tool is useful before writing a parser, importing data, or sharing a sample bug report. Missing-field counts, one-level nested paths, and record lengths also help spot optional fields, schema drift, enrichment steps that only ran for some records, and unusually large log events.

## Next ideas

- add a compact summary for high-cardinality fields
