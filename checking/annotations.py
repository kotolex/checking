from inspect import isfunction
from inspect import signature
from inspect import getsource
from sys import stderr
from typing import Callable, Any, Iterable, Tuple

from .classes.basic_suite import TestSuite
from .classes.basic_test import Test
from .exceptions import *


def test(*args, enabled: bool = True, name: str = None, data_provider: str = None, retries: int = 1,
         groups: Tuple[str] = None, priority: int = 0, timeout: int = 0, only_if: Callable = None):
    """
    The annotation that marks a function in a module as a test, does not work with classes and class methods and with
    functions, that take an argument (except using of data provider).
    :param args: parameters, in which, among other things, a function may come if the method is marked just with  @test.
    :param enabled: is the flag of the active test, if False then the test does not fall into the run and all its other
    settings are ignored too
    :param name: the name of the test, but if there is no name, then the name is the function name
    :param data_provider: is the string name of data provider, which is not need to be in current module with test, the
    main is that it was found during assembling of test entities. If not found, the exception UnknownProviderName will
    be raised.
    :param retries: is the total amount of attempts of run test, this is the number of how many times the test will be
    run again in case of errors. If the test is successful, no more attempts are made, fixtures before and after the
    test are run just 1 time!
    :param groups: is the list of group names, to which the test will be assigned, if it empty, group automatically
    creates with the name of the module. This parameter allows to group tests from different modules to one run.
    :param priority: is the priority, for organization of tests execution order. The greater is 0, as parameter high the
    execution of the test will be done later.
    :param timeout is the number of seconds during waiting the test ends. If the test had not end, then
    TestBrokenException exception will raised, and the thread, in which the test is executing, will be interrupted.
    Due to a possible memory leak, it should be used only when there is a special need.
    :param only_if: accepts a function that will be called before the test starts and the test will only be launched if
    it returns True. Should be taken to filter tests, for instance in relation to the operating system used.
    :return: _fake
    """
    if not enabled:
        return _fake

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
            if timeout:
                test_object.timeout = int(timeout)
                if test_object.timeout < 0:
                    test_object.timeout = 0
            if data_provider:
                test_object.provider = data_provider
            TestSuite.get_instance().get_or_create(group).add_test(test_object)
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def data(*args, enabled: bool = True, name: str = None):
    """
    The annotation that marks a data provider, that is, a function that supplies data to a test. Such a function should
    return Iterable or Sequence, otherwise will be an error. It is not possible at compile time to determine if the
    function returns the correct type, so an exception with the wrong type will be thrown at runtime. Exception tests
    with such provider are added to ignored.
    :param args: are parameters in which, among other things, a function may come if the method is marked simply with
    @data
    :param enabled: the flag of the active provider, if False, then it does not fall into the list of providers and all
    its other settings are ignored
    :param name: is the name, if not specified, then takes the name of the function. By this name, tests are searched by
    the provider, therefore only unique names are allowed. Duplicate name throws DuplicateNameException
    :return: __fake
    """
    if not enabled:
        return _fake

    def real_decorator(func: Callable[[None], Iterable]):
        __check_is_function_without_args(func, 'data')
        name_ = name if name else func.__name__
        providers = TestSuite.get_instance().providers
        if name_ in providers:
            raise DuplicateNameException(f'Provider with name "{name_}" already exists! Only unique names allowed!')
        providers[name_] = func
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before(*args, group_name: str = None):
    """
    It marks the function as mandatory to run before each module/group test.
    :param group_name: the name of the group before which test the function will be executed. If no group name is
    specified, a group is automatically created with the module name. A function does not have to be in the same module
    as the tests.
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'before')
        group = group_name if group_name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_before_test(func)
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def after(*args, group_name: str = None):
    """
    It marks the function as mandatory to run after each module/group test. If there are functions running before the
    test (@before) and they failed, then these functions will not start!
    :param group_name: the name of the group after each test of which the function will be executed. If the group name
    is not specified, a group with the module name is automatically created. A function does not have to be in the same
    module as the tests.
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after')
        group = group_name if group_name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_after_test(func)
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_group(*args, name: str = None):
    """
    It marks the function as mandatory to run before the module/group is executed, that is, it is executed once before
    all module/group tests are run.
    :param name: is the name of the module or group, before which tests the function will be executed once. If no name
    is specified, then the name of the current module where the annotation is used is taken.
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'before_module')
        group = name if name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_before(func)
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def after_group(*args, name: str = None, always_run: bool = False):
    """
    It marks the function as mandatory for run after the module/group is executed, that is, it is executed once after
    all module/group tests have been completed. If there is a function running before the module/group
    (@before_module) and it failed, then this function will not be launched if the always_run=True flag is not used.
    With this flag, the function ignores the results of preliminary functions and always starts.
    :param name: is the name of the module or group after which tests will be executed once the function. If no name is
    specified, then the name of the current module where the annotation is used is taken
    :param args: are parameters in which, among other things, a function may come if the method is marked simply by
    @after_module
    :param always_run: is the function start flag, regardless of the result of the preliminary functions. If True, it
    will be launched anyway
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_module')
        group = name if name else func.__module__
        TestSuite.get_instance().get_or_create(group).add_after(func)
        if always_run:
            TestSuite.get_instance().get_or_create(func.__module__).always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_suite(func: Callable[[], None]):
    """
    Marks the function as mandatory to run before executing the entire test-suite, that is, it is performed
    once at the very beginning of testing.
    :param func: is the function that does not take any argument
    :return: None
    """
    __check_is_function_without_args(func, 'before_suite')
    TestSuite.get_instance().add_before(func)


def after_suite(*args, always_run: bool = False):
    """
    It marks the function as mandatory for the run after the entire test run (test suite) has been completed, that is,
    it is performed once at the very end of the test after all groups and tests. If there are functions before the whole
    run (@before_suite) and they failed, then this function will not be executed, except when using the
    always_run=True flag. In this case, it will always be launched.
    :param args: are parameters in which, among other things, a function may come if the method is marked simply
    @after_suite
    :param always_run: is the function start flag, regardless of the result of the preliminary functions. If True, it
    will be launched anyway
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_suite')
        TestSuite.get_instance().add_after(func)
        if always_run:
            TestSuite.always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def _fake(*args):
    """
    Stub function that does nothing
    :param args:
    :return: None
    """
    pass


def _check_func_for_soft_assert(func):
    try:
        code = getsource(func)
        is_soft_assert_there = 'SoftAssert(' in code
        if not is_soft_assert_there:
            return
        if not 'assert_all()' in code:
            print(f'WARNING! Function {func.__module__}.{func.__name__} marked with @test seems to contains SoftAssert '
                  f'object without calling assert_all()!', file=stderr)
    except Exception:
        # Consciously ignore it, just check for a warning, this is not critical
        pass


def __check_is_function_without_args(func: Callable, annotation_name: str):
    """
    Checking that the annotation is above the function without arguments, it is not intended to use annotations with
    classes and / or with their methods.
    :param func: is the function
    :param annotation_name: is the name of annotation (for errors)
    :return: None
    :raises: WrongAnnotationPlacement
    """
    if not isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            f"Annotation '{annotation_name}' must be used only with no-argument functions! Its not supposed to work "
            f"with classes or class methods!")


def __check_is_function_for_provider(func: Callable[[Any], None]):
    """
    Check that the function is suitable to accept values (use a data provider), that is, it has exactly 1 argument.
    :param func: is the function
    :return: None
    :raises: WrongAnnotationPlacement
    """
    if not isfunction(func) or not signature(func).parameters:
        raise WrongAnnotationPlacement(f"Function '{func.__name__}' marked with data_provider has no argument!")
    if len(signature(func).parameters) > 1:
        raise WrongAnnotationPlacement(f"Function '{func.__name__}' marked with data_provider "
                                       f"has more than 1 argument!")
