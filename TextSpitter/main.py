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
    ):
        self.file = FileExtractor(file_obj, filename)

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
        file_types_tup = ("pdf", "docx", "txt", "text")
        if file_type in file_types_tup:
            if file_type == file_types_tup[0]:
                text = self.file.pdf_file_read()
            elif file_type == file_types_tup[1]:
                text = self.file.docx_file_read()
            # elif file_type == file_types_tup[2]:
            #     text = DocFileRead(self.text)
            else:
                text = self.file.text_file_read()
            return text
        else:
            mime_type = self.file.get_file_type(self.file.file.name)

            logger.error(
                f"You are using an incorrect file format for file submissions. "
                f"Please upload a .docx/.doc/.txt/.pdf file OR! Note the "
                f"mimetype of your submitted data and submit an error report "
                f"to github with the following: {mime_type}"
            )
