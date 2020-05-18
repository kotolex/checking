from typing import Any, Type
from inspect import ismodule
from contextlib import contextmanager

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException


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
