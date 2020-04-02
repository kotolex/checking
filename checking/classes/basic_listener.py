import traceback
import time

from .basic_case import TestCase
from .basic_group import TestGroup
from .basic_suite import TestSuite
from checking.helpers.exception_traceback import get_trace_filtered_by_filename


def _print_splitter_line():
    print('-' * 10)


def short(object) -> str:
    return _short(str(object), width=50)


def _short(x, width: int = 10):
    string = str(x)
    if len(string) > width:
        return string[:45] + '[...]'
    return string


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


class DefaultListener(Listener):
    """
    Listener by default for standard behaviour during for run events.
    The user can write his own listeners by the class blueprint.
    """

    def on_before_suite_failed(self, test_suite):
        super().on_before_suite_failed(test_suite)
        print(f'Before suite "{test_suite.name}" failed! Process stopped!')

    def on_suite_starts(self, test_suite: TestSuite):
        super().on_suite_starts(test_suite)
        self.start_time = time.time()

    def on_empty_suite(self, test_suite: TestSuite):
        print('No tests were found! Stopped...')

    def on_suite_ends(self, test_suite: TestSuite):
        super().on_suite_ends(test_suite)
        if not self.verbose:
            print()
        print()
        print("=" * 30)
        elapsed = time.time() - self.start_time
        success_count = len(test_suite.success())
        f_count = len(test_suite.failed())
        b_count = len(test_suite.broken())
        i_count = len(test_suite.ignored())
        all_count = f_count + b_count + i_count + success_count
        print(f'Total tests:{all_count}, success tests : {success_count}, failed tests:{f_count}, broken tests:'
              f'{b_count}, ignored tests:{i_count}')
        print(f'Time elapsed: {elapsed:.2f} seconds.')
        if self.verbose == 3:
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

    def on_success(self, group: TestGroup, test: TestCase):
        super().on_success(group, test)
        if not self.verbose:
            print('.', end='')
        elif self.verbose > 1:
            _print_splitter_line()
            add_ = '' if not test.argument else f'[{short(test.argument)}]'
            print(f'Test "{test}" {add_} SUCCESS!')

    def on_broken(self, group: TestGroup, test: TestCase, exception_: Exception):
        super().on_broken(group, test, exception_)
        self._failed_or_broken(test, exception_, 'broken')

    def on_failed(self, group: TestGroup, test: TestCase, exception_: Exception):
        super().on_failed(group, test, exception_)
        self._failed_or_broken(test, exception_, 'failed')

    def on_ignored(self, group: TestGroup, test: TestCase, fixture_type: str):
        super().on_ignored(group, test, fixture_type)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        print(f'Because of fixture "{fixture_type}" tests "{test}" {add_} was IGNORED!')
        _print_splitter_line()

    def on_fixture_failed(self, group_name: str, fixture_type: str, exception_: Exception):
        super().on_fixture_failed(group_name, fixture_type, exception_)
        _print_splitter_line()
        print(f'Fixture {fixture_type} "{group_name}" failed!')
        for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
        print(exception_)

    def on_ignored_with_provider(self, test: TestCase, group: TestGroup):
        super().on_ignored_with_provider(test, group)
        print(f'Provider "{test.provider}" for {test} not returns iterable! All tests with provider were IGNORED!')

    def on_test_starts(self, test: TestCase, group: TestGroup):
        super().on_test_starts(test, group)

    def on_ignored_by_condition(self, group: TestGroup, test: TestCase, exc: Exception):
        super().on_ignored_by_condition(group, test, exc)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        print(f'Test "{test}" {add_} ignored because of condition!')

    def _failed_or_broken(self, test, exception_, _result):
        _letter = f'{_result.upper()}!'
        if not self.verbose:
            print(_letter[0], end='')
        else:
            if self.verbose > 0:
                _print_splitter_line()
            add_ = '' if not test.argument else f'[{short(test.argument)}]'
            print(f'Test "{test}" {add_} {_letter}')
            print(get_trace_filtered_by_filename(exception_))
            print(exception_)
