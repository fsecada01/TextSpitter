from .main import WordLoader


name = 'TextSpitter'


def TextSpitter(file_path):
    return WordLoader(file_path).file_load()
