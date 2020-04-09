from typing import Callable, Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

from .classes.basic_suite import TestSuite
from .classes.basic_group import TestGroup
from .classes.basic_case import TestCase
from .classes.basic_test import Test
from .classes.listeners.basic import Listener
from .classes.listeners.default import DefaultListener
from .exceptions import UnknownProviderName, TestIgnoredException
from .classes.exc_thread import run_with_timeout

# Tests listener
_listener: Listener

# Common parameters for whole test-suite
common_parameters: Dict[str, Any] = {}


def start(verbose: int = 0, listener: Listener = None, groups: List[str] = None, params: Dict[str, Any] = None,
          threads: int = 1, suite_name: str = 'Default Test Suite'):
    """
    The main function of tests start

    :param suite_name: name of the test-suite
    :param listener: is test listener, DefaultListener is used by default. If set, then the verbose parameter is ignored
    (the one in the listener is used).
    :param verbose: is the report detail, 0 - briefly (only dots and 1 letter), 1 - detail, indicating only dropped
    tests, 2 - detail, indicating successful and fallen, 3 - detail and at the end, a list of fallen and broken ones
    If not between 0 and 3, then 0 is accepted
    :param groups: is the list of group names to run, to run only the tests you need
    :param params: is the dictionary of parameters available in all tests (general run parameters)
    :param threads: is the number of threads to run tests by default is 1. Each group can run in a separate thread if
    necessary. This is an experimental feature and it can be useful only for tests NOT performing any complex
    calculations (CPU bound). It is best to use this parameter (more than 1) for tests related to the use of I / O
    operations - disk work, network requests. Obey the GIL!
    :return: None
    """
    verbose = 0 if verbose not in range(4) else verbose
    # If a listener is specified, then use it, otherwise by default
    global _listener
    _listener = listener if listener else DefaultListener(verbose)
    test_suite = TestSuite.get_instance()
    test_suite.name = suite_name
    if groups:
        test_suite.filter_groups(groups)
    # If there are no tests, then stop
    if test_suite.is_empty():
        _listener.on_empty_suite(test_suite)
        return
    if params:
        common_parameters.update(params)
    if threads < 1:
        threads = 1
    _run(test_suite, threads)


def _run(test_suite: TestSuite, threads: int = 1):
    # Create a pool of threads to run tests, by default 1 thread execution
    pool = ThreadPoolExecutor(max_workers=threads)
    # Check if all used provider names are found
    _check_data_providers(test_suite)
    _listener.on_suite_starts(test_suite)
    try:
        # If the fixture before the test suite has fallen, then will not run the tests (fixture after the test suite
        # will be executed with the appropriate flag)
        if not _run_before_suite(test_suite):
            return
        for group in test_suite.groups.values():
            # If there are no tests in the group, then skip it
            if not group.tests:
                continue
            pool.submit(_run_group_before_and_after_at_separate_thread, group)
        pool.shutdown(wait=True)
        _run_after(test_suite)
    finally:
        _listener.on_suite_ends(test_suite)


def _run_group_before_and_after_at_separate_thread(group: TestGroup):
    # If the fixture before the group fell, then we do not run the tests
    if not _run_before_group(group):
        return
    _run_all_tests_in_group(group)
    _run_after(group)


def _run_before_suite(test_suite: TestSuite) -> bool:
    _run_before(test_suite)
    if test_suite.is_before_failed:
        _listener.on_before_suite_failed(test_suite)
        if test_suite.always_run_after:
            _run_after(test_suite)
        return False
    return True


def _run_before_group(group: TestGroup) -> bool:
    _run_before(group)
    if group.is_before_failed:
        for test in group.tests:
            _listener.on_ignored(group, test, 'before module/group')
        if group.always_run_after:
            _run_after(group)
        return False
    return True


def _run_test_with_provider(test, group):
    generator = _provider_next(test.provider)
    try:
        for param in generator:
            clone = test.clone()
            clone.argument = param
            is_one_of_before_test_failed = _run_test_with_before_and_after(clone, group, False)
            if is_one_of_before_test_failed:
                print(f'Because of "before_test" all tests for {test} with data provider "{test.provider}" was IGNORED!')
                break
    except TypeError as e:
        if 'is not iterable' not in e.args[0]:
            raise e
        else:
            _listener.on_ignored_with_provider(test, group)


def _run_all_tests_in_group(group: TestGroup):
    is_one_of_before_test_failed = False
    group.sort_test_by_priority()
    for test in group.tests:
        if test.provider:
            _run_test_with_provider(test, group)
        else:
            is_one_of_before_test_failed = _run_test_with_before_and_after(test, group, is_one_of_before_test_failed)


def _run_test_with_before_and_after(test: TestCase, group: TestGroup, is_before_failed: bool) -> bool:
    if not is_before_failed:
        _run_before(test)
    else:
        test.is_before_failed = True
    if test.is_before_failed:
        _listener.on_ignored(group, test, 'before test')
        return True
    for retry in range(test.retries):
        clone = test.clone()
        if retry > 0:
            clone.name = clone.name + f' ({retry})'
        result = _run_test(clone, group)
        if result:
            break
    _run_after(test)
    return False


def _provider_next(provider_name: str) -> Any:
    for param in TestSuite.get_instance().providers[provider_name]():
        yield param


def _run_test(test: Test, group: TestGroup) -> bool:
    _listener.on_test_starts(test, group)
    try:
        if test.timeout:
            run_with_timeout(test)
        else:
            test.run()
        _listener.on_success(group, test)
        return True
    except AssertionError as e:
        _listener.on_failed(group, test, e)
    except TestIgnoredException as e:
        _listener.on_ignored_by_condition(group, test, e)
    except Exception as e:
        _listener.on_broken(group, test, e)
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
