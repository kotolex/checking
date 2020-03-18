class WrongAnnotationPlacement(Exception):
    """
    Бросается, если аннотация установлена над функцией принимающей аргументы, или над классом/методом класса.
    При использвании аннотации @test с указанием дата-провайдера будет брошено, если функция не принимает хотя бы один
    аргумент
    """
    pass


class DuplicateNameException(Exception):
    """
    Будет брошено, если имя провайдера уже есть в наборе, нужно переименовать метод поставщика данных или задать ему имя
    через параметр
    """
    pass


class UnknownProviderName(Exception):
    """
    Будет брошено, если после формирования тестового прогона (тест-сьюта) не найден провайдер с указанным именем
    """
    pass


class TestBrokenException(Exception):
    """
    Будет брошено для уведомления о проблемах с тестом, не связанных с ассертом
    """
    pass


class TestIgnoredException(Exception):
    """
    Будет брошено для уведомления о том, что тест проигнорирован (не выполнились фикстуры или only_if)
    """
    pass


class ExceptionWrapper(Exception):
    """
    Обертка для исключений, в которую потом можно передать другое исключение. Используется с waiting_exception
    """

    def __init__(self):
        self.value = None
        self.message = 'Expect exception, but none raised!'
        self.args = (self.message,)
        self.type = type(self)

    def __str__(self):
        return str(self.value) if self.value else self.message

    def set_value(self, exception: Exception):
        self.value = exception
        self.args = exception.args
        self.message = self.args[0]
        self.type = type(exception)
