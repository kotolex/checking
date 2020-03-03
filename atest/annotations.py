import inspect
from inspect import signature
from typing import Callable

from .basic_test import Test
from .basic_suite import TestSuite


# TODO always run, enabled, timeout(?)

class WrongAnnotationPlacement(BaseException):
    pass


def __check_is_function_without_args(func: Callable, annotation_name: str):
    if not inspect.isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            f"Annotation '{annotation_name}' must be used only with no-argument functions! Its not supposed to work "
            f"with classes or class methods!")


def test(func: Callable[[], None]):
    __check_is_function_without_args(func, 'test')
    TestSuite.get_instance().get_or_create(func.__module__).add_test(Test(func.__name__, func))


def before(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before')
    TestSuite.get_instance().get_or_create(func.__module__).add_before_test(func)


def after(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after')
    TestSuite.get_instance().get_or_create(func.__module__).add_after_test(func)


def before_module(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before_module')
    TestSuite.get_instance().get_or_create(func.__module__).add_before(func)


def after_module(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after_module')
    TestSuite.get_instance().get_or_create(func.__module__).add_after(func)


def before_suite(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before_suite')
    TestSuite.get_instance().add_before(func)


def after_suite(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after_suite')
    TestSuite.get_instance().add_after(func)
