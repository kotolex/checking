from typing import Callable

from .test_case import TestCase


class Test(TestCase):
    """
    Класс представляющий тест, основная единица тестового прогона
    """

    def __init__(self, name: str, test: Callable):
        """
        Инициализация объекта кроме имени требует ссылки на функцию, которая и является тестом
        :param name: имя теста
        :param test: функция, которая будет запущена при выполнении теста
        """
        super().__init__(name)
        self.test = test
        self.group_name = '__main__'

    def run(self):
        """
        Запуск теста (функции, помеченной аннотацией test)
        :return: None
        """
        self.test()

    def __str__(self):
        return f'{self.group_name}.{self.name}'
