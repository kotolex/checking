from typing import Any, Iterable
from atest.exceptions import *
from atest.asserts import *


class FluentAssert:
    """
    Класс для гибких, читаемых проверок
    """

    def __init__(self, obj: Any):
        self.__actual = obj

    def is_a(self, type_: Type):
        if type(type_) is not type:
            raise TestBrokenException(f'Argument "{type_}"{type(type_)} is not type!')
        assert isinstance(self.__actual, type_)

    def is_none(self):
        is_none(self.__actual)

    def is_not_none(self):
        not_none(self.__actual)

    def equal(self, obj: Any):
        equals(self.__actual, obj)

    def not_equal(self, obj: Any):
        not_equals(self.__actual, obj)

    def less_than(self, obj: Any):
        if not type(self.__actual) is type(obj):
            raise TestBrokenException('To compare "less" or "greater" both arguments must be the same type!')
        assert self.__actual < obj

    def greater_than(self, obj: Any):
        if not type(self.__actual) is type(obj):
            raise TestBrokenException('To compare "less" or "greater" both arguments must be the same type!')
        assert self.__actual > obj

    def length_equal_to_length_of(self, obj: Any):
        try:
            len_ = len(self.__actual)
            len_obj = len(obj)
            if len_ != len_obj:
                raise AssertionError(f'Length of object is {len_}, it is not equal to {len_obj}')
        except TypeError:
            raise TestBrokenException(f'There is no length for one of ["{self.__actual}"{type(self.__actual)},'
                                      f' "{obj}"{type(obj)}]')

    def length_equal_to(self, obj: int):
        try:
            len_ = len(self.__actual)
            if type(obj) is not int:
                raise TestBrokenException(f'Length can be only int type, not {type(obj)}')
            if len_ != obj:
                raise AssertionError(f'Length of object is {len_}, it is not equal to {obj}')
        except TypeError:
            raise TestBrokenException(f'There is no length for object "{self.__actual}"{type(self.__actual)}')

    def length_less_than_length_of(self, obj: Any):
        assert len(self.__actual) < len(obj)

    def length_less_than(self, obj: int):
        assert len(self.__actual) < obj

    def length_greater_than_length_of(self, obj: Any):
        assert len(self.__actual) > len(obj)

    def length_greater_than(self, obj: int):
        assert len(self.__actual) > obj

    def is_sorted(self, reverse_order: bool = False):
        def smaller(a, b):
            return a <= b

        def bigger(a, b):
            return a >= b

        check = smaller if not reverse_order else bigger
        for index, element in enumerate(self.__actual):
            if index == len(self.__actual) - 1:
                break
            if not check(element, self.__actual[index + 1]):
                raise AssertionError(f'Object {self.__actual} is not sorted!')

    def contains(self, obj: Any):
        contains(obj, self.__actual)

    def not_contains(self, obj: Any):
        assert obj not in self.__actual

    def child_of(self, obj: Type):
        assert issubclass(type(self.__actual), obj)

    def contains_in_any_order(self, obj: Iterable):
        for element in obj:
            contains(element, self.__actual)


def verify(obj: Any) -> FluentAssert:
    return FluentAssert(obj)
