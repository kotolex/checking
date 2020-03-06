from inspect import signature
from inspect import isfunction
from typing import Callable, Any, Iterable

from .classes.basic_test import Test
from .classes.basic_suite import TestSuite
from .exceptions import *


# TODO timeout(?), unit-tests, docs!


def __check_is_function_without_args(func: Callable, annotation_name: str):
    """
    Проверка на то, что аннотация стоит над функцией без аргументов, не предполагается использование аннотаций
    с классами и/или с их методами
    :param func: функция
    :param annotation_name: название аннотации (для ошибки)
    :return: None
    :raises: WrongAnnotationPlacement
    """
    if not isfunction(func) or signature(func).parameters:
        raise WrongAnnotationPlacement(
            f"Annotation '{annotation_name}' must be used only with no-argument functions! Its not supposed to work "
            f"with classes or class methods!")


def __check_is_function_for_provider(func: Callable[[Any], None]):
    """
    Проверка, что функция пригодна принимать значения (использовать провайдер данных),
    то есть имеет как минимум 1 аргумент.
    :param func: функция
    :return: None
    :raises: WrongAnnotationPlacement
    """
    if not isfunction(func) or not signature(func).parameters:
        raise WrongAnnotationPlacement(
            f"Function '{func.__name__}' marked with data_provider has no argument! Must be one at least!")


def test(*args, enabled: bool = True, data_provider: str = None):
    """
    Аннотация, помечающая функцию в модуле как тест, не работает с классами и методами класса, а также с функциями,
    принимающими аргумент на вход (кроме использования дата провайдера).
    :param args: параметры, в которых в том числе может прийти функция, если метод помечен просто @test
    :param enabled: флаг активного теста, если False то тест не попадает в прогон и все прочие его настройки игнорируются
    :param data_provider: строковое имя дата-провайдера, который не обязательно должен быть в текущем модуле с тестом,
    главное, чтобы он был найден при сборе тестовых сущностей. Если не найден то будет брошено UnknownProviderName
    :return: _fake
    """
    if not enabled:
        return _fake

    def real_decorator(func: Callable[[], None]):
        if not data_provider:
            __check_is_function_without_args(func, 'test')
        else:
            __check_is_function_for_provider(func)
        test_object = Test(func.__name__, func)
        if data_provider:
            test_object.provider = data_provider
        TestSuite.get_instance().get_or_create(func.__module__).add_test(test_object)
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def data(*args, enabled: bool = True, name: str = None):
    """
    Аннотация помечающая поставщик данных, то есть функцию, поставляющую данные в тест. Такая функция должна возвращать
    Iterable или Sequence, иначе будет брошена ошибка. Невозможно во время компиляции определить возвращает ли функция
    верный ли тип, поэтому исключение при неверном типе будет брошено уже во время выполнения. При исключении тесты
    с таким провайдером добавляются в игнорированные.
    :param args: параметры, в которых в том числе может прийти функция, если метод помечен просто @data
    :param enabled: флаг активного поставщика, если False то он не попадает в список провайдеров и все прочие его
     настройки игнорируются
    :param name: имя, если не указано, то берет имя функции. По этому имени тесты ищут провайдер, потому допустимы
    только уникальные имена. При дублировании имени бросает DuplicateNameException
    :return: __fake
    """
    if not enabled:
        return _fake

    def real_decorator(func: Callable[[None], Iterable]):
        __check_is_function_without_args(func, 'data')
        name_ = name if name else func.__name__
        providers = TestSuite.get_instance().providers
        if name_ in providers:
            raise DuplicateNameException(f'Provider with name "{name_}" already exists! Only unique names allowed!')
        providers[name_] = func
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before(func: Callable[[], None]):
    """
    Помечает функцию, как обязательную к прогону перед каждым тестом модуля/группы
    :param func: функция, не принимающая аргументов
    :return: None
    """
    __check_is_function_without_args(func, 'before')
    TestSuite.get_instance().get_or_create(func.__module__).add_before_test(func)


def after(func: Callable[[], None]):
    """
    Помечает функцию, как обязательную к прогону после каждого теста модуля/группы. Если есть функции, прогоняющиеся
    перед тестом (@before) и они выполнились с ошибкой, то данные функции запускаться не будут!
    :param func: функция, не принимающая аргументов
    :return: None
    """
    __check_is_function_without_args(func, 'after')
    TestSuite.get_instance().get_or_create(func.__module__).add_after_test(func)


def before_module(func: Callable[[], None]):
    """
    Помечает функцию, как обязательную к прогону перед выполнением модуля/группы, то есть выполняется один раз до
    запуска всех тестов модуля/группы
    :param func: функция, не принимающая аргументов
    :return: None
    """
    __check_is_function_without_args(func, 'before_module')
    TestSuite.get_instance().get_or_create(func.__module__).add_before(func)


def after_module(*args, always_run: bool = False):
    """
    Помечает функцию, как обязательную к прогону после выполнения модуля/группы, то есть выполняется один раз после
    выполнения всех тестов модуля/группы. Если есть функция, прогоняющаяся перед модулем/группой (@before_module) и она
    выполнилась с ошибкой, то данная функция не будет запущена, если не использован флаг always_run = True. При таком
    флаге функция игнорирует результаты предварительных функций и запускается всегда
    :param args: параметры, в которых в том числе может прийти функция, если метод помечен просто @after_module
    :param always_run: флаг старта функции независимо от результата выполнения предварительных функций. Если True, то
    будет запущена в любом случае
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_module')
        TestSuite.get_instance().get_or_create(func.__module__).add_after(func)
        if always_run:
            TestSuite.get_instance().get_or_create(func.__module__).always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def before_suite(func: Callable[[], None]):
    """
    Помечает функцию, как обязательную к прогону перед выпонением всего тестового набора (тест-сьюта), то есть
    выполняется один раз в самом начале тестирования.
    :param func: функция, не принимающая аргументов
    :return: None
    """
    __check_is_function_without_args(func, 'before_suite')
    TestSuite.get_instance().add_before(func)


def after_suite(*args, always_run: bool = False):
    """
    Помечает функцию, как обязательную к прогону после выполнения всего тестового прогона (тест-сьюта), то есть
    выполняется один раз в самом конце тестирования после всех групп и тестов. Если есть функции перед всем прогоном
    (@before_suite) и они выполнились с ошибкой, то данная функция не будет выполнена, кроме случая использования флага
    always_run = True. В таком случае будет запущена всегда.
    :param args: параметры, в которых в том числе может прийти функция, если метод помечен просто @after_suite
    :param always_run: флаг старта функции независимо от результата выполнения предварительных функций. Если True, то
    будет запущена в любом случае
    :return: __fake
    """

    def real_decorator(func: Callable[[], None]):
        __check_is_function_without_args(func, 'after_suite')
        TestSuite.get_instance().add_after(func)
        if always_run:
            TestSuite.always_run_after = True
        return _fake

    if args:
        return real_decorator(args[0])
    return real_decorator


def _fake(*args):
    """
    Функция-заглушка, не делает ничего
    :param args:
    :return: None
    """
    pass
