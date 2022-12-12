import os
from typing import List
from configuration import Configuration

from models.file import File
from models.version import Version
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

def get_included_and_current_versions_filter(session, configuration: Configuration) -> List[str]:
    
    if not configuration.include_versions:
        return []

    current_version: Version = session.query(Version) \
                                      .filter(Version.name == configuration.next_version_name) \
                                      .first()

    return configuration.include_versions + [current_version.tag]