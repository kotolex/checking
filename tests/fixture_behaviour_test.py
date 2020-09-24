from unittest import main, TestCase

from checking.annotations import *
import checking.runner as runner
from checking.runner import start
from checking.classes.listeners.basic import Listener
from importlib import reload

common_str = ''


def failed():
    assert 1 == 2


def par_1():
    runner.common_parameters['1'] = 1


def par_2():
    assert 1 == runner.common_parameters['1']


def clear():
    reload(runner)
    test_suite = TestSuite.get_instance()
    test_suite.groups.clear()
    test_suite.before.clear()
    test_suite.after.clear()
    test_suite.is_before_failed = False
    test_suite.providers.clear()
    test_suite.cache.clear()
    test_suite.cached.clear()
    global common_str
    common_str = ''
    runner.common_parameters.clear()


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
        list(TestSuite.get_instance().groups.values())[0].is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('_ag', common_str)

    def test_not_run_after_group_if_before_failed(self):
        clear()
        after_group(a_group)
        test(fn)
        list(TestSuite.get_instance().groups.values())[0].is_before_failed = True
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
        list(TestSuite.get_instance().groups.values())[0].tests[0].is_before_failed = True
        start(listener=self._listener)
        self.assertEqual('bs_bg_bt__ag_as', common_str)

    def test_all_fixtures_default_with_two_tests_and_different_groups(self):
        clear()
        test(fn)
        test(groups=['api'])(fn)
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

    def test_priorities(self):
        clear()
        test(priority=3)(b_suite)
        test(priority=2)(a_suite)
        test(priority=1)(b_group)
        test(fn)
        start(listener=self._listener)
        self.assertEqual('testbg__asbs_', common_str)

    def test_common_params(self):
        clear()
        test(par_1)
        test(par_2)
        start(listener=self._listener)
        self.assertEqual(runner.common_parameters, {'1': 1})

    def test_no_tests_if_filter_not_existed_group(self):
        clear()
        test(par_1)
        test(groups=['a'])(par_2)
        start(listener=self._listener, groups=['b'])
        self.assertFalse(TestSuite.tests_count())

    def test_one_test_if_filter_existed_group(self):
        clear()
        test(par_1)
        test(groups=['a'])(par_2)
        start(listener=self._listener, groups=['a'])
        self.assertEqual(1, TestSuite.tests_count())

    def test_no_params_on_default(self):
        clear()
        test(fn)
        start(listener=self._listener)
        self.assertFalse(runner.common_parameters)

    def test_params_if_exists(self):
        clear()
        test(fn)
        start(listener=self._listener, params={'test': 'test'})
        self.assertTrue(runner.common_parameters)
        self.assertEqual(runner.common_parameters, {'test': 'test'})

    def test_params_if_exists_and_use_in_test(self):
        clear()
        test(par_1)
        start(listener=self._listener, params={'test': 'test'})
        self.assertTrue(runner.common_parameters)
        self.assertEqual('test', runner.common_parameters['test'])
        self.assertEqual(1, runner.common_parameters['1'])


if __name__ == '__main__':
    main()
