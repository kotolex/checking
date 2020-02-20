import inspect
from inspect import signature
from typing import Callable

from .runner import _MAIN, _DICT


class WrongAnnotationPlacement(BaseException):
    pass


def test(func: Callable[[], None]):
    if not inspect.isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            "Annotation 'test' must be used only with no-argument functions! Its not supposed to work with classes or class methods")
    _DICT[func.__module__].append(func)
    _MAIN.append(func)
