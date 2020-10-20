import glob
from datetime import datetime
from collections.abc import Set, Mapping
from typing import Any, Iterable, Callable


def short(obj: Any, width: int = 45) -> str:
    """
    Reduces the string representation to a specific length, replacing all characters after the specified length with
    three dots ([...]) plus symbols count to end.
    If the string representation is shorter than the specified length, it returns it unchanged.
    :param obj: String or object[Any]
    :param width: Maximum string representation length
    :return: shortened string
    """
    str_ = str(obj)
    len_ = len(str_) - width
    if len_ > 0:
        return str_[:width] + f'[...+{len_}]'
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


def str_date_time():
    """
    Generates current date and time for using at file names
    :return: str like 2020-02-22_12_58_58
    """
    return datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')


def fake(*args):
    """
    Stub function that does nothing
    :param args: ignored params
    :return: None
    """
    pass


class FakePoolExecutor:
    """
    Fake to use 1 threaded execution, mimic real ThreadPool methods
    """

    def submit(self, func: Callable, param: Any):
        func(param)

    def shutdown(self, wait):
        pass


def format_seconds(seconds: float) -> str:
    """
    Creates string representation of seconds count, which format it to hours and/or minutes if possible
    :param seconds: amount of seconds
    :return: str
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
    Function to gets differs between objects for message in asserts. Objects must be the same type and has length.
    Returns empty string if objects are the same, equal, not the same type, has no length, or not one of
    (Mapping, Iterable, Set)
    :param first: any object to compare
    :param second: any object to compare
    :return: string info about difference or empty if cant be checked
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
                       f"\n    second value='{short(sec_element)}' <{type(sec_element).__name__}"
            if element != sec_element:
                return f"Diff at element index {index}:" \
                       f"\n    first  value='{short(element)}' <{type(element).__name__}>" \
                       f"\n    second value='{short(sec_element)}' <{type(sec_element).__name__}>"
    return ''
