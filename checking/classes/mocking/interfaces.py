from typing import NoReturn

from .calls import Call


class Observer:

    def __init__(self):
        pass

    def notify(self, call_: Call) -> NoReturn:
        raise NotImplementedError()
