from .core import *


class WordLoader:
    def __init__(self, file):
        self.name = file
        self.text = str(file)

    def file_load(self):
        file_loc = self.name
        file_type = file_loc.split('.')[-1]

        # file_types_tup = ('pdf', 'docx', 'doc', 'txt', 'text')
        file_types_tup = ('pdf', 'docx', 'txt', 'text')
        if file_type in file_types_tup:
            if file_type == file_types_tup[0]:
                text = PdfFileRead(self.name)
            elif file_type == file_types_tup[1]:
                text = DocxFileRead(self.text)
            # elif file_type == file_types_tup[2]:
            #     text = DocFileRead(self.text)
            else:
                text = TextFileRead(self.text)
            return text
        else:
            mime_type = mimetypes.guess_type(file_loc)
            print('''You are using an incorrect file format for file submissions.
            Please upload a .docx/.doc/.txt/.pdf file OR!

            Note the mimetype of your submitted data and submit an error
            report to github with the following: %s''' % (mime_type, ))
