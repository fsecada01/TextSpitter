from .core import FileExtractor
import mimetypes


class WordLoader:
    def __init__(self, file):
        self.name = file
        self.extractor = FileExtractor(file)

    def file_load(self):
        file_loc = self.name
        file_type = file_loc.split(".")[-1]
        # file_type = file_loc.split('.')[-1]

        # file_types_tup = ('pdf', 'docx', 'doc', 'txt', 'text')
        file_types_tup = ("pdf", "docx", "txt", "text")
        if file_type in file_types_tup:
            if file_type == file_types_tup[0]:
                text = self.extractor.PdfFileRead()
            elif file_type == file_types_tup[1]:
                text = self.extractor.DocxFileRead()
            # elif file_type == file_types_tup[2]:
            #     text = DocFileRead(self.text)
            else:
                text = self.extractor.TextFileRead()
            return text
        else:
            mime_type = mimetypes.guess_type(file_loc)
            print(
                f"You are using an incorrect file format for file submissions.\n\
            Please upload a .docx/.doc/.txt/.pdf file OR!\n\
            Note the mimetype of your submitted data and submit an error \
            report to github with the following: {mime_type}"
            )
