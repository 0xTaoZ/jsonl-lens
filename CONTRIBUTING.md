# Contributing

Small, boring improvements are welcome here.

Good first changes:

- add a CLI flag with a focused test
- improve issue messages for common JSON mistakes
- add sample files that show a realistic log shape
- keep the tool dependency-free unless a library clearly earns its place

Before committing, run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
