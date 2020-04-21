import glob
from typing import Any


def short(message: Any, width: int = 10) -> str:
    """
    Reduces the string representation to a specific length, replacing all characters after the specified length with
    three dots ([...]).
    If the string representation is shorter than the specified length, it returns it unchanged.
    :param message: String or object[Any]
    :param width: Maximum string representation length
    :return: shortened string
    """
    str_ = str(message)
    if len(str_) > width:
        return str_[:45] + '[...]'
    return str_


def print_splitter_line():
    """
    Displays a dash separator in the form of a 10 dash (for separating test results)
    :return: None
    """
    print('-' * 10)


def is_file_exists(file_name: str) -> bool:
    """
    Tells, if the file with name exists
    :return: True, if the file exists
    """
    return len(glob.glob(file_name)) == 1
