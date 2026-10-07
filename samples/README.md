# Samples

The sample file contains three valid JSON object records and two intentionally bad lines. Some fields only appear on selected records so the CLI can show missing-field summaries, and a few object-valued fields show one-level nested path summaries.

Use `--max-samples 1` or `--max-samples 0` with this file to check how the report limits sample records while keeping field, record-length, and issue summaries.

It is fake data for testing the CLI output.

`cardinality.jsonl` contains four valid records with three distinct request IDs. Compare the default threshold with `--high-cardinality-threshold 0.75` to review the boundary and common-value hiding.
