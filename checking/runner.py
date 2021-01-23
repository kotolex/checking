from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Dict, List, Union, Optional

from .classes.common import Common
from .helpers.others import fake
from .classes.basic_test import Test
from .helpers.report import generate
from .classes.basic_case import TestCase
from .classes.basic_suite import TestSuite
from .classes.basic_group import TestGroup
from .helpers.others import FakePoolExecutor
from .classes.listeners.basic import Listener
from .classes.exc_thread import run_with_timeout
from .classes.listeners.default import DefaultListener
from .helpers.exception_traceback import exception_with_assert
from .exceptions import UnknownProviderName, TestIgnoredException, OnlyIfFailedException, SkipTestException

# Holds the reference to the global test listener object
_listener: Listener
# Test suite execution control flag. Is set to False when max fail count is reached, the test run is then terminated.
_can_run = True
# Max number of failed tests for the whole suite. If 0, the execution is not interrupted until the end of all tests.
_max_fail = 0
# Stores the number of currently failed tests.
_actual_failed_count = 0
# Stores the shared parameters and common functions for the whole test suite.
common: Common = Common()


def start(verbose: int = 0, listener: Optional[Listener] = None, groups: Optional[List[str]] = None,
          params: Optional[Dict[str, Any]] = None, threads: int = 1, suite_name: str = 'Default Test Suite',
          dry_run: bool = False, filter_by_name: Optional[str] = None, random_order: bool = False,
          max_fail: int = 0, generate_report: bool = False, **kwargs):
    """
    Launches the test suite.

    :param verbose: is the report detail:
        0 - brief (dots for successful, letter F for failed tests)
        1 - report only the failed tests
        2 - report both successful and failed tests
        3 - same as 2, additionally list all failed and broken tests at the end of the test run
        reset to 0 if any other value
    :param listener: test listener instance, defaults to DefaultListener.
        If provided, 'verbose' parameter is ignored and verbose setting from the provided listener is used.
    :param groups: list of the test group names to execute
    :param params: dict of parameters shared for all tests
    :param threads: number of threads to run tests in.
        Each test group can be executed in a separate thread.
        WARNING! This is an experimental feature which should be used for lightweight tests,
        not performing resource-intensive calculations (not CPU-bound).
        Use threads parameter to run I/O-bound tests (tests using database, file system, network, etc.).
        Obey the GIL!
    :param suite_name: test suite name
    :param dry_run: if True, runs the test suite, replacing all marked test functions with an empty stub function,
        ensuring all tests will succeed. Use to check the suite configuration, e.g. number of tests in a suite,
        test execution order, provider parameters, etc.
    :param filter_by_name: if specified, leaves only tests with names containing the specified string,
        filtering out the rest
    :param random_order: if specified, runs tests within each group in random order
    :param max_fail: if greater than 0, halts the suite execution when number of failed tests reaches to this parameter
    :param generate_report: if specified, creates an HTML report containing the test run results in the test folder
    :return: None
    """
    verbose = 0 if verbose not in range(4) else verbose
    if type(max_fail) is int and max_fail > 0:
        global _max_fail
        _max_fail = max_fail
    # use specified listener if provided
    global _listener
    _listener = listener if listener else DefaultListener(verbose)
    test_suite = TestSuite.get_instance()
    test_suite.name = suite_name
    if groups:
        test_suite.filter_groups(groups)
    if filter_by_name:
        test_suite.filter_tests(filter_by_name)
    # run the listener hooks and halt if there are no tests found
    if test_suite.is_empty():
        _listener.on_empty_suite(test_suite)
        _listener.on_suite_ends(test_suite)
        if generate_report:
            generate(test_suite)
        return
    if params:
        common.update(params)
    if threads < 1:
        threads = 1
    # use one thread if there's only one test group
    if threads > 1 and len(test_suite.groups) <= 1:
        threads = 1
    if dry_run:
        _dry_run(test_suite)
    # check if all provider names are resolved
    _check_data_providers(test_suite)
    _run(test_suite, threads, random_order, generate_report)


def _dry_run(test_suite: TestSuite):
    """
    Clears all fixtures and replaces the real tests with an empty stub function.

    :param test_suite: suite to launch a dry run on
    :return: None
    """
    # run listener hook
    _listener.on_dry_run(test_suite)
    test_suite.before = []
    test_suite.after = []
    for group in test_suite.groups.values():
        group.before = []
        group.after = []
        for test in group.tests:
            test.before = []
            test.after = []
            test.test = fake


def _run(test_suite: TestSuite, threads: int = 1, random_order: bool = False, generate_report: bool = False):
    """
    Helper, executes a test suite with validated parameters.
    """
    for group in test_suite.groups.values():
        if random_order:
            group.shuffle_tests()
        else:
            group.sort_test_by_priority()
    # use fake thread pool for 1 thread
    pool = FakePoolExecutor() if threads <= 1 else ThreadPoolExecutor(max_workers=threads)
    test_suite.start_suite()
    # run listener hook
    _listener.on_suite_starts(test_suite)
    try:
        # do not run tests if any 'before*' fixtures have failed
        # 'after*' fixtures will be executed respecting the fixture's 'always_run' parameter
        if not _run_before_suite(test_suite):
            return
        for group in test_suite.groups.values():
            # skip empty test groups
            if not group.tests:
                continue
            pool.submit(_run_group_before_and_after_at_separate_thread, group)
        pool.shutdown(wait=True)
        _run_after(test_suite)
    finally:
        test_suite.stop_suite()
        # run listener hook
        _listener.on_suite_ends(test_suite)
        if generate_report:
            generate(test_suite)


def _run_group_before_and_after_at_separate_thread(group: TestGroup):
    """
    Helper, thread worker, handles test and fixture execution.
    """
    # do not run tests if any fixtures have failed
    if not _run_before_group(group):
        return
    _run_all_tests_in_group(group)
    _run_after(group)


def _run_before_suite(test_suite: TestSuite) -> bool:
    """
    Helper, runs 'before_suite' fixtures.

    :param test_suite: TestSuite instance
    :return: True if all fixtures have finished successfully, False otherwise
    """
    _run_before(test_suite)
    if test_suite.is_before_failed:
        # run listener hook
        _listener.on_before_suite_failed(test_suite)
        if test_suite.always_run_after:
            _run_after(test_suite)
        return False
    return True


def _run_before_group(group: TestGroup) -> bool:
    """
    Helper, runs 'before_group' fixtures.

    :param group: TestGroup instance
    :return: True if all fixtures have finished successfully, False otherwise
    """
    _run_before(group)
    if group.is_before_failed:
        for test in group.tests:
            test.stop(TestIgnoredException('Before module/group has failed!'))
            # run listener hook
            _listener.on_ignored(test, 'before module/group')
        if group.always_run_after:
            _run_after(group)
        return False
    return True


def _run_test_with_provider(test: Test):
    """
    Helper, runs tests which have a provider.

    :param test: Test instance
    :return: None
    """
    test_suite = TestSuite.get_instance()
    provider = test.provider
    # get provider data from the cache, if present
    generator = _provider_next(provider) if provider not in test_suite.cache else test_suite.cache[provider]
    try:
        is_any_value_provides = False
        need_to_cache = provider in test_suite.cached and provider not in test_suite.cache
        list_of_arguments = []
        for param in generator:
            is_any_value_provides = True
            if not _can_run:
                break
            clone = test.clone()
            clone.argument = param
            if need_to_cache:
                list_of_arguments.append(param)
            is_one_of_before_test_failed = _run_test_with_before_and_after(clone, False)
            if is_one_of_before_test_failed:
                # run listener hook
                _listener.on_before_provider_failed(test, provider)
                break
        # ignore tests with empty providers
        if not is_any_value_provides:
            test.stop(TestIgnoredException(f'Provider {test.provider} is empty.'))
            # run listener hook
            _listener.on_ignored_with_provider(test)
        else:
            if need_to_cache:
                test_suite.cache[provider] = tuple(list_of_arguments)
    except TypeError as e:
        if 'is not iterable' not in e.args[0]:
            _listener.on_error_with_provider(provider, e)
            raise
        else:
            test.stop(TestIgnoredException(f'Error using provider {test.provider}.'))
            # run listener hook and ignore the exception
            _listener.on_ignored_with_provider(test)


def _run_all_tests_in_group(group: TestGroup):
    """
    Helper, sorts tests by priority and executes all test from the specified group.

    :param group: TestGroup instance
    :return: None
    """
    is_one_of_before_test_failed = False
    for test in group.tests:
        if not _can_run:
            break
        if test.provider:
            _run_test_with_provider(test)
        else:
            is_one_of_before_test_failed = _run_test_with_before_and_after(test, is_one_of_before_test_failed)


def _run_test_with_before_and_after(test: Test, is_before_failed: bool) -> bool:
    """
    Helper, runs a test with the corresponding 'before_test' and 'after_test' fixtures.

    :param test: Test instance
    :param is_before_failed:
    :return:
    """
    if not is_before_failed:
        _run_before(test)
    else:
        test.is_before_failed = True
    if test.is_before_failed:
        test.stop(TestIgnoredException("''before_test' fixture has failed."))
        # run listener hook
        _listener.on_ignored(test, 'before test')
        return True
    for retry in range(test.retries):
        clone = test.clone()
        if retry > 0:
            clone.name = clone.name + f' ({retry})'
        result = _run_test(clone)
        if result:
            break
    _run_after(test)
    return False


def _provider_next(provider_name: str) -> Any:
    """
    Helper, looks up the specified provider function and yields test data from it.
    Tries to close a resource after reading the data, if the provider has a 'close' callable attribute.

    :param provider_name: provider name
    :return: generator
    """
    iter_ = TestSuite.get_instance().providers[provider_name][0]()
    yield from iter_
    # try-close the resource (e.g. file) if provider was using it
    if hasattr(iter_, 'close'):
        try:
            iter_.close()
        except Exception as ex:
            # run listener hook and ignore the exception
            _listener.on_error_with_provider(provider_name, exc=ex)


def _run_test(test: Test) -> bool:
    """
    Helper, runs the test and collects the test result.

    :param test: Test instance
    :return: True if test succeeds, False otherwise
    """
    # run listener hook
    _listener.on_test_starts(test)
    try:
        if test.timeout:
            run_with_timeout(test)
        else:
            test.run()
        test.stop()
        # run listener hook
        _listener.on_success(test)
        return True
    except AssertionError as e:
        e = exception_with_assert(e)
        test.stop(e)
        # run listener hook
        _listener.on_failed(test, e)
        global _actual_failed_count
        if _max_fail and _actual_failed_count < _max_fail:
            _actual_failed_count += 1
        if _max_fail and _actual_failed_count >= _max_fail:
            global _can_run
            _can_run = False
            # run listener hook
            _listener.on_suite_stop_with_max_fail(_max_fail)
    except (TestIgnoredException, OnlyIfFailedException, SkipTestException, SystemExit) as e:
        test.stop(e)
        # run listener hook
        _listener.on_ignored_by_condition(test, e)
    except Exception as e:
        test.stop(e)
        # run listener hook
        _listener.on_broken(test, e)
    return False


def _check_data_providers(suite: TestSuite):
    """
    Helper, checks if any tests in the specified suite use a data provider and the provider name is resolved.

    :param suite: TestSuite instance
    :return: None
    :raise UnknownProviderName: if a test uses a provider which name was not successfully resolved
    """
    all_data_providers = [test.provider for group in suite.groups.values() for test in group.tests if test.provider]
    if not all_data_providers:
        return
    is_all_provider_known = all(provider in suite.providers for provider in all_data_providers)
    if not is_all_provider_known:
        name_ = [provider for provider in all_data_providers if provider not in suite.providers]
        raise UnknownProviderName(f"Could not find provider(s) named {name_}. "
                                  f"Current module must contain functions marked with the '@data' decorator.")


def _run_before(test_case: Union[TestCase, TestSuite]):
    """
    Helper, runs all fixtures before a test case or the test suite.
    Sets 'is_before_failed' flag to True if a fixture fails.

    :param test_case: Test or TestGroup instance
    :return: None
    """
    for before in test_case.before:
        result = _run_fixture(before, 'before', test_case.name)
        if result:
            test_case.is_before_failed = True


def _run_after(test_case: Union[TestCase, TestSuite]):
    """
    Helper, runs all fixtures after a test or a test group.

    :param test_case: Test or TestGroup instance
    :return: None
    """
    if not test_case.always_run_after and test_case.is_before_failed:
        return
    for after in test_case.after:
        _run_fixture(after, 'after', test_case.name)


def _run_fixture(func: Callable, fixture_type: str, group_name: str) -> bool:
    """
    Helper, runs a fixture and returns the result of the fixture execution.

    :param func: function, marked with a 'before*' decorator
    :param fixture_type: string fixture classifier to use with the listener events (e.g. 'before', 'after' ...)
    :param group_name: test group name
    :return: True if the fixture has failed, False otherwise
    """
    is_failed: bool = False
    try:
        func()
    except Exception as error:
        # run listener hook
        _listener.on_fixture_failed(group_name, fixture_type, error)
        is_failed = True
    return is_failed
