from types import FunctionType
from .runner import _MAIN, _DICT


def test(func: FunctionType):
    if str(type(func)) !="<class 'function'>":
        raise ValueError("Annotation test must be used only with functions! Its not supposed to work with class methods")
    _DICT[func.__module__].append(func)
    _MAIN.append(func)
