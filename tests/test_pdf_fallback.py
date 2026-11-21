"""
Regression tests for the pypdf fallback path in ``FileExtractor.pdf_file_read``.

The primary extractor is PyMuPDF. When it is unavailable or raises, the code
falls back to ``pypdf.PdfReader``. These tests force that path by setting the
module-level ``core.pymupdf`` to ``None`` and pin the behaviour the code
defines: text is returned for a valid PDF, and any failure (encrypted, corrupt,
truncated) degrades to an empty string rather than raising.
"""

from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

from TextSpitter import core
from TextSpitter.core import FileExtractor

SAMPLE_TEXT = "Hello fallback world"


def _build_pdf(encrypt_with: str | None = None) -> bytes:
    """Build a one-page PDF containing SAMPLE_TEXT using only pypdf."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=200)
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): font}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 18 Tf 20 100 Td ({SAMPLE_TEXT}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(stream)
    if encrypt_with is not None:
        writer.encrypt(encrypt_with)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def force_pypdf(monkeypatch):
    """Make the PyMuPDF branch fail so the pypdf fallback is exercised."""
    monkeypatch.setattr(core, "pymupdf", None)
    assert core.pypdf is not None


def _extract(data: bytes) -> str:
    return FileExtractor(
        file_obj=BytesIO(data), filename="sample.pdf"
    ).pdf_file_read()


def test_fixture_pdf_is_valid():
    """Guard: the generated PDF really contains the sample text."""
    text = PdfReader(BytesIO(_build_pdf())).pages[0].extract_text()
    assert SAMPLE_TEXT in text


def test_fallback_valid_pdf_returns_text(force_pypdf):
    assert SAMPLE_TEXT in _extract(_build_pdf())


def test_fallback_encrypted_pdf_returns_empty_without_raising(force_pypdf):
    """An encrypted PDF cannot be read without a password: empty string."""
    data = _build_pdf(encrypt_with="s3cret")
    assert _extract(data) == ""


def test_fallback_corrupt_pdf_returns_empty_without_raising(force_pypdf):
    assert _extract(b"this is definitely not a pdf") == ""


def test_fallback_truncated_pdf_does_not_raise(force_pypdf):
    """A truncated PDF yields a str (possibly empty), never an exception."""
    data = _build_pdf()
    result = _extract(data[: len(data) // 2])
    assert isinstance(result, str)


def test_fallback_logs_when_both_extractors_fail(force_pypdf, log_capture):
    _extract(b"%PDF-1.4\ngarbage")
    assert any("failed" in m.lower() for m in log_capture)
