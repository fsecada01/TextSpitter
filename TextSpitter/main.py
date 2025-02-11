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
        file_type = self.file.file_ext
        # file_type = file_loc.split('.')[-1]

        # file_types_tup = ('pdf', 'docx', 'doc', 'txt', 'text')
        file_ext_matrix = {
            "pdf": "pdf_file_read",
            "docx": "docx_file_read",
            "txt": "text_file_read",
            "text": "text_file_read",
            "csv": "csv_file_read",
        }
        if file_type in file_ext_matrix:
            text = getattr(self.file, file_ext_matrix[file_type])()
            return text
        else:
            mime_type = self.file.get_file_type(self.file.file.name)

            logger.error(
                f"You are using an incorrect file format for file submissions. "
                f"Please upload a .docx/.doc/.txt/.pdf file OR! Note the "
                f"mimetype of your submitted data and submit an error report "
                f"to github with the following: {mime_type}"
            )
