from unittest import main, TestCase

from atest.annotations import *
from atest.test_runner import start
from atest.classes.basic_listener import Listener

common_str = ''


def failed():
    assert 1 == 2


def clear():
    test_suite = TestSuite.get_instance()
    test_suite.groups.clear()
    test_suite.before.clear()
    test_suite.after.clear()
    test_suite.is_before_failed = False
    global common_str
    common_str = ''


def b_suite():
    global common_str
    common_str += 'bs_'


def a_suite():
    global common_str
    common_str += '_as'


def b_group():
    global common_str
    common_str += 'bg_'


def b_group_2():
    global common_str
    common_str += 'BG_'


def a_group():
    global common_str
    common_str += '_ag'


def a_group_2():
    global common_str
    common_str += '_AG'


def b_test():
    global common_str
    common_str += 'bt_'


def b_test_2():
    global common_str
    common_str += 'BT_'


def a_test():
    global common_str
    common_str += '_at'


def a_test_2():
    global common_str
    common_str += '_AT'


def fn():
    global common_str
    common_str += 'test'


class TestBeforeAndAfter(TestCase):
    _listener = Listener(0)

    def test_no_fixture_when_simple_test(self):
        clear()
        test(fn)
        start(listener=self._listener)
        self.assertEqual('test', common_str)

    def test_before_suite_default(self):
        clear()
        test(fn)
        before_suite(b_suite)
        start(listener=self._listener)
        self.assertEqual('bs_test', common_str)

    def test_after_suite_default(self):
        clear()
        test(fn)
        after_suite(a_suite)
        start(listener=self._listener)
        self.assertEqual('test_as', common_str)

    def test_before_group_default(self):
        clear()
        test(fn)
        before_group(b_group)
        start(listener=self._listener)
        self.assertEqual('bg_test', common_str)

    def test_after_group_default(self):
        clear()
        test(fn)
        after_group(a_group)
        start(listener=self._listener)
        self.assertEqual('test_ag', common_str)

    def test_before_test_default(self):
        clear()
        test(fn)
        before(b_test)
        start(listener=self._listener)
        self.assertEqual('bt_test', common_str)

    def test_after_test_default(self):
        clear()
        test(fn)
        after(a_test)
        start(listener=self._listener)
        self.assertEqual('test_at', common_str)

    def test_all_fixtures_default(self):
        clear()
        test(fn)
        after_group(a_group)
        before_group(b_group)
        before(b_test)
        after(a_test)
        before_suite(b_suite)
        after_suite(a_suite)
        start(listener=self._listener)
        self.assertEqual('bs_bg_bt_test_at_ag_as', common_str)

    def test_all_fixtures_default_with_two_tests(self):
        clear()
        test(fn)
        test(fn)
        after_group(a_group)
        before_group(b_group)
        before(b_test)
        after(a_test)
        before_suite(b_suite)
        after_suite(a_suite)
        start(listener=self._listener)
        self.assertEqual('bs_bg_bt_test_atbt_test_at_ag_as', common_str)

    def test_run_after_suite_if_before_failed_and_flag_true(self):
        clear()
        after_suite(always_run=True)(a_suite)
        test(fn)
        TestSuite.get_instance().is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('_as', common_str)

    def test_not_run_after_suite_if_before_failed(self):
        clear()
        after_suite(a_suite)
        test(fn)
        TestSuite.get_instance().is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('', common_str)

    def test_run_after_group_if_before_failed_and_flag_true(self):
        clear()
        after_group(always_run=True)(a_group)
        test(fn)
        TestSuite.get_instance().get_or_create('fixture_behaviour_test').is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('_ag', common_str)

    def test_not_run_after_group_if_before_failed(self):
        clear()
        after_group(a_group)
        test(fn)
        TestSuite.get_instance().get_or_create('fixture_behaviour_test').is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('', common_str)

    def test_no_after_test_if_before_failed(self):
        clear()
        test(fn)
        after_group(a_group)
        before_group(b_group)
        before(b_test)
        after(a_test)
        before_suite(b_suite)
        after_suite(a_suite)
        TestSuite.get_instance().get_or_create('fixture_behaviour_test').tests[0].is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('bs_bg_bt__ag_as', common_str)

    def test_all_fixtures_default_with_two_tests_and_different_groups(self):
        clear()
        test(fn)
        test(group_name='api')(fn)
        after_group(a_group)
        before_group(b_group)
        before(b_test)
        after(a_test)
        after_group(name='api')(a_group_2)
        before_group(name='api')(b_group_2)
        before(group_name='api')(b_test_2)
        after(group_name='api')(a_test_2)
        before_suite(b_suite)
        after_suite(a_suite)
        start(listener=self._listener)
        self.assertEqual('bs_bg_bt_test_at_agBG_BT_test_AT_AG_as', common_str)

    def test_retries_if_not_fails(self):
        clear()
        test(retries=3)(fn)
        start(listener=self._listener)
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_retries_if_fails(self):
        clear()
        test(retries=3)(failed)
        start(listener=self._listener)
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(3, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())


if __name__ == '__main__':
    main()
