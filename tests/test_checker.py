from env_guard.checker import check, parse_env_example


def test_parse_env_example_basic(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("DATABASE_URL=postgres://localhost\nAPI_KEY=\n")

    declared = parse_env_example(str(env_file))

    assert declared == {"DATABASE_URL", "API_KEY"}


def test_parse_env_example_no_equals_sign(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("DATABASE_URL\nAPI_KEY=secret\n")

    declared = parse_env_example(str(env_file))

    assert declared == {"DATABASE_URL", "API_KEY"}


def test_parse_env_example_skips_comments_and_blank_lines(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text(
        "# This is a comment\n"
        "DATABASE_URL=postgres://localhost\n"
        "\n"
        "   \n"
        "# ANOTHER_COMMENT=value\n"
        "API_KEY=secret\n"
    )

    declared = parse_env_example(str(env_file))

    assert declared == {"DATABASE_URL", "API_KEY"}


def test_parse_env_example_missing_file(tmp_path):
    env_file = tmp_path / "does_not_exist.env"

    declared = parse_env_example(str(env_file))

    assert declared == set()


def test_check_finds_missing_variable():
    scanned = {
        "app.py": [("DATABASE_URL", 1), ("STRIPE_KEY", 2)],
    }
    declared = {"DATABASE_URL"}

    missing, unused = check(scanned, declared)

    assert missing == ["STRIPE_KEY"]
    assert unused == []


def test_check_finds_unused_variable():
    scanned = {
        "app.py": [("DATABASE_URL", 1)],
    }
    declared = {"DATABASE_URL", "OLD_API_KEY"}

    missing, unused = check(scanned, declared)

    assert missing == []
    assert unused == ["OLD_API_KEY"]


def test_check_with_no_issues():
    scanned = {
        "app.py": [("DATABASE_URL", 1)],
    }
    declared = {"DATABASE_URL"}

    missing, unused = check(scanned, declared)

    assert missing == []
    assert unused == []


def test_check_with_empty_inputs():
    missing, unused = check({}, set())

    assert missing == []
    assert unused == []


def test_check_deduplicates_repeated_variable_usage():
    scanned = {
        "app.py": [("DATABASE_URL", 1), ("DATABASE_URL", 5)],
        "db.py": [("DATABASE_URL", 12)],
    }
    declared = {"DATABASE_URL"}

    missing, unused = check(scanned, declared)

    assert missing == []
    assert unused == []