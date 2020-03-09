from unittest import main, TestCase

from atest.annotations import *
from atest.test_runner import start
from atest.classes.basic_listener import Listener

common_str = ''


def clear():
    test_suite = TestSuite.get_instance()
    test_suite.groups.clear()
    test_suite.before.clear()
    test_suite.after.clear()
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


def a_group():
    global common_str
    common_str += '_ag'


def b_test():
    global common_str
    common_str += 'bt_'


def a_test():
    global common_str
    common_str += '_at'


def fn():
    global common_str
    common_str += 'test'


class TestBeforeAndAfter(TestCase):
    _listener = Listener(0)

    def test_no_fixture_when_simple_test(self):
        clear()
        test(fn)
        start(listener =self._listener)
        self.assertEqual('test', common_str)

    def test_before_suite_default(self):
        clear()
        test(fn)
        before_suite(b_suite)
        start(listener =self._listener)
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


if __name__ == '__main__':
    main()