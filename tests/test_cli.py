"""
Tests for the textspitter CLI entry point (TextSpitter.cli:main).
"""

import sys

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_cli(args: list[str], monkeypatch):
    """Call cli.main() with the given argv list; return (stdout, stderr, exit_code)."""
    from io import StringIO

    from TextSpitter.cli import main

    captured_out = StringIO()
    captured_err = StringIO()
    exit_code = 0

    monkeypatch.setattr(sys, "argv", ["textspitter"] + args)

    import builtins

    real_print = builtins.print

    def fake_print(*args, file=None, **kwargs):
        if file is sys.stderr:
            real_print(*args, file=captured_err, **kwargs)
        else:
            real_print(*args, file=captured_out, **kwargs)

    monkeypatch.setattr(builtins, "print", fake_print)

    try:
        main()
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    return captured_out.getvalue(), captured_err.getvalue(), exit_code


# ---------------------------------------------------------------------------
# Basic extraction tests
# ---------------------------------------------------------------------------


def test_cli_txt_stdout(tmp_path, monkeypatch):
    """Extracting a .txt file should print its contents to stdout."""
    txt = tmp_path / "hello.txt"
    txt.write_text("Hello CLI world", encoding="utf-8")

    stdout, stderr, code = run_cli([str(txt)], monkeypatch)

    assert "Hello CLI world" in stdout
    assert code == 0


def test_cli_multiple_files(tmp_path, monkeypatch):
    """Multiple files should be concatenated in stdout."""
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("File A content", encoding="utf-8")
    b.write_text("File B content", encoding="utf-8")

    stdout, _, code = run_cli([str(a), str(b)], monkeypatch)

    assert "File A content" in stdout
    assert "File B content" in stdout
    assert code == 0


def test_cli_output_flag(tmp_path, monkeypatch):
    """The -o flag should write output to a file instead of stdout."""
    src = tmp_path / "source.txt"
    out = tmp_path / "output.txt"
    src.write_text("Written to file", encoding="utf-8")

    stdout, _, code = run_cli([str(src), "-o", str(out)], monkeypatch)

    assert out.exists()
    assert "Written to file" in out.read_text(encoding="utf-8")
    assert stdout.strip() == ""
    assert code == 0


def test_cli_csv_file(tmp_path, monkeypatch):
    """CSV files should be extracted as raw text."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\nBob,25", encoding="utf-8")

    stdout, _, code = run_cli([str(csv_file)], monkeypatch)

    assert "Alice" in stdout
    assert code == 0


def test_cli_source_code_file(tmp_path, monkeypatch):
    """Python source files should be extracted."""
    py_file = tmp_path / "script.py"
    py_file.write_text("print('hello')\n", encoding="utf-8")

    stdout, _, code = run_cli([str(py_file)], monkeypatch)

    assert "print" in stdout
    assert code == 0


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_cli_missing_file(tmp_path, monkeypatch):
    """A missing file should produce an error message on stderr and exit 1."""
    missing = tmp_path / "nonexistent.txt"

    _, stderr, code = run_cli([str(missing)], monkeypatch)

    assert code == 1
    assert "Error" in stderr or "error" in stderr or str(missing) in stderr


def test_cli_no_args(monkeypatch):
    """Calling with no arguments should exit with a non-zero code (argparse error)."""
    monkeypatch.setattr(sys, "argv", ["textspitter"])

    from TextSpitter.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code != 0


# ---------------------------------------------------------------------------
# Output file tests
# ---------------------------------------------------------------------------


def test_cli_output_creates_file(tmp_path, monkeypatch):
    """Output file is created even if it didn't exist before."""
    src = tmp_path / "in.txt"
    out = tmp_path / "subdir" / "out.txt"
    src.write_text("data", encoding="utf-8")
    out.parent.mkdir(parents=True)

    _, _, code = run_cli([str(src), "-o", str(out)], monkeypatch)

    assert out.exists()
    assert code == 0


def test_cli_output_overwrites_existing(tmp_path, monkeypatch):
    """An existing output file should be overwritten."""
    src = tmp_path / "new.txt"
    out = tmp_path / "out.txt"
    src.write_text("new content", encoding="utf-8")
    out.write_text("old content", encoding="utf-8")

    _, _, code = run_cli([str(src), "-o", str(out)], monkeypatch)

    assert "new content" in out.read_text(encoding="utf-8")
    assert code == 0


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------


def test_cli_latin1_file(tmp_path, monkeypatch):
    """Files encoded in latin-1 should be extracted without errors."""
    latin = tmp_path / "latin.txt"
    latin.write_bytes("caf\xe9 r\xe9sum\xe9".encode("latin-1"))

    stdout, _, code = run_cli([str(latin)], monkeypatch)

    assert code == 0
    assert len(stdout) > 0
