from env_guard.scanner import extract_env_vars, find_py_files, scan_directory


def test_extract_env_vars_detects_getenv(tmp_path):
    file = tmp_path / "app.py"
    file.write_text('import os\nvalue = os.getenv("DATABASE_URL")\n')

    results = extract_env_vars(file)

    assert ("DATABASE_URL", 2) in results


def test_extract_env_vars_detects_environ_bracket(tmp_path):
    file = tmp_path / "app.py"
    file.write_text('import os\nvalue = os.environ["API_KEY"]\n')

    results = extract_env_vars(file)

    assert ("API_KEY", 2) in results


def test_extract_env_vars_detects_environ_get(tmp_path):
    file = tmp_path / "app.py"
    file.write_text('import os\nvalue = os.environ.get("SECRET_TOKEN")\n')

    results = extract_env_vars(file)

    assert ("SECRET_TOKEN", 2) in results


def test_extract_env_vars_detects_dotenv_bracket_access(tmp_path):
    file = tmp_path / "app.py"
    file.write_text(
        "from dotenv import dotenv_values\n"
        "config = dotenv_values('.env')\n"
        'value = config["DATABASE_URL"]\n'
    )

    results = extract_env_vars(file)

    assert ("DATABASE_URL", 3) in results


def test_extract_env_vars_detects_dotenv_get_access(tmp_path):
    file = tmp_path / "app.py"
    file.write_text(
        "from dotenv import dotenv_values\n"
        "config = dotenv_values('.env')\n"
        'value = config.get("API_KEY")\n'
    )

    results = extract_env_vars(file)

    assert ("API_KEY", 3) in results


def test_extract_env_vars_no_dotenv_assignment_means_no_dotenv_patterns(tmp_path):
    file = tmp_path / "app.py"
    file.write_text('value = config["DATABASE_URL"]\n')

    results = extract_env_vars(file)

    assert results == []


def test_extract_env_vars_returns_empty_for_no_matches(tmp_path):
    file = tmp_path / "app.py"
    file.write_text("def add(a, b):\n    return a + b\n")

    results = extract_env_vars(file)

    assert results == []


def test_extract_env_vars_handles_unreadable_file(tmp_path):
    file = tmp_path / "binary.py"
    file.write_bytes(b"\xff\xfe\x00\x01")

    results = extract_env_vars(file)

    assert results == []


def test_find_py_files_excludes_default_dirs(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")

    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "ignored.py").write_text("y = 2\n")

    files = find_py_files(str(tmp_path))

    names = {f.name for f in files}
    assert "app.py" in names
    assert "ignored.py" not in names


def test_find_py_files_respects_user_ignore(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("y = 2\n")

    files = find_py_files(str(tmp_path), ignore=["tests"])

    names = {f.name for f in files}
    assert "app.py" in names
    assert "test_app.py" not in names


def test_find_py_files_ignore_by_filename(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / "legacy.py").write_text("y = 2\n")

    files = find_py_files(str(tmp_path), ignore=["legacy.py"])

    names = {f.name for f in files}
    assert "app.py" in names
    assert "legacy.py" not in names


def test_scan_directory_aggregates_multiple_files(tmp_path):
    (tmp_path / "db.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')
    (tmp_path / "payments.py").write_text('import os\nkey = os.environ["STRIPE_KEY"]\n')
    (tmp_path / "utils.py").write_text("def helper():\n    return 42\n")

    results = scan_directory(str(tmp_path))

    assert len(results) == 2

    all_vars = {var for vars_found in results.values() for var, _ in vars_found}
    assert all_vars == {"DATABASE_URL", "STRIPE_KEY"}


def test_scan_directory_returns_empty_dict_for_no_matches(tmp_path):
    (tmp_path / "utils.py").write_text("def helper():\n    return 42\n")

    results = scan_directory(str(tmp_path))

    assert results == {}


def test_scan_directory_with_ignore(tmp_path):
    (tmp_path / "app.py").write_text('import os\nurl = os.getenv("DATABASE_URL")\n')

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text('import os\nkey = os.getenv("TEST_ONLY_VAR")\n')

    results = scan_directory(str(tmp_path), ignore=["tests"])

    all_vars = {var for vars_found in results.values() for var, _ in vars_found}
    assert all_vars == {"DATABASE_URL"}
    assert "TEST_ONLY_VAR" not in all_vars