from ..basic_test import Test
from ..basic_case import TestCase
from ..basic_suite import TestSuite
from checking.helpers.others import short


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
        pass

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
        self._to_results(test, 'ignored')

    def on_success(self, test: Test):
        """
        It calls when the test finished successfully.
        :param test: is TestCase
        :return: None
        """
        self._to_results(test, 'success')

    def on_failed(self, test: Test, exception_: Exception):
        """
        It calls if an assert falls at test (embedded or from checking.asserts module)
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        self._to_results(test, 'failed')

    def on_broken(self, test: Test, exception_: Exception):
        """
        It calls when the test is 'broken', actually, it falls with an exception, but not by assert.
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        self._to_results(test, 'broken')

    def on_ignored(self, test: Test, fixture_type: str):
        """
        It calls when the test has been ignored due to fallen fixture (before).
        :param test: is TestCase
        :param fixture_type: is the name of the fixture, called ignore
        :return: None
        """
        self._to_results(test, 'ignored')

    def on_ignored_by_condition(self, test: Test, exc: Exception):
        """
        It calls when the test has been ignored by statement (only_if).
        :param test: is TestCase
        :param exc: is the exception
        :return: None
        """
        self._to_results(test, 'ignored')

    @staticmethod
    def _to_results(test: Test, result: str):
        test.group.add_result_to(test, result)

    def on_before_suite_failed(self, test_suite):
        """
        It calls at the falling of @before_suite fixture.
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    @staticmethod
    def _get_test_arg_short_without_new_line(test: Test):
        if test.argument:
            short_ = short(test.argument).replace('\n', '')
            return f'[{short_}]'
        return ''
