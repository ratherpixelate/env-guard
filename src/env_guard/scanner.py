import re
from pathlib import Path

# Matches: os.getenv("VAR"), os.environ["VAR"], os.environ.get("VAR")
ENV_PATTERNS = [
    r'os\.getenv\(\s*["\']([^"\']+)["\']\s*[\,\)]',
    r'os\.environ\[\s*["\']([^"\']+)["\']\s*\]',
    r'os\.environ\.get\(\s*["\']([^"\']+)["\']\s*[\,\)]',
]

COMPILED = [re.compile(p) for p in ENV_PATTERNS]

EXCLUDE_DIRS = {".venv", "__pycache__", ".git", "node_modules", ".tox", ".mypy_cache"}

def find_py_files(directory: str, ignore: list[str] | None = None) -> list[Path]:
    """Recursively find all .py files, excluding common non-project directories."""
    root = Path(directory)
    ignore_parts = set(ignore) if ignore else set()
    results = []

    for file in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in file.parts):
            continue
        if any(part in ignore_parts for part in file.parts):
            continue
        results.append(file)

    return results


def extract_env_vars(file_path: Path) -> list[tuple[str, int]]:
    """
    Scan a single .py file and return a list of (VAR_NAME, line_number) tuples
    for every environment variable access found.
    """
    results = []
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return results

    for line_num, line in enumerate(lines, start=1):
        for pattern in COMPILED:
            for match in pattern.finditer(line):
                results.append((match.group(1), line_num))

    return results


def scan_directory(directory: str, ignore: list[str] | None = None) -> dict[str, list[tuple[str, int]]]:
    """
    Scan all .py files in a directory.
    Returns a dict mapping file path (str) -> list of (VAR_NAME, line_number).
    """
    py_files = find_py_files(directory, ignore=ignore)
    results = {}

    for file in py_files:
        found = extract_env_vars(file)
        if found:
            results[str(file)] = found

    return results