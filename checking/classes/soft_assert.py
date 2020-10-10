from inspect import isfunction
from typing import List, Callable

from ..asserts import *
from ..helpers.exception_traceback import get_trace_filtered_by_filename


class SoftAssert:
    """
    The class for applying soft checks, that is, checks that do not stop the test immediately, but allow to perform
    other checks. This can be convenient for obtaining information about various parts of the system under test, for
    instance, for validating some of fields. It allows you to get information about all the fallen checks, and not about
    the first, as is the case with a simple test.
    An example:

    soft_assert = SoftAssert()
    soft_assert.check(lambda : equals(1, my_json['field1'], 'message'))
    soft_assert.check(lambda : equals('text', my_json['field2'], 'message'))
    soft_assert.contains(1,my_json['list'])
    soft_assert.assert_all()
    """

    def __init__(self, check_immediately: bool = False):
        """
        The initializer that accepts by default that there is no need to do checks immediately. It could be critical
        for tests, where the system state can change due to checks or other actions.
        :param check_immediately: is the flag for immediately checking the condition, if it is True, then the check will
        done right away, but the test does not fall, all results anyway will be displayed after assert_all() calling.
        """
        self.__funcs = []
        self.__result = []
        self.__check_immediately = check_immediately

    def check(self, lambda_):
        """
        Soft check that takes lambda as an argument executes later, when checking all conditions. If flag
        check_immediately=True, then checked (executed) immediately, but exceptions will be drop during the final run.
        It is recommended to use this method for obtaining the error with the trace.
        An example:

        soft_assert = SoftAssert()
        soft_assert.put(lambda : equals(1,2,'message'))

        :param lambda_: the lambda does not take any parameters
        :return: None
        """
        if not isfunction(lambda_):
            raise TestBrokenException(f'Argument for SoftAssert.check function must be function, preferably lambda!')
        if self.__check_immediately:
            self._check(lambda_)
        else:
            self.__funcs.append(lambda_)

    def assert_all(self):
        """
        Checking all conditions, which have been received before and display all list fallen checks with string
        indicating.
        Supposed, that it is the final action in any test.
        :return: None
        :raise AssertionError in the case of checks fall
        :raise Exception if there were other exceptions during checks execution
        """
        if not self.__check_immediately:
            for func in self.__funcs:
                self._check(func)
        if not self.__result:
            return
        raise AssertionError(self._create_message(self.__result))

    def equals(self, expected: Any, actual: Any, message: str = None):
        self.check(lambda: equals(expected, actual, message))

    def not_equals(self, expected: Any, actual: Any, message: str = None):
        self.check(lambda: not_equals(expected, actual, message))

    def is_none(self, obj: Any, message: str = None):
        self.check(lambda: is_none(obj, message))

    def is_not_none(self, obj: Any, message: str = None):
        self.check(lambda: is_not_none(obj, message))

    def contains(self, part: Any, whole: Any, message: str = None):
        self.check(lambda: contains(part, whole, message))

    def not_contains(self, part: Any, whole: Any, message: str = None):
        self.check(lambda: not_contains(part, whole, message))

    def is_true(self, obj: Any, message: str = None):
        self.check(lambda: is_true(obj, message))

    def is_false(self, obj: Any, message: str = None):
        self.check(lambda: is_false(obj, message))

    def is_zero(self, actual: Union[int, float]):
        self.check(lambda: is_zero(actual))

    def is_positive(self, actual: Union[int, float, Sequence]):
        self.check(lambda: is_positive(actual))

    def is_negative(self, actual: Union[int, float]):
        self.check(lambda: is_negative(actual))

    def is_empty(self, container: Sized, message: str = None):
        self.check(lambda: is_empty(container, message))

    def is_not_empty(self, container: Sized, message: str = None):
        self.check(lambda: is_not_empty(container, message))

    @staticmethod
    def _create_message(exceptions: List[Exception]) -> str:
        message = '=' * 20
        message += '\nFAILED ASSERTS:\n'
        for exception in exceptions:
            message += "\n".join([get_trace_filtered_by_filename(exception), str(exception), f'{("-" * 20)}\n'])
        return message

    def _check(self, func: Callable):
        try:
            func()
        except Exception as ex:
            self.__result.append(ex)
