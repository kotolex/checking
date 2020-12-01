import os
import traceback
from typing import List, Tuple

SEPARATOR = os.path.sep
CASES = {
    '==': 'Objects are not equals (#1 != #2)',
    '!=': 'Objects are equal (#1 == #2)',
    '>=': '#1 is less than #2',
    '<=': '#1 is greater than #2',
    '<': '#1 is greater or equal to #2',
    '>': '#1 is less or equal to #2',
    ' is not ': '#1 is #2 (points to one object)',
    ' is ': '#1 is not #2 (points to different objects)',
}


def _is_need_to_hide(name: str) -> bool:
    """
    Helper, checks traceback strings for the library internal module and some standard library module references.
    Used to truncate uninformative parts of the exception traceback.

    :param name: name of the module
    :return: True if name is one of the excluded modules, False otherwise
    """
    parts = (f'checking{SEPARATOR}asserts.py',
             f'checking{SEPARATOR}classes{SEPARATOR}',
             f'checking{SEPARATOR}runner.py{SEPARATOR}',
             f'{SEPARATOR}contextlib.py',)
    return any(part in name for part in parts)


def get_trace(exception: Exception) -> List[Tuple]:
    """
    Parses the whole error traceback and collects assertion fail info into a list of tuples.

    :param exception: exception to analyze
    :return: list, containing pairs consisting of the error location (file name, line number and test function name)
        and the line of code, which triggered an assertion fail
    """
    result = []
    for tb in iter(traceback.extract_tb(exception.__traceback__)):
        first = f'File "{tb.filename}", line {tb.lineno}, in {tb.name}'
        second = f'-->    {tb.line}'
        result.append((first, second))
    return result


def get_trace_filtered_by_filename(exception: Exception) -> str:
    """
    Builds the assertion error report string, truncating uninformative parts
    (parts belonging to the library internal classes).

    :param exception: exception to analyze
    :return: formatted traceback string
    """
    return '\n'.join(f'{a}\n{b}' for a, b in get_trace(exception) if not _is_need_to_hide(a))


def exception_with_assert(exception: Exception) -> Exception:
    """
    Tries to handle standard Python assertions.

    :param exception: exception to analyze
    :return: forwards the exception argument back to the caller if no standard Python assertions detected,
        AssertionError with the updated traceback otherwise
    """
    trace = get_trace(exception)
    trace_last_line: str = trace[-1][-1]
    # return the original exception if no standard Python asserts detected in the traceback
    if 'assert ' not in trace_last_line:
        return exception
    trace_last_line = trace_last_line.replace('-->', '').replace('assert', '').lstrip()
    message = ''
    # parse the message text if exists (traceback line ends with a quote and a comma)
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
    error.__traceback__ = exception.__traceback__
    del exception
    return error


def _is_line_ends_with_message(line: str) -> bool:
    """
    Helper, checks if an assert statement ends with a message.

    :param line: assert statement text to check for a message
    :return: True if message exists, False otherwise
    """
    line = line[::-1].replace(' ', '')
    if line[0] != "'" and line[0] != '"':
        return False
    char = '"' if line[0] == '"' else "'"
    index_of_last_quote = line.index(char, line.index(char) + 1)
    return line[index_of_last_quote + 1] == ','
