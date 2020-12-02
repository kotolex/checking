import glob
from datetime import datetime
from collections.abc import Set, Mapping
from typing import Any, Iterable, Callable


def short(obj: Any, width: int = 45) -> str:
    """
    Elides an object string representation to the specified length,
    adding ellipsis (...) and the remaining glyph count to the end of the string.
    Returns the string as-is if string representation is shorter than the specified width.

    :param obj: object to format the string representation for
    :param width: required string representation length
    :return: formatted elided string
    """
    str_ = str(obj)
    len_ = len(str_) - width
    if len_ > 0:
        return str_[:width] + f'[...+{len_}]'
    return str_


def print_splitter_line():
    """
    Prints test result separator (ten dashes '-') to stdout.

    :return: None
    """
    print('-' * 10)


def is_file_exists(file_name: str) -> bool:
    """
    Checks if a file exists.

    :param file_name: file name to check
    :return: True, if the file exists, False otherwise
    """
    return len(glob.glob(file_name)) == 1


def str_date_time():
    """
    Generates a datetime signature for the current time to use in a file name.

    :return: string formatted like '2020-02-22_12-58-58'
    """
    return datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')


def fake(*_):
    """
    Stub function that does nothing.

    :param _: ignored function arguments
    :return: None
    """
    pass


class FakePoolExecutor:
    """
    Fake thread pool object to use for the single-threaded execution, mimics the real ThreadPool behaviour.
    """
    def submit(self, func: Callable, param: Any):
        func(param)

    def shutdown(self, wait):
        pass


def format_seconds(seconds: float) -> str:
    """
    Formats a time count report string, employing minutes and hours if necessary.

    :param seconds: second count
    :return: formatted report string
    """
    if not seconds // 60:
        return f'{seconds:.2f} seconds'
    hours = ''
    if seconds // 3600:
        hours = f'{int(seconds // 3600)} hour(s) '
        seconds = seconds - ((seconds // 3600) * 3600)
    minutes = int(seconds // 60)
    seconds = seconds - minutes * 60
    return f'{hours}{minutes} minute(s) and {seconds:.2f} seconds'


def diff(first: Any, second: Any) -> str:
    """
    Calculates the difference between the two specified objects and builds the diff report string.
    To calculate the difference, objects must be of the same type and have the length attribute.

    :param first: any object to compare
    :param second: any object to compare
    :return: formatted diff report string or empty string if objects are the same or equal,
        are not of the same type, have no length, or do not have type Union[Mapping, Iterable, Set]
    """
    if type(first) != type(second) or first is second or first == second:
        return ''
    type_1 = type(first)
    try:
        len_first = len(first)
        len_second = len(second)
        if len_first != len_second:
            return f"Length of '{short(first, 20)}' <{type_1.__name__}> == {len_first} but " \
                   f"length of '{short(second, 20)}' <{type_1.__name__}> == {len_second}"
    except TypeError:
        return ''
    if isinstance(first, Set):
        return f"Different elements in two sets: {short(first ^ second)}"
    if isinstance(first, Mapping):
        for key, value in first.items():
            if key not in second:
                return f"Dict {short(second, 20)} has no key='{key}' <{type(key).__name__}>, but contains key(s)" \
                       f" {short(set(second.keys() - set(first.keys())), 100)}"
            if value != second[key]:
                return f"Diff in entry under key='{short(key)}' <{type(key).__name__}>:" \
                       f"\n    first  value='{short(value)}' <{type(value).__name__}>" \
                       f"\n    second value='{short(second[key])}' <{type(second[key]).__name__}>"
    if isinstance(first, Iterable):
        iter_2 = iter(second)
        for index, element in enumerate(first):
            sec_element = next(iter_2)
            if type(element) != type(sec_element):
                return f"Different types at element index {index}:" \
                       f"\n    first  value='{short(element)}' <{type(element).__name__}>" \
                       f"\n    second value='{short(sec_element)}' <{type(sec_element).__name__}>"
            if element != sec_element:
                return f"Diff at element index {index}:" \
                       f"\n    first  value='{short(element)}' <{type(element).__name__}>" \
                       f"\n    second value='{short(sec_element)}' <{type(sec_element).__name__}>"
    return ''
