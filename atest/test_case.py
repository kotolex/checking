from typing import List, Callable


class TestCase:
    """
    Родитель для теста и группы тестов (тестового набора), содержит общие методы.
    """

    def __init__(self, name: str):
        self.name = name
        # Список функций, выполняемых до теста/набора
        self.before: List[Callable] = []
        # Список функций, выполняемых после теста/набора
        self.after: List[Callable] = []
        # Флаг того, что предварительная операция упала, в таком случае не будет стартовать функция после теста
        self.is_before_failed: bool = False
        # Флаг обязательного запуска функций после теста, даже если предварительные упали
        self.always_run_after: bool = False
        # Имя провайдера для дальнейшей поставки данных в тест
        self.provider = None

    def add_before(self, func: Callable):
        self.before.append(func)

    def add_after(self, func: Callable):
        self.after.append(func)
