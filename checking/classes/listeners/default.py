import time
import traceback

from .basic import Listener
from ..basic_case import TestCase
from ..basic_group import TestGroup
from ..basic_suite import TestSuite
from checking.helpers.others import short
from checking.helpers.others import print_splitter_line
from checking.helpers.exception_traceback import get_trace_filtered_by_filename


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
        self.counts = 0
        print(f'Starting suite "{test_suite.name}"')

    def on_empty_suite(self, test_suite: TestSuite):
        super().on_empty_suite(test_suite)
        print('No tests were found! Stopped...')

    def on_dry_run(self, test_suite: TestSuite):
        super().on_dry_run(test_suite)
        print_splitter_line()
        print("DRY RUN MODE! No real tests will be executed! All fixtures will be ignored!")
        print_splitter_line()

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
            self.counts += 1
            if self.counts > 100:
                print('')
                self.counts = 0
        elif self.verbose > 1:
            print_splitter_line()
            add_ = Listener._get_test_arg_short_without_new_line(test)
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
        print_splitter_line()

    def on_fixture_failed(self, group_name: str, fixture_type: str, exception_: Exception):
        super().on_fixture_failed(group_name, fixture_type, exception_)
        print_splitter_line()
        print(f'Fixture {fixture_type} "{group_name}" failed!')
        for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
        print(exception_)

    def on_ignored_with_provider(self, test: TestCase, group: TestGroup):
        super().on_ignored_with_provider(test, group)
        print(f'Provider "{test.provider}" for {test} not returns iterable or empty!'
              f' All tests with provider were IGNORED!')

    def on_test_starts(self, test: TestCase, group: TestGroup):
        super().on_test_starts(test, group)

    def on_ignored_by_condition(self, group: TestGroup, test: TestCase, exc: Exception):
        super().on_ignored_by_condition(group, test, exc)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        if type(exc) is SystemExit:
            print(f'Test "{test}" {add_} ignored because of sys.exit() call inside function!')
        else:
            print(f'Test "{test}" {add_} ignored because of condition ({test.only_if.__module__}.{test.only_if})!')

    def _failed_or_broken(self, test, exception_, _result):
        _letter = f'{_result.upper()}!'
        if not self.verbose:
            print(_letter[0], end='')
            self.counts += 1
            if self.counts > 100:
                print('')
                self.counts = 0
        else:
            if self.verbose > 0:
                print_splitter_line()
            add_ = Listener._get_test_arg_short_without_new_line(test)
            print(f'Test "{test}" {add_} {_letter}')
            print(get_trace_filtered_by_filename(exception_))
            print(exception_)
