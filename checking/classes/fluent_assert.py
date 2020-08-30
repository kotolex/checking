from typing import Iterable, Sized, Type

from checking.asserts import *
from checking.helpers.others import short


class FluentAssert:
    """
    The class for flexible and readable checks, which can be assembled in chains (sharing if desired AND).
    If there is failure of one of the checks, the test falls and other conditions are not checked.
    An example:

    verify(my_list).is_not_none().AND.is_a(list).AND.contains(2).AND.is_sorted()

    """

    def __init__(self, obj: Any):
        """
        During initialization receive an object, which need to check. It is not intended to be a class or type!
        :param obj:
        """
        self.__actual = obj
        self._t = type(self.__actual)
        # Строковое представление объекта в сокращенном виде (не более 50 символов)
        self.str = short(self.__actual)
        # Ссылка на самого себя для читаемой последовательности проверок
        self.AND = self

    @property
    def size(self):
        """
        Switch all following checks to the length of actual object
        :return: FluentAssert
        :raises: TestBrokenException if object has no length
        """
        self._check_has_len(self.__actual)
        return FluentAssert(len(self.__actual))

    def has_attribute(self, name: str):
        """
        Check, if actual object has attribute with given name
        :param name: string name of the attribute
        :return: FluentAssert
        """
        if not hasattr(self.__actual, name):
            raise AssertionError(f'"{self.str}"{self._t} has no attribute "{short(name)}"')
        return self

    def attribute(self, name: str):
        """
        Switch all following checks to attribute of the object or raise exception, if object has no attribute with
        given name
        :param name: name of the attribute
        :return: FluentAssert
        :raises: AssertionError if object has no attribute
        """
        self.has_attribute(name)
        return FluentAssert(getattr(self.__actual, name))

    def same_as(self, obj: Any):
        """
        Check, if the instance and the current one are the same. Similarly of checking a is b.
        :param obj: is the instance for checking
        :return: None
        """
        if self.__actual is not obj:
            raise AssertionError(f'"{self.str}"{self._t} is not "{short(obj)}"{type(obj)}')
        return self

    def not_same_as(self, obj: Any):
        """
        Check, if the instance and the current one are not the same. Similarly of checking a is not b.
        :param obj: is the instance for checking
        :return: None
        """
        if self.__actual is obj:
            raise AssertionError(f'"{self.str}"{self._t} is the same as "{short(obj)}"{type(obj)}')
        return self

    def child_of(self, type_: Type):
        """
        Check, if the instance is a concrete class(type) or his child.
        :param type_: is the type for checking
        :return: None
        """
        self._check_is_type(type_)
        if issubclass(type(self.__actual), type_):
            return self
        raise AssertionError(f'"{self.str}"{self._t} is not sub-class of {type_}')

    def type_is(self, type_: Type):
        """
        Check, if the  actual object is instance of given class.
        :param type_: class to check
        :return: FluentAssert
        :raises: AssertionError if object is not instanse of given type
        """
        self._check_is_type(type_)
        if isinstance(self.__actual, type_):
            return self
        raise AssertionError(f'"{self.str}"{self._t} is not of type {type_}')

    def is_none(self):
        is_none(self.__actual)
        return self

    def is_not_none(self):
        not_none(self.__actual)
        return self

    def is_true(self):
        is_true(self.__actual)
        return self

    def is_false(self):
        is_false(self.__actual)
        return self

    def equal(self, obj: Any):
        equals(self.__actual, obj)
        return self

    def not_equal(self, obj: Any):
        not_equals(self.__actual, obj)
        return self

    def is_empty(self):
        is_empty(self.__actual)
        return self

    def is_not_empty(self):
        is_not_empty(self.__actual)
        return self

    def is_positive(self):
        is_positive(self.__actual)
        return self

    def is_negative(self):
        is_negative(self.__actual)
        return self

    def is_zero(self):
        is_zero(self.__actual)
        return self

    def less_than(self, obj: Any):
        """
        Checking that the checking object is less than current.
        :param obj: is the object for comparing
        :return:
        """
        self._check_same_type(obj)
        if self.__actual >= obj:
            raise AssertionError(f'"{self.str}" is not less than "{short(obj)}"!')
        return self

    def greater_than(self, obj: Any):
        self._check_same_type(obj)
        if self.__actual <= obj:
            raise AssertionError(f'"{self.str}" is not greater than "{short(obj)}"!')
        return self

    def equal_to_length_of(self, obj: Sized):
        self._check_has_len(obj)
        self.equal(len(obj))
        return self

    def less_than_length_of(self, obj: Sized):
        self._check_has_len(obj)
        self.less_than(len(obj))
        return self

    def greater_than_length_of(self, obj: Sized):
        self._check_has_len(obj)
        self.greater_than(len(obj))
        return self

    def is_sorted(self, reverse_order: bool = False):
        """
        Checking, that object is sorted (it can be used just to list/tuple/str and another Sequence).
        :param reverse_order: if it is True then check sort in reverse (from the biggest to the lowest)
        :return:
        """
        if not isinstance(self.__actual, Sequence):
            raise TestBrokenException(f'Only sequences can be checked for sorted, not {self._t}')
        smaller = lambda a, b: a <= b
        bigger = lambda a, b: a >= b
        check = smaller if not reverse_order else bigger
        for index, element in enumerate(self.__actual):
            if index == len(self.__actual) - 1:
                break
            if not check(element, self.__actual[index + 1]):
                raise AssertionError(f'Object "{self.str}" is not sorted!')
        return self

    def contains(self, obj: Any):
        contains(obj, self.__actual)
        return self

    def not_contains(self, obj: Any):
        not_contains(obj, self.__actual)
        return self

    def contains_in_any_order(self, obj: Iterable):
        if not isinstance(obj, Iterable):
            raise TestBrokenException(f'Only Iterables can be argument here, not {type(obj)}')
        for element in obj:
            contains(element, self.__actual)
        return self

    def is_in(self, container: Any):
        contains(self.__actual, container)
        return self

    def is_not_in(self, container: Any):
        not_contains(self.__actual, container)
        return self

    def _check_same_type(self, second):
        if self._t is not type(second):
            raise TestBrokenException('To compare "less" or "greater" both arguments must be the same type!')

    def _check_is_type(self, obj):
        if type(obj) is not type:
            raise TestBrokenException(f'Argument "{obj}"{type(obj)} is not type!')

    def _check_has_len(self, obj):
        try:
            len(obj)
        except TypeError:
            raise TestBrokenException(f'There is no length for "{short(obj)}"{type(obj)}')


def verify(obj: Any) -> FluentAssert:
    return FluentAssert(obj)
