import traceback
from typing import Callable

from .basic_suite import TestSuite
from .test_group import TestGroup
from .test_case import TestCase
from .basic_test import Test

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


def run(test_suite: TestSuite, verbose: int = 0):
    verbose = 0 if verbose not in range(4) else verbose
    if test_suite.is_empty():
        print('No tests were found! Stopped...')
        return
    for group_name, group in test_suite.groups.items():
        _run_before(group)
        if group.is_before_failed:
            for test in group.tests:
                _put_to_ignored(test, group, 'before module/group')
            continue
        is_one_of_before_test_failed = False
        for test in group.tests:
            if not is_one_of_before_test_failed:
                _run_before(test)
            else:
                test.is_before_failed = True
            if test.is_before_failed:
                _put_to_ignored(test, group, 'before test')
                is_one_of_before_test_failed = True
                continue
            try:
                test.run()
                if not verbose:
                    print('.', end='')
                elif verbose == 2:
                    _print_splitter_line()
                    print(f'{group_name}.{test.name}', " SUCCESS!")
                    group.add_result_to(test)
            except Exception as e:
                if verbose > 0:
                    _print_splitter_line()
                if type(e) is AssertionError:
                    _unsuccessful_test(test, group, verbose, e)
                else:
                    _unsuccessful_test(test, group, verbose, e, False)
            _run_after(test)
        _run_after(group)
    if not verbose:
        print()


def _unsuccessful_test(test_object: Test, group: TestGroup, verbose: int, error: Exception, is_failed: bool = True):
    """
    Вывод информации о упавшем тесте
    :param test_object: объект тестового класса
    :param verbose: подробность с которой нужно выводить (подробнее смотри start())
    :param error: упавшее исключение
    :param is_failed: упал тест по ассерту или нет
    :return: None
    """
    _result = 'failed' if is_failed else 'broken'
    _letter = f'{_result.upper()}!'
    group.add_result_to(test_object, _result)
    if not verbose:
        print(_letter[0], end='')
    else:
        print(f'Test {test_object} {_letter}')
        for tb in (e for e in traceback.extract_tb(error.__traceback__) if not _is_module(e.filename)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
            print(f'-->    {tb.line}')
        print(error)


def _run_before(test_case: TestCase):
    for before in test_case.before:
        result = _run_fixture(before, 'before', test_case.name)
        if result:
            test_case.is_before_failed = True


def _run_after(test_case: TestCase):
    if test_case.is_before_failed:
        return
    for after in test_case.after:
        _run_fixture(after, 'after', test_case.name)


def _run_fixture(func: Callable, fixture_type: str, group_name: str) -> bool:
    is_failed: bool = False
    try:
        func()
    except Exception as error:
        _print_splitter_line()
        print(f'Fixture {fixture_type} "{group_name}" failed!')
        for tb in (e for e in traceback.extract_tb(error.__traceback__)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
        print(error)
        is_failed = True
    return is_failed


def _put_to_ignored(test_object: Test, group: TestGroup, fixture_type: str):
    group.add_result_to(test_object, 'ignored')
    _print_splitter_line()
    print(f'Because of fixture "{fixture_type}" test {test_object} was IGNORED!')


def _print_splitter_line():
    print('-' * 10)
