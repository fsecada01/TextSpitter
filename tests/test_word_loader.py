from unittest.mock import MagicMock

import pytest

# Attempt to import the specific logger instance if your project structure allows
# This helps in precisely targeting the logger for adding a sink.
try:
    from TextSpitter.logger import logger as word_loader_logger_instance
except ImportError:
    # Fallback: if the specific instance isn't easily importable this way,
    # we might need to rely on loguru's global logger or how it's configured
    # in TextSpitter.main. For tests, if this fails, capsys is an alternative
    # if loguru writes to stderr.
    from loguru import logger as word_loader_logger_instance

from TextSpitter.core import FileExtractor
from TextSpitter.main import WordLoader


@pytest.fixture
def loguru_test_sink(request):  # request is a pytest fixture
    """
    Fixture to capture loguru logs from the WordLoader's logger into a list.
    Uses a marker to optionally skip if loguru logger cannot be configured.
    """
    if not (
        hasattr(word_loader_logger_instance, "add")
        and hasattr(word_loader_logger_instance, "remove")
    ):
        pytest.skip(
            "Loguru logger instance not available or not a Loguru object for "
            "sink testing."
        )

    log_messages = []

    def sink_function(message):
        log_messages.append(message.record["message"])

    handler_id = word_loader_logger_instance.add(
        sink_function, format="{message}"
    )
    yield log_messages

    try:
        word_loader_logger_instance.remove(handler_id)
    except ValueError:
        pass  # Handler already removed or never added


@pytest.fixture
def mock_file_extractor(mocker):
    """Fixture to create a mock FileExtractor instance."""
    mock_extractor = MagicMock(spec=FileExtractor)
    mock_extractor.pdf_file_read = MagicMock(return_value="pdf content")
    mock_extractor.docx_file_read = MagicMock(return_value="docx content")
    mock_extractor.text_file_read = MagicMock(return_value="text content")
    mock_extractor.csv_file_read = MagicMock(return_value="csv,content")
    mock_extractor.code_file_read = MagicMock(return_value="code content")
    mock_extractor.is_programming_language_file = MagicMock(return_value=False)
    mock_extractor.get_file_type = MagicMock(
        return_value="application/octet-stream"
    )
    return mock_extractor


@pytest.fixture
def word_loader_with_mock_extractor(mocker, mock_file_extractor):
    """Fixture to create a WordLoader instance with a mocked FileExtractor."""
    mocker.patch(
        "TextSpitter.main.FileExtractor", return_value=mock_file_extractor
    )
    return WordLoader(filename="dummy.txt")


def test_file_load_pdf_extension(
    word_loader_with_mock_extractor, mock_file_extractor
):
    mock_file_extractor.file_ext = "pdf"
    mock_file_extractor.file_name = "test.pdf"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "pdf content"
    mock_file_extractor.pdf_file_read.assert_called_once()


def test_file_load_docx_extension(
    word_loader_with_mock_extractor, mock_file_extractor
):
    mock_file_extractor.file_ext = "docx"
    mock_file_extractor.file_name = "test.docx"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "docx content"
    mock_file_extractor.docx_file_read.assert_called_once()


def test_file_load_txt_extension(
    word_loader_with_mock_extractor, mock_file_extractor
):
    mock_file_extractor.file_ext = "txt"
    mock_file_extractor.file_name = "test.txt"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "text content"
    mock_file_extractor.text_file_read.assert_called_once()


def test_file_load_text_extension_uppercase(
    word_loader_with_mock_extractor, mock_file_extractor
):
    mock_file_extractor.file_ext = "TEXT"
    mock_file_extractor.file_name = "test.TEXT"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "text content"
    mock_file_extractor.text_file_read.assert_called_once()


def test_file_load_csv_extension(
    word_loader_with_mock_extractor, mock_file_extractor
):
    mock_file_extractor.file_ext = "csv"
    mock_file_extractor.file_name = "data.csv"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "csv,content"
    mock_file_extractor.csv_file_read.assert_called_once()


def test_file_load_programming_language_file_py(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "py"
    mock_file_extractor.file_name = "script.py"
    mock_file_extractor.is_programming_language_file.return_value = True
    content = word_loader_with_mock_extractor.file_load()

    assert content == "code content"
    mock_file_extractor.is_programming_language_file.assert_called_once_with(
        "py"
    )
    mock_file_extractor.code_file_read.assert_called_once()
    full_log_text = "\n".join(loguru_test_sink)
    assert (
        f"Processing programming language file: {mock_file_extractor.file_name}"
        in full_log_text
    )


def test_file_load_programming_language_file_js(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "js"
    mock_file_extractor.file_name = "script.js"
    mock_file_extractor.is_programming_language_file.return_value = True
    content = word_loader_with_mock_extractor.file_load()

    assert content == "code content"
    mock_file_extractor.is_programming_language_file.assert_called_once_with(
        "js"
    )
    mock_file_extractor.code_file_read.assert_called_once()
    full_log_text = "\n".join(loguru_test_sink)
    assert (
        f"Processing programming language file: {mock_file_extractor.file_name}"
        in full_log_text
    )


def test_file_load_unknown_ext_fallback_to_mime_plain_text(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "log"
    mock_file_extractor.file_name = "app.log"
    mock_file_extractor.is_programming_language_file.return_value = False
    mock_file_extractor.get_file_type.return_value = "plain"
    content = word_loader_with_mock_extractor.file_load()

    assert content == "code content"
    mock_file_extractor.get_file_type.assert_called_once_with(
        mock_file_extractor.file_name
    )
    mock_file_extractor.code_file_read.assert_called_once()
    full_log_text = "\n".join(loguru_test_sink)
    assert "Processing text-based file by mime type: plain" in full_log_text


def test_file_load_unknown_ext_fallback_to_mime_javascript(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "jsx"
    mock_file_extractor.file_name = "component.jsx"
    mock_file_extractor.is_programming_language_file.return_value = False
    mock_file_extractor.get_file_type.return_value = "javascript"
    content = word_loader_with_mock_extractor.file_load()

    assert content == "code content"
    mock_file_extractor.get_file_type.assert_called_once_with(
        mock_file_extractor.file_name
    )
    mock_file_extractor.code_file_read.assert_called_once()
    full_log_text = "\n".join(loguru_test_sink)
    assert (
        "Processing text-based file by mime type: javascript" in full_log_text
    )


def test_file_load_unsupported_file_type_error_log(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "xyz"
    mock_file_extractor.file_name = "unknown.xyz"
    mock_file_extractor.is_programming_language_file.return_value = False
    mock_file_extractor.get_file_type.return_value = "application/octet-stream"
    content = word_loader_with_mock_extractor.file_load()

    assert content == ""
    mock_file_extractor.get_file_type.assert_called_once_with(
        mock_file_extractor.file_name
    )
    full_log_text = "\n".join(loguru_test_sink)
    assert (
        "You are using an incorrect file format for file submissions."
        in full_log_text
    )
    assert "application/octet-stream" in full_log_text


def test_file_load_extension_priority_over_mime(
    word_loader_with_mock_extractor, mock_file_extractor
):  # No logging to check here
    mock_file_extractor.file_ext = "txt"
    mock_file_extractor.file_name = "test.txt"
    content = word_loader_with_mock_extractor.file_load()
    assert content == "text content"
    mock_file_extractor.text_file_read.assert_called_once()
    mock_file_extractor.is_programming_language_file.assert_not_called()
    mock_file_extractor.get_file_type.assert_not_called()


def test_file_load_programming_lang_priority_over_mime(
    word_loader_with_mock_extractor, mock_file_extractor, loguru_test_sink
):
    mock_file_extractor.file_ext = "py"
    mock_file_extractor.file_name = "script.py"
    mock_file_extractor.is_programming_language_file.return_value = True
    mock_file_extractor.get_file_type.return_value = (
        "plain"  # Should be ignored
    )
    content = word_loader_with_mock_extractor.file_load()

    assert content == "code content"
    mock_file_extractor.is_programming_language_file.assert_called_once_with(
        "py"
    )
    mock_file_extractor.code_file_read.assert_called_once()
    mock_file_extractor.get_file_type.assert_not_called()
    full_log_text = "\n".join(loguru_test_sink)
    assert (
        f"Processing programming language file: {mock_file_extractor.file_name}"
        in full_log_text
    )
