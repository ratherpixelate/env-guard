from typer.testing import CliRunner

from env_guard.main import app

runner = CliRunner()


def test_scan_exits_zero_when_everything_matches(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n")

    result = runner.invoke(app, ["scan", str(tmp_path)])

    assert result.exit_code == 0


def test_scan_exits_one_when_variable_missing(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("UNRELATED_VAR=\n")

    result = runner.invoke(
        app, ["scan", str(tmp_path), "--env-file", str(tmp_path / ".env.example")]
    )

    assert result.exit_code == 1
    assert "DATABASE_URL" in result.stdout


def test_scan_reports_unused_variable(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("DATABASE_URL=\nOLD_API_KEY=\n")

    result = runner.invoke(
        app, ["scan", str(tmp_path), "--env-file", str(tmp_path / ".env.example")]
    )

    assert "OLD_API_KEY" in result.stdout


def test_scan_with_no_env_usage(tmp_path):
    (tmp_path / "app.py").write_text("def add(a, b):\n    return a + b\n")

    result = runner.invoke(app, ["scan", str(tmp_path)])

    assert result.exit_code == 0
    assert "No environment variable usage found" in result.stdout


def test_scan_with_ignore_excludes_directory(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text('import os\nkey = os.getenv("TEST_ONLY_VAR")\n')

    result = runner.invoke(app, ["scan", str(tmp_path), "--ignore", "tests"])

    assert result.exit_code == 0
    assert "TEST_ONLY_VAR" not in result.stdout


def test_scan_with_no_table_skips_table_output(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("DATABASE_URL=\n")

    result = runner.invoke(app, ["scan", str(tmp_path), "--no-table"])

    assert result.exit_code == 0
    assert "Detected Environment Variables" not in result.stdout


def test_scan_with_missing_env_example_skips_cross_reference(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')

    result = runner.invoke(
        app, ["scan", str(tmp_path), "--env-file", str(tmp_path / "nonexistent.env")]
    )

    assert result.exit_code == 0
    assert "skipping cross-reference" in result.stdout


def test_scan_with_empty_env_example_also_skips_cross_reference(tmp_path):
    """
    Known limitation: an existing-but-empty .env.example is treated the
    same as a missing one, because parse_env_example returns an empty
    set in both cases and `if not declared` can't tell them apart.
    This means env-guard won't flag DATABASE_URL as missing here, even
    though .env.example exists.
    """
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / ".env.example").write_text("")

    result = runner.invoke(
        app, ["scan", str(tmp_path), "--env-file", str(tmp_path / ".env.example")]
    )

    assert result.exit_code == 0
    assert "skipping cross-reference" in result.stdout