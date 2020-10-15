import os
import traceback
from typing import List, Tuple

SEPARATOR = os.path.sep
CASES = {'==': 'Objects are not equals (#1 != #2)',
         '!=': 'Objects are equal (#1 == #2)',
         '>=': '#1 is less than #2',
         '<=': '#1 is greater than #2',
         '<': '#1 is greater or equal to #2',
         '>': '#1 is less or equal to #2',
         ' is not ': '#1 is #2 (points to one object)',
         ' is ': '#1 is not #2 (points to different objects)',
         }


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


def exception_with_assert(e: Exception) -> Exception:
    """
    Tries to handle with assert of python
    :param e: raised exception
    :return: argument exception if no 'assert' in line or changed exception otherwise
    """
    trace = get_trace(e)
    trace_last_line: str = trace[-1][-1]
    # if no assert in traceback then just reruns original exception
    if 'assert ' not in trace_last_line:
        return e
    trace_last_line = trace_last_line.replace('-->', '').replace('assert', '').lstrip()
    message = ''
    # if line ends with quote and comma, so message text exist, parse it
    if _is_line_ends_with_message(trace_last_line):
        trace_last_line, _, message = trace_last_line.rpartition(',')
        trace_last_line = trace_last_line.rstrip()
        message = message.lstrip().replace('"', '').replace("'", '') + '\n'
    for key, value in CASES.items():
        if key in trace_last_line:
            first, second = [char.lstrip().rstrip() for char in trace_last_line.split(key)]
            message = f"{message}{value.replace('#1', first).replace('#2', second)}"
            break
    else:
        message = f'{message}"{trace_last_line}" returns False but True was expected'
    error = AssertionError(message)
    error.__traceback__ = e.__traceback__
    del e
    return error


def _is_line_ends_with_message(text: str) -> bool:
    """
    Function returns True if assert statement ends with message
    """
    text = text[::-1].replace(' ', '')
    if not text[0] == "'" and not text[0] == '"':
        return False
    char = '"' if text[0] == '"' else "'"
    index_of_last_quote = text.index(char, text.index(char) + 1)
    return text[index_of_last_quote + 1] == ','
