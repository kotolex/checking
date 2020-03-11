from typing import Callable, Any

from .basic_case import TestCase


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
        self.group_name: str = '__main__'
        self.argument: Any = None

    def run(self):
        """
        Запуск теста (функции, помеченной аннотацией test)
        :return: None
        """
        if self.argument is not None:
            self.test(self.argument)
        else:
            self.test()

    def __str__(self):
        return f'{self.group_name}.{self.name}'

    def clone(self) -> TestCase:
        """
        Клонирование объекта, мутабл поля копируются
        :return: новый Test
        """
        clone = Test(self.name, self.test)
        clone.group_name = self.group_name
        clone.provider = self.provider
        clone.after = self.after[:]
        clone.before = self.before[:]
        clone.is_before_failed = self.is_before_failed
        clone.always_run_after = self.always_run_after
        clone.retries = self.retries
        clone.priority = self.priority
        clone.argument = self.argument
        return clone
