import inspect
from inspect import signature
from typing import Callable, Any, Iterable

from .basic_test import Test
from .basic_suite import TestSuite


# TODO timeout(?)

class WrongAnnotationPlacement(BaseException):
    pass

class DuplicateNameException(BaseException):
    pass


def __check_is_function_without_args(func: Callable, annotation_name: str):
    if not inspect.isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            f"Annotation '{annotation_name}' must be used only with no-argument functions! Its not supposed to work "
            f"with classes or class methods!")


def _fake(*args):
    pass


def test(*args, enabled: bool = True):
    if not enabled:
        return _fake

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'test')
        TestSuite.get_instance().get_or_create(func.__module__).add_test(Test(func.__name__, func))
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def data(*args, enabled: bool = True, name: str = None):
    if not enabled:
        return _fake

    def real_decorator(func: Callable[[None], Iterable]):
        __check_is_function_without_args(func, 'data')
        name_ = name if name else func.__name__
        providers = TestSuite.get_instance().providers
        if name_ in providers:
            raise DuplicateNameException(f'Data provider with name "{name_}" already exists! Only unique names allowed!')
        providers[name_] = func
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before')
    TestSuite.get_instance().get_or_create(func.__module__).add_before_test(func)


def after(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after')
    TestSuite.get_instance().get_or_create(func.__module__).add_after_test(func)


def before_module(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before_module')
    TestSuite.get_instance().get_or_create(func.__module__).add_before(func)


def after_module(*args, always_run: bool = False):
    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_module')
        TestSuite.get_instance().get_or_create(func.__module__).add_after(func)
        if always_run:
            TestSuite.get_instance().get_or_create(func.__module__).always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_suite(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before_suite')
    TestSuite.get_instance().add_before(func)


def after_suite(*args, always_run: bool = False):
    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_suite')
        TestSuite.get_instance().add_after(func)
        if always_run:
            TestSuite.always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator
