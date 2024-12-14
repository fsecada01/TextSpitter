"""
Core application that contains the `FileExtractor` class object
"""

import mimetypes
from io import BytesIO
from pathlib import Path
from typing import IO

from docx import Document


class FileExtractor:
    """
    Wrapper for extracting file contents to string
    """

    def __init__(
        self,
        file_obj: str | Path | None | IO = None,
        filename: str | None = None,
    ):
        """
        The extractor wrapper will initialize by assigning the filename to the
        object's file property; if a file-like object is provided instead of a
        name, then a file_ext arg will be required.

        `filename` is depreciated.

        Args:
            file_obj: str | Path | None
            filename: : str | None
        """

        if filename:
            self.file = Path(filename)
            self.file_ext = filename.split(".")[-1]
            self.file_name = self.file.name
        else:
            if isinstance(file_obj, str):
                file_obj = Path(file_obj)

            elif file_obj and any(
                (isinstance(file_obj, x) for x in (Path, IO))
            ):
                pass

            if hasattr(file_obj, "name"):
                self.file = file_obj
                self.file_ext = file_obj.name.split(".")[-1]
                self.file_name = file_obj.name
            else:
                raise Exception(
                    "Your file object does not contain a name attribute. Please"
                    " add a name attribute with a file extension, and try "
                    "again. Need the file ext. data for mime-typing."
                )

    @staticmethod
    def get_file_type(file: str | Path):
        """
        A static method that guesses the mime type for a given file object.
        The return value is taken from the sliced value from
        `mimetypes.guess_type`
        Args:
            file: str

        Returns:
            str

        """
        mime_type = mimetypes.guess_type(file)[0]
        return mime_type.split("/")[1]

    def get_contents(self):
        """
        Reads the contents from a file and returns it.

        Returns:
            str | int | bytes
        """
        mime_type = (
            self.get_file_type(self.file)
            if isinstance(self.file, str)
            else self.get_file_type(self.file_name)
        )
        open_mode = "r" if "text" in mime_type else "rb"
        with self.file.open(open_mode) as f:
            return f.read()

    def pdf_file_read(self):
        """
        This current code provides a workaround in case MuPDF (a dependency
        for PyMuPDF) is not usable in the development environment. For such
        instances, the module relies on PyPDF2 to extract text data. However,
        because of the likelihood of white spaces being rampant in the
        extracted string data, those characters get filtered out.
        """

        contents = self.get_contents()

        try:
            import fitz

            pdf_file = fitz.Document(stream=contents, filetype="pdf")
            raw_text = [ele.get_text("text") for ele in pdf_file]
            text = "".join(raw_text)
        # else:
        except Exception:
            import PyPDF2

            pdf_reader = PyPDF2.PdfFileReader(contents)
            raw_text = [ele.extractText() for ele in pdf_reader.pages]
            text = "".join(raw_text)
        return text

    def docx_file_read(self):
        """
        Reads contents from an MS Word file, extracts text data from paragraph
        objects, and then concatenates them to form a returnable string value.
        Returns:
            str
        """
        contents = self.get_contents()
        f_stream = BytesIO(contents)
        document = Document(f_stream)
        raw_text = [p.text for p in document.paragraphs]
        text = "\n".join(raw_text)
        return text

    def text_file_read(self):
        """
        Reads contents from a text file, and returns the string value

        Returns:
            str
        """
        with self.file.open() as f:
            return f.read()
