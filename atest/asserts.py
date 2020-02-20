from typing import Any


def _mess(message: str) -> str:
    return f'{message}\n' if message else ''


def equals(expected: Any, actual: Any, message: str = None):
    if (expected is actual) or expected == actual:
        return
    _message = _mess(message)
    raise AssertionError(
        f'{_message}Expected "{expected}" ({type(expected).__name__}), but got "{actual}"({type(actual).__name__})!')


def is_none(obj: Any, message: str = None):
    _message = _mess(message)
    if obj is not None:
        raise AssertionError(f'{_message}Object {obj}({type(obj).__name__}) is not None!')


def not_none(obj: Any, message: str = None):
    _message = _mess(message)
    if obj is None:
        raise AssertionError(f'{_message}Unexpected None!')
