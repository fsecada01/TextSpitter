import mimetypes
from docx import Document
from io import BytesIO
from typing import BinaryIO


class FileExtractor:
    """
    Wrapper for extracting file contents to string
    """

    def __init__(self, file: str or BinaryIO):
        if type(file) == BinaryIO:
            self.file = file
            self.name = file.name
        elif type(file) == str:
            self.file = None
            self.name = file

    @staticmethod
    def get_file_type(file):
        mime_type = mimetypes.guess_type(file)[0]
        guess_file_type = mime_type.split("/")[1]
        return guess_file_type

    def get_contents(self):
        write_mode = "rb+"
        if ".txt" in self.name:
            write_mode = "r+"
        if self.file:
            file = self.file
            with file.open() as f:
                contents = f.read()
        else:
            with open(self.name, write_mode) as f:
                contents = f.read()
        return contents

    def PdfFileRead(self):
        """This current code provides a workaround in case MuPDF (a dependency for
        PyMuPDF) is not usable in the development environment. For such instances,
        the module relies on PyPDF2 to extract text data. However, because of the
        likelihood of white spaces being rampant in the extracted string data,
        those characters get filtered out."""

        contents = self.get_contents()

        try:
            import fitz

            pdf_file = fitz.Document(stream=contents, filetype="pdf")
            raw_text = [ele.getText("text") for ele in pdf_file]
            text = "".join(raw_text)
        # else:
        except Exception:
            import PyPDF2

            pdf_reader = PyPDF2.PdfFileReader(contents)
            raw_text = [ele.extractText() for ele in pdf_reader.pages]
            text = "".join(raw_text)
        return text

    def DocxFileRead(self):
        contents = self.get_contents()
        f_stream = BytesIO(contents)
        document = Document(f_stream)
        raw_text = [p.text for p in document.paragraphs]
        text = "\n".join(raw_text)
        return text

    def TextFileRead(self):
        return self.get_contents()
