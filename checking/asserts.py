from typing import Any, Union, Sequence, Sized

from .helpers.others import short
from .exceptions import TestBrokenException


def is_true(obj: Any, message: str = None):
    """
    Checking of the object for truth.
    :param obj: is the object for checking
    :param message: optional message, recommended to use it
    :return: None
    """
    if not obj:
        _message = _mess(message)
        raise AssertionError(f'{_message}Expected True, but got False! ')


def is_false(obj: Any, message: str = None):
    """
    Checking an object for non-truth (false).
    :param obj: is the object for checking
    :param message: optional message, recommended to use it
    :return: None
    """
    if obj:
        _message = _mess(message)
        raise AssertionError(f'{_message}Expected False, but got True')


def equals(expected: Any, actual: Any, message: str = None):
    """
    It compares the equality of two objects.
    :param expected: is the expected object
    :param actual: is the actual object
    :param message: is the message to be indicated when verification fails
    :return: None
    :raises AssertionError if the objects are not equal, indicating the objects and their types
    """
    if (expected is actual) or expected == actual:
        return
    _message = _mess(message)
    raise AssertionError(f'{_message}Objects are not equal!\n'
                         f'Expected:"{short(expected, 150)}" <{type(expected).__name__}>\n'
                         f'Actual  :"{short(actual, 150)}" <{type(actual).__name__}>!')


def not_equals(expected: Any, actual: Any, message: str = None):
    """
    It checks that objects are not equal.
    :param expected: is the expected object
    :param actual: is the actual object
    :param message: is the message to be indicated when verification fails
    :return: None
    :raises AssertionError if objects are equal
    """
    if (expected is actual) or expected == actual:
        _message = _mess(message)
        raise AssertionError(f'Objects are equal: ({short(expected)}, {short(actual)})!')


def is_none(obj: Any, message: str = None):
    """
    It checks that the object is None, the inverse function for checking not_none.
    :param obj: is the checked object
    :param message: is the message to be indicated when verification fails
    :return: None
    :raises AssertionError with type of the object
    """
    _message = _mess(message)
    if obj is not None:
        raise AssertionError(f'{_message}Object {short(obj)}<{type(obj).__name__}> is not None!')


def not_none(obj: Any, message: str = None):
    """
    It checks that the object is not None, the inverse function for is_none.
    :param obj: is the checked object
    :param message: is the message to be indicated when verification fails
    :return: None
    :raises AssertionError
    """
    _message = _mess(message)
    if obj is None:
        raise AssertionError(f'{_message}Unexpected None!')


def test_fail(message: str = None):
    """
    Forced failure of the test, can be used in rare conditions instead of checking obviously wrong conditions.
    :param message: is the optional message
    :return: None
    """
    raise AssertionError(message if message else 'Test was forcibly failed!')


def test_brake(message: str = None):
    """
    Forcibly bring the test to a broken state, can be used in rare conditions instead of throwing exceptions.
    :param message: is the optional message
    :return: None
    """
    raise TestBrokenException(message if message else 'Test was forcibly broken!')


def contains(part: Any, whole: Any, message: str = None):
    """
    Checks that one object is part of (enters) another. Similar to check a in b.
    :param part: is the object-part that is part of the whole
    :param whole: is the entity that contains a part
    :param message: is the optional message
    :return: None
    :raises AssertionError if one object is part of the second
    :raises TestBrokenException if whole is not iterable or objects cannot be checked for content, for instance
    1 in '123'
    """
    __contains_or_not(part, whole, message=message)


def not_contains(part: Any, whole: Any, message: str = None):
    """
    Checks that one object is not part (not included) of the second. Similar to checking a not in b.
    :param part: is the part object that is part of the whole
    :param whole: is the integer object that contains part
    :param message: is the optional message
    :return: None
    :raises AssertionError if one object is part of the second
    :raises TestBrokenException if whole is not iterable or objects cannot be checked for content, for instance
    1 not in '123'
    """
    __contains_or_not(part, whole, is_contains=False, message=message)


def is_zero(actual: Union[int, float]):
    """
    Function checks that the object is 0.
    :param actual: int or float argument
    :return: None
    """
    _check_argument_is_number(actual, 'is_zero')
    if actual != 0:
        raise AssertionError(f'"{short(actual)}"<{type(actual).__name__}> is not equal to zero!')


def is_positive(actual: Union[int, float, Sequence]):
    """
    Function checks that the object is bigger than 0, if it is Sequence(list, str, etc.) checks that length is positive.
    :param actual: int, float or Sequence argument
    :return: None
    """
    if type(actual) in (int, float):
        if actual <= 0:
            raise AssertionError(f'{actual} is not positive!')
    else:
        try:
            len_ = len(actual)
            if len_ <= 0:
                raise AssertionError(f'Length of "{short(actual)}"<{type(actual).__name__}> is not positive!')
        except TypeError:
            raise TestBrokenException(f'Object "{short(actual)}"<{type(actual).__name__}> has no len!')


def is_negative(actual: Union[int, float]):
    """
    Function checks that the object is smaller than 0.
    :param actual: int or float argument
    :return: None
    """
    _check_argument_is_number(actual, 'is_negative')
    if actual >= 0:
        raise AssertionError(f'"{short(actual)}"<{type(actual).__name__}> is not negative!')


def is_empty(container: Sized, message: str = None):
    """
    Function checks the container is empty (len==0)
    :param message: optional message
    :param container: any object which has size
    :return: None
    """
    _message = _mess(message)
    if _get_length_if_sized(container):
        raise AssertionError(f'{_message}"{short(container)}"<{type(container).__name__}> is not empty!')


def is_not_empty(container: Sized, message: str = None):
    """
    Function checks the container is NOT empty (len>0)
    :param message: optional message
    :param container: any object which has size
    :return: None
    """
    _message = _mess(message)
    if not _get_length_if_sized(container):
        raise AssertionError(f'{_message}"{short(container)}"<{type(container).__name__}> is empty!')


def __contains_or_not(part, whole, is_contains: bool = True, message: str = None):
    try:
        if is_contains and part in whole:
            return
        if not is_contains and part not in whole:
            return
    except TypeError as e:
        if 'requires' in e.args[0]:
            raise TestBrokenException(f'Object "{short(part)}" <{type(part).__name__}> and '
                                      f'"{short(whole)}"<{type(whole).__name__}> are of different types and '
                                      f'cant be check for contains!')
        raise TestBrokenException(
            f'"{short(whole)}"<{type(whole).__name__}> is not iterable and cant be check for contains!')
    _message = _mess(message)
    add_ = 'is a' if not is_contains else 'is not'
    raise AssertionError(f'{_message}Object "{short(part)}" <{type(part).__name__}>, {add_} part of \n'
                         f'"{short(whole, 150)}"<{type(whole).__name__}>!')


def _mess(message: str) -> str:
    return f'{message}\n' if message else ''


def _get_length_if_sized(container: Sized) -> int:
    """
    Returns length of container or raise Exception
    :param container: Sized object
    :return: length of object
    :raises: TestBrokenException if object has ho length
    """
    try:
        return len(container)
    except TypeError:
        raise TestBrokenException(f'"{short(container)}"<{type(container).__name__}> '
                                  f'has no len and cant be checked for emptiness!')


def _check_argument_is_number(actual, name: str):
    if type(actual) not in (int, float):
        raise TestBrokenException(f"Only int or float types allowed for {name}," +
                                  f" but got '{short(actual)}'<{type(actual).__name__}>")
