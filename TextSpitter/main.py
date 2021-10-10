from .core import FileExtractor
from typing import IO
import mimetypes


class WordLoader:
    def __init__(self, file_obj=None, filename: str or None = None):
        self.file = FileExtractor(file_obj, filename)

    def file_load(self):
        file_type = self.file.file_ext
        # file_type = file_loc.split('.')[-1]

        # file_types_tup = ('pdf', 'docx', 'doc', 'txt', 'text')
        file_types_tup = ("pdf", "docx", "txt", "text")
        if file_type in file_types_tup:
            if file_type == file_types_tup[0]:
                text = self.file.PdfFileRead()
            elif file_type == file_types_tup[1]:
                text = self.file.DocxFileRead()
            # elif file_type == file_types_tup[2]:
            #     text = DocFileRead(self.text)
            else:
                text = self.file.TextFileRead()
            return text
        else:
            mime_type = self.file.get_file_type(self.file.name)
            print(
                f"You are using an incorrect file format for file submissions.\n\
            Please upload a .docx/.doc/.txt/.pdf file OR!\n\
            Note the mimetype of your submitted data and submit an error \
            report to github with the following: {mime_type}"
            )
