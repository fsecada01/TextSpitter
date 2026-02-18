"""
The main application to host the `WordLoader` object.
"""

from pathlib import Path

from .core import FileExtractor
from .logger import logger


class WordLoader:
    """
    Dispatch wrapper that routes a file to the correct
    :class:`~TextSpitter.core.FileExtractor` reader.

    Accepts a file-system path (``str`` or :class:`pathlib.Path`) and an
    optional *filename* hint.  Strings are converted to
    :class:`~pathlib.Path` objects automatically.

    Use :class:`~TextSpitter.core.FileExtractor` directly if you need to
    pass a ``BytesIO``, ``SpooledTemporaryFile``, or raw ``bytes``.
    """

    FILE_EXT_MATRIX: dict[str, str] = {
        "pdf": "pdf_file_read",
        "docx": "docx_file_read",
        "txt": "text_file_read",
        "text": "text_file_read",
        "csv": "csv_file_read",
    }

    TEXT_MIME_TYPES: frozenset[str] = frozenset(
        {
            "plain",
            "javascript",
            "x-python",
            "x-c",
            "x-java-source",
            "x-c++",
            "html",
            "css",
            "json",
            "xml",
        }
    )

    def __init__(
        self,
        file_obj: str | Path | None = None,
        filename: str | None = None,
        file_attr: str = "name",
    ):
        if isinstance(file_obj, str):
            file_obj = Path(file_obj)
        self.file = FileExtractor(
            file_obj=file_obj, filename=filename, file_attr=file_attr
        )

    def file_load(self) -> str:
        """
        The primary function for this object. The file is processed and then
        sent to the appropriate text extraction function based on the
        appropriate file mimetype.

        Returns:
            str
        """
        file_type = self.file.file_ext.lower()

        # Check if it's a specific supported format first
        if file_type in self.FILE_EXT_MATRIX:
            text = getattr(self.file, self.FILE_EXT_MATRIX[file_type])()
            return text
        # Check if it's a programming language file
        elif self.file.is_programming_language_file(file_type):
            logger.info(
                f"Processing programming language file: {self.file.file_name}"
            )
            text = self.file.code_file_read()
            return text
        else:
            # Fall back to mime type detection
            mime_type = self.file.get_file_type(self.file.file_name)

            # Check if mime type suggests it's a text-based file
            if mime_type in self.TEXT_MIME_TYPES:
                logger.info(
                    f"Processing text-based file by mime type: {mime_type}"
                )
                text = (
                    self.file.code_file_read()
                )  # Use code_file_read for better encoding handling
                return text

            logger.error(
                f"You are using an incorrect file format for file submissions. "
                f"Please upload a .docx/.doc/.txt/.pdf file or a supported "
                f"programming language file (.py, .js, .java, .cpp, etc.). "
                f"Note the mimetype of your submitted data and submit an "
                f"error report to github with the following: {mime_type}"
            )

            return ""
