import inspect
from inspect import signature
from typing import Callable

from .runner import _MAIN
from .classes import Test


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
    _MAIN.append(Test(func.__module__, func))


def before(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before')
    Test.before_each(func.__module__, func)


def after(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after')
    Test.after_each(func.__module__, func)


def before_module(func: Callable[[], None]):
    __check_is_function_without_args(func, 'before_module')
    Test.before_module(func.__module__, func)


def after_module(func: Callable[[], None]):
    __check_is_function_without_args(func, 'after_module')
    Test.after_module(func.__module__, func)
