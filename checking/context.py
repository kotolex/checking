import builtins
from inspect import ismodule
from io import StringIO, BytesIO
from contextlib import contextmanager
from typing import Any, Type, Iterable, List

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException
from .classes.mocking.write_wrapper import WriteWrapper


@contextmanager
def mock_builtins(function_name: str, func):
    """
    Mock of built-in functions like print, input and so on. After exiting the context manager, the original function
    regains its previous behavior.
    :param function_name: is the the name of one of the python built-in function
    :param func: is the replacement function, which will be called instead of the original
    :return:
    """
    if function_name == 'open':
        print(f'WARNING! For using mock with open function, please use mock_open. '
              f'Read the documentation at https://bitbucket.org/kotolex/atest/src')
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
def mock_input(iterable_: Iterable):
    """
    Context manager for mocking standard input function. Takes iterable argument to get data from. Pay attention that
    all values will be cast to str, like real input works (always returns str).
    It is just sugar instead of mock_builtins('input')
    :param iterable_: container with data to set in input
    :return: None
    """
    iterator = iter(iterable_)
    with mock_builtins('input', lambda *args: str(next(iterator))):
        yield


@contextmanager
def mock_print(container: List[Any]):
    """
    Context manager for mocking standard print function. Takes list as argument to collect data.
    It is just sugar instead of mock_builtins('print'). If you need some specific behaviour, like using some print
    arguments (file, end etc.) than use mock_input('print'...
    :param container: List of any types to save data
    :return: None
    """
    with mock_builtins('print', lambda arg: container.append(arg)):
        yield container


@contextmanager
def mock_open(on_read_text: str = '', on_read_bytes: bytes = b'', new_line: str = '\n', raises: Exception = None):
    """
    Context manager for mocking open text ot byte file. Use it instead of mock_builtins('open', func)
    :param on_read_text: string to get when open text file in read mode
    :param on_read_bytes: bytes to get when open bytes file in read mode
    :param new_line: how to determine new line, '\n' by default, will be ignored for bytes
    :param raises: if need to raise exception on open file. If not None - other options will be ignored
    :return: list with values, which be pushed into it by write on open file
    :raises: ValueError if on_read_* not str or bytes
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

    # If we raise on open, then no need to check arguments
    if raises is None:
        if type(on_read_text) is not str:
            raise ValueError("Parameter on_read_text must be str!")
        if type(on_read_bytes) is not bytes:
            raise ValueError('Parameter on_read_bytes must be bytes')
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
    Context manager for mocking (spoofing) any function or module attribute.
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
        raise AssertionError(f'Expect no exception, but raised {type(e).__name__} ("{e}")!')
