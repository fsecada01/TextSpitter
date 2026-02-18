"""
Tests for the FileExtractor class.
"""

from io import BytesIO, IOBase
from pathlib import Path
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from TextSpitter.core import FileExtractor


# --- Fixtures ---
@pytest.fixture
def temp_dir():
    """Provides a temporary directory for tests."""
    with TemporaryDirectory() as tmpdir:
        yield tmpdir


# --- __init__ tests ---
def test_init_with_filename_str():
    extractor = FileExtractor(filename="test.txt")
    assert extractor.file_name == "test.txt"
    assert extractor.file_ext == "txt"
    assert isinstance(extractor.file, Path)
    assert str(extractor.file) == "test.txt"


def test_init_with_path_object():
    p = Path("mydir/test.docx")
    extractor = FileExtractor(file_obj=p)
    assert extractor.file_name == "test.docx"
    assert extractor.file_ext == "docx"
    assert extractor.file == p


def test_init_with_bytesio_and_filename():
    data = b"some data"
    file_obj = BytesIO(data)
    extractor = FileExtractor(file_obj=file_obj, filename="stream.bin")
    assert extractor.file_name == "stream.bin"
    assert extractor.file_ext == "bin"
    assert extractor.file == file_obj


def test_init_with_bytes_and_filename():
    data = b"byte content"
    extractor = FileExtractor(file_obj=data, filename="memory.dat")
    assert extractor.file_name == "memory.dat"
    assert extractor.file_ext == "dat"
    assert extractor.file == data


def test_init_with_spooled_temp_file_and_filename():
    with SpooledTemporaryFile() as stf:
        stf.write(b"spooled data")
        stf.seek(0)
        extractor = FileExtractor(file_obj=stf, filename="spooled.tmp")
        assert extractor.file_name == "spooled.tmp"
        assert extractor.file_ext == "tmp"
        assert extractor.file == stf


def test_init_with_file_like_object_with_name_attr():
    mock_file = MagicMock(spec=IOBase)
    mock_file.name = "from_attr.log"
    extractor = FileExtractor(file_obj=mock_file)
    assert extractor.file_name == "from_attr.log"
    assert extractor.file_ext == "log"
    assert extractor.file == mock_file


def test_init_with_file_like_object_with_custom_file_attr():
    mock_file = MagicMock()
    mock_file.custom_path = "custom.attr.file.ext"
    extractor = FileExtractor(file_obj=mock_file, file_attr="custom_path")
    assert extractor.file_name == "custom.attr.file.ext"
    assert extractor.file_ext == "ext"
    assert extractor.file == mock_file


def test_init_with_file_like_object_non_string_file_attr_uses_filename():
    mock_file = MagicMock(spec=IOBase)
    mock_file.name = 123  # Non-string name attribute
    extractor = FileExtractor(file_obj=mock_file, filename="fallback.txt")
    assert extractor.file_name == "fallback.txt"
    assert extractor.file_ext == "txt"
    assert extractor.file == mock_file


def test_init_filename_case_extension():
    extractor = FileExtractor(filename="TEST.TXT")
    assert extractor.file_ext == "txt"


def test_init_path_case_extension():
    extractor = FileExtractor(file_obj=Path("TEST.DOCX"))
    assert extractor.file_ext == "docx"


def test_init_no_extension_filename():
    extractor = FileExtractor(filename="noextension")
    assert extractor.file_name == "noextension"
    assert extractor.file_ext == "noextension"


def test_init_no_extension_path():
    extractor = FileExtractor(file_obj=Path("noextension"))
    assert extractor.file_name == "noextension"
    assert extractor.file_ext == ""


def test_init_raises_error_for_stream_without_filename():
    with pytest.raises(
        Exception, match="A 'filename' with an extension is required"
    ):
        FileExtractor(file_obj=BytesIO(b"content"))


def test_init_raises_error_for_bytes_without_filename():
    with pytest.raises(
        Exception, match="A 'filename' with an extension is required"
    ):
        FileExtractor(file_obj=b"content")


def test_init_raises_error_for_object_without_usable_name_attr_and_no_filename():
    mock_file = MagicMock(spec=IOBase)
    mock_file.name = 123
    with pytest.raises(
        Exception, match="does not contain a usable 'name' attribute"
    ):
        FileExtractor(file_obj=mock_file)


def test_init_raises_value_error_if_no_args():
    with pytest.raises(
        ValueError, match="Either 'file_obj' or 'filename' must be provided."
    ):
        FileExtractor()


# --- get_file_type tests ---
def test_get_file_type_known_mime_docx(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        None,
    )
    file_type = FileExtractor.get_file_type("test.docx")
    assert (
        file_type
        == "vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    mock_guess_type.assert_called_with("test.docx")


def test_get_file_type_known_mime_pdf(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = ("application/pdf", None)
    file_type = FileExtractor.get_file_type(Path("mydoc.pdf"))
    assert file_type == "pdf"
    mock_guess_type.assert_called_with(str(Path("mydoc.pdf")))


def test_get_file_type_unknown_mime_fallback_to_ext_py(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = (None, None)
    file_type = FileExtractor.get_file_type("script.py")
    assert file_type == "x-python"


def test_get_file_type_unknown_mime_and_unknown_ext_octet_stream(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = (None, None)
    file_type = FileExtractor.get_file_type("file.unknownext")
    assert file_type == "octet-stream"


def test_get_file_type_no_extension_str_input_octet_stream(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = (None, None)
    file_type = FileExtractor.get_file_type("noext")
    assert file_type == "octet-stream"


def test_get_file_type_no_extension_path_input_octet_stream(mocker):
    mock_guess_type = mocker.patch("TextSpitter.core.mimetypes.guess_type")
    mock_guess_type.return_value = (None, None)
    file_type = FileExtractor.get_file_type(Path("noext"))
    assert file_type == "octet-stream"


# --- is_programming_language_file tests ---
@pytest.mark.parametrize(
    "ext, expected",
    [
        ("py", True),
        ("JS", True),
        ("html", True),
        ("txt", False),
        ("pdf", False),
        ("", False),
    ],
)
def test_is_programming_language_file(ext, expected):
    assert FileExtractor.is_programming_language_file(ext) == expected


# --- get_contents tests ---
def test_get_contents_from_path(temp_dir):
    content = b"Hello from path"
    path_to_file = Path(temp_dir) / "test_file.txt"
    with open(path_to_file, "wb") as tmp_file:
        tmp_file.write(content)
    extractor = FileExtractor(file_obj=path_to_file)
    assert extractor.get_contents() == content


def test_get_contents_from_bytesio():
    data = b"bytesio test data"
    extractor = FileExtractor(file_obj=BytesIO(data), filename="dummy.bin")
    assert extractor.get_contents() == data
    assert extractor.get_contents() == data  # Test rewind


def test_get_contents_from_spooled_temp_file():
    data = b"spooled temporary file data"
    with SpooledTemporaryFile() as stf:
        stf.write(data)
        stf.seek(0)
        extractor = FileExtractor(file_obj=stf, filename="dummy.tmp")
        assert extractor.get_contents() == data
        stf.seek(0)
        assert extractor.get_contents() == data


def test_get_contents_from_bytes():
    data = b"direct bytes data"
    extractor = FileExtractor(file_obj=data, filename="dummy.raw")
    assert extractor.get_contents() == data


def test_get_contents_stream_returns_string_warns_and_encodes(log_capture):
    mock_file_obj = MagicMock(spec=IOBase)
    mock_file_obj.read = MagicMock(return_value="string data from stream")
    mock_file_obj.seek = MagicMock(return_value=0)
    extractor = FileExtractor(file_obj=mock_file_obj, filename="dummy.txt")
    content_bytes = extractor.get_contents()
    assert content_bytes == "string data from stream".encode("utf-8")
    assert "Read data from stream as string, encoding to UTF-8." in "\n".join(log_capture)


def test_get_contents_unsupported_type_raises_error():
    extractor = FileExtractor(filename="dummy.txt")
    extractor.file = 12345  # An unsupported type
    with pytest.raises(
        TypeError,
        match="FileExtractor: self.file is of an unexpected type '<class 'int'>'",
    ):
        extractor.get_contents()


# --- code_file_read tests ---
def test_code_file_read_utf8():
    content_str = "def greet(): return 'Привет, мир!'"
    extractor = FileExtractor(
        file_obj=content_str.encode("utf-8"), filename="script.py"
    )
    assert extractor.code_file_read() == content_str


def test_code_file_read_latin1():
    content_str = "café crème"
    extractor = FileExtractor(
        file_obj=content_str.encode("latin-1"), filename="script.ans"
    )
    assert extractor.code_file_read() == content_str


def test_code_file_read_fallback_to_replace_on_decode_error(mocker, log_capture):
    original_bytes_content = b"\x80\x90\xa0"  # Intended to fail initial decodes

    mock_bytes_instance = MagicMock(spec=bytes)

    def mock_decode_side_effect(encoding, errors=None):
        if encoding == "utf-8" and errors == "replace":
            return original_bytes_content.decode("utf-8", errors="replace")
        if encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            raise UnicodeDecodeError(
                encoding, b"", 0, 0, "mocked reason for loop fail"
            )
        return original_bytes_content.decode(
            encoding, errors=errors or "strict"
        )  # Fallback for unexpected calls

    mock_bytes_instance.decode = MagicMock(side_effect=mock_decode_side_effect)
    mocker.patch.object(
        FileExtractor, "get_contents", return_value=mock_bytes_instance
    )

    extractor = FileExtractor(filename="broken.bin")
    decoded_content = extractor.code_file_read()

    assert (
        "Could not decode code file broken.bin with standard encodings"
        in "\n".join(log_capture)
    )
    mock_bytes_instance.decode.assert_any_call("utf-8", errors="replace")
    assert decoded_content == original_bytes_content.decode(
        "utf-8", errors="replace"
    )


# --- pdf_file_read tests ---
def test_pdf_file_read_with_pymupdf(mocker):
    mock_pymupdf_module = mocker.patch("TextSpitter.core.pymupdf", create=True)
    assert mock_pymupdf_module is not None

    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Page 1 text. "
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Page 2 text."

    mock_opened_pdf_doc_context = MagicMock()
    mock_opened_pdf_doc_context.__enter__.return_value = [
        mock_page1,
        mock_page2,
    ]
    mock_opened_pdf_doc_context.__exit__.return_value = None
    mock_pymupdf_module.open.return_value = mock_opened_pdf_doc_context

    extractor = FileExtractor(file_obj=b"fake pdf data", filename="test.pdf")
    result = extractor.pdf_file_read()

    assert result == "Page 1 text. Page 2 text."
    mock_pymupdf_module.open.assert_called_once_with(
        stream=b"fake pdf data", filetype="pdf"
    )


def test_pdf_file_read_fallback_to_pypdf(mocker, log_capture):
    mocker.patch(
        "TextSpitter.core.pymupdf", None
    )  # Simulate pymupdf not imported
    mock_pypdf_module = mocker.patch("TextSpitter.core.pypdf", create=True)
    assert mock_pypdf_module is not None

    mock_pdf_reader_instance = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "PyPDF Page 1. "
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "PyPDF Page 2."
    mock_pdf_reader_instance.pages = [mock_page1, mock_page2]
    mock_pypdf_module.PdfReader.return_value = mock_pdf_reader_instance

    extractor = FileExtractor(file_obj=b"fake pdf data", filename="test.pdf")
    result = extractor.pdf_file_read()

    assert result == "PyPDF Page 1. PyPDF Page 2."
    assert (
        "PyMuPDF failed (pymupdf module not available or import failed.), trying PyPDF2"
        in "\n".join(log_capture)
    )
    mock_pypdf_module.PdfReader.assert_called_once()
    assert isinstance(mock_pypdf_module.PdfReader.call_args[0][0], BytesIO)
    assert (
        mock_pypdf_module.PdfReader.call_args[0][0].getvalue()
        == b"fake pdf data"
    )


def test_pdf_file_read_both_fail(mocker, log_capture):
    mock_pymupdf_module = mocker.patch("TextSpitter.core.pymupdf", create=True)
    assert mock_pymupdf_module is not None
    mock_pymupdf_module.open.side_effect = Exception("PyMuPDF open error")

    mock_pypdf_module = mocker.patch("TextSpitter.core.pypdf", create=True)
    assert mock_pypdf_module is not None
    mock_pypdf_module.PdfReader.side_effect = Exception("PyPDF reader error")

    extractor = FileExtractor(file_obj=b"fake pdf data", filename="test.pdf")
    result = extractor.pdf_file_read()

    assert result == ""
    logs = "\n".join(log_capture)
    assert "PyMuPDF failed (PyMuPDF open error), trying PyPDF2 for PDF: test.pdf" in logs
    assert "Both PyMuPDF and PyPDF2 failed for PDF test.pdf: PyPDF reader error" in logs


# --- docx_file_read tests ---
def test_docx_file_read_success(mocker):
    mock_docx_Document = mocker.patch("TextSpitter.core.Document", create=True)
    mock_doc_instance = MagicMock()
    mock_p1 = MagicMock()
    mock_p1.text = "First paragraph."
    mock_p2 = MagicMock()
    mock_p2.text = "Second paragraph."
    mock_doc_instance.paragraphs = [mock_p1, mock_p2]
    mock_docx_Document.return_value = mock_doc_instance
    extractor = FileExtractor(file_obj=b"fake docx data", filename="test.docx")
    result = extractor.docx_file_read()
    assert result == "First paragraph.\nSecond paragraph."
    assert isinstance(mock_docx_Document.call_args[0][0], BytesIO)
    assert mock_docx_Document.call_args[0][0].read() == b"fake docx data"


def test_docx_file_read_failure(mocker, log_capture):
    mocker.patch(
        "TextSpitter.core.Document",
        create=True,
        side_effect=Exception("DOCX parsing error"),
    )
    extractor = FileExtractor(file_obj=b"fake docx data", filename="test.docx")
    result = extractor.docx_file_read()
    assert result == ""
    assert (
        "Error reading DOCX file test.docx: DOCX parsing error"
        in "\n".join(log_capture)
    )


# --- text_file_read and csv_file_read tests ---
def test_text_file_read_utf8():
    content_str = "Simple text with Ümlauts and accents éàç."
    extractor = FileExtractor(
        file_obj=content_str.encode("utf-8"), filename="textfile.txt"
    )
    assert extractor.text_file_read() == content_str


def test_text_file_read_latin1_fallback():
    content_str = "Latin-1 text: ±§°"
    extractor = FileExtractor(
        file_obj=content_str.encode("latin-1"), filename="textfile.txt"
    )
    assert extractor.text_file_read() == content_str


def test_text_file_read_replace_on_decode_error(mocker, log_capture):
    original_bytes_content = (
        b"\x81\xfe\xff"  # Intended to fail utf-8 and latin-1
    )

    mock_bytes_instance = MagicMock(spec=bytes)

    def mock_decode_side_effect(encoding, errors=None):
        if encoding == "utf-8" and errors == "replace":
            return original_bytes_content.decode("utf-8", errors="replace")
        if encoding in ["utf-8", "latin-1"]:  # For text_file_read loop
            raise UnicodeDecodeError(
                encoding, b"", 0, 0, "mocked reason for loop fail"
            )
        return original_bytes_content.decode(
            encoding, errors=errors or "strict"
        )

    mock_bytes_instance.decode = MagicMock(side_effect=mock_decode_side_effect)
    mocker.patch.object(
        FileExtractor, "get_contents", return_value=mock_bytes_instance
    )

    extractor = FileExtractor(filename="badtext.txt")
    result = extractor.text_file_read()

    assert (
        "Could not decode text file badtext.txt with utf-8 or latin-1"
        in "\n".join(log_capture)
    )
    mock_bytes_instance.decode.assert_any_call("utf-8", errors="replace")
    assert result == original_bytes_content.decode("utf-8", errors="replace")


def test_csv_file_read_utf8():
    content_str = "col1,col2\nval1,val2 with accents éàç"
    extractor = FileExtractor(
        file_obj=content_str.encode("utf-8"), filename="data.csv"
    )
    assert extractor.csv_file_read() == content_str


def test_csv_file_read_latin1_fallback():
    content_str = "col1,col2\nval1,val2 with Latin-1: ±§°"
    extractor = FileExtractor(
        file_obj=content_str.encode("latin-1"), filename="data.csv"
    )
    assert extractor.csv_file_read() == content_str


def test_csv_file_read_replace_on_decode_error(mocker, log_capture):
    original_bytes_content = (
        b"\xcc\x81\xfe\xff"  # Intended to fail utf-8 and latin-1
    )

    mock_bytes_instance = MagicMock(spec=bytes)

    def mock_decode_side_effect(encoding, errors=None):
        if encoding == "utf-8" and errors == "replace":
            return original_bytes_content.decode("utf-8", errors="replace")
        if encoding in ["utf-8", "latin-1"]:  # For csv_file_read loop
            raise UnicodeDecodeError(
                encoding, b"", 0, 0, "mocked reason for loop fail"
            )
        return original_bytes_content.decode(
            encoding, errors=errors or "strict"
        )

    mock_bytes_instance.decode = MagicMock(side_effect=mock_decode_side_effect)
    mocker.patch.object(
        FileExtractor, "get_contents", return_value=mock_bytes_instance
    )

    extractor = FileExtractor(filename="bad.csv")
    result = extractor.csv_file_read()

    assert (
        "Could not decode CSV file bad.csv with utf-8 or latin-1"
        in "\n".join(log_capture)
    )
    mock_bytes_instance.decode.assert_any_call("utf-8", errors="replace")
    assert result == original_bytes_content.decode("utf-8", errors="replace")
