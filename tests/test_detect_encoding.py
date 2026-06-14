"""
Tests for the detect_encoding function (Rust and Python fallback paths).
"""

import pytest

from TextSpitter import _RUST_AVAILABLE, detect_encoding
from TextSpitter._fallback import detect_encoding as fallback_detect

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["rust", "fallback"])
def detect(request):
    if request.param == "rust":
        if not _RUST_AVAILABLE:
            pytest.skip("Rust extension not available")
        return detect_encoding
    return fallback_detect


# ---------------------------------------------------------------------------
# Core behaviour (both paths)
# ---------------------------------------------------------------------------

def test_utf8_text(detect):
    data = "Hello, world!".encode("utf-8")
    assert detect(data) == "utf-8"


def test_utf8_with_multibyte(detect):
    data = "café résumé naïve".encode("utf-8")
    assert detect(data) == "utf-8"


def test_empty_bytes_returns_utf8(detect):
    assert detect(b"") == "utf-8"


def test_pure_ascii_returns_utf8(detect):
    # ASCII is a valid subset of UTF-8; should be identified as utf-8.
    assert detect(b"Hello world 12345") == "utf-8"


def test_windows1252_smart_quotes(detect):
    # 0x93/0x94 are Windows-1252 curly quotes — invalid in UTF-8.
    data = b"He said \x93hello\x94 to her"
    result = detect(data)
    assert result in ("cp1252", "windows-1252", "latin-1"), f"unexpected: {result}"


def test_return_type_is_str(detect):
    assert isinstance(detect(b"test"), str)


def test_return_value_is_valid_python_codec(detect):
    encodings_to_probe = [
        "Hello UTF-8".encode("utf-8"),
        b"byte string \x80\x81",
    ]
    for data in encodings_to_probe:
        enc = detect(data)
        # The returned codec name must be usable with bytes.decode().
        try:
            data.decode(enc, errors="replace")
        except LookupError:
            pytest.fail(f"detect_encoding returned invalid codec name: {enc!r}")


# ---------------------------------------------------------------------------
# Rust-only: large buffer handled without panic
# ---------------------------------------------------------------------------

def test_large_buffer_does_not_panic():
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available")
    data = ("The quick brown fox jumps over the lazy dog. " * 10_000).encode("utf-8")
    result = detect_encoding(data)
    assert result == "utf-8"
