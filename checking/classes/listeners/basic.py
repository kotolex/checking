from ..basic_case import TestCase
from ..basic_group import TestGroup
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

    def on_test_starts(self, test: TestCase, group: TestGroup):
        """
        It calls before test starts (after preliminary fixtures, but before the test).
        :param test: is the instance of the test with all parameters
        :param group: is the group, to which the test belongs
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

    def on_ignored_with_provider(self, test: TestCase, group: TestGroup):
        """
        It calls when the function which marked @data does not return Iterable and all of tests, which tied to the
        provider is ignored.
        :param test: is TestCase
        :param group: is TestGroup
        :return: None
        """
        self._to_results(group, test, 'ignored')

    def on_success(self, group: TestGroup, test: TestCase):
        """
        It calls when the test finished successfully.
        :param group: is TestGroup
        :param test: is TestCase
        :return: None
        """
        self._to_results(group, test, 'success')

    def on_failed(self, group: TestGroup, test: TestCase, exception_: Exception):
        """
        It calls if an assert falls at test (embedded or from checking.asserts module)
        :param group: is TestGroup
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        self._to_results(group, test, 'failed')

    def on_broken(self, group: TestGroup, test: TestCase, exception_: Exception):
        """
        It calls when the test is 'broken', actually, it falls with an exception, but not by assert.
        :param group: is TestGroup
        :param test: is TestCase
        :param exception_: is fell assert
        :return: None
        """
        self._to_results(group, test, 'broken')

    def on_ignored(self, group: TestGroup, test: TestCase, fixture_type: str):
        """
        It calls when the test has been ignored due to fallen fixture (before).
        :param group: is TestGroup
        :param test: is TestCase
        :param fixture_type: is the name of the fixture, called ignore
        :return: None
        """
        self._to_results(group, test, 'ignored')

    def on_ignored_by_condition(self, group: TestGroup, test: TestCase, exc: Exception):
        """
        It calls when the test has been ignored by statement (only_if).
        :param group: is TestGroup
        :param test: is TestCase
        :param exc: is the exception
        :return: None
        """
        self._to_results(group, test, 'ignored')

    def _to_results(self, group: TestGroup, test: TestCase, result: str):
        group.add_result_to(test, result)

    def on_before_suite_failed(self, test_suite):
        """
        It calls at the falling of @before_suite fixture.
        :param test_suite: is TestSuite
        :return: None
        """
        pass

    @staticmethod
    def _get_test_arg_short_without_new_line(test: TestCase):
        if test.argument:
            short_ = short(test.argument).replace('\n', '')
            return f'[{short_}]'
        return ''
