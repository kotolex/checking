import time
import logging
from threading import currentThread

from .basic import Listener
from ..basic_case import TestCase
from ..basic_group import TestGroup
from ..basic_suite import TestSuite
from checking.helpers.others import short, str_date_time


class DefaultFileListener(Listener):
    """
    Listener by default for logging all events to local file.
    The user can write his own listeners by the class blueprint.
    """

    def __init__(self, log_level: str = logging.DEBUG, name: str = None, use_time: bool = True):
        """
        Init all parameters for logger
        :param log_level: level of logging, DEBUG by default
        :param name: name of the result file, by default is 'test_suite'
        :param use_time: if True, appends date and time to file name of the log.
        Example: test_suite_2020-04-09_17-51-29.log
        """
        super().__init__(0)
        name_ = 'test_suite' if not name else name
        str_time = str_date_time()
        time_ = f'_{str_time}' if use_time else ''
        format_ = '%(asctime)-15s Thread[%(threadName)s] %(levelname)s: %(message)s'
        handler = logging.FileHandler(f'{name_}{time_}.log', 'w', encoding='utf-8')
        logging.basicConfig(level=log_level, format=format_, handlers=(handler,))

    def on_suite_starts(self, test_suite: TestSuite):
        super().on_suite_starts(test_suite)
        logger = logging.getLogger()
        logger.info(f'Test-suite "{test_suite.name}" started!')
        self.start_time = time.time()

    def on_dry_run(self, test_suite: TestSuite):
        super().on_dry_run(test_suite)
        logger = logging.getLogger()
        logger.warning("DRY RUN MODE! No real tests will be executed! All fixtures will be ignored!")

    def on_suite_ends(self, test_suite: TestSuite):
        super().on_suite_ends(test_suite)
        elapsed = time.time() - self.start_time
        success_count = len(test_suite.success())
        f_count = len(test_suite.failed())
        b_count = len(test_suite.broken())
        i_count = len(test_suite.ignored())
        all_count = f_count + b_count + i_count + success_count
        logger = logging.getLogger()
        logger.info(f'Test-suite "{test_suite.name}" finished!')
        logger.info(f'Total tests:{all_count}, success tests : {success_count}, failed tests:{f_count}, broken tests:'
                    f'{b_count}, ignored tests:{i_count}')
        logger.info(f'Time elapsed: {elapsed:.2f} seconds.')

    def on_test_starts(self, test: TestCase, group: TestGroup):
        super().on_test_starts(test, group)
        logger = logging.getLogger(currentThread().getName())
        logger.info(f'Test  "{test}" started!')

    def on_empty_suite(self, test_suite: TestSuite):
        super().on_empty_suite(test_suite)
        logger = logging.getLogger()
        logger.critical(f'Test-suite "{test_suite.name}" is empty! No tests found')

    def on_fixture_failed(self, group_name: str, fixture_type: str, exception_: Exception):
        super().on_fixture_failed(group_name, fixture_type, exception_)
        logger = logging.getLogger(currentThread().getName())
        logger.exception(f'Fixture {fixture_type} "{group_name}" failed!', exc_info=exception_)

    def on_ignored_with_provider(self, test: TestCase, group: TestGroup):
        super().on_ignored_with_provider(test, group)
        logger = logging.getLogger(currentThread().getName())
        logger.warning(f'Provider "{test.provider}" for {test} not returns iterable or empty! '
                       f'All tests with provider were IGNORED!')

    def on_success(self, group: TestGroup, test: TestCase):
        super().on_success(group, test)
        add_ = Listener._get_test_arg_short_without_new_line(test)
        logger = logging.getLogger(currentThread().getName())
        logger.info(f'Test "{test}" {add_} SUCCESS!')

    def on_failed(self, group: TestGroup, test: TestCase, exception_: Exception):
        super().on_failed(group, test, exception_)
        add_ = Listener._get_test_arg_short_without_new_line(test)
        logger = logging.getLogger(currentThread().getName())
        logger.exception(f'Test "{test}" {add_} FAILED!', exc_info=exception_)

    def on_broken(self, group: TestGroup, test: TestCase, exception_: Exception):
        super().on_broken(group, test, exception_)
        add_ = Listener._get_test_arg_short_without_new_line(test)
        logger = logging.getLogger(currentThread().getName())
        logger.exception(f'Test "{test}" {add_} BROKEN!', exc_info=exception_)

    def on_ignored(self, group: TestGroup, test: TestCase, fixture_type: str):
        super().on_ignored(group, test, fixture_type)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        logger = logging.getLogger(currentThread().getName())
        logger.warning(f'Because of fixture "{fixture_type}" tests "{test}" {add_} was IGNORED!')

    def on_ignored_by_condition(self, group: TestGroup, test: TestCase, exc: Exception):
        super().on_ignored_by_condition(group, test, exc)
        add_ = '' if not test.argument else f'[{short(test.argument)}]'
        logger = logging.getLogger(currentThread().getName())
        if type(exc) is SystemExit:
            logger.warning(f'Test "{test}" {add_} ignored because of sys.exit() call inside function!')
        else:
            logger.warning(f'Test "{test}" {add_} ignored because of condition'
                           f' ({test.only_if.__module__}.{test.only_if})!')

    def on_before_suite_failed(self, test_suite):
        super().on_before_suite_failed(test_suite)
        logger = logging.getLogger()
        logger.critical(f'Before suite "{test_suite.name}" failed! Process stopped!')
