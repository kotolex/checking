class WrongAnnotationPlacement(Exception):
    """
    Бросается, если аннотация установлена над функцией принимающей аргументы, классом или метододм класса.
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
