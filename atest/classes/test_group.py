from typing import List, Callable, Dict

from .basic_test import Test
from .test_case import TestCase


class TestGroup(TestCase):
    """
    Класс тестового набора или группы тестов, представляет собой все тесты из одного модуля, или все тесты одной группы,
    однако это не тест-сьют (набор всех наборов). Тесть-сьют может быть только один и содержит все наборы тестов,
    тест-сьют всегда создается при старте тестирования. Если есть хоть 1 тест, то при старте будет создан тестовый набор,
     который будет помещен в тест-сьют.
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Список тестов, то есть объектов класса Test
        self.tests: List[Test] = []
        # Список функций выполняемых перед каждым тестом
        self.before_all: List[Callable] = []
        # Список функций выполняемых после каждого теста
        self.after_all: List[Callable] = []
        # Словарь результатов прогона данного набора
        self.test_results: Dict[str, List[Test]] = {'success': [], 'broken': [], 'failed': [], 'ignored': []}

    def add_test(self, test: Test):
        """
        Добавление теста в набор, при этом он получает имя группы, списки предварительных и последующих функций
        :param test: объект класса Test
        :return: None
        """
        test.group_name = self.name
        test.before = self.before_all
        test.after = self.after_all
        self.tests.append(test)

    def add_before_test(self, func: Callable):
        """
        Добавление еще одной функции в предварительный пул, для выполнения перед каждым тестом.
        :param func: функция
        :return: None
        """
        self.before_all.append(func)

    def add_after_test(self, func: Callable):
        """
        Добавление еще одной функции в завершающий пул, для выполнения после каждого теста
        :param func: функция
        :return: None
        """
        self.after_all.append(func)

    def add_result_to(self, test: TestCase, result: str = 'success'):
        """
        Добавления теста в соответствующий раздел словаря результатов
        :param test: объект TestCase
        :param result: результат, по-умолчанию успешен
        :return: None
        """
        self.test_results[result].append(test)

    def is_empty(self):
        """
        Пуст ли набор
        :return: True если нет тестов в наборе
        """
        return len(self.tests) == 0

    def tests_count(self):
        """
        Возвращает количество тестов. Если тесты уже были выполнены и есть результаты, то вернет сумму тестов из
        результатов, иначе просто количество TestCase в списке tests. Это сделано потому что на момент старта тестов
        не известно сколько их будет в сумме, благодаря перезапускам (retries) и/или провайдерам.
        :return: количество тестов
        """
        runnned_count = sum([len(e) for e in self.test_results.values()])
        return runnned_count if runnned_count else len(self.tests)
