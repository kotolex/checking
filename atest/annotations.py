import inspect
from inspect import signature

from types import FunctionType
from .runner import _MAIN, _DICT


class WrongAnnotationPlacement(BaseException):
    pass


def test(func: FunctionType):
    if not inspect.isfunction(func) or str(signature(func)) != '()':
        raise WrongAnnotationPlacement(
            "Annotation 'test' must be used only with no-argument functions! Its not supposed to work with classes or class methods")
    _DICT[func.__module__].append(func)
    _MAIN.append(func)
