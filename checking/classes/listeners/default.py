import traceback

from .basic import Listener
from ..basic_test import Test
from ..basic_suite import TestSuite
from checking.helpers.others import short
from checking.helpers.others import format_seconds
from checking.helpers.exception_traceback import get_trace_filtered_by_filename


class DefaultListener(Listener):
    """
    Listener by default for standard behaviour during for run events.
    The user can write his own listeners by the class blueprint.
    """

    def __init__(self, verbose: int):
        super().__init__(verbose)
        self.counts = 0

    def on_before_suite_failed(self, test_suite):
        super().on_before_suite_failed(test_suite)
        Listener.print_sync(f'Before suite "{test_suite.name}" failed! Process stopped!')

    def on_suite_starts(self, test_suite: TestSuite):
        super().on_suite_starts(test_suite)
        Listener.print_sync(f'Starting suite "{test_suite.name}"')

    def on_empty_suite(self, test_suite: TestSuite):
        super().on_empty_suite(test_suite)
        Listener.print_sync('No tests were found! Stopped...')

    def on_dry_run(self, test_suite: TestSuite):
        super().on_dry_run(test_suite)
        text = f'{"-" * 10}\nDRY RUN MODE! No real tests will be executed! All fixtures will be ignored!\n{"-" * 10}'
        Listener.print_sync(text)

    def on_suite_stop_with_max_fail(self, max_fail: int):
        super().on_suite_stop_with_max_fail(max_fail)
        text = f'{"-" * 10}\nATTENTION! Suite stops because of reaching maximum count of failed tests={max_fail}' \
               f'\n{"-" * 10}'
        Listener.print_sync(text)

    def on_suite_ends(self, test_suite: TestSuite):
        super().on_suite_ends(test_suite)
        if not self.verbose:
            print()
        print()
        print("=" * 30)
        elapsed = format_seconds(test_suite.suite_duration())
        success_count = len(test_suite.success())
        f_count = len(test_suite.failed())
        b_count = len(test_suite.broken())
        i_count = len(test_suite.ignored())
        all_count = f_count + b_count + i_count + success_count
        print(f'Total tests: {all_count}, success tests: {success_count}, failed tests: {f_count}, broken tests: '
              f'{b_count}, ignored tests: {i_count}')
        print(f'Time elapsed: {elapsed}.')
        print(f'Success percent: {success_count / (all_count):.2%}')
        if self.verbose == 3:
            if f_count:
                print(f'\nFailed tests are:')
                for failed_test in test_suite.failed():
                    print(' ' * 4, failed_test, Listener._get_test_arg_short_without_new_line(failed_test))
            if b_count:
                print(f'\nBroken tests are:')
                for broken_test in test_suite.broken():
                    print(' ' * 4, broken_test, Listener._get_test_arg_short_without_new_line(broken_test))
            if i_count:
                print(f'\nIgnored tests are:')
                for ignored_test in test_suite.ignored():
                    print(' ' * 4, ignored_test)
        print("=" * 30)

    def on_success(self, test: Test):
        super().on_success(test)
        if not self.verbose:
            print('.', end='')
            self.counts += 1
            if self.counts > 100:
                print('')
                self.counts = 0
        elif self.verbose > 1:
            add_ = Listener._get_test_arg_short_without_new_line(test)
            text = f'{"-" * 10}\nTest "{test}" {add_} SUCCESS!\n'
            Listener.print_sync(text)

    def on_broken(self, test: Test, exception_: Exception):
        super().on_broken(test, exception_)
        self._failed_or_broken(test, exception_, 'broken')

    def on_failed(self, test: Test, exception_: Exception):
        super().on_failed(test, exception_)
        self._failed_or_broken(test, exception_, 'failed')

    def on_ignored(self, test: Test, fixture_type: str):
        super().on_ignored(test, fixture_type)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        text = f'Because of fixture "{fixture_type}" tests "{test}" {add_} was IGNORED!\n{"-" * 10}'
        Listener.print_sync(text)

    def on_fixture_failed(self, group_name: str, fixture_type: str, exception_: Exception):
        super().on_fixture_failed(group_name, fixture_type, exception_)
        text = f'{"-" * 10}\nFixture {fixture_type} "{group_name}" failed!\n'
        for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
            text = f'{text}File "{tb.filename}", line {tb.lineno}, in {tb.name}\n'
        print(exception_)
        text = f'{text}{exception_}'
        Listener.print_sync(text)

    def on_ignored_with_provider(self, test: Test):
        super().on_ignored_with_provider(test)
        text = f'Provider "{test.provider}" for {test} not returns iterable or empty! ' \
               f'All tests with provider were IGNORED!'
        Listener.print_sync(text)

    def on_test_starts(self, test: Test):
        super().on_test_starts(test)

    def on_ignored_by_condition(self, test: Test, exc: Exception):
        super().on_ignored_by_condition(test, exc)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        if type(exc) is SystemExit:
            Listener.print_sync(f'Test "{test}" {add_} ignored because of sys.exit() call inside function!')
        else:
            Listener.print_sync(
                f'Test "{test}" {add_} ignored because of condition ({test.only_if.__module__}.{test.only_if})!')

    def _failed_or_broken(self, test: Test, exception_: Exception, _result: str):
        _letter = f'{_result.upper()}!'
        if not self.verbose:
            print(_letter[0], end='')
            self.counts += 1
            if self.counts > 100:
                print('')
                self.counts = 0
        else:
            text = ''
            if self.verbose > 0:
                text = f'{"-" * 10}\n'
            add_ = Listener._get_test_arg_short_without_new_line(test)
            text = f'{text}Test "{test}" {add_} {_letter}\n{get_trace_filtered_by_filename(exception_)}\n{exception_}'
            Listener.print_sync(text)
