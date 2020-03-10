from contextlib import contextmanager
from typing import Any, Type

from .exceptions import ExceptionWrapper
from .exceptions import TestBrokenException


def equals(expected: Any, actual: Any, message: str = None):
    """
    Сравнивает равенство двух объектов
    :param expected: ожидаемый объект
    :param actual: актуальный объект
    :param message: сообщение, которое будет указано при провале проверки
    :return: None
    :raises AssertionError с указанием объектов и их типов
    """
    if (expected is actual) or expected == actual:
        return
    _message = _mess(message)
    raise AssertionError(f'{_message}Expected "{expected}" ({type(expected).__name__}), '
                         f'but got "{actual}"({type(actual).__name__})!')


def is_none(obj: Any, message: str = None):
    """
    Проверяется, что объект является None, обратная функция для проверки not_none
    :param obj: проверяемый объект
    :param message: сообщение, которое будет указано при провале проверки
    :return: None
    :raises AssertionError с указанием типа объекта
    """
    _message = _mess(message)
    if obj is not None:
        raise AssertionError(f'{_message}Object {obj}({type(obj).__name__}) is not None!')


def not_none(obj: Any, message: str = None):
    """
    Проверяется, что объект не None, обратная функция для is_none
    :param obj: проверяемый объект
    :param message: сообщение, которое будет указано при провале проверки
    :return: None
    :raises AssertionError
    """
    _message = _mess(message)
    if obj is None:
        raise AssertionError(f'{_message}Unexpected None!')


@contextmanager
def waiting_exception(exception: Type[Exception]):
    """
    Менеджер контекста для проверки падения исключения при определенных действиях. Пример:

    with waiting_exception(ZeroDivisionError) as exc:
        some_action()
    print(exc.message) # Выведет сообщение из исключения

    :param exception: ожидаемый тип исключения, нельзя использовать BaseException, не рекомендуется использовать
    Exception (лучше использовать конкретное исключение)
    :return: контекст ExceptionWrapper, который изначально пуст, а при падении исключения получает его в параметр value
    :raises TestBrokenException если использовано BaseException или не наследники Exception
    :raises AssertionError если упало не то исключение, которое ожидалось
    :raises ExceptionWrapper если не упало исключений
    """
    fake = ExceptionWrapper()
    try:
        if exception is BaseException:
            raise TestBrokenException('You must use concrete exception, except of BaseException!')
        if not issubclass(type(exception), type(Exception)):
            raise TestBrokenException(f"Exception or its subclasses expected, but got {exception}({type(exception)})")
        yield fake
    except TestBrokenException as e:
        raise e
    except exception as e:
        fake.set_value(e)
        return
    except Exception as e:
        raise AssertionError(f'Expect {exception}, but raised {type(e)} ("{e}")')
    else:
        raise fake


@contextmanager
def no_exception_expected():
    """
    Менеджер контекста для ситуаций, когда не ожидается падения исключений, более явно, чем просто писать тест
    без ассерта. Пример:

    with no_exception_expected():
        some_action()

    :return: None
    :raises AssertionError если исключение (любой наследник Exception) все же падает
    """
    try:
        yield
    except Exception as e:
        raise AssertionError(f'Expect no exception, but raised {type(e)} ("{e}")')


def test_fail(message: str = None):
    """
    Принудительный провал теста, может быть использовано в редких условиях вместо проверки заведомо неверных условий
    :param message: опциональное сообщение
    :return: None
    """
    raise AssertionError(message if message else 'Test was forcibly failed!')


def test_brake(message: str = None):
    """
    Принудительно приводим тест в сломанное состояние, может быть использовано в редких условиях вместо
    бросания исключений
    :param message: опциональное сообщение
    :return: None
    """
    raise TestBrokenException(message if message else 'Test was forcibly broken!')


def _mess(message: str) -> str:
    return f'{message}\n' if message else ''
