import traceback
import time
from typing import List, Tuple

from .classes import Test
# TODO write unit tests

# Основной набор тестов, позволяет хранить и одноименные
_MAIN: List[Test] = []
# Проваленные тесты (упали по ассертам)
_FAILED: List[Test] = []
# Сломанные тесты - падают с любым исключением кроме ассертов
_BROKEN: List[Test] = []
# Проигнорированные тесты
_IGNORED: List[Test] = []
# My product modules
# TODO find another way
_MODULES = ('annotations', 'asserts', 'runner', "classes")


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
    if not _MAIN:
        print('No tests were found! Stopped...')
        return
    start_time = time.time()
    for test_object in _MAIN:
        test_object.count_down()
        result_pair = _run_fixture(test_object, 'before')
        if not result_pair[0]:
            _put_to_ignored(test_object, result_pair)
            continue
        result_pair = _run_fixture(test_object, 'before_test')
        if not result_pair[0]:
            _put_to_ignored(test_object, result_pair)
            _run_fixture(test_object, 'after')
            continue
        try:
            test_object.run()
            if not verbose:
                print('.', end='')
            elif verbose == 2:
                print_splitter_line()
                print(test_object, " SUCCESS!")
        except Exception as e:
            if verbose > 0:
                print_splitter_line()
            if type(e) == AssertionError:
                _unsuccessful_test(test_object, verbose, e)
            else:
                _unsuccessful_test(test_object, verbose, e, False)
            continue
        else:
            _run_fixture(test_object, 'after_test')
        finally:
            _run_fixture(test_object, 'after')
        if not verbose:
            print()
    _finish(time.time() - start_time, verbose)


def _run_fixture(test: Test, type_: str) -> Tuple[bool, str]:
    mod_name = test.module_name
    _message = f'Because of {type_} fixture'
    values = {
        'before': (test.before, test.run_before_module),
        'before_test': (test.before_test, test.run_before_test),
        'after': (test.after, test.run_after_module),
        'after_test': (test.after_test, test.run_after_test),
    }
    path = values[type_][0]
    run = values[type_][1]
    if 'before' in type_ and path[mod_name] == False:
        return False, _message
    try:
        run()
        return True, ''
    except Exception as error:
        print_splitter_line()
        print(f'{type_} "{mod_name}" failed!')
        for tb in (e for e in traceback.extract_tb(error.__traceback__)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
        print(error)
        if 'before' in type_:
            path[mod_name] = False
        return False, _message


def _finish(elapsed: float, verbose: int):
    """
    Выводит финальную информацию по тест-сьюту
    :param elapsed: время, за которое прошли все тесты
    :return: None
    """
    print()
    print("=" * 30)
    all_count = len(_MAIN)
    f_count = len(_FAILED)
    b_count = len(_BROKEN)
    i_count = len(_IGNORED)
    success_count = all_count - (f_count + b_count + i_count)
    print(f'Total tests:{all_count}, success tests : {success_count}, failed tests:{f_count}, broken tests:'
          f'{b_count}, ignored tests:{i_count}')
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
        if _IGNORED:
            print(f'\nIgnored tests are:')
            for ignored_test in _IGNORED:
                print(' ' * 4, ignored_test)
    print("=" * 30)


def _put_to_ignored(test_object: Test, result_pair: Tuple[bool, str]):
    _IGNORED.append(test_object)
    print_splitter_line()
    print(f'{result_pair[1]} {test_object} was IGNORED!')


def print_splitter_line():
    print('-' * 10)
