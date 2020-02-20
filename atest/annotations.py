import inspect
from inspect import signature
from typing import Callable

from .runner import _MAIN, _DICT
from .classes import Test


class WrongAnnotationPlacement(BaseException):
    pass


def test(func: Callable[[], None]):
    if not inspect.isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            "Annotation 'test' must be used only with no-argument functions! Its not supposed to work with classes or "
            "class methods")
    _MAIN.append(Test(func.__module__, func))
