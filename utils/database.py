import os

from models.file import File
from utils.proglang import guess_programing_language

def save_file_if_not_found(session, file_path):
    file = session.query(File).filter(File.path == file_path).first()
    if not file:
        # Guess the programming language
        extension = os.path.splitext(file_path)[-1]
        lang = guess_programing_language(extension)
        file = File(path=file_path, language=lang)
        session.add(file)
        session.commit()
    return file
