import traceback
import time
from _collections import defaultdict

# Основной набор тестов, позволяет хранить и одноименные
_MAIN = []
# Проваленные тесты (упали по ассертам)
_FAILED = []
# Сломанные тесты - падают с любым исключением кроме ассертов
_BROKEN = []
# My product name
__PACKAGE = 'atest'
# TODO filter
_DICT = defaultdict(list)


def _unsuccessful_test(test, verbose, error, is_failed=True):
    """
    Вывод информации о упавшем тесте
    :param test: тестовый метод
    :param verbose: подробность с которой нужно выводить (подробнее смотри start())
    :param error: упавшее исключение
    :param is_failed: упал тест по ассерту или нет
    :return: None
    """
    _list = _FAILED if is_failed else _BROKEN
    _letter = 'FAILED!' if is_failed else 'BROKEN!'
    _list.append(test)
    if not verbose:
        print(_letter[0], end='')
    else:
        print(test.__name__, _letter)
        for tb in (e for e in traceback.extract_tb(error.__traceback__) if __PACKAGE not in e.filename):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
            print(f'-->    {tb.line}')
        print(error)


def start(verbose=0):
    """
    Главная функция запуска тестов.

    :param verbose: подробность отчетов, 0 - кратко (только точки и 1 буква), 1 - подробно, с указанием только
    упавших тестов, 2- подробно, с указанием успешнах и упавших
    :return: None
    """
    start_time = time.time()
    for test in _MAIN:
        try:
            test()
            if not verbose:
                print('.', end='')
            elif verbose == 2:
                print('-' * 10)
                print(test.__name__, " SUCCESS!")
        except Exception as e:
            if verbose > 0:
                print('-' * 10)
            if type(e) == AssertionError:
                _unsuccessful_test(test, verbose, e)
            else:
                _unsuccessful_test(test, verbose, e, False)
    if not verbose:
        print()
    _finish(time.time() - start_time)


def _finish(elapsed: float):
    """
    Выводит финальную информацию по тест-сьюту
    :param elapsed: время, за которое прошли все тесты
    :return: None
    """
    print("=" * 30)
    print(f'Total tests:{len(_MAIN)}, failed tests:{len(_FAILED)}, broken tests:{len(_BROKEN)}')
    print(f'Time elapsed: {elapsed:.2f} seconds.')
    if _FAILED:
        print(f'\nFailed tests are:')
        for failed_test in _FAILED:
            print(' ' * 4, failed_test.__name__)
    if _BROKEN:
        print(f'\nBroken tests are:')
        for broken_test in _BROKEN:
            print(' ' * 4, broken_test.__name__)
    print("=" * 30)
