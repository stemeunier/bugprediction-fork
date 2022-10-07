from tests.__fixtures__ import *

def test_guess_programing_language():
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
    pass