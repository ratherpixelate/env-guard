# env-guard

A command-line tool for Python projects that detects missing or undocumented environment variables by statically scanning source files and cross-referencing them against a `.env.example`.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

Environment variable mismatches are a common source of production failures. `env-guard` addresses this by scanning your codebase for every `os.getenv`, `os.environ.get`, and `os.environ[]` call, then comparing the results against your `.env.example` to surface any discrepancies before deployment.

---

## Features

- Static scanning of `.py` files for environment variable usage
- Cross-reference against `.env.example` to detect missing and unused variables
- Rich, color-coded terminal output with an optional plain-text mode for CI
- `--ignore` flag to exclude specific files or directories from scanning
- Exits with code `1` on any issues, making it suitable for use in CI pipelines

---

## Installation

> This package is not yet published to PyPI. Install from source:

```bash
git clone https://github.com/ratherpixelate/env-guard.git
cd env-guard
uv sync
```

---

## Usage

Run from the root of your Python project:

```bash
env-guard scan
```

### Options

```
env-guard scan [OPTIONS] [PATH]

Arguments:
  PATH                   Directory to scan [default: .]

Options:
  -e, --env-file TEXT    Path to .env.example [default: .env.example]
  -i, --ignore TEXT      Name to ignore during scanning (repeatable)
      --no-table         Output plain text instead of a formatted table
      --help             Show this message and exit.
```

### Example Output

```
env-guard scanning: .

Ignoring: tests, scripts

                Detected Environment Variables
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━┓
┃ File               ┃ Variable      ┃ Line ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━┩
│ app/db.py          │ DATABASE_URL  │   12 │
│ app/payments.py    │ STRIPE_KEY    │    8 │
└────────────────────┴───────────────┴──────┘

Missing from .env.example:
  ✗ STRIPE_KEY

No unused variables.

Scan complete — 1 missing, 0 unused.
```

---

## Ignoring Files and Directories

Use `--ignore` or `-i` to exclude paths from scanning. The value is matched against each segment of every file path, so it applies at any depth.

```bash
env-guard scan --ignore tests --ignore migrations
env-guard scan -i tests -i scripts/seed.py
```

---

## CI Integration

```yaml
- name: Check environment variables
  run: env-guard scan --no-table
```

The process exits with code `1` if any variables are missing from `.env.example`, which will fail the workflow step.

---

## Project Structure

```
env-guard/
├── src/
│   └── env_guard/
│       ├── __init__.py
│       ├── main.py        # CLI entrypoint (Typer)
│       ├── scanner.py     # Regex-based source file scanner
│       └── checker.py     # .env.example cross-reference logic
├── tests/
├── pyproject.toml
└── README.md
```

---

## Roadmap

- [x] Static scanning for `os.getenv` and `os.environ` usages
- [x] Cross-reference against `.env.example`
- [x] Rich table output with `--no-table` flag
- [x] CI-friendly exit codes
- [x] `--ignore` flag for excluding files and directories
- [ ] `python-dotenv` `load_dotenv()` support
- [ ] pytest test suite
- [ ] PyPI release
- [ ] GitHub Actions CI

---

## Tech Stack

- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Rich](https://github.com/Textualize/rich) — terminal formatting
- [uv](https://github.com/astral-sh/uv) — packaging and dependency management

---

## License

MIT © [ratherpixelate](https://github.com/ratherpixelate)