import time

from .test_runner import run
from .basic_suite import TestSuite


def start(verbose: int = 0):
    """
    Главная функция запуска тестов.

    :param verbose: подробность отчетов, 0 - кратко (только точки и 1 буква), 1 - подробно, с указанием только
    упавших тестов, 2- подробно, с указанием успешных и упавших, 3 - подробно и в конце вывод списка упавших и сломанных
    Если не в промежутке от 0 до 3 то принимается 0
    :return: None
    """
    start_time = time.time()
    run(TestSuite.get_instance(), verbose)
    _finish(time.time() - start_time, verbose)


def _finish(elapsed: float, verbose: int):
    """
    Выводит финальную информацию по тест-сьюту
    :param elapsed: время, за которое прошли все тесты
    :return: None
    """
    print()
    print("=" * 30)
    test_suite = TestSuite.get_instance()
    all_count = test_suite.tests_count()
    f_count = len(test_suite.failed())
    b_count = len(test_suite.broken())
    i_count = len(test_suite.ignored())
    success_count = all_count - (f_count + b_count + i_count)
    print(f'Total tests:{all_count}, success tests : {success_count}, failed tests:{f_count}, broken tests:'
          f'{b_count}, ignored tests:{i_count}')
    print(f'Time elapsed: {elapsed:.2f} seconds.')
    if verbose == 3:
        if f_count:
            print(f'\nFailed tests are:')
            for failed_test in test_suite.failed():
                print(' ' * 4, failed_test)
        if b_count:
            print(f'\nBroken tests are:')
            for broken_test in test_suite.broken():
                print(' ' * 4, broken_test)
        if i_count:
            print(f'\nIgnored tests are:')
            for ignored_test in test_suite.ignored():
                print(' ' * 4, ignored_test)
    print("=" * 30)
