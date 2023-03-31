import os
import json

def guess_programing_language(file_extension):
    """
    Guess what is the programming language from a file extension
    
    
    >>>guess_programing_language("php")
    PHP
    >>>guess_programing_language(".php")
    PHP
    >>>guess_programing_language(".hidden/test.h")
    C
    >>>guess_programing_language("")
    None
    >>>guess_programing_language("java")
    Java
    >>>guess_programing_language("c++")
    C++
    >>>guess_programing_language("c")
    C
    >>>guess_programing_language("class")
    None
    >>>guess_programing_language("cpp")
    C++
    """
    # Clean the input
    if (file_extension == ""):
        return None
    elif "/" in file_extension:
        file_extension = os.path.splitext(file_extension)[1]
    if (file_extension == ""):
        return None
    if file_extension[0] != ".":
        file_extension = "." + file_extension

    # TODO : bug when the file is at the root folder of the project
        
    # Load the Github's Linguist JSON map
    if hasattr(guess_programing_language, 'language_map') is False:
        fd = open(os.path.dirname(os.path.realpath(__file__)) + "/resources/languages.json",mode='r')
        guess_programing_language.language_map = json.load(fd)
        fd.close()
    
    # Match with the most probable language
    language_results = list(map(
            lambda file_args: file_args[0] if file_extension in list(map(
                lambda i: i, file_args[1].get("extensions", []))) else None, guess_programing_language.language_map.items()))
    language_results = list(filter(None, language_results))
    return language_results[0] if len(language_results) > 0 else None

def is_python_file(file_name) -> bool:
    """
    Checks if a given file name corresponds to a Python file.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        bool: `True` if the file name corresponds to a Python file, `False` otherwise.
    """
    extension = file_name.split('.')[-1].lower()
    return extension == 'py'