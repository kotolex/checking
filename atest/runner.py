import traceback
import time
from collections import defaultdict
from typing import List

from .classes import Test

# Основной набор тестов, позволяет хранить и одноименные
_MAIN: List[Test] = []
# Проваленные тесты (упали по ассертам)
_FAILED = []
# Сломанные тесты - падают с любым исключением кроме ассертов
_BROKEN = []
# My product name
_MODULES = ('annotations', 'asserts', 'runner', "classes")
_DICT = defaultdict(list)


def _is_module(name: str) -> bool:
    """
    Проверяем на модуль атеста, чтобы не выводить трейсы ошибок самой библиотеки (которые юзеру не интересны)
    :param name: имя
    :return: является ли это именем одного из модулей проекта
    """
    for module_name in _MODULES:
        if name.endswith(module_name + '.py'):
            return True
    return False


def _unsuccessful_test(test_object: Test, verbose: int, error: Exception, is_failed: bool = True):
    """
    Вывод информации о упавшем тесте
    :param test_object: объект тестового класса
    :param verbose: подробность с которой нужно выводить (подробнее смотри start())
    :param error: упавшее исключение
    :param is_failed: упал тест по ассерту или нет
    :return: None
    """
    _list = _FAILED if is_failed else _BROKEN
    _letter = 'FAILED!' if is_failed else 'BROKEN!'
    _list.append(test_object)
    if not verbose:
        print(_letter[0], end='')
    else:
        print(test_object, _letter)
        for tb in (e for e in traceback.extract_tb(error.__traceback__) if not _is_module(e.filename)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
            print(f'-->    {tb.line}')
        print(error)


def start(verbose: int = 0):
    """
    Главная функция запуска тестов.

    :param verbose: подробность отчетов, 0 - кратко (только точки и 1 буква), 1 - подробно, с указанием только
    упавших тестов, 2- подробно, с указанием успешных и упавших, 3 - подробно и в конце вывод списка упавших и сломанных
    Если не в промежутке от 0 до 3 то принимается 0
    :return: None
    """
    verbose = 0 if verbose not in range(4) else verbose
    start_time = time.time()
    for test_object in _MAIN:
        try:
            test_object.run()
            if not verbose:
                print('.', end='')
            elif verbose == 2:
                print('-' * 10)
                print(test_object, " SUCCESS!")
        except Exception as e:
            if verbose > 0:
                print('-' * 10)
            if type(e) == AssertionError:
                _unsuccessful_test(test_object, verbose, e)
            else:
                _unsuccessful_test(test_object, verbose, e, False)
    if not verbose:
        print()
    for test_object in _MAIN:
        try:
            test_object.finish()
        except Exception as e:
            print(e)
    _finish(time.time() - start_time, verbose)


def _finish(elapsed: float, verbose: int):
    """
    Выводит финальную информацию по тест-сьюту
    :param elapsed: время, за которое прошли все тесты
    :return: None
    """
    print("=" * 30)
    all_count = len(_MAIN)
    f_count = len(_FAILED)
    b_count = len(_BROKEN)
    success_count = all_count - (f_count + b_count)
    print(f'Total tests:{all_count}, success tests : {success_count}, failed tests:{f_count}, broken tests:{b_count}')
    print(f'Time elapsed: {elapsed:.2f} seconds.')
    if verbose == 3:
        if _FAILED:
            print(f'\nFailed tests are:')
            for failed_test in _FAILED:
                print(' ' * 4, failed_test)
        if _BROKEN:
            print(f'\nBroken tests are:')
            for broken_test in _BROKEN:
                print(' ' * 4, broken_test)
    print("=" * 30)
