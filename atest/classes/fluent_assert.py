from typing import Any, Iterable
from atest.exceptions import *
from atest.asserts import *


class FluentAssert:
    """
    Класс для гибких, читаемых проверок
    """

    def __init__(self, obj: Any):
        self.__actual = obj

    def is_a(self, type_):
        assert isinstance(self.__actual, type_)

    def is_none(self):
        pass

    def is_not_none(self):
        pass

    def equal(self, obj: Any):
        assert self.__actual == obj

    def not_equal(self, obj: Any):
        assert self.__actual != obj

    def less_than(self, obj: Any):
        assert self.__actual < obj

    def greater_than(self, obj: Any):
        assert self.__actual > obj

    def length_equal_to_length_of(self, obj: Any):
        assert len(self.__actual) == len(obj)

    def length_equal_to(self, obj: int):
        assert len(self.__actual) == obj

    def length_less_than_length_of(self, obj: Any):
        assert len(self.__actual) < len(obj)

    def length_less_than(self, obj: int):
        assert len(self.__actual) < obj

    def length_greater_than_length_of(self, obj: Any):
        assert len(self.__actual) > len(obj)

    def length_greater_than(self, obj: int):
        assert len(self.__actual) > obj

    def is_sorted(self, reverse_order: bool = False):
        pass
        # TODO 1

    def contains(self, obj: Any):
        assert obj in self.__actual

    def not_contains(self, obj: Any):
        assert obj not in self.__actual

    def child_of(self, obj: Any):
        assert issubclass(type(self.__actual), obj)

    def contains_in_any_order(self, obj: Iterable):
        pass
        # TODO


def verify(obj: Any) -> FluentAssert:
    return FluentAssert(obj)
