"""
The main application to host the `WordLoader` object.
"""

from pathlib import Path
from typing import IO

from .core import FileExtractor
from .logger import logger


class WordLoader:
    """
    The CBO that wraps around a `FileExtractor` object. This class object
    then provides a `file_load` function to process the given file object.

    OOP design principle is being implemented to facilitate future
    features/enhancements to functionalities.
    """

    def __init__(
        self,
        file_obj: str | Path | IO | None = None,
        filename: str | None = None,
        file_attr: str = "name",
    ):
        self.file = FileExtractor(
            file_obj=file_obj, filename=filename, file_attr=file_attr
        )

    def file_load(self):
        """
        The primary function for this object. The file is processed and then
        sent to the appropriate text extraction function based on the
        appropriate file mimetype.

        Returns:
            str
        """
        file_type = self.file.file_ext.lower()

        # Primary file extension mapping
        file_ext_matrix = {
            "pdf": "pdf_file_read",
            "docx": "docx_file_read",
            "txt": "text_file_read",
            "text": "text_file_read",
            "csv": "csv_file_read",
        }

        # Check if it's a specific supported format first
        if file_type in file_ext_matrix:
            text = getattr(self.file, file_ext_matrix[file_type])()
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
            text_mime_types = [
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
            ]

            if mime_type in text_mime_types:
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
