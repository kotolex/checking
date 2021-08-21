from threading import Lock

from ..basic_test import Test
from ..basic_case import TestCase
from ..basic_suite import TestSuite
from ...helpers.others import short


class Listener:
    """
    The parent of listeners of tests. Actually, the user can write their own listener and change the behaviour by
    default, by the way, his listener should be an inheritor of this class.
    """

    def __init__(self, verbose: int = 0):
        self.verbose = verbose

    def on_suite_starts(self, test_suite: TestSuite):
        """
        It calls at the start of the run, after checking the providers.
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    def on_suite_stop_with_max_fail(self, max_fail: int):
        """
        It calls when max_fail parameter was specified and reached, so suite stops
        :param max_fail: count of failed test
        :return:
        """
        pass

    def on_suite_ends(self, test_suite: TestSuite):
        """
        It calls at the end of the run, when all tests finished and fixtures.
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    def on_test_starts(self, test: TestCase):
        """
        It calls before test starts (after preliminary fixtures, but before the test).
        :param test: is the instance of the test with all parameters
        :return: None
        """
        pass

    def on_empty_suite(self, test_suite: TestSuite):
        """
        It calls before the run stops because of there are no tests in any of the groups.
        :param test_suite: is TestSuite
        :return: None
        """
        test_suite.start_suite()
        test_suite.stop_suite()

    def on_dry_run(self, test_suite: TestSuite):
        """
        It calls if suite is run in dry mode (no real tests executes)
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    def on_fixture_failed(self, group_name: str, fixture_type: str, exception_: Exception):
        """
        It calls when a fixture failed to start (before/after).
        :param group_name: is the name of the group of tests
        :param fixture_type: is the name of fixture
        :param exception_: fell exception
        :return: None
        """
        pass

    def on_ignored_with_provider(self, test: Test):
        """
        It calls when the function which marked @data does not return Iterable and all of tests, which tied to the
        provider is ignored.
        :param test: is TestCase
        :return: None
        """
        pass

    def on_error_with_provider(self, name: str, exc: Exception):
        """
        It calls when some provider error appears, which is not expected
        :param name: unique name of the provider
        :param exc: raised exception
        :return: None
        """
        pass

    def on_before_provider_failed(self, test: Test, provider: str):
        """
        It calls when 'before' fixture failef for test with provider
        :param test: TestCase
        :param provider: unique name of the provider
        :return: None
        """
        pass

    def on_success(self, test: Test):
        """
        It calls when the test finished successfully.
        :param test: is TestCase
        :return: None
        """
        pass

    def on_failed(self, test: Test, exception_: Exception):
        """
        It calls if an assert falls at test (embedded or from checking.asserts module)
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        pass

    def on_broken(self, test: Test, exception_: Exception):
        """
        It calls when the test is 'broken', actually, it falls with an exception, but not by assert.
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        pass

    def on_ignored(self, test: Test, fixture_type: str):
        """
        It calls when the test has been ignored due to fallen fixture (before).
        :param test: is TestCase
        :param fixture_type: is the name of the fixture, called ignore
        :return: None
        """
        pass

    def on_ignored_by_condition(self, test: Test, exc: Exception):
        """
        It calls when the test has been ignored by statement (only_if).
        :param test: is TestCase
        :param exc: is the exception
        :return: None
        """
        pass

    def on_before_suite_failed(self, test_suite):
        """
        It calls at the falling of @before_suite fixture.
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    @staticmethod
    def _get_test_arg_short_without_new_line(test: Test):
        if test.provider:
            suite = TestSuite.get_instance()
            mapping_function = str
            if len(suite.providers[test.provider]) == 2:
                mapping_function = suite.providers[test.provider][1]
            short_ = short(mapping_function(test.str_arg)).replace('\n', '')
            return f'[{short_}]'
        return ''

    @staticmethod
    def print_sync(value):
        lock = Lock()
        lock.acquire(blocking=True, timeout=1.0)
        print(value)
        lock.release()
