from contextlib import contextmanager
from typing import Any, Type, Union, Sequence
from inspect import ismodule

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException
from .helpers.others import short


def is_true(obj: Any, message: str = None):
    """
    Checking of the object for truth.
    :param object: is the object for checking
    :return: None
    """
    if not obj:
        _message = _mess(message)
        raise AssertionError(f'{_message}Expected True, but got False! ')


def is_false(obj: Any, message: str = None):
    """
    Checking an object for non-truth (false).
    :param obj: is the object for checking
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
    raise AssertionError(f'{_message}Expected "{short(expected)}" <{type(expected).__name__}>, '
                         f'but got "{short(actual)}"<{type(actual).__name__}>!')


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
        raise AssertionError(f'Objects are equal ({short(expected)}, {short(actual)})!')


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


@contextmanager
def waiting_exception(exception: Type[Exception]):
    """
    The context manager to check if an exception is thrown during certain actions. An example:

    with waiting_exception(ZeroDivisionError) as exc:
        some_action()
    print(exc.message) # Displays a message from the exception

    :param exception: is the expected exception type, you cannot use BaseException, it is not recommended to use
    Exception (better use specific exception)
    :return: ExceptionWrapper context, which is initially empty, and when an exception is thrown, gets it in the value
    parameter
    :raises TestBrokenException if BaseException is used or not inheritors of Exception
    :raises AssertionError if the wrong exception is thrown, which was expected
    :raises ExceptionWrapper if no exceptions are raised
    """
    fake = ExceptionWrapper()
    try:
        if exception is BaseException:
            raise TestBrokenException('You must use concrete exception, except of BaseException!')
        if not issubclass(type(exception), type(Exception)):
            raise TestBrokenException(f'Exception or its subclasses expected, but got '
                                      f'"{exception}"<{type(exception).__name__}>')
        yield fake
    except TestBrokenException as e:
        raise e
    except exception as e:
        fake.set_value(e)
        return
    except Exception as e:
        raise AssertionError(f'Expect {exception}, but raised {type(e).__name__} ("{e}")')
    else:
        raise fake


@contextmanager
def no_exception_expected():
    """
    The context manager for situations where exceptions are not expected to raise is more explicit than just writing a
    test without an assertion. An example:

    with no_exception_expected():
        some_action()

    :return: None
    :raises AssertionError if the exception (any descendant of Exception) nevertheless falls
    """
    try:
        yield
    except Exception as e:
        raise AssertionError(f'Expect no exception, but raised {type(e).__name__} ("{e}")')


@contextmanager
def mock_builtins(function_name: str, func):
    """
    EXPERIMENTAL!
    Mock of built-in functions like print, input and so on. After exiting the context manager, the original function
    regains its previous behavior.
    :param function_name: is the the name of one of the python built-in function
    :param func: is the replacement function, which will be called instead of the original
    :return:
    """
    import builtins as b
    if not hasattr(b, function_name):
        raise TestBrokenException(f'No build-in function "{function_name}"!')
    temp_ = None
    try:
        temp_ = getattr(b, function_name)
        setattr(b, function_name, func)
        yield
    finally:
        if temp_:
            setattr(b, function_name, temp_)


@contextmanager
def mock(module_: Any, function_name: str, func: Any):
    """
    EXPERIMENTAL!
    Context manager for moking (spoofing) any function or module attribute.
    :param module_: is the module object (not a name! it must be imported in the test)
    :param function_name: is the function name
    :param func: is the replacement function, but there may be an attribute
    :return:
    """
    if not ismodule(module_):
        raise TestBrokenException(f'"{module_} is not a module!')
    if not hasattr(module_, function_name):
        raise TestBrokenException(f'No function "{function_name} at module {module_}"!')
    temp_ = None
    try:
        temp_ = getattr(module_, function_name)
        setattr(module_, function_name, func)
        yield
    finally:
        if temp_:
            setattr(module_, function_name, temp_)


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


def __contains_or_not(part, whole, is_contains: bool = True, message: str = None):
    try:
        if is_contains and part in whole:
            return
        if not is_contains and part not in whole:
            return
    except TypeError as e:
        if 'requires' in e.args[0]:
            raise TestBrokenException(f'Object "{short(part)}" <{type(part).__name__}> and '
                                      f'"{short(whole)}"<{type(whole).__name__}> are of different types and cant be check '
                                      f'for contains!')
        raise TestBrokenException(
            f'"{short(whole)}"<{type(whole).__name__}> is not iterable and cant be check for contains!')
    _message = _mess(message)
    add_ = 'is a' if not is_contains else 'is not'
    raise AssertionError(f'{_message}Object "{short(part)}" <{type(part).__name__}>, {add_} part of '
                         f'"{short(whole)}"<{type(whole).__name__}>!')


def _mess(message: str) -> str:
    return f'{message}\n' if message else ''


def _check_argument_is_number(actual, name: str):
    if type(actual) not in (int, float):
        raise TestBrokenException(f"Only int or float types allowed for {name}," +
                                  f" but got '{short(actual)}'<{type(actual).__name__}>")
