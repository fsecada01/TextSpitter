import mimetypes
from docx import Document
from io import BytesIO
try:
    import fitz
except Exception:
    import PyPDF2


def PdfFileRead(file):
    '''This current code provides a workaround in case MuPDF (a dependency for
    PyMuPDF) is not usable in the development environment. For such instances,
    the module relies on PyPDF2 to extract text data. However, because of the
    likelihood of white spaces being rampant in the extracted string data,
    those characters get filtered out.'''

    try:
        with file.open() as f:
            pdf_file = fitz.Document(stream=f.read(), filetype='pdf')
            raw_text = [ele.getText('text') for ele in pdf_file]
            text = ''.join(raw_text)
    # else:
    except Exception:
        with open(file, 'rb') as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            raw_text = [ele.extractText() for ele in pdf_reader.pages]
            text = ''.join(raw_text)
    return text


def DocxFileRead(file):
    with file.open() as f:
        f_stream = BytesIO(f.read())
        document = Document(f_stream)
        raw_text = [p.text for p in document.paragraphs]
        text = '\n'.join(raw_text)
    return text


def TextFileRead(file):
    return open(file, 'r').read()


def get_file_type(file):
    mime_type = mimetypes.guess_type(file)[0]
    guess_file_type = mime_type.split('/')[1]
    return guess_file_type
