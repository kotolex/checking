import traceback
from typing import Callable, Any

from atest.classes.basic_suite import TestSuite
from atest.classes.test_group import TestGroup
from atest.classes.test_case import TestCase
from atest.classes.basic_test import Test

# TODO find another way for modules. Docs!
_MODULES = ('annotations', 'asserts', 'runner', "classes")


class UnknownProviderName(BaseException):
    pass


def run(test_suite: TestSuite, verbose: int = 0):
    verbose = 0 if verbose not in range(4) else verbose
    if test_suite.is_empty():
        print('No tests were found! Stopped...')
        return
    _check_data_providers(test_suite)
    if not _run_before_suite(test_suite):
        return
    for group in test_suite.groups.values():
        if not _run_before_group(group):
            continue
        _run_all_tests_in_group(group, verbose)
        _run_after(group)
    _run_after(test_suite)
    if not verbose:
        print()


def _run_before_suite(test_suite: TestSuite) -> bool:
    _run_before(test_suite)
    if test_suite.is_before_failed:
        print(f'Before suite "{test_suite.name}" failed! Process stopped!')
        if test_suite.always_run_after:
            _run_after(test_suite)
        return False
    return True


def _run_before_group(group: TestGroup) -> bool:
    _run_before(group)
    if group.is_before_failed:
        for test in group.tests:
            _put_to_ignored(test, group, 'before module/group')
        if group.always_run_after:
            _run_after(group)
        return False
    return True


def _run_test_with_provider(test, group, verbose):
    generator = _provider_next(test.provider)
    try:
        for param in generator:
            clone = test.clone()
            clone.name = clone.name + f' [{param}]'
            is_one_of_before_test_failed = _run_test_with_before_and_after(clone, group, False, verbose, param)
            if is_one_of_before_test_failed:
                print(f'Because of "before_test" all test for {test} with data provider "{test.provider}" was IGNORED!')
                break
    except TypeError as e:
        if 'is not iterable' not in e.args[0]:
            raise e
        else:
            group.add_result_to(test, 'ignored')
            print(f'Provider "{test.provider}" for {test} not returns iterable! All tests with provider were IGNORED!')


def _run_all_tests_in_group(group: TestGroup, verbose: int):
    is_one_of_before_test_failed = False
    for test in group.tests:
        if test.provider:
            _run_test_with_provider(test, group, verbose)
        else:
            is_one_of_before_test_failed = _run_test_with_before_and_after(test, group, is_one_of_before_test_failed,
                                                                           verbose)


def _run_test_with_before_and_after(test: TestCase, group: TestGroup, is_one_of_before_test_failed: bool, verbose: int,
                                    arg: Any = None) -> bool:
    if not is_one_of_before_test_failed:
        _run_before(test)
    else:
        test.is_before_failed = True
    if test.is_before_failed:
        _put_to_ignored(test, group, 'before test')
        return True
    _run_test(test, group, verbose, arg)
    _run_after(test)
    return False


def _provider_next(provider_name: str) -> Any:
    for param in TestSuite.get_instance().providers[provider_name]():
        yield param


def _run_test(test: Test, group: TestGroup, verbose: int, arg=None):
    try:
        if arg is not None:
            test.run(arg)
        else:
            test.run()
        if not verbose:
            print('.', end='')
        elif verbose > 1:
            _print_splitter_line()
            print(f'{test} SUCCESS!')
            group.add_result_to(test)
    except Exception as e:
        if verbose > 0:
            _print_splitter_line()
        if type(e) is AssertionError:
            _unsuccessful_test(test, group, verbose, e)
        else:
            _unsuccessful_test(test, group, verbose, e, False)


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


def _check_data_providers(suite: TestSuite):
    all_data_providers = [test.provider for group in suite.groups.values() for test in group.tests if test.provider]
    if not all_data_providers:
        return
    is_all_provider_known = all([provider in suite.providers for provider in all_data_providers])
    if not is_all_provider_known:
        name_ = [provider for provider in all_data_providers if provider not in suite.providers]
        raise UnknownProviderName(f'Cant find provider with name(s) {name_}. '
                                  f'You must have method with @data annotation in this package!')


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
    if not test_case.always_run_after and test_case.is_before_failed:
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


def _put_to_ignored(test_object: TestCase, group: TestGroup, fixture_type: str):
    group.add_result_to(test_object, 'ignored')
    _print_splitter_line()
    print(f'Because of fixture "{fixture_type}" test {test_object} was IGNORED!')


def _print_splitter_line():
    print('-' * 10)
