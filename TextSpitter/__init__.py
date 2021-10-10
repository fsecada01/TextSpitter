from .main import WordLoader


name = "TextSpitter"


def TextSpitter(file_obj=None, filename: str or None = None):
    return WordLoader(file_obj=file_obj, filename=filename).file_load()
