import builtins

from inspect import ismodule
from io import StringIO, BytesIO
from contextlib import contextmanager
from typing import Any, Type, Iterable, List, Callable, Union

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException
from .classes.mocking.write_wrapper import WriteWrapper


@contextmanager
def mock_builtins(function_name: str, func: Callable):
    """
    Provides a context within which built-in functions (print, input, open, etc.),
    can be replaced with a mock implementation.
    Reverts the mocked function to the original implementation upon exiting the context.

    :param function_name: a python built-in function name
    :param func: callback to replace the original
    :return: None
    """
    if function_name == 'open':
        print(f'WARNING! It\'s strongly recommended to use mock_open() to mock the open() built-in.'
              f'Refer to: https://bitbucket.org/kotolex/atest/src')
    import builtins as b
    if not hasattr(b, function_name):
        raise TestBrokenException(f'No build-in "{function_name}" found!')
    temp_ = None
    try:
        temp_ = getattr(b, function_name)
        setattr(b, function_name, func)
        yield
    finally:
        if temp_:
            setattr(b, function_name, temp_)


@contextmanager
def mock_input(iterable_: Iterable[str]):
    """
    Convenience helper, shorthand for mock_builtins('input', func).

    :param iterable_: collection of values to feed via input.
    Please note, that values will be forcibly cast to str to mimic the original behavior.
    :return: None
    """
    iterator = iter(iterable_)
    with mock_builtins('input', lambda *args: str(next(iterator))):
        yield


@contextmanager
def mock_print(container: List[str]):
    """
    Convenience helper, shorthand for mock_builtins('print', func).
    Accumulates the "print"-ed strings into the "container" argument.
    If you need some specific behavior, e.g. use print arguments, please use generic mock_builtins('print', func).

    :param container: a list container, to store the printed strings
    :return: None
    """
    with mock_builtins('print', lambda *args, **kwargs: container.append(args)):
        yield container


@contextmanager
def mock_open(on_read_text: str = '', on_read_bytes: bytes = b'',
              new_line: str = '\n', raises: Exception = None) -> List[Union[str, bytes]]:
    """
    Convenience helper to mock the open() built-in.
    Strongly recommended to use this one instead of mock_builtins('open', func)

    :param on_read_text: string to return for mode="rt"
    :param on_read_bytes: bytes to return for mode="rb"
    :param new_line: new line delimiter, is ignored for mode="rb"
    :param raises: error to raise on file open, other parameters are ignored
    :return: a list of written str/bytes values for mode="w"
    :raise: ValueError if on_read_* parameter does not have correct type
    """
    container = []

    def fake_open(*args, **kwargs):
        if raises:
            raise raises
        if (len(args) > 1 and 'w' in args[1]) or (kwargs.get("mode") and 'w' in kwargs.get("mode")):
            return WriteWrapper(container)
        if (len(args) > 1 and 'b' in args[1]) or (kwargs.get("mode") and 'b' in kwargs.get("mode")):
            return BytesIO(on_read_bytes)
        return StringIO(on_read_text, new_line)

    # skip argument parsing if raises on open
    if raises is None:
        if type(on_read_text) is not str:
            raise ValueError("on_read_text must be str")
        if type(on_read_bytes) is not bytes:
            raise ValueError('on_read_bytes must be bytes')
    temp_ = None
    try:
        temp_ = builtins.open
        builtins.open = fake_open
        yield container
    finally:
        if temp_:
            builtins.open = temp_


@contextmanager
def mock(module_: Any, function_name: str, func: Any):
    """
    Provides a context within which an arbitrary object can be replaced with a mock implementation.
    Restores the original behavior upon exiting the context.

    :param module_: an imported module object
    :param function_name: object name to mock
    :param func: the replacement object
    :return: None
    """
    if not ismodule(module_):
        raise TestBrokenException(f'"{module_} is not a module!')
    if not hasattr(module_, function_name):
        raise TestBrokenException(f'No object "{function_name} found in module {module_}"!')
    temp_ = None
    try:
        temp_ = getattr(module_, function_name)
        setattr(module_, function_name, func)
        yield
    finally:
        if temp_:
            setattr(module_, function_name, temp_)


@contextmanager
def should_raise(exception: Type[Exception]) -> ExceptionWrapper:
    """
    Expects and catches a specified exception.

    Example:

        with should_raise(ZeroDivisionError) as exc:
            some_action()
        print(exc.message) # Displays a message from the exception

    :param exception: expected exception type. While Exception itself is allowed, prefer using specific exception types.
    The use of BaseException is forbidden.
    :return: ExceptionWrapper helper object
    :raise TestBrokenException if BaseException is used or exception parameter is not an Exception subclass
    :raise AssertionError if a wrong exception is caught
    :raise ExceptionWrapper if no exceptions are raised
    """
    fake = ExceptionWrapper()
    try:
        if exception is BaseException:
            raise TestBrokenException('BaseException is forbidden, you must use concrete exception types.')
        if not issubclass(type(exception), type(Exception)):
            raise TestBrokenException(f'Expected Exception or a subclass, got '
                                      f'"{exception}"<{type(exception).__name__}>')
        yield fake
    except TestBrokenException as e:
        raise e
    except exception as e:
        fake.set_value(e)
        return
    except Exception as e:
        raise AssertionError(f'Expected {exception}, got {type(e).__name__} ("{e}")')
    else:
        raise fake


@contextmanager
def no_exception_expected():
    """
    Ensures no exception is raised within itself. Use this instead of a naked call.

    Example:

        with no_exception_expected():
            some_action()

    :return: None
    :raise AssertionError if any exception is raised
    """
    try:
        yield
    except Exception as e:
        raise AssertionError(f'Expect no exception, but raised {type(e).__name__} ("{e}")!')
