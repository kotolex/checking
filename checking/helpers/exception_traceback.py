import os
import traceback
from typing import List, Tuple

SEPARATOR = os.path.sep


def _is_need_to_hide(name: str) -> bool:
    parts = (f'checking{SEPARATOR}asserts.py',
             f'checking{SEPARATOR}classes{SEPARATOR}',
             f'checking{SEPARATOR}runner.py{SEPARATOR}',
             f'{SEPARATOR}contextlib.py',)
    """
    Check the strings of traceback for the contents of the internal modules of the project and some modules of standard 
    library, to as not to display error traces (which the user is not interested in).
    :param name: is the name
    :return: True if it is the name of one of the internal modules.
    """
    return any([part in name for part in parts])


def get_trace(exception_: Exception) -> List[Tuple]:
    """
    Returns all trace of error as list, which consists with tuples (error line location, an error).
    :param exception_:  is the exception that whose trace is needed.
    :return: the list of tuples.
    """
    result = []
    for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
        first = f'File "{tb.filename}", line {tb.lineno}, in {tb.name}'
        second = f'-->    {tb.line}'
        result.append((first, second))
    return result


def get_trace_filtered_by_filename(exception_: Exception) -> str:
    """
    Returns string representation of the trace error, which has been filtered by module name, actually remain only
    strings which are not owned by the main 'checking' classes.
    :param exception_: the exception, whose stacktrace is needed
    :return: the string, where each note is defined \n
    """
    return '\n'.join([f'{a}\n{b}' for a, b in get_trace(exception_) if not _is_need_to_hide(a)])
