# jsonl-lens

A small Python CLI for inspecting JSON Lines files.

It counts valid and invalid lines, summarizes which fields appear, and shows a few sample records. It is meant for quick checks on application logs, exported events, and small data files.

## Quick start

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

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

Issues
- line 4: invalid JSON: Expecting property name enclosed in double quotes
- line 5: record is not a JSON object
```

JSON output is available for scripts:

```bash
PYTHONPATH=src python3 -m jsonl_lens samples/events.jsonl --json
```

## Why this exists

JSONL is easy to produce, but messy files are common. A small inspection tool is useful before writing a parser, importing data, or sharing a sample bug report.

## Next ideas

- add `--fields-only` for quick schema checks
- add `--max-issues` to control noisy files
- add simple warnings for mixed field types
