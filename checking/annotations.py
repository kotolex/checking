from os import path
from sys import stderr
from sys import _getframe
from inspect import signature
from inspect import getsource
from inspect import isfunction
from typing import Callable, Any, Iterable, Tuple, Union, Sequence, Container, Optional

from .exceptions import *
from .classes.basic_test import Test
from .classes.data_file import DataFile
from .classes.basic_suite import TestSuite
from .helpers.others import is_file_exists, fake


def test(*args, enabled: bool = True, name: Optional[str] = None, description: Optional[str] = None,
         data_provider: Optional[str] = None, retries: int = 1, groups: Optional[Tuple[str]] = None,
         priority: int = 0, timeout: int = 0, only_if: Optional[Callable[[], bool]] = None):
    """
    Decorator, marks a function as a test. Does not work with classes, class methods and functions,
    that take arguments, except when explicitly using a data provider.

    :param args: handles the '@test' shorthand, holds the wrapped function reference
    :param enabled: marks a test as active or inactive; if inactive, all other parameters are ignored
    :param name: test name; if None, wrapped function name is used
    :param description: test description; if None, wrapped function docstring is used with parameter taking precedence
    :param data_provider: data provider name, must be resolved during the test suite bootstrap, raises otherwise
    :param retries: number of retries on the test failure; no additional attempts are made on success
    :param groups: list of test group names the marked test is assigned to; if None, the current module name is used;
        use this parameter to allow tests defined in different modules to be executed in the same test run
    :param priority: test priority, the higher the number, the later a test is executed;
        use this parameter to control the test execution order
    :param timeout: number of seconds to wait for a busy test to finish executing;
        if timeout is reached, the thread executing the test is terminated and TestBrokenException is raised;
        use sparingly due to possible memory leaks
    :param only_if: callable predicate to evaluate before the test execution;
        the test is executed only if the predicate evaluates to True;
        use this parameter to filter tests on a condition, for example the type of OS
    :return: fake
    :raise UnknownProviderName: if no corresponding data provider is found during the bootstrap
    :raise TestBrokenException: if test timeout is reached
    :raise ValueError:
        1. if only_if parameter is present and is not a callable
        2. if groups parameter is present and is not a tuple of strings
    """
    if not enabled:
        return fake

    def real_decorator(func: Callable[[], None]):
        if not data_provider:
            __check_is_function_without_args(func, 'test')
        else:
            __check_is_function_for_provider(func)
        name_ = name if name else func.__name__
        _check_func_for_soft_assert(func)
        if only_if is not None and not callable(only_if):
            raise ValueError('Only_if parameter of @test annotation must be a function, returning True or False!')
        nonlocal groups
        if not groups:
            groups = [func.__module__]
        else:
            if type(groups) not in (list, tuple, set):
                raise ValueError('Group parameter of @test annotation must be a tuple of strings (Tuple[str])!')
        for group in groups:
            test_object = Test(name_, func)
            test_object.only_if = only_if
            test_object.retries = retries
            test_object.priority = priority
            if description:
                test_object.description = description
            if timeout:
                test_object.timeout = int(timeout)
                if test_object.timeout < 0:
                    test_object.timeout = 0
            if data_provider:
                test_object.provider = data_provider
            TestSuite.get_instance().get_or_create(group).add_test(test_object)
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def provider(*args, enabled: bool = True, name: Optional[str] = None, cached: bool = False,
             map_to_str: Callable[[Any], str] = str):
    """
    Decorator, marks a function as data provider, which will supply data to a test.
    Marked function must return an **Iterable** object
    and typing error will be raised at runtime if the returned value is not an **Iterable**.
    Any test using a rising provider will be marked as 'ignored'.

    :param args: handles the '@provider' shorthand, holds the wrapped function reference
    :param enabled: marks a provider as active or inactive; if inactive, all other parameters are ignored
    :param name: provider name, maps providers to tests that use them, must be unique;
        if None, wrapped function name is used
    :param cached: toggles caching;
        if enabled, all data a provider generates will be stored into memory upon the first provider call,
        all subsequent calls will use the cached data to avoid repeating resource-intensive data fetches;
        be wary of the memory consumption
    :param map_to_str: callable attribute, must return a string representation of the data item
    :return: fake
    :raise DuplicateProviderNameException: if provider name is already registered
    :raise WrongDecoratedObject: if decorator is used on a function without return or yield statements
    """
    if not enabled:
        return fake

    def real_decorator(func: Callable[[None], Iterable]):
        __check_is_function_without_args(func, 'provider')
        if not _has_yield_or_return(func):
            raise WrongDecoratedObject(f'Function marked with @data must returns or yields Iterable!')
        name_ = name if name else func.__name__
        providers = TestSuite.get_instance().providers
        if name_ in providers:
            raise DuplicateProviderNameException(f'Provider with name "{name_}" already exists! '
                                                 f'Only unique names allowed!')
        providers[name_] = (func, map_to_str)
        nonlocal cached
        if cached:
            TestSuite.get_instance().cached.append(name_)
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before(*args, group_name: Optional[str] = None):
    """
    Decorator, marks a function as a mandatory part of each test in a group.
    The marked function is executed once strictly before each test in the specified test group.
    Use this decorator to setup specific repeating environment for each test in a group.

    :param args: handles the '@before' shorthand, holds the wrapped function reference
    :param group_name: the name of a test group test functions are bound to;
        if None, a new group with the name of the current module is created;
        decorated function does not have to be in the same module as the tests
    :return: fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'before')
        group = group_name if group_name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_before_test(func)
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def after(*args, group_name: Optional[str] = None):
    """
    Decorator, marks a function as a mandatory part of each test in a group.
    The marked function is executed once strictly after each test in a group.
    The marked function is not executed if corresponding **@before** fails.
    Use this decorator to correctly tear down fixtures built for individual tests.

    :param args: handles the '@after' shorthand, holds the wrapped function reference
    :param group_name: the name of a test group test functions in question are bound to;
        if None, a new group with the name of the current module is created;
        decorated function does not have to be in the same module as the tests
    :return: fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after')
        group = group_name if group_name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_after_test(func)
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_group(*args, name: Optional[str] = None):
    """
    Decorator, marks a function as a mandatory part of a test group bootstrap process.
    The marked function is executed once strictly before the first test in the specified test group.
    Use this decorator to build test fixtures for individual test groups.

    :param args: handles the '@before_group' shorthand, holds the wrapped function reference
    :param name: the name of a module or a test group the function is executed in advance of,
        if no name is specified, the name of the current module is used
    :return: fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'before_group')
        group = name if name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_before(func)
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def after_group(*args, name: Optional[str] = None, always_run: bool = False):
    """
    Decorator, marks a function as a mandatory part of a test group teardown process.
    The marked function is executed once strictly after all of the tests in a group have finished running.
    The marked function is not executed if corresponding **@before_group** fails, unless always_run set to True.
    Use this decorator to correctly tear down fixtures built for individual test groups.

    :param args: handles the '@after_group' shorthand, holds the wrapped function reference
    :param name: the name of a module or a test group the function is executed after,
        if no name is specified, the name of the current module is used
    :param always_run: if False, execute only if corresponding '@before_group' has finished successfully,
        if True, force the function execution anyway
    :return: fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_group')
        group = name if name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_after(func)
        if always_run:
            TestSuite.get_instance().get_or_create(group).always_run_after = True
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_suite(func: Callable[[], None]):
    """
    Decorator, marks a function as a mandatory part of the whole test suite bootstrap process.
    The marked function is executed once strictly before any of the tests and functions, marked with **@before_group**.
    Use this decorator to build test fixtures for the whole test suite.

    :param func: a callable object, must not take any arguments
    :return: None
    """
    __check_is_function_without_args(func, 'before_suite')
    TestSuite.get_instance().add_before(func)


def after_suite(*args, always_run: bool = False):
    """
    Decorator, marks a function as a mandatory part of a test suite teardown process.
    The marked function is executed once strictly after all of the test in the suite have finished running and
    all of the functions marked with **@before_group** are executed.
    The marked function is not executed if **@before_suite** fails, unless always_run set to True.
    Use this decorator to correctly tear down fixtures built for the whole test suite.

    :param args: handles the '@after_suite' decorator shorthand, holds the wrapped function reference
    :param always_run: if False, execute only if corresponding '@before_suite' has finished successfully,
        if True, force the function execution anyway
    :return: fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_suite')
        TestSuite.get_instance().add_after(func)
        if always_run:
            TestSuite.always_run_after = True
        return fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def _has_yield_or_return(function: Callable) -> bool:
    code = getsource(function)
    return ' return ' in code or ' yield ' in code


def _check_func_for_soft_assert(func):
    try:
        code = getsource(func)
        is_soft_assert_there = 'SoftAssert(' in code
        if not is_soft_assert_there:
            return
        if 'assert_all()' not in code:
            print(f'WARNING! Function {func.__module__}.{func.__name__} marked with @test seems to contains SoftAssert '
                  f'object without calling assert_all()!', file=stderr)
    except Exception:
        # Consciously ignore it, just check for a warning, this is not critical
        pass


def __check_is_function_without_args(func: Callable, annotation_name: str):
    """
    Helper, checks whether a decorator marks a function with no arguments.
    The library is designed to work with free functions, classes and methods are not supported.

    :param func: function object to check
    :param annotation_name: decorator name
    :return: None
    :raise WrongDecoratedObject: if marked function is not a free function with no arguments
    """
    if not isfunction(func) or signature(func).parameters:
        raise WrongDecoratedObject(
            f"Annotation '{annotation_name}' must be used only with no-argument functions! Its not supposed to work "
            f"with classes or class methods!")


def __check_is_function_for_provider(func: Callable[[Any], None]):
    """
    Helper, checks whether a function is compliant with the data provider API, i.e.
    takes exactly one argument.

    :param func: function object to check
    :return: None
    :raise WrongDecoratedObject if marked function is not a free function with exactly one argument
    """
    if not isfunction(func) or not signature(func).parameters:
        raise WrongDecoratedObject(f"Function '{func.__name__}' marked with data_provider has no argument!")
    if len(signature(func).parameters) > 1:
        raise WrongDecoratedObject(f"Function '{func.__name__}' marked with data_provider "
                                   f"has more than 1 argument!")


def DATA_FILE(file_path: str, name: Optional[str] = None, cached: bool = False, encoding: str = 'UTF-8',
              map_function: Optional[Callable] = None):
    """
    Convenience helper, simplifies usage of a text file as a data provider.
    Lazy-reads the specified file.
    Must be defined in the module namespace, not in a fixture or a test.
    Note: uppercase name is left deliberately, to attract attention.

    :param name: provider name, maps providers to tests that use them, must be unique;
        if None, file_path argument is used;
    :param cached: toggles caching;
        if enabled, all data provider generates will be stored into memory upon the first provider call,
        all subsequent calls will use the cached data to avoid repeating file reads;
    :param file_path: path to a file including the file name,
        relative paths are allowed but the file must be accessible from the current module directory
    :param encoding: text file encoding, defaults to UTF-8
    :param map_function: callable to execute against each read line
    :return: None
    :raise FileNotFoundError: if specified file does no exist
    """

    def wrapper():
        return DataFile(real_path, encoding=encoding, map_function=map_function)

    if name is None:
        name = file_path
    try:
        # Get last frame to verify file-path
        frame = _getframe(1)
        assert frame  # It can't be no last frame!
        first_path = path.split(frame.f_globals['__file__'])[0]
        real_path = path.join(first_path, file_path)
        if not is_file_exists(real_path):
            raise FileNotFoundError(f'Cant find file! Is file "{real_path}" exists?')
        provider(name=name, cached=cached)(wrapper)
    finally:
        del frame


def CONTAINER(value: Union[Sequence, Iterable, Container], name: str = None, map_to_str: Callable[[Any], str] = str):
    """
    Convenience helper, simplifies usage of a Python container types as a data provider,
    e.g. Iterable literals, comprehensions and generators, etc.
    Must be defined in the module namespace, not in a fixture or a test.
    Note: uppercase name is left deliberately, to attract attention.

    :param value: any object which supports the Python iterator protocol
    :param name: provider name, maps providers to tests that use them, must be unique;
        if None, 'container' is used;
    :param map_to_str: callable attribute, returning a string representation of an object
    :return: None
    """

    def _():
        return value

    name = name if name is not None else 'container'
    provider(name=name, map_to_str=map_to_str)(_)
