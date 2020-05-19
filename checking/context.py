import builtins
from io import StringIO, BytesIO
from inspect import ismodule
from contextlib import contextmanager
from typing import Any, Type, Union, List, Tuple, Set

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException
from .classes.mocking.doubles import Spy


@contextmanager
def mock_builtins(function_name: str, func):
    """
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
def mock_readfile(values_to_read: Union[str, bytes, List, Tuple], new_line: str = '\n', raises: Exception = None):
    """
    Context manager for mocking open text file. Use it instead of mock_builtins('open', func)
    :param values_to_read: string/bytes or list/tuple of strings/bytes (but not both)
    :param new_line: how to determine new line, '\n' by default, will be ignored for bytes
    :param raises: if need to raise exception on open file. If not None - other options will be ignored
    :return: list of calls, where we can get args and kwargs of open function call
    :raises: ValueError if values_to_read not str/bytes or list with something except str/bytes
    """
    is_bytes: bool = type(values_to_read) is bytes
    # If we raise on open, then no need to check arguments
    if raises is None:
        if type(values_to_read) not in (str, bytes, list, tuple):
            raise ValueError('Parameter values_to_read must be str/bytes or (list, tuple) of str or bytes!')
        if type(values_to_read) not in (str, bytes):
            is_all_strings = all((type(x) is str for x in values_to_read))
            is_all_bytes = all((type(x) is bytes for x in values_to_read))
            is_bytes = is_all_bytes
            if not is_all_strings and not is_all_bytes:
                raise ValueError('Container values_to_read can contains only str OR only bytes!')
    value = values_to_read
    if type(values_to_read) not in (str, bytes) and raises is None:
        if is_bytes:
            value = b''.join(values_to_read)
        else:
            value = f'{new_line}'.join(values_to_read)
    temp_ = None
    try:
        spy = Spy()
        spy.raises(raises)
        if raises:
            spy.returns(spy)
        else:
            spy.returns(StringIO(value, newline=new_line) if not is_bytes else BytesIO(value))
        temp_ = builtins.open
        builtins.open = spy
        yield spy.chain
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
