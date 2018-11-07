import fitz
import mimetypes
import win32com.client
from docx import Document


def PdfFileRead(file):
    pdf_file = fitz.open(file)
    i = 0
    text = ''
    while i < len(pdf_file):
        text += pdf_file[i].getText('text')
        i += 1
    return text


def DocxFileRead(file):
    document = Document(file)
    text = ''
    for p in document.paragraphs:
        text = text + p.text + '\n'
    return text


def DocFileRead(file):
    word = win32com.client.Dispatch('Word.Application')
    word.visible = False
    wb = word.Documents.Open(file)
    doc = word.ActiveDocument
    text = doc.Range().Text
    return text


def TextFileRead(file):
    text = open(file, 'r').read()
    return text


def get_file_type(file):
    mime_type = mimetypes.guess_type(file)[0]
    guess_file_type = mime_type.split('/')[1]
    return guess_file_type
