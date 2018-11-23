import mimetypes
from docx import Document
try:
    import fitz
except Exception as e:
    import PyPDF2


def PdfFileRead(file):
    '''This current code provides a workaround in case MuPDF (a dependency for
    PyMuPDF) is not usable in the development environment. For such instances,
    the module relies on PyPDF2 to extract text data.  However, because of the
    likelihood of white spaces being rampant in the extracted string data,
    those characters get filtered out.'''
    i = 0
    text = ''

    if 'fitz' in dir():
        pdf_file = fitz.open(file)
        while i < len(pdf_file):
            text += pdf_file[i].getText('text')
            i += 1
    else:
        pdf_file = open(file, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(file)
        while i < pdf_reader.numPages:
            payload = pdf_reader.getPage(i).extractText().replace('\n', '')
            text += payload.encode('ascii', 'ignore').decode('unicode_escape')
            i += 1
    return text


def DocxFileRead(file):
    document = Document(file)
    text = ''
    for p in document.paragraphs:
        text = text + p.text + '\n'
    return text


def TextFileRead(file):
    text = open(file, 'r').read()
    return text


def get_file_type(file):
    mime_type = mimetypes.guess_type(file)[0]
    guess_file_type = mime_type.split('/')[1]
    return guess_file_type
