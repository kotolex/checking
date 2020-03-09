import traceback
from typing import Callable, Any

from .classes.basic_suite import TestSuite
from .classes.test_group import TestGroup
from .classes.test_case import TestCase
from .classes.basic_test import Test
from .classes.basic_listener import DefaultListener, Listener
from .exceptions import UnknownProviderName

_listener: Listener = DefaultListener()


def run(test_suite: TestSuite, verbose: int = 0, listener: Listener = None):
    verbose = 0 if verbose not in range(4) else verbose
    # Если тестов нет, то продолжать не стоит
    if test_suite.is_empty():
        print('No tests were found! Stopped...')
        return
    if listener:
        global _listener
        _listener = listener
           # Проверка все ли используемые имена профайдеров найдены
    _check_data_providers(test_suite)
    # Если фикстура перед тест-сьютом упала, то тесты не запускаем (фикстура после тест-сюта будет выполнена
    # при соответствующем флаге)
    if not _run_before_suite(test_suite):
        return
    for group in test_suite.groups.values():
        # Если в группе нет тестов, то пропускаем ее
        if not group.tests:
            continue
        # Если фикстура перед группой упала, то тесты не запускаем
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
            _listener.on_ignored_with_provider(test, group)


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
    for retry in range(test.retries):
        clone = test.clone()
        if retry > 0:
            clone.name = clone.name + f' ({retry})'
        result = _run_test(clone, group, verbose, arg)
        if result:
            break
    _run_after(test)
    return False


def _provider_next(provider_name: str) -> Any:
    for param in TestSuite.get_instance().providers[provider_name]():
        yield param


def _run_test(test: Test, group: TestGroup, verbose: int, arg=None) -> bool:
    try:
        if arg is not None:
            test.run(arg)
        else:
            test.run()
        _listener.on_success(group, test, verbose)
        return True
    except Exception as e:
        if type(e) is AssertionError:
            _listener.on_failed(group, test, e, verbose)
        else:
            _listener.on_broken(group, test, e, verbose)
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
        _listener.on_fixture_failed(group_name, fixture_type, error)
        is_failed = True
    return is_failed


def _put_to_ignored(test_object: TestCase, group: TestGroup, fixture_type: str):
    _listener.on_ignored(group, test_object, fixture_type)
