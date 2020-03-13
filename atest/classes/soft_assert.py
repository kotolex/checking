from typing import List, Callable, Any

from atest.helpers.exception_traceback import get_trace_filtered_by_filename
from atest.asserts import *


class SoftAssert:
    """
    Класс для применения мягких проверок, то есть проверок, которые не уронят тест сразу, а позволят выполнить и другие
    проверки. Это может быть удобно для получения информации о различных частях проверяемой системы, например для
    валидации каких-то полей. Позволит получить информацию о всех упавших проверках, а не о первой, как в случае с
    простым тестом.
    Пример:

    soft_assert = SoftAssert()
    soft_assert.check(lambda : equals(1, my_json['field1'], 'message'))
    soft_assert.check(lambda : equals('text', my_json['field2'], 'message'))
    soft_assert.contains(1,my_json['list'])
    soft_assert.assert_all()
    """

    def __init__(self, check_immediately: bool = False):
        """
        Инициализатор, который принимает по умолчанию, что не нужно делать проверки немедленно. Это может быть критично
        для тестов, где состояние системы может измениться из-за проверок или иных действий.
        :param check_immediately: флаг немедленной проверки условий, если True то проверка будет выполнена сразу, но
        тест не упадет, все результаты в любом случае будут выведены после вызова  assert_all()
        """
        self.__funcs = []
        self.__result = []
        self.__check_immediately = check_immediately

    def check(self, lambda_):
        """
        Мягкая проверка, принимает лямбду, которая выполнится позже, при проверке всех условий. Если флаг
        check_immediately=True, то проверяется (выполняется) сразу, но исключения будут брошены при финальной проверке.
        Рекомендуется использовать именно этот метод, для получения ошибки с трейсом.
        Пример:

        soft_assert = SoftAssert()
        soft_assert.put(lambda : equals(1,2,'message'))

        :param lambda_: лямбда не принимающая параметров
        :return: None
        """
        if self.__check_immediately:
            self._check(lambda_)
        else:
            self.__funcs.append(lambda_)

    def assert_all(self):
        """
        Проверяются все условия, полученные ранее и выводится весь список упавших проверок с указанием строк.
        Предполагается, что это будет финальное действие в любом тесте
        :return: None
        :raises AssertionError в случае падения проверок
        :raises Exception если были другие исключения при выполнении проверок
        """
        if not self.__check_immediately:
            for func in self.__funcs:
                self._check(func)
        if not self.__result:
            return
        raise AssertionError(self._create_message(self.__result))

    def equals(self, expected: Any, actual: Any, message: str = None):
        self.check(lambda: equals(expected, actual, message))

    def is_none(self, obj: Any, message: str = None):
        self.check(lambda: is_none(obj, message))

    def not_none(self, obj: Any, message: str = None):
        self.check(lambda: not_none(obj, message))

    def contains(self, part: Any, whole: Any, message: str = None):
        self.check(lambda: contains(part, whole, message))

    def not_contains(self, part: Any, whole: Any, message: str = None):
        self.check(lambda: not_contains(part, whole, message))

    def is_true(self, obj: Any, message: str = None):
        self.check(lambda: is_true(obj, message))

    def is_false(self, obj: Any, message: str = None):
        self.check(lambda: is_false(obj, message))

    def _create_message(self, exceptions: List[Exception]) -> str:
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
