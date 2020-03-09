from typing import Dict, List, Callable, Iterable, Any

from .basic_group import TestGroup
from .basic_test import Test


class TestSuite:
    """
    Класс прогона, тест-сьют, всегда в единственном экземпляре (синглтон), включает в себя все наборы.
    Если есть хоть 1 тест, то включает в себя 1 набор.
    """
    instance = None

    # Словарь пар имя набора-набор
    groups: Dict[str, TestGroup] = {}

    # Дата провайдеры (доступны всем тестам во всех наборах)
    providers: Dict[str, Callable[[None], Iterable]] = {}

    # Списки функций выполняемых перед и после всего прогона
    before: List[Callable] = []
    after: List[Callable] = []
    name: str = 'Default Test Suite'

    # Флаг что предварительные функции упали
    is_before_failed: bool = False

    # Флаг что завершающие функции нужно выполнять независимо от результата предварительных
    always_run_after: bool = False

    def __new__(cls, *args, **kwargs):
        if not TestSuite.instance:
            TestSuite.instance = super(TestSuite, cls).__new__(cls)
        return TestSuite.instance

    @classmethod
    def add_before(cls, func: Callable):
        cls.before.append(func)

    @classmethod
    def add_after(cls, func: Callable):
        cls.after.append(func)

    @classmethod
    def get_instance(cls):
        return TestSuite()

    @classmethod
    def get_or_create(cls, group_name: str) -> TestGroup:
        """
        Создает или возврашает набор тестов по имени
        :param group_name: имя набора
        :return: TestGroup
        """
        if group_name not in cls.groups:
            cls.groups[group_name] = TestGroup(group_name)
        return cls.groups[group_name]

    @classmethod
    def is_empty(cls) -> bool:
        """
        Возвращает пустой ли прогон (нет тестов ни в одной из групп)
        :return: True если нет тестов
        """
        return all([group.is_empty() for group in cls.groups.values()])

    @classmethod
    def tests_count(cls) -> int:
        """
        Возвращает общее количество тестов. В набор попадают только тесты с параметром enabled=True
        :return: количество тестов
        """
        if cls.is_empty():
            return 0
        return sum([group.tests_count() for group in cls.groups.values()])

    @classmethod
    def success(cls) -> List[Test]:
        """
        Возвращает список успешных тестов
        :return:
        """
        return cls._test_result_of('success')

    @classmethod
    def failed(cls) -> List[Test]:
        """
        Возвращает список упаших тестов
        :return:
        """
        return cls._test_result_of('failed')

    @classmethod
    def broken(cls) -> List[Test]:
        """
        Возвращает список сломанных тестов (упали по исключению, а не ассерту)
        :return:
        """
        return cls._test_result_of('broken')

    @classmethod
    def ignored(cls) -> List[Test]:
        """
        Возвращает список проигнорированных тестов (неудачные предварительные функции)
        :return:
        """
        return cls._test_result_of('ignored')

    @classmethod
    def _test_result_of(cls, name: str) -> List[Test]:
        return [test for group in cls.groups.values() for test in group.test_results[name]]
